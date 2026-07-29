"""Shared figure builders for the five parametric-geometry acts.

Same dark GUI theme as chief_engineer.plot_theme (the control room's own
palette), specialised for two shapes every one of these acts needs:

- a coefficient/quantity time history over a periodic or settling solve,
  with the averaging window and its band marked directly on the curve;
- a refinement-ladder plot: the gate quantity at each mesh rung against the
  published/exact reference line.

Every axis carries an explicit label and unit; no plot in this module ever
carries a rolling-mean legend entry on a coefficient trace.
"""

from __future__ import annotations

from pathlib import Path


def history_plot(out_png: str | Path, times, values, *, ylabel: str, title: str,
                 window_start: float | None = None, mean: float | None = None,
                 band: float | None = None) -> str | None:
    from chief_engineer import plot_theme as t

    plt = t._pyplot()
    if plt is None:
        return None
    fig, ax = plt.subplots(figsize=(11.4, 4.6), dpi=150)
    ax.plot(times, values, color=t.LIVE, linewidth=1.1, label="solved history")
    if window_start is not None and mean is not None:
        ax.axvspan(window_start, times[-1] if times else window_start,
                  color=t.LIVE, alpha=0.08, linewidth=0,
                  label="averaging window")
        if band is not None:
            ax.axhspan(mean - band, mean + band, color=t.VALID, alpha=0.14,
                      linewidth=0, label="reported band")
        ax.axhline(mean, color=t.VALID, linewidth=1.6, label="reported mean")
    # An impulsive start can carry a brief transient spike many times the
    # settled amplitude; scaling the axis to the whole series would flatten
    # the settled oscillation this plot exists to show. The view is framed
    # on the settled window (or, absent one, a robust range of the whole
    # series) -- the full history is still drawn, just not what sets the
    # scale, so nothing is hidden, only framed to be readable.
    settled = ([v for tm, v in zip(times, values) if tm >= window_start]
              if window_start is not None else list(values))
    if settled:
        lo, hi = min(settled), max(settled)
        pad = max(0.15 * (hi - lo), 1e-6)
        ax.set_ylim(lo - pad, hi + pad)
    t.style_axes(ax, "Time (nondimensional convective units)", ylabel, title)
    leg = ax.legend(frameon=False, fontsize=10, labelcolor=t.INK, loc="best")
    for text in leg.get_texts():
        text.set_color(t.INK)
    fig.tight_layout()
    fig.savefig(out_png)
    plt.close(fig)
    return str(out_png)


def ladder_plot(out_png: str | Path, cells, values, *, ylabel: str, title: str,
                reference: float | None = None,
                reference_label: str = "reference") -> str | None:
    from chief_engineer import plot_theme as t

    plt = t._pyplot()
    if plt is None:
        return None
    fig, ax = plt.subplots(figsize=(9.0, 4.6), dpi=150)
    ax.plot(cells, values, color=t.LIVE, linewidth=2.0, marker="o",
           markersize=7, markeredgecolor=t.INK, markeredgewidth=0.8,
           label="mesh rungs")
    if reference is not None:
        ax.axhline(reference, color=t.VALID, linewidth=1.6, linestyle="--",
                  label=reference_label)
    t.style_axes(ax, "Cells", ylabel, title)
    leg = ax.legend(frameon=False, fontsize=10, labelcolor=t.INK, loc="best")
    for text in leg.get_texts():
        text.set_color(t.INK)
    fig.tight_layout()
    fig.savefig(out_png)
    plt.close(fig)
    return str(out_png)
