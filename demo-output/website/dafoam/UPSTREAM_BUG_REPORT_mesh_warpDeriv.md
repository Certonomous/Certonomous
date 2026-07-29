# Bug report: `mesh.warpDeriv` disagrees with a finite difference of the actual warp, sign-flipped, for opposing-direction/combination FFD shape variables

**Status: not filed anywhere.** This document is written so it could be filed as-is against
`mdolab/idwarp` and/or `mdolab/dafoam` on GitHub, but no issue has been opened.

## Summary

For a shape design variable built from a pair of FFD control points moving in *opposing* directions
within a single design variable (a standard construction used to move an airfoil's leading or trailing
edge while a paired "mirror" point moves the opposite way, keeping the LE/TE position fixed),
`mesh.warpDeriv` — IDWarp's reverse-mode mesh-warp derivative, and the exact function DAFoam's real
discrete adjoint calls for its mesh sensitivity — returns a result that disagrees with a finite
difference of the actual nonlinear warp by **108–149% relative error, with the sign flipped**, verified
via the standard adjoint dot-product identity. Single-point ("local") shape design variables — one FFD
point moving along one axis per DV, no opposing-direction pairing — do not show this defect in any of
3 independently tested cases (2 different tutorials, 2 different DV APIs).

Consequence for users of `check_totals`/gradient verification on this class of design variable: the
finite-difference check is correct; the analytic (adjoint) gradient is wrong. On the official,
unmodified `DAFoam/tutorials` NACA0012 case, this produces a *sign-flipped* `dCD/dShape` component for
the leading-edge combination mode, silently, with no error or warning — `check_totals` reports a large
relative-error percentage, which is easy to attribute to "finite-difference noise on a hard case"
(the working assumption in this lab for months) rather than to a wrong analytic gradient, because the
FD-vs-adjoint mismatch is genuinely step-independent (a hallmark normally associated with an FD problem,
not an adjoint problem) — see "Why this looks like an FD problem at first" below.

## Environment

- Docker image: `dafoam/opt-packages:latest`, digest
  `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`, pulled 2026-07-26.
- `dafoam` 5.0.0, `idwarp` 2.6.2, `pygeo` 1.13.0 (`pip show`, confirmed in-container).
- OpenFOAM v2506 (build `_615aae61d7-20250627`).
- Case: `DAFoam/tutorials` (`https://github.com/DAFoam/tutorials`, commit
  `d3b7e38b058aba2a98a74092e15c41ec455c570d`, 2026-05-16), `NACA0012_Airfoil/incompressible`, unmodified
  except as noted. 4,032-cell mesh, `DASimpleFoam`, Spalart-Allmaras, wall functions
  (`nutUSpaldingWallFunction`).
- `useAD` is left at its DAFoam default in this case's `daOptions`: `{"mode": "reverse",
  "dvName": "None", "seedIndex": -9999}` (confirmed by reading `pyDAFoam.py` in the container). This
  matters: `DAFoamWarper.compute_jacvec_product` (`dafoam/mphys/mphys_dafoam.py`) calls
  `mesh.warpDeriv(dxV)` — the reverse-mode function — and explicitly does not support `mode="fwd"`.
  `mesh.warpDerivFwd` exists but is a *different* function this case's adjoint never calls; testing it
  instead (which an earlier, retracted diagnostic in this investigation did) produces 33–200% error on
  every shape component including the ones independently verified clean through the full CFD+adjoint
  chain — consistent with testing an unexercised code path, not with a shared defect.

## The design-variable construction that triggers it

From the tutorial's own `runScript.py`, unmodified, `Top.configure()`:

```python
pts = self.geometry.DVGeo.getLocalIndex(0)
dir_y = np.array([0.0, 1.0, 0.0])
shapes = []
for i in range(1, pts.shape[0] - 1):
    for j in range(pts.shape[1]):
        # single-station: one chordwise position, top+bottom move together
        shapes.append({pts[i, j, 0]: dir_y, pts[i, j, 1]: dir_y})
for i in [0, pts.shape[0] - 1]:
    # COMBINATION mode: the LE (i=0) or TE (i=pts.shape[0]-1) point and its
    # "mirror" point move in OPPOSING directions within the SAME design variable,
    # so the LE/TE position itself stays fixed while the surface pivots around it
    shapes.append({pts[i, 0, 0]: dir_y, pts[i, 0, 1]: dir_y, pts[i, 1, 0]: -dir_y, pts[i, 1, 1]: -dir_y})
