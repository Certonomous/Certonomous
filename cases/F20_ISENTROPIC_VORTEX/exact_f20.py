#!/usr/bin/env python3
"""
F20 -- THE EXACT SOLUTION of the 2-D inviscid isentropic vortex (Yee, Sandham
& Djomehri 1999 / Shu 1998 form) and the DISCRETISATION-DERIVED error
prediction every F20 band is built from.

    free stream rho = p = T = 1, (u, v) = (1, 1), gamma = 1.4, R = 1
    vortex strength beta = 5 centred at (5, 5) on the periodic box [0, 10]^2:
      u = 1 - beta/(2 pi) e^{(1 - r^2)/2} (y - 5),  v = 1 + beta/(2 pi) e^{(1 - r^2)/2} (x - 5)
      T = 1 - (gamma - 1) beta^2 / (8 gamma pi^2) e^{1 - r^2},   rho = T^{1/(gamma-1)},  p = rho T
    the whole pattern translates with (1, 1) and returns to its origin at t = 10.

THE REFERENCE IS NOT A PAPER ON THIS BOX.  IT IS A SUBSTITUTION.  The closed
form is verified at selftest by symbolic substitution into the steady Euler
equations in the frame moving with the free stream (continuity, x- and
y-momentum identically zero; entropy p/rho^gamma == 1 exactly); a planted
control (beta in T raised 10 %) must make the momentum residual non-zero; and
the field at t = 10 is shown to equal the field at t = 0 at every cell centre.
The closed form is NOT exactly periodic on a 10 x 10 box (Gaussian tails): the
velocity seam mismatch is 4.9e-5 and the density mismatch is below 1e-12; the
reference used is the PERIODISED field and the discretisation model is
initialised with the same periodised data, so the seam is inside the prediction.

THE BAND PRINCIPLE -- derived from the discretisation, not measured on the
case.  `knp_model` is a numpy re-implementation of rhoCentralFoam's scheme in
two dimensions (directed vanLeer / vanLeerV reconstruction with OpenFOAM's
NVDTVD / NVDVTVDV ratios and the 1000x clamp, the Kurganov weights and fluxes
exactly as rhoCentralFoam.C forms them per face, explicit Euler in time), run
on the ladder's COARSE level (128^2 at its own dt) and on 64^2 at the same
dt/h AND at half that dt.  Because the solver's time integration is FIRST
order (explicit Euler) and dt refines with h, every error carries an O(dt)
part.  For E2 (a norm) the medium and fine levels are extrapolated with the
model's observed order (a control requires it in [1.0, 2.5]); the honest
expectation is an observed order BETWEEN 1 and 2.  For the box-mean kinetic
energy the model SEPARATES the error into a dissipative spatial part S(h)
(read at dt -> 0 from the two 64^2 runs, order ~1.7) and an anti-dissipative
Euler part +B dt (B ~ 0.27): they CANCEL near 128^2 and the sign changes
inside the ladder, so the KE triple is predicted non-monotone; the KE band is
built from |S| + |B dt| at fine (sum of magnitudes, independent of the
cancellation) and the value prediction is their signed sum.

Omissions, stated: vanLeerV's exact tensor form (implemented here as its
projection r = 2 (dU . d.gradU)/|dU|^2 - 1, which is OpenFOAM's definition on
a Cartesian mesh); the extrapolation across two halvings; floating-point
ordering.  Hence a FACTOR-3 window, declared before compute, not an equality.

Refusals are `raise` and `sys.exit(2)`.  Zero `assert` (L-332).
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: exact_f20.py must not run under `python3 -O`.\n")
    sys.exit(2)

import json
import math
import argparse

import numpy as np

# ---------------------------------------------------------------------------
# THE CASE, FROZEN.
# ---------------------------------------------------------------------------
GAMMA = 1.4
R_GAS = 1.0
CP = GAMMA / (GAMMA - 1.0) * R_GAS   # 3.5
CV = CP - R_GAS                      # 2.5
NA_FOAM, K_FOAM = 6.0221417930e+23, 1.38065e-23
MOL_WEIGHT = 1e3 * (NA_FOAM * K_FOAM)          # 8314.47006650545 -> RR/W = 1
BETA = 5.0
U_INF, V_INF = 1.0, 1.0
L_BOX = 10.0
X0, Y0 = 5.0, 5.0
T_END = 10.0                         # one period: U_INF * T_END = L_BOX
# name, N (cells per side), steps (dt = T_END/steps)
LEVELS = (("coarse", 128, 4000), ("medium", 256, 8000), ("fine", 512, 16000))
CO_CEILING = 0.25                    # on the solver-reported CoNum (classical 0.5)


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def h_of(n):
    return L_BOX / float(n)


def dt_of(steps):
    return T_END / float(steps)


def _rel(x, y, t):
    """coordinates relative to the vortex centre at time t, wrapped into [-L/2, L/2)."""
    dx = np.mod(np.asarray(x, dtype=float) - X0 - U_INF * t + 0.5 * L_BOX, L_BOX) - 0.5 * L_BOX
    dy = np.mod(np.asarray(y, dtype=float) - Y0 - V_INF * t + 0.5 * L_BOX, L_BOX) - 0.5 * L_BOX
    return dx, dy


def fields_exact(x, y, t):
    """(rho, u, v, p, T) at points (x, y), time t, on the periodic box."""
    dx, dy = _rel(x, y, t)
    r2 = dx * dx + dy * dy
    g = np.exp(0.5 * (1.0 - r2))
    k = BETA / (2.0 * math.pi)
    u = U_INF - k * g * dy
    v = V_INF + k * g * dx
    T = 1.0 - (GAMMA - 1.0) * BETA ** 2 / (8.0 * GAMMA * math.pi ** 2) * g * g
    rho = T ** (1.0 / (GAMMA - 1.0))
    p = rho * R_GAS * T
    return rho, u, v, p, T


def rho_exact(x, y, t):
    return fields_exact(x, y, t)[0]


_KE = {}


def ke_exact(n_quad=4096):
    """box mean of rho |u|^2 / 2 at t = 0 (== t = T_END) by the midpoint rule."""
    if n_quad not in _KE:
        c = (np.arange(n_quad) + 0.5) * (L_BOX / n_quad)
        X, Y = np.meshgrid(c, c)
        rho, u, v, _p, _T = fields_exact(X, Y, 0.0)
        _KE[n_quad] = float(np.mean(0.5 * rho * (u * u + v * v)))
    return _KE[n_quad]


def seam_mismatch():
    """the PERIODISED field's jump across the x = 0 / x = L seam: the closed
    form evaluated at x -> 0+ (dx -> -5) against x -> L- (dx -> +5)."""
    y = np.linspace(0.0, L_BOX, 2001)
    eps = 1e-9
    f0 = fields_exact(np.full_like(y, eps), y, 0.0)
    f1 = fields_exact(np.full_like(y, L_BOX - eps), y, 0.0)
    return dict(velocity=float(max(np.max(np.abs(f0[1] - f1[1])), np.max(np.abs(f0[2] - f1[2])))),
                density=float(np.max(np.abs(f0[0] - f1[0]))))


# ---------------------------------------------------------------------------
# THE DISCRETISATION MODEL: rhoCentralFoam's KNP scheme in two dimensions
# ---------------------------------------------------------------------------
def _van_leer(r):
    return (r + np.abs(r)) / (1.0 + np.abs(r))


def _ratio(gradcf, gradf):
    sg = np.where(gradcf >= 0, 1.0, -1.0) * np.where(gradf >= 0, 1.0, -1.0)
    clamp = np.abs(gradcf) >= 1000.0 * np.abs(gradf)
    safe = np.where(clamp, 1.0, gradf)
    return np.where(clamp, 2.0 * 1000.0 * sg - 1.0, 2.0 * gradcf / safe - 1.0)


def _recon_scalar(q, ax):
    """face between cell P and its +ax neighbour N (periodic): pos and neg values."""
    qN = np.roll(q, -1, ax); qW = np.roll(q, 1, ax); qNN = np.roll(q, -2, ax)
    gradf = qN - q
    f_pos = q + 0.5 * _van_leer(_ratio(0.5 * (qN - qW), gradf)) * gradf
    f_neg = qN - 0.5 * _van_leer(_ratio(0.5 * (qNN - q), gradf)) * gradf
    return f_pos, f_neg


def _recon_vector(qx, qy, ax):
    """vanLeerV: one limiter for both components from the projection of the
    face jump on the cell's directional derivative (OpenFOAM NVDVTVDV::r)."""
    qxN = np.roll(qx, -1, ax); qxW = np.roll(qx, 1, ax); qxNN = np.roll(qx, -2, ax)
    qyN = np.roll(qy, -1, ax); qyW = np.roll(qy, 1, ax); qyNN = np.roll(qy, -2, ax)
    gfx, gfy = qxN - qx, qyN - qy
    gradf = gfx * gfx + gfy * gfy
    gc_pos = gfx * 0.5 * (qxN - qxW) + gfy * 0.5 * (qyN - qyW)
    gc_neg = gfx * 0.5 * (qxNN - qx) + gfy * 0.5 * (qyNN - qy)
    psi_p = _van_leer(_ratio(gc_pos, gradf))
    psi_n = _van_leer(_ratio(gc_neg, gradf))
    return (qx + 0.5 * psi_p * gfx, qy + 0.5 * psi_p * gfy, qxN - 0.5 * psi_n * gfx, qyN - 0.5 * psi_n * gfy)


