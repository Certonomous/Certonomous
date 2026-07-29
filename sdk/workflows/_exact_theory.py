"""Closed-form compressible-flow reference relations shared by the supersonic
and hypersonic acts (oblique-shock wedge, Taylor-Maccoll cone, shock-expansion
diamond airfoil, Billig blunt-body standoff, and the Roshko/Williamson
Strouhal correlation for the vortex-shedding cylinder).

gamma = 1.4 (air) throughout. Ported verbatim from the exact-theory modules
validated in the F3 (supersonic exact-theory) and F4 (hypersonic blunt-body)
campaigns -- no CFD output is used anywhere in this file, and nothing here is
re-derived or loosened from what those campaigns already checked against
published sources (Anderson, "Fundamentals of Aerodynamics" / "Hypersonic and
High-Temperature Gas Dynamics"; NASA GRC's analytic oblique-shock and cone10
validation pages; Roshko 1954 / Williamson 1996 for the cylinder wake).
"""

from __future__ import annotations

import math

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

GAMMA = 1.4


# ---------------------------------------------------------------------------
# Normal shock
# ---------------------------------------------------------------------------
def normal_shock(M1n: float, gamma: float = GAMMA) -> dict:
    g = gamma
    p2_p1 = 1 + 2 * g / (g + 1) * (M1n**2 - 1)
    rho2_rho1 = (g + 1) * M1n**2 / ((g - 1) * M1n**2 + 2)
    T2_T1 = p2_p1 / rho2_rho1
    M2n = math.sqrt((1 + (g - 1) / 2 * M1n**2) / (g * M1n**2 - (g - 1) / 2))
    p02_p01 = (((g + 1) * M1n**2 / ((g - 1) * M1n**2 + 2)) ** (g / (g - 1))) * \
              ((g + 1) / (2 * g * M1n**2 - (g - 1))) ** (1 / (g - 1))
    return dict(M1n=M1n, M2n=M2n, p2_p1=p2_p1, rho2_rho1=rho2_rho1,
                T2_T1=T2_T1, p02_p01=p02_p01)


# ---------------------------------------------------------------------------
# theta-beta-M (oblique shock on a 2D wedge)
# ---------------------------------------------------------------------------
def theta_from_beta(M1: float, beta: float, gamma: float = GAMMA) -> float:
    g = gamma
    num = M1**2 * math.sin(beta) ** 2 - 1
    den = M1**2 * (g + math.cos(2 * beta)) + 2
    tan_theta = 2 / math.tan(beta) * num / den
    return math.atan(tan_theta)


def beta_max_theta(M1: float, gamma: float = GAMMA) -> tuple[float, float]:
    mu = math.asin(1 / M1)
    betas = np.linspace(mu + 1e-6, np.pi / 2 - 1e-9, 20000)
    thetas = np.array([theta_from_beta(M1, b, gamma) for b in betas])
    i = int(np.argmax(thetas))
    return float(betas[i]), float(thetas[i])


def beta_from_theta(M1: float, theta: float, gamma: float = GAMMA,
                    weak: bool = True) -> float:
    mu = math.asin(1 / M1)
    beta_md, theta_md = beta_max_theta(M1, gamma)
    if theta >= theta_md:
        raise ValueError(
            f"theta={math.degrees(theta):.3f} deg exceeds max attached "
            f"deflection {math.degrees(theta_md):.3f} deg at M1={M1}: "
            f"shock would detach")
    f = lambda b: theta_from_beta(M1, b, gamma) - theta
    lo, hi = (mu + 1e-8, beta_md) if weak else (beta_md, np.pi / 2 - 1e-8)
    return brentq(f, lo, hi, xtol=1e-12, rtol=1e-14)


def oblique_shock(M1: float, beta: float, gamma: float = GAMMA) -> dict:
    theta = theta_from_beta(M1, beta, gamma)
    M1n = M1 * math.sin(beta)
    ns = normal_shock(M1n, gamma)
    M2n = ns["M2n"]
    M2 = M2n / math.sin(beta - theta)
    out = dict(M1=M1, beta=beta, theta=theta, M2=M2)
    out.update(ns)
    return out


