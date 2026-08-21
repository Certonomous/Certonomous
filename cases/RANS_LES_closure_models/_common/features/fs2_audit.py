#!/usr/bin/env python3
"""FS2 degeneracy audit + FS5 extrapolation-coverage check on the FS1 library.

Per flow family and per feature: variance, range, the fraction algebraically
zero, and the feature-matrix numerical rank. Plus the tensor-basis per-cell rank
(charter section 5(b)) and the FS5 test-vs-training range coverage.

No training. Reads the FS1 .npz files and the benchmark tensor basis.
"""
from __future__ import annotations
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, COMMON)
sys.path.insert(0, os.path.join(os.path.dirname(COMMON), "Ling2016_TBNN"))
from train_tbnn import TEST

FEAT = "/home/ubuntu/closure-data/features"
OUT_JSON = os.path.join(FEAT, "fs2_audit.json")
ZERO_ABS = 1e-12          # |value| below this counts as algebraically zero
ZERO_REL = 1e-12          # ... or below this fraction of the feature's own max
RANK_RCOND = 1e-10        # SVD tolerance, relative to the largest singular value


def load_all():
    man = json.load(open(os.path.join(FEAT, "manifest.json")))
    names = man["features"]
    data, fam = {}, {}
    for case, m in man["cases"].items():
        z = np.load(os.path.join(FEAT, f"{case}.npz"), allow_pickle=True)
        data[case] = z["F"].astype(np.float64)
        fam[case] = m["family"]
    return names, data, fam, man


def rank_of(X):
    """Numerical rank of the column-standardised feature matrix."""
    Xs = X - X.mean(0)
    sd = Xs.std(0); sd[sd < 1e-300] = 1.0
    Xs = Xs / sd
    s = np.linalg.svd(Xs, compute_uv=False)
    tol = RANK_RCOND * s[0] if s[0] > 0 else 0.0
    return int((s > tol).sum()), s


