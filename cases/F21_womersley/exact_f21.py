#!/usr/bin/env python3
"""
F21 -- THE EXACT SOLUTION of pulsatile (Womersley) laminar flow in a 2-D
channel, and the DISCRETISATION-DERIVED error prediction every F21 band is
built from.

    channel  y in [-H, H], walls no-slip; x in [0, LX] cyclic (the solution is
             x-invariant, so any x-variation the solver produces is error)
    drive    uniform body force  f(t) = A cos(omega t)  in x  (= -dp/dx)
    exact    u(y, t) = Re[ (A / (i omega)) (1 - cosh(k y) / cosh(k H)) e^{i omega t} ],
             k = sqrt(i omega / nu),   v = 0,   p = const
    Womersley number  alpha = H sqrt(omega / nu) = 5 EXACTLY (nu = 2 pi / 25, omega = 2 pi)

THE REFERENCE IS NOT A PAPER ON THIS BOX.  IT IS A SUBSTITUTION.  The closed
form is substituted symbolically into the unsteady x-momentum equation
(u_t = nu u_yy + A cos(omega t); the convective term is identically zero for
an x-invariant field and continuity is trivially satisfied by v = 0); a planted
control (k -> 1.1 k) must make the residual non-zero.  The same residual is
also evaluated numerically at random points.

THE BAND PRINCIPLE -- derived from the discretisation, not measured.  The flow
is linear and one-dimensional, so the solver's own discretisation reduces
EXACTLY to a 1-D finite-volume heat equation: cell-centred second-order
Laplacian with the no-slip face gradient (u_P - 0)/(h/2) at the walls, the
`backward` (BDF2) time derivative with OpenFOAM's Euler-implicit first step,
and the explicit cosine source evaluated at the new time level.  The PISO
pressure correction is identically zero on an x-invariant field (p = const), so
the discrete solution below IS the solver's discrete solution up to solver
tolerances, the preservation of x-invariance and round-off.  The model is
solved on the two coarse ladder levels and extrapolated to the fine level with
its own observed order (a control requires it in [1.7, 2.3]); the direct fine
solve is also computed and must agree with the extrapolation to 10 %
(cross-check; the REGISTERED prediction is the extrapolated one).  A FACTOR-3
window, declared before compute, covers the omissions (tolerances, the
x-invariance the solver must keep, PIMPLE's momentum predictor being solved
before the source is re-evaluated).

Refusals are `raise` and `sys.exit(2)`.  Zero `assert` (L-332).
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: exact_f21.py must not run under `python3 -O`.\n")
    sys.exit(2)

import json
import math
import argparse

import numpy as np

# ---------------------------------------------------------------------------
# THE CASE, FROZEN.
# ---------------------------------------------------------------------------
H = 1.0                                 # channel half-height
LX = 2.0                                # cyclic streamwise length (= 2H: square cells at N x N)
OMEGA = 2.0 * math.pi                   # drive angular frequency: PERIOD = 1
PERIOD = 2.0 * math.pi / OMEGA
A_DRIVE = 1.0                           # body-force amplitude (kinematic), = -dp/dx amplitude
ALPHA = 5.0                             # Womersley number, EXACT by construction of NU
NU = OMEGA * H ** 2 / ALPHA ** 2        # = 2 pi / 25 = 0.25132741228718347
U_REF = A_DRIVE / OMEGA                 # the Womersley velocity scale A/omega, the normaliser
N_PERIODS = 12                          # full periods of transient decay before the locked phase
PHASE_DEG = 90.0                        # locked phase: t_end = 12 T + T/4, where the centreline velocity peaks
                                        # (phase 0 was scanned and REJECTED at registration: the centreline
                                        # error there is a cancellation whose model order is 3.6 / 7.8 -- the
                                        # F19 lesson; at 90 deg the model orders are 2.00 / 2.00)
T_END = (N_PERIODS + PHASE_DEG / 360.0) * PERIOD     # = 12.25
STEPS_PER_PERIOD = dict(coarse=96, medium=192, fine=384)
PROBE = (LX / 2.0, 0.0)                 # G-F21-2: centreline probe (x, y)
# name, N (cells per direction: N x N over LX x 2H, square cells), steps to T_END (dt = T_END/steps)
LEVELS = (("coarse", 128, 1176), ("medium", 256, 2352), ("fine", 512, 4704))   # steps = 12.25 x 96 x N/128
MODEL_GRIDS = ((128, 1176), (256, 2352))    # solved; the fine level is extrapolated (and cross-checked)
K_COMPLEX = complex(0.0, OMEGA / NU) ** 0.5   # sqrt(i omega / nu), principal root


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def h_of(n):
    return 2.0 * H / float(n)


def dt_of(steps):
    return T_END / float(steps)


def u_exact(x, y, t, k=K_COMPLEX):
    """x is accepted for signature uniformity and ignored: the field is x-invariant."""
    y = np.asarray(y, dtype=float)
    prof = (A_DRIVE / (1j * OMEGA)) * (1.0 - np.cosh(k * y) / np.cosh(k * H)) * np.exp(1j * OMEGA * t)
    return np.real(prof) + 0.0 * np.asarray(x, dtype=float)


def v_exact(x, y, t):
    return np.zeros(np.broadcast(np.asarray(x), np.asarray(y)).shape)


def u_probe_exact(t=T_END):
    return float(u_exact(PROBE[0], PROBE[1], t) / U_REF)


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


def centres(n):
    h = h_of(n)
    xg = (np.arange(n) + 0.5) * h
    yg = -H + (np.arange(n) + 0.5) * h
    return h, xg, yg


# ---------------------------------------------------------------------------
# THE DISCRETE MODEL -- the solver's own 1-D discretisation, solved directly
# ---------------------------------------------------------------------------
def discrete_solution(n, steps, wall_coeff=3.0):
    """Cell-centred FV in y (n cells over 2H), no-slip walls, BDF2 with an
    Euler-implicit first step (OpenFOAM `backward`), cosine source at the new
    time level.  `wall_coeff` = 3 is the no-slip stencil (u_N - 3 u_P)/h^2 at
    a wall cell; the planted control passes 2 (a zero-gradient wall)."""
    from scipy.linalg import solve_banded
    h, _xg, yg = centres(n)
    dt = dt_of(steps)
    diag = np.full(n, -2.0); diag[0] = diag[-1] = -wall_coeff
    off = np.ones(n - 1)
    u_prev = None
    u = u_exact(0.0, yg, 0.0)
    u_at_prev_period = None
    spp = steps / (T_END / PERIOD)
    if abs(spp - round(spp)) > 1e-9:
        refuse("steps %d is not an integer number of steps per period at T_END = %g" % (steps, T_END))
    idx_prev_period = steps - int(round(spp))          # t = T_END - PERIOD
    for k in range(steps):
        t1 = (k + 1) * dt
        if k == 0:
            c, rhs = 1.0 / dt, u / dt + A_DRIVE * math.cos(OMEGA * t1)
        else:
            c, rhs = 1.5 / dt, (2.0 * u - 0.5 * u_prev) / dt + A_DRIVE * math.cos(OMEGA * t1)
        ab = np.zeros((3, n))
        ab[0, 1:] = -NU * off / h ** 2
        ab[1, :] = c - NU * diag / h ** 2
        ab[2, :-1] = -NU * off / h ** 2
        u_new = solve_banded((1, 1), ab, rhs)
        u_prev, u = u, u_new
        if k + 1 == idx_prev_period:
            u_at_prev_period = u.copy()
    if u_at_prev_period is None:
        refuse("model never reached t = (N_PERIODS - 1) T")
    eu = u - u_exact(0.0, yg, T_END)
    e2 = float(math.sqrt(np.mean(eu ** 2)) / U_REF)
    j = n // 2
    probe_err = float(0.5 * (eu[j - 1] + eu[j]) / U_REF)    # bilinear at y = 0 of an x-invariant field
    period_change = float(math.sqrt(np.mean((u - u_at_prev_period) ** 2)) / U_REF)
    return dict(n=n, steps=steps, h=h, dt=dt, yg=yg, u_model=u, eu=eu, E2_pred=e2, probe_err_pred=probe_err,
                period_change_pred=period_change, courant=float(np.max(np.abs(u)) * dt / h))


_CACHE = {}


def solved(n, steps):
    if (n, steps) not in MODEL_GRIDS:
        refuse("grid %d x %d steps is not solved by the model; it is extrapolated" % (n, steps))
    if (n, steps) not in _CACHE:
        _CACHE[(n, steps)] = discrete_solution(n, steps)
    return _CACHE[(n, steps)]


def model_orders():
    a, b = solved(*MODEL_GRIDS[0]), solved(*MODEL_GRIDS[1])
    r = math.log(a["h"] / b["h"])
    return (math.log(a["E2_pred"] / b["E2_pred"]) / r,
            math.log(abs(a["probe_err_pred"]) / abs(b["probe_err_pred"])) / r)


def predictions():
    """Solved where the ladder grid is a MODEL_GRID; otherwise extrapolated
    from the finest solved grid with the model's own orders."""
    if "table" not in _CACHE:
        ref = solved(*MODEL_GRIDS[-1])
        p_e2, p_pr = model_orders()
        tab = []
        for nm, n, s in LEVELS:
            if (n, s) in MODEL_GRIDS:
                m = solved(n, s)
                tab.append(dict(name=nm, n=n, cells=n * n, steps=s, h=m["h"], dt=m["dt"], E2_pred=m["E2_pred"],
                                probe_err_pred=m["probe_err_pred"], period_change_pred=m["period_change_pred"],
                                courant=m["courant"], source="solved"))
            else:
                f = h_of(n) / ref["h"]
                tab.append(dict(name=nm, n=n, cells=n * n, steps=s, h=h_of(n), dt=dt_of(s),
                                E2_pred=ref["E2_pred"] * f ** p_e2, probe_err_pred=ref["probe_err_pred"] * f ** p_pr,
                                period_change_pred=ref["period_change_pred"] * f ** p_e2, courant=ref["courant"],
                                source="extrapolated from %d x %d steps with model orders %.4f (E2), %.4f (probe)"
                                       % (ref["n"], ref["steps"], p_e2, p_pr)))
        _CACHE["table"] = tab
    return _CACHE["table"]


