#!/usr/bin/env python3
"""Is the surface tessellation fine enough for the mesh level that will snap to it?

WHY THIS EXISTS.  snappyHexMesh snaps to the STL, so the STL *is* the geometry.  If a level's
surface cells are smaller than the STL's local facets, that level is snapping to a geometry
coarser than its own mesh can resolve, and refinement stops buying geometric fidelity.  The
family then converges — smoothly, with good residuals — to the wrong answer, and CHECKMESH
FLAGS NOTHING.  There is no residual signature for this failure.

THE STATISTIC IS AREA-WEIGHTED, AND THAT IS THE WHOLE POINT.  This check was written because
a COUNT-weighted median edge length (0.539 mm on the blades) was reported as evidence of
adequacy when the AREA-weighted facet size was 2.995 mm — a factor of five and a half, in the
direction that made a badly coarse tessellation look fine.  Curvature-driven refinement puts
thousands of tiny facets along the leading and trailing edges; they are numerous and carry
almost no area.  The flat panels in the middle of a blade are few and carry nearly all of it.
That is exactly `docs/NUMERICS_KNOWLEDGE.md` N-X5: a count share OVERSTATES the weighted share
of anything concentrated in refinement.  A count is a locator, never a magnitude.

REGISTERED VERDICTS, by the percentage of a patch's AREA carried by facets larger than that
level's surface cell size:

    <= 5 %      PASS                  the level resolves the geometry it snaps to
    5 - 20 %    MARGINAL              usable, disclosed on the certificate with the number
    > 20 %      TESSELLATION-LIMITED  the level is disclosed as limited above a stated size,
                                      or the tessellation is regenerated

Exit 2 if any level is TESSELLATION-LIMITED, so this refuses rather than warns.
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from stl_metrics import read_stl                      # noqa: E402
sys.path.insert(0, os.path.dirname(__file__))
from make_stl import classify, PATCHES                # noqa: E402

PASS_PCT = 5.0
MARGINAL_PCT = 20.0


def facet_size(tris: np.ndarray):
    """(area, representative facet dimension) — the edge of the equilateral triangle of equal
    area, so a sliver is not credited with the length of its long side."""
    v0, v1, v2 = tris[:, 0], tris[:, 1], tris[:, 2]
    a = 0.5 * np.linalg.norm(np.cross(v1 - v0, v2 - v0), axis=1)
    return a, np.sqrt(4.0 * a / np.sqrt(3.0))


def area_weighted_pct(a: np.ndarray, h: np.ndarray, q: float) -> float:
    o = np.argsort(h)
    cw = np.cumsum(a[o]) / a.sum()
    return float(np.interp(q, cw, h[o]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--stl', required=True, help='tessellated CAD, in the CAD units (mm)')
    ap.add_argument('--levels', default='coarse=0.625,medium=0.417,fine=0.278',
                    help='surface cell size per family level, mm')
    a = ap.parse_args()

    levels = []
    for tok in a.levels.split(','):
        k, v = tok.split('=')
        levels.append((k.strip(), float(v)))

    tris = read_stl(a.stl)
    lab = classify(tris)
    ar, h = facet_size(tris)

    print(f'tessellation: {a.stl}  ({len(tris)} triangles)')
    print('AREA-WEIGHTED facet size, mm  (a count-weighted one would flatter this by ~5x)\n')
    print(f"{'patch':>8} {'p50':>8} {'p90':>8} {'p99':>8} {'max':>8}")
    groups = {}
    for p in PATCHES[:4]:
        m = lab == p
        if m.sum() == 0:
            continue
        groups[p] = (ar[m], h[m])
        print(f'{p:>8} {area_weighted_pct(ar[m], h[m], 0.50):8.3f} '
              f'{area_weighted_pct(ar[m], h[m], 0.90):8.3f} '
              f'{area_weighted_pct(ar[m], h[m], 0.99):8.3f} {h[m].max():8.3f}')

    print(f'\n% of patch AREA on facets LARGER than the level surface cell '
          f'(PASS <= {PASS_PCT:g}%, MARGINAL <= {MARGINAL_PCT:g}%)\n')
    hdr = f"{'level':>8} {'cell mm':>9} " + ''.join(f'{p:>12}' for p in groups)
    print(hdr)
    worst = 0.0
    verdicts = {}
    for name, s in levels:
        row = f'{name:>8} {s:9.3f} '
        lv = 0.0
        for p, (aa, hh) in groups.items():
            frac = 100.0 * aa[hh > s].sum() / aa.sum()
            lv = max(lv, frac)
            row += f'{frac:11.1f}%'
        verdicts[name] = ('PASS' if lv <= PASS_PCT else
                          'MARGINAL' if lv <= MARGINAL_PCT else 'TESSELLATION-LIMITED')
        worst = max(worst, lv)
        print(row + f'   -> {verdicts[name]}')

    print()
    bad = [k for k, v in verdicts.items() if v == 'TESSELLATION-LIMITED']
    if bad:
        print(f'REFUSE: {", ".join(bad)} snap to a geometry coarser than their own cells. '
              f'Worst patch share {worst:.1f}%.')
        print('  Regenerate the tessellation with MeshSizeMax at or below the finest surface')
        print('  cell, or disclose the family as tessellation-limited above a stated level.')
        print('  MeshSizeMax is the binding constraint: curvature refinement never governs a')
        print('  flat panel, which is where nearly all the area lives.')
        return 2
    print(f'ADEQUACY PASS for every level. Worst patch area share {worst:.1f}%.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
