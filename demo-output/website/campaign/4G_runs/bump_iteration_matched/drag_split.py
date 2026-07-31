"""Pressure/viscous drag split at MATCHED iteration counts.

Section 10.4 blames the bump ladder's low observed order on a pressure-drag component with
no observed order at all. That claim must not rest on the rungs' own unequal iteration
caps, which is the exact fault section 10.3 convicts the published total of. It does not
have to: `forceCoeffs` prints the Total/Pressure/Viscous split at every iteration into
`log.simpleFoam`, so the split is recoverable at any matched count for free.

Result: the pressure increments change sign at EVERY matched count from 3,000 to 9,000,
and the second increment grows steadily more positive as the rungs converge rather than
shrinking toward zero. The pressure drag is not a nearly-converged quantity that a longer
run would tidy up.

Sources, in order of preference per rung:
  - drag_split.dat.gz in this directory (coarse and medium, out to 30,000 iterations),
  - demo-output/website/tmr/runs/bump-*/log.simpleFoam (all three, to their published caps).
Fine has no re-run history here, so the matched table stops at its published 9,000.

Usage:  python3 drag_split.py     (from anywhere)
"""
import gzip
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
PUB = os.path.join(REPO, "demo-output", "website", "tmr", "runs")
LEVELS = ("coarse", "medium", "fine")
COMPONENTS = (("TOTAL", 0), ("PRESSURE", 1), ("VISCOUS", 2))


def from_log(path):
    """Cd total/pressure/viscous per iteration, from simpleFoam's forceCoeffs block."""
    out, iteration = {}, 0
    with open(path, errors="replace") as handle:
        for line in handle:
            if line.startswith("Time = "):
                iteration = int(line.split("=")[1])
            found = re.match(
                r"\s*Cd:\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)", line)
            if found:
                out[iteration] = tuple(float(g) for g in found.groups())
    return out


def from_table(path):
    out = {}
    with gzip.open(path, "rt") as handle:
        for line in handle:
            if line.startswith("#"):
                continue
            parts = line.split()
            out[int(parts[0])] = tuple(float(x) for x in parts[1:4])
    return out


def history(level):
    merged = {}
    published = os.path.join(PUB, f"bump-{level}", "log.simpleFoam")
    if os.path.exists(published):
        merged.update(from_log(published))
    rerun = os.path.join(HERE, level, "drag_split.dat.gz")
    if os.path.exists(rerun):
        merged.update(from_table(rerun))
    return merged


def order(values):
    """Observed order on a factor-2 triple, or None when the increments change sign."""
    d21, d32 = values[1] - values[0], values[2] - values[1]
    if d21 * d32 <= 0:
        return None, d21, d32
    return math.log(d21 / d32) / math.log(2.0), d21, d32


def show(name, values):
    p, d21, d32 = order(values)
    verdict = f"p = {p:7.4f}" if p is not None else "NON-MONOTONE: increments cross"
    return (f"{name} " + " ".join(f"{v:.6e}" for v in values)
            + f"   increments {d21:+.3e} {d32:+.3e}   {verdict}")


def main():
    runs = {level: history(level) for level in LEVELS}
    print("Cd histories available to iteration:",
          {level: max(runs[level]) for level in LEVELS})
    for name, index in COMPONENTS:
        print(f"\n{name} drag at matched iteration counts")
        for n in (3000, 4000, 5000, 6000, 7000, 8000, 9000):
            if all(n in runs[level] for level in LEVELS):
                print("   " + show(f"n = {n:5d} ",
                                   [runs[level][n][index] for level in LEVELS]))
    print("\nAS PUBLISHED, unmatched caps 4000/6000/9000")
    for name, index in COMPONENTS:
        print("   " + show(f"{name:9s}",
                           [runs["coarse"][4000][index], runs["medium"][6000][index],
                            runs["fine"][9000][index]]))


if __name__ == "__main__":
    main()