# ---------------------------------------------------------------------------
# CONTROLS
# ---------------------------------------------------------------------------
def control_symbolic_substitution():
    try:
        import sympy as sp
    except ImportError:
        refuse("sympy is not importable; the exact solution cannot be verified by substitution")
    y, t = sp.symbols("y t", real=True)
    k = sp.symbols("k")
    nu, w, A, Hs = sp.symbols("nu omega A H", positive=True)
    U = (A / (sp.I * w)) * (1 - sp.cosh(k * y) / sp.cosh(k * Hs)) * sp.exp(sp.I * w * t)
    R = sp.diff(U, t) - nu * sp.diff(U, y, 2) - A * sp.exp(sp.I * w * t)
    R = sp.simplify(sp.expand(R).subs(k ** 2, sp.I * w / nu))
    if R != 0:
        refuse("SYMBOLIC SUBSTITUTION FAILED: x-momentum residual %s is not identically zero" % R)
    # numeric residual of the REAL solution at random points (complex-step-free: analytic derivatives)
    rng = np.random.RandomState(21)
    ys, ts = rng.uniform(-H, H, 200), rng.uniform(0, T_END, 200)
    kk = K_COMPLEX
    prof = lambda yy: (A_DRIVE / (1j * OMEGA)) * (1.0 - np.cosh(kk * yy) / np.cosh(kk * H))
    ut = np.real(1j * OMEGA * prof(ys) * np.exp(1j * OMEGA * ts))
    uyy = np.real((A_DRIVE / (1j * OMEGA)) * (-kk ** 2 * np.cosh(kk * ys) / np.cosh(kk * H)) * np.exp(1j * OMEGA * ts))
    res = ut - NU * uyy - A_DRIVE * np.cos(OMEGA * ts)
    if np.max(np.abs(res)) > 1e-12:
        refuse("NUMERIC RESIDUAL of the exact solution is %.3e, not round-off" % np.max(np.abs(res)))
    wall = np.max(np.abs(u_exact(0.0, np.array([-H, H]), ts[:5, None])))
    if wall > 1e-14:
        refuse("the exact solution does not vanish at the walls: %.3e" % wall)
    if abs(H * math.sqrt(OMEGA / NU) - ALPHA) > 1e-12:
        refuse("Womersley number is not %g" % ALPHA)
    return dict(control="symbolic_substitution_into_unsteady_x_momentum", residual=str(R),
                numeric_residual_max=float(np.max(np.abs(res))), wall_value_max=float(wall), alpha=ALPHA, passed=True)


