#!/usr/bin/env python3
"""make_t18_tables.py -- the numbers behind every T18 figure, as CSV, plus the
plots and the PDF copies. Plain python3, no ParaView.

    python3 docs/campaigns/T-family/demo/render_T18_paraview/make_t18_tables.py

WHY THE CSV IS NOT OPTIONAL
---------------------------
Act A ships ``actA_radial_profile.csv`` beside ``actA_radial_profile.pdf`` and
``actA_map_table.csv`` beside its table. The rule that produces this is simple:
a figure is a picture OF something, and the something has to be on disk beside
it or the figure is the only copy of a number nobody can check. Every plot this
script draws writes its own CSV first and plots FROM that CSV.

WHERE THE NUMBERS COME FROM, AND WHAT IS NOT RECOMPUTED HERE
-------------------------------------------------------------
Nothing in this file re-grades T18. The verdicts, the triples, the observed
orders and the GCIs are READ from ``gate_t18.json``, which the frozen comparator
``analyse_t18.py`` wrote. Re-deriving them here would produce a second set of
numbers with no standing, and if the two ever disagreed the figure would be
quietly wrong.

The two things this file DOES compute are the profile curves, and both come from
frozen instruments rather than from arithmetic typed here:

* the solved profile uses ``analyse_t18.read_field`` and ``analyse_t18.idx`` --
  the grade's own reader and the grade's own cell-index convention;
* the analytic profile uses ``exact_t18.Series`` -- the grade's own reference.

THE VERDICT
-----------
Rows G1, G2, G3: PASS. Rung ceiling: GATE REACHED. Both are stamped on every
figure through ``demo3d_render_common.assert_stamp``, which refuses a stamp
carrying a verdict word the case does not own, and refuses the word
"validation" outright -- T18's reference is an analytic series, and there is no
experiment anywhere in this rung.
"""
import csv
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt              # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages   # noqa: E402
import matplotlib.image as mpimg             # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "scripts"))
T18_RUNS = os.path.join(REPO, "verification", "runs", "T-family", "T18_runs")
sys.path.insert(0, T18_RUNS)

import demo3d_render_common as C             # noqa: E402
from exact_t18 import Series                 # noqa: E402
from analyse_t18 import read_field, idx      # noqa: E402

CASE = "T18_CU_f"
OUT = os.path.join(REPO, "docs", "campaigns", "T-family", "demo", "figures_T18")
GATE = os.path.join(T18_RUNS, "gate_t18.json")

N = 80
BI = 1.0
FO_END = 0.2
FO = {"1": 0.1, "2": 0.2}

STAMP = ("T18_CU_f ; 512000 cells (80 x 80 x 80) ; laplacianFoam ; "
         "rows G1 G2 G3: PASS ; rung ceiling: GATE REACHED")

SUB = ("Octant as solved ; symmetry at x=0 y=0 z=0 ; Robin faces at x=L y=L "
       "z=L ; Bi = 1.0 ; L = 0.010 m")

FAILS = []


def stamp_axes(fig, second=SUB):
    """The mandatory stamp, through the SAME guard the ParaView renders use."""
    C.assert_stamp(STAMP, CASE)
    C.assert_caption_renderable(second)
    fig.text(0.012, 0.040, STAMP, fontsize=8.5, color="#262626", family="DejaVu Sans")
    fig.text(0.012, 0.014, second, fontsize=7.2, color="#4a4a4a", family="DejaVu Sans")


def save(fig, base):
    png = os.path.join(OUT, base + ".png")
    pdf = os.path.join(OUT, base + ".pdf")
    fig.savefig(png, dpi=170, facecolor="white")
    fig.savefig(pdf, facecolor="white")
    plt.close(fig)
    for p in (png, pdf):
        C.verify_written_image(p)
    print(f"  wrote {base}.png / .pdf")


# ---------------------------------------------------------------------------
# 1. The graded rows -- READ from the comparator's own gate file
# ---------------------------------------------------------------------------

