#!/usr/bin/env python3
"""T15 analytic referent: Morton, Taylor & Turner (1956) top-hat plume theory,
DERIVED HERE from the conservation equations, never transcribed from a table.

Top-hat conventions, b(z) plume radius, w(z) vertical velocity, g'(z) reduced
gravity, entrainment dQ/dz = 2 pi alpha b w:

    Q = pi b^2 w          (volume flux,   m^3/s)
    M = pi b^2 w^2        (momentum flux, m^4/s^2)
    F = pi b^2 w g' = F0  (buoyancy flux, m^4/s^3 -- CONSERVED, unstratified)

    dQ/dz = 2 alpha sqrt(pi M)        (entrainment)
    dM/dz = F Q / M                   (buoyancy drives momentum)
    dF/dz = 0                         (unstratified environment)

Similarity solution with a virtual origin at z = z0:

    b(z)  = c_b (z - z0),   c_b = 6 alpha / 5
    w(z)  = c_w (z - z0)^(-1/3),  c_w = ( 3 F0 / (4 pi c_b^2) )^(1/3)
    g'(z) = c_g (z - z0)^(-5/3),  c_g = (4/3) c_w^2
    Q(z)  = pi c_b^2 c_w (z - z0)^(+5/3)
    M(z)  = pi c_b^2 c_w^2 (z - z0)^(+4/3)

THE THREE GRADED EXPONENTS -1/3, -5/3, +5/3 ARE EXACT CONSEQUENCES OF THE
CONSERVATION EQUATIONS AND CARRY NO alpha.  The RADIUS law does carry alpha
(c_b = 6 alpha / 5) and is therefore the row on which a closure's entrainment
error shows up -- T8_PREREGISTRATION.md section 2, registered prediction P1.

VIRTUAL ORIGIN, AND A CORRECTION TO THE PARENT'S PROSE.
T8_PREREGISTRATION.md section 12 S2 states "A source with Gamma_0 = 1 is pure
from z = 0, so the virtual origin sits at the source".  THAT PROSE IS WRONG FOR
A SOURCE OF FINITE RADIUS and this module says so with the arithmetic:
b(0) = b0 requires z0 = -b0 / c_b, which for b0 = 0.1 m and alpha = 0.12 is
z0 = -0.694444 m -- the virtual origin sits 0.694 m BELOW the source plane.
Route B checks it: c_w (-z0)^(-1/3) must reproduce the registered source
velocity w0 = 0.6 m/s EXACTLY, and it does (B3).  T8's own INSTRUMENT refits z0
from the radius (section 12 S4) and is unaffected; only the prose is wrong.

ROUTE B (run by verify(); every failure is sys.exit(2)):
 (B1) the closed form satisfies the three ODEs -- residuals by centred
      differences on the closed form itself, at two stencil widths, falling as
      h^2 (ratio required in [3, 5]);
 (B2) the three flux definitions are mutually consistent: Q^2/(pi M) = b^2,
      M/Q = w, F/Q = g', to 1e-14 relative;
 (B3) the registered source condition is ON the solution: with
      z0 = -b0/c_b, w(0) == w0 and g'(0) == gprime0 to 1e-12 relative, and
      F0 recomputed from pi b0^2 w0 gprime0 matches the registered F0;
 (B4) INDEPENDENT NUMERICAL ROUTE: the ODE system integrated by RK4 from the
      source reproduces the closed form to 1e-9 relative at every station, and
      a log-log fit of the integrated w, g', Q on (z - z0) returns the
      exponents to 1e-9;
 (B5) PLANTED MUTATION: c_b mutated by 1 percent is REFUSED by B3, and an
      exponent mutated by 1 percent is REFUSED by B4.

NO `assert` STATEMENT IN THIS FILE (L-332).  Every refusal is sys.exit(2).
Exit: 0 verified, 2 REFUSAL.
"""
import math
import sys

EXIT_OK, EXIT_REFUSE = 0, 2

# exact exponents -- consequences of the conservation equations, no alpha
N_W = -1.0 / 3.0
N_T = -5.0 / 3.0
N_Q = +5.0 / 3.0
N_B = +1.0


def refuse(msg):
    sys.stderr.write("REFUSE: %s\n" % msg)
    sys.exit(EXIT_REFUSE)