def control_substitution_is_able_to_fail():
    import sympy as sp
    y, t = sp.symbols("y t", real=True)
    k = sp.symbols("k")
    nu, w, A, Hs = sp.symbols("nu omega A H", positive=True)
    kp = sp.Rational(11, 10) * k                                   # PLANT: 1.1 k
    U = (A / (sp.I * w)) * (1 - sp.cosh(kp * y) / sp.cosh(kp * Hs)) * sp.exp(sp.I * w * t)
    R = sp.simplify(sp.expand(sp.diff(U, t) - nu * sp.diff(U, y, 2) - A * sp.exp(sp.I * w * t)).subs(k ** 2, sp.I * w / nu))
    if R == 0:
        refuse("PLANTED CONTROL FAILED: k planted at 1.1 k still gave zero residual")
    return dict(control="PZ-F21-K_planted_1.1k_must_be_nonzero", planted_factor=1.1, residual_is_zero=False, passed=True)


def control_ladder_is_geometrically_similar():
    rh = [h_of(LEVELS[i][1]) / h_of(LEVELS[i + 1][1]) for i in range(2)]
    rt = [dt_of(LEVELS[i][2]) / dt_of(LEVELS[i + 1][2]) for i in range(2)]
    if max(abs(r - 2.0) for r in rh + rt) > 1e-12:
        refuse("the ladder is not a factor-2 refinement in h and dt: %s %s" % (rh, rt))
    if abs(LX / (2.0 * H) - 1.0) > 1e-15:
        refuse("cells are not square: LX/(2H) = %g" % (LX / (2.0 * H)))
    for nm, n, s in LEVELS:
        if n % 2 or abs(s - T_END / PERIOD * STEPS_PER_PERIOD[nm]) > 1e-9:
            refuse("level %s %d x %d: N must be even (probe straddles y = 0) and steps = T_END/T x %d"
                   % (nm, n, s, STEPS_PER_PERIOD[nm]))
    if abs(T_END - 12.25) > 1e-12:
        refuse("T_END is not the registered 12.25")
    return dict(control="constant_ratio_refinement_h_and_dt", h_ratios=rh, dt_ratios=rt, passed=True)


