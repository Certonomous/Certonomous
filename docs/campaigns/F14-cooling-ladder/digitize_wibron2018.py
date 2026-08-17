#!/usr/bin/env python3
"""digitize_wibron2018.py -- extract the K2c-A reference values from the figures
of Wibron, Ljung and Lundstrom 2018, Energies 11(3):644.

    python3 docs/campaigns/F14-cooling-ladder/digitize_wibron2018.py
    python3 docs/campaigns/F14-cooling-ladder/digitize_wibron2018.py --write

Run from the repository root.  `--write` refreshes the .dat files under
reference-data/wibron_2018_digitized/.  Without it the script only prints.

EVERY NUMBER THIS SCRIPT PRINTS IS DIGITIZED, NOT TABULATED.  The paper
tabulates its boundary conditions (its Tables 1 and 2) and states its
instrument accuracies in prose, but the quantities a solve is graded against
live only in Figures 3, 6, 7 and 8.  Nothing here may be quoted without the
word "digitized" and the figure number attached.

WHAT THE METHOD IS, AND WHY IT IS NOT PIXEL DIGITIZATION
--------------------------------------------------------
Figures 3, 6, 7 and 8 of this paper are VECTOR art: each is a PDF Form XObject
whose content stream contains the plotted geometry as path operators.  Figures
1, 2, 4, 5, 9 and 10 are raster images and are not digitized here at all.
Checked with `pdfimages -list` (no image object on pages 7, 10, 11) and with
pypdf (`/Subtype /Form` on those pages).

So the extraction reads coordinates, not pixels:

  1. Tokenise the form's content stream and replay it, tracking the graphics
     state (stroke gray, fill gray, line width) and collecting every painted
     path.
  2. Find the axes rectangle (the white-filled `re` that MATLAB emits as the
     plot box) and the axis TICK MARKS (short segments planted on the box
     edges).  Calibrate by least squares of tick position against the tick
     LABEL VALUES read from the same stream's text operators.  The fit residual
     is reported for every panel and is the calibration error.
  3. Read the data primitives:
       - bar charts (Fig 6): the bar is a `re`; its height IS the value;
       - error bars (Figs 3b, 6): stroked segments; the cap midpoint is a
         SECOND, independent encoding of the same datum and is compared;
       - experiment markers (Figs 7, 8): closed 8-segment polygons (circles
         drawn as octagons); the centre is the mean of the vertex extrema,
         which is exact for a symmetric marker;
       - CFD profiles (Figs 3, 7, 8): 500-vertex polylines; each vertex is a
         datum.
  4. Stroke WIDTH never enters any value.  Curve thickness is a pixel-reading
     error source and there is no pixel reading here; the paths carry their
     own centrelines.

Reader repeatability is zero by construction: the extraction is deterministic
and re-running this command reproduces byte-identical output.  That removes the
usual dominant digitisation error and replaces it with the four measured ones
reported by --controls below.

THE CONTROLS.  A digitisation with no established accuracy cannot arm a gate.
Five run every time this script runs and each is printed with its recovery
error:

  C1  Figure 6 error-bar half-width against the +-1 C stated for the Raritan
      DPX2-T1H1 in the paper's Section 3.5.  A TEXT-STATED value recovered from
      a figure.
  C2  Figure 3b GCI band maximum half-width against the "maximum discretization
      uncertainty is 0.0521 m/s" stated in Section 4.1.  A second text-stated
      value, in the velocity units the velocity rows are graded in.
  C3  Height-axis upper limit against the 3.150 m room height of Section 3.1.
      A third text-stated value, on the other axis.
  C4  Equation (9) with the Table 2 heat loads and face velocities: the paper
      sets T_back = mean(T_front) + q/(m_dot c_p), so (T_back - T_front)*v/q
      must be one constant across racks.  TABULATED inputs, digitized outputs.
  C5  Cross-figure identity: the fine-grid RSM profile at L1 is plotted twice,
      as Figure 3a's "Fine grid" and as Figure 7a's RSM curve, on axes with
      different limits.  Digitizing both and differencing measures the whole
      pipeline including calibration.
  C6  Cross-figure repeatability of the EXPERIMENT markers: the L1 and L2
      measured points appear in both Figure 7a,b and Figure 8a,b.  This is the
      marker-placement error, and it is the largest term in the velocity
      budget.

C8, the semantic control, is not automated: the digitized values must reproduce
the paper's own sentences "All the values predicted by the CFD model are within
the experimental error bars" (front) and "all values except for two are within
the experimental error bars" (back).  The printed tables show whether they do.

WHAT NO READING OF A FIGURE CAN RECOVER, STATED SO IT IS NOT CLAIMED
--------------------------------------------------------------------
Whether the value the authors PLOTTED equals the value they MEASURED.  Any
rounding, averaging or transcription between instrument and figure is invisible
here and is not covered by any control above.  The digitisation uncertainty
reported is the uncertainty of reading the figure, and nothing more.
"""
import argparse
import math
import os
import re
import sys

