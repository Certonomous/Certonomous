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


ARM_20 = REPO / "verification/runs/T-family/T25R2_MODULE_runs/T25R2_L1_OC20"
MONITOR_20 = ARM_20 / "postProcessing/module/module_minmax/0/fieldMinMax.dat"


def read_minmax_at(path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        cells = line.split("\t")
        rows.append((float(cells[0]), float(cells[2].strip()),
                     float(cells[4].strip())))
    if not rows:
        raise SystemExit(f"{path} carries no rows")
    return rows


def read_surface_at(path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        cells = line.split()
        rows.append((float(cells[0]), float(cells[-1])))
    if not rows:
        raise SystemExit(f"{path} carries no rows")
    return rows


OUTLET_10 = CASE / "postProcessing/coolant/outlet_Tbar/0/surfaceFieldValue.dat"
OUTLET_20 = ARM_20 / "postProcessing/coolant/outlet_Tbar/0/surfaceFieldValue.dat"
OC_GATE = CASE.parent / "OC_GATE.json"


def outlet_overlay() -> None:
    """THE MONEY SHOT, drawn where the gap actually lives. The 23.2 mK the
    registered check refused on is O3, the COOLANT OUTLET area-mean at the
    takeoff transient (analyse_t25R2.py:326); measured between the two arms'
    own outlet monitors it is 23.2 mK at t = 60 s, while the hottest-cell
    traces differ by at most 1.3 mK. So the overlay that makes the refusal
    legible is the outlet channel: both arms' own monitors, pulse shaded,
    with the 40-90 s inset where the two curves visibly separate during the
    pulse and collapse together after it. Every point is a monitor row;
    the annotated gap is computed from the two plotted curves and the
    allowance is read from the graded gate record, never retyped."""
    import json

    from chief_engineer import plot_theme as theme

    plt = theme._pyplot()
    a10 = read_surface_at(OUTLET_10)
    a20 = read_surface_at(OUTLET_20)
    if [t for t, _ in a10] != [t for t, _ in a20]:
        raise SystemExit("the two arms' outlet monitors carry different "
                         "time stamps; the overlay would be misaligned")
    gate = json.loads(OC_GATE.read_text(encoding="utf-8"))
    detail = gate["results"]["OUTER_LOOP_GATE"]["detail"]
    allowed_mk = float(detail["O3_tol"]) * 1000.0
    by20 = dict(a20)
    gap_60_mk = abs(a10[[t for t, _ in a10].index(60.0)][1] - by20[60.0]) \
        * 1000.0

    fig, ax = plt.subplots(figsize=(11.4, 4.6), dpi=150)
    ax.axvspan(0.0, SWITCH_S, color=theme.INK, alpha=0.06, linewidth=0)
    ax.plot([t for t, _ in a10], [v - 273.15 for _, v in a10],
            color=theme.LIVE, linewidth=1.4, label="10 sweeps per step")
    second = theme.WARN if hasattr(theme, "WARN") else theme.VALID
    ax.plot([t for t, _ in a20], [v - 273.15 for _, v in a20],
            color=second, linewidth=1.2, linestyle="--",
            label="20 sweeps per step")
    theme.style_axes(ax, "t (s)", "T (C)",
                     "Coolant outlet, two solver efforts")
    legend = ax.legend(frameon=False, fontsize=10, loc="lower right")
    for text in legend.get_texts():
        text.set_color(theme.INK)

    axins = ax.inset_axes([0.42, 0.12, 0.34, 0.5])
    for rows, colour, style in ((a10, theme.LIVE, "-"),
                                (a20, legend.get_lines()[1].get_color(),
                                 "--")):
        window = [(t, v - 273.15) for t, v in rows if 40 <= t <= 90]
        axins.plot([w[0] for w in window], [w[1] for w in window],
                   color=colour, linewidth=1.3, linestyle=style)
    axins.axvspan(40, SWITCH_S, color=theme.INK, alpha=0.06, linewidth=0)
    axins.set_title(f"takeoff transient: {gap_60_mk:.1f} mK apart, "
                    f"{allowed_mk:.1f} allowed", fontsize=8, color=theme.INK)
    axins.tick_params(labelsize=7, colors=theme.INK)
    for spine in axins.spines.values():
        spine.set_color(theme.INK)
        spine.set_alpha(0.4)
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / "actC_outlet_overlay.png"
    fig.savefig(target)
    plt.close(fig)
    print(f"wrote {target}")


def two_arm_overlay() -> None:
    """The COMPANION to the outlet money shot: the hottest-cell trace at 10
    sweeps against 20 sweeps. The two traces differ by at most 1.3 mK over
    the whole record, and showing that coincidence is the point -- the cells
    barely move between solver efforts; the outlet is where the refused
    23.2 mK lives. Every point is a row of one of the two arms' own
    monitors; nothing is synthesised, smoothed or shifted."""
    from chief_engineer import plot_theme as theme

    plt = theme._pyplot()
    a10 = read_minmax_at(MONITOR)
    a20 = read_minmax_at(MONITOR_20)
    fig, ax = plt.subplots(figsize=(11.4, 4.6), dpi=150)
    ax.axvspan(0.0, SWITCH_S, color=theme.INK, alpha=0.06, linewidth=0)
    ax.plot([r[0] for r in a10], [r[2] - 273.15 for r in a10],
            color=theme.LIVE, linewidth=1.4, label="10 sweeps per step")
    ax.plot([r[0] for r in a20], [r[2] - 273.15 for r in a20],
            color=theme.WARN if hasattr(theme, "WARN") else theme.VALID,
            linewidth=1.2, linestyle="--", label="20 sweeps per step")
    theme.style_axes(ax, "t (s)", "T (C)",
                     "Hottest cell, two solver efforts")
    legend = ax.legend(frameon=False, fontsize=10, loc="lower right")
    for text in legend.get_texts():
        text.set_color(theme.INK)

    # The inset that makes the refusal legible: the takeoff transient,
    # where the registered sweep check measured the 2.32e-2 K movement.
    axins = ax.inset_axes([0.42, 0.14, 0.30, 0.44])
    for rows, colour, style in ((a10, theme.LIVE, "-"),
                                (a20, legend.get_lines()[1].get_color(),
                                 "--")):
        window = [(t, mx - 273.15) for t, _mn, mx in rows if 40 <= t <= 90]
        axins.plot([w[0] for w in window], [w[1] for w in window],
                   color=colour, linewidth=1.2, linestyle=style)
    axins.axvspan(40, SWITCH_S, color=theme.INK, alpha=0.06, linewidth=0)
    by20 = {t: mx for t, _mn, mx in a20}
    coincide_mk = max(abs(mx - by20[t]) for t, _mn, mx in a10
                      if t in by20) * 1000.0
    axins.set_title(f"takeoff transient: traces within {coincide_mk:.1f} mK",
                    fontsize=8, color=theme.INK)
    axins.tick_params(labelsize=7, colors=theme.INK)
    for spine in axins.spines.values():
        spine.set_color(theme.INK)
        spine.set_alpha(0.4)
    fig.tight_layout()
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / "actC_two_arm_overlay.png"
    fig.savefig(target)
    plt.close(fig)
    print(f"wrote {target}")


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
    ax.axvspan(0.0, SWITCH_S, color=theme.INK, alpha=0.06, linewidth=0)
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
    outlet_overlay()
    two_arm_overlay()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
