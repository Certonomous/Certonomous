"""ACT PLOT LIBRARY — the figures every act produces, one function each.

Paper theme, to match the control room's narrative column and the register:
white panel, ink text, one colour bar, tabular numerals, a legend inside the
axes, and the figure standard on every output (title <= 10 words, axis labels
with units, one caption line handled by the act, min/max only on the bar).

Every function takes plain arrays / dicts as inputs so the lab can call it
straight from a run tree, and every function accepts ``pending=True``, which
draws the SAME axes and labels with a "run in progress" mark instead of data.
That is what lets the GUI be built before the runs land: the act spec names
the function and its inputs; the lab swaps ``pending`` for the numbers.

    from workflows.act_plots_lib import cp_stations, grid_family, force_history
    cp_stations(out, stations=[{"eta":0.20,"xc":[...],"cp_cfd":[...],"xc_exp":[...],"cp_exp":[...]}, ...],
                title="Surface pressure, six AGARD stations", band=0.05)

All functions return the Path they wrote.
"""
from __future__ import annotations

from pathlib import Path
from typing import Mapping, Sequence

INK = "#182233"; INK2 = "#4A5568"; RULE = "#CBD3DC"; PAPER = "#FFFFFF"
GREEN = "#1F7A5C"; BLUE = "#2B5FB3"; AMBER = "#B7791F"; RED = "#B42318"; GREY = "#8A94A6"

def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.facecolor": PAPER, "axes.facecolor": PAPER, "savefig.facecolor": PAPER,
        "axes.edgecolor": RULE, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
        "text.color": INK, "axes.grid": True, "grid.color": "#EEF1F4", "grid.linewidth": 0.8,
        "font.family": "DejaVu Sans", "font.size": 10.5, "axes.titlesize": 12, "axes.titleweight": "semibold",
        "axes.titlelocation": "left", "legend.frameon": False, "legend.fontsize": 9.5,
        "axes.spines.top": False, "axes.spines.right": False, "mathtext.default": "regular",
    })
    return plt

def _pending(ax, note="run in progress"):
    ax.text(0.5, 0.5, note, transform=ax.transAxes, ha="center", va="center",
            fontsize=13, color=GREY, alpha=0.9,
            bbox=dict(boxstyle="round,pad=0.5", fc="#F3F5F7", ec=RULE))

def _finish(fig, out: Path, dpi=150) -> Path:
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(); fig.savefig(out, dpi=dpi); 
    import matplotlib.pyplot as plt; plt.close(fig)
    return out

