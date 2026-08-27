#!/usr/bin/env python3
"""T16 analytic referent: fully developed laminar MIXED CONVECTION between
vertical parallel plates with ASYMMETRIC isothermal walls (Aung & Worku 1986),
DERIVED HERE from the Boussinesq equations, never transcribed from a table.

Geometry: gap b in x, flow upward in z, gravity (0 0 -g).  Hot wall at x = 0
(T_h), cold wall at x = b (T_c).  Y = x/b, U = w/U0 with U0 the MEAN velocity,
theta = (T - T_c)/(T_h - T_c), and the single mixed-convection group

    G = Gr/Re = g beta (T_h - T_c) b^2 / (nu U0),
    Gr = g beta (T_h - T_c) b^3 / nu^2,   Re = U0 b / nu.

ENERGY.  Fully developed means no z dependence, so w dT/dz = alpha T'' reduces
to T'' = 0: theta(Y) = 1 - Y, LINEAR, and -- the fact this rung leans on --
a linear T with dT/dz = 0 satisfies the energy equation for ANY w(x), so the
temperature field is exact everywhere in the channel, entrance region included.

MOMENTUM.  0 = -dp/dz + mu w'' + rho g beta (T - T_c) gives, nondimensionally,
    U'' + G theta(Y) + P = 0,   P = -(b^2/(mu U0)) dp/dz,
    U(0) = U(1) = 0,  integral_0^1 U dY = 1 (U0 IS the mean).
Solving:  P = 12 - G/2  and

    U(Y) = 6 Y (1 - Y) - (G/12) Y (1 - Y) (2Y - 1)
         = Y (1 - Y) [ 6 - (G/12)(2Y - 1) ].

Wall shear:  U'(0) = 6 + G/12,  -U'(1) = 6 - G/12, so the ASYMMETRY RATIO is
    tau_hot / tau_cold = (6 + G/12) / (6 - G/12),
and FLOW REVERSAL at the cold wall begins at G = 72 (Aung & Worku's criterion).

THE REGISTERED POINT IS G = 48, two thirds of the reversal threshold, where the
closed form collapses to U(Y) = 10 Y - 18 Y^2 + 8 Y^3 and

    U(0.25) = 1.5 exactly      U(0.75) = 0.75 exactly
    tau_hot/tau_cold = 5 exactly    integral U dY = 1 exactly
    Y_max = (36 - sqrt(336))/48

THIS MODULE REFUSES IF THE CLOSED FORM DOES NOT REPRODUCE THOSE VALUES.

ROUTE B (verify(); every failure is sys.exit(2)):
 (B1) the closed form satisfies U'' + G theta + P = 0 -- centred-difference
      residuals at two stencil widths, and the differences are EXACT on a cubic
      so the residual must sit at round-off at BOTH widths;
 (B2) the boundary conditions and the mass constraint: U(0) = U(1) = 0 and
      Simpson's rule over the profile returns 1, to 1e-14;
 (B3) THE TABULATED VALUES: U(0.25) = 1.5, U(0.75) = 0.75,
      tau_hot/tau_cold = 5, all to 1e-13, and Y_max against the closed-form root
      of the quadratic 24Y^2 - 36Y + 10;
 (B4) INDEPENDENT NUMERICAL ROUTE: RK4 SHOOTING on y1' = y2, y2' = -(P+G theta),
      shooting on U'(0) for U(1) = 0.  The right-hand side is LINEAR in Y, so
      RK4 is exact to round-off on the cubic and the route is held to 1e-12 in
      both the profile and the mass constraint;
 (B4b) THE BAND MODEL IS SECOND ORDER AND CONVERGES ON THE CLOSED FORM: the
      tridiagonal finite-volume model that `discrete_expectation` uses to GROUND
      the pre-registered bands is run at N = 250/500/1000; its G1 error must
      fall at ratio ~4 per halving of h (required in [3.5, 4.5]) and Richardson-
      extrapolate onto the closed form to better than 1e-9.  This is what
      entitles the discrete model to set a band;
 (B5) PLANTED MUTATION: G perturbed by 1 percent is REFUSED by B3.

THREE REPAIRS, 2026-08-27, DISCLOSED IN FULL IN `T16_PREREGISTRATION.md` §9.
This module was found UNTRACKED on disk, left by a lane that was killed before
it registered anything.  It was read in full, its derivation was re-derived
independently line by line, and it FAILED its own Route B (`--selftest` rc 1).
Three defects were repaired BEFORE the freeze, while nothing was frozen and no
solver had run:
  R1  `dUdY` carried a MINUS on the (G/12) group, giving U'(0) = 6 - G/12 = 2
      instead of 6 + G/12 = 10 -- it SWAPPED THE TWO WALLS and put the steeper
      shear at the COLD wall, which is the wrong physics.
  R2  `Y_max` built its quadratic from R1's wrong derivative and returned
      0.6319 (peak displaced toward the COLD wall) instead of 0.3681 (peak
      toward the HOT wall).  Its own docstring's quadratic 24Y^2-36Y+10 was
      right; only the code disagreed with it.
  R3  B4 compared the SECOND-ORDER finite-volume model against the closed form
      at a 1e-9 tolerance that is unreachable by construction (the truncation
      error at N = 2000 is ~1e-7), so `verify()` refused every call it was ever
      given.  B4 is now the RK4 route; the FV model's convergence became B4b.
The independent confirmation that R1/R2 are right, and not merely different:
after the repair the DISCRETE model's own Y_max error falls 1.250e-03 ->
3.125e-04 -> 7.812e-05 at N = 20/40/80, i.e. exactly h^2 onto the repaired
reference; against the as-found reference it sat at a constant -2.64e-01 and
converged onto nothing.

`discrete_expectation(N)` returns what the SAME finite-volume discretisation the
solver uses (half-cell wall treatment, cell-centred, mass-constrained) predicts
for each graded row at N cells -- the bands in the pre-registration are derived
from it, exactly as T13's were.

NO `assert` STATEMENT IN THIS FILE (L-332).  Every refusal is sys.exit(2).
Exit: 0 verified, 2 REFUSAL.
"""
import math
import sys

