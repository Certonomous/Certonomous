#!/usr/bin/env python3
"""
Exact analytic (inviscid, incompressible-potential-flow) theory for a symmetric
Joukowski airfoil, via the classic Joukowski conformal map.

VERIFICATION STANDARD (per F3 campaign precedent, demo-output/website/campaign/
F3_supersonic_exact_theory.md): before this module's airfoil Cp/CL formulas are
trusted for gating a CFD run, the underlying potential-flow building block --
flow around a bare circular cylinder -- is checked against the classic published
closed-form result

    Cp(theta) = 1 - 4 sin^2(theta)                         (Cp on |zeta|=R, Gamma=0)

which appears in essentially every incompressible-aerodynamics text (e.g.
Anderson, "Fundamentals of Aerodynamics"; also re-derived independently in the
SIAM student paper fetched during this task's research pass,
https://www.siam.org/media/m1xn4xk2/modeling_the_fluid_flow.pdf, Sec. 4).
See `_selftest_cylinder()` below -- run this file directly to execute it.

GEOMETRY. Circle-plane circle: center zc = -eps (real, symmetric/uncambered),
radius R = 1+eps, chosen so the circle passes exactly through zeta=+1 (b=1,
normalized map). Joukowski map: z = zeta + 1/zeta. This places a CUSPED
trailing edge at z=+2 (dz/dzeta = 0 there) -- the DPW-8/HFCFDVW-specified
cusped Joukowski geometry (AIAA 2023-1244 Sec. IV: "features a cusped trailing
edge... removes the inviscid singularity at the trailing edge at zero degrees
angle of attack").

eps is NOT independently confirmed from any committee source reachable in this
pass (flagged explicitly in DPW8_V2_joukowski.md) -- we pick eps=0.10 (a
standard, textbook-scale choice used across Joukowski-airfoil teaching examples,
giving the thickness ratio computed and reported by `airfoil_geometry()` below)
and hold it FIXED and clearly stated for our own generated grid family and its
own exact solution. The gate this buys is self-consistent and unfakeable in the
F3 sense: our CFD mesh is built from the SAME map with the SAME eps, so any
gap between the CFD surface Cp and this module's closed-form Cp reflects real
solver behavior (viscosity, compressibility, mesh truncation) -- not a
mismatched reference geometry.

ZERO-LIFT PROOF (alpha=0, uncambered): the circle center lies on the real axis
(zc real), so at alpha=0 the two potential-flow stagnation points on the circle
are exactly the real-axis points zeta = zc+R (=+1, the TE cusp) and
zeta = zc-R (the LE). Both automatically satisfy their required conditions with
ZERO circulation (Gamma=0) -- no Kutta root-find is needed at alpha=0; this is
an exact symmetry argument, not a numerical coincidence. Gamma=0 => CL=0
exactly, by the Kutta-Joukowski theorem L'=rho U_inf Gamma. This matches the
HFCFDVW/Galbraith case sheet's own mandatory check: "Participants should also
verify that machine zero lift is computed on all grids."
(https://how5.cenaero.be/.../VR1_RANSJoukowskiAirfoil_0.pdf, "Mandatory
campaign" section.)
"""
import numpy as np


def cylinder_cp(theta, alpha=0.0, gamma_over_4piUR=0.0):
    """Cp on the surface of a bare circle (unit radius, centered at origin),
    uniform flow at angle alpha, circulation parameter Gamma/(4 pi U R).
    Classic result (Gamma=0, alpha=0): Cp = 1 - 4 sin^2(theta)."""
    # w(zeta) = U[(zeta)e^{-ia} + R^2 e^{ia}/zeta] + iGamma/(2pi) ln(zeta), R=1, U=1
    # surface speed (zeta=e^{i theta}): standard result
    # V/U = 2 sin(theta - alpha) + Gamma/(2 pi U R)   [tangential speed on |zeta|=R]
    Vt_over_U = 2.0 * np.sin(theta - alpha) + 2.0 * gamma_over_4piUR
    return 1.0 - Vt_over_U ** 2


