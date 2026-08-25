#!/usr/bin/env python3
"""p is CENSORED in the written field (pressureControl clips it to
[10132.5, 202650]), so amplitude must be read from the UNCENSORED fields:
T, rho and |U|.  Per iteration, per region, relative departure from freestream."""
import json, math, pathlib, sys
from collections import defaultdict
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from field_probe import read_field, patch_owner_cells, mag

CASE = pathlib.Path(sys.argv[1])
C = read_field(CASE / "0" / "C")["internal"]
PATCH = patch_owner_cells(CASE / "constant" / "polyMesh")
WALL = set(PATCH["aerofoil"]["owner_cells"]); INF = set(PATCH["inflow"]["owner_cells"])
OUTF = set(PATCH["outflow"]["owner_cells"])
UINF = math.hypot(254.55661283, 12.40536100); TINF = 300.0

def band(i):
    x, y, _ = C[i]; r = math.hypot(x - 0.5, y)
    if i in WALL: return "1 WALL"
    if i in INF:  return "6 INFLOW-PATCH"
    if i in OUTF: return "7 OUTFLOW-PATCH"
    if r < 1.5: return "2 near <1.5c"
    if r < 6:   return "3 mid 1.5-6c"
    if r < 20:  return "4 outer 6-20c"
    return "5 far >20c"

BANDS = sorted({band(i) for i in range(len(C))})
IDX = defaultdict(list)
for i in range(len(C)): IDX[band(i)].append(i)

def loc(i):
    x, y, _ = C[i]; return f"({x:.4g},{y:.4g})"

print("T minimum (K) by region -- freestream T = 300 K.  Energy eqn is what kills the run at it 148.")
print(f"{'it':>3} " + " ".join(f"{b:>15}" for b in BANDS) + "   global T min  at")
Tglob = []
for t in range(1, 16):
    f = CASE / str(t) / "T"
    if not f.exists(): continue
    v = read_field(f)["internal"]
    mins = {b: min(v[i] for i in IDX[b]) for b in BANDS}
    gi = min(range(len(v)), key=lambda i: v[i])
    Tglob.append((t, v[gi], gi))
    print(f"{t:>3} " + " ".join(f"{mins[b]:>15.6g}" for b in BANDS) + f"   {v[gi]:>10.5g}  {loc(gi)}")

print("\n|U| maximum (m/s) by region -- freestream |U| = %.2f m/s" % UINF)
print(f"{'it':>3} " + " ".join(f"{b:>15}" for b in BANDS) + "   global |U|max  at")
for t in range(1, 16):
    f = CASE / str(t) / "U"
    if not f.exists(): continue
    v = [mag(x) for x in read_field(f)["internal"]]
    mx = {b: max(v[i] for i in IDX[b]) for b in BANDS}
    gi = max(range(len(v)), key=lambda i: v[i])
    print(f"{t:>3} " + " ".join(f"{mx[b]:>15.6g}" for b in BANDS) + f"   {v[gi]:>11.6g}  {loc(gi)}")

print("\nrho minimum (kg/m3) by region -- freestream rho = 1.1766")
print(f"{'it':>3} " + " ".join(f"{b:>15}" for b in BANDS))
for t in range(1, 16):
    f = CASE / str(t) / "rho"
    if not f.exists(): continue
    v = read_field(f)["internal"]
    mn = {b: min(v[i] for i in IDX[b]) for b in BANDS}
    print(f"{t:>3} " + " ".join(f"{mn[b]:>15.6g}" for b in BANDS))