class MTT(object):
    """The closed-form pure plume for buoyancy flux F0 and entrainment alpha,
    with the virtual origin placed so that b(0) == b0."""

    def __init__(self, F0, alpha, b0, c_b_mutation=1.0):
        self.F0 = float(F0)
        self.alpha = float(alpha)
        self.b0 = float(b0)
        self.c_b = c_b_mutation * 6.0 * self.alpha / 5.0
        self.c_w = (3.0 * self.F0 / (4.0 * math.pi * self.c_b ** 2)) ** (1.0 / 3.0)
        self.c_g = (4.0 / 3.0) * self.c_w ** 2
        self.z0 = -self.b0 / self.c_b          # metres, NEGATIVE: below the source

    def zeta(self, z):
        return z - self.z0

    def b(self, z):
        return self.c_b * self.zeta(z)

    def w(self, z):
        return self.c_w * self.zeta(z) ** (-1.0 / 3.0)

    def gprime(self, z):
        return self.c_g * self.zeta(z) ** (-5.0 / 3.0)

    def dT(self, z, g, beta):
        return self.gprime(z) / (g * beta)

    def Q(self, z):
        return math.pi * self.c_b ** 2 * self.c_w * self.zeta(z) ** (5.0 / 3.0)

    def M(self, z):
        return math.pi * self.c_b ** 2 * self.c_w ** 2 * self.zeta(z) ** (4.0 / 3.0)

    def F(self, z):
        return math.pi * self.b(z) ** 2 * self.w(z) * self.gprime(z)


def _ols(xs, ys):
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx <= 0.0:
        refuse("OLS: the abscissa has no spread")
    s = sxy / sxx
    c = my - s * mx
    syy = sum((y - my) ** 2 for y in ys)
    r2 = 1.0 if syy == 0.0 else 1.0 - sum((y - (s * x + c)) ** 2 for x, y in zip(xs, ys)) / syy
    return s, c, r2


def fit_exponent(zs, vals, z0):
    """OLS of ln(value) on ln(z - z0).  REFUSES on a non-positive operand
    rather than dropping the station silently."""
    xs, ys = [], []
    for z, v in zip(zs, vals):
        zz = z - z0
        if zz <= 0.0 or v <= 0.0:
            return None, "non-positive operand at z = %.6f (z - z0 = %.6g, value = %.6g)" % (z, zz, v)
        xs.append(math.log(zz))
        ys.append(math.log(v))
    s, _c, r2 = _ols(xs, ys)
    return dict(exponent=s, r2=r2, n=len(xs)), ""


def fit_radius(zs, bs):
    """b(z) = s (z - z0): slope s (GRADED as db/dz) and x-intercept z0."""
    s, c, r2 = _ols(list(zs), list(bs))
    if s == 0.0:
        refuse("radius fit slope is exactly zero; the virtual origin is undefined")
    return dict(slope=s, z0=-c / s, r2=r2, alpha=(5.0 / 6.0) * s)


# ------------------------------------------------------------------ ROUTE B
def _ode_residuals(m, z, h):
    """Centred differences of the CLOSED FORM against the three ODEs."""
    dQ = (m.Q(z + h) - m.Q(z - h)) / (2 * h)
    dM = (m.M(z + h) - m.M(z - h)) / (2 * h)
    dF = (m.F(z + h) - m.F(z - h)) / (2 * h)
    r1 = dQ - 2.0 * m.alpha * math.sqrt(math.pi * m.M(z))
    r2 = dM - m.F0 * m.Q(z) / m.M(z)  # noqa: E501
    return abs(r1), abs(r2), abs(dF)


def _rk4(m, z_end, n=20000):
    """INDEPENDENT numerical route: integrate dQ/dz, dM/dz from the source."""
    Q = m.Q(0.0)
    M = m.M(0.0)
    h = z_end / n
    zz = 0.0
    out = []

    def d(Qv, Mv):
        return (2.0 * m.alpha * math.sqrt(math.pi * Mv), m.F0 * Qv / Mv)

    for i in range(n):
        k1 = d(Q, M)
        k2 = d(Q + 0.5 * h * k1[0], M + 0.5 * h * k1[1])
        k3 = d(Q + 0.5 * h * k2[0], M + 0.5 * h * k2[1])
        k4 = d(Q + h * k3[0], M + h * k3[1])
        Q += h * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]) / 6.0
        M += h * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]) / 6.0
        zz += h
        out.append((zz, Q, M))
    return out