EXIT_OK, EXIT_REFUSE = 0, 2
G_REG = 48.0                      # the registered mixed-convection group
G_REVERSAL = 72.0                 # flow reversal at the cold wall begins here


def refuse(msg):
    sys.stderr.write("REFUSE: %s\n" % msg)
    sys.exit(EXIT_REFUSE)


# ------------------------------------------------------------ closed form
def theta(Y):
    return 1.0 - Y


def P_of(G):
    return 12.0 - G / 2.0


def U(Y, G=G_REG):
    return Y * (1.0 - Y) * (6.0 - (G / 12.0) * (2.0 * Y - 1.0))


def dUdY(Y, G=G_REG):
    # U(Y) = Y(1-Y)[6 - (G/12)(2Y-1)] = 6Y - 6Y^2 + (G/12)(2Y^3 - 3Y^2 + Y),
    # so dU/dY = 6 - 12Y + (G/12)(6Y^2 - 6Y + 1).
    # REPAIR R1 (2026-08-27, disclosed in T16_PREREGISTRATION.md section 9): the
    # module as found UNTRACKED on disk carried a MINUS on the (G/12) group.
    # That put U'(0) at 6 - G/12 = 2 instead of 6 + G/12 = 10 and so SWAPPED THE
    # TWO WALLS -- it made the shear steeper at the COLD wall, which is the
    # wrong physics.  Verified against a central difference of U() at
    # Y = 0, 0.25, 0.5, 0.75, 1: +10, +2.5, -2, -3.5, -2.
    return 6.0 - 12.0 * Y + (G / 12.0) * (6.0 * Y * Y - 6.0 * Y + 1.0)


