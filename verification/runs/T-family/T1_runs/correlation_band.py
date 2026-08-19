#!/usr/bin/env python3
"""
Arm T1b's band from two published correlations, BEFORE any case exists.

The design claim in T1's specification 3.2 is that this band is fixed by the two
formulae and the swept Reynolds numbers alone, so no solution can move it.  That
claim is only checkable if the band is computed and committed NOW, with no case
directory in existence.  That is what this script is for.

  Dittus-Boelter  Nu = 0.023 Re^0.8 Pr^n,  n = 0.4 heating
                  stated validity 0.6 <= Pr <= 160, Re >~ 1e4, L/D >~ 10
  Gnielinski      Nu = (f/8)(Re-1000)Pr / [1 + 12.7 (f/8)^0.5 (Pr^(2/3) - 1)]
                  f = (0.790 ln Re - 1.64)^-2   (Petukhov)
                  stated validity 0.5 <= Pr <= 2000, 3000 <= Re <= 5e6

  reference = midpoint,  band = half-spread.

REGISTERED HONESTY CONDITION (specification 3.2): where the half-spread is below
2 % of the midpoint the row is REPORTED, NEVER GRADED, because the band would
then be measuring the two correlations' coincidental agreement rather than this
lab's error.  That rule is applied here, not left to a reader.
"""
import json
import math
import os
import sys

PR = 0.71
RE_SWEEP = (1.0e4, 3.0e4, 1.0e5, 3.0e5)
MIN_HALF_SPREAD_PCT = 2.0

DB_VALID = dict(Pr=(0.6, 160.0), Re=(1.0e4, None), note="L/D >~ 10")
GN_VALID = dict(Pr=(0.5, 2000.0), Re=(3.0e3, 5.0e6), note="")


def dittus_boelter(Re, Pr, heating=True):
    return 0.023 * Re ** 0.8 * Pr ** (0.4 if heating else 0.3)


def petukhov_f(Re):
    return (0.790 * math.log(Re) - 1.64) ** -2.0


def gnielinski(Re, Pr):
    f = petukhov_f(Re)
    return ((f / 8.0) * (Re - 1000.0) * Pr
            / (1.0 + 12.7 * math.sqrt(f / 8.0) * (Pr ** (2.0 / 3.0) - 1.0)))


def in_range(v, lo, hi):
    return (lo is None or v >= lo) and (hi is None or v <= hi)


def main():
    rows = []
    print(f"T1b band, armed from two correlations at Pr = {PR}\n")
    print(f"{'Re':>10}  {'Dittus-Boelter':>15} {'Gnielinski':>12} "
          f"{'midpoint':>10} {'band':>9} {'band %':>8}  status")
    for Re in RE_SWEEP:
        db = dittus_boelter(Re, PR)
        gn = gnielinski(Re, PR)
        mid = 0.5 * (db + gn)
        band = 0.5 * abs(db - gn)
        pct = 100.0 * band / mid
        graded = pct >= MIN_HALF_SPREAD_PCT
        # validity is checked, not assumed
        v = []
        if not in_range(PR, *DB_VALID["Pr"]):
            v.append("Pr outside Dittus-Boelter")
        if not in_range(Re, *DB_VALID["Re"]):
            v.append("Re outside Dittus-Boelter")
        if not in_range(PR, *GN_VALID["Pr"]):
            v.append("Pr outside Gnielinski")
        if not in_range(Re, *GN_VALID["Re"]):
            v.append("Re outside Gnielinski")
        status = "GRADED" if graded else f"REPORTED (< {MIN_HALF_SPREAD_PCT} %)"
        if v:
            status = "REFUSED: " + "; ".join(v)
        rows.append(dict(Re=Re, Pr=PR, dittus_boelter=db, gnielinski=gn,
                         reference=mid, band=band, band_pct=pct,
                         graded=graded and not v,
                         validity_violations=v,
                         petukhov_f=petukhov_f(Re)))
        print(f"{Re:10.0f}  {db:15.3f} {gn:12.3f} {mid:10.3f} {band:9.3f} "
              f"{pct:7.2f}%  {status}")

    ng = sum(1 for r in rows if r["graded"])
    print(f"\n{ng} of {len(rows)} swept points arm a band; "
          f"{len(rows)-ng} report without grading.")
    spread = [r["band_pct"] for r in rows]
    print(f"half-spread ranges {min(spread):.2f} % to {max(spread):.2f} % "
          "across the sweep.")
    print("\nWHAT THIS BAND IS NOT: it is the disagreement between two accepted "
          "correlations,")
    print("not either correlation's own stated accuracy, which neither source "
          "provides here.")
    print("It therefore bounds what the LITERATURE agrees on, and a solution "
          "inside it is")
    print("consistent with the canon -- NOT verified to that tolerance.")

    out = dict(Pr=PR, Re_sweep=list(RE_SWEEP),
               min_half_spread_pct=MIN_HALF_SPREAD_PCT, rows=rows,
               armed_before_any_case=True)
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "T1b_band.json")
    with open(p, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(f"\nwritten: {os.path.basename(p)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
