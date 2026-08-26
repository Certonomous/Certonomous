#!/usr/bin/env python3
"""T5 FIGURE DIGITISER -- A REFERENCE-PRODUCING INSTRUMENT, ON THE GRADING PATH.

WHAT THIS IS
------------
Meinders 1998 has NO tabulated appendix and the PDF is an IMAGE-ONLY 1-bit scan
(measured: 300 ppi, bpc=1, CCITT G4; `pdftotext` returns ZERO non-whitespace
characters over all 281 pages, against a control of 121,044 characters from
another PDF read by the same binary in the same session).  Every reference value
T5 grades against must therefore be DIGITISED FROM A FIGURE.

    THE DIGITISER PRODUCES THE REFERENCE.  A REFERENCE-PRODUCING INSTRUMENT IS A
    MEASUREMENT INSTRUMENT, AND IT TAKES THE FULL DISCIPLINE WITH NO DISCOUNT FOR
    BEING "JUST" A FIGURE READER.

So: frozen by sha at the pre-registration commit, on the grading path; NO `assert`
carries a refusal, guard, control or gate (`python3 -O` deletes them -- L-332);
every refusal is `raise`/`sys.exit(2)` and is DRIVEN under `-O` in the selftest and
shown to fire identically; and `scripts/check_assert_guards.py --require-clean`
requires zero `ast.Assert` nodes in this file.

`digitise_t3_secondary.py:190,191` carry T3's axis calibration in two `assert`
statements and are Class A in this territory's `-O` inventory.  They are FROZEN and
are NOT repaired (the 2026-08-25T22:48Z bound is forward-only).  T3 is the
precedent for WHAT A DIGITISER IS.  It is not the precedent for HOW TO GUARD ONE.

THE PLANTED-CALIBRATION CONTROL, AND WHY IT IS A RASTER
------------------------------------------------------
A synthetic figure of known values, digitised blind, refusing above a registered
tolerance -- but the control figure MUST TRAVEL THE SAME CHANNEL AS THE REAL ONE.

    A clean vector-graphics control would exercise a channel the real artifact does
    not use.  That is this lab's single most repeated defect: `blockMesh` never
    reads `0/`; a launcher selftest passed with a FAKE SOLVER on PATH; a mesh dry
    run never touched `0.orig/`.  EVERY ONE EXERCISED THE CHANNEL ITS AUTHOR WAS
    THINKING ABOUT RATHER THAN THE CHANNEL THAT CONSUMES THE ARTIFACT.

The channel was MEASURED on the real page, not assumed (`pdfimages -list`, PDF
page 162 = Fig. 5.45):

    width 1926  height 2816  color gray  comp 1  BPC 1  enc CCITT  301 x 300 ppi

and on the rendered raster: 3 distinct grey levels, 99.988 % of pixels exactly 0
or 255, blank-margin standard deviation 0.0.  THE SCAN IS BITONAL, NOT GREYSCALE.

So the control raster is rendered at 300 dpi, hard-thresholded to 1 bit, and
round-tripped through CCITT Group 4 -- the same encoder the thesis PDF uses.
G4 is lossless; THE LOSSY STEP IS THE 1-BIT THRESHOLD, and that is the step the
control has to reproduce.  Resolution and degradation are stated in the output so
the control's own fidelity is a measured claim rather than an assumption.

WHAT IT REFUSES ON
------------------
  * fewer tick anchors than registered            -> exit 2
  * tick spacing not uniform to TICK_UNIFORM_TOL  -> exit 2
  * axis line not coincident with the first tick  -> exit 2
  * linear axis fit residual over FIT_RESID_TOL   -> exit 2
  * a control error over CONTROL_TOL              -> exit 2  (the planted control)

TWO UNCERTAINTIES, NEVER MERGED
-------------------------------
Meinders states ~5 % on local `h` mid-face (five faces) and ~10 % at the edges --
read from the RENDERED IMAGE of printed p. 59, not from OCR.  That is the
EXPERIMENTAL uncertainty.  The DIGITISATION uncertainty is a SECOND, INDEPENDENT
source that WE introduce and that a tabulated-appendix rung does not have.  This
file emits the digitisation component as a MEASURED number from the planted
control.  It never combines them: the combination rule belongs to the
pre-registration, and an uncertainty absorbed into another is an uncertainty
nobody can audit later.

AMENDMENT 2026-08-26 (PRE-FIRST-COMPUTE) -- CLOSED-FRAME, INWARD-TICK, LINE-SERIES
---------------------------------------------------------------------------------
The frozen instrument (blob e55d6208) REFUSED all three registered figures
(5.45: "x-axis line at y=53 does not coincide with the last y tick at NONE";
5.37 / 5.39: "y-axis line at x=1043 does not coincide with the first x tick at
1054.5").  Read from the rendered pages: the thesis plots are CLOSED BOX FRAMES
with ticks pointing INWARD, and 5.37 / 5.39 are five LINE-CONNECTED symbol series
over a path A|B|C|D with full-height partition lines at B and C.  The refusals
were CORRECT -- the frame finder took a frame line for an axis and the outward
tick search found nothing -- and every original arm is kept unchanged below.

What is ADDED (nothing above this note is edited; the open-frame path, its raster
control and its selftest arms are untouched):

  * `find_frame`        closed frame = the two outermost long horizontal and the
                        two outermost long vertical ink lines; internal
                        full-height vertical lines are the path partitions.
  * `find_inward_ticks` ticks are runs of ink leaving the LEFT frame line to the
                        RIGHT and the BOTTOM frame line UPWARD.
  * `pair_labels`       AXIS CALIBRATION IS DERIVED FROM TICK LABELS READ AGAINST
                        TICK POSITIONS: every text cluster in the label band left
                        of / below the frame must pair with the nearest anchor
                        candidate (frame edge, tick, partition line) within
                        LABEL_PAIR_TOL_PX; refuses on an unpairable label, on two
                        labels sharing an anchor, on a paired tick shorter than an
                        unpaired one, and on a paired count that is not the
                        registered count.  Label VALUES stay registered, never
                        inferred from the image; tesseract is run on each label
                        crop and a clean numeric read that DISAGREES with the
                        registered value refuses (an unreadable crop is recorded
                        as unread and does not).
  * `find_hollow_markers` / `classify_marker`
                        SERIES SEPARATION RULE, stated: a marker is a group of
                        enclosed white holes (the interior of a hollow symbol,
                        split in two by the series line) within MARKER_PX of each
                        other; its ink window is correlated against synthetic
                        ring templates (circle, square, up-triangle) at the
                        registered size, and it is assigned to the series whose
                        template correlates best PROVIDED the margin over the
                        runner-up is >= CLASSIFY_MARGIN; otherwise it is
                        UNCLASSIFIED and dropped (reported, never used).  The
                        thesis figures carry one symbol per series, so the
                        symbol IS the series.  Solid symbols (+, x) are
                        classified by axis/diagonal ink fractions; a solid blob
                        that fits neither, or a hole group larger than
                        MARKER_PX * MERGED_SIZE_FRAC, is MERGED and dropped.
  * `series_value_at`   POINT figures: the series marker nearest the registered
                        abscissa, refused if none within ABSCISSA_TOL;
                        PATH figures: linear interpolation between the series'
                        markers, refused if any gap along the path exceeds
                        PATH_MAX_GAP or a partition holds fewer than
                        PATH_MIN_PTS markers; the value is the path-weighted mean
                        over the central 80 % of each partition (§7.1) with the
                        full-partition mean REPORTED beside it.
  * `run_closed_control` A SECOND PLANTED CONTROL in the closed-frame,
                        inward-tick, line-connected multi-series style, rendered
                        from known values and degraded through the SAME measured
                        channel (skew, ink spread, 1-bit threshold, speckle,
                        CCITT G4).  Its max error as a fraction of span is the
                        digitisation increment for 5.37 / 5.39; the original
                        raster control remains the increment for 5.45.  BOTH must
                        PASS.  A mis-anchored closed frame is the planted negative
                        control and must FIRE under `python3` and `python3 -O`.
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

# ---------------------------------------------------------------------------
# REGISTERED CONSTANTS -- fixed here, before any figure was digitised.
# ---------------------------------------------------------------------------
RENDER_DPI = 300                  # matches the embedded scan's 301 x 300 ppi
SCAN_BPC = 1                      # measured: bpc=1, bitonal
SCAN_ENCODER = "group4"           # measured: enc=ccitt (G4)
THRESHOLD = 128                   # 1-bit hard threshold, the lossy step
TICK_UNIFORM_TOL = 0.04           # max relative departure from uniform spacing
FIT_RESID_TOL_PX = 2.0            # max residual of the pixel->data linear fit
AXIS_TICK_COINCIDE_PX = 6.0       # axis line must sit within this of tick 1
CONTROL_TOL_FRAC = 0.02           # planted control must recover within 2 % of span
MIN_MARKER_PX = 12                # a blob smaller than this is scan speckle
# ---- DEGRADATION, MEASURED ON THE REAL PAGE, NOT GUESSED -------------------
# `pdfimages -list` on PDF page 162 gives 1926x2816, bpc=1, enc=ccitt, 301x300
# ppi.  On the rendered raster, measured directly:
#   * SKEW      the densest axis line in the figure region drifts 0.001755 px/px
#               over 1698 px  ->  0.1006 degrees
#   * SPECKLE   2478 connected components, of which 33 are <=1 px and 109 <=4 px
#               (4.40 % of components)
#   * INK       axis-line thickness 4-12 px where a vector render would give ~2
# The control reproduces all three.  A clean render would reproduce NONE of them
# and would exercise a channel the real artifact does not use.
SKEW_DEG = 0.1006                 # measured, page 162
SPECKLE_FRAC = 0.0440             # measured: fraction of components that are <=4 px
INK_DILATE_PX = 1                 # measured: real strokes run 4-12 px, render ~2


def refuse(msg):
    """The replacement form for `assert`.  Unaffected by `python3 -O`."""
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


# ---------------------------------------------------------------------------
# The control raster: synthesise -> render 300 dpi -> 1-bit -> CCITT G4
# ---------------------------------------------------------------------------
def build_control_raster(path, xs, ys, xlim, ylim, xticks, yticks):
    """Render a Fig-5.45-shaped scatter with KNOWN values, then degrade it to the
    measured channel.  Returns a dict describing the degradation applied."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6.4, 4.2), dpi=RENDER_DPI)
    ax.scatter(xs, ys, marker="o", s=90, facecolors="none", edgecolors="black",
               linewidths=1.4)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)
    ax.tick_params(direction="out", length=7, width=1.4, labelsize=13)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_linewidth(1.4)
    fig.tight_layout()
    tmp_png = path + ".grey.png"
    fig.savefig(tmp_png, dpi=RENDER_DPI, facecolor="white")
    plt.close(fig)

    im = Image.open(tmp_png).convert("L")
    # ---- DEGRADE IN THE ORDER A REAL SCAN DEGRADES ------------------------
    # (a) SKEW: the page sits crooked on the platen, BEFORE thresholding.
    im = im.rotate(SKEW_DEG, resample=Image.BICUBIC, fillcolor=255)
    arr = np.array(im)
    # (b) INK SPREAD: toner/print bleed thickens strokes, before thresholding.
    if INK_DILATE_PX > 0:
        from scipy import ndimage as _nd
        dark = arr < THRESHOLD
        dark = _nd.binary_dilation(dark, iterations=INK_DILATE_PX)
        arr = np.where(dark, 0, arr).astype(np.uint8)
    bilevel = (arr >= THRESHOLD).astype(np.uint8) * 255
    # (c) SPECKLE: bitonal scanners emit isolated dark pixels.  Planted at the
    #     measured density, with a FIXED SEED so the control is reproducible.
    rng = np.random.default_rng(20260826)
    n_spk = int(SPECKLE_FRAC * 2478)
    hgt, wid = bilevel.shape
    # Speckle AREA is matched to the measurement, not invented: on the real page
    # 33 components are <=1 px and 109 are <=4 px.  Planting 4x4 BLOCKS (area 16)
    # instead of area<=4 specks made 17 of them survive the marker filter and the
    # control refused with "23 markers recovered, 6 planted" -- the control
    # catching a defect in the control, which is the right order for that to
    # happen in.
    for _ in range(n_spk):
        sy = int(rng.integers(0, hgt - 2)); sx = int(rng.integers(0, wid - 2))
        area = int(rng.integers(1, 5))          # 1..4 px, as measured
        if area == 1:
            bilevel[sy, sx] = 0
        elif area == 2:
            bilevel[sy, sx:sx + 2] = 0
        elif area == 3:
            bilevel[sy, sx:sx + 2] = 0; bilevel[sy + 1, sx] = 0
        else:
            bilevel[sy:sy + 2, sx:sx + 2] = 0
    bi = Image.fromarray(bilevel).convert("1")
    # round-trip through the SAME encoder the thesis PDF uses
    bi.save(path, format="TIFF", compression=SCAN_ENCODER)
    os.unlink(tmp_png)
    n_spk_out = n_spk
    reloaded = np.array(Image.open(path).convert("L"))
    levels = int(np.unique(reloaded).size)
    return dict(render_dpi=RENDER_DPI, bits_per_channel=SCAN_BPC,
                threshold=THRESHOLD, encoder=SCAN_ENCODER,
                skew_deg=SKEW_DEG, speckle_frac=SPECKLE_FRAC,
                ink_dilate_px=INK_DILATE_PX, speckle_blobs_planted=n_spk_out,
                raster_px=[int(reloaded.shape[1]), int(reloaded.shape[0])],
                distinct_grey_levels_after_roundtrip=levels)


