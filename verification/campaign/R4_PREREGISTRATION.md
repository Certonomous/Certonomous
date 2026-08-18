# R4 — asymptotic-range ladders: pre-registration

**Written 2026-08-01 12:30 UTC, after meshing and before any solver was
launched.** The three meshes exist and their cell counts are stated below;
**no drag coefficient has been computed on any of them.** Meshing produces a
cell count, not a force, so fixing the refinement ratio at this point is
experiment design, not tuning. Every number that decides the outcome is still
unmeasured when this file is written.

Item: `r4-asymptotic-range-ladders`, docket rank 175 of 180, `est_core_min`
400.0, approved 2026-07-31.

---

## 1. The proposal's premise, checked against the record first

The proposal asks whether the non-asymptotic verdicts on the Ahmed body and the
B-52 come from **an insufficient refinement ratio** or from **genuinely
non-monotone grid convergence**, and proposes re-running each *with a constant
ratio*. Before spending a core-minute, the stored ladders were re-read. The
premise is **half right, and the half that is wrong is the B-52**.

Computed from `models/curriculum/uq-studies/b52.json` and
`models/curriculum/uq-studies/ahmed_25.json` through `chief_engineer.uq`
(`eca_hoekstra_band`, `dim=3`), 2026-08-01:

| Ladder | fit triple (cells) | r21 | r32 | ratio mismatch | guards failed |
| --- | --- | --- | --- | --- | --- |
| B-52 | 193 880 / 255 358 / 330 950 | 1.0903 | 1.0962 | **0.54%** | increment_trend, extrapolation_sanity |
| Ahmed 25° | 20 621 / 45 753 / 79 439 | 1.2019 | 1.3043 | **7.85%** | extrapolation_sanity |

**The B-52's fitted triple is already a constant-ratio ladder** — the two ratios
agree to half a percent. Re-running it "with a constant ratio" would change
nothing, because it has one. The proposal's rationale quotes the six-rung
sequence 0.0551, 0.0448, 0.0491, 0.0472, 0.0496, 0.0523 as evidence of
non-monotonicity, but `b52.json`'s own `recipe_audit` records that the first
two rungs used nearBody refinement level 1 and the other four used level 2, so
those six numbers are two mesh families and are not extrapolation-comparable.
Inside the one valid family the fitted triple is **monotone increasing**, which
is why the stored record says `"monotone": true` and fails on
`increment_trend` instead.

What *is* wrong with the B-52 ladder is not that its ratio is unequal but that
it is **far too small**: r = 1.09 against the r ≥ 1.3 that grid-convergence
practice asks for. The consequence is measurable. The Richardson step
multiplies the finest increment by 1/(r^p − 1):

| Ladder | at its own r | at r = 1.30 | penalty |
| --- | --- | --- | --- |
| B-52 (p = 2.253, r = 1.0903) | **4.65×** | 1.24× | **3.75× worse** |
| Ahmed (p = 1.95, r = 1.2019) | **2.32×** | 1.50× | 1.55× worse |

So the B-52's extrapolation amplifies whatever sits in its finest increment
almost five-fold. **That reframes the question but does not answer it**, because
amplification only matters if there is noise to amplify.

## 2. How big is the noise? Measured, not assumed

Three independent runs of the *same* Ahmed production setup (79 439 cells,
kOmegaSST, magUInf 40, Aref 0.401696) exist in this tree, and their Cd values
were recomputed here with the lab's own window convention (mean over the final
20% of the force history, `head_engineer.envelope_statistics`):

| Cd | rows | source |
| --- | --- | --- |
| 0.08481225252258064 | — | `models/curriculum/uq-studies/ahmed_25.json`, `levels[production].cd` |
| 0.08480834261333332 | 154 | `mission-output/ahmed-body/act7-ahmed_25/coefficient.dat` (parallel: `log.decomposePar` present) |
| 0.08479995438000000 | 154 | `demo-output/website/campaign/W3_runs/kOmegaSST/postProcessing/forceCoeffs1/0/coefficient.dat` |

**Run-to-run spread on one setup: 1.23 × 10⁻⁵ in Cd.**

Against that floor:

* the Ahmed ladder's finest increment is 4.975 × 10⁻³ — **404× the noise**;
* the B-52's finest increment is 2.702 × 10⁻³ against its own measured
  iterative 2σ of 1.07 × 10⁻⁵ (`b52.json` `iterative_audit`, force history read
  from `/home/ubuntu/certonomous-runs/study-b52-fine-uq/postProcessing/forceCoeffs1/0/coefficient.dat`,
  mtime 2026-07-27T03:48:11Z) — **253× the noise**.

