"""ACT PLOT LIBRARY, math-only edition.

Every axis label, legend entry and annotation is a mathematical symbol set in mathtext;
no English prose reaches an image. Titles are never drawn: the act carries the caption.
No verdict word and no band annotation in words: a band is a shaded region labelled by
its half-width, a limit is a dashed line labelled by its symbol and value.

Callers may still pass English labels (the build scripts do); :func:`sym` maps them to
symbols by rule, and anything it cannot map is dropped from the legend rather than
printed in English.

Functions (signatures kept from the previous edition):
    cp_stations, grid_family, force_history, residual_history, sweep_curve,
    vertical_profiles, cost_vs_setpoint, optimization_history, gradient_check,
    decomposition, aoa_sweep, metric_bars, envelope_map, stacked_bars
Every function returns the Path it wrote. ``pending=True`` draws the same axes with a
quiet mark instead of data.
"""
from __future__ import annotations
import re
from pathlib import Path
from typing import Mapping, Sequence

INK = "#182233"; INK2 = "#4A5568"; RULE = "#CBD3DC"; PAPER = "#FFFFFF"
GREEN = "#1F7A5C"; BLUE = "#2B5FB3"; AMBER = "#B7791F"; RED = "#B42318"; GREY = "#8A94A6"; VIOLET = "#7C5CBF"
PALETTE = [BLUE, GREEN, AMBER, RED, VIOLET, GREY]
DEG = r"^{\circ}\mathrm{C}"


def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.facecolor": PAPER, "axes.facecolor": PAPER, "savefig.facecolor": PAPER,
        "axes.edgecolor": RULE, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
        "text.color": INK, "axes.grid": True, "grid.color": "#EEF1F4", "grid.linewidth": 0.8,
        "font.family": "DejaVu Sans", "font.size": 11, "axes.labelsize": 12.5,
        "legend.frameon": False, "legend.fontsize": 10.5,
        "axes.spines.top": False, "axes.spines.right": False, "mathtext.fontset": "dejavusans",
    })
    return plt


def _finish(fig, out: Path, dpi=160) -> Path:
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(); fig.savefig(out, dpi=dpi)
    import matplotlib.pyplot as plt; plt.close(fig)
    return out


def _pending(ax):
    ax.text(0.5, 0.5, r"$\cdots$", transform=ax.transAxes, ha="center", va="center", fontsize=30, color=GREY)


# ---------------------------------------------------------------- symbol mapping
_UNIT = {"°c": DEG, "degc": DEG, "c": DEG, "k": r"\mathrm{K}", "m": r"\mathrm{m}", "s": r"\mathrm{s}",
         "m/s": r"\mathrm{m\,s^{-1}}", "m2/s2": r"\mathrm{m^2\,s^{-2}}", "m²/s²": r"\mathrm{m^2\,s^{-2}}",
         "m3": r"\mathrm{m^3}", "m³": r"\mathrm{m^3}", "%": r"\%", "percent": r"\%", "–": "-", "-": "-", "1": "-", "n": r"\mathrm{N}"}

