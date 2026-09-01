#!/usr/bin/env python3
"""Act A screen data products, built from the sixteen landed motor-in-duct
points.  NOTHING IS SOLVED HERE.  Every number is read from a field, a mesh or
a monitor file that was already on disk.

WHAT IT WRITES (all into this directory, beside this file):
  actA_map_table.{pdf,svg,csv}        the 16-row peak-temperature map
  actA_envelope.{pdf,svg,csv}         peak temperature vs airspeed + limit line
  actA_radial_profile.{pdf,svg,csv}   radial cut through the hottest solid cell
  actA_monitor_replay.{pdf,svg,csv}   16 tiles, replayed from the run monitors
  actA_assumption_beat.{pdf,svg,csv}  hand model vs coupled solve
  actA_screen_data.json               everything above, for a re-render

THE UNCERTAINTY COLUMN IS HONESTLY EMPTY.  All sixteen points ran at a single
grid.  A discretisation error bar needs at least three grids; none exists and
none is constructed, interpolated or borrowed.  The column carries the reason,
not a number.  What IS a real measured quantity is the MARGIN TO THE 200 degC
limit, and that is what the envelope screen draws -- labelled as margin to the
limit so it cannot be read as a numerical error bar.

PLANTED-ZERO CONTROL, CLAUDE.md rule 3, on all three distinct readers:
  peak-temperature field reader -- the frozen comparator's own control, reused
  radial-profile reader         -- mesh_reader_actA.planted_profile_control
  monitor-trace reader          -- planted_monitor_control, below
A reader that cannot see the plant REFUSES; it does not degrade.

Naming: no internal identifier, case name or process word appears in any
figure, caption, axis or column header.  Operating points are named by their
physics -- watts and metres per second.
"""
import csv
import json
import os
import shutil
import sys
import tempfile

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                 # noqa: E402
from matplotlib.patches import Rectangle                        # noqa: E402
import matplotlib.cm as cm                                      # noqa: E402
import matplotlib.colors as mcolors                             # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mesh_reader_actA as MR                                   # noqa: E402

A24 = MR.A24
REPO = MR.REPO
RUNS = os.path.join(REPO, "verification", "runs", "T-family")
T23_ROOT = os.path.join(RUNS, "T23_runs")
T24_ROOT = os.path.join(RUNS, "T24_runs")

KELVIN_C = 273.15
T_INF_K = 288.0                 # registered inlet temperature
LIMIT_C = 200.0                 # the engineering temperature limit
DESIGN_C = 120.0                # the design isotherm
ENDTIME = "10000"
PLANT = MR.PLANT                # 1.234e-03 K

# The sixteen landed points: (power W, airspeed m/s, run root, case dir name).
POINTS = ([(80, u, T24_ROOT, "T24_P080_U%d" % u) for u in (10, 20, 30, 40)] +
          [(155, u, T24_ROOT, "T24_P155_U%d" % u) for u in (10, 20, 30, 40)] +
          [(230, u, T24_ROOT, "T24_P230_U%d" % u) for u in (10, 20, 30, 40)] +
          [(305, u, T23_ROOT, "T23_P305_U%d" % u) for u in (10, 20, 30, 40)])

# The hand model's two closures, as recorded beside the four solved points.
HAND_MODEL = {           # airspeed -> (duct-correlation rise/solved rise,
    10: (3.541, 2.031),  #             flat-plate rise/solved rise)
    20: (3.369, 1.947),
    30: (3.280, 1.911),
    40: (3.235, 1.896),
}
HAND_ABS_C = {           # airspeed -> (duct predicted degC, flat-plate degC)
    10: (329.1, 195.1),
    20: (197.3, 120.3),
    30: (148.0, 92.4),
    40: (121.6, 77.4),
}

UNCERTAINTY_TEXT = ("not available - single grid, no grid-refinement "
                    "error estimate")

plt.rcParams.update({
    "font.size": 9,
    "font.family": "serif",
    "mathtext.fontset": "dejavuserif",
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linewidth": 0.5,
    "pdf.fonttype": 42,
    "svg.fonttype": "none",
    "figure.dpi": 120,
})

EXTS = ("pdf", "svg")


def save(fig, stem):
    for e in EXTS:
        fig.savefig(os.path.join(HERE, "%s.%s" % (stem, e)),
                    bbox_inches="tight")
    plt.close(fig)
    return [os.path.join(HERE, "%s.%s" % (stem, e)) for e in EXTS]


def refuse(msg):
    sys.stderr.write("REFUSE: %s\n" % msg)
    raise SystemExit(2)


# ==========================================================================
# READER C -- the run monitor.  Tab-separated; the location columns contain
# spaces, so a whitespace split reads the wrong column and this reader does
# not do that.
# ==========================================================================

MONITOR_REL = os.path.join("postProcessing", "housing", "housing_T", "0",
                           "fieldMinMax.dat")


def monitor_path(root, case):
    return os.path.join(root, case, MONITOR_REL)


def read_monitor(path):
    """-> (iteration array, max-T array in K, min-T array in K).

    Column order is taken from the file's own header line, never assumed."""
    lines = open(path).read().split("\n")
    hdr = [l for l in lines if l.startswith("#") and "Time" in l]
    if len(hdr) != 1:
        refuse("%s has %d header lines carrying `Time`, expected 1"
               % (path, len(hdr)))
    names = [c.strip() for c in hdr[0].lstrip("#").split("\t") if c.strip()]
    try:
        i_t, i_min, i_max = (names.index("Time"), names.index("min"),
                             names.index("max"))
    except ValueError:
        refuse("%s header %r carries no Time/min/max triple" % (path, names))
    it, mx, mn = [], [], []
    for l in lines:
        if not l.strip() or l.startswith("#"):
            continue
        c = [x.strip() for x in l.split("\t") if x.strip() != ""]
        if len(c) <= max(i_t, i_min, i_max):
            refuse("%s: row with %d columns against a %d-column header"
                   % (path, len(c), len(names)))
        it.append(float(c[i_t]))
        mn.append(float(c[i_min]))
        mx.append(float(c[i_max]))
    if not it:
        refuse("%s carries no data rows" % path)
    return np.array(it), np.array(mx), np.array(mn)


