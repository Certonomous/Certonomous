"""M6C2 L1 hyperbolic extrusion, surface handed to pyHyp IN MEMORY via `patches`.

WHY `patches` AND NOT A FILE: two tools in this image are broken for this path and
a planted control proved each rather than a guess.
  * `cgns_utils plot3d2cgns` cannot read the output of its OWN SIBLING
    `cgns2plot3d` -- identical "Fortran runtime error: End of file" at
    cgns_utilities.F90:2616 on a file the toolchain itself wrote from a known-good
    CGNS. My PLOT3D was never the problem.
  * the cgnsutilities CGNS WRITER rejects a 2-D zone whose dims and coords match
    the reference file's exactly: "Invalid input: VertexSize[0]=201 and
    CellSize[0]=64" -- it pairs the vertex count of one axis with the cell count of
    another.
pyHyp's own option `patches` takes the surface as numpy arrays, so neither is
needed.

A3's options verbatim except N (ours: 33 nodes = 32 march cells; A3's 8/15/28/52/65
has steps 1.875/1.867/1.857/1.25 and is not a family) and s0 held FIXED in physical
units across levels so the triple measures one thing.
"""
import numpy as np
from pyhyp import pyHyp

t = open("/work/m6_wing_uncapped_L1.xyz").read().split()
nb = int(t[0]); p = 1; dims = []
for _ in range(nb):
    dims.append((int(t[p]), int(t[p+1]), int(t[p+2]))); p += 3
patches = []
for (a, b, c) in dims:
    n = a*b*c
    arr = np.array(t[p:p+3*n], dtype=float); p += 3*n
    X = np.zeros((a, b, 3))
    for k in range(3):
        X[:, :, k] = arr[k*n:(k+1)*n].reshape(a, b, order="F")
    patches.append(X)
print(f"  patches: {len(patches)}  shape {patches[0].shape}", flush=True)

opts = {
    "inputFile": "", "fileType": "PLOT3D", "patches": patches,
    "unattachedEdgesAreSymmetry": True, "outerFaceBC": "farfield",
    "autoConnect": True, "BC": {}, "families": "wall",
    "N": 33, "s0": 1.0e-4, "marchDist": 12.0,
    "ps0": -1.0, "pGridRatio": -1.0, "cMax": 0.1,
    "epsE": 1.0, "epsI": 2.0, "theta": 3.0,
    "volCoef": 0.25, "volBlend": 0.0005, "volSmoothIter": 100,
    "kspRelTol": 1e-4,
}
h = pyHyp(options=opts)
h.run()
h.writeCGNS("/work/m6c2_L1_UNCAPPED.cgns")
print("  DONE", flush=True)
