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

    for root, _d, files in os.walk(tmp, topdown=False):
        for f in files:
            os.unlink(os.path.join(root, f))
        os.rmdir(root)

    if failures:
        for f in failures:
            print("FAILED: " + f)
        return 1
    print("SELFTEST PASS: 3 arms, 0 FAILED.")
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
    a = ap.parse_args()
    if a.selftest:
        return selftest()
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



# ===========================================================================
# AMENDMENT 7 (PROPOSED, PRE-FIRST-GRADED-COMPUTE) -- CLOSED-BOX FRAMES,
# INWARD TICKS, LINE-CONNECTED SERIES.
#
# EVERYTHING ABOVE THIS LINE IS LINES 1-506 OF THE FROZEN BLOB e55d6208,
# BYTE-FOR-BYTE.  The frozen file itself is NOT edited; this file is a proposal
# held beside it until the supervisor reads the diff and promotes it.
#
# WHY.  The frozen instrument REFUSED all three registered figures (commit
# 89d38653): Fig. 5.45 "x-axis line at y=53 does not coincide with the last y
# tick at NONE"; Figs 5.37/5.39 "y-axis line at x=1043 does not coincide with
# the first x tick at 1054.5".  Read from the rendered pages: the thesis plots
# are CLOSED BOX FRAMES with ticks pointing INWARD (major and minor), and
# 5.37 / 5.39 are five LINE-CONNECTED symbol series over a path A|B|C|D with
# full-height partition lines at B and C.  The frozen `find_axes` takes the
# longest inked row (the TOP frame line, which is longer than the bottom one
# once the bottom one is broken by the inward x ticks) and `find_ticks`
# searches OUTSIDE an open L-frame.  The refusals were correct.  The 0.2514 %
# control of S16.7 was an open-frame, outward-tick, isolated-marker raster and
# does not transfer to these figures.
#
# WHAT IS ADDED (method stated, per the supervisor's brief):
#   (a) FRAME: the four frame lines are the outermost rows/columns whose
#       LONGEST CONTIGUOUS ink run is >= FRAME_RUN_FRAC of the largest such run;
#       internal full-height columns are the path partitions.  The page skew is
#       MEASURED from the bottom frame line's row-centre drift and the raster is
#       DE-SKEWED by rotation before anything is read; the residual skew is
#       recorded.  Axis anchors = [near frame edge] + interior MAJOR inward ticks
#       + [far frame edge]; a tick is a thin (<= TICK_MAX_THICK_PX rows/cols)
#       run of ink leaving the frame line into the plot whose centre-line does
#       not drift (a series curve leaving the frame does); majors are the
#       (n_registered - 2) longest, and the instrument refuses unless the
#       shortest chosen major is >= MAJOR_MINOR_RATIO x the longest unchosen
#       tick (an ambiguous major/minor split calibrates nothing).  The frozen
#       `calibrate` (count, uniformity, residual refusals) and the y-sign
#       refusal are reused unchanged.
#   (b) MARKERS: series separation by TEMPLATE MATCHING, not connected
#       components (the 1-bit scan fragments a symbol's stroke into 2-3
#       components, and in a line-connected figure the whole series network is
#       ONE component -- measured: 615 x 409 px, 10316 px, on Fig. 5.39).  For
#       each registered symbol (circle, square, up-triangle, plus, cross) a
#       binary ring/arm template is drawn at the symbol size MEASURED on the
#       crop (5.45: 18 px; 5.37: 13 px; 5.39: 13 px), dilated by the measured
#       ink spread, and correlated with the ink raster by FFT.  The score is the
#       RECALL of template ink (fraction of the template's pixels that are ink
#       in the raster); a connecting line through the symbol does not reduce
#       it.  A marker is a local maximum with recall >= RECALL_ACCEPT whose
#       interior (the hollow, for ring symbols; the four quadrant gaps, for
#       arm symbols) carries <= INTERIOR_MAX_FRAC ink.  Every symbol whose
#       template passes at a location is accepted THERE -- that is the
#       decomposition rule for overlapping symbols (a + over a x, a square
#       enclosing a triangle): no centroid of a merged blob is ever used.  A
#       location where two RING templates both pass within RING_MARGIN of each
#       other is AMBIGUOUS and dropped (reported, never used).
#   (c) TWO NEW PLANTED RASTER CONTROLS in the CLOSED-BOX, INWARD-TICK style,
#       degraded through the SAME measured channel as the frozen control
#       (skew, ink spread, 1-bit threshold, speckle, CCITT G4): a POINTS control
#       shaped like Fig. 5.45 (five symbol series, with a + planted ON a x at
#       the registered abscissa and a square planted ON a triangle, as the real
#       figure has) and a PATH control shaped like Figs 5.37/5.39 (partitions
#       at B and C, five line-connected series with dips at B and C).  The full
#       read runs on each; the instrument REFUSES (exit 2) unless every planted
#       marker is recovered within CLOSED_CONTROL_TOL_FRAC of span.  The
#       recovered-vs-planted MAX and RMS errors, in data units and as % of
#       span, are the new MEASURED digitisation increment for each figure kind.
#   (d) PLANT SIZED TO THE READER (L-340): the 5.45 reader is a per-marker
#       reader, so the points control is graded marker by marker; the 5.37 /
#       5.39 reader delivers a central-80 % partition MEAN, so the path control
#       plants whole series and grades BOTH the per-marker recovery AND the
#       three partition means against the planted truth.
#   (e) REFUSALS PRESERVED / ADDED: abscissa not within ABSCISSA_TOL of the
#       registered Re_H (S10 D1); symbol radius in data units recorded; the
#       blind-repeat spread of five registered points is measured by re-reading
#       the SAME crop under five independent sub-pixel perturbations (shift by
#       a non-integer offset + rotation of +-0.03 deg, bicubic, re-thresholded)
#       -- an algorithmic reader repeats itself exactly on identical input, so
#       the honest repeat is over the resampling the reader is exposed to.
#   (f) SELFTEST: every refusal below is DRIVEN; the mis-anchored closed frame
#       is driven under `python3` AND `python3 -O` by subprocess and must return
#       rc 2 under both; zero `ast.Assert` nodes in this file.
#
# THE SEPARATION OF S10: this lane (the author of this section) did NOT write
# build_t5.py and did NOT open any T5 run directory's solver output while
# producing the reference.
# ===========================================================================
import math

_trapz = getattr(np, "trapezoid", None) or getattr(np, "trapz")

FRAME_RUN_FRAC = 0.60          # a frame line's longest run >= this x the max run
PARTITION_SPAN_FRAC = 0.85     # an internal column spanning >= this of the frame
TICK_PROBE_PX = 60             # a tick is followed this far into the plot
TICK_MIN_LEN_PX = 8            # shorter = frame roughness / speckle
TICK_MAX_THICK_PX = 12         # thicker = not a tick (real strokes are 4-12 px,
                               # MEASURED on page 162; 6 dropped the majors)
LINE_SEARCH_PX = 4             # the frame line is looked for this far either
                               # side of its nominal centre, per row / column
TICK_DRIFT_PX = 2.0            # a tick's centre-line drifts less than this
MAJOR_MINOR_RATIO = 1.3        # shortest major / longest minor must be >= this
EDGE_LOCAL_PX = 80             # frame-edge centre measured over this many px
                               # next to the axis the anchors belong to
RECALL_ACCEPT = 0.82           # template ink fraction present = a marker
INTERIOR_MAX_FRAC = 0.90       # interior ink above this = a SOLID blob (a hollow
                               # symbol with a series line through it measures
                               # 0.5-0.8 at 13 px; only a filled symbol reaches 1)
EXCL_ACCEPT = 0.60             # exclusive-pixel recall vs a co-passing template
MATCH_TOL_FRAC = 0.02          # a recovered marker pairs with a planted one only
                               # within this fraction of span on BOTH axes
PATH_MIN_RECOVERY = 0.90       # fraction of planted in-window markers the path
                               # reader must recover
COPASS_RADIUS_PX = 3           # a co-passing template is looked for within this
ABSCISSA_TOL = 100.0           # S10 D1: registered abscissa +- this
PATH_MIN_PTS = 6               # markers per partition, minimum
PATH_MAX_GAP = 0.22            # path units; larger gap inside the window refuses
PATH_CENTRAL = (0.10, 0.90)    # S7.1: central 80 % of each partition
CLOSED_CONTROL_TOL_FRAC = 0.02 # closed controls must recover within 2 % of span
REPEAT_N = 5                   # S10: five blind re-reads
REPEAT_ROT_DEG = 0.03
REPEAT_SEED = 20260826
FRAME_EXCLUDE_PX = 6           # ink this close to a frame/partition line is not a marker
# ---- A7 CONTINUATION (second lane, 2026-08-26): tick reading and anchoring ----
TICK_GAP_PX = 4                # a tick's ink may break for at most this many px
                               # (MEASURED on the Fig. 5.45 crop: the 60 W/m2K
                               # tick breaks 3 px from the frame, the 2000 tick
                               # 2 px; both were LOST by a contiguous-run reader)
TICK_BAND_PX = 1               # a tick is read over rows/cols +- this: the 2-px
                               # ticks drift one row over their length
MAJOR_MATCH_PX = 6.0           # a found tick is the registered major ONLY within
                               # this of the position the two frame edges predict
PARTITION_TICK_MAX_PX = 25     # a path divider may sit at most this from its
                               # corner tick (MEASURED 10-11 px on 5.37 and 5.39:
                               # the printed dividers are NOT at the corners; the
                               # TICKS are the path anchors, the dividers are not)
CTRL_DIVIDER_OFFSET = 0.034    # the path control draws its dividers this far
                               # outside B and C (path units), as the real
                               # figures do (MEASURED -10.6 / +10.2 px of 310)
INK_DILATE_PX_FROZEN = INK_DILATE_PX   # the frozen control's dilation, untouched
LINE_LINK_PX = 36              # accepted markers of one symbol closer than this
                               # are joined by their series line, whose ink is
                               # claimed for that symbol (real pitch ~14-15 px;
                               # 2.5 pitches bridges one lost marker)
CTRL_TICK_GAP_PX = 3           # the controls break every second tick by this
                               # many px, 6 px from the frame line, as the real
                               # page does (MEASURED 2-4 px)

# ---------------------------------------------------------------------------
# REGISTERED FIGURES.  Page numbers and legends READ FROM THE RENDERED PAGES
# (rule 15) by the author of this section on 2026-08-26; the crops are the
# committed fig*_crop.png files and their crop boxes are recorded beside them
# (verified byte-identical to the same boxes cut from a fresh 300-dpi
# `pdftoppm` render of the page).  Label VALUES are registered, never read from
# the image.  `exclude_px` boxes (crop pixel coordinates) are the in-frame text
# labels REAR / TOP / FRONT read from the page, registered so a letter cannot
# be taken for a symbol.
# ---------------------------------------------------------------------------
FIGURES = {
    "5.45": dict(
        crop="fig545_crop.png", page_printed=160, page_pdf=162,
        crop_box=[300, 320, 1500, 1120], render_dpi=300,
        caption="Face-averaged heat transfer coefficients for the single cube "
                "as a function of the Reynolds number Re_H",
        kind="points", x_name="Re_H", y_name="h", y_units="W/m2K",
        xticks=[0.0, 2000.0, 4000.0, 6000.0], yticks=[0.0, 30.0, 60.0, 90.0],
        symbol_px=18, stroke_px=2,
        # legend read from PDF page 162: + SIDE (N), o FRONT, x SIDE (S),
        # triangle REAR, square TOP
        series=dict(front="circle", top="square", rear="triangle",
                    side_N="plus", side_S="cross"),
        graded=["front", "top", "rear"],
        at=4440.0, exclude_px=[]),
    "5.37": dict(
        crop="fig537_lower_crop.png", page_printed=149, page_pdf=151,
        crop_box=[300, 1500, 1400, 2000], render_dpi=300,
        caption="Profiles of the surface temperature along path ABCDA (upper "
                "plot) and along path ABCD (lower plot) for Re_H = 4440 for "
                "different internal copper temperatures -- LOWER plot",
        kind="path", x_name="location on path ABCD", y_name="T_sur",
        y_units="degC",
        xticks=[0.0, 1.0, 2.0, 3.0], yticks=[40.0, 50.0, 60.0, 70.0],
        # symbol size MEASURED on the crop 2026-08-26 (second lane): circles
        # span 10 rows x 11 columns outside-to-outside with 1-px strokes
        # (rows 268-277, cols 213-235 of the deskewed crop), triangles 10-11
        # px (rows 176-186); the first draft's 13 px found ONE triangle in
        # partition AB (refused).  stroke_px 2 is the template ring width
        # (3 px) on the 1-px-dilated ink, not the page's stroke.
        symbol_px=11, stroke_px=2,
        # legend read from PDF page 151: + 60, o 65, x 70, triangle 75,
        # square 80 degC
        series=dict(T_co_60="plus", T_co_65="circle", T_co_70="cross",
                    T_co_75="triangle", T_co_80="square"),
        registered_series="T_co_75",
        # THE RANK READER READS THIS FIGURE.  The five T_co series never cross
        # (T_sur rises monotonically with T_co; thesis printed p. 148: "the
        # temperature profiles are more or less congruent"), and the legend on
        # PDF page 151 fixes the order: T_co = 80 uppermost, 75 second, then 70,
        # 65, 60.  Registered BEFORE any value was taken.  The symbol reader is
        # kept for this figure only as the control's second opinion -- on the
        # real crop it returns 3 of 66 markers of the registered series and is
        # NOT used to produce a value (see the RANK READER note).
        reader="rank", n_series=5, rank_from_top=2,
        partitions={"AB": "rear", "BC": "top", "CD": "front"},
        # REAR / TOP / FRONT labels inside the frame, read from the page
        exclude_px=[[180, 32, 320, 80], [500, 32, 620, 80], [850, 32, 1010, 80]]),
    "5.39": dict(
        crop="fig539_lower_crop.png", page_printed=151, page_pdf=153,
        crop_box=[300, 870, 1380, 1370], render_dpi=300,
        caption="Distributions of the surface temperature and heat transfer "
                "coefficient along path ABCD parametric in the Reynolds "
                "number -- LOWER plot, h/h_tot",
        kind="path", x_name="location on path ABCD", y_name="h/h_tot",
        y_units="h/h_tot",
        xticks=[0.0, 1.0, 2.0, 3.0], yticks=[0.0, 1.0, 2.0, 3.0],
        # symbol size MEASURED on the crop 2026-08-26: circles 8 rows x 7-8
        # columns (rows 274-281 of the deskewed crop), the smallest symbols of
        # the three figures; the five series overlap almost everywhere
        symbol_px=10, stroke_px=2,
        # caption read from PDF page 153: (+) 2750, (o) 3200, (x) 4000,
        # (triangle) 4440, (square) 4970
        series=dict(Re_2750="plus", Re_3200="circle", Re_4000="cross",
                    Re_4440="triangle", Re_4970="square"),
        registered_series="Re_4440",
        # NO RANK IS REGISTERED FOR 5.39: its five Reynolds-number series
        # OVERLAP AND CROSS -- S7.3 of the pre-registration says so in advance
        # ("a small scanned plot carrying five overlapping Reynolds-number
        # symbol series") -- and the measurement agrees: 29 of 906 in-frame
        # columns resolve into exactly five curves (0 of 907, against the
        # registered 0.50).  The reader REFUSES on this figure and the rows
        # built on it stay absent.  That refusal is the answer, not a defect.
        reader="rank", n_series=5, rank_from_top=None,
        partitions={"AB": "rear", "BC": "top", "CD": "front"},
        # the B tick on the bottom line is NOT PRINTED on this figure: at the
        # predicted 415 px the crop holds two stray pixels (rows yc-12, yc-8 at
        # column 416), read from the raster on 2026-08-26; the C tick is at
        # 725.5 px (0.2 px from the edge prediction).  One absent x major is
        # registered here; the edges + C still give three anchors.  Rows from
        # this figure are REPORTED only (S16.4).
        x_majors_may_be_absent=1,
        exclude_px=[]),
}


# ---------------------------------------------------------------------------
# Raster helpers
# ---------------------------------------------------------------------------
def _longest_runs(ink, axis):
    """Longest contiguous ink run per row (axis=1) or per column (axis=0)."""
    a = ink if axis == 1 else ink.T
    n, m = a.shape
    out = np.zeros(n, dtype=int)
    for i in range(n):
        r = a[i]
        if not r.any():
            continue
        d = np.diff(np.concatenate(([0], r.astype(np.int8), [0])))
        starts = np.where(d == 1)[0]
        ends = np.where(d == -1)[0]
        out[i] = int((ends - starts).max())
    return out