def planted_monitor_control(path, mag=PLANT):
    """Copy the monitor, add `mag` to the max entry of ONE row located by LINE
    INDEX, read it back, and require exactly one shifted sample of exactly that
    magnitude.  REFUSES rather than degrades."""
    scratch = tempfile.mkdtemp(prefix="actAmon_")
    dest = os.path.join(scratch, "fieldMinMax.dat")
    try:
        shutil.copy2(path, dest)
        pristine = open(dest).read()

        a = read_monitor(dest)[1]
        b = read_monitor(dest)[1]
        if not np.array_equal(a, b):
            refuse("monitor reader is NOISY: two reads of identical bytes "
                   "differ")

        lines = pristine.split("\n")
        hdr_i = [k for k, l in enumerate(lines)
                 if l.startswith("#") and "Time" in l][0]
        names = [c.strip() for c in lines[hdr_i].lstrip("#").split("\t")
                 if c.strip()]
        i_max = names.index("max")
        data_idx = [k for k, l in enumerate(lines)
                    if l.strip() and not l.startswith("#")]
        tgt = data_idx[len(data_idx) // 2]
        cols = lines[tgt].split("\t")
        # locate the max column among the non-empty fields, by index not value
        pos = [k for k, c in enumerate(cols) if c.strip() != ""]
        cols[pos[i_max]] = "%.12e" % (float(cols[pos[i_max]].strip()) + mag)
        lines[tgt] = "\t".join(cols)
        open(dest, "w").write("\n".join(lines))

        c = read_monitor(dest)[1]
        d = c - a
        nz = np.where(d != 0.0)[0]
        if len(nz) != 1:
            refuse("monitor reader saw %d perturbed samples, expected 1"
                   % len(nz))
        seen = float(d[nz[0]])
        rel = abs(seen - mag) / mag
        if rel > 1e-9:
            refuse("monitor reader read %.6e K at the plant against %.6e K "
                   "planted" % (seen, mag))
        if open(path).read() != pristine:
            refuse("the monitor file changed under the control")
        return dict(passed=True, planted_K=mag, read_K=seen, rel_error=rel,
                    row_index=int(nz[0]), n_perturbed=1)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


# ==========================================================================
# 1.  THE 16-ROW MAP
# ==========================================================================

def build_map():
    rows = []
    for p_w, u_ms, root, case in POINTS:
        cdir = os.path.join(root, case)
        t_k = A24.read_Q1(cdir)                 # frozen comparator's reader
        t_c = t_k - KELVIN_C
        rows.append(dict(power_W=p_w, airspeed_ms=u_ms,
                         peak_T_degC=t_c,
                         rise_above_inlet_K=t_k - T_INF_K,
                         margin_to_limit_K=LIMIT_C - t_c,
                         margin_to_design_K=DESIGN_C - t_c,
                         numerical_uncertainty=UNCERTAINTY_TEXT,
                         source_field=os.path.join(cdir, ENDTIME, "housing",
                                                   "T")))
    return rows


ANCHORS = {(80, 10): 38.1374, (80, 20): 29.0795, (80, 30): 25.5462,
           (80, 40): 23.5897, (305, 10): 103.6078}


def check_anchors(rows):
    out = []
    for r in rows:
        k = (r["power_W"], r["airspeed_ms"])
        if k in ANCHORS:
            d = abs(round(r["peak_T_degC"], 4) - ANCHORS[k])
            out.append(dict(power_W=k[0], airspeed_ms=k[1],
                            expected_degC=ANCHORS[k],
                            measured_degC=r["peak_T_degC"],
                            abs_diff_degC=d, matches=bool(d <= 5e-5)))
    return out


def fig_map_table(rows):
    powers = sorted({r["power_W"] for r in rows})
    speeds = sorted({r["airspeed_ms"] for r in rows})
    grid = np.full((len(powers), len(speeds)), np.nan)
    for r in rows:
        grid[powers.index(r["power_W"]), speeds.index(r["airspeed_ms"])] = \
            r["peak_T_degC"]
    vmin, vmax = float(np.nanmin(grid)), float(np.nanmax(grid))

    fig = plt.figure(figsize=(9.2, 9.8))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.35], hspace=0.30,
                          bottom=0.075, top=0.955)

    # --- upper: the map as a shaded grid, colour bar UNCLIPPED with min/max
    ax = fig.add_subplot(gs[0])
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)     # exactly the data range
    im = ax.imshow(grid, cmap="inferno", norm=norm, aspect="auto",
                   origin="lower")
    ax.set_xticks(range(len(speeds)))
    ax.set_xticklabels([r"$%d$" % s for s in speeds])
    ax.set_yticks(range(len(powers)))
    ax.set_yticklabels([r"$%d$" % p for p in powers])
    ax.set_xlabel(r"Airspeed $U_\infty$  [m s$^{-1}$]")
    ax.set_ylabel(r"Dissipated power $P$  [W]")
    ax.set_title("Peak housing temperature over the sixteen solved operating "
                 "points", fontsize=10)
    ax.grid(False)
    for i in range(len(powers)):
        for j in range(len(speeds)):
            v = grid[i, j]
            fr = (v - vmin) / (vmax - vmin)
            ax.text(j, i, r"$%.4f$" % v, ha="center", va="center",
                    fontsize=9.5, color="white" if fr < 0.62 else "black")
    cb = fig.colorbar(im, ax=ax, pad=0.02)
    cb.set_label(r"Peak temperature  $[^\circ\mathrm{C}]$")
    cb.ax.text(0.5, -0.045, r"min $%.4f$" % vmin, transform=cb.ax.transAxes,
               ha="center", va="top", fontsize=7.5)
    cb.ax.text(0.5, 1.045, r"max $%.4f$" % vmax, transform=cb.ax.transAxes,
               ha="center", va="bottom", fontsize=7.5)

    # --- lower: the 16 rows with units and the uncertainty column
    ax2 = fig.add_subplot(gs[1])
    ax2.axis("off")
    head = ["Power\n[W]", "Airspeed\n[m s$^{-1}$]",
            "Peak temperature\n[$^\\circ$C]", "Rise above inlet\n[K]",
            "Margin to 200 $^\\circ$C\n[K]", "Numerical uncertainty\n[K]"]
    body = []
    for r in rows:
        body.append(["%d" % r["power_W"], "%d" % r["airspeed_ms"],
                     "%.4f" % r["peak_T_degC"],
                     "%.4f" % r["rise_above_inlet_K"],
                     "%+.4f" % r["margin_to_limit_K"],
                     "not available"])
    tb = ax2.table(cellText=body, colLabels=head, cellLoc="center",
                   bbox=[0.02, 0.02, 0.96, 0.96],
                   colWidths=[0.10, 0.12, 0.19, 0.17, 0.19, 0.19])
    tb.auto_set_font_size(False)
    tb.set_fontsize(8.0)
    for (r_i, c_i), cell in tb.get_celld().items():
        cell.set_linewidth(0.4)
        if r_i == 0:
            cell.set_text_props(weight="bold", fontsize=7.6)
            cell.set_facecolor("#e9e9ee")
        else:
            cell.set_facecolor("#ffffff" if r_i % 2 else "#f6f6f8")
        if c_i == 5 and r_i > 0:
            cell.set_text_props(color="#7a1f1f", fontsize=7.6)
    ax2.set_title("The sixteen solved points, with units", fontsize=10, pad=6)
    fig.text(0.5, 0.030,
             "Numerical uncertainty column: " + UNCERTAINTY_TEXT + ".",
             ha="center", va="top", fontsize=8.4, color="#7a1f1f",
             weight="bold")
    fig.text(0.5, 0.010,
             "All sixteen points were solved on one grid. A discretisation "
             "error bar needs a refinement study; none was run, so none "
             "exists for any row and none is estimated, interpolated or "
             "borrowed here.",
             ha="center", va="top", fontsize=7.6, color="#7a1f1f")
    return fig, dict(vmin=vmin, vmax=vmax, powers=powers, speeds=speeds,
                     grid=grid.tolist())


