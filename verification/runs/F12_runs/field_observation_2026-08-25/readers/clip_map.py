#!/usr/bin/env python3
"""WHERE is the pressure field being clipped by pressureControl, and how many
cells?  A handful of cells in one place = LOCALISED.  Thousands spread over the
domain = GLOBAL.  Uses the same planted-control-validated reader."""
import json, math, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from field_probe import read_field, patch_owner_cells

CASE = pathlib.Path(sys.argv[1])
C = read_field(CASE / "0" / "C")["internal"]
PATCH = patch_owner_cells(CASE / "constant" / "polyMesh")
WALL = set(PATCH["aerofoil"]["owner_cells"])
INF  = set(PATCH["inflow"]["owner_cells"])
OUTF = set(PATCH["outflow"]["owner_cells"])
FLOOR, CEIL = 10132.5, 202650.0
TOL = 1e-6

def band(i):
    x, y, _ = C[i]
    r = math.hypot(x - 0.5, y)
    if i in WALL: return "ON THE AEROFOIL WALL"
    if i in INF:  return "on the inflow patch"
    if i in OUTF: return "on the outflow patch"
    if r < 1.5:   return "near field  r<1.5c"
    if r < 6:     return "mid field   1.5-6c"
    if r < 20:    return "outer       6-20c"
    return "FAR FIELD   >20c"

print(f"{'it':>3} {'nFLOOR':>7} {'nCEIL':>7} {'ntot':>7} {'%dom':>6}   breakdown of clipped cells by region")
for t in range(1, 16):
    f = CASE / str(t) / "p"
    if not f.exists(): continue
    v = read_field(f)["internal"]
    lo = [i for i, x in enumerate(v) if abs(x - FLOOR) < TOL]
    hi = [i for i, x in enumerate(v) if abs(x - CEIL) < TOL]
    tot = lo + hi
    from collections import Counter
    c = Counter(band(i) for i in tot)
    br = "  ".join(f"{k}:{n}" for k, n in sorted(c.items(), key=lambda kv: -kv[1]))
    print(f"{t:>3} {len(lo):>7} {len(hi):>7} {len(tot):>7} {100*len(tot)/len(v):>5.1f}%   {br}")
    if t <= 3 and tot:
        xs = [C[i][0] for i in tot]; ys = [C[i][1] for i in tot]
        print(f"       bbox of clipped cells: x [{min(xs):.3f}, {max(xs):.3f}]  "
              f"y [{min(ys):.3f}, {max(ys):.3f}]   (chord is x in [0,1])")
