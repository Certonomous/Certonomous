#!/usr/bin/env python
"""
A5 (U-Bend Channel) variant of probeWarpDeriv.py. Same method, same identity,
same fix (explicit MPI allreduce; tests mesh.warpDeriv, the reverse-mode
function this case's real adjoint calls -- confirmed daOptionsAero["useAD"] =
{"mode": "reverse"} in this case's own runScript.py, byte-identical setup).

Tests components of the "shapexUpper" DV group (the one FD-checked in A5's
own check_totals, 27 components, idx8/idx17 sign-flipped per
A5_ubend_internal.md's per-component table). Unlike A1's shape functions
(nom_addShapeFunctionDV, which can define a DV as an arbitrary combination of
several FFD points moving in different/opposing directions -- idx6's LE combo
mode), A5 uses nom_addLocalDV, which pyGeo implements as ONE FFD point moving
along ONE axis per DV, unconditionally -- there is no "combination mode"
construction available in this DV family at all. Every one of A5's 27
shapexUpper components, including idx8 and idx17, is structurally a
single-station mode in A1's terms. This script tests whether warpDeriv is
wrong for idx8/idx17 despite that.

No CFD solve anywhere in this script. Pure geometry: DVGeo + IDWarp only.
"""
import os
import argparse
import numpy as np
from mpi4py import MPI
from dafoam.mphys import DAFoamBuilder
from pygeo import DVGeometry, geo_utils

parser = argparse.ArgumentParser()
parser.add_argument("--idx", type=int, required=True, help="shapexUpper index to test (0-26)")
parser.add_argument("--h", type=float, default=1e-4)
parser.add_argument("--seed", type=int, default=2026)
args = parser.parse_args()

U0 = 8.4

daOptionsAero = {
    "solverName": "DASimpleFoam",
    "designSurfaces": ["ubend"],
    "useAD": {"mode": "reverse"},
    "primalMinResTol": 1e-8,
    "primalMinResTolDiff": 1e7,
    "writeMinorIterations": True,
    "wallDistanceMethod": "daCustom",
    "primalBC": {"useWallFunction": True},
    "function": {
        "TP1": {"type": "totalPressure", "source": "patchToFace", "patches": ["inlet"], "scale": 1.0, "addToAdjoint": True},
        "TP2": {"type": "totalPressure", "source": "patchToFace", "patches": ["outlet"], "scale": 1.0, "addToAdjoint": True},
        "HFX": {"type": "wallHeatFlux", "source": "patchToFace", "patches": ["ubend"], "scale": 1.0, "addToAdjoint": False},
    },
    "adjStateOrdering": "cell",
    "adjEqnOption": {"gmresRelTol": 1e-5, "gmresTolDiff": 1e4, "pcFillLevel": 2,
                      "jacMatReOrdering": "natural", "gmresMaxIters": 3000, "gmresRestart": 3000},
    "normalizeStates": {"U": U0, "p": (U0 * U0) / 2.0, "nuTilda": 1e-3, "phi": 1.0, "T": 300},
    "inputInfo": {"aero_vol_coords": {"type": "volCoord", "components": ["solver", "function"]}},
    "outputInfo": {"q_convect": {"type": "thermalCouplingOutput", "patches": ["ubend"], "components": ["thermalCoupling"]}},
}

meshOptions = {
    "gridFile": os.getcwd(),
    "fileType": "OpenFOAM",
    "symmetryPlanes": [],
}

comm = MPI.COMM_WORLD
rank = comm.rank
nRanks = comm.size

builder = DAFoamBuilder(daOptionsAero, meshOptions, scenario="aerodynamic")
builder.initialize(comm)
DASolver = builder.DASolver
mesh = DASolver.mesh

xs0 = DASolver.getSurfaceCoordinates(DASolver.designSurfacesGroup)

DVGeo = DVGeometry(os.path.join(os.getcwd(), "FFD", "UBendDuctFFDSym.xyz"))
ptSetName = "x_aero0"
DVGeo.addPointSet(xs0, ptSetName)

pts = DVGeo.getLocalIndex(0)
if rank == 0:
    print("A5WARPDERIV pts.shape =", pts.shape, flush=True)

# EXACT same selection as runScript.py's shapexUpper DV group
indexList = []
indexList.extend(pts[7:16, 1, :].flatten())
PS = geo_utils.PointSelect("list", indexList)
nShape = DVGeo.addLocalDV("shapexUpper", axis="x", pointSelect=PS)
if rank == 0:
    print("A5WARPDERIV nShape (shapexUpper) =", nShape, flush=True)
assert nShape == 27, "expected 27 shapexUpper DVs, got %d" % nShape

idx = args.idx
assert 0 <= idx < nShape


def set_shape(vec):
    DVGeo.setDesignVars({"shapexUpper": np.array(vec)})


def get_warped_Xv(shapeVec):
    set_shape(shapeVec)
    xs = DVGeo.update(ptSetName)
    DASolver.setSurfaceCoordinates(xs, DASolver.designSurfacesGroup)
    mesh.warpMesh()
    return mesh.getSolverGrid().copy()


Xv0 = get_warped_Xv(np.zeros(nShape))
nXvLocal = Xv0.size
nXvGlobal = comm.allreduce(nXvLocal, op=MPI.SUM)

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

set_shape(np.zeros(nShape))
DVGeo.update(ptSetName)
seedDV = {"shapexUpper": np.zeros(nShape)}
seedDV["shapexUpper"][idx] = 1.0
AN_dXs_idx = DVGeo.totalSensitivityProd(seedDV, ptSetName).reshape(xs0.shape)

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
        "A5WARPDERIV_RESULT idx=%d h=%.3e seed=%d nRanks=%d nXvGlobal=%d "
        "FD_scalar=%.12e AN_scalar=%.12e abs_diff=%.6e rel_err=%.6e"
        % (idx, h, args.seed, nRanks, nXvGlobal, FD_scalar_global, AN_scalar_global, absdiff, relerr),
        flush=True,
    )
    print("A5WARPDERIV_DONE idx=%d nRanks=%d" % (idx, nRanks), flush=True)
