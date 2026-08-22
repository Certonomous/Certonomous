#!/usr/bin/env python3
"""R4 - the a-priori gate of PREREGISTRATION sec. 6.

  "The discovered b^Delta must beat the TRAIN-MEAN tensor on training-family
   b_rms.  The train-mean constant beats k-omega SST on 8 of 8 held-out cases
   (BASELINES.md sec. 6.4), so SST is not the bar and is not quoted as one.
   Registered: PASS requires the discovered model below train-mean b_rms on
   >= 3 of the 4 training families."

Everything is measured on the frozen-extraction fields, where the identity
  b_data = b_lin + b^Delta,      b_lin = -(nu_t/k) S      (Schmelzer Eq. 3)
holds exactly, so the model's total anisotropy is b_lin + b^Delta_model and the
truth it is scored against is b_data.  b_rms is the Frobenius convention of
`_common/score_prediction.frob_rms`: sqrt(mean_cells ||pred - truth||_F^2).

The linear-EVM column (b^Delta = 0) is REPORTED for context and is NOT the bar.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r4_lib as R

DS = os.path.join(R.WORK, "dataset")
FAMILIES = ["hills", "ducts", "PHLL10595", "CBFS13700"]


def frob_rms(x):
    return float(np.sqrt((x ** 2).sum(axis=(1, 2)).mean()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    cases = a.cases.split(",")
    R.assert_no_test_case(cases)
    model = json.load(open(a.model))
    man = json.load(open(os.path.join(DS, "dataset_manifest.json")))
    names = man["candidates"]

    # CLAUDE.md standing rule 3 - reader control before any number is quoted
    import sys as _s
    _s.path.insert(0, os.path.join(os.path.dirname(HERE), "_common"))
    from of_read import read_field as _rf
    fz = os.path.join(R.WORK, "frozen", cases[0])
    pz_reader = R.planted_zero_reader_check(
        os.path.join(fz, R.latest_time(fz), "bijDelta"), _rf,
        os.path.join(R.WORK, "_plant", "bijDelta"))

    per_case, fam_cells = {}, {f: [] for f in FAMILIES}
    for case in cases:
        z = np.load(os.path.join(DS, f"{case}.npz"))
        ok = z["k_les_raw"] > 0
        CT, bData, b_lin = z["CT"][:, ok], z["bData"][ok], z["b_lin"][ok]
        bmod = np.zeros_like(bData)
        for nm, (_, _, _, c) in zip(model["bDelta"]["names"],
                                    model["bDelta"]["terms"]):
            bmod += c * CT[names.index(nm)]
        per_case[case] = dict(family=man["cases"][case]["family"],
                              n=int(ok.sum()))
        fam_cells[man["cases"][case]["family"]].append(
            (bData, b_lin, bmod))

    # the train-mean tensor, computed on THIS lane's fitted cells
    allb = np.concatenate([b for f in FAMILIES for (b, _, _) in fam_cells[f]])
    bmean_lane = allb.mean(axis=0)
    shipped = json.load(open(os.path.join(
        os.path.dirname(HERE), "_common", "trainmean_baseline.json")))
    bmean_shipped = np.array(shipped["b_mean"])

    rows, wins = {}, 0
    for f in FAMILIES:
        bD = np.concatenate([x[0] for x in fam_cells[f]])
        bL = np.concatenate([x[1] for x in fam_cells[f]])
        bM = np.concatenate([x[2] for x in fam_cells[f]])
        r = dict(
            n_cells=int(bD.shape[0]),
            discovered=frob_rms(bL + bM - bD),
            train_mean_lane=frob_rms(np.broadcast_to(bmean_lane, bD.shape) - bD),
            train_mean_shipped=frob_rms(
                np.broadcast_to(bmean_shipped, bD.shape) - bD),
            linear_evm_reported_not_the_bar=frob_rms(bL - bD),
            zero=frob_rms(bD))
        r["beats_train_mean_lane"] = r["discovered"] < r["train_mean_lane"]
        r["beats_train_mean_shipped"] = (r["discovered"]
                                         < r["train_mean_shipped"])
        wins += int(r["beats_train_mean_lane"])
        rows[f] = r
    verdict = "PASS" if wins >= 3 else "GATE FAIL"
    out = dict(gate="PREREGISTRATION sec. 6 a-priori: discovered b^Delta below "
                    "train-mean b_rms on >= 3 of 4 training families",
               families_beaten=wins, n_families=len(FAMILIES),
               verdict=verdict, per_family=rows,
               train_mean_lane=bmean_lane.tolist(),
               train_mean_shipped=bmean_shipped.tolist(),
               train_mean_shipped_source="_common/trainmean_baseline.json "
                                         "(BASELINES.md sec. 6.4)",
               cases=cases, planted_zero_reader_control=pz_reader)
    json.dump(out, open(a.out, "w"), indent=1)
    print(f"{'family':12s} {'discovered':>12s} {'train-mean':>12s} "
          f"{'(shipped)':>12s} {'linear-EVM':>12s} {'b=0':>10s}  beats?")
    for f in FAMILIES:
        r = rows[f]
        print(f"{f:12s} {r['discovered']:12.6f} {r['train_mean_lane']:12.6f} "
              f"{r['train_mean_shipped']:12.6f} "
              f"{r['linear_evm_reported_not_the_bar']:12.6f} {r['zero']:10.6f}"
              f"  {'YES' if r['beats_train_mean_lane'] else 'no'}")
    print(f"\nA-PRIORI GATE: {wins}/4 families -> {verdict}")


if __name__ == "__main__":
    main()
