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
  actA_assumptions.{pdf,svg}          the assumptions box
  actA_screen_data.json               everything above, for a re-render

THE PEAK IS IN THE CORE, NOT THE HOUSING.  Until 2026-09-01 every peak on this
screen set was the maximum over the HOUSING region, and the margin to the
200 degC limit was computed from it.  The core region is MEASURED here to run
1.067 to 4.142 K hotter at every one of the sixteen points, so that peak
understated the body's true peak and OVERSTATED the margin -- the direction
that hurts whoever reads it.  Both peaks are now carried, the margin is
computed on the CORE, and `peak_T_degC` is the core value because the core is
where the peak is.  The housing peak keeps its own key and its own column and
is never called the hottest point.

THE UNCERTAINTY COLUMN IS HONESTLY EMPTY.  All sixteen points ran at a single
grid.  A discretisation error bar needs at least three grids; none exists and
none is constructed, interpolated or borrowed.  The column carries the reason,
not a number.  What IS a real measured quantity is the MARGIN TO THE 200 degC
limit, and that is what the envelope screen draws -- labelled as margin to the
limit so it cannot be read as a numerical error bar.

THE ANCHOR CHECK DIFFERENCES UNROUNDED VALUES.  It used to round the
measurement to four decimals before subtracting a four-decimal expectation,
which manufactures an exact zero out of arithmetic rather than agreement.  A
zero produced by rounding is not evidence, for the same reason a zero from a
blind reader is not.  The registered gate stays at 5e-5 K, unchanged; only the
defect in the instrument is repaired.

PLANTED-ZERO CONTROL, CLAUDE.md rule 3, on all FOUR distinct readers:
  peak core-temperature reader   -- planted_core_control, below
  peak housing-temperature field -- the frozen comparator's own control, reused
  radial-profile reader          -- mesh_reader_actA.planted_profile_control
  monitor-trace reader           -- planted_monitor_control, below
A reader that cannot see the plant REFUSES; it does not degrade.

Naming: no internal identifier, case name or process word appears in any
figure, caption, axis or column header.  Operating points are named by their
physics -- watts and metres per second.
"""
import csv
import json
import os
import re
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
sys.path.insert(0, os.path.dirname(HERE))
import latex_style as LS                                        # noqa: E402
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
# The frozen T24 comparator's registered control apparatus, IMPORTED so that
# this file cannot quietly hold a different ladder or a different tolerance.
LADDER = A24.LADDER             # section 3.6 clause 3, the magnitude ladder
PLANT_REL_SLACK = A24.PLANT_REL_SLACK           # clause 5, RELATIVE, 1e-9

# The three mesh regions of this body.  `core` is the heat-generating solid and
# is where the peak temperature is; `housing` is the aluminium wall around it.
SOLID_REGIONS = ("core", "housing")
MESH_REGIONS = ("fluid", "housing", "core")

# 0.1 degC SIGNIFICANT FIGURES on every temperature and temperature difference
# DISPLAYED IN A FIGURE, per the 2026-09-01 figure standard, until the grid
# triple lands.  It is applied to figure text only.  It is NOT applied to the
# JSON or the CSV, which are the record and not a display, and it is NOT
# applied to instrument evidence -- a planted magnitude of 1.234e-03 K or an
# anchor residual of 3.7e-05 K rounded to 0.1 K becomes 0.0 and stops being
# evidence at all, which is the very defect the anchor check above repairs.
T_FMT = "%.1f"

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

# Text is set by LaTeX itself (Latin Modern), not by matplotlib's mathtext
# imitation of it.  latex_style.apply() refuses if LaTeX did not in fact run.
LS.apply(plt, base_font_size=9, extra={
    "axes.grid": True,
    "grid.alpha": 0.25,
    "grid.linewidth": 0.5,
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
# READER A2 -- THE PEAK CORE TEMPERATURE, and its planted-zero control.
#
# The frozen comparator reads Q1 = max(T) over the HOUSING only, because that
# is what T23/T24 registered as their bound.  The body's actual peak is in the
# CORE, which is measured here to sit 1.067 to 4.142 K above the housing at
# every one of the sixteen points.  A screen that quotes the housing peak as
# the peak understates it and overstates the margin to the limit.
#
# The frozen `planted_zero_control` cannot be reused for this reader: it pins
# the field path to `<endTime>/housing/T` at its own line 466, so its restore
# and its clause-8 no-write check both look at the wrong file for a core
# reader.  The nine clauses are therefore reimplemented here against the core
# field, with PLANT, the magnitude LADDER and the relative sizing tolerance
# ALL IMPORTED from the frozen comparator rather than restated.
# ==========================================================================

def core_field(case_dir):
    return os.path.join(case_dir, ENDTIME, "core", "T")


def read_core_peak(case_dir):
    """max(T) over the whole core region.  Reader path: internalField, window
    delimited by the field's OWN header through the frozen comparator."""
    lines, first, n = A24.internal_window(core_field(case_dir))
    return max(float(lines[first + i]) for i in range(n))


def plant_core_peak(case_dir, mag):
    """Plant `mag` into the HOTTEST core internalField cell, BY LINE INDEX
    computed from the field's own header.  Returns the count planted."""
    p = core_field(case_dir)
    lines, first, n = A24.internal_window(p)
    vals = [float(lines[first + i]) for i in range(n)]
    j = max(range(n), key=lambda i: vals[i])
    lines[first + j] = "%.12g" % (vals[j] + mag)        # writePrecision 12
    open(p, "w").write("\n".join(lines))
    return 1


def clear_local_pycache():
    """The frozen clause 9, extended to this directory.  A stale bytecode cache
    INVERTS a mutation control; PYTHONDONTWRITEBYTECODE does not fix it."""
    A24.clear_pycache()
    p = os.path.join(HERE, "__pycache__")
    if os.path.isdir(p):
        shutil.rmtree(p, ignore_errors=True)


