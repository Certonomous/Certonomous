#!/usr/bin/env python3
"""Charter section 6 invariance check on the FS1 library.

Applies (a) a Galilean boost U -> U + c and (b) a rigid rotation Q to one stored
field, recomputes every feature AND every normaliser from the transformed raw
ingredients, and reports the max relative change per feature.

Invariant features must come back at ~1e-12. Anything that does not is reported
BY NAME - that is the deliverable, not a failure.
"""
from __future__ import annotations
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, COMMON)
from of_read import read_field, latest_time_dir, sym_to_full, structured_gradient
from wall_distance import wall_distance
import sst_baseline_metrics as SB
from build_features import (invariants_47, norm_bounded, antisym_from_vec,
                            BETA_STAR, CT_DURBIN, mm, tr)

CASE = "CBFS13700"
PATH = "/home/ubuntu/closure-challenge-benchmark/data/CBFS"
OUT = "/home/ubuntu/closure-data/features/invariance_check.json"


def features_from_raw(U, k, omega, nut, tau_R, A, gp, gk, dwall, nu):
    """Exactly the block A/B/C/D pipeline of build_features, from raw arrays."""
    S = 0.5 * (A + A.transpose(0, 2, 1)); W = 0.5 * (A - A.transpose(0, 2, 1))
    eps = BETA_STAR * np.maximum(k, 0.0) * np.maximum(omega, 1e-30)
    DUDt = np.einsum("nj,nij->ni", U, A)
    nS = np.sqrt((S ** 2).sum(axis=(1, 2))); nW = np.sqrt((W ** 2).sum(axis=(1, 2)))
    blocks, names = [], []
    for tag, Tinv in (("A", eps / np.maximum(k, 1e-30)),
                      ("B", 1.0 / np.maximum(np.maximum(
                          k / np.maximum(eps, 1e-30),
                          CT_DURBIN * np.sqrt(nu / np.maximum(eps, 1e-30))), 1e-30))):
        Sh = norm_bounded(S, Tinv); Wh = norm_bounded(W, nW)
        Ph = antisym_from_vec(norm_bounded(gp, np.linalg.norm(DUDt, axis=1)))
        Kh = antisym_from_vec(norm_bounded(gk, eps / np.sqrt(np.maximum(k, 1e-30))))
        inv, nm = invariants_47(Sh, Wh, Ph, Kh)
        blocks.append(inv); names += [f"{n}__{tag}" for n in nm]
    _b = lambda a, c: np.where(np.abs(a) + np.abs(c) > 1e-30,
                               a / np.maximum(np.abs(a) + np.abs(c), 1e-30), 0.0)
    q = {
        "q1_wallRe": np.minimum(np.sqrt(np.maximum(k, 0)) * dwall / (50.0 * nu), 2.0),
        "q2_turbIntensity": _b(k, 0.5 * (U ** 2).sum(1)),
        "q3_timeScaleRatio": _b(k / np.maximum(eps, 1e-30), 1.0 / np.maximum(nS, 1e-30)),
        "q4_pgradAlongStreamline": _b(np.einsum("ni,ni->n", U, gp),
                                      np.linalg.norm(gp, axis=1) * np.linalg.norm(U, axis=1)),
        "q5_excessRotation": _b(nW - nS, nW + nS),
        "q6_stressRatio": _b(np.sqrt((tau_R ** 2).sum(axis=(1, 2))), k),
        "q7_viscRatio": _b(nut, 100.0 * nu),
        "q8_kConvection": _b(np.einsum("ni,ni->n", U, gk),
                             np.abs(np.einsum("nij,nij->n", tau_R, S))),
        "q9_nonOrthogonality": _b(np.abs(np.einsum("ni,nj,nij->n", U, U, S)),
                                  (np.linalg.norm(U, axis=1) ** 2) * nS),
        "q10_streamlineCurv": _b(np.abs(np.einsum("ni,nij,nj->n", U, A, U)),
                                 (np.linalg.norm(U, axis=1) ** 2)
                                 * np.sqrt((A ** 2).sum(axis=(1, 2)))),
        "q11_turbReynolds": _b(np.sqrt(np.maximum(k, 0)) / np.maximum(nu * omega, 1e-30), 50.0),
    }
    blocks.append(np.stack(list(q.values()), axis=1)); names += list(q.keys())
    Tt = np.maximum(k / np.maximum(eps, 1e-30),
                    CT_DURBIN * np.sqrt(nu / np.maximum(eps, 1e-30)))[:, None, None]
    s, r = S * Tt, W * Tt; s2 = mm(s, s); r2 = mm(r, r)
    blocks.append(np.stack([tr(s2), tr(r2), tr(mm(s2, s)), tr(mm(r2, s)), tr(mm(r2, s2))], axis=1))
    names += ["lam1", "lam2", "lam3", "lam4", "lam5"]
    return np.concatenate(blocks, axis=1), names


