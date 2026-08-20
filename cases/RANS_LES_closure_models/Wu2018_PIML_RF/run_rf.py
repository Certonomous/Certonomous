#!/usr/bin/env python3
"""Wu, Xiao & Paterson (2018) physics-informed random forest, as a labelled
VARIANT. See PREREGISTRATION.md - written first.

E1: the benchmark split (comparable with the TBNN/TBRF siblings).
E2: hill-shape transfer - train on alpha_10 only, test on alpha_05 and alpha_15.
"""
from __future__ import annotations
import json, os, sys, time
import numpy as np
from sklearn.ensemble import RandomForestRegressor

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.join(os.path.dirname(HERE), "_common")
sys.path.insert(0, COMMON); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Ling2016_TBNN"))
from of_read import realisability_violation
from train_tbnn import TEST, VAL, GROUP_EXCLUDED, assert_disjoint, per_case_rms, frob_rms

DATA = "/home/ubuntu/closure-data/tbnn/dataset.npz"
FEXT = "/home/ubuntu/closure-data/tbnn/features_ext.npz"
OUT = "/home/ubuntu/closure-data/wu2018"
os.makedirs(OUT, exist_ok=True)
SYM = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]


def to6(b):
    return np.stack([b[:, i, j] for i, j in SYM], axis=1)


def from6(y):
    n = y.shape[0]
    b = np.zeros((n, 3, 3), np.float64)
    for c, (i, j) in enumerate(SYM):
        b[:, i, j] = y[:, c]; b[:, j, i] = y[:, c]
    return b


def main():
    t0 = time.time()
    z = np.load(DATA, allow_pickle=True)
    names = [str(x) for x in z["names"]]
    bL, bR, valid, cid = z["b_LES"], z["b_RANS"], z["valid"], z["case_id"]
    F = np.load(FEXT, allow_pickle=True)["F"]
    fnames = [str(x) for x in np.load(FEXT, allow_pickle=True)["feature_names"]]
    cid_of = {n: i for i, n in enumerate(names)}
    # additional finiteness mask: b_RANS is NaN where the converged k_RANS falls
    # below the anisotropy floor even though k_LES does not. Counted, not hidden.
    finite = np.isfinite(bL).all(axis=(1, 2)) & np.isfinite(bR).all(axis=(1, 2)) & np.isfinite(F).all(axis=1)
    n_dropped = int((valid & ~finite).sum())
    print(f"[mask] cells valid={int(valid.sum())} of {len(valid)}; "
          f"additionally dropped for non-finite b_RANS or features: {n_dropped}", flush=True)
    valid = valid & finite
    mask = lambda cs: np.isin(cid, [cid_of[c] for c in cs]) & valid

    split_of = {n: ("test" if n in TEST else "val" if n in VAL
                    else "excluded" if n in GROUP_EXCLUDED else "train") for n in names}
    lines = assert_disjoint([n for n in names if split_of[n] != "excluded"], split_of)
    for L in lines:
        print("[assert] " + L, flush=True)

    E1_train = [n for n in names if split_of[n] == "train"]
    E1_test = sorted(TEST)
    a10 = [n for n in names if n.startswith("alpha_10")]
    a05 = [n for n in names if n.startswith("alpha_05")]
    a15 = [n for n in names if n.startswith("alpha_15")]
    assert not (set(a10) & set(a05)) and not (set(a10) & set(a15)), "E2 leak"
    print(f"[assert] E2 train={len(a10)} alpha_10 hills; test={len(a05)} alpha_05 + {len(a15)} alpha_15; disjoint by construction", flush=True)

    out = {"n_dropped_nonfinite": n_dropped, "assert_lines": lines, "feature_names": fnames, "E1": {}, "E2": {}}
    dB = to6(bL - bR)

    for exp, trn, tst in (("E1", E1_train, E1_test), ("E2", a10, a05 + a15)):
        mtr, mte = mask(trn), mask(tst)
        # Mahalanobis of test features vs training distribution
        mu = F[mtr].mean(0); Cv = np.cov(F[mtr].T) + 1e-9 * np.eye(F.shape[1])
        Ci = np.linalg.inv(Cv)
        d = F[mte] - mu
        maha = np.sqrt(np.maximum(np.einsum("ni,ij,nj->n", d, Ci, d), 0))
        dtr = F[mtr] - mu
        mtr_maha = np.sqrt(np.maximum(np.einsum("ni,ij,nj->n", dtr, Ci, dtr), 0))
        p99 = float(np.percentile(mtr_maha, 99))
        out[exp]["mahalanobis"] = {"train_p99": p99,
                                   "test_median": float(np.median(maha)),
                                   "test_p99": float(np.percentile(maha, 99)),
                                   "frac_test_beyond_train_p99": float((maha > p99).mean())}
        for seed in range(5):
            rf = RandomForestRegressor(n_estimators=100, max_depth=20,
                                       min_samples_leaf=9, max_features="sqrt",
                                       random_state=seed, n_jobs=6)
            rf.fit(F[mtr], dB[mtr])
            pred_b = bR + from6(rf.predict(F))
            pc = per_case_rms(pred_b, bL, cid, names, mte)
            viol, _ = realisability_violation(pred_b[mte])
            tviol, _ = realisability_violation(bL[mte])
            out[exp][f"seed{seed}"] = {
                "per_case": pc,
                "overall_b_rms": frob_rms(pred_b[mte] - bL[mte]),
                "realisability_violation_frac": float(viol.mean()),
                "truth_violation_frac": float(tviol.mean()),
                "feature_importance": dict(zip(fnames, [round(float(v), 4) for v in rf.feature_importances_]))}
            print(f"[{exp} seed{seed}] b_rms={out[exp][f'seed{seed}']['overall_b_rms']:.4f} "
                  f"viol={viol.mean():.4f} (truth {tviol.mean():.4f})", flush=True)
    out["seconds"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "train_log.json"), "w"), indent=1)
    print("wrote train_log.json", flush=True)


if __name__ == "__main__":
    main()
