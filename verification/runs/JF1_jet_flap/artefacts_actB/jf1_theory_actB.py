#!/usr/bin/env python3
"""
JF1 ACT B -- jet-flap thin-aerofoil THEORY MODULE, and the numbers the one-page
result sheet quotes.

SOURCE OF THE FORMULAE, VERIFIED BY VISUAL PAGE READ (CLAUDE.md rule 15, L-144)
------------------------------------------------------------------------------
Williams, J., Butler, S. F. J. and Wood, M. N. (1961),
    "The Aerodynamics of Jet Flaps",
    Aeronautical Research Council Reports and Memoranda No. 3304
    (Ministry of Aviation, H.M.S.O. 1963).
File read:
  docs/papers/powered_lift_and_ducted_propulsion/
      williams_butler_wood_1961_arc_rm3304_aerodynamics_of_jet_flaps.pdf
Pages rendered at 170-200 dpi with pdftoppm and read AS IMAGES on 2026-08-31 by
this module's author:
  PDF p.1  -- title page (rule-15 discharge, transcribed in RULE15_TITLE_PAGE)
  PDF p.4  = printed p.3  -- jet-reaction sentence, C_mu sin(theta + alpha)
  PDF p.6  = printed p.5  -- equations (1), (2), (3)
  PDF p.18 = printed p.17 -- reference list, refs 26 and 27
The OCR sidecar (.txt) states in its own header that equations are corrupted and
was NOT used for any number here.

THE GROUPING -- THIS IS THE POINT OF THE MODULE
-----------------------------------------------
Printed p.5, eq. (2), read off the page image:

    (dCL/dtheta)_inf = [ 4 pi C_mu' ( 1 + 0.151 C_mu'^(1/2) + 0.139 C_mu' ) ]^(1/2)
    (dCL/dalpha)_inf = 2 pi ( 1 + 0.151 C_mu'^(1/2) + 0.219 C_mu' )

The series sits INSIDE the square root, together with 4 pi C_mu'.  A form that
circulated in this lab put the series OUTSIDE the root,

    dCL/dtheta = 2 sqrt(pi C_mu) ( 1 + 0.151 sqrt(C_mu) + 0.139 C_mu )   <-- WRONG

which is the correct form multiplied by sqrt(S), S = 1 + 0.151 sqrt(C_mu) +
0.139 C_mu -- a one-signed, monotonically growing overprediction (+2.0% at
C_mu = 0.05 rising to +7.3% at C_mu = 0.40).  All three constants are identical
between the two forms, so a check of the CONSTANTS alone returns "all correct".
Both forms are implemented below; only `dCL_dtau` is ever used for a result.
`dCL_dtau_WRONG_GROUPING_DO_NOT_USE` exists so the bias can be printed.

SCOPE
-----
This case is strictly two-dimensional, so the source's sectional coefficient
C_mu' equals the case's jet momentum coefficient C_mu_jet, and the source's
finite-aspect-ratio factor F(A, C_mu) of eq. (3) is NOT used.

The three constants 0.151, 0.139, 0.219 are FIT PARAMETERS of an interpolation
formula (printed p.5: "simple interpolation formulae fit the computed values for
c_f/c = 0 (T.E. blowing) at C_mu'-values of 1 and 4 and asymptotically as
C_mu' -> 0").  They are never Taylor-expanded, truncated or re-derived; the
formulae are used whole or not at all.  The swept range 0 <= C_mu_jet <= 0.40
lies inside the fitted range.
"""

from __future__ import annotations

import json
import math
import os
import re
import sys

# ----------------------------------------------------------------------------
# Rule-15 record: transcribed from the page image, not from any manifest.
# ----------------------------------------------------------------------------
RULE15_TITLE_PAGE = (
    "PDF p.1, read as a 200 dpi page image on 2026-08-31: "
    "'ROYAL AIRCRAFT ESTABLISHMENT BEDFORD' (library stamp) / "
    "'R. & M. No. 3304' / royal arms / "
    "'MINISTRY OF AVIATION' / "
    "'AERONAUTICAL RESEARCH COUNCIL REPORTS AND MEMORANDA' / "
    "'The Aerodynamics of Jet Flaps' / "
    "'By J. WILLIAMS, S. F. J. BUTLER and M. N. WOOD' / "
    "'LONDON: HER MAJESTY'S STATIONERY OFFICE' / '1963' / "
    "'THIRTEEN SHILLINGS NET'"
)

