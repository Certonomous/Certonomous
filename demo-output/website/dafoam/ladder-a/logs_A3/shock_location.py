#!/usr/bin/env python3
"""
Estimate shock chordwise location (x/c of steepest Cp rise, upper/suction
surface only) for both CFD and experiment at each eta station, using each
dataset's own native point distribution (no common-grid interpolation, to
avoid smoothing away the shock).
"""
import json
import re
import numpy as np

cfd = json.load(open("cp_extracted.json"))
raw = open("case_2308.dat").read().splitlines()

sec = None
exp = {}
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

sec_eta = {1: 0.20, 2: 0.44, 3: 0.65, 4: 0.80, 5: 0.90, 6: 0.96, 7: 0.99}
eta_sec = {v: k for k, v in sec_eta.items()}
stations = [0.20, 0.44, 0.65, 0.80, 0.90, 0.96, 0.99]


def shock_xoc(xoc, cp, xmin=0.15, xmax=0.85):
    """Location of max positive dCp/d(x/c) (steepest pressure recovery) within [xmin,xmax]
    of chord, restricting to upper surface, native point spacing."""
    xoc = np.array(xoc)
    cp = np.array(cp)
    order = np.argsort(xoc)
    xoc, cp = xoc[order], cp[order]
    xu, idx = np.unique(xoc, return_index=True)
    cpu = cp[idx]
    mask = (xu >= xmin) & (xu <= xmax)
    if mask.sum() < 3:
        return None, None
    xu_m, cpu_m = xu[mask], cpu[mask]
    dcp = np.diff(cpu_m) / np.diff(xu_m)
    i = np.argmax(dcp)
    x_shock = 0.5 * (xu_m[i] + xu_m[i + 1])
    return float(x_shock), float(dcp[i])


print(f"{'eta':>6} {'CFD x/c':>9} {'CFD slope':>10} {'EXP x/c':>9} {'EXP slope':>10} {'shift(x/c)':>11}")
out = {}
for eta in stations:
    sdata = cfd["stations"].get(str(eta), {})
    if sdata.get("n_points", 0) == 0:
        continue
    xoc_c = np.array(sdata["xoc"])
    cp_c = np.array(sdata["cp"])
    y_c = np.array(sdata["y"])
    upper_c = y_c >= 0
    x_shock_c, slope_c = shock_xoc(xoc_c[upper_c], cp_c[upper_c])

    secnum = eta_sec[eta]
    rows = exp[secnum]
    xoc_e = np.array([r[0] for r in rows])
    zoc_e = np.array([r[1] for r in rows])
    cp_e = np.array([r[2] for r in rows])
    upper_e = zoc_e >= 0
    x_shock_e, slope_e = shock_xoc(xoc_e[upper_e], cp_e[upper_e])

    shift = None
    if x_shock_c is not None and x_shock_e is not None:
        shift = x_shock_c - x_shock_e
    out[eta] = {"cfd_xoc": x_shock_c, "cfd_slope": slope_c, "exp_xoc": x_shock_e, "exp_slope": slope_e, "shift_xoc": shift}
    print(f"{eta:6.2f} {x_shock_c:9.4f} {slope_c:10.3f} {x_shock_e:9.4f} {slope_e:10.3f} {shift:11.4f}")

json.dump(out, open("shock_location.json", "w"), indent=1)
print("wrote shock_location.json")
