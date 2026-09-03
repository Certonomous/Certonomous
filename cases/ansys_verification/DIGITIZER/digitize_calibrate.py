#!/usr/bin/env python3
# =============================================================================
# DIGITIZER instrument -- calibration of read-off uncertainty u_read for the
# ansys-verification team's digitized references.  DRAFT (ansys-lane-opus48).
# NOT A FREEZE COMMIT.
#
# SPECIFICATION: ANSYS_VERIFICATION_CHARTER Amendment v1.23 **section 28** (which
# adopts, as charter law, the five holes this lane found in section 25 before the
# freeze), read together with section 25 (25.1-25.8), and the section 18 / 22.5 /
# 16.4 constructions they reuse.  Where 28 rules, 28 governs.
#
# WHAT THIS IS.  A digitized reference is a *measurement of a figure* (25.1), not a
# reference value; it carries u_read.  This script builds the reader and CALIBRATES
# u_read on SYNTHETIC plates whose truth is known BY CONSTRUCTION (25.3), and does
# so PER GATED QUANTITY IN THAT QUANTITY'S OWN UNITS (28.2).
#
# 28.2 THE WRONG-NUMBER PATH, CLOSED.  A y-value u_read folded into an x-location
# gate is dimensionally meaningless.  Every term of 25.4 (synthetic-control
# statistic, pixel floor, two-read-off half-spread) is computed ON THE GATED
# QUANTITY IN ITS OWN UNITS.  Two quantities are implemented, the two this team
# will need first:
#   * VALUE   -- a value-at-a-station read; units = y data-units; controls plant a
#                known y-offset of the curve.
#   * POSITION-- the x-location of a feature (e.g. a shock); units = x data-units;
#                controls plant a known x-DISPLACEMENT of the feature, never a
#                y-offset.  This is Fig .46.2's quantity (shock location).
# A value u_read never licenses a position gate, and vice versa (28.2).
#
# THREE PLANTS PER QUANTITY, each REFUSING (exit 2) rather than degrading
# (25.3, rule 3, 16.4):
#   * PLANT-DETECT  a control displaced by 3 u_read (IN THE QUANTITY'S DIMENSION)
#                   MUST read back as displaced; a blind reader refuses.
#   * PLANT-NULL    an undisplaced control MUST read back at zero within u_read; a
#                   reader that reports displacement on a clean control refuses.
#   * AXIS PLANT    (28.4) axis fitted on a SUBSET of ticks, verified against a
#                   HELD-OUT tick (pixel floor); PLUS orientation declared
#                   explicitly and a SLOPE-SIGN check against that declaration.  A
#                   planted-flip (pairing reversed vs the declaration) MUST refuse
#                   -- the held-out check alone passes a flip (L-436's class: fit
#                   and check degrade together), and the slope-sign check is the
#                   independent third assertion that breaks that agreement.  A log
#                   axis declared linear also refuses.
#
# u_read (25.4 / 28.2) = max( synthetic-control statistic on the quantity,
#                             HALF the spread of two independent read-offs OF THE
#                               QUANTITY (28.3: perturbation ranges pre-registered
#                               and DEFENDED; narrowing one after a target value is
#                               known voids the calibration),
#                             the one-pixel floor on the quantity's axis ).
# 28.5: where the read is locally steep, the steep-region statistic is used; both
# are reported and the choice is frozen before the read.
#
# 28.6: synthetic plates are matched to the target's ANSWER-BLIND FORMAT only; the
# curve values are never read.  u_read is PER-TARGET-FORMAT, re-derived per case.
# There is NO lab-wide u_read.
#
# HARD RULE (25.2 / 28.8).  Calibrated on SYNTHETIC plates ONLY.  Never reads
# VM2026R1 Fig .46.2 or any real plate from a case whose answer this lab knows.
# There is no mode that opens a real plate.
#
# MODES:
#   --selftest    exercise every arm on small fixtures; NO committed u_read.  This
#                 is the "build & self-test" step, allowed pre-freeze.
#   --calibrate   POST-FREEZE: render N>=20 plates per the FROZEN answer-blind
#                 format and DERIVE the committed per-quantity u_read.  Consumes
#                 compute the pre-registration governs; MUST NOT run until the
#                 supervisor commits the freeze.
# =============================================================================
import os, sys, math, json, hashlib, argparse, tempfile, shutil
import numpy as np

try:
    from PIL import Image
except Exception as e:                                        # pragma: no cover
    sys.stderr.write("REFUSE (exit 2): Pillow (PIL) is required: %s\n" % e); sys.exit(2)

# ---- frozen constants (a-priori; NEVER derived from a calibration run) -------
# A REPRESENTATIVE answer-blind format (28.6), deliberately NOT Fig .46.2's.  Per
# case, the synthetic plates are re-matched to the target's answer-blind format and
# u_read re-derived (28.6); nothing here transfers to a case by assertion.
DPI              = 150
FIG_W_IN, FIG_H_IN = 6.0, 4.5             # -> 900 x 675 px
MARGIN_PX        = 90                      # plot-box inset -> 720 x 495 interior
TICK_LEN_PX      = 8
LINE_WIDTH_PX    = 2.0
FRAME_WIDTH_PX   = 2.0
GRID_GRAY        = 0.85
CURVE_RGB        = (0.05, 0.10, 0.75)      # distinct BLUE curve; ticks/frame black
N_CAL            = 24                       # calibration plates (>= 20, 25.3)
N_XSAMPLE        = 4                        # curve super-sampling per column (gap-free)