RULE15_REFERENCE_26 = (
    "PDF p.18 = printed p.17, read as a 170 dpi page image on 2026-08-31: "
    "'26  D. A. Spence -- The lift-coefficient of a thin, jet-flapped wing. "
    "Proc. Roy. Soc. A. Vol. 238. pp. 46 to 68. 1956.'"
)

RULE15_EQ2_INTRODUCTION = (
    "PDF p.6 = printed p.5, read as a 200 dpi page image on 2026-08-31: "
    "'The following simple interpolation formulae fit the computed values for "
    "c_f/c = 0 (T.E. blowing) at C_mu'-values of 1 and 4 and asymptotically as "
    "C_mu' -> 0.'  NO reference number is attached to eq. (2) on that page."
)

RULE15_SPENCE_ATTRIBUTION = (
    "PDF p.4 = printed p.3, read as a 200 dpi page image on 2026-08-31: "
    "'The two-dimensional problem was solved by Spence using a treatment akin "
    "to classical \"mean line\" theory, both for ejection from the trailing "
    "edge[26] and over a plain (hinged) flap[27].'  This attributes the "
    "UNDERLYING THEORY to Spence; the interpolation formula of eq. (2) is "
    "printed by Williams, Butler and Wood and carries no Spence citation."
)

RULE15_JET_REACTION = (
    "PDF p.4 = printed p.3, read as a 200 dpi page image on 2026-08-31: "
    "'The total lift C_L on the jet-flap aerofoil represents a considerable "
    "magnification of the direct jet-reaction lift C_mu sin(theta + alpha) "
    "from the corresponding vertical component of the jet momentum, because of "
    "the additional pressure lift on the aerofoil.'"
)

# Spence (1956) is NOT held by this lab: no title page of it has been read here.
SPENCE_1956_HELD = False

# ----------------------------------------------------------------------------
# The three fit constants, exactly as printed (0.151, 0.139, 0.219).
# ----------------------------------------------------------------------------
A1 = 0.151
A2_THETA = 0.139
A2_ALPHA = 0.219

TAU_RAD = math.pi / 6.0          # 30 deg exactly, per the case registration
CMU_SWEEP = (0.0, 0.05, 0.10, 0.20, 0.40)


def series_theta(cmu: float) -> float:
    """S(C_mu) = 1 + 0.151 sqrt(C_mu) + 0.139 C_mu -- the bracket of eq. (2a)."""
    if cmu < 0.0:
        raise ValueError("C_mu must be non-negative")
    return 1.0 + A1 * math.sqrt(cmu) + A2_THETA * cmu


def series_alpha(cmu: float) -> float:
    """1 + 0.151 sqrt(C_mu) + 0.219 C_mu -- the bracket of eq. (2b)."""
    if cmu < 0.0:
        raise ValueError("C_mu must be non-negative")
    return 1.0 + A1 * math.sqrt(cmu) + A2_ALPHA * cmu


def dCL_dtau(cmu: float) -> float:
    """(dCL/dtheta)_inf, per radian.  SERIES INSIDE THE ROOT -- eq. (2a)."""
    return math.sqrt(4.0 * math.pi * cmu * series_theta(cmu))


def dCL_dtau_WRONG_GROUPING_DO_NOT_USE(cmu: float) -> float:
    """The circulated form, series OUTSIDE the root.  Printed for contrast only."""
    return 2.0 * math.sqrt(math.pi * cmu) * series_theta(cmu)


def dCL_dalpha(cmu: float) -> float:
    """(dCL/dalpha)_inf, per radian -- eq. (2b).  Not square-rooted."""
    return 2.0 * math.pi * series_alpha(cmu)


