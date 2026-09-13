#!/usr/bin/env python3
"""Leading-edge radius of the PPTC blade, read off the mesher instead of fitted.

THE METHOD.  gmsh's curvature-driven sizing sets element size h = 2*pi*R_curv / N, where N is
`Mesh.MeshSizeFromCurvature`.  So on a tessellation whose size is set by CURVATURE, the facet
size is a DIRECT READOUT of the local radius of curvature:

    R_curv = N * h / (2 * pi)

No circle fitting.  No chord-extremum search.  Both of those failed on this geometry
(`MESH_PIPELINE_RECORD.md` correction 1 addendum E: six of eight stations refused to fit, the
two that fitted carried residuals at 40-46 % of the fitted radius, and widening the sampling
shell moved the measured chord by 9 %, so the "ends" the search found were not stably the
leading and trailing edges).

THE GUARD, AND IT IS THE WHOLE POINT.  **The readout is valid ONLY where curvature is the
BINDING constraint.**  A facet sized by `MeshSizeMin`, by `MeshSizeMax`, or by a background
size field reports THAT constraint and not the radius -- and it reports it as a confident
number rather than as a refusal, which is worse than an honest bound.

That is not hypothetical: it is exactly how the first attempt went wrong.  On the earlier
tessellation, N = 12 with a 0.40 mm floor, the leading-edge facets sat ON the floor, so the
data could only ever yield R <= 12 * 0.40 / (2*pi) = 0.764 mm.  Circles were being fitted to
points whose spacing was set by a clamp rather than by the geometry.

So every facet is classified -- CURVATURE-bound, FLOOR-bound or MAX-bound -- and a station
where the floor or the max binds on a material fraction of its leading-edge facets is
**REFUSED, not averaged**.  The bound fraction is reported per station beside the radius, so a
floor that was not low enough announces itself instead of being assumed away.

SEPARATING THE LEADING EDGE FROM THE TRAILING EDGE.  Both are high-curvature bands, and the
trailing edge is the sharper of the two ("The trailing edge for the upper propeller radii is
sharp" -- smp'11 geometry sheet).  They are separated by PROVENANCE rather than by curvature:
the trailing edge IS a CAD curve -- one of the five 114.465 mm root-to-tip curves measured in
addendum D -- while the leading edge has no CAD edge at all.  Facets near those curves are
therefore trailing edge by construction, and the remaining high-curvature band is the leading
edge.  The CAD curves come from `gmsh -1`, which meshes them independently of any surface.
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
BOUND_TOL = 0.05          # a facet within 5 % of a clamp is taken as bound by it
REFUSE_BOUND_PCT = 20.0   # refuse a station if this much of its LE facets are clamp-bound
TE_EXCLUSION_MM = 1.5     # facets this close to a CAD curve are trailing edge or tip


def read_cad_curve_points(msh: str) -> np.ndarray:
    """Node coordinates of the CAD's own 1D curve mesh (gmsh -1, msh2)."""
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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--stl', required=True)
    ap.add_argument('--cad-curves', required=True, help='gmsh -1 output (.msh, format msh2)')
    ap.add_argument('--curvature-n', type=float, required=True, help='Mesh.MeshSizeFromCurvature')
    ap.add_argument('--floor', type=float, required=True, help='Mesh.MeshSizeMin, mm')
    ap.add_argument('--ceiling', type=float, required=True, help='Mesh.MeshSizeMax, mm')
    ap.add_argument('--stations', default='0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.95')
    a = ap.parse_args()

    tris = read_stl(a.stl)
    lab = classify(tris)
    bl = tris[lab == 'blades']
    v0, v1, v2 = bl[:, 0], bl[:, 1], bl[:, 2]
    area = 0.5 * np.linalg.norm(np.cross(v1 - v0, v2 - v0), axis=1)
    h = np.sqrt(4.0 * area / np.sqrt(3.0))
    cen = bl.mean(axis=1)
    rad = np.hypot(cen[:, 1], cen[:, 2])

    floor_bound = h <= a.floor * (1.0 + BOUND_TOL)
    max_bound = h >= a.ceiling * (1.0 - BOUND_TOL)
    curv_bound = ~(floor_bound | max_bound)
    R_read = a.curvature_n * h / (2.0 * math.pi)

    print(f'tessellation {a.stl}')
    print(f'  curvature N = {a.curvature_n:g}, floor = {a.floor:g} mm, ceiling = {a.ceiling:g} mm')
    print(f'  blade facets {len(bl)}:  curvature-bound {100*curv_bound.mean():.1f}%, '
          f'floor-bound {100*floor_bound.mean():.1f}%, max-bound {100*max_bound.mean():.1f}%')
    print(f'  if every LE facet were floor-bound the data would yield only the BOUND '
          f'R <= {a.curvature_n*a.floor/(2*math.pi):.4f} mm\n')

    cad = read_cad_curve_points(a.cad_curves)
    cadr = np.hypot(cad[:, 1], cad[:, 2])
    cad = cad[cadr > 30.0]                      # blade-region CAD curves: TE and tip
    print(f'  CAD curve reference: {len(cad)} nodes beyond r = 30 mm '
          f'(trailing and tip edges; the LE has none -- addendum D)\n')

    print(f"{'r/R':>6} {'nLE':>6} {'clamp%':>7} {'R p50':>8} {'R p10':>8} {'R p90':>8}  verdict")
    for st in [float(x) for x in a.stations.split(',')]:
        rt = st * R_PROP
        band = np.abs(rad - rt) < 1.0
        if band.sum() < 50:
            print(f'{st:6.2f} {"":>6} {"":>7}   too few facets in the radial band')
            continue
        idx = np.where(band)[0]
        # drop facets near any CAD curve -- those are trailing edge or tip, by provenance
        c = cen[idx]
        keep = np.ones(len(idx), dtype=bool)
        for k in range(len(idx)):
            if np.min(np.linalg.norm(cad - c[k], axis=1)) < TE_EXCLUSION_MM:
                keep[k] = False
        idx = idx[keep]
        if len(idx) < 30:
            print(f'{st:6.2f} {len(idx):6d} {"":>7}   too few facets after excluding the CAD edges')
            continue
        # the leading edge is the remaining highest-curvature band: smallest facets
        thr = np.percentile(h[idx], 10)
        le = idx[h[idx] <= thr]
        clamp = 100.0 * (floor_bound[le] | max_bound[le]).mean()
        good = le[curv_bound[le]]
        if clamp > REFUSE_BOUND_PCT or len(good) < 20:
            print(f'{st:6.2f} {len(le):6d} {clamp:6.1f}%   REFUSED -- the clamp binds on '
                  f'{clamp:.1f}% of the leading-edge facets, so these report the clamp and '
                  f'not the radius')
            continue
        Rv = R_read[good]
        print(f'{st:6.2f} {len(le):6d} {clamp:6.1f}% {np.percentile(Rv,50):8.4f} '
              f'{np.percentile(Rv,10):8.4f} {np.percentile(Rv,90):8.4f}  ok')

    print('\nA REFUSED station is not a missing number -- it is the instrument declining to '
          'report a clamp as a radius.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
