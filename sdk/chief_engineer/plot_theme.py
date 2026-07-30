"""Publication-grade, GUI-themed matplotlib figures.

Every report figure must read as part of the control room, not a default
matplotlib chart pasted in: the dark SpaceX skin, tabular mono numerals,
mathtext axis labels ($C_d$, $\\pm\\sigma$), a titled frame, a legend, and one
annotated key value. Figures are rendered wide (report-column width) so nothing
lands as a thumbnail.

The palette mirrors control_room.html so a PNG dropped into the report column is
indistinguishable in tone from the live canvases beside it.
"""

from __future__ import annotations

import math
from pathlib import Path

# --- palette lifted verbatim from control_room.html -----------------------
BG = "#0a0c0e"        # --panel
PANEL = "#0f1315"     # --panel-2
INK = "#f4f6f8"       # --ink
MUTED = "#868d95"     # --muted
DIM = "#545a61"       # --dim
LIVE = "#57a5ff"      # --live
VALID = "#4fd483"     # --validated
TREND = "#f2bb52"     # --trend
NEEDS = "#f26a5c"     # --needs
GRID = "#191d21"      # --line


def _pyplot():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    # A one-shot rcParams push so mathtext, mono numerals, and the dark frame
    # are the default for every figure this module makes.
    plt.rcParams.update({
        "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
        "text.color": INK, "axes.labelcolor": INK, "axes.edgecolor": MUTED,
        "xtick.color": MUTED, "ytick.color": MUTED,
        "font.family": "monospace", "font.size": 12,
        "mathtext.fontset": "cm", "axes.titlesize": 14,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    })
    return plt


def metric_label(name: str) -> str:
    """Mathtext axis label for a coefficient name — $C_d$, $C_\\ell$, $L/D$.

    Report figures label their axes in the same typeset math the live canvases
    and the memo use, never a bare ``Cd`` string.
    """
    key = str(name).strip()
    return {
        "Cd": r"$C_d$", "Cl": r"$C_\ell$", "CD": r"$C_D$", "CL": r"$C_L$",
        "L_D": r"$L/D$", "LD": r"$L/D$", "cd": r"$C_d$", "cl": r"$C_\ell$",
    }.get(key, key)


def style_axes(ax, xlabel: str, ylabel: str, title: str) -> None:
    ax.set_xlabel(xlabel, color=INK, fontsize=13)
    ax.set_ylabel(ylabel, color=INK, fontsize=13)
    ax.set_title(title, color=INK, fontsize=14, loc="left", pad=12, weight="bold")
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(DIM)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.tick_params(colors=MUTED, labelsize=10)


def waveform_figure(out_png: str | Path, phases, *, q_peak: float,
                    t_systole: float, t_cycle: float, alpha: float,
                    title: str | None = None) -> str | None:
    """The idealized systolic waveform with the k=3 weighted phase points marked.

    ``phases`` are the study's Phase records (name, tau, flow_rate, weight); the
    curve is the half-sine ejection pulse over one cardiac cycle, the three phase
    points are ringed and annotated with the stroke-volume weight each carries.
    """
    plt = _pyplot()
    if plt is None:
        return None

    # Half-sine ejection over systole (0..t_systole), zero through diastole.
    n = 400
    ts = [t_cycle * i / (n - 1) for i in range(n)]
    qs = []
    for t in ts:
        tau = t / t_systole
        qs.append((q_peak * math.sin(math.pi * tau) if 0.0 < tau < 1.0 else 0.0) * 1e3)

    q_top = max(qs) * 1.28   # headroom so the peak label clears the title

    fig, ax = plt.subplots(figsize=(11.4, 4.6), dpi=150)
    ax.axvspan(0, t_systole, color=VALID, alpha=0.05, linewidth=0)
    ax.fill_between(ts, 0, qs, color=LIVE, alpha=0.12, linewidth=0)
    ax.plot(ts, qs, color=LIVE, linewidth=2.4, label=r"$Q(t)=Q_{\mathrm{peak}}\,\sin(\pi t/T_s)$")

    # The three phase points, ringed and labelled with the stroke-volume weight
    # each carries. The peak sits highest, so its label is placed to the side to
    # clear both the curve and the title.
    q_max = max(p.flow_rate for p in phases)
    for p in phases:
        t = p.tau * t_systole
        q = p.flow_rate * 1e3
        ax.scatter([t], [q], s=120, color=TREND, edgecolor=INK,
                   linewidth=1.4, zorder=5)
        if p.flow_rate >= q_max - 1e-12:
            off, ha = (14, -8), "left"
        else:
            off, ha = (0, 16), "center"
        ax.annotate(f"{p.name.split()[0]}\n$w={p.weight:.2f}$",
                    xy=(t, q), xytext=off, textcoords="offset points",
                    ha=ha, fontsize=10.5, color=INK, fontfamily="monospace")
        ax.plot([t, t], [0, q], color=TREND, linewidth=0.9, alpha=0.5,
                linestyle=(0, (3, 3)))

    # Region labels sit just inside the plot near the axis — clear of the
    # legend above and the tick labels below.
    ax.text(t_systole * 0.5, q_top * 0.05, "systole, ejection", ha="center",
            va="bottom", fontsize=10, color=MUTED)
    ax.text((t_systole + t_cycle) / 2, q_top * 0.05, "diastole, valve shut",
            ha="center", va="bottom", fontsize=10, color=DIM)
    ax.annotate(rf"$\alpha \approx {alpha:.1f}$  (Womersley)",
                xy=(0.985, 0.62), xycoords="axes fraction", ha="right",
                fontsize=12, color=TREND, weight="bold")

    ax.set_xlim(0, t_cycle)
    ax.set_ylim(min(0, min(qs)) - 0.02, q_top)
    style_axes(ax, r"cardiac-cycle time  $t$  [s]",
               r"aortic flow rate  $Q$  [L/s]",
               title or "Idealized systolic waveform, three weighted phase points")
    leg = ax.legend(frameon=False, fontsize=10.5, labelcolor=INK, loc="upper left")
    for text in leg.get_texts():
        text.set_color(INK)
    fig.tight_layout()
    fig.savefig(out_png)
    plt.close(fig)
    return str(out_png)


def envelope_trace_figure(out_png: str | Path, xs, ys, los, his, *,
                          xlabel: str, ylabel: str, title: str,
                          series_label: str, annotation: str | None = None,
                          color: str = LIVE) -> str | None:
    """A streaming objective trace frozen to a publication figure.

    ``xs``/``ys`` are the iterates, ``los``/``his`` the running envelope. Mirrors
    the live canvas trace so a report PNG and the on-screen trace match.
    """
    plt = _pyplot()
    if plt is None:
        return None
    fig, ax = plt.subplots(figsize=(11.4, 4.6), dpi=150)
    if los and his:
        ax.fill_between(xs, los, his, color=color, alpha=0.15, linewidth=0,
                        label=r"$\pm\sigma$ envelope")
    ax.plot(xs, ys, color=color, linewidth=2.4, marker="o", markersize=5,
            markeredgecolor=INK, markeredgewidth=0.8, label=series_label)
    if annotation:
        ax.annotate(annotation, xy=(xs[-1], ys[-1]), xytext=(-8, 16),
                    textcoords="offset points", ha="right", fontsize=12,
                    color=INK, weight="bold")
    style_axes(ax, xlabel, ylabel, title)
    leg = ax.legend(frameon=False, fontsize=10.5, labelcolor=INK, loc="best")
    for text in leg.get_texts():
        text.set_color(INK)
    fig.tight_layout()
    fig.savefig(out_png)
    plt.close(fig)
    return str(out_png)
