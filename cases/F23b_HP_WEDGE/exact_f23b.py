#!/usr/bin/env python3
"""
F23b -- THE EXACT SOLUTION of fully developed Hagen-Poiseuille pipe flow, the
DISCRETISATION-DERIVED error prediction every F23b band is built from, and the
FROZEN TOLERANCE TABLES of the pre-registration.

Registration: verification/campaign/F23b_HP_WEDGE_PREREGISTRATION.md
              frozen at 57d31dde, AMENDMENT 1 (pre-compute) at 440aca3d.

    u(r) = 2 Ubar (1 - r^2/R^2),   -dp/dx = G = 8 nu Ubar / R^2,   f.Re = 64
    R = 0.5 (D = 1), nu = 0.01, Ubar = 1  ->  Re_D = 100, G = 0.32, u_max = 2

WHAT IS CARRIED FROM F23 BYTE-FOR-BYTE (prereg section 2 and section 6): the
case, HALF_ANGLE_DEG = 0.04, the ladder, the exact solution, the discrete model
`discrete()`, and EVERY predicted value and band.  Section 6 states in terms
that they are properties of the CONVERGED DISCRETE problem on the mesh's own
geometry and are therefore independent of the relaxation factor, the linear
solver tolerance and the iteration count -- which is why F23b is a
re-registration and not a new case.

WHAT F23b ADDS, and only this:
  * N_ITER 400 (was 4000) and WRITE_EVERY = N_ITER/40 (prereg section 5.3).
    The CHECKPOINT COUNT stays 40 and the Class C window stays 12 checkpoints.
    N_ITER is THE ONLY MOVABLE INPUT and section 5.5's branch rule is the only
    rule that may move it.
  * TOL_REL_WEDGE / TOL_CM -- the G-WEDGE tolerances (prereg section 4.3).
  * PLATEAU_TOL(gate, level) -- per-level plateau tolerances (prereg 5.4).
  * The tightened iterative floor UX_RES_TOL = 1e-12 (prereg section 7).
  * The arm-acceptance thresholds of section 5.5.

THE REFERENCE IS NOT A PAPER ON THIS BOX.  IT IS A SUBSTITUTION.  The profile is
substituted symbolically into the axisymmetric x-momentum equation at selftest
(residual identically zero); a planted control (R scaled 1.1 inside the profile)
must make the residual non-zero.

Refusals are `raise` and `sys.exit(2)`.  Zero `assert` (L-332).  Hard `-O`
refusal at entry.
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: exact_f23b.py must not run under `python3 -O` (the shared "
                     "roache_triple.py seals rule 1 and rule 5 with checks -O would blind).\n")
    sys.exit(2)

import json
import math
import argparse

import numpy as np

# ---------------------------------------------------------------------------
# THE CASE, FROZEN.  Byte-for-byte F23 (prereg section 2).
# ---------------------------------------------------------------------------
R = 0.5                                   # pipe radius
D = 2.0 * R                               # 1.0
NU = 0.01
UBAR = 1.0
RE = UBAR * D / NU                        # 100
G = 8.0 * NU * UBAR / R ** 2              # 0.32 = -dp/dx, the fvOptions source per unit volume
U_MAX = 2.0 * UBAR
F_RE_EXACT = 64.0
L = 16.0 * D                              # streamwise extent (cyclic); buys cells, not accuracy
HALF_ANGLE_DEG = 0.04                     # wedge HALF angle (0.08 deg total); N-AV9 bias ~ 2 a^2 ~ 1e-6
X_STATION_FRAC = 0.5                      # the graded station: the x-column nearest x = L/2 + dx/2
# name, NR (radial cells), NX (axial cells); dx = dr = R/NR at every level
LEVELS = (("coarse", 64, 2048), ("medium", 128, 4096), ("fine", 256, 8192))
RANKS = 4                                 # every level: decomposePar simple n (1 4 1)

# ---------------------------------------------------------------------------
# THE ITERATION COUNT -- prereg section 5.3.  N_ITER is the ONE movable input
# (section 5.5); WRITE_EVERY is DERIVED from it and the checkpoint count is
# FIXED at 40, so a moved N_ITER never silently moves a criterion defined in
# checkpoints (F17c section 8.4's warning).
# ---------------------------------------------------------------------------
N_ITER = 400                              # registered value; section 5.5 rule 1
CHECKPOINTS = 40                          # FROZEN.  Never derived, never moved.
CLASS_C_WINDOW = 12                       # FROZEN, in CHECKPOINTS (section 5.3)


def write_every(n_iter=None):
    """writeInterval = N_ITER / CHECKPOINTS, an integer by construction."""
    n = N_ITER if n_iter is None else int(n_iter)
    if n % CHECKPOINTS != 0:
        refuse("N_ITER = %d is not a multiple of the frozen checkpoint count %d; "
               "writeInterval would not be an integer and the Class C series would "
               "not carry %d samples" % (n, CHECKPOINTS, CHECKPOINTS))
    return n // CHECKPOINTS


WRITE_EVERY = N_ITER // CHECKPOINTS       # 10 at N_ITER = 400

# ---------------------------------------------------------------------------
# G-WEDGE -- prereg section 4.3.  FROZEN TABLES.
#
# HOW THE TABLE WAS DERIVED, AND WHY IT IS FROZEN AS A TABLE RATHER THAN AS A
# FORMULA.  Section 4.3 registers
#
#     TOL_REL_WEDGE(level) = max( 0.1 x |E_pred_fRe(level)| / 64 , FLOOR_REL )
#
# and tabulates the three values to seven digits.  The tabulated values are that
# formula evaluated at the FOUR-SIGNIFICANT-FIGURE E_pred_fRe of the section 4.3
# table (-7.778e-03 / -1.922e-03 / -4.571e-04), NOT at the model's full-precision
# prediction: 0.1 x 0.007778 / 64 = 1.2153125e-05 -> the registered 1.215313e-05,
# where the full-precision model gives 1.2153769e-05.  The registered number is
# the FROZEN THRESHOLD, so the table is authoritative and the formula is carried
# as a CHECK on it (control_wedge_tolerances_are_the_registered_ones), never as
# the source.  A threshold recomputed at grade time is not a frozen threshold.
# ---------------------------------------------------------------------------
FLOOR_REL = 1.0e-08                       # FROZEN; never binds on this ladder
K_CM = 1.0                                # FROZEN; textbook sequential-summation bound
EPS_MACH = 2.220446049250313e-16          # FROZEN

TOL_REL_WEDGE = {"coarse": 1.215313e-05, "medium": 3.003125e-06, "fine": 7.142188e-07}
# the four-significant-figure predicted f.Re errors the table above was built from
E_PRED_FRE_TABULATED = {"coarse": -7.778e-03, "medium": -1.922e-03, "fine": -4.571e-04}
# section 4.3 limb 2, tabulated to seven digits; the formula is carried below as a check
TOL_CM_DEG = {"coarse": 2.874681e-06, "medium": 9.674350e-06, "fine": 3.824547e-05}
# section 4.4 / AMENDMENT 1 section A1.4: the CONTROL's acceptance band on the ratio
# of the planted reading to the tolerance.  A band on a control's reading, not a gate.
GWEDGE_PLANT_RATIO = 3.0
GWEDGE_PLANT_RATIO_BAND = (2.9, 3.1)
GWEDGE_ACCEPT_CEILING = 1.0e-08           # AMENDMENT 1 table: the MUST-ACCEPT limb
GWEDGE_ROUNDTRIP_TOL = 1.0e-14            # C-4: the plant must survive its own file format

MAX_NON_ORTHO = 70.0                      # MESH_STANDARD section 3, byte-for-byte F23
MAX_SKEW = 4.0
ASPECT_ADVISORY = 1000.0

# ---------------------------------------------------------------------------
# THE ITERATIVE FLOOR AND THE PLATEAU TOLERANCES -- prereg sections 5.4 and 7.
# ---------------------------------------------------------------------------
UX_RES_TOL = 1.0e-12                      # was 1e-8 in F23; section 7 limb (1)(a)
TRANSVERSE_FIELD_TOL = 1.0e-10            # x U_MAX, on max|Uy|, max|Uz| at endTime

# section 5.4: PLATEAU_TOL(gate, level) = min(2.0e-04, 0.1 x |E_pred| / scale).
# For E2n the gate quantity IS an error norm, so the L-346 bound is 0.1 relative
# and 2.0e-04 binds at every level.  For f.Re the L-346 bound is TOL_REL_WEDGE
# and binds at every level.  FROZEN, for the reason given above the wedge table.
PLATEAU_TOL_CEILING = 2.0e-04
PLATEAU_TOL = {
    "G-F23b-1_E2_normalised_profile": {"coarse": 2.000000e-04, "medium": 2.000000e-04,
                                       "fine": 2.000000e-04},
    "G-F23b-2_f_Re": {"coarse": 1.215313e-05, "medium": 3.003125e-06, "fine": 7.142188e-07},
}
PLATEAU_VAR_RATIO = (0.2, 5.0)            # unchanged from F23
PLATEAU_MIN_SAMPLES = 20                  # Class C element 4

# ---------------------------------------------------------------------------
# THE PRE-LADDER ARMS -- prereg section 5.5 and AMENDMENT 1 section A1.5.
# ---------------------------------------------------------------------------
ARM_UBAR_TOL = 1.0e-10                    # |1 - Ubar| acceptance
ARM_UX_RES_TOL = 1.0e-12                  # Ux initial residual at acceptance
ARM_N_ACCEPT = 80                         # branch rule 1: accepts at n <= 80
ARM_N_MAX = 400                           # branch rule 3: does not accept by 400 -> ARM-F
A0_NR, A0_NX = 16, 64                     # AMENDMENT 1 item A0, the birth control mesh
A0_N_ITER = 4000                          # A0 runs under F23's alpha_U = 0.7 dictionary

BAND_FACTOR = 3.0                         # THE ONE DECLARED PARAMETER both bands are built from


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def level_names():
    return [n for n, _nr, _nx in LEVELS]


def n_wedge_faces(name):
    """Faces per wedge patch = NR x NX (one wedge face per cell, both patches)."""
    for nm, nr, nx in LEVELS:
        if nm == name:
            return nr * nx
    refuse("unknown level %r" % name)


def tol_cm_formula(name):
    """Section 4.3 limb 2, evaluated.  Carried as a CHECK on TOL_CM_DEG."""
    a = math.radians(HALF_ANGLE_DEG)
    return (HALF_ANGLE_DEG * TOL_REL_WEDGE[name]
            + K_CM * n_wedge_faces(name) * EPS_MACH / math.sin(a) * 180.0 / math.pi)


def h_of(nr):
    return R / float(nr)


def u_exact(r):
    return 2.0 * UBAR * (1.0 - (np.asarray(r, dtype=float) / R) ** 2)


def wedge_geometry(nr, half_angle_deg=HALF_ANGLE_DEG):
    """The blockMesh wedge's own geometry per radial cell, per unit dx.

    Faces at polar radius r_f = j dr are planar chords with centre y = r_f cos a
    and half-width z = r_f sin a; the cell j is the trapezoid between chords j
    and j+1 (a triangle at the axis).  half_angle_deg=None gives the POLAR LIMIT.
    Byte-for-byte F23 (prereg section 2).
    """
    rf = np.linspace(0.0, R, nr + 1)
    rt = (2.0 / 3.0) * (rf[1:] ** 3 - rf[:-1] ** 3) / (rf[1:] ** 2 - rf[:-1] ** 2)   # polar centroid
    if half_angle_deg is None:
        ca, sa = 1.0, 1.0
    else:
        a = math.radians(half_angle_deg)
        ca, sa = math.cos(a), math.sin(a)
    yc = ca * rt                           # the mesh's cell centre (on z = 0)
    area = 2.0 * rf * sa                   # chord face areas per unit dx (area[0] = 0: the axis)
    vol = sa * ca * (rf[1:] ** 2 - rf[:-1] ** 2)   # trapezoid areas per unit dx
    y_wall = R * ca                        # wall face centre
    return dict(nr=nr, rf=rf, rt=rt, yc=yc, area=area, vol=vol, y_wall=y_wall, ca=ca, sa=sa)


def discrete(nr, half_angle_deg=HALF_ANGLE_DEG):
    """Assemble and solve the radial stencil simpleFoam reduces to on this mesh.

    On the fully developed cyclic wedge the x-faces cancel identically and the
    convection term is null, so the steady discrete x-momentum equation per cell
    reduces EXACTLY to  sum_f nu |S_f| (u_N - u_P)/|d_f| + G V_P = 0  with the
    wedge mesh's OWN face areas, volumes and centroid distances.  Byte-for-byte
    F23: the prediction is a function of the SCHEME, the GRID and the WEDGE ANGLE
    and nothing else -- in particular NOT of the relaxation factor or N_ITER.
    """
    g = wedge_geometry(nr, half_angle_deg)
    yc, A, V = g["yc"], g["area"], g["vol"]
    M = np.zeros((nr, nr))
    b = -G * V
    for j in range(nr):
        if j > 0:
            c = NU * A[j] / (yc[j] - yc[j - 1])
            M[j, j] -= c
            M[j, j - 1] += c
        if j < nr - 1:
            c = NU * A[j + 1] / (yc[j + 1] - yc[j])
            M[j, j] -= c
            M[j, j + 1] += c
        else:
            c = NU * A[j + 1] / (g["y_wall"] - yc[j])     # wall: u = 0 at the face centre
            M[j, j] -= c
    u = np.linalg.solve(M, b)
    resid = float(np.max(np.abs(M @ u - b)))
    # PLANTED CONTROL on the evaluator: the exact profile at the mesh's own
    # centres must NOT satisfy the discrete equations, or the stencil evaluator
    # sees nothing.
    trunc = float(np.max(np.abs(M @ u_exact(yc) - b)))
    ubar_h = float(np.sum(V * u) / np.sum(V))
    e2n = e2_normalised(u, ubar_h, yc, V)
    fre = f_re(ubar_h)
    return dict(nr=nr, h=h_of(nr), u=u, yc=yc, vol=V, ubar_h=ubar_h,
                E2n_pred=e2n, fRe_pred=fre, fRe_err_pred=fre - F_RE_EXACT,
                solve_residual_max=resid, truncation_residual_max=trunc,
                half_angle_deg=half_angle_deg)


def e2_normalised(u, ubar_h, yc, V):
    """G-F23b-1: volume-weighted L2 error of the NORMALISED profile u/Ubar_h
    against 2(1 - r^2/R^2) at the mesh's own cell centres, over one station."""
    return float(math.sqrt(np.sum(V * (u / ubar_h - u_exact(yc) / UBAR) ** 2) / np.sum(V)))


