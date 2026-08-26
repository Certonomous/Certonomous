#!/usr/bin/env python3
"""
F25 -- THE EXACT SOLUTION of fully developed laminar flow in a SQUARE DUCT, and
the DISCRETISATION-DERIVED error prediction every F25 band is built from.
Lineage: cases/F23_HP_WEDGE/exact_f23.py (the cfd registration standard).

THE CASE.  Square duct of side 2A = 1 (hydraulic diameter D_h = 2A = 1),
nu = 0.01, streamwise CYCLIC with a FIXED body force G = -dp/dx (per unit
mass) applied to every cell (constant/fvOptions, vectorSemiImplicitSource,
volumeMode specific).  G is IMPOSED and the bulk velocity Ubar_h is READ from
the field, so f.Re_h = 2 D_h^2 G / (nu Ubar_h) (Darcy f = 2 D_h G / Ubar^2,
Re = Ubar D_h / nu).  G = 0.2845 puts Re_Dh = Ubar D_h / nu at 99.99 by the
exact series (Re_Dh ~ 100).  The discrete problem is LINEAR (as F23).

THE REFERENCE -- the series solution of the Poisson problem
    nu (u_yy + u_zz) + G = 0  on  |y'| < A, |z'| < A,   u = 0 on the walls,
(y', z' measured from the duct centre), in the closed-form-plus-exponential
form used here:

    u(y', z') = (G / 2 nu) (A^2 - y'^2)
              - (16 A^2 G / pi^3 nu) SUM_{i = 1, 3, 5, ...} (-1)^((i-1)/2)
                    cosh(i pi z' / 2A) / cosh(i pi / 2) . cos(i pi y' / 2A) / i^3

    Ubar = (A^2 G / 3 nu) [ 1 - (192 / pi^5) SUM_{i odd} tanh(i pi / 2) / i^5 ]
    f.Re = 2 D_h^2 G / (nu Ubar) = 24 / [ 1 - (192 / pi^5) SUM_{i odd} tanh(i pi / 2) / i^5 ]

The parabola is the 1-D Poiseuille solution between the walls y' = +/-A; every
series term cosh(k z') cos(k y') is harmonic, so the sum satisfies the Poisson
equation term by term (checked SYMBOLICALLY at selftest); on z' = +/-A the
series equals the parabola's own Fourier cosine series, so u = 0 there, and on
y' = +/-A both parts vanish (cos(i pi / 2) = 0 for odd i).  The cosh ratio
decays as exp(-i pi (A - |z'|) / 2A), so at every CELL CENTRE (never on the
wall) the series converges EXPONENTIALLY; the truncation is controlled here by
N_TERMS versus 2 N_TERMS (refused above CONV_TOL) and by the y <-> z symmetry
of the square (refused above CONV_TOL).  Ubar's tanh series converges as
1 / i^5 with tanh -> 1 exponentially; it is cross-checked against a
Gauss-Legendre quadrature of the field series (the field has an r^2 log r
corner behaviour, so that quadrature is algebraic: tolerance 1e-10, stated;
measured gap 8.8e-13 at 160 x 160 Gauss points).

SOURCE, STATED HONESTLY (rule 15).  This is the classical eigenfunction
solution of the rectangular-duct Poisson problem (Shah & London 1978, "Laminar
Flow Forced Convection in Ducts", rectangular-duct section; White, "Viscous
Fluid Flow", the rectangular-duct solution in chapter 3).  NO copy of either
is on disk under docs/papers/ (searched: shah / london / duct -> only Pinelli
et al. 2010 and Vinuesa et al. 2014, both turbulent DNS), so NO equation
number is cited from a document on this box.  The reference actually USED is
the derivation above, established by symbolic substitution in this file, and
the literature figure f.Re = 56.908 (square duct, Darcy form; the memory of
those texts, NOT a document on this box) is a CROSS-CHECK the series must
reproduce to 4 decimals (F_RE_LITERATURE below) -- the series is the
reference, the tabulated number is not.

THE BAND PRINCIPLE -- derived from the discretisation, not measured.  On the
fully developed cyclic duct with cubic cells every x-face contribution cancels
identically (u is x-uniform; the cyclic pair closes the column), convection is
null (v = w = 0, d/dx = 0) and grad p = 0, so simpleFoam's steady discrete
x-momentum equation per cell reduces EXACTLY to the 5-point cross-section
stencil of the `Gauss linear corrected` Laplacian on an orthogonal mesh:

    nu h SUM_{interior faces} (u_N - u_P)  -  2 nu h u_P (per wall face)  +  G h^3 = 0

with the wall a `noSlip` fixedValue face at distance h/2 from the cell centre.
`discrete()` assembles and solves that system on the blockMesh geometry (cell
centres at (j + 1/2) h, volumes h^3; build_f25.py checks the built mesh's own
0/C and 0/V against it and refuses otherwise).  The prediction is therefore a
function of the SCHEME and the GRID and nothing else.

THE L-345 CONTROL (a DEGENERATE prediction is a registration defect): the
model's own E2n and f.Re triples are classified through the SAME
scripts/roache_triple.py the grader uses (`triple_from_cells`, dim = 3); the
registration REFUSES unless both read CONVERGING with 1.7 <= p <= 2.3, and the
classifier is shown able to say DEGENERATE on a planted equal-increment
triple.

WHAT THE MODEL OMITS, stated: SIMPLE's iterative tolerance (the census in
grade_f25.py gates it; its floor is DERIVED from the predicted fine-level
error, L-346), the pressure-velocity coupling (identically inactive: p is
uniform on the cyclic domain), floating-point ordering across 4 ranks.  Hence
a FACTOR-3 window, declared before compute, not an equality.

Refusals are `raise` and `sys.exit(2)`.  Zero `assert` (L-332).
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: exact_f25.py must not run under `python3 -O` (the shared "
                     "roache_triple.py seals rule 1 and rule 5 with checks -O would blind).\n")
    sys.exit(2)

import os
import json
import math
import argparse

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_REPO, "scripts"))
import roache_triple as RT          # noqa: E402  -- the L-345 registration control uses THE gate's classifier

# ---------------------------------------------------------------------------
# THE CASE, FROZEN.
# ---------------------------------------------------------------------------
A = 0.5                                   # duct HALF-width; side 2A = 1
SIDE = 2.0 * A                            # 1.0
D_H = SIDE                                # hydraulic diameter of a square = its side
NU = 0.01
G = 0.2845                                # -dp/dx per unit mass, the fvOptions source (volumeMode specific)
F_RE_LITERATURE = 56.908                  # Darcy f.Re for the square duct -- cross-check only (see module docstring)
N_TERMS = 400                             # odd-i series terms (i = 1 .. 2 N_TERMS - 1); doubled by the control
CONV_TOL = 1.0e-13                        # absolute, on u (u_max ~ 2.1): N vs 2N terms, and y <-> z symmetry
UBAR_QUAD_TOL = 1.0e-10                  # tanh/zeta series vs Gauss-Legendre quadrature of the field series (measured 8.8e-13)
# name, NR (cells per cross-section side), NX (axial cells); cubic cells h = SIDE/NR, L = NX h = 8 D_h
LEVELS = (("coarse", 16, 128), ("medium", 32, 256), ("fine", 64, 512))
L = 8.0 * D_H                             # 8.0: streamwise extent (cyclic); buys cells for the hours order, not accuracy
X_STATION_FRAC = 0.5                      # the graded station: the x-slab nearest x = L/2 + dx/2
RANKS = 4                                 # every level: decomposePar simple n (1 2 2)
N_ITER = 4000                             # simpleFoam iterations, fixed (controlDict endTime)
WRITE_EVERY = 100                         # checkpoints for the Class C series
DIM = 3                                   # refinement by exactly 2 in ALL THREE directions


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def h_of(nr):
    return SIDE / float(nr)


# ---------------------------------------------------------------------------
# THE EXACT SOLUTION
# ---------------------------------------------------------------------------
def u_exact(y, z, n_terms=N_TERMS):
    """u at (y, z) in DUCT coordinates (0 <= y, z <= SIDE); vectorised."""
    yp = np.asarray(y, dtype=float) - A
    zp = np.asarray(z, dtype=float) - A
    if np.any(np.abs(yp) > A + 1e-12) or np.any(np.abs(zp) > A + 1e-12):
        refuse("u_exact evaluated outside the duct")
    para = (G / (2.0 * NU)) * (A ** 2 - yp ** 2)
    s = np.zeros(np.broadcast(yp, zp).shape)
    for k in range(n_terms):
        i = 2 * k + 1
        kk = i * math.pi / (2.0 * A)
        # cosh(kk z') / cosh(kk A) written as a sum of decaying exponentials (no overflow at large i)
        ratio = (np.exp(kk * (zp - A)) + np.exp(-kk * (zp + A))) / (1.0 + math.exp(-2.0 * kk * A))
        s += ((-1.0) ** k) * ratio * np.cos(kk * yp) / float(i) ** 3
    return para - (16.0 * A ** 2 * G / (math.pi ** 3 * NU)) * s


def _tanh_sum(n_terms):
    """SUM_{i odd} tanh(i pi / 2) / i^5, split as SUM 1/i^5 - SUM 2 / ((e^{i pi} + 1) i^5):
    the first is (1 - 2^-5) zeta(5) in closed form, the second converges EXPONENTIALLY
    (the raw tanh sum converges only as 1/N^4 and cannot reach machine precision)."""
    from scipy.special import zeta
    odd_zeta5 = (1.0 - 2.0 ** -5) * float(zeta(5.0, 1.0))
    # 2 / (e^x + 1) = 2 e^-x / (1 + e^-x): no overflow at large i
    tail = sum(2.0 * math.exp(-(2 * k + 1) * math.pi) / ((1.0 + math.exp(-(2 * k + 1) * math.pi)) * float(2 * k + 1) ** 5)
               for k in range(n_terms))
    return odd_zeta5 - tail


def ubar_exact(n_terms=N_TERMS):
    return (A ** 2 * G / (3.0 * NU)) * (1.0 - (192.0 / math.pi ** 5) * _tanh_sum(n_terms))


def f_re(ubar_h):
    """f.Re from the imposed G and a bulk velocity (Darcy f; Re on D_h)."""
    return float(2.0 * D_H ** 2 * G / (NU * ubar_h))


def f_re_exact(n_terms=N_TERMS):
    return f_re(ubar_exact(n_terms))


def re_dh():
    return ubar_exact() * D_H / NU


U_MAX = None      # filled lazily by u_max(): the centreline value of the exact profile


def u_max():
    global U_MAX
    if U_MAX is None:
        U_MAX = float(u_exact(A, A))
    return U_MAX


# ---------------------------------------------------------------------------
# THE DISCRETISATION MODEL -- the 5-point cross-section stencil, solved
# ---------------------------------------------------------------------------
def cross_section_geometry(nr):
    h = h_of(nr)
    c = (np.arange(nr) + 0.5) * h
    Y, Z = np.meshgrid(c, c, indexing="ij")          # (nr, nr): Y varies along axis 0
    return dict(nr=nr, h=h, yc=Y.ravel(), zc=Z.ravel(), vol=np.full(nr * nr, h ** 3))


def discrete(nr):
    """Assemble and solve the cross-section stencil simpleFoam reduces to on
    the cubic mesh.  Returns the discrete profile and the derived predictions."""
    from scipy.sparse import lil_matrix
    from scipy.sparse.linalg import spsolve
    g = cross_section_geometry(nr)
    h = g["h"]
    n = nr * nr
    M = lil_matrix((n, n))
    b = np.full(n, -G * h ** 3 / (NU * h))           # divided through by nu h
    for j in range(nr):
        for k in range(nr):
            p = j * nr + k
            diag = 0.0
            for (jj, kk) in ((j - 1, k), (j + 1, k), (j, k - 1), (j, k + 1)):
                if 0 <= jj < nr and 0 <= kk < nr:
                    M[p, jj * nr + kk] = 1.0
                    diag -= 1.0
                else:
                    diag -= 2.0                        # wall face at distance h/2: (0 - u_P)/(h/2) h^2 -> -2 h u_P
            M[p, p] = diag
    M = M.tocsr()
    u = spsolve(M, b)
    resid = float(np.max(np.abs(M @ u - b)))
    # PLANTED CONTROL on the evaluator: the exact profile at the mesh's own
    # centres must NOT satisfy the discrete equations (non-zero truncation
    # residual), or the stencil evaluator sees nothing.
    trunc = float(np.max(np.abs(M @ u_exact(g["yc"], g["zc"]) - b)))
    ubar_h = float(np.sum(g["vol"] * u) / np.sum(g["vol"]))
    e2n = e2_normalised(u, ubar_h, g["yc"], g["zc"], g["vol"])
    fre = f_re(ubar_h)
    return dict(nr=nr, h=h, u=u, yc=g["yc"], zc=g["zc"], vol=g["vol"], ubar_h=ubar_h,
                E2n_pred=e2n, fRe_pred=fre, fRe_err_pred=fre - f_re_exact(),
                solve_residual_max=resid, truncation_residual_max=trunc)


def e2_normalised(u, ubar_h, yc, zc, V):
    """G-F25-1: volume-weighted L2 error of the NORMALISED profile u/Ubar_h
    against u_exact/Ubar at the mesh's own cell centres, over one station."""
    return float(math.sqrt(np.sum(V * (u / ubar_h - u_exact(yc, zc) / ubar_exact()) ** 2) / np.sum(V)))


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
            tab.append(dict(name=name, nr=nr, nx=nx, cells=nr * nr * nx, h=h_of(nr),
                            E2n_pred=m["E2n_pred"], fRe_pred=m["fRe_pred"], fRe_err_pred=m["fRe_err_pred"],
                            ubar_h_pred=m["ubar_h"],
                            solve_residual_max=m["solve_residual_max"],
                            truncation_residual_max=m["truncation_residual_max"]))
        _CACHE["table"] = tab
    return _CACHE["table"]


