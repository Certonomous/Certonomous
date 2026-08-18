#!/usr/bin/env python
"""
IDWarp-only mechanism test across IDWarp's OWN regression meshes.

No DAFoam, no OpenFOAM, no pyGeo/FFD, no CFD. Every case, option value, and
surface displacement below is copied verbatim from `tests/test_USMesh.py`
(IDWarp v2.6.2). The ONLY thing varied is `useRotations`.

The check is IDWarp's own `verifyWarpDeriv`, which central-differences
`warpMesh()` per surface DOF and compares against `warpDeriv`'s `dXs` entry.

Prediction under our mechanism (getRotationMatrix3d's `axisMag < tol` branch,
src/utils/vectorUtils.f90:58, whose Tapenade reverse discards all rotation
sensitivity at src/adjoint/outputReverse/vectorUtils_b.f90:124-128):

  * the AD column must be BIT-IDENTICAL for useRotations on vs off
  * the FD column must change
  * with useRotations=off the two must agree to FD truncation (~1e-5 %)

Falsified if the AD column moves, or if the errors survive useRotations=off.

Usage: python repro_geometries.py <case> <on|off>
"""
import sys
import numpy
from mpi4py import MPI
from idwarp import USMesh

CASES = {
    # name:            (gridFile,                             extra options,               displacement)
    "inflate_cube": ("input_files/symm_block.cgns", {}, "inflate"),
    "o_mesh": ("input_files/o_mesh.cgns", {}, "shear"),
    "co_mesh": ("input_files/co_mesh.cgns", {}, "shear"),
    "sym_mesh": ("input_files/mdo_tutorial_face_bcs.cgns",
                 {"symmetryPlanes": [[[0, 0, 0], [0, 0, 1]]]}, "shear"),
    "onera_m6": ("input_files/onera_m6.cgns", {}, "shear"),
}

case = sys.argv[1]
useRot = (sys.argv[2] if len(sys.argv) > 2 else "on") == "on"
gridFile, extra, disp = CASES[case]

# verbatim tests/test_USMesh.py setUp() defOpts
meshOptions = {
    "gridFile": gridFile,
    "fileType": "CGNS",
    "aExp": 3.0,
    "bExp": 5.0,
    "LdefFact": 1.0,
    "alpha": 0.25,
    "errTol": 0.0005,
    "evalMode": "fast",
    "symmTol": 1e-6,
    "useRotations": useRot,   # <-- the only thing varied
    "bucketSize": 8,
}
meshOptions.update(extra)

rank = MPI.COMM_WORLD.rank
if rank == 0:
    print("GEOM === case=%s useRotations=%s grid=%s disp=%s ===" % (case, useRot, gridFile, disp), flush=True)

mesh = USMesh(options=meshOptions)
coords0 = mesh.getSurfaceCoordinates()
new_coords = coords0.copy()

if disp == "inflate":          # verbatim test_inflate_cube
    for i in range(len(coords0)):
        new_coords[i, 0] *= 1.1
        new_coords[i, 1] *= 1.2
        new_coords[i, 2] *= 1.3
else:                           # verbatim eval_warp() "shearing sweep deflection"
    for i in range(len(coords0)):
        span = coords0[i, 2]
        new_coords[i, 0] += 0.05 * span

mesh.setSurfaceCoordinates(new_coords)
mesh.warpMesh()

dXv_warp = numpy.linspace(0, 1.0, mesh.warp.griddata.warpmeshdof)
mesh.warpDeriv(dXv_warp, solverVec=False)
dXs = mesh.getdXs()
s = MPI.COMM_WORLD.reduce(float(numpy.sum(dXs.flatten())), op=MPI.SUM)
n2 = MPI.COMM_WORLD.reduce(float(numpy.dot(dXs.flatten(), dXs.flatten())), op=MPI.SUM)
if rank == 0:
    print("GEOM_ANFINGERPRINT case=%s useRotations=%s sum(dXs)=%.15e ||dXs||=%.15e"
          % (case, useRot, s, n2 ** 0.5), flush=True)

if rank == 0:
    print("GEOM_VERIFY case=%s useRotations=%s ===" % (case, useRot), flush=True)
mesh.verifyWarpDeriv(dXv_warp, solverVec=False, dofStart=0, dofEnd=11)
if rank == 0:
    print("GEOM_DONE case=%s useRotations=%s" % (case, useRot), flush=True)
