#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""VMFL006 REFERENCE MODULE -- the lab's OWN evaluation of the Graetz series, by
TWO INDEPENDENT INSTRUMENTS, and the pre-freeze comparison against the manual.

Ansys Fluid Dynamics Verification Manual, Release 2026 R1, VMFL006
"Multicomponent Species Transport in Pipe Flow", pp. 27-28.  The source the manual
cites: W.M. Kays & M.E. Crawford, "Convective Heat and Mass Transfer", 3rd Ed.,
McGraw-Hill, New York NY, pp. 126-134, 1993.

THE PROBLEM, from the manual's own stated inputs (p.27): circular pipe R = 0.0025 m,
L = 0.1 m; fully developed laminar velocity, u_m = 1 m/s; rho = 1 kg/m3;
mu = 1.0e-5 Pa-s; D_AB = 1.43e-5 m2/s; Y_A(inlet) = 0.5 uniform; Y_A(wall) = 0.9.
Re_D = 500 (laminar); Sc = mu/(rho*D_AB) = 0.6993006993.

This is the GRAETZ problem in mass-transfer form.  With the NORMALIZED mass
fraction the manual's table reports,

    theta = (Y_wall - Y)/(Y_wall - Y_inlet) = (0.9 - Y)/0.4,

eta = r/R and the Graetz coordinate tau = x*D_AB/(2 R^2 u_m), the equation is

    (1 - eta^2) d(theta)/d(tau) = (1/eta) d/d(eta)( eta d(theta)/d(eta) ),

and separating theta = sum_n c_n phi_n(eta) exp(-Lam_n tau) gives the singular
Sturm-Liouville eigenproblem

    -(1/eta) d/d(eta)( eta d(phi)/d(eta) ) = Lam (1 - eta^2) phi,
     phi'(0) = 0 (regularity on the axis),  phi(1) = 0 (fixed wall value),

whose eigenvalues are Lam_n = lambda_n^2 with lambda_n the classical Graetz values
2.704364, 6.679032, 10.673380, ... (Sellars, Tribus & Klein; Kays & Crawford
Table 8-1).  The check that fixes the FACTOR-OF-TWO convention, which is the one
thing easy to get wrong here, is the energy/mass balance: the asymptotic decay
rate of the mixing-cup mean in tau must equal 2*Nu = 2*3.657 = 7.314 = lambda_0^2,
and it does.  A convention giving 2*lambda_0^2 would decay twice as fast and is
excluded by that identity, not by recollection.

WHICH STATISTIC THE MANUAL'S TABLE ACTUALLY REPORTS -- THE PRE-FREEZE FINDING.
The manual's Table .06.1 caption reads "Comparison of Mass Fraction of Species A
Along the Axis".  One line above it, the manual's own prose reads: "the value of
species A is the mass-weighted average of the normalized species mass fraction A
at x-locations".  Those are two different quantities and the manual asserts both.
This module evaluates BOTH and the numbers settle it -- see main().

  * MIXING-CUP (mass-weighted) mean:  worst deviation from the printed targets
    0.048 %.
  * TRUE ON-AXIS (centreline) value:  worst deviation 78.5 %.

The prose is right; the caption is wrong.  The gate frozen in PREREGISTRATION.md
is therefore the MIXING CUP, and the case is set up to measure exactly that.

TWO INSTRUMENTS, DELIBERATELY UNLIKE EACH OTHER:
  A. `modes_fv()`   -- a finite-volume discretisation of the Sturm-Liouville
     operator, diagonally scaled to a symmetric tridiagonal standard eigenproblem
     and solved with scipy.linalg.eigh_tridiagonal.  The axis singularity is
     handled exactly by a zero-area face, so no series expansion about eta = 0 is
     needed.  ORIGIN: this instrument was written by an earlier `ansys-verification`
     lane on 2026-08-26 (04:49Z) and left UNCOMMITTED in the worktree; it is
     carried here with that attribution, unchanged in method.
  B. `modes_shoot()` -- a shooting method: fixed-step vectorised RK4 integration of
     the ODE from the axis to the wall, with brentq on phi(1; Lam) = 0.  It shares
     no code, no discretisation and no library routine with A.

