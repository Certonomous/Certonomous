#!/usr/bin/env python3
"""T19's analytic reference, DERIVED -- never transcribed from a page.

FULLY DEVELOPED LAMINAR FLOW AND HEAT TRANSFER BETWEEN PARALLEL PLATES
(the PLANAR partner of T1c's axisymmetric pipe).

THE GENERIC DUCT.  Both the parallel-plate channel and the round pipe are the
same one-dimensional problem with a geometry index s: the transverse Laplacian
is (1/xi^s) d/dxi (xi^s d/dxi) on the half-domain xi in [0,1], with symmetry at
xi = 0 and the wall at xi = 1.

    s = 0  parallel plates, xi = distance from the mid-plane / half-gap a,
           full gap b = 2a, hydraulic diameter Dh = 2b = 4a
    s = 1  round pipe,      xi = r/R, a = R, Dh = 2R

    Dh = 4a/(1+s) in both.

EVERYTHING BELOW IS COMPUTED FOR GENERAL s AND THEN CHECKED AT s = 1 AGAINST
T1c's REGISTERED PIPE NUMBERS, WHICH THIS MODULE DID NOT COMPUTE
(docs/campaigns/T-family/T1_FORCED_CONVECTION_CANON_PREREGISTRATION.md,
verification/runs/T-family/T1_runs/L_q_c/CASE.txt):

    f.Re    = 64          Nu (uniform q") = 48/11 = 4.3636364
    Nu (uniform T_s) = 3.6567934

A module that gets the plate numbers by a route that cannot reproduce the pipe
numbers is refused.  This is the same discipline T14 used against T11.

1. VELOCITY AND f.Re -- CLOSED FORM.
   (1/xi^s)(xi^s u')' = (a^2/mu) dp/dx  gives  u = u_max (1 - xi^2) with
   u_max = (-dp/dx) a^2 / (2(1+s) mu), and u_max/ubar = (s+3)/2.
   Force balance and the definition f = (-dp/dx) Dh / (rho ubar^2 / 2) give

       f.Re = 32 (s+3)/(1+s)

   s = 0 -> 96 (parallel plates);  s = 1 -> 64 (pipe, T1c's registered value).

2. Nu FOR UNIFORM WALL HEAT FLUX (the H boundary condition) -- QUADRATURE.
   Fully developed with uniform q": dT/dx is a constant K, and
       (1/xi^s)(xi^s T')' = K u/ubar
   is integrated twice from the symmetry plane.  With
       T'(1) = wall gradient,  T_m = INT xi^s (u/ubar) T / INT xi^s (u/ubar),
       Nu = T'(1) (4/(1+s)) / (T(1) - T_m)
   s = 1 must return 48/11; s = 0 returns 140/17 = 8.2352941176, and this
   module CHECKS the plate value against that closed form as well, because
   140/17 is itself derivable in closed form from the same quadrature.

3. Nu FOR UNIFORM WALL TEMPERATURE (the T boundary condition) -- EIGENVALUE.
       (1/xi^s)(xi^s psi')' + Lambda (u/ubar) psi = 0,  psi'(0) = 0, psi(1) = 0
   is discretised conservatively on cell centres and its lowest eigenvalue found
   by inverse iteration with a tridiagonal (Thomas) solve -- no third-party
   dependency.  Nu is formed from the converged eigenfunction and RICHARDSON
   EXTRAPOLATED over two ODE meshes (M and 2M, error O(h^2)).
   s = 1 must return 3.6567934 (T1c's registered value); s = 0 returns the
   plate value this rung grades.

VERIFICATION IS BY ROUTE B: the computed profiles are differentiated on their
own output and must satisfy their own ODEs and boundary conditions; the two
independent quadratures of the mean must agree; and the s = 1 cross-checks
above must hold to 1e-7 relative or the module REFUSES.  A selftest plants a
1 percent error into the velocity profile and requires the refusal to fire.

NO `assert` STATEMENT IN THIS FILE (L-332).  Every refusal is sys.exit(2).
"""
import sys

EXIT_REFUSE = 2