def model_orders():
    tab = predictions()
    fre = f_re_exact()
    p_e2 = [math.log(tab[i]["E2n_pred"] / tab[i + 1]["E2n_pred"]) / math.log(2.0) for i in range(2)]
    p_fr = [math.log(abs(tab[i]["fRe_pred"] - fre) / abs(tab[i + 1]["fRe_pred"] - fre)) / math.log(2.0)
            for i in range(2)]
    return p_e2, p_fr


# ---------------------------------------------------------------------------
# CONTROLS
# ---------------------------------------------------------------------------
def _sym(A_factor=1):
    import sympy as sp
    y, z = sp.symbols("y z", real=True)
    As = sp.Rational(1, 2) * A_factor
    nu = sp.Rational(1, 100)
    Gs = sp.Rational(2845, 10000)                      # the REGISTERED G, never a planted one
    para = Gs / (2 * nu) * (As ** 2 - y ** 2)
    return sp, y, z, As, nu, Gs, para


def control_symbolic_substitution():
    """The parabola satisfies nu (u_yy + u_zz) + G = 0 identically; every
    series term cosh(k z) cos(k y) is harmonic for every k (symbolic k); on
    y = +/-A the term vanishes for odd i; on z = +/-A the series reproduces
    the parabola's Fourier coefficients (checked symbolically for the first
    three odd i by integrating the parabola against cos(i pi y / 2A))."""
    try:
        import sympy  # noqa: F401
    except ImportError:
        refuse("sympy is not importable; the exact solution cannot be verified by substitution")
    sp, y, z, As, nu, Gs, para = _sym()
    res_para = sp.simplify(nu * (sp.diff(para, y, 2) + sp.diff(para, z, 2)) + Gs)
    if res_para != 0:
        refuse("SYMBOLIC SUBSTITUTION FAILED: the parabola's Poisson residual is %s, not 0" % res_para)
    kk = sp.symbols("k", positive=True)
    term = sp.cosh(kk * z) * sp.cos(kk * y)
    res_term = sp.simplify(sp.diff(term, y, 2) + sp.diff(term, z, 2))
    if res_term != 0:
        refuse("SYMBOLIC SUBSTITUTION FAILED: the series term cosh(kz) cos(ky) is not harmonic: %s" % res_term)
    coeff_ok = []
    for i in (1, 3, 5):
        kk_i = i * sp.pi / (2 * As)
        # Fourier cosine coefficient of the parabola on [-A, A] against cos(k_i y), even extension
        c_fourier = sp.simplify(sp.integrate(para * sp.cos(kk_i * y), (y, -As, As)) / As)
        c_series = sp.simplify(16 * As ** 2 * Gs / (sp.pi ** 3 * nu) * (-1) ** ((i - 1) // 2) / sp.Integer(i) ** 3)
        coeff_ok.append(sp.simplify(c_fourier - c_series) == 0)
        if not coeff_ok[-1]:
            refuse("SYMBOLIC SUBSTITUTION FAILED: series coefficient i = %d (%s) is not the parabola's Fourier "
                   "coefficient (%s); u would not vanish on z = +/-A" % (i, c_series, c_fourier))
    if abs(float(Gs) - G) > 1e-15:
        refuse("G in this module (%.17g) disagrees with the symbolic G (%.17g)" % (G, float(Gs)))
    return dict(control="symbolic_substitution_into_duct_poisson_equation", parabola_residual=str(res_para),
                harmonic_term_residual=str(res_term), wall_fourier_coefficients_match=[1, 3, 5], passed=True)


def control_substitution_is_able_to_fail():
    """PLANTED CONTROL (rule 3): A scaled 1.1 inside the parabola must give a
    non-zero Poisson residual against the registered G."""
    import sympy as sp0
    sp, y, z, As, nu, Gs, para = _sym(A_factor=sp0.Rational(11, 10))
    # the parabola is invariant to A in its curvature; plant the CURVATURE instead: scale y^2 by 1.1
    para_pl = Gs / (2 * nu) * (As ** 2 - sp0.Rational(11, 10) * y ** 2)
    res = sp.simplify(nu * (sp.diff(para_pl, y, 2) + sp.diff(para_pl, z, 2)) + Gs)
    if res == 0:
        refuse("PLANTED CONTROL FAILED: a 1.1x curvature plant still gave a zero Poisson residual")
    return dict(control="PZ-F25-CURVATURE_planted_1.1x_must_be_nonzero", planted_factor=1.1, residual=str(res),
                passed=True)


def control_series_converged_and_symmetric():
    """The field series at EVERY fine-level cell centre: N_TERMS vs 2 N_TERMS
    below CONV_TOL; u(y, z) == u(z, y) below CONV_TOL; Ubar's tanh series
    (N vs 2N below 1e-15) agrees with a Gauss-Legendre quadrature of the field
    series to UBAR_QUAD_TOL; f.Re reproduces the literature 56.908 to 4
    decimals; every wall-adjacent centre lies strictly inside the duct."""
    g = cross_section_geometry(LEVELS[-1][1])
    u1 = u_exact(g["yc"], g["zc"], N_TERMS)
    u2 = u_exact(g["yc"], g["zc"], 2 * N_TERMS)
    d_terms = float(np.max(np.abs(u1 - u2)))
    if d_terms > CONV_TOL:
        refuse("SERIES NOT CONVERGED at the fine cell centres: N=%d vs 2N differ by %.3e > %.1e" % (N_TERMS, d_terms, CONV_TOL))
    d_sym = float(np.max(np.abs(u1 - u_exact(g["zc"], g["yc"], N_TERMS))))
    if d_sym > CONV_TOL:
        refuse("SERIES NOT SYMMETRIC in y <-> z: %.3e > %.1e" % (d_sym, CONV_TOL))
    if np.any(u1 <= 0.0):
        refuse("the exact profile is not positive at every cell centre")
    ub1, ub2 = ubar_exact(N_TERMS), ubar_exact(2 * N_TERMS)
    if abs(ub1 - ub2) > 1e-15:
        refuse("Ubar tanh series not converged: %.17g vs %.17g" % (ub1, ub2))
    # PLANTED CONTROL on the convergence detector: a series cut at 3 terms must be SEEN to differ
    d_short = float(np.max(np.abs(u_exact(g["yc"], g["zc"], 3) - u2)))
    if d_short <= CONV_TOL:
        refuse("PLANTED CONTROL FAILED: a 3-term series was not seen to differ from the converged one")
    xq, wq = np.polynomial.legendre.leggauss(160)
    yq = A + A * xq
    Yq, Zq = np.meshgrid(yq, yq, indexing="ij")
    Wq = np.outer(wq, wq) * A * A
    ub_quad = float(np.sum(Wq * u_exact(Yq.ravel(), Zq.ravel()).reshape(Yq.shape)) / SIDE ** 2)
    if abs(ub_quad - ub1) > UBAR_QUAD_TOL:
        refuse("Ubar from the tanh series (%.12g) and from quadrature of the field series (%.12g) disagree by "
               "%.3e > %.1e" % (ub1, ub_quad, abs(ub_quad - ub1), UBAR_QUAD_TOL))
    fre = f_re_exact()
    if abs(fre - F_RE_LITERATURE) > 5e-4:
        refuse("the series f.Re %.6f does not reproduce the literature square-duct value %.3f" % (fre, F_RE_LITERATURE))
    return dict(control="series_converged_symmetric_and_reproduces_fRe_56.908", n_terms=N_TERMS,
                max_diff_N_vs_2N=d_terms, max_asymmetry=d_sym, planted_3_term_diff=d_short,
                ubar_series=ub1, ubar_quadrature=ub_quad, ubar_quad_gap=abs(ub_quad - ub1),
                f_re_series=fre, f_re_literature=F_RE_LITERATURE, re_dh=re_dh(), u_max=u_max(), passed=True)


def control_ladder_is_geometrically_similar():
    for name, nr, nx in LEVELS:
        if abs(L / nx - SIDE / nr) > 1e-14:
            refuse("level %s has dx != h: %.17g vs %.17g" % (name, L / nx, SIDE / nr))
    rr = [LEVELS[i + 1][1] / LEVELS[i][1] for i in range(2)]
    rx = [LEVELS[i + 1][2] / LEVELS[i][2] for i in range(2)]
    rc = [(LEVELS[i + 1][1] ** 2 * LEVELS[i + 1][2]) / (LEVELS[i][1] ** 2 * LEVELS[i][2]) for i in range(2)]
    if max(abs(v - 2.0) for v in rr + rx) > 1e-12 or max(abs(v - 8.0) for v in rc) > 1e-12:
        refuse("the ladder is not a factor-2 refinement in all three directions: side %s, x %s, cells %s" % (rr, rx, rc))
    return dict(control="constant_ratio_refinement_all_three_directions_cubic_cells", side_ratios=rr, x_ratios=rx,
                cell_ratios=rc, passed=True)


def control_model_is_solved_and_second_order():
    tab = predictions()
    for row in tab:
        if row["solve_residual_max"] > 1e-10:
            refuse("model at level %s not solved: max residual %.3e" % (row["name"], row["solve_residual_max"]))
        if row["truncation_residual_max"] <= 0.0:
            refuse("PLANTED CONTROL FAILED: the stencil evaluator returned a zero truncation residual on the "
                   "exact profile at level %s; an evaluator that sees nothing is not evidence" % row["name"])
    p_e2, p_fr = model_orders()
    if not all(1.7 <= p <= 2.3 for p in p_e2 + p_fr):
        refuse("the model is not second order across the ladder: E2n orders %s, fRe orders %s" % (p_e2, p_fr))
    signs = [np.sign(row["fRe_err_pred"]) for row in tab]
    if not (signs[0] == signs[1] == signs[2]):
        refuse("the model's predicted f.Re error changes sign across the ladder %s: the triple would be "
               "OSCILLATORY by prediction and the gate must not be registered on it" % [row["fRe_err_pred"] for row in tab])
    return dict(control="model_solved_and_second_order", orders_E2n=p_e2, orders_fRe=p_fr, passed=True)


def control_model_triples_classify_converging():
    """L-345: the registered model's OWN triples through THE grader's
    classifier (roache_triple.triple_from_cells, dim = 3).  A DEGENERATE /
    STAGNANT / OSCILLATORY / EXACT prediction is a REGISTRATION DEFECT and is
    refused here, before any compute.  The classifier is shown able to say
    DEGENERATE on a planted equal-increment triple (rule 3)."""
    tab = predictions()
    cells = [row["cells"] for row in tab]
    out = {}
    for key, vals in (("E2n", [row["E2n_pred"] for row in tab]), ("fRe", [row["fRe_pred"] for row in tab])):
        t = RT.triple_from_cells(vals[0], vals[1], vals[2], cells[0], cells[1], cells[2], DIM)
        out[key] = dict(state=t["state"], order=t.get("order"), values=vals)
        if t["state"] != "CONVERGING":
            refuse("L-345 REGISTRATION DEFECT: the model's own %s triple %s classifies %s (order %s) through "
                   "roache_triple; a gate cannot be registered on a quantity whose prediction the instrument "
                   "cannot read" % (key, vals, t["state"], t.get("order")))
        if abs(t["r21"] - 2.0) > 1e-12 or abs(t["r32"] - 2.0) > 1e-12:
            refuse("the model triple's refinement ratios are not exactly 2 at dim = 3: %s / %s" % (t["r21"], t["r32"]))
    planted = RT.triple_from_cells(0.850756, 0.850649, 0.850540, cells[0], cells[1], cells[2], DIM)   # F19's x_s: equal increments
    if planted["state"] != "DEGENERATE":
        refuse("PLANTED CONTROL FAILED: the classifier did not read F19's equal-increment x_s triple as DEGENERATE (%s)"
               % planted["state"])
    return dict(control="PZ-F25-L345_model_triples_CONVERGING_through_roache_triple_and_planted_DEGENERATE_seen",
                model_triples=out, planted_degenerate_state=planted["state"], planted_degenerate_order=planted["order"],
                dim=DIM, passed=True)


def selftest_predicate(controls):
    if len(controls) != 6:
        return False, "expected 6 controls, ran %d" % len(controls)
    for c in controls:
        if not c.get("passed"):
            return False, "control %s did not pass" % c.get("control")
    if not __debug__:
        return False, "running under -O"
    return True, ("6 controls green: the series satisfies the duct Poisson equation identically (parabola residual 0, "
                  "every term harmonic, wall Fourier coefficients match for i = 1, 3, 5); a 1.1x curvature plant makes "
                  "the residual non-zero; the series is converged (N vs 2N) and y<->z symmetric at every fine cell "
                  "centre and reproduces f.Re = 56.908; the ladder refines by exactly 2 in all three directions with "
                  "cubic cells; the discretisation model is solved to round-off, sees a non-zero truncation residual "
                  "on the exact profile and is second order; the model's own triples classify CONVERGING through "
                  "roache_triple at dim = 3 and a planted equal-increment triple is read DEGENERATE (L-345)")


def all_controls():
    return [control_symbolic_substitution(), control_substitution_is_able_to_fail(),
            control_series_converged_and_symmetric(), control_ladder_is_geometrically_similar(),
            control_model_is_solved_and_second_order(), control_model_triples_classify_converging()]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    controls = all_controls()
    tab = predictions()
    if a.json:
        print(json.dumps(dict(constants=dict(A=A, side=SIDE, D_h=D_H, nu=NU, G=G, L=L, Re_Dh=re_dh(), Ubar=ubar_exact(),
                                             u_max=u_max(), f_re_exact=f_re_exact(), n_iter=N_ITER,
                                             write_every=WRITE_EVERY, ranks=RANKS, dim=DIM),
                              levels=[dict((k, v) for k, v in r.items()) for r in tab],
                              orders=dict(E2n=model_orders()[0], fRe=model_orders()[1]),
                              controls=controls), indent=2, default=str))
        return 0
    ok, why = selftest_predicate(controls)
    if a.selftest:
        print(json.dumps(dict(controls=controls, levels=tab, orders=dict(E2n=model_orders()[0], fRe=model_orders()[1]),
                              predicate=dict(ok=ok, why=why)), indent=2, default=str))
        if not ok:
            refuse("SELFTEST DID NOT ESTABLISH ITS CLAIM: %s" % why)
        print("\nSELFTEST GREEN -- %s" % why)
        return 0
    print("A=%g side=%g D_h=%g nu=%g G=%g L=%g  Ubar=%.15g Re_Dh=%.6f u_max=%.15g f.Re=%.12f (literature %.3f)"
          % (A, SIDE, D_H, NU, G, L, ubar_exact(), re_dh(), u_max(), f_re_exact(), F_RE_LITERATURE))
    for r in tab:
        print("%-7s nr=%d nx=%d cells=%d h=%.6g  E2n_pred=%.6e  fRe_pred=%.9f (err %+.3e)  ubar_h=%.12f"
              % (r["name"], r["nr"], r["nx"], r["cells"], r["h"], r["E2n_pred"], r["fRe_pred"], r["fRe_err_pred"], r["ubar_h_pred"]))
    print("model orders: E2n %s  fRe %s" % model_orders())
    return 0


if __name__ == "__main__":
    sys.exit(main())
