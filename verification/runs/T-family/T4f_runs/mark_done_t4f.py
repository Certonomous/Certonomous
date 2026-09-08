#!/usr/bin/env python3
"""DRAFT completion marker for T4f -- the TRANSIENT / URANS impinging-jet rung.

Adapted from the FROZEN mark_done_t4e.py (blob e4e44396) for a transient run.  Rule 4's clauses 1-4
and clause 6 (the age guard) are UNCHANGED.  Clause 5 is GENERALISED -- and this touches Sanaa's
rule-4 wording, so it is FLAGGED and requires her ruling before freeze (see below).

  1. STATUS.<case> exists and carries the solver's own in-wrapper rc; rc == 0
  2. log.solve carries an `End` line
  3. the last written time == endTime from the case's own system/controlDict (0.08 s)
  4. every registered field present at that time (T U p_rgh alphat nut k omega, plus phi)
  5. *** GENERALISED FOR TRANSIENT ***  the ExecutionTime line count == round(endTime / deltaT), i.e.
     the number of TIME STEPS, reading deltaT from the case's own controlDict.  The frozen instrument
     hard-wires `n_exec == int(endTime)`, which is the deltaT=1 STEADY form (endTime IS the iteration
     count).  For a transient (deltaT 8e-7, endTime 0.08) int(endTime)=0 and that clause spuriously
     fails.  round(endTime/deltaT) is the faithful generalisation (steps-recorded == steps-that-should-
     have-run); with a FIXED deltaT dividing endTime it is EXACT and INTEGER.
       *** THIS CHANGES CLAUDE.md RULE 4 CLAUSE-5 WORDING.  It is NOT a lane's or a supervisor's call.
       Precedent: the phi-field addition to rule 4 was made only on Sanaa's approval (2026-09-06).  The
       supervisor must carry this generalisation to Sanaa BEFORE freeze.  Until then it is a flagged
       open item, not a settled clause. ***
  6. THE AGE GUARD: every field at endTime is NEWER than the case's own 0/T.

PARALLEL (verification ruling 19b7330a): the run is decomposed (method simple).  This instrument
grades the RECONSTRUCTED fields in the case root (launch_t4f.sh runs reconstructPar after the solve),
NOT the processor*/ fields, so clauses 3/4/6 read the case-root endTime dir exactly as for a serial run;
reconstructPar writes those fields AFTER the solve, so they are newer than 0/T (age guard holds).  The
ExecutionTime count (clause 5) is read from the combined master log.solve (mpirun writes one
ExecutionTime line per time step), so round(endTime/deltaT) is UNCHANGED by decomposition.  The
clause-5 generalisation is left EXACTLY as drafted (Sanaa's ruling pending; not pre-empted).

Infrastructure fields (L-342): reported NOT MEASURED, grade proceeds; `capped` labels a non-zero rc.

NO `assert` STATEMENT IN THIS FILE (L-332).  --selftest drives every clause and the STATUS refusal
under python3 and python3 -O.

STATUS: DRAFT.  Not frozen, not run against any real case.

Usage:  python3 mark_done_t4f.py [CASE ...] [--root DIR] | --selftest
Exit codes: 0 all DONE ; 1 at least one NOT DONE ; 2 REFUSAL
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
CASES = ("T4f_IJ_f",)
NEEDED = ("T", "U", "p_rgh", "alphat", "nut", "k", "omega", "phi")
INFRA = ("wall_s", "timeout_s", "ranks", "core_min", "capped", "checkmesh_rc",
         "started_utc", "ended_utc", "solver_path", "note")
EXIT_OK, EXIT_NOTDONE, EXIT_REFUSE = 0, 1, 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def _control_scalar(case, key):
    p = os.path.join(ROOT, case, "system", "controlDict")
    if not os.path.isfile(p):
        refuse("no system/controlDict for %s -- %s is unknowable" % (case, key))
    m = re.search(r"^\s*%s\s+([0-9.eE+-]+)\s*;" % key, open(p).read(), re.M)
    if not m:
        refuse("controlDict for %s states no %s" % (case, key))
    return float(m.group(1))


def expected_steps(case):
    """round(endTime / deltaT) -- the transient clause-5 generalisation (see module docstring)."""
    et = _control_scalar(case, "endTime")
    dt = _control_scalar(case, "deltaT")
    if dt <= 0:
        refuse("controlDict for %s has non-positive deltaT %g" % (case, dt))
    n = et / dt
    rn = round(n)
    if abs(n - rn) > 1e-6:
        refuse("endTime/deltaT = %.6f is not integer for %s -- a FIXED dt dividing endTime is required "
               "so clause 5 is exact (T4f_PREREGISTRATION.md section 6)" % (n, case))
    return et, int(rn)


def read_status(case):
    p = os.path.join(ROOT, "STATUS.%s" % case)
    if not os.path.isfile(p):
        refuse("no STATUS.%s -- the solver's exit status was never recorded; an absent STATUS is "
               "refused, not inferred (K0d L1)." % case)
    txt = open(p).read()
    d = dict(re.findall(r"^([A-Za-z_]+)=(.*)$", txt, re.M))
    if "rc" not in d or not re.fullmatch(r"-?\d+", d["rc"].strip()):
        refuse("STATUS.%s carries no integer rc: %r" % (case, txt.strip()))
    not_measured = [k for k in INFRA if k not in d]
    return d, not_measured


def check(case):
    d = os.path.join(ROOT, case)
    if not os.path.isdir(d):
        refuse("no case directory %s" % d)
    st, nm = read_status(case)
    fails = []
    rc = int(st["rc"])
    if rc != 0:
        label = "CRASH (rc=%d)" % rc
        capped = st.get("capped")
        if capped == "yes":
            label = ("CAPPED (rc=%d, wall_s=%s >= timeout_s=%s): rule 12, the run stopped at its "
                     "registered cap and is NOT A RESULT, never re-launched at a larger cap"
                     % (rc, st.get("wall_s"), st.get("timeout_s")))
        elif capped == "no":
            label = ("CRASH (rc=%d at wall_s=%s below timeout_s=%s): a finding until triage says "
                     "otherwise" % (rc, st.get("wall_s"), st.get("timeout_s")))
        else:
            label += " -- capped witness NOT MEASURED, cap-stop vs crash undetermined"
        fails.append(label)

    log = os.path.join(d, "log.solve")
    if not os.path.isfile(log):
        return fails + ["no log.solve"], nm
    n_end = n_exec = 0
    with open(log, errors="replace") as fh:
        for line in fh:
            if line.startswith("ExecutionTime"):
                n_exec += 1
            elif line.rstrip() == "End":
                n_end += 1
    if n_end == 0:
        fails.append("log.solve has no End line")
    et, n_steps = expected_steps(case)
    times = sorted((float(x) for x in os.listdir(d)
                    if re.fullmatch(r"[0-9]+(\.[0-9]+)?", x)), key=float)
    nonzero = [t for t in times if t > 0]
    if not nonzero:
        return fails + ["no time directory beyond 0 -- the solver wrote no fields"], nm
    last = nonzero[-1]
    if abs(last - et) > 1e-9:
        fails.append("last written time %g != endTime %g" % (last, et))
    tdir = None
    for cand in ("%g" % last, ("%.8g" % last)):
        if os.path.isdir(os.path.join(d, cand)):
            tdir = os.path.join(d, cand)
            break
    if tdir is None:
        return fails + ["cannot resolve the endTime directory for time %g" % last], nm
    miss = [f for f in NEEDED if not os.path.isfile(os.path.join(tdir, f))]
    if miss:
        return fails + ["time %g is missing %s" % (last, ",".join(miss))], nm
    if n_exec != n_steps:
        fails.append("%d ExecutionTime lines, expected %d (= round(endTime/deltaT), transient clause-5 "
                     "generalisation)" % (n_exec, n_steps))
    ref = os.path.join(d, "0", "T")
    if not os.path.isfile(ref):
        fails.append("no 0/T, so the run cannot be dated and the age guard cannot be evaluated")
    else:
        age = os.path.getmtime(ref)
        stale = [f for f in NEEDED if os.path.getmtime(os.path.join(tdir, f)) < age]
        if stale:
            fails.append("time %g holds fields OLDER than 0/T (%s) -- not written by this run"
                         % (last, ",".join(stale)))
    return fails, nm


def _forge(root, case, rc="0", endTime=0.08, deltaT=8e-7, n_exec=None, with_end=True,
           stale=False, status=True, infra=True, missing_field=None):
    import time
    d = os.path.join(root, case)
    os.makedirs(os.path.join(d, "system"), exist_ok=True)
    os.makedirs(os.path.join(d, "0"), exist_ok=True)
    open(os.path.join(d, "system", "controlDict"), "w").write(
        "endTime %.10g;\ndeltaT %.10g;\n" % (endTime, deltaT))
    open(os.path.join(d, "0", "T"), "w").write("x\n")
    t0 = time.time() - 100
    os.utime(os.path.join(d, "0", "T"), (t0, t0))
    tname = "%g" % endTime
    td = os.path.join(d, tname)
    os.makedirs(td, exist_ok=True)
    for f in NEEDED:
        if f == missing_field:
            continue
        p = os.path.join(td, f)
        open(p, "w").write("y\n")
        if stale:
            os.utime(p, (t0 - 100, t0 - 100))
    n = int(round(endTime / deltaT)) if n_exec is None else n_exec
    open(os.path.join(d, "log.solve"), "w").write(
        "ExecutionTime = 1 s\n" * n + ("End\n" if with_end else ""))
    if status:
        lines = ["case=%s" % case, "rc=%s" % rc]
        if infra:
            lines += ["wall_s=10", "ranks=1", "core_min=0.167", "timeout_s=600", "capped=no",
                      "checkmesh_rc=0", "started_utc=x", "ended_utc=y", "solver_path=/x", "note=clean"]
        open(os.path.join(root, "STATUS.%s" % case), "w").write("\n".join(lines) + "\n")


def selftest():
    import shutil
    import tempfile
    global ROOT
    fails = []
    case = CASES[0]

    def expect(name, want_code, want_marker, **kw):
        global ROOT
        tmp = tempfile.mkdtemp(prefix="md4f_")
        try:
            _forge(tmp, case, **kw)
            ROOT = tmp
            code = None
            try:
                code = main([case])
            except SystemExit as e:
                code = e.code
            marker = os.path.exists(os.path.join(tmp, "DONE.%s" % case))
            ok = (code == want_code) and (marker == want_marker)
            print("  [%s] %s -> exit %s, marker %s" % ("ok " if ok else "FAIL", name, code, marker))
            if not ok:
                fails.append(name)
        finally:
            ROOT = HERE
            shutil.rmtree(tmp, ignore_errors=True)

    print("mark_done_t4f selftest (transient clause-5 generalisation driven both ways):")
    expect("clean transient case (100000 steps @ dt 8e-7) -> DONE", 0, True)
    expect("rc=1 -> NOT DONE (CRASH)", 1, False, rc="1")
    expect("no End line -> NOT DONE", 1, False, with_end=False)
    expect("ExecutionTime count short (one step missing) -> NOT DONE", 1, False,
           n_exec=int(round(0.08 / 8e-7)) - 1)
    expect("clause-5 generalisation: int(endTime)=0 would spuriously fail steady form; here the "
           "correct round(endTime/deltaT) count -> DONE", 0, True)
    expect("a field missing at endTime -> NOT DONE", 1, False, missing_field=NEEDED[0])
    expect("age guard (fields older than 0/T) -> NOT DONE", 1, False, stale=True)
    expect("absent STATUS -> REFUSE exit 2", 2, False, status=False)
    expect("all infrastructure absent -> still DONE, NOT MEASURED disclosed", 0, True, infra=False)
    import ast
    n_assert = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse(open(os.path.abspath(__file__)).read())))
    ok = (n_assert == 0)
    print("  [%s] AST assert count in this file = %d (must be 0)" % ("ok " if ok else "FAIL", n_assert))
    if not ok:
        fails.append("ast")
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main(argv):
    global ROOT
    if "--selftest" in argv:
        return selftest()
    if "--root" in argv:
        ROOT = os.path.abspath(argv[argv.index("--root") + 1])
        argv = [a for i, a in enumerate(argv) if a != "--root" and (i == 0 or argv[i - 1] != "--root")]
    want = [a for a in argv if not a.startswith("-")] or list(CASES)
    for c in want:
        if c not in CASES:
            refuse("%r is not the registered T4f case: %s" % (c, " ".join(CASES)))
    rc = EXIT_OK
    for case in want:
        f, nm = check(case)
        infra = ("  [infrastructure NOT MEASURED: %s -- disclosed, grade proceeds]" % ",".join(nm)) if nm else ""
        if f:
            rc = EXIT_NOTDONE
            print("NOT DONE  %-10s - %s%s" % (case, "; ".join(f), infra))
        else:
            marker = os.path.join(ROOT, "DONE.%s" % case)
            if not os.path.exists(marker):
                open(marker, "w").write("strict rule met (clauses 1-6; clause 5 = transient "
                                        "round(endTime/deltaT), pending Sanaa's ruling)%s\n" % infra)
            print("DONE      %-10s%s" % (case, infra))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
