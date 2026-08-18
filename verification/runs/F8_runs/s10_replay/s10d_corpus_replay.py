#!/usr/bin/env python3
"""Replay line for the PROPOSED S10d magnitude-explosion branch.

Rule as proposed (see proposal `s10d-monitored-quantity-magnitude-explosion`
and ZERO_COMPUTE_DIAGNOSTICS_2026-08-08.md task 3): over a monitored-quantity
history with the first 10% of samples excluded as startup, let m be the median
|q| of the first half of the remainder and q_end = |last sample|. FATAL when
q_end >= 1e6 * m AND the last 5 magnitude steps are all increasing.

Corpus per Monitor Standard standing rule 6: every coefficient.dat under
demo-output (the S12 corpus root) -- Cd and Cl columns -- PLUS every
forces-object moment.dat/force.dat x-column under demo-output, because the rail
gap this branch closes is exactly that those histories are outside the corpus.
Zero compute: file reading only. Writes s10d_corpus_replay.json.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

# NOT `parents[5]`, and this is a defect class rather than a typo: a
# repository root derived by COUNTING segments up from a path under a
# MOVING tree points somewhere else the moment the tree moves.  MOVE_MAP
# batch 7 made this file ONE SEGMENT SHALLOWER, so `parents[5]` went from
# the repository root to `/home/ubuntu`.  There is no path literal in the
# expression, so no prefix rewrite and no grep for `demo-output` reaches it
# -- the same class cost `sdk/tests/test_a2_shape.py:28` a green comparison
# over ten synthetic bodies at batch 6.  DERIVED BY SEARCHING for the
# marker, so the answer no longer depends on this file's depth.
REPO = next((_p for _p in Path(__file__).resolve().parents
            if (_p / "scripts" / "lab_paths.py").is_file()), None)
if REPO is None:
    raise RuntimeError(
        "cannot locate scripts/lab_paths.py above %s; refusing to "
        "guess a repository root" % __file__)
ROOT = REPO / "demo-output"

ORDERS_RATIO = 1.0e6
TAIL_STEPS = 5


def fires(series: list[float]) -> dict | None:
    n = len(series)
    if n < 20:
        return None
    body = [abs(v) for v in series[max(1, n // 10):]]
    half = body[: len(body) // 2]
    m = statistics.median(half)
    q_end = body[-1]
    if m <= 0.0 or q_end < ORDERS_RATIO * m:
        return None
    tail = body[-(TAIL_STEPS + 1):]
    if not all(b > a for a, b in zip(tail, tail[1:])):
        return None
    import math
    return {"orders": round(math.log10(q_end / m), 1), "median_ref": m,
            "final": q_end}


def columns(path: Path, wanted: list[int]) -> list[list[float]]:
    out: list[list[float]] = [[] for _ in wanted]
    for line in path.read_text(errors="replace").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        try:
            for i, col in enumerate(wanted):
                out[i].append(float(parts[col]))
        except (ValueError, IndexError):
            continue
    return out


def main() -> None:
    results = {"corpus": {"coefficient_histories": 0, "forces_histories": 0},
               "fires": []}
    # coefficient.dat: columns per OpenFOAM forceCoeffs; grade Cd, Cl by
    # header lookup, falling back to columns 1 and 4.
    for dat in sorted(ROOT.rglob("coefficient.dat")):
        header = [ln for ln in dat.read_text(errors="replace").splitlines()
                  if ln.startswith("#")]
        names = header[-1].lstrip("#").split() if header else []
        idx = []
        for want in ("Cd", "Cl"):
            idx.append(names.index(want) if want in names else
                       {"Cd": 1, "Cl": 4}[want])
        for name, series in zip(("Cd", "Cl"), columns(dat, idx)):
            results["corpus"]["coefficient_histories"] += 1
            f = fires(series)
            if f:
                results["fires"].append(
                    {"file": str(dat.relative_to(REPO)), "quantity": name,
                     **f})
    # forces-object histories: total_x is column 1 in both files.
    for pat in ("moment.dat", "force.dat"):
        for dat in sorted(ROOT.rglob(pat)):
            if "bladeForces" not in str(dat) and "forces" not in str(dat):
                continue
            (series,) = columns(dat, [1]) or ([],)
            results["corpus"]["forces_histories"] += 1
            f = fires(series)
            if f:
                results["fires"].append(
                    {"file": str(dat.relative_to(REPO)),
                     "quantity": f"{pat}:total_x", **f})
    results["fire_count"] = len(results["fires"])
    out = Path(__file__).parent / "s10d_corpus_replay.json"
    out.write_text(json.dumps(results, indent=1))
    print(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