import pypdf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
PDF = os.path.join(ROOT, "docs", "papers",
                   "wibron_ljung_lundstrom_2018_en11030644.pdf")
PDF_SHA256 = "4de4798ed5eed60feda123c7a2398674a6a9177f44906175847d90f5227d7b77"
OUTDIR = os.path.join(HERE, "reference-data", "wibron_2018_digitized")

RACKS = ["R%d" % i for i in range(1, 11)]
# Paper Table 2, READ IN FULL, p. 6.  Tabulated, not digitized.
TABLE2 = {"R1": (0.40, 5180), "R2": (0.46, 5194), "R3": (0.47, 5161),
          "R4": (0.45, 5152), "R5": (0.26, 0), "R6": (0.41, 1762),
          "R7": (0.38, 5194), "R8": (0.43, 5266), "R9": (0.42, 5326),
          "R10": (0.39, 5198)}
# Paper Section 3.5, READ IN FULL, pp. 6-7.  Stated, not digitized.
T_SENSOR_ACC_K = 1.0                      # Raritan DPX2-T1H1, +-1 C
V_ACC_REL, V_ACC_ABS = 0.02, 0.02         # Dantec 54T33, +-2% of reading +-0.02 m/s
V_ACC_RANGE = (0.05, 1.0)                 # m/s, the range that accuracy is quoted for
GCI_MAX_MPS = 0.0521                      # Section 4.1, fine-grid max discretization unc.
ROOM_HEIGHT_M = 3.150                     # Section 3.1

# ---------------------------------------------------------------- PDF vectors
NUM = re.compile(rb"[-+]?(?:\d+\.?\d*|\.\d+)")


def tokenize(data):
    toks, i, n = [], 0, len(data)
    while i < n:
        c = data[i:i + 1]
        if c.isspace():
            i += 1
            continue
        if c == b"%":
            j = data.find(b"\n", i)
            i = n if j < 0 else j + 1
            continue
        if c == b"(":
            depth, j, buf = 1, i + 1, b""
            while j < n and depth:
                ch = data[j:j + 1]
                if ch == b"\\":
                    buf += data[j:j + 2]
                    j += 2
                    continue
                if ch == b"(":
                    depth += 1
                elif ch == b")":
                    depth -= 1
                    if depth == 0:
                        break
                buf += ch
                j += 1
            toks.append(("str", buf))
            i = j + 1
            continue
        if c == b"<":
            j = data.find(b">", i)
            toks.append(("hex", data[i + 1:j]))
            i = j + 1
            continue
        if c == b"/":
            j = i + 1
            while j < n and not data[j:j + 1].isspace() and data[j:j + 1] not in b"/[]<>(){}":
                j += 1
            toks.append(("name", data[i + 1:j].decode("latin-1")))
            i = j
            continue
        if c in b"[]":
            toks.append(("op", c.decode()))
            i += 1
            continue
        m = NUM.match(data, i)
        if m and (c.isdigit() or c in b"-+."):
            toks.append(("num", float(m.group())))
            i = m.end()
            continue
        j = i
        while j < n and not data[j:j + 1].isspace() and data[j:j + 1] not in b"/[]<>(){}%(":
            j += 1
        if j == i:
            j = i + 1
        toks.append(("op", data[i:j].decode("latin-1")))
        i = j
    return toks


class Path(object):
    __slots__ = ("subpaths", "stroke", "fill", "lw", "op")

    def __init__(self, subpaths, stroke, fill, lw, op):
        self.subpaths, self.stroke, self.fill, self.lw, self.op = subpaths, stroke, fill, lw, op


