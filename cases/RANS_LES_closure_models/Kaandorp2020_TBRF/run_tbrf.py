#!/usr/bin/env python3
"""Run the TBRF reproduction. See PREREGISTRATION.md - written first.

Two feature sets (5 Pope invariants; 17 bounded markers), 3 seeds each,
100 trees, 21,000 training cells sampled at random - Kaandorp & Dwight's own
settings (VERIFIED-PDF: arXiv:1810.08794v2, Table 2 and p. 30).

Bounded: max_depth, min_leaf, per-forest wall-clock self-timeout, per-forest
pickle checkpoint so a restart resumes at the forest boundary.
"""
from __future__ import annotations
import json, os, pickle, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.join(os.path.dirname(HERE), "_common")
sys.path.insert(0, HERE); sys.path.insert(0, COMMON)
from tbrf import TensorBasisRandomForest
from of_read import realisability_violation
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Ling2016_TBNN"))
from train_tbnn import TEST, VAL, GROUP_EXCLUDED, assert_disjoint, per_case_rms, frob_rms

DATA = "/home/ubuntu/closure-data/tbnn/dataset.npz"
FEXT = "/home/ubuntu/closure-data/tbnn/features_ext.npz"
CKPT = "/home/ubuntu/closure-data/tbrf"
os.makedirs(CKPT, exist_ok=True)

N_TREES = 100
N_SAMPLE = 21000
MAX_DEPTH = 12
MIN_LEAF = 9
N_THRESH = 16
WALL_LIMIT_S = 3600 * 4


def main():
    t0 = time.time()
    z = np.load(DATA, allow_pickle=True)
    names = [str(x) for x in z["names"]]
    lam, T, bL, valid, cid = z["lam"], z["T"], z["b_LES"], z["valid"], z["case_id"]
    zf = np.load(FEXT, allow_pickle=True)
    assert [str(x) for x in zf["names"]] == names, "feature file case order mismatch"
    F17 = zf["F"]; fnames = [str(x) for x in zf["feature_names"]]

    split_of = {n: ("test" if n in TEST else "val" if n in VAL
                    else "excluded" if n in GROUP_EXCLUDED else "train") for n in names}
    lines = assert_disjoint([n for n in names if split_of[n] != "excluded"], split_of)
    for L in lines:
        print("[assert] " + L, flush=True)

    idx_of = {s: np.zeros(len(cid), bool) for s in ("train", "val", "test")}
    for i, n in enumerate(names):
        if split_of[n] in idx_of:
            idx_of[split_of[n]] |= (cid == i)
    for s in idx_of:
        idx_of[s] &= valid
    print({s: int(v.sum()) for s, v in idx_of.items()}, flush=True)

    tr = idx_of["train"]
    tsc = np.sqrt((T[tr] ** 2).sum(axis=(2, 3)).mean(axis=0)) + 1e-30
    Tn = (T / tsc[None, :, None, None]).astype(np.float32)

    # per-cell rank of the 10-tensor basis (Pope 1975 p.335: 3 in two dimensions)
    sub = np.random.default_rng(0).choice(np.where(tr)[0], 5000, replace=False)
    M = Tn[sub].reshape(len(sub), 10, 9).astype(np.float64)
    sv = np.linalg.svd(M, compute_uv=False)
    rank = (sv > 1e-8 * sv[:, :1]).sum(1)
    rank_hist = np.bincount(rank, minlength=11).tolist()
    print("[basis] per-cell rank of {T^(n)}: mean %.2f hist %s" % (rank.mean(), rank_hist), flush=True)

    out = {"assert_lines": lines, "basis_rank_mean": float(rank.mean()),
           "basis_rank_hist": rank_hist, "feature_names": fnames, "runs": {}}
    tr_idx_all = np.where(tr)[0]

    for tag, X in (("FS5", lam), ("FS17", F17)):
        mtry = 5 if tag == "FS5" else 11
        for seed in (0, 1, 2):
            key = f"{tag}_s{seed}"
            ck = os.path.join(CKPT, key + ".pkl")
            if os.path.exists(ck):
                forest = pickle.load(open(ck, "rb"))
                print(f"[resume] {key}: {len(forest.trees)} trees already", flush=True)
            else:
                forest = TensorBasisRandomForest(n_trees=N_TREES, seed=seed,
                                                 max_depth=MAX_DEPTH, min_leaf=MIN_LEAF,
                                                 mtry=mtry, n_thresh=N_THRESH)
            if len(forest.trees) < N_TREES:
                rng = np.random.default_rng(1000 + seed)
                sel = rng.choice(tr_idx_all, N_SAMPLE, replace=False)
                def ckpt(f, i):
                    if i % 10 == 0 or i == N_TREES:
                        pickle.dump(f, open(ck, "wb"))
                t1 = time.time()
                forest.fit(X[sel].astype(np.float64), Tn[sel], bL[sel],
                           verbose=False, checkpoint=ckpt)
                pickle.dump(forest, open(ck, "wb"))
                print(f"[fit] {key} {N_TREES} trees in {time.time()-t1:.0f}s", flush=True)
            pred = forest.predict(X.astype(np.float64), Tn)
            np.save(os.path.join(CKPT, f"pred_{key}.npy"), pred.astype(np.float32))
            pc = per_case_rms(pred, bL, cid, names, idx_of["test"])
            out["runs"][key] = {"per_case": pc,
                                "val_b_rms": frob_rms(pred[idx_of["val"]] - bL[idx_of["val"]]),
                                "train_b_rms": frob_rms(pred[tr] - bL[tr])}
            print(f"[done] {key} val={out['runs'][key]['val_b_rms']:.4f} test={pc}", flush=True)
            if time.time() - t0 > WALL_LIMIT_S:
                print("[self-timeout] stopping", flush=True)
                out["self_timeout"] = True
                break
    out["seconds"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(HERE, "train_log.json"), "w"), indent=1)
    print("wrote train_log.json", flush=True)


if __name__ == "__main__":
    main()
