# A3GC L3 — p-stall triage (read-only; no compute launched; no verdict token)

Lane record, 2026-09-12. The L3 grading is committed (39e299af8) and is the frozen
comparator's alone; nothing here moves it. This asks only **why p stalls**.

## 1. The stall is NOT p-only — all six equations floor together

`/home/ubuntu/certonomous-runs/A3GC-L3/primal.log`, 6000 outer iterations, full
per-equation `Initial residual` history extracted.

| eqn | value at iter 6000 | rel. peak-to-peak, last 200 | last iter running-min improved |
|---|---|---|---|
| p | 2.290019532e-05 | 3.31% | 4268 |
| Ux | 3.010176379e-07 | 2.85% | 4268 |
| Uy | 5.244561171e-07 | 3.40% | 4229 |
| Uz | 3.001399027e-07 | 3.88% | 4163 |
| e | 7.957233673e-07 | 3.25% | 4302 |
| nuTilda | 6.812088816e-06 | 3.07% | 4506 |

All six plateau at the same iteration (~500) and wobble by the same ~3%. p is the
largest only because of per-equation normalisation. **Ux, Uy, Uz and e are all BELOW
1e-06**; only p and nuTilda sit above it. Log-linear decay of p:
-6.69e-03 decades/step over [300,500]; -1.68e-04 over [500,700]; **+1.60e-08 over
[1000,6000]** — dead flat, faintly rising.

Objectives are converged while the residual is not: CD = 0.02977980053, last-10
peak-to-peak 1.885e-06 (6.3e-05 relative); CL = 0.303391751, 5.6e-06 relative.
A limit cycle of ~3% in residual that moves the forces by 6e-05.

`Bounding nuTilda>1e-16` fires on **61 of 61** printed samples, iteration 1 through
6000 (L2: 8 of 8). Clipping never stops. `printInterval` 100 hides the per-iteration
count and magnitude.

## 2. Mesh evidence — both `meshgen/logCheckMesh.txt`, both "Failed 2 mesh checks"

| metric | L3 (99,840 c) | L2 (798,720 c) | worse |
|---|---|---|---|
| small-determinant cells | 18,471 = **18.50%** | 110,979 = **13.89%** | L3 |
| min cell determinant | 3.968723e-07 | 2.725081e-08 | **L2, 14x** |
| max aspect ratio | 222.35 | 792.38 | **L2, 3.6x** |
| max non-orthogonality | 61.158 deg | 72.071 deg | **L2** |
| severely non-ortho faces (>70) | 0 | 241 | **L2** |
| lowQualityTetFaces | 18 | 586 | **L2** |
| max skewness | 1.4408 | 1.4406 | equal |

**The 8x-finer mesh is worse on five of six metrics.** The only metric favouring L2
is the small-determinant *fraction*, and only by 1.33x. The leading hypothesis —
that 18.50% small-determinant cells causes the stall — is not supported.

**Where the bad cells are.** Pure structured hex (99,840 cells = 6,240 surface x 16
wall-normal, 6 faces/cell, all hexahedra). 18,471 / 6,240 = **2.96 layers' worth**,
i.e. a wall-normal band spanning essentially every surface column — not a
trailing-edge concentration. L2: 110,979 / 24,960 = 4.45 layers of 32, same
character. The 18 retained `lowQualityTetFaces`
(`constant/polyMesh/sets/lowQualityTetFaces.gz`) are face IDs 66,342–107,112 of
306,848, in near-pairs at stride 47 — a structured band, not a geometric feature.
`underdeterminedCells` was not retained on disk. **Limit: face IDs were not mapped to
coordinates (that needs a mesh utility), so the band is not placed geometrically.**

## 3. Root cause — the wall-normal stretching ratio is forced to r = 2.09

`genWingMesh.py` differs between levels in **one parameter only** (`N`), with
`s0 = 1.0e-4` and `marchDist = 12.0` held fixed (PREREG Sec.2.6).

| level | pyHyp N | wall-normal cells | **implied geometric growth ratio r** | last-layer thickness | CD |
|---|---|---|---|---|---|
| L3 | 17 | 16 | **2.0880** | 6.25 | 0.0297798 |
| L2 (running) | 33 | 32 | 1.4006 | 3.43 | ~0.0224 @ iter 775, still moving |
| shipped validated ref | 65 | 64 | 1.1674 | 1.72 | 0.0229956 |

