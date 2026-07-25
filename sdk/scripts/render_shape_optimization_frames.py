"""Run the shape-optimization act headless and render one still per
design evaluation for the website video.

The act (workflows.shape_optimization) sweeps the cylinder diameter over
0.7-1.4 m through real OpenFOAM solves, then confirms and uncertainty-bands
the winner. Its emitted events are captured here; each frame shows the
current shape (cylinder cross-section, to scale, fixed axes) beside the
objective history so far, in the control-room theme. Real evaluations only,
no interpolated frames.

    python scripts/render_shape_optimization_frames.py

Outputs 1920x1080 PNGs at demo-output/plots/shape_optimization/frame_0001.png ...
plus the captured events at .../events.jsonl.
"""

from __future__ import annotations

import json
import math
import re
import sys
import time
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))

from chief_engineer import plot_theme as t

REPO = SDK.parent
OUT_DIR = REPO / "demo-output" / "plots" / "shape_optimization"

_ANCHOR_RE = re.compile(r"Anchor .*?: D=([-\d.eE]+), Cd=([-\d.eE]+)")
_CONFIRM_RE = re.compile(r"Confirmation solve: Cd=([-\d.eE]+) vs")
_PREDICT_RE = re.compile(r"Optimum predicted at D=([-\d.eE]+)")
_LABEL_RE = re.compile(r"D=([-\d.eE]+) m")
_CD_RE = re.compile(r"Cd=([-\d.eE]+)")


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
        code = shape_optimization.main(
            request="Find the drag-minimal cylinder within these tolerances",
            emit=emit)
        emit("runner.done", {"exit": code})
    return events


def evaluations(events: list[dict]) -> tuple[list[dict], dict | None]:
    """Reconstruct the design evaluations, in design order, plus the verdict."""
    from_dispatch: dict[int, dict] = {}
    anchors: list[dict] = []
    predicted_d = None
    verdict = None
    for record in events:
        event, payload = record["event"], record["payload"]
        if event == "dispatch.update" and payload.get("state") == "done":
            d = _LABEL_RE.search(payload.get("label", ""))
            cd = _CD_RE.search(payload.get("detail", ""))
            if d and cd:
                from_dispatch[int(payload.get("slot", len(from_dispatch)))] = {
                    "D": float(d.group(1)), "Cd": float(cd.group(1))}
        elif event == "transcript.entry":
            text = str(payload.get("text", payload))
            for m in _ANCHOR_RE.finditer(text):
                anchors.append({"D": float(m.group(1)), "Cd": float(m.group(2))})
            m = _PREDICT_RE.search(text)
            if m:
                predicted_d = float(m.group(1))
            m = _CONFIRM_RE.search(text)
            if m and predicted_d is not None:
                anchors.append({"D": predicted_d, "Cd": float(m.group(1)),
                                "confirmation": True})
        elif event == "result.verdict":
            verdict = payload
    if from_dispatch:
        evals = [from_dispatch[k] for k in sorted(from_dispatch)]
    else:
        evals = anchors
    return evals, verdict


def render(evals: list[dict], verdict: dict | None, out_dir: Path) -> int:
    plt = t._pyplot()
    out_dir.mkdir(parents=True, exist_ok=True)
    n = len(evals)
    d_max = max(e["D"] for e in evals)
    lim = 0.6 * d_max * 1.15
    cds = [e["Cd"] for e in evals]
    pad = 0.08 * (max(cds) - min(cds) or 1.0)
    y_lo, y_hi = min(cds) - pad, max(cds) + pad

    fig = plt.figure(figsize=(12.8, 7.2), dpi=150)
    gs = fig.add_gridspec(1, 2, width_ratios=(1.0, 1.35), wspace=0.28,
                          left=0.07, right=0.965, top=0.86, bottom=0.11)
    ax_shape = fig.add_subplot(gs[0, 0])
    ax_obj = fig.add_subplot(gs[0, 1])

    for k in range(n):
        current = evals[k]
        best = min(range(k + 1), key=lambda i: cds[i])

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
        xs_e = list(range(1, k + 2))
        ax_obj.plot(xs_e, cds[:k + 1], color=t.LIVE, linewidth=2.0,
                    marker="o", markersize=8, markeredgecolor=t.INK,
                    markeredgewidth=0.8, label="evaluated designs")
        ax_obj.plot([best + 1], [cds[best]], marker="o", markersize=11,
                    color=t.VALID, markeredgecolor=t.INK, markeredgewidth=1.2,
                    linestyle="none", label="best so far", zorder=5)
        ax_obj.annotate(f"$C_d$ = {current['Cd']:.4g}",
                        xy=(0.975, 0.955), xycoords="axes fraction",
                        ha="right", va="top", fontsize=14, color=t.INK,
                        weight="bold")
        ax_obj.annotate(f"evaluation {k + 1} / {n}"
                        + ("  (confirmation)" if current.get("confirmation") else ""),
                        xy=(0.975, 0.885), xycoords="axes fraction",
                        ha="right", va="top", fontsize=11, color=t.MUTED)
        if k == n - 1 and verdict:
            ax_obj.annotate(
                f"winner: $C_d$ = {verdict['value']} $\\pm$ {verdict['ci']} "
                f"({verdict.get('confidence', '95%')}, {verdict.get('envelope', '')})",
                xy=(0.975, 0.82), xycoords="axes fraction", ha="right",
                va="top", fontsize=11, color=t.VALID)
        ax_obj.set_xlim(0.5, n + 0.5)
        ax_obj.set_ylim(y_lo, y_hi)
        ax_obj.set_xticks(list(range(1, n + 1)))
        t.style_axes(ax_obj, "design evaluation", "$C_d$",
                     "Objective: drag coefficient")
        leg = ax_obj.legend(frameon=False, fontsize=10.5, loc="lower left")
        for text in leg.get_texts():
            text.set_color(t.INK)

        fig.suptitle("Shape optimization: drag-minimal cylinder, real solves",
                     color=t.INK, fontsize=15, fontweight="bold", x=0.07,
                     ha="left", y=0.955)
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
    evals, verdict = evaluations(events)
    if not evals:
        print("no design evaluations captured; no frames rendered")
        return 1
    count = render(evals, verdict, OUT_DIR)
    print(f"{count} frames -> {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
