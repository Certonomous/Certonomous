#!/usr/bin/env python3
"""T25R6c COMPLETION MARKER -- DEFAULT-DENY.

Writes `DONE.<CASE>` only when rule 4 holds in FULL, and the rule-4 definition is
IMPORTED FROM THE FROZEN GRADER rather than retyped, so there is exactly ONE
definition of completion in this rung.  A retyped guard is a new guard, and a new
guard is unproven no matter how carefully it was copied.

WHY THE MARKER MATTERS BEYOND BOOKKEEPING: scripts/check_comparator_freeze.py
dates a comparator's freeze against the EARLIEST completion marker of the cases
it grades.  A marker saying "done" about a case that is not done would corrupt
every freeze judgment later dated against it.  So an incomplete case gets NO
marker at all -- never a marker with a caveat inside it.

    python3 mark_done_t25R6c.py --case <abs case dir>
"""
import datetime
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GRADER = os.path.join(HERE, "grade_t25R6c.py")
EXIT_REFUSE = 2


def load_grader():
    if not os.path.isfile(GRADER):
        print("REFUSE: the frozen grader is absent: %s" % GRADER)
        sys.exit(EXIT_REFUSE)
    spec = importlib.util.spec_from_file_location("grade_t25R6c", GRADER)
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
        fh.write("rule4=COMPLETE (all conjuncts, both legs, age guard vs 0/module/T)\n")
        fh.write("finished_utc=%s\n"
                 % datetime.datetime.now(datetime.timezone.utc)
                 .strftime("%Y-%m-%dT%H:%M:%SZ"))
        fh.write("grader_sha256=%s\n" % g.sha256_of(GRADER))
        fh.write("completion_definition=IMPORTED from grade_t25R6c.rule4; not retyped\n")
    print("DONE %s -> %s" % (case, p))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
