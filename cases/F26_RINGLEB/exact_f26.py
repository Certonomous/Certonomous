#!/usr/bin/env python3
"""
F26 -- THE EXACT SOLUTION of Ringleb flow (the hodograph solution of the 2-D
steady isentropic Euler equations, gamma = 1.4) on an entirely SUBSONIC
streamline channel, and the mesh map every F26 level is built from.

NO REFERENCE DOCUMENT FOR RINGLEB FLOW EXISTS ON THIS BOX (docs/papers/ and
docs/standards/ were searched at registration; docs/standards/
High_order_grid_convergence.pdf is Ekaterinaris 2005, a review of high-order
schemes, and carries no Ringleb section -- see its _PROVENANCE.md).  The
equations below are therefore stated in their standard form and VERIFIED BY
SUBSTITUTION at selftest, which is the only citation this module makes.

Stagnation state a0 = 1, rho0 = 1, T0 = 1/gamma (R = 1), p0 = 1/gamma.
Hodograph variables: speed V (units of a0) and flow angle theta.

    c(V)   = sqrt(1 - (gamma-1)/2 V^2)          sound speed
    rho    = c^(2/(gamma-1)) = c^5               p = c^7/gamma        T = c^2/gamma
    J(V)   = 1/c + 1/(3c^3) + 1/(5c^5) - (1/2) ln((1+c)/(1-c))
    A(V)   = 1/(2 rho V^2)
    x      = J/2 + A cos(2 theta)                y = A sin(2 theta)
    (u, v) = V (cos theta, sin theta)
    psi    = sin(theta)/V  (stream function; a streamline is psi = 1/k = const)
    phi    = cos(theta)/(rho V)  (velocity potential; equipotentials are orthogonal to streamlines)

Iso-speed lines are the circles centred (J/2, 0) of radius A; they are nested
exactly while M < 1 (the sonic line is their envelope), so the inversion
(x, y) -> V is a monotone scalar root and is unique in the subsonic region.

THE DOMAIN (registered): the channel between the streamlines psi = 1/K_MIN
(outer wall) and psi = 1/K_MAX (inner wall), cut by the equipotentials
phi = -PHI_END (inflow) and phi = +PHI_END (outflow).  On a streamline k the
speed is V = k sin(theta) <= k, so the maximum Mach in the domain is
M(K_MAX) = K_MAX / c(K_MAX): ENTIRELY SUBSONIC, printed at selftest.  The
flow is normal to the equipotential ends (a well-posed subsonic inflow /
outflow), and the FLOW-NET (phi, psi) is an ORTHOGONAL body-fitted
curvilinear grid: the mesh nodes are the images of a uniform (phi, psi)
lattice under the exact map, so every wall node lies on the exact streamline
and every end node on the exact equipotential.

THE INVERSION (x, y) -> (V, theta): Newton on F(V) = (x - J/2)^2 + y^2 - A^2
inside a bisection bracket, then theta = atan2(y, x - J/2)/2 lifted to
(0, pi).  A control round-trips (V, psi) -> (x, y) -> (V, psi) at 10^4 random
points to 1e-12 and refuses otherwise.

THE BAND PRINCIPLE -- derived from the discretisation, not measured on the
case: knp_f26.py re-implements rhoCentralFoam's Kurganov / vanLeer / vanLeerV
/ explicit-Euler scheme on the level's OWN face geometry (owner-neighbour
finite volume, Gauss linear gradients, OpenFOAM's NVDTVD / NVDVTVDV limiter
ratios) and marches sub-ladder grids to a steady state; the ladder's levels
are extrapolated with the model's observed order.  See predictions().

Refusals are `raise` and `sys.exit(2)`.  Zero `assert` (L-332).
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: exact_f26.py must not run under `python3 -O`.\n")
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
MOL_WEIGHT = 1e3 * (NA_FOAM * K_FOAM)          # 8314.47006650545 -> RR/W = 1 (as F19/F20)
T0 = 1.0 / GAMMA                     # stagnation temperature (a0 = 1, R = 1)
P0 = 1.0 / GAMMA                     # stagnation pressure (rho0 = 1)
K_MIN = 0.5                          # outer wall streamline  psi = 1/K_MIN = 2.0
K_MAX = 0.8                          # inner wall streamline  psi = 1/K_MAX = 1.25
PHI_END = 2.4                        # inflow at phi = -PHI_END, outflow at phi = +PHI_END
PSI_MIN, PSI_MAX = 1.0 / K_MAX, 1.0 / K_MIN
V_SONIC = math.sqrt(2.0 / (GAMMA + 1.0))       # 0.9129: M = 1
# name, N_ALONG (cells along phi), N_ACROSS (cells across psi); both refine by exactly 2
LEVELS = (("coarse", 384, 64), ("medium", 768, 128), ("fine", 1536, 256))
# ^ n_along x n_across = 24,576 / 98,304 / 393,216 cells; factor 2 in h both ways.
# The instrument sub-ladder that sized this (48x8, 96x16, 192x32) is NOT a level
# and build_f26.py --scratch refuses any shape that appears above.
CO_TARGET = 0.20                     # solver-convention max Courant number the fixed dt is set to (exact field, own mesh)
CO_CEILING = 0.25                    # census ceiling on the solver-reported max Courant number


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


# ---------------------------------------------------------------------------
# THE CLOSED FORM
# ---------------------------------------------------------------------------
def c_of(V):
    return np.sqrt(1.0 - 0.5 * (GAMMA - 1.0) * np.asarray(V, dtype=float) ** 2)


def rho_of(V):
    return c_of(V) ** (2.0 / (GAMMA - 1.0))


def p_of(V):
    return c_of(V) ** (2.0 * GAMMA / (GAMMA - 1.0)) / GAMMA


def T_of(V):
    return c_of(V) ** 2 / GAMMA


def mach_of(V):
    return np.asarray(V, dtype=float) / c_of(V)


def J_of(V):
    c = c_of(V)
    return 1.0 / c + 1.0 / (3.0 * c ** 3) + 1.0 / (5.0 * c ** 5) - 0.5 * np.log((1.0 + c) / (1.0 - c))


def A_of(V):
    V = np.asarray(V, dtype=float)
    return 1.0 / (2.0 * rho_of(V) * V ** 2)


def xy_of(V, theta):
    V = np.asarray(V, dtype=float)
    theta = np.asarray(theta, dtype=float)
    A = A_of(V)
    return J_of(V) / 2.0 + A * np.cos(2.0 * theta), A * np.sin(2.0 * theta)


def psi_of(V, theta):
    return np.sin(theta) / np.asarray(V, dtype=float)


def phi_of(V, theta):
    return np.cos(theta) / (rho_of(V) * np.asarray(V, dtype=float))


def fields_of(V, theta):
    """(rho, u, v, p, T) from the hodograph variables."""
    V = np.asarray(V, dtype=float)
    return rho_of(V), V * np.cos(theta), V * np.sin(theta), p_of(V), T_of(V)


def entropy_of(p, rho):
    """s = ln(gamma p / rho^gamma): identically 0 for the exact flow (homentropic)."""
    return np.log(GAMMA * np.asarray(p, dtype=float) / np.asarray(rho, dtype=float) ** GAMMA)


# ---------------------------------------------------------------------------
# FLOW-NET MAP (phi, psi) -> (V, theta) -> (x, y)
# ---------------------------------------------------------------------------
def V_from_phipsi(phi, psi, tol=1e-15):
    """solve V^2 (psi^2 + phi^2 rho(V)^2) = 1 for V in (0, V_SONIC) by Newton with bisection safeguard."""
    phi = np.asarray(phi, dtype=float)
    psi = np.asarray(psi, dtype=float)
    lo = np.full(np.broadcast(phi, psi).shape, 1e-6)
    hi = np.full(lo.shape, V_SONIC * 0.999999)

    def g(V):
        return V * V * (psi * psi + phi * phi * rho_of(V) ** 2) - 1.0
    # g increases with V (psi^2 term) and rho decreases mildly; g(lo) < 0 < g(hi) inside the subsonic map
    V = 0.5 * (lo + hi)
    for _ in range(100):
        gv = g(V)
        # derivative
        r = rho_of(V)
        drdV = -V * c_of(V) ** 3          # d(c^5)/dV = 5 c^4 c' with c' = -0.2 V / c
        dg = 2.0 * V * (psi * psi + phi * phi * r * r) + V * V * (2.0 * phi * phi * r * drdV)
        lo = np.where(gv < 0, V, lo)
        hi = np.where(gv > 0, V, hi)
        Vn = V - gv / dg
        bad = ~((Vn > lo) & (Vn < hi))
        Vn = np.where(bad, 0.5 * (lo + hi), Vn)
        if np.max(np.abs(Vn - V)) < tol:
            V = Vn
            break
        V = Vn
    if np.max(np.abs(g(V))) > 1e-12:
        refuse("V_from_phipsi did not converge: max |g| = %.3e" % np.max(np.abs(g(V))))
    return V


def theta_from_phipsi(phi, psi, V):
    return np.arctan2(psi * V, phi * rho_of(V) * V)


def xy_from_phipsi(phi, psi):
    V = V_from_phipsi(phi, psi)
    th = theta_from_phipsi(phi, psi, V)
    x, y = xy_of(V, th)
    return x, y, V, th


# ---------------------------------------------------------------------------
# THE INVERSION (x, y) -> (V, theta, psi, phi)
# ---------------------------------------------------------------------------
def invert(x, y, tol=1e-15):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    shape = np.broadcast(x, y).shape
    lo = np.full(shape, 1e-3)
    hi = np.full(shape, V_SONIC * 0.999999)

    def F(V):
        return (x - J_of(V) / 2.0) ** 2 + y * y - A_of(V) ** 2

    def dF(V):
        c = c_of(V)
        dJ = 1.0 / (c ** 7 * V)                       # dJ/dV, closed form
        r = rho_of(V)
        drdV = -V * c ** 3
        A = A_of(V)
        dA = -(drdV * V * V + 2.0 * r * V) / (2.0 * r * r * V ** 4)
        return -2.0 * (x - J_of(V) / 2.0) * dJ / 2.0 - 2.0 * A * dA
    V = 0.5 * (lo + hi)
    for _ in range(200):
        f = F(V)
        lo = np.where(f < 0, V, lo)
        hi = np.where(f > 0, V, hi)
        Vn = V - f / dF(V)
        bad = ~((Vn > lo) & (Vn < hi))
        Vn = np.where(bad, 0.5 * (lo + hi), Vn)
        if np.max(np.abs(Vn - V)) < tol:
            V = Vn
            break
        V = Vn
    resid = np.max(np.abs(F(V)))
    if resid > 1e-11:
        refuse("hodograph inversion did not converge: max |F| = %.3e" % resid)
    two_theta = np.arctan2(y, x - J_of(V) / 2.0)
    two_theta = np.where(two_theta < 0, two_theta + 2.0 * math.pi, two_theta)
    th = 0.5 * two_theta
    return V, th


def grad_V(V, theta):
    """(dV/dx, dV/dy) from the inverse of the hodograph Jacobian d(x, y)/d(V, theta)."""
    V = np.asarray(V, dtype=float)
    c = c_of(V)
    r = rho_of(V)
    A = A_of(V)
    dJ = 1.0 / (c ** 7 * V)
    drdV = -V * c ** 3
    dA = -(drdV * V * V + 2.0 * r * V) / (2.0 * r * r * V ** 4)
    x_t = -2.0 * A * np.sin(2.0 * theta)
    y_t = 2.0 * A * np.cos(2.0 * theta)
    x_V = dJ / 2.0 + dA * np.cos(2.0 * theta)
    y_V = dA * np.sin(2.0 * theta)
    det = x_V * y_t - x_t * y_V
    return y_t / det, -x_t / det


def dp_dV(V):
    """dp/dV = -rho V (Bernoulli: dp = -rho V dV along the isentrope)."""
    V = np.asarray(V, dtype=float)
    return -rho_of(V) * V


def dp_dn(x, y, nx, ny):
    """exact normal pressure gradient at points (x, y) for unit normals (nx, ny)."""
    V, th = invert(x, y)
    Vx, Vy = grad_V(V, th)
    return dp_dV(V) * (Vx * nx + Vy * ny)


def fields_at(x, y):
    """exact (rho, u, v, p, T, V, theta, psi, phi, M) at physical points."""
    V, th = invert(x, y)
    rho, u, v, p, T = fields_of(V, th)
    return dict(rho=rho, u=u, v=v, p=p, T=T, V=V, theta=th, psi=psi_of(V, th), phi=phi_of(V, th), M=mach_of(V))


# ---------------------------------------------------------------------------
# THE MESH: images of a uniform (phi, psi) lattice
# ---------------------------------------------------------------------------
def lattice(n_along, n_across):
    """node arrays X[j, i], Y[j, i], i = 0..n_along (phi, inflow -> outflow), j = 0..n_across
    (psi: j = 0 is the INNER wall psi = PSI_MIN = 1/K_MAX, j = n_across the OUTER wall
    psi = PSI_MAX = 1/K_MIN); (phi, psi, z) is right-handed so blockMesh's block is not inside-out."""
    phi = np.linspace(-PHI_END, PHI_END, n_along + 1)
    psi = np.linspace(PSI_MIN, PSI_MAX, n_across + 1)
    PHI, PSI = np.meshgrid(phi, psi)
    x, y, V, th = xy_from_phipsi(PHI, PSI)
    return dict(phi=phi, psi=psi, X=x, Y=y, V=V, theta=th)