# ---------------------------------------------------------------------------
# Prandtl-Meyer function and its inverse
# ---------------------------------------------------------------------------
def prandtl_meyer(M: float, gamma: float = GAMMA) -> float:
    g = gamma
    k = math.sqrt((g + 1) / (g - 1))
    return k * math.atan(math.sqrt(M**2 - 1) / k) - math.atan(math.sqrt(M**2 - 1))


def inverse_prandtl_meyer(nu: float, gamma: float = GAMMA, M_hi: float = 50.0) -> float:
    f = lambda M: prandtl_meyer(M, gamma) - nu
    return brentq(f, 1.0 + 1e-10, M_hi, xtol=1e-13, rtol=1e-14)


# ---------------------------------------------------------------------------
# Taylor-Maccoll axisymmetric cone flow (shooting method)
# ---------------------------------------------------------------------------
def _tm_rhs(theta, y, gamma):
    Vr, Vt = y
    a2 = (gamma - 1) / 2 * (1 - Vr**2 - Vt**2)
    dVr = Vt
    num = Vr * Vt**2 - a2 * (2 * Vr + Vt / math.tan(theta))
    den = a2 - Vt**2
    dVt = num / den
    return [dVr, dVt]


def _shock_start_state(M1: float, beta: float, gamma: float = GAMMA) -> tuple[float, float]:
    g = gamma
    theta_defl = theta_from_beta(M1, beta, gamma)
    M1n = M1 * math.sin(beta)
    ns = normal_shock(M1n, gamma)
    M2n = ns["M2n"]
    M2 = M2n / math.sin(beta - theta_defl)
    Vmax_over_V2 = math.sqrt(1 + 2 / ((g - 1) * M2**2))
    Vprime2 = 1.0 / Vmax_over_V2
    flow_angle_from_axis = theta_defl
    Vr = Vprime2 * math.cos(beta - flow_angle_from_axis)
    Vt = -Vprime2 * math.sin(beta - flow_angle_from_axis)
    return Vr, Vt


def taylor_maccoll_shoot(M1: float, beta: float, gamma: float = GAMMA):
    Vr0, Vt0 = _shock_start_state(M1, beta, gamma)

    def event_Vt_zero(theta, y, gamma):
        return y[1]
    event_Vt_zero.terminal = True
    event_Vt_zero.direction = 1

    sol = solve_ivp(_tm_rhs, [beta, 1e-4], [Vr0, Vt0], args=(gamma,),
                    events=event_Vt_zero, max_step=1e-4, rtol=1e-12,
                    atol=1e-13, dense_output=False)
    if len(sol.t_events[0]) == 0:
        return None
    theta_c = sol.t_events[0][0]
    Vr_c = sol.y_events[0][0][0]
    a2_c = (gamma - 1) / 2 * (1 - Vr_c**2)
    M_c = Vr_c / math.sqrt(a2_c)
    return theta_c, Vr_c, M_c


def taylor_maccoll_solve(M1: float, theta_c_target_rad: float, gamma: float = GAMMA) -> dict:
    mu = math.asin(1 / M1)

    def f(beta):
        res = taylor_maccoll_shoot(M1, beta, gamma)
        if res is None:
            return -1.0
        theta_c, _, _ = res
        return theta_c - theta_c_target_rad

    lo, hi = mu + 1e-5, np.pi / 2 - 1e-6
    betas = np.linspace(lo, hi, 400)
    prev_b, prev_v, bracket = None, None, None
    for b in betas:
        v = f(b)
        if prev_v is not None and np.sign(v) != np.sign(prev_v) and prev_v != -1.0:
            bracket = (prev_b, b)
            break
        prev_b, prev_v = b, v
    if bracket is None:
        raise RuntimeError("could not bracket the Taylor-Maccoll shock angle")
    beta = brentq(f, bracket[0], bracket[1], xtol=1e-10, rtol=1e-12)

    theta_c, Vr_c, M_c = taylor_maccoll_shoot(M1, beta, gamma)
    M1n = M1 * math.sin(beta)
    ns = normal_shock(M1n, gamma)
    theta_defl = theta_from_beta(M1, beta, gamma)
    M2n = ns["M2n"]
    M2 = M2n / math.sin(beta - theta_defl)
    p2_p1 = ns["p2_p1"]
    g = gamma
    p02_p2 = (1 + (g - 1) / 2 * M2**2) ** (g / (g - 1))
    p0_pc = (1 + (g - 1) / 2 * M_c**2) ** (g / (g - 1))
    pc_p1 = p2_p1 * p02_p2 / p0_pc
    return dict(M1=M1, theta_c=theta_c, beta=beta, M2=M2, p2_p1=p2_p1,
                M_c=M_c, pc_p1=pc_p1)


