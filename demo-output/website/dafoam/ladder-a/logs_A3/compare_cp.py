#!/usr/bin/env python3
"""
Compare extracted CFD Cp (cp_extracted.json, from extract_cp.py) against the
AGARD AR-138 / NASA-TMR experimental Case 2308 data (case_2308.dat), at the
7 standard eta stations. Splits each station's data into upper (suction) and
lower (pressure) surface by sign of the local thickness coordinate, then
linearly interpolates both curves onto a common set of x/c query points and
reports pointwise + aggregate deviation.
"""
import json
import re
import numpy as np
import sys

cfd = json.load(open("cp_extracted.json"))
raw = open("case_2308.dat").read().splitlines()

# ---- parse case_2308.dat ----
sec = None
exp = {}  # section number -> list of (x/c, z/c, cp)
for l in raw:
    l = l.strip()
    if l.startswith("ZONE"):
        m = re.search(r"Section (\d+)", l)
        sec = int(m.group(1))
        exp[sec] = []
    elif l and not l.startswith("TITLE") and not l.startswith("VARIABLES"):
        parts = l.split()
        if len(parts) == 5:
            _, _, xoc, zoc, cp = (float(p) for p in parts)
            exp[sec].append((xoc, zoc, cp))

# section -> eta mapping (Destarac & Dumont, NASA TMR ONERA_M6_Test_Case_TMR.pdf, Table 3)
sec_eta = {1: 0.20, 2: 0.44, 3: 0.65, 4: 0.80, 5: 0.90, 6: 0.96, 7: 0.99}
eta_sec = {v: k for k, v in sec_eta.items()}

stations = [0.20, 0.44, 0.65, 0.80, 0.90, 0.96, 0.99]


def split_surfaces(xoc, zoc_or_y, cp):
    xoc = np.array(xoc)
    z = np.array(zoc_or_y)
    cp = np.array(cp)
    upper = z >= 0
    lower = ~upper
    return (xoc[upper], cp[upper]), (xoc[lower], cp[lower])


def interp_sorted(xq, x, y):
    order = np.argsort(x)
    x = np.array(x)[order]
    y = np.array(y)[order]
    # dedupe identical x
    xu, idx = np.unique(x, return_index=True)
    yu = y[idx]
    return np.interp(xq, xu, yu, left=np.nan, right=np.nan)


qpts = np.arange(0.05, 0.951, 0.05)

report = {}
print(f"{'eta':>6} {'surf':>6} {'n_cfd':>6} {'n_exp':>6} {'n_common':>8} {'RMSdev':>9} {'MAXdev':>9} {'meanBias':>9}")
for eta in stations:
    sdata = cfd["stations"].get(str(eta), {})
    if sdata.get("n_points", 0) == 0:
        continue
    (xu_c, cpu_c), (xl_c, cpl_c) = split_surfaces(sdata["xoc"], sdata["y"], sdata["cp"])

    secnum = eta_sec[eta]
    exp_rows = exp[secnum]
    xoc_e = [r[0] for r in exp_rows]
    zoc_e = [r[1] for r in exp_rows]
    cp_e = [r[2] for r in exp_rows]
    (xu_e, cpu_e), (xl_e, cpl_e) = split_surfaces(xoc_e, zoc_e, cp_e)

    report[eta] = {}
    for surf, (xc, cpc, xe, cpe) in [
        ("upper", (xu_c, cpu_c, xu_e, cpu_e)),
        ("lower", (xl_c, cpl_c, xl_e, cpl_e)),
    ]:
        cfd_i = interp_sorted(qpts, xc, cpc)
        exp_i = interp_sorted(qpts, xe, cpe)
        valid = ~np.isnan(cfd_i) & ~np.isnan(exp_i)
        if valid.sum() == 0:
            continue
        dev = cfd_i[valid] - exp_i[valid]
        rms = float(np.sqrt(np.mean(dev ** 2)))
        mx = float(np.max(np.abs(dev)))
        bias = float(np.mean(dev))
        n_common = int(valid.sum())
        report[eta][surf] = {
            "n_cfd": len(xc), "n_exp": len(xe), "n_common": n_common,
            "rms_dev": rms, "max_dev": mx, "mean_bias": bias,
            "qpts": qpts[valid].tolist(),
            "cfd": cfd_i[valid].tolist(),
            "exp": exp_i[valid].tolist(),
        }
        print(f"{eta:6.2f} {surf:>6} {len(xc):6d} {len(xe):6d} {n_common:8d} {rms:9.4f} {mx:9.4f} {bias:9.4f}")

json.dump(report, open("cp_comparison.json", "w"), indent=1)
print("wrote cp_comparison.json")
