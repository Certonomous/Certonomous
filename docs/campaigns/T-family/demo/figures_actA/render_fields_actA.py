#!/usr/bin/env python3
# =========================================================================
# ACT A FIELD RENDERS -- built from the four landed 305 W operating points.
#
# NOTHING HERE SOLVES ANYTHING.  It reads the runs that already exist on
# disk and writes the field images, the mesh zoom and the data files the
# display mission needs.  No solver is launched, no case directory is
# written to, and no `.tex` sheet is touched.
#
# EVERY COLOURED SHAPE IS ONE FINITE-VOLUME CELL OF THE REAL COMPUTATIONAL
# MESH, DRAWN AT ITS OWN EXTENT AND COLOURED BY ITS OWN STORED VALUE.
# The corners come out of `constant/<region>/polyMesh/points` through the
# cells' own faces; the values come out of `10000/<region>/<field>`.  There
# is no STL, no surface tessellation, no triangulation, and no
# interpolation onto a display grid.  This is the same rule the Act C
# renderer follows (`../figures/make_act_c_screens.py`); the geometry here
# is an axisymmetric wedge rather than a rectangular stack, so the cell
# polygon is built differently -- but a cell is still exactly one polygon.
#
# REUSED, NOT RE-IMPLEMENTED:
#   * `mesh_reader_actA.py`      -- polyMesh readers, cell centres.
#   * `analyse_t24.py` (frozen)  -- `_foam_list`, `internal_window`,
#                                   `_list_window`, and `PLANT`.
#   * each case's own `build_t23.py` -- the REGISTERED geometry constants
#     and cell counts, imported so no radius and no cell count is typed a
#     second time in this file.
#
# THE GEOMETRY GUARD IS RE-ASSERTED IN THIS SCRIPT'S OWN CODE PATH, five
# ways, per region and per case.  A guard that only runs inside a module
# this script imports is not a guard on this script.
#
# PLANTED CONTROL (CLAUDE.md rule 3), THREE ARMS, ALL BEFORE ANY FIGURE:
#   (a) NEGATIVE  -- two reads of identical bytes must differ by bitwise 0.
#   (b) SCALAR    -- a known perturbation is planted in ONE known mesh cell
#                    of ONE known region, read back through the SAME
#                    extractor that colours the panels, and required to
#                    appear at that size, in that cell, and NOWHERE else in
#                    any region.
#   (c) VECTOR    -- the same, for the velocity extractor.
#   The case tree is copied to scratch first and its bytes are checksummed
#   before and after.  If any arm fails, the script EXITS and writes no
#   figure.
# =========================================================================
import csv
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                # noqa: E402
from matplotlib.collections import PolyCollection              # noqa: E402
from matplotlib.patches import Rectangle                       # noqa: E402
import numpy as np                                             # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, HERE)
import mesh_reader_actA as MR                                  # noqa: E402

A24 = MR.A24
ENDTIME = MR.ENDTIME                     # "10000", from the frozen comparator
KELVIN_C = MR.KELVIN_C                   # 273.15, from the frozen comparator
PLANT = MR.PLANT                         # 1.234e-03, never redefined here
# The magnitude ladder and the ONE sizing tolerance are IMPORTED from the same
# frozen comparator, so this file cannot quietly hold a different ladder or a
# different tolerance from the sibling screen builder.
LADDER = A24.LADDER                      # clause 3, the magnitude ladder
PLANT_REL_SLACK = A24.PLANT_REL_SLACK    # clause 5, RELATIVE, 1e-9

# Sanaa's 2026-09-01 figure standard: 0.1 degC significant figures on every
# temperature DRAWN in a figure, until the grid triple lands.  Instrument
# evidence -- planted magnitudes, anchor residuals, the geometry guard -- is
# NEVER rounded, and is recorded at full precision in the bundle.
DISPLAY_DP_T = 1                         # decimal places on drawn temperatures
DISPLAY_DP_V = 1                         # decimal places on drawn air speeds

RUNS = os.path.join(REPO, "verification", "runs", "T-family", "T23_runs")
SPEEDS = (10, 20, 30, 40)
CASES = {u: os.path.join(RUNS, "T23_P305_U%d" % u) for u in SPEEDS}
REGIONS = ("core", "housing", "fluid")

# Measured wall-resolution figure, quoted from the campaign record rather
# than recomputed here.  Carried WITH its caveat everywhere it is printed.
YPLUS_MAX = {10: 0.4037, 20: 0.7515, 30: 1.0790, 40: 1.3970}
YPLUS_SOURCE = os.path.join(REPO, "docs", "campaigns", "T-family",
                            "CASE3_MAP_RESULTS.md")

plt.rcParams.update({
    "font.size": 9,
    "axes.titlesize": 9,
    "axes.labelsize": 9,
    "mathtext.fontset": "dejavuserif",
    "pdf.fonttype": 42,
    "svg.fonttype": "none",
    "figure.dpi": 150,
})


def refuse(msg):
    sys.stderr.write("REFUSE: %s\n" % msg)
    raise SystemExit(2)


# --------------------------------------------------------------------------
# THE REGISTERED GEOMETRY, imported from the case's own build script so that
# no radius, no axial station and no cell count is typed twice.
# --------------------------------------------------------------------------

def load_registered_geometry(case_dir):
    p = os.path.join(case_dir, "build_t23.py")
    if not os.path.isfile(p):
        refuse("the case carries no build script at %s" % p)
    spec = importlib.util.spec_from_file_location("build_registered", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)          # every action sits under __main__
    return mod


# --------------------------------------------------------------------------
# CELL POLYGONS IN THE MERIDIONAL PLANE.  Exact, not approximated.
#
# The mesh is a 5 degree wedge about the z axis.  Every cell is a hexahedron
# whose eight corner points fall into four (z, r) pairs, each appearing twice
# -- once on each wedge plane.  The four distinct pairs ARE the cell as it is
# drawn.  Nothing is projected, averaged or fitted.
#
# THE ONE TOLERANCE IN THIS FILE, AND WHY IT IS THE SIZE IT IS.  The two
# wedge planes are written to the mesh file in ASCII at 12 significant
# figures, so the mirrored point of a pair can differ from its partner in
# the last stored digit: MEASURED, the largest such disagreement anywhere in
# these three meshes is 9.991e-14 m in radius and EXACTLY ZERO in z.  The
# smallest real radial cell dimension in the same meshes is 2.309e-05 m.
# `PAIR_TOL_M` is set at 1.0e-12 m: ten times above the largest write-format
# artefact, and 2.3e+07 times below the smallest real feature it could
# possibly merge.  BOTH SIDES ARE ASSERTED BELOW, per region, every run --
# so the tolerance is a measured quantity here and not a convenience.
# --------------------------------------------------------------------------

PAIR_TOL_M = 1.0e-12
PAIR_TOL_SAFETY = 1.0e4          # smallest real cell / tolerance, minimum


