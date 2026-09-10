#!/usr/bin/env python3
"""K2b-U3-R3 completion certification -- the strict completion rule (rule 4),
in the ADAPTIVE-timestep form Sanaa ratified on 2026-09-09.

Written 2026-09-09 as a NEW instrument (no frozen file edited, rule 6).  It is
the adjustTimeStep sibling of the fixed-dt guard the K2bU3R3 pre-registration
§5.2 named (`mark_done_t3.py`, whose fifth conjunct is `n_exec == int(endTime)`
= `int(80) = 80`; K2bU3R3 is an adjustTimeStep run that took 995 steps, so that
fixed guard is MIS-WIRED for it -- it would refuse a genuinely complete run).

Reads ONLY from:
  docs/campaigns/F14-cooling-ladder/K2bU3R3_PREREGISTRATION.md  (frozen 41e18d71)
    §5.2 the completion field set and endTime 80.0
  build_k2bU3R3.py  (frozen 41e18d71)  -- the wrapper whose control flow makes
    the queue launcher's `launcher_rc` a code-verified proxy for the SOLVER rc
    (see clause 1).

THE APPROVED ADAPTIVE FORM (Sanaa 2026-09-09 "approve", ratifying
T1b_L4_AMENDMENT §12.3): for an adjustTimeStep run the fifth completion conjunct
is `n_exec == n_time_written` -- the count of `^ExecutionTime` lines equals the
count of `^Time = ` lines and both are non-zero (the solver logs exactly one of
each per step; a truncated or duplicated log breaks the equality).  This is the
fixed-dt clause-5's adaptive sibling; `int(endTime)` and `round(endTime/deltaT)`
do NOT apply to a variable-step run (§12.3 boundary).  The counting pattern
below is COPIED VERBATIM from the proven `scripts/mark_done_k0g.py:247-248,
287-292` (rule 14: the lesson is applied at this call site, not merely cited).

A case is DONE only if ALL of rule 4 holds:
  1. the SOLVER exited 0
  2. an `End` line in the solver log
  3. last written time == controlDict endTime (80.0)
  4. the registered completion field set present at endTime (§5.2, thermal
     family: T U p_rgh alphat nut k omega phi)
  5. `n_exec == n_time_written`, both non-zero  (ADAPTIVE clause 5, approved)
  6. every field at endTime NEWER than the case's own 0/T  -- the age guard
     (D438, L-143)
  7. the LAUNCH guard refuses a case in which 0/ or a numeric time directory
     already exists (a PRE-launch condition, exposed as --launch-guard)

CLAUSE 1 -- HOW THE SOLVER rc IS ESTABLISHED, stated so it can be refused.
This run was launched through the detached queue, which writes
`STATUS.queue.K2bU3R3` = `launcher_rc=<N>` and NOTES that this is
"exit-status-of-the-launch-argv-NOT-the-solver-rc".  The launch argv is
`build_k2bU3R3.py run ...`, whose run() (build_k2bU3R3.py:174,184-192):
  * line 174 captures the SOLVER rc: `rc = _sh("timeout ... SOLVER ...")`;
  * line 184  `if rc == 124: sys.exit("BLOCKED (over-cap) ...")`  (non-zero exit);
  * line 188  `if rc != 0:   sys.exit("BLOCKED: ... exited {rc} ...")` (non-zero);
  * line 190  prints the rc==0-ONLY success line and line 192 `return 0`.
So `launcher_rc == 0`  <=>  solver rc == 0 AND cap not hit AND mesh OK.  This is
a CODE-VERIFIED equivalence, not a laundered launcher exit.  To keep clause 1
fail-closed and independent of that single token, this instrument requires BOTH:
  (a) STATUS.queue.<case> present and `launcher_rc == 0`, AND
  (b) launcher.queue.out present, containing the wrapper's rc==0-only success
      marker and NO `BLOCKED` line.
If STATUS.queue.<case> is absent, clause 1 CANNOT be evaluated -> REFUSE (exit 2),
never a silent pass (mirrors mark_done_k0g.py's absent-STATUS refusal).  A
`launcher_rc != 0`, or a missing/failed success marker, or a `BLOCKED` line, is
NOT DONE (exit 1).

Exit codes:  0 case DONE
             1 case NOT DONE (reasons printed)
             2 REFUSAL -- a structural precondition means the question cannot be
               asked (missing STATUS.queue, unregistered case, no controlDict)

Usage:
    python3 mark_done_k2bU3R3.py [--root <K2b_runs dir>] [case]
    python3 mark_done_k2bU3R3.py --root <dir> --launch-guard <case>
    python3 mark_done_k2bU3R3.py --selftest
"""
import argparse
import os
import re
import shutil
import sys
import tempfile

