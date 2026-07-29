#!/usr/bin/env python
"""
Verify IDWarp's mesh.warpDeriv() -- the ACTUAL, REVERSE-mode mesh-warping
derivative DAFoam's real adjoint calls (DAFoamWarper.compute_jacvec_product
in dafoam/mphys/mphys_dafoam.py: "self.DASolver.mesh.warpDeriv(dxV)"; this
case's daOptions never overrides useAD.mode, whose DAFoam default is
"reverse" -- confirmed directly from pyDAFoam.py:426 in the container this
session, and DAFoamWarper.compute_jacvec_product itself refuses mode="fwd").
warpDerivFwd is a SEPARATE, forward-mode function this case's adjoint never
calls; testing it (as the retracted diagnose_chain.py did, and it showed
100-200% relative error on EVERY one of the 8 components including the
well-verified idx2-5 -- impossible if that were the code path real dCD/dShape
depends on, since idx2-5 independently check out to 1.5-6.4% there) tests the
wrong function. This script tests only warpDeriv, the one that matters.

warpDeriv is a REVERSE-mode Jacobian-transpose-vector product: given a seed
w in the OUTPUT (volume mesh coordinate, Xv) space, it returns w^T (dXv/dXs),
a vector in the surface-coordinate (Xs) space -- it does not expose a full
forward Jacobian or a single column directly. The only rigorous way to check
a reverse-mode VJP against a pure finite difference of the underlying
nonlinear function is the standard adjoint/dot-product identity:

    <w, dXv/dShape_idx>_FD  ==  <warpDeriv(w), dXs/dShape_idx>_analytic

LHS: re-warp the mesh at shape+h*e_idx and shape-h*e_idx (the TRUE nonlinear
     warp, no derivative code involved at all -- exactly what check_totals'
     own finite difference does), central-difference the volume coordinates,
     dot with the fixed seed w.
RHS: call the REAL mesh.warpDeriv(w) (exactly as DAFoamWarper does) to get
     the reverse-mode surface-space vector, dot it with DVGeo's own
     forward-mode surface-sensitivity for shape idx (DVGeo.totalSensitivityProd,
     independently validated elsewhere in this investigation to 1e-13 relative
     error against FD and against the geometric constraint Jacobians -- NOT
     the thing under test here).

If these two scalars disagree, warpDeriv is not a valid linearization of the
real warp for that design variable -- and since the check_totals finite
difference perturbs+re-warps (uses the warp, never touches warpDeriv) while
the real adjoint chain calls warpDeriv directly, THAT would mean the ADJOINT
is wrong and the FD CHECK is right, the reverse of every hypothesis tested so
far in this investigation.

Fix vs. the retracted diagnose_chain2.py: this version (a) restricts to idx4
(control) and idx6 (suspect) only, (b) explicitly MPI-allreduces both the FD
and analytic scalars (diagnose_chain2.py computed a per-rank LOCAL dot
product and printed only rank 0's partition -- silently wrong under >1 rank,
which independently explains why it could not be trusted in parallel), and
(c) is run at BOTH np=1 and np=3 explicitly, to empirically settle (not
assume) whether this specific function's correctness depends on rank count.

No CFD solve anywhere in this script. Pure geometry: DVGeo + IDWarp only.
"""
import os
import sys
import argparse
import numpy as np
from mpi4py import MPI
from dafoam.mphys import DAFoamBuilder
from pygeo import DVGeometry

parser = argparse.ArgumentParser()
parser.add_argument("--idx", type=int, required=True, help="shape DV index to test (0-7)")
parser.add_argument("--h", type=float, default=1e-4)
parser.add_argument("--seed", type=int, default=2026)
args = parser.parse_args()

U0 = 10.0
p0 = 0.0
nuTilda0 = 4.5e-5
aoa0 = 5.13918623195176
A0 = 0.1
rho0 = 1.0

