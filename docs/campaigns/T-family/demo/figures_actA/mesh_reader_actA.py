#!/usr/bin/env python3
"""Cell-centre reader for the motor-in-duct wedge cases -- REAL COMPUTATIONAL
MESH, never an STL tessellation.

WHY THIS FILE EXISTS.  The Act A radial-profile screen needs temperature as a
function of RADIUS.  The frozen comparators `analyse_t23.py` / `analyse_t24.py`
read the temperature field and the interface-patch face areas, and this module
REUSES their parsing for everything they already do (`internal_window`,
`_foam_list`, `patch_face_areas`).  What they do NOT do is locate a cell in
space, because neither Q1 (max over the region) nor Q2 (area average on one
patch) needs a coordinate.  This module adds exactly that one thing: cell
centres computed from the case's own `constant/<region>/polyMesh`, by the
OpenFOAM decomposition (face centres and areas from a fan about the face's
point average; cell centres from the pyramid decomposition about the face-centre
average).  No coordinate is read from a surface file, an STL, or a name.

PLANTED-ZERO CONTROL, CLAUDE.md rule 3.  A profile of zeros from a reader that
cannot see a non-zero is not evidence.  `planted_profile_control` copies the
case to scratch, writes a known perturbation into ONE named internal-field cell
BY LINE INDEX (never by value), reads the profile back, and requires that the
perturbation appears at exactly the expected radius, at exactly the expected
magnitude, in exactly one sample.  It REFUSES rather than degrades.

Nothing here writes into a case directory.
"""
import math
import os
import re
import shutil
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))

T24_DIR = os.path.join(REPO, "verification", "runs", "T-family", "T24_runs")