def cell_polygons(case_dir, region):
    pts = MR.read_points(case_dir, region)
    fl, faces_arr = MR.read_faces(case_dir, region)
    if faces_arr is None:
        refuse("%s/%s: mixed face sizes -- this renderer draws the all-quad "
               "wedge meshes of this family only" % (case_dir, region))
    own = MR.read_labels(case_dir, region, "owner")
    nei = MR.read_labels(case_dir, region, "neighbour")
    nc = MR.n_cells(case_dir, region)

    # cell -> its corner point ids, gathered through the cells' own faces
    bag = [set() for _ in range(nc)]
    for fi in range(faces_arr.shape[0]):
        bag[own[fi]].update(faces_arr[fi])
        if fi < len(nei):
            bag[nei[fi]].update(faces_arr[fi])
    npts = np.array([len(b) for b in bag])
    if not (npts == 8).all():
        refuse("%s/%s: %d cells do not have 8 corner points -- this renderer "
               "will not draw a cell it cannot bound exactly"
               % (case_dir, region, int((npts != 8).sum())))
    P = np.array([sorted(b) for b in bag], dtype=np.int64)      # (nc, 8)

    zr = np.stack([pts[:, 2], np.hypot(pts[:, 0], pts[:, 1])], axis=1)
    Z = zr[P]                                                   # (nc, 8, 2)
    order = np.lexsort((Z[:, :, 1], Z[:, :, 0]), axis=1)
    Zs = np.take_along_axis(Z, order[:, :, None], axis=1)

    # The two wedge planes must pair up: same z EXACTLY, same r to within the
    # write-format artefact.  Both are measured and asserted, not assumed.
    dpair = np.abs(Zs[:, 0::2, :] - Zs[:, 1::2, :])
    dz_pair = float(dpair[:, :, 0].max())
    dr_pair = float(dpair[:, :, 1].max())
    if dz_pair != 0.0:
        refuse("%s/%s: the two wedge planes disagree in z by %.3e m -- the "
               "mesh is not the wedge this renderer is entitled to draw"
               % (case_dir, region, dz_pair))
    if dr_pair > PAIR_TOL_M:
        refuse("%s/%s: the two wedge planes disagree in radius by %.3e m, "
               "above the %.1e m pairing tolerance -- this is a geometry "
               "difference, not a write-format artefact"
               % (case_dir, region, dr_pair, PAIR_TOL_M))
    quad = Zs[:, 0::2, :]                                       # (nc, 4, 2)

    # A wedge cell is bounded by two axial planes and two radial surfaces, so
    # its meridional footprint is an axis-aligned rectangle.  ASSERTED, not
    # assumed: exactly two distinct z (exact) and two radius clusters that are
    # tight to the pairing tolerance and separated far above it.
    z0 = quad[:, :, 0].min(axis=1)
    z1 = quad[:, :, 0].max(axis=1)
    rs = np.sort(quad[:, :, 1], axis=1)
    nz_distinct = np.array([len(np.unique(q)) for q in quad[:, :, 0]])
    if not (nz_distinct == 2).all():
        refuse("%s/%s: %d cells do not have exactly two distinct axial "
               "coordinates" % (case_dir, region,
                                int((nz_distinct != 2).sum())))
    spread_lo = float((rs[:, 1] - rs[:, 0]).max())
    spread_hi = float((rs[:, 3] - rs[:, 2]).max())
    if max(spread_lo, spread_hi) > PAIR_TOL_M:
        refuse("%s/%s: a cell's two inner (or two outer) corner radii differ "
               "by %.3e m, above the %.1e m tolerance"
               % (case_dir, region, max(spread_lo, spread_hi), PAIR_TOL_M))
    r0 = rs[:, :2].min(axis=1)
    r1 = rs[:, 2:].max(axis=1)
    dr_cell = float((r1 - r0).min())
    dz_cell = float((z1 - z0).min())
    if dr_cell < PAIR_TOL_SAFETY * PAIR_TOL_M:
        refuse("%s/%s: the smallest real radial cell dimension is %.3e m, "
               "within %.0fx of the %.1e m pairing tolerance -- the tolerance "
               "could merge two real corners and this renderer will not use it"
               % (case_dir, region, dr_cell, PAIR_TOL_SAFETY, PAIR_TOL_M))
    rect_exact = True

    poly = np.empty((nc, 4, 2))
    poly[:, 0] = np.stack([z0, r0], axis=1)
    poly[:, 1] = np.stack([z1, r0], axis=1)
    poly[:, 2] = np.stack([z1, r1], axis=1)
    poly[:, 3] = np.stack([z0, r1], axis=1)                     # CCW

    x, y = poly[:, :, 0], poly[:, :, 1]
    area = 0.5 * np.abs(np.sum(x * np.roll(y, -1, axis=1)
                               - np.roll(x, -1, axis=1) * y, axis=1))
    if (area <= 0.0).any():
        refuse("%s/%s: %d cells have non-positive meridional area"
               % (case_dir, region, int((area <= 0.0).sum())))
    tol = {"largest_wedge_plane_radius_disagreement_m": dr_pair,
           "largest_wedge_plane_axial_disagreement_m": dz_pair,
           "pairing_tolerance_m": PAIR_TOL_M,
           "smallest_real_radial_cell_dimension_m": dr_cell,
           "smallest_real_axial_cell_dimension_m": dz_cell,
           "tolerance_headroom_above_artefact": (PAIR_TOL_M / dr_pair
                                                 if dr_pair > 0 else None),
           "tolerance_margin_below_smallest_real_feature":
               dr_cell / PAIR_TOL_M}
    return poly, area, rect_exact, nc, tol


def geometry_guard(case_dir, region, poly, area, rect_exact, nc, G):
    """The five-way guard, re-asserted here in this script's own code path."""
    exp_cells = {"core": G.NR_CORE * G.NZ_MID,
                 "housing": G.NR_HOUS * G.NZ_MID,
                 "fluid": (G.NR_BL_IN + G.NR_MID + G.NR_BL_OUT)
                          * (G.NZ_UP + G.NZ_MID + G.NZ_DOWN)}[region]
    exp_r = {"core": (G.R0, G.R1), "housing": (G.R1, G.R2),
             "fluid": (G.R2, G.R5)}[region]
    exp_z = {"core": (G.Z1, G.Z2), "housing": (G.Z1, G.Z2),
             "fluid": (G.Z0, G.Z3)}[region]
    exp_area = (exp_r[1] - exp_r[0]) * (exp_z[1] - exp_z[0])

    bad = []
    if nc != exp_cells:
        bad.append("cell count %d against the registered %d" % (nc, exp_cells))
    if len(poly) != nc:
        bad.append("built %d polygons for %d cells" % (len(poly), nc))
    rr = (float(poly[:, :, 1].min()), float(poly[:, :, 1].max()))
    zz = (float(poly[:, :, 0].min()), float(poly[:, :, 0].max()))
    if abs(rr[0] - exp_r[0]) > 1e-9 or abs(rr[1] - exp_r[1]) > 1e-9:
        bad.append("radial extent %.12g..%.12g against the registered "
                   "%.12g..%.12g" % (rr[0], rr[1], exp_r[0], exp_r[1]))
    if abs(zz[0] - exp_z[0]) > 1e-9 or abs(zz[1] - exp_z[1]) > 1e-9:
        bad.append("axial extent %.12g..%.12g against the registered "
                   "%.12g..%.12g" % (zz[0], zz[1], exp_z[0], exp_z[1]))
    ta = float(area.sum())
    if abs(ta - exp_area) / exp_area > 1e-9:
        bad.append("meridional area %.12g m2 against the registered %.12g m2"
                   % (ta, exp_area))
    if not rect_exact:
        bad.append("some cell footprint is not bounded by exactly two axial "
                   "and two radial surfaces")
    if bad:
        refuse("%s/%s does not match the registered geometry: %s"
               % (case_dir, region, "; ".join(bad)))
    return {"cells": nc, "r_min_m": rr[0], "r_max_m": rr[1],
            "z_min_m": zz[0], "z_max_m": zz[1],
            "meridional_area_m2": ta,
            "registered_meridional_area_m2": exp_area,
            "footprint_is_exact_rectangle": rect_exact}


