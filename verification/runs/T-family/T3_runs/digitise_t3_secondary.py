#!/usr/bin/env python3
"""
Digitise the SECONDARY referent for T3: Figure 9 of Smirnov, Abramov, Ivanov,
Smirnovsky, Yakubov (2016), J. Phys.: Conf. Ser. 745 032016, CC-BY 3.0, which
REPRODUCES the Vogel and Eaton (1985) skin-friction and Stanton-number
distributions as filled circles beside the authors' 2D and 3D RANS curves.

THIS IS NOT A PRIMARY.  The primary (Vogel and Eaton 1985, J. Heat Transfer
107, 922-929; Stanford report MD-44) is NOT OBTAINED.  The secondary states no
experimental uncertainty.  Nothing written by this script arms a band.

Everything below is read from the rendered page: the axis lines and tick
marks are FOUND in the bitmap and checked against the printed labels; the
symbol centroids are connected components of a morphological opening that
removes every stroke thinner than the symbol; the solid 2D RANS curves are
traced column by column.  No point is typed in by hand.
"""
import hashlib
import json
import os
import sys
import datetime

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = ("/tmp/claude-1000/-home-ubuntu/64b13819-ff95-4d4d-a50f-3720bab19084/"
           "scratchpad")
PDF = os.path.join(SCRATCH, "acq", "jpcs2016_745_032016.pdf")
PAGE_PNG = os.path.join(SCRATCH, "t3dig", "page6-6.png")      # pdftoppm -r 600
DPI = 600
PAGE = 6
CROP = (1450, 4520, 3560, 5900)       # (left, top, right, bottom) on the page
X_TICKS = [0, 5, 10, 15, 20]          # printed x/H labels, left to right
Y_TICKS = [0.004, 0.003, 0.002, 0.001, 0.0, -0.001, -0.002]   # top to bottom
DARK = 128
OUT_JSON = os.path.join(HERE, "T3_secondary_digitisation.json")
OUT_OVERLAY = os.path.join(HERE, "T3_secondary_digitisation_overlay.png")
OUT_REPLOT = os.path.join(HERE, "T3_secondary_digitisation_replot.png")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def runs_1d(mask):
    """(start, end) of every True run in a 1-D boolean array; end exclusive."""
    m = np.concatenate(([False], mask, [False]))
    d = np.diff(m.astype(int))
    return list(zip(np.where(d == 1)[0], np.where(d == -1)[0]))


def cluster_positions(pos, gap=4):
    """Group sorted integer positions that are within `gap` of each other."""
    pos = sorted(pos)
    out, cur = [], [pos[0]]
    for p in pos[1:]:
        if p - cur[-1] <= gap:
            cur.append(p)
        else:
            out.append(cur)
            cur = [p]
    out.append(cur)
    return [float(np.mean(c)) for c in out]


def find_axes(dark):
    """The y-axis is the LEFTMOST long dark column, the x-axis the LOWEST long
    dark row (the figure also carries a faint top frame line at the 0.004
    level and a right frame line, so 'longest' alone is not enough)."""
    H, W = dark.shape
    col_runs = {}
    for x in range(W):
        for a, b in runs_1d(dark[:, x]):
            if b - a > col_runs.get(x, (0, None))[0]:
                col_runs[x] = (b - a, (a, b))
    lmax = max(v[0] for v in col_runs.values())
    long_cols = sorted(x for x, v in col_runs.items() if v[0] >= 0.9 * lmax)
    best_col = long_cols[0]
    best_span = col_runs[best_col][1]
    row_runs = {}
    for y in range(H):
        for a, b in runs_1d(dark[y, :]):
            if b - a > row_runs.get(y, (0, None))[0]:
                row_runs[y] = (b - a, (a, b))
    lmax2 = max(v[0] for v in row_runs.values())
    long_rows = sorted(y for y, v in row_runs.items() if v[0] >= 0.9 * lmax2)
    best_row = long_rows[-1]
    best_span2 = row_runs[best_row][1]
    # the axis line may be several px wide: centre of the contiguous dark band
    xs = [x for x in range(best_col - 4, best_col + 5)
          if dark[best_span[0] + 5:best_span[1] - 5, x].mean() > 0.9]
    ys = [y for y in range(best_row - 4, best_row + 5)
          if dark[y, best_span2[0] + 5:best_span2[1] - 5].mean() > 0.9]
    return dict(yaxis_x=float(np.mean(xs)), yaxis_x_cols=xs,
                yaxis_rows=(int(best_span[0]), int(best_span[1])),
                xaxis_y=float(np.mean(ys)), xaxis_y_rows=ys,
                xaxis_cols=(int(best_span2[0]), int(best_span2[1])),
                long_columns=long_cols, long_rows=long_rows)


