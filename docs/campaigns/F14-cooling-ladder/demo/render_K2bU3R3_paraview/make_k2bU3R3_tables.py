#!/usr/bin/env python3
"""make_k2bU3R3_tables.py -- the numbers behind the K2bU3R3 figures, as CSV,
plus the plots and the PDF copies. Plain python3, no ParaView.

    python3 docs/campaigns/F14-cooling-ladder/demo/render_K2bU3R3_paraview/make_k2bU3R3_tables.py

THE SERIES IS NOT RE-READ, IT IS IMPORTED
------------------------------------------
The graded quantity is the mass-flow-weighted inlet temperature averaged over
the four rack inlets, sampled from the solver log. This file does NOT write its
own parser for that. It imports ``analyse_k2bU3.series`` -- the reader the grade
itself used -- and repeats ``analyse_k2bU3.grade``'s combine, window and
peak-to-peak arithmetic with the imported constants ``DISCARD`` and ``WIN``.

Then it CHECKS ITSELF against the published grade. ``K2bU3R3_GRADE.txt`` states
final-window p2p 0.6058 K, preceding-window p2p 1.4414 K, ratio 0.420. If the
figure's numbers do not reproduce those to the printed precision this script
REFUSES, because a plot of a quantity that disagrees with the graded value of
the same quantity is worse than no plot: it is a second, unaccountable number
wearing the authority of the first.

THE VERDICT, AND THE WORD THAT IS NOT AVAILABLE HERE
-----------------------------------------------------
**GATE REACHED.** Not PASS. The gate is a survives/damps DISCRIMINATOR --
p2p >= 0.30 K AND ratio >= 0.8 means SURVIVES; p2p <= 0.10 K OR ratio <= 0.5
means DAMPS -- and it has no band for a value to be inside, so the
value-in-band word PASS does not apply to it. It was corrected away from PASS on
2026-09-09 under VERIFICATION_CHARTER section 2.

``demo3d_render_common.assert_stamp`` enforces that mechanically: PASS is absent
from this case's ``allowed_verdicts``, and any stamp carrying it is refused
before a figure is drawn.

WHAT THE OUTCOME DOES AND DOES NOT SAY
---------------------------------------
The 3-D case DAMPS the oscillation the 2-D slice sustained. Per the grade's own
outcome text, the 2-D finding STANDS as true of the 2-D slice -- it is not
retracted and it was not wrong. What changed is its extrapolation. The figures
say that and no more.
"""
import csv
import os
import statistics
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                        # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages   # noqa: E402
import matplotlib.image as mpimg                       # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "scripts"))
K2B_RUNS = os.path.join(REPO, "verification", "runs", "F14-cooling-ladder",
                        "K2b_runs")
sys.path.insert(0, K2B_RUNS)

import demo3d_render_common as C                       # noqa: E402
from analyse_k2bU3 import (                            # noqa: E402
    series, DISCARD, WIN, PERIOD_2D, P_SURV, P_DAMP, R_SURV, R_DAMP,
)

CASE = "K2bU3R3_D59"
OUT = os.path.join(REPO, "docs", "campaigns", "F14-cooling-ladder", "demo",
                   "figures_K2bU3R3")

RXS = [rf'weightedAverage\(rack{r}_in\) of T = ([-0-9.eE+]+)' for r in range(4)]

STAMP = ("K2bU3R3_D59 ; 137000 cells ; buoyantBoussinesqPimpleFoam ; "
         "GATE REACHED")
GEOM = ("Room 3.6 x 3.5 x 2.7 m ; 4 racks ; OPEN row ends ; graded quantity is "
        "the mean of the four rack inlet temperatures")

#: The published grade, from K2bU3R3_GRADE.txt. This script must reproduce it.
PUBLISHED = {"final_p2p": 0.6058, "pre_p2p": 1.4414, "ratio": 0.420,
             "final_mean": 293.5306, "outcome": "DAMPS"}
TOL = 5e-4          # the grade prints four decimals; agree to within half of one


def stamp_axes(fig, second=GEOM):
    C.assert_stamp(STAMP, CASE)
    C.assert_caption_renderable(second)
    fig.text(0.012, 0.036, STAMP, fontsize=8.5, color="#262626")
    fig.text(0.012, 0.013, second, fontsize=7.2, color="#4a4a4a")


