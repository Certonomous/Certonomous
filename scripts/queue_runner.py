#!/usr/bin/env python3
"""queue_runner.py -- the lab's OS-level queue runner (Sanaa's order, 2026-08-26 ~03:00Z,
LAB_STATE CHIEF addendum "DETACHED QUEUES RULED"; permission at HEAD in bc0e687e).

WHAT IT IS.  A plain script that, once started detached (`setsid nohup ...`), outlives
every agent and session.  Each tick it (1) measures the box -- busy % from a /proc/stat
delta, never loadavg; MemAvailable from /proc/meminfo -- (2) reads every
verification/queue/<team>/*.json entry, (3) validates each with
scripts/queue_entry_check.py (the SAME checks a supervisor runs by hand: schema, frozen
prereg sha exists and holds the prereg path, age guard, ranks), and (4) launches AT MOST
ONE valid entry per tick, only when the box is under the ceiling, round-robin across
teams, oldest entry first within a team.

WHAT IT NEVER DOES.  It never kills anything: a cap is a runaway guard that REPORTS
(CAP_OVERRUN.txt beside the run at 1.00 x the entry's `cap_core_min_registered`, or
ESTIMATE_OVERRUN.txt at 1.10 x the estimate when no cap is registered) and never terminates
(COMPUTE_BUDGET_CHARTER).  It never
deletes anything: a refused entry is MOVED to <team>/refused/ with its reasons beside it.
It never edits, stages or commits in git; the only git it runs is the validator's
read-only allowlist.  It never dispatches to another host: an entry carrying `host`
other than this box is skipped with a logged reason (remote dispatch is not this
script's).  It never runs under `python3 -O` (refuses, rc 2).  It never authorises: an
entry sitting in a queue directory is a proposal; the supervisor's SUPERVISION_CHARTER
section 3 check 4 happened at enqueue time or it did not happen, and this script cannot
tell the difference.  The queue directory README says so and this docstring repeats it.

HOW A LAUNCH LOOKS.  Every launch is
    setsid nohup bash -c 'cd <cwd>; <argv> > <cwd>/launcher.queue.out 2>&1;
                          echo "rc=$? end=<utc>" > <cwd>/STATUS.<case_id>' < /dev/null &
so the rc is captured INSIDE the detached wrapper.  The parent's rc is never trusted --
this lab measured that `setsid`/`timeout` return 0 for every outcome (4225ef0c,
83769288).  The entry file is moved to <team>/launched/ and a line is appended to
verification/queue/LAUNCH_LOG.tsv (utc, team, case_id, pid, sid, ranks, cost, prereg sha).

INSTRUMENT RULES.  No `assert` anywhere (L-332; `--selftest` parses its own AST and
refuses on one).  No unconditional success print: every LAUNCHED / EMPTY / REFUSED line
is printed from inside the branch that verified it.  `--selftest` (standing rule 3)
drives three planted controls in a scratch queue root: a valid entry whose argv is
`true` must produce exactly one launch and a STATUS reading rc=0; an EMPTY queue must
produce zero launches and say EMPTY; an entry missing `prereg_commit` must be REFUSED
and moved -- and the three outputs must not read alike.  The box reading (busy %,
MemAvailable) is INJECTED in the selftest (`tick(..., measure=fake)`), so no control
depends on the live load; one control hands in a saturated reading and must be HELD.
EXIT PATH (2026-08-26): SIGTERM/SIGINT/SIGHUP are handled and every way out of the
daemon loop logs `EXIT reason=<signal name|ExceptionClass: msg|normal> pid=<pid>` to
runner.log before the process ends; an escaping exception is logged and RE-RAISED,
never swallowed.  `--selftest` sends SIGTERM to a scratch-root daemon and requires
that line.

USAGE
    python3 scripts/queue_runner.py --daemon            # loop forever, 60 s ticks
    python3 scripts/queue_runner.py --once              # one tick, then exit
    python3 scripts/queue_runner.py --selftest
    options: --root <queue root> --busy-ceiling 85 --core-fraction 0.9 --interval 60
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
import queue_entry_check as qec  # noqa: E402  (read-only validator; never launches)

EXIT_REFUSE = 2
DEFAULT_ROOT = REPO / "verification" / "queue"
TEAMS = tuple(qec.TEAMS)
SKIP_DIRS = ("launched", "refused")


class Refusal(RuntimeError):
    pass


def refuse(msg: str) -> None:
    raise Refusal(msg)


class Signalled(BaseException):
    """Raised by the daemon's signal handlers so that the ONE exit path in main()
    can log `EXIT reason=<signal name>` before the process ends. BaseException, not
    Exception: the per-tick `except Exception` must never swallow a signal.
    (2026-08-26: runner pid 189825 died between 20:47:43Z and 20:48:01Z with no
    recorded reason; a daemon that exits without saying why is a finding.)"""

    def __init__(self, signum: int):
        super().__init__(signum)
        self.signum = int(signum)
        try:
            self.name = signal.Signals(self.signum).name
        except ValueError:
            self.name = f"SIG{self.signum}"


def _raise_signalled(signum, _frame) -> None:
    raise Signalled(signum)


def install_signal_handlers() -> tuple[str, ...]:
    names = []
    for s in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(s, _raise_signalled)
        names.append(s.name)
    return tuple(names)


def utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ----------------------------------------------------------------------------- box
def _stat_snapshot() -> tuple[int, int]:
    with open("/proc/stat") as f:
        parts = f.readline().split()
    vals = [int(x) for x in parts[1:]]
    idle = vals[3] + vals[4]
    return sum(vals), idle


def busy_percent(window_s: float = 5.0) -> float:
    t0, i0 = _stat_snapshot()
    time.sleep(window_s)
    t1, i1 = _stat_snapshot()
    tot = t1 - t0
    if tot <= 0:
        refuse("/proc/stat delta is not positive; busy % cannot be measured")
    return 100.0 * (1.0 - (i1 - i0) / tot)


def mem_available_gb() -> float:
    with open("/proc/meminfo") as f:
        for line in f:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) / (1024.0 * 1024.0)
    refuse("MemAvailable not found in /proc/meminfo")
    return 0.0  # unreachable; keeps the type checker honest


# ---------------------------------------------------------------------------- lock
def acquire_lock(pidfile: Path) -> None:
    if pidfile.exists():
        txt = pidfile.read_text().strip()
        try:
            pid = int(txt)
        except ValueError:
            pid = -1
        if pid > 0:
            try:
                os.kill(pid, 0)
                refuse(f"another runner is alive: pid {pid} in {pidfile}")
            except ProcessLookupError:
                pass  # stale pidfile; take over
            except PermissionError:
                refuse(f"another runner (pid {pid}) is alive under another user")
    pidfile.parent.mkdir(parents=True, exist_ok=True)
    pidfile.write_text(f"{os.getpid()}\n")


# ---------------------------------------------------------------------------- log
class Log:
    def __init__(self, path: Path | None, echo: bool):
        self.path = path
        self.echo = echo
        if path is not None:
            path.parent.mkdir(parents=True, exist_ok=True)

    def __call__(self, msg: str) -> None:
        line = f"{utc()} {msg}"
        if self.path is not None:
            with open(self.path, "a") as f:
                f.write(line + "\n")
        if self.echo:
            print(line, flush=True)


# --------------------------------------------------------------------------- queue
def list_entries(root: Path) -> dict[str, list[Path]]:
    out: dict[str, list[Path]] = {}
    for team in TEAMS:
        d = root / team
        if not d.is_dir():
            continue
        files = sorted((p for p in d.glob("*.json")), key=lambda p: p.stat().st_mtime)
        out[team] = files
    return out


def move_refused(path: Path, reasons: list[str], log: Log) -> None:
    dst_dir = path.parent / "refused"
    dst_dir.mkdir(exist_ok=True)
    dst = dst_dir / path.name
    shutil.move(str(path), str(dst))
    (dst_dir / (path.stem + ".REFUSED.txt")).write_text(
        f"{utc()} REFUSED by queue_runner; validator reasons:\n" + "\n".join(reasons) + "\n")
    log(f"REFUSED {path} -> {dst}: " + " | ".join(reasons))


def launch(entry: dict, path: Path, root: Path, log: Log) -> tuple[int, int]:
    cwd = Path(entry["cwd"])
    case_id = entry["case_id"]
    argv = entry["launch_cmd"]
    quoted = " ".join("'" + str(a).replace("'", "'\"'\"'") + "'" for a in argv)
    status = cwd / f"STATUS.{case_id}"
    out = cwd / "launcher.queue.out"
    # The STATUS file records the LAUNCH ARGV's exit status -- an INFRASTRUCTURE
    # record (L-342). It never claims the solver's rc: a launcher that refused at zero
    # compute and exited 0 would otherwise read as a completed solve (heat-transfer
    # T5_X_2d, 2026-08-26). Rule 4 is applied from the case's own RC/log files.
    inner = (f"cd '{cwd}' && {quoted} > '{out}' 2>&1; R=$?; "
             f"echo \"launcher_rc=$R end=$(date -u +%Y-%m-%dT%H:%M:%SZ) "
             f"note=exit-status-of-the-launch-argv-NOT-the-solver-rc\" > '{status}'")
    with open(os.devnull, "rb") as devnull:
        proc = subprocess.Popen(
            ["setsid", "nohup", "bash", "-c", inner],
            stdin=devnull, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True, cwd=str(cwd))
    pid = proc.pid
    try:
        sid = os.getsid(pid)
    except ProcessLookupError:
        sid = -1  # already finished (a trivial argv); the STATUS file is the record
    launched_dir = path.parent / "launched"
    launched_dir.mkdir(exist_ok=True)
    dst = launched_dir / path.name
    shutil.move(str(path), str(dst))
    meta = dict(entry)
    meta["_launch"] = dict(utc=utc(), pid=pid, sid=sid, status_file=str(status),
                           wrapper_out=str(out), started_epoch=time.time())
    # L-342 (Sanaa, 2026-08-26): a bookkeeping failure invalidates the bookkeeping,
    # never the physics artefacts. The completion record therefore names which of
    # its fields a grader may refuse on and which it may only REPORT on.
    meta["_field_classes"] = dict(
        physics_critical=[f"STATUS.{case_id} (rc inside the detached wrapper)",
                          "the case's own log End line, endTime fields and 0/ age guard"],
        infrastructure=["_launch.pid", "_launch.sid", "_launch.utc", "_launch.started_epoch",
                        "LAUNCH_LOG.tsv row", "CAP_OVERRUN.txt", "ESTIMATE_OVERRUN.txt", "cost_core_min_estimate",
                        "memory_floor_gb", "runner.log lines"],
        rule="a missing or inconsistent INFRASTRUCTURE field is a BOOKKEEPING DEFECT "
             "reported beside the verdict and voids only the cost claim; only a "
             "PHYSICS_CRITICAL field may produce NOT A RESULT (L-342)")
    dst.write_text(json.dumps(meta, indent=2) + "\n")
    with open(root / "LAUNCH_LOG.tsv", "a") as f:
        f.write("\t".join(str(x) for x in (
            utc(), entry["team"], case_id, pid, sid, entry["ranks"],
            entry["cost_core_min_estimate"], entry["prereg_commit"], status)) + "\n")
    log(f"LAUNCHED team={entry['team']} case={case_id} pid={pid} sid={sid} "
        f"ranks={entry['ranks']} est={entry['cost_core_min_estimate']} core-min "
        f"prereg={entry['prereg_commit'][:8]} STATUS={status}")
    return pid, sid


def cap_watch(root: Path, log: Log, now: float | None = None) -> None:
    """Runaway guard that REPORTS. Never kills.

    Two flags, keyed on what the entry actually registered (cfd supervisor's order,
    2026-08-26 17:46Z, after F20's flag fired at 1.10 x its ESTIMATE while the run sat at
    29 % of its CAP):
      * entry carries a numeric `cap_core_min_registered` > 0  ->  `CAP_OVERRUN.txt` at
        1.00 x cap x 60 / ranks seconds elapsed, and NOT before;
      * no such field  ->  `ESTIMATE_OVERRUN.txt` at 1.10 x cost_core_min_estimate x 60 /
        ranks, whose text says it is an ESTIMATE overrun and not a cap.
    Both say REPORTED NOT ENFORCED; neither kills (COMPUTE_BUDGET_CHARTER).  `now` is
    injectable so --selftest can drive the clock; the daemon passes nothing.
    """
    t_now = time.time() if now is None else float(now)
    for team in TEAMS:
        d = root / team / "launched"
        if not d.is_dir():
            continue
        for p in d.glob("*.json"):
            try:
                meta = json.loads(p.read_text())
            except (OSError, json.JSONDecodeError):
                continue
            li = meta.get("_launch") or {}
            status = Path(li.get("status_file", "/nonexistent"))
            if status.exists() or "started_epoch" not in li:
                continue
            ranks = max(1, int(meta.get("ranks", 1)))
            est = float(meta["cost_core_min_estimate"])
            elapsed = t_now - float(li["started_epoch"])
            cap = meta.get("cap_core_min_registered")
            has_cap = isinstance(cap, (int, float)) and not isinstance(cap, bool) and cap > 0
            if has_cap:
                allowed_wall = float(cap) * 60.0 / ranks * 1.00
                flag = Path(meta["cwd"]) / "CAP_OVERRUN.txt"
                text = (f"{utc()} CAP OVERRUN REPORTED, NOT ENFORCED: case {meta['case_id']} "
                        f"elapsed {elapsed:.0f} s > 1.00 x registered CAP {allowed_wall:.0f} s "
                        f"({cap} core-min cap / {ranks} ranks; estimate {est} core-min). "
                        f"The run was NOT killed (caps report; COMPUTE_BUDGET_CHARTER).\n")
                word = "CAP-OVERRUN"
            else:
                allowed_wall = est * 60.0 / ranks * 1.10
                flag = Path(meta["cwd"]) / "ESTIMATE_OVERRUN.txt"
                text = (f"{utc()} ESTIMATE OVERRUN REPORTED, NOT ENFORCED -- THIS IS AN ESTIMATE "
                        f"OVERRUN, NOT A CAP: the entry for case {meta['case_id']} carries no "
                        f"cap_core_min_registered, so the only registered figure is the estimate; "
                        f"elapsed {elapsed:.0f} s > 1.10 x estimate {allowed_wall/1.1:.0f} s "
                        f"({est} core-min / {ranks} ranks). No cap was crossed by this record. "
                        f"The run was NOT killed (caps report; COMPUTE_BUDGET_CHARTER).\n")
                word = "ESTIMATE-OVERRUN"
            if elapsed > allowed_wall and not flag.exists():
                flag.write_text(text)
                log(f"{word} reported for {meta['case_id']} -> {flag}")


def measure_box(busy_window: float) -> tuple[float, float]:
    """The daemon's real reading: (busy %, MemAvailable GB) from /proc."""
    return busy_percent(busy_window), mem_available_gb()


