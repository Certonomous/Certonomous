#!/usr/bin/env python3
"""Act C -- GATE screens.  Three figures, every one a CONVERGENCE DIAGNOSTIC.

*** NOT ONE NUMBER ON THESE SCREENS IS A THERMAL RESULT. ***

The distinction this file is built around, and it is the whole point:

  ADMISSIBLE -- a DIFFERENCE BETWEEN TWO ARMS that differ only in outer-sweep
    count.  `2.315190e-02 K` is a statement about the METHOD: it says the
    answer still moves when an arbitrary iteration count is doubled.  It tells
    a viewer nothing about how hot anything got.

  WITHHELD -- anything that would tell a viewer how hot the module got.  Every
    cell temperature, every rise, the outlet temperature itself, the
    acceptance criteria, the energy ledger, and the adiabatic bounds (which
    would disclose the scale of the answer by the back door).

The mechanical form of that boundary, which `check_actC_gate_screen.py`
enforces rather than trusting: **every kelvin magnitude on these screens is
strictly below 0.1 K.**  The convergence deltas span 5.2e-04 to 2.4e-02 K and
the thresholds are 1.234e-03 and 1.234e-02 K, all far below it; every withheld
quantity -- absolute temperatures near 293 K, rises of order 1 K and up -- is
far above it.  The separation is clean by two orders of magnitude, so the rule
is decidable by reading a number rather than by judging a sentence.

ALL PLOTS LATEXIFIED via the shared `latex_style`, whose `apply()` renders a
throwaway PDF and reads the embedded font names back off disk before returning.

Every value below is MEASURED.  Nothing is drawn by hand and nothing is
interpolated.  Sources are the two completed arms of the battery-module case
and the numerics probe that preceded them.

Usage: python3 make_actC_gate_screens.py
"""
import csv
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                 # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import latex_style as LS                                        # noqa: E402

T = LS.tex_text

# --------------------------------------------------------------------------
# THE MEASURED DATA.  Convergence diagnostics only.
# --------------------------------------------------------------------------

# The two thresholds, in kelvin.  Presented on screen as "the smallest
# difference this screen calls a signal" and "a tenth of it"; the internal
# constant they derive from is not named on a customer surface.
TOL_SIGNAL = 1.234e-02
TOL_TENTH = 1.234e-03

# The three registered agreement checks: 10 outer sweeps against 20, same mesh,
# same load, same relaxation, identical in every other respect.
CHECKS = [
    ("A", "Solid temperature field,\nevery cell, every frame",
     1.199542e-03, TOL_SIGNAL, "pass"),
    ("B", "Streamwise difference\nwithin a cell",
     6.675809e-04, TOL_TENTH, "pass"),
    ("C", "Coolant outlet,\narea-mean",
     2.315190e-02, TOL_SIGNAL, "fail"),
]

# Agreement over the run: |10 sweeps - 20 sweeps| at each written frame.
TIMES = [30.0, 60.0, 120.0, 300.0, 900.0]
D_OUTLET = [2.404233e-02, 2.315190e-02, 4.404260e-03, 3.722504e-03, 2.006354e-03]
D_SOLID = [5.208319e-04, 9.964913e-04, 1.055683e-03, 1.199542e-03, 1.060819e-03]

# The sweep sequence at the 30 s frame.  Both entries are differences between
# two arms; the first is measured by the numerics probe on the same mesh, the
# same load and the same relaxation.
SEQ = [("5 against 10", 6.02e-03), ("10 against 20", 5.208319e-04)]

PULSE_END = 60.0        # s -- the load steps down here
OK = "#1b6b3a"
BAD = "#a4361f"
GREY = "#4a4a4a"
LIGHT = "#c8c8c8"