They agree to 3.3e-07 relative on the ten station values.  NOTHING HERE IS
DIGITISED FROM A FIGURE AND NOTHING IS READ BACK FROM THE MANUAL'S TABLE; the
manual's printed targets are quoted BESIDE the lab's own values as an INDEPENDENT
CORROBORATION, and they are the GATE only because PREREGISTRATION.md freezes them
as the gate.

TIER, stated here so no reader infers otherwise from this file: the reference is
ANALYTICAL/closed-form.  Under PREREG_TEMPLATE Amendment 1 a closed form buys V and
NEVER P, so VMFL006's ceiling is GATE REACHED, not PASS -- band met is CODE
VERIFICATION, not a validation credential.

NO `assert` CARRIES ANY GUARD (PREREG_TEMPLATE Amendment 6); `python3 -O` strips
them, so every refusal below is an explicit sys.exit.

  python3 graetz_reference_vmfl006.py            # the table and the comparison
  python3 graetz_reference_vmfl006.py --selftest # drive the derivation's own checks
"""
import sys
import numpy as np
from scipy.linalg import eigh_tridiagonal
from scipy.optimize import brentq

R_PIPE = 0.0025          # m    manual p.27
L_PIPE = 0.1             # m    manual p.27
U_MEAN = 1.0             # m/s  manual p.27
D_AB   = 1.43e-05        # m2/s manual p.27
RHO    = 1.0             # kg/m3
MU     = 1.0e-05         # Pa-s
Y_IN   = 0.5             # manual p.27
Y_WALL = 0.9             # manual p.27

STATIONS = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10]   # m

# The manual's PRINTED Kays & Crawford targets (p.28, Table .06.1).
MANUAL_TARGETS = [0.8225, 0.7308, 0.6593, 0.5992, 0.5469,
                  0.5006, 0.4589, 0.4212, 0.3869, 0.3555]
# Ansys Fluent's own reported values (p.28) -- CONTEXT ONLY, never a gate.
FLUENT_VALUES  = [0.8227, 0.7309, 0.6594, 0.5993, 0.5471,
                  0.5007, 0.4591, 0.4215, 0.3872, 0.3557]
# The manual's printed "Ratio" column (p.28) -- see ratio_column_finding().
MANUAL_RATIOS  = [1.002, 1.001, 1.002, 1.002, 1.004,
                  1.002, 1.004, 1.007, 1.008, 1.006]

# Classical Graetz eigenvalues lambda_n (Sellars, Tribus & Klein; Kays & Crawford
# Table 8-1).  Lam_n = lambda_n^2 in this file's convention.
CLASSICAL_LAMBDA = [2.704364, 6.679032, 10.673380, 14.671077, 18.669870]
NU_FULLY_DEVELOPED = 3.6567934722


def tau_of_x(x):
    """The Graetz coordinate of this problem: tau = x*D_AB/(2 R^2 u_m)."""
    return x * D_AB / (2.0 * R_PIPE * R_PIPE * U_MEAN)


# ----------------------------------------------------- INSTRUMENT A: finite volume
def modes_fv(ncell=8000, nmode=60):
    """First nmode (lambda, I, J) by a finite-volume Sturm-Liouville eigenproblem.

    Written by an earlier ansys-verification lane (2026-08-26 04:49Z, uncommitted
    in the worktree) and carried here unchanged in method, with attribution."""
    d = 1.0 / ncell
    eta = (np.arange(ncell) + 0.5) * d          # cell centres
    f_out = (np.arange(ncell) + 1.0) * d        # outer face radius of each cell
    f_in = np.arange(ncell) * d                 # inner face radius (0 on the axis
                                                # cell -> the singularity carries
                                                # zero area, no special case needed)
    a_diag = (f_out + f_in) / d**2
    a_diag[-1] = (2.0 * 1.0 + f_in[-1]) / d**2  # wall: phi = 0 half a cell beyond
    a_off = -f_out[:-1] / d**2
    wgt = (1.0 - eta**2) * eta                  # Sturm-Liouville weight
    s = 1.0 / np.sqrt(wgt)
    w, v = eigh_tridiagonal(a_diag * s * s, a_off * s[:-1] * s[1:],
                            select="i", select_range=(0, nmode - 1))
    lam = np.sqrt(w)
    phi = v * s[:, None]
    phi = phi / phi[0, :]                       # normalise phi(axis) = 1
    I = d * (phi * wgt[:, None]).sum(0)
    J = d * (phi**2 * wgt[:, None]).sum(0)
    return lam, I, J


# --------------------------------------------------------- INSTRUMENT B: shooting
_E0 = 1e-8


def _rk4(Lam, nstep=40000, want_profile=False):
    """Vectorised fixed-step RK4 of phi'' + phi'/eta + Lam*(1-eta^2)*phi = 0."""
    Lam = np.atleast_1d(np.asarray(Lam, dtype=float))
    h = (1.0 - _E0) / nstep
    y0 = 1.0 - Lam * _E0**2 / 4.0
    y1 = -Lam * _E0 / 2.0
    e = _E0
    prof = [y0.copy()] if want_profile else None

    def dv(e, a, b):
        return b, -b / e - Lam * (1.0 - e * e) * a

    for _ in range(nstep):
        k1a, k1b = dv(e, y0, y1)
        k2a, k2b = dv(e + h / 2, y0 + h / 2 * k1a, y1 + h / 2 * k1b)
        k3a, k3b = dv(e + h / 2, y0 + h / 2 * k2a, y1 + h / 2 * k2b)
        k4a, k4b = dv(e + h, y0 + h * k3a, y1 + h * k3b)
        y0 = y0 + h / 6 * (k1a + 2 * k2a + 2 * k3a + k4a)
        y1 = y1 + h / 6 * (k1b + 2 * k2b + 2 * k3b + k4b)
        e += h
        if want_profile:
            prof.append(y0.copy())
    return (y0, np.array(prof)) if want_profile else y0