def _face_fluxes(rho, rhoUx, rhoUy, rPsi, e, c, h, ax):
    """KNP fluxes through the faces normal to axis `ax` (Sf = h along that axis)."""
    rho_p, rho_n = _recon_scalar(rho, ax)
    rUx_p, rUy_p, rUx_n, rUy_n = _recon_vector(rhoUx, rhoUy, ax)
    rPsi_p, rPsi_n = _recon_scalar(rPsi, ax)
    e_p, e_n = _recon_scalar(e, ax)
    c_p, c_n = _recon_scalar(c, ax)
    Ux_p, Uy_p = rUx_p / rho_p, rUy_p / rho_p
    Ux_n, Uy_n = rUx_n / rho_n, rUy_n / rho_n
    p_p, p_n = rho_p * rPsi_p, rho_n * rPsi_n
    Un_p = Ux_p if ax == 1 else Uy_p
    Un_n = Ux_n if ax == 1 else Uy_n
    phiv_p, phiv_n = Un_p * h, Un_n * h
    cSf_p, cSf_n = c_p * h, c_n * h
    ap = np.maximum(np.maximum(phiv_p + cSf_p, phiv_n + cSf_n), 0.0)
    am = np.minimum(np.minimum(phiv_p - cSf_p, phiv_n - cSf_n), 0.0)
    a_pos = ap / (ap - am)
    aSf = am * a_pos
    a_neg = 1.0 - a_pos
    aphiv_p = phiv_p * a_pos - aSf
    aphiv_n = phiv_n * a_neg + aSf
    amax = np.maximum(np.abs(aphiv_p), np.abs(aphiv_n))
    phi = aphiv_p * rho_p + aphiv_n * rho_n
    pf = (a_pos * p_p + a_neg * p_n) * h
    phiUx = aphiv_p * rUx_p + aphiv_n * rUx_n + (pf if ax == 1 else 0.0)
    phiUy = aphiv_p * rUy_p + aphiv_n * rUy_n + (pf if ax == 0 else 0.0)
    phiEp = (aphiv_p * (rho_p * (e_p + 0.5 * (Ux_p * Ux_p + Uy_p * Uy_p)) + p_p)
             + aphiv_n * (rho_n * (e_n + 0.5 * (Ux_n * Ux_n + Uy_n * Uy_n)) + p_n) + aSf * p_p - aSf * p_n)
    return phi, phiUx, phiUy, phiEp, amax


