#!/usr/bin/env python3
"""Is pre-registration 6.3's LEADING-EDGE BAND buildable, and at what cost?

Everything here is arithmetic on MEASURED inputs, each named at the point of use:

  * R_LE(r/R)          -- `measure_le_curvature.py` on the production tessellation `prod7`,
                          five blades per station, recorded in LE_SPAN_prod7.txt.  These are
                          UPPER BOUNDS: the nose ladder over-reports a nose it cannot span,
                          and the cm1-versus-prod7 comparison shows the value still falling
                          with tessellation refinement.
  * LE path length     -- measured here, from the leading-edge facets themselves.
  * meshing rate       -- 19 700 035 cells in 12 538.33 s on 1 rank (F360_coarse
                          log.snappyHexMesh, "Finished meshing in") = 10.61 core-min per
                          million cells.  MEASURED on this case, this CAD, this box.
  * tessellation rate  -- prod7: 7 230 286 facets, gmsh CPU 11 439.9 s (log.prod7)
                          = 1.582 ms per facet.  MEASURED, and the record's own evidence
                          (addendum C: 4 of 5 curvature-driven runs KILLED) says it is a
                          FLOOR, not a prediction.

THE TWO CONSTRAINTS ARE INDEPENDENT AND BOTH MUST HOLD.  A refinement level buys nothing
unless the STL it snaps to carries facets at least as fine as the cell.  snappyHexMesh snaps
to the triangulation; below the facet size the surface IS flat, and refinement past it adds
cells that resolve a polyhedron rather than a propeller -- with no residual signature and no
checkMesh complaint.
"""
from __future__ import annotations

import argparse
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from stl_metrics import read_stl                      # noqa: E402
sys.path.insert(0, os.path.dirname(__file__))
from make_stl import classify                         # noqa: E402

R_PROP = 125.0
BG_FINE_MM = 8.9          # fine-level near-field background cell (make_snappy.py docstring)
FAMILY_BG = (('coarse', 20.0), ('medium', 13.3), ('fine', 8.9))
MESH_CORE_MIN_PER_MCELL = 12538.33 / 60.0 / 19.700035   # MEASURED, F360_coarse
TESS_MS_PER_FACET = 11439.9 * 1000.0 / 7230286.0        # MEASURED, prod7

# MEASURED span distribution, prod7, from LE_SPAN_prod7.txt.  r/R -> (R_LE mm, facet mm).
SPAN = {0.35: (1.9068, 0.2163), 0.40: (1.0728, 0.2260), 0.45: (0.9366, 0.2157),
        0.50: (0.7162, 0.2101), 0.55: (0.4733, 0.1743), 0.60: (0.3408, 0.1272),
        0.65: (0.2542, 0.0740), 0.70: (0.1938, 0.0722), 0.75: (0.1446, 0.0639),
        0.80: (0.1062, 0.0393), 0.85: (0.0836, 0.0451), 0.90: (0.0562, 0.0374),
        0.95: (0.0723, 0.0376)}


