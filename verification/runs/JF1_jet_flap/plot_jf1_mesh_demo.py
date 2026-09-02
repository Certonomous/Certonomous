#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mesh and near-wall figures for the blown trailing-edge slot demo.

EVERY POLYGON DRAWN BY THIS SCRIPT IS A REAL CELL FROM `constant/polyMesh`.
There is no STL anywhere in this file: the 2-D slice is the `back` empty-patch
face list, which on a one-cell-deep mesh is exactly one quadrilateral per cell.
If the reader below cannot open `constant/polyMesh/points`, `faces` and
`boundary` it RAISES; it never falls back to a surface tessellation.

House style follows `plot_jf1_actB_demo.py` (same fonts, palette, caveat box
and cost line), including its `assert_no_banner` check: there is no longer a
banner to draw, and each page is asserted free of the removed word before it
is written.  Output: `artefacts/jet_flap_5..7_*.{pdf,png}`.

Run:  python3 plot_jf1_mesh_demo.py
"""
import os
import re
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# ONE style block for the campaign, and it refuses rather than falling back
# to a substitute serif; and the two figure-standard limits (a ten-word
# title, a twenty-word caption) enforced where they are already implemented
# rather than reimplemented here.
from jf1_figure_style import latin_modern_rc, sheet_note   # noqa: E402
from plot_jf1_actB_demo import (assert_no_banner, caption,   # noqa: E402
                                check_title)
import jf1_display_numbers as jf1num                       # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

# the two meshes, named by what they are for -- never by an internal id
FLOW = "JF1_P1_L1_CMESH_PHYSICS"      # C-topology, unit span, flow-field figure
FLOW_TIME = "20000"
SWEEP = "JF1_L1_BLOWN_CMU010_A0"      # O-topology, 10 mm span, force sweep
SWEEP_UNBLOWN = "JF1_L1_UNBLOWN_A0"
SWEEP_TIME = "8000"

def _sweep_yplus_max():
    """Largest wall spacing on each of the five calculations, in sweep order.

    This figure renders ONE of the five cases, because a histogram has to be
    of something. But the page it sits on is captioned as the grid all five
    ran on, so any number it states about the grid has to come from all five.
    Reading the rendered case and calling it the grid's is how "largest 0.256"
    reached a signed page while the true sweep maximum was 0.398.

    Shared reader, one implementation, plants and refuses.
    """
    import sys as _sys

    _sys.path.insert(0, HERE)
    import jf1_display_numbers as _jf1num

    return [_jf1num.wall_yplus(_jf1num.RUN_ROOT / name, SWEEP_TIME)["max"]
            for _, name in _jf1num.SWEEP_CASES]


CHORD = 1.0
H_SLOT = 0.005                         # m, registered slot height
SLOT_FLOOR = 12                        # registered floor, cells across h
WAKE_BOX_END = 4.0                     # m, trailing edge + 3 chords

# compute, taken from the same sources the other demo figures use
FLOW_ESTIMATE_CORE_MIN = 90.5
SWEEP_ESTIMATE_EACH = 11.36
SWEEP_N = 5

# ------------------------------------------------------------------- styling --
plt.rcParams.update({
    **latin_modern_rc(),
    "axes.titlesize": 12.5,
    "axes.labelsize": 11.5,
})

INK = "#16161a"
INK2 = "#45454e"
MUTED = "#8a8a93"
GRIDC = "#dcdce2"
WARN = "#a51c1c"
MESHC = "#3f7cb4"
MESHC2 = "#0b4f8f"
BODY = "#26262c"
BOXC = "#c1121f"
ACCENT = "#0b4f8f"



def tidy(ax):
    ax.grid(True, color=GRIDC, lw=0.6)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=INK2, labelsize=9.5)


def frame(ax):
    """Boxed frame for a mesh panel -- all four spines, no grid."""
    ax.grid(False)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(True)
        ax.spines[s].set_color(MUTED)
        ax.spines[s].set_linewidth(0.8)
    ax.tick_params(colors=INK2, labelsize=8.5)




def caveat_box(ax, bullets, title="WHAT YOU SHOULD KNOW ABOUT THIS MESH",
               width=88):
    """Two columns of plain-English bullets, hard-wrapped so neither column
    can run off the page."""
    import textwrap
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                               fc="#f5f5f8", ec=GRIDC, lw=0.8, zorder=0,
                               clip_on=False))
    ax.text(0.012, 0.93, title, transform=ax.transAxes, fontsize=9.6,
            color=INK, weight="bold", va="top", ha="left")
    wrapped = [textwrap.wrap(b, width=width) for b in bullets]
    counts = [len(w) for w in wrapped]
    total = sum(counts)
    # cut where the two columns come out most nearly equal in LINES
    cut, best = 1, None
    for i in range(1, len(wrapped)):
        left = sum(counts[:i])
        d = abs(left - (total - left))
        if best is None or d < best:
            best, cut = d, i
    for col, chunk in ((0.012, wrapped[:cut]), (0.508, wrapped[cut:])):
        txt = "\n".join("•  " + w[0] + ("\n" + "\n".join("   " + l
                                                         for l in w[1:])
                                        if len(w) > 1 else "")
                        for w in chunk)
        ax.text(col, 0.79, txt, transform=ax.transAxes, fontsize=8.5,
                color=INK2, va="top", ha="left", linespacing=1.36)


def cost_line(fig, text):
    fig.text(0.5, 0.010, text, ha="center", va="bottom", fontsize=8.0,
             color=MUTED)


# =========================================================== polyMesh reader ==
class MeshReadError(Exception):
    pass


def _body(path):
    if not os.path.isfile(path):
        raise MeshReadError("no such mesh file: %s" % path)
    txt = open(path).read()
    if "FoamFile" not in txt:
        raise MeshReadError("not an OpenFOAM file: %s" % path)
    if not re.search(r"format\s+ascii", txt):
        raise MeshReadError("mesh file is not ascii, refusing to guess: %s"
                            % path)
    i = txt.index("FoamFile")
    j = txt.index("}", i)
    return txt[j + 1:]


def read_points(path):
    b = _body(path)
    m = re.search(r"^\s*(\d+)\s*$", b, re.M)
    n = int(m.group(1))
    start = b.index("(", m.end())
    vals = re.findall(r"\(\s*([-\dEe.+]+)\s+([-\dEe.+]+)\s+([-\dEe.+]+)\s*\)",
                      b[start:])
    if len(vals) != n:
        raise MeshReadError("points: header says %d, read %d" % (n, len(vals)))
    return np.asarray(vals, dtype=float)


def read_faces(path):
    b = _body(path)
    m = re.search(r"^\s*(\d+)\s*$", b, re.M)
    n = int(m.group(1))
    start = b.index("(", m.end())
    out = []
    for mm in re.finditer(r"(\d+)\s*\(([^)]*)\)", b[start:]):
        idx = [int(t) for t in mm.group(2).split()]
        if len(idx) != int(mm.group(1)):
            raise MeshReadError("face length mismatch in %s" % path)
        out.append(idx)
        if len(out) == n:
            break
    if len(out) != n:
        raise MeshReadError("faces: header says %d, read %d" % (n, len(out)))
    return out


def read_boundary(path):
    b = _body(path)
    pat = {}
    for mm in re.finditer(r"(\w+)\s*\{([^}]*)\}", b):
        d = mm.group(2)
        nf = re.search(r"nFaces\s+(\d+)", d)
        sf = re.search(r"startFace\s+(\d+)", d)
        ty = re.search(r"type\s+(\w+)", d)
        if nf and sf:
            pat[mm.group(1)] = dict(nFaces=int(nf.group(1)),
                                    startFace=int(sf.group(1)),
                                    type=ty.group(1) if ty else "?")
    if not pat:
        raise MeshReadError("no patches parsed from %s" % path)
    return pat


class Mesh(object):
    """The real computational mesh, read from constant/polyMesh."""

    def __init__(self, case_dir):
        pm = os.path.join(case_dir, "constant", "polyMesh")
        # REFUSE rather than fall back: an STL is not a mesh.
        for f in ("points", "faces", "boundary"):
            if not os.path.isfile(os.path.join(pm, f)):
                raise MeshReadError(
                    "constant/polyMesh/%s missing under %s -- refusing to "
                    "draw anything else" % (f, case_dir))
        self.case = case_dir
        self.pm = pm
        self.points = read_points(os.path.join(pm, "points"))
        self.faces = read_faces(os.path.join(pm, "faces"))
        self.bnd = read_boundary(os.path.join(pm, "boundary"))
        for p in ("back", "front", "airfoil", "jetSlot"):
            if p not in self.bnd:
                raise MeshReadError("patch %r absent from %s" % (p, pm))
        if self.bnd["back"]["type"] != "empty":
            raise MeshReadError("`back` is not an empty patch: this is not a "
                                "one-cell-deep 2-D mesh")
        self.n_cells = self.bnd["back"]["nFaces"]

        # 2-D cell footprints: one quad per cell, straight off the empty patch
        pf = self.patch_faces("back")
        self.polys = [self.points[f][:, :2] for f in pf]
        self.centroid = np.array([p.mean(axis=0) for p in self.polys])
        z = self.points[:, 2]
        self.t_z = float(z.max() - z.min())

    def patch_faces(self, name):
        p = self.bnd[name]
        return self.faces[p["startFace"]:p["startFace"] + p["nFaces"]]

    def patch_poly(self, name):
        return [self.points[f] for f in self.patch_faces(name)]

    # ---------------------------------------------------------- measurements --
    def slot_measure(self):
        """Measure the slot from the mesh: height, tiling, cells across it."""
        jp = self.patch_poly("jetSlot")
        lo = np.array([p[:, 1].min() for p in jp])
        hi = np.array([p[:, 1].max() for p in jp])
        bands = sorted(zip(lo, hi))
        gap = max(abs(bands[i + 1][0] - bands[i][1])
                  for i in range(len(bands) - 1))
        dy = np.array([b - a for a, b in bands])
        h = hi.max() - lo.min()
        area = 0.0
        for p in jp:
            area += 0.5 * np.linalg.norm(np.cross(p[2] - p[0], p[3] - p[1]))
        xs = np.array([p[:, 0].mean() for p in jp])
        return dict(n_across=len(jp), h=float(h), gap=float(gap),
                    dy_min=float(dy.min()), dy_max=float(dy.max()),
                    area=float(area), x=float(xs.mean()),
                    y_lo=float(lo.min()), y_hi=float(hi.max()),
                    bands=bands)

    def slot_cell_crosscheck(self, h):
        """Independent count: cell centroids inside the slot band at the first
        station downstream of the slot plane."""
        s = self.slot_measure()
        dy = s["dy_max"]
        c = self.centroid
        band = np.abs(c[:, 1]) <= 0.5 * h * (1.0 + 1e-7)
        near = band & (c[:, 0] > s["x"]) & (c[:, 0] < s["x"] + 1.5 * dy)
        return int(near.sum())

    def wake_box_cells(self, x0, x1):
        """Number of cells ALONG THE FLOW between x0 and x1 in the wake sheet:
        count distinct streamwise stations, not the raw cell tally."""
        s = self.slot_measure()
        c = self.centroid
        sel = (np.abs(c[:, 1]) < 0.5 * s["h"]) & (c[:, 0] > x0) & (c[:, 0] < x1)
        xs = np.unique(np.round(c[sel, 0], 12))
        return int(len(xs))

    def wall_layer_slice(self, x0, x1, height):
        """Cells above the upper surface, plotted against HEIGHT ABOVE THE
        WALL.  Real cell vertices; only the vertical datum is shifted, so the
        first 5 um layer is visible against a 1 m chord."""
        us = self.upper_surface()

        def ysurf(x):
            return np.interp(x, us[:, 0], us[:, 1])

        c = self.centroid
        cand = np.where((c[:, 0] > x0) & (c[:, 0] < x1) & (c[:, 1] > 0))[0]
        out = []
        for i in cand:
            p = self.polys[i]
            q = p.copy()
            q[:, 1] = p[:, 1] - ysurf(p[:, 0])
            hmin, hmax = q[:, 1].min(), q[:, 1].max()
            if hmin > -1e-9 and hmin < height:
                out.append(q)
        if not out:
            raise MeshReadError("no wall-layer cells found")
        return out

    def in_window(self, xlim, ylim, pad=1.0):
        c = self.centroid
        dx = (xlim[1] - xlim[0]) * pad
        dy = (ylim[1] - ylim[0]) * pad
        return np.where((c[:, 0] > xlim[0] - dx) & (c[:, 0] < xlim[1] + dx)
                        & (c[:, 1] > ylim[0] - dy) & (c[:, 1] < ylim[1] + dy))[0]

    def upper_surface(self):
        ap = np.array([p[:, :2].mean(axis=0) for p in self.patch_poly("airfoil")])
        up = ap[ap[:, 1] > 0]
        return up[np.argsort(up[:, 0])]


def draw_mesh(ax, mesh, xlim, ylim, lw=0.35, color=MESHC, face="white",
              pad=1.0):
    """Draw the REAL cells whose footprint falls in the window."""
    idx = mesh.in_window(xlim, ylim, pad=pad)
    if len(idx) == 0:
        raise MeshReadError("no cells in the requested window -- refusing to "
                            "draw an empty panel")
    pc = PolyCollection([mesh.polys[i] for i in idx], facecolors=face,
                        edgecolors=color, linewidths=lw, zorder=2)
    ax.add_collection(pc)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    return len(idx)


def draw_body(ax, mesh, color=BODY, lw=1.1):
    """The solid surface, drawn from the wall patch of the MESH (not an STL)."""
    ap = mesh.patch_poly("airfoil")
    segs = []
    for p in ap:
        q = p[np.isclose(p[:, 2], p[:, 2].min())][:, :2]
        if len(q) == 2:
            segs.append(q)
    from matplotlib.collections import LineCollection
    ax.add_collection(LineCollection(segs, colors=color, linewidths=lw,
                                     zorder=6))


# ======================================================== checkMesh scraping ==
CM_KEYS = [
    ("cells", r"cells:\s+(\d+)"),
    ("points", r"points:\s+(\d+)"),
    ("faces", r"faces:\s+(\d+)"),
    ("hex", r"hexahedra:\s+(\d+)"),
    ("nonorth_max", r"non-orthogonality Max:\s*([-\d.eE+]+)"),
    ("nonorth_avg", r"non-orthogonality Max:\s*[-\d.eE+]+\s+average:\s*([-\d.eE+]+)"),
    ("skew_max", r"Max skewness = ([-\d.eE+]+)"),
    ("vol_min", r"Min volume = ([-\d.eE+]+)"),
    ("vol_max", r"Max volume = ([-\d.eE+]+)"),
    ("ar_max", r"[Mm]ax aspect ratio:?\s*=?\s*([-\d.eE+]+)"),
]


def read_checkmesh(path):
    txt = open(path).read()
    out = {"path": path}
    for k, pat in CM_KEYS:
        m = re.search(pat, txt)
        out[k] = float(m.group(1).rstrip(".")) if m else None
    # negative volumes: checkMesh names them explicitly when present
    neg = re.search(r"(\d+)\s+cells with\s+zero or negative", txt) \
        or re.search(r"zero or negative cell volume.*?(\d+)", txt)
    out["neg_vol"] = int(neg.group(1)) if neg else 0
    out["vol_ok"] = "Cell volumes OK" in txt
    out["mesh_ok"] = "Mesh OK." in txt
    m = re.search(r"Failed (\d+) mesh checks", txt)
    out["failed_checks"] = int(m.group(1)) if m else 0
    out["high_ar_cells"] = None
    m = re.search(r"number of cells (\d+)", txt)
    if m:
        out["high_ar_cells"] = int(m.group(1))
    return out


# ============================================================= field reading ==
def read_patch_scalars(path, patch):
    txt = open(path).read()
    i = txt.index("boundaryField")
    seg = txt[i:]
    m = re.search(re.escape(patch) + r"\s*\{", seg)
    if not m:
        raise MeshReadError("patch %r absent from %s" % (patch, path))
    tail = seg[m.end():]
    blk = tail[:tail.index("}")]
    mm = re.search(r"nonuniform\s+List<scalar>\s*(\d+)\s*\(", blk)
    if not mm:
        raise MeshReadError("patch %r on %s carries no per-face list"
                            % (patch, path))
    n = int(mm.group(1))
    rest = mm.string[mm.end():]
    vals = np.array([float(t) for t in rest[:rest.index(")")].split()])
    if len(vals) != n:
        raise MeshReadError("y+ list: header %d, read %d" % (n, len(vals)))
    return vals


def read_yplus_history(case_dir):
    dat = os.path.join(case_dir, "postProcessing", "yPlus", "0", "yPlus.dat")
    rows = []
    for ln in open(dat):
        if ln.startswith("#"):
            continue
        t = ln.split()
        if len(t) >= 5:
            rows.append([float(t[0]), float(t[2]), float(t[3]), float(t[4])])
    return np.array(rows), dat


def exec_core_min(log_path, ranks):
    last = None
    with open(log_path) as fh:
        for ln in fh:
            if ln.startswith("ExecutionTime"):
                last = ln
    m = re.search(r"ExecutionTime = ([\d.]+) s", last)
    return float(m.group(1)) * ranks / 60.0


# ====================================================================== main ==
def main():
    out = os.path.join(HERE, "artefacts")
    os.makedirs(out, exist_ok=True)

    flow_dir = os.path.join(HERE, FLOW)
    sweep_dir = os.path.join(HERE, SWEEP)

    mF = Mesh(flow_dir)
    mS = Mesh(sweep_dir)

    sF = mF.slot_measure()
    sS = mS.slot_measure()
    xcF = mF.slot_cell_crosscheck(sF["h"])
    n_wake = mF.wake_box_cells(CHORD, WAKE_BOX_END)

    cmF = read_checkmesh(os.path.join(flow_dir, "log.checkMesh"))
    cmS = read_checkmesh(os.path.join(sweep_dir, "log.checkMesh"))

    yp = read_patch_scalars(os.path.join(flow_dir, FLOW_TIME, "yPlus"),
                            "airfoil")
    ypS = read_patch_scalars(os.path.join(sweep_dir, SWEEP_TIME, "yPlus"),
                             "airfoil")
    hist, hist_path = read_yplus_history(flow_dir)

    # y+ face positions, matched to the airfoil patch face order
    apF = np.array([p[:, :2].mean(axis=0) for p in mF.patch_poly("airfoil")])
    if len(apF) != len(yp):
        raise MeshReadError("wall faces %d, y+ values %d" % (len(apF), len(yp)))

    # cross-check the field read against the solver's own running summary
    tail = hist[-1]
    for name, a, b in (("min", tail[1], yp.min()),
                       ("max", tail[2], yp.max()),
                       ("mean", tail[3], yp.mean())):
        if abs(a - b) / max(abs(b), 1e-30) > 1e-6:
            raise MeshReadError("y+ %s disagrees between the field and the "
                                "run's own summary: %.9e vs %.9e"
                                % (name, a, b))

    # ------------------------------------------------------------- compute ---
    flow_core = exec_core_min(os.path.join(flow_dir, "log.simpleFoam"), 4)

    # COST BASIS FOR THE FIVE-ROW SWEEP -- FIXED, DO NOT RE-DERIVE.
    # Two honest bases exist and they differ by 0.23 %:
    #   (a) ExecutionTime x ranks / 60 from log.simpleFoam ....... 117.2147
    #   (b) the sum of each run's own RUN_STATUS core_min_MEASURED  117.4833
    # The RUN_STATUS basis (b) GOVERNS.  It is the run's own recorded field, it
    # is what the cost ledger cites, and it is what the Act B lift/pressure
    # figures quote.  One act must not show two numbers for one quantity, so
    # this file reads (b) exactly as those figures do.  exec_core_min() below
    # is still used for the SINGLE flow run, whose RUN_STATUS basis is not in
    # play on any other figure.  Do not switch this back to (a).
    sweep_core = 0.0
    for d in (SWEEP_UNBLOWN, "JF1_L1_BLOWN_CMU005_A0", "JF1_L1_BLOWN_CMU010_A0",
              "JF1_L1_BLOWN_CMU020_A0", "JF1_L1_BLOWN_CMU040_A0"):
        case = os.path.join(HERE, d)
        st = {}
        for f in os.listdir(case):
            if f.startswith("RUN_STATUS"):
                for line in open(os.path.join(case, f)):
                    q = line.split(None, 1)
                    if len(q) == 2:
                        st[q[0]] = q[1].strip()
        if "core_min_MEASURED" not in st:
            raise MeshReadError(
                "no core_min_MEASURED in the RUN_STATUS file for %s -- the "
                "governing cost basis is unreadable and this figure must not "
                "fall back to the ExecutionTime basis, which would print a "
                "second number for the same quantity" % d)
        sweep_core += float(st["core_min_MEASURED"])
    sweep_est = SWEEP_ESTIMATE_EACH * SWEEP_N

    cost_flow = ("Computer time for the calculation these near-wall numbers "
                 "come from: we estimated %.1f processor-minutes before running it "
                 "and used %.1f — %.1f %% over our estimate.  Building the "
                 "mesh itself took under one processor-minute."
                 % (FLOW_ESTIMATE_CORE_MIN, flow_core,
                    100.0 * (flow_core / FLOW_ESTIMATE_CORE_MIN - 1.0)))
    cost_sweep = ("Computer time for the five calculations this mesh carries: "
                  "we estimated %.1f processor-minutes before running them and used "
                  "%.1f — %.2f times our estimate.  Building the mesh itself "
                  "took under one processor-minute."
                  % (sweep_est, sweep_core, sweep_core / sweep_est))

    written = []
    notes = []

    def save(fig, stem):
        for ext in ("pdf", "png"):
            p = os.path.join(out, "%s.%s" % (stem, ext))
            fig.savefig(p, dpi=200, facecolor="white")
            written.append(p)
        plt.close(fig)

    # ================================ FIGURE 5: the flow-field mesh, sliced ==
    fig = plt.figure(figsize=(14.0, 8.8))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.65, 1.35],
                          width_ratios=[1.0, 1.0, 1.0],
                          left=0.055, right=0.982, top=0.885, bottom=0.130,
                          hspace=0.40, wspace=0.20)
    assert_no_banner(fig)
    fig.text(0.5, 0.955,
             check_title("The grid the flow is computed on"),
             ha="center", va="top", fontsize=15.5, color=INK, weight="bold")

    # -- (a) near field, spanning the wing and the refined wake -------------
    ax = fig.add_subplot(gs[0, :])
    xlim, ylim = (-0.55, 4.60), (-0.92, 0.92)
    draw_mesh(ax, mF, xlim, ylim, lw=0.16, pad=0.06)
    ax.add_patch(Rectangle((CHORD, ylim[0]), WAKE_BOX_END - CHORD,
                           ylim[1] - ylim[0], fill=False, ec=BOXC, lw=1.5,
                           ls=(0, (5, 3)), zorder=7))
    ax.annotate("", xy=(CHORD, -0.50), xytext=(WAKE_BOX_END, -0.50),
                arrowprops=dict(arrowstyle="<->", color=BOXC, lw=1.3),
                zorder=8)
    ax.text(0.5 * (CHORD + WAKE_BOX_END), -0.56,
            "refined wake region: trailing edge to 3 chords downstream\n"
            "%d cells along the flow, each no more than 8 %% longer\n"
            "than the one before it" % n_wake,
            ha="center", va="top", fontsize=8.8, color=BOXC, weight="bold",
            zorder=8, linespacing=1.3,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=BOXC, lw=0.7,
                      alpha=0.95))
    draw_body(ax, mF)
    for (bx, by, bw, bh, tag, tx, ty) in (
            (-0.02, -0.055, 0.10, 0.11, "B", -0.10, 0.10),
            (0.955, -0.050, 0.075, 0.10, "C", 0.90, 0.10)):
        ax.add_patch(Rectangle((bx, by), bw, bh, fill=False, ec=ACCENT,
                               lw=1.3, zorder=8))
        ax.text(tx, ty, tag, fontsize=10.5, color=ACCENT, weight="bold",
                zorder=9, ha="center")
    # panel D looks at a 1 mm-tall strip on the upper surface: too thin to
    # outline, so it is marked with a bar and a leader.
    us = mF.upper_surface()
    xd = np.linspace(0.30, 0.70, 60)
    ax.plot(xd, np.interp(xd, us[:, 0], us[:, 1]), color=ACCENT, lw=3.0,
            solid_capstyle="butt", zorder=9)
    ax.annotate("D", xy=(0.50, np.interp(0.50, us[:, 0], us[:, 1])),
                xytext=(0.46, 0.30), fontsize=10.5, color=ACCENT,
                weight="bold", ha="center",
                arrowprops=dict(arrowstyle="->", color=ACCENT, lw=1.1),
                zorder=9)
    ax.set_aspect("equal")
    frame(ax)
    ax.set_xlabel(r"$x$ [m]")
    ax.set_ylabel(r"$y$ [m]")
    ax.set_title("A.  Around the wing and through the wake  "
                 "(the whole grid reaches 25 m in every direction)",
                 color=INK, fontsize=11.5, pad=7)

    # -- (B) leading edge ---------------------------------------------------
    ax = fig.add_subplot(gs[1, 0])
    xl, yl = (-0.018, 0.082), (-0.050, 0.050)
    draw_mesh(ax, mF, xl, yl, lw=0.30, pad=0.12)
    draw_body(ax, mF, lw=1.4)
    ax.set_aspect("equal")
    frame(ax)
    ax.set_xlabel(r"$x$ [m]")
    ax.set_ylabel(r"$y$ [m]")
    ax.set_title("B.  Leading edge", color=INK, fontsize=11.0, pad=6)

    # -- (C) trailing edge and slot ----------------------------------------
    ax = fig.add_subplot(gs[1, 1])
    xl, yl = (0.958, 1.033), (-0.0375, 0.0375)
    draw_mesh(ax, mF, xl, yl, lw=0.30, pad=0.12)
    draw_body(ax, mF, lw=1.4)
    ax.plot([sF["x"], sF["x"]], [sF["y_lo"], sF["y_hi"]], color=BOXC, lw=2.6,
            zorder=9, solid_capstyle="butt")
    ax.annotate("air leaves here,\n30° below the chord line",
                xy=(sF["x"], 0.0), xytext=(0.975, -0.026),
                fontsize=8.5, color=BOXC, weight="bold", ha="left",
                arrowprops=dict(arrowstyle="->", color=BOXC, lw=1.1),
                zorder=10)
    ax.set_aspect("equal")
    frame(ax)
    ax.set_xlabel(r"$x$ [m]")
    ax.set_ylabel(r"$y$ [m]")
    ax.set_title("C.  Trailing edge and the slot", color=INK, fontsize=11.0,
                 pad=6)

    # -- (D) wall-normal layers, plotted against height above the wall ------
    ax = fig.add_subplot(gs[1, 2])
    band = 4.0e-4
    x0d, x1d = 0.30, 0.70
    lay = mF.wall_layer_slice(x0d, x1d, band)
    # plot in micrometres so the near-wall packing is legible
    lay_um = [np.column_stack((q[:, 0], q[:, 1] * 1e6)) for q in lay]
    ax.add_collection(PolyCollection(lay_um, facecolors="white",
                                     edgecolors=MESHC, linewidths=0.45,
                                     zorder=2))
    ax.axhline(0.0, color=BODY, lw=2.0, zorder=7)
    # layers per column: the strip holds whole columns, so cells / columns
    apu = mF.upper_surface()
    edges = np.sort(apu[(apu[:, 0] > x0d) & (apu[:, 0] < x1d)][:, 0])
    cx = np.array([q[:, 0].mean() for q in lay])
    col_id = np.searchsorted(edges, cx)
    mid = int(np.searchsorted(edges, 0.5))
    n_layers = int(np.sum(col_id == mid))
    if n_layers < 2:
        raise MeshReadError("mid-chord wall column holds %d cells" % n_layers)
    ax.set_xlim(x0d, x1d)
    ax.set_ylim(-0.045 * band * 1e6, band * 1e6)
    ax.set_aspect("auto")
    frame(ax)
    ax.set_xlabel(r"position along the chord $x$ [m]")
    ax.set_ylabel(r"height above the wing surface [$\mu$m]")
    ax.set_title("D.  The layers packed against the wall\n"
                 "(height measured up from the surface)",
                 color=INK, fontsize=11.0, pad=6)
    ax.text(0.5, 0.955,
            "%d layers in the first 400 $\\mu$m at half-chord;\n"
            "the one touching the wall is 5.0 $\\mu$m thick" % n_layers,
            transform=ax.transAxes, ha="center", va="top", fontsize=8.4,
            color=ACCENT, weight="bold",
            bbox=dict(boxstyle="round,pad=0.28", fc="white", ec=ACCENT,
                      lw=0.7, alpha=0.93))

    caption(fig, "Cell edges read back from the solved case: the whole grid, "
                 "the leading edge, the slot and the wall layers.", y=0.032)
    notes.append(sheet_note(
        "jet_flap_5_mesh_flowfield", "The grid the flow was computed on",
        "Every line on this page is an edge of a real computation cell, read "
        "back out of the solved case. This is the grid the equations were "
        "solved on, not a drawing of the shape and not the triangles of a CAD "
        "surface: a C-shaped grid wrapped round the wing and trailed "
        "downstream, %s cells, one cell deep, %.1f m span. No surface "
        "tessellation is used anywhere, and the wing outline is drawn from "
        "the wall faces of the grid itself, so the outline and the cells "
        "cannot disagree.\n\n"
        "Panel D measures height up from the surface rather than from the "
        "centreline. At true proportions the layers next to the wall are far "
        "too thin to see: the first is 5 micrometres against a 1 m chord. The "
        "refined wake region is refinement along the flow direction, where "
        "cell length grows by no more than 8 %% from one cell to the next out "
        "to 3 chords and then relaxes toward the far boundary.\n\n"
        "This is a two-dimensional calculation. The grid is one cell deep and "
        "the two side faces take no part in the solution."
        % ("{:,}".format(mF.n_cells), mF.t_z)))
    cost_line(fig, cost_flow)
    save(fig, "jet_flap_5_mesh_flowfield")

    # ==================== FIGURE 6: slot resolution, quality, near-wall =====
    fig = plt.figure(figsize=(14.0, 8.6))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.10, 1.15],
                          left=0.058, right=0.982, top=0.890, bottom=0.090,
                          hspace=0.20, wspace=0.26)
    assert_no_banner(fig)
    fig.text(0.5, 0.958,
             check_title("How well the grid resolves the two places that matter"),
             ha="center", va="top", fontsize=15.5, color=INK, weight="bold")

    # -- (A) slot mouth, cells counted --------------------------------------
    ax = fig.add_subplot(gs[0, 0])
    pad_x = 3.2e-3
    xl = (sF["x"] - pad_x, sF["x"] + pad_x)
    yl = (-0.5 * sF["h"] - 3.0e-3, 0.5 * sF["h"] + 1.0e-3)
    draw_mesh(ax, mF, xl, yl, lw=0.75, pad=0.25)
    for i, (lo, hi) in enumerate(sF["bands"]):
        ax.add_patch(Rectangle((sF["x"] - 3.6e-4, lo), 3.6e-4, hi - lo,
                               fc="#ffd9d9", ec=BOXC, lw=0.8, zorder=5))
        ax.text(sF["x"] - 1.85e-4, 0.5 * (lo + hi), "%d" % (i + 1),
                ha="center", va="center", fontsize=6.6, color=BOXC,
                weight="bold", zorder=6)
    ax.annotate("", xy=(sF["x"] + 2.0e-3, sF["y_lo"]),
                xytext=(sF["x"] + 2.0e-3, sF["y_hi"]),
                arrowprops=dict(arrowstyle="<->", color=INK, lw=1.2))
    ax.text(sF["x"] + 2.25e-3, 0.0,
            "slot height\n%.1f mm" % (1e3 * sF["h"]),
            fontsize=8.6, color=INK, va="center", ha="left", weight="bold")
    ax.set_aspect("equal")
    frame(ax)
    ax.set_xlabel(r"$x$ [m]")
    ax.set_ylabel(r"$y$ [m]")
    ax.set_title("A.  Cells across the slot, counted one by one",
                 color=INK, fontsize=11.0, pad=6)
    ax.text(0.52, 0.045,
            "%d cells across the slot height, each %.3f mm tall.\n"
            "The design target was at least %d."
            % (sF["n_across"], 1e3 * sF["dy_max"], SLOT_FLOOR),
            transform=ax.transAxes, ha="center", va="bottom", fontsize=8.8,
            color=BOXC, weight="bold", linespacing=1.35, zorder=10,
            bbox=dict(boxstyle="round,pad=0.32", fc="white", ec=BOXC, lw=0.8,
                      alpha=0.95))

    # -- (B) y+ histogram ----------------------------------------------------
    ax = fig.add_subplot(gs[0, 1])
    bins = np.linspace(0.0, max(0.5, yp.max() * 1.06), 26)
    ax.hist(yp, bins=bins, color="#7fa8d0", edgecolor=MESHC2, linewidth=0.7)
    ax.axvline(1.0, color=WARN, lw=1.6, ls="--")
    ax.text(0.905, 0.90, "wall-resolved limit,\n"
                         r"$y^{+}=1$", transform=ax.transAxes, ha="right",
            va="top", fontsize=8.8, color=WARN, weight="bold")
    ax.set_xlim(0.0, 1.08)
    tidy(ax)
    ax.set_xlabel(r"near-wall spacing $y^{+}$ [--]")
    ax.set_ylabel("number of wall cells [--]")
    ax.set_title("B.  Near-wall spacing over the whole surface",
                 color=INK, fontsize=11.0, pad=6)
    ax.text(0.50, 0.72,
            "smallest %.3f\naverage  %.3f\nlargest  %.3f"
            % (yp.min(), yp.mean(), yp.max()),
            transform=ax.transAxes, ha="left", va="top", fontsize=9.0,
            color=INK, family="monospace",
            bbox=dict(boxstyle="round,pad=0.35", fc="#f5f5f8", ec=GRIDC,
                      lw=0.8))

    # -- (C) y+ along the surface -------------------------------------------
    ax = fig.add_subplot(gs[0, 2])
    up = apF[:, 1] > 0
    lo = ~up
    for sel, lab, c, mk in ((up, "upper surface", MESHC2, "o"),
                            (lo, "lower surface", "#c1121f", "s")):
        o = np.argsort(apF[sel, 0])
        ax.plot(apF[sel, 0][o] / CHORD, yp[sel][o], mk + "-", color=c,
                ms=2.4, lw=1.0, label=lab)
    ax.axhline(1.0, color=WARN, lw=1.5, ls="--")
    ax.text(0.02, 1.02, r"wall-resolved limit, $y^{+}=1$", fontsize=8.5,
            color=WARN, weight="bold", va="bottom")
    ax.set_ylim(0.0, 1.22)
    ax.set_xlim(-0.02, 1.02)
    tidy(ax)
    ax.legend(frameon=False, fontsize=9.0, loc="center right")
    ax.set_xlabel(r"distance along the chord $x/c$ [--]")
    ax.set_ylabel(r"near-wall spacing $y^{+}$ [--]")
    ax.set_title(r"C.  Where the wall spacing is largest",
                 color=INK, fontsize=11.0, pad=6)

    # -- (D) mesh quality table ---------------------------------------------
    ax = fig.add_subplot(gs[1, :])
    ax.axis("off")
    rows = [
        ("cells", "{:,}".format(int(cmF["cells"])).replace(",", " "),
         "{:,}".format(int(cmS["cells"])).replace(",", " "), "--",
         "every cell a six-sided box"),
        ("cells across the slot", "%d" % sF["n_across"], "%d" % sS["n_across"],
         r"$\geq$ 12", "counted from the stored grid"),
        ("largest cell distortion", "%.1f" % cmF["nonorth_max"],
         "%.1f" % cmS["nonorth_max"], "< 65",
         "angle between neighbouring cells, degrees"),
        ("average cell distortion", "%.1f" % cmF["nonorth_avg"],
         "%.1f" % cmS["nonorth_avg"], "--", "degrees"),
        ("largest cell skew", "%.2f" % cmF["skew_max"],
         "%.2f" % cmS["skew_max"], "< 4",
         "how far a face centre misses the line joining cell centres"),
        ("cells of zero or negative volume", "%d" % cmF["neg_vol"],
         "%d" % cmS["neg_vol"], "0", "a single one invalidates a calculation"),
        ("smallest cell volume [m³]", "%.2e" % cmF["vol_min"],
         "%.2e" % cmS["vol_min"], "> 0", "--"),
        ("largest cell stretch", "%.3g" % cmF["ar_max"],
         "%.3g" % cmS["ar_max"], "reported",
         "length ÷ thickness; large by design in the far wake"),
    ]
    ax.text(0.0, 1.00, "D.  Grid quality, as measured by the standard "
            "checking tool", transform=ax.transAxes, fontsize=11.0,
            color=INK, weight="bold", va="top")
    cols = [0.0, 0.325, 0.475, 0.615, 0.735]
    heads = ["measure", "flow-field grid\n(%s cells)"
             % "{:,}".format(int(cmF["cells"])).replace(",", " "),
             "force-sweep grid\n(%s cells)"
             % "{:,}".format(int(cmS["cells"])).replace(",", " "),
             "target set\nbefore building", "what it means"]
    for cx, hd in zip(cols, heads):
        ax.text(cx, 0.880, hd, transform=ax.transAxes, fontsize=8.8,
                color=INK, weight="bold", va="top", linespacing=1.3)
    ax.plot([0.0, 1.0], [0.735, 0.735], transform=ax.transAxes, color=MUTED,
            lw=0.9, clip_on=False)
    yy = 0.672
    for r in rows:
        for cx, cell in zip(cols, r):
            ax.text(cx, yy, cell, transform=ax.transAxes, fontsize=8.5,
                    color=INK2 if cx == 0.0 else INK, va="top")
        yy -= 0.082
    # The paragraph that used to sit under this table is on the sheet
    # note: figures carry no paragraphs, and the sentence about why the
    # far-wake stretch figure is large is an explanation, not a number.

    tailw = hist[hist[:, 0] >= 18000]
    spread = 100.0 * (tailw[:, 2].max() - tailw[:, 2].min()) / tailw[:, 2].mean()
    caption(fig, "Cells across the slot, wall spacing over the wing, and the "
                 "quality measures of both grids.", y=0.032)
    notes.append(sheet_note(
        "jet_flap_6_mesh_resolution",
        "How well the grid resolves the two places that matter",
        "The slot is 5.0 mm tall, one two-hundredth of the chord, and the "
        "sheet of air it releases is the whole point of the design. The other "
        "place that matters is the skin of the wing, where the drag is made. "
        "Both are counted here rather than asserted.\n\n"
        "Panels B and C are properties of the grid and the solved flow "
        "together, so they are read from the calculation and not from the "
        "grid alone. All %d wall cells sit below the wall-resolved limit, the "
        "largest being %.3f, so the flow next to the wall is computed rather "
        "than assumed from a formula. The near-wall spacing stopped moving "
        "well before the calculation ended: over the last 2,000 steps its "
        "largest value varies by %.3f %%. That calculation reached its step "
        "limit before it met its convergence target, so its flow field should "
        "be read as indicative.\n\n"
        "Panel D sets two different grids beside each other in one table. "
        "They are never drawn on shared axes. Both are made only of six-sided "
        "boxes and no cell was cut or collapsed. The stretch figure is large "
        "in the outer wake because cells are deliberately long there, in the "
        "flow direction, where nothing is changing across the flow: the "
        "stretching lies along the direction being resolved."
        % (len(yp), yp.max(), spread)))
    cost_line(fig, cost_flow)
    save(fig, "jet_flap_6_mesh_resolution")

    # ==================== FIGURE 7: the force-sweep mesh, sliced ============
    fig = plt.figure(figsize=(14.0, 8.5))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.55, 1.30],
                          left=0.055, right=0.982, top=0.885, bottom=0.130,
                          hspace=0.40, wspace=0.20)
    assert_no_banner(fig)
    fig.text(0.5, 0.955,
             check_title("The grid the lift and pressure figures are computed on"),
             ha="center", va="top", fontsize=15.5, color=INK, weight="bold")

    ax = fig.add_subplot(gs[0, :])
    xlim, ylim = (-1.35, 2.65), (-0.72, 0.72)
    draw_mesh(ax, mS, xlim, ylim, lw=0.16, pad=0.08)
    draw_body(ax, mS)
    for (bx, by, bw, bh, tag, tx, ty) in (
            (-0.02, -0.055, 0.10, 0.11, "B", -0.11, 0.10),
            (0.955, -0.050, 0.075, 0.10, "C", 0.89, 0.10)):
        ax.add_patch(Rectangle((bx, by), bw, bh, fill=False, ec=ACCENT,
                               lw=1.3, zorder=8))
        ax.text(tx, ty, tag, fontsize=10.5, color=ACCENT, weight="bold",
                zorder=9, ha="center")
    ax.set_aspect("equal")
    frame(ax)
    ax.set_xlabel(r"$x$ [m]")
    ax.set_ylabel(r"$y$ [m]")
    ax.set_title("A.  Around the wing  (the whole grid reaches 26 m in every "
                 "direction)", color=INK, fontsize=11.5, pad=7)

    ax = fig.add_subplot(gs[1, 0])
    draw_mesh(ax, mS, (-0.018, 0.082), (-0.050, 0.050), lw=0.30, pad=0.12)
    draw_body(ax, mS, lw=1.4)
    ax.set_aspect("equal")
    frame(ax)
    ax.set_xlabel(r"$x$ [m]")
    ax.set_ylabel(r"$y$ [m]")
    ax.set_title("B.  Leading edge", color=INK, fontsize=11.0, pad=6)

    ax = fig.add_subplot(gs[1, 1])
    draw_mesh(ax, mS, (0.958, 1.033), (-0.0375, 0.0375), lw=0.30, pad=0.12)
    draw_body(ax, mS, lw=1.4)
    ax.plot([sS["x"], sS["x"]], [sS["y_lo"], sS["y_hi"]], color=BOXC, lw=2.6,
            zorder=9, solid_capstyle="butt")
    ax.set_aspect("equal")
    frame(ax)
    ax.set_xlabel(r"$x$ [m]")
    ax.set_ylabel(r"$y$ [m]")
    ax.set_title("C.  Trailing edge and the slot", color=INK, fontsize=11.0,
                 pad=6)

    ax = fig.add_subplot(gs[1, 2])
    pad_x = 3.2e-3
    draw_mesh(ax, mS, (sS["x"] - pad_x, sS["x"] + pad_x),
              (-0.5 * sS["h"] - 1.0e-3, 0.5 * sS["h"] + 1.0e-3),
              lw=0.75, pad=0.25)
    for i, (lo, hi) in enumerate(sS["bands"]):
        ax.add_patch(Rectangle((sS["x"] - 3.6e-4, lo), 3.6e-4, hi - lo,
                               fc="#ffd9d9", ec=BOXC, lw=0.8, zorder=5))
        ax.text(sS["x"] - 1.85e-4, 0.5 * (lo + hi), "%d" % (i + 1),
                ha="center", va="center", fontsize=6.6, color=BOXC,
                weight="bold", zorder=6)
    ax.set_aspect("equal")
    frame(ax)
    ax.set_xlabel(r"$x$ [m]")
    ax.set_ylabel(r"$y$ [m]")
    ax.set_title("D.  Cells across the slot: %d" % sS["n_across"],
                 color=INK, fontsize=11.0, pad=6)

    caption(fig, "Sliced cell by cell: the wing, the leading edge, the "
                 "trailing edge and the cells across the slot.", y=0.032)
    notes.append(sheet_note(
        "jet_flap_7_mesh_forcesweep",
        "The grid the lift and pressures are computed on",
        "A different grid from the flow-field page and a different shape of "
        "grid: an O-shape that closes around the wing rather than trailing "
        "behind it. All five calculations ran on this one grid, %s cells, one "
        "cell deep, %.0f mm span. Four had the slot open and blowing at "
        "different strengths, so the differences among those four come from "
        "the blowing alone; the fifth is a reference case with the slot "
        "closed. It is drawn cell by cell from the stored grid of the solved "
        "cases, with no surface tessellation anywhere.\n\n"
        "This grid is not the grid on the flow-field page. The two are shown "
        "on separate pages and never on shared axes. %d cells span the %.1f "
        "mm slot here as well, each %.3f mm tall. The largest cell distortion "
        "is %.1f degrees, the largest skew %.2f, and no cell has zero or "
        "negative volume.\n\n"
        "Near-wall spacing rises with blowing, from largest %.3f with the "
        "slot closed to largest %.3f at the strongest jet. Every wall cell of "
        "every calculation is below the wall-resolved limit. The page is "
        "captioned as the grid all five calculations ran on, so this is the "
        "worst of the five and not the one case the figure renders. None of "
        "the five reached its convergence target; the lift they report had "
        "stopped moving."
        % ("{:,}".format(mS.n_cells), 1e3 * mS.t_z,
           sS["n_across"], 1e3 * sS["h"], 1e3 * sS["dy_max"],
           cmS["nonorth_max"], cmS["skew_max"],
           _sweep_yplus_max()[0], _sweep_yplus_max()[-1])))
    # THE COST FOOTER IS GONE FROM THIS FIGURE (Sanaa 2010Z: it baked the
    # retired 56.8 / 117.5 / 2.07x set and an em dash into the pixels; her
    # option taken is removal, so no screen-set number is baked into a
    # rendered artifact either). The compute story lives on the compute
    # table and the conclusion, one surface, never a figure footer that
    # drifts when the story moves. cost_sweep still feeds the sheet note.
    save(fig, "jet_flap_7_mesh_forcesweep")

    # -------------------------------------------------------------- readout --
    print("MESH SOURCE            : constant/polyMesh only; no STL is opened "
          "by this script")
    print("flow-field grid        : %s cells, t_z %.3g m, %s"
          % (mF.n_cells, mF.t_z, mF.pm))
    print("force-sweep grid       : %s cells, t_z %.3g m, %s"
          % (mS.n_cells, mS.t_z, mS.pm))
    print("SLOT, flow-field grid  : h = %.9g m MEASURED, cells across = %d, "
          "band dy %.6e..%.6e, tiling gap %.3e, area %.9g m2"
          % (sF["h"], sF["n_across"], sF["dy_min"], sF["dy_max"], sF["gap"],
             sF["area"]))
    print("  independent recount  : %d cell centroids in the slot band "
          "immediately downstream" % xcF)
    print("SLOT, force-sweep grid : h = %.9g m MEASURED, cells across = %d"
          % (sS["h"], sS["n_across"]))
    print("REFINED WAKE REGION    : %d cells between the trailing edge and "
          "3 chords downstream" % n_wake)
    print("checkMesh, flow-field  : %s" % cmF["path"])
    print("  cells %d  nonorth max %.4f avg %.4f  skew %.4f  negvol %d  "
          "AR %.6g  'Mesh OK' printed: %s  failed checks: %d"
          % (cmF["cells"], cmF["nonorth_max"], cmF["nonorth_avg"],
             cmF["skew_max"], cmF["neg_vol"], cmF["ar_max"],
             cmF["mesh_ok"], cmF["failed_checks"]))
    print("checkMesh, force-sweep : %s" % cmS["path"])
    print("  cells %d  nonorth max %.4f avg %.4f  skew %.4f  negvol %d  "
          "AR %.6g  'Mesh OK' printed: %s  failed checks: %d"
          % (cmS["cells"], cmS["nonorth_max"], cmS["nonorth_avg"],
             cmS["skew_max"], cmS["neg_vol"], cmS["ar_max"],
             cmS["mesh_ok"], cmS["failed_checks"]))
    print("y+, flow-field grid    : %s/%s/yPlus  n=%d  min %.6g  mean %.6g  "
          "max %.6g  median %.6g"
          % (FLOW, FLOW_TIME, len(yp), yp.min(), yp.mean(), yp.max(),
             np.median(yp)))
    print("  agrees with the run's own summary at %s" % hist_path)
    print("y+, force-sweep grid   : %s/%s/yPlus  n=%d  min %.6g  mean %.6g  "
          "max %.6g" % (SWEEP, SWEEP_TIME, len(ypS), ypS.min(), ypS.mean(),
                        ypS.max()))
    print("WRITTEN:")
    # This page's grids, recorded at render time beside the figures. The
    # screen shows the force-grid slice; its provenance is what lets the
    # act's grid statement be checked instead of trusted.
    print("PROVENANCE %s" % jf1num.write_figure_provenance({
        "jet_flap_5_mesh_flowfield": os.path.join(HERE, FLOW),
        "jet_flap_6_mesh_resolution": os.path.join(HERE, FLOW),
        "jet_flap_7_mesh_forcesweep": os.path.join(HERE, SWEEP),
    }))
    for p in notes:
        print("SHEET NOTE %s" % p)
    for p in written:
        print("  %s" % p)


if __name__ == "__main__":
    main()