# SIMPLE ITERATION COUNTS -- sized from THIS ladder's own MEASURED convergence rate
# (pre-registration section 5); NEVER inherited from a coarser ladder (L-346).
N_STEPS = dict(coarse=0, medium=0, fine=0)   # TRIPWIRE ZEROS -- replaced by the measured sizing before freeze
N_CHECKPOINTS = 20


def steps_of(name):
    if name not in N_STEPS:
        refuse("unknown level %r" % name)
    return N_STEPS[name]


def write_every_of(name):
    return steps_of(name) // N_CHECKPOINTS


def level_shape(name):
    lv = dict((n, (na, nc)) for n, na, nc in LEVELS)
    if name not in lv:
        refuse("unknown level %r" % name)
    return lv[name]


# ---------------------------------------------------------------------------
# CONTROLS
# ---------------------------------------------------------------------------
def _sym(gamma_rho_factor=1):
    import sympy as sp
    V, th = sp.symbols("V theta", positive=True)
    g = sp.Rational(7, 5)
    c = sp.sqrt(1 - (g - 1) / 2 * V ** 2)
    rho = c ** (2 / (g * gamma_rho_factor - 1))    # the plant lives in rho's exponent only
    p = c ** (2 * g / (g - 1)) / g
    J = 1 / c + 1 / (3 * c ** 3) + 1 / (5 * c ** 5) - sp.Rational(1, 2) * sp.log((1 + c) / (1 - c))
    A = 1 / (2 * c ** (2 / (g - 1)) * V ** 2)      # the registered map (unplanted)
    x = J / 2 + sp.cos(2 * th) * A
    y = sp.sin(2 * th) * A
    u, v = V * sp.cos(th), V * sp.sin(th)
    xV, xt, yV, yt = sp.diff(x, V), sp.diff(x, th), sp.diff(y, V), sp.diff(y, th)
    det = xV * yt - xt * yV

    def dx(f):
        return (sp.diff(f, V) * yt - sp.diff(f, th) * yV) / det

    def dy(f):
        return (-sp.diff(f, V) * xt + sp.diff(f, th) * xV) / det
    res = dict(continuity=dx(rho * u) + dy(rho * v),
               x_momentum=rho * (u * dx(u) + v * dy(u)) + dx(p),
               y_momentum=rho * (u * dx(v) + v * dy(v)) + dy(p),
               vorticity=dx(v) - dy(u),
               entropy=sp.log(g * p / rho ** g))
    return sp, V, th, res


