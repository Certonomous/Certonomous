#!/usr/bin/env python3
"""PRD-E1 COMPLETION GUARD -- STRICT COMPLETION RULE (CLAUDE.md rule 4),
all-or-nothing, FIXED-deltaT clause-5, for the incompressible isothermal
simpleFoam porous-duct case.  FAIL-CLOSED: any incomplete clause is NOT DONE and
a structural precondition failure is a REFUSAL (exit 2), never an inference.

STOP-BEFORE-FREEZE.  Authored for the supervisor's non-delegable §3 check-1
diff-read and verification's audit; NOTHING is launched or graded here.

WHICH PATTERN THIS IS.  It is `verification/runs/T-family/T23_runs/mark_done_t23.py`
in shape (rc-DERIVE path for a queue-clobbered STATUS; L-342 physics/infrastructure
split; "REFUSE, never degrade"), with the T23 multi-region field tuple REPLACED by
the SINGLE-REGION INCOMPRESSIBLE ISOTHERMAL set and the T23 adaptive concerns
dropped -- this case is steady simpleFoam with deltaT=1 (clause-5 fixed-dt).

THE FIELD SET IS EXPLICIT AND IS NOT THE THERMAL SET (draft §7 clause 5:315;
ruling §4.5).  This is INCOMPRESSIBLE ISOTHERMAL: there is no energy equation,
no T, no p_rgh, no alphat.

    NEEDED = (U, p, k, omega, nut, phi)

`phi` is included per Sanaa's 2026-09-06 addition to rule 4.  `p` here is the
KINEMATIC pressure simpleFoam writes; the comparator multiplies Delta-p by rho.

THE SIX CONJUNCTS (CLAUDE.md rule 4), every one evaluated:
  1. rc = 0            -- READ from STATUS if it carries an integer rc, else
                          DERIVED FROM THE LOG (End==1, FOAM FATAL==0,
                          last==endTime); launcher_rc is NEVER accepted as rc
                          (L-342; Sanaa 2026-08-26 "bookkeeping never voids
                          physics"); every line says rc_source.
  2. exactly one End line, and zero FOAM FATAL.
  3. last written time == controlDict endTime.
  4. every NEEDED field present at endTime.
  5. clause-5 FIXED-deltaT: ExecutionTime line count == round(endTime/deltaT).
     Steady simpleFoam with deltaT=1 => the count equals endTime.  This is the
     FIXED-deltaT form (T1b_L4_AMENDMENT §12, Sanaa 2026-09-09), NOT the
     adaptive n_exec==n_time path -- that path is only for adjustTimeStep runs.
  6. AGE GUARD: every field at endTime NEWER than the case's own 0/U (the
     age reference the launcher touches LAST; a single-region incompressible case
     has no 0/T).  A field older than 0/U was not written by this run (D438,L-143).
  7. LAUNCH GUARD (--launch-guard): REFUSE a case where 0/ or a numeric time dir
     already exists, so a stale directory cannot be graded as this run's output.

An ABSENT STATUS is a REFUSAL, never inferred from an End line (K0d L1).
NO module-level assert (L-332).  --selftest forges cases and drives every clause
under python3 and python3 -O, with a PLANTED control on each (rule 3 discipline:
a clause never shown able to FIRE is not known to work).

Usage:
  python3 mark_done_prd.py --root DIR --case NAME [--endtime N] [--rc-policy derive|read]
  python3 mark_done_prd.py --root DIR --launch-guard CASE
  python3 mark_done_prd.py --selftest
Exit: 0 DONE, 1 NOT DONE, 2 REFUSAL.
"""
import argparse
import os
import re
import sys

EXIT_OK, EXIT_NOTDONE, EXIT_REFUSE = 0, 1, 2

# INCOMPRESSIBLE ISOTHERMAL simpleFoam field set (draft §7 clause 5; ruling §4.5).
# NOT the thermal {T, p_rgh, alphat}.  `phi` per Sanaa 2026-09-06.
NEEDED = ("U", "p", "k", "omega", "nut", "phi")
AGE_REF = ("0", "U")     # the launcher touches 0/U LAST (no 0/T in this case)
INFRA = ("wall_s", "ranks", "core_min", "cap_core_min", "timeout_s",
         "capped", "solver")


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def _controldict(root, case):
    p = os.path.join(root, case, "system", "controlDict")
    if not os.path.isfile(p):
        refuse("no system/controlDict for %s -- a completion rule that guesses "
               "its own target is not a rule" % case)
    return p