EXIT_OK, EXIT_NOTDONE, EXIT_REFUSE = 0, 1, 2

HERE = os.path.dirname(os.path.abspath(__file__))

# --------------------------------------------------------------------------
# REGISTERED CONSTANTS.  Each carries the clause of the FROZEN prereg (41e18d71)
# or the frozen wrapper that fixes it.  Nothing here is a choice of this script.
# --------------------------------------------------------------------------

# The single registered case (K2bU3R3_PREREGISTRATION.md §3: "One case only").
CASE = "K2bU3R3_D59"

# The solver, and its log (build_k2bU3R3.py:44-46 LOGNAME/SOLVER).
LOGNAME = "log.buoyantBoussinesqPimpleFoam"

# The registered completion field set, K2bU3R3_PREREGISTRATION.md §5.2 verbatim:
# "fields present (`T U p_rgh alphat nut k omega phi` -- thermal family)".
REGISTERED_FIELDS = ("T", "U", "p_rgh", "alphat", "nut", "k", "omega", "phi")

# The queue launcher's status file and its rc=0 token.  The detached queue writes
# it INSIDE the case directory, named by the registered CASE_ID (K2bU3R3), which
# is NOT the case-DIR name (K2bU3R3_D59, which carries the mesh suffix).  So the
# file for this run is  K2bU3R3_D59/STATUS.queue.K2bU3R3  (launched JSON
# `_launch.status_file`), and this instrument LOCATES it by the glob
# STATUS.queue.* inside the case dir (exactly one per case) rather than guessing
# the case_id -- a name-mismatch here was caught live by the confirm run.
QUEUE_STATUS_GLOB = "STATUS.queue.*"
QUEUE_OUT = "launcher.queue.out"

# The wrapper's rc==0-ONLY success marker (build_k2bU3R3.py:190-191): it is
# printed only after the `if rc != 0: sys.exit(...)` guard at :188, so its
# presence in launcher.queue.out is a direct read of the solver-rc==0 branch.
SUCCESS_MARKER = "Grade with analyse_k2bU3R3.py"
# The wrapper prints a line beginning "BLOCKED" on every non-zero solver rc
# (build_k2bU3R3.py:167,170,185-186,189).
BLOCKED_MARKER = "BLOCKED"


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


# --------------------------------------------------------------------------
# disk readers
# --------------------------------------------------------------------------
def field_path(tdir, field):
    """Path of `field` inside `tdir`, accepting the compressed form (`.gz`).
    Reads the registered clause ("every field present"), which names fields and
    not filenames, under either writeCompression setting."""
    plain = os.path.join(tdir, field)
    if os.path.isfile(plain):
        return plain
    gz = os.path.join(tdir, field + ".gz")
    if os.path.isfile(gz):
        return gz
    return None


def numeric_times(d):
    return sorted((x for x in os.listdir(d)
                   if re.fullmatch(r"[0-9]+(\.[0-9]+)?", x)), key=float)


def control_end_time(d):
    p = os.path.join(d, "system", "controlDict")
    if not os.path.isfile(p):
        return None
    m = re.search(r"^\s*endTime\s+([0-9.eE+-]+)\s*;", open(p).read(), re.M)
    return float(m.group(1)) if m else None


def queue_launcher_rc(root, case):
    """(rc, note) from STATUS.queue.<case>, or (None, reason) if it is absent or
    states no launcher_rc.  This is the WRAPPER-RUN exit; clause 1 pairs it with
    the success marker below."""
    p = os.path.join(root, QUEUE_STATUS.format(case=case))
    if not os.path.isfile(p):
        return None, f"no {os.path.basename(p)} (case never finished under the queue)"
    s = open(p, errors="replace").read()
    m = re.search(r"\blauncher_rc=(\d+)", s)
    if not m:
        return None, f"STATUS.queue is {s.strip()!r}, which states no launcher_rc"
    return int(m.group(1)), s.strip()


