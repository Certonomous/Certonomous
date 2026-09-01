#!/usr/bin/env python3
"""STRICT COMPLETION (CLAUDE.md rule 4), all-or-nothing, for the FOUR T25R2 runs.

Gates registered at `docs/campaigns/T-family/T25R2_PREREGISTRATION.md` section
6.4.

THIS FILE IS FROZEN BEFORE ANY T25R2 COMPUTE.  No solver, no `blockMesh`, no
`checkMesh`, no `splitMeshRegions` has run for T25R2 and no T25R2 case directory
exists.  The completion rule therefore cannot have been shaped by a result it
had already seen, which is the whole evidentiary content of CLAUDE.md rule 2.

PATTERN.  This is `verification/runs/T-family/T25R_MODULE_runs/mark_done_t25R.py`
in shape -- itself T24's with the L-342 physics/infrastructure split -- with the
registered differences named below.  T25R's completion rule was RIGHT and is
inherited VERBATIM in substance; what changes is the REGISTERED RUN SET and the
document it is frozen against.  `mark_done_t25R.py` is FROZEN and is NOT EDITED
by this rung (CLAUDE.md rule 6); this is a separate file for a separate
registration.

  DIFFERENCE 1.  THE FIELD TUPLE IS THIS RUNG'S, NOT AN INHERITED ONE.
    `T, p` in <endTime>/module   (a SOLID region of chtMultiRegionFoam requires
                                  p; there is no U, k, omega, nut or alphat and
                                  requiring them would make completion
                                  impossible for a MODELLING reason)
    `T U p p_rgh alphat nut k omega` in <endTime>/coolant  (the FLUID region)
    The feasibility rung T25_MOD_L1 was SOLID-ONLY and used {T, p} on ONE region.
    THAT TUPLE IS WRONG FOR T25R2 and is not inherited.  T25R2 has a fluid
    region.

  DIFFERENCE 2.  THE AGE-GUARD REFERENCE IS `0/module/T`, not `0/T`.  A
    multi-region case has no `0/T`.  `run_one_t25R2.sh` touches `0/module/T`
    LAST, on the line immediately before the START block, so that file dates the
    run that was allowed to produce the answer.

  DIFFERENCE 3.  THE ExecutionTime CONJUNCT IS A STEP-COUNT IDENTITY, NOT A
    TIME-VALUE IDENTITY.  Rule 4's wording "ExecutionTime count == endTime" is a
    SHORTHAND that is only literally true at deltaT = 1.  The operative test is
    count == REGISTERED STEP COUNT: 1800 at deltaT 0.5, 3600 at deltaT 0.25.
    Precedent verified inside this family: T20_LC_c, endTime 4500 at deltaT 6,
    750 registered steps, ExecutionTime count 750 (docs/LAB_STATE.md:11221).
    Reading the clause literally would fail every case with deltaT != 1.
    On an adaptive or non-unit step the substantive form is ONE ExecutionTime
    PER ADVANCED STEP WITH NO TRUNCATED TAIL.  T25R2 registers
    `adjustTimeStep no`, so the count is exact -- and this file CHECKS that
    `adjustTimeStep` is not `yes` rather than assuming it, because on an
    adaptive step the identity would not hold and a silent pass would be worse
    than a refusal.

  DIFFERENCE 4.  THE STALE-MARKER RE-CHECK.  A DONE.<case> marker found on disk
    is NOT accepted on sight.  Every conjunct is re-evaluated on every
    invocation and a marker whose case no longer satisfies them is REMOVED.
    A marker is a cache, never evidence.

=== rc IS ALWAYS DERIVED FROM THE LOG, AND NEVER READ FROM STATUS ===

`launcher_rc` IS NOT rc AND IS NEVER ACCEPTED AS rc, EVEN AT 0.  It is the exit
status of the argv the queue runner spawned, and a 0 there is exactly the shape
of the setsid trap: `setsid timeout cmd` exits 0 for every outcome.  The queue
runner is MEASURED to overwrite STATUS.<case> after the launcher writes it
(T24 section 3.5a: it happened to T22_CHTb_L1 and to all four T23_P305_U*).
This file assumes it will happen again.

CONJUNCT 1 is therefore DERIVED FROM log.solve: exactly one `End` line, ZERO
`FOAM FATAL`, and last written time == endTime.  Every line printed names which
conjuncts were UNEVALUABLE FROM STATUS and what they were evaluated from
instead.  A conjunct silently treated as passing because its evidence was
destroyed is the failure mode that paragraph exists to prevent.

A DERIVATION THAT CANNOT RETURN "NOT DONE" IS NOT A DERIVATION.  --selftest
drives every negative arm.

A CONTRADICTION IS NOT RESOLVED BY PICKING THE CONVENIENT RECORD.  If STATUS
survives intact and carries a genuine non-zero rc while the log derives clean,
this file returns NOT DONE and names the contradiction.

SANAA'S UNIVERSAL RULE OF 2026-08-26 GOVERNS THE CHOICE NOT TO REFUSE:
BOOKKEEPING NEVER VOIDS PHYSICS.  A destroyed ledger field cannot void a solve.
L-342 field classes:
  PHYSICS-CRITICAL: rc (derived), the End line, zero FOAM FATAL, last time ==
    endTime, fields present per region, ExecutionTime count, the age guard.
  INFRASTRUCTURE: wall_s, ranks, core_min, cap_core_min, timeout_s, capped,
    solver, note -- an ABSENT infrastructure field is NOT MEASURED and is
    REPORTED; it never voids a run.

AN ABSENT STATUS FILE IS STILL A REFUSAL (exit 2), never an inference from an
End line (K0d L1).  NO `assert` (L-332) -- this file must behave identically
under `python3 -O`.

THE CAP IS A NAMED OUTCOME, NOT A SURPRISE (T25R2 section 8.2, CLAUDE.md rule
12).  A capped row is NOT A RESULT for THAT ROW ALONE and DOES NOT GET A NEW
BUDGET.  A timeout kill leaves no End line and a short last time, so conjuncts
1-3 fail by construction; what this file adds is that when the evidence survives
in STATUS the stop is NAMED as a cap stop so the completion report can attribute
it and never fold it into the cost ratio.

Usage: python3 mark_done_t25R2.py [CASE ...] [--root DIR] | --selftest
Exit:  0 all DONE, 1 at least one NOT DONE, 2 REFUSAL.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

# T25R2 section 1, THE REGISTERED RUN SET.  FOUR, named, and closed.
# case -> registered step count (section 6.4 conjunct 5).
#
# DIFFERENCE 5 (new in T25R2).  `T25R2_L1_OC20` IS A FULL REGISTERED RUN, not a
# diagnostic sidecar.  It is L1 in every respect except `nOuterCorrectors`
# (20 rather than 10) and it carries the IDENTICAL completion rule: it is the
# second arm of the section 3.5 OUTER-LOOP INDEPENDENCE GATE, and a gate whose
# reference arm is allowed to be incomplete is not a gate.  Its registered step
# count is 1800, the same as `T25R2_L1`: sweeps are inside a step, not steps.
CASES = {
    "T25R2_L1":        1800,
    "T25R2_L1_OC20":   1800,
    "T25R2_L2":        1800,
    "T25R2_L2_DT025":  3600,
}

# T25R section 6.4 conjunct 4.  PER REGION, because one region is a SOLID.
NEEDED = {
    "coolant": ("T", "U", "p", "p_rgh", "alphat", "nut", "k", "omega"),
    "module":  ("T", "p"),
}
AGE_REF = ("0", "module", "T")            # T25R2 section 6.4 conjunct 6
END_TIME = 900.0                          # T25R2 section 3.4

INFRA = ("wall_s", "ranks", "core_min", "cap_core_min", "timeout_s",
         "capped", "solver")
EXIT_OK, EXIT_NOTDONE, EXIT_REFUSE = 0, 1, 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def dict_entry(root, case, key):
    """Raw string value of `key` in system/controlDict.  None if absent."""
    p = os.path.join(root, case, "system", "controlDict")
    if not os.path.isfile(p):
        refuse("no system/controlDict for %s -- a completion rule that guesses "
               "its own target is not a rule" % case)
    m = re.search(r"^\s*%s\s+([^;]+);" % key, open(p).read(), re.M)
    return m.group(1).strip() if m else None


def dict_num(root, case, key):
    v = dict_entry(root, case, key)
    if v is None:
        refuse("controlDict for %s states no %s" % (case, key))
    try:
        return float(v)
    except ValueError:
        refuse("controlDict for %s has non-numeric %s = %r" % (case, key, v))


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
                     "refused -- the queue runner is measured to overwrite "
                     "STATUS): " + ",".join(missing))

    log = os.path.join(d, "log.solve")
    if not os.path.isfile(log):
        return fails + ["no log.solve"], notes
    body = open(log, errors="replace").read()

    n_end = len(re.findall(r"^End\s*$", body, re.M))
    n_fatal = len(re.findall(r"FOAM FATAL", body))

    et = dict_num(root, case, "endTime")
    dt = dict_num(root, case, "deltaT")
    want_steps = CASES[case]

    # --- THE REGISTERED ENDTIME AND STEP COUNT ARE NOT TAKEN ON TRUST.
    #     A case whose controlDict does not match section 3.4 / 6.4 is not the
    #     registered case, whatever its directory is called.
    if abs(et - END_TIME) > 1e-9:
        fails.append("controlDict endTime %g != the REGISTERED %g (T25R2 3.4) -- "
                     "this is not the registered case" % (et, END_TIME))
    if dt <= 0.0 or abs(et / dt - want_steps) > 1e-6:
        fails.append("controlDict deltaT %g over endTime %g gives %.6f steps, "
                     "but T25R2 6.4 registers %d for %s"
                     % (dt, et, (et / dt if dt else float('nan')), want_steps,
                        case))

    # --- DIFFERENCE 3: the step-count identity only holds on a FIXED step.
    ats = dict_entry(root, case, "adjustTimeStep")
    if ats is not None and ats.lower() in ("yes", "true", "on", "1"):
        fails.append("controlDict has adjustTimeStep %s -- T25R2 3.4 registers "
                     "`no`. On an adaptive step the ExecutionTime count is NOT "
                     "a step-count identity and this instrument will not "
                     "certify it silently" % ats)

    times = sorted(float(x) for x in os.listdir(d)
                   if re.fullmatch(r"[0-9]+(\.[0-9]+)?", x))
    nonzero = [t for t in times if t > 0]
    last = nonzero[-1] if nonzero else None

    # --- CONJUNCT 1: rc.  ALWAYS DERIVED FROM THE LOG.
    why = []
    if "launcher_rc" in st:
        why.append("STATUS carries launcher_rc=%s, which is the exit status of "
                   "the LAUNCH ARGV and NOT the solver's rc; it is NOT accepted "
                   "as rc, EVEN AT 0, because a 0 there is the shape of the "
                   "setsid trap" % st["launcher_rc"])
    if "rc" not in st:
        why.append("STATUS carries no rc key at all")
    notes.append("CONJUNCT 1 (rc = 0) IS UNEVALUABLE FROM STATUS: "
                 + "; ".join(why or ["STATUS carries no usable solver rc"]))
    notes.append("CONJUNCT 1 EVALUATED INSTEAD FROM log.solve: End lines=%d "
                 "(want exactly 1), FOAM FATAL=%d (want 0), last time=%s "
                 "(want %g). rc_source=DERIVED-FROM-LOG"
                 % (n_end, n_fatal, "none" if last is None else "%g" % last, et))
    if n_end != 1 or n_fatal != 0 or last is None or abs(last - et) > 1e-9:
        fails.append("rc CANNOT BE DERIVED as 0: End lines=%d, FOAM FATAL=%d, "
                     "last time=%s vs endTime %g"
                     % (n_end, n_fatal,
                        "none" if last is None else "%g" % last, et))

    # --- THE CAP, NAMED WHEN ITS EVIDENCE SURVIVES (T25R2 8.2, rule 12).
    if st.get("capped") in ("1", "yes") or st.get("rc") == "124":
        fails.append("CAPPED at the registered timeout (capped=%s, rc=%s, "
                     "wall_s=%s against timeout_s=%s): the run reached its "
                     "registered cap and was STOPPED. It DOES NOT GET A NEW "
                     "BUDGET (CLAUDE.md rule 12). This row is NOT A RESULT, the "
                     "other rows are untouched, and the cap stop is its own "
                     "finding -- never folded into the cost ratio"
                     % (st.get("capped", "NOT MEASURED"),
                        st.get("rc", "NOT MEASURED"),
                        st.get("wall_s", "NOT MEASURED"),
                        st.get("timeout_s", "NOT MEASURED")))

    # --- A SURVIVING, GENUINE, NON-ZERO rc CONTRADICTS A CLEAN DERIVATION.
    if re.fullmatch(r"-?\d+", st.get("rc", "")) and int(st["rc"]) != 0:
        notes.append("STATUS SURVIVED INTACT and carries a genuine rc=%s. The "
                     "derivation remains the registered path, but a non-zero rc "
                     "is DIRECT evidence of failure and the two records are not "
                     "reconciled by picking the convenient one" % st["rc"])
        fails.append("CRASH: STATUS rc=%s (capped=%s) -- a crash is a FINDING "
                     "until triage says otherwise"
                     % (st["rc"], st.get("capped", "NOT MEASURED")))

    # --- CONJUNCT 2: exactly one End line.
    if n_end != 1:
        fails.append("log.solve carries %d End lines, expected exactly 1" % n_end)
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

    # --- CONJUNCT 5: ExecutionTime count == THE REGISTERED STEP COUNT.
    n_exec = len(re.findall(r"^ExecutionTime", body, re.M))
    if n_exec != want_steps:
        fails.append("%d ExecutionTime lines, expected the REGISTERED %d "
                     "(endTime %g / deltaT %g). This is a STEP-COUNT identity, "
                     "not a time-value identity; a shortfall is a TRUNCATED "
                     "TAIL" % (n_exec, want_steps, et, dt))

    # --- CONJUNCT 6: THE AGE GUARD, against 0/module/T.
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

    notes.append("rc_source=DERIVED-FROM-LOG")
    return fails, notes


def run(root, want):
    rc = EXIT_OK
    for case in want:
        if case not in CASES:
            refuse("%r is not a registered T25R2 case (section 1): %s"
                   % (case, " ".join(sorted(CASES))))
        fails, notes = check(root, case)
        for n in notes:
            print("NOTE      %-18s - %s" % (case, n))
        marker = os.path.join(root, "DONE.%s" % case)
        if fails:
            rc = EXIT_NOTDONE
            print("NOT DONE  %-18s - %s" % (case, "; ".join(fails)))
            # DIFFERENCE 4: THE STALE-MARKER RE-CHECK.  A marker is a cache,
            # never evidence.  A case that no longer completes loses its marker.
            if os.path.exists(marker):
                os.remove(marker)
                print("STALE     %-18s - DONE marker REMOVED: the case no "
                      "longer satisfies rule 4" % case)
        else:
            if not os.path.exists(marker):
                open(marker, "w").write("done\n")
            print("DONE      %-18s - all six conjuncts hold" % case)
    return rc


# --------------------------------------------------------------------------
# SELFTEST.  Forges cases in scratch and drives every clause, positive and
# negative, under python3 and python3 -O.  A derivation that cannot return NOT
# DONE is not a derivation.
# --------------------------------------------------------------------------

def _forge(root, case, steps=None, dt=0.5, end=1, fatal=0, n_exec=None,
           last="900", fields=True, age_ok=True, status=None, ats="no",
           endtime=900.0):
    steps = CASES[case] if steps is None else steps
    n_exec = steps if n_exec is None else n_exec
    d = os.path.join(root, case)
    os.makedirs(os.path.join(d, "system"), exist_ok=True)
    open(os.path.join(d, "system", "controlDict"), "w").write(
        "application     chtMultiRegionFoam;\nendTime         %g;\n"
        "deltaT          %g;\nadjustTimeStep  %s;\n" % (endtime, dt, ats))
    st = status if status is not None else (
        "launcher_rc=0\nnote=exit-status-of-the-launch-argv-NOT-the-solver-rc\n")
    open(os.path.join(d, "STATUS.%s" % case), "w").write(st)
    body = ["ExecutionTime = %g s  ClockTime = %d s" % (i * 0.1, i)
            for i in range(1, n_exec + 1)]
    body += ["FOAM FATAL ERROR"] * fatal
    body += ["End"] * end
    open(os.path.join(d, "log.solve"), "w").write("\n".join(body) + "\n")

    ref = os.path.join(d, "0", "module")
    os.makedirs(ref, exist_ok=True)
    open(os.path.join(ref, "T"), "w").write("x\n")
    if fields:
        for region, fl in NEEDED.items():
            td = os.path.join(d, last, region)
            os.makedirs(td, exist_ok=True)
            for f in fl:
                open(os.path.join(td, f), "w").write("x\n")
    # the age guard: 0/module/T must be OLDER than every field.
    t0 = os.path.getmtime(os.path.join(ref, "T"))
    shift = -100.0 if age_ok else +100.0
    os.utime(os.path.join(ref, "T"), (t0 + shift, t0 + shift))
    return d


def selftest():
    fails = 0

    def chk(name, cond):
        nonlocal fails
        print("  %-4s %s" % ("ok" if cond else "FAIL", name))
        if not cond:
            fails += 1

    root = tempfile.mkdtemp(prefix="t25R2md_")
    try:
        C = "T25R2_L2"
        _forge(root, C)
        chk("clean forge is DONE", run(root, [C]) == EXIT_OK)
        chk("clean forge wrote DONE marker",
            os.path.exists(os.path.join(root, "DONE.%s" % C)))

        # NEGATIVE ARM 1: launcher_rc=0 with a planted FOAM FATAL.
        shutil.rmtree(os.path.join(root, C))
        _forge(root, C, fatal=1)
        chk("planted FOAM FATAL under launcher_rc=0 -> NOT DONE",
            run(root, [C]) == EXIT_NOTDONE)
        chk("STALE marker was REMOVED",
            not os.path.exists(os.path.join(root, "DONE.%s" % C)))

        # NEGATIVE ARM 2: the End line removed.
        shutil.rmtree(os.path.join(root, C))
        _forge(root, C, end=0)
        chk("missing End line -> NOT DONE", run(root, [C]) == EXIT_NOTDONE)

        # NEGATIVE ARM 3: last time short of endTime.
        shutil.rmtree(os.path.join(root, C))
        _forge(root, C, last="450")
        chk("last time 450 vs endTime 900 -> NOT DONE",
            run(root, [C]) == EXIT_NOTDONE)

        # NEGATIVE ARM 4: a truncated ExecutionTime tail.
        shutil.rmtree(os.path.join(root, C))
        _forge(root, C, n_exec=CASES[C] - 1)
        chk("ExecutionTime count short by one -> NOT DONE",
            run(root, [C]) == EXIT_NOTDONE)

        # NEGATIVE ARM 5: THE FLUID TUPLE IS ENFORCED.  A solid-only case that
        # would have passed the FEASIBILITY rung's {T,p} must FAIL here.
        shutil.rmtree(os.path.join(root, C))
        _forge(root, C)
        os.remove(os.path.join(root, C, "900", "coolant", "omega"))
        chk("coolant/omega absent -> NOT DONE (the solid-only tuple is NOT "
            "inherited)", run(root, [C]) == EXIT_NOTDONE)

        # NEGATIVE ARM 6: the age guard.
        shutil.rmtree(os.path.join(root, C))
        _forge(root, C, age_ok=False)
        chk("fields older than 0/module/T -> NOT DONE",
            run(root, [C]) == EXIT_NOTDONE)

        # NEGATIVE ARM 7: a genuine non-zero rc contradicting a clean log.
        shutil.rmtree(os.path.join(root, C))
        _forge(root, C, status="rc=1\ncapped=no\nwall_s=10\n")
        chk("genuine rc=1 with a clean log -> NOT DONE (contradiction named)",
            run(root, [C]) == EXIT_NOTDONE)

        # NEGATIVE ARM 8: the cap, named.
        shutil.rmtree(os.path.join(root, C))
        _forge(root, C, status="rc=124\ncapped=yes\nwall_s=5640\n"
                               "timeout_s=5640\n")
        chk("capped=yes / rc=124 -> NOT DONE (cap stop, no new budget)",
            run(root, [C]) == EXIT_NOTDONE)

        # NEGATIVE ARM 9: adaptive stepping breaks the step-count identity.
        shutil.rmtree(os.path.join(root, C))
        _forge(root, C, ats="yes")
        chk("adjustTimeStep yes -> NOT DONE (identity does not hold)",
            run(root, [C]) == EXIT_NOTDONE)

        # NEGATIVE ARM 10: a deltaT that is not the registered one.
        shutil.rmtree(os.path.join(root, C))
        _forge(root, C, dt=0.25, n_exec=CASES[C])
        chk("deltaT 0.25 under the id registered at 0.5 -> NOT DONE",
            run(root, [C]) == EXIT_NOTDONE)

        # NEGATIVE ARM 11: the wrong endTime.
        shutil.rmtree(os.path.join(root, C))
        _forge(root, C, endtime=450.0, last="450", dt=0.25)
        chk("endTime 450 -> NOT DONE (not the registered case)",
            run(root, [C]) == EXIT_NOTDONE)

        # THE DT025 ARM, whose registered count is 3600 and not 1800.
        D = "T25R2_L2_DT025"
        _forge(root, D, dt=0.25)
        chk("T25R2_L2_DT025 at deltaT 0.25 / 3600 steps is DONE",
            run(root, [D]) == EXIT_OK)
        shutil.rmtree(os.path.join(root, D))
        _forge(root, D, dt=0.25, n_exec=1800)
        chk("T25R2_L2_DT025 with 1800 ExecutionTime lines -> NOT DONE",
            run(root, [D]) == EXIT_NOTDONE)

        # THE OC20 ARM.  Section 3.5 gates on agreement between T25R2_L1 and
        # T25R2_L1_OC20, so the OC20 arm carries the IDENTICAL completion rule
        # and a gate whose reference arm may be incomplete is not a gate.
        O = "T25R2_L1_OC20"
        _forge(root, O)
        chk("T25R2_L1_OC20 at 1800 steps is DONE (sweeps are inside a step, "
            "not steps)", run(root, [O]) == EXIT_OK)
        shutil.rmtree(os.path.join(root, O))
        _forge(root, O, n_exec=CASES[O] - 1)
        chk("T25R2_L1_OC20 with a truncated ExecutionTime tail -> NOT DONE: "
            "the OUTER-LOOP GATE'S REFERENCE ARM IS NOT EXEMPT",
            run(root, [O]) == EXIT_NOTDONE)

        # AN ABSENT STATUS IS A REFUSAL, NOT AN INFERENCE (K0d L1).
        shutil.rmtree(os.path.join(root, C))
        _forge(root, C)
        os.remove(os.path.join(root, C, "STATUS.%s" % C))
        r = subprocess.run([sys.executable, os.path.abspath(__file__),
                            C, "--root", root],
                           capture_output=True, text=True)
        chk("absent STATUS -> REFUSE (exit 2), never an inference",
            r.returncode == EXIT_REFUSE and "REFUSE" in r.stdout)

        # AN UNREGISTERED CASE NAME IS A REFUSAL.
        r = subprocess.run([sys.executable, os.path.abspath(__file__),
                            "T25R2_L9", "--root", root],
                           capture_output=True, text=True)
        chk("unregistered case name -> REFUSE (exit 2)",
            r.returncode == EXIT_REFUSE)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    print("SELFTEST %s (%d failed)" % ("PASS" if fails == 0 else "FAIL", fails))
    return EXIT_OK if fails == 0 else EXIT_NOTDONE


def main(argv):
    if "--selftest" in argv:
        return selftest()
    root = HERE
    if "--root" in argv:
        i = argv.index("--root")
        root = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    want = [a for a in argv if not a.startswith("-")] or sorted(CASES)
    return run(root, want)


def _guarded(argv):
    """*** THE TRACEBACK TRAP, MEASURED ELSEWHERE THIS NIGHT AND CLOSED HERE. ***

    An instrument with no `except` clause lets an uncaught traceback leave the
    interpreter with exit status 1 -- which in this file's own exit vocabulary
    is NOT DONE, i.e. a GRADED outcome.  A crash would then be indistinguishable
    from a measurement, which is the precise shape of a false negative result.
    Every uncaught exception is therefore converted to a REFUSAL (exit 2) with
    the traceback printed, because a crashed instrument has measured NOTHING and
    is not entitled to return a graded answer of any kind.

    `SystemExit` is re-raised untouched: it carries the deliberate exit codes of
    `refuse()` and of `run()`.
    """
    try:
        return main(argv)
    except SystemExit:
        raise
    except BaseException:
        import traceback
        traceback.print_exc()
        print("REFUSE: mark_done_t25R2.py raised an uncaught exception. A "
              "CRASHED INSTRUMENT HAS MEASURED NOTHING and exits on the REFUSE "
              "path (2), NEVER on the NOT DONE path (1), so that a crash can "
              "never be mistaken for a graded completion verdict.")
        return EXIT_REFUSE


if __name__ == "__main__":
    sys.exit(_guarded(sys.argv[1:]))