# T1c's registered pipe numbers -- this module did not compute them.
T1C_REGISTERED = dict(fRe=64.0, Nu_q=48.0 / 11.0, Nu_Ts=3.6567934)
# The closed-form plate value for uniform q", used only as a second opinion on
# the quadrature route (the quadrature is the referent, not this constant).
PLATE_NU_H_CLOSED_FORM = 140.0 / 17.0


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def u_over_ubar(xi, s, mutate=1.0):
    """u/ubar = ((s+3)/2)(1 - xi^2).  `mutate` exists ONLY for the selftest."""
    return mutate * 0.5 * (s + 3.0) * (1.0 - xi * xi)


def f_Re(s):
    """32 (s+3)/(1+s):  96 for plates, 64 for the pipe."""
    return 32.0 * (s + 3.0) / (1.0 + s)


def _simpson(vals, h):
    n = len(vals) - 1
    if n % 2:
        refuse("Simpson needs an even number of intervals (got %d)" % n)
    tot = vals[0] + vals[-1]
    for i in range(1, n):
        tot += (4.0 if i % 2 else 2.0) * vals[i]
    return tot * h / 3.0


def nu_uniform_flux(s, M=4000, mutate=1.0):
    """Nu for uniform wall heat flux, by double quadrature of the fully
    developed energy equation.  K is set to 1: Nu is scale-free."""
    h = 1.0 / M
    xs = [i * h for i in range(M + 1)]
    # T'(xi) = xi^-s INT_0^xi t^s U(t) dt   (regular at xi = 0)
    inner = [0.0] * (M + 1)
    acc = 0.0
    # THE FIRST TRAPEZOID STARTS AT THE INTEGRAND'S VALUE AT xi = 0, NOT AT ZERO.
    # For s = 1 the integrand vanishes there and the distinction is invisible; for
    # s = 0 it is 3/2, and starting from zero makes the whole quadrature FIRST
    # order (measured: the plate Nu converged at O(h) and missed 140/17 by 5.4e-05
    # at M = 4000, while the pipe was already at 5.7e-09).
    prev = (xs[0] ** s) * u_over_ubar(xs[0], s, mutate)
    for i in range(1, M + 1):
        cur = (xs[i] ** s) * u_over_ubar(xs[i], s, mutate)
        acc += 0.5 * (prev + cur) * h
        prev = cur
        inner[i] = acc
    dT = [0.0] * (M + 1)
    for i in range(1, M + 1):
        dT[i] = inner[i] / (xs[i] ** s) if s else inner[i]
    # T(xi), T(0) = 0
    T = [0.0] * (M + 1)
    acc = 0.0
    for i in range(1, M + 1):
        acc += 0.5 * (dT[i - 1] + dT[i]) * h
        T[i] = acc
    w = [(xs[i] ** s) * u_over_ubar(xs[i], s, mutate) for i in range(M + 1)]
    Tm = _simpson([w[i] * T[i] for i in range(M + 1)], h) / _simpson(w, h)
    return dT[M] * (4.0 / (1.0 + s)) / (T[M] - Tm)


def _thomas(a, b, c, d):
    """Solve a tridiagonal system in place-free form (Thomas algorithm)."""
    n = len(d)
    cp = [0.0] * n
    dp = [0.0] * n
    cp[0] = c[0] / b[0]
    dp[0] = d[0] / b[0]
    for i in range(1, n):
        m = b[i] - a[i] * cp[i - 1]
        cp[i] = c[i] / m
        dp[i] = (d[i] - a[i] * dp[i - 1]) / m
    x = [0.0] * n
    x[-1] = dp[-1]
    for i in range(n - 2, -1, -1):
        x[i] = dp[i] - cp[i] * x[i + 1]
    return x


