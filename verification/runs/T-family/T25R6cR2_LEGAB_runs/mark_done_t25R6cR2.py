#!/usr/bin/env python3
"""T25R6c-R2 COMPLETION MARKER -- DEFAULT-DENY.

Writes `DONE.<CASE>` only when rule 4 holds in FULL, and the rule-4 definition is
IMPORTED FROM THE FROZEN GRADER rather than retyped, so there is exactly ONE
definition of completion in this rung.  A retyped guard is a new guard, and a new
guard is unproven no matter how carefully it was copied.

WHY THE MARKER MATTERS BEYOND BOOKKEEPING: scripts/check_comparator_freeze.py
dates a comparator's freeze against the EARLIEST completion marker of the cases
it grades.  A marker saying "done" about a case that is not done would corrupt
every freeze judgment later dated against it.  So an incomplete case gets NO
marker at all -- never a marker with a caveat inside it.

THIS FILE ISSUES NO VERDICT.  It imports and calls `rule4` only.  Grading
T25R6c-R2 requires `grade_t25R6cR2.py --grade`, which is a CHANGED MEASUREMENT
SCRIPT whose diff is the supervisor's personal, non-delegable read
(SUPERVISION_CHARTER section 3 check 1).

    python3 mark_done_t25R6cR2.py --case <abs case dir>
"""
import datetime
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GRADER = os.path.join(HERE, "grade_t25R6cR2.py")
EXIT_REFUSE = 2


def load_grader():
    if not os.path.isfile(GRADER):
        print("REFUSE: the frozen grader is absent: %s" % GRADER)
        sys.exit(EXIT_REFUSE)
    spec = importlib.util.spec_from_file_location("grade_t25R6cR2", GRADER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(argv):
    if "--case" not in argv:
        print(__doc__)
        return EXIT_REFUSE
    case_dir = os.path.abspath(argv[argv.index("--case") + 1])
    g = load_grader()
    case = os.path.basename(case_dir)
    if case != g.CASE:
        print("REFUSE: %r is not this rung's registered case (%r)" % (case, g.CASE))
        return EXIT_REFUSE

    lga = g.read_exec(os.path.join(case_dir, "log.solve.legA"))
    lgb = g.read_exec(os.path.join(case_dir, "log.solve.legB"))
    ok, bad = g.rule4(case_dir, case, lga, lgb)
    if not ok:
        print("NO MARKER for %s -- rule 4 incomplete: %s" % (case, "; ".join(bad)))
        return 1

    p = os.path.join(HERE, "DONE.%s" % case)
    with open(p, "w") as fh:
        fh.write("case=%s\n" % case)
        fh.write("rung=T25R6c-R2\n")
        fh.write("registration=docs/campaigns/T-family/T25R6cR2_PREREGISTRATION.md\n")
        fh.write("rule4=COMPLETE (all conjuncts, both legs, age guard vs 0/module/T)\n")
        fh.write("registered_steps=%d legA + %d legB\n" % (g.N_A, g.N_B))
        fh.write("endTime_legA=%g endTime_legB=%g\n" % (g.ENDTIME_A, g.ENDTIME_B))
        fh.write("exec_s_legA=%.2f exec_s_legB=%.2f\n"
                 % (lga["exec_at"][g.N_A], lgb["exec_at"][g.N_B]))
        fh.write("exec_s_basis=CPU TIME (user+system, rank 0), NOT wall -- "
                 "OpenFOAM-v2606 TimeIO.C:631 -> cpuTimePosix -> times(2)\n")
        fh.write("finished_utc=%s\n"
                 % datetime.datetime.now(datetime.timezone.utc)
                 .strftime("%Y-%m-%dT%H:%M:%SZ"))
        fh.write("grader_sha256=%s\n" % g.sha256_of(GRADER))
        fh.write("completion_definition=IMPORTED from grade_t25R6cR2.rule4; "
                 "not retyped\n")
        fh.write("this_marker_is_not_a_verdict=rule 4 is COMPLETION, not grading. "
                 "G-R2-1 and G-R2-2 are not evaluated here.\n")
    print("DONE %s -> %s" % (case, p))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
