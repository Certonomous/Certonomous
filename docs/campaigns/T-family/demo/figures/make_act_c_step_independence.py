#!/usr/bin/env python3
# =========================================================================
# ACT C, C6.4 -- THE STEP-INDEPENDENCE TABLE.
#
# NOTHING HERE SOLVES ANYTHING.  Both arms were already on disk when this
# script was written; it reads them and writes one figure, one CSV and one
# JSON block.  No solver is launched, no case is written to, no compute is
# booked.
#
# WHY THIS IS A SEPARATE SCRIPT AND NOT A BLOCK INSIDE
# make_act_c_screens.py:  that script rewrites every Act C figure it owns,
# and re-running it to add one product would churn eight vector files whose
# only change would be an embedded timestamp.  This script writes ONLY the
# three files it owns and merges nothing into anybody else's output.  It
# carries the same imports, the same parser and the same refusal discipline
# as the script it sits beside.
#
# WHAT THIS PRODUCT IS, AND WHAT IT IS NOT
#   It is a TWO-POINT step-size check on an ungated feasibility run.
#   It is NOT a convergence study.  Two levels cannot measure an observed
#   order and two levels in time with one level in space are not a Roache
#   triple, so no observed order is computed here, NO GCI is quoted here,
#   and no ratio between the two energy-closure gaps appears on any surface
#   this script writes.  A reader who wants the full reading has the record:
#   verification/runs/T-family/T25_MODULE_runs/T25_STEP_INDEPENDENCE.md
#
# PLANTED CONTROL (CLAUDE.md rule 3), TWICE:
#   (a) analyse_t25.selftest on EACH arm -- the shared parser must see
#       +1 K on all 960 cells at t = 900 s, separately for each case tree.
#       A second arm is a second reader target and gets its own control.
#   (b) this script's own DIFFERENCE reader -- the quantity on screen is a
#       difference between two arms, so the control plants a known
#       perturbation of PLANT = 1.234e-03 K (scripts/roache_triple.py:169)
#       into a copy of the fine arm and refuses unless the difference the
#       table is built from moves by exactly that much.  A differencer that
#       cannot see a planted difference cannot report a zero difference.
# =========================================================================
import csv
import json
import os
import shutil
import sys
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = "/home/ubuntu/Certonomous/verification/runs/T-family/T25_MODULE_runs"
CASE_COARSE = os.path.join(RUNS, "T25_MOD_L1")          # deltaT 0.5 s
CASE_FINE = os.path.join(RUNS, "T25_MOD_L1_DT025")      # deltaT 0.25 s
RECORD = os.path.join(RUNS, "T25_STEP_INDEPENDENCE.md")
sys.path.insert(0, RUNS)
sys.path.insert(0, os.path.dirname(HERE))
import latex_style as LS                                   # noqa: E402
import analyse_t25 as A                                    # noqa: E402

PLANT = 1.234e-03          # scripts/roache_triple.py:169, not redefined
PLANT_TOL = 1.0e-9
END_CELLS = (1, 8)         # one-based module cell numbers
STEP_COARSE_S = 0.5
STEP_FINE_S = 0.25

# One caption line, at most 20 words, per the 03:10Z figure standard.  The
# numbers live in the table beside it; the fuller reading of what a two-point
# step check does and does not establish belongs to the sheet text, not to
# the figure, which carries no paragraphs.
CAPTION = ("Peak rise moves under 0.0003 K when the step halves. "
           "Two step sizes only. Not a convergence study.")

# Text is set by LaTeX itself (Latin Modern), shared with Act A via
# latex_style, which refuses if LaTeX did not in fact run.
LS.apply(plt, base_font_size=9, extra={"figure.dpi": 150})


# --------------------------------------------------------------- reading
def arm(case):
    """One arm, read through the shared parser: times, per-cell field,
    per-cell peak rise, and the percentage of the heat input accounted for."""
    rows, closure_pct, _qint, _last = A.analyse(case, quiet=True)
    times = np.array([r["t"] for r in rows])
    percell = np.array([r["percell"] for r in rows])
    peak_rise = percell.max(axis=0) - A.T_REF
    return times, percell, peak_rise, closure_pct