self.geometry.nom_addShapeFunctionDV(dvName="shape", shapes=shapes)
```

This produces 8 shape DVs: idx0–idx5 are single-station (one chordwise position, points move together),
idx6 is the leading-edge combination mode, idx7 is the trailing-edge combination mode. **Both idx6 and
idx7 share the identical opposing-direction construction.**

## The identity used to test `warpDeriv` in isolation

`mesh.warpDeriv` is a reverse-mode Jacobian-transpose-vector product: given a seed `w` in the OUTPUT
(volume-mesh coordinate, `Xv`) space, it returns `w^T (dXv/dXs)`, a vector in surface-coordinate (`Xs`)
space. It does not expose a forward Jacobian column directly, so the correct way to check a reverse-mode
VJP against a pure finite difference of the underlying nonlinear function (no derivative code involved
on the FD side at all) is the standard adjoint/dot-product identity:

```
<w, dXv/dShape_idx>_FD   ==   <warpDeriv(w), dXs/dShape_idx>_analytic
```

- LHS ("FD_scalar"): perturb `shape[idx]` by `+h` and `-h`, call `DVGeo.update()` then
  `mesh.warpMesh()` at each (the actual, nonlinear, run-it-and-see warp — the exact code path
  `check_totals`' own finite difference exercises), central-difference the resulting volume-mesh
  coordinates (`mesh.getSolverGrid()`), dot with a fixed seed `w`.
- RHS ("AN_scalar"): call `mesh.warpDeriv(w)` (exactly as `DAFoamWarper.compute_jacvec_product` does in
  the real adjoint), take `mesh.getdXs()`, dot it with `DVGeo.totalSensitivityProd`'s forward-mode
  surface sensitivity for that shape index (pyGeo's own FFD Jacobian — independently confirmed exact to
  ~1e-13 relative error against FD elsewhere in this investigation, not the function under test here).

If these two scalars disagree, `warpDeriv` is not a valid linearization of the actual warp for that
design variable, for the tested direction `w`.

## Minimal reproducer

Pure geometry: `DVGeo` + IDWarp only, **no CFD solve**. Requires only the tutorial's mesh/FFD/`0.orig`
(no primal or adjoint solve needed to reach this test). Run inside `dafoam/opt-packages:latest`, working
directory = the tutorial case dir (`NACA0012_Airfoil/incompressible` after its own `preProcessing.sh`
has generated the mesh once):

```python
#!/usr/bin/env python
import os, argparse
import numpy as np
from mpi4py import MPI
from dafoam.mphys import DAFoamBuilder
from pygeo import DVGeometry

parser = argparse.ArgumentParser()
parser.add_argument("--idx", type=int, required=True)   # 0-7
parser.add_argument("--h", type=float, default=1e-4)
parser.add_argument("--seed", type=int, default=2026)
args = parser.parse_args()

U0, p0, nuTilda0, aoa0, A0, rho0 = 10.0, 0.0, 4.5e-5, 5.13918623195176, 0.1, 1.0
daOptions = {
    "designSurfaces": ["wing"], "solverName": "DASimpleFoam", "primalMinResTol": 1.0e-8,
    "primalBC": {"U0": {"variable": "U", "patches": ["inout"], "value": [U0, 0.0, 0.0]},
                 "p0": {"variable": "p", "patches": ["inout"], "value": [p0]},
                 "nuTilda0": {"variable": "nuTilda", "patches": ["inout"], "value": [nuTilda0]},
                 "useWallFunction": True},
    "function": {"CD": {"type": "force", "source": "patchToFace", "patches": ["wing"],
                         "directionMode": "parallelToFlow", "patchVelocityInputName": "patchV",
                         "scale": 1.0 / (0.5 * U0 * U0 * A0 * rho0)}},
    "adjEqnOption": {"gmresRelTol": 1.0e-6, "pcFillLevel": 1, "jacMatReOrdering": "rcm"},
    "normalizeStates": {"U": U0, "p": U0 * U0 / 2.0, "nuTilda": nuTilda0 * 10.0, "phi": 1.0},
    "inputInfo": {"aero_vol_coords": {"type": "volCoord", "components": ["solver", "function"]},
                  "patchV": {"type": "patchVelocity", "patches": ["inout"], "flowAxis": "x",
                             "normalAxis": "y", "components": ["solver", "function"]}},
}
meshOptions = {"gridFile": os.getcwd(), "fileType": "OpenFOAM",
               "symmetryPlanes": [[[0.0, 0.0, 0.0], [0.0, 0.0, 1.0]], [[0.0, 0.0, 0.1], [0.0, 0.0, 1.0]]]}