def control_num(cd_path, key):
    m = re.search(r"^\s*%s\s+([0-9.eE+-]+)\s*;" % key, open(cd_path).read(), re.M)
    if not m:
        refuse("controlDict %s states no %s" % (cd_path, key))
    return float(m.group(1))


def field_path(tdir, field):
    plain = os.path.join(tdir, field)
    if os.path.isfile(plain):
        return plain
    gz = plain + ".gz"
    return gz if os.path.isfile(gz) else None


def numeric_times(d):
    return sorted((x for x in os.listdir(d)
                   if re.fullmatch(r"[0-9]+(\.[0-9]+)?", x)), key=float)


def read_status(root, case):
    p = os.path.join(root, case, "STATUS.%s" % case)
    if not os.path.isfile(p):
        refuse("no STATUS.%s -- the run's own record was never written. An "
               "absent STATUS is not inferred from an End line (K0d L1); it is "
               "refused." % case)
    return dict(re.findall(r"([A-Za-z_]\w*)=(\S+)", open(p, errors="replace").read()))


def launch_guard(root, case):
    """Clause 7: refuse a case where 0/ or a numeric time dir already exists."""
    d = os.path.join(root, case)
    if not os.path.isdir(d):
        return ["no case directory %s" % d]
    bad = []
    if os.path.isdir(os.path.join(d, "0")):
        bad.append("a '0' directory already exists (age guard cannot be trusted)")
    stray = [t for t in numeric_times(d) if float(t) > 0]
    if stray:
        bad.append("numeric time directories already exist: " + ",".join(stray))
    return bad