_RULES = [  # (regex on the lowercased label, symbol); first match wins
    (r"iteration", r"$n$"),
    (r"^time\b|\btime\s*\[", r"$t$"),
    (r"x\s*/\s*c", r"$x/c$"),
    (r"^eta|η", r"$\eta$"),
    (r"n\^?\{?-?2/3|finer", r"$N^{-2/3}$"),
    (r"residual", r"$r$"),
    (r"^coefficient", r"$C$"),
    (r"hottest inlet|inlet.*max", r"$T_{\mathrm{in,max}}$"),
    (r"rack inlet t|inlet temperature", r"$T_{\mathrm{in}}$"),
    (r"supply temperature|setpoint|supply t\b", r"$T_{\mathrm{sup}}$"),
    (r"supply airflow|airflow", r"$\dot V/\dot V_0$"),
    (r"^height", r"$z$"),
    (r"pressure drop", r"$\Delta p$"),
    (r"volume above", r"$V_{T>T_{\lim}}$"),
    (r"relative cost|^cost", r"$\mathcal{C}/\mathcal{C}_0$"),
    (r"^j\b|advance ratio", r"$J$"),
    (r"angle of attack|^alpha", r"$\alpha$"),
    (r"drag reduction|counts", r"$\Delta C_D$"),
    (r"objective", r"$f$"),
    (r"^percent$|^%$", r"$[\%]$"),
    (r"stationarity window|^window", r"$n\in\Delta n$"),
    (r"tunnel|experiment|\bexp\b|\btum\b", r"$\mathrm{exp}$"),
    (r"\blab\b|\bcfd\b|\bours\b|\bour\b", r"$\mathrm{CFD}$"),
    (r"^levels?$", r"$N$"),
    (r"gci", r"$\pm\,\mathrm{GCI}$"),
    (r"registered band|published band|band from cfd|^band", r"$\pm$"),
    (r"^reference", r"$\mathrm{ref}$"),
    (r"\broom\b|3[- ]?d", r"$3\mathrm{D}$"),
    (r"\bslice\b|2[- ]?d", r"$2\mathrm{D}$"),
    (r"rci", r"$\mathrm{RCI}$"),
    (r"rti", r"$\mathrm{RTI}$"),
    (r"capture", r"$\mathrm{CI}$"),
    (r"recirc", r"$f_{\mathrm{rec}}$"),
    (r"every inlet inside|inside the limit", r"$T_{\mathrm{in,max}}\le T_{\lim}$"),
    (r"over the limit|infeasible", r"$T_{\mathrm{in,max}}>T_{\lim}$"),
    (r"boundary", r"$T_{\mathrm{in,max}}=T_{\lim}$"),
    (r"limit|recommended|allowable", r"$T_{\lim}$"),
    (r"cold aisle", r"$T_{\mathrm{in}}$"),
    (r"hot aisle", r"$T_{\mathrm{out}}$"),
    (r"adjoint", r"$\partial f/\partial x\ \mathrm{adj}$"),
    (r"finite difference|\bfd\b", r"$\partial f/\partial x\ \mathrm{FD}$"),
    (r"^shape", r"$\Delta C_D^{\mathrm{shape}}$"), (r"^twist", r"$\Delta C_D^{\mathrm{twist}}$"), (r"^trim", r"$\Delta C_D^{\mathrm{trim}}$"),
    (r"^hull", r"$F^{\mathrm{hull}}$"), (r"^sail", r"$F^{\mathrm{sail}}$"), (r"^fin", r"$F^{\mathrm{fin}}$"),
]


def _unit_of(label: str) -> str:
    m = re.search(r"\[([^\]]+)\]", label)
    if not m: return ""
    u = m.group(1).strip()
    return _UNIT.get(u.lower(), _UNIT.get(u, r"\mathrm{%s}" % u))


def _value_in(label: str):
    m = re.search(r"(-?\d+\.\d+(?:e[+-]?\d+)?|-?\d+e[+-]?\d+)", label)
    return m.group(1) if m else None


def _fmt(v) -> str:
    x = float(v)
    if abs(x) >= 1e4 or (abs(x) < 1e-2 and x != 0): return "%.3g" % x
    return "%.4g" % x


def _with_unit(base: str, label: str, with_unit: bool) -> str:
    u = _unit_of(label) if with_unit else ""
    return base[:-1] + (r"\ \ [%s]$" % u) if (u and base.endswith("$")) else base