def _div(F, ax):
    return F - np.roll(F, 1, ax)


def knp_model(n, steps, gamma=GAMMA):
    h, dt = h_of(n), dt_of(steps)
    c1 = (np.arange(n) + 0.5) * h
    X, Y = np.meshgrid(c1, c1)                     # [j, i]: y along axis 0, x along axis 1
    rho, u, v, p, T = fields_exact(X, Y, 0.0)
    rhoUx, rhoUy = rho * u, rho * v
    rhoE = rho * (CV * T + 0.5 * (u * u + v * v))
    vol = h * h
    co_max = 0.0
    for _k in range(steps):
        T = p / (rho * R_GAS)
        rPsi = R_GAS * T
        e = CV * T
        c = np.sqrt(gamma * rPsi)
        fx = _face_fluxes(rho, rhoUx, rhoUy, rPsi, e, c, h, 1)
        fy = _face_fluxes(rho, rhoUx, rhoUy, rPsi, e, c, h, 0)
        s = fx[4] + np.roll(fx[4], 1, 1) + fy[4] + np.roll(fy[4], 1, 0)
        co_max = max(co_max, float(np.max(0.5 * s / vol * dt)))
        rho = rho - dt / vol * (_div(fx[0], 1) + _div(fy[0], 0))
        rhoUx = rhoUx - dt / vol * (_div(fx[1], 1) + _div(fy[1], 0))
        rhoUy = rhoUy - dt / vol * (_div(fx[2], 1) + _div(fy[2], 0))
        rhoE = rhoE - dt / vol * (_div(fx[3], 1) + _div(fy[3], 0))
        u, v = rhoUx / rho, rhoUy / rho
        T = (rhoE / rho - 0.5 * (u * u + v * v)) / CV
        p = rho * R_GAS * T
    rho_ex = rho_exact(X, Y, T_END)
    E2 = float(math.sqrt(np.mean((rho - rho_ex) ** 2)))
    ke = float(np.mean(0.5 * rho * (u * u + v * v)))
    return dict(n=n, steps=steps, h=h, dt=dt, xc=X.ravel(), yc=Y.ravel(), rho=rho, u=u, v=v,
                E2_pred=E2, ke_pred=ke, ke_err_pred=ke - ke_exact(), co_max_model=co_max,
                mass=float(np.sum(rho) * vol), mass0=float(np.sum(rho_ex) * vol))