# plant / acceptance thresholds (pre-registered; see PREREGISTRATION.md sec 6)
FLOOR_PX         = 1.5                      # AXIS held-out tolerance: 1 px + AA slack
DETECT_MULT      = 3.0                      # PLANT-DETECT displacement = 3 * u_read
DETECT_BAND      = 1.0                      # GATE: |recovered - planted| <= BAND*u_read
NULL_K           = 1.0                      # PLANT-NULL: |offset| <= K*u_read else refuse

# 28.3 -- PERTURBATION RANGES for the two independent read-offs, FROZEN AND DEFENDED.
# Narrowing any of these AFTER a target value is known voids the calibration (28.3);
# where disputed, the WIDER defensible range is used.  Defences are in the prereg.
COLOR_THRESH_RANGE = (0.28, 0.42)          # curve-colour selection radius (of sqrt3)
FEAT_WIN_RANGE     = (1, 3)                 # px half-window for feature-x refinement
# tick-drop: any one INTERIOR tick may be dropped from each axis fit.
COLOR_THRESH_DEFAULT = 0.35
SEED0            = 20260903

# orientation -> sign of the fit slope (pixel vs data), given ticks detected ASC.
# x ticks asc = left->right cols ; y ticks asc = top->bottom rows.
ORIENT_SIGN = {"right": +1, "left": -1, "up": -1, "down": +1}

class SystemExit2(SystemExit):
    def __init__(self, msg): super().__init__(2); self.msg = msg
def refuse(msg):
    sys.stderr.write("REFUSE (exit 2): %s\n" % msg); raise SystemExit2(msg)


# =============================================================================
# PlateSpec + transforms (KNOWN BY CONSTRUCTION for rendering; RECOVERED, never
# handed, for digitizing).
# =============================================================================
class PlateSpec:
    def __init__(self, x_range, y_range, x_ticks, y_ticks, x_log=False, y_log=False,
                 x_orient="right", y_orient="up",
                 w=None, h=None, margin=MARGIN_PX, dpi=DPI,
                 line_width=LINE_WIDTH_PX, tick_len=TICK_LEN_PX):
        self.x0, self.x1 = float(x_range[0]), float(x_range[1])
        self.y0, self.y1 = float(y_range[0]), float(y_range[1])
        self.x_ticks = [float(t) for t in x_ticks]; self.y_ticks = [float(t) for t in y_ticks]
        self.x_log, self.y_log = bool(x_log), bool(y_log)
        self.x_orient, self.y_orient = x_orient, y_orient
        self.w = int(w if w is not None else round(FIG_W_IN * dpi))
        self.h = int(h if h is not None else round(FIG_H_IN * dpi))
        self.margin = int(margin); self.dpi = int(dpi)
        self.line_width = float(line_width); self.tick_len = int(tick_len)
        self.bx0 = self.margin; self.bx1 = self.w - self.margin
        self.by0 = self.margin; self.by1 = self.h - self.margin
        if self.x_log and (self.x0 <= 0 or self.x1 <= 0): refuse("log x with non-positive range")
        if self.y_log and (self.y0 <= 0 or self.y1 <= 0): refuse("log y with non-positive range")

    def _tx(self, xd):
        xd = np.asarray(xd, float)
        return ((np.log10(xd) - np.log10(self.x0)) / (np.log10(self.x1) - np.log10(self.x0))
                if self.x_log else (xd - self.x0) / (self.x1 - self.x0))
    def _ty(self, yd):
        yd = np.asarray(yd, float)
        return ((np.log10(yd) - np.log10(self.y0)) / (np.log10(self.y1) - np.log10(self.y0))
                if self.y_log else (yd - self.y0) / (self.y1 - self.y0))
    def x_to_col(self, xd):
        u = self._tx(xd)
        return self.bx0 + (u if self.x_orient == "right" else (1 - u)) * (self.bx1 - self.bx0)
    def y_to_row(self, yd):
        v = self._ty(yd)
        return (self.by1 - v * (self.by1 - self.by0) if self.y_orient == "up"
                else self.by0 + v * (self.by1 - self.by0))
    def x_units_per_px(self):
        span = (self.bx1 - self.bx0)
        if self.x_log:
            mid = math.sqrt(self.x0 * self.x1)
            return mid * math.log(10.0) * (math.log10(self.x1) - math.log10(self.x0)) / span
        return (self.x1 - self.x0) / span
    def y_units_per_px(self):
        span = (self.by1 - self.by0)
        if self.y_log:
            mid = math.sqrt(self.y0 * self.y1)
            return mid * math.log(10.0) * (math.log10(self.y1) - math.log10(self.y0)) / span
        return (self.y1 - self.y0) / span


