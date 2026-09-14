#!/usr/bin/env python3
"""D6R3 MP_R4 STAGER -- THREE registered edits to a COPY of the frozen producer.  Refuses anything else.

EDIT 1 (adjoint): jacMatReOrdering "natural" -> "rcm".  KEPT -- MEASURED load-bearing in MP_R2/MP_R3:
  MP_R1 with "natural" died at Main iteration 1 with PetscConvergedReason -9 (DIVERGED_NANORINF);
  with "rcm" the NaN is gone and the KSP iterates.

EDIT 1b (adjoint, THE RUNG-4 CHANGE): asmOverlap 1 -> 2, with pcFillLevel LEFT AT THE PUBLISHED 1.
  The published tutorial does not set asmOverlap, so it takes DAFoam's default of 1
  (pyDAFoam.py:528).  This is an INSERTION, not a replacement.
  WHY THIS LEVER AND NOT MORE FILL: the weakness in a 20-way decomposition is the coupling BETWEEN
  ASM subdomains, and overlap is the parameter that addresses it directly.  Its memory cost is
  LINEAR IN THE HALO, unlike pcFillLevel, for which DAFoam's own docstring warns "the memory usage
  generally grows exponentially" (DALinearEqn.C:59-62).  DAFoam's docstring for overlap
  (DALinearEqn.C:50-52): "ASM overlap for solving the linearEqn in parallel. Usually set it to 1.
  Setting a higher number increases the convergence but significantly increase the memory usage."
  MEASURED EVIDENCE THAT RUNG 4 IS NEEDED, from MP_R2b (rcm + pcFillLevel 1) at 20 ranks:
      iteration    0: 1.947952423304e-03
      iteration 1500: 1.658369814130e-03
      0.06990 decades over 1500 iterations = 0.004660 decades / 100 iterations
      governing bar = 1e-04 x initial = 1.947952e-07 (gmresTolDiff 1.0e2 relaxing rtol 1e-6,
        DALinearEqn.C:424-429, pyDAFoam.py:536) -- NOT the banner's 1e-06
      decades still needed: 3.9301  ->  84,341 iterations at this rate, against a 2000 cap
  Fill level 1 is therefore MEASURED to fail by a factor of ~42x, not projected to.
  This RESTORES DAFOAM'S OWN DEFAULT.  pyDAFoam.py:530 sets "jacMatReOrdering": "rcm" as the
  default; CRM_Wing/runScript.py:66 is the PUBLISHED OVERRIDE to "natural" (= no reordering,
  the worst case for ILU fill-in and pivot stability).  DALinearEqn.C:275-305 handles "rcm" as
  MATORDERINGRCM, and an unrecognised string falls back SILENTLY to nested dissection -- which is
  why the runtime block must be read back (L-40).
  Declared NEXT RUNG if this does not hold: pcFillLevel 1 -> 2.  NOT applied here; one change at a
  time, so the acting change is identifiable.

EDIT 2 (hot start): seed aoa0 per condition from the CONVERGED trim of MP_R1.
  An INITIAL-CONDITION change, not a physics change.  findFeasibleDesign stays in the loop, so the
  trim still converges from the warm start rather than being skipped.

usage: d6r3_mp_stage_r2.py <frozen_producer> <staged_output>
"""
import hashlib
import sys

FROZEN_MD5 = "efc3e62699690edd32e4ee910aad09c8"

E1_OLD = '        "jacMatReOrdering": "natural",\n'
# asmOverlap is ABSENT from the published file (default 1), so rung 4 INSERTS it beside pcFillLevel.
E1B_OLD = '        "pcFillLevel": 1,\n'
E1B_NEW = '        "pcFillLevel": 1,\n        "asmOverlap": 2,\n'
E1_NEW = '        "jacMatReOrdering": "rcm",\n'

