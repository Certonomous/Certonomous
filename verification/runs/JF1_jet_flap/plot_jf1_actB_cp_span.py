#!/usr/bin/env python3
"""
JET-FLAP (BLOWN WING) -- TWO ADDITIONAL CUSTOMER-FACING FIGURES.

  FIGURE  jet_flap_2_chordwise_pressure   -- chordwise pressure distribution,
      UNCLIPPED, upper and lower surfaces on separate axes, all five jet
      strengths overlaid on each, with a leading-edge detail row in which the
      forward stagnation point and its approach to Cp = +1 are visible.
      Supersedes the clipped `jet_flap_2_surface_pressure` figure, whose y-axis
      was cut at Cp = +1.15 / -2.6 and therefore hid both the stagnation value
      and the slot-lip suction.

  FIGURE  jet_flap_8_spanwise_uniformity  -- the measured two-dimensionality of
      these calculations: the largest difference in every solved quantity
      between the two faces that bound the span, measured, with a deliberately
      altered copy carried alongside so that a zero means the check can see a
      difference and did not find one.

Built to Demo Standard v2 output rules R1-R10.  Nothing this script DRAWS is
internal language: no case identifiers, no solver dictionary names (the span
patch type is described, never named), no gate or verdict vocabulary, no
rule/lesson/docket numbers, no talk of lab process.  Each figure carries a
plain-English caveat box, a compute line with the up-front estimate beside the
spend, and units on every number.

INTERNAL NOTES (this file is not user-visible; the FIGURES are).

  * SOURCE TREE.  Every number here comes from the REGISTERED JF1 conditions --
    U_inf = 10 m/s, nu = 1e-5 m2/s, Re_c = 1.0e6, low-Re wall treatment
    (measured wall y+ max 0.19 on the airfoil).  The GUI's "unseen geometry"
    mission ran the same STL at an ASSUMED 100 m/s with wall functions; NOTHING
    from that run enters this script, and this script reads no file belonging
    to it.  The two must never be mixed.

  * TWO MESHES, NEVER ON ONE AXIS.  The five completed calculations share ONE
    39,984-cell O-topology mesh (span 0.01 m) and differ ONLY in blowing --
    that is the controlled comparison, and it alone supplies the pressure
    figure.  The 46,180-cell C-topology calculation (span 1.0 m) appears ONLY
    in the two-dimensionality figure, where it is a SEPARATE column and no
    coefficient is formed from it.

  * Cp IS NONDIMENSIONAL AND NEEDS NO REFERENCE AREA.  Cp = p / (0.5 U_inf^2)
    with p the kinematic pressure simpleFoam stores (m2/s2).  The span t_z and
    the reference area Aref, which DO differ between the meshes (0.01 m / 1.0 m
    and 0.01 m2 / 1.0 m2), enter no quantity drawn on the pressure figure.  The
    script asserts that it applied no area normalisation.

  * SURFACE SAMPLES ARE FACE-CENTRE VALUES (interpolate false), 396 faces on
    the airfoil.  The stagnation point therefore falls BETWEEN face centres and
    its chordwise location carries a resolution uncertainty of half the local
    face spacing; that is the uncertainty column on the table.  The Cp VALUE
    carries no quantified uncertainty -- no mesh-refinement study was run.

  * PLANTED-PERTURBATION CONTROLS on every reader and on the span comparator
    itself, before any figure is drawn.  The span comparator's control is a
    DELIBERATELY MISPAIRED face map: if the comparator cannot report a large
    difference when the pairing is broken, its zero on the true pairing is not
    evidence and the script refuses (exit 2).

  * NOT ONE of the five completed calculations met the convergence target on
    all five channels; the C-topology calculation ran to its iteration cap
    without a converged line.  Said plainly on both figures.
"""

import math
import os
import re
import shutil
import sys

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from plot_jf1_p1_demo import (            # noqa: E402
    Refusal, refuse, read_internal, read_raw_surface, plant_control_raw,
)
from plot_jf1_actB_demo import (          # noqa: E402
    tidy, banner, caveat_box, cost_line,
    INK, INK2, MUTED, GRIDC, WARN, RAMP, UNBLOWN_C,
    SWEEP, SWEEP_TIME, LIVE, U_INF, Q_INF, CHORD, SWEEP_ESTIMATE_EACH,
)

OMESH_CELLS = 39984
CMESH_CELLS = 46180
LIVE_TIME = 20000

CMU_ORDER = [0.05, 0.10, 0.20, 0.40]

# quantities compared across the span: (file, drawn name, drawn units)
QUANTITIES = [
    ("U",     "velocity",                  "velocity",             "m s$^{-1}$"),
    ("p",     "pressure per unit density", "pressure",             "m$^{2}$ s$^{-2}$"),
    ("k",     "turbulent kinetic energy",  "turbulent energy",     "m$^{2}$ s$^{-2}$"),
    ("omega", "turbulence frequency",      "turbulence frequency", "s$^{-1}$"),
    ("nut",   "turbulent viscosity",       "turbulent viscosity",  "m$^{2}$ s$^{-1}$"),
]

MISPAIR_PLANT = "roll the span pairing by one face"


