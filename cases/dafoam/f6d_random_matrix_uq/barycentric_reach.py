"""
F6d -- how far do the random-matrix samples actually travel in the barycentric
triangle, compared with the eigenspace corners?

This is the diagnostic that explains any width difference between the two
bands, and it costs no CFD: it is computed directly on the sampled Reynolds
stress fields, before propagation.

Metric: the barycentric-plane distance from the baseline state, in the
equilateral triangle with vertices
    1C = (1, 0),  2C = (0, 0),  3C = (0.5, sqrt(3)/2)
(the standard mapping used by Emory/Iaccarino and reproduced in the paper's
own Fig. 1).  The corner perturbation moves every cell to a vertex by
construction; the random-matrix draw moves it by a distance the dispersion
parameter delta controls.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CASE = HERE.parent / "f6b_periodic_hills" / "case_breuer_re10595"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(CASE))
import rmt_sampler as rmt   # noqa: E402
import foam_io as fio       # noqa: E402

V1C = np.array([1.0, 0.0])
V2C = np.array([0.0, 0.0])
V3C = np.array([0.5, np.sqrt(3) / 2])


def to_plane(C):
    return C[:, 0:1] * V1C + C[:, 1:2] * V2C + C[:, 2:3] * V3C


def main(n_draws=200):
    R_bar = rmt.read_symmtensor_internal(CASE / "10000" / "turbulenceProperties:R")
    k_bar, C_bar = rmt.barycentric(R_bar)
    P_bar = to_plane(C_bar)

    Cx = fio.read_internal_field(str(CASE / "0" / "Cx"))
    Cy = fio.read_internal_field(str(CASE / "0" / "Cy"))
    xy = np.column_stack([Cx, Cy])

    kl = rmt.build_kl_basis()
    P = rmt.build_interp_operator(kl, xy)
    L_R, _ = rmt.cholesky_upper_field(R_bar)

    # weight by cell turbulent kinetic energy so the statistic is not dominated
    # by the near-quiescent core; report both weighted and unweighted.
    out = {"n_cells": int(R_bar.shape[0]), "n_draws": n_draws}

    # corner reference: distance from baseline to each vertex
    for name, V in (("oneC", V1C), ("twoC", V2C), ("threeC", V3C)):
        d = np.linalg.norm(P_bar - V, axis=1)
        out[f"corner_{name}_bary_distance"] = {
            "mean": float(d.mean()), "median": float(np.median(d)),
            "p95": float(np.percentile(d, 95)),
            "k_weighted_mean": float((d * k_bar).sum() / k_bar.sum()),
        }

    for delta in (0.2, 0.6):
        s = rmt.RandomMatrixSampler(delta, kl, seed=99)
        acc, accw = [], []
        kmag = []
        for _ in range(n_draws):
            G = rmt.interp_G(P, s.sample_G_field())
            G = 0.5 * (G + np.transpose(G, (0, 2, 1)))
            R = rmt.assemble_R(L_R, G)
            k_s, C_s = rmt.barycentric(R)
            d = np.linalg.norm(to_plane(C_s) - P_bar, axis=1)
            acc.append(d)
            accw.append(float((d * k_bar).sum() / k_bar.sum()))
            kmag.append(float(np.abs(np.log(np.maximum(k_s, 1e-30) /
                                            np.maximum(k_bar, 1e-30))).mean()))
        acc = np.concatenate(acc)
        out[f"rmt_delta{delta}_bary_distance"] = {
            "mean": float(acc.mean()), "median": float(np.median(acc)),
            "p95": float(np.percentile(acc, 95)), "max": float(acc.max()),
            "k_weighted_mean": float(np.mean(accw)),
            "mean_abs_log_k_ratio": float(np.mean(kmag)),
        }
    print(json.dumps(out, indent=2))
    (HERE / "barycentric_reach.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
