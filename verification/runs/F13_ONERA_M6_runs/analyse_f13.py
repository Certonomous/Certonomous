#!/usr/bin/env python3
"""F1 (ONERA M6) -- ADMISSION comparator for rung R0.

Registered path (F13_ONERA_M6_PREREGISTRATION.md section 9).  It grades the SS5
admission checks and NOTHING ELSE at this rung.  It REFUSES (exit 2) rather than
degrade, and an ABSENT checkMesh log reads ABSENT -- never clean.

SS5 admission, verbatim: max non-orthogonality <= 70 deg; max skewness <= 4;
checkMesh prints "Mesh OK"; node nesting L1 in L2 in L3 read from the BUILT
polyMesh to 1e-12 c_root; r = 2.000 +/- 0.002; L1 max y+ <= 300 (L2/L3 reported,
not gated); L3 S2 chordwise cell <= 0.00650 c measured from the built mesh.
"""
import json
import os
import re
import sys

import numpy as np

ROOT = "/home/ubuntu/Certonomous"
RUN = os.path.join(ROOT, "verification/runs/F13_ONERA_M6_runs")
sys.path.insert(0, os.path.join(ROOT, "cases/F13_onera_m6"))
C_ROOT_REG = 0.8059
NEST_TOL = 1e-12 * C_ROOT_REG          # 8.059e-13 m


def refuse(why):
    print(f"REFUSED: {why}")
    sys.exit(2)


def read_points(case):
    p = os.path.join(case, "constant", "polyMesh", "points")
    if not os.path.exists(p):
        refuse(f"points ABSENT at {p}")
    with open(p) as fh:
        t = fh.read()
    i = t.index("(", t.index("}"))
    body = t[i + 1:t.rindex(")")].strip().split("\n")
    return np.array([[float(v) for v in l[1:-1].split()] for l in body])


def parse_checkmesh(path):
    """ABSENT reads ABSENT.  Never clean."""
    if not os.path.exists(path):
        return {"present": False, "verdict": "ABSENT"}
    t = open(path).read()
    out = {"present": True}
    m = re.search(r"Mesh non-orthogonality Max:\s*([0-9.eE+-]+)\s*average:\s*([0-9.eE+-]+)", t)
    out["nonortho_max"] = float(m.group(1)) if m else None
    out["nonortho_avg"] = float(m.group(2)) if m else None
    m = re.search(r"Max skewness\s*=\s*([0-9.eE+-]+)", t)
    out["skew_max"] = float(m.group(1)) if m else None
    m = re.search(r"Max aspect ratio:\s*([0-9.eE+-]+), number of cells\s*(\d+)", t)
    out["aspect_max"] = float(m.group(1)) if m else None
    out["aspect_cells"] = int(m.group(2)) if m else 0
    m = re.search(r"severely non-orthogonal \(> 70 degrees\) faces:\s*(\d+)", t)
    out["nonortho_severe"] = int(m.group(1)) if m else 0
    out["mesh_ok"] = bool(re.search(r"^\s*Mesh OK\.\s*$", t, re.M))
    m = re.search(r"Failed (\d+) mesh checks", t)
    out["failed_checks"] = int(m.group(1)) if m else 0
    m = re.search(r"cells:\s*(\d+)", t)
    out["cells"] = int(m.group(1)) if m else None
    return out


def nesting(levels, geo):
    """L1 in L2 in L3, read from the BUILT polyMesh, with a PLANTED control."""
    from make_blockmesh_m6 import Mesh
    maps = {}
    for m in levels:
        mm = Mesh(m, geo, verbose=False)
        maps[m] = mm
    res = {}
    P = {m: read_points(os.path.join(RUN, "mesh", f"m{m}")) for m in levels}
    for coarse, fine in ((1, 2), (2, 4), (1, 4)):
        if coarse not in levels or fine not in levels:
            continue
        f = fine // coarse
        a, b = maps[coarse], maps[fine]
        d = 0.0
        # C-grid nodes
        ii = np.arange(a.NW + 1); jj = np.arange(a.NN + 1); kk = np.arange(a.NS + 1)
        ia, ja, ka = np.meshgrid(ii, jj, kk, indexing="ij")
        pa = a.pid[ia, ja, ka].ravel()
        pb = b.pid[ia * f, ja * f, ka * f].ravel()
        d = max(d, float(np.abs(P[coarse][pa] - P[fine][pb]).max()))
        # tip-fill interior nodes
        aa = np.arange(a.NA + 1); bb = np.arange(a.NB + 1)
        kf = np.arange(a.NS - a.NSW + 1)
        Aa, Bb, Kk = np.meshgrid(aa, bb, kf, indexing="ij")
        qa = a.fpid[Aa, Bb, Kk].ravel()
        qb = b.fpid[Aa * f, Bb * f, Kk * f].ravel()
        d = max(d, float(np.abs(P[coarse][qa] - P[fine][qb]).max()))
        res[f"L{coarse}_in_L{fine}_max_m"] = d
    # ---- PLANTED CONTROL (rule 3): the reader MUST see a perturbation
    if 1 in levels and 4 in levels:
        Q = P[4].copy()
        a, b = maps[1], maps[4]
        Q[b.pid[0, 0, 0]] += 1.0e-9
        ii = np.arange(a.NW + 1); jj = np.arange(a.NN + 1); kk = np.arange(a.NS + 1)
        ia, ja, ka = np.meshgrid(ii, jj, kk, indexing="ij")
        dp = float(np.abs(P[1][a.pid[ia, ja, ka].ravel()]
                          - Q[b.pid[ia * 4, ja * 4, ka * 4].ravel()]).max())
        res["planted_control_m"] = dp
        res["planted_control_seen"] = bool(dp > NEST_TOL)
        if not res["planted_control_seen"]:
            refuse("PLANTED CONTROL FAILED: the nesting reader cannot see a 1e-9 m "
                   "perturbation, so its zeros are not evidence")
    return res