def shear_ratio(G=G_REG):
    lo = 6.0 - G / 12.0
    if lo <= 0.0:
        refuse("G = %g is at or past the flow-reversal threshold %g; the shear ratio is not defined"
               % (G, G_REVERSAL))
    return (6.0 + G / 12.0) / lo


def Y_max(G=G_REG):
    """dU/dY = 0.  At G = 48 this is 24Y^2 - 36Y + 10 = 0, root in (0, 1)."""
    # coefficients of dU/dY = a Y^2 + b Y + c from the REPAIRED derivative; at
    # G = 48 they are 24, -36, +10 -- exactly this docstring's quadratic.
    # REPAIR R2 (2026-08-27): the module as found built them from the R1 sign
    # error and returned the root 0.6319 (peak displaced toward the COLD wall)
    # instead of 0.3681 (peak toward the HOT wall, which is the physics).
    a = (G / 12.0) * 6.0
    b = -12.0 - (G / 12.0) * 6.0
    c = 6.0 + G / 12.0
    if a == 0.0:
        return 0.5
    disc = b * b - 4.0 * a * c
    if disc < 0.0:
        refuse("dU/dY has no real root for G = %g" % G)
    r1 = (-b + math.sqrt(disc)) / (2.0 * a)
    r2 = (-b - math.sqrt(disc)) / (2.0 * a)
    cand = [r for r in (r1, r2) if 0.0 < r < 1.0]
    if len(cand) != 1:
        refuse("dU/dY has %d roots in (0,1) for G = %g: %r" % (len(cand), G, (r1, r2)))
    return cand[0]


def simpson(f, n=20000):
    h = 1.0 / n
    s = f(0.0) + f(1.0)
    for i in range(1, n):
        s += (4.0 if i % 2 else 2.0) * f(i * h)
    return s * h / 3.0


# --------------------------------------- INDEPENDENT ROUTE: RK4 shooting (B4)
def _rk4_march(G, P, s, n):
    """Integrate y1' = y2, y2' = -(P + G theta(Y)) from Y = 0 with y1(0) = 0,
    y2(0) = s.  The right-hand side is LINEAR in Y, so RK4 is exact to
    round-off on the resulting cubic.  Returns the node values of y1."""
    h = 1.0 / n
    y1, y2 = 0.0, s
    out = [0.0]
    for i in range(n):
        Y = i * h

        def f2(t):
            return -(P + G * theta(t))

        k1a, k1b = y2, f2(Y)
        k2a, k2b = y2 + 0.5 * h * k1b, f2(Y + 0.5 * h)
        k3a, k3b = y2 + 0.5 * h * k2b, f2(Y + 0.5 * h)
        k4a, k4b = y2 + h * k3b, f2(Y + h)
        y1 = y1 + (h / 6.0) * (k1a + 2.0 * k2a + 2.0 * k3a + k4a)
        y2 = y2 + (h / 6.0) * (k1b + 2.0 * k2b + 2.0 * k3b + k4b)
        out.append(y1)
    return out


def rk4_shoot(G=G_REG, P=None, n=4000):
    """Shoot for U'(0) so that U(1) = 0, then report the worst node deviation
    from the closed form and |mean - 1| by composite Simpson on the RK4 nodes.
    Returns (worst_dev, mean_dev, s_star)."""
    if P is None:
        P = P_of(G)
    a = _rk4_march(G, P, 0.0, n)[-1]
    b = _rk4_march(G, P, 1.0, n)[-1] - a
    if b == 0.0:
        refuse("the shooting map is degenerate: U(1) does not depend on U'(0)")
    s_star = -a / b
    y = _rk4_march(G, P, s_star, n)
    h = 1.0 / n
    worst = max(abs(y[i] - U(i * h, G)) for i in range(n + 1))
    # composite Simpson over the RK4 nodes (n is even)
    s = y[0] + y[n]
    for i in range(1, n):
        s += (4.0 if i % 2 else 2.0) * y[i]
    mean = s * h / 3.0
    return worst, abs(mean - 1.0), s_star


