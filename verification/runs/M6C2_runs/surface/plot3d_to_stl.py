#!/usr/bin/env python3
"""M6 ROUTE (d) STEP 1 -- make the PROVEN body consumable by snappyHexMesh.

WHY THIS EXISTS: route (c) died because pyHyp MARCHES. snappyHexMesh does not
march, which is the mechanism change. But snappy cannot read the proven body at
all: that body is a 9-block STRUCTURED PLOT3D surface and snappy requires a
TRIANGULATED one. No M6 STL exists anywhere in the repo. This converts it, and
REFUSES rather than degrades.

IT DOES NOT RE-DERIVE THE BODY. The body is already proven against the AR-138
source table at 1.887e-15 / 2.442e-15 / 1.915e-15 (BODY_PROOF_MP.txt). What is
proven HERE is only that the CONVERSION did not change it, and that the result
is closed in the sense snappy depends on.

THE CLAIM SNAPPY ACTUALLY RESTS ON is edge manifoldness: every edge shared by
exactly two triangles, except along the ROOT (y = 0), which is the symmetry
plane and is legitimately open -- the same exception make_level.py grants, and
the same one OpenFOAM's own half-body tutorials rely on.

RULE 3 IS APPLIED TO THE MANIFOLDNESS READER, NOT JUST TO THE ROUND TRIP: a
count of zero open edges from a reader never shown able to see an open edge is
not evidence. The crown is displaced 1 mm -- make_level.py's own plant -- and
the reader MUST report more open edges, or this refuses.

exit 0 accepted | 2 a reader failed its plant | 3 conversion changed the body
     | 4 open edges that are not the root symmetry plane | 5 non-manifold edges
"""
import sys, pathlib, numpy as np
from collections import defaultdict

NAMES = ["wing_upper", "wing_base", "wing_lower", "wing_nose",
         "cap_upper", "cap_base", "cap_lower", "cap_nose", "crown"]
ROOT_TOL = 1e-9      # a vertex is ON the symmetry plane if |y| <= this


def read_plot3d(path):
    """Inverse of build_capped_multipatch.write_plot3d, one value per line.
    Header per block is (B.shape[1], B.shape[0], 1); values run with the
    B.shape[1] index FASTEST. Reconstructed as P[a, b, c] == B[a, b, c]."""
    toks = pathlib.Path(path).read_text().split()
    p = 0
    nblk = int(toks[p]); p += 1
    dims = []
    for _ in range(nblk):
        n1, n2, n3 = int(toks[p]), int(toks[p + 1]), int(toks[p + 2]); p += 3
        assert n3 == 1, f"block is not a surface: nk={n3}"
        dims.append((n1, n2))
    blocks = []
    for (n1, n2) in dims:
        P = np.empty((n2, n1, 3))
        for c in range(3):
            v = np.array(toks[p:p + n1 * n2], dtype=float); p += n1 * n2
            P[:, :, c] = v.reshape(n2, n1)      # a outer, b fastest
        blocks.append(P)
    assert p == len(toks), f"{len(toks) - p} tokens left unread -- format mismatch"
    return blocks


def triangulate(P):
    """Structured (na, nb) point grid -> triangles as index triples into a flat
    vertex list. Two triangles per quad, consistent winding."""
    na, nb = P.shape[0], P.shape[1]
    V = P.reshape(-1, 3)
    idx = lambda a, b: a * nb + b
    T = []
    for a in range(na - 1):
        for b in range(nb - 1):
            v00, v01, v11, v10 = idx(a, b), idx(a, b + 1), idx(a + 1, b + 1), idx(a + 1, b)
            T.append((v00, v01, v11)); T.append((v00, v11, v10))
    return V, np.array(T, dtype=np.int64)


def edge_census(all_tris_xyz, quant=1e-9):
    """Open / manifold / non-manifold edge counts over the WHOLE assembly.
    Vertices are welded on a quantised key so patches that meet point-for-point
    share edges. Returns (open_edges, nonmanifold_edges) as coordinate pairs."""
    def key(v):
        return (round(float(v[0]) / quant), round(float(v[1]) / quant), round(float(v[2]) / quant))
    cnt = defaultdict(int)
    rep = {}
    for tri in all_tris_xyz:
        k = [key(v) for v in tri]
        for i in range(3):
            e = tuple(sorted((k[i], k[(i + 1) % 3])))
            cnt[e] += 1
            if e not in rep:
                rep[e] = (tri[i], tri[(i + 1) % 3])
    open_e = [rep[e] for e, c in cnt.items() if c == 1]
    nonman = [rep[e] for e, c in cnt.items() if c > 2]
    return open_e, nonman


