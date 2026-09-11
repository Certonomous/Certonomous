"""Volume CGNS -> formatted multiblock PLOT3D, for `plot3dToFoam`.

NOT via `cgns_utils cgns2plot3d`: M6C1 Addendum 1 A1.4 established with a planted
control that this toolchain cannot read back its own sibling's PLOT3D output
(`Fortran runtime error: End of file` at cgns_utilities.F90:2616 on a file the
toolchain itself wrote from a known-good CGNS). The arrays are read with
cgnsutilities and written here, one value per line, by code whose format is known.
"""
import sys, numpy as np
from cgnsutilities.cgnsutilities import readGrid

src, out = sys.argv[1], sys.argv[2]
g = readGrid(src)
blocks = [b.coords.copy() for b in g.blocks]           # each (ni, nj, nk, 3)
print(f"  volume blocks: {len(blocks)}  shapes {[b.shape[:3] for b in blocks]}", flush=True)
npts = sum(int(np.prod(b.shape[:3])) for b in blocks)
ncell = sum(int(np.prod([d - 1 for d in b.shape[:3]])) for b in blocks)
print(f"  points {npts}   cells (before interface merge) {ncell}", flush=True)
mn = min(float(np.abs(np.diff(b, axis=0)).min()) for b in blocks)
print(f"  smallest |dx| along i over all blocks: {mn:.6e}", flush=True)
with open(out, "w") as f:
    f.write(f"{len(blocks)}\n")
    for b in blocks:
        f.write("%d %d %d\n" % b.shape[:3])
    for b in blocks:
        for c in range(3):
            v = b[:, :, :, c].ravel(order="F")
            f.write("".join(f" {x:.15g}\n" for x in v))
print(f"  WROTE {out}", flush=True)