def graded_rows():
    with open(GATE, encoding="utf-8") as fh:
        gate = json.load(fh)
    rows = gate["rows"]

    csv_path = os.path.join(OUT, "T18_graded_rows.csv")
    cols = ["row", "quantity", "fine_value", "reference", "deviation_rel",
            "band_lo", "band_hi", "coarse", "medium", "fine", "triple",
            "observed_order_p", "GCI_percent", "verdict", "planted_zero_control"]
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        out = []
        for r in rows:
            # gate_t18.json's own key names, taken literally. Guessing at
            # them with .get(a, .get(b)) fallbacks is how a table quietly fills
            # a column with None and still renders.
            trip = r["triple"]
            pz = gate["planted_zero_controls"][r["row"]]
            rec = dict(
                row=r["row"],
                quantity=r["quantity"],
                fine_value=r["value_fine"],
                reference=r["reference"],
                deviation_rel=r["rel_deviation"],
                band_lo=r["band"][0],
                band_hi=r["band"][1],
                coarse=trip["c"],
                medium=trip["m"],
                fine=trip["f"],
                triple=r["triple_state"],
                observed_order_p=r["observed_order"],
                GCI_percent=r["gci_pct"],
                verdict=r["verdict"],
                planted_zero_control=pz["status"],
            )
            out.append(rec)
            w.writerow([rec[c] for c in cols])
    print(f"  wrote T18_graded_rows.csv ({len(out)} rows)")

    # --- the table figure, drawn FROM the csv that was just written ---
    with open(csv_path, encoding="utf-8") as fh:
        recs = list(csv.DictReader(fh))

    fig = plt.figure(figsize=(13.6, 3.35))
    ax = fig.add_axes([0.03, 0.30, 0.94, 0.52])
    ax.axis("off")
    ax.set_title("T18 graded rows -- fine level graded against an exact "
                 "analytic series, three-level Roache triple",
                 fontsize=11.5, loc="left", pad=14)

    head = ["row", "quantity", "fine value", "analytic reference",
            "deviation", "pre-registered band", "triple", "p", "GCI %",
            "planted zero", "verdict"]
    body = []
    for r in recs:
        q = {"G1": "theta mean over the octant",
             "G2": "theta at the cube centre (0,0,0)",
             "G3": "theta at a Robin face centre (1,0,0)"}.get(r["row"], "")
        body.append([
            r["row"], q,
            f"{float(r['fine_value']):.10f}",
            f"{float(r['reference']):.10f}",
            f"{float(r['deviation_rel']):+.3e}",
            f"[{float(r['band_lo']):.7f}, {float(r['band_hi']):.7f}]",
            r["triple"],
            f"{float(r['observed_order_p']):.4f}",
            f"{float(r['GCI_percent']):.2e}",
            r["planted_zero_control"],
            r["verdict"],
        ])

    tab = ax.table(cellText=body, colLabels=head, loc="upper center",
                   cellLoc="left", colLoc="left")
    tab.auto_set_font_size(False)
    tab.set_fontsize(8.0)
    tab.scale(1, 1.85)
    ncol = len(head)
    for (row, col), cell in tab.get_celld().items():
        cell.set_linewidth(0.4)
        cell.set_edgecolor("#c8c8c8")
        if row == 0:
            cell.set_facecolor("#eef1f5")
            cell.set_text_props(weight="bold", color="#222222")
        elif col == ncol - 1:
            cell.set_text_props(weight="bold", color="#14532d")
            cell.set_facecolor("#eaf6ee")
    tab.auto_set_column_width(list(range(ncol)))

    fig.text(0.03, 0.175,
             "Every value above is read from gate_t18.json, written by the "
             "frozen comparator analyse_t18.py. Nothing on this page is "
             "re-graded here.",
             fontsize=7.6, color="#555555")
    fig.text(0.03, 0.135,
             "The rung ceiling is GATE REACHED because the reference is an "
             "EXACT series: the rung scores V and never P. The row verdicts "
             "are PASS inside the pre-registered band.",
             fontsize=7.6, color="#555555")
    stamp_axes(fig)
    save(fig, "T18_graded_rows")
    return recs


