#!/usr/bin/env python3
"""
F17 -- THE EXACT SOLUTION of Kovasznay flow, and the DISCRETISATION-DERIVED
error prediction every F17 band is built from.

    u = 1 - exp(lam x) cos(2 pi y)
    v = (lam / 2 pi) exp(lam x) sin(2 pi y)
    p = (1 - exp(2 lam x)) / 2
    lam = Re/2 - sqrt(Re^2/4 + 4 pi^2),   nu = 1/Re,   Re = 40

THE REFERENCE IS NOT A PAPER ON THIS BOX.  IT IS A SUBSTITUTION.
-----------------------------------------------------------------
Standing rule 15 requires title-page verification of every retrieved paper.
This case retrieves none.  The closed form is verified here by SYMBOLIC
SUBSTITUTION INTO THE STEADY INCOMPRESSIBLE NAVIER-STOKES EQUATIONS, on this
box, at selftest time.  Three residuals must be identically zero (continuity,
x-momentum, y-momentum) and a planted control (lam scaled by 1.1) must make
the momentum residuals NON-zero.

THE BAND PRINCIPLE -- derived from the discretisation, not measured
-------------------------------------------------------------------
The solver's steady discrete solution U_h satisfies the discrete equations
exactly; the exact solution does not.  Evaluating the solver's OWN stencils on
the exact field gives the truncation residual r_h (momentum) and d_h
(continuity), both O(h^2).  The leading-order discrete error e_h then solves
the LINEARISED discrete equations forced by those residuals:

    J_h e_h = -(r_h, d_h)

That linear system is assembled and solved here with scipy.sparse, on the
SAME uniform grids the ladder runs, with the same collocated central stencils
simpleFoam uses on a uniform Cartesian mesh (Gauss linear convection, Gauss
linear orthogonal Laplacian, Gauss linear pressure gradient, Rhie-Chow
interpolated flux with a compact pressure Laplacian).  The prediction is
therefore a function of the SCHEME and the GRID and nothing else.

WHAT THE MODEL OMITS, stated rather than glossed:
  * it is a linearisation; the true error also feeds back through the
    nonlinear terms (second order in the error, negligible at these sizes);
  * rAU in the Rhie-Chow term is taken as 1/a_P of the UNRELAXED central
    operator, not the relaxed one the solver uses; the term is O(h^3) on a
    smooth pressure, so this changes the stabilisation, not the O(h^2) error;
  * the inlet/outlet boundary datum is the FACE-AVERAGED exact velocity (so the
    boundary fluxes balance exactly and adjustPhi has nothing to remove), and
    the model imposes exactly that datum.

Because of those omissions the registered band is a FACTOR-3 window around the
prediction, declared before compute, not an equality.

Refusals are `raise` and `sys.exit(2)`.  Zero `assert` statements (L-332).
"""
import sys

if not __debug__:
    sys.stderr.write(
        "REFUSED: exact_f17.py must not run under `python3 -O`.\n"
        "  -O deletes every `assert`, including the ones in the shared\n"
        "  roache_triple.py that carry rule 1's vocabulary and rule 5's one-way gate.\n")
    sys.exit(2)

import json
import math
import argparse

import numpy as np

# ---------------------------------------------------------------------------
# THE CASE, FROZEN.
# ---------------------------------------------------------------------------
RE = 40.0
NU = 1.0 / RE                                   # 0.025
LAM = RE / 2.0 - math.sqrt(RE ** 2 / 4.0 + 4.0 * math.pi ** 2)   # -0.963740...
U0 = 1.0                                        # free-stream, the normaliser
X0, X1 = -0.5, 1.0                              # streamwise extent, 1.5
Y0, Y1 = -0.5, 0.5                              # ONE period of cos(2 pi y): cyclic
LX, LY = X1 - X0, Y1 - Y0
PROBE = (0.5, 0.0)                              # G-F17-2 probe point (x, y)
ALPHA_U = 0.7                                   # solver relaxation, recorded

