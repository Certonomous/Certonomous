#!/usr/bin/env python3
"""
Digitiser for Ansys Fluid Dynamics Verification Manual (Release 2026 R1, March 2026),
VMFL078 "Polyhedral Mesh Accuracy", Figure .78.2:
   "Comparison of X-Velocity along the vertical centerline in the symmetry plane"
   printed p.224 == PDF page 238.

The figure is an EMBEDDED RASTER, 720 x 448 px RGB at 96 ppi (pdfimages -list, page
238, object 2923).  That bitmap is the information ceiling: re-rendering the PDF at
higher dpi adds interpolated pixels, not data.  This digitiser therefore reads the
native bitmap.

Series in the figure:
  black line + markers : "Ansys Fluent"  (the manual's own solution)
  red round markers    : "Referance" [sic] -- Jifei Wang & Decheng Wan, "Parallel
                         Simulation of 3D Lid-driven Cubic Cavity Flows by Finite
                         Element Method", Proc. 21st (2011) Int. Offshore and Polar
                         Engineering Conference, Maui, Hawaii, June 19-24 2011.
                         (This is what the MANUAL ITSELF cites -- not Ku/Hirsh/Taylor
                         and not Albensoeder/Kuhlmann.)

Abscissa "Position (m)" is the coordinate ALONG the vertical centerline, i.e. height
y, 0 at the stationary floor and 1 at the moving lid (the curve reaches the lid speed
1.0 m/s at Position = 1.0).  Ordinate is u_x in m/s, lid speed 1 m/s, so the plotted
value is already normalised by the lid speed.

UNCERTAINTY MODEL (fixed here, before any comparison with any solver output):
  u_cal  : axis calibration, from the least-squares residual of the 11 x-ticks and
           8 y-ticks about a straight line.
  u_band : the marker/line band.  At a sampled abscissa the coloured pixels occupy a
           contiguous run of rows; the true curve lies somewhere in that run.  Model
           it as UNIFORM over the run -> u = (half run height)/sqrt(3).  Floored at
           0.5 px/sqrt(3) (pixel quantisation).  In the dense part of the figure the
           round markers overlap and cannot be resolved individually, so this uniform
           model -- not a marker-centroid model -- is the honest one.
  u_thr  : colour-threshold sensitivity, measured by re-extracting at three red
           thresholds and taking the half-spread of the recovered value.
  u_slope: the markers are discrete, so a sampled column may be empty and the reader
           takes the marker within a +-2 column window.  That abscissa error projects
           through the local slope into a velocity error, |du/dy| * u_x, with
           u_x = sqrt((2/sqrt3)^2 + (0.5/sqrt3)^2) px converted to metres, combined
           with the x calibration residual.  Negligible mid-cavity (slope ~0.3-1.5),
           dominant inside the lid boundary layer (slope ~13) -- which is precisely
           why the pre-registered gate does not extend into it.
  U95 = 2 * sqrt(u_cal^2 + u_band^2 + u_thr^2 + u_slope^2).
"""
import json, sys
import numpy as np
from PIL import Image

PNG = sys.argv[1]
OUT = sys.argv[2]

a = np.array(Image.open(PNG).convert("RGB")).astype(int)
assert a.shape == (448, 720, 3), a.shape
R, G, B = a[:, :, 0], a[:, :, 1], a[:, :, 2]

# ---- axis anchors: tick-mark pixel columns/rows, read from the bitmap ------------
XT = {0.0: [215, 216], 0.1: [258, 259], 0.2: [302], 0.3: [345], 0.4: [388, 389],
      0.5: [431, 432], 0.6: [474, 475], 0.7: [518], 0.8: [561], 0.9: [604, 605],
      1.0: [647, 648]}
YT = {1.0: [44, 45], 0.8: [89], 0.6: [134], 0.4: [178, 179], 0.2: [223, 224],
      0.0: [268, 269], -0.2: [313], -0.4: [358]}


