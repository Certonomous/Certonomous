#!/usr/bin/env python3
"""SpaRTA model discovery (Schmelzer, Dwight & Cinnella 2020, Sections 3.1-3.3)
on the k-corrective-frozen-RANS fields extracted by the previous rung.

Implements, per the paper:
  - the 2-D basis (Eqs. 10-11): T1 = S, T2 = S.W - W.S, T3 = S.S - I/3 tr(S.S),
    I1 = S_mn S_nm, I2 = W_mn W_nm (<= 0), with S, W nondimensionalised by
    tau = 1/omega and the velocity-gradient convention A_ij = d_j U_i taken
    literally from the paper's Section 2.2;
  - the 16-entry monomial vector B (Eq. 13) -> 48 tensorial candidates for
    b_Delta (Eq. 14) and 48 scalar candidates for R (Eq. 15, with the 2k
    factor of Eq. 12 carried in the candidate so the inferred coefficients
    are directly comparable to the paper's Eqs. 22-24);
  - the |value| > 1e5 candidate-discard rule;
  - model selection: elastic net (Eq. 17) via cyclic coordinate descent on
    the Gram matrix, over rho (Eq. 18) and 100 log-spaced lambdas down to
    1e-3 lambda_max with lambda_max = max|C^T Delta|/(K rho) (Eq. 19),
    candidates standardised to unit RMS (uncentred; no intercept exists in
    the physical model), warm-started along the descending lambda path;
  - model inference: Ridge regression (Eq. 20) on the raw (unstandardised)
    candidates for each unique abstract model form, at lambda_r in the
    paper's stated range 0.01 < lambda_r < 0.1.

Conventions pre-registered in W2_SPARTA_REGRESSION_PREREGISTRATION.md.

Usage:
  sparta_regression.py discover --case-dir <frozen-case> --time <t> \
      --out <json> [--stacking 9|6]
  sparta_regression.py evalmodel --case-dir <frozen-case> --time <t> \
      --rterms "1:0:0:0.93" --bterms "" \
      [--check-kdeficit <file> --check-bijdelta <file>]
"""

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sparta_frozen_score import read_of_field  # noqa: E402

# Eq. 13: exponent pairs (p, q) meaning I1^p * I2^q, in the paper's order
B_EXPONENTS = [
    (0, 0), (1, 0), (0, 1), (2, 0), (0, 2), (2, 3), (4, 2), (1, 2),
    (1, 3), (1, 4), (3, 1), (2, 4), (2, 1), (1, 1), (3, 2), (2, 2),
]
DISCARD_MAG = 1.0e5
RHO_GRID = [0.01, 0.1, 0.2, 0.5, 0.7, 0.9, 0.95, 0.99, 1.0]  # Eq. 18
N_LAMBDA = 100
XI = 1.0e-3
LAMBDA_R = [0.01, 0.0316227766, 0.1]  # endpoints + geometric mid (primary)
# OpenFOAM symmTensor component order and the tensor positions they map to
SYMM_IDX = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]


def monomial_name(p, q, tname):
    parts = []
    if p:
        parts.append("I1" if p == 1 else f"I1^{p}")
    if q:
        parts.append("I2" if q == 1 else f"I2^{q}")
    parts.append(tname)
    return "*".join(parts)


def load_frozen(case_dir, tdir):
    d = Path(case_dir) / str(tdir)
    U = read_of_field(d / "U")
    k = read_of_field(d / "k")[:, 0]
    omega = read_of_field(d / "omega")[:, 0]
    gradU = read_of_field(d / "grad(U)")          # 9 comps, (gradU)_ij = d_i U_j
    kDef = read_of_field(d / "kDeficit")[:, 0]
    bDel = read_of_field(d / "bijDelta")          # 6 comps
    return U, k, omega, gradU, kDef, bDel


def symm_to_full(b6):
    """(N,6) OpenFOAM symmTensor -> (N,3,3)."""
    n = b6.shape[0]
    out = np.empty((n, 3, 3))
    for c, (i, j) in enumerate(SYMM_IDX):
        out[:, i, j] = b6[:, c]
        out[:, j, i] = b6[:, c]
    return out


def full_to_symm(t):
    """(N,3,3) -> (N,6) OpenFOAM order."""
    return np.stack([t[:, i, j] for (i, j) in SYMM_IDX], axis=1)