# ---------------------------------------------------------------- aero: Cp at stations
def cp_stations(out, stations: Sequence[Mapping] = (), *, title="Surface pressure at the tap stations",
                band: float | None = None, pending=False, ncols=3):
    """One panel per span station: Cp vs x/c, CFD line, experiment markers, optional +-band.
    station keys: eta, xc, cp_cfd, xc_exp, cp_exp (lists)."""
    plt = _plt()
    n = max(len(stations), 6 if pending else 1)
    rows = -(-n // ncols)
    fig, axes = plt.subplots(rows, ncols, figsize=(11, 3.1 * rows), sharey=True)
    axes = axes.ravel() if hasattr(axes, "ravel") else [axes]
    for k, ax in enumerate(axes):
        ax.invert_yaxis(); ax.set_xlabel("x / c  [–]"); 
        if k % ncols == 0: ax.set_ylabel("$C_p$  [–]")
        if pending or k >= len(stations):
            ax.set_title(f"η = {'—' if pending else stations[k]['eta']}", fontsize=10.5, loc="left")
            ax.set_xlim(0, 1); ax.set_ylim(1.2, -1.6); _pending(ax); continue
        s = stations[k]; ax.set_title(f"η = {s['eta']:.2f}", fontsize=10.5, loc="left")
        if band: ax.fill_between(s["xc"], [c - band for c in s["cp_cfd"]], [c + band for c in s["cp_cfd"]], color=BLUE, alpha=.10, lw=0, label=f"±{band:g} band")
        ax.plot(s["xc"], s["cp_cfd"], color=BLUE, lw=1.6, label="lab")
        if s.get("xc_exp") is not None: ax.plot(s["xc_exp"], s["cp_exp"], "o", ms=3.2, color=INK, mfc="none", label="tunnel")
        ax.set_ylim(top=min(-1.6, min(s["cp_cfd"]) - 0.1), bottom=1.2)   # aero convention: suction up
        if k == 0: ax.legend(loc="lower right")
    fig.suptitle(title, x=0.01, ha="left", fontsize=12.5, fontweight="semibold")
    return _finish(fig, out)

# ---------------------------------------------------------------- grid family / observed order
def grid_family(out, levels: Sequence[Mapping] = (), *, quantity="$C_d$", unit="[–]", order=None, gci=None,
                title="Grid family and observed order", reference=None, pending=False, band=None):
    """quantity vs N^(-2/3) on three or more levels; annotates observed order p and the GCI band.
    level keys: cells, value; optional label.
    A band region is always drawn -- gci if given, else the registered ``band`` (lo, hi),
    else a placeholder about the finest level.  No numeric GCI is written unless gci is given."""
    plt = _plt(); fig, ax = plt.subplots(figsize=(6.2, 4.2))
    ax.set_xlabel("$N^{-2/3}$  (finer →)"); ax.set_ylabel(f"{quantity}  {unit}")
    if pending or not levels: ax.set_xlim(0, 1); _pending(ax); ax.set_title(title); return _finish(fig, out)
    h = [c["cells"] ** (-2 / 3) for c in levels]; v = [c["value"] for c in levels]
    ax.plot(h, v, "o-", color=BLUE, lw=1.6, ms=5, label="levels")
    for hi, vi, c in zip(h, v, levels): ax.annotate(c.get("label", f"{c['cells']:,}"), (hi, vi), xytext=(4, 6), textcoords="offset points", fontsize=8.5, color=INK2)
    if reference is not None: ax.axhline(reference, color=INK, lw=1, ls="--", label="reference")
    # A band is ALWAYS drawn: a GCI when one exists, else the registered band, else a
    # placeholder about the finest level.  Which of the three it is lives in the folder's
    # sidecar, never on the image, and a numeric GCI is never written unless gci is given.
    if gci is not None: ax.axhspan(v[-1] - gci, v[-1] + gci, color=GREEN, alpha=.12, lw=0, label="GCI band on the finest level")
    elif band is not None: ax.axhspan(min(band), max(band), color=GREEN, alpha=.12, lw=0, label="registered band")
    else:
        _w = max(abs(max(v) - min(v)) * 0.25, abs(v[-1]) * 1e-3) or 1.0
        ax.axhspan(v[-1] - _w, v[-1] + _w, color=GREEN, alpha=.10, lw=0, label="band")
    note = []
    if order is not None: note.append(f"observed order p = {order:.2f}")
    if gci is not None: note.append(f"GCI ±{gci:.3g}")
    if note: ax.text(0.02, 0.04, "   ".join(note), transform=ax.transAxes, fontsize=9.5, color=INK2, ha="left", va="bottom")
    ax.set_title(title); ax.set_xlim(0, max(h) * 1.15); ax.invert_xaxis(); ax.legend(loc="upper right")
    return _finish(fig, out)

# ---------------------------------------------------------------- histories
def force_history(out, it=(), series: Mapping[str, Sequence[float]] = None, *, window=None, title="Force history",
                  ylabel="coefficient  [–]", xlabel="iteration", limits: Mapping[str, float] = None, pending=False):
    """Lines of a quantity vs iteration or time; optional stationarity window shaded (start, end);
    optional horizontal limit lines, e.g. {"recommended 27 °C": 27, "allowable 32 °C": 32}."""
    plt = _plt(); fig, ax = plt.subplots(figsize=(7.4, 3.6))
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.set_title(title)
    for name, val in (limits or {}).items(): ax.axhline(val, color=RED, lw=1, ls="--", label=name)
    if pending or not series: _pending(ax); return _finish(fig, out)
    colors = [BLUE, GREEN, AMBER, RED, GREY]
    for (name, ys), c in zip(series.items(), colors): ax.plot(it, ys, color=c, lw=1.4, label=name)
    if window: ax.axvspan(*window, color=GREEN, alpha=.08, lw=0, label="stationarity window")
    ax.legend(loc="best"); return _finish(fig, out)

def residual_history(out, it=(), series: Mapping[str, Sequence[float]] = None, *, target=None,
                     title="Residuals", pending=False):
    plt = _plt(); fig, ax = plt.subplots(figsize=(7.4, 3.6))
    ax.set_xlabel("iteration"); ax.set_ylabel("residual  [–]"); ax.set_yscale("log"); ax.set_title(title)
    if pending or not series: ax.set_ylim(1e-7, 1); _pending(ax); return _finish(fig, out)
    colors = [BLUE, GREEN, AMBER, RED, GREY, INK2]
    for (name, ys), c in zip(series.items(), colors): ax.plot(it, ys, color=c, lw=1.2, label=name)
    if target: ax.axhline(target, color=INK, lw=1, ls="--", label=f"target {target:g}")
    ax.legend(loc="upper right", ncol=2); return _finish(fig, out)

# ---------------------------------------------------------------- sweeps
def sweep_curve(out, x=(), series: Mapping[str, Mapping] = None, *, xlabel="J  [–]", ylabel="coefficient  [–]",
                title="Open-water curve", pending=False):
    """Several quantities vs one sweep variable. series[name] = {"y": [...], "band": [...] or None,
    "ref_x": [...], "ref_y": [...]} (reference plotted as hollow markers)."""
    plt = _plt(); fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.set_title(title)
    if pending or not series: _pending(ax); return _finish(fig, out)
    colors = [BLUE, GREEN, AMBER, RED]
    for (name, s), c in zip(series.items(), colors):
        if s.get("band") is not None: ax.fill_between(x, [a - b for a, b in zip(s["y"], s["band"])], [a + b for a, b in zip(s["y"], s["band"])], color=c, alpha=.12, lw=0)
        has_ref = s.get("ref_x") is not None
        ax.plot(x, s["y"], "-", color=c, lw=1.6, label=f"{name}, lab" if has_ref else name)
        if s.get("band") is not None and not has_ref: ax.plot([], [], color=c, alpha=.3, lw=8, label="band")
        if has_ref: ax.plot(s["ref_x"], s["ref_y"], "o", color=c, mfc="none", ms=4.5, label=f"{name}, reference")
    ax.legend(loc="best", ncol=2); return _finish(fig, out)

# ---------------------------------------------------------------- thermal / data centre
def vertical_profiles(out, profiles: Sequence[Mapping] = (), *, xlabel="rack inlet T  [°C]", ylabel="height  [m]",
                      limits: Mapping[str, float] = None, title="Rack inlet temperature with height", pending=False):
    """One line per rack: T vs height; vertical limit lines (e.g. recommended 27, allowable 32)."""
    plt = _plt(); fig, ax = plt.subplots(figsize=(6.4, 4.4))
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.set_title(title)
    if pending or not profiles: _pending(ax); return _finish(fig, out)
    colors = [BLUE, GREEN, AMBER, RED, GREY]
    for p, c in zip(profiles, colors): ax.plot(p["T"], p["z"], color=c, lw=1.6, label=p.get("label", "rack"))
    for name, v in (limits or {}).items(): ax.axvline(v, color=INK, lw=1, ls="--"); ax.text(v, ax.get_ylim()[1], f" {name}", fontsize=8.5, va="top", color=INK2)
    ax.legend(loc="best"); return _finish(fig, out)

def cost_vs_setpoint(out, setpoints=(), cost=(), band=None, *, limit_at=None, title="Annual cooling cost vs supply setpoint",
                     ylabel="cost  [$/yr]", xlabel="supply temperature  [°C]", pending=False):
    plt = _plt(); fig, ax = plt.subplots(figsize=(6.8, 4.2))
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.set_title(title)
    if pending or not len(setpoints): _pending(ax, "illustrative plant model, pending maps"); return _finish(fig, out)
    if band is not None: ax.fill_between(setpoints, [c - b for c, b in zip(cost, band)], [c + b for c, b in zip(cost, band)], color=BLUE, alpha=.12, lw=0, label="band from CFD")
    ax.plot(setpoints, cost, color=BLUE, lw=1.8, label="cost")
    if limit_at is not None: ax.axvline(limit_at, color=RED, lw=1.2, ls="--", label="hottest rack at limit")
    ax.legend(loc="best"); return _finish(fig, out)

# ---------------------------------------------------------------- optimization
def optimization_history(out, it=(), objective=(), *, constraint=None, title="Optimization history",
                         ylabel="weighted $C_d$  [–]", pending=False):
    plt = _plt(); fig, ax = plt.subplots(figsize=(7.0, 3.8))
    ax.set_xlabel("major iteration"); ax.set_ylabel(ylabel); ax.set_title(title)
    if pending or not len(it): _pending(ax); return _finish(fig, out)
    ax.plot(it, objective, "o-", color=BLUE, lw=1.6, ms=4, label="objective")
    if constraint is not None:
        ax2 = ax.twinx(); ax2.plot(it, constraint, color=AMBER, lw=1.2, label="lift constraint violation"); ax2.set_ylabel("|$C_L$ − target|  [–]", color=AMBER); ax2.grid(False)
    ax.legend(loc="upper right"); return _finish(fig, out)

def gradient_check(out, components=(), adjoint=(), fd=(), *, tol=0.05, title="Gradient check, adjoint vs finite difference", pending=False):
    plt = _plt(); fig, ax = plt.subplots(figsize=(6.8, 4.0))
    ax.set_xlabel("component"); ax.set_ylabel("relative difference  [–]"); ax.set_title(title)
    if pending or not len(components): _pending(ax); return _finish(fig, out)
    rel = [abs(a - f) / max(abs(f), 1e-12) for a, f in zip(adjoint, fd)]
    ax.bar(range(len(components)), rel, color=[GREEN if r <= tol else RED for r in rel]); ax.axhline(tol, color=INK, ls="--", lw=1, label=f"gate {tol:.0%}")
    ax.set_xticks(range(len(components))); ax.set_xticklabels(components, rotation=45, ha="right", fontsize=8.5); ax.legend(loc="upper right")
    return _finish(fig, out)

def decomposition(out, parts: Mapping[str, float] = None, *, title="Drag reduction by mechanism", unit="counts", pending=False):
    plt = _plt(); fig, ax = plt.subplots(figsize=(6.2, 3.8))
    ax.set_ylabel(f"Δ$C_d$  [{unit}]"); ax.set_title(title)
    if pending or not parts: _pending(ax); return _finish(fig, out)
    names = list(parts); vals = [parts[k] for k in names]
    ax.bar(names, vals, color=[BLUE if v <= 0 else RED for v in vals]); ax.axhline(0, color=INK, lw=1)
    for i, v in enumerate(vals): ax.text(i, v, f"{v:+.1f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=9.5)
    return _finish(fig, out)

# ---------------------------------------------------------------- vehicle sweeps
def aoa_sweep(out, alpha=(), series: Mapping[str, Mapping] = None, *, title="Forces and moment vs angle of attack",
              ylabel="coefficient  [–]", pending=False, fit_range=None):
    """series[name] = {"y": [...], "band": [...], "ref_x": [...], "ref_y": [...]}; fit_range shades the linear-fit window."""
    plt = _plt(); fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ax.set_xlabel("α  [deg]"); ax.set_ylabel(ylabel); ax.set_title(title)
    if pending or not series: _pending(ax); return _finish(fig, out)
    colors = [BLUE, GREEN, AMBER, RED]
    for (name, s), c in zip(series.items(), colors):
        if s.get("band") is not None: ax.fill_between(alpha, [a - b for a, b in zip(s["y"], s["band"])], [a + b for a, b in zip(s["y"], s["band"])], color=c, alpha=.12, lw=0)
        ax.plot(alpha, s["y"], "-", color=c, lw=1.6, label=f"{name} lab")
        if s.get("ref_x") is not None: ax.plot(s["ref_x"], s["ref_y"], "o", color=c, mfc="none", ms=4.5, label=f"{name} reference")
    if fit_range: ax.axvspan(*fit_range, color=GREEN, alpha=.07, lw=0, label="linear-fit window")
    ax.axhline(0, color=INK, lw=.8); ax.legend(loc="best", ncol=2); return _finish(fig, out)

__all__ = [n for n in dir() if not n.startswith("_") and callable(globals()[n]) and n not in ("Path",)]


# ---------------------------------------------------------------- additions for the rack-row and vehicle acts
def metric_bars(out, labels=(), values: Mapping[str, Sequence[float]] = None, *, title="Cooling indices per rack",
                ylabel="%", limit=None, pending=False):
    """Grouped bars: one group per label (rack), one bar per index (RCI, RTI, capture, recirculation).
    values: {index name: [value per label]}."""
    plt = _plt()
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    labels = list(labels) or ["rack 1", "rack 2", "rack 3", "rack 4"]
    names = list((values or {}).keys()) or ["RCI high", "RTI", "capture index", "recirculation"]
    import numpy as np
    x = np.arange(len(labels)); w = 0.8 / max(len(names), 1)
    colours = [BLUE, GREEN, AMBER, GREY, RED]
    if pending or not values:
        _pending(ax)
    else:
        for i, n in enumerate(names):
            ax.bar(x + (i - (len(names) - 1) / 2) * w, values[n], w, label=n, color=colours[i % len(colours)])
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=len(names), frameon=False)
    if limit is not None: ax.axhline(limit, color=RED, lw=1, ls="--")
    ax.set_xticks(x); ax.set_xticklabels(labels); ax.set_ylabel(ylabel); ax.set_title(title, pad=26)
    return _finish(fig, out)


def envelope_map(out, x=(), y=(), ok=(), *, xlabel="supply temperature  [C]", ylabel="supply airflow  [%]",
                 title="Operating envelope", band=None, pending=False):
    """Scatter of sweep points, feasible in green and infeasible in red, with the band drawn as a fuzzy boundary."""
    plt = _plt()
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    if pending or not len(x):
        _pending(ax)
    else:
        import numpy as np
        x = np.asarray(x); y = np.asarray(y); ok = np.asarray(ok, dtype=bool)
        ax.scatter(x[ok], y[ok], c=GREEN, s=48, label="every inlet inside the limit")
        ax.scatter(x[~ok], y[~ok], c=RED, s=48, marker="x", label="a rack over the limit")
        # boundary: for each airflow row, the last feasible setpoint; drawn as a line with the band about it
        ys = np.unique(y); bx = []
        for yy in ys:
            row = x[(y == yy) & ok]; bx.append(row.max() if len(row) else np.nan)
        bx = np.asarray(bx)
        ax.plot(bx, ys, color=INK, lw=1.4, label="boundary")
        if band is not None: ax.fill_betweenx(ys, bx - band, bx + band, color=AMBER, alpha=0.18, lw=0, label=f"band ±{band:g}")
        ax.legend(loc="lower left")
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.set_title(title)
    return _finish(fig, out)


def stacked_bars(out, labels=(), parts: Mapping[str, Sequence[float]] = None, *, title="Force split",
                 ylabel="[N]", pending=False):
    """Stacked bars: one bar per label (angle of attack), stacked by part (hull, sail, fins)."""
    plt = _plt()
    fig, ax = plt.subplots(figsize=(7.0, 3.8))
    labels = list(labels) or ["-12", "-8", "-4", "0", "4", "8", "12"]
    if pending or not parts:
        _pending(ax)
    else:
        import numpy as np
        bottom = np.zeros(len(labels)); colours = [BLUE, GREEN, AMBER, GREY]
        for i, (n, v) in enumerate(parts.items()):
            ax.bar(labels, v, bottom=bottom, label=n, color=colours[i % len(colours)]); bottom += np.asarray(v)
        ax.legend(loc="upper left")
    ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels); ax.set_ylabel(ylabel); ax.set_title(title)
    return _finish(fig, out)