# The three mesh levels: (name, Nx, Ny).  UNIFORM SQUARE cells at every level,
# h = LX/Nx = LY/Ny, so the meshes are geometrically similar and both
# directions refine by exactly 2 (dim = 2 in roache_triple).
LEVELS = (("coarse", 192, 128), ("medium", 384, 256), ("fine", 768, 512))   # F17b: F17's fine is this coarse
# F17b EXTENSION: the linear model is SOLVED on these grids (F17's own medium and
# fine; 192x128 = 29.5 s, 2.85 GB RSS measured) and EXTRAPOLATED to the two finer
# F17b levels with the model's own observed order between them.  384x256 measured
# 255 s / 14.9 GB RSS and 768x512 would exceed this 30 GB box, so it is not solved.
MODEL_GRIDS = ((96, 64), (192, 128))
N_ITER = 4000                                   # simpleFoam iterations, fixed
WRITE_EVERY = 100                               # checkpoints for the Class C series


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def h_of(nx):
    return LX / float(nx)


def u_exact(x, y):
    return 1.0 - np.exp(LAM * x) * np.cos(2.0 * math.pi * y)


def v_exact(x, y):
    return LAM / (2.0 * math.pi) * np.exp(LAM * x) * np.sin(2.0 * math.pi * y)


def p_exact(x, y):
    return 0.5 * (1.0 - np.exp(2.0 * LAM * x))


def u_face_avg_x(x, ya, yb):
    """Average of u over the y-segment [ya, yb] at fixed x (an x-normal face)."""
    return 1.0 - np.exp(LAM * x) * (np.sin(2 * math.pi * yb) - np.sin(2 * math.pi * ya)) / (2 * math.pi * (yb - ya))


def v_face_avg_x(x, ya, yb):
    return LAM / (2 * math.pi) * np.exp(LAM * x) * (-(np.cos(2 * math.pi * yb) - np.cos(2 * math.pi * ya))) / (2 * math.pi * (yb - ya))


# ---------------------------------------------------------------------------
# THE DISCRETE MODEL
# ---------------------------------------------------------------------------
def grid(nx, ny):
    h = h_of(nx)
    if abs(LY / ny - h) > 1e-14:
        refuse("level %dx%d is not square-celled: LX/Nx = %.17g, LY/Ny = %.17g"
               % (nx, ny, h, LY / ny))
    xc = X0 + (np.arange(nx) + 0.5) * h
    yc = Y0 + (np.arange(ny) + 0.5) * h
    return h, xc, yc


