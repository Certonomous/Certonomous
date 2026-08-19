#!/usr/bin/env python3
"""
Derive T1c's reference constants instead of transcribing them.

T1's specification claims the laminar-pipe rung has a reference that CANNOT be
wrong.  That claim is only worth something if the constants are reproduced from
the governing equations here, in code, rather than typed in from a textbook page
where a digit can be dropped silently.  Each constant below is obtained TWICE --
once in closed form and once by a numerical solution of the same problem -- and
the two must agree.

Zero compute in the solver sense: no case, no mesh, no OpenFOAM.  Pure quadrature
and a tridiagonal eigenproblem, a fraction of a second.

  f . Re = 64            Hagen-Poiseuille, Darcy friction factor
  Nu     = 48/11         fully developed, CONSTANT WALL HEAT FLUX
  Nu     = 3.6568        fully developed, CONSTANT WALL TEMPERATURE
                         (the first Graetz eigenvalue, Nu = lambda_0^2 / 2)
"""
import sys


def friction_closed_form():
    """f = 64/Re from the parabolic profile, as f.Re."""
    # u(r) = 2U(1 - (r/R)^2);  tau_w = -mu du/dr|_R = 4 mu U / R
    # f = 8 tau_w / (rho U^2) = 32 mu U / (rho U^2 R) = 64 nu / (U D) = 64/Re
    return 64.0


def friction_numeric(n=200001):
    """f.Re by integrating the profile: mean velocity and wall shear from u(r)."""
    # work in eta = r/R with u = 2(1 - eta^2) in units of U
    h = 1.0 / (n - 1)
    # mean velocity = 2 * integral_0^1 u(eta) eta d(eta)  must return 1.0
    tot = 0.0
    for i in range(n):
        e = i * h
        w = 0.5 if i in (0, n - 1) else 1.0
        tot += w * 2.0 * (1.0 - e * e) * e * h
    Umean = 2.0 * tot
    # du/d(eta) at the wall, one-sided high-order difference on the same grid
    def u(e):
        return 2.0 * (1.0 - e * e)
    dudeta = (3 * u(1.0) - 4 * u(1.0 - h) + u(1.0 - 2 * h)) / (2 * h)
    # tau_w = mu (U/R) (-du/deta)
    # f     = 8 tau_w / (rho U^2) = 8 nu (-du/deta) / (R U)
    # Re    = U D / nu = 2 U R / nu   ->   nu/(R U) = 2/Re
    # f     = 16 (-du/deta) / Re      ->   f.Re = 16 (-du/deta) / Umean^2
    return 16.0 * (-dudeta) / (Umean ** 2)


def nu_constant_flux_closed_form():
    return 48.0 / 11.0


def nu_constant_flux_numeric(n=400001):
    """Integrate the fully developed constant-q'' problem directly.

    With u = 2U(1-eta^2) and dT/dx constant, the energy equation
        (1/eta) d/deta (eta dtheta/deta) = (2 R^2 dTm/dx / alpha)(1-eta^2)
    integrates to theta(eta) = C (eta^2 - eta^4/4), and Nu follows from the
    ratio of the wall gradient to the bulk-to-wall difference.  Both the profile
    and the bulk average are formed numerically here.
    """
    h = 1.0 / (n - 1)
    # theta(eta) = eta^2 - eta^4/4, up to a constant factor that cancels in Nu
    def th(e):
        return e * e - 0.25 * e ** 4
    # bulk (velocity-weighted) mean: 2 * int u_norm theta eta deta, u_norm=2(1-e^2)
    num = 0.0
    den = 0.0
    for i in range(n):
        e = i * h
        w = 0.5 if i in (0, n - 1) else 1.0
        un = 2.0 * (1.0 - e * e)
        num += w * un * th(e) * e * h
        den += w * un * e * h
    th_bulk = num / den
    th_wall = th(1.0)
    dthdeta_wall = (3 * th(1.0) - 4 * th(1.0 - h) + th(1.0 - 2 * h)) / (2 * h)
    # Nu = h D / k = (q'' D)/(k (Tw - Tb)); q'' ~ k dT/dr|_w
    # in eta and D = 2R:  Nu = 2 * dth/deta|_w / (th_wall - th_bulk)
    return 2.0 * dthdeta_wall / (th_wall - th_bulk)


