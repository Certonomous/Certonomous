# Rung 3 restart challenge — the adversarial defense of my own ceiling claim: PRE-REGISTRATION

Filed 2026-08-10 by the DAFoam solver agent, chief-approved. **This arm exists to try to break a
finding I just reported.** The rung-3 result (`834574a6`) claims a conditioning ceiling between
42,120 and 79,560 cells. Before that hardens, its sharpest available challenge must be run:
**a ceiling that a restart parameter removes is not a conditioning ceiling, it is a Krylov-budget
artifact** — and this family has twice refused to call a budget a wall (rung 2's `-3`; the sub-LU
memory death). It would be inconsistent to accept a wall here without trying the one lever whose
mechanism matches the failure. Committed BEFORE compute.

## 1. The mechanism being tested

Rung 3's CD solve stagnates at ~1.6152e−02 with `gmresRestart 200`, crossing **20 restart
boundaries** in 4,000 iterations. Restarted GMRES discards its entire Krylov subspace at each
restart; if the search directions that would reduce this residual live beyond a 200-vector
window, the method cannot find them no matter how many iterations it burns — and
**stagnation-at-flat is exactly what a repeatedly-reset GMRES looks like in that situation**.
The stagnation would then be an artifact of the restart budget, not a property of the operator.

Supporting prior: `gmresRestart 200 → 1000` (L2) was a material winner at rung 1 (−15.5% CD /
−20.1% CL iterations, `3ac8257e`), so the lever demonstrably does work on this operator family.

## 2. The lever, and the memory arithmetic (why this is affordable where Richardson was not)

**`gmresRestart: 200 → 1000`** (5x the window). Everything else identical to the stage-1 arm.

Memory: the adjoint state vector is ~6 unknowns per cell plus one per internal face —
79,560 x 6 + 235,386 ≈ **713,000 unknowns**, i.e. ~5.7 MB per Krylov vector in double precision.
- restart 200: 200 x 5.7 MB ≈ **1.14 GB**
- restart 1000: 1000 x 5.7 MB ≈ **5.7 GB**
- **predicted increase ≈ +4.6 GB**

Stage 1 peaked at **11.65 GiB against a 22 GiB cap** with 10.35 GiB spare, so the predicted peak
is **~16.3 GiB — under the cap with ~5.7 GiB still spare**, and the host carries ~29 GB free.
This is precisely the trade Richardson could not offer: Richardson bought its iteration cut with
no memory and then collapsed at a restart boundary, whereas this lever spends memory rung 3
measurably has. Cap held at `--memory=22g`; the standing memory guard applies (stop and report
if the container approaches the cap or host MemAvailable falls below 6 GB — and a memory death
is NOT EVALUABLE, never a conditioning verdict).

## 3. Iteration cap — bounded so it cannot repeat the 4,000-iteration burn without new information

**`gmresMaxIters: 1200`** (stage 1 used 4,000), chosen because the decisive information arrives
early and the design makes that explicit: **with restart 1000, the first 1,000 iterations are a
SINGLE uninterrupted Krylov cycle with no restart at all.** That is the cleanest possible test of
the hypothesis — if a 1,000-vector window contains the directions a 200-vector window discards,
the residual must fall materially below the stagnation plateau *within that first cycle*. Running
past ~1,200 buys nothing this arm needs: the answer is visible at iteration 1,000, and 200 more
carry it just past the first restart to show whether a restart destabilises it (the stage-0
signature). A negative result at 1,200 does not become positive at 4,000 — the plateau is flat.

## 4. The comparison baseline, fixed now from stage 1's own log (so it cannot be chosen later)

Stage-1 CD residuals, `gmresRestart 200`, quoted before this arm runs:

| iteration | 200 | 500 | 900 | **1000** | 1300 | 4000 |
|---|---|---|---|---|---|---|
| residual | 1.618871466028e−02 | 1.615395949809e−02 | 1.615249565219e−02 | **1.615247229756e−02** | 1.615246604817e−02 | 1.615245992220e−02 |

**The graded checkpoint is iteration 1000: 1.615247229756e−02** (initial residual
2.121343646203e−02; total reduction to that point, 1.31x).

**CD is the graded solve.** CD is what stagnated; CL was never attempted in stage 1. Under a
1,200 cap CL cannot converge even on the healthy trend (its baseline requirement is larger), so
**CL's outcome under this arm is reported but NOT graded**, and its failure will not be read as
evidence either way. Stated now so it cannot be leaned on afterwards.

## 5. Outcome mapping — three branches, equally weighted, written before the result

- **A — CONVERGES** (CD `PetscConvergedReason: 2`): **the ceiling claim is WITHDRAWN.** The
  rung-3 record is corrected at its source to say **"restart-budget-limited above 42,120 cells"**
  — a better and cheaper finding than a wall, because it is a fixable one: it would mean the
  ladder continues upward with a one-token change and the "ceiling between 42,120 and 79,560
  cells" sentence must be struck, not softened. I would also owe the record an explanation of why
  rung 3's `-3` fooled the pre-registered budget-vs-wall test that rung 2's `-3` passed.
- **B — STAGNATES the same way** (CD residual within 10x of the 1.615247e−02 checkpoint at
  iteration 1000, or flat thereafter): **the conditioning ceiling survives its sharpest available
  challenge and hardens.** A 5x Krylov window changing nothing is strong evidence the directions
  are not being discarded — they are not there. The bracket (42,120–79,560 cells) stands as
  reported.
- **C — PARTIAL: materially more descent, no convergence.** Pre-stated because it is the likeliest
  outcome and the most open to motivated reading, so the bar is fixed now: **material = the CD
  residual at iteration 1000 is at least 10x below the baseline checkpoint (i.e. ≤ 1.615e−03).**
  - If material-but-not-converged: **the ceiling claim is NOT withdrawn and NOT hardened.** It is
    reclassified as **"restart-sensitive but not restart-removable"**: the wall moves under
    Krylov budget, so it is not purely a property of the operator, but a 5x window does not clear
    it. The follow-up that would settle it (restart 2000, ~11.4 GB of Krylov vectors — at the
    edge of this cap and needing a bigger box) is named, not run.
  - If the improvement is **below** the 10x bar (a 2x–5x nudge): that is **branch B, not branch
    C.** A wall that yields a factor of two to a fivefold Krylov window is still a wall, and I am
    fixing that reading now rather than after seeing the number.

## 6. Proofs, mechanics, price

Required in-log before any number counts: `transonicPCOption 1;`, **no** sub-LU banner,
**`GMRES Restart: 1000`**, `GMRES Max Iterations: 1200`, and a cold start from uniform. Staged
copy (guidelines §8) so stage 1's case stays as the record it is; `decomposePar -force` from the
pristine serial `0/`; launcher `lever_echo.txt` declares, the solver's DAOption/KSP dump confirms;
setsid + `.t0/.rc/.t1` ledger; polled inline with **explicit handoff naming container, ledger and
log path if it outlives the turn.**

**Price, from the measured rung-3 basis:** stage 1 ran 4,000 CD iterations in 1,265 s of solve
time = 0.316 s/iteration at restart 200. Orthogonalisation cost grows with the subspace, and the
average subspace over a 1,000-cycle is ~5x larger, so ~0.7–0.9 s/iteration is expected: **1,200
iterations ≈ 840–1,080 s, plus ~150 s primal/PC setup ≈ 16–20 min wall ≈ 66–82 core-min.** That
is the honest price of defending the claim, and it is bounded by §3's cap by construction.
