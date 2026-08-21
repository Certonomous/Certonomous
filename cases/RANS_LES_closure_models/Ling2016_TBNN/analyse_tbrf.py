#!/usr/bin/env python3
"""Score the tensor-basis random-forest sibling comparator (secs. 7b, 7b-i of
RESULTS.md) on the TEST cases.

Recreated in the repository 2026-08-21 after the session scratchpad was cleared.
Behaviour unchanged; output path moved to /home/ubuntu/closure-data/.

Usage: /home/ubuntu/closure-venv/bin/python analyse_tbrf.py
"""
from __future__ import annotations
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.join(os.path.dirname(HERE), "_common")
sys.path.insert(0, COMMON); sys.path.insert(0, HERE)
from score_prediction import load, frob_rms
from of_read import realisability_violation
from train_tbnn import TEST

CK = "/home/ubuntu/closure-data/tbrf"
OUT = "/home/ubuntu/closure-data/tbrf_analysis.json"
BASELINE = "/home/ubuntu/closure-data/baseline_on_mask.json"

d = load()
names, cid, bL, valid = d["names"], d["cid"], d["b_LES"], d["valid"]
cid_of = {n: i for i, n in enumerate(names)}
tm = np.isin(cid, [cid_of[c] for c in TEST]) & valid
bl = json.load(open(BASELINE)) if os.path.exists(BASELINE) else {}

res = {}
for tag in ("FS5", "FS17"):
    per, viol = {}, {}
    for s in range(3):
        p = os.path.join(CK, f"pred_{tag}_s{s}.npy")
        if not os.path.exists(p):
            continue
        pr = np.load(p).astype(np.float64)
        for c in sorted(TEST):
            m = tm & (cid == cid_of[c])
            per.setdefault(c, []).append(frob_rms(pr[m] - bL[m]))
        vv, _ = realisability_violation(pr[tm])
        viol[s] = float(vv.mean())
    if per:
        res[tag] = dict(per_case={c: dict(mean=float(np.mean(v)), lo=float(min(v)),
                                          hi=float(max(v)), n=len(v))
                                  for c, v in per.items()}, viol=viol)

json.dump(res, open(OUT, "w"), indent=1)
for tag, v in res.items():
    print(f"== {tag}  viol={ {k: round(x,4) for k,x in v['viol'].items()} }")
    w = 0
    for c, x in v["per_case"].items():
        sst = bl.get(c, {}).get("sst")
        beat = (sst is not None and x["mean"] < sst)
        w += beat
        print(f"  {c:22s} mean={x['mean']:.4g} range=[{x['lo']:.4g},{x['hi']:.4g}] "
              f"n={x['n']}" + (f" SST={sst:.4f} {'Y' if beat else 'N'}" if sst else ""))
    print(f"  beats SST on {w} of {len(v['per_case'])}")
print(f"\nwrote {OUT}")
