#!/usr/bin/env python3
# =====================================================================
# D6RF4 P_conv WATCHER.
#
# WHAT THIS FILE IS.  A read-only observer for the D6RF4 `P_conv` arm.  It
# LAUNCHES NOTHING, STAGES NOTHING, GRADES NOTHING and WRITES NOTHING outside
# its own output file.  It does not re-fire an aborted arm; a re-fire is the
# supervisor's act and this file has no code path that could take it.
#
# WHY IT IS NOT A GRADER.  The verdict comes from the frozen grading path
# `d6rf4_grade.py`.  This watcher reports OBSERVATIONS so a supervisor learns
# the arm's state without sitting on it.  Where it reports the accept floor it
# does so by CALLING THE FROZEN INSTRUMENT `d6rf4_accept_floor_control.py`
# rather than by re-implementing its reader -- a second reader would be a
# second answer, and the registered one is the instrument's.
#
# THE ABSENT-ROOT DISTINCTION, WHICH IS THIS FILE'S MAIN POINT.
# A missing run root means two completely different things and the difference
# is the whole diagnostic value of the watch:
#
#   ROOT_ABSENT_AWAITING_DAEMON  -- the row is placed, the launcher has not yet
#       run, the root does not exist YET.  EXPECTED.  Not a fault.
#   ROOT_ABSENT_LAUNCHER_ABORTED -- the launcher RAN and exited non-zero, and
#       the root's absence is EXPLAINED BY THAT EXIT.  A finding.
#   ROOT_ABSENT_UNEXPLAINED      -- the launcher recorded a rc=0 completion and
#       the root still is not there.  A finding of a different shape.
#
# A watcher that printed a bare `ABSENT` for all three would make a sustained
# expected state look identical to a crash.  The state token is therefore
# always resolved against the launcher's own status artefact, never from the
# filesystem alone.
#
# PLANTED CONTROL, `CLAUDE.md` rule 3.  Every reader below is driven in BOTH
# directions by `--selftest` before the watcher is armed: shown able to see a
# known non-zero it was not told, and shown to REFUSE / report a distinct
# absent-token rather than a zero when its source is missing or empty.  A zero
# from a reader not shown able to see a non-zero is not evidence.
# =====================================================================
import argparse
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTERED_BASE = "/home/ubuntu/certonomous-runs/CURRICULUM-D6RF4-a2-wing-convergence-probe"
ARM = "P_conv"
ACCEPT_FLOOR_CONTROL = os.path.join(HERE, "d6rf4_accept_floor_control.py")
STATUS_QUEUE = os.path.join(HERE, "STATUS.queue.D6RF4-%s" % ARM)
LAUNCHER_OUT = os.path.join(HERE, "launcher.queue.out")

# The registered accept floor.  Carried for REPORTING only; this file never
# gates on it and never writes it anywhere the grader reads.
REG_TOL, REG_DIFF, REG_FLOOR = "1e-08", "1000", 1.0e-05

TIME_RE = re.compile(r"^Time = (\d+(?:\.\d+)?)\s*$")
RES_RE2 = re.compile(
    r"^(\w+) initRes: ([0-9eE+\-.]+) finalRes: ([0-9eE+\-.]+) nIters: (\d+)\s*$")
EXEC_RE = re.compile(r"^ExecutionTime = ([0-9.]+) s\s+ClockTime = ([0-9.]+) s\s*$")
CDCL_RE = re.compile(r"^(CD|CL): ([0-9eE+\-.]+) final: ([0-9eE+\-.]+)\s*$")

# The six fields G-CONV gates, in the registered order.
GCONV_FIELDS = ["U0", "U1", "U2", "he", "p", "nuTilda"]