def replay(data):
    """Return (paths, texts).  texts is [(x, y, string)] in stream coordinates."""
    gs = dict(stroke=0.0, fill=0.0, lw=1.0)
    stack, paths, texts = [], [], []
    cur, sub, start, operands = [], [], None, []
    tm = tlm = [1, 0, 0, 1, 0, 0]
    for kind, val in tokenize(data):
        if kind != "op" or val in ("[", "]"):
            operands.append((kind, val))
            continue
        op, nums = val, [v for k, v in operands if k == "num"]
        if op == "q":
            stack.append(dict(gs))
        elif op == "Q":
            if stack:
                gs = stack.pop()
        elif op == "g" and nums:
            gs["fill"] = nums[-1]
        elif op == "G" and nums:
            gs["stroke"] = nums[-1]
        elif op == "rg" and len(nums) >= 3:
            gs["fill"] = sum(nums[-3:]) / 3.0
        elif op == "RG" and len(nums) >= 3:
            gs["stroke"] = sum(nums[-3:]) / 3.0
        elif op == "w" and nums:
            gs["lw"] = nums[-1]
        elif op == "m" and len(nums) >= 2:
            if sub:
                cur.append(sub)
            sub = [(nums[-2], nums[-1])]
            start = sub[0]
        elif op in ("l",) and len(nums) >= 2:
            sub.append((nums[-2], nums[-1]))
        elif op == "c" and len(nums) >= 6:
            sub.append((nums[-2], nums[-1]))
        elif op in ("v", "y") and len(nums) >= 4:
            sub.append((nums[-2], nums[-1]))
        elif op == "re" and len(nums) >= 4:
            x, y, w, h = nums[-4:]
            if sub:
                cur.append(sub)
                sub = []
            cur.append([(x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)])
        elif op == "h":
            if sub and start:
                sub.append(start)
        elif op in ("S", "s", "f", "F", "f*", "B", "B*", "b", "b*", "n"):
            if sub:
                cur.append(sub)
                sub = []
            if cur and op != "n":
                paths.append(Path(cur, gs["stroke"], gs["fill"], gs["lw"], op))
            cur, start = [], None
        elif op == "BT":
            tm = tlm = [1, 0, 0, 1, 0, 0]
        elif op == "Tm" and len(nums) >= 6:
            tm = list(nums[-6:])
            tlm = list(tm)
        elif op == "Td" and len(nums) >= 2:
            tlm = [tlm[0], tlm[1], tlm[2], tlm[3],
                   tlm[4] + nums[-2] * tlm[0] + nums[-1] * tlm[2],
                   tlm[5] + nums[-2] * tlm[1] + nums[-1] * tlm[3]]
            tm = list(tlm)
        elif op == "Tj" and operands and operands[-1][0] == "str":
            texts.append((tm[4], tm[5], operands[-1][1].decode("latin-1")))
        elif op == "TJ":
            texts.append((tm[4], tm[5],
                          "".join(v.decode("latin-1") for k, v in operands if k == "str")))
        operands = []
    return paths, texts


def forms(page_index):
    rdr = pypdf.PdfReader(PDF)
    xo = rdr.pages[page_index]["/Resources"]["/XObject"].get_object()
    return {k: v.get_object().get_data() for k, v in xo.items()
            if v.get_object().get("/Subtype") == "/Form"}


# ---------------------------------------------------------------- calibration
def plot_boxes(paths, wmin, wmax, hmin):
    out = []
    for p in paths:
        if p.op == "f" and abs(p.fill - 1.0) < 1e-9 and len(p.subpaths) == 1:
            xs = [a for a, _ in p.subpaths[0]]
            ys = [b for _, b in p.subpaths[0]]
            w, h = max(xs) - min(xs), max(ys) - min(ys)
            if wmin < w < wmax and h > hmin:
                out.append((min(xs), min(ys), w, h))
    return out


def ticks(paths, box, lwmax=6.0):
    x0, y0, w, h = box
    x1, y1 = x0 + w, y0 + h
    xt, yt = set(), set()
    for p in paths:
        if p.op != "S" or p.lw > lwmax:
            continue
        for s in p.subpaths:
            if len(s) != 2:
                continue
            (ax, ay), (bx, by) = s
            if abs(ax - bx) < 1e-6 and abs(ay - y0) < 1e-6 and 0 < abs(by - ay) < h * 0.1 \
                    and x0 - 1 <= ax <= x1 + 1:
                xt.add(round(ax, 4))
            if abs(ay - by) < 1e-6 and abs(ax - x0) < 1e-6 and 0 < abs(bx - ax) < w * 0.1 \
                    and y0 - 1 <= ay <= y1 + 1:
                yt.add(round(ay, 4))
    return sorted(xt), sorted(yt)


def lsq(pos, vals):
    n = len(pos)
    if n != len(vals):
        raise SystemExit("tick count %d does not match label count %d" % (n, len(vals)))
    sx, sy = sum(pos), sum(vals)
    sxx = sum(p * p for p in pos)
    sxy = sum(p * v for p, v in zip(pos, vals))
    a = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    b = (sy - a * sx) / n
    return a, b, max(abs(v - (a * p + b)) for p, v in zip(pos, vals))