# ==========================================================================
# 2.  THE ENVELOPE
# ==========================================================================

def fig_envelope(rows):
    powers = sorted({r["power_W"] for r in rows})
    speeds = sorted({r["airspeed_ms"] for r in rows})
    fig, ax = plt.subplots(figsize=(7.6, 5.4))

    ax.axhspan(0, LIMIT_C, facecolor="#2e7d32", alpha=0.075, zorder=0,
               edgecolor="none")
    ax.axhline(LIMIT_C, color="#b3261e", lw=1.7, zorder=3)
    ax.text(33.0, LIMIT_C + 3.0,
            r"200 $^\circ$C temperature limit",
            color="#b3261e", va="bottom", ha="center", fontsize=8.6,
            weight="bold", zorder=6)
    ax.text(33.0, 165.0, "SAFE REGION\n(shaded: below the limit)",
            color="#2e7d32", fontsize=9.0, ha="center", va="center",
            weight="bold", zorder=6)
    ax.axhline(DESIGN_C, color="#7a5c00", lw=1.1, ls="--", zorder=3)
    ax.text(37.0, DESIGN_C + 3.5, r"120 $^\circ$C design isotherm",
            color="#7a5c00", va="bottom", ha="center", fontsize=8.4, zorder=6)

    cmap = plt.get_cmap("viridis", len(powers) + 1)
    series = {}
    for i, p in enumerate(powers):
        xs = speeds
        ys = [next(r["peak_T_degC"] for r in rows
                   if r["power_W"] == p and r["airspeed_ms"] == s)
              for s in speeds]
        series[p] = ys
        ax.plot(xs, ys, "-o", ms=4.5, lw=1.5, color=cmap(i),
                label=r"$P = %d$ W" % p, zorder=4)

    hot = min(rows, key=lambda r: r["margin_to_limit_K"])
    ax.annotate("", xy=(hot["airspeed_ms"], LIMIT_C),
                xytext=(hot["airspeed_ms"], hot["peak_T_degC"]),
                arrowprops=dict(arrowstyle="<->", color="#b3261e", lw=1.2),
                zorder=5)
    ax.text(hot["airspeed_ms"] + 0.9,
            0.5 * (LIMIT_C + hot["peak_T_degC"]),
            "margin to the limit\nat the hottest solved point\n"
            r"$+%.4f$ K" % hot["margin_to_limit_K"],
            color="#b3261e", fontsize=8.4, va="center", ha="left",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#b3261e",
                      lw=0.6, alpha=0.92), zorder=7)

    ax.set_xlim(6.0, 44.0)
    ax.set_ylim(0, 215)
    ax.set_xticks(speeds)
    ax.set_xlabel(r"Airspeed $U_\infty$  [m s$^{-1}$]")
    ax.set_ylabel(r"Peak housing temperature  $[^\circ\mathrm{C}]$")
    ax.set_title("Temperature envelope of the solved operating map",
                 fontsize=10)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.115), ncol=4,
              fontsize=8.5, framealpha=1.0,
              title="one curve per dissipated power", title_fontsize=8.0)
    ax.text(0.012, 0.015,
            "The double-headed arrow is the MARGIN TO THE 200 $^\\circ$C "
            "limit, a measured temperature difference.\nIt is not a numerical "
            "error bar: the sixteen points ran on one grid, so no "
            "grid-refinement\nuncertainty band exists and none is drawn.",
            transform=ax.transAxes, fontsize=7.2, color="#444444",
            va="bottom", ha="left")
    return fig, series


