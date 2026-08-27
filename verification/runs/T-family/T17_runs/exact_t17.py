#!/usr/bin/env python3
"""T17's analytic reference, DERIVED -- never transcribed from a page.

AXISYMMETRIC TRANSIENT CONDUCTION IN A FINITE (SHORT) CYLINDER (T11d).

THE PROBLEM.  A quarter section of a solid cylinder of radius R and half-length
H: the axis at r = 0, a symmetry plane at z = 0, convective (Robin) surfaces at
r = R and z = H with the same h and T_inf, uniform initial temperature T_0,
constant properties, no generation:

    theta_t = alpha (theta_rr + theta_r / r + theta_zz),  theta = (T-T_inf)/(T_0-T_inf)
    theta_r(0,z) = 0 (regularity on the axis),  theta_z(r,0) = 0 (symmetry)
    -k theta_r(R,z) = h theta(R,z),  -k theta_z(r,H) = h theta(r,H)
    theta(r, z, 0) = 1

SEPARATION -- THE CLASSIC PRODUCT SOLUTION.  With R = H and the same h, define
Bi = hR/k = hH/k and Fo = alpha t / R^2 = alpha t / H^2.  Because the initial
condition is the product 1*1 and every boundary condition is homogeneous and
separable, theta(r,z,t) = C(r*,Fo) P(z*,Fo) where

  C is the INFINITE-CYLINDER series (Bessel):
    C(r*,Fo) = SUM_n D_n exp(-zeta_n^2 Fo) J0(zeta_n r*)
    zeta_n J1(zeta_n) = Bi J0(zeta_n)
    D_n = (2/zeta_n) J1(zeta_n) / (J0(zeta_n)^2 + J1(zeta_n)^2)
    C_mean(Fo) = SUM_n D_n exp(-zeta_n^2 Fo) 2 J1(zeta_n)/zeta_n
        (because the disc-average of J0(zeta r*) is 2 INT_0^1 r J0(zeta r) dr
         = 2 J1(zeta)/zeta)

  P is the PLANE-WALL series (the T11 series):
    P(z*,Fo) = SUM_n A_n exp(-eta_n^2 Fo) cos(eta_n z*)
    A_n = 4 sin(eta_n)/(2 eta_n + sin(2 eta_n)),  eta_n tan(eta_n) = Bi
    P_mean(Fo) = SUM_n A_n exp(-eta_n^2 Fo) sin(eta_n)/eta_n

Proof: with theta = C P, theta_t = C_t P + C P_t
  = alpha (C_rr + C_r/r) P + alpha C P_zz = alpha (theta_rr + theta_r/r + theta_zz);
each boundary condition reduces to a one-factor condition because the other
factor is common; the initial product is 1.  Uniqueness does the rest.

    theta_mean(Fo) = C_mean(Fo) * P_mean(Fo)

BESSEL FUNCTIONS ARE COMPUTED HERE, NOT IMPORTED.  J0 and J1 come from their
integral representations

    J0(x) = (1/2pi) INT_0^{2pi} cos(x sin t) dt
    J1(x) = (1/2pi) INT_0^{2pi} cos(t - x sin t) dt

evaluated by the trapezoidal rule on a periodic analytic integrand, which
converges spectrally and suffers none of the catastrophic cancellation the
power series suffers at large x.  This file has NO third-party dependency; the
selftest cross-checks it against an INDEPENDENT power-series implementation
(accurate for small x) and, if scipy happens to be installed, against
scipy.special as well -- reported, never required.

VERIFICATION IS BY ROUTE B plus FOUR independent checks:
  (a) the axisymmetric PDE, by centred differences on the series' own output,
      at two stencil widths, falling as h^2;
  (b) the axis regularity condition and the symmetry plane;
  (c) both Robin surfaces;
  (d) the initial condition;
  (e) the mean by 2-r-weighted Simpson quadrature against the closed form;
  (f) J0 and J1 satisfy Bessel's equation x^2 y'' + x y' + (x^2 - nu^2) y = 0;
  (g) THE LUMPED LIMIT, which is an EXTERNAL statement about the physics and
      not about this series: as Bi -> 0 the cylinder factor must approach
      exp(-2 Bi Fo) and the plane-wall factor exp(-Bi Fo), because V/A is R/2
      for a cylinder and H for a slab;
  (h) CROSS-CHECK of the plane-wall factor against T11's registered numbers,
      which this module did not compute (T11_PREREGISTRATION.md section 6:
      P_mean 0.8515954577, P(0) 0.9506417785, P(1) 0.6433907845).

A selftest plants a 1 percent error into the Bessel coefficients D_n and
requires a refusal to fire (rule 3 applied to the referent itself).

NO `assert` STATEMENT IN THIS FILE (L-332).  Every refusal is sys.exit(2).
"""
import math
import sys

