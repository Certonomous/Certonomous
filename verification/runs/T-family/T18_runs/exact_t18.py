#!/usr/bin/env python3
"""T18's analytic reference, DERIVED -- never transcribed from a page.

THREE-DIMENSIONAL TRANSIENT CONDUCTION IN A CUBE (T11c: the third EXACT
transient, the 3-D product extension of T11 and T14).

THE PROBLEM.  An octant of a cube of half-side L, symmetry planes at x = 0,
y = 0 and z = 0, convective (Robin) faces at x = L, y = L and z = L with the
same h, T_inf, uniform initial temperature T_0, constant properties, no
generation:

    theta_t = alpha (theta_xx + theta_yy + theta_zz),  theta = (T-T_inf)/(T_0-T_inf)
    theta_x(0,y,z) = theta_y(x,0,z) = theta_z(x,y,0) = 0
    -k theta_n = h theta on x = L, y = L, z = L
    theta(x, y, z, 0) = 1

SEPARATION.  Because the initial condition is the product 1*1*1 and every
boundary condition is homogeneous and separable, theta = f(x,t) f(y,t) f(z,t)
where f is the ONE-DIMENSIONAL plane-wall solution (the T11 series):

    f(x*, Fo) = SUM_n C_n exp(-zeta_n^2 Fo) cos(zeta_n x*)
    C_n       = 4 sin(zeta_n) / (2 zeta_n + sin(2 zeta_n))
    zeta_n tan(zeta_n) = Bi,   x* = x/L,  Fo = alpha t / L^2,  Bi = h L / k

Proof: with theta = f(x,t) f(y,t) f(z,t),
  theta_t = f_t f f + f f_t f + f f f_t
          = alpha (f_xx f f + f f_yy f + f f f_zz)
          = alpha (theta_xx + theta_yy + theta_zz);
each boundary condition reduces to the 1-D one because the other two factors
are common to both sides; the initial product is 1.  Uniqueness of the linear
problem does the rest.

    theta_mean(Fo) = f_mean(Fo)^3,
    f_mean = SUM_n C_n exp(-zeta_n^2 Fo) sin(zeta_n)/zeta_n

The series is exact for all Fo.  The reductions (one-term, lumped,
semi-infinite) are NOT used as referents.

VERIFICATION IS BY ROUTE B: the series is differentiated numerically on its own
output and must satisfy the 3-D PDE, all three symmetry planes, all three Robin
faces and the initial condition; the mean is confirmed by 3-D Simpson
quadrature against the closed form; and the 1-D factors are CROSS-CHECKED
against TWO sets of numbers this module did not compute --

    T11 (1-D plane wall), T11_PREREGISTRATION.md section 6:
        f_mean 0.8515954577, f(0) 0.9506417785, f(1) 0.6433907845
    T14 (2-D square),      T14_registered.json graded_rows:
        theta_mean 0.7252148236, theta(0,0) 0.9037197910, theta(1,0) 0.6116341596

-- so a wrong eigenvalue, a wrong coefficient or a wrong sign is REFUSED rather
than graded.  A selftest plants a 1 percent error into C_n and requires that
refusal to fire (rule 3 applied to the referent itself).

NO `assert` STATEMENT IN THIS FILE (L-332).  Every refusal is sys.exit(2).
"""
import math
import sys

N_TERMS = 80
EXIT_REFUSE = 2

# T11's registered 1-D values (docs/campaigns/T-family/T11_PREREGISTRATION.md section 6)
T11_REGISTERED = dict(Fo=0.20, Bi=1.0, f_mean=0.8515954577,
                      f_0=0.9506417785, f_1=0.6433907845)
# T14's registered 2-D values (verification/runs/T-family/T14_runs/T14_registered.json)
T14_REGISTERED = dict(Fo=0.20, Bi=1.0, theta_mean=0.7252148236,
                      theta_00=0.9037197910, theta_10=0.6116341596)


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def eigenvalues(Bi, n=N_TERMS):
    """Roots of zeta tan(zeta) = Bi, one per interval ((k-1)pi, (k-1/2)pi), by bisection."""
    zs = []
    for k in range(n):
        lo, hi = k * math.pi + 1e-12, (k + 0.5) * math.pi - 1e-12
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            g = mid * math.tan(mid) - Bi
            if g > 0:
                hi = mid
            else:
                lo = mid
        zs.append(0.5 * (lo + hi))
    return zs


def coefficients(zs, mutate=1.0):
    """C_n = 4 sin z / (2 z + sin 2 z).  `mutate` exists ONLY for the selftest's
    planted-wrong-referent arm."""
    return [mutate * 4.0 * math.sin(z) / (2.0 * z + math.sin(2.0 * z)) for z in zs]


class Series:
    def __init__(self, Bi, mutate=1.0):
        self.Bi = Bi
        self.z = eigenvalues(Bi)
        self.C = coefficients(self.z, mutate)

    def f(self, xs, Fo):
        return sum(c * math.exp(-z * z * Fo) * math.cos(z * xs) for c, z in zip(self.C, self.z))

    def f_mean(self, Fo):
        return sum(c * math.exp(-z * z * Fo) * math.sin(z) / z for c, z in zip(self.C, self.z))

    def theta(self, xs, ys, zs_, Fo):
        return self.f(xs, Fo) * self.f(ys, Fo) * self.f(zs_, Fo)

    def theta_mean(self, Fo):
        return self.f_mean(Fo) ** 3


