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
RE-ARMED CWD (2026-08-26, ansys VMFL064-R2 20:45Z and heat-transfer T5_C 20:52/20:54Z): a
launched record keyed on case_id alone was read by cap_watch as governing a cwd whose
owner had removed STATUS for a re-run, and the relaunch then overwrote the record the
flag was about.  Now (1) a launch ARCHIVES any current record of the same name or
case_id as `<name>.<its utc, colons stripped>.json` (log word `ARCHIVED`; nothing
deleted) and cap_watch watches only current records; (2) a record whose STATUS has been
seen is stamped `_launch.status_seen_utc` and never fires again; (3) every flag names
the launch it judges (`launch_utc= pid= started_epoch=`) and is written at most once per
launch record.  `--selftest` plants the sequence and both mutations (each must flip).

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
import re
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

# A launched record is CURRENT while it is `launched/<name>.json`. When the same case_id is
# launched again (its owner removed STATUS and re-enqueued -- ansys VMFL064-R2 20:45Z and
# heat-transfer T5_C -> T5_C_v2 20:54Z, 2026-08-26), the previous record is ARCHIVED, never
# deleted, as `launched/<name>.<its _launch.utc with the colons stripped>.json`, e.g.
# `VMFL064-R2.2026-08-26T174913Z.json`. cap_watch watches ONLY current records: a file
# whose name matches ARCHIVED_RE is never watched, so a stale record cannot judge a cwd
# that somebody else has re-armed. The optional `.<n>` guards a same-second collision.
ARCHIVED_RE = re.compile(r"\.\d{4}-\d{2}-\d{2}T\d{6}Z(\.\d+)?\.json$")


def is_current_record(p: Path) -> bool:
    return p.suffix == ".json" and ARCHIVED_RE.search(p.name) is None


def _write_json(p: Path, obj: dict) -> None:
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2) + "\n")
    os.replace(tmp, p)


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


