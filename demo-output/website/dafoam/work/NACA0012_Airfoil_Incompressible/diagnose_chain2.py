#!/usr/bin/env python
"""
Isolate the FFD (pyGeo/DVGeo) + mesh-warping (IDWarp) chain from the CFD
adjoint, using the EXACT reverse-mode routine the real adjoint uses
(mesh.warpDeriv, called from DAFoamWarper.compute_jacvec_product in
dafoam/mphys/mphys_dafoam.py), not warpDerivFwd (which DAFoam only uses in
the separate, rarely-used useAD.mode=="forward" path, not this tutorial's
useAD.mode=="reverse" setup). No CFD solve, no flow adjoint anywhere here.

Method: for a fixed seed vector w on the volume-mesh output (Xv), define the
scalar g_idx(shape) = dot(w, Xv(shape)) as a function of shape DV idx only
(others held at 0). Then:
  FD_scalar  = dot(w, (Xv(+h*e_idx) - Xv(-h*e_idx)) / (2h))   [true nonlinear warp,
               central difference -- no analytic derivative code involved at all]
  AN_scalar  = dot(mesh.warpDeriv(w) -> dXs_seed,  AN_dXs_idx)  [the exact reverse
               chain: IDWarp warpDeriv (as used by DAFoamWarper) contracted with
               the analytic DVGeo surface-sensitivity for shape idx, which was
               already confirmed exact to 1e-13 in diagnose_chain.py]
These two scalars must agree if IDWarp's warpDeriv (dXv/dXs)^T is a correct
linearization of the actual nonlinear warp used by FD_scalar. This is valid for
an arbitrary w since dot products with an arbitrary FIXED w are just linear
functionals of Xv(shape); no assumption about w being a "smooth" deformation
direction is needed (unlike perturbing the mesh directly by w, which was the
flawed test in diagnose_warp.py).
"""
import os
import numpy as np
from mpi4py import MPI
from dafoam.mphys import DAFoamBuilder
from pygeo import DVGeometry

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

if rank == 0:
    print("DIAGCHAIN2 nShape =", nShape)


def set_shape(vec):
    DVGeo.setDesignVars({"shape": np.array(vec)})


def get_warped_Xv(shapeVec):
    set_shape(shapeVec)
    xs = DVGeo.update(ptSetName)
    DASolver.setSurfaceCoordinates(xs, DASolver.designSurfacesGroup)
    mesh.warpMesh()
    return mesh.getSolverGrid().copy()


Xv0 = get_warped_Xv(np.zeros(nShape))
nXv = Xv0.size

# fixed seed on the volume-mesh output space (solver ordering), same seed reused
# for every idx so results are directly comparable
np.random.seed(2026)
w = np.random.random(nXv).astype("d")

h = 1e-4
for idx in range(nShape):
    ePlus = np.zeros(nShape)
    ePlus[idx] = h
    eMinus = np.zeros(nShape)
    eMinus[idx] = -h

    Xv_p = get_warped_Xv(ePlus)
    Xv_m = get_warped_Xv(eMinus)
    FD_dXv_idx = (Xv_p - Xv_m) / (2.0 * h)
    FD_scalar = float(np.dot(w, FD_dXv_idx))

    # analytic surface sensitivity for this shape idx (already confirmed exact
    # in diagnose_chain.py, re-derived here for a self-contained script)
    set_shape(np.zeros(nShape))
    DVGeo.update(ptSetName)
    seedDV = {"shape": np.zeros(nShape)}
    seedDV["shape"][idx] = 1.0
    AN_dXs_idx = DVGeo.totalSensitivityProd(seedDV, ptSetName).reshape(xs0.shape)

    # reverse-mode mesh-warping derivative, exactly as DAFoamWarper.compute_jacvec_product
    # calls it: mesh.warpDeriv(dxV) then mesh.getdXs()
    set_shape(np.zeros(nShape))
    xs_base = DVGeo.update(ptSetName)
    DASolver.setSurfaceCoordinates(xs_base, DASolver.designSurfacesGroup)
    mesh.warpMesh()
    mesh.warpDeriv(w)
    dXs_seed = mesh.getdXs()
    dXs_seed = DASolver.mapVector(dXs_seed, DASolver.allWallsGroup, DASolver.designSurfacesGroup)

    AN_scalar = float(np.dot(dXs_seed.flatten(), AN_dXs_idx.flatten()))

    relerr = abs(FD_scalar - AN_scalar) / (abs(FD_scalar) + 1e-300)
    if rank == 0:
        print(
            f"DIAGCHAIN2 idx={idx} FD_scalar={FD_scalar:.10e} AN_scalar={AN_scalar:.10e} "
            f"abs_diff={FD_scalar - AN_scalar:.6e} rel_err={relerr:.6e}"
        )

if rank == 0:
    print("DIAGCHAIN2 DONE")