# ---------------------------------------------------------------------------
# 2. The centreline profile -- solved field against the analytic series
# ---------------------------------------------------------------------------

def centreline_profile():
    """theta along the x axis at the cell-centre row nearest y = z = 0.

    That row runs from the CENTRE of the full cube (x* = 0, the symmetry corner)
    out to a ROBIN FACE (x* = 1), so it crosses the whole cooling front. It also
    passes through both pointwise graded rows: G2 sits at its inner end and G3
    at its outer end.

    The analytic curve is evaluated at the SAME cell-centre coordinates as the
    solved one, y* = z* = 0.5/N rather than 0. Comparing a cell-centre value
    against an analytic value at the face would manufacture a discrepancy of
    order 1/N that is a coordinate error, not a solver error.
    """
    S = Series(BI)
    cs = [(i + 0.5) / N for i in range(N)]        # cell-centre x*
    off = 0.5 / N                                  # y* = z* of that row

    csv_path = os.path.join(OUT, "T18_centreline_profile.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Fo", "x_star", "y_star", "z_star", "theta_solved",
                    "theta_analytic", "difference"])
        data = {}
        for td, fo in sorted(FO.items(), key=lambda kv: kv[1]):
            F = read_field(C.facts(CASE)["case_dir"], td, N)
            if len(F) != N ** 3:
                C.refuse(f"the field at t = {td} has {len(F):,} values, not "
                         f"{N**3:,}; this profile will not be drawn from it")
            xs, sol, ana = [], [], []
            for i in range(N):
                v = F[idx(N, i, 0, 0)]
                a = S.theta(cs[i], off, off, fo)
                xs.append(cs[i]); sol.append(v); ana.append(a)
                w.writerow([fo, f"{cs[i]:.8f}", f"{off:.8f}", f"{off:.8f}",
                            f"{v:.10f}", f"{a:.10f}", f"{v - a:+.3e}"])
            data[fo] = (xs, sol, ana)
    print(f"  wrote T18_centreline_profile.csv ({N * len(FO)} rows)")

    fig = plt.figure(figsize=(11.0, 6.6))
    ax = fig.add_axes([0.075, 0.40, 0.88, 0.50])
    axr = fig.add_axes([0.075, 0.155, 0.88, 0.195], sharex=ax)

    colours = {0.1: "#1f5fa8", 0.2: "#b3391c"}
    for fo, (xs, sol, ana) in sorted(data.items()):
        ax.plot(xs, ana, "-", color=colours[fo], lw=1.7,
                label=f"analytic series, Fo = {fo}  (80 terms)")
        ax.plot(xs[::3], sol[::3], "o", color=colours[fo], ms=3.4,
                markerfacecolor="white", markeredgewidth=0.9,
                label=f"solved, 80 x 80 x 80, Fo = {fo}")
        axr.plot(xs, [s - a for s, a in zip(sol, ana)], "-",
                 color=colours[fo], lw=1.3, label=f"Fo = {fo}")

    ax.set_ylabel("theta = (T - T_inf) / (T0 - T_inf)", fontsize=9.5)
    ax.set_title("T18 centreline profile: cube centre (x* = 0) out to a Robin "
                 "face (x* = 1), at the cell-centre row nearest y = z = 0",
                 fontsize=11.5, loc="left", pad=10)
    ax.legend(fontsize=8.2, frameon=False, ncol=2, loc="lower left")
    ax.grid(alpha=0.25, lw=0.5)
    ax.tick_params(labelbottom=False, labelsize=8.5)

    axr.axhline(0, color="#888888", lw=0.7)
    axr.set_ylabel("solved - analytic", fontsize=8.5)
    axr.set_xlabel("x* = x / L      (0 = cube centre by symmetry, "
                   "1 = Robin face)", fontsize=9.5)
    axr.grid(alpha=0.25, lw=0.5)
    axr.tick_params(labelsize=8.5)
    axr.legend(fontsize=8, frameon=False, ncol=2)

    # the two pointwise graded rows live on this line -- say where
    # textcoords is AXES FRACTION, not data. Placing these in data coordinates
    # put the G2 label below the visible y-range, so its arrow ran off the panel
    # to a caption nobody could read -- the label was simply gone from the page.
    ax.annotate("G2 graded here\n(cube centre, x* = 0)",
                xy=(0.0, data[0.2][1][0]), xycoords="data",
                xytext=(0.10, 0.80), textcoords="axes fraction",
                fontsize=8, color="#333333",
                arrowprops=dict(arrowstyle="->", color="#666666", lw=0.8))
    ax.annotate("G3 graded here\n(Robin face centre, x* = 1)",
                xy=(1.0, data[0.2][1][-1]), xycoords="data",
                xytext=(0.56, 0.26), textcoords="axes fraction",
                fontsize=8, color="#333333",
                arrowprops=dict(arrowstyle="->", color="#666666", lw=0.8))

    stamp_axes(fig, SUB + " ; profile and reference both at cell centres")
    save(fig, "T18_centreline_profile")
    return data


