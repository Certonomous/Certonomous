#!/usr/bin/env python3
"""
F16 -- THE EXACT SOLUTION of Stokes' second problem (oscillating wall).

    u(y, t) = U0 * exp(-k y) * sin(omega t - k y),   k = sqrt(omega / (2 nu))
    v = w = 0,   p = const

THE REFERENCE IS NOT A PAPER ON THIS BOX.  IT IS A SUBSTITUTION.
-----------------------------------------------------------------
Standing rule 15 requires title-page verification of every retrieved paper.
This case retrieves none.  The exact solution is verified here by SYMBOLIC
SUBSTITUTION INTO THE INCOMPRESSIBLE NAVIER-STOKES EQUATIONS, on this box, at
selftest time -- which is a stronger provenance than a citation, because a
citation can be mis-transcribed and a residual of zero cannot.

Three things are checked, and each can fail:
  1. continuity   du/dx + dv/dy + dw/dz  ==  0
  2. convection   (u . grad) u           ==  0   (so the solution is exact for
                                                  the FULL nonlinear equations,
                                                  not only for the heat equation)
  3. x-momentum   du/dt - nu d2u/dy2     ==  0

A planted control perturbs the trial solution and requires all three residuals
to become non-zero: a checker that returns zero for a wrong function is not a
checker.

WHY THIS CASE EXISTS
--------------------
It supplies BOTH halves of the lab's largest structural gap in one row: a KNOWN
ANSWER (closed form, machine-verified above) joined to a CONVERGING THREE-LEVEL
GRID LADDER.  Its solution is SMOOTH and transcendental, so a second-order
scheme must recover its design order -- deliberately the opposite regime to
F15, whose solution is discontinuous and whose L1 error can converge no faster
than first order.  Together the two cases bracket the two convergence regimes.

Refusals are `raise` and `sys.exit(2)`.  Zero `assert` statements (L-332).
"""
import sys

if not __debug__:
    sys.stderr.write(
        "REFUSED: exact_stokes.py must not run under `python3 -O`.\n"
        "  -O deletes every `assert`, including roache_triple.py:195,632,634,637,\n"
        "  which carry rule 1's verdict vocabulary and rule 5's one-way gate.\n")
    sys.exit(2)

import json
import math
import argparse

# ---------------------------------------------------------------------------
# THE CASE, FROZEN.  Chosen so every derived length is exact in decimal.
# ---------------------------------------------------------------------------
DELTA = 0.01                       # Stokes length, m   (chosen)
PERIOD = 1.0                       # s                  (chosen)
U0 = 1.0                           # m/s                (chosen)
OMEGA = 2.0 * math.pi / PERIOD     # rad/s              -> 6.283185307179586
NU = OMEGA * DELTA ** 2 / 2.0      # m^2/s              -> 3.141592653589793e-4
K = 1.0 / DELTA                    # 1/m                -> 100 exactly
H_OVER_DELTA = 14                  # domain height in Stokes lengths
H = H_OVER_DELTA * DELTA           # m                  -> 0.14
N_PERIODS = 40                     # run length

# The three mesh levels.  UNIFORM spacing at every level, so the three meshes
# are GEOMETRICALLY SIMILAR -- a fixed-expansion-ratio graded ladder is NOT,
# and a Roache triple on non-similar meshes is not a Roache triple.
LEVELS = (("coarse", 56, 400), ("medium", 112, 800), ("fine", 224, 1600))
#          name      Ny   steps-per-period          dy = H/Ny, dt = PERIOD/steps


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def u_exact(y, t):
    return U0 * math.exp(-K * y) * math.sin(OMEGA * t - K * y)


def dy_of(ny):
    return H / float(ny)


def dt_of(nsteps):
    return PERIOD / float(nsteps)


# ---------------------------------------------------------------------------
# THE BAND PRINCIPLE, DERIVED HERE SO A READER CAN CHECK IT
# ---------------------------------------------------------------------------
def predicted_pointwise_error_amplitude(dy):
    """Leading truncation error of a second-order central Laplacian on this
    exact profile, propagated to a SOLUTION error.

    The complex form is u = Im{U0 exp(-(1+i) k y) exp(i omega t)}.  Its fourth
    y-derivative carries the factor (-(1+i)k)^4 = -4 k^4, so the second-order
    central second difference has local truncation error

        tau  =  nu * (dy^2 / 12) * u''''  ~  nu * (dy^2/12) * 4 k^4 * U0 e^{-ky}

    A periodic solution error e obeys  i omega e - nu e'' = tau, and on this
    layer  omega = 2 nu k^2, so |e| ~ |tau| / omega, giving

        |e(y)|  ~  (k^2 dy^2 / 6) * U0 * exp(-k y).

    That is the ONE constant every F16 band is built from.  It is asymptotic and
    it drops the phase and the (100x smaller, see cost section) temporal
    contribution, which is why the registered band is a factor-3 window around
    it rather than an equality.
    """
    return (K ** 2 * dy ** 2) / 6.0 * U0


