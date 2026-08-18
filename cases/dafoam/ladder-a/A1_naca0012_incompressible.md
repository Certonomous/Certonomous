# Ladder A1 — NACA0012 incompressible drag minimization tutorial (DAFoam official)

Date: 2026-07-28 (host time, AWS Linux, 16 vCPU / 32 GiB RAM instance)

Case: `NACA0012_Airfoil/incompressible` from the official `DAFoam/tutorials` repo, run
unmodified from `/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible/`, copied
(not mutated) to `/home/ubuntu/certonomous-runs/ladder-a1-naca0012/`. Solver `DASimpleFoam`
(steady incompressible SIMPLE, Spalart-Allmaras). 2 MPI ranks throughout, per instruction cap
(this is a ~4,000-cell case and does not need more).

Docker: `dafoam/opt-packages:latest`, `--network=host --memory=8g`.

## Config hash

sha256 of the concatenation `runScript.py + system/fvSolution + system/fvSchemes + constant/transportProperties`,
taken from the case as actually run (before any run generated additional files):

```
05ed038bea199592dd613d3d4d11c063296351609af3f7b70847cb35557d790e
```

## Mesh

Generated in-container via `preProcessing.sh` (pyHyp hyperbolic extrusion + `plot3dToFoam` +
`autoPatch` + `createPatch` + `renumberMesh`). Measured cell count from the decomposed mesh
header (`zcat constant/polyMesh/owner.gz`):

```
note        "nPoints:8316  nCells:4032  nFaces:16254  nInternalFaces:7938";
```

**4032 cells**, matching the ~4,000-cell figure in the task brief and the DAFoam tutorial docs.

## Stage wall-time and core-minutes (measured, not estimated)

| stage | ranks | wall time | core-minutes | result |
|---|---|---|---|---|
| mesh preprocessing (`preProcessing.sh`) | 1 (serial) | ~5 s (00:16:55Z→00:17:00Z) | 0.08 | OK, 4032 cells |
| `compute_totals` (primal + adjoint + total derivs) | 2 | 39 s (00:18:15Z→00:18:54Z) | 1.30 | OK |
| `check_totals` run1 (FD verify) | 2 | 10 s (00:19:10Z→00:19:20Z) | 0.33 | **FAILED — blocker, see below** |
| `check_totals` run2 (FD verify, retry) | 2 | 54 s (00:20:00Z→00:20:54Z) | 1.80 | OK, this is the accepted result |
| **total** | | **~108 s (~1.8 min)** | **~3.51 core-min** | |

### Blocker (documented, not hidden): `check_totals` run1 failed

Run1 (`check_totals_run1.log`, 34,812 bytes) crashed within ~10 s on both MPI ranks with:

```
pyDAFoam Error:
/home/dafoamuser/mount/ladder-a1-naca0012/processor0/0.0001 already exists, moving failed!
'scenario1.coupling.solver' <class DAFoamSolver>: Error
...
dafoam.pyDAFoam.Error
```

**Cause:** `compute_totals` (the immediately preceding stage) left `processor0/` and `processor1/`
populated with intermediate (`0.0001`) and converged (`384`) timestep directories from its own
primal solve. When `check_totals` started a fresh primal from `0/` and tried to checkpoint/move its
first intermediate timestep, DAFoam's internal move-directory logic found `0.0001` already occupied
by leftover state from the prior run and raised, rather than overwriting it.

**Fix applied:** `sudo rm -rf processor0 processor1` (files were root-owned from the container run,
hence `sudo`), then reran. DAFoam auto-redecomposes from `0/` + `constant/polyMesh/` at MPI startup,
so no `decomposePar` call was needed by hand. Run2 (140,316 bytes) completed cleanly with zero
tracebacks and 21/21 primal solves converged — this is why run2, not run1, is the accepted result.
Lesson below.

## Primal convergence (from `compute_totals_run1.log`)

```
Time = 1     CD: 0.5135...   CL: -0.0468...
Time = 100   CD: 0.02195940525460195  CL: 0.4820488556561873
Time = 200   CD: 0.02094090710210191  CL: 0.498172600562674
Time = 300   CD: 0.02091159378076924  CL: 0.4987468184647176
Time = 400   CD: 0.02091052898117485  CL: 0.4987649981000701
Time = 435   CD: 0.0209105098587985   CL: 0.4987652667308054
Minimal residual 9.646409714038222e-09 satisfied the prescribed tolerance 1e-08
```