# ---------------------------------------------------------------------
# READERS.  Each returns a token, never a bare zero.
# ---------------------------------------------------------------------
def read_time_blocks(logpath):
    """Return (state, blocks).  `blocks` is a list of dicts, one per `Time =`.

    STATES, and none of them is a silent zero:
      SOURCE_ABSENT   -- the file is not there
      SOURCE_EMPTY    -- the file is there and holds no bytes
      NO_TIME_BLOCKS  -- the file has content but no `Time = ` line
      READ            -- at least one block, returned
    """
    if not os.path.exists(logpath):
        return "SOURCE_ABSENT", []
    try:
        if os.path.getsize(logpath) == 0:
            return "SOURCE_EMPTY", []
        with open(logpath, "r", errors="replace") as fh:
            lines = fh.read().splitlines()
    except OSError as e:
        return "SOURCE_UNREADABLE:%s" % e, []

    blocks, cur = [], None
    for ln in lines:
        m = TIME_RE.match(ln)
        if m:
            if cur is not None:
                blocks.append(cur)
            cur = {"Time": m.group(1), "res": {}, "CD": None, "CL": None,
                   "ExecutionTime": None}
            continue
        if cur is None:
            continue
        m = RES_RE2.match(ln)
        if m:
            cur["res"][m.group(1)] = {"initRes": m.group(2),
                                      "finalRes": m.group(3),
                                      "nIters": m.group(4)}
            continue
        m = CDCL_RE.match(ln)
        if m:
            cur[m.group(1)] = m.group(2)
            continue
        m = EXEC_RE.match(ln)
        if m:
            cur["ExecutionTime"] = m.group(1)
    if cur is not None:
        blocks.append(cur)
    if not blocks:
        return "NO_TIME_BLOCKS", []
    return "READ", blocks


def read_launcher_state():
    """Resolve WHY the root is in the state it is in, from the launcher's own
    artefacts.  Never guesses; an unreadable status is said to be unreadable."""
    st = {"status_file": STATUS_QUEUE, "status": None, "launcher_rc": None,
          "end": None, "tail": None}
    if os.path.exists(STATUS_QUEUE):
        try:
            txt = open(STATUS_QUEUE).read().strip()
            st["status"] = txt
            m = re.search(r"launcher_rc=(-?\d+)", txt)
            if m:
                st["launcher_rc"] = int(m.group(1))
            m = re.search(r"end=(\S+)", txt)
            if m:
                st["end"] = m.group(1)
        except OSError as e:
            st["status"] = "UNREADABLE:%s" % e
    if os.path.exists(LAUNCHER_OUT):
        try:
            ls = [l.rstrip() for l in open(LAUNCHER_OUT, errors="replace")
                  if l.strip()]
            st["tail"] = ls[-4:]
        except OSError as e:
            st["tail"] = ["UNREADABLE:%s" % e]
    return st


def resolve_root_state(base, launcher):
    """THE THREE-WAY ABSENT DISTINCTION.  See this file's header."""
    if os.path.isdir(base):
        try:
            mode = oct(os.stat(base).st_mode & 0o777)[2:]
        except OSError as e:
            return "ROOT_PRESENT_UNSTATABLE:%s" % e, None
        return "ROOT_PRESENT", mode
    rc = launcher.get("launcher_rc")
    if rc is None:
        return "ROOT_ABSENT_AWAITING_DAEMON", None
    if rc != 0:
        return "ROOT_ABSENT_LAUNCHER_ABORTED", None
    return "ROOT_ABSENT_UNEXPLAINED", None


def find_container_logs(base):
    """The arm's container logs, newest last.  Absence is a token."""
    if not os.path.isdir(base):
        return "BASE_ABSENT", []
    try:
        names = [n for n in os.listdir(base)
                 if n.startswith(ARM + "_") and n.endswith(".log")]
    except OSError as e:
        return "BASE_UNREADABLE:%s" % e, []
    if not names:
        return "NO_ARM_LOG_YET", []
    names.sort()
    return "FOUND", [os.path.join(base, n) for n in names]


