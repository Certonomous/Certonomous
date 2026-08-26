#!/usr/bin/env python3
"""Turn T4b STATUS files into DONE markers under the STRICT COMPLETION RULE,
with L-342's field classes applied from the start.

PHYSICS-CRITICAL (each a conjunct; any failure -> NOT DONE, no marker):
  1. STATUS.<case> EXISTS and carries the solver's own rc, written INSIDE the
     launch wrapper (launch_t4b.sh runs the solver in its foreground under
     `timeout` and writes rc=$? -- an in-wrapper rc is not a poller); rc == 0
  2. log.solve carries an `End` line
  3. the last written time == endTime from the case's own system/controlDict
  4. every registered field is present at that time
     (T U p_rgh alphat nut k omega, plus phi which control C3 reads)
  5. the ExecutionTime line count == endTime
  6. THE AGE GUARD: every field at endTime is NEWER than the case's own 0/T
     (0/T is touched LAST at launch; L-143, D438)

INFRASTRUCTURE (L-342, Sanaa's rule d4d0c29d: "a bookkeeping failure
invalidates the bookkeeping, never the physics artifacts"): wall_s, timeout_s,
ranks, core_min, capped, checkmesh_rc, started/ended_utc, solver_path, note.
An absent or malformed infrastructure field is reported NOT MEASURED and the
grade PROCEEDS.  In particular `capped` is NOT a conjunct: the T11/T4 form that
returned NOT DONE on a missing `capped` witness was audited CONFLATING
(docs/campaigns/T-family/L342_FIELD_CLASS_AUDIT_2026-08-26.md, row 30) and is
not repeated here.  `capped` is still READ when present, because it is the
witness that separates a cap-stop (rc 124 at wall_s >= timeout_s: rule 12, the
run stops and is NOT A RESULT) from a crash (a finding needing triage) -- but it
only ever LABELS a non-zero rc, it never voids an rc=0 run.

REFUSAL, NOT INFERENCE.  An ABSENT STATUS file is a REFUSAL (exit 2), never a
pass and never a NOT DONE that a reader could mistake for a graded outcome: the
consumer side of the K0d L1 defect, where a launcher wrote no rc and the right
answer was to refuse rather than infer rc=0 from an End line.

NO `assert` STATEMENT IN THIS FILE (L-332).  --selftest forges cases in a
scratch root and DRIVES every clause and the STATUS refusal, under python3 and
python3 -O alike (the mark_done_t3_rff.py pattern); --root DIR points the
reader at another tree (selftest use).

Usage:  python3 mark_done_t4b.py [CASE ...] [--root DIR] | --selftest

Exit codes:  0 all requested cases DONE
             1 at least one NOT DONE (a reportable outcome on physics fields)
             2 REFUSAL -- STATUS absent, or a structural precondition failed
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = HERE
CASES = ("T4b_IJ_c", "T4b_IJ_m", "T4b_IJ_f")
NEEDED = ("T", "U", "p_rgh", "alphat", "nut", "k", "omega", "phi")
INFRA = ("wall_s", "timeout_s", "ranks", "core_min", "capped", "checkmesh_rc",
         "started_utc", "ended_utc", "solver_path", "note")
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


def read_status(case):
    """The physics-critical field is rc; everything else is infrastructure."""
    p = os.path.join(ROOT, "STATUS.%s" % case)
    if not os.path.isfile(p):
        refuse("no STATUS.%s -- the solver's exit status was never recorded. An "
               "absent STATUS is not inferred from an End line (K0d L1); it is "
               "refused." % case)
    txt = open(p).read()
    d = dict(re.findall(r"^([A-Za-z_]+)=(.*)$", txt, re.M))
    if "rc" not in d or not re.fullmatch(r"-?\d+", d["rc"].strip()):
        refuse("STATUS.%s carries no integer rc: %r" % (case, txt.strip()))
    not_measured = [k for k in INFRA if k not in d]
    return d, not_measured


def check(case):
    """Return (list of physics failures, list of infrastructure NOT MEASURED)."""
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
        return fails + ["no log.solve"], nm
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
        return fails + ["no time directory beyond 0 -- the solver wrote no fields"], nm
    last = nonzero[-1]
    if abs(last - et) > 1e-9:
        fails.append("last written time %g != endTime %g" % (last, et))
    tdir = os.path.join(d, "%g" % last)
    miss = [f for f in NEEDED if not os.path.isfile(os.path.join(tdir, f))]
    if miss:
        return fails + ["time %g is missing %s" % (last, ",".join(miss))], nm
    if n_exec != int(et):
        fails.append("%d ExecutionTime lines, expected %d" % (n_exec, int(et)))
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


def _forge(root, case, rc="0", end=40, n_exec=None, with_end=True, stale=False,
           status=True, infra=True, missing_field=None):
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
    open(os.path.join(d, "log.solve"), "w").write("ExecutionTime = 1 s\n" * n + ("End\n" if with_end else ""))
    if status:
        lines = ["case=%s" % case, "rc=%s" % rc]
        if infra:
            lines += ["wall_s=10", "ranks=1", "core_min=0.167", "timeout_s=600", "capped=no",
                      "checkmesh_rc=0", "started_utc=x", "ended_utc=y", "solver_path=/x", "note=clean"]
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
        tmp = tempfile.mkdtemp(prefix="md_selftest_")
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

    print("mark_done selftest (planted controls; each clause drives the rule):")
    expect("clean forged case -> DONE, marker written", 0, True)
    expect("rc=1, capped=no -> NOT DONE (CRASH label)", 1, False, rc="1")
    expect("no End line -> NOT DONE", 1, False, with_end=False)
    expect("ExecutionTime count short -> NOT DONE", 1, False, n_exec=39)
    expect("a registered field missing at endTime -> NOT DONE", 1, False, missing_field=NEEDED[0])
    expect("fields OLDER than 0/T (age guard) -> NOT DONE", 1, False, stale=True)
    expect("absent STATUS -> REFUSE exit 2, no marker", 2, False, status=False)
    expect("every infrastructure field absent (incl. capped) -> still DONE, NOT MEASURED disclosed", 0, True, infra=False)
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
            refuse("%r is not one of the registered %s cases: %s" % (c, "T4b", " ".join(CASES)))
    rc = EXIT_OK
    for case in want:
        fails, nm = check(case)
        infra = ("  [infrastructure NOT MEASURED: %s -- disclosed, grade proceeds]" % ",".join(nm)) if nm else ""
        if fails:
            rc = EXIT_NOTDONE
            print("NOT DONE  %-10s - %s%s" % (case, "; ".join(fails), infra))
        else:
            marker = os.path.join(ROOT, "DONE.%s" % case)
            if not os.path.exists(marker):
                open(marker, "w").write("strict rule met (physics-critical clauses 1-6)%s\n" % infra)
            print("DONE      %-10s%s" % (case, infra))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
