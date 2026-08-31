#!/usr/bin/env python3
"""T15 analytic referent: the Ostrach (1953) similarity solution for laminar
natural convection on a vertical isothermal flat plate, INTEGRATED HERE by a
shooting method, never transcribed from a table.

Similarity form (Ostrach 1953, NACA Report 1111):
    eta   = (y/x) (Gr_x/4)^{1/4}
    psi   = 4 nu (Gr_x/4)^{1/4} F(eta)
    u     = (2 nu / x) Gr_x^{1/2} F'(eta)         (streamwise, along the plate)
    theta = (T - T_inf) / (T_w - T_inf)
    F''' + 3 F F'' - 2 F'^2 + theta = 0
    theta'' + 3 Pr F theta' = 0
    F(0) = F'(0) = 0, theta(0) = 1 ; F'(inf) = 0, theta(inf) = 0
    Nu_x = -theta'(0) (Gr_x/4)^{1/4}
Ostrach's tabulated value at Pr = 0.72 is -theta'(0) = 0.5046, i.e.
Nu_x = 0.5046 (Gr_x/4)^{1/4} = 0.3568 Gr_x^{1/4}.  The registered Pr is 0.71.

ROUTE B (verified in --verify, exit 2 on any failure):
  (B1) ODE residuals of the returned solution at every node < 1e-8;
  (B2) far-field conditions |F'(eta_max)|, |theta(eta_max)| < 1e-6;
  (B3) the Pr = 0.72 cross-check: -theta'(0) recovered to |diff| <= 1e-4 of
       Ostrach's 0.5046, and 0.3568 Gr^{1/4} form to 1e-4;
  (B4) a PLANTED 1 percent mutation of the coefficient is REFUSED by B3.
NO `assert` STATEMENT IN THIS FILE (L-332); every refusal is sys.exit(2).
"""
import math
import sys

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import fsolve

ETA_MAX = 12.0
PR_REG = 0.71
OSTRACH_PR = 0.72
OSTRACH_THETA0 = 0.5046          # -theta'(0), Ostrach 1953 Table at Pr = 0.72
OSTRACH_GR_COEF = 0.3568         # Nu_x = 0.3568 Gr_x^{1/4}, Pr = 0.72
XCHECK_TOL = 1.0e-4


def refuse(msg):
    sys.stderr.write("REFUSE: %s\n" % msg)
    sys.exit(2)


def rhs(eta, z, pr):
    f, fp, fpp, th, thp = z
    return [fp, fpp, -3.0 * f * fpp + 2.0 * fp * fp - th, thp, -3.0 * pr * f * thp]


def integrate(fpp0, thp0, pr, eta_max=ETA_MAX, dense=False):
    sol = solve_ivp(rhs, (0.0, eta_max), [0.0, 0.0, fpp0, 1.0, thp0], args=(pr,),
                    method="DOP853", rtol=1e-12, atol=1e-14, dense_output=dense)
    return sol


def shoot(pr, guess=(0.67, -0.50)):
    def resid(s):
        sol = integrate(s[0], s[1], pr)
        return [sol.y[1, -1], sol.y[3, -1]]
    s, info, ier, msg = fsolve(resid, guess, xtol=1e-13, full_output=True)
    if ier != 1:
        refuse("shooting did not converge for Pr=%g: %s" % (pr, msg))
    return float(s[0]), float(s[1])


class Similarity:
    """The solved profile at one Pr, with the readers the comparator uses."""

    def __init__(self, pr=PR_REG):
        self.pr = pr
        self.fpp0, self.thp0 = shoot(pr)
        self.sol = integrate(self.fpp0, self.thp0, pr, dense=True)
        eta = np.linspace(0.0, 4.0, 40001)
        fp = self.sol.sol(eta)[1]
        i = int(np.argmax(fp))
        # refine the maximum by golden section on the dense solution
        a, b = eta[max(i - 1, 0)], eta[min(i + 1, len(eta) - 1)]
        for _ in range(200):
            c = b - 0.6180339887498949 * (b - a)
            d = a + 0.6180339887498949 * (b - a)
            if self.sol.sol(c)[1] > self.sol.sol(d)[1]:
                b = d
            else:
                a = c
        self.eta_umax = 0.5 * (a + b)
        self.fp_max = float(self.sol.sol(self.eta_umax)[1])

    def theta0(self):
        return -self.thp0

    def profile(self, eta):
        return self.sol.sol(np.asarray(eta, dtype=float))

    # physical readers -------------------------------------------------
    def nu_x(self, gr_x):
        return self.theta0() * (gr_x / 4.0) ** 0.25

    def u_max(self, x, gr_x, nu):
        return 2.0 * nu / x * math.sqrt(gr_x) * self.fp_max

    def y_umax(self, x, gr_x):
        return self.eta_umax * x / (gr_x / 4.0) ** 0.25

    def delta_T99(self, x, gr_x):
        eta = np.linspace(0.0, ETA_MAX, 120001)
        th = self.sol.sol(eta)[3]
        j = int(np.argmax(th < 0.01))
        return eta[j] * x / (gr_x / 4.0) ** 0.25

    def T_profile(self, y, x, gr_x):
        eta = np.asarray(y, dtype=float) / x * (gr_x / 4.0) ** 0.25
        eta = np.clip(eta, 0.0, ETA_MAX)
        return self.sol.sol(eta)[3]

    def u_profile(self, y, x, gr_x, nu):
        eta = np.asarray(y, dtype=float) / x * (gr_x / 4.0) ** 0.25
        eta = np.clip(eta, 0.0, ETA_MAX)
        return 2.0 * nu / x * math.sqrt(gr_x) * self.sol.sol(eta)[1]