_CACHE = {}
MODEL_RUNS = ((64, 2000), (64, 4000), (128, 4000))   # (n, steps): 64^2 at dt and dt/2, 128^2 at dt
B_LEVEL = 64                                         # the Euler slope B = d(KE err)/d(dt) is read at 64^2


def model(n, steps=None):
    if steps is None:
        steps = dict((nn, s) for nn, s in MODEL_RUNS if nn == n).get(n)
        if steps is None:
            steps = dict((nn, s) for _nm, nn, s in LEVELS).get(n)
    key = (n, steps)
    if key not in _CACHE:
        if key not in MODEL_RUNS:
            refuse("model run %r is not one of the registered MODEL_RUNS; it is extrapolated" % (key,))
        _CACHE[key] = knp_model(n, steps)
    return _CACHE[key]


def decomposition():
    """KE error = S(h) + B dt.  B from the two 64^2 runs (dt and dt/2); S(h) at
    64^2 and 128^2 by subtracting B dt; the spatial order p_S from S(64)/S(128);
    the E2 order p_e2 from the two registered-dt runs."""
    if "decomp" not in _CACHE:
        m64, m64h, m128 = model(64, 2000), model(64, 4000), model(128, 4000)
        B = (m64["ke_err_pred"] - m64h["ke_err_pred"]) / (m64["dt"] - m64h["dt"])
        S64 = m64["ke_err_pred"] - B * m64["dt"]
        S128 = m128["ke_err_pred"] - B * m128["dt"]
        p_S = math.log(abs(S64) / abs(S128)) / math.log(2.0)
        p_e2 = math.log(m64["E2_pred"] / m128["E2_pred"]) / math.log(2.0)
        _CACHE["decomp"] = dict(B=B, S64=S64, S128=S128, p_S=p_S, p_e2=p_e2)
    return _CACHE["decomp"]


