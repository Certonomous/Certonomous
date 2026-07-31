# Generator finding: `genAirFoilMesh.py`'s pyHyp extrusion lets maximum cell aspect ratio worsen under refinement

**Status: not filed anywhere.** Written so it can stand on its own, independent of whatever investigation
found it, per the standing rule that a real generator behaviour someone will hit "from the outside" is
worth recording in its own right, not buried inside the case that happened to surface it.

## Summary

`work/NACA0012_Airfoil_Incompressible/genAirFoilMesh.py` and its "refined" twin
(`work_refined/NACA0012_Airfoil_Incompressible_refined/genAirFoilMesh.py`) both build a NACA0012 mesh via
`pyHyp` hyperbolic extrusion from a profile curve. The refined version doubles surface point density and
halves the first wall-normal cell height relative to the coarse version, while leaving `pyHyp`'s own
smoothing parameters (`epsE`, `epsI`, `theta`, `volCoef`, `volBlend`, `volSmoothIter`) completely
unchanged. Measured directly (`checkMesh -allGeometry`, stock OpenFOAM, both meshes already on disk, no
solve): the **maximum cell aspect ratio anywhere in the mesh gets worse, not better, under this
refinement — 97.9 → 167.5**, a genuine, reproducible property of the generator, not an artifact of any
one measurement. Maximum non-orthogonality also worsens (22.7° → 27.0°), while maximum skewness improves
(1.43 → 0.86) and every AVERAGE metric improves — so the effect is real but localized to specific cells,
not visible in a whole-mesh summary statistic someone would naturally check first.

**Someone refining a mesh built by this generator, expecting quality to improve uniformly (the normal,
reasonable expectation), will be wrong for at least these two metrics, at exactly the cells where it
would matter most for a wall-resolved viscous solve.**

## How it was found

Found while investigating an unrelated gradient-accuracy defect on the NACA0012 A1 case (two interior
leading-edge-adjacent shape design variables carry a real, step-independent 9-16% adjoint-vs-finite-
difference disagreement that WORSENS under mesh refinement — see `PROOF.md` §19.2 and
`DAFOAM_CASE_STATUS.md` for that separate investigation). The refinement-worsening signature motivated
checking whether a mesh QUALITY metric, as opposed to cell SIZE, might be worsening somewhere under the
same refinement — which led to reading `genAirFoilMesh.py` directly rather than assuming the refined mesh
was uniformly better. **This generator finding is recorded here as a property of the tool, independent of
whether it turns out to explain that gradient defect** — direct measurement (`PROOF.md` §19.2) showed it
does NOT cleanly discriminate the flagged design variables from clean controls, so it is very likely not
that defect's cause. It is filed here anyway, because the aspect-ratio behaviour itself is real,
reproducible, and surprising regardless of that outcome.

## The mechanism, as far as it can be stated without pyHyp's own internals

`genAirFoilMesh.py`'s user-facing refinement (comments in the file, comparing the coarse and refined
versions):

| parameter | coarse | refined | change |
|---|---|---|---|
| `dX1PS`/`dX1SS` (first chordwise spacing from LE) | 0.005 | 0.0025 | 2x finer |
| `Alpha1PS`/`Alpha1SS` (LE clustering growth rate) | 1.2 | 1.15 | slower growth, MORE points concentrated near LE |
| `dXMaxPS`/`dXMaxSS` (max chordwise spacing) | 0.02 | 0.01 | 2x finer |
| `NpExtrude` (wall-normal extrusion layers) | 33 | 65 | ~2x more layers |
| `yWall` (first wall-normal cell height) | 4e-3 | 2e-3 | 2x finer |
| `epsE`, `epsI`, `theta`, `volCoef`, `volBlend`, `volSmoothIter` (pyHyp smoothing) | unchanged | unchanged | **not scaled with resolution** |

Every USER-FACING spacing parameter was refined together, in a way that looks like it should preserve
cell shape (both chordwise and wall-normal spacing roughly halved). But `pyHyp`'s hyperbolic march is a
smoothing-regularized PDE-marching process, and its smoothing strength (`epsE`/`epsI`/`volSmoothIter`)
was held fixed while the geometry it has to track (a fixed leading-edge radius of curvature) is now
sampled at roughly double the point density. A fixed amount of smoothing applied to a more tightly-packed
representation of a fixed curvature is a plausible, concrete route to the march producing more distorted
(higher aspect ratio) cells exactly where the curvature is highest — consistent with what was measured
(the true LE nose band showed the largest aspect-ratio growth factor, x1.92, of four chordwise bands
checked). **This mechanism is stated as a plausible explanation from reading the generator's own
parameters, not confirmed by reading pyHyp's own source or by an ablation on its smoothing options** — an
honest distinction, not yet closed.

## Measured evidence

`checkMesh -allGeometry -writeAllFields` (stock OpenFOAM 2606, no container — pure mesh geometry, does
not depend on the DAFoam build), both meshes as they already exist on disk:

| | coarse (4032 cells) | refined (14720 cells) | direction |
|---|---|---|---|
| Max cell aspect ratio | 97.87 | 167.50 | **worse** |
| Max non-orthogonality | 22.75° | 26.96° | **worse** |
| Max skewness | 1.432 | 0.862 | better |
| Mean non-orthogonality | 2.548° | 1.897° | better |

Chordwise-banded max aspect ratio (`work/NACA0012_Airfoil_Incompressible/probeMeshMetricRefinement.py`,
new script, `probemeshmetricrefinement_run1.log`):

