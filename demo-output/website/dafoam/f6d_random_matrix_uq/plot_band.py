"""F6d -- figure: the random-matrix probabilistic band against the LES
reference, the kOmegaSST baseline, and the eigenspace corner union, plus the
station velocity profiles.  Reads only aggregate_result.json and the member
cases; computes nothing new."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import analyse  # noqa: E402

INK = "#22303f"
MUTED = "#7a8b99"
ACCENT = {"d0.2": "#2f6f9f", "d0.6": "#b8562f"}
LES_C = "#1d7a52"

res = json.loads((HERE / "aggregate_result.json").read_text())


def panel_reattachment(ax):
    les = res["les_reference"]["reattachment_x_over_h_range"]
    ax.axvspan(les[0], les[1], color=LES_C, alpha=0.18, zorder=0)
    ax.axvline(np.mean(les), color=LES_C, lw=1.6, zorder=1)
    ax.text(les[0], 1.11, "LES 4.6-4.7", color=LES_C, ha="right",
            va="bottom", transform=ax.get_xaxis_transform(), fontsize=9)

    base = res["baseline"]["reattachment_x_over_h"]
    ax.axvline(base, color=INK, lw=1.6, ls="--", zorder=1)
    ax.text(base, 1.11, f"kOmegaSST baseline {base:.2f}", color=INK,
            ha="right", va="bottom", transform=ax.get_xaxis_transform(), fontsize=9)

    rows, labels = [], []
    y = 0
    for key in ("d0.2", "d0.6"):
        rm = res.get("random_matrix", {}).get(key)
        if not rm or "reattachment" not in rm.get("all_admitted", {}):
            continue
        xs = np.array([m["reattachment"] for m in rm["members"]])
        r = rm["all_admitted"]["reattachment"]
        ax.scatter(xs, np.full_like(xs, y), s=17, color=ACCENT[key], alpha=0.5,
                   zorder=3, edgecolors="none")
        ax.plot([r["p05"], r["p95"]], [y, y], color=ACCENT[key], lw=5, zorder=2,
                solid_capstyle="butt", alpha=0.75)
        ax.plot([r["min"], r["max"]], [y, y], color=ACCENT[key], lw=1.2, zorder=2)
        ax.scatter([r["p50"]], [y], marker="|", s=300, color=ACCENT[key], zorder=4,
                   linewidths=2.2)
        labels.append(f"random matrix  $\\delta$ = {key[1:]}   (n = {rm['n_admitted']},"
                      f" bar = 5-95%)")
        rows.append(y)
        y -= 1

    # the corner union in the corner method's OWN live-turbulence-model form
    live = res.get("live_model_runs", {})
    pts = [(n.replace("live_", ""), v["reattachment"])
           for n, v in live.items()
           if n.startswith("live_") and v.get("reattachment") is not None
           and v.get("n_reversed_regions", 99) <= 2]
    if pts:
        xs = [p[1] for p in pts]
        ax.plot([min(xs), max(xs)], [y, y], color=MUTED, lw=5,
                solid_capstyle="butt", zorder=2)
        ax.scatter(xs, np.full(len(xs), y), s=42, color=INK, zorder=4, marker="D")
        for n_, x_ in pts:
            ax.annotate(n_, (x_, y), textcoords="offset points",
                        xytext=(0, -15), ha="center", fontsize=8, color=INK)
        labels.append("eigenspace corners (live model, corrected sign)")
        rows.append(y)
        y -= 1

    ax.set_yticks(rows)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_ylim(y + 0.6, 0.9)
    ax.set_xlabel("reattachment  $x/h$")
    ax.set_title("Reattachment: probabilistic band vs corner union vs LES\n"
                 "(3C omitted from the corner union: its wall trace fragments)",
                 fontsize=10.5, color=INK, loc="left", pad=26)
    ax.grid(axis="x", color="#dde3e8", lw=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)


def panel_profiles(axes):
    """Ux profiles at four stations: ensemble spread, baseline, LES."""
    f = analyse.les_interp()
    stations = [1, 3, 5, 7]
    base = analyse.station_profiles(analyse.CASE, 10000)
    for ax, st in zip(axes, stations):
        for key in ("d0.2", "d0.6"):
            rm = res.get("random_matrix", {}).get(key)
            if not rm:
                continue
            for m in rm["members"]:
                p = analyse.station_profiles(HERE / "ens" / m["case"], m["time"])
                if st not in p:
                    continue
                xs, ys, U = p[st]
                ax.plot(U[:, 0], ys, color=ACCENT[key], lw=0.5, alpha=0.25, zorder=1)
        if st in base:
            xs, ys, U = base[st]
            ax.plot(U[:, 0], ys, color=INK, lw=1.8, ls="--", zorder=3, label="baseline")
            UL = f(np.column_stack([xs, ys]))
            ax.plot(UL[:, 0], ys, color=LES_C, lw=1.8, zorder=4, label="LES")
        ax.set_title(f"$x/h$ = {st}", fontsize=10, color=INK)
        ax.set_xlabel("$U_x$")
        ax.grid(color="#eef2f5", lw=0.6)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axes[0].set_ylabel("$y/h$")
    axes[0].legend(fontsize=8, frameon=False)


def main():
    fig = plt.figure(figsize=(11, 8.0))
    gs = fig.add_gridspec(2, 4, height_ratios=[1.0, 1.25], hspace=0.42, wspace=0.28)
    ax0 = fig.add_subplot(gs[0, :])
    panel_reattachment(ax0)
    axes = [fig.add_subplot(gs[1, i]) for i in range(4)]
    panel_profiles(axes)
    fig.suptitle(
        "F6d - random-matrix model-form UQ (Xiao, Wang & Ghanem 2016) on periodic hills, "
        "$Re_H$ = 10595",
        fontsize=12.5, color=INK, x=0.02, ha="left", y=0.985)
    out = HERE / "F6d_band.png"
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