# ==========================================================================
# 3.  THE RADIAL PROFILE
# ==========================================================================

REGION_LABEL = {"core": "heat-generating rotor core\n"
                        r"solid, $k = 40$ W m$^{-1}$K$^{-1}$",
                "housing": "aluminium housing wall\n"
                           r"solid, $k = 167$ W m$^{-1}$K$^{-1}$",
                "fluid": "cooling air annulus\n"
                         r"$k = 0.026$ W m$^{-1}$K$^{-1}$"}
REGION_SHORT = {"core": "rotor core", "housing": "housing wall",
                "fluid": "cooling air"}
REGION_FACE = {"core": "#d8c8a8", "housing": "#c9d6e3", "fluid": "#eef3ee"}


def build_radial(hot_case_dir, others):
    """Radial cut through the axial station holding the hottest solid cell."""
    # locate the hottest solid cell's axial position from the case's own field
    cc, _ = MR.cell_centres(hot_case_dir, "housing")
    T = MR.read_internal_T(hot_case_dir, "housing")
    z_hot = float(cc[int(np.argmax(T)), 2])
    prof, z_used = MR.radial_profile(hot_case_dir,
                                     ("core", "housing", "fluid"), z_hot)
    extra = {}
    for label, cdir in others.items():
        p, _ = MR.radial_profile(cdir, ("fluid",), z_hot)
        extra[label] = (p[0][1], p[0][2])
    return prof, z_used, z_hot, extra


def region_stats(r_m, T_K):
    x = r_m * 1000.0
    Tc = T_K - KELVIN_C
    c = np.polyfit(x, Tc, 1)
    fit = np.polyval(c, x)
    ss = 1.0 - ((Tc - fit) ** 2).sum() / ((Tc - Tc.mean()) ** 2).sum()
    loc = np.gradient(Tc, x)
    return dict(mean_slope_K_per_mm=float(c[0]),
                r_squared=float(ss),
                max_abs_residual_K=float(np.abs(Tc - fit).max()),
                local_slope_first_K_per_mm=float(loc[0]),
                local_slope_last_K_per_mm=float(loc[-1]),
                r_min_mm=float(x.min()), r_max_mm=float(x.max()),
                T_at_r_min_degC=float(Tc[0]), T_at_r_max_degC=float(Tc[-1]),
                drop_K=float(Tc[0] - Tc[-1]), n_cells=int(len(x)))


REGION_COLOUR = {"core": "#b5651d", "housing": "#1f5fb3", "fluid": "#2e7d32"}