def sym(label, ysym: str | None = None, with_unit=True) -> str | None:
    """English label -> math symbol. None when nothing sensible exists (the caller drops it)."""
    if label is None: return None
    s = str(label).strip()
    if not s: return None
    if s.startswith("$") and s.endswith("$"): return s
    low = s.lower()
    m = re.match(r"^rack\s*(\d+)$", low)
    if m: return r"$R_{%s}$" % m.group(1)
    value = _value_in(s)
    # a reference or limit line named in English with a number
    if ysym and value and re.search(r"endpoint|window mean|shipped|\bmean\b|experiment|tunnel|\btum\b|published|reference", low):
        tag = "exp" if re.search(r"experiment|tunnel|\btum\b", low) else ("ref,fine" if "fine" in low else "ref")
        core = ysym.strip("$")
        core = (r"\overline{%s}" % core) if re.search(r"mean", low) else core
        return r"$%s^{\,\mathrm{%s}}=%s$" % (core, tag, _fmt(value))
    if value and re.search(r"limit|recommended|allowable", low):
        return r"$T_{\lim}=%s\,%s$" % (_fmt(value), DEG)
    for pat, symbol in _RULES:
        if re.search(pat, low):
            if symbol == r"$\pm$" and value: return r"$\pm %s$" % _fmt(value)
            return _with_unit(symbol, s, with_unit)
    if value and ysym: return r"$%s^{\,\mathrm{ref}}=%s$" % (ysym.strip("$"), _fmt(value))
    u = _unit_of(s)
    return (r"$[%s]$" % u) if u else None


def _ysym_from(label: str) -> str:
    m = re.search(r"\$[^$]+\$", str(label or ""))
    return m.group(0) if m else r"$y$"


def _axis(label, default: str) -> str:
    """Axis label as symbol with unit; a math label is kept, an English one is mapped."""
    if label is None: return default
    s = str(label)
    if s.strip().startswith("$"):
        m = re.match(r"^\s*(\$[^$]+\$)\s*(\[[^\]]+\])?", s)
        if m and m.group(2): return _with_unit(m.group(1), m.group(2), True)
        return m.group(1) if m else default
    return sym(s) or default


def _legend(ax, **kw):
    handles, labels = ax.get_legend_handles_labels()
    keep = [(h, l) for h, l in zip(handles, labels) if l and not l.startswith("_")]
    if keep: ax.legend([h for h, _ in keep], [l for _, l in keep], **kw)


