#!/usr/bin/env python3
"""Leading-edge radius of the PPTC blade from the DISCRETE CURVATURE of the production
tessellation -- no circle fit, no chord-extremum search, and NO dependence on a gmsh
curvature knob.

WHY A THIRD INSTRUMENT.  Two have already failed on this geometry and both failures are on the
record (`MESH_PIPELINE_RECORD.md`):

  * addendum E -- circle fitting to section point clouds: six of eight stations refused to fit,
    the two that fitted carried residuals at 40-46 % of the fitted radius, and the chord-extremum
    search moved the r/R = 0.5 chord by 9 % when the sampling shell was widened, so the "ends"
    it located were not stably the leading and trailing edges.
  * addendum F/G -- `measure_le_radius.py`, which reads R = N.h/(2.pi) off gmsh's own
    curvature-driven sizing.  Sound where it applies, but it applies ONLY to a tessellation
    built with `Mesh.MeshSizeFromCurvature` ON, and it inherits BOTH of that run's clamps.
    **Every production tessellation on disk -- `prod7`, `cm1`, `c1` -- sets
    `Mesh.MeshSizeFromCurvature = 0`.**  Facet size there is set by a radial MathEval field,
    so N.h/(2.pi) reads the FIELD and not the geometry.  Applying it to `prod7` would report
    the background field as a radius, which is addendum G's error in a new costume.

THE ESTIMATOR, AND THE BIAS THAT KILLED ITS FIRST FORM.  The obvious estimator is
kappa = angle(n1, n2)/|c1 - c2| between two FACETS sharing an edge.  **That form is wrong and
the synthetic ladder caught it: it recovered 0.6639 mm for a cylinder of radius 1.000 mm --
not a scattered answer but a tight, confident one, biased by EXACTLY 3/2 in curvature.**

The cause is that a flat facet's normal does not belong at its centroid.  A facet spanning the
circumferential arc [j, j+1] carries the true surface normal of the arc MIDPOINT j+0.5, while
its centroid sits at j+1/3 or j+2/3 depending on which half of the quad it is.  On a structured
quad-split cylinder the two facets either side of an axial edge have centroids 2/3 of an arc
apart but normals a FULL arc apart, so kappa comes out at 1.5/R.  The error therefore depends
on the TRIANGULATION PATTERN, which is why the ladder read those radii correctly at 2 mm and
above -- gmsh's Frontal-Delaunay is unstructured there -- and wrongly below.  **An estimator
whose error depends on a pattern the geometry does not control is not an instrument.**

SECOND FORM, ALSO REJECTED, AND BY THE SAME LADDER.  Moving the normal to the VERTEX (the
area-weighted mean of the incident facet normals) removes the 3/2 bias outright -- but taking
kappa as the MAXIMUM of angle(N_u, N_v)/|p_u - p_v| over a vertex's incident edges still read
1.1501 mm for a 1.000 mm cylinder, **+15.0 %**.  The reason is directional sampling: an edge
leaving the vertex at an angle alpha from the direction of maximum curvature sees only
kappa.cos(alpha), so a max over the six-or-so directions a triangulation happens to offer is a
maximum over a sample, not over the sphere of directions.  It is biased LOW in curvature and
therefore HIGH in radius -- the flattering direction -- and by an amount that again depends on
the triangulation and not on the geometry.

THE FORM USED HERE fits the SHAPE OPERATOR by least squares over every incident edge.  With
vertex normals N and a tangent frame (t1, t2) at vertex v, each neighbour u contributes the
tangential displacement dp and the tangential normal variation dn, and the symmetric 2x2
operator S is fitted to

    S . dp  =  dn      for every neighbour u of v

giving three unknowns (s11, s12, s22) from 2 x valence equations.  The principal curvatures are
S's eigenvalues in closed form and kappa_max = max(|k1|, |k2|); R_LE = 1/kappa_max.  Because the
fit uses ALL directions it recovers the true principal curvature whatever direction the edges
run in.  A facet takes the MEDIAN of its three vertices.  Nothing is clamped, and the ladder
below reports what it is worth.

THE RESOLVABLE WINDOW, PRINTED BEFORE ANY FACET IS READ (addendum G's generalisation: an
instrument that reads a physical quantity through a numerical control inherits every clamp on
that control, at BOTH ends).  This estimator's controls are the local facet size h and the
angular resolution of the tessellation:

  * SMALL-R end.  A nose of radius R is spanned by pi.R/h facets, each turning theta = h/R.
    Below R ~ 2h the turn per facet exceeds 30 deg, the polygon is a crude one and the chord
    approximation degrades.  The window's lower edge is therefore ~2h and it is MEASURED, not
    asserted, by the synthetic ladder in --selftest.
  * LARGE-R end.  As R grows theta shrinks towards the tessellation's own normal noise.  The
    upper edge is measured in-file against the shaft, a cylinder of registered radius
    20.000 mm carrying 0.40 mm facets.

TWO CONTROLS, BOTH OF WHICH CAN FAIL AND ARE REPORTED WHETHER THEY DO OR NOT.

  1. IN-FILE CONTROL -- the shaft.  `make_stl.py:R_SHAFT` records r = 20.000 mm exactly,
     measured in `GEOMETRY_ADMISSION_RECORD.md` section 3.  The instrument runs on the SAME
     file, through the SAME reader and the SAME classifier, and must return 20 mm.  A reader
     that cannot see a known radius in the file it is grading is not evidence about an unknown
     one (`CLAUDE.md` rule 3, applied to a curvature instead of a zero).
  2. SYNTHETIC LADDER -- `--selftest` tessellates cylinders of radius 0.125 .. 8 mm at the
     blade facet size and reports recovered against true.  This is the arm that shows the
     instrument CAN see a small radius; without it a large answer is unfalsifiable.

THE LEADING EDGE IS LOCATED BY SECTION GEOMETRY, NOT BY A CURVATURE PERCENTILE.  The first
form of this instrument took the top decile of curvature in a radial band as "the leading
edge".  **It reported R_LE = 24.4 mm at r/R = 0.50 on a section only 8.2 mm thick -- an
impossible answer, tight to 1.0 % across five blades.**  The nose carries a few hundred facets
out of ~21,000 in the band, so a decile is 90 % ordinary surface and its MEDIAN is the surface,
not the nose.  A selector that is consistent across five blades is not thereby correct: all
five were diluted identically.

The form used here extracts the SECTION -- a thin radial shell, one blade, unrolled to
(r.dtheta, x) -- takes the chord as its principal axis, and identifies the leading edge as the
END NEARER THE POINT OF MAXIMUM THICKNESS.  That is a property of every blade section family
and it needs no convention, no rotation sign and no CAD provenance.  The section extraction is
checked against SVA's own published table: chord at r/R = 0.70 measured against C0.70 =
104.1670 mm from `sva_2011_smp11_case2_pptc_geometry_table`.

CAD PROVENANCE IS KEPT, AS AN INDEPENDENT CROSS-CHECK RATHER THAN AS THE SELECTOR.  Both are high-curvature
bands and the trailing edge is the sharper of the two ("The trailing edge for the upper
propeller radii is sharp" -- smp'11 geometry sheet).  The CAD carries ONE root-to-tip curve per
blade and it is the trailing edge; THE LEADING EDGE HAS NO CAD EDGE AT ALL (addendum D).  So
facets within TE_EXCLUSION_MM of a blade-region CAD curve node are trailing edge or tip BY
CONSTRUCTION, and what remains is the leading edge.

UNITS.  Asserted, never assumed: the file's maximum radius about x is compared against the
known VP1304 diameter D = 0.250 m and the instrument REFUSES unless millimetres is the reading
that agrees.  This lab has already applied a metres selector to a millimetre STL and selected
1 facet out of 7,230,286.
"""
from __future__ import annotations