def f_re(ubar_h):
    """G-F23b-2: f.Re from the imposed G and the READ bulk velocity."""
    return float(2.0 * D ** 2 * G / (NU * ubar_h))


_CACHE = {}


def model(name):
    lv = dict((n, nr) for n, nr, _nx in LEVELS)
    if name not in lv:
        refuse("unknown level %r" % name)
    if name not in _CACHE:
        _CACHE[name] = discrete(lv[name])
    return _CACHE[name]


def predictions():
    if "table" not in _CACHE:
        tab = []
        for name, nr, nx in LEVELS:
            m = model(name)
            p = discrete(nr, None)                       # polar limit: the wedge bias removed
            tab.append(dict(name=name, nr=nr, nx=nx, cells=nr * nx, h=h_of(nr),
                            E2n_pred=m["E2n_pred"], fRe_pred=m["fRe_pred"], fRe_err_pred=m["fRe_err_pred"],
                            ubar_h_pred=m["ubar_h"],
                            E2n_polar=p["E2n_pred"], fRe_polar=p["fRe_pred"],
                            wedge_bias_E2n=m["E2n_pred"] - p["E2n_pred"],
                            wedge_bias_fRe=m["fRe_pred"] - p["fRe_pred"],
                            wedge_bias_ubar=m["ubar_h"] - p["ubar_h"],
                            solve_residual_max=m["solve_residual_max"],
                            truncation_residual_max=m["truncation_residual_max"]))
        _CACHE["table"] = tab
    return _CACHE["table"]


