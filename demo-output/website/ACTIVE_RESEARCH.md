# Active Research board

Live status per ladder, with measured numbers only. Every figure here is copied
from a solver output, a scored artifact, or a published leaderboard. Nothing is
estimated unless the row says so.

Created 2026-07-28 because no board of this name existed in the repository. If
an external board was intended instead, this file should be pointed at it — the
question is logged in the blockers list, and work did not wait on the answer.

Last updated: 2026-08-07 UTC (Ladder C — **round 5 is the entry of record:
overall 0.0566, rank 1 of 5 scored locally at benchmark commit `deb91557`**
— a local scoring, not an official placement; the untrained QCR2000 term
took the ducts under a rule frozen before any solve. Dated update paragraph
in the Ladder C section).

Update 2026-08-07 UTC: Ladder C — **round 5 (2026-08-07) is the entry of
record: overall 0.0566, locally rank 1 of 5** under the R5 pre-registration
(criterion overall < 0.065438 → ACCEPT); AR_14's nominal best-on-board tie
was lost as pre-accepted in writing (+0.0029) against −0.0731 on the two
Ret_360 ducts; the 6th cumulative scoring call. The round-4 paragraph below
is superseded and the new paragraph in Ladder C carries the numbers.

Update 2026-08-11 UTC: **Rank-1 companion (MANDATORY, chief ruling) —
RECOMPUTED AGAINST A SIX-ENTRY BOARD.** Any statement of rank 1 or of the
0.056647 headline, on any surface, carries these four clauses.

**P(rank 1) = 50%** — 50.2% over a 400,000-draw case-level bootstrap, and an
eight-case sample cannot pin it tighter than **0–97% at 95%** (double bootstrap).
**Frame:** the **six**-entry LIVE board fetched 2026-08-11T23:33Z by two
independent routes; eight cases; our 0.056647191704213645 read from
`closure_challenge_round5_qcr.json` at commit `07a7fe9e`.
~~**P(rank 1) = 68%**, 2–100% at 95%~~ — **STRUCK 2026-08-11: the previous figure
was computed 2026-08-10 against a FOUR-entry board that no longer exists.** Two
entrants have since appeared, one of them the new leader (Yang, 0.0580), and our
margin over Yang more than halved, 0.002878 → 0.001365.

**Four leads are now not statistically decided** — Yang (t = −0.19), Reissmann
(t = −0.50), Wu & Zhang (t = −0.95) and Tian, Buchanan, Hickel & Dwight
(t = −1.03); the leads over Liu and Montoya are decided (98.7%, 99.8%).
**The standing is three deletions wide** (~~two cases wide~~) — deleting any one
of `alpha_15_13929_4048`, `alpha_15_13929_2024` or `alpha_05_4071_4048` drops the
point rank to 2, 3 and 2 respectively; delete `NASA_2DWMH` and P(rank 1) rises to
78.5%. **`AR_1_Ret_360` and `AR_3_Ret_360` are ties below published precision**
(0.00003 and 0.00008) and are not per-case wins or losses. Source:
`campaign/PROBABILITY_OF_RANK_SIX_ENTRY_2026-08-11.md`; the superseded four-entry
computation is kept, not deleted, at `campaign/PROBABILITY_OF_RANK_2026-08-10.md`.
The figure may never appear without its interval **and its board**.

Update 2026-07-30 UTC: Ladder C — closure challenge submission policy
established, eligibility verdict recorded, compliance audit run; **both blocking
defects since cleared — the eight submission CSVs now exist and the false
docstring is corrected**. Ladder W5 — external challenge scouting sweep filed to
the docket.

Update 2026-08-01 UTC: Ladder A — the A1/A5 gradient defect is root-caused to a
source line and repaired in a **local** IDWarp patch, confirmed by repair; the
A1/A5 rows and the consolidated FD table below now carry the patched numbers
beside the stock ones. **The shipped toolchain still carries the bug; no stock
verdict changes.**

Update 2026-08-04 UTC: Ladder C — **round 4 (2026-07-31) is the entry of
record: overall 0.0654, rank 3 of 5**; the round-3 headline in the Ladder C
section below is superseded and the new paragraph there carries the numbers.
Ladder A — two results committed after the 2026-08-01 note: **A4's verdict
moves CONDITIONAL → PASS (2026-08-02)** — the published 10.04% was DAFoam's
default `scotch` decomposition on this mesh, not a gradient defect (1.10%
against the shipped toolchain at np=1 — the single graded configuration of
record per `dafoam/VERIFICATION_A4_decomposition_supervisor_sweep.md` W-3,
commit 27d25762 — 0.00054% patched under `simple` at
np=4; the decomposition alone closes 92% of the published error, the rotation
patch 11%, and the two defects factor — `dafoam/DAFOAM_CASE_STATUS.md`,
`PROOF.md` §25.5), **supervisor sweep CONFIRMED 2026-08-04** (`dafoam/VERIFICATION_A4_decomposition_supervisor_sweep.md`, commit 27d25762); and
**blocker B-7 is closed (2026-08-02)** — A2's 14% CD spread was a wrong-script
error (every W5 run invoked the aerostructural `runScript.py` where the
published numbers come from `runScript_AeroOnly.py`); from a pristine clone
the primal reproduces CD 0.02772949 / CL 0.4775877833 to all ten printed
digits, `check_totals` returns 18 of 18 rows identical to the published log,
and the regrade W5 could not run is done (CD/shape 1.71% → 0.0506%), so
**A2's PASS is now re-measured rather than asserted** (`PROOF.md` §25.1,
§25.1b).

---

## Headline result: the uncertainty machinery predicted a NASA model error before the run

On the NASA wall mounted hump, our model form uncertainty band contains the
documented reattachment error, and the prediction that it would was written
down before the runs executed.

The product thesis is that the lab bounds its own trust. This is that thesis
tested against a real, independently published model form bias, not against
our own numbers.

The scientifically serious part is what we found by auditing our own claim
rather than defending it. We first reported that the linear turbulence models
all cluster above the experimental value and that none reach it alone. That
held only while one of them sat short of its own convergence standard.
Converged, it crosses below the experiment and the narrow spread contains the
truth after all. Separately, two of the anisotropy corner runs turned out never
to have converged either, so the wide band they defined is withdrawn. What
remains is tighter than what we published and rests only on runs that met their
gate.

| Quantity | Value |
| --- | --- |
| Experiment reattachment x/c | 1.100 |
| Our baseline reattachment x/c | 1.2534, a +13.95% error |
| Inter model spread alone, all four models converged | 1.0722 to 1.2503, contains the experiment |
| Inter model spread as first reported, one model unconverged | 1.1299 to 1.2534, did not contain it |
| Full band, converged runs only | 1.0722 to 1.2534, contains the experiment |
| Full band as first published | 0.5278 to 1.2534, withdrawn: two corner runs never converged |
| Closest single check to experiment | 1.1437, +3.97% (k-epsilon) |

- The prediction was committed to the record before any of the runs that
  scored it.
- The band is wide, a factor of roughly 2.4. Containment is necessary. It is
  not sufficient on its own.
- The honest claim is that the machinery bounded a real published error and
  said so in advance, not that the uncertainty is tight.
- The ambition ahead is to tighten the band while it still holds the truth,
  and to test the same machinery against another independently documented
  case.

---

## Ladder A — DAFoam verification and reproduction