def control_model_is_second_order_and_sensitive():
    p_e2, p_pr = model_orders()
    if not (1.7 <= p_e2 <= 2.3 and 1.7 <= p_pr <= 2.3):
        refuse("the model's predicted errors do not scale as h^2 between the solved grids: "
               "orders %.3f (E2), %.3f (probe)" % (p_e2, p_pr))
    fine = dict((r["name"], r) for r in predictions())["fine"]
    direct = discrete_solution(fine["n"], fine["steps"])
    ratio = fine["E2_pred"] / direct["E2_pred"]
    if not (0.9 <= ratio <= 1.1):
        refuse("the fine-level extrapolation (%.6e) disagrees with the direct fine solve (%.6e) by more than 10 %%"
               % (fine["E2_pred"], direct["E2_pred"]))
    n, s = MODEL_GRIDS[0]
    planted = discrete_solution(n, s, wall_coeff=2.0)
    if planted["E2_pred"] < 10.0 * solved(n, s)["E2_pred"]:
        refuse("PLANTED CONTROL FAILED: a zero-gradient wall stencil did not move the model's E2 by 10x "
               "(%.3e vs %.3e); the model is not reading its own wall discretisation"
               % (planted["E2_pred"], solved(n, s)["E2_pred"]))
    if max(r["courant"] for r in predictions()) > 0.5:
        refuse("Courant number above 0.5 at some level")
    return dict(control="model_second_order_between_solved_grids_extrapolation_crosschecked_and_wall_stencil_planted",
                model_orders=dict(E2=p_e2, probe=p_pr), fine_extrapolated_E2=fine["E2_pred"],
                fine_direct_E2=direct["E2_pred"], fine_direct_probe_err=direct["probe_err_pred"],
                fine_direct_period_change=direct["period_change_pred"], extrapolation_over_direct=ratio,
                planted_wall_E2=planted["E2_pred"], passed=True)


