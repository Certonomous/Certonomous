#!/usr/bin/env python3
"""T11's analytic reference, DERIVED -- never transcribed from a page.

This lab's established method for an EXACT-tier rung is to reproduce the
reference from the governing relations inside the rung's own module, by routes
that share no code, and to REFUSE when they disagree.  Precedents on disk:
exact_laminar_pipe.py (T1c), exact_t9a.py (T9a), exact_t10a.py (T10a); and
T1_FORCED_CONVECTION_CANON_PREREGISTRATION.md section 2.1: "reproduced in the
rung's own comparator from the derivation, not typed in from a textbook page."
A derivation transcribes nothing and therefore cannot inherit a transcription
error.

THE SOLUTION.  One-dimensional transient conduction in a plane wall of
half-thickness L, insulated (or symmetric) at x = 0, convective at x = L, with
constant properties and a uniform initial temperature:

    theta(x, Fo) = (T - T_inf)/(T_0 - T_inf)
                 = SUM_n  C_n exp(-zeta_n^2 Fo) cos(zeta_n x/L)

    C_n = 4 sin(zeta_n) / (2 zeta_n + sin(2 zeta_n))
    zeta_n tan(zeta_n) = Bi        (the transcendental eigenvalue condition)
    Fo  = alpha t / L^2 ,   Bi = h L / k

TWO ROUTES, AND THEY ARE NOT THE SAME KIND OF CHECK.  Route B is NOT a second
algebraic rearrangement of Route A -- that would only re-check arithmetic.  It
asks the stronger question: DOES THE EXPRESSION SOLVE THE PROBLEM?  Route A
builds the series; Route B verifies numerically, by finite differences on
Route A's own output, that it satisfies the heat equation, both boundary
conditions and the initial condition.  A series with a wrong coefficient, a
wrong eigenvalue or a wrong sign fails Route B even though its algebra is
self-consistent.

THE LUMPED LIMIT IS HYGIENE, NOT INDEPENDENCE.  As Bi -> 0 this series must
collapse to exp(-Bi Fo).  That is a limit OF THIS SERIES and proves only that
the algebra is right; it cannot prove the series is the right series.  It is
reported as a SELF-CONSISTENCY control and is never presented as independent
corroboration.  (Presenting a self-consistency check as independence is the
same error as a planted control that plants into the wrong channel.)

No `assert` appears in this file.  Every failure is an explicit sys.exit(2).
"""
import math
import sys

EXIT_REFUSE = 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def eigenvalues(Bi, n_terms=80):
    """Roots of zeta tan(zeta) = Bi, one per branch [n*pi, (n+1/2)*pi).

    Bisection, not Newton: the function has a pole at the top of every branch
    and Newton walks into it.  The bracket is chosen so exactly one root lies
    inside and the sign change is guaranteed.
    """
    if Bi <= 0:
        refuse("Bi must be positive; got %r" % Bi)
    out = []
    for n in range(n_terms):
        lo = n * math.pi + 1e-15
        hi = (n + 0.5) * math.pi - 1e-12
        flo = lo * math.tan(lo) - Bi
        fhi = hi * math.tan(hi) - Bi
        if flo * fhi > 0:
            refuse("no sign change on branch %d for Bi=%g: the bracket is "
                   "wrong and a root would be missed silently" % (n, Bi))
        for _ in range(300):
            m = 0.5 * (lo + hi)
            if m * math.tan(m) - Bi < 0:
                lo = m
            else:
                hi = m
        out.append(0.5 * (lo + hi))
    return out


def coeffs(zetas):
    return [4.0 * math.sin(z) / (2.0 * z + math.sin(2.0 * z)) for z in zetas]


def theta(xstar, Fo, Bi, n_terms=80):
    """ROUTE A -- the eigenfunction expansion.  xstar = x/L in [0, 1]."""
    Z = eigenvalues(Bi, n_terms)
    C = coeffs(Z)
    return sum(c * math.exp(-z * z * Fo) * math.cos(z * xstar)
               for z, c in zip(Z, C))


def theta_mean(Fo, Bi, n_terms=80):
    """Volume-averaged theta over the wall -- the stored-energy quantity.

    MESH-INDEPENDENT BY CONSTRUCTION, which is why it is the primary graded
    row: a pointwise value has to be interpolated to a fixed x*, and the
    interpolation error would enter the Roache triple alongside the
    discretisation error it is supposed to isolate.  Integrating
    cos(zeta x*) over x* in [0,1] gives sin(zeta)/zeta.
    """
    Z = eigenvalues(Bi, n_terms)
    C = coeffs(Z)
    return sum(c * math.exp(-z * z * Fo) * math.sin(z) / z
               for z, c in zip(Z, C))


def theta_mean_route_b(Fo, Bi, n_terms=80, n_quad=20001):
    """ROUTE B for the mean: Simpson quadrature of Route A's own theta(x*).
    Shares none of the closed-form integration."""
    n = n_quad if n_quad % 2 else n_quad + 1
    h = 1.0 / (n - 1)
    tot = 0.0
    for i in range(n):
        x = i * h
        w = 1.0 if i in (0, n - 1) else (4.0 if i % 2 else 2.0)
        tot += w * theta(x, Fo, Bi, n_terms)
    return tot * h / 3.0