def model_orders(polar=False):
    key = "E2n_polar" if polar else "E2n_pred"
    keyf = "fRe_polar" if polar else "fRe_pred"
    tab = predictions()
    p_e2 = [math.log(tab[i][key] / tab[i + 1][key]) / math.log(2.0) for i in range(2)]
    p_fr = [math.log(abs(tab[i][keyf] - F_RE_EXACT) / abs(tab[i + 1][keyf] - F_RE_EXACT)) / math.log(2.0)
            for i in range(2)]
    return p_e2, p_fr


# ---------------------------------------------------------------------------
# CONTROLS
# ---------------------------------------------------------------------------
def _sym(R_factor=1):
    import sympy as sp
    r = sp.symbols("r", positive=True)
    Rs = sp.Rational(1, 2) * R_factor
    nu = sp.Rational(1, 100)
    ub = sp.Integer(1)
    u = 2 * ub * (1 - r ** 2 / Rs ** 2)
    Gs = 8 * nu * ub / sp.Rational(1, 2) ** 2          # the REGISTERED G (R = 1/2), never the planted one
    return sp, r, Rs, nu, ub, u, Gs


def control_symbolic_substitution():
    try:
        import sympy  # noqa: F401
    except ImportError:
        refuse("sympy is not importable; the exact solution cannot be verified by substitution")
    sp, r, Rs, nu, ub, u, Gs = _sym()
    mom = sp.simplify(nu / r * sp.diff(r * sp.diff(u, r), r) + Gs)
    ubar = sp.simplify(2 / Rs ** 2 * sp.integrate(u * r, (r, 0, Rs)))
    fre = sp.simplify(2 * (2 * Rs) ** 2 * Gs / (nu * ubar))
    if mom != 0:
        refuse("SYMBOLIC SUBSTITUTION FAILED: axisymmetric x-momentum residual is %s, not 0" % mom)
    if ubar != ub:
        refuse("bulk velocity of the profile is %s, not Ubar" % ubar)
    if fre != 64:
        refuse("f.Re of the profile is %s, not 64" % fre)
    if abs(float(Gs) - G) > 1e-15:
        refuse("G in this module (%.17g) disagrees with the symbolic G (%.17g)" % (G, float(Gs)))
    return dict(control="symbolic_substitution_into_axisymmetric_momentum",
                momentum_residual=str(mom), ubar=str(ubar), f_re=str(fre), passed=True)