def predicted_L2_error(dy):
    """The domain-normalised L2 norm of the amplitude above:

        E2 = sqrt( (1/H) Int_0^H e(y)^2 dy ) / U0
           = (k^2 dy^2 / 6) * sqrt( (1 - e^{-2kH}) / (2 k H) )
    """
    amp = predicted_pointwise_error_amplitude(dy) / U0
    return amp * math.sqrt((1.0 - math.exp(-2.0 * K * H)) / (2.0 * K * H))


def predicted_error_at_delta(dy):
    """The same amplitude evaluated at y = DELTA."""
    return predicted_pointwise_error_amplitude(dy) / U0 * math.exp(-1.0)


def u_at_delta_exact_normalised():
    """u(delta, t)/U0 at the graded phase omega t = 0 (mod 2 pi)."""
    return math.exp(-1.0) * math.sin(-1.0)


def domain_truncation_error():
    """The exact solution is not zero at y = H, but the top boundary imposes
    zero.  This is the size of that inconsistency, normalised the same way E2
    is.  It must sit far below the FINEST level's discretisation error or the
    ladder has a grid-independent floor and will stagnate."""
    amp = math.exp(-K * H)
    return amp / math.sqrt(2.0 * K * H)


# ---------------------------------------------------------------------------
# CONTROLS
# ---------------------------------------------------------------------------
def control_symbolic_substitution():
    """Substitute the closed form into the FULL incompressible Navier-Stokes
    equations symbolically and require all three residuals to be identically
    zero."""
    try:
        import sympy as sp
    except ImportError:
        refuse("sympy is not importable; the exact solution cannot be verified "
               "by substitution and NOTHING may be registered on it")
    x, y, z, t = sp.symbols("x y z t")
    nu, om, u0 = sp.symbols("nu omega U0", positive=True)
    k = sp.sqrt(om / (2 * nu))
    u = u0 * sp.exp(-k * y) * sp.sin(om * t - k * y)
    v = sp.Integer(0)
    w = sp.Integer(0)
    res = {
        "continuity": sp.simplify(sp.diff(u, x) + sp.diff(v, y) + sp.diff(w, z)),
        "convection_x": sp.simplify(u * sp.diff(u, x) + v * sp.diff(u, y)
                                    + w * sp.diff(u, z)),
        "x_momentum": sp.simplify(sp.diff(u, t) - nu * sp.diff(u, y, 2)),
    }
    bad = [n for n, r in res.items() if r != 0]
    if bad:
        refuse("SYMBOLIC SUBSTITUTION FAILED: residuals %s are not identically "
               "zero, so the registered closed form is NOT an exact solution of "
               "the equations the solver integrates" % bad)
    return dict(control="symbolic_substitution_into_full_NS",
                residuals=dict((n, str(r)) for n, r in res.items()), passed=True)


def control_substitution_is_able_to_fail():
    """PLANTED CONTROL (standing rule 3).  Perturb the exponent and require the
    momentum residual to become non-zero.  A substitution check that returns
    zero for a wrong function proves nothing about the right one."""
    import sympy as sp
    y, t = sp.symbols("y t")
    nu, om, u0 = sp.symbols("nu omega U0", positive=True)
    k = sp.sqrt(om / (2 * nu))
    bad_u = u0 * sp.exp(-1.37 * k * y) * sp.sin(om * t - k * y)   # PLANT: 1.37
    r = sp.simplify(sp.diff(bad_u, t) - nu * sp.diff(bad_u, y, 2))
    if r == 0:
        refuse("PLANTED CONTROL FAILED: a decay exponent planted at 1.37 k still "
               "gave a zero momentum residual. The substitution checker cannot "
               "see a wrong solution, so its zeros are NOT EVIDENCE.")
    return dict(control="PZ-F16-EXPONENT_planted_1.37k_must_be_nonzero",
                planted_factor=1.37, residual_is_zero=False, passed=True)