| Rung | Case | Status | Headline measured result |
| --- | --- | --- | --- |
| A1 | NACA0012 incompressible, official tutorial | **COMPLETE; ~~FD-verified~~ CD/shape FAIL against the shipped toolchain under the current standard (sign-flipped idx6); cause found and fixed in a local patch, 2026-08-01 — see note below the FD table** | CD 0.0209105, CL 0.4987653, 4,032 cells, 3.51 core-min. CD/CL wrt patchV, CL/shape and constraints pass; CD/shape carries a real sign-flipped component (idx6, 634% under the real seed) traced to IDWarp `vectorUtils.f90:58`. Patched-warp results, recorded beside the stock FAIL: idx6 → 5.54e-04% sign agreeing, idx0/idx1 11.92%/11.58% → 1.2e-05%, primal md5-identical. **Full-chain `check_totals` measured 2026-08-01, np=2, stock and patched back to back: CD/shape 11.43% → 0.03745%, CL/shape 1.671% → 0.01494%, every FD magnitude bit-identical between the two runs and the baseline primal converging to the same 9.646409714038222e-09** (`dafoam/W5_GRADIENT_REGRADE.md` §1). **Stock DAFoam/IDWarp 2.6.2 as shipped still carries the bug** |
| A2 | MACH tutorial wing (3D) | **COMPLETE, optimization run; ~~the FD verification is NOT currently re-runnable (2026-08-01)~~ *(superseded 2026-08-02: B-7 closed — the 14% spread was a wrong-script error, the published verification re-runs digit-for-digit and the regrade is done; PASS re-measured, see the 2026-08-04 update above)*** | CD 0.02772949, CL 0.47759, 38,304 cells; **28.28% drag reduction** at matched CL, time-boxed; 692.5 core-min. **The preserved case is post-optimisation**: its primal starts at CD 0.03142 against the published 0.02772949, a patched `check_totals` died at perturbation 132/211 with a DAFoam mesh-quality error after 238 core-min, and rebuilding the mesh from `preProcessing.sh` lands at 0.02964133 — a 14% spread across four solves of the same case, CL climbing 0.4776/0.4967/0.4999/0.5216. ~~**Measured on A2's own geometry: the corrected derivative is a bit-identical no-op for the 7 twist DVs** (analytic 2.020405e-03 and 2.266683e-02 unchanged), so CD/twist and CL/twist hold; the 96 local FFD shape DVs are the mode A1 shows the defect *does* reach, and they are unregraded.~~ *(Struck 2026-08-04, docket `w4-carry-the-warp-patch-to-the-blocked-rungs`: this cell went stale two days after the fact — the "no-op" was measured on the wrong (aerostructural) script, and the 96 shape DVs WERE regraded 2026-08-02 on the published aero-only case: CD/shape 1.71% → 0.0506%, CL/shape 1.17% → 0.0219%, CL/twist 1.12% → 0.0097%, CD/twist the one degrading row 0.389% → 0.505%, still deep in PASS — `W4-a2-provenance/a2_ao_{stock,patched}_checktotals.log`, re-parsed in `dafoam/W4_CARRY_TO_BLOCKED_RUNGS.md` §1. The stale cell propagated into a 180-core-min item brief; L-32's satellite-lag defect, caught by survey.)* `dafoam/W5_GRADIENT_REGRADE.md` §3, §3a, §3b |
| A3 | ONERA M6 transonic | **primal UNCONVERGED; adjoint blocked at every mesh size** | The primal plateaus at 1.02e-06 against its own 1e-08 tolerance and raises an explicit error, so CD 0.02299556 and CL 0.31311589 are uncertified. The Cp comparison was never evaluable -- the solver raises before writing a field. Adjoint returns a linear-solver breakdown at 21,840, 42,120, 79,560 and 99,840 cells, so mesh size is not the constraint; 127.5 core-min |
| A4 | Ahmed body 25 deg | **gradient ~~CONDITIONAL~~ → PASS *(superseded 2026-08-02: the 10.04% was the `scotch` decomposition, not the gradient — see the 2026-08-04 update above)*, supervisor sweep CONFIRMED 2026-08-04 (`dafoam/VERIFICATION_A4_decomposition_supervisor_sweep.md`, commit 27d25762); primal drag WITHDRAWN** | Gradient checked at 10.04% on a 2,777-cell mesh; re-run today on the shipped toolchain it reproduces exactly (analytic 0.21821, FD 0.24258, 10.04%), and re-run with the corrected `getRotationMatrix3d` derivative it moves only to **8.953%** — the FD unchanged at 0.24258, the baseline primal CD identical at 0.03125419. **About 11% of A4's gradient disagreement is the rotation defect; the other 89% has no identified cause**, unlike A1 and A5 where the same four lines collapse the error to FD-truncation level. ~~Grade stays CONDITIONAL (5–15% band) and the file's own unreconciled "PASS" wording is superseded.~~ *(Superseded 2026-08-02: the residual is identified — DAFoam's default `scotch` decomposition, an artifact independent of the gradient itself — and the verdict moves up to PASS, supervisor sweep CONFIRMED 2026-08-04 (`dafoam/VERIFICATION_A4_decomposition_supervisor_sweep.md`, commit 27d25762); `PROOF.md` §25.4–25.5.)* Evidence: `dafoam/W5_GRADIENT_REGRADE.md` §2, `dafoam/w5_regrade/a4_{stock,patched}_checktotals.tail.log`. The 45,760-cell primal that produced CD 0.06998 is withdrawn: its turbulence field diverged while its normalised residual read as converged, and the drag was computed from that state. Needs a re-run before any drag number is quoted; 10.9 core-min + 7.0 core-min regrade |
| A5 | U-bend internal flow | ~~running~~ *(stale cell, superseded)* **COMPLETE; FD verdict FAIL against the shipped toolchain; cause found and fixed in a local patch, 2026-08-01 — see note below the FD table** | 4,800 cells, ~26.0 core-min. FD aggregate 46.6%, 2 of 27 components sign-flipped (idx8 207.0%, idx17 121.6%) — root cause shared with A1: IDWarp `vectorUtils.f90:58` degenerate-rotation branch, real-seed solve-free reproduction component by component. Patched-warp results, recorded beside the stock FAIL: idx8/idx17 → 3.0e-06/7.0e-06 signs agreeing; all 27 stock-objective components rel_err 0.0000 (before-worst 80.79%); primal md5-identical. **Full-chain `check_totals` measured 2026-08-01 on the published pressure-loss configuration, np=4, stock and patched back to back: 46.6377% → 2.2372%** (analytic 1.938364e+01 → 3.350432e+01 against an FD of 3.340851e+01 identical in both, baseline TP1 2869.524210823638 identical in both and in the published log). A patched A5 would carry no flagged component and a 2.24% aggregate, inside the ≤5% PASS band — **but 2.24% is 60× A1's patched residual and is not explained**, and no shipped stack produces it (`dafoam/W5_GRADIENT_REGRADE.md` §4). **Stock DAFoam/IDWarp 2.6.2 as shipped still carries the bug** |
| A6 | CRM wing (wing-alone; DPW4 wing-body rejected on time-box grounds), transonic | **COMPLETE, converged primal, matches published tutorial baseline** | CD 0.0209014, CL 0.5000146, 579,072 cells, matches DAFoam's own published tutorial CD=0.02090 to 0.0067%; a raw temperature-residual figure at the same checkpoint is anomalously large and has not been cleared, so this row is provisional pending that check; adjoint not attempted (known-infeasible per A3, mesh 1.45x A3's OOM point); 38.4 core-min |

### Consolidated FD verification table (every adjoint rung)

| Rung | derivative | analytic vs FD, relative error |
| --- | --- | --- |
| A1 | geometric constraints wrt shape | **4.4e-14 to 1.4e-10** |
| A1 | CD wrt flow parameter | **0.232%** |
| A1 | CL wrt flow parameter | **0.232%** |
| A1 | CL wrt shape | **1.67%** |
| A1 | CD wrt shape | **11.43%** on the difference-vector norm, but the two gradient magnitudes agree to **0.451%**. **FAIL against the shipped toolchain** (sign-flipped idx6; 634% under the real seed). *Patched local IDWarp (2026-08-01), rotations ON, real seed: idx6 → 5.54e-04% sign agreeing; idx0/idx1 11.92%/11.58% → 1.23e-05%/1.26e-05%; idx7 1.31e-06%; idx4 1.47e-04%. Stock still fails* |

| A4 | CD wrt rear-slant shape | **1.10%** shipped at np=1 — the single graded configuration of record, per `dafoam/VERIFICATION_A4_decomposition_supervisor_sweep.md` W-3, commit 27d25762 — and **PASS** under the current standard, supervisor sweep CONFIRMED 2026-08-04. Patched under `simple` at np=4 it is 0.00054%. ~~10.04%, adjoint 0.21821, FD 0.24258.~~ ~~CONDITIONAL under the current standard.~~ *(Superseded 2026-08-02: the 10.04% is a `scotch`-decomposition artifact and is not the graded configuration. It was graded PASS against the calibrated band, which is retired; two other records graded it CONDITIONAL before the decomposition finding.)* *(Grade corrected 2026-08-14, tree at `13b965dd`: this row led with 10.04% as its bolded figure and carried PASS beside it, while the current standard grades 10.04% CONDITIONAL — the number shown and the grade shown were two different configurations, and the CONDITIONAL that belongs to 10.04% was struck rather than the figure. The figure now leading the row is the one the grade is of. No measurement moved and no verdict moved; found by self_audit `FD grades vs current standard`.)* |
| A5 | objective wrt shape, 27 components | **46.6%** aggregate; only 5 of 27 within the 12% band; **2 sign flips** — **FAIL against the shipped toolchain**. *Patched local IDWarp (2026-08-01), rotations ON, real seed: idx8 207.0% flip → 3.0e-06, idx17 121.6% flip → 7.0e-06, signs agree; all 27 stock-objective components rel_err 0.0000 (before-worst 80.79%). Stock still fails* |