def save(fig, base):
    png = os.path.join(OUT, base + ".png")
    pdf = os.path.join(OUT, base + ".pdf")
    fig.savefig(png, dpi=170, facecolor="white")
    fig.savefig(pdf, facecolor="white")
    plt.close(fig)
    for p in (png, pdf):
        C.verify_written_image(p)
    print(f"  wrote {base}.png / .pdf")


def graded_series():
    """The combined series and both windows, exactly as analyse_k2bU3.grade does."""
    times, per = series(CASE, RXS)
    keys = [k for k in RXS if k in per]
    if len(keys) != 4:
        C.refuse(f"only {len(keys)} of 4 rack inlet monitors were found in the "
                 f"solver log; the graded quantity is the mean over FOUR and "
                 f"this figure will not draw a mean over fewer")
    n = min(len(per[k]) for k in keys)
    ts = [(per[keys[0]][i][0],
           statistics.fmean(per[k][i][1] for k in keys)) for i in range(n)]

    fin = [(a, b) for a, b in ts if DISCARD + WIN < a <= DISCARD + 2 * WIN]
    pre = [(a, b) for a, b in ts if DISCARD < a <= DISCARD + WIN]
    Bv = max(b for _, b in fin) - min(b for _, b in fin)
    Pv = max(b for _, b in pre) - min(b for _, b in pre)
    ratio = Bv / Pv if Pv else float("inf")
    fmean = statistics.fmean([b for _, b in fin])

    # --- the self-check against the published grade -----------------------
    for name, got, want in (("final-window p2p", Bv, PUBLISHED["final_p2p"]),
                            ("preceding-window p2p", Pv, PUBLISHED["pre_p2p"]),
                            ("ratio", ratio, PUBLISHED["ratio"]),
                            ("final-window mean", fmean, PUBLISHED["final_mean"])):
        if abs(got - want) > TOL * max(1.0, abs(want)):
            C.refuse(
                f"this figure computes {name} = {got:.6f} where "
                f"K2bU3R3_GRADE.txt states {want}. A plot that disagrees with "
                f"the graded value of the same quantity is a second number "
                f"wearing the authority of the first. Refusing to draw it")
    print(f"  reproduces the grade: final p2p {Bv:.4f} K, preceding "
          f"{Pv:.4f} K, ratio {ratio:.3f}  (published {PUBLISHED['final_p2p']}, "
          f"{PUBLISHED['pre_p2p']}, {PUBLISHED['ratio']})")

    # per-rack series too, for the CSV
    per_rack = {r: per[RXS[r]] for r in range(4)}
    return ts, per_rack, fin, pre, Bv, Pv, ratio, fmean


def write_csv(ts, per_rack):
    path = os.path.join(OUT, "K2bU3R3_rack_inlet_series.csv")
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["time_s", "rack0_in_T_K", "rack1_in_T_K", "rack2_in_T_K",
                    "rack3_in_T_K", "mean_of_four_K", "window"])
        for i, (t, m) in enumerate(ts):
            win = ("preceding_40_60" if DISCARD < t <= DISCARD + WIN else
                   "final_60_80" if DISCARD + WIN < t <= DISCARD + 2 * WIN
                   else "discarded_0_40")
            w.writerow([f"{t:.4f}"] +
                       [f"{per_rack[r][i][1]:.6f}" for r in range(4)] +
                       [f"{m:.6f}", win])
    print(f"  wrote K2bU3R3_rack_inlet_series.csv ({len(ts)} rows)")
    return path