def difference_reading(coarse_case, fine_case):
    """The numbers the screen shows, and the guards that make them readable.

    Refuses rather than degrades if the two arms cannot be compared on equal
    terms: a differing cell count, a differing number of write times, or
    write times that are not the same instants.
    """
    tc, pc, rise_c, close_c = arm(coarse_case)
    tf, pf, rise_f, close_f = arm(fine_case)

    bad = []
    if pc.shape[1] != pf.shape[1]:
        bad.append(f"cell counts differ: {pc.shape[1]} against {pf.shape[1]}")
    if len(tc) != len(tf):
        bad.append(f"write-time counts differ: {len(tc)} against {len(tf)}")
    elif float(np.max(np.abs(tc - tf))) > 1e-9:
        bad.append("the two arms were not written at the same instants")
    if bad:
        sys.exit("REFUSE: the two arms are not comparable term by term: "
                 + "; ".join(bad))

    diff = pf - pc                      # fine minus coarse, per time, per cell
    k, i = np.unravel_index(int(np.argmax(np.abs(diff))), diff.shape)
    return {
        "times": tc,
        "n_write_times": int(len(tc)),
        "n_cells": int(pc.shape[1]),
        "peak_rise_coarse_K": rise_c,
        "peak_rise_fine_K": rise_f,
        "peak_rise_diff_K": rise_f - rise_c,
        "closure_percent_coarse": close_c,
        "closure_percent_fine": close_f,
        "largest_abs_diff_K": float(abs(diff[k, i])),
        "largest_abs_diff_time_s": float(tc[k]),
        "largest_abs_diff_cell": int(i) + 1,
    }


# ---------------------------------------------- planted control (b)
def plant_difference_control(coarse_case, fine_case):
    """Plant PLANT K on every cell of the FINE arm at t = 900 s and require
    the differencer to see exactly that shift in the peak-rise difference."""
    print("PLANTED CONTROL (b) -- the difference reader")
    tmp = tempfile.mkdtemp(prefix="t25_stepdiff_plant_")
    dst = os.path.join(tmp, "case")
    try:
        shutil.copytree(fine_case, dst,
                        ignore=shutil.ignore_patterns("postProcessing"))
        base = difference_reading(coarse_case, dst)

        p = os.path.join(dst, "900", "module", "T")
        txt = open(p).read()
        k = txt.index("internalField")
        body, j = A.read_list(txt, k)
        vals = [float(v) + PLANT for v in body.split()]
        open(p, "w").write(txt[:txt.index("(", k) + 1] + "\n"
                           + "\n".join(repr(v) for v in vals) + "\n" + txt[j:])

        seen = difference_reading(coarse_case, dst)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    shift = seen["peak_rise_diff_K"] - base["peak_rise_diff_K"]
    worst = float(np.max(np.abs(shift - PLANT)))
    ok = worst < PLANT_TOL
    print(f"  planted            +{PLANT:.6e} K on all 960 mesh cells of the "
          f"{STEP_FINE_S} s arm at t = 900 s")
    print(f"  differencer saw    {float(np.min(shift)):+.9e} to "
          f"{float(np.max(shift)):+.9e} K on the eight per-cell differences")
    print(f"  worst departure    {worst:.3e} K from the planted size")
    print("  RESULT             "
          + ("PLANT SEEN" if ok else "PLANT NOT SEEN -- REFUSE"))
    if not ok:
        sys.exit("REFUSE: the difference reader cannot see a planted "
                 "difference, so a small difference it reports is not "
                 "evidence and no table is written")
    return {
        "planted_K": PLANT,
        "scope": f"all 960 mesh cells of the {STEP_FINE_S} s arm at t = 900 s",
        "reader": "the two-arm per-cell peak-rise differencer",
        "worst_departure_K": worst,
        "seen": bool(ok),
    }


