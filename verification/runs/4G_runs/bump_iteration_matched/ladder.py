"""Regenerate section 10's matched-iteration table and drag split.

Why a matched table exists at all: the published bump ladder stops its three rungs at
4,000 / 6,000 / 9,000 iterations, so the (large, still-moving) iterative error is unequal
across the rungs by construction and feeds straight into the grid-to-grid increments that
the observed order is computed from. `coefficient.dat` records Cd at every iteration, so
the ladder can be recomputed at any COMMON iteration count and the two effects separated.

Reads only committed files:
  - cd_history.dat.gz in this directory (the 30,000-iteration re-runs), and
  - demo-output/website/tmr/runs/bump-{coarse,medium,fine}/postProcessing/... (published)
The re-runs reproduce the published runs where they overlap: coarse at n = 4,000 agrees to
+0.0009%, and all three log.checkMesh reproduce 4G_runs/bump/log.checkMesh.* exactly.

Usage:  python3 ladder.py
"""
import gzip
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
PUB = os.path.join(REPO, "demo-output", "website", "tmr", "runs")
LEVELS = ("coarse", "medium", "fine")


def _read(path, opener, col):
    out = {}
    with opener(path, "rt") as handle:
        for line in handle:
            if line.startswith("#"):
                continue
            parts = line.split()
            out[int(float(parts[0]))] = float(parts[col])
    return out


def history(level):
    """Cd against iteration, re-run history preferred, published filling the gaps."""
    merged = {}
    rerun = os.path.join(HERE, level, "cd_history.dat.gz")
    if os.path.exists(rerun):
        merged.update(_read(rerun, gzip.open, 1))
    published = os.path.join(
        PUB, f"bump-{level}", "postProcessing", "forceCoeffs1", "0", "coefficient.dat")
    if os.path.exists(published):
        for n, cd in _read(published, open, 1).items():
            merged.setdefault(n, cd)
    return merged


def order(values):
    """Observed order, Richardson value and GCI on a factor-2 refinement triple.

    Returns None when the increments change sign: a ladder whose successive increments do
    not shrink monotonically has no observed order, and inventing one anyway is the B-52
    mistake this corpus has already paid for once.
    """
    lo, mid, hi = values
    d21, d32 = mid - lo, hi - mid
    if d21 * d32 <= 0:
        return None
    p = math.log(d21 / d32) / math.log(2.0)
    richardson = hi + d32 / (2 ** p - 1)
    gci = 1.25 * abs(d32 / hi) / (2 ** p - 1) * 100
    return p, richardson, gci


def main():
    runs = {level: history(level) for level in LEVELS}
    print("Cd histories available to iteration:",
          {level: max(runs[level]) for level in LEVELS})
    print(f"\n{'matched n':>9} {'coarse':>13} {'medium':>13} {'fine':>13} "
          f"{'p':>8} {'GCI fine':>9} {'Rich-fine':>10}")
    for n in (500, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000,
              10000, 12000, 15000, 20000, 25000, 30000):
        if not all(n in runs[level] for level in LEVELS):
            continue
        values = [runs[level][n] for level in LEVELS]
        row = f"{n:9d} " + " ".join(f"{v:13.9f}" for v in values)
        result = order(values)
        if result is None:
            print(row + "   increments cross: no observed order")
            continue
        p, richardson, gci = result
        print(row + f" {p:8.4f} {gci:8.3f}% "
                    f"{100 * (richardson - values[-1]) / values[-1]:9.3f}%")
    published = [runs["coarse"][4000], runs["medium"][6000], runs["fine"][9000]]
    p, _, gci = order(published)
    print(f"\nas published, unmatched caps 4000/6000/9000: p = {p:.4f}, GCI = {gci:.3f}%")
    print("bump_sst.json quotes p = 0.5446, GCI = 3.839% from the original serial runs")


if __name__ == "__main__":
    main()
