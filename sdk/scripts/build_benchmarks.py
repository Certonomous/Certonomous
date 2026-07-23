"""Build the website benchmarks artifact from the mega-batch ledger.

Emits two files under demo-output/website/:

- ``benchmarks.json`` — per-solver stats (count, mean/median wall time,
  per-worker throughput), the closure-challenge target board, and the
  reduced-order speed benchmark (placeholders until BG-1's measured NACA 4412
  race numbers land).
- ``benchmarks.png`` — a clean four-panel matplotlib figure (titles, axed and
  unit-labelled, key values annotated) rendered to the house plot standard.

Re-run near end of shift so the numbers reflect the final ledger count::

    python sdk/scripts/build_benchmarks.py

The closure-challenge board is the PUBLIC leaderboard target only. We display no
"our score" — the entry is honestly "baseline in training, winners not yet
beaten". A real computed score is added only when one is measured.
"""

from __future__ import annotations

import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

_SDK = Path(__file__).resolve().parents[1]
if str(_SDK) not in sys.path:
    sys.path.insert(0, str(_SDK))

from chief_engineer import lab_stats  # noqa: E402

_REPO = _SDK.parent
_OUT = _REPO / "demo-output" / "website"
_LEDGER = _OUT / "mega-batch" / "ledger.jsonl"

# Validated categorical palette (dataviz reference, light mode), slots 1-3.
_C = {"openfoam-cylinder": "#2a78d6", "vspaero-wing": "#eb6834",
      "reduced-order": "#1baf7a"}
_SURFACE = "#fcfcfb"
_INK = "#0b0b0b"
_INK2 = "#52514e"
_GRID = "#e2e1dc"

_SOLVER_LABEL = {
    "openfoam-cylinder": "OpenFOAM cylinder\n(real solve)",
    "vspaero-wing": "VSPAERO wing\n(real solve)",
    "reduced-order": "Valve cycle\n(reduced-order)",
}

# Public closure-challenge leaderboard target (rank #4). Target values only.
_CLOSURE = {
    "name": "Closure-challenge benchmark",
    "status": "ACTIVE RESEARCH",
    "board": "public leaderboard",
    "target_rank": 4,
    "target_overall": 0.0779,
    "target_per_case": [0.068, 0.1364, 0.0591, 0.0882, 0.0895, 0.0866, 0.0487, 0.0464],
    "our_entry": "baseline in training — winners not yet beaten. Target: top 4.",
    "our_score": None,   # never displayed until a real computed score exists
}

# Speed benchmark — measured on this machine, 2026-07-23 (BG-1's NACA 4412
# race, pass 1 headline; pass 2 under heavier load gave 29.8x). Every point a
# real VSPAERO solve; details in docs/HANDOFF-BG1.md and
# demo-output/website/race/benchmarks.md.
_SPEED = {
    "name": "Reduced-order speed benchmark",
    "case": "NACA 4412",
    "full_mc_core_min": 45.4,
    "reduced_core_min": 2.1,
    "speedup_x": 21.5,
    "status": "measured",
    "source": "BG-1 measured race (docs/HANDOFF-BG1.md)",
}


