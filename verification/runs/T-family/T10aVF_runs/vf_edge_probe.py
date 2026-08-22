#!/usr/bin/env python3
"""
T10a-VF: read-only per-pair probe.

For a chosen emitting face, classify every entry of its view-factor row by the
mesh relationship of the receiving face -- shares an edge / shares only a point
/ neither -- and compare the entries against the exact concentric-sphere kernel
F_ij = A_j / (4 pi R^2), which for two elements anywhere on the inside of a
sphere of radius R is independent of their separation.

The point of the probe is the SHARED-EDGE column: viewFactorsGen's 2LI branch
forces quadrature order 0 for a coincident edge pair and regularises the log
singularity as ln(r^2) -> 2 ln(alpha*|s_i|), whose exact value is 2 ln|s_i| - 3.
The resulting per-pair error is  -(2 ln alpha + 3)/(4 pi),  independent of h.

Read-only.
"""
import sys, os, math, argparse
from collections import defaultdict


def read_boundary(case):
    path = os.path.join(case, "constant", "polyMesh", "boundary")
    txt = open(path).read()
    body = txt[txt.index("// * * *"):]
    import re
    out = []
    for m in re.finditer(r"(\w+)\s*\{[^}]*?nFaces\s+(\d+);[^}]*?startFace\s+(\d+);", body, re.S):
        out.append((m.group(1), int(m.group(2)), int(m.group(3))))
    return out


def read_points(case):
    path = os.path.join(case, "constant", "polyMesh", "points")
    pts = []
    with open(path) as fh:
        n = None
        for line in fh:
            s = line.strip()
            if s.isdigit():
                n = int(s); break
        for line in fh:
            if line.strip() == "(":
                break
        while len(pts) < n:
            s = fh.readline().strip()
            if not s or s == "(":
                continue
            pts.append(tuple(float(x) for x in s.strip("()").split()))
    return pts


def read_faces(case, lo, hi):
    """Return {faceIndex: (v0,v1,...)} for global face indices in [lo,hi)."""
    path = os.path.join(case, "constant", "polyMesh", "faces")
    out = {}
    with open(path) as fh:
        n = None
        for line in fh:
            s = line.strip()
            if s.isdigit():
                n = int(s); break
        for line in fh:
            if line.strip() == "(":
                break
        i = 0
        while i < n:
            s = fh.readline().strip()
            if not s or s == "(":
                continue
            if lo <= i < hi:
                k = s.index("(")
                out[i] = tuple(int(x) for x in s[k + 1:s.rindex(")")].split())
            i += 1
            if i >= hi:
                break
    return out


def row_of(path, cast, want):
    """Return row `want` of an OpenFOAM ascii ListList, streaming."""
    with open(path) as fh:
        n = None
        for line in fh:
            s = line.strip()
            if s.isdigit():
                n = int(s); break
        for line in fh:
            if line.strip() == "(":
                break
        for r in range(n):
            m = None
            for line in fh:
                s = line.strip()
                if not s or s == "(":
                    continue
                m = int(s); break
            for line in fh:
                if line.strip() == "(":
                    break
            vals = []
            while len(vals) < m:
                s = fh.readline().strip()
                if not s:
                    continue
                vals.append(cast(s))
            for line in fh:
                if line.strip() == ")":
                    break
            if r == want:
                return vals
    return None