def fit(t):
    v = np.array(sorted(t))
    px = np.array([np.mean(t[k]) for k in sorted(t)])
    m, c = np.linalg.lstsq(np.vstack([v, np.ones_like(v)]).T, px, rcond=None)[0]
    return m, c, px - (m * v + c)


MX, CX, RESX = fit(XT)
MY, CY, RESY = fit(YT)
u_cal_x = float(np.sqrt((RESX ** 2).mean()) / abs(MX))          # m
u_cal_y = float(np.sqrt((RESY ** 2).mean()) / abs(MY))          # m/s
col2x = lambda c: (c - CX) / MX
row2u = lambda r: (r - CY) / MY

PLOT_L, PLOT_R = 216, 649      # plot interior columns (y-axis at 215/216, x=1.0 at 647/648)


def red_mask(t):
    m = (R > t) & (R - G > 45) & (R - B > 45)
    m[:, :PLOT_L] = False                      # drop the legend swatch at col 14
    return m


def black_mask():
    m = (R < 110) & (G < 110) & (B < 110)
    m[:, :PLOT_L] = False
    m[356:, :] = False                          # x-axis line at row 358 and tick labels
    return m


def band_at(mask, col, halfwin=2):
    """contiguous row-run of set pixels in a +-halfwin column window about `col`"""
    lo, hi = max(0, col - halfwin), min(mask.shape[1], col + halfwin + 1)
    rows = np.where(mask[:, lo:hi].any(axis=1))[0]
    if rows.size == 0:
        return None
    # keep the run containing the global median (guards against a stray pixel)
    med = int(np.median(rows))
    runs, s, p = [], rows[0], rows[0]
    for v in rows[1:]:
        if v != p + 1:
            runs.append((s, p))
            s = v
        p = v
    runs.append((s, p))
    best = min(runs, key=lambda rr: 0 if rr[0] <= med <= rr[1] else min(abs(rr[0] - med), abs(rr[1] - med)))
    return best


def extract(mask, col):
    br = band_at(mask, col)
    if br is None:
        return None
    r0, r1 = br
    centre = 0.5 * (r0 + r1)
    half = 0.5 * (r1 - r0 + 1)
    return centre, half


THRESHOLDS = (95, 110, 130)
xs_grid = np.arange(PLOT_L, PLOT_R)

series = {}
for name, maskfn in (("reference", lambda t: red_mask(t)), ("fluent", lambda t: black_mask())):
    per_thr = []
    thr_list = THRESHOLDS if name == "reference" else (0,)
    for t in thr_list:
        m = maskfn(t)
        per_thr.append({int(c): extract(m, int(c)) for c in xs_grid})
    series[name] = per_thr

rows = []
for c in xs_grid:
    base = series["reference"][1][int(c)]          # nominal threshold 110
    if base is None:
        continue
    centre, half = base
    vals = [series["reference"][k][int(c)][0] for k in range(3)
            if series["reference"][k][int(c)] is not None]
    u_thr_px = 0.5 * (max(vals) - min(vals)) if len(vals) > 1 else 0.0
    u_band_px = max(half, 0.5) / np.sqrt(3.0)
    u_px = np.sqrt(u_band_px ** 2 + u_thr_px ** 2)
    fl = series["fluent"][0][int(c)]
    rows.append(dict(col=int(c),
                     position_m=float(col2x(c)),
                     u_ref_mps=float(row2u(centre)),
                     _u_vert=float(np.sqrt((u_px / abs(MY)) ** 2 + u_cal_y ** 2)),
                     band_px=float(2 * half),
                     u_fluent_mps=(float(row2u(fl[0])) if fl else None)))

