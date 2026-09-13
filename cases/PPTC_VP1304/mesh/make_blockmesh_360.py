#!/usr/bin/env python3
"""FULL 360 degree background mesh for the PPTC VP1304 open-water act.

WHY A SECOND GENERATOR AND NOT A FLAG.  `make_blockmesh.py` builds exactly one topology: a
72 deg wedge closed by two CYCLIC patches.  A 360 deg domain is a DIFFERENT topology -- it
closes on itself and has NO cyclic patches at all -- and `blockMesh` cannot express it as a
wedge of half-angle 180 because the two closing faces would be coincident.  It needs a
multi-block annulus whose last azimuthal block's high face IS the first block's low face.
That is new code, and putting it behind a flag in the sector generator would put two
topologies in one function where the passage family depends on the other one being untouched.

EVERYTHING ELSE IS IMPORTED FROM THE SECTOR GENERATOR AND NOT RE-DERIVED -- the domain
extents, the radial and axial stations, the graded cell counts, and above all R_AXIS.  The
axis treatment earned its place: replacing the collapsed axis with a slip cylinder of radius
2 mm made the background 100 % hexahedral (hexRef8 requires 8 points per cell and a collapsed
pie slice is a 6-point prism) AND improved it -- max skewness 0.330 -> 0.273, max aspect
104.0 -> 87.6, small-determinant cells 252 -> 192, at an IDENTICAL cell count.

WHAT THIS DOMAIN BUYS, WHICH IS THE POINT OF BUILDING IT.  snappyHexMesh cannot extrude a
prism layer on a wall that TERMINATES ON A CYCLIC -- measured three times tonight, at two
different cell sizes, each time on a face lying exactly on a periodic plane:

    coarse, planes +-36.0000 deg : failing face at theta = -36.0000 deg, r = 110.6 mm (blade)
    coarse, planes rotated       : failing face at theta = -14.7170 deg, r =  35.4 mm (hub)
    medium, planes rotated       : failing face at theta = -14.7170 deg, r =  33.8 mm (hub)

The hub, cap and shaft are bodies of revolution and cross a periodic plane at EVERY wedge
phase, so no rotation can fix it on a sector.  A 360 deg domain HAS NO PERIODIC PLANES, so
the mechanism cannot fire and layers can carry all four registered patches of section 6.3.

THE AXIS IS STILL A SLIP CYLINDER, patch `axisRod`, type `patch` and NOT `wall` so it stays
out of wallDist and the k-omega SST wall treatment never measures a distance to it.
"""
from __future__ import annotations

