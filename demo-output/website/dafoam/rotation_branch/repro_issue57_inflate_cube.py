#!/usr/bin/env python
"""
Reproduce mdolab/idwarp OPEN issue #57 ("`inflate_cube` test appears to fail",
opened 2021-07-14, label `bug`, zero comments) and test our mechanism against it.

Issue #57 reports IDWarp's OWN `verifyWarpDeriv` printing 216-218% errors with
sign flips on DOFs 0 and 3 of the `inflate_cube` test, while DOFs 1,2,4,5 read
~3e-5. Nobody ever replied. This script runs that exact test -- same mesh
(`input_files/symm_block.cgns`), same options, same displacement, same
`verifyWarpDeriv(dXv_warp, solverVec=False, dofStart=0, dofEnd=5)` call, all
copied from `tests/test_USMesh.py::test_inflate_cube` -- and then reruns it with
`useRotations=False`.

There is NO DAFoam, NO OpenFOAM, NO pyGeo/FFD, and NO CFD anywhere in this file.
It is IDWarp alone, checked by IDWarp's own instrument, on IDWarp's own test mesh.

Our claim: the 216% is `getRotationMatrix3d`'s `axisMag < tol` branch
(src/utils/vectorUtils.f90:58) whose Tapenade reverse
(src/adjoint/outputReverse/vectorUtils_b.f90:124-128) discards ALL rotation
sensitivity. If so, `useRotations=False` must drive the errors to ~0.

Usage:  python repro_issue57_inflate_cube.py <on|off>
"""
import sys
import numpy
from mpi4py import MPI
from idwarp import USMesh

useRot = (sys.argv[1] if len(sys.argv) > 1 else "on") == "on"
HFD = float(sys.argv[2]) if len(sys.argv) > 2 else 1e-6

# --- verbatim from tests/test_USMesh.py setUp() defOpts + test_inflate_cube ---
meshOptions = {
    "gridFile": "input_files/symm_block.cgns",
    "fileType": "CGNS",
    "aExp": 3.0,
    "bExp": 5.0,
    "LdefFact": 1.0,
    "alpha": 0.25,
    "errTol": 0.0005,
    "evalMode": "fast",
    "symmTol": 1e-6,
    "useRotations": useRot,   # <-- THE ONLY THING THIS SCRIPT VARIES
    "bucketSize": 8,
}

if MPI.COMM_WORLD.rank == 0:
    print("=" * 78, flush=True)
    print("ISSUE57 inflate_cube  useRotations=%s" % useRot, flush=True)
    print("=" * 78, flush=True)

mesh = USMesh(options=meshOptions)

# --- verbatim from eval_warp() ---
coords0 = mesh.getSurfaceCoordinates()
new_coords = coords0.copy()
for i in range(len(coords0)):
    new_coords[i, 0] *= 1.1
    new_coords[i, 1] *= 1.2
    new_coords[i, 2] *= 1.3

mesh.setSurfaceCoordinates(new_coords)
mesh.warpMesh()

vCoords = mesh.getWarpGrid()
val = MPI.COMM_WORLD.reduce(numpy.sum(vCoords.flatten()), op=MPI.SUM)
if MPI.COMM_WORLD.rank == 0:
    print("ISSUE57 Sum of vCoords Warped: %.15e" % val, flush=True)

dXv_warp = numpy.linspace(0, 1.0, mesh.warp.griddata.warpmeshdof)

mesh.warpDeriv(dXv_warp, solverVec=False)
dXs = mesh.getdXs()
val = MPI.COMM_WORLD.reduce(numpy.sum(dXs.flatten()), op=MPI.SUM)
n2 = MPI.COMM_WORLD.reduce(float(numpy.dot(dXs.flatten(), dXs.flatten())), op=MPI.SUM)
if MPI.COMM_WORLD.rank == 0:
    # The mechanism predicts this fingerprint is IDENTICAL for useRotations on/off,
    # because the rotation branch contributes exactly zero to the analytic derivative.
    print("ISSUE57_ANFINGERPRINT useRotations=%s sum(dXs)=%.15e ||dXs||=%.15e"
          % (useRot, val, n2 ** 0.5), flush=True)

# --- IDWarp's own instrument, exactly as test_USMesh.py invokes it ---
if MPI.COMM_WORLD.rank == 0:
    print("ISSUE57_VERIFY === verifyWarpDeriv(dofStart=0, dofEnd=5) h=%g ===" % HFD, flush=True)
mesh.verifyWarpDeriv(dXv_warp, solverVec=False, dofStart=0, dofEnd=5, h=HFD)
if MPI.COMM_WORLD.rank == 0:
    print("ISSUE57_VERIFY === done useRotations=%s ===" % useRot, flush=True)