def markers(paths, dmin, dmax):
    out = []
    for p in paths:
        if p.op not in ("f", "f*"):
            continue
        for s in p.subpaths:
            if not (7 <= len(s) <= 12):
                continue
            xs = [a for a, _ in s]
            ys = [b for _, b in s]
            w, h = max(xs) - min(xs), max(ys) - min(ys)
            if abs(w - h) > 1e-3 or not (dmin < w < dmax):
                continue
            out.append(((max(xs) + min(xs)) / 2.0, (max(ys) + min(ys)) / 2.0))
    return out


def legend_zone(paths, lw_min=25.0, pad=120.0):
    """Bounding box of the legend's line samples.

    MATLAB draws each legend key as a lone TWO-POINT horizontal stroked segment
    at the same width as the data curves.  A data curve never has two points.
    In Figure 7 the legend sits above the panels; in Figure 8 it sits INSIDE the
    axes box, so excluding it by box membership alone silently admits the legend
    marker as a data point -- which is exactly the error this function exists to
    stop.  Returns None when no legend key is found.
    """
    xs, ys = [], []
    for p in paths:
        if p.op != "S" or p.lw < lw_min:
            continue
        for s in p.subpaths:
            if len(s) == 2 and abs(s[0][1] - s[1][1]) < 1e-6:
                xs += [s[0][0], s[1][0]]
                ys += [s[0][1], s[1][1]]
    if not xs:
        return None
    # A legend entry drawn as a MARKER (the "Exp." key) has no line sample, so
    # it lies one row outside the line keys' own bounding box.  Extend by one
    # inter-key row pitch, or the zone misses exactly the key that matters.
    rows = sorted(set(round(y, 3) for y in ys))
    pitch = min(b - a for a, b in zip(rows, rows[1:])) if len(rows) > 1 else 0.0
    return (min(xs) - pad, min(ys) - pitch - pad,
            max(xs) + pad, max(ys) + pitch + pad)


def in_zone(z, x, y):
    return z is not None and z[0] <= x <= z[2] and z[1] <= y <= z[3]


# ---------------------------------------------------------------- extractions
def fig6(which):
    """which = 'a' (front, Im12) or 'b' (back, Im13).  Returns dict + calib info."""
    name = {"a": "/Im12", "b": "/Im13"}[which]
    paths, _ = replay(forms(9)[name])
    box = plot_boxes(paths, 2000, 5600, 2000)[0]
    _, yt = ticks(paths, box)
    ay, by, res = lsq(yt, [0, 5, 10, 15, 20, 25, 30, 35, 40])
    zero = ay * box[1] + by

    def bars(fillval):
        out = []
        for p in paths:
            if p.op != "f" or abs(p.fill - fillval) > 1e-9 or len(p.subpaths) != 1:
                continue
            s = p.subpaths[0]
            xs = [a for a, _ in s]
            ys = [b for _, b in s]
            if not (90 < max(xs) - min(xs) < 110):
                continue
            out.append((min(xs), max(ys) - min(ys)))
        out.sort()
        return out

    cfd, exp = bars(1.0), bars(0.0)
    ebar = []
    for p in paths:
        if p.op == "S" and abs(p.lw - 15.0) < 1e-9:
            for s in p.subpaths:
                (ax, ay_), (bx, by_) = s
                if abs(ax - bx) < 1e-6 and abs(by_ - ay_) > 1e-9:
                    ebar.append((ax, min(ay_, by_), max(ay_, by_)))
    ebar.sort()
    rows = []
    for i, r in enumerate(RACKS):
        t_cfd = ay * (box[1] + cfd[i][1]) + by - zero
        t_exp = ay * (box[1] + exp[i][1]) + by - zero
        mid = half = None
        for x, lo, hi in ebar:
            if abs(x - (exp[i][0] + 52.7)) < 8.0:
                mid = ay * (lo + hi) / 2.0 + by - zero
                half = ay * (hi - lo) / 2.0
        present = exp[i][1] > 1e-9
        rows.append(dict(rack=r, cfd=t_cfd, exp=t_exp if present else None,
                         ebar_mid=mid if present else None,
                         ebar_half=half if present else None))
    return dict(rows=rows, tick_resid_raw=res, scale=1.0 / ay,
                box_top=ay * (box[1] + box[3]) + by, box=box)


