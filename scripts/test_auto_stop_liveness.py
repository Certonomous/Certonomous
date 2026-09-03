#!/usr/bin/env python3
"""Planted-control test for the auto-stop liveness decision (CLAUDE.md rule 3).

WHY THIS FILE EXISTS
--------------------
At 02:25:05Z on 2026-09-03 `/usr/local/bin/auto-stop.sh` logged
`idle 34min, shutting down` and SIGTERMed two containerized DAFoam sweeps
7 h 49 min into a 10.33 h budget. Measured from `docker inspect`:
a1wr_sweep_C_20260902T181935Z and a1wr_sweep_I_20260902T181935Z, both
StartedAt 2026-09-02T18:35:58Z, both FinishedAt 2026-09-03T02:25:05.6Z, both
ExitCode 143 (128+15 = SIGTERM), both User 0:0, both WorkingDir /mnt/case.
`scripts/auto_stop_patched.sh` adds clauses (4), (5a), (5b) and (6) to see that
work. This file is the control that says whether it does -- and, just as
importantly, whether it can still stop an idle box.

RULE 3, AND WHY EVERY HALF IS MANDATORY
---------------------------------------
"A zero from a reader not shown able to see a non-zero is not evidence."
Applied to a liveness gate the reading runs BOTH ways, and a third way:

  * the ALIVE half plants work the decision MUST see, and refuses if the
    decision says idle. Without it the patch is unproven.
  * the IDLE half plants a genuinely quiet box the decision MUST still stop,
    and refuses if the decision says alive. WITHOUT THIS HALF A PATCH THAT
    SIMPLY RETURNS "ALIVE" PASSES EVERY TEST -- and that patch is also a
    failure, because Sanaa pays for this box by the hour.
  * THE FLIP. Every ALIVE control is bound to a named IDLE partner and the two
    are asserted to DISAGREE. A pair that agrees is reported REFUSED even when
    both halves individually hit their expectation, because a detector wired to
    a constant can satisfy one half by accident but never both. This is the
    check that makes the other two mean anything, and it is why the pairs are
    declared in data below rather than left implicit.
  * DISCRIMINATION. Control Z1 runs the SAME planted busy state through the
    CURRENTLY INSTALLED script and requires it to shut down. If the installed
    script already saw the work, this whole suite would be measuring nothing.

WHAT THIS TEST WILL NOT DO
--------------------------
  * It never reads /home/ubuntu/certonomous-runs and never reads the real
    verification/queue. RUNROOTS, REPO (and so QUEUE_ROOT and the hold file),
    SESSIONS and MARKER are all injected at a scratch tree built per control
    under tempfile.mkdtemp().
  * It CANNOT power the box off, and this is enforced twice over rather than
    asserted once. (a) AUTO_STOP_DRY_RUN=1 and DRY_RUN=1 are exported for every
    invocation, and the script's only `sudo shutdown` line is guarded by
    `[ -n "$DRY_RUN" ] && { ...; exit 0; }` immediately above it. (b) a shim
    directory is PREPENDED to PATH holding tripwire `sudo`, `shutdown`,
    `poweroff`, `halt`, `reboot` and `systemctl`; any attempt to call one
    appends to a flag file and exits 97, and the existence of that flag file
    FAILS the run. Either guard alone suffices; both are present so that a
    future edit which breaks one is caught by the other.
  * It reads /usr/local/bin/auto-stop.sh (world-readable, mode 755) and never
    writes, chmods or installs anything anywhere outside its own tmpdir. It
    runs no sudo. Installation is Sanaa's, not this lab's.

AUTO_STOP_DRY_RUN=1 IS THE PATCH'S ONLY INTERFACE ADDITION, stated plainly: the
installed script honours `DRY_RUN` only; the patched copy accepts both. Both
controls export both spellings so the same harness drives either script.

USAGE
    python3 scripts/test_auto_stop_liveness.py
    python3 scripts/test_auto_stop_liveness.py --script <path>
    python3 scripts/test_auto_stop_liveness.py --selftest

EXIT CODES, AND WHY 3 EXISTS (added 2026-09-03, cfd lane; see the amendment note
on adjudicate() below)
    0  every control behaved as pre-registered, AND every pair was evaluated in
       BOTH directions and flipped. Only this code licenses the both-directions
       claim, and only this code prints it.
    1  REFUSED -- a control landed off its pre-registered verdict, or a pair that
       WAS evaluated did not flip.
    2  the script under test is not there.
    3  NOT WITNESSED -- nothing went wrong, and nothing was proven either: at
       least one pair had a half SKIPPED, so the reader was never shown able to
       see both a presence and an absence. This is the code the suite returned
       zero for until 2026-09-03.
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
from pathlib import Path

PATCHED = Path("/home/ubuntu/Certonomous/scripts/auto_stop_patched.sh")
INSTALLED = Path("/usr/local/bin/auto-stop.sh")

# The planted argv signature. It is the launcher's OWN emitted string --
# scripts/queue_runner.py:509 builds `STATUS.queue.<case_id>` and :529-533
# writes it from inside the wrapper -- so the plant is the real shape and not a
# shape invented to be findable.
PLANT_SIG = "STATUS.queue.PLANTED_CONTROL_1234"

# A session id that must not exist. Verified absent at run time (see
# dead_sid()); not merely assumed, because "surely nothing has that pid" is the
# kind of assumption this lab exists to refuse.
DEAD_SID_CANDIDATE = 4194301

TRIPWIRES = ("sudo", "shutdown", "poweroff", "halt", "reboot", "systemctl")

# Solver basenames clause (1) matches. Copied from the script under test at
# read time rather than duplicated here -- see real_solver_running().
SOLVER_PROBE_NAME = "simpleFoam"


class Refused(Exception):
    """A control did not behave as pre-registered. Never downgraded to a warning."""


class Skipped(Exception):
    """A control could not be run at all. Reported by name, never as a pass."""


# --------------------------------------------------------------------------
# the sandbox
# --------------------------------------------------------------------------

def build_sandbox(tmp: Path) -> dict:
    """A complete stand-in for every path the script reads. Nothing real."""
    runroot = tmp / "runroot"
    (runroot / "CASE1" / "out").mkdir(parents=True)
    repo = tmp / "repo"
    # QUEUE_ROOT defaults to $REPO/verification/queue, so building it here is
    # what keeps the real queue out of reach.
    (repo / "verification" / "queue" / "cfd" / "launched").mkdir(parents=True)
    sessions = tmp / "sessions" / "projects" / "-home-ubuntu-Certonomous"
    sessions.mkdir(parents=True)   # exists but holds no *.jsonl, so clause (3)
                                   # evaluates false rather than reporting BLIND
    marker = tmp / "marker"
    marker.touch()
    tripdir = tmp / "tripwire_bin"
    tripdir.mkdir()
    flag = tmp / "TRIPWIRE_FIRED"
    for name in TRIPWIRES:
        p = tripdir / name
        p.write_text("#!/bin/sh\n" f'echo "{name} $*" >> "{flag}"\n' "exit 97\n")
        p.chmod(0o755)
    return {"tmp": tmp, "runroot": runroot, "repo": repo, "sessions": sessions,
            "marker": marker, "tripdir": tripdir, "flag": flag,
            "queue": repo / "verification" / "queue"}


def age_marker(marker: Path, minutes: int) -> None:
    """Backdate the marker so `idle` has ALREADY passed the threshold.

    This is what forces the script to make the decision under test. With a
    fresh marker every control would report `under threshold` and the suite
    would be measuring the clock, not the clauses.
    """
    t = time.time() - minutes * 60
    os.utime(marker, (t, t))


def run_script(script: Path, sb: dict, *, idle_minutes: int, fresh_minutes: int,
               docker: str, extra_env: dict | None = None,
               timeout: int = 120) -> tuple[int, str]:
    env = dict(os.environ)
    env.update({
        "AUTO_STOP_DRY_RUN": "1",
        "DRY_RUN": "1",                      # the installed script knows only this
        "IDLE_MINUTES": str(idle_minutes),
        "RUN_FRESH_MINUTES": str(fresh_minutes),
        "MARKER": str(sb["marker"]),
        "REPO": str(sb["repo"]),
        "RUNROOTS": str(sb["runroot"]),
        "SESSIONS": str(sb["sessions"]),
        "DOCKER": docker,
        "PATH": f"{sb['tripdir']}:{env.get('PATH', '')}",
    })
    if extra_env:
        env.update(extra_env)
    proc = subprocess.run(["bash", str(script)], env=env, timeout=timeout,
                          capture_output=True, text=True)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def verdict(out: str) -> str:
    """Reduce the script's own words to one of three states.

    It reads the script's OUTPUT, not its exit code: `keep` and the dry-run
    shutdown path both exit 0, so an exit code cannot tell them apart. This is
    the reader; the ALIVE/IDLE halves are what show it can see both.
    """
    alive = "ALIVE:" in out
    stopping = "would run 'sudo shutdown -h now'" in out or ", shutting down" in out
    if alive and not stopping:
        return "ALIVE"
    if stopping and not alive:
        return "IDLE"
    return f"AMBIGUOUS(alive={alive},stopping={stopping})"


def check_tripwire(sb: dict, label: str) -> None:
    if sb["flag"].exists():
        raise Refused(
            f"{label}: TRIPWIRE FIRED -- the script invoked a power command. "
            f"Contents: {sb['flag'].read_text().strip()!r}")


# --------------------------------------------------------------------------
# contamination prechecks -- what this suite cannot control
# --------------------------------------------------------------------------

def solver_list(script: Path) -> list[str]:
    for line in script.read_text().splitlines():
        if line.startswith("SOLVERS="):
            return line.split("'")[1].split()
    return []


def real_solver_running(script: Path) -> str | None:
    """Clause (1) scans the REAL /proc and is the one clause this suite cannot
    sandbox. A genuine solver running on the box would hold every IDLE-half
    control ALIVE, and reporting that as a patch failure would be a lie about
    the instrument. So it is detected and the affected controls are SKIPPED BY
    NAME, which is a different claim from a pass.
    """
    names = set(solver_list(script))
    if not names:
        return None
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            exe = os.readlink(f"/proc/{pid}/exe")
        except OSError:
            continue
        if os.path.basename(exe) in names:
            return f"pid {pid} is {os.path.basename(exe)}"
    return None


def dead_sid() -> int:
    """A session id verified ABSENT right now, not assumed absent."""
    out = subprocess.run(["ps", "-eo", "sid="], capture_output=True, text=True).stdout
    live = {int(x) for x in out.split() if x.isdigit()}
    cand = DEAD_SID_CANDIDATE
    while cand in live:
        cand -= 1
    return cand


# --------------------------------------------------------------------------
# the plants
# --------------------------------------------------------------------------

def plant_write(sb: dict) -> Path:
    """Clause (6): a file written NOW under the injected run root."""
    f = sb["runroot"] / "CASE1" / "out" / "sweep.log"
    f.write_text("planted control write\n")
    return f


def plant_stale(sb: dict, minutes: int) -> Path:
    """The idle half: the run root holds a file, but an OLD one.

    Not an EMPTY run root, deliberately. An empty tree and a stale tree are
    different facts, and only the stale one proves the freshness COMPARISON is
    doing work rather than the tree merely being absent.
    """
    f = sb["runroot"] / "CASE1" / "out" / "sweep.log"
    f.write_text("stale control write\n")
    t = time.time() - minutes * 60
    os.utime(f, (t, t))
    return f


def spawn_driver(sb: dict, cwd: Path) -> subprocess.Popen:
    """Clause (5a): the measured queue-driver shape.

    comm == `bash`, a kernel-resolved cwd, and the launcher's own
    `STATUS.queue.` signature in argv. It SLEEPS rather than burning CPU
    because a real chain driver does -- it blocks waiting on its solver child.
    A CPU-based control here would pass for the wrong reason.
    """
    inner = (f"cd '{cwd}' && sleep 60 > /dev/null 2>&1; R=$?; "
             f"echo \"launcher_rc=$R\" > '{cwd}/{PLANT_SIG}'")
    return subprocess.Popen(["bash", "-c", inner], cwd=str(cwd),
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def plant_queue_record(sb: dict, *, sid: int, stamped: bool) -> Path:
    """Clause (5b): a launched/ record in the daemon's own shape.

    Field names and semantics are the daemon's, not this test's:
    queue_runner.py:551 writes `_launch` with `sid`; :645-654 stamps
    `status_seen_utc` once the case's STATUS file is observed.
    """
    launch = {"utc": "2026-09-03T00:00:00Z", "pid": sid, "sid": sid,
              "status_file": str(sb["runroot"] / "STATUS.queue.PLANTED"),
              "wrapper_out": str(sb["runroot"] / "launcher.queue.out"),
              "started_epoch": time.time() - 3600}
    if stamped:
        launch["status_seen_utc"] = "2026-09-03T00:05:00Z"
    rec = sb["queue"] / "cfd" / "launched" / "PLANTED_CASE.json"
    rec.write_text(json.dumps({"case_id": "PLANTED_CASE", "team": "cfd",
                               "_launch": launch}, indent=1))
    return rec


def spawn_session_leader() -> subprocess.Popen:
    """A live session whose sid == its pid, for the clause (5b) ALIVE half."""
    return subprocess.Popen(["sleep", "60"], start_new_session=True,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def spawn_burner(cwd: Path | None = None, argv0: str | None = None) -> subprocess.Popen:
    """A process that really does move CPU ticks."""
    cmd = [argv0 or "bash", "-c",
           "end=$((SECONDS+60)); while [ $SECONDS -lt $end ]; do :; done"]
    return subprocess.Popen(cmd, cwd=str(cwd) if cwd else None,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def spawn_py(cwd: Path, busy: bool) -> subprocess.Popen:
    """Clause (2)'s subject: comm `python3`, cwd inside the injected REPO."""
    code = ("import time\nt=time.time()+60\nwhile time.time()<t: pass\n" if busy
            else "import time\ntime.sleep(60)\n")
    return subprocess.Popen(["python3", "-c", code], cwd=str(cwd),
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def spawn_named_binary(tmp: Path, name: str) -> subprocess.Popen:
    """Clause (1)'s subject: a real binary whose BASENAME is a solver name.

    A copy of /bin/sleep renamed, because clause (1) matches
    basename(readlink /proc/PID/exe) -- a kernel fact, so only a real file with
    that name can plant it. This is also the negative control's mechanism: the
    identical binary under a non-solver name must NOT hold the box.
    """
    p = tmp / name
    shutil.copy2("/bin/sleep", p)
    p.chmod(0o755)
    return subprocess.Popen([str(p), "60"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def docker_stub(tmp: Path, tag: str, *, pid: int | None = None,
                ps_rc: int = 0, ps_stderr: str = "", top_empty: bool = False) -> str:
    """A `docker` that reports what the control needs it to report.

    A STUB AND NOT A REAL CONTAINER, on purpose: this suite must run on a box
    with no docker daemon and must be able to plant states a real daemon will
    not produce on demand (socket permission denied, `top` unreadable).
    `docker top -o pid` was measured against a LIVE probe container on this box
    on 2026-09-03 -- it printed "PID\\n27788\\n", host-namespace, unpadded --
    and the stub reproduces that interface. What is under test here is the
    script's DECISION on those pids, not docker's own behaviour.
    """
    p = tmp / f"docker_stub_{tag}"
    if ps_rc != 0:
        body = ("#!/bin/sh\n"
                'case "$1" in\n'
                f'  ps) echo "{ps_stderr}" >&2; exit {ps_rc} ;;\n'
                f'  *) exit {ps_rc} ;;\n'
                "esac\n")
    elif pid is None:
        body = '#!/bin/sh\ncase "$1" in\n  ps) exit 0 ;;\n  *) exit 0 ;;\nesac\n'
    elif top_empty:
        body = ("#!/bin/sh\n"
                'case "$1" in\n'
                "  ps) echo planted_container_cid ;;\n"
                "  top) exit 0 ;;\n"
                "  *) exit 0 ;;\n"
                "esac\n")
    else:
        body = ("#!/bin/sh\n"
                'case "$1" in\n'
                "  ps) echo planted_container_cid ;;\n"
                f"  top) echo PID; echo {pid} ;;\n"
                "  *) exit 0 ;;\n"
                "esac\n")
    p.write_text(body)
    p.chmod(0o755)
    return str(p)


# --------------------------------------------------------------------------
# the runner
# --------------------------------------------------------------------------

def control(name: str, expect: str, fn) -> dict:
    tmp = Path(tempfile.mkdtemp(prefix="autostop_control_"))
    procs: list[subprocess.Popen] = []
    try:
        sb = build_sandbox(tmp)
        try:
            rc, out, extra = fn(tmp, sb, procs)
        except Skipped as e:
            return {"name": name, "expect": expect, "got": "SKIP", "ok": None,
                    "rc": None, "note": str(e), "line": ""}
        check_tripwire(sb, name)
        got = verdict(out)
        return {"name": name, "expect": expect, "got": got, "ok": (got == expect),
                "rc": rc, "note": extra,
                "line": next((l for l in out.splitlines()
                              if "ALIVE:" in l or "shutting down" in l
                              or "would run" in l), "")}
    finally:
        for p in procs:
            try:
                p.kill(); p.wait(timeout=5)
            except Exception:
                pass
        for d in tmp.rglob("*"):
            try:
                if d.is_dir():
                    d.chmod(0o755)
            except Exception:
                pass
        shutil.rmtree(tmp, ignore_errors=True)


def adjudicate(results: list[dict], pairs: list[tuple]) -> tuple[int, list[str]]:
    """Turn control outcomes into ONE verdict. Pure: no I/O, no clock, no /proc.

    WHY THIS IS A FUNCTION AND NOT INLINE IN main() (2026-09-03, cfd lane)
    ---------------------------------------------------------------------
    THE DEFECT IT REPAIRS, measured on this box on 2026-09-03 and filed at
    verification/runs/AUTOSTOP_LIVENESS/suite_host_2026-09-03T1815Z.txt:

        controls: 12 passed, 0 failed, 12 skipped
        every one of the TEN flip pairs printed [SKIP], Z1 included
        SUITE EXIT CODE: 0
        and the run still printed, unconditionally:
          "every evaluated pair flipped. The reader was shown able to see both
           a non-zero and a zero."

    THAT SENTENCE WAS FALSE FOR THAT RUN. Not one pair had been evaluated. The
    box had three teams' OpenFOAM solvers live, clause (1) reads the real /proc
    and cannot be sandboxed, so every IDLE-half control SKIPPED -- correctly --
    and the suite absorbed all twelve skips into neither the pass column nor the
    fail column and exited 0.

    A skip is honest. Counting it as a pass is not, and printing the
    both-directions claim over a run that evaluated no direction is the exact
    disease this suite exists to catch: a green badge on a test that tested
    nothing. It is the same shape as a reader that reports a zero it was never
    shown able to see a non-zero with -- which is CLAUDE.md rule 3, turned on
    the harness itself.

    THE REPAIR, and it is three lines of doctrine rather than three lines of code:
      (a) skips are counted in their OWN column and never fold into either other;
      (b) a pair with an unwitnessed half REFUSES -- rc 3, NOT WITNESSED -- so
          the suite cannot pass by not looking;
      (c) THE CLAIM IS PRINTED FROM THE EVIDENCE, NEVER FROM THE RUN COMPLETING.
          The old sentence was unconditional. That was the whole bug: the run
          finishing was being read as the reading succeeding.

    Pure so it can be driven by --selftest with synthetic rows, in both
    directions, without a box, a solver or a clock. The thing that changed here
    is the ADJUDICATION, so the control has to exercise the adjudication.

    Returns (exit_code, lines_to_print).
    """
    out: list[str] = []
    by_id = {r["name"].split()[0]: r for r in results}

    out.append("")
    out.append("  FLIP CHECK -- a busy control that does not flip the answer is not a control")
    flip_fail: list[str] = []
    unwitnessed: list[str] = []
    for busy, idle, signal in pairs:
        b, i = by_id.get(busy), by_id.get(idle)
        if b is None or i is None:
            missing = busy if b is None else idle
            flip_fail.append(f"{busy}/{idle}")
            out.append(f"    [REFUSED] {busy} vs {idle:4s}  {signal}: control {missing} "
                       f"is named in the flip table and was never run")
            continue
        if b["ok"] is None or i["ok"] is None:
            which = busy if b["ok"] is None else idle
            unwitnessed.append(f"{busy}/{idle}")
            out.append(f"    [NOT WITNESSED] {busy} vs {idle:4s}  {signal}: "
                       f"{which} SKIPPED, so this pair proves nothing in either direction")
            continue
        flipped = (b["got"] != i["got"] and b["got"] == "ALIVE" and i["got"] == "IDLE")
        out.append(f"    [{'ok     ' if flipped else 'REFUSED'}] {busy} vs {idle:4s}  "
                   f"{signal}: {b['got']} vs {i['got']}")
        if not flipped:
            flip_fail.append(f"{busy}/{idle}")

    n_pass = sum(1 for r in results if r["ok"] is True)
    n_fail = sum(1 for r in results if r["ok"] is False)
    n_skip = sum(1 for r in results if r["ok"] is None)
    n_pair_ok = len(pairs) - len(flip_fail) - len(unwitnessed)
    out.append("")
    out.append(f"  controls: {n_pass} passed, {n_fail} failed, {n_skip} skipped")
    out.append(f"  pairs:    {n_pair_ok} witnessed in BOTH directions, "
               f"{len(flip_fail)} refused, {len(unwitnessed)} not witnessed")
    if n_skip:
        for r in results:
            if r["ok"] is None:
                out.append(f"    SKIPPED {r['name'].split()[0]}: {r['note']}")

    if n_fail or flip_fail:
        out.append("")
        out.append(f"REFUSED: {n_fail} control(s) off their pre-registered verdict; "
                   f"{len(flip_fail)} pair(s) did not flip"
                   f"{': ' + ', '.join(flip_fail) if flip_fail else ''}")
        if unwitnessed:
            out.append(f"  and {len(unwitnessed)} pair(s) were NOT WITNESSED at all: "
                       f"{', '.join(unwitnessed)}")
        return 1, out

    if unwitnessed:
        out.append("")
        out.append(f"NOT WITNESSED: no control landed off its verdict, and no pair was "
                   f"proven either. {len(unwitnessed)} pair(s) had a half SKIPPED: "
                   f"{', '.join(unwitnessed)}")
        out.append("  THIS RUN DOES NOT MAKE THE BOTH-DIRECTIONS CLAIM. The reader was not "
                   "shown able to see both a presence and an absence, so per CLAUDE.md rule 3 "
                   "there is no evidence here -- only an absence of contradiction.")
        return 3, out

    out.append("")
    out.append(f"All {n_pass} controls behaved as pre-registered and all {len(pairs)} pairs "
               f"were evaluated in BOTH directions and flipped. The reader was shown able to "
               f"see both a non-zero and a zero.")
    return 0, out


def _row(cid: str, expect: str, got: str) -> dict:
    """A synthetic control outcome for --selftest. `got` of None means SKIP."""
    return {"name": f"{cid}  synthetic", "expect": expect, "got": got or "SKIP",
            "ok": None if got is None else (got == expect), "rc": 0,
            "note": "synthetic row, no script was run", "line": ""}


def selftest() -> int:
    """A planted control on the ADJUDICATOR -- in both directions, like everything else here.

    A fix to a both-directions check that is itself only checked one way would be
    the original defect wearing a repair's clothes. So this drives adjudicate()
    with synthetic rows and refuses unless it answers correctly on EVERY arm:
    a clean run must still PASS (or the repair has broken the suite into always
    refusing, which is just as useless as always passing), and each way of being
    unproven must REFUSE with the right code.
    """
    pairs = [("A1", "A0", "signal under test")]
    cases = [
        ("clean both directions -> 0, and the claim is printed",
         [_row("A1", "ALIVE", "ALIVE"), _row("A0", "IDLE", "IDLE")], 0, True),
        ("IDLE half skipped -> 3 NOT WITNESSED, claim withheld  [THE 2026-09-03 DEFECT]",
         [_row("A1", "ALIVE", "ALIVE"), _row("A0", "IDLE", None)], 3, False),
        ("ALIVE half skipped -> 3 NOT WITNESSED, claim withheld",
         [_row("A1", "ALIVE", None), _row("A0", "IDLE", "IDLE")], 3, False),
        ("both halves skipped -> 3 NOT WITNESSED, claim withheld",
         [_row("A1", "ALIVE", None), _row("A0", "IDLE", None)], 3, False),
        ("a control off its verdict -> 1 REFUSED",
         [_row("A1", "ALIVE", "IDLE"), _row("A0", "IDLE", "IDLE")], 1, False),
        ("pair evaluated but does not flip -> 1 REFUSED",
         [_row("A1", "ALIVE", "ALIVE"), _row("A0", "IDLE", "ALIVE")], 1, False),
        ("a pair naming a control that was never run -> 1 REFUSED",
         [_row("A1", "ALIVE", "ALIVE")], 1, False),
    ]
    claim = "shown able to see both a non-zero and a zero"
    bad = 0
    print("SELFTEST of adjudicate() -- the both-directions check, checked both ways")
    for label, rows, want_rc, want_claim in cases:
        rc, lines = adjudicate(rows, pairs)
        text = "\n".join(lines)
        got_claim = claim in text
        ok = (rc == want_rc) and (got_claim == want_claim)
        print(f"  [{'ok     ' if ok else 'REFUSED'}] {label}")
        print(f"            rc={rc} (want {want_rc}); "
              f"both-directions claim printed={got_claim} (want {want_claim})")
        if not ok:
            bad += 1

    # THE MUTATION CONTROL. A selftest that only shows the fixed code passing
    # cannot tell a working adjudicator from one that returns 0 unconditionally
    # -- which is precisely the bug being repaired. So: re-run the skip arm
    # through the OLD logic, reproduced here, and REFUSE unless the old logic
    # gets it WRONG. If the line below ever prints "ok", the repair is not in
    # the code path the suite actually runs.
    rows = [_row("A1", "ALIVE", "ALIVE"), _row("A0", "IDLE", None)]
    old_flip_fail = [f"{b}/{i}" for b, i, _ in pairs
                     if not (rows[0]["ok"] is None or rows[1]["ok"] is None)
                     and not (rows[0]["got"] == "ALIVE" and rows[1]["got"] == "IDLE")]
    old_rc = 1 if (sum(1 for r in rows if r["ok"] is False) or old_flip_fail) else 0
    mutation_ok = (old_rc == 0)
    print(f"  [{'ok     ' if mutation_ok else 'REFUSED'}] MUTATION CONTROL: the pre-repair "
          f"logic returns {old_rc} on the skip arm")
    print(f"            it must return 0 -- that IS the defect. If it refuses here, this "
          f"selftest is not exercising the thing that was broken.")
    if not mutation_ok:
        bad += 1

    if bad:
        print(f"\nREFUSED: {bad} selftest arm(s) wrong")
        return 1
    print(f"\nAll {len(cases)} arms and the mutation control behaved as pre-registered.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true",
                    help="drive adjudicate() with synthetic rows; runs no script")
    ap.add_argument("--script", default=str(PATCHED))
    ap.add_argument("--idle-minutes", type=int, default=30)
    ap.add_argument("--fresh-minutes", type=int, default=30)
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    script = Path(args.script)
    if not script.is_file():
        print(f"REFUSED: no script at {script}", file=sys.stderr)
        return 2

    IM, FM = args.idle_minutes, args.fresh_minutes
    AGE = IM + 5          # every control is a live decision, not a clock reading
    STALE = FM + 20
    contamination = real_solver_running(script)
    DEAD = dead_sid()

    def needs_quiet_box():
        if contamination:
            raise Skipped(f"a real solver is running on this box ({contamination}); "
                          f"clause (1) reads the real /proc and cannot be sandboxed, "
                          f"so an IDLE-half control here would be measuring the box, "
                          f"not the patch")

    # ---- clause (6) -----------------------------------------------------
    def A1(tmp, sb, procs):
        age_marker(sb["marker"], AGE); f = plant_write(sb)
        rc, out = run_script(script, sb, idle_minutes=IM, fresh_minutes=FM,
                             docker=docker_stub(tmp, "empty"))
        return rc, out, f"fresh write {f.name} at t-0 under injected RUNROOTS"

    def A0(tmp, sb, procs):
        needs_quiet_box()
        age_marker(sb["marker"], AGE); f = plant_stale(sb, STALE)
        rc, out = run_script(script, sb, idle_minutes=IM, fresh_minutes=FM,
                             docker=docker_stub(tmp, "empty"))
        return rc, out, f"run root holds only {f.name}, aged {STALE}min"

    def A2(tmp, sb, procs):
        if os.geteuid() == 0:
            raise Skipped("running as root: a mode-000 directory does not produce "
                          "the EACCES this control plants")
        age_marker(sb["marker"], AGE); plant_stale(sb, STALE)
        locked = sb["runroot"] / "locked"
        locked.mkdir(); (locked / "x").write_text("x"); locked.chmod(0o000)
        rc, out = run_script(script, sb, idle_minutes=IM, fresh_minutes=FM,
                             docker=docker_stub(tmp, "empty"))
        locked.chmod(0o755)
        return rc, out, "unreadable dir in run root -> find errors -> backstop BLIND"

    # ---- clause (5a) ----------------------------------------------------
    def B1(tmp, sb, procs):
        age_marker(sb["marker"], AGE); plant_stale(sb, STALE)
        procs.append(spawn_driver(sb, sb["runroot"] / "CASE1")); time.sleep(1.5)
        rc, out = run_script(script, sb, idle_minutes=IM, fresh_minutes=FM,
                             docker=docker_stub(tmp, "empty"))
        return rc, out, "driver-shaped bash, cwd IN run root, stale tree"

    def B0(tmp, sb, procs):
        needs_quiet_box()
        age_marker(sb["marker"], AGE); plant_stale(sb, STALE)
        outside = tmp / "outside"; outside.mkdir()
        procs.append(spawn_driver(sb, outside)); time.sleep(1.5)
        rc, out = run_script(script, sb, idle_minutes=IM, fresh_minutes=FM,
                             docker=docker_stub(tmp, "empty"))
        return rc, out, "IDENTICAL driver argv, cwd OUTSIDE repo and run roots"

    # ---- clause (5b) ----------------------------------------------------
    def C1(tmp, sb, procs):
        age_marker(sb["marker"], AGE); plant_stale(sb, STALE)
        leader = spawn_session_leader(); procs.append(leader); time.sleep(0.5)
        plant_queue_record(sb, sid=leader.pid, stamped=False)
        rc, out = run_script(script, sb, idle_minutes=IM, fresh_minutes=FM,
                             docker=docker_stub(tmp, "empty"))
        return rc, out, f"unstamped launched record, sid {leader.pid} LIVE"

    def C0(tmp, sb, procs):
        needs_quiet_box()
        age_marker(sb["marker"], AGE); plant_stale(sb, STALE)
        plant_queue_record(sb, sid=DEAD, stamped=False)
        rc, out = run_script(script, sb, idle_minutes=IM, fresh_minutes=FM,
                             docker=docker_stub(tmp, "empty"))
        return rc, out, (f"unstamped launched record, sid {DEAD} DEAD -- the five "
                         f"real stale rows on this box, incl. A1WR_chain.json")

    def C0b(tmp, sb, procs):
        needs_quiet_box()
        age_marker(sb["marker"], AGE); plant_stale(sb, STALE)
        leader = spawn_session_leader(); procs.append(leader); time.sleep(0.5)
        plant_queue_record(sb, sid=leader.pid, stamped=True)
        rc, out = run_script(script, sb, idle_minutes=IM, fresh_minutes=FM,
                             docker=docker_stub(tmp, "empty"))
        return rc, out, f"STAMPED record (daemon saw completion), sid {leader.pid} live"

    # ---- clause (4) -----------------------------------------------------
    def D1(tmp, sb, procs):
        age_marker(sb["marker"], AGE); plant_stale(sb, STALE)
        b = spawn_burner(); procs.append(b); time.sleep(1.0)
        rc, out = run_script(script, sb, idle_minutes=IM, fresh_minutes=FM,
                             docker=docker_stub(tmp, "busy", pid=b.pid))
        return rc, out, f"container stub reports CPU-burning host pid {b.pid}"

    def D0(tmp, sb, procs):
        needs_quiet_box()
        age_marker(sb["marker"], AGE); plant_stale(sb, STALE)
        s = subprocess.Popen(["sleep", "60"], stdout=subprocess.DEVNULL)
        procs.append(s); time.sleep(1.0)
        rc, out = run_script(script, sb, idle_minutes=IM, fresh_minutes=FM,
                             docker=docker_stub(tmp, "idle", pid=s.pid))
        return rc, out, f"container stub reports IDLE host pid {s.pid}"

    def D2(tmp, sb, procs):
        age_marker(sb["marker"], AGE); plant_stale(sb, STALE)
        rc, out = run_script(script, sb, idle_minutes=IM, fresh_minutes=FM,
                             docker=docker_stub(tmp, "daemondown", ps_rc=1,
                                                ps_stderr="Cannot connect to the Docker daemon"))
        return rc, out, "docker installed, daemon DOWN (ps rc=1) -> INDETERMINATE"

    def D3(tmp, sb, procs):
        age_marker(sb["marker"], AGE); plant_stale(sb, STALE)
        rc, out = run_script(script, sb, idle_minutes=IM, fresh_minutes=FM,
                             docker=docker_stub(tmp, "perm", ps_rc=1,
                                                ps_stderr="permission denied while trying to connect"))
        return rc, out, "docker installed, PERMISSION DENIED -> INDETERMINATE"

    def D3b(tmp, sb, procs):
        needs_quiet_box()
        age_marker(sb["marker"], AGE); plant_stale(sb, STALE)
        rc, out = run_script(script, sb, idle_minutes=IM, fresh_minutes=FM,
                             docker=docker_stub(tmp, "perm2", ps_rc=1,
                                                ps_stderr="permission denied"),
                             extra_env={"DOCKER_BLIND_ALIVE": "0"})
        return rc, out, "SAME blind docker, DOCKER_BLIND_ALIVE=0 -> the switch works"

    def D4(tmp, sb, procs):
        age_marker(sb["marker"], AGE); plant_stale(sb, STALE)
        rc, out = run_script(script, sb, idle_minutes=IM, fresh_minutes=FM,
                             docker=docker_stub(tmp, "topless", pid=1, top_empty=True))
        return rc, out, "container UP but 'docker top' unreadable -> cannot judge"

    def D5(tmp, sb, procs):
        needs_quiet_box()
        age_marker(sb["marker"], AGE); plant_stale(sb, STALE)
        rc, out = run_script(script, sb, idle_minutes=IM, fresh_minutes=FM,
                             docker=str(tmp / "no_such_docker_binary"))
        return rc, out, "NO docker executable -> determinate, not indeterminate"

    # ---- preserved originals: clauses (0), (1), (2), (3) ----------------
    def E1(tmp, sb, procs):
        age_marker(sb["marker"], AGE); plant_stale(sb, STALE)
        (sb["repo"] / ".autostop-hold").touch()
        rc, out = run_script(script, sb, idle_minutes=IM, fresh_minutes=FM,
                             docker=docker_stub(tmp, "empty"))
        return rc, out, "clause (0) hold file, fresh"

    def E0(tmp, sb, procs):
        needs_quiet_box()
        age_marker(sb["marker"], AGE); plant_stale(sb, STALE)
        h = sb["repo"] / ".autostop-hold"; h.touch()
        t = time.time() - 25 * 3600
        os.utime(h, (t, t))
        rc, out = run_script(script, sb, idle_minutes=IM, fresh_minutes=FM,
                             docker=docker_stub(tmp, "empty"))
        return rc, out, "clause (0) hold file aged 25h -> EXPIRED, must not pin"

    def F1(tmp, sb, procs):
        age_marker(sb["marker"], AGE); plant_stale(sb, STALE)
        procs.append(spawn_named_binary(tmp, SOLVER_PROBE_NAME)); time.sleep(0.7)
        rc, out = run_script(script, sb, idle_minutes=IM, fresh_minutes=FM,
                             docker=docker_stub(tmp, "empty"))
        return rc, out, f"clause (1) real binary named {SOLVER_PROBE_NAME}"

    def F0(tmp, sb, procs):
        needs_quiet_box()
        age_marker(sb["marker"], AGE); plant_stale(sb, STALE)
        procs.append(spawn_named_binary(tmp, "notASolverAtAll")); time.sleep(0.7)
        rc, out = run_script(script, sb, idle_minutes=IM, fresh_minutes=FM,
                             docker=docker_stub(tmp, "empty"))
        return rc, out, "clause (1) IDENTICAL binary, non-solver basename"

    def G1(tmp, sb, procs):
        age_marker(sb["marker"], AGE); plant_stale(sb, STALE)
        procs.append(spawn_py(sb["repo"], busy=True)); time.sleep(1.0)
        rc, out = run_script(script, sb, idle_minutes=IM, fresh_minutes=FM,
                             docker=docker_stub(tmp, "empty"))
        return rc, out, "clause (2) python3 burning CPU with cwd in REPO"

    def G0(tmp, sb, procs):
        needs_quiet_box()
        age_marker(sb["marker"], AGE); plant_stale(sb, STALE)
        procs.append(spawn_py(sb["repo"], busy=False)); time.sleep(1.0)
        rc, out = run_script(script, sb, idle_minutes=IM, fresh_minutes=FM,
                             docker=docker_stub(tmp, "empty"))
        return rc, out, "clause (2) python3 in REPO but PARKED -> must not pin"

    def H1(tmp, sb, procs):
        age_marker(sb["marker"], AGE); plant_stale(sb, STALE)
        (sb["sessions"] / "live.jsonl").write_text("{}\n")
        rc, out = run_script(script, sb, idle_minutes=IM, fresh_minutes=FM,
                             docker=docker_stub(tmp, "empty"))
        return rc, out, "clause (3) transcript written at t-0"

    def H0(tmp, sb, procs):
        needs_quiet_box()
        age_marker(sb["marker"], AGE); plant_stale(sb, STALE)
        j = sb["sessions"] / "live.jsonl"; j.write_text("{}\n")
        t = time.time() - (IM + 20) * 60
        os.utime(j, (t, t))
        rc, out = run_script(script, sb, idle_minutes=IM, fresh_minutes=FM,
                             docker=docker_stub(tmp, "empty"))
        return rc, out, f"clause (3) transcript aged {IM + 20}min"

    # ---- discrimination -------------------------------------------------
    def Z1(tmp, sb, procs):
        needs_quiet_box()
        if not INSTALLED.is_file():
            raise Skipped(f"{INSTALLED} not present, nothing to discriminate against")
        age_marker(sb["marker"], AGE); plant_write(sb)
        rc, out = run_script(INSTALLED, sb, idle_minutes=IM, fresh_minutes=FM,
                             docker=docker_stub(tmp, "empty"))
        return rc, out, "control A1's EXACT plant, run through the INSTALLED script"

    controls = [
        ("A1  clause(6) run tree written now        ", "ALIVE", A1),
        ("A0  clause(6) run tree stale              ", "IDLE",  A0),
        ("A2  clause(6) scan cannot read the tree   ", "ALIVE", A2),
        ("B1  clause(5a) chain driver, cwd in root  ", "ALIVE", B1),
        ("B0  clause(5a) same driver, cwd outside   ", "IDLE",  B0),
        ("C1  clause(5b) unstamped record, sid live ", "ALIVE", C1),
        ("C0  clause(5b) unstamped record, sid dead ", "IDLE",  C0),
        ("C0b clause(5b) stamped record, sid live   ", "IDLE",  C0b),
        ("D1  clause(4) container burning CPU       ", "ALIVE", D1),
        ("D0  clause(4) container present but idle  ", "IDLE",  D0),
        ("D2  clause(4) docker daemon down          ", "ALIVE", D2),
        ("D3  clause(4) docker permission denied    ", "ALIVE", D3),
        ("D3b clause(4) same, DOCKER_BLIND_ALIVE=0  ", "IDLE",  D3b),
        ("D4  clause(4) 'docker top' unreadable     ", "ALIVE", D4),
        ("D5  clause(4) no docker executable at all ", "IDLE",  D5),
        ("E1  clause(0) hold file fresh    [ORIG]   ", "ALIVE", E1),
        ("E0  clause(0) hold file expired  [ORIG]   ", "IDLE",  E0),
        ("F1  clause(1) solver by exe name [ORIG]   ", "ALIVE", F1),
        ("F0  clause(1) same binary, other name     ", "IDLE",  F0),
        ("G1  clause(2) repo worker busy   [ORIG]   ", "ALIVE", G1),
        ("G0  clause(2) repo worker parked          ", "IDLE",  G0),
        ("H1  clause(3) transcript fresh   [ORIG]   ", "ALIVE", H1),
        ("H0  clause(3) transcript stale            ", "IDLE",  H0),
        ("Z1  INSTALLED script, A1's plant [DISCRIM]", "IDLE",  Z1),
    ]

    # THE FLIP TABLE. Declared here, in data, so it cannot be adjusted after
    # seeing an answer. Each entry names the BUSY control, its IDLE partner and
    # the single signal the pair isolates. A pair whose two halves AGREE is
    # REFUSED even if both individually met expectation.
    pairs = [
        ("A1", "A0",  "clause (6) run-tree freshness"),
        ("B1", "B0",  "clause (5a) driver cwd test"),
        ("C1", "C0",  "clause (5b) session liveness"),
        ("C1", "C0b", "clause (5b) daemon's status_seen_utc stamp"),
        ("D1", "D0",  "clause (4) container CPU test"),
        ("D2", "D3b", "clause (4) INDETERMINATE-therefore-ALIVE"),
        ("F1", "F0",  "clause (1) solver basename match"),
        ("G1", "G0",  "clause (2) repo worker CPU test"),
        ("H1", "H0",  "clause (3) transcript freshness"),
        ("A1", "Z1",  "the patch sees what the INSTALLED script does not"),
    ]

    print(f"planted-control test of {script}")
    print(f"  IDLE_MINUTES={IM}  RUN_FRESH_MINUTES={FM}  marker backdated {AGE}min")
    print(f"  every path injected under tempfile.mkdtemp(); "
          f"/home/ubuntu/certonomous-runs and the real verification/queue are NEVER read")
    print(f"  power commands {TRIPWIRES} shimmed to tripwires on PATH; "
          f"AUTO_STOP_DRY_RUN=1 exported")
    if contamination:
        print(f"  CONTAMINATION: {contamination} -- IDLE-half controls will SKIP")
    print()

    results = [control(n, e, f) for n, e, f in controls]

    for r in results:
        tag = "SKIP   " if r["ok"] is None else ("ok     " if r["ok"] else "REFUSED")
        print(f"  [{tag}] {r['name']}  expected {r['expect']:5s} got {r['got']}")
        print(f"            plant: {r['note']}")
        if r["line"]:
            print(f"            script said: {r['line'].strip()}")

    rc, lines = adjudicate(results, pairs)
    for line in lines:
        print(line)
    return rc


if __name__ == "__main__":
    sys.exit(main())
