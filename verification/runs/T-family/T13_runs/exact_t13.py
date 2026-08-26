#!/usr/bin/env python3
"""T13's analytic reference, DERIVED -- never transcribed from a page.

NATURAL CONVECTION IN A VERTICAL SLOT, CONDUCTION REGIME (the Batchelor 1954
parallel-flow solution; the textbook exact solution of the Boussinesq
equations between two infinite vertical plates).

This lab sources EXACT-tier referents by DERIVATION inside the rung's own module
(exact_laminar_pipe.py for T1c, exact_t9a.py, exact_t10a.py, exact_t11.py;
T1_FORCED_CONVECTION_CANON_PREREGISTRATION.md section 2.1).  A derivation
transcribes nothing and therefore cannot inherit a transcription error.

THE PROBLEM.  Two infinite vertical plates a distance L apart, the plate at
x = 0 held at T_h and the plate at x = L at T_c, gravity g in the -y direction,
Boussinesq fluid of kinematic viscosity nu and expansion coefficient beta,
reference temperature T_ref = (T_h + T_c)/2.  Fully developed: nothing depends
on y, u_x = 0, v = v(x), T = T(x).

  energy:      v dT/dy = alpha d2T/dx2  ->  d2T/dx2 = 0
               T(x) = T_h - DeltaT * xi,         xi = x/L,  DeltaT = T_h - T_c
               so  T - T_ref = DeltaT (1/2 - xi)

  y-momentum:  0 = -dp/dy + nu d2v/dx2 + g beta (T - T_ref)
  x-momentum:  0 = -dp/dx                     ->  p = p(y)

  dp/dy must then be a constant; integrating the y-momentum equation across
  the gap with v(0) = v(L) = 0 (no slip) gives
      L dp/dy = nu [v'(L) - v'(0)] + g beta DeltaT L * 0
  and the ZERO-NET-FLOW condition  int_0^L v dx = 0  (a closed slot carries no
  net vertical mass flux) fixes dp/dy = 0: with v'' = -(g beta DeltaT / nu)
  (1/2 - xi) + dp/dy / nu, the only solution with v(0) = v(L) = 0 AND zero net
  flow is the one with dp/dy = 0, because the buoyancy term is antisymmetric
  about xi = 1/2 and so is its double integral, whereas a nonzero dp/dy adds a
  symmetric Poiseuille parabola whose integral is not zero.

  Write v = u_ref * phi(xi),  u_ref = g beta DeltaT L^2 / nu.  Then
      phi''(xi) = xi - 1/2
      phi'(xi)  = xi^2/2 - xi/2 + a
      phi(xi)   = xi^3/6 - xi^2/4 + a xi + b
      phi(0) = 0  ->  b = 0;   phi(1) = 0  ->  1/6 - 1/4 + a = 0  ->  a = 1/12
      phi(xi)   = xi^3/6 - xi^2/4 + xi/12 = (1/12) xi (1 - xi)(1 - 2 xi)
  Check: int_0^1 phi dxi = (1/12)(1/2 - 1 + 1/2) = 0  (zero net flow, verified
  numerically below).  So

      v(x) = (g beta DeltaT L^2 / (12 nu)) * xi (1 - xi)(1 - 2 xi).

  NON-DIMENSIONAL FORM.  Gr_L = g beta DeltaT L^3 / nu^2,  Ra_L = Gr_L Pr.
      v L / nu = Gr_L * phi(xi);   v / u_ref = phi(xi).
  Pr enters only through Ra; the conduction-regime profile is Pr-independent.

  THE MAXIMUM.  phi'(xi) = (1 - 6 xi + 6 xi^2)/12 = 0  ->
      xi* = 1/2 -+ sqrt(3)/6 = 0.21132487 (upflow, hot side), 0.78867513 (downflow)
  At xi* = 1/2 - sqrt(3)/6:  xi(1 - xi) = 1/4 - 3/36 = 1/6,  1 - 2 xi = 1/sqrt(3)
      phi_max = (1/12)(1/6)(1/sqrt(3)) = 1 / (72 sqrt(3)) = 8.0187537e-03
      v_max   = g beta DeltaT L^2 / (72 sqrt(3) nu) = u_ref / (72 sqrt(3))
  The profile is antisymmetric about xi = 1/2: v(1 - xi) = -v(xi).

  WALL HEAT FLUX.  q = k DeltaT / L on both walls (pure conduction), so
      Nu_L = q L / (k DeltaT) = 1  exactly.

WHERE IT HOLDS.  The parallel-flow solution is an EXACT solution of the steady
Boussinesq equations for the infinite slot at ANY Ra: v.grad(v) and v.grad(T)
vanish identically because nothing depends on y.  What limits it is (i)
STABILITY -- the conduction regime loses stability to stationary transverse
rolls at Gr_L of order 8e3 for Pr ~ 0.7 (Vest and Arpaci 1969, from the lane's
recollection; no paper on disk; NOT load-bearing: the rung measures its own
steadiness through the plateau control) -- and (ii) in a FINITE slot, the END
REGIONS, whose disturbance decays into the core like exp(-lambda y/L) with
lambda >= pi for the temperature (the slowest Fourier mode of the gap,
sin(pi xi) exp(-pi y/L)) and lambda ~ 4.2 for the Stokes velocity
(Papkovich-Fadle, lane's recollection, not load-bearing); at finite Peclet the
thermal rate is reduced, roughly to pi (sqrt(1 + (Pe/2pi)^2) - Pe/2pi) for a
uniformly advected mode.  T13 registers Ra_L = 100 (Pe_max = Pr Gr phi_max =
0.71 * 140.8 * 8.02e-3 = 0.80, Re_max = 1.13) so that at the mid-height of a
slot of aspect ratio H/L = 10 the a-priori bound on the end effect is
exp(-2.75 * 5) ~ 1e-6 relative, and the rung MEASURES the end effect on every
level (witness W1) rather than trusting the bound.

THE DISCRETISATION EXPECTATION -- DERIVED, NOT PROBED.  On a uniform Cartesian
mesh with the fully developed structure, OpenFOAM's Gauss linear corrected
Laplacian is EXACT on the cubic phi in the interior (the central second
difference of a cubic has zero truncation error), the source g beta (T - T_ref)
is exact at cell centres (T linear is reproduced exactly), and the whole
discretisation error comes from the WALL FLUX, which the cell-centred scheme
forms as (v_P - v_wall)/(h/2) = v'(0) + (h/4) v''(0) + O(h^2): an O(h) flux
error localised in the wall cell, whose global effect is O(h^2) (a localised
source of integrated strength O(h) acting through a Green's function of size
O(h) at the wall cell).  So the expected observed order is p = 2, and the
expected error at each level is obtained EXACTLY by solving the 1-D
cell-centred system

    (phi_{i+1} - 2 phi_i + phi_{i-1}) / h^2 = xi_i - 1/2          (interior)
    (phi_1 - 3 phi_0) / h^2 = xi_0 - 1/2                          (wall cell, v_wall = 0)

for N = 20 / 40 / 80.  discrete_expectation(N) does that; the numbers it
returns are the registered predictions (T13_PREREGISTRATION.md section 6),
and the bands are multiples of the fine-level expectation.  The 2-D SIMPLE
discretisation reduces to this 1-D system in the core because the discrete
p_rgh = -g beta y (T(x) - T_ref) balances ghf snGrad(rhok) face by face
(bilinear against linear), so phi_x = 0, phi_y is column-constant, and both
div(phi,U) and div(phi,T) vanish on a y-invariant field; the only things this
1-D model cannot see are the end regions (measured by W1) and the linear-solver
tolerances.

No `assert` appears in this file.  Every failure is an explicit sys.exit(2).
"""
import math
import sys