def tick(root: Path, log: Log, busy_ceiling: float, core_fraction: float,
         busy_window: float, rr_state: dict, launch_fn=launch, measure=None) -> str:
    """One scheduling pass. Returns one of EMPTY / HELD / LAUNCHED / REFUSED-ONLY.

    `measure` is injectable: a callable returning (busy_percent, mem_available_gb).
    The daemon passes nothing and reads /proc; --selftest passes a fake returning
    known values so its controls do not depend on the live box's load (2026-08-26:
    control 5b failed on a box at >= 94 % busy and passed on re-run -- the L-339
    class, a test users learn to re-run).
    """
    cap_watch(root, log)
    queues = list_entries(root)
    total = sum(len(v) for v in queues.values())
    if total == 0:
        log("EMPTY: no entries in any team queue; nothing launched")
        return "EMPTY"
    busy, mem = measure_box(busy_window) if measure is None else measure()
    busy, mem = float(busy), float(mem)
    ncpu = os.cpu_count() or 1
    busy_cores = busy / 100.0 * ncpu
    log(f"box busy={busy:.1f}% (~{busy_cores:.1f}/{ncpu} cores) MemAvailable={mem:.1f} GB; "
        f"{total} entr{'y' if total == 1 else 'ies'} queued")
    order = [t for t in TEAMS if queues.get(t)]
    start = rr_state.get("cursor", 0) % max(1, len(order))
    order = order[start:] + order[:start]
    any_refused = False
    for team in order:
        for path in queues[team]:
            entry, fails = qec.load_entry(path)
            if entry is not None:
                fails = qec.validate(entry, REPO)
            if fails:
                move_refused(path, fails, log)
                any_refused = True
                continue
            host = str(entry.get("host", "local")).strip().lower()
            if host not in ("", "local", "localhost", os.uname().nodename.lower()):
                log(f"SKIP {path}: host={host!r} is not this box; remote dispatch is not "
                    f"this runner's")
                continue
            ranks = int(entry["ranks"])
            floor = float(entry.get("memory_floor_gb", 0.0))
            if busy >= busy_ceiling:
                log(f"HELD {path.name}: busy {busy:.1f}% >= ceiling {busy_ceiling}%")
                return "HELD"
            if busy_cores + ranks > core_fraction * ncpu:
                # first-fit over the WHOLE queue: a held wide entry must not block a
                # narrow one behind it (heat-transfer T5 lane, 2026-08-26 16:4xZ)
                log(f"HELD {path.name}: {busy_cores:.1f} busy + {ranks} ranks > "
                    f"{core_fraction} x {ncpu} cores; trying the next entry")
                continue
            if mem < floor:
                log(f"HELD {path.name}: MemAvailable {mem:.1f} GB < registered floor {floor} GB")
                continue
            launch_fn(entry, path, root, log)
            rr_state["cursor"] = (TEAMS.index(team) + 1) % len(TEAMS)
            return "LAUNCHED"
    if any_refused:
        return "REFUSED-ONLY"
    log("HELD: entries present but none launchable this tick")
    return "HELD"