def check(root, case, endtime=None, rc_policy="derive"):
    """-> (fails, notes).  fails non-empty => NOT DONE."""
    fails, notes = [], []
    d = os.path.join(root, case)
    if not os.path.isdir(d):
        return ["no case directory"], notes

    st = read_status(root, case)                     # may REFUSE (exit 2)

    missing = [k for k in INFRA if k not in st]
    if missing:
        notes.append("INFRASTRUCTURE fields NOT MEASURED (L-342; reported, not "
                     "refused): " + ",".join(missing))

    log = os.path.join(d, "log.simpleFoam")
    if not os.path.isfile(log):
        log = os.path.join(d, "log.solve")           # fallback launcher name
    if not os.path.isfile(log):
        return fails + ["no log.simpleFoam / log.solve"], notes
    body = open(log, errors="replace").read()

    n_end = len(re.findall(r"^End\s*$", body, re.M))
    n_fatal = len(re.findall(r"FOAM FATAL", body))

    cd = _controldict(root, case)
    et = control_num(cd, "endTime") if endtime is None else float(endtime)
    dt = control_num(cd, "deltaT")
    times = [float(t) for t in numeric_times(d)]
    nonzero = [t for t in times if t > 0]
    last = nonzero[-1] if nonzero else None

    # --- CONJUNCT 1: rc ---------------------------------------------------
    if rc_policy == "read":
        rc_source = "READ-FROM-STATUS"
        if not re.fullmatch(r"-?\d+", st.get("rc", "")):
            fails.append("STATUS carries no integer rc key; rc_policy=read needs one")
        elif int(st["rc"]) != 0:
            fails.append("CRASH/CAP: STATUS rc=%s -- a crash is a FINDING until "
                         "triage says otherwise" % st["rc"])
    else:  # derive (mark_done_t23.py logic)
        if re.fullmatch(r"-?\d+", st.get("rc", "")):
            rc_source = "READ-FROM-STATUS"
            if int(st["rc"]) != 0:
                fails.append("CRASH/CAP: STATUS rc=%s" % st["rc"])
        else:
            rc_source = "DERIVED-FROM-LOG"
            why = ("STATUS carries launcher_rc=%s, the exit status of the LAUNCH "
                   "ARGV and NOT the solver rc; it is NOT accepted as rc"
                   % st["launcher_rc"]) if "launcher_rc" in st else \
                  "STATUS carries no rc key at all"
            notes.append("CONJUNCT 1 (rc=0) UNEVALUABLE FROM STATUS: " + why)
            notes.append("CONJUNCT 1 DERIVED from log: End=%d (want 1), FOAM "
                         "FATAL=%d (want 0), last=%s (want %g)"
                         % (n_end, n_fatal, "none" if last is None else "%g" % last, et))
            if n_end != 1 or n_fatal != 0 or last is None or abs(last - et) > 1e-9:
                fails.append("rc CANNOT BE DERIVED as 0: End=%d, FOAM FATAL=%d, "
                             "last=%s vs endTime %g"
                             % (n_end, n_fatal,
                                "none" if last is None else "%g" % last, et))

    # --- CONJUNCT 2: exactly one End line, zero FOAM FATAL ----------------
    if n_end != 1:
        fails.append("log carries %d End lines, expected exactly 1" % n_end)
    if n_fatal:
        fails.append("log carries %d FOAM FATAL occurrences" % n_fatal)

    # --- CONJUNCT 3: last written time == endTime -------------------------
    if last is None:
        return fails + ["no time directory beyond 0 -- the solver wrote no fields"], notes
    if abs(last - et) > 1e-9:
        fails.append("last written time %g != endTime %g" % (last, et))

    # --- CONJUNCT 4: registered fields present at endTime -----------------
    tdir = os.path.join(d, "%g" % last)
    present = {f: field_path(tdir, f) for f in NEEDED}
    miss = [f for f in NEEDED if present[f] is None]
    if miss:
        return fails + ["time %g is missing %s" % (last, ",".join(miss))], notes

    # --- CONJUNCT 5: clause-5 FIXED-deltaT: ExecutionTime == round(et/dt) --
    n_exec = len(re.findall(r"^ExecutionTime", body, re.M))
    want = int(round(et / dt))
    if n_exec != want:
        fails.append("%d ExecutionTime lines, expected %d (endTime %g / deltaT %g)"
                     % (n_exec, want, et, dt))

    # --- CONJUNCT 6: THE AGE GUARD, against 0/U ---------------------------
    ref = os.path.join(d, *AGE_REF)
    if not os.path.isfile(ref):
        fails.append("no %s, so the run cannot be dated and the age guard cannot "
                     "be evaluated" % os.path.join(*AGE_REF))
    else:
        age = os.path.getmtime(ref)
        stale = [f for f in NEEDED if os.path.getmtime(present[f]) < age]
        if stale:
            fails.append("time %g holds fields OLDER than %s (%s) -- not written "
                         "by this run (D438, L-143)"
                         % (last, os.path.join(*AGE_REF), ",".join(stale)))

    notes.append("rc_source=%s" % rc_source)
    return fails, notes


def run_case(root, case, endtime=None, rc_policy="derive"):
    fails, notes = check(root, case, endtime=endtime, rc_policy=rc_policy)
    for n in notes:
        print("NOTE      %-14s - %s" % (case, n))
    if fails:
        print("NOT DONE  %-14s - %s" % (case, "; ".join(fails)))
        return EXIT_NOTDONE
    m = os.path.join(root, "DONE.%s" % case)
    if not os.path.exists(m):
        open(m, "w").write("strict completion rule met (fixed-deltaT clause-5)\n")
    print("DONE      %-14s" % case)
    return EXIT_OK


