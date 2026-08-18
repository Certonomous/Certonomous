"""
F4 hypersonic blunt-body closed-form gates:
  1. Billig (1967) shock standoff / shock-shape correlation, cylinder-wedge branch
     (2D circular-cylinder-nosed body -- the geometry used in this campaign).
  2. Modified Newtonian surface-pressure theory (Lees), with Cp_max from the
     exact Rayleigh-Pitot normal-shock formula.

Both are reproduced here EXACTLY as printed in the primary citable source:

    Anderson, John D., Jr., "Hypersonic and High-Temperature Gas Dynamics",
    2nd ed., AIAA Education Series, 2006 -- Sec. 5.4 "Correlations for
    Hypersonic Shock-Wave Shapes" (Eqs. 5.36-5.38) and Sec. 3.3 "Modified
    Newtonian Law" (Eqs. 3.15-3.19).

Section 5.4's own citation for the shock-shape/standoff correlation itself:
    Billig, F. S., "Shock-Wave Shapes Around Spherical- and Cylindrical-Nosed
    Bodies," Journal of Spacecraft and Rockets, Vol. 4, No. 6, June 1967,
    pp. 822-823.  (Anderson's reference [69].)

Section 3.3's own citation for the modified-Newtonian modification itself:
    Lees, L. (Anderson's reference [8]; original modification to straight
    Newtonian sin^2(theta) law, replacing the constant 2 with the exact
    Rayleigh-Pitot Cp_max(M1, gamma)).

VERIFICATION OF THE PRIMARY SOURCE (done before any use, per the F3/F4 hard
rule against fabricated citations): the exact wording, equation numbers and
page numbers above were read directly out of the textbook PDF (fetched from
a university OCW mirror and OCR'd via pdftotext) in this session -- not
recalled from memory. Cross-checked initial web-search summaries claiming a
"4.76" cylinder-wedge coefficient turned out to be third-party paraphrase
noise; the number printed in the primary textbook source (and independently
matching the value we started this campaign with) is exp[4.67/M_inf^2].
This is why the primary PDF was fetched and grepped rather than trusting the
search snippets. See F4_hypersonic_blunt_body.md Sec. 0 for the full
verification trail.

No CFD output is used anywhere in this file -- exactly the same discipline as
F3_runs/exact_theory.py, which this module imports from for the normal-shock
building block (already validated to 6 significant figures against NASA GRC's
analytic oblique-shock page in the F3 campaign).
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "F3_runs"))
from exact_theory import normal_shock, GAMMA  # noqa: E402  (reuse, don't rebuild)


# ----------------------------------------------------------------------------
# Billig (1967) shock standoff / shock-shape correlation (Anderson Eqs 5.36-5.38)
# ----------------------------------------------------------------------------
def billig_delta_over_R(M1, kind="cylinder"):
    """Eq. (5.37). kind='cylinder' -> cylinder-wedge branch (2D, our geometry);
    kind='sphere' -> sphere-cone (axisymmetric) branch, included only for
    reference/contrast, not used as this campaign's CFD gate."""
    if kind == "cylinder":
        return 0.386 * np.exp(4.67 / M1**2)
    elif kind == "sphere":
        return 0.143 * np.exp(3.24 / M1**2)
    else:
        raise ValueError(kind)


def billig_Rc_over_R(M1, kind="cylinder"):
    """Eq. (5.38): radius of curvature of the shock at its vertex."""
    if kind == "cylinder":
        return 1.386 * np.exp(1.8 / (M1 - 1) ** 0.75)
    elif kind == "sphere":
        return 1.143 * np.exp(0.54 / (M1 - 1) ** 1.2)
    else:
        raise ValueError(kind)


def billig_shock_x_of_y(y, R, M1, kind="cylinder"):
    """Eq. (5.36): shock shape x(y), body nose at x=-R (stagnation point),
    freestream in +x. beta = wave angle at y->infinity; for a plain cylinder
    (no downstream wedge/cone afterbody -- the flow downstream of the nose is
    parallel to freestream, i.e. body surface parallel to freestream at
    infinity), Anderson states beta is a Mach wave, beta = asin(1/M1)."""
    delta = billig_delta_over_R(M1, kind) * R
    Rc = billig_Rc_over_R(M1, kind) * R
    beta = np.arcsin(1.0 / M1)
    cotb2 = 1.0 / np.tan(beta) ** 2
    return R + delta - Rc * cotb2 * (np.sqrt(1 + y**2 * np.tan(beta) ** 2 / Rc**2) - 1)


