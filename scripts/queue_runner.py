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
(CAP_OVERRUN.txt beside the run) and never terminates (COMPUTE_BUDGET_CHARTER).  It never
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
and moved -- and the three outputs must not read alike.

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
import subprocess
import sys
import tempfile
import time
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
                        "LAUNCH_LOG.tsv row", "CAP_OVERRUN.txt", "cost_core_min_estimate",
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


def cap_watch(root: Path, log: Log) -> None:
    """Runaway guard that REPORTS. Never kills."""
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
            allowed_wall = float(meta["cost_core_min_estimate"]) * 60.0 / ranks * 1.10
            elapsed = time.time() - float(li["started_epoch"])
            flag = Path(meta["cwd"]) / "CAP_OVERRUN.txt"
            if elapsed > allowed_wall and not flag.exists():
                flag.write_text(
                    f"{utc()} CAP OVERRUN REPORTED, NOT ENFORCED: case {meta['case_id']} "
                    f"elapsed {elapsed:.0f} s > 1.10 x registered {allowed_wall/1.1:.0f} s "
                    f"({meta['cost_core_min_estimate']} core-min / {ranks} ranks). "
                    f"The run was NOT killed (caps report; COMPUTE_BUDGET_CHARTER).\n")
                log(f"CAP-OVERRUN reported for {meta['case_id']} -> {flag}")


def tick(root: Path, log: Log, busy_ceiling: float, core_fraction: float,
         busy_window: float, rr_state: dict, launch_fn=launch) -> str:
    """One scheduling pass. Returns one of EMPTY / HELD / LAUNCHED / REFUSED-ONLY."""
    cap_watch(root, log)
    queues = list_entries(root)
    total = sum(len(v) for v in queues.values())
    if total == 0:
        log("EMPTY: no entries in any team queue; nothing launched")
        return "EMPTY"
    busy = busy_percent(busy_window)
    mem = mem_available_gb()
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

    # control 1: EMPTY queue -> zero launches, says EMPTY
    r = tick(root, log, 85.0, 0.9, 0.2, rr)
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
    r = tick(root, log, 100.0, 1.0, 0.2, rr)
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
    r2 = tick(root, log, 100.0, 1.0, 0.2, rr)
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
    r3 = tick(root, log, 100.0, 1.0, 0.2, rr)
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
    r4 = tick(root, log, 100.0, 1.0, 0.2, rr)
    check("entry with a nonexistent prereg sha -> REFUSED", r4 == "REFUSED-ONLY" and
          (root / "cfd" / "refused" / "SELFTEST_BADSHA.json").exists())

    # control 5: ceiling holds a valid entry
    good2 = dict(good)
    good2["case_id"] = "SELFTEST_HELD"
    (root / "cfd" / "SELFTEST_HELD.json").write_text(json.dumps(good2))
    r5 = tick(root, log, 0.0, 1.0, 0.2, rr)   # ceiling 0 % -> everything is held
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
    r5b = tick(root, log, 100.0, 1.0, 0.2, rr)
    check("held wide entry does not block the narrow entry behind it (first-fit over the queue)",
          r5b == "LAUNCHED" and (root / "cfd" / "launched" / "SELFTEST_NARROW.json").exists()
          and (root / "cfd" / "SELFTEST_WIDE.json").exists())
    (root / "cfd" / "SELFTEST_WIDE.json").unlink()
    (root / "cfd" / "SELFTEST_HELD.json").write_text(json.dumps(good2))
    # control 6: remote host entry is skipped, not launched
    good3 = dict(good)
    good3["case_id"] = "SELFTEST_REMOTE"
    good3["host"] = "3.15.199.152"
    (root / "cfd" / "SELFTEST_HELD.json").unlink()
    (root / "cfd" / "SELFTEST_REMOTE.json").write_text(json.dumps(good3))
    r6 = tick(root, log, 100.0, 1.0, 0.2, rr)
    check("remote-host entry -> SKIP, stays queued, no launch", r6 == "HELD" and
          (root / "cfd" / "SELFTEST_REMOTE.json").exists() and
          len((root / "LAUNCH_LOG.tsv").read_text().splitlines()) == 2)

    full_log = (tmp / "runner.log").read_text()
    check("EMPTY and LAUNCHED outputs do not read alike",
          "EMPTY:" in empty_text and "LAUNCHED" not in empty_text and "LAUNCHED" in full_log)

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
    log(f"START pid={os.getpid()} sid={os.getsid(0)} root={root} ceiling={a.busy_ceiling}% "
        f"core_fraction={a.core_fraction} interval={a.interval}s HEAD="
        + subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
                         capture_output=True, text=True).stdout.strip())
    rr: dict = {}
    while True:
        try:
            tick(root, log, a.busy_ceiling, a.core_fraction, 5.0, rr)
        except Refusal as exc:
            log(f"REFUSED (tick): {exc}")
        except Exception as exc:  # the daemon must not die on one bad entry
            log(f"ERROR (tick, continuing): {type(exc).__name__}: {exc}")
        if a.once:
            return 0
        time.sleep(a.interval)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Refusal as exc:
        print(f"REFUSED: {exc}")
        sys.exit(EXIT_REFUSE)
