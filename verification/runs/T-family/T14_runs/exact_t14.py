#!/usr/bin/env python3
"""T14's analytic reference, DERIVED -- never transcribed from a page.

TWO-DIMENSIONAL TRANSIENT CONDUCTION IN A SQUARE (T11b: the second EXACT
transient, the 2-D product extension of T11).

THE PROBLEM.  A square of half-side L, symmetry planes at x = 0 and y = 0,
convective (Robin) faces at x = L and y = L with the same h, T_inf, uniform
initial temperature T_0, constant properties, no generation:

    theta_t = alpha (theta_xx + theta_yy),      theta = (T - T_inf)/(T_0 - T_inf)
    theta_x(0, y) = 0,  theta_y(x, 0) = 0
    -k theta_x(L, y) = h theta(L, y),  -k theta_y(x, L) = h theta(x, L)
    theta(x, y, 0) = 1

SEPARATION.  Because the initial condition is the product 1 * 1 and every
boundary condition is homogeneous and separable, theta(x, y, t) = f(x, t) f(y, t)
where f is the ONE-DIMENSIONAL plane-wall solution (the T11 series):

    f(x*, Fo) = SUM_n C_n exp(-zeta_n^2 Fo) cos(zeta_n x*)
    C_n       = 4 sin(zeta_n) / (2 zeta_n + sin(2 zeta_n))
    zeta_n tan(zeta_n) = Bi,   x* = x/L,  Fo = alpha t / L^2,  Bi = h L / k

Proof: with theta = f(x,t) f(y,t),  theta_t = f_t f + f f_t
  = alpha f_xx f + alpha f f_yy = alpha (theta_xx + theta_yy);  each boundary
condition reduces to the 1-D one because the other factor is common; the
initial product is 1.  Uniqueness of the linear problem does the rest.

    theta_mean(Fo) = f_mean(Fo)^2,   f_mean = SUM_n C_n exp(-zeta_n^2 Fo) sin(zeta_n)/zeta_n

The series is exact for all Fo.  The reductions (one-term, lumped,
semi-infinite) are NOT used as referents.

VERIFICATION IS BY ROUTE B: the series is differentiated numerically on its
own output and must satisfy the PDE, both boundary conditions and the initial
condition; the 1-D factors are CROSS-CHECKED against T11's registered values
(T11_PREREGISTRATION.md section 6: theta_mean 0.8515954577, theta(0) 0.9506417785,
theta(1) 0.6433907845 at Fo = 0.20, Bi = 1) -- a number this module did not
compute -- so a wrong eigenvalue, a wrong coefficient or a wrong sign is
REFUSED rather than graded.  A selftest plants a 1 percent error into C_n and
requires that refusal to fire (rule 3 applied to the referent itself).

NO `assert` STATEMENT IN THIS FILE (L-332).  Every refusal is sys.exit(2).
"""
import math
import sys

N_TERMS = 80
EXIT_REFUSE = 2

# T11's registered values (docs/campaigns/T-family/T11_PREREGISTRATION.md section 6)
T11_REGISTERED = dict(Fo=0.20, Bi=1.0, theta_mean=0.8515954577,
                      theta_0=0.9506417785, theta_1=0.6433907845)


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

    def theta(self, xs, ys, Fo):
        return self.f(xs, Fo) * self.f(ys, Fo)

    def theta_mean(self, Fo):
        return self.f_mean(Fo) ** 2