def CL_theory_total(cmu: float, tau: float = TAU_RAD, alpha: float = 0.0) -> float:
    """
    Eq. (1): (C_L)_inf = theta (dCL/dtheta)_inf + alpha (dCL/dalpha)_inf.

    This is the TOTAL sectional lift of the theory.  It ALREADY CONTAINS the
    direct jet reaction (printed p.3: the total lift is a 'magnification of the
    direct jet-reaction lift C_mu sin(theta + alpha)').  It is therefore never
    summed with `jet_reaction` -- `jet_reaction` is a PART of it, reported in its
    own column, and `CL_theory_circulation` is what is left when it is removed.
    """
    return tau * dCL_dtau(cmu) + alpha * dCL_dalpha(cmu)


def jet_reaction(cmu: float, tau: float = TAU_RAD, alpha: float = 0.0) -> float:
    """Direct jet-reaction lift, C_mu sin(theta + alpha).  Printed p.3."""
    return cmu * math.sin(tau + alpha)


def CL_theory_circulation(cmu: float, tau: float = TAU_RAD, alpha: float = 0.0) -> float:
    """Theory total MINUS the direct jet reaction: the pressure/circulation part."""
    return CL_theory_total(cmu, tau, alpha) - jet_reaction(cmu, tau, alpha)


def marginal_dCL_dCmu(cmu: float, tau: float = TAU_RAD) -> float:
    """
    d(CL_theory_total)/d(C_mu) at fixed tau, alpha = 0.  Analytic.

    f(C_mu) = 4 pi ( C_mu + 0.151 C_mu^1.5 + 0.139 C_mu^2 ),  CL = tau sqrt(f)
    df/dC_mu = 4 pi ( 1 + 1.5*0.151 sqrt(C_mu) + 2*0.139 C_mu )
    dCL/dC_mu = tau (df/dC_mu) / (2 sqrt(f))

    Diverges as C_mu -> 0 like tau sqrt(pi / C_mu): the square-root law means the
    FIRST unit of jet momentum is worth unboundedly more than the last.
    """
    if cmu <= 0.0:
        return float("inf")
    f = 4.0 * math.pi * (cmu + A1 * cmu ** 1.5 + A2_THETA * cmu * cmu)
    dfdc = 4.0 * math.pi * (1.0 + 1.5 * A1 * math.sqrt(cmu) + 2.0 * A2_THETA * cmu)
    return tau * dfdc / (2.0 * math.sqrt(f))


def marginal_check_fd(cmu: float, tau: float = TAU_RAD, h: float = 1e-6) -> float:
    """Central finite difference, to check `marginal_dCL_dCmu` against itself."""
    return (CL_theory_total(cmu + h, tau) - CL_theory_total(cmu - h, tau)) / (2.0 * h)


# ----------------------------------------------------------------------------
# Self-verification of the implementation against the registered 10-digit values.
# These four numbers were computed independently and frozen in
# verification/campaign/JF1_PREREGISTRATION.md section 1.4 before this module
# existed.  If the implementation does not reproduce them, this module refuses.
# ----------------------------------------------------------------------------
REGISTERED_CL_THEORY = {
    0.05: 0.4234034434,
    0.10: 0.6047756775,
    0.20: 0.8687421542,
    0.40: 1.2594769538,
}
REGISTERED_S = {
    0.05: 1.0407146265,
    0.10: 1.0616503927,
    0.20: 1.0953292529,
    0.40: 1.1511007853,
}