import argparse
import math
import os
import subprocess
import sys
import tempfile

import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from stl_metrics import read_stl                      # noqa: E402
sys.path.insert(0, os.path.dirname(__file__))
from make_stl import classify, R_SHAFT                # noqa: E402

R_PROP = 125.0            # mm, D/2 -- Report 3752 Table 1, D = 250 mm
D_KNOWN_M = 0.250
UNITS_TOL = 0.02          # the mm reading must land within 2 % of the known diameter
TE_EXCLUSION_MM = 1.5     # facets this close to a blade-region CAD curve are TE or tip
BAND_MM = 1.0             # radial half-width of a station
SHELL_MM = 0.25           # radial half-width of a section shell
LE_WINDOW_MM = 0.75       # chordwise window at the leading-edge end, mm
REFUSE_R_OVER_H = 1.50    # below this the nose spans under 5 facets: REFUSE, do not report
WARN_R_OVER_H = 3.00      # between the two, report with the facet count stated
SHAFT_CONTROL_TOL = 0.05  # the in-file control must recover 20.000 mm within 5 %


# --------------------------------------------------------------------------- geometry helpers
def facet_frame(tris: np.ndarray):
    v0, v1, v2 = tris[:, 0], tris[:, 1], tris[:, 2]
    nv = np.cross(v1 - v0, v2 - v0)
    ln = np.linalg.norm(nv, axis=1)
    area = 0.5 * ln
    ln = np.where(ln == 0, 1.0, ln)
    return nv / ln[:, None], tris.mean(axis=1), area, np.sqrt(4.0 * area / np.sqrt(3.0))


