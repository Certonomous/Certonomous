#!/usr/bin/env python3
"""
F23 -- THE EXACT SOLUTION of fully developed Hagen-Poiseuille pipe flow, and
the DISCRETISATION-DERIVED error prediction every F23 band is built from.

    u(r) = 2 Ubar (1 - r^2/R^2),   -dp/dx = G = 8 nu Ubar / R^2,   f.Re = 64
    R = 0.5 (D = 1), nu = 0.01, Ubar = 1  ->  Re_D = 100, G = 0.32, u_max = 2

THE CASE IS FULLY DEVELOPED BY CONSTRUCTION -- streamwise CYCLIC with a FIXED
body force G (constant/fvOptions, vectorSemiImplicitSource, volumeMode
specific).  Chosen over a developing inlet/outlet pipe because the closed form
is then an exact solution of the case as posed (a developing pipe has no
closed form and the developed length is itself a discretisation-dependent
quantity), and chosen over an adaptive `meanVelocityForce` so the discrete
problem is LINEAR and the bulk velocity is a READ quantity: G is imposed,
Ubar_h is read from the field, and f.Re_h = 2 D^2 G / (nu Ubar_h).

THE REFERENCE IS NOT A PAPER ON THIS BOX.  IT IS A SUBSTITUTION.
The profile is substituted symbolically into the axisymmetric x-momentum
equation  nu (1/r) d/dr (r du/dr) + G = 0  at selftest (residual identically
zero); a planted control (R scaled 1.1 inside the profile) must make the
residual non-zero.  The integral identities Ubar = (2/R^2) int u r dr and
f.Re = 64 are checked symbolically too.

THE BAND PRINCIPLE -- derived from the discretisation, not measured.
On the fully developed cyclic wedge the x-faces cancel identically and the
convection term is null, so simpleFoam's steady discrete x-momentum equation
per cell reduces EXACTLY to the radial stencil

    sum_f  nu |S_f| (u_N - u_P) / |d_f|  +  G V_P = 0

with |S_f|, V_P and |d_f| the wedge mesh's OWN face areas, cell volumes and
centroid-to-centroid distances (Gauss linear corrected Laplacian on a mesh
that is orthogonal in the r-x plane; the wedge patches contribute nothing
to the x-component; the wall is a fixedValue face at distance |C_f - C_P|).
`discrete()` builds that tridiagonal system on the exact blockMesh geometry
(chord faces at y = r_f cos a, z = +/- r_f sin a; trapezoid centroids) and
solves it.  The prediction is therefore a function of the SCHEME, the GRID and
the WEDGE ANGLE and nothing else.

THE WEDGE BIAS, CARRIED EXPLICITLY (NUMERICS_KNOWLEDGE N-AV9): a wedge cell
is flat-sided, so the discrete solution converges to (1 + O(a^2)) times the
polar discrete solution, an error grid refinement does not remove.  The model
contains it exactly (the cos a / sin a factors are the mesh's).  The half
angle a = HALF_ANGLE_DEG is registered so that the bias at the FINE level is
below a tenth of the fine level's predicted discretisation error -- a control
refuses otherwise -- and the bias is printed per level as
model(a) - model(a -> 0).

WHAT THE MODEL OMITS, stated: SIMPLE's iterative tolerance (the census in
grade_f23.py gates it), the pressure-velocity coupling (identically inactive:
p is uniform on the cyclic domain), any x-non-uniformity (printed by the
grader as a diagnostic), floating-point ordering across 4 ranks.  Hence a
FACTOR-3 window, declared before compute, not an equality.

Refusals are `raise` and `sys.exit(2)`.  Zero `assert` (L-332).
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: exact_f23.py must not run under `python3 -O` (the shared "
                     "roache_triple.py seals rule 1 and rule 5 with checks -O would blind).\n")
    sys.exit(2)

import json
import math
import argparse

import numpy as np

# ---------------------------------------------------------------------------
# THE CASE, FROZEN.
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
N_ITER = 4000                             # simpleFoam iterations, fixed (controlDict endTime)
WRITE_EVERY = 100                         # checkpoints for the Class C series


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def h_of(nr):
    return R / float(nr)


def u_exact(r):
    return 2.0 * UBAR * (1.0 - (np.asarray(r, dtype=float) / R) ** 2)


def wedge_geometry(nr, half_angle_deg=HALF_ANGLE_DEG):
    """The blockMesh wedge's own geometry per radial cell, per unit dx.

    Faces at polar radius r_f = j dr are planar chords with centre y = r_f cos a
    and half-width z = r_f sin a; the cell j is the trapezoid between chords j
    and j+1 (a triangle at the axis).  Returns dict of arrays over cells /
    faces.  half_angle_deg=None gives the POLAR LIMIT (a -> 0, per unit angle).
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
    """Assemble and solve the radial stencil simpleFoam reduces to on this
    mesh.  Returns the discrete profile and the derived scalar predictions."""
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
    # centres must NOT satisfy the discrete equations (non-zero truncation
    # residual), or the stencil evaluator sees nothing.
    trunc = float(np.max(np.abs(M @ u_exact(yc) - b)))
    ubar_h = float(np.sum(V * u) / np.sum(V))
    e2n = e2_normalised(u, ubar_h, yc, V)
    fre = f_re(ubar_h)
    return dict(nr=nr, h=h_of(nr), u=u, yc=yc, vol=V, ubar_h=ubar_h,
                E2n_pred=e2n, fRe_pred=fre, fRe_err_pred=fre - F_RE_EXACT,
                solve_residual_max=resid, truncation_residual_max=trunc,
                half_angle_deg=half_angle_deg)


