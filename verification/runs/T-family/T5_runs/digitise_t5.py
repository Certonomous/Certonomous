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


if __name__ == "__main__":
    sys.exit(main())