def _groups(idx, gap=1):
    """Consecutive-index groups (start, end) of a sorted index array."""
    if len(idx) == 0:
        return []
    out, s, p = [], idx[0], idx[0]
    for i in idx[1:]:
        if i - p > gap:
            out.append((int(s), int(p)))
            s = i
        p = i
    out.append((int(s), int(p)))
    return out


def _band_sums(ink, axis, win=7):
    """Ink count per row (axis=1) / column (axis=0), summed over a sliding
    window of `win` -- a THIN line that wanders across a few rows because of
    skew still sums to its full length inside the window (measured on Fig.
    5.45: the 1-2 px frame line spreads over rows 51-56 with at most 311 of
    985 px in any one row)."""
    s = ink.sum(axis=axis).astype(float)
    k = np.ones(win)
    return np.convolve(s, k, mode="same")


def _bridged_longest_run(v, gap=6):
    """Longest run of True in v, bridging gaps of <= `gap` False."""
    idx = np.where(v)[0]
    if len(idx) == 0:
        return 0
    best = cur_s = idx[0]; prev = idx[0]; best_len = 1
    for i in idx[1:]:
        if i - prev > gap + 1:
            best_len = max(best_len, prev - cur_s + 1)
            cur_s = i
        prev = i
    return int(max(best_len, prev - cur_s + 1))


def measure_skew_deg(ink, band_rows, x0, x1):
    """Row-centre drift of a horizontal frame line lying inside band_rows."""
    lo, hi = int(band_rows[0]) - 2, int(band_rows[1]) + 3
    xs, ys = [], []
    for x in range(int(x0) + 15, int(x1) - 15):
        col = ink[max(0, lo):hi, x]
        rows = np.where(col)[0]
        if len(rows) == 0 or len(rows) > 6:
            continue
        xs.append(x); ys.append(rows.mean() + max(0, lo))
    if len(xs) < 20:
        return 0.0
    slope = np.polyfit(xs, ys, 1)[0]
    return float(np.degrees(np.arctan(slope)))


def find_frame(ink):
    """Closed box from windowed ink sums: the outermost row-bands and
    column-bands whose windowed sum is >= FRAME_RUN_FRAC of the maximum are the
    frame lines.  Internal columns are partitions only if, in addition, their
    gap-bridged contiguous run spans >= PARTITION_SPAN_FRAC of the frame height
    (a bundle of steep series curves sums high but is not contiguous)."""
    hgt, wid = ink.shape
    rowS = _band_sums(ink, 1)
    colS = _band_sums(ink, 0)
    if rowS.max() < 100 or colS.max() < 100:
        refuse("no closed frame: windowed ink sums peak at %d px in rows and %d "
               "px in columns; a frame line is at least 100 px"
               % (rowS.max(), colS.max()))
    hrows = _groups(np.where(rowS >= FRAME_RUN_FRAC * rowS.max())[0], gap=2)
    vcols = _groups(np.where(colS >= FRAME_RUN_FRAC * colS.max())[0], gap=2)
    if len(hrows) < 2 or len(vcols) < 2:
        refuse("no closed frame: %d horizontal and %d vertical frame-length line "
               "groups found (a closed box has >= 2 of each)"
               % (len(hrows), len(vcols)))
    top, bot = hrows[0], hrows[-1]
    left, right = vcols[0], vcols[-1]
    def centre(group, axis):
        s, e = group
        sub = ink[s:e + 1, :] if axis == 1 else ink[:, s:e + 1]
        prof = sub.sum(axis=axis).astype(float) if axis == 1 else sub.sum(axis=0).astype(float)
        if prof.sum() == 0:
            return (s + e) / 2.0
        return float(s + (prof * np.arange(len(prof))).sum() / prof.sum())
    y0, y1 = centre(top, 1), centre(bot, 1)
    x0, x1 = centre(left, 0), centre(right, 0)
    fh = y1 - y0
    parts = []
    for s, e in vcols[1:-1]:
        if s <= x0 + 10 or e >= x1 - 10:
            continue
        col = ink[int(y0):int(y1) + 1, s:e + 1].any(axis=1)
        if _bridged_longest_run(col) >= PARTITION_SPAN_FRAC * fh:
            # centre from the FULL-HEIGHT columns only: the 7-px window sum
            # widens the group over the series ink converging on the partition
            # (the dips at B and C), and an ink-weighted centre over the whole
            # group landed 10 px inside the true thirds on both real path
            # figures (MEASURED: 5.37 gave 411.9 / 742.8 against 422.6 / 733.0)
            counts = ink[int(y0):int(y1) + 1, s:e + 1].sum(axis=0).astype(float)
            full = counts >= 0.8 * counts.max()
            cols = np.arange(s, e + 1)[full]
            parts.append(float((counts[full] * cols).sum() / counts[full].sum()))
    return dict(x0=x0, x1=x1, y0=y0, y1=y1,
                thick=dict(top=top[1] - top[0] + 1, bottom=bot[1] - bot[0] + 1,
                           left=left[1] - left[0] + 1, right=right[1] - right[0] + 1),
                partitions=parts,
                top_rows=top, bottom_rows=bot, left_cols=left, right_cols=right)


def _line_centre_local(ink, band, along_lo, along_hi, horizontal):
    """Centre of a frame line measured only over [along_lo, along_hi]."""
    lo, hi = band
    if horizontal:
        sub = ink[lo:hi + 1, along_lo:along_hi]
        prof = sub.sum(axis=1).astype(float)
    else:
        sub = ink[along_lo:along_hi, lo:hi + 1]
        prof = sub.sum(axis=0).astype(float)
    if prof.sum() == 0:
        return (lo + hi) / 2.0
    return float(lo + (prof * np.arange(len(prof))).sum() / prof.sum())


def _run_from(ink, r, c, dr, dc, limit):
    """Contiguous ink run from (r, c) stepping (dr, dc), at most `limit`."""
    n = 0
    hgt, wid = ink.shape
    while 0 <= r < hgt and 0 <= c < wid and ink[r, c] and n < limit:
        n += 1
        r += dr
        c += dc
    return n


def _bridged_extent(v, start, step, limit, gap):
    """Distance from `start` along the 1-D bool array v (direction `step`) to
    the LAST ink pixel reachable without crossing more than `gap` consecutive
    white pixels, at most `limit`."""
    n = len(v)
    last = 0
    white = 0
    i = start
    k = 0
    while 0 <= i < n and k < limit:
        if v[i]:
            last = k
            white = 0
        else:
            white += 1
            if white > gap:
                break
        i += step
        k += 1
    return last + 1


def find_inward_ticks(ink, frame):
    """Ticks leave the LEFT frame line rightward and the BOTTOM line upward.

    Per row (left axis) / per column (bottom axis) the ink run from the frame
    line INTO the plot is measured over a band of +-TICK_BAND_PX rows/columns
    (OR-ed) and bridging ink gaps of <= TICK_GAP_PX -- the printed ticks are 2 px
    thin, drift a row over their length and BREAK near the frame (measured, see
    the constants).  Rows without a tick give the line's own half-thickness (the
    median run = baseline); a tick is a group of <= TICK_MAX_THICK_PX adjacent
    rows whose run exceeds the baseline by >= TICK_MIN_LEN_PX and by
    < TICK_PROBE_PX (a series curve leaving the frame runs further, or spreads
    over more rows, and is not a tick).  Returns {"left": [(centre_px,
    length_px)], "bottom": [...]}.  Which ticks are MAJORS is decided by
    POSITION in match_major_ticks, never by length."""
    hgt, wid = ink.shape
    out = {}
    b = TICK_BAND_PX

    def extent_1d(v, c0, step):
        """Inward extent from the nominal line centre c0 along v, starting at
        the ink pixel nearest c0 (within +-LINE_SEARCH_PX across the line)."""
        for o in sorted(range(-LINE_SEARCH_PX, LINE_SEARCH_PX + 1), key=abs):
            c = c0 + o
            if 0 <= c < len(v) and v[c]:
                n = _bridged_extent(v, c, step, TICK_PROBE_PX + 10, TICK_GAP_PX)
                return (o * step) + n
        return 0

    def collect(runs, lo):
        base = float(np.median(runs))
        idx = np.where(runs >= base + TICK_MIN_LEN_PX)[0]
        ticks = []
        for s, e in _groups(idx):
            thick = e - s + 1
            if thick > TICK_MAX_THICK_PX:
                continue
            length = float(np.median(runs[s:e + 1]) - base)
            if TICK_MIN_LEN_PX <= length < TICK_PROBE_PX:
                ticks.append(((s + e) / 2.0 + lo, int(round(length))))
        return ticks
    # ---- left axis: ticks run to the RIGHT from the left line -------------
    xc = int(round(frame["x0"]))
    r_lo, r_hi = int(frame["y0"]) + 4, int(frame["y1"]) - 3
    runs = np.array([extent_1d(ink[max(0, r - b):r + b + 1, :].any(axis=0), xc, +1)
                     for r in range(r_lo, r_hi)])
    out["left"] = collect(runs, r_lo)
    # ---- bottom axis: ticks run UP from the bottom line -------------------
    yc = int(round(frame["y1"]))
    c_lo, c_hi = int(frame["x0"]) + 4, int(frame["x1"]) - 3
    runs = np.array([extent_1d(ink[:, max(0, c - b):c + b + 1].any(axis=1), yc, -1)
                     for c in range(c_lo, c_hi)])
    out["bottom"] = collect(runs, c_lo)
    return out


def match_major_ticks(ticks, px_lo, px_hi, vals, name, allow_missing=0):
    """The registered interior majors, found BY POSITION.

    The two frame edges carry the first and last registered values; they
    predict where every interior major must sit.  A found inward tick within
    MAJOR_MATCH_PX of that prediction IS the major; none there is a refusal
    (the frame edges are not the registered axis ends, or the ticks are not
    readable -- either way no value can be trusted).  Two majors landing on
    one tick refuse.  Tick LENGTH plays no part: on the real page the majors
    are 26-29 px and the minors 10-16 px on one axis and 16 vs 8 px on the
    other, and a length split refused the real figure (16 vs 15 px).  The
    positional match is the stronger test: a minor is a full minor pitch
    (>= 28 px here) from any major position, far outside the tolerance."""
    if len(vals) < 2 or vals[-1] == vals[0]:
        refuse("%s: registered anchor values %s cannot span an axis" % (name, vals))
    v0, v1 = float(vals[0]), float(vals[-1])
    used = {}
    out = []
    missing = []
    for v in vals[1:-1]:
        pred = px_lo + (px_hi - px_lo) * (float(v) - v0) / (v1 - v0)
        best = min(range(len(ticks)), key=lambda i: abs(ticks[i][0] - pred)) \
            if ticks else None
        off = abs(ticks[best][0] - pred) if ticks else float("inf")
        if off > MAJOR_MATCH_PX and len(missing) < allow_missing:
            # registered per figure (x_majors_may_be_absent): the printed tick
            # is absent from the page; recorded, and the edges + the remaining
            # majors still give >= 3 anchors to the uniformity / residual test
            missing.append(dict(value=float(v), predicted_px=float(pred),
                                nearest_tick_px=(None if best is None
                                                 else float(ticks[best][0]))))
            continue
        if best is None:
            refuse("%s: no inward ticks found at all; the registered major %g "
                   "cannot be anchored" % (name, v))
        if off > MAJOR_MATCH_PX:
            refuse("%s: no inward tick within %.1f px of %.1f px, where the two "
                   "frame edges (%.1f, %.1f px = %g, %g) put the registered major "
                   "%g; nearest found tick is %.1f px away (%d ticks found at %s). "
                   "Either the frame edges are not the registered axis ends or "
                   "the ticks are unreadable, and both make every value wrong."
                   % (name, MAJOR_MATCH_PX, pred, px_lo, px_hi, v0, v1, v, off,
                      len(ticks), [round(t[0], 1) for t in ticks]))
        if best in used:
            refuse("%s: registered majors %g and %g both land on the one tick at "
                   "%.1f px -- the registered tick set does not describe this axis"
                   % (name, used[best], v, ticks[best][0]))
        used[best] = v
        out.append(dict(px=float(ticks[best][0]), length_px=int(ticks[best][1]),
                        value=float(v), offset_from_edge_prediction_px=float(off)))
    if not out:
        refuse("%s: none of the registered interior majors %s was found; the "
               "frame edges alone are an untested claim" % (name, list(vals[1:-1])))
    return out, missing


def select_major_ticks(ticks, n_major, name):
    """RETAINED for the selftest arm (G) only; no longer on the reading path.
    The n_major longest ticks, refused unless clearly longer than the rest."""
    if len(ticks) < n_major:
        refuse("%s: %d inward ticks found, %d interior major anchors registered"
               % (name, len(ticks), n_major))
    by_len = sorted(ticks, key=lambda t: -t[1])
    chosen = by_len[:n_major]
    rest = by_len[n_major:]
    if rest and n_major > 0:
        ratio = chosen[-1][1] / float(max(rest[0][1], 1))
        if ratio < MAJOR_MINOR_RATIO:
            refuse("%s: major/minor tick split is ambiguous -- shortest chosen "
                   "major %d px vs longest unchosen %d px (ratio %.2f < %.2f). An "
                   "ambiguous split calibrates nothing." % (name, chosen[-1][1],
                                                            rest[0][1], ratio,
                                                            MAJOR_MINOR_RATIO))
    return sorted(c[0] for c in chosen)

def deskew(ink):
    """Rotate the raster by the MEASURED skew of the bottom frame line."""
    frame = find_frame(ink)
    skew = measure_skew_deg(ink, frame["bottom_rows"], frame["x0"], frame["x1"])
    if abs(skew) < 0.005:
        return ink, skew, 0.0
    im = Image.fromarray(((~ink) * 255).astype(np.uint8))
    im = im.rotate(skew, resample=Image.BICUBIC, fillcolor=255)
    ink2 = np.array(im) < THRESHOLD
    frame2 = find_frame(ink2)
    resid = measure_skew_deg(ink2, frame2["bottom_rows"], frame2["x0"], frame2["x1"])
    return ink2, skew, resid


def calibrate_anchors(px, values, name):
    """The frozen calibrate() with its uniformity test generalised: the
    per-interval SCALE (px per data unit) must be uniform to TICK_UNIFORM_TOL,
    which is the same test when the registered values are evenly spaced and
    the right test when a registered major is absent (5.39: anchors A, C, D
    at 0, 2, 3 -- the pixel spacings are 2:1 by construction, not a fault).
    The linear fit and its FIT_RESID_TOL_PX refusal are unchanged."""
    if len(px) != len(values):
        refuse("%s: %d anchors, %d registered values" % (name, len(px), len(values)))
    if len(px) < 3:
        refuse("%s: %d anchors; three are the minimum for a tested calibration"
               % (name, len(px)))
    dpx = np.diff(np.asarray(px, dtype=float))
    dv = np.diff(np.asarray(values, dtype=float))
    if np.any(dv == 0):
        refuse("%s: two anchors carry the same registered value" % name)
    scale = dpx / dv
    rel = float(np.max(np.abs(scale - scale.mean())) / max(abs(scale.mean()), 1e-9))
    if rel > TICK_UNIFORM_TOL:
        refuse("%s: anchor scale not uniform (max relative departure %.4f > %.4f "
               "over intervals %s px / %s). The axis is not linear or an anchor "
               "is wrong." % (name, rel, TICK_UNIFORM_TOL,
                              [round(float(x), 1) for x in dpx],
                              [float(x) for x in dv]))
    A = np.vstack([np.asarray(px, dtype=float), np.ones(len(px))]).T
    coef, *_ = np.linalg.lstsq(A, np.asarray(values, dtype=float), rcond=None)
    resid_data = A @ coef - np.asarray(values, dtype=float)
    s = abs(coef[0]) if abs(coef[0]) > 1e-12 else 1e-12
    resid_px = float(np.max(np.abs(resid_data)) / s)
    if resid_px > FIT_RESID_TOL_PX:
        refuse("%s: linear fit residual %.3f px > %.3f px. The axis is not linear "
               "in pixels and a linear map would be wrong everywhere."
               % (name, resid_px, FIT_RESID_TOL_PX))
    return float(coef[0]), float(coef[1]), resid_px