def _nu_uniform_T_at(s, M, mutate=1.0):
    """One ODE mesh: conservative finite volumes on cell centres, lowest
    eigenvalue by inverse iteration."""
    h = 1.0 / M
    xc = [(i + 0.5) * h for i in range(M)]
    xf = [i * h for i in range(M + 1)]           # faces, xf[0] = 0 (symmetry), xf[M] = 1 (wall)
    U = [u_over_ubar(x, s, mutate) for x in xc]
    B = [(xc[i] ** s) * U[i] for i in range(M)]
    # A' psi = Lambda B psi, with A' = -(1/xi^s)(xi^s psi')' in conservative form,
    # multiplied through by xi_i^s h so the operator is symmetric.
    lo = [0.0] * M
    di = [0.0] * M
    up = [0.0] * M
    for i in range(M):
        left = (xf[i] ** s) / h if i > 0 else 0.0            # xf[0]^s = 0 for s=1; for s=0 the
        if i == 0:
            left = 0.0                                        # symmetry face carries no flux
        right = (xf[i + 1] ** s) / h if i < M - 1 else (xf[M] ** s) / (0.5 * h)
        lo[i] = -left
        up[i] = -right if i < M - 1 else 0.0
        di[i] = left + right
    # inverse iteration on A'^-1 B
    v = [1.0] * M
    lam = 0.0
    for _ in range(400):
        rhs = [B[i] * v[i] for i in range(M)]
        x = _thomas(lo, di, up, rhs)
        nrm = max(abs(t) for t in x)
        if nrm == 0.0:
            refuse("inverse iteration collapsed")
        x = [t / nrm for t in x]
        newlam = 1.0 / nrm
        if abs(newlam - lam) <= 1e-15 * abs(newlam):
            v = x
            lam = newlam
            break
        v, lam = x, newlam
    psi = v
    if psi[0] < 0:
        psi = [-t for t in psi]
    dpsi_wall = (0.0 - psi[M - 1]) / (0.5 * h)
    num = sum(B[i] * psi[i] for i in range(M)) * h
    den = sum(B[i] for i in range(M)) * h
    psi_m = num / den
    return abs(dpsi_wall) * (4.0 / (1.0 + s)) / psi_m


def nu_uniform_T(s, M=4000, mutate=1.0):
    """RICHARDSON EXTRAPOLATED over two ODE meshes (error O(h^2))."""
    n1 = _nu_uniform_T_at(s, M, mutate)
    n2 = _nu_uniform_T_at(s, 2 * M, mutate)
    return n2 + (n2 - n1) / 3.0


def verify(mutate=1.0, tol_cross=1e-7, quiet=False):
    """ROUTE B + the s = 1 cross-checks against T1c's registered pipe numbers."""
    # (a) the velocity profile satisfies its own ODE and the no-slip wall
    for s in (0, 1):
        hh = 1e-4
        worst = 0.0
        for xi in (0.2, 0.5, 0.8):
            up = (u_over_ubar(xi + hh, s, mutate) - u_over_ubar(xi - hh, s, mutate)) / (2 * hh)
            upp = (u_over_ubar(xi + hh, s, mutate) - 2 * u_over_ubar(xi, s, mutate)
                   + u_over_ubar(xi - hh, s, mutate)) / (hh * hh)
            # (1/xi^s)(xi^s u')' = u'' + s u'/xi must be the constant -2(s+3)/2 * ... :
            lhs = upp + (s * up / xi if s else 0.0)
            worst = max(worst, abs(lhs - (-(s + 3.0) * (1.0 + s))))
        if worst > 1e-6:
            refuse("Route B: u/ubar does not satisfy its own ODE at s=%d (worst %.3e)" % (s, worst))
        if abs(u_over_ubar(1.0, s, mutate)) > 1e-14 * max(1.0, abs(mutate)):
            refuse("Route B: u/ubar is not zero at the wall at s=%d" % s)
    # (b) the bulk mean of u/ubar is 1 by construction -- an independent quadrature
    for s in (0, 1):
        M = 2000
        h = 1.0 / M
        xs = [i * h for i in range(M + 1)]
        w = [xs[i] ** s for i in range(M + 1)]
        num = _simpson([w[i] * u_over_ubar(xs[i], s, mutate) for i in range(M + 1)], h)
        den = _simpson(w, h)
        if abs(num / den - 1.0) > 1e-9:
            refuse("Route B: the bulk mean of u/ubar at s=%d is %.12f, not 1 -- the profile is "
                   "not normalised (this is the NORMALISATION control: a uniform scaling of the "
                   "velocity is invisible to the ODE and to the wall condition, and is caught here)"
                   % (s, num / den))
    # (c) CROSS-CHECK at s = 1 against T1c's registered pipe numbers
    got = dict(fRe=f_Re(1), Nu_q=nu_uniform_flux(1, mutate=mutate), Nu_Ts=nu_uniform_T(1, mutate=mutate))
    for k, want in T1C_REGISTERED.items():
        if abs(got[k] - want) > tol_cross * abs(want):
            refuse("CROSS-CHECK against T1c's registered PIPE %s FAILED: this module's generic-duct "
                   "route gives %.10f, T1c registers %.10f (relative %.3e > %.1e). A route that "
                   "cannot reproduce the pipe is not used for the plates."
                   % (k, got[k], want, abs(got[k] - want) / abs(want), tol_cross))
    # (d) the plate uniform-flux value against its own closed form 140/17
    nh = nu_uniform_flux(0, mutate=mutate)
    if abs(nh - PLATE_NU_H_CLOSED_FORM) > 1e-7 * PLATE_NU_H_CLOSED_FORM:
        refuse("the quadrature's plate uniform-flux Nu %.10f disagrees with the closed form "
               "140/17 = %.10f by %.3e relative" % (nh, PLATE_NU_H_CLOSED_FORM,
                                                    abs(nh - PLATE_NU_H_CLOSED_FORM) / PLATE_NU_H_CLOSED_FORM))
    # (e) the eigenvalue route's own mesh convergence: the two ODE meshes must
    # differ by a second-order amount, not an arbitrary one
    a1 = _nu_uniform_T_at(0, 2000, mutate)
    a2 = _nu_uniform_T_at(0, 4000, mutate)
    a3 = _nu_uniform_T_at(0, 8000, mutate)
    p = None
    if abs(a2 - a3) > 0:
        r = (a1 - a2) / (a2 - a3)
        p = r
        if not (3.0 <= r <= 5.0):
            refuse("the uniform-T eigenvalue route is not second order in its own ODE mesh "
                   "(ratio %.3f, expected near 4)" % r)
    out = dict(fRe_plates=f_Re(0), Nu_H_plates=nh, Nu_T_plates=nu_uniform_T(0, mutate=mutate),
               fRe_pipe=got["fRe"], Nu_H_pipe=got["Nu_q"], Nu_T_pipe=got["Nu_Ts"],
               ode_mesh_ratio=p)
    if not quiet:
        print("  exact_t19.verify: profile ODE ok; bulk mean normalised; ODE-mesh ratio %.3f; "
              "CROSS-CHECK vs T1c registered pipe values PASS "
              "(f.Re %.8f vs 64, Nu_q %.8f vs 4.3636364, Nu_Ts %.8f vs 3.6567934)"
              % (p, got["fRe"], got["Nu_q"], got["Nu_Ts"]))
        print("  PLATES: f.Re = %.10f   Nu_H = %.10f   Nu_T = %.10f"
              % (out["fRe_plates"], out["Nu_H_plates"], out["Nu_T_plates"]))
    return out