# =============================================================================
# Antialiased rasteriser.  Pixel (row r, col c) centre at (x=c, y=r).
# =============================================================================
def _blend_seg(img, p0, p1, width, rgb):
    x0, y0 = p0; x1, y1 = p1; H, W = img.shape[0], img.shape[1]; pad = width + 1.0
    minc = max(int(math.floor(min(x0, x1) - pad)), 0); maxc = min(int(math.ceil(max(x0, x1) + pad)), W - 1)
    minr = max(int(math.floor(min(y0, y1) - pad)), 0); maxr = min(int(math.ceil(max(y0, y1) + pad)), H - 1)
    if minc > maxc or minr > maxr: return
    cc, rr = np.meshgrid(np.arange(minc, maxc + 1, dtype=float), np.arange(minr, maxr + 1, dtype=float))
    dx, dy = (x1 - x0), (y1 - y0); L2 = dx * dx + dy * dy
    t = np.zeros_like(cc) if L2 < 1e-12 else np.clip(((cc - x0) * dx + (rr - y0) * dy) / L2, 0.0, 1.0)
    dist = np.sqrt((cc - (x0 + t * dx)) ** 2 + (rr - (y0 + t * dy)) ** 2)
    cov = np.clip(width / 2.0 + 0.5 - dist, 0.0, 1.0)
    sub = img[minr:maxr + 1, minc:maxc + 1, :]
    for k in range(3): sub[:, :, k] = sub[:, :, k] * (1.0 - cov) + rgb[k] * cov

def _polyline(img, cols, rows, width, rgb):
    for i in range(len(cols) - 1):
        _blend_seg(img, (cols[i], rows[i]), (cols[i + 1], rows[i + 1]), width, rgb)

def render_plate(spec, curve_fn, y_displace=0.0):
    img = np.ones((spec.h, spec.w, 3), dtype=float); black = (0.0, 0.0, 0.0)
    for xt in spec.x_ticks:
        c = float(spec.x_to_col(xt)); _blend_seg(img, (c, spec.by0), (c, spec.by1), 1.0, (GRID_GRAY,) * 3)
    for yt in spec.y_ticks:
        r = float(spec.y_to_row(yt)); _blend_seg(img, (spec.bx0, r), (spec.bx1, r), 1.0, (GRID_GRAY,) * 3)
    _blend_seg(img, (spec.bx0, spec.by0), (spec.bx1, spec.by0), FRAME_WIDTH_PX, black)
    _blend_seg(img, (spec.bx0, spec.by1), (spec.bx1, spec.by1), FRAME_WIDTH_PX, black)
    _blend_seg(img, (spec.bx0, spec.by0), (spec.bx0, spec.by1), FRAME_WIDTH_PX, black)
    _blend_seg(img, (spec.bx1, spec.by0), (spec.bx1, spec.by1), FRAME_WIDTH_PX, black)
    for xt in spec.x_ticks:
        c = float(spec.x_to_col(xt)); _blend_seg(img, (c, spec.by1), (c, spec.by1 + spec.tick_len), FRAME_WIDTH_PX, black)
    for yt in spec.y_ticks:
        r = float(spec.y_to_row(yt)); _blend_seg(img, (spec.bx0 - spec.tick_len, r), (spec.bx0, r), FRAME_WIDTH_PX, black)
    ncol = spec.bx1 - spec.bx0; n = max(64, ncol * N_XSAMPLE)
    xs = (np.power(10.0, np.linspace(math.log10(spec.x0), math.log10(spec.x1), n))
          if spec.x_log else np.linspace(spec.x0, spec.x1, n))
    ys = np.asarray(curve_fn(xs), float) + y_displace
    cols = spec.x_to_col(xs); rows = spec.y_to_row(ys)
    inside = (rows >= spec.by0 - 1) & (rows <= spec.by1 + 1)
    _polyline(img, cols[inside], np.clip(rows[inside], spec.by0, spec.by1), spec.line_width, CURVE_RGB)
    return (np.clip(img, 0.0, 1.0) * 255.0 + 0.5).astype(np.uint8)

def save_png(arr, path): Image.fromarray(arr, "RGB").save(path)