def run_accept_floor_control(logpath):
    """Call the FROZEN instrument.  Never re-implement its reader here."""
    if not os.path.exists(ACCEPT_FLOOR_CONTROL):
        return {"state": "CONTROL_ABSENT", "path": ACCEPT_FLOOR_CONTROL}
    try:
        p = subprocess.run([sys.executable, ACCEPT_FLOOR_CONTROL,
                            "--log", logpath],
                           capture_output=True, text=True, timeout=180)
    except Exception as e:
        return {"state": "CONTROL_DID_NOT_RUN", "err": str(e)[:400]}
    return {"state": "CONTROL_RAN", "rc": p.returncode,
            "stdout_tail": p.stdout.strip().splitlines()[-12:],
            "stderr_tail": p.stderr.strip().splitlines()[-6:]}


# ---------------------------------------------------------------------
# THE PLANTED CONTROL -- DRIVEN IN BOTH DIRECTIONS BEFORE ARMING.
# ---------------------------------------------------------------------
PLANT_P = "1.234003e-03"      # a value that appears NOWHERE in this file's logic
PLANT_NUTILDA = "5.678009e-04"
PLANT_TIME = "747"


def _plant_log(path):
    """Write a fixture carrying KNOWN values the reader was not told."""
    with open(path, "w") as fh:
        fh.write("some preamble\n")
        fh.write("Time = %s\n\n" % PLANT_TIME)
        fh.write("U0 initRes: 1.1e-07 finalRes: 1.1e-08 nIters: 1\n")
        fh.write("U1 initRes: 2.2e-07 finalRes: 2.2e-08 nIters: 2\n")
        fh.write("U2 initRes: 3.3e-08 finalRes: 3.3e-09 nIters: 1\n")
        fh.write("he initRes: 4.4e-09 finalRes: 4.4e-10 nIters: 2\n")
        fh.write("p initRes: %s finalRes: 9.9e-07 nIters: 1\n" % PLANT_P)
        fh.write("nuTilda initRes: %s finalRes: 8.8e-07 nIters: 1\n"
                 % PLANT_NUTILDA)
        fh.write("CD: 0.0184758685 final: 0.0184758685\n")
        fh.write("CL: 0.3999751808 final: 0.3999751808\n")
        fh.write("ExecutionTime = 19.71 s  ClockTime = 20 s\n")