def tri_area_centroid(p):
    """OpenFOAM-style face area vector and centroid for a (possibly warped) face."""
    n = len(p)
    ctr = tuple(sum(q[k] for q in p) / n for k in range(3))
    Sf = [0.0, 0.0, 0.0]
    Cf = [0.0, 0.0, 0.0]
    asum = 0.0
    for i in range(n):
        a, b = p[i], p[(i + 1) % n]
        u = tuple(b[k] - a[k] for k in range(3))
        v = tuple(ctr[k] - a[k] for k in range(3))
        c = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
        mag = math.sqrt(sum(x * x for x in c)) / 2.0
        tc = tuple((a[k] + b[k] + ctr[k]) / 3.0 for k in range(3))
        for k in range(3):
            Sf[k] += c[k] / 2.0
            Cf[k] += mag * tc[k]
        asum += mag
    if asum > 0:
        Cf = [x / asum for x in Cf]
    return Sf, tuple(Cf), asum


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("case")
    ap.add_argument("--patch", required=True, help="emitting patch name")
    ap.add_argument("--row", type=int, default=None,
                    help="row within the patch (default: middle)")
    ap.add_argument("--R", type=float, default=None,
                    help="sphere radius for the exact kernel A_j/(4 pi R^2)")
    ap.add_argument("--alpha", type=float, default=0.21)
    a = ap.parse_args()

    bnds = read_boundary(a.case)
    off = 0
    comp = {}
    for nm, nf, sf in bnds:
        comp[nm] = (off, off + nf, sf)
        off += nf
    lo, hi, startFace = comp[a.patch]
    local = a.row if a.row is not None else (hi - lo) // 2
    grow_i = lo + local

    pts = read_points(a.case)
    faces = read_faces(a.case, min(b[2] for b in bnds),
                       max(b[2] + b[1] for b in bnds))
    # map compact index -> global face index
    def gface(ci):
        for nm, nf, sf in bnds:
            l, h, s = comp[nm]
            if l <= ci < h:
                return s + (ci - l), nm
        return None, None

    Frow = row_of(os.path.join(a.case, "constant", "F"), float, grow_i)
    Grow = row_of(os.path.join(a.case, "constant", "globalFaceFaces"), int, grow_i)

    gi, _ = gface(grow_i)
    vi = set(faces[gi])
    ei = set()
    fv = faces[gi]
    for k in range(len(fv)):
        ei.add(frozenset((fv[k], fv[(k + 1) % len(fv)])))

    buckets = defaultdict(lambda: {"n": 0, "F": 0.0, "exact": 0.0, "vals": []})
    R = a.R
    tot = 0.0
    for v, cj in zip(Frow, Grow):
        gj, pj = gface(cj)
        fj = faces[gj]
        shared_e = any(frozenset((fj[k], fj[(k + 1) % len(fj)])) in ei
                       for k in range(len(fj)))
        shared_p = len(vi.intersection(fj)) > 0
        if cj == grow_i:
            key = "self"
        elif shared_e:
            key = "shares an EDGE"
        elif shared_p:
            key = "shares a POINT only"
        else:
            key = "no shared vertex"
        key = "%-20s [%s]" % (key, pj)
        Sf, Cf, area = tri_area_centroid([pts[x] for x in fj])
        ex = area / (4.0 * math.pi * R * R) if R else 0.0
        b = buckets[key]
        b["n"] += 1
        b["F"] += v
        b["exact"] += ex
        b["vals"].append((v, ex))
        tot += v

    print("case  : %s" % os.path.abspath(a.case))
    print("emitter: patch %s, local row %d (global boundary index %d)" % (a.patch, local, grow_i))
    print("row sum: %.8f     (closed enclosure => must be exactly 1)" % tot)
    if R:
        print("exact kernel used: A_j/(4 pi R^2) with R = %g  (uniform for the inside of a sphere)" % R)
    print()
    print("%-42s %6s %14s %14s %14s %12s" %
          ("relationship to emitter", "count", "sum F (util)", "sum F (exact)",
           "excess", "per pair"))
    for k in sorted(buckets):
        b = buckets[k]
        print("%-42s %6d %14.8f %14.8f %14.8f %12.7f" %
              (k, b["n"], b["F"], b["exact"], b["F"] - b["exact"],
               (b["F"] - b["exact"]) / b["n"]))
    pred = -(2.0 * math.log(a.alpha) + 3.0) / (4.0 * math.pi)
    print()
    print("predicted per-shared-edge-pair error at alpha=%.5f : %+.7f" % (a.alpha, pred))
    print("(zero at alpha = exp(-3/2) = %.11f)" % math.exp(-1.5))


if __name__ == "__main__":
    main()