def billig_shock_y_of_x(x, R, M1, kind="cylinder"):
    """Invert Eq. (5.36) for y given x (valid on the single-valued upper
    branch, y>=0); used only for a priori domain sizing (keeping the CFD
    farfield boundary outside the correlation's predicted shock), NOT as
    part of the gate itself."""
    delta = billig_delta_over_R(M1, kind) * R
    Rc = billig_Rc_over_R(M1, kind) * R
    beta = np.arcsin(1.0 / M1)
    cotb2 = 1.0 / np.tan(beta) ** 2
    K = R + delta - x
    val = 1 + K / (Rc * cotb2)
    inside = val**2 - 1
    if inside < 0:
        return 0.0
    return np.sqrt((Rc / np.tan(beta)) ** 2 * inside)


# ----------------------------------------------------------------------------
# Modified Newtonian surface-pressure theory (Anderson Eqs 3.15-3.19, Lees)
# ----------------------------------------------------------------------------
def cp_max_rayleigh_pitot(M1, gamma=GAMMA):
    """Eq. (3.18)/(3.19): Cp at the stagnation point behind a normal shock,
    built from the ALREADY-VALIDATED normal_shock() (F3, 6 sig figs vs NASA
    GRC) plus the standard isentropic p0/p relation (elementary, used already
    and implicitly cross-checked throughout F3's Taylor-Maccoll module).
        Cp_max = (2/(gamma*M1^2)) * (p02/p1 - 1)
    """
    ns = normal_shock(M1, gamma)  # normal shock AT the freestream Mach (stagnation streamline)
    p02_p01 = ns["p02_p01"]
    g = gamma
    p01_p1 = (1 + (g - 1) / 2 * M1**2) ** (g / (g - 1))  # isentropic, upstream of shock
    p02_p1 = p02_p01 * p01_p1
    return 2.0 / (g * M1**2) * (p02_p1 - 1)


def modified_newtonian_cp(theta_incl_rad, M1, gamma=GAMMA):
    """Eq. (3.15): Cp = Cp_max * sin^2(theta), theta = local surface
    inclination TO THE FREESTREAM (theta=90deg at a stagnation point, where
    the local tangent plane is normal to the freestream; theta=0 where the
    surface is parallel to the freestream, e.g. far around a cylinder
    shoulder)."""
    cpmax = cp_max_rayleigh_pitot(M1, gamma)
    return cpmax * np.sin(theta_incl_rad) ** 2


def modified_newtonian_cp_of_theta_c(theta_c_rad, M1, gamma=GAMMA):
    """Convenience form parametrized by theta_c = angle measured AROUND the
    body FROM the stagnation point (theta_c=0 at stagnation, theta_c=90deg at
    the shoulder) -- this is the natural coordinate for our mesh/sampling.
    theta_incl = 90deg - theta_c, so sin^2(theta_incl) = cos^2(theta_c):
        Cp(theta_c) = Cp_max * cos^2(theta_c)
    the algebraically-equivalent, more commonly printed form of Eq. (3.15)
    for a body measured from its stagnation point."""
    cpmax = cp_max_rayleigh_pitot(M1, gamma)
    return cpmax * np.cos(theta_c_rad) ** 2


# ----------------------------------------------------------------------------
# Self-check when run directly
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    print("Billig cylinder-wedge standoff and Rc, M=6,7,8, R=1:")
    for M in (6.0, 7.0, 8.0):
        d = billig_delta_over_R(M)
        rc = billig_Rc_over_R(M)
        cpmax = cp_max_rayleigh_pitot(M)
        print(f"  M={M:.1f}: delta/R={d:.4f}  Rc/R={rc:.4f}  Cp_max={cpmax:.4f}")
    print()
    print("Cross-check: as M1 -> inf, Cp_max should -> 1.839 (gamma=1.4), per Anderson p.62:")
    print(f"  Cp_max(M=50) = {cp_max_rayleigh_pitot(50.0):.4f}  (limit: 1.839)")
