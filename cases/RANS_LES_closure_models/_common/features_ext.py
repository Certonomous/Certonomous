#!/usr/bin/env python3
"""The extended (17-feature) input set used by the TBRF reproduction.

Features 1-5 are Pope's five invariants (identical to the TBNN inputs).
Features 6-17 are bounded flow markers of the form a/(|a|+|b|), the normalisation
style of Wang, Wu & Xiao (2017) Table 1 [VERIFIED-PDF: arXiv:1606.07987v2].

DEPARTURE, disclosed: Kaandorp & Dwight (2020) take their 17 features from
Wang et al.'s table, which includes a wall-distance-based Reynolds number. The
benchmark ships `walldist` only on the parametric hills and the NASA hump, not on
the ducts, PH_Breuer or CBFS, so **no wall-distance feature is used here**. The
count 17 is matched deliberately; the contents are not identical to theirs.
"""
from __future__ import annotations
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from of_read import read_field, latest_time_dir, sym_to_full, structured_gradient
import sst_baseline_metrics as SB
import tensor_basis as TB

NAMES = ["lam1", "lam2", "lam3", "lam4", "lam5",
         "q_excess_rotation", "q_turb_intensity", "q_strain_time_ratio",
         "q_pgrad_streamline", "q_nonorthogonality", "q_k_convection",
         "q_stress_ratio", "q_visc_ratio", "q_pgrad_vs_shear",
         "q_streamline_curv", "q_strain_vs_rot", "q_turb_reynolds"]


def _b(a, c):
    """Bounded ratio a/(|a|+|c|), zero where both vanish."""
    d = np.abs(a) + np.abs(c)
    return np.where(d > 1e-30, a / np.maximum(d, 1e-30), 0.0)


def extended_features(case, path, family):
    d = SB.load_case(case, path, family)
    t = latest_time_dir(path)
    C, U, k, nut = d["C"], d["U"], d["k"], d["nut"]
    omega = read_field(os.path.join(path, t, "omega"))
    p = read_field(os.path.join(path, t, "p"))
    nu = SB.case_meta(path).get("nu", 1e-5)
    A = TB._grad_u(d)
    S = 0.5 * (A + A.transpose(0, 2, 1))
    W = 0.5 * (A - A.transpose(0, 2, 1))
    eps = TB.BETA_STAR * np.maximum(k, 0) * np.maximum(omega, 1e-30)
    Tt = np.maximum(k, 0) / np.maximum(eps, 1e-30)
    nu_val = nu if nu else 1e-5
    Tt = np.maximum(Tt, TB.CT_DURBIN * np.sqrt(nu_val / np.maximum(eps, 1e-30)))
    lam, _ = TB.invariants_and_basis(S * Tt[:, None, None], W * Tt[:, None, None])

    gp = structured_gradient(C, p)
    gk = structured_gradient(C, k)
    nS = np.sqrt((S ** 2).sum(axis=(1, 2)))
    nW = np.sqrt((W ** 2).sum(axis=(1, 2)))
    nU = np.linalg.norm(U, axis=1)
    tau_R = sym_to_full(d["tau_R"])
    ntau = np.sqrt((tau_R ** 2).sum(axis=(1, 2)))
    Pk = np.abs(np.einsum("nij,nij->n", tau_R, S))

    f = np.empty((C.shape[0], 17), np.float32)
    f[:, 0:5] = lam
    f[:, 5] = _b(nW - nS, nW + nS)
    f[:, 6] = _b(k, 0.5 * (U ** 2).sum(1))
    f[:, 7] = _b(nS * Tt, np.ones_like(nS))
    f[:, 8] = _b(np.einsum("ni,ni->n", U, gp), np.linalg.norm(gp, axis=1) * nU)
    f[:, 9] = _b(np.abs(np.einsum("ni,nj,nij->n", U, U, S)), nU * nU * nS)
    f[:, 10] = _b(np.einsum("ni,ni->n", U, gk), Pk)
    f[:, 11] = _b(ntau, k)
    f[:, 12] = _b(nut, 100.0 * nu_val)
    f[:, 13] = _b(np.linalg.norm(gp, axis=1), np.abs(np.einsum("nj,nij,ni->n", U, A, U)) / np.maximum(nU, 1e-30))
    f[:, 14] = _b(np.abs(np.einsum("ni,nij,nj->n", U, A, U)), nU * nU * np.sqrt((A ** 2).sum(axis=(1, 2))))
    f[:, 15] = _b(nS - nW, nS + nW)
    f[:, 16] = _b(np.sqrt(np.maximum(k, 0)) / np.maximum(nu_val * omega, 1e-30), 50.0 * np.ones_like(k))
    return f