def build_basis(k, omega, gradU9):
    """Return A (d_j U_i), T[3] (N,3,3), I1, I2 per the declared conventions."""
    gof = gradU9.reshape(-1, 3, 3)      # (gof)_ij = d_i U_j (OpenFOAM grad)
    A = np.transpose(gof, (0, 2, 1))    # A_ij = d_j U_i (paper Section 2.2)
    tau = 1.0 / omega
    S = 0.5 * tau[:, None, None] * (A + np.transpose(A, (0, 2, 1)))
    W = 0.5 * tau[:, None, None] * (A - np.transpose(A, (0, 2, 1)))
    I1 = np.einsum("nij,nji->n", S, S)
    I2 = np.einsum("nij,nji->n", W, W)  # <= 0
    T1 = S
    T2 = np.einsum("nik,nkj->nij", S, W) - np.einsum("nik,nkj->nij", W, S)
    SS = np.einsum("nik,nkj->nij", S, S)
    T3 = SS - (np.trace(SS, axis1=1, axis2=2) / 3.0)[:, None, None] \
        * np.eye(3)[None, :, :]
    return A, [T1, T2, T3], I1, I2


def build_libraries(k, omega, gradU9):
    """Return (names, tensor candidates (M,N,3,3), R candidates (M,N))."""
    A, T, I1, I2 = build_basis(k, omega, gradU9)
    names, tens, rcols = [], [], []
    for n, Tn in enumerate(T, start=1):
        for (p, q) in B_EXPONENTS:
            mono = (I1 ** p) * (I2 ** q)
            cand = mono[:, None, None] * Tn
            names.append(monomial_name(p, q, f"T{n}"))
            tens.append(cand)
            # Eq. 12/15 with the 2k factor carried in the candidate
            rcols.append(2.0 * k * np.einsum("nij,nij->n", cand, A))
    return names, np.array(tens), np.array(rcols), (A, T, I1, I2)


def stack_tensor(c_full, stacking):
    """(M,N,3,3) -> (M, rows). stacking 9: all entries (Frobenius weighting);
    stacking 6: unique symmTensor components once each."""
    if stacking == 9:
        return c_full.reshape(c_full.shape[0], -1)
    s6 = np.stack([c_full[:, :, i, j] for (i, j) in SYMM_IDX], axis=2)
    return s6.reshape(c_full.shape[0], -1)


def enet_path_supports(X, y, log=print):
    """Elastic net (Eqs. 17-19) over the (lambda, rho) grid; returns the set
    of unique supports (abstract model forms) and the survival grid count."""
    K, m = X.shape
    scale = np.sqrt((X ** 2).mean(axis=0))
    scale[scale == 0] = 1.0
    Xs = X / scale
    G = (Xs.T @ Xs) / K                 # (m,m)
    b = (Xs.T @ y) / K                  # (m,)
    supports = {}
    for rho in RHO_GRID:
        lam_max = np.max(np.abs(b)) / rho
        lams = np.logspace(np.log10(lam_max), np.log10(XI * lam_max),
                           N_LAMBDA)
        w = np.zeros(m)
        for lam in lams:
            w = cd_enet(G, b, w, lam, rho)
            supp = tuple(np.flatnonzero(np.abs(w) > 1e-10))
            if supp:
                supports.setdefault(supp, 0)
                supports[supp] += 1
    return supports


def cd_enet(G, b, w0, lam, rho, tol=1e-6, max_iter=2000):
    """Cyclic coordinate descent for
    (1/2K)||y-Xw||^2 + lam*rho*||w||_1 + lam*(1-rho)/2*||w||^2
    on the Gram matrix (X unit-RMS columns => diag(G) ~= 1)."""
    w = w0.copy()
    m = len(b)
    l1 = lam * rho
    l2 = lam * (1.0 - rho)
    Gw = G @ w
    for _ in range(max_iter):
        w_max = 0.0
        d_max = 0.0
        for j in range(m):
            wj = w[j]
            zj = b[j] - Gw[j] + G[j, j] * wj
            wn = np.sign(zj) * max(abs(zj) - l1, 0.0) / (G[j, j] + l2)
            if wn != wj:
                Gw += G[:, j] * (wn - wj)
                w[j] = wn
                d_max = max(d_max, abs(wn - wj))
            w_max = max(w_max, abs(w[j]))
        if d_max <= tol * max(w_max, 1e-12):
            break
    return w


def ridge_infer(X, y, support, lam_r):
    """Eq. 20 taken literally: ||C_s theta - Delta||^2 + lam_r ||theta||^2
    on the RAW candidates."""
    Xs = X[:, list(support)]
    A = Xs.T @ Xs + lam_r * np.eye(len(support))
    theta = np.linalg.solve(A, Xs.T @ y)
    resid = y - Xs @ theta
    return theta, float((resid ** 2).mean())


