#!/usr/bin/env python3
"""F12 field-localisation probe -- the REGISTERED departure criteria D1/D2/D3.

Criteria are those frozen in
verification/campaign/F12_FIELD_LOCALISATION_PREREGISTRATION.md sec 3
(blob sha256 bca4074a7de26f478115a1efc1706c9cba6daedab8174cf72c202566d534b667).
This file holds NO threshold of its own -- every constant below is quoted from
that freeze.  It reads through field_probe, which is under planted control.
"""
import json, math, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from field_probe import read_field, patch_owner_cells

CASE = pathlib.Path(sys.argv[1]); LOG = pathlib.Path(sys.argv[2]); OUT = pathlib.Path(sys.argv[3])

# ---- REGISTERED CONSTANTS (sec 2 and sec 3 of the freeze) -------------------
P_REF, PMINF, PMAXF = 101325.0, 0.1, 2.0     # 0/p uniform; fvSolution SIMPLE
FLOOR, CEIL = P_REF*PMINF, P_REF*PMAXF       # = 10132.5 , 202650  Pa   (D1)
T_REF = 300.0                                # 0/T uniform
T_FLOOR, T_CEIL = 0.0, 2.0*T_REF             # thermoI.H check ; factor-2 (D2)
D3_TOL = 0.5                                 # K, onset threshold        (D3)
CHORD, QC = 1.0, (0.25, 0.0)                 # r measured from quarter chord
NMAX = 15

C = read_field(CASE/"0"/"C")["internal"]
PATCH = patch_owner_cells(CASE/"constant"/"polyMesh")
def r(i):
    x, y, _ = C[i]; return math.hypot(x-QC[0], y-QC[1])/CHORD
def loc(i):
    x, y, _ = C[i]
    return {"cell": i, "x": round(x,6), "y": round(y,6), "r_qc": round(r(i),4)}

wall = set(PATCH["aerofoil"]["owner_cells"])
infl = set(PATCH["inflow"]["owner_cells"])
outf = set(PATCH["outflow"]["owner_cells"])
REGIONS = {
 "aerofoil_wall": lambda i: i in wall,
 "near_r_lt_1.5c": lambda i: r(i) < 1.5,
 "mid_1.5_to_6c": lambda i: 1.5 <= r(i) < 6.0,
 "outer_6_to_20c": lambda i: 6.0 <= r(i) < 20.0,
 "far_ge_20c":    lambda i: r(i) >= 20.0,
 "inflow_patch":  lambda i: i in infl,
 "outflow_patch": lambda i: i in outf,
}
MEMB = {k: [i for i in range(len(C)) if f(i)] for k, f in REGIONS.items()}

# ---- D1: pre-clip p, from the solver's OWN pressureControl print ------------
preclip, t = {}, None
for line in LOG.read_text(errors="replace").splitlines():
    m = re.match(r"^Time = (\d+)", line)
    if m: t = int(m.group(1)); continue
    m = re.match(r"^pressureControl: p (max|min) ([-+0-9.eE]+)", line)
    if m and t is not None and t <= NMAX:
        preclip.setdefault(t, {})[m.group(1)] = float(m.group(2))

d1 = []
for n in range(1, NMAX+1):
    e = preclip.get(n, {})
    lo, hi = e.get("min"), e.get("max")
    dep = (lo is not None and lo < FLOOR) or (hi is not None and hi > CEIL)
    d1.append({"iteration": n, "preclip_p_min": lo, "preclip_p_max": hi,
               "outside_registered_bounds": bool(dep)})
N_p = next((row["iteration"] for row in d1 if row["outside_registered_bounds"]), None)