def modes_shoot(nmode=14, nstep=40000):
    """First nmode (lambda, I, J) by shooting. Shares no code with modes_fv()."""
    hi = (4 * (nmode + 1) + 8.0 / 3.0) ** 2 * 1.2
    scan = np.linspace(1.0, hi, 6000)
    vals = _rk4(scan)
    roots = []
    for i in range(1, len(scan)):
        if vals[i - 1] * vals[i] < 0:
            roots.append(brentq(lambda L: float(_rk4(L)[0]), scan[i - 1], scan[i],
                                xtol=1e-11, rtol=8.9e-16))
            if len(roots) == nmode:
                break
    lam, I, J = [], [], []
    eta = np.linspace(_E0, 1.0, nstep + 1)
    w = (1.0 - eta**2) * eta
    for Lm in roots:
        _, prof = _rk4(Lm, nstep=nstep, want_profile=True)
        ph = prof[:, 0]
        lam.append(np.sqrt(Lm))
        I.append(np.trapezoid(ph * w, eta))
        J.append(np.trapezoid(ph * ph * w, eta))
    return np.array(lam), np.array(I), np.array(J)


# ------------------------------------------------------------------ the statistics
def theta_mixcup(tau, lam, I, J):
    """MIXING-CUP (mass-weighted) mean -- the statistic the manual's PROSE names."""
    return float((4.0 * (I**2 / J) * np.exp(-(lam**2) * tau)).sum())


def theta_axis(tau, lam, I, J):
    """TRUE ON-AXIS value (phi_n(0) = 1) -- the statistic the manual's CAPTION names."""
    return float(((I / J) * np.exp(-(lam**2) * tau)).sum())


def lab_reference(instrument="shoot"):
    lam, I, J = modes_shoot() if instrument == "shoot" else modes_fv()
    mix = [theta_mixcup(tau_of_x(x), lam, I, J) for x in STATIONS]
    ax = [theta_axis(tau_of_x(x), lam, I, J) for x in STATIONS]
    return mix, ax, (lam, I, J)


