#!/usr/bin/env python3
"""T25R2 COMPLETION + COST-CALIBRATION REPORTER.

*** THIS SCRIPT DECIDES NOTHING AND IS NOT IN SECTION 11's FREEZE TABLE. ***

RULE 4 COMPLETION IS DECIDED BY `mark_done_t25R2.py` AND IS NOT REIMPLEMENTED
HERE.  This file CALLS it and prints its verdict FIRST.  Everything after that
is a CORROBORATION READ: the same six conjuncts measured again straight off the
raw artefacts, so a reader can see the evidence rather than take the marker's
word for it.  Where the two ever disagree, `mark_done_t25R2.py` IS THE
AUTHORITY and this file is the thing that is wrong -- it has no power to pass a
run the marker failed, and it is explicit about that on its own face.

*** IT EMITS NO WORD FROM THE FIXED VOCABULARY EXCEPT WHEN QUOTING THE MARKER,
AND IT GRADES NO PHYSICS. ***  D1/D2/D3, the energy gate and the section 3.5
outer-loop gate belong to `analyse_t25R2.py` and to nothing else.  No number
printed here is a result.

WHY THE AGE-GUARD MARGIN IS COMPUTED OVER *EVERY* WRITTEN TIME.  Rule 4's
conjunct 6 requires the fields AT endTime to be newer than the case's own
`0/module/T`.  That is the binding test and `mark_done_t25R2.py` applies it.
This file additionally reports the TIGHTEST margin across ALL written times and
BOTH regions, because a margin of a few seconds at some intermediate write is
the shape of a case that was partially restaged, and a guard that only ever
looks at the last write would not see it.

Usage: python3 report_completion_t25R2.py <CASE> [--out FILE]
Exit:  0 the marker says DONE, 1 the marker says NOT DONE, 2 REFUSAL.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mark_done_t25R2 as MD                                    # noqa: E402
import analyse_t25R2 as A                                       # noqa: E402

# Section 8.2 of the frozen document, transcribed.  POINT / HARD CAP / timeout.
COST = {
    "T25R2_L1":       dict(point=8.30, cap=34, timeout=2040, factor=4),
    "T25R2_L1_OC20":  dict(point=18.09, cap=73, timeout=4380, factor=4),
    "T25R2_L2":       dict(point=18.68, cap=94, timeout=5640, factor=5),
    "T25R2_L2_DT025": dict(point=37.35, cap=187, timeout=11220, factor=5),
}
RATE_USD_PER_CORE_H = 0.0513      # owner-stated 2026-08-21/22, NOT measured


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(2)


def main(argv):
    # `--out` takes a VALUE, and that value is not a case name.  The first
    # draft of this parser collected it as a second positional and the guard
    # below REFUSED rather than guess which of the two was meant -- which is
    # the behaviour wanted, on a bug that was mine.
    out = None
    argv = list(argv)
    if "--out" in argv:
        i = argv.index("--out")
        if i + 1 >= len(argv):
            refuse("--out was given with no path after it")
        out = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    want = [a for a in argv if not a.startswith("-")]
    if len(want) != 1 or want[0] not in MD.CASES:
        refuse("name exactly one registered T25R2 case: %s"
               % " ".join(sorted(MD.CASES)))
    case = want[0]
    d = os.path.join(HERE, case)
    L = []
    say = L.append

    say("=" * 74)
    say("%s -- COMPLETION AND COST, %d registered steps, nOuterCorrectors %d"
        % (case, MD.CASES[case], A.NOUTER[case]))
    say("=" * 74)

    # ---- THE AUTHORITY, FIRST AND UNCONDITIONALLY. ------------------------
    fails, notes = MD.check(HERE, case)
    say("RULE 4 IS DECIDED BY mark_done_t25R2.py AND IS NOT REIMPLEMENTED HERE.")
    for n in notes:
        say("  MARKER NOTE  %s" % n)
    if fails:
        say("  MARKER VERDICT: NOT DONE -- %s" % "; ".join(fails))
    else:
        say("  MARKER VERDICT: DONE -- all six conjuncts hold.")

    # ---- CORROBORATION: the six conjuncts, measured off raw artefacts. ----
    say("")
    say("CORROBORATION READ (evidence, not authority):")
    log = os.path.join(d, "log.solve")
    if not os.path.isfile(log):
        refuse("no log.solve for %s" % case)
    body = open(log, errors="replace").read()

    rcf = os.path.join(d, ".rc.%s" % case)
    rc_raw = open(rcf).read().strip() if os.path.isfile(rcf) else "ABSENT"
    stp = os.path.join(d, "STATUS.%s" % case)
    st = dict(re.findall(r"^([a-z_]+)=(.*)$", open(stp).read(), re.M)) \
        if os.path.isfile(stp) else {}

    n_end = len(re.findall(r"^End\s*$", body, re.M))
    n_fatal = len(re.findall(r"FOAM FATAL", body))
    n_exec = len(re.findall(r"^ExecutionTime", body, re.M))
    times = sorted(float(x) for x in os.listdir(d)
                   if re.fullmatch(r"[0-9]+(\.[0-9]+)?", x))
    nz = [t for t in times if t > 0]
    last = nz[-1] if nz else None

    say("  1. rc        SOLVER rc RECORDED, NOT INFERRED: .rc.%s = %s ; "
        "STATUS rc = %s. (launcher_rc is never accepted as rc, even at 0.)"
        % (case, rc_raw, st.get("rc", "NOT MEASURED")))
    say("  2. End       exactly %d `End` line(s) [want 1] ; %d FOAM FATAL "
        "[want 0]" % (n_end, n_fatal))
    say("  3. lastTime  %s written time dirs, last = %s [want %g]"
        % (len(times), "none" if last is None else "%g" % last, MD.END_TIME))
    miss = []
    if last is not None:
        td = os.path.join(d, "%g" % last)
        for region in sorted(MD.NEEDED):
            for f in MD.NEEDED[region]:
                if not os.path.isfile(os.path.join(td, region, f)):
                    miss.append("%s/%s" % (region, f))
    say("  4. fields    module %s ; coolant %s -- missing: %s"
        % (",".join(MD.NEEDED["module"]), ",".join(MD.NEEDED["coolant"]),
           ",".join(miss) if miss else "NONE"))
    say("  5. steps     %d ExecutionTime lines [want the REGISTERED %d]. This "
        "is a STEP-COUNT identity, not a time-value identity: endTime %g at "
        "deltaT %g." % (n_exec, MD.CASES[case], MD.END_TIME, A.DELTAT[case]))

    # ---- conjunct 6, and the TIGHTEST margin over EVERY written time. -----
    ref = os.path.join(d, *MD.AGE_REF)
    if not os.path.isfile(ref):
        say("  6. ageGuard NO %s -- the run cannot be dated."
            % "/".join(MD.AGE_REF))
    else:
        t0 = os.path.getmtime(ref)
        worst, worst_at, n_checked, stale = None, None, 0, []
        for t in times:
            td = os.path.join(d, "%g" % t)
            for region in sorted(MD.NEEDED):
                for f in MD.NEEDED[region]:
                    p = os.path.join(td, region, f)
                    if not os.path.isfile(p):
                        continue
                    n_checked += 1
                    m = os.path.getmtime(p) - t0
                    if t > 0 and (worst is None or m < worst):
                        worst, worst_at = m, "t=%g %s/%s" % (t, region, f)
                    if t > 0 and m < 0:
                        stale.append("t=%g %s/%s" % (t, region, f))
        say("  6. ageGuard reference %s ; %d field files checked across ALL %d "
            "written times and BOTH regions."
            % ("/".join(MD.AGE_REF), n_checked, len(times)))
        say("     TIGHTEST margin over every written time: %+.3f s at %s "
            "[must be > 0]" % (worst if worst is not None else float("nan"),
                               worst_at))
        say("     fields OLDER than the reference: %s"
            % (",".join(stale) if stale else "NONE"))

    # ---- COST, rule 12. --------------------------------------------------
    c = COST[case]
    m = re.findall(r"^ExecutionTime = ([0-9.eE+-]+) s", body, re.M)
    exec_s = float(m[-1]) if m else None
    ranks = int(st.get("ranks", "1") or 1)
    say("")
    say("COST -- CLAUDE.md RULE 12.  The unit is CORE-MINUTES (wall s x ranks "
        "/ 60).")
    if exec_s is None:
        say("  ExecutionTime NOT MEASURED -- no ExecutionTime line in log.solve.")
        return 1 if fails else 0
    actual_solver = exec_s * ranks / 60.0
    wall = float(st["wall_s"]) if "wall_s" in st else None
    actual_wall = (wall * ranks / 60.0) if wall is not None else None
    say("  SOLVER core-min (log.solve ExecutionTime %.2f s x ranks %d / 60) "
        "= %.3f" % (exec_s, ranks, actual_solver))
    if actual_wall is not None:
        say("  WALL   core-min (STATUS wall_s %g x ranks %d / 60) = %.3f"
            % (wall, ranks, actual_wall))
        say("  LAUNCH OVERHEAD, NAMED SEPARATELY (wall minus solver) = %.3f "
            "core-min -- staging `0` from `0.orig`, the age touch and the "
            "5 s poll granularity of the launcher. It is NOT waste and it is "
            "NOT folded into the ratio." % (actual_wall - actual_solver))
    say("  PRE-REGISTERED POINT (section 8.2) = %.2f core-min ; HARD CAP = %d "
        "core-min (x%d margin) ; timeout_s = %d"
        % (c["point"], c["cap"], c["factor"], c["timeout"]))
    say("  *** RATIO actual/predicted = %.3f *** (solver core-min against the "
        "POINT)" % (actual_solver / c["point"]))
    say("  against the HARD CAP: %.3f of it used, %.3f core-min unspent"
        % (actual_solver / c["cap"], c["cap"] - actual_solver))
    say("  capped=%s rc=%s -- a cap stop is a NAMED OUTCOME and does not get a "
        "new budget (rule 12)."
        % (st.get("capped", "NOT MEASURED"), st.get("rc", "NOT MEASURED")))
    usd = actual_solver / 60.0 * RATE_USD_PER_CORE_H
    say("  DOLLARS %.4f USD at $%.4f/core-h, c7a.4xlarge -- *** DERIVED, NOT "
        "MEASURED ***. cost_basis = REPORTED-BY-OWNER: this box cannot read "
        "its own billing (COMPUTE_BUDGET_CHARTER section 5)." % (usd,
                                                                RATE_USD_PER_CORE_H))

    # ---- CONTENTION, ATTRIBUTED AND NEVER ABSORBED. ----------------------
    lc = os.path.join(d, "..", "LAUNCH_CONTEXT.%s.txt" % case)
    lc2 = os.path.join(HERE, "LAUNCH_CONTEXT.%s.txt" % case)
    p = lc2 if os.path.isfile(lc2) else lc
    say("")
    say("CONTENTION -- ATTRIBUTED SEPARATELY, NEVER ABSORBED INTO THE RATIO "
        "(COMPUTE_BUDGET_CHARTER section 6).")
    if os.path.isfile(p):
        for line in open(p).read().strip().splitlines():
            say("  %s" % line)
    else:
        say("  NO LAUNCH CONTEXT RECORDED -- contention is NOT MEASURED for "
            "this row and must be reported as such, never assumed absent.")
    say("  Section 8.1 caveat 4 stands: wall-derived core-minutes on a SHARED "
        "box carry contention. ExecutionTime is the solver's own CPU-time "
        "accounting and is the figure used for the ratio above.")

    txt = "\n".join(L)
    print(txt)
    if out:
        open(out, "w").write(txt + "\n")
    return 1 if fails else 0


def _guarded(argv, _fn=None):
    fn = main if _fn is None else _fn
    try:
        return fn(argv)
    except SystemExit:
        raise
    except BaseException:
        import traceback
        traceback.print_exc()
        print("REFUSE: report_completion_t25R2.py raised an uncaught "
              "exception. A CRASHED REPORTER HAS REPORTED NOTHING and exits 2, "
              "never on the NOT DONE path.")
        return 2


if __name__ == "__main__":
    sys.exit(_guarded(sys.argv[1:]))
