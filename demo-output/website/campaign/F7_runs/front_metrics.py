#!/usr/bin/env python3
"""F7a surge-front extraction, mesh-independent form.

Reads reconstructed interFoam time directories (structured 2D blockMesh) and
returns, for each written time, the surge-front position Z = x_front/a using a
depth-integrated water height

    h(x) = sum_over_column( alpha.water * dy )

with the front located where h(x) falls through a *physical* threshold
expressed as a fraction of the initial column height a.  Sweeping that
threshold gives an honest uncertainty band on the metric itself, which the
earlier single-threshold (0.01a) and single-row (alpha=0.5 line probe)
definitions did not provide.

Non-dimensionalisation follows Leakey, Glenis & Hewett (arXiv:2108.08769)
Sec 3.3.2 / Fig. 7, which states verbatim that column height and surge front
position are "normalised by dividing by a, and the time multiplied by
sqrt(g/a)".

Usage:  front_metrics.py <case_dir> <a> <thresholds,comma-sep> [out.json]
Cell centres are taken from a `C` field written by `postProcess -func writeCellCentres`
(auto-detected in the first available time directory that has one).
"""
import gzip
import json
import math
import os
import re
import sys
from collections import defaultdict

G = 9.81


def _open(path):
    """Open an OpenFOAM field, transparently handling the .gz form."""
    if os.path.exists(path):
        return open(path)
    if os.path.exists(path + ".gz"):
        return gzip.open(path + ".gz", "rt")
    raise FileNotFoundError(path)


def _read_list(path, kind):
    txt = _open(path).read()
    m = re.search(
        r"internalField\s+nonuniform\s+List<%s>\s*\n(\d+)\n\(\n(.*?)\n\)\s*;" % kind,
        txt,
        re.S,
    )
    if m is None:
        m2 = re.search(r"internalField\s+uniform\s+([-\d.eE+]+)\s*;", txt)
        if m2 is not None:
            return None, float(m2.group(1))
        raise ValueError("cannot parse %s" % path)
    n = int(m.group(1))
    body = m.group(2).split("\n")
    assert len(body) == n, (len(body), n, path)
    return body, None


def read_scalar(path, ncells):
    body, uni = _read_list(path, "scalar")
    if body is None:
        return [uni] * ncells
    return [float(x) for x in body]


def read_vector(path):
    body, _ = _read_list(path, "vector")
    out = []
    for line in body:
        out.append(tuple(float(v) for v in line.strip().strip("()").split()))
    return out


def find_centres(case_dir):
    for d in sorted(os.listdir(case_dir)):
        p = os.path.join(case_dir, d, "C")
        if os.path.exists(p) or os.path.exists(p + ".gz"):
            return p
    raise SystemExit("no C (cell-centre) field found in %s; run "
                     "`postProcess -func writeCellCentres`" % case_dir)


def column_profile(alpha, C, dy):
    """Depth-integrated water height h(x) on the structured column grid."""
    cols = defaultdict(float)
    for i, c in enumerate(C):
        cols[round(c[0], 9)] += alpha[i] * dy
    xs = sorted(cols)
    return xs, [cols[x] for x in xs]


def front_at(xs, h, thresh):
    """Furthest x at which h(x) crosses down through `thresh` (linear interp)."""
    for i in range(len(xs) - 1, 0, -1):
        if h[i] < thresh <= h[i - 1]:
            den = h[i] - h[i - 1]
            frac = (thresh - h[i - 1]) / den if den else 0.0
            return xs[i - 1] + frac * (xs[i] - xs[i - 1])
    return None


def column_height(alpha, C, dx, a):
    """Mean water depth over the ORIGINAL column footprint 0 <= x <= a,
    normalised by a.  Martin & Moyce's 'column height' measurement."""
    tot = 0.0
    for i, c in enumerate(C):
        if c[0] <= a:
            tot += alpha[i]
    # number of x-columns inside the footprint
    ncol = len({round(c[0], 9) for c in C if c[0] <= a})
    nrow = len({round(c[1], 9) for c in C})
    return tot / (ncol * nrow) * (
        (max(c[1] for c in C) + 0.5 * (max(c[1] for c in C) / (nrow - 0.5))) / a
    ) if nrow > 1 else 0.0


def main():
    case_dir = sys.argv[1]
    a = float(sys.argv[2])
    thresholds = [float(t) for t in sys.argv[3].split(",")]
    out_path = sys.argv[4] if len(sys.argv) > 4 else None

    cpath = find_centres(case_dir)
    C = read_vector(cpath)
    ys = sorted({round(c[1], 9) for c in C})
    dy = ys[1] - ys[0] if len(ys) > 1 else 2 * ys[0]
    xs_all = sorted({round(c[0], 9) for c in C})
    dx = xs_all[1] - xs_all[0]

    times = []
    for d in os.listdir(case_dir):
        try:
            t = float(d)
        except ValueError:
            continue
        ap = os.path.join(case_dir, d, "alpha.water")
        if t > 0 and (os.path.exists(ap) or os.path.exists(ap + ".gz")):
            times.append((t, d))
    times.sort()

    rows = []
    for t, d in times:
        alpha = read_scalar(os.path.join(case_dir, d, "alpha.water"), len(C))
        xs, h = column_profile(alpha, C, dy)
        rec = {"t": t, "T": t * math.sqrt(G / a)}
        for th in thresholds:
            f = front_at(xs, h, th * a)
            rec["Z_%g" % th] = f / a if f is not None else None
        # Martin & Moyce "column height": water depth at the back wall,
        # i.e. the leftmost column of cells, normalised by a.
        rec["h_col"] = h[0] / a
        rows.append(rec)

    hdr = "  T      " + "".join("Z(%.3fa)  " % th for th in thresholds) + " h_col"
    print("case: %s   dx=%.5g (a/%.1f)  dy=%.5g (a/%.1f)  ncells=%d"
          % (case_dir, dx, a / dx, dy, a / dy, len(C)))
    print(hdr)
    for r in rows:
        line = "%6.3f  " % r["T"]
        for th in thresholds:
            v = r["Z_%g" % th]
            line += "%9s " % ("%.4f" % v if v is not None else "-")
        line += "  %.4f" % r["h_col"]
        print(line)

    if out_path:
        json.dump({"case": case_dir, "a": a, "dx": dx, "dy": dy,
                   "ncells": len(C), "thresholds": thresholds, "rows": rows},
                  open(out_path, "w"), indent=1)


if __name__ == "__main__":
    main()
