#!/usr/bin/env python3
"""R4 step 2 - assemble the SpaRTA candidate library on the 27 frozen training
cases.  SELECTS NOTHING and FITS NOTHING; it builds columns and writes them.

Ansatz (PREREGISTRATION sec. 2, Schmelzer Eq. 8, preprint p. 8):
    b^Delta_ij = sum_m c_m I1^p I2^q T^(n)_ij
with tau = 1/omega, S = (tau/2)(A + A^T), Omega = (tau/2)(A - A^T),
I1 = S_mn S_nm, I2 = Omega_mn Omega_nm (<= 0), A_ij = d_j U_i.
R carries the 2k factor of Schmelzer Eq. 12 inside the candidate, exactly as
`kOmegaSSTSparta::updateCorrections` evaluates it, so a fitted coefficient is
the number that goes into `RTerms` unchanged.

Exponent grid (PREREGISTRATION sec. 2.4): p, q in {0,1,2} with p + q <= 2.
Tensors: T1 = S, T2 = SW - WS, T3 = S^2 - I tr(S^2)/3, T4 = W^2 - I tr(W^2)/3.

The frozen degeneracy of PREREGISTRATION sec. 2.1 (exact duct T4 = -T3 and
I2 = -I1) is MEASURED here per family and re-reported; it is acted on in
fs3_select.py, not here.

No test or validation case is read (asserted).
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "_common"))
import r4_lib as R
from of_read import read_field

FROZEN = os.path.join(R.WORK, "frozen")
OUT = os.path.join(R.WORK, "dataset")

# PREREGISTRATION sec. 2.4
EXPONENTS = [(0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2)]
SYMM_IDX = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]


def mono_name(p, q, tname):
    parts = []
    if p:
        parts.append("I1" if p == 1 else f"I1^{p}")
    if q:
        parts.append("I2" if q == 1 else f"I2^{q}")
    parts.append(tname)
    return "*".join(parts)


CAND_NAMES = [mono_name(p, q, f"T{n}")
              for n in (1, 2, 3, 4) for (p, q) in EXPONENTS]


def sym_to_full(b6):
    n = b6.shape[0]
    out = np.empty((n, 3, 3))
    for c, (i, j) in enumerate(SYMM_IDX):
        out[:, i, j] = b6[:, c]
        out[:, j, i] = b6[:, c]
    return out


def basis(k, omega, gradU9):
    """A (A_ij = d_j U_i), [T1..T4], I1, I2 -- the solver's own conventions."""
    gof = gradU9.reshape(-1, 3, 3)          # OpenFOAM: (gradU)_ij = d_i U_j
    A = np.transpose(gof, (0, 2, 1))        # paper: A_ij = d_j U_i
    tau = 1.0 / omega
    S = 0.5 * tau[:, None, None] * (A + np.transpose(A, (0, 2, 1)))
    W = 0.5 * tau[:, None, None] * (A - np.transpose(A, (0, 2, 1)))
    I1 = np.einsum("nij,nji->n", S, S)
    I2 = np.einsum("nij,nji->n", W, W)      # <= 0
    eye = np.eye(3)[None, :, :]
    SS = np.einsum("nik,nkj->nij", S, S)
    WW = np.einsum("nik,nkj->nij", W, W)
    T1 = S
    T2 = (np.einsum("nik,nkj->nij", S, W) - np.einsum("nik,nkj->nij", W, S))
    T3 = SS - (np.trace(SS, axis1=1, axis2=2) / 3.0)[:, None, None] * eye
    T4 = WW - (np.trace(WW, axis1=1, axis2=2) / 3.0)[:, None, None] * eye
    return A, [T1, T2, T3, T4], I1, I2


def case_columns(case_dir):
    t = R.latest_time(case_dir)
    d = os.path.join(case_dir, t)
    k = read_field(os.path.join(d, "k")).ravel()
    # `bound(k, kMin)` inside the model replaces every non-positive k_LES cell
    # with a small POSITIVE value, so the written k cannot identify the cells
    # where the LES anisotropy is undefined.  The shipped 0/k can, and does.
    k_les_raw = read_field(os.path.join(case_dir, "0", "k")).ravel()
    omega = read_field(os.path.join(d, "omega")).ravel()
    nut = read_field(os.path.join(d, "nut")).ravel()
    gradU = read_field(os.path.join(d, "grad(U)"))
    kDef = read_field(os.path.join(d, "kDeficit")).ravel()
    bDel = sym_to_full(read_field(os.path.join(d, "bijDelta")))
    bData = sym_to_full(read_field(os.path.join(d, "bijData")))
    A, T, I1, I2 = basis(k, omega, gradU)
    n = k.shape[0]
    CT = np.empty((len(CAND_NAMES), n, 3, 3))
    CR = np.empty((len(CAND_NAMES), n))
    c = 0
    for Tn in T:
        for (p, q) in EXPONENTS:
            mono = (I1 ** p) * (I2 ** q)
            cand = mono[:, None, None] * Tn
            CT[c] = cand
            CR[c] = 2.0 * k * np.einsum("nij,nij->n", cand, A)
            c += 1
    # b_lin: the linear-EVM anisotropy the correction is added to (Schmelzer
    # Eq. 3), formed from the SAME frozen fields, so b_data = b_lin + b^Delta.
    S_dim = 0.5 * (A + np.transpose(A, (0, 2, 1)))
    b_lin = -(nut / np.maximum(k, 1e-30))[:, None, None] * S_dim
    return dict(n=n, k=k, k_les_raw=k_les_raw, omega=omega, nut=nut,
                I1=I1, I2=I2, A=A,
                T3=T[2], T4=T[3], CT=CT, CR=CR, kDef=kDef, bDel=bDel,
                bData=bData, b_lin=b_lin, time=t)


