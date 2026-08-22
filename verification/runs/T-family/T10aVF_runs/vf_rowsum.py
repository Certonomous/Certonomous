#!/usr/bin/env python3
"""
T10a-VF: read-only row-sum analysis of an OpenFOAM view-factor matrix.

Streams constant/F (scalarListList, compact/visibility-indexed) together with
constant/globalFaceFaces (labelListList, the column indices) and reports, per
boundary patch, the distribution of the row sums  S_i = sum_j F_ij, which for a
CLOSED enclosure must equal 1 exactly for every row, independently of how
coarsely the surfaces are faceted.

Also splits each row sum by the patch of the receiving face, so that a
self-view (concave) contribution can be separated from cross-patch
contributions.

Read-only: opens nothing for writing, touches no case file.
"""
import sys, os, argparse
from collections import OrderedDict


def read_boundary(case):
    """Return OrderedDict name -> (nFaces, startFace) for boundary patches."""
    path = os.path.join(case, "constant", "polyMesh", "boundary")
    toks = []
    with open(path) as fh:
        for line in fh:
            s = line.strip()
            if s.startswith("//") or s.startswith("/*") or s.startswith("|") or s.startswith("\\"):
                continue
            toks.append(s)
    # crude but sufficient parse of the patch list
    patches = OrderedDict()
    name = None
    cur = {}
    depth = 0
    for s in toks:
        if s == "{":
            depth += 1
            continue
        if s == "}":
            depth -= 1
            if name is not None:
                patches[name] = (int(cur.get("nFaces", 0)), int(cur.get("startFace", 0)))
            name, cur = None, {}
            continue
        if depth == 1:
            k = s.rstrip(";").split()
            if len(k) >= 2 and k[0] in ("nFaces", "startFace"):
                cur[k[0]] = k[1]
        elif depth == 0 and s and not s[0].isdigit() and s not in ("(", ")") \
                and "FoamFile" not in s and "version" not in s and "format" not in s \
                and "arch" not in s and "class" not in s and "location" not in s \
                and "object" not in s and "{" not in s and "}" not in s:
            name = s
    return patches


def stream_list_list(path, cast):
    """Yield lists from an OpenFOAM ascii <T>ListList file, one row at a time."""
    with open(path) as fh:
        # advance to the outer size line
        n = None
        for line in fh:
            s = line.strip()
            if not s or s.startswith("//") or s.startswith("|") or s.startswith("\\") \
                    or s.startswith("/*") or s.startswith("*"):
                continue
            if s.isdigit():
                n = int(s)
                break
            # header block: skip through the closing brace of FoamFile
        if n is None:
            raise RuntimeError("no outer size found in %s" % path)
        # next non-empty must be "("
        for line in fh:
            if line.strip() == "(":
                break
        for _ in range(n):
            # row size
            m = None
            for line in fh:
                s = line.strip()
                if not s:
                    continue
                if s == "(":
                    continue
                m = int(s)
                break
            for line in fh:
                if line.strip() == "(":
                    break
            row = [None] * m
            k = 0
            while k < m:
                s = fh.readline().strip()
                if not s:
                    continue
                row[k] = cast(s)
                k += 1
            # closing ")"
            for line in fh:
                if line.strip() == ")":
                    break
            yield row


def patch_of(idx, bounds):
    """bounds: list of (name, lo, hi) over the *boundary-face* numbering."""
    for name, lo, hi in bounds:
        if lo <= idx < hi:
            return name
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("case")
    ap.add_argument("--label", default=None)
    a = ap.parse_args()
    case = a.case
    label = a.label or os.path.basename(os.path.abspath(case))

    patches = read_boundary(case)
    # view-factor faces are the wall patches carrying the F matrix, in patch
    # order, numbered 0..N-1 across the *radiative* patches only.
    off = 0
    bounds = []
    for nm, (nf, sf) in patches.items():
        bounds.append((nm, off, off + nf))
        off += nf
    ntot = off

    fpath = os.path.join(case, "constant", "F")
    gpath = os.path.join(case, "constant", "globalFaceFaces")

    names = [b[0] for b in bounds]
    # accumulators
    stats = {nm: {"n": 0, "sum": 0.0, "min": 1e30, "max": -1e30,
                  "cross": {n2: 0.0 for n2 in names}, "rows": []} for nm in names}
    nvis = {nm: 0 for nm in names}

    fgen = stream_list_list(fpath, float)
    ggen = stream_list_list(gpath, int)

    i = 0
    for frow, grow in zip(fgen, ggen):
        if len(frow) != len(grow):
            raise RuntimeError("row %d: F has %d entries, globalFaceFaces %d"
                               % (i, len(frow), len(grow)))
        src = patch_of(i, bounds)
        st = stats[src]
        tot = 0.0
        cross = st["cross"]
        for v, j in zip(frow, grow):
            tot += v
            cross[patch_of(j, bounds)] += v
        st["n"] += 1
        st["sum"] += tot
        st["min"] = min(st["min"], tot)
        st["max"] = max(st["max"], tot)
        st["rows"].append(tot)
        nvis[src] += len(frow)
        i += 1
    if i != ntot:
        print("WARNING: %d rows in F, %d boundary faces" % (i, ntot))

    print("=" * 78)
    print("case: %s   (%s)" % (os.path.abspath(case), label))
    print("radiative faces: %d   patches: %s" % (ntot, ", ".join(names)))
    print("=" * 78)
    hdr = ("patch", "nRows", "meanSum", "minSum", "maxSum",
           "meanDefect%", "maxDefect%", "meanVis")
    print("%-12s %7s %12s %12s %12s %12s %12s %9s" % hdr)
    for nm in names:
        st = stats[nm]
        if st["n"] == 0:
            continue
        mean = st["sum"] / st["n"]
        rows = st["rows"]
        defs = [abs(1.0 - r) * 100.0 for r in rows]
        print("%-12s %7d %12.8f %12.8f %12.8f %12.5f %12.5f %9.1f"
              % (nm, st["n"], mean, st["min"], st["max"],
                 sum(defs) / len(defs), max(defs), nvis[nm] / st["n"]))
    print()
    print("row-sum split by RECEIVING patch (mean over rows of the emitting patch):")
    print("%-12s %s" % ("from \\ to", "  ".join("%14s" % n for n in names)))
    for nm in names:
        st = stats[nm]
        if st["n"] == 0:
            continue
        print("%-12s %s" % (nm, "  ".join("%14.8f" % (st["cross"][n2] / st["n"])
                                          for n2 in names)))
    print()
    # percentile spread of the defect, per patch
    print("row-sum percentiles per emitting patch:")
    print("%-12s %10s %10s %10s %10s %10s" % ("patch", "p0", "p5", "p50", "p95", "p100"))
    for nm in names:
        st = stats[nm]
        if st["n"] == 0:
            continue
        r = sorted(st["rows"])
        q = lambda p: r[min(len(r) - 1, int(p * (len(r) - 1)))]
        print("%-12s %10.6f %10.6f %10.6f %10.6f %10.6f"
              % (nm, r[0], q(0.05), q(0.50), q(0.95), r[-1]))


if __name__ == "__main__":
    main()