### 2026-08-01 note on the A1/A5 patched numbers: what changed and what did not

The A1/A5 gradient defect is one mechanism, named to a source line: IDWarp
2.6.2's `getRotationMatrix3d` degenerate-rotation branch
(`src/utils/vectorUtils.f90:58`), whose AD reverse returns a derivative of
exactly zero at the undeformed baseline — the state every gradient evaluation
uses — where the true value is a cross-product term. A four-line corrected
derivative, applied in a **scratch clone only**, collapses every measured error
to FD-truncation level with rotations ON, leaves the primal warp md5-identical,
and also answers upstream's five-year-open `mdolab/idwarp#57` (210%/213% →
8.6e-06%/3.4e-05%). Root cause confirmed by repair:
`dafoam/ROOTCAUSE_getRotationMatrix3d.md`, `dafoam/PATCH_getRotationMatrix3d.md`,
`dafoam/PROOF.md` §23–24.

**What did not change: no installed package was modified, nothing has been filed
upstream (Katie's call), and every verdict on this board is graded against the
SHIPPED stock toolchain, which still carries the bug. A reader must not take the
italicised patched numbers as the state of shipped DAFoam — they are the proof
of the diagnosis, recorded beside the stock FAILs.**

### A4 found a silent solver mismatch that affects the credentials wall

The Ahmed primal landed **22.05% away from our own validated OpenFOAM baseline**
on the same mesh, boundary conditions and turbulence model. The cause is not
tolerance and not mesh: our baseline sets `consistent yes` in its `SIMPLE` block
— **verified directly in the case file** — which selects the consistent pressure
correction. `DASimpleFoam` does not implement it and silently runs the plain
variant instead.

On the 25 degree slant this is not a small numerical difference. That geometry
has a **documented bistable wake**, so the two algorithms settle on *different
branches of the solution*. Both sat within the experimental band once rebased to
frontal area — ours 0.2510 and the baseline 0.3219 against the measured 0.285,
at 11.93% and 12.95%.

> **Correction, 2026-07-30.** The sentence above previously opened "Neither
> number is wrong on its own terms," and is written in the present tense. That
> no longer holds for **0.2510**: the A4 row of the status table above withdraws
> it (the 45,760-cell DAFoam primal's turbulence field diverged while its
> normalised residual read as converged, and the drag was computed from that
> state). This paragraph and that row contradicted each other 29 lines apart.
> The withdrawal stands; **0.2510 must not be cited as a result**, here or
> anywhere. The *bistable-wake / SIMPLE-vs-SIMPLEC* reasoning in this section is
> unaffected and still worth keeping — it is why the two codes were expected to
> differ at all — but it can no longer be supported by that particular number.
> **0.3219 is unaffected** and remains the validated 45,753-cell OpenFOAM
> baseline. For how 0.3219 relates to the act's 0.3041, see
> `campaign/AHMED_BODY_RECONCILIATION.md`.

**Any credential or comparison that places the two solvers side by side inherits
this**, and an audit is now queued.

**A4 also validated the memory-wall constraint as actionable:** the primal ran
at 45,760 cells and the adjoint was deliberately coarsened to 2,777, which made
it tractable and produced the first passing FD verification since A1. Coarsening
for the gradient stage while comparing the primal on the fine mesh is legitimate
precisely because it was disclosed.

### Cross-rung finding: the adjoint has a memory wall on this host, between 10^4 and 10^5 cells

This one held up, and it constrains the whole ladder.

| rung | cells | adjoint outcome |
| --- | --- | --- |
| A1 NACA0012 | 4,032 | works, FD verified |
| A5 U-bend | 4,800 | works, GMRES converged in 86 iterations |
| A3 ONERA M6 | 399,360 | **OOM** in the mesh-sized residual/volume-coordinate Jacobian assembly |
| A3 coarsened | 99,840 | **still OOM** |

Eight independent mitigations were tried on A3 and ruled out: 12 GB and 18 GB
container caps, 4-rank and 2-rank decomposition, GMRES restart 1000 to 200, and
preconditioner fill level 1 to 0. The 2-rank attempt drove the host to 1.77 GB
free and was killed manually rather than left to run — the right call, given
this box has been taken down twice in two nights by memory exhaustion.

**The working envelope for adjoint work on this instance is order 10^3 to 10^4
cells, not 10^5.** Consequences, stated now rather than discovered later:

- **A6 (CRM / DPW-class) cannot produce a gradient here.** The queue already
  scoped it as "converged primal is success, gradient is stretch" — that
  judgement is now backed by measurement rather than caution.
- **A4 was briefed to build the smallest mesh that still resolves the 25 degree
  slant separation**, and to coarsen further for the adjoint stage specifically.
  Verifying a gradient on a coarser mesh than the primal comparison is
  legitimate as long as it is disclosed.
- A genuine matrix-free adjoint path exists (`adjUseColoring=False`) but trades
  the memory for a runtime cost that was not attempted and should not be assumed
  tractable.

### Refuted cross-rung finding: FD agreement is NOT gated by primal convergence

Neither rung could see this alone. Placed side by side:

| rung | primal state | FD shape-derivative result |
| --- | --- | --- |
| A1 | residual **9.646e-09** against tolerance 1e-08, converged | 11.43%, **no sign flips** |
| A5 | p initRes plateau **2.2576e-04**; total field residual norm2 **55.776** | 46.6%, **2 sign flips** |

Five orders of magnitude apart in primal convergence; four times the FD error,
plus sign flips. **Hypothesis: the adjoint is exact for the discrete converged
state, so if the primal sits at a residual plateau the adjoint is linearised
about a point that is not a solution, while each finite-difference perturbation
re-solves to a slightly different point on that same non-converged manifold.**
The difference between those is noise no step size can remove — which is
precisely what A5's own step-size sweep found when the FD estimate failed to
converge toward the adjoint value as the step grew.

A supporting detail from A5's record: the 55.776 total is dominated by
temperature at 41.16. That case descends from a conjugate-heat-transfer family
and still solves temperature, which is excluded from both the objective and the
adjoint yet remains in the primal state and far from converged. **The state the
adjoint linearises about is polluted by a field the adjoint cannot see.**

### The test ran. The hypothesis is **REFUTED**.

| metric | before | after tightening |
| --- | --- | --- |
| p initRes | 2.2576e-04 | 2.0568e-04 (9% better, still far from 1e-8) |
| total residual norm2 | 55.776 | 59.324 — **worse** |
| FD aggregate error | 46.64% | **46.21% — no material change** |
| components within 12% | 5 of 27 | 4 of 27 |
| sign flips | 2 | 3 |

`residualControl` at A1's 1e-8 bar, solver tolerances tightened one to two
orders of magnitude, `endTime` extended 1000 → 5000 → 10000. **Iterations 1000
through 10000 produced bit-identical residuals** — never under-iteration, but a
true fixed point of the discrete iteration, plausibly the curved duct's
secondary-flow structure which a coarse steady solve cannot resolve away. The
tightened design point differs from the original only in the 6th significant
figure (pressure loss 52.34517755 against 52.34521634), so this is the same
state, not a better-converged one.

**The mechanism I proposed was also wrong.** I argued temperature, at 41.16 of
the 55.776 total, was polluting the linearisation point. But this case carries
constant viscosity with no temperature dependence and no buoyancy, and the
objective is a pure function of pressure and velocity — temperature's adjoint
row is **analytically decoupled** from the rows the gradient depends on. It had
no channel into the result, and tightening its solve predictably did nothing.

**The rule that replaces it** (now L-7): do not assume "converge harder" fixes
gradient disagreement. Establish first, with one cheap high-iteration run,
whether convergence is even available. A plateau that survives a tenfold
iteration increase is reporting something about the physics or the mesh, and the
next lever is resolution or geometry smoothness, not solver settings.

A5's original measured numbers stand untouched in the record; this is an
appended addendum. **A1's 11.43% therefore remains unexplained**, and the
step-size study already in the proposal queue is the next probe.

### RESOLVED — the step-size sweep settles it: A1's 11.43% is REAL, not a check artefact

The priority probe swept the finite-difference step across eight decades on A1,
reproducing the original 11.43% exactly at step 1e-3 before doing anything else.

| step | aggregate error | | step | aggregate error |
| --- | --- | --- | --- | --- |
| 1e-8 | 94.95% | | 1e-3 | **11.43%** (reproduces A1) |
| 1e-7 | 52.88% | | 5e-3 | 10.47% |
| 1e-6 | 17.64% | | 1e-2 | 8.94% |
| 1e-5 | 12.27% | | 2e-2 | 4.28% |
| 1e-4 | 11.52% | | 3e-2 | 9.83% |
| | | | 5e-2, 1e-1 | primal failed |

**Not a clean V, and not flat.** Roundoff blow-up below 1e-4, solver failure
above 3e-2, and a noisy non-monotonic plateau between. **The step was never the
problem** — A1's original 1e-3 was a fine choice.

**The disagreement is three specific components.** Excluding idx0, idx1 and
idx6, the remaining five components sit **dead flat at 2.5 to 3.0% across the
whole plateau** with cosine similarity 0.99998 — the harness is sound there.
**idx6 is sign-inverted at essentially every step**, holding −110% to −118%
relative error across three decades, and alone drives **74 to 83% of the squared
error norm**. idx0 and idx1 carry a stable 9 to 16% disagreement.

**This independently reproduces the prior session's `PROOF.md` finding to four
and six significant figures** — 82.70% versus 82.7% for idx6's contribution, and
cosine 0.999983 versus 0.999983. Two separate investigations, different sessions,
same numbers. That is about as strong as corroboration gets here.

### The old band is RETIRED. New grading standard.

| verdict | criterion |
| --- | --- |
| **PASS** | ≤5% aggregate **and** no flagged component |
| **CONDITIONAL** | 5 to 15% |
| **FAIL** | >15%, **or** any sign-flipped / unstable component regardless of aggregate |

**Grading on the aggregate vector norm alone is now proven fragile:** on the
same case at the same step window it swings between 4.3% and 11.5% purely from
how one bad component happens to land. A single defective component can hide
inside a healthy-looking norm, and a healthy gradient can be dragged below the
line by one.

**Consequence for A4, as I flagged when A2 landed: its 10.04% is downgraded from
PASS to CONDITIONAL / unverified.** The reasoning is sharper than mine was — A4
has only **one** scalar design variable, so it cannot hide behind vector-norm
dilution, and its number sits in the range of A1's genuinely defective
components rather than the harness-sound 2.5 to 5% floor. The same sweep should
be run on A4 directly before its gradient is trusted.

### RECALIBRATION — the "1 to 12 percent is normal" band was built on n=1 and is too loose

I derived that band from A1 alone and handed it to every subsequent agent as
settled. A2 shows it is not.

| rung | cells | CD wrt shape, FD error | shape DVs |
| --- | --- | --- | --- |
| A4 Ahmed body | 2,777 | 10.04% | 1 scalar |
| A1 NACA0012 | 4,032 | 11.43% | 20 |
| A5 U-bend | 4,800 | **46.60%** | 27 |
| **A2 MACH wing** | 38,304 | **1.71%** | 96 |

**The spread is 1.71% to 46.60% — a factor of 27.** A2 demonstrates that 1.71%
is achievable on a *larger* mesh with *more* design variables, which is the
opposite of what "shape derivatives are just noisy" would predict. A1's 11.43%
is therefore not a floor imposed by the method; it is specific to A1, and
`PROOF.md` already localises it to three leading-edge control points.

**Consequence I have to own: A4 was graded PASS at 10.04% against this band.**
Its measured numbers are sound and stand unchanged, but **the verdict label
rests on a threshold that no longer looks defensible** — 10.04% is 5.9 times the
best result achieved tonight. A4 should be read as "within the observed spread,
well above the best achieved", not as a clean pass.

**This is the same error I made with the primal-convergence hypothesis**:
generalising from too few points and propagating it as established. There it was
n=2; here it was n=1, and it travelled further because four agents were briefed
with it. The step-size study already in the queue is now the priority probe —
until it runs, the honest statement is that **the acceptable FD tolerance for
shape derivatives on this stack is not yet established**, and rung verdicts that
hinge on it are provisional.

**The calibration that governs every later rung.** The geometric constraints
verifying at machine precision proves the harness, the deformation chain and the
check itself are sound — so the 11.43% cannot be waved away as a broken rig.
And because the gradient *magnitudes* agree to 0.451% while the difference norm
is 11.43%, the disagreement is ~~directional, per-component noise, not a scale
error~~ *(superseded, see below)*. ~~A shape-derivative gap of order 1 to 12
percent against central differences is normal for this class.~~ *(That grading
band is retired; the current standard is pass at 5% or better with no flagged
component.)*

~~This also settles a stale docket entry: the "3 of 8 components at 11.9 and
11.6 percent with one sign-reversed" describes the **tutorial's own** known
failure signature, not our sail case, which was separately recorded as
differing from it at 0.7 to 8.2 percent with no sign flips. **Our adjoint
behaves better than the official tutorial's.**~~

> **Superseded, 2026-08-01.** Both struck claims predate the root cause. The
> disagreement was never noise: it is one defect at a named source line, the
> IDWarp degenerate-rotation branch, whose reverse derivative is exactly zero
> where the truth is a cross-product term. The 11.9 and 11.6 percent signature
> this paragraph attributed to the tutorial alone was the same defect in our
> own chain, and it collapses to 1.2e-05 percent under the local patch. No
> adjoint here "behaves better" than another; they share the bug. Stock
> toolchain verdicts stand as graded. See the 2026-08-01 note under the FD
> table above.

## Ladder B — closure literature with adjoints

| Rung | Status | Result |
| --- | --- | --- |
| B1 | **COMPLETE** | Ranked reproduction plans written; benchmark clone and public leaderboard located on this box |
| B2 | **COMPLETE, verified** | Uncorrected duct baseline reproduced to 0.16% and 0.64% |
| B3 | running | The field inversion itself |
| B4 | queued | Feed findings back into the closure track |

**Top pick:** Wu, Zhang and Zhang, AIAA Journal 63(2), 2025, 687-706. They invert
a correction field on the SST destruction term through DAFoam's own discrete
adjoint, ~~train only on a public separated-flow case, and generalise to the ducts
without seeing them~~ *(superseded 2026-08-04, see below)*. Rejected candidates
were reported with reasons rather than
padded: one leaderboard entry is gradient-free rather than field-inversion, two
foundational papers have zero case-geometry overlap, and one paper's citation
could not be pinned down and was reported as a gap instead of guessed.

> **Superseded, 2026-08-04.** The struck clause described the rank-2 *entry's*
> protocol and attributed it to the *paper*; the W2 deep-read of both artifacts
> (`campaign/W2_WU_ZHANG_DESTRUCTION_FIML_READING.md` §1, commit `393ad74f`)
> separates them. Three corrections. **First**, CBFS-only training is true of
> the rank-2 entry (its own description document,
> `docs/papers/wu_zhang_sst_qcrc_challenge_description.pdf`, §2) and false of
> the paper (arXiv:2402.16355), whose models train on **mixed NASA hump +
> CBFS** — and the hump is scored case `NASA_2DWMH`, so the paper's protocol
> scored on this benchmark would be in-sample by construction; a clean scored
> reproduction must copy the entry's CBFS-only choice. **Second**, "generalise
> to the ducts without seeing them" is stated by neither artifact — the paper
> has no duct case and the entry document shows only CBFS and the ZPG plate;
> duct zero-shot is this lab's own inference from the entry's training set
> plus the leaderboard, and is carried as ours. **Third**, the rank-2 model is
> **SST-QCRC**: the conditioned β on the destruction term (paper Eqs. (5)–(6),
> entry Eq. (2)) *plus* an untrained QCR2000 quadratic constitutive term,
> `c_r = 0.3` (entry Eq. (1)), previously unnoticed in the lab's record. The
> `w3-beta-on-omega-destruction-model-patch` item below therefore reproduces
> the paper's inversion capability, not the deployed rank-2 model; parity with
> the duct scores also needs the QCR term, filed as
> `w3-qcr-constitutive-term-for-rank2-parity`.

**What this lab can invert on is not that term, restated 2026-08-01 under
ruling R6.** DAFoam's field hook multiplies the omega equation's PRODUCTION
term; the destruction term's coefficient is the blended model constant and
carries no field hook. Our own goal is therefore a production-term inversion,
which is what can be built on this stack, and it does not inherit the
destruction-term goal, the paper's result, or the like-for-like reproduction
claim that would go with it. The destruction-term variant needs a patched and
rebuilt turbulence model and is filed on its own as
`w3-beta-on-omega-destruction-model-patch`.

### B2 — the duct baseline is reproduced, and the pipeline was validated before it was trusted

The benchmark clone turned out to ship **the paper authors' own uncorrected
case directories** — mesh, boundary conditions, `fvOptions`, and the original
run log. Re-solved as-is on this box and scored through the benchmark's own
unmodified scorer:

| case | ours | published floor | deviation | field vs field |
| --- | --- | --- | --- | --- |
| AR_1_Ret_360 | 0.1290 | 0.1288 | +0.0002 (0.16%) | 0.023% |
| AR_3_Ret_360 | 0.1251 | 0.1243 | +0.0008 (0.64%) | 0.09% |

**The sanity check is what makes these trustworthy:** scoring the benchmark's
*own* baseline field through our scorer reproduced 0.1288 and 0.1243 exactly,
confirming the scoring pipeline before any of our own numbers were believed.
30.9 core-min total.

Three deviations documented with cause rather than smoothed over: a custom
frozen-turbulence library whose source is not distributed anywhere in the public
clone (stock SST substituted, measured as effectively inert at under 0.1% field
agreement, but **not** verified against the library's own source); an OpenFOAM
fork mismatch between the original Foundation build and this box's ESI build,
worth 10 to 13 percent in iteration count but only 0.02 to 0.09 percent in the
converged field; and a renamed diagnostics function object, dropped with no
effect on the solved field.

**Blocker found and flagged rather than worked around:** the CBFS reference
fields use `#include`-macro'd dictionaries that the field parser silently fails
on, returning nothing at all. A silent empty read is precisely the failure that
manufactures a fake result, so it was handed to B3 as the first thing to fix.

## Campaign F6 — closure-aligned separated flows

### F6a NASA wall-mounted hump — GATE REACHED

| quantity | ours | NASA experiment | deviation |
| --- | --- | --- | --- |
| separation x/c | 0.6544 | 0.665 | **−1.59%** |
| reattachment x/c | 1.2534 | 1.100 | **+13.95%** |

**The +13.95% is not our error, and the cross-checks are what establish that.**
Against NASA's *own published SST CFD*, our separation point differs by 0.06%
and our reattachment sits inside their published 1.25–1.27 range. Against the
benchmark's shipped baseline field, ≤0.02%. Through the benchmark's own scorer,
0.0622 against the published floor of 0.0621, +0.16%.

So our solver reproduces NASA's SST result almost exactly, and **both** miss the
experiment the same way. The deviation is the documented linear-eddy-viscosity
over-prediction of bubble length — a **turbulence-model deficiency, not a solver
error**. Reference data was fetched live from the relocated TMR site, not
recalled. 5.25 core-min for all three rungs.

### F6c square duct vs DNS — GATE MEASURED, FAIL, and the failure is structural

| case | DNS secondary flow (% of U_bulk) | RANS captures |
| --- | --- | --- |
| AR_1_Ret_360 | 2.22% | **0.0%** |
| AR_3_Ret_360 | 2.07% | **0.0%** |

Uncorrected k-omega SST produces **exactly zero** secondary flow — machine
precision, ~1e-15% of bulk. This is not a resolution or convergence artefact; a
linear Boussinesq closure has zero normal-stress anisotropy by construction, and
secondary flow of the second kind is driven entirely by that anisotropy. The
model *cannot* produce it. Zero new CFD was spent: B2's converged baselines were
reused. 0 core-min.

### Supervisor analysis: the duct deficit is NOT mainly the missing secondary flow

The obvious inference from F6c is that the ducts dominate our deficit because
the secondary flow is missing. **I checked, and that inference is wrong.**

| case | our error | secondary flow absent | **max share explained** | rank-2 total error |
| --- | --- | --- | --- | --- |
| AR_1_Ret_360 | 9.19% | 2.22% | **24%** | 4.55% |
| AR_3_Ret_360 | 8.62% | 2.07% | **24%** | 3.99% |

Since the secondary flow is entirely absent, it can account for at most its own
magnitude. **At least 76% of our duct error is streamwise-profile error.**

And the decisive comparison: **rank 2's total error (4.55%, 3.99%) is smaller
than our streamwise-only remainder (~7.0%, ~6.6%).** A scalar correction on the
turbulence destruction term does not create anisotropy either, so rank 2 is
almost certainly carrying the same ~2.2% secondary-flow floor — meaning their
streamwise error is roughly 2.3% against our 7.0%. **They are about three times
better at the part that dominates.**

*Caveat: scaled MAE does not decompose exactly, so these are bounds and
estimates, not an exact error budget.*

**Two consequences, and they point in different directions:**
1. **B3's field inversion is well targeted after all.** The dominant term is the
   streamwise profile, which is exactly what a scalar eddy-viscosity correction
   can fix. Unblocking the GMRES failure remains the highest-value single task.
2. **~2.2% is a floor for the entire linear-eddy-viscosity class**, ours and
   rank 2's alike. Rank 2 at ~4.0–4.6% is already within twice that floor.
   Beating it needs a closure that resolves anisotropy — which is precisely the
   **TBNN and SpaRTA** classes named as M2's next two reproductions. F6c has now
   supplied the physics argument for that ordering, rather than it resting on
   convenience.

## Ladder C — closure challenge

**Round 5 (2026-08-07), the entry of record: closure metric moved
0.0654 → 0.0566 (−0.0088), RANK 1 of 5 scored locally at benchmark commit
`deb91557` — a local scoring, not an official placement; we remain
unsubmitted.** A duct-only change with physics instead of a fit: the
untrained QCR2000 constitutive term (`kOmegaSSTQCR`, `Ccr1 = 0.3`,
Spalart's published constant, nothing fitted to anything) replaced the
round-4 ML duct correction on all three test ducts, forward-solved to
convergence on the shipped meshes; the five non-duct CSVs are byte-identical
to round 4 and scored identically. Governance: all-or-none rule frozen at
`0bade54a` **before the first validation iteration existed**, gate passed
ALL on the benchmark's own suggested validation duct `AR_7_Ret_180` (ratio
0.4770 ≤ 0.70, r 0.9284 ≥ 0.85, both arms converged); accept criterion
(< 0.065438), expectation band (0.059–0.0666) and the AR_14 risk statement
frozen in `campaign/R5_PREREGISTRATION.md` @ `e865076b` before the call;
independent pre-score verification (hashes vs round-4 manifest, 1000×3
finiteness, fresh ordering-check rerun, pre-registration hash table vs
disk) all passed. Per-case: AR_1_Ret_360 0.0811 → **0.0455** (−0.0356),
AR_3_Ret_360 0.0775 → **0.0400** (−0.0375), AR_14_Ret_180 0.0325 →
**0.0353 — the pre-accepted regression: the 0.00003 nominal best-on-board
tie with Reissmann is LOST**, exactly the risk the pre-registration put in
writing, not reverted (reverting one duct after seeing its score is
per-case selection on test outcomes; the bundle was judged as a bundle and
won 12× over). ~~Best-on-board now 4 of 8 (both alpha_15, both alpha_05).~~
*(Struck 2026-08-12: 4 of 8 was the four-entry board of the 2026-08-07
scoring day. Against the six-entry board fetched 2026-08-11T23:33Z it is
**2 of 8** — both `alpha_15` hills lost to Tian, Buchanan, Hickel & Dwight —
and both survivors are the organisers' own unmodified RANS baseline passed
through the decline gate, so **the model's own count is ZERO of 8**; the
count may not be stated without that disclosure.
`campaign/PROBABILITY_OF_RANK_SIX_ENTRY_2026-08-11.md` §3a.)*
Overall 0.056647 vs Reissmann's published 0.059525 — margin 0.002878,
**which carries the G1 seed qualifier: the truth-free seed-spread bound on
the three unchanged PH-model predictions is 0.0024 overall-equivalent,
comparable to the margin itself**
(`closure_challenge_stability_physicality_audit.md` §1; carried forward
2026-08-07, family supervision review F1). The
result landed *below* the pre-stated expectation band; the campaign's
central arithmetic (match rank 2's ducts ≈ 0.056288) was nearly exact, and
our three QCR duct scores land within 0.0004 of the SST-QCRC entry's (Wu &
Zhang) published duct scores on all three ducts — same untrained term,
independent solve, same answer. This was the **6th cumulative scoring
call** (floor, rounds 1–5; a self-imposed ledger — the benchmark imposes no
limit). Compute: 37.0 solver core-min measured vs 95 budgeted. Katie's
send-package (`CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md`) now carries this
stronger entry; her items 6–7 remain the only things between it and the
steward. Records: `closure_challenge_round5_qcr.json`,
`closure_challenge_submission_round5/` (8 CSVs + MANIFEST),
`CLOSURE_CHALLENGE_STATUS.md` §0f, `campaign/R5_PREREGISTRATION.md`,
`campaign/R5_RULE_FREEZE.md`, `campaign/R5_validation_AR7.json`,
`closure_challenge_round5_qcr_forward.json`.

**Round 4 (2026-07-31) *(superseded as entry of record by round 5 above,
2026-08-07)*: closure metric moved
0.0676 → 0.0654 (−0.0022), rank 3 of 5, gap to rank 2 cut 0.0052 → 0.0030.**
A duct-only change: Variant D replaces the round-2/3 duct model — a
Reynolds-invariant `d/d_max` feature and a velocity-scale-normalised target,
trained on the 4 DUCT training cases (`AR_1/3/5/10_Ret_180`) and
pre-registered on the benchmark's own suggested duct validation case
`AR_7_Ret_180` (`closure_challenge_duct_reynolds_transfer.json`, committed
before any test score for it existed). The five non-duct predictions are
byte-identical to round 3, SHA-256-verified against the entry manifest.
Per-case: AR_1_Ret_360 0.0919 → 0.0811, AR_3_Ret_360 0.0862 → 0.0775,
AR_14_Ret_180 0.0303 → **0.0325 — a regression, deliberately NOT reverted**:
choosing per-case between two models after seeing their per-case test scores
is selection on test outcomes, exactly what the benchmark's one strict rule
exists to prevent; Variant D was frozen on validation evidence and applied to
all three ducts or none. AR_14's lead over Reissmann collapses from 0.0022 to
0.00003 (0.0324698 against the published 0.0325) — a nominal lead that must
not be reported as a comfortable win. We are no longer last on any duct; last
on the board only on NASA_2DWMH. Best-on-board 5 of 8, unchanged. This was
the 5th cumulative scoring call (distinct prediction sets scored — a
self-imposed ledger; the benchmark imposes no limit). The sign pattern
matched the pre-registered diagnosis on all three ducts: improvement
concentrated where `Re_y` leaves the trained range (−0.0108, −0.0087), a
small loss where it does not (+0.0022). Records:
`demo-output/website/closure_challenge_trained_entry_round4_duct.json`,
`demo-output/website/closure_challenge_submission_round4/test/` (8 CSVs),
`sdk/scripts/closure_round4_duct_rescale.py`,
`CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` §7.1.

**Round 3 *(superseded as entry of record by round 4 above)*: closure metric
moved 0.0741 → 0.0676 (−0.0065).** The C1
gate (fit and validated on train/validation only, deliberately not applied
to the test set in the prior session) was evaluated on the 4 official PH
test cases for the first time, using only their RANS-derived features. It
correctly declined the correction on the 2 cases it was hurting
(`alpha_05_4071_4048`, `alpha_05_4071_2024`) and correctly kept applying it
on the 2 it was helping — 4/4 correct, matching its validation performance.
This was the single 4th official scoring call this lab has made on this
benchmark. Full account: `demo-output/website/CLOSURE_CHALLENGE_STATUS.md`
§0, `demo-output/website/closure_challenge_trained_entry_round3_gated.json`,
`sdk/scripts/apply_closure_ph_gate.py`. Compute: 83s wall / 2-core cap /
356 MB peak RSS — model-fitting and inference only, no CFD solve.

### Where we actually stand

*(Updated 2026-08-07, round 5. All entrant numbers quoted from the
benchmark README at commit `deb91557`; ours scored locally through the
unmodified eval package at `1c4e22c8` — a local scoring, not an official
placement.)*

> **FRAME WARNING ADDED 2026-08-15, and it is about the table as much as the
> paragraph below it.** The table's ordinals come off `deb91557`, the **four**-entrant
> scoring clone frozen 2026-05-04, which **scores but does not rank** — so the table is a
> correct rendering of a board that has not existed since 2026-08-11T23:33Z, and its
> "Rank 1" is not a standing. **The board of record for every ordinal on this page is the
> SIX-entry board retrieved 2026-08-11T23:33Z and re-verified unchanged 2026-08-14T21:01Z**
> (`campaign/BOARD_MOVED_2026-08-11.md`, re-fetched in `campaign/BOARD_RESCORE_2026-08-14.md`).
> Against it there are two more entrants — Yang at 0.0580 and Tian, Buchanan, Hickel &
> Dwight at 0.0641 — neither of which appears in the five rows below. The mandatory
> companion clauses for any statement of rank 1 are at the top of this file (2026-08-11),
> and they bind this table too.

| Rank | Entry | Overall |
| --- | --- | --- |
| **1** | **ours, unsubmitted (round 5, scored locally)** | **0.0566** |
| 2 | Reissmann, Fang, and Sandberg | 0.0595 |
| 3 | Wu and Zhang | 0.0624 |
| — | ours, unsubmitted (round 4, superseded) | 0.0654 |
| 4 | Liu, Wang, Zhao, and Xiao | 0.0737 |
| 5 | Montoya, Oulghelou, and Cinnella | 0.0779 |

**Best score on the entire leaderboard: 2 of the 8 cases — recomputed
2026-08-15 against the six-entry board retrieved 2026-08-11T23:33Z,
re-verified unchanged 2026-08-14T21:01Z.** And the count belonging to our
own model is **zero of the 8**, which is the figure that has to be read
first, because the two we do lead are not a result of ours at all.

The two are `alpha_05_4071_4048` (ours 0.0461, next-best 0.0569) and
`alpha_05_4071_2024` (ours 0.0719, next-best 0.0748). On **both**, our
submitted prediction *is* the organisers' own unmodified RANS field: the
decline gate declined to correct those cases and we passed the baseline
through untouched. **Anyone submitting that baseline unchanged scores
exactly the same on those two rows.** The credit there belongs to a file
every entrant is handed for free, and to nothing we built. So "2 of 8" on
its own is still a misleading way to say this; the honest form is *2 of 8
on the board, 0 of 8 earned by the model.*

The other six, live: on `alpha_15_13929_4048` (ours 0.0501) and
`alpha_15_13929_2024` (ours 0.1011) we are behind Tian, Buchanan, Hickel &
Dwight, at 0.0432 and 0.0998 — these two are the cases the count lost when
the board grew. Ducts, all three behind Yang: `AR_1_Ret_360` 0.0455 against
0.0291, `AR_3_Ret_360` 0.0400 against 0.0311, `AR_14_Ret_180` 0.0353
against 0.0250. `NASA_2DWMH` is our worst row on the whole board, 0.0632
against 0.0294. The overall is a mean and not a count of wins, which is why
0.056647 is still the lowest overall number while the per-case tally reads
as it does: this entry is consistent, not peaked.

> ~~**We hold the best score on the entire leaderboard on four of eight
> cases** (was five — AR_14's nominal lead was spent, knowingly, on the
> round-5 bundle): alpha_15_13929_4048 at 0.0501 against a best-other
> 0.0592, alpha_15_13929_2024 at 0.1011 against 0.1195, alpha_05_4071_4048
> at 0.0461 against 0.0569, alpha_05_4071_2024 at 0.0719 against 0.0760
> (both alpha_05 cases the gated raw-RANS value, which itself beats every
> published entry on those two cases). On the ducts: AR_1_Ret_360 0.0455 (a
> published-precision tie with Wu & Zhang, behind Reissmann's 0.0387),
> AR_3_Ret_360 0.0400 (vs Wu & Zhang 0.0399, Reissmann 0.0341),
> AR_14_Ret_180 0.0353 (vs Reissmann 0.0325, Wu & Zhang 0.0350). Last on
> the board only on NASA_2DWMH (0.0632 vs best 0.0364).~~
>
> **STRUCK 2026-08-15, kept so the correction stays visible.** Every
> comparison figure above was a **four**-entry-board number, and the
> paragraph stated it in the **present tense** under a heading that says
> where we stand — so it was a claim about the live board, made from a
> superseded one, and it survived four days after the board moved on
> 2026-08-11T23:33Z. Six of its eight comparison values were wrong against
> the live board, not one: the two alpha_15 best-others (0.0592, 0.1195),
> `alpha_05_4071_2024`'s (0.0760), and all three duct best-others, none of
> which had Yang in them because Yang was not on the board they were
> written against. Re-derived by executing over two committed records that
> do not consult one another — `LIVE_BOARD` in
> `sdk/scripts/probability_of_rank.py`, read by AST, and
> `round5_per_case_full` in `closure_challenge_round5_qcr.json` — and
> cross-checked against `scripts/self_audit.py`'s own `_closure_facts()`,
> which derives `best` = 2, `declined` = 2, **`earned` = 0** from the same
> two files by a different route. Found by the Ladder V V6/V10 grade of
> 2026-08-15 (`campaign/LADDER_V_V6_V10_GRADE_2026-08-15.md`, failure 2).

**What is still blocked, unchanged**: the duct streamwise-profile deficit
(Term 2, the larger of the two identified recoverable terms) remains gated
on the DAFoam/PETSc adjoint GMRES `KSP_DIVERGED_NANORINF` failure (Ladder
B3) — a CFD-solving problem, out of scope for a 2-core/3GB data-and-fitting
compute budget, and another agent is actively working it (not duplicated
here). That is the highest-value target once a solving budget is available.

**New (this session): feature-expressivity audit answers the cheaper prior
question — can the existing DUCT feature set express the missing correction
at all, before spending more capacity or another adjoint session on it?**
One-sentence answer: not fully blind, but two of its seven features
(`I3_S3`, `I4_W2S`) are *provably, always* zero on this entire flow family
(RANS produces exactly zero secondary flow, and that algebraic form makes
those two invariants vanish identically for any shear rates — verified both
on real data and over 50,000 random shear pairs), and of the five that
remain, the component that most drives secondary-flow generation
(`b_yy - b_zz`, normal-stress difference) is not reliably predictable
(held-out R²=0.04, one fold strongly negative), while the other (`b_yz`,
shear) carries only a weak but consistent signal (held-out R²=0.27). Full
account: `demo-output/website/CLOSURE_CHALLENGE_STATUS.md` §0b,
`demo-output/website/closure_challenge_duct_anisotropy_expressivity.json`,
`sdk/scripts/closure_duct_anisotropy_expressivity.py`. Scope: DUCT training
cases only (`AR_1/3/5/10_Ret_180`), no validation/test case touched, no
`score()` call, Ladder B3 not touched. Compute: 17.5s / 2-core cap / 170 MB
peak RSS.

**New (this session): a general, cross-family generalization-failure
criterion, part of it proven.** A model trained exclusively on cases where
two input dimensions are algebraically forced to zero (the DUCT model, per
§0b) has zero learned dependence on them; fed a case where they are
genuinely nonzero, it breaks catastrophically (3.9x-10.4x baseline error),
6 of 6 times tested. Not a proxy: verified with a same-case/same-viscosity,
different-model controlled comparison (`CBFS`, `PH_Breuer`, each scored
under both models -- the label flips, viscosity does not), and by checking
the DUCT model correctly reads no-mismatch on its own validation case
(rules out "which model" as a trivial stand-in). A naive statistical
analogue (feature-range coverage) was tested and rejected: it fires on 9 of
9 instances including the one that helped, i.e. zero true negatives -- the
same "looks-strong-secretly-a-proxy" failure §0b already caught, caught
again and stated plainly rather than reported at face value. What it
cannot do: rank ordinary (non-catastrophic) generalization quality, say
anything about the PH model's own out-of-family behavior (no equivalent
proof exists there), or claim to generalize past the 2 model families
tested. Not applied to any test case. Full account:
`CLOSURE_CHALLENGE_STATUS.md` §0c,
`demo-output/website/closure_challenge_generalization_criterion.json`,
`sdk/scripts/closure_generalization_criterion.py`. Compute: 268s / 2-core
cap / 289 MB peak RSS. Ladder B3 not touched. **Coordinator correction
applied**: state this in the asymmetric form measured -- "a model blind to
a dimension fails on cases that need it" -- not as a symmetric criterion;
only 1 instance tests the reverse direction.

**Bounded follow-up: applied the frozen criterion to the 8 official test
cases' features (no ground truth, no score() call) against the model
currently applied to each.** Zero cases flagged by the proven mechanism --
all 3 duct test cases sit inside the DUCT model's training regime, both
PH-corrected cases and both gate-declined cases sit inside the PH model's.
One due-diligence catch along the way: a naive mean-based check first
flagged NASA_2DWMH at an absurd +2.1e8; investigated rather than trusted,
and traced to a real but DIFFERENT mechanism (all 15 features, not just
I3/I4, are out of range because the tau=1/(Cmu*omega) normalization
explodes in NASA's low-turbulence outer-flow region) -- not the proven
DUCT mechanism, and its already-known actual outcome (+0.0011, mild) does
not match what the proven mechanism predicts, so it is reported separately
rather than folded in as equivalent evidence. **Zero cases warrant a 5th
official scoring call on this evidence** -- the criterion changes nothing
about the current entry. Full account: `CLOSURE_CHALLENGE_STATUS.md` §0d,
`demo-output/website/closure_challenge_criterion_test_case_table.json`,
`sdk/scripts/closure_criterion_on_test_features.py`. Compute: 52.9s /
2-core cap / 179 MB peak RSS.

**New (this session): the submission-policy question on the roadmap is answered —
Certonomous CAN submit, and two defects were found that must be fixed first.**
Roadmap 4B ("find out the challenge's policies and determine whether Certonomous
can submit") has been open and repeatedly flagged. Rules established from the live
sources, not from our local clone alone: the GitHub API confirms the benchmark repo
HEAD is still `deb9155` (pushed 2026-05-04), identical to our clone, so the rules
~~and the four-entry leaderboard~~ quoted in our records are current as of today.

> **The struck half expired, and the date is the whole of the reason (marked
> 2026-08-11).** The *rules* half stands. The *leaderboard* half does not.
> **Executed 2026-08-11: `git ls-remote origin HEAD` in the clone returns
> `d572d40c`, not the pinned `deb91557`.** The upstream repo HEAD has moved since
> this paragraph was written, and with it the README's leaderboard: fetched live
> the same day, the board carries **six** entries and a new leader
> (`campaign/BOARD_MOVED_2026-08-11.md`). The evidence quoted above was sound on
> its own date; what it was not is *durable*, and nothing here said it had an
> expiry. **The pin scores; it does not rank** — and the freshness alarm costs one
> `git ls-remote`, which reads the remote without moving the clone or the pin.

| Question | Answer | Source |
| --- | --- | --- |
| May a company enter? | **Yes — no eligibility clause exists anywhere.** Framed as "This is a community effort!" | benchmark README, eval README, arXiv 2603.28884 |
| Deadline? | **None.** "Submissions are accepted anytime!" | README |
| Submission or scoring-call limit? | **None stated, and none possible** — the package ships the test ground truth and the README instructs submitters to preview their score | README + `closure_challenge` package |
| Format | CSV, 1000 rows x 3 cols, no header, emailed to the steward with authors + references | README, confirmed against the 4 accepted submissions |
| The one strict rule | Train or validate on a test case -> **automatic withdrawal plus a note on the leaderboard** | README, verbatim |

**Our "four official scoring calls, ever" is a self-imposed discipline, NOT
compliance with a benchmark limit.** No such limit exists. Nothing we publish may
imply otherwise.

**Adversarial compliance audit — the one strict rule is NOT violated, verified by
reading the code rather than our own prose.** Ground-truth reads in
`apply_closure_ph_gate.py` occur only inside loops over the 21 training cases
(lines 115, 215); the test-case loop (165-167) loads RANS fields only.
`closure_baseline_error_gate.py` enforces train/val/test disjointness with
executable assertions and imports the test list solely to assert non-intersection.
The 21-fit / 4-check gate uses exactly the benchmark's own suggested split. The
refused 0.0675 shortcut was correctly refused.

**Two defects were found, neither a rule violation, both of which blocked
submission. BOTH ARE NOW CLEARED (2026-07-30, later the same day):**

1. ~~`apply_closure_ph_gate.py`'s docstring claims "Exactly ONE
   `score()`/`evaluate_by_case()` call is made."~~ **FIXED.** The same run makes
   **four invocations over two prediction sets** (lines 205-206 re-score the RANS
   floor, 288-289 score the entry). Substantively harmless — re-scoring an
   unmodified baseline tunes nothing — but an entry whose credibility rests on
   precise self-accounting cannot ship a sentence a reviewer can falsify forty
   lines later. The docstring now states the four invocations explicitly, names
   which pair is the re-score of an already-counted prediction set, and defines
   the unit the ledger counts (distinct prediction sets scored). It also records
   that the benchmark imposes no scoring-call limit at all.
2. ~~**No submittable artifact exists.**~~ **FIXED — the eight CSVs now exist**, at
   `demo-output/website/closure_challenge_submission/test/{case}.csv`, written by
   `sdk/scripts/export_closure_submission_csvs.py` in 69.7s on the 2-core cap.
   *(Round-3 set; round 4 carries its own eight CSVs at
   `closure_challenge_submission_round4/test/`, with the five non-duct files
   byte-identical, SHA-256-verified. The round-5 entry of record carries its
   eight CSVs at `closure_challenge_submission_round5/test/`, hashed in
   `campaign/R5_PREREGISTRATION.md` §3 and format-verified against the accepted
   submissions at benchmark commit `deb91557` — Ladder V rung V7, 2026-08-08.)*

   | Check | Result |
   | --- | --- |
   | Scoring calls consumed | **0** |
   | How zero is guaranteed | Not by omission. `score`, `score_from_csv`, `evaluate_by_case`, `evaluate_from_csv_by_case`, `evaluate_individual_case`, `_velocity_field`, `_ground_truth` and `_load_csv_predictions` are replaced with raising stubs in all three package namespaces **before any pipeline work**, and the guard is proven armed by calling `score()` and catching the refusal. Only evaluation-point **coordinates** were readable |
   | Is `evaluation_points()` a scoring call? | **No.** It returns `_ground_truth()[case]['coords']` only, never `['U']`. Interpolating to those points is what the task requires |
   | Reproduces the entry of record | **8 of 8 checks pass** — both harness commits, refit alpha 0.7499, threshold 0.1263, the top-3 feature names, all four gate decisions and predicted errors, and the per-case prediction source |
   | Format | 1000 rows x 3 cols, comma-delimited, no header, no alphabetic character except the `e` of scientific notation, trailing newline — matching accepted submissions wu, montoya and wang |
   | Independent sanity check | Mean velocity magnitude per case sits inside the band spanned by the accepted submissions on all eight cases, which would catch a point-ordering, column-ordering or units error **without any scoring call**. **The band was measured over FOUR submissions** — those in the frozen clone at `deb9155`. **There are now six** (`campaign/BOARD_MOVED_2026-08-11.md`), and the two new ones' prediction files are not in the frozen clone, so the band has not been re-measured over them. **The verdict is unaffected, by monotonicity rather than by re-running:** adding a submission to a band can only move the min down or leave it and the max up or leave it, so a value inside the four-submission band is inside the six-submission band *a fortiori*. **What monotonicity does not cover, stated because it is a real weakening:** if either new submission is pathological — far outside the old band on some case — the band widens enough that passing it stops discriminating. The check would still pass and would *mean less*. So the verdict stands and the instrument's power is now unmeasured, which is not the same thing as intact. |

   The recorded 0.0676 was **not** recomputed and is carried across from the round-3
   record unchanged.

Also caught: our records label the eval package **v0.2.1**, but at the pinned commit
`1c4e22c8` its `pyproject.toml` declares **0.3.1** ("vector magnitude metric, mean
over cases") — upstream never bumped `__version__`. The score is unaffected; cite
the commit hash, which is unambiguous.

**Highest reputational exposure, and it is not a rules problem**: on
`alpha_05_4071_4048` and `alpha_05_4071_2024` our submitted field IS the unmodified
baseline RANS solve, and those two of our five "best on board" rows credit the
organisers' own baseline, not our model. Legitimate, already stated on `closure.html`
— but it must go in the submission email itself, because being discovered is far
worse than disclosing.

**Genuinely unresolved, flagged rather than resolved optimistically**: neither the
benchmark repo nor `xiaoh/para-database-for-PIML` (the source of our 21 PH training
cases) carries any licence — GitHub API `license: null` for both — so a commercial
entity has no explicit grant to train on it. Mitigating: a submission is our
predicted velocities on the organisers' evaluation points, not redistribution of
source data. Separately, ERCOFTAC content is CC BY 4.0 with **"AI/ML-training & TDM
reserved"** — that bears only on the challenge's 3D cases (wing-body junction, Ahmed
body), which are not test cases and which our pipeline does not touch.

**Status: draft package prepared for Katie's proofreading, nothing sent.** No
submission, no account, no contact with the steward or a GitHub issue. Full account:
`demo-output/website/CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md`.

**What remains before anything can be sent is now entirely Katie's, not the lab's.**
Of the five prerequisites the draft lists, three are done: the docstring is fixed,
the eight CSVs exist, and the version label is superseded by the commit hash
`1c4e22c8` (recorded in the submission manifest, with the reason — upstream's
`__init__` still says 0.2.1 while `pyproject.toml` at that commit says 0.3.1).
Outstanding: **Katie fills the author names and the reference URL, and Katie
proofreads and approves.** Nothing moves before that.

Ambition ahead: get the sign-off, and put the entry on the board where its score
— 0.0654 when this was written; 0.0566 since round 5 superseded it on 2026-08-07;
submissions parked by Katie 2026-08-07 pending the Ladder V gate — can be
independently rescored by someone outside this lab — the first external
check this result would ever have had.

### C2 — where the deficit lives

| case | share of the gap to rank 2 |
| --- | --- |
| AR_1_Ret_360 | **31.5%** |
| AR_3_Ret_360 | **31.4%** |
| NASA_2DWMH | 18.2% |
| alpha_05_4071_4048 | 10.4% |
| alpha_05_4071_2024 | 8.5% |

The two square ducts are **62.9%** of the deficit. Separately, the correction is
worse than doing nothing on three cases against the uncorrected baseline, worth
0.0066 on the mean, which is 1.7 times our margin over rank 4. Both terms are
real; the duct term is the larger by a factor of eight.

### C1 — training line: test-blind baseline-error gate **BUILT AND VALIDATED**

A gate that predicts, from features the test cases legitimately expose, whether
the correction should be applied at all. Fitted on the 21 training cases,
checked on the 4 held-out validation cases, **never on a test case**.

| Result | Value |
| --- | --- |
| Features after screening | 3 (p90 of two Pope invariants, plus a backflow-fraction separation proxy) |
| Separation on held-out validation | **AUC 1.0** |
| Threshold set from training data alone | classified **4 of 4** validation cases correctly |
| Trivial always-apply baseline | 3 of 4 |
| Compute | ~0.06 core-min, single core, no flow solve |

**Two things make this trustworthy rather than merely good-looking.** First, the
agent's own first attempt — a 15-feature model — overfit and was reported, not
buried: training cross-validation looked strong at r +0.93 while validation
collapsed to r +0.25 with the wrong rank order and one prediction twice outside
the observed training range. Feature screening to 3 was the fix. Second, the
n=4 caveat is stated plainly: with only one positive label, an AUC of 1.0 has
roughly a 1-in-4 chance of arising by luck. **Encouraging, not established** —
the same caution C2 applied to its own n=5 finding.

**Leakage independently verified by the supervisor, not merely asserted.** The
script loads only the training and validation splits, imports the test list
solely to assert that it never intersects them, and never calls the benchmark's
scoring function. The only matches for a test-case name anywhere in the file are
in the docstring, one of which is the sentence stating it does not touch them.

**Not applied to the test set, and no scoring call made.** Producing a validated
gate is the deliverable; deciding to spend the single shot is not tonight's call.

### C3 — NACA 4412 credential: **NOT VALIDATED**

Not because a number missed, but because the grading method is self-referential:
the reference is anchored on the solve's own lift, so a 25.0 percent lift
over-prediction inflates the induced term by 56.2 percent and widens the band
with it. Graded that way, the two best-resolved rungs fail and the worst-resolved
passes.

**Knowledge entry.** At fixed refinement, across a 17.7 fold change in boundary
layer coverage (4.36 to 77.0 percent), **drag moved 0.037 percent while lift
moved 9.41 percent**. Drag agreement is not evidence of a resolved boundary
layer on a low aspect ratio wing.

## Ladder D — background

| Item | Status |
| --- | --- |
| D1 mega batch | Running, 3 workers, single-instance lock in force. Session count and 0 failures tracked in the runner log; morning count is the true count |
| D2 queue refill | **6 proposals drafted and style-validated, 755 core-min costed** |
| D3 nightly retro | Queued for end of night |

### D2 proposals drafted this session

| Proposal | Core-min |
| --- | --- |
| Anchor the NACA 4412 reference independently of the solve | 15 |
| Add a boundary layer coverage gate to drag-only credentials | 20 |
| Shape derivative step size study | 35 |
| Closure baseline error estimator gate | 45 |
| Converge lift on the NACA 4412 ladder | 220 |
| Closure duct field inversion | 420 |

## Blocked

Billing alarm and spend cap cannot be read from this instance (no role, no
credentials, no client). Ledger cannot be synced off-host by either route. Both
are recorded in the blockers list with their exact unblock actions. **No spend
figure is reported anywhere in this board, because none can be measured.**