# --------------------------------------------------------------------------
# THE FIELD EXTRACTORS.  These are the functions that colour the panels; the
# planted controls exercise these, not a private copy of them.
# --------------------------------------------------------------------------

def read_scalar(case_dir, region, name, nc):
    p = os.path.join(case_dir, ENDTIME, region, name)
    lines, first, n = A24.internal_window(p)
    if n != nc:
        refuse("%s holds %d values against %d mesh cells" % (p, n, nc))
    return np.array([float(lines[first + i]) for i in range(n)])


_VEC = re.compile(r"^\(([^)]*)\)$")


def read_vector(case_dir, region, name, nc):
    """internalField `nonuniform List<vector>`, located structurally by the
    frozen comparator's own window finder -- never by counting lines."""
    p = os.path.join(case_dir, ENDTIME, region, name)
    lines = open(p).read().split("\n")
    idx = [k for k, l in enumerate(lines)
           if re.match(r"\s*internalField\s+nonuniform\s+List<vector>", l)]
    if len(idx) != 1:
        refuse("%s has %d internalField vector list headers, expected exactly 1"
               % (p, len(idx)))
    first, n = A24._list_window(lines, idx[0])
    if n != nc:
        refuse("%s holds %d vectors against %d mesh cells" % (p, n, nc))
    out = np.empty((n, 3))
    for i in range(n):
        m = _VEC.match(lines[first + i].strip())
        if not m:
            refuse("%s line %d is not a bracketed vector" % (p, first + i + 1))
        v = m.group(1).split()
        if len(v) != 3:
            refuse("%s line %d holds %d components, expected 3"
                   % (p, first + i + 1, len(v)))
        out[i] = [float(x) for x in v]
    return out


def read_all_T(case_dir, ncs):
    return {r: read_scalar(case_dir, r, "T", ncs[r]) for r in REGIONS}


# --------------------------------------------------------------------------
# PLANTED CONTROLS.  CLAUDE.md rule 3.  Run before any figure is drawn.
# --------------------------------------------------------------------------

def tree_digest(case_dir):
    """sha256 over every byte of the end-time fields and the three polyMeshes,
    so that 'the case tree is unchanged' is a measurement and not a belief."""
    h = hashlib.sha256()
    paths = []
    for r in REGIONS:
        d = os.path.join(case_dir, ENDTIME, r)
        paths += [os.path.join(d, f) for f in sorted(os.listdir(d))]
        d = os.path.join(case_dir, "constant", r, "polyMesh")
        paths += [os.path.join(d, f) for f in sorted(os.listdir(d))]
    for p in sorted(paths):
        h.update(p.encode())
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
    return h.hexdigest(), len(paths)


def _scratch_case(case_dir):
    """A copy whose end-time fields may be written; `constant` is a symlink,
    so the mesh is read from the real case and can never be written."""
    scratch = tempfile.mkdtemp(prefix="actA_field_plant_")
    dst = os.path.join(scratch, "case")
    os.makedirs(dst)
    os.symlink(os.path.join(case_dir, "constant"),
               os.path.join(dst, "constant"))
    shutil.copytree(os.path.join(case_dir, ENDTIME),
                    os.path.join(dst, ENDTIME))
    return scratch, dst


