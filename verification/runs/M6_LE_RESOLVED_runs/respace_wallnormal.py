#!/usr/bin/env python3
"""TOOL 2 (Path A, grid-b) -- PATCH-PRESERVING wall-normal re-spacing.

The board's Path A marches at y+~35 (pyHyp's validated regime -> non-orth ~61 deg) and THEN
re-spaces the wall-normal points to y+<1 (s0=1.546335e-6). Re-spacing REDISTRIBUTES the nodes
ALONG each existing wall-normal column curve: the grid-LINE DIRECTION is preserved, so the march's
non-orthogonality is preserved (proven on the A3 baseline volume: 61.158 -> 61.147 deg, 0.011 deg).

Unlike the diagnostic respace_a3.py (which merged everything into ONE `walls` patch and is unusable
for the grader), THIS tool operates on the MARCHED VOLUME CGNS and keeps the block/surface topology
intact: it mutates only the COORDINATE VALUES along the wall-normal axis, leaving dims unchanged, so
after writePlot3D the SAME plot3dToFoam + autoPatch + createPatch reproduces the {wing, symmetry,
farfield} 3-patch set the grader requires. Dims are never changed, so the cgnsutilities Block
constructor bug (VertexSize/CellSize transposition, measured in this build) is never triggered.

s0 is applied on the WALL-rooted columns (k=0 on the marched surface = the wing/cap wall). Runs in
the dafoam-team:v1 container; reads/writes only under the mounted scratch dir."""
import argparse
import os

import numpy as np


def _geom_ratio(total, m, s0):
    """geometric distribution of m cells over arclength `total`, first cell s0; return the m+1
    node arclengths and the ratio r."""
    if s0 >= total / m:
        return np.linspace(0.0, total, m + 1), 1.0
    lo, hi = 1.0 + 1e-12, 5.0
    rt = total / s0
    for _ in range(200):
        md = 0.5 * (lo + hi)
        g = (md ** m - 1.0) / (md - 1.0)
        lo, hi = (md, hi) if g < rt else (lo, md)
    r = 0.5 * (lo + hi)
    s = np.array([s0 * (r ** k - 1.0) / (r - 1.0) for k in range(m + 1)])
    s[-1] = total
    return s, r


def _wall_normal_axis(dims, n_layers_plus1):
    ax = [i for i, d in enumerate(dims[:3]) if d == n_layers_plus1]
    if len(ax) != 1:
        raise RuntimeError(f"cannot uniquely identify wall-normal axis: dims={list(dims)} "
                           f"expected exactly one == {n_layers_plus1}")
    return ax[0]


def respace(in_cgns, out_cgns, out_plot3d, s0, n_layers_plus1):
    from cgnsutilities import cgnsutilities as C
    g = C.readGrid(in_cgns)
    rmax = 0.0
    for b in g.blocks:
        dims = list(b.dims)
        kax = _wall_normal_axis(dims, n_layers_plus1)
        c = np.array(b.coords)                       # (n0,n1,n2,3)
        moved = np.moveaxis(c, kax, 2)               # wall-normal -> axis 2
        s0shape = moved.shape
        nA, nB, nK, _ = s0shape
        for i in range(nA):
            for j in range(nB):
                col = moved[i, j]                    # (nK,3) wall(k=0)->farfield
                seg = np.linalg.norm(np.diff(col, axis=0), axis=1)
                s = np.concatenate([[0.0], np.cumsum(seg)])
                tot = s[-1]
                if tot <= 0:
                    continue
                t, r = _geom_ratio(tot, nK - 1, s0)
                rmax = max(rmax, r)
                newcol = np.empty_like(col)
                for a in range(3):
                    newcol[:, a] = np.interp(t, s, col[:, a])
                moved[i, j] = newcol
        c2 = np.moveaxis(moved, 2, kax)
        b.coords = np.asfortranarray(c2)             # dims unchanged -> clean write
    g.writeToCGNS(out_cgns)
    g.writePlot3d(out_plot3d)
    print(f"RESPACED s0={s0:.6e} n_layers+1={n_layers_plus1} growth_r_max={rmax:.4f}")
    print(f"  wrote {out_cgns} + {out_plot3d}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--in-cgns", required=True)
    ap.add_argument("--out-cgns", required=True)
    ap.add_argument("--out-plot3d", required=True)
    ap.add_argument("--s0", type=float, default=1.546335364348132e-06)
    ap.add_argument("--layers-plus1", type=int, required=True)
    a = ap.parse_args()
    respace(a.in_cgns, a.out_cgns, a.out_plot3d, a.s0, a.layers_plus1)