def verify(F0, alpha, b0, w0, gprime0, quiet=False, mutate_c_b=1.0, mutate_exponent=1.0):
    fails = []
    # the buoyancy flux the REGISTERED source condition implies, computed here;
    # the registered F0 is checked against it in B3 rather than trusted.
    F0_exact = math.pi * b0 ** 2 * w0 * gprime0
    m = MTT(F0_exact, alpha, b0, c_b_mutation=mutate_c_b)
    say = (lambda *a: None) if quiet else (lambda *a: print(*a))

    # B1 -- ODE residuals of the closed form, two stencil widths, h^2 falling
    z = 3.0
    a1, a2, a3 = _ode_residuals(m, z, 1e-3)
    b1, b2, b3 = _ode_residuals(m, z, 5e-4)
    sc = max(abs(m.Q(z)), 1.0)
    ratios = []
    for (ca, cb, name) in ((a1, b1, "entrainment"), (a2, b2, "momentum")):
        if cb == 0.0:
            ratios.append(float("inf"))
        else:
            ratios.append(ca / cb)
    okB1 = (a1 / sc < 1e-6 and a2 < 1e-6 and a3 < 1e-9 and
            all(3.0 <= r <= 5.0 for r in ratios if r != float("inf")))
    if okB1:
        say("B1 ODE residuals at z=3: entrainment %.3e momentum %.3e dF/dz %.3e; h^2 ratios %s -> PASS"
            % (a1, a2, a3, ", ".join("%.3f" % r for r in ratios)))
    else:
        fails.append("B1 ODE residuals (%.3e, %.3e, %.3e; ratios %s)"
                     % (a1, a2, a3, ", ".join("%.3f" % r for r in ratios)))

    # B2 -- flux definitions mutually consistent
    worst = 0.0
    for z in (0.5, 1.0, 2.0, 3.0, 5.0, 8.0):
        worst = max(worst,
                    abs(m.Q(z) ** 2 / (math.pi * m.M(z)) - m.b(z) ** 2) / m.b(z) ** 2,
                    abs(m.M(z) / m.Q(z) - m.w(z)) / m.w(z),
                    abs(m.F0 / m.Q(z) - m.gprime(z)) / m.gprime(z))
    if worst < 1e-14:
        say("B2 flux identities Q^2/(pi M)=b^2, M/Q=w, F/Q=g': worst relative %.3e -> PASS" % worst)
    else:
        fails.append("B2 flux identities, worst relative %.3e" % worst)

    # B3 -- the registered source condition is ON the solution
    dw = abs(m.w(0.0) - w0) / w0
    dg = abs(m.gprime(0.0) - gprime0) / gprime0
    dF = abs(F0_exact - F0) / F0
    if dw < 1e-12 and dg < 1e-12 and dF < 1e-9:
        say("B3 source ON the similarity solution: z0 = %.9f m (BELOW the source plane), "
            "w(0)=%.9f vs w0=%.9f (rel %.2e), g'(0) rel %.2e, F0 rel %.2e -> PASS"
            % (m.z0, m.w(0.0), w0, dw, dg, dF))
    else:
        fails.append("B3 source condition (w rel %.3e, g' rel %.3e, F0 rel %.3e)" % (dw, dg, dF))

    # B4 -- independent RK4 route reproduces the closed form and the exponents
    traj = _rk4(m, 8.0, n=20000)
    worst = 0.0
    zs, ws, gs, qs = [], [], [], []
    for (zz, Q, M) in traj[::200]:
        if zz < 0.5:
            continue
        w_num = M / Q
        g_num = m.F0 / Q
        worst = max(worst, abs(w_num - m.w(zz)) / m.w(zz), abs(Q - m.Q(zz)) / m.Q(zz))
        zs.append(zz)
        ws.append(w_num * zz ** (mutate_exponent - 1.0))
        gs.append(g_num)
        qs.append(Q)
    fw, _ = fit_exponent(zs, ws, m.z0)
    fg, _ = fit_exponent(zs, gs, m.z0)
    fq, _ = fit_exponent(zs, qs, m.z0)
    if fw is None or fg is None or fq is None:
        fails.append("B4 exponent fit refused its own operand")
    else:
        de = max(abs(fw["exponent"] - N_W), abs(fg["exponent"] - N_T), abs(fq["exponent"] - N_Q))
        if worst < 1e-9 and de < 1e-9:
            say("B4 independent RK4 route: worst |num-closed|/closed %.3e; fitted exponents "
                "n_w %.12f n_T %.12f n_Q %.12f (worst deviation %.3e) -> PASS"
                % (worst, fw["exponent"], fg["exponent"], fq["exponent"], de))
        else:
            fails.append("B4 numerical route (worst field %.3e, worst exponent deviation %.3e)" % (worst, de))

    if fails:
        return None, fails
    return m, []