def self_verify(tol: float = 5e-10) -> list[str]:
    """Return the verification lines; raise SystemExit(2) on any mismatch."""
    lines = []
    for cmu, want in sorted(REGISTERED_CL_THEORY.items()):
        got = CL_theory_total(cmu)
        if abs(got - want) > tol:
            print(f"REFUSE: CL_theory({cmu}) = {got!r} != registered {want!r}",
                  file=sys.stderr)
            raise SystemExit(2)
        lines.append(f"  CL_theory(C_mu={cmu:.2f}) = {got:.10f}  == registered "
                     f"{want:.10f}  (|d| = {abs(got-want):.2e})")
    for cmu, want in sorted(REGISTERED_S.items()):
        got = series_theta(cmu)
        if abs(got - want) > tol:
            print(f"REFUSE: S({cmu}) = {got!r} != registered {want!r}", file=sys.stderr)
            raise SystemExit(2)
    # analytic derivative vs finite difference
    for cmu in (0.05, 0.10, 0.20, 0.40):
        a, f = marginal_dCL_dCmu(cmu), marginal_check_fd(cmu)
        if abs(a - f) > 1e-6 * max(1.0, abs(a)):
            print(f"REFUSE: marginal({cmu}) analytic {a!r} != fd {f!r}", file=sys.stderr)
            raise SystemExit(2)
        lines.append(f"  dCL/dC_mu(C_mu={cmu:.2f}) analytic {a:.8f} == "
                     f"finite-difference {f:.8f}")
    # the unblown limit must be exactly zero lift at alpha = 0
    if CL_theory_total(0.0) != 0.0:
        print("REFUSE: CL_theory(0) is not exactly zero", file=sys.stderr)
        raise SystemExit(2)
    lines.append("  CL_theory(C_mu=0.00) = 0.0000000000 exactly (unblown, alpha = 0)")
    return lines


# ----------------------------------------------------------------------------
# Measured lift, read from the solver's own force-coefficient history.
# ----------------------------------------------------------------------------
RUN_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

CASES = [
    (0.00, "JF1_L1_UNBLOWN_A0"),
    (0.05, "JF1_L1_BLOWN_CMU005_A0"),
    (0.10, "JF1_L1_BLOWN_CMU010_A0"),
    (0.20, "JF1_L1_BLOWN_CMU020_A0"),
    (0.40, "JF1_L1_BLOWN_CMU040_A0"),
]

# Final initial-residuals against the 1e-06 criterion, supplied with this task by
# the supervisor who measured them.  Reproduced here, and independently
# re-extracted from each case's own solver log by `read_final_residuals` below;
# the two are compared and a mismatch REFUSES.
SUPERVISOR_K_RESIDUAL = {
    0.00: 3.457e-06,
    0.05: 5.941e-06,
    0.10: 2.550e-05,
    0.20: 4.572e-05,
    0.40: 1.472e-04,
}

_RES_RE = re.compile(
    r"Solving for (\w+), Initial residual = ([0-9.eE+-]+), "
    r"Final residual = ([0-9.eE+-]+)"
)


def read_final_residuals(case_dir: str) -> dict[str, float]:
    """Last initial-residual seen for each channel in log.simpleFoam."""
    path = os.path.join(case_dir, "log.simpleFoam")
    out: dict[str, float] = {}
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            m = _RES_RE.search(line)
            if m:
                out[m.group(1)] = float(m.group(2))
    if not out:
        raise SystemExit(f"REFUSE: no residual lines parsed from {path}")
    return out


def read_cl_history(case_dir: str) -> list[tuple[float, float]]:
    """(iteration, Cl) from postProcessing/forceCoeffs/0/coefficient.dat."""
    path = os.path.join(case_dir, "postProcessing", "forceCoeffs", "0",
                        "coefficient.dat")
    rows: list[tuple[float, float]] = []
    with open(path, "r", errors="replace") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            f = line.split()
            # column order from the header: Time Cd Cd(f) Cd(r) Cl ...
            rows.append((float(f[0]), float(f[4])))
    if not rows:
        raise SystemExit(f"REFUSE: no coefficient rows parsed from {path}")
    return rows


def measured_row(case_dir: str, window: int = 1000) -> dict:
    """
    Measured aero lift and an honest spread for it.

    The spread is the half range of Cl over the last `window` iterations.  It is
    NOT a discretisation uncertainty and is not presented as one: it is how much
    the number is still moving while the solution tightens.
    """
    hist = read_cl_history(case_dir)
    tail = [cl for _, cl in hist[-window:]]
    lo, hi = min(tail), max(tail)
    return {
        "iterations": hist[-1][0],
        "CL_aero": hist[-1][1],
        "CL_aero_mean_tail": sum(tail) / len(tail),
        "half_range_tail": 0.5 * (hi - lo),
        "window": window,
    }