def selftest(ctrl_dir):
    """Drive every reader BOTH ways.  Exit 0 only if all directions hold."""
    os.makedirs(ctrl_dir, exist_ok=True)
    out, ok = [], True

    def say(good, label, detail):
        nonlocal ok
        if not good:
            ok = False
        out.append("  %-5s %s  %s" % ("OK" if good else "FAIL", label, detail))

    # -------- direction 1: the reader CAN see a planted non-zero ----------
    f = os.path.join(ctrl_dir, "planted.log")
    _plant_log(f)
    state, blocks = read_time_blocks(f)
    saw_p = blocks and blocks[-1]["res"].get("p", {}).get("initRes") == PLANT_P
    saw_nu = blocks and blocks[-1]["res"].get("nuTilda", {}).get("initRes") == PLANT_NUTILDA
    saw_t = blocks and blocks[-1]["Time"] == PLANT_TIME
    saw_all6 = blocks and all(k in blocks[-1]["res"] for k in GCONV_FIELDS)
    say(state == "READ" and saw_p and saw_nu and saw_t and saw_all6,
        "direction 1  PLANTED LOG   ",
        "state=%s Time=%s p=%s nuTilda=%s all6_fields=%s -- the reader SEES a "
        "non-zero it was never told" % (
            state, blocks[-1]["Time"] if blocks else None,
            blocks[-1]["res"].get("p", {}).get("initRes") if blocks else None,
            blocks[-1]["res"].get("nuTilda", {}).get("initRes") if blocks else None,
            saw_all6))

    # -------- direction 2: ABSENT source is a TOKEN, never a zero ---------
    state, blocks = read_time_blocks(os.path.join(ctrl_dir, "does_not_exist.log"))
    say(state == "SOURCE_ABSENT" and blocks == [],
        "direction 2  ABSENT LOG    ",
        "state=%s blocks=%d -- absence reports its own token, NOT an empty "
        "residual set that would read as convergence" % (state, len(blocks)))

    # -------- direction 3: EMPTY source is distinguishable from absent ----
    e = os.path.join(ctrl_dir, "empty.log")
    open(e, "w").close()
    state, blocks = read_time_blocks(e)
    say(state == "SOURCE_EMPTY",
        "direction 3  EMPTY LOG     ",
        "state=%s -- an empty file is NOT the same token as a missing one" % state)

    # -------- direction 4: content with no Time blocks ---------------------
    n = os.path.join(ctrl_dir, "notime.log")
    with open(n, "w") as fh:
        fh.write("Create mesh...\nSIMPLE: no convergence criteria found\n")
    state, blocks = read_time_blocks(n)
    say(state == "NO_TIME_BLOCKS",
        "direction 4  NO TIME BLOCKS",
        "state=%s -- a started-but-uniterated solver is its own state" % state)

    # -------- direction 5: the reader must NOT invent a field -------------
    m = os.path.join(ctrl_dir, "missing_nutilda.log")
    with open(m, "w") as fh:
        fh.write("Time = 10\n\np initRes: 1.0e-05 finalRes: 1.0e-06 nIters: 1\n")
    state, blocks = read_time_blocks(m)
    absent_fields = [k for k in GCONV_FIELDS if k not in blocks[-1]["res"]]
    say(state == "READ" and "nuTilda" in absent_fields and len(absent_fields) == 5,
        "direction 5  MISSING FIELD ",
        "absent=%s -- a field the log does not carry is REPORTED ABSENT, never "
        "defaulted to a passing value (nuTilda is the SECOND binding field)"
        % ",".join(absent_fields))

    # -------- direction 6: the three-way root-absence distinction ---------
    for rc, want in ((None, "ROOT_ABSENT_AWAITING_DAEMON"),
                     (4, "ROOT_ABSENT_LAUNCHER_ABORTED"),
                     (0, "ROOT_ABSENT_UNEXPLAINED")):
        got, _ = resolve_root_state(os.path.join(ctrl_dir, "no_such_root"),
                                    {"launcher_rc": rc})
        say(got == want, "direction 6  ROOT ABSENT rc=%-4s" % rc,
            "state=%s -- a sustained ABSENT is legible as its CAUSE, not as one "
            "undifferentiated fault" % got)
    present = os.path.join(ctrl_dir, "a_root")
    os.makedirs(present, exist_ok=True)
    got, mode = resolve_root_state(present, {"launcher_rc": None})
    say(got == "ROOT_PRESENT", "direction 6  ROOT PRESENT     ",
        "state=%s mode=%s -- and the mode is REPORTED because L-251 gates on it"
        % (got, mode))

    # -------- direction 7: the accept-floor call REACHES the instrument ---
    res = run_accept_floor_control(f)
    say(res.get("state") == "CONTROL_RAN",
        "direction 7  FLOOR CONTROL ",
        "state=%s rc=%s -- the watcher CALLS the frozen instrument; it does not "
        "re-implement the floor reader, so there is only ever ONE answer"
        % (res.get("state"), res.get("rc")))

    hdr = ["D6RF4 P_conv WATCHER -- READERS DRIVEN IN BOTH DIRECTIONS",
           "  planted p initRes    = %s  (appears nowhere in this file's logic)"
           % PLANT_P,
           "  planted nuTilda      = %s" % PLANT_NUTILDA,
           "  planted Time         = %s" % PLANT_TIME]
    tail = ["", "RESULT %s" % ("ALL DIRECTIONS AS REGISTERED" if ok
                               else "NOT AS REGISTERED -- WATCHER NOT ARMED"),
            "driven %s" % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())]
    print("\n".join(hdr + out + tail))
    return 0 if ok else 2


