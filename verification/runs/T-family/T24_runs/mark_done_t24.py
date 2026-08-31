#!/usr/bin/env python3
"""Turn the TWELVE T24 cases into DONE markers under the STRICT COMPLETION RULE
(CLAUDE.md rule 4), all-or-nothing.  Gates registered at
`docs/campaigns/T-family/T24_PREREGISTRATION.md` section 3.5 and section 3.5a,
FROZEN at b9057489.

THIS FILE IS FROZEN BEFORE THE TWELVE SOLVERS LAND.  It was written and
committed while all twelve were still running, so that the completion rule could
not have been shaped by a result it had already seen.  That ordering is the
whole evidentiary content of CLAUDE.md rule 2, and it is the reason this file
exists in the shape it does rather than a more convenient one.

WHICH MARKER PATTERN THIS IS, AND WHY.  This is
`verification/runs/T-family/T23_runs/mark_done_t23.py` in shape -- the marker of
the parent rung, which already solved exactly this problem on exactly this
geometry -- with the registered differences named below.  T23's marker was
itself T19's with the L-342 physics / infrastructure split, and that split is
the distinction the whole rc question turns on.

  INHERITED DIFFERENCE 1.  THE FIELD TUPLE IS PER-REGION (T24 3.5 conjunct 4):
    `T, p` in <endTime>/core and <endTime>/housing; `T U p p_rgh alphat nut k
    omega` in <endTime>/fluid.  The core and housing are SOLID regions and the
    fluid tuple does not apply to them; requiring it would make completion
    impossible for a reason that is a modelling fact, not a defect.
  INHERITED DIFFERENCE 2.  THE AGE-GUARD REFERENCE IS `0/housing/T`, not `0/T`
    (T24 3.5 conjunct 6).  A multi-region case has no `0/T`.  `run_t24.sh`
    touches `0/housing/T` LAST, on the line immediately before the START block,
    so that file dates the run that was allowed to produce the answer.
  INHERITED DIFFERENCE 3.  STATUS.<case> lives INSIDE the case directory.
  NEW DIFFERENCE 4.  TWELVE cases, and `rc` IS ALWAYS DERIVED.  SEE BELOW.
  NEW DIFFERENCE 5.  THE CAP IS A NAMED OUTCOME, NOT A SURPRISE.  SEE BELOW.

=== THE CLOBBERED STATUS, AND WHY rc IS DERIVED AND NEVER READ ===

T24 section 3.5a REGISTERED THIS UP FRONT, BEFORE COMPUTE, rather than
discovering it at grading time.  MEASURED, twice, across five cases: the queue
runner overwrites the launcher's `STATUS.<case>` after the launcher writes it,
leaving three keys -- `launcher_rc`, `end`, `note` -- and destroying `rc`,
`wall_s`, `ranks`, `core_min`, `cap_core_min`, `timeout_s`, `capped` and
`solver`.  It happened to `T22_CHTb_L1` and then to all four `T23_P305_U*`.
This file assumes it will happen again.

  * `launcher_rc` IS NOT rc AND IS NEVER ACCEPTED AS rc, EVEN AT 0.  It is the
    exit status of the argv the queue runner spawned, and a 0 there is exactly
    the shape of the `setsid` trap the launcher exists to avoid: `setsid timeout
    cmd` exits 0 for every outcome.  The STATUS file says so on its own face
    (`note=exit-status-of-the-launch-argv-NOT-the-solver-rc`).
  * SO CONJUNCT 1 (`rc = 0`) IS **UNEVALUABLE FROM STATUS** AND IS **DERIVED
    FROM THE LOG**, per T24 3.5a: exactly one `End` line, ZERO `FOAM FATAL`, and
    the last written time equal to endTime.  EVERY line this file prints names
    which conjuncts were UNEVALUABLE FROM STATUS and what they were evaluated
    from instead.  A conjunct silently treated as passing because its evidence
    was destroyed is the failure mode that paragraph exists to prevent.
  * THE DERIVATION IS NOT A RUBBER STAMP AND ITS SELFTEST PROVES IT.  T24 3.5a
    registers three negative arms and this file drives all three: `launcher_rc=0`
    with a planted `FOAM FATAL` -> NOT DONE; with the `End` line removed -> NOT
    DONE; with last time 9000 -> NOT DONE.  **A derivation that cannot return
    NOT DONE is not a derivation.**
  * A CONTRADICTION IS NOT RESOLVED BY PICKING THE CONVENIENT RECORD.  If a
    STATUS survives intact and carries a genuine non-zero `rc` while the log
    derives clean, the two independent records of one run disagree.  This file
    returns NOT DONE and names the contradiction.  Rule 4 is all-or-nothing and
    the conservative direction is the only honest one; the derivation is the
    registered path, not a licence to overrule direct evidence of failure.
  * SANAA'S UNIVERSAL RULE OF 2026-08-26 GOVERNS THE CHOICE NOT TO REFUSE:
    **bookkeeping never voids physics.**  A destroyed ledger field cannot void a
    solve.  The destroyed INFRASTRUCTURE fields are reported NOT MEASURED and do
    not void the run; the PHYSICS-CRITICAL conjuncts are all evaluated, on the
    log rather than on the ledger, and each says which.
  * `queue_runner.py` IS CFD'S INSTRUMENT.  The clobber is ESCALATED, NOT
    REPAIRED HERE.  This file proposes no repair and no replacement tool
    (Sanaa's 14-day plumbing freeze).

=== THE CAP IS A REGISTERED OUTCOME OF THIS RUNG, NOT AN ACCIDENT ===

T24 section 5.3 registered, before compute, that these twelve cases run
TWELVE-CONCURRENT on a 16-core box against a rate measured FOUR-concurrent, that
the wall-time headroom to the registered `timeout 2700s` is 1.476x, and that a
contention penalty above ~48 % caps a case.  **A capped case is NOT A RESULT for
THAT ROW ALONE and it does not get a new budget** (CLAUDE.md rule 12).

The capping is caught by the derivation itself and needs no separate gate: a
`timeout` kill leaves no `End` line and a last time below endTime, so conjuncts
1, 2 and 3 all fail.  What this file adds is that when the evidence of capping
survives in STATUS it is NAMED as a CONTENTION finding rather than reported as a
bare missing End line, so that the completion report can attribute it (T24 5.3:
capping is reported as contention and is NEVER folded into the actual/predicted
cost ratio).

L-342 FIELD CLASSES.  PHYSICS-CRITICAL: rc (here derived), the End line, zero
FOAM FATAL, last time == endTime, fields present, ExecutionTime count, the age
guard.  INFRASTRUCTURE: wall_s, ranks, core_min, cap_core_min, timeout_s,
capped, solver, note -- an ABSENT infrastructure field is NOT MEASURED and is
REPORTED; it never voids a run.

AN ABSENT STATUS FILE IS STILL A REFUSAL (exit 2), never an inference from an
End line (K0d L1).  NO `assert` (L-332).  `--selftest` forges cases in scratch
and drives every clause under python3 and python3 -O.

Usage: python3 mark_done_t24.py [CASE ...] [--root DIR] | --selftest
Exit: 0 all DONE, 1 at least one NOT DONE, 2 REFUSAL.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# T24 section 6.2, THE REGISTERED RUN SET.  Twelve, named.  The power is padded
# to three digits so a lexical sort of the case directories is also a numerical
# sort of the power levels.
CASES = tuple("T24_P%03d_U%d" % (p, u)
              for p in (80, 155, 230) for u in (10, 20, 30, 40))

# T24 3.5 conjunct 4.  PER REGION, because two of the three regions are solids.
NEEDED = {
    "fluid":   ("T", "U", "p", "p_rgh", "alphat", "nut", "k", "omega"),
    "housing": ("T", "p"),
    "core":    ("T", "p"),
}
AGE_REF = ("0", "housing", "T")          # T24 3.5 conjunct 6

INFRA = ("wall_s", "ranks", "core_min", "cap_core_min", "timeout_s",
         "capped", "solver")
EXIT_OK, EXIT_NOTDONE, EXIT_REFUSE = 0, 1, 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def dict_num(root, case, key):
    p = os.path.join(root, case, "system", "controlDict")
    if not os.path.isfile(p):
        refuse("no system/controlDict for %s -- a completion rule that guesses "
               "its own target is not a rule" % case)
    m = re.search(r"^\s*%s\s+([0-9.eE+-]+)\s*;" % key, open(p).read(), re.M)
    if not m:
        refuse("controlDict for %s states no %s" % (case, key))
    return float(m.group(1))


def read_status(root, case):
    """STATUS.<case> from INSIDE the case directory.  Absent -> REFUSE."""
    p = os.path.join(root, case, "STATUS.%s" % case)
    if not os.path.isfile(p):
        refuse("no STATUS.%s -- the run's own record was never written. An "
               "absent STATUS is not inferred from an End line (K0d L1); it is "
               "refused." % case)
    return dict(re.findall(r"^([a-z_]+)=(.*)$", open(p).read(), re.M))


def check(root, case):
    """-> (fails, notes).  fails non-empty => NOT DONE."""
    d = os.path.join(root, case)
    fails, notes = [], []
    if not os.path.isdir(d):
        return ["no case directory"], notes

    st = read_status(root, case)

    # --- INFRASTRUCTURE (L-342): reported absent, never a completion conjunct.
    missing = [k for k in INFRA if k not in st]
    if missing:
        notes.append("INFRASTRUCTURE fields NOT MEASURED (L-342; reported, not "
                     "refused; the queue runner overwrote STATUS, as T24 3.5a "
                     "registered in advance that it would): " + ",".join(missing))

    log = os.path.join(d, "log.solve")
    if not os.path.isfile(log):
        return fails + ["no log.solve"], notes
    body = open(log, errors="replace").read()

    n_end = len(re.findall(r"^End\s*$", body, re.M))
    n_fatal = len(re.findall(r"FOAM FATAL", body))

    et = dict_num(root, case, "endTime")
    dt = dict_num(root, case, "deltaT")
    times = sorted(float(x) for x in os.listdir(d)
                   if re.fullmatch(r"[0-9]+(\.[0-9]+)?", x))
    nonzero = [t for t in times if t > 0]
    last = nonzero[-1] if nonzero else None

    # --- CONJUNCT 1: rc.  ALWAYS DERIVED FROM THE LOG (T24 3.5a).
    #     `launcher_rc` is NEVER accepted as rc, whatever its value, INCLUDING 0.
    rc_source = "DERIVED-FROM-LOG"
    why = []
    if "launcher_rc" in st:
        why.append("STATUS carries launcher_rc=%s, which is the exit status of "
                   "the LAUNCH ARGV and NOT the solver's rc (the file says so "
                   "on its own face); it is NOT accepted as rc, EVEN AT 0, "
                   "because a 0 there is the shape of the setsid trap"
                   % st["launcher_rc"])
    if "rc" not in st:
        why.append("STATUS carries no rc key at all")
    notes.append("CONJUNCT 1 (rc = 0) IS UNEVALUABLE FROM STATUS: "
                 + "; ".join(why or ["STATUS carries no usable solver rc"]))
    notes.append("CONJUNCT 1 EVALUATED INSTEAD FROM log.solve (T24 3.5a): End "
                 "lines=%d (want exactly 1), FOAM FATAL=%d (want 0), last "
                 "time=%s (want %g). rc_source=DERIVED-FROM-LOG"
                 % (n_end, n_fatal, "none" if last is None else "%g" % last, et))
    if n_end != 1 or n_fatal != 0 or last is None or abs(last - et) > 1e-9:
        fails.append("rc CANNOT BE DERIVED as 0: End lines=%d, FOAM FATAL=%d, "
                     "last time=%s vs endTime %g"
                     % (n_end, n_fatal,
                        "none" if last is None else "%g" % last, et))

    # --- THE CAP, NAMED WHEN ITS EVIDENCE SURVIVES (T24 5.3, rule 12).
    if st.get("capped") in ("1", "yes") or st.get("rc") == "124":
        fails.append("CAPPED at the registered timeout (capped=%s, rc=%s, "
                     "wall_s=%s against timeout_s=%s): the run reached its "
                     "registered cap and was STOPPED. It does not get a new "
                     "budget (rule 12). This row is NOT A RESULT and the other "
                     "eleven are untouched; T24 5.3 registers the capping as a "
                     "CONTENTION finding, never folded into the cost ratio"
                     % (st.get("capped", "NOT MEASURED"), st.get("rc", "NOT "
                        "MEASURED"), st.get("wall_s", "NOT MEASURED"),
                        st.get("timeout_s", "NOT MEASURED")))

    # --- A SURVIVING, GENUINE, NON-ZERO `rc` CONTRADICTS A CLEAN DERIVATION.
    if re.fullmatch(r"-?\d+", st.get("rc", "")) and int(st["rc"]) != 0:
        notes.append("STATUS SURVIVED INTACT and carries a genuine rc=%s. The "
                     "derivation of T24 3.5a remains the registered path, but a "
                     "non-zero rc is DIRECT evidence of failure and the two "
                     "records are not reconciled by picking the convenient one"
                     % st["rc"])
        fails.append("CRASH: STATUS rc=%s (capped=%s) -- a crash is a FINDING "
                     "until triage says otherwise"
                     % (st["rc"], st.get("capped", "NOT MEASURED")))

    # --- CONJUNCT 2: exactly one End line.
    if n_end != 1:
        fails.append("log.solve carries %d End lines, expected exactly 1" % n_end)

    # --- FOAM FATAL is reported as its own line whichever path was taken.
    if n_fatal:
        fails.append("log.solve carries %d FOAM FATAL occurrences" % n_fatal)

    # --- CONJUNCT 3: last written time == endTime.
    if last is None:
        return fails + ["no time directory beyond 0 -- the solver wrote no "
                        "fields"], notes
    if abs(last - et) > 1e-9:
        fails.append("last written time %g != endTime %g" % (last, et))

    # --- CONJUNCT 4: registered fields present, PER REGION.
    tdir = os.path.join(d, "%g" % last)
    miss = []
    for region in sorted(NEEDED):
        for f in NEEDED[region]:
            if not os.path.isfile(os.path.join(tdir, region, f)):
                miss.append("%s/%s" % (region, f))
    if miss:
        return fails + ["time %g is missing %s" % (last, ",".join(miss))], notes

    # --- CONJUNCT 5: ExecutionTime line count == endTime / deltaT.
    n_exec = len(re.findall(r"^ExecutionTime", body, re.M))
    want = int(round(et / dt))
    if n_exec != want:
        fails.append("%d ExecutionTime lines, expected %d (endTime %g / deltaT "
                     "%g)" % (n_exec, want, et, dt))

    # --- CONJUNCT 6: THE AGE GUARD, against 0/housing/T.
    ref = os.path.join(d, *AGE_REF)
    if not os.path.isfile(ref):
        fails.append("no %s, so the run cannot be dated and the age guard "
                     "cannot be evaluated" % "/".join(AGE_REF))
    else:
        age = os.path.getmtime(ref)
        stale = []
        for region in sorted(NEEDED):
            for f in NEEDED[region]:
                if os.path.getmtime(os.path.join(tdir, region, f)) < age:
                    stale.append("%s/%s" % (region, f))
        if stale:
            fails.append("time %g holds fields OLDER than %s (%s) -- not "
                         "written by this run"
                         % (last, "/".join(AGE_REF), ",".join(stale)))

    notes.append("rc_source=%s" % rc_source)
    return fails, notes


def run(root, want):
    rc = EXIT_OK
    for case in want:
        if case not in CASES:
            refuse("%r is not a registered T24 case (section 6.2): %s"
                   % (case, " ".join(CASES)))
        fails, notes = check(root, case)
        for n in notes:
            print("NOTE      %-14s - %s" % (case, n))
        if fails:
            rc = EXIT_NOTDONE
            print("NOT DONE  %-14s - %s" % (case, "; ".join(fails)))
        else:
            m = os.path.join(root, "DONE.%s" % case)
            if not os.path.exists(m):
                open(m, "w").write("done\n")
            print("DONE      %-14s" % case)
    return rc


def _forge(root, case, end=1, fatal=0, n_exec=None, last="10000", field=True,
           stale=False, status=True, rc=None, launcher_rc="0", infra=False,
           capped=None, et=10000.0, dt=1.0):
    d = os.path.join(root, case)
    os.makedirs(os.path.join(d, "system"), exist_ok=True)
    for region in NEEDED:
        os.makedirs(os.path.join(d, "0", region), exist_ok=True)
        for nm in NEEDED[region]:
            open(os.path.join(d, "0", region, nm), "w").write("x")
    open(os.path.join(d, "system", "controlDict"), "w").write(
        "endTime %g;\ndeltaT %g;\n" % (et, dt))
    # 0/housing/T is touched LAST, exactly as run_t24.sh does it.
    open(os.path.join(d, *AGE_REF), "w").write("x")
    t0 = os.path.getmtime(os.path.join(d, *AGE_REF))
    n = int(round(et / dt)) if n_exec is None else n_exec
    open(os.path.join(d, "log.solve"), "w").write(
        "ExecutionTime = 1 s\n" * n
        + "--> FOAM FATAL ERROR: forged\n" * fatal
        + "End\n" * end)
    tdir = os.path.join(d, last)
    if field:
        for region in NEEDED:
            os.makedirs(os.path.join(tdir, region), exist_ok=True)
            for nm in NEEDED[region]:
                q = os.path.join(tdir, region, nm)
                open(q, "w").write("y")
                os.utime(q, (t0 - 100, t0 - 100) if stale else (t0 + 5, t0 + 5))
    else:
        os.makedirs(tdir, exist_ok=True)
    if status:
        s = ""
        if rc is not None:
            s += "case=%s\nrc=%s\n" % (case, rc)
        if capped is not None:
            s += "capped=%s\nwall_s=2700\ntimeout_s=2700\n" % capped
        if launcher_rc is not None:
            s += ("launcher_rc=%s\nend=2026-08-31T21:02:47Z\n"
                  "note=exit-status-of-the-launch-argv-NOT-the-solver-rc\n"
                  % launcher_rc)
        if infra:
            s += ("wall_s=1787\nranks=1\ncore_min=29.7833\ncap_core_min=45.0\n"
                  "timeout_s=2700\ncapped=0\nsolver=chtMultiRegionSimpleFoam\n")
        open(os.path.join(d, "STATUS.%s" % case), "w").write(s)


def selftest():
    import tempfile
    import shutil
    import ast
    fails = []

    def drive(label, want_rc, want_marker, want_derived=None, **kw):
        tmp = tempfile.mkdtemp(prefix="t24md_")
        try:
            _forge(tmp, CASES[0], **kw)
            import io
            import contextlib
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    code = run(tmp, [CASES[0]])
            except SystemExit as e:
                code = e.code
            out = buf.getvalue()
            marker = os.path.exists(os.path.join(tmp, "DONE.%s" % CASES[0]))
            ok = (code == want_rc and marker == want_marker)
            if want_derived is not None:
                ok = ok and (("DERIVED-FROM-LOG" in out) == want_derived)
                ok = ok and (("UNEVALUABLE FROM STATUS" in out) == want_derived)
            print("  [%s] %-70s -> exit %s, DONE %s"
                  % ("ok " if ok else "FAIL", label, code, marker))
            if not ok:
                fails.append(label)
                print(out)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    # The clobbered-STATUS shape THIS RUNG EXPECTS, and its three registered
    # negative arms (T24 3.5a).
    drive("clobbered STATUS (launcher_rc only) -> DONE, rc DERIVED, loud",
          EXIT_OK, True, want_derived=True)
    drive("NEGATIVE ARM 1 (3.5a): launcher_rc=0 but FOAM FATAL -> NOT DONE",
          EXIT_NOTDONE, False, want_derived=True, fatal=1)
    drive("NEGATIVE ARM 2 (3.5a): launcher_rc=0 but no End line -> NOT DONE",
          EXIT_NOTDONE, False, want_derived=True, end=0)
    drive("NEGATIVE ARM 3 (3.5a): launcher_rc=0 but last time 9000 -> NOT DONE",
          EXIT_NOTDONE, False, want_derived=True, last="9000")
    drive("launcher_rc=1 with a clean log -> DONE (launcher_rc is NOT rc)",
          EXIT_OK, True, want_derived=True, launcher_rc="1")
    # rc is ALWAYS derived at T24, so an intact STATUS does NOT switch paths.
    drive("intact STATUS rc=0 -> DONE, and rc is STILL DERIVED (3.5a)",
          EXIT_OK, True, want_derived=True, rc="0", launcher_rc=None, infra=True)
    drive("intact STATUS rc=1 vs a clean log -> NOT DONE (CONTRADICTION)",
          EXIT_NOTDONE, False, want_derived=True, rc="1", launcher_rc=None,
          infra=True)
    # THE CAP, as a named outcome (T24 5.3, rule 12).
    drive("CAPPED: STATUS capped=1 -> NOT DONE, named as CONTENTION",
          EXIT_NOTDONE, False, want_derived=True, capped="1", launcher_rc=None)
    drive("CAPPED: a timeout kill (rc=124, no End, last time 9000) -> NOT DONE",
          EXIT_NOTDONE, False, want_derived=True, rc="124", launcher_rc=None,
          end=0, last="9000")
    # The remaining rule-4 conjuncts.
    drive("STATUS absent -> REFUSE (never inferred from End)",
          EXIT_REFUSE, False, status=False)
    drive("two End lines -> NOT DONE", EXIT_NOTDONE, False, end=2)
    drive("registered fields missing at endTime -> NOT DONE",
          EXIT_NOTDONE, False, field=False)
    drive("ExecutionTime count 9999 != 10000 -> NOT DONE",
          EXIT_NOTDONE, False, n_exec=9999)
    drive("fields at endTime OLDER than 0/housing/T -> NOT DONE (age guard)",
          EXIT_NOTDONE, False, stale=True)

    # A per-region control: dropping ONE solid field must fail, so the
    # per-region tuple is not decoration.
    tmp = tempfile.mkdtemp(prefix="t24md_")
    try:
        _forge(tmp, CASES[0])
        os.remove(os.path.join(tmp, CASES[0], "10000", "housing", "p"))
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = run(tmp, [CASES[0]])
        ok = (code == EXIT_NOTDONE)
        print("  [%s] per-region control: 10000/housing/p removed -> NOT DONE"
              % ("ok " if ok else "FAIL"))
        if not ok:
            fails.append("per-region")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # An unregistered case name must REFUSE: the run set of 6.2 is closed.
    tmp = tempfile.mkdtemp(prefix="t24md_")
    try:
        code = None
        import io
        import contextlib
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                run(tmp, ["T24_P305_U10"])
        except SystemExit as e:
            code = e.code
        ok = (code == EXIT_REFUSE)
        print("  [%s] an UNREGISTERED case name -> REFUSE (6.2 names twelve, "
              "and P305 is T23's level, not this rung's)"
              % ("ok " if ok else "FAIL"))
        if not ok:
            fails.append("case-set")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    ok = (len(CASES) == 12 and len(set(CASES)) == 12)
    print("  [%s] the registered run set is TWELVE distinct cases (6.2): %s"
          % ("ok " if ok else "FAIL", ",".join(CASES)))
    if not ok:
        fails.append("twelve")

    src = open(__file__).read()
    n0 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src)))
    n1 = sum(isinstance(n, ast.Assert)
             for n in ast.walk(ast.parse(src + "\nassert 1\n")))
    ok = (n0 == 0 and n1 == 1)
    print("  [%s] AST assert count = %d (planted control: %d)"
          % ("ok " if ok else "FAIL", n0, n1))
    if not ok:
        fails.append("ast")

    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    root = HERE
    if "--root" in argv:
        i = argv.index("--root")
        root = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    want = [a for a in argv if not a.startswith("-")] or list(CASES)
    return run(root, want)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