def control_substitution_is_able_to_fail():
    """PLANTED CONTROL (rule 3): R scaled 1.1 inside the profile must give a
    non-zero momentum residual against the registered G."""
    sp, r, Rs, nu, ub, u, Gs = _sym(R_factor=sp_rational_11_10())
    mom = sp.simplify(nu / r * sp.diff(r * sp.diff(u, r), r) + Gs)
    if mom == 0:
        refuse("PLANTED CONTROL FAILED: R planted at 1.1x still gave a zero momentum residual")
    return dict(control="PZ-F23b-RADIUS_planted_1.1x_must_be_nonzero", planted_factor=1.1,
                residual=str(mom), passed=True)


def sp_rational_11_10():
    import sympy as sp
    return sp.Rational(11, 10)


def control_ladder_is_geometrically_similar():
    for name, nr, nx in LEVELS:
        if abs(L / nx - R / nr) > 1e-14:
            refuse("level %s has dx != dr: %.17g vs %.17g" % (name, L / nx, R / nr))
    rr = [LEVELS[i + 1][1] / LEVELS[i][1] for i in range(2)]
    rx = [LEVELS[i + 1][2] / LEVELS[i][2] for i in range(2)]
    if max(abs(v - 2.0) for v in rr + rx) > 1e-12:
        refuse("the ladder is not a factor-2 refinement in both directions: %s %s" % (rr, rx))
    return dict(control="constant_ratio_refinement_both_directions_square_cells", r_ratios=rr, x_ratios=rx,
                passed=True)