def planted_controls(case_dir, ncs):
    """The frozen comparator's registered clauses, on BOTH field extractors.

    Clause 9 the bytecode caches are cleared first; clause 1 copy-first with a
    refusal if the scratch resolves inside the case; clause 2 negative arm at
    bitwise 0.0 with NO tolerance; clause 3 the IMPORTED magnitude ladder,
    measured rung by rung; clause 4 refuse if the reader is BLIND; clause 5 the
    RELATIVE sizing predicate `at_plant >= PLANT*(1-1e-9)`; clause 8 the case is
    checked to be unwritten and the scratch is removed in a `finally`.
    REFUSES rather than degrades."""
    A24.clear_pycache()                                          # clause 9
    _p = os.path.join(HERE, "__pycache__")
    if os.path.isdir(_p):
        shutil.rmtree(_p, ignore_errors=True)

    before, nfiles = tree_digest(case_dir)
    case_real = os.path.realpath(case_dir)
    scratch, dst = _scratch_case(case_dir)
    rep = {}
    try:
        # ---- CLAUSE 1: COPY FIRST, NEVER WRITE INTO THE CASE.
        if os.path.realpath(scratch) == case_real \
           or os.path.realpath(scratch).startswith(case_real + os.sep):
            refuse("the field-control scratch %s resolves INSIDE the case %s "
                   "-- clause 1 forbids writing into the case under any "
                   "circumstance" % (scratch, case_real))
        if os.path.realpath(dst).startswith(case_real + os.sep):
            refuse("the field-control copy %s resolves INSIDE the case %s"
                   % (dst, case_real))

        # ---- (a) NEGATIVE ARM: identical bytes must read bitwise identical
        a0 = read_all_T(dst, ncs)
        a1 = read_all_T(dst, ncs)
        for r in REGIONS:
            if not np.array_equal(a0[r], a1[r]):
                refuse("the temperature extractor is NOISY: two reads of "
                       "identical bytes differ in region %s" % r)
        v0 = read_vector(dst, "fluid", "U", ncs["fluid"])
        v1 = read_vector(dst, "fluid", "U", ncs["fluid"])
        if not np.array_equal(v0, v1):
            refuse("the velocity extractor is NOISY: two reads of identical "
                   "bytes differ")
        rep["negative_arm"] = {
            "two_reads_of_identical_bytes_differ_by": 0.0,
            "regions": list(REGIONS) + ["fluid velocity"], "passed": True}

        # ---- (b) SCALAR ARM: one cell, one region, located by LINE INDEX,
        #      walked rung by rung down the IMPORTED magnitude ladder.
        preg, pidx = "housing", ncs["housing"] // 2
        fld = os.path.join(dst, ENDTIME, preg, "T")
        pristine = open(fld).read()

        def _plant_T(mag):
            lines, first, n = A24.internal_window(fld)
            base_val = float(lines[first + pidx])
            lines[first + pidx] = "%.12g" % (base_val + mag)
            open(fld, "w").write("\n".join(lines))
            return base_val

        rungs, floor, at_plant, elsewhere_at_plant, old = [], None, None, None, None
        for mag in LADDER:
            open(fld, "w").write(pristine)
            old = _plant_T(mag)
            seen = read_all_T(dst, ncs)
            got = float(seen[preg][pidx] - a0[preg][pidx])
            els = 0.0
            for r in REGIONS:
                d = seen[r] - a0[r]
                if r == preg:
                    d = np.delete(d, pidx)
                if len(d):
                    els = max(els, float(np.abs(d).max()))
            rungs.append((float(mag), got, els))
            if got != 0.0:
                floor = mag if floor is None else min(floor, mag)
            if mag == PLANT:
                at_plant, elsewhere_at_plant = got, els
        open(fld, "w").write(pristine)

        # CLAUSE 4: REFUSE IF THE READER IS BLIND.
        if floor is None:
            refuse("the temperature extractor is BLIND -- no magnitude in the "
                   "imported ladder produced a non-zero read. An instrument "
                   "that cannot see a planted perturbation is not entitled to "
                   "colour a panel that is offered as evidence")
        if at_plant is None:
            refuse("PLANT was not exercised by the imported temperature ladder")
        # CLAUSE 5: THE ONLY SIZING TOLERANCE, AND IT IS RELATIVE.
        if not (at_plant >= PLANT * (1.0 - PLANT_REL_SLACK)):
            refuse("the temperature extractor read %.6e K at PLANT, below the "
                   "registered RELATIVE predicate PLANT*(1-1e-9) = %.6e K"
                   % (at_plant, PLANT * (1.0 - PLANT_REL_SLACK)))
        if elsewhere_at_plant != 0.0:
            refuse("the temperature extractor did not LOCALISE the planted "
                   "%.6e K change: %.3e K moved in the other %d cells"
                   % (PLANT, elsewhere_at_plant, sum(ncs.values()) - 1))
        rep["scalar_arm"] = {
            "planted_K": float(PLANT), "region": preg, "cell_index": int(pidx),
            "baseline_value_K": old, "read_back_K": float(at_plant),
            "detection_floor_K": float(floor),
            "ladder_K": [r[0] for r in rungs],
            "ladder_read_K": [r[1] for r in rungs],
            "ladder_change_elsewhere_K": [r[2] for r in rungs],
            "relative_predicate": "read_at_PLANT >= PLANT*(1-1e-9)",
            "largest_change_anywhere_else_K": float(elsewhere_at_plant),
            "cells_searched": int(sum(ncs.values())), "passed": True}

        # ---- (c) VECTOR ARM: one cell of the velocity field, same ladder.
        vidx = ncs["fluid"] // 2
        vfld = os.path.join(dst, ENDTIME, "fluid", "U")
        vpristine = open(vfld).read()

        def _plant_U(mag):
            vlines = open(vfld).read().split("\n")
            vi = [k for k, l in enumerate(vlines)
                  if re.match(r"\s*internalField\s+nonuniform\s+List<vector>",
                              l)]
            vfirst, _vn = A24._list_window(vlines, vi[0])
            comps = _VEC.match(vlines[vfirst + vidx].strip()).group(1).split()
            base_z = float(comps[2])
            vlines[vfirst + vidx] = "(%s %s %.12g)" % (comps[0], comps[1],
                                                       base_z + mag)
            open(vfld, "w").write("\n".join(vlines))
            return base_z

        vrungs, vfloor, v_at_plant, oldz = [], None, None, None
        v_else_at_plant, v_other_at_plant = None, None
        for mag in LADDER:
            open(vfld, "w").write(vpristine)
            oldz = _plant_U(mag)
            vseen = read_vector(dst, "fluid", "U", ncs["fluid"])
            dv = vseen - v0
            got = float(dv[vidx, 2])
            els = float(np.abs(np.delete(dv, vidx, axis=0)).max())
            oth = float(np.abs(dv[vidx, :2]).max())
            vrungs.append((float(mag), got, els, oth))
            if got != 0.0:
                vfloor = mag if vfloor is None else min(vfloor, mag)
            if mag == PLANT:
                v_at_plant, v_else_at_plant, v_other_at_plant = got, els, oth
        open(vfld, "w").write(vpristine)

        if vfloor is None:
            refuse("the velocity extractor is BLIND -- no magnitude in the "
                   "imported ladder produced a non-zero read")
        if v_at_plant is None:
            refuse("PLANT was not exercised by the imported velocity ladder")
        if not (v_at_plant >= PLANT * (1.0 - PLANT_REL_SLACK)):
            refuse("the velocity extractor read %.6e m/s at PLANT, below the "
                   "registered RELATIVE predicate PLANT*(1-1e-9) = %.6e"
                   % (v_at_plant, PLANT * (1.0 - PLANT_REL_SLACK)))
        if v_else_at_plant != 0.0 or v_other_at_plant != 0.0:
            refuse("the velocity extractor did not LOCALISE the planted %.6e "
                   "m/s change: %.3e m/s moved in the other %d cells and "
                   "%.3e m/s in the other two components"
                   % (PLANT, v_else_at_plant, ncs["fluid"] - 1,
                      v_other_at_plant))
        rep["vector_arm"] = {
            "planted_m_per_s": float(PLANT), "region": "fluid",
            "component": "axial", "cell_index": int(vidx),
            "baseline_axial_m_per_s": oldz,
            "read_back_m_per_s": float(v_at_plant),
            "detection_floor_m_per_s": float(vfloor),
            "ladder_m_per_s": [r[0] for r in vrungs],
            "ladder_read_m_per_s": [r[1] for r in vrungs],
            "relative_predicate": "read_at_PLANT >= PLANT*(1-1e-9)",
            "largest_change_anywhere_else_m_per_s": float(v_else_at_plant),
            "largest_change_in_other_components_m_per_s":
                float(v_other_at_plant),
            "cells_searched": int(ncs["fluid"]), "passed": True}

        # ---- CLAUSE 8: the case was never written to, CHECKED not asserted.
        for r in REGIONS:
            if open(os.path.join(case_dir, ENDTIME, r, "T")).read() \
               != open(os.path.join(dst, ENDTIME, r, "T")).read():
                refuse("the case file and the restored copy differ in region "
                       "%s -- the control may have written into the case" % r)
        if open(os.path.join(case_dir, ENDTIME, "fluid", "U")).read() \
           != open(vfld).read():
            refuse("the case velocity file and the restored copy differ -- "
                   "the control may have written into the case")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    after, nfiles2 = tree_digest(case_dir)
    rep["case_tree_unchanged"] = {
        "files_checksummed": nfiles,
        "sha256_before": before, "sha256_after": after,
        "identical": bool(before == after and nfiles == nfiles2)}
    if not rep["case_tree_unchanged"]["identical"]:
        refuse("the case tree changed while the controls ran -- the controls "
               "may have written into the case")
    return rep


# --------------------------------------------------------------------------
# FIGURES.  R5: nothing user-visible carries a case id, a rung letter, a tier
# word, a verdict word, a rule number or any lab-process language.
# --------------------------------------------------------------------------

CMAP_T = "inferno"
CMAP_V = "viridis"


def _collection(poly, vals, cmap, vmin, vmax):
    pc = PolyCollection(poly, cmap=cmap, edgecolors="none", linewidths=0.0,
                        antialiased=False)
    pc.set_array(np.asarray(vals))
    pc.set_clim(vmin, vmax)
    return pc


def _bar(fig, pc, axes, unit, vmin, vmax, dp, location="right"):
    """One colour bar per figure: numeric ticks and the unit, nothing else.

    The scale spans the full range of everything drawn, so nothing is clipped,
    and the minimum and the maximum are the bar's END TICKS -- they appear
    here and NOWHERE else in the figure (Sanaa's 2026-09-01 figure standard).
    Ticks are printed at the display precision, which the bundle records; the
    unrounded values live in the bundle and in the cell table."""
    fmt = "%%.%df" % dp
    cb = fig.colorbar(pc, ax=axes, location=location, shrink=0.9, pad=0.012)
    cb.set_label(unit)
    ticks = [vmin + f * (vmax - vmin) for f in (0.0, 0.25, 0.5, 0.75, 1.0)]
    cb.set_ticks(ticks)
    setter = (cb.ax.set_yticklabels if location == "right"
              else cb.ax.set_xticklabels)
    setter([fmt % t for t in ticks], fontsize=7)
    return cb