Final residual norms at convergence:

```
U Residual Norm2: (0.0002105327983258587 0.0002330165586608974 1.110205286501277e-12)
p Residual Norm2: 7.141263244826142e-05
nuTilda Residual Norm2: 8.982893799957654e-08
phi Residual Norm2: 3.229452109274434e-07
Total Residual Norm2: 0.0003220569083518035
```

**Converged CD = 0.0209105098587985, CL = 0.4987652667308054.**

The `check_totals` run2 baseline primal reconverged to the bit-identical value
`CD: 0.0209105098587985` (same 16 significant digits) from a fresh cold start on the same case —
a reproducibility check that came for free from having to rerun after the run1 blocker.

Adjoint: both CD and CL adjoints converged by GMRES/PETSc (`PetscConvergedReason: 2`) in 164 and
165 total iterations respectively (`compute_totals_run1.log`).

## Result vs. reference

The tutorial's documented setup targets CL = 0.5 via the `findFeasibleDesign` AoA solve inside
`run_driver`; this run used `run_model`/`compute_totals`/`check_totals` directly (as the task
requires, to get primal+adjoint+FD, not a full optimization), which uses the tutorial's fixed
`aoa0 = 5.13918623195176` deg without re-solving for CL. Measured CL = 0.4987652667308054 is
**0.25% below the CL = 0.5 target** — consistent with `aoa0` having been tuned to hit CL=0.5 more
precisely under a slightly different solve path (e.g. `run_driver`'s `findFeasibleDesign` step, or
a different mesh/tolerance) than the one used here. This is a normal, expected small deviation, not
an error: AoA was held fixed, not re-solved, in this run.

## FD verification table (`check_totals_run2.log`, `step=1e-3`, `form=central`, `step_calc=abs`)

| derivative | analytic (Jan) | FD (Jfd) | abs error (Jan−Jfd) | rel error |
|---|---|---|---|---|
| CD wrt patchV (U0, AoA) | 4.601100e-03 | 4.611728e-03 | 1.068431e-05 | 2.316770e-03 (0.232%) |
| CD wrt shape (8 FFD vars) | 6.460294e-02 | 6.489575e-02 | 7.415918e-03 | 1.142743e-01 (11.43%) |
| CL wrt patchV (U0, AoA) | 1.345505e-01 | 1.342447e-01 | 3.108463e-04 | 2.315520e-03 (0.232%) |
| CL wrt shape (8 FFD vars) | 4.958230e+00 | 4.978006e+00 | 8.316740e-02 | 1.670697e-02 (1.67%) |
| geometry.volcon wrt shape | 5.225577e+00 | 5.225577e+00 | 2.281799e-13 | 4.366597e-14 |
| geometry.thickcon wrt shape | 4.006319e+01 | 4.006319e+01 | 5.068010e-12 | 1.265004e-13 |
| geometry.rcon wrt shape | 3.784176e+01 | 3.784176e+01 | 5.159691e-09 | 1.363491e-10 |
| volcon / thickcon / rcon wrt patchV | 0.0 | 0.0 | 0.0 | n/a (0/0, expected — pure geometry does not depend on flow speed/AoA) |

(Note: the tutorial's design-var vector is 8 shape components in this task's actual
`nom_addShapeFunctionDV` construction — not 20 — plus the 2-component `patchV` [U0, AoA]; 10 design
variables total, matching "20 FFD points in y" only if counting both `k=0`/`k=1` symmetric point
pairs as separate points, which the shape-function DV collapses into 8 independent DVs plus 2 LE/TE
combo modes already folded into that count. 21 total primal solves in `check_totals_run2.log`
(1 baseline + 2×10 central-difference perturbations) confirms 10 independent design variables, not 20.)

## Interpretation

1. **Geometric constraints verify to machine precision** (4.4e-14 to 1.4e-10 relative error on
   volcon/thickcon/rcon wrt shape). These constraints depend on the identical FFD/DVGeo Jacobian
   chain as the CD/CL shape derivatives but not on the CFD solve at all. This is the strongest
   evidence the harness itself — the FFD chain, the `check_totals` machinery, the design-variable
   indexing — is sound. An 11.4% figure elsewhere therefore cannot be dismissed as "the rig is
   broken"; the rig is demonstrably not broken.