def find_ticks(dark, ax):
    """Ticks stick OUT of the frame: left of the y-axis, below the x-axis."""
    yx = int(round(ax["yaxis_x"]))
    xy = int(round(ax["xaxis_y"]))
    # y ticks: rows that are dark in the band 6..24 px left of the axis line
    band = dark[:, yx - 24: yx - 6]
    rows = np.where(band.mean(axis=1) > 0.8)[0]
    y_ticks_px = cluster_positions(rows)
    # x ticks: columns dark in the band 6..24 px below the axis line
    band = dark[xy + 6: xy + 24, :]
    cols = np.where(band.mean(axis=0) > 0.8)[0]
    x_ticks_px = cluster_positions(cols)
    return y_ticks_px, x_ticks_px


def linfit(px, val):
    """val = a*px + b by least squares; returns a, b, max residual in val."""
    A = np.vstack([px, np.ones(len(px))]).T
    (a, b), *_ = np.linalg.lstsq(A, np.asarray(val, float), rcond=None)
    resid = np.asarray(val) - (a * np.asarray(px) + b)
    return float(a), float(b), float(np.max(np.abs(resid)))


def overlay(crop, ax, y_ticks_px, x_ticks_px, exp_st, exp_cf, ambiguous,
            legend, tr_st, tr_cf, r_sym):
    """Detected points and traced polylines drawn on the cropped figure."""
    ov = crop.convert("RGB")
    dr = ImageDraw.Draw(ov)
    for t in y_ticks_px:
        dr.line([(ax["yaxis_x"] - 40, t), (ax["yaxis_x"] + 40, t)], fill=(0, 160, 0), width=2)
    for t in x_ticks_px:
        dr.line([(t, ax["xaxis_y"] - 40), (t, ax["xaxis_y"] + 40)], fill=(0, 160, 0), width=2)
    for d in exp_st:
        dr.ellipse([d["px"] - r_sym, d["py"] - r_sym, d["px"] + r_sym, d["py"] + r_sym],
                   outline=(255, 0, 0), width=3)
    for d in exp_cf:
        dr.ellipse([d["px"] - r_sym, d["py"] - r_sym, d["px"] + r_sym, d["py"] + r_sym],
                   outline=(0, 0, 255), width=3)
    for d in ambiguous:
        dr.rectangle([d["px"] - r_sym - 4, d["py"] - r_sym - 4, d["px"] + r_sym + 4, d["py"] + r_sym + 4],
                     outline=(255, 0, 255), width=3)
    for lg in legend:
        dr.rectangle([lg["px"] - r_sym - 6, lg["py"] - r_sym - 6,
                      lg["px"] + r_sym + 6, lg["py"] + r_sym + 6], outline=(255, 140, 0), width=3)
    for tr, colr in ((tr_st, (255, 0, 255)), (tr_cf, (0, 200, 200))):
        pts = [(x, y) for x, y, ok in tr]
        dr.line(pts, fill=colr, width=2)
    ov.save(OUT_OVERLAY)
    print("wrote", OUT_OVERLAY)