# ==========================================================================
# --selftest -- planted controls: each clause fires on a defect, quiet on clean.
# ==========================================================================
def _forge(root, case, end=1, fatal=0, n_exec=None, last="3000", field=True,
           stale=False, status=True, rc=None, launcher_rc="0", infra=False,
           et=3000.0, dt=1.0):
    import time as _time
    d = os.path.join(root, case)
    os.makedirs(os.path.join(d, "system"), exist_ok=True)
    open(os.path.join(d, "system", "controlDict"), "w").write(
        "application simpleFoam;\nendTime %g;\ndeltaT %g;\n" % (et, dt))
    z = os.path.join(d, "0")
    os.makedirs(z, exist_ok=True)
    # 0/U is touched LAST at launch (as run_prd.sh will do); date the run by it.
    open(os.path.join(z, "U"), "w").write("0/U\n")
    t0 = os.path.getmtime(os.path.join(z, *AGE_REF[1:]))
    n = int(round(et / dt)) if n_exec is None else n_exec
    open(os.path.join(d, "log.simpleFoam"), "w").write(
        "ExecutionTime = 1 s\n" * n
        + "--> FOAM FATAL ERROR: forged\n" * fatal
        + "End\n" * end)
    tdir = os.path.join(d, last)
    if field:
        os.makedirs(tdir, exist_ok=True)
        for nm in NEEDED:
            q = os.path.join(tdir, nm)
            open(q, "w").write("y")
            os.utime(q, (t0 - 100, t0 - 100) if stale else (t0 + 5, t0 + 5))
    else:
        os.makedirs(tdir, exist_ok=True)
    if status:
        s = ""
        if rc is not None:
            s += "case=%s rc=%s\n" % (case, rc)
        if launcher_rc is not None:
            s += ("launcher_rc=%s end=2026-09-09T00:00:00Z "
                  "note=exit-status-of-the-launch-argv-NOT-the-solver-rc\n" % launcher_rc)
        if infra:
            s += ("wall_s=120 ranks=16 core_min=32.0 cap_core_min=100.0 "
                  "timeout_s=600 capped=0 solver=simpleFoam\n")
        open(os.path.join(d, "STATUS.%s" % case), "w").write(s)


