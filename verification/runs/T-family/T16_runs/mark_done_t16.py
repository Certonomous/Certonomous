#!/usr/bin/env python3
"""Turn T16 STATUS files into DONE markers under the STRICT COMPLETION RULE,
with L-342's field classes applied from the start (the mark_done_t4b.py form).

FIELD CLASSES, DECLARED EXPLICITLY (L-342; the prose form of
`T3_runs/mark_done_t3_rff.py:8-18`, which `docs/L342_GRADER_AUDIT.md` names as
the model, copied rather than reinvented).  BOTH halves are driven by
`--selftest`; a class declaration no test exercises is a comment.

  PHYSICS-CRITICAL -- each a conjunct; any failure is NOT DONE and no marker is
  written.  L-342 relaxes NOTHING here; it only stops a dead poller voiding a
  good run.
    P1. the solver's rc VALUE is 0
    P2. log.solve carries an `End` line
    P3. the last written time == endTime from the case's own system/controlDict
    P4. every registered field is present at that time: T U p_rgh phi
    P5. THE AGE GUARD -- every field at endTime is NEWER than the case's own
        0/T (0/T is touched LAST at launch; L-143, D438)

  INFRASTRUCTURE -- reported; an absent or malformed value is stated NOT
  MEASURED, disclosed in the marker, and NEVER a refusal and never a conjunct
  (Sanaa's universal rule d4d0c29d, "a bookkeeping failure invalidates the
  bookkeeping, never the physics artifacts"):
    the **ExecutionTime line count**, wall_s, timeout_s, ranks, core_min,
    capped, checkmesh_rc, solver, solver_path, note, started_utc, ended_utc,
    ledger rows, pids, and the presence of log.launch / log.checkMesh.

  **THE `ExecutionTime` COUNT IS INFRASTRUCTURE, NOT PHYSICS.**  This is the
  exact misclassification `docs/L342_GRADER_AUDIT.md` found in
  `T14_runs/mark_done_t14.py:14-16` (refusing at `:107`) and in 27 other
  heat-transfer comparators, and the audit's point is that declaring the
  classes and then putting `ExecutionTime` on the physics side is WORSE than
  not declaring them, because it reassures a reader the split was done.  A
  short or absent count here is printed as NOT MEASURED beside a DONE.  It is
  a line-counting artefact of a print statement -- a solver that reached
  `End` at `endTime` with every field written and newer than `0/T` produced
  the physics whatever its log printing did (VMFLGPU001 AMENDMENT 4:
  petsc4Foam prints endTime + 2 lines and that is not a physics failure).

  `capped` is NOT a conjunct either (the T11/T4 form that returned NOT DONE on
  a missing `capped` witness was audited CONFLATING,
  `L342_FIELD_CLASS_AUDIT_2026-08-26.md`); it is still READ when present,
  because it separates a cap-stop (rule 12: the run stops, NOT A RESULT) from a
  crash (a finding needing triage) -- but it only LABELS a non-zero rc, never
  voids rc = 0.

RULING R-RC (verification, relayed 2026-08-27): **the `rc` VALUE is physics;
the `rc` RECORD is infrastructure.**  An absent STATUS file is therefore NOT an
automatic refusal any more.  It is NOT MEASURED, and only if ALL FOUR remaining
physics conditions P2-P5 hold is the case DONE -- and then `rc = 0` is printed
**as an inference and labelled as one**, never as a reading.  A `FOAM FATAL`
error, a `FOAM FATAL IO` error, a `Segmentation fault` or any signal token
anywhere in log.solve **still REFUSES**, absent record or not: the K0d L1
defect was inferring success from an End line past evidence of a crash, and
that inference is still forbidden.

NO `assert` STATEMENT IN THIS FILE (L-332).  --selftest forges cases in a
scratch root and DRIVES every clause, BOTH class halves, and the R-RC arms,
under python3 and python3 -O alike; --root DIR points the reader at another
tree (selftest use).

Usage:  python3 mark_done_t16.py [CASE ...] [--root DIR] | --selftest

Exit codes:  0 all requested cases DONE
             1 at least one NOT DONE (a reportable outcome on physics fields)
             2 REFUSAL -- a crash token in the log, or a structural
               precondition (no case directory, no controlDict) failed
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
CASES = ("T16_MC_c", "T16_MC_m", "T16_MC_f")
NEEDED = ("T", "U", "p_rgh", "phi")
INFRA = ("wall_s", "timeout_s", "ranks", "core_min", "capped", "checkmesh_rc",
         "solver", "solver_path", "note", "started_utc", "ended_utc")
EXIT_OK, EXIT_NOTDONE, EXIT_REFUSE = 0, 1, 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def control_end_time(case):
    p = os.path.join(ROOT, case, "system", "controlDict")
    if not os.path.isfile(p):
        refuse("no system/controlDict for %s -- endTime is unknowable" % case)
    m = re.search(r"^\s*endTime\s+([0-9.eE+-]+)\s*;", open(p).read(), re.M)
    if not m:
        refuse("controlDict for %s states no endTime" % case)
    return float(m.group(1))


CRASH_TOKENS = ("FOAM FATAL ERROR", "FOAM FATAL IO ERROR", "Segmentation fault",
                "Floating point exception", "Aborted", "signal ")


def crash_tokens_in_log(case):
    """R-RC's hard limit on inference: a crash token in log.solve REFUSES, absent
    rc record or not.  Streamed, never loaded whole."""
    p = os.path.join(ROOT, case, "log.solve")
    if not os.path.isfile(p):
        return []
    hits = []
    with open(p, errors="replace") as fh:
        for line in fh:
            for tok in CRASH_TOKENS:
                if tok in line:
                    hits.append(tok)
    return sorted(set(hits))


def read_status(case):
    """RULING R-RC: the rc VALUE is physics, the rc RECORD is infrastructure.
    Returns (dict-or-None, not_measured list).  A None dict means the record is
    NOT MEASURED; the caller then requires all four remaining physics conditions
    and prints rc = 0 as a LABELLED INFERENCE, never as a reading."""
    p = os.path.join(ROOT, "STATUS.%s" % case)
    if not os.path.isfile(p):
        return None, ["rc(record)"] + list(INFRA)
    txt = open(p).read()
    d = dict(re.findall(r"^([A-Za-z_]+)=(.*)$", txt, re.M))
    if "rc" not in d or not re.fullmatch(r"-?\d+", d["rc"].strip()):
        return None, ["rc(record, present but not an integer: %r)" % txt.strip()[:60]] + \
            [k for k in INFRA if k not in d]
    not_measured = [k for k in INFRA if k not in d]
    return d, not_measured


def check(case):
    """Return (list of physics failures, list of infrastructure NOT MEASURED)."""
    d = os.path.join(ROOT, case)
    if not os.path.isdir(d):
        refuse("no case directory %s" % d)
    st, nm = read_status(case)
    fails = []
    notes = []
    hits = crash_tokens_in_log(case)
    if hits:
        refuse("log.solve of %s carries crash token(s) %s -- R-RC forbids inferring "
               "success past evidence of a crash (K0d L1), with or without an rc record"
               % (case, ", ".join(repr(h) for h in hits)))
    if st is None:
        # R-RC: the RECORD is missing.  rc is NOT MEASURED.  The case can still be
        # DONE, but only on all four remaining physics conditions, and rc = 0 is
        # then an INFERENCE and is labelled one.
        notes.append("rc RECORD NOT MEASURED (no readable STATUS.%s); log.solve carries no "
                     "crash token; rc = 0 is INFERRED FROM THE REMAINING PHYSICS CONDITIONS "
                     "P2-P5 AND IS LABELLED AN INFERENCE, NOT A READING (ruling R-RC)" % case)
        st = {}
        rc = 0
    else:
        rc = int(st["rc"])
    if rc != 0:
        label = "CRASH (rc=%d)" % rc
        capped = st.get("capped")
        if capped == "yes":
            label = ("CAPPED (rc=%d, wall_s=%s >= timeout_s=%s): rule 12, the run "
                     "stopped at its registered cap and is NOT A RESULT, never "
                     "re-launched at a larger cap" % (rc, st.get("wall_s"), st.get("timeout_s")))
        elif capped == "no":
            label = ("CRASH (rc=%d at wall_s=%s below timeout_s=%s): a finding "
                     "until triage says otherwise" % (rc, st.get("wall_s"), st.get("timeout_s")))
        else:
            label += " -- capped witness NOT MEASURED, cap-stop vs crash undetermined"
        fails.append(label)

    log = os.path.join(d, "log.solve")
    if not os.path.isfile(log):
        return fails + ["no log.solve"], nm, notes
    n_end = 0
    n_exec = 0
    with open(log, errors="replace") as fh:          # streamed, never loaded whole
        for line in fh:
            if line.startswith("ExecutionTime"):
                n_exec += 1
            elif line.rstrip() == "End":
                n_end += 1
    if n_end == 0:
        fails.append("log.solve has no End line")
    et = control_end_time(case)
    times = sorted((float(x) for x in os.listdir(d)
                    if re.fullmatch(r"[0-9]+(\.[0-9]+)?", x)), key=float)
    nonzero = [t for t in times if t > 0]
    if not nonzero:
        return fails + ["no time directory beyond 0 -- the solver wrote no fields"], nm, notes
    last = nonzero[-1]
    if abs(last - et) > 1e-9:
        fails.append("last written time %g != endTime %g" % (last, et))
    tdir = os.path.join(d, "%g" % last)
    miss = [f for f in NEEDED if not os.path.isfile(os.path.join(tdir, f))]
    if miss:
        return fails + ["time %g is missing %s" % (last, ",".join(miss))], nm, notes
    # THE ExecutionTime COUNT IS INFRASTRUCTURE (L-342 audit, T14 misclassification).
    # It is READ, it is REPORTED, and it never enters `fails`.
    if n_exec != int(et):
        nm = nm + ["ExecutionTime count (%d lines, endTime %d -- a log-printing artefact, "
                   "NOT a physics conjunct)" % (n_exec, int(et))]
    ref = os.path.join(d, "0", "T")
    if not os.path.isfile(ref):
        fails.append("no 0/T, so the run cannot be dated and the age guard cannot be evaluated")
    else:
        age = os.path.getmtime(ref)
        stale = [f for f in NEEDED if os.path.getmtime(os.path.join(tdir, f)) < age]
        if stale:
            fails.append("time %g holds fields OLDER than 0/T (%s) -- not written by this run"
                         % (last, ",".join(stale)))
    return fails, nm, notes


def _forge(root, case, rc="0", end=40, n_exec=None, with_end=True, stale=False,
           status=True, infra=True, missing_field=None, capped="no", fatal=False):
    """A synthetic case shaped exactly like a finished run, in a scratch root."""
    import time
    d = os.path.join(root, case)
    for sub in ("0", "system"):
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    open(os.path.join(d, "system", "controlDict"), "w").write("endTime %d;\n" % end)
    open(os.path.join(d, "0", "T"), "w").write("x\n")
    t0 = time.time() - 100
    os.utime(os.path.join(d, "0", "T"), (t0, t0))
    td = os.path.join(d, str(end))
    os.makedirs(td, exist_ok=True)
    for f in NEEDED:
        if f == missing_field:
            continue
        p = os.path.join(td, f)
        open(p, "w").write("y\n")
        if stale:
            os.utime(p, (t0 - 100, t0 - 100))
    n = end if n_exec is None else n_exec
    body = "ExecutionTime = 1 s\n" * n
    if fatal:
        body += "--> FOAM FATAL ERROR: (openfoam-2606)\n"
    open(os.path.join(d, "log.solve"), "w").write(body + ("End\n" if with_end else ""))
    if status:
        lines = ["case=%s" % case, "rc=%s" % rc]
        if infra:
            lines += ["wall_s=10", "ranks=1", "core_min=0.167", "timeout_s=600", "capped=%s" % capped,
                      "checkmesh_rc=0", "solver=x", "solver_path=/x", "note=clean", "started_utc=x", "ended_utc=y"]
        open(os.path.join(root, "STATUS.%s" % case), "w").write("\n".join(lines) + "\n")


def selftest():
    """Planted controls: each clause is driven both ways; the STATUS refusal is
    driven; an absent infrastructure field is shown NOT to void the case."""
    import shutil
    import tempfile
    global ROOT
    fails = []
    case = CASES[0]

    def expect(name, want_code, want_marker, **kw):
        global ROOT
        tmp = tempfile.mkdtemp(prefix="md13_selftest_")
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

    print("mark_done_t16 selftest (planted controls; each clause drives the rule):")
    expect("clean forged case -> DONE, marker written", 0, True)
    expect("rc=1, capped=no -> NOT DONE (CRASH label)", 1, False, rc="1")
    expect("rc=124, capped=yes -> NOT DONE (CAPPED label, rule 12)", 1, False, rc="124", capped="yes")
    expect("no End line -> NOT DONE", 1, False, with_end=False)
    expect("a registered field missing at endTime -> NOT DONE (PHYSICS half P4)", 1, False,
           missing_field=NEEDED[3])
    expect("fields OLDER than 0/T (age guard) -> NOT DONE (PHYSICS half P5)", 1, False, stale=True)
    print("  -- the INFRASTRUCTURE half: each of these WOULD have refused before L-342 --")
    expect("ExecutionTime count SHORT (39 of 40) -> still DONE, NOT MEASURED disclosed "
           "(the T14 misclassification, not repeated here)", 0, True, n_exec=39)
    expect("ExecutionTime count LONG (42 of 40, the petsc4Foam shape) -> still DONE", 0, True, n_exec=42)
    expect("every infrastructure field absent (incl. capped) -> still DONE, NOT MEASURED disclosed",
           0, True, infra=False)
    print("  -- ruling R-RC: the rc VALUE is physics, the rc RECORD is infrastructure --")
    expect("absent STATUS record, P2-P5 all hold, clean log -> DONE with rc=0 LABELLED AN INFERENCE",
           0, True, status=False)
    expect("absent STATUS record AND a physics condition fails (no End) -> NOT DONE, no marker",
           1, False, status=False, with_end=False)
    expect("absent STATUS record AND `FOAM FATAL ERROR` in log.solve -> REFUSE exit 2 (R-RC's "
           "hard limit: no inference past evidence of a crash, K0d L1)", 2, False,
           status=False, fatal=True)
    expect("STATUS present with rc=0 but `FOAM FATAL ERROR` in log.solve -> REFUSE exit 2",
           2, False, fatal=True)
    # an unregistered case name is refused
    code = None
    try:
        code = main(["T16_MC_x"])
    except SystemExit as e:
        code = e.code
    ok = (code == 2)
    print("  [%s] unregistered case name -> REFUSE exit 2" % ("ok " if ok else "FAIL"))
    if not ok:
        fails.append("unregistered")
    import ast
    n_assert = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse(open(os.path.abspath(__file__)).read())))
    planted = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse("assert 1\n")))
    ok = (n_assert == 0 and planted == 1)
    print("  [%s] AST assert count in this file = %d (counter sees a planted assert: %d)" % ("ok " if ok else "FAIL", n_assert, planted))
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
            refuse("%r is not one of the registered T16 cases: %s" % (c, " ".join(CASES)))
    rc = EXIT_OK
    for case in want:
        fails, nm, notes = check(case)
        infra = ("  [infrastructure NOT MEASURED: %s -- disclosed, grade proceeds]" % ",".join(nm)) if nm else ""
        infer = ("  [INFERENCE, LABELLED: %s]" % "; ".join(notes)) if notes else ""
        if fails:
            rc = EXIT_NOTDONE
            print("NOT DONE  %-10s - %s%s%s" % (case, "; ".join(fails), infra, infer))
        else:
            marker = os.path.join(ROOT, "DONE.%s" % case)
            if not os.path.exists(marker):
                open(marker, "w").write(
                    "strict rule met on the PHYSICS-CRITICAL conjuncts P1-P5%s%s\n" % (infra, infer))
            print("DONE      %-10s%s%s" % (case, infra, infer))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