def fig_radial(prof, z_used, extra, stats):
    """Four panels sharing one temperature axis.  The three material regions
    get one panel each -- the housing wall is 3.5 mm of a 118 mm radius span
    and is invisible on a single common axis, so the radius axis is BROKEN at
    the two material interfaces and each panel stays linear in r.  The fourth
    panel is the near-wall air at all four airspeeds, which is where the air's
    single slope is shown not to be one slope."""
    order = {"core": 0, "housing": 1, "fluid": 2}
    byreg = {p[0]: p for p in prof}
    fig = plt.figure(figsize=(12.0, 5.2))
    gs = fig.add_gridspec(1, 4, width_ratios=[1.35, 0.85, 1.5, 1.35],
                          wspace=0.10, left=0.055, right=0.985,
                          top=0.795, bottom=0.185)

    ymin = min((p[2] - KELVIN_C).min() for p in prof) - 4.0
    ymax = max((p[2] - KELVIN_C).max() for p in prof) + 16.0
    axes = []
    for reg in ("core", "housing", "fluid"):
        ax = fig.add_subplot(gs[order[reg]], sharey=axes[0] if axes else None)
        axes.append(ax)
        _r, T = byreg[reg][1] * 1000.0, byreg[reg][2] - KELVIN_C
        ax.set_facecolor(REGION_FACE[reg])
        ax.plot(_r, T, "-o", ms=3.0, lw=1.4, color=REGION_COLOUR[reg])
        s = stats[reg]
        pad = 0.06 * (s["r_max_mm"] - s["r_min_mm"])
        ax.set_xlim(s["r_min_mm"] - pad, s["r_max_mm"] + pad)
        ax.set_ylim(ymin, ymax)
        ax.set_xlabel(r"Radius  $r$  [mm]", fontsize=8.5)
        ax.set_title(REGION_LABEL[reg], fontsize=8.2, pad=5)
        ax.tick_params(labelsize=7.6)
        if order[reg] > 0:
            plt.setp(ax.get_yticklabels(), visible=False)
        else:
            ax.set_ylabel(r"Temperature  $[^\circ\mathrm{C}]$")
        note = (r"mean slope" "\n"
                r"$%.4f$ K mm$^{-1}$" "\n"
                r"drop over region $%.4f$ K" "\n"
                r"straight-line fit $R^2 = %.4f$"
                % (s["mean_slope_K_per_mm"], s["drop_K"], s["r_squared"]))
        ax.text(0.5, 0.66, note, transform=ax.transAxes, fontsize=7.6,
                ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.30", fc="white",
                          ec=REGION_COLOUR[reg], lw=0.7, alpha=0.95),
                zorder=6)
        if reg != "housing":
            ax.text(0.5, 0.42,
                    "curved: a single slope here is a\nregion average, not a "
                    "local gradient",
                    transform=ax.transAxes, fontsize=7.0, ha="center",
                    va="center", color="#7a1f1f", style="italic", zorder=6)
        else:
            ax.text(0.5, 0.42, "straight to four decimals",
                    transform=ax.transAxes, fontsize=7.0, ha="center",
                    va="center", color="#1f5fb3", style="italic", zorder=6)

    # --- fourth panel: the near-wall air at all four airspeeds
    ax2 = fig.add_subplot(gs[3])
    fl = byreg["fluid"]
    ax2.plot(fl[1] * 1000.0, fl[2] - KELVIN_C, "-o", ms=3.0, lw=1.4,
             color="#2e7d32", label=r"$U_\infty = 10$ m s$^{-1}$")
    for lab, (r, T) in sorted(extra.items(), key=lambda kv: int(kv[0])):
        ax2.plot(r * 1000.0, T - KELVIN_C, "-", lw=1.2,
                 label=r"$U_\infty = %s$ m s$^{-1}$" % lab)
    ax2.set_xlim(37.3, 50.0)
    ax2.set_ylim(ymin, ymax)
    ax2.set_xlabel(r"Radius  $r$  [mm]", fontsize=8.5)
    ax2.set_title("cooling air, first 12 mm off the housing surface\n"
                  "all four airspeeds", fontsize=8.2, pad=5)
    ax2.tick_params(labelsize=7.6)
    ax2.legend(fontsize=7.2, loc="upper right", framealpha=0.95)
    s = stats["fluid"]
    ax2.text(0.5, 0.30,
             "air gradient at the surface\n"
             r"$%.1f$ K mm$^{-1}$, falling to" "\n"
             r"$%.4f$ K mm$^{-1}$ in the free stream"
             % (s["local_slope_first_K_per_mm"],
                s["local_slope_last_K_per_mm"]),
             transform=ax2.transAxes, fontsize=7.4, ha="center", va="top",
             bbox=dict(boxstyle="round,pad=0.30", fc="white", ec="#2e7d32",
                       lw=0.7, alpha=0.95))

    fig.suptitle("Radial temperature cut through the hottest solid cell     "
                 r"$P = 305$ W,   $U_\infty = 10$ m s$^{-1}$,   axial station"
                 r" $z = %.2f$ mm" % (z_used * 1000.0),
                 fontsize=10.5, y=0.975)
    fig.text(0.5, 0.925,
             "radius axis broken at the two material interfaces so the 3.5 mm "
             "housing wall is visible; every panel is linear in $r$ and every "
             "marker is one computational cell",
             ha="center", fontsize=7.8, color="#444444")
    fig.text(0.5, 0.045,
             "THREE MATERIAL REGIONS, THREE DISTINCT MEAN SLOPES "
             r"($%.4f$ / $%.4f$ / $%.4f$ K mm$^{-1}$) - but only the housing "
             "wall is a straight line."
             % (stats["core"]["mean_slope_K_per_mm"],
                stats["housing"]["mean_slope_K_per_mm"],
                stats["fluid"]["mean_slope_K_per_mm"]),
             ha="center", fontsize=8.2, color="#7a1f1f", weight="bold")
    fig.text(0.5, 0.020,
             "The rotor core carries a volumetric heat source and the air "
             "carries a thermal boundary layer, so both are curved; their "
             "single slopes are region averages and are labelled as such.",
             ha="center", fontsize=7.6, color="#444444")
    return fig


# ==========================================================================
# 4.  THE 16-TILE MONITOR REPLAY
# ==========================================================================

def fig_monitor(traces, final_internal):
    fig, axes = plt.subplots(4, 4, figsize=(11.0, 8.2), sharex=True)
    powers = sorted({p for p, _u in traces})
    speeds = sorted({u for _p, u in traces})
    for i, p in enumerate(powers):
        for j, u in enumerate(speeds):
            ax = axes[len(powers) - 1 - i, j]
            it, mx, mn = traces[(p, u)]
            ax.plot(it, mx - KELVIN_C, lw=1.3, color="#b3261e")
            ax.plot(it, mn - KELVIN_C, lw=1.0, color="#1f5fb3", alpha=0.8)
            ax.fill_between(it, mn - KELVIN_C, mx - KELVIN_C,
                            color="#b3261e", alpha=0.10)
            fin = mx[-1] - KELVIN_C
            ax.axhline(fin, color="#666666", lw=0.6, ls=":")
            ax.set_title(r"$%d$ W,  $%d$ m s$^{-1}$" % (p, u), fontsize=8.0,
                         pad=3)
            ax.text(0.97, 0.10, r"settles at $%.4f\ ^\circ$C" % fin,
                    transform=ax.transAxes, fontsize=6.6, ha="right",
                    color="#333333")
            ax.tick_params(labelsize=6.6)
            ax.set_ylim(0, 115)
            if j == 0:
                ax.set_ylabel(r"$T$  $[^\circ\mathrm{C}]$", fontsize=7.5)
            if i == 0:
                ax.set_xlabel("Iteration", fontsize=7.5)
    fig.suptitle("Solid-body temperature monitors, replayed from the sixteen "
                 "runs\n"
                 "upper trace: hottest point in the housing; lower trace: "
                 "coldest point; band between them", fontsize=10, y=0.975)
    fig.text(0.5, 0.005,
             "Every trace is the run's own monitor output, sampled every 100 "
             "iterations and replayed unchanged. The monitor scans the housing "
             "cells AND its bounding faces,\nso its settled value sits "
             "%.4f K above the cell-only peak quoted in the map table at the "
             "hottest point - both are real readings of the same solution."
             % final_internal["offset_K"],
             ha="center", fontsize=7.0, color="#444444")
    return fig


# ==========================================================================
# 5.  THE ASSUMPTION BEAT
# ==========================================================================