# ------------------------------------------- the discrete (finite-volume) model
def _tridiag(a, b, c, d):
    n = len(b)
    cp = [0.0] * n
    dp = [0.0] * n
    cp[0] = c[0] / b[0]
    dp[0] = d[0] / b[0]
    for i in range(1, n):
        m = b[i] - a[i] * cp[i - 1]
        cp[i] = c[i] / m if i < n - 1 else 0.0
        dp[i] = (d[i] - a[i] * dp[i - 1]) / m
    x = [0.0] * n
    x[-1] = dp[-1]
    for i in range(n - 2, -1, -1):
        x[i] = dp[i] - cp[i] * x[i + 1]
    return x


def _fv_solve(N, G, P):
    """U'' = -(P + G theta) on cell centres, DIRICHLET 0 at both faces with the
    HALF-CELL wall treatment the finite-volume solver uses."""
    h = 1.0 / N
    a = [1.0] * N
    b = [-2.0] * N
    c = [1.0] * N
    a[0] = 0.0
    b[0] = -3.0
    c[-1] = 0.0
    b[-1] = -3.0
    d = [-(P + G * theta((i + 0.5) * h)) * h * h for i in range(N)]
    return _tridiag(a, b, c, d)


def fv_profile(N, G=G_REG):
    """The discrete profile with the mass constraint mean(U) = 1 satisfied by
    solving for P: the system is linear in P, so two solves suffice."""
    u0 = _fv_solve(N, G, 0.0)
    u1 = _fv_solve(N, G, 1.0)
    m0 = sum(u0) / N
    m1 = sum(u1) / N - m0
    if m1 == 0.0:
        refuse("the discrete system is insensitive to the pressure gradient")
    P = (1.0 - m0) / m1
    u = [u0[i] + P * (u1[i] - u0[i]) for i in range(N)]
    return u, P


def lagrange4(xs, ys, xstar):
    """THE COMPARATOR'S POINT READER, shared with `interp_at` so the band model
    and the graded number come off the SAME interpolation.  `xs` are the cell
    centres of one row and `ys` the values on it; the four centres bracketing
    `xstar` are used."""
    n = len(xs)
    if n < 4:
        refuse("lagrange4 needs at least 4 points, got %d" % n)
    k = 0
    while k < n - 4 and xs[k + 3] < xstar:
        k += 1
    while k > 0 and xs[k + 1] > xstar:
        k -= 1
    return _lagrange4(xs[k:k + 4], ys[k:k + 4], xstar)


def cubic_max_location(xs, ys):
    """THE COMPARATOR'S LOCATION READER: the argmax of the cubic through the
    four cells around the largest value, by bisection on its derivative.  Same
    routine `discrete_expectation` uses, so the pre-registered band for G1b is
    the band of THIS reader and not of an idealised one."""
    n = len(xs)
    if n < 4:
        refuse("cubic_max_location needs at least 4 points, got %d" % n)
    i = max(range(n), key=lambda k: ys[k])
    i = min(max(i, 1), n - 3)
    xs4, ys4 = xs[i - 1:i + 3], ys[i - 1:i + 3]
    lo, hi = xs4[0], xs4[-1]
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        e = 1e-9
        if _lagrange4(xs4, ys4, mid + e) > _lagrange4(xs4, ys4, mid - e):
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# The registered station on the profile and the three closed-form values the
# comparator grades against.  They are COMPUTED here, never typed in.
Y_STAR      = 0.25
U_STAR      = U(Y_STAR)          # 1.5 exactly at G = 48
SHEAR_RATIO = shear_ratio()      # 5   exactly at G = 48
Y_MAX       = Y_max()            # (36 - sqrt(336))/48


def _lagrange4(xs, ys, x):
    s = 0.0
    for i in range(4):
        t = ys[i]
        for j in range(4):
            if j != i:
                t *= (x - xs[j]) / (xs[i] - xs[j])
        s += t
    return s