def e2_normalised(u, ubar_h, yc, V):
    """G-F23-1: volume-weighted L2 error of the NORMALISED profile u/Ubar_h
    against 2(1 - r^2/R^2) at the mesh's own cell centres, over one station."""
    return float(math.sqrt(np.sum(V * (u / ubar_h - u_exact(yc) / UBAR) ** 2) / np.sum(V)))


def f_re(ubar_h):
    """G-F23-2: f.Re from the imposed G and the READ bulk velocity."""
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
    return dict(control="PZ-F23-RADIUS_planted_1.1x_must_be_nonzero", planted_factor=1.1,
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
               "discretisation error (%.3e); a smaller half angle is required" % (fine["wedge_bias_E2n"], fine["E2n_polar"]))
    if abs(fine["wedge_bias_fRe"]) > 0.1 * abs(fine["fRe_polar"] - F_RE_EXACT):
        refuse("WEDGE ANGLE INADMISSIBLE for f.Re: bias %.3e vs discretisation %.3e"
               % (fine["wedge_bias_fRe"], fine["fRe_polar"] - F_RE_EXACT))
    signs = [np.sign(row["fRe_err_pred"]) for row in tab]
    if not (signs[0] == signs[1] == signs[2]):
        refuse("the model's predicted f.Re error changes sign across the ladder %s: the triple would be "
               "OSCILLATORY by prediction and the gate must not be registered on it" % [row["fRe_err_pred"] for row in tab])
    p_e2w, p_frw = model_orders(polar=False)
    return dict(control="model_solved_second_order_and_wedge_bias_admissible", polar_orders_E2n=p_e2,
                polar_orders_fRe=p_fr, wedge_orders_E2n=p_e2w, wedge_orders_fRe=p_frw,
                fine_bias_E2n=fine["wedge_bias_E2n"], fine_bias_fRe=fine["wedge_bias_fRe"],
                fine_E2n_polar=fine["E2n_polar"], half_angle_deg=HALF_ANGLE_DEG, passed=True)


def selftest_predicate(controls):
    if len(controls) != 4:
        return False, "expected 4 controls, ran %d" % len(controls)
    for c in controls:
        if not c.get("passed"):
            return False, "control %s did not pass" % c.get("control")
    if not __debug__:
        return False, "running under -O"
    return True, ("4 controls green: the profile satisfies the axisymmetric momentum equation identically "
                  "with Ubar = 1 and f.Re = 64 under symbolic substitution; R planted at 1.1x makes the "
                  "residual non-zero; the ladder refines by exactly 2 in r and x with square cells; the "
                  "discretisation model is solved to round-off, sees a non-zero truncation residual on the "
                  "exact profile, is second order in the polar limit, and the registered wedge half angle's "
                  "N-AV9 bias is below a tenth of the fine level's discretisation error")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    controls = [control_symbolic_substitution(), control_substitution_is_able_to_fail(),
                control_ladder_is_geometrically_similar(),
                control_model_is_solved_second_order_and_wedge_admissible()]
    tab = predictions()
    if a.json:
        print(json.dumps(dict(constants=dict(R=R, D=D, nu=NU, Ubar=UBAR, Re=RE, G=G, L=L,
                                             half_angle_deg=HALF_ANGLE_DEG, n_iter=N_ITER,
                                             write_every=WRITE_EVERY, ranks=RANKS),
                              levels=[dict((k, v) for k, v in r.items()) for r in tab],
                              orders=dict(wedge=model_orders(), polar=model_orders(polar=True)),
                              controls=controls), indent=2, default=str))
        return 0
    ok, why = selftest_predicate(controls)
    if a.selftest:
        print(json.dumps(dict(controls=controls, levels=tab, orders=dict(wedge=model_orders(), polar=model_orders(polar=True)),
                              predicate=dict(ok=ok, why=why)), indent=2, default=str))
        if not ok:
            refuse("SELFTEST DID NOT ESTABLISH ITS CLAIM: %s" % why)
        print("\nSELFTEST GREEN -- %s" % why)
        return 0
    print("R=%g nu=%g Ubar=%g Re=%g G=%g L=%g half-angle=%g deg" % (R, NU, UBAR, RE, G, L, HALF_ANGLE_DEG))
    for r in tab:
        print("%-7s nr=%d nx=%d cells=%d h=%.6g  E2n_pred=%.6e (polar %.6e, bias %+.2e)  fRe_pred=%.9f (err %+.3e, polar err %+.3e)"
              % (r["name"], r["nr"], r["nx"], r["cells"], r["h"], r["E2n_pred"], r["E2n_polar"], r["wedge_bias_E2n"],
                 r["fRe_pred"], r["fRe_err_pred"], r["fRe_polar"] - F_RE_EXACT))
    print("model orders (wedge): E2n %s  fRe %s" % model_orders())
    print("model orders (polar): E2n %s  fRe %s" % model_orders(polar=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