def _worst(sp, V, th, res, n=60, dps=40, seed=1):
    import mpmath
    import random
    mpmath.mp.dps = dps
    rnd = random.Random(seed)
    out = {}
    for k, e in res.items():
        f = sp.lambdify((V, th), e, "mpmath")
        w = mpmath.mpf(0)
        for _ in range(n):
            w = max(w, abs(f(mpmath.mpf(rnd.uniform(0.25, 0.88)), mpmath.mpf(rnd.uniform(0.3, 2.8)))))
        out[k] = float(w)
    return out


def control_symbolic_substitution():
    try:
        sp, V, th, res = _sym()
    except ImportError:
        refuse("sympy is not importable; the exact solution cannot be verified by substitution")
    cont = sp.simplify(res["continuity"])
    if cont != 0:
        refuse("SYMBOLIC SUBSTITUTION FAILED: continuity residual simplifies to %s, not 0" % cont)
    w = _worst(sp, V, th, res)
    bad = [k for k, v in w.items() if v > 1e-30]
    if bad:
        refuse("SUBSTITUTION FAILED at 40 digits: residuals %s exceed 1e-30: %s" % (bad, w))
    return dict(control="substitution_into_steady_Euler_via_hodograph_Jacobian",
                continuity_symbolic=str(cont), worst_residual_40_digits=w, passed=True)


