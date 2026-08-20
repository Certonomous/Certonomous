#!/usr/bin/env python3
"""Per-case SST and b=0 baselines on the SAME cell mask a reproduction used.

The numbers in BASELINES.md use the k_LES anisotropy floor only; the Phase-3
reproductions additionally drop cells where b_RANS or a feature is non-finite.
Comparing a model to BASELINES.md across a different mask would be a small but
real apples-to-oranges error, so every RESULTS.md quotes both.
"""
from __future__ import annotations
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from score_prediction import load, frob_rms
from of_read import realisability_violation
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "Ling2016_TBNN"))
from train_tbnn import TEST, VAL, GROUP_EXCLUDED

d = load()
names, cid, bL, bR, valid = d["names"], d["cid"], d["b_LES"], d["b_RANS"], d["valid"]
cid_of = {n: i for i, n in enumerate(names)}
out = {}
for nm in names:
    m = valid & (cid == cid_of[nm])
    if m.sum() == 0:
        continue
    tv, _ = realisability_violation(bL[m]); rv, _ = realisability_violation(bR[m])
    out[nm] = dict(n=int(m.sum()), sst=frob_rms(bR[m] - bL[m]), zero=frob_rms(bL[m]),
                   viol_truth=float(tv.mean()), viol_sst=float(rv.mean()))
tm = np.isin(cid, [cid_of[c] for c in TEST]) & valid
out["_pooled_TEST"] = dict(n=int(tm.sum()), sst=frob_rms(bR[tm] - bL[tm]), zero=frob_rms(bL[tm]))
json.dump(out, open("/home/ubuntu/closure-data/baseline_on_mask.json", "w"), indent=1)
for k in sorted(TEST) + ["_pooled_TEST"]:
    v = out[k]; print(f"{k:24s} n={v['n']:6d} SST b_rms={v['sst']:.4f} zero={v['zero']:.4f}")
