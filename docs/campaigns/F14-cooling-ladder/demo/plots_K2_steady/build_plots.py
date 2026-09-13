#!/usr/bin/env python3
"""Build the K2 STEADY (rack-row) demo plot folder from REAL fields on disk.

Zero solver compute.  Readers reused, never re-derived:
  * verification/runs/F14-cooling-ladder/K2g_runs/foam_patch_reader.py -- the FROZEN
    reader every K2f/K2g level is graded through (area-weighted patch average).
  * the runs' own function-object output (postProcessing/*.dat) and solver logs.

Figure names are the plot orders' names (docs/plot_orders/README_PLOT_ORDERS.md B).
No verdict stamp and no band annotation is drawn on any image: both live in
SIDECAR.md and README.md (owner correction, 2026-09-13).
"""
import csv, hashlib, json, os, re, sys

REPO = "/home/ubuntu/Certonomous"
HERE = os.path.join(REPO, "docs/campaigns/F14-cooling-ladder/demo/plots_K2_steady")
F14 = os.path.join(REPO, "verification/runs/F14-cooling-ladder")
sys.path.insert(0, os.path.join(REPO, "sdk"))
sys.path.insert(0, os.path.join(F14, "K2g_runs"))
from workflows.act_residual_frames import residual_frames
from workflows.act_plots_lib import (grid_family, residual_history, vertical_profiles,
                                     metric_bars, sweep_curve, envelope_map, cost_vs_setpoint)
import foam_patch_reader as R

BAND_DP = (27.9699, 28.0901)          # K2g_PREREGISTRATION.md section 5, G-DP
LIM = {"limit 27 °C": 27.0}   # ONE limit, the user's. No "recommended", no "allowable", no 32.
K = 273.15
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

# ------------------------------------------------------------------ 1. grid family
LEV = [(os.path.join(F14, "K2f_runs/K2f_L1"), 58368, 3000, "L1"),
       (os.path.join(F14, "K2f_runs/K2f_L2"), 196992, 3000, "L2"),
       (os.path.join(F14, "K2g_runs/K2f_L3"), 664848, 803, "L3")]
lv, rows = [], []
for case, cells, t, lab in LEV:
    dp = R.area_average(case, t, "p_rgh", "tile")[0] - R.area_average(case, t, "p_rgh", "return")[0]
    lv.append({"cells": cells, "value": dp, "label": "%s  %s" % (lab, format(cells, ","))})
    rows.append([lab, cells, t, dp])
    note("k2_family.png", os.path.join(case, str(t), "p_rgh"), str(t))
grid_family(os.path.join(HERE, "k2_family.png"), levels=lv,
            quantity="module Δp", unit="[m²/s²]",
            title="Grid family, module pressure drop", band=BAND_DP)
wcsv("k2_family", ["level", "cells", "time_dir", "DP_module_m2_s2"], rows)

# ------------------------------------------------------------------ 2. residuals (fine level)
LOG = os.path.join(F14, "K2g_runs/K2f_L3/log.solve")
pat = re.compile(r"Solving for (\w+), Initial residual = ([0-9.eE+-]+)")
it, res = [], {}
n = 0
for ln in open(LOG, errors="ignore"):
    if ln.startswith("Time = "):
        n += 1
        for k in res:
            if len(res[k]) < n - 1:
                res[k] += [float("nan")] * (n - 1 - len(res[k]))
        it.append(n)
        continue
    m = pat.search(ln)
    if m and n:
        k, v = m.group(1), float(m.group(2))
        res.setdefault(k, [])
        if len(res[k]) < n:
            res[k].append(v)
for k in res:
    res[k] += [float("nan")] * (n - len(res[k]))
want = [("Ux", "$U_x$"), ("Uz", "$U_z$"), ("T", "$T$"), ("p_rgh", "$p_{rgh}$")]
ser = {lab: res[k] for k, lab in want if k in res}
for _f, _p, _n in residual_frames(HERE, "k2_residuals", it, ser, target=1e-5,
                                 final_name="k2_residuals.png"):
    note(os.path.basename(_p), LOG, str(int(_n)))
note("k2_residuals.png", LOG, "803")
wcsv("k2_residuals", ["iteration"] + list(ser), [[it[i]] + [ser[k][i] for k in ser] for i in range(len(it))])