def fig_series(ts, per_rack, Bv, Pv, ratio, fmean):
    fig = plt.figure(figsize=(12.6, 6.6))
    ax = fig.add_axes([0.075, 0.205, 0.90, 0.70])

    t = [a for a, _ in ts]
    m = [b for _, b in ts]
    for r in range(4):
        ax.plot([a for a, _ in per_rack[r]], [b for _, b in per_rack[r]],
                lw=0.7, alpha=0.42,
                color=["#7aa6c2", "#8fb08a", "#c9a86a", "#c08fa8"][r],
                label=f"rack{r}_in" if r == 0 else None)
    ax.plot(t, m, color="#123f6d", lw=1.7,
            label="mean of the four rack inlets -- THE GRADED QUANTITY")

    ax.axvspan(DISCARD, DISCARD + WIN, color="#f0a04b", alpha=0.16, lw=0)
    ax.axvspan(DISCARD + WIN, DISCARD + 2 * WIN, color="#4b8bf0", alpha=0.16, lw=0)
    ax.axvspan(0, DISCARD, color="#bbbbbb", alpha=0.13, lw=0)

    for x0, x1, lab, col in ((0, DISCARD, "discarded\n0 to 40 s", "#777777"),
                             (DISCARD, DISCARD + WIN,
                              f"preceding window\n40 to 60 s\np2p {Pv:.4f} K",
                              "#a2620f"),
                             (DISCARD + WIN, DISCARD + 2 * WIN,
                              f"final window\n60 to 80 s\np2p {Bv:.4f} K",
                              "#1a4f9c")):
        ax.text((x0 + x1) / 2, 0.965, lab, transform=ax.get_xaxis_transform(),
                ha="center", va="top", fontsize=8.4, color=col, weight="bold")

    ax.set_xlabel("t  (s)", fontsize=9.5)
    ax.set_ylabel("rack inlet temperature  (K)", fontsize=9.5)
    ax.set_title("K2bU3R3 rack inlet temperature: the oscillation DAMPS in 3-D "
                 f"-- ratio {ratio:.3f} against a registered DAMPS threshold "
                 "of 0.5 or below", fontsize=11.3, loc="left", pad=10)
    ax.grid(alpha=0.25, lw=0.5)
    ax.legend(fontsize=8.4, frameon=False, loc="lower right")
    ax.tick_params(labelsize=8.5)

    fig.text(0.075, 0.105,
             f"Gate, fixed before the run: p2p >= {P_SURV} K AND ratio >= "
             f"{R_SURV} = SURVIVES ; p2p <= {P_DAMP} K OR ratio <= {R_DAMP} = "
             f"DAMPS. Measured ratio {ratio:.3f}, so DAMPS.",
             fontsize=7.7, color="#555555")
    fig.text(0.075, 0.078,
             "The 2-D slice sustained a limit cycle of period "
             f"{PERIOD_2D:.3f} s. That 2-D finding STANDS as true of the 2-D "
             "slice; what this case changes is its extrapolation to 3-D.",
             fontsize=7.7, color="#555555")
    stamp_axes(fig)
    save(fig, "K2bU3R3_rack_inlet_series")


