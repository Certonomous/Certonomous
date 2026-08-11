#!/usr/bin/env python3
"""F7a: what does the OLD front-position definition actually evaluate to?

This script exists to answer one question with data instead of assertion:

    The 2026-07-28 gate spec defined the surge front as
        "the alpha.water = 0.5 crossing at the first cell above the floor"
    (system/sampling comment, verbatim: "Horizontal line just above the floor
    (y = half of first cell height), used to locate the surge-front position
    (alpha.water = 0.5 crossing)").

    That sentence admits more than one faithful reading.  Do the readings give
    materially different numbers on the SAME solver output?

It reads only ALREADY-WRITTEN, git-tracked field data.  It runs no solver.

Readings implemented (each is a defensible reading of the old prose, not a
strawman):

  A_row0_interp   row 0 (cell centres at y = dy/2), alpha=0.5 crossing found by
                  linear interpolation between cell centres, FURTHEST crossing.
                  Closest to what was actually executed.
  B_row1_interp   row 1 (y = 3dy/2).  "the first cell ABOVE the floor" read as
                  the first cell above the floor-adjacent cell.
  C_row0_cell     row 0, no interpolation: front = x of the LAST cell centre
                  whose alpha >= 0.5 ("nearest cell").
  D_row0_face     row 0, no interpolation: front = downstream FACE of that cell.
  E_row0_first    row 0, interpolated, but the FIRST crossing from the left
                  rather than the furthest.
  F_row0_a005     row 0, interpolated, threshold alpha = 0.05 (interface smeared
                  across several cells -> "where the water ends" read as the
                  air-side edge of the smear).
  G_row0_a095     row 0, interpolated, threshold alpha = 0.95 (water-side edge).

Comparison-axis readings (applied to reading A unless stated):

  Z_at_T          deviation in Z evaluated at the reference T   (as published)
  T_at_Z          deviation in T evaluated at the reference Z   (equally
                  faithful: the Martin & Moyce points sit at ROUND Z values,
                  6,7,...,13 -- the measured quantity is the time to reach a
                  station, so "deviation" can be taken along either axis)
  n6 / n8         mean taken over the six points T=3.90-7.72 or all eight

Time-origin readings:

  t0_solver       T = t * sqrt(g/a), t = OpenFOAM time (t=0 at solver start)
  t0_Z1           t re-zeroed at the instant the front leaves the column
                  footprint (Z = 1), a convention used to remove the release
                  transient

Usage:  old_spec_readings.py <case_dir> [out.json]
"""
import bisect
import gzip
import json
import math
import os
import re
import sys
from collections import defaultdict

G = 9.81
A = 0.05715  # Martin & Moyce a = 2 1/4 in

# Martin & Moyce (1952) front points, digitised twice independently from Fig. 7
# of Leakey, Glenis & Hewett (arXiv:2108.08769).  Copied from grade_f7a.py so
# the two scripts are graded against an identical reference.
MM_FRONT = [(3.90, 6.00), (4.49, 7.00), (5.17, 8.00), (5.91, 9.00),
            (6.70, 10.00), (7.72, 11.00), (8.58, 12.00), (9.53, 13.00)]
SIX = MM_FRONT[:6]


def _open(path):
    if os.path.exists(path):
        return open(path)
    if os.path.exists(path + ".gz"):
        return gzip.open(path + ".gz", "rt")
    raise FileNotFoundError(path)


def _read_list(path, kind):
    txt = _open(path).read()
    m = re.search(
        r"internalField\s+nonuniform\s+List<%s>\s*\n(\d+)\n\(\n(.*?)\n\)\s*;" % kind,
        txt, re.S)
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
    return [tuple(float(v) for v in ln.strip().strip("()").split()) for ln in body]


def find_centres(case_dir):
    for d in sorted(os.listdir(case_dir)):
        p = os.path.join(case_dir, d, "C")
        if os.path.exists(p) or os.path.exists(p + ".gz"):
            return p
    raise SystemExit("no cell-centre field C in %s" % case_dir)


# --- front readings ---------------------------------------------------------

ROWDP = 8  # decimals used to group cell centres into rows.  9 splits the
           # a/16 family's upper rows on ASCII round-off (37 apparent rows for
           # a 240x20 mesh); 8 recovers exactly 20.  Rows 0 and 1 -- the only
           # ones this script probes -- carry the full nx count at either
           # setting on all 15 tracked cases, checked before use.


def _row(alpha, C, ys, k):
    """(xs, alphas) along the k-th cell row from the floor, sorted in x."""
    yk = ys[k]
    pts = [(C[i][0], alpha[i]) for i in range(len(C))
           if round(C[i][1], ROWDP) == yk]
    pts.sort()
    return [p[0] for p in pts], [p[1] for p in pts]