def _load_frozen_comparator():
    """Import the frozen T24 comparator and REUSE its parsing.  Imported by
    path so no copy of its readers is ever made here."""
    import importlib.util
    p = os.path.join(T24_DIR, "analyse_t24.py")
    if not os.path.isfile(p):
        raise SystemExit("REFUSE: frozen comparator absent at %s" % p)
    spec = importlib.util.spec_from_file_location("analyse_t24_frozen", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


A24 = _load_frozen_comparator()

KELVIN_C = A24.KELVIN_C
ENDTIME = A24.ENDTIME


def refuse(msg):
    sys.stderr.write("REFUSE: %s\n" % msg)
    raise SystemExit(2)


# --------------------------------------------------------------------------
# polyMesh readers.  `_foam_list` is the FROZEN comparator's, reused.
# --------------------------------------------------------------------------

def read_points(case_dir, region):
    p = os.path.join(case_dir, "constant", region, "polyMesh", "points")
    pts = A24._foam_list(p, lambda s: tuple(float(x)
                                            for x in s.strip("()").split()))
    return np.asarray(pts, dtype=float)


def read_faces(case_dir, region):
    p = os.path.join(case_dir, "constant", region, "polyMesh", "faces")
    fl = A24._foam_list(
        p, lambda s: [int(x) for x in s[s.index("(") + 1:s.rindex(")")].split()])
    n = np.array([len(f) for f in fl], dtype=np.int64)
    if not (n == n[0]).all():
        # general case still supported; the wedge meshes here are all-quad
        return fl, None
    return fl, np.asarray(fl, dtype=np.int64)


def read_labels(case_dir, region, name):
    p = os.path.join(case_dir, "constant", region, "polyMesh", name)
    return np.asarray(A24._foam_list(p, lambda s: int(s)), dtype=np.int64)


def n_cells(case_dir, region):
    """From the polyMesh's own `note`, cross-checked against max(owner)."""
    p = os.path.join(case_dir, "constant", region, "polyMesh", "owner")
    head = open(p).read(4000)
    m = re.search(r"nCells:(\d+)", head)
    if not m:
        refuse("%s carries no nCells note" % p)
    return int(m.group(1))


# --------------------------------------------------------------------------
# GEOMETRY.  The OpenFOAM decomposition, written out rather than approximated.
# --------------------------------------------------------------------------

def face_centres_and_areas(pts, faces_arr):
    """All-quad fast path: fan decomposition about the point average, exactly
    as OpenFOAM's primitiveMeshFaceCentresAndAreas does for nPoints > 3."""
    P = pts[faces_arr]                          # (nF, k, 3)
    k = P.shape[1]
    est = P.mean(axis=1)                        # (nF, 3)
    ctr = np.zeros_like(est)
    sf = np.zeros_like(est)
    asum = np.zeros(P.shape[0])
    for i in range(k):
        p0 = P[:, i, :]
        p1 = P[:, (i + 1) % k, :]
        nxt = np.cross(p1 - p0, est - p0)
        a = np.linalg.norm(nxt, axis=1)
        c = (p0 + p1 + est) / 3.0
        ctr += c * a[:, None]
        sf += 0.5 * nxt
        asum += a
    ok = asum > 0.0
    if not ok.all():
        refuse("%d zero-area faces -- a cell centre built on one is undefined"
               % int((~ok).sum()))
    ctr /= asum[:, None]
    return ctr, sf


def cell_centres(case_dir, region):
    """(nCells, 3) real cell centres, OpenFOAM pyramid decomposition."""
    pts = read_points(case_dir, region)
    _, faces_arr = read_faces(case_dir, region)
    if faces_arr is None:
        refuse("%s/%s: mixed face sizes -- this reader handles the all-quad "
               "wedge meshes of this family only" % (case_dir, region))
    own = read_labels(case_dir, region, "owner")
    nei = read_labels(case_dir, region, "neighbour")
    nc = n_cells(case_dir, region)
    if own.max() + 1 != nc:
        refuse("%s/%s: owner max %d against nCells %d"
               % (case_dir, region, own.max(), nc))
    fc, sf = face_centres_and_areas(pts, faces_arr)

    # cEst = average of the face centres of each cell
    acc = np.zeros((nc, 3))
    cnt = np.zeros(nc)
    np.add.at(acc, own, fc)
    np.add.at(cnt, own, 1.0)
    np.add.at(acc, nei, fc[:len(nei)])
    np.add.at(cnt, nei, 1.0)
    cEst = acc / cnt[:, None]

    # pyramid decomposition about cEst
    ccv = np.zeros((nc, 3))
    vol = np.zeros(nc)

    d_own = fc - cEst[own]
    pv_own = (sf * d_own).sum(axis=1) / 3.0
    pc_own = 0.75 * fc + 0.25 * cEst[own]
    np.add.at(ccv, own, pc_own * pv_own[:, None])
    np.add.at(vol, own, pv_own)

    fcn = fc[:len(nei)]
    sfn = sf[:len(nei)]
    d_nei = fcn - cEst[nei]
    pv_nei = -(sfn * d_nei).sum(axis=1) / 3.0
    pc_nei = 0.75 * fcn + 0.25 * cEst[nei]
    np.add.at(ccv, nei, pc_nei * pv_nei[:, None])
    np.add.at(vol, nei, pv_nei)

    if (vol <= 0.0).any():
        refuse("%s/%s: %d cells with non-positive volume"
               % (case_dir, region, int((vol <= 0.0).sum())))
    return ccv / vol[:, None], vol


# --------------------------------------------------------------------------
# THE FIELD READER.  internalField window comes from the FROZEN comparator.
# --------------------------------------------------------------------------

def read_internal_T(case_dir, region):
    p = os.path.join(case_dir, ENDTIME, region, "T")
    lines, first, n = A24.internal_window(p)
    return np.array([float(lines[first + i]) for i in range(n)])


# --------------------------------------------------------------------------
# THE RADIAL PROFILE READER.
# --------------------------------------------------------------------------

Z_LAYER_TOL = 1.0e-7                    # m; axial cell size here is ~8.9e-4 m


def axial_layers(z, tol=Z_LAYER_TOL):
    """Group cell-centre z values into structured axial layers.

    NOT a rounding: cell centres in one layer of a graded wedge agree only to
    the precision of the pyramid decomposition, which is far below `tol` and
    far above nothing, so a fixed decimal round splits some layers and merges
    none.  Consecutive-gap clustering is used instead, and the widest cluster
    is asserted to be narrower than `tol`."""
    o = np.argsort(z)
    zs = z[o]
    brk = np.where(np.diff(zs) > tol)[0]
    starts = np.concatenate(([0], brk + 1))
    ends = np.concatenate((brk + 1, [len(zs)]))
    lab = np.empty(len(z), dtype=np.int64)
    ctr = np.empty(len(starts))
    for i, (a, b) in enumerate(zip(starts, ends)):
        lab[o[a:b]] = i
        ctr[i] = zs[a:b].mean()
        if zs[b - 1] - zs[a] > tol:
            refuse("axial layer %d spans %.3e m, wider than the %.1e m "
                   "clustering tolerance" % (i, zs[b - 1] - zs[a], tol))
    return lab, ctr


def radial_profile(case_dir, regions, z_target):
    """-> list of (region, r_m, T_K) arrays for the ONE axial cell layer whose
    centres sit closest to `z_target`, sorted by radius.

    The layer is selected on the CORE region's distinct centre-z values, then
    the same z is matched in every region, so all three regions are sampled at
    one axial station and not at three different ones."""
    out = []
    z_used = None
    for reg in regions:
        cc, _ = cell_centres(case_dir, reg)
        T = read_internal_T(case_dir, reg)
        if len(T) != cc.shape[0]:
            refuse("%s/%s: %d temperatures against %d cells"
                   % (case_dir, reg, len(T), cc.shape[0]))
        lab, ctr = axial_layers(cc[:, 2])
        if z_used is None:
            z_used = float(ctr[np.argmin(np.abs(ctr - z_target))])
        k = int(np.argmin(np.abs(ctr - z_used)))
        zi = float(ctr[k])
        if abs(zi - z_used) > 1e-6:
            refuse("region %s has no cell layer at z = %.12g m (nearest %.12g) "
                   "-- the profile will NOT be assembled from mismatched "
                   "axial stations" % (reg, z_used, zi))
        sel = lab == k
        r = np.hypot(cc[sel, 0], cc[sel, 1])
        t = T[sel]
        o = np.argsort(r)
        out.append((reg, r[o], t[o], float(zi)))
    return out, float(z_used)


# --------------------------------------------------------------------------
# PLANTED-ZERO CONTROL for THIS reader (CLAUDE.md rule 3).
# --------------------------------------------------------------------------

PLANT = A24.PLANT                       # 1.234e-03 K, imported, never redefined


def planted_profile_control(case_dir, region, z_target, mag=PLANT):
    """Copy the case, plant `mag` K into ONE internal cell by LINE INDEX, read
    the profile back, and require the perturbation to appear at exactly one
    radius at exactly that magnitude.  REFUSES rather than degrades."""
    case_real = os.path.realpath(case_dir)
    scratch = tempfile.mkdtemp(prefix="actActl_")
    dest = os.path.join(scratch, os.path.basename(case_dir))
    try:
        if os.path.realpath(scratch).startswith(case_real + os.sep):
            refuse("control scratch resolves inside the case")
        shutil.copytree(case_dir, dest, symlinks=True,
                        ignore=shutil.ignore_patterns("log.solve", "*.py",
                                                      "postProcessing"))
        fld = os.path.join(dest, ENDTIME, region, "T")
        pristine = open(fld).read()

        # NEGATIVE ARM: two reads of identical bytes must differ by bitwise 0.
        p0, _ = radial_profile(dest, (region,), z_target)
        p1, _ = radial_profile(dest, (region,), z_target)
        if not np.array_equal(p0[0][2], p1[0][2]):
            refuse("radial reader is NOISY: two reads of identical bytes "
                   "differ")
        base_r, base_T = p0[0][1], p0[0][2]

        # POSITIVE ARM: plant into the cell that sits at the MIDDLE radius of
        # the profile, located by LINE INDEX from the field's own header.
        lines, first, n = A24.internal_window(fld)
        cc, _ = cell_centres(dest, region)
        lab, ctr = axial_layers(cc[:, 2])
        k = int(np.argmin(np.abs(ctr - z_target)))
        sel = np.where(lab == k)[0]
        r_sel = np.hypot(cc[sel, 0], cc[sel, 1])
        target_cell = int(sel[np.argsort(r_sel)[len(sel) // 2]])
        r_expect = float(np.sort(r_sel)[len(sel) // 2])
        old = float(lines[first + target_cell])
        lines[first + target_cell] = "%.12g" % (old + mag)
        open(fld, "w").write("\n".join(lines))

        p2, _ = radial_profile(dest, (region,), z_target)
        got_r, got_T = p2[0][1], p2[0][2]
        d = got_T - base_T
        nz = np.where(d != 0.0)[0]
        if len(nz) != 1:
            refuse("radial reader saw %d perturbed samples, expected exactly 1 "
                   "-- a reader that cannot localise a plant cannot localise a "
                   "gradient" % len(nz))
        seen = float(d[nz[0]])
        seen_r = float(got_r[nz[0]])
        rel = abs(seen - mag) / mag
        if rel > 1e-9:
            refuse("radial reader read %.6e K at the plant against %.6e K "
                   "planted (rel %.3e)" % (seen, mag, rel))
        if abs(seen_r - r_expect) > 1e-12:
            refuse("radial reader placed the plant at r = %.12g m against the "
                   "expected %.12g m" % (seen_r, r_expect))

        open(fld, "w").write(pristine)
        if open(fld).read() != open(os.path.join(case_dir, ENDTIME, region,
                                                 "T")).read():
            refuse("the case file and the restored copy differ -- the control "
                   "may have written into the case")
        return dict(passed=True, planted_K=mag, read_K=seen,
                    rel_error=rel, radius_m=seen_r, n_perturbed=int(len(nz)),
                    cell_index=target_cell, region=region)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