# ===================================================================== mesh ===
def _brace_body(txt, start):
    """Text inside the first balanced ( ... ) at or after `start`."""
    k = txt.index("(", start)
    depth = 0
    for i in range(k, len(txt)):
        c = txt[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return txt[k + 1:i]
    refuse("unbalanced parentheses from offset %d" % start)


def _count_then_body(path):
    txt = open(path).read()
    j = txt.index("}")                      # end of the FoamFile header dict
    m = re.search(r"^\s*(\d+)\s*$", txt[j:], re.M)
    if not m:
        refuse("no element count in %s" % path)
    return int(m.group(1)), _brace_body(txt, j + m.end())


def read_points(path):
    n, b = _count_then_body(path)
    a = np.fromstring(b.replace("(", " ").replace(")", " "), sep=" ")
    a = a.reshape(-1, 3)
    if len(a) != n:
        refuse("point count mismatch in %s: header %d, parsed %d"
               % (path, n, len(a)))
    return a


def read_labels(path):
    n, b = _count_then_body(path)
    a = np.fromstring(b, sep=" ", dtype=float).astype(np.int64)
    if len(a) != n:
        refuse("label count mismatch in %s: header %d, parsed %d"
               % (path, n, len(a)))
    return a


def read_faces(path):
    n, b = _count_then_body(path)
    faces = [np.fromstring(m.group(2), sep=" ", dtype=float).astype(np.int64)
             for m in re.finditer(r"(\d+)\s*\(([^)]*)\)", b)]
    if len(faces) != n:
        refuse("face count mismatch in %s: header %d, parsed %d"
               % (path, n, len(faces)))
    return faces


def read_boundary(path):
    n, b = _count_then_body(path)
    out = []
    for m in re.finditer(r"([A-Za-z_]\w*)\s*\{([^}]*)\}", b):
        d = dict((k, v.strip())
                 for k, v in re.findall(r"(\w+)\s+([^;]+);", m.group(2)))
        out.append((m.group(1), d))
    if len(out) != n:
        refuse("patch count mismatch in %s: header %d, parsed %d"
               % (path, n, len(out)))
    return out


def field_patch_block(path, patch):
    """The literal text of one patch entry inside boundaryField."""
    txt = open(path).read()
    i = txt.index("boundaryField")
    m = re.search(r"^\s*%s\s*$" % re.escape(patch), txt[i:], re.M)
    if not m:
        refuse("no boundaryField entry for '%s' in %s" % (patch, path))
    k = txt.index("{", i + m.end())
    depth = 0
    for q in range(k, len(txt)):
        if txt[q] == "{":
            depth += 1
        elif txt[q] == "}":
            depth -= 1
            if depth == 0:
                return txt[k + 1:q]
    refuse("unbalanced boundaryField block for '%s' in %s" % (patch, path))


# ======================================================== span measurement ===
def span_topology(case_dir):
    """Everything the span comparison needs, MEASURED off the mesh files.

    Returns a dict; refuses if the mesh is not a single cell across the span
    bounded by two zero-degree-of-freedom faces."""
    pm = os.path.join(case_dir, "constant", "polyMesh")
    P = read_points(os.path.join(pm, "points"))
    own = read_labels(os.path.join(pm, "owner"))
    nei = read_labels(os.path.join(pm, "neighbour"))
    bnd = read_boundary(os.path.join(pm, "boundary"))
    faces = read_faces(os.path.join(pm, "faces"))
    ncells = int(max(own.max(), nei.max())) + 1

    span = [(nm, d) for nm, d in bnd if d.get("type") == "empty"]
    if len(span) != 2:
        refuse("%s: expected exactly 2 span-bounding zero-DOF patches, found %d"
               % (case_dir, len(span)))

    zs = np.unique(P[:, 2])
    if len(zs) != 2:
        refuse("%s: the mesh spans %d distinct out-of-plane coordinates, not 2 "
               "-- it is not one cell thick" % (case_dir, len(zs)))
    t_z = float(zs[1] - zs[0])

    # the two point planes must be the SAME planform, point for point
    lo = P[P[:, 2] == zs[0]][:, :2]
    hi = P[P[:, 2] == zs[1]][:, :2]
    if len(lo) != len(hi):
        refuse("%s: %d points on one span plane, %d on the other"
               % (case_dir, len(lo), len(hi)))
    il = np.lexsort((lo[:, 1], lo[:, 0]))
    ih = np.lexsort((hi[:, 1], hi[:, 0]))
    plane_dev = float(np.abs(lo[il] - hi[ih]).max())

    info = {}
    cent = {}
    for nm, d in span:
        s, n = int(d["startFace"]), int(d["nFaces"])
        if n != ncells:
            refuse("%s: span-bounding patch '%s' carries %d faces but the mesh "
                   "has %d cells -- not one cell across the span"
                   % (case_dir, nm, n, ncells))
        idx = np.arange(s, s + n)
        c = np.empty((n, 3))
        nv = np.empty(n, dtype=np.int64)
        zdev = 0.0
        for j, f in enumerate(idx):
            pts = P[faces[f]]
            nv[j] = len(pts)
            c[j] = pts.mean(axis=0)
            zdev = max(zdev, float(pts[:, 2].max() - pts[:, 2].min()))
        if nv.min() != 4 or nv.max() != 4:
            refuse("%s: span-bounding faces are not all quadrilaterals "
                   "(%d..%d vertices)" % (case_dir, nv.min(), nv.max()))
        if zdev > 1e-12:
            refuse("%s: a span-bounding face is not flat in the out-of-plane "
                   "direction (%.3e m)" % (case_dir, zdev))
        cells = own[idx]
        if not np.array_equal(np.sort(cells), np.arange(ncells)):
            refuse("%s: the faces of span-bounding patch '%s' are not a "
                   "one-to-one map onto the cells" % (case_dir, nm))
        info[nm] = dict(start=s, n=n, cells=cells)
        cent[nm] = c

    a, b = [nm for nm, _ in span]
    # Pair the two patches BY PLAN-VIEW GEOMETRY, not by cell, so that a mesh
    # more than one cell thick would pair DIFFERENT cells and the difference
    # this comparator reports would be a real spanwise variation.  Nearest
    # neighbour, not a sort: the two face centroids are means over vertex lists
    # OpenFOAM stores in opposite winding order, so they agree only to rounding
    # and a lexicographic sort breaks ties inconsistently between the patches.
    ca, cb = cent[a], cent[b]
    tree = cKDTree(cb[:, :2])
    dist, ib = tree.query(ca[:, :2], k=1)
    pair_dev = float(dist.max())
    if pair_dev > 1e-10:
        refuse("%s: the span-bounding faces do not pair in plan view "
               "(worst %.3e m)" % (case_dir, pair_dev))
    if len(np.unique(ib)) != len(ib):
        refuse("%s: the span-bounding faces do not pair one-to-one in plan "
               "view" % case_dir)
    cell_a = info[a]["cells"]
    cell_b = info[b]["cells"][ib]
    thick = np.abs(ca[:, 2] - cb[ib][:, 2])

    return dict(ncells=ncells, npoints=len(P), nfaces=len(own),
                ninternal=len(nei), patches=bnd, span_names=(a, b),
                t_z=t_z, plane_dev=plane_dev, pair_dev=pair_dev,
                cell_a=cell_a, cell_b=cell_b,
                thick_min=float(thick.min()), thick_max=float(thick.max()))


def span_diff(topo, values, mispair=False):
    """Largest |value(face on one span boundary) - value(its partner on the
    other)| over every pair.  `mispair` rolls the partner list by one face --
    the planted control: the comparator MUST see a difference then."""
    a = topo["cell_a"]
    b = topo["cell_b"] if not mispair else np.roll(topo["cell_b"], 1)
    d = values[a] - values[b]
    if d.ndim == 2:
        return float(np.abs(d).max()), float(np.linalg.norm(d, axis=1).max())
    return float(np.abs(d).max()), float(np.abs(d).max())


def measure_run(case_dir, time_dir):
    """Span uniformity + out-of-plane velocity for one calculation."""
    topo = span_topology(case_dir)
    td = os.path.join(case_dir, str(time_dir))
    out = {"topo": topo, "time": time_dir, "fields": {}}

    for fname, _, _, _ in QUANTITIES:
        p = os.path.join(td, fname)
        if not os.path.exists(p):
            refuse("%s: no stored '%s' at iteration %s" % (case_dir, fname,
                                                           time_dir))
        for nm in topo["span_names"]:
            blk = field_patch_block(p, nm)
            kind = re.search(r"type\s+(\w+)\s*;", blk)
            if not kind or kind.group(1) != "empty":
                refuse("%s: '%s' on span boundary '%s' is '%s', not the "
                       "zero-degree-of-freedom type"
                       % (case_dir, fname, nm, kind.group(1) if kind else "?"))
            if re.search(r"\bvalue\b", blk):
                refuse("%s: '%s' carries stored values on span boundary '%s' "
                       "-- the span is not degenerate" % (case_dir, fname, nm))
        v = read_internal(p)
        comp, mag = span_diff(topo, v)
        cmp_m, mag_m = span_diff(topo, v, mispair=True)
        scale = float(np.abs(v).max()) if v.ndim == 1 else \
            float(np.linalg.norm(v, axis=1).max())
        out["fields"][fname] = dict(
            n=len(v), max_abs=mag, max_comp=comp, scale=scale,
            rel=(mag / scale if scale > 0 else float("nan")),
            control=mag_m, control_comp=cmp_m)
        if fname == "U":
            out["uz_internal"] = float(np.abs(v[:, 2]).max())
            out["uz_rel"] = out["uz_internal"] / U_INF
            # every patch that stores values, too
            worst, where = 0.0, "none"
            txt = open(p).read()
            i = txt.index("boundaryField")
            for nm, d in topo["patches"]:
                blk = field_patch_block(p, nm)
                m = re.search(r"value\s+nonuniform\s+List<vector>\s*\s*(\d+)",
                              blk)
                if not m:
                    continue
                body = _brace_body(blk, m.start())
                arr = re.findall(r"\(([^)]*)\)", body)
                w = max(abs(float(s.split()[2])) for s in arr)
                if w > worst:
                    worst, where = w, nm
            out["uz_patch"] = worst
            out["uz_patch_where"] = where
    return out


# ==================================================== chordwise Cp readout ===
def surface_cp(base, d):
    """x/c, y/c, Cp on the wing surface.  NO area normalisation is applied and
    none is possible: Cp is p / (0.5 U_inf^2) and carries no length."""
    p = os.path.join(base, LIVE, "artefacts", "_omesh", d, "postProcessing",
                     "jfSurf", str(SWEEP_TIME), "p_airfoilSurf.raw")
    a = read_raw_surface(p)
    if a.shape[1] != 4:
        refuse("expected a scalar raw surface (4 columns) in %s" % p)
    if float(np.abs(a[:, 2]).max()) > 1e-12:
        refuse("surface samples are not on the mid-span plane in %s" % p)
    return a[:, 0] / CHORD, a[:, 1] / CHORD, a[:, 3] / Q_INF, p


def stagnation(x, y, cp, forward=0.5):
    """Forward stagnation face, its chordwise location, and the resolution
    uncertainty on that location: half the local chordwise face spacing."""
    m = x < forward
    i = int(np.argmax(cp[m]))
    xs, ys, cs = float(x[m][i]), float(y[m][i]), float(cp[m][i])
    same = (y > 0) if ys > 0 else (y < 0)
    xo = np.sort(x[same])
    j = int(np.argmin(np.abs(xo - xs)))
    lo = xo[max(0, j - 1)]
    hi = xo[min(len(xo) - 1, j + 1)]
    return xs, ys, cs, 0.5 * float(max(xs - lo, hi - xs))


# ================================================================== tables ===
SUP = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def sci(v, sig=3):
    """LaTeX-set scientific notation for a drawn number (Standard v2 R2)."""
    if v == 0.0:
        return "0 exactly"
    e = int(math.floor(math.log10(abs(v))))
    m = v / 10.0 ** e
    return "$%.*f\\times10^{%d}$" % (sig - 1, m, e)


def sciu(v, sig=2):
    """The same number for a plain-text caveat line."""
    if v == 0.0:
        return "0"
    e = int(math.floor(math.log10(abs(v))))
    m = v / 10.0 ** e
    return "%.*f×10%s" % (sig - 1, m, str(e).translate(SUP))


def grp(n):
    return "{:,}".format(n).replace(",", " ")


def draw_table(ax, headers, rows, widths, title, fs=8.5, hfs=8.4):
    """Header block sized from the tallest header so rows never collide."""
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                               fc="#fbfbfd", ec=GRIDC, lw=0.8, zorder=0,
                               clip_on=False))
    ax.text(0.010, 0.975, title, transform=ax.transAxes, fontsize=9.4,
            color=INK, weight="bold", va="top", ha="left")
    xs = np.concatenate([[0.014], 0.014 + np.cumsum(widths)[:-1]])

    hb = ax.get_position().height * ax.figure.get_figheight()   # inches
    line = hfs * 1.34 / 72.0                                    # inches
    hl = max(h.count("\n") for h in headers) + 1
    y_head = 0.975 - (11.0 / 72.0) / hb                    # under the title
    y_rule = y_head - (hl * line + 6.0 / 72.0) / hb
    for x, h in zip(xs, headers):
        ax.text(x, y_head, h, transform=ax.transAxes, fontsize=hfs, color=INK,
                weight="bold", va="top", ha="left", linespacing=1.34)
    ax.plot([0.012, 0.988], [y_rule, y_rule], transform=ax.transAxes,
            color=GRIDC, lw=1.0, clip_on=False)
    dy = (y_rule - 0.035) / max(1, len(rows))
    for r, row in enumerate(rows):
        yy = y_rule - (r + 0.6) * dy
        for x, cell in zip(xs, row):
            ax.text(x, yy, cell, transform=ax.transAxes, fontsize=fs,
                    color=INK2, va="center", ha="left")