EXIT_REFUSE = 2

XI_STAR = 0.5 - math.sqrt(3.0) / 6.0            # location of max upflow
PHI_MAX = 1.0 / (72.0 * math.sqrt(3.0))           # phi(XI_STAR)
NU_EXACT = 1.0                                    # conduction: Nu_L = 1


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def phi(xi):
    """ROUTE A: the closed form, v / u_ref."""
    return xi * (1.0 - xi) * (1.0 - 2.0 * xi) / 12.0


def phi_route_b(xi):
    """ROUTE B: the un-factored polynomial from the integration constants
    (a = 1/12, b = 0), sharing no algebra with the factored form."""
    return xi ** 3 / 6.0 - xi ** 2 / 4.0 + xi / 12.0


def theta_lin(xi):
    """(T - T_c)/DeltaT for the linear conduction profile: 1 - xi."""
    return 1.0 - xi


def u_ref(g, beta, dT, L, nu):
    return g * beta * dT * L * L / nu


def verify(n=2001):
    """The expression must SOLVE the problem, not merely be self-consistent:
    (1) phi'' = xi - 1/2 by finite differences on Route A's own output;
    (2) phi(0) = phi(1) = 0;  (3) zero net flow by Simpson quadrature;
    (4) Route A == Route B;  (5) the stationary point and the maximum;
    (6) antisymmetry phi(1-xi) = -phi(xi).  REFUSES on any failure."""
    h = 1e-4
    worst = 0.0
    for k in range(1, 100):
        xi = k / 100.0
        d2 = (phi(xi + h) - 2 * phi(xi) + phi(xi - h)) / (h * h)
        worst = max(worst, abs(d2 - (xi - 0.5)))
    if worst > 1e-6:
        refuse("Route B: phi'' != xi - 1/2 by finite differences (worst %.3e)" % worst)
    if abs(phi(0.0)) > 1e-15 or abs(phi(1.0)) > 1e-15:
        refuse("no-slip not satisfied: phi(0)=%.3e phi(1)=%.3e" % (phi(0.0), phi(1.0)))
    m = n if n % 2 else n + 1
    hh = 1.0 / (m - 1)
    tot = 0.0
    for i in range(m):
        w = 1.0 if i in (0, m - 1) else (4.0 if i % 2 else 2.0)
        tot += w * phi(i * hh)
    net = tot * hh / 3.0
    if abs(net) > 1e-14:
        refuse("zero-net-flow violated: int phi = %.3e" % net)
    wab = max(abs(phi(k / 200.0) - phi_route_b(k / 200.0)) for k in range(201))
    if wab > 1e-15:
        refuse("Route A and Route B disagree by %.3e" % wab)
    dphi = (phi(XI_STAR + h) - phi(XI_STAR - h)) / (2 * h)
    # central difference: error h^2 phi'''/6 = 1.7e-9 on a cubic, so the
    # numerical check tolerates 1e-8 and the closed-form derivative is exact
    dphi_exact = (1.0 - 6.0 * XI_STAR + 6.0 * XI_STAR ** 2) / 12.0
    if abs(dphi) > 1e-8 or abs(dphi_exact) > 1e-16:
        refuse("phi'(xi*) = %.3e numerical / %.3e closed form: xi* is not a stationary point"
               % (dphi, dphi_exact))
    if abs(phi(XI_STAR) - PHI_MAX) > 1e-16:
        refuse("phi(xi*) = %.17g != 1/(72 sqrt 3) = %.17g" % (phi(XI_STAR), PHI_MAX))
    scan = max(phi(k / 10000.0) for k in range(10001))
    if scan > PHI_MAX + 1e-12:
        refuse("a scanned value %.17g exceeds the claimed maximum %.17g" % (scan, PHI_MAX))
    wanti = max(abs(phi(1 - k / 200.0) + phi(k / 200.0)) for k in range(201))
    if wanti > 1e-16:
        refuse("profile is not antisymmetric (worst %.3e)" % wanti)
    print("  exact_t13.verify: phi'' = xi - 1/2 (worst %.1e); phi(0)=phi(1)=0; "
          "int phi = %.1e; A==B to %.1e; xi* = %.10f, phi_max = %.10e; antisymmetric"
          % (worst, net, wab, XI_STAR, PHI_MAX))
    return True