# ---------------------------------------------------------------------------
# Digitisation
# ---------------------------------------------------------------------------
def load_bitonal(path):
    a = np.array(Image.open(path).convert("L"))
    return (a < THRESHOLD)          # True = ink


def find_axes(ink):
    """Longest fully-inked row and column = the x and y axis lines."""
    rows = ink.sum(axis=1)
    cols = ink.sum(axis=0)
    if rows.max() < 20 or cols.max() < 20:
        refuse("no axis line found: the raster carries almost no ink "
               "(max row %d px, max col %d px)" % (rows.max(), cols.max()))
    return int(np.argmax(rows)), int(np.argmax(cols))   # (xaxis_y, yaxis_x)


def find_ticks(ink, axis_y, axis_x):
    """Ticks stick OUT of the frame: below the x axis, left of the y axis."""
    # The search bands are CLIPPED TO THE FRAME.  Without the clip the x-tick
    # band runs left of the y axis and picks up the y-axis TICK LABELS, and the
    # y-tick band runs below the x axis and picks up the x labels.  Both produce
    # a plausible-looking anchor set that is silently wrong -- which is exactly
    # what the coincidence guard below is there to catch, and it did catch it.
    below = ink[axis_y + 3:axis_y + 14, axis_x:]
    xt = [v + axis_x for v in _runs(np.where(below.sum(axis=0) >= 6)[0])]
    left = ink[:axis_y + 1, max(0, axis_x - 14):max(1, axis_x - 3)]
    yt = _runs(np.where(left.sum(axis=1) >= 6)[0])
    return xt, yt


def _runs(idx):
    """Collapse consecutive pixel indices into run centres."""
    if len(idx) == 0:
        return []
    out, start, prev = [], idx[0], idx[0]
    for i in idx[1:]:
        if i - prev > 3:
            out.append((start + prev) / 2.0)
            start = i
        prev = i
    out.append((start + prev) / 2.0)
    return out


def calibrate(px, values, name):
    """Least-squares pixel->data map, with THREE refusals and no assert."""
    if len(px) != len(values):
        refuse("%s: found %d tick marks, %d registered anchor values -- the "
               "figure is not the registered one, or the tick finder is wrong. "
               "A calibration built on a mismatched anchor set is silently wrong."
               % (name, len(px), len(values)))
    d = np.diff(px)
    if len(d) >= 2:
        rel = float(np.max(np.abs(d - d.mean())) / max(d.mean(), 1e-9))
        if rel > TICK_UNIFORM_TOL:
            refuse("%s: tick spacing not uniform (max relative departure %.4f > "
                   "%.4f). A non-uniform tick set means the axis is not linear or "
                   "a tick was missed." % (name, rel, TICK_UNIFORM_TOL))
    A = np.vstack([np.asarray(px, dtype=float), np.ones(len(px))]).T
    coef, *_ = np.linalg.lstsq(A, np.asarray(values, dtype=float), rcond=None)
    resid_data = A @ coef - np.asarray(values, dtype=float)
    scale = abs(coef[0]) if abs(coef[0]) > 1e-12 else 1e-12
    resid_px = float(np.max(np.abs(resid_data)) / scale)
    if resid_px > FIT_RESID_TOL_PX:
        refuse("%s: linear fit residual %.3f px > %.3f px. The axis is not linear "
               "in pixels and a linear map would be wrong everywhere."
               % (name, resid_px, FIT_RESID_TOL_PX))
    return float(coef[0]), float(coef[1]), resid_px


def frame_margin_px(shape):
    """How far the frame lines can wander into the plot, DERIVED from the
    measured skew rather than chosen.

    A skewed axis line is not straight in raster coordinates: at SKEW_DEG it
    drifts `tan(skew) * length` pixels across the raster.  With a 4 px margin the
    control leaked the y axis (area 3002 px) and part of the x axis (area 536 px)
    into the marker set and refused with "8 markers recovered, 6 planted" -- the
    control catching an under-sized margin, which is what it is for.
    """
    drift = np.tan(np.radians(SKEW_DEG)) * float(max(shape))
    return int(np.ceil(drift)) + 4


def find_markers(ink, axis_y, axis_x):
    """Connected components inside the plot frame."""
    from scipy import ndimage
    m = frame_margin_px(ink.shape)
    inside = np.zeros_like(ink)
    inside[:axis_y - m, axis_x + m:] = ink[:axis_y - m, axis_x + m:]
    lab, n = ndimage.label(inside)
    out = []
    for i in range(1, n + 1):
        ys, xs = np.where(lab == i)
        if len(ys) < MIN_MARKER_PX:
            continue
        out.append((float(xs.mean()), float(ys.mean()), int(len(ys))))
    return out