def discrete_error(nx, ny):
    """Assemble and solve  J_h e = -(r_h, d_h)  on the nx x ny grid.

    Returns dict with the cell-centred predicted error fields eu, ev (Ny, Nx),
    the residual norms, and the derived scalar predictions.
    """
    import scipy.sparse as sp
    import scipy.sparse.linalg as spl

    h, xc, yc = grid(nx, ny)
    X, Y = np.meshgrid(xc, yc)                  # shape (ny, nx), [j, i]
    U = u_exact(X, Y)
    V = v_exact(X, Y)
    PP = p_exact(X, Y)
    N = nx * ny
    vol = h * h

    def cid(i, j):
        return (j % ny) * nx + i                 # y is periodic

    # boundary face data (x = X0 inlet, x = X1 outlet): FACE-AVERAGED exact
    ya = yc - 0.5 * h
    yb = yc + 0.5 * h
    Ub_in = u_face_avg_x(X0, ya, yb); Vb_in = v_face_avg_x(X0, ya, yb)
    Ub_out = u_face_avg_x(X1, ya, yb); Vb_out = v_face_avg_x(X1, ya, yb)
    Pb_in = np.full(ny, float(p_exact(X0, 0.0))); Pb_out = np.full(ny, float(p_exact(X1, 0.0)))

    # ---- residuals of the exact field under the solver's stencils ---------
    ru = np.zeros((ny, nx)); rv = np.zeros((ny, nx)); d = np.zeros((ny, nx))
    # a_P diagonal of the central operator, for rAU
    aP = np.full((ny, nx), 4.0 * NU / h)          # diffusion part, per unit volume

    rows, cols, vals = [], [], []
    rhs = np.zeros(3 * N + 1)

    def add(r, c, v):
        rows.append(r); cols.append(c); vals.append(v)

    IU, IV, IQ = 0, N, 2 * N

    def face(P, Nb, dirx, diry, Uf, Vf, phi):
        """Interior face between cells P and Nb, outward normal of P = (dirx, diry).
        Uf, Vf: exact face velocity; phi: exact face flux (P outward)."""
        for (row, sgn, other) in ((P, +1.0, Nb), (Nb, -1.0, P)):
            ph = sgn * phi
            nx_, ny_ = sgn * dirx, sgn * diry
            # convection linearised: (1/V)[ phi*(e_P+e_N)/2 + ((e_P+e_N)/2 . n) h U_f ]
            for comp, base, Ufk in ((0, IU, Uf), (1, IV, Vf)):
                add(base + row, base + row, ph / (2 * vol))
                add(base + row, base + other, ph / (2 * vol))
                # (e . n) h U_f,k : n has one nonzero component
                if nx_ != 0.0:
                    add(base + row, IU + row, nx_ * h * Ufk / (2 * vol))
                    add(base + row, IU + other, nx_ * h * Ufk / (2 * vol))
                else:
                    add(base + row, IV + row, ny_ * h * Ufk / (2 * vol))
                    add(base + row, IV + other, ny_ * h * Ufk / (2 * vol))
                # diffusion: -nu (e_N - e_P)/V
                add(base + row, base + row, NU / vol)
                add(base + row, base + other, -NU / vol)
            # pressure gradient (Gauss linear): (1/V) (q_P+q_N)/2 n h
            if nx_ != 0.0:
                add(IU + row, IQ + row, nx_ / (2 * h)); add(IU + row, IQ + other, nx_ / (2 * h))
            else:
                add(IV + row, IQ + row, ny_ / (2 * h)); add(IV + row, IQ + other, ny_ / (2 * h))

    # loop cells, build residuals and interior-face coefficients once per face
    for j in range(ny):
        for i in range(nx):
            P = cid(i, j)
            up, vp, pp = U[j, i], V[j, i], PP[j, i]
            cu = cv = 0.0; lu = lv = 0.0; gpx = gpy = 0.0; div = 0.0
            # ---- east face
            if i < nx - 1:
                Nb = cid(i + 1, j)
                Uf, Vf, Pf = 0.5 * (up + U[j, i + 1]), 0.5 * (vp + V[j, i + 1]), 0.5 * (pp + PP[j, i + 1])
                phi = Uf * h
                cu += phi * Uf; cv += phi * Vf
                lu += (U[j, i + 1] - up); lv += (V[j, i + 1] - vp)
                gpx += Pf * h; div += phi
                aP[j, i] += abs(phi) / (2 * vol)
                face(P, Nb, 1.0, 0.0, Uf, Vf, phi)
            else:
                Uf, Vf, Pf = Ub_out[j], Vb_out[j], Pb_out[j]
                phi = Uf * h
                cu += phi * Uf; cv += phi * Vf
                lu += 2.0 * (Uf - up); lv += 2.0 * (Vf - vp)
                gpx += Pf * h; div += phi
                aP[j, i] += abs(phi) / (2 * vol)
                add(IU + P, IU + P, 2 * NU / vol); add(IV + P, IV + P, 2 * NU / vol)
                add(IU + P, IQ + P, 1.0 / h)      # q_b = q_P (Neumann correction)
            # ---- west face
            if i > 0:
                Uf, Vf, Pf = 0.5 * (up + U[j, i - 1]), 0.5 * (vp + V[j, i - 1]), 0.5 * (pp + PP[j, i - 1])
                phi = -Uf * h
                cu += phi * Uf; cv += phi * Vf
                lu += (U[j, i - 1] - up); lv += (V[j, i - 1] - vp)
                gpx -= Pf * h; div += phi
                aP[j, i] += abs(phi) / (2 * vol)
            else:
                Uf, Vf, Pf = Ub_in[j], Vb_in[j], Pb_in[j]
                phi = -Uf * h
                cu += phi * Uf; cv += phi * Vf
                lu += 2.0 * (Uf - up); lv += 2.0 * (Vf - vp)
                gpx -= Pf * h; div += phi
                aP[j, i] += abs(phi) / (2 * vol)
                add(IU + P, IU + P, 2 * NU / vol); add(IV + P, IV + P, 2 * NU / vol)
                add(IU + P, IQ + P, -1.0 / h)
            # ---- north face (periodic)
            jn = (j + 1) % ny
            Uf, Vf, Pf = 0.5 * (up + U[jn, i]), 0.5 * (vp + V[jn, i]), 0.5 * (pp + PP[jn, i])
            phi = Vf * h
            cu += phi * Uf; cv += phi * Vf
            lu += (U[jn, i] - up); lv += (V[jn, i] - vp)
            gpy += Pf * h; div += phi
            aP[j, i] += abs(phi) / (2 * vol)
            face(P, cid(i, jn), 0.0, 1.0, Uf, Vf, phi)
            # ---- south face (periodic)
            js = (j - 1) % ny
            Uf, Vf, Pf = 0.5 * (up + U[js, i]), 0.5 * (vp + V[js, i]), 0.5 * (pp + PP[js, i])
            phi = -Vf * h
            cu += phi * Uf; cv += phi * Vf
            lu += (U[js, i] - up); lv += (V[js, i] - vp)
            gpy -= Pf * h; div += phi
            aP[j, i] += abs(phi) / (2 * vol)

            ru[j, i] = cu / vol - NU * lu / vol + gpx / vol
            rv[j, i] = cv / vol - NU * lv / vol + gpy / vol
            d[j, i] = div

    # ---- continuity rows with Rhie-Chow corrected interior fluxes ----------
    rA = ALPHA_U / aP                              # solver-shaped rAU (relaxed)

    def gq_coeffs(i, j, comp):
        """Coefficients of the wide (Gauss linear) gradient of q at cell (i,j),
        component comp (0=x, 1=y), with q_b = q_P at x-boundaries."""
        out = {}
        if comp == 0:
            if i < nx - 1:
                out[cid(i + 1, j)] = out.get(cid(i + 1, j), 0.0) + 0.5 / h
                out[cid(i, j)] = out.get(cid(i, j), 0.0) + 0.5 / h
            else:
                out[cid(i, j)] = out.get(cid(i, j), 0.0) + 1.0 / h
            if i > 0:
                out[cid(i - 1, j)] = out.get(cid(i - 1, j), 0.0) - 0.5 / h
                out[cid(i, j)] = out.get(cid(i, j), 0.0) - 0.5 / h
            else:
                out[cid(i, j)] = out.get(cid(i, j), 0.0) - 1.0 / h
        else:
            out[cid(i, (j + 1) % ny)] = out.get(cid(i, (j + 1) % ny), 0.0) + 0.5 / h
            out[cid(i, (j - 1) % ny)] = out.get(cid(i, (j - 1) % ny), 0.0) - 0.5 / h
        return out

    def cont_face(P, Nb, i, j, i2, j2, comp):
        rAf = 0.5 * (rA[j, i] + rA[j2, i2])
        base = IU if comp == 0 else IV
        # interpolated error flux (e_P + e_N)/2 * h, outward from P
        for (row, sgn) in ((P, +1.0), (Nb, -1.0)):
            add(IQ + row, base + P, sgn * 0.5 * h)
            add(IQ + row, base + Nb, sgn * 0.5 * h)
            # - rAf h [ (q_N - q_P)/h - 0.5 ((Gq)_P + (Gq)_N) . n ]
            add(IQ + row, IQ + Nb, -sgn * rAf)
            add(IQ + row, IQ + P, +sgn * rAf)
            for cell, coef in gq_coeffs(i, j, comp).items():
                add(IQ + row, IQ + cell, sgn * rAf * h * 0.5 * coef)
            for cell, coef in gq_coeffs(i2, j2, comp).items():
                add(IQ + row, IQ + cell, sgn * rAf * h * 0.5 * coef)

    for j in range(ny):
        for i in range(nx):
            P = cid(i, j)
            if i < nx - 1:
                cont_face(P, cid(i + 1, j), i, j, i + 1, j, 0)
            jn = (j + 1) % ny
            cont_face(P, cid(i, jn), i, j, i, jn, 1)

    # pressure level: Lagrange multiplier  sum q = 0
    for c in range(N):
        add(IQ + c, 3 * N, 1.0)
        add(3 * N, IQ + c, 1.0)

    rhs[IU:IU + N] = -ru.ravel()
    rhs[IV:IV + N] = -rv.ravel()
    rhs[IQ:IQ + N] = -d.ravel()
    M = sp.csc_matrix((vals, (rows, cols)), shape=(3 * N + 1, 3 * N + 1))
    sol = spl.spsolve(M, rhs)
    eu = sol[IU:IU + N].reshape(ny, nx)
    ev = sol[IV:IV + N].reshape(ny, nx)
    q = sol[IQ:IQ + N].reshape(ny, nx)
    resid = float(np.max(np.abs(M @ sol - rhs)))
    e2 = float(math.sqrt(np.mean(eu ** 2 + ev ** 2)) / U0)
    return dict(nx=nx, ny=ny, h=h, eu=eu, ev=ev, q=q, xc=xc, yc=yc,
                E2_pred=e2,
                probe_err_pred=float(bilinear(xc, yc, eu, PROBE[0], PROBE[1])),
                sum_boundary_flux=float(np.sum(Ub_out) * h - np.sum(Ub_in) * h),
                r_momentum_L2=float(math.sqrt(np.mean(ru ** 2 + rv ** 2))),
                d_continuity_max=float(np.max(np.abs(d))),
                solve_residual_max=resid)