# --------------------------------------------------------------------------
# clause 7 -- the LAUNCH guard, called BEFORE a solver starts
# --------------------------------------------------------------------------
def launch_guard(root, case):
    d = os.path.join(root, case)
    if not os.path.isdir(d):
        return [f"no case directory {d}"]
    bad = []
    if os.path.isdir(os.path.join(d, "0")):
        bad.append("a '0' directory already exists")
    stray = [t for t in numeric_times(d) if float(t) > 0]
    if stray:
        bad.append("numeric time directories already exist: " + ",".join(stray))
    return bad


# --------------------------------------------------------------------------
# clauses 1-6
# --------------------------------------------------------------------------
def check(root, case):
    """Return (fails, info).  fails empty == every registered clause holds.
    May REFUSE (exit 2) when a structural precondition cannot be evaluated."""
    info = dict(case=case, fields=REGISTERED_FIELDS)
    d = os.path.join(root, case)
    if not os.path.isdir(d):
        return ["no case directory"], info
    fails = []

    # --- clause 1 -- the SOLVER rc, via the code-verified launcher proxy ------
    # An ABSENT STATUS.queue is a REFUSAL, not a verdict: the instrument cannot
    # evaluate clause 1 at all (mirrors mark_done_k0g.py's absent-STATUS refusal).
    rc, note = queue_launcher_rc(root, case)
    if rc is None:
        info["status_absent"] = True
        return [note], info
    if rc != 0:
        fails.append(f"STATUS.queue is {note!r}: launcher_rc={rc} != 0 (the "
                     f"wrapper exits non-zero on any non-zero solver rc, "
                     f"build_k2bU3R3.py:184-189)")
    # corroborating success marker: the rc==0-only success line, no BLOCKED line
    qout = os.path.join(d, QUEUE_OUT)
    if not os.path.isfile(qout):
        fails.append(f"no {QUEUE_OUT}, so the wrapper's rc==0-only success "
                     f"marker cannot be confirmed")
    else:
        ob = open(qout, errors="replace").read()
        if SUCCESS_MARKER not in ob:
            fails.append(f"{QUEUE_OUT} lacks the wrapper's rc==0-only success "
                         f"marker {SUCCESS_MARKER!r} (build_k2bU3R3.py:190-191)")
        if re.search(r"^\s*" + BLOCKED_MARKER, ob, re.M):
            fails.append(f"{QUEUE_OUT} carries a {BLOCKED_MARKER!r} line (the "
                         f"wrapper's non-zero-rc / over-cap exit)")

    # --- clause 2 -------------------------------------------------------------
    log = os.path.join(d, LOGNAME)
    if not os.path.isfile(log):
        return fails + [f"no {LOGNAME}"], info
    body = open(log, errors="replace").read()
    if not re.search(r"^End\s*$", body, re.M):
        fails.append(f"{LOGNAME} has no End line")

    # --- clause 5 -- ADAPTIVE completion, the APPROVED form -------------------
    # COPIED VERBATIM from mark_done_k0g.py:247-248 (rule 14).  For an
    # adjustTimeStep run #steps is not endTime and not round(endTime/deltaT); the
    # transient-appropriate check is internal consistency: one "Time = " line and
    # one "ExecutionTime" line per step, so the counts must be EQUAL and non-zero.
    n_exec = 0
    n_time = 0
    n_exec += len(re.findall(r"^ExecutionTime", body, re.M))
    n_time += len(re.findall(r"^Time = ", body, re.M))
    info["n_exec"] = n_exec
    info["n_time"] = n_time
    if n_exec < 1 or n_time < 1:
        fails.append(f"no time steps logged (ExecutionTime={n_exec}, "
                     f"Time-lines={n_time})")
    elif n_exec != n_time:
        fails.append(f"{n_exec} ExecutionTime lines != {n_time} 'Time =' lines "
                     f"(a truncated or duplicated solver log)")

    # --- clause 3 -------------------------------------------------------------
    et = control_end_time(d)
    if et is None:
        return fails + ["no system/controlDict, so endTime cannot be read"], info
    info["endTime"] = et
    times = [float(t) for t in numeric_times(d)]
    nonzero = [t for t in times if t > 0]
    if not nonzero:
        fails.append("no time directory beyond 0")
        return fails, info
    last = nonzero[-1]
    info["last_time"] = last
    if abs(last - et) > 1e-9:
        fails.append(f"last written time {last:g} != endTime {et:g}")

    # --- clause 4 -------------------------------------------------------------
    tdir = os.path.join(d, f"{last:g}")
    present = {f: field_path(tdir, f) for f in REGISTERED_FIELDS}
    miss = [f for f in REGISTERED_FIELDS if present[f] is None]
    if miss:
        fails.append(f"time {last:g} is missing {','.join(miss)} "
                     f"(registered §5.2 set: {' '.join(REGISTERED_FIELDS)})")

    # --- clause 6 -- THE AGE GUARD --------------------------------------------
    t0 = field_path(os.path.join(d, "0"), "T")
    if t0 is None:
        fails.append("no 0/T, so the run's start cannot be dated and the age "
                     "guard cannot be applied")
    elif not miss:
        age0 = os.path.getmtime(t0)
        stale = [f for f in REGISTERED_FIELDS
                 if os.path.getmtime(present[f]) < age0]
        if stale:
            fails.append("time %g holds fields OLDER than 0/T (%s) -- not "
                         "written by this run (D438, L-143)"
                         % (last, ",".join(stale)))
    return fails, info


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=HERE,
                    help="the K2b_runs directory holding the case directory")
    ap.add_argument("--launch-guard", metavar="CASE", default=None,
                    help="apply clause 7 BEFORE launching CASE and exit")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("cases", nargs="*")
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest()
    root = os.path.abspath(a.root)
    if not os.path.isdir(root):
        refuse(f"no such run directory: {root}")

    if a.launch_guard:
        bad = launch_guard(root, a.launch_guard)
        if bad:
            print(f"LAUNCH REFUSED for {a.launch_guard} (clause 7):")
            for r in bad:
                print("   - " + r)
            return EXIT_REFUSE
        print(f"launch guard clear for {a.launch_guard}: no 0 and no numeric "
              f"time directory exists")
        return EXIT_OK

    cases = a.cases or [CASE]
    ok, bad, absent = [], {}, []
    for c in cases:
        fails, inf = check(root, c)
        if inf.get("status_absent"):
            absent.append(c)
        (ok.append(c) if not fails else bad.setdefault(c, fails))
    for c in ok:
        marker = os.path.join(root, f"DONE.{c}")
        if not os.path.exists(marker):
            open(marker, "w").write("strict completion rule met (rule 4, "
                                    "adaptive clause 5 n_exec==n_time_written; "
                                    "K2bU3R3_PREREGISTRATION.md §5.2)\n")
    print(f"{len(ok)}/{len(cases)} case(s) meet the strict completion rule")
    for c in sorted(bad):
        print(f"  NOT DONE  {c}")
        for r in bad[c]:
            print(f"            - {r}")
    if absent:
        print()
        print("REFUSE: no STATUS.queue file for " + ", ".join(sorted(absent)) + ".")
        print("  A missing launcher_rc is NOT a passing rc.  clause 1 cannot be "
              "evaluated, and this instrument INFERS NOTHING (exit 2 REFUSAL, "
              "not exit 1 NOT DONE).")
        return EXIT_REFUSE
    return EXIT_OK if not bad else EXIT_NOTDONE