def cross_interp(xs, al, thr, furthest=True):
    """alpha crosses down through thr; linear interp between cell centres."""
    hits = []
    for i in range(len(xs) - 1):
        a0, a1 = al[i], al[i + 1]
        if (a0 - thr) * (a1 - thr) <= 0 and a0 != a1:
            hits.append(xs[i] + (thr - a0) / (a1 - a0) * (xs[i + 1] - xs[i]))
    if not hits:
        return None
    return hits[-1] if furthest else hits[0]


def last_cell(xs, al, thr, dx, face=False):
    """x of the last cell whose alpha >= thr (its centre, or its downstream face)."""
    idx = [i for i, v in enumerate(al) if v >= thr]
    if not idx:
        return None
    x = xs[idx[-1]]
    return x + 0.5 * dx if face else x


READINGS = ["A_row0_interp", "B_row1_interp", "C_row0_cell", "D_row0_face",
            "E_row0_first", "F_row0_a005", "G_row0_a095"]


def fronts(alpha, C, ys, dx):
    x0, a0 = _row(alpha, C, ys, 0)
    out = {}
    out["A_row0_interp"] = cross_interp(x0, a0, 0.5, furthest=True)
    if len(ys) > 1:
        x1, a1 = _row(alpha, C, ys, 1)
        out["B_row1_interp"] = cross_interp(x1, a1, 0.5, furthest=True)
    else:
        out["B_row1_interp"] = None
    out["C_row0_cell"] = last_cell(x0, a0, 0.5, dx, face=False)
    out["D_row0_face"] = last_cell(x0, a0, 0.5, dx, face=True)
    out["E_row0_first"] = cross_interp(x0, a0, 0.5, furthest=False)
    out["F_row0_a005"] = cross_interp(x0, a0, 0.05, furthest=True)
    out["G_row0_a095"] = cross_interp(x0, a0, 0.95, furthest=True)
    return {k: (v / A if v is not None else None) for k, v in out.items()}


# --- grading ----------------------------------------------------------------

def interp_xy(rows, x):
    xs = [r[0] for r in rows]
    i = bisect.bisect_left(xs, x)
    if i <= 0 or i >= len(rows):
        return None
    (x0, y0), (x1, y1) = rows[i - 1], rows[i]
    return y0 + (x - x0) / (x1 - x0) * (y1 - y0)


def dev_Z_at_T(series, ref):
    """series = [(T, Z)]; deviation in Z at each reference T."""
    devs = []
    for T, Zr in ref:
        Zs = interp_xy(series, T)
        if Zs is None:
            continue
        devs.append((T, Zr, Zs, (Zs - Zr) / Zr * 100.0))
    return devs


def dev_T_at_Z(series, ref):
    """deviation in T at each reference Z (invert the series: Z -> T)."""
    inv = sorted((Z, T) for T, Z in series if Z is not None)
    devs = []
    for Tr, Zr in ref:
        Ts = interp_xy(inv, Zr)
        if Ts is None:
            continue
        devs.append((Zr, Tr, Ts, (Ts - Tr) / Tr * 100.0))
    return devs


def summarise(devs):
    if not devs:
        return None, None, 0
    d = [r[3] for r in devs]
    return sum(d) / len(d), max(abs(v) for v in d), len(d)