def fig_assumption(rows):
    speeds = sorted(HAND_MODEL)
    solved = {u: next(r["peak_T_degC"] for r in rows
                      if r["power_W"] == 305 and r["airspeed_ms"] == u)
              for u in speeds}
    fig = plt.figure(figsize=(13.4, 4.7))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 1.30, 0.95], wspace=0.30,
                          left=0.055, right=0.985, top=0.855, bottom=0.155)

    # --- panel 1: absolute temperatures
    ax = fig.add_subplot(gs[0])
    w = 0.26
    xs = np.arange(len(speeds))
    ax.bar(xs - w, [HAND_ABS_C[u][0] for u in speeds], w,
           label="hand model, duct correlation", color="#c0654a")
    ax.bar(xs, [HAND_ABS_C[u][1] for u in speeds], w,
           label="hand model, flat-plate correlation", color="#e0a458")
    ax.bar(xs + w, [solved[u] for u in speeds], w,
           label="coupled solve", color="#2f6f8f")
    ax.axhline(LIMIT_C, color="#b3261e", lw=1.3)
    ax.text(len(speeds) - 0.55, LIMIT_C + 6, r"200 $^\circ$C limit",
            color="#b3261e", fontsize=7.6, ha="right")
    ax.set_xticks(xs)
    ax.set_xticklabels([r"$%d$" % u for u in speeds])
    ax.set_xlabel(r"Airspeed $U_\infty$  [m s$^{-1}$]")
    ax.set_ylabel(r"Peak temperature  $[^\circ\mathrm{C}]$")
    ax.set_title(r"Hand model against the solve, at $P = 305$ W", fontsize=9.5)
    ax.legend(fontsize=7.0, loc="upper right")

    # --- panel 2: the overprediction factor, which SHRINKS with airspeed
    ax2 = fig.add_subplot(gs[1])
    duct = [HAND_MODEL[u][0] for u in speeds]
    flat = [HAND_MODEL[u][1] for u in speeds]
    ax2.plot(speeds, duct, "-o", color="#c0654a", lw=1.6, ms=5)
    ax2.plot(speeds, flat, "-s", color="#e0a458", lw=1.6, ms=5)
    ax2.text(41.5, duct[-1], "duct\ncorrelation", color="#c0654a",
             fontsize=7.6, va="center", ha="left")
    ax2.text(41.5, flat[-1], "flat-plate\ncorrelation", color="#e0a458",
             fontsize=7.6, va="center", ha="left")
    ax2.axhline(1.0, color="#2f6f8f", lw=1.3, ls="--")
    ax2.text(8.0, 1.04, "coupled solve (reference, 1.000)", color="#2f6f8f",
             fontsize=7.8, va="bottom", ha="left")
    for u, d, f in zip(speeds, duct, flat):
        dx = -14 if u == speeds[-1] else 0
        ax2.annotate(r"$%.3f$" % d, (u, d), textcoords="offset points",
                     xytext=(dx, 8), ha="center", fontsize=7.4,
                     color="#c0654a")
        ax2.annotate(r"$%.3f$" % f, (u, f), textcoords="offset points",
                     xytext=(dx, -14), ha="center", fontsize=7.4,
                     color="#e0a458")
    ax2.set_xticks(speeds)
    ax2.set_xlim(7, 52)
    ax2.set_ylim(0.80, 4.05)
    ax2.set_xlabel(r"Airspeed $U_\infty$  [m s$^{-1}$]")
    ax2.set_ylabel("Hand-model rise / solved rise  [-]")
    ax2.set_title("The hand model's overprediction\nSHRINKS as airspeed rises",
                  fontsize=9.5)
    ax2.text(0.47, 0.20,
             "Largest error at the LOWEST airspeed:\n"
             r"$%.3f\times$ and $%.3f\times$ at $10$ m s$^{-1}$," "\n"
             r"falling to $%.3f\times$ and $%.3f\times$ at $40$ m s$^{-1}$."
             % (duct[0], flat[0], duct[-1], flat[-1]),
             transform=ax2.transAxes, fontsize=7.4, va="center", ha="center",
             color="#444444",
             bbox=dict(boxstyle="round,pad=0.30", fc="white", ec="#bbbbbb",
                       lw=0.5, alpha=0.95))

    # --- panel 3: the power the solved rise implies at 20 m/s
    ax3 = fig.add_subplot(gs[2])
    rise20 = solved[20] + KELVIN_C - T_INF_K
    p120 = 305.0 * (DESIGN_C - (T_INF_K - KELVIN_C)) / rise20
    p200 = 305.0 * (LIMIT_C - (T_INF_K - KELVIN_C)) / rise20
    names = ["solved\noperating\npoint",
             "power that\nwould reach\n" + r"120 $^\circ$C",
             "power that\nwould reach\n" + r"200 $^\circ$C"]
    vals = [305.0, p120, p200]
    cols = ["#2f6f8f", "#7a5c00", "#b3261e"]
    b = ax3.bar(names, vals, color=cols, width=0.55)
    for rect, v, i in zip(b, vals, range(3)):
        ax3.text(rect.get_x() + rect.get_width() / 2, v + 22,
                 (r"$%.0f$ W" % v) + ("\nsolved" if i == 0
                                      else "\nEXTRAPOLATED"),
                 ha="center", va="bottom", fontsize=7.6, color=cols[i],
                 weight="bold" if i == 0 else "normal")
    ax3.set_ylim(0, 2150)
    ax3.set_ylabel(r"Dissipated power  [W]")
    ax3.set_title(r"Power headroom implied at $U_\infty = 20$ m s$^{-1}$",
                  fontsize=9.5)
    ax3.text(0.5, 0.985,
             "The two right-hand bars scale the\n"
             r"measured $%.3f$ K rise linearly in power." "\n"
             "The highest power solved anywhere\n"
             "is 305 W, so both sit beyond\n"
             "everything that was computed." % rise20,
             transform=ax3.transAxes, fontsize=6.9, va="top", ha="center",
             color="#444444",
             bbox=dict(boxstyle="round,pad=0.28", fc="white", ec="#bbbbbb",
                       lw=0.5, alpha=0.95))
    ax3.tick_params(axis="x", labelsize=7.2)
    return fig, dict(solved_degC=solved, duct_factor=dict(zip(speeds, duct)),
                     flat_factor=dict(zip(speeds, flat)),
                     rise_at_20ms_K=float(rise20),
                     power_for_120C_at_20ms_W=float(p120),
                     power_for_200C_at_20ms_W=float(p200))