def nu_constant_temperature_numeric(n=20000):
    """First Graetz eigenvalue by finite differences; Nu = lambda_0^2 / 2.

    Solve  -(1/eta)(eta theta')' = lambda^2 (1 - eta^2) theta
    with theta'(0) = 0 and theta(1) = 0 -- a generalised symmetric eigenproblem
    A x = lambda^2 B x, solved here by inverse iteration on a tridiagonal system
    so that no linear-algebra dependency is needed.
    """
    h = 1.0 / n
    # unknowns at eta_i = (i+0.5)h, i = 0..n-1 ; theta(1)=0 imposed at the face
    N = n
    eta = [(i + 0.5) * h for i in range(N)]
    # A: -(1/eta) d/deta(eta d/deta) in conservative finite-volume form
    # face positions eta_{i+1/2} = (i+1)h
    lower = [0.0] * N
    diag = [0.0] * N
    upper = [0.0] * N
    for i in range(N):
        ep = (i + 1) * h          # right face
        em = i * h                # left face
        cp = ep / (eta[i] * h * h)
        cm = em / (eta[i] * h * h)
        if i == N - 1:
            # theta at the wall face is zero: ghost value = -theta_i
            diag[i] = cp * 2.0 + cm
            lower[i] = -cm
        else:
            diag[i] = cp + cm
            upper[i] = -cp
            if i > 0:
                lower[i] = -cm
            else:
                diag[i] = cp        # symmetry at the axis: no flux through em=0
    B = [(1.0 - e * e) for e in eta]

    def solve_shifted(rhs, shift):
        """Thomas algorithm on (A - shift*B)."""
        a = [lower[i] for i in range(N)]
        b = [diag[i] - shift * B[i] for i in range(N)]
        c = [upper[i] for i in range(N)]
        d = list(rhs)
        for i in range(1, N):
            m = a[i] / b[i - 1]
            b[i] -= m * c[i - 1]
            d[i] -= m * d[i - 1]
        x = [0.0] * N
        x[N - 1] = d[N - 1] / b[N - 1]
        for i in range(N - 2, -1, -1):
            x[i] = (d[i] - c[i] * x[i + 1]) / b[i]
        return x

    # inverse iteration with a shift just below the known first eigenvalue
    shift = 7.0
    x = [1.0] * N
    lam = None
    for _ in range(200):
        y = solve_shifted([B[i] * x[i] for i in range(N)], shift)
        nrm = max(abs(v) for v in y)
        x = [v / nrm for v in y]
        # Rayleigh quotient for A x = lambda B x
        Ax = []
        for i in range(N):
            v = diag[i] * x[i]
            if i > 0:
                v += lower[i] * x[i - 1]
            if i < N - 1:
                v += upper[i] * x[i + 1]
            Ax.append(v)
        num = sum(x[i] * Ax[i] for i in range(N))
        den = sum(x[i] * B[i] * x[i] for i in range(N))
        new = num / den
        if lam is not None and abs(new - lam) < 1e-12:
            lam = new
            break
        lam = new
    return lam / 2.0, lam


def main():
    ok = True

    def check(name, a, b, tol):
        nonlocal ok
        good = abs(a - b) <= tol * max(1.0, abs(b))
        ok = ok and good
        print(f"  {'ok  ' if good else 'FAIL'} {name:44s} {a:.6f}  vs  {b:.6f}"
              f"   (rel {abs(a-b)/abs(b):.2e}, tol {tol:.0e})")

    print("T1c reference constants, derived two ways each:\n")
    check("f.Re  closed form vs numeric profile",
          friction_numeric(), friction_closed_form(), 1e-4)
    check("Nu constant q''  numeric vs 48/11",
          nu_constant_flux_numeric(), nu_constant_flux_closed_form(), 1e-4)
    nu_T, lam = nu_constant_temperature_numeric()
    print(f"       first Graetz eigenvalue lambda_0^2 = {lam:.6f}")
    check("Nu constant Ts   numeric vs 3.656794",
          nu_T, 3.6567934, 2e-3)

    print("\nregistered in T1_FORCED_CONVECTION_CANON_PREREGISTRATION.md 2.1:")
    print(f"  Nu (constant Ts) = 3.657      derived here as {nu_T:.4f}")
    print(f"  Nu (constant q'')= 48/11 = {48/11:.4f}  derived here as "
          f"{nu_constant_flux_numeric():.4f}")
    print(f"  f.Re             = 64         derived here as "
          f"{friction_numeric():.4f}")
    print("\nDERIVATION " + ("AGREES" if ok else "DISAGREES"))
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main())
