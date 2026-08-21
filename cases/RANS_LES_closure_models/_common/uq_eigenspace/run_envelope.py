#!/usr/bin/env python3
"""PART A.3 -- the registered question, a-priori, on frozen TRAINING-family fields.

Does the LES/DNS truth lie inside the eigenspace perturbation envelope?
Per case, per quantity, as fractions. Registered in
`cases/RANS_LES_closure_models/NASA_hump_gate/PREREGISTRATION.md` A.3 before any
number below was computed. Nothing is fitted; nothing is solved.
"""
from __future__ import annotations
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, COMMON)
import eigenspace as E
from of_read import read_field, sym_to_full, anisotropy
import sst_baseline_metrics as SB

OUT = "/home/ubuntu/closure-data/uq_eigenspace"
os.makedirs(OUT, exist_ok=True)
DELTAS = (0.25, 0.50, 0.75, 1.00)

# TRAINING-family only. No TEST case, no hump. (PREREGISTRATION A.3)
CASES = [
    ("PHLL10595", os.path.join(SB.DATA, "PH_Breuer"), "hill"),
    ("CBFS13700", os.path.join(SB.DATA, "CBFS"), "hill"),
    ("AR_1_Ret_180", os.path.join(SB.DATA, "DUCT", "AR_1_Ret_180"), "duct"),
    ("AR_3_Ret_180", os.path.join(SB.DATA, "DUCT", "AR_3_Ret_180"), "duct"),
    ("alpha_10_9000_3036", None, "hill"),
    ("alpha_05_7071_3036", None, "hill"),
    ("alpha_15_10929_3036", None, "hill"),
    ("alpha_125", None, "hill"),
]


def main():
    rows = {}
    for name, path, fam in CASES:
        if path is None:
            path = SB.PH_ALPHA[name]
        d = SB.load_case(name, path, fam)
        A = np.asarray(d["gradU"]).reshape(-1, 3, 3).transpose(0, 2, 1)   # dU_i/dx_j
        k = d["k"]
        kref = float(np.mean(np.abs(d["k_LES"])))
        b_R, okR = anisotropy(sym_to_full(d["tau_R"]), k, k_ref=kref)
        b_L, okL = anisotropy(sym_to_full(d["tau_LES"]), d["k_LES"])
        m = okR & okL & np.isfinite(b_R).all(axis=(1, 2)) & np.isfinite(b_L).all(axis=(1, 2))
        b_R, b_L, kk, AA = b_R[m], b_L[m], k[m], A[m]
        n = int(m.sum())

        c_R, lam_R, _ = E.barycentric_coords(b_R)
        c_L, lam_L, _ = E.barycentric_coords(b_L)
        Pk_L = E.production(b_L, d["k_LES"][m], AA)

        row = {"n_cells": n, "n_masked": int((~m).sum()),
               "truth_unrealisable_frac": float((c_L.min(axis=1) < -1e-7).mean()),
               "shape_cover": {}, "prod_cover": {}, "impl_nonrealisable": {}}

        for dB in DELTAS:
            cs = np.stack([E.perturb_eigenvalues(c_R, t, dB) for t in E.CORNERS])
            row["impl_nonrealisable"][f"{dB:.2f}"] = sum(
                E.assert_realisable(cs[i]) for i in range(3))
            row["shape_cover"][f"{dB:.2f}"] = float(E.inside_hull_c(c_L, cs).mean())
            states, labels = E.five_states(b_R, AA, dB)
            Pk = np.stack([E.production(s, kk, AA) for s in states])
            lo, hi = E.envelope(Pk)
            row["prod_cover"][f"{dB:.2f}"] = float(((Pk_L >= lo) & (Pk_L <= hi)).mean())

        req = E.delta_B_required(c_R, c_L)
        fin = np.isfinite(req)
        row["delta_B_req"] = {
            "median": float(np.median(req[fin])) if fin.any() else None,
            "p95": float(np.percentile(req[fin], 95)) if fin.any() else None,
            "frac_gt_1": float((req > 1.0).mean()),
            "frac_infinite": float((~fin).mean())}
        rows[name] = row
        print(f"[{name:20s}] n={n:6d} truth_unreal={row['truth_unrealisable_frac']:.4f} "
              f"shape@1.0={row['shape_cover']['1.00']:.4f} "
              f"prod@1.0={row['prod_cover']['1.00']:.4f} "
              f"dBreq_med={row['delta_B_req']['median']:.3f} "
              f"dBreq_p95={row['delta_B_req']['p95']:.3f} "
              f"frac>1={row['delta_B_req']['frac_gt_1']:.4f}", flush=True)
    json.dump(rows, open(os.path.join(OUT, "envelope.json"), "w"), indent=1)

    sh1 = [v["shape_cover"]["1.00"] for v in rows.values()]
    pr1 = [v["prod_cover"]["1.00"] for v in rows.values()]
    med = [v["delta_B_req"]["median"] for v in rows.values()]
    bad = sum(sum(v["impl_nonrealisable"].values()) for v in rows.values())
    print(f"\nP-A1 shape@1.0 >= 0.95 on every case : min={min(sh1):.4f} -> "
          f"{'PASS' if min(sh1) >= 0.95 else 'GATE FAIL'}")
    print(f"P-A2 prod@1.0 < 0.95 on >= one case  : min={min(pr1):.4f} max={max(pr1):.4f} -> "
          f"{'PASS' if min(pr1) < 0.95 else 'GATE FAIL'}")
    print(f"P-A3 median delta_B_req in [0.2,0.8] : min={min(med):.3f} max={max(med):.3f} -> "
          f"{'PASS' if all(0.2 <= x <= 0.8 for x in med) else 'GATE FAIL'}")
    print(f"implementation check, cells leaving the simplex under eq.(7): {bad}")


if __name__ == "__main__":
    main()