def digitise(path, xticks, yticks):
    ink = load_bitonal(path)
    axis_y, axis_x = find_axes(ink)
    xt, yt = find_ticks(ink, axis_y, axis_x)
    if abs(xt[0] - axis_x) > AXIS_TICK_COINCIDE_PX if xt else True:
        refuse("the y-axis line at x=%d does not coincide with the first x tick "
               "at %s (tolerance %.1f px). Either the frame or the tick set was "
               "misidentified, and both make every extracted value wrong."
               % (axis_x, ("%.1f" % xt[0]) if xt else "NONE",
                  AXIS_TICK_COINCIDE_PX))
    if abs(yt[-1] - axis_y) > AXIS_TICK_COINCIDE_PX if yt else True:
        refuse("the x-axis line at y=%d does not coincide with the last y tick "
               "at %s (tolerance %.1f px)."
               % (axis_y, ("%.1f" % yt[-1]) if yt else "NONE",
                  AXIS_TICK_COINCIDE_PX))
    ax_, bx_, rx = calibrate(xt, xticks, "x-axis")
    # THE Y AXIS IS INVERTED IN PIXEL SPACE AND THIS IS NOT A DETAIL.
    # `_runs` returns tick centres in ASCENDING PIXEL ROW, i.e. TOP FIRST, while
    # `yticks` is registered in ASCENDING DATA ORDER, i.e. BOTTOM FIRST.  Pairing
    # them as given maps the top tick to the smallest value and REFLECTS EVERY
    # EXTRACTED POINT ABOUT THE AXIS MIDPOINT.
    #     THE PLANTED RASTER CONTROL CAUGHT EXACTLY THIS, ON THE FIRST RUN:
    #     truth 28.70 came back as 61.37, and 90 - 28.70 = 61.30.  The x axis,
    #     which is not inverted, recovered to 0.097 % of span in the same run --
    #     so a control that only checked x would have reported success.
    # The reversal is explicit here, and the sign guard below makes it checkable
    # rather than trusted.
    ay_, by_, ry = calibrate(yt, list(reversed(yticks)), "y-axis")
    if ay_ >= 0.0:
        refuse("y-axis calibration has a non-negative scale (%.6g data per px). "
               "In an image, data y must DECREASE as the pixel row increases; a "
               "non-negative scale means the anchor order is wrong and every "
               "extracted value would be reflected about the axis midpoint."
               % ay_)
    pts = []
    for px, py, area in find_markers(ink, axis_y, axis_x):
        pts.append(dict(px=px, py=py, area_px=area,
                        x=ax_ * px + bx_, y=ay_ * py + by_))
    return dict(
        axis_pixels=dict(xaxis_y=axis_y, yaxis_x=axis_x),
        tick_anchors_px=dict(x=[float(v) for v in xt], y=[float(v) for v in yt]),
        tick_anchors_data=dict(x=list(xticks), y=list(yticks)),
        calibration=dict(x=[ax_, bx_], y=[ay_, by_],
                         max_resid_px=dict(x=rx, y=ry)),
        points=pts)


# ---------------------------------------------------------------------------
# THE PLANTED CALIBRATION CONTROL
# ---------------------------------------------------------------------------
CONTROL_XLIM = (0.0, 6000.0)
CONTROL_YLIM = (0.0, 90.0)
CONTROL_XTICKS = [0.0, 2000.0, 4000.0, 6000.0]
CONTROL_YTICKS = [0.0, 30.0, 60.0, 90.0]
# Known truth.  Chosen to span the frame and to sit at values that are NOT on the
# tick anchors, so recovering them cannot be an artefact of the calibration.
CONTROL_TRUTH = [(700.0, 28.7), (1400.0, 46.3), (2500.0, 61.4),
                 (3300.0, 72.8), (4440.0, 79.1), (5000.0, 84.6)]


def run_control(workdir, verbose=True):
    """Build the raster, digitise it BLIND, and measure the recovery error."""
    path = os.path.join(workdir, "control_fig.tif")
    xs = [p[0] for p in CONTROL_TRUTH]
    ys = [p[1] for p in CONTROL_TRUTH]
    prov = build_control_raster(path, xs, ys, CONTROL_XLIM, CONTROL_YLIM,
                                CONTROL_XTICKS, CONTROL_YTICKS)
    got = digitise(path, CONTROL_XTICKS, CONTROL_YTICKS)
    found = sorted([(p["x"], p["y"]) for p in got["points"]])
    truth = sorted(CONTROL_TRUTH)
    if len(found) != len(truth):
        refuse("planted control: %d markers recovered, %d planted. A control that "
               "cannot even count the planted points cannot bound anything."
               % (len(found), len(truth)))
    xspan = CONTROL_XLIM[1] - CONTROL_XLIM[0]
    yspan = CONTROL_YLIM[1] - CONTROL_YLIM[0]
    ex = [abs(f[0] - t[0]) for f, t in zip(found, truth)]
    ey = [abs(f[1] - t[1]) for f, t in zip(found, truth)]
    res = dict(
        provenance=prov,
        n_points=len(truth),
        x_err_max=max(ex), x_err_rms=float(np.sqrt(np.mean(np.square(ex)))),
        y_err_max=max(ey), y_err_rms=float(np.sqrt(np.mean(np.square(ey)))),
        x_err_max_frac_of_span=max(ex) / xspan,
        y_err_max_frac_of_span=max(ey) / yspan,
        truth=truth, recovered=found,
        calibration=got["calibration"])
    if verbose:
        print("PLANTED CALIBRATION CONTROL -- raster, same channel as the scan")
        print("  render %d dpi, %d bpc, threshold %d, encoder %s, raster %dx%d px,"
              " %d grey level(s) after round-trip"
              % (prov["render_dpi"], prov["bits_per_channel"], prov["threshold"],
                 prov["encoder"], prov["raster_px"][0], prov["raster_px"][1],
                 prov["distinct_grey_levels_after_roundtrip"]))
        print("  points planted/recovered: %d/%d" % (len(truth), len(found)))
        for t, f in zip(truth, found):
            print("    truth (%8.1f, %6.2f)  ->  recovered (%8.1f, %6.2f)   "
                  "dx %6.2f  dy %5.3f" % (t[0], t[1], f[0], f[1],
                                          abs(f[0] - t[0]), abs(f[1] - t[1])))
        print("  MEASURED DIGITISATION ERROR:")
        print("    x: max %.3f (%.4f %% of span)   rms %.3f"
              % (res["x_err_max"], 100 * res["x_err_max_frac_of_span"],
                 res["x_err_rms"]))
        print("    y: max %.4f W/m2K (%.4f %% of span)   rms %.4f"
              % (res["y_err_max"], 100 * res["y_err_max_frac_of_span"],
                 res["y_err_rms"]))
    if res["y_err_max_frac_of_span"] > CONTROL_TOL_FRAC:
        refuse("planted control: y error %.4f of span exceeds the registered "
               "%.4f. The digitiser cannot recover known values from a raster in "
               "the real channel, so nothing it extracts from the real figure is "
               "evidence." % (res["y_err_max_frac_of_span"], CONTROL_TOL_FRAC))
    return res


# ===========================================================================
# AMENDMENT 2026-08-26 (PRE-FIRST-COMPUTE): CLOSED FRAME, INWARD TICKS,
# LABEL-PAIRED CALIBRATION, MARKER-SHAPE SERIES SEPARATION, PATH MEANS.
# Everything above this line is the frozen e55d6208 instrument, unedited.
# ===========================================================================
import shutil

FRAME_LINE_FRAC = 0.60            # a frame line carries >= this of the max line ink
FRAME_MIN_SPAN_PX = 200           # and is at least this long
PARTITION_SPAN_FRAC = 0.90        # an internal line spanning >= this of the frame height
TICK_PROBE_PX = 60                # how far inside the frame a tick is followed
TICK_MIN_LEN_PX = 5               # shorter runs are frame-line roughness
TICK_MAX_THICK_PX = 7             # a tick is thin; a curve leaving the frame is not
LABEL_BAND_PX = 140               # label text lives within this of the frame line
LABEL_GAP_PX = 3                  # and not closer than this (frame-line ink)
LABEL_MIN_AREA_PX = 12            # a text component smaller than this is speckle
LABEL_CLUSTER_GAP_FRAC = 0.9      # glyphs closer than this x char height are one label
LABEL_PAIR_TOL_PX = 22            # label centre must sit within this of its anchor
CLASSIFY_MARGIN = 0.06            # best template must beat the runner-up by this
MERGED_SIZE_FRAC = 1.45           # a hole group wider than this x MARKER_PX is merged
HOLE_MIN_FRAC = 0.05              # hole area >= this x MARKER_PX^2 (drops speckle holes)
ABSCISSA_TOL = 100.0              # §10 D1: the abscissa must be within +-100 of 4440
PATH_MAX_GAP = 0.15               # path units; a larger gap between series markers refuses
PATH_MIN_PTS = 8                  # markers per partition, minimum
PATH_CENTRAL = (0.10, 0.90)       # §7.1: central 80 % of each partition
CLOSED_CONTROL_TOL_FRAC = 0.02    # the closed-frame control must recover within 2 % of span
MARKER_TEMPLATE_STROKE_FRAC = 0.14  # ring stroke as a fraction of marker size (measured 2-4 px of 12-26)

# ---------------------------------------------------------------------------
# REGISTERED FIGURES.  Page numbers read from the rendered pages (rule 15): the
# printed folio sits in the running head and the caption names the figure.
# Crops are the committed fig*_crop.png files (300 dpi pdftoppm of the page).
# ---------------------------------------------------------------------------
FIGURES = {
    "5.45": dict(
        crop="fig545_crop.png", page_printed=160, page_pdf=162,
        title="Face-averaged heat transfer coefficients for the single cube as a "
              "function of the Reynolds number Re_H",
        kind="points", x_name="Re_H", y_name="h", y_units="W/m2K",
        xlabels=["0", "2000", "4000", "6000"], xticks=[0.0, 2000.0, 4000.0, 6000.0],
        ylabels=["90.0", "60.0", "30.0", "0"], yticks=[0.0, 30.0, 60.0, 90.0],
        marker_px=26,
        # legend read from the page: + SIDE (N), o FRONT, x SIDE (S), triangle REAR, square TOP
        series=dict(front="circle", top="square", rear="triangle",
                    side_N="plus", side_S="cross"),
        at=4440.0),
    "5.37": dict(
        crop="fig537_lower_crop.png", page_printed=149, page_pdf=151,
        title="Profiles of the surface temperature along path ABCDA (upper plot) and "
              "along path ABCD (lower plot) for the T_co sweep -- LOWER plot",
        kind="path", x_name="location on path ABCD", y_name="T_sur", y_units="degC",
        xlabels=["A", "B", "C", "D"], xticks=[0.0, 1.0, 2.0, 3.0],
        ylabels=["70", "60", "50", "40"], yticks=[40.0, 50.0, 60.0, 70.0],
        marker_px=13,
        # legend read from the page: + 60, o 65, x 70, triangle 75, square 80 degC
        series=dict(T_co_60="plus", T_co_65="circle", T_co_70="cross",
                    T_co_75="triangle", T_co_80="square"),
        registered_series="T_co_75",
        partitions={"AB": "rear", "BC": "top", "CD": "front"}),
    "5.39": dict(
        crop="fig539_lower_crop.png", page_printed=151, page_pdf=153,
        title="Distributions of the surface temperature and heat transfer coefficient "
              "along path ABCD parametric in the Reynolds number -- LOWER plot h/h_tot",
        kind="path", x_name="location on path ABCD", y_name="h/h_tot", y_units="h/h_tot",
        xlabels=["A", "B", "C", "D"], xticks=[0.0, 1.0, 2.0, 3.0],
        ylabels=["3.0", "2.0", "1.0", "0"], yticks=[0.0, 1.0, 2.0, 3.0],
        marker_px=14,
        # caption read from the page: (+) 2750, (o) 3200, (x) 4000, (triangle) 4440, (square) 4970
        series=dict(Re_2750="plus", Re_3200="circle", Re_4000="cross",
                    Re_4440="triangle", Re_4970="square"),
        registered_series="Re_4440",
        partitions={"AB": "rear", "BC": "top", "CD": "front"}),
}
PATH_EDGE_NOTE = ("path ABCD (thesis Fig. 5.39 sketch, printed p. 151): A = rear face "
                  "at the floor, B = rear/top edge, C = top/front edge, D = front face at "
                  "the floor. Partition CD therefore runs from the top leading edge DOWN "
                  "to the floor; BC from the trailing edge to the leading edge.")


