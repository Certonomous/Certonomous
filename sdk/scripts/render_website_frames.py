"""Render per-iteration Cd / Cl convergence stills for the website video.

Source: the motorbike act's real force history (postProcessing forceCoeffs
coefficient.dat, 300 solver iterations). Frame k draws the history up to
iteration k with the rolling +-2 sigma envelope computed exactly as the act's
``plot_with_envelope`` computes it (window = 25, sample standard deviation),
in the control-room theme from ``chief_engineer.plot_theme``. Axes are fixed
across all frames so the assembled video does not jump.

    python scripts/render_website_frames.py [coefficient.dat] [out_root]

Outputs 1920x1080 PNGs:
    demo-output/plots/C_d/frame_0001.png ...
    demo-output/plots/C_l/frame_0001.png ...
"""

from __future__ import annotations

import sys
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))

from chief_engineer import plot_theme as t
from chief_engineer.head_engineer import parse_coefficient_history

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
DEFAULT_HISTORY = REPO / "mission-output" / "geometry-study" / "study-motorBike" / "coefficient.dat"
DEFAULT_OUT = lab_paths.PLOTS
WINDOW = 25          # the act's rolling-envelope window (plot_with_envelope)
MAX_FRAMES = 400     # above this, render every 2nd iteration


def rolling_envelope(series: list[float], window: int = WINDOW):
    """Rolling mean and +-2 sigma bounds, identical to plot_with_envelope."""
    means, los, his = [], [], []
    for i in range(len(series)):
        chunk = series[max(0, i - window + 1): i + 1]
        m = sum(chunk) / len(chunk)
        s = ((sum((v - m) ** 2 for v in chunk) / (len(chunk) - 1)) ** 0.5
             if len(chunk) > 1 else 0.0)
        means.append(m)
        los.append(m - 2 * s)
        his.append(m + 2 * s)
    return means, los, his


def render_series(name: str, iters: list[float], series: list[float],
                  out_dir: Path) -> int:
    plt = t._pyplot()
    out_dir.mkdir(parents=True, exist_ok=True)
    means, los, his = rolling_envelope(series)
    label = t.metric_label(name)
    n = len(series)

    # Fixed axes across every frame: the video must not jump.
    x_lo, x_hi = iters[0], iters[-1]
    y_all = series + los + his
    y_min, y_max = min(y_all), max(y_all)
    pad = 0.06 * (y_max - y_min or 1.0)
    y_lo, y_hi = y_min - pad, y_max + pad

    step = 1 if n <= MAX_FRAMES else 2
    picks = list(range(0, n, step))
    if picks[-1] != n - 1:
        picks.append(n - 1)

    fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=150)
    for frame, k in enumerate(picks, start=1):
        ax.clear()
        xs, ys = iters[:k + 1], series[:k + 1]
        ax.fill_between(xs, los[:k + 1], his[:k + 1], color=t.LIVE,
                        alpha=0.16, linewidth=0, label=r"$\pm 2\sigma$ envelope")
        ax.plot(xs, ys, color=t.LIVE, linewidth=0.9, alpha=0.4,
                label="coefficient history")
        ax.plot(xs, means[:k + 1], color=t.LIVE, linewidth=2.4,
                label="_nolegend_")
        ax.plot([xs[-1]], [ys[-1]], marker="o", markersize=7, color=t.LIVE,
                markeredgecolor=t.INK, markeredgewidth=1.0, zorder=5)

        sigma2 = his[k] - means[k]
        ax.annotate(f"{label} = {means[k]:.4g} $\\pm$ {sigma2:.2g} (95%)",
                    xy=(0.985, 0.955), xycoords="axes fraction", ha="right",
                    va="top", fontsize=14, color=t.INK, weight="bold")
        ax.annotate(f"iteration {int(iters[k])} / {int(iters[-1])}",
                    xy=(0.985, 0.895), xycoords="axes fraction", ha="right",
                    va="top", fontsize=11, color=t.MUTED)

        ax.set_xlim(x_lo, x_hi)
        ax.set_ylim(y_lo, y_hi)
        t.style_axes(ax, "solver iteration", label,
                     f"{label} convergence with uncertainty envelope")
        leg = ax.legend(frameon=False, fontsize=10.5, loc="upper center")
        for text in leg.get_texts():
            text.set_color(t.INK)
        fig.tight_layout()
        fig.savefig(out_dir / f"frame_{frame:04d}.png")
    plt.close(fig)
    return len(picks)


def main(argv: list[str]) -> int:
    history = Path(argv[0]) if argv else DEFAULT_HISTORY
    out_root = Path(argv[1]) if len(argv) > 1 else DEFAULT_OUT
    columns = parse_coefficient_history(history.read_text(encoding="utf-8"))
    iters = columns["Time"]
    for name, folder in (("Cd", "C_d"), ("Cl", "C_l")):
        count = render_series(name, iters, columns[name], out_root / folder)
        print(f"{name}: {count} frames -> {out_root / folder}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