def bilinear(xc, yc, F, x, y):
    """Bilinear interpolation of a cell-centred field (ny, nx) at (x, y).
    Refuses outside the cell-centre hull."""
    if not (xc[0] <= x <= xc[-1] and yc[0] <= y <= yc[-1]):
        refuse("probe (%g, %g) is outside the cell-centre hull" % (x, y))
    i = int(np.searchsorted(xc, x) - 1); i = min(max(i, 0), len(xc) - 2)
    j = int(np.searchsorted(yc, y) - 1); j = min(max(j, 0), len(yc) - 2)
    tx = (x - xc[i]) / (xc[i + 1] - xc[i]); ty = (y - yc[j]) / (yc[j + 1] - yc[j])
    return ((1 - tx) * (1 - ty) * F[j, i] + tx * (1 - ty) * F[j, i + 1]
            + (1 - tx) * ty * F[j + 1, i] + tx * ty * F[j + 1, i + 1])


def u_probe_exact():
    return float(u_exact(PROBE[0], PROBE[1]) / U0)


_CACHE = {}


def solved(nx, ny):
    """The full model (error fields included) SOLVED on one grid, cached per process."""
    if (nx, ny) not in MODEL_GRIDS:
        refuse("grid %dx%d is not solved by the model; it is extrapolated" % (nx, ny))
    if (nx, ny) not in _CACHE:
        _CACHE[(nx, ny)] = discrete_error(nx, ny)
    return _CACHE[(nx, ny)]