def _line_groups(idx, max_gap=1):
    """Consecutive indices -> (centre, first, last) groups."""
    out = []
    if len(idx) == 0:
        return out
    start = prev = int(idx[0])
    for i in idx[1:]:
        i = int(i)
        if i - prev > max_gap:
            out.append(((start + prev) / 2.0, start, prev))
            start = i
        prev = i
    out.append(((start + prev) / 2.0, start, prev))
    return out


def find_frame(ink):
    """Closed box frame: outermost long horizontal and vertical ink lines.
    Skew is absorbed by a 5-px dilation across the line before counting."""
    from scipy import ndimage
    dv = ndimage.binary_dilation(ink, structure=np.ones((5, 1)))
    dh = ndimage.binary_dilation(ink, structure=np.ones((1, 5)))
    rows = dv.sum(axis=1)
    cols = dh.sum(axis=0)
    if rows.max() < FRAME_MIN_SPAN_PX or cols.max() < FRAME_MIN_SPAN_PX:
        refuse("closed frame: no line longer than %d px (max row %d, max col %d)"
               % (FRAME_MIN_SPAN_PX, rows.max(), cols.max()))
    hl = _line_groups(np.where(rows >= FRAME_LINE_FRAC * rows.max())[0])
    vl = _line_groups(np.where(cols >= FRAME_LINE_FRAC * cols.max())[0])
    if len(hl) < 2 or len(vl) < 2:
        refuse("closed frame: need 2 horizontal and 2 vertical frame lines, found "
               "%d and %d. This is not a closed box, or the crop cut it."
               % (len(hl), len(vl)))
    top, bottom = hl[0], hl[-1]
    left, right = vl[0], vl[-1]
    # internal full-height verticals (path partitions) between left and right
    span = bottom[0] - top[0]
    internal = []
    for c, a, b in vl[1:-1]:
        seg = ink[int(top[1]):int(bottom[2]) + 1, a:b + 1].any(axis=1).sum()
        if seg >= PARTITION_SPAN_FRAC * span:
            internal.append(dict(x=c, first=a, last=b))
    if len(hl) > 2:
        refuse("closed frame: %d full-width horizontal lines; a closed frame has 2 "
               "and this file registers no horizontal partitions." % len(hl))
    return dict(top=dict(y=top[0], first=top[1], last=top[2]),
                bottom=dict(y=bottom[0], first=bottom[1], last=bottom[2]),
                left=dict(x=left[0], first=left[1], last=left[2]),
                right=dict(x=right[0], first=right[1], last=right[2]),
                internal_vertical=internal)


def find_inward_ticks(ink, frame):
    """Ticks leave the LEFT frame line to the RIGHT and the BOTTOM line UPWARD.
    Returns lists of dicts(pos, length, thick)."""
    L, B, T, R = frame["left"], frame["bottom"], frame["top"], frame["right"]
    # --- left frame: rows with ink just right of the line
    x0 = int(L["last"]) + 1
    band = ink[int(T["last"]) + 2:int(B["first"]) - 1, x0:x0 + TICK_PROBE_PX]
    hit = band[:, :3].all(axis=1)
    yt = []
    for c, a, b in _line_groups(np.where(hit)[0], max_gap=0):
        thick = b - a + 1
        row = band[a:b + 1].any(axis=0)
        length = int(np.argmin(row)) if not row.all() else TICK_PROBE_PX
        if length >= TICK_MIN_LEN_PX and thick <= TICK_MAX_THICK_PX:
            yt.append(dict(pos=c + int(T["last"]) + 2, length=length, thick=thick))
    # --- bottom frame: columns with ink just above the line
    y1 = int(B["first"]) - 1
    band = ink[max(0, y1 - TICK_PROBE_PX):y1 + 1, int(L["last"]) + 2:int(R["first"]) - 1]
    band = band[::-1]                      # row 0 = just above the frame line
    hit = band[:3, :].all(axis=0)
    xt = []
    for c, a, b in _line_groups(np.where(hit)[0], max_gap=0):
        thick = b - a + 1
        col = band[:, a:b + 1].any(axis=1)
        length = int(np.argmin(col)) if not col.all() else TICK_PROBE_PX
        if length >= TICK_MIN_LEN_PX and thick <= TICK_MAX_THICK_PX:
            xt.append(dict(pos=c + int(L["last"]) + 2, length=length, thick=thick))
    return xt, yt


def _clusters(ink_band, min_area, axis):
    """Connected text components in a band, clustered into labels along `axis`
    (0 = cluster vertically-stacked glyphs by row, 1 = by column)."""
    from scipy import ndimage
    lab, n = ndimage.label(ink_band, structure=np.ones((3, 3)))
    comps = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        if sl is None:
            continue
        m = lab[sl] == i
        area = int(m.sum())
        if area < min_area:
            continue
        ys, xs = np.where(m)
        comps.append(dict(y0=sl[0].start, y1=sl[0].stop, x0=sl[1].start, x1=sl[1].stop,
                          cy=float(ys.mean() + sl[0].start), cx=float(xs.mean() + sl[1].start),
                          area=area))
    if not comps:
        return []
    if axis == 1:      # x labels: glyphs side by side, cluster along x
        comps.sort(key=lambda c: c["x0"])
    else:              # y labels: glyphs side by side too (e.g. "90.0"), cluster along x,
        comps.sort(key=lambda c: c["x0"])   # but different labels are separated in y
    clusters = []
    for c in comps:
        placed = False
        for cl in clusters:
            h = max(cl["y1"] - cl["y0"], c["y1"] - c["y0"])
            gap = c["x0"] - cl["x1"]
            yover = min(cl["y1"], c["y1"]) - max(cl["y0"], c["y0"])
            if gap <= LABEL_CLUSTER_GAP_FRAC * h and yover > 0.3 * min(cl["y1"] - cl["y0"], c["y1"] - c["y0"]):
                cl["x1"] = max(cl["x1"], c["x1"]); cl["x0"] = min(cl["x0"], c["x0"])
                cl["y0"] = min(cl["y0"], c["y0"]); cl["y1"] = max(cl["y1"], c["y1"])
                cl["members"].append(c); placed = True
                break
        if not placed:
            clusters.append(dict(x0=c["x0"], x1=c["x1"], y0=c["y0"], y1=c["y1"], members=[c]))
    for cl in clusters:
        tot = sum(m["area"] for m in cl["members"])
        cl["cx"] = sum(m["cx"] * m["area"] for m in cl["members"]) / tot
        cl["cy"] = sum(m["cy"] * m["area"] for m in cl["members"]) / tot
        cl["bbox_cx"] = (cl["x0"] + cl["x1"]) / 2.0
        cl["bbox_cy"] = (cl["y0"] + cl["y1"]) / 2.0
        cl["area"] = tot
    return clusters


def _ocr(grey, box, whitelist):
    """tesseract on one label crop, 4x upscaled.  Returns the stripped string or
    None when tesseract is absent or returns nothing."""
    if shutil.which("tesseract") is None:
        return None
    x0, y0, x1, y1 = box
    pad = 6
    crop = Image.fromarray(grey[max(0, y0 - pad):y1 + pad, max(0, x0 - pad):x1 + pad])
    crop = crop.resize((crop.size[0] * 4, crop.size[1] * 4), Image.LANCZOS)
    tmp = tempfile.mkdtemp(prefix="t5_ocr_")
    pth = os.path.join(tmp, "l.png")
    crop.save(pth)
    try:
        p = subprocess.run(["tesseract", pth, "-", "--psm", "7", "-c",
                            "tessedit_char_whitelist=" + whitelist],
                           capture_output=True, text=True)
        s = p.stdout.strip()
    finally:
        os.unlink(pth); os.rmdir(tmp)
    return s or None


