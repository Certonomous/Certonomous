#!/usr/bin/env python3
"""
mark_done_t21.py -- turn T21 STATUS files into DONE markers, under a rule the
runner does not itself apply (the mark_done_t3.py / mark_done_t1b_L4.py form;
rationale there and in L-143).

REGISTERED BY docs/campaigns/T-family/T21_PREREGISTRATION.md S6, which states
CLAUDE.md rule 4 in its steady form for a two-SOLID-region case.  Pinned by
sha256 in that document's AMENDMENT 3.

A case is DONE here only if ALL SIX conjuncts hold -- rule 4 is all-or-nothing
and this script REFUSES rather than degrades:

  1. STATUS.<case> exists INSIDE the case directory and reports rc=0.
     (Inside, not beside: the frozen comparator reads it at
     analyse_t21.py:370 as os.path.join(case_dir, "STATUS."+basename).)
  2. log.solve carries EXACTLY ONE OpenFOAM "End" line.  Exactly one, not at
     least one: a second End is a restart that replayed part of the run.
  3. the last written time directory == controlDict endTime (registered 3000).
     S6.1: there is NO residualControl, so a short run is not a converged run,
     it is a different experiment that exited cleanly -- the T19 corpse.
  4. that time directory carries T and p in BOTH regions, core and housing.
     The thermal family's list `T U p_rgh alphat nut k omega phi` DOES NOT
     APPLY (S6 conjunct 4): there is no fluid region and those fields must not
     exist.  betavSolid is optional and is not required.
  5. the number of ExecutionTime lines == endTime (deltaT 1, so
     round(endTime/deltaT) == endTime -- the historical unit-step case).
  6. THE AGE GUARD: every one of those fields is NEWER than the case's own
     0/housing/T, which launch_t21.sh touches LAST when it arms 0/ from
     0.orig/.  0/housing/T dates the run that was ALLOWED to produce the
     answer; only file age separates a fresh answer from one a previous run
     left behind at the same absolute path (L-143).

PHYSICS / INFRASTRUCTURE SPLIT (Sanaa's universal rule 2026-08-26, L-342):
bookkeeping never voids physics.  checkmesh_rc, the postProcess pass and the
S7.4 contention disclosure are INFRASTRUCTURE: they are REPORTED beside each
case and they NEVER decide DONE.  The six conjuncts above are the whole test.

This script never retracts: an existing DONE.<case> is left alone.  It writes
DONE.<case> in the T21_runs root (where a reader lists the family) and exits 1
if any requested case is not done, 2 on a refusal.

Usage:  python3 mark_done_t21.py [--root DIR] [case ...]
"""
import argparse
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))

# S8.1, the six registered cases, in registered order.
CASES = ["T21_CYL_c", "T21_CYL_m", "T21_CYL_f",
         "T21_CYL_W1", "T21_CYL_P1000", "T21_CYL_S10"]
CASES_BASELINE = tuple(CASES)            # rule 14 baseline
REGIONS = ("core", "housing")            # S6 conjunct 4
NEEDED = ("T", "p")                      # S6 conjunct 4 -- exactly these
END_TIME_REG = 3000                      # S8.1


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(2)


def cases_intact_or_refuse():
    """RULE 14 at every call site: the case list is inserted, never silently
    reduced.  A case dropped here would mark a partial set complete."""
    for c in CASES_BASELINE:
        if c not in CASES:
            refuse("rule 14: registered case %r removed from CASES" % c)


def control_end_time(d):
    p = os.path.join(d, "system", "controlDict")
    if not os.path.isfile(p):
        return None
    m = re.search(r"^\s*endTime\s+([0-9.eE+-]+)\s*;", open(p).read(), re.M)
    return float(m.group(1)) if m else None


def infrastructure(case_dir, case):
    """REPORTED, never decisive (L-342)."""
    out = []
    st = os.path.join(case_dir, "STATUS.%s" % case)
    if os.path.isfile(st):
        s = open(st).read()
        for k in ("core_min", "point_core_min", "cap_exceeded",
                  "checkmesh_rc", "load1_at_launch", "calibration_admissible"):
            m = re.search(r"^%s=(\S*)" % k, s, re.M)
            if m:
                out.append("%s=%s" % (k, m.group(1)))
    pp = os.path.join(case_dir, "POSTPROCESS.%s" % case)
    if os.path.isfile(pp):
        m = re.search(r"^rc=(\S+)", open(pp).read(), re.M)
        out.append("postprocess_rc=%s" % (m.group(1) if m else "?"))
    else:
        out.append("postprocess_rc=absent")
    return out


