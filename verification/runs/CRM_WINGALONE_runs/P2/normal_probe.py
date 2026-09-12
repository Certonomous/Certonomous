#!/usr/bin/env python3
"""DECISIVE PLANARITY PROBE — independent of P1 (y-coordinate) and P2 (block index).
A face lying in the root plane has unit normal along y. Classify by NORMAL, then
measure max|y| over those faces. Answers 'is pyHyp's symmetry plane planar?' without
building P2.  PLANT: tilt one face's normal and require the classifier to drop it."""
import sys, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../P1")
from split_patches import body

def normal(q, co):
    p = [co[i] for i in q]
    ux, uy, uz = (p[1][j] - p[0][j] for j in range(3))
    vx, vy, vz = (p[2][j] - p[0][j] for j in range(3))
    nx, ny, nz = uy*vz - uz*vy, uz*vx - ux*vz, ux*vy - uy*vx
    m = (nx*nx + ny*ny + nz*nz) ** 0.5
    return (0.0, 0.0, 0.0) if m == 0 else (nx/m, ny/m, nz/m)

pm = sys.argv[1]
b = open(os.path.join(pm, "boundary")).read()
m = re.search(r"defaultFaces\s*\{[^}]*?nFaces\s+(\d+);[^}]*?startFace\s+(\d+);", b, re.S)
nb, start = int(m.group(1)), int(m.group(2))
fl, fs = body(os.path.join(pm, "faces")); pl_, ps = body(os.path.join(pm, "points"))
faces, need = [], set()
for k in range(nb):
    t = [int(x) for x in re.findall(r"\d+", fl[fs+1+start+k])][1:]
    faces.append(t); need.update(t)
co = {}
for i in need:
    v = re.findall(r"[-+0-9.eE]+", pl_[ps+1+i]); co[i] = (float(v[0]), float(v[1]), float(v[2]))

THRESH = 0.99
ny_aligned, maxy_over_them, ymax_face = 0, 0.0, None
for q in faces:
    if abs(normal(q, co)[1]) > THRESH:
        ny_aligned += 1
        my = max(abs(co[i][1]) for i in q)
        if my > maxy_over_them: maxy_over_them, ymax_face = my, q
print("PLANARITY PROBE — classify by FACE NORMAL, not by coordinate or index")
print("  faces with |n_y| > %.2f (root-plane candidates) : %d" % (THRESH, ny_aligned))
print("  block-topology PREDICTED symmetry faces          : 14144")
print("  agreement: %s" % ("YES — a THIRD independent route gives the same count"
                           if ny_aligned == 14144 else "NO — %+d" % (ny_aligned - 14144)))
print("  MAX |y| over those faces                         : %.6e mesh-units" % maxy_over_them)
print("  = %.6f m physical (1 mesh-unit = 6.976368 m)" % (maxy_over_them * 6.976368))
print("  VERDICT: symmetry plane is %s"
      % ("PLANAR to ~1e-6 — a symmetryPlane BC is well posed"
         if maxy_over_them < 1e-6 else
         "*** NOT PLANAR *** — OpenFOAM symmetryPlane requires a uniform patch normal"))
# --- PLANT: tilt one aligned face and require the classifier to DROP it
print("\nPLANT — tilt one root-plane face's normal and require it to be dropped")
victim = next(q for q in faces if abs(normal(q, co)[1]) > THRESH)
saved = {i: co[i] for i in victim}
before = abs(normal(victim, co)[1])
co[victim[0]] = (co[victim[0]][0], co[victim[0]][1] + 5.0, co[victim[0]][2])
after = abs(normal(victim, co)[1])
for i, c in saved.items(): co[i] = c
restored = abs(normal(victim, co)[1])
seen = before > THRESH >= after
print("  |n_y| before %.6f -> after tilt %.6f -> restored %.6f" % (before, after, restored))
print("  classifier dropped the tilted face: %s" % seen)
print("  residue after restore: %s" % ("NONE" if abs(restored-before) < 1e-12 else "*** RESIDUE ***"))
if not seen:
    print("  REFUSE: the normal test cannot see a tilted face; its count is NOT evidence.")
    sys.exit(2)
print("  CONTROL PASSED -> the count and max|y| above are evidence.")