def selftest():
    import ast
    F0, alpha, b0, w0, gp0 = 0.01302881305, 0.12, 0.1, 0.6, 0.6912
    fails = []
    print("mtt_t15 selftest:")
    m, f = verify(F0, alpha, b0, w0, gp0)
    ok = (m is not None and not f)
    print("  [%s] ROUTE B B1-B4 on the registered constants" % ("ok " if ok else "FAIL"))
    if not ok:
        fails.append("routeB: %s" % f)
    # B5a -- c_b mutated 1 percent must be REFUSED by B3
    m2, f2 = verify(F0, alpha, b0, w0, gp0, quiet=True, mutate_c_b=1.01)
    fired = (m2 is None) and any(x.startswith("B3") for x in f2)
    print("  [%s] PLANTED 1 percent c_b mutation -> B3 REFUSES (%s)"
          % ("ok " if fired else "FAIL", "; ".join(f2) if f2 else "accepted BLIND"))
    if not fired:
        fails.append("B5a")
    # B5b -- an exponent mutated by 1 percent must be REFUSED by B4
    m3, f3 = verify(F0, alpha, b0, w0, gp0, quiet=True, mutate_exponent=1.01)
    fired = (m3 is None) and any(x.startswith("B4") for x in f3)
    print("  [%s] PLANTED 1 percent exponent mutation -> B4 REFUSES (%s)"
          % ("ok " if fired else "FAIL", "; ".join(f3) if f3 else "accepted BLIND"))
    if not fired:
        fails.append("B5b")
    # the readers are exact on the analytic profile
    mm = MTT(F0, alpha, b0)
    zs = [0.1 * i for i in range(20, 51)]          # z/D = 10.0 .. 25.0
    fw, why = fit_exponent(zs, [mm.w(z) for z in zs], mm.z0)
    fb = fit_radius(zs, [mm.b(z) for z in zs])
    ok = (fw is not None and abs(fw["exponent"] - N_W) < 1e-12
          and abs(fb["slope"] - 6.0 * alpha / 5.0) < 1e-12 and abs(fb["z0"] - mm.z0) < 1e-9)
    print("  [%s] readers exact on the analytic profile over z/D in [10,25]: n_w %.14f, "
          "db/dz %.14f (6 alpha/5 = %.14f), z0 %.9f m"
          % ("ok " if ok else "FAIL", fw["exponent"] if fw else float("nan"),
             fb["slope"], 6.0 * alpha / 5.0, fb["z0"]))
    if not ok:
        fails.append("readers")
    # the exponent fit REFUSES a non-positive operand rather than dropping it
    bad, why = fit_exponent([0.1, 0.2], [1.0, 1.0], 0.5)
    ok = (bad is None and "non-positive" in why)
    print("  [%s] fit_exponent on z - z0 <= 0 -> refuses with a reason (%s)" % ("ok " if ok else "FAIL", why[:48]))
    if not ok:
        fails.append("operand")
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
        m, f = verify(0.01302881305, 0.12, 0.1, 0.6, 0.6912)
        if f:
            refuse("route B failed: %s" % "; ".join(f))
        print("ROUTE B VERIFIED (B1 B2 B3 B4 each printed from inside its own branch)")
        return EXIT_OK
    print(__doc__)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