# ---------------------------------------------------------------- aero: Cp at stations
def cp_stations(out, stations: Sequence[Mapping] = (), *, title=None, band: float | None = None, pending=False, ncols=3):
    plt = _plt()
    n = max(len(stations), 6 if pending else 1); rows = -(-n // ncols)
    fig, axes = plt.subplots(rows, ncols, figsize=(11.5, 3.4 * rows), sharey=True)
    axes = axes.ravel() if hasattr(axes, "ravel") else [axes]
    for k, ax in enumerate(axes):
        ax.set_xlabel(r"$x/c$")
        if k % ncols == 0: ax.set_ylabel(r"$C_p$")
        if pending or k >= len(stations):
            ax.set_title(r"$\eta=\cdots$", loc="left", fontsize=11); ax.set_xlim(0, 1); ax.set_ylim(1.2, -1.6); _pending(ax); continue
        s = stations[k]; ax.set_title(r"$\eta=%.2f$" % s["eta"], loc="left", fontsize=11)
        if band: ax.fill_between(s["xc"], [c - band for c in s["cp_cfd"]], [c + band for c in s["cp_cfd"]], color=BLUE, alpha=.10, lw=0, label=r"$\pm %g$" % band)
        ax.plot(s["xc"], s["cp_cfd"], color=BLUE, lw=1.6, label=r"$C_p$")
        if s.get("xc_exp") is not None: ax.plot(s["xc_exp"], s["cp_exp"], "o", ms=3.4, color=INK, mfc="none", label=r"$C_p^{\,\mathrm{exp}}$")
        lo = min(min(s["cp_cfd"]), min(s.get("cp_exp") or [0])); ax.set_ylim(1.2, min(-1.6, lo - 0.1))
        if k == 0: _legend(ax, loc="lower right")
    return _finish(fig, out)


# ---------------------------------------------------------------- grid family / observed order
def grid_family(out, levels: Sequence[Mapping] = (), *, quantity="$C_D$", unit="", order=None, gci=None, title=None,
                reference=None, band=None, pending=False):
    plt = _plt(); fig, ax = plt.subplots(figsize=(6.4, 4.4))
    q = quantity if str(quantity).startswith("$") else (sym(quantity, with_unit=False) or r"$y$")
    ax.set_xlabel(r"$N^{-2/3}$"); ax.set_ylabel(_with_unit(q, "[%s]" % unit if unit else "", bool(unit)))
    if pending or not levels: ax.set_xlim(0, 1); _pending(ax); return _finish(fig, out)
    h = [c["cells"] ** (-2 / 3) for c in levels]; v = [c["value"] for c in levels]
    ax.plot(h, v, "o-", color=BLUE, lw=1.6, ms=5.5, label=q)
    for hi, vi, c in zip(h, v, levels):
        ax.annotate(r"$N=%s$" % _fmt(c["cells"]), (hi, vi), xytext=(5, 6), textcoords="offset points", fontsize=9.5, color=INK2)
    if reference is not None: ax.axhline(reference, color=INK, lw=1, ls="--", label=q[:-1] + r"^{\,\mathrm{exp}}=%s$" % _fmt(reference))
    if band is not None: ax.axhspan(band[0], band[1], color=GREEN, alpha=.12, lw=0, label=r"$[%s,\ %s]$" % (_fmt(band[0]), _fmt(band[1])))
    if gci is not None: ax.axhspan(v[-1] - gci, v[-1] + gci, color=GREEN, alpha=.12, lw=0, label=r"$\pm\,\mathrm{GCI}$")
    note = []
    if order is not None: note.append(r"$p=%.2f$" % order)
    if gci is not None: note.append(r"$\mathrm{GCI}=%s$" % _fmt(gci))
    if note: ax.text(0.02, 0.04, "   ".join(note), transform=ax.transAxes, fontsize=11, color=INK2, ha="left", va="bottom")
    ax.set_xlim(0, max(h) * 1.15); ax.invert_xaxis(); _legend(ax, loc="upper right")
    return _finish(fig, out)


# ---------------------------------------------------------------- histories
def force_history(out, it=(), series: Mapping[str, Sequence[float]] = None, *, window=None, title=None,
                  ylabel="$C$", xlabel="iteration", limits: Mapping[str, float] = None, window_mean=False, pending=False):
    """window_mean=True draws the mean of the first series over the window as a solid line labelled with its value."""
    plt = _plt(); fig, ax = plt.subplots(figsize=(7.6, 3.8))
    ys = _ysym_from(ylabel) if "$" in str(ylabel) else (sym(ylabel, with_unit=False) or r"$y$")
    ax.set_xlabel(_axis(xlabel, r"$n$")); ax.set_ylabel(_axis(ylabel, ys))
    if pending or not series: _pending(ax); return _finish(fig, out)
    for (name, vals), c in zip(series.items(), PALETTE): ax.plot(it, vals, color=c, lw=1.4, label=sym(name, ys, with_unit=False) or "_")
    if window and window_mean:
        import numpy as np
        first = list(series.values())[0]; iv = np.asarray(it, dtype=float); vv = np.asarray(first, dtype=float)
        sel = (iv >= window[0]) & (iv <= window[1]); mval = float(np.nanmean(vv[sel])) if sel.any() else float("nan")
        ax.axhline(mval, color=BLUE, lw=1.2, label=r"$\overline{%s}=%s$" % (ys.strip("$"), _fmt(mval)))
    for name, val in (limits or {}).items():
        ax.axhline(val, color=RED, lw=1, ls="--", label=sym(name, ys, with_unit=False) or r"$%s=%s$" % (ys.strip("$"), _fmt(val)))
    if window: ax.axvspan(*window, color=GREEN, alpha=.08, lw=0, label=r"$n\in[%s,\,%s]$" % (_fmt(window[0]), _fmt(window[1])))
    _legend(ax, loc="best"); return _finish(fig, out)


def residual_history(out, it=(), series: Mapping[str, Sequence[float]] = None, *, target=None, title=None, pending=False,
                     xlim=None, ylim=None):
    """xlim/ylim pin the axes so a SERIES of frames cut at 10, 25, 50, 75 and 100 % of a
    run can be stepped through and the curves are seen to descend. Without them each
    frame autoscales to its own data and the descent is invisible: every frame looks
    the same and the last decade of the run looks like the first."""
    plt = _plt(); fig, ax = plt.subplots(figsize=(7.6, 3.8))
    ax.set_xlabel(r"$n$"); ax.set_ylabel(r"$r$"); ax.set_yscale("log")
    if xlim: ax.set_xlim(*xlim)
    if ylim: ax.set_ylim(*ylim)
    if pending or not series: ax.set_ylim(1e-7, 1); _pending(ax); return _finish(fig, out)
    for (name, vals), c in zip(series.items(), PALETTE): ax.plot(it, vals, color=c, lw=1.2, label=sym(name, with_unit=False) or "_")
    if target: ax.axhline(target, color=INK, lw=1, ls="--", label=r"$r_{\mathrm{target}}=%s$" % _fmt(target))
    if xlim: ax.set_xlim(*xlim)
    if ylim: ax.set_ylim(*ylim)
    _legend(ax, loc="upper right", ncol=2); return _finish(fig, out)


# ---------------------------------------------------------------- sweeps
def sweep_curve(out, x=(), series: Mapping[str, Mapping] = None, *, xlabel="$J$", ylabel="$C$", title=None, pending=False,
                limits: Mapping[str, float] = None):
    plt = _plt(); fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ys = _ysym_from(ylabel) if "$" in str(ylabel) else (sym(ylabel, with_unit=False) or r"$y$")
    ax.set_xlabel(_axis(xlabel, r"$x$")); ax.set_ylabel(_axis(ylabel, ys))
    if pending or not series: _pending(ax); return _finish(fig, out)
    for (name, s), c in zip(series.items(), PALETTE):
        label = sym(name, ys, with_unit=False) or ys
        if s.get("band") is not None:
            ax.fill_between(x, [a - b for a, b in zip(s["y"], s["band"])], [a + b for a, b in zip(s["y"], s["band"])], color=c, alpha=.12, lw=0, label=r"$\pm$")
        ax.plot(x, s["y"], "-", color=c, lw=1.6, label=label)
        if s.get("ref_x") is not None: ax.plot(s["ref_x"], s["ref_y"], "o", color=c, mfc="none", ms=4.5, label=label[:-1] + r"^{\,\mathrm{exp}}$")
    for name, val in (limits or {}).items(): ax.axhline(val, color=RED, lw=1, ls="--", label=sym(name, ys, with_unit=False))
    _legend(ax, loc="best", ncol=2); return _finish(fig, out)


# ---------------------------------------------------------------- thermal / data centre
def vertical_profiles(out, profiles: Sequence[Mapping] = (), *, xlabel=None, ylabel=None, limits: Mapping[str, float] = None,
                      title=None, pending=False):
    plt = _plt(); fig, ax = plt.subplots(figsize=(6.4, 4.6))
    ax.set_xlabel(r"$T\ \ [%s]$" % DEG); ax.set_ylabel(r"$z\ \ [\mathrm{m}]$")
    if pending or not profiles: _pending(ax); return _finish(fig, out)
    for pr, c in zip(profiles, PALETTE):
        ax.plot(pr["T"], pr["z"], color=c, lw=1.5, label=sym(pr.get("label", ""), "$T$", with_unit=False) or "_")
    for name, val in (limits or {}).items(): ax.axvline(val, color=RED, lw=1, ls="--", label=r"$T_{\lim}=%s\,%s$" % (_fmt(val), DEG))
    _legend(ax, loc="lower right"); return _finish(fig, out)


def cost_vs_setpoint(out, setpoints=(), cost=(), band=None, *, limit_at=None, title=None, ylabel=None, xlabel=None, pending=False):
    plt = _plt(); fig, ax = plt.subplots(figsize=(6.8, 4.2))
    ax.set_xlabel(r"$T_{\mathrm{sup}}\ \ [%s]$" % DEG); ax.set_ylabel(r"$\mathcal{C}/\mathcal{C}_0$")
    if pending or not len(setpoints): _pending(ax); return _finish(fig, out)
    import numpy as np
    sp = np.asarray(setpoints, dtype=float); cs = np.asarray(cost, dtype=float)
    if band is not None:
        b = np.asarray(band, dtype=float); ax.fill_between(sp, cs - b, cs + b, color=BLUE, alpha=.12, lw=0, label=r"$\pm$")
    ax.plot(sp, cs, color=BLUE, lw=1.6, label=r"$\mathcal{C}/\mathcal{C}_0$")
    if limit_at is not None: ax.axvline(limit_at, color=RED, lw=1, ls="--", label=r"$T_{\mathrm{in,max}}=T_{\lim}$")
    _legend(ax, loc="best"); return _finish(fig, out)


def metric_bars(out, labels=(), values: Mapping[str, Sequence[float]] = None, *, title=None, ylabel="[%]", limit=None, pending=False):
    plt = _plt(); fig, ax = plt.subplots(figsize=(7.4, 3.8))
    import numpy as np
    labels = list(labels) or ["rack 1", "rack 2", "rack 3", "rack 4"]
    names = list((values or {}).keys()) or ["RCI", "RTI", "CI", "rec"]
    x = np.arange(len(labels)); w = 0.8 / max(len(names), 1)
    if pending or not values: _pending(ax)
    else:
        for i, n in enumerate(names):
            ax.bar(x + (i - (len(names) - 1) / 2) * w, values[n], w, label=sym(n, with_unit=False) or "_", color=PALETTE[i % len(PALETTE)])
        _legend(ax, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=len(names))
    if limit is not None: ax.axhline(limit, color=RED, lw=1, ls="--")
    ax.set_xticks(x); ax.set_xticklabels([sym(l, with_unit=False) or l for l in labels]); ax.set_ylabel(r"$[\%]$")
    return _finish(fig, out)


def envelope_map(out, x=(), y=(), ok=(), *, xlabel=None, ylabel=None, title=None, band=None, pending=False):
    plt = _plt(); fig, ax = plt.subplots(figsize=(6.4, 4.4))
    ax.set_xlabel(r"$T_{\mathrm{sup}}\ \ [%s]$" % DEG); ax.set_ylabel(r"$\dot V/\dot V_0\ \ [\%]$")
    if pending or not len(x): _pending(ax); return _finish(fig, out)
    import numpy as np
    x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float); ok = np.asarray(ok, dtype=bool)
    ax.scatter(x[ok], y[ok], c=GREEN, s=48, label=r"$T_{\mathrm{in,max}}\le T_{\lim}$")
    ax.scatter(x[~ok], y[~ok], c=RED, s=48, marker="x", label=r"$T_{\mathrm{in,max}}>T_{\lim}$")
    ys = np.unique(y); bx = []
    for yy in ys:
        row = x[(y == yy) & ok]; bx.append(row.max() if len(row) else np.nan)
    bx = np.asarray(bx); ax.plot(bx, ys, color=INK, lw=1.4, label=r"$T_{\mathrm{in,max}}=T_{\lim}$")
    if band is not None: ax.fill_betweenx(ys, bx - band, bx + band, color=AMBER, alpha=0.18, lw=0, label=r"$\pm %g$" % band)
    _legend(ax, loc="lower left"); return _finish(fig, out)