N_TERMS_WALL = 80
N_TERMS_CYL = 25
BESSEL_M = 512          # trapezoidal points on [0, 2pi)
EXIT_REFUSE = 2

# T11's registered plane-wall values (docs/campaigns/T-family/T11_PREREGISTRATION.md section 6)
T11_REGISTERED = dict(Fo=0.20, Bi=1.0, P_mean=0.8515954577,
                      P_0=0.9506417785, P_1=0.6433907845)


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


# ------------------------------------------------------------- Bessel J0, J1
_TRAP = [2.0 * math.pi * m / BESSEL_M for m in range(BESSEL_M)]


def J0(x):
    return sum(math.cos(x * math.sin(t)) for t in _TRAP) / BESSEL_M


def J1(x):
    return sum(math.cos(t - x * math.sin(t)) for t in _TRAP) / BESSEL_M


def J0_series(x, n=60):
    """INDEPENDENT implementation, power series.  Accurate for |x| <~ 12; used
    only by the selftest as a second opinion, never by the referent."""
    s, term = 0.0, 1.0
    for k in range(n):
        if k:
            term *= -(x * x) / (4.0 * k * k)
        s += term
    return s


def J1_series(x, n=60):
    s, term = 0.0, x / 2.0
    for k in range(n):
        if k:
            term *= -(x * x) / (4.0 * k * (k + 1))
        s += term
    return s


# --------------------------------------------------------------- eigenvalues
def wall_eigenvalues(Bi, n=N_TERMS_WALL):
    """Roots of eta tan(eta) = Bi, one per ((k-1)pi, (k-1/2)pi), by bisection."""
    zs = []
    for k in range(n):
        lo, hi = k * math.pi + 1e-12, (k + 0.5) * math.pi - 1e-12
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if mid * math.tan(mid) - Bi > 0:
                hi = mid
            else:
                lo = mid
        zs.append(0.5 * (lo + hi))
    return zs


def cyl_eigenvalues(Bi, n=N_TERMS_CYL, zmax=None):
    """Roots of g(z) = z J1(z) - Bi J0(z), found by a DENSE SCAN for sign changes
    followed by bisection -- no closed-form bracketing is assumed."""
    zmax = zmax or (n + 2) * math.pi
    step = 1.0e-3
    def g(z):
        return z * J1(z) - Bi * J0(z)
    zs = []
    z0, g0 = step, g(step)
    z = z0 + step
    while z < zmax and len(zs) < n:
        g1 = g(z)
        if g0 == 0.0:
            zs.append(z0)
        elif g0 * g1 < 0.0:
            lo, hi = z0, z
            for _ in range(200):
                mid = 0.5 * (lo + hi)
                if g(mid) * g0 > 0:
                    lo = mid
                else:
                    hi = mid
            zs.append(0.5 * (lo + hi))
        z0, g0 = z, g1
        z += step
    if len(zs) < n:
        refuse("cylinder eigenvalue scan found only %d of %d roots below z=%.3f" % (len(zs), n, zmax))
    return zs


