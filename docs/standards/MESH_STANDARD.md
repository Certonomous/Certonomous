# Certonomous Mesh Standard

Version 1.0, dated 2026-07-25. Produced by the overnight reading program (R1).
Governs every mesh-quality gate the lab enforces before a solve is admitted as
evidence. Gates change only through the governed path: an edit to
`docs/physics_rules.yaml` carrying its citation, plus a proposal in the agenda
inbox so the owner sees the change. Enforcement code is never edited to move a
threshold silently.

## 1. Purpose and scope

A mesh gate exists to answer one question before solver time is spent: can the
discretization on this mesh support the accuracy claim the result will carry?
This standard states every gate the lab enforces, the literature or source-code
basis for its value, the failure mode it prevents, and the prescribed action on
breach. It also calibrates the bands against what reference-grade grids
actually achieve, using the NASA TMR flat-plate grids on disk under
`models/tmr/` and their checkMesh reports under
`demo-output/website/tmr/runs/*/log.checkMesh`.

## 2. Where the gates live

- Values: `docs/physics_rules.yaml`, section `mesh_quality` (added 2026-07-25
  by this program, with citations inline).
- Enforcement: the geometry workflow (`sdk/workflows/geometry_study.py`,
  `MAX_NON_ORTHOGONALITY`, `MAX_SKEWNESS`, `mesh_validity`,
  `enforce_boundary_skewness`). Wiring the workflow to read the yaml section is
  proposed, not done here; the values written to the yaml match what the
  workflow enforces today, so there is no divergence window.

## 3. Gates

### 3.1 Max non-orthogonality: hard gate 70 degrees, warning band 65 to 70

- Basis: checkMesh itself warns at 70 degrees; the threshold is
  `nonOrthThreshold_ = 70` in the OpenFOAM source
  (`src/OpenFOAM/meshes/primitiveMesh/primitiveMeshCheck/primitiveMeshCheck.C`,
  v2606 tree on disk). snappyHexMesh generates to `maxNonOrtho 65`
  (`etc/caseDicts/meshQualityDict`) and relaxes to 75 only during layer
  addition. 65 is the generation constraint, 70 the acceptance threshold.
- Failure mode: above 70 degrees the non-orthogonal correction to the
  Laplacian becomes large and explicit; with zero or few correctors the
  diffusion term loses accuracy first and boundedness second, and steady
  convergence stalls or oscillates.
- Action: above 70, no validated force from this mesh; the numerical channel
  carries the breach and the fidelity chip is capped. Between 65 and 70, solve
  but record the warning.
- Lab evidence: motorcycle case at max non-ortho 65.0 converged with one
  corrector; the airliner-class hex meshes sit far below the gate.

### 3.2 Max skewness: hard gate 4, boundary faces included

- Basis: checkMesh fails skewness at 4 (`skewThreshold_ = 4`, same source
  file). snappyHexMesh generation allows `maxInternalSkewness 4` but
  `maxBoundarySkewness 20`; the lab deliberately enforces 4 on boundary faces
  as well (`enforce_boundary_skewness(MAX_SKEWNESS)` in the geometry workflow)
  because forces are integrated on boundary faces, exactly where the upstream
  default is loosest.
- Failure mode: skewness moves the face interpolation point away from the face
  center; convective fluxes pick up a first-order error that concentrates on
  the very patches the force report reads.
- Action: above 4, trust is capped and the mesh channel carries the value as
  measured; the run may proceed for ranking purposes only.
- Lab evidence: motorcycle case max skew 8.94 on 13 faces capped the result
  below VALIDATED even with converged forces; two overnight missions recorded
  the same cap at skew 5.06 and 8.94.

### 3.3 Aspect ratio: advisory at 1000, never a lone rejection

- Basis: checkMesh reports high-aspect-ratio cells above
  `aspectThreshold_ = 1000` (same source file) but counts this as a failed
  check without stopping anything.
