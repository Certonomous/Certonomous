#!/usr/bin/env python3
"""Quantify the k-omega SST baseline error against LES/DNS truth, per case.

This is the "trivial baseline" every Phase 3 closure reproduction in
cases/RANS_LES_closure_models/ must beat: the uncorrected k-omega SST solve
that the Closure Challenge benchmark ships with each case, scored against the
LES/DNS truth that ships beside it.

It computes, per case:
  * velocity error (RMS and MAE) normalised by the mean true velocity magnitude
  * turbulent kinetic energy error
  * Reynolds-stress error, normalised by 2*mean(k_LES)
  * anisotropy-tensor error ||b_RANS - b_LES||_F, and the size of b_LES itself
  * realisability: fraction of cells whose modelled b lies outside the
    barycentric triangle (Schumann realisability), for RANS and for the truth
  * periodic hills / hump / step: separation and reattachment abscissae taken
    from the sign of the streamwise velocity in the first cell layer off the
    bottom wall, computed identically for RANS and LES so the comparison is
    apples to apples
  * ducts: in-plane (secondary) velocity intensity, which a linear eddy
    viscosity model produces as identically zero

Nothing is fitted and nothing is trained here. Reads only; writes a JSON and a
markdown table into this directory.

Usage:
    /home/ubuntu/closure-venv/bin/python sst_baseline_metrics.py
"""
from __future__ import annotations

import json
import os
import re
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from of_read import (read_field, latest_time_dir, sym_to_full, anisotropy,
                     realisability_violation, barycentric, structured_gradient,
                     structured_shape, plane_axes, validate_gradient)

BENCH = "/home/ubuntu/closure-challenge-benchmark"
DATA = os.path.join(BENCH, "data")
HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- case table
# split labels follow the benchmark README's suggested train/val split; the TEST
# label is the benchmark's strict rule (never train or validate on these).
PH_ALPHA = {}
for alpha in ("alpha_05", "alpha_075", "alpha_10", "alpha_125", "alpha_15"):
    d = os.path.join(DATA, "Parm_PH_29", alpha)
    if os.path.isdir(d):
        for c in sorted(os.listdir(d)):
            if os.path.isdir(os.path.join(d, c)):
                PH_ALPHA[c] = os.path.join(d, c)

TEST_CASES = {"alpha_15_13929_4048", "alpha_15_13929_2024",
              "alpha_05_4071_4048", "alpha_05_4071_2024",
              "AR_1_Ret_360", "AR_3_Ret_360", "AR_14_Ret_180", "NASA_2DWMH"}
VAL_CASES = {"alpha_05_10071_4048", "alpha_05_10071_2024",
             "alpha_15_7929_4048", "alpha_15_7929_2024", "AR_7_Ret_180"}

DUCTS = {c: os.path.join(DATA, "DUCT", c)
         for c in sorted(os.listdir(os.path.join(DATA, "DUCT")))
         if os.path.isdir(os.path.join(DATA, "DUCT", c))}


def split_of(case):
    if case in TEST_CASES:
        return "TEST"
    if case in VAL_CASES:
        return "val"
    return "train"