def planted_core_control(case_dir, label="peak core-temperature reader"):
    """The frozen comparator's nine clauses, against the CORE field.

    Clause 1 copy-first with a refusal if the scratch resolves inside the case;
    clause 2 negative arm at bitwise 0.0 with NO tolerance; clause 3 the
    imported magnitude ladder, measured rung by rung; clause 4 refuse if the
    reader is blind; clause 5 the RELATIVE sizing predicate
    `at_plant >= PLANT*(1-1e-9)`; clause 8 the case is checked to be unwritten
    and the scratch is removed in a `finally`; clause 9 the bytecode caches are
    cleared first.  REFUSES rather than degrades."""
    clear_local_pycache()                                       # clause 9
    case_real = os.path.realpath(case_dir)
    scratch = tempfile.mkdtemp(prefix="actAcore_")
    dest = os.path.join(scratch, os.path.basename(case_dir))
    try:
        # CLAUSE 1: COPY FIRST, NEVER WRITE INTO THE CASE.
        if os.path.realpath(scratch) == case_real \
           or os.path.realpath(scratch).startswith(case_real + os.sep):
            refuse("core control scratch %s resolves INSIDE the case %s -- "
                   "clause 1 forbids writing into the case under any "
                   "circumstance" % (scratch, case_real))
        shutil.copytree(case_dir, dest, symlinks=True,
                        ignore=shutil.ignore_patterns("log.solve", "*.py",
                                                      "postProcessing"))
        if os.path.realpath(dest).startswith(case_real + os.sep):
            refuse("core control copy %s resolves INSIDE the case" % dest)
        pristine = open(core_field(dest)).read()

        # CLAUSE 2: NEGATIVE ARM.  Bitwise 0.0, no absolute tolerance.
        a = read_core_peak(dest)
        b = read_core_peak(dest)
        if (b - a) != 0.0:
            refuse("%s NEGATIVE ARM: the reader is NOISY -- two reads of "
                   "identical bytes differ by %r, and the registered threshold "
                   "is bitwise 0.0 with no tolerance" % (label, b - a))
        base = a

        # CLAUSE 3: POSITIVE ARM, the MEASURED ladder, exact and epsilon-free.
        rungs, floor, at_plant, n_planted = [], None, None, None
        for mag in LADDER:
            open(core_field(dest), "w").write(pristine)
            cnt = plant_core_peak(dest, mag)
            got = read_core_peak(dest) - base
            rungs.append((float(mag), float(got), int(cnt)))
            if got != 0.0:
                floor = mag if floor is None else min(floor, mag)
            if mag == PLANT:
                at_plant, n_planted = got, cnt
        open(core_field(dest), "w").write(pristine)

        # CLAUSE 4: REFUSE IF THE READER IS BLIND.
        if floor is None:
            refuse("%s POSITIVE ARM: the reader is BLIND -- no magnitude in "
                   "the imported ladder produced a non-zero read. An "
                   "instrument that cannot see a planted perturbation is not "
                   "entitled to certify a peak or a margin" % label)

        # CLAUSE 5: THE ONLY SIZING TOLERANCE, AND IT IS RELATIVE.
        if at_plant is None:
            refuse("%s: PLANT was not exercised by the ladder" % label)
        if not (at_plant >= PLANT * (1.0 - PLANT_REL_SLACK)):
            refuse("%s: read at PLANT is %.6e K, below the registered RELATIVE "
                   "predicate PLANT*(1-1e-9) = %.6e K"
                   % (label, at_plant, PLANT * (1.0 - PLANT_REL_SLACK)))

        # CLAUSE 8: the case was never written to, CHECKED not asserted.
        if open(core_field(case_dir)).read() != open(core_field(dest)).read():
            refuse("%s: the case file and the restored copy differ -- the "
                   "control may have written into the case" % label)
        return dict(passed=True, region="core", planted_K=float(PLANT),
                    read_K=float(at_plant), detection_floor_K=float(floor),
                    n_cells_planted=int(n_planted), base_K=float(base),
                    ladder_K=[r[0] for r in rungs],
                    ladder_read_K=[r[1] for r in rungs])
    finally:
        shutil.rmtree(scratch, ignore_errors=True)              # clause 8


# ==========================================================================
# READER C -- the run monitor.  Tab-separated; the location columns contain
# spaces, so a whitespace split reads the wrong column and this reader does
# not do that.
# ==========================================================================

MONITOR_REL = os.path.join("postProcessing", "housing", "housing_T", "0",
                           "fieldMinMax.dat")
CORE_MONITOR_REL = os.path.join("postProcessing", "core", "core_T", "0",
                                "fieldMinMax.dat")


def monitor_path(root, case):
    return os.path.join(root, case, MONITOR_REL)


def core_monitor_path(root, case):
    return os.path.join(root, case, CORE_MONITOR_REL)


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
    """Both solid peaks at every point.  `peak_T_degC` is the CORE value
    because the core is where the peak is; the housing peak keeps its own key
    and is never presented as the hottest point.  Every margin and every rise
    is computed from the core, which is the conservative direction and the only
    one that does not overstate how much room is left to the limit."""
    rows = []
    for p_w, u_ms, root, case in POINTS:
        cdir = os.path.join(root, case)
        core_k = read_core_peak(cdir)                   # reader A2, above
        hous_k = A24.read_Q1(cdir)                      # frozen Q1 reader
        core_c, hous_c = core_k - KELVIN_C, hous_k - KELVIN_C
        rows.append(dict(power_W=p_w, airspeed_ms=u_ms,
                         peak_T_degC=core_c,
                         peak_T_region="core",
                         peak_core_T_degC=core_c,
                         peak_housing_T_degC=hous_c,
                         core_above_housing_K=core_c - hous_c,
                         rise_above_inlet_K=core_k - T_INF_K,
                         housing_rise_above_inlet_K=hous_k - T_INF_K,
                         margin_to_limit_K=LIMIT_C - core_c,
                         margin_to_design_K=DESIGN_C - core_c,
                         housing_margin_to_limit_K=LIMIT_C - hous_c,
                         numerical_uncertainty=UNCERTAINTY_TEXT,
                         source_field=os.path.join(cdir, ENDTIME, "core", "T"),
                         source_field_housing=os.path.join(cdir, ENDTIME,
                                                           "housing", "T")))
    return rows


# The five values transcribed from the frozen T23/T24 record, which registered
# its bound on the HOUSING peak.  The anchor check is therefore a check on the
# HOUSING peak and stays one; it is not silently re-pointed at the core, which
# no frozen document carries a value for.
ANCHORS = {(80, 10): 38.1374, (80, 20): 29.0795, (80, 30): 25.5462,
           (80, 40): 23.5897, (305, 10): 103.6078}
ANCHOR_QUANTITY = ("peak housing temperature, the quantity the frozen T23/T24 "
                   "record registered its bound on")
# REGISTERED, and NOT ADJUSTED HERE.  The instrument below was repaired; the
# threshold it is read against was left exactly where it was registered,
# because moving a threshold to suit an outcome is what pre-registration
# forbids.
ANCHOR_GATE_K = 5e-5


def check_anchors(rows):
    """Difference the UNROUNDED measurement against the transcribed value.

    The previous form computed `abs(round(measured, 4) - expected)` against a
    four-decimal table.  Rounding the measurement to the expectation's own
    precision before subtracting cannot produce anything but an exact zero
    whenever the two agree to within half a unit in the last place, so the
    zero it reported was arithmetic, not agreement -- the same family of
    defect as a zero read by an instrument that has not been shown able to see
    a non-zero.  The real residuals are reported; the registered 5e-5 K gate is
    unchanged."""
    out = []
    for r in rows:
        k = (r["power_W"], r["airspeed_ms"])
        if k in ANCHORS:
            m = r["peak_housing_T_degC"]
            d = abs(m - ANCHORS[k])
            out.append(dict(power_W=k[0], airspeed_ms=k[1],
                            quantity=ANCHOR_QUANTITY,
                            expected_degC=ANCHORS[k],
                            measured_degC=m,
                            abs_diff_degC=d,
                            gate_K=ANCHOR_GATE_K,
                            differenced="unrounded on both sides",
                            matches=bool(d <= ANCHOR_GATE_K)))
    return out