def route_b_residuals(Bi, Fo, n_terms=80, h=1e-5):
    """ROUTE B -- does Route A's expression SOLVE the problem?

    In (x*, Fo) variables the heat equation is  d(theta)/dFo = d2(theta)/dx*2,
    the insulated face is  d(theta)/dx* = 0 at x* = 0, and the convective face
    is  -d(theta)/dx* = Bi theta  at x* = 1.  All four residuals are formed by
    central differences on Route A's own output and share none of its algebra.
    """
    def th(x, F):
        return theta(x, F, Bi, n_terms)

    x0 = 0.5                                   # interior point for the PDE
    d2 = (th(x0 + h, Fo) - 2 * th(x0, Fo) + th(x0 - h, Fo)) / (h * h)
    dt = (th(x0, Fo + h) - th(x0, Fo - h)) / (2 * h)
    pde = abs(dt - d2) / max(abs(d2), 1e-30)

    # insulated at x*=0: one-sided, because x<0 is outside the domain
    ins = abs((th(h, Fo) - th(0.0, Fo)) / h)

    # convective at x*=1: -dtheta/dx* = Bi*theta
    dx1 = (th(1.0, Fo) - th(1.0 - h, Fo)) / h
    rob = abs(-dx1 - Bi * th(1.0, Fo)) / max(abs(Bi * th(1.0, Fo)), 1e-30)

    # initial condition: theta(x*, 0) = 1
    ic = abs(th(0.37, 1e-9) - 1.0)
    # the closed-form mean against Simpson quadrature of the same theta
    ma = theta_mean(Fo, Bi, n_terms)
    mb = theta_mean_route_b(Fo, Bi, n_terms, 2001)
    mean = abs(ma - mb) / max(abs(ma), 1e-30)
    return dict(pde=pde, insulated=ins, robin=rob, initial=ic, mean=mean)


def verify(Bi, Fo, n_terms=80, tol_pde=1e-4, tol_robin=1e-3,
           tol_ins=1e-4, tol_ic=5e-3, quiet=False):
    """Run Route B against Route A and REFUSE on disagreement."""
    r = route_b_residuals(Bi, Fo, n_terms)
    bad = []
    if r["pde"] > tol_pde:
        bad.append("heat equation residual %.3e > %.1e" % (r["pde"], tol_pde))
    if r["insulated"] > tol_ins:
        bad.append("insulated-face residual %.3e > %.1e" % (r["insulated"], tol_ins))
    if r["robin"] > tol_robin:
        bad.append("convective-face residual %.3e > %.1e" % (r["robin"], tol_robin))
    if r["initial"] > tol_ic:
        bad.append("initial-condition residual %.3e > %.1e" % (r["initial"], tol_ic))
    if r["mean"] > 1e-9:
        bad.append("closed-form mean vs quadrature %.3e > 1e-09" % r["mean"])
    if bad:
        refuse("ROUTE B REJECTS ROUTE A at Bi=%g Fo=%g: %s. The expansion does "
               "not solve the problem it claims to solve, so no T11 number "
               "derived from it is evidence." % (Bi, Fo, "; ".join(bad)))
    if not quiet:
        print("  ROUTE B (independent): PDE %.2e  insulated %.2e  robin %.2e  "
              "initial %.2e  mean-vs-quadrature %.2e -- all within tolerance" %
              (r["pde"], r["insulated"], r["robin"], r["initial"], r["mean"]))
    return r


def lumped_limit_selfcheck(quiet=False):
    """SELF-CONSISTENCY ONLY -- a limit of this same series, not independence.

    As Bi -> 0 the expansion must collapse to the lumped exponential
    exp(-Bi*Fo).  The difference must fall LINEARLY with Bi, because the lumped
    form is the O(Bi) truncation; a difference that does not shrink that way
    means the coefficients are wrong.
    """
    Fo = 5.0
    rows = []
    for Bi in (1e-3, 1e-4):
        s = theta(0.0, Fo, Bi, n_terms=3)
        lump = math.exp(-Bi * Fo)
        rows.append((Bi, s, lump, abs(s - lump) / lump))
    ratio = rows[0][3] / rows[1][3] if rows[1][3] else float("inf")
    if not (5.0 < ratio < 20.0):
        refuse("lumped-limit self-check: the difference fell by %.2fx for a 10x "
               "drop in Bi; a linear collapse was required" % ratio)
    if not quiet:
        for Bi, s, lump, d in rows:
            print("  self-consistency (NOT independence): Bi=%.0e series=%.10f "
                  "lumped=%.10f rel diff=%.2e" % (Bi, s, lump, d))
    return rows


if __name__ == "__main__":
    Bi = 1.0
    print("T11 analytic reference -- derived, then verified")
    print("Bi = %g" % Bi)
    for Fo in (0.05, 0.1, 0.2):
        verify(Bi, Fo)
    lumped_limit_selfcheck()
    print("\n  theta(x*, Fo) at Bi = 1:")
    for Fo in (0.05, 0.1, 0.2):
        print("    Fo=%.2f  centre %.10f  mid %.10f  surface %.10f  MEAN %.10f"
              % (Fo, theta(0.0, Fo, Bi), theta(0.5, Fo, Bi), theta(1.0, Fo, Bi),
                 theta_mean(Fo, Bi)))
