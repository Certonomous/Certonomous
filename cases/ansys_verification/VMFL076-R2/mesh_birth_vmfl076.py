#!/usr/bin/env python3
"""VMFL076 mesh birth certificate. Every number below is READ BACK from
OpenFOAM's own C field; nothing is constructed from nx, ny or (j+1/2)."""
import re
import sys

d = sys.argv[1]
txt = open(d + "/0/C").read()
txt = re.sub(r"/\*.*?\*/", " ", txt, flags=re.S)
start = txt.index("(", txt.index("List<vector>")) + 1
dep, i = 1, start
while i < len(txt) and dep:
    if txt[i] == "(":
        dep += 1
    elif txt[i] == ")":
        dep -= 1
    i += 1
N = r"[-+0-9.eE]+"
tri = re.findall(r"\(\s*(%s)\s+(%s)\s+(%s)\s*\)" % (N, N, N), txt[start:i - 1])
if not tri:
    sys.stderr.write("no cell centres read from 0/C\n")
    sys.exit(2)
xs = [float(a) for a, b, c in tri]
ys = [float(b) for a, b, c in tri]
uy = sorted(set(round(y, 12) for y in ys))
ux = sorted(set(round(x, 12) for x in xs))
print("cells_read_from_C = %d" % len(tri))
print("distinct_x        = %d" % len(ux))
print("distinct_y        = %d" % len(uy))
print("x_min             = %.12g" % min(xs))
print("x_max             = %.12g" % max(xs))
print("y_first_centre    = %.12g" % uy[0])
print("y_last_centre     = %.12g" % uy[-1])
print("first_cell_height = %.12g" % (2.0 * uy[0]))
print("y_expansion_ratio = %.12g" % ((0.5 - uy[-1]) / uy[0]))
print("gate_station_x_is_a_face = %s" % ("yes" if min(abs(x - 0.75) for x in ux) > 1e-12 else "NO"))
print("NOTE: read back from OpenFOAM's own C field; nothing constructed.")