| band | coarse max | refined max | growth factor |
|---|---|---|---|
| true LE nose, x ∈ [-0.02, 0.05] | 16.49 | 31.62 | **x1.92** (largest of the four bands) |
| x ∈ [0.20, 0.30] | 12.88 | 20.30 | x1.58 |
| x ∈ [0.45, 0.55] | 10.27 | 20.28 | x1.98 |
| x ∈ [0.70, 0.80] | 15.44 | 20.28 | x1.31 |

The growth factor is not perfectly monotonic with distance from the LE (the x∈[0.45,0.55] band shows
slightly more growth than the LE-adjacent x∈[0.20,0.30] band) — the true LE nose band's growth is the
largest of the four, but the effect is not confined to a single narrow region; it is broader than "only
at the leading edge," consistent with a generator-wide smoothing/resolution interaction rather than a
purely local geometric singularity.

## What this does and does not establish

- **Established:** maximum cell aspect ratio is a real, reproducible, measured property of this
  generator's output that gets WORSE, not better, under a refinement a user would reasonably expect to
  improve mesh quality uniformly. This is independent of, and does not require, the gradient-defect
  investigation that led to finding it.
- **Not established:** the specific pyHyp-internal cause (smoothing-vs-point-density interaction is the
  best-supported hypothesis from reading the generator's own parameters, not confirmed against pyHyp's
  source). Also not established: whether this same behaviour appears in other pyHyp-based generators in
  this codebase, or is specific to this profile/parameter combination — not checked this session.

## What to check before trusting a refinement from this generator

1. **Do not assume `checkMesh`'s global maximum improves under refinement just because average metrics
   do.** Check the maximum, not just the mean — the mean genuinely does improve here, which would mask
   the effect for anyone checking only a summary statistic.
2. If a wall-resolved viscous solve is sensitive to near-wall cell shape (most are), check aspect ratio
   specifically, banded by chordwise (or equivalent) location, not just the single global maximum, since
   the worst cells were not always at the same location as the mesh's own global-max cell (which sat at
   the blunt trailing edge in both meshes tested here, not the leading edge).
3. If refining specifically to improve resolution in a high-curvature region, consider whether pyHyp's
   smoothing options (`epsE`, `epsI`, `theta`, `volSmoothIter`) need to scale with the refinement too,
   rather than being left at their coarse-mesh values — not tested this session, but a concrete,
   actionable next step if this generator is refined again.

## Evidence

- `work/NACA0012_Airfoil_Incompressible/genAirFoilMesh.py`,
  `work_refined/NACA0012_Airfoil_Incompressible_refined/genAirFoilMesh.py` — the generator itself, coarse
  and refined parameter sets (comments in the refined version document the deltas)
- `work/NACA0012_Airfoil_Incompressible/probeMeshMetricRefinement.py` — new script, LE-band mesh-metric
  comparison
- `probemeshmetricrefinement_run1.log` — raw output backing the tables above
- `PROOF.md` §19.2 — the gradient-defect investigation this was found during (that investigation's own
  verdict on whether this explains the defect: measured, real, non-discriminating — see that section for
  the full reasoning, kept separate from this generator-level finding per the coordinator's direction)

---

## Independent cross-check, 2026-07-30 (roadmap 4G)

This finding was re-measured from scratch by a separate investigation looking into the TMR ladder's own
"insane mesh aspect ratio". Full record: `demo-output/website/campaign/4G_tmr_mesh_aspect_ratio.md`.

**Confirmed.** Both numbers reproduce exactly on a clean `checkMesh -allGeometry`:
97.87218721638968 → 167.4971796573039, with the global-max cell at the blunt trailing edge (x ≈ 1.0000
and x ≈ 0.9988) in both meshes, precisely as stated above. The measurement is sound.

**Two clarifications that change how the number should be read, neither of which contradicts the finding:**

1. **These are 3D meshes, so the number is not computed the way a 2D mesh's is.** `checkMesh` reports
   `Mesh has 3 geometric (non-empty/wedge) directions (1 1 1)` for both. OpenFOAM's aspect ratio
   (`primitiveMeshTools::cellClosedness`) takes an extra volume-based branch when `nDims == 3`, and its
   directional loop is gated on `meshD[dir] == 1`, so a 3D mesh **includes** the span while an
   `empty`-patched 2D mesh **excludes** it. A pyHyp "167" and a 2D TMR "20 million" are therefore not the
   same quantity, and comparing them numerically is a mistake waiting to happen.
2. **Worsening under refinement is normal here, not anomalous.** NASA Langley's own TMR-distributed
   NACA0012 reference grids — the grids CFL3D and FUN3D use — were converted and measured with the same
   tool and show the same behaviour, much more strongly: max aspect ratio **20,650,841 → 26,446,227 →
   29,899,837** across their 113x33, 225x65 and 449x129 rungs. Refinement halves near-wall spacing while
   the farfield extent stays fixed, so the ratio of longest to thinnest cell must grow. **"Max aspect
   ratio worsens under refinement" is therefore a property of reference-grade wall-resolved grid families
   in general and cannot, on its own, indicate a generator defect.**

For scale: these meshes report `Max aspect ratio = 97.87 ... OK` and `167.50 ... OK` — they **pass**
checkMesh's aspect-ratio check, which every TMR ladder mesh fails. A large part of the magnitude
difference is simply domain extent: ~16 chords here versus ~500 chords for NASA's grids.

**Still open, and still worth doing:** the `epsE`/`epsI`/`theta`/`volSmoothIter` scaling ablation this
document proposes as its concrete next step was **not** run — pyHyp is not installed on the 4G host
(`import pyhyp` → `ModuleNotFoundError`). The mechanism remains an unconfirmed hypothesis, exactly as
stated above. Nothing in the cross-check settles it either way.
