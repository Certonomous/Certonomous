#!/usr/bin/env python3
r"""Bound the 4->16 rank RE-PARTITION on Cp, the quantity M6J actually grades.

Two runs, both advanced from the SAME verified checkpoint t=3800 to t=4200, with
identical schemes, solvers, relaxation and turbulence model.  THE ONLY DIFFERENCE
IS THE PARTITION:

  control  verification/runs/M6J_runs/M6J_L1_CP_CONTROL_4RANK  n (2 2 1),  4 ranks
  graded   verification/runs/M6J_runs/M6J_L1                   n (2 2 4), 16 ranks

WHY THIS EXISTS.  ADDENDUM 2 sec.A2.3 registered the re-partition as a perturbation.
The 85-iteration double-computed overlap bounded it on the FORCE COEFFICIENTS
(Cd max 1.62e-04) -- but those are INTEGRALS of surface pressure, and cancellation
can hide a local difference inside an integral.  The M6J gate reads Cp LOCALLY, at
span stations eta = 0.65 and 0.90.  That read was unbounded until this comparison.

Cp comes from the family's OWN extractor, verification/runs/M6I_runs/extract_cp_m6i.py,
so this measures the partition and not two different definitions of Cp.

REFUSES rather than degrades: if the two station grids do not correspond point for
point, no number is printed.  A Cp difference computed against a resampled or
reordered surface would be a measurement of the interpolation.
"""
from __future__ import annotations

import json
import math
import sys

GATE_STATIONS = ("0.65", "0.9")


def load(path):
    with open(path) as f:
        return json.load(f)


def main(argv):
    if len(argv) < 2:
        print("usage: compare_cp_partition.py <cp_4rank.json> <cp_16rank.json>")
        return 2
    a, b = load(argv[0]), load(argv[1])
    sa, sb = a["stations"], b["stations"]

    common = [k for k in sa if k in sb]
    if not common:
        print("REFUSE: no common stations")
        return 2
    missing = sorted(set(sa) ^ set(sb))
    if missing:
        print(f"REFUSE: station sets differ: {missing}")
        return 2

    def eta_key(k):
        return float(k)

    print("RE-PARTITION BOUND ON Cp  --  4 ranks n(2 2 1)  vs  16 ranks n(2 2 4)")
    print("both advanced t=3800 -> t=4200, one change: the partition\n")
    print(f"{'eta':>6} {'n_pts':>6} {'Cp range':>16} {'max|dCp|':>11} "
          f"{'rms dCp':>11} {'max|dCp|/range':>15} {'gate':>6}")
    worst = 0.0
    worst_gate = 0.0
    for k in sorted(common, key=eta_key):
        A, B = sa[k], sb[k]
        if A["n_points"] != B["n_points"]:
            print(f"REFUSE: eta={k} point counts differ "
                  f"({A['n_points']} vs {B['n_points']}) -- grids do not correspond")
            return 2
        xa, xb = A["xoc"], B["xoc"]
        # the cut must land on the same surface points, or a Cp delta is meaningless
        dx = max(abs(p - q) for p, q in zip(xa, xb))
        if dx > 1e-9:
            print(f"REFUSE: eta={k} x/c grids differ by {dx:.3e} -- not point-for-point")
            return 2
        ca, cb = A["cp"], B["cp"]
        d = [p - q for p, q in zip(ca, cb)]
        mx = max(abs(v) for v in d)
        rms = math.sqrt(sum(v * v for v in d) / len(d))
        rng = max(ca) - min(ca)
        is_gate = k in GATE_STATIONS
        worst = max(worst, mx)
        if is_gate:
            worst_gate = max(worst_gate, mx)
        print(f"{k:>6} {A['n_points']:>6} [{min(ca):>6.3f},{max(ca):>6.3f}] "
              f"{mx:>11.3e} {rms:>11.3e} {mx/rng:>15.3e} {'GATE' if is_gate else '':>6}")

    print(f"\n  worst |dCp| over all six stations : {worst:.3e}")
    print(f"  worst |dCp| at the GATE stations  : {worst_gate:.3e}  (eta 0.65, 0.90)")
    print("\n  This is the re-partition's effect on the graded read, measured, not assumed.")
    print("  It is NOT round-off: it is round-off amplified by 400 iterations of an")
    print("  iterative solve that has not yet converged to a fixed point.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