def collect_measured() -> list[dict]:
    """
    Read every case with ONE code path, and PLANT-CHECK the reader (rule 3):
    a reader that returns ~0 for the unblown row is only evidence if the SAME
    reader is shown returning a large non-zero elsewhere.
    """
    rows = []
    for cmu, name in CASES:
        d = os.path.join(RUN_ROOT, name)
        r = measured_row(d)
        r["C_mu"] = cmu
        r["case_dir"] = d
        r["residuals"] = read_final_residuals(d)
        rows.append(r)

    # --- reader control, refuse rather than degrade -------------------------
    unblown = [r for r in rows if r["C_mu"] == 0.0][0]
    blown = [r for r in rows if r["C_mu"] > 0.0]
    if not blown:
        raise SystemExit("REFUSE: no blown row to prove the reader sees non-zero")
    biggest = max(abs(r["CL_aero"]) for r in blown)
    if biggest < 1e-2:
        raise SystemExit("REFUSE: the Cl reader never returned a large non-zero; "
                         "its near-zero unblown value is not evidence")
    if abs(unblown["CL_aero"]) > 1e-3:
        raise SystemExit("REFUSE: unblown symmetric section at alpha = 0 returned "
                         f"Cl = {unblown['CL_aero']!r}, not near zero")

    # --- residual cross-check against the figures supplied with the task ----
    for r in rows:
        want = SUPERVISOR_K_RESIDUAL[r["C_mu"]]
        got = r["residuals"].get("k")
        if got is None:
            raise SystemExit(f"REFUSE: no k residual in {r['case_dir']}")
        if abs(got - want) > 0.02 * want:
            raise SystemExit(
                f"REFUSE: k residual mismatch at C_mu={r['C_mu']}: log gives "
                f"{got:.4e}, task states {want:.4e}")
    return rows