def selftest():
    fails = []
    out = verify()
    for label, mut in (("u/ubar planted 1 percent wrong", 1.01),
                       ("u/ubar planted 1e-6 wrong", 1.0 + 1e-6)):
        fired = False
        try:
            verify(mutate=mut, quiet=True)
        except SystemExit as e:
            fired = (e.code == EXIT_REFUSE)
        print("  [%s] %-32s -> verify REFUSES (exit 2)" % ("ok " if fired else "FAIL", label))
        if not fired:
            fails.append(label)
    ok = abs(out["fRe_plates"] - 96.0) < 1e-12
    print("  [%s] plate f.Re = %.12f (exactly 96 by the closed form)" % ("ok " if ok else "FAIL", out["fRe_plates"]))
    if not ok:
        fails.append("fre")
    ok = abs(out["Nu_H_plates"] - 140.0 / 17.0) < 1e-7
    print("  [%s] plate Nu_H = %.10f (140/17 = %.10f)" % ("ok " if ok else "FAIL", out["Nu_H_plates"], 140.0 / 17.0))
    if not ok:
        fails.append("nuh")
    ok = 7.5 < out["Nu_T_plates"] < 7.6
    print("  [%s] plate Nu_T = %.10f (the parallel-plate Graetz limit)" % ("ok " if ok else "FAIL", out["Nu_T_plates"]))
    if not ok:
        fails.append("nut")
    import ast
    src = open(__file__).read()
    n0 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src)))
    n1 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src + "\nassert 1\n")))
    ok = (n0 == 0 and n1 == 1)
    print("  [%s] AST assert count = %d (planted control: %d)" % ("ok " if ok else "FAIL", n0, n1))
    if not ok:
        fails.append("ast")
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    o = verify()
    for k in sorted(o):
        print("%-14s %s" % (k, o[k]))