MAP_TITLE = "Peak core temperature, 16 operating points"
# The caption must describe the picture that is actually drawn. It used to
# say "the table carries both solid peaks", which was true while a table sat
# inside this figure and became false the moment the table moved to the sheet.
MAP_CAPTION = (r"16 points $\cdot$ $P$ = 80--305 W $\cdot$ "
               r"$U_\infty$ = 10--40 m s$^{-1}$ $\cdot$ "
               r"$T_\mathrm{core}$ 24.7--107.7 $^\circ$C")


def fig_map_table(rows):
    """The map shades the CORE peak, which is the body's actual peak, so
    Sanaa's registered title is true of what is drawn.

    NO TABLE LIVES IN THIS FIGURE.  Under Sanaa's 2026-09-01 figure standard --
    "move the measured-values table out of the pressure figure into the sheet"
    -- a figure carries the picture and the sheet carries the numbers.  This
    figure previously drew the 4x4 map AND a full sixteen-row table of measured
    values in a second axes below it, which is exactly the defect she named on
    the jet flap.

    The sixteen rows were not deleted, they MOVED: they are the results table
    of the act itself (``motor_thermal_act.results()``, table
    ``motor_thermal_map``) and they are on disk beside this figure as
    ``actA_map_table.csv``, which this module still writes.  Nothing measured
    was lost by the split.
    """
    powers = sorted({r["power_W"] for r in rows})
    speeds = sorted({r["airspeed_ms"] for r in rows})
    grid = np.full((len(powers), len(speeds)), np.nan)
    for r in rows:
        grid[powers.index(r["power_W"]), speeds.index(r["airspeed_ms"])] = \
            r["peak_core_T_degC"]
    vmin, vmax = float(np.nanmin(grid)), float(np.nanmax(grid))
    hmin = float(min(r["peak_housing_T_degC"] for r in rows))
    hmax = float(max(r["peak_housing_T_degC"] for r in rows))

    fig = plt.figure(figsize=(9.6, 5.4))
    # ONE axes. The map, and nothing else: colour bar UNCLIPPED, min and max
    # carried by the bar's own END TICKS and nowhere else.
    ax = fig.add_subplot(1, 1, 1)
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)     # exactly the data range
    im = ax.imshow(grid, cmap="inferno", norm=norm, aspect="auto",
                   origin="lower")
    ax.set_xticks(range(len(speeds)))
    ax.set_xticklabels([r"$%d$" % s for s in speeds])
    ax.set_yticks(range(len(powers)))
    ax.set_yticklabels([r"$%d$" % p for p in powers])
    ax.set_xlabel(r"Airspeed $U_\infty$  [m s$^{-1}$]")
    ax.set_ylabel(r"Dissipated power $P$  [W]")
    ax.set_title(MAP_TITLE, fontsize=10.5)
    ax.grid(False)
    for i in range(len(powers)):
        for j in range(len(speeds)):
            v = grid[i, j]
            fr = (v - vmin) / (vmax - vmin)
            ax.text(j, i, r"$" + (T_FMT % v) + "$", ha="center", va="center",
                    fontsize=9.5, color="white" if fr < 0.62 else "black")
    cb = fig.colorbar(im, ax=ax, pad=0.02)
    cb.set_label(r"$^\circ$C")
    mid = np.linspace(vmin, vmax, 5)[1:-1]
    cb.set_ticks([vmin] + list(mid) + [vmax])
    cb.set_ticklabels([T_FMT % t for t in [vmin] + list(mid) + [vmax]])
    cb.ax.tick_params(labelsize=8.0)

    fig.subplots_adjust(bottom=0.20, top=0.90)
    fig.text(0.5, 0.075, MAP_CAPTION, ha="center", va="top", fontsize=8.2,
             color="#333333")
    return fig, dict(vmin=vmin, vmax=vmax, powers=powers, speeds=speeds,
                     grid=grid.tolist(), housing_min=hmin, housing_max=hmax)


# ==========================================================================
# 2.  THE ENVELOPE
# ==========================================================================

ENVELOPE_TITLE = "Peak core temperature against airspeed"
ENVELOPE_CAPTION = (r"4 curves, $P$ = 80--305 W $\cdot$ limit 200 $^\circ$C "
                    r"$\cdot$ min margin +92.3 K at 305 W, 10 m s$^{-1}$")


def fig_envelope(rows):
    powers = sorted({r["power_W"] for r in rows})
    speeds = sorted({r["airspeed_ms"] for r in rows})
    fig, ax = plt.subplots(figsize=(7.6, 5.4))

    ax.axhspan(0, LIMIT_C, facecolor="#2e7d32", alpha=0.075, zorder=0,
               edgecolor="none")
    ax.axhline(LIMIT_C, color="#b3261e", lw=1.7, zorder=3)
    ax.text(33.0, LIMIT_C + 3.0,
            r"200 $^\circ$C limit",
            color="#b3261e", va="bottom", ha="center", fontsize=8.6,
            zorder=6)
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
            "margin to the limit\n" + r"$+" + (T_FMT % hot["margin_to_limit_K"])
            + r"$ K",
            color="#b3261e", fontsize=8.4, va="center", ha="left",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#b3261e",
                      lw=0.6, alpha=0.92), zorder=7)

    ax.set_xlim(6.0, 44.0)
    ax.set_ylim(0, 215)
    ax.set_xticks(speeds)
    ax.set_xlabel(r"Airspeed $U_\infty$  [m s$^{-1}$]")
    ax.set_ylabel(r"Peak core temperature  $[^\circ\mathrm{C}]$")
    ax.set_title(ENVELOPE_TITLE, fontsize=10.5)
    # The legend sits INSIDE the axes, per the 2026-09-01 figure standard.
    ax.legend(loc="lower left", ncol=2, fontsize=8.2, framealpha=1.0,
              borderpad=0.5)
    fig.subplots_adjust(bottom=0.165)
    fig.text(0.5, 0.012, ENVELOPE_CAPTION, ha="center", va="bottom",
             fontsize=8.2, color="#333333")
    return fig, series


# ==========================================================================
# 3.  THE RADIAL PROFILE
# ==========================================================================

REGION_LABEL = {"core": "heat-generating core\n"
                        r"solid, $k = 40$ W m$^{-1}$K$^{-1}$",
                "housing": "aluminium housing wall\n"
                           r"solid, $k = 167$ W m$^{-1}$K$^{-1}$",
                "fluid": "cooling air annulus\n"
                         r"$k = 0.026$ W m$^{-1}$K$^{-1}$"}
REGION_SHORT = {"core": "core", "housing": "housing wall",
                "fluid": "cooling air"}
REGION_FACE = {"core": "#d8c8a8", "housing": "#c9d6e3", "fluid": "#eef3ee"}


