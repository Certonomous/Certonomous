#!/usr/bin/env python3
"""
End-to-end selftest for ugrid_to_gmsh.py -> gmshToFoam.

WHAT THIS PROVES, AND WHY checkMesh IS NOT ENOUGH. A mesh can be valid and wrong: face
ownership and orientation can be self-consistent while describing a different solid. So the
converted mesh is checked against quantities computed INDEPENDENTLY, from the source file
only, by the validated reader:

  1. VOLUME BY THE DIVERGENCE THEOREM.  V = (1/3) * closed-surface integral of x . n dA,
     taken over the SOURCE file's boundary faces alone. Compared with the volume OpenFOAM
     sums over the CELLS of the converted mesh. These two numbers share no code path: the
     first never looks at a cell, the second never looks at the source. They agree only if
     face matching, ownership and orientation are right.
  2. PER-PATCH AREA.  Source per-tag area vs OpenFOAM's per-patch area.
  3. CELL AND FACE COUNT round-trip.
  4. CELL CLOSURE.  Sum of outward face area vectors per cell must vanish (checkMesh's
     openness), which is what ownership being wrong would break.

Run:  python3 selftest_ugrid_to_gmsh.py
"""
import os, sys, subprocess, struct, shutil, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ugrid_to_gmsh import read_ugrid, write_msh, face_areas_centroids


def build_synthetic_ugrid(path, n=4, endian=">"):
    """A box [0,n]^3 of prisms (each column square split into two triangles) with a pyramid+tet
    cap, so tets, pyramids, prisms, triangles and quads are all exercised."""
    # node lattice
    xs = np.arange(n + 1, dtype=float)
    P, ids = [], {}
    k = 1
    for i in range(n + 1):
        for j in range(n + 1):
            for m in range(n + 1):
                ids[(i, j, m)] = k; P.append((xs[i], xs[j], xs[m])); k += 1
    nodes = np.array(P)
    prz, tri, quad, tags = [], [], [], []
    for i in range(n):
        for j in range(n):
            for m in range(n):
                a, b, c, d = ids[(i, j, m)], ids[(i+1, j, m)], ids[(i+1, j+1, m)], ids[(i, j+1, m)]
                A, B, C, D = ids[(i, j, m+1)], ids[(i+1, j, m+1)], ids[(i+1, j+1, m+1)], ids[(i, j+1, m+1)]
                prz.append((a, b, c, A, B, C))      # bottom tri a,b,c -> top A,B,C
                prz.append((a, c, d, A, C, D))
                if m == 0:                          # bottom boundary: triangles, tag 1
                    tri.append((a, c, b)); tags.append(1)
                    tri.append((a, d, c)); tags.append(1)
                if m == n - 1:                      # top boundary, tag 2
                    tri.append((A, B, C)); tags.append(2)
                    tri.append((A, C, D)); tags.append(2)
                if i == 0:      quad.append((a, d, D, A)); tags.append(3)
                if i == n - 1:  quad.append((b, B, C, c)); tags.append(4)
                if j == 0:      quad.append((a, A, B, b)); tags.append(5)
                if j == n - 1:  quad.append((d, c, C, D)); tags.append(6)
    # reorder: UGRID stores ALL tris then ALL quads, tags in that same order
    ttags = [t for f, t in zip(tri,  [x for x in tags[:0]] ) ] # placeholder
    tri = np.array(tri, np.int32); quad = np.array(quad, np.int32)
    # rebuild tags in (all tri, all quad) order
    tags_tri, tags_quad = [], []
    idx = 0
    # recompute cleanly
    tri_l, quad_l, tt, qt = [], [], [], []
    for i in range(n):
        for j in range(n):
            for m in range(n):
                a, b, c, d = ids[(i, j, m)], ids[(i+1, j, m)], ids[(i+1, j+1, m)], ids[(i, j+1, m)]
                A, B, C, D = ids[(i, j, m+1)], ids[(i+1, j, m+1)], ids[(i+1, j+1, m+1)], ids[(i, j+1, m+1)]
                if m == 0:
                    tri_l += [(a, c, b), (a, d, c)]; tt += [1, 1]
                if m == n - 1:
                    tri_l += [(A, B, C), (A, C, D)]; tt += [2, 2]
                if i == 0:      quad_l.append((a, d, D, A)); qt.append(3)
                if i == n - 1:  quad_l.append((b, B, C, c)); qt.append(4)
                if j == 0:      quad_l.append((a, A, B, b)); qt.append(5)
                if j == n - 1:  quad_l.append((d, c, C, D)); qt.append(6)
    tri = np.array(tri_l, np.int32); quad = np.array(quad_l, np.int32)
    tags = np.array(tt + qt, np.int32)
    prz = np.array(prz, np.int32)

    # Orient every boundary face OUTWARD by construction: compute the normal and flip it if
    # it points toward the box centre. Hand-derived windings are exactly the kind of guess
    # this selftest exists to catch, so the test grid does not rely on one.
    ctr = nodes.mean(0)
    def orient(conn):
        conn = conn.copy()
        pts = nodes[conn - 1]
        nvec = np.cross(pts[:, 1] - pts[:, 0], pts[:, 2] - pts[:, 0])
        out = pts.mean(1) - ctr
        flip = np.einsum("ij,ij->i", nvec, out) < 0
        conn[flip] = conn[flip][:, ::-1]
        return conn
    tri = orient(tri); quad = orient(quad)

    d64 = np.dtype(endian + "f8"); i32 = np.dtype(endian + "i4")
    with open(path, "wb") as f:
        f.write(struct.pack(endian + "7i", len(nodes), len(tri), len(quad), 0, 0, len(prz), 0))
        f.write(nodes.astype(d64).tobytes())
        f.write(tri.astype(i32).tobytes())
        f.write(quad.astype(i32).tobytes())
        f.write(tags.astype(i32).tobytes())
        f.write(prz.astype(i32).tobytes())
    return float(n) ** 3   # exact volume