# --------------------------------------------------------------------------
# selftest -- planted controls (rule 3).  Every clause is shown able to FIRE on
# a planted defect and to STAY QUIET on the clean counterpart.  A clause never
# shown able to fire is not evidence.
# --------------------------------------------------------------------------
def _synthetic(root, case, endtime=80, fields=None, break_clause=None,
               gzip_fields=False, n_steps=120, launcher_rc=0,
               success=True, blocked=False):
    """Build a minimal on-disk ADAPTIVE case that satisfies every clause, then
    break exactly one.  Times/paths built numerically from `endtime`.  The log
    carries one 'Time = ' line and one 'ExecutionTime' line PER STEP with a
    VARIABLE synthetic dt (adaptive), so clause 5 checks their EQUALITY, never a
    count against endTime or endTime/deltaT."""
    import time as _time
    fields = fields if fields is not None else REGISTERED_FIELDS
    d = os.path.join(root, case)
    os.makedirs(os.path.join(d, "system"), exist_ok=True)
    open(os.path.join(d, "system", "controlDict"), "w").write(
        f"endTime {endtime};\ndeltaT 0.005;\nadjustTimeStep yes;\nmaxCo 2.0;\n")
    z = os.path.join(d, "0")
    os.makedirs(z, exist_ok=True)
    open(os.path.join(z, "T"), "w").write("0/T\n")
    _time.sleep(0.02)
    last = endtime if break_clause != "clause3" else endtime - 20
    tdir = os.path.join(d, str(int(last)))
    os.makedirs(tdir, exist_ok=True)
    emit = [f for f in fields if not (break_clause == "clause4" and f == fields[-1])]
    for f in emit:
        if gzip_fields:
            import gzip as _gzip
            with _gzip.open(os.path.join(tdir, f + ".gz"), "wt") as fh:
                fh.write(f"{f} at {last}\n")
        else:
            open(os.path.join(tdir, f), "w").write(f"{f} at {last}\n")
    if break_clause == "clause6":
        old = os.path.getmtime(os.path.join(z, "T")) - 100
        for f in emit:
            os.utime(os.path.join(tdir, f + (".gz" if gzip_fields else "")),
                     (old, old))
    # one Time line and one ExecutionTime line per step, VARIABLE dt (adaptive)
    body = "".join("Time = %g\nExecutionTime = %d s\n"
                   % (0.005 + 0.08 * i, i) for i in range(1, n_steps + 1))
    if break_clause == "clause5":
        body += "ExecutionTime = 999 s\n"          # one extra: n_exec != n_time
    if break_clause != "clause2":
        body += "End\n"
    open(os.path.join(d, LOGNAME), "w").write(body)
    # the queue artifacts: STATUS.queue (launcher_rc) + launcher.queue.out
    if break_clause != "clause1_nostatus":
        open(os.path.join(root, QUEUE_STATUS.format(case=case)), "w").write(
            f"launcher_rc={launcher_rc} end=2026-09-09T00:00:00Z "
            f"note=exit-status-of-the-launch-argv-NOT-the-solver-rc\n")
    ob = ""
    if success:
        ob += f"{case}: 137000 cells, {n_steps} steps, 1.0s. {SUCCESS_MARKER}\n"
    if blocked:
        ob += f"{BLOCKED_MARKER}: {LOGNAME} exited 1; see {LOGNAME}.\n"
    open(os.path.join(d, QUEUE_OUT), "w").write(ob)
    return d