# ----------------------------------------------------------------------------
def main() -> int:
    out_dir = os.path.dirname(os.path.abspath(__file__))

    print("JF1 ACT B -- JET-FLAP THEORY MODULE")
    print("=" * 78)
    print("SOURCE (rule 15, verified by page image, not by filename or manifest):")
    print("  " + RULE15_TITLE_PAGE)
    print()
    print("IMPLEMENTATION SELF-VERIFICATION against the registered 10-digit values:")
    for line in self_verify():
        print(line)
    print()

    print("THEORY TABLE -- tau = 30 deg = pi/6 exactly, alpha = 0 deg")
    print("-" * 78)
    hdr = (f"{'C_mu':>6} {'S':>12} {'dCL/dtau':>12} {'CL total':>12} "
           f"{'jet react':>12} {'circulation':>12} {'dCL/dC_mu':>12}")
    print(hdr)
    theory_rows = []
    for cmu in CMU_SWEEP:
        row = {
            "C_mu": cmu,
            "S": series_theta(cmu),
            "dCL_dtau": dCL_dtau(cmu),
            "dCL_dalpha": dCL_dalpha(cmu),
            "CL_total": CL_theory_total(cmu),
            "jet_reaction": jet_reaction(cmu),
            "CL_circulation": CL_theory_circulation(cmu),
            "marginal": marginal_dCL_dCmu(cmu),
            "CL_total_wrong_grouping": TAU_RAD * dCL_dtau_WRONG_GROUPING_DO_NOT_USE(cmu),
        }
        row["wrong_grouping_bias_pct"] = (
            100.0 * (row["CL_total_wrong_grouping"] / row["CL_total"] - 1.0)
            if row["CL_total"] > 0 else 0.0)
        theory_rows.append(row)
        m = row["marginal"]
        print(f"{cmu:6.2f} {row['S']:12.8f} {row['dCL_dtau']:12.8f} "
              f"{row['CL_total']:12.8f} {row['jet_reaction']:12.8f} "
              f"{row['CL_circulation']:12.8f} "
              f"{('inf' if m == float('inf') else f'{m:12.6f}'):>12}")
    print()

    print("GROUPING BIAS -- what the circulated form would have added")
    print("-" * 78)
    for row in theory_rows:
        if row["C_mu"] == 0.0:
            continue
        print(f"  C_mu = {row['C_mu']:.2f}: correct {row['CL_total']:.10f}, "
              f"circulated {row['CL_total_wrong_grouping']:.10f}, "
              f"bias {row['wrong_grouping_bias_pct']:+.4f} %")
    print()

    print("DIMINISHING RETURN -- lift bought per unit of jet momentum coefficient")
    print("-" * 78)
    first = theory_rows[1]   # C_mu 0.05
    last = theory_rows[-1]   # C_mu 0.40
    third = theory_rows[-2]  # C_mu 0.20
    seg_lo = first["CL_total"] / 0.05
    seg_hi = (last["CL_total"] - third["CL_total"]) / 0.20
    print(f"  first 0.05 of blowing:      {seg_lo:.4f} lift per unit C_mu")
    print(f"  last  0.20 of blowing:      {seg_hi:.4f} lift per unit C_mu")
    print(f"  ratio (early : late):       {seg_lo / seg_hi:.2f} : 1")
    print(f"  marginal at C_mu = 0.05:    {first['marginal']:.4f} per unit C_mu")
    print(f"  marginal at C_mu = 0.40:    {last['marginal']:.4f} per unit C_mu")
    print(f"  marginal ratio:             {first['marginal'] / last['marginal']:.2f} : 1")
    lin = first["CL_total"] * (0.40 / 0.05)
    print(f"  a LINEAR extrapolation from C_mu = 0.05 to 0.40 predicts "
          f"{lin:.4f}; theory gives {last['CL_total']:.4f} "
          f"({100.0 * (lin / last['CL_total'] - 1.0):+.1f} %)")
    print()

    measured = collect_measured()
    print("MEASURED AERO LIFT (surface integration only; jet reaction NOT included)")
    print("-" * 78)
    print(f"{'C_mu':>6} {'iters':>7} {'CL_aero':>13} {'half-range':>12} "
          f"{'k resid':>11} {'p resid':>11}")
    for r in measured:
        print(f"{r['C_mu']:6.2f} {int(r['iterations']):7d} {r['CL_aero']:13.6e} "
              f"{r['half_range_tail']:12.3e} {r['residuals']['k']:11.3e} "
              f"{r['residuals'].get('p', float('nan')):11.3e}")
    kr = {r["C_mu"]: r["residuals"]["k"] for r in measured}
    print(f"\n  k-residual growth, unblown to strongest jet: "
          f"x{kr[0.40] / kr[0.00]:.1f}  (monotone: "
          f"{all(kr[a] < kr[b] for a, b in zip([0.0, 0.05, 0.10, 0.20], [0.05, 0.10, 0.20, 0.40]))})")

    payload = {
        "source": {
            "citation": ("Williams, J., Butler, S. F. J. and Wood, M. N. (1961), "
                         "'The Aerodynamics of Jet Flaps', Aeronautical Research "
                         "Council Reports and Memoranda No. 3304, H.M.S.O. 1963, "
                         "printed p.5 eq. (2), printed p.3 section 2."),
            "file": ("docs/papers/powered_lift_and_ducted_propulsion/"
                     "williams_butler_wood_1961_arc_rm3304_aerodynamics_of_"
                     "jet_flaps.pdf"),
            "rule15_title_page": RULE15_TITLE_PAGE,
            "rule15_eq2_introduction": RULE15_EQ2_INTRODUCTION,
            "rule15_spence_attribution": RULE15_SPENCE_ATTRIBUTION,
            "rule15_reference_26": RULE15_REFERENCE_26,
            "rule15_jet_reaction": RULE15_JET_REACTION,
            "spence_1956_held_by_this_lab": SPENCE_1956_HELD,
        },
        "tau_rad": TAU_RAD,
        "alpha_deg": 0.0,
        "theory": theory_rows,
        "measured": [
            {k: v for k, v in r.items() if k != "residuals"} | {"residuals": r["residuals"]}
            for r in measured
        ],
    }
    with open(os.path.join(out_dir, "jf1_theory_actB_numbers.json"), "w") as fh:
        json.dump(payload, fh, indent=2, default=str)
    print(f"\nWrote {os.path.join(out_dir, 'jf1_theory_actB_numbers.json')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
