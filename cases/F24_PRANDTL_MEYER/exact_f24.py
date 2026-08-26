#!/usr/bin/env python3
"""
F24 -- THE EXACT SOLUTION of the Prandtl-Meyer expansion around a convex corner
(M1 = 2.0, deflection 15 deg, gamma = 1.4, inviscid), the exact CENTRED
SIMPLE-WAVE FIELD inside the fan, and the registered band derivation for the
F24 gates.

    nu(M) = sqrt((g+1)/(g-1)) atan( sqrt((g-1)/(g+1) (M^2 - 1)) ) - atan( sqrt(M^2 - 1) )
    nu(M2) = nu(M1) + delta           ->  M2 = 2.598446326990895
    p2/p1 = [ (1 + (g-1)/2 M1^2) / (1 + (g-1)/2 M2^2) ]^{g/(g-1)} = 0.3930677946090901
    T2/T1 = 0.7658320905723576,   region 2 flow direction = -15 deg

THE FAN.  The C- characteristics are rays from the corner.  On the ray at
polar angle phi (from the upstream flow direction, counter-clockwise) the
local Mach number M satisfies   mu(M) - (nu(M) - nu(M1)) = phi,   with
mu = asin(1/M); the head ray is phi = mu(M1) = 30 deg, the tail ray is
phi = mu(M2) - delta = 7.63 deg; p, T follow isentropically from M.

Nondimensional perfect gas exactly as F19/F20 (R = 1, gamma = 1.4, Cp = 3.5):
state 1 is p1 = T1 = rho1 = 1, c1 = sqrt(1.4), U1 = (2 c1, 0, 0).

THE REFERENCE IS NOT A PAPER ON THIS BOX.  IT IS A SUBSTITUTION.  At selftest
the closed-form nu(M) is checked against the defining integral
int sqrt(M^2-1) / (1 + (g-1)/2 M^2) dM/M by adaptive quadrature (1e-11), the
isentropic ratios are re-derived from the definition of M with T0 constant
across the fan, the fan field is continuous with state 1 at the head ray and
state 2 at the tail ray and satisfies the ray relation to 1e-12, and the
planted control (gamma raised 10 % in the closed form only) must break the
quadrature identity.

THE BANDS -- FROM THE REAL SCHEME ON A THREE-GRID SUB-LADDER, DISCLOSED.
F17/F20/F22 derived their bands from a re-implementation of the solver's
stencils.  A 2-D Kurganov/vanLeer re-implementation on a two-block sheared mesh
was not affordable in this registration, so the "model" is the REAL scheme on
three SUB-LADDER grids that are NOT levels of the ladder (h = 1/16, 1/32, 1/64;
the ladder is 1/150, 1/300, 1/600), run to the registered endTime in the
writing invocation (scratch, about one core-minute in total, not retained, no
gate quantity of the ladder read from them), read by the grader's own readers
with the grader's own plateau-window mean.  The sub-ladder triple of EVERY
gate quantity is run through scripts/roache_triple.py at registration (the F19
rule); a quantity whose sub-ladder triple is CONVERGING is GATED with a band
extrapolated from the finest sub-ladder grid with the observed order (clamped
to P_CLAMP); a quantity whose triple is DEGENERATE, OSCILLATORY, STAGNANT or
DIVERGENT is registered REPORTED-NOT-GATED: its values, triple and order are
printed, and no verdict is issued on it.  The readings are REGISTERED
CONSTANTS below with the artifact they came from; the factor-3 window around
the extrapolated fine error is the declared admission of what three coarse
readings cannot know about 1/600.  GATE_MODE is not a choice: a control
re-derives it from the readings through roache_triple and refuses if the
registered mode disagrees.

Refusals are `raise` and `sys.exit(2)`.  Zero `assert` (L-332).
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: exact_f24.py must not run under `python3 -O` (the shared "
                     "roache_triple.py seals rule 1 and rule 5 with checks -O would blind).\n")
    sys.exit(2)

import os
import json
import math
import argparse

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import roache_triple as RT              # noqa: E402  -- the SAME instrument the grader gates with

# ---------------------------------------------------------------------------
# THE CASE, FROZEN.
# ---------------------------------------------------------------------------
GAMMA = 1.4
R_GAS = 1.0
CP = GAMMA / (GAMMA - 1.0) * R_GAS   # 3.5
NA_FOAM, K_FOAM = 6.0221417930e+23, 1.38065e-23
MOL_WEIGHT = 1e3 * (NA_FOAM * K_FOAM)          # 8314.47006650545 -> RR/W = 1
M1 = 2.0
DELTA_DEG = 15.0
P1, T1, RHO1 = 1.0, 1.0, 1.0
C1 = math.sqrt(GAMMA * R_GAS * T1)
U1 = M1 * C1
X_IN, X_CORNER, X_OUT = -0.5, 0.0, 1.5
H_TOP = 1.0
T_END = 4.0
WRITE_DT = 0.1
DT_OVER_H = 0.04
CO_CEILING = 0.35                    # on the solver-reported CoNum (classical 0.5)
# name, N (cells per unit length; h = 1/N), steps (dt = T_END/steps = DT_OVER_H / N)
LEVELS = (("coarse", 150, 15000), ("medium", 300, 30000), ("fine", 600, 60000))
RANKS = 4
# THE SAMPLING BOX in region 2: x in [X_BOX0, X_BOX1], perpendicular distance
# from the deflected wall n in [0, N_BOX]; the tail Mach line (mu2 = 22.63 deg
# above the wall) is at n >= 0.388 over the box (control below).
X_BOX0, X_BOX1, N_BOX = 0.9, 1.3, 0.25
# THE LINE ACROSS THE FAN: the one column of cells at x = X_LINE + h/2 (block B
# has vertical grid lines, so every level has exactly N cells in that column,
# from the wall y = -0.268 to the sloped top y = 0.732; the tail ray crosses it
# at y = 0.134 and the head ray at y = 0.577 -- the whole fan, inside the domain).
X_LINE = 1.0

# ---------------------------------------------------------------------------
# SUB-LADDER READINGS -- REGISTERED CONSTANTS (see module docstring).
# N -> readings of the grader's own quantities (plateau-window means over the
# last 12 of 40 checkpoints, t = 2.9 ... 4.0) on the scratch grid h = 1/N run
# serially to T_END with the registered dictionaries; artifact: the scratch
# runs named in the pre-registration section 4 (not retained).
# ---------------------------------------------------------------------------
SUBLADDER_GRIDS = (16, 32, 64)
SUBLADDER = {
    16: dict(p_box=0.3871698814155447, M_box=2.589249667115091, p_line=0.03395297691285794,
             box_cells=28, line_cells=16, p_box_window_std=1.72e-4, p_line_series_std=1.12e-3, co_max=0.1370, clock_s=2),
    32: dict(p_box=0.3933488773180131, M_box=2.5832201757024285, p_line=0.01854222742786359,
             box_cells=104, line_cells=32, p_box_window_std=6.95e-5, p_line_series_std=3.64e-4, co_max=0.1370, clock_s=8),
    64: dict(p_box=0.39319706158636886, M_box=2.59039946749601, p_line=0.009980854573740325,
             box_cells=425, line_cells=64, p_box_window_std=7.96e-6, p_line_series_std=1.75e-4, co_max=0.1370, clock_s=55),
}
# Registered GATE MODE per quantity.  DERIVED, not chosen, where the sub-ladder
# triple is CONVERGING (-> GATED-EXTRAPOLATED, band from the extrapolated fine
# error, order claimed); where it is NOT CONVERGING the registration may gate
# with an ABSOLUTE band (3x the finest sub-ladder error, NO order claim, rule 5
# free to return NOT A RESULT on the ladder triple) or report without a gate.
# control_subladder_registration refuses an extrapolated gate on a
# non-CONVERGING triple and refuses any registered mode that is not one of MODES.
MODES = ("GATED-EXTRAPOLATED", "GATED-ABSOLUTE", "REPORTED-NOT-GATED")
GATE_MODE = {"p_box": "GATED-ABSOLUTE", "M_box": "REPORTED-NOT-GATED", "p_line": "GATED-EXTRAPOLATED"}
P_CLAMP = (0.5, 2.0)
QUANTITIES = ("p_box", "M_box", "p_line")
BAND_FACTOR = 3.0                    # the one declared parameter (the grader re-reads it from here)


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def h_of(n):
    return 1.0 / float(n)


def dt_of(steps):
    return T_END / float(steps)


def nu(M, gamma=GAMMA):
    a = (gamma + 1.0) / (gamma - 1.0)
    return math.sqrt(a) * math.atan(math.sqrt((M * M - 1.0) / a)) - math.atan(math.sqrt(M * M - 1.0))


def nu_quadrature(M, gamma=GAMMA):
    """The defining integral by adaptive quadrature, to 1e-13."""
    from scipy.integrate import quad
    f = lambda m: math.sqrt(m * m - 1.0) / (1.0 + 0.5 * (gamma - 1.0) * m * m) / m
    val, err = quad(f, 1.0, M, epsabs=1e-14, epsrel=1e-14, limit=200)
    return val


def m2_exact(gamma=GAMMA):
    target = nu(M1, gamma) + math.radians(DELTA_DEG)
    lo, hi = 1.0 + 1e-12, 20.0
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        if nu(mid, gamma) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def state2(gamma=GAMMA):
    M2 = m2_exact(gamma)
    k = 0.5 * (gamma - 1.0)
    Tr = (1.0 + k * M1 * M1) / (1.0 + k * M2 * M2)
    pr = Tr ** (gamma / (gamma - 1.0))
    T2 = T1 * Tr
    c2 = math.sqrt(gamma * R_GAS * T2)
    d = math.radians(DELTA_DEG)
    return dict(M2=M2, p2_over_p1=pr, T2_over_T1=Tr, rho2_over_rho1=pr / Tr, T2=T2, p2=P1 * pr,
                u2=M2 * c2 * math.cos(d), v2=-M2 * c2 * math.sin(d), c2=c2,
                mu1_deg=math.degrees(math.asin(1.0 / M1)), mu2_deg=math.degrees(math.asin(1.0 / M2)),
                nu1_deg=math.degrees(nu(M1, gamma)), nu2_deg=math.degrees(nu(M2, gamma)),
                phi_head_deg=math.degrees(math.asin(1.0 / M1)),
                phi_tail_deg=math.degrees(math.asin(1.0 / M2)) - DELTA_DEG)


def wall_y(x):
    """The deflected wall for x >= 0 (y = 0 for x < 0)."""
    x = np.asarray(x, dtype=float)
    return np.where(x > 0.0, -x * math.tan(math.radians(DELTA_DEG)), 0.0)


def box_mask(xc, yc):
    """Cells whose centre lies in the sampling box (region 2)."""
    d = math.radians(DELTA_DEG)
    n = (np.asarray(yc) - wall_y(xc)) * math.cos(d)
    return (xc >= X_BOX0) & (xc <= X_BOX1) & (n >= 0.0) & (n <= N_BOX)


def line_mask(xc, n):
    """Cells of the column at x = X_LINE + h/2 (h = 1/n); the caller refuses a count != n."""
    h = h_of(n)
    return np.abs(np.asarray(xc, dtype=float) - (X_LINE + 0.5 * h)) < 0.25 * h


def mach(U, T):
    return np.sqrt(U[:, 0] ** 2 + U[:, 1] ** 2 + U[:, 2] ** 2) / np.sqrt(GAMMA * R_GAS * np.asarray(T))


# ---------------------------------------------------------------------------
# THE EXACT FAN FIELD (centred simple wave)
# ---------------------------------------------------------------------------
def _nu_vec(M, gamma=GAMMA):
    a = (gamma + 1.0) / (gamma - 1.0)
    return math.sqrt(a) * np.arctan(np.sqrt((M * M - 1.0) / a)) - np.arctan(np.sqrt(M * M - 1.0))


def fan_field(x, y):
    """Exact field at the points (x, y): dict of arrays M, p, T, theta (rad) and
    region (1 upstream of the head ray, 0 inside the fan, 2 downstream of the
    tail ray).  Rays are measured from the corner at the origin."""
    x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float)
    s2 = state2()
    phi = np.arctan2(y, x)
    phi_head = math.radians(s2["phi_head_deg"]); phi_tail = math.radians(s2["phi_tail_deg"])
    nu1 = nu(M1)
    M = np.full(x.shape, M1)
    region = np.ones(x.shape, dtype=int)
    inside = (phi < phi_head) & (phi > phi_tail)
    region[inside] = 0
    down = phi <= phi_tail
    region[down] = 2
    M[down] = s2["M2"]
    if np.any(inside):
        lo = np.full(int(inside.sum()), M1); hi = np.full(int(inside.sum()), s2["M2"])
        target = phi[inside]
        for _ in range(100):                          # g(M) = mu(M) - (nu(M) - nu1) decreases with M
            mid = 0.5 * (lo + hi)
            g = np.arcsin(1.0 / mid) - (_nu_vec(mid) - nu1)
            hi = np.where(g < target, mid, hi)
            lo = np.where(g < target, lo, mid)
        M[inside] = 0.5 * (lo + hi)
    k = 0.5 * (GAMMA - 1.0)
    Tr = (1.0 + k * M1 * M1) / (1.0 + k * M * M)
    return dict(M=M, p=P1 * Tr ** (GAMMA / (GAMMA - 1.0)), T=T1 * Tr, theta=-(_nu_vec(M) - nu1), region=region, phi=phi)


def line_l2(p, xc, yc, V, n):
    """The G-F24-2 quantity: sqrt( sum_j V_j (p_j - p_exact(x_j, y_j))^2 / sum_j V_j ) / p1
    over the column at x = X_LINE + h/2, whose count must be exactly n."""
    p = np.asarray(p, dtype=float); xc = np.asarray(xc, dtype=float); yc = np.asarray(yc, dtype=float)
    V = np.asarray(V, dtype=float)
    if not (p.shape == xc.shape == yc.shape == V.shape):
        refuse("line_l2: p, C and V do not carry the same cell count")
    m = line_mask(xc, n)
    cnt = int(m.sum())
    if cnt != n:
        refuse("the column at x = X_LINE + h/2 holds %d cells, registered %d" % (cnt, n))
    ex = fan_field(xc[m], yc[m])["p"]
    return float(math.sqrt(np.sum(V[m] * (p[m] - ex) ** 2) / np.sum(V[m])) / P1)


# ---------------------------------------------------------------------------
# THE BAND DERIVATION FROM THE SUB-LADDER CONSTANTS
# ---------------------------------------------------------------------------
def _registered():
    for n in SUBLADDER_GRIDS:
        if SUBLADDER.get(n) is None:
            refuse("sub-ladder grid 1/%d is not registered (SUBLADDER[%d] is None)" % (n, n))
    for q in QUANTITIES:
        if GATE_MODE.get(q) not in MODES:
            refuse("GATE_MODE[%r] = %r is not one of %s" % (q, GATE_MODE.get(q), MODES))


def reference(q):
    s2 = state2()
    return {"p_box": s2["p2_over_p1"], "M_box": s2["M2"], "p_line": 0.0}[q]


def subladder_levels(q):
    """Coarse-first level list of the RAW quantity on the sub-ladder (the same
    values a ladder grade feeds grade_ladder)."""
    _registered()
    return [dict(name="n%d" % n, cells=2 * n * n, value=float(SUBLADDER[n][q])) for n in SUBLADDER_GRIDS]


def subladder_triple(q):
    """The finest sub-ladder triple of quantity q through roache_triple's own
    arithmetic (state, order) -- the mode derivation."""
    tr = RT.all_triples(subladder_levels(q), 2)[-1]
    return dict(state=tr["state"], order=tr.get("order"), levels=tr.get("levels"))


def mode_allowed(q):
    """The set of modes the sub-ladder triple ADMITS for quantity q."""
    return ("GATED-EXTRAPOLATED",) if subladder_triple(q)["state"] == "CONVERGING" \
        else ("GATED-ABSOLUTE", "REPORTED-NOT-GATED")


def _error_series(q):
    ref = reference(q)
    return [(h_of(n), float(SUBLADDER[n][q]) - ref) for n in SUBLADDER_GRIDS]


def gate_specs():
    """Per quantity: mode, reference, band (or None), the sub-ladder triple, the
    extrapolation (GATED-EXTRAPOLATED only) and a one-line principle."""
    _registered()
    out = {}
    for q in QUANTITIES:
        tri = subladder_triple(q)
        ref = reference(q)
        mode = GATE_MODE[q]
        (h_a, ea), (h_b, eb), (h_c, ec) = _error_series(q)
        spec = dict(quantity=q, mode=mode, reference=ref, triple=tri, subladder_h=[h_a, h_b, h_c],
                    subladder_errors=[ea, eb, ec], band=None, per_level=None, fine_pred=None, order_claim=None)
        if mode == "GATED-EXTRAPOLATED":
            if eb == 0.0 or ec == 0.0 or np.sign(eb) != np.sign(ec):
                refuse("sub-ladder errors for %s change sign or vanish (%.3e, %.3e): no extrapolation is defensible" % (q, eb, ec))
            p_obs = math.log(abs(eb) / abs(ec)) / math.log(h_b / h_c)
            p_used = min(max(p_obs, P_CLAMP[0]), P_CLAMP[1])
            per_level = dict((name, ec * (h_of(n) / h_c) ** p_used) for name, n, _s in LEVELS)
            fine = per_level["fine"]
            tol = BAND_FACTOR * abs(fine)
            band = (abs(fine) / BAND_FACTOR, abs(fine) * BAND_FACTOR) if ref == 0.0 else (ref - tol, ref + tol)
            spec.update(p_observed=p_obs, p_used=p_used, per_level=per_level, fine_pred=fine, band=band, order_claim=p_used,
                        principle="sub-ladder triple %s (order %.3f); fine-level error extrapolated from h = 1/%d with order %.3f "
                                  "(clamped to %s) = %+.6e; band = %s" % (tri["state"], tri["order"] or float("nan"), SUBLADDER_GRIDS[-1],
                                                                          p_used, list(P_CLAMP), fine, list(band)))
        elif mode == "GATED-ABSOLUTE":
            tol = BAND_FACTOR * abs(ec)
            band = (ref - tol, ref + tol)
            spec.update(band=band, fine_pred=None,
                        principle="sub-ladder triple %s: NO ORDER CLAIM and no extrapolation; ABSOLUTE band = reference +/- %g x the "
                                  "finest sub-ladder error (h = 1/%d: %+.6e) = %s; rule 5 may return NOT A RESULT on the ladder triple "
                                  "and that outcome is registered as possible" % (tri["state"], BAND_FACTOR, SUBLADDER_GRIDS[-1], ec, list(band)))
        else:
            spec.update(principle="REPORTED-NOT-GATED at registration: the sub-ladder triple is %s (errors %+.3e / %+.3e / %+.3e); "
                                  "the grader prints the values, the ladder triple and its order beside the exact reference and "
                                  "issues NO verdict" % (tri["state"], ea, eb, ec))
        out[q] = spec
    return out


def predictions():
    s2 = state2()
    gs = gate_specs()
    tab = []
    for name, n, steps in LEVELS:
        row = dict(name=name, n=n, cells=2 * n * n, h=h_of(n), dt=dt_of(steps), steps=steps)
        for q in QUANTITIES:
            row[q + "_err_pred"] = gs[q]["per_level"][name] if gs[q]["per_level"] else None
        tab.append(row)
    return tab


# ---------------------------------------------------------------------------
# CONTROLS
# ---------------------------------------------------------------------------
def control_nu_closed_form_matches_quadrature():
    s2 = state2()
    bad = []
    for M in (M1, s2["M2"], 1.5, 3.0):
        a, b = nu(M), nu_quadrature(M)
        if abs(a - b) > 1e-11:
            bad.append((M, a, b))
    if bad:
        refuse("nu(M) closed form disagrees with its defining integral: %s" % bad)
    if abs(nu(s2["M2"]) - nu(M1) - math.radians(DELTA_DEG)) > 1e-12:
        refuse("nu(M2) - nu(M1) is not the registered deflection")
    k = 0.5 * (GAMMA - 1.0)
    T2 = T1 * (1 + k * M1 ** 2) / (1 + k * s2["M2"] ** 2)
    p2 = P1 * (T2 / T1) ** (GAMMA / (GAMMA - 1.0))
    if abs(T2 - s2["T2"]) > 1e-14 or abs(p2 - s2["p2"]) > 1e-14:
        refuse("isentropic ratios do not re-derive")
    return dict(control="nu_closed_form_vs_defining_integral_and_isentropic_rederivation",
                M2=s2["M2"], p2_over_p1=s2["p2_over_p1"], T2_over_T1=s2["T2_over_T1"], passed=True)


def control_substitution_is_able_to_fail():
    """PLANTED CONTROL (rule 3): gamma raised 10 % in the closed form only must
    break the identity with the gamma = 1.4 quadrature."""
    d = abs(nu(M1, GAMMA * 1.1) - nu_quadrature(M1, GAMMA))
    if d < 1e-3:
        refuse("PLANTED CONTROL FAILED: gamma planted at 1.1x still matched the quadrature (|d| = %.3e)" % d)
    return dict(control="PZ-F24-GAMMA_planted_1.1x_must_break_the_identity", planted_factor=1.1,
                mismatch=d, passed=True)


def control_fan_field():
    """The centred simple wave: continuous with state 1 at the head ray and with
    state 2 at the tail ray; the ray relation holds to 1e-12 on 50 rays; M
    increases monotonically through the fan; the column at X_LINE crosses the
    whole fan inside the domain; a planted ray angle off the fan reads state 1/2."""
    s2 = state2()
    ph, pt = math.radians(s2["phi_head_deg"]), math.radians(s2["phi_tail_deg"])
    eps = 1e-9
    r = 1.0
    f = fan_field(r * np.cos([ph + eps, ph - eps, pt + eps, pt - eps]), r * np.sin([ph + eps, ph - eps, pt + eps, pt - eps]))
    if abs(f["p"][0] - P1) > 1e-12 or abs(f["p"][1] - P1) > 1e-7 or abs(f["p"][3] - s2["p2"]) > 1e-12 or abs(f["p"][2] - s2["p2"]) > 1e-7:
        refuse("the fan field is not continuous with state 1 at the head ray / state 2 at the tail ray: %s" % f["p"].tolist())
    phis = np.linspace(pt + 1e-6, ph - 1e-6, 50)
    g = fan_field(np.cos(phis), np.sin(phis))
    resid = np.arcsin(1.0 / g["M"]) - (_nu_vec(g["M"]) - nu(M1)) - phis
    if np.max(np.abs(resid)) > 1e-12:
        refuse("the ray relation mu(M) - (nu(M) - nu(M1)) = phi fails by %.3e" % np.max(np.abs(resid)))
    if np.any(np.diff(g["M"]) > 0):
        refuse("M does not increase monotonically from the head ray to the tail ray")
    if np.max(np.abs(g["theta"] + (_nu_vec(g["M"]) - nu(M1)))) > 1e-15 or g["theta"][0] > -math.radians(DELTA_DEG) + 1e-5:
        refuse("the flow direction does not follow -(nu(M) - nu(M1)) through the fan")
    y_wall = float(wall_y(X_LINE)); y_tail = X_LINE * math.tan(pt); y_head = X_LINE * math.tan(ph)
    y_top = H_TOP - X_LINE * math.tan(math.radians(DELTA_DEG))
    if not (y_wall < y_tail < y_head < y_top):
        refuse("the column at X_LINE does not cross the whole fan inside the domain (%g %g %g %g)" % (y_wall, y_tail, y_head, y_top))
    for name, n, _s in LEVELS:
        if abs((X_LINE - X_CORNER) * n - round((X_LINE - X_CORNER) * n)) > 1e-12:
            refuse("X_LINE + h/2 is not a cell-column centre at level %s" % name)
    off = fan_field(np.array([-0.3, 1.2]), np.array([0.5, -0.3]))
    if off["region"][0] != 1 or off["region"][1] != 2 or abs(off["M"][1] - s2["M2"]) > 1e-15:
        refuse("points outside the fan are not classified state 1 / state 2")
    return dict(control="fan_field_continuous_ray_relation_monotone_column_crosses_fan",
                phi_head_deg=s2["phi_head_deg"], phi_tail_deg=s2["phi_tail_deg"], max_ray_residual=float(np.max(np.abs(resid))),
                line_y=dict(wall=y_wall, tail=y_tail, head=y_head, top=y_top), passed=True)


def control_box_lies_in_region_2():
    s2 = state2()
    d = math.radians(DELTA_DEG)
    mu2 = math.radians(s2["mu2_deg"])
    margin = []
    for x in (X_BOX0, X_BOX1):
        s_along = x / math.cos(d)
        n_tail = s_along * math.tan(mu2)
        margin.append(n_tail - N_BOX)
    if min(margin) < 0.1:
        refuse("the sampling box reaches within 0.1 of the tail Mach line (margins %s)" % margin)
    y_head_at_outlet = X_OUT * math.tan(math.radians(s2["mu1_deg"]))
    return dict(control="sampling_box_in_region_2", tail_margins=margin,
                y_head_at_outlet=y_head_at_outlet, top_at_outlet=H_TOP - X_OUT * math.tan(d),
                head_crosses_sloped_top_at_x=H_TOP / (math.tan(math.radians(s2["mu1_deg"])) + math.tan(d)), passed=True)


def control_ladder_is_geometrically_similar():
    for name, n, steps in LEVELS:
        if abs(dt_of(steps) * n - DT_OVER_H) > 1e-12:
            refuse("level %s does not keep dt/h = %g" % (name, DT_OVER_H))
    r = [LEVELS[i + 1][1] / LEVELS[i][1] for i in range(2)]
    rs = [LEVELS[i + 1][2] / LEVELS[i][2] for i in range(2)]
    if max(abs(v - 2.0) for v in r + rs) > 1e-12:
        refuse("the ladder is not a factor-2 refinement in h and dt: %s %s" % (r, rs))
    for n in SUBLADDER_GRIDS:
        if n in [a for _nm, a, _s in LEVELS]:
            refuse("sub-ladder grid 1/%d IS a ladder level" % n)
    if [SUBLADDER_GRIDS[i + 1] / SUBLADDER_GRIDS[i] for i in range(2)] != [2.0, 2.0]:
        refuse("the sub-ladder is not a factor-2 family")
    return dict(control="constant_ratio_refinement_h_and_dt_and_subladder_disjoint", h_ratios=r, step_ratios=rs, passed=True)


def control_subladder_registration():
    """GATE_MODE is ADMITTED, not chosen freely: for every quantity the registered
    mode must be one the sub-ladder triple admits through roache_triple
    (CONVERGING admits only GATED-EXTRAPOLATED; anything else admits only
    GATED-ABSOLUTE or REPORTED-NOT-GATED); an extrapolated gate's observed order
    must lie in [0.3, 3]; the derivation is shown able to say both no (a planted
    equal-increment series) and yes (a planted power law)."""
    _registered()
    detail = {}
    for q in QUANTITIES:
        tri = subladder_triple(q)
        allowed = mode_allowed(q)
        if GATE_MODE[q] not in allowed:
            refuse("GATE_MODE[%r] is registered %s but the sub-ladder triple is %s, which admits only %s"
                   % (q, GATE_MODE[q], tri["state"], allowed))
        detail[q] = dict(registered=GATE_MODE[q], admitted=allowed, triple=tri)
        if GATE_MODE[q] == "GATED-EXTRAPOLATED":
            gs = gate_specs()[q]
            if not (0.3 <= gs["p_observed"] <= 3.0):
                refuse("sub-ladder order for %s is %.3f, outside [0.3, 3]" % (q, gs["p_observed"]))
            detail[q].update(p_observed=gs["p_observed"], p_used=gs["p_used"], fine_pred=gs["fine_pred"])
    planted = [dict(name="a", cells=512, value=1.2), dict(name="b", cells=2048, value=1.1), dict(name="c", cells=8192, value=1.0)]
    st = RT.all_triples(planted, 2)[-1]["state"]
    if st == "CONVERGING":
        refuse("PLANTED CONTROL FAILED: an equal-increment series was classified CONVERGING; the mode derivation cannot say no")
    planted2 = [dict(name="a", cells=512, value=1.2), dict(name="b", cells=2048, value=1.1), dict(name="c", cells=8192, value=1.05)]
    st2 = RT.all_triples(planted2, 2)[-1]["state"]
    if st2 != "CONVERGING":
        refuse("PLANTED CONTROL FAILED: a halving-error series was classified %s; the mode derivation cannot say yes" % st2)
    detail["planted_equal_increments"] = dict(state=st, admits=("GATED-ABSOLUTE", "REPORTED-NOT-GATED"))
    detail["planted_power_law"] = dict(state=st2, admits=("GATED-EXTRAPOLATED",))
    return dict(control="PZ-F24-GATE_MODE_admitted_by_subladder_triple_through_roache_triple", detail=detail, passed=True)


def selftest_predicate(controls):
    if len(controls) != 6:
        return False, "expected 6 controls, ran %d" % len(controls)
    for c in controls:
        if not c.get("passed"):
            return False, "control %s did not pass" % c.get("control")
    if not __debug__:
        return False, "running under -O"
    return True, ("6 controls green: nu(M) closed form equals its defining integral and nu(M2) - nu(M1) is the registered "
                  "deflection; gamma planted at 1.1x breaks the identity; the fan field is continuous at both rays, "
                  "satisfies the ray relation to 1e-12 and the X_LINE column crosses the whole fan; the box sits below "
                  "the tail ray; the ladder and sub-ladder refine by exactly 2 and are disjoint; every registered GATE_MODE "
                  "is admitted by its sub-ladder triple through roache_triple, and the derivation says no to a planted "
                  "equal-increment series and yes to a planted power law")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    controls = [control_nu_closed_form_matches_quadrature(), control_substitution_is_able_to_fail(),
                control_fan_field(), control_box_lies_in_region_2(), control_ladder_is_geometrically_similar(),
                control_subladder_registration()]
    tab = predictions()
    s2 = state2()
    if a.json:
        print(json.dumps(dict(state2=s2, levels=tab, gate_specs=gate_specs(), controls=controls),
                         indent=2, default=str))
        return 0
    ok, why = selftest_predicate(controls)
    if a.selftest:
        print(json.dumps(dict(controls=controls, state2=s2, levels=tab, gate_specs=gate_specs(),
                              predicate=dict(ok=ok, why=why)), indent=2, default=str))
        if not ok:
            refuse("SELFTEST DID NOT ESTABLISH ITS CLAIM: %s" % why)
        print("\nSELFTEST GREEN -- %s" % why)
        return 0
    print("M1=%g delta=%g deg -> M2=%.12f p2/p1=%.12f T2/T1=%.12f mu1=%.4f mu2=%.4f head=%.4f tail=%.4f"
          % (M1, DELTA_DEG, s2["M2"], s2["p2_over_p1"], s2["T2_over_T1"], s2["mu1_deg"], s2["mu2_deg"], s2["phi_head_deg"], s2["phi_tail_deg"]))
    for r in tab:
        print("%-7s N=%d cells=%d h=%.6g dt=%.3e steps=%d  p_box err pred %s  M_box err pred %s  p_line pred %s"
              % (r["name"], r["n"], r["cells"], r["h"], r["dt"], r["steps"], r["p_box_err_pred"], r["M_box_err_pred"], r["p_line_err_pred"]))
    print(json.dumps(gate_specs(), indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