# ------------------------------------------------------------------------ selftest
def _count_asserts() -> int:
    import ast
    return sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(Path(__file__).read_text())))


def selftest() -> int:
    checks: list[tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        checks.append((name, ok, detail))
        print(("  ok   " if ok else "  FAIL ") + name + (f"  [{detail}]" if detail else ""))

    print("queue_runner.py --selftest (planted controls in a scratch root; nothing real is touched)")
    n_assert = _count_asserts()
    check("0 ast.Assert nodes in this file", n_assert == 0, f"found {n_assert}")

    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    tmp = Path(tempfile.mkdtemp(prefix="queue_runner_selftest_"))
    root = tmp / "queue"
    for t in TEAMS:
        (root / t).mkdir(parents=True)
    log = Log(tmp / "runner.log", echo=False)
    rr: dict = {}

    # The box reading is INJECTED for every control below: a quiet box (10 % busy,
    # 100 GB free), so no control depends on the live load. Control 5c proves the
    # injected value is the one consulted by handing in a saturated reading.
    def quiet():
        return 10.0, 100.0

    def saturated():
        return 99.0, 100.0

    # control 1: EMPTY queue -> zero launches, says EMPTY
    r = tick(root, log, 85.0, 0.9, 0.2, rr, measure=quiet)
    empty_text = (tmp / "runner.log").read_text()
    check("empty queue -> EMPTY, no LAUNCH_LOG", r == "EMPTY" and not (root / "LAUNCH_LOG.tsv").exists())

    # control 2: one valid entry whose argv is `true` -> exactly one launch, STATUS rc=0
    case_dir = tmp / "case_ok"
    case_dir.mkdir()
    good = dict(team="cfd", case_id="SELFTEST_OK", prereg_commit=head,
                prereg_path="CLAUDE.md", launch_cmd=["true"], cwd=str(case_dir), ranks=1,
                cost_core_min_estimate=0.01,
                cost_basis="derived, not measured: selftest placeholder", memory_floor_gb=0.5,
                enqueued_by="queue_runner selftest")
    (root / "cfd" / "SELFTEST_OK.json").write_text(json.dumps(good))
    r = tick(root, log, 100.0, 1.0, 0.2, rr, measure=quiet)
    for _ in range(50):
        if (case_dir / "STATUS.SELFTEST_OK").exists():
            break
        time.sleep(0.1)
    st = (case_dir / "STATUS.SELFTEST_OK").read_text() if (case_dir / "STATUS.SELFTEST_OK").exists() else ""
    n_launch = len((root / "LAUNCH_LOG.tsv").read_text().splitlines()) if (root / "LAUNCH_LOG.tsv").exists() else 0
    check("valid entry -> LAUNCHED once, STATUS launcher_rc=0 (labelled as launcher rc), entry moved to launched/",
          r == "LAUNCHED" and n_launch == 1 and st.startswith("launcher_rc=0") and "NOT-the-solver-rc" in st and
          (root / "cfd" / "launched" / "SELFTEST_OK.json").exists() and
          not (root / "cfd" / "SELFTEST_OK.json").exists(),
          f"tick={r} launches={n_launch} status={st.strip()!r}")
    # a second tick must NOT relaunch it
    r2 = tick(root, log, 100.0, 1.0, 0.2, rr, measure=quiet)
    n_launch2 = len((root / "LAUNCH_LOG.tsv").read_text().splitlines())
    check("second tick does not relaunch a launched entry", r2 == "EMPTY" and n_launch2 == 1)
    rec = json.loads((root / "cfd" / "launched" / "SELFTEST_OK.json").read_text())
    fc = rec.get("_field_classes", {})
    check("launched record carries the L-342 field-class split (physics_critical / infrastructure)",
          any("STATUS.SELFTEST_OK" in x for x in fc.get("physics_critical", [])) and
          "_launch.pid" in fc.get("infrastructure", []) and "L-342" in fc.get("rule", ""))

    # control 3: entry missing prereg_commit -> REFUSED and moved, never launched
    bad = dict(good)
    bad.pop("prereg_commit")
    bad["case_id"] = "SELFTEST_BAD"
    (root / "cfd" / "SELFTEST_BAD.json").write_text(json.dumps(bad))
    r3 = tick(root, log, 100.0, 1.0, 0.2, rr, measure=quiet)
    n_launch3 = len((root / "LAUNCH_LOG.tsv").read_text().splitlines())
    check("entry missing prereg_commit -> REFUSED, moved to refused/, no launch",
          r3 == "REFUSED-ONLY" and n_launch3 == 1 and
          (root / "cfd" / "refused" / "SELFTEST_BAD.json").exists() and
          (root / "cfd" / "refused" / "SELFTEST_BAD.REFUSED.txt").exists())

    # control 4: a bad-sha entry (wrong commit) is refused by the validator's git check
    bad2 = dict(good)
    bad2["case_id"] = "SELFTEST_BADSHA"
    bad2["prereg_commit"] = qec.NONEXISTENT_SHA
    (root / "cfd" / "SELFTEST_BADSHA.json").write_text(json.dumps(bad2))
    r4 = tick(root, log, 100.0, 1.0, 0.2, rr, measure=quiet)
    check("entry with a nonexistent prereg sha -> REFUSED", r4 == "REFUSED-ONLY" and
          (root / "cfd" / "refused" / "SELFTEST_BADSHA.json").exists())

    # control 5: ceiling holds a valid entry
    good2 = dict(good)
    good2["case_id"] = "SELFTEST_HELD"
    (root / "cfd" / "SELFTEST_HELD.json").write_text(json.dumps(good2))
    r5 = tick(root, log, 0.0, 1.0, 0.2, rr, measure=quiet)   # ceiling 0 % -> everything is held
    check("busy ceiling 0% -> HELD, entry stays queued", r5 == "HELD" and
          (root / "cfd" / "SELFTEST_HELD.json").exists())

    # control 5b: a held WIDE entry must not block a narrow one queued behind it
    wide = dict(good); wide["case_id"] = "SELFTEST_WIDE"; wide["ranks"] = 10 ** 6
    (root / "cfd" / "SELFTEST_HELD.json").unlink()
    (root / "cfd" / "SELFTEST_WIDE.json").write_text(json.dumps(wide))
    time.sleep(0.05)
    narrow_dir = tmp / "case_narrow"; narrow_dir.mkdir()
    narrow = dict(good); narrow["case_id"] = "SELFTEST_NARROW"; narrow["cwd"] = str(narrow_dir)
    (root / "cfd" / "SELFTEST_NARROW.json").write_text(json.dumps(narrow))
    r5b = tick(root, log, 100.0, 1.0, 0.2, rr, measure=quiet)
    check("held wide entry does not block the narrow entry behind it (first-fit over the queue)",
          r5b == "LAUNCHED" and (root / "cfd" / "launched" / "SELFTEST_NARROW.json").exists()
          and (root / "cfd" / "SELFTEST_WIDE.json").exists())
    (root / "cfd" / "SELFTEST_WIDE.json").unlink()
    (root / "cfd" / "SELFTEST_HELD.json").write_text(json.dumps(good2))
    # control 5c: the injected reading is the one consulted -- the SAME valid entry under
    # a saturated fake (99 %) against the default 85 % ceiling must be HELD, and under
    # the quiet fake must launch. The control flips on the injection alone.
    r5c_held = tick(root, log, 85.0, 1.0, 0.2, rr, measure=saturated)
    still_queued = (root / "cfd" / "SELFTEST_HELD.json").exists()
    r5c_go = tick(root, log, 85.0, 1.0, 0.2, rr, measure=quiet)
    held_log = (tmp / "runner.log").read_text()
    check("injected busy reading governs: 99% fake -> HELD (entry stays), 10% fake -> LAUNCHED",
          r5c_held == "HELD" and still_queued and r5c_go == "LAUNCHED" and
          "busy 99.0% >= ceiling 85.0%" in held_log and
          (root / "cfd" / "launched" / "SELFTEST_HELD.json").exists(),
          f"held={r5c_held} go={r5c_go}")
    n_launch_5c = len((root / "LAUNCH_LOG.tsv").read_text().splitlines())
    (root / "cfd" / "SELFTEST_HELD.json").write_text(json.dumps(good2))
    # control 6: remote host entry is skipped, not launched
    good3 = dict(good)
    good3["case_id"] = "SELFTEST_REMOTE"
    good3["host"] = "3.15.199.152"
    (root / "cfd" / "SELFTEST_HELD.json").unlink()
    (root / "cfd" / "SELFTEST_REMOTE.json").write_text(json.dumps(good3))
    r6 = tick(root, log, 100.0, 1.0, 0.2, rr, measure=quiet)
    check("remote-host entry -> SKIP, stays queued, no launch", r6 == "HELD" and
          (root / "cfd" / "SELFTEST_REMOTE.json").exists() and
          len((root / "LAUNCH_LOG.tsv").read_text().splitlines()) == n_launch_5c)

    # control 7: cap watch keys on the registered CAP when the entry carries one --
    # CAP_OVERRUN.txt at 1.00 x cap x 60 / ranks, and NOT before; never ESTIMATE_OVERRUN.txt
    cap_dir = tmp / "case_cap"; cap_dir.mkdir()
    t0 = 1_000_000.0
    capped = dict(good); capped["case_id"] = "SELFTEST_CAP"; capped["cwd"] = str(cap_dir)
    capped["cost_core_min_estimate"] = 0.01           # 0.66 s at 1.10x -- long past at every probe below
    capped["cap_core_min_registered"] = 1.0           # 60 s at 1.00x, ranks 1
    capped["_launch"] = dict(status_file=str(cap_dir / "STATUS.SELFTEST_CAP"), started_epoch=t0)
    (root / "cfd" / "launched" / "SELFTEST_CAP.json").write_text(json.dumps(capped))
    cap_watch(root, log, now=t0 + 59.0)
    before = not (cap_dir / "CAP_OVERRUN.txt").exists() and not (cap_dir / "ESTIMATE_OVERRUN.txt").exists()
    cap_watch(root, log, now=t0 + 61.0)
    cap_txt = (cap_dir / "CAP_OVERRUN.txt").read_text() if (cap_dir / "CAP_OVERRUN.txt").exists() else ""
    check("entry WITH cap_core_min_registered -> CAP_OVERRUN.txt at 1.00 x cap, not at 59 s, present at 61 s",
          before and "1.00 x registered CAP 60 s" in cap_txt and "NOT ENFORCED" in cap_txt,
          f"before={before} text={cap_txt.strip()[:60]!r}")
    check("entry WITH cap never gets ESTIMATE_OVERRUN.txt (estimate long exceeded, cap governs)",
          not (cap_dir / "ESTIMATE_OVERRUN.txt").exists())
    # control 7b: the guard mutated -- strip the cap field and the SAME record must flip to the
    # estimate path, so the CAP file above is coming from the field and not from elsewhere
    est_dir = tmp / "case_est"; est_dir.mkdir()
    uncapped = dict(capped); uncapped["case_id"] = "SELFTEST_EST"; uncapped["cwd"] = str(est_dir)
    uncapped.pop("cap_core_min_registered")
    uncapped["cost_core_min_estimate"] = 1.0          # 66 s at 1.10x, ranks 1
    uncapped["_launch"] = dict(status_file=str(est_dir / "STATUS.SELFTEST_EST"), started_epoch=t0)
    (root / "cfd" / "launched" / "SELFTEST_EST.json").write_text(json.dumps(uncapped))
    cap_watch(root, log, now=t0 + 65.0)
    before_e = not (est_dir / "ESTIMATE_OVERRUN.txt").exists() and not (est_dir / "CAP_OVERRUN.txt").exists()
    cap_watch(root, log, now=t0 + 67.0)
    est_txt = (est_dir / "ESTIMATE_OVERRUN.txt").read_text() if (est_dir / "ESTIMATE_OVERRUN.txt").exists() else ""
    check("entry WITHOUT cap -> ESTIMATE_OVERRUN.txt at 1.10 x estimate, not at 65 s, present at 67 s, says NOT A CAP",
          before_e and "ESTIMATE OVERRUN" in est_txt and "NOT A CAP" in est_txt and "NOT ENFORCED" in est_txt,
          f"before={before_e} text={est_txt.strip()[:60]!r}")
    check("entry WITHOUT cap never gets CAP_OVERRUN.txt", not (est_dir / "CAP_OVERRUN.txt").exists())
    # control 7c: a STATUS file (run finished) silences both watches
    fin_dir = tmp / "case_fin"; fin_dir.mkdir()
    finished = dict(uncapped); finished["case_id"] = "SELFTEST_FIN"; finished["cwd"] = str(fin_dir)
    finished["_launch"] = dict(status_file=str(fin_dir / "STATUS.SELFTEST_FIN"), started_epoch=t0)
    (fin_dir / "STATUS.SELFTEST_FIN").write_text("launcher_rc=0\n")
    (root / "cfd" / "launched" / "SELFTEST_FIN.json").write_text(json.dumps(finished))
    cap_watch(root, log, now=t0 + 10_000.0)
    check("finished entry (STATUS present) -> neither overrun file, however late",
          not (fin_dir / "ESTIMATE_OVERRUN.txt").exists() and not (fin_dir / "CAP_OVERRUN.txt").exists())
    watch_log = (tmp / "runner.log").read_text()
    check("runner.log carries one CAP-OVERRUN and one ESTIMATE-OVERRUN line, and they do not read alike",
          watch_log.count("CAP-OVERRUN reported") == 1 and watch_log.count("ESTIMATE-OVERRUN reported") == 1)

    full_log = (tmp / "runner.log").read_text()
    check("EMPTY and LAUNCHED outputs do not read alike",
          "EMPTY:" in empty_text and "LAUNCHED" not in empty_text and "LAUNCHED" in full_log)

    # control 8: the exit path. A real --daemon subprocess on a SCRATCH root (its own
    # pidfile, its own log; the live runner is untouched) is sent SIGTERM and must leave
    # `EXIT reason=SIGTERM pid=<its pid>` in its runner.log and exit 128+15. The zero is
    # planted: the EXIT line must be ABSENT before the signal and PRESENT after it.
    droot = tmp / "daemon_root"
    for t in TEAMS:
        (droot / t).mkdir(parents=True)
    dlog = droot / "runner.log"
    proc = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "--daemon",
                             "--root", str(droot), "--interval", "0.2"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    started = False
    for _ in range(100):
        if dlog.exists() and "START pid=" in dlog.read_text():
            started = True
            break
        time.sleep(0.1)
    before_exit = dlog.read_text() if dlog.exists() else ""
    exit_absent_before = "EXIT reason=" not in before_exit
    if started:
        proc.send_signal(signal.SIGTERM)
    try:
        rc_d = proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        rc_d = None
    after_exit = dlog.read_text() if dlog.exists() else ""
    want = f"EXIT reason=SIGTERM pid={proc.pid}"
    check("SIGTERM to a scratch-root daemon -> `EXIT reason=SIGTERM pid=<pid>` logged, rc 143; "
          "line absent before the signal",
          started and exit_absent_before and want in after_exit and rc_d == 143,
          f"started={started} absent_before={exit_absent_before} rc={rc_d} "
          f"tail={after_exit.strip().splitlines()[-1][-70:] if after_exit.strip() else ''!r}")
    # control 8b: a normal --once exit logs `EXIT reason=normal` (the word set is closed)
    oroot = tmp / "once_root"
    for t in TEAMS:
        (oroot / t).mkdir(parents=True)
    po = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--once",
                         "--root", str(oroot)], capture_output=True, text=True)
    olog = (oroot / "runner.log").read_text() if (oroot / "runner.log").exists() else ""
    check("--once exit logs `EXIT reason=normal pid=<pid>`, rc 0",
          po.returncode == 0 and "EXIT reason=normal pid=" in olog and "EXIT reason=SIG" not in olog)

    shutil.rmtree(tmp)  # scratch root only, created by mkdtemp above
    n_fail = sum(1 for _, ok, _ in checks if not ok)
    if n_fail:
        print(f"SELFTEST FAIL: {n_fail} of {len(checks)} checks failed")
        return 1
    if len(checks) >= 10:
        print(f"SELFTEST PASS: {len(checks)}/{len(checks)} checks, 0 asserts")
        return 0
    print("SELFTEST FAIL: too few checks ran")
    return 1