def ratio_column_finding():
    """A SECOND, separate observation about the manual's own table, measured here.

    The printed Ratio column is NOT Fluent/Target.  For all ten rows, to the
    printed precision, ratio_printed == 1 + 10*(Fluent/Target - 1).  Returns the
    two candidate ratios per row so a reader can check it without re-deriving it.
    It touches NO gate: the gate is the Target column."""
    out = []
    for f, t, r in zip(FLUENT_VALUES, MANUAL_TARGETS, MANUAL_RATIOS):
        plain = f / t
        tenx = 1.0 + 10.0 * (plain - 1.0)
        out.append({"target": t, "fluent": f, "printed_ratio": r,
                    "fluent_over_target": plain,
                    "one_plus_ten_delta": tenx,
                    "printed_matches_10x": abs(round(tenx, 3) - r) < 5e-4,
                    "printed_matches_plain": abs(round(plain, 3) - r) < 5e-4})
    return out


def main():
    mix, ax, (lam, I, J) = lab_reference("shoot")
    mfv, afv, _ = lab_reference("fv")
    print("VMFL006 -- lab-evaluated Graetz reference (manual pp.27-28)")
    print("  Re_D = %.6g   Sc = %.10g   D_AB = %g m2/s   tau(x) = x*D/(2 R^2 u_m)"
          % (RHO * U_MEAN * 2 * R_PIPE / MU, MU / (RHO * D_AB), D_AB))
    print("  shooting eigenvalues lambda_n : " + ", ".join("%.6f" % l for l in lam[:5]))
    print("  finite-volume   lambda_n      : " + ", ".join("%.6f" % l for l in modes_fv()[0][:5]))
    print("  classical (Sellars/Tribus/Klein): " + ", ".join("%.6f" % l for l in CLASSICAL_LAMBDA))
    print("  convention check: asymptotic decay rate in tau = lambda_0^2 = %.6f "
          "must equal 2*Nu = %.6f" % (lam[0] ** 2, 2 * NU_FULLY_DEVELOPED))
    print()
    print("  x (m)   tau         MIXING CUP (lab)   ON AXIS (lab)     manual   dev_mix    dev_axis")
    for x, m, a, t in zip(STATIONS, mix, ax, MANUAL_TARGETS):
        print("   %.2f   %.8f   %.9f      %.9f     %.4f   %+7.4f %%  %+8.3f %%"
              % (x, tau_of_x(x), m, a, t, 100 * (m - t) / t, 100 * (a - t) / t))
    wm = max(abs(m - t) / t for m, t in zip(mix, MANUAL_TARGETS))
    wa = max(abs(a - t) / t for a, t in zip(ax, MANUAL_TARGETS))
    wi = max(abs(m - f) / f for m, f in zip(mix, mfv))
    print()
    print("  worst |MIXING CUP - manual target| / target = %.5f %%" % (100 * wm))
    print("  worst |ON AXIS    - manual target| / target = %.5f %%" % (100 * wa))
    print("  worst |shooting - finite volume| / value    = %.3e  (two instruments)" % wi)
    print()
    print("  => the manual's Table .06.1 numbers are the MIXING-CUP MEAN, as its own")
    print("     prose says, NOT the on-axis value its caption says.")
    print()
    print("  LAB_MIXCUP (shooting)      = [" + ", ".join("%.9f" % v for v in mix) + "]")
    print("  LAB_MIXCUP (finite volume) = [" + ", ".join("%.9f" % v for v in mfv) + "]")
    print()
    rf = ratio_column_finding()
    n10 = sum(1 for r in rf if r["printed_matches_10x"])
    npl = sum(1 for r in rf if r["printed_matches_plain"])
    print("  manual's printed Ratio column: matches Fluent/Target in %d of 10 rows;" % npl)
    print("  matches 1 + 10*(Fluent/Target - 1) in %d of 10 rows. Reported, gates nothing."
          % n10)