def pair_labels(ink, grey, frame, ticks, labels, values, axis):
    """AXIS CALIBRATION FROM TICK LABELS READ AGAINST TICK POSITIONS.

    axis 'y': label band LEFT of the left frame line, anchors = top frame, left
              ticks, bottom frame, in ascending pixel row.
    axis 'x': label band BELOW the bottom frame line, anchors = left frame,
              bottom ticks, internal partition lines, right frame.
    `labels` are the registered label STRINGS in the order they appear on the
    page (y: top to bottom; x: left to right) and `values` the registered data
    values in ASCENDING data order.  Returns (anchor_px ascending data order,
    report)."""
    L, B, T, R = frame["left"], frame["bottom"], frame["top"], frame["right"]
    if axis == "y":
        xa, xb = max(0, int(L["first"]) - LABEL_BAND_PX), max(1, int(L["first"]) - LABEL_GAP_PX)
        ya, yb = max(0, int(T["first"]) - 30), int(B["last"]) + 30
        band = ink[ya:yb, xa:xb]
        cl = _clusters(band, LABEL_MIN_AREA_PX, axis=0)
        for c in cl:
            c["x0"] += xa; c["x1"] += xa; c["y0"] += ya; c["y1"] += ya
            c["cx"] += xa; c["cy"] += ya; c["bbox_cx"] += xa; c["bbox_cy"] += ya
            c["pos"] = c["bbox_cy"]
        cand = ([dict(pos=T["y"], kind="frame_top", length=None)]
                + [dict(pos=t["pos"], kind="tick", length=t["length"]) for t in ticks]
                + [dict(pos=B["y"], kind="frame_bottom", length=None)])
        cl.sort(key=lambda c: c["pos"])          # top to bottom, as `labels`
        whitelist = "0123456789.-"
    else:
        ya, yb = int(B["last"]) + LABEL_GAP_PX, min(ink.shape[0], int(B["last"]) + LABEL_BAND_PX)
        xa, xb = max(0, int(L["first"]) - 60), min(ink.shape[1], int(R["last"]) + 60)
        band = ink[ya:yb, xa:xb]
        cl = _clusters(band, LABEL_MIN_AREA_PX, axis=1)
        for c in cl:
            c["x0"] += xa; c["x1"] += xa; c["y0"] += ya; c["y1"] += ya
            c["cx"] += xa; c["cy"] += ya; c["bbox_cx"] += xa; c["bbox_cy"] += ya
            c["pos"] = c["bbox_cx"]
        cand = ([dict(pos=L["x"], kind="frame_left", length=None)]
                + [dict(pos=t["pos"], kind="tick", length=t["length"]) for t in ticks]
                + [dict(pos=v["x"], kind="partition", length=None) for v in frame["internal_vertical"]]
                + [dict(pos=R["x"], kind="frame_right", length=None)])
        cl.sort(key=lambda c: c["pos"])          # left to right, as `labels`
        whitelist = "0123456789.-ABCD"
    # keep only the label row/column nearest the frame: the axis TITLE sits further
    # out than the tick labels and must not be paired.  For y the tick labels are
    # the clusters whose right edge is nearest the frame; a cluster further than
    # one cluster-width beyond the nearest is title text and is reported.
    if axis == "y" and cl:
        near = max(c["x1"] for c in cl)
        keep = [c for c in cl if near - c["x1"] <= 0.5 * (c["x1"] - c["x0"]) + 12]
    elif axis == "x" and cl:
        near = min(c["y0"] for c in cl)
        keep = [c for c in cl if c["y0"] - near <= 0.5 * (c["y1"] - c["y0"]) + 12]
    else:
        keep = cl
    dropped = [dict(x0=c["x0"], y0=c["y0"], x1=c["x1"], y1=c["y1"], why="beyond label row (title text)")
               for c in cl if c not in keep]
    cand.sort(key=lambda c: c["pos"])
    pairs = []
    used = {}
    for c in keep:
        d = [abs(c["pos"] - a["pos"]) for a in cand]
        j = int(np.argmin(d))
        if d[j] > LABEL_PAIR_TOL_PX:
            refuse("%s-axis: the label at (%d..%d, %d..%d) cannot be paired with any "
                   "tick, frame edge or partition line within %.0f px (nearest %.1f px). "
                   "A label with no anchor is a calibration nobody can check."
                   % (axis, c["x0"], c["x1"], c["y0"], c["y1"], LABEL_PAIR_TOL_PX, d[j]))
        if j in used:
            refuse("%s-axis: two labels pair with the same anchor at %.1f px. The tick "
                   "set is incomplete or the label band caught non-label text."
                   % (axis, cand[j]["pos"]))
        used[j] = c
        pairs.append((j, c))
    paired = [cand[j] for j, _ in pairs]
    unpaired_ticks = [a for k, a in enumerate(cand) if a["kind"] == "tick" and k not in used]
    if unpaired_ticks and any(a["kind"] == "tick" for a in paired):
        minp = min(a["length"] for a in paired if a["kind"] == "tick")
        maxu = max(a["length"] for a in unpaired_ticks)
        if maxu > minp:
            refuse("%s-axis: a labelled tick (%d px) is shorter than an unlabelled one "
                   "(%d px): a label sits on a minor tick while a major tick goes "
                   "unlabelled, so the pairing is wrong." % (axis, minp, maxu))
    if len(paired) != len(values):
        refuse("%s-axis: %d labels paired, %d registered anchor values (%r). The "
               "figure is not the registered one or the label band is wrong."
               % (axis, len(paired), len(values), values))
    # OCR each paired label; a CLEAN read that disagrees with the registered
    # string refuses; an unreadable one is recorded.
    ocr = []
    for (j, c), reg in zip(pairs, labels):
        s = _ocr(grey, (c["x0"], c["y0"], c["x1"], c["y1"]), whitelist)
        ok = None
        if s is not None:
            try:
                ok = abs(float(s) - float(reg)) < 1e-9
            except ValueError:
                ok = (s.strip() == reg.strip()) if s.strip() in ("A", "B", "C", "D") else None
        ocr.append(dict(registered=reg, read=s, agrees=ok))
        if ok is False:
            refuse("%s-axis: the label paired with the anchor at %.1f px reads %r under "
                   "OCR but is registered as %r. The registered label set does not "
                   "match the page." % (axis, cand[j]["pos"], s, reg))
    pos_page_order = [a["pos"] for a in paired]        # y: top->bottom; x: left->right
    anchors = list(reversed(pos_page_order)) if axis == "y" else pos_page_order
    rep = dict(candidates=[dict(pos=float(a["pos"]), kind=a["kind"], length=a["length"]) for a in cand],
               paired=[dict(pos=float(a["pos"]), kind=a["kind"], label=l)
                       for a, l in zip(paired, labels)],
               unpaired_ticks=len(unpaired_ticks), dropped_text=dropped, ocr=ocr)
    return anchors, rep


def _template(shape, size, stroke):
    """Synthetic ring template of a hollow marker (1 = ink) in a size x size window."""
    from PIL import ImageDraw
    im = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(im)
    m = 1
    if shape == "circle":
        d.ellipse([m, m, size - 1 - m, size - 1 - m], outline=255, width=stroke)
    elif shape == "square":
        d.rectangle([m, m, size - 1 - m, size - 1 - m], outline=255, width=stroke)
    elif shape == "triangle":
        d.polygon([(size / 2.0, m), (size - 1 - m, size - 1 - m), (m, size - 1 - m)], outline=255)
        for k in range(1, stroke):
            d.polygon([(size / 2.0, m + k), (size - 1 - m - k, size - 1 - m - k),
                       (m + k, size - 1 - m - k)], outline=255)
    elif shape == "plus":
        c = size // 2
        d.line([(m, c), (size - 1 - m, c)], fill=255, width=stroke)
        d.line([(c, m), (c, size - 1 - m)], fill=255, width=stroke)
    elif shape == "cross":
        d.line([(m, m), (size - 1 - m, size - 1 - m)], fill=255, width=stroke)
        d.line([(m, size - 1 - m), (size - 1 - m, m)], fill=255, width=stroke)
    return (np.array(im) > 0).astype(float)


def _ncc(a, b):
    a = a - a.mean(); b = b - b.mean()
    den = np.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / den) if den > 0 else 0.0


def classify_marker(ink, cx, cy, marker_px, hollow):
    """Template correlation at the candidate centre; the best shape wins only by
    CLASSIFY_MARGIN over the runner-up."""
    size = int(round(marker_px))
    stroke = max(2, int(round(MARKER_TEMPLATE_STROKE_FRAC * size)))
    shapes = ("circle", "square", "triangle") if hollow else ("plus", "cross")
    best = {}
    half = size // 2
    for s in shapes:
        t = _template(s, size, stroke)
        sc = -1.0
        for dy in (-1, 0, 1):          # 1-px jitter absorbs centroid rounding
            for dx in (-1, 0, 1):
                y0 = int(round(cy)) - half + dy; x0 = int(round(cx)) - half + dx
                if y0 < 0 or x0 < 0 or y0 + size > ink.shape[0] or x0 + size > ink.shape[1]:
                    continue
                sc = max(sc, _ncc(ink[y0:y0 + size, x0:x0 + size].astype(float), t))
        best[s] = sc
    order = sorted(best.items(), key=lambda kv: -kv[1])
    margin = order[0][1] - (order[1][1] if len(order) > 1 else -1.0)
    label = order[0][0] if margin >= CLASSIFY_MARGIN and order[0][1] > 0 else "UNCLASSIFIED"
    return label, {k: round(v, 4) for k, v in best.items()}, margin


