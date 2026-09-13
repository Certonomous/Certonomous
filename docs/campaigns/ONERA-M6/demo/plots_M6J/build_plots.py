#!/usr/bin/env python3
"""Build the ONERA M6 (M6J family) demo plot folder from REAL fields on disk.

Zero solver compute.  Every array is read from the run tree; nothing is typed in.
Readers reused, never re-derived:
  * the family's own Cp extraction  -- verification/runs/M6J_runs/<L>/cp_extracted.json
    (written by verification/runs/M6I_runs/extract_cp_m6i.py, the file the grader read)
  * the grader's own reference reader and upper/lower split --
    scripts/grade_m6_agard_cp.py  read_reference() / cfd_curve()

Figure names are the plot orders' names (docs/plot_orders/README_PLOT_ORDERS.md A).
No verdict stamp and no band annotation is drawn on any image: both live in the
folder's SIDECAR.md and README.md (owner correction, 2026-09-13).
"""
import csv, hashlib, json, os, sys

REPO = "/home/ubuntu/Certonomous"
HERE = os.path.join(REPO, "docs/campaigns/ONERA-M6/demo/plots_M6J")
RUNS = os.path.join(REPO, "verification/runs/M6J_runs")
sys.path.insert(0, os.path.join(REPO, "sdk"))
sys.path.insert(0, os.path.join(REPO, "scripts"))
from workflows.act_plots_lib import cp_stations, grid_family, force_history, residual_history
import grade_m6_agard_cp as G

LEVELS = [("M6J_L3", 15360, "L3"), ("M6J_L2", 122880, "L2"), ("M6J_L1", 983040, "L1")]
FINE = "M6J_L1"
STATIONS = (0.20, 0.44, 0.65, 0.80, 0.90, 0.96)
BAND_CP = 0.050

prov = []          # (figure, artifact path, time dir, sha256)

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def note(fig, path, tdir):
    prov.append((fig, path, tdir, sha(path)))