def selftest():
    import tempfile
    import shutil
    import ast
    import io
    import contextlib
    print("mark_done_prd.py --selftest (planted controls; NO solver)")
    CASE = "PRD_E1_L1_U100"
    fails = []

    def drive(label, want_rc, want_marker, want_derived=None, rc_policy="derive", **kw):
        tmp = tempfile.mkdtemp(prefix="prd_md_")
        try:
            _forge(tmp, CASE, **kw)
            buf = io.StringIO()
            code = None
            try:
                with contextlib.redirect_stdout(buf):
                    code = run_case(tmp, CASE, rc_policy=rc_policy)
            except SystemExit as e:
                code = e.code
            out = buf.getvalue()
            marker = os.path.exists(os.path.join(tmp, "DONE.%s" % CASE))
            ok = (code == want_rc and marker == want_marker)
            if want_derived is not None:
                ok = ok and (("DERIVED-FROM-LOG" in out) == want_derived)
            print("  [%s] %-62s -> exit %s, DONE %s"
                  % ("ok " if ok else "FAIL", label, code, marker))
            if not ok:
                fails.append(label)
                print(out)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    # CLEAN control FIRST (a clause never shown able to stay quiet flags all).
    drive("CLEAN clobbered-STATUS case -> DONE, rc DERIVED", EXIT_OK, True,
          want_derived=True)
    # per-clause planted defects
    drive("clause1: FOAM FATAL -> rc NOT derivable -> NOT DONE", EXIT_NOTDONE, False,
          want_derived=True, fatal=1)
    drive("clause2: no End line -> NOT DONE", EXIT_NOTDONE, False, want_derived=True, end=0)
    drive("clause2: two End lines -> NOT DONE", EXIT_NOTDONE, False, want_derived=True, end=2)
    drive("clause3: last time 2000 != 3000 -> NOT DONE", EXIT_NOTDONE, False,
          want_derived=True, last="2000")
    drive("clause4: a registered field missing -> NOT DONE", EXIT_NOTDONE, False,
          field=False)
    drive("clause5: ExecutionTime 2999 != 3000 -> NOT DONE", EXIT_NOTDONE, False,
          want_derived=True, n_exec=2999)
    drive("clause6: fields OLDER than 0/U (age guard) -> NOT DONE", EXIT_NOTDONE,
          False, want_derived=True, stale=True)
    # rc-policy READ path, both directions; launcher_rc is NEVER rc
    drive("rc_policy=read, STATUS rc=0 -> DONE (rc READ)", EXIT_OK, True,
          want_derived=False, rc_policy="read", rc="0", launcher_rc=None, infra=True)
    drive("rc_policy=read, STATUS rc=1 -> NOT DONE (CRASH)", EXIT_NOTDONE, False,
          rc_policy="read", rc="1", launcher_rc=None, infra=True)
    drive("launcher_rc=1 with clean log -> DONE (launcher_rc is NOT rc)", EXIT_OK,
          True, want_derived=True, launcher_rc="1")

    # A field-set control: dropping ONE field (phi) must fail -> the set matters.
    tmp = tempfile.mkdtemp(prefix="prd_md_")
    try:
        _forge(tmp, CASE)
        os.remove(os.path.join(tmp, CASE, "3000", "phi"))
        code = run_case(tmp, CASE)
        ok = (code == EXIT_NOTDONE)
        print("  [%s] field-set control: 3000/phi removed -> NOT DONE"
              % ("ok " if ok else "FAIL"))
        if not ok:
            fails.append("field-set")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # absent STATUS -> REFUSE (never inferred from End; K0d L1)
    tmp = tempfile.mkdtemp(prefix="prd_md_")
    try:
        _forge(tmp, CASE, status=False)
        buf = io.StringIO()
        code = None
        try:
            with contextlib.redirect_stdout(buf):
                code = run_case(tmp, CASE)
        except SystemExit as e:
            code = e.code
        ok = (code == EXIT_REFUSE and "no STATUS" in buf.getvalue())
        print("  [%s] absent STATUS -> REFUSE (exit 2), never inferred"
              % ("ok " if ok else "FAIL"))
        if not ok:
            fails.append("absent-status-refusal")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # launch guard (clause 7), both directions
    tmp = tempfile.mkdtemp(prefix="prd_md_")
    try:
        gd = os.path.join(tmp, "g", "system")
        os.makedirs(gd, exist_ok=True)
        ok = not launch_guard(tmp, "g")
        print("  [%s] clause 7 quiet: no 0, no time dir" % ("ok " if ok else "FAIL"))
        if not ok:
            fails.append("guard-quiet")
        os.makedirs(os.path.join(tmp, "g", "0"), exist_ok=True)
        ok = bool(launch_guard(tmp, "g"))
        print("  [%s] clause 7 FIRES: 0/ already exists" % ("ok " if ok else "FAIL"))
        if not ok:
            fails.append("guard-fires-0")
        os.makedirs(os.path.join(tmp, "g", "40"), exist_ok=True)
        ok = any("numeric time" in r for r in launch_guard(tmp, "g"))
        print("  [%s] clause 7 FIRES: a numeric time dir exists" % ("ok " if ok else "FAIL"))
        if not ok:
            fails.append("guard-fires-time")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # no module-level assert (L-332)
    src = open(os.path.abspath(__file__)).read()
    n0 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src)))
    n1 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src + "\nassert 1\n")))
    ok = (n0 == 0 and n1 == 1)
    print("  [%s] AST assert count = %d (planted control: %d)"
          % ("ok " if ok else "FAIL", n0, n1))
    if not ok:
        fails.append("ast")

    print("\nSELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    for f in fails:
        print("   - " + f)
    return EXIT_OK if not fails else EXIT_NOTDONE


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=None)
    ap.add_argument("--case", default=None)
    ap.add_argument("--endtime", type=float, default=None)
    ap.add_argument("--rc-policy", choices=("derive", "read"), default="derive")
    ap.add_argument("--launch-guard", metavar="CASE", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)

    if a.selftest:
        return selftest()
    if a.root is None:
        refuse("--root is required (this script does not guess the run directory)")
    root = os.path.abspath(a.root)
    if not os.path.isdir(root):
        refuse("no such run directory: %s" % root)
    if a.launch_guard:
        bad = launch_guard(root, a.launch_guard)
        if bad:
            print("LAUNCH REFUSED for %s (clause 7):" % a.launch_guard)
            for r in bad:
                print("   - " + r)
            return EXIT_REFUSE
        print("launch guard clear for %s" % a.launch_guard)
        return EXIT_OK
    if not a.case:
        refuse("--case is required when no --launch-guard/--selftest is given")
    return run_case(root, a.case, endtime=a.endtime, rc_policy=a.rc_policy)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