def selftest():
    ok = True

    def chk(n, c, d=""):
        nonlocal ok
        print(("  [PASS] " if c else "  [FAIL] ") + n + ("" if not d else "   " + str(d)))
        ok = ok and bool(c)

    print("graetz_reference_vmfl006.py --selftest")
    lam_s, I_s, J_s = modes_shoot()
    lam_f, I_f, J_f = modes_fv()
    for k in range(5):
        chk("shooting lambda_%d matches the classical %.6f" % (k, CLASSICAL_LAMBDA[k]),
            abs(lam_s[k] - CLASSICAL_LAMBDA[k]) < 1e-5, "%.9f" % lam_s[k])
        chk("finite-volume lambda_%d matches the classical %.6f" % (k, CLASSICAL_LAMBDA[k]),
            abs(lam_f[k] - CLASSICAL_LAMBDA[k]) < 1e-4, "%.9f" % lam_f[k])
    chk("eigenvalues strictly increasing (shooting)", bool(np.all(np.diff(lam_s) > 0)))

    # THE CONVENTION CHECK. This is the one that would catch the factor-of-two error,
    # and it is an INDEPENDENT physical identity (fully developed Nusselt number),
    # not a restatement of the eigenproblem.
    chk("asymptotic decay rate in tau equals 2*Nu = %.6f (fixes the factor-of-2 convention)"
        % (2 * NU_FULLY_DEVELOPED),
        abs(lam_s[0] ** 2 - 2 * NU_FULLY_DEVELOPED) < 1e-4, "%.9f" % (lam_s[0] ** 2))

    mix_s, ax_s, _ = lab_reference("shoot")
    mix_f, ax_f, _ = lab_reference("fv")
    chk("theta_mixcup strictly decreasing downstream",
        all(a > b for a, b in zip(mix_s[:-1], mix_s[1:])))
    chk("theta_axis strictly decreasing downstream",
        all(a > b for a, b in zip(ax_s[:-1], ax_s[1:])))
    chk("theta_axis is ABOVE theta_mixcup everywhere (the core is the last to mix)",
        all(a > m for a, m in zip(ax_s, mix_s)))

    wi = max(abs(a - b) / b for a, b in zip(mix_s, mix_f))
    chk("the TWO independent instruments agree to 1e-5", wi < 1e-5, "%.3e" % wi)

    wm = max(abs(m - t) / t for m, t in zip(mix_s, MANUAL_TARGETS))
    wa = max(abs(a - t) / t for a, t in zip(ax_s, MANUAL_TARGETS))
    chk("the MIXING CUP corroborates the manual's printed targets within 0.1 %",
        wm < 1e-3, "worst %.5f %%" % (100 * wm))
    chk("the ON-AXIS value does NOT (this is the finding, and it is what makes the "
        "mixing-cup agreement evidence rather than a coincidence)",
        wa > 0.1, "worst %.3f %%" % (100 * wa))

    chk("Sc = 0.6993006993", abs(MU / (RHO * D_AB) - 0.6993006993) < 1e-9)
    chk("Re_D = 500 (laminar, as the manual states)",
        abs(RHO * U_MEAN * 2 * R_PIPE / MU - 500.0) < 1e-9)
    chk("tau(x = 0.10 m) = 0.1144", abs(tau_of_x(0.10) - 0.1144) < 1e-12, tau_of_x(0.10))

    rf = ratio_column_finding()
    chk("the manual's printed Ratio column matches 1 + 10*(Fluent/Target - 1) in ALL ten rows",
        all(r["printed_matches_10x"] for r in rf),
        "%d/10" % sum(1 for r in rf if r["printed_matches_10x"]))
    chk("...and matches the plain Fluent/Target in NONE of them",
        not any(r["printed_matches_plain"] for r in rf),
        "%d/10" % sum(1 for r in rf if r["printed_matches_plain"]))

    print("SELFTEST: %s" % ("all checks passed" if ok else "FAILURES PRESENT"))
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    main()
    sys.exit(0)
