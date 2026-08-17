"""Run the shape-optimization act headless and render one still per gradient
step for the website video.

The act (workflows.shape_optimization) calibrates a differentiable
reduced-order model on solver runs, walks the model's design gradient from
the starting shape to the optimum, and confirms the converged shape with a
solver run. Its emitted events are captured here; each frame shows the
current shape (cylinder cross-section, to scale, fixed axes) beside the
objective descending along the gradient walk, in the control-room theme.
One frame per computed gradient-trajectory point, none interpolated.

    python scripts/render_shape_optimization_frames.py           # run the act
    python scripts/render_shape_optimization_frames.py --replay  # reuse events

Outputs 1920x1080 PNGs at demo-output/plots/shape_optimization/frame_0001.png ...
plus the captured events at .../events.jsonl.
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))

from chief_engineer import plot_theme as t

# The one module that names this repository's tree (MOVE_MAP batch 3).
# Every name it exports is bound to a legacy/successor PAIR resolved
# against the filesystem at import, so the constants below are correct
# before the move, between batches and after it, with no edit here.
import sys as _sys  # noqa: E402
import pathlib as _pathlib  # noqa: E402
_LAB_PATHS_DIR = str(_pathlib.Path(__file__).resolve().parents[2]
                     / "scripts")
if _LAB_PATHS_DIR not in _sys.path:
    _sys.path.insert(0, _LAB_PATHS_DIR)
import lab_paths  # noqa: E402

REPO = SDK.parent
OUT_DIR = lab_paths.PLOTS / "shape_optimization"


def run_act(events_path: Path) -> list[dict]:
    events: list[dict] = []
    events_path.parent.mkdir(parents=True, exist_ok=True)
    with open(events_path, "w", encoding="utf-8") as fh:
        def emit(event: str, payload: dict) -> None:
            record = {"t": time.time(), "event": event, "payload": payload}
            events.append(record)
            try:
                fh.write(json.dumps(record) + "\n")
                fh.flush()
            except (TypeError, ValueError, OSError):
                pass

        from workflows import shape_optimization
        # The staged route is the one the website films: calibration solver
        # runs, then the gradient walk on the model, then the confirmation
        # run. force_scarce commits the act to it regardless of spare cores.
        code = shape_optimization.main(
            request="Find the drag-minimal cylinder within these tolerances",
            force_scarce=True, emit=emit)
        emit("runner.done", {"exit": code})
    return events


def trajectory(events: list[dict]) -> tuple[list[dict], list[dict],
                                            dict | None, dict | None]:
    """The gradient trajectory plus calibration, confirmation, and verdict."""
    steps: list[dict] = []
    calibration: list[dict] = []
    confirmation: dict | None = None
    verdict: dict | None = None
    for record in events:
        event, payload = record["event"], record["payload"]
        if event == "descent.step":
            steps.append(payload)
        elif event == "calibration.solve":
            calibration.append(payload)
        elif event == "confirmation.solve":
            confirmation = payload
        elif event == "result.verdict":
            verdict = payload
    steps.sort(key=lambda p: p.get("step", 0))
    return steps, calibration, confirmation, verdict


def render(steps: list[dict], calibration: list[dict],
           confirmation: dict | None, verdict: dict | None,
           out_dir: Path) -> int:
    plt = t._pyplot()
    out_dir.mkdir(parents=True, exist_ok=True)
    for stale in out_dir.glob("frame_*.png"):
        stale.unlink()
    n = len(steps)
    last = n - 1
    ds = [p["D"] for p in steps]
    objs = [p["objective"] for p in steps]
    d_max = max(ds + ([confirmation["D"]] if confirmation else []))
    lim = 0.6 * d_max * 1.15
    y_vals = objs + ([confirmation["Cd"]] if confirmation else [])
    pad = 0.08 * (max(y_vals) - min(y_vals) or 1.0)
    y_lo, y_hi = min(y_vals) - pad, max(y_vals) + pad

    fig = plt.figure(figsize=(12.8, 7.2), dpi=150)
    gs = fig.add_gridspec(1, 2, width_ratios=(1.0, 1.35), wspace=0.28,
                          left=0.07, right=0.965, top=0.86, bottom=0.11)
    ax_shape = fig.add_subplot(gs[0, 0])
    ax_obj = fig.add_subplot(gs[0, 1])

    for k in range(n):
        current = steps[k]

        ax_shape.clear()
        theta = [2 * math.pi * i / 200 for i in range(201)]
        r = current["D"] / 2
        xs = [r * math.cos(a) for a in theta]
        ys = [r * math.sin(a) for a in theta]
        ax_shape.fill(xs, ys, color=t.LIVE, alpha=0.15, linewidth=0)
        ax_shape.plot(xs, ys, color=t.LIVE, linewidth=2.4)
        ax_shape.annotate("flow", xy=(-0.52 * lim, 0.90 * lim), fontsize=10,
                          color=t.MUTED, ha="center", va="bottom")
        ax_shape.annotate("", xy=(-0.3 * lim, 0.86 * lim),
                          xytext=(-0.75 * lim, 0.86 * lim),
                          arrowprops={"arrowstyle": "->", "color": t.MUTED,
                                      "linewidth": 1.6})
        ax_shape.annotate(f"D = {current['D']:.3g} m", xy=(0, 0),
                          ha="center", va="center", fontsize=13,
                          color=t.INK, weight="bold")
        ax_shape.set_xlim(-lim, lim)
        ax_shape.set_ylim(-lim, lim)
        ax_shape.set_aspect("equal")
        t.style_axes(ax_shape, "x [m]", "y [m]",
                     "Current shape: cylinder section")

        ax_obj.clear()
        ax_obj.plot(list(range(k + 1)), objs[:k + 1], color=t.LIVE,
                    linewidth=2.2, label="gradient descent on the model")
        ax_obj.plot([k], [objs[k]], marker="o", markersize=9, color=t.LIVE,
                    markeredgecolor=t.INK, markeredgewidth=1.0,
                    linestyle="none", zorder=5)
        ax_obj.annotate(f"$C_d$ = {objs[k]:.4g}",
                        xy=(0.975, 0.955), xycoords="axes fraction",
                        ha="right", va="top", fontsize=14, color=t.INK,
                        weight="bold")
        ax_obj.annotate(f"step {k} / {last}, following the design gradient",
                        xy=(0.975, 0.885), xycoords="axes fraction",
                        ha="right", va="top", fontsize=11, color=t.MUTED)
        ax_obj.annotate(f"$dC_d/dD$ = {current['gradient']:+.3g} per m",
                        xy=(0.975, 0.825), xycoords="axes fraction",
                        ha="right", va="top", fontsize=11, color=t.MUTED)
        if calibration:
            ax_obj.annotate(
                f"{len(calibration)} solver runs calibrate the model",
                xy=(0.975, 0.705), xycoords="axes fraction",
                ha="right", va="top", fontsize=10, color=t.MUTED)
        if k == last and confirmation:
            ax_obj.plot([last], [confirmation["Cd"]], marker="o",
                        markersize=11, color=t.VALID, markeredgecolor=t.INK,
                        markeredgewidth=1.2, linestyle="none", zorder=6,
                        label="confirmed with a solver run")
            note = f"confirmed: $C_d$ = {confirmation['Cd']:.4g}"
            if verdict:
                note += (f" $\\pm$ {verdict['ci']} "
                         f"({verdict.get('confidence', '95%')}, "
                         f"{verdict.get('envelope', '')})")
            ax_obj.annotate(note, xy=(0.975, 0.765), xycoords="axes fraction",
                            ha="right", va="top", fontsize=11, color=t.VALID)
        ax_obj.set_xlim(-0.5, last + 0.5)
        ax_obj.set_ylim(y_lo, y_hi)
        t.style_axes(ax_obj, "gradient step", "$C_d$",
                     "Objective: drag coefficient on the calibrated model")
        leg = ax_obj.legend(frameon=False, fontsize=10.5, loc="lower left")
        for text in leg.get_texts():
            text.set_color(t.INK)

        fig.suptitle("Shape optimization: the geometry follows the design "
                     "gradient", color=t.INK, fontsize=15, fontweight="bold",
                     x=0.07, ha="left", y=0.955)
        fig.savefig(out_dir / f"frame_{k + 1:04d}.png")
    plt.close(fig)
    return n


def main() -> int:
    events_path = OUT_DIR / "events.jsonl"
    if "--replay" in sys.argv and events_path.exists():
        events = [json.loads(line)
                  for line in events_path.read_text(encoding="utf-8").splitlines()
                  if line.strip()]
    else:
        events = run_act(events_path)
    steps, calibration, confirmation, verdict = trajectory(events)
    if not steps:
        print("no gradient trajectory captured; no frames rendered")
        return 1
    count = render(steps, calibration, confirmation, verdict, OUT_DIR)
    print(f"{count} frames -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
