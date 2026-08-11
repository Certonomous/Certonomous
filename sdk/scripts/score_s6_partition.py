#!/usr/bin/env python3
"""Score the S6 sentinel/gated/fail-open partition with the SHIPPED helpers.

WHY THIS EXISTS. The 135 / 81 / 6 table in
`campaign/S6_WIRING_PREREGISTRATION.md` and its 2026-08-11 re-score were both
produced by ad-hoc scripts that were never committed, so the only way to check
either number was to write a third one -- and a number nobody can re-derive is
a number nobody can refute. This is that script, kept deliberately thin: it
imports `chief_engineer.head_engineer._field_reachability`, the function the
production gate itself arms from, and applies it to the archived
`system/fvSolution` of every gated log in the replay artifact. No second
implementation of the relation exists here; a re-implementation agreeing with
itself would prove nothing about the one that ships.

The fire labels come from `replay_s1_s6.json`, which replayed `LogMonitor`
with `max(per_field)` as the target. Where the gate's own arming target
differs from that, the label is NOT reused: the log is replayed again at the
gate's target, because a fire measured against a different target than the one
the gate would arm is not this gate's fire rate. Pass `--no-refire` to skip
that and see the difference it makes.

Zero core-minutes: it reads archived logs and dictionaries and launches
nothing.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "sdk"))

from chief_engineer.head_engineer import (  # noqa: E402
    LogMonitor, _field_reachability)

REPLAY = REPO / "demo-output" / "website" / "monitor" / "replay_s1_s6.json"

# The three families the pre-registration scored separately, because a single
# global rate hides the spread in both directions.
FAMILIES = (("dafoam", "/dafoam/"), ("campaign", "/campaign/"),
            ("mega-batch", "/mega-batch/"))


def family(log: str) -> str:
    for name, marker in FAMILIES:
        if marker in log:
            return name
    return "other"


def fires(log: str, target: float) -> bool:
    """Replay S6 over one archived log at one target."""
    monitor = LogMonitor(novel=True, residual_target=target)
    step = Path(log).name
    with open(REPO / log, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            monitor.feed(step, line)
    return any(a.kind == "residual-stall" for a in monitor.anomalies)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replay", default=str(REPLAY))
    parser.add_argument("--no-refire", action="store_true",
                        help="reuse the replay's fire label even where the "
                             "gate's arming target differs from the one it "
                             "was measured at")
    parser.add_argument("--json", default="")
    args = parser.parse_args()

    replay = json.loads(Path(args.replay).read_text())
    sources = replay["s6_target_sources"]
    replay_fires = set(replay["gated_s6"]["loose_fires"])

    rows = []
    refired = 0
    for log, info in sorted(sources.items()):
        path = REPO / info["fvSolution"]
        text = path.read_text(errors="replace") if path.exists() else ""
        resolved = _field_reachability(text)
        reachable = resolved["reachable"]
        if reachable:
            klass = "gated"
        elif resolved["excluded"]:
            klass = "sentinel-excluded"
        else:
            klass = "fail-open"
        # The gate arms from the LOOSEST reachable target.
        target = max(reachable.values()) if reachable else None
        replay_target = (max(info["per_field"].values())
                         if info["per_field"] else None)
        fired = log in replay_fires
        if (not args.no_refire and klass == "gated"
                and target != replay_target):
            fired = fires(log, target)
            refired += 1
        rows.append({"log": log, "class": klass, "fire": fired,
                     "family": family(log), "target": target,
                     "unresolved": resolved["unresolved"],
                     "sentinel_1e15": any(
                         entry["target"] == 1e-15
                         for entry in resolved["excluded"].values())})

    counts = Counter(r["class"] for r in rows)
    fired = Counter(r["class"] for r in rows if r["fire"])
    print(f"{len(rows)} gated logs, from {args.replay}")
    for klass in ("sentinel-excluded", "gated", "fail-open"):
        n, f = counts[klass], fired[klass]
        rate = f"{100 * f / n:.0f}%" if n else "--"
        print(f"  {klass:18s} {n:4d} logs   fire {f:4d}   {rate}")
    gated = [r for r in rows if r["class"] == "gated"]
    hits = sum(r["fire"] for r in gated)
    print(f"  gated fire rate: {hits}/{len(gated)} = "
          f"{100 * hits / len(gated):.0f}%" if gated else "  no gated logs")
    for name, _marker in FAMILIES:
        members = [r for r in gated if r["family"] == name]
        if not members:
            continue
        hit = sum(r["fire"] for r in members)
        print(f"    {name:12s} {hit}/{len(members)} = "
              f"{100 * hit / len(members):.0f}%")
    excluded = [r for r in rows if r["class"] == "sentinel-excluded"]
    print(f"  excluded members carrying a 1e-15 target: "
          f"{sum(r['sentinel_1e15'] for r in excluded)} of {len(excluded)}")
    print(f"  logs with a control whose tolerance is unresolvable: "
          f"{sum(1 for r in rows if r['unresolved'])}")
    print(f"  fire labels recomputed at the gate's own target: {refired}")
    if args.json:
        Path(args.json).write_text(json.dumps(rows, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