# ---- slope-projected abscissa term, then the combined U95 -----------------------
U_X_PX = float(np.sqrt((2.0 / np.sqrt(3.0)) ** 2 + (0.5 / np.sqrt(3.0)) ** 2))
u_x_m = float(np.sqrt((U_X_PX / abs(MX)) ** 2 + u_cal_x ** 2))
_xa = np.array([q["position_m"] for q in rows])
_ua = np.array([q["u_ref_mps"] for q in rows])
_slope = np.gradient(_ua, _xa)
# smooth the slope over ~9 px so single-pixel steps do not create spurious spikes
_k = np.ones(9) / 9.0
_slope = np.convolve(_slope, _k, mode="same")
for q, sl in zip(rows, _slope):
    uu = float(np.sqrt(q.pop("_u_vert") ** 2 + (abs(sl) * u_x_m) ** 2))
    q["slope_per_m"] = round(float(sl), 4)
    q["u_std_mps"] = round(uu, 6)
    q["U95_mps"] = round(2 * uu, 6)
    q["position_m"] = round(q["position_m"], 6)
    q["u_ref_mps"] = round(q["u_ref_mps"], 6)
    q["band_px"] = round(q["band_px"], 3)
    if q["u_fluent_mps"] is not None:
        q["u_fluent_mps"] = round(q["u_fluent_mps"], 6)

# ---- figure-internal validation of the calibration against two EXACT data --------
# the floor is no-slip (u=0 at Position 0) and the lid moves at 1 m/s (u=1 at Position 1)
def _at(xt):
    j = int(np.argmin(np.abs(_xa - xt)))
    return rows[j]["position_m"], rows[j]["u_ref_mps"], rows[j]["U95_mps"]
VALID = {"floor_no_slip_expect_0.0": _at(0.0), "lid_speed_expect_1.0": _at(1.0)}

meta = dict(
    source_pdf="docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.pdf",
    source_release="Release 2026 R1, March 2026, ANSYS, Inc. (Synopsys) -- title page verified",
    figure="Figure .78.2: Comparison of X-Velocity along the vertical centerline in the symmetry plane",
    printed_page=224, pdf_page=238,
    bitmap="embedded raster 720x448 RGB, 96 ppi, PDF object 2923 (native resolution)",
    manual_cited_reference=("Jifei Wang and Decheng Wan, 'Parallel Simulation of 3D Lid-driven "
                            "Cubic Cavity Flows by Finite Element Method', Proc. Twenty-first (2011) "
                            "International Offshore and Polar Engineering Conference, Maui, Hawaii, "
                            "USA, June 19-24, 2011"),
    abscissa="Position (m) = height along the vertical centerline of the symmetry plane; 0 = floor, 1 = lid",
    ordinate="X Velocity [m/s]; lid speed 1 m/s so the value is u_x/U_lid",
    calibration=dict(
        x_anchor_low="tick 0.0 m at pixel column 215.5",
        x_anchor_high="tick 1.0 m at pixel column 647.5",
        y_anchor_low="tick -0.4 m/s at pixel row 358.0",
        y_anchor_high="tick 1.0 m/s at pixel row 44.5",
        x_px_per_m=round(float(MX), 4), x_intercept_px=round(float(CX), 4),
        y_px_per_mps=round(float(MY), 4), y_intercept_px=round(float(CY), 4),
        x_tick_residual_rms_px=round(float(np.sqrt((RESX ** 2).mean())), 4),
        y_tick_residual_rms_px=round(float(np.sqrt((RESY ** 2).mean())), 4),
        u_cal_x_m=round(u_cal_x, 6), u_cal_y_mps=round(u_cal_y, 6)),
    uncertainty_model=("U95 = 2*sqrt(u_band^2 + u_thr^2 + u_cal^2 + (|du/dy|*u_x)^2); "
                       "u_band = (half band height px)/sqrt(3); u_x = %.5f m" % u_x_m),
    abscissa_std_uncertainty_m=round(u_x_m, 6),
    calibration_validation=VALID,
    red_thresholds_tested=list(THRESHOLDS),
    n_points=len(rows))

json.dump(dict(meta=meta, points=rows), open(OUT, "w"), indent=1)
print("wrote", OUT, len(rows), "columns")
