#!/usr/bin/env python
"""
Isolate the mesh-warping (IDWarp) derivative from the CFD adjoint entirely.
Builds the same DAFoam/IDWarp setup as runScript.py (same daOptions/meshOptions),
but stops after DASolver.setMesh() -- no CFD solve, no adjoint. Then calls
IDWarp's own built-in self-verification (verifyWarpDeriv), which FD-checks
warpDeriv/warpDerivFwd against the mesh-warping formula itself, independent of
DAFoam's flow solver and independent of pyGeo/DVGeo.
"""
import os
import numpy as np
from mpi4py import MPI
from dafoam.mphys import DAFoamBuilder

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
    "evalMode": "exact",
}

comm = MPI.COMM_WORLD
rank = comm.rank

builder = DAFoamBuilder(daOptions, meshOptions, scenario="aerodynamic")
builder.initialize(comm)
DASolver = builder.DASolver
mesh = DASolver.mesh

if rank == 0:
    print("DIAGWARP evalMode =", mesh.getOption("evalMode"))
    print("DIAGWARP warpmeshdof =", mesh.warp.griddata.warpmeshdof)
    print("DIAGWARP solvermeshdof =", mesh.warp.griddata.solvermeshdof)

# initialize internal surface / baseline warp state
mesh.warpMesh()

np.random.seed(314)
ndof = mesh.warp.griddata.warpmeshdof
dXvWarp = np.random.random(ndof).astype("d")

if rank == 0:
    print("DIAGWARP === verifyWarpDeriv over first 60 dof, h=1e-6 ===")
mesh.verifyWarpDeriv(dXv=dXvWarp, solverVec=False, dofStart=0, dofEnd=60, h=1e-6)

if rank == 0:
    print("DIAGWARP === verifyWarpDeriv over first 60 dof, h=1e-4 ===")
mesh.verifyWarpDeriv(dXv=dXvWarp, solverVec=False, dofStart=0, dofEnd=60, h=1e-4)

if rank == 0:
    print("DIAGWARP DONE")
