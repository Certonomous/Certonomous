"""PLOT3D (ASCII) -> CGNS via the cgnsutilities PYTHON API.

WHY NOT `cgns_utils plot3d2cgns`: it is broken in this image, and a planted control
proved it rather than a guess. Fed the output of its OWN SIBLING `cgns2plot3d`
-- produced from a known-good CGNS -- it fails identically:
    At line 2616 of file cgns_utilities.F90 ... Fortran runtime error: End of file
So the reader cannot read what the writer writes, and my file was never the
problem. Two reformattings of my own file were spent before the control was run.
"""
import sys, numpy as np
from cgnsutilities.cgnsutilities import Block, Grid

t = open(sys.argv[1]).read().split()
nb = int(t[0]); p = 1; dims = []
for _ in range(nb):
    dims.append((int(t[p]), int(t[p+1]), int(t[p+2]))); p += 3
g = Grid()
for bi, (a, b, c) in enumerate(dims):
    n = a*b*c
    arr = np.array(t[p:p+3*n], dtype=float); p += 3*n
    coords = np.zeros((a, b, c, 3))
    for k in range(3):
        coords[:, :, :, k] = arr[k*n:(k+1)*n].reshape(a, b, c, order="F")
    g.addBlock(Block(f"surf_{bi}", [a, b, c], coords))
g.writeToCGNS(sys.argv[2])
print(f"  wrote {sys.argv[2]}: {nb} block(s), dims {dims}")