def degeneracy(d):
    """PREREGISTRATION sec. 2.1 quantities, re-measured on this lane's fields."""
    T3, T4 = d["T3"], d["T4"]
    n3 = np.sqrt((T3 ** 2).sum(axis=(1, 2)))
    r34 = np.sqrt(((T3 + T4) ** 2).sum(axis=(1, 2))) / np.maximum(n3, 1e-300)
    i12 = np.abs(d["I1"] + d["I2"]) / np.maximum(np.abs(d["I1"]), 1e-300)
    # per-cell rank of {T1..T4} on a seeded subsample, as FS2 measured it
    rng = np.random.default_rng(0)
    m = min(4000, d["n"])
    idx = rng.choice(d["n"], m, replace=False)
    M = np.stack([d["CT"][j * len(EXPONENTS)][idx].reshape(m, 9)
                  for j in range(4)], axis=1)          # (m, 4, 9)
    sv = np.linalg.svd(M, compute_uv=False)
    ranks = (sv > sv[:, :1] * 1e-10).sum(axis=1)   # relative tolerance: this
    # reproduces PREREGISTRATION sec. 2.1's 3.000 on the BASELINE RANS duct
    # field exactly (2.7398e-17 / 6.4084e-16 / 7.0760e-15 against its 2.74e-17
    # / 6.41e-16 / 7.08e-15), which is what fixes the convention.
    return dict(T4_plus_T3_over_T3_median=float(np.median(r34)),
                T4_plus_T3_over_T3_p99=float(np.percentile(r34, 99)),
                T4_plus_T3_over_T3_max=float(r34.max()),
                I1_plus_I2_over_I1_median=float(np.median(i12)),
                rank_mean=float(ranks.mean()),
                rank_hist=[int((ranks == r).sum()) for r in range(5)],
                n_sampled=int(m))


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default="",
                    help="comma-separated subset; default = every training "
                         "case whose frozen run meets the STRICT COMPLETION RULE")
    a = ap.parse_args()
    cases = R.training_cases()
    if a.cases:
        want = set(a.cases.split(","))
        cases = [c for c in cases if c[0] in want]
        assert len(cases) == len(want), "unknown case name in --cases"
    R.assert_no_test_case([c for c, _, _ in cases])
    os.makedirs(OUT, exist_ok=True)
    meta, deg = {}, {}
    for case, _, family in cases:
        cd = os.path.join(FROZEN, case)
        ok, why, info = R.frozen_complete(cd)
        assert ok, f"{case}: frozen run NOT complete ({why}) - refusing to fit"
        d = case_columns(cd)
        np.savez_compressed(
            os.path.join(OUT, f"{case}.npz"),
            CT=d["CT"].astype(np.float64), CR=d["CR"].astype(np.float64),
            kDef=d["kDef"], bDel=d["bDel"], bData=d["bData"],
            b_lin=d["b_lin"], k=d["k"], k_les_raw=d["k_les_raw"],
            omega=d["omega"], I1=d["I1"],
            I2=d["I2"], names=np.array(CAND_NAMES))
        deg[case] = degeneracy(d)
        meta[case] = dict(family=family, n_cells=int(d["n"]),
                          frozen_time=d["time"],
                          converged_at=info.get("converged_at"),
                          R_drift_pct=info.get("R_drift_pct"))
        print(f"[ok] {case:22s} {family:10s} n={d['n']:6d} "
              f"rank={deg[case]['rank_mean']:.3f} "
              f"|T3+T4|/|T3| med={deg[case]['T4_plus_T3_over_T3_median']:.3e}",
              flush=True)
    json.dump(dict(candidates=CAND_NAMES, n_candidates=len(CAND_NAMES),
                   exponents=EXPONENTS, cases=meta, degeneracy=deg,
                   n_cells_total=sum(m["n_cells"] for m in meta.values())),
              open(os.path.join(OUT, "dataset_manifest.json"), "w"), indent=1)
    print(f"\n{len(meta)} cases, "
          f"{sum(m['n_cells'] for m in meta.values())} cells -> {OUT}")


if __name__ == "__main__":
    main()