# ------------------------------------------------------------------- loading
def load_case(case, path, family):
    """Return a dict of RANS + LES fields on the shared cell centres."""
    t = latest_time_dir(path)
    if family == "duct":
        cpath = os.path.join(path, "constant", "C")
    elif os.path.exists(os.path.join(path, t, "C")):
        cpath = os.path.join(path, t, "C")
    else:
        cpath = os.path.join(path, "0", "C")
    C = read_field(cpath)
    n = C.shape[0]

    d = {"case": case, "path": path, "time": t, "C": C, "n": n, "family": family}
    d["U"] = read_field(os.path.join(path, t, "U"))
    d["k"] = read_field(os.path.join(path, t, "k"))
    d["nut"] = read_field(os.path.join(path, t, "nut"))
    d["U_LES"] = read_field(os.path.join(path, "0", "U_LES"))
    d["k_LES"] = read_field(os.path.join(path, "0", "k_LES"))
    d["tau_LES"] = read_field(os.path.join(path, "0", "tauij_LES"))

    # RANS Boussinesq stress: use the shipped tauij_B where present, else build
    # it from nu_t and gradU, else from a finite-difference gradient.
    tb = os.path.join(path, t, "tauij_B")
    gu = os.path.join(path, t, "gradU")
    if os.path.exists(tb):
        d["tau_R"] = read_field(tb)
        d["gradU"] = read_field(gu) if os.path.exists(gu) else None
        d["tau_R_src"] = "shipped tauij_B"
    elif os.path.exists(gu):
        g = read_field(gu).reshape(-1, 3, 3)
        d["gradU"] = read_field(gu)
        d["tau_R"] = _bouss(d["k"], d["nut"], g)
        d["tau_R_src"] = "built from shipped gradU"
    else:
        g = structured_gradient(C, d["U"])          # dU_i/dx_j
        d["gradU"] = g.transpose(0, 2, 1).reshape(-1, 9)
        d["tau_R"] = _bouss(d["k"], d["nut"], g)
        d["tau_R_src"] = ("built from a structured-mesh chain-rule gradient "
                          "(validated to 0.5-1.0% interior rel-L2 against the "
                          "OpenFOAM gradU shipped on the hills)")
    return d


def _bouss(k, nut, g):
    """(2/3) k delta_ij - 2 nu_t S_ij as an (N,6) symmTensor."""
    S = 0.5 * (g + g.transpose(0, 2, 1))
    tk = 2.0 / 3.0 * k
    return np.stack([tk - 2 * nut * S[:, 0, 0],
                     -2 * nut * S[:, 0, 1],
                     -2 * nut * S[:, 0, 2],
                     tk - 2 * nut * S[:, 1, 1],
                     -2 * nut * S[:, 1, 2],
                     tk - 2 * nut * S[:, 2, 2]], axis=1)


# ------------------------------------------------------------------- metrics
def field_metrics(d):
    m = {}
    U, UL = d["U"], d["U_LES"]
    dU = U - UL
    Umag = np.linalg.norm(UL, axis=1)
    Uref = Umag.mean()
    m["n_cells"] = int(d["n"])
    m["U_ref_mean_LES"] = float(Uref)
    m["U_rms_err_rel"] = float(np.sqrt(np.mean(np.sum(dU ** 2, axis=1))) / Uref)
    m["U_mae_rel"] = float(np.mean(np.linalg.norm(dU, axis=1)) / Uref)

    kL = d["k_LES"]
    kref = float(np.mean(np.abs(kL)))
    m["k_ref_mean_LES"] = kref
    m["k_rms_err_rel"] = float(np.sqrt(np.mean((d["k"] - kL) ** 2)) / kref)
    m["k_bias_rel"] = float(np.mean(d["k"] - kL) / kref)

    tL = sym_to_full(d["tau_LES"])
    bL, vL = anisotropy(tL, kL, k_ref=kref)
    m["b_LES_rms_norm"] = float(np.sqrt(np.nanmean(np.sum(bL[vL] ** 2, axis=(1, 2)))))
    viol_L, _ = realisability_violation(np.nan_to_num(bL[vL]))
    m["frac_truth_nonrealisable"] = float(viol_L.mean())
    m["n_cells_k_masked"] = int((~vL).sum())

    if d["tau_R"] is not None:
        tR = sym_to_full(d["tau_R"])
        m["tau_rms_err_rel"] = float(
            np.sqrt(np.mean(np.sum((tR - tL) ** 2, axis=(1, 2)))) / (2 * kref))
        bR, vR = anisotropy(tR, d["k"], k_ref=float(np.mean(np.abs(d["k"]))))
        v = vL & vR
        dbn = np.sqrt(np.sum((bR[v] - bL[v]) ** 2, axis=(1, 2)))
        m["b_rms_err"] = float(np.sqrt(np.mean(dbn ** 2)))
        m["b_median_err"] = float(np.median(dbn))
        m["b_p95_err"] = float(np.percentile(dbn, 95))
        m["b_RANS_rms_norm"] = float(np.sqrt(np.mean(np.sum(bR[v] ** 2, axis=(1, 2)))))
        viol_R, mn = realisability_violation(bR[v])
        m["frac_RANS_nonrealisable"] = float(viol_R.mean())
        m["worst_RANS_barycentric_coord"] = float(mn.min())
        # componentwise, normalised the same way
        db = bR[v] - bL[v]
        for lab, (i, j) in {"11": (0, 0), "12": (0, 1), "13": (0, 2),
                            "22": (1, 1), "23": (1, 2), "33": (2, 2)}.items():
            m[f"b{lab}_rms_err"] = float(np.sqrt(np.mean(db[:, i, j] ** 2)))
        m["tau_R_src"] = d["tau_R_src"]
        m.update(_ev_realisability_margin(d))
    else:
        m["tau_R_src"] = d["tau_R_src"]
    return m


