#!/usr/bin/env python3
"""PART A.4 (OPTIONAL, registered before solving) -- five eigenspace re-solves on
one TRAINING hill, and the velocity-envelope coverage question.
Prediction P-A4, registered in advance: coverage < 0.50."""
from __future__ import annotations
import os, sys, json, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.dirname(HERE)
KDIR = "/home/ubuntu/Certonomous/cases/RANS_LES_closure_models/Kaandorp2020_TBRF/aposteriori"
sys.path.insert(0, HERE); sys.path.insert(0, COMMON); sys.path.insert(0, KDIR)
import eigenspace as E
from of_read import read_field, sym_to_full, anisotropy, structured_gradient
import sst_baseline_metrics as SB
from setup_case import build, CASES
import run_lane as RL

TAG = "alpha_10_9000_3036"
OUT = "/home/ubuntu/closure-data/uq_eigenspace"
DELTA_B = 1.0


def main():
    src, fam = CASES[TAG]
    d = SB.load_case(TAG, src, fam)
    A = np.asarray(d["gradU"]).reshape(-1, 3, 3).transpose(0, 2, 1)
    kref = float(np.mean(np.abs(d["k_LES"])))
    b_R, ok = anisotropy(sym_to_full(d["tau_R"]), d["k"], k_ref=kref)
    b_R = np.nan_to_num(b_R)
    states, labels = E.five_states(b_R, A, DELTA_B)
    res, Us = {}, []
    for st, lab in zip(states, labels):
        t0w = time.time()
        case, t0, nmask = build(TAG, f"EIG_{lab}", st, 5000, 5000)
        RL.patch_fvsolution(case)
        r = RL.run_solver(case)
        p = RL.parse_log(case)
        s = RL.score(TAG, case, int(t0) + 5000)
        res[lab] = dict(**r, **p, **s, n_kmask=nmask)
        tw = None
        for x in os.listdir(case):
            q = os.path.join(case, x)
            if os.path.isdir(q) and os.path.exists(os.path.join(q, "U")):
                try:
                    if float(x) > float(t0):
                        tw = x if tw is None or float(x) > float(tw) else tw
                except ValueError:
                    pass
        Us.append(read_field(os.path.join(case, tw, "U")) if tw else None)
        print(f"[A.4] {lab:10s} it={p['iterations']:6d} U_rms={s.get('U_rms')} "
              f"wall={r['wall_s']}s", flush=True)
        json.dump(res, open(os.path.join(OUT, "resolves.json"), "w"), indent=1)
    good = [u for u in Us if u is not None]
    if len(good) >= 2:
        U = np.stack(good)
        lo, hi = U.min(axis=0), U.max(axis=0)
        UL = d["U_LES"]
        inside = ((UL >= lo) & (UL <= hi))
        res["_envelope"] = dict(
            n_states=len(good),
            cover_all_components=float(inside.all(axis=1).mean()),
            cover_Ux=float(inside[:, 0].mean()), cover_Uy=float(inside[:, 1].mean()),
            width_rel=float(np.mean(np.linalg.norm(hi - lo, axis=1))
                            / np.mean(np.linalg.norm(UL, axis=1))))
        print(f"[A.4] velocity envelope coverage (all components) = "
              f"{res['_envelope']['cover_all_components']:.4f} -> P-A4 "
              f"{'PASS' if res['_envelope']['cover_all_components'] < 0.50 else 'FALSIFIED'}",
              flush=True)
    json.dump(res, open(os.path.join(OUT, "resolves.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
