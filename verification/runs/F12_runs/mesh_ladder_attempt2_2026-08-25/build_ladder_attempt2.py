#!/usr/bin/env python3
"""F12 ATTEMPT 2 -- build the replacement RAE 2822 mesh ladder and grade the
FROZEN admission gate A on it.

MESH ONLY.  This script NEVER launches rhoSimpleFoam and contains no call to
it.  Phase 1 stops at gate A; the solver launches only after the cfd supervisor
has personally read the mesh evidence.  The three case directories this script
writes carry NO 0/ fields and NO thermophysicalProperties, so a solver cannot
be started from them by accident.

WHAT IS REPLACED AND WHAT IS NOT
--------------------------------
Replaced: the mesh instrument.  Attempt 1's O-grid mapped the aerofoil surface
onto the far-field circle by PROPORTIONAL ARC LENGTH inside four quarter
blocks, with the block corners at the leading edge, both mid-chord points and
the trailing edge.  That sends the surface station at x/c = 0.5 -- whose
outward normal points at 88.54 deg -- to the far-field point at 135 deg, and
the station at x/c = 0.05 -- normal at 104.6 deg -- to 174.7 deg.  The angle
between the radial grid line and the surface normal IS the near-wall
non-orthogonality, and on attempt 1 it peaks at 70.6 deg near x/c = 0.07.
Because it is a property of the CORRESPONDENCE and not of the spacing it does
not shrink under refinement: attempt 1 measured 70.646 / 70.861 / 72.542 deg
with the over-70 face count scaling 4.03x then 4.00x -- a fixed FRACTION of the
mesh.

Attempt 2 sets the far-field point of every surface station from that station's
own SURFACE NORMAL DIRECTION.  Orthogonality is then DECOUPLED from resolution:
inside a block both the inner (polyLine) and the outer (arc) edge carry the
SAME simpleGrading and the SAME cell count, so the surface -> far-field
correspondence is proportional arc length WHATEVER the grading is.  The
near-wall misalignment therefore depends only on WHERE THE BLOCK CORNERS ARE
and WHAT OUTER ANGLE EACH CORNER IS GIVEN -- never on the cell counts or the
gradings, which are free to serve resolution and cannot move the gate.

NOT replaced: gate A, gate B, gates 1-4, their thresholds, the caps, the
labels, the PASS rule, the cell counts (23,040 / 92,160 / 368,640), the
far-field radius, the wake length, the patch names, the patch face assignment,
the wall-normal first-cell anchoring (2.0e-6 / 1.0e-6 / 5.0e-7 chord) or the
y+ convention.  None of them is read from this file; they are quoted from the
frozen pre-registration blob and asserted against it before anything is built.

The frozen document is NOT edited and NOT imported from the working tree: it is
read from the HEAD blob and its sha asserted.  sdk/workflows/rae2822_case9.py
is imported READ-ONLY, for the section spline, the checkMesh parser, the
first-cell anchors and the schemes/solution dictionaries.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time

import numpy as np

REPO = pathlib.Path("/home/ubuntu/Certonomous")
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "sdk"))

from sdk.workflows import rae2822_case9 as W                     # noqa: E402
from sdk.workflows.tmr_verification import _foam, _foam_header   # noqa: E402
from sdk.workflows.tmr_verification import ratio_for_first_cell  # noqa: E402

SELF_REL = ("verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25/"
            "build_ladder_attempt2.py")
HERE = REPO / "verification/runs/F12_runs/mesh_ladder_attempt2_2026-08-25"
PREREG = "verification/campaign/F12_PREREGISTRATION.md"
PREREG_BLOB = "080303c57aee52849bb625579565a84ca5469717"

# --- frozen quantities, asserted against the HEAD blob before anything is built
GATE_A_NONORTHO = 70.0
GATE_A_SKEWNESS = 4.0
CELLS_FROZEN = (23040, 92160, 368640)
FARFIELD_R = 50.0
WAKE_LEN = 50.0
FIRST_CELL_ANCHOR = 2.0e-6
YPLUS_PER_CHORD = 2.330e5     # frozen amendment section 6, full-height convention
YPLUS_LE_FACTOR = 1.709       # frozen amendment section 6, ESTIMATED, not gated

# --- the replacement recipe, LEVEL-INDEPENDENT ------------------------------
# Block-corner chordwise stations.  Chosen for RESOLUTION and for one stated
# STRUCTURAL requirement -- the trailing-edge-adjacent block must span at least
# 0.40 chord, so its far-field arc is not degenerate (see DESIGN_CRITERION_DEG).
CORNER_X = (0.0, 0.0025, 0.01, 0.03, 0.08, 0.18, 0.35, 0.55, 1.0)
# Strict-monotonicity blend for the surface-normal angle.  The RAE 2822 lower
# surface is CONCAVE aft of x/c ~ 0.7, so its outward-normal angle is NOT
# monotone; a bare running-max saturates and would emit DEGENERATE blocks with
# zero outer arc.  Blending a fraction of the arc-length-linear map restores
# strict monotonicity.
MONOTONISE_BLEND = 0.30
# Target surface spacing, in arc length, as a function of x/c.  Held FIXED
# across the ladder; only the cell COUNT doubles, so the family is similar.
# DS_MID is not a free knob: it is solved so the surface cell demand comes to
# N_SURF_TOTAL_COARSE, which is what fixes the frozen cell counts.
DS_LE, DS_MID, DS_TE = 8.0e-4, 0.012610, 8.0e-3
# THE DESIGN CRITERION, DECLARED BEFORE THE DESIGN WAS EVALUATED, AND STRICTER
# THAN THE GATE IT IS NOT ALLOWED TO TOUCH.  The frozen gate is 70 deg; this
# recipe is required to predict <= 55 deg at ALL THREE levels on BOTH validated
# predictors, and REFUSES to build otherwise.  Among the configurations meeting
# it, the recipe was selected on RESOLUTION -- the finest trailing-edge spacing
# -- and NOT on gate margin.  The search was run once over a space fixed in
# advance: ds_te in {0.006, 0.008, 0.010, 0.012, 0.014} x blend in {0.20, 0.25,
# 0.30}; 9 of the 15 met the criterion, and the selected point is the smallest
# ds_te among them, at the smallest qualifying blend.  Recorded in
# ATTEMPT2_MESH_REGISTRATION.md.
DESIGN_CRITERION_DEG = 55.0
N_SURF_TOTAL_COARSE = 192     # with n_wake = 48 and ny = 80 this is 23,040 cells
N_POLY = 160                  # geometry polyLine points per block edge
N_GEOM_SAMPLE = 200001        # arc-length / normal-angle sampling per surface
LEVELS = (("coarse", 1, 80, 48), ("medium", 2, 160, 96), ("fine", 4, 320, 192))
# Deterministic decomposition, pinned.  `hierarchical` is SEED-FREE: the
# partition is a pure function of the cell centres, so identical input gives
# identical partitions BY CONSTRUCTION.  `scotch` is NOT used -- this team
# measured it return 12777/12906/12965 and then 12974/12870/12865 on a
# BYTE-IDENTICAL mesh, and that alone decided a convergence verdict.
DECOMP_METHOD = "hierarchical"
DECOMP_N = (2, 2, 1)
DECOMP_RANKS = 4


def abort(msg: str) -> None:
    sys.stderr.write("ABORT: " + msg + "\n")
    raise SystemExit(1)


def git_bytes(*args: str) -> bytes:
    p = subprocess.run(["git", "-C", str(REPO), *args], capture_output=True)
    if p.returncode != 0:
        abort("git " + " ".join(args) + " rc=" + str(p.returncode))
    return p.stdout


# ---------------------------------------------------------------------------
# Geometry: arc length and outward-normal angle on each surface
# ---------------------------------------------------------------------------

def _sample(sec, sign, n=N_GEOM_SAMPLE):
    t = np.linspace(0.0, 1.0, n)
    x = t ** 2
    spline = sec.upper if sign > 0 else sec.lower
    try:                                    # vectorised path
        y = np.asarray(spline._spline(np.sqrt(np.minimum(x, spline._x_max))),
                       dtype=float)
    except Exception:                       # documented fallback, same values
        y = np.array([sec.y(float(v), sign) for v in x])
    s = np.concatenate([[0.0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))])
    dx, dy = np.gradient(x), np.gradient(y)
    nx, ny = -dy, dx
    nn = np.hypot(nx, ny)
    nx, ny = nx / nn, ny / nn
    if sign < 0:
        nx, ny = -nx, -ny
    phi = np.degrees(np.arctan2(ny, nx))
    if sign < 0:
        phi = np.where(phi < 0.0, phi + 360.0, phi)
    return x, y, s, phi


class Correspondence:
    """The surface-station -> far-field-angle map that fixes orthogonality."""

    def __init__(self, sec):
        self.xu, self.yu, self.su, self.phu = _sample(sec, +1.0)
        self.xl, self.yl, self.sl, self.phl = _sample(sec, -1.0)
        self.phum = np.minimum.accumulate(self.phu)      # upper: 180 -> ~58
        self.phlm = np.maximum.accumulate(self.phl)      # lower: 180 -> ~279
        lam = MONOTONISE_BLEND
        linu = 180.0 - (180.0 - self.phum[-1]) * (self.su / self.su[-1])
        self.thu = (1 - lam) * self.phum + lam * linu
        linl = 180.0 + (self.phlm[-1] - 180.0) * (self.sl / self.sl[-1])
        self.thl = (1 - lam) * self.phlm + lam * linl

    def _axes(self, side):
        if side == "u":
            return self.xu, self.yu, self.su, self.phum, self.thu
        return self.xl, self.yl, self.sl, self.phlm, self.thl

    def arc(self, side, x):
        X, _, S, _, _ = self._axes(side)
        return float(np.interp(x, X, S))

    def psi(self, side, s):
        _, _, S, _, TH = self._axes(side)
        if side == "u":
            return 180.0 - 90.0 * (180.0 - np.interp(s, S, TH)) / (180.0 - TH[-1])
        return 180.0 + 90.0 * (np.interp(s, S, TH) - 180.0) / (TH[-1] - 180.0)

    def normal_angle(self, side, s):
        _, _, S, PH, _ = self._axes(side)
        return float(np.interp(s, S, PH))

    def point(self, side, s):
        X, Y, S, _, _ = self._axes(side)
        return float(np.interp(s, S, X)), float(np.interp(s, S, Y))


def ds_target(x):
    x = np.asarray(x, dtype=float)
    return (DS_MID + (DS_LE - DS_MID) * np.exp(-x / 0.03)
            + (DS_TE - DS_MID) * np.exp(-(1.0 - x) / 0.10))


def plan_blocks(corr):
    """The level-independent surface-block plan.

    The UPPER chain runs LE -> TE and the LOWER chain runs TE -> LE.  That
    direction is not cosmetic: with the outward normal as the block's local y,
    only this traversal leaves both chains RIGHT-HANDED, which is the ordering
    attempt 1's four-block dict also used.
    """
    raw = []
    for side in ("u", "l"):
        xs = CORNER_X if side == "u" else tuple(reversed(CORNER_X))
        X, _, S, _, _ = corr._axes(side)
        sc = [corr.arc(side, x) for x in xs]
        sc[0] = 0.0 if side == "u" else float(S[-1])
        sc[-1] = float(S[-1]) if side == "u" else 0.0
        dc = [float(corr.psi(side, s)) for s in sc]
        dc[0] = 180.0 if side == "u" else 270.0
        dc[-1] = 90.0 if side == "u" else 180.0
        for k in range(len(xs) - 1):
            ss = np.linspace(sc[k], sc[k + 1], 4001)
            xx = np.interp(ss, S, X) if side == "u" else np.interp(ss, S, X)
            demand = abs(float(np.trapezoid(1.0 / ds_target(xx), ss)))
            raw.append(dict(side=side, k=k, s_a=sc[k], s_b=sc[k + 1],
                            deg_a=dc[k], deg_b=dc[k + 1],
                            x_a=xs[k], x_b=xs[k + 1], demand=demand))
    n = [max(1, int(math.floor(r["demand"]))) for r in raw]
    rem = [r["demand"] - math.floor(r["demand"]) for r in raw]
    short = N_SURF_TOTAL_COARSE - sum(n)
    for i in sorted(range(len(raw)), key=lambda i: -rem[i])[:max(0, short)]:
        n[i] += 1
    while sum(n) > N_SURF_TOTAL_COARSE:
        j = max(range(len(n)), key=lambda i: (n[i], rem[i]))
        if n[j] <= 1:
            abort("cell budget cannot be met without a zero-cell block")
        n[j] -= 1
    if sum(n) != N_SURF_TOTAL_COARSE:
        abort(f"surface cell budget {sum(n)} != {N_SURF_TOTAL_COARSE}")
    for r, nk in zip(raw, n):
        r["n_coarse"] = nk
        r["grading"] = float(ds_target(r["x_b"]) / ds_target(r["x_a"]))
        if abs(r["deg_b"] - r["deg_a"]) < 1.0e-6:
            abort(f"degenerate block {r['side']}{r['k']}: zero outer arc")
    return raw


def edge_nodes(n, ratio):
    """Fractional arc positions of the n+1 nodes of a simpleGrading edge."""
    if n == 1 or abs(ratio - 1.0) < 1e-12:
        return np.linspace(0.0, 1.0, n + 1)
    r = ratio ** (1.0 / (n - 1))
    c = np.concatenate([[0.0], np.cumsum(r ** np.arange(n))])
    return c / c[-1]


def _cell(block, mult, which):
    n = block["n_coarse"] * mult
    f = edge_nodes(n, block["grading"])
    L = abs(block["s_b"] - block["s_a"])
    return L * float(f[1] - f[0]) if which == "first" else L * float(f[-1] - f[-2])


def predict_nonortho(corr, plan, mult):
    """Predicted max NEAR-WALL non-orthogonality: the angle between the
    straight surface->far-field line and the outward surface normal, at every
    azimuthal cell node.

    PLANTED AGAINST A KNOWN NON-ZERO: run on attempt 1's own four-block
    correspondence this predictor returns 70.608 deg, against the 70.646 deg
    attempt 1's checkMesh MEASURED.  It is a design instrument only; every
    number that gates below comes from a real checkMesh log.
    """
    worst, loc = 0.0, None
    for b in plan:
        for fi in edge_nodes(b["n_coarse"] * mult, b["grading"]):
            s = b["s_a"] + (b["s_b"] - b["s_a"]) * fi
            d = math.radians(b["deg_a"] + (b["deg_b"] - b["deg_a"]) * fi)
            px, py = corr.point(b["side"], s)
            va = math.degrees(math.atan2(FARFIELD_R * math.sin(d) - py,
                                         1.0 + FARFIELD_R * math.cos(d) - px))
            dd = abs((va - corr.normal_angle(b["side"], s) + 180.0) % 360.0 - 180.0)
            if dd > worst:
                worst, loc = dd, (b["side"], b["k"], px)
    return worst, loc


def predict_interface(plan, mult, ny, n_wake, first_cell):
    """Predicted non-orthogonality at the O-ring / wake-block INTERFACE.

    Second, INDEPENDENT failure mode, and the one that actually decided this
    design.  Across the shared radial edge at the trailing edge, an O-ring cell
    is a WEDGE that fans with radius while the wake-block cell is a RECTANGLE.
    A radially graded wedge of height h at radius r carries its centroid
    h^2/(12 r) further out than the node midpoint; the rectangle does not.  That
    centroid offset is a mismatch ALONG the face, and when the two cells are
    thin ACROSS it the centre-to-centre vector tilts hard off the face normal.
    Two fanning cells have the SAME offset and cancel, so this mode lives only
    at the two wake interfaces.

    PLANTED AGAINST A KNOWN NON-ZERO: on the first candidate recipe this
    predictor returned 79.359 deg at the lower trailing edge, against the
    78.5518 deg that mesh's checkMesh MEASURED, and 41.575 deg at the upper
    trailing edge, which is where checkMesh put all 8 of its breaching faces --
    on the LOWER edge only.  A design instrument; every gating number below
    comes from a real checkMesh log.
    """
    r_y = ratio_for_first_cell(FARFIELD_R, ny, first_cell)
    rho = r_y ** (1.0 / (ny - 1))
    dY = FARFIELD_R * (rho - 1.0) ** 2 / (3.0 * (1.0 + rho) ** 2)
    up = [b for b in plan if b["side"] == "u"]
    lo = [b for b in plan if b["side"] == "l"]
    te_b = up[-1]
    te_sp = _cell(te_b, mult, "last")
    r_w = ratio_for_first_cell(WAKE_LEN, n_wake, te_sp)
    w_wake = (FARFIELD_R + WAKE_LEN - 1.0) * float(edge_nodes(n_wake, r_w)[1])
    out = {}
    for tag, b, end in (("upper_TE", te_b, "last"), ("lower_TE", lo[0], "first")):
        n = b["n_coarse"] * mult
        f = edge_nodes(n, b["grading"])
        frac = float(f[1] - f[0]) if end == "first" else float(f[-1] - f[-2])
        arc = abs(b["deg_b"] - b["deg_a"]) * math.pi / 180.0 * FARFIELD_R
        w_ring = arc * frac
        dX = 0.5 * (w_ring + w_wake)
        out[tag] = {"angle_deg": math.degrees(math.atan2(dY, dX)),
                    "w_ring": w_ring, "w_wake": w_wake, "centroid_offset": dY}
    return out


# ---------------------------------------------------------------------------
# blockMeshDict
# ---------------------------------------------------------------------------

def blockmesh_dict(sec, corr, plan, mult, ny, n_wake):
    R, W_OUT = FARFIELD_R, FARFIELD_R + WAKE_LEN
    up = [b for b in plan if b["side"] == "u"]
    lo = [b for b in plan if b["side"] == "l"]
    NB = len(up)

    inner = [corr.point("u", b["s_a"]) for b in up] + [(1.0, 0.0)]
    inner += [corr.point("l", b["s_a"]) for b in lo[1:]]
    iu = list(range(NB + 1))
    il = [NB] + [NB + 1 + j for j in range(NB - 1)] + [0]

    outer_deg = [b["deg_a"] for b in up] + [90.0, 270.0]
    outer_deg += [b["deg_a"] for b in lo[1:]]
    ou = list(range(NB + 1))
    ol = [NB + 1] + [NB + 2 + j for j in range(NB - 1)] + [0]

    OFF = len(inner)
    WK0, WKP, WKM = OFF + len(outer_deg), OFF + len(outer_deg) + 1, OFF + len(outer_deg) + 2
    NV = WKM + 1

    def op(deg):
        r = math.radians(deg)
        return (1.0 + R * math.cos(r), R * math.sin(r))

    verts = list(inner) + [op(d) for d in outer_deg] \
        + [(W_OUT, 0.0), (W_OUT, R), (W_OUT, -R)]
    if len(verts) != NV:
        abort(f"vertex bookkeeping: {len(verts)} != {NV}")

    L = [_foam_header("dictionary", "blockMeshDict", "system"),
         "\nscale   1;\n\nvertices\n("]
    for z in (0, 1):
        for i, (x, y) in enumerate(verts):
            L.append(f"    ({x:.12g} {y:.12g} {z})   // {i + NV * z}")
    L.append(");\n\nblocks\n(")

    first_cell = FIRST_CELL_ANCHOR / mult
    r_y = ratio_for_first_cell(R, ny, first_cell)
    if not first_cell < R / ny:
        abort(f"aerofoil first cell {first_cell:g} is not finer than this "
              f"level's uniform wall-normal spacing {R / ny:g}; "
              "ratio_for_first_cell would return 1.0 and build an UNGRADED "
              "column, changing the KIND of mesh this level is. Refusing.")
    # THE WAKE OUTLET IS UNIFORM, AT EVERY LEVEL, BY CONSTRUCTION.
    # Attempt 1 anchored it at 0.3 chord.  Measured on this ladder that leaves
    # the wake block's two wall-normal ends grossly mismatched -- r_y (first
    # cell 2e-6) at the trailing edge against a 0.3-chord first cell at the
    # outlet -- which tapers the first streamwise wake cells and drives a THIRD
    # non-orthogonality mechanism that NEITHER predictor above models.  Measured
    # over a five-point sweep of that anchor declared before it was run, max
    # non-orthogonality at coarse / medium / fine:
    #   0.0001 -> 85.6 / 73.5 / 40.4        0.030 -> 86.8 / 85.7 / 81.6
    #   0.0003 -> 80.9 / 58.3 / 37.2        0.100 -> 79.8 / 81.3 / 80.7
    #   0.0010 -> 77.5 / 51.6 / 37.2        0.300 -> 64.1 / 65.7 / 67.1 (attempt 1's)
    #   0.0030 -> 85.3 / 75.5 / 47.8        UNIFORM -> 51.1 / 51.5 / 51.9
    # A uniform outlet is the SAME KIND of distribution at EVERY level and it
    # halves with the ladder like every other spacing, so the family stays
    # geometrically similar.  What the frozen module's guard refuses is a SILENT
    # flip to uniform at ONE level only -- a branch flip, not a drift -- and
    # that is not what this is: it is declared, it is level-invariant, and it is
    # the only setting measured whose margin does not degrade under refinement.
    far_first = R / ny
    r_y_far = 1.0

    for chain_i, chain_o, blocks in ((iu, ou, up), (il, ol, lo)):
        for k, b in enumerate(blocks):
            a, bb = chain_i[k], chain_i[k + 1]
            oa, ob = OFF + chain_o[k], OFF + chain_o[k + 1]
            n = b["n_coarse"] * mult
            L.append(f"    hex ({a} {bb} {ob} {oa} {a+NV} {bb+NV} {ob+NV} {oa+NV})"
                     f" ({n} {ny} 1)\n"
                     f"        simpleGrading ({b['grading']:.10g} {r_y:.10g} 1)")
    te, o90, o270 = iu[-1], OFF + ou[-1], OFF + ol[0]
    te_spacing = _cell(up[-1], mult, "last")
    r_wake = ratio_for_first_cell(WAKE_LEN, n_wake, te_spacing)
    L.append(f"    hex ({te} {WK0} {WKP} {o90} {te+NV} {WK0+NV} {WKP+NV} {o90+NV})"
             f" ({n_wake} {ny} 1)\n"
             f"        edgeGrading ({r_wake:.10g} {r_wake:.10g} {r_wake:.10g} {r_wake:.10g}\n"
             f"                     {r_y:.10g} {r_y_far:.10g} {r_y_far:.10g} {r_y:.10g}\n"
             f"                     1 1 1 1)")
    L.append(f"    hex ({WK0} {te} {o270} {WKM} {WK0+NV} {te+NV} {o270+NV} {WKM+NV})"
             f" ({n_wake} {ny} 1)\n"
             f"        edgeGrading ({1.0/r_wake:.10g} {1.0/r_wake:.10g} {1.0/r_wake:.10g} {1.0/r_wake:.10g}\n"
             f"                     {r_y_far:.10g} {r_y:.10g} {r_y:.10g} {r_y_far:.10g}\n"
             f"                     1 1 1 1)")
    L.append(");\n\nedges\n(")

    def poly(points, z):
        body = "\n".join(f"        ({x:.12g} {y:.12g} {z})" for x, y in points)
        return f"(\n{body}\n    )"

    for z, off in ((0.0, 0), (1.0, NV)):
        for chain_i, chain_o, blocks, side in ((iu, ou, up, "u"), (il, ol, lo, "l")):
            for k, b in enumerate(blocks):
                pts = W.surface_points(sec, b["x_a"], b["x_b"],
                                       +1.0 if side == "u" else -1.0, n=N_POLY)
                L.append(f"    polyLine {chain_i[k] + off} {chain_i[k + 1] + off} "
                         f"{poly(pts, z)}")
                mx, my = op(0.5 * (b["deg_a"] + b["deg_b"]))
                L.append(f"    arc {OFF + chain_o[k] + off} "
                         f"{OFF + chain_o[k + 1] + off} ({mx:.12g} {my:.12g} {z:g})")
    L.append(");\n\nboundary\n(")

    aer, inf, outf, fab = [], [], [], []
    for chain_i, chain_o, blocks in ((iu, ou, up), (il, ol, lo)):
        for k in range(len(blocks)):
            a, bb = chain_i[k], chain_i[k + 1]
            oa, ob = OFF + chain_o[k], OFF + chain_o[k + 1]
            aer.append(f"({a} {bb} {bb+NV} {a+NV})")
            inf.append(f"({oa} {ob} {ob+NV} {oa+NV})")
            fab.append(f"({a} {bb} {ob} {oa})")
            fab.append(f"({a+NV} {bb+NV} {ob+NV} {oa+NV})")
    # Patch roles reproduce attempt 1's dict FACE FOR FACE, including its
    # asymmetry: the UPPER wake block's far boundary is `outflow` while the
    # LOWER wake block's is `inflow`.  That asymmetry is REPORTED, NOT
    # REPAIRED here -- it is a boundary-condition question and belongs to
    # gate B, which this phase does not touch.
    inf.append(f"({WKM} {o270} {o270+NV} {WKM+NV})")
    outf.append(f"({o90} {WKP} {WKP+NV} {o90+NV})")
    outf.append(f"({WK0} {WKP} {WKP+NV} {WK0+NV})")
    outf.append(f"({WK0} {WKM} {WKM+NV} {WK0+NV})")
    fab.append(f"({te} {WK0} {WKP} {o90})")
    fab.append(f"({te+NV} {WK0+NV} {WKP+NV} {o90+NV})")
    fab.append(f"({WK0} {te} {o270} {WKM})")
    fab.append(f"({WK0+NV} {te+NV} {o270+NV} {WKM+NV})")

    def patch(name, kind, faces):
        body = "\n            ".join(faces)
        return (f"    {name}\n    {{\n        type {kind};\n        faces\n"
                f"        (\n            {body}\n        );\n    }}")

    L.append(patch("aerofoil", "wall", aer))
    L.append(patch("inflow", "patch", inf))
    L.append(patch("outflow", "patch", outf))
    L.append(patch("frontAndBack", "empty", fab))
    L.append(");\n")
    meta = dict(r_y=r_y, r_y_far=r_y_far, r_wake=r_wake, first_cell=first_cell,
                far_first_cell=far_first, te_spacing=te_spacing,
                n_vertices=NV * 2, n_blocks=2 * NB + 2)
    return "\n".join(L), meta


# ---------------------------------------------------------------------------
# checkMesh reading -- an ABSENT log reads ABSENT, never clean
# ---------------------------------------------------------------------------

def read_check_mesh(path: pathlib.Path):
    if not path.exists():
        return {"status": "ABSENT", "log": str(path)}
    txt = path.read_text(errors="replace")
    out = dict(W.parse_check_mesh(txt))       # the committed reader
    out["status"] = "PRESENT"
    out["log"] = str(path)
    m = re.search(r"severely non-orthogonal \(> 70 degrees\) faces:\s*(\d+)", txt)
    if m:
        out["faces_over_70"] = int(m.group(1))
    elif "Non-orthogonality check OK." in txt:
        out["faces_over_70"] = 0              # stated by checkMesh, not defaulted
    else:
        out["faces_over_70"] = None           # unknown reads unknown
    return out


def grade_gate_a(q):
    if q.get("status") != "PRESENT":
        return {"verdict": "ABSENT", "breaches": ["checkMesh log ABSENT"]}
    no, sk = q.get("max_non_orthogonality"), q.get("max_skewness")
    if no is None or sk is None:
        return {"verdict": "ABSENT",
                "breaches": ["checkMesh log present but its quality lines "
                             "could not be read"]}
    br = []
    if no > GATE_A_NONORTHO:
        br.append(f"max non-orthogonality {no} > {GATE_A_NONORTHO}")
    if sk > GATE_A_SKEWNESS:
        br.append(f"max skewness {sk} > {GATE_A_SKEWNESS}")
    return {"verdict": "PASS" if not br else "GATE FAIL", "breaches": br,
            "max_non_orthogonality": no, "max_skewness": sk,
            "nonortho_margin_deg": GATE_A_NONORTHO - no,
            "skewness_margin": GATE_A_SKEWNESS - sk}


def control_dict():
    return _foam_header("dictionary", "controlDict", "system") + """
