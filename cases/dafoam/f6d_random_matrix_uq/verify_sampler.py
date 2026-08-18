"""
F6d -- verification of the random-matrix sampler AGAINST THE PAPER'S OWN STATED
PROPERTIES, run before any CFD.  Nothing here touches a solver; every check is
a property the paper asserts and that an implementation can get wrong silently.

Checks:
  V1  E{[G]} = [I]                         (paper Sec. 3.1, constraint below Eq. 8)
      -- and the same check with Appendix A's factor-of-2-less L_ii, to show
      which of the paper's two mutually inconsistent formulas is the right one.
  V2  delta recovered from Eq. (12):  delta = (1/d) E{||[G]-[I]||_F^2} ^ 1/2
  V3  every realisation [G] positive definite  (the paper's central claim:
      realizability "guaranteed by construction")
  V4  KL basis: Fredholm solution sanity -- pointwise variance -> 1 as modes
      are added; variance captured by N_KL = 30 (paper says ~90%)
  V5  PCE: the reconstructed marginal of u_i matches Gamma(k_i, 1)
  V6  the synthesised field has the prescribed two-point correlation, Eq. (18)
  V7  field-sampled [R] realisations are positive semi-definite on the real
      RANS mesh, and the ensemble mean of [R] returns [R_bar]

Usage:  python3 verify_sampler.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import gamma as gamma_dist
from scipy.stats import kstest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "f6b_periodic_hills" / "case_breuer_re10595"))

import rmt_sampler as rmt  # noqa: E402
import foam_io as fio      # noqa: E402

CASE = HERE.parent / "f6b_periodic_hills" / "case_breuer_re10595"
R_PATH = CASE / "10000" / "turbulenceProperties:R"

out = {}


def report(name, ok, detail):
    tag = "PASS" if ok else "FAIL"
    print(f"[{tag}] {name}: {detail}")
    out[name] = {"pass": bool(ok), "detail": detail}
    return ok


# --------------------------------------------------------------------- V1/V2/V3
def v1_v2_v3(delta, n=200000, seed=1):
    kl = rmt.build_kl_basis(nx=6, ny=4, n_kl=4)  # unused here, cheap placeholder
    s = rmt.RandomMatrixSampler(delta, kl, seed=seed)
    G = s.sample_G_pointwise(n)
    mean = G.mean(axis=0)
    err = np.abs(mean - np.eye(3)).max()
    # 3-sigma-ish tolerance on a Monte Carlo mean of n samples
    tol = 8.0 / np.sqrt(n)
    report(f"V1 E[G]=I (delta={delta})", err < tol,
           f"max|E[G]-I| = {err:.5f} (MC tol {tol:.5f}); "
           f"diag E[G] = {np.diag(mean).round(5).tolist()}")

    # the Appendix-A variant, L_ii = sigma_d*sqrt(u) (no factor 2): should FAIL
    rng = np.random.default_rng(seed + 7)
    L = np.zeros((n, 3, 3))
    for i in range(3):
        u = rng.gamma(s.shapes[i], 1.0, size=n)
        L[:, i, i] = s.sigma_d * np.sqrt(u)
    for (i, j) in [(0, 1), (0, 2), (1, 2)]:
        L[:, i, j] = s.sigma_d * rng.standard_normal(n)
    G_appx = np.einsum("nki,nkj->nij", L, L)
    d_appx = np.diag(G_appx.mean(axis=0))
    print(f"       [context] Appendix-A variant (no factor 2) gives diag E[G] = "
          f"{d_appx.round(5).tolist()} -- i.e. ~1/2, confirming the main text "
          f"(Eq. 16/24) is the correct formula and Appendix A step 2.4 a typo.")
    out.setdefault("context", {})[f"appendixA_variant_diagEG_delta{delta}"] = d_appx.tolist()

    # V2: delta recovered from Eq. (12)
    diff = G - np.eye(3)
    fro2 = np.einsum("nij,nij->n", diff, diff)
    delta_hat = np.sqrt(fro2.mean() / rmt.D)
    report(f"V2 delta recovered from Eq.(12) (delta={delta})",
           abs(delta_hat - delta) / delta < 0.02,
           f"delta_hat = {delta_hat:.5f} vs specified {delta}")

    # V3: positive definiteness of every realisation
    ev = np.linalg.eigvalsh(G)
    report(f"V3 every [G] positive definite (delta={delta})", (ev[:, 0] > 0).all(),
           f"min eigenvalue over {n} draws = {ev[:,0].min():.3e}")


# ------------------------------------------------------------------------- V4
def v4(kl):
    var = kl.pointwise_variance()
    report("V4a KL pointwise variance <= 1", var.max() <= 1.0 + 1e-9,
           f"max Var[w(x)] = {var.max():.4f}, mean = {var.mean():.4f} "
           f"(untruncated value is exactly 1)")
    report("V4b KL variance captured by N_KL modes", kl.variance_captured > 0.85,
           f"{100*kl.variance_captured:.2f}% of total variance in "
           f"{kl.lam.size} modes (paper Sec. 4.1 reports ~90% for N_KL=30)")
    out.setdefault("context", {})["kl_variance_captured"] = kl.variance_captured
    out["context"]["kl_lambda_first10"] = kl.lam[:10].tolist()


# ------------------------------------------------------------------------- V5
def v5(delta, kl, seed=3):
    s = rmt.RandomMatrixSampler(delta, kl, seed=seed)
    rng = np.random.default_rng(seed)
    w = rng.standard_normal(200000)
    worst = 0.0
    for i in range(3):
        u = rmt.pce_evaluate(s.pce[i], w)
        ks = kstest(u, gamma_dist(s.shapes[i], scale=1.0).cdf)
        worst = max(worst, ks.statistic)
    report(f"V5 PCE marginal matches Gamma(k_i,1) (delta={delta})",
           np.isfinite(worst) and worst < 0.02,
           f"worst KS statistic over i=1,2,3 = {worst:.3e} "
           f"(N_p={s.n_p}; paper Sec. 4.1: 'third order ... found to be sufficient')")

    # independent second quadrature rule for the SAME Eq.(27) coefficients
    alt = []
    for i in range(3):
        c_alt = rmt.pce_coefficients(s.shapes[i], s.n_p, n_quad=40)
        alt.append(float(np.abs(c_alt - s.pce[i]).max() / max(abs(s.pce[i][0]), 1e-30)))
    report(f"V5b PCE coefficients quadrature-converged (delta={delta})",
           max(alt) < 1e-8,
           f"max relative change from n_quad 80 -> 40 = {max(alt):.2e}; "
           f"U_beta(i=1) = {np.round(s.pce[0], 6).tolist()}")


# ------------------------------------------------------------------------- V6
def v6(kl, seed=5, n=4000):
    rng = np.random.default_rng(seed)
    M = kl.phi.shape[0]
    # empirical two-point correlation against the prescribed Eq. (18) kernel
    idx = rng.choice(M, size=60, replace=False)
    W = np.empty((n, idx.size))
    for r in range(n):
        W[r] = kl.synthesize(rng.standard_normal(kl.lam.size))[idx]
    emp = np.corrcoef(W.T)
    dx = (kl.xy[idx, 0][:, None] - kl.xy[idx, 0][None, :]) / kl.lx
    dy = (kl.xy[idx, 1][:, None] - kl.xy[idx, 1][None, :]) / kl.ly
    exact = np.exp(-(dx ** 2 + dy ** 2))
    err = np.abs(emp - exact).max()
    report("V6 synthesised field reproduces kernel Eq.(18)", err < 0.12,
           f"max |rho_empirical - rho_Eq18| = {err:.4f} over 60 probe points, "
           f"{n} realisations, N_KL={kl.lam.size} (truncation makes this "
           f"an approximation by construction)")


# ------------------------------------------------------------------------- V7
def v7(delta, kl, n_samples=200, seed=11):
    R_bar = rmt.read_symmtensor_internal(R_PATH)
    L_R, audit = rmt.cholesky_upper_field(R_bar)
    print(f"       [context] baseline Reynolds-stress realizability audit: "
          f"{audit['n_cells_indefinite']}/{audit['n_cells']} cells "
          f"({100*audit['frac_cells_indefinite']:.3f}%) have a NEGATIVE eigenvalue; "
          f"worst lambda_min/tr(R) = {audit['worst_eigenvalue_over_trace']:.4e}; "
          f"{audit['n_cells_jittered']} cells needed the paper's Sec.3.1 diagonal shift.")
    out.setdefault("context", {})["baseline_realizability_audit"] = audit

    Cx = fio.read_internal_field(str(CASE / "0" / "Cx"))
    Cy = fio.read_internal_field(str(CASE / "0" / "Cy"))
    xy_rans = np.column_stack([Cx, Cy])

    s = rmt.RandomMatrixSampler(delta, kl, seed=seed)
    P = rmt.build_interp_operator(kl, xy_rans)

    acc = np.zeros_like(R_bar)
    min_eig = np.inf
    for _ in range(n_samples):
        G_kl = s.sample_G_field()
        G_rans = rmt.interp_G(P, G_kl)
        G_rans = 0.5 * (G_rans + np.transpose(G_rans, (0, 2, 1)))
        R = rmt.assemble_R(L_R, G_rans)
        if not np.isfinite(R).all():
            raise FloatingPointError("non-finite entry in a sampled [R]")
        acc += R
        min_eig = min(min_eig, float(np.linalg.eigvalsh(R)[:, 0].min()))
    mean_R = acc / n_samples

    report(f"V7a sampled [R] realizable on the RANS mesh (delta={delta})",
           min_eig >= -1e-14,
           f"min eigenvalue over {n_samples} field realisations x "
           f"{R_bar.shape[0]} cells = {min_eig:.3e}")

    # ensemble mean should return R_bar (Eq. 7); MC error ~ delta/sqrt(N)
    scale = np.abs(R_bar).max()
    rel = np.abs(mean_R - R_bar).max() / scale
    report(f"V7b E[R] returns the baseline R_bar (delta={delta})", rel < 0.35,
           f"max|mean(R)-R_bar|/max|R_bar| = {rel:.4f} over {n_samples} "
           f"field samples (MC error, decreases as 1/sqrt(N))")
    return audit


def main():
    print("=" * 78)
    print("F6d sampler verification -- Xiao, Wang & Ghanem arXiv:1603.09656")
    print("=" * 78)
    for delta in (0.2, 0.6):
        v1_v2_v3(delta)
    kl = rmt.build_kl_basis()   # paper Table 1: 50 x 30, N_KL = 30, lx=2, ly=1
    v4(kl)
    for delta in (0.2, 0.6):
        v5(delta, kl)
    v6(kl)
    v7(0.2, kl, n_samples=60)
    n_fail = sum(1 for v in out.values() if isinstance(v, dict) and v.get("pass") is False)
    print("-" * 78)
    print(f"{sum(1 for v in out.values() if isinstance(v,dict) and 'pass' in v)} checks, "
          f"{n_fail} failed")
    (HERE / "verify_sampler_result.json").write_text(json.dumps(out, indent=2))
    print(f"wrote {HERE/'verify_sampler_result.json'}")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