def model(name):
    """The full model at one LADDER level -- only where that level's grid is solved."""
    lv = dict((n, (nx, ny)) for n, nx, ny in LEVELS)
    if name not in lv:
        refuse("unknown level %r" % name)
    return solved(*lv[name])


def model_orders():
    a, b = solved(*MODEL_GRIDS[0]), solved(*MODEL_GRIDS[1])
    r = math.log(a["h"] / b["h"])
    return (math.log(a["E2_pred"] / b["E2_pred"]) / r,
            math.log(abs(a["probe_err_pred"]) / abs(b["probe_err_pred"])) / r)


def predictions():
    """Solved where the ladder grid is a MODEL_GRID; otherwise extrapolated from
    the finest solved grid with the model's own orders (E2 and probe separately)."""
    if "table" not in _CACHE:
        ref = solved(*MODEL_GRIDS[-1])
        p_e2, p_pr = model_orders()
        tab = []
        for name, nx, ny in LEVELS:
            if (nx, ny) in MODEL_GRIDS:
                m, src = solved(nx, ny), "solved"
                e2, pe = m["E2_pred"], m["probe_err_pred"]
            else:
                m, src = ref, ("extrapolated from %dx%d with model orders %.4f (E2), %.4f (probe)"
                               % (ref["nx"], ref["ny"], p_e2, p_pr))
                e2 = ref["E2_pred"] * (h_of(nx) / ref["h"]) ** p_e2
                pe = ref["probe_err_pred"] * (h_of(nx) / ref["h"]) ** p_pr
            tab.append(dict(name=name, nx=nx, ny=ny, cells=nx * ny, h=h_of(nx),
                            E2_pred=e2, probe_err_pred=pe,
                            r_momentum_L2=m["r_momentum_L2"],
                            d_continuity_max=m["d_continuity_max"],
                            sum_boundary_flux=m["sum_boundary_flux"],
                            solve_residual_max=m["solve_residual_max"], source=src))
        _CACHE["table"] = tab
    return _CACHE["table"]