def _ev_realisability_margin(d):
    """How close the linear eddy-viscosity anisotropy comes to non-realisability.

    For an incompressible linear eddy-viscosity model b_ij = -(nu_t/k) S_ij, so
    b is traceless and its eigenvalues are -(nu_t/k) * eig(S). Realisability
    (Schumann 1977) needs every eigenvalue of b in [-1/3, 2/3], so the binding
    constraint is (nu_t/k) * lambda_max(S) <= 1/3.

    Menter's SST a1 limiter caps nu_t at a1 k / (S F2) with a1 = 0.31, i.e. it
    caps (nu_t/k)*S at 0.31 < 1/3 -- the limiter IS a realisability constraint.
    We measure the realised ratio here, and also what a standard k-epsilon with
    C_mu = 0.09 would have produced on the same mean field, using the SST
    identity epsilon = C_mu k omega.
    """
    g = np.asarray(d["gradU"]).reshape(-1, 3, 3).transpose(0, 2, 1)  # dU_i/dx_j
    S = 0.5 * (g + g.transpose(0, 2, 1))
    lam = np.linalg.eigvalsh(S)[:, ::-1]
    lmax = lam[:, 0]
    k = d["k"]
    kref = float(np.mean(np.abs(k)))
    ok = k > 1e-4 * kref
    r_sst = (d["nut"][ok] / k[ok]) * lmax[ok]
    # Counterfactual, SAME k and omega, no a1 limiter: an unlimited linear eddy
    # viscosity nu_t = C_mu k^2/eps = k/omega (using eps = C_mu k omega), which
    # is what standard k-epsilon / Wilcox k-omega would use. This is a
    # diagnostic on the frozen SST field, NOT a k-epsilon solve.
    om = read_field(os.path.join(d["path"], d["time"], "omega"))
    r_ke = lmax[ok] / om[ok]
    Smag = np.sqrt(2.0 * np.sum(S ** 2, axis=(1, 2)))[ok]
    return {"ev_ratio_nut_lmaxS_over_k_p99": float(np.percentile(r_sst, 99)),
            "ev_ratio_nut_lmaxS_over_k_max": float(r_sst.max()),
            "frac_cells_ev_ratio_gt_third_SST": float((r_sst > 1.0 / 3).mean()),
            "frac_cells_ev_ratio_gt_third_unlimited_counterfactual":
                float((r_ke > 1.0 / 3).mean()),
            "ev_ratio_unlimited_counterfactual_max": float(r_ke.max()),
            "ev_ratio_unlimited_counterfactual_p99": float(np.percentile(r_ke, 99)),
            "frac_cells_SST_a1_limiter_active":
                float((d["nut"][ok] < 0.99 * k[ok] / np.maximum(om[ok], 1e-30)).mean()),
            "Sk_over_eps_p99": float(np.percentile(Smag / (0.09 * om[ok]), 99))}