E2_ANCHOR = 'RUN_DIRS = {"cl04": "mp04", "cl05": "mp05", "cl06": "mp06"}\n'
E2_BLOCK = (
    'RUN_DIRS = {"cl04": "mp04", "cl05": "mp05", "cl06": "mp06"}\n'
    '# MP_R4 HOT START -- the CONVERGED trim of MP_R1, an INITIAL CONDITION and not a physics change.\n'
    '# MP_R1 FindFeasibleDesign Iter 2: DesignVars [1.32496937 2.11023869 2.88211463]\n'
    '#                                  Constraints [0.39999898 0.50000009 0.59999612]\n'
    '#                                  Residual Norm 6.950287052456217e-06 -> Converged (tol 1e-4)\n'
    'AOA0_HOTSTART = {"cl04": 1.32496937, "cl05": 2.11023869, "cl06": 2.88211463}\n'
)
E2B_OLD = '            self.dvs.add_output("patchV_" + pt, val=np.array([U0, aoa0]))\n'
E2B_NEW = '            self.dvs.add_output("patchV_" + pt, val=np.array([U0, AOA0_HOTSTART[pt]]))\n'


def main(src, dst):
    raw = open(src).read()
    got = hashlib.md5(raw.encode()).hexdigest()
    if got != FROZEN_MD5:
        print("REFUSE: producer md5 %s, frozen %s" % (got, FROZEN_MD5)); return 10
    for name, s in (("E1_OLD", E1_OLD), ("E1B_OLD", E1B_OLD), ("E2_ANCHOR", E2_ANCHOR), ("E2B_OLD", E2B_OLD)):
        if raw.count(s) != 1:
            print("REFUSE: %s occurs %d times, expected 1" % (name, raw.count(s))); return 10
    if '"asmOverlap"' in raw:
        print("REFUSE: the frozen producer already sets asmOverlap"); return 10
    if '"rcm"' in raw or "AOA0_HOTSTART" in raw:
        print("REFUSE: the frozen producer already carries a staged edit"); return 10

    out = raw.replace(E1_OLD, E1_NEW).replace(E1B_OLD, E1B_NEW).replace(E2_ANCHOR, E2_BLOCK).replace(E2B_OLD, E2B_NEW)
    open(dst, "w").write(out)

    # ASSERT the diff is EXACTLY the two registered edits: 2 lines changed, 5 lines added
    a, b = raw.split("\n"), out.split("\n")
    added = len(b) - len(a)
    if added != 6:
        print("REFUSE: %d lines added, expected 6 (5 hot-start + 1 asmOverlap)" % added); return 10
    changed = [i for i in range(min(len(a), len(b))) if a[i] != b[i]]
    # READ-BACK: the values the solver will actually read
    body = out.split("daOptions = {")[1].split("\n}")[0]
    if '"jacMatReOrdering": "rcm",' not in body:
        print("REFUSE: rcm not readable back from the staged daOptions"); return 10
    if '"natural"' in body:
        print("REFUSE: natural still present in the staged daOptions"); return 10
    for k in ('AOA0_HOTSTART = {"cl04": 1.32496937, "cl05": 2.11023869, "cl06": 2.88211463}',
              'val=np.array([U0, AOA0_HOTSTART[pt]])'):
        if k not in out:
            print("REFUSE: %s not readable back" % k); return 10
    if '"pcFillLevel": 1,' not in body:
        print("REFUSE: pcFillLevel must remain at the published 1 in MP_R4"); return 10
    if '"asmOverlap": 2,' not in body:
        print("REFUSE: asmOverlap 2 not readable back from the staged daOptions"); return 10
    if '"primalMinResTolDiff"' in body or '"primalFuncStdTol"' in body:
        print("REFUSE: a forbidden key is assigned in the staged daOptions"); return 10
    print("D6R3_MPR4_STAGE OK src md5=%s -> %s  (+%d lines, %d changed lines)" % (got, dst, added, len(changed)))
    print("D6R3_MPR4_STAGE READBACK jacMatReOrdering=rcm (DAFoam default, pyDAFoam.py:530); "
          "pcFillLevel=1 UNCHANGED (published); asmOverlap=2 (default 1, pyDAFoam.py:528); AOA0_HOTSTART=[1.32496937, 2.11023869, 2.88211463]; "
          "primalMinResTolDiff UNSET; primalFuncStdTol ABSENT")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
