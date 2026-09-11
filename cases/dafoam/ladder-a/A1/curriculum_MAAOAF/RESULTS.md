# MAAOAF — RESULTS. **`potentialFoam` INITIALISATION IS THE ONLY ARM THAT CLEARS ITERATION 1. IT MOVES CLIP ONSET FROM ITERATION 1 TO ITERATION 167 — NECESSARY, AND NOT SUFFICIENT.**

Frozen `3e2257590e88e196cfb42658059e8837110b173a` (+ ADDENDUM 1 `266f34bfc`). Four arms, MA288, 130,304 cells, np=1, `endTime 500`, `printInterval 1`, image `dafoam-idwarp-rot:v1` @ `sha256:2927768a…`. Graded by frozen `grade_maaoaf.py` (md5 `0b81bdef8ab595e7901612f7908f44a2`), all four exit 0, both planted-control directions live on every log.

| arm | one change | **first clip** | clips @t1 / t10 / t50 | total clips | ended | verdict |
|---|---|---|---|---|---|---|
| R0 | none — reproduce | **Time = 1** | 2 / 9 / 5 | 3748 `{p 928, U 1184, rho 689, e 947}` | Time = 500 | `NOT A RESULT` |
| N1 | `primalVarBounds` widened | Time = 1 | 1 / 0 / 0 | 8 | **died Time = 8** | `NOT A RESULT` |
| **N2** | **`potentialFoam -writePhi`** | **Time = 167** | **0 / 0 / 0** | 1021 `{p 411, U 150, rho 118, e 342}` | Time = 500 | `NOT A RESULT` |
| N3 | `div(phi,U)` → bounded upwind | Time = 1 | 2 / 8 / 3 | 3466 | Time = 500 | `NOT A RESULT` |

**ALL FOUR FAIL `G-BOUND`, which requires ZERO clips. None converged, and none is rescued.** The result is the **discrimination**, not a pass.

**1. N2 CONFIRMS THE DIAGNOSIS.** The registered cause was initialisation: `p` clips in the very first SIMPLE pressure solve from a uniform freestream start. `potentialFoam` — **already wired into `fvSolution` as `potentialFlow{nNonOrthogonalCorrectors 20;}` with a `Phi` solver, and never invoked** — gives that solve a sane starting field. **Clip onset moves from iteration 1 to iteration 167, with ZERO clips through iteration 100.** No other arm clears iteration 1. Total clips fall 3.7×.

**2. AND IT IS NOT SUFFICIENT, which the arm's own numbers say plainly.** N2's clipping resumes at 167 and grows — t200 1, t300 4, t400 3, t500 9 — ending with `p initRes 0.617`, `he initRes 0.201` and cumulative continuity **45.45**. **Fixing the start does not fix the solve.** A successor must address what degrades from ~167 onward, and this ladder does not identify it.

**3. N1's PREDICTION IS CONFIRMED, AND ITS MECHANISM IS SHARPER THAN PREDICTED — I HAD IT WRONG FIRST.** Predicted: widening the bounds fails, worse than R0. Measured: died at `Time = 8`. **I first read its `rc=134` as an FPE. That was wrong, and I read the exit code instead of the log.** The log gives a `FOAM FATAL ERROR` from the thermophysical model itself: **`Negative initial temperature T0: -1039.448985413342`**, at `thermoI.H:57`, exiting via `Foam::error::simpleExit` → abort → signal 6 → 134. **Not a floating-point trap — a controlled refusal by the thermo model.** The bounds were the only thing keeping the energy field physical, and removing them sent `T` negative.

**4. N1 IS ALSO `N-D45`'s SHAPE IN A NEW PLACE, AND IT IS WHY THE MATCHED-ITERATION RULE MATTERS.** N1's clip count is **8 — by far the lowest of the four — and it is the worst arm.** Its clips fall to **zero** at t10 and t50 because the field had gone non-finite, not because it was healthy. **On total clips N1 looks best; on survival it looks catastrophic; only the rate at matched iterations reads it correctly.** (Rule adopted from cfd, whose CRM ladder measured two identical configurations dying at iterations 20 and 324 under MPI reduction-order non-determinism.)

**5. N3's PREDICTION IS CONFIRMED — a registered NEAR-NULL that behaved as registered.** Predicted partial and explicitly **not** clearing iteration 1, since `U` clips only at `Time = 100`, after `p`. Measured: still 2 clips at `t1`, identical to R0; total down only 7.5 %.

**6. cfd's "THE LOWER CLAMP FIRES FIRST" DOES NOT TRANSFER TO THIS CASE.** On MA288 **both `p` clamps fire in the SAME `Time = 1` block** — `p<500000` then `p>20000`. The first pressure solve produces a field exceeding **both** bounds at once, **so no bound tuning can fix it** — which is independently why N1 failed and why the initialisation arm is the one that moved.

**COST:** 9.950 + 1.117 + 8.117 + N2's arm, all within the per-arm 15.0 cap and the 60.0 item cap. `$` **derived at $0.0513/core-h, not measured.**

**WHAT THIS DOES NOT ESTABLISH.** The six compressible sweep points are **not** re-run and their `NOT A RESULT` stands. Whether `potentialFoam` initialisation plus a further fix makes them gradeable is **UNMEASURED**. **No sweep report will be written until it has points that converged.**