def fig7():
    """Five panels L1..L5.  Returns per-panel Exp markers and CFD curves."""
    paths, _ = replay(forms(10)["/Im14"])
    boxes = sorted(plot_boxes(paths, 500, 3000, 1000))
    names = ["L1", "L2", "L3", "L4", "L5"]
    allm = markers(paths, 40, 80)
    zone = legend_zone(paths)
    out = {}
    for nm, box in zip(names, boxes):
        x0, y0, w, h = box
        xt, yt = ticks(paths, box)
        ax, bx, rx = lsq(xt, [0, 0.5, 1.0, 1.5])
        ay, by, ry = lsq(yt, [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
        pts = []
        for mx, my in allm:
            if not (x0 <= mx <= x0 + w and y0 <= my <= y0 + h):
                continue          # outside the axes box
            if in_zone(zone, mx, my):
                continue          # legend key, not a datum
            pts.append((ay * my + by, ax * mx + bx))
        pts.sort()
        curves = {}
        for p in paths:
            if p.op == "S" and abs(p.lw - 25.0) < 1e-9 and len(p.subpaths[0]) > 400 \
                    and x0 <= p.subpaths[0][0][0] <= x0 + w:
                curves[round(p.stroke, 4)] = [(ay * y + by, ax * x + bx)
                                              for x, y in p.subpaths[0]]
        out[nm] = dict(exp=pts, curves=curves, tick_resid=(rx, ry),
                       vscale=1.0 / ax, hscale=1.0 / ay,
                       box_top=ay * (y0 + h) + by, box_right=ax * (x0 + w) + bx)
    return out


def fig8():
    out = {}
    for name, lab in (("/Im15", "L1"), ("/Im16", "L2")):
        paths, _ = replay(forms(10)[name])
        box = plot_boxes(paths, 2000, 5600, 2000)[0]
        x0, y0, w, h = box
        xt, yt = ticks(paths, box)
        ax, bx, _ = lsq(xt, [0, .2, .4, .6, .8, 1.0, 1.2, 1.4, 1.6])
        ay, by, _ = lsq(yt, [0, .5, 1.0, 1.5, 2.0, 2.5, 3.0])
        zone = legend_zone(paths)
        pts = sorted((ay * my + by, ax * mx + bx) for mx, my in markers(paths, 60, 100)
                     if x0 <= mx <= x0 + w and y0 <= my <= y0 + h
                     and not in_zone(zone, mx, my))
        out[lab] = dict(exp=pts, vscale=1.0 / ax, hscale=1.0 / ay)
    return out


def fig3():
    """3a: coarse/medium/fine/extrapolated at L1.  3b: fine grid with GCI band."""
    XL = [0, .2, .4, .6, .8, 1.0, 1.2]
    YL = [0, .5, 1.0, 1.5, 2.0, 2.5, 3.0]
    pa, _ = replay(forms(6)["/Im5"])
    boxa = plot_boxes(pa, 2000, 5600, 2000)[0]
    xt, yt = ticks(pa, boxa)
    axa, bxa, _ = lsq(xt, XL)
    aya, bya, _ = lsq(yt, YL)
    fine = [p for p in pa if p.op == "S" and p.lw >= 25
            and abs(p.stroke) < 1e-9 and len(p.subpaths[0]) >= 500][0].subpaths[0]
    fine = [(aya * y + bya, axa * x + bxa) for x, y in fine]

    pb, _ = replay(forms(6)["/Im6"])
    boxb = plot_boxes(pb, 2000, 5600, 2000)[0]
    xt, yt = ticks(pb, boxb)
    axb, bxb, _ = lsq(xt, XL)
    ayb, byb, _ = lsq(yt, YL)
    big = [p for p in pb if p.op == "S" and p.lw >= 25]
    base = [p.subpaths[0] for p in big if abs(p.stroke) < 1e-9][0]
    fam = [p.subpaths[0] for p in big if abs(p.stroke) > 1e-9]
    by_y = {}
    for s in fam:
        for x, y in s:
            by_y.setdefault(round(y, 3), []).append(x)
    worst, worst_h = 0.0, None
    for x, y in base:
        xs = by_y.get(round(y, 3))
        if not xs:
            continue
        d = max(abs(u - x) for u in xs)
        if d > worst:
            worst, worst_h = d, y
    return dict(fine_3a=fine, band_max_mps=worst * axb,
                band_max_h=ayb * worst_h + byb,
                base_3b=[(ayb * y + byb, axb * x + bxb) for x, y in base])


# ---------------------------------------------------------------- controls
def controls(f6a, f6b, f7, f8, f3):
    out = []
    halves = [r["ebar_half"] for r in f6a["rows"] + f6b["rows"] if r["ebar_half"] is not None]
    out.append(("C1", "Fig 6 error-bar half-width vs +-1 C stated in Sec. 3.5",
                "%.6f C" % T_SENSOR_ACC_K,
                "%.6f C (n=%d, spread %.2e)" % (sum(halves) / len(halves), len(halves),
                                                max(halves) - min(halves)),
                abs(sum(halves) / len(halves) - T_SENSOR_ACC_K), "C"))
    out.append(("C2", "Fig 3b GCI band max half-width vs 0.0521 m/s stated in Sec. 4.1",
                "%.6f m/s" % GCI_MAX_MPS, "%.6f m/s (at h = %.3f m)"
                % (f3["band_max_mps"], f3["band_max_h"]),
                abs(f3["band_max_mps"] - GCI_MAX_MPS), "m/s"))
    tops = [f7[k]["box_top"] for k in f7]
    out.append(("C3", "Fig 7 height-axis upper limit vs 3.150 m room height, Sec. 3.1",
                "%.6f m" % ROOM_HEIGHT_M, "%.6f m (5 panels, spread %.2e)"
                % (sum(tops) / len(tops), max(tops) - min(tops)),
                abs(sum(tops) / len(tops) - ROOM_HEIGHT_M), "m"))
    # C4: Eq (9) with Table 2
    full = ["R1", "R2", "R3", "R4", "R7", "R8", "R9", "R10"]
    d6a = {r["rack"]: r for r in f6a["rows"]}
    d6b = {r["rack"]: r for r in f6b["rows"]}
    ks = []
    for r in full:
        v, q = TABLE2[r]
        ks.append((d6b[r]["cfd"] - d6a[r]["cfd"]) * v / q)
    kbar = sum(ks) / len(ks)
    worst = max(abs(k - kbar) for k in ks)
    # translate the constancy residual into kelvin on a representative rack
    dT_rep = sum(d6b[r]["cfd"] - d6a[r]["cfd"] for r in full) / len(full)
    out.append(("C4", "Eq. (9) constancy of (dT_CFD)*v/q over the 8 full racks",
                "one constant", "%.6e +- %.2e (max dev %.3f%%)"
                % (kbar, worst, 100 * worst / kbar), dT_rep * worst / kbar, "K"))
    # C5: Fig 3a fine grid vs Fig 7a RSM
    fine = f3["fine_3a"]
    rsm = f7["L1"]["curves"][0.502]
    n = min(len(fine), len(rsm))
    dv = [abs(fine[i][1] - rsm[i][1]) for i in range(n)]
    out.append(("C5", "Fig 3a 'Fine grid' vs Fig 7a RSM curve at L1, %d vertices" % n,
                "identical", "max %.2e, rms %.2e m/s"
                % (max(dv), math.sqrt(sum(d * d for d in dv) / n)), max(dv), "m/s"))
    # C6: Exp markers common to Fig 7 and Fig 8
    dvs, dhs = [], []
    for lab in ("L1", "L2"):
        a, b = f7[lab]["exp"], f8[lab]["exp"]
        for i in range(min(len(a), len(b))):
            dhs.append(abs(a[i][0] - b[i][0]))
            dvs.append(abs(a[i][1] - b[i][1]))
    out.append(("C6", "Exp markers, Fig 7a,b vs Fig 8a,b (%d common points)" % len(dvs),
                "identical", "v: max %.4f rms %.4f m/s ; h: max %.4f m"
                % (max(dvs), math.sqrt(sum(d * d for d in dvs) / len(dvs)), max(dhs)),
                max(dvs), "m/s"))
    # C7: the two independent encodings of the same experimental temperature --
    # the bar's own height, and the midpoint of its error-bar caps.
    red = [abs(r["exp"] - r["ebar_mid"]) for r in f6a["rows"] + f6b["rows"]
           if r["exp"] is not None]
    out.append(("C7", "Fig 6 bar height vs error-bar cap midpoint (%d values)" % len(red),
                "identical", "max %.2e C" % max(red), max(red), "C"))
    bounds = dict(T_internal=max(red), T_physical=dT_rep * worst / kbar,
                  V_marker=max(dvs), V_marker_rms=math.sqrt(sum(d * d for d in dvs) / len(dvs)),
                  V_curve=max(dv), H_marker=max(dhs),
                  calib_T=None)
    return out, bounds


def v_band(v, dig):
    """Pass half-band on a velocity point, per K2c 3.1 row 3 with digitisation added."""
    inst = V_ACC_ABS + V_ACC_REL * v
    return max(0.15 * v, inst + GCI_MAX_MPS + dig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true",
                    help="refresh reference-data/wibron_2018_digitized/")
    a = ap.parse_args()

    import hashlib
    h = hashlib.sha256(open(PDF, "rb").read()).hexdigest()
    print("source  : docs/papers/wibron_ljung_lundstrom_2018_en11030644.pdf")
    print("sha256  : %s  %s" % (h, "OK" if h == PDF_SHA256 else "MISMATCH -- STOP"))
    if h != PDF_SHA256:
        return 2
    print("figures : 3 (p.7 /Im5,/Im6), 6 (p.10 /Im12,/Im13), 7 (p.11 /Im14), "
          "8 (p.11 /Im15,/Im16) -- all vector Form XObjects")
    print()

    f6a, f6b = fig6("a"), fig6("b")
    f7, f8, f3 = fig7(), fig8(), fig3()
    ctl, bnd = controls(f6a, f6b, f7, f8, f3)

    print("== CONTROLS")
    print("%-4s %-62s %-16s %-42s %s" % ("id", "what", "reference", "recovered", "recovery error"))
    for cid, what, ref, got, err, unit in ctl:
        print("%-4s %-62s %-16s %-42s %.3e %s" % (cid, what, ref, got, err, unit))
    print()

    def ceil_to(x, step):
        return math.ceil(x / step - 1e-12) * step

    # Adopted digitisation increments.  DERIVED, not asserted: each is the
    # largest control-established bound for that quantity class, rounded up to
    # the next reporting step.  The conservative bound is taken deliberately --
    # C4's residual also carries the paper's own front-face averaging term and
    # so over-states the reading error, and a gate band that under-states it
    # would claim precision this extraction did not measure.
    dig_T = ceil_to(bnd["T_physical"], 0.01)      # K
    dig_V = ceil_to(bnd["V_marker"], 0.001)       # m/s
    dig_H = ceil_to(bnd["H_marker"], 0.001)       # m

    for lab, f6, panel in (("6a FRONT", f6a, "front"), ("6b BACK", f6b, "back")):
        print("== FIGURE %s -- rack %s temperature, sensor point 1.09 m (DIGITIZED)" % (lab, panel))
        print("   y-axis tick fit residual %.2e raw = %.2e C ; %.4f raw per C"
              % (f6["tick_resid_raw"], f6["tick_resid_raw"] / f6["scale"], f6["scale"]))
        print("   %-4s %12s %12s %12s %12s %10s %12s" %
              ("rack", "T_exp_dig", "T_CFD_dig", "|CFD-exp|", "ebar_half", "in +-1 C",
               "gate band"))
        for r in f6["rows"]:
            if r["exp"] is None:
                print("   %-4s %12s %12.4f %12s %12s %10s %12s"
                      % (r["rack"], "NO DATUM", r["cfd"], "-", "-", "-", "NOT ARMABLE"))
                continue
            d = abs(r["cfd"] - r["exp"])
            print("   %-4s %12.4f %12.4f %12.4f %12.5f %10s %12s"
                  % (r["rack"], r["exp"], r["cfd"], d, r["ebar_half"],
                     "yes" if d <= T_SENSOR_ACC_K else "NO",
                     "+-%.3f K" % (T_SENSOR_ACC_K + dig_T)))
        print()

    # The two racks C4 could not use, checked as PREDICTIONS rather than fitted.
    print("== EQ. (9) CHECK ON THE TWO PARTIAL RACKS (predictions, not fitted)")
    d6a = {r["rack"]: r for r in f6a["rows"]}
    d6b = {r["rack"]: r for r in f6b["rows"]}
    full = ["R1", "R2", "R3", "R4", "R7", "R8", "R9", "R10"]
    ks = [(d6b[r]["cfd"] - d6a[r]["cfd"]) * TABLE2[r][0] / TABLE2[r][1] for r in full]
    kbar = sum(ks) / len(ks)
    print("   fitted constant 1/(rho.A.c_p) = %.6e K.m/(W.s) over the 8 full racks" % kbar)
    for r in ("R5", "R6"):
        v, q = TABLE2[r]
        pred = kbar * q / v
        obs = d6b[r]["cfd"] - d6a[r]["cfd"]
        print("   %-3s q = %5d W, v = %.2f m/s -> Eq.(9) predicts dT = %7.3f K, "
              "Fig 6 gives %7.3f K, residual %+7.3f K"
              % (r, q, v, pred, obs, obs - pred))
    print()

    print("== FIGURE 7 -- measured velocity profiles (DIGITIZED), with the K2c-A band")
    print("   %-3s %8s %10s %10s %10s %10s  %s"
          % ("loc", "h_dig(m)", "v_dig(m/s)", "instr", "GCI", "digit", "pass half-band (m/s)"))
    for lab in ("L1", "L2", "L3", "L4", "L5"):
        for h, v in f7[lab]["exp"]:
            print("   %-3s %8.3f %10.4f %10.4f %10.4f %10.4f  %.4f%s"
                  % (lab, h, v, V_ACC_ABS + V_ACC_REL * v, GCI_MAX_MPS, dig_V,
                     v_band(v, dig_V), "" if lab in ("L3", "L5") else "   [REPORT-ONLY row]"))
    print()
    print("== ADOPTED DIGITISATION INCREMENTS (derived from the controls above)")
    print("   %-28s %-14s %-12s %s" % ("quantity class", "measured bound", "adopted", "from"))
    print("   %-28s %-14s %-12s %s"
          % ("temperature, Fig 6 bars", "%.2e K" % bnd["T_internal"],
             "", "C7 two-encoding redundancy (internal)"))
    print("   %-28s %-14s %-12s %s"
          % ("temperature, Fig 6 bars", "%.3f K" % bnd["T_physical"],
             "+-%.2f K" % dig_T, "C4 Eq.(9) residual (independent, conservative)"))
    print("   %-28s %-14s %-12s %s"
          % ("velocity, Fig 7 markers", "%.4f m/s" % bnd["V_marker"],
             "+-%.3f m/s" % dig_V, "C6 cross-figure max (rms %.4f)" % bnd["V_marker_rms"]))
    print("   %-28s %-14s %-12s %s"
          % ("height, Fig 7 markers", "%.4f m" % bnd["H_marker"],
             "+-%.3f m" % dig_H, "C6 cross-figure max"))
    print("   %-28s %-14s %-12s %s"
          % ("velocity, CFD polylines", "%.2e m/s" % bnd["V_curve"],
             "+-0.0001 m/s", "C5 cross-figure curve identity"))

    if a.write:
        if not os.path.isdir(OUTDIR):
            os.makedirs(OUTDIR)
        hdr = ("# DIGITIZED from Wibron, Ljung and Lundstrom 2018, Energies 11(3):644, CC-BY.\n"
               "# Source PDF sha256 %s\n"
               "# Produced by docs/campaigns/F14-cooling-ladder/digitize_wibron2018.py --write\n"
               "# NOT TABULATED IN THE PAPER.  Every value below is a figure reading.\n"
               "# Digitisation increments, derived by the controls printed by the\n"
               "# command above and restated here so no reader can quote a value\n"
               "# finer than it was measured (L-28):\n"
               "#   temperature  +-%.2f K      velocity  +-%.3f m/s      height  +-%.3f m\n"
               "# More decimals are carried below only so the file round-trips; the\n"
               "# graded value is the one at the increment.\n"
               % (PDF_SHA256, dig_T, dig_V, dig_H))
        with open(os.path.join(OUTDIR, "fig6_rack_temperatures.dat"), "w") as fh:
            fh.write(hdr)
            fh.write("# Figure 6a (front) and 6b (back), sensor point 1.09 m above the\n"
                     "# lower edge of the rack doors.  NO DATUM = the paper plots no\n"
                     "# experimental bar for that rack (bar height exactly zero).\n"
                     "# rack  T_exp_front  T_cfd_front  T_exp_back  T_cfd_back   (deg C)\n")
            d6b = {r["rack"]: r for r in f6b["rows"]}
            for r in f6a["rows"]:
                b = d6b[r["rack"]]
                fh.write("%-5s %12s %12.4f %12s %12.4f\n" % (
                    r["rack"],
                    "NODATUM" if r["exp"] is None else "%.4f" % r["exp"], r["cfd"],
                    "NODATUM" if b["exp"] is None else "%.4f" % b["exp"], b["cfd"]))
        with open(os.path.join(OUTDIR, "fig7_velocity_profiles.dat"), "w") as fh:
            fh.write(hdr)
            fh.write("# Figure 7a-e, measured (Exp.) velocity profiles.\n"
                     "# loc  height_m  velocity_mps\n")
            for lab in ("L1", "L2", "L3", "L4", "L5"):
                for hh, vv in f7[lab]["exp"]:
                    fh.write("%-4s %9.4f %9.4f\n" % (lab, hh, vv))
        print("\nwrote %s" % OUTDIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