# --------------------------------------------------------------- figure
def fig_step_independence(d, out):
    cells = np.arange(1, d["n_cells"] + 1)
    fig = plt.figure(figsize=(11.4, 7.6), constrained_layout=True)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.15, 1.0])
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, :])

    # --- panel 1: the two arms on the same axis; they overlay, and that is
    # the finding rather than a plotting failure, so it is said in the title.
    ax1.plot(cells, d["peak_rise_coarse_K"], "o", ms=9, mfc="none",
             mew=1.6, color="#1f4e79",
             label=f"time step {STEP_COARSE_S} s")
    ax1.plot(cells, d["peak_rise_fine_K"], "x", ms=7, mew=1.6,
             color="#c1440e", label=f"time step {STEP_FINE_S} s")
    ax1.set_xlabel("Module cell")
    ax1.set_ylabel("Peak temperature rise above coolant, K")
    ax1.set_xticks(cells)
    ax1.grid(alpha=0.3, lw=0.5)
    ax1.legend(fontsize=8, frameon=False)
    ax1.set_title("Peak rise per cell, both step sizes", fontsize=9)

    # --- panel 2: the difference, at the scale it actually has
    ax2.bar(cells, d["peak_rise_diff_K"] * 1e3, width=0.6, color="#1f4e79")
    ax2.axhline(d["largest_abs_diff_K"] * 1e3, ls="--", lw=1.1,
                color="#c1440e")
    ax2.annotate(
        f"largest {d['largest_abs_diff_K'] * 1e3:.5f} mK, cell "
        f"{d['largest_abs_diff_cell']}, "
        f"t = {d['largest_abs_diff_time_s']:.0f} s",
        xy=(cells[-1], d["largest_abs_diff_K"] * 1e3),
        xytext=(0.02, 0.92), textcoords="axes fraction",
        fontsize=7.5, color="#c1440e", va="top")
    ax2.set_xlabel("Module cell")
    ax2.set_ylabel("Peak rise, finer step minus coarser, mK")
    ax2.set_xticks(cells)
    ax2.grid(alpha=0.3, lw=0.5, axis="y")
    ax2.set_title("Difference, finer step minus coarser", fontsize=9)

    # --- panel 3: the numbers themselves
    ax3.axis("off")
    end = END_CELLS[0] - 1
    inner = 1
    hdr = ["Quantity", f"Time step {STEP_COARSE_S} s",
           f"Time step {STEP_FINE_S} s", "Change", "Change, %"]
    rc, rf = d["peak_rise_coarse_K"], d["peak_rise_fine_K"]
    body = [
        [f"Peak rise, end cells {END_CELLS[0]} and {END_CELLS[1]}, K",
         f"{rc[end]:.6f}", f"{rf[end]:.6f}",
         f"{rf[end] - rc[end]:+.4e}",
         f"{100.0 * (rf[end] - rc[end]) / rc[end]:+.4f}"],
        ["Peak rise, interior cells 2 to 7, K",
         f"{rc[inner]:.6f}", f"{rf[inner]:.6f}",
         f"{rf[inner] - rc[inner]:+.4e}",
         f"{100.0 * (rf[inner] - rc[inner]) / rc[inner]:+.4f}"],
        [f"Largest disagreement at any of the {d['n_write_times']} write "
         f"times, K",
         "--", "--",
         f"{d['largest_abs_diff_K']:.4e}",
         f"at t = {d['largest_abs_diff_time_s']:.0f} s, cell "
         f"{d['largest_abs_diff_cell']}"],
        ["Heat input left unaccounted by the energy budget, %",
         f"{100.0 - d['closure_percent_coarse']:.6f}",
         f"{100.0 - d['closure_percent_fine']:.6f}",
         "--", "--"],
    ]
    # Under usetex every cell is LaTeX source: the per-cent signs in the
    # header and the row labels would otherwise comment out the rest of the
    # line.  Numbers are untouched by tex_text.
    hdr = [LS.tex_text(c) for c in hdr]
    body = [[LS.tex_text(c) for c in row] for row in body]
    tb = ax3.table(cellText=body, colLabels=hdr, loc="upper center",
                   cellLoc="center",
                   colWidths=[0.34, 0.14, 0.14, 0.17, 0.21])
    tb.auto_set_font_size(False)
    tb.set_fontsize(8)
    tb.scale(1, 1.6)
    for (r, c), cell in tb.get_celld().items():
        cell.set_linewidth(0.5)
        if r == 0:
            cell.set_facecolor("#e8eef5")
            cell.set_text_props(fontsize=7.5)
        elif c == 0:
            cell.set_text_props(ha="left")
    # LaTeX never sees matplotlib's font weight, so the header is bolded in
    # the source instead.
    LS.bold_cells(tb, lambda k: k[0] == 0)
    # The table is drawn from the top of ax3 downward and does not fill it,
    # so the caption is placed just under the last row rather than at the
    # bottom of the axes, which would leave a band of empty page.
    ax3.text(0.0, 0.34, _wrapped(CAPTION, 132), transform=ax3.transAxes,
             fontsize=7.8, va="top", ha="left")

    fig.suptitle("Time step check, 0.5 s against 0.25 s", fontsize=10)
    for ext in ("pdf", "svg"):
        fig.savefig(f"{out}.{ext}", bbox_inches="tight")
    plt.close(fig)


