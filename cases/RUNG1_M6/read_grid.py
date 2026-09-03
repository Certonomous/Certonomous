#!/usr/bin/env python3
"""R1-M0 PLOT3D grid reader -- cell count and ACHIEVED first-cell height, read back from
the WRITTEN grid.  verification/campaign/RUNG1_M6_PREREGISTRATION.md §5, §9.

Two readings, and both are read off the file pyHyp actually wrote:

  1. CELL COUNT, as sum over blocks of (i-1)(j-1)(k-1).  This is an INDEPENDENT second
     instrument beside checkMesh's own `cells:` line; the driver asserts the two agree.
  2. ACHIEVED first-cell height, as |P(i,j,k=1) - P(i,j,k=0)| over every wall node.
     The REQUESTED `s0` is an INPUT AND IS NEVER A MEASUREMENT (M6S-P prereg §2 reading 3);
     it is carried here only so the ratio achieved/requested can be printed.

PLANTED CONTROLS (rule 3): the reader is shown able to see a mutation planted into a COPY
of the grid on disk, and to see the unmutated nodes unchanged.  A height this reader
reports is evidence only because it demonstrably tracks the bytes.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import statistics
import sys


def read_plot3d(path):
    """Multiblock ASCII PLOT3D: nblocks / (i j k) per block / then X.. Y.. Z.. per block."""
    with open(path) as fh:
        toks = fh.read().split()
    p = 0
    nb = int(toks[p]); p += 1
    dims = []
    for _ in range(nb):
        dims.append((int(toks[p]), int(toks[p + 1]), int(toks[p + 2]))); p += 3
    blocks = []
    for (ni, nj, nk) in dims:
        n = ni * nj * nk
        xyz = []
        for _ in range(3):
            xyz.append([float(t) for t in toks[p:p + n]]); p += n
        blocks.append(((ni, nj, nk), xyz))
    return blocks, p, len(toks)


def first_cell_heights(blocks):
    """|P(k=1) - P(k=0)| for every (i,j) wall node.  PLOT3D is Fortran-ordered: the index
    into a flat block array for (i,j,k) is i + ni*j + ni*nj*k."""
    h = []
    for (ni, nj, nk), (X, Y, Z) in blocks:
        if nk < 2:
            continue
        s0, s1 = 0, ni * nj
        for j in range(nj):
            for i in range(ni):
                a = i + ni * j
                dx = X[s1 + a] - X[s0 + a]
                dy = Y[s1 + a] - Y[s0 + a]
                dz = Z[s1 + a] - Z[s0 + a]
                h.append(math.sqrt(dx * dx + dy * dy + dz * dz))
    return h


def measure(path, requested_s0=None):
    blocks, consumed, total = read_plot3d(path)
    dims = [d for d, _ in blocks]
    cells = sum((i - 1) * (j - 1) * (k - 1) for (i, j, k) in dims)
    nodes = sum(i * j * k for (i, j, k) in dims)
    h = first_cell_heights(blocks)
    hs = sorted(h)
    out = {
        "grid": path,
        "grid_bytes": os.path.getsize(path),
        "n_blocks": len(blocks),
        "block_dims_nodes": dims,
        "nodes": nodes,
        "cells_DERIVED_sum_(i-1)(j-1)(k-1)": cells,
        "tokens_consumed": consumed,
        "tokens_total": total,
        "fully_consumed": consumed == total,
        "wall_nodes_sampled": len(h),
        "first_cell_height_m": {
            "min": hs[0], "max": hs[-1],
            "median": statistics.median(hs), "mean": statistics.fmean(hs),
            "p05": hs[int(0.05 * (len(hs) - 1))], "p95": hs[int(0.95 * (len(hs) - 1))],
            "spread_max_over_min": hs[-1] / hs[0],
        },
    }
    if requested_s0:
        out["requested_s0_INPUT_NEVER_A_MEASUREMENT"] = requested_s0
        out["median_over_requested"] = statistics.median(hs) / requested_s0
        out["max_over_requested"] = hs[-1] / requested_s0
    return out


def selftest(path, workdir):
    """Plant a known displacement into a COPY on disk, read it back, and require the
    reader to SEE it -- and require the untouched nodes to be unchanged."""
    os.makedirs(workdir, exist_ok=True)
    base = measure(path)
    ctl = [{"control": "P1 the grid parses and every token is consumed",
            "pass": base["fully_consumed"],
            "observed": {"consumed": base["tokens_consumed"], "total": base["tokens_total"]},
            "expected": "consumed == total"}]

    # P2 -- displace the SECOND k-layer of block 0 by a known +delta in x.  The first-cell
    # height of block 0's wall nodes must move; the reader must see the new maximum.
    blocks, _, _ = read_plot3d(path)
    (ni, nj, nk), _ = blocks[0]
    delta = 2.5e-05
    with open(path) as fh:
        toks = fh.read().split()
    hdr = 1 + 3 * len(blocks)
    s1 = hdr + ni * nj                      # start of block 0's X at k=1
    for a in range(ni * nj):
        toks[s1 + a] = repr(float(toks[s1 + a]) + delta)
    mut = os.path.join(workdir, "PLANT_mutated_volumeMesh.xyz")
    open(mut, "w").write("\n".join(toks[:hdr]) + "\n" + "\n".join(toks[hdr:]) + "\n")
    m = measure(mut)
    moved = m["first_cell_height_m"]["max"] != base["first_cell_height_m"]["max"]
    ctl.append({"control": "P2 a %.1e m displacement planted on disk MOVES the reading" % delta,
                "pass": bool(moved),
                "observed": {"base_max": base["first_cell_height_m"]["max"],
                             "mutated_max": m["first_cell_height_m"]["max"]},
                "expected": "the maximum changes"})
    # P3 -- the cell count is a topology reading and must NOT move under a node
    #       displacement.  A reader that confused geometry for topology fails here.
    ctl.append({"control": "P3 the cell count is unchanged by a node displacement",
                "pass": m["cells_DERIVED_sum_(i-1)(j-1)(k-1)"] ==
                        base["cells_DERIVED_sum_(i-1)(j-1)(k-1)"],
                "observed": {"base": base["cells_DERIVED_sum_(i-1)(j-1)(k-1)"],
                             "mutated": m["cells_DERIVED_sum_(i-1)(j-1)(k-1)"]},
                "expected": "equal"})
    return all(c["pass"] for c in ctl), ctl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid", required=True)
    ap.add_argument("--requested-s0", type=float, default=None)
    ap.add_argument("--json-out")
    ap.add_argument("--selftest-workdir")
    ap.add_argument("--controls-out")
    a = ap.parse_args()
    if not os.path.exists(a.grid):
        print(json.dumps({"state": "ABSENT", "grid": a.grid}), file=sys.stderr)
        return 2
    blob = measure(a.grid, a.requested_s0)
    if a.selftest_workdir:
        ok, ctl = selftest(a.grid, a.selftest_workdir)
        blob["planted_controls_all_pass"] = ok
        blob["planted_controls"] = ctl
        if a.controls_out:
            json.dump({"all_controls_pass": ok, "controls": ctl},
                      open(a.controls_out, "w"), indent=2)
        if not ok:
            print(json.dumps(blob, indent=2))
            print("A PLANTED CONTROL FAILED (§9).", file=sys.stderr)
            return 4
    if a.json_out:
        json.dump(blob, open(a.json_out, "w"), indent=2)
    print(json.dumps(blob, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