# ---------------------------------------------------------------------------
# CONTROLS
# ---------------------------------------------------------------------------
def control_symbolic_substitution():
    try:
        import sympy as sp
    except ImportError:
        refuse("sympy is not importable; the exact solution cannot be verified "
               "by substitution and NOTHING may be registered on it")
    x, y = sp.symbols("x y", real=True)
    Re = sp.Rational(40)
    nu = 1 / Re
    lam = Re / 2 - sp.sqrt(Re ** 2 / 4 + 4 * sp.pi ** 2)
    u = 1 - sp.exp(lam * x) * sp.cos(2 * sp.pi * y)
    v = lam / (2 * sp.pi) * sp.exp(lam * x) * sp.sin(2 * sp.pi * y)
    p = (1 - sp.exp(2 * lam * x)) / 2
    res = {
        "continuity": sp.simplify(sp.diff(u, x) + sp.diff(v, y)),
        "x_momentum": sp.simplify(u * sp.diff(u, x) + v * sp.diff(u, y) + sp.diff(p, x)
                                  - nu * (sp.diff(u, x, 2) + sp.diff(u, y, 2))),
        "y_momentum": sp.simplify(u * sp.diff(v, x) + v * sp.diff(v, y) + sp.diff(p, y)
                                  - nu * (sp.diff(v, x, 2) + sp.diff(v, y, 2))),
    }
    bad = [n for n, r in res.items() if r != 0]
    if bad:
        refuse("SYMBOLIC SUBSTITUTION FAILED: residuals %s are not identically "
               "zero; the registered closed form is NOT an exact solution" % bad)
    if abs(float(lam) - LAM) > 1e-12:
        refuse("LAM in this module (%.15g) disagrees with the symbolic lam (%.15g)"
               % (LAM, float(lam)))
    return dict(control="symbolic_substitution_into_steady_NS",
                residuals=dict((n, str(r)) for n, r in res.items()), passed=True)


def control_substitution_is_able_to_fail():
    """PLANTED CONTROL (rule 3): lam scaled by 1.1 must give non-zero momentum
    residuals, or the substitution checker cannot see a wrong solution."""
    import sympy as sp
    x, y = sp.symbols("x y", real=True)
    Re = sp.Rational(40)
    nu = 1 / Re
    lam = sp.Rational(11, 10) * (Re / 2 - sp.sqrt(Re ** 2 / 4 + 4 * sp.pi ** 2))   # PLANT
    u = 1 - sp.exp(lam * x) * sp.cos(2 * sp.pi * y)
    v = lam / (2 * sp.pi) * sp.exp(lam * x) * sp.sin(2 * sp.pi * y)
    p = (1 - sp.exp(2 * lam * x)) / 2
    r = sp.simplify(u * sp.diff(u, x) + v * sp.diff(u, y) + sp.diff(p, x)
                    - nu * (sp.diff(u, x, 2) + sp.diff(u, y, 2)))
    if r == 0:
        refuse("PLANTED CONTROL FAILED: lam planted at 1.1x still gave a zero "
               "x-momentum residual; the checker cannot see a wrong solution")
    return dict(control="PZ-F17-LAMBDA_planted_1.1x_must_be_nonzero",
                planted_factor=1.1, residual_is_zero=False, passed=True)


def control_ladder_is_geometrically_similar():
    for name, nx, ny in LEVELS:
        if abs(LX / nx - LY / ny) > 1e-14:
            refuse("level %s has non-square cells" % name)
    r = [h_of(LEVELS[i][1]) / h_of(LEVELS[i + 1][1]) for i in range(2)]
    ry = [(LY / LEVELS[i][2]) / (LY / LEVELS[i + 1][2]) for i in range(2)]
    if max(abs(v - 2.0) for v in r + ry) > 1e-12:
        refuse("the ladder is not a factor-2 refinement in both directions: %s %s"
               % (r, ry))
    return dict(control="constant_ratio_refinement_both_directions",
                h_ratios_x=r, h_ratios_y=ry, passed=True)


def control_boundary_fluxes_balance():
    """The imposed face-averaged inlet/outlet data must carry ZERO net flux to
    round-off, or simpleFoam's adjustPhi refuses the case (fatal) at the first
    iteration.  Checked on every level."""
    out = []
    for name, nx, ny in LEVELS:
        h, xc, yc = grid(nx, ny)
        ya, yb = yc - 0.5 * h, yc + 0.5 * h
        net = float(np.sum(u_face_avg_x(X1, ya, yb)) * h - np.sum(u_face_avg_x(X0, ya, yb)) * h)
        if abs(net) > 1e-12:
            refuse("net boundary flux at level %s is %.3e, not zero: adjustPhi "
                   "would refuse this case" % (name, net))
        out.append(dict(level=name, net_flux=net))
    return dict(control="face_averaged_boundary_data_balances_to_roundoff",
                levels=out, passed=True)


