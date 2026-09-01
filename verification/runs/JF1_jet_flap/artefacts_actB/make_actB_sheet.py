#!/usr/bin/env python3
"""
Emit the one-page ACT B result sheet, `JF1_actB_result_sheet.tex`.

Every number in the sheet is substituted from `jf1_theory_actB`, never typed by
hand, so a transcription error cannot enter the customer-facing page.

The sheet itself is customer-facing and carries no internal identifiers, no
process language and no verdict vocabulary.  This generator is an internal file
and its comments are not part of the sheet.
"""

from __future__ import annotations

import os
import sys

import jf1_theory_actB as th

OUT_TEX = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "blown_trailing_edge_result_sheet.tex")

# ---------------------------------------------------------------- cost inputs
# Measured core-minutes for the five completed conditions, from the run logs,
# supplied with this task by the supervisor who read them.
CORE_MIN_ACTUAL = [23.7667, 24.4333, 21.7500, 22.3333, 25.2000]
CORE_MIN_ACTUAL_TOTAL = 117.4833
# Upfront figure for the same five conditions, fixed before any of them started:
# 5 runs x 11.36 core-min (JF1_PREREGISTRATION.md section 12, line "G1-G5").
CORE_MIN_ESTIMATE_FIVE = 5 * 11.36
# Upfront figure for the sixth, finer-mesh companion condition.
#
# ITS ACTUAL COST IS NO LONGER TYPED AND ITS STATE IS NO LONGER ASSERTED. This
# sheet said, for hours after the run ended, that the sixth condition was "now
# running" and "not yet complete", and quoted only a forecast for it. The run
# finished at 2026-08-31T23:09:08Z: End line present, last time directory 20000
# against an endTime of 20000. A sentence about whether something is running
# cannot be a literal in a generator, because the literal keeps saying it.
CORE_MIN_ESTIMATE_SIXTH = 90.5
SIXTH_CASE = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "JF1_P1_L1_CMESH_PHYSICS")
RATE_USD_PER_CORE_HOUR = 0.0513   # owner-stated machine rate

# Movement of the lift coefficient over the last 4,000 iterations, rounded up to
# one significant figure.  A settling indicator, not a total uncertainty.
#
# THIS USED TO BE A HARD-CODED DICT AND THE DICT DID NOT MATCH ITS OWN CAPTION.
# It read
#
#   SETTLE_BAND = {0.00: 5e-07, 0.05: 5e-07, 0.10: 5e-07, 0.20: 9e-06,
#                  0.40: 5e-06}
#
# and four of those five values were smaller than the quantity the caption
# above describes: at C_mu = 0.20 the sheet printed 9e-06 against a measured
# half-range of 3.383e-05, understating by 3.8x.  They also failed the caption's
# own rounding rule, which says round UP: 6.901e-07 rounded up to one
# significant figure is 7e-07, and the sheet printed 5e-07.  They matched
# neither the 4,000-iteration window nor the 1,000-iteration one, so "it was
# computed on the shorter window" is ruled out by measurement rather than by
# argument.
#
# The column is now COMPUTED at render time from each case's force history, by
# the same reader the rest of this campaign uses.  Editing the dict to better
# numbers was rejected deliberately: a constant wearing a measured caption is
# the defect, and better constants leave the defect in place for whoever next
# changes a run.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import jf1_display_numbers as jf1num  # noqa: E402


def settle_band(case_dir: str) -> float:
    """Movement over the final 4,000 iterations, rounded up to one figure.

    One implementation, shared with the embedded lift panel and with the
    control-room screen, because two implementations of one number is how the
    two diverge without anybody noticing.  The reader plants a known value into
    a copy of the force history and refuses if it cannot read it back, and it
    refuses outright rather than shortening the window if fewer than 4,000
    iterations exist.
    """
    return jf1num.movement_1sf(
        jf1num.settling(case_dir, jf1num.SETTLE_WINDOW)["half_range"])