def _save(fig, stem, rows, header):
    for ext in ("pdf", "svg"):
        fig.savefig(os.path.join(HERE, "%s.%s" % (stem, ext)),
                    bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    with open(os.path.join(HERE, "%s.csv" % stem), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print("wrote %s.{pdf,svg,csv}" % stem)


def fig_checks():
    """Screen 1 -- the three agreement checks against their thresholds."""
    fig, ax = plt.subplots(figsize=(3.5, 1.85))
    ys = list(range(len(CHECKS)))[::-1]
    for y, (cid, label, val, tol, state) in zip(ys, CHECKS):
        col = OK if state == "pass" else BAD
        ax.plot([tol], [y], marker="|", ms=13, mew=1.6, color=GREY, zorder=3)
        ax.plot([val], [y], marker="o", ms=6.0, color=col, zorder=4)
        ax.hlines(y, min(val, tol), max(val, tol), color=col, lw=1.4,
                  alpha=0.55, zorder=2)
    ax.set_yticks(ys)
    ax.set_yticklabels([T("%s   %s" % (c[0], c[1].replace("\n", " ")))
                        for c in CHECKS], fontsize=6.6)
    ax.set_xscale("log")
    ax.set_xlim(3e-4, 6e-2)
    ax.set_xlabel(T(r"agreement between 10 and 20 sweeps, K"))
    ax.set_title(LS.bold(T("Agreement against its limit")), pad=4)
    ax.grid(axis="x", color=LIGHT, lw=0.5, alpha=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.annotate(T("limit"), xy=(TOL_SIGNAL, 2.42), fontsize=6.0,
                color=GREY, ha="center")
    ax.annotate(T("over"), xy=(2.315190e-02, -0.42), fontsize=6.2,
                color=BAD, ha="center")
    _save(fig, "actC_gate_checks",
          [[c[0], c[1].replace("\n", " "), c[2], c[3], c[4]] for c in CHECKS],
          ["check", "quantity", "agreement_K", "limit_K", "state"])


def fig_over_run():
    """Screen 2 -- agreement over the run.  The localisation is the finding."""
    fig, ax = plt.subplots(figsize=(3.5, 1.95))
    ax.axvspan(0, PULSE_END, color="#f0e6d8", zorder=0)
    ax.axhline(TOL_SIGNAL, color=GREY, lw=1.0, ls=(0, (4, 2)), zorder=2)
    ax.plot(TIMES, D_OUTLET, marker="o", ms=4.2, lw=1.5, color=BAD,
            label=T("coolant outlet"), zorder=4)
    ax.plot(TIMES, D_SOLID, marker="s", ms=3.8, lw=1.5, color=OK,
            label=T("solid, every cell"), zorder=4)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(22, 1200)
    ax.set_ylim(3e-4, 6e-2)
    ax.set_xlabel(T("time into the run, s"))
    ax.set_ylabel(T("agreement, K"))
    ax.set_title(LS.bold(T("Agreement over the run")), pad=4)
    ax.grid(color=LIGHT, lw=0.5, alpha=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.annotate(T("limit"), xy=(760, TOL_SIGNAL * 1.18), fontsize=6.0,
                color=GREY, ha="right")
    ax.annotate(T("takeoff pulse"), xy=(31, 3.6e-2), fontsize=6.2,
                color="#7a5a30")
    ax.legend(fontsize=6.2, frameon=False, loc="lower left")
    _save(fig, "actC_gate_over_run",
          [[t, o, s] for t, o, s in zip(TIMES, D_OUTLET, D_SOLID)],
          ["time_s", "outlet_agreement_K", "solid_agreement_K"])


def fig_sequence():
    """Screen 3 -- the sweep sequence on the solid: 5, 10, 20."""
    fig, ax = plt.subplots(figsize=(2.5, 1.85))
    xs = [0, 1]
    vals = [v for _, v in SEQ]
    ax.bar(xs, vals, width=0.52, color=[LIGHT, OK], zorder=3)
    for x, v in zip(xs, vals):
        ax.annotate(T("%.2e" % v), xy=(x, v * 1.22), fontsize=6.2,
                    ha="center", color=GREY)
    ax.set_xticks(xs)
    ax.set_xticklabels([T(s) for s, _ in SEQ], fontsize=6.6)
    ax.set_yscale("log")
    ax.set_ylim(2e-4, 3e-2)
    ax.set_ylabel(T("agreement, K"))
    ax.set_title(LS.bold(T("Sweep sequence, 30 s frame")), pad=4)
    ax.grid(axis="y", color=LIGHT, lw=0.5, alpha=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.annotate(T(r"$11.6\times$ closer"), xy=(0.5, 1.15e-2), fontsize=6.4,
                ha="center", color=OK)
    _save(fig, "actC_gate_sequence", [[a, b] for a, b in SEQ],
          ["sweep_pair", "agreement_K"])


def main():
    LS.apply(plt, base_font_size=7.4)
    fig_checks()
    fig_over_run()
    fig_sequence()
    # Read the fonts back off disk, per figure, rather than trusting rcParams.
    bad = []
    for f in sorted(os.listdir(HERE)):
        if not f.endswith(".pdf"):
            continue
        fonts = LS.pdf_fonts(os.path.join(HERE, f))
        latex = any(x.startswith(LS.EXPECTED_FONT_STEM) for x in fonts)
        fell = any(x.startswith(LS.FORBIDDEN_FONT_STEM) for x in fonts)
        print("  %-28s fonts %s" % (f, fonts))
        if fell or not latex:
            bad.append(f)
    if bad:
        sys.stderr.write("REFUSE: %s did not go through LaTeX.\n" % bad)
        return 2
    print("every figure latexified, verified by reading the embedded fonts "
          "back off disk")
    return 0


if __name__ == "__main__":
    sys.exit(main())
