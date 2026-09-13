DIAGNOSTIC CONTROL -- NOT A GRADED RUN, NOT A RUNG, NO GATE READS THIS.

Purpose: bound the 4->16 rank RE-PARTITION on Cp, the quantity M6J actually grades.
ADDENDUM 2 sec.A2.3 registered that the resume perturbation would be read.  The force
coefficients were bounded from the 85-iteration double-computed overlap (Cd max
1.62e-04).  Cp could NOT be: the overlap window holds only per-iteration INTEGRALS
(forceCoeffs), residuals and clip counts -- no field data.  The 4-rank state stops at
t=3800 and the 16-rank run's first new write is t=4000, so there is no common written
time after the re-partition.

Method: this case carries the PRESERVED 4-rank decomposition at t=3800 (identical to
M6J_L1/processors_4rank_PRE_RERANK/) and advances it 3800 -> 4000 at 4 ranks, n (2 2 1).
M6J_L1 advanced the SAME t=3800 state 3800 -> 4000 at 16 ranks, n (2 2 4).  Comparing Cp
on the wing at t=4000 is then a clean one-change measurement: same physics, same schemes,
same solvers, same relaxation, 200 iterations -- ONLY the partition differs.

The ONLY dictionary change from the graded case is endTime 8000 -> 4000; fvSchemes,
fvSolution and decomposeParDict are asserted byte-identical above.

CORRECTION during staging: the first copy inherited M6J_L1's CURRENT decomposeParDict,
which ADDENDUM 2 changed to numberOfSubdomains 16 / n (2 2 4).  That is inconsistent with
this case's 4-rank processor directories.  Replaced with the REGISTERED 4-rank file
(system/decomposeParDict.4rank.registered, numberOfSubdomains 4, n (2 2 1)) and asserted
dict-count == processor-dir-count.  Caught by the staging assert, not by the solver.

REVISION, 2026-09-13T17:58Z -- TWO CHANGES, BOTH FORCED BY MEASUREMENT:

(1) THE COMPARISON TIME MOVED 4000 -> 4200.  The graded run's t=4000 was DESTROYED by
    its own `purgeWrite 2` before it could be reconstructed: at Time 4474 the run held
    only 3800, 4200 and 4400.  t=4200 and t=4400 were reconstructed to M6J_L1's TOP
    LEVEL, where purgeWrite does not reach, and are now safe.  4200 is the comparison.
    LESSON SHAPE: under purgeWrite N, any diagnostic comparison against a LIVE graded
    run must reconstruct the target time within N write intervals or it is gone.  There
    is no warning and no error -- the directory simply is not there.

(2) THE CONTROL IS RESTARTED AS ONE SEGMENT, 3800 -> 4200, discarding 42 completed
    iterations (22.27 core-min, ABORTED_PARTIAL.* files).  The first attempt would have
    stopped at endTime 4000 and resumed, putting a stop/restart INSIDE a control whose
    whole purpose is to measure the effect of a stop/restart.  Same-partition restart
    from a binary checkpoint should be exact, but "should be" is not a control, and the
    confound is removed rather than disclosed.  One segment, no seam.