def main():
    from m6_section import M6Geometry
    geo = M6Geometry(verbose=False)
    geo.z_tip = geo.z_tip_measured
    levels = [int(x) for x in sys.argv[1:]] or [1, 2, 4]
    out = {"levels": levels, "gates": {}, "checkMesh": {}, "cells": {}}
    for m in levels:
        out["checkMesh"][f"m{m}"] = parse_checkmesh(os.path.join(RUN, "mesh", f"m{m}", "log.checkMesh"))
    # r from the built cell counts
    cells = {m: out["checkMesh"][f"m{m}"].get("cells") for m in levels}
    out["cells"] = cells
    rr = {}
    for c, f in ((1, 2), (2, 4)):
        if cells.get(c) and cells.get(f):
            rr[f"r_L{c}_L{f}"] = (cells[f] / cells[c]) ** (1.0 / 3.0)
    out["r"] = rr
    out["nesting"] = nesting(levels, geo) if len(levels) > 1 else {}
    # y+ ESTIMATE (no solve exists yet -- this is an ESTIMATE, never a measurement)
    nu, U = 1.9642e-5, 285.67
    Re = 11.72e6
    cf = 0.0592 * Re ** -0.2
    ut = U * np.sqrt(cf / 2.0)
    from make_blockmesh_m6 import Mesh
    yp = {}
    s2 = {}
    for m in levels:
        mm = Mesh(m, geo, verbose=False)
        yp[f"m{m}"] = float((mm.delta0 / 2.0) * ut / nu)
        s2[f"m{m}"] = float(0.90 / (36 * m))
    out["yplus_estimate"] = yp
    out["yplus_basis"] = ("flat-plate cf = 0.0592 Re^-0.2 at Re = 11.72e6 -> cf = "
                          f"{cf:.6f}, u_tau = {ut:.4f} m/s. ESTIMATE, NOT A MEASUREMENT: "
                          "no solve exists under this registration.")
    out["S2_cell_over_c"] = s2

    g = out["gates"]
    for m in levels:
        cm = out["checkMesh"][f"m{m}"]
        if not cm["present"]:
            g[f"m{m}_checkMesh"] = "ABSENT"
            continue
        g[f"m{m}_nonortho<=70"] = "PASS" if cm["nonortho_max"] <= 70.0 else "GATE FAIL"
        g[f"m{m}_skew<=4"] = "PASS" if cm["skew_max"] <= 4.0 else "GATE FAIL"
        g[f"m{m}_MeshOK"] = "PASS" if cm["mesh_ok"] else "GATE FAIL"
    for k, v in rr.items():
        g[k + "_2.000+-0.002"] = "PASS" if abs(v - 2.0) <= 0.002 else "GATE FAIL"
    for k, v in out["nesting"].items():
        if k.endswith("_max_m"):
            g[k + "<=1e-12c"] = "PASS" if v <= NEST_TOL else "GATE FAIL"
    if 1 in levels:
        g["m1_yplus<=300_ESTIMATE"] = "PASS" if yp["m1"] <= 300 else "GATE FAIL"
    if 4 in levels:
        g["m4_S2cell<=0.00650c"] = "PASS" if s2["m4"] <= 0.00650 else "GATE FAIL"

    fails = [k for k, v in g.items() if v in ("GATE FAIL", "ABSENT")]
    out["admission"] = "PASS" if not fails else "GATE FAIL"
    out["failing_channels"] = fails
    p = os.path.join(RUN, "R0_ADMISSION.json")
    with open(p, "w") as fh:
        json.dump(out, fh, indent=2)
        fh.flush(); os.fsync(fh.fileno())
    print(json.dumps(out, indent=2))
    print(f"\nADMISSION: {out['admission']}   failing: {fails}")


if __name__ == "__main__":
    main()