def main():
    d = SB.load_case(CASE, PATH, "cbfs")
    t = latest_time_dir(PATH)
    C, U, k, nut = d["C"], d["U"], d["k"], d["nut"]
    omega = read_field(os.path.join(PATH, t, "omega"))
    p = read_field(os.path.join(PATH, t, "p"))
    nu = SB.case_meta(PATH).get("nu", 1e-5)
    A = structured_gradient(C, U)
    gp = structured_gradient(C, p); gk = structured_gradient(C, k)
    dwall, _ = wall_distance(PATH, C)
    tau_R = sym_to_full(d["tau_R"])
    F0, names = features_from_raw(U, k, omega, nut, tau_R, A, gp, gk, dwall, nu)

    res = {"case": CASE, "n_cells": int(C.shape[0]), "tests": {}}

    # (a) Galilean boost: U -> U + c. Gradients are unchanged by construction.
    c = np.array([0.37, -0.21, 0.13]) * float(np.linalg.norm(U, axis=1).mean())
    Fb, _ = features_from_raw(U + c, k, omega, nut, tau_R, A, gp, gk, dwall, nu)
    scale = np.maximum(np.abs(F0).max(axis=0), 1e-12)
    rel_b = np.abs(Fb - F0).max(axis=0) / scale
    res["tests"]["galilean_boost"] = {"c": c.tolist(),
                                      "max_rel_change": float(rel_b.max())}

    # (b) rigid rotation Q of the frame: vectors -> Q v, tensors -> Q T Q^T
    th = 0.7
    Q = np.array([[np.cos(th), -np.sin(th), 0], [np.sin(th), np.cos(th), 0], [0, 0, 1.0]])
    rv = lambda v: v @ Q.T
    rt = lambda T: np.einsum("ab,nbc,dc->nad", Q, T, Q)
    Fr, _ = features_from_raw(rv(U), k, omega, nut, rt(tau_R), rt(A), rv(gp), rv(gk), dwall, nu)
    rel_r = np.abs(Fr - F0).max(axis=0) / scale
    res["tests"]["rotation"] = {"angle_rad": th, "max_rel_change": float(rel_r.max())}

    TOL = 1e-12
    res["not_galilean_invariant"] = sorted(
        [names[i] for i in np.where(rel_b > TOL)[0]])
    res["not_rotation_invariant"] = sorted(
        [names[i] for i in np.where(rel_r > TOL)[0]])
    res["per_feature"] = {names[i]: {"galilean": float(rel_b[i]), "rotation": float(rel_r[i])}
                          for i in range(len(names))}
    res["tolerance"] = TOL
    json.dump(res, open(OUT, "w"), indent=1)

    print(f"case {CASE}, {res['n_cells']} cells, {len(names)} features, tol {TOL:g}")
    print(f"  Galilean boost c = {np.round(c,4).tolist()} : max rel change {rel_b.max():.3e}")
    print(f"  rotation {th} rad                          : max rel change {rel_r.max():.3e}")
    print(f"\nNOT Galilean invariant ({len(res['not_galilean_invariant'])}):")
    for n in res["not_galilean_invariant"]:
        print(f"    {n:34s} {res['per_feature'][n]['galilean']:.3e}")
    print(f"\nNOT rotation invariant ({len(res['not_rotation_invariant'])}):")
    for n in res["not_rotation_invariant"]:
        print(f"    {n:34s} {res['per_feature'][n]['rotation']:.3e}")


if __name__ == "__main__":
    main()
