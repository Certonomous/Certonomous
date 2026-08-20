#!/usr/bin/env python3
"""The Charter-2c ANISOTROPY baseline: a single constant tensor.

Computes the mean b_LES over the Phase-3 training cells and scores that constant,
as a prediction, against the LES/DNS truth on the 8 strict TEST cases. Also
recomputes the k-omega SST and `b = 0` errors on the IDENTICAL cell mask, so all
three are comparable.

Why this exists: the SST anisotropy error is not a demanding baseline. A constant
tensor beats it on every held-out case (see the table this writes). Any
anisotropy model in cases/RANS_LES_closure_models/ must therefore beat the
TRAIN-MEAN predictor, not merely SST.

Nothing is fitted beyond an arithmetic mean. Reads only; writes one JSON here.

Usage:  /home/ubuntu/closure-venv/bin/python trainmean_baseline.py
"""
from __future__ import annotations
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from of_read import realisability_violation
from score_prediction import load, frob_rms

OUT = os.path.join(HERE, "trainmean_baseline.json")

# ---- the Phase-3 split, restated here so this script is self-contained -------
# Identical to cases/RANS_LES_closure_models/Ling2016_TBNN/PREREGISTRATION.md s.6.
TEST = ["alpha_15_13929_4048", "alpha_15_13929_2024",
        "alpha_05_4071_4048", "alpha_05_4071_2024",
        "AR_1_Ret_360", "AR_3_Ret_360", "AR_14_Ret_180", "NASA_2DWMH"]
VAL = ["alpha_05_10071_4048", "alpha_05_10071_2024",
       "alpha_15_7929_4048", "alpha_15_7929_2024", "AR_7_Ret_180"]
# hills in the same (alpha, length) triple as a TEST/VAL hill: excluded from
# training to stop a near-duplicate leak (BASELINES.md sec. 6.2).
GROUP_EXCLUDED = ["alpha_15_13929_3036", "alpha_05_4071_3036",
                  "alpha_05_10071_3036", "alpha_15_7929_3036"]


def main():
    d = load()
    names, cid, bL, bR, valid = d["names"], d["cid"], d["b_LES"], d["b_RANS"], d["valid"]
    cid_of = {n: i for i, n in enumerate(names)}
    held = set(TEST) | set(VAL) | set(GROUP_EXCLUDED)
    train_cases = [n for n in names if n not in held]
    m_train = np.isin(cid, [cid_of[c] for c in train_cases]) & valid

    b_mean = bL[m_train].mean(0)
    out = {
        "definition": "constant prediction b_pred(x) = mean of b_LES over the training cells",
        "train_cases": sorted(train_cases),
        "n_train_cases": len(train_cases),
        "n_train_cells": int(m_train.sum()),
        "excluded_for_group_leak": sorted(GROUP_EXCLUDED),
        "val_cases": sorted(VAL),
        "test_cases": sorted(TEST),
        "b_mean": [[round(float(x), 6) for x in row] for row in b_mean],
        "b_mean_frobenius": float(np.linalg.norm(b_mean)),
        "cell_mask": ("valid = k_LES above the anisotropy floor AND b_LES, b_RANS and the "
                      "17 extended features all finite; the last condition drops 567 cells "
                      "that BASELINES.md sections 3-5 keep, so these SST numbers differ in "
                      "the fourth decimal from those tables and are the ones a Phase-3 "
                      "reproduction must quote"),
        "per_case": {},
    }
    vio_mean, _ = realisability_violation(b_mean[None])
    out["b_mean_realisable"] = bool(not vio_mean[0])

    for c in TEST:
        m = valid & (cid == cid_of[c])
        tv, _ = realisability_violation(bL[m])
        rv, _ = realisability_violation(bR[m])
        out["per_case"][c] = {
            "n_cells": int(m.sum()),
            "train_mean": frob_rms(bL[m] - b_mean[None]),
            "sst": frob_rms(bR[m] - bL[m]),
            "zero": frob_rms(bL[m]),
            "viol_truth": float(tv.mean()),
            "viol_sst": float(rv.mean()),
        }
    m_all = np.isin(cid, [cid_of[c] for c in TEST]) & valid
    out["pooled_TEST"] = {
        "n_cells": int(m_all.sum()),
        "train_mean": frob_rms(bL[m_all] - b_mean[None]),
        "sst": frob_rms(bR[m_all] - bL[m_all]),
        "zero": frob_rms(bL[m_all]),
    }
    n_beat = sum(1 for v in out["per_case"].values() if v["train_mean"] < v["sst"])
    out["n_test_cases_where_constant_beats_sst"] = n_beat
    out["n_test_cases"] = len(TEST)

    json.dump(out, open(OUT, "w"), indent=1)
    print(f"train cases {len(train_cases)}, train cells {out['n_train_cells']}")
    print("b_mean =\n", np.round(b_mean, 4))
    print(f"realisable: {out['b_mean_realisable']}")
    for c in TEST:
        v = out["per_case"][c]
        print(f"  {c:22s} n={v['n_cells']:6d} train_mean={v['train_mean']:.4f} "
              f"sst={v['sst']:.4f} zero={v['zero']:.4f} "
              f"{'CONSTANT WINS' if v['train_mean'] < v['sst'] else 'sst wins'}")
    p = out["pooled_TEST"]
    print(f"  pooled                 n={p['n_cells']:6d} train_mean={p['train_mean']:.4f} "
          f"sst={p['sst']:.4f} zero={p['zero']:.4f}")
    print(f"constant beats SST on {n_beat} of {len(TEST)} test cases -> {OUT}")


if __name__ == "__main__":
    main()