def selftest_predicate(controls):
    if len(controls) != 4:
        return False, "expected 4 controls, ran %d" % len(controls)
    for c in controls:
        if not c.get("passed"):
            return False, "control %s did not pass" % c.get("control")
    if not __debug__:
        return False, "running under -O"
    return True, ("4 controls green: the closed form satisfies the unsteady x-momentum equation identically "
                  "under symbolic substitution and to round-off numerically, vanishes at the walls, and has "
                  "alpha = 5; k planted at 1.1 k makes the residual non-zero; h and dt refine by exactly 2; "
                  "the discrete model is second order, its fine extrapolation agrees with the direct fine "
                  "solve to 10 %, and it sees a planted wall-stencil defect")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    controls = [control_symbolic_substitution(), control_substitution_is_able_to_fail(),
                control_ladder_is_geometrically_similar(), control_model_is_second_order_and_sensitive()]
    tab = predictions()
    if a.json:
        print(json.dumps(dict(constants=dict(nu=NU, omega=OMEGA, alpha=ALPHA, H=H, LX=LX, A=A_DRIVE, U_ref=U_REF,
                                             T_END=T_END), levels=tab, u_probe_exact_T=u_probe_exact(),
                              controls=controls), indent=2))
        return 0
    ok, why = selftest_predicate(controls)
    if a.selftest:
        print(json.dumps(dict(controls=controls, levels=tab, u_probe_exact_T=u_probe_exact(),
                              predicate=dict(ok=ok, why=why)), indent=2))
        if not ok:
            refuse("SELFTEST DID NOT ESTABLISH ITS CLAIM: %s" % why)
        print("\nSELFTEST GREEN -- %s" % why)
        return 0
    print("nu=%.17g omega=%.17g alpha=%g H=%g LX=%g A=%g U_ref=%.17g T_END=%g  u_probe_exact(T)/U_ref=%.15f"
          % (NU, OMEGA, ALPHA, H, LX, A_DRIVE, U_REF, T_END, u_probe_exact()))
    for r in tab:
        print("%-7s %dx%d steps=%d h=%.5g dt=%.5g Co=%.3f  E2_pred=%.6e  probe_err_pred=%.6e  period_change=%.3e  [%s]"
              % (r["name"], r["n"], r["n"], r["steps"], r["h"], r["dt"], r["courant"], r["E2_pred"],
                 r["probe_err_pred"], r["period_change_pred"], r["source"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