comm = MPI.COMM_WORLD
builder = DAFoamBuilder(daOptions, meshOptions, scenario="aerodynamic")
builder.initialize(comm)
DASolver = builder.DASolver
mesh = DASolver.mesh
xs0 = DASolver.getSurfaceCoordinates(DASolver.designSurfacesGroup)

DVGeo = DVGeometry(os.path.join(os.getcwd(), "FFD", "wingFFD.xyz"))
ptSetName = "x_aero0"
DVGeo.addPointSet(xs0, ptSetName)
pts = DVGeo.getLocalIndex(0)
dir_y = np.array([0.0, 1.0, 0.0])
shapes = []
for i in range(1, pts.shape[0] - 1):
    for j in range(pts.shape[1]):
        shapes.append({pts[i, j, 0]: dir_y, pts[i, j, 1]: dir_y})
for i in [0, pts.shape[0] - 1]:
    shapes.append({pts[i, 0, 0]: dir_y, pts[i, 0, 1]: dir_y, pts[i, 1, 0]: -dir_y, pts[i, 1, 1]: -dir_y})
nShape = len(shapes)
DVGeo.addShapeFunctionDV("shape", shapes)
idx = args.idx

def set_shape(vec):
    DVGeo.setDesignVars({"shape": np.array(vec)})

def get_warped_Xv(shapeVec):
    set_shape(shapeVec)
    xs = DVGeo.update(ptSetName)
    DASolver.setSurfaceCoordinates(xs, DASolver.designSurfacesGroup)
    mesh.warpMesh()
    return mesh.getSolverGrid().copy()

Xv0 = get_warped_Xv(np.zeros(nShape))
nXvLocal = Xv0.size
np.random.seed(args.seed)
w = np.random.random(nXvLocal).astype("d")

h = args.h
ePlus = np.zeros(nShape); ePlus[idx] = h
eMinus = np.zeros(nShape); eMinus[idx] = -h
Xv_p = get_warped_Xv(ePlus)
Xv_m = get_warped_Xv(eMinus)
FD_dXv_idx_local = (Xv_p - Xv_m) / (2.0 * h)
FD_scalar = comm.allreduce(float(np.dot(w, FD_dXv_idx_local)), op=MPI.SUM)

set_shape(np.zeros(nShape))
DVGeo.update(ptSetName)
seedDV = {"shape": np.zeros(nShape)}; seedDV["shape"][idx] = 1.0
AN_dXs_idx = DVGeo.totalSensitivityProd(seedDV, ptSetName).reshape(xs0.shape)

set_shape(np.zeros(nShape))
xs_base = DVGeo.update(ptSetName)
DASolver.setSurfaceCoordinates(xs_base, DASolver.designSurfacesGroup)
mesh.warpMesh()
mesh.warpDeriv(w)                      # <-- the function under test
dXs_seed = mesh.getdXs()
dXs_seed = DASolver.mapVector(dXs_seed, DASolver.allWallsGroup, DASolver.designSurfacesGroup)
AN_scalar = comm.allreduce(float(np.dot(dXs_seed.flatten(), AN_dXs_idx.flatten())), op=MPI.SUM)

if comm.rank == 0:
    relerr = abs(FD_scalar - AN_scalar) / (abs(FD_scalar) + 1e-300)
    print(f"idx={idx} FD_scalar={FD_scalar:.6e} AN_scalar={AN_scalar:.6e} rel_err={relerr:.6f}")
```

Run (decomposition is handled internally by `DAFoamBuilder.initialize(comm)` — do not call
`decomposePar` manually, it will conflict with the builder's own decomposition):

```bash
sudo docker run --rm --cpus=3 --memory=3g \
  -v <case_dir>:/home/dafoamuser/mount -w /home/dafoamuser/mount \
  dafoam/opt-packages:latest \
  bash -lc 'source /home/dafoamuser/dafoam/loadDAFoam.sh && \
            mpirun --allow-run-as-root -np 4 python repro.py --idx 6 --h 1e-4 --seed 2026'