# ------------------------------------------------------------------ 3. inlet profiles
PROF = os.path.join(F14, "K2b_runs/K2bP_C3b_noplant/postProcessing/aisleProfiles/5000")
profiles, prows = [], []
for stem, lab in (("coldAisleMid_T_U.xy", "cold aisle (rack inlet)"),
                  ("hotAisleMid_T_U.xy", "hot aisle (rack exhaust)")):
    p = os.path.join(PROF, stem)
    z, T = [], []
    for ln in open(p):
        c = ln.split()
        if len(c) >= 2:
            z.append(float(c[0])); T.append(float(c[1]) - K)
    profiles.append({"label": lab, "z": z, "T": T})
    prows += [[lab, a, b] for a, b in zip(z, T)]
    note("k2_inlet_profiles.png", p, "5000")
vertical_profiles(os.path.join(HERE, "k2_inlet_profiles.png"), profiles=profiles,
                  limits=LIM, title="Aisle temperature with height")
wcsv("k2_inlet_profiles", ["line", "z_m", "T_degC"], prows)

# ------------------------------------------------------------------ 4. cooling indices
D59 = os.path.join(F14, "K2b_runs/K2bU3R3_D59")
T_sup = R.area_average(D59, 80, "T", "tile")[0]
T_ret = R.area_average(D59, 80, "T", "return")[0]
note("k2_indices.png", os.path.join(D59, "80", "T"), "80")
labels, rci, rti, cap, rec, irows = [], [], [], [], [], []
dT = []
for i in range(4):
    sp = os.path.join(D59, "postProcessing/T_rack%d_in_mdot/0/surfaceFieldValue.dat" % i)
    _, v = series(sp)
    Tin = v[-1]
    Tout = R.area_average(D59, 80, "T", "rack%d_out" % i)[0]
    note("k2_indices.png", sp, "0")
    r = 100.0 * (Tin - T_sup) / (Tout - T_sup)
    labels.append("rack %d" % (i + 1)); rec.append(r); cap.append(100.0 - r)
    rci.append(100.0 * (1.0 - max(Tin - K - 27.0, 0.0) / 5.0))
    dT.append(Tout - Tin)
    irows.append([labels[-1], Tin - K, Tout - K, rci[-1], 100.0 - r, r])
rti_val = 100.0 * (T_ret - T_sup) / (sum(dT) / len(dT))
rti = [rti_val] * 4
metric_bars(os.path.join(HERE, "k2_indices.png"), labels=labels,
            values={"RCI high": rci, "RTI": rti, "capture index": cap, "recirculation": rec},
            limit=100, title="Cooling indices per rack")
wcsv("k2_indices", ["rack", "T_inlet_degC", "T_outlet_degC", "RCI_high_pct",
                    "capture_index_pct", "recirculation_pct"], irows)
wcsv("k2_indices_room", ["T_supply_degC", "T_return_degC", "RTI_pct"],
     [[T_sup - K, T_ret - K, rti_val]])

# ------------------------------------------------------------------ 5. sweeps -- NOT SOLVED
# The eight setpoint/airflow solves the orders call for do not exist in the run tree.
# The library's own registered placeholder is used: the axes and labels are the ordered
# ones and the panel says "run in progress".  Nothing is invented.
sweep_curve(os.path.join(HERE, "k2_map_setpoint.png"), pending=True,
            xlabel="supply temperature  [°C]", ylabel="hottest inlet  [°C]",
            title="Hottest rack inlet vs supply setpoint")
sweep_curve(os.path.join(HERE, "k2_map_airflow.png"), pending=True,
            xlabel="supply airflow  [%]", ylabel="hottest inlet  [°C]",
            title="Hottest rack inlet vs supply airflow")
envelope_map(os.path.join(HERE, "k2_envelope.png"), pending=True,
             xlabel="supply temperature  [°C]", ylabel="supply airflow  [%]",
             title="Operating envelope")
cost_vs_setpoint(os.path.join(HERE, "k2_cost.png"), pending=True,
                 ylabel="relative cost  [–]", xlabel="supply temperature  [°C]",
                 title="Relative cooling cost vs setpoint")

with open(os.path.join(HERE, "PROVENANCE.tsv"), "w") as f:
    f.write("figure\tartifact\ttime_dir\tsha256\n")
    for r in prov:
        f.write("\t".join(str(x) for x in r) + "\n")
print("family:", [(l["label"], round(l["value"], 6)) for l in lv])
print("residual keys:", list(res), "n_iter", n)
print("T_sup", round(T_sup - K, 3), "T_ret", round(T_ret - K, 3), "RTI", round(rti_val, 2))
print("indices:", [(l, round(a, 2), round(b, 2), round(c, 2)) for l, a, b, c in zip(labels, rci, cap, rec)])
print("pngs:", sorted(x for x in os.listdir(HERE) if x.endswith(".png")))