def find_hollow_markers(ink, frame, marker_px):
    """A marker is a group of enclosed white holes within MARKER_PX of each other.
    Frame and partition lines are masked first (a hole must not be a frame corner)."""
    from scipy import ndimage
    L, B, T, R = frame["left"], frame["bottom"], frame["top"], frame["right"]
    y0, y1 = int(T["last"]) + 1, int(B["first"])
    x0, x1 = int(L["last"]) + 1, int(R["first"])
    sub = ink[y0:y1, x0:x1].copy()
    for v in frame["internal_vertical"]:
        a, b = int(v["first"]) - x0 - 2, int(v["last"]) - x0 + 3
        sub[:, max(0, a):b] = False
    white = ~sub
    lab, n = ndimage.label(white)
    # background = the white component(s) touching the sub-image border
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
    areas = ndimage.sum(white, lab, index=np.arange(1, n + 1))
    objs = ndimage.find_objects(lab)
    holes = []
    amin = HOLE_MIN_FRAC * marker_px * marker_px
    amax = (MERGED_SIZE_FRAC * marker_px) ** 2
    for i in range(1, n + 1):
        if i in border or areas[i - 1] < amin or areas[i - 1] > amax:
            continue
        sl = objs[i - 1]
        ys, xs = np.where(lab[sl] == i)
        holes.append(dict(cy=float(ys.mean() + sl[0].start), cx=float(xs.mean() + sl[1].start),
                          y0=sl[0].start, y1=sl[0].stop, x0=sl[1].start, x1=sl[1].stop,
                          area=float(areas[i - 1])))
    # group holes within 0.6 marker_px (a series line splits an interior in two)
    groups = []
    for h in sorted(holes, key=lambda h: (h["cx"], h["cy"])):
        for g in groups:
            if abs(h["cx"] - g["cx"]) <= 0.6 * marker_px and abs(h["cy"] - g["cy"]) <= 0.6 * marker_px:
                g["members"].append(h)
                tot = sum(m["area"] for m in g["members"])
                g["cx"] = sum(m["cx"] * m["area"] for m in g["members"]) / tot
                g["cy"] = sum(m["cy"] * m["area"] for m in g["members"]) / tot
                g["x0"] = min(g["x0"], h["x0"]); g["x1"] = max(g["x1"], h["x1"])
                g["y0"] = min(g["y0"], h["y0"]); g["y1"] = max(g["y1"], h["y1"])
                break
        else:
            groups.append(dict(cx=h["cx"], cy=h["cy"], x0=h["x0"], x1=h["x1"], y0=h["y0"],
                               y1=h["y1"], members=[h]))
    out = []
    for g in groups:
        w, hgt = g["x1"] - g["x0"], g["y1"] - g["y0"]
        # interior bbox centre is a better centre than the hole centroid when a
        # line splits the interior unevenly
        cx, cy = (g["x0"] + g["x1"]) / 2.0, (g["y0"] + g["y1"]) / 2.0
        rec = dict(px=cx + x0, py=cy + y0, interior_w=int(w), interior_h=int(hgt),
                   n_holes=len(g["members"]))
        if max(w, hgt) > MERGED_SIZE_FRAC * marker_px * 0.85:
            rec.update(shape="MERGED", scores={}, margin=0.0)
        else:
            lbl, sc, mg = classify_marker(ink, rec["px"], rec["py"], marker_px, hollow=True)
            rec.update(shape=lbl, scores=sc, margin=round(mg, 4))
        out.append(rec)
    return out


def find_solid_markers(ink, frame, marker_px, hollow_markers):
    """Solid symbols (+, x): ink components inside the frame with no enclosed
    hole, of marker size, not overlapping a hollow marker."""
    from scipy import ndimage
    L, B, T, R = frame["left"], frame["bottom"], frame["top"], frame["right"]
    y0, y1 = int(T["last"]) + 1, int(B["first"])
    x0, x1 = int(L["last"]) + 1, int(R["first"])
    sub = ink[y0:y1, x0:x1].copy()
    for v in frame["internal_vertical"]:
        a, b = int(v["first"]) - x0 - 2, int(v["last"]) - x0 + 3
        sub[:, max(0, a):b] = False
    lab, n = ndimage.label(sub, structure=np.ones((3, 3)))
    out = []
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        if sl is None:
            continue
        w, h = sl[1].stop - sl[1].start, sl[0].stop - sl[0].start
        if max(w, h) < 0.5 * marker_px or min(w, h) < 0.3 * marker_px:
            continue
        m = lab[sl] == i
        ys, xs = np.where(m)
        px, py = xs.mean() + sl[1].start + x0, ys.mean() + sl[0].start + y0
        if any(abs(px - hm["px"]) < 0.7 * marker_px and abs(py - hm["py"]) < 0.7 * marker_px
               for hm in hollow_markers):
            continue
        rec = dict(px=float(px), py=float(py), bbox_w=int(w), bbox_h=int(h), area=int(m.sum()))
        if max(w, h) > MERGED_SIZE_FRAC * marker_px:
            rec.update(shape="MERGED", scores={}, margin=0.0)
        else:
            lbl, sc, mg = classify_marker(ink, px, py, marker_px, hollow=False)
            rec.update(shape=lbl, scores=sc, margin=round(mg, 4))
        out.append(rec)
    return out


def calibrate_closed(ink, grey, frame, fig):
    xt, yt = find_inward_ticks(ink, frame)
    xa, xrep = pair_labels(ink, grey, frame, xt, fig["xlabels"], fig["xticks"], "x")
    ya, yrep = pair_labels(ink, grey, frame, yt, fig["ylabels"], fig["yticks"], "y")
    ax_, bx_, rx = calibrate(xa, fig["xticks"], "x-axis")
    ay_, by_, ry = calibrate(ya, fig["yticks"], "y-axis")   # ya is BOTTOM-first (ascending data)
    if ay_ >= 0.0:
        refuse("y-axis calibration has a non-negative scale (%.6g data per px): the "
               "anchor order is wrong and every value would be reflected." % ay_)
    if ax_ <= 0.0:
        refuse("x-axis calibration has a non-positive scale (%.6g data per px)." % ax_)
    return dict(x=[ax_, bx_], y=[ay_, by_], max_resid_px=dict(x=rx, y=ry),
                x_anchors_px=[float(v) for v in xa], y_anchors_px_bottom_first=[float(v) for v in ya],
                x_report=xrep, y_report=yrep)


def digitise_closed(path, fig):
    """Closed-frame figure -> calibrated, classified markers.  No values are
    selected here; `series_value_at` does that against the registered request."""
    grey = np.array(Image.open(path).convert("L"))
    ink = grey < THRESHOLD
    frame = find_frame(ink)
    cal = calibrate_closed(ink, grey, frame, fig)
    hollow = find_hollow_markers(ink, frame, fig["marker_px"])
    solid = find_solid_markers(ink, frame, fig["marker_px"], hollow)
    ax_, bx_ = cal["x"]; ay_, by_ = cal["y"]
    markers = []
    for m in hollow + solid:
        m = dict(m)
        m["x"] = ax_ * m["px"] + bx_
        m["y"] = ay_ * m["py"] + by_
        markers.append(m)
    counts = {}
    for m in markers:
        counts[m["shape"]] = counts.get(m["shape"], 0) + 1
    return dict(frame=dict(top=frame["top"]["y"], bottom=frame["bottom"]["y"],
                           left=frame["left"]["x"], right=frame["right"]["x"],
                           internal_vertical=[v["x"] for v in frame["internal_vertical"]]),
                calibration=cal, marker_px=fig["marker_px"],
                symbol_radius_data_units=dict(
                    x=abs(ax_) * fig["marker_px"] / 2.0, y=abs(ay_) * fig["marker_px"] / 2.0),
                shape_counts=counts, markers=markers)


def series_value_at(dig, fig, series_name):
    """POINT figures: the marker of `series_name`'s symbol nearest fig['at'].
    PATH figures: per-partition central-80 % path-weighted mean of the linearly
    interpolated series, with the full-partition mean beside it."""
    shape = fig["series"][series_name]
    pts = sorted([(m["x"], m["y"]) for m in dig["markers"] if m["shape"] == shape])
    if fig["kind"] == "points":
        if not pts:
            refuse("%s: no marker classified as %r (series %s) -- the series cannot be "
                   "separated." % (fig["crop"], shape, series_name))
        at = fig["at"]
        j = int(np.argmin([abs(p[0] - at) for p in pts]))
        if abs(pts[j][0] - at) > ABSCISSA_TOL:
            refuse("%s: nearest %r marker sits at x=%.1f, not within +-%.0f of the "
                   "registered abscissa %.0f (§10 D1)." % (fig["crop"], shape, pts[j][0],
                                                             ABSCISSA_TOL, at))
        # a MERGED blob at the same abscissa means another series touches this one
        merged_here = [m for m in dig["markers"] if m["shape"] == "MERGED"
                       and abs(m["x"] - pts[j][0]) < ABSCISSA_TOL and abs(m["y"] - pts[j][1]) < 2 * dig["symbol_radius_data_units"]["y"]]
        if merged_here:
            refuse("%s: the %r marker at x=%.1f touches a MERGED blob -- the series "
                   "cannot be separated at the registered abscissa." % (fig["crop"], shape, pts[j][0]))
        return dict(series=series_name, symbol=shape, abscissa=pts[j][0], value=pts[j][1],
                    n_series_markers=len(pts))
    # ---- path figure
    xs = np.array([p[0] for p in pts]); ys = np.array([p[1] for p in pts])
    out = dict(series=series_name, symbol=shape, n_series_markers=int(len(pts)), partitions={})
    for k, (pname, face) in enumerate(sorted(fig["partitions"].items())):
        lo, hi = float(k), float(k + 1)
        sel = (xs >= lo - 0.02) & (xs <= hi + 0.02)
        px_, py_ = xs[sel], ys[sel]
        if len(px_) < PATH_MIN_PTS:
            refuse("%s: partition %s (%s) holds %d %r markers, fewer than %d -- the series "
                   "cannot be separated on that face." % (fig["crop"], pname, face, len(px_), shape, PATH_MIN_PTS))
        gaps = np.diff(px_)
        if gaps.max() > PATH_MAX_GAP:
            refuse("%s: partition %s (%s): a gap of %.3f path units between consecutive %r "
                   "markers exceeds %.2f -- markers were lost to overlap and interpolation "
                   "across the gap would invent the curve." % (fig["crop"], pname, face,
                                                                gaps.max(), shape, PATH_MAX_GAP))
        c0, c1 = lo + PATH_CENTRAL[0], lo + PATH_CENTRAL[1]
        if px_[0] > c0 or px_[-1] < c1:
            refuse("%s: partition %s (%s): %r markers cover [%.3f, %.3f], not the central "
                   "window [%.2f, %.2f]." % (fig["crop"], pname, face, shape, px_[0], px_[-1], c0, c1))
        grid = np.linspace(c0, c1, 401)
        central = float(np.trapz(np.interp(grid, px_, py_), grid) / (c1 - c0))
        f0, f1 = max(lo, px_[0]), min(hi, px_[-1])
        gridf = np.linspace(f0, f1, 401)
        full = float(np.trapz(np.interp(gridf, px_, py_), gridf) / (f1 - f0))
        out["partitions"][pname] = dict(
            face=face, n_markers=int(len(px_)), max_gap=float(gaps.max()),
            central_80pct_mean=central, central_window=[c0, c1],
            full_partition_mean_REPORTED=full, full_coverage=[float(f0), float(f1)],
            y_at_markers_min=float(py_.min()), y_at_markers_max=float(py_.max()))
    return out


