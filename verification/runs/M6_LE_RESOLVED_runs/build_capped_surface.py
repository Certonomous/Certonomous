#!/usr/bin/env python3
"""TOOL 1 (Path A, grid-b) -- build a CAPPED pyHyp-marchable surface CGNS (ALL 9 master zones).

Fixes the tip-cap gap: gen_m6_gridb.py:master_surface_blocks() kept ONLY the two wing-surface
zones and DISCARDED the 7 collar zones that form the ROUNDED TIP CAP + TE/root closure, so its
surface was topologically open at the tip and TE (lane finding, cfd check-2 accepted). THIS tool
retains ALL 9 zones so pyHyp autoConnect stitches a closed, capped wing exactly as the native A3
march did.

MEASURED CONSTRAINT (this dafoam-team:v1 cgnsutilities build): the cgnsutilities Block CONSTRUCTOR
transposes VertexSize/CellSize on writeToCGNS for surface (nk=1) zones (VertexSize[0]=161 vs
CellSize[0]=256, reproduced on an unmodified block), so constructing NEW blocks -- the only way to
ADD chordwise points (gen's Lf=557 upsamples the native 257) -- is BLOCKED. Two operations that do
NOT change dims write cleanly:
  * cgnsutilities coarsen()  -- exact 2:1 coarsening, gives a 2n-1 EXACTLY-NESTED family
    (chord 257/129/65, span 161/81/41, cap 17/9/5), tested clean.
  * in-place COORDINATE redistribution at FIXED dims (add nose+shock clustering by moving the
    existing points along each chord line) -- writes cleanly (same mechanism TOOL 2 relies on).
CONSEQUENCE: the achievable finest surface is the NATIVE 257 chord; gen's Lf=557 (needed for the
shock-band curvature gate dx/c<=0.0012 -- native 257 fully clustered reaches only ~0.0033) is NOT
buildable here. That is a curvature-gate limitation FLAGGED for the supervisor, not waived.

RUNS IN the dafoam-team:v1 container (needs cgnsutilities); master surface read-only; writes only
under the mounted out path. Reuses gen_m6_gridb.clustering_distribution for the chord density.
"""
import argparse
import os
import sys

import numpy as np

# gen_m6_gridb is the SUPERSEDED re-loft recipe; it is imported LAZILY (only under --cluster)
# so the buildable NO-CLUSTER coarsen chain -- the one the coarsest/medium levels actually use --
# is reproducible WITHOUT it. NOTE (freeze-time, 2026-09-10): the --cluster branch below is not a
# viable production path on the cap-preserving route: (i) in-place per-zone clustering diverges the
# shared cap-edge nodes so pyHyp autoConnect fails ("Unknown topology"); (ii) the cgnsutilities
# Block-ctor transpose bug forbids ADDING chordwise points, so the buildable max is native 257,
# whose in-place-clustered shock Delta x/c ~0.0033 FAILS the prereg §3.4 gate (<=0.0012). The
# clustered graded surface the prereg specifies is therefore NOT buildable here -- supervisor ruling.


def _cluster_chord_inplace(block, t_chord):
    """Redistribute the CHORD-direction nodes (native dim was 257 -> the axis whose current length
    matches the clustering count is not known a-priori; the chord axis is the one that is NOT the
    span/cap). We identify chord as the axis whose coordinate varies most in x. Fixed dims."""
    c = np.array(block.coords)[:, :, 0, :]           # (n0,n1,3)
    dx0 = abs(c[-1, :, 0] - c[0, :, 0]).mean()
    dx1 = abs(c[:, -1, 0] - c[:, 0, 0]).mean()
    dz0 = abs(c[-1, :, 2] - c[0, :, 2]).mean()
    dz1 = abs(c[:, -1, 2] - c[:, 0, 2]).mean()
    chord_axis = 0 if (dx0 > dz0 and dx0 >= dx1) else (1 if dx1 > dz1 else None)
    if chord_axis is None:
        return                                       # pure cap corner: leave as-is
    n = c.shape[chord_axis]
    if len(t_chord) != n:
        t = np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(t_chord)), t_chord)
    else:
        t = np.asarray(t_chord)
    moved = np.moveaxis(c, chord_axis, 0)            # (n, other, 3)
    for b in range(moved.shape[1]):
        line = moved[:, b, :]
        order = np.argsort(line[:, 0]); xl = line[order]
        xs = xl[:, 0]; x_lo, x_hi = xs[0], xs[-1]; span = (x_hi - x_lo) or 1.0
        tx = (xs - x_lo) / span
        tx, uniq = np.unique(tx, return_index=True); xl = xl[uniq]
        new = np.empty((n, 3))
        for a in range(3):
            new[:, a] = np.interp(t, tx, xl[:, a])
        moved[:, b, :] = new
    c2 = np.moveaxis(moved, 0, chord_axis)
    block.coords = np.asfortranarray(c2[:, :, None, :])


def build(master_cgns, out_cgns, n_coarsen, cluster, level_id):
    from cgnsutilities import cgnsutilities as C
    g = C.readGrid(master_cgns)
    for _ in range(n_coarsen):
        g.coarsen()
    if cluster:
        sys.path.insert(0, os.environ.get("M6_RUN_DIR", "/run"))
        import gen_m6_gridb as G   # noqa: E402 -- lazy: only the superseded cluster path needs it
        G.load_sizing()
        t_chord, _ = G.clustering_distribution(
            g.blocks[0].dims[1], G.GEN_NOSE_TARGET, G.SHOCK_DXC, G.SHOCK_XC_LO, G.SHOCK_XC_HI)
        for b in g.blocks:
            _cluster_chord_inplace(b, t_chord)
    # DEFECT (measured 2026-09-10, dafoam-team:v1 cgnsutilities): g.connect() computes the block
    # 1-to-1 connectivity, but g.writeToCGNS() then ABORTS with "Invalid transformation index: 0.
    # The indices must all be between 1 and 2" when it writes that connectivity for these
    # degenerate-k (nk=1) surface zones -- the k-direction transform index is 0, which cgio rejects,
    # and the partial write collapses the file to the FIRST wing zone only (1 zone / 2665 nodes,
    # reproducing the very cap-less defect this tool exists to fix). Writing WITHOUT connect()
    # preserves all 9 coarsened zones (6765 nodes at coarsen=2, cap intact); pyHyp stitches the
    # zones itself at march time via autoConnect=True (driver_pyhyp_options / genWingMesh both set
    # it), so the on-disk 1-to-1 connectivity is not needed. g.connect() is therefore OMITTED.
    g.writeToCGNS(out_cgns)
    dims = [(b.name.decode() if isinstance(b.name, bytes) else b.name, list(b.dims))
            for b in g.blocks]
    print(f"WROTE {out_cgns}  coarsen={n_coarsen} cluster={cluster} level={level_id}")
    for name, d in dims:
        print(f"  {name:14s} {d}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--master", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--coarsen", type=int, default=2,
                    help="number of 2:1 coarsenings (2=coarsest Lc, 1=Lm, 0=native Lf)")
    ap.add_argument("--cluster", action="store_true",
                    help="add nose+shock chordwise clustering by in-place redistribution")
    ap.add_argument("--level", default="Lc")
    a = ap.parse_args()
    build(a.master, a.out, a.coarsen, a.cluster, a.level)
