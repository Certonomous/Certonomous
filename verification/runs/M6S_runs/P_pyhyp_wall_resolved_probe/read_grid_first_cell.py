#!/usr/bin/env python3
"""M6S-P registered READING 3(b) -- the read-back of the achieved first-cell height from
the WRITTEN GRID, as distinct from reading 3(a), the level-2 March Distance in the log.

Prereg §2 reading 3: "Read (a) the level-2 March Distance -- the cumulative distance after
the first step, which is the first cell height -- and (b), if a grid is written, the
read-back from the written grid."  A grid was written, so (b) is due.

MESH_STANDARD.md §9.2:528-538 is why this reader exists at all: "The requested value is the
thing that lied. Only the returned value tells the truth."  The requested s0 = 1.319e-06 is
an INPUT and is never reported here as a measurement.

NO GATE.  Prereg §2 reading 3: "No target, band or tolerance is registered for this reading
-- it has no gate."  And §1.1 governs everything here: this says NOTHING about whether max
non-orthogonality clears 70 degrees, because pyHyp's grid and OpenFOAM's checkMesh are
different instruments and no checkMesh was run.

RULE 3 -- the reader carries a LIVE PLANTED CONTROL and REFUSES (exit 2) if it cannot see
it.  A number from a reader not shown able to see a known non-zero is not evidence.  The
control writes a synthetic plot3d grid with a KNOWN first-cell height to disk, reads it
back through the SAME production path, then MUTATES one wall node on disk and requires the
reader to see the mutation move the maximum.

Plot3D, ASCII, multiblock, as pyHyp's writePlot3D emits it:
    nblocks / (ni nj nk) per block / then per block all X, then all Y, then all Z,
    with i fastest and k -- the MARCHING direction -- slowest.  The wall is k = 1 and the
    first marched node is k = 2, so the first-cell height at wall node (i,j) is
    |P(i,j,2) - P(i,j,1)|.
"""
import json
import math
import sys

PLANT_H = 7.5e-06         # known first-cell height planted into the control grid
PLANT_MUT = 2.5e-05       # the mutation the reader must see move the maximum


def parse(path):
    toks = open(path).read().split()
    nb = int(toks[0])
    p = 1
    dims = []
    for _ in range(nb):
        dims.append(tuple(int(toks[p + i]) for i in range(3)))
        p += 3
    return dims, toks[p:]


def first_cell_heights(path):
    """The production path.  Returns one height per WALL node, over every block."""
    dims, vals = parse(path)
    tot = sum(ni * nj * nk for ni, nj, nk in dims)
    if len(vals) != 3 * tot:
        raise ValueError("REFUSE: %s carries %d coordinate values, expected %d for %s"
                         % (path, len(vals), 3 * tot, dims))
    out, q = [], 0
    for (ni, nj, nk) in dims:
        if nk < 2:
            raise ValueError("REFUSE: block with nk=%d has no first cell" % nk)
        n = ni * nj * nk
        X, Y, Z = vals[q:q + n], vals[q + n:q + 2 * n], vals[q + 2 * n:q + 3 * n]
        q += 3 * n
        plane = ni * nj
        for idx in range(plane):
            dx = float(X[idx + plane]) - float(X[idx])
            dy = float(Y[idx + plane]) - float(Y[idx])
            dz = float(Z[idx + plane]) - float(Z[idx])
            out.append(math.sqrt(dx * dx + dy * dy + dz * dz))
    return out, dims


def write_control(path, h):
    """One block, 3x3x4, wall plane at z=0 and the first marched plane at z=h."""
    ni = nj = 3
    nk = 4
    X, Y, Z = [], [], []
    for k in range(nk):
        for j in range(nj):
            for i in range(ni):
                X.append(float(i))
                Y.append(float(j))
                Z.append(0.0 if k == 0 else h * (2.0 ** (k - 1)))
    with open(path, "w") as f:
        f.write("   1\n%5d%5d%5d\n" % (ni, nj, nk))
        for arr in (X, Y, Z):
            for v in arr:
                f.write(" %.14E\n" % v)


def mutate_control(path, ni=3, nj=3, nk=4, node=0, newz=PLANT_MUT):
    """Move ONE first-marched-plane node on disk, through the file, not in memory."""
    toks = open(path).read().split()
    n = ni * nj * nk
    head = 1 + 3
    zbase = head + 2 * n
    toks[zbase + ni * nj + node] = "%.14E" % newz
    with open(path, "w") as f:
        f.write("   1\n%5d%5d%5d\n" % (ni, nj, nk))
        for v in toks[head:]:
            f.write(" %s\n" % v)


def controls(tmpdir):
    ok, checks = True, []
    cpath = "%s/PLANT_control_grid.xyz" % tmpdir
    write_control(cpath, PLANT_H)
    h, dims = first_cell_heights(cpath)
    c1 = len(h) == 9
    c2 = abs(max(h) - PLANT_H) < 1e-16 and abs(min(h) - PLANT_H) < 1e-16
    mutate_control(cpath)
    h2, _ = first_cell_heights(cpath)
    c3 = abs(max(h2) - PLANT_MUT) < 1e-16
    c4 = abs(min(h2) - PLANT_H) < 1e-16
    for name, passed, got in (
            ("PLANT: reader returns one height per wall node (9)", c1, len(h)),
            ("PLANT: reader reads the planted height %.3e exactly" % PLANT_H, c2, max(h)),
            ("PLANT: reader SEES a %.3e mutation planted on disk" % PLANT_MUT, c3, max(h2)),
            ("PLANT: the unmutated nodes are unchanged", c4, min(h2))):
        checks.append({"check": name, "pass": bool(passed), "observed": got})
        print("%-4s %-58s observed=%s" % ("PASS" if passed else "FAIL", name, got))
        ok = ok and passed
    return ok, checks


def main():
    grid, out_json, tmpdir = sys.argv[1], sys.argv[2], sys.argv[3]
    ok, checks = controls(tmpdir)
    if not ok:
        print("REFUSE: the planted control failed; this reader grades nothing (rule 3).")
        return 2
    h, dims = first_cell_heights(grid)
    h.sort()
    n = len(h)
    res = {
        "reading": "3(b) -- achieved first-cell height, READ BACK FROM THE WRITTEN GRID",
        "grid": grid,
        "blocks": [list(d) for d in dims],
        "wall_nodes_sampled": n,
        "first_cell_height_m": {
            "min": h[0], "median": h[n // 2], "mean": sum(h) / n, "max": h[-1],
            "p05": h[int(0.05 * n)], "p95": h[int(0.95 * n)],
            "spread_max_over_min": h[-1] / h[0],
        },
        "requested_s0_INPUT_NEVER_A_MEASUREMENT": 1.319e-06,
        "median_over_requested": h[n // 2] / 1.319e-06,
        "max_over_requested": h[-1] / 1.319e-06,
        "reading_3a_level2_march_distance_m": 1.43e-06,
        "NO_GATE": ("Prereg §2 reading 3 registers no target, band or tolerance for this "
                    "reading. §1.1 governs: nothing here bears on max non-orthogonality or "
                    "on whether option 3 clears MESH_STANDARD §3.1, and no checkMesh was run."),
        "planted_control": checks,
    }
    json.dump(res, open(out_json, "w"), indent=2)
    print(json.dumps({k: v for k, v in res.items() if k != "planted_control"}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