# =============================================================================
# The DIGITIZER: recover axes from ticks, extract the curve, invert to data.  Given
# only the tick DATA VALUES (from the axis LABELS a human reads), the log/linear
# flags, and the ORIENTATION declaration -- never the transform (25.3, 28.4).
# =============================================================================
def _find_frame(dark):
    H, W = dark.shape; rowsum = dark.sum(axis=1); colsum = dark.sum(axis=0)
    top = int(np.argmax(rowsum[: H // 3])); bot = int(H - 1 - np.argmax(rowsum[::-1][: H // 3]))
    lft = int(np.argmax(colsum[: W // 3])); rgt = int(W - 1 - np.argmax(colsum[::-1][: W // 3]))
    def _cen(v, i, rad=3):
        lo = max(0, i - rad); hi = min(len(v), i + rad + 1); w = v[lo:hi]; idx = np.arange(lo, hi)
        return float((w * idx).sum() / w.sum()) if w.sum() > 0 else float(i)
    bx0, by0, bx1, by1 = _cen(colsum, lft), _cen(rowsum, top), _cen(colsum, rgt), _cen(rowsum, bot)
    if not (bx1 - bx0 > 20 and by1 - by0 > 20): refuse("frame not found")
    return bx0, by0, bx1, by1

def _clusters(mask, weight):
    out = []; i = 0; n = len(mask)
    while i < n:
        if mask[i]:
            j = i
            while j < n and mask[j]: j += 1
            idx = np.arange(i, j); w = weight[i:j]
            out.append(float((idx * w).sum() / w.sum()) if w.sum() > 0 else float((i + j - 1) / 2)); i = j
        else: i += 1
    return out

def _detect_ticks(dark, box):
    bx0, by0, bx1, by1 = box; H, W = dark.shape
    r_lo = int(round(by1)) + 2; r_hi = min(H, int(round(by1)) + TICK_LEN_PX)
    band = dark[r_lo:r_hi, :].sum(axis=0) if r_hi > r_lo else np.zeros(W)
    xmask = band > (0.5 * band.max() if band.max() > 0 else 1e9)
    xmask[: int(bx0) - 2] = False; xmask[int(bx1) + 3:] = False
    c_lo = max(0, int(round(bx0)) - TICK_LEN_PX); c_hi = int(round(bx0)) - 2
    band2 = dark[:, c_lo:c_hi].sum(axis=1) if c_hi > c_lo else np.zeros(H)
    ymask = band2 > (0.5 * band2.max() if band2.max() > 0 else 1e9)
    ymask[: int(by0) - 2] = False; ymask[int(by1) + 3:] = False
    return sorted(_clusters(xmask, band)), sorted(_clusters(ymask, band2))

def _pair(pix_asc, data_vals, orient):
    """Assign data values to ascending pixel positions per the declared orientation."""
    ds = sorted(float(v) for v in data_vals)                 # ascending
    if orient in ("right", "down"):
        return list(pix_asc), ds                             # slope > 0
    return list(pix_asc), ds[::-1]                           # left/up -> slope < 0

def _fit_axis(pix, data, is_log, holdout_idx, orient, force_flip=False):
    if len(pix) != len(data):
        refuse("axis fit: %d tick pixels vs %d labels -- a tick was missed or invented" % (len(pix), len(data)))
    if len(pix) < 3: refuse("axis fit needs >=3 ticks for a held-out check; got %d" % len(pix))
    if force_flip: data = list(reversed(data))               # TEST-ONLY: planted flip (28.4)
    T = (lambda d: math.log10(d)) if is_log else (lambda d: d)
    idxs = [i for i in range(len(pix)) if i != holdout_idx]
    X = np.array([T(data[i]) for i in idxs]); Y = np.array([pix[i] for i in idxs], float)
    b, a = np.polyfit(X, Y, 1)
    # SLOPE-SIGN check (28.4): the independent third assertion that does not degrade
    # with the pairing; it catches a pairing inconsistent with the declared
    # orientation (the class that bit the build), which the held-out check passes.
    want = ORIENT_SIGN[orient]
    if not (b * want > 0):
        refuse("AXIS PLANT slope-sign: fitted slope %.4g contradicts declared orientation '%s' "
               "(a reversed pairing is a self-consistent line the held-out check passes; 28.4)" % (b, orient))
    pred = a + b * T(data[holdout_idx]); err = abs(pred - pix[holdout_idx])
    return a, b, err

def digitize(arr, labels, nuisance=None):
    """labels: {x_ticks,y_ticks,x_log,y_log,x_orient,y_orient} -- answer-blind
    format only.  Returns read curve + axis diagnostics.  REFUSES on axis-plant /
    slope-sign / extraction failure."""
    nu = nuisance or {}
    rgb = arr.astype(float) / 255.0
    blackish = ((rgb[:, :, 0] < 0.35) & (rgb[:, :, 1] < 0.35) & (rgb[:, :, 2] < 0.35)).astype(float)
    box = _find_frame(blackish); bx0, by0, bx1, by1 = box
    xcols, yrows = _detect_ticks(blackish, box)
    xp, xd = _pair(xcols, labels["x_ticks"], labels.get("x_orient", "right"))
    yp, yd = _pair(yrows, labels["y_ticks"], labels.get("y_orient", "up"))
    # nuisance: drop one INTERIOR tick from each fit (a defensible operator choice)
    def _drop(p, d, which):
        if which is None or len(p) <= 3: return p, d
        k = 1 + (which % (len(p) - 2)); return p[:k] + p[k + 1:], d[:k] + d[k + 1:]
    xp, xd = _drop(xp, xd, nu.get("drop_x")); yp, yd = _drop(yp, yd, nu.get("drop_y"))
    ax_a, ax_b, xerr = _fit_axis(xp, xd, labels["x_log"], len(xp) - 1, labels.get("x_orient", "right"))
    ay_a, ay_b, yerr = _fit_axis(yp, yd, labels["y_log"], len(yp) - 1, labels.get("y_orient", "up"),
                                 force_flip=bool(nu.get("force_pair_flip")))
    if xerr > FLOOR_PX: refuse("AXIS PLANT (x): held-out tick off %.3f px > %.2f (log-as-linear lands here)" % (xerr, FLOOR_PX))
    if yerr > FLOOR_PX: refuse("AXIS PLANT (y): held-out tick off %.3f px > %.2f" % (yerr, FLOOR_PX))
    def col_to_x(c):
        t = (c - ax_a) / ax_b; return 10.0 ** t if labels["x_log"] else t
    def row_to_y(r):
        t = (r - ay_a) / ay_b; return 10.0 ** t if labels["y_log"] else t
    cthr = nu.get("color_thresh", COLOR_THRESH_DEFAULT)
    cd = np.sqrt((rgb[:, :, 0] - CURVE_RGB[0]) ** 2 + (rgb[:, :, 1] - CURVE_RGB[1]) ** 2 + (rgb[:, :, 2] - CURVE_RGB[2]) ** 2)
    curveness = np.clip(1.0 - cd / (cthr * math.sqrt(3.0)), 0.0, 1.0)
    c0, c1 = int(math.ceil(bx0 + 2)), int(math.floor(bx1 - 2))
    r0, r1 = int(math.ceil(by0 + 1)), int(math.floor(by1 - 1))
    rx, ry = [], []
    rows = np.arange(r0, r1 + 1, dtype=float)
    for c in range(c0, c1 + 1):
        colw = curveness[r0:r1 + 1, c]; s = colw.sum()
        if s <= 1e-6: continue
        rx.append(col_to_x(float(c))); ry.append(row_to_y(float((rows * colw).sum() / s)))
    if len(rx) < 10: refuse("digitize: only %d curve columns (<10) -- extraction failed" % len(rx))
    o = np.argsort(rx)
    return {"x": np.array(rx)[o], "y": np.array(ry)[o],
            "x_holdout_err_px": xerr, "y_holdout_err_px": yerr,
            "n_xticks": len(xcols), "n_yticks": len(yrows), "feat_win": int(nu.get("feat_win", 1))}


def _interp(x, y, x0):
    if x0 <= x[0]: return y[0]
    if x0 >= x[-1]: return y[-1]
    i = int(np.searchsorted(x, x0)) - 1; i = max(0, min(i, len(x) - 2))
    t = (x0 - x[i]) / (x[i + 1] - x[i]); return y[i] * (1 - t) + y[i + 1] * t


# =============================================================================
# QUANTITIES (28.2).  Each measures ONE gated quantity, in ITS OWN units, and
# defines the truth that quantity has by construction.
# =============================================================================
class ValueQuantity:
    """Value-at-a-station: read y at a fixed x station.  Units = y data-units.
    A y-offset control (y_displace) is its PLANT-DETECT displacement."""
    dim = "value"; units = "y-data"
    def __init__(self, spec, x_station): self.spec = spec; self.x_station = float(x_station)
    def measure(self, read): return _interp(read["x"], read["y"], self.x_station)
    def truth(self, curve_fn, y_displace=0.0): return float(np.asarray(curve_fn(np.array([self.x_station])))[0]) + y_displace
    def pixel_floor(self): return self.spec.y_units_per_px()
    def render(self, curve_fn, disp): return render_plate(self.spec, curve_fn, y_displace=disp)  # disp is a y-offset

class PositionQuantity:
    """x-location of a feature (steepest DESCENT).  Units = x data-units.  Its
    PLANT-DETECT displacement is a known x-DISPLACEMENT of the feature (28.2),
    realised by rendering the curve with its feature shifted -- never a y-offset.
    Measure-only: the per-plate truth (the feature's known x) is supplied by the
    caller, so the SAME digitize serves both quantities (cost discipline, 28.7)."""
    dim = "position"; units = "x-data"
    def __init__(self, spec): self.spec = spec
    def _locate(self, x, y, win=1):
        if len(x) < 7: refuse("position: too few points to locate a feature")
        k = max(1, int(win))
        # EDGE-REPLICATING moving average -- np.convolve mode='same' zero-pads and
        # fabricates a gradient cliff at the plot boundary that captures argmin
        # (this bit the build: the feature located at the right edge, not the shock).
        yp = np.pad(np.asarray(y, float), k, mode="edge")
        ker = np.ones(2 * k + 1) / (2 * k + 1)
        ys = np.convolve(yp, ker, mode="valid")
        dydx = np.gradient(ys, x)
        m = max(k + 1, 2)                                     # search the INTERIOR only
        i = m + int(np.argmin(dydx[m:len(x) - m]))           # steepest descent
        lo = max(0, i - k); hi = min(len(x), i + k + 1)      # centroid of the steep neighbourhood
        w = np.clip(-dydx[lo:hi], 0, None)
        return float((x[lo:hi] * w).sum() / w.sum()) if w.sum() > 0 else float(x[i])
    def measure(self, read): return self._locate(read["x"], read["y"], read.get("feat_win", 1))
    def pixel_floor(self): return self.spec.x_units_per_px()


# =============================================================================
# Two independent read-offs (25.4 middle term, 28.3).  Independence is manufactured
# by INDEPENDENTLY perturbing DEFENSIBLE operator choices whose ranges are frozen
# and defended (COLOR_THRESH_RANGE, tick-drop, FEAT_WIN_RANGE).  Half the spread of
# THE QUANTITY is the operator-variance floor.  Demonstrated on synthetic plates;
# per case it runs on the target plate at registration -- never on a forbidden plate.
# =============================================================================
def _nuisance(rng):
    return {"drop_x": int(rng.integers(0, 1000)), "drop_y": int(rng.integers(0, 1000)),
            "color_thresh": float(rng.uniform(*COLOR_THRESH_RANGE)),
            "feat_win": int(rng.integers(FEAT_WIN_RANGE[0], FEAT_WIN_RANGE[1] + 1))}

def two_readoff_halfspread(arr, labels, quantity, seed):
    a = digitize(arr, labels, _nuisance(np.random.default_rng(seed)))
    b = digitize(arr, labels, _nuisance(np.random.default_rng(seed + 777)))
    qa, qb = quantity.measure(a), quantity.measure(b)
    return 0.5 * abs(qa - qb), qa, qb


# =============================================================================
# Synthetic curve families.  Truth is whatever these RETURN.  nozzle_curve carries
# BOTH a smooth region (value read) and a sharp feature (position read) in one
# plate, so ONE set of N plates calibrates BOTH quantities (cost discipline, 28.7).
# =============================================================================
def nozzle_curve(spec, feat_x, peak=2.0, lo=0.4, post=0.9, s=0.012):
    x0, x1 = spec.x0, spec.x1; tc = (feat_x - x0) / (x1 - x0)
    amp = peak - post
    def f(x):
        t = (np.asarray(x, float) - x0) / (x1 - x0)
        rise = lo + (peak - lo) * np.clip(t / max(tc, 1e-6), 0, 1)
        shock = amp * 0.5 * (1 + np.tanh((t - tc) / s))
        y = rise - shock
        return np.clip(y, spec.y0 + 0.02 * (spec.y1 - spec.y0), spec.y1 - 0.02 * (spec.y1 - spec.y0))
    return f

def nozzle_factory(spec, **kw):
    return lambda feat_x: nozzle_curve(spec, feat_x, **kw)

def cal_plate_params(i):
    """Deterministic per-plate variation across the family (feature x, shape)."""
    rng = np.random.default_rng(SEED0 + i)
    feat_x = float(rng.uniform(0.9, 1.3))          # feature location varies (x in [0,2])
    peak = float(rng.uniform(1.9, 2.15)); lo = float(rng.uniform(0.35, 0.55))
    post = float(rng.uniform(0.8, 1.05)); s = float(rng.uniform(0.010, 0.016))
    return feat_x, dict(peak=peak, lo=lo, post=post, s=s)

def default_spec(x_log=False):
    if x_log:
        return PlateSpec((0.1, 100.0), (0.0, 2.5), [0.1, 1.0, 10.0, 100.0],
                         [0.0, 0.5, 1.0, 1.5, 2.0, 2.5], x_log=True)
    return PlateSpec((0.0, 2.0), (0.0, 2.5), [0.0, 0.4, 0.8, 1.2, 1.6, 2.0],
                     [0.0, 0.5, 1.0, 1.5, 2.0, 2.5])

def labels_of(spec):
    return {"x_ticks": spec.x_ticks, "y_ticks": spec.y_ticks, "x_log": spec.x_log,
            "y_log": spec.y_log, "x_orient": spec.x_orient, "y_orient": spec.y_orient}

X_STATION = 0.517   # a SMOOTH (pre-feature) station for the value read, frozen; chosen
                    # OFF a pixel-centre column so the value error is representative,
                    # not the coincidental ~0 an exact pixel-centre station can give.


# =============================================================================
# Per-quantity finalisation + the three plants (each refuses -> NOT A RESULT).
# The per-plate errors are collected ONCE from the shared family in calibrate();
# this assembles the three u_read floors and runs the plants for one quantity.
# =============================================================================
def finalize_quantity(spec, labels, quantity, errs, steep_errs,
                      control_render, control_truth, verbose=True):
    errs = np.asarray(errs, float)
    syn_rms = float(np.sqrt(np.mean(errs ** 2)))
    syn_rms_steep = float(np.sqrt(np.mean(np.asarray(steep_errs, float) ** 2))) if steep_errs else None
    pixel_floor = quantity.pixel_floor()
    # two independent read-offs OF THIS QUANTITY on the reference control plate (28.3)
    half_spread, qa, qb = two_readoff_halfspread(control_render(0.0), labels, quantity, SEED0)
    u_read = max(syn_rms, half_spread, pixel_floor)
    # PLANT-NULL (undisplaced control reads back within u_read)
    null_err = quantity.measure(digitize(control_render(0.0), labels)) - control_truth
    if abs(null_err) > NULL_K * u_read:
        refuse("PLANT-NULL [%s]: clean control offset %.5g > %.5g (K*u_read)" % (quantity.dim, null_err, NULL_K * u_read))
    # PLANT-DETECT (displacement IN THE QUANTITY'S OWN DIMENSION, 28.2)
    delta = DETECT_MULT * u_read
    det = quantity.measure(digitize(control_render(delta), labels)) - control_truth
    if det <= u_read:
        refuse("PLANT-DETECT [%s]: 3u_read=%.5g read as %.5g <= u_read -- BLIND (rule 3)" % (quantity.dim, delta, det))
    recovery_err = abs(det - delta)
    rep = {"dim": quantity.dim, "units": quantity.units, "u_read": u_read,
           "terms": {"syn_rms": syn_rms, "half_spread": half_spread, "pixel_floor": pixel_floor},
           "syn_rms_steep": syn_rms_steep, "rms_bias": float(np.mean(errs)),
           "plant_detect": {"delta_3u": delta, "recovered": det, "recovery_err": recovery_err,
                            "band_ok": recovery_err <= DETECT_BAND * u_read},
           "plant_null": {"offset": null_err, "limit": NULL_K * u_read}}
    if verbose:
        print("  [%-8s] u_read=%.5g %s  (syn_rms=%.4g half=%.4g floor=%.4g)  detect_band_ok=%s bias=%.4g"
              % (quantity.dim, u_read, quantity.units, syn_rms, half_spread, pixel_floor,
                 rep["plant_detect"]["band_ok"], rep["rms_bias"]))
        if syn_rms_steep is not None:
            print("             steep-region syn_rms=%.4g (%.2fx whole) -- a steep read uses THIS (28.5)"
                  % (syn_rms_steep, syn_rms_steep / syn_rms if syn_rms else float("nan")))
    return rep


def calibrate(out_dir=None, n=N_CAL, verbose=True):
    """ONE nozzle family of N plates serves BOTH gated quantities: each plate is
    digitized ONCE and yields a value error (at X_STATION) and a position error
    (the located feature vs its known x).  28.7 cost discipline."""
    spec = default_spec(); labels = labels_of(spec)
    valq = ValueQuantity(spec, X_STATION); posq = PositionQuantity(spec)
    verr, verr_steep, perr = [], [], []
    fam0 = None
    for i in range(n):
        feat_x, kw = cal_plate_params(i); cf = nozzle_curve(spec, feat_x, **kw)
        arr = render_plate(spec, cf, 0.0)
        if out_dir: save_png(arr, os.path.join(out_dir, "cal_%02d.png" % i))
        rd = digitize(arr, labels)                          # AXIS PLANT runs inside
        verr.append(valq.measure(rd) - float(cf(np.array([X_STATION]))[0]))
        perr.append(posq.measure(rd) - feat_x)
        yv = np.asarray(cf(rd["x"]), float); sl = np.abs(np.gradient(yv, rd["x"])); steep = sl >= np.median(sl)
        if steep.sum() > 3:
            verr_steep.append(float(np.sqrt(np.mean((rd["y"][steep] - yv[steep]) ** 2))))
        if i == 0: fam0 = (cf, feat_x, kw)
    cf0, feat0, kw0 = fam0
    if verbose: print("CALIBRATION (per gated quantity, in its own units; 28.2):")
    rv = finalize_quantity(spec, labels, valq, verr, verr_steep,
                           control_render=lambda d: render_plate(spec, cf0, y_displace=d),   # y-offset (value dim)
                           control_truth=float(cf0(np.array([X_STATION]))[0]), verbose=verbose)
    rp = finalize_quantity(spec, labels, posq, perr, None,
                           control_render=lambda d: render_plate(spec, nozzle_curve(spec, feat0 + d, **kw0), 0.0),  # x-disp (position dim)
                           control_truth=feat0, verbose=verbose)
    # AXIS PLANT negative controls (shared): log-as-linear + planted-flip MUST refuse (28.4)
    lspec = default_spec(x_log=True)
    log_caught = _neg_control_refuses(lambda: digitize(
        render_plate(lspec, nozzle_curve(lspec, 5.0), 0.0), {**labels_of(lspec), "x_log": False}))
    flip_arr = render_plate(spec, cf0, 0.0)
    flip_caught = _neg_control_refuses(lambda: digitize(flip_arr, labels, {"force_pair_flip": True}))
    if not log_caught: refuse("AXIS PLANT: log-as-linear NOT caught")
    if not flip_caught: refuse("AXIS PLANT: planted axis-flip NOT caught (28.4)")
    # ---- task verdict (its own; see PREREGISTRATION.md sec 6) ----
    band_ok = rv["plant_detect"]["band_ok"] and rp["plant_detect"]["band_ok"]
    bias_ok = abs(rv["rms_bias"]) <= rv["u_read"] and abs(rp["rms_bias"]) <= rp["u_read"]
    verdict = "PASS" if (band_ok and bias_ok) else "GATE FAIL"
    rep = {"verdict": verdict, "n_plates": n, "value": rv, "position": rp,
           "axis_negatives": {"log_as_linear_caught": log_caught, "planted_flip_caught": flip_caught},
           "band_ok": band_ok, "bias_ok": bias_ok}
    if verbose:
        print("AXIS negatives: log-as-linear caught=%s  planted-flip caught=%s" % (log_caught, flip_caught))
        print("CALIBRATION VERDICT: %s  (value u_read=%.5g y-data ; position u_read=%.5g x-data)"
              % (verdict, rv["u_read"], rp["u_read"]))
        print(json.dumps(rep, indent=2, default=lambda o: float(o) if isinstance(o, (np.floating,)) else o))
    return rep

def _neg_control_refuses(thunk):
    try: thunk(); return False
    except SystemExit2: return True


# =============================================================================
# SELFTEST (allowed pre-freeze).  Exercises EVERY arm on small fixtures and proves
# each plant fires / refuses.  Produces NO committed u_read.
# =============================================================================
def selftest():
    ok = True; tmp = tempfile.mkdtemp(prefix="digitizer_selftest_")
    try:
        spec = default_spec(); labels = labels_of(spec)
        cf = nozzle_curve(spec, 1.10)
        arr = render_plate(spec, cf, 0.0); rd = digitize(arr, labels)
        # 0 value read
        valq = ValueQuantity(spec, X_STATION)
        verr = valq.measure(rd) - valq.truth(cf, 0.0)
        print("SELFTEST 0 value read@x=%.2f: err=%.4g holdout_px=(%.3f,%.3f)" % (X_STATION, verr, rd["x_holdout_err_px"], rd["y_holdout_err_px"]))
        ok = ok and abs(verr) < 5 * spec.y_units_per_px() and rd["x_holdout_err_px"] <= FLOOR_PX
        # 0b position read (truth = the known feature x, 1.10)
        posq = PositionQuantity(spec)
        perr = posq.measure(rd) - 1.10
        print("SELFTEST 0b position read: feature err=%.4g x-data (floor_x=%.4g)" % (perr, spec.x_units_per_px()))
        ok = ok and abs(perr) < 8 * spec.x_units_per_px()
        # provisional per-quantity u_read (selftest-only)
        uv = max(abs(verr), spec.y_units_per_px()); up = max(abs(perr), spec.x_units_per_px())
        # 1 VALUE plants
        nv = _q_off(digitize(render_plate(spec, cf, 0.0), labels), valq, cf, 0.0)
        print("SELFTEST 1a VALUE null: offset=%.4g <= %.4g -> %s" % (nv, NULL_K * uv, abs(nv) <= NULL_K * uv)); ok = ok and abs(nv) <= NULL_K * uv
        dv = _q_off(digitize(render_plate(spec, cf, DETECT_MULT * uv), labels), valq, cf, 0.0)
        print("SELFTEST 1b VALUE detect: planted %.4g -> %.4g (>u=%.4g) -> %s" % (DETECT_MULT * uv, dv, uv, dv > uv)); ok = ok and dv > uv
        # 2 POSITION plants (x-displacement of the feature, NOT a y-offset)
        pf = nozzle_factory(spec)
        np_null = posq.measure(digitize(render_plate(spec, pf(1.10), 0.0), labels)) - 1.10
        print("SELFTEST 2a POSITION null: offset=%.4g <= %.4g -> %s" % (np_null, NULL_K * up, abs(np_null) <= NULL_K * up)); ok = ok and abs(np_null) <= NULL_K * up
        dxp = DETECT_MULT * up
        np_det = posq.measure(digitize(render_plate(spec, pf(1.10 + dxp), 0.0), labels)) - 1.10
        print("SELFTEST 2b POSITION detect: planted x-disp %.4g -> recovered %.4g (>u=%.4g) -> %s" % (dxp, np_det, up, np_det > up)); ok = ok and np_det > up
        # 3 AXIS negatives
        lspec = default_spec(x_log=True); larr = render_plate(lspec, nozzle_curve(lspec, 5.0), 0.0)
        log_caught = _neg_control_refuses(lambda: digitize(larr, {**labels_of(lspec), "x_log": False}))
        print("SELFTEST 3a AXIS log-as-linear refuses: %s" % log_caught); ok = ok and log_caught
        log_pos = not _neg_control_refuses(lambda: digitize(larr, labels_of(lspec)))
        print("SELFTEST 3b AXIS log declared-correctly passes: %s" % log_pos); ok = ok and log_pos
        flip_caught = _neg_control_refuses(lambda: digitize(arr, labels, {"force_pair_flip": True}))
        print("SELFTEST 3c AXIS planted-flip refuses (slope-sign, 28.4): %s" % flip_caught); ok = ok and flip_caught
        # 4 tick-count mismatch refuses
        mm = _neg_control_refuses(lambda: digitize(arr, {**labels, "x_ticks": labels["x_ticks"][:-1]}))
        print("SELFTEST 4 tick-count mismatch refuses: %s" % mm); ok = ok and mm
        # 5 two-readoff half-spread per quantity is real & finite
        hv, _, _ = two_readoff_halfspread(render_plate(spec, cf, 0.0), labels, valq, SEED0)
        hp, _, _ = two_readoff_halfspread(render_plate(spec, pf(1.10), 0.0), labels, posq, SEED0)
        print("SELFTEST 5 two-readoff half-spread: value=%.4g y-data, position=%.4g x-data" % (hv, hp))
        ok = ok and math.isfinite(hv) and math.isfinite(hp) and hv >= 0 and hp >= 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("SELFTEST: %s" % ("ALL PASS" if ok else "FAILURES ABOVE"))
    return 0 if ok else 1

def _q_off(read, quantity, cf, disp): return quantity.measure(read) - quantity.truth(cf, 0.0)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="DIGITIZER instrument calibration (charter 25/28).")
    ap.add_argument("--selftest", action="store_true", help="exercise every arm; no committed u_read")
    ap.add_argument("--calibrate", action="store_true", help="POST-FREEZE: derive committed per-quantity u_read (compute)")
    ap.add_argument("--out", default=None, help="dir to save rendered plates (calibrate)")
    ap.add_argument("--n", type=int, default=N_CAL, help="calibration plates (>=20)")
    args = ap.parse_args()
    if args.selftest: sys.exit(selftest())
    if args.calibrate:
        if args.n < 20: refuse("--calibrate needs n>=20 synthetic plates (25.3); got %d" % args.n)
        if args.out: os.makedirs(args.out, exist_ok=True)
        try:
            rep = calibrate(out_dir=args.out, n=args.n)
            sys.exit(0 if rep["verdict"] in ("PASS", "GATE FAIL") else 1)
        except SystemExit2: sys.exit(2)
    ap.print_help(); sys.exit(64)