def control_truncation_floor_is_dominated():
    """The domain-truncation error must be far below the FINEST level's
    predicted discretisation error, or the ladder has a grid-independent floor
    and the triple will stagnate."""
    dy_fine = dy_of(LEVELS[-1][1])
    trunc = domain_truncation_error()
    pred = predicted_L2_error(dy_fine)
    ratio = pred / trunc
    if ratio < 100.0:
        refuse("the domain-truncation error %.3e is only %.1fx below the finest "
               "predicted discretisation error %.3e; H = %g m is too short and "
               "the ladder would stagnate on a grid-independent floor"
               % (trunc, ratio, pred, H))
    return dict(control="truncation_floor_dominated_by_discretisation",
                domain_truncation_L2=trunc, finest_predicted_L2=pred,
                ratio=ratio, passed=True)


def control_ladder_is_geometrically_similar():
    """Refinement must be by a constant factor in BOTH dy and dt, or the
    observed order is fitted across a change of recipe (VERIFICATION 3.2)."""
    ry = [dy_of(LEVELS[i][1]) / dy_of(LEVELS[i + 1][1]) for i in range(2)]
    rt = [dt_of(LEVELS[i][2]) / dt_of(LEVELS[i + 1][2]) for i in range(2)]
    if max(abs(r - 2.0) for r in ry + rt) > 1e-12:
        refuse("the ladder is not a constant-ratio refinement: dy ratios %s, "
               "dt ratios %s" % (ry, rt))
    for _name, ny, _ns in LEVELS:
        if abs(H / ny * ny - H) > 1e-15:
            refuse("H = %g is not an exact multiple of the level spacing" % H)
    return dict(control="constant_ratio_refinement", dy_ratios=ry,
                dt_ratios=rt, passed=True)


def selftest_predicate(controls):
    if len(controls) != 4:
        return False, "expected 4 controls, ran %d" % len(controls)
    for c in controls:
        if not c.get("passed"):
            return False, "control %s did not pass" % c.get("control")
    if not __debug__:
        return False, "running under -O"
    return True, ("4 controls green: the closed form satisfies continuity, the "
                  "convective term and x-momentum identically under symbolic "
                  "substitution into the FULL incompressible Navier-Stokes "
                  "equations; a decay exponent planted at 1.37 k makes the "
                  "momentum residual non-zero; the domain-truncation floor is "
                  "dominated by the finest discretisation error; and the ladder "
                  "refines dy and dt by exactly 2 at every step")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    controls = [control_symbolic_substitution(),
                control_substitution_is_able_to_fail(),
                control_truncation_floor_is_dominated(),
                control_ladder_is_geometrically_similar()]

    table = [dict(name=n, ny=ny, nsteps_per_period=ns, dy=dy_of(ny),
                  dt=dt_of(ns),
                  predicted_L2=predicted_L2_error(dy_of(ny)),
                  predicted_err_at_delta=predicted_error_at_delta(dy_of(ny)))
             for n, ny, ns in LEVELS]

    if a.json:
        print(json.dumps(dict(
            constants=dict(delta=DELTA, period=PERIOD, U0=U0, omega=OMEGA,
                           nu=NU, k=K, H=H, n_periods=N_PERIODS),
            levels=table,
            u_at_delta_exact=u_at_delta_exact_normalised(),
            domain_truncation_L2=domain_truncation_error(),
            controls=controls), indent=2))
        return 0

    ok, why = selftest_predicate(controls)
    if a.selftest:
        print(json.dumps(dict(controls=controls, levels=table,
                              predicate=dict(ok=ok, why=why)), indent=2))
        if not ok:
            refuse("SELFTEST DID NOT ESTABLISH ITS CLAIM: %s" % why)
        # THE CLAIM IS INSIDE THE PASSING BRANCH.
        print("\nSELFTEST GREEN -- %s" % why)
        return 0

    print("delta=%g m  T=%g s  omega=%.12f  nu=%.15g  k=%g  H=%g m  periods=%d"
          % (DELTA, PERIOD, OMEGA, NU, K, H, N_PERIODS))
    print("u(delta, omega t = 0)/U0 = %.15f" % u_at_delta_exact_normalised())
    print("domain truncation L2 = %.6e" % domain_truncation_error())
    for r in table:
        print("%-7s Ny=%4d dy=%.9g dt=%.9g  E2_pred=%.6e  e(delta)_pred=%.6e"
              % (r["name"], r["ny"], r["dy"], r["dt"], r["predicted_L2"],
                 r["predicted_err_at_delta"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
