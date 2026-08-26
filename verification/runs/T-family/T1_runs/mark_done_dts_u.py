#!/usr/bin/env python3
"""Turn the T1c-U `STATUS_u.<case>` files into DONE markers under the STRICT
COMPLETION RULE (CLAUDE.md rule 4), all-or-nothing:

  1. STATUS_u.<case> EXISTS in the run root and carries the SOLVER's own rc,
     written INSIDE the launcher wrapper (run_one_dts_u.sh), and rc == 0
  2. log.solve carries an `End` line
  3. the last written time == endTime from the case's own controlDict
  4. the registered fields T U p_rgh alphat phi are present at that time
  5. ExecutionTime line count == endTime (deltaT 1, the parent chain's)
  6. THE AGE GUARD: every needed field at endTime NEWER than the case's own 0/T
  7. AT LEAST TWO written time directories beyond 0 -- the campaign's registered
     convergence criterion is the LAST-TWO-CHECKPOINT field change
     (analyse_t1c.iterative_convergence), and a run with one checkpoint cannot
     be tested against it at all.  This clause is PHYSICS-CRITICAL for the same
     reason T1c's own docstring gives: a non-converged case once impersonated a
     discretisation failure behind "a merely unremarkable 4e-05" residual, and
     comparing the written fields is the direct test.

L-342 FIELD CLASSES.  PHYSICS-CRITICAL: rc, End, last time, fields present,
ExecutionTime count, the age guard, the two checkpoints.  INFRASTRUCTURE:
wall_s, timeout_s, ranks, core_min, capped, checkmesh_rc, solver, solver_path,
note, started_utc, ended_utc -- an ABSENT infrastructure field is NOT MEASURED
and is REPORTED; it never voids a run.  `capped` labels a non-zero rc; it is
never a completion conjunct.

THE STATUS NAMESPACE IS SEPARATE ON PURPOSE.  The older T1 arms wrote
`STATUS.<case>` in a one-line `rc= wall= checkMesh_rc=` format from
run_one_dts.sh; those files and that launcher are NOT touched, NOT edited and
NOT read here.  This arm writes and reads `STATUS_u.<case>` only.

AN ABSENT STATUS FILE IS A REFUSAL (exit 2), NEVER AN INFERENCE FROM AN End
LINE (K0d L1).  NO `assert` (L-332).  --selftest forges cases in scratch and
drives every clause under python3 and python3 -O.

Usage: python3 mark_done_dts_u.py [CASE ...] [--root DIR] | --selftest
Exit: 0 all DONE, 1 at least one NOT DONE, 2 REFUSAL.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = ("D_Ts_Re25_U_c", "D_Ts_Re25_U_m", "D_Ts_Re25_U_f",
         "L_Ts_U_c", "L_Ts_U_m", "L_Ts_U_f")
NEEDED = ("T", "U", "p_rgh", "alphat", "phi")
INFRA = ("wall_s", "timeout_s", "ranks", "core_min", "capped", "checkmesh_rc",
         "solver", "solver_path", "note", "started_utc", "ended_utc")
EXIT_OK, EXIT_NOTDONE, EXIT_REFUSE = 0, 1, 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def dict_num(root, case, key):
    p = os.path.join(root, case, "system", "controlDict")
    if not os.path.isfile(p):
        refuse("no system/controlDict for %s -- a completion rule that guesses its own target is not a rule" % case)
    m = re.search(r"^\s*%s\s+([0-9.eE+-]+)\s*;" % key, open(p).read(), re.M)
    if not m:
        refuse("controlDict for %s states no %s" % (case, key))
    return float(m.group(1))


def read_status(root, case):
    p = os.path.join(root, "STATUS_u.%s" % case)
    if not os.path.isfile(p):
        refuse("no STATUS_u.%s -- the solver's exit status was never recorded. An absent STATUS is not "
               "inferred from an End line (K0d L1); it is refused." % case)
    txt = open(p).read()
    d = dict(re.findall(r"^([a-z_]+)=(.*)$", txt, re.M))
    if not re.fullmatch(r"-?\d+", d.get("rc", "")):
        refuse("STATUS_u.%s carries no integer rc: %r" % (case, txt.strip()))
    return d


def check(root, case):
    d = os.path.join(root, case)
    fails, notes = [], []
    if not os.path.isdir(d):
        return ["no case directory"], notes
    st = read_status(root, case)
    missing = [k for k in INFRA if k not in st]
    if missing:
        notes.append("INFRASTRUCTURE fields NOT MEASURED (L-342, reported, not refused): " + ",".join(missing))
    rc = int(st["rc"])
    if rc != 0:
        if st.get("capped") == "yes":
            fails.append("CAPPED: rc=%s at wall_s=%s against timeout_s=%s -- the run reached its registered "
                         "cap and was stopped; an overrun does not get a new budget (rule 12)"
                         % (rc, st.get("wall_s"), st.get("timeout_s")))
        else:
            fails.append("CRASH: rc=%s (capped=%s) -- a crash is a FINDING until triage says otherwise"
                         % (rc, st.get("capped", "NOT MEASURED")))
    log = os.path.join(d, "log.solve")
    if not os.path.isfile(log):
        return fails + ["no log.solve"], notes
    body = open(log, errors="replace").read()
    if not re.search(r"^End\s*$", body, re.M):
        fails.append("log.solve has no End line")
    et = dict_num(root, case, "endTime")
    times = sorted((float(x) for x in os.listdir(d) if re.fullmatch(r"[0-9]+(\.[0-9]+)?", x)))
    nonzero = [t for t in times if t > 0]
    if not nonzero:
        return fails + ["no time directory beyond 0 -- the solver wrote no fields"], notes
    if len(nonzero) < 2:
        fails.append("only %d written checkpoint beyond 0 -- the registered convergence criterion is the "
                     "LAST-TWO-CHECKPOINT field change and cannot be evaluated at all" % len(nonzero))
    last = nonzero[-1]
    if abs(last - et) > 1e-9:
        fails.append("last written time %g != endTime %g" % (last, et))
    tdir = os.path.join(d, "%g" % last)
    miss = [f for f in NEEDED if not os.path.isfile(os.path.join(tdir, f))]
    if miss:
        return fails + ["time %g is missing %s" % (last, ",".join(miss))], notes
    n_exec = len(re.findall(r"^ExecutionTime", body, re.M))
    if n_exec != int(round(et)):
        fails.append("%d ExecutionTime lines, expected %d (endTime %g, deltaT 1)" % (n_exec, int(round(et)), et))
    ref = os.path.join(d, "0", "T")
    if not os.path.isfile(ref):
        fails.append("no 0/T, so the run cannot be dated and the age guard cannot be evaluated")
    else:
        age = os.path.getmtime(ref)
        stale = [f for f in NEEDED if os.path.getmtime(os.path.join(tdir, f)) < age]
        if stale:
            fails.append("time %g holds fields OLDER than 0/T (%s) -- not written by this run"
                         % (last, ",".join(stale)))
    return fails, notes


def run(root, want):
    rc = EXIT_OK
    for case in want:
        if case not in CASES:
            refuse("%r is not a registered T1c-U case: %s" % (case, " ".join(CASES)))
        fails, notes = check(root, case)
        for n in notes:
            print("NOTE      %-16s - %s" % (case, n))
        if fails:
            rc = EXIT_NOTDONE
            print("NOT DONE  %-16s - %s" % (case, "; ".join(fails)))
        else:
            m = os.path.join(root, "DONE_u.%s" % case)
            if not os.path.exists(m):
                open(m, "w").write("done\n")
            print("DONE      %-16s" % case)
    return rc


def _forge(root, case, rc="0", end=True, n_exec=None, last="40000", fields=True, stale=False,
           status=True, infra=True, et=40000.0, checkpoints=2, drop="",):
    d = os.path.join(root, case)
    os.makedirs(os.path.join(d, "system"), exist_ok=True)
    os.makedirs(os.path.join(d, "0"), exist_ok=True)
    open(os.path.join(d, "system", "controlDict"), "w").write("endTime %g;\ndeltaT 1;\n" % et)
    open(os.path.join(d, "0", "T"), "w").write("x")
    t0 = os.path.getmtime(os.path.join(d, "0", "T"))
    n = int(round(et)) if n_exec is None else n_exec
    open(os.path.join(d, "log.solve"), "w").write("ExecutionTime = 1 s\n" * n + ("End\n" if end else ""))
    tds = [last] if checkpoints < 2 else ["%g" % (float(last) - 2000), last]
    for td in tds:
        os.makedirs(os.path.join(d, td), exist_ok=True)
        if fields:
            for f in NEEDED:
                if drop and f == drop and td == last:
                    continue
                p = os.path.join(d, td, f)
                open(p, "w").write("y")
                os.utime(p, (t0 - 100, t0 - 100) if stale else (t0 + 5, t0 + 5))
    if status:
        s = "case=%s\nrc=%s\n" % (case, rc)
        if infra:
            s += ("wall_s=550\nranks=1\ncore_min=9.173\ntimeout_s=1200\ncapped=%s\ncheckmesh_rc=0\n"
                  "solver=buoyantBoussinesqSimpleFoam\nsolver_path=/x\nnote=clean\nstarted_utc=t\nended_utc=t\n"
                  % ("yes" if rc == "124" else "no"))
        open(os.path.join(root, "STATUS_u.%s" % case), "w").write(s)


def selftest():
    import ast
    import shutil
    import tempfile
    fails = []
    C = "D_Ts_Re25_U_c"

    def drive(label, want_rc, want_marker, **kw):
        tmp = tempfile.mkdtemp(prefix="dtsumd_")
        try:
            _forge(tmp, C, **kw)
            code = None
            try:
                code = run(tmp, [C])
            except SystemExit as e:
                code = e.code
            marker = os.path.exists(os.path.join(tmp, "DONE_u.%s" % C))
            ok = (code == want_rc and marker == want_marker)
            print("  [%s] %-66s -> exit %s, DONE marker %s" % ("ok " if ok else "FAIL", label, code, marker))
            if not ok:
                fails.append(label)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    drive("pristine forged case -> DONE", EXIT_OK, True)
    drive("STATUS_u absent -> REFUSE (never inferred from End)", EXIT_REFUSE, False, status=False)
    drive("rc=1 below cap -> NOT DONE (CRASH)", EXIT_NOTDONE, False, rc="1")
    drive("rc=124 capped=yes -> NOT DONE (CAPPED, no new budget)", EXIT_NOTDONE, False, rc="124")
    drive("no End line -> NOT DONE", EXIT_NOTDONE, False, end=False)
    drive("last time 38000 != endTime 40000 -> NOT DONE", EXIT_NOTDONE, False, last="38000")
    drive("phi missing at endTime -> NOT DONE", EXIT_NOTDONE, False, drop="phi")
    drive("ExecutionTime count 39999 != 40000 -> NOT DONE", EXIT_NOTDONE, False, n_exec=39999)
    drive("fields at endTime OLDER than 0/T -> NOT DONE (age guard)", EXIT_NOTDONE, False, stale=True)
    drive("ONE checkpoint only -> NOT DONE (last-two-checkpoint criterion unevaluable)",
          EXIT_NOTDONE, False, checkpoints=1)
    drive("all INFRASTRUCTURE fields absent -> DONE with NOTE (L-342)", EXIT_OK, True, infra=False)
    # a case name outside the registered six is refused
    fired = False
    tmp = tempfile.mkdtemp(prefix="dtsumd2_")
    try:
        run(tmp, ["L_Ts_c"])
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("  [%s] a PARENT case name (L_Ts_c) -> REFUSE: this instrument grades only the six U cases"
          % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("scope")
    src = open(__file__).read()
    n0 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src)))
    n1 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src + "\nassert 1\n")))
    ok = (n0 == 0 and n1 == 1)
    print("  [%s] AST assert count = %d (planted control: %d)" % ("ok " if ok else "FAIL", n0, n1))
    if not ok:
        fails.append("ast")
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    root = HERE
    if "--root" in argv:
        root = argv[argv.index("--root") + 1]
        argv = [a for i, a in enumerate(argv) if a != "--root" and argv[max(i - 1, 0)] != "--root"]
    want = [a for a in argv if not a.startswith("-")] or list(CASES)
    return run(root, want)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