def main():
    case_dir = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else None

    C = read_vector(find_centres(case_dir))
    ys = sorted({round(c[1], ROWDP) for c in C})
    xs_all = sorted({round(c[0], 9) for c in C})
    dy = ys[1] - ys[0] if len(ys) > 1 else 2 * ys[0]
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

    series = {k: [] for k in READINGS}
    rows = []
    for t, d in times:
        alpha = read_scalar(os.path.join(case_dir, d, "alpha.water"), len(C))
        f = fronts(alpha, C, ys, dx)
        T = t * math.sqrt(G / A)
        rows.append(dict(t=t, T=T, **f))
        for k in READINGS:
            if f[k] is not None:
                series[k].append((T, f[k]))

    print("case %s   dx=a/%.0f  dy=a/%.0f  ncells=%d  nrows=%d"
          % (case_dir, A / dx, A / dy, len(C), len(ys)))
    print("row 0 centre y = %.6g m = a/%.1f ; row 1 centre y = %.6g m = a/%.1f"
          % (ys[0], A / ys[0], ys[1], A / ys[1]))

    # 1. front readings, Z at reference T, six-point and eight-point means
    print("\n[1] FRONT-CRITERION READINGS  (deviation in Z at reference T)")
    print("  %-16s %10s %10s %6s   %10s %10s %6s"
          % ("reading", "mean6", "max6", "n", "mean8", "max8", "n"))
    summary = {}
    for k in READINGS:
        m6, x6, n6 = summarise(dev_Z_at_T(series[k], SIX))
        m8, x8, n8 = summarise(dev_Z_at_T(series[k], MM_FRONT))
        summary[k] = dict(mean6=m6, max6=x6, n6=n6, mean8=m8, max8=x8, n8=n8)
        fmt = lambda v: "-" if v is None else "%+.1f%%" % v
        print("  %-16s %10s %10s %6d   %10s %10s %6d"
              % (k, fmt(m6), fmt(x6), n6, fmt(m8), fmt(x8), n8))

    # 2. pointwise table for the two readings that bracket the spread
    print("\n[2] POINTWISE, reading A (row 0) vs reading B (row 1)")
    print("  %6s %8s %10s %10s %10s %10s"
          % ("T", "Z_ref", "Z_A", "dev_A", "Z_B", "dev_B"))
    for T, Zr in MM_FRONT:
        Za = interp_xy(series["A_row0_interp"], T)
        Zb = interp_xy(series["B_row1_interp"], T)
        f = lambda v: "-" if v is None else "%.3f" % v
        da = "-" if Za is None else "%+.1f%%" % ((Za - Zr) / Zr * 100)
        db = "-" if Zb is None else "%+.1f%%" % ((Zb - Zr) / Zr * 100)
        print("  %6.2f %8.2f %10s %10s %10s %10s" % (T, Zr, f(Za), da, f(Zb), db))

    # 3. comparison-axis reading: deviation in T at reference Z
    print("\n[3] COMPARISON-AXIS READING (reading A held fixed)")
    m6z, x6z, n6z = summarise(dev_Z_at_T(series["A_row0_interp"], SIX))
    m6t, x6t, n6t = summarise(dev_T_at_Z(series["A_row0_interp"], SIX))
    m8t, x8t, n8t = summarise(dev_T_at_Z(series["A_row0_interp"], MM_FRONT))
    axis = dict(Z_at_T_mean6=m6z, Z_at_T_max6=x6z,
                T_at_Z_mean6=m6t, T_at_Z_max6=x6t, T_at_Z_n6=n6t,
                T_at_Z_mean8=m8t, T_at_Z_max8=x8t, T_at_Z_n8=n8t)
    g = lambda v: "-" if v is None else "%+.1f%%" % v
    print("  deviation in Z at reference T : mean6 %s  max6 %s  (n=%d)"
          % (g(m6z), g(x6z), n6z))
    print("  deviation in T at reference Z : mean6 %s  max6 %s  (n=%d)"
          % (g(m6t), g(x6t), n6t))
    print("  deviation in T at reference Z : mean8 %s  max8 %s  (n=%d)"
          % (g(m8t), g(x8t), n8t))

    # 4. time-origin reading: re-zero t at the instant the front reaches Z=1
    print("\n[4] TIME-ORIGIN READING (reading A held fixed)")
    inv = sorted((Z, T) for T, Z in series["A_row0_interp"])
    T_at_Z1 = interp_xy(inv, 1.0)
    T_first = series["A_row0_interp"][0][0]
    origin = {"T_at_Z1": T_at_Z1, "T_first_write": T_first}
    print("  t0 = solver start (as published) : mean6 %s  max6 %s" % (g(m6z), g(x6z)))

    # (i) t0 at the first written field -- a literal reading of "time origin =
    #     first solver write".  Shifts every T by the write interval.
    shifted_w = [(T - T_first, Z) for T, Z in series["A_row0_interp"]]
    m6w, x6w, n6w = summarise(dev_Z_at_T(shifted_w, SIX))
    origin.update(write_mean6=m6w, write_max6=x6w, write_n6=n6w)
    print("  t0 = first solver write (T=%.4f): mean6 %s  max6 %s"
          % (T_first, g(m6w), g(x6w)))

    # (ii) t0 re-zeroed when the front leaves the column footprint (Z=1).
    if T_at_Z1 is not None:
        shifted = [(T - T_at_Z1, Z) for T, Z in series["A_row0_interp"]]
        m6s, x6s, n6s = summarise(dev_Z_at_T(shifted, SIX))
        origin.update(shift_mean6=m6s, shift_max6=x6s, shift_n6=n6s)
        print("  t0 re-zeroed at Z=1 (T=%.4f) : mean6 %s  max6 %s"
              % (T_at_Z1, g(m6s), g(x6s)))
    else:
        print("  t0 re-zeroed at Z=1  : NOT EVALUABLE -- the front is already "
              "at Z=%.3f by the first written field (T=%.4f), so the archived "
              "write cadence cannot resolve the release transient"
              % (series["A_row0_interp"][0][1], T_first))

    if out_path:
        json.dump({"case": case_dir, "a": A, "dx": dx, "dy": dy,
                   "ncells": len(C), "nrows": len(ys),
                   "y_row0": ys[0], "y_row1": ys[1] if len(ys) > 1 else None,
                   "readings": summary, "axis": axis, "origin": origin,
                   "rows": rows},
                  open(out_path, "w"), indent=1)


if __name__ == "__main__":
    main()
