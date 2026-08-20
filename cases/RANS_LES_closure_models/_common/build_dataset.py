#!/usr/bin/env python3
"""Assemble the Pope-basis dataset for every benchmark case, once, into
/home/ubuntu/closure-data/tbnn/dataset.npz  (OUTSIDE the repo).

Reads only. Writes one npz plus a provenance json.
"""
from __future__ import annotations
import os, sys, json, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sst_baseline_metrics as SB
import tensor_basis as TB

OUT = "/home/ubuntu/closure-data/tbnn"
os.makedirs(OUT, exist_ok=True)


def all_cases():
    cases = []
    for c, p in sorted(SB.PH_ALPHA.items()):
        cases.append((c, p, "hill"))
    for c, p in sorted(SB.DUCTS.items()):
        cases.append((c, p, "duct"))
    for c, sub in (("PHLL10595", "PH_Breuer"), ("CBFS13700", "CBFS"),
                   ("NASA_2DWMH", "NASA_2DWMH")):
        p = os.path.join(SB.DATA, sub)
        if os.path.isdir(os.path.join(p, c)):
            p = os.path.join(p, c)
        if os.path.isdir(p):
            cases.append((c, p, "hill" if c != "NASA_2DWMH" else "hump"))
    return cases


def main():
    t0 = time.time()
    lam, T, bL, bR, valid, cid, names, fams, splits, npts = [], [], [], [], [], [], [], [], [], []
    for i, (c, p, fam) in enumerate(all_cases()):
        d = TB.case_arrays(c, p, fam)
        lam.append(d["lam"].astype(np.float32))
        T.append(d["T"].astype(np.float32))
        bL.append(d["b_LES"].astype(np.float32))
        bR.append(d["b_RANS"].astype(np.float32))
        valid.append(d["valid"])
        cid.append(np.full(d["n"], i, np.int32))
        names.append(c); fams.append(fam); splits.append(d["split"]); npts.append(d["n"])
        print(f"[ok] {c:24s} n={d['n']:6d} split={d['split']:5s} valid={int(d['valid'].sum()):6d}", flush=True)
    np.savez_compressed(os.path.join(OUT, "dataset.npz"),
                        lam=np.concatenate(lam), T=np.concatenate(T),
                        b_LES=np.concatenate(bL), b_RANS=np.concatenate(bR),
                        valid=np.concatenate(valid), case_id=np.concatenate(cid),
                        names=np.array(names), families=np.array(fams),
                        splits=np.array(splits), ncells=np.array(npts))
    prov = dict(benchmark="/home/ubuntu/closure-challenge-benchmark",
                commit="deb91557184af3cb95f5190494ec52d8f2c6a0d1",
                source_url="https://github.com/rmcconke/closure-challenge-benchmark.git",
                beta_star=TB.BETA_STAR, CT_durbin=TB.CT_DURBIN,
                n_cases=len(names), n_cells=int(sum(npts)),
                seconds=round(time.time() - t0, 1))
    json.dump(prov, open(os.path.join(OUT, "provenance.json"), "w"), indent=1)
    print(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