def interp_at(u, N, Ystar):
    """4-point Lagrange at cell centres -- the comparator's own reader."""
    cs = [(i + 0.5) / N for i in range(N)]
    k = min(max(int(Ystar * N - 1.5), 0), N - 4)
    return _lagrange4(cs[k:k + 4], u[k:k + 4], Ystar)


def discrete_expectation(N, G=G_REG):
    """What the FV discretisation predicts for each graded row at N cells."""
    u, P = fv_profile(N, G)
    h = 1.0 / N
    g1 = interp_at(u, N, 0.25)
    g1b_grid = [(i + 0.5) * h for i in range(N)]
    i = max(range(N), key=lambda k: u[k])
    i = min(max(i, 1), N - 3)
    xs = g1b_grid[i - 1:i + 3]
    ys = u[i - 1:i + 3]
    # the maximum of the cubic through four points, by bisection on its derivative
    lo, hi = xs[0], xs[-1]
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        e = 1e-9
        if _lagrange4(xs, ys, mid + e) > _lagrange4(xs, ys, mid - e):
            lo = mid
        else:
            hi = mid
    g1b = 0.5 * (lo + hi)
    tau_hot = u[0] / (h / 2.0)
    tau_cold = u[-1] / (h / 2.0)
    g3 = tau_hot / tau_cold
    return dict(N=N, P=P, G1=g1, G1_rel_err=(g1 - U(0.25, G)) / U(0.25, G),
                G1b=g1b, G1b_abs_err=g1b - Y_max(G),
                G3=g3, G3_rel_err=(g3 - shear_ratio(G)) / shear_ratio(G))


def discrete_profile(N, G=G_REG):
    """(cell centres, U at them) from the SAME finite-volume model the bands come
    from.  The comparator's selftest forges its synthetic ladder out of this, so
    the forged ladder carries a REAL second-order error law rather than an
    invented one."""
    u, _ = fv_profile(N, G)
    return [(i + 0.5) / N for i in range(N)], u


def selfcheck_readers(G=G_REG):
    """The comparator's two point readers, exercised on the ANALYTIC profile
    sampled at cell centres, where the answer is known exactly.  REFUSES (exit 2)
    if either reader cannot recover the closed form -- a reader that cannot read
    a profile it was handed exactly is not allowed to grade one off a solver."""
    worst_val, worst_loc = 0.0, 0.0
    for N in (20, 40, 80):
        xs = [(i + 0.5) / N for i in range(N)]
        ys = [U(x, G) for x in xs]
        worst_val = max(worst_val, abs(lagrange4(xs, ys, Y_STAR) - U(Y_STAR, G)))
        worst_loc = max(worst_loc, abs(cubic_max_location(xs, ys) - Y_max(G)))
    if worst_val > 1e-12 or worst_loc > 1e-8:
        refuse("reader self-check FAILED on the ANALYTIC profile: worst value error %.3e "
               "(floor 1e-12), worst location error %.3e (floor 1e-8)" % (worst_val, worst_loc))
    print("  reader self-check: on the analytic profile at N = 20/40/80 the 4-point Lagrange "
          "reader recovers U(%.2f) to %.3e and the cubic-max reader recovers Y_max to %.3e "
          "-- both readers are EXACT on a cubic, so every error they report on a solve is the "
          "SOLVE's" % (Y_STAR, worst_val, worst_loc))
    return worst_val, worst_loc


def expectation_table(Ns, G=G_REG):
    """The discrete expectation at each registered level, in the order given.
    `build_t16.py` calls this to GROUND the pre-registered bands, and the
    pre-registration quotes the numbers it returns."""
    return [discrete_expectation(N, G) for N in Ns]