Even the B-52's 4.65× amplification acts on a signal 253× above the floor. **So
the non-asymptotic verdicts are not noise being magnified by a small ratio.**
Both increments are real.

That leaves one live hypothesis for the Ahmed body, and it is the one this run
tests: **the ladder is simply not fine enough yet.** Its extrapolated value
0.07328 sits 13.6% below its finest rung, which is what a ladder still far from
its limit looks like.

## 3. What is being run

The Ahmed body only. The B-52 is **not** re-run under this item, and the reason
is stated above rather than in a report afterwards: its ladder already has the
constant ratio the proposal wanted to give it, so the proposed intervention is
a no-op on that body. Correcting the premise is the finding; building the run
anyway would be building on a premise the record falsifies.

The Ahmed ladder is **extended upward at a constant ratio**, holding the mesh
recipe fixed and moving one knob — the background blockMesh division triple —
exactly as `run_uq_studies.b52_fourth_rung` does. Surface refinement stays at
level (3 4), feature edges at level 2, region levels ((1e15 1)); the STL, the
domain, the closure (kOmegaSST), magUInf 40, rhoInf 1.225, Aref 0.401696,
lRef 1.044 and `residualControl` at 1e-4 are the production case's, unchanged.

| Rung | blockMesh divisions | cells (checkMesh, measured) | mesh OK |
| --- | --- | --- | --- |
| c1 | (60 13 36) | **79 439** | yes, max non-orth 45.03, max skew 3.12 |
| c2 | (78 17 47) | **144 240** | yes, max non-orth 48.25, max skew 1.35 |
| c3 | (98 21 59) | **254 911** | yes, max non-orth 49.42, max skew 2.00 |

c1 reproduces the stored production rung's cell count **exactly** (79 439),
which is the check that the recipe was rebuilt correctly.

Achieved ratios: **r21 = 1.2090, r32 = 1.2200, mismatch 0.90%** — against the
existing Ahmed ladder's 7.85%. One re-mesh was performed to reach this: c3 was
first built at (101 22 61) → 284 812 cells (2.74% mismatch) and rebuilt at
(98 21 59). That re-mesh moved a cell count only; no Cd existed for either
version when it was made, and both counts are recorded here.

**Rank count: 4 MPI ranks per rung, scotch decomposition, identical for all
three rungs.** All three run concurrently — 12 of the 14 usable cores. The rank
count is held constant across rungs deliberately: decomposition perturbs a
steady SIMPLE solve at the linear-solver tolerance level, and the ladder's
signal is the difference between rungs, so a rung-varying rank count would put
a decomposition artefact directly into the increments. c1 is re-solved rather
than reused for the same reason — the stored production number came from runs
at a different decomposition.

**Cost estimate before the fact:** meshing measured at 1.2 core-minutes total
(44.6 s wall, three concurrent). Solve estimated at 60–120 core-minutes for the
three rungs at 4 ranks, from the production rung's 154-iteration convergence
scaled by cell count. Against `est_core_min` 400.0. Measured cost is reported in
the results file whatever it turns out to be.

## 4. The gates, fixed now

**G1 — the experiment worked.** r21 and r32 agree within 3%. *Already met at
0.90% (§3). Recorded before solving so it cannot be claimed after.*

**G2 — the increments are signal.** Each rung's Cd 2σ over its own final-20%
window must be below 10% of the smaller of the two ladder increments. If it is
not, the increments are iterative noise and nothing below is interpretable.

**G3 — the question.** Fit the three rungs with `uq.eca_hoekstra_band(dim=3)`.

* **G3-A: the ladder enters the asymptotic range** — `increment_trend` and
  `extrapolation_sanity` both hold and `conclusive` is true. Then the Ahmed
  body's non-asymptotic verdict was an artefact of a ladder that stopped too
  coarse, the band stops being the conservative 1.25 × spread, and the case for
  moving Ahmed off the held-back tier is made on numbers.
* **G3-B: it does not.** Then the verdict is a property of this flow on this
  snapped-hex family and not of the experiment design, and it stays
  not-conclusive. **This outcome is not a failure and will not be rewritten.**

**G4 — falsifiable prediction, on the record before the solve.**
The extrapolated value from the *existing* ladder is 0.07328. If the flow is
converging monotonically towards a limit near there, the new rungs should keep
falling. **Predicted: Cd(c2) and Cd(c3) both below Cd(c1) = 0.08480, with
|Cd(c3) − Cd(c2)| < |Cd(c2) − Cd(c1)| (shrinking increments), and the fitted
phi0 landing above 0.0733 — i.e. the extrapolation pulling back towards the
data as the ladder refines.** If Cd rises with refinement instead, the Ahmed
body behaves like the B-52 and that is the finding.

*Nothing below this line existed when the solvers were launched.*
