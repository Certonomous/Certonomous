#!/usr/bin/env python3
"""
JF1 ACT B -- the CL-versus-C_mu theory curve, as a VECTOR pdf with LaTeX labels.

This is the theory-curve figure only.  The Cp distribution, the jet-sheet
trajectory and the field plot are produced elsewhere and are not duplicated here.

Output: JF1_actB_CL_vs_Cmu.pdf  (vector; no raster fallback is written)
"""

from __future__ import annotations

import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import rcParams

import jf1_theory_actB as th

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "fig_lift_vs_blowing.pdf")

# Movement of the lift coefficient over the last 4,000 iterations, rounded up to
# one significant figure.  This is a settle indicator, NOT a grid uncertainty.
SETTLE_BAND = {0.00: 5e-07, 0.05: 5e-07, 0.10: 5e-07, 0.20: 9e-06, 0.40: 5e-06}


def main() -> int:
    rcParams.update({
        "font.family": "serif",
        "mathtext.fontset": "cm",
        "axes.labelsize": 11,
        "axes.titlesize": 11,
        "legend.fontsize": 8.5,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "pdf.fonttype": 42,
    })

    # --- theory curve -------------------------------------------------------
    n = 601
    cmu = [0.42 * i / (n - 1) for i in range(n)]
    cl_theory = [th.CL_theory_total(c) for c in cmu]
    react = [th.jet_reaction(c) for c in cmu]
    circ = [th.CL_theory_circulation(c) for c in cmu]

    # --- what a linear expectation would have predicted ---------------------
    anchor = 0.05
    slope = th.CL_theory_total(anchor) / anchor
    lin = [slope * c for c in cmu]

    # --- solved points ------------------------------------------------------
    rows = th.collect_measured()
    x = [r["C_mu"] for r in rows]
    y_aero = [r["CL_aero"] for r in rows]
    y_tot = [r["CL_aero"] + th.jet_reaction(r["C_mu"]) for r in rows]
    err = [SETTLE_BAND[r["C_mu"]] for r in rows]

    fig, ax = plt.subplots(figsize=(6.1, 4.1))

    ax.plot(cmu, lin, ls=(0, (6, 4)), lw=1.2, color="#9a9a9a",
            label=r"linear expectation anchored at $C_\mu = 0.05$")
    ax.plot(cmu, cl_theory, lw=2.0, color="#1f4e79",
            label="jet-flap thin-aerofoil theory, $(C_L)_\\infty$\n"
                  "Williams, Butler & Wood, ARC R&M 3304 (1961), eq. (2)")
    ax.plot(cmu, circ, lw=1.2, ls="-.", color="#1f4e79", alpha=0.65,
            label=r"theory, pressure part only  $(C_L)_\infty - C_\mu \sin\tau$")
    ax.plot(cmu, react, lw=1.2, ls=":", color="#a33",
            label=r"direct jet reaction  $C_\mu \sin(\tau + \alpha)$")

    ax.errorbar(x, y_tot, yerr=err, fmt="o", ms=6, mfc="white", mew=1.5,
                color="#1f4e79", capsize=3, zorder=5,
                label=r"solved: surface lift $+\ C_\mu \sin(\tau+\alpha)$")
    ax.errorbar(x, y_aero, yerr=err, fmt="s", ms=5, mfc="white", mew=1.2,
                color="#555555", capsize=3, zorder=5,
                label=r"solved: surface lift $C_{L,\mathrm{surface}}$ alone")

    ax.set_xlabel(r"jet momentum coefficient  $C_\mu$  [--]")
    ax.set_ylabel(r"sectional lift coefficient  $C_L$  [--]")
    ax.set_title(r"Blown trailing edge, $\tau = 30^\circ$, "
                 r"$\alpha = 0^\circ$, $Re_c = 1.0\times10^{6}$")
    ax.set_xlim(0.0, 0.42)
    ax.set_ylim(0.0, 3.6)
    ax.grid(True, which="major", ls=":", lw=0.6, alpha=0.6)
    ax.legend(loc="upper left", framealpha=0.95)

    ax.text(0.985, 0.055,
            "square-root growth, not linear: the first $0.05$ of blowing\n"
            "buys $8.47$ of lift per unit $C_\\mu$; the last $0.20$ buys\n"
            "$1.95$ -- a factor of $4.3$ less for the same jet momentum",
            transform=ax.transAxes, fontsize=8.5, ha="right", va="bottom",
            bbox=dict(boxstyle="round,pad=0.4", fc="#f5f5f0", ec="#bbb", lw=0.7))

    fig.tight_layout()
    fig.savefig(OUT, format="pdf")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