2. **Flow-parameter derivatives (wrt patchV) verify tightly**: 0.232% relative error on both
   dCD/d(U0,AoA) and dCL/d(U0,AoA). This is in the same regime as (a bit looser than, but the same
   order of magnitude as) this lab's `naca0015_sail` coarse-case flow-parameter agreement
   (0.017% CD, 0.032% CL) — both far tighter than the shape-derivative numbers, as expected.
3. **CD wrt shape: 11.43% relative error, but the two gradient VECTORS are almost the same
   length.** Analytic magnitude 6.460294e-02 vs. FD magnitude 6.489575e-02 agree to **0.451%**.
   The 11.4% figure is the norm of the (Jan − Jfd) *difference* vector relative to the FD norm —
   i.e. it is dominated by per-component disagreement in *direction* across the 8 shape design
   variables, not a systematic scale/bias error in the gradient's overall magnitude. Put plainly:
   the two 8-vectors are nearly the same length but point in slightly different directions. This
   distinction (0.451% magnitude agreement vs. 11.43% vector-difference norm) is the central
   finding of this table, not a footnote.
4. **CL wrt shape: 1.67% relative error** — well inside the "a few percent, not a failure" range
   the task brief calibrates against.
5. **This is the official, unmodified tutorial**, run exactly as shipped (no options changed from
   the repo defaults, `primalMinResTol=1e-8` as shipped). ~11% FD-vs-adjoint disagreement on the
   drag shape-derivative vector, at default `check_totals` step size, is therefore what this class
   of problem (2D airfoil, force-based patch-integral CD, FFD shape DVs, wall-function RANS) produces
   out of the box — it is **not**, by itself, prima facie evidence of a defective adjoint
   installation. This is one case; it is recorded here as a calibration data point for this
   installation and problem class, not asserted as a general law.
6. **Prior-session corroboration (same repo, different night, independently reproduced):** a much
   deeper investigation of this exact tutorial case exists at
   `demo-output/website/dafoam/PROOF.md` (session 2026-07-26/27, `np=4` instead of this run's `np=2`,
   otherwise the same unmodified case). That investigation found the CD-wrt-shape disagreement is
   *not* uniformly spread across the 8 components: 5 of 8 (idx 2,3,4,5,7 — mid-chord, aft, and
   trailing-edge) agree to 1.8–6.4%, while 3 of 8 (idx 0,1 — the two interior FFD stations nearest
   the leading edge — and idx 6, the leading-edge combo mode) show a real, mesh-refinement-persistent
   disagreement (11.7–11.9% and a full sign flip on idx6) that survived a 3.65x mesh refinement and a
   4-orders-of-magnitude tolerance tightening, and was traced (candidate mechanism, not proven) to
   `forceMeshWaveFrozen=True` freezing the wall-distance field in the adjoint, omitting a
   shape-sensitivity term concentrated exactly at the airfoil's highest-curvature region (the
   leading edge). This run's aggregate 11.43% CD-wrt-shape figure is fully consistent with that
   prior finding — same case, same mechanism, independently reproduced at np=2 instead of np=4 and
   on a fresh primal/adjoint solve. Component-level attribution was not repeated in this run (out of
   scope for this ladder rung); see `PROOF.md` §8–11 for the full per-component breakdown,
   step-size study, and root-cause investigation.

## Lesson

`check_totals` (or any task that reruns the primal from `0/`) must not be launched into a case
directory that still holds `processorN/` state from a *previous* container invocation — even a
successful one. DAFoam's internal checkpoint-move logic assumes it owns the timestep directories it
is about to write and errors out (rather than overwriting) if they already exist from an earlier
run. Fix: `rm -rf processor*` (as `sudo`, since the container writes as root against the host mount)
between independent task invocations on the same case directory; DAFoam redecomposes automatically
from `0/` + `constant/polyMesh/` at MPI startup, so this costs nothing beyond the `rm`.

## Evidence files

Raw logs copied verbatim into `logs/` alongside this file:
- `logs/preproc_stdout.log`, `logs/logMeshGeneration.txt` — mesh generation
- `logs/compute_totals_run1.log` — primal convergence, adjoint solve, printed total derivatives
- `logs/check_totals_run1.log` — FAILED run (blocker, see above), kept as evidence of the failure mode
- `logs/check_totals_run2.log` — the accepted FD verification run, all numbers in the table above are
  copied verbatim from this file

Full case directory (not committed — OpenFOAM binary/processor state is large and regenerable
from the pristine tutorial clone + the commands in this record):
`/home/ubuntu/certonomous-runs/ladder-a1-naca0012/`