class Series:
    """The product referent.  `mutate_cyl` and `mutate_wall` exist ONLY for the
    selftest's planted-wrong-referent arms."""

    def __init__(self, Bi, mutate_cyl=1.0, mutate_wall=1.0):
        self.Bi = Bi
        # the mutation factors are CARRIED so that the lumped-limit normalisation
        # check in verify() is applied to THE SAME coefficient formula under test;
        # a limit check built from a fresh, unmutated series checks nothing (this
        # was measured: a 1 percent D_n mutation survived until this was fixed).
        self.mutate_cyl, self.mutate_wall = mutate_cyl, mutate_wall
        self.eta = wall_eigenvalues(Bi)
        self.A = [mutate_wall * 4.0 * math.sin(e) / (2.0 * e + math.sin(2.0 * e)) for e in self.eta]
        self.zeta = cyl_eigenvalues(Bi)
        self.D = []
        for z in self.zeta:
            j0, j1 = J0(z), J1(z)
            self.D.append(mutate_cyl * (2.0 / z) * j1 / (j0 * j0 + j1 * j1))

    # ---- the plane-wall (axial) factor
    def P(self, zs, Fo):
        return sum(a * math.exp(-e * e * Fo) * math.cos(e * zs) for a, e in zip(self.A, self.eta))

    def P_mean(self, Fo):
        return sum(a * math.exp(-e * e * Fo) * math.sin(e) / e for a, e in zip(self.A, self.eta))

    # ---- the infinite-cylinder (radial) factor
    def C(self, rs, Fo):
        return sum(d * math.exp(-z * z * Fo) * J0(z * rs) for d, z in zip(self.D, self.zeta))

    def C_mean(self, Fo):
        return sum(d * math.exp(-z * z * Fo) * 2.0 * J1(z) / z for d, z in zip(self.D, self.zeta))

    # ---- the product
    def theta(self, rs, zs, Fo):
        return self.C(rs, Fo) * self.P(zs, Fo)

    def theta_mean(self, Fo):
        return self.C_mean(Fo) * self.P_mean(Fo)