def main():
    names, data, fam, man = load_all()
    nF = len(names)
    families = sorted(set(fam.values()))
    out = {"n_features": nF, "families": families,
           "rank_rcond": RANK_RCOND, "zero_abs": ZERO_ABS,
           "zero_test": "absolute only: max|v| < 1e-12; see L-TBD-F2",
           "per_family": {}, "per_feature": {}, "coverage": {}}

    fam_X = {f: np.concatenate([data[c] for c in data if fam[c] == f]) for f in families}
    pooled = np.concatenate([data[c] for c in data])

    # ---- per-family rank and per-feature degeneracy
    for f in families + ["POOLED"]:
        X = pooled if f == "POOLED" else fam_X[f]
        r, s = rank_of(X)
        col_max = np.abs(X).max(0)
        # DEAD is an ABSOLUTE test only. A relative test against a global max
        # across features is meaningless here: the features are incommensurable
        # (the Pope invariants reach 1e14 while every normalised invariant is
        # bounded by ~1), so a global threshold of 1e-12*gmax = 150 would flag
        # every bounded feature as dead. See LESSONS_DRAFT.md L-TBD-F2.
        dead = [names[i] for i in range(nF) if col_max[i] < ZERO_ABS]
        near_const = [names[i] for i in range(nF)
                      if names[i] not in dead and X[:, i].std() < 1e-8 * max(col_max[i], 1e-30)]
        out["per_family"][f] = {
            "n_cells": int(X.shape[0]), "rank": r, "n_features": nF,
            "rank_deficiency": nF - r,
            "n_dead": len(dead), "dead_features": dead,
            "n_near_constant": len(near_const), "near_constant_features": near_const,
            "max_abs_by_feature": {names[i]: float(col_max[i]) for i in range(nF)},
            "singular_value_ratio_first_to_last": float(s[0] / max(s[-1], 1e-300)),
        }

    # ---- per-feature stats, pooled
    for i, n in enumerate(names):
        v = pooled[:, i]
        out["per_feature"][n] = {
            "mean": float(v.mean()), "std": float(v.std()),
            "min": float(v.min()), "max": float(v.max()),
            "p01": float(np.percentile(v, 1)), "p50": float(np.percentile(v, 50)),
            "p99": float(np.percentile(v, 99)),
            "frac_below_1e-12_abs": float((np.abs(v) < ZERO_ABS).mean()),
        }

    # ---- FS5 coverage: TEST cases against TRAINING cases
    tr_cases = [c for c in data if c not in TEST]
    te_cases = [c for c in data if c in TEST]
    Xtr = np.concatenate([data[c] for c in tr_cases])
    lo, hi = Xtr.min(0), Xtr.max(0)
    span = np.maximum(hi - lo, 1e-30)
    cov = {}
    for c in te_cases:
        X = data[c]
        outside = (X < lo) | (X > hi)
        # how far beyond, in units of the training span
        beyond = np.maximum((lo - X) / span, (X - hi) / span).max(0)
        cov[c] = {
            "n_cells": int(X.shape[0]),
            "frac_cells_any_feature_outside": float(outside.any(1).mean()),
            "mean_frac_features_outside_per_cell": float(outside.mean()),
            "features_with_any_outside": int((outside.any(0)).sum()),
            "worst_features": sorted(
                [(names[i], float(outside[:, i].mean()), float(beyond[i]))
                 for i in range(nF) if outside[:, i].any()],
                key=lambda t: -t[1])[:12],
        }
    out["coverage"] = {"train_cases": sorted(tr_cases), "test_cases": sorted(te_cases),
                       "per_test_case": cov}

    # ---- charter section 5(b): per-cell rank of Pope's ten-tensor basis.
    # Re-measured here because the figure "3.24, never above 5" is quoted in
    # three records from a pointer (Kaandorp2020_TBRF/train_log.json) that does
    # not resolve. This is the live source.
    DS = "/home/ubuntu/closure-data/tbnn/dataset.npz"
    if os.path.exists(DS):
        z = np.load(DS, allow_pickle=True)
        Tt, cid = z["T"], z["case_id"]
        cnames = [str(x) for x in z["names"]]
        rng = np.random.default_rng(0)
        br = {}
        for i, cn in enumerate(cnames):
            idx = np.where(cid == i)[0]
            if idx.size > 4000:
                idx = rng.choice(idx, 4000, replace=False)
            M = Tt[idx].reshape(len(idx), 10, 9).astype(np.float64)
            sv = np.linalg.svd(M, compute_uv=False)
            rk = (sv > 1e-8 * sv[:, :1]).sum(1)
            br[cn] = {"n_sampled": int(len(idx)), "mean_rank": float(rk.mean()),
                      "min_rank": int(rk.min()), "max_rank": int(rk.max()),
                      "hist": np.bincount(rk, minlength=11).tolist()}
        allr = np.array([v["mean_rank"] for v in br.values()])
        out["tensor_basis_rank"] = {
            "method": "numerical rank of the 10x9 flattened tensor stack per cell, "
                      "singular values above 1e-8*sigma_max; up to 4000 cells per case, seed 0",
            "per_case": br,
            "pooled_mean_of_case_means": float(allr.mean()),
            "min_case_mean": float(allr.min()), "max_case_mean": float(allr.max()),
            "max_rank_any_cell": int(max(v["max_rank"] for v in br.values())),
            "source_note": "live re-measurement; supersedes the unsourced 3.24 quoted in "
                           "Ling2016_TBNN/RESULTS.md, Wu2018_PIML_RF/RESULTS.md and "
                           "_common/FEASIBILITY.md (charter section 5(b) provenance defect)",
        }
        print(f"\ntensor-basis per-cell rank: case means {allr.min():.3f}-{allr.max():.3f}, "
              f"mean of case means {allr.mean():.3f}, max rank in any cell "
              f"{out['tensor_basis_rank']['max_rank_any_cell']}")

    json.dump(out, open(OUT_JSON, "w"), indent=1)

    print(f"{nF} features, families {families}")
    print(f"\n{'family':14s} {'cells':>8s} {'rank':>6s} {'deficit':>8s} {'dead':>6s} {'nearconst':>10s} {'s1/sN':>12s}")
    for f in families + ["POOLED"]:
        d = out["per_family"][f]
        print(f"{f:14s} {d['n_cells']:8d} {d['rank']:6d} {d['rank_deficiency']:8d} "
              f"{d['n_dead']:6d} {d['n_near_constant']:10d} {d['singular_value_ratio_first_to_last']:12.3e}")
    print("\nDEAD (algebraically zero) pooled:")
    for n in out["per_family"]["POOLED"]["dead_features"]:
        print(f"    {n}")
    print("\nFS5 coverage, TEST vs TRAINING range:")
    for c, d in cov.items():
        print(f"  {c:22s} cells outside on >=1 feature: {d['frac_cells_any_feature_outside']*100:6.2f}% "
              f" features ever outside: {d['features_with_any_outside']:3d}/{nF}")


if __name__ == "__main__":
    main()