# ---------------------------------------------------------------------------
# Shock-expansion theory: symmetric diamond (double-wedge) airfoil wave drag
# ---------------------------------------------------------------------------
def diamond_wave_drag(M1: float, eps_rad: float, gamma: float = GAMMA) -> dict:
    beta = beta_from_theta(M1, eps_rad, gamma)
    obl = oblique_shock(M1, beta, gamma)
    M2, p2_p1 = obl["M2"], obl["p2_p1"]
    nu2 = prandtl_meyer(M2, gamma)
    nu3 = nu2 + 2 * eps_rad
    M3 = inverse_prandtl_meyer(nu3, gamma)
    g = gamma
    p3_p2 = ((1 + (g - 1) / 2 * M2**2) / (1 + (g - 1) / 2 * M3**2)) ** (g / (g - 1))
    p3_p1 = p3_p2 * p2_p1
    t_over_c = math.tan(eps_rad)
    cd = 2 * t_over_c * (p2_p1 - p3_p1) / (g * M1**2)
    return dict(M1=M1, eps_deg=math.degrees(eps_rad), beta_deg=math.degrees(beta),
                M2=M2, p2_p1=p2_p1, M3=M3, p3_p1=p3_p1, t_over_c=t_over_c, cd=cd)


# ---------------------------------------------------------------------------
# Billig (1967) shock standoff / shock-shape correlation (Anderson Eqs 5.36-5.38)
# ---------------------------------------------------------------------------
def billig_delta_over_R(M1: float, kind: str = "cylinder") -> float:
    if kind == "cylinder":
        return 0.386 * math.exp(4.67 / M1**2)
    if kind == "sphere":
        return 0.143 * math.exp(3.24 / M1**2)
    raise ValueError(kind)


def billig_Rc_over_R(M1: float, kind: str = "cylinder") -> float:
    if kind == "cylinder":
        return 1.386 * math.exp(1.8 / (M1 - 1) ** 0.75)
    if kind == "sphere":
        return 1.143 * math.exp(0.54 / (M1 - 1) ** 1.2)
    raise ValueError(kind)


def billig_shock_y_of_x(x: float, R: float, M1: float, kind: str = "cylinder") -> float:
    """Invert Eq. (5.36) for y given x; used only for a priori domain sizing,
    never as part of the gate itself."""
    delta = billig_delta_over_R(M1, kind) * R
    Rc = billig_Rc_over_R(M1, kind) * R
    beta = math.asin(1.0 / M1)
    cotb2 = 1.0 / math.tan(beta) ** 2
    K = R + delta - x
    val = 1 + K / (Rc * cotb2)
    inside = val**2 - 1
    if inside < 0:
        return 0.0
    return math.sqrt((Rc / math.tan(beta)) ** 2 * inside)


def cp_max_rayleigh_pitot(M1: float, gamma: float = GAMMA) -> float:
    ns = normal_shock(M1, gamma)
    p02_p01 = ns["p02_p01"]
    g = gamma
    p01_p1 = (1 + (g - 1) / 2 * M1**2) ** (g / (g - 1))
    p02_p1 = p02_p01 * p01_p1
    return 2.0 / (g * M1**2) * (p02_p1 - 1)


def modified_newtonian_cp_of_theta_c(theta_c_rad: float, M1: float,
                                     gamma: float = GAMMA) -> float:
    cpmax = cp_max_rayleigh_pitot(M1, gamma)
    return cpmax * math.cos(theta_c_rad) ** 2


# ---------------------------------------------------------------------------
# Roshko (1954) / Williamson (1996) cylinder-wake Strouhal correlation
# ---------------------------------------------------------------------------
def roshko_strouhal(reynolds: float) -> float:
    """St = 0.198 (1 - 19.7/Re), the Roshko/Williamson subcritical, laminar,
    periodic vortex-shedding correlation, the exact form this lab's Re=100-180
    cylinder family already gated against (mega-batch Family 1)."""
    return 0.198 * (1 - 19.7 / reynolds)
