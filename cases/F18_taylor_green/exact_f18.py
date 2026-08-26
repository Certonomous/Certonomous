#!/usr/bin/env python3
"""
F18 -- THE EXACT SOLUTION of the 2-D decaying Taylor-Green vortex, and the
DISCRETISATION-DERIVED error prediction every F18 band is built from.

    u =  sin x cos y e^{-2 nu t},  v = -cos x sin y e^{-2 nu t},
    p = +(cos 2x + cos 2y)/4 e^{-4 nu t},   on [0, 2 pi]^2 periodic

THE REFERENCE IS NOT A PAPER ON THIS BOX.  IT IS A SUBSTITUTION.  The closed
form is verified by symbolic substitution into the UNSTEADY incompressible
Navier-Stokes equations at selftest (continuity, x- and y-momentum identically
zero); a planted control (decay rate 2 nu -> 2.3 nu) must make the momentum
residuals non-zero.

THE BAND PRINCIPLE -- derived from the discretisation, not measured.  The
solver's own uniform-Cartesian stencils (Gauss linear convection, Gauss linear
orthogonal Laplacian, Gauss linear pressure gradient, Rhie-Chow interpolated
flux with a compact pressure Laplacian, BDF2 `backward` time derivative) are
evaluated on the exact field, giving the momentum residual r(t), the continuity
residual d(t) and the BDF2 time-derivative residual.  The leading-order error e
then obeys the LINEARISED discrete equations forced by those residuals,

    d e/dt + C_h'(U(t)) e - nu L_h e + G_h q = -r(t),   D_h e + RC(q) = -d(t),

which are integrated here with the same BDF2 step the solver uses (diffusion and
projection implicit with one sparse LU, the linearised convection explicit
second-order Adams-Bashforth), on the SAME grids and time steps the ladder runs
at coarse and medium; the fine level is extrapolated with the model's own
observed order (a control requires it to lie in [1.7, 2.3]).

Omissions, stated: the nonlinear feedback of the error on itself (second order
in e); PISO's non-iterated pressure-velocity splitting (whose first-order part
on this flow is a pure gradient the projection removes); the first `backward`
step which OpenFOAM takes as Euler implicit (one O(dt^2) local error).  Hence a
FACTOR-3 window, declared before compute, not an equality.

Refusals are `raise` and `sys.exit(2)`.  Zero `assert` (L-332).
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: exact_f18.py must not run under `python3 -O`.\n")
    sys.exit(2)

import json
import math
import argparse

import numpy as np

# ---------------------------------------------------------------------------
# THE CASE, FROZEN.
# ---------------------------------------------------------------------------
NU = 0.1
U0 = 1.0
L = 2.0 * math.pi
T_END = 2.0
# name, N (cells per side), steps (dt = T_END/steps): Co = U0 dt / h = 0.2 at every level
LEVELS = (("coarse", 64, 100), ("medium", 128, 200), ("fine", 256, 400))
MODEL_LEVELS = ("coarse", "medium")          # integrated; fine is extrapolated


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def h_of(n):
    return L / float(n)


def dt_of(steps):
    return T_END / float(steps)


def u_exact(x, y, t):
    return U0 * np.sin(x) * np.cos(y) * math.exp(-2.0 * NU * t)


def v_exact(x, y, t):
    return -U0 * np.cos(x) * np.sin(y) * math.exp(-2.0 * NU * t)


def p_exact(x, y, t):
    return U0 ** 2 * (np.cos(2 * x) + np.cos(2 * y)) / 4.0 * math.exp(-4.0 * NU * t)


def ke_norm_exact(t):
    """mean over the box of |u|^2 / 2 = (U0^2/4) e^{-4 nu t}."""
    return U0 ** 2 / 4.0 * math.exp(-4.0 * NU * t)


# ---------------------------------------------------------------------------
# THE DISCRETE MODEL (periodic in both directions)
# ---------------------------------------------------------------------------
def grid(n):
    h = h_of(n)
    c = (np.arange(n) + 0.5) * h
    return h, c, c


def _operators(n):
    """Sparse periodic operators on the n x n grid at t = 0:
    K0: linearised convection about U(0) (scales as e^{-2 nu t});
    Lm: Laplacian; Gx, Gy: wide gradient; the Rhie-Chow-corrected divergence
    blocks; plus the residual fields r_conv0, r_diff0, d0 and the exact fields."""
    import scipy.sparse as sp
    h, xc, yc = grid(n)
    X, Y = np.meshgrid(xc, yc)
    U = u_exact(X, Y, 0.0); V = v_exact(X, Y, 0.0); P = p_exact(X, Y, 0.0)
    N = n * n
    vol = h * h

    def cid(i, j):
        return (j % n) * n + (i % n)

    I = np.arange(n)
    ii, jj = np.meshgrid(I, I)                       # [j, i]
    Pc = cid(ii, jj).ravel()
    E = cid(ii + 1, jj).ravel(); W = cid(ii - 1, jj).ravel()
    Nn = cid(ii, jj + 1).ravel(); S = cid(ii, jj - 1).ravel()
    u = U.ravel(); v = V.ravel(); p = P.ravel()

    # face values / fluxes (outward from P) for east and north faces
    Ue = 0.5 * (u + u[E]); Ve = 0.5 * (v + v[E]); pe = 0.5 * (p + p[E]); phie = Ue * h
    Un = 0.5 * (u + u[Nn]); Vn = 0.5 * (v + v[Nn]); pn = 0.5 * (p + p[Nn]); phin = Vn * h
    # west/south faces are the neighbours' east/north faces with reversed sign
    Uw = Ue[W]; Vw = Ve[W]; pw = pe[W]; phiw = -phie[W]
    Us = Un[S]; Vs = Vn[S]; ps = pn[S]; phis = -phin[S]

    # residuals of the exact field
    cu = (phie * Ue + phiw * Uw + phin * Un + phis * Us) / vol
    cv = (phie * Ve + phiw * Vw + phin * Vn + phis * Vs) / vol
    lu = (u[E] + u[W] + u[Nn] + u[S] - 4 * u) / vol
    lv = (v[E] + v[W] + v[Nn] + v[S] - 4 * v) / vol
    gpx = (pe - pw) / h; gpy = (pn - ps) / h
    # exact: (u.grad)u + grad p = 0 for TGV, and lap u = -2u
    r_conv_u = cu + gpx; r_conv_v = cv + gpy
    r_diff_u = -NU * (lu + 2.0 * u); r_diff_v = -NU * (lv + 2.0 * v)
    d0 = phie + phiw + phin + phis

    def coo(rows, cols, vals, shape):
        return sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=shape)

    # Laplacian (per volume)
    one = np.ones(N)
    Lm = coo([Pc, Pc, Pc, Pc, Pc], [Pc, E, W, Nn, S],
             [-4 * one / vol, one / vol, one / vol, one / vol, one / vol], (N, N))
    # wide gradient
    Gx = coo([Pc, Pc], [E, W], [0.5 * one / h, -0.5 * one / h], (N, N))
    Gy = coo([Pc, Pc], [Nn, S], [0.5 * one / h, -0.5 * one / h], (N, N))
    # linearised convection K0 (2N x 2N): (1/V) sum_f [phi_f e_f + (e_f.n) h U_f]
    rows, cols, vals = [], [], []

    def addf(rowbase, colbase, r, c, val):
        rows.append(rowbase + r); cols.append(colbase + c); vals.append(val)
    for (nb, phi, Uf, Vf, dirx) in ((E, phie, Ue, Ve, True), (W, phiw, Uw, Vw, True),
                                     (Nn, phin, Un, Vn, False), (S, phis, Us, Vs, False)):
        sgn = 1.0 if nb is E or nb is Nn else -1.0     # outward normal sign along the axis
        for comp, base, Ufk in ((0, 0, Uf), (1, N, Vf)):
            addf(base, base, Pc, Pc, phi / (2 * vol)); addf(base, base, Pc, nb, phi / (2 * vol))
            cb = 0 if dirx else N
            addf(base, cb, Pc, Pc, sgn * h * Ufk / (2 * vol)); addf(base, cb, Pc, nb, sgn * h * Ufk / (2 * vol))
    K0 = coo(rows, cols, vals, (2 * N, 2 * N))
    # divergence of interpolated error (per face, summed per cell): D (N x 2N)
    Dm = coo([Pc, Pc, Pc, Pc, Pc, Pc, Pc, Pc],
             [Pc, E, Pc, W, N + Pc, N + Nn, N + Pc, N + S],
             [0.5 * h * one, 0.5 * h * one, -0.5 * h * one, -0.5 * h * one,
              0.5 * h * one, 0.5 * h * one, -0.5 * h * one, -0.5 * h * one], (N, 2 * N))
    # Rhie-Chow: - rA h [ (q_N - q_P)/h - 0.5((Gq)_P + (Gq)_N).n ] per face, summed; rA set later
    Lc = coo([Pc, Pc, Pc, Pc, Pc], [Pc, E, W, Nn, S], [-4 * one, one, one, one, one], (N, N))  # compact, times 1
    # wide-Laplacian-like term via interpolated gradient: sum over faces of 0.5((Gq)_P+(Gq)_N).n h
    Ex = sp.csr_matrix((one, (Pc, E)), shape=(N, N)); Wx = sp.csr_matrix((one, (Pc, W)), shape=(N, N))
    Ny_ = sp.csr_matrix((one, (Pc, Nn)), shape=(N, N)); Sy = sp.csr_matrix((one, (Pc, S)), shape=(N, N))
    Iden = sp.identity(N, format="csr")
    Wide = 0.5 * h * ((Iden + Ex) @ Gx - (Iden + Wx) @ Gx + (Iden + Ny_) @ Gy - (Iden + Sy) @ Gy)
    RC_shape = -(Lc - Wide)          # to be scaled by rA h... : flux = -rA h [(q_N-q_P)/h - avg(Gq).n] = -rA[(q_N-q_P) - h avg(Gq).n]
    return dict(n=n, N=N, h=h, xc=xc, yc=yc, u=u, v=v, Lm=Lm, Gx=Gx, Gy=Gy, K0=K0, Dm=Dm,
                RC=RC_shape, r_conv=np.concatenate([r_conv_u, r_conv_v]),
                r_diff=np.concatenate([r_diff_u, r_diff_v]), d0=d0,
                r_conv_L2=float(math.sqrt(np.mean(r_conv_u ** 2 + r_conv_v ** 2))),
                r_diff_L2=float(math.sqrt(np.mean(r_diff_u ** 2 + r_diff_v ** 2))))


def discrete_error(n, steps):
    """Integrate the linearised error equations to T_END with BDF2 and return
    the predicted error field and scalars at t = T_END."""
    import scipy.sparse as sp
    import scipy.sparse.linalg as spl
    op = _operators(n)
    N, h = op["N"], op["h"]
    dt = dt_of(steps)
    aP = 1.5 / dt + 4.0 * NU / h ** 2          # BDF2 diagonal + diffusion diagonal
    rA = 1.0 / aP
    Iden = sp.identity(N, format="csr")
    Z = sp.csr_matrix((N, N))
    A = sp.bmat([[1.5 / dt * Iden - NU * op["Lm"], Z, op["Gx"]],
                 [Z, 1.5 / dt * Iden - NU * op["Lm"], op["Gy"]],
                 [op["Dm"][:, :N], op["Dm"][:, N:], rA * op["RC"]]], format="csc")
    # pressure level: pin via Lagrange multiplier
    ones = np.ones((N, 1))
    A = sp.bmat([[A, sp.vstack([sp.csr_matrix((2 * N, 1)), sp.csr_matrix(ones)])],
                 [sp.hstack([sp.csr_matrix((1, 2 * N)), sp.csr_matrix(ones.T)]), None]], format="csc")
    lu = spl.splu(A)
    K0 = op["K0"]
    dec2 = lambda t: math.exp(-2 * NU * t)
    dec4 = lambda t: math.exp(-4 * NU * t)
    # BDF2 time-derivative residual of the exact decay, per unit of u(0)
    bdf2_fac = (3.0 - 4.0 * math.exp(2 * NU * dt) + math.exp(4 * NU * dt)) / (2 * dt) + 2 * NU
    uex0 = np.concatenate([op["u"], op["v"]])

    def forcing(t):
        r = op["r_conv"] * dec4(t) + op["r_diff"] * dec2(t) + bdf2_fac * uex0 * dec2(t)
        d = op["d0"] * dec2(t)
        return r, d

    e_old = np.zeros(2 * N); e_cur = np.zeros(2 * N)
    c_old = np.zeros(2 * N); c_cur = np.zeros(2 * N)
    t = 0.0
    for k in range(steps):
        t_new = t + dt
        r, d = forcing(t_new)
        # explicit AB2 for the linearised convection; first step uses AB1
        c_pred = 2 * c_cur - c_old if k > 0 else c_cur
        rhs_mom = (2.0 * e_cur - 0.5 * e_old) / dt - c_pred - r
        rhs = np.concatenate([rhs_mom, -d, [0.0]])
        sol = lu.solve(rhs)
        e_new = sol[:2 * N]
        e_old, e_cur = e_cur, e_new
        c_old, c_cur = c_cur, (K0 @ e_cur) * dec2(t_new)
        t = t_new
    eu = e_cur[:N]; ev = e_cur[N:]
    e2 = float(math.sqrt(np.mean(eu ** 2 + ev ** 2)) / U0)
    uT = op["u"] * dec2(T_END); vT = op["v"] * dec2(T_END)
    ke_err = float(np.mean(uT * eu + vT * ev + 0.5 * (eu ** 2 + ev ** 2)))
    return dict(n=n, steps=steps, h=h, dt=dt, xc=op["xc"], yc=op["yc"],
                eu=eu.reshape(n, n), ev=ev.reshape(n, n), E2_pred=e2, ke_err_pred=ke_err,
                r_conv_L2=op["r_conv_L2"], r_diff_L2=op["r_diff_L2"],
                d_max=float(np.max(np.abs(op["d0"]))), bdf2_residual_factor=bdf2_fac)


_CACHE = {}


def model(name):
    if name not in _CACHE:
        lv = dict((nm, (n, s)) for nm, n, s in LEVELS)
        if name not in MODEL_LEVELS:
            refuse("level %r is not integrated by the model; it is extrapolated" % name)
        _CACHE[name] = discrete_error(*lv[name])
    return _CACHE[name]


def predictions():
    """Integrated at coarse and medium; fine extrapolated with the model's own order."""
    if "table" not in _CACHE:
        mc, mm = model("coarse"), model("medium")
        p_e2 = math.log(mc["E2_pred"] / mm["E2_pred"]) / math.log(2.0)
        p_ke = math.log(abs(mc["ke_err_pred"]) / abs(mm["ke_err_pred"])) / math.log(2.0)
        fine_e2 = mm["E2_pred"] / 2.0 ** p_e2
        fine_ke = mm["ke_err_pred"] / 2.0 ** p_ke
        tab = []
        for nm, n, s in LEVELS:
            if nm in MODEL_LEVELS:
                m = model(nm)
                tab.append(dict(name=nm, n=n, cells=n * n, steps=s, h=m["h"], dt=m["dt"],
                                E2_pred=m["E2_pred"], ke_err_pred=m["ke_err_pred"],
                                r_conv_L2=m["r_conv_L2"], r_diff_L2=m["r_diff_L2"], source="integrated"))
            else:
                tab.append(dict(name=nm, n=n, cells=n * n, steps=s, h=h_of(n), dt=dt_of(s),
                                E2_pred=fine_e2, ke_err_pred=fine_ke,
                                source="extrapolated from medium with model orders %.4f (E2), %.4f (KE)" % (p_e2, p_ke)))
        _CACHE["table"] = tab
        _CACHE["orders"] = (p_e2, p_ke)
    return _CACHE["table"]