# ---------------------------------------------------------------------------
# 3. The front-march montage, and PDF copies of the ParaView renders
# ---------------------------------------------------------------------------

def front_march():
    """Fo = 0.1 beside Fo = 0.2 -- the front moving, at identical contour levels.

    The panels are the ParaView renders themselves, so each keeps its own burnt
    in stamp; this page adds only the pairing and the reading.
    """
    left = os.path.join(OUT, "T18_isosurfaces_Fo0.1.png")
    right = os.path.join(OUT, "T18_isosurfaces_Fo0.2.png")
    for p in (left, right):
        C.verify_written_image(p)

    fig = plt.figure(figsize=(15.0, 5.9))
    for i, (p, lab) in enumerate(((left, "Fo = 0.1  (t = 1 s)"),
                                  (right, "Fo = 0.2  (t = 2 s)"))):
        ax = fig.add_axes([0.005 + i * 0.5, 0.10, 0.49, 0.80])
        ax.imshow(mpimg.imread(p))
        ax.axis("off")
        ax.set_title(lab, fontsize=11, color="#222222")
    fig.text(0.012, 0.945,
             "T18 cooling front, same isosurface levels at both times: the "
             "shells move inward and the theta = 0.35 shell exists only at "
             "Fo = 0.2",
             fontsize=10.5, color="#222222")
    fig.text(0.012, 0.055,
             "At Fo = 0.1 the coldest cell in the octant is still theta = "
             "0.386, so a theta = 0.35 shell has not formed. Its absence in "
             "the left panel is the field, not a plotting choice.",
             fontsize=7.6, color="#555555")
    stamp_axes(fig)
    save(fig, "T18_front_march")


def pdf_copies():
    """A PDF beside every ParaView PNG, as Act A ships both."""
    made = 0
    for name in sorted(os.listdir(OUT)):
        if not name.endswith(".png"):
            continue
        base = name[:-4]
        pdf = os.path.join(OUT, base + ".pdf")
        if os.path.exists(pdf):
            continue                     # matplotlib figures wrote their own
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
    print("T18 tables, profiles and CSVs")
    print("=" * 74)
    os.makedirs(OUT, exist_ok=True)
    C.assert_stamp(STAMP, CASE)
    print(f"  stamp accepted: {STAMP}")
    graded_rows()
    centreline_profile()
    front_march()
    pdf_copies()
    print("  all figures carry the verdict stamp above")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except C.RenderRefusal as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)