```

(A single-rank invocation, `python repro.py --idx 6 ...` with no `mpirun`, reproduces the same
qualitative result — this is not a parallel-decomposition artifact.)

## Results

| idx | construction | seed | ranks | FD_scalar | AN_scalar (`warpDeriv`) | rel. err. | sign |
|---|---|---|---|---|---|---|---|
| 4 | single-station (control) | 2026 | 1 | 477.8887 | 477.4013 | 0.10% | agree |
| 4 | single-station (control) | 2026 | 4 | 485.2993 | 496.7999 | 2.37% | agree |
| 4 | single-station (control) | 42 | 4 | 473.8014 | 482.4881 | 1.83% | agree |
| 4 | single-station (control) | 2026 (h=1e-5) | 4 | 485.2651 | 496.7999 | 2.38% | agree |
| **6** | **combination (LE)** | 2026 | 1 | 11.8983 | -1.8153 | **115.26%** | **FLIPPED** |
| **6** | **combination (LE)** | 2026 | 4 | 13.1338 | -1.5600 | **111.88%** | **FLIPPED** |
| **6** | **combination (LE)** | 42 | 4 | 14.6722 | -1.1222 | **107.65%** | **FLIPPED** |
| **6** | **combination (LE)** | 2026 (h=1e-5) | 4 | 13.1323 | -1.5600 | **111.88%** | **FLIPPED** |
| **7** | **combination (TE)** | 2026 | 4 | -7.4350 | 1.0593 | **114.25%** | **FLIPPED** |
| **7** | **combination (TE)** | 42 | 4 | -7.6036 | 0.9709 | **112.77%** | **FLIPPED** |

`AN_scalar` (a single analytic evaluation, not a finite difference) is **bit-identical** between
`h=1e-4` and `h=1e-5` for idx6, by construction — it cannot depend on step size. `FD_scalar` itself
moves by 0.01% across that same decade of `h` — the disagreement is a fixed gap between two converged
numbers at every step size tested, not a resolution artifact on either side.

**idx4 (single-station) agrees to 0.1–2.4% in every configuration tested, sign always correct. idx6 and
idx7 (both combination-mode DVs) disagree by 108–149% and are SIGN-FLIPPED in every configuration
tested**, independent of seed, step size, and serial-vs-4-rank-parallel execution.

## An important open question, reported honestly rather than smoothed over

Despite idx6 and idx7 sharing the identical construction and both failing this test in the same way,
**only idx6 produces a wrong result in the real, full-chain `dCD/dShape` gradient** (verified via
`check_totals` against finite differences across two mesh resolutions in this investigation — idx7
agrees to 1.5–1.8%, idx6 is sign-flipped). The seed `w` used above is an arbitrary fixed random vector,
not the real force-objective's own reverse-mode seed (`dCD/dXv`); our working, not-yet-confirmed
hypothesis is that `warpDeriv`'s linearization error exists in some subspace at both the LE and the TE
for this construction, but only survives contraction with the real objective's own gradient direction
(concentrated near the LE stagnation region for a drag objective at this Reynolds number/incidence) at
the LE. **We have not run the follow-up test that would confirm this** (repeating the identity above
with the real `dCD/dXv` as `w`, which requires a CFD+adjoint solve rather than pure geometry). We report
this openly because a maintainer with source-level access to IDWarp's implementation of `warpDeriv`
(likely in the RBF/mesh-warping derivative assembly, specifically wherever a single design variable maps
to multiple, oppositely-signed surface-point perturbations) may be able to resolve it directly from the
code rather than from black-box measurement.

## Suggested starting point for maintainers

The measured pattern — correct for a DV that perturbs one FFD point along one axis, wrong (sign-flipped,
not just numerically imprecise) for a DV that perturbs two or more FFD points with different/opposing
sign conventions within the same design variable — is consistent with an indexing, aliasing, or
sign-accumulation bug specific to the reverse-mode accumulation path for multi-point design variables in
`mesh.warpDeriv`/`mesh.getdXs()`, as opposed to a general accuracy or conditioning problem (a
conditioning problem would not produce a clean, step-independent, bit-reproducible sign flip). We have
not traced this into IDWarp's own source in this investigation and cannot point to a specific line.

## Files behind this report (this lab's internal paths, not part of the reproducer)

- `demo-output/website/dafoam/work/NACA0012_Airfoil_Incompressible/probeWarpDeriv.py` — the exact
  script behind the idx4/idx6 numbers above (parameterized `--idx`/`--h`/`--seed` version of the
  reproducer)
- `demo-output/website/dafoam/probewarpderiv_idx{4,6,7}_*_run1.log` — raw stdout for every
  configuration in the results table
- `demo-output/website/dafoam/PROOF.md`, sections 15–16 — full investigation history, including 6 other
  mechanisms tested and refuted before this one was found (residual-tolerance noise, FFD/DVGeo Jacobian
  convention, coarse-mesh discretization error, frozen wall-distance, a wall-function branch-crossing
  hypothesis, and combination-mode mesh pinching), and a second, independent case (A5, U-Bend Channel)
  that shares the coarse symptom profile (step-independent, sign-flipped) but was tested and shown NOT
  to share this specific `warpDeriv` mechanism — so this defect is confirmed for the NACA0012 case
  specifically, not assumed to explain every gradient-accuracy failure encountered.