- Calibration, and why this gate must stay advisory: the NASA TMR flat-plate
  grids are reference-grade by construction, and their checkMesh reports on
  disk measure max aspect ratio 74041 (coarse, 816 cells), 69043 (medium,
  3264 cells), 66643 (fine, 13056 cells), each with max non-orthogonality 0
  and skewness at machine precision. The fine grid resolves the wall to
  average y-plus 0.14 and reproduces the flat-plate drag benchmark. A hard
  aspect-ratio gate at 1000 would reject every reference-grade wall-resolved
  RANS grid the lab owns.
- The defensible rule: high aspect ratio is legitimate where the anisotropy is
  aligned with a resolved direction on orthogonal cells (wall-normal
  boundary-layer grids), and dangerous where it coincides with
  non-orthogonality or skew. Gate written to `physics_rules.yaml`: aspect
  ratio above 1000 requires an alignment justification on the record; aspect
  ratio above 1000 together with non-orthogonality above 60 degrees or
  skewness above 2 is a flag for investigation.
- Failure mode prevented: on non-orthogonal or skewed cells, extreme
  anisotropy amplifies the interpolation and correction errors and produces
  stiff, poorly conditioned matrices that stall linear solvers.

### 3.4 Volume ratio: proposed gate, warn below 0.01

- Basis: snappyHexMesh refuses adjacent-cell volume ratios below
  `minVolRatio 0.01` at generation (`etc/caseDicts/meshQualityDict`).
  checkMesh reports the metric under `-allGeometry`. The lab currently has no
  volume-ratio gate; this standard proposes adopting 0.01 as a warning
  threshold, carried in `physics_rules.yaml` and surfaced through proposal
  `r1-mesh-gate-extension`.
- Failure mode: abrupt cell-size jumps degrade linear interpolation weights
  and multigrid coarsening; the error appears as local wiggles near refinement
  boundaries and slow pressure convergence.

### 3.5 Informational metrics, recorded but not gated

- Cell determinant (snappy generation floor `minDeterminant 0.001`) and face
  interpolation weight (`minFaceWeight 0.05`): recorded when checkMesh
  reports them; persistent values at the floor accompany the failure modes
  above rather than causing new ones.

## 4. Calibration table: what reference-grade grids achieve

From `demo-output/website/tmr/runs/*/log.checkMesh` and `record.json`
(OpenFOAM v2606, NASA TMR 2-D zero-pressure-gradient flat plate):

| Grid | Cells | Max non-ortho | Max skewness | Max aspect ratio | Cd |
| --- | --- | --- | --- | --- | --- |
| Coarse | 816 | 0 | 3.3e-15 | 74041 | see record.json |
| Medium | 3264 | 0 | 8.0e-15 | 69043 | see record.json |
| Fine | 13056 | 0 | 2.1e-14 | 66643 | 0.0028343 |

Reading: reference grids are orthogonal and unskewed to machine precision and
buy wall resolution with aspect ratio, not with cell count. The lab's gates on
non-orthogonality and skewness are the load-bearing ones; aspect ratio is a
context signal.

## 5. Change control

1. A gate value changes only in `docs/physics_rules.yaml`, with the citation
   in a comment beside the number.
2. Every change is mirrored by a proposal JSON in the agenda inbox so the
   owner sees it before any surface shows it.
3. A test that pins a gate value is updated only when the new value is the
   cited, defensible one, and the update says so.

## Sources

- OpenFOAM v2606 source, primitiveMeshCheck.C, checkMesh thresholds.
- OpenFOAM v2606 source, caseDicts meshQualityDict, snappyHexMesh generation
  defaults.
- NASA Turbulence Modeling Resource, 2-D zero-pressure-gradient flat plate
  grids, as meshed and checked on disk under `models/tmr/` and
  `demo-output/website/tmr/runs/`.
- Certonomous Numericist knowledge base, `docs/NUMERICS_KNOWLEDGE.md`,
  validated facts 2 and 7.