def model_orders():
    predictions()
    return _CACHE["orders"]


# ---------------------------------------------------------------------------
# CONTROLS
# ---------------------------------------------------------------------------
def control_symbolic_substitution():
    try:
        import sympy as sp
    except ImportError:
        refuse("sympy is not importable; the exact solution cannot be verified by substitution")
    x, y, t = sp.symbols("x y t", real=True)
    nu = sp.Rational(1, 10)
    u = sp.sin(x) * sp.cos(y) * sp.exp(-2 * nu * t)
    v = -sp.cos(x) * sp.sin(y) * sp.exp(-2 * nu * t)
    p = (sp.cos(2 * x) + sp.cos(2 * y)) / 4 * sp.exp(-4 * nu * t)
    res = {
        "continuity": sp.simplify(sp.diff(u, x) + sp.diff(v, y)),
        "x_momentum": sp.simplify(sp.diff(u, t) + u * sp.diff(u, x) + v * sp.diff(u, y) + sp.diff(p, x)
                                  - nu * (sp.diff(u, x, 2) + sp.diff(u, y, 2))),
        "y_momentum": sp.simplify(sp.diff(v, t) + u * sp.diff(v, x) + v * sp.diff(v, y) + sp.diff(p, y)
                                  - nu * (sp.diff(v, x, 2) + sp.diff(v, y, 2))),
    }
    bad = [k for k, r in res.items() if r != 0]
    if bad:
        refuse("SYMBOLIC SUBSTITUTION FAILED: residuals %s are not identically zero" % bad)
    if abs(float(nu) - NU) > 1e-15:
        refuse("NU disagrees with the symbolic nu")
    return dict(control="symbolic_substitution_into_unsteady_NS",
                residuals=dict((k, str(r)) for k, r in res.items()), passed=True)


