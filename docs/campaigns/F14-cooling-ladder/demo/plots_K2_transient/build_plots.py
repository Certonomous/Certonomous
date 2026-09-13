#!/usr/bin/env python3
"""Build the K2 TRANSIENT demo plot folder from REAL series on disk.

Zero solver compute.  Sources, each named in SIDECAR.md:
  * K2h_runs/K2h_L3  -- the graded transient fine level (PASS), dp_tile/dp_return
    per time step and the time-averaged fields TMean/UMean/p_rghMean at t = 110.
  * K2b_runs/K2bU3R3_D59 -- the 3-D four-rack room (GATE REACHED), the ONLY run in
    this territory that emits PER-RACK INLET TEMPERATURE against time.
  * K2b_runs/K2bU3_L025 -- the finest 2-D slice of the same module, for 2-D vs 3-D.

Figure names are the plot orders' names (docs/plot_orders/README_PLOT_ORDERS.md C).
No verdict stamp and no band annotation is drawn on any image: both live in
SIDECAR.md and README.md (owner correction, 2026-09-13).
"""
import csv, hashlib, os, sys

REPO = "/home/ubuntu/Certonomous"
HERE = os.path.join(REPO, "docs/campaigns/F14-cooling-ladder/demo/plots_K2_transient")
F14 = os.path.join(REPO, "verification/runs/F14-cooling-ladder")
sys.path.insert(0, os.path.join(REPO, "sdk"))
from workflows.act_plots_lib import force_history, grid_family

K = 273.15
LIM = {"recommended 27 °C": 27.0, "allowable 32 °C": 32.0}
prov = []

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def note(fig, path, tdir):
    prov.append((fig, path, tdir, sha(path)))

def wcsv(stem, header, rows):
    with open(os.path.join(HERE, stem + ".csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)

def series(path):
    t, v = [], []
    for ln in open(path):
        if ln.startswith("#"):
            continue
        p = ln.split()
        if len(p) >= 2:
            t.append(float(p[0])); v.append(float(p[1]))
    return t, v

def resample(t, v, grid):
    out, j = [], 0
    for g in grid:
        while j + 1 < len(t) and t[j + 1] <= g:
            j += 1
        out.append(v[j])
    return out

# ------------------------------------------------------------------ 1. ride-through
D59 = os.path.join(F14, "K2b_runs/K2bU3R3_D59")
ser, tref = {}, None
for i in range(4):
    p = os.path.join(D59, "postProcessing/T_rack%d_in_mdot/0/surfaceFieldValue.dat" % i)
    t, v = series(p)
    note("k2t_ride_through.png", p, "0")
    if tref is None:
        tref = t
    ser["rack %d" % (i + 1)] = [x - K for x in (v if t == tref else resample(t, v, tref))]
force_history(os.path.join(HERE, "k2t_ride_through.png"), tref, series=ser,
              xlabel="time  [s]", ylabel="inlet temperature  [°C]", limits=LIM,
              title="Rack inlet temperature against time")
wcsv("k2t_ride_through", ["time_s"] + list(ser),
     [[tref[i]] + [ser[k][i] for k in ser] for i in range(len(tref))])

# ------------------------------------------------------------------ 2. 2-D vs 3-D
p2 = os.path.join(F14, "K2b_runs/K2bU3_L025/postProcessing/T_rack_in_mdot/0/surfaceFieldValue.dat")
t2, v2 = series(p2)
note("k2t_2d_vs_3d.png", p2, "0")
hottest = [max(ser[k][i] for k in ser) for i in range(len(tref))]
tmax = min(max(tref), max(t2))
g = [x for x in tref if x <= tmax]
force_history(os.path.join(HERE, "k2t_2d_vs_3d.png"), g,
              series={"room (3-D, 137,000 cells)": hottest[:len(g)],
                      "slice (2-D, 11,600 cells)": [x - K for x in resample(t2, v2, g)]},
              xlabel="time  [s]", ylabel="hottest inlet  [°C]",
              title="Hottest rack inlet, room against slice")
wcsv("k2t_2d_vs_3d", ["time_s", "room_degC", "slice_degC"],
     [[g[i], hottest[i], (resample(t2, v2, g))[i] - K] for i in range(len(g))])

# ------------------------------------------------------------------ 3. K2h module Δp history
DP = os.path.join(F14, "K2h_runs/K2h_L3/postProcessing")
tt, vv = [], []
for d in sorted(os.listdir(os.path.join(DP, "dp_tile")), key=float):
    p = os.path.join(DP, "dp_tile", d, "surfaceFieldValue.dat")
    a, b = series(p)
    note("k2t_dp_history.png", p, d)
    for x, y in zip(a, b):
        while tt and x <= tt[-1]:
            tt.pop(); vv.pop()
        tt.append(x); vv.append(y)
force_history(os.path.join(HERE, "k2t_dp_history.png"), tt,
              series={"module Δp": vv}, window=(42.0, 112.0),
              xlabel="time  [s]", ylabel="module Δp  [m²/s²]",
              title="Module pressure drop through the record")
wcsv("k2t_dp_history", ["time_s", "DP_module_m2_s2"], list(zip(tt, vv)))

# The ordered iso-surface volume above 27 degC per write is NOT emitted by this run
# (only t = 0, 10 and 110 are written).  The library's registered placeholder is used.
force_history(os.path.join(HERE, "k2t_hot_cloud.png"), pending=True,
              xlabel="time  [s]", ylabel="volume above limit  [m³]",
              title="Volume above the 27 °C limit")

# ------------------------------------------------------------------ 4. temporal family
grid_family(os.path.join(HERE, "k2t_temporal_family.png"), pending=True,
            quantity="time to 27 °C", unit="[s]",
            title="Temporal family, crossing time")

with open(os.path.join(HERE, "PROVENANCE.tsv"), "w") as f:
    f.write("figure\tartifact\ttime_dir\tsha256\n")
    for r in prov:
        f.write("\t".join(str(x) for x in r) + "\n")
print("ride-through n:", len(tref), "t", tref[0], "->", tref[-1],
      "final:", {k: round(ser[k][-1], 3) for k in ser})
print("2d vs 3d n:", len(g), "slice t", t2[0], "->", t2[-1])
print("dp n:", len(tt), "t", tt[0], "->", tt[-1])
print("pngs:", sorted(x for x in os.listdir(HERE) if x.endswith(".png")))