# ------------------------------------------------------------------ ROUTE B
def verify(G=G_REG, quiet=False, mutate_G=1.0):
    fails = []
    say = (lambda *a: None) if quiet else (lambda *a: print(*a))
    Gm = G * mutate_G
    P = P_of(Gm)

    # B1 -- the ODE, by centred differences that are EXACT on a cubic
    worst = 0.0
    for h in (1e-2, 5e-3):
        for Y in (0.1, 0.3, 0.5, 0.7, 0.9):
            r = (U(Y + h, Gm) - 2.0 * U(Y, Gm) + U(Y - h, Gm)) / (h * h) + Gm * theta(Y) + P
            worst = max(worst, abs(r))
    okB1 = worst < 1e-9
    if okB1:
        say("B1 U'' + G theta + P = 0: worst residual %.3e at BOTH stencil widths "
            "(the difference is exact on a cubic) -> PASS" % worst)
    else:
        fails.append("B1 ODE residual %.3e" % worst)

    # B2 -- boundary conditions and the mass constraint
    m = simpson(lambda y: U(y, Gm))
    okB2 = (abs(U(0.0, Gm)) < 1e-15 and abs(U(1.0, Gm)) < 1e-15 and abs(m - 1.0) < 1e-14)
    if okB2:
        say("B2 U(0) = U(1) = 0 and Simpson integral = %.16f (|1 - I| = %.2e) -> PASS" % (m, abs(m - 1.0)))
    else:
        fails.append("B2 BCs/mass (U(0)=%.3e, U(1)=%.3e, I=%.16f)" % (U(0.0, Gm), U(1.0, Gm), m))

    # B3 -- THE TABULATED VALUES, and this module refuses if they do not come back
    tab = ((0.25, 1.5), (0.75, 0.75))
    d = max(abs(U(y, Gm) - v) for y, v in tab)
    sr = shear_ratio(Gm)
    dsr = abs(sr - 5.0)
    ym = Y_max(Gm)
    ym_closed = (36.0 - math.sqrt(336.0)) / 48.0
    dym = abs(ym - ym_closed)
    okB3 = (d < 1e-13 and dsr < 1e-13 and dym < 1e-13)
    if okB3:
        say("B3 tabulated values at G = %g: U(0.25) = %.15f (want 1.5), U(0.75) = %.15f (want 0.75), "
            "tau_hot/tau_cold = %.15f (want 5), Y_max = %.15f (closed root %.15f) -> PASS"
            % (Gm, U(0.25, Gm), U(0.75, Gm), sr, ym, ym_closed))
    else:
        fails.append("B3 tabulated values (worst U dev %.3e, shear-ratio dev %.3e, Y_max dev %.3e)"
                     % (d, dsr, dym))

    # B4 -- an INDEPENDENT numerical route: RK4 SHOOTING on the first-order
    # system.  REPAIR R3 (2026-08-27): the module as found compared the SECOND-
    # ORDER finite-volume model of B4b below against the closed form at a 1e-9
    # tolerance.  That tolerance is unreachable BY CONSTRUCTION -- at N = 2000
    # the FV truncation error is ~1e-7 -- so B4 as found could never pass and
    # verify() refused every call.  RK4 is exact to round-off here because the
    # ODE's right-hand side is LINEAR in Y (the solution is a cubic), so it is a
    # genuinely independent route that can be held to 1e-12.
    du, dm, s_star = rk4_shoot(Gm, P)
    okB4 = (du < 1e-12 and dm < 1e-12)
    if okB4:
        say("B4 INDEPENDENT RK4 shooting route (n = 4000 steps, exact on a cubic): "
            "U'(0) recovered %.15f (closed %.15f), worst |U_rk4 - U_closed| %.3e, "
            "|mean - 1| %.3e -> PASS" % (s_star, dUdY(0.0, Gm), du, dm))
    else:
        fails.append("B4 RK4 route (worst profile dev %.3e, mean dev %.3e)" % (du, dm))

    # B4b -- the FV model that GROUNDS THE BANDS is second-order and converges
    # ON the closed form.  This is the check that entitles discrete_expectation
    # to set a pre-registered band: the error must fall at ratio ~4 per halving
    # of h, and Richardson extrapolation of the two must land on the closed form.
    e = []
    for N in (250, 500, 1000):
        uN, _ = fv_profile(N, Gm)
        e.append(interp_at(uN, N, 0.25) - U(0.25, Gm))
    r1 = e[0] / e[1] if e[1] else float("inf")
    r2 = e[1] / e[2] if e[2] else float("inf")
    rich = e[2] - (e[1] - e[2]) / 3.0          # Richardson remainder at N = 1000
    okB4b = (3.5 < r1 < 4.5 and 3.5 < r2 < 4.5 and abs(rich) < 1e-9)
    if okB4b:
        say("B4b FV band model is SECOND ORDER and converges on the closed form: "
            "errors %.3e / %.3e / %.3e at N = 250/500/1000, ratios %.4f and %.4f "
            "(required in [3.5, 4.5]), Richardson remainder %.3e < 1e-9 -> PASS"
            % (e[0], e[1], e[2], r1, r2, rich))
    else:
        fails.append("B4b FV order (ratios %.4f, %.4f; Richardson remainder %.3e)" % (r1, r2, rich))

    if fails:
        return None, fails
    return dict(G=Gm, P=P, U_025=U(0.25, Gm), U_075=U(0.75, Gm), shear_ratio=sr, Y_max=ym,
                reversal_G=G_REVERSAL, margin_to_reversal=G_REVERSAL / Gm), []