def verify(Bi, Fo, series=None, tol_pde=2e-4, tol_bc=1e-6, tol_cross=1e-9, quiet=False):
    """ROUTE B + the lumped limit + the T11 cross-check.  Refuses (exit 2) on any failure."""
    S = series or Series(Bi)
    h = 1e-3

    # (f) Bessel's equation, on this file's OWN J0/J1 -- checked first, because
    # everything radial rests on them.
    for nu, fn in ((0, J0), (1, J1)):
        worst = 0.0
        for x in (0.7, 1.3, 2.9, 5.4, 8.6, 11.9):
            yp = (fn(x + h) - fn(x - h)) / (2 * h)
            ypp = (fn(x + h) - 2 * fn(x) + fn(x - h)) / (h * h)
            worst = max(worst, abs(x * x * ypp + x * yp + (x * x - nu * nu) * fn(x)))
        if worst > 1e-5:
            refuse("J%d does not satisfy Bessel's equation (worst residual %.3e)" % (nu, worst))

    # (a) the axisymmetric PDE at two stencil widths
    def pde_residual(hh):
        w = 0.0
        for rs in (0.2, 0.5, 0.85):
            for zs in (0.2, 0.5, 0.85):
                tt = (S.theta(rs, zs, Fo + hh) - S.theta(rs, zs, Fo - hh)) / (2 * hh)
                c0 = S.theta(rs, zs, Fo)
                rr = (S.theta(rs + hh, zs, Fo) - 2 * c0 + S.theta(rs - hh, zs, Fo)) / (hh * hh)
                r1 = (S.theta(rs + hh, zs, Fo) - S.theta(rs - hh, zs, Fo)) / (2 * hh)
                zz = (S.theta(rs, zs + hh, Fo) - 2 * c0 + S.theta(rs, zs - hh, Fo)) / (hh * hh)
                w = max(w, abs(tt - (rr + r1 / rs + zz)))
        return w
    worst, worst2 = pde_residual(h), pde_residual(2 * h)
    if worst > tol_pde:
        refuse("Route B: the series does not satisfy theta_t = theta_rr + theta_r/r + theta_zz "
               "(worst residual %.3e > %.1e)" % (worst, tol_pde))
    if not (3.0 <= worst2 / worst <= 5.0):
        refuse("Route B: the PDE residual does not fall as h^2 (%.3e at 2h vs %.3e at h, ratio %.2f) "
               "-- it is not finite-difference truncation" % (worst2, worst, worst2 / worst))

    # (b) axis regularity and the z = 0 symmetry plane
    gr = abs((S.theta(h, 0.4, Fo) - S.theta(-h, 0.4, Fo)) / (2 * h))
    gz = abs((S.theta(0.4, h, Fo) - S.theta(0.4, -h, Fo)) / (2 * h))
    if max(gr, gz) > tol_bc:
        refuse("Route B: axis/symmetry gradient %.3e > %.1e" % (max(gr, gz), tol_bc))

    # (c) both Robin surfaces
    grr = (S.theta(1 + h, 0.4, Fo) - S.theta(1 - h, 0.4, Fo)) / (2 * h)
    rob_r = abs(-grr - Bi * S.theta(1.0, 0.4, Fo))
    gzz = (S.theta(0.4, 1 + h, Fo) - S.theta(0.4, 1 - h, Fo)) / (2 * h)
    rob_z = abs(-gzz - Bi * S.theta(0.4, 1.0, Fo))
    if max(rob_r, rob_z) > tol_bc:
        refuse("Route B: Robin surface residual r %.3e / z %.3e > %.1e" % (rob_r, rob_z, tol_bc))

    # (d) initial condition (Gibbs at the surfaces; interior only)
    ic = max(abs(S.theta(a, b, 0.0) - 1.0) for a in (0.1, 0.4) for b in (0.1, 0.4))
    if ic > 2e-2:
        refuse("Route B: initial condition not recovered (worst %.3e)" % ic)

    # (e) the mean: 2r-weighted Simpson in r, plain Simpson in z, vs the closed form
    n = 400
    w = [1] + [4 if i % 2 else 2 for i in range(1, n)] + [1]
    cm = sum(w[i] * 2.0 * (i / n) * S.C(i / n, Fo) for i in range(n + 1)) / (3.0 * n)
    pm = sum(w[i] * S.P(i / n, Fo) for i in range(n + 1)) / (3.0 * n)
    dq = max(abs(cm - S.C_mean(Fo)), abs(pm - S.P_mean(Fo)))
    if dq > 1e-8:
        refuse("closed-form means disagree with Simpson by %.3e (C %.12g vs %.12g; P %.12g vs %.12g)"
               % (dq, S.C_mean(Fo), cm, S.P_mean(Fo), pm))

    # (g) THE LUMPED LIMIT -- an external statement about the physics
    if Bi > 1e-6:
        small = 1.0e-4
        # BUILT WITH THE SAME COEFFICIENT FORMULA (mutations carried), so this is
        # the NORMALISATION control on D_n and A_n as well as an external physics
        # check: a uniform scaling of either coefficient set satisfies the PDE and
        # both Robin conditions and is invisible to Route B, but it moves the
        # lumped limit by exactly the scale factor.
        Sl = Series(small, mutate_cyl=S.mutate_cyl, mutate_wall=S.mutate_wall)
        want_c, got_c = math.exp(-2.0 * small * Fo), Sl.C_mean(Fo)
        want_p, got_p = math.exp(-small * Fo), Sl.P_mean(Fo)
        if abs(got_c - want_c) > 5e-8 or abs(got_p - want_p) > 5e-8:
            refuse("LUMPED LIMIT FAILED at Bi=1e-4: cylinder mean %.12f vs exp(-2 Bi Fo) %.12f "
                   "(|d| %.3e); wall mean %.12f vs exp(-Bi Fo) %.12f (|d| %.3e) -- the eigenvalues "
                   "or the coefficients are wrong"
                   % (got_c, want_c, abs(got_c - want_c), got_p, want_p, abs(got_p - want_p)))

    # (h) CROSS-CHECK the plane-wall factor against T11's registered numbers
    R = T11_REGISTERED
    if abs(Bi - R["Bi"]) < 1e-15 and abs(Fo - R["Fo"]) < 1e-15:
        for label, got, want in (("P_mean", S.P_mean(Fo), R["P_mean"]),
                                 ("P(0)", S.P(0.0, Fo), R["P_0"]),
                                 ("P(1)", S.P(1.0, Fo), R["P_1"])):
            if abs(got - want) > tol_cross:
                refuse("CROSS-CHECK against T11's registered plane-wall %s FAILED: this module "
                       "gives %.10f, T11_PREREGISTRATION.md section 6 registers %.10f (|diff| %.3e "
                       "> %.1e). The referent is wrong or mutated; nothing is graded against it."
                       % (label, got, want, abs(got - want), tol_cross))
    if not quiet:
        print("  exact_t17.verify: Bessel ODE ok; PDE residual %.2e (ratio %.2f); axis/symmetry %.1e; "
              "Robin %.1e/%.1e; IC %.1e; Simpson agrees to %.1e; LUMPED LIMIT ok; cross-check vs T11 "
              "registered plane-wall values PASS (Bi=%g Fo=%g)"
              % (worst, worst2 / worst, max(gr, gz), rob_r, rob_z, ic, dq, Bi, Fo))
    return S