def control_model_is_second_order_and_solved():
    """The model's own predictions must (a) come from a solved linear system
    (residual at round-off) and (b) scale as h^2 across the ladder, or it is
    not a discretisation-derived prediction of anything.  Also a PLANTED
    control on the residual evaluator: the model applied to the exact field
    must see a NON-zero truncation residual (a stencil evaluator returning
    zero on the exact field would be an evaluator that sees nothing)."""
    tab = predictions()
    for nx, ny in MODEL_GRIDS:
        row = solved(nx, ny)
        if row["solve_residual_max"] > 1e-8:
            refuse("linear model on grid %dx%d not solved: max residual %.3e"
                   % (nx, ny, row["solve_residual_max"]))
        if row["r_momentum_L2"] <= 0.0:
            refuse("PLANTED CONTROL FAILED: the stencil evaluator returned a zero "
                   "truncation residual on the exact field on grid %dx%d" % (nx, ny))
    p12, p23 = model_orders()          # E2 order and probe order between the SOLVED grids
    if not (1.7 <= p12 <= 2.3 and 1.7 <= p23 <= 2.3):
        refuse("the model's predicted errors do not scale as h^2 between the solved grids: "
               "model orders %.3f (E2), %.3f (probe)" % (p12, p23))
    pe = [row["probe_err_pred"] for row in tab]
    if not (np.sign(pe[0]) == np.sign(pe[1]) == np.sign(pe[2])):
        refuse("the model's predicted probe error changes sign across the ladder "
               "%s; the probe triple would be OSCILLATORY by prediction and the "
               "gate must not be registered on it" % pe)
    return dict(control="model_solved_and_second_order",
                model_orders=[p12, p23], probe_err_pred=pe, passed=True)


def selftest_predicate(controls):
    if len(controls) != 5:
        return False, "expected 5 controls, ran %d" % len(controls)
    for c in controls:
        if not c.get("passed"):
            return False, "control %s did not pass" % c.get("control")
    if not __debug__:
        return False, "running under -O"
    return True, ("5 controls green: the closed form satisfies continuity and both "
                  "momentum equations identically under symbolic substitution; a "
                  "lam planted at 1.1x makes the momentum residual non-zero; the "
                  "ladder refines by exactly 2 in both directions with square "
                  "cells; the face-averaged boundary data carries zero net flux; "
                  "and the discretisation model is solved to round-off and "
                  "scales as h^2 with a sign-stable probe error")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    controls = [control_symbolic_substitution(),
                control_substitution_is_able_to_fail(),
                control_ladder_is_geometrically_similar(),
                control_boundary_fluxes_balance(),
                control_model_is_second_order_and_solved()]
    tab = predictions()
    if a.json:
        print(json.dumps(dict(constants=dict(Re=RE, nu=NU, lam=LAM, U0=U0,
                                             x=[X0, X1], y=[Y0, Y1], probe=PROBE,
                                             n_iter=N_ITER, write_every=WRITE_EVERY),
                              levels=tab, u_probe_exact=u_probe_exact(),
                              controls=controls), indent=2))
        return 0
    ok, why = selftest_predicate(controls)
    if a.selftest:
        print(json.dumps(dict(controls=controls, levels=tab,
                              u_probe_exact=u_probe_exact(),
                              predicate=dict(ok=ok, why=why)), indent=2))
        if not ok:
            refuse("SELFTEST DID NOT ESTABLISH ITS CLAIM: %s" % why)
        print("\nSELFTEST GREEN -- %s" % why)
        return 0
    print("Re=%g nu=%g lam=%.15g  domain x[%g,%g] y[%g,%g] cyclic-y  probe=%s"
          % (RE, NU, LAM, X0, X1, Y0, Y1, PROBE))
    print("u(probe)/U0 exact = %.15f" % u_probe_exact())
    for r in tab:
        print("%-7s %dx%d h=%.6g  E2_pred=%.6e  probe_err_pred=%.6e  |r|=%.3e  solve_res=%.1e  [%s]"
              % (r["name"], r["nx"], r["ny"], r["h"], r["E2_pred"], r["probe_err_pred"],
                 r["r_momentum_L2"], r["solve_residual_max"], r["source"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
