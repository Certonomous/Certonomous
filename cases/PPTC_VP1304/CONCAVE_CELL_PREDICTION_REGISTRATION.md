# PPTC VP1304 — concave-cell population: PREDICTION REGISTERED BEFORE THE MESH IS BUILT

**Status: registered before any mesh of this act exists.** At the commit that introduces
this file, `cases/PPTC_VP1304/mesh/` does not exist, no `snappyHexMesh` has been run for
this act, and no `checkMesh` output for it exists anywhere on disk. That ordering is the
whole evidentiary content of this document: the numbers below are a **prediction**, made
from another case's measurement, and they can be wrong.

Companion to the frozen pre-registration
`cases/PPTC_VP1304/PPTC_VP1304_OPEN_WATER_PREREGISTRATION.md` (commit `09396b48`). This
file adds **no gate** and changes nothing frozen there. A failed prediction here is recorded
as a failed prediction and alters no gate, band or label.

---

## 1. Why this act and not another

`docs/NUMERICS_KNOWLEDGE.md` entry **N-X5**, dated addendum 1 (2026-09-12), scopes the
finding **by mesher** and names this act directly:

> **PPTC VP1304** — snappyHexMesh from an admitted STL, with a refinement box around the
> blades and a cylinder along the tip-vortex path. Inherits, **and it is the valuable
> one: it has not been meshed yet**, so it can register the expected population *before*
> its build rather than discovering it in a `checkMesh` afterwards.

This act's mesh (pre-registration §6.3) is exactly the configuration N-X5 scopes:
snappyHexMesh, local refinement, a refinement box around the blades, a cylinder along the
tip-vortex path 1D downstream, and 6 prism layers at growth ratio 1.2. **It will have this
population.** The only question this registration can honestly ask is whether the
*structure* N-X5 measured reproduces on a different geometry.

## 2. The basis, cited to its artifact and not to recollection

N-X5, measured on SUBOFF A1 L1: 3,268,613 cells, snappyHexMesh, local refinement plus 6
prism layers. Evidence at
`verification/runs/navier_class/SUBOFF_A1/L1/log.checkMesh.FULLFLAG` and
`constant/polyMesh/sets/concaveCells`; thresholds frozen before measurement in
`verification/campaign/SUBOFF_A1b_CONCAVE_FORCE_SHARE_PREREGISTRATION.md`, commit
`bc73dc0cae2063477d9d54ee5512b93a68be3249`.

| quantity measured there | value |
|---|---|
| concave cells | 65,027 = 1.989% of the mesh |
| concave cells on a volume jump > 4× across an internal face | **95.12%**, against a **15.93%** mesh baseline (enrichment 6.0×) |
| stability of that share at 2× / 4× / 6× thresholds | 97.56% / 95.12% / 92.81% |
| **converse:** cells on a jump that are concave | **11.88%** — a transition is NECESSARY, NOT SUFFICIENT |
| graded-surface cell share vs area share | 0.67% vs **0.0526%** — a factor of **12.7** |
| mean area of concave-owner faces ÷ mean face area | **0.162×** |

The discriminator is the **volume ratio across an internal face**, because an octree level
jump is 8× (isotropic halving in 3D) while prism-layer gradation is the `expansionRatio`,
here 1.2×. Two orders apart, so any threshold between them separates them with no judgement
call. N-X5 also records that `constant/polyMesh/cellLevel` does not survive
`reconstructParMesh`, so refinement level cannot be read and the volume-ratio test is the
substitute — that constraint applies here identically.

## 3. THE PREDICTIONS — falsifiable, each with a number

Measured on **every level** of the family (coarse, medium, fine) after it is built, and on
the full-360 coarse mesh.

| # | prediction | falsified if |
|---|---|---|
| **P1** | The concave population is **non-empty** on every level: concave cells > 0.1% of the mesh. | any level reports < 0.1%, or zero |
| **P2** | **≥ 85%** of concave cells sit on an internal face with volume ratio > 4×. | the share is < 85% |
| **P3** | That share is **stable within ±5 percentage points** across the 2×, 4× and 6× thresholds. | the spread exceeds 5 points |
| **P4** | The **converse holds**: **< 25%** of cells on a jump are concave — a transition is necessary and not sufficient. | ≥ 25% of jump cells are concave |
| **P5** | On the graded surfaces, the **AREA share** of faces whose owner cell is concave is **smaller than the CELL share by a factor > 3**. | the factor is ≤ 3, or the area share exceeds the cell share |
| **P6** | Mean area of those faces is **< 0.5×** the mean face area of the graded surfaces. | it is ≥ 0.5× |
| **P7** | The area share of concave-owner faces on the graded surfaces is **< 0.5%**. | it is ≥ 0.5% |

**The direction is the load-bearing part, not the magnitude.** N-X5's general statement is
that a cell-count share **overstates** the area-weighted share of a population concentrated
in refinement, because refined regions hold more cells of smaller size. P5, P6 and P7 test
that direction on a different geometry. **The magnitudes are expected to differ from
SUBOFF's** — this act has a 72° periodic passage, a tip-vortex refinement cylinder and a
much larger refined fraction than a hull, so the 12.7× factor is NOT predicted to reproduce
and is not what is being tested. Only its sign and its order are.

## 4. What is reported, and in which measure

Per pre-registration §6.4 and §6.5, and per N-X5's instruction that a count is **a locator,
never a magnitude**:

> **The AREA share on the graded surfaces (`blades`, `hub`, `cap`, `shaft`) is what is
> reported beside any force result. The cell share is reported too, and explicitly labelled
> a locator.** A concave-cell statistic is never weighed against KT or KQ in cell units.

This sits beside the pre-registration's own volume gate (Sanaa's cell-volume growth cap of
1.25, §6.4), which is a **separate and stricter** constraint than anything here; a mesh
inside that cap will have a *smaller* concave population than SUBOFF's, and P1 exists
precisely so that "we found none" cannot pass unexamined.

## 5. READER CONTROL — planted-zero doctrine applied to the area reader

CLAUDE.md rule 3: a zero from a reader not shown able to see a non-zero is not evidence.
P5, P6 and P7 are all **small numbers produced by an area reader**, which is exactly the
shape of answer the rule exists to distrust. N-X5's own measurement was believable because
its area reader first reproduced the registered hull wetted area to a relative error of
1.49e-16. The same control is registered here, and it is a **refusal**, not a warning:

1. **Before** any concave-area share is computed, the area reader sums the wetted area of
   the graded patches from the mesh and must reproduce the **registered surface area of the
   admitted geometry** — measured from the admitted CAD in
   `GEOMETRY_ADMISSION_RECORD.md` — to within the tessellation tolerance recorded there.
2. The reader is then handed a **planted set**: a known, non-empty set of faces on the
   graded surfaces whose summed area is computed independently. It must return that area.
3. **If the reader cannot reproduce the known non-zero, it refuses (exit 2)** and no share
   is reported. It does not degrade to a warning, and no number from it enters any record.

## 6. Instrument

The volume-ratio-across-a-face test is computed directly from `constant/polyMesh`
(`owner`, `neighbour`, cell volumes), not from `cellLevel`, for the reason N-X5 records.
The same reader supplies the max adjacent-cell volume ratio that pre-registration §6.4
requires for Sanaa's 1.25 growth cap, so one instrument serves both and is verified once.
It is stored under this case directory, never cited from a scratch path (L-186).