daOptions = {
    "designSurfaces": ["wing"],
    "solverName": "DASimpleFoam",
    "primalMinResTol": 1.0e-8,
    "primalBC": {
        "U0": {"variable": "U", "patches": ["inout"], "value": [U0, 0.0, 0.0]},
        "p0": {"variable": "p", "patches": ["inout"], "value": [p0]},
        "nuTilda0": {"variable": "nuTilda", "patches": ["inout"], "value": [nuTilda0]},
        "useWallFunction": True,
    },
    "function": {
        "CD": {"type": "force", "source": "patchToFace", "patches": ["wing"],
               "directionMode": "parallelToFlow", "patchVelocityInputName": "patchV",
               "scale": 1.0 / (0.5 * U0 * U0 * A0 * rho0)},
        "CL": {"type": "force", "source": "patchToFace", "patches": ["wing"],
               "directionMode": "normalToFlow", "patchVelocityInputName": "patchV",
               "scale": 1.0 / (0.5 * U0 * U0 * A0 * rho0)},
    },
    "adjEqnOption": {"gmresRelTol": 1.0e-6, "pcFillLevel": 1, "jacMatReOrdering": "rcm"},
    "normalizeStates": {"U": U0, "p": U0 * U0 / 2.0, "nuTilda": nuTilda0 * 10.0, "phi": 1.0},
    "inputInfo": {
        "aero_vol_coords": {"type": "volCoord", "components": ["solver", "function"]},
        "patchV": {"type": "patchVelocity", "patches": ["inout"], "flowAxis": "x",
                   "normalAxis": "y", "components": ["solver", "function"]},
    },
}

meshOptions = {
    "gridFile": os.getcwd(),
    "fileType": "OpenFOAM",
    "symmetryPlanes": [[[0.0, 0.0, 0.0], [0.0, 0.0, 1.0]], [[0.0, 0.0, 0.1], [0.0, 0.0, 1.0]]],
}

comm = MPI.COMM_WORLD
rank = comm.rank
nRanks = comm.size

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
assert nShape == 8, "expected 8 shape DVs, got %d" % nShape
idx = args.idx
assert 0 <= idx < nShape


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
nXvGlobal = comm.allreduce(nXvLocal, op=MPI.SUM)

# fixed seed on the LOCAL volume-mesh output partition -- same construction
# used consistently for FD and AN on THIS rank, so the identity holds
# regardless of what any other rank does; no cross-rank uniqueness required.
np.random.seed(args.seed)
w = np.random.random(nXvLocal).astype("d")

h = args.h
ePlus = np.zeros(nShape)
ePlus[idx] = h
eMinus = np.zeros(nShape)
eMinus[idx] = -h

Xv_p = get_warped_Xv(ePlus)
Xv_m = get_warped_Xv(eMinus)
FD_dXv_idx_local = (Xv_p - Xv_m) / (2.0 * h)
FD_scalar_local = float(np.dot(w, FD_dXv_idx_local))
FD_scalar_global = comm.allreduce(FD_scalar_local, op=MPI.SUM)

# analytic surface sensitivity for this shape idx (DVGeo forward-mode Jacobian,
# independently validated elsewhere to ~1e-13 -- NOT under test here)
set_shape(np.zeros(nShape))
DVGeo.update(ptSetName)
seedDV = {"shape": np.zeros(nShape)}
seedDV["shape"][idx] = 1.0
AN_dXs_idx = DVGeo.totalSensitivityProd(seedDV, ptSetName).reshape(xs0.shape)

# THE function under test: mesh.warpDeriv, reverse-mode, exactly as
# DAFoamWarper.compute_jacvec_product calls it in the real adjoint chain
set_shape(np.zeros(nShape))
xs_base = DVGeo.update(ptSetName)
DASolver.setSurfaceCoordinates(xs_base, DASolver.designSurfacesGroup)
mesh.warpMesh()
mesh.warpDeriv(w)
dXs_seed = mesh.getdXs()
dXs_seed = DASolver.mapVector(dXs_seed, DASolver.allWallsGroup, DASolver.designSurfacesGroup)

AN_scalar_local = float(np.dot(dXs_seed.flatten(), AN_dXs_idx.flatten()))
AN_scalar_global = comm.allreduce(AN_scalar_local, op=MPI.SUM)

absdiff = FD_scalar_global - AN_scalar_global
relerr = abs(absdiff) / (abs(FD_scalar_global) + 1e-300)

if rank == 0:
    print(
        "WARPDERIV_RESULT idx=%d h=%.3e seed=%d nRanks=%d nXvGlobal=%d "
        "FD_scalar=%.12e AN_scalar=%.12e abs_diff=%.6e rel_err=%.6e"
        % (idx, h, args.seed, nRanks, nXvGlobal, FD_scalar_global, AN_scalar_global, absdiff, relerr),
        flush=True,
    )
    print("WARPDERIV_DONE idx=%d nRanks=%d" % (idx, nRanks), flush=True)