def stacked_bars(out, labels=(), parts: Mapping[str, Sequence[float]] = None, *, title=None, ylabel="$F$", pending=False):
    plt = _plt(); fig, ax = plt.subplots(figsize=(7.0, 3.8))
    labels = list(labels) or ["-12", "-8", "-4", "0", "4", "8", "12"]
    ax.set_xlabel(r"$\alpha\ \ [^{\circ}]$"); ax.set_ylabel(_axis(ylabel, r"$F\ \ [\mathrm{N}]$"))
    if pending or not parts: _pending(ax); return _finish(fig, out)
    import numpy as np
    bottom = np.zeros(len(labels))
    for i, (n, v) in enumerate(parts.items()):
        ax.bar(labels, v, bottom=bottom, label=sym(n, with_unit=False) or "_", color=PALETTE[i % len(PALETTE)]); bottom += np.asarray(v, dtype=float)
    _legend(ax, loc="upper left"); return _finish(fig, out)


# ---------------------------------------------------------------- optimization
def optimization_history(out, it=(), objective=(), *, constraint=None, title=None, pending=False):
    plt = _plt(); fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.set_xlabel(r"$k$"); ax.set_ylabel(r"$f$")
    if pending or not len(it): _pending(ax); return _finish(fig, out)
    ax.plot(it, objective, "o-", color=BLUE, lw=1.4, ms=4, label=r"$f_k$")
    if constraint is not None:
        ax2 = ax.twinx(); ax2.plot(it, constraint, "s--", color=AMBER, lw=1.2, ms=3.5, label=r"$\|g_k\|$"); ax2.set_ylabel(r"$\|g\|$"); ax2.grid(False)
        h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels(); ax.legend(h1 + h2, l1 + l2, loc="upper right")
    else: _legend(ax, loc="upper right")
    return _finish(fig, out)


