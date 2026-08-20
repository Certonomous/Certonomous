#!/usr/bin/env python3
"""Score a predicted anisotropy field against the benchmark truth, with every
check the Phase-3 charter requires: per-case b_rms, the SST baseline on the same
cells, realisability of the prediction beside the truth's own violation rate, and
a Mahalanobis extrapolation statistic.

Usage (as a library):  from score_prediction import score
"""
from __future__ import annotations
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from of_read import realisability_violation

DATA = "/home/ubuntu/closure-data/tbnn/dataset.npz"
FEXT = "/home/ubuntu/closure-data/tbnn/features_ext.npz"


def load():
    """Two cell masks, deliberately named apart because they differ by 567 cells.

    `valid_les_only` -- k_LES above the anisotropy floor, so b_LES is defined.
        This is what a model that never touches b_RANS can train and be scored on
        (e.g. the TBNN, which regresses b_LES from RANS-side inputs only).
    `valid` -- the same, AND b_RANS finite. b_RANS = tau_RANS/(2 k_RANS) - I/3 is
        undefined where the converged RANS k underflows even though k_LES does
        not. Required by anything that compares against, or corrects, b_RANS.

    All 567 cells separating the two are non-finite b_RANS; the extended features
    and b_LES contribute none. Quote the mask name, never just the count.
    """
    z = np.load(DATA, allow_pickle=True)
    names = [str(x) for x in z["names"]]
    F = np.load(FEXT, allow_pickle=True)["F"]
    valid_les_only = z["valid"]
    finite = (np.isfinite(z["b_LES"]).all(axis=(1, 2))
              & np.isfinite(z["b_RANS"]).all(axis=(1, 2)) & np.isfinite(F).all(axis=1))
    return dict(names=names, lam=z["lam"], T=z["T"], b_LES=z["b_LES"],
                b_RANS=z["b_RANS"], valid=valid_les_only & finite,
                valid_les_only=valid_les_only, cid=z["case_id"], F=F)


def frob_rms(x):
    return float(np.sqrt((x ** 2).sum(axis=(1, 2)).mean()))


def score(pred, d, test_mask, train_mask, feats=None):
    """pred: (N,3,3) over ALL cells. Returns a dict of everything reportable."""
    names, cid, bL, bR = d["names"], d["cid"], d["b_LES"], d["b_RANS"]
    per = {}
    for i, nm in enumerate(names):
        m = test_mask & (cid == i)
        if m.sum() == 0:
            continue
        pv, _ = realisability_violation(pred[m])
        tv, _ = realisability_violation(bL[m])
        rv, _ = realisability_violation(bR[m])
        per[nm] = dict(
            n=int(m.sum()),
            model=frob_rms(pred[m] - bL[m]),
            sst=frob_rms(bR[m] - bL[m]),
            zero=frob_rms(bL[m]),
            viol_model=float(pv.mean()), viol_truth=float(tv.mean()),
            viol_sst=float(rv.mean()))
    X = d["F"] if feats is None else feats
    mu = X[train_mask].mean(0)
    C = np.cov(X[train_mask].T) + 1e-9 * np.eye(X.shape[1])
    Ci = np.linalg.inv(C)
    md = lambda m: np.sqrt(np.maximum(np.einsum("ni,ij,nj->n", X[m] - mu, Ci, X[m] - mu), 0))
    tr_d = md(train_mask)
    p99 = float(np.percentile(tr_d, 99))
    maha = {}
    for i, nm in enumerate(names):
        m = test_mask & (cid == i)
        if m.sum() == 0:
            continue
        v = md(m)
        maha[nm] = dict(median=float(np.median(v)),
                        frac_beyond_train_p99=float((v > p99).mean()))
    return dict(per_case=per, train_p99_mahalanobis=p99, mahalanobis=maha,
                overall=dict(model=frob_rms(pred[test_mask] - bL[test_mask]),
                             sst=frob_rms(bR[test_mask] - bL[test_mask]),
                             zero=frob_rms(bL[test_mask])))