def control_substitution_is_able_to_fail():
    """PLANTED CONTROL (rule 3): gamma in rho's exponent raised 10 % must break continuity and momentum."""
    sp, V, th, res = _sym(gamma_rho_factor=sp_rational_11_10())
    w = _worst(sp, V, th, dict(continuity=res["continuity"], x_momentum=res["x_momentum"]), n=10)
    if min(w.values()) < 1e-6:
        refuse("PLANTED CONTROL FAILED: a 1.1 gamma plant in rho still gave residuals %s" % w)
    return dict(control="PZ-F26-GAMMA_planted_1.1_in_rho_must_break_Euler", residuals=w, passed=True)


def sp_rational_11_10():
    import sympy as sp
    return sp.Rational(11, 10)


def control_inversion_round_trips(n=10000, seed=26, tol=1e-12):
    rng = np.random.default_rng(seed)
    V0 = rng.uniform(0.3, 0.86, n)
    k = rng.uniform(K_MIN, K_MAX, n)
    keep = V0 < k
    V0, k = V0[keep], k[keep]
    th0 = np.where(rng.uniform(0, 1, V0.size) < 0.5, np.arcsin(V0 / k), math.pi - np.arcsin(V0 / k))
    psi0 = psi_of(V0, th0)
    x, y = xy_of(V0, th0)
    V1, th1 = invert(x, y)
    psi1 = psi_of(V1, th1)
    dV, dpsi, dth = np.max(np.abs(V1 - V0)), np.max(np.abs(psi1 - psi0)), np.max(np.abs(th1 - th0))
    if max(dV, dpsi, dth) > tol:
        refuse("INVERSION ROUND TRIP FAILED: max |dV| %.3e |dpsi| %.3e |dtheta| %.3e over %d points" % (dV, dpsi, dth, V0.size))
    # planted: a point displaced by 1e-3 must NOT return the same V
    V2, _ = invert(x + 1e-3, y)
    if np.max(np.abs(V2 - V0)) < 1e-9:
        refuse("PLANTED CONTROL FAILED: the inversion returned the same V for a displaced point")
    x2, y2, V3, th3 = xy_from_phipsi(phi_of(V0, th0), psi0)
    dxy = max(np.max(np.abs(x2 - x)), np.max(np.abs(y2 - y)))
    if dxy > tol:
        refuse("FLOW-NET MAP ROUND TRIP FAILED: (phi, psi) -> (x, y) differs by %.3e" % dxy)
    # the analytic gradient of V against a central difference of the inversion (1e-6 step)
    eps = 1e-6
    Vx_fd = (invert(x + eps, y)[0] - invert(x - eps, y)[0]) / (2 * eps)
    Vy_fd = (invert(x, y + eps)[0] - invert(x, y - eps)[0]) / (2 * eps)
    Vx, Vy = grad_V(V0, th0)
    dg = max(np.max(np.abs(Vx - Vx_fd)), np.max(np.abs(Vy - Vy_fd)))
    if dg > 1e-6:
        refuse("grad_V disagrees with the finite-difference gradient of the inversion: %.3e" % dg)
    return dict(control="hodograph_inversion_round_trip_1e-12", points=int(V0.size), max_dV=float(dV), grad_V_vs_fd=float(dg),
                max_dpsi=float(dpsi), max_dtheta=float(dth), flow_net_max_dxy=float(dxy),
                planted_displacement_moved_V=float(np.max(np.abs(V2 - V0))), passed=True)