def discover(args):
    t0 = time.time()
    U, k, omega, gradU, kDef, bDel = load_frozen(args.case_dir, args.time)
    names, tens, rcols, _ = build_libraries(k, omega, gradU)
    result = {"case_dir": str(args.case_dir), "time": args.time,
              "n_cells": int(k.shape[0]), "stacking": args.stacking,
              "rho_grid": RHO_GRID, "n_lambda": N_LAMBDA, "xi": XI,
              "lambda_r": LAMBDA_R, "targets": {}}

    for target in ("R", "bDelta"):
        if target == "R":
            X = rcols.T                              # (N, 48)
            y = kDef
        else:
            X = stack_tensor(tens, args.stacking).T  # (rows, 48)
            yfull = symm_to_full(bDel)
            if args.stacking == 9:
                y = yfull.reshape(-1)
            else:
                y = full_to_symm(yfull).reshape(-1)
        # Discard rule (Section 3.1)
        colmax = np.abs(X).max(axis=0)
        keep = np.flatnonzero(colmax <= DISCARD_MAG)
        discarded = [names[j] for j in np.flatnonzero(colmax > DISCARD_MAG)]
        Xk = X[:, keep]
        kept_names = [names[j] for j in keep]

        supports = enet_path_supports(Xk, y)
        forms = []
        for supp, hits in sorted(supports.items(),
                                 key=lambda kv: (len(kv[0]), -kv[1])):
            entry = {"active": [kept_names[j] for j in supp],
                     "grid_hits": hits, "coefficients": {}}
            for lam_r in LAMBDA_R:
                theta, mse = ridge_infer(Xk, y, supp, lam_r)
                entry["coefficients"][str(lam_r)] = {
                    "theta": {kept_names[j]: float(t)
                              for j, t in zip(supp, theta)},
                    "train_mse": mse,
                }
            forms.append(entry)
        result["targets"][target] = {
            "n_rows": int(X.shape[0]),
            "n_candidates_kept": int(len(keep)),
            "discarded": discarded,
            "n_distinct_forms": len(forms),
            "target_mse_of_zero_model": float((y ** 2).mean()),
            "forms": forms,
        }
        print(f"[{target}] rows={X.shape[0]} kept={len(keep)} "
              f"discarded={len(discarded)} forms={len(forms)}")

    result["wall_seconds"] = round(time.time() - t0, 2)
    Path(args.out).write_text(json.dumps(result, indent=1))
    print(f"wrote {args.out} ({result['wall_seconds']} s)")


def parse_terms(spec):
    """'1:0:0:0.93,2:0:0:4.09' -> list of (n, p, q, c)."""
    out = []
    if spec:
        for part in spec.split(","):
            n, p, q, c = part.split(":")
            out.append((int(n), int(p), int(q), float(c)))
    return out


def evalmodel(args):
    """IC1: evaluate the symbolic model exactly as the solver does and
    compare with solver-written fields."""
    U, k, omega, gradU, kDef, bDel = load_frozen(args.case_dir, args.time)
    A, T, I1, I2 = build_basis(k, omega, gradU)
    b_model = np.zeros_like(T[0])
    for (n, p, q, c) in parse_terms(args.bterms):
        b_model += c * ((I1 ** p) * (I2 ** q))[:, None, None] * T[n - 1]
    r_model = np.zeros_like(k)
    for (n, p, q, c) in parse_terms(args.rterms):
        cand = ((I1 ** p) * (I2 ** q))[:, None, None] * T[n - 1]
        r_model += 2.0 * k * c * np.einsum("nij,nij->n", cand, A)
    report = {}
    if args.check_kdeficit:
        solver = read_of_field(args.check_kdeficit)[:, 0]
        denom = np.linalg.norm(solver) or 1.0
        report["kDeficit_rel_l2"] = float(
            np.linalg.norm(solver - r_model) / denom)
    if args.check_bijdelta:
        solver = read_of_field(args.check_bijdelta)
        mine = full_to_symm(b_model)
        denom = np.linalg.norm(solver) or 1.0
        report["bijDelta_rel_l2"] = float(
            np.linalg.norm(solver - mine) / denom)
    print(json.dumps(report, indent=1))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("discover")
    d.add_argument("--case-dir", required=True)
    d.add_argument("--time", required=True)
    d.add_argument("--out", required=True)
    d.add_argument("--stacking", type=int, default=9, choices=(9, 6))
    d.set_defaults(func=discover)
    e = sub.add_parser("evalmodel")
    e.add_argument("--case-dir", required=True)
    e.add_argument("--time", required=True)
    e.add_argument("--rterms", default="")
    e.add_argument("--bterms", default="")
    e.add_argument("--check-kdeficit")
    e.add_argument("--check-bijdelta")
    e.set_defaults(func=evalmodel)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