def build_radial(hot_case_dir, others):
    """Radial cut through the axial station holding the hottest solid cell.

    The station used to be located from the HOUSING field alone, which named
    the hottest HOUSING cell and not the hottest solid cell -- the same
    housing-only assumption that understated the peak in the map.  Both solid
    regions are searched here and the winner is measured, not assumed; the
    two stations are also compared and the comparison is returned so the
    figure's title can be checked rather than trusted."""
    hottest = {}
    for reg in SOLID_REGIONS:
        cc, _ = MR.cell_centres(hot_case_dir, reg)
        T = MR.read_internal_T(hot_case_dir, reg)
        j = int(np.argmax(T))
        hottest[reg] = dict(region=reg, T_degC=float(T[j] - KELVIN_C),
                            z_m=float(cc[j, 2]),
                            r_m=float(np.hypot(cc[j, 0], cc[j, 1])))
    win = max(hottest.values(), key=lambda d: d["T_degC"])
    z_hot = win["z_m"]
    prof, z_used = MR.radial_profile(hot_case_dir,
                                     ("core", "housing", "fluid"), z_hot)
    extra = {}
    for label, cdir in others.items():
        p, _ = MR.radial_profile(cdir, ("fluid",), z_hot)
        extra[label] = (p[0][1], p[0][2])
    locator = dict(
        hottest_solid_region=win["region"],
        hottest_solid_T_degC=win["T_degC"],
        per_region=hottest,
        stations_agree=bool(abs(hottest["core"]["z_m"]
                                - hottest["housing"]["z_m"]) < 1e-9),
        station_separation_m=float(abs(hottest["core"]["z_m"]
                                       - hottest["housing"]["z_m"])))
    return prof, z_used, z_hot, extra, locator


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


RADIAL_TITLE = "Radial temperature through the hottest cell"
RADIAL_CAPTION = (r"$P$ = 305 W $\cdot$ $U_\infty$ = 10 m s$^{-1}$ $\cdot$ "
                  r"$k$ = 40 / 167 / 0.026 W m$^{-1}$K$^{-1}$ $\cdot$ "
                  r"$r$ = 6--125 mm")


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
                          top=0.860, bottom=0.130)

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
        note = (r"mean slope $%.3f$ K mm$^{-1}$" "\n"
                + r"drop over region $" + (T_FMT % s["drop_K"]) + r"$ K" "\n"
                + r"straight-line fit $R^2 = %.4f$") \
            % (s["mean_slope_K_per_mm"], s["r_squared"])
        ax.text(0.5, 0.66, note, transform=ax.transAxes, fontsize=7.6,
                ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.30", fc="white",
                          ec=REGION_COLOUR[reg], lw=0.7, alpha=0.95),
                zorder=6)

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
             r"$%.3f$ K mm$^{-1}$ in the free stream"
             % (s["local_slope_first_K_per_mm"],
                s["local_slope_last_K_per_mm"]),
             transform=ax2.transAxes, fontsize=7.4, ha="center", va="top",
             bbox=dict(boxstyle="round,pad=0.30", fc="white", ec="#2e7d32",
                       lw=0.7, alpha=0.95))

    fig.suptitle(RADIAL_TITLE, fontsize=11.0, y=0.965)
    fig.text(0.5, 0.030, RADIAL_CAPTION, ha="center", fontsize=8.2,
             color="#333333")
    return fig


# ==========================================================================
# 4.  THE 16-TILE MONITOR REPLAY
# ==========================================================================

MONITOR_TITLE = "Temperature monitors, sixteen runs"
MONITOR_CAPTION = (r"16 runs $\cdot$ 100 samples each $\cdot$ "
                   r"core peak 107.7 $^\circ$C, housing 103.6 $^\circ$C")

#: Colour by POWER (her 1800Z spec: 4 colours, legend = these only); shade
#: by airspeed within each colour, faster air lighter, so the four lines of
#: one power read as one family and separate by their line-end tags.
POWER_COLOUR = {80: "#4c78a8", 155: "#2e7d32", 230: "#e08214", 305: "#b3261e"}
SPEED_ALPHA = {10: 1.0, 20: 0.8, 30: 0.6, 40: 0.45}


def _monitor_chart(ax, traces, powers, speeds, tag_x):
    """One shared-axis chart of her 1800Z spec: sixteen lines, colour by
    power, shade by airspeed, m/s tag at each right endpoint, an endpoint
    dot on every line -- no per-panel titles anywhere. Endpoints of
    different power groups can land within a degree of each other, so the
    TAGS (never the data) are dodged apart by a minimum spacing, sorted by
    endpoint height."""
    ends = []
    for p in powers:
        for u in speeds:
            it, mx = traces[(p, u)]
            colour = POWER_COLOUR[p]
            y_end = mx[-1] - KELVIN_C
            ax.plot(it, mx - KELVIN_C, lw=1.3, color=colour,
                    alpha=SPEED_ALPHA[u])
            ax.plot([it[-1]], [y_end], marker="o", ms=3.0,
                    color=colour, alpha=SPEED_ALPHA[u])
            ends.append([y_end, u, colour, SPEED_ALPHA[u]])
    ends.sort(key=lambda e: e[0])
    min_gap = 2.5
    tag_y = None
    for entry in ends:
        tag_y = entry[0] if tag_y is None else max(entry[0],
                                                   tag_y + min_gap)
        ax.text(tag_x, tag_y, "%d" % entry[1], fontsize=6.2,
                color=entry[2], alpha=max(entry[3], 0.7),
                va="center", ha="left")
    ax.set_ylim(20, 110)
    ax.set_xlim(left=0)
    ax.set_ylabel(r"$T$  $[^\circ\mathrm{C}]$", fontsize=8.5)
    ax.tick_params(labelsize=7.0)


def fig_monitor(core_traces, housing_traces, final_internal):
    """HER 1800Z DESIGN, retiring the per-panel grid ("The per-panel layout
    has failed three rounds; retire it"). One shared-axis chart: X
    iteration, Y temperature 20-110 C, sixteen lines, CORE only; housing on
    a second identical chart below (her stated alternative to a toggle).
    Colour by power, shade by airspeed within each colour; legend carries
    the four power colours only; every line ends in a dot with a small m/s
    tag at its right endpoint; the hottest line carries the endpoint text
    in her pattern ("305 W · 10 m/s · 107.7 C"). This layout cannot
    overprint: no per-panel titles exist."""
    from matplotlib.lines import Line2D

    fig, (ax_core, ax_house) = plt.subplots(
        2, 1, figsize=(11.0, 8.6), sharex=True)
    powers = sorted({p for p, _u in core_traces})
    speeds = sorted({u for _p, u in core_traces})
    span = max(core_traces[k][0][-1] for k in core_traces)
    tag_x = span * 1.012
    _monitor_chart(ax_core, core_traces, powers, speeds, tag_x)
    _monitor_chart(ax_house, housing_traces, powers, speeds, tag_x)
    for ax, name in ((ax_core, "core"), (ax_house, "housing")):
        ax.set_xlim(0, span * 1.06)
        ax.text(0.008, 0.965, name, transform=ax.transAxes, fontsize=8.5,
                ha="left", va="top", color="#333333")
    ax_house.set_xlabel("Iteration", fontsize=8.5)
    # The endpoint text, her pattern, on the hottest core line.
    hot = max(core_traces, key=lambda k: core_traces[k][1][-1])
    it, mx = core_traces[hot]
    ax_core.annotate(r"%d W $\cdot$ %d m s$^{-1}$ $\cdot$ %s $^\circ$C"
                     % (hot[0], hot[1], T_FMT % (mx[-1] - KELVIN_C)),
                     xy=(it[-1], mx[-1] - KELVIN_C),
                     xytext=(0.72, 0.955), textcoords="axes fraction",
                     fontsize=7.4, color="#333333", ha="left", va="top")
    handles = [Line2D([0], [0], color=POWER_COLOUR[p], lw=1.6,
                      label="%d W" % p) for p in powers]
    ax_core.legend(handles=handles, fontsize=7.4, loc="upper center",
                   bbox_to_anchor=(0.40, 0.97), framealpha=0.92, ncol=4)
    fig.suptitle(MONITOR_TITLE, fontsize=10.5, y=0.975)
    fig.text(0.5, 0.006, MONITOR_CAPTION, ha="center", fontsize=8.0,
             color="#333333")
    return fig