def control_substitution_is_able_to_fail():
    import sympy as sp
    x, y, t = sp.symbols("x y t", real=True)
    nu = sp.Rational(1, 10)
    u = sp.sin(x) * sp.cos(y) * sp.exp(-sp.Rational(23, 10) * nu * t)     # PLANT: 2.3 nu
    v = -sp.cos(x) * sp.sin(y) * sp.exp(-sp.Rational(23, 10) * nu * t)
    p = (sp.cos(2 * x) + sp.cos(2 * y)) / 4 * sp.exp(-sp.Rational(23, 5) * nu * t)
    r = sp.simplify(sp.diff(u, t) + u * sp.diff(u, x) + v * sp.diff(u, y) + sp.diff(p, x)
                    - nu * (sp.diff(u, x, 2) + sp.diff(u, y, 2)))
    if r == 0:
        refuse("PLANTED CONTROL FAILED: decay rate planted at 2.3 nu still gave zero residual")
    return dict(control="PZ-F18-DECAY_planted_2.3nu_must_be_nonzero", planted_factor=1.15,
                residual_is_zero=False, passed=True)


def control_ladder_is_geometrically_similar():
    rh = [h_of(LEVELS[i][1]) / h_of(LEVELS[i + 1][1]) for i in range(2)]
    rt = [dt_of(LEVELS[i][2]) / dt_of(LEVELS[i + 1][2]) for i in range(2)]
    if max(abs(r - 2.0) for r in rh + rt) > 1e-12:
        refuse("the ladder is not a factor-2 refinement in h and dt: %s %s" % (rh, rt))
    co = [U0 * dt_of(s) / h_of(n) for _nm, n, s in LEVELS]
    if max(abs(c - co[0]) for c in co) > 1e-12:
        refuse("Courant number is not constant across the ladder: %s" % co)
    return dict(control="constant_ratio_refinement_h_and_dt", h_ratios=rh, dt_ratios=rt, courant=co[0], passed=True)