At L3 the wall-normal cells **more than double in size every layer**. With s0 and
marchDist both pinned, this is arithmetic, not an accident: 16 cells reaching 12.0
from 1e-4 *requires* r = 2.088. Holding r <= 1.30 at 16 cells would need s0 = 0.055
(mean y+ ~18,000) or marchDist = 0.022. **A well-stretched 16-layer level does not
exist under Sec.2.6's constraints.**

A small cell determinant *is* the signature of extreme stretching, so the 18.50%
figure is an effect of r = 2.09, not an independent defect.

The shipped reference at `/home/ubuntu/certonomous-runs/A3-onera-m6-transonic`
(`run_model_run3.log`, endTime 6000, primalMinResTol 1e-8) has the **same 6,240-face
surface resolution as L3** and differs only in N (65 vs 17). It produced
CD = 0.0229955633 stable to 1e-7 and a validated Cp comparison. **L3's CD is +29.5%
against it.**

Corollary for the triple: r goes 2.09 -> 1.40 -> 1.17 across L3/L2/L1. The three
meshes are **not geometrically similar** — the near-wall discretisation changes
character, not just scale — so the family does not have one fixed asymptotic order.

## 4. The discriminating L2-vs-L3 comparison, at matched step number

| step | L3 p initRes | L2 p initRes | L2/L3 |
|---|---|---|---|
| 200 | 2.759e-03 | 2.590e-02 | 9.4x |
| 400 | 5.762e-05 | 4.170e-03 | 72.4x |
| 500 | 2.543e-05 | 2.151e-03 | 84.6x |
| 700 | 2.314e-05 | 1.018e-03 | 44.0x |
| 770 | 2.275e-05 | 1.037e-03 | 45.6x |

L2 is **9x to 85x above L3 at every matched step** and has not come within 45x of
L3's floor. L2's own decay: -3.80e-03 decades/step [300,500]; -1.52e-03 [500,700];
**+1.94e-05 [600,775] — flat to rising at 1.04e-03.**

**Direction: against the mesh-quality/recoverable reading.** The finer mesh is
converging more slowly per iteration and has flattened *earlier and 45x higher*,
not descended through L3's floor.

**Strength: MODERATE, not conclusive.** 175 flat steps is not a plateau (L3's is
5,500), and L2's last-200 residual wobble is 19% against L3's 3.3% — L2 is plainly
still in transient. ~2,000-4,000 more L2 iterations settle it, and they are already
being paid for.

## 5. Solver setup — no innocent explanation available

`diff` of L3's `system/fvSolution` and `system/fvSchemes` against the shipped,
validated tutorial: **byte-identical, both files.** No lab-introduced setup defect.

- p: GAMG, GaussSeidel, `relTol 0.1`, `tolerance 0`. **Cannot floor the outer
  residual** — at iteration 6000 it takes initRes 2.290019532e-05 to finalRes
  7.605712237e-07 in 2 iterations, a 30x drop *every step*. The linear solve is
  healthy; the **outer SIMPLE iteration** is what has stalled.
- p field and equation relaxation 1.0: correct for SIMPLEC (`DARhoSimpleCFoam`), not
  a defect. U/e/nuTilda 0.80.
- `nNonOrthogonalCorrectors 0` at max non-ortho 61.16 deg: lagged correction, but it
  converges with the outer loop at steady state, and it is the shipped setting. Weak.
- y+ mean 33.62, max 102.49, min 8.44 — inside wall-function range.

The only difference between L3 and the validated reference is the mesh, and within
the mesh only N, and through N only r.

## 6. Ranked causes

**1. Wall-normal stretching r = 2.0880 at the coarse level.** FOR: computed from the
generator's own three parameters; explains the 18.50% small determinant as an effect;
explains the wall-normal band location; CD +29.5% vs a validated case at identical
surface resolution differing only in N; setup byte-identical to that validated case.
AGAINST: L2 at r = 1.401 is worse on five of six checkMesh metrics yet is the
hypothesised improvement; and L2 has not yet descended past L3's floor (Sec. 4).

**2. A persistent clipping limit cycle.** `Bounding nuTilda>1e-16` on every sampled
iteration, 1 through 6000. Clipping is non-smooth and applied after the linear solve;
a perturbation re-injected each iteration sets a floor the outer loop cannot pass.
FOR: fits every observation — all six equations floored together, linear solves
healthy, ~3% coherent wobble, objectives stable. AGAINST: unproven —
`printInterval 100` hides the clipped-cell count and magnitude, and benign far-field
nuTilda clipping is common and harmless.