def _selftest_cylinder():
    theta = np.linspace(0, 2 * np.pi, 2001)
    cp_mine = cylinder_cp(theta, alpha=0.0, gamma_over_4piUR=0.0)
    cp_published = 1.0 - 4.0 * np.sin(theta) ** 2
    err = np.max(np.abs(cp_mine - cp_published))
    print(f"[selftest] cylinder Cp vs published Cp=1-4sin^2(theta): max abs err = {err:.3e}")
    assert err < 1e-12, "cylinder Cp implementation does not match published closed form"
    # stagnation points at machine zero: theta=0 and theta=pi should give Cp=1
    for th in (0.0, np.pi):
        cpv = cylinder_cp(np.array([th]))[0]
        assert abs(cpv - 1.0) < 1e-12, f"stagnation Cp check failed at theta={th}: {cpv}"
    print("[selftest] cylinder self-test PASSED (stagnation Cp=1 at theta=0, pi; "
          "matches published Cp=1-4sin^2(theta) to machine precision)")


class JoukowskiAirfoil:
    def __init__(self, eps=0.10, alpha_deg=0.0):
        self.eps = eps
        self.alpha = np.radians(alpha_deg)
        self.zc = -eps + 0j
        self.R = 1.0 + eps

    def circle_point(self, theta):
        return self.zc + self.R * np.exp(1j * theta)

    def z_of_zeta(self, zeta):
        return zeta + 1.0 / zeta

    def dzdzeta(self, zeta):
        return 1.0 - 1.0 / zeta ** 2

    def circulation_over_4piUR(self):
        """Gamma/(4 pi U R). At alpha=0, uncambered (zc real): exactly 0 by the
        symmetry argument in the module docstring. General alpha (not used for
        the V2 case, alpha=0) via the standard closed-form Kutta condition for a
        circle whose surface point zeta=+1 (angle beta below) is forced to be
        the rear stagnation point: Gamma/(4 pi U R) = sin(alpha+beta)/2 * ... ;
        implemented here via the standard elementary formula
        Gamma = -4 pi U R sin(alpha+beta), beta=angle of (R,0) offset from
        center i.e. beta = angle(zeta_TE - zc) measured s.t. beta=0 when TE
        point is at theta=0 on the circle relative to center (our case:
        zeta_TE - zc = R exactly on the real axis => beta=0).
        """
        beta = 0.0  # zc is real (uncambered): TE point (zeta=1) sits at theta=0 on the circle
        return -np.sin(self.alpha + beta) / 2.0

    def surface(self, n=2000):
        theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
        zeta = self.circle_point(theta)
        z = self.z_of_zeta(zeta)
        return theta, z

    def chord_and_tc(self, n=200000):
        theta, z = self.surface(n)
        x = z.real
        c = x.max() - x.min()
        y = z.imag
        # thickness at each x: for symmetric airfoil, max |y| roughly at mid-chord
        tmax = y.max() - y.min()
        return c, tmax, tmax / c

    def surface_cp(self, n=4000, eps_theta=1e-6):
        """Exact inviscid Cp(theta) on the mapped airfoil surface, alpha as set
        in __init__. Handles the removable singularity at the cusp (zeta=+1,
        theta=0) via a symmetric-limit L'Hopital finite-difference straddle."""
        theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
        g = self.circulation_over_4piUR()
        zeta = self.circle_point(theta)
        Vt_over_U = 2.0 * np.sin(theta - self.alpha) + 2.0 * g  # tangential surface speed / U, in zeta-plane
        # dw/dzeta magnitude on the circle relates to Vt via |dw/dzeta| = Vt (tangential,
        # since normal component is zero on the surface); complex velocity in zeta-plane:
        # the physical (z-plane) speed is |dw/dzeta| / |dz/dzeta|, taking the L'Hopital
        # limit at the cusp (theta -> 0 mod 2pi) where dz/dzeta -> 0 simultaneously with
        # the local zeta-plane speed -> 0 there (Gamma=0, alpha=0 case: stagnation at TE).
        dzdz = self.dzdzeta(zeta)
        mag_dzdz = np.abs(dzdz)
        speed = np.full_like(theta, np.nan)
        near_cusp = mag_dzdz < 1e-6
        far = ~near_cusp
        speed[far] = np.abs(Vt_over_U[far]) / mag_dzdz[far]
        # cusp limit via symmetric finite offset in theta (both numerator and
        # denominator vanish there for the zero-lift symmetric case)
        if np.any(near_cusp):
            idxs = np.where(near_cusp)[0]
            for i in idxs:
                th0 = theta[i]
                thp = th0 + eps_theta
                zetap = self.circle_point(thp)
                Vtp = 2.0 * np.sin(thp - self.alpha) + 2.0 * g
                sp = abs(Vtp) / abs(self.dzdzeta(zetap))
                speed[i] = sp
        cp = 1.0 - speed ** 2
        return theta, cp

    def cl_from_cp_integration(self, n=200000):
        """Independent check: integrate Cp*n_hat over the surface (pressure
        force) and compare to the Kutta-Joukowski circulation-theorem lift.
        Two different computational paths from the same map; agreement to
        near-machine precision is the internal consistency check (F3-style)."""
        theta, z = self.surface(n)
        _, cp = self.surface_cp(n)
        x, y = z.real, z.imag
        c, _, _ = self.chord_and_tc(n)
        dx = np.roll(x, -1) - x
        dy = np.roll(y, -1) - y
        # panel-based normal-force integration (trapezoid over closed loop)
        cp_mid = 0.5 * (cp + np.roll(cp, -1))
        # Cp acts along -n_hat (pressure pushes inward); force per unit span:
        # Fx = -oint p * dy ; Fy = oint p * dx  (dividing by q*c for coefficients)
        cx = np.sum(-cp_mid * dy) / c
        cy = np.sum(cp_mid * dx) / c
        alpha = self.alpha
        cl = cy * np.cos(alpha) - cx * np.sin(alpha)
        cd = cy * np.sin(alpha) + cx * np.cos(alpha)
        return cl, cd