def verify(Bi, Fo, series=None, tol_pde=5e-5, tol_bc=1e-7, tol_cross=1e-9, quiet=False):
    """ROUTE B + TWO CROSS-CHECKS.  Refuses (exit 2) on any failure."""
    S = series or Series(Bi)
    h = 1e-3

    # (a) the 3-D PDE, by centred finite differences on the series itself, at 8
    # points, at TWO stencil widths: the residual must be small AND fall as h^2
    # (ratio in [3, 5]) so that what remains is shown to be finite-difference
    # truncation and not a series error.
    def pde_residual(hh):
        w = 0.0
        for xs in (0.15, 0.65):
            for ys in (0.25, 0.75):
                for zz in (0.35, 0.85):
                    tt = (S.theta(xs, ys, zz, Fo + hh) - S.theta(xs, ys, zz, Fo - hh)) / (2 * hh)
                    c0 = S.theta(xs, ys, zz, Fo)
                    xx = (S.theta(xs + hh, ys, zz, Fo) - 2 * c0 + S.theta(xs - hh, ys, zz, Fo)) / (hh * hh)
                    yy = (S.theta(xs, ys + hh, zz, Fo) - 2 * c0 + S.theta(xs, ys - hh, zz, Fo)) / (hh * hh)
                    zzz = (S.theta(xs, ys, zz + hh, Fo) - 2 * c0 + S.theta(xs, ys, zz - hh, Fo)) / (hh * hh)
                    w = max(w, abs(tt - (xx + yy + zzz)))
        return w
    worst, worst2 = pde_residual(h), pde_residual(2 * h)
    if worst > tol_pde:
        refuse("Route B: the series does not satisfy theta_t = theta_xx + theta_yy + theta_zz "
               "(worst residual %.3e > %.1e)" % (worst, tol_pde))
    if not (3.0 <= worst2 / worst <= 5.0):
        refuse("Route B: the PDE residual does not fall as h^2 (%.3e at 2h vs %.3e at h, "
               "ratio %.2f) -- it is not finite-difference truncation" % (worst2, worst, worst2 / worst))

    # (b) all THREE symmetry planes
    g = [abs((S.theta(h, 0.4, 0.6, Fo) - S.theta(-h, 0.4, 0.6, Fo)) / (2 * h)),
         abs((S.theta(0.4, h, 0.6, Fo) - S.theta(0.4, -h, 0.6, Fo)) / (2 * h)),
         abs((S.theta(0.4, 0.6, h, Fo) - S.theta(0.4, 0.6, -h, Fo)) / (2 * h))]
    if max(g) > tol_bc:
        refuse("Route B: symmetry-plane gradient %.3e > %.1e" % (max(g), tol_bc))

    # (c) all THREE Robin faces: -theta_n(1) = Bi theta(1)
    rob = []
    gx = (S.theta(1 + h, 0.4, 0.6, Fo) - S.theta(1 - h, 0.4, 0.6, Fo)) / (2 * h)
    rob.append(abs(-gx - Bi * S.theta(1.0, 0.4, 0.6, Fo)))
    gy = (S.theta(0.4, 1 + h, 0.6, Fo) - S.theta(0.4, 1 - h, 0.6, Fo)) / (2 * h)
    rob.append(abs(-gy - Bi * S.theta(0.4, 1.0, 0.6, Fo)))
    gz = (S.theta(0.4, 0.6, 1 + h, Fo) - S.theta(0.4, 0.6, 1 - h, Fo)) / (2 * h)
    rob.append(abs(-gz - Bi * S.theta(0.4, 0.6, 1.0, Fo)))
    if max(rob) > tol_bc:
        refuse("Route B: Robin face residual %.3e > %.1e" % (max(rob), tol_bc))

    # (d) initial condition: the series at Fo = 0 is 1 (Gibbs at the faces; interior)
    ic = max(abs(S.theta(a, b, c, 0.0) - 1.0)
             for a in (0.1, 0.5) for b in (0.1, 0.5) for c in (0.1, 0.5))
    if ic > 1e-2:
        refuse("Route B: initial condition not recovered (worst %.3e)" % ic)

    # (e) product structure: theta is invariant under any permutation of (x,y,z)
    perm = max(abs(S.theta(0.1, 0.4, 0.8, Fo) - S.theta(p, q, r, Fo))
               for p, q, r in ((0.1, 0.8, 0.4), (0.4, 0.1, 0.8), (0.4, 0.8, 0.1),
                               (0.8, 0.1, 0.4), (0.8, 0.4, 0.1)))
    if perm > 1e-15:
        refuse("product structure broken: theta is not permutation-symmetric (%.3e)" % perm)

    # (f) the mean by 3-D Simpson quadrature vs the closed form
    n = 60
    w = [1] + [4 if i % 2 else 2 for i in range(1, n)] + [1]
    fs = [S.f(i / n, Fo) for i in range(n + 1)]
    q1 = sum(w[i] * fs[i] for i in range(n + 1)) / (3.0 * n)
    q = q1 ** 3
    if abs(q - S.theta_mean(Fo)) > 1e-9:
        refuse("closed-form theta_mean %.12g disagrees with Simpson %.12g" % (S.theta_mean(Fo), q))

    # (g) CROSS-CHECK 1: T11's registered 1-D numbers (only at T11's point)
    R = T11_REGISTERED
    if abs(Bi - R["Bi"]) < 1e-15 and abs(Fo - R["Fo"]) < 1e-15:
        for label, got, want in (("f_mean", S.f_mean(Fo), R["f_mean"]),
                                 ("f(0)", S.f(0.0, Fo), R["f_0"]),
                                 ("f(1)", S.f(1.0, Fo), R["f_1"])):
            if abs(got - want) > tol_cross:
                refuse("CROSS-CHECK against T11's registered 1-D %s FAILED: this module "
                       "gives %.10f, T11_PREREGISTRATION.md section 6 registers %.10f "
                       "(|diff| %.3e > %.1e). The referent is wrong or mutated; nothing "
                       "is graded against it." % (label, got, want, abs(got - want), tol_cross))
    # (h) CROSS-CHECK 2: T14's registered 2-D numbers, which are the SQUARE of the
    # same factors -- an independent registration of the same series by another rung.
    R2 = T14_REGISTERED
    if abs(Bi - R2["Bi"]) < 1e-15 and abs(Fo - R2["Fo"]) < 1e-15:
        for label, got, want in (("theta_mean_2D", S.f_mean(Fo) ** 2, R2["theta_mean"]),
                                 ("theta(0,0)_2D", S.f(0.0, Fo) ** 2, R2["theta_00"]),
                                 ("theta(1,0)_2D", S.f(1.0, Fo) * S.f(0.0, Fo), R2["theta_10"])):
            if abs(got - want) > tol_cross:
                refuse("CROSS-CHECK against T14's registered 2-D %s FAILED: this module "
                       "gives %.10f, T14_registered.json registers %.10f (|diff| %.3e > %.1e). "
                       "The referent is wrong or mutated; nothing is graded against it."
                       % (label, got, want, abs(got - want), tol_cross))
    if not quiet:
        print("  exact_t18.verify: PDE residual %.2e (falls as h^2, ratio %.2f); symmetry grads %.1e; "
              "Robin %.1e; IC %.1e; permutation-symmetric; Simpson agrees to %.1e; cross-checks vs "
              "T11 AND T14 registered values PASS (Bi=%g Fo=%g)"
              % (worst, worst2 / worst, max(g), max(rob), ic, abs(q - S.theta_mean(Fo)), Bi, Fo))
    return S