def selftest():
    import ast
    fails = []
    print("exact_t16 selftest:")
    r, f = verify()
    ok = (r is not None and not f)
    print("  [%s] ROUTE B B1-B4 at the registered G = %g" % ("ok " if ok else "FAIL", G_REG))
    if not ok:
        fails.append("routeB: %s" % f)
    r2, f2 = verify(quiet=True, mutate_G=1.01)
    fired = (r2 is None) and any(x.startswith("B3") for x in f2)
    print("  [%s] PLANTED 1 percent G mutation -> B3 REFUSES the tabulated values (%s)"
          % ("ok " if fired else "FAIL", "; ".join(f2)[:96] if f2 else "ACCEPTED BLIND"))
    if not fired:
        fails.append("B5")
    # the discrete model, at the three registered levels
    print("  discrete_expectation (the same FV discretisation the solver uses):")
    prev = None
    monotone = True
    for N in (20, 40, 80):
        d = discrete_expectation(N)
        print("      N=%3d  G1 %+.9f (rel err %+.3e)  G1b %+.9f (abs err %+.3e)  G3 %+.9f (rel err %+.3e)"
              % (N, d["G1"], d["G1_rel_err"], d["G1b"], d["G1b_abs_err"], d["G3"], d["G3_rel_err"]))
        if prev is not None and abs(d["G1_rel_err"]) >= abs(prev):
            monotone = False
        prev = abs(d["G1_rel_err"])
    print("  [%s] the predicted G1 error falls monotonically with refinement" % ("ok " if monotone else "FAIL"))
    if not monotone:
        fails.append("discrete-monotone")
    # the reversal margin is registered and real
    ok = abs(shear_ratio(G_REG) - 5.0) < 1e-13 and G_REG / G_REVERSAL == 2.0 / 3.0
    print("  [%s] G = %g is exactly 2/3 of the reversal threshold %g; no reversal (dU/dY at the cold "
          "wall = %+.6f > 0)" % ("ok " if ok else "FAIL", G_REG, G_REVERSAL, -dUdY(1.0)))
    if not ok:
        fails.append("reversal")
    src = open(__file__).read()
    n0 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src)))
    n1 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src + "\nassert 1\n")))
    ok = (n0 == 0 and n1 == 1)
    print("  [%s] AST assert count in this file = %d (counter sees a planted assert: %d)"
          % ("ok " if ok else "FAIL", n0, n1))
    if not ok:
        fails.append("ast")
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if "--verify" in argv:
        r, f = verify()
        if f:
            refuse("route B failed: %s" % "; ".join(f))
        print("ROUTE B VERIFIED (B1 B2 B3 B4 each printed from inside its own branch)")
        return EXIT_OK
    print(__doc__)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