# ---- per-iteration field reads ---------------------------------------------
d2, d3rows, clip = [], [], []
for n in range(0, NMAX+1):
    d = CASE/str(n)
    if not d.is_dir(): continue
    def _internal(fp):
        f = read_field(fp)
        v = f["internal"]
        if not v:                      # a `uniform` field: expand to n_cells
            u = f.get("uniform_internal")
            u = u[0] if isinstance(u, (list, tuple)) else u
            v = [float(u)]*len(C)
        return v
    T = _internal(d/"T")
    P = _internal(d/"p")
    # D2 -- admissibility of T
    bad_lo = [i for i, v in enumerate(T) if v <= T_FLOOR]
    bad_hi = [i for i, v in enumerate(T) if v > T_CEIL]
    d2.append({"iteration": n, "T_min": min(T), "T_min_at": loc(T.index(min(T))),
               "n_T_le_0K": len(bad_lo), "n_T_gt_600K": len(bad_hi),
               "departed": bool(bad_lo or bad_hi)})
    # D3 -- onset by region, on |T - 300| > 0.5 K
    row = {"iteration": n, "regions": {}}
    for k, idx in MEMB.items():
        dev = max(abs(T[i]-T_REF) for i in idx)
        am = max(idx, key=lambda i: abs(T[i]-T_REF))
        row["regions"][k] = {"max_abs_dev_K": round(dev, 6),
                             "departed": bool(dev > D3_TOL),
                             "at": loc(am), "T": round(T[am], 4)}
    d3rows.append(row)
    # spatial locator: cells pinned AT the censored bounds on disk
    at_lo = [i for i, v in enumerate(P) if v <= FLOOR*(1+1e-12)]
    at_hi = [i for i, v in enumerate(P) if v >= CEIL*(1-1e-12)]
    byreg = {k: sum(1 for i in at_lo+at_hi if i in set(idx)) for k, idx in MEMB.items()}
    clip.append({"iteration": n, "n_at_floor": len(at_lo), "n_at_ceiling": len(at_hi),
                 "n_total": len(at_lo)+len(at_hi),
                 "pct_of_domain": round(100.0*(len(at_lo)+len(at_hi))/len(C), 2),
                 "by_region": byreg,
                 "sample": [loc(i) for i in (at_lo+at_hi)[:6]]})

first = {}
for k in MEMB:
    first[k] = next((row["iteration"] for row in d3rows
                     if row["iteration"] >= 1 and row["regions"][k]["departed"]), None)
order = sorted(first, key=lambda k: (999 if first[k] is None else first[k], k))
N_T = next((row["iteration"] for row in d2 if row["iteration"] >= 1 and row["departed"]), None)

OUT.write_text(json.dumps({
  "registered_constants": {"p_floor": FLOOR, "p_ceiling": CEIL, "T_floor": T_FLOOR,
                           "T_ceiling": T_CEIL, "D3_tol_K": D3_TOL, "T_ref": T_REF,
                           "n_cells": len(C)},
  "region_sizes": {k: len(v) for k, v in MEMB.items()},
  "D1_preclip_p": d1, "D1_first_departure_iteration": N_p,
  "D2_T_admissibility": d2, "D2_first_departure_iteration": N_T,
  "D3_onset_by_region": d3rows, "D3_first_departure_by_region": first,
  "D3_departure_order": order,
  "clipped_cell_census_on_disk": clip}, indent=1))

print(f"cells {len(C)}   regions " + ", ".join(f"{k}={len(v)}" for k, v in MEMB.items()))
print(f"\nD1  p outside [{FLOOR}, {CEIL}] Pa (pre-clip, solver print): FIRST DEPARTURE N_p = {N_p}")
for row in d1[:3]:
    print(f"    it {row['iteration']:>2}  pre-clip p min {row['preclip_p_min']}  max {row['preclip_p_max']}  departed={row['outside_registered_bounds']}")
print(f"\nD2  T <= 0 K or T > 600 K: FIRST DEPARTURE = {N_T}  (None = not reached in window)")
for row in d2:
    if row["iteration"] in (1, 5, 10, 15):
        print(f"    it {row['iteration']:>2}  T_min {row['T_min']:.4f} K at cell {row['T_min_at']['cell']} "
              f"(x={row['T_min_at']['x']}, y={row['T_min_at']['y']}, r={row['T_min_at']['r_qc']}c)")
print(f"\nD3  region departs when max|T-300| > {D3_TOL} K.  DEPARTURE ORDER:")
for k in order:
    print(f"    {first[k] if first[k] is not None else 'never':>5}   {k}")
print("\nClipped-cell census on disk (spatial locator; p is censored):")
for row in clip:
    if row["iteration"] in (1, 2, 5, 10, 13, 15):
        nz = {k: v for k, v in row["by_region"].items() if v}
        print(f"    it {row['iteration']:>2}  floor {row['n_at_floor']:>6}  ceil {row['n_at_ceiling']:>6}  "
              f"total {row['n_total']:>6} ({row['pct_of_domain']:>5.2f}%)  {nz}")
print(f"\nwrote {OUT}")