**3. Intrinsic coarse resolution of the transonic shock.** FOR: CD +29.5%; 16
wall-normal cells at r = 2.09 cannot resolve a shock/boundary-layer interaction.
AGAINST, as an explanation *of the stall*: a genuinely unsteady shock would oscillate
the forces, and CD/CL are stable to 6.3e-05 and 5.6e-06. This is an **accuracy**
finding, not the residual-floor mechanism.

## 7. The measurement that settles cause 1 — single variable, ~77 core-min

Regenerate the coarse level at **pyHyp N = 33 on L3's existing 6,240-face
`surfaceMesh.cgns`** = 199,680 cells, and run the identical primal on 4 ranks.

This holds the surface resolution **exactly** at L3's and changes **only** r, 2.0880
-> 1.4006. Nothing else in the case moves; `fvSolution`, `fvSchemes` and
`runScript_a3gc.py` are untouched, so the byte-identity with the validated tutorial
survives.

- p descends below 2.290019532e-05 -> the stall is stretching-linked and curable, and
  the constant-r family below is the recovery path.
- p floors near 2.3e-05 again -> stretching is exonerated, and cause 2 (clipping)
  becomes the target; the coarse level still has to change on accuracy grounds.

Cost: L3 measured 439.6 s ExecutionTime x 4 ranks = **29.31 core-min** for 6000
iterations at 99,840 cells. At 2.0x the cells, ~58.6 core-min solve + ~18 core-min
mesh generation (L3 stage-1 reference 410 wall s / ~9 core-min, scaled) = **~77
core-min, ~15 min wall on 4 ranks**. At $0.0513/core-h that is ~$0.066 —
**derived, not measured**; the box cannot read its own billing
(COMPUTE_BUDGET_CHARTER Sec.5). Pre-authorised by a wide margin. This needs its own
pre-registration before it is launched.

## 8. The named fix

**A constant-r family, refining in the two surface directions only, N = 33 throughout:**

| level | N | surface faces | cells | r |
|---|---|---|---|---|
| coarse (new) | 33 | 6,240 | **199,680** | 1.4006 |
| medium | 33 | 24,960 | **798,720** | 1.4006 |
| fine | 33 | 99,840 | 3,194,880 | 1.4006 |

**The medium level is exactly the L2 that is running right now** (N=33 x 24,960 =
798,720). The running solver is not touched and not restarted; it becomes the middle
member. Only the coarse level has to be built, at the ~77 core-min in Sec. 7 — the
same run that settles cause 1 doubles as the new coarse level.

Effective refinement ratio between levels is 4^(1/3) = 1.587, above Roache's
recommended 1.3 minimum.

**Honest limitation, stated because it is a real cost of this fix:** at constant N
the wall-normal discretisation error does not reduce across the triple, so
Richardson extrapolation removes the surface-direction error and leaves the
wall-normal error as an unremoved bias. That bias is bounded and estimable against
the shipped N=65 reference (CD 0.0229955633). The alternative — a 3D-similar family —
**cannot** hold r constant while s0 and marchDist are pinned, which is the Sec. 3
corollary. Choosing between "constant r, biased" and "3D-similar, r varying 2.09 to
1.17" is a pre-registration decision, not a lane's.

**Cost of the fine level, for planning:** L2 has spent 3414.02 s ExecutionTime x 8
ranks = 455.2 core-min for 777 of 6000 iterations; extrapolated, L2 completes at
~3,515 core-min (~58.6 core-h, ~7.3 h wall on 8 ranks). The 4x fine level is ~234
core-h and ~29 h wall on 8 ranks — affordable in core-minutes, but it is the schedule
risk, not the budget risk.

## Artifacts
- `/home/ubuntu/certonomous-runs/A3GC-L3/primal.log`, `primal.log.rc`
- `/home/ubuntu/certonomous-runs/A3GC-L3/meshgen/logCheckMesh.txt`
- `/home/ubuntu/certonomous-runs/A3GC-L3/constant/polyMesh/sets/lowQualityTetFaces.gz`
- `/home/ubuntu/certonomous-runs/A3GC-L3/genWingMesh.py`, `system/fvSolution`, `system/fvSchemes`, `runScript_a3gc.py`
- `/home/ubuntu/certonomous-runs/A3GC-L2/primal.log`, `meshgen/logCheckMesh.txt`, `genWingMesh.py` (read-only; solver live)
- `/home/ubuntu/certonomous-runs/A3-onera-m6-transonic/run_model_run3.log`, `runScript.py`, `genWingMesh.py`, `system/`
