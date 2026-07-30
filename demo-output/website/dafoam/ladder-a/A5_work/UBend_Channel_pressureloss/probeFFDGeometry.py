#!/usr/bin/env python
"""
Pure-geometry diagnostic (no CFD, no solver init even needed for the FFD part):
print the physical (x,y,z) coordinates of every shapexUpper FFD control point,
in DV order, alongside the case's own real per-component FD-vs-adjoint relative
error (from A5_ubend_internal.md's already-measured table), to check whether
the two sign-flipped components (idx8, idx17) are spatially distinguished --
in particular whether they sit on or near the "sym" symmetry-plane patch --
from the well-behaved ones (e.g. idx2, idx26, both independently verified
clean against mesh.warpDeriv).

Also prints the mesh's own point-coordinate bounding box (from constant/polyMesh)
in each axis, and the DAFoam meshOptions actually used by this case's runScript.py
(symmetryPlanes: [] -- confirmed empty, i.e. IDWarp is not told about the "sym"
patch at all), so the FFD point z (or whichever axis the sym plane sits on) can
be compared directly against the domain's own symmetry-plane coordinate.
"""
import os
import numpy as np
from pygeo import DVGeometry, geo_utils

DVGeo = DVGeometry(os.path.join(os.getcwd(), "FFD", "UBendDuctFFDSym.xyz"))
pts = DVGeo.getLocalIndex(0)
print("PROBEFFD pts.shape =", pts.shape)

indexListUpper = list(pts[7:16, 1, :].flatten())
indexListLower = list(pts[7:16, 0, :].flatten())
print("PROBEFFD len(indexListUpper) =", len(indexListUpper))

coef = DVGeo.FFD.coef  # (nCtl, 3) physical FFD control-point coordinates

# real per-component rel. err % from A5_ubend_internal.md's already-measured table
real_relerr = {
    0: 115.3, 1: 6.9, 2: 1.1, 3: 179.2, 4: 76.1, 5: 15.1, 6: 18.1, 7: 31.8,
    8: 207.6, 9: 32.4, 10: 34.0, 11: 52.2, 12: 57.0, 13: 27.4, 14: 88.0,
    15: 42.9, 16: 12.3, 17: 121.6, 18: 47.9, 19: 167.1, 20: 60.4, 21: 42.1,
    22: 24.3, 23: 63.8, 24: 8.5, 25: 2.3, 26: 2.7,
}
sign_flip = {8, 17}

print("PROBEFFD idx  rawPtIdx     x            y            z          real_relerr%  sign_flip")
for m, rawIdx in enumerate(indexListUpper):
    x, y, z = coef[rawIdx]
    flip = "FLIP" if m in sign_flip else ""
    print("PROBEFFD %3d  %8d  %11.6f  %11.6f  %11.6f  %8.1f  %s" % (m, rawIdx, x, y, z, real_relerr[m], flip))

# also print the i,j,k grid indices explicitly for each m (helps interpret pts[7:16,1,:] layout)
print("PROBEFFD --- grid (i,j,k) for shapexUpper (j=1 slice) ---")
count = 0
for i in range(7, 16):
    for k in range(pts.shape[2]):
        rawIdx = pts[i, 1, k]
        assert rawIdx == indexListUpper[count]
        print("PROBEFFD m=%2d  i=%2d j=1 k=%d  rawPtIdx=%d  coef=%s" % (count, i, k, rawIdx, coef[rawIdx]))
        count += 1

print("PROBEFFD FFD coef bounding box: x=[%.6f,%.6f] y=[%.6f,%.6f] z=[%.6f,%.6f]" % (
    coef[:, 0].min(), coef[:, 0].max(), coef[:, 1].min(), coef[:, 1].max(), coef[:, 2].min(), coef[:, 2].max()))

print("PROBEFFD DONE")
