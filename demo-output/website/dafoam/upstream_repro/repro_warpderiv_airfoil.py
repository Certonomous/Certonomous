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