def _ledger_span_hours(rows: list[dict]) -> float:
    stamps = []
    for r in rows:
        ts = r.get("timestamp")
        if not ts:
            continue
        try:
            stamps.append(datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"))
        except Exception:
            continue
    if len(stamps) < 2:
        return 0.0
    return (max(stamps) - min(stamps)).total_seconds() / 3600.0


def compute_stats() -> dict:
    rows = lab_stats.read_ledger(_LEDGER)
    ok = [r for r in rows if r.get("ok")]
    per_solver: dict[str, dict] = {}
    for solver in ("openfoam-cylinder", "vspaero-wing", "reduced-order"):
        walls = [float(r["wall_seconds"]) for r in ok
                 if r.get("solver") == solver and r.get("wall_seconds") is not None]
        if not walls:
            continue
        mean_w = statistics.fmean(walls)
        per_solver[solver] = {
            "label": "real-solve" if solver != "reduced-order" else "reduced-order-eval",
            "count": len(walls),
            "mean_wall_s": round(mean_w, 3),
            "median_wall_s": round(statistics.median(walls), 3),
            "min_wall_s": round(min(walls), 3),
            "max_wall_s": round(max(walls), 3),
            # What one worker sustains on this solver alone.
            "per_worker_throughput_per_hr": round(3600.0 / mean_w, 1) if mean_w else None,
        }
    span_h = _ledger_span_hours(ok)
    overall_tp = round(len(ok) / span_h, 1) if span_h > 0 else None
    return {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ledger": str(_LEDGER),
        "totals": {
            "evaluations_ok": len(ok),
            "evaluations_failed": len(rows) - len(ok),
            "wall_span_hours": round(span_h, 3),
            "observed_throughput_per_hr": overall_tp,
            "core_hours": round(sum(float(r.get("wall_seconds") or 0) for r in ok) / 3600.0, 3),
        },
        "per_solver": per_solver,
        "closure_challenge": _CLOSURE,
        "speed_benchmark": _SPEED,
    }


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def render_png(data: dict, out_path: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "figure.facecolor": _SURFACE,
        "axes.facecolor": _SURFACE,
        "axes.edgecolor": _GRID,
        "axes.labelcolor": _INK2,
        "text.color": _INK,
        "xtick.color": _INK2,
        "ytick.color": _INK2,
        "axes.grid": True,
        "grid.color": _GRID,
        "grid.linewidth": 0.8,
    })

    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    fig.suptitle("Certonomous — laboratory benchmarks",
                 fontsize=18, fontweight="bold", color=_INK, x=0.5, y=0.98)
    tot = data["totals"]
    fig.text(0.5, 0.938,
             f"{tot['evaluations_ok']:,} real evaluations on the ledger  ·  "
             f"{tot['core_hours']} solver core-hours  ·  "
             f"generated {data['generated_at']}",
             ha="center", fontsize=10.5, color=_INK2)

    solvers = list(data["per_solver"].keys())
    labels = [_SOLVER_LABEL.get(s, s) for s in solvers]
    colors = [_C.get(s, "#888888") for s in solvers]

    # Panel A — evaluation counts by solver.
    ax = axes[0][0]
    counts = [data["per_solver"][s]["count"] for s in solvers]
    bars = ax.bar(labels, counts, color=colors, width=0.62, zorder=3)
    ax.set_title("Real evaluations by solver", fontsize=13, fontweight="bold",
                 color=_INK, loc="left")
    ax.set_ylabel("evaluations (count)")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis="x", visible=False)
    for bar, c in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f"{c:,}", ha="center", va="bottom", fontsize=11,
                fontweight="bold", color=_INK)

    # Panel B — mean wall time by solver (log y, huge dynamic range).
    ax = axes[1][0]
    means = [data["per_solver"][s]["mean_wall_s"] for s in solvers]
    bars = ax.bar(labels, means, color=colors, width=0.62, zorder=3)
    ax.set_yscale("log")
    # Headroom so the tallest bar's two-line annotation clears the title.
    ax.set_ylim(min(means) * 0.4, max(means) * 12)
    ax.set_title("Mean wall time per evaluation", fontsize=13, fontweight="bold",
                 color=_INK, loc="left", pad=10)
    ax.set_ylabel("seconds (log scale)")
    ax.grid(axis="x", visible=False)
    for bar, s in zip(bars, solvers):
        m = data["per_solver"][s]["mean_wall_s"]
        tp = data["per_solver"][s]["per_worker_throughput_per_hr"]
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f"{m:g}s\n{tp:,.0f}/hr·worker", ha="center", va="bottom",
                fontsize=9.5, color=_INK)

    # Panel C — closure-challenge target board.
    ax = axes[0][1]
    cc = data["closure_challenge"]
    cases = [f"c{i+1}" for i in range(len(cc["target_per_case"]))]
    ax.bar(cases, cc["target_per_case"], color="#4a3aa7", width=0.66, zorder=3,
           alpha=0.9)
    ax.axhline(cc["target_overall"], color=_INK, linewidth=1.4, linestyle="--",
               zorder=4)
    ax.text(len(cases) - 0.5, cc["target_overall"],
            f"  overall target {cc['target_overall']}", ha="right", va="bottom",
            fontsize=10, fontweight="bold", color=_INK)
    ax.set_title(f"Closure-challenge benchmark — {cc['status']}", fontsize=13,
                 fontweight="bold", color=_INK, loc="left")
    ax.set_ylabel("target score (lower is better)")
    ax.set_xlabel(f"{cc['board']} target, rank #{cc['target_rank']}")
    ax.grid(axis="x", visible=False)
    ax.text(0.02, 0.94, "our entry: " + cc["our_entry"], transform=ax.transAxes,
            fontsize=9.5, color=_INK2, va="top", wrap=True,
            bbox=dict(boxstyle="round,pad=0.4", fc="#f2f1ec", ec=_GRID))

    # Panel D — speed benchmark card (text; pending until measured).
    ax = axes[1][1]
    ax.axis("off")
    sp = data["speed_benchmark"]
    ax.text(0.02, 0.92, sp["name"], fontsize=13, fontweight="bold", color=_INK,
            va="top")
    ax.text(0.02, 0.80, f"case: {sp['case']}", fontsize=11, color=_INK2, va="top")

    def _fmt(v, unit):
        return f"{v} {unit}" if v is not None else "pending measured run"

    lines = [
        ("full Monte-Carlo", _fmt(sp["full_mc_core_min"], "core-min")),
        ("reduced-order", _fmt(sp["reduced_core_min"], "core-min")),
        ("speedup", _fmt(sp["speedup_x"], "x")),
    ]
    y = 0.62
    for name, val in lines:
        ax.text(0.04, y, name, fontsize=11, color=_INK2, va="top")
        pending = "pending" in val
        ax.text(0.62, y, val, fontsize=12,
                fontweight="normal" if pending else "bold",
                color="#a06a00" if pending else _INK, va="top")
        y -= 0.13
    ax.text(0.02, 0.10, f"source: {sp['source']}", fontsize=9, color=_INK2,
            va="top", style="italic")

    fig.tight_layout(rect=(0, 0, 1, 0.925))
    fig.savefig(out_path, dpi=130, facecolor=_SURFACE)
    plt.close(fig)


def main() -> int:
    _OUT.mkdir(parents=True, exist_ok=True)
    data = compute_stats()
    (_OUT / "benchmarks.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
    render_png(data, _OUT / "benchmarks.png")
    print(f"[benchmarks] wrote benchmarks.json ({data['totals']['evaluations_ok']} evals) "
          f"+ benchmarks.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
