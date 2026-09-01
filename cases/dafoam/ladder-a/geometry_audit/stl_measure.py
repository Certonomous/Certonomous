#!/usr/bin/env python3
"""Measure an STL: bbox on all three axes, facet count, and per-axis slice structure.
No third-party deps. Handles binary and ASCII STL."""
import struct
import sys


def read_stl(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    # Binary detection: header 80 bytes + uint32 count, then 50 bytes/facet
    if len(raw) >= 84:
        n = struct.unpack_from("<I", raw, 80)[0]
        if 84 + 50 * n == len(raw):
            tris = []
            off = 84
            for _ in range(n):
                vals = struct.unpack_from("<12f", raw, off)
                tris.append((vals[0:3], vals[3:6], vals[6:9], vals[9:12]))
                off += 50
            return raw[:80].decode("ascii", "replace").rstrip("\x00 "), tris, "binary"
    # ASCII fallback
    txt = raw.decode("ascii", "replace")
    tris = []
    nrm = (0.0, 0.0, 0.0)
    verts = []
    name = ""
    for line in txt.splitlines():
        s = line.strip().split()
        if not s:
            continue
        if s[0] == "solid" and not name:
            name = " ".join(s[1:])
        elif s[0] == "facet" and len(s) >= 5:
            nrm = tuple(float(x) for x in s[2:5])
            verts = []
        elif s[0] == "vertex":
            verts.append(tuple(float(x) for x in s[1:4]))
        elif s[0] == "endfacet":
            if len(verts) == 3:
                tris.append((nrm, verts[0], verts[1], verts[2]))
    return name, tris, "ascii"


def bbox(tris):
    lo = [float("inf")] * 3
    hi = [float("-inf")] * 3
    for t in tris:
        for v in t[1:]:
            for i in range(3):
                if v[i] < lo[i]:
                    lo[i] = v[i]
                if v[i] > hi[i]:
                    hi[i] = v[i]
    return lo, hi


def unique_coords(tris, axis, tol=1e-7):
    vals = sorted({round(v[axis] / tol) * tol for t in tris for v in t[1:]})
    # cluster
    out = []
    for v in vals:
        if not out or abs(v - out[-1]) > 1e-6:
            out.append(v)
    return out


def report(path):
    name, tris, fmt = read_stl(path)
    lo, hi = bbox(tris)
    ext = [hi[i] - lo[i] for i in range(3)]
    print(f"file      : {path}")
    print(f"format    : {fmt}")
    print(f"solid name: {name!r}")
    print(f"facets    : {len(tris)}")
    for i, ax in enumerate("XYZ"):
        print(f"  {ax}: min {lo[i]: .6f}  max {hi[i]: .6f}  extent {ext[i]: .6f}")
    order = sorted(range(3), key=lambda i: ext[i])
    print(f"  extents sorted (small->large): "
          + ", ".join(f"{'XYZ'[i]}={ext[i]:.6f}" for i in order))
    if ext[order[1]] > 0:
        print(f"  ratio smallest/middle = {ext[order[0]] / ext[order[1]]:.4f}")
    if ext[order[2]] > 0:
        print(f"  ratio middle/largest  = {ext[order[1]] / ext[order[2]]:.4f}")
    for i, ax in enumerate("XYZ"):
        u = unique_coords(tris, i)
        print(f"  distinct {ax} planes: {len(u)}"
              + (f"  -> {['%.5f' % x for x in u]}" if len(u) <= 24 else ""))
    return name, tris, lo, hi, ext


if __name__ == "__main__":
    for p in sys.argv[1:]:
        report(p)
        print("-" * 70)