def control_model_is_solved_second_order_and_wedge_admissible():
    tab = predictions()
    for row in tab:
        if row["solve_residual_max"] > 1e-10:
            refuse("model at level %s not solved: max residual %.3e" % (row["name"], row["solve_residual_max"]))
        if row["truncation_residual_max"] <= 0.0:
            refuse("PLANTED CONTROL FAILED: the stencil evaluator returned a zero truncation residual on the "
                   "exact profile at level %s; an evaluator that sees nothing is not evidence" % row["name"])
    p_e2, p_fr = model_orders(polar=True)
    if not all(1.7 <= p <= 2.3 for p in p_e2 + p_fr):
        refuse("the polar-limit model is not second order across the ladder: E2n orders %s, fRe orders %s"
               % (p_e2, p_fr))
    fine = tab[-1]
    if abs(fine["wedge_bias_E2n"]) > 0.1 * fine["E2n_polar"]:
        refuse("WEDGE ANGLE INADMISSIBLE: the N-AV9 bias at fine (%.3e) exceeds a tenth of the fine "
               "discretisation error (%.3e); a smaller half angle is required"
               % (fine["wedge_bias_E2n"], fine["E2n_polar"]))
    if abs(fine["wedge_bias_fRe"]) > 0.1 * abs(fine["fRe_polar"] - F_RE_EXACT):
        refuse("WEDGE ANGLE INADMISSIBLE for f.Re: bias %.3e vs discretisation %.3e"
               % (fine["wedge_bias_fRe"], fine["fRe_polar"] - F_RE_EXACT))
    signs = [np.sign(row["fRe_err_pred"]) for row in tab]
    if not (signs[0] == signs[1] == signs[2]):
        refuse("the model's predicted f.Re error changes sign across the ladder %s: the triple would be "
               "OSCILLATORY by prediction and the gate must not be registered on it"
               % [row["fRe_err_pred"] for row in tab])
    p_e2w, p_frw = model_orders(polar=False)
    return dict(control="model_solved_second_order_and_wedge_bias_admissible", polar_orders_E2n=p_e2,
                polar_orders_fRe=p_fr, wedge_orders_E2n=p_e2w, wedge_orders_fRe=p_frw,
                fine_bias_E2n=fine["wedge_bias_E2n"], fine_bias_fRe=fine["wedge_bias_fRe"],
                fine_E2n_polar=fine["E2n_polar"], half_angle_deg=HALF_ANGLE_DEG, passed=True)