def le_path_length(stl: str, cad_msh: str) -> float:
    """Arc length of the leading-edge path, measured from the leading-edge facets."""
    from scipy.spatial import cKDTree
    from measure_le_curvature import (facet_frame, read_cad_curve_points, SHELL_MM,
                                      LE_WINDOW_MM)
    tris = read_stl(stl)
    lab = classify(tris)
    n, c, area, h = facet_frame(tris)
    rc = np.hypot(c[:, 1], c[:, 2])
    bl = lab == 'blades'
    cad = read_cad_curve_points(cad_msh)
    cad = cad[np.hypot(cad[:, 1], cad[:, 2]) > 45.0]
    tree = cKDTree(cad)
    pts = []
    ref_ang = [None]
    for st in np.arange(0.30, 0.995, 0.01):
        rt = st * R_PROP
        band = np.where(bl & (np.abs(rc - rt) < SHELL_MM))[0]
        if len(band) < 500:
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
        if not groups:
            continue
        # ONE BLADE, FOLLOWED ACROSS THE SPAN.  Taking the largest group at each station
        # silently changes blade from station to station: the first form of this did, and the
        # polyline then jumped a chord length (~100 mm) at each change, reporting a leading
        # edge 6 461 mm long on a blade 86 mm tall.  The blade is pinned by ANGLE to the one
        # chosen at the first station and carried forward.
        angs = [float(np.median(np.arctan2(c[band[o[g]], 2], c[band[o[g]], 1]))) for g in groups]
        if ref_ang[0] is None:
            ref_ang[0] = angs[0]
        j = int(np.argmin([abs((aa - ref_ang[0] + np.pi) % (2 * np.pi) - np.pi) for aa in angs]))
        ref_ang[0] = angs[j]
        idx = band[o[groups[j]]]
        t = np.arctan2(c[idx, 2], c[idx, 1])
        dt = (t - np.median(t) + np.pi) % (2 * np.pi) - np.pi
        P = np.column_stack([rt * dt, c[idx, 0]])
        Pm = P - P.mean(axis=0)
        ev, evec = np.linalg.eigh(np.cov(Pm.T))
        e = evec[:, np.argmax(ev)]
        sc = Pm @ e
        sc = sc - sc.min()
        ends = {}
        for tag, win in (('lo', sc <= LE_WINDOW_MM), ('hi', sc >= sc.max() - LE_WINDOW_MM)):
            wi = idx[win]
            if len(wi) >= 20:
                ends[tag] = (float(np.median(tree.query(c[wi], k=1)[0])), c[wi].mean(axis=0))
        if len(ends) < 2:
            continue
        pts.append(max(ends.values(), key=lambda z: z[0])[1])
    P = np.asarray(pts)
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    # a segment longer than 5 mm between stations 1.25 mm apart in radius is the end-selection
    # having flipped ends; it is DROPPED and counted, never averaged in.
    good = seg < 5.0
    return float(seg[good].sum() * len(seg) / max(good.sum(), 1)), len(P), int((~good).sum())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--stl', required=True)
    ap.add_argument('--cad-curves', required=True)
    ap.add_argument('--band-mm', type=float, default=1.0,
                    help='radius of the refinement tube about the LE path, mm')
    a = ap.parse_args()

    L, npts, nflip = le_path_length(a.stl, a.cad_curves)
    print(f'LEADING-EDGE PATH, measured from the leading-edge facets of {os.path.basename(a.stl)}')
    print(f'  {npts} stations from r/R 0.30 to 0.99 on ONE blade, polyline length '
          f'{L:.3f} mm per blade')
    print(f'  {nflip} of {npts-1} segments rejected as end-selection flips (> 5 mm) and '
          f'the remainder rescaled')
    print(f'  for scale, the CAD trailing-edge curve is 114.465 mm (addendum D)\n')

    print('WHAT THE CLAUSE DEMANDS, STATION BY STATION -- literal parse (cell <= R_LE/8),')
    print('registered as governing by addendum E.5.\n')
    print(f"{'r/R':>6} {'R_LE mm':>9} {'cell R/8':>9} {'fine lvl':>9} {'lvl cell':>9} "
          f"{'STL facet':>10} {'facet/cell':>11}  can the STL carry it?")
    need_level = {}
    for st, (R, hf) in SPAN.items():
        need = R / 8.0
        lvl = math.ceil(math.log2(BG_FINE_MM / need))
        cell = BG_FINE_MM / 2 ** lvl
        need_level[st] = lvl
        ratio = hf / cell
        ok = 'YES' if hf <= cell else f'NO -- facet is {ratio:.1f}x the cell'
        print(f'{st:6.2f} {R:9.4f} {need:9.4f} {lvl:9d} {cell:9.5f} {hf:10.4f} '
              f'{ratio:11.1f}  {ok}')

    print(f'\nWHAT EACH LEVEL BUYS -- the outermost radius at which 8 cells span R_LE,')
    print(f'and the cells a tube of radius {a.band_mm:g} mm about the LE path would add.\n')
    print(f"{'level':>6} {'cell mm':>9} {'covers to':>10} {'cells/blade':>13} "
          f"{'passage tot':>13} {'core-min':>11} {'STL facets':>12} {'tess core-min':>14}")
    sts = sorted(SPAN)
    for lvl in range(5, 13):
        cell = BG_FINE_MM / 2 ** lvl
        covered = [st for st in sts if SPAN[st][0] / 8.0 >= cell]
        cov = f'r/R {max(covered):.2f}' if covered else 'nothing'
        vol = math.pi * a.band_mm ** 2 * L
        cells = vol / cell ** 3
        # transition shells: nCellsBetweenLevels 3 down to the registered blade level 5
        r0 = a.band_mm
        for lv in range(lvl - 1, 4, -1):
            d = BG_FINE_MM / 2 ** lv
            r1 = r0 + 3 * d
            cells += math.pi * (r1 ** 2 - r0 ** 2) * L / d ** 3
            r0 = r1
        passage = 9.0e6 + cells                      # fine passage target + the band
        cmin = passage / 1e6 * MESH_CORE_MIN_PER_MCELL
        # the STL must carry facets <= cell over the band: area 2 x band x L x 5 blades
        fac = (2 * a.band_mm * L * 5) / (math.sqrt(3) / 4 * cell ** 2)
        tess = (fac + 7.23e6) * TESS_MS_PER_FACET / 1000.0 / 60.0
        print(f'{lvl:6d} {cell:9.5f} {cov:>10} {cells/1e6:12.2f}M {passage/1e6:12.2f}M '
              f'{cmin:11.0f} {fac/1e6:11.1f}M {tess:14.0f}')
    print(f'\nmeshing rate  {MESH_CORE_MIN_PER_MCELL:.2f} core-min per million cells '
          f'(MEASURED: F360_coarse, 19 700 035 cells, 12 538.33 s, 1 rank)')
    print(f'tessellation  {TESS_MS_PER_FACET:.3f} ms per facet '
          f'(MEASURED: prod7, 7 230 286 facets, gmsh CPU 11 439.9 s)')
    print('Both rates are FLOORS. snappyHexMesh cost per cell rises with refinement depth,')
    print('and addendum C records 4 of 5 curvature-driven gmsh runs on this CAD KILLED.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