def fig_gate_table(Bv, Pv, ratio, fmean, n_fin, n_pre):
    path = os.path.join(OUT, "K2bU3R3_gate.csv")
    rows = [
        ["final window 60-80 s peak-to-peak", f"{Bv:.4f}", "K",
         f"<= {P_DAMP} K means DAMPS", "measured"],
        ["preceding window 40-60 s peak-to-peak", f"{Pv:.4f}", "K",
         "reference for the ratio", "measured"],
        ["ratio final / preceding", f"{ratio:.3f}", "-",
         f"<= {R_DAMP} means DAMPS", "measured"],
        ["final window mean", f"{fmean:.4f}", "K", "reported", "measured"],
        ["samples in the final window", str(n_fin), "-",
         "aliasing floor 10 per period", "measured"],
        ["samples in the preceding window", str(n_pre), "-",
         "aliasing floor 10 per period", "measured"],
        ["SURVIVES threshold", f"p2p >= {P_SURV} and ratio >= {R_SURV}", "-",
         "pre-registered", "frozen"],
        ["DAMPS threshold", f"p2p <= {P_DAMP} or ratio <= {R_DAMP}", "-",
         "pre-registered", "frozen"],
        # NOT the bare token "PASS", deliberately. The planted-zero control did
        # pass -- K2bU3R3_GRADE.txt says "control PASSES" -- and that is a
        # property of the READER, not a verdict on the case. But this is a
        # K2bU3R3 table, and K2bU3R3's verdict is GATE REACHED and never PASS.
        # Printing the token here invites a reader scanning the column to carry
        # it to the case, so the control is reported in words instead and loses
        # nothing: it was armed, and it recovered the plant.
        ["planted-zero control", "armed; plant recovered", "-",
         "detection floor 1.234e-03 K, 81x below the 0.1 K DAMPS floor",
         "measured"],
        ["outcome", "DAMPS", "-", "the discriminator's answer", "graded"],
        # The explanatory text deliberately does NOT spell the forbidden token,
        # even to deny it. A CSV column is read by eye and by grep, and both
        # would report a PASS sitting in a K2bU3R3 table. The README carries the
        # full explanation in prose, where there is room to say why.
        ["VERDICT", "GATE REACHED", "-",
         "discriminator gate; the value-in-band verdict word does not apply",
         "graded"],
    ]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "value", "units", "pre_registered_meaning",
                    "status"])
        w.writerows(rows)
    print(f"  wrote K2bU3R3_gate.csv ({len(rows)} rows)")

    fig = plt.figure(figsize=(13.2, 5.2))
    ax = fig.add_axes([0.03, 0.20, 0.94, 0.66])
    ax.axis("off")
    ax.set_title("K2bU3R3 gate -- does the 2-D limit cycle survive in 3-D at "
                 "the 59 mm feasible mesh?", fontsize=11.5, loc="left", pad=12)
    tab = ax.table(cellText=rows,
                   colLabels=["quantity", "value", "units",
                              "pre-registered meaning", "status"],
                   loc="upper center", cellLoc="left", colLoc="left")
    tab.auto_set_font_size(False)
    tab.set_fontsize(8.0)
    tab.scale(1, 1.42)
    for (r, c), cell in tab.get_celld().items():
        cell.set_linewidth(0.4)
        cell.set_edgecolor("#c8c8c8")
        if r == 0:
            cell.set_facecolor("#eef1f5")
            cell.set_text_props(weight="bold", color="#222222")
        elif rows[r - 1][0] == "VERDICT":
            cell.set_facecolor("#eaf1f8")
            cell.set_text_props(weight="bold", color="#12395f")
    tab.auto_set_column_width([0, 1, 2, 3, 4])

    fig.text(0.03, 0.135,
             "Thresholds and windows are frozen in K2bU3R3_PREREGISTRATION.md "
             "and were fixed before the run. This page recomputes the measured "
             "rows through the grade's own reader and refuses if they differ "
             "from K2bU3R3_GRADE.txt.",
             fontsize=7.7, color="#555555")
    fig.text(0.03, 0.108,
             "The verdict is GATE REACHED. It is not PASS: a survives/damps "
             "discriminator has no band for a value to lie inside, so the "
             "value-in-band word does not apply to it.",
             fontsize=7.7, color="#555555")
    stamp_axes(fig)
    save(fig, "K2bU3R3_gate")


def pdf_copies():
    made = 0
    for name in sorted(os.listdir(OUT)):
        if not name.endswith(".png"):
            continue
        pdf = os.path.join(OUT, name[:-4] + ".pdf")
        if os.path.exists(pdf):
            continue
        img = mpimg.imread(os.path.join(OUT, name))
        h, w = img.shape[0], img.shape[1]
        fig = plt.figure(figsize=(w / 170.0, h / 170.0))
        ax = fig.add_axes([0, 0, 1, 1])
        ax.imshow(img)
        ax.axis("off")
        with PdfPages(pdf) as pp:
            pp.savefig(fig, facecolor="white")
        plt.close(fig)
        C.verify_written_image(pdf)
        made += 1
    print(f"  wrote {made} PDF copies of the ParaView renders")


def main() -> int:
    print("=" * 74)
    print("K2bU3R3_D59 tables, monitor series and CSVs")
    print("=" * 74)
    os.makedirs(OUT, exist_ok=True)
    C.assert_stamp(STAMP, CASE)
    print(f"  stamp accepted: {STAMP}")
    ts, per_rack, fin, pre, Bv, Pv, ratio, fmean = graded_series()
    write_csv(ts, per_rack)
    fig_series(ts, per_rack, Bv, Pv, ratio, fmean)
    fig_gate_table(Bv, Pv, ratio, fmean, len(fin), len(pre))
    pdf_copies()
    print("  all figures carry the verdict stamp above")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except C.RenderRefusal as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)