def predictions():
    if "table" not in _CACHE:
        d = decomposition()
        m128 = model(128, 4000)
        tab = []
        for nm, n, s in LEVELS:
            k = math.log2(n / 128.0)
            h, dt = h_of(n), dt_of(s)
            S = d["S128"] / 2.0 ** (d["p_S"] * k)
            E = d["B"] * dt
            row = dict(name=nm, n=n, cells=n * n, steps=s, h=h, dt=dt,
                       E2_pred=m128["E2_pred"] / 2.0 ** (d["p_e2"] * k),
                       ke_spatial_pred=S, ke_euler_pred=E, ke_err_pred=S + E, ke_tol_basis=abs(S) + abs(E))
            if n == 128:
                row["E2_pred"] = m128["E2_pred"]
                row["ke_err_pred"] = m128["ke_err_pred"]
                row["source"] = "integrated (E2 and KE error direct; the S + B dt split is the model's own)"
            else:
                row["source"] = ("extrapolated from the integrated 128^2 model: E2 with order %.4f; KE as "
                                 "S(h) with spatial order %.4f plus B dt, B = %.4f" % (d["p_e2"], d["p_S"], d["B"]))
            tab.append(row)
        _CACHE["table"] = tab
    return _CACHE["table"]


def model_orders():
    d = decomposition()
    return (d["p_e2"], d["p_S"])


# ---------------------------------------------------------------------------
# CONTROLS
# ---------------------------------------------------------------------------
def _sym_fields(beta_T_factor=1):
    import sympy as sp
    x, y = sp.symbols("x y", real=True)
    g = sp.Rational(7, 5)
    beta = sp.Integer(5)
    r2 = x ** 2 + y ** 2
    G = sp.exp((1 - r2) / 2)
    k = beta / (2 * sp.pi)
    up = -k * G * y
    vp = k * G * x
    T = 1 - (g - 1) * (beta * beta_T_factor) ** 2 / (8 * g * sp.pi ** 2) * G ** 2
    rho = T ** (1 / (g - 1))
    p = rho * T
    return sp, x, y, g, up, vp, T, rho, p


def control_symbolic_substitution():
    try:
        sp, x, y, g, up, vp, T, rho, p = _sym_fields()
    except ImportError:
        refuse("sympy is not importable; the exact solution cannot be verified by substitution")
    res = {
        "continuity": sp.simplify(sp.diff(rho * up, x) + sp.diff(rho * vp, y)),
        "x_momentum": sp.simplify(rho * (up * sp.diff(up, x) + vp * sp.diff(up, y)) + sp.diff(p, x)),
        "y_momentum": sp.simplify(rho * (up * sp.diff(vp, x) + vp * sp.diff(vp, y)) + sp.diff(p, y)),
        "entropy": sp.simplify(sp.powdenest(p / rho ** g, force=True) - 1),
    }
    bad = [k for k, r in res.items() if r != 0]
    if bad:
        refuse("SYMBOLIC SUBSTITUTION FAILED: residuals %s are not identically zero" % bad)
    return dict(control="symbolic_substitution_into_steady_Euler_in_the_comoving_frame",
                residuals=dict((k, str(r)) for k, r in res.items()), passed=True)


def control_substitution_is_able_to_fail():
    sp, x, y, g, up, vp, T, rho, p = _sym_fields(beta_T_factor=sp_rational_11_10())
    r = sp.simplify(rho * (up * sp.diff(up, x) + vp * sp.diff(up, y)) + sp.diff(p, x))
    if r == 0:
        refuse("PLANTED CONTROL FAILED: beta in T planted at 1.1 beta still gave zero residual")
    val = float(r.subs({x: 0.7, y: -0.3}))
    if abs(val) < 1e-6:
        refuse("PLANTED CONTROL FAILED: residual with planted beta is numerically zero at a test point")
    return dict(control="PZ-F20-BETA_planted_1.1beta_in_T_must_be_nonzero", residual_at_test_point=val, passed=True)


def sp_rational_11_10():
    import sympy as sp
    return sp.Rational(11, 10)


