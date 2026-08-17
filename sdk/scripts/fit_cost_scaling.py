#!/usr/bin/env python3
"""Fit a cost scaling law per solver family from the mega-batch ledger.

WHY. Every proposal on the docket carries a predicted cost and, until this
file, nothing fitted one from the lab's own history. The audit's
`check_cost_predictions` grades predictions that somebody wrote down; it has
three pairs across one family and no family has met the within-20-percent
three-times bar. This fits the laws those predictions should have come from.

WHAT A COST IS HERE, and this is the part the docket keeps getting wrong.

  **A cost without a rank count is not a cost.** Core-minutes are wall seconds
  times MPI ranks over sixty, so a wall-time law is only a cost law once the
  ranks are stated. Every row in this ledger is serial: the mega-batch runner
  invokes solvers through `tmr_verification._foam`, which runs
  `[*_run_prefix(), *args]` with no `mpirun` and no `-parallel`, and the two
  non-OpenFOAM families are single-process by construction. So ranks = 1 on
  every row and core-minutes = wall_seconds / 60 throughout. That equality is
  a property of THIS ledger and does not transfer to a decomposed run.

TWO LAWS PER FAMILY, and they answer different questions.

  * **A priori.** Wall time as a power law in the design parameters alone, the
    quantities a proposal knows before anything runs. This is the only law that
    can price an unstarted item.
  * **A posteriori.** Wall time as a power law in the run's own size, cells and
    iterations where the family records them. This one explains cost and cannot
    forecast it, because it needs the run. It is fitted anyway, because the gap
    between the two is the measurement of how much of a family's cost is
    unknowable in advance, and that gap is exactly what the flat-plate rung
    overran on: its cells were priced correctly and its iterations were not.

CLEANING, stated rather than assumed. Rows are dropped for three reasons and
each count is reported: a torn line that does not parse, a row the runner
recorded as not ok, and a row above the audit's stall threshold of 3600 s.
The stall rows are host stalls recorded as normal runs, and a law fitted
through them inherits the stall.

THE FIT. Ordinary least squares on logs, so `wall = C * prod(x_i ^ b_i)`.
Reported per family: n, the exponents, R2, the median and 90th percentile of
the absolute relative residual, and whether the family clears the bar the
compute charter sets, three consecutive predictions within 20 percent. The bar
is applied to a held-out tail rather than to the fitted points, because a fit
graded on its own training data grades the fit and not the forecast.

NO COMPUTE. Reads one ledger.

  python3 sdk/scripts/fit_cost_scaling.py [--out PATH]
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
from pathlib import Path

# The one module that names this repository's tree (MOVE_MAP batch 3).
# Every name it exports is bound to a legacy/successor PAIR resolved
# against the filesystem at import, so the constants below are correct
# before the move, between batches and after it, with no edit here.
import sys as _sys  # noqa: E402
import pathlib as _pathlib  # noqa: E402
_LAB_PATHS_DIR = str(_pathlib.Path(__file__).resolve().parents[2]
                     / "scripts")
if _LAB_PATHS_DIR not in _sys.path:
    _sys.path.insert(0, _LAB_PATHS_DIR)
import lab_paths  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
LEDGER = lab_paths.MEGA_BATCH / "ledger.jsonl"

# The audit's own threshold (scripts/self_audit.py STALL_SECONDS), so the two
# readings of this ledger clean it the same way.
STALL_SECONDS = 3600.0

# Held-out fraction, taken from the tail in ledger order so the holdout is
# later work rather than a random slice of the same afternoon.
HOLDOUT_FRACTION = 0.2
HOLDOUT_MIN = 20

# What each family knows BEFORE it runs (design) and what it only knows after
# (size). Anything not listed is not a cost driver in that family: a target
# lift coefficient does not set a solve's length, and including it would fit
# noise with a plausible exponent.
FAMILIES: dict[str, dict[str, list[str]]] = {
    "openfoam-cylinder": {
        "design": ["cylinder_diameter", "inlet_velocity",
                   "kinematic_viscosity", "mesh_refinement"],
        "size": ["cell_count", "solver_iterations"],
    },
    "openfoam-cylinder-unsteady": {
        "design": ["reynolds"],
        "size": ["cells", "steps"],
    },
    "rhosimplefoam-naca0012-transonic": {
        "design": ["mach", "alpha_deg", "reynolds"],
        "size": ["cells", "iterations_actual"],
    },
    "simplefoam-ahmed-3d-viscous": {
        "design": ["slant_deg", "reynolds"],
        "size": ["cells", "solver_iterations"],
    },
    "vspaero-wing": {
        "design": ["span", "area", "sweep", "taper"],
        "size": [],
    },
    "reduced-order": {
        "design": ["opening_angle_deg"],
        "size": ["phase_points"],
    },
}

WITHIN = 0.20        # the charter's 20 percent
RUN_NEEDED = 3       # three consecutive

# THE HOLE IN THIS BAR, recorded 2026-08-01 and deliberately NOT patched here:
# the threshold and the streak logic are left exactly as the charter set them.
# A relative-error streak gate is a test of the family's variance, not of the
# law's skill. Both quantities it compares are divided by the same measured
# wall time, so on a family whose cost is nearly constant the gate is cleared
# by any predictor that lands near that constant, including one that carries no
# explanatory power at all -- and it is then cleared indefinitely, because every
# further row of the same tight family is another hit. Streak length therefore
# grows with the size of the holdout, not with the quality of the law. The
# demonstrated instance is `vspaero-wing`, re-fitted from
# demo-output/website/mega-batch/ledger.jsonl by this script and recorded in
# demo-output/website/mega-batch/cost_scaling.json: holdout_longest_run_
# within_20pct = 6457 with r2_log_space = 0.0002 and skill_vs_null = -43.9273,
# i.e. the fitted law's median holdout error (0.0602) is about 45x the error of
# simply predicting the family's training median (0.0013), and the constant
# predictor scores the identical 6,457-long run (null_longest_run_within_20pct
# = 6457). The four exponents are 0.003, -0.0003, 0.0011 and 0.0004 on a family
# whose wall time runs 5.23 s median against a 5.51 s mean, so the "law" is a
# constant in disguise and the bar cannot see the difference. RECOMMENDATION
# ONLY, for whoever owns the charter: auto-approval should require the streak
# AND `beats_the_null_model` on the same holdout (the constant-predictor
# comparison this script already computes below), because a gate that a
# constant passes is not evidence that a law was learned.


def _num(value) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def _ols(rows: list[tuple[list[float], float]]) -> dict | None:
    """Least squares for y = a0 + sum a_i x_i, by normal equations.

    Small, dense and well conditioned after the log transform; a dependency on
    numpy would buy nothing here and this file has to run anywhere the ledger
    does.
    """
    if not rows:
        return None
    width = len(rows[0][0]) + 1
    if len(rows) <= width:
        return None
    ata = [[0.0] * width for _ in range(width)]
    atb = [0.0] * width
    for xs, y in rows:
        vector = [1.0, *xs]
        for i in range(width):
            atb[i] += vector[i] * y
            for j in range(width):
                ata[i][j] += vector[i] * vector[j]
    # Gaussian elimination with partial pivoting.
    matrix = [row[:] + [atb[i]] for i, row in enumerate(ata)]
    for col in range(width):
        pivot = max(range(col, width), key=lambda r: abs(matrix[r][col]))
        if abs(matrix[pivot][col]) < 1e-12:
            return None
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        for r in range(width):
            if r == col:
                continue
            factor = matrix[r][col] / matrix[col][col]
            for c in range(col, width + 1):
                matrix[r][c] -= factor * matrix[col][c]
    coeffs = [matrix[i][width] / matrix[i][i] for i in range(width)]
    mean_y = statistics.fmean(y for _, y in rows)
    ss_tot = sum((y - mean_y) ** 2 for _, y in rows)
    ss_res = 0.0
    for xs, y in rows:
        pred = coeffs[0] + sum(c * x for c, x in zip(coeffs[1:], xs))
        ss_res += (y - pred) ** 2
    return {"coeffs": coeffs,
            "r2": (1.0 - ss_res / ss_tot) if ss_tot > 0 else None}


def _predict(fit: dict, xs: list[float]) -> float:
    coeffs = fit["coeffs"]
    return math.exp(coeffs[0] + sum(c * x for c, x in zip(coeffs[1:], xs)))


def _longest_run(hits: list[bool]) -> int:
    best = current = 0
    for hit in hits:
        current = current + 1 if hit else 0
        best = max(best, current)
    return best


def fit_family(name: str, rows: list[dict], predictors: list[str],
               kind: str) -> dict:
    """One power-law fit, trained on the head and graded on the tail."""
    samples = []
    for row in rows:
        pool = {**(row.get("design") or {}), **(row.get("metrics") or {})}
        values = [_num(pool.get(key)) for key in predictors]
        wall = _num(row.get("wall_seconds"))
        if wall is None or wall <= 0 or any(
                v is None or v <= 0 for v in values):
            continue
        samples.append(([math.log(v) for v in values], math.log(wall), wall))
    result = {"kind": kind, "predictors": list(predictors),
              "usable_rows": len(samples)}
    if len(samples) <= len(predictors) + 1:
        result["fit"] = None
        result["why"] = ("not enough rows carry every predictor as a positive "
                         "number")
        return result
    holdout = max(HOLDOUT_MIN, int(len(samples) * HOLDOUT_FRACTION))
    holdout = min(holdout, len(samples) // 2)
    train = samples[:len(samples) - holdout]
    test = samples[len(samples) - holdout:]
    fit = _ols([(xs, y) for xs, y, _ in train])
    if fit is None:
        result["fit"] = None
        result["why"] = "the design matrix is singular on this family"
        return result
    # THE NULL MODEL, and it is the reason this file does not stop at the bar.
    # "Three consecutive predictions within 20 percent" is passed by any law
    # applied to a family whose cost barely varies, because predicting the
    # family's own median is already within 20 percent of almost every row.
    # The bar measures the spread of the family, not the skill of the law. So
    # every fit is graded against the constant predictor on the same holdout,
    # and a law that does not beat it is reported as not beating it.
    null = statistics.median(wall for _, _, wall in train)
    errors = []
    hits = []
    null_errors = []
    null_hits = []
    for xs, _, wall in test:
        pred = _predict(fit, xs)
        rel = abs(pred - wall) / wall
        errors.append(rel)
        hits.append(rel <= WITHIN)
        null_rel = abs(null - wall) / wall
        null_errors.append(null_rel)
        null_hits.append(null_rel <= WITHIN)
    null_median = statistics.median(null_errors)
    law_median = statistics.median(errors)
    result.update({
        "null_model_median_wall_s": round(null, 4),
        "null_median_abs_rel_error": round(null_median, 4),
        "null_within_20pct": sum(null_hits),
        "null_longest_run_within_20pct": _longest_run(null_hits),
        "skill_vs_null": (round(1.0 - law_median / null_median, 4)
                          if null_median > 0 else None),
        "beats_the_null_model": law_median < null_median,
    })
    result.update({
        "n_train": len(train),
        "n_test": len(test),
        "constant": round(math.exp(fit["coeffs"][0]), 6),
        "exponents": {key: round(coeff, 4) for key, coeff
                      in zip(predictors, fit["coeffs"][1:])},
        "r2_log_space": round(fit["r2"], 4) if fit["r2"] is not None else None,
        "holdout_median_abs_rel_error": round(statistics.median(errors), 4),
        "holdout_p90_abs_rel_error": round(
            sorted(errors)[int(0.9 * (len(errors) - 1))], 4),
        "holdout_within_20pct": sum(hits),
        "holdout_longest_run_within_20pct": _longest_run(hits),
        "clears_three_consecutive_bar": _longest_run(hits) >= RUN_NEEDED,
    })
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", default=str(LEDGER))
    parser.add_argument("--out", default=str(
        lab_paths.MEGA_BATCH / "cost_scaling.json"))
    args = parser.parse_args()

    torn = not_ok = stalled = 0
    by_family: dict[str, list[dict]] = {}
    with open(args.ledger, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                torn += 1
                continue
            if not row.get("ok"):
                not_ok += 1
                continue
            wall = _num(row.get("wall_seconds"))
            if wall is not None and wall > STALL_SECONDS:
                stalled += 1
                continue
            by_family.setdefault(str(row.get("solver")), []).append(row)

    report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "ledger": str(Path(args.ledger).relative_to(REPO)),
        "ranks_per_row": 1,
        "ranks_evidence": (
            "the mega-batch runner invokes every OpenFOAM family through "
            "workflows/tmr_verification._foam, which runs [*_run_prefix(), "
            "*args] with no mpirun and no -parallel; the wing and "
            "reduced-order families are single-process by construction. "
            "core-minutes = wall_seconds / 60 on this ledger only."),
        "cleaning": {"torn_lines": torn, "rows_not_ok": not_ok,
                     "rows_above_stall_threshold": stalled,
                     "stall_threshold_s": STALL_SECONDS},
        "families": {},
    }
    for family, spec in FAMILIES.items():
        rows = by_family.get(family, [])
        walls = [w for w in (_num(r.get("wall_seconds")) for r in rows)
                 if w is not None]
        entry = {
            "clean_rows": len(rows),
            "wall_seconds": {
                "median": round(statistics.median(walls), 3) if walls else None,
                "mean": round(statistics.fmean(walls), 3) if walls else None,
                "max": round(max(walls), 3) if walls else None,
            },
            "core_minutes_median": (round(statistics.median(walls) / 60.0, 4)
                                    if walls else None),
            "a_priori": fit_family(family, rows, spec["design"], "a priori"),
        }
        if spec["size"]:
            entry["a_posteriori"] = fit_family(family, rows, spec["size"],
                                               "a posteriori")
        report["families"][family] = entry

    clears = [name for name, entry in report["families"].items()
              if (entry["a_priori"].get("clears_three_consecutive_bar"))]
    useful = [name for name, entry in report["families"].items()
              if entry["a_priori"].get("clears_three_consecutive_bar")
              and entry["a_priori"].get("beats_the_null_model")]
    report["families_clearing_the_bar_a_priori"] = sorted(clears)
    report["families_whose_law_also_beats_predicting_the_median"] = sorted(useful)
    report["what_the_bar_does_not_test"] = (
        "clearing three consecutive predictions within 20 percent says nothing "
        "on its own about a family whose cost barely varies: predicting that "
        "family's median clears the same bar. Each fit is therefore graded "
        "against the constant predictor on the same holdout, and the second "
        "list above is the one that means a law was learned.")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    print(f"\nwrote {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