def _caption(fig, text):
    """Exactly one caption line, of at most 20 words, checked here."""
    n = len(text.split())
    if n > 20:
        refuse("the caption is %d words, above the 20-word limit: %r"
               % (n, text))
    fig.text(0.5, -0.004, text, ha="center", va="top", fontsize=8)


def _title(fig, text):
    """The figure title, of at most 10 words, checked here."""
    n = len(text.split())
    if n > 10:
        refuse("the figure title is %d words, above the 10-word limit: %r"
               % (n, text))
    fig.suptitle(text, fontsize=11)


def _inset(ax, text, loc="upper left"):
    """A label inside the axes -- the only place this figure standard allows
    text other than the title, the axis labels, the colour bar and the one
    caption line."""
    x, ha = (0.012, "left") if "left" in loc else (0.988, "right")
    y, va = (0.975, "top") if "upper" in loc else (0.025, "bottom")
    ax.text(x, y, text, transform=ax.transAxes, ha=ha, va=va, fontsize=7.5,
            zorder=8,
            bbox=dict(fc="white", ec="0.6", lw=0.4, alpha=0.88,
                      boxstyle="round,pad=0.22"))


def _save(fig, stem, exts=("pdf", "png")):
    """PDF is the vector artifact; PNG is the raster the artifact server needs.

    SVG is written only where it stays a reasonable size.  A panel here holds
    up to 39 680 real cell polygons, and SVG stores every one as its own
    uncompressed path element: the field figures come out at 23-26 MB in SVG
    against 1.6 MB in PDF, which compresses the identical path stream.  The
    PDF is fully vector -- every cell is still its own path -- so nothing is
    lost by leaving the SVG out of the two largest figures."""
    out = []
    for ext in exts:
        p = "%s.%s" % (stem, ext)
        fig.savefig(p, bbox_inches="tight",
                    **({"dpi": 200} if ext == "png" else {}))
        out.append(p)
    plt.close(fig)
    return out


# The near-surface window, and the one deliberate distortion in this file.
# The thermal and viscous layers on the cooled surface are microns to
# millimetres thick against a body a quarter of a metre long, so at equal
# aspect they are thinner than a printed line.  The right-hand column of the
# two field figures stretches the RADIAL axis by exactly ZOOM_ASPECT relative
# to the axial axis.  Both axes keep their own real dimensions in metres and
# the factor is printed on the figure -- the picture is stretched, the
# numbers are not.
ZOOM_Z = (-0.020, 0.250)
ZOOM_DR = 0.0020
ZOOM_ASPECT = 40.0


def zoom_selection(geo, G):
    """The fluid cells whose footprint actually falls inside the near-surface
    window, so a panel's printed range is the range of what that panel draws
    and not of some larger region."""
    poly = geo["fluid"]["poly"]
    return ((poly[:, :, 0].max(axis=1) >= ZOOM_Z[0])
            & (poly[:, :, 0].min(axis=1) <= ZOOM_Z[1])
            & (poly[:, :, 1].min(axis=1) <= G.R2 + ZOOM_DR))


def _support_block(ax, G, z0, z1):
    """The unheated support the model does not resolve, drawn as what it is
    rather than left as white space that reads like missing data."""
    ax.add_patch(Rectangle((z0, G.R0), z1 - z0, G.R2 - G.R0,
                           fc="#e9e6e0", ec="none", zorder=1))


def fig_temperature(geo, tC, G, stem):
    allv = np.concatenate([tC[u][r] for u in SPEEDS for r in REGIONS])
    vmin, vmax = float(allv.min()), float(allv.max())
    fig, axes = plt.subplots(len(SPEEDS), 2, figsize=(13.6, 9.4),
                             constrained_layout=True,
                             gridspec_kw={"width_ratios": [1.5, 1.0]})
    pc = None
    sel = zoom_selection(geo, G)
    zlim = {}
    for (al, ar), u in zip(axes, SPEEDS):
        for ax, zoom in ((al, False), (ar, True)):
            _support_block(ax, G, *(ZOOM_Z if zoom else (G.Z0, G.Z3)))
            for r in (("fluid",) if zoom else REGIONS):
                pc = _collection(geo[r]["poly"], tC[u][r], CMAP_T, vmin, vmax)
                ax.add_collection(pc)
            if zoom:
                ax.set_xlim(*ZOOM_Z)
                ax.set_ylim(G.R2 - 0.15 * ZOOM_DR, G.R2 + ZOOM_DR)
                ax.set_aspect(ZOOM_ASPECT)
            else:
                ax.add_patch(Rectangle(
                    (G.Z1, G.R0), G.Z2 - G.Z1, G.R2 - G.R0, fill=False,
                    ec="#00e5ff", lw=0.8, ls=(0, (4, 2)), zorder=5))
                ax.set_xlim(G.Z0, G.Z3)
                ax.set_ylim(G.R0, G.R5)
                ax.set_aspect("equal")
            ax.axhline(G.R2, color="0.15", lw=0.7)
            ax.tick_params(labelsize=7)
        f = tC[u]["fluid"][sel]
        zlim[u] = (float(f.min()), float(f.max()))
        al.set_ylabel(r"Radius $r$, m")
        _inset(al, r"$U_\infty$ = %d m s$^{-1}$" % u)
        _inset(ar, r"$U_\infty$ = %d m s$^{-1}$, radial axis $\times$ %.0f"
               % (u, ZOOM_ASPECT))
    for ax in axes[-1]:
        ax.set_xlabel(r"Axial position $z$, m")
    _bar(fig, pc, list(axes.ravel()), r"$^\circ$C", vmin, vmax, DISPLAY_DP_T)
    axes[0][0].legend(
        handles=[Rectangle((0, 0), 1, 1, fill=False, ec="#00e5ff", lw=0.8,
                           ls=(0, (4, 2)), label="solid body"),
                 Rectangle((0, 0), 1, 1, fc="#e9e6e0", ec="0.6", lw=0.4,
                           label="unheated support")],
        fontsize=7.5, loc="upper right", framealpha=0.9)
    _title(fig, "Temperature field, 305 W")
    _caption(fig, "Each polygon is one finite-volume cell of the computational "
                  "mesh, coloured by its own stored value.")
    return _save(fig, stem), vmin, vmax, zlim, int(sel.sum())