def control_model_is_second_order_and_forced():
    tab = predictions()
    p_e2, p_ke = model_orders()
    for row in tab:
        if row.get("source") == "integrated" and (row["r_conv_L2"] <= 0.0 or row["r_diff_L2"] <= 0.0):
            refuse("PLANTED CONTROL FAILED: the stencil evaluator returned a zero truncation residual "
                   "on the exact field at level %s" % row["name"])
    if not (1.7 <= p_e2 <= 2.3 and 1.7 <= p_ke <= 2.3):
        refuse("the model's predicted errors do not scale as h^2: orders E2 %.3f, KE %.3f" % (p_e2, p_ke))
    ke = [row["ke_err_pred"] for row in tab]
    if not (np.sign(ke[0]) == np.sign(ke[1]) == np.sign(ke[2])):
        refuse("the model's predicted KE error changes sign across the ladder %s" % ke)
    return dict(control="model_forced_and_second_order", model_orders=dict(E2=p_e2, KE=p_ke),
                ke_err_pred=ke, passed=True)


def selftest_predicate(controls):
    if len(controls) != 4:
        return False, "expected 4 controls, ran %d" % len(controls)
    for c in controls:
        if not c.get("passed"):
            return False, "control %s did not pass" % c.get("control")
    if not __debug__:
        return False, "running under -O"
    return True, ("4 controls green: the closed form satisfies continuity and both momentum equations "
                  "identically under symbolic substitution into the unsteady NS equations; a decay "
                  "rate planted at 2.3 nu makes the residual non-zero; h and dt refine by exactly 2 at "
                  "constant Courant number; the discretisation model is forced by a non-zero residual "
                  "and scales as h^2 with a sign-stable KE error")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    controls = [control_symbolic_substitution(), control_substitution_is_able_to_fail(),
                control_ladder_is_geometrically_similar(), control_model_is_second_order_and_forced()]
    tab = predictions()
    if a.json:
        print(json.dumps(dict(constants=dict(nu=NU, U0=U0, L=L, T=T_END), levels=tab,
                              ke_norm_exact_T=ke_norm_exact(T_END), controls=controls), indent=2))
        return 0
    ok, why = selftest_predicate(controls)
    if a.selftest:
        print(json.dumps(dict(controls=controls, levels=tab, ke_norm_exact_T=ke_norm_exact(T_END),
                              predicate=dict(ok=ok, why=why)), indent=2))
        if not ok:
            refuse("SELFTEST DID NOT ESTABLISH ITS CLAIM: %s" % why)
        print("\nSELFTEST GREEN -- %s" % why)
        return 0
    print("nu=%g U0=%g L=%.15g T=%g  KE_norm_exact(T)=%.15f" % (NU, U0, L, T_END, ke_norm_exact(T_END)))
    for r in tab:
        print("%-7s %dx%d steps=%d h=%.5g dt=%.5g  E2_pred=%.6e  KE_err_pred=%.6e  [%s]"
              % (r["name"], r["n"], r["n"], r["steps"], r["h"], r["dt"], r["E2_pred"], r["ke_err_pred"], r["source"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