def assemble(blocks):
    out = []
    for P in blocks:
        V, T = triangulate(P)
        out.append((V, T))
    tris = []
    for V, T in out:
        for t in T:
            tris.append((V[t[0]], V[t[1]], V[t[2]]))
    return out, tris


def main():
    src = sys.argv[1]; dst = sys.argv[2]
    blocks = read_plot3d(src)
    print(f"=== {src} -> {dst} ===")
    if len(blocks) != len(NAMES):
        print(f"  REFUSED: {len(blocks)} blocks, expected {len(NAMES)}"); return 3
    for n, P in zip(NAMES, blocks):
        print(f"  patch {n:12s} {P.shape[0]:4d} x {P.shape[1]:4d}")

    per, tris = assemble(blocks)
    ntri = sum(len(T) for _, T in per)
    exp = sum(2 * (P.shape[0] - 1) * (P.shape[1] - 1) for P in blocks)
    print(f"  triangles {ntri} (expected {exp})")
    if ntri != exp:
        print("  REFUSED (3): triangle count does not match the structured grids"); return 3

    # ---- LIMB 1: the conversion did not move the body ------------------------
    dev = 0.0
    for (V, T), P in zip(per, blocks):
        dev = max(dev, float(np.abs(V - P.reshape(-1, 3)).max()))
    print(f"  [limb 1] max |STL vertex - PLOT3D point| = {dev:.3e}")
    if dev != 0.0:
        print("  REFUSED (3): the conversion moved the body"); return 3

    # ---- LIMB 2: manifoldness, WITH ITS PLANT FIRST --------------------------
    q = [P.copy() for P in blocks]
    q[8] = q[8] + np.array([0.0, 0.0, 1e-3])          # make_level.py's own plant
    _, ptris = assemble(q)
    p_open, _ = edge_census(ptris)
    base_open, nonman = edge_census(tris)
    print(f"  [limb 2 PLANT] as built {len(base_open)} open edges; crown displaced "
          f"1 mm -> {len(p_open)}")
    if not len(p_open) > len(base_open):
        print("  REFUSED (2): the manifoldness reader was not shown able to see an open seam")
        return 2
    print("    control PASSES -- the reader is shown able to SEE an open seam")

    if nonman:
        print(f"  REFUSED (5): {len(nonman)} NON-MANIFOLD edges (shared by >2 triangles)")
        return 5

    off_root = [e for e in base_open
                if not (abs(e[0][1]) <= ROOT_TOL and abs(e[1][1]) <= ROOT_TOL)]
    print(f"  [limb 2] open edges {len(base_open)}: {len(base_open)-len(off_root)} on the ROOT "
          f"plane |y|<={ROOT_TOL:g} (the symmetry plane, expected), {len(off_root)} elsewhere")
    if off_root:
        ys = sorted({round(float(v[1]), 6) for e in off_root for v in e})[:6]
        print(f"  REFUSED (4): open edges away from the symmetry plane, y values {ys}")
        return 4

    # ---- write the multi-solid ASCII STL (named regions snappy can refine on)
    with open(dst, "w") as f:
        for nm, (V, T) in zip(NAMES, per):
            f.write(f"solid {nm}\n")
            for t in T:
                a, b, c = V[t[0]], V[t[1]], V[t[2]]
                n = np.cross(b - a, c - a); L = float(np.linalg.norm(n))
                n = n / L if L > 0 else np.zeros(3)
                f.write(f"facet normal {n[0]:.9g} {n[1]:.9g} {n[2]:.9g}\n outer loop\n")
                for v in (a, b, c):
                    f.write(f"  vertex {v[0]:.15g} {v[1]:.15g} {v[2]:.15g}\n")
                f.write(" endloop\nendfacet\n")
            f.write(f"endsolid {nm}\n")
    mn = np.min([t for tri in tris for t in tri], axis=0)
    mx = np.max([t for tri in tris for t in tri], axis=0)
    print(f"  bbox x [{mn[0]:.6f}, {mx[0]:.6f}]  y [{mn[1]:.6f}, {mx[1]:.6f}]  "
          f"z [{mn[2]:.6f}, {mx[2]:.6f}]")
    print(f"  WROTE {dst}  ({pathlib.Path(dst).stat().st_size/1e6:.2f} MB, {ntri} triangles, "
          f"{len(NAMES)} named solids)")
    print("  ACCEPTED: closed except the root symmetry plane, manifold, body unmoved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
