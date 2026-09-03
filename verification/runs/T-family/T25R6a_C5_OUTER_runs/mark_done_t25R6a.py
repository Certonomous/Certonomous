#!/usr/bin/env python3
"""T25R6a COMPLETION MARKER -- rule 4, all conjuncts, and the DATED DONE marker.

Registration: docs/campaigns/T-family/T25R6a_PREREGISTRATION.md v1.1, section 7.5.

WHY THIS EXISTS AT ALL, STATED SO IT IS NOT MISTAKEN FOR BOOKKEEPING
--------------------------------------------------------------------
scripts/check_comparator_freeze.py judges a comparator by comparing its last
COMMIT time against the earliest COMPLETION MARKER of the cases it grades.  A
tree with no DONE.<CASE> marker gives it nothing to judge against, so it can
only report NO-MARKERS: an explicit, counted, UNJUDGED row.  A comparator with
no markers is not frozen -- it is unjudgeable.

verification/runs/T-family/T25R5_LINSOLVER_runs/ carries NO DONE.* marker at
all, so all three of its graders sit in exactly that unjudged state.  This file
is why T25R6a will not.

The marker carries `finished_utc=` because an mtime is a property of the
filesystem while `finished_utc` is a property of the RUN -- 87 of 156 markers in
this repository carry no such line and are dated only by mtime, which the
checker's --strict-markers mode correctly declines to trust.

RULE 4 IS NOT RE-IMPLEMENTED HERE.  It is imported from the frozen grader, so
there is exactly ONE definition of completion in this rung and the marker cannot
disagree with the verdict.

    python3 mark_done_t25R6a.py --case <abs case dir>
    python3 mark_done_t25R6a.py --all
"""
import datetime
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GRADER = os.path.join(HERE, "grade_t25R6a.py")
CASES = ["B0_L1", "C5_L1", "B0_L3", "C5_L3"]
EXIT_REFUSE = 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def grader():
    if not os.path.isfile(GRADER):
        refuse("the grader is absent: %s -- rule 4 is defined there and is not "
               "re-implemented here." % GRADER)
    spec = importlib.util.spec_from_file_location("grade_t25R6a", GRADER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def mark(case_dir, mod):
    case = os.path.basename(case_dir.rstrip("/"))
    if case not in CASES:
        refuse("%r is not a registered case of this rung" % case)
    log = mod.read_log(os.path.join(case_dir, "log.solve.legA"))
    ok, bad = mod.rule4(case_dir, case, log)

    started = finished = ""
    for nm, dst in ((".t.%s.start" % case, "started"), (".t.%s.end" % case, "finished")):
        p = os.path.join(case_dir, nm)
        if os.path.isfile(p):
            v = open(p).read().strip()
            if dst == "started":
                started = v
            else:
                finished = v
    if not finished:
        # An mtime is a property of the FILESYSTEM.  If the run did not stamp
        # itself, say so in the marker rather than silently substituting one.
        finished = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ")
        basis = "marker-write time (the run wrote no .t.%s.end stamp)" % case
    else:
        basis = "the run's own .t.%s.end stamp" % case

    path = os.path.join(case_dir, "..", "DONE.%s" % case)
    path = os.path.abspath(path)
    if not ok:
        # DEFAULT-DENY: an incomplete case gets NO completion marker.  A marker
        # that says "done" about a case that is not done would corrupt every
        # freeze judgment that later dates itself against it.
        print("NOT MARKED  %s -- rule 4 incomplete: %s" % (case, "; ".join(bad)))
        return 1

    with open(path, "w") as f:
        f.write("finished_utc=%s\n" % finished)
        f.write("finished_utc_basis=%s\n" % basis)
        f.write("started_utc=%s\n" % (started or "(unstamped)"))
        f.write("case=%s\n" % case)
        f.write("rung=T25R6a\n")
        f.write("registration=docs/campaigns/T-family/T25R6a_PREREGISTRATION.md v1.1\n")
        f.write("registered_steps=%d\n" % mod.STEPS)
        f.write("endTime=%s\n" % mod.ENDTIME)
        f.write("exec_s=%s\n" % (log["exec_s"] if log else "n/a"))
        f.write("strict rule met (all conjuncts, including the age guard against "
                "the case's own 0/module/T)\n")
    print("MARKED      %s -> %s  (finished_utc=%s)" % (case, path, finished))
    return 0


if __name__ == "__main__":
    mod = grader()
    if "--all" in sys.argv:
        rc = 0
        for c in CASES:
            d = os.path.join(HERE, c)
            if os.path.isdir(d):
                rc |= mark(d, mod)
        sys.exit(rc)
    if "--case" not in sys.argv:
        print(__doc__)
        sys.exit(EXIT_REFUSE)
    sys.exit(mark(sys.argv[sys.argv.index("--case") + 1], mod))
