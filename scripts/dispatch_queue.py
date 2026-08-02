#!/usr/bin/env python3
"""The step between an approved item and a machine with nothing to do.

    python3 scripts/dispatch_queue.py            # human-readable
    python3 scripts/dispatch_queue.py --json     # machine-readable
    python3 scripts/dispatch_queue.py --quiet    # the head of the queue only

WHY THIS EXISTS, measured rather than supposed. The duty cycle of this lab's
own mega-batch ledger decomposes exactly: a 1.583 gross mean is 3.02 cores
while busy multiplied by a 52.5 percent duty cycle, and 47.5 percent of
one-minute bins hold no work at all. A burst on 2026-08-01 sustained 11.06
cores for 1.77 hours, so the box is not slow. The docket has held eighty-plus
approved items throughout. The lab therefore lacks neither work nor capacity;
it lacks the step between them. Approval and dispatch are separate acts and
the second only happens when a person or an agent notices.

WHAT THIS DOES AND DOES NOT DO. It does not launch anything. It answers, from
the records, the one question nobody had written down: *if something were going
to start work right now, what would it start, and what is stopping everything
else?* Every item that is not at the head of the queue is named with the single
reason it is not, so "nothing is running" stops being one undifferentiated fact
and becomes a list somebody can shorten.

WHY IT DOES NOT LAUNCH, and what has to exist first. A queue that starts its
own work needs a ceiling before it has one, and the case is measured: the
largest overrun on record is 1,175.0 core-minutes against a 120 core-minute
estimate, 9.8 times under, and **the item was at `proposed` the whole time and
was never approved**. A spend gate that fires at approval cannot see that run at
all, because no approval was ever sought. So the ceiling has to bind at LAUNCH.

It cannot bind at launch today, and this report measures why rather than
asserting it. `scripts/launch_solve.sh` is the one sanctioned launcher, and its
completion records carry `job`, `pid`, `started`, `finished`, `case` and a
convergence verdict. They do not carry which docket item the run belongs to,
and they do not carry a rank count. Core-minutes are wall seconds times ranks
over sixty (COMPUTE_BUDGET_CHARTER section 2), so with no rank count the unit
the ceiling is denominated in is not derivable from the launch record, and with
no item the spend cannot be attributed to the thing that was approved. Both
gaps are counted below from the registry itself.

The ceilings named here are the charter's proposed numbers and they are NOT
ratified. This file says so on every line that uses one, and the gate is
advisory: it reports what it would refuse. Turning that into a refusal is
Katie's decision, not this script's.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DOCKET = REPO / "demo-output" / "website" / "agenda" / "docket.json"
REGISTRY = REPO / "demo-output" / "website" / "solve_registry"
CHARTER = REPO / "docs" / "charters" / "COMPUTE_BUDGET_CHARTER.md"

# The charter's proposed standing ceilings, in core-minutes, in ONE place.
# THEY ARE NOT RATIFIED. `COMPUTE_BUDGET_CHARTER.md` proposes them and no
# ruling has adopted them, so `CEILINGS_RATIFIED` is False and every gate below
# reports rather than refuses. A ceiling nobody agreed to is not a ceiling, and
# a script that enforced one would be legislating.
CEILINGS_RATIFIED = False
PER_ITEM_CORE_MIN = 240.0
PER_DAY_CORE_MIN = 480.0
# The charter's own smallest tier, the one an item can spend without a specific
# conversation about that item.
STANDING_CORE_MIN = 60.0

# Cores the machine keeps for itself, matching `chief_engineer.compute_audit`.
RESERVED_CORES = 2

# A cost basis that says only this is a guess. Measured on the docket
# 2026-08-01: 48 of the 67 approved compute items, carrying 8,433 of the 9,929
# approved core-minutes, price themselves this way. A dispatcher that spent on
# those numbers would be spending on nothing.
_BARE_ESTIMATE = re.compile(r"^\s*estimate\b[\s;,.]*$", re.I)
# Reused deliberately from `scripts/self_audit.py`, which counts the same gap
# weekly: a refinement rung priced by its cells alone is priced by half.
_RUNG_SHAPED = re.compile(
    r"\brung\b|\bladder\b|refinement|grid[\s-]convergence|finest grid", re.I)
_ITERATION_TERM = re.compile(
    r"\biterat|\bsteps?\b|\bsweeps?\b|endTime|time step", re.I)


def _load_docket() -> list[dict]:
    data = json.loads(DOCKET.read_text(encoding="utf-8"))
    proposals = data.get("proposals") if isinstance(data, dict) else data
    return [p for p in (proposals or []) if isinstance(p, dict)]


def _est(proposal: dict) -> float:
    try:
        return float(proposal.get("est_core_min") or 0.0)
    except (TypeError, ValueError):
        return 0.0


def registry_attribution() -> dict:
    """What the launch records can and cannot say about spend.

    A ceiling that binds at launch has to answer two questions about the run
    being launched: which approved item is it, and how many core-minutes will
    it cost. Neither is in the record today, and this counts by how much.
    """
    records = sorted(REGISTRY.glob("*.done")) if REGISTRY.is_dir() else []
    # A field printed as UNATTRIBUTED or UNSTATED is a recorded absence, which
    # is better than a silent one and is still not an attribution. Both are
    # counted, separately, because the two say different things: how many runs
    # went through a launcher that asks, and how many were actually answered.
    field = re.compile(r"^\s*(item|ranks)\s*:\s*(\S+)", re.I | re.M)
    asked = {"item": 0, "ranks": 0}
    answered = {"item": 0, "ranks": 0}
    timed = 0
    for record in records:
        head = record.read_text(encoding="utf-8", errors="replace") \
            .split("--- last")[0]
        for name, value in field.findall(head):
            key = name.lower()
            asked[key] += 1
            if value.upper() not in ("UNATTRIBUTED", "UNSTATED", "NONE", ""):
                answered[key] += 1
        if "started:" in head and "finished:" in head:
            timed += 1
    return {
        "records": len(records),
        "naming_a_docket_item": answered["item"],
        "asked_for_an_item": asked["item"],
        "stating_a_rank_count": answered["ranks"],
        "asked_for_a_rank_count": asked["ranks"],
        "carrying_start_and_finish": timed,
        "core_minutes_derivable": answered["ranks"],
        "spend_attributable_to_an_item": answered["item"],
    }


def machine() -> dict:
    """What the box is doing, read now."""
    cores = os.cpu_count() or 0
    try:
        one, five, fifteen = os.getloadavg()
    except OSError:
        one = five = fifteen = float("nan")
    usable = max(0, cores - RESERVED_CORES)
    return {"cores": cores, "reserved": RESERVED_CORES, "usable": usable,
            "load_1min": round(one, 2), "load_5min": round(five, 2),
            "load_15min": round(fifteen, 2),
            "idle_cores": round(max(0.0, usable - one), 2)}


# Why an item is not at the head of the queue. Ordered: the FIRST reason that
# applies is the one reported, so every item carries exactly one, and the
# counts below add up to the docket. An item reported under a late reason has
# already cleared every earlier one.
def _blocking_reason(proposal: dict) -> tuple[str, str] | None:
    status = proposal.get("status")
    est = _est(proposal)
    basis = str(proposal.get("cost_basis") or "")
    text = f"{proposal.get('objective', '')} {proposal.get('rationale', '')}"

    if status in ("done", "dismissed"):
        return ("closed", f"status is {status}")
    if status != "approved":
        return ("not approved",
                f"status is {status!r}; approval and dispatch are separate "
                f"acts and this one has not had the first")
    if est <= 0:
        return ("no solver needed",
                "zero estimated core-minutes; this is desk work and a compute "
                "queue is not what is holding it")
    if not basis:
        return ("no cost basis",
                f"{est:g} core-min with no cost_basis at all; charter 1 "
                f"disqualifies a proposal with no cost")
    if _BARE_ESTIMATE.search(basis):
        return ("priced by guess",
                f"{est:g} core-min whose cost_basis is the bare word "
                f"'estimate'; a dispatcher spending on that is spending on a "
                f"number nobody measured")
    if _RUNG_SHAPED.search(text) and not _ITERATION_TERM.search(basis):
        return ("rung priced by its grid alone",
                f"{est:g} core-min on a rung-shaped item whose basis names no "
                f"iteration count; the flat plate's finest rung came in at "
                f"1.48x and the whole overrun was settling")
    if est > PER_ITEM_CORE_MIN:
        return ("over the per-item ceiling",
                f"{est:g} core-min against a proposed and unratified per-item "
                f"ceiling of {PER_ITEM_CORE_MIN:g}")
    return None


def queue() -> dict:
    proposals = _load_docket()
    launchable, blocked = [], {}
    for proposal in proposals:
        reason = _blocking_reason(proposal)
        if reason is None:
            launchable.append(proposal)
        else:
            blocked.setdefault(reason[0], []).append((proposal, reason[1]))
    # Cheapest first. A queue that has never drained wants its shortest
    # measurable result first, not its most ambitious one: the head of the
    # queue is the thing that proves the loop closes.
    launchable.sort(key=lambda p: (_est(p), str(p.get("id"))))

    approved = [p for p in proposals if p.get("status") == "approved"]
    compute = [p for p in approved if _est(p) > 0]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(
            timespec="seconds"),
        "docket": str(DOCKET.relative_to(REPO)),
        "proposals": len(proposals),
        "approved": len(approved),
        "approved_needing_a_solver": len(compute),
        "approved_core_min": round(sum(_est(p) for p in compute), 1),
        "launchable": [
            {"id": p.get("id"), "est_core_min": _est(p),
             "cost_basis": p.get("cost_basis"),
             "objective": p.get("objective")}
            for p in launchable],
        "launchable_core_min": round(sum(_est(p) for p in launchable), 1),
        "blocked": {reason: [{"id": p.get("id"), "est_core_min": _est(p),
                              "why": why} for p, why in rows]
                    for reason, rows in blocked.items()},
        "ceilings": {"ratified": CEILINGS_RATIFIED,
                     "per_item_core_min": PER_ITEM_CORE_MIN,
                     "per_day_core_min": PER_DAY_CORE_MIN,
                     "standing_core_min": STANDING_CORE_MIN,
                     "source": str(CHARTER.relative_to(REPO))},
        "attribution": registry_attribution(),
        "machine": machine(),
    }


def report(state: dict, quiet: bool = False) -> None:
    head = state["launchable"]
    print("Dispatch queue")
    print("=" * 78)
    box = state["machine"]
    print(f"box            {box['cores']} cores, {box['reserved']} reserved, "
          f"{box['usable']} usable; load {box['load_1min']} / "
          f"{box['load_5min']} / {box['load_15min']}; "
          f"{box['idle_cores']} core(s) idle right now")
    print(f"docket         {state['proposals']} proposals, "
          f"{state['approved']} approved, "
          f"{state['approved_needing_a_solver']} of those need a solver "
          f"({state['approved_core_min']:g} core-min)")
    print()
    if not head:
        print("HEAD OF QUEUE   nothing is launchable, and that is a finding, "
              "not a rest state")
    else:
        first = head[0]
        print(f"{len(head)} item(s) are approved, priced on a measurement, "
              f"inside the proposed ceiling and not started: "
              f"{state['launchable_core_min']:g} core-min. At the burst rate "
              f"this box has already sustained, 11.06 cores, that is "
              f"{state['launchable_core_min'] / 11.06 / 60:.1f} hours of work.")
        print()
        basis = str(first["cost_basis"] or "")
        print(f"HEAD OF QUEUE   {first['id']}")
        print(f"                {first['est_core_min']:g} core-min, basis: "
              f"{basis[:180]}{'...' if len(basis) > 180 else ''}")
        print(f"                {first['objective']}")
        for item in head[1:] if not quiet else []:
            print(f"                then {item['id']} "
                  f"({item['est_core_min']:g} core-min)")
    if quiet:
        return
    print()
    print("WHY NOTHING ELSE STARTS -- one reason per item, the first that "
          "applies")
    print("-" * 78)
    for reason, rows in sorted(state["blocked"].items(),
                               key=lambda kv: -len(kv[1])):
        spend = sum(r["est_core_min"] for r in rows)
        print(f"  {reason}: {len(rows)} item(s)"
              + (f", {spend:g} core-min" if spend else ""))
        if reason == "closed":
            continue  # not blocked, just finished; counted so the sum closes
        for row in sorted(rows, key=lambda r: -r["est_core_min"])[:6]:
            if row["est_core_min"]:
                print(f"      {row['id']}: {row['why']}")
    print()
    print("WHY THE CEILING CANNOT BIND AT LAUNCH YET")
    print("-" * 78)
    attribution = state["attribution"]
    print(f"  {attribution['records']} completion record(s) in "
          f"demo-output/website/solve_registry")
    print(f"  {attribution['naming_a_docket_item']} name a docket item "
          f"({attribution['asked_for_an_item']} were even asked), so spend "
          f"cannot be attributed to the thing that was approved")
    print(f"  {attribution['stating_a_rank_count']} state a rank count "
          f"({attribution['asked_for_a_rank_count']} were even asked), so "
          f"core-minutes -- wall seconds x ranks / 60 -- are not derivable "
          f"from the launch record")
    print(f"  {attribution['carrying_start_and_finish']} carry both a start "
          f"and a finish, so WALL time is derivable for all of them")
    print(f"  the largest overrun on record, 1,175.0 core-min against a 120 "
          f"core-min estimate, ran on an item at 'proposed'; a gate that "
          f"fires at approval could not have seen it")
    ceilings = state["ceilings"]
    print(f"  ceilings in use here: per-item {ceilings['per_item_core_min']:g}"
          f", per-day {ceilings['per_day_core_min']:g}, standing "
          f"{ceilings['standing_core_min']:g} core-min, from "
          f"{ceilings['source']} -- "
          f"{'RATIFIED' if ceilings['ratified'] else 'PROPOSED AND NOT '
             'RATIFIED, so every gate above reports and none refuses'}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--quiet", action="store_true",
                        help="the head of the queue only")
    args = parser.parse_args()
    state = queue()
    if args.json:
        print(json.dumps(state, indent=1))
    else:
        report(state, quiet=args.quiet)
    # Zero when something is launchable, 1 when the queue is empty and the box
    # is idle -- so a caller can tell the two kinds of nothing apart.
    return 0 if state["launchable"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