application     rhoSimpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         1;
deltaT          1;
writeControl    timeStep;
writeInterval   1;
"""


def decompose_dict():
    return _foam_header("dictionary", "decomposeParDict", "system") + f"""
numberOfSubdomains {DECOMP_RANKS};
method          {DECOMP_METHOD};
coeffs
{{
    n           ({DECOMP_N[0]} {DECOMP_N[1]} {DECOMP_N[2]});
    order       xyz;
}}
"""


def write_case_shell(case: pathlib.Path, dict_text: str):
    (case / "system").mkdir(parents=True)
    (case / "constant").mkdir(parents=True)
    (case / "system" / "blockMeshDict").write_text(dict_text)
    (case / "system" / "controlDict").write_text(control_dict())
    (case / "system" / "decomposeParDict").write_text(decompose_dict())
    (case / "system" / "fvSchemes").write_text(W.fv_schemes())
    (case / "system" / "fvSolution").write_text(W.fv_solution())


def polygon(path):
    txt = pathlib.Path(path).read_text()
    pts = []
    for m in re.finditer(r"polyLine\s+\d+\s+\d+\s*\((.*?)\n\s*\)", txt, re.S):
        for q in re.findall(r"\(([^()]*)\)", m.group(1)):
            v = [float(t) for t in q.split()]
            if v[2] == 0.0:
                pts.append((round(v[0], 12), round(v[1], 12)))
    return sorted(set(pts)), len(re.findall(r"polyLine\s+\d+\s+\d+", txt))


def main() -> int:
    t0_phase = time.monotonic()
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    loadavg = open("/proc/loadavg").read().split()[:3]

    # -- rule 2: this builder must BE its committed blob ---------------------
    disk_self = hashlib.sha256((REPO / SELF_REL).read_bytes()).hexdigest()
    blob_self = hashlib.sha256(git_bytes("cat-file", "-p",
                                         f"HEAD:{SELF_REL}")).hexdigest()
    if disk_self != blob_self:
        abort("this builder DIFFERS from its HEAD blob; refusing to run")

    # -- rule 2: the frozen pre-registration is the one that was frozen ------
    got = git_bytes("rev-parse", f"HEAD:{PREREG}").decode().strip()
    if got != PREREG_BLOB:
        abort(f"frozen pre-registration blob {got} != {PREREG_BLOB}")
    on_disk = subprocess.run(["git", "-C", str(REPO), "hash-object", PREREG],
                             capture_output=True, text=True).stdout.strip()
    if on_disk != PREREG_BLOB:
        abort(f"worktree pre-registration {on_disk} != HEAD blob {PREREG_BLOB}")
    head_text = git_bytes("cat-file", "-p", f"HEAD:{PREREG}").decode()
    for needle in ("max non-orthogonality\n<= 70 degrees and max skewness <= 4",
                   "upper surface RMS <= **0.08**",
                   "lower surface RMS <= **0.04**",
                   "<= **0.020**",
                   "|CN - 0.803| / 0.803 <= **5%**",
                   "|CD - 0.0168| / 0.0168 <= **20%**",
                   "| coarse | 48 | 48 | 80 | 23,040 |"):
        if needle not in head_text:
            abort(f"frozen text not found in the HEAD blob: {needle!r}")

    # -- earlier attempt trees must still exist, undeleted, unrenamed --------
    for p in ("verification/runs/F12_runs/coarse_workshop_M0.734_a2.79",
              "verification/runs/F12_runs/mesh_audit_2026-08-25",
              "verification/runs/F12_runs/mesh_audit_2026-08-25/mesh_audit.json",
              "verification/runs/F12_runs/reference"):
        if not (REPO / p).exists():
            abort(f"earlier attempt tree MISSING: {p}")

    # -- every directory this run writes must be ABSENT ---------------------
    targets = [HERE / n for n, _, _, _ in LEVELS] \
        + [HERE / "control_attempt1_correspondence"]
    for t in targets:
        if os.path.exists(t):
            abort(f"registered run directory already exists: {t}")

    sec = W.rae_section()
    corr = Correspondence(sec)
    plan = plan_blocks(corr)

    # -- the declared design criterion is asserted BEFORE anything is written --
    predicted = {}
    for name, mult, ny, n_wake in LEVELS:
        w, wloc = predict_nonortho(corr, plan, mult)
        iv = predict_interface(plan, mult, ny, n_wake, FIRST_CELL_ANCHOR / mult)
        worst = max(w, iv["upper_TE"]["angle_deg"], iv["lower_TE"]["angle_deg"])
        predicted[name] = {"near_wall_deg": w,
                           "near_wall_location": {"side": wloc[0], "block": wloc[1],
                                                  "x": wloc[2]},
                           "interface": iv, "max_deg": worst}
        if worst > DESIGN_CRITERION_DEG:
            abort(f"design criterion: level {name!r} predicts {worst:.3f} deg "
                  f"> {DESIGN_CRITERION_DEG} deg. REFUSING TO BUILD. The gate is "
                  f"NOT relaxed to accommodate a recipe; the recipe is rejected.")
    # HONEST LIMIT ON BOTH PREDICTORS: they model the near-wall
    # correspondence and the O-ring/wake interface, and they DO NOT BOUND
    # the measured maximum.  A third mechanism lives inside the wake block
    # (see blockmesh_dict) and is bounded only empirically.  This assertion
    # is a DESIGN FILTER on two identified mechanisms, NOT a prediction of
    # gate A.  Gate A is decided below, and only, by a real checkMesh log.

    res = {"stamp_utc": stamp, "loadavg_at_launch": loadavg,
           "prereg_blob": PREREG_BLOB, "builder_sha256": disk_self,
           "recipe": {"corner_x": list(CORNER_X),
                      "monotonise_blend": MONOTONISE_BLEND,
                      "ds_le": DS_LE, "ds_mid": DS_MID, "ds_te": DS_TE,
                      "n_surf_total_coarse": N_SURF_TOTAL_COARSE,
                      "n_poly_points_per_block_edge": N_POLY,
                      "farfield_r": FARFIELD_R, "wake_len": WAKE_LEN,
                      "first_cell_anchor": FIRST_CELL_ANCHOR,
                      "design_criterion_deg": DESIGN_CRITERION_DEG,
                      "decomposition": {"method": DECOMP_METHOD,
                                        "n": list(DECOMP_N),
                                        "ranks": DECOMP_RANKS,
                                        "seed": "none: hierarchical is "
                                                "seed-free by construction"}},
           "blocks": plan, "predicted": predicted, "levels": {}, "timings": {}, "controls": {}}

    for name, mult, ny, n_wake in LEVELS:
        case = HERE / name
        t = time.monotonic()
        text, meta = blockmesh_dict(sec, corr, plan, mult, ny, n_wake)
        write_case_shell(case, text)
        t_write = time.monotonic() - t

        t = time.monotonic()
        rc_bm = _foam(["blockMesh"], case, "log.blockMesh", timeout=1800)
        t_bm = time.monotonic() - t
        t = time.monotonic()
        rc_cm = _foam(["checkMesh"], case, "log.checkMesh", timeout=1800)
        t_cm = time.monotonic() - t

        q = read_check_mesh(case / "log.checkMesh")
        gate = grade_gate_a(q)
        if rc_bm.returncode != 0:
            gate = {"verdict": "NOT A RESULT",
                    "breaches": [f"blockMesh rc={rc_bm.returncode}"]}

        parts = []
        t = time.monotonic()
        for rep in (1, 2):
            _foam(["decomposePar", "-force"], case,
                  f"log.decomposePar.{rep}", timeout=1800)
            txt = (case / f"log.decomposePar.{rep}").read_text(errors="replace")
            parts.append([int(m) for m in
                          re.findall(r"Number of cells = (\d+)", txt)])
        t_dec = time.monotonic() - t
        det = bool(parts[0]) and parts[0] == parts[1] \
            and sum(parts[0]) == q.get("cells")

        expected = CELLS_FROZEN[[l[0] for l in LEVELS].index(name)]
        res["levels"][name] = {
            "blockMesh_rc": rc_bm.returncode, "checkMesh_rc": rc_cm.returncode,
            "cells_expected_frozen": expected, "cells_built": q.get("cells"),
            "cells_match_frozen": q.get("cells") == expected,
            "ny": ny, "n_wake": n_wake,
            "n_surf_total": N_SURF_TOTAL_COARSE * mult,
            "n_blocks": meta["n_blocks"], "n_vertices": meta["n_vertices"],
            "first_cell_wall_normal": meta["first_cell"],
            "wall_normal_total_expansion": meta["r_y"],
            "wake_outlet_total_expansion": meta["r_y_far"],
            "wake_streamwise_total_expansion": meta["r_wake"],
            "surface_min_first_cell": min(_cell(b, mult, "first") for b in plan),
            "te_streamwise_spacing": meta["te_spacing"],
            "y_plus_full_height": meta["first_cell"] * YPLUS_PER_CHORD,
            "y_plus_cell_centre": 0.5 * meta["first_cell"] * YPLUS_PER_CHORD,
            "y_plus_full_height_x_le_factor":
                meta["first_cell"] * YPLUS_PER_CHORD * YPLUS_LE_FACTOR,
            "quality": q, "gate_A": gate,
            "predicted": predicted[name],
            "decomposition": {"method": DECOMP_METHOD, "ranks": DECOMP_RANKS,
                              "partition_cells_run1": parts[0],
                              "partition_cells_run2": parts[1],
                              "identical_across_two_runs": det},
        }
        res["timings"][name] = {"dict_write_s": round(t_write, 3),
                                "blockMesh_s": round(t_bm, 3),
                                "checkMesh_s": round(t_cm, 3),
                                "decomposePar_x2_s": round(t_dec, 3)}

    # ---- PLANTED CONTROLS on the gate-A reader ----------------------------
    plant_log = HERE / "PLANT_checkMesh_log"
    src = (HERE / "coarse" / "log.checkMesh").read_text(errors="replace")
    plant_log.write_text(re.sub(r"Mesh non-orthogonality Max: [0-9.eE+-]+",
                                "Mesh non-orthogonality Max: 88.8", src, count=1))
    pq = read_check_mesh(plant_log); pg = grade_gate_a(pq)
    aq = read_check_mesh(HERE / "PLANT_this_log_does_not_exist")
    ag = grade_gate_a(aq)

    ctrl = HERE / "control_attempt1_correspondence"
    write_case_shell(ctrl, W.blockmesh_dict(sec, W.GridLevel("coarse", 48, 48, 80)))
    t = time.monotonic()
    _foam(["blockMesh"], ctrl, "log.blockMesh", timeout=1800)
    _foam(["checkMesh"], ctrl, "log.checkMesh", timeout=1800)
    t_ctrl = time.monotonic() - t
    cq = read_check_mesh(ctrl / "log.checkMesh"); cg = grade_gate_a(cq)
    pred_old, _ = None, None

    res["controls"] = {
        "text_plant": {"planted_value": 88.8,
                       "read_back": pq.get("max_non_orthogonality"),
                       "verdict": pg["verdict"], "artifact": str(plant_log)},
        "absent_plant": {"status": aq.get("status"), "verdict": ag["verdict"]},
        "attempt1_correspondence_rebuilt": {
            "max_non_orthogonality": cq.get("max_non_orthogonality"),
            "max_skewness": cq.get("max_skewness"),
            "faces_over_70": cq.get("faces_over_70"),
            "verdict": cg["verdict"],
            "artifact": str(ctrl / "log.checkMesh")},
    }
    res["timings"]["control_attempt1_s"] = round(t_ctrl, 3)
    reader_ok = (pg["verdict"] == "GATE FAIL" and ag["verdict"] == "ABSENT"
                 and cg["verdict"] == "GATE FAIL")
    res["reader_shown_able_to_see_a_breach"] = reader_ok
    if not reader_ok:
        abort("PLANTED CONTROL FAILED: the gate-A reader was not shown able to "
              "see a breach; every verdict below would be inadmissible")

    # ---- similarity invariants --------------------------------------------
    names = [n for n, _, _, _ in LEVELS]
    inv = [res["levels"][n]["wall_normal_total_expansion"] for n in names]
    sfc = [res["levels"][n]["surface_min_first_cell"] for n in names]
    res["similarity"] = {
        "wall_normal_total_expansion": inv,
        "wall_normal_spread_pct": 100.0 * (max(inv) - min(inv)) / min(inv),
        "surface_first_cell": sfc,
        "surface_first_cell_ratios": [sfc[0] / sfc[1], sfc[1] / sfc[2]],
        "wake_streamwise_total_expansion":
            [res["levels"][n]["wake_streamwise_total_expansion"] for n in names],
        "wake_outlet_total_expansion":
            [res["levels"][n]["wake_outlet_total_expansion"] for n in names],
        "first_cell_wall_normal":
            [res["levels"][n]["first_cell_wall_normal"] for n in names],
    }

    # ---- polygon identity across the ladder, with its own planted control --
    pgs = {n: polygon(HERE / n / "system" / "blockMeshDict") for n in names}
    thin_path = HERE / "PLANT_polygon_thinned_blockMeshDict"
    ft = (HERE / "fine" / "system" / "blockMeshDict").read_text()

    def _thin(m):
        keep = re.findall(r"\([^()]*\)", m.group(1))[::2]
        return ("polyLine 0 0 (\n" + "\n".join("        " + k for k in keep)
                + "\n    )")
    thin_path.write_text(re.sub(r"polyLine\s+\d+\s+\d+\s*\((.*?)\n\s*\)",
                                _thin, ft, flags=re.S))
    pg_p = polygon(thin_path)
    res["geometric_floor"] = {
        "n_polylines": {n: pgs[n][1] for n in names},
        "n_unique_xy": {n: len(pgs[n][0]) for n in names},
        "identical_coarse_medium": pgs["coarse"][0] == pgs["medium"][0],
        "identical_medium_fine": pgs["medium"][0] == pgs["fine"][0],
        "planted_thinned_unique_xy": len(pg_p[0]),
        "reader_sees_the_difference": pg_p[0] != pgs["fine"][0],
        "planted_artifact": str(thin_path),
    }
    if not res["geometric_floor"]["reader_sees_the_difference"]:
        abort("PLANTED CONTROL FAILED: the polygon reader cannot see a thinned "
              "polygon; the identity claim would be inadmissible")

    # ---- cost --------------------------------------------------------------
    wall = time.monotonic() - t0_phase
    res["cost"] = {
        "wall_s_total": round(wall, 3), "ranks": 1,
        "core_min_actual": round(wall / 60.0, 4),
        "model": "t = 0.930 s x (N/23040)^0.72, a MEASURED FIT to the attempt-1 "
                 "mesh-audit timings, plus ~1.5 s per-process startup",
        "blockMesh_checkMesh_predicted_s": {
            n: round(0.930 * (c / 23040.0) ** 0.72, 3)
            for n, c in zip(names, CELLS_FROZEN)},
        "blockMesh_checkMesh_actual_s": {
            n: round(res["timings"][n]["blockMesh_s"]
                     + res["timings"][n]["checkMesh_s"], 3) for n in names},
        "cost_basis": "reported-by-owner, NOT measured: the $0.0513/core-h "
                      "c7a.4xlarge rate is owner-stated 2026-08-21/22 and this "
                      "box cannot read its own billing "
                      "(COMPUTE_BUDGET_CHARTER.md section 5)",
        "dollars_derived_not_measured": round((wall / 3600.0) * 0.0513, 6),
        "loadavg_at_launch": loadavg,
    }

    (HERE / "gate_a_attempt2.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({
        "gate_A": {n: res["levels"][n]["gate_A"]["verdict"] for n in names},
        "max_non_ortho": {n: res["levels"][n]["quality"].get("max_non_orthogonality")
                          for n in names},
        "max_skewness": {n: res["levels"][n]["quality"].get("max_skewness")
                         for n in names},
        "faces_over_70": {n: res["levels"][n]["quality"].get("faces_over_70")
                          for n in names},
        "cells": {n: res["levels"][n]["cells_built"] for n in names},
        "predicted_max": {n: round(predicted[n]["max_deg"], 3) for n in names},
        "controls_ok": reader_ok, "wall_s": round(wall, 2)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
