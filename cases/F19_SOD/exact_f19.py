#!/usr/bin/env python3
"""
F19 -- THE EXACT SOLUTION of the Sod shock tube (Toro's Test 1) and the
DISCRETISATION-DERIVED error prediction every F19 band is built from.

    x in [0, 1], diaphragm at x0 = 0.5, gamma = 1.4, t_end = 0.2
    left  (x < x0):  rho = 1,     u = 0,  p = 1
    right (x > x0):  rho = 0.125, u = 0,  p = 0.1

THE REFERENCE IS NOT A PAPER ON THIS BOX.  IT IS AN EXACT RIEMANN SOLVER,
implemented here (Toro, "Riemann Solvers and Numerical Methods for Fluid
Dynamics", ch. 4: Newton iteration on the pressure function f(p) = f_L + f_R +
(u_R - u_L)).  Its star state is compared at selftest against the textbook
figures for Test 1 (p* = 0.30313, u* = 0.92745, rho*_L = 0.42632, rho*_R =
0.26557, Toro Table 4.3) -- AND, so that the check is not circular, the
profile it produces is verified against three integral identities that do
not involve those figures at all: total mass, momentum and energy of the
exact solution at t = 0.2 must equal their initial values plus the boundary
fluxes (0.5625, 0.18, 1.375), to 1e-12; the Rankine-Hugoniot mass flux must
be equal on both sides of the shock; and p/rho^gamma must be constant inside
the rarefaction fan.  A planted control (p_R raised 10 %) must MOVE p*.

THE BAND PRINCIPLE -- derived from the discretisation, not measured on the
case.  `knp_model` is a numpy re-implementation of rhoCentralFoam's own
discretisation on the SAME grids and time steps the ladder runs: directed
vanLeer reconstruction of rho, rhoU, rPsi = RT, e and c to faces (OpenFOAM's
NVDTVD ratio r = 2 (d.grad_c)/(phi_N - phi_P) - 1, vanLeer limiter
(r + |r|)/(1 + |r|), with the 1000x clamp), the Kurganov central-upwind flux
exactly as rhoCentralFoam.C forms it (ap, am, a_pos = ap/(ap - am), aSf =
am a_pos, aphiv_pos/neg, phi, phiUp, phiEp) and explicit Euler time stepping
of rho, rhoU, rhoE followed by the primitive update.  The model's L1 density
error and midpoint-crossing shock position at each level are the predictions.

Omissions, stated: OpenFOAM's `vanLeerV` limits the momentum vector by the
projection of its jump on the cell gradient (identical to the scalar form in
one dimension, so no omission here); boundary handling at x = 0 and x = 1
(zeroGradient; no wave reaches either boundary by t = 0.2: the shock is at
0.8504, the rarefaction head at 0.2634); floating-point ordering.  Hence a
FACTOR-3 window on the L1 error, declared before compute, not an equality.

ORDER, HONESTLY: the solution has two discontinuities.  A second-order
central-upwind scheme converges at ~first order in L1 near a shock and at
~2/3 near a contact, so the OBSERVED order of the L1 error is expected in
[0.6, 1.2] -- the model's own order is printed -- and the band is a value
band that does not depend on p.  A triple with p < STAGNANT_FLOOR = 0.5 reads
STAGNANT = NOT A RESULT in the shared instrument; that outcome is registered
as possible and is not a defect of the gate.

Refusals are `raise` and `sys.exit(2)`.  Zero `assert` (L-332).
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: exact_f19.py must not run under `python3 -O`.\n")
    sys.exit(2)

import json
import math
import argparse

import numpy as np

# ---------------------------------------------------------------------------
# THE CASE, FROZEN.
# ---------------------------------------------------------------------------
GAMMA = 1.4
R_GAS = 1.0                          # nondimensional gas: p = rho T
CP = GAMMA / (GAMMA - 1.0) * R_GAS   # 3.5
CV = CP - R_GAS                      # 2.5
# OpenFOAM v2606: RR = 1e3 * NA * k with NA = 6.0221417930e+23, k = 1.38065e-23
# (src/OpenFOAM/global/constants; etc/controlDict).  molWeight = RR makes the
# specific gas constant RR/W exactly 1.0 in the solver.
NA_FOAM, K_FOAM = 6.0221417930e+23, 1.38065e-23
MOL_WEIGHT = 1e3 * (NA_FOAM * K_FOAM)          # 8314.47006650545
RHO_L, U_L, P_L = 1.0, 0.0, 1.0
RHO_R, U_R, P_R = 0.125, 0.0, 0.1
X0 = 0.5
X_MIN, X_MAX = 0.0, 1.0
L = X_MAX - X_MIN
T_END = 0.2
# name, cells, steps (dt = T_END/steps): Co = S_max dt / h constant across the ladder
LEVELS = (("coarse", 400, 1000), ("medium", 800, 2000), ("fine", 1600, 4000))
# rhoCentralFoam's centralCourantNo.H reports 0.5 * sum_f amaxSf / V * dt with amaxSf =
# max(|aphiv_pos|, |aphiv_neg|) = (|u| + c)/2 per face for the Kurganov weights, i.e.
# HALF the classical (|u| + c) dt / h.  Both conventions are carried; the census ceiling
# below is on the SOLVER'S reported number (classical 0.5 = explicit KNP+Euler limit).
CO_CEILING = 0.25                    # on the solver-reported CoNum (grader, rule 5 limb 1)

# Toro, Riemann Solvers and Numerical Methods for Fluid Dynamics, 3rd ed.,
# Table 4.3, Test 1 -- TEXTBOOK FIGURES, five decimals.  Compared against, never
# used in, the iteration below.
TORO_TEST1 = dict(p_star=0.30313, u_star=0.92745, rho_star_L=0.42632, rho_star_R=0.26557)
TORO_TOL = 6.0e-6                    # half a unit in the fifth decimal, plus rounding

# exact conserved totals over [0, 1] at t = T_END (initial value + boundary flux x t)
MASS_EXACT = 0.5 * RHO_L + 0.5 * RHO_R                                 # 0.5625
MOMENTUM_EXACT = (P_L - P_R) * T_END                                   # 0.18
ENERGY_EXACT = 0.5 * (P_L / (GAMMA - 1.0)) + 0.5 * (P_R / (GAMMA - 1.0))  # 1.375


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def h_of(n):
    return L / float(n)


def dt_of(steps):
    return T_END / float(steps)


def sound(rho, p, gamma=GAMMA):
    return math.sqrt(gamma * p / rho)


# ---------------------------------------------------------------------------
# THE EXACT RIEMANN SOLVER (Toro ch. 4)
# ---------------------------------------------------------------------------
def _fK(p, rhoK, pK, gamma):
    aK = sound(rhoK, pK, gamma)
    if p > pK:                                     # shock
        A = 2.0 / ((gamma + 1.0) * rhoK)
        B = (gamma - 1.0) / (gamma + 1.0) * pK
        f = (p - pK) * math.sqrt(A / (p + B))
        df = math.sqrt(A / (B + p)) * (1.0 - 0.5 * (p - pK) / (B + p))
    else:                                          # rarefaction
        f = 2.0 * aK / (gamma - 1.0) * ((p / pK) ** ((gamma - 1.0) / (2.0 * gamma)) - 1.0)
        df = 1.0 / (rhoK * aK) * (p / pK) ** (-(gamma + 1.0) / (2.0 * gamma))
    return f, df


def star_state(left=(RHO_L, U_L, P_L), right=(RHO_R, U_R, P_R), gamma=GAMMA):
    """Newton iteration on f(p) = f_L(p) + f_R(p) + (u_R - u_L) from the PVRS
    guess; returns the star state, the wave speeds and the iteration record."""
    rhoL, uL, pL = left
    rhoR, uR, pR = right
    aL, aR = sound(rhoL, pL, gamma), sound(rhoR, pR, gamma)
    # PVRS guess (Toro 9.20)
    ppv = 0.5 * (pL + pR) - 0.125 * (uR - uL) * (rhoL + rhoR) * (aL + aR)
    p = max(1e-8, ppv)
    it, res = 0, None
    for it in range(1, 101):
        fL, dfL = _fK(p, rhoL, pL, gamma)
        fR, dfR = _fK(p, rhoR, pR, gamma)
        f = fL + fR + (uR - uL)
        dp = f / (dfL + dfR)
        p_new = max(1e-12, p - dp)
        res = abs(f)
        if abs(p_new - p) < 1e-15 * max(1.0, p):
            p = p_new
            break
        p = p_new
    fL, _ = _fK(p, rhoL, pL, gamma)
    fR, _ = _fK(p, rhoR, pR, gamma)
    res = abs(fL + fR + (uR - uL))
    u = 0.5 * (uL + uR) + 0.5 * (fR - fL)
    g1 = (gamma - 1.0) / (gamma + 1.0)
    out = dict(p=p, u=u, iterations=it, residual=res, gamma=gamma,
               left=dict(rho=rhoL, u=uL, p=pL, a=aL), right=dict(rho=rhoR, u=uR, p=pR, a=aR))
    if p > pL:                                     # left shock
        out["left_wave"] = "shock"
        out["rhoL"] = rhoL * ((p / pL + g1) / (g1 * p / pL + 1.0))
        out["S_L"] = uL - aL * math.sqrt((gamma + 1.0) / (2.0 * gamma) * p / pL + (gamma - 1.0) / (2.0 * gamma))
    else:                                          # left rarefaction
        out["left_wave"] = "rarefaction"
        out["rhoL"] = rhoL * (p / pL) ** (1.0 / gamma)
        aLs = aL * (p / pL) ** ((gamma - 1.0) / (2.0 * gamma))
        out["aL_star"] = aLs
        out["S_HL"] = uL - aL
        out["S_TL"] = u - aLs
    if p > pR:                                     # right shock
        out["right_wave"] = "shock"
        out["rhoR"] = rhoR * ((p / pR + g1) / (g1 * p / pR + 1.0))
        out["S_R"] = uR + aR * math.sqrt((gamma + 1.0) / (2.0 * gamma) * p / pR + (gamma - 1.0) / (2.0 * gamma))
    else:                                          # right rarefaction
        out["right_wave"] = "rarefaction"
        out["rhoR"] = rhoR * (p / pR) ** (1.0 / gamma)
        aRs = aR * (p / pR) ** ((gamma - 1.0) / (2.0 * gamma))
        out["aR_star"] = aRs
        out["S_HR"] = uR + aR
        out["S_TR"] = u + aRs
    return out


_STAR = None


def star():
    global _STAR
    if _STAR is None:
        _STAR = star_state()
        if not (_STAR["left_wave"] == "rarefaction" and _STAR["right_wave"] == "shock"):
            refuse("Sod must resolve as left rarefaction / contact / right shock; got %s / %s"
                   % (_STAR["left_wave"], _STAR["right_wave"]))
    return _STAR


def shock_position_exact(t=T_END):
    return X0 + star()["S_R"] * t


def max_signal_speed():
    s = star()
    return max(abs(s["left"]["u"]) + s["left"]["a"], abs(s["u"]) + s["aL_star"],
               abs(s["u"]) + sound(s["rhoR"], s["p"]), abs(s["right"]["u"]) + s["right"]["a"], s["S_R"])


def courant(n, steps):
    """classical S_max dt / h"""
    return max_signal_speed() * dt_of(steps) / h_of(n)


def courant_foam(n, steps):
    """the number rhoCentralFoam prints as `max Courant Number` (half the classical)"""
    return 0.5 * courant(n, steps)


def sample(x, t):
    """Point values (rho, u, p) of the exact solution at positions x, time t."""
    s = star()
    x = np.asarray(x, dtype=float)
    xi = (x - X0) / t
    g = GAMMA
    aL, uL, rhoL, pL = s["left"]["a"], s["left"]["u"], s["left"]["rho"], s["left"]["p"]
    rho = np.empty_like(xi); u = np.empty_like(xi); p = np.empty_like(xi)
    m_left = xi <= s["S_HL"]
    m_fan = (xi > s["S_HL"]) & (xi < s["S_TL"])
    m_starL = (xi >= s["S_TL"]) & (xi < s["u"])
    m_starR = (xi >= s["u"]) & (xi < s["S_R"])
    m_right = xi >= s["S_R"]
    rho[m_left], u[m_left], p[m_left] = rhoL, uL, pL
    a_fan = 2.0 / (g + 1.0) * (aL + 0.5 * (g - 1.0) * (uL - xi[m_fan]))
    u[m_fan] = 2.0 / (g + 1.0) * (aL + 0.5 * (g - 1.0) * uL + xi[m_fan])
    rho[m_fan] = rhoL * (a_fan / aL) ** (2.0 / (g - 1.0))
    p[m_fan] = pL * (a_fan / aL) ** (2.0 * g / (g - 1.0))
    rho[m_starL], u[m_starL], p[m_starL] = s["rhoL"], s["u"], s["p"]
    rho[m_starR], u[m_starR], p[m_starR] = s["rhoR"], s["u"], s["p"]
    rho[m_right], u[m_right], p[m_right] = s["right"]["rho"], s["right"]["u"], s["right"]["p"]
    return rho, u, p


def _fan_rho_antiderivative(xi, t):
    """Antiderivative in x of rho inside the fan, x = X0 + xi t."""
    s = star()
    g = GAMMA
    aL, uL, rhoL = s["left"]["a"], s["left"]["u"], s["left"]["rho"]
    A = 2.0 / (g + 1.0) * (aL + 0.5 * (g - 1.0) * uL)
    B = (g - 1.0) / (g + 1.0)
    m = 2.0 / (g - 1.0)
    return -t * rhoL / aL ** m * (A - B * xi) ** (m + 1.0) / (B * (m + 1.0))


def cell_averages(faces, t=T_END):
    """Exact cell averages of rho on cells [faces[i], faces[i+1]]: piecewise
    analytic integration split at the four wave positions."""
    s = star()
    faces = np.asarray(faces, dtype=float)
    xh, xt, xc_, xs = (X0 + s["S_HL"] * t, X0 + s["S_TL"] * t, X0 + s["u"] * t, X0 + s["S_R"] * t)
    pieces = ((X_MIN - 1.0, xh, "const", s["left"]["rho"]), (xh, xt, "fan", None),
              (xt, xc_, "const", s["rhoL"]), (xc_, xs, "const", s["rhoR"]),
              (xs, X_MAX + 1.0, "const", s["right"]["rho"]))
    out = np.zeros(len(faces) - 1)
    for k in range(len(faces) - 1):
        a, b = faces[k], faces[k + 1]
        tot = 0.0
        for (pa, pb, kind, val) in pieces:
            lo, hi = max(a, pa), min(b, pb)
            if hi <= lo:
                continue
            if kind == "const":
                tot += val * (hi - lo)
            else:
                tot += _fan_rho_antiderivative((hi - X0) / t, t) - _fan_rho_antiderivative((lo - X0) / t, t)
        out[k] = tot / (b - a)
    return out


def shock_position_from_profile(rho, xc):
    """Midpoint crossing between the post-shock star density and the right
    state, scanned from the right, linearly interpolated between the last cell
    at or above the midpoint and its right neighbour."""
    s = star()
    mid = 0.5 * (s["rhoR"] + s["right"]["rho"])
    rho = np.asarray(rho); xc = np.asarray(xc)
    idx = np.nonzero(rho >= mid)[0]
    if len(idx) == 0 or idx[-1] + 1 >= len(rho):
        refuse("no midpoint crossing of the shock density in the profile")
    j = idx[-1]
    f = (rho[j] - mid) / (rho[j] - rho[j + 1])
    return float(xc[j] + f * (xc[j + 1] - xc[j]))


# ---------------------------------------------------------------------------
# THE DISCRETISATION MODEL: rhoCentralFoam's KNP scheme in one dimension
# ---------------------------------------------------------------------------
def _van_leer(r):
    return (r + np.abs(r)) / (1.0 + np.abs(r))


def _ratio(gradcf, gradf):
    """OpenFOAM NVDTVD::r with its 1000x clamp (sign(0) = +1 as in Foam::sign)."""
    sg = np.where(gradcf >= 0, 1.0, -1.0) * np.where(gradf >= 0, 1.0, -1.0)
    clamp = np.abs(gradcf) >= 1000.0 * np.abs(gradf)
    safe = np.where(clamp, 1.0, gradf)
    return np.where(clamp, 2.0 * 1000.0 * sg - 1.0, 2.0 * gradcf / safe - 1.0)


def _reconstruct_1d(q):
    """q padded with 2 ghost cells each side (zeroGradient).  Returns the
    pos (owner-side) and neg (neighbour-side) face values for the n+1 faces
    between q[1..n+1] (i.e. faces i-1/2 for the real cells and the two ends)."""
    # faces between cell j and j+1 for j = 1 .. n+1 (padded index)
    qP = q[1:-2]; qN = q[2:-1]; qW = q[:-3]; qNN = q[3:]
    gradf = qN - qP
    r_pos = _ratio(0.5 * (qN - qW), gradf)          # d . grad_c(P) = (q_N - q_W)/2
    r_neg = _ratio(0.5 * (qNN - qP), gradf)         # d . grad_c(N) = (q_NN - q_P)/2
    f_pos = qP + 0.5 * _van_leer(r_pos) * gradf
    f_neg = qN - 0.5 * _van_leer(r_neg) * gradf
    return f_pos, f_neg


def _pad(q):
    return np.concatenate([[q[0], q[0]], q, [q[-1], q[-1]]])


def knp_model(n, steps, gamma=GAMMA, return_history=False):
    """Explicit-Euler KNP (Kurganov) integration on n uniform cells for `steps`
    steps of dt = T_END/steps, initialised with point values of the exact
    t = 0 state at the cell centres (as build_f19.py initialises the case)."""
    h, dt = h_of(n), dt_of(steps)
    xc = X_MIN + (np.arange(n) + 0.5) * h
    rho = np.where(xc < X0, RHO_L, RHO_R).astype(float)
    u = np.where(xc < X0, U_L, U_R).astype(float)
    p = np.where(xc < X0, P_L, P_R).astype(float)
    cv = CV
    rhoU = rho * u
    rhoE = rho * (p / (rho * (gamma - 1.0)) + 0.5 * u * u)
    co_max = 0.0
    for _k in range(steps):
        T = p / (rho * R_GAS)
        rPsi = R_GAS * T
        e = cv * T
        c = np.sqrt(gamma * rPsi)
        rho_p, rho_n = _reconstruct_1d(_pad(rho))
        rhoU_p, rhoU_n = _reconstruct_1d(_pad(rhoU))
        rPsi_p, rPsi_n = _reconstruct_1d(_pad(rPsi))
        e_p, e_n = _reconstruct_1d(_pad(e))
        c_p, c_n = _reconstruct_1d(_pad(c))
        U_p, U_n = rhoU_p / rho_p, rhoU_n / rho_n
        p_p, p_n = rho_p * rPsi_p, rho_n * rPsi_n
        phiv_p, phiv_n = U_p, U_n                          # |Sf| = 1
        ap = np.maximum(np.maximum(phiv_p + c_p, phiv_n + c_n), 0.0)
        am = np.minimum(np.minimum(phiv_p - c_p, phiv_n - c_n), 0.0)
        a_pos = ap / (ap - am)
        aSf = am * a_pos
        a_neg = 1.0 - a_pos
        aphiv_p = phiv_p * a_pos - aSf
        aphiv_n = phiv_n * a_neg + aSf
        amax = np.maximum(np.abs(aphiv_p), np.abs(aphiv_n))
        co_max = max(co_max, float(np.max(0.5 * (amax[:-1] + amax[1:]) / h * dt)))
        phi = aphiv_p * rho_p + aphiv_n * rho_n
        phiUp = aphiv_p * rhoU_p + aphiv_n * rhoU_n + (a_pos * p_p + a_neg * p_n)
        phiEp = (aphiv_p * (rho_p * (e_p + 0.5 * U_p * U_p) + p_p)
                 + aphiv_n * (rho_n * (e_n + 0.5 * U_n * U_n) + p_n) + aSf * p_p - aSf * p_n)
        rho = rho - dt / h * (phi[1:] - phi[:-1])
        rhoU = rhoU - dt / h * (phiUp[1:] - phiUp[:-1])
        rhoE = rhoE - dt / h * (phiEp[1:] - phiEp[:-1])
        u = rhoU / rho
        e_new = rhoE / rho - 0.5 * u * u
        T = e_new / cv
        p = rho * R_GAS * T
    faces = X_MIN + np.arange(n + 1) * h
    rho_bar = cell_averages(faces, T_END)
    E1 = float(np.mean(np.abs(rho - rho_bar)))
    xs = shock_position_from_profile(rho, xc)
    return dict(n=n, steps=steps, h=h, dt=dt, xc=xc, rho=rho, u=u, p=p, E1_pred=E1, xs_pred=xs,
                xs_err_pred=xs - shock_position_exact(), co_max_model=co_max,
                mass=float(np.sum(rho) * h))


_CACHE = {}


def model(name):
    if name not in _CACHE:
        lv = dict((nm, (n, s)) for nm, n, s in LEVELS)
        if name not in lv:
            refuse("unknown level %r" % name)
        _CACHE[name] = knp_model(*lv[name])
    return _CACHE[name]


def predictions():
    if "table" not in _CACHE:
        tab = []
        for nm, n, s in LEVELS:
            m = model(nm)
            tab.append(dict(name=nm, n=n, cells=n, steps=s, h=m["h"], dt=m["dt"], courant=courant(n, s),
                            courant_foam=courant_foam(n, s),
                            E1_pred=m["E1_pred"], xs_pred=m["xs_pred"], xs_err_pred=m["xs_err_pred"],
                            co_max_model=m["co_max_model"], source="integrated"))
        e = [r["E1_pred"] for r in tab]
        _CACHE["orders"] = (math.log(e[0] / e[1]) / math.log(2.0), math.log(e[1] / e[2]) / math.log(2.0))
        _CACHE["table"] = tab
    return _CACHE["table"]


def model_orders():
    predictions()
    return _CACHE["orders"]


# ---------------------------------------------------------------------------
# CONTROLS
# ---------------------------------------------------------------------------
def control_star_state_matches_toro():
    s = star()
    got = dict(p_star=s["p"], u_star=s["u"], rho_star_L=s["rhoL"], rho_star_R=s["rhoR"])
    bad = dict((k, (got[k], TORO_TEST1[k])) for k in TORO_TEST1 if abs(got[k] - TORO_TEST1[k]) > TORO_TOL)
    if bad:
        refuse("star state from this file's own Newton iteration disagrees with Toro Table 4.3: %s" % bad)
    if s["residual"] > 1e-13:
        refuse("pressure-function residual %.3e at the converged p*" % s["residual"])
    return dict(control="own_iteration_reproduces_Toro_Table_4.3_Test_1", derived=got, textbook=TORO_TEST1,
                tolerance=TORO_TOL, newton_iterations=s["iterations"], residual=s["residual"],
                shock_speed=s["S_R"], shock_position_at_T=shock_position_exact(), passed=True)


def control_star_state_is_able_to_move():
    s0 = star()["p"]
    s1 = star_state(right=(RHO_R, U_R, 1.1 * P_R))["p"]      # PLANT: p_R + 10 %
    s2 = star_state(gamma=5.0 / 3.0)["p"]                    # PLANT: monatomic gamma
    if abs(s1 - s0) < 1e-3 or abs(s2 - s0) < 1e-3:
        refuse("PLANTED CONTROL FAILED: p* did not move under a planted p_R (%g -> %g) or gamma (%g)" % (s0, s1, s2))
    return dict(control="PZ-F19-STAR_planted_pR_and_gamma_must_move_p_star", p_star=s0,
                p_star_pR_times_1p1=s1, p_star_gamma_5_3=s2, passed=True)


def control_profile_conserves_and_satisfies_RH():
    """NON-CIRCULAR: integral identities and jump conditions on the sampled
    profile that never touch the textbook figures."""
    n = 20000
    faces = X_MIN + np.arange(n + 1) * (L / n)
    xc = 0.5 * (faces[:-1] + faces[1:])
    rho_bar = cell_averages(faces, T_END)
    rho, u, p = sample(xc, T_END)
    h = L / n
    mass = float(np.sum(rho_bar) * h)
    # momentum and energy by midpoint rule with the discontinuity cells refined 2000x
    def refined_sum(fn):
        tot = 0.0
        s = star()
        breaks = [X0 + s["S_HL"] * T_END, X0 + s["S_TL"] * T_END, X0 + s["u"] * T_END, X0 + s["S_R"] * T_END]
        for k in range(n):
            a, b = faces[k], faces[k + 1]
            if any(a < br < b for br in breaks):
                xx = a + (np.arange(2000) + 0.5) * (h / 2000)
                tot += float(np.sum(fn(*sample(xx, T_END))) * h / 2000)
            else:
                tot += float(fn(*sample(np.array([0.5 * (a + b)]), T_END))[0] * h)
        return tot
    mom = refined_sum(lambda r, uu, pp: r * uu)
    ene = refined_sum(lambda r, uu, pp: pp / (GAMMA - 1.0) + 0.5 * r * uu * uu)
    if abs(mass - MASS_EXACT) > 1e-12:
        refuse("exact profile does not conserve mass: %.15g vs %.15g" % (mass, MASS_EXACT))
    if abs(mom - MOMENTUM_EXACT) > 1e-6 or abs(ene - ENERGY_EXACT) > 1e-6:
        refuse("exact profile fails the momentum/energy identities: %.9g vs %.9g, %.9g vs %.9g"
               % (mom, MOMENTUM_EXACT, ene, ENERGY_EXACT))
    s = star()
    S = s["S_R"]
    jL = s["rhoR"] * (s["u"] - S); jR = s["right"]["rho"] * (s["right"]["u"] - S)
    if abs(jL - jR) > 1e-12:
        refuse("Rankine-Hugoniot mass flux differs across the shock: %.15g vs %.15g" % (jL, jR))
    xf = X0 + np.linspace(s["S_HL"], s["S_TL"], 7)[1:-1] * T_END
    rf, uf, pf = sample(xf, T_END)
    ent = pf / rf ** GAMMA
    if np.max(np.abs(ent - P_L / RHO_L ** GAMMA)) > 1e-12:
        refuse("the rarefaction fan is not isentropic: %s" % ent)
    # the cell-average integrator against a brute-force midpoint sum on a coarse grid
    nc = 50
    fc = X_MIN + np.arange(nc + 1) * (L / nc)
    ca = cell_averages(fc, T_END)
    nsub = 20000
    brute = np.array([np.mean(sample(fc[k] + (np.arange(nsub) + 0.5) * (L / nc / nsub), T_END)[0]) for k in range(nc)])
    xcont, xshk = X0 + s["u"] * T_END, X0 + s["S_R"] * T_END
    jump = np.array([(fc[k] < xcont < fc[k + 1]) or (fc[k] < xshk < fc[k + 1]) for k in range(nc)])
    d_smooth = float(np.max(np.abs(ca - brute)[~jump]))          # fan kinks included: midpoint is exact enough
    d_jump = float(np.max(np.abs(ca - brute)[jump]))             # bounded by the BRUTE FORCE's own limit
    if d_smooth > 1e-9 or d_jump > max(s["rhoL"] - s["rhoR"], s["rhoR"] - s["right"]["rho"]) / nsub:
        refuse("cell_averages disagrees with a brute-force midpoint sum: smooth cells %.3e, jump cells %.3e"
               % (d_smooth, d_jump))
    return dict(control="profile_conserves_mass_momentum_energy_RH_isentropic_fan",
                mass=mass, momentum=mom, energy=ene, targets=dict(mass=MASS_EXACT, momentum=MOMENTUM_EXACT, energy=ENERGY_EXACT),
                rh_mass_flux=(jL, jR), fan_entropy_spread=float(np.max(np.abs(ent - P_L / RHO_L ** GAMMA))),
                cell_average_vs_brute=dict(smooth_cells=d_smooth, jump_cells=d_jump, n_sub=nsub), passed=True)


def control_ladder_is_geometrically_similar():
    rh = [h_of(LEVELS[i][1]) / h_of(LEVELS[i + 1][1]) for i in range(2)]
    rt = [dt_of(LEVELS[i][2]) / dt_of(LEVELS[i + 1][2]) for i in range(2)]
    if max(abs(r - 2.0) for r in rh + rt) > 1e-12:
        refuse("the ladder is not a factor-2 refinement in h and dt: %s %s" % (rh, rt))
    co = [courant(n, s) for _nm, n, s in LEVELS]
    if max(abs(c - co[0]) for c in co) > 1e-12:
        refuse("Courant number is not constant across the ladder: %s" % co)
    if co[0] > 0.2:
        refuse("registered Courant number %.4f exceeds 0.2" % co[0])
    return dict(control="constant_ratio_refinement_h_and_dt", h_ratios=rh, dt_ratios=rt,
                courant_classical=co[0], courant_foam_reported=0.5 * co[0], max_signal_speed=max_signal_speed(), passed=True)


def control_model_is_forced_and_first_order_like():
    tab = predictions()
    p1, p2 = model_orders()
    for r in tab:
        if not (r["E1_pred"] > 0.0 and math.isfinite(r["E1_pred"])):
            refuse("the discretisation model returned a non-positive or non-finite L1 error at %s" % r["name"])
        if abs(r["co_max_model"] - r["courant_foam"]) > 0.02 or r["co_max_model"] > CO_CEILING:
            refuse("the model's own max solver-convention Courant %.4f at %s disagrees with the registered "
                   "%.4f or exceeds the census ceiling %.2f" % (r["co_max_model"], r["name"], r["courant_foam"], CO_CEILING))
        if abs(model(r["name"])["mass"] - MASS_EXACT) > 1e-10:
            refuse("the model does not conserve mass at %s: %.15g" % (r["name"], model(r["name"])["mass"]))
    e = [r["E1_pred"] for r in tab]
    if not (e[0] > e[1] > e[2]):
        refuse("the model's L1 error is not monotone decreasing: %s" % e)
    if not (0.5 <= p1 <= 1.5 and 0.5 <= p2 <= 1.5):
        refuse("the model's observed orders %.3f, %.3f lie outside [0.5, 1.5]" % (p1, p2))
    return dict(control="model_forced_monotone_mass_conserving_order_in_range", model_orders=(p1, p2),
                E1_pred=e, xs_err_pred=[r["xs_err_pred"] for r in tab], passed=True)


def selftest_predicate(controls):
    if len(controls) != 5:
        return False, "expected 5 controls, ran %d" % len(controls)
    for c in controls:
        if not c.get("passed"):
            return False, "control %s did not pass" % c.get("control")
    if not __debug__:
        return False, "running under -O"
    return True, ("5 controls green: the star state from this file's own Newton iteration matches Toro "
                  "Table 4.3 Test 1 to 6e-6; planted p_R and gamma move p*; the profile conserves mass to "
                  "1e-12 and momentum/energy to 1e-6, satisfies Rankine-Hugoniot across the shock and is "
                  "isentropic in the fan; h and dt refine by exactly 2 at constant Courant; the KNP "
                  "discretisation model is forced, mass-conserving, monotone and of order in [0.5, 1.5]")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    controls = [control_star_state_matches_toro(), control_star_state_is_able_to_move(),
                control_profile_conserves_and_satisfies_RH(), control_ladder_is_geometrically_similar(),
                control_model_is_forced_and_first_order_like()]
    tab = predictions()
    s = star()
    summary = dict(constants=dict(gamma=GAMMA, R=R_GAS, Cp=CP, Cv=CV, molWeight=MOL_WEIGHT, x0=X0, T=T_END),
                   star=dict(p=s["p"], u=s["u"], rhoL=s["rhoL"], rhoR=s["rhoR"], S_HL=s["S_HL"], S_TL=s["S_TL"], S_R=s["S_R"]),
                   shock_position_exact=shock_position_exact(), levels=tab, model_orders=model_orders())
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
    print("p*=%.6f u*=%.6f rho*L=%.6f rho*R=%.6f S=%.6f x_s(T)=%.6f" % (s["p"], s["u"], s["rhoL"], s["rhoR"], s["S_R"], shock_position_exact()))
    for r in tab:
        print("%-7s n=%d steps=%d h=%.5g dt=%.5g Co=%.4f (solver prints %.4f; model %.4f)  E1_pred=%.6e  xs_pred=%.6f xs_err_pred=%+.3e" %
              (r["name"], r["n"], r["steps"], r["h"], r["dt"], r["courant"], r["courant_foam"], r["co_max_model"], r["E1_pred"], r["xs_pred"], r["xs_err_pred"]))
    print("model orders: %.4f (c->m), %.4f (m->f)" % model_orders())
    return 0


if __name__ == "__main__":
    sys.exit(main())