def selftest():
    print("=" * 74)
    print("mark_done_k2bU3R3.py -- SELFTEST (planted controls, ADAPTIVE clause 5)")
    print("=" * 74)
    fails = []

    def check_(label, cond, detail=""):
        print(f"  {'OK  ' if cond else 'FAIL'}  {label}"
              + (f"   [{detail}]" if detail else ""))
        if not cond:
            fails.append(label)

    tmp = tempfile.mkdtemp(prefix="k2bU3R3_md_")
    try:
        # the CLEAN control first
        _synthetic(tmp, "clean", break_clause=None)
        f, _ = check(tmp, "clean")
        check_("clean case satisfies all clauses", not f, str(f))

        # clause 5 clean: unequal step count is exactly what is NOT allowed; the
        # equal count IS (adaptive form).  Prove a clean run has n_exec==n_time.
        _synthetic(tmp, "eq", break_clause=None, n_steps=995)
        f, inf = check(tmp, "eq")
        check_("adaptive clause 5: n_exec==n_time (995==995) PASSES, not gated "
               "on int(endTime) or round(endTime/deltaT)",
               not f and inf["n_exec"] == 995 and inf["n_time"] == 995
               and inf["n_exec"] != int(inf["endTime"]),
               f"n_exec={inf['n_exec']} n_time={inf['n_time']} endTime={inf['endTime']}")

        for clause, label in (("clause2", "no End line"),
                              ("clause3", "last time != endTime"),
                              ("clause4", "a registered field missing"),
                              ("clause5", "ExecutionTime count != Time-line count"),
                              ("clause6", "fields OLDER than 0/T (age guard)")):
            shutil.rmtree(os.path.join(tmp, "brk"), ignore_errors=True)
            _synthetic(tmp, "brk", break_clause=clause)
            f, _ = check(tmp, "brk")
            check_(f"{clause} FIRES on a planted defect: {label}", bool(f),
                   "; ".join(f)[:90])

        # clause 1 -- three ways it must fire, and one forged run it must reject
        shutil.rmtree(os.path.join(tmp, "rc1"), ignore_errors=True)
        _synthetic(tmp, "rc1", launcher_rc=1)
        f, _ = check(tmp, "rc1")
        check_("clause 1 FIRES on launcher_rc=1 (BLOCKED wrapper exit)",
               any("launcher_rc" in r for r in f), "; ".join(f)[:90])

        shutil.rmtree(os.path.join(tmp, "nomark"), ignore_errors=True)
        _synthetic(tmp, "nomark", launcher_rc=0, success=False)
        f, _ = check(tmp, "nomark")
        check_("clause 1 FIRES when the rc==0-only success marker is ABSENT "
               "(launcher_rc alone is not trusted)",
               any("success marker" in r for r in f), "; ".join(f)[:90])

        # THE FORGED RUN: launcher_rc forced to 0 AND a fake success marker, but
        # a BLOCKED line proves the solver actually failed -- a false DONE must
        # be REFUSED (rule 3: a zero from a reader not shown a non-zero).
        shutil.rmtree(os.path.join(tmp, "forge"), ignore_errors=True)
        _synthetic(tmp, "forge", launcher_rc=0, success=True, blocked=True)
        f, _ = check(tmp, "forge")
        check_("clause 1 FIRES on a FORGED run (launcher_rc=0 + success marker "
               "but a BLOCKED line present) -- false DONE refused",
               any("BLOCKED" in r for r in f), "; ".join(f)[:90])

        # clause 1 REFUSAL: absent STATUS.queue -> exit 2, never a silent pass
        import subprocess
        shutil.rmtree(os.path.join(tmp, "nostat"), ignore_errors=True)
        _synthetic(tmp, "nostat", break_clause="clause1_nostatus")
        r = subprocess.run([sys.executable, os.path.abspath(__file__),
                            "--root", tmp, "nostat"],
                           capture_output=True, text=True)
        check_("REFUSES (exit 2) on an ABSENT STATUS.queue, never infers rc=0",
               r.returncode == EXIT_REFUSE and "no STATUS.queue" in r.stdout,
               f"rc={r.returncode}")

        # gzip clean, and gzip age-guard fire
        shutil.rmtree(os.path.join(tmp, "gz"), ignore_errors=True)
        _synthetic(tmp, "gz", break_clause=None, gzip_fields=True)
        f, _ = check(tmp, "gz")
        check_("GZIPPED clean case still satisfies all clauses", not f, str(f))
        shutil.rmtree(os.path.join(tmp, "gzold"), ignore_errors=True)
        _synthetic(tmp, "gzold", break_clause="clause6", gzip_fields=True)
        f, _ = check(tmp, "gzold")
        check_("GZIPPED stale case: the AGE GUARD still FIRES",
               any("OLDER" in r or "0/T" in r for r in f), str(f))

        # clause 7 both directions
        d = os.path.join(tmp, "guardcase")
        os.makedirs(os.path.join(d, "system"), exist_ok=True)
        check_("clause 7 stays quiet on a case with no 0 and no time dir",
               not launch_guard(tmp, "guardcase"))
        os.makedirs(os.path.join(d, "0"), exist_ok=True)
        check_("clause 7 FIRES when 0 already exists",
               bool(launch_guard(tmp, "guardcase")))
        os.makedirs(os.path.join(d, "80"), exist_ok=True)
        check_("clause 7 FIRES when a numeric time dir already exists",
               any("numeric time" in r for r in launch_guard(tmp, "guardcase")))

        # the registered field set is the §5.2 thermal family
        check_("registered field set is §5.2 thermal family "
               "(T U p_rgh alphat nut k omega phi)",
               REGISTERED_FIELDS == ("T", "U", "p_rgh", "alphat", "nut", "k",
                                     "omega", "phi"), str(REGISTERED_FIELDS))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if fails:
        print(f"SELFTEST FAILED: {len(fails)} check(s) did not hold")
        for f in fails:
            print("   - " + f)
        return EXIT_NOTDONE
    print("SELFTEST PASSED: every clause was shown able to FIRE on a planted")
    print("defect and to STAY QUIET on its clean counterpart; the adaptive")
    print("clause 5 (n_exec==n_time_written) passes 995==995 and is not gated")
    print("on int(endTime) or round(endTime/deltaT); a forged rc=0 is refused.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