def control_field_returns_after_one_period():
    n = 512
    c = (np.arange(n) + 0.5) * (L_BOX / n)
    X, Y = np.meshgrid(c, c)
    f0 = fields_exact(X, Y, 0.0)
    fT = fields_exact(X, Y, T_END)
    d = max(float(np.max(np.abs(a - b))) for a, b in zip(f0, fT))
    fh = fields_exact(X, Y, 0.5 * T_END)
    dh = float(np.max(np.abs(f0[0] - fh[0])))
    if d > 1e-13:
        refuse("the field at t = T does not equal the field at t = 0 on the periodic box: max diff %.3e" % d)
    if dh < 1e-2:
        refuse("PLANTED CONTROL FAILED: the field at t = T/2 should differ from t = 0 (vortex on the opposite corner)")
    sm = seam_mismatch()
    if not (1e-6 < sm["velocity"] < 1e-4) or sm["density"] > 1e-9:
        refuse("seam mismatch is not the registered ~4.9e-5 in velocity / ~1e-11 in density: %s" % sm)
    ke1, ke2 = ke_exact(2048), ke_exact(4096)
    if abs(ke1 - ke2) > 1e-9:
        refuse("box-mean KE quadrature not converged: %.12f vs %.12f" % (ke1, ke2))
    return dict(control="field_at_T_equals_field_at_0_and_moves_at_T_over_2", max_diff_at_T=d, diff_at_half_period=dh,
                seam_mismatch=sm, ke_exact=ke2, ke_quadrature_diff=abs(ke1 - ke2), passed=True)


def control_ladder_is_geometrically_similar():
    rh = [h_of(LEVELS[i][1]) / h_of(LEVELS[i + 1][1]) for i in range(2)]
    rt = [dt_of(LEVELS[i][2]) / dt_of(LEVELS[i + 1][2]) for i in range(2)]
    if max(abs(r - 2.0) for r in rh + rt) > 1e-12:
        refuse("the ladder is not a factor-2 refinement in h and dt: %s %s" % (rh, rt))
    co = [dt_of(s) / h_of(n) for _nm, n, s in LEVELS] + [dt_of(2000) / h_of(64), dt_of(4000) / h_of(128)]
    if max(abs(c - co[0]) for c in co) > 1e-12:
        refuse("dt/h is not constant across the ladder and the registered-dt model runs: %s" % co)
    return dict(control="constant_ratio_refinement_h_and_dt", h_ratios=rh, dt_ratios=rt, dt_over_h=co[0], passed=True)


def control_model_is_forced_and_ordered():
    tab = predictions()
    d = decomposition()
    for (n, s) in MODEL_RUNS:
        m = model(n, s)
        if not (m["E2_pred"] > 0 and math.isfinite(m["E2_pred"])):
            refuse("the model returned a non-positive or non-finite E2 at %d^2 / %d steps" % (n, s))
        if abs(m["mass"] - m["mass0"]) > 1e-9:
            refuse("the model does not conserve mass at %d^2: %.15g vs %.15g" % (n, m["mass"], m["mass0"]))
        if m["co_max_model"] > CO_CEILING:
            refuse("the model's solver-convention max Courant %.4f at %d^2 exceeds the ceiling" % (m["co_max_model"], n))
    if not (1.0 <= d["p_e2"] <= 2.5):
        refuse("the model's E2 order %.3f lies outside [1.0, 2.5]" % d["p_e2"])
    if not (1.0 <= d["p_S"] <= 2.5):
        refuse("the model's spatial KE-error order %.3f lies outside [1.0, 2.5]" % d["p_S"])
    if not (d["B"] > 0 and d["S64"] < 0 and d["S128"] < 0):
        refuse("the KE decomposition is not (dissipative spatial part, anti-dissipative Euler part): B %.4g S64 %.4g S128 %.4g"
               % (d["B"], d["S64"], d["S128"]))
    fine = tab[-1]
    if not (abs(fine["ke_err_pred"]) <= fine["ke_tol_basis"]):
        refuse("the predicted fine KE error is not inside its own magnitude-sum basis")
    signs = [np.sign(r["ke_err_pred"]) for r in tab]
    return dict(control="model_forced_mass_conserving_ordered_KE_decomposed", model_orders=dict(E2=d["p_e2"], KE_spatial=d["p_S"]),
                euler_slope_B=d["B"], spatial_S=dict(n64=d["S64"], n128=d["S128"]),
                ke_err_pred=[r["ke_err_pred"] for r in tab], ke_sign_change_inside_ladder=bool(len(set(signs)) > 1),
                co_max_model=dict(("%d_%d" % k, model(*k)["co_max_model"]) for k in MODEL_RUNS), passed=True)