def archive_previous_records(launched_dir: Path, case_id: str, new_name: str, log: Log) -> list[Path]:
    """Before a new launch record is written, every CURRENT record the new launch would
    shadow -- the same file name, or the same case_id under another name (heat-transfer's
    T5_C.json beside T5_C_v2.json) -- is RENAMED to `<stem>.<its _launch.utc, colons
    stripped>.json`. Nothing is deleted. A record keyed on case_id alone was read by
    cap_watch as governing a cwd its owner had already re-armed: ansys VMFL064-R2,
    2026-08-26 -- CAP_OVERRUN stamped 20:45:38Z against the 17:49:13Z record (elapsed
    10,585 s), and the 20:45:43Z relaunch then OVERWROTE that record, so the flag named a
    launch nobody could find any more."""
    archived: list[Path] = []
    for p in sorted(launched_dir.glob("*.json")):
        if not is_current_record(p):
            continue
        try:
            old = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError):
            old = {}
        if p.name != new_name and old.get("case_id") != case_id:
            continue
        li = old.get("_launch") or {}
        old_utc = str(li.get("utc") or datetime.fromtimestamp(
            p.stat().st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        stamp = old_utc.replace(":", "")
        dst = p.with_name(f"{p.stem}.{stamp}.json")
        n = 1
        while dst.exists():
            n += 1
            dst = p.with_name(f"{p.stem}.{stamp}.{n}.json")
        os.replace(p, dst)
        log(f"ARCHIVED previous launch record for {case_id} ({old_utc}, pid {li.get('pid', 'unknown')}) "
            f"-> {dst.name}")
        archived.append(dst)
    return archived


def launch(entry: dict, path: Path, root: Path, log: Log, archive: bool = True) -> tuple[int, int]:
    """`archive` is True in every real call; --selftest passes False ONLY for the mutation
    control that must reproduce the stale-flag defect (the control has to flip)."""
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
    if archive:
        archive_previous_records(launched_dir, case_id, dst.name, log)
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


def cap_watch(root: Path, log: Log, now: float | None = None, retire_seen: bool = True) -> None:
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

    WHICH LAUNCH A FLAG IS ABOUT (2026-08-26, after VMFL064-R2 and T5_C):
      * only CURRENT records are watched -- `launched/<name>.json`, never a name matching
        ARCHIVED_RE (a record retired by a later launch of the same case_id);
      * a record whose STATUS has been SEEN is stamped `_launch.status_seen_utc` once and is
        finished for good: if STATUS later vanishes, that is somebody re-arming the cwd for
        a re-run, not this launch running on (`retire_seen=False` only in the selftest's
        mutation control, which must reproduce the stale flag);
      * the flag text names the launch it judges -- `launch_utc=<_launch.utc> pid=<pid>
        started_epoch=<epoch>` -- and is written AT MOST ONCE PER LAUNCH RECORD: an existing
        flag that already names this launch is left alone; one that names another launch of
        the same cwd is superseded, its text kept beneath the new one, not deleted.
      Before this change the flag was written once per FILE (`not flag.exists()`): a stale
      flag from an earlier launch silenced every later launch of the same cwd for ever.
    """
    t_now = time.time() if now is None else float(now)
    for team in TEAMS:
        d = root / team / "launched"
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.json")):
            if not is_current_record(p):
                continue  # archived record: a launch that a later launch has retired
            try:
                meta = json.loads(p.read_text())
            except (OSError, json.JSONDecodeError):
                continue
            li = meta.get("_launch") or {}
            status = Path(li.get("status_file", "/nonexistent"))
            if "started_epoch" not in li:
                continue
            if status.exists():
                if retire_seen and "status_seen_utc" not in li:
                    li["status_seen_utc"] = utc()
                    meta["_launch"] = li
                    _write_json(p, meta)
                continue
            if retire_seen and "status_seen_utc" in li:
                continue  # this launch finished; the missing STATUS is a re-armed cwd
            ranks = max(1, int(meta.get("ranks", 1)))
            est = float(meta["cost_core_min_estimate"])
            elapsed = t_now - float(li["started_epoch"])
            ident = (f"launch_utc={li.get('utc', '?')} pid={li.get('pid', '?')} "
                     f"started_epoch={float(li['started_epoch']):.3f}")
            cap = meta.get("cap_core_min_registered")
            has_cap = isinstance(cap, (int, float)) and not isinstance(cap, bool) and cap > 0
            if has_cap:
                allowed_wall = float(cap) * 60.0 / ranks * 1.00
                flag = Path(meta["cwd"]) / "CAP_OVERRUN.txt"
                text = (f"{utc()} CAP OVERRUN REPORTED, NOT ENFORCED: case {meta['case_id']} "
                        f"[{ident}] "
                        f"elapsed {elapsed:.0f} s > 1.00 x registered CAP {allowed_wall:.0f} s "
                        f"({cap} core-min cap / {ranks} ranks; estimate {est} core-min). "
                        f"The run was NOT killed (caps report; COMPUTE_BUDGET_CHARTER).\n")
                word = "CAP-OVERRUN"
            else:
                allowed_wall = est * 60.0 / ranks * 1.10
                flag = Path(meta["cwd"]) / "ESTIMATE_OVERRUN.txt"
                text = (f"{utc()} ESTIMATE OVERRUN REPORTED, NOT ENFORCED -- THIS IS AN ESTIMATE "
                        f"OVERRUN, NOT A CAP: the entry for case {meta['case_id']} "
                        f"[{ident}] carries no "
                        f"cap_core_min_registered, so the only registered figure is the estimate; "
                        f"elapsed {elapsed:.0f} s > 1.10 x estimate {allowed_wall/1.1:.0f} s "
                        f"({est} core-min / {ranks} ranks). No cap was crossed by this record. "
                        f"The run was NOT killed (caps report; COMPUTE_BUDGET_CHARTER).\n")
                word = "ESTIMATE-OVERRUN"
            if elapsed <= allowed_wall:
                continue
            prior = flag.read_text() if flag.exists() else ""
            if ident in prior:
                continue  # already flagged for THIS launch record; one flag per launch
            if prior:
                text += ("--- the text below judged ANOTHER launch of this cwd; superseded, "
                         "kept, not deleted ---\n" + prior)
            flag.write_text(text)
            log(f"{word} reported for {meta['case_id']} [{ident}] -> {flag}")


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

    # control 9: the RE-ARMED cwd (ansys VMFL064-R2, 2026-08-26: first launch 17:49:13Z pid
    # 326419 finished; its owner removed STATUS for a re-run; CAP_OVERRUN stamped 20:45:38Z
    # with elapsed 10,585 s from the FIRST record; the 20:45:43Z relaunch pid 390178 then
    # overwrote that record. Same class: heat-transfer T5_C 17:41Z vs T5_C_v2 20:54Z).
    # Launch A goes through the REAL launch path (argv `true`), so its record carries a real
    # `_launch`. The `true` argv writes STATUS within milliseconds; where a control needs "a
    # run still going", STATUS is removed and the comment says so.
    def launch_case(name: str, entry: dict, status: Path, launch_fn=launch) -> dict:
        (root / "cfd" / name).write_text(json.dumps(entry))
        tick(root, log, 100.0, 1.0, 0.2, rr, launch_fn=launch_fn, measure=quiet)
        for _ in range(50):
            if status.exists():
                break
            time.sleep(0.1)
        return json.loads((root / "cfd" / "launched" / name).read_text())

    def flag_text(d: Path) -> str:
        f = d / "CAP_OVERRUN.txt"
        return f.read_text() if f.exists() else ""

    def archived_for(stem: str) -> list[Path]:
        return sorted(p for p in (root / "cfd" / "launched").glob(f"{stem}.*.json")
                      if not is_current_record(p))

    rearm_dir = tmp / "case_rearm"; rearm_dir.mkdir()
    rearm = dict(good); rearm["case_id"] = "SELFTEST_REARM"; rearm["cwd"] = str(rearm_dir)
    rearm["cap_core_min_registered"] = 1.0                   # 60 s at 1.00x, ranks 1
    rearm_status = rearm_dir / "STATUS.SELFTEST_REARM"
    rec_a = launch_case("SELFTEST_REARM.json", rearm, rearm_status)
    a_utc, a_pid, a_epoch = rec_a["_launch"]["utc"], rec_a["_launch"]["pid"], rec_a["_launch"]["started_epoch"]
    cap_watch(root, log, now=a_epoch + 10_000.0)                     # finished: nothing, however late
    quiet_finished = flag_text(rearm_dir) == ""
    stamped = "status_seen_utc" in json.loads((root / "cfd" / "launched" / "SELFTEST_REARM.json").read_text())["_launch"]
    # 9a: STATUS removed by the owner; the watcher runs BEFORE the relaunch (the 20:45:38Z window)
    rearm_status.unlink()
    cap_watch(root, log, now=a_epoch + 10_001.0)
    quiet_window = flag_text(rearm_dir) == ""
    check("re-armed cwd: launch A (real launch path, STATUS landed) -> no flag at +10,000 s; record stamped "
          "status_seen_utc; STATUS removed -> the finished record still writes nothing at +10,001 s",
          rearm_status.exists() is False and quiet_finished and stamped and quiet_window,
          f"finished_quiet={quiet_finished} stamped={stamped} window_quiet={quiet_window}")
    # 9b: mutation control -- the stamp not consulted -> the SAME window fires the STALE flag naming A
    cap_watch(root, log, now=a_epoch + 10_001.0, retire_seen=False)
    stale = flag_text(rearm_dir)
    check("mutation control (status_seen not consulted): the same window writes the STALE flag, "
          "elapsed 10001 s, naming launch A -- the control flips on the retirement alone",
          f"launch_utc={a_utc} pid={a_pid}" in stale and "elapsed 10001 s" in stale, f"text={stale.strip()[:90]!r}")
    # 9c: the same case_id, same file name, launched again (VMFL064-R2): A is ARCHIVED, B is fresh
    time.sleep(1.1)                                                  # so B's utc differs from A's
    rec_b = launch_case("SELFTEST_REARM.json", rearm, rearm_status)
    b_utc, b_pid, b_epoch = rec_b["_launch"]["utc"], rec_b["_launch"]["pid"], rec_b["_launch"]["started_epoch"]
    arch = archived_for("SELFTEST_REARM")
    arch_name = f"SELFTEST_REARM.{a_utc.replace(':', '')}.json"
    arch_ok = (len(arch) == 1 and arch[0].name == arch_name and
               json.loads(arch[0].read_text())["_launch"]["started_epoch"] == a_epoch)
    arch_line = f"ARCHIVED previous launch record for SELFTEST_REARM ({a_utc}, pid {a_pid})"
    check("relaunch of the same case_id -> previous record ARCHIVED as <id>.<utc>.json holding A's epoch "
          "(kept, not deleted), ARCHIVED line logged, new record has a fresh started_epoch and no stamp",
          arch_ok and arch_line in (tmp / "runner.log").read_text() and b_epoch > a_epoch and
          b_utc != a_utc and "status_seen_utc" not in rec_b["_launch"],
          f"archived={[p.name for p in arch]} b-a={b_epoch - a_epoch:.2f}s")
    # 9d: B is a long run -- its `true` STATUS is removed to stand in for a run still going
    rearm_status.unlink()
    cap_watch(root, log, now=b_epoch + 1.0)
    t1 = flag_text(rearm_dir)
    check("cap_watch at B + 1 s writes nothing about B (the archived A record is not watched; the "
          "flag on disk still names only A)",
          f"launch_utc={b_utc}" not in t1 and t1.count("CAP OVERRUN REPORTED") == 1)
    cap_watch(root, log, now=b_epoch + 61.0)
    t2 = flag_text(rearm_dir)
    top = t2.splitlines()[0] if t2 else ""
    check("cap_watch at B + cap + 1 s writes the flag naming the NEW launch (launch_utc=B pid=B) on top; "
          "A's superseded text kept beneath",
          f"launch_utc={b_utc} pid={b_pid}" in top and "elapsed 61 s" in top and
          f"launch_utc={a_utc} pid={a_pid}" in t2 and "superseded, kept" in t2, f"top={top[:100]!r}")
    cap_watch(root, log, now=b_epoch + 3_600.0)
    check("a flag naming this launch is written once: a later watch (B + 3600 s) leaves the file unchanged",
          flag_text(rearm_dir) == t2)
    # 9e: the T5_C class -- the same case_id re-enqueued under ANOTHER file name (T5_C.json,
    # then T5_C_v2.json, same cwd), the first launch never having written STATUS. First the
    # MUTATION (archive step disabled): the old record persists and fires the stale flag at
    # C + 1 s. Then the real path: the old record is archived by case_id and nothing fires.
    def no_archive(entry, path, root_, log_):
        return launch(entry, path, root_, log_, archive=False)

    results = {}
    for tag, fn in (("mut", no_archive), ("fix", launch)):
        d2 = tmp / f"case_rearm2_{tag}"; d2.mkdir()
        e2 = dict(rearm); e2["case_id"] = f"SELFTEST_REARM2_{tag}"; e2["cwd"] = str(d2)
        s2 = d2 / f"STATUS.SELFTEST_REARM2_{tag}"
        r_old = launch_case(f"SELFTEST_REARM2_{tag}.json", e2, s2)
        s2.unlink()                                              # never seen by the watcher (T5_C)
        time.sleep(1.1)
        r_new = launch_case(f"SELFTEST_REARM2_{tag}_v2.json", e2, s2, launch_fn=fn)
        # the first launch was hours ago (T5_C 17:41Z vs T5_C_v2 20:54Z): the file now
        # holding the old record -- current (mutation) or archived (fixed) -- has its
        # started_epoch set back 10,000 s, so "now = C + 1 s" is 10,001 s after it either way
        p_old = root / "cfd" / "launched" / f"SELFTEST_REARM2_{tag}.json"
        for h in ([p_old] if p_old.exists() else archived_for(f"SELFTEST_REARM2_{tag}")):
            rec = json.loads(h.read_text())
            rec["_launch"]["started_epoch"] -= 10_000.0
            h.write_text(json.dumps(rec))
        s2.unlink()                                              # the re-run is "still going"
        cap_watch(root, log, now=r_new["_launch"]["started_epoch"] + 1.0)
        results[tag] = dict(old=r_old["_launch"], new=r_new["_launch"], flag=flag_text(d2),
                            old_current=(root / "cfd" / "launched" / f"SELFTEST_REARM2_{tag}.json").exists(),
                            archived=[p.name for p in archived_for(f"SELFTEST_REARM2_{tag}")])
    m, f_ = results["mut"], results["fix"]
    check("T5_C class, mutation (archive disabled): old record under its own name persists beside the _v2 "
          "record and fires the STALE flag at C + 1 s naming the OLD launch",
          m["old_current"] and not m["archived"] and f"launch_utc={m['old']['utc']} pid={m['old']['pid']}" in m["flag"]
          and f"launch_utc={m['new']['utc']}" not in m["flag"], f"flag={m['flag'].strip()[:80]!r}")
    check("T5_C class, fixed: the old record is ARCHIVED by case_id when _v2 launches; nothing fires at C + 1 s "
          "-- the control flips on the archive step alone",
          not f_["old_current"] and f_["archived"] == [f"SELFTEST_REARM2_fix.{f_['old']['utc'].replace(':', '')}.json"]
          and f_["flag"] == "", f"archived={f_['archived']} flag={f_['flag'].strip()[:60]!r}")

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