# ----------------------------------------------------------- readers' kernels
def lagrange4(xs, ys, x):
    """4-point Lagrange interpolation at x through the 4 nodes nearest x.
    Exact on a cubic, so on the analytic profile its interpolation error is
    ZERO and what it reports on a numerical profile is the discretisation
    error alone (the reason a 2-point interpolant, whose O(h^2) error would
    enter the Roache triple alongside the discretisation error, is not used)."""
    n = len(xs)
    if n < 4:
        refuse("lagrange4 needs >= 4 nodes, got %d" % n)
    # index of the first node of the 4-node window bracketing x
    k = min(range(n), key=lambda i: abs(xs[i] - x))
    i0 = min(max(k - 1, 0), n - 4)
    if xs[i0 + 1] > x and i0 > 0:
        i0 -= 1
    i0 = min(max(i0, 0), n - 4)
    tot = 0.0
    for a in range(4):
        w = 1.0
        for b in range(4):
            if a != b:
                w *= (x - xs[i0 + b]) / (xs[i0 + a] - xs[i0 + b])
        tot += w * ys[i0 + a]
    return tot


def cubic_max_location(xs, ys):
    """Location of the maximum from the cubic through the 4 nodes around the
    largest sample: the stationary point of the fitted cubic nearest that
    sample.  Exact on the analytic cubic."""
    n = len(xs)
    k = max(range(n), key=lambda i: ys[i])
    i0 = min(max(k - 1, 0), n - 4)
    X = xs[i0:i0 + 4]
    Y = ys[i0:i0 + 4]
    # cubic coefficients by solving the 4x4 Vandermonde (Gaussian elimination)
    A = [[X[i] ** 3, X[i] ** 2, X[i], 1.0, Y[i]] for i in range(4)]
    for c in range(4):
        p = max(range(c, 4), key=lambda r: abs(A[r][c]))
        A[c], A[p] = A[p], A[c]
        if A[c][c] == 0.0:
            refuse("cubic fit: singular Vandermonde")
        for r in range(4):
            if r != c:
                f = A[r][c] / A[c][c]
                for cc in range(c, 5):
                    A[r][cc] -= f * A[c][cc]
    a3, a2, a1 = A[0][4] / A[0][0], A[1][4] / A[1][1], A[2][4] / A[2][2]
    disc = a2 * a2 - 3.0 * a3 * a1
    if disc < 0.0 or a3 == 0.0:
        refuse("cubic fit: no real stationary point")
    r1 = (-a2 + math.sqrt(disc)) / (3.0 * a3)
    r2 = (-a2 - math.sqrt(disc)) / (3.0 * a3)
    # the maximum has negative second derivative 6 a3 x + 2 a2
    cands = [r for r in (r1, r2) if 6.0 * a3 * r + 2.0 * a2 < 0.0]
    if not cands:
        refuse("cubic fit: no maximum among stationary points")
    return min(cands, key=lambda r: abs(r - xs[k]))