def selftest_predicate(controls):
    if len(controls) != 5:
        return False, "expected 5 controls, ran %d" % len(controls)
    for c in controls:
        if not c.get("passed"):
            return False, "control %s did not pass" % c.get("control")
    if not __debug__:
        return False, "running under -O"
    return True, ("5 controls green: the closed form satisfies continuity, both momentum equations and uniform "
                  "entropy identically under symbolic substitution; a planted 1.1 beta makes the residual non-zero; "
                  "the field returns to itself at t = T and differs at T/2; h and dt refine by exactly 2 at "
                  "constant dt/h; the KNP model is forced, mass-conserving, its E2 and spatial-KE orders in [1, 2.5], "
                  "and its KE error decomposes into a dissipative spatial part and an anti-dissipative Euler part")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--model-n", type=int, default=None, help="integrate the model once at N^2 (consistency check only)")
    a = ap.parse_args(argv)
    if a.model_n:
        lv = dict((n, s) for _nm, n, s in LEVELS)
        lv.update(dict(MODEL_RUNS))
        if a.model_n not in lv:
            refuse("no registered step count for %d^2" % a.model_n)
        m = knp_model(a.model_n, lv[a.model_n])
        print(json.dumps(dict(n=a.model_n, steps=lv[a.model_n], E2=m["E2_pred"], ke_err=m["ke_err_pred"],
                              co_max=m["co_max_model"], mass=m["mass"], mass0=m["mass0"])))
        return 0
    controls = [control_symbolic_substitution(), control_substitution_is_able_to_fail(),
                control_field_returns_after_one_period(), control_ladder_is_geometrically_similar(),
                control_model_is_forced_and_ordered()]
    tab = predictions()
    summary = dict(constants=dict(gamma=GAMMA, R=R_GAS, Cp=CP, Cv=CV, molWeight=MOL_WEIGHT, beta=BETA, L=L_BOX, T=T_END),
                   ke_exact=ke_exact(), seam=seam_mismatch(), levels=tab, model_orders=model_orders(), decomposition=decomposition(),
                   model_runs=dict(("%d_%d" % k, dict(E2=model(*k)["E2_pred"], ke_err=model(*k)["ke_err_pred"], co_max=model(*k)["co_max_model"]))
                                   for k in MODEL_RUNS))
    if a.json:
        print(json.dumps(dict(summary, controls=controls), indent=2))
        return 0
    ok, why = selftest_predicate(controls)
    if a.selftest:
        print(json.dumps(dict(summary, controls=controls, predicate=dict(ok=ok, why=why)), indent=2))
        if not ok:
            refuse("SELFTEST DID NOT ESTABLISH ITS CLAIM: %s" % why)
        print("\nSELFTEST GREEN -- %s" % why)
        return 0
    print("KE_exact=%.12f seam=%s" % (ke_exact(), seam_mismatch()))
    for k in MODEL_RUNS:
        m = model(*k)
        print("model %3d^2 steps=%d E2=%.6e ke_err=%+.6e co_max=%.4f" % (k[0], m["steps"], m["E2_pred"], m["ke_err_pred"], m["co_max_model"]))
    print("decomposition: %s" % decomposition())
    for r in tab:
        print("%-7s %dx%d steps=%d h=%.5g dt=%.5g  E2_pred=%.6e  KE_err_pred=%+.6e  [%s]"
              % (r["name"], r["n"], r["n"], r["steps"], r["h"], r["dt"], r["E2_pred"], r["ke_err_pred"], r["source"]))
    print("model orders: E2 %.4f, KE spatial %.4f" % model_orders())
    return 0


if __name__ == "__main__":
    sys.exit(main())