def verify(Bi, Fo, series=None, tol_pde=5e-5, tol_bc=1e-7, tol_cross=1e-9, quiet=False):
    """ROUTE B + CROSS-CHECK.  Refuses (exit 2) on any failure."""
    S = series or Series(Bi)
    h = 1e-3
    # (a) the 2-D PDE, by centred finite differences on the series itself, at 9
    # points, at TWO stencil widths: the residual must be small AND fall as h^2
    # (ratio in [3, 5]) so that what remains is shown to be finite-difference
    # truncation and not a series error.
    def pde_residual(hh):
        w = 0.0
        for xs in (0.1, 0.5, 0.9):
            for ys in (0.2, 0.5, 0.8):
                tt = (S.theta(xs, ys, Fo + hh) - S.theta(xs, ys, Fo - hh)) / (2 * hh)
                xx = (S.theta(xs + hh, ys, Fo) - 2 * S.theta(xs, ys, Fo) + S.theta(xs - hh, ys, Fo)) / (hh * hh)
                yy = (S.theta(xs, ys + hh, Fo) - 2 * S.theta(xs, ys, Fo) + S.theta(xs, ys - hh, Fo)) / (hh * hh)
                w = max(w, abs(tt - (xx + yy)))
        return w
    worst, worst2 = pde_residual(h), pde_residual(2 * h)
    if worst > tol_pde:
        refuse("Route B: the series does not satisfy theta_t = theta_xx + theta_yy "
               "(worst residual %.3e > %.1e)" % (worst, tol_pde))
    if not (3.0 <= worst2 / worst <= 5.0):
        refuse("Route B: the PDE residual does not fall as h^2 (%.3e at 2h vs %.3e at h, "
               "ratio %.2f) -- it is not finite-difference truncation" % (worst2, worst, worst2 / worst))
    # (b) symmetry planes: theta_x(0,y) = 0, theta_y(x,0) = 0
    sx = abs((S.theta(h, 0.4, Fo) - S.theta(-h, 0.4, Fo)) / (2 * h))
    sy = abs((S.theta(0.4, h, Fo) - S.theta(0.4, -h, Fo)) / (2 * h))
    if max(sx, sy) > tol_bc:
        refuse("Route B: symmetry-plane gradient %.3e > %.1e" % (max(sx, sy), tol_bc))
    # (c) Robin faces: -theta_x(1,y) = Bi theta(1,y)  (and by symmetry in y)
    gx = (S.theta(1 + h, 0.4, Fo) - S.theta(1 - h, 0.4, Fo)) / (2 * h)
    rob = abs(-gx - Bi * S.theta(1.0, 0.4, Fo))
    if rob > tol_bc:
        refuse("Route B: Robin face residual %.3e > %.1e" % (rob, tol_bc))
    # (d) initial condition: the series at Fo = 0 is 1 (Gibbs at the face; interior)
    ic = max(abs(S.theta(xs, ys, 0.0) - 1.0) for xs in (0.1, 0.5, 0.8) for ys in (0.1, 0.5, 0.8))
    if ic > 5e-3:
        refuse("Route B: initial condition not recovered (worst %.3e)" % ic)
    # (e) product structure: theta(x,y) == f(x) f(y) and theta(x,y) == theta(y,x)
    sym = max(abs(S.theta(a, b, Fo) - S.theta(b, a, Fo)) for a, b in ((0.1, 0.7), (0.3, 0.9)))
    if sym > 1e-15:
        refuse("product structure broken: theta(x,y) != theta(y,x) by %.3e" % sym)
    # (f) the mean by 2-D Simpson quadrature vs closed form
    n = 200
    w = [1] + [4 if i % 2 else 2 for i in range(1, n)] + [1]
    tot = 0.0
    for i in range(n + 1):
        for j in range(n + 1):
            tot += w[i] * w[j] * S.theta(i / n, j / n, Fo)
    q = tot / (3.0 * n) ** 2
    if abs(q - S.theta_mean(Fo)) > 1e-9:
        refuse("closed-form theta_mean %.12g disagrees with Simpson %.12g" % (S.theta_mean(Fo), q))
    # (g) CROSS-CHECK against T11's registered numbers (only at T11's point)
    R = T11_REGISTERED
    if abs(Bi - R["Bi"]) < 1e-15 and abs(Fo - R["Fo"]) < 1e-15:
        for label, got, want in (("theta_mean", S.f_mean(Fo), R["theta_mean"]),
                                 ("theta(0)", S.f(0.0, Fo), R["theta_0"]),
                                 ("theta(1)", S.f(1.0, Fo), R["theta_1"])):
            if abs(got - want) > tol_cross:
                refuse("CROSS-CHECK against T11's registered 1-D %s FAILED: this module "
                       "gives %.10f, T11_PREREGISTRATION.md section 6 registers %.10f "
                       "(|diff| %.3e > %.1e). The referent is wrong or mutated; nothing "
                       "is graded against it." % (label, got, want, abs(got - want), tol_cross))
    if not quiet:
        print("  exact_t14.verify: PDE residual %.2e; symmetry grads %.1e; Robin %.1e; "
              "IC %.1e; theta(x,y)=theta(y,x); Simpson agrees to %.1e; cross-check vs "
              "T11 registered values PASS (Bi=%g Fo=%g)"
              % (worst, max(sx, sy), rob, ic, abs(q - S.theta_mean(Fo)), Bi, Fo))
    return S


def selftest():
    """The planted-wrong-referent arm: C_n mutated by 1 percent MUST be refused."""
    fails = []
    S = verify(1.0, 0.20)
    print("  theta_mean = %.10f  theta(0,0) = %.10f  theta(1,0) = %.10f"
          % (S.theta_mean(0.2), S.theta(0, 0, 0.2), S.theta(1, 0, 0.2)))
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
        # a wrong eigenvalue set (Bi = 1.01 series checked at Bi = 1) must be refused too
        verify(1.0, 0.20, series=Series(1.01), quiet=True)
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    print("  [%s] eigenvalues from Bi=1.01 checked at Bi=1 -> verify REFUSES" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("planted-wrong-eigenvalues")
    import ast
    n_assert = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(open(__file__).read())))
    n_planted = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(open(__file__).read() + "\nassert 1\n")))
    ok = (n_assert == 0 and n_planted == 1)
    print("  [%s] AST assert count = %d (counter sees a planted assert: %d)" % ("ok " if ok else "FAIL", n_assert, n_planted))
    if not ok:
        fails.append("ast")
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    S = verify(1.0, 0.20)
    print("theta_mean(Fo=0.2, Bi=1) = %.12f" % S.theta_mean(0.2))
    print("theta(0,0)               = %.12f" % S.theta(0, 0, 0.2))
    print("theta(1,0)               = %.12f" % S.theta(1, 0, 0.2))
