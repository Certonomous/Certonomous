#!/usr/bin/env python3
"""F28 -- CORROBORATING CHANNEL: p's GATING first-solve initial residual trend.

EVIDENCE, NOT THE ARBITER.  PRECOMMITTED_READINGS.md section 4 is explicit that
this channel may not overturn the reading selected by the absolute criterion.

WHICH OF THE TWO p SOLVES.  With `nNonOrthogonalCorrectors 1` the SIMPLE loop
runs the pressure equation TWICE per outer iteration.  THE GATING QUANTITY IS
THE FIRST.  Two earlier lanes read different ones and reached opposite
conclusions -- the second, corrector solve reads ~1e-3 and looks like healthy
convergence while the first is flat.  This reader takes solve #1 ONLY, and its
`--validate` proves it is reading solve #1 by reproducing the frozen file's
published baseline 0.3668997977 at iteration 15000, a figure that belongs to
solve #1 and NOT to solve #2 (which reads 1.368988259e-03 there).  The two are
two orders of magnitude apart, so agreeing with one falsifies reading the other.

Usage:  read_pres_trend_f28.py <case_dir> [--every 1500]
        read_pres_trend_f28.py --validate <baseline_case_dir>
"""
import os
import re
import sys

TIME = re.compile(r"^Time = (\d+)")
PSOLVE = re.compile(r"Solving for p,\s+Initial residual = ([0-9.eE+-]+)")
CONT = re.compile(r"time step continuity errors :.*sum local = ([0-9.eE+-]+)")

REF_ITER = 15000
REF_FIRST = 0.3668997977      # frozen file section 4, baseline, solve #1
REF_SECOND = 1.368988259e-03  # the DECOY: solve #2 at the same iteration
REF_CONT = 2.775360385e-04    # frozen file section 4, sum local at final iter


def scan(case_dir):
    """Return (first_solve, second_solve, sum_local, converged_lines)."""
    path = os.path.join(case_dir, "log.simpleFoam")
    if not os.path.isfile(path):
        raise SystemExit("REFUSE: no log.simpleFoam at %s" % path)
    first, second, cont = {}, {}, {}
    t = None
    n = 0
    converged = 0
    for ln in open(path, errors="replace"):
        m = TIME.match(ln)
        if m:
            t = int(m.group(1))
            n = 0
            continue
        if "SIMPLE solution converged" in ln:
            converged += 1
        m = PSOLVE.search(ln)
        if m and t is not None:
            n += 1
            if n == 1:
                first[t] = float(m.group(1))
            elif n == 2:
                second[t] = float(m.group(1))
            continue
        m = CONT.search(ln)
        if m and t is not None:
            cont[t] = float(m.group(1))
    if not first:
        raise SystemExit("REFUSE: no `Solving for p` lines found in %s" % path)
    return first, second, cont, converged


def validate(baseline_dir):
    print("READER VALIDATION -- prove it reads the GATING first p solve, not the")
    print("corrector.  The two are two orders apart, so agreeing with one")
    print("falsifies reading the other.")
    first, second, cont, conv = scan(baseline_dir)
    ok = True
    checks = [
        ("first-solve  @%d" % REF_ITER, first.get(REF_ITER), REF_FIRST, 1e-9),
        ("second-solve @%d" % REF_ITER, second.get(REF_ITER), REF_SECOND, 1e-11),
        ("sum local    @%d" % REF_ITER, cont.get(REF_ITER), REF_CONT, 1e-12),
    ]
    for name, got, want, tol in checks:
        good = got is not None and abs(got - want) <= tol
        ok = ok and good
        print("  %-22s published %-16.10g reader %-16s %s"
              % (name, want, "%.10g" % got if got is not None else "MISSING",
                 "AGREES" if good else "*** DISAGREES ***"))
    same = (first.get(REF_ITER) == second.get(REF_ITER))
    print("  the two solves are DISTINCT at %d: %s" % (REF_ITER, "no" if same else "yes"))
    ok = ok and not same
    print("  `SIMPLE solution converged` lines: %d (frozen baseline: none)" % conv)
    print("VALIDATION %s" % ("rc 0" if ok else "FAILED"))
    return 0 if ok else 2


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--validate":
        sys.exit(validate(args[1]))
    if not args:
        raise SystemExit(__doc__)
    case = args[0]
    every = 1500
    if "--every" in args:
        every = int(args[args.index("--every") + 1])
    first, second, cont, conv = scan(case)
    iters = sorted(first)
    print("case  %s" % case)
    print("p FIRST-solve (GATING) initial residual, sampled every %d iterations:" % every)
    print("  %8s  %16s  %16s  %16s" % ("iter", "p solve#1 (GATING)", "p solve#2 (decoy)",
                                       "cont sum local"))
    for t in iters:
        if t % every == 0 or t == iters[-1] or t == iters[0]:
            print("  %8d  %16.10g  %16s  %16s"
                  % (t, first[t],
                     "%.6g" % second[t] if t in second else "-",
                     "%.6g" % cont[t] if t in cont else "-"))
    lo, hi = first[iters[0]], first[iters[-1]]
    print("first %d -> last %d : %.6g -> %.6g   decay factor %.4g"
          % (iters[0], iters[-1], lo, hi, (hi / lo) if lo else float("nan")))
    print("`SIMPLE solution converged` lines: %d" % conv)
    print("CORROBORATING EVIDENCE ONLY -- this channel may NOT overturn the")
    print("reading selected by the absolute criterion.")
