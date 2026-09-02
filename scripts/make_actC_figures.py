#!/usr/bin/env python3
"""Figures for demo Act C, the battery module, read off the solved run.

One figure today: the module's hottest and coolest point against time, off
``postProcessing/module/module_minmax/0/fieldMinMax.dat`` of the completed
run ``T25R2_L1``, with the registered takeoff-to-cruise switch at t = 60 s
marked. Nothing is smoothed and nothing is typed: every value on the curve
is a row of the run's own monitor.

The act states beside every number from this run that the verification gate
refused the run as a certified result; this figure does not soften that. It
is the value printed beside the refusal, which is the lab's own doctrine for
a row that is not a result (CLAUDE.md rule 5).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "sdk"))

CASE = REPO / "verification/runs/T-family/T25R2_MODULE_runs/T25R2_L1"
MONITOR = CASE / "postProcessing/module/module_minmax/0/fieldMinMax.dat"
OUT = REPO / "docs/campaigns/T-family/demo/figures_actC"
SWITCH_S = 60.0   # registered pulse table breakpoint, system/fvOptions


def read_minmax():
    rows = []
    for line in MONITOR.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        cells = line.split("\t")
        rows.append((float(cells[0]), float(cells[2].strip()),
                     float(cells[4].strip())))
    if not rows:
        raise SystemExit(f"{MONITOR} carries no rows")
    return rows


def stage_field_render() -> None:
    """Copy the ParaView temperature render beside the curve, under a
    screen-safe name (the render's own file name carries a case id, which is
    never user visible). The provenance sidecar travels with it, and the copy
    refuses if the sidecar names a different case than this script reads."""
    import json
    import shutil

    source = CASE / "paraview" / f"{CASE.name}_field_T.png"
    side = source.with_suffix(".json")
    if not source.is_file() or not side.is_file():
        raise SystemExit(
            f"{source} or its sidecar is not on disk; run "
            f"scripts/render_thermal_paraview.py over the case first")
    record = json.loads(side.read_text(encoding="utf-8"))
    if Path(record.get("case", "")).resolve() != CASE.resolve():
        raise SystemExit(
            "the field render's sidecar names a different case; it will not "
            "be staged under this act's name")
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, OUT / "actC_temperature_field.png")
    shutil.copy2(side, OUT / "actC_temperature_field.json")
    print(f"wrote {OUT / 'actC_temperature_field.png'}")


def main() -> int:
    from chief_engineer import plot_theme as theme

    plt = theme._pyplot()
    if plt is None:
        raise SystemExit("matplotlib is not available")
    rows = read_minmax()
    times = [r[0] for r in rows]
    hottest = [r[2] - 273.15 for r in rows]
    coolest = [r[1] - 273.15 for r in rows]

    fig, ax = plt.subplots(figsize=(11.4, 4.6), dpi=150)
    ax.plot(times, hottest, color=theme.LIVE, linewidth=1.4,
            label="hottest point in the module")
    ax.plot(times, coolest, color=theme.VALID, linewidth=1.1,
            label="coolest point in the module")
    ax.axvline(SWITCH_S, color=theme.INK, linewidth=0.9, alpha=0.5)
    ax.annotate("takeoff to cruise, t = 60 s",
                xy=(SWITCH_S, hottest[-1]),
                xytext=(SWITCH_S + 30.0, hottest[-1] - 0.6),
                color=theme.INK, fontsize=10)
    theme.style_axes(ax, "t (s)", "T (C)",
                     "Module temperature under the pulse")
    legend = ax.legend(frameon=False, fontsize=10, loc="lower right")
    for text in legend.get_texts():
        text.set_color(theme.INK)
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / "actC_module_history.png"
    fig.savefig(target)
    print(f"wrote {target}")
    stage_field_render()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
