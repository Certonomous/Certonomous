#!/usr/bin/env python3
"""P1B DIAGNOSTIC — WHERE are the wing faces that exceed the frozen |r| <= 4.3 gate?

THIS CHANGES NO GATE. WING_R_MAX stays 4.3. This asks only WHAT the exceedance is,
so that "a finding about the radius band" is substantiated rather than asserted.

Imports the P1B instrument so the classifier under test is the SAME OBJECT that
produced the graded number -- not a re-implementation that could differ silently.
"""
import sys, os, re, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import split_patches_p1b as M

pm = sys.argv[1]
nb, start = None, None
txt = open(os.path.join(pm, "boundary")).read()
m = re.search(r"defaultFaces\s*\{[^}]*?nFaces\s+(\d+);[^}]*?startFace\s+(\d+);", txt, re.S)
nb, start = int(m.group(1)), int(m.group(2))

flines, fs = M.body(os.path.join(pm, "faces"))
plines, ps = M.body(os.path.join(pm, "points"))
faces, need = [], set()
for k in range(nb):
    pl = [int(x) for x in re.findall(r"\d+", flines[fs + 1 + start + k])][1:]
    faces.append(pl); need.update(pl)
coords = {}
for idx in need:
    v = re.findall(r"[-+0-9.eE]+", plines[ps + 1 + idx])
    coords[idx] = (float(v[0]), float(v[1]), float(v[2]))

over = []
wing = []
for pl in faces:
    name, r = M.classify(pl, coords)
    if name != "wing":
        continue
    pts = [coords[i] for i in pl]; n = len(pts)
    c = (sum(p[0] for p in pts)/n, sum(p[1] for p in pts)/n, sum(p[2] for p in pts)/n)
    wing.append((r, c))
    if r > M.WING_R_MAX:
        over.append((r, c))

wing.sort(key=lambda t: -t[0])
print("WING faces: %d   |r| gate (FROZEN, not moved): %.1f" % (len(wing), M.WING_R_MAX))
print("faces exceeding the gate: %d  (%.3f %% of the wing patch)" % (len(over), 100.0*len(over)/len(wing)))
print("max |r| = %.4f   min |r| = %.4f" % (wing[0][0], wing[-1][0]))
xs=[c[0] for r,c in over]; ys=[c[1] for r,c in over]; zs=[c[2] for r,c in over]
if over:
    print("\nEXCEEDING faces, centre extents:")
    print("  x %.4f .. %.4f" % (min(xs), max(xs)))
    print("  y %.4f .. %.4f   (wing tip y is 3.7666681523 per section 2)" % (min(ys), max(ys)))
    print("  z %.4f .. %.4f" % (min(zs), max(zs)))
    print("\ntop 8 by |r|:   (x, y, z)  ->  |r|,  and sqrt(x^2+z^2) = distance from the SPAN axis")
    for r, c in wing[:8]:
        print("  (%8.4f %8.4f %8.4f) -> |r| %7.4f   r_axis %7.4f" % (c[0], c[1], c[2], r, math.hypot(c[0], c[2])))
    print("\nALL exceeding faces have y >= %.4f : %s" % (min(ys), min(ys) > 3.0))
    print("max distance from the SPAN AXIS among exceeding faces: %.4f" % max(math.hypot(c[0],c[2]) for r,c in over))