def discrete_curvature(tris: np.ndarray):
    """Per-facet kappa_max from a least-squares SHAPE OPERATOR at each vertex.

    Vertices are matched on their EXACT float32 bits.  gmsh writes a shared vertex as the same
    float32 in every facet that carries it, so exact matching is correct here -- and the
    MANIFOLD RATE is returned so that an assumption which stopped being true announces itself
    instead of quietly halving the adjacency.
    """
    n, c, area, h = facet_frame(tris)
    key = np.ascontiguousarray(tris.reshape(-1, 3).astype(np.float32)).view(np.int32)
    kview = key.reshape(-1, 3).copy().view([('a', np.int32), ('b', np.int32),
                                            ('c', np.int32)]).ravel()
    uniq, vid = np.unique(kview, return_inverse=True)
    vid = np.asarray(vid).reshape(-1, 3)
    nv = len(uniq)
    pos = np.zeros((nv, 3))
    pos[vid.ravel()] = tris.reshape(-1, 3)

    # area-weighted vertex normals: the normal belongs at the vertex, not at a facet centroid
    acc = np.zeros((nv, 3))
    w = n * area[:, None]
    flat = vid.ravel()
    for k in range(3):
        acc[:, k] = np.bincount(flat, weights=np.repeat(w[:, k], 3), minlength=nv)
    ln = np.linalg.norm(acc, axis=1)
    ln = np.where(ln == 0, 1.0, ln)
    N = acc / ln[:, None]

    e = np.concatenate([vid[:, [0, 1]], vid[:, [1, 2]], vid[:, [2, 0]]], axis=0)
    e = np.sort(e, axis=1).astype(np.int64)
    ek = e[:, 0] * np.int64(nv) + e[:, 1]
    euk, cnt = np.unique(ek, return_counts=True)
    eu = np.stack([euk // np.int64(nv), euk % np.int64(nv)], axis=1)
    manifold = float((cnt == 2).sum()) / len(eu) if len(eu) else 0.0

    # tangent frame per vertex, from the least-aligned cardinal axis
    ax = np.zeros((nv, 3))
    ax[np.arange(nv), np.argmin(np.abs(N), axis=1)] = 1.0
    t1 = np.cross(N, ax)
    t1 /= np.linalg.norm(t1, axis=1)[:, None]
    t2 = np.cross(N, t1)

    # directed edges, both ways
    u = np.concatenate([eu[:, 0], eu[:, 1]])
    v = np.concatenate([eu[:, 1], eu[:, 0]])
    dp = pos[v] - pos[u]
    dn = N[v] - N[u]
    a1 = np.einsum('ij,ij->i', dp, t1[u])
    a2 = np.einsum('ij,ij->i', dp, t2[u])
    b1 = np.einsum('ij,ij->i', dn, t1[u])
    b2 = np.einsum('ij,ij->i', dn, t2[u])

    # normal equations for x = [s11, s12, s22] from rows [a1,a2,0]->b1 and [0,a1,a2]->b2
    ATA = np.zeros((nv, 3, 3))
    ATb = np.zeros((nv, 3))
    rows = ((a1, a2, np.zeros_like(a1), b1), (np.zeros_like(a1), a1, a2, b2))
    for r0, r1, r2, rb in rows:
        R_ = (r0, r1, r2)
        for i in range(3):
            ATb[:, i] += np.bincount(u, weights=R_[i] * rb, minlength=nv)
            for j in range(3):
                ATA[:, i, j] += np.bincount(u, weights=R_[i] * R_[j], minlength=nv)
    ATA[:, 0, 0] += 1e-12
    ATA[:, 1, 1] += 1e-12
    ATA[:, 2, 2] += 1e-12
    x = np.linalg.solve(ATA, ATb[:, :, None])[:, :, 0]
    s11, s12, s22 = x[:, 0], x[:, 1], x[:, 2]
    tr = 0.5 * (s11 + s22)
    rt = np.sqrt(np.maximum(0.25 * (s11 - s22) ** 2 + s12 ** 2, 0.0))
    kv = np.maximum(np.abs(tr + rt), np.abs(tr - rt))
    kfac = np.median(kv[vid], axis=1)
    theta = np.arccos(np.clip(np.einsum('ij,ij->i', N[eu[:, 0]], N[eu[:, 1]]), -1.0, 1.0))
    return kfac, manifold, theta, h


def read_cad_curve_points(msh: str) -> np.ndarray:
    nodes, mode, first = [], None, True
    with open(msh) as fh:
        for ln in fh:
            s = ln.strip()
            if s.startswith('$'):
                mode = s[1:] if not s.startswith('$End') else None
                first = True
                continue
            if mode == 'Nodes':
                if first:
                    first = False
                    continue
                t = s.split()
                if len(t) == 4:
                    nodes.append((float(t[1]), float(t[2]), float(t[3])))
    return np.asarray(nodes)


def assert_units(tris: np.ndarray) -> float:
    pts = tris.reshape(-1, 3)
    rmax = float(np.hypot(pts[:, 1], pts[:, 2]).max())
    print('UNITS -- asserted against the known VP1304 diameter BEFORE any dimensional selector')
    print(f'  max radius about x in FILE UNITS      {rmax:.6f}')
    print(f'  known D (Report 3752 Table 1)         {D_KNOWN_M} m = {D_KNOWN_M*1000:g} mm')
    best = None
    for name, f in (('millimetres', 1e-3), ('centimetres', 1e-2),
                    ('metres', 1.0), ('inches', 0.0254)):
        ratio = 2 * rmax * f / D_KNOWN_M
        flag = ''
        if abs(ratio - 1.0) <= UNITS_TOL:
            flag, best = '   <== AGREES', name
        print(f'    as {name:12s}  D = {2*rmax*f:12.6f} m   ratio {ratio:12.6f}{flag}')
    if best != 'millimetres':
        raise SystemExit(f'*** REFUSE: the file does not read as millimetres (best: {best}). '
                         f'Every selector below is in mm.')
    print('  -> the file is in MILLIMETRES.  All selectors below are mm.\n')
    return rmax


# ------------------------------------------------------------------------------------ selftest
NOSE_GEO = """SetFactory("OpenCASCADE");
Cylinder(1) = {{0,0,0, 0,0,{T}, {R}}};
Cylinder(2) = {{{L},0,0, 0,0,{T}, {R}}};
Box(3) = {{0,{mR},0, {L}, {D}, {T}}};
BooleanUnion{{ Volume{{1}}; Delete; }}{{ Volume{{2}}; Volume{{3}}; Delete; }}
Mesh.MeshSizeFromCurvature = 0;
Mesh.MeshSizeFromPoints = 0;
Mesh.MeshSizeMin = {h};
Mesh.MeshSizeMax = {h};
Mesh.Algorithm = 6;
"""

CYL_GEO = """SetFactory("OpenCASCADE");
Cylinder(1) = {{0,0,0, 0,0,{L}, {R}}};
Mesh.MeshSizeFromCurvature = 0;
Mesh.MeshSizeFromPoints = 0;
Mesh.MeshSizeMin = {h};
Mesh.MeshSizeMax = {h};
Mesh.Algorithm = 6;
"""


def _recover(stl: str, keep, R: float):
    tris = read_stl(stl)
    n, c, area, hh = facet_frame(tris)
    m = keep(n, c, R)
    k, pr, theta, _ = discrete_curvature(tris)
    kv = k[m]
    kv = kv[kv > 0]
    if len(kv) < 10:
        return None, 0, 0.0
    return 1.0 / np.median(kv), int(m.sum()), float(np.median(hh[m]))


def selftest(h: float, radii) -> int:
    print('=== LADDER 1, CYLINDER -- the arm that shows the instrument CAN see a small radius.')
    print(f'    Known radius, tessellated at the blade facet size h = {h:g} mm, read by the')
    print('    SAME estimator.  A recovered radius is credible only where this is accurate.\n')
    print(f"{'R true':>9} {'facets':>9} {'h meas':>9} {'R/h':>7} {'R recov':>9} {'err %':>8}  verdict")
    ok = True
    for R in radii:
        with tempfile.TemporaryDirectory() as td:
            geo, stl = os.path.join(td, 'c.geo'), os.path.join(td, 'c.stl')
            with open(geo, 'w') as fh:
                fh.write(CYL_GEO.format(R=R, L=max(4 * R, 20 * h), h=h))
            r = subprocess.run(['gmsh', '-2', geo, '-o', stl, '-format', 'stl', '-bin',
                                '-nt', '2'], capture_output=True, text=True)
            if r.returncode != 0 or not os.path.exists(stl):
                print(f'{R:9.4f}   gmsh failed rc={r.returncode}')
                ok = False
                continue
            Rr, nn, hm = _recover(stl, lambda n, c, R: (np.abs(n[:, 2]) < 0.3) &
                                  (np.abs(np.hypot(c[:, 0], c[:, 1]) - R) < 0.25 * R), R)
        err = 100.0 * (Rr - R) / R
        print(f'{R:9.4f} {nn:9d} {hm:9.4f} {R/h:7.2f} {Rr:9.4f} {err:8.2f}  '
              f'{"OK" if abs(err) <= 5 else "MARGINAL" if abs(err) <= 15 else "OUTSIDE WINDOW"}')

    print('\n=== LADDER 2, NOSE -- AND THIS IS THE ONE THAT MATTERS.  A cylinder is curved')
    print('    everywhere; a LEADING EDGE is a rounded nose of radius R blending immediately')
    print('    into a nearly FLAT flank, and the vertex normals at the apex average the flank')
    print('    in.  The nose here is a semicylinder of radius R closing a flat slab of')
    print('    thickness 2R, tessellated at the same h.  If the two ladders disagree, the')
    print('    NOSE one governs, because it is the shape being measured.\n')
    print(f"{'R true':>9} {'facets':>9} {'h meas':>9} {'R/h':>7} {'R recov':>9} {'err %':>8}  verdict")
    lo_edge = None
    for R in radii:
        with tempfile.TemporaryDirectory() as td:
            geo, stl = os.path.join(td, 'n.geo'), os.path.join(td, 'n.stl')
            L = max(20 * R, 40 * h)
            with open(geo, 'w') as fh:
                fh.write(NOSE_GEO.format(R=R, L=L, T=max(4 * R, 20 * h), mR=-R, D=2 * R, h=h))
            r = subprocess.run(['gmsh', '-2', geo, '-o', stl, '-format', 'stl', '-bin',
                                '-nt', '2'], capture_output=True, text=True)
            if r.returncode != 0 or not os.path.exists(stl):
                print(f'{R:9.4f}   gmsh failed rc={r.returncode}')
                ok = False
                continue
            # the nose: facets on the cap of the first cylinder, x < 0
            Rr, nn, hm = _recover(stl, lambda n, c, R: (np.abs(n[:, 2]) < 0.3) & (c[:, 0] < 0),
                                  R)
        if Rr is None:
            print(f'{R:9.4f}   no nose facets selected')
            ok = False
            continue
        err = 100.0 * (Rr - R) / R
        v = 'OK' if abs(err) <= 5 else 'MARGINAL' if abs(err) <= 15 else 'OUTSIDE WINDOW'
        if v == 'OK' and lo_edge is None:
            lo_edge = R
        print(f'{R:9.4f} {nn:9d} {hm:9.4f} {R/h:7.2f} {Rr:9.4f} {err:8.2f}  {v}')
    print(f'\n  MEASURED lower edge of the NOSE window: R >= {lo_edge} mm at h = {h:g} mm'
          if lo_edge else '\n  NO nose radius recovered within 5 %')
    return 0 if ok else 2


# ---------------------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--stl')
    ap.add_argument('--cad-curves')
    ap.add_argument('--stations', default='0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.95')
    ap.add_argument('--cache')
    ap.add_argument('--selftest', action='store_true')
    ap.add_argument('--selftest-h', type=float, default=0.19)
    a = ap.parse_args()

    if a.selftest:
        return selftest(a.selftest_h, [0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0])

    tris = read_stl(a.stl)
    print(f'tessellation {a.stl}   {len(tris)} facets\n')
    assert_units(tris)

    lab = classify(tris)
    cache = a.cache or (os.path.splitext(a.stl)[0] + '.curv.npz')
    if os.path.exists(cache):
        z = np.load(cache)
        kmax, pair_rate, h = z['kmax'], float(z['pair_rate']), z['h']
        print(f'curvature READ FROM CACHE {cache}')
    else:
        kmax, pair_rate, theta, h = discrete_curvature(tris)
        np.savez_compressed(cache, kmax=kmax, pair_rate=pair_rate, h=h)
        print(f'curvature WRITTEN TO CACHE {cache}')
    print(f'ADJACENCY: {100*pair_rate:.3f} % of mesh edges are manifold (exactly 2 facets) on exact float32 vertex '
          f'identity.  A low rate would mean the estimator is reading fewer neighbours than\n'
          f'  the surface has, so it is printed rather than assumed.\n')

    # ---- IN-FILE CONTROL: the shaft is a cylinder of registered radius 20.000 mm ----------
    sh = lab == 'shaft'
    n, c, area, _ = facet_frame(tris)
    rc_ = np.hypot(c[:, 1], c[:, 2])
    wall = sh & (np.abs(rc_ - R_SHAFT) < 1.0) & (np.abs(n[:, 0]) < 0.3)
    kv = kmax[wall]
    kv = kv[kv > 0]
    Rrec = 1.0 / np.median(kv)
    err = abs(Rrec - R_SHAFT) / R_SHAFT
    print(f'IN-FILE CONTROL -- the shaft, a cylinder of REGISTERED radius {R_SHAFT:.3f} mm '
          f'(make_stl.py:R_SHAFT,\n  measured in GEOMETRY_ADMISSION_RECORD.md section 3), '
          f'read through the same reader and\n  classifier as the blade.')
    print(f'  {wall.sum()} wall facets, median h {np.median(h[wall]):.4f} mm'
          f'  ->  R recovered {Rrec:.4f} mm   error {100*err:.2f} %')
    if err > SHAFT_CONTROL_TOL:
        print(f'  *** REFUSE: the instrument cannot recover a KNOWN radius in this very file. '
              f'It is not evidence about an unknown one.')
        return 2
    print(f'  CONTROL PASSES (<= {100*SHAFT_CONTROL_TOL:g} %).  The estimator is believable '
          f'at R ~ {R_SHAFT:g} mm, h ~ 0.40 mm.\n')

    cad = read_cad_curve_points(a.cad_curves)
    cadr = np.hypot(cad[:, 1], cad[:, 2])
    cad = cad[cadr > 45.0]
    print(f'CAD curve reference: {len(cad)} nodes beyond r = 45 mm -- the trailing and tip '
          f'edges.\n  The leading edge has NO CAD curve (addendum D), so what survives the '
          f'{TE_EXCLUSION_MM:g} mm\n  exclusion IS the leading edge, by provenance.\n')

    tree = cKDTree(cad)
    bl = lab == 'blades'
    v0, v1, v2 = tris[:, 0], tris[:, 1], tris[:, 2]
    emax = np.max(np.stack([np.linalg.norm(v1 - v0, axis=1),
                            np.linalg.norm(v2 - v1, axis=1),
                            np.linalg.norm(v0 - v2, axis=1)], axis=1), axis=1)

    print(f"{'r/R':>6} {'chord':>8} {'t_max':>7} {'x_t':>6} {'end/check':>13} {'nWin':>5} "
          f"{'edge_LE':>7} {'R_LE':>8} {'R p99':>8} {'R/h':>6} {'dCAD':>7} {'R_TE':>8}  verdict")
    summary = {}
    for st in [float(x) for x in a.stations.split(',')]:
        rt = st * R_PROP
        band = np.where(bl & (np.abs(rc_ - rt) < SHELL_MM))[0]
        if len(band) < 500:
            print(f'{st:6.2f}   too few facets in the shell ({len(band)})')
            continue
        th = np.arctan2(c[band, 2], c[band, 1])
        o = np.argsort(th)
        ths = th[o]
        brk = np.where(np.diff(ths) > np.deg2rad(5))[0]
        groups = np.split(np.arange(len(ths)), brk + 1)
        if len(groups) > 1 and (ths[0] + 2 * np.pi - ths[-1]) < np.deg2rad(5):
            groups[0] = np.concatenate([groups[0], groups[-1]])
            groups = groups[:-1]
        groups = [g for g in groups if len(g) > 200]
        vals, chords = [], []
        for gi, g in enumerate(groups):
            idx = band[o[g]]
            t = np.arctan2(c[idx, 2], c[idx, 1])
            dt = (t - np.median(t) + np.pi) % (2 * np.pi) - np.pi
            P = np.column_stack([rt * dt, c[idx, 0]])
            P = P - P.mean(axis=0)
            ev, evec = np.linalg.eigh(np.cov(P.T))
            e = evec[:, np.argmax(ev)]
            sc = P @ e
            q = P @ np.array([-e[1], e[0]])
            sc = sc - sc.min()
            chord = sc.max()
            # point of maximum thickness, on a 25-bin profile
            E = np.linspace(0, chord, 26)
            thick = np.array([(np.ptp(q[(sc >= E[i]) & (sc < E[i + 1])])
                               if ((sc >= E[i]) & (sc < E[i + 1])).sum() > 2 else 0.0)
                              for i in range(25)])
            x_t = 0.5 * (E[np.argmax(thick)] + E[np.argmax(thick) + 1]) / chord

            # BOTH ends are measured.  The leading edge is chosen by CAD PROVENANCE -- the
            # trailing edge IS a CAD curve and the leading edge has none (addendum D) -- and
            # the MAXIMUM-THICKNESS test is reported beside it as an INDEPENDENT check.  A
            # disagreement is printed, never silently resolved: the first form of this loop
            # decided on thickness alone, and at r/R 0.80 and 0.90 the profile tied at
            # x_t = 0.50, so it picked the TRAILING edge on some blades and the leading edge
            # on others and averaged the two into one number.
            ends = {}
            for tag, win in (('lo', sc <= LE_WINDOW_MM), ('hi', sc >= chord - LE_WINDOW_MM)):
                wi = idx[win]
                if len(wi) < 20:
                    continue
                ends[tag] = dict(wi=wi, n=len(wi),
                                 R=1.0 / np.percentile(kmax[wi], 90),
                                 R99=1.0 / np.percentile(kmax[wi], 99),
                                 emx=float(np.median(emax[wi])),
                                 d=float(np.median(tree.query(c[wi], k=1)[0])))
            if len(ends) < 2:
                continue
            le_tag = max(ends, key=lambda t: ends[t]['d'])
            te_tag = 'hi' if le_tag == 'lo' else 'lo'
            thick_says = 'lo' if x_t < 0.5 else 'hi'
            agree = 'agree' if thick_says == le_tag else 'DISAGREE'
            if abs(x_t - 0.5) < 0.02:
                agree = 'undecided'
            ee = ends[le_tag]
            R50, R99, emx, dcad = ee['R'], ee['R99'], ee['emx'], ee['d']
            ratio = R50 / emx
            v = ('REFUSED -- the tessellation cannot represent this radius'
                 if ratio < REFUSE_R_OVER_H else
                 'ok' if ratio >= WARN_R_OVER_H else
                 f'ok BUT only {math.pi*ratio:.1f} facets span the nose')
            if agree == 'DISAGREE':
                v = 'REFUSED -- CAD provenance and max-thickness name DIFFERENT ends'
            if gi == 0:
                print(f'{st:6.2f} {chord:8.3f} {thick.max():7.3f} {x_t:6.2f} '
                      f'{le_tag:>3}/{agree:<9} {ee["n"]:5d} {emx:7.4f} {R50:8.4f} '
                      f'{R99:8.4f} {ratio:6.2f} {dcad:7.2f} {ends[te_tag]["R"]:8.4f}  {v}')
            if agree == 'DISAGREE':
                continue
            if ratio >= REFUSE_R_OVER_H:
                vals.append(R50)
            chords.append(chord)
        if vals:
            v = np.asarray(vals)
            summary[st] = (v.mean(), v.std(ddof=1) if len(v) > 1 else 0.0, len(v),
                           float(np.mean(chords)))
            print(f'{st:6.2f} {"ALL":>8}  chord {np.mean(chords):.3f} mm   R_LE mean '
                  f'{v.mean():.4f} mm  sd {v.std(ddof=1) if len(v)>1 else 0:.4f} over '
                  f'{len(v)} of {len(groups)} blades')
        else:
            summary[st] = (float("nan"), float("nan"), 0, float(np.mean(chords)) if chords else 0)
            print(f'{st:6.2f} {"ALL":>8}  REFUSED on all {len(groups)} blades -- '
                  f'the leading edge is finer than the tessellation that carries it')
    print('\n=== SPAN DISTRIBUTION, and what pre-registration 6.3 then demands ===')
    print('  SVA table check: C0.70 = 104.1670 mm published '
          '(sva_2011_smp11_case2_pptc_geometry_table)')
    print(f"{'r/R':>6} {'r mm':>8} {'chord':>9} {'R_LE mm':>9} {'sd':>8} {'blades':>7} "
          f"{'cell R/8':>9} {'cell R/4':>9}")
    for st, (m, sd, nb, ch) in summary.items():
        if nb:
            print(f'{st:6.2f} {st*R_PROP:8.2f} {ch:9.3f} {m:9.4f} {sd:8.4f} {nb:7d} '
                  f'{m/8:9.4f} {m/4:9.4f}')
        else:
            print(f'{st:6.2f} {st*R_PROP:8.2f} {ch:9.3f} {"REFUSED":>9} {"":>8} {0:7d} '
                  f'{"":>9} {"":>9}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