# ==========================================================================
# MAIN
# ==========================================================================

def main():
    out = {}
    print("== READING THE SIXTEEN POINTS")
    rows = build_map()
    anchors = check_anchors(rows)
    for a in anchors:
        print("   anchor %3d W / %2d m/s  expected %9.4f  measured %.6f  %s"
              % (a["power_W"], a["airspeed_ms"], a["expected_degC"],
                 a["measured_degC"], "MATCH" if a["matches"] else "DIFFERS"))
    if not all(a["matches"] for a in anchors):
        refuse("an anchor value does not reproduce from the field on disk")

    print("\n== PLANTED-ZERO CONTROLS (CLAUDE.md rule 3)")
    controls = {}
    hot_dir = os.path.join(T23_ROOT, "T23_P305_U10")
    c1 = A24.planted_zero_control(hot_dir, "peak-temperature field reader",
                                  A24.read_Q1, A24.plant_Q1)
    controls["peak_temperature_field_reader"] = dict(
        passed=bool(c1["passed"]), planted_K=PLANT,
        read_K=float(c1["at_plant"]), detection_floor_K=float(c1["floor"]),
        n_cells_planted=int(c1["n_planted"]))
    print("   peak-temperature field reader: planted %.6e K, read %.6e K, "
          "floor %.0e K" % (PLANT, c1["at_plant"], c1["floor"]))

    c2 = MR.planted_profile_control(hot_dir, "housing", 0.1245536)
    controls["radial_profile_reader"] = {k: (float(v) if isinstance(v, float)
                                             else v) for k, v in c2.items()}
    print("   radial-profile reader: planted %.6e K, read %.6e K at "
          "r = %.6f m, %d sample perturbed"
          % (PLANT, c2["read_K"], c2["radius_m"], c2["n_perturbed"]))

    c3 = planted_monitor_control(monitor_path(T23_ROOT, "T23_P305_U10"))
    controls["monitor_trace_reader"] = c3
    print("   monitor-trace reader: planted %.6e K, read %.6e K, %d sample "
          "perturbed" % (PLANT, c3["read_K"], c3["n_perturbed"]))

    print("\n== FIGURES")
    fig, mapmeta = fig_map_table(rows)
    save(fig, "actA_map_table")
    print("   map table   min %.4f degC  max %.4f degC"
          % (mapmeta["vmin"], mapmeta["vmax"]))

    fig, series = fig_envelope(rows)
    save(fig, "actA_envelope")
    hot = min(rows, key=lambda r: r["margin_to_limit_K"])
    print("   envelope    worst margin %+.4f K at %d W / %d m/s"
          % (hot["margin_to_limit_K"], hot["power_W"], hot["airspeed_ms"]))

    others = {str(u): os.path.join(T23_ROOT, "T23_P305_U%d" % u)
              for u in (20, 30, 40)}
    prof, z_used, z_hot, extra = build_radial(hot_dir, others)
    stats = {reg: region_stats(r, T) for reg, r, T, _z in prof}
    fig = fig_radial(prof, z_used, extra, stats)
    save(fig, "actA_radial_profile")
    for reg in ("core", "housing", "fluid"):
        s = stats[reg]
        print("   radial %-8s slope %+9.4f K/mm  R2 %.5f  local %+9.3f -> "
              "%+8.4f K/mm" % (reg, s["mean_slope_K_per_mm"], s["r_squared"],
                               s["local_slope_first_K_per_mm"],
                               s["local_slope_last_K_per_mm"]))

    traces = {}
    for p_w, u_ms, root, case in POINTS:
        traces[(p_w, u_ms)] = read_monitor(monitor_path(root, case))
    hot_final_mon = traces[(305, 10)][1][-1] - KELVIN_C
    hot_internal = next(r["peak_T_degC"] for r in rows
                        if r["power_W"] == 305 and r["airspeed_ms"] == 10)
    fin = dict(monitor_degC=float(hot_final_mon),
               internal_cells_degC=float(hot_internal),
               offset_K=float(hot_final_mon - hot_internal))
    fig = fig_monitor(traces, fin)
    save(fig, "actA_monitor_replay")
    print("   monitors    16 tiles, %d samples each, monitor peak %.4f degC "
          "against cell-only peak %.4f degC (offset %.4f K)"
          % (len(traces[(305, 10)][0]), fin["monitor_degC"],
             fin["internal_cells_degC"], fin["offset_K"]))

    fig, beat = fig_assumption(rows)
    save(fig, "actA_assumption_beat")
    print("   assumption  duct %s  flat %s"
          % (["%.3f" % beat["duct_factor"][u] for u in (10, 20, 30, 40)],
             ["%.3f" % beat["flat_factor"][u] for u in (10, 20, 30, 40)]))
    print("   power at 20 m/s: %.1f W to 120 degC, %.1f W to 200 degC "
          "(both extrapolated)" % (beat["power_for_120C_at_20ms_W"],
                                   beat["power_for_200C_at_20ms_W"]))

    # ------------------------------------------------------------------ CSV
    with open(os.path.join(HERE, "actA_map_table.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["power_W", "airspeed_m_per_s", "peak_temperature_degC",
                    "rise_above_inlet_K", "margin_to_200C_limit_K",
                    "margin_to_120C_design_K", "numerical_uncertainty_K"])
        for r in rows:
            w.writerow(["%d" % r["power_W"], "%d" % r["airspeed_ms"],
                        "%.6f" % r["peak_T_degC"],
                        "%.6f" % r["rise_above_inlet_K"],
                        "%.6f" % r["margin_to_limit_K"],
                        "%.6f" % r["margin_to_design_K"],
                        UNCERTAINTY_TEXT])

    with open(os.path.join(HERE, "actA_envelope.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["power_W", "airspeed_m_per_s", "peak_temperature_degC",
                    "margin_to_200C_limit_K", "limit_degC",
                    "design_isotherm_degC"])
        for r in rows:
            w.writerow(["%d" % r["power_W"], "%d" % r["airspeed_ms"],
                        "%.6f" % r["peak_T_degC"],
                        "%.6f" % r["margin_to_limit_K"], "200", "120"])

    with open(os.path.join(HERE, "actA_radial_profile.csv"), "w",
              newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["region", "radius_mm", "temperature_degC", "power_W",
                    "airspeed_m_per_s", "axial_station_mm"])
        for reg, r, T, _z in prof:
            for rr, tt in zip(r, T):
                w.writerow([REGION_SHORT[reg], "%.6f" % (rr * 1000.0),
                            "%.6f" % (tt - KELVIN_C), "305", "10",
                            "%.6f" % (z_used * 1000.0)])
        for lab, (r, T) in sorted(extra.items()):
            for rr, tt in zip(r, T):
                w.writerow(["cooling air", "%.6f" % (rr * 1000.0),
                            "%.6f" % (tt - KELVIN_C), "305", lab,
                            "%.6f" % (z_used * 1000.0)])

    with open(os.path.join(HERE, "actA_monitor_replay.csv"), "w",
              newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["power_W", "airspeed_m_per_s", "iteration",
                    "solid_peak_temperature_degC",
                    "solid_minimum_temperature_degC"])
        for (p_w, u_ms), (it, mx, mn) in sorted(traces.items()):
            for a, b, c in zip(it, mx, mn):
                w.writerow(["%d" % p_w, "%d" % u_ms, "%d" % int(a),
                            "%.6f" % (b - KELVIN_C), "%.6f" % (c - KELVIN_C)])

    with open(os.path.join(HERE, "actA_assumption_beat.csv"), "w",
              newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["airspeed_m_per_s", "power_W",
                    "hand_model_duct_correlation_degC",
                    "hand_model_flat_plate_correlation_degC",
                    "coupled_solve_degC",
                    "overprediction_factor_duct",
                    "overprediction_factor_flat_plate"])
        for u in sorted(HAND_MODEL):
            w.writerow(["%d" % u, "305", "%.1f" % HAND_ABS_C[u][0],
                        "%.1f" % HAND_ABS_C[u][1],
                        "%.6f" % beat["solved_degC"][u],
                        "%.3f" % beat["duct_factor"][u],
                        "%.3f" % beat["flat_factor"][u]])

    # ----------------------------------------------------------------- JSON
    out = dict(
        map_rows=rows,
        anchor_checks=anchors,
        map_colour_range_degC=dict(minimum=mapmeta["vmin"],
                                   maximum=mapmeta["vmax"]),
        envelope=dict(series_degC={str(k): v for k, v in series.items()},
                      limit_degC=LIMIT_C, design_isotherm_degC=DESIGN_C,
                      worst_margin_K=hot["margin_to_limit_K"],
                      worst_point=dict(power_W=hot["power_W"],
                                       airspeed_ms=hot["airspeed_ms"]),
                      uncertainty_band="NONE - single grid, no "
                                       "grid-refinement error estimate "
                                       "exists; the drawn interval is the "
                                       "measured margin to the 200 degC "
                                       "limit"),
        radial=dict(axial_station_m=z_used,
                    hottest_solid_cell_axial_m=z_hot,
                    power_W=305, airspeed_ms=10,
                    region_stats=stats,
                    profile={REGION_SHORT[reg]:
                             dict(radius_mm=(r * 1000.0).tolist(),
                                  temperature_degC=(T - KELVIN_C).tolist())
                             for reg, r, T, _z in prof},
                    near_wall_air_by_airspeed={
                        lab: dict(radius_mm=(r * 1000.0).tolist(),
                                  temperature_degC=(T - KELVIN_C).tolist())
                        for lab, (r, T) in extra.items()}),
        monitors=dict(quantity="minimum and maximum temperature over the "
                               "housing solid region and its bounding faces, "
                               "written by the run itself every 100 "
                               "iterations",
                      source_file_pattern=MONITOR_REL,
                      samples_per_case=int(len(traces[(305, 10)][0])),
                      settled_vs_cell_only=fin,
                      traces={"%d_W_%d_ms" % k:
                              dict(iteration=it.tolist(),
                                   peak_degC=(mx - KELVIN_C).tolist(),
                                   minimum_degC=(mn - KELVIN_C).tolist())
                              for k, (it, mx, mn) in traces.items()}),
        assumption_beat=beat,
        numerical_uncertainty=dict(
            available=False,
            reason="all sixteen points ran at one grid level; a "
                   "discretisation error bar requires a grid triple and none "
                   "was run, so none exists and none is constructed",
            column_entry=UNCERTAINTY_TEXT),
        planted_zero_controls=controls,
    )
    with open(os.path.join(HERE, "actA_screen_data.json"), "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True, default=float)
    print("\n== WROTE actA_screen_data.json and five CSV files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