def _selftest_airfoil_zero_lift(eps=0.10):
    af = JoukowskiAirfoil(eps=eps, alpha_deg=0.0)
    g = af.circulation_over_4piUR()
    assert abs(g) < 1e-15, f"expected exact zero circulation at alpha=0, got {g}"
    cl, cd_inviscid = af.cl_from_cp_integration(n=400000)
    print(f"[selftest] Joukowski eps={eps}: Gamma/(4piUR)={g:.3e} (exact 0 by symmetry), "
          f"CL from Cp-integration = {cl:.3e} (expect ~0), "
          f"inviscid Cd from Cp-integration = {cd_inviscid:.3e} (expect ~0, d'Alembert)")
    assert abs(cl) < 1e-6, f"CL should be ~0 at alpha=0 symmetric, got {cl}"
    assert abs(cd_inviscid) < 1e-4, f"inviscid Cd should be ~0 (d'Alembert), got {cd_inviscid}"
    c, tmax, tc = af.chord_and_tc()
    print(f"[selftest] geometry: chord={c:.6f}, max thickness={tmax:.6f}, t/c={tc*100:.3f}%")
    # stagnation Cp checks at LE and TE
    theta, cp = af.surface_cp(n=200000)
    cp_te = cp[0]
    ile = np.argmin(np.real(af.z_of_zeta(af.circle_point(theta))))
    cp_le = cp[ile]
    print(f"[selftest] Cp at TE (cusp, theta=0): {cp_te:.6f} (finite, generally != 1 for a cusp -- "
          f"NOT a stagnation point in the z-plane despite being one in the zeta-plane)")
    print(f"[selftest] Cp at LE (theta={theta[ile]:.4f} rad): {cp_le:.6f} (expect ~1, true stagnation point)")
    assert abs(cp_le - 1.0) < 1e-3, f"LE stagnation Cp should be ~1, got {cp_le}"
    return af


if __name__ == "__main__":
    _selftest_cylinder()
    print()
    _selftest_airfoil_zero_lift(eps=0.10)