# ---------------------------------------------------------------------
# THE WATCH LOOP.  Observes.  Never launches, never re-fires.
# ---------------------------------------------------------------------
def watch(outpath, interval, deadline_s):
    t0 = time.time()
    last_sig = None

    def emit(s):
        with open(outpath, "a") as fh:
            fh.write(s + "\n")
            fh.flush()

    emit("=" * 72)
    emit("D6RF4 P_conv WATCH  armed %s  pid=%d"
         % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), os.getpid()))
    emit("  base      %s" % REGISTERED_BASE)
    emit("  registered accept floor %s x %s = %.1e  (REPORTED, never gated here)"
         % (REG_TOL, REG_DIFF, REG_FLOOR))
    emit("  THIS WATCHER LAUNCHES NOTHING AND RE-FIRES NOTHING.")
    emit("=" * 72)

    while time.time() - t0 < deadline_s:
        launcher = read_launcher_state()
        rstate, rmode = resolve_root_state(REGISTERED_BASE, launcher)
        lstate, logs = find_container_logs(REGISTERED_BASE)

        detail = ""
        if logs:
            tstate, blocks = read_time_blocks(logs[-1])
            if blocks:
                b = blocks[-1]
                fields = " ".join(
                    "%s=%s" % (k, b["res"].get(k, {}).get("initRes", "ABSENT"))
                    for k in GCONV_FIELDS)
                detail = ("blocks=%d lastTime=%s %s CD=%s CL=%s exec=%s"
                          % (len(blocks), b["Time"], fields, b["CD"], b["CL"],
                             b["ExecutionTime"]))
            else:
                detail = "log_state=%s" % tstate

        sig = (rstate, lstate, detail, launcher.get("launcher_rc"))
        if sig != last_sig:
            emit("%s  root=%s%s  log=%s  launcher_rc=%s"
                 % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    rstate, (" mode=%s" % rmode) if rmode else "",
                    lstate, launcher.get("launcher_rc")))
            if rstate == "ROOT_ABSENT_LAUNCHER_ABORTED":
                emit("    EXPLAINED: the launcher RAN and exited %s.  The root's "
                     "absence is that exit, NOT a pending daemon tick."
                     % launcher.get("launcher_rc"))
                for t in (launcher.get("tail") or []):
                    emit("    launcher| %s" % t)
            elif rstate == "ROOT_ABSENT_AWAITING_DAEMON":
                emit("    EXPECTED: the row is placed and the launcher has not "
                     "run yet.  A sustained reading here is NOT a fault.")
            if detail:
                emit("    %s" % detail)
            if logs:
                fl = run_accept_floor_control(logs[-1])
                emit("    ACCEPT_FLOOR_UNMOVED via frozen instrument: %s"
                     % json.dumps({k: v for k, v in fl.items()
                                   if k != "stdout_tail"}))
                for t in (fl.get("stdout_tail") or []):
                    emit("    floor| %s" % t)
            last_sig = sig
        time.sleep(interval)

    emit("%s  WATCH WINDOW ENDED after %ds -- this is the watcher stopping, "
         "NOT a verdict about the arm."
         % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), deadline_s))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--ctrl-dir", default=None)
    ap.add_argument("--watch", action="store_true")
    ap.add_argument("--out", default=os.path.join(HERE, "P_conv_WATCH.txt"))
    ap.add_argument("--interval", type=float, default=20.0)
    ap.add_argument("--deadline", type=float, default=5400.0)
    a = ap.parse_args()
    if a.selftest:
        d = a.ctrl_dir or os.path.join(
            os.environ.get("TMPDIR", "/tmp"), "d6rf4_watch_ctrl_%d" % os.getpid())
        return selftest(d)
    if a.watch:
        return watch(a.out, a.interval, a.deadline)
    ap.error("one of --selftest or --watch is required")


if __name__ == "__main__":
    sys.exit(main())