# ==========================================================================
# 5.  THE ASSUMPTION BEAT
# ==========================================================================

BEAT_TITLE = "Hand estimate versus coupled solve, 305 W"
BEAT_CAPTION = (r"hand/solve 3.54$\rightarrow$3.24 (duct), "
                r"2.03$\rightarrow$1.90 (flat), $U_\infty$ = 10--40 m s$^{-1}$")


def fig_assumption(rows):
    """The hand model against the solve.

    The comparison is made on the HOUSING peak, because that is the quantity
    the two hand correlations predict: both are surface-convection closures
    for the wall of the body, and neither carries the internal conduction that
    puts the core above it.  Comparing them against the core peak would credit
    the correlations with an overprediction they do not make."""
    speeds = sorted(HAND_MODEL)
    solved = {u: next(r["peak_housing_T_degC"] for r in rows
                      if r["power_W"] == 305 and r["airspeed_ms"] == u)
              for u in speeds}
    fig = plt.figure(figsize=(10.6, 4.9))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.05, 1.30], wspace=0.26,
                          left=0.070, right=0.980, top=0.840, bottom=0.180)
    fig.suptitle(BEAT_TITLE, fontsize=10.5, y=0.965)

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
    ax.set_ylabel(r"Peak housing temperature  $[^\circ\mathrm{C}]$")
    ax.set_title("Absolute temperature", fontsize=9.5)
    ax.legend(fontsize=7.0, loc="upper right")

    # --- panel 2: the overprediction factor, which shrinks with airspeed
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
    ax2.text(8.0, 1.04, "coupled solve, reference 1.000", color="#2f6f8f",
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
    ax2.set_title("Overprediction factor", fontsize=9.5)

    # THE THIRD PANEL IS GONE.  It carried two bars labelled EXTRAPOLATED --
    # the power that would reach 120 degC and the power that would reach
    # 200 degC at 20 m/s, both obtained by scaling the measured rise linearly
    # in power past the 305 W that is the highest power solved anywhere.  They
    # were withdrawn on 2026-09-01 by Sanaa's direction.  The two derived
    # powers are withdrawn from the bundle with them, so that no downstream
    # consumer can put back on a screen a number this file no longer draws.
    fig.text(0.5, 0.020, BEAT_CAPTION, ha="center", fontsize=8.2,
             color="#333333")
    return fig, dict(solved_degC=solved, duct_factor=dict(zip(speeds, duct)),
                     flat_factor=dict(zip(speeds, flat)),
                     solved_rise_at_20ms_K=float(solved[20] + KELVIN_C
                                                 - T_INF_K),
                     extrapolated_power_headroom="withdrawn 2026-09-01: the "
                                                 "120 degC and 200 degC power "
                                                 "bars scaled the measured "
                                                 "rise past the highest power "
                                                 "solved and are no longer "
                                                 "drawn or carried")


# ==========================================================================
# 6.  THE THREE FACTS, MEASURED HERE SO THEY SURVIVE A REGENERATION
#
# `reader`, `mesh.n_mesh_cells` and `mesh.geometry_guard` were written into the
# bundle by hand once.  A hand-written key does not survive the next run of
# this file, so they are MEASURED here instead: the cell counts from each
# region's own polyMesh header, and the geometry guard by actually running the
# frozen comparator's sha256 identity check over all sixteen cases rather than
# describing it.
# ==========================================================================

READER_TEXT = (
    "The peak core temperature is the maximum of T over the core "
    "internalField, read by `read_core_peak` beside this bundle. The peak "
    "housing temperature is Q1 of the frozen comparators -- the maximum of T "
    "over the housing internalField -- read by "
    "verification/runs/T-family/T23_runs/analyse_t23.py for the four 305 W "
    "points and verification/runs/T-family/T24_runs/analyse_t24.py for the "
    "other twelve. Those comparators also carry Q2, the temperature on the "
    "housing side of the housing_to_fluid interface averaged over the real "
    "polygon areas of that patch's faces. The margin to the limit is computed "
    "on the core, which is the hotter of the two solids at every point.")

GEOMETRY_GUARD_TEXT = (
    "Before any temperature is read, every case's polyMesh points in all "
    "three regions is asserted byte-identical by sha256 to the registered "
    "reference mesh (analyse_t24.py:366 points_digest, :378 mesh_identity). A "
    "missing points file refuses the grading pass rather than waiving the "
    "check, and a mismatch makes the affected rows NOT A RESULT.")


def measure_mesh():
    """Cell counts per region, MEASURED from each case's own polyMesh header
    and asserted identical across all sixteen operating points."""
    per_case = {}
    for p_w, u_ms, root, case in POINTS:
        cdir = os.path.join(root, case)
        per_case[case] = {r: int(MR.n_cells(cdir, r)) for r in MESH_REGIONS}
    first = per_case[POINTS[0][3]]
    same = all(v == first for v in per_case.values())
    if not same:
        refuse("the sixteen cases do not carry the same cell counts: %r"
               % per_case)
    return dict(n_mesh_cells=int(sum(first.values())),
                cells_by_region=first,
                n_regions=len(MESH_REGIONS),
                cells_source="the nCells field of "
                             "constant/<region>/polyMesh/owner, read in every "
                             "one of the sixteen cases",
                identical_across_operating_points=bool(same))


def measure_geometry_guard():
    """RUN the frozen comparator's mesh-identity check over all sixteen cases
    rather than describe it, and report what it found."""
    t24_cases = [c for _p, _u, root, c in POINTS if root == T24_ROOT]
    t23_cases = [c for _p, _u, root, c in POINTS if root == T23_ROOT]
    ok24, _d24, _ref = A24.mesh_identity(T24_ROOT, t24_cases)
    ok23, _d23, _r2 = A24.mesh_identity(T23_ROOT, t23_cases,
                                        ref_root=T23_ROOT)
    ok = dict(ok24)
    ok.update(ok23)
    n_pairs = len(ok) * len(MESH_REGIONS)
    if not all(ok.values()):
        bad = sorted(k for k, v in ok.items() if not v)
        return dict(text=GEOMETRY_GUARD_TEXT, all_identical=False,
                    n_cases=len(ok), n_region_case_pairs=n_pairs,
                    mismatched_cases=bad,
                    result="NOT A RESULT for %d of %d cases: the registered "
                           "identity claim is false for them"
                           % (len(bad), len(ok)))
    return dict(text=GEOMETRY_GUARD_TEXT, all_identical=True,
                n_cases=len(ok), n_region_case_pairs=n_pairs,
                mismatched_cases=[],
                result="all %d cases byte-identical in fluid, housing and "
                       "core -- %d of %d region-case pairs"
                       % (len(ok), n_pairs, n_pairs))


def measure_radiation():
    """`radiation neglected` is a MEASURED switch, not a remembered one."""
    out, cdir = {}, os.path.join(T23_ROOT, "T23_P305_U10")
    for reg in MESH_REGIONS:
        p = os.path.join(cdir, "constant", reg, "radiationProperties")
        if not os.path.isfile(p):
            refuse("no %s -- the radiation assumption cannot be measured and "
                   "is not asserted from memory" % p)
        txt = open(p).read()
        m = re.search(r"radiationModel\s+(\w+)\s*;", txt)
        s = re.search(r"^\s*radiation\s+(\w+)\s*;", txt, re.M)
        if not m or not s:
            refuse("%s carries no radiation/radiationModel pair" % p)
        out[reg] = dict(radiation=s.group(1), radiationModel=m.group(1))
    off = all(v["radiation"] == "off" and v["radiationModel"] == "none"
              for v in out.values())
    return dict(per_region=out, radiation_off_everywhere=bool(off))


# ==========================================================================
# 7.  THE ASSUMPTIONS BOX
# Every limitation here is about the PHYSICS, and every one of them stays.
# ==========================================================================

def build_assumptions(mesh, guard, rad, radial_locator):
    return [
        dict(heading="Single grid",
             text="One mesh level: %d cells across %d regions. "
                  "A discretisation error bar needs three grids. "
                  "No numerical uncertainty is quoted for any row."
                  % (mesh["n_mesh_cells"], mesh["n_regions"]),
             measured=True),
        dict(heading="Steady points only",
             text="Each of the sixteen points is a separate converged steady "
                  "state. Warm-up time and response to a load change are "
                  "outside this result.",
             measured=True),
        dict(heading="Radiation neglected",
             text="Radiation is off in all three regions. Heat leaves the "
                  "body by conduction and forced convection alone. "
                  "The real part has a radiative path; it is not represented.",
             measured=bool(rad["radiation_off_everywhere"])),
        dict(heading="Representative geometry and materials",
             text="The body is a representative motor-in-duct wedge. "
                  "Conductivities are constant: 40, 167 and 0.026 W/mK for "
                  "core, housing and air. It is not a particular product.",
             measured=False),
        dict(heading="Turbulence is modelled, not resolved",
             text="The air side uses the k-omega SST closure. Convective "
                  "heat transfer carries that model's error. No model-form "
                  "uncertainty is quoted.",
             measured=True),
        dict(heading="The peak is in the core",
             text="The hottest solid cell is in the %s at %s degC. "
                  "That is %s K above the housing peak. "
                  "Margin to the 200 degC limit is computed on the core."
                  % (radial_locator["hottest_solid_region"],
                     T_FMT % radial_locator["hottest_solid_T_degC"],
                     T_FMT % (radial_locator["hottest_solid_T_degC"]
                              - radial_locator["per_region"]["housing"]
                              ["T_degC"])),
             measured=True),
        dict(heading="Mesh identity is checked, not assumed",
             text=guard["result"][0].upper() + guard["result"][1:] + ".",
             measured=True),
    ]


ASSUMPTIONS_WRAP = 118          # characters; measured against the 9.6 in width


def _wrap(text, width=ASSUMPTIONS_WRAP):
    out, line = [], ""
    for word in text.split():
        if line and len(line) + len(word) + 1 > width:
            out.append(line)
            line = word
        else:
            line = (line + " " + word).strip()
    out.append(line)
    return out


def fig_assumptions(items):
    """One box, one heading per limitation, and the box is sized from the text
    rather than guessed at -- an item that runs off the bottom of its own frame
    is an item a reader does not read."""
    wrapped = [_wrap(it["text"]) for it in items]
    head_h, line_h, gap_h = 0.026, 0.0265, 0.028
    total = sum(head_h + line_h * len(w) + gap_h for w in wrapped)
    top = 0.885
    fig = plt.figure(figsize=(9.6, 6.6))
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    ax.axis("off")
    ax.set_title("What this result assumes", fontsize=12.5, pad=-4, y=0.945)
    y = top
    for it, w in zip(items, wrapped):
        ax.text(0.048, y, LS.bold(LS.tex_text(it["heading"])), fontsize=9.6,
                va="top", ha="left", color="#1a1a1a")
        ax.text(0.048, y - head_h, "\n".join(w), fontsize=8.2, va="top",
                ha="left", color="#333333", linespacing=1.42)
        y -= head_h + line_h * len(w) + gap_h
    bottom = top - total - 0.012
    if bottom < 0.02:
        refuse("the assumptions box overflows its own frame by %.3f of the "
               "page -- widen the figure rather than drop an assumption"
               % (0.02 - bottom))
    ax.add_patch(Rectangle((0.028, bottom), 0.944, top - bottom + 0.045,
                           fill=False, ec="#999999", lw=0.8,
                           transform=ax.transAxes))
    return fig


# ==========================================================================
# 8.  THE SHEET TEXT, and THE STATEMENTS OF FACT.
#
# The figure standard of 2026-09-01 moves every explanation out of the figure
# and into the sheet beside it, one compact paragraph per figure.  The
# paragraphs are built here so they say what the figure actually drew.
# ==========================================================================

def sheet_text(mapmeta, stats, fin, locator):
    return {
        "actA_map_table":
            "The shading is the peak temperature in the core, which is the "
            "hottest solid at every point. The table carries the housing peak "
            "beside it and the difference between them, and the margin to the "
            "200 degC limit is taken from the core because that is the "
            "smaller of the two margins. The uncertainty column is empty for "
            "every row: one grid admits no discretisation error bar, and none "
            "is estimated, interpolated or borrowed.",
        "actA_envelope":
            "One curve per dissipated power, each joining the four solved "
            "airspeeds. The double-headed arrow is the margin from the "
            "hottest solved point to the 200 degC limit, a measured "
            "temperature difference and not a numerical error bar; the "
            "sixteen points ran on one grid, so no grid-refinement band "
            "exists and none is drawn.",
        "actA_radial_profile":
            "The radius axis is broken at the two material interfaces because "
            "the housing wall is 3.5 mm of a 118 mm span and vanishes on a "
            "single common axis; each panel stays linear in radius and every "
            "marker is one computational cell. The core carries a volumetric "
            "heat source and the air carries a thermal boundary layer, so "
            "both curve and the single slope printed for each is a region "
            "average rather than a local gradient. Only the housing wall is "
            "straight.",
        "actA_monitor_replay":
            "Every trace is the run's own monitor output, sampled every 100 "
            "iterations and shown unchanged: the core monitors on the upper "
            "chart, the housing monitors on the identical chart below (her "
            "18:00Z single-chart design; the per-panel grid is retired). "
            "The housing monitor scans the housing cells and the faces "
            "bounding them, so its settled value sits %.4f K above the "
            "housing cell-only peak in the table; both are real readings "
            "of the same solution."
            % fin["offset_K"],
        "actA_assumption_beat":
            "Both hand correlations are surface-convection closures for the "
            "wall, so they are compared against the housing peak, which is "
            "what they predict. Each overpredicts the temperature rise, most "
            "at the lowest airspeed, and the overprediction shrinks as "
            "airspeed rises. The panel that scaled the measured rise into a "
            "power headroom beyond the highest power solved was withdrawn on "
            "2026-09-01.",
        "actA_assumptions":
            "Every limitation on this sheet is about the physics of the run "
            "and every one of them still applies to the numbers on the other "
            "sheets.",
    }


def facts(mesh, controls, anchors):
    """The statements of fact for the header and the sheets.

    TWO OF THE FOUR SENTENCES AS DICTATED ON 2026-09-01 WERE MEASURABLY FALSE
    and are not written here in that form.

      * "a planted 0.001 K perturbation" -- the magnitude is 1.234e-03 K in
        every control, imported from the frozen comparator.  0.001 K is that
        figure at one significant figure and the readers were never asked for
        it.
      * "agreement to 1e-5 K" -- the largest anchor residual is 3.7361e-05 K,
        3.7 times that.  "Better than 1e-4 K" is true and is what is written.

    The count moved too: there are now FOUR readers under control, not three,
    because the core reader is new.  Every sentence below is built from the
    measurements in this run rather than transcribed."""
    n_ctl = len(controls)
    mags = sorted({c["planted_K"] for c in controls.values()})
    if len(mags) != 1:
        refuse("the controls did not all plant one magnitude: %r" % mags)
    worst = max(a["abs_diff_degC"] for a in anchors)
    # The replacement sentence is CHECKED before it is written.  A claim of
    # "better than 1e-4 K" that has not been measured against 1e-4 K is the
    # same kind of unverified sentence as the one it replaces.
    if not (worst < 1.0e-4):
        refuse("the largest anchor residual is %.6e K, so the sentence "
               "'agreement better than 1e-4 K' is NOT true and is not written"
               % worst)
    return dict(
        solver="Solver: OpenFOAM chtMultiRegionSimpleFoam, steady conjugate "
               "heat transfer, k-omega SST.",
        scale="%d operating points solved on this geometry, %s cells."
              % (len(POINTS), format(mesh["n_mesh_cells"], ",")),
        instrument_checks="Instrument checks: %d readers each detected a "
                          "planted %.3e K perturbation."
                          % (n_ctl, mags[0]),
        anchor_check="Anchor check: %d values reproduced from the fields on "
                     "disk against the frozen record, agreement better than "
                     "1e-4 K." % len(anchors),
        anchor_check_largest_residual_K=worst,
        corrections_to_the_dictated_wording=[
            "'a planted 0.001 K perturbation' -> the measured magnitude is "
            "%.3e K, imported from the frozen T24 comparator and never "
            "redefined." % mags[0],
            "'three readers' -> there are %d readers under planted-zero "
            "control, the core reader having been added on 2026-09-01."
            % n_ctl,
            "'agreement to 1e-5 K' -> the largest residual measured is "
            "%.4e K, which is %.1f times 1e-5; 'better than 1e-4 K' is true "
            "and defensible." % (worst, worst / 1.0e-5),
        ])


# ==========================================================================
# MAIN
# ==========================================================================

def main():
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

    c0 = planted_core_control(hot_dir)
    controls["peak_core_temperature_reader"] = c0
    print("   peak core-temperature reader: planted %.6e K, read %.6e K, "
          "floor %.0e K" % (PLANT, c0["read_K"], c0["detection_floor_K"]))

    c1 = A24.planted_zero_control(hot_dir,
                                  "peak housing-temperature field reader",
                                  A24.read_Q1, A24.plant_Q1)
    controls["peak_housing_temperature_field_reader"] = dict(
        passed=bool(c1["passed"]), planted_K=PLANT,
        read_K=float(c1["at_plant"]), detection_floor_K=float(c1["floor"]),
        n_cells_planted=int(c1["n_planted"]))
    print("   peak housing-temperature reader: planted %.6e K, read %.6e K, "
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

    print("\n== THE THREE FACTS, MEASURED")
    mesh = measure_mesh()
    guard = measure_geometry_guard()
    rad = measure_radiation()
    mesh["geometry_guard"] = GEOMETRY_GUARD_TEXT
    mesh["geometry_guard_result"] = guard["result"]
    print("   mesh cells  %d across %d regions %r"
          % (mesh["n_mesh_cells"], mesh["n_regions"], mesh["cells_by_region"]))
    print("   guard       %s" % guard["result"])
    print("   radiation   off everywhere: %s"
          % rad["radiation_off_everywhere"])
    if not guard["all_identical"]:
        refuse("the registered mesh-identity claim is false for %r"
               % guard["mismatched_cases"])

    print("\n== FIGURES")
    fig, mapmeta = fig_map_table(rows)
    save(fig, "actA_map_table")
    print("   map table   core %.4f to %.4f degC, housing %.4f to %.4f degC"
          % (mapmeta["vmin"], mapmeta["vmax"], mapmeta["housing_min"],
             mapmeta["housing_max"]))

    fig, series = fig_envelope(rows)
    save(fig, "actA_envelope")
    hot = min(rows, key=lambda r: r["margin_to_limit_K"])
    print("   envelope    worst core margin %+.4f K at %d W / %d m/s "
          "(housing would have said %+.4f K)"
          % (hot["margin_to_limit_K"], hot["power_W"], hot["airspeed_ms"],
             hot["housing_margin_to_limit_K"]))

    others = {str(u): os.path.join(T23_ROOT, "T23_P305_U%d" % u)
              for u in (20, 30, 40)}
    prof, z_used, z_hot, extra, locator = build_radial(hot_dir, others)
    stats = {reg: region_stats(r, T) for reg, r, T, _z in prof}
    fig = fig_radial(prof, z_used, extra, stats)
    save(fig, "actA_radial_profile")
    print("   radial      hottest solid cell is in the %s at %.4f degC; the "
          "core and housing stations agree: %s"
          % (locator["hottest_solid_region"], locator["hottest_solid_T_degC"],
             locator["stations_agree"]))
    for reg in ("core", "housing", "fluid"):
        s = stats[reg]
        print("   radial %-8s slope %+9.4f K/mm  R2 %.5f  local %+9.3f -> "
              "%+8.4f K/mm" % (reg, s["mean_slope_K_per_mm"], s["r_squared"],
                               s["local_slope_first_K_per_mm"],
                               s["local_slope_last_K_per_mm"]))

    traces = {}
    core_traces = {}
    for p_w, u_ms, root, case in POINTS:
        traces[(p_w, u_ms)] = read_monitor(monitor_path(root, case))
        it, mx, _mn = read_monitor(core_monitor_path(root, case))
        core_traces[(p_w, u_ms)] = (it, mx)
    hot_final_mon = traces[(305, 10)][1][-1] - KELVIN_C
    # The monitor scans the HOUSING region and its bounding faces, so it is
    # compared against the HOUSING cell-only peak.  Comparing it against the
    # core peak -- now the value in `peak_T_degC` -- would subtract two
    # different regions and report the difference as an instrument offset.
    hot_internal = next(r["peak_housing_T_degC"] for r in rows
                        if r["power_W"] == 305 and r["airspeed_ms"] == 10)
    fin = dict(monitor_degC=float(hot_final_mon),
               internal_cells_degC=float(hot_internal),
               region="housing",
               offset_K=float(hot_final_mon - hot_internal))
    housing_traces = {k: (v[0], v[1]) for k, v in traces.items()}
    fig = fig_monitor(core_traces, housing_traces, fin)
    save(fig, "actA_monitor_replay")
    print("   monitors    2 shared-axis charts, %d samples each, housing "
          "monitor peak "
          "%.4f degC against housing cell-only peak %.4f degC (offset %.4f K)"
          % (len(traces[(305, 10)][0]), fin["monitor_degC"],
             fin["internal_cells_degC"], fin["offset_K"]))

    fig, beat = fig_assumption(rows)
    save(fig, "actA_assumption_beat")
    print("   assumption  duct %s  flat %s (extrapolated headroom panel "
          "withdrawn)"
          % (["%.3f" % beat["duct_factor"][u] for u in (10, 20, 30, 40)],
             ["%.3f" % beat["flat_factor"][u] for u in (10, 20, 30, 40)]))

    assumptions = build_assumptions(mesh, guard, rad, locator)
    fig = fig_assumptions(assumptions)
    save(fig, "actA_assumptions")
    print("   assumptions %d items, every physics limitation kept"
          % len(assumptions))

    # ------------------------------------------------------------------ CSV
    with open(os.path.join(HERE, "actA_map_table.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["power_W", "airspeed_m_per_s", "peak_core_temperature_degC",
                    "peak_housing_temperature_degC", "core_above_housing_K",
                    "rise_above_inlet_K", "margin_to_200C_limit_on_core_K",
                    "margin_to_120C_design_on_core_K",
                    "margin_to_200C_limit_on_housing_K",
                    "numerical_uncertainty_K"])
        for r in rows:
            w.writerow(["%d" % r["power_W"], "%d" % r["airspeed_ms"],
                        "%.6f" % r["peak_core_T_degC"],
                        "%.6f" % r["peak_housing_T_degC"],
                        "%.6f" % r["core_above_housing_K"],
                        "%.6f" % r["rise_above_inlet_K"],
                        "%.6f" % r["margin_to_limit_K"],
                        "%.6f" % r["margin_to_design_K"],
                        "%.6f" % r["housing_margin_to_limit_K"],
                        UNCERTAINTY_TEXT])

    with open(os.path.join(HERE, "actA_envelope.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["power_W", "airspeed_m_per_s",
                    "peak_core_temperature_degC",
                    "margin_to_200C_limit_on_core_K", "limit_degC",
                    "design_isotherm_degC"])
        for r in rows:
            w.writerow(["%d" % r["power_W"], "%d" % r["airspeed_ms"],
                        "%.6f" % r["peak_core_T_degC"],
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
                    "coupled_solve_housing_degC",
                    "overprediction_factor_duct",
                    "overprediction_factor_flat_plate"])
        for u in sorted(HAND_MODEL):
            w.writerow(["%d" % u, "305", "%.1f" % HAND_ABS_C[u][0],
                        "%.1f" % HAND_ABS_C[u][1],
                        "%.6f" % beat["solved_degC"][u],
                        "%.3f" % beat["duct_factor"][u],
                        "%.3f" % beat["flat_factor"][u]])

    # ----------------------------------------------------------------- JSON
    # NOTE ON PRECISION.  Every number below keeps its full read precision.
    # The 0.1 degC display rule is applied where a number is DRAWN, not where
    # it is recorded, and it is never applied to instrument evidence: a
    # planted magnitude of 1.234e-03 K or an anchor residual of 3.7e-05 K
    # rounded to 0.1 K is 0.0 and has stopped being evidence.
    out = dict(
        map_rows=rows,
        anchor_checks=anchors,
        anchor_check_method=dict(
            quantity=ANCHOR_QUANTITY,
            gate_K=ANCHOR_GATE_K,
            gate_status="REGISTERED; repaired the instrument, not the "
                        "threshold",
            differenced="unrounded on both sides",
            repaired="2026-09-01: the difference used to be taken between the "
                     "measurement ROUNDED TO FOUR DECIMALS and a four-decimal "
                     "expectation, which manufactures an exact zero out of "
                     "arithmetic instead of agreement. The residuals reported "
                     "here are real.",
            largest_residual_K=max(a["abs_diff_degC"] for a in anchors)),
        reader=READER_TEXT,
        mesh=mesh,
        geometry_guard=guard,
        radiation=rad,
        assumptions=assumptions,
        solver=dict(
            line="Solver: OpenFOAM chtMultiRegionSimpleFoam, steady "
                 "conjugate heat transfer, k-omega SST.",
            application="chtMultiRegionSimpleFoam",
            regime="steady", turbulence_model="kOmegaSST",
            coupling="conduction and turbulent forced convection, coupled at "
                     "the solid/fluid interfaces"),
        map_colour_range_degC=dict(minimum=mapmeta["vmin"],
                                   maximum=mapmeta["vmax"],
                                   region="core",
                                   quantity="peak core temperature"),
        map_colour_range_housing_degC=dict(minimum=mapmeta["housing_min"],
                                           maximum=mapmeta["housing_max"],
                                           region="housing"),
        envelope=dict(series_degC={str(k): v for k, v in series.items()},
                      quantity="peak core temperature",
                      limit_degC=LIMIT_C, design_isotherm_degC=DESIGN_C,
                      worst_margin_K=hot["margin_to_limit_K"],
                      worst_margin_computed_on="core",
                      worst_margin_on_housing_K=hot[
                          "housing_margin_to_limit_K"],
                      worst_point=dict(power_W=hot["power_W"],
                                       airspeed_ms=hot["airspeed_ms"]),
                      uncertainty_band="NONE - single grid, no "
                                       "grid-refinement error estimate "
                                       "exists; the drawn interval is the "
                                       "measured margin to the 200 degC "
                                       "limit"),
        radial=dict(axial_station_m=z_used,
                    hottest_solid_cell_axial_m=z_hot,
                    hottest_solid_cell=locator,
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
        figure_sheet_text=sheet_text(mapmeta, stats, fin, locator),
        display_precision=dict(
            temperatures_in_figures="0.1 degC, until the grid triple lands",
            not_applied_to="the JSON and CSV record, planted-control "
                           "magnitudes and anchor residuals -- rounding "
                           "instrument evidence to 0.1 K destroys it",
            applies_from="2026-09-01"),
        statements_of_fact=facts(mesh, controls, anchors),
    )
    with open(os.path.join(HERE, "actA_screen_data.json"), "w") as fh:
        json.dump(out, fh, indent=2, sort_keys=True, default=float)
    print("\n== WROTE actA_screen_data.json and five CSV files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