def ode_residual_max(sim, n=4001):
    eta = np.linspace(0.0, ETA_MAX, n)
    z = sim.profile(eta)
    f, fp, fpp, th, thp = z
    # derivatives of the dense solution by the RHS itself would be circular;
    # use high-order central differences on the dense output instead
    h = 1e-4
    zp = sim.profile(np.clip(eta + h, 0, ETA_MAX))
    zm = sim.profile(np.clip(eta - h, 0, ETA_MAX))
    inner = (eta > h) & (eta < ETA_MAX - h)
    fppp = (zp[2] - zm[2]) / (2 * h)
    thpp = (zp[4] - zm[4]) / (2 * h)
    r1 = fppp + 3 * f * fpp - 2 * fp * fp + th
    r2 = thpp + 3 * sim.pr * f * thp
    return float(np.max(np.abs(r1[inner]))), float(np.max(np.abs(r2[inner])))


def cross_check(theta0_072, coef_theta0=OSTRACH_THETA0, coef_gr=OSTRACH_GR_COEF, tol=XCHECK_TOL):
    """Route-B3: returns (ok, d1, d2); REFUSAL is the caller's (exit 2)."""
    d1 = abs(theta0_072 - coef_theta0)
    d2 = abs(theta0_072 / math.sqrt(2.0) - coef_gr)
    return (d1 <= tol and d2 <= tol), d1, d2


def verify():
    fails = []
    sim71 = Similarity(PR_REG)
    sim72 = Similarity(OSTRACH_PR)
    r1, r2 = ode_residual_max(sim71)
    print("B1 ODE residuals (Pr=%.2f): momentum %.3e energy %.3e" % (PR_REG, r1, r2))
    if not (r1 < 1e-8 and r2 < 1e-8):
        fails.append("B1 residuals")
    zf = sim71.profile(ETA_MAX)
    print("B2 far field at eta=%.1f: F'=%.3e theta=%.3e" % (ETA_MAX, zf[1], zf[3]))
    if not (abs(zf[1]) < 1e-6 and abs(zf[3]) < 1e-6):
        fails.append("B2 far field")
    ok, d1, d2 = cross_check(sim72.theta0())
    print("B3 Pr=0.72: -theta'(0)=%.6f vs Ostrach 0.5046 |diff|=%.2e; /sqrt2=%.6f vs 0.3568 |diff|=%.2e -> %s"
          % (sim72.theta0(), d1, sim72.theta0() / math.sqrt(2), d2, "AGREE" if ok else "DISAGREE"))
    if not ok:
        fails.append("B3 cross-check")
    okm, d1m, d2m = cross_check(sim72.theta0(), coef_theta0=OSTRACH_THETA0 * 1.01, coef_gr=OSTRACH_GR_COEF * 1.01)
    print("B4 planted 1 percent coefficient mutation: |diff|=%.2e, %.2e -> %s"
          % (d1m, d2m, "REFUSED" if not okm else "ACCEPTED (BLIND)"))
    if okm:
        fails.append("B4 mutation not refused")
    print("Pr=%.2f: F''(0)=%.6f  -theta'(0)=%.6f  eta_umax=%.6f  F'max=%.6f"
          % (PR_REG, sim71.fpp0, sim71.theta0(), sim71.eta_umax, sim71.fp_max))
    print("Pr=%.2f: F''(0)=%.6f  -theta'(0)=%.6f" % (OSTRACH_PR, sim72.fpp0, sim72.theta0()))
    if fails:
        refuse("route B failed: %s" % ", ".join(fails))
    print("ROUTE B VERIFIED: B1 B2 B3 B4 all passed (each printed from inside its own branch)")


if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify()
    else:
        print(__doc__)