def selftest():
    """The planted-wrong-referent arms: C_n mutated by 1 percent, and eigenvalues
    from the wrong Bi, MUST both be refused."""
    fails = []
    S = verify(1.0, 0.20)
    print("  theta_mean = %.10f  theta(0,0,0) = %.10f  theta(1,0,0) = %.10f  theta(1,1,1) = %.10f"
          % (S.theta_mean(0.2), S.theta(0, 0, 0, 0.2), S.theta(1, 0, 0, 0.2), S.theta(1, 1, 1, 0.2)))
    fired = False
    try:
        verify(1.0, 0.20, series=Series(1.0, mutate=1.01), quiet=True)
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    print("  [%s] C_n planted 1 percent wrong -> verify REFUSES (exit 2)" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("planted-wrong-referent")
    fired = False
    try:
        verify(1.0, 0.20, series=Series(1.01), quiet=True)
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    print("  [%s] eigenvalues from Bi=1.01 checked at Bi=1 -> verify REFUSES" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("planted-wrong-eigenvalues")
    # a mutation small enough to survive Route B but not the cross-checks
    fired = False
    try:
        verify(1.0, 0.20, series=Series(1.0, mutate=1.0 + 1e-7), quiet=True)
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    print("  [%s] C_n planted 1e-7 wrong -> the T11/T14 CROSS-CHECKS refuse it" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("cross-check-sensitivity")
    import ast
    src = open(__file__).read()
    n_assert = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src)))
    n_planted = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src + "\nassert 1\n")))
    ok = (n_assert == 0 and n_planted == 1)
    print("  [%s] AST assert count = %d (counter sees a planted assert: %d)"
          % ("ok " if ok else "FAIL", n_assert, n_planted))
    if not ok:
        fails.append("ast")
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    S = verify(1.0, 0.20)
    print("theta_mean(Fo=0.2, Bi=1) = %.12f" % S.theta_mean(0.2))
    print("theta(0,0,0)             = %.12f" % S.theta(0, 0, 0, 0.2))
    print("theta(1,0,0)             = %.12f" % S.theta(1, 0, 0, 0.2))
    print("theta(1,1,1)             = %.12f" % S.theta(1, 1, 1, 0.2))
