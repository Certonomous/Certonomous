#!/usr/bin/env python3
"""
F22 -- THE EXACT SOLUTION of the 2-D decaying Lamb-Oseen vortex, and the
DISCRETISATION-DERIVED error prediction every F22 band is built from.

    omega(r, t) = Gamma / (4 pi nu t') exp(-r^2 / (4 nu t')),        t' = t + T0
    u_theta     = Gamma / (2 pi r) (1 - exp(-r^2 / (4 nu t'))),      u_r = 0
    p(r, t)     = -(Gamma/2pi)^2 / (8 nu t') [ (1 - e^{-eta})^2 / eta + 2 (E1(eta) - E1(2 eta)) ],
                  eta = r^2 / (4 nu t'),  E1 the exponential integral
on the square [-L, L]^2 with the far-field velocity FIXED to the potential
vortex Gamma/(2 pi r) theta-hat, which equals the exact velocity there to
exp(-L^2 / (4 nu (T_END + T0))) = 5e-12 relative, so the boundary datum is
time-independent to round-off.

THE REFERENCE IS NOT A PAPER ON THIS BOX.  IT IS A SUBSTITUTION.  The vorticity
form is substituted symbolically into the 2-D vorticity transport equation
(omega_t + u.grad omega = nu lap omega; u.grad omega = 0 for an axisymmetric
vortex) and the velocity is checked to induce that vorticity and to satisfy
continuity; the radial momentum balance dp/dr = u_theta^2 / r is checked
symbolically for the closed-form pressure; a planted control (decay t' -> 1.1 t')
must make the vorticity residual non-zero.

THE BAND PRINCIPLE -- derived from the discretisation, not measured.  The F18
model adapted to Dirichlet velocity boundaries: the solver's own uniform-
Cartesian stencils (Gauss linear convection, Gauss linear orthogonal Laplacian,
Gauss linear pressure gradient with a zero-gradient boundary datum for the
pressure error, Rhie-Chow interpolated flux, BDF2 `backward`) are evaluated on
the exact field at every step, giving the momentum residual r(t), the
continuity residual d(t) and the BDF2 residual of the exact time dependence.
The leading-order error e obeys the LINEARISED discrete equations forced by
those residuals,

    d e/dt + C_h'(U(t)) e - nu L_h e + G_h q = -r(t),   D_h e + RC(q) = -d(t),   e = 0 on the boundary,

integrated with the same BDF2 step (diffusion and projection implicit with one
sparse LU, the linearised convection explicit second-order Adams-Bashforth,
matrix-free about the exact field at the new time level), on the two grids
MODEL_GRIDS of the ladder's own family; every ladder level is extrapolated from
the finest integrated grid with the model's own observed order (a control
requires it in [1.7, 2.3]).

Omissions, stated: the nonlinear feedback of the error on itself; PISO's
non-iterated splitting; the Euler-implicit first `backward` step; the boundary
pressure datum (zero-gradient on q against fixedFluxPressure in the solver),
confined to the boundary ring where the velocity is 5 % of the core value.
Hence a FACTOR-3 window, declared before compute, not an equality.

Refusals are `raise` and `sys.exit(2)`.  Zero `assert` (L-332).
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: exact_f22.py must not run under `python3 -O`.\n")
    sys.exit(2)

import json
import math
import argparse

import numpy as np
from scipy.special import exp1

# ---------------------------------------------------------------------------
# THE CASE, FROZEN.
# ---------------------------------------------------------------------------
GAMMA = 1.0                              # circulation
NU = 0.01
T0 = 2.0                                 # virtual origin: core radius sqrt(4 nu T0) = 0.2828 at t = 0
L = 2.5                                  # box half-width: [-L, L]^2
T_END = 4.0                              # t' = 6 at the end: core radius 0.4899; far-field datum exact to 5e-12
R_C0 = math.sqrt(4.0 * NU * T0)
U_REF = GAMMA / (2.0 * math.pi * R_C0)   # the velocity scale Gamma / (2 pi r_c(0)) = 0.5627, the normaliser
# name, N (cells per side over 2L), steps to T_END (dt = T_END/steps): Co ~ 0.14 at every level
LEVELS = (("coarse", 192, 400), ("medium", 384, 800), ("fine", 768, 1600))
MODEL_GRIDS = ((48, 100), (96, 200))     # integrated: the ladder family's two grids below the coarse level
# (96^2 x 200 = 27 s; 192^2 x 400 was integrated ONCE in the writing invocation -- 5.9 min, 5.7 GB RSS on a
# loaded box -- as a cross-check of the extrapolation and is NOT part of the instrument: prereg section 4)


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def h_of(n):
    return 2.0 * L / float(n)


def dt_of(steps):
    return T_END / float(steps)


def _tp(t):
    return t + T0


def omega_exact(x, y, t):
    r2 = np.asarray(x) ** 2 + np.asarray(y) ** 2
    return GAMMA / (4.0 * math.pi * NU * _tp(t)) * np.exp(-r2 / (4.0 * NU * _tp(t)))


def _utheta_over_r(x, y, t):
    """u_theta / r, finite at r = 0 (series), so u = -y (u_theta/r), v = x (u_theta/r)."""
    r2 = np.asarray(x, dtype=float) ** 2 + np.asarray(y, dtype=float) ** 2
    s = 4.0 * NU * _tp(t)
    with np.errstate(divide="ignore", invalid="ignore"):
        f = np.where(r2 > 1e-300, (1.0 - np.exp(-r2 / s)) / r2, 1.0 / s)
    return GAMMA / (2.0 * math.pi) * f


def u_exact(x, y, t):
    return -np.asarray(y, dtype=float) * _utheta_over_r(x, y, t)


def v_exact(x, y, t):
    return np.asarray(x, dtype=float) * _utheta_over_r(x, y, t)


def dudt_exact(x, y, t):
    """d/dt of u: u_theta = a (1 - e^{-eta}) / r, d u_theta/dt = -a r e^{-eta} / (4 nu t'^2)."""
    r2 = np.asarray(x, dtype=float) ** 2 + np.asarray(y, dtype=float) ** 2
    s = 4.0 * NU * _tp(t)
    g = -GAMMA / (2.0 * math.pi) * np.exp(-r2 / s) / (s * _tp(t))     # (d u_theta/dt) / r
    return -np.asarray(y, dtype=float) * g, np.asarray(x, dtype=float) * g


def u_potential(x, y):
    """The far-field datum: the potential vortex Gamma / (2 pi r) theta-hat."""
    r2 = np.asarray(x, dtype=float) ** 2 + np.asarray(y, dtype=float) ** 2
    a = GAMMA / (2.0 * math.pi) / r2
    return -np.asarray(y, dtype=float) * a, np.asarray(x, dtype=float) * a


def p_exact(x, y, t):
    r2 = np.asarray(x, dtype=float) ** 2 + np.asarray(y, dtype=float) ** 2
    s = 4.0 * NU * _tp(t)
    eta = r2 / s
    a2 = (GAMMA / (2.0 * math.pi)) ** 2
    with np.errstate(divide="ignore", invalid="ignore"):
        term = np.where(eta > 1e-12, (1.0 - np.exp(-eta)) ** 2 / np.where(eta > 1e-12, eta, 1.0), eta)
        ei = np.where(eta > 1e-12, exp1(np.where(eta > 1e-12, eta, 1.0)) - exp1(np.where(eta > 1e-12, 2 * eta, 2.0)), math.log(2.0))
    return -a2 / (2.0 * s) * (term + 2.0 * ei)


def omega_peak_exact(t=T_END):
    return GAMMA / (4.0 * math.pi * NU * _tp(t))


# ---------------------------------------------------------------------------
# THE DISCRETE MODEL (Dirichlet velocity on the four sides)
# ---------------------------------------------------------------------------
def grid(n):
    h = h_of(n)
    c = -L + (np.arange(n) + 0.5) * h
    return h, c, c


def curl_h(u2d, v2d, h):
    """The grader's vorticity stencil: central differences on the cell-centred
    grid, interior cells only (the boundary ring is dropped)."""
    return ((v2d[1:-1, 2:] - v2d[1:-1, :-2]) - (u2d[2:, 1:-1] - u2d[:-2, 1:-1])) / (2.0 * h)


class _Mesh(object):
    """Face structures on an n x n cell-centred grid with Dirichlet velocity
    boundaries.  With Ax = (Spx - Snx)^T, (Ax @ F)[P] += F and (Ax @ F)[N] -= F
    for a face quantity F counted positive in the +x sense: the outward-normal
    sum every finite-volume operator below is built from."""

    def __init__(self, n):
        import scipy.sparse as sp
        self.n = n
        self.N = N = n * n
        self.h = h = h_of(n)
        _h, xc, yc = grid(n)
        X, Y = np.meshgrid(xc, yc)
        self.xc, self.yc = X.ravel(), Y.ravel()
        I = np.arange(n)
        ii, jj = np.meshgrid(I, I)
        cid = lambda i, j: (j * n + i).ravel()
        px = cid(ii[:, :-1], jj[:, :-1]); nx_ = cid(ii[:, :-1] + 1, jj[:, :-1])     # interior x-faces P -> N = east
        py = cid(ii[:-1, :], jj[:-1, :]); ny_ = cid(ii[:-1, :], jj[:-1, :] + 1)     # interior y-faces P -> N = north
        pick = lambda c: sp.csr_matrix((np.ones(c.size), (np.arange(c.size), c)), shape=(c.size, N))
        self.Spx, self.Snx, self.Spy, self.Sny = pick(px), pick(nx_), pick(py), pick(ny_)
        self.Ax = (self.Spx - self.Snx).T.tocsr()
        self.Ay = (self.Spy - self.Sny).T.tocsr()
        self.Mx = 0.5 * (self.Spx + self.Snx)
        self.My = 0.5 * (self.Spy + self.Sny)
        self.Jx = self.Snx - self.Spx                     # face difference q_N - q_P
        self.Jy = self.Sny - self.Spy
        self.bW = cid(ii[:, 0], jj[:, 0]); self.bE = cid(ii[:, -1], jj[:, -1])
        self.bS = cid(ii[0, :], jj[0, :]); self.bN = cid(ii[-1, :], jj[-1, :])
        self.bnd = (("W", self.bW, -1.0, 0.0, self.xc[self.bW] - h / 2, self.yc[self.bW]),
                    ("E", self.bE, 1.0, 0.0, self.xc[self.bE] + h / 2, self.yc[self.bE]),
                    ("S", self.bS, 0.0, -1.0, self.xc[self.bS], self.yc[self.bS] - h / 2),
                    ("N", self.bN, 0.0, 1.0, self.xc[self.bN], self.yc[self.bN] + h / 2))
        db = np.zeros(N); gbx = np.zeros(N); gby = np.zeros(N)
        for _nm, cells, nx1, ny1, _bx, _by in self.bnd:
            np.add.at(db, cells, -2.0); np.add.at(gbx, cells, nx1); np.add.at(gby, cells, ny1)
        # Laplacian, e = 0 on boundary faces: sum_f (e_N - e_P)/h^2, boundary face (0 - e_P)/(h/2)/h
        self.Lm = (self.Ax @ self.Jx + self.Ay @ self.Jy + sp.diags(db)) / h ** 2
        # gradient, zero-gradient boundary datum q_b = q_P: (1/h) sum_f q_f n
        self.Gx = (self.Ax @ self.Mx + sp.diags(gbx)) / h
        self.Gy = (self.Ay @ self.My + sp.diags(gby)) / h
        # divergence of the interpolated error, boundary faces 0: sum_f e_f . n h
        self.Dx = h * (self.Ax @ self.Mx)
        self.Dy = h * (self.Ay @ self.My)
        # Rhie-Chow correction per interior face: -rA [(q_N - q_P) - h avg(Gq).n]; cell sum; times rA outside
        self.RC = -(self.Ax @ (self.Jx - h * self.Mx @ self.Gx) + self.Ay @ (self.Jy - h * self.My @ self.Gy))

    def exact_faces(self, t):
        h = self.h
        u = u_exact(self.xc, self.yc, t); v = v_exact(self.xc, self.yc, t)
        Ufx = self.Mx @ u; Vfx = self.Mx @ v; phix = Ufx * h
        Ufy = self.My @ u; Vfy = self.My @ v; phiy = Vfy * h
        bnd = {}
        for nm, _cells, nx1, ny1, bx, by in self.bnd:
            ub, vb = u_potential(bx, by)
            bnd[nm] = (ub, vb, (ub * nx1 + vb * ny1) * h)
        return u, v, Ufx, Vfx, phix, Ufy, Vfy, phiy, bnd

    def residuals(self, t):
        """Truncation residuals of the exact field at time t on this grid."""
        h = self.h; V = h * h
        u, v, Ufx, Vfx, phix, Ufy, Vfy, phiy, bnd = self.exact_faces(t)
        cu = self.Ax @ (phix * Ufx) + self.Ay @ (phiy * Ufy)
        cv = self.Ax @ (phix * Vfx) + self.Ay @ (phiy * Vfy)
        d = self.Ax @ phix + self.Ay @ phiy
        p = p_exact(self.xc, self.yc, t)
        gpx = self.Ax @ (self.Mx @ p); gpy = self.Ay @ (self.My @ p)
        lu = self.Ax @ (self.Jx @ u) + self.Ay @ (self.Jy @ u)
        lv = self.Ax @ (self.Jx @ v) + self.Ay @ (self.Jy @ v)
        for nm, cells, nx1, ny1, bx, by in self.bnd:
            ub, vb, phib = bnd[nm]
            np.add.at(cu, cells, phib * ub); np.add.at(cv, cells, phib * vb); np.add.at(d, cells, phib)
            pb = p_exact(bx, by, t)
            np.add.at(gpx, cells, pb * nx1); np.add.at(gpy, cells, pb * ny1)
            np.add.at(lu, cells, 2.0 * (ub - u[cells])); np.add.at(lv, cells, 2.0 * (vb - v[cells]))
        dut, dvt = dudt_exact(self.xc, self.yc, t)
        r_conv_u = cu / V + gpx / h; r_conv_v = cv / V + gpy / h          # exact: u.grad u + grad p = 0
        r_diff_u = -NU * lu / V + dut; r_diff_v = -NU * lv / V + dvt      # exact: nu lap u = du/dt
        return dict(u=u, v=v, r_conv=np.concatenate([r_conv_u, r_conv_v]), r_diff=np.concatenate([r_diff_u, r_diff_v]),
                    d=d, Ufx=Ufx, Vfx=Vfx, phix=phix, Ufy=Ufy, Vfy=Vfy, phiy=phiy)

    def conv_lin(self, res, e):
        """Linearised convection about the exact field: (1/V) sum_f [phi_f e_f + (e_f . n) |S_f| U_f], interior faces only."""
        N = self.N; h = self.h; V = h * h
        eu, ev = e[:N], e[N:]
        efx_u = self.Mx @ eu; efx_v = self.Mx @ ev
        efy_u = self.My @ eu; efy_v = self.My @ ev
        cu = self.Ax @ (res["phix"] * efx_u + efx_u * h * res["Ufx"]) + self.Ay @ (res["phiy"] * efy_u + efy_v * h * res["Ufy"])
        cv = self.Ax @ (res["phix"] * efx_v + efx_u * h * res["Vfx"]) + self.Ay @ (res["phiy"] * efy_v + efy_v * h * res["Vfy"])
        return np.concatenate([cu, cv]) / V


def discrete_error(n, steps):
    """Integrate the linearised error equations to T_END with BDF2 and return
    the predicted error field and scalars at t = T_END."""
    import scipy.sparse as sp
    import scipy.sparse.linalg as spl
    M = _Mesh(n)
    N, h = M.N, M.h
    dt = dt_of(steps)
    aP = 1.5 / dt + 4.0 * NU / h ** 2
    rA = 1.0 / aP
    Iden = sp.identity(N, format="csr")
    Z = sp.csr_matrix((N, N))
    A = sp.bmat([[1.5 / dt * Iden - NU * M.Lm, Z, M.Gx],
                 [Z, 1.5 / dt * Iden - NU * M.Lm, M.Gy],
                 [M.Dx, M.Dy, rA * M.RC]], format="csc")
    ones = np.ones((N, 1))
    A = sp.bmat([[A, sp.vstack([sp.csr_matrix((2 * N, 1)), sp.csr_matrix(ones)])],
                 [sp.hstack([sp.csr_matrix((1, 2 * N)), sp.csr_matrix(ones.T)]), None]], format="csc")
    lu = spl.splu(A)
    e_old = np.zeros(2 * N); e_cur = np.zeros(2 * N)
    c_old = np.zeros(2 * N); c_cur = np.zeros(2 * N)
    U_prev2 = np.concatenate([u_exact(M.xc, M.yc, 0.0), v_exact(M.xc, M.yc, 0.0)])
    U_prev1 = U_prev2
    r_conv_L2 = r_diff_L2 = 0.0
    t = 0.0
    for k in range(steps):
        t_new = t + dt
        res = M.residuals(t_new)
        U_new = np.concatenate([res["u"], res["v"]])
        dut, dvt = dudt_exact(M.xc, M.yc, t_new)
        if k == 0:
            bdf = (U_new - U_prev1) / dt - np.concatenate([dut, dvt])
        else:
            bdf = (1.5 * U_new - 2.0 * U_prev1 + 0.5 * U_prev2) / dt - np.concatenate([dut, dvt])
        r = res["r_conv"] + res["r_diff"] + bdf
        if k == steps - 1:
            r_conv_L2 = float(math.sqrt(np.mean(res["r_conv"] ** 2))); r_diff_L2 = float(math.sqrt(np.mean(res["r_diff"] ** 2)))
        c_pred = 2 * c_cur - c_old if k > 0 else c_cur
        rhs_mom = (2.0 * e_cur - 0.5 * e_old) / dt - c_pred - r
        rhs = np.concatenate([rhs_mom, -res["d"], [0.0]])
        sol = lu.solve(rhs)
        e_new = sol[:2 * N]
        e_old, e_cur = e_cur, e_new
        c_old, c_cur = c_cur, M.conv_lin(res, e_cur)
        U_prev2, U_prev1 = U_prev1, U_new
        t = t_new
    eu = e_cur[:N].reshape(n, n); ev = e_cur[N:].reshape(n, n)
    e2 = float(math.sqrt(np.mean(eu ** 2 + ev ** 2)) / U_REF)
    uT = u_exact(M.xc, M.yc, T_END).reshape(n, n); vT = v_exact(M.xc, M.yc, T_END).reshape(n, n)
    w_ex = curl_h(uT, vT, h); w_mod = curl_h(uT + eu, vT + ev, h)
    return dict(n=n, steps=steps, h=h, dt=dt, eu=eu, ev=ev, E2_pred=e2,
                peak_ref=float(np.max(w_ex)), peak_err_pred=float(np.max(w_mod) - np.max(w_ex)),
                r_conv_L2=r_conv_L2, r_diff_L2=r_diff_L2, courant=float(np.max(np.hypot(uT, vT)) * dt / h))


_CACHE = {}


def integrated(n, steps):
    if (n, steps) not in MODEL_GRIDS:
        refuse("grid %d^2 x %d is not integrated by the model; it is extrapolated" % (n, steps))
    if (n, steps) not in _CACHE:
        _CACHE[(n, steps)] = discrete_error(n, steps)
    return _CACHE[(n, steps)]


def predictions():
    if "table" not in _CACHE:
        mc, mm = integrated(*MODEL_GRIDS[0]), integrated(*MODEL_GRIDS[1])
        r = math.log(mc["h"] / mm["h"])
        p_e2 = math.log(mc["E2_pred"] / mm["E2_pred"]) / r
        p_pk = math.log(abs(mc["peak_err_pred"]) / abs(mm["peak_err_pred"])) / r
        tab = []
        for nm, n, s in LEVELS:
            if (n, s) in MODEL_GRIDS:
                m = integrated(n, s)
                tab.append(dict(name=nm, n=n, cells=n * n, steps=s, h=m["h"], dt=m["dt"], E2_pred=m["E2_pred"],
                                peak_err_pred=m["peak_err_pred"], courant=m["courant"], source="integrated"))
            else:
                f = h_of(n) / mm["h"]
                tab.append(dict(name=nm, n=n, cells=n * n, steps=s, h=h_of(n), dt=dt_of(s),
                                E2_pred=mm["E2_pred"] * f ** p_e2, peak_err_pred=mm["peak_err_pred"] * f ** p_pk,
                                courant=mm["courant"],
                                source="extrapolated from %d^2 x %d with model orders %.4f (E2), %.4f (peak vorticity)"
                                       % (mm["n"], mm["steps"], p_e2, p_pk)))
        _CACHE["table"] = tab
        _CACHE["orders"] = (p_e2, p_pk)
    return _CACHE["table"]


def model_orders():
    predictions()
    return _CACHE["orders"]


# ---------------------------------------------------------------------------
# CONTROLS
# ---------------------------------------------------------------------------
def _sym():
    import sympy as sp
    x, y, t = sp.symbols("x y t", real=True)
    nu, G, T0s = sp.symbols("nu Gamma T0", positive=True)
    return sp, x, y, t, nu, G, T0s


def control_symbolic_substitution():
    try:
        sp, x, y, t, nu, G, T0s = _sym()
    except ImportError:
        refuse("sympy is not importable; the exact solution cannot be verified by substitution")
    tp = t + T0s
    r2 = x ** 2 + y ** 2
    w = G / (4 * sp.pi * nu * tp) * sp.exp(-r2 / (4 * nu * tp))
    f = G / (2 * sp.pi) * (1 - sp.exp(-r2 / (4 * nu * tp))) / r2        # u_theta / r
    u = -y * f; v = x * f
    res = {
        "vorticity_transport": sp.simplify(sp.diff(w, t) + u * sp.diff(w, x) + v * sp.diff(w, y) - nu * (sp.diff(w, x, 2) + sp.diff(w, y, 2))),
        "curl_u_is_omega": sp.simplify(sp.diff(v, x) - sp.diff(u, y) - w),
        "continuity": sp.simplify(sp.diff(u, x) + sp.diff(v, y)),
    }
    # radial momentum balance for the closed-form pressure: dp/dr = u_theta^2 / r, checked on eta
    eta = sp.symbols("eta", positive=True)
    s = sp.symbols("s", positive=True)                                   # s = 4 nu t'
    a2 = (G / (2 * sp.pi)) ** 2
    P = -a2 / (2 * s) * ((1 - sp.exp(-eta)) ** 2 / eta + 2 * (sp.expint(1, eta) - sp.expint(1, 2 * eta)))
    r = sp.sqrt(s * eta)
    dP_dr = sp.diff(P, eta) * 2 * r / s                                  # deta/dr = 2 r / s
    ut2_over_r = (sp.sqrt(a2) * (1 - sp.exp(-eta)) / r) ** 2 / r
    res["radial_momentum_dp_dr"] = sp.simplify(dP_dr - ut2_over_r)
    bad = [k for k, v in res.items() if v != 0]
    if bad:
        refuse("SYMBOLIC SUBSTITUTION FAILED: residuals %s are not identically zero" % bad)
    # numeric: velocity at the far-field datum vs the exact velocity at T_END
    xs = np.array([L, L, -L, 0.3]); ys = np.array([0.0, 1.7, -2.2, L])
    ub, vb = u_potential(xs, ys)
    rel = np.max(np.hypot(ub - u_exact(xs, ys, T_END), vb - v_exact(xs, ys, T_END)) / np.hypot(ub, vb))
    if rel > 1e-10:
        refuse("the far-field datum differs from the exact velocity at T_END by %.3e relative" % rel)
    pk = float(np.max(omega_exact(np.array([0.0]), np.array([0.0]), T_END)))
    if abs(pk - omega_peak_exact()) > 1e-14:
        refuse("omega_peak_exact disagrees with omega_exact at the origin")
    return dict(control="symbolic_substitution_vorticity_transport_curl_continuity_radial_momentum",
                residuals=dict((k, str(v)) for k, v in res.items()), far_field_datum_rel_error=float(rel),
                omega_peak_T=pk, passed=True)


def control_substitution_is_able_to_fail():
    sp, x, y, t, nu, G, T0s = _sym()
    tp = sp.Rational(11, 10) * (t + T0s)                                 # PLANT: 1.1 t'
    r2 = x ** 2 + y ** 2
    w = G / (4 * sp.pi * nu * (t + T0s)) * sp.exp(-r2 / (4 * nu * tp))
    res = sp.simplify(sp.diff(w, t) - nu * (sp.diff(w, x, 2) + sp.diff(w, y, 2)))
    if res == 0:
        refuse("PLANTED CONTROL FAILED: t' planted at 1.1 t' still gave zero residual")
    return dict(control="PZ-F22-DECAY_planted_1.1tprime_must_be_nonzero", planted_factor=1.1, residual_is_zero=False, passed=True)


def control_ladder_is_geometrically_similar():
    rh = [h_of(LEVELS[i][1]) / h_of(LEVELS[i + 1][1]) for i in range(2)]
    rt = [dt_of(LEVELS[i][2]) / dt_of(LEVELS[i + 1][2]) for i in range(2)]
    if max(abs(r - 2.0) for r in rh + rt) > 1e-12:
        refuse("the ladder is not a factor-2 refinement in h and dt: %s %s" % (rh, rt))
    for _nm, n, _s in LEVELS:
        if n % 2:
            refuse("N must be even: the vortex centre sits on a vertex, and the peak cells are the four around it")
    far = math.exp(-L ** 2 / (4.0 * NU * (T_END + T0)))
    if far > 1e-10:
        refuse("the far-field datum is not time-independent to round-off: exp(-L^2/(4 nu t'_end)) = %.3e" % far)
    return dict(control="constant_ratio_refinement_h_and_dt_and_far_field_datum", h_ratios=rh, dt_ratios=rt,
                far_field_correction=far, passed=True)


def control_model_is_second_order_and_forced():
    tab = predictions()
    p_e2, p_pk = model_orders()
    for n, st in MODEL_GRIDS:
        row = integrated(n, st)
        if row["r_conv_L2"] <= 0.0 or row["r_diff_L2"] <= 0.0:
            refuse("PLANTED CONTROL FAILED: the stencil evaluator returned a zero truncation residual on grid %d^2" % n)
    if not (1.7 <= p_e2 <= 2.3 and 1.7 <= p_pk <= 2.3):
        refuse("the model's predicted errors do not scale as h^2: orders E2 %.3f, peak vorticity %.3f" % (p_e2, p_pk))
    pk = [row["peak_err_pred"] for row in tab]
    if not (np.sign(pk[0]) == np.sign(pk[1]) == np.sign(pk[2])):
        refuse("the model's predicted peak-vorticity error changes sign across the ladder %s" % pk)
    if max(r["courant"] for r in tab) > 0.5:
        refuse("Courant number above 0.5 at some level")
    return dict(control="model_forced_and_second_order", model_orders=dict(E2=p_e2, peak_vorticity=p_pk),
                peak_err_pred=pk, passed=True)


def selftest_predicate(controls):
    if len(controls) != 4:
        return False, "expected 4 controls, ran %d" % len(controls)
    for c in controls:
        if not c.get("passed"):
            return False, "control %s did not pass" % c.get("control")
    if not __debug__:
        return False, "running under -O"
    return True, ("4 controls green: the vorticity satisfies the transport equation, the velocity induces it and is "
                  "divergence-free, the closed-form pressure balances the radial momentum, all under symbolic "
                  "substitution; t' planted at 1.1 t' makes the residual non-zero; h and dt refine by exactly 2 with a "
                  "far-field datum exact to round-off; the discretisation model is forced by a non-zero residual and "
                  "scales as h^2 with a sign-stable peak-vorticity error")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    controls = [control_symbolic_substitution(), control_substitution_is_able_to_fail(),
                control_ladder_is_geometrically_similar(), control_model_is_second_order_and_forced()]
    tab = predictions()
    if a.json:
        print(json.dumps(dict(constants=dict(Gamma=GAMMA, nu=NU, T0=T0, L=L, T_END=T_END, U_ref=U_REF, r_c0=R_C0),
                              levels=tab, omega_peak_exact_T=omega_peak_exact(), controls=controls), indent=2))
        return 0
    ok, why = selftest_predicate(controls)
    if a.selftest:
        print(json.dumps(dict(controls=controls, levels=tab, omega_peak_exact_T=omega_peak_exact(),
                              predicate=dict(ok=ok, why=why)), indent=2))
        if not ok:
            refuse("SELFTEST DID NOT ESTABLISH ITS CLAIM: %s" % why)
        print("\nSELFTEST GREEN -- %s" % why)
        return 0
    print("Gamma=%g nu=%g T0=%g L=%g T=%g U_ref=%.6f r_c0=%.4f  omega_peak_exact(T)=%.15f" % (GAMMA, NU, T0, L, T_END, U_REF, R_C0, omega_peak_exact()))
    for r in tab:
        print("%-7s %dx%d steps=%d h=%.5g dt=%.5g Co=%.3f  E2_pred=%.6e  peak_err_pred=%.6e  [%s]"
              % (r["name"], r["n"], r["n"], r["steps"], r["h"], r["dt"], r["courant"], r["E2_pred"], r["peak_err_pred"], r["source"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