def control_model_reproduces_the_registered_predictions():
    """The registration's section 6 table, to the digits it prints.  If this
    module's model has drifted from the frozen document, the bands below it are
    no longer the registered bands and NOTHING may grade against them."""
    want = {"coarse": (1.149980e-04, 63.992221588), "medium": (2.869164e-05, 63.998078262),
            "fine": (7.128682e-06, 63.999542924)}
    got = {}
    for row in predictions():
        e2, fre = want[row["name"]]
        got[row["name"]] = (row["E2n_pred"], row["fRe_pred"])
        if abs(row["E2n_pred"] - e2) > 5e-11:
            refuse("model E2n at %s is %.9e, the registration's section 6 prints %.6e"
                   % (row["name"], row["E2n_pred"], e2))
        if abs(row["fRe_pred"] - fre) > 5e-9:
            refuse("model f.Re at %s is %.9f, the registration's section 6 prints %.9f"
                   % (row["name"], row["fRe_pred"], fre))
    return dict(control="model_reproduces_prereg_section_6_predicted_values",
                registered=want, computed=got, passed=True)


def control_wedge_tolerances_are_the_registered_ones():
    """G-WEDGE's frozen tables, checked against the formulas the registration
    derives them from.  Section 4.3's TOL_REL_WEDGE is the formula at the
    registration's own FOUR-SIGNIFICANT-FIGURE E_pred (see the module header);
    section 4.3's TOL_CM is the formula at full precision, and reproduces the
    tabulated value to better than 1e-5 relative."""
    for name in level_names():
        want = max(0.1 * abs(E_PRED_FRE_TABULATED[name]) / F_RE_EXACT, FLOOR_REL)
        # The registration PRINTS the tolerance to seven significant figures and
        # that printed number is the frozen threshold, so the check is that the
        # formula ROUNDS to it at that precision -- not that it equals it in
        # binary.  Coarse (1.2153125e-05 -> 1.215313e-05) and fine
        # (7.1421875e-07 -> 7.142188e-07) round; medium is exact.
        if float("%.7g" % want) != TOL_REL_WEDGE[name]:
            refuse("TOL_REL_WEDGE[%s] = %.9e is not max(0.1 x |%.4e| / 64, %.1e) = %.9e "
                   "rounded to seven significant figures (%.7g)"
                   % (name, TOL_REL_WEDGE[name], E_PRED_FRE_TABULATED[name], FLOOR_REL, want, want))
        if TOL_REL_WEDGE[name] <= FLOOR_REL:
            refuse("TOL_REL_WEDGE[%s] has fallen to FLOOR_REL; the registration states the floor "
                   "does not bind on this ladder" % name)
        f = tol_cm_formula(name)
        if abs(f - TOL_CM_DEG[name]) > 1e-5 * TOL_CM_DEG[name]:
            refuse("TOL_CM[%s]: the section 4.3 formula gives %.9e, the registration tabulates %.9e"
                   % (name, f, TOL_CM_DEG[name]))
        if PLATEAU_TOL["G-F23b-2_f_Re"][name] != TOL_REL_WEDGE[name]:
            refuse("section 5.4's f.Re plateau tolerance at %s is not the L-346 bound" % name)
        if PLATEAU_TOL["G-F23b-1_E2_normalised_profile"][name] != PLATEAU_TOL_CEILING:
            refuse("section 5.4's E2n plateau tolerance at %s is not the 2.0e-04 ceiling" % name)
    # the SHAPE the registration states in terms: limb 2's occupancy FALLS with
    # refinement where F23's rose.  Measured occupancies from section 4.3.
    occ = [2.766821e-07 / TOL_CM_DEG["coarse"], 7.984975e-07 / TOL_CM_DEG["medium"],
           2.720290e-06 / TOL_CM_DEG["fine"]]
    if not (occ[0] > occ[1] > occ[2]):
        refuse("limb 2 occupancy does not fall with refinement: %s; that is the design criterion "
               "section 4.3 registers and it is not met" % occ)
    return dict(control="G-WEDGE_frozen_tolerance_tables_match_their_registered_derivations",
                TOL_REL_WEDGE=dict(TOL_REL_WEDGE), TOL_CM_DEG=dict(TOL_CM_DEG),
                TOL_CM_formula=dict((n, tol_cm_formula(n)) for n in level_names()),
                limb2_occupancy_falls=occ, passed=True)