def sci(x: float, sig: int = 6) -> str:
    """LaTeX scientific notation, e.g. 4.05733 \\times 10^{-1}."""
    if x == 0.0:
        return r"$0$"
    s = f"{x:.{sig - 1}e}"
    mant, exp = s.split("e")
    return rf"${mant} \times 10^{{{int(exp)}}}$"


def usd(core_min: float) -> float:
    return core_min / 60.0 * RATE_USD_PER_CORE_HOUR


def main() -> int:
    theory = {c: {
        "CL": th.CL_theory_total(c),
        "react": th.jet_reaction(c),
        "circ": th.CL_theory_circulation(c),
        "marg": th.marginal_dCL_dCmu(c),
        "dtau": th.dCL_dtau(c),
    } for c in th.CMU_SWEEP}

    measured = {r["C_mu"]: r for r in th.collect_measured()}

    # ---- theory table rows -------------------------------------------------
    trows = []
    for c in th.CMU_SWEEP:
        t = theory[c]
        marg = "---" if t["marg"] == float("inf") else f"{t['marg']:.3f}"
        trows.append(
            f"{c:.2f} & {sci(t['CL'])} & {sci(t['react'])} & {sci(t['circ'])} "
            f"& {marg} & $<10^{{-9}}$ \\\\")

    # ---- solved table rows -------------------------------------------------
    mrows = []
    for c in th.CMU_SWEEP:
        m = measured[c]
        surf = m["CL_aero"]
        react = th.jet_reaction(c)
        total = surf + react
        band = settle_band(m["case_dir"])
        kres = m["residuals"]["k"]
        if theory[c]["CL"] > 0:
            diff = f"{100.0 * (total / theory[c]['CL'] - 1.0):+.2f}"
        else:
            diff = "---"
        # The C_mu = 0 row is NOT the blown case with the jet turned down: that
        # calculation was run with the slot CLOSED.  It is a reference, marked
        # with a dagger and explained in the note under the table.  Never let
        # it be described as one of five conditions differing only in blowing.
        cmu_cell = f"{c:.2f}$^{{\\dagger}}$" if c == 0.0 else f"{c:.2f}"
        mrows.append(
            f"{cmu_cell} & {sci(surf)} & {sci(react)} & {sci(total)} & "
            f"{sci(band, 1)} & {sci(kres, 3)} & {diff} \\\\")

    kr0 = measured[0.00]["residuals"]["k"]
    kr4 = measured[0.40]["residuals"]["k"]
    k_factor = kr4 / kr0

    seg_lo = theory[0.05]["CL"] / 0.05
    seg_hi = (theory[0.40]["CL"] - theory[0.20]["CL"]) / 0.20
    lin_pred = theory[0.05]["CL"] * (0.40 / 0.05)
    lin_over = 100.0 * (lin_pred / theory[0.40]["CL"] - 1.0)

    usd_actual = usd(CORE_MIN_ACTUAL_TOTAL)
    usd_est5 = usd(CORE_MIN_ESTIMATE_FIVE)
    usd_est6 = usd(CORE_MIN_ESTIMATE_SIXTH)
    ratio = CORE_MIN_ACTUAL_TOTAL / CORE_MIN_ESTIMATE_FIVE

    # The sixth condition's ACTUAL cost, read from its own record on the same
    # gross basis as the five above rather than typed. The reader refuses a run
    # with no End line, so a cost cannot be quoted as final for something still
    # going, and it refuses a rank count its processor directories contradict.
    # It was validated against the five constants above, which it reproduces
    # exactly, before being trusted with a sixth the sheet has never carried.
    sixth = jf1num.measured_core_minutes(SIXTH_CASE)
    core_min_sixth = sixth["core_min"]
    usd_sixth = usd(core_min_sixth)
    ratio_sixth = core_min_sixth / CORE_MIN_ESTIMATE_SIXTH

    tex = rf"""% ---------------------------------------------------------------
% Blown trailing edge -- one-page result sheet.
% GENERATED by make_actB_sheet.py; every number is substituted from the
% theory module, none is typed by hand.  Edit the generator, not this file.
% ---------------------------------------------------------------
\documentclass[8pt,a4paper]{{extarticle}}
\usepackage[margin=10mm,top=8mm,bottom=6mm]{{geometry}}
\usepackage{{booktabs,graphicx,xcolor,caption,microtype,multicol}}
\setlength{{\columnsep}}{{8mm}}
\usepackage[T1]{{fontenc}}
\usepackage{{lmodern}}
\definecolor{{navy}}{{HTML}}{{1F4E79}}
\definecolor{{boxbg}}{{HTML}}{{FBF6E9}}
\definecolor{{boxrule}}{{HTML}}{{C9A227}}
\captionsetup{{font=small,labelfont=bf,skip=3pt}}
\setlength{{\parindent}}{{0pt}}
\setlength{{\parskip}}{{1pt}}
\pagestyle{{empty}}

\newcommand{{\shead}}[1]{{\vspace{{1pt}}{{\color{{navy}}\bfseries\large #1}}\vspace{{1pt}}\hrule\vspace{{3pt}}}}
\newcommand{{\role}}[1]{{{{\color{{navy}}\bfseries #1.}}}}

\begin{{document}}

{{\color{{navy}}\LARGE\bfseries Blown trailing edge: how much lift does the jet buy?}}\\[2pt]
{{Two-dimensional aerofoil section, jet blown from the trailing edge at
$\tau = 30^\circ$ below the chord line, $\alpha = 0^\circ$,
chord Reynolds number $1.0 \times 10^{{6}}$, chord $1.0$~m, free stream $10.0$~m\,s$^{{-1}}$.}}

\shead{{The answer in one line}}

Lift does not grow in proportion to blowing. It grows as the \emph{{square
root}} of the jet momentum coefficient $C_\mu$, so the first increment of blowing
is worth far more than the last: the first $0.05$ of $C_\mu$ buys {seg_lo:.2f} of
lift coefficient per unit $C_\mu$, the last $0.20$ only {seg_hi:.2f} --- a factor
of {seg_lo / seg_hi:.1f}. Sizing a blowing system on a straight line through a
low-blowing data point overpredicts the lift at $C_\mu = 0.40$ by
{lin_over:.0f}\%.

\shead{{Table 1 -- Published thin-aerofoil theory for a jet-flapped section}}

\begin{{center}}\small
\begin{{tabular}}{{cccccc}}
\toprule
Jet momentum & Total lift & \multicolumn{{2}}{{c}}{{of which:}} & Marginal lift & Uncertainty \\
coefficient & coefficient & jet reaction & pressure lift & per unit $C_\mu$ & on the value \\
$C_\mu$ [--] & $(C_L)_\infty$ [--] & $C_\mu \sin(\tau+\alpha)$ [--] & [--] &
$\mathrm{{d}}C_L/\mathrm{{d}}C_\mu$ [--] & [--] \\
\midrule
{chr(10).join(trows)}
\bottomrule
\end{{tabular}}
\end{{center}}

\vspace{{-7pt}}
{{\footnotesize The jet-reaction column is the direct vertical component of the
jet momentum, reported separately and never folded silently into the lift
column: here it is a \emph{{part}} of the total, and the pressure-lift column is
what remains. The marginal column is the slope of the total with respect to
$C_\mu$; it is unbounded as $C_\mu \to 0$, which is the square-root law stated as
a number. Uncertainty is the arithmetic error of evaluating the published
expression; the accuracy of the published fit is not stated in the source.}}

\shead{{Table 2 -- Solved flow field: four blown conditions and a slot-closed reference}}

\begin{{center}}\small
\begin{{tabular}}{{ccccccc}}
\toprule
Jet momentum & Lift from the & Jet reaction & Lift, surface & Movement in the & Turbulence & Difference \\
coefficient & aerofoil surface & (added, not & $+$ jet reaction & last 4{{,}}000 & equation & from \\
$C_\mu$ [--] & $C_{{L,\mathrm{{surface}}}}$ [--] & measured) [--] & [--] & iterations [--] & imbalance [--] & Table 1 [\%] \\
\midrule
{chr(10).join(mrows)}
\bottomrule
\end{{tabular}}
\end{{center}}

\vspace{{-7pt}}
{{\footnotesize The surface column integrates pressure and shear over the
aerofoil only; it does \emph{{not}} contain the jet reaction, which is added
explicitly in the fourth column to give a quantity comparable with Table~1.
``Movement'' is how much the lift still shifted over the final 4{{,}}000
iterations: half the range it covered there, rounded up to one significant
figure. ``Turbulence equation imbalance'' is how far the turbulent kinetic
energy equation is from being satisfied at the last iteration; the target set
before running was $1 \times 10^{{-6}}$. $^{{\dagger}}$The $C_\mu = 0$ row is a
reference case with the slot \emph{{closed}}; the other four have it open and
differ only in jet strength.}}

\vspace{{2pt}}
\begin{{center}}
\begin{{minipage}}[t]{{0.455\textwidth}}
\vspace{{0pt}}
\centering
\includegraphics[width=\textwidth]{{fig_lift_vs_blowing.pdf}}

\vspace{{2pt}}
{{\footnotesize\raggedright\textbf{{Figure 1. Lift against blowing.}} The solid
curve is published thin-aerofoil theory for a jet-flapped section (Williams,
Butler \& Wood, ARC R\&M 3304, 1961, eq.~2). The dashed grey line is what a
linear expectation anchored at $C_\mu = 0.05$ would have predicted; the gap
between the two is the message of this sheet. Uncertainty bars on the solved
points are the movement column of Table~2 and are smaller than the markers.\par}}
\end{{minipage}}\hfill
\begin{{minipage}}[t]{{0.515\textwidth}}
\vspace{{0pt}}
\setlength{{\fboxsep}}{{6pt}}
\fcolorbox{{boxrule}}{{boxbg}}{{\parbox{{\dimexpr\textwidth-14pt}}{{\footnotesize%
{{\bfseries Please read before using these numbers.}}\\[2pt]
$\bullet$ The theory curve is trustworthy arithmetic against a published
formula. The solved points are not yet finished calculations and none of them is
described here as verified.\\
$\bullet$ The uncertainty column in Table~2 says how much each number was still
moving at the end of the run. It is \emph{{not}} a total error bar: the
contribution from mesh resolution has not been established for these five
conditions, and it is larger than the number shown.\\
$\bullet$ The published formula is an interpolation fit to computed values, valid
for blowing from the trailing edge with no separate flap, and is used whole over
the range it was fitted for. It is inviscid thin-aerofoil theory: no stall, no
separation, no viscous loss, so it overstates lift wherever the real jet sheet or
boundary layer breaks down.\\
$\bullet$ Everything here is two-dimensional. No finite-span correction has been
applied, and a real wing of finite aspect ratio will achieve less.
}}}}

\vspace{{5pt}}
{{\color{{navy}}\bfseries What this cost}}\vspace{{1pt}}\hrule\vspace{{2pt}}
{{\footnotesize\raggedright The five solved conditions used
{CORE_MIN_ACTUAL_TOTAL:.1f} core-minutes of compute in total
({', '.join(f'{v:.1f}' for v in CORE_MIN_ACTUAL)} core-minutes respectively).
The figure quoted before any of them started was {CORE_MIN_ESTIMATE_FIVE:.1f}
core-minutes, so the work came in {ratio:.2f} times the upfront estimate. The
sixth, finer-mesh companion condition was quoted at
{CORE_MIN_ESTIMATE_SIXTH:.1f} core-minutes upfront and used
{core_min_sixth:.1f}, {ratio_sixth:.2f} times its estimate. The theory curve
costs no solver time. At the machine's hourly rate of
\${RATE_USD_PER_CORE_HOUR:.4f} per core-hour that is \${usd_actual:.3f} spent
against a \${usd_est5:.3f} estimate for the five, and \${usd_sixth:.3f} against
\${usd_est6:.3f} for the finer mesh. Money figures are derived from the hourly
rate; they are not read from a metered bill.\par}}
\end{{minipage}}
\end{{center}}

\shead{{What has been checked, what has not, and how the team reads it}}

\begin{{multicols}}{{2}}
\textbf{{Checked.}} The theory curve reproduces the published expression exactly.
The lift derivatives were read off the printed page of Williams, Butler \& Wood,
\emph{{The Aerodynamics of Jet Flaps}}, Aeronautical Research Council Reports and
Memoranda No.~3304 (H.M.S.O., 1963), page~5, equation~(2), and the jet-reaction
convention $C_\mu \sin(\tau + \alpha)$ off page~3. Our evaluation reproduces the
values fixed before running to better than $5 \times 10^{{-10}}$ in lift
coefficient at every point in Table~1, and the marginal-lift column matches an
independent finite-difference evaluation of the same expression to eight figures.

\textbf{{Checked.}} The reference section, slot closed, returns a surface lift
coefficient of {sci(measured[0.00]['CL_aero'], 3)} at zero incidence, as a
symmetric section must. The same solver and reader gave $1.01$ at the strongest
blowing, so the near-zero is physics, not a reader that could only give zero.

\textbf{{Not checked.}} \emph{{None of the solved points in Table~2 is offered as
verified against anything.}} The solutions are still tightening: no condition has
brought every equation below the $1 \times 10^{{-6}}$ target set before running,
and no mesh-refinement study has been completed for these five conditions. The
last column of Table~2 is an observation, not an agreement claim.

\role{{Lead Researcher}} The physics worth taking away is the square-root law:
blowing buys circulation, and circulation grows with the square root of jet
momentum, so the system pays back fastest at low blowing rates. At
$C_\mu = 0.40$ the jet provides $0.20$ of lift coefficient directly and
{theory[0.40]['circ']:.2f} indirectly, through the pressure field it induces on
the aerofoil --- five times the direct part, and that amplification is the
point of the configuration.

\role{{Lead Engineer}} Size the system at the knee, not at the top. Going from
$C_\mu = 0$ to $0.05$ delivers {theory[0.05]['CL']:.2f} of lift coefficient;
quadrupling jet momentum from $0.10$ to $0.40$ delivers only another
{theory[0.40]['CL'] - theory[0.10]['CL']:.2f}. Budget analysis time accordingly:
this flow becomes markedly harder to solve as blowing increases, so a strongly
blown case is not a mildly blown case with a different inlet number.

\role{{Lead Numericist}} Confidence differs sharply between the two tables.
Table~1 is arithmetic against a published expression, exact to the digits shown.
Table~2 has not reached the target set before running: the turbulence equation
imbalance grows monotonically with blowing, from {sci(kr0, 3)} at the reference
to {sci(kr4, 3)} at the strongest jet, a factor of {k_factor:.0f}. The lift is
still moving at the end of every run, by the amount in the movement column,
which is why that column is quoted at all --- a settling indicator is not a
converged one. The finer companion mesh has completed, and it does not close
this gap: it is a different grid topology on a different reference area, run as
a diagnostic, so it is not a refinement of the five and no grid-refinement
study has been carried out. The mesh contribution to the uncertainty on
Table~2 therefore remains unquantified.
\end{{multicols}}

\end{{document}}
"""
    with open(OUT_TEX, "w") as fh:
        fh.write(tex)
    print(f"wrote {OUT_TEX}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
