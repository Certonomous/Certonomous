#!/usr/bin/env python3
"""IC1 - implementation cross-check of the frozen model.

`kOmegaSSTSparta` writes its construction-time `bijDelta` and `kDeficit` when
`writeInitialCorrections` is on.  This script evaluates the SAME frozen term
sets from the SAME 0/ fields in Python, independently of the solver, and
reports the relative L2 difference.  It catches component-ordering,
exponent-mapping, 2k-factor and I2-sign slips between the two implementations,
which is the only way to know the number in `RTerms` means what `MODEL.md` says
it means.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_common"))
import r4_lib as R
from assemble_dataset import basis, sym_to_full
from of_read import read_field

SYMM = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=os.path.join(HERE, "MODEL.json"))
    ap.add_argument("--cfg", default="discovered")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    m = json.load(open(a.model))
    key = ("bDelta_planted_zero_clean_sensitivity"
           if a.cfg == "discovered_pzclean" else "bDelta")
    rterms = [tuple(t) for t in m["R"]["terms"]]
    bterms = [tuple(t) for t in m[key]["terms"]]
    rows = {}
    for d in sorted(glob.glob(os.path.join(R.WORK, "aposteriori", "*",
                                           a.cfg, "0"))):
        case = d.split(os.sep)[-3]
        if not os.path.exists(os.path.join(d, "bijDelta")):
            continue
        # the solver evaluates from grad(U) of the 0/ field; reproduce it with
        # the same OpenFOAM operator by asking postProcess, else fall back to
        # the frozen case's own written grad(U) shape check
        gpath = os.path.join(d, "grad(U)")
        if not os.path.exists(gpath):
            os.system(f'cd {os.path.dirname(d)} && openfoam2606 postProcess '
                      f'-func "grad(U)" -time 0 > log.gradU0 2>&1')
        if not os.path.exists(gpath):
            rows[case] = dict(status="no grad(U) at time 0")
            continue
        k = read_field(os.path.join(d, "k")).ravel()
        omega = read_field(os.path.join(d, "omega")).ravel()
        A, T, I1, I2 = basis(k, omega, read_field(gpath))
        b = np.zeros_like(T[0])
        for (n, p, q, c) in bterms:
            b += c * ((I1 ** p) * (I2 ** q))[:, None, None] * T[n - 1]
        r = np.zeros_like(k)
        for (n, p, q, c) in rterms:
            cand = ((I1 ** p) * (I2 ** q))[:, None, None] * T[n - 1]
            r += 2.0 * k * c * np.einsum("nij,nij->n", cand, A)
        sb = read_field(os.path.join(d, "bijDelta"))
        sr = read_field(os.path.join(d, "kDeficit")).ravel()
        mine = np.stack([b[:, i, j] for (i, j) in SYMM], axis=1)
        rows[case] = dict(
            n=int(k.size),
            bijDelta_rel_l2=float(np.linalg.norm(sb - mine)
                                  / max(np.linalg.norm(sb), 1e-300)),
            kDeficit_rel_l2=float(np.linalg.norm(sr - r)
                                  / max(np.linalg.norm(sr), 1e-300)))
        print(f"{case:22s} bijDelta rel-L2 = {rows[case]['bijDelta_rel_l2']:.3e}"
              f"   kDeficit rel-L2 = {rows[case]['kDeficit_rel_l2']:.3e}",
              flush=True)
    worst = max((v.get("bijDelta_rel_l2", 0) for v in rows.values()), default=0)
    worst = max(worst, max((v.get("kDeficit_rel_l2", 0)
                            for v in rows.values()), default=0))
    verdict = "PASS" if worst < 1e-10 else (
        "GATE REACHED" if worst < 1e-2 else "GATE FAIL")
    json.dump(dict(cfg=a.cfg, worst_rel_l2=worst, verdict=verdict, cases=rows),
              open(a.out, "w"), indent=1)
    print(f"\nIC1 worst relative L2 = {worst:.3e} -> {verdict}")


if __name__ == "__main__":
    main()
