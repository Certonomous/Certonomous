#!/usr/bin/env python3
"""DIAGNOSTIC ONLY — not the graded instrument. Why did 832 faces miss the symmetry test?"""
import sys, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from split_patches import body, classify, Y_SYMM_TOL
pm = sys.argv[1]
btxt = open(os.path.join(pm, "boundary")).read()
m = re.search(r"defaultFaces\s*\{[^}]*?nFaces\s+(\d+);[^}]*?startFace\s+(\d+);", btxt, re.S)
nb, start = int(m.group(1)), int(m.group(2))
fl, fs = body(os.path.join(pm, "faces")); pl_, ps = body(os.path.join(pm, "points"))
faces, need = [], set()
for k in range(nb):
    t = [int(x) for x in re.findall(r"\d+", fl[fs + 1 + start + k])][1:]
    faces.append(t); need.update(t)
co = {}
for i in need:
    v = re.findall(r"[-+0-9.eE]+", pl_[ps + 1 + i]); co[i] = (float(v[0]), float(v[1]), float(v[2]))
import collections
h = collections.Counter(); radii = []
for q in faces:
    maxy = max(abs(co[i][1]) for i in q)
    if maxy < Y_SYMM_TOL: h["symmetry (maxy<1e-9)"] += 1; continue
    c = [sum(co[i][j] for i in q)/len(q) for j in (0,1,2)]
    r = (c[0]**2+c[1]**2+c[2]**2)**0.5
    if   maxy < 1e-6: b="1e-9..1e-6"
    elif maxy < 1e-3: b="1e-6..1e-3"
    elif maxy < 1e-1: b="1e-3..1e-1"
    else:             b=">1e-1 (genuinely off-plane)"
    h[b]+=1; radii.append((b,r,maxy))
print("max|y| over each boundary face's vertices:")
for k,v in sorted(h.items()): print("  %-28s %6d" % (k,v))
near = [x for x in radii if x[0] != ">1e-1 (genuinely off-plane)"]
print("\nfaces with 1e-9 <= max|y| < 1e-1  (candidates for a too-tight tolerance): %d" % len(near))
if near:
    print("  their |r| range: %.3f .. %.3f" % (min(x[1] for x in near), max(x[1] for x in near)))
    print("  their max|y| range: %.3e .. %.3e" % (min(x[2] for x in near), max(x[2] for x in near)))
off = [x for x in radii if x[0] == ">1e-1 (genuinely off-plane)"]
print("\ngenuinely off-plane faces: %d, |r| range %.3f .. %.3f" % (len(off), min(x[1] for x in off), max(x[1] for x in off)))
print("\n*** DOES THE SYMMETRY PLANE SPAN THE RADIUS RANGE THE r>40 BAND ASSUMES IS EMPTY? ***")
sym_r = []
for q in faces:
    if max(abs(co[i][1]) for i in q) < Y_SYMM_TOL:
        c = [sum(co[i][j] for i in q)/len(q) for j in (0,1,2)]
        sym_r.append((c[0]**2+c[1]**2+c[2]**2)**0.5)
print("  symmetry-plane face |r|: min %.3f  max %.3f  -- spans the 4.3..80 'dead zone': %s"
      % (min(sym_r), max(sym_r), "YES" if (min(sym_r) < 40 < max(sym_r)) else "no"))
