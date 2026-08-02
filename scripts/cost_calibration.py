#!/usr/bin/env python3
"""Estimate against measured, for every completed item that recorded both.

    python3 scripts/cost_calibration.py            # human-readable
    python3 scripts/cost_calibration.py --json     # machine-readable

WHY THIS EXISTS. The lab prices compute with a 3x planning multiplier that its
own forecast calls "explicitly a guess from two calibration points". Two points
are not a distribution. Meanwhile `scripts/self_audit.py` carried a
measured-versus-predicted table of three pairs typed into the audit file as
constants -- it read nothing on disk, so it could not fail on a wrong pair, and
it had no way to notice that completed items on the docket were recording their
own measured cost in prose that nothing parsed.

WHAT THIS READS. `measured_core_min` on a completed docket item, and nothing
else. Every one of those fields carries a `measured_basis` quoting the sentence
in that item's own outcome the figure was read from, so a reader can check any
row against the record in one step. An item that finished without a readable
cost carries `measured_core_min_unstated` naming why, so the gap is on the
report rather than being the absence of a row.

WHAT IT FOUND, and it is not a better multiplier. A multiplier assumes the
error has one scale. It does not. Run this for the current numbers; the shape
at first measurement, over 15 pairs, was that a cost basis naming a prior
measurement had never over-run by more than 1.05x, and every over-run on record
-- 1.48x, 9.79x and 13.55x -- came from a basis whose first word was
"estimate". The predictor is the basis, not a factor.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import statistics
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DOCKET = REPO / "demo-output" / "website" / "agenda" / "docket.json"

# The lab's own convention: a cost_basis states its kind in its first word.
# "measured" means a figure taken off a run that happened; anything else is a
# forecast, however much reasoning follows it.
_MEASURED_BASIS = re.compile(r"^\s*measured\b", re.I)
# The forecast's standing planning multiplier, which this file exists to test.
PLANNING_MULTIPLIER = 3.0
# The auto-approve bar the audit grades forecast skill by.
WITHIN = 0.20


def _rows() -> tuple[list[dict], list[dict]]:
    data = json.loads(DOCKET.read_text(encoding="utf-8"))
    proposals = data.get("proposals") if isinstance(data, dict) else data
    pairs, gaps = [], []
    for proposal in proposals or []:
        if not isinstance(proposal, dict) or proposal.get("status") != "done":
            continue
        try:
            estimate = float(proposal.get("est_core_min") or 0.0)
        except (TypeError, ValueError):
            continue
        if estimate <= 0:
            continue          # a zero-estimate item makes no ratio
        measured = proposal.get("measured_core_min")
        if measured is None:
            gaps.append({"id": proposal.get("id"), "est_core_min": estimate,
                         "why": proposal.get("measured_core_min_unstated")
                         or "no measured cost recorded and no reason given"})
            continue
        measured = float(measured)
        basis = str(proposal.get("cost_basis") or "")
        pairs.append({
            "id": proposal.get("id"),
            "est_core_min": estimate,
            "measured_core_min": measured,
            "ratio": measured / estimate,
            "basis_kind": "measured" if _MEASURED_BASIS.search(basis)
                          else "forecast",
            "cost_basis": basis,
            "measured_basis": proposal.get("measured_basis"),
        })
    pairs.sort(key=lambda r: -r["est_core_min"])
    return pairs, gaps


def analyse() -> dict:
    pairs, gaps = _rows()
    if not pairs:
        return {"pairs": [], "gaps": gaps, "n": 0}
    ratios = [r["ratio"] for r in pairs]
    positive = [r for r in ratios if r > 0]

    def cut(rows):
        if not rows:
            return None
        rs = [r["ratio"] for r in rows]
        pos = [r for r in rs if r > 0]
        return {
            "n": len(rows),
            "worst_overrun": round(max(rs), 3),
            "worst_underspend": round(min(rs), 3),
            "median_ratio": round(statistics.median(rs), 3),
            "geometric_mean_of_nonzero": (
                round(math.exp(sum(math.log(r) for r in pos) / len(pos)), 3)
                if pos else None),
            "inside_the_3x_band": sum(1 for r in rs
                                      if 1 / PLANNING_MULTIPLIER <= r
                                      <= PLANNING_MULTIPLIER),
            "within_20_percent": sum(1 for r in rs
                                     if 1 - WITHIN <= r <= 1 + WITHIN),
            "needed_no_solver_at_all": sum(1 for r in rs if r == 0),
        }

    measured = [r for r in pairs if r["basis_kind"] == "measured"]
    forecast = [r for r in pairs if r["basis_kind"] == "forecast"]
    return {
        "n": len(pairs),
        "pairs": pairs,
        "gaps": gaps,
        "est_total": round(sum(r["est_core_min"] for r in pairs), 1),
        "measured_total": round(sum(r["measured_core_min"] for r in pairs), 1),
        "aggregate_ratio": round(sum(r["measured_core_min"] for r in pairs)
                                 / sum(r["est_core_min"] for r in pairs), 3),
        "all": cut(pairs),
        "basis_names_a_measurement": cut(measured),
        "basis_is_a_forecast": cut(forecast),
        "overruns": sorted(
            ({"id": r["id"], "ratio": round(r["ratio"], 2),
              "basis_kind": r["basis_kind"]}
             for r in pairs if r["ratio"] > 1.0),
            key=lambda r: -r["ratio"]),
        "priced_for_a_solver_that_never_ran": [
            {"id": r["id"], "est_core_min": r["est_core_min"]}
            for r in pairs if r["measured_core_min"] == 0],
    }


def report(state: dict) -> None:
    print("Cost calibration: estimate against measured")
    print("=" * 92)
    if not state["n"]:
        print("no completed item records both an estimate and a measured cost")
        return
    print(f"{'ratio':>7}  {'est':>8}  {'measured':>10}  basis   item")
    print("-" * 92)
    for row in state["pairs"]:
        print(f"{row['ratio']:7.3f}  {row['est_core_min']:8.1f}  "
              f"{row['measured_core_min']:10.3f}  "
              f"{row['basis_kind'][:8]:8s} {row['id']}")
    print("-" * 92)
    print(f"{state['n']} pairs; {state['est_total']:g} core-min estimated, "
          f"{state['measured_total']:g} measured, aggregate ratio "
          f"{state['aggregate_ratio']}")
    print()
    print("THE MULTIPLIER IS THE WRONG INSTRUMENT")
    whole = state["all"]
    print(f"  a 3x planning multiplier brackets "
          f"{whole['inside_the_3x_band']} of {whole['n']} pairs; "
          f"{whole['within_20_percent']} land within 20 percent")
    print(f"  median ratio {whole['median_ratio']}, so the typical item costs "
          f"a fraction of its estimate, while the worst over-runs at "
          f"{whole['worst_overrun']}x")
    print(f"  {whole['needed_no_solver_at_all']} of {whole['n']} items spent "
          f"EXACTLY ZERO: the work turned out to need no solver. Multiplying a "
          f"wrong-category estimate by three makes it worse, not safer")
    for row in state["priced_for_a_solver_that_never_ran"]:
        print(f"      {row['id']}: {row['est_core_min']:g} core-min priced, "
              f"none spent")
    print()
    print("WHAT DOES PREDICT: THE BASIS, NOT A FACTOR")
    for label, key in (("cost_basis begins 'measured'",
                        "basis_names_a_measurement"),
                       ("cost_basis is a forecast", "basis_is_a_forecast")):
        cut = state[key]
        if not cut:
            continue
        print(f"  {label}: {cut['n']} pair(s), worst over-run "
              f"{cut['worst_overrun']}x, median {cut['median_ratio']}, "
              f"{cut['inside_the_3x_band']} inside the 3x band")
    print("  every over-run on record, by basis kind:")
    for row in state["overruns"]:
        print(f"      {row['ratio']}x  {row['basis_kind']:8s} {row['id']}")
    print()
    print("  CAVEAT, and it is not small. The measured-basis sample is small, "
          "and an item that could be priced from a measurement may be one the "
          "lab already understood, so the basis may be a proxy for that "
          "understanding rather than a cause of the accuracy.")
    print()
    print(f"COMPLETED ITEMS WITH AN ESTIMATE AND NO READABLE MEASURED COST: "
          f"{len(state['gaps'])}")
    for row in state["gaps"]:
        print(f"  {row['id']} ({row['est_core_min']:g} core-min): {row['why']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    state = analyse()
    if args.json:
        print(json.dumps(state, indent=1))
    else:
        report(state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