# --------------------------------------------- the discretisation expectation
def discrete_profile(N):
    """Solve the 1-D cell-centred FV system for phi on N uniform cells with the
    half-cell wall flux (v_wall = 0).  Thomas algorithm.  Returns (xi, phi)."""
    if N < 4:
        refuse("N must be >= 4")
    h = 1.0 / N
    xi = [(i + 0.5) * h for i in range(N)]
    a = [1.0] * N          # sub-diagonal (coefficient of phi_{i-1})
    b = [-2.0] * N         # diagonal
    c = [1.0] * N          # super-diagonal
    d = [(xi[i] - 0.5) * h * h for i in range(N)]
    b[0] = -3.0
    b[N - 1] = -3.0
    a[0] = 0.0
    c[N - 1] = 0.0
    # forward sweep
    for i in range(1, N):
        m = a[i] / b[i - 1]
        b[i] -= m * c[i - 1]
        d[i] -= m * d[i - 1]
    x = [0.0] * N
    x[N - 1] = d[N - 1] / b[N - 1]
    for i in range(N - 2, -1, -1):
        x[i] = (d[i] - c[i] * x[i + 1]) / b[i]
    return xi, x


def discrete_expectation(N):
    """The registered EXPECTATION of the graded readers on N cells across the
    gap: G1 (phi at xi* by lagrange4) and G1b (xi_max by cubic fit), each as
    (value, error, relative error)."""
    xi, ph = discrete_profile(N)
    g1 = lagrange4(xi, ph, XI_STAR)
    g1b = cubic_max_location(xi, ph)
    rms = math.sqrt(sum((ph[i] - phi(xi[i])) ** 2 for i in range(N)) / N)
    return dict(N=N, G1=g1, G1_err=g1 - PHI_MAX, G1_rel=(g1 - PHI_MAX) / PHI_MAX,
                G1b=g1b, G1b_err=g1b - XI_STAR, rms_err=rms)


def expectation_table(levels=(20, 40, 80)):
    rows = [discrete_expectation(N) for N in levels]
    for k in range(1, len(rows)):
        for key in ("G1_err", "G1b_err", "rms_err"):
            e1, e0 = rows[k - 1][key], rows[k][key]
            rows[k]["p_" + key] = (math.log(abs(e1 / e0)) / math.log(2.0)
                                    if e0 != 0.0 and e1 / e0 > 0 else None)
    return rows


def selfcheck_readers():
    """The readers must be EXACT on the analytic cubic (the value control the
    family registered as N-T8): lagrange4 at xi* and the cubic-fit location,
    both on N = 20 cell centres of the analytic profile."""
    for N in (20, 40, 80):
        xi = [(i + 0.5) / N for i in range(N)]
        ph = [phi(x) for x in xi]
        v = lagrange4(xi, ph, XI_STAR)
        loc = cubic_max_location(xi, ph)
        if abs(v - PHI_MAX) > 1e-15 * 100:
            refuse("lagrange4 is not exact on the analytic cubic at N=%d: %.3e" % (N, v - PHI_MAX))
        if abs(loc - XI_STAR) > 1e-12:
            refuse("cubic_max_location is not exact on the analytic cubic at N=%d: %.3e" % (N, loc - XI_STAR))
    print("  exact_t13.selfcheck_readers: lagrange4 and cubic_max_location exact on the analytic cubic at N = 20/40/80")
    return True


if __name__ == "__main__":
    verify()
    selfcheck_readers()
    print("  discrete expectation (1-D cell-centred model, half-cell wall flux):")
    for r in expectation_table():
        print("    N=%-3d G1=%.10e err=%+.3e rel=%+.3e p=%s | xi_max=%.8f err=%+.3e p=%s | rms=%.3e p=%s"
              % (r["N"], r["G1"], r["G1_err"], r["G1_rel"],
                 ("%.4f" % r["p_G1_err"]) if r.get("p_G1_err") else "-",
                 r["G1b"], r["G1b_err"],
                 ("%.4f" % r["p_G1b_err"]) if r.get("p_G1b_err") else "-",
                 r["rms_err"], ("%.4f" % r["p_rms_err"]) if r.get("p_rms_err") else "-"))