def fig_velocity(geo, umag, G, stem):
    """ONE colour bar, shared by all eight panels and spanning the full range
    of everything drawn, so nothing is clipped and the minimum and maximum are
    the bar's end ticks.  The earlier per-row scales are gone: four bars cannot
    satisfy a standard that puts the extremes on the bar and nowhere else, and
    a shared scale is what makes the fourfold difference between rows readable
    as a difference rather than as four identically-coloured pictures."""
    fig, axes = plt.subplots(len(SPEEDS), 2, figsize=(13.6, 9.4),
                             constrained_layout=True,
                             gridspec_kw={"width_ratios": [1.5, 1.0]})
    lim, zlim = {}, {}
    sel = zoom_selection(geo, G)
    allv = np.concatenate([umag[u] for u in SPEEDS])
    vmin, vmax = float(allv.min()), float(allv.max())
    pc = None
    for (al, ar), u in zip(axes, SPEEDS):
        v = umag[u]
        lo, hi = float(v.min()), float(v.max())
        lim[u] = (lo, hi)
        for ax, zoom in ((al, False), (ar, True)):
            _support_block(ax, G, *(ZOOM_Z if zoom else (G.Z0, G.Z3)))
            pc = _collection(geo["fluid"]["poly"], v, CMAP_V, vmin, vmax)
            ax.add_collection(pc)
            if zoom:
                ax.set_xlim(*ZOOM_Z)
                ax.set_ylim(G.R2 - 0.15 * ZOOM_DR, G.R2 + ZOOM_DR)
                ax.set_aspect(ZOOM_ASPECT)
            else:
                ax.add_patch(Rectangle((G.Z1, G.R0), G.Z2 - G.Z1,
                                       G.R2 - G.R0, fc="#cfcac2", ec="0.35",
                                       lw=0.7, zorder=4))
                ax.set_xlim(G.Z0, G.Z3)
                ax.set_ylim(G.R0, G.R5)
                ax.set_aspect("equal")
            ax.axhline(G.R2, color="0.15", lw=0.7)
            ax.tick_params(labelsize=7)
        al.set_ylabel(r"Radius $r$, m")
        zlim[u] = (float(v[sel].min()), float(v[sel].max()))
        _inset(al, r"$U_\infty$ = %d m s$^{-1}$" % u)
        _inset(ar, r"$U_\infty$ = %d m s$^{-1}$, radial axis $\times$ %.0f"
               % (u, ZOOM_ASPECT))
    for ax in axes[-1]:
        ax.set_xlabel(r"Axial position $z$, m")
    _bar(fig, pc, list(axes.ravel()), r"m s$^{-1}$", vmin, vmax, DISPLAY_DP_V)
    axes[0][0].legend(
        handles=[Rectangle((0, 0), 1, 1, fc="#cfcac2", ec="0.35", lw=0.7,
                           label="solid body"),
                 Rectangle((0, 0), 1, 1, fc="#e9e6e0", ec="0.6", lw=0.4,
                           label="unheated support")],
        fontsize=7.5, loc="upper right", framealpha=0.9)
    _title(fig, "Air speed, 305 W")
    _caption(fig, "Speed of the solved velocity vector, one polygon per "
                  "finite-volume cell, on one shared scale.")
    return _save(fig, stem), lim, zlim, vmin, vmax


def fig_thumbnails(geo, tC, G, vmin, vmax, stem):
    fig, axes = plt.subplots(1, len(SPEEDS), figsize=(12.4, 2.5),
                             constrained_layout=True)
    pc = None
    for ax, u in zip(axes, SPEEDS):
        _support_block(ax, G, G.Z0, G.Z3)
        for r in REGIONS:
            pc = _collection(geo[r]["poly"], tC[u][r], CMAP_T, vmin, vmax)
            ax.add_collection(pc)
        ax.set_xlim(G.Z0, G.Z3)
        ax.set_ylim(G.R0, G.R5)
        ax.set_aspect("equal")
        _inset(ax, r"$U_\infty$ = %d m s$^{-1}$" % u)
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_linewidth(0.6)
    _bar(fig, pc, list(axes), r"$^\circ$C", vmin, vmax, DISPLAY_DP_T,
         location="bottom")
    _title(fig, "Temperature at four cooling airspeeds, 305 W")
    _caption(fig, "One shared scale across the four airspeeds; each polygon is "
                  "one finite-volume cell of the mesh.")
    return _save(fig, stem)


def near_wall_spacing(geo, G):
    """Measured first-cell height on the air side of the metal shell."""
    poly = geo["fluid"]["poly"]
    rmin = poly[:, :, 1].min(axis=1)
    rmax = poly[:, :, 1].max(axis=1)
    sel = np.abs(rmin - G.R2) < 1e-12
    if not sel.any():
        refuse("no air cell touches the shell surface at r = %.12g m" % G.R2)
    h = rmax[sel] - rmin[sel]
    if h.max() - h.min() > 1e-15:
        refuse("the first air cell height is not uniform along the shell "
               "(%.6e to %.6e m)" % (h.min(), h.max()))
    # the shell's own first cell, for the record
    hp = geo["housing"]["poly"]
    hs = np.abs(hp[:, :, 1].max(axis=1) - G.R2) < 1e-12
    hh = (hp[hs, :, 1].max(axis=1) - hp[hs, :, 1].min(axis=1))
    return float(h[0]), int(sel.sum()), float(hh.min()), float(hh.max())


def fig_mesh_zoom(geo, G, h_first, stem):
    """Three real zoom levels on the cooled surface, every one at TRUE
    proportions -- no axis of this figure is stretched.  Each panel states the
    height of the window it shows in millimetres, so the magnification between
    panels is a number the reader can check rather than a claim."""
    zm = 0.5 * (G.Z1 + G.Z2)
    W1 = (zm - 0.020, zm + 0.020, 0.0250, 0.0550)
    W2 = (zm - 0.0016, zm + 0.0016, G.R2 - 0.0016, G.R2 + 0.0016)
    W3 = (zm - 0.0010, zm + 0.0010, G.R2 - 3.0e-5, G.R2 + 2.3e-4)
    cols = {"core": "#c65b1d", "housing": "#1f5fa8", "fluid": "#3d8b52"}
    names = {"core": "heat-generating core", "housing": "metal shell",
             "fluid": "cooling air"}

    fig = plt.figure(figsize=(12.0, 7.4), constrained_layout=True)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 0.44])
    a1 = fig.add_subplot(gs[0, 0])
    a2 = fig.add_subplot(gs[0, 1])
    a3 = fig.add_subplot(gs[1, :])
    counted = {}
    for ax, W, lw in ((a1, W1, 0.25), (a2, W2, 0.55), (a3, W3, 0.8)):
        n = 0
        for r in REGIONS:
            poly = geo[r]["poly"]
            keep = ((poly[:, :, 0].max(axis=1) > W[0])
                    & (poly[:, :, 0].min(axis=1) < W[1])
                    & (poly[:, :, 1].max(axis=1) > W[2])
                    & (poly[:, :, 1].min(axis=1) < W[3]))
            n += int(keep.sum())
            ax.add_collection(PolyCollection(
                poly[keep], facecolors="none", edgecolors=cols[r],
                linewidths=lw, label=names[r]))
        counted[id(ax)] = n
        ax.set_xlim(W[0], W[1])
        ax.set_ylim(W[2], W[3])
        ax.set_aspect("equal")
        ax.axhline(G.R2, color="k", lw=1.0, ls=(0, (5, 3)))
        ax.set_xlabel(r"Axial position $z$, m")
        ax.set_ylabel(r"Radius $r$, m")
        ax.tick_params(labelsize=7.5)

    _inset(a1, "%.0f mm window, %d cells"
           % ((W1[3] - W1[2]) * 1e3, counted[id(a1)]), loc="upper right")
    _inset(a2, "%.1f mm window, %d cells"
           % ((W2[3] - W2[2]) * 1e3, counted[id(a2)]), loc="upper right")
    _inset(a3, r"%.0f $\mu$m window, %d cells"
           % ((W3[3] - W3[2]) * 1e6, counted[id(a3)]), loc="upper right")
    az = zm + 0.00055
    a3.annotate("", xy=(az, G.R2), xytext=(az, G.R2 + h_first),
                arrowprops=dict(arrowstyle="<->", color="#b3002d", lw=1.3,
                                shrinkA=0, shrinkB=0))
    a3.text(az + 3.5e-5, G.R2 + 0.5 * h_first,
            r"first air cell, %.3f $\mu$m" % (h_first * 1e6),
            fontsize=8, va="center", color="#b3002d")
    a3.text(zm - 0.00095, G.R2 - 1.4e-5, "metal shell", fontsize=7.5,
            color="#1f5fa8", va="center")
    h, l = a1.get_legend_handles_labels()
    a1.legend(h, l, fontsize=8, loc="upper left", framealpha=0.92)
    _title(fig, "Computational mesh at the cooled surface, three zooms")
    _caption(fig, "Every quadrilateral is one finite-volume cell; all three "
                  "panels are at true proportions, no axis stretched.")
    return _save(fig, stem, exts=("pdf", "svg", "png")), counted[id(a3)]