def gradient_check(out, components=(), adjoint=(), fd=(), *, tol=0.05, title=None, pending=False):
    plt = _plt(); fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.set_xlabel(r"$i$"); ax.set_ylabel(r"$\partial f/\partial x_i$")
    if pending or not len(components): _pending(ax); return _finish(fig, out)
    import numpy as np
    x = np.arange(len(components))
    ax.bar(x - 0.2, adjoint, 0.4, color=BLUE, label=r"$\mathrm{adj}$"); ax.bar(x + 0.2, fd, 0.4, color=AMBER, label=r"$\mathrm{FD}$")
    ax.set_xticks(x); ax.set_xticklabels([sym(c, with_unit=False) or r"$x_{%d}$" % (i + 1) for i, c in enumerate(components)])
    ax.text(0.02, 0.95, r"$|\Delta|\le %g$" % tol, transform=ax.transAxes, va="top", color=INK2)
    _legend(ax, loc="upper right"); return _finish(fig, out)


def decomposition(out, parts: Mapping[str, float] = None, *, title=None, unit="counts", pending=False):
    plt = _plt(); fig, ax = plt.subplots(figsize=(6.0, 3.8))
    ax.set_ylabel(r"$\Delta C_D\ \ [10^{-4}]$")
    if pending or not parts: _pending(ax); return _finish(fig, out)
    names = list(parts.keys()); vals = list(parts.values())
    ax.bar([sym(n, with_unit=False) or n for n in names], vals, color=[PALETTE[i % len(PALETTE)] for i in range(len(names))])
    ax.axhline(0, color=INK, lw=0.8); return _finish(fig, out)


def aoa_sweep(out, alpha=(), series: Mapping[str, Mapping] = None, *, title=None, pending=False):
    plt = _plt(); fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.set_xlabel(r"$\alpha\ \ [^{\circ}]$"); ax.set_ylabel(r"$C$")
    if pending or not series: _pending(ax); return _finish(fig, out)
    for (name, s), c in zip(series.items(), PALETTE):
        label = sym(name, with_unit=False) or name
        if s.get("band") is not None: ax.fill_between(alpha, [a - b for a, b in zip(s["y"], s["band"])], [a + b for a, b in zip(s["y"], s["band"])], color=c, alpha=.12, lw=0)
        ax.plot(alpha, s["y"], "-", color=c, lw=1.6, label=label)
        if s.get("ref_x") is not None: ax.plot(s["ref_x"], s["ref_y"], "o", color=c, mfc="none", ms=4.5, label=label[:-1] + r"^{\,\mathrm{exp}}$")
    _legend(ax, loc="best", ncol=2); return _finish(fig, out)