def calibrate_closed(ink, frame, xticks, yticks, kind, x_majors_may_be_absent=0):
    """Anchors: the frame edges (registered first / last values) plus the
    interior majors matched BY POSITION on both axes.  For a path figure the x
    anchors are the corner TICKS at B and C, not the printed dividers: the
    dividers are checked to sit within PARTITION_TICK_MAX_PX of their tick and
    are then used only as marker-exclusion zones."""
    ticks = find_inward_ticks(ink, frame)
    lo, hi = int(frame["x0"]) + frame["thick"]["left"] + 2, \
        int(frame["x0"]) + frame["thick"]["left"] + 2 + EDGE_LOCAL_PX
    y_top = _line_centre_local(ink, frame["top_rows"], lo, hi, True)
    y_bot = _line_centre_local(ink, frame["bottom_rows"], lo, hi, True)
    lo_y, hi_y = int(frame["y1"]) - frame["thick"]["bottom"] - 2 - EDGE_LOCAL_PX, \
        int(frame["y1"]) - frame["thick"]["bottom"] - 2
    x_left = _line_centre_local(ink, frame["left_cols"], lo_y, hi_y, False)
    x_right = _line_centre_local(ink, frame["right_cols"], lo_y, hi_y, False)
    # y: pixel rows ascend as data descends -> predict from top=last value
    y_major, y_missing = match_major_ticks(ticks["left"], y_top, y_bot,
                                           list(reversed(yticks)), "y-axis")
    ypx = [y_top] + sorted(m["px"] for m in y_major) + [y_bot]
    yvals = [yticks[-1]] + sorted((m["value"] for m in y_major), reverse=True) + [yticks[0]]
    x_major, x_missing = match_major_ticks(ticks["bottom"], x_left, x_right,
                                           list(xticks), "x-axis",
                                           allow_missing=x_majors_may_be_absent)
    xpx = [x_left] + sorted(m["px"] for m in x_major) + [x_right]
    xvals = [xticks[0]] + sorted(m["value"] for m in x_major) + [xticks[-1]]
    divider_offsets = None
    if kind == "path":
        n_x_major = len(xticks) - 2
        if len(frame["partitions"]) != n_x_major:
            refuse("path figure: %d full-height partition lines found, %d "
                   "registered (%s). A mismatch means the figure is not the "
                   "registered one." % (len(frame["partitions"]), n_x_major, xticks))
        divider_offsets = []
        for m in sorted(x_major, key=lambda d: d["px"]):
            near = min(frame["partitions"], key=lambda p: abs(p - m["px"]))
            if abs(near - m["px"]) > PARTITION_TICK_MAX_PX:
                refuse("path figure: the divider nearest the corner tick %g at "
                       "%.1f px is %.1f px away (> %d). The dividers must sit at "
                       "the path corners; this figure's do not."
                       % (m["value"], m["px"], abs(near - m["px"]),
                          PARTITION_TICK_MAX_PX))
            divider_offsets.append(dict(corner=m["value"], tick_px=m["px"],
                                        divider_px=float(near),
                                        offset_px=float(near - m["px"])))
    ax_, bx_, rx = calibrate_anchors(xpx, xvals, "x-axis")
    ay_, by_, ry = calibrate_anchors(ypx, yvals, "y-axis")
    if ay_ >= 0.0:
        refuse("y-axis calibration has a non-negative scale (%.6g data per px); "
               "the anchor order is wrong and every value would be reflected"
               % ay_)
    return dict(x=[ax_, bx_], y=[ay_, by_], max_resid_px=dict(x=rx, y=ry),
                anchors_px=dict(x=[float(v) for v in xpx],
                                y=[float(v) for v in ypx]),
                anchors_data=dict(x=list(xticks), y=list(yticks)),
                majors_matched=dict(x=x_major, y=y_major),
                majors_absent=dict(x=x_missing, y=y_missing),
                divider_offsets=divider_offsets,
                ticks_found=dict(left=[[float(c), int(l)] for c, l in ticks["left"]],
                                 bottom=[[float(c), int(l)] for c, l in ticks["bottom"]]))

def make_template(symbol, size_px, stroke_px):
    """Binary (ring, interior) masks for a symbol drawn at size_px."""
    n = size_px + 2 * stroke_px + 2
    n += (n % 2 == 0)              # odd, so the template has a centre PIXEL and a
                                   # correlation peak sits on the symbol centre
    c = (n - 1) / 2.0
    yy, xx = np.mgrid[0:n, 0:n]
    dx, dy = xx - c, yy - c
    r = size_px / 2.0
    # `interior` is the region a SOLID blob would fill and a hollow symbol leaves
    # white: inset from the ring by stroke + 1 px (the measured 1-px ink spread
    # thickens every real stroke).  The up-triangle has NO interior worth
    # testing -- its inradius is 0.309 x size (4.0 px at 13 px), so after the
    # inset a few pixels remain and any series line through the symbol fills
    # them (measured on the path control: six planted triangles with recall
    # 0.94-0.98 rejected at interior 0.8-1.0).  Its solid-blob protection is
    # the exclusive-evidence rule in find_symbol_markers and the controls'
    # spurious-marker refusal.
    if symbol == "circle":
        d = np.sqrt(dx ** 2 + dy ** 2)
        ring = np.abs(d - r) <= stroke_px / 2.0 + 0.5
        interior = d < r - stroke_px - 1.0
    elif symbol == "square":
        d = np.maximum(np.abs(dx), np.abs(dy))
        ring = np.abs(d - r) <= stroke_px / 2.0 + 0.5
        interior = d < r - stroke_px - 1.0
    elif symbol == "triangle":
        # up-triangle in the size box: apex up, base width = height = size_px
        h = float(size_px)
        w = size_px / 2.0
        verts = [(0.0, -h / 2.0), (-w, h / 2.0), (w, h / 2.0)]
        ds = []
        for i in range(3):
            p1, p2 = verts[i], verts[(i + 1) % 3]
            ex, ey = p2[0] - p1[0], p2[1] - p1[1]
            ln = math.hypot(ex, ey)
            s = (ex * (dy - p1[1]) - ey * (dx - p1[0])) / ln
            sc = (ex * (h / 6.0 - p1[1]) - ey * (0.0 - p1[0])) / ln  # centroid
            ds.append(s if sc > 0 else -s)
        dist = np.minimum(np.minimum(ds[0], ds[1]), ds[2])   # inside positive
        ring = np.abs(dist) <= stroke_px / 2.0 + 0.5
        interior = np.zeros_like(ring)                       # none: see above
    elif symbol == "plus":
        ring = (np.abs(dx) <= stroke_px / 2.0 + 0.5) & (np.abs(dy) <= r) | \
               (np.abs(dy) <= stroke_px / 2.0 + 0.5) & (np.abs(dx) <= r)
        interior = (np.abs(dx) > stroke_px + 1.5) & (np.abs(dy) > stroke_px + 1.5) & \
                   (np.maximum(np.abs(dx), np.abs(dy)) < r * 0.8)
    elif symbol == "cross":
        u, v = (dx + dy) / math.sqrt(2), (dx - dy) / math.sqrt(2)
        ring = (np.abs(u) <= stroke_px / 2.0 + 0.5) & (np.abs(v) <= r) | \
               (np.abs(v) <= stroke_px / 2.0 + 0.5) & (np.abs(u) <= r)
        interior = (np.abs(u) > stroke_px + 1.5) & (np.abs(v) > stroke_px + 1.5) & \
                   (np.maximum(np.abs(u), np.abs(v)) < r * 0.8)
    else:
        refuse("unknown symbol %r" % symbol)
    return ring.astype(np.float32), interior.astype(np.float32)


def _corr(ink_f, mask):
    from scipy import signal
    return signal.fftconvolve(ink_f, mask[::-1, ::-1], mode="same")


def template_maps(ink, symbols, size_px, stroke_px):
    """Recall, interior and pairwise EXCLUSIVE-recall maps for every symbol.

    recall_s(x,y)      = fraction of template s's ring pixels that are ink
    interior_s(x,y)    = fraction of template s's interior pixels that are ink
    excl_{s,t}(x,y)    = recall of s over the ring pixels of s that are NOT
                         within one stroke of t's ring (same centre).
    The exclusive map is what separates a lone square (circle recall 0.85 on
    the control, above RECALL_ACCEPT) from a genuine circle: the circle's
    exclusive pixels against the square are its diagonal arcs, and a lone
    square has no ink there."""
    from scipy import ndimage
    ink_f = ink.astype(np.float32)
    tpl = {s: make_template(s, size_px, stroke_px) for s in symbols}
    n = max(t[0].shape[0] for t in tpl.values())
    def pad(m):
        out = np.zeros((n, n), np.float32)
        o = (n - m.shape[0]) // 2
        out[o:o + m.shape[0], o:o + m.shape[1]] = m
        return out
    ring = {s: pad(tpl[s][0]) for s in symbols}
    inter = {s: pad(tpl[s][1]) for s in symbols}
    maps = dict(recall={}, interior={}, recall_nbhd={})
    fp = np.ones((2 * COPASS_RADIUS_PX + 1, 2 * COPASS_RADIUS_PX + 1), bool)
    for s in symbols:
        maps["recall"][s] = _corr(ink_f, ring[s]) / max(ring[s].sum(), 1.0)
        maps["recall_nbhd"][s] = ndimage.maximum_filter(maps["recall"][s], footprint=fp)
        # interior map is None for a symbol with no testable interior (triangle)
        maps["interior"][s] = (_corr(ink_f, inter[s]) / inter[s].sum()) \
            if inter[s].sum() >= 8 else None
    return maps


def _paint(img, mask, cy, cx, value):
    """Add `value` x mask into img centred on (cy, cx); mask has odd side."""
    n = mask.shape[0]; o = n // 2
    y0, x0 = cy - o, cx - o
    ys, xs = slice(max(0, y0), min(img.shape[0], y0 + n)), \
        slice(max(0, x0), min(img.shape[1], x0 + n))
    img[ys, xs] += value * mask[ys.start - y0:ys.stop - y0, xs.start - x0:xs.stop - x0]