def wcsv(stem, header, rows):
    p = os.path.join(HERE, stem + ".csv")
    with open(p, "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)
    return p

# ------------------------------------------------------------------ 1. Cp stations
grade_f = os.path.join(RUNS, FINE, "m6j_grade_%s.json" % FINE)
grade = json.load(open(grade_f))
ref_f = grade["reference"]["file"]
ref = G.read_reference(ref_f)
ext_f = os.path.join(RUNS, FINE, "cp_extracted.json")
ext = json.load(open(ext_f))
vtp_time = ext["vtp"].rsplit("/", 3)[1]        # e.g. M6J_L1_8000

stations, cprows = [], []
for eta in STATIONS:
    blk = ext["stations"]["%g" % eta]
    up = G.cfd_curve(blk, "upper", blk.get("x_le"), blk.get("x_te"))
    lo = G.cfd_curve(blk, "lower", blk.get("x_le"), blk.get("x_te"))
    rup = ref[(round(eta, 4), "upper")]
    rlo = ref[(round(eta, 4), "lower")]
    stations.append({"eta": eta,
                     "xc": [t[0] for t in up], "cp_cfd": [t[1] for t in up],
                     "xc_exp": [p[0] for p in rup], "cp_exp": [p[1] for p in rup]})
    for surf, cur, rr in (("upper", up, rup), ("lower", lo, rlo)):
        for x, c in cur:
            cprows.append([eta, surf, "cfd", x, c])
        for x, c in rr:
            cprows.append([eta, surf, "tunnel", x, c])
cp_stations(os.path.join(HERE, "m6_cp_stations.png"), stations=stations,
            title="Surface pressure at six AGARD stations", band=BAND_CP)
wcsv("m6_cp_stations", ["eta", "surface", "source", "x_over_c", "Cp"], cprows)
note("m6_cp_stations.png", ext_f, vtp_time)
note("m6_cp_stations.png", ref_f, "-")
note("m6_cp_stations.png", grade_f, vtp_time)

# ------------------------------------------------------------------ 2. grid family
lv, frows = [], []
for name, cells, lab in LEVELS:
    gf = os.path.join(RUNS, name, "m6j_grade_%s.json" % name)
    g = json.load(open(gf))
    rms = [r["rms_dev"] for r in g["cp_rows"].values()]
    val = sum(rms) / len(rms)
    lv.append({"cells": cells, "value": val, "label": "%s  %s" % (lab, format(cells, ","))})
    frows.append([name, cells, val, g["verdict"]])
    note("m6_family.png", gf, json.load(open(os.path.join(RUNS, name, "cp_extracted.json")))["vtp"].rsplit("/", 3)[1])
grid_family(os.path.join(HERE, "m6_family.png"), levels=lv,
            quantity="row RMS $C_p$ deviation", unit="[–]",
            title="Grid family, Cp deviation from tunnel", band=(0.0, BAND_CP))
wcsv("m6_family", ["level", "cells", "mean_row_rms_Cp_deviation", "verdict"], frows)

# ------------------------------------------------------------------ 3. forces
def read_cols(path, want):
    hdr, out = None, []
    for ln in open(path):
        if ln.startswith("#"):
            if "Time" in ln:
                hdr = ln.lstrip("#").split()
            continue
        p = ln.split()
        if hdr and len(p) == len(hdr):
            out.append([float(x) if _f(x) else x for x in p])
    idx = {k: hdr.index(k) for k in want if k in hdr}
    return hdr, out, idx

def _f(x):
    try:
        float(x); return True
    except ValueError:
        return False

fdirs = sorted(os.listdir(os.path.join(RUNS, FINE, "postProcessing/forceCoeffs")), key=float)
it, cd, cl = [], [], []
for d in fdirs:
    p = os.path.join(RUNS, FINE, "postProcessing/forceCoeffs", d, "coefficient.dat")
    hdr, rows, idx = read_cols(p, ("Time", "Cd", "Cl"))
    for r in rows:
        t = r[idx["Time"]]
        while it and t <= it[-1]:
            it.pop(); cd.pop(); cl.pop()
        it.append(t); cd.append(r[idx["Cd"]]); cl.append(r[idx["Cl"]])
    note("m6_forces.png", p, d)
force_history(os.path.join(HERE, "m6_forces.png"), it,
              series={"$C_L$": cl, "$C_D$": cd},
              title="Force coefficients, fine level", ylabel="coefficient  [–]")
wcsv("m6_forces", ["iteration", "Cl", "Cd"], list(zip(it, cl, cd)))

# ------------------------------------------------------------------ 4. residuals
rdirs = sorted(os.listdir(os.path.join(RUNS, FINE, "postProcessing/residuals")), key=float)
want = ["Ux_initial", "Uy_initial", "Uz_initial", "e_initial", "p_initial"]
rit, series = [], {k: [] for k in want}
for d in rdirs:
    p = os.path.join(RUNS, FINE, "postProcessing/residuals", d, "solverInfo.dat")
    hdr, rows, idx = read_cols(p, ["Time"] + want)
    for r in rows:
        t = r[idx["Time"]]
        while rit and t <= rit[-1]:
            rit.pop()
            for k in want: series[k].pop()
        rit.append(t)
        for k in want: series[k].append(r[idx[k]])
    note("m6_residuals.png", p, d)
lab = {"Ux_initial": "$U_x$", "Uy_initial": "$U_y$", "Uz_initial": "$U_z$",
       "e_initial": "$e$", "p_initial": "$p$"}
residual_history(os.path.join(HERE, "m6_residuals.png"), rit,
                 series={lab[k]: series[k] for k in want}, target=1e-6,
                 title="Initial residuals, fine level")
wcsv("m6_residuals", ["iteration"] + [lab[k] for k in want],
     [[rit[i]] + [series[k][i] for k in want] for i in range(len(rit))])

# ------------------------------------------------------------------ provenance
with open(os.path.join(HERE, "PROVENANCE.tsv"), "w") as f:
    f.write("figure\tartifact\ttime_dir\tsha256\n")
    for r in prov:
        f.write("\t".join(str(x) for x in r) + "\n")
print("figures written:", sorted(x for x in os.listdir(HERE) if x.endswith(".png")))
print("family:", [(l["label"], round(l["value"], 4)) for l in lv])
print("forces n:", len(it), "residuals n:", len(rit))