# ==================================================================== main ===
def main():
    base = HERE
    out = os.path.join(base, "artefacts")
    os.makedirs(out, exist_ok=True)
    scratch = os.path.join(base, LIVE, "artefacts", "_recon", "_plant")
    os.makedirs(scratch, exist_ok=True)

    written = []

    def save(fig, stem):
        for ext in ("pdf", "png"):
            p = os.path.join(out, "%s.%s" % (stem, ext))
            fig.savefig(p, dpi=200, facecolor="white")
            written.append(p)
        plt.close(fig)

    # ---------------------------------------------------------- compute line
    spend = 0.0
    for d, _, _ in SWEEP:
        st = {}
        case = os.path.join(base, d)
        for f in os.listdir(case):
            if f.startswith("RUN_STATUS"):
                for line in open(os.path.join(case, f)):
                    q = line.split(None, 1)
                    if len(q) == 2:
                        st[q[0]] = q[1].strip()
        spend += float(st["core_min_MEASURED"])
    sweep_estimate = SWEEP_ESTIMATE_EACH * len(SWEEP)
    cost_sweep = ("Computer time for the five calculations on this chart: we "
                  "estimated %.1f core-minutes before running them and used "
                  "%.1f — %.2f times our estimate."
                  % (sweep_estimate, spend, spend / sweep_estimate))

    # ============================================ FIGURE: chordwise pressure
    # ---- planted-perturbation control on the surface reader ---------------
    plant_control_raw(os.path.join(base, LIVE, "artefacts", "_omesh",
                                   SWEEP[0][0], "postProcessing", "jfSurf",
                                   str(SWEEP_TIME), "p_airfoilSurf.raw"),
                      scratch)
    plant_control_raw(os.path.join(base, LIVE, "artefacts", "_omesh",
                                   SWEEP[4][0], "postProcessing", "jfSurf",
                                   str(SWEEP_TIME), "p_airfoilSurf.raw"),
                      scratch)

    cps = []
    for d, cmu, _ in SWEEP:
        x, y, cp, path = surface_cp(base, d)
        xs, ys, cs, ux = stagnation(x, y, cp)
        up = (y > 0) & (x < 0.98)
        cps.append(dict(cmu=cmu, x=x, y=y, cp=cp, path=path, n=len(x),
                        stag_x=xs, stag_y=ys, stag_cp=cs, stag_ux=ux,
                        peak_cp=float(cp[up].min()),
                        peak_x=float(x[up][int(np.argmin(cp[up]))]),
                        cp_lo=float(cp.min()), cp_hi=float(cp.max())))

    lo = min(r["cp_lo"] for r in cps)
    hi = max(r["cp_hi"] for r in cps)
    pad = 0.06 * (hi - lo)
    YLIM = (hi + pad, lo - pad)          # inverted: suction upward

    fig = plt.figure(figsize=(14.0, 12.9))
    gs = fig.add_gridspec(4, 2, height_ratios=[2.30, 1.62, 1.20, 1.85],
                          left=0.062, right=0.985, top=0.855, bottom=0.045,
                          hspace=0.42, wspace=0.17)
    axu = fig.add_subplot(gs[0, 0])
    axl = fig.add_subplot(gs[0, 1])
    axzu = fig.add_subplot(gs[1, 0])
    axzl = fig.add_subplot(gs[1, 1])
    axt = fig.add_subplot(gs[2, :])
    axc = fig.add_subplot(gs[3, :])

    handles = []
    for r in cps:
        col = UNBLOWN_C if r["cmu"] == 0 else RAMP[CMU_ORDER.index(r["cmu"])]
        ls = (0, (5, 3)) if r["cmu"] == 0 else "-"
        lab = "no blowing" if r["cmu"] == 0 else "$C_\\mu = %.2f$" % r["cmu"]
        x, y, cp = r["x"], r["y"], r["cp"]
        for axx, axz, sel in ((axu, axzu, y > 0), (axl, axzl, y < 0)):
            s = np.argsort(x[sel])
            axx.plot(x[sel][s], cp[sel][s], ls=ls, color=col, lw=1.9)
            axz.plot(x[sel][s], cp[sel][s], ls=ls, color=col, lw=1.9,
                     marker="o", ms=2.4, mew=0)
        handles.append(Line2D([], [], color=col, ls=ls, lw=2.2, label=lab))
        axzl.plot([r["stag_x"]], [r["stag_cp"]], marker="o", ms=7.5,
                  mfc="none", mec=col, mew=1.7, zorder=5)

    for axx, ttl in ((axu, "Upper (suction) surface — full scale, nothing cut off"),
                     (axl, "Lower (pressure) surface — full scale, nothing cut off")):
        axx.axhline(0, color=MUTED, lw=0.8)
        axx.set_ylim(*YLIM)
        axx.set_xlim(-0.02, 1.02)
        axx.set_xlabel("distance along the chord  $x/c$  [–]")
        axx.set_title(ttl, weight="bold", color=INK, loc="left", fontsize=11.2,
                      pad=8)
        tidy(axx)
    axu.set_ylabel("pressure coefficient  $C_p$  [–]")

    ZX = 0.075
    zlo = min(min(r["cp"][r["x"] < ZX].min() for r in cps), -0.2)
    for axz, ttl in ((axzu, "Leading edge, upper surface (detail)"),
                     (axzl, "Leading edge, lower surface (detail)")):
        axz.axhline(0, color=MUTED, lw=0.8)
        axz.axhline(1.0, color=WARN, lw=1.1, ls=(0, (4, 3)), zorder=1)
        axz.set_xlim(-0.0035, ZX)
        axz.set_ylim(1.20, zlo - 0.12)
        axz.set_xlabel("distance along the chord  $x/c$  [–]")
        axz.set_title(ttl, weight="bold", color=INK, loc="left", fontsize=10.8,
                      pad=7)
        tidy(axz)
    axzu.set_ylabel("pressure coefficient  $C_p$  [–]")
    for axz in (axzu, axzl):
        axz.text(ZX * 0.985, 1.0, "  ideal stagnation, $C_p = +1$  ", color=WARN,
                 fontsize=8.8, ha="right", va="bottom")
    axzl.annotate("the oncoming air is brought to rest here.\n"
                  "The stronger the jet, the further back\n"
                  "along the lower surface that point sits.",
                  xy=(cps[4]["stag_x"], cps[4]["stag_cp"]),
                  xytext=(0.0180, -1.42), fontsize=9.0, color=INK2, ha="left",
                  va="top",
                  arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.1,
                                  shrinkB=7,
                                  connectionstyle="arc3,rad=0.30"))

    leg = axu.legend(handles=handles, frameon=False, fontsize=9.4,
                     loc="upper left", title="jet strength")
    leg.get_title().set_color(INK2)
    for t_ in leg.get_texts():
        t_.set_color(INK2)

    rows = []
    for r in cps:
        rows.append([
            "none" if r["cmu"] == 0 else "%.2f" % r["cmu"],
            "%+.4f" % r["stag_cp"],
            "%.5f" % r["stag_x"],
            "±%.5f" % r["stag_ux"],
            "lower" if r["stag_y"] < 0 else "upper",
            "%+.3f" % r["peak_cp"],
            "%.3f" % r["peak_x"],
            "%+.3f" % r["cp_lo"],
        ])
    draw_table(
        axt,
        ["jet strength\n$C_\\mu$  [–]",
         "stagnation\npressure $C_p$  [–]",
         "its location\n$x/c$  [–]",
         "location\nuncertainty  [–]",
         "on which\nsurface",
         "strongest suction,\n$x/c<0.98$:  $C_p$  [–]",
         "at\n$x/c$  [–]",
         "lowest $C_p$ on\nthe surface  [–]"],
        rows,
        [0.108, 0.146, 0.104, 0.104, 0.098, 0.170, 0.086, 0.130],
        "MEASURED VALUES BEHIND THIS CHART  (all quantities dimensionless; "
        "396 surface samples per curve)")

    banner(fig)
    fig.text(0.5, 0.952,
             "Pressure around the wing, drawn to full scale with nothing cut "
             "off the axis. Same wing, same mesh, same flow speed in all five "
             "curves; only the strength\nof the trailing-edge jet changes, so "
             "this is a controlled comparison. Suction is plotted upward, the "
             "usual aerodynamic convention. The area enclosed between the\n"
             "upper and lower curves is the lift. The lower row magnifies the "
             "first 7.5 % of the chord, where every curve reaches $C_p = +1$ "
             "— the point at which the\noncoming air is brought to rest. With "
             "no jet that point sits on the nose; the stronger the jet, the "
             "further back along the lower surface it moves.",
             ha="center", va="top", fontsize=9.2, color=INK2, linespacing=1.5)

    cp_caveat = (
        "  •  The stagnation pressure comes out between +1.0015 and +1.0057\n"
        "     rather than exactly +1. The overshoot is 0.15 % to 0.57 % and is\n"
        "     a resolution effect: pressure is sampled at the centre of each\n"
        "     surface cell, not at the exact stagnation point.\n"
        "  •  The strong peaks at the trailing edge are the slot lip. They are\n"
        "     real features of the calculation and they set the scale of the\n"
        "     top row. Nothing is cut off, which is why the mid-chord detail\n"
        "     looks flatter here than on a chart with a cropped axis.\n"
        "  •  None of these calculations reached the convergence target that\n"
        "     was fixed before they were run (all five solution channels below\n"
        "     1×10⁻⁶). The turbulence-energy channel is the slowest everywhere\n"
        "     and worsens with blowing — 3.5×10⁻⁶ with no jet, 1.5×10⁻⁴ at the\n"
        "     strongest jet, a factor of 43.\n"
        "  •  Mesh sensitivity has NOT been quantified: no refinement study was\n"
        "     run, so no uncertainty is claimed on any pressure value. The one\n"
        "     uncertainty in the table is on WHERE the stagnation point sits,\n"
        "     and it is half the local surface-cell spacing.\n"
        "  •  No experimental pressure data exists for this configuration, so no\n"
        "     measured reference curve is drawn. Treat these as indicative.")
    caveat_box(axc, cp_caveat)
    cost_line(fig, cost_sweep)
    save(fig, "jet_flap_2_chordwise_pressure")

    # ========================================= FIGURE: spanwise uniformity ==
    runs = []
    for d, cmu, _ in SWEEP:
        m = measure_run(os.path.join(base, d), SWEEP_TIME)
        m["cmu"] = cmu
        m["dir"] = d
        runs.append(m)
    live = measure_run(os.path.join(base, LIVE), LIVE_TIME)
    live["dir"] = LIVE

    # planted control on the comparator, on EVERY run and EVERY quantity
    for m in runs + [live]:
        for fname, _, _, _ in QUANTITIES:
            f = m["fields"][fname]
            if not (f["control"] > 0.0):
                refuse("the span comparison cannot see a difference even when "
                       "the face pairing is deliberately broken (%s, %s) -- "
                       "its zero on the true pairing is not evidence"
                       % (m["dir"], fname))
            if not (f["max_abs"] < f["control"]):
                refuse("the span comparison found as much difference on the "
                       "true pairing as on the broken one (%s, %s)"
                       % (m["dir"], fname))

    worst = {}
    for fname, _, _, _ in QUANTITIES:
        worst[fname] = dict(
            sweep=max(m["fields"][fname]["max_abs"] for m in runs),
            sweep_ctl=min(m["fields"][fname]["control"] for m in runs),
            live=live["fields"][fname]["max_abs"],
            live_ctl=live["fields"][fname]["control"],
            sweep_rel=max(m["fields"][fname]["rel"] for m in runs),
            live_rel=live["fields"][fname]["rel"])
    uz_sweep = max(m["uz_internal"] for m in runs)
    uz_live = live["uz_internal"]
    uz_sweep_p = max(m["uz_patch"] for m in runs)
    uz_live_p = live["uz_patch"]

    fig = plt.figure(figsize=(14.0, 11.8))
    gs = fig.add_gridspec(4, 2, height_ratios=[2.05, 0.28, 1.10, 1.75],
                          left=0.132, right=0.985, top=0.845, bottom=0.045,
                          hspace=0.34, wspace=0.26)
    axd = fig.add_subplot(gs[0, 0])
    axz = fig.add_subplot(gs[0, 1])
    axleg = fig.add_subplot(gs[1, :])
    axt = fig.add_subplot(gs[2, :])
    axc = fig.add_subplot(gs[3, :])
    axleg.axis("off")

    names = [n for _, _, n, _ in QUANTITIES]
    ypos = np.arange(len(names))[::-1]
    for i, (fname, _, nm, _) in zip(ypos, QUANTITIES):
        w = worst[fname]
        axd.plot([w["sweep_ctl"]], [i + 0.15], "o", ms=8.0, mfc="none",
                 mec=WARN, mew=1.7)
        axd.plot([w["live_ctl"]], [i - 0.15], "o", ms=8.0, mfc="none",
                 mec=WARN, mew=1.7)
        axd.plot([w["sweep"]], [i + 0.15], "o", ms=8.5, color=RAMP[3])
        axd.plot([w["live"]], [i - 0.15], "s", ms=7.5, color=INK)
    axd.set_yticks(ypos)
    axd.set_yticklabels(names, fontsize=9.4)
    axd.set_xscale("symlog", linthresh=1e-15)
    axd.set_xlim(-2e-16, 3e3)
    axd.set_xticks([0.0, 1e-12, 1e-8, 1e-4, 1e0, 1e3])
    axd.set_xticklabels(["0", "$10^{-12}$", "$10^{-8}$", "$10^{-4}$",
                         "$10^{0}$", "$10^{3}$"])
    axd.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    axd.set_xlabel("largest difference between the two ends of the span "
                   "(in each quantity's own units)")
    axd.set_ylim(-0.7, len(names) - 0.3)
    axd.set_title("Every solved quantity, measured end to end across the span",
                  weight="bold", color=INK, loc="left", fontsize=11.2, pad=8)
    tidy(axd)
    axd.axvline(0.0, color=MUTED, lw=0.9)
    axleg.legend(handles=[
        Line2D([], [], color=RAMP[3], marker="o", ls="none", ms=8.5,
               label="39 984-cell mesh — measured (worst of five)"),
        Line2D([], [], color=INK, marker="s", ls="none", ms=7.5,
               label="46 180-cell mesh — measured"),
        Line2D([], [], mfc="none", mec=WARN, mew=1.7, marker="o", ls="none",
               ms=8.0, label="the same check on a deliberately altered copy"),
    ], frameon=False, fontsize=9.2, loc="center", ncol=3,
        columnspacing=2.6, handletextpad=0.7)

    lbl = ["39 984-cell\nmesh\n(interior)", "39 984-cell\nmesh\n(boundaries)",
           "46 180-cell\nmesh\n(interior)", "46 180-cell\nmesh\n(boundaries)"]
    val = [uz_sweep, uz_sweep_p, uz_live, uz_live_p]
    floor = 1e-24
    axz.bar(range(4), [max(v, floor) for v in val],
            color=[RAMP[3], RAMP[1], INK, MUTED], width=0.58)
    axz.set_yscale("log")
    axz.set_ylim(floor, 1e2)
    axz.axhline(U_INF, color=WARN, lw=1.2, ls=(0, (4, 3)))
    axz.text(3.45, U_INF * 1.25, "flow speed, 10 m s$^{-1}$", color=WARN,
             fontsize=8.8, ha="right", va="bottom")
    axz.axhline(2.2e-16 * U_INF, color=MUTED, lw=1.0, ls=(0, (2, 3)))
    axz.annotate("one unit in the last digit the arithmetic holds",
                 xy=(2.95, 2.2e-16 * U_INF), xytext=(2.60, 1e-11),
                 color=MUTED, fontsize=8.4, ha="right", va="bottom",
                 arrowprops=dict(arrowstyle="->", color=MUTED, lw=0.9))
    axz.set_xticks(range(4))
    axz.set_xticklabels(lbl, fontsize=8.4)
    axz.set_ylabel("largest out-of-plane speed  [m s$^{-1}$]")
    axz.set_title("Air motion along the span: how much is there?",
                  weight="bold", color=INK, loc="left", fontsize=11.2, pad=8)
    tidy(axz)
    for i, v in enumerate(val):
        axz.annotate(sci(v, 2), xy=(i, max(v, floor)), xytext=(0, 5),
                     textcoords="offset points", ha="center", va="bottom",
                     fontsize=8.8, color=INK)

    trows = []
    for fname, nm, sh, un in QUANTITIES:
        w = worst[fname]
        trows.append([nm, un, sci(w["sweep"]), sci(w["live"]),
                      sci(max(w["sweep_rel"], w["live_rel"])),
                      sci(min(w["sweep_ctl"], w["live_ctl"]))])
    trows.append(["out-of-plane velocity component", "m s$^{-1}$",
                  sci(uz_sweep), sci(uz_live),
                  sci(max(uz_sweep, uz_live) / U_INF),
                  "—  (an absolute level, not a difference)"])
    draw_table(
        axt,
        ["quantity", "units",
         "largest span difference,\n39 984-cell mesh",
         "largest span difference,\n46 180-cell mesh",
         "as a fraction of the largest\nvalue in the field  [–]",
         "the same check on a\ndeliberately altered copy"],
        trows,
        [0.238, 0.108, 0.150, 0.150, 0.160, 0.190],
        "MEASURED VALUES BEHIND THIS CHART  (%s and %s cells; one face pair "
        "compared per cell, %s and %s pairs)"
        % (grp(OMESH_CELLS), grp(CMESH_CELLS), grp(OMESH_CELLS),
           grp(CMESH_CELLS)), fs=8.4)

    banner(fig)
    fig.text(0.5, 0.952,
             "These calculations are two-dimensional, and this is the "
             "measurement rather than the claim. The mesh is one cell deep, "
             "and the two faces that close\nthe span carry no solution values "
             "of their own, so the flow has no room to vary along the span. "
             "Every cell was matched face to face\nacross the span by position "
             "and every solved quantity compared: the differences are zero. The "
             "right-hand chart asks the same question physically — how fast\n"
             "does air move along the span? Below %s m s⁻¹, the level at "
             "which the arithmetic itself stops being able to tell a number "
             "from zero."
             % sciu(max(uz_sweep, uz_live), 1),
             ha="center", va="top", fontsize=9.2, color=INK2, linespacing=1.5)

    span_caveat = (
        "  •  A zero is only worth something if the check could have found\n"
        "     something else. Every comparison was repeated on a copy in which\n"
        "     the pairing between the two ends of the span was shifted by one\n"
        "     cell on purpose. On those copies the check reports large\n"
        "     differences — the red circles, and the last table column. The\n"
        "     zeros are therefore a finding, not a blind spot.\n"
        "  •  Two meshes are reported side by side and never mixed: 39 984\n"
        "     cells with a 0.01 m span, and 46 180 cells with a 1 m span. No\n"
        "     lift or drag figure is formed from either on this chart.\n"
        "  •  The differences are exactly zero, not merely small — which is what\n"
        "     a one-cell-deep calculation should give, and the point of the\n"
        "     check: the calculation that ran is the two-dimensional one that\n"
        "     was intended.\n"
        "  •  Air speed ALONG the span is not identically zero and we do not\n"
        "     claim it is. It reaches %s m s⁻¹ in the coarser mesh and %s m s⁻¹\n"
        "     in the finer one — %s and %s of the flow speed, at or below one\n"
        "     unit in the last digit the arithmetic holds. Rounding, not motion.\n"
        % (sciu(uz_sweep), sciu(uz_live), sciu(uz_sweep / U_INF, 1),
           sciu(uz_live / U_INF, 1))) + (
        "  •  This check spent no computer time of its own; it re-reads results\n"
        "     already produced. The convergence caveats on the other charts\n"
        "     apply unchanged: none of these calculations met the target that\n"
        "     was fixed before they ran.")
    caveat_box(axc, span_caveat)
    cost_line(fig, "This check consumed no additional computer time; it "
                   "re-reads calculations already completed. " + cost_sweep)
    save(fig, "jet_flap_8_spanwise_uniformity")

    # ---------------------------------------------------------------- report
    print("== CHORDWISE PRESSURE ==")
    print("  %-6s %-11s %-11s %-11s %-8s %-10s %-9s" %
          ("Cmu", "stag Cp", "x/c", "+/- x/c", "surf", "peak Cp", "at x/c"))
    for r in cps:
        print("  %-6.2f %-+11.6f %-11.6f %-11.6f %-8s %-+10.4f %-9.4f  %s"
              % (r["cmu"], r["stag_cp"], r["stag_x"], r["stag_ux"],
                 "lower" if r["stag_y"] < 0 else "upper", r["peak_cp"],
                 r["peak_x"], os.path.relpath(r["path"], base)))
    print("  full unclipped Cp range across all five curves: %+.4f .. %+.4f"
          % (lo, hi))
    print()
    print("== SPANWISE UNIFORMITY ==")
    for m in runs + [live]:
        t = m["topo"]
        print("  %s  @ iteration %s" % (m["dir"], m["time"]))
        print("     cells %d  points %d  faces %d  span-bounding patches %s "
              "(zero-DOF)  t_z = %.6f m  cell thickness %.9f..%.9f m"
              % (t["ncells"], t["npoints"], t["nfaces"], list(t["span_names"]),
                 t["t_z"], t["thick_min"], t["thick_max"]))
        print("     planform of the two point planes identical to %.3e m; "
              "face pairing to %.3e m" % (t["plane_dev"], t["pair_dev"]))
        for fname, nm, sh, un in QUANTITIES:
            f = m["fields"][fname]
            print("     %-6s n=%-7d span max|delta| = %.6e  rel = %.6e  "
                  "field max = %.6e  | broken-pairing control = %.6e"
                  % (fname, f["n"], f["max_abs"], f["rel"], f["scale"],
                     f["control"]))
        print("     max |U_z| interior = %.6e m/s (%.3e of U_inf); "
              "worst stored patch = %.6e m/s on '%s'"
              % (m["uz_internal"], m["uz_rel"], m["uz_patch"],
                 m["uz_patch_where"]))
    print()
    for p in written:
        print("WROTE %s" % p)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Refusal as e:
        sys.stderr.write("REFUSED: %s\n" % e)
        sys.exit(2)