def control_domain_is_subsonic_and_ladder_similar():
    m_max = float(mach_of(K_MAX))
    if not (m_max < 0.95):
        refuse("the inner wall reaches M = %.4f; the registered cell is subsonic-compressible" % m_max)
    lat = lattice(*level_shape("coarse"))
    m_lat = float(np.max(mach_of(lat["V"])))
    if m_lat > m_max + 1e-12:
        refuse("a lattice node exceeds the wall Mach bound: %.6f > %.6f" % (m_lat, m_max))
    ra = [LEVELS[i + 1][1] / LEVELS[i][1] for i in range(2)]
    rc = [LEVELS[i + 1][2] / LEVELS[i][2] for i in range(2)]
    if max(abs(v - 2.0) for v in ra + rc) > 1e-12:
        refuse("the ladder is not a factor-2 refinement in both directions: %s %s" % (ra, rc))
    # entropy of the exact field is identically zero at the lattice nodes
    s = entropy_of(p_of(lat["V"]), rho_of(lat["V"]))
    if np.max(np.abs(s)) > 1e-14:
        refuse("the exact field is not homentropic at the lattice nodes: max |s| = %.3e" % np.max(np.abs(s)))
    return dict(control="domain_entirely_subsonic_and_ladder_factor_2", M_max_domain=m_max, M_max_at_nodes=m_lat,
                M_min_inflow=float(np.min(mach_of(lat["V"][:, 0]))), M_max_inflow=float(np.max(mach_of(lat["V"][:, 0]))),
                along_ratios=ra, across_ratios=rc, max_abs_entropy_exact=float(np.max(np.abs(s))), passed=True)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    controls = [control_symbolic_substitution(), control_substitution_is_able_to_fail(),
                control_inversion_round_trips(), control_domain_is_subsonic_and_ladder_similar()]
    lat = lattice(*level_shape("coarse"))
    summary = dict(constants=dict(gamma=GAMMA, R=R_GAS, Cp=CP, Cv=CV, molWeight=MOL_WEIGHT, T0=T0, p0=P0,
                                  K_MIN=K_MIN, K_MAX=K_MAX, PHI_END=PHI_END, V_SONIC=V_SONIC),
                   M_max=float(mach_of(K_MAX)), levels=[dict(name=n, n_along=na, n_across=nc, cells=na * nc) for n, na, nc in LEVELS],
                   bbox=dict(xmin=float(lat["X"].min()), xmax=float(lat["X"].max()), ymin=float(lat["Y"].min()), ymax=float(lat["Y"].max())))
    ok = all(c.get("passed") for c in controls) and len(controls) == 4 and __debug__
    if a.json:
        print(json.dumps(dict(summary, controls=controls), indent=2))
        return 0
    if a.selftest:
        print(json.dumps(dict(summary, controls=controls, predicate=dict(ok=ok)), indent=2))
        if not ok:
            refuse("SELFTEST DID NOT ESTABLISH ITS CLAIM")
        print("\nSELFTEST GREEN -- 4 controls: continuity simplifies to 0 and all Euler residuals < 1e-30 at 40 digits; "
              "a 1.1 gamma plant breaks them; the inversion round-trips 1e4 points to 1e-12; the domain is subsonic "
              "(M_max %.4f) and the ladder refines by exactly 2 both ways" % summary["M_max"])
        return 0
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