# ------------------------------------------------------------------------------ main
def main(argv: list[str]) -> int:
    if sys.flags.optimize:
        print("REFUSE: queue_runner does not run under python -O (its guards would be stripped)")
        return EXIT_REFUSE
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--daemon", action="store_true")
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--busy-ceiling", type=float, default=85.0,
                    help="do not launch when busy %% >= this (Sanaa's 80-90 %% band)")
    ap.add_argument("--core-fraction", type=float, default=0.9)
    ap.add_argument("--interval", type=float, default=60.0)
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not (a.daemon or a.once):
        ap.print_help()
        return 1
    root = Path(a.root)
    if not root.is_dir():
        refuse(f"queue root {root} is not a directory")
    log = Log(root / "runner.log", echo=True)
    acquire_lock(root / "runner.pid")
    pid = os.getpid()
    handled = install_signal_handlers()
    log(f"START pid={pid} sid={os.getsid(0)} root={root} ceiling={a.busy_ceiling}% "
        f"core_fraction={a.core_fraction} interval={a.interval}s HEAD="
        + subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
                         capture_output=True, text=True).stdout.strip()
        + f" exit_logging={'+'.join(handled)}+exception+normal")
    rr: dict = {}
    # THE ONE EXIT PATH. Every way out of the loop below logs `EXIT reason=... pid=...`
    # before the process ends: a handled signal (by name), an escaping exception (class
    # and message, plus the innermost frame), or a normal --once return. Nothing here
    # catches-and-continues: an exception that escapes a tick is logged and RE-RAISED,
    # so the process dies loudly and cron (queue_runner.sh) restarts it with a record.
    try:
        while True:
            try:
                tick(root, log, a.busy_ceiling, a.core_fraction, 5.0, rr)
            except Refusal as exc:
                log(f"REFUSED (tick): {exc}")
            except Exception as exc:  # one bad ENTRY must not stop the queue; it is logged
                log(f"ERROR (tick, continuing): {type(exc).__name__}: {exc}")
            if a.once:
                log(f"EXIT reason=normal pid={pid}")
                return 0
            time.sleep(a.interval)
    except Signalled as sig:
        log(f"EXIT reason={sig.name} pid={pid}")
        return 128 + sig.signum
    except BaseException as exc:
        frames = traceback.extract_tb(exc.__traceback__)
        where = f" at {frames[-1].filename}:{frames[-1].lineno}" if frames else ""
        log(f"EXIT reason={type(exc).__name__}: {exc} pid={pid}{where}")
        raise


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Refusal as exc:
        print(f"REFUSED: {exc}")
        sys.exit(EXIT_REFUSE)