# ---------------------------------------------------------------------------
# THE SECOND PLANTED CONTROL: closed frame, inward ticks, five line-connected
# series over a partitioned path, degraded through the SAME measured channel.
# ---------------------------------------------------------------------------
CLOSED_CONTROL_YLIM = (40.0, 70.0)
CLOSED_CONTROL_YTICKS = [40.0, 50.0, 60.0, 70.0]
CLOSED_CONTROL_YLABELS = ["70", "60", "50", "40"]
CLOSED_CONTROL_XLABELS = ["A", "B", "C", "D"]
CLOSED_CONTROL_XTICKS = [0.0, 1.0, 2.0, 3.0]
CLOSED_CONTROL_MARKER_PX = 13
CLOSED_CONTROL_SERIES = {"s_plus": "plus", "s_circle": "circle", "s_cross": "cross",
                         "s_tri": "triangle", "s_sq": "square"}
CLOSED_CONTROL_OFFSETS = {"s_plus": -8.0, "s_circle": -4.0, "s_cross": 0.0, "s_tri": 4.0, "s_sq": 8.0}


def closed_control_truth(n_per_partition=24):
    """Known series: a 5.37-shaped profile plus a per-series offset; the circle
    series crosses the triangle series inside partition BC so overlap is
    exercised, not avoided."""
    xs = np.concatenate([np.linspace(k + 0.02, k + 0.98, n_per_partition) for k in range(3)])
    base = 55.0 + 6.0 * np.sin(np.pi * (xs % 1.0)) - 4.0 * np.exp(-((xs % 1.0) - 0.5) ** 2 / 0.02)
    truth = {}
    for name, off in CLOSED_CONTROL_OFFSETS.items():
        y = base + off
        if name == "s_circle":
            y = y + 9.0 * np.clip(xs - 1.2, 0, 0.6) - 9.0 * np.clip(xs - 1.9, 0, 0.6)   # crosses s_tri in BC
        truth[name] = (xs, y)
    return truth