def control_iteration_count_is_admissible():
    """N_ITER is the one movable input; every value section 5.5 can produce must
    leave writeInterval an integer and the checkpoint count at 40."""
    if write_every(N_ITER) * CHECKPOINTS != N_ITER:
        refuse("writeInterval x %d != N_ITER" % CHECKPOINTS)
    if CLASS_C_WINDOW > CHECKPOINTS:
        refuse("the Class C window (%d) exceeds the checkpoint count (%d)" % (CLASS_C_WINDOW, CHECKPOINTS))
    if PLATEAU_MIN_SAMPLES > CHECKPOINTS:
        refuse("Class C element 4's minimum (%d) exceeds the checkpoint count (%d)"
               % (PLATEAU_MIN_SAMPLES, CHECKPOINTS))
    # PLANTED: a non-multiple must REFUSE, or the integrality check is a constant.
    import subprocess
    probe = ("import sys; sys.path.insert(0, %r)\nimport exact_f23b as E\n"
             "try:\n    E.write_every(401)\n    print('CONTROL_FAILED_NO_REFUSAL')\n"
             "except SystemExit as e:\n    print('REFUSED' if e.code == 2 else 'WRONG_CODE')\n"
             % __HERE__)
    p = subprocess.run([sys.executable, "-c", probe], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if "REFUSED" not in p.stdout.decode():
        refuse("PLANTED CONTROL FAILED: write_every(401) did not refuse (got %r)"
               % p.stdout.decode().strip())
    if UX_RES_TOL >= 1.0e-8:
        refuse("UX_RES_TOL has not been tightened from F23's 1e-8; section 5 registers 1e-12")
    return dict(control="N_ITER_admissible_and_write_every_refuses_a_non_multiple",
                n_iter=N_ITER, write_every=WRITE_EVERY, checkpoints=CHECKPOINTS,
                class_c_window=CLASS_C_WINDOW, ux_res_tol=UX_RES_TOL,
                planted_401_refused=True, passed=True)


import os                                              # noqa: E402
__HERE__ = os.path.dirname(os.path.abspath(__file__))


CONTROLS = (control_symbolic_substitution, control_substitution_is_able_to_fail,
            control_ladder_is_geometrically_similar,
            control_model_is_solved_second_order_and_wedge_admissible,
            control_model_reproduces_the_registered_predictions,
            control_wedge_tolerances_are_the_registered_ones,
            control_iteration_count_is_admissible)


def selftest_predicate(controls):
    if len(controls) != len(CONTROLS):
        return False, "expected %d controls, ran %d" % (len(CONTROLS), len(controls))
    for c in controls:
        if not c.get("passed"):
            return False, "control %s did not pass" % c.get("control")
    if not __debug__:
        return False, "running under -O"
    return True, ("%d controls green: the profile satisfies the axisymmetric momentum equation "
                  "identically with Ubar = 1 and f.Re = 64 under symbolic substitution; R planted at "
                  "1.1x makes the residual non-zero; the ladder refines by exactly 2 in r and x with "
                  "square cells; the discretisation model is solved to round-off, sees a non-zero "
                  "truncation residual on the exact profile, is second order in the polar limit, and "
                  "the registered wedge half angle's N-AV9 bias is below a tenth of the fine level's "
                  "discretisation error; the model reproduces the registration's own section 6 table; "
                  "G-WEDGE's frozen tolerance tables match their registered derivations and limb 2's "
                  "occupancy FALLS with refinement; and write_every REFUSES a non-multiple of 40"
                  % len(CONTROLS))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    controls = [c() for c in CONTROLS]
    tab = predictions()
    if a.json:
        print(json.dumps(dict(constants=dict(R=R, D=D, nu=NU, Ubar=UBAR, Re=RE, G=G, L=L,
                                             half_angle_deg=HALF_ANGLE_DEG, n_iter=N_ITER,
                                             write_every=WRITE_EVERY, checkpoints=CHECKPOINTS,
                                             ranks=RANKS, ux_res_tol=UX_RES_TOL),
                              tolerances=dict(TOL_REL_WEDGE=TOL_REL_WEDGE, TOL_CM_DEG=TOL_CM_DEG,
                                              PLATEAU_TOL=PLATEAU_TOL),
                              levels=[dict((k, v) for k, v in r.items()) for r in tab],
                              orders=dict(wedge=model_orders(), polar=model_orders(polar=True)),
                              controls=controls), indent=2, default=str))
        return 0
    ok, why = selftest_predicate(controls)
    if a.selftest:
        print(json.dumps(dict(controls=controls, levels=tab,
                              orders=dict(wedge=model_orders(), polar=model_orders(polar=True)),
                              predicate=dict(ok=ok, why=why)), indent=2, default=str))
        if not ok:
            refuse("SELFTEST DID NOT ESTABLISH ITS CLAIM: %s" % why)
        print("\nSELFTEST GREEN -- %s" % why)
        return 0
    print("R=%g nu=%g Ubar=%g Re=%g G=%g L=%g half-angle=%g deg N_ITER=%d writeInterval=%d"
          % (R, NU, UBAR, RE, G, L, HALF_ANGLE_DEG, N_ITER, WRITE_EVERY))
    for r in tab:
        print("%-7s nr=%d nx=%d cells=%d h=%.6g  E2n_pred=%.6e (polar %.6e, bias %+.2e)  "
              "fRe_pred=%.9f (err %+.3e)  TOL_REL_WEDGE=%.6e  TOL_CM=%.6e deg"
              % (r["name"], r["nr"], r["nx"], r["cells"], r["h"], r["E2n_pred"], r["E2n_polar"],
                 r["wedge_bias_E2n"], r["fRe_pred"], r["fRe_err_pred"],
                 TOL_REL_WEDGE[r["name"]], TOL_CM_DEG[r["name"]]))
    print("model orders (wedge): E2n %s  fRe %s" % model_orders())
    print("model orders (polar): E2n %s  fRe %s" % model_orders(polar=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