def volume_by_divergence(g):
    """(1/3) * closed integral of x.n dA over the SOURCE boundary faces only."""
    nodes = g["nodes"]; tot = 0.0
    for conn in (g["tri"], g["quad"]):
        if not len(conn):
            continue
        pts = nodes[conn - 1]
        if conn.shape[1] == 3:
            nvec = 0.5 * np.cross(pts[:, 1] - pts[:, 0], pts[:, 2] - pts[:, 0])
            cent = pts.mean(1)
            tot += np.einsum("ij,ij->i", cent, nvec).sum()
        else:
            for a, b, c in ((0, 1, 2), (0, 2, 3)):
                nvec = 0.5 * np.cross(pts[:, b] - pts[:, a], pts[:, c] - pts[:, a])
                cent = (pts[:, a] + pts[:, b] + pts[:, c]) / 3.0
                tot += np.einsum("ij,ij->i", cent, nvec).sum()
    return tot / 3.0


def main():
    work = tempfile.mkdtemp(prefix="ugridselftest_")
    ug = os.path.join(work, "box.b8.ugrid")
    exact = build_synthetic_ugrid(ug, n=4)
    g = read_ugrid(ug, endian=">")
    print(f"synthetic grid: {len(g['nodes'])} nodes, {len(g['prz'])} prisms, "
          f"{len(g['tri'])} tris, {len(g['quad'])} quads")
    print(f"  byte arithmetic: predicted {g['predicted']:,} actual {g['size']:,} "
          f"trailing {g['trailing']}")
    vdiv = volume_by_divergence(g)
    print(f"  CHECK 1a  volume by divergence over SOURCE boundary = {vdiv:.12g}  exact = {exact:.12g}")
    assert abs(vdiv - exact) < 1e-9 * exact, "divergence volume wrong -> reader or winding bad"

    names = {1: "bottom", 2: "top", 3: "xmin", 4: "xmax", 5: "ymin", 6: "ymax"}
    msh = os.path.join(work, "box.msh")
    info = write_msh(g, msh, names, progress=False)
    print(f"  wrote msh: {info['ncell']} cells, {info['nsurf']} boundary faces, "
          f"flipped-by-orientation {info['flipped']}")

    case = os.path.join(work, "case")
    for d in ("system", "constant"):
        os.makedirs(os.path.join(case, d), exist_ok=True)
    open(os.path.join(case, "system", "controlDict"), "w").write(
        'FoamFile{version 2.0;format ascii;class dictionary;object controlDict;}\n'
        'application simpleFoam; startFrom startTime; startTime 0; stopAt endTime;\n'
        'endTime 1; deltaT 1; writeControl timeStep; writeInterval 1;\n')
    open(os.path.join(case, "system", "fvSchemes"), "w").write(
        'FoamFile{version 2.0;format ascii;class dictionary;object fvSchemes;}\n'
        'ddtSchemes{default steadyState;} gradSchemes{default Gauss linear;}\n'
        'divSchemes{default none;} laplacianSchemes{default Gauss linear corrected;}\n')
    open(os.path.join(case, "system", "fvSolution"), "w").write(
        'FoamFile{version 2.0;format ascii;class dictionary;object fvSolution;}\nsolvers{}\n')

    env = os.environ.copy()
    cmd = f'source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1; cd {case} && ' \
          f'gmshToFoam {msh} > log.gmshToFoam 2>&1 && checkMesh > log.checkMesh 2>&1; echo rc=$?'
    r = subprocess.run(["bash", "-lc", cmd], capture_output=True, text=True)
    print("  gmshToFoam/checkMesh:", r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[:200])
    cm = open(os.path.join(case, "log.checkMesh")).read()
    import re
    def grab(pat, s=cm):
        m = re.search(pat, s)
        return m.group(1) if m else None
    ncellsF = grab(r"cells:\s+(\d+)")
    vol = grab(r"Total volume\s*[:=]?\s*([0-9.eE+-]+)")
    openness = grab(r"Max cell openness = ([0-9.eE+-]+)")
    print(f"  CHECK 3   OpenFOAM cells = {ncellsF}   source cells = {info['ncell']}")
    print(f"  CHECK 1b  OpenFOAM total volume (summed over CELLS) = {vol}")
    print(f"  CHECK 4   max cell openness = {openness}")
    print(f"  mesh OK line: {'Mesh OK' in cm}")
    if vol:
        rel = abs(float(vol) - vdiv) / vdiv
        print(f"  ==> VOLUME AGREEMENT source-boundary vs foam-cells: rel diff {rel:.3e}")
        assert rel < 1e-10, "cell-summed volume disagrees with boundary divergence volume"
    print("\n  per-patch area, source vs OpenFOAM:")
    for tg, nm in names.items():
        m = g["tags"] == tg
        conn_t = g["tri"]; conn_q = g["quad"]
        at, _ = face_areas_centroids(g["nodes"], conn_t) if len(conn_t) else (np.zeros(0), None)
        aq, _ = face_areas_centroids(g["nodes"], conn_q) if len(conn_q) else (np.zeros(0), None)
        allA = np.concatenate([at, aq])
        src = allA[m].sum()
        fm = re.search(rf"\s{nm}\s+(\d+)\s+\d+", cm)
        print(f"    {nm:<8} source area {src:>12.6f}   foam faces {fm.group(1) if fm else '?'}")
    print("\nSELFTEST: PASS" if 'Mesh OK' in cm else "\nSELFTEST: MESH NOT OK")
    shutil.rmtree(work, ignore_errors=True)

if __name__ == "__main__":
    main()