def explain_away(ink, cands, size_px, stroke_px):
    """THE SERIES-SEPARATION RULE for overlapping and touching symbols.

    Candidates are accepted in descending recall.  Every accepted marker CLAIMS
    the ink under its ring dilated by stroke//2 + 1 px.  A marker stands only on
    the pixels of its own ring that no OTHER accepted marker claims: it needs
    >= 8 such pixels and >= EXCL_ACCEPT of them inked.  The lowest-recall marker
    failing that is dropped and the claims are rebuilt, to a fixed point.

    What this does, measured on the points control: a + between a square and a
    triangle 10 px apart (recall 0.85, every ring pixel under their ink) is
    dropped; a circle whose ring is the union of a triangle's base and a cross's
    arms is dropped; a circle on a real square is dropped (0 pixels clear of the
    square at 18 or 13 px, MEASURED); a + planted ON a x keeps its arms beyond
    the centre (56 px clear at 18 px) and a triangle inside a square keeps its
    legs (132 px clear), so both planted coincidences of the real Fig. 5.45 are
    read as TWO markers and no merged-blob centroid is ever used."""
    from scipy import ndimage
    if not cands:
        return [], []
    ring, grown = {}, {}
    for s in set(d["symbol"] for d in cands):
        r = make_template(s, size_px, stroke_px)[0] > 0
        ring[s] = r
        grown[s] = ndimage.binary_dilation(r, iterations=stroke_px // 2 + 1).astype(np.int16)
    accepted = sorted(cands, key=lambda d: -d["recall"])
    dropped = []
    lw = stroke_px + 2
    while True:
        claim = np.zeros(ink.shape, np.int16)
        for d in accepted:
            _paint(claim, grown[d["symbol"]], int(d["py"]), int(d["px"]), 1)
        # THE SERIES LINE IS CLAIMED TOO: consecutive accepted markers of one
        # symbol closer than LINE_LINK_PX are joined by their series line, and
        # that line's ink (width stroke + 2) is claimed for that symbol.  On
        # the path control two adjacent squares 14 px apart plus the line
        # between them gave a TRIANGLE template 77 unclaimed ring pixels at
        # recall 0.82 -- a spurious marker of the registered symbol inside a
        # central window, which the control refused (measured 2026-08-26).
        # A marker of symbol s is tested against the lines of OTHER symbols
        # only: its own series line legitimately runs through its ring.
        line_claim = {}
        for s in set(d["symbol"] for d in accepted):
            pts = sorted((d for d in accepted if d["symbol"] == s), key=lambda d: d["px"])
            lc = np.zeros(ink.shape, np.int16)
            for a, b in zip(pts, pts[1:]):
                if math.hypot(b["px"] - a["px"], b["py"] - a["py"]) > LINE_LINK_PX:
                    continue
                n = int(math.hypot(b["px"] - a["px"], b["py"] - a["py"])) + 1
                for t in np.linspace(0.0, 1.0, 2 * n + 1):
                    cy = int(round(a["py"] + t * (b["py"] - a["py"])))
                    cx = int(round(a["px"] + t * (b["px"] - a["px"])))
                    lc[max(0, cy - lw // 2):cy + lw // 2 + 1,
                       max(0, cx - lw // 2):cx + lw // 2 + 1] = 1
            line_claim[s] = lc
        worst = None
        for d in accepted:
            r = ring[d["symbol"]]; n = r.shape[0]; o = n // 2
            cy, cx = int(d["py"]), int(d["px"])
            win = claim[cy - o:cy + o + 1, cx - o:cx + o + 1]
            if win.shape != r.shape:
                d["unclaimed_px"], d["unclaimed_recall"] = None, None
                continue                        # touches the raster edge: untestable
            others = win - grown[d["symbol"]]
            for s, lc in line_claim.items():
                if s != d["symbol"]:
                    others = others + lc[cy - o:cy + o + 1, cx - o:cx + o + 1]
            unclaimed = r & (others <= 0)
            n_un = int(unclaimed.sum())
            inkwin = ink[cy - o:cy + o + 1, cx - o:cx + o + 1]
            rec = float(inkwin[unclaimed].mean()) if n_un >= 8 else None
            d["unclaimed_px"], d["unclaimed_recall"] = n_un, rec
            if rec is None or rec < EXCL_ACCEPT:
                if worst is None or d["recall"] < worst["recall"]:
                    worst = d
        if worst is None:
            break
        worst["rejected"] = ("explained by neighbouring markers: %d ring px unclaimed, "
                             "recall on them %s"
                             % (worst["unclaimed_px"],
                                "n/a" if worst["unclaimed_recall"] is None
                                else "%.2f" % worst["unclaimed_recall"]))
        dropped.append(worst)
        accepted = [d for d in accepted if d is not worst]
    return accepted, dropped


def stroke_px_of(_exclude_px):
    """Registered stroke width shared by every figure (2 px); a helper so the
    exclusion growth is stated in one place."""
    return 2


def find_symbol_markers(ink, frame, symbol, size_px, exclude_px, maps, symbols):
    """All locations where `symbol`'s template passes the three rules."""
    from scipy import ndimage
    rec = maps["recall"][symbol]
    inte = maps["interior"][symbol]
    m = FRAME_EXCLUDE_PX + size_px // 2
    valid = np.zeros_like(ink, dtype=bool)
    valid[int(frame["y0"]) + m:int(frame["y1"]) - m,
          int(frame["x0"]) + m:int(frame["x1"]) - m] = True
    for p in frame["partitions"]:
        valid[:, max(0, int(p) - m):int(p) + m + 1] = False
    # an exclusion box keeps out every candidate whose RING would overlap it,
    # not only the candidates centred inside it: on the path control a square
    # of an excluded series sat just inside the TOP label box and a TRIANGLE
    # template centred 8 px outside the box stood on that square's ink plus
    # the series line (recall 0.84, 77 unclaimed ring px at 0.82) -- a spurious
    # marker of the registered symbol, which the control refused (2026-08-26)
    g = size_px // 2 + stroke_px_of(exclude_px) + 1
    for (ex0, ey0, ex1, ey1) in exclude_px:
        valid[max(0, ey0 - g):ey1 + g, max(0, ex0 - g):ex1 + g] = False
    score = np.where(valid, rec, 0.0)
    footprint = np.ones((int(size_px * 0.7) | 1, int(size_px * 0.7) | 1), bool)
    mx = ndimage.maximum_filter(score, footprint=footprint)
    cand = np.where((score >= RECALL_ACCEPT) & (score >= mx - 1e-6))
    out, rejected = [], []
    for py, px in zip(*cand):
        d = dict(px=float(px), py=float(py), recall=float(score[py, px]),
                 interior_frac=(None if inte is None else float(inte[py, px])),
                 symbol=symbol)
        if inte is not None and inte[py, px] > INTERIOR_MAX_FRAC:
            # a + planted ON a x fills each other's quadrant gaps: the interior
            # rule is waived for an ARM symbol when the other arm symbol also
            # passes here (the asterisk case of the real figure at Re_H 4440)
            other = {"plus": "cross", "cross": "plus"}.get(symbol)
            if not (other in symbols and maps["recall_nbhd"][other][py, px] >= RECALL_ACCEPT):
                d["rejected"] = "interior %.2f" % inte[py, px]; rejected.append(d); continue
        # separation from other symbols' ink is decided AFTER all symbols'
        # candidates are known, in explain_away()
        out.append(d)
    out.sort(key=lambda d: -d["recall"])
    kept = []
    for d in out:
        if all(math.hypot(d["px"] - k["px"], d["py"] - k["py"]) > size_px * 0.5
               for k in kept):
            kept.append(d)
    return kept, rejected


RING_SYMBOLS = ("circle", "square", "triangle")


MATCH_DILATE_PX = 1            # the ink is dilated by this before template
                               # matching: the PRINTED symbol strokes are 1-2 px
                               # (MEASURED on the Fig. 5.45 crop: circle ring
                               # 1-2 px, outer diameter 19-20 px) and a 3-px
                               # template ring over a 1.5-px stroke reads recall
                               # ~0.5 however well centred; dilated by 1 px the
                               # stroke fills the ring.  Positions are unchanged
                               # (dilation is symmetric); the controls travel the
                               # same step.


def classify_markers(ink, frame, fig):
    """Every registered symbol's markers under the recall / interior /
    exclusive-recall rules; rejected candidates are returned for the record."""
    from scipy import ndimage
    symbols = sorted(set(fig["series"].values()))
    ink_m = ndimage.binary_dilation(ink, iterations=MATCH_DILATE_PX) \
        if MATCH_DILATE_PX > 0 else ink
    maps = template_maps(ink_m, symbols, fig["symbol_px"], fig["stroke_px"])
    cands, rejected = [], []
    for s in symbols:
        k, r = find_symbol_markers(ink_m, frame, s, fig["symbol_px"],
                                   fig["exclude_px"], maps, symbols)
        cands.extend(k)
        rejected.extend(r)
    kept, dropped = explain_away(ink_m, cands, fig["symbol_px"], fig["stroke_px"])
    rejected.extend(dropped)
    by_symbol = {s: sorted([d for d in kept if d["symbol"] == s], key=lambda d: -d["recall"])
                 for s in symbols}
    return by_symbol, rejected


def to_data(cal, px, py):
    return cal["x"][0] * px + cal["x"][1], cal["y"][0] * py + cal["y"][1]


# ---------------------------------------------------------------------------
# The two readers
# ---------------------------------------------------------------------------
def read_points_figure(ink, fig, verbose=False):
    frame = find_frame(ink)
    cal = calibrate_closed(ink, frame, fig["xticks"], fig["yticks"], "points")
    by_symbol, rejected = classify_markers(ink, frame, fig)
    series = {}
    for name, sym in fig["series"].items():
        pts = []
        for d in by_symbol[sym]:
            x, y = to_data(cal, d["px"], d["py"])
            pts.append(dict(x=x, y=y, px=d["px"], py=d["py"], recall=d["recall"]))
        pts.sort(key=lambda p: p["x"])
        series[name] = pts
    return dict(frame=dict(x0=frame["x0"], x1=frame["x1"], y0=frame["y0"],
                           y1=frame["y1"], partitions=frame["partitions"]),
                calibration=cal, series=series,
                rejected=[dict(px=a["px"], py=a["py"], symbol=a["symbol"],
                               why=a["rejected"]) for a in rejected],
                symbol_radius_data=abs(cal["y"][0]) * fig["symbol_px"] / 2.0)


def value_at_abscissa(series_pts, at, name):
    """The marker nearest the registered abscissa; S10 D1 refusal."""
    if not series_pts:
        refuse("%s: no marker of the registered symbol was found anywhere in "
               "the frame" % name)
    best = min(series_pts, key=lambda p: abs(p["x"] - at))
    if abs(best["x"] - at) > ABSCISSA_TOL:
        refuse("%s: nearest marker abscissa %.1f is not within +-%.0f of the "
               "registered %.1f (S10 D1)" % (name, best["x"], ABSCISSA_TOL, at))
    return best


def partition_mean(pts, lo, hi, name):
    """Arc-length-weighted mean of the linear interpolant over [lo, hi] of a
    partition, from that partition's markers.  Refuses on sparse coverage."""
    pts = sorted(pts, key=lambda p: p["x"])
    if len(pts) < PATH_MIN_PTS:
        refuse("%s: %d markers in the partition, %d required"
               % (name, len(pts), PATH_MIN_PTS))
    xs = np.array([p["x"] for p in pts])
    ys = np.array([p["y"] for p in pts])
    span = hi - lo
    wlo, whi = lo + PATH_CENTRAL[0] * span, lo + PATH_CENTRAL[1] * span
    if xs[0] > wlo + PATH_MAX_GAP * span or xs[-1] < whi - PATH_MAX_GAP * span:
        refuse("%s: markers cover [%.3f, %.3f] but the central window is "
               "[%.3f, %.3f] (max gap %.2f of the partition)"
               % (name, xs[0], xs[-1], wlo, whi, PATH_MAX_GAP))
    inwin = (xs >= wlo - PATH_MAX_GAP * span) & (xs <= whi + PATH_MAX_GAP * span)
    gaps = np.diff(xs[inwin])
    if len(gaps) and gaps.max() > PATH_MAX_GAP * span:
        refuse("%s: a gap of %.3f path units between consecutive markers inside "
               "the central window exceeds %.3f" % (name, gaps.max(),
                                                    PATH_MAX_GAP * span))
    grid = np.linspace(wlo, whi, 401)
    vals = np.interp(grid, xs, ys)          # flat beyond the ends, inside tol
    return float(_trapz(vals, grid) / (whi - wlo)), int(inwin.sum())


def read_path_figure(ink, fig, verbose=False):
    frame = find_frame(ink)
    cal = calibrate_closed(ink, frame, fig["xticks"], fig["yticks"], "path",
                           fig.get("x_majors_may_be_absent", 0))
    by_symbol, rejected = classify_markers(ink, frame, fig)
    sym = fig["series"][fig["registered_series"]]
    pts = []
    for d in by_symbol[sym]:
        x, y = to_data(cal, d["px"], d["py"])
        pts.append(dict(x=x, y=y, px=d["px"], py=d["py"], recall=d["recall"]))
    pts.sort(key=lambda p: p["x"])
    parts = {}
    xt = fig["xticks"]
    for i, (pname, face) in enumerate(fig["partitions"].items()):
        lo, hi = xt[i], xt[i + 1]
        sub = [p for p in pts if lo <= p["x"] <= hi]
        parts[pname] = dict(face=face, lo=lo, hi=hi, n_markers=len(sub),
                            points=sub)
    return dict(frame=dict(x0=frame["x0"], x1=frame["x1"], y0=frame["y0"],
                           y1=frame["y1"], partitions=frame["partitions"]),
                calibration=cal, series_points=pts, partitions=parts,
                other_symbols={s: len(v) for s, v in by_symbol.items()},
                rejected_n=len(rejected),
                symbol_radius_data=abs(cal["y"][0]) * fig["symbol_px"] / 2.0)


def load_ink(path):
    return load_bitonal(path)


def perturbed_copies(ink, n, seed):
    """n independent sub-pixel resamplings of the same raster (blind repeats)."""
    rng = np.random.default_rng(seed)
    im = Image.fromarray(((~ink) * 255).astype(np.uint8))
    out = []
    for _ in range(n):
        ang = float(rng.uniform(-REPEAT_ROT_DEG, REPEAT_ROT_DEG))
        sx, sy = float(rng.uniform(-0.5, 0.5)), float(rng.uniform(-0.5, 0.5))
        j = im.rotate(ang, resample=Image.BICUBIC, fillcolor=255)
        j = j.transform(j.size, Image.AFFINE, (1, 0, sx, 0, 1, sy),
                        resample=Image.BICUBIC, fillcolor=255)
        out.append(np.array(j) < THRESHOLD)
    return out


# ---------------------------------------------------------------------------
# Channel degradation, identical in every step to the frozen control's
# ---------------------------------------------------------------------------
CTRL_LW_FRAME_PT = 1.6         # frame line 6-7 px  (MEASURED on all three crops)
CTRL_LW_TICK_PT = 0.5          # ticks 2 px          (measured, Fig. 5.45 / 5.37)
CTRL_LW_MARKER_PT = 0.45       # symbol stroke 1-2 px (measured, Fig. 5.45 circles)
CTRL_LW_SERIES_PT = 0.35       # series line 1-2 px   (measured, Fig. 5.37)
CTRL_INK_DILATE_PX = 0         # the closed controls are drawn AT the page's
                               # measured stroke widths and are NOT dilated: the
                               # frozen control's +1 px dilation (INK_DILATE_PX)
                               # modelled ink spread on top of matplotlib's
                               # default 0.5-pt marker edge and produced 3-4 px
                               # symbol strokes, twice the page's; a reader tuned
                               # on those found NO circle on the real Fig. 5.45
                               # (measured 2026-08-26).  Skew, 1-bit threshold,
                               # speckle, G4 round-trip and planted tick breaks
                               # are unchanged.


def degrade_to_channel(grey_png, out_path, seed=20260826, tick_bases=None,
                       dilate_px=None):
    im = Image.open(grey_png).convert("L")
    im = im.rotate(SKEW_DEG, resample=Image.BICUBIC, fillcolor=255)
    arr = np.array(im)
    INK_DILATE_PX = INK_DILATE_PX_FROZEN if dilate_px is None else dilate_px
    if INK_DILATE_PX > 0:
        from scipy import ndimage as _nd
        dark = arr < THRESHOLD
        dark = _nd.binary_dilation(dark, iterations=INK_DILATE_PX)
        arr = np.where(dark, 0, arr).astype(np.uint8)
    bilevel = (arr >= THRESHOLD).astype(np.uint8) * 255
    # PLANTED TICK BREAKS: every second tick is cut by CTRL_TICK_GAP_PX white
    # pixels, 6 px inside the frame line, as the printed ticks are (measured).
    # tick_bases are (row, col, drow, dcol) in the UNROTATED render; the
    # SKEW_DEG rotation is applied about the image centre by PIL, so the same
    # rotation is applied to the base points here.
    n_gaps = 0
    if tick_bases:
        th = math.radians(SKEW_DEG)
        cy0, cx0 = (arr.shape[0] - 1) / 2.0, (arr.shape[1] - 1) / 2.0
        for i, (r, c, dr, dc) in enumerate(tick_bases):
            if i % 2:
                continue
            # PIL rotate(angle) is counter-clockwise in image coordinates
            x, y = c - cx0, r - cy0
            xr = x * math.cos(th) + y * math.sin(th)
            yr = -x * math.sin(th) + y * math.cos(th)
            rr, cc = int(round(yr + cy0)), int(round(xr + cx0))
            for k in range(6, 6 + CTRL_TICK_GAP_PX):
                gr, gc = rr + dr * k, cc + dc * k
                if dr:
                    bilevel[gr, max(0, gc - 3):gc + 4] = 255
                else:
                    bilevel[max(0, gr - 3):gr + 4, gc] = 255
            n_gaps += 1
    rng = np.random.default_rng(seed)
    n_spk = int(SPECKLE_FRAC * 2478)
    hgt, wid = bilevel.shape
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
    Image.fromarray(bilevel).convert("1").save(out_path, format="TIFF",
                                               compression=SCAN_ENCODER)
    reloaded = np.array(Image.open(out_path).convert("L"))
    return dict(render_dpi=RENDER_DPI, bits_per_channel=SCAN_BPC,
                threshold=THRESHOLD, encoder=SCAN_ENCODER, skew_deg=SKEW_DEG,
                speckle_frac=SPECKLE_FRAC, ink_dilate_px=INK_DILATE_PX,
                render_lw_pt=dict(frame=CTRL_LW_FRAME_PT, tick=CTRL_LW_TICK_PT,
                                  marker=CTRL_LW_MARKER_PT, series=CTRL_LW_SERIES_PT)
                if dilate_px is not None else "frozen control (matplotlib defaults)",
                speckle_blobs_planted=n_spk,
                tick_breaks_planted=n_gaps, tick_break_px=CTRL_TICK_GAP_PX,
                raster_px=[int(reloaded.shape[1]), int(reloaded.shape[0])],
                distinct_grey_levels_after_roundtrip=int(np.unique(reloaded).size))


MPL_MARKER = dict(circle="o", square="s", triangle="^", plus="+", cross="x")


def _tick_bases(f, ax):
    """(row, col, drow, dcol) of every bottom/left tick's base in the saved
    raster: the point on the frame line where the tick starts, and the inward
    direction.  Read from the axes transform, not from the image."""
    f.canvas.draw()
    hgt = int(round(f.get_figheight() * f.dpi))
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    out = []
    for xt in list(ax.get_xticks()) + list(ax.get_xticks(minor=True)):
        if not (x0 < xt < x1):
            continue
        px, py = ax.transData.transform((xt, y0))
        out.append((int(round(hgt - 1 - py)), int(round(px)), -1, 0))
    for yt in list(ax.get_yticks()) + list(ax.get_yticks(minor=True)):
        if not (y0 < yt < y1):
            continue
        px, py = ax.transData.transform((x0, yt))
        out.append((int(round(hgt - 1 - py)), int(round(px)), 0, +1))
    return out


def _style_axes(ax, xticks, yticks, xminor, yminor, size_pt, lw,
                xmaj_pt=4.3, ymaj_pt=7.0, minor_pt=3.0):
    """Tick lengths in points, per axis, AS MEASURED on the printed figures at
    300 dpi (4.17 px/pt): Fig. 5.45 y majors 29 px, x majors 18 px, minors
    8-16 px; Fig. 5.37 y majors 27 px, x majors 12-18 px, minors 9-13 px.  A
    control with 37-px ticks (matplotlib's default 9 pt) is not the page."""
    ax.set_xlim(xticks[0], xticks[-1]); ax.set_ylim(yticks[0], yticks[-1])
    ax.set_xticks(xticks); ax.set_yticks(yticks)
    ax.set_xticks(xminor, minor=True); ax.set_yticks(yminor, minor=True)
    ax.tick_params(which="major", direction="in", width=CTRL_LW_TICK_PT,
                   labelsize=size_pt, top=True, right=True)
    ax.tick_params(axis="x", which="major", length=xmaj_pt)
    ax.tick_params(axis="y", which="major", length=ymaj_pt)
    ax.tick_params(which="minor", direction="in", length=minor_pt,
                   width=CTRL_LW_TICK_PT, top=True, right=True)
    for s in ax.spines.values():
        s.set_linewidth(lw)


# ---------------------------------------------------------------------------
# CONTROL 1: closed-frame POINTS figure shaped like Fig. 5.45
# ---------------------------------------------------------------------------
POINTS_CTRL_RE = [533.0, 890.0, 1350.0, 1800.0, 2220.0, 2753.0, 3197.0,
                  3996.0, 4440.0, 4973.0]


POINTS_CTRL_TRUTH = {
    # values laid out like the real Fig. 5.45 (read by eye from the page for
    # LAYOUT only -- these are the CONTROL's planted values, not the reference)
    "front":  [28.7, 38.4, 47.6, 55.3, 61.4, 67.2, 72.1, 77.8, 83.2, 84.9],
    "rear":   [8.6, 10.8, 17.9, 35.4, 44.3, 44.1, 49.6, 52.7, 57.9, 60.7],
    "top":    [12.6, 11.3, 13.4, 16.7, 19.6, 35.2, 41.1, 51.3, 54.4, 60.7],
    "side_N": [12.9, 11.9, 15.3, 17.1, 23.1, 43.6, 50.8, 60.1, 65.4, 67.4],
    "side_S": [13.6, 14.1, 12.7, 17.3, 21.1, 42.0, 47.1, 57.2, 65.4, 64.9],
}
# planted coincidences, as the real figure has them: side_N ON side_S at 4440
# (+ on x -> the asterisk blob), top ON rear at 4973 (square enclosing triangle)
POINTS_CTRL_GATED_RE_MIN = 3000.0   # every marker at Re >= this must be recovered;
                                    # the reader reads at 4440 +- 100 and the four
                                    # abscissae >= 3000 bracket it at the real
                                    # figure's spacing; below 3000 the real figure
                                    # piles hollow and arm symbols INSIDE each other
                                    # (Re 533-2753), which this reader is NOT claimed
                                    # to resolve -- recovery there is REPORTED


def points_control_truth():
    return {name: [(float(r), float(v)) for r, v in zip(POINTS_CTRL_RE, vals)]
            for name, vals in POINTS_CTRL_TRUTH.items()}


def build_points_control(path, fig):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    truth = points_control_truth()
    f = plt.figure(figsize=(4.6, 3.0), dpi=RENDER_DPI)
    ax = f.add_axes([0.14, 0.14, 0.714, 0.713])
    size_pt = fig["symbol_px"] * 72.0 / RENDER_DPI
    for name, sym in fig["series"].items():
        xs = [p[0] for p in truth[name]]; ys = [p[1] for p in truth[name]]
        ax.plot(xs, ys, linestyle="none", marker=MPL_MARKER[sym], markersize=size_pt,
                markerfacecolor="none", markeredgecolor="black",
                markeredgewidth=CTRL_LW_MARKER_PT)
    _style_axes(ax, fig["xticks"], fig["yticks"],
                [1000, 3000, 5000], [6 * k for k in range(1, 15) if k % 5],
                8, CTRL_LW_FRAME_PT)
    tmp = path + ".grey.png"
    bases = _tick_bases(f, ax)
    f.savefig(tmp, dpi=RENDER_DPI, facecolor="white"); plt.close(f)
    prov = degrade_to_channel(tmp, path, tick_bases=bases,
                              dilate_px=CTRL_INK_DILATE_PX); os.unlink(tmp)
    return truth, prov


def grade_points_control(got, truth, fig, verbose=True):
    yspan = fig["yticks"][-1] - fig["yticks"][0]
    xspan = fig["xticks"][-1] - fig["xticks"][0]
    ex, ey, rows = [], [], []
    n_planted = n_found = 0
    n_low_planted = n_low_found = 0
    spurious = []
    for name, tps in truth.items():
        rec = got["series"][name]
        for (tx, ty) in tps:
            gated = tx >= POINTS_CTRL_GATED_RE_MIN
            if gated:
                n_planted += 1
            else:
                n_low_planted += 1
            best = min(rec, key=lambda p: math.hypot((p["x"] - tx) / xspan,
                                                     (p["y"] - ty) / yspan)) if rec else None
            if best is None or abs(best["x"] - tx) / xspan > MATCH_TOL_FRAC or \
                    abs(best["y"] - ty) / yspan > MATCH_TOL_FRAC:
                rows.append((name, tx, ty, None, None)); continue
            dx, dy = abs(best["x"] - tx), abs(best["y"] - ty)
            if gated:
                n_found += 1
                ex.append(dx); ey.append(dy)
            else:
                n_low_found += 1
            rows.append((name, tx, ty, best["x"], best["y"]))
        # SPURIOUS: a recovered marker of this series in the gated region that
        # is not a planted marker of this series.  A reader that invents a
        # marker of the graded symbol near the registered abscissa would hand
        # value_at_abscissa a wrong value with no refusal -- so this refuses.
        for p in rec:
            if p["x"] < POINTS_CTRL_GATED_RE_MIN - ABSCISSA_TOL:
                continue
            if not any(abs(p["x"] - tx) / xspan <= MATCH_TOL_FRAC and
                       abs(p["y"] - ty) / yspan <= MATCH_TOL_FRAC for (tx, ty) in tps):
                spurious.append((name, p["x"], p["y"]))
    res = dict(n_planted=n_planted, n_recovered=n_found,
               low_re_planted=n_low_planted, low_re_recovered=n_low_found,
               n_spurious_gated=len(spurious),
               spurious_gated=[dict(series=s, x=x, y=y) for s, x, y in spurious],
               x_err_max=max(ex) if ex else None,
               x_err_rms=float(np.sqrt(np.mean(np.square(ex)))) if ex else None,
               y_err_max=max(ey) if ey else None,
               y_err_rms=float(np.sqrt(np.mean(np.square(ey)))) if ey else None,
               y_err_max_frac_of_span=(max(ey) / yspan) if ey else None,
               x_err_max_frac_of_span=(max(ex) / xspan) if ex else None,
               n_rejected=len(got["rejected"]),
               calibration=got["calibration"])
    if verbose:
        print("CLOSED-FRAME POINTS CONTROL (Fig. 5.45 style, same channel)")
        print("  gated (Re >= %.0f) planted/recovered: %d/%d; low-Re pile-up "
              "(reported) %d/%d; candidates rejected: %d"
              % (POINTS_CTRL_GATED_RE_MIN, n_planted, n_found, n_low_planted,
                 n_low_found, res["n_rejected"]))
        for r in rows:
            if r[3] is None:
                print("    %-7s truth (%7.1f, %6.2f) -> NOT RECOVERED" % r[:3])
        for s, x, y in spurious:
            print("    %-7s SPURIOUS recovered marker at (%7.1f, %6.2f), no plant there"
                  % (s, x, y))
        if ey:
            print("  MEASURED: y max %.4f %s (%.4f %% of span) rms %.4f; x max %.2f "
                  "(%.4f %% of span)" % (res["y_err_max"], fig["y_units"],
                                         100 * res["y_err_max_frac_of_span"],
                                         res["y_err_rms"], res["x_err_max"],
                                         100 * res["x_err_max_frac_of_span"]))
    if n_found != n_planted:
        refuse("closed points control: %d of %d planted markers at Re >= %.0f "
               "recovered. A reader that loses planted markers cannot be trusted "
               "to keep the real ones." % (n_found, n_planted,
                                           POINTS_CTRL_GATED_RE_MIN))
    if spurious:
        refuse("closed points control: %d SPURIOUS marker(s) of a registered symbol "
               "at Re >= %.0f where nothing of that series was planted (%s). A "
               "reader that invents markers cannot be trusted near the registered "
               "abscissa." % (len(spurious), POINTS_CTRL_GATED_RE_MIN - ABSCISSA_TOL,
                              "; ".join("%s (%.0f, %.1f)" % s for s in spurious)))
    if res["y_err_max_frac_of_span"] > CLOSED_CONTROL_TOL_FRAC:
        refuse("closed points control: y error %.4f of span exceeds %.4f"
               % (res["y_err_max_frac_of_span"], CLOSED_CONTROL_TOL_FRAC))
    return res


# ---------------------------------------------------------------------------
# CONTROL 2: closed-frame PATH figure shaped like Figs 5.37 / 5.39
# ---------------------------------------------------------------------------
def _path_curve(x, base, amp, floor=None):
    """Smooth profile over ABCD with dips at B (x=1) and C (x=2), like 5.37.
    The dip bottoms out at `floor` (default base - 0.9 amp), so that, as on the
    printed page, every series stays INSIDE the frame at the corners: a curve
    plunging through the bottom frame line buried the corner ticks under ink
    and the reader lost both x majors (measured with the unfloored form)."""
    depth = amp * 0.9 if floor is None else (base - floor)
    rise = amp * (1.0 - np.exp(-6.0 * (x - np.floor(x + 1e-9))))
    dipB = depth * np.exp(-((x - 1.0) / 0.06) ** 2)
    dipC = depth * np.exp(-((x - 2.0) / 0.06) ** 2)
    hump = amp * 0.45 * np.exp(-((x - 1.72) / 0.22) ** 2)
    return base + rise - dipB - dipC + hump


PATH_CTRL_SERIES_BASE = dict(T_co_60=42.0, T_co_65=45.0, T_co_70=48.0,
                             T_co_75=51.0, T_co_80=54.0)
# the bases are chosen so that no series' FIRST symbol (half a pitch inside A)
# sits on the 50 or 60 major: a 13-px symbol drawn over a 27-px tick makes the
# tick's row group thicker than TICK_MAX_THICK_PX and the reader drops it, then
# REFUSES the axis (measured with bases 48.5 / 51.0: the 50 and 55 ticks were
# lost under the x and o first symbols).  The real Fig. 5.37 has its + series
# starting AT 50 degC and its 50 major survived (9 px of 27 read); the control
# does not rely on that luck, and the refusal it would otherwise produce is the
# reader's honest answer to an obscured anchor, not a defect.
PATH_CTRL_AMP = dict(T_co_60=6.5, T_co_65=7.5, T_co_70=8.0, T_co_75=8.5,
                     T_co_80=9.0)
# bases 3 degC apart and amplitudes rising with T_co as on the page (read from
# the crop: values at A 43 / 46.5 / 50 / 52.5 / 55, TOP-face peaks 52.5 / 58 /
# 61.5 / 65.5 / 69): the control's peaks are 51.4 / 55.9 / 59.6 / 63.3 / 67.0,
# every series inside the 40-70 frame and the registered series' hump CLEAR of
# the in-frame label band (top 14 % of the frame, > 65.8 degC).  With the first
# draft's amplitudes the registered series peaked at 66.7 INSIDE that band and
# five consecutive markers were lost to the label exclusion (measured: a 0.226
# path-unit gap, refused).
PATH_CTRL_FLOOR = dict(T_co_60=40.8, T_co_65=43.0, T_co_70=45.5,
                       T_co_75=48.0, T_co_80=50.5)
# corner minima, degC, SPREAD as on the printed Fig. 5.37 (read from the crop:
# the + series dips to ~41 at B, o ~45.5, x ~48, triangle ~50.5, square ~52.5),
# so that only ONE series reaches the corner tick's zone; five series piled on
# the floor buried the B tick under a 23-px-wide ink cluster (measured) --
# a shape the page does not have
PATH_CTRL_DX = 0.045           # planted marker pitch, path units: the real 5.37
                               # series carry ~22 markers per partition (hollow
                               # interiors 7-9 px at ~15 px pitch, MEASURED on the
                               # crop), so consecutive 13-px symbols nearly touch
                               # -- the plant is at the reader's real density


def path_control_truth(fig):
    # the first marker sits half a pitch INSIDE the frame, as on the printed
    # page (the real series' first symbols are 3-8 px inside A); a marker
    # centred ON the frame line would merge its ink with the y-axis ticks,
    # which the printed figures do not do
    xs = np.arange(PATH_CTRL_DX / 2.0, 3.0 - PATH_CTRL_DX / 4.0, PATH_CTRL_DX)
    truth = {}
    for name in fig["series"]:
        curve = _path_curve(xs, PATH_CTRL_SERIES_BASE[name], PATH_CTRL_AMP[name],
                            PATH_CTRL_FLOOR[name])
        truth[name] = [(float(x), round(float(y), 3)) for x, y in zip(xs, curve)]
    # PLANTED means: the S7.1 central-80 % path-weighted mean computed from the
    # PLANTED MARKERS by the same linear interpolant the reader uses -- the
    # thesis's markers ARE its data and that is the quantity the reader is
    # defined to deliver.  The mean of the CONTINUOUS curve is returned beside
    # it as the sampling difference, reported and never graded.
    reg = fig["registered_series"]
    txs = np.array([p[0] for p in truth[reg]]); tys = np.array([p[1] for p in truth[reg]])
    means, continuous = {}, {}
    for i, pname in enumerate(fig["partitions"]):
        lo, hi = float(i), float(i + 1)
        wlo, whi = lo + PATH_CENTRAL[0], lo + PATH_CENTRAL[1]
        g = np.linspace(wlo, whi, 4001)
        means[pname] = float(_trapz(np.interp(g, txs, tys), g) / (whi - wlo))
        continuous[pname] = float(_trapz(_path_curve(g, PATH_CTRL_SERIES_BASE[reg],
                                                      PATH_CTRL_AMP[reg],
                                                      PATH_CTRL_FLOOR[reg]), g) / (whi - wlo))
    means["_continuous_curve"] = continuous
    return truth, means


def build_path_control(path, fig):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    truth, means = path_control_truth(fig)
    f = plt.figure(figsize=(4.2, 2.2), dpi=RENDER_DPI)
    ax = f.add_axes([0.12, 0.16, 0.739, 0.645])
    size_pt = fig["symbol_px"] * 72.0 / RENDER_DPI
    for name, sym in fig["series"].items():
        xs = [p[0] for p in truth[name]]; ys = [p[1] for p in truth[name]]
        ax.plot(xs, ys, linestyle="-", linewidth=CTRL_LW_SERIES_PT, color="black",
                marker=MPL_MARKER[sym], markersize=size_pt,
                markerfacecolor="none", markeredgecolor="black",
                markeredgewidth=CTRL_LW_MARKER_PT)
    # the printed dividers sit OUTSIDE the corner ticks (measured -10.6 / +10.2
    # px of a 310-px partition on Fig. 5.37, -10.8 / +10.3 on 5.39): the control
    # reproduces that, so the reader is shown NOT to take a divider for a corner
    for p, off in ((1.0, -CTRL_DIVIDER_OFFSET), (2.0, +CTRL_DIVIDER_OFFSET)):
        ax.axvline(p + off, color="black", linewidth=CTRL_LW_FRAME_PT)
    yt = fig["yticks"]
    ymin = [yt[0] + (yt[1] - yt[0]) * (k + 0.5) for k in range(len(yt) - 1)]
    _style_axes(ax, fig["xticks"], fig["yticks"], [0.5, 1.5, 2.5], ymin, 8,
                CTRL_LW_FRAME_PT, xmaj_pt=3.6, ymaj_pt=6.5, minor_pt=2.6)
    ax.set_xticklabels(["A", "B", "C", "D"])
    for x, lab in ((0.5, "REAR"), (1.5, "TOP"), (2.5, "FRONT")):
        ax.text(x, yt[-1] - 0.06 * (yt[-1] - yt[0]), lab, ha="center", va="top",
                fontsize=8)
    tmp = path + ".grey.png"
    bases = _tick_bases(f, ax)
    f.savefig(tmp, dpi=RENDER_DPI, facecolor="white"); plt.close(f)
    prov = degrade_to_channel(tmp, path, tick_bases=bases,
                              dilate_px=CTRL_INK_DILATE_PX); os.unlink(tmp)
    return truth, means, prov


def path_control_exclusions(ink):
    """The REAR/TOP/FRONT labels the control draws: exclusion boxes derived
    from the frame (top 12 % of the frame height, centred in each panel)."""
    frame = find_frame(ink)
    fh = frame["y1"] - frame["y0"]
    xs = [frame["x0"]] + list(frame["partitions"]) + [frame["x1"]]
    boxes = []
    for i in range(len(xs) - 1):
        c = (xs[i] + xs[i + 1]) / 2.0
        boxes.append([int(c - 90), int(frame["y0"]), int(c + 90),
                      int(frame["y0"] + 0.14 * fh)])
    return boxes


def grade_path_control(got, truth, means, fig, verbose=True):
    yspan = fig["yticks"][-1] - fig["yticks"][0]
    reg = fig["registered_series"]
    tps = truth[reg]
    rec = got["series_points"]
    xt = fig["xticks"]
    def in_window(x):
        i = min(int(x), len(xt) - 2)
        lo, hi = xt[i], xt[i + 1]
        return lo + PATH_CENTRAL[0] * (hi - lo) <= x <= lo + PATH_CENTRAL[1] * (hi - lo)
    # recovery is graded INSIDE the central-80 % windows (S7.1): the markers at
    # the partition boundaries sit inside the frame/partition exclusion margin by
    # construction and the dips at B and C lie outside every window
    # a recovered marker pairs with a planted one only within 40 % of the planted
    # pitch along the path (the 2 %-of-span rule would reach 0.06, MORE than one
    # pitch, and paired a marker with its neighbour: measured x max 0.0463)
    xtol = min(MATCH_TOL_FRAC * 3.0, 0.4 * PATH_CTRL_DX)
    ey, ex, lost, n_win = [], [], 0, 0
    for (tx, ty) in tps:
        if not in_window(tx):
            continue
        n_win += 1
        best = min(rec, key=lambda p: math.hypot((p["x"] - tx) / 3.0,
                                                 (p["y"] - ty) / yspan)) if rec else None
        if best is None or abs(best["x"] - tx) > xtol or \
                abs(best["y"] - ty) / yspan > MATCH_TOL_FRAC:
            lost += 1; continue
        ex.append(abs(best["x"] - tx)); ey.append(abs(best["y"] - ty))
    # SPURIOUS: a recovered marker of the registered symbol inside a window that
    # is not a planted marker of the registered series -- it would enter the
    # partition mean with no refusal, so this refuses
    spurious = [p for p in rec if in_window(p["x"]) and not any(
        abs(p["x"] - tx) <= xtol and abs(p["y"] - ty) / yspan <= MATCH_TOL_FRAC
        for (tx, ty) in tps)]
    # the reader's partition means, per L-340 sized to the averaging reader
    pm = {}
    for pname, part in got["partitions"].items():
        m, n = partition_mean(part["points"], part["lo"], part["hi"],
                              "control partition %s" % pname)
        pm[pname] = dict(recovered=m, planted=means[pname],
                         planted_continuous_curve=means["_continuous_curve"][pname],
                         err=abs(m - means[pname]), n_in_window=n)
    res = dict(n_planted_in_window=n_win, n_recovered_in_window=n_win - lost,
               n_planted_total=len(tps), n_spurious_in_window=len(spurious),
               spurious_in_window=[dict(x=p["x"], y=p["y"]) for p in spurious],
               y_err_max=max(ey) if ey else None,
               y_err_rms=float(np.sqrt(np.mean(np.square(ey)))) if ey else None,
               y_err_max_frac_of_span=(max(ey) / yspan) if ey else None,
               x_err_max=max(ex) if ex else None,
               partition_means=pm,
               mean_err_max=max(v["err"] for v in pm.values()),
               mean_err_max_frac_of_span=max(v["err"] for v in pm.values()) / yspan,
               n_rejected=got["rejected_n"], calibration=got["calibration"])
    if verbose:
        print("CLOSED-FRAME PATH CONTROL (Figs 5.37/5.39 style, same channel)")
        print("  registered series %s: planted in the central windows %d, recovered %d, "
              "spurious %d; %d planted in all; candidates rejected %d"
              % (reg, n_win, n_win - lost, len(spurious), len(tps), res["n_rejected"]))
        if ey:
            print("  per-marker: y max %.4f %s (%.4f %% of span) rms %.4f; x max %.4f path"
                  % (res["y_err_max"], fig["y_units"],
                     100 * res["y_err_max_frac_of_span"], res["y_err_rms"],
                     res["x_err_max"]))
        for pname, v in pm.items():
            print("  partition %s: planted mean %.4f recovered %.4f err %.4f (%d markers in "
                  "window; continuous-curve mean %.4f, reported)"
                  % (pname, v["planted"], v["recovered"], v["err"], v["n_in_window"],
                     v["planted_continuous_curve"]))
    if n_win == 0 or (n_win - lost) / float(n_win) < PATH_MIN_RECOVERY:
        refuse("closed path control: %d of %d planted in-window markers of the "
               "registered series recovered (< %.0f %%)"
               % (n_win - lost, n_win, 100 * PATH_MIN_RECOVERY))
    if spurious:
        refuse("closed path control: %d SPURIOUS marker(s) of the registered symbol "
               "inside the central windows where none was planted (%s)"
               % (len(spurious), "; ".join("(%.3f, %.2f)" % (p["x"], p["y"])
                                            for p in spurious)))
    if res["y_err_max_frac_of_span"] > CLOSED_CONTROL_TOL_FRAC:
        refuse("closed path control: per-marker y error %.4f of span exceeds %.4f"
               % (res["y_err_max_frac_of_span"], CLOSED_CONTROL_TOL_FRAC))
    if res["mean_err_max_frac_of_span"] > CLOSED_CONTROL_TOL_FRAC:
        refuse("closed path control: partition-mean error %.4f of span exceeds %.4f"
               % (res["mean_err_max_frac_of_span"], CLOSED_CONTROL_TOL_FRAC))
    return res


# ---------------------------------------------------------------------------
# THE RANK READER -- a second reader, for a path figure whose SYMBOL series
# cannot be separated symbol-by-symbol
# ---------------------------------------------------------------------------
# MEASURED, and it is why this reader exists.  On the real Fig. 5.37 crop the
# template reader of the section above finds 66 circles (the true count) but
# ONE square and THREE triangles of 66: the printed squares of consecutive
# points TOUCH (side 10 px at a 11-12 px pitch, read off the deskewed raster),
# their top and bottom edges merge into one run, and a ring template over a
# merged glyph reads a recall of 0.68 where 0.82 is required.  The + and x
# templates, whose rings are thin arms, then over-fire on the dense ink (385
# and 360 candidates for 66 true markers) and explain_away() removes the real
# triangles as "claimed" by those spurious neighbours.  A reader that returns
# 3 of 66 markers of the registered series is not a reader, and no amount of
# threshold-turning against the real page would be a measurement -- it would be
# a reader fitted to the answer.
#
# WHAT THIS READER USES INSTEAD, and it is a property of the PAGE, registered
# before any value is taken: Fig. 5.37 plots the SAME path for five internal
# copper temperatures T_co = 60, 65, 70, 75, 80 degC, and the surface
# temperature rises monotonically with T_co, so the five line-connected curves
# NEVER CROSS.  The thesis says so in its own words (printed p. 148: "the
# temperature profiles are more or less congruent") and the page shows it.
# The reader therefore does not identify symbols at all.  It scans the frame
# COLUMN BY COLUMN, merges ink groups closer than one symbol height into one
# curve, and REQUIRES EXACTLY n_series groups; a column that resolves into any
# other number is UNUSABLE and is dropped, never repaired.  The registered
# series is taken by its RANK from the top of the frame, which the legend
# fixes (T_co = 80 uppermost, T_co = 75 second).
#
# MEASURED on the real crops (deskewed, in-frame columns, merge gap 12 px):
#   Fig. 5.37  560 of 905 columns resolve into exactly 5 curves  (0.619)
#   Fig. 5.39    0 of 907 columns resolve into exactly 5 curves  (0.000)
# Fig. 5.39's five Reynolds-number series OVERLAP and CROSS -- S7.3 of the
# pre-registration says so in advance ("five overlapping Reynolds-number symbol
# series") -- so no rank is registered for it and this reader REFUSES on it.
# THAT REFUSAL IS THE HONEST ANSWER FOR 5.39, not a defect to be tuned away.
RANK_MERGE_GAP_PX = 12         # ink groups closer than this are ONE curve: the
                               # tallest registered symbol is 11 px, so a hollow
                               # marker's top and bottom edges never break by
                               # more than that
RANK_MIN_USABLE_FRAC = 0.50    # fewer usable columns than this -> REFUSE
RANK_MIN_WINDOW_COLS = 40      # usable columns required inside a central window
RANK_MAX_JUMP_PX = 25.0        # a curve may not move more than this between two
                               # ADJACENT usable columns
RANK_MAX_WINDOW_GAP = 0.05     # path units: a gap this large in the usable
                               # columns inside a central window -> REFUSE
RANK_ANCHOR_TOL_PX = 3.0       # a tracked curve must still BE the rank-k
                               # curve at every column where all n_series
                               # curves resolve
RANK_EDGE_PX = 4               # frame and divider lines are excluded this far


def rank_columns(ink, frame, n_series):
    """Per-column merged ink groups over the whole frame.

    Returns (columns, n_in_frame, n_resolved): `columns` is an ordered list of
    (column px, [group centre px, TOP FIRST]) for every in-frame column carrying
    ink, and `n_resolved` counts those carrying exactly n_series groups.  Nothing
    is blanked and nothing is repaired: n_resolved / n_in_frame is the evidence
    that the figure's series separate at all, and the tracker below decides which
    group is the registered curve."""
    x0 = int(math.ceil(frame["x0"])) + RANK_EDGE_PX
    x1 = int(math.floor(frame["x1"])) - RANK_EDGE_PX
    y0 = int(math.ceil(frame["y0"])) + RANK_EDGE_PX
    y1 = int(math.floor(frame["y1"])) - RANK_EDGE_PX
    parts = [float(p) for p in frame["partitions"]]
    cols, n_cols, n_res = [], 0, 0
    for c in range(x0, x1 + 1):
        if any(abs(c - p) <= RANK_EDGE_PX for p in parts):
            continue
        n_cols += 1
        idx = np.where(ink[y0:y1, c])[0]
        if len(idx) == 0:
            continue
        brk = np.where(np.diff(idx) > RANK_MERGE_GAP_PX)[0]
        groups = np.split(idx, brk + 1)
        if len(groups) == n_series:
            n_res += 1
        cols.append((float(c), [float(y0) + float(g.mean()) for g in groups]))
    return cols, n_cols, n_res


def track_curve(cols, k, n_series, lo_px, hi_px, name):
    """Follow ONE curve across a window, anchored on the columns where all
    n_series curves resolve, refusing the moment the track contradicts one.

    Why a tracker and not the rank alone: on the printed page AND on the control
    the in-frame REAR / TOP / FRONT labels sit in the top eighth of the frame and
    the hottest series runs THROUGH them, so a band of columns carries
    n_series + 1 groups and a pure rank reader drops them (measured: a 0.174
    path-unit hole in the control's TOP window).  Blanking the label boxes is
    worse -- it deletes the curve that runs through them.  The tracker steps
    column by column, takes the group NEAREST the previous centre, and stops
    stepping when the nearest group is further than RANK_MAX_JUMP_PX.

    THE SELF-CHECK IS THE POINT: at every column that DOES resolve into exactly
    n_series groups, the tracked centre must still be that column's rank-k
    centre, within RANK_ANCHOR_TOL_PX.  A track that has slid onto a neighbouring
    series is caught the moment the series separate again, and a swapped curve is
    another series' value under this row's name."""
    by = dict(cols)
    xs = sorted(c for c in by if lo_px - 1.0 <= c <= hi_px + 1.0)
    if not xs:
        refuse("%s: no in-frame column inside the window" % name)
    seeds = [c for c in xs if len(by[c]) == n_series]
    if not seeds:
        refuse("%s: no column inside the window resolves into exactly %d curves, "
               "so the tracked curve cannot be anchored to a rank"
               % (name, n_series))
    mid = 0.5 * (lo_px + hi_px)
    seed = min(seeds, key=lambda c: abs(c - mid))
    out = {seed: by[seed][k]}
    i0 = xs.index(seed)
    for direction in (1, -1):
        prev = by[seed][k]
        j = i0 + direction
        while 0 <= j < len(xs):
            c = xs[j]
            cent = by[c]
            best = min(cent, key=lambda v: abs(v - prev))
            if abs(best - prev) <= RANK_MAX_JUMP_PX:
                if len(cent) == n_series and abs(best - cent[k]) > RANK_ANCHOR_TOL_PX:
                    refuse("%s: at column %.0f all %d curves resolve and the "
                           "tracked curve sits %.1f px from the rank-%d curve "
                           "(limit %.1f). The track has moved onto another "
                           "series, and a swapped curve is another series' value "
                           "under this row's name."
                           % (name, c, n_series, abs(best - cent[k]), k + 1,
                              RANK_ANCHOR_TOL_PX))
                out[c] = best
                prev = best
            j += direction
    return sorted(out.items())


def read_path_figure_rank(ink, fig, verbose=False):
    """The registered series' curve, by rank, from a closed-frame path figure."""
    frame = find_frame(ink)
    cal = calibrate_closed(ink, frame, fig["xticks"], fig["yticks"], "path",
                           fig.get("x_majors_may_be_absent", 0))
    n = fig["n_series"]
    cols, n_cols, n_res = rank_columns(ink, frame, n)
    frac = n_res / float(max(n_cols, 1))
    if frac < RANK_MIN_USABLE_FRAC:
        refuse("rank reader on %s: only %d of %d in-frame columns resolve into "
               "exactly %d curves (%.3f < %.2f). The series do not separate on "
               "this figure, so no ranked value can be read from it."
               % (fig.get("crop", "?"), n_res, n_cols, n, frac,
                  RANK_MIN_USABLE_FRAC))
    if fig.get("rank_from_top") is None:
        refuse("rank reader on %s: no rank is registered for the graded series "
               "on this figure (its series cross), so a rank cannot name it"
               % fig.get("crop", "?"))
    k = int(fig["rank_from_top"]) - 1
    xt = fig["xticks"]
    parts, allpts = {}, []
    for i, (pname, face) in enumerate(fig["partitions"].items()):
        lo, hi = xt[i], xt[i + 1]
        span = hi - lo
        # THE TRACK IS BOUNDED TO S7.1's CENTRAL 80 % EXACTLY, with no margin.
        # Measured: with a 0.05-unit margin the track ran into the corner dip at
        # B, where the five curves plunge and merge, and slid onto a neighbouring
        # series -- the anchor check caught it (22.4 px from the rank-2 curve at
        # column 394 of the real Fig. 5.37 crop, rc 2).  Bounded to the window
        # the row actually uses, the track disagrees with the resolved rank at
        # ZERO of 146 / 182 / 134 resolved columns in AB / BC / CD.  The window
        # is not moved to make the reader work: it is S7.1's registered window,
        # and the margin that was removed was never part of it.
        wlo = lo + PATH_CENTRAL[0] * span
        whi = lo + PATH_CENTRAL[1] * span
        lo_px = (wlo - cal["x"][1]) / cal["x"][0]
        hi_px = (whi - cal["x"][1]) / cal["x"][0]
        if lo_px > hi_px:
            lo_px, hi_px = hi_px, lo_px
        tracked = track_curve(cols, k, n, lo_px, hi_px,
                              "%s partition %s" % (fig.get("crop", "?"), pname))
        pts = []
        for c, py in tracked:
            x, y = to_data(cal, c, py)
            pts.append(dict(x=x, y=y, px=c, py=py))
        pts.sort(key=lambda p: p["x"])
        parts[pname] = dict(face=face, lo=lo, hi=hi, n_cols=len(pts), points=pts)
        allpts.extend(pts)
    allpts.sort(key=lambda p: p["x"])
    return dict(frame=dict(x0=frame["x0"], x1=frame["x1"], y0=frame["y0"],
                           y1=frame["y1"], partitions=frame["partitions"]),
                calibration=cal, series_points=allpts, partitions=parts,
                columns_usable=n_res, columns_in_frame=n_cols,
                columns_usable_frac=frac,
                symbol_radius_data=abs(cal["y"][0]) * fig["symbol_px"] / 2.0)


def rank_partition_mean(pts, lo, hi, name):
    """S7.1's central-80 % path-weighted mean of the ranked curve."""
    xs = np.array([p["x"] for p in pts])
    ys = np.array([p["y"] for p in pts])
    span = hi - lo
    wlo, whi = lo + PATH_CENTRAL[0] * span, lo + PATH_CENTRAL[1] * span
    sel = (xs >= wlo - RANK_MAX_WINDOW_GAP) & (xs <= whi + RANK_MAX_WINDOW_GAP)
    sx, sy = xs[sel], ys[sel]
    if len(sx) < RANK_MIN_WINDOW_COLS:
        refuse("%s: %d usable columns inside the central window, %d required"
               % (name, len(sx), RANK_MIN_WINDOW_COLS))
    if sx[0] > wlo + RANK_MAX_WINDOW_GAP or sx[-1] < whi - RANK_MAX_WINDOW_GAP:
        refuse("%s: usable columns cover [%.3f, %.3f] but the central window is "
               "[%.3f, %.3f]" % (name, sx[0], sx[-1], wlo, whi))
    g = np.diff(sx)
    if len(g) and g.max() > RANK_MAX_WINDOW_GAP:
        refuse("%s: a gap of %.3f path units in the usable columns inside the "
               "central window exceeds %.3f" % (name, g.max(), RANK_MAX_WINDOW_GAP))
    sp = np.array([p["py"] for p in pts])[sel]
    sc = np.array([p["px"] for p in pts])[sel]
    for i in range(1, len(sp)):
        if sc[i] - sc[i - 1] <= 2.0 and abs(sp[i] - sp[i - 1]) > RANK_MAX_JUMP_PX:
            refuse("%s: the ranked curve jumps %.1f px between adjacent columns "
                   "%.0f and %.0f INSIDE the central window (limit %.1f). A jump "
                   "that large is a curve swap, and a swapped curve is another "
                   "series' value under this row's name."
                   % (name, abs(sp[i] - sp[i - 1]), sc[i - 1], sc[i],
                      RANK_MAX_JUMP_PX))
    grid = np.linspace(wlo, whi, 401)
    return float(_trapz(np.interp(grid, sx, sy), grid) / (whi - wlo)), int(len(sx))


def grade_rank_control(workdir, fig_id="5.37", verbose=True, rank_override=None,
                       truth_shift=0.0, label=None):
    """THE PLANTED CONTROL FOR THE RANK READER, and the plant is SIZED TO THE
    READER (L-340).

    The graded quantity this reader delivers is a MEAN over the central 80 % of
    a partition -- an AVERAGING reader.  A single-point plant would be diluted
    by ~1/sqrt(N) and the control would refuse a working reader, which is
    L-340's measured failure.  So the plant is THE WHOLE CURVE: five
    line-connected series of known values are rendered through the measured
    channel, and the recovered curve is compared to the planted one BOTH
    per-column (a point read) AND as the partition mean (the averaged read the
    row actually uses).  A shift of the planted curve moves the recovered mean
    one-for-one, so the control is reachable by the reader it guards."""
    fig = dict(FIGURES[fig_id])
    path = os.path.join(workdir, "closed_rank_control.tif")
    truth, means, prov = build_path_control(path, fig)
    ink, skew, resid = deskew(load_ink(path))
    fig["exclude_px"] = path_control_exclusions(ink)
    if rank_override is not None:
        fig["rank_from_top"] = rank_override
    got = read_path_figure_rank(ink, fig)
    reg = fig["registered_series"]
    txs = np.array([p[0] for p in truth[reg]])
    tys = np.array([p[1] for p in truth[reg]]) + truth_shift
    yspan = fig["yticks"][-1] - fig["yticks"][0]
    errs, pmeans = [], {}
    for p in got["series_points"]:
        if txs[0] <= p["x"] <= txs[-1]:
            errs.append(p["y"] - float(np.interp(p["x"], txs, tys)))
    errs = np.array(errs)
    if len(errs) == 0:
        refuse("rank control: no recovered column fell inside the planted span")
    ymax, yrms = float(np.abs(errs).max()), float(np.sqrt((errs ** 2).mean()))
    mean_err_max = 0.0
    for pname, part in got["partitions"].items():
        m, ncol = rank_partition_mean(part["points"], part["lo"], part["hi"],
                                      "rank control %s" % pname)
        planted = means[pname] + truth_shift
        pmeans[pname] = dict(planted=planted, recovered=m, err=m - planted,
                             n_cols=ncol,
                             continuous_curve=means["_continuous_curve"][pname])
        mean_err_max = max(mean_err_max, abs(m - planted))
    if verbose:
        print("CLOSED-FRAME RANK CONTROL (Fig. %s style, same channel)%s"
              % (fig_id, "" if label is None else " -- " + label))
        print("  columns: %d of %d in frame resolve into exactly %d curves (%.3f)"
              % (got["columns_usable"], got["columns_in_frame"], fig["n_series"],
                 got["columns_usable_frac"]))
        print("  per-column vs the planted curve: y max %.4f %s (%.4f %% of span) "
              "rms %.4f" % (ymax, fig["y_units"], 100 * ymax / yspan, yrms))
        for pname in ("AB", "BC", "CD"):
            d = pmeans[pname]
            print("  partition %s: planted mean %.4f recovered %.4f err %.4f "
                  "(%d usable columns; continuous-curve mean %.4f, reported)"
                  % (pname, d["planted"], d["recovered"], d["err"], d["n_cols"],
                     d["continuous_curve"]))
    # THE GATED QUANTITY IS THE PARTITION MEAN, because that is the quantity the
    # row takes; the per-column error is REPORTED beside it and never gated.
    # Measured reason, and it is a property of a column read, not a defect: a
    # column cuts the polyline vertically, so where the curve is steep the ink in
    # one column spans a large range and its centre is the midpoint of that span.
    # On the control, over the 250 columns of each of S7.1's central-80 % windows,
    # the per-column error is 0.5920 degC at its worst and 0.1671 rms (1.97 % and
    # 0.56 % of the 30-degC span), and the worst columns sit at the window edges
    # where the curve steepens into a corner.  The partition MEAN over those 250
    # columns is 0.0962 / 0.0983 / 0.1122 degC (0.32-0.37 % of span).  The
    # per-column MAX is nevertheless carried INTO the digitisation increment,
    # which makes the increment larger, never smaller.
    if mean_err_max / yspan > CLOSED_CONTROL_TOL_FRAC:
        refuse("closed rank control: partition-mean error %.4f of span exceeds "
               "%.4f" % (mean_err_max / yspan, CLOSED_CONTROL_TOL_FRAC))
    return dict(figure=fig_id, n_columns_usable=got["columns_usable"],
                n_columns_in_frame=got["columns_in_frame"],
                columns_usable_frac=got["columns_usable_frac"],
                n_planted_markers=len(truth[reg]),
                y_err_max=ymax, y_err_rms=yrms,
                y_err_max_frac_of_span=ymax / yspan,
                partition_means=pmeans, mean_err_max=mean_err_max,
                mean_err_max_frac_of_span=mean_err_max / yspan,
                provenance=prov, skew_measured_deg=skew,
                skew_residual_deg=resid)


def run_closed_controls(workdir, verbose=True):
    fig_p = dict(FIGURES["5.45"])
    path_p = os.path.join(workdir, "closed_points_control.tif")
    truth_p, prov_p = build_points_control(path_p, fig_p)
    ink, skew, resid = deskew(load_ink(path_p))
    got = read_points_figure(ink, fig_p)
    res_p = grade_points_control(got, truth_p, fig_p, verbose)
    res_p["provenance"] = prov_p
    res_p["skew_measured_deg"] = skew; res_p["skew_residual_deg"] = resid
    fig_q = dict(FIGURES["5.37"])
    path_q = os.path.join(workdir, "closed_path_control.tif")
    truth_q, means_q, prov_q = build_path_control(path_q, fig_q)
    ink, skew, resid = deskew(load_ink(path_q))
    fig_q["exclude_px"] = path_control_exclusions(ink)
    got = read_path_figure(ink, fig_q)
    res_q = grade_path_control(got, truth_q, means_q, fig_q, verbose)
    res_q["provenance"] = prov_q
    res_q["skew_measured_deg"] = skew; res_q["skew_residual_deg"] = resid
    res_r = grade_rank_control(workdir, "5.37", verbose)
    return dict(points=res_p, path=res_q, rank=res_r)


# ---------------------------------------------------------------------------
# Reading the real figures, with blind repeats
# ---------------------------------------------------------------------------
def read_figure_full(fig_id, crop_dir, verbose=True):
    fig = FIGURES[fig_id]
    path = os.path.join(crop_dir, fig["crop"])
    ink0 = load_ink(path)
    ink, skew, resid = deskew(ink0)
    if fig["kind"] == "points":
        reader = read_points_figure
    elif fig.get("reader") == "rank":
        reader = read_path_figure_rank
    else:
        reader = read_path_figure
    got = reader(ink, fig)
    out = dict(figure=fig_id, crop=fig["crop"], crop_box=fig["crop_box"],
               page_printed=fig["page_printed"], page_pdf=fig["page_pdf"],
               skew_measured_deg=skew, skew_residual_deg=resid,
               calibration=got["calibration"], frame=got["frame"],
               symbol_px=fig["symbol_px"],
               symbol_radius_data=got["symbol_radius_data"])
    if fig["kind"] == "points":
        # ONE MARKER PER SERIES PER ABSCISSA: the page plots one value per face
        # per Reynolds number.  Two markers of one symbol within +-ABSCISSA_TOL
        # of each other are a merged blob read twice or a pile-up read as the
        # wrong symbol (measured on the real figure: a spurious FRONT circle at
        # Re 3206 / 49.9 W/m2K where + x and triangle overlap, recall 0.83).
        # At the REGISTERED abscissa that is a refusal for a graded series;
        # elsewhere it is recorded as a duplicate, never used, never silent.
        dups = {}
        for name, pts in got["series"].items():
            xs = sorted(p["x"] for p in pts)
            dd = [(a, b) for a, b in zip(xs, xs[1:]) if b - a <= ABSCISSA_TOL]
            if dd:
                dups[name] = [dict(x1=a, x2=b) for a, b in dd]
            near = [p for p in pts if abs(p["x"] - fig["at"]) <= ABSCISSA_TOL]
            if name in fig["graded"] and len(near) > 1:
                refuse("%s %s: %d markers of the registered symbol within +-%.0f "
                       "of the registered abscissa %.0f (%s); the value there is "
                       "ambiguous" % (fig_id, name, len(near), ABSCISSA_TOL,
                                      fig["at"], [(round(p["x"]), round(p["y"], 2))
                                                  for p in near]))
        out["duplicate_abscissae"] = dups
        vals = {}
        for name in fig["series"]:
            v = value_at_abscissa(got["series"][name], fig["at"], "5.45 %s" % name) \
                if name in fig["graded"] else None
            if v is None:
                pts = got["series"][name]
                near = [p for p in pts if abs(p["x"] - fig["at"]) <= ABSCISSA_TOL]
                v = min(near, key=lambda p: abs(p["x"] - fig["at"])) if near else None
            vals[name] = None if v is None else dict(x=v["x"], y=v["y"],
                                                     recall=v["recall"])
        out["values_at_abscissa"] = vals
        out["series_counts"] = {n: len(p) for n, p in got["series"].items()}
        out["rejected_candidates_n"] = len(got["rejected"])
        # blind repeats: the three graded values + two other markers
        reps = {n: [] for n in fig["graded"]}
        for ink_r in perturbed_copies(ink, REPEAT_N, REPEAT_SEED):
            g = read_points_figure(ink_r, fig)
            for n in fig["graded"]:
                pts = g["series"][n]
                near = [p for p in pts if abs(p["x"] - fig["at"]) <= ABSCISSA_TOL]
                reps[n].append(min(near, key=lambda p: abs(p["x"] - fig["at"]))["y"]
                               if near else None)
        out["blind_repeats"] = reps
    elif fig.get("reader") == "rank":
        means = {}
        for pname, part in got["partitions"].items():
            m, n = rank_partition_mean(part["points"], part["lo"], part["hi"],
                                       "%s partition %s" % (fig_id, pname))
            means[pname] = dict(face=part["face"], mean_central80=m,
                                n_cols=part["n_cols"], n_in_window=n)
        out["partition_means"] = means
        out["reader"] = "rank"
        out["rank_from_top"] = fig["rank_from_top"]
        out["n_series"] = fig["n_series"]
        out["columns_usable"] = got["columns_usable"]
        out["columns_in_frame"] = got["columns_in_frame"]
        out["columns_usable_frac"] = got["columns_usable_frac"]
        out["series_points"] = [dict(x=round(p["x"], 4), y=round(p["y"], 4))
                                for p in got["series_points"]]
        reps = {p: [] for p in fig["partitions"]}
        for ink_r in perturbed_copies(ink, REPEAT_N, REPEAT_SEED):
            try:
                g = read_path_figure_rank(ink_r, fig)
            except SystemExit:
                for pname in fig["partitions"]:
                    reps[pname].append(None)
                continue
            for pname, part in g["partitions"].items():
                try:
                    m, _n = rank_partition_mean(part["points"], part["lo"],
                                                part["hi"], pname)
                except SystemExit:
                    m = None
                reps[pname].append(m)
        out["blind_repeats"] = reps
    else:
        means = {}
        for pname, part in got["partitions"].items():
            m, n = partition_mean(part["points"], part["lo"], part["hi"],
                                  "%s partition %s" % (fig_id, pname))
            means[pname] = dict(face=part["face"], mean_central80=m,
                                n_markers=part["n_markers"], n_in_window=n)
        out["partition_means"] = means
        out["series_n_markers"] = len(got["series_points"])
        out["series_points"] = [dict(x=round(p["x"], 4), y=round(p["y"], 4))
                                for p in got["series_points"]]
        out["other_symbol_counts"] = got["other_symbols"]
        out["rejected_candidates_n"] = got["rejected_n"]
        reps = {p: [] for p in fig["partitions"]}
        for ink_r in perturbed_copies(ink, REPEAT_N, REPEAT_SEED):
            g = read_path_figure(ink_r, fig)
            for pname, part in g["partitions"].items():
                try:
                    m, _n = partition_mean(part["points"], part["lo"], part["hi"], pname)
                except SystemExit:
                    m = None
                reps[pname].append(m)
        out["blind_repeats"] = reps
    if verbose:
        print("FIGURE %s (%s, printed p. %d = PDF %d): skew %.4f deg (residual %.4f), "
              "x scale %.5g/px, y scale %.5g/px, fit resid x %.2f y %.2f px, "
              "symbol radius %.3f %s"
              % (fig_id, fig["crop"], fig["page_printed"], fig["page_pdf"], skew,
                 resid, got["calibration"]["x"][0], got["calibration"]["y"][0],
                 got["calibration"]["max_resid_px"]["x"],
                 got["calibration"]["max_resid_px"]["y"],
                 got["symbol_radius_data"], fig["y_units"]))
    return out


def _spread(vals):
    v = [x for x in vals if x is not None]
    return (max(v) - min(v)) if len(v) >= 2 else None


# ---------------------------------------------------------------------------
# Selftest -- every refusal driven, one of them under `-O` by subprocess
# ---------------------------------------------------------------------------
def selftest_a7():
    failures = []
    tmp = tempfile.mkdtemp(prefix="t5_digitiser_a7_")
    me = os.path.abspath(__file__)

    # (A) the frozen arms, unchanged
    rc = selftest()
    if rc != 0:
        failures.append("frozen selftest arms FAILED")

    # (B) the two closed-frame planted controls MUST pass
    try:
        res = run_closed_controls(tmp)
        print("CLOSED CONTROLS PASS: points y max %.4f %% of span; path per-marker "
              "y max %.4f %% of span, partition-mean max %.4f %% of span."
              % (100 * res["points"]["y_err_max_frac_of_span"],
                 100 * res["path"]["y_err_max_frac_of_span"],
                 100 * res["path"]["mean_err_max_frac_of_span"]))
        print("RANK CONTROL PASS: partition-mean max %.4f %% of span (GATED); "
              "per-column max %.4f %% of span (reported)."
              % (100 * res["rank"]["mean_err_max_frac_of_span"],
                 100 * res["rank"]["y_err_max_frac_of_span"]))
    except SystemExit:
        failures.append("CLOSED CONTROL FAILED -- the reader could not recover "
                        "planted values from a closed-frame raster")
        res = None

    pts_tif = os.path.join(tmp, "closed_points_control.tif")
    path_tif = os.path.join(tmp, "closed_path_control.tif")

    def expect_refusal(label, fn):
        try:
            fn()
        except SystemExit as e:
            if e.code == 2:
                print("REFUSAL DRIVEN: %s -> rc 2" % label); return
            failures.append("%s: exited %r, not 2" % (label, e.code)); return
        failures.append("%s: did NOT refuse" % label)

    if os.path.isfile(pts_tif):
        ink, _s, _r = deskew(load_ink(pts_tif))
        fig = dict(FIGURES["5.45"])
        # (C) mis-anchored: 3 y anchors registered against a 4-anchor axis
        bad = dict(fig); bad["yticks"] = [0.0, 45.0, 90.0]
        expect_refusal("mis-anchored y set (3 vs 4)",
                       lambda: read_points_figure(ink, bad))
        # (D) abscissa refusal: no marker within +-100 of 5600
        got = read_points_figure(ink, fig)
        expect_refusal("abscissa not within +-100 of registered",
                       lambda: value_at_abscissa(got["series"]["front"], 5600.0, "x"))
        # (E) partition mismatch: a points figure read as a 2-partition path
        badp = dict(FIGURES["5.37"]); badp["symbol_px"] = fig["symbol_px"]
        expect_refusal("partition count mismatch (points figure read as path)",
                       lambda: read_path_figure(ink, badp))
        # (F) blank raster: no frame
        blank = np.zeros_like(ink)
        expect_refusal("blank raster has no frame", lambda: find_frame(blank))
        # (G) ambiguous major/minor split
        expect_refusal("ambiguous major/minor tick split",
                       lambda: select_major_ticks([(10, 20), (30, 20), (50, 20),
                                                   (70, 20)], 2, "y"))
        # (H) control tolerance: a truth table shifted by 5 % of span must refuse
        shifted = {k: [(x, y + 4.5) for (x, y) in v]
                   for k, v in points_control_truth().items()}
        expect_refusal("closed points control tolerance (truth shifted 5 %)",
                       lambda: grade_points_control(got, shifted, fig, verbose=False))
        # (M) spurious marker: a front marker invented at Re 4440 where no
        # circle was planted must refuse (it is what value_at_abscissa reads)
        forged = dict(got); forged["series"] = dict(got["series"])
        forged["series"]["front"] = list(got["series"]["front"]) + \
            [dict(x=4440.0, y=40.0, px=0.0, py=0.0, recall=1.0)]
        expect_refusal("closed points control: spurious front marker at 4440",
                       lambda: grade_points_control(forged, points_control_truth(),
                                                    fig, verbose=False))
        # (I) the arm that bites: subprocess under BOTH interpreters, rc 2
        rcs = {}
        for tag, argv in (("python3", [sys.executable, me]),
                          ("python3 -O", [sys.executable, "-O", me])):
            q = subprocess.run(argv + ["--closed-figure", pts_tif, "--kind", "points",
                                       "--xticks", "0,2000,4000,6000",
                                       "--yticks", "0,45,90"],
                               capture_output=True, text=True)
            rcs[tag] = (q.returncode, "REFUSED" in q.stderr)
        if rcs["python3"] == (2, True) and rcs["python3 -O"] == (2, True):
            print("REFUSAL FIRES UNDER `-O`: mis-anchored closed frame rc 2 under BOTH.")
        else:
            failures.append("closed-frame refusal did not fire identically: %r" % (rcs,))
    if os.path.isfile(path_tif):
        ink, _s, _r = deskew(load_ink(path_tif))
        figq = dict(FIGURES["5.37"]); figq["exclude_px"] = path_control_exclusions(ink)
        got = read_path_figure(ink, figq)
        # (J) sparse partition: too few markers
        expect_refusal("partition with too few markers",
                       lambda: partition_mean(got["partitions"]["AB"]["points"][:3],
                                              0.0, 1.0, "AB"))
        # (K) coverage gap inside the central window
        sub = [p for p in got["partitions"]["BC"]["points"]
               if not (1.35 <= p["x"] <= 1.65)]
        expect_refusal("gap inside the central window",
                       lambda: partition_mean(sub, 1.0, 2.0, "BC"))
        # (L) path-control tolerance on the partition means
        truth_q, means_q = path_control_truth(figq)
        bad_means = {k: (v if isinstance(v, dict) else v + 1.5) for k, v in means_q.items()}
        expect_refusal("closed path control tolerance (means shifted 5 %)",
                       lambda: grade_path_control(got, truth_q, bad_means, figq,
                                                  verbose=False))
        # (N) spurious in-window marker of the registered symbol must refuse
        forged = dict(got)
        forged["series_points"] = list(got["series_points"]) + \
            [dict(x=1.5, y=45.0, px=0.0, py=0.0, recall=1.0)]
        expect_refusal("closed path control: spurious in-window marker",
                       lambda: grade_path_control(forged, truth_q, means_q, figq,
                                                  verbose=False))

    # (M) THE RANK READER's OWN REFUSALS, all four driven
    #  M1  the plant moved by 5 % of span must break the mean tolerance -- the
    #      control is REACHABLE, which is what makes a pass mean anything
    expect_refusal("rank control tolerance (planted curve shifted 5 % of span)",
                   lambda: grade_rank_control(tmp, "5.37", verbose=False,
                                              truth_shift=0.05 * 30.0))
    #  M2  THE MUTATION CONTROL: track rank 1 (T_co = 80) and grade it against
    #      the rank-2 (T_co = 75) plant.  A reader that returned something
    #      rank-independent -- a mean of all five, say -- would pass this, and
    #      it must not.
    expect_refusal("rank control reads the WRONG rank (1 instead of 2)",
                   lambda: grade_rank_control(tmp, "5.37", verbose=False,
                                              rank_override=1))
    if os.path.isfile(pts_tif):
        ink_p, _s, _r = deskew(load_ink(pts_tif))
        #  M3  a raster with no five-curve structure: the separation refusal
        expect_refusal("rank reader on a figure whose series do not separate",
                       lambda: read_path_figure_rank(ink_p, dict(FIGURES["5.37"])))
    if os.path.isfile(path_tif):
        ink_q, _s, _r = deskew(load_ink(path_tif))
        norank = dict(FIGURES["5.37"]); norank["rank_from_top"] = None
        norank["exclude_px"] = path_control_exclusions(ink_q)
        #  M4  no registered rank (the Fig. 5.39 case) -> refuse
        expect_refusal("rank reader with no registered rank (the 5.39 case)",
                       lambda: read_path_figure_rank(ink_q, norank))

    for root, _d, files in os.walk(tmp, topdown=False):
        for f in files:
            os.unlink(os.path.join(root, f))
        os.rmdir(root)
    if failures:
        for f in failures:
            print("FAILED: " + f)
        return 1
    print("SELFTEST PASS (A7): frozen 3 arms + closed controls + 16 driven refusals, "
          "0 FAILED.")
    return 0


# ---------------------------------------------------------------------------
# Producing the reference (S7.6 schema)
# ---------------------------------------------------------------------------
def produce_reference(crop_dir, out_path, lane_id):
    import datetime
    tmp = tempfile.mkdtemp(prefix="t5_a7_ctrl_")
    print("== CONTROLS FIRST (rule 3) ==")
    ctrl = run_closed_controls(tmp)
    for root, _d, files in os.walk(tmp, topdown=False):
        for f in files:
            os.unlink(os.path.join(root, f))
        os.rmdir(root)
    print("== REAL FIGURES ==")
    reads = {}
    refusals = {}
    for fid in ("5.45", "5.37", "5.39"):
        try:
            reads[fid] = read_figure_full(fid, crop_dir)
        except SystemExit as e:
            # capture the refusal text for the record; the rows it feeds stay null
            refusals[fid] = "rc %r (see stderr above)" % e.code
    yspan45 = 90.0
    inc45 = dict(control_max=ctrl["points"]["y_err_max"],
                 control_rms=ctrl["points"]["y_err_rms"],
                 control_max_frac_of_span=ctrl["points"]["y_err_max_frac_of_span"])
    yspan37 = 30.0
    # Fig. 5.37 is read by the RANK reader, so its increment comes from the RANK
    # control, not from the symbol-path control (which is kept and reported as
    # the second opinion on the same raster).
    inc37 = dict(control_column_max=ctrl["rank"]["y_err_max"],
                 control_column_rms=ctrl["rank"]["y_err_rms"],
                 control_mean_max=ctrl["rank"]["mean_err_max"],
                 control_max_frac_of_span=max(ctrl["rank"]["y_err_max_frac_of_span"],
                                              ctrl["rank"]["mean_err_max_frac_of_span"]),
                 symbol_control_marker_max=ctrl["path"]["y_err_max"],
                 symbol_control_mean_max=ctrl["path"]["mean_err_max"])
    rows = {}
    graded_ok = True
    r45 = reads.get("5.45")
    for row, face in (("G1a", "front"), ("G2a", "top"), ("G3a", "rear")):
        v = r45["values_at_abscissa"][face] if r45 else None
        spread = _spread(r45["blind_repeats"][face]) if r45 else None
        radius = r45["symbol_radius_data"] if r45 else None
        inc = max(x for x in (inc45["control_max"], radius, spread) if x is not None) \
            if v else None
        rows[row] = dict(value=None if v is None else round(v["y"], 3),
                         uncertainty=None if v is None else round(0.10 * v["y"], 3),
                         uncertainty_basis="10 % of the value (S7.2: a face average "
                                           "contains its edges; thesis p. 59 'about 10 %')",
                         units="W/m2K", figure="5.45", page_printed=160, page_pdf=162,
                         face=face, abscissa_read=None if v is None else round(v["x"], 1),
                         digitisation_increment=None if inc is None else round(inc, 4),
                         increment_units="W/m2K",
                         increment_components=dict(control_max_err=inc45["control_max"],
                                                   symbol_radius=radius,
                                                   blind_repeat_spread=spread),
                         template_recall=None if v is None else round(v["recall"], 3))
        graded_ok = graded_ok and (v is not None)
    r37 = reads.get("5.37")
    for row, pname in (("G5a", "CD"), ("G5b", "BC"), ("G5c", "AB")):
        m = r37["partition_means"][pname] if r37 else None
        spread = _spread(r37["blind_repeats"][pname]) if r37 else None
        radius = r37["symbol_radius_data"] if r37 else None
        inc = max(x for x in (inc37["control_mean_max"], inc37["control_column_max"],
                              radius, spread) if x is not None) if m else None
        rows[row] = dict(value=None if m is None else round(m["mean_central80"], 3),
                         uncertainty=0.4, units="degC", figure="5.37",
                         page_printed=149, page_pdf=151,
                         face=m["face"] if m else {"CD": "front", "BC": "top", "AB": "rear"}[pname],
                         partition=pname, series="T_co = 75 degC (triangle)",
                         n_columns=None if m is None else m["n_cols"],
                         reader="rank (column-tracked curve, rank 2 of 5 from the "
                                "top; the symbol reader returns 3 of 66 markers of "
                                "the registered series on this crop and is NOT used)",
                         digitisation_increment=None if inc is None else round(inc, 4),
                         increment_units="degC",
                         increment_components=dict(control_column_max_err=inc37["control_column_max"],
                                                   control_mean_max_err=inc37["control_mean_max"],
                                                   symbol_radius=radius,
                                                   blind_repeat_spread=spread))
        graded_ok = graded_ok and (m is not None)
    r39 = reads.get("5.39")
    for row, pname in (("G1", "CD"), ("G2", "BC"), ("G3", "AB")):
        m = r39["partition_means"][pname] if r39 else None
        spread = _spread(r39["blind_repeats"][pname]) if r39 else None
        rows[row] = dict(value=None if m is None else round(m["mean_central80"], 4),
                         uncertainty=None, units="h/h_tot", figure="5.39",
                         page_printed=151, page_pdf=153, partition=pname,
                         series="Re_H = 4440 (triangle)",
                         n_markers=None if m is None else m["n_markers"],
                         digitisation_increment=None if m is None else round(
                             max(x for x in (inc37["control_mean_max"] / yspan37 * 3.0,
                                             r39["symbol_radius_data"], spread)
                                 if x is not None), 4),
                         increment_units="h/h_tot",
                         disposition="REPORTED (S16.4)",
                         note=None if r39 else refusals.get("5.39"))
    hbar = None
    if r45:
        vs = r45["values_at_abscissa"]
        if all(vs[k] is not None for k in ("front", "top", "rear", "side_N", "side_S")):
            hbar = round(sum(vs[k]["y"] for k in ("front", "top", "rear", "side_N",
                                                  "side_S")) / 5.0, 3)
    prov = dict(
        citation="Meinders, E.R. (1998), Experimental study of heat transfer in "
                 "turbulent flows over wall-mounted cubes, TU Delft, ISBN 90-9012103-x",
        sha256="36c89a548030eae2aac84f2453c7c531632998433da660f4b655624cff6514cb",
        title_verified_page1=True,
        digitised=bool(graded_ok),
        digitiser=lane_id,
        digitised_utc=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        page_offset_printed_to_pdf=2,
        instrument="digitise_t5.A7_PROPOSED.py (the frozen e55d6208 lines 1-506 "
                   "verbatim + the A7 closed-frame section), run on the committed "
                   "300-dpi crops; digitised=true ONLY because both closed-frame "
                   "planted controls passed in this same run",
        controls=dict(points=dict(n_planted=ctrl["points"]["n_planted"],
                                  n_recovered=ctrl["points"]["n_recovered"],
                                  y_err_max=ctrl["points"]["y_err_max"],
                                  y_err_rms=ctrl["points"]["y_err_rms"],
                                  y_err_max_pct_of_span=100 * ctrl["points"]["y_err_max_frac_of_span"],
                                  x_err_max=ctrl["points"]["x_err_max"],
                                  n_spurious_gated=ctrl["points"]["n_spurious_gated"],
                                  low_re_planted=ctrl["points"]["low_re_planted"],
                                  low_re_recovered=ctrl["points"]["low_re_recovered"],
                                  n_rejected=ctrl["points"]["n_rejected"],
                                  channel=ctrl["points"]["provenance"]),
                      rank=dict(n_columns_usable=ctrl["rank"]["n_columns_usable"],
                                n_columns_in_frame=ctrl["rank"]["n_columns_in_frame"],
                                columns_usable_frac=ctrl["rank"]["columns_usable_frac"],
                                n_planted_markers=ctrl["rank"]["n_planted_markers"],
                                column_y_err_max=ctrl["rank"]["y_err_max"],
                                column_y_err_rms=ctrl["rank"]["y_err_rms"],
                                column_y_err_max_pct_of_span=100 * ctrl["rank"]["y_err_max_frac_of_span"],
                                partition_means=ctrl["rank"]["partition_means"],
                                mean_err_max=ctrl["rank"]["mean_err_max"],
                                mean_err_max_pct_of_span=100 * ctrl["rank"]["mean_err_max_frac_of_span"],
                                gated_quantity="the partition mean (the quantity "
                                               "the row takes); the per-column "
                                               "error is REPORTED, never gated",
                                channel=ctrl["rank"]["provenance"]),
                      path=dict(n_planted_in_window=ctrl["path"]["n_planted_in_window"],
                                n_recovered_in_window=ctrl["path"]["n_recovered_in_window"],
                                n_planted_total=ctrl["path"]["n_planted_total"],
                                n_spurious_in_window=ctrl["path"]["n_spurious_in_window"],
                                marker_y_err_max=ctrl["path"]["y_err_max"],
                                marker_y_err_rms=ctrl["path"]["y_err_rms"],
                                marker_y_err_max_pct_of_span=100 * ctrl["path"]["y_err_max_frac_of_span"],
                                partition_means=ctrl["path"]["partition_means"],
                                mean_err_max=ctrl["path"]["mean_err_max"],
                                mean_err_max_pct_of_span=100 * ctrl["path"]["mean_err_max_frac_of_span"],
                                channel=ctrl["path"]["provenance"])),
        figure_reads={fid: {k: v for k, v in r.items() if k != "series_points"}
                      for fid, r in reads.items()},
        series_points_5_39=r39["series_points"] if r39 else None,
        refusals=refusals,
        increment_rule="digitisation_increment = max(closed-control MAX error, "
                       "symbol radius in data units, blind-repeat spread) -- S10's "
                       "rule (radius vs spread) widened by the control's measured "
                       "error, never narrowed",
        separation_S10="the author of the A7 section did not write build_t5.py and "
                       "opened no T5 run directory's solver output while producing "
                       "this file",
        what_the_controls_do_not_bound="ink-to-ink overlap of DIFFERENT symbols is "
                                       "planted twice (+ on x, square on triangle); "
                                       "denser overlap as in Fig. 5.39 is not planted "
                                       "and its rows are REPORTED only")
    ref = dict(provenance=prov,
               conditions=dict(Re_H=4440.0, u_B_m_s=4.47, H_m=0.015, T_core_C=75.0,
                               T_in_C=20.5),
               rows=rows,
               reported=dict(G4_thesis_text=dict(x_R_over_H_low=2.4, x_R_over_H_high=2.5,
                                                 page_printed=137, page_pdf=139,
                                                 uncertainty_stated=False),
                             h_bar_cube=dict(value=hbar, units="W/m2K",
                                             reconstructed_from="figure 5.45, five faces "
                                             "at the marker nearest Re_H 4440 (the side "
                                             "faces' + and x are planted-overlap cases; "
                                             "each is read by its own template)",
                                             faces={k: (None if (not r45 or r45["values_at_abscissa"][k] is None)
                                                        else round(r45["values_at_abscissa"][k]["y"], 3))
                                                    for k in ("front", "top", "rear", "side_N", "side_S")})))
    with open(out_path, "w") as fh:
        json.dump(ref, fh, indent=1, default=float)
    print("wrote %s (digitised=%s)" % (out_path, prov["digitised"]))
    return 0


def main_a7():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--closed-controls", action="store_true")
    ap.add_argument("--closed-figure")
    ap.add_argument("--kind", choices=["points", "path"])
    ap.add_argument("--xticks")
    ap.add_argument("--yticks")
    ap.add_argument("--produce-reference", metavar="CROP_DIR")
    ap.add_argument("--lane-id", default="unstated")
    ap.add_argument("--out")
    a, rest = ap.parse_known_args()
    if a.selftest:
        return selftest_a7()
    if a.closed_controls:
        tmp = tempfile.mkdtemp(prefix="t5_a7_ctrl_")
        res = run_closed_controls(tmp)
        if a.out:
            with open(a.out, "w") as fh:
                json.dump(res, fh, indent=1, default=float)
            print("wrote " + a.out)
        for root, _d, files in os.walk(tmp, topdown=False):
            for f in files:
                os.unlink(os.path.join(root, f))
            os.rmdir(root)
        return 0
    if a.closed_figure:
        if not (a.xticks and a.yticks and a.kind):
            refuse("--closed-figure needs --kind, --xticks and --yticks: anchor "
                   "VALUES are registered, never inferred from the image")
        fig = dict(FIGURES["5.45"] if a.kind == "points" else FIGURES["5.37"])
        fig["xticks"] = [float(v) for v in a.xticks.split(",")]
        fig["yticks"] = [float(v) for v in a.yticks.split(",")]
        ink, skew, resid = deskew(load_ink(a.closed_figure))
        got = (read_points_figure if a.kind == "points" else read_path_figure)(ink, fig)
        out = dict(skew_deg=skew, calibration=got["calibration"], frame=got["frame"])
        print(json.dumps(out, indent=1, default=float))
        return 0
    if a.produce_reference:
        if not a.out:
            refuse("--produce-reference needs --out")
        return produce_reference(a.produce_reference, a.out, a.lane_id)
    # legacy open-frame flags go to the frozen main() unchanged
    return main()


if __name__ == "__main__":
    sys.exit(main_a7())
