#!/usr/bin/env python3
"""Score the TBNN and the plain-MLP control on the TEST cases, and compute the
pre-registered Mahalanobis extrapolation statistic.

Recreated in the repository 2026-08-21: this lived in the session scratchpad,
which was cleared by an unrelated workstream. Behaviour is unchanged; only the
output path moved (scratchpad -> /home/ubuntu/closure-data/), which is why the
numbers it prints reproduce those already in RESULTS.md.

Usage: /home/ubuntu/closure-venv/bin/python analyse_tbnn.py
"""
from __future__ import annotations
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.join(os.path.dirname(HERE), "_common")
sys.path.insert(0, COMMON); sys.path.insert(0, HERE)
from score_prediction import load, frob_rms
from of_read import realisability_violation
from train_tbnn import TEST, VAL, GROUP_EXCLUDED

CK = "/home/ubuntu/closure-data/tbnn/ckpt"
CK_MLP_ONLY = "/home/ubuntu/closure-data/tbnn/ckpt_mlponly"
OUT = "/home/ubuntu/closure-data/tbnn_analysis.json"
BASELINE = "/home/ubuntu/closure-data/baseline_on_mask.json"

d = load()
names, cid, bL, valid, lam = d["names"], d["cid"], d["b_LES"], d["valid"], d["lam"]
cid_of = {n: i for i, n in enumerate(names)}
tm = np.isin(cid, [cid_of[c] for c in TEST]) & valid
held = set(TEST) | set(VAL) | set(GROUP_EXCLUDED)
trm = np.isin(cid, [cid_of[c] for c in names if c not in held]) & valid

# Mahalanobis on the five invariants AS FED to the network (signed-log scaled)
lam_s = np.sign(lam) * np.log1p(np.abs(lam))
mu = lam_s[trm].mean(0)
Ci = np.linalg.inv(np.cov(lam_s[trm].T) + 1e-9 * np.eye(lam_s.shape[1]))
md = lambda m: np.sqrt(np.maximum(
    np.einsum("ni,ij,nj->n", lam_s[m] - mu, Ci, lam_s[m] - mu), 0))
p99 = float(np.percentile(md(trm), 99))

out = {"train_p99_maha": p99, "maha": {}, "models": {}}
for c in sorted(TEST):
    v = md(tm & (cid == cid_of[c]))
    out["maha"][c] = dict(median=float(np.median(v)), p99=float(np.percentile(v, 99)),
                          frac_beyond=float((v > p99).mean()))

for tag, ckdir, nseed in (("TBNN", CK, 5), ("MLP", CK, 5), ("MLP_isolated", CK_MLP_ONLY, 3)):
    base = tag.split("_")[0]
    per, viol, pooled = {}, {}, {}
    for s in range(nseed):
        p = os.path.join(ckdir, f"pred_{base}_s{s}.npy")
        if not os.path.exists(p):
            continue
        pr = np.load(p).astype(np.float64)
        for c in sorted(TEST):
            m = tm & (cid == cid_of[c])
            per.setdefault(c, []).append(frob_rms(pr[m] - bL[m]))
        vv, _ = realisability_violation(pr[tm])
        viol[s] = float(vv.mean()); pooled[s] = frob_rms(pr[tm] - bL[tm])
    if per:
        out["models"][tag] = dict(
            per_case={c: dict(mean=float(np.mean(v)), lo=float(min(v)),
                              hi=float(max(v)), n=len(v)) for c, v in per.items()},
            viol=viol, pooled=pooled)

json.dump(out, open(OUT, "w"), indent=1)
bl = json.load(open(BASELINE)) if os.path.exists(BASELINE) else {}
print(f"train Mahalanobis p99 = {p99:.3f}")
for c, v in out["maha"].items():
    print(f"  {c:22s} median={v['median']:.3f} p99={v['p99']:.4g} beyond={v['frac_beyond']*100:.2f}%")
for tag, m in out["models"].items():
    print(f"\n== {tag}  viol={ {k: round(x,4) for k,x in m['viol'].items()} }")
    for c, v in m["per_case"].items():
        s = f"  {c:22s} mean={v['mean']:.4g} range=[{v['lo']:.4g},{v['hi']:.4g}] n={v['n']}"
        if c in bl:
            s += f"  SST={bl[c]['sst']:.4f} zero={bl[c]['zero']:.4f}"
        print(s)
print(f"\nwrote {OUT}")