def check(root, case):
    """Return the list of failed conjuncts.  Empty list == DONE."""
    d = os.path.join(root, case)
    if not os.path.isdir(d):
        return ["no case directory"]
    fails = []

    # 1. rc = 0, from STATUS INSIDE the case directory
    st = os.path.join(d, "STATUS.%s" % case)
    if not os.path.isfile(st):
        return ["no STATUS.%s inside the case directory (the case never finished)" % case]
    s = open(st).read()
    m = re.search(r"^rc=(\S+)$", s, re.M)
    if not m:
        fails.append("STATUS has no rc= line")
    elif m.group(1) != "0":
        fails.append("STATUS rc=%s, not 0" % m.group(1))

    log = os.path.join(d, "log.solve")
    if not os.path.isfile(log):
        return fails + ["no log.solve"]
    body = open(log, errors="replace").read()

    # 2. EXACTLY ONE End line
    n_end = len(re.findall(r"^End\s*$", body, re.M))
    if n_end != 1:
        fails.append("%d 'End' lines in log.solve, expected exactly 1" % n_end)

    # 3. last time == endTime (and the dict's endTime == the registered one)
    et = control_end_time(d)
    if et is None:
        fails.append("no readable endTime in system/controlDict")
    elif abs(et - END_TIME_REG) > 0:
        fails.append("controlDict endTime %g != registered %d (S8.1)" % (et, END_TIME_REG))
    times = sorted((x for x in os.listdir(d)
                    if re.fullmatch(r"[0-9]+(\.[0-9]+)?", x) and float(x) > 0.0),
                   key=float)
    lt = times[-1] if times else None
    if lt is None:
        fails.append("no time directory beyond 0 -- nothing was written")
    else:
        if et is not None and abs(float(lt) - et) > 0:
            fails.append("last written time %s != endTime %g (S6.1: no "
                         "residualControl, so a short run is a DIFFERENT "
                         "experiment that exited cleanly)" % (lt, et))
        # 4. fields present: T and p in BOTH regions
        miss = [("%s/%s/%s" % (lt, r, f))
                for r in REGIONS for f in NEEDED
                if not os.path.isfile(os.path.join(d, lt, r, f))]
        if miss:
            fails.append("time %s is missing %s" % (lt, ",".join(miss)))
        else:
            # 6. THE AGE GUARD, against the case's OWN 0/housing/T
            zero_t = os.path.join(d, "0", "housing", "T")
            if not os.path.isfile(zero_t):
                fails.append("age guard: no 0/housing/T -- the launch cannot be "
                             "dated, so the answer cannot be attributed to it")
            else:
                t0 = os.stat(zero_t).st_mtime
                stale = [("%s/%s/%s" % (lt, r, f))
                         for r in REGIONS for f in NEEDED
                         if os.stat(os.path.join(d, lt, r, f)).st_mtime <= t0]
                if stale:
                    fails.append("age guard: %s NOT NEWER than 0/housing/T -- "
                                 "not written by this run (L-143)"
                                 % ",".join(stale))

    # 5. ExecutionTime count == endTime (deltaT 1)
    n_exec = len(re.findall(r"^ExecutionTime\s*=", body, re.M))
    want = int(et) if et is not None else END_TIME_REG
    if n_exec != want:
        fails.append("%d ExecutionTime lines, expected %d (deltaT 1)" % (n_exec, want))
    return fails