import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_blockmesh import (                                    # noqa: E402
    D, X_INLET, X_OUTLET, R_OUTER, X_NEAR_FWD, X_NEAR_AFT, R_NEAR, R_AXIS, HEADER)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--case', required=True)
    ap.add_argument('--ratio', type=float, default=1.0,
                    help='family refinement ratio -- THE SAME numbers as the passage family, '
                         'so a full-360 level is comparable with the passage level of the '
                         'same ratio cell-for-cell')
    ap.add_argument('--blocks', type=int, default=4,
                    help='azimuthal BLOCKS around the annulus. Only the block count changes; '
                         'the azimuthal CELL count is fixed by --ratio so the mesh is '
                         'independent of it.')
    a = ap.parse_args()

    k = a.ratio
    nb = a.blocks

    def n(base):
        return max(1, int(math.ceil(base * k)))

    # 12 azimuthal cells per 72 deg in the passage family -> 60 per 360 deg, SAME cell size.
    n_theta_tot = n(60)
    n_theta_blk = max(1, int(math.ceil(n_theta_tot / nb)))
    n_theta_tot = n_theta_blk * nb          # the truth after rounding, reported below
    n_r_in, n_r_out = n(8), n(18)
    n_x_aft, n_x_mid, n_x_fwd = n(22), n(28), n(11)
    exp_r_out, exp_x_aft, exp_x_fwd = 8.0, 5.0, 3.0

    xs = [X_OUTLET, X_NEAR_AFT, X_NEAR_FWD, X_INLET]
    shells = (('axs', R_AXIS), ('in', R_NEAR), ('out', R_OUTER))
    v, idx = [], {}

    def add(key, p):
        idx[key] = len(v)
        v.append(p)

    # One ring of vertices per (station, shell), nb vertices around -- the ring CLOSES, so
    # block j uses j and (j+1) % nb and the last block's high face IS the first block's low
    # face. That closure is the whole topological difference from the wedge.
    for i, x in enumerate(xs):
        for name, rad in shells:
            for j in range(nb):
                t = 2.0 * math.pi * j / nb
                add((name, i, j), (x, rad * math.cos(t), rad * math.sin(t)))

    blocks, edges = [], []
    for i in range(3):
        nx = (n_x_aft, n_x_mid, n_x_fwd)[i]
        gx = (f'{1.0/exp_x_aft:g}', '1', f'{exp_x_fwd:g}')[i]
        for j in range(nb):
            jp = (j + 1) % nb
            b = [idx[('axs', i, j)], idx[('in', i, j)], idx[('in', i, jp)],
                 idx[('axs', i, jp)],
                 idx[('axs', i + 1, j)], idx[('in', i + 1, j)], idx[('in', i + 1, jp)],
                 idx[('axs', i + 1, jp)]]
            blocks.append((b, (n_r_in, n_theta_blk, nx), ('1', '1', gx)))
            b = [idx[('in', i, j)], idx[('out', i, j)], idx[('out', i, jp)],
                 idx[('in', i, jp)],
                 idx[('in', i + 1, j)], idx[('out', i + 1, j)], idx[('out', i + 1, jp)],
                 idx[('in', i + 1, jp)]]
            blocks.append((b, (n_r_out, n_theta_blk, nx), (f'{exp_r_out:g}', '1', gx)))

    # True arcs, not chords, on every ring -- the midpoint sits at the half angle.
    for i in range(len(xs)):
        for name, rad in shells:
            for j in range(nb):
                jp = (j + 1) % nb
                tm = 2.0 * math.pi * (j + 0.5) / nb
                edges.append((idx[(name, i, j)], idx[(name, i, jp)],
                              (xs[i], rad * math.cos(tm), rad * math.sin(tm))))

    out = [HEADER, 'vertices\n(\n']
    for p in v:
        out.append(f'    ({p[0]:.8g} {p[1]:.8g} {p[2]:.8g})\n')
    out.append(');\n\nblocks\n(\n')
    for b, nn, gg in blocks:
        out.append(f'    hex ({" ".join(str(q) for q in b)}) '
                   f'({nn[0]} {nn[1]} {nn[2]}) simpleGrading ({gg[0]} {gg[1]} {gg[2]})\n')
    out.append(');\n\nedges\n(\n')
    for p0, p1, m in edges:
        out.append(f'    arc {p0} {p1} ({m[0]:.8g} {m[1]:.8g} {m[2]:.8g})\n')
    out.append(');\n\nboundary\n(\n')

    def emit(name, typ, faces):
        out.append(f'    {name}\n    {{\n        type {typ};\n        faces\n        (\n')
        for f in faces:
            out.append(f'            ({" ".join(str(q) for q in f)})\n')
        out.append('        );\n    }\n')

    inlet, outlet, outer, rod = [], [], [], []
    for j in range(nb):
        jp = (j + 1) % nb
        inlet.append([idx[('axs', 3, j)], idx[('axs', 3, jp)], idx[('in', 3, jp)],
                      idx[('in', 3, j)]])
        inlet.append([idx[('in', 3, j)], idx[('in', 3, jp)], idx[('out', 3, jp)],
                      idx[('out', 3, j)]])
        outlet.append([idx[('axs', 0, j)], idx[('in', 0, j)], idx[('in', 0, jp)],
                       idx[('axs', 0, jp)]])
        outlet.append([idx[('in', 0, j)], idx[('out', 0, j)], idx[('out', 0, jp)],
                       idx[('in', 0, jp)]])
        for i in range(3):
            outer.append([idx[('out', i, j)], idx[('out', i + 1, j)],
                          idx[('out', i + 1, jp)], idx[('out', i, jp)]])
            rod.append([idx[('axs', i, j)], idx[('axs', i, jp)],
                        idx[('axs', i + 1, jp)], idx[('axs', i + 1, j)]])

    emit('inlet', 'patch', inlet)
    emit('outlet', 'patch', outlet)
    emit('outerBoundary', 'patch', outer)
    # `patch`, NOT `wall` -- see the module docstring.
    emit('axisRod', 'patch', rod)
    out.append(');\n\nmergePatchPairs\n(\n);\n\n'
               '// ************************************************************************* //\n')

    p = os.path.join(a.case, 'system', 'blockMeshDict')
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w') as fh:
        fh.write(''.join(out))

    total = sum(nn[0] * nn[1] * nn[2] for _, nn, _ in blocks)
    print(f'wrote {p}')
    print(f'  FULL 360 deg annulus -- NO CYCLIC PATCHES, {nb} azimuthal blocks that CLOSE')
    print(f'  family ratio {k}, azimuthal cells {n_theta_tot} '
          f'({n_theta_blk} per block x {nb})')
    print(f'  cells: radial {n_r_in}+{n_r_out}, axial {n_x_aft}+{n_x_mid}+{n_x_fwd}'
          f'  -> background {total} cells')
    print(f'  patches: inlet, outlet, outerBoundary, axisRod   (four, and none of them cyclic)')
    rnear = R_NEAR
    print(f'  near-field cell at the blade tip: r.dtheta '
          f'{2*math.pi*0.125/n_theta_tot*1000:.1f} mm')
    print(f'  axis is a slip cylinder at r = {R_AXIS*1000:g} mm, patch axisRod, type patch')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