def main():
    if not os.path.isfile(PAGE_PNG):
        sys.exit(f"render first: pdftoppm -r {DPI} -f {PAGE} -l {PAGE} -png")
    page = Image.open(PAGE_PNG).convert("L")
    crop = page.crop(CROP)
    g = np.asarray(crop, dtype=np.uint8)
    dark = g < DARK
    H, W = dark.shape

    ax = find_axes(dark)
    y_ticks_px, x_ticks_px = find_ticks(dark, ax)
    # keep only ticks inside the axis spans (reject label strokes etc.)
    y_ticks_px = [t for t in y_ticks_px
                  if ax["yaxis_rows"][0] - 5 <= t <= ax["yaxis_rows"][1] + 5]
    x_ticks_px = [t for t in x_ticks_px
                  if ax["xaxis_cols"][0] - 5 <= t <= ax["xaxis_cols"][1] + 5]
    if len(y_ticks_px) != len(Y_TICKS) or len(x_ticks_px) != len(X_TICKS):
        sys.exit(f"tick count mismatch: found {len(y_ticks_px)} y ticks "
                 f"{y_ticks_px} and {len(x_ticks_px)} x ticks {x_ticks_px}")
    ay, by, ry = linfit(y_ticks_px, Y_TICKS)
    axx, bx, rx = linfit(x_ticks_px, X_TICKS)
    # spacing uniformity, as a check on the calibration
    dy = np.diff(y_ticks_px)
    dx = np.diff(x_ticks_px)
    print(f"y-axis at column {ax['yaxis_x']:.1f}, rows {ax['yaxis_rows']}")
    print(f"x-axis at row {ax['xaxis_y']:.1f}, cols {ax['xaxis_cols']}")
    print(f"y ticks px {np.round(y_ticks_px,1).tolist()} spacings "
          f"{np.round(dy,1).tolist()}  max resid {ry:.2e}")
    print(f"x ticks px {np.round(x_ticks_px,1).tolist()} spacings "
          f"{np.round(dx,1).tolist()}  max resid {rx:.2e}")
    # the axis lines themselves must sit at the first tick of each axis
    assert abs(ax["yaxis_x"] - x_ticks_px[0]) < 4, "y-axis not at x/H = 0"
    assert abs(ax["xaxis_y"] - y_ticks_px[-1]) < 4, "x-axis not at -0.002"

    def to_data(px, py):
        return axx * px + bx, ay * py + by

    def to_px(xh, v):
        return (xh - bx) / axx, (v - by) / ay

    # ---- plot interior ----------------------------------------------------
    # For SYMBOL detection only the label regions (left of the y-axis, below
    # the x-axis) are removed: the opening below deletes every thin stroke,
    # frame lines included, and a symbol touching the right frame line (the
    # x/H = 20 symbol does) must not be cut in half by a mask.
    x0 = int(round(ax["yaxis_x"])) + 4
    y1 = int(round(ax["xaxis_y"])) - 4
    interior = np.zeros_like(dark)
    interior[: y1, x0:] = True
    work = dark & interior
    # for CURVE tracing the top and right frame lines are removed as well
    interior_lines = interior.copy()
    interior_lines[: ax["yaxis_rows"][0] + 8, :] = False
    interior_lines[:, ax["xaxis_cols"][1] - 8:] = False

    # ---- filled circles: opening with a disk removes every thin stroke ------
    # First estimate the symbol size from the components of the RAW mask that
    # are roughly circular and isolated; then open with a disk a little smaller.
    lab, n = ndi.label(work)
    sizes = ndi.sum(work, lab, range(1, n + 1))
    sl = ndi.find_objects(lab)
    cand_r = []
    for i, s in enumerate(sl):
        h = s[0].stop - s[0].start
        w = s[1].stop - s[1].start
        if 10 <= h <= 60 and 10 <= w <= 60 and abs(h - w) <= 3:
            fill = sizes[i] / (np.pi * (0.5 * (h + w) / 2.0) ** 2)
            if 0.85 <= fill <= 1.15:
                cand_r.append(0.25 * (h + w))
    if len(cand_r) < 3:
        sys.exit("could not find isolated circular components for sizing")
    r_sym = float(np.median(cand_r))
    print(f"isolated circular components: {len(cand_r)}, median radius "
          f"{r_sym:.2f} px (range {min(cand_r):.1f}..{max(cand_r):.1f})")
    r_open = int(round(0.7 * r_sym))
    yy, xx = np.mgrid[-r_open:r_open + 1, -r_open:r_open + 1]
    disk = (xx ** 2 + yy ** 2) <= r_open ** 2
    opened = ndi.binary_opening(work, structure=disk)
    lab2, n2 = ndi.label(opened)
    cents = ndi.center_of_mass(opened, lab2, range(1, n2 + 1))
    areas = ndi.sum(opened, lab2, range(1, n2 + 1))
    blobs = []
    for (cy, cx), a in zip(cents, areas):
        # a filled circle of radius r_sym opened by r_open keeps ~ its full area
        if a < 0.5 * np.pi * r_sym ** 2 or a > 2.5 * np.pi * r_sym ** 2:
            continue
        # chord check on the RAW mask: the dark chord through the centre,
        # vertical and horizontal, must be about one symbol diameter
        iy, ix = int(round(cy)), int(round(cx))
        col = work[:, ix]
        row = work[iy, :]
        def chord(line, c):
            lo = c
            while lo > 0 and line[lo - 1]:
                lo -= 1
            hi = c
            while hi < len(line) - 1 and line[hi + 1]:
                hi += 1
            return hi - lo + 1
        cv, ch = chord(col, iy), chord(row, ix)
        # TWO OVERLAPPING SYMBOLS survive the opening as ONE component whose
        # horizontal extent exceeds a diameter.  Rule, stated: if the opened
        # component is wider than 1.5 diameters, it is split into two symbols
        # whose centres sit one radius in from its left and right edges, each
        # ordinate being the centre of the vertical dark chord at that column.
        comp = (lab2 == lab2[iy, ix])
        xs_c = np.where(comp.any(axis=0))[0]
        width = xs_c[-1] - xs_c[0] + 1
        if width > 1.5 * 2.0 * r_sym:
            for xc in (xs_c[0] + r_sym, xs_c[-1] - r_sym):
                xi = int(round(xc))
                rows_on = np.where(comp[:, xi])[0]
                yc = 0.5 * (rows_on[0] + rows_on[-1])
                blobs.append(dict(px=float(xc), py=float(yc), area=float(a) / 2.0,
                                  chord_v=int(chord(work[:, xi], int(round(yc)))),
                                  chord_h=int(width), radius_est=r_sym,
                                  split_from_merged_pair=True))
            continue
        blobs.append(dict(px=float(cx), py=float(cy), area=float(a),
                          chord_v=cv, chord_h=ch,
                          radius_est=0.5 * min(cv, ch)))
    print(f"blobs after opening (r_open={r_open}): {len(blobs)}")
    r_from_chords = float(np.median([b["radius_est"] for b in blobs]))
    print(f"symbol radius from chords: median {r_from_chords:.2f} px")

    # ---- trace the solid 2D RANS curves, circles masked out -----------------
    # remove the circles (dilated by 3 px) from the working mask
    circ = np.zeros_like(work)
    for b in blobs:
        yy2, xx2 = np.ogrid[:H, :W]
        circ |= (xx2 - b["px"]) ** 2 + (yy2 - b["py"]) ** 2 <= (r_sym + 3) ** 2
    lines = dark & interior_lines & ~circ

    def trace(y_start_data, lines, guide, corridor=120.0, max_thick=14,
              gap_pen=3.0, thick_pen=3.0, lookback=90, start_lock=25.0):
        """Global minimum-cost path through the dark runs, left to right.

        Every column contributes candidate nodes (centre of each dark run no
        thicker than max_thick px; the solid line is 3-4 px, the dotted 3D
        RANS line 5-6 px and gapped; where the two touch the merged run is
        about 10 px and is still a candidate, penalised).  A path pays |dy|
        for every step, gap_pen per skipped column that is NOT hidden behind
        a symbol, and thick_pen per px of run thickness above 4.  The
        cheapest path from the curve's ordinate at the y-axis (start_lock px
        either side) to the right edge is the continuous thin solid line.
        Candidates are further restricted to a CORRIDOR of +/- corridor px
        about a guide: the piecewise-linear interpolant through the detected
        experiment symbols of the same series (which the solid curve follows
        to within about 80 px everywhere), prepended with the curve's own
        ordinate at the y-axis.  The corridor makes the two traces distinct
        by construction.  Columns inside gaps are filled by linear
        interpolation between the flanking nodes."""
        x_end = int(round(to_px(20.0, 0)[0])) - 8
        xs_px = np.arange(x0, x_end)
        # a column costs nothing to skip when a symbol hides THIS curve there:
        # a circle within 45 px of the guide ordinate (symbols of the other
        # series, far from the guide, do not make the column free)
        paid_col = np.ones(W)
        for x in range(W):
            gy = int(round(guide(x)))
            if circ[max(0, gy - 45): gy + 46, x].any():
                paid_col[x] = 0.0
        P = np.concatenate(([0.0], np.cumsum(paid_col)))   # P[x] = sum paid_col[:x]
        nodes = []                       # (x, y, cost, parent_index, thick)
        y_s = to_px(0.0, y_start_data)[1]
        nodes.append((x0 - 1, y_s, 0.0, -1, 0))
        act_x, act_y, act_c, act_i = [x0 - 1], [y_s], [0.0], [0]
        for x in xs_px:
            gy = guide(x)
            cands = [(0.5 * (a + b - 1), b - a) for a, b in runs_1d(lines[:, x])
                     if b - a <= max_thick and abs(0.5 * (a + b - 1) - gy) <= corridor]
            if not cands:
                continue
            ax_ = np.asarray(act_x); ay_ = np.asarray(act_y); ac_ = np.asarray(act_c)
            keep = (x - ax_) <= lookback
            ax_, ay_, ac_ = ax_[keep], ay_[keep], ac_[keep]
            ai_ = [i for i, k in zip(act_i, keep) if k]
            is_start = np.asarray([i == 0 for i in ai_])
            gap = gap_pen * (P[x] - P[ax_ + 1])          # paid columns between
            new = []
            for yc, thick in cands:
                dy = np.abs(yc - ay_)
                cost = ac_ + dy + gap + thick_pen * max(0, thick - 4)
                cost = cost + np.where(is_start & (dy > start_lock), 1e9, 0.0)
                j = int(np.argmin(cost))
                nodes.append((int(x), float(yc), float(cost[j]), ai_[j], int(thick)))
                new.append(len(nodes) - 1)
            act_x = list(ax_) + [x] * len(new)
            act_y = list(ay_) + [nodes[k][1] for k in new]
            act_c = list(ac_) + [nodes[k][2] for k in new]
            act_i = ai_ + new
        last = [i for i, n in enumerate(nodes) if n[0] >= x_end - lookback]
        i = min(last, key=lambda k: nodes[k][2] + gap_pen * (P[x_end] - P[nodes[k][0] + 1]))
        path = []
        while i >= 0:
            path.append(nodes[i]); i = nodes[i][3]
        path = path[::-1][1:]                       # drop the synthetic start
        obs = {n[0]: n[1] for n in path}
        px_ = np.array([n[0] for n in path]); py_ = np.array([n[1] for n in path])
        out = []
        for x in xs_px:
            if x in obs:
                out.append((int(x), float(obs[x]), True))
            elif px_[0] <= x <= px_[-1]:
                out.append((int(x), float(np.interp(x, px_, py_)), False))
        return out

    # the St solid curve starts at the axis around 0.0005, the Cf one near 0
    # (read off the bitmap: dark runs in the first interior columns)
    first = lines[:, x0 + 2: x0 + 8].mean(axis=1) > 0.5
    starts = [ay * 0.5 * (a + b - 1) + by for a, b in runs_1d(first)]
    print(f"curve ordinates at the y-axis: {np.round(starts, 5).tolist()}")
    st_start = max(s for s in starts if 0.0002 < s < 0.0015)
    cf_start = min(starts, key=lambda s: abs(s))

    # PROVISIONAL series split for the corridor guides, by value alone: for
    # x/H >= 1.5 the St symbols exceed 0.002 and the Cf symbols stay below
    # 0.0019; for x/H < 1.5 the St symbols exceed 0.0008 and the Cf symbols
    # sit near 0.  (The final assignment below is by nearest traced curve.)
    def prov_is_st(b):
        xh, v = to_data(b["px"], b["py"])
        return v > (0.002 if xh >= 1.5 else 0.0008)
    def guide_from(pts, y_axis_data):
        pts = sorted(pts)
        gx = np.array([x0 - 1] + [p[0] for p in pts])
        gy = np.array([to_px(0.0, y_axis_data)[1]] + [p[1] for p in pts])
        return lambda x: float(np.interp(x, gx, gy))
    g_st = guide_from([(b["px"], b["py"]) for b in blobs if prov_is_st(b)
                       and not (to_data(b["px"], b["py"])[0] > 10 and
                                abs(to_data(b["px"], b["py"])[1]) < 0.0005)], st_start)
    g_cf = guide_from([(b["px"], b["py"]) for b in blobs if not prov_is_st(b)
                       and not (to_data(b["px"], b["py"])[0] > 10 and
                                abs(to_data(b["px"], b["py"])[1]) < 0.0005)], cf_start)
    tr_st = trace(st_start, lines, g_st)
    # the Cf curve is traced with the St path masked out (a band of 7 px)
    lines_cf = lines.copy()
    for x, y, _ in tr_st:
        lines_cf[max(0, int(y) - 7): int(y) + 8, x] = False
    tr_cf = trace(cf_start, lines_cf, g_cf)

    def polyline(tr, every=8):
        """Every `every`-th column of the trace (observed and interpolated),
        about 0.1 x/H apart."""
        pts = [(x, y) for x, y, ok in tr]
        pts = pts[::every] + ([pts[-1]] if (len(pts) - 1) % every else [])
        return [[round(to_data(x, y)[0], 4), round(to_data(x, y)[1], 6)]
                for x, y in pts]
    rans_st = polyline(tr_st)
    rans_cf = polyline(tr_cf)
    hit_st = sum(ok for _, _, ok in tr_st) / len(tr_st)
    hit_cf = sum(ok for _, _, ok in tr_cf) / len(tr_cf)
    print(f"trace St: {len(tr_st)} columns, {hit_st:.1%} with a thin run; "
          f"Cf: {len(tr_cf)} columns, {hit_cf:.1%}")

    # ---- assign symbols to series; exclude the legend symbol ---------------
    def curve_y_at(tr, xpx):
        i = int(round(xpx)) - tr[0][0]
        i = min(max(i, 0), len(tr) - 1)
        return tr[i][1]

    exp_st, exp_cf, legend, ambiguous = [], [], [], []
    for b in blobs:
        xh, v = to_data(b["px"], b["py"])
        # LEGEND EXCLUSION RULE, stated: the legend symbol sits beside the word
        # "Experiment" at x/H about 13 and ordinate about 0.  No data symbol
        # can be there: for x/H > 10 the Cf symbols exceed 0.001 and the St
        # symbols exceed 0.002 (the rule is checked on the overlay by eye).
        if xh > 10.0 and abs(v) < 0.0005:
            legend.append(dict(b, xH=xh, value=v))
            continue
        d_st = abs(b["py"] - curve_y_at(tr_st, b["px"]))
        d_cf = abs(b["py"] - curve_y_at(tr_cf, b["px"]))
        rec = dict(b, xH=float(xh), value=float(v),
                   dist_px_to_St_curve=float(d_st), dist_px_to_Cf_curve=float(d_cf))
        # AMBIGUITY RULE, stated: a symbol farther than 3 radii from BOTH solid
        # curves whose two distances are within a factor of 2 of each other
        # cannot be assigned by proximity and is listed separately, in neither
        # series.  (Everywhere the St and Cf symbols differ from their curves,
        # the other curve is several times farther away.)
        if min(d_st, d_cf) > 3.0 * r_sym and max(d_st, d_cf) < 2.0 * min(d_st, d_cf):
            ambiguous.append(rec)
            continue
        (exp_st if d_st < d_cf else exp_cf).append(rec)
    if len(legend) != 1:
        sys.exit(f"expected exactly one legend symbol, found {len(legend)}")
    exp_st.sort(key=lambda d: d["xH"])
    exp_cf.sort(key=lambda d: d["xH"])
    print(f"ambiguous symbols: {[(round(d['xH'],3), round(d['value'],6)) for d in ambiguous]}")
    print(f"St symbols {len(exp_st)}, Cf symbols {len(exp_cf)}, legend at "
          f"x/H={legend[0]['xH']:.2f} val={legend[0]['value']:.5f}")

    # digitisation increment: half-symbol width in data units
    inc_x = abs(axx) * r_sym
    inc_y = abs(ay) * r_sym

    # ---- derived quantities from the SYMBOLS ------------------------------
    st_xy = np.array([[d["xH"], d["value"]] for d in exp_st]).reshape(-1, 2)
    cf_xy = np.array([[d["xH"], d["value"]] for d in exp_cf]).reshape(-1, 2)
    if len(st_xy) < 3 or len(cf_xy) < 3:
        overlay(crop, ax, y_ticks_px, x_ticks_px, exp_st, exp_cf, ambiguous,
                legend, tr_st, tr_cf, r_sym)
        sys.exit("too few symbols assigned; see the overlay")
    ipk = int(np.argmax(st_xy[:, 1]))
    St_peak, x_peak = float(st_xy[ipk, 1]), float(st_xy[ipk, 0])

    def interp(xy, x):
        if x < xy[0, 0] or x > xy[-1, 0]:
            return None
        return float(np.interp(x, xy[:, 0], xy[:, 1]))
    # St at 20: the last symbol sits at x/H close to 20 -- if it is within the
    # x increment of 20, report it directly rather than extrapolating
    def st_at(x):
        v = interp(st_xy, x)
        if v is None and abs(x - st_xy[-1, 0]) <= inc_x:
            return float(st_xy[-1, 1]), "last symbol within one x-increment of the station"
        return v, "linear interpolation between neighbouring symbols"
    St10, how10 = st_at(10.0)
    St20, how20 = st_at(20.0)
    # reattachment: last negative-to-positive crossing of the Cf symbols
    cross = []
    for i in range(len(cf_xy) - 1):
        a, b = cf_xy[i], cf_xy[i + 1]
        if a[1] < 0.0 <= b[1]:
            cross.append(float(a[0] + (0.0 - a[1]) * (b[0] - a[0]) / (b[1] - a[1])))
    x_R = cross[-1] if cross else None
    # the x-uncertainty of a crossing also carries the ordinate increment
    # through the local slope
    if cross:
        i = max(i for i in range(len(cf_xy) - 1)
                if cf_xy[i, 1] < 0.0 <= cf_xy[i + 1, 1])
        slope_cf = (cf_xy[i + 1, 1] - cf_xy[i, 1]) / (cf_xy[i + 1, 0] - cf_xy[i, 0])
        inc_xR = float(np.hypot(inc_x, inc_y / slope_cf))
    else:
        inc_xR = None

    derived = dict(
        St_peak=dict(value=St_peak, increment=inc_y, x_peak_H=x_peak,
                     x_increment=inc_x,
                     note="maximum of the St symbols; x_peak_H is that symbol's abscissa"),
        St_10H=dict(value=St10, increment=inc_y, how=how10),
        St_20H=dict(value=St20, increment=inc_y, how=how20),
        x_R_H=dict(value=x_R, increment=inc_xR,
                   all_crossings=cross,
                   note="last negative-to-positive crossing of the Cf symbols, "
                        "linear between neighbours; increment combines the x "
                        "increment with the ordinate increment through the local slope"),
    )
    print("derived: " + json.dumps(derived, indent=1))

    out = dict(
        provenance=dict(
            paper="Smirnov E M, Abramov A G, Ivanov N G, Smirnovsky A A, "
                  "Yakubov S, 'Numerical simulation of heat transfer in a "
                  "turbulent flow over a backward-facing step' (title as "
                  "read from the PDF), 7th European Thermal-Sciences Conference "
                  "(Eurotherm 2016)",
            journal="J. Phys.: Conf. Ser. 745 (2016) 032016",
            doi="10.1088/1742-6596/745/3/032016",
            licence="CC-BY 3.0",
            figure="Figure 9: Comparison of the skin friction and Stanton "
                   "number experimental distributions with those calculated "
                   "with 2D and 3D RANS formulations",
            page=PAGE, pdf_sha256=sha256(PDF), render_dpi=DPI,
            crop_box_on_page_px=list(CROP),
            date="2026-08-21",
            status="SECONDARY, NOT A PRIMARY: a reproduction of Vogel and "
                   "Eaton 1985 data in an open paper; the primary is NOT "
                   "OBTAINED; no experimental uncertainty is stated in the "
                   "secondary; this file arms NO band",
            method="axis lines found as the longest dark column/row runs; "
                   "ticks found as dark runs protruding left of the y-axis "
                   "and below the x-axis, matched to the printed labels by "
                   "count and checked for uniform spacing; filled circles are "
                   "the connected components surviving a binary opening with "
                   "a disk of radius 0.7 symbol radii, sized by the dark "
                   "chords through each centroid on the raw mask; the solid "
                   "2D RANS curves are traced column by column preferring "
                   "thin runs (the 3D RANS curve is dotted and thicker); "
                   "symbols are assigned to the series whose solid curve is "
                   "nearer; the legend symbol (x/H > 10, |value| < 0.0005) is "
                   "excluded",
            script=os.path.basename(__file__),
        ),
        axis_calibration=dict(
            yaxis_px_column=ax["yaxis_x"], xaxis_px_row=ax["xaxis_y"],
            y_ticks=dict(labels=Y_TICKS, px_rows=y_ticks_px,
                         map="value = a*py + b", a=ay, b=by,
                         max_residual=ry, spacings_px=dy.tolist()),
            x_ticks=dict(labels=X_TICKS, px_cols=x_ticks_px,
                         map="x/H = a*px + b", a=axx, b=bx,
                         max_residual=rx, spacings_px=dx.tolist()),
            pixel_origin="top-left of the crop box",
        ),
        symbol=dict(radius_px_from_isolated_components=r_sym,
                    radius_px_from_chords=r_from_chords,
                    n_isolated_for_sizing=len(cand_r),
                    increment_xH=inc_x, increment_ordinate=inc_y,
                    note="increment = half symbol width in data units; the "
                         "digitisation resolution, NOT an experimental "
                         "uncertainty"),
        experiment_St=[[round(d["xH"], 4), round(d["value"], 6)] for d in exp_st],
        experiment_Cf=[[round(d["xH"], 4), round(d["value"], 6)] for d in exp_cf],
        experiment_St_px=[[round(d["px"], 1), round(d["py"], 1)] for d in exp_st],
        experiment_Cf_px=[[round(d["px"], 1), round(d["py"], 1)] for d in exp_cf],
        ambiguous_symbols_excluded=[dict(xH=round(d["xH"], 4), value=round(d["value"], 6),
                                         px=round(d["px"], 1), py=round(d["py"], 1),
                                         dist_px_to_St_curve=round(d["dist_px_to_St_curve"], 1),
                                         dist_px_to_Cf_curve=round(d["dist_px_to_Cf_curve"], 1))
                                    for d in ambiguous],
        ambiguity_rule="a symbol farther than 3 symbol radii from both solid curves with the two distances within a factor of 2 is assigned to neither series",
        split_rule="an opened component wider than 1.5 diameters is two overlapping symbols, centred one radius in from its edges",
        experiment_St_split_flags=[bool(d.get("split_from_merged_pair")) for d in exp_st],
        experiment_Cf_split_flags=[bool(d.get("split_from_merged_pair")) for d in exp_cf],
        legend_symbol_excluded=dict(px=legend[0]["px"], py=legend[0]["py"],
                                    xH=legend[0]["xH"], value=legend[0]["value"]),
        rans2d_St=rans_st, rans2d_Cf=rans_cf,
        rans2d_trace_hit_fraction=dict(St=hit_st, Cf=hit_cf),
        rans2d_trace_limitations="the traces are secondary information and are "
            "not graded; checked by eye on the overlay: for x/H < 1.3 the St "
            "trace follows the dotted 3D RANS line (within 40 px of the solid "
            "2D RANS bump at St about 0.0008 near x/H = 0.3) rather than the "
            "solid line; elsewhere both traces follow the solid lines to within "
            "the line thickness; columns hidden by a symbol are linearly "
            "interpolated",
        curve_start_ordinates_at_axis=starts,
        derived_from_experiment=derived,
    )
    with open(OUT_JSON, "w") as fh:
        json.dump(out, fh, indent=1)
    print("wrote", OUT_JSON)

    overlay(crop, ax, y_ticks_px, x_ticks_px, exp_st, exp_cf, ambiguous,
            legend, tr_st, tr_cf, r_sym)

    # ---- replot from the JSON alone ---------------------------------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    J = json.load(open(OUT_JSON))
    fig, axp = plt.subplots(figsize=(7, 4.5))
    s = np.array(J["experiment_St"]); c = np.array(J["experiment_Cf"])
    axp.plot(s[:, 0], s[:, 1], "o", color="tab:red", label="Experiment St (digitised)")
    axp.plot(c[:, 0], c[:, 1], "o", color="tab:blue", label="Experiment Cf (digitised)")
    rs = np.array(J["rans2d_St"]); rc = np.array(J["rans2d_Cf"])
    axp.plot(rs[:, 0], rs[:, 1], "-", color="k", label="2D RANS (traced)")
    axp.plot(rc[:, 0], rc[:, 1], "-", color="k")
    axp.set_xlim(0, 20); axp.set_ylim(-0.002, 0.004)
    axp.set_xticks(X_TICKS); axp.set_yticks(sorted(Y_TICKS))
    axp.set_xlabel("x/H"); axp.set_ylabel("St, Cf")
    axp.grid(True, alpha=0.3); axp.legend(loc="lower right", fontsize=8)
    axp.set_title("Replot from T3_secondary_digitisation.json only (SECONDARY; arms no band)",
                  fontsize=9)
    fig.tight_layout(); fig.savefig(OUT_REPLOT, dpi=150)
    print("wrote", OUT_REPLOT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