def _wrapped(text, width):
    import textwrap
    return "\n".join(textwrap.wrap(text, width))


# ----------------------------------------------------------------- main
def main():
    for case in (CASE_COARSE, CASE_FINE):
        if not os.path.isdir(case):
            sys.exit(f"REFUSE: {case} is not on disk; nothing is written")

    print("PLANTED CONTROL (a) -- shared parser, the "
          f"{STEP_COARSE_S} s arm")
    A.selftest(CASE_COARSE)
    print()
    print("PLANTED CONTROL (a) -- shared parser, the "
          f"{STEP_FINE_S} s arm")
    A.selftest(CASE_FINE)
    print()

    plant = plant_difference_control(CASE_COARSE, CASE_FINE)
    print()

    d = difference_reading(CASE_COARSE, CASE_FINE)

    # The two groupings the screen quotes must be groupings, not one cell
    # standing for six: refuse if the cells in a group are not the same
    # number to the precision the table prints.
    rc, rf = d["peak_rise_coarse_K"], d["peak_rise_fine_K"]
    ends = [0, d["n_cells"] - 1]
    interior = list(range(1, d["n_cells"] - 1))
    for name, idx in (("end cells", ends), ("interior cells", interior)):
        for pair, tag in ((rc, "coarse"), (rf, "fine")):
            spread = float(np.max(pair[idx]) - np.min(pair[idx]))
            if spread > 5e-7:
                sys.exit(f"REFUSE: the {name} of the {tag} arm are not one "
                         f"number to the printed precision (spread "
                         f"{spread:.3e} K); the grouped table would be "
                         f"quoting one cell as if it were all of them")

    fig_step_independence(d, os.path.join(HERE, "actc_step_independence"))

    with open(os.path.join(HERE, "actc_step_independence.csv"), "w",
              newline="") as f:
        w = csv.writer(f)
        w.writerow(["module_cell", f"peak_rise_K_dt_{STEP_COARSE_S}",
                    f"peak_rise_K_dt_{STEP_FINE_S}", "difference_K",
                    "difference_percent"])
        for i in range(d["n_cells"]):
            w.writerow([i + 1, f"{rc[i]:.9f}", f"{rf[i]:.9f}",
                        f"{rf[i] - rc[i]:.9e}",
                        f"{100.0 * (rf[i] - rc[i]) / rc[i]:.6f}"])

    block = {
        "product": "Act C, C6.4 -- time-step independence, two arms",
        "record": RECORD,
        "case_coarse": CASE_COARSE,
        "case_fine": CASE_FINE,
        "reader": os.path.join(RUNS, "analyse_t25.py"),
        "generator": os.path.abspath(__file__),
        "time_step_coarse_s": STEP_COARSE_S,
        "time_step_fine_s": STEP_FINE_S,
        "n_write_times": d["n_write_times"],
        "n_module_cells": d["n_cells"],
        "instrument_check_step_difference_reader": plant,
        "caption": CAPTION,
        "step_independence_table": {
            "headers": ["Quantity", f"Time step {STEP_COARSE_S} s",
                        f"Time step {STEP_FINE_S} s", "Change", "Change, %"],
            "rows": [
                [f"Peak rise, end cells {END_CELLS[0]} and {END_CELLS[1]}, K",
                 f"{rc[0]:.6f}", f"{rf[0]:.6f}", f"{rf[0] - rc[0]:+.4e}",
                 f"{100.0 * (rf[0] - rc[0]) / rc[0]:+.4f}"],
                ["Peak rise, interior cells 2–7, K",
                 f"{rc[1]:.6f}", f"{rf[1]:.6f}", f"{rf[1] - rc[1]:+.4e}",
                 f"{100.0 * (rf[1] - rc[1]) / rc[1]:+.4f}"],
                [f"Largest disagreement at any of the {d['n_write_times']} "
                 f"write times, K",
                 "—", "—", f"{d['largest_abs_diff_K']:.4e}",
                 f"at t = {d['largest_abs_diff_time_s']:.0f} s, cell "
                 f"{d['largest_abs_diff_cell']}"],
                ["Heat input left unaccounted by the energy budget, %",
                 f"{100.0 - d['closure_percent_coarse']:.6f}",
                 f"{100.0 - d['closure_percent_fine']:.6f}",
                 "—", "—"],
            ],
        },
        "per_cell": [
            {"cell": i + 1,
             "peak_rise_K_coarse": float(rc[i]),
             "peak_rise_K_fine": float(rf[i]),
             "difference_K": float(rf[i] - rc[i]),
             "difference_percent": float(100.0 * (rf[i] - rc[i]) / rc[i])}
            for i in range(d["n_cells"])],
        "largest_abs_diff_K": d["largest_abs_diff_K"],
        "largest_abs_diff_time_s": d["largest_abs_diff_time_s"],
        "largest_abs_diff_cell": d["largest_abs_diff_cell"],
        "unaccounted_percent_coarse": 100.0 - d["closure_percent_coarse"],
        "unaccounted_percent_fine": 100.0 - d["closure_percent_fine"],
        "grading": ("NOT GRADED -- a two-point step-size check on an ungated "
                    "feasibility run. Two step sizes on one mesh are not "
                    "enough to put an error bar on the answer, so none is "
                    "quoted, and this product carries no verdict, no gate "
                    "and no threshold."),
    }
    with open(os.path.join(HERE, "actc_step_independence.json"), "w") as f:
        json.dump(block, f, indent=2)

    print(f"end cells      {rc[0]:.6f} -> {rf[0]:.6f} K  "
          f"({100.0 * (rf[0] - rc[0]) / rc[0]:+.4f} %)")
    print(f"interior cells {rc[1]:.6f} -> {rf[1]:.6f} K  "
          f"({100.0 * (rf[1] - rc[1]) / rc[1]:+.4f} %)")
    print(f"largest disagreement {d['largest_abs_diff_K']:.4e} K at "
          f"t = {d['largest_abs_diff_time_s']:.1f} s, cell "
          f"{d['largest_abs_diff_cell']}")
    print(f"unaccounted    {100.0 - d['closure_percent_coarse']:.6f} % -> "
          f"{100.0 - d['closure_percent_fine']:.6f} %")
    print("wrote actc_step_independence.{pdf,svg,csv,json}")


if __name__ == "__main__":
    main()