def selftest():
    """The strict rule is only worth what its failure modes are worth: each
    conjunct is shown to REFUSE a tree that violates it and only it."""
    import tempfile, shutil, time
    ok = [True]

    def chk(c, m):
        ok[0] = ok[0] and bool(c)
        print("  [%s] %s" % ("PASS" if c else "FAIL", m))

    root = tempfile.mkdtemp(prefix="t21_md_")
    case = "T21_CYL_c"

    def build_good():
        shutil.rmtree(os.path.join(root, case), ignore_errors=True)
        d = os.path.join(root, case)
        os.makedirs(os.path.join(d, "system"))
        open(os.path.join(d, "system", "controlDict"), "w").write(
            "endTime %d;\ndeltaT 1;\n" % END_TIME_REG)
        for r in REGIONS:
            os.makedirs(os.path.join(d, "0", r))
            for f in NEEDED:
                open(os.path.join(d, "0", r, f), "w").write("x\n")
        time.sleep(0.02)
        os.utime(os.path.join(d, "0", "housing", "T"), None)   # touched LAST
        time.sleep(0.02)
        for r in REGIONS:
            os.makedirs(os.path.join(d, str(END_TIME_REG), r))
            for f in NEEDED:
                open(os.path.join(d, str(END_TIME_REG), r, f), "w").write("x\n")
        open(os.path.join(d, "log.solve"), "w").write(
            "".join("ExecutionTime = %d s\n" % i for i in range(END_TIME_REG)) + "End\n")
        open(os.path.join(d, "STATUS.%s" % case), "w").write("case=%s\nrc=0\n" % case)
        return d

    try:
        d = build_good()
        chk(check(root, case) == [], "a complete tree is DONE (all six conjuncts)")

        open(os.path.join(d, "STATUS.%s" % case), "w").write("case=%s\nrc=1\n" % case)
        chk(any("rc=1" in f for f in check(root, case)), "conjunct 1: rc!=0 REFUSED")

        d = build_good()
        open(os.path.join(d, "log.solve"), "a").write("End\n")
        chk(any("'End' lines" in f for f in check(root, case)),
            "conjunct 2: a SECOND End line REFUSED (a replayed restart)")

        d = build_good()
        os.rename(os.path.join(d, str(END_TIME_REG)), os.path.join(d, "828"))
        chk(any("last written time" in f for f in check(root, case)),
            "conjunct 3: last time 828 != endTime REFUSED (the T19 corpse)")

        d = build_good()
        os.remove(os.path.join(d, str(END_TIME_REG), "core", "p"))
        chk(any("missing" in f for f in check(root, case)),
            "conjunct 4: a missing core/p REFUSED")

        d = build_good()
        open(os.path.join(d, "log.solve"), "w").write(
            "".join("ExecutionTime = %d s\n" % i for i in range(17)) + "End\n")
        chk(any("ExecutionTime lines" in f for f in check(root, case)),
            "conjunct 5: 17 ExecutionTime lines REFUSED")

        # conjunct 6 -- THE AGE GUARD, the one this file exists for
        d = build_good()
        old = os.stat(os.path.join(d, "0", "housing", "T")).st_mtime
        for r in REGIONS:
            for f in NEEDED:
                os.utime(os.path.join(d, str(END_TIME_REG), r, f), (old - 60, old - 60))
        fails = check(root, case)
        chk(any("age guard" in f for f in fails),
            "conjunct 6: fields OLDER than 0/housing/T REFUSED -- THE AGE GUARD FIRES")
        d = build_good()
        shutil.rmtree(os.path.join(d, "0"))
        chk(any("age guard" in f for f in check(root, case)),
            "conjunct 6: NO 0/housing/T at all REFUSED -- an undatable run is not done")

        # rule 14
        saved = list(CASES)
        CASES.remove("T21_CYL_f")
        try:
            cases_intact_or_refuse(); chk(False, "rule 14 should have refused")
        except SystemExit as e:
            chk(e.code == 2, "rule 14 REFUSES a dropped registered case (exit %s)" % e.code)
        CASES[:] = saved
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print("\nSELFTEST %s" % ("PASSED" if ok[0] else "FAILED"))
    return 0 if ok[0] else 1


def main():
    if "--selftest" in sys.argv:
        print("mark_done_t21 selftest -- RULE 4, ALL SIX CONJUNCTS, EACH SHOWN TO REFUSE")
        return selftest()
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=HERE)
    ap.add_argument("cases", nargs="*")
    a = ap.parse_args()
    cases_intact_or_refuse()
    root = os.path.abspath(a.root)
    want = a.cases or list(CASES)
    for c in want:
        if c not in CASES:
            refuse("%r is not one of the six registered T21 cases (S8.1)" % c)
    ok, bad = [], {}
    for c in want:
        f = check(root, c)
        (ok.append(c) if not f else bad.setdefault(c, f))
    for c in ok:
        marker = os.path.join(root, "DONE.%s" % c)
        if not os.path.exists(marker):
            open(marker, "w").write(
                "strict rule met -- CLAUDE.md rule 4, all six conjuncts "
                "(T21_PREREGISTRATION.md S6)\n")
    print("%d/%d T21 cases meet the strict completion rule" % (len(ok), len(want)))
    for c in ok:
        print("  DONE      %s   [infrastructure, non-decisive: %s]"
              % (c, "; ".join(infrastructure(os.path.join(root, c), c))))
    for c in sorted(bad):
        print("  NOT DONE  %s" % c)
        for r in bad[c]:
            print("            - %s" % r)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