def selftest():
    fails = []
    S = verify(1.0, 0.20)
    Fo = 0.20
    print("  C_mean = %.10f  P_mean = %.10f  theta_mean = %.10f"
          % (S.C_mean(Fo), S.P_mean(Fo), S.theta_mean(Fo)))
    print("  theta(0,0) = %.10f  theta(1,0) = %.10f  theta(0,1) = %.10f"
          % (S.theta(0, 0, Fo), S.theta(1, 0, Fo), S.theta(0, 1, Fo)))
    # (1) the two independent Bessel implementations must agree where both are valid
    worst = max(max(abs(J0(x) - J0_series(x)), abs(J1(x) - J1_series(x)))
                for x in (0.3, 1.1, 2.7, 4.9, 7.4, 10.3, 11.8))
    ok = worst < 1e-12
    print("  [%s] integral-representation J0/J1 vs an INDEPENDENT power series: worst %.2e"
          % ("ok " if ok else "FAIL", worst))
    if not ok:
        fails.append("bessel-independent")
    # (2) scipy, if present -- reported, never required
    try:
        from scipy import special as _sp
        w2 = max(max(abs(J0(x) - _sp.j0(x)), abs(J1(x) - _sp.j1(x))) for x in (0.3, 2.7, 7.4, 18.0, 25.0))
        print("  [ok ] scipy.special cross-check (REPORTED, not required): worst %.2e" % w2)
    except Exception as e:                                          # noqa: BLE001
        print("  [ok ] scipy not available for the optional cross-check (%s) -- REPORTED, not required"
              % type(e).__name__)
    # (3) the first three cylinder eigenvalues, printed so a reader can see them
    print("  cylinder eigenvalues (Bi=1): " + ", ".join("%.8f" % z for z in S.zeta[:4]))
    # (4) planted-wrong-referent arms
    for label, kw in (("D_n planted 1 percent wrong", dict(mutate_cyl=1.01)),
                      ("A_n planted 1 percent wrong", dict(mutate_wall=1.01)),
                      ("A_n planted 1e-7 wrong", dict(mutate_wall=1.0 + 1e-7)),
                      ("D_n planted 1e-6 wrong", dict(mutate_cyl=1.0 + 1e-6))):
        fired = False
        try:
            verify(1.0, 0.20, series=Series(1.0, **kw), quiet=True)
        except SystemExit as e:
            fired = (e.code == EXIT_REFUSE)
        print("  [%s] %-32s -> verify REFUSES (exit 2)" % ("ok " if fired else "FAIL", label))
        if not fired:
            fails.append(label)
    # (5) eigenvalues from the wrong Bi
    fired = False
    try:
        verify(1.0, 0.20, series=Series(1.05), quiet=True)
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    print("  [%s] eigenvalues from Bi=1.05 checked at Bi=1 -> verify REFUSES" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("planted-wrong-eigenvalues")
    import ast
    src = open(__file__).read()
    n0 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src)))
    n1 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src + "\nassert 1\n")))
    ok = (n0 == 0 and n1 == 1)
    print("  [%s] AST assert count = %d (counter sees a planted assert: %d)" % ("ok " if ok else "FAIL", n0, n1))
    if not ok:
        fails.append("ast")
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    S = verify(1.0, 0.20)
    print("theta_mean(Fo=0.2, Bi=1) = %.12f" % S.theta_mean(0.2))
    print("theta(0,0)               = %.12f" % S.theta(0.0, 0.0, 0.2))
    print("theta(1,0)               = %.12f" % S.theta(1.0, 0.0, 0.2))
    print("theta(0,1)               = %.12f" % S.theta(0.0, 1.0, 0.2))
