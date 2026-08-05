"""The master statistics table and the our-metric-vs-their-metric mapping.

TWO OUTPUTS.

(1) `closure_eval_master_table.md` / `.json` -- every number the battery
    and the public record produce, in one place, each row labelled with
    where it came from and whether it is ours or published. Three blocks:
      A. the public leaderboard, per case, as published (cited, not
         recomputed -- we cannot recompute another entrant's score without
         their prediction files, and we do not have them for three of the
         four entrants).
      B. our battery's train/validation cases: challenge metric on cells,
         plus the field diagnostics the challenge metric does not carry.
      C. the metric-vs-physics mapping for the eight submitted test
         predictions: score against continuity violation.

(2) `metric_vs_physics.png` -- the figure that shows a good challenge
    score co-existing with a worse field. Per test case, the submitted
    prediction and the raw-RANS floor are plotted as (challenge score,
    relative continuity error) and joined by an arrow, so the trade the
    scalar hides is visible as a direction.

SOURCES, all already on disk, none recomputed here:
  demo-output/website/closure_eval/{ph,duct}_battery.json  (this session)
  demo-output/website/closure_challenge_divergence_audit.json
  demo-output/website/closure_challenge_trained_entry_round4_duct.json
  /home/ubuntu/closure-challenge-benchmark/README.md       (leaderboard)

NO SCORING CALL AND NO GROUND-TRUTH READ HAPPENS HERE -- this script only
reads JSON that earlier, guarded runs wrote.

Run::
    /home/ubuntu/closure-venv/bin/python \
        sdk/scripts/closure_eval_battery/build_master_table.py
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import battery_common as bc  # noqa: E402

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

_WEB = bc.OUT_DIR.parent
_BENCH_README = Path.home() / "closure-challenge-benchmark" / "README.md"

CASE_ORDER = ["alpha_15_13929_4048", "alpha_15_13929_2024",
              "alpha_05_4071_4048", "alpha_05_4071_2024",
              "AR_1_Ret_360", "AR_3_Ret_360", "AR_14_Ret_180", "NASA_2DWMH"]

# Validated categorical palette (validate_palette.js, light surface #FFFFFF:
# lightness band pass, chroma floor pass, CVD separation pass worst dE 13.5
# deutan, normal-vision floor pass worst dE 29.9, contrast pass).
CAT = {
    "PH-corrected": "#0077BB",
    "duct-corrected": "#CC3311",
    "declined (raw RANS)": "#009988",
}
SUBMITTED_KIND = {
    "alpha_15_13929_4048": "PH-corrected",
    "alpha_15_13929_2024": "PH-corrected",
    "NASA_2DWMH": "PH-corrected",
    "AR_1_Ret_360": "duct-corrected",
    "AR_3_Ret_360": "duct-corrected",
    "AR_14_Ret_180": "duct-corrected",
    "alpha_05_4071_4048": "declined (raw RANS)",
    "alpha_05_4071_2024": "declined (raw RANS)",
}


def parse_leaderboard(md_path: Path):
    """Read the public leaderboard straight out of the benchmark repo's own
    README table, so the published numbers in our table are transcribed by
    machine rather than by hand."""
    rows, cases = [], None
    for line in md_path.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[0] == "Rank":
            cases = cells[3:]
            continue
        if cases and re.fullmatch(r"\d+", cells[0]):
            name = re.sub(r"\[([^\]]*)\].*", r"\1", cells[1])
            rows.append({"rank": int(cells[0]), "authors": name,
                         "overall": float(cells[2]),
                         "per_case": {c: float(v) for c, v in zip(cases, cells[3:])}})
        elif rows:
            break
    return rows, cases


def figure_metric_vs_physics(rows, outpath):
    """The mapping figure: challenge score against the continuity error of
    the field that earned it, submitted vs RANS floor, arrow between."""
    # The three ducts' RANS floors sit at ~1e-17 -- their fully-developed
    # unidirectional solution is EXACTLY solenoidal cell-wise. Plotting that
    # honestly on a log axis would spend 13 decades of the panel on machine
    # zero, so the axis is clipped and those points are pinned to the floor
    # line with a down-arrow marker and named in the annotation. The value
    # is not hidden: it is in the table and in the caption.
    FLOOR = 2e-4
    fig, ax = plt.subplots(figsize=(10.0, 6.2))
    seen = set()
    n_clipped = 0
    # label offsets tuned per case so the eight labels do not collide
    OFF = {"alpha_15_13929_4048": (6, 8), "alpha_15_13929_2024": (8, -3),
           "alpha_05_4071_4048": (-4, -14), "alpha_05_4071_2024": (7, -12),
           "AR_1_Ret_360": (8, 6), "AR_3_Ret_360": (-64, 9),
           "AR_14_Ret_180": (-20, 10), "NASA_2DWMH": (9, 2)}
    for r in rows:
        col = CAT[r["kind"]]
        lbl = r["kind"] if r["kind"] not in seen else None
        seen.add(r["kind"])
        y_sub = max(r["div_sub"], FLOOR)
        y_flr, clipped = max(r["div_floor"], FLOOR), r["div_floor"] < FLOOR
        n_clipped += int(clipped)
        moved = abs(r["score_sub"] - r["score_floor"]) > 1e-6 or \
            abs(r["div_sub"] - r["div_floor"]) > 1e-6
        if moved:
            ax.annotate("", xy=(r["score_sub"], y_sub),
                        xytext=(r["score_floor"], y_flr),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=1.3,
                                        alpha=0.75, shrinkA=6, shrinkB=7))
        ax.scatter([r["score_floor"]], [y_flr], s=62,
                   marker="v" if clipped else "o",
                   facecolors="none", edgecolors=col, linewidths=1.5, zorder=4)
        ax.scatter([r["score_sub"]], [y_sub], s=66, color=col,
                   edgecolors="white", linewidths=1.4, zorder=5, label=lbl)
        ax.annotate(r["case"], (r["score_sub"], y_sub), textcoords="offset points",
                    xytext=OFF.get(r["case"], (7, 5)), fontsize=7.5, color="#222222")
    ax.set_yscale("log")
    ax.set_ylim(FLOOR * 0.75, 0.35)
    ax.axhline(FLOOR, color="#999999", linestyle=":", linewidth=1.0, zorder=1)
    ax.annotate(f"axis floor — {n_clipped} RANS duct fields sit at "
                r"$\sim\!10^{-17}$, exactly solenoidal; pinned here as ▽",
                xy=(0.45, FLOOR), xycoords=("axes fraction", "data"),
                xytext=(0, 5), textcoords="offset points",
                fontsize=7, color="#666666")
    ax.set_xlabel("challenge score for that case  (scaled MAE at the 1000 "
                  "official evaluation points; lower is better) →")
    ax.set_ylabel(r"continuity error of the field that earned it:  "
                  r"$\|\nabla\!\cdot\!U\| \,/\, \|\nabla U\|_F$   (log scale)")
    ax.grid(alpha=0.25, linewidth=0.5, which="both")
    ax.set_axisbelow(True)
    # legend: colour = submission kind; marker fill = submitted vs floor
    handles, labels = ax.get_legend_handles_labels()
    from matplotlib.lines import Line2D
    handles += [Line2D([], [], marker="o", linestyle="none", color="#555555",
                       markerfacecolor="#555555", markersize=7,
                       label="submitted prediction (filled)"),
                Line2D([], [], marker="o", linestyle="none", color="#555555",
                       markerfacecolor="none", markersize=7,
                       label="raw-RANS floor (open) — arrow shows what the "
                             "correction bought and cost")]
    ax.legend(handles=handles, fontsize=7.5, loc="lower left", framealpha=0.95)
    ax.set_title(
        "A better score, a worse field: the eight submitted predictions\n"
        "Every arrow points left (score improves) and up (continuity degrades)\n"
        "scores: closure_challenge_trained_entry_round4_duct.json;  continuity: "
        "closure_challenge_stability_physicality_audit.md §2\n"
        "(volume-weighted RMS over every cell, one validated Green-Gauss "
        "operator applied identically to both fields)",
        fontsize=8.5, loc="left")
    fig.tight_layout()
    fig.savefig(outpath, dpi=160)
    plt.close(fig)


def main() -> int:
    ph = json.loads((bc.OUT_DIR / "ph_battery.json").read_text())
    duct = json.loads((bc.OUT_DIR / "duct_battery.json").read_text())
    div = json.loads((_WEB / "closure_challenge_divergence_audit.json").read_text())
    r4 = json.loads((_WEB / "closure_challenge_trained_entry_round4_duct.json").read_text())
    board, board_cases = parse_leaderboard(_BENCH_README)

    res = r4["official_test_harness_result"]
    per_case = res["round4_per_case"]
    floor = res["rans_identity_floor_per_case"]
    dpc = div["per_case"]

    # ---- Block C rows: metric vs physics, per submitted test case --------
    map_rows = []
    for case in CASE_ORDER:
        d = dpc[case]
        map_rows.append({
            "case": case,
            "kind": SUBMITTED_KIND[case],
            "score_sub": per_case[case],
            "score_floor": floor[case],
            "div_sub": max(d["div_over_grad_scale_corrected"], 1e-18),
            "div_floor": max(d["div_over_grad_scale_RANS"], 1e-18),
            "div_ratio": d["ratio_corrected_over_rans"],
        })
    figure_metric_vs_physics(map_rows, bc.OUT_DIR / "metric_vs_physics.png")

    # ---- Master table ----------------------------------------------------
    L = []
    A = L.append
    A("# Closure Challenge — master statistics table")
    A("")
    A(f"Assembled {datetime.now(timezone.utc).date()} by "
      "`sdk/scripts/closure_eval_battery/build_master_table.py` from records "
      "already on disk. **No scoring call and no ground-truth read happens in "
      "this script.** Companion: `CLOSURE_EVALUATION_PROTOCOL.md` (what each "
      "metric is and who uses it).")
    A("")
    A("---")
    A("")
    A("## A. The public leaderboard, as published")
    A("")
    A("Transcribed by machine from `~/closure-challenge-benchmark/README.md` "
      "(the benchmark's own statement that it, not the preprint, is "
      "\"the main source of up-to-date information\"). **These are other "
      "people's numbers on the eight official test cases. We did not "
      "recompute them and could not** — three of the four entrants' "
      "prediction files are in the repo, but re-scoring them would consume "
      "scoring calls on ground truth to no purpose. Our row is our own "
      "recorded round-4 result, not a leaderboard entry: **the entry has not "
      "been submitted**, so we do not appear on the board.")
    A("")
    hdr = ["source", "overall"] + CASE_ORDER
    A("| " + " | ".join(hdr) + " |")
    A("|" + "---|" * len(hdr))
    for r in board:
        cells = [f"{r['rank']}. {r['authors']} (published)", f"{r['overall']:.4f}"]
        cells += [f"{r['per_case'].get(c, float('nan')):.4f}" for c in CASE_ORDER]
        A("| " + " | ".join(cells) + " |")
    A("| **ours, round 4 (recorded, not submitted)** | "
      f"**{res['round4_overall']:.4f}** | "
      + " | ".join(f"**{per_case[c]:.4f}**" for c in CASE_ORDER) + " |")
    A("| raw-RANS floor (our measurement, zero ML) | 0.1036 | "
      + " | ".join(f"{floor[c]:.4f}" for c in CASE_ORDER) + " |")
    A("")
    A("Leaderboard caveat, recorded because it matters for any rank claim: "
      "the challenge preprint (arXiv:2603.28884) Table 1 lists **three** "
      f"entrants; this README lists **{['zero','one','two','three','four','five'][len(board)]}**"
      " (it adds Liu, Wang, Zhao & Xiao). The README is the "
      "later and self-declared authoritative source, and is what is "
      "transcribed above.")
    A("")
    A("---")
    A("")
    A("## B. The battery: what the metric sees, and what it does not")
    A("")
    A("Train and validation cases only — the cases where reading truth is "
      "legal under the benchmark's own split. **The models are the entry of "
      "record's own**, re-fit and anchored: PH pooled validation scaled MAE "
      f"came back {ph['validity_anchor']['pooled_validation_scaled_mae_this_run']} "
      f"against the recorded {ph['validity_anchor']['recorded_round1_value']}; "
      "duct variant D's `AR_7_Ret_180` came back "
      f"{duct['validity_anchor']['AR_7_Ret_180_corrected_scaled_mae_this_run']} "
      f"against the pre-registered "
      f"{duct['validity_anchor']['pre_registered_value']}.")
    A("")
    A("The scaled-MAE columns are the **challenge's own formula** "
      "(`mean ||U_pred - U_true|| / mean ||U_true||`) evaluated on every mesh "
      "cell rather than the 1000 official points, so they are comparable in "
      "kind to a leaderboard number but not identical to one.")
    A("")
    A("### B1. Periodic hills")
    A("")
    A("| case | role | cells | scaled MAE, RANS | scaled MAE, corrected | "
      "error removed | continuity error, RANS | continuity error, corrected |")
    A("|---|---|---|---|---|---|---|---|")
    for case, s in ph["per_case"].items():
        d = dpc.get(case)
        cr = f"{d['div_over_grad_scale_RANS'] * 100:.2f}%" if d else "—"
        cc = f"{d['div_over_grad_scale_corrected'] * 100:.2f}%" if d else "—"
        gain = s["scaled_mae_cells_rans"] - s["scaled_mae_cells_corrected"]
        A(f"| `{case}` | {s['group']} | {s['n_cells']} | "
          f"{s['scaled_mae_cells_rans']:.4f} | {s['scaled_mae_cells_corrected']:.4f} | "
          f"{100 * gain / s['scaled_mae_cells_rans']:+.1f}% | {cr} | {cc} |")
    A("")
    A("### B2. Ducts — the column the challenge metric has no way to show")
    A("")
    A("Secondary-flow intensity is the volume-weighted mean in-plane speed "
      "`|(Uy,Uz)|` divided by `U_b`. It is not a challenge metric and not "
      "taken from any paper; it is our scalar summary of the quantity "
      "Ling et al. (JFM 2016) Fig. 6 draws.")
    A("")
    A("| case | role | cells | AR | scaled MAE, RANS | scaled MAE, corrected | "
      "secondary-flow intensity: RANS | corrected | truth | fraction recovered |")
    A("|---|---|---|---|---|---|---|---|---|---|")
    for case, s in duct["per_case"].items():
        A(f"| `{case}` | {s['role']} | {s['n_cells']} | {s['aspect_ratio']:.0f} | "
          f"{s['scaled_mae_cells_rans']:.4f} | {s['scaled_mae_cells_corrected']:.4f} | "
          f"{s['secondary_flow_intensity_rans']:.1e} | "
          f"{s['secondary_flow_intensity_corrected']:.4f} | "
          f"{s['secondary_flow_intensity_truth']:.4f} | "
          f"{100 * s['secondary_flow_recovered_fraction']:.0f}% |")
    A("")
    A("---")
    A("")
    A("## C. The mapping: where a good score hides a bad field")
    A("")
    A("Figure: `closure_eval/metric_vs_physics.png`. Continuity numbers are "
      "quoted from `closure_challenge_stability_physicality_audit.md` §2 and "
      "its record `closure_challenge_divergence_audit.json` — not recomputed "
      "here.")
    A("")
    A("| test case | submitted field | score, floor → submitted | "
      "continuity error, floor → submitted | continuity ratio |")
    A("|---|---|---|---|---|")
    for r in map_rows:
        ratio = ("—" if r["kind"].startswith("declined")
                 else (f"{r['div_ratio']:.1f}×" if r["div_ratio"] < 1e6
                       else f"{r['div_ratio']:.0e}× (÷ machine zero)"))
        A(f"| `{r['case']}` | {r['kind']} | "
          f"{r['score_floor']:.4f} → **{r['score_sub']:.4f}** | "
          f"{100 * r['div_floor']:.2f}% → **{100 * r['div_sub']:.2f}%** | {ratio} |")
    A("")
    A("**What the table says, stated with the sign against us.** On the two "
      "hills the correction is applied to, the score improves by 0.082 and "
      "0.104 while the field's continuity error goes from 0.18% and 0.08% of "
      "its own velocity-gradient scale to 10.5% and 9.7% — a factor 58 and "
      "124. On the three ducts the RANS field is divergence-free to machine "
      "precision (its fully-developed unidirectional solution is exactly "
      "solenoidal cell-wise) and the corrected field is not, at 2.3–3.4%. "
      "**The scoring metric never sees any of this**, and nothing here "
      "changes the recorded 0.0654.")
    A("")
    A("**The two declined cases are the only submissions that are both "
      "competitive and clean.** They ship the organisers' own solve, so they "
      "inherit its physicality untouched (ratio 1.000 by construction) — and "
      "on both, the raw RANS floor already beats every published entrant for "
      "that case (0.0461 vs best-published 0.0569; 0.0719 vs 0.0760). The "
      "part of the entry that does nothing is the part that survives a "
      "physics check.")
    A("")

    md = "\n".join(L) + "\n"
    (bc.OUT_DIR / "closure_eval_master_table.md").write_text(md, encoding="utf-8")
    print(f"wrote {bc.OUT_DIR / 'closure_eval_master_table.md'}")

    bc.write_json(bc.OUT_DIR / "closure_eval_master_table.json", {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "produced_by": "sdk/scripts/closure_eval_battery/build_master_table.py",
        "scoring_calls": 0,
        "ground_truth_reads": 0,
        "leaderboard_as_published": board,
        "leaderboard_source": str(_BENCH_README),
        "leaderboard_row_count_readme": len(board),
        "leaderboard_row_count_preprint_table1": 3,
        "our_round4": {"overall": res["round4_overall"], "per_case": per_case,
                       "submitted_to_organisers": False},
        "rans_floor_per_case": floor,
        "metric_vs_physics_rows": map_rows,
        "ph_battery": ph["per_case"],
        "duct_battery": duct["per_case"],
    })
    print(f"wrote {bc.OUT_DIR / 'metric_vs_physics.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
