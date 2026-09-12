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
from make_snappy import LEVELS                        # noqa: E402

# Near-field background cell at family ratio 1.0, millimetres, from make_blockmesh.py.
# ONE SOURCE OF TRUTH: the surface cell each patch achieves is background / 2^level, and the
# levels come from make_snappy.py rather than being retyped here, so the gate cannot drift
# away from the dictionary it is gating.
BACKGROUND_MM = 20.0
FAMILY = (('coarse', 1.00), ('medium', 1.50), ('fine', 2.25))


def surface_cell(patch: str, ratio: float) -> float:
    return (BACKGROUND_MM / ratio) / 2 ** LEVELS[patch][1]

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
    a = ap.parse_args()

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

    print(f'\n% of patch AREA on facets LARGER than THAT PATCH\'S OWN surface cell '
          f'(PASS <= {PASS_PCT:g}%, MARGINAL <= {MARGINAL_PCT:g}%)')
    print('  The cell differs per patch because the refinement level does: the blades carry KQ')
    print('  and the graded loading, the hub, cap and shaft carry only thrust and are smooth')
    print('  bodies of revolution. Resolution follows the geometry.\n')
    worst = 0.0
    verdicts = {}
    bad = []
    for name, ratio in FAMILY:
        print(f'  {name} (family ratio {ratio:g}, background {BACKGROUND_MM/ratio:.2f} mm)')
        lv = 'PASS'
        for p, (aa, hh) in groups.items():
            cell = surface_cell(p, ratio)
            frac = 100.0 * aa[hh > cell].sum() / aa.sum()
            worst = max(worst, frac)
            v = ('PASS' if frac <= PASS_PCT else
                 'MARGINAL' if frac <= MARGINAL_PCT else 'TESSELLATION-LIMITED')
            if v == 'TESSELLATION-LIMITED':
                lv = v
                bad.append(f'{name}/{p}')
            elif v == 'MARGINAL' and lv == 'PASS':
                lv = v
            print(f'    {p:>16} cell {cell:7.4f} mm   {frac:6.1f}% of area oversized   {v}')
        verdicts[name] = lv
        print(f'    -> {name}: {lv}\n')

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