def build_closed_control_raster(path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    truth = closed_control_truth()
    mk = {"plus": "+", "circle": "o", "cross": "x", "triangle": "^", "square": "s"}
    fig, ax = plt.subplots(figsize=(3.7, 1.7), dpi=RENDER_DPI)
    for name, (xs, ys) in truth.items():
        ax.plot(xs, ys, color="black", linewidth=0.6, marker=mk[CLOSED_CONTROL_SERIES[name]],
                markersize=3.1, markerfacecolor="none", markeredgecolor="black", markeredgewidth=0.6)
    for xv in (1.0, 2.0):
        ax.axvline(xv, color="black", linewidth=0.9)
    ax.set_xlim(0.0, 3.0); ax.set_ylim(*CLOSED_CONTROL_YLIM)
    ax.set_xticks(CLOSED_CONTROL_XTICKS); ax.set_xticklabels(CLOSED_CONTROL_XLABELS)
    ax.set_yticks(CLOSED_CONTROL_YTICKS); ax.set_yticklabels(CLOSED_CONTROL_YLABELS[::-1])
    ax.set_yticks([45.0, 55.0, 65.0], minor=True)
    ax.tick_params(direction="in", length=6, width=0.9, labelsize=9, pad=3)
    ax.tick_params(which="minor", direction="in", length=3, width=0.9)
    for s in ax.spines.values():
        s.set_linewidth(0.9)
    fig.subplots_adjust(left=0.13, right=0.97, top=0.95, bottom=0.14)
    tmp_png = path + ".grey.png"
    fig.savefig(tmp_png, dpi=RENDER_DPI, facecolor="white")
    plt.close(fig)
    prov = _degrade_to_channel(tmp_png, path)
    os.unlink(tmp_png)
    return truth, prov


def _degrade_to_channel(grey_png, out_path, seed=20260826):
    """Skew, ink spread, 1-bit threshold, speckle, CCITT G4 -- the measured channel,
    applied exactly as `build_control_raster` applies it."""
    from scipy import ndimage as _nd
    im = Image.open(grey_png).convert("L")
    im = im.rotate(SKEW_DEG, resample=Image.BICUBIC, fillcolor=255)
    arr = np.array(im)
    if INK_DILATE_PX > 0:
        dark = _nd.binary_dilation(arr < THRESHOLD, iterations=INK_DILATE_PX)
        arr = np.where(dark, 0, arr).astype(np.uint8)
    bilevel = (arr >= THRESHOLD).astype(np.uint8) * 255
    rng = np.random.default_rng(seed)
    hgt, wid = bilevel.shape
    n_spk = int(SPECKLE_FRAC * 2478 * (hgt * wid) / (1260.0 * 1920.0))
    for _ in range(n_spk):
        sy = int(rng.integers(0, hgt - 2)); sx = int(rng.integers(0, wid - 2))
        area = int(rng.integers(1, 5))
        if area == 1:
            bilevel[sy, sx] = 0
        elif area == 2:
            bilevel[sy, sx:sx + 2] = 0
        elif area == 3:
            bilevel[sy, sx:sx + 2] = 0; bilevel[sy + 1, sx] = 0
        else:
            bilevel[sy:sy + 2, sx:sx + 2] = 0
    Image.fromarray(bilevel).convert("1").save(out_path, format="TIFF", compression=SCAN_ENCODER)
    reloaded = np.array(Image.open(out_path).convert("L"))
    return dict(render_dpi=RENDER_DPI, bits_per_channel=SCAN_BPC, threshold=THRESHOLD,
                encoder=SCAN_ENCODER, skew_deg=SKEW_DEG, speckle_frac=SPECKLE_FRAC,
                ink_dilate_px=INK_DILATE_PX, speckle_blobs_planted=n_spk,
                raster_px=[int(reloaded.shape[1]), int(reloaded.shape[0])],
                distinct_grey_levels_after_roundtrip=int(np.unique(reloaded).size))


CLOSED_CONTROL_FIG = dict(
    crop="closed_control.tif", kind="path", x_name="path", y_name="y", y_units="units",
    xlabels=CLOSED_CONTROL_XLABELS, xticks=CLOSED_CONTROL_XTICKS,
    ylabels=CLOSED_CONTROL_YLABELS, yticks=CLOSED_CONTROL_YTICKS,
    marker_px=CLOSED_CONTROL_MARKER_PX, series=CLOSED_CONTROL_SERIES,
    registered_series="s_tri", partitions={"AB": "p0", "BC": "p1", "CD": "p2"})


def run_closed_control(workdir, verbose=True, mis_anchor=False):
    """Build the closed-frame raster, digitise it BLIND, measure the recovery
    error of the registered (triangle) series at its markers and in the
    partition means.  `mis_anchor` registers FIVE y labels against a four-label
    axis: the planted negative control, which must REFUSE."""
    path = os.path.join(workdir, "closed_control.tif")
    truth, prov = build_closed_control_raster(path)
    fig = dict(CLOSED_CONTROL_FIG)
    if mis_anchor:
        fig["ylabels"] = ["70", "60", "50", "45", "40"]
        fig["yticks"] = [40.0, 45.0, 50.0, 60.0, 70.0]
    dig = digitise_closed(path, fig)
    val = series_value_at(dig, fig, "s_tri")
    txs, tys = truth["s_tri"]
    span = CLOSED_CONTROL_YLIM[1] - CLOSED_CONTROL_YLIM[0]
    # point-wise: every classified triangle marker against the nearest truth point
    got = sorted([(m["x"], m["y"]) for m in dig["markers"] if m["shape"] == "triangle"])
    errs = []
    for gx, gy in got:
        j = int(np.argmin(np.abs(txs - gx)))
        errs.append((abs(gx - txs[j]), abs(gy - tys[j])))
    ex = max(e[0] for e in errs); ey = max(e[1] for e in errs)
    # partition means against the truth polyline integrated the same way
    mean_err = {}
    for k, pname in enumerate(("AB", "BC", "CD")):
        c0, c1 = k + PATH_CENTRAL[0], k + PATH_CENTRAL[1]
        grid = np.linspace(c0, c1, 401)
        tmean = float(np.trapz(np.interp(grid, txs, tys), grid) / (c1 - c0))
        mean_err[pname] = dict(truth=tmean, recovered=val["partitions"][pname]["central_80pct_mean"],
                               err=abs(tmean - val["partitions"][pname]["central_80pct_mean"]))
    emax = max(v["err"] for v in mean_err.values())
    # series separation: how many truth markers did we classify, and any false ones?
    res = dict(provenance=prov, shape_counts=dig["shape_counts"],
               triangle_markers_planted=int(len(txs)), triangle_markers_recovered=len(got),
               x_err_max=ex, y_err_max=ey, y_err_max_frac_of_span=ey / span,
               partition_mean_err=mean_err, partition_mean_err_max=emax,
               partition_mean_err_max_frac_of_span=emax / span,
               calibration=dict(x=dig["calibration"]["x"], y=dig["calibration"]["y"],
                                max_resid_px=dig["calibration"]["max_resid_px"]),
               label_pairing=dict(x=dig["calibration"]["x_report"]["paired"],
                                  y=dig["calibration"]["y_report"]["paired"]),
               ocr=dict(x=dig["calibration"]["x_report"]["ocr"], y=dig["calibration"]["y_report"]["ocr"]))
    if verbose:
        print("PLANTED CLOSED-FRAME CONTROL -- inward ticks, 5 line-connected series, partitions")
        print("  raster %dx%d px, %d grey level(s) after G4 round-trip; shapes found: %s"
              % (prov["raster_px"][0], prov["raster_px"][1],
                 prov["distinct_grey_levels_after_roundtrip"], dig["shape_counts"]))
        print("  triangle markers planted/recovered: %d/%d" % (len(txs), len(got)))
        print("  MEASURED DIGITISATION ERROR (triangle series):")
        print("    per marker: x max %.4f path units, y max %.4f units (%.4f %% of span)"
              % (ex, ey, 100 * ey / span))
        for k, v in mean_err.items():
            print("    partition %s central-80%% mean: truth %.4f recovered %.4f err %.4f"
                  % (k, v["truth"], v["recovered"], v["err"]))
        print("    partition means: max err %.4f units (%.4f %% of span)" % (emax, 100 * emax / span))
    if len(got) < 0.8 * len(txs):
        refuse("closed control: only %d of %d triangle markers recovered -- the series "
               "separation rule loses too much of the series." % (len(got), len(txs)))
    if ey / span > CLOSED_CONTROL_TOL_FRAC or emax / span > CLOSED_CONTROL_TOL_FRAC:
        refuse("closed control: y error %.4f of span (markers) / %.4f (means) exceeds the "
               "registered %.4f." % (ey / span, emax / span, CLOSED_CONTROL_TOL_FRAC))
    return res


def selftest_closed(tmp):
    """The added arms.  Returns a list of failure strings."""
    failures = []
    try:
        res = run_closed_control(tmp)
        print("CLOSED PLANT RECOVERED: %d/%d triangle markers, y error %.4f %% of span "
              "(markers), %.4f %% (partition means)."
              % (res["triangle_markers_recovered"], res["triangle_markers_planted"],
                 100 * res["y_err_max_frac_of_span"], 100 * res["partition_mean_err_max_frac_of_span"]))
    except SystemExit:
        failures.append("CLOSED PLANTED CONTROL FAILED")
    me = os.path.abspath(__file__)
    rcs = {}
    for tag, argv in (("python3", [sys.executable, me]), ("python3 -O", [sys.executable, "-O", me])):
        q = subprocess.run(argv + ["--closed-control", "--mis-anchor"], capture_output=True, text=True)
        rcs[tag] = (q.returncode, "REFUSED" in q.stderr)
    if all(rc == 2 and seen for rc, seen in rcs.values()):
        print("CLOSED MIS-ANCHOR REFUSED under BOTH `python3` and `python3 -O` (rc 2): five "
              "registered y labels against a four-label closed frame.")
    else:
        failures.append("closed mis-anchor negative control did not fire identically: %r" % (rcs,))
    return failures


def build_reference(outdir, lane_id):
    """Run every registered figure and assemble T5_reference_primary.json rows.
    Refusals propagate (exit 2); nothing is eyeballed in."""
    import datetime
    tmp = tempfile.mkdtemp(prefix="t5_ctl_")
    try:
        raster = run_control(tmp, verbose=False)
        closed = run_closed_control(tmp, verbose=False)
    finally:
        for root, _d, files in os.walk(tmp, topdown=False):
            for f in files:
                os.unlink(os.path.join(root, f))
            os.rmdir(root)
    per_fig = {}
    for fid, fig in FIGURES.items():
        path = os.path.join(outdir, fig["crop"])
        dig = digitise_closed(path, fig)
        per_fig[fid] = dict(dig=dig, extracted={}, refused={})
        wanted = ([n for n in fig["series"]] if fig["kind"] == "points" else [fig["registered_series"]])
        for name in wanted:
            try:
                per_fig[fid]["extracted"][name] = series_value_at(dig, fig, name)
            except SystemExit:
                per_fig[fid]["refused"][name] = "REFUSED (see stderr)"
    return dict(raster_control=raster, closed_control=closed, figures=per_fig,
                digitised_utc=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                lane_id=lane_id)


def selftest():
    failures = []
    tmp = tempfile.mkdtemp(prefix="t5_digitiser_")

    # (1) THE PLANTED CONTROL FIRST -- rule 3.  Everything after it is worthless
    #     if the digitiser cannot recover planted values in the real channel.
    try:
        res = run_control(tmp)
        print("PLANT RECOVERED: %d/%d markers, y error %.4f %% of span."
              % (res["n_points"], res["n_points"],
                 100 * res["y_err_max_frac_of_span"]))
    except SystemExit:
        failures.append("PLANTED CONTROL FAILED -- the digitiser could not "
                        "recover planted values from a raster in the real channel")
        res = None

    # (2) NEGATIVE ARM: a mis-registered anchor set must REFUSE, not silently
    #     rescale.  This is the T3 defect class driven deliberately.
    path = os.path.join(tmp, "control_fig.tif")
    if os.path.isfile(path):
        me = os.path.abspath(__file__)
        p = subprocess.run([sys.executable, me, "--figure", path,
                            "--xticks", "0,2000,4000",     # WRONG: 3 not 4
                            "--yticks", "0,30,60,90"],
                           capture_output=True, text=True)
        if p.returncode == 2 and "REFUSED" in p.stderr:
            print("MIS-ANCHOR REFUSED: a 3-anchor x set against a 4-tick axis "
                  "returned rc 2 instead of silently rescaling.")
        else:
            failures.append("mis-anchored run did not refuse: rc=%d" % p.returncode)

        # (3) THE ARM THAT BITES -- driven under `python3 -O`, refusal must FIRE.
        rcs = {}
        for tag, argv in (("python3", [sys.executable, me]),
                          ("python3 -O", [sys.executable, "-O", me])):
            q = subprocess.run(argv + ["--figure", path, "--xticks", "0,2000,4000",
                                       "--yticks", "0,30,60,90"],
                               capture_output=True, text=True)
            rcs[tag] = q.returncode
        if rcs["python3"] == 2 and rcs["python3 -O"] == 2:
            print("REFUSAL FIRES UNDER `-O`: the mis-anchored figure returned rc 2 "
                  "under BOTH `python3` and `python3 -O`.")
        else:
            failures.append("refusal did not fire identically: %r" % (rcs,))

    # (4)+(5) AMENDMENT 2026-08-26: the closed-frame planted control and its
    #     mis-anchored negative control, driven under both interpreters.
    failures.extend(selftest_closed(tmp))

    for root, _d, files in os.walk(tmp, topdown=False):
        for f in files:
            os.unlink(os.path.join(root, f))
        os.rmdir(root)

    if failures:
        for f in failures:
            print("FAILED: " + f)
        return 1
    print("SELFTEST PASS: 5 arms (3 open-frame + 2 closed-frame), 0 FAILED.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--control", action="store_true",
                    help="run the planted calibration control and print its "
                         "MEASURED error")
    ap.add_argument("--figure")
    ap.add_argument("--xticks")
    ap.add_argument("--yticks")
    ap.add_argument("--out")
    # ---- AMENDMENT 2026-08-26: closed-frame arms
    ap.add_argument("--closed-control", action="store_true",
                    help="run the closed-frame line-series planted control")
    ap.add_argument("--mis-anchor", action="store_true",
                    help="with --closed-control: register 5 y labels against 4 (must REFUSE)")
    ap.add_argument("--fig", choices=sorted(FIGURES),
                    help="digitise one REGISTERED thesis figure (crop in --dir)")
    ap.add_argument("--dir", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--series", help="with --fig: series name to extract (default: all registered)")
    ap.add_argument("--build-reference", action="store_true",
                    help="run both controls and all registered figures; print the assembled record")
    ap.add_argument("--lane", default="unnamed-lane")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.closed_control:
        tmp = tempfile.mkdtemp(prefix="t5_cctl_")
        try:
            res = run_closed_control(tmp, mis_anchor=a.mis_anchor)
        finally:
            for root, _d, files in os.walk(tmp, topdown=False):
                for f in files:
                    os.unlink(os.path.join(root, f))
                os.rmdir(root)
        if a.out:
            with open(a.out, "w") as fh:
                json.dump(res, fh, indent=1)
            print("wrote " + a.out)
        return 0
    if a.fig:
        fig = FIGURES[a.fig]
        dig = digitise_closed(os.path.join(a.dir, fig["crop"]), fig)
        names = [a.series] if a.series else (list(fig["series"]) if fig["kind"] == "points"
                                              else [fig["registered_series"]])
        got = dict(figure=a.fig, page_printed=fig["page_printed"], page_pdf=fig["page_pdf"],
                   digitised=dig, values={n: series_value_at(dig, fig, n) for n in names})
        out = json.dumps(got, indent=1, default=float)
        if a.out:
            with open(a.out, "w") as fh:
                fh.write(out)
            print("wrote " + a.out)
        else:
            print(out)
        return 0
    if a.build_reference:
        rec = build_reference(a.dir, a.lane)
        out = json.dumps(rec, indent=1, default=float)
        if a.out:
            with open(a.out, "w") as fh:
                fh.write(out)
            print("wrote " + a.out)
        else:
            print(out)
        return 0
    if a.control:
        tmp = tempfile.mkdtemp(prefix="t5_control_")
        res = run_control(tmp)
        if a.out:
            with open(a.out, "w") as fh:
                json.dump(res, fh, indent=1)
            print("wrote " + a.out)
        for root, _d, files in os.walk(tmp, topdown=False):
            for f in files:
                os.unlink(os.path.join(root, f))
            os.rmdir(root)
        return 0
    if a.figure:
        if not (a.xticks and a.yticks):
            refuse("--figure needs --xticks and --yticks: the anchor VALUES are "
                   "registered, never inferred from the image")
        xt = [float(v) for v in a.xticks.split(",")]
        yt = [float(v) for v in a.yticks.split(",")]
        got = digitise(a.figure, xt, yt)
        out = json.dumps(got, indent=1)
        if a.out:
            with open(a.out, "w") as fh:
                fh.write(out)
            print("wrote " + a.out)
        else:
            print(out)
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
