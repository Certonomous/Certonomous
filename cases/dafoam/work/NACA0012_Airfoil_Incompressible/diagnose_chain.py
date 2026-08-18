#!/usr/bin/env python
"""
Isolate the FFD (pyGeo/DVGeo) + mesh-warping (IDWarp) chain from the CFD
adjoint entirely. No CFD solve, no flow adjoint anywhere in this script.

For each of the 8 real "shape" design variables (exact same shape-function
definitions as runScript.py), compute:
  - FD_dXs  : finite difference of DVGeo.update() surface points wrt the DV
  - AN_dXs  : analytic DVGeo.totalSensitivityProd() surface sensitivity wrt the DV
  - FD_dXv  : finite difference of the ACTUAL warped volume mesh (setSurfaceCoordinates
              + warpMesh + getSolverGrid, i.e. the true nonlinear warp) wrt the DV
  - AN_dXv  : analytic chain: mesh.warpDerivFwd(AN_dXs), i.e. the same forward-mode
              AD path DAFoam uses internally (calcFFD2XvSeeds) to seed volume coords
              from a shape DV, with NO flow solve involved

This directly tests whether the FFD Jacobian and the mesh-warping derivative
(the two candidates named in the task: "FFD/design-variable point ordering or
sign convention mismatch" and "surface-mesh warping/dvGeo Jacobian not matching")
reproduce the ACTUAL mesh deformation to first order, for all 8 shape indices,
completely independent of the CFD solver and its adjoint.
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

# get baseline design-surface coordinates exactly the way runScript.py does
# (mesh.mphys_get_surface_mesh() pulls from DASolver via getSurfaceCoordinates)
xs0 = DASolver.getSurfaceCoordinates(DASolver.designSurfacesGroup)

DVGeo = DVGeometry(os.path.join(os.getcwd(), "FFD", "wingFFD.xyz"))
ptSetName = "x_aero0"
DVGeo.addPointSet(xs0, ptSetName)

pts = DVGeo.getLocalIndex(0)
if rank == 0:
    print("DIAGCHAIN pts.shape =", pts.shape)
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
    print("DIAGCHAIN nShape =", nShape)


def set_shape(vec):
    DVGeo.setDesignVars({"shape": np.array(vec)})


def get_warped_Xv(shapeVec):
    """True nonlinear chain: DVGeo.update -> setSurfaceCoordinates -> warpMesh -> getSolverGrid"""
    set_shape(shapeVec)
    xs = DVGeo.update(ptSetName)
    DASolver.setSurfaceCoordinates(xs, DASolver.designSurfacesGroup)
    mesh.warpMesh()
    return mesh.getSolverGrid().copy(), xs.copy()


# baseline
Xv0, Xs0check = get_warped_Xv(np.zeros(nShape))

h = 1e-4
results = []
for idx in range(nShape):
    ePlus = np.zeros(nShape)
    ePlus[idx] = h
    eMinus = np.zeros(nShape)
    eMinus[idx] = -h

    Xv_p, Xs_p = get_warped_Xv(ePlus)
    Xv_m, Xs_m = get_warped_Xv(eMinus)

    FD_dXv = (Xv_p - Xv_m) / (2.0 * h)
    FD_dXs = (Xs_p - Xs_m) / (2.0 * h)

    # analytic surface sensitivity (pyGeo forward-mode seed)
    set_shape(np.zeros(nShape))
    DVGeo.update(ptSetName)  # reset baseline state for a clean analytic eval
    seed = {"shape": np.zeros(nShape)}
    seed["shape"][idx] = 1.0
    AN_dXs = DVGeo.totalSensitivityProd(seed, ptSetName).reshape(Xs0check.shape)

    # propagate analytic surface sensitivity through the REAL (nonlinear-at-baseline)
    # forward mesh-warp derivative, exactly like DAFoam's calcFFD2XvSeeds does
    set_shape(np.zeros(nShape))
    xs_base = DVGeo.update(ptSetName)
    DASolver.setSurfaceCoordinates(xs_base, DASolver.designSurfacesGroup)
    mesh.warpMesh()
    AN_dXv = mesh.warpDerivFwd(AN_dXs)

    dXs_err = np.linalg.norm(FD_dXs.flatten() - AN_dXs.flatten()) / (np.linalg.norm(AN_dXs.flatten()) + 1e-300)
    dXv_err = np.linalg.norm(FD_dXv.flatten() - AN_dXv.flatten()) / (np.linalg.norm(AN_dXv.flatten()) + 1e-300)
    dXv_max_abs_diff = np.max(np.abs(FD_dXv.flatten() - AN_dXv.flatten()))
    dXv_norm_FD = np.linalg.norm(FD_dXv.flatten())
    dXv_norm_AN = np.linalg.norm(AN_dXv.flatten())

    if rank == 0:
        print(
            f"DIAGCHAIN idx={idx} "
            f"dXs_relerr={dXs_err:.6e} "
            f"dXv_relerr={dXv_err:.6e} "
            f"|FD_dXv|={dXv_norm_FD:.6e} |AN_dXv|={dXv_norm_AN:.6e} "
            f"maxabsdiff={dXv_max_abs_diff:.6e}"
        )
    results.append((idx, dXs_err, dXv_err))

if rank == 0:
    print("DIAGCHAIN DONE")
