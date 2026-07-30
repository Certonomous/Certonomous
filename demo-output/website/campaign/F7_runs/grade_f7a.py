#!/usr/bin/env python3
"""F7a grading: interFoam dam break vs Martin & Moyce (1952).

Two references, both traceable:

  MM_FRONT / MM_HEIGHT
      Martin & Moyce (1952) experimental points, digitised from Fig. 7 of
      Leakey, Glenis & Hewett, arXiv:2108.08769.  Digitised twice,
      independently: once in the original F7 pass (2026-07-28) and once in the
      2026-07-30 R1 audit by axis-tick calibration + connected-component
      centroid detection at 600 dpi.  The two digitisations agree to <=0.01 in
      T and <=0.005 in Z on all eight front points.

  REF_SIM
      The same figure's own simulation curve (Bassi split pressure superbee,
      inviscid, no surface tension, no interface compression, 240x20 cells =
      dx=dy=a/16, domain 15a x 1.25a).  Digitised in the R1 audit by green-pixel
      column-mean.  This is the code-to-code comparator: it is the standard a
      published solver achieves on this benchmark with this mesh.

Usage: grade_f7a.py <metrics.json from front_metrics.py> [threshold]
"""
import bisect
import json
import sys

# --- Martin & Moyce (1952) experimental points, Fig. 7 left column ----------
MM_FRONT = [(3.90, 6.00), (4.49, 7.00), (5.17, 8.00), (5.91, 9.00),
            (6.70, 10.00), (7.72, 11.00), (8.58, 12.00), (9.53, 13.00)]
MM_HEIGHT = [(0.00, 1.00), (0.80, 0.89), (1.29, 0.78), (1.74, 0.67),
             (2.15, 0.56), (2.57, 0.44), (3.08, 0.33), (4.27, 0.22),
             (6.30, 0.11)]

# --- reference paper's own simulation, same figure -------------------------
REF_SIM = [(-0.017, 0.998), (0.846, 1.437), (1.537, 2.332), (2.228, 3.252),
           (2.919, 4.326), (3.783, 5.583), (4.474, 6.678), (5.165, 7.669),
           (5.855, 8.648), (6.546, 9.640), (7.237, 10.564), (7.928, 11.380),
           (8.619, 12.221), (9.310, 13.003)]


def interp(rows, x):
    xs = [r[0] for r in rows]
    i = bisect.bisect_left(xs, x)
    if i <= 0 or i >= len(rows):
        return None
    (x0, y0), (x1, y1) = rows[i - 1], rows[i]
    return y0 + (x - x0) / (x1 - x0) * (y1 - y0)


def table(sim, ref, label, unit=""):
    devs = []
    print("  %-6s %-10s %-10s %s" % ("T", "ref", "sim", "dev"))
    for T, R in ref:
        S = interp(sim, T)
        if S is None:
            continue
        d = (S - R) / R * 100
        devs.append(d)
        print("  %6.2f %10.3f %10.3f  %+6.1f%%" % (T, R, S, d))
    if devs:
        mean = sum(devs) / len(devs)
        print("  %s: mean %+.1f%%, max |dev| %.1f%%, n=%d"
              % (label, mean, max(abs(d) for d in devs), len(devs)))
    return devs


def main():
    data = json.load(open(sys.argv[1]))
    th = sys.argv[2] if len(sys.argv) > 2 else "%g" % data["thresholds"][0]
    key = "Z_" + th
    rows = data["rows"]
    front = [(r["T"], r[key]) for r in rows if r.get(key) is not None]
    height = [(r["T"], r["h_col"]) for r in rows]

    print("case %s  (%d cells, dx=%.5g, dy=%.5g)  front threshold h=%sa"
          % (data["case"], data["ncells"], data["dx"], data["dy"], th))
    print("\n[1] surge front vs Martin & Moyce (1952) experiment")
    table(front, MM_FRONT, "FRONT vs EXPERIMENT")
    print("\n[2] surge front vs reference paper's own simulation (same figure)")
    table(front, REF_SIM[3:], "FRONT vs REFERENCE SIM")
    print("\n[3] column height at back wall vs Martin & Moyce (1952) experiment")
    table(height, [p for p in MM_HEIGHT if p[0] > 0], "COLUMN HEIGHT vs EXPERIMENT")


if __name__ == "__main__":
    main()