# ------------------------------------------------------------------- main
def main():
    print("SOURCE CASES")
    for u in SPEEDS:
        print("  %2d m/s  %s" % (u, CASES[u]))

    G = load_registered_geometry(CASES[10])
    print("\nREGISTERED GEOMETRY (imported from the case's own build script)")
    print("  bore %.4f m   core to %.4f m   shell %.4f-%.4f m   "
          "duct wall %.4f m" % (G.R0, G.R1, G.R1, G.R2, G.R5))
    print("  body length %.4f m   domain z %.4f to %.4f m"
          % (G.Z2 - G.Z1, G.Z0, G.Z3))

    # ---------------------------------------------------------- mesh + guard
    geo, guards, tols = {}, {}, {}
    for r in REGIONS:
        poly, area, rect, nc, tol = cell_polygons(CASES[10], r)
        guards[r] = geometry_guard(CASES[10], r, poly, area, rect, nc, G)
        geo[r] = {"poly": poly, "area": area, "n": nc}
        tols[r] = tol
        print("  %-8s %6d cells  meridional area %.9f m2  "
              "smallest radial cell %.6e m  wedge-plane disagreement %.3e m "
              "(tolerance %.1e m, margin %.2e)"
              % (r, nc, area.sum(), tol["smallest_real_radial_cell_dimension_m"],
                 tol["largest_wedge_plane_radius_disagreement_m"], PAIR_TOL_M,
                 tol["tolerance_margin_below_smallest_real_feature"]))
    ncs = {r: geo[r]["n"] for r in REGIONS}
    print("  five-way geometry guard: satisfied for all three regions")

    # the four cases must share one mesh; asserted rather than assumed
    for u in SPEEDS[1:]:
        for r in REGIONS:
            p2, _, _, n2, _ = cell_polygons(CASES[u], r)
            if n2 != ncs[r] or not np.array_equal(p2, geo[r]["poly"]):
                refuse("the %d m/s case does not share the %d m/s mesh in "
                       "region %s -- one geometry table cannot serve both"
                       % (u, SPEEDS[0], r))
    print("  the four operating points share ONE mesh, bitwise: asserted")

    # ------------------------------------------------------------- controls
    print("\nPLANTED CONTROLS -- CLAUDE.md rule 3")
    controls = {}
    for u in SPEEDS:
        c = planted_controls(CASES[u], ncs)
        controls[u] = c
        s, v = c["scalar_arm"], c["vector_arm"]
        print("  %2d m/s  temperature: planted %+.6e K in cell %d of the "
              "metal shell, read %+.6e K there, %.3e K in the other %d cells"
              % (u, s["planted_K"], s["cell_index"], s["read_back_K"],
                 s["largest_change_anywhere_else_K"],
                 s["cells_searched"] - 1))
        print("          velocity:    planted %+.6e m/s in cell %d of the air, "
              "read %+.6e m/s there, %.3e m/s in the other %d cells"
              % (v["planted_m_per_s"], v["cell_index"], v["read_back_m_per_s"],
                 v["largest_change_anywhere_else_m_per_s"],
                 v["cells_searched"] - 1))
        print("          case tree unchanged over %d files: %s"
              % (c["case_tree_unchanged"]["files_checksummed"],
                 c["case_tree_unchanged"]["identical"]))

    # ---------------------------------------------------------------- fields
    print("\nFIELDS READ FROM THE END-TIME DIRECTORIES")
    tC, umag, uvec = {}, {}, {}
    for u in SPEEDS:
        T = read_all_T(CASES[u], ncs)
        tC[u] = {r: T[r] - KELVIN_C for r in REGIONS}
        U = read_vector(CASES[u], "fluid", "U", ncs["fluid"])
        uvec[u] = U
        umag[u] = np.linalg.norm(U, axis=1)
        lo = min(float(tC[u][r].min()) for r in REGIONS)
        hi = max(float(tC[u][r].max()) for r in REGIONS)
        print("  %2d m/s  temperature %.6f to %.6f degC over %d cells   "
              "air speed %.6f to %.6f m/s over %d cells"
              % (u, lo, hi, sum(ncs.values()), umag[u].min(), umag[u].max(),
                 ncs["fluid"]))

    h_first, n_first, hs_lo, hs_hi = near_wall_spacing(geo, G)
    print("\n  first air cell at the cooled surface: %.9e m (%.4f um), "
          "uniform over %d cells along the surface"
          % (h_first, h_first * 1e6, n_first))
    print("  first shell cell at the same surface:  %.9e to %.9e m"
          % (hs_lo, hs_hi))

    # --------------------------------------------------------------- figures
    print("\nFIGURES")
    files = {}
    f, vmin, vmax, tzoom, nzoom = fig_temperature(
        geo, tC, G, os.path.join(HERE, "actA_temperature_field"))
    files["temperature_field"] = f
    print("  temperature   shared scale %.6f to %.6f degC" % (vmin, vmax))
    for u in SPEEDS:
        print("                near-surface window (%d cells) at %2d m/s: "
              "%.6f to %.6f degC" % (nzoom, u, tzoom[u][0], tzoom[u][1]))
    f, vlim, vzoom, vsmin, vsmax = fig_velocity(
        geo, umag, G, os.path.join(HERE, "actA_velocity_field"))
    files["velocity_field"] = f
    print("  air speed     shared scale %.6f to %.6f m/s" % (vsmin, vsmax))
    files["airspeed_thumbnails"] = fig_thumbnails(
        geo, tC, G, vmin, vmax, os.path.join(HERE, "actA_airspeed_thumbnails"))
    # fig_mesh_zoom returns (paths, cells_in_the_finest_panel) -- unpacked, so
    # the path list is a list of paths and not a list holding an int.
    files["mesh_boundary_layer"], n_finest = fig_mesh_zoom(
        geo, G, h_first, os.path.join(HERE, "actA_mesh_boundary_layer"))
    print("  mesh zoom     %d cells in the finest panel" % n_finest)
    for k, v in files.items():
        for p in v:
            print("  %-22s %8.2f kB  %s"
                  % (k, os.path.getsize(p) / 1024.0, os.path.basename(p)))

    # ------------------------------------------------------------- data out
    cell_csv = os.path.join(HERE, "actA_field_cells.csv")
    with open(cell_csv, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["material_region", "cell_index", "z_min_m", "z_max_m",
                    "r_min_m", "r_max_m"]
                   + ["temperature_degC_at_%dmps" % u for u in SPEEDS]
                   + ["air_speed_mps_at_%dmps" % u for u in SPEEDS])
        label = {"core": "heat_generating_core", "housing": "metal_shell",
                 "fluid": "cooling_air"}
        for r in REGIONS:
            poly = geo[r]["poly"]
            z0 = poly[:, :, 0].min(axis=1)
            z1 = poly[:, :, 0].max(axis=1)
            r0 = poly[:, :, 1].min(axis=1)
            r1 = poly[:, :, 1].max(axis=1)
            for i in range(geo[r]["n"]):
                row = [label[r], i, "%.9g" % z0[i], "%.9g" % z1[i],
                       "%.9g" % r0[i], "%.9g" % r1[i]]
                row += ["%.7f" % tC[u][r][i] for u in SPEEDS]
                row += (["%.7f" % umag[u][i] for u in SPEEDS]
                        if r == "fluid" else
                        ["no velocity field - solid region"] * len(SPEEDS))
                w.writerow(row)
    print("  %-22s %8.2f kB  %s" % ("cell data", os.path.getsize(cell_csv)
                                    / 1024.0, os.path.basename(cell_csv)))

    bundle = {
        "what_this_is": (
            "Field renders for the four cooling-airspeed operating points at "
            "the highest solved heat load. Every coloured shape is one "
            "finite-volume cell of the computational mesh, drawn at its own "
            "extent and coloured by its own stored value."),
        "source_cases": {str(u): CASES[u] for u in SPEEDS},
        "source_fields": {
            str(u): {r: os.path.join(CASES[u], ENDTIME, r, "T")
                     for r in REGIONS}
            for u in SPEEDS},
        "source_velocity_fields": {
            str(u): os.path.join(CASES[u], ENDTIME, "fluid", "U")
            for u in SPEEDS},
        "source_meshes": {r: os.path.join(CASES[10], "constant", r, "polyMesh")
                          for r in REGIONS},
        "registered_geometry_source": os.path.join(CASES[10], "build_t23.py"),
        "readers_reused": [
            os.path.join(HERE, "mesh_reader_actA.py"),
            os.path.join(RUNS, "analyse_t24.py")],
        "fields_present_in_the_end_time_directories": {
            r: sorted(os.listdir(os.path.join(CASES[10], ENDTIME, r)))
            for r in REGIONS},
        "geometry_guard": guards,
        "wedge_plane_pairing": tols,
        "one_mesh_shared_by_all_four_points": True,
        "planted_controls": {str(u): controls[u] for u in SPEEDS},
        "temperature_shared_colour_scale_degC": [vmin, vmax],
        "temperature_per_panel_degC": {
            str(u): [min(float(tC[u][r].min()) for r in REGIONS),
                     max(float(tC[u][r].max()) for r in REGIONS)]
            for u in SPEEDS},
        "temperature_per_panel_per_region_degC": {
            str(u): {r: [float(tC[u][r].min()), float(tC[u][r].max())]
                     for r in REGIONS} for u in SPEEDS},
        "air_speed_shared_colour_scale_mps": [vsmin, vsmax],
        "air_speed_per_panel_mps": {str(u): list(vlim[u]) for u in SPEEDS},
        "figure_titles": {
            "temperature_field": "Temperature field, 305 W",
            "velocity_field": "Air speed, 305 W",
            "airspeed_thumbnails":
                "Temperature at four cooling airspeeds, 305 W",
            "mesh_boundary_layer":
                "Computational mesh at the cooled surface, three zooms"},
        "display_precision": {
            "drawn_temperature_decimal_places": DISPLAY_DP_T,
            "drawn_air_speed_decimal_places": DISPLAY_DP_V,
            "rule": ("Sanaa's 2026-09-01 figure standard: 0.1 degC "
                     "significant figures on temperatures DRAWN in a figure, "
                     "until the grid triple at 305 W and 20 m/s lands. "
                     "Instrument evidence -- planted magnitudes, detection "
                     "floors, the geometry guard, the cell table -- is NEVER "
                     "rounded and is recorded here at full precision."),
            "applies_to": ("colour-bar tick labels on the field figures and "
                           "the thumbnails"),
            "does_not_apply_to": ("planted_controls, geometry_guard, "
                                  "wedge_plane_pairing, the cell CSV, and "
                                  "every range recorded in this bundle")},
        "figure_standard": {
            "source": os.path.join(
                REPO, "etc", "sessions",
                "2026-09-01T0310Z_sanaa_actA_figure_header_standard.md"),
            "title_word_limit": 10,
            "caption_word_limit": 20,
            "colour_bar_carries": "numeric ticks and the unit only",
            "extremes_appear": ("as the colour bar's end ticks and nowhere "
                                "else in the figure"),
            "colour_bars_unclipped": True,
            "one_shared_colour_bar_per_figure": True},
        "air_temperature_per_panel_degC": {
            str(u): [float(tC[u]["fluid"].min()), float(tC[u]["fluid"].max())]
            for u in SPEEDS},
        "near_surface_zoom": {
            "axial_window_m": list(ZOOM_Z),
            "radial_window_above_surface_m": ZOOM_DR,
            "cells_drawn": nzoom,
            "temperature_per_panel_degC": {str(u): list(tzoom[u])
                                           for u in SPEEDS},
            "air_speed_per_panel_mps": {str(u): list(vzoom[u])
                                        for u in SPEEDS},
            "radial_axis_stretched_relative_to_axial_by": ZOOM_ASPECT,
            "note": ("The right-hand column of the two field figures stretches "
                     "the radial axis by this factor so the near-surface "
                     "layer is visible. Both axes carry their own real "
                     "dimensions in metres; only the picture is stretched.")},
        "vector_output": {
            "format": "pdf",
            "svg_written_for": ["mesh_boundary_layer"],
            "why": ("A field panel holds up to 39680 real cell polygons and "
                    "SVG stores every one as an uncompressed path element: "
                    "the field figures come out at 23-26 MB in SVG against "
                    "1.6 MB in PDF, which compresses the identical path "
                    "stream. The PDF is fully vector; no cell is merged, "
                    "rasterised or dropped.")},
        "first_air_cell_height_m": h_first,
        "first_air_cell_height_uniform_over_cells": n_first,
        "first_shell_cell_height_range_m": [hs_lo, hs_hi],
        "wall_resolution_figure": {
            "quantity": "maximum y+ on the cooled surface",
            "values": {str(u): YPLUS_MAX[u] for u in SPEEDS},
            "source": YPLUS_SOURCE,
            "caveat": ("ABOVE 1 AT 30 AND 40 m/s. The near-wall mesh does not "
                       "keep y+ below 1 at the two highest airspeeds, so any "
                       "wall-resolved reading at those two speeds carries "
                       "that limit and must be printed with it. Measured and "
                       "reported; it is not a gated quantity here."),
            "not_recomputed_here": True},
        "uncertainty": (
            "No numerical uncertainty is attached to any value in these "
            "images. One mesh level was run, so no grid-refinement error "
            "estimate exists for them."),
        "figures": files,
        "cell_data_csv": cell_csv,
    }
    js = os.path.join(HERE, "actA_field_render_data.json")
    with open(js, "w") as fh:
        json.dump(bundle, fh, indent=2)
    print("  %-22s %8.2f kB  %s" % ("bundle", os.path.getsize(js) / 1024.0,
                                    os.path.basename(js)))

    print("\nWALL RESOLUTION, quoted with its caveat")
    for u in SPEEDS:
        print("  %2d m/s  max y+ %.4f%s"
              % (u, YPLUS_MAX[u], "   ABOVE 1" if YPLUS_MAX[u] > 1 else ""))
    print("  source %s" % YPLUS_SOURCE)


if __name__ == "__main__":
    main()
