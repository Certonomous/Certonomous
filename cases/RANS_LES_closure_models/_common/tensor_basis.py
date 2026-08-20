#!/usr/bin/env python3
"""Pope (1975) integrity basis: the 5 invariants and 10 tensors, plus the
per-case feature/label assembly used by the Phase-3 tensor-basis reproductions.

Basis and invariants are written exactly as Pope, J. Fluid Mech. 72(2), p. 335
[VERIFIED-PDF], and as reproduced by Ling, Kurzawski & Templeton (2016) eq. (2),
p. 7 [VERIFIED-PDF: SAND2016-7345J].

Nothing here is fitted. Reads only from the benchmark clone; writes only into
/home/ubuntu/closure-data/ (outside the repo).
"""
from __future__ import annotations
import os, sys, json, hashlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from of_read import (read_field, latest_time_dir, sym_to_full, anisotropy,
                     realisability_violation, structured_gradient)
import sst_baseline_metrics as SB          # reuse its verified case table + loader

BETA_STAR = 0.09        # Menter 1994 eq. (A6), p. 1603 [VERIFIED-PDF]
CT_DURBIN = 6.0         # Durbin time-scale bound coefficient (disclosed departure)


# ------------------------------------------------------------------ basis
def invariants_and_basis(s, r):
    """s, r: (N,3,3) normalised strain and rotation. Returns lam (N,5), T (N,10,3,3)."""
    N = s.shape[0]
    I = np.eye(3)[None, :, :]
    mm = lambda a, b: np.einsum("nij,njk->nik", a, b)
    tr = lambda a: np.einsum("nii->n", a)

    s2 = mm(s, s); s3 = mm(s2, s)
    r2 = mm(r, r)
    r2s = mm(r2, s); r2s2 = mm(r2, s2)

    lam = np.stack([tr(s2), tr(r2), tr(s3), tr(r2s), tr(r2s2)], axis=1)

    sr = mm(s, r); rs = mm(r, s)
    rs2 = mm(r, s2); s2r = mm(s2, r)
    r2s_sr2 = r2s + mm(s, r2)
    T = np.empty((N, 10, 3, 3))
    T[:, 0] = s
    T[:, 1] = sr - rs
    T[:, 2] = s2 - I * (tr(s2) / 3.0)[:, None, None]
    T[:, 3] = r2 - I * (tr(r2) / 3.0)[:, None, None]
    T[:, 4] = rs2 - s2r
    T[:, 5] = r2s_sr2 - I * (2.0 / 3.0 * tr(mm(s, r2)))[:, None, None]
    T[:, 6] = mm(rs, r2) - mm(r2, sr)
    T[:, 7] = mm(sr, s2) - mm(s2, rs)
    T[:, 8] = mm(r2, s2) + mm(s2, r2) - I * (2.0 / 3.0 * tr(r2s2))[:, None, None]
    T[:, 9] = mm(mm(r, s2), r2) - mm(mm(r2, s2), r)
    return lam, T


def _grad_u(d):
    """dU_i/dx_j as (N,3,3), from the shipped gradU where present."""
    if d.get("gradU") is not None:
        G = np.asarray(d["gradU"]).reshape(-1, 3, 3)
        # OpenFOAM writes gradU with component (j,i) = d U_i / d x_j
        return G.transpose(0, 2, 1)
    return structured_gradient(d["C"], d["U"])


def case_arrays(case, path, family):
    """Everything one case contributes: lam, T, b_LES, b_RANS, mask, coords."""
    d = SB.load_case(case, path, family)
    t = latest_time_dir(path)
    omega = read_field(os.path.join(path, t, "omega"))
    k = d["k"]
    A = _grad_u(d)
    S = 0.5 * (A + A.transpose(0, 2, 1))
    W = 0.5 * (A - A.transpose(0, 2, 1))

    eps = BETA_STAR * np.maximum(k, 0.0) * np.maximum(omega, 1e-30)
    T_turb = np.maximum(k, 0.0) / np.maximum(eps, 1e-30)
    # Durbin lower bound on the time scale; nu from the case's transportProperties
    nu = SB.case_meta(path).get("nu")
    if nu is not None and nu > 0:
        T_turb = np.maximum(T_turb, CT_DURBIN * np.sqrt(nu / np.maximum(eps, 1e-30)))
    Tt = T_turb[:, None, None]
    lam, Tb = invariants_and_basis(S * Tt, W * Tt)

    tau_L = sym_to_full(d["tau_LES"])
    b_L, valid = anisotropy(tau_L, d["k_LES"])
    tau_R = sym_to_full(d["tau_R"])
    b_R, _ = anisotropy(tau_R, k, k_ref=d["k_LES"])
    return dict(case=case, family=family, split=SB.split_of(case),
                lam=lam, T=Tb, b_LES=b_L, b_RANS=b_R, valid=valid,
                C=d["C"], n=d["n"], time=t)