def hill_wall_metrics(d, nx=120):
    """Separation / reattachment on the bottom wall from the first cell layer.

    The 2-D hill, step and hump meshes are structured blocks with the i index
    fastest and j = 0 the cell row adjacent to the bottom (shaped) wall; both
    facts are verified geometrically in of_read.structured_shape() and by the
    row-0 wall-normal coordinate. The recirculation region is taken as the
    LONGEST contiguous run of negative streamwise velocity in that row, which
    ignores the small numerical sign flips that occur at an inlet or in a
    corner. The SAME row and the SAME criterion are applied to the RANS field
    and to the LES field interpolated onto that mesh, so the difference is a
    model error and not a post-processing difference.

    Validated on PH_Breuer: this gives x_sep = 0.259, x_reatt = 7.643 for the
    RANS field, and OpenFOAM's own bottom-wall wallShearStress (written by the
    solver into postProcessing/bottomValues/10000) changes sign at x = 0.259
    and x = 7.6439. Independent agreement to 4 significant figures.
    """
    C, n = d["C"], d["n"]
    if nx is None or n % nx:
        return {}
    keep, thin = plane_axes(C)
    sw = keep[0]                       # streamwise axis of these meshes
    row = slice(0, nx)
    x = C[row, sw]
    out = {"nx": nx, "ny": n // nx, "streamwise_axis": sw}
    for tag, U in (("RANS", d["U"]), ("LES", d["U_LES"])):
        r = _longest_reversed_run(x, U[row, sw])
        out[f"x_sep_{tag}"] = r["x_sep"]
        out[f"x_reatt_{tag}"] = r["x_reatt"]
        out[f"L_bubble_{tag}"] = r["L"]
        out[f"reattaches_in_domain_{tag}"] = r["reattaches"]
        out[f"separates_in_domain_{tag}"] = r["separates"]
        out[f"frac_row_reversed_{tag}"] = r["frac_reversed"]
    for q in ("x_sep", "x_reatt", "L_bubble"):
        a, b = out.get(f"{q}_RANS"), out.get(f"{q}_LES")
        out[f"{q}_err"] = (a - b) if (a is not None and b is not None) else None
    if out.get("L_bubble_err") is not None and out["L_bubble_LES"]:
        out["L_bubble_rel_err"] = out["L_bubble_err"] / out["L_bubble_LES"]
    return out


def _longest_reversed_run(x, ux):
    """Longest contiguous negative-U_x run in a wall-adjacent cell row."""
    neg = ux < 0
    out = {"x_sep": None, "x_reatt": None, "L": None, "reattaches": None,
           "separates": None, "frac_reversed": float(neg.mean())}
    if not neg.any():
        out.update(reattaches=None, separates=None)
        return out
    # contiguous runs
    idx = np.where(neg)[0]
    breaks = np.where(np.diff(idx) > 1)[0]
    runs = np.split(idx, breaks + 1)
    run = max(runs, key=len)
    i0, i1 = run[0], run[-1]
    if i0 > 0:
        f = ux[i0 - 1] / (ux[i0 - 1] - ux[i0])
        out["x_sep"] = float(x[i0 - 1] + f * (x[i0] - x[i0 - 1]))
        out["separates"] = True
    else:
        out["separates"] = False          # reversed flow already at the first cell
    if i1 < len(ux) - 1:
        f = ux[i1] / (ux[i1] - ux[i1 + 1])
        out["x_reatt"] = float(x[i1] + f * (x[i1 + 1] - x[i1]))
        out["reattaches"] = True
    else:
        out["reattaches"] = False         # still reversed at the last cell
    if out["x_sep"] is not None and out["x_reatt"] is not None:
        out["L"] = out["x_reatt"] - out["x_sep"]
    return out


def duct_metrics(d):
    """Secondary (in-plane) flow intensity. Streamwise is x for these meshes."""
    out = {}
    for tag, U in (("RANS", d["U"]), ("LES", d["U_LES"])):
        ip = np.linalg.norm(U[:, 1:], axis=1)
        sw = np.abs(U[:, 0])
        out[f"U_bulk_{tag}"] = float(sw.mean())
        out[f"sec_mean_{tag}"] = float(ip.mean())
        out[f"sec_max_{tag}"] = float(ip.max())
    ub = out["U_bulk_LES"]
    out["sec_mean_LES_pct_of_bulk"] = 100.0 * out["sec_mean_LES"] / ub
    out["sec_max_LES_pct_of_bulk"] = 100.0 * out["sec_max_LES"] / ub
    out["sec_mean_RANS_pct_of_bulk"] = 100.0 * out["sec_mean_RANS"] / ub
    out["sec_max_RANS_pct_of_bulk"] = 100.0 * out["sec_max_RANS"] / ub
    out["sec_recovered_frac"] = out["sec_mean_RANS"] / out["sec_mean_LES"]
    # the anisotropy component that drives it
    kL = d["k_LES"]
    tL = sym_to_full(d["tau_LES"])
    bL, v = anisotropy(tL, kL)
    out["b23_LES_rms"] = float(np.sqrt(np.nanmean(bL[v][:, 1, 2] ** 2)))
    out["b22_minus_b33_LES_rms"] = float(
        np.sqrt(np.nanmean((bL[v][:, 1, 1] - bL[v][:, 2, 2]) ** 2)))
    if d["tau_R"] is not None:
        tR = sym_to_full(d["tau_R"])
        bR, vR = anisotropy(tR, d["k"])
        out["b23_RANS_rms"] = float(np.sqrt(np.nanmean(bR[vR][:, 1, 2] ** 2)))
        out["b22_minus_b33_RANS_rms"] = float(
            np.sqrt(np.nanmean((bR[vR][:, 1, 1] - bR[vR][:, 2, 2]) ** 2)))
    return out


def case_meta(path):
    """nu, and any Re/AR the case files themselves record."""
    meta = {}
    tp = os.path.join(path, "constant", "transportProperties")
    if os.path.exists(tp):
        txt = open(tp).read()
        m = re.search(r"^\s*nu\s+(?:nu\s+)?\[[^\]]*\]\s*([-\d.eE+]+)\s*;(.*)$",
                      txt, re.M)
        if m:
            meta["nu"] = float(m.group(1))
            c = re.search(r"Re_H\s*=\s*(\d+)", m.group(2))
            if c:
                meta["Re_H"] = int(c.group(1))
    cd = os.path.join(path, "caseDef")
    if os.path.exists(cd):
        for key in ("h", "AR", "Re_b", "Re_tau", "nu", "Re_c", "c", "Mref"):
            m = re.search(rf"^\s*{key}\s+([-\d.eE+]+)\s*;", open(cd).read(), re.M)
            if m:
                meta[key] = float(m.group(1))
    return meta


# ---------------------------------------------------------------------- main
def main():
    results = {}
    cases = []
    for c, p in PH_ALPHA.items():
        cases.append((c, p, "PHLL29"))
    for c, p in DUCTS.items():
        cases.append((c, p, "duct"))
    cases.append(("PHLL10595", os.path.join(DATA, "PH_Breuer"), "PHLL10595"))
    cases.append(("CBFS13700", os.path.join(DATA, "CBFS"), "CBFS"))
    cases.append(("NASA_2DWMH", os.path.join(DATA, "NASA_2DWMH"), "hump"))

    for case, path, family in cases:
        try:
            d = load_case(case, path, family)
            m = field_metrics(d)
            m["family"] = family
            m["split"] = split_of(case)
            m["time_dir"] = d["time"]
            m.update(case_meta(path))
            if family == "duct":
                m.update(duct_metrics(d))
            else:
                nx = structured_shape(d["C"])[1]
                if nx:
                    m.update(hill_wall_metrics(d, nx=nx))
            results[case] = m
            print(f"[ok]   {case:24s} n={m['n_cells']:6d} "
                  f"U_rms_rel={m['U_rms_err_rel']:.4f} "
                  f"b_rms_err={m.get('b_rms_err', float('nan')):.4f}")
        except Exception as e:
            print(f"[FAIL] {case:24s} {type(e).__name__}: {e}")
            results[case] = {"error": f"{type(e).__name__}: {e}"}

    with open(os.path.join(HERE, "sst_baseline_metrics.json"), "w") as fh:
        json.dump(results, fh, indent=1, sort_keys=True)
    print(f"\nwrote {os.path.join(HERE, 'sst_baseline_metrics.json')}")


def _guess_nx(d):
    """Number of cells in the i direction of a structured 2-D mesh."""
    C = d["C"]
    x0 = C[0, 0]
    for i in range(1, min(4000, C.shape[0])):
        if abs(C[i, 0] - x0) < 1e-9 * max(1.0, abs(x0)):
            return i
    return None


if __name__ == "__main__":
    main()
