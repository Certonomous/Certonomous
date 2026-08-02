#!/usr/bin/env python3
"""How much of this lab's measured wall time was contention rather than work.

    python3 scripts/contention_audit.py                   # the whole corpus
    python3 scripts/contention_audit.py --window \
        2026-08-01T07:56 2026-08-01T09:43                 # one measurement window
    python3 scripts/contention_audit.py --json

WHY THIS EXISTS. `scripts/cost_calibration.py` found that the predictor of a
cost overrun is the cost BASIS: over its first fifteen pairs, a basis beginning
"measured" never over-ran past 1.051x while a forecast basis reached 13.55x.
That result only means something if "measured" means something, and a wall
clock taken while more solvers than cores share the box is a measurement of the
queue. Before this file the lab could not check: the completion records in
`demo-output/website/solve_registry` carry a start and a finish and nothing
about the conditions, so every one of them is a wall clock with no way to tell
whether the box was quiet.

WHAT IT READS, and it is not a new measurement. OpenFOAM already prints both
clocks side by side on every iteration -- `ExecutionTime` is CPU consumed,
`ClockTime` is wall elapsed -- and the last pair in a log is the run's own total.
Their ratio is the fraction of the wall clock the process actually held its
core. Nothing here launches anything or re-runs anything; it reads logs on disk.

THE INSTRUMENT WAS NOT INVENTED HERE. The B-52 rung-7 record reached this
conclusion first and by hand: "the basis was finer2's WALL clock of 285 s on a
run whose own log reads ExecutionTime 183.26 s ClockTime 284 s -- 35 percent of
that basis was contention. Take ExecutionTime for a cost basis, not wall clock."
This file is that check applied to every log instead of one.

WHAT THE RATIO CANNOT SEE, stated because a bound with an undeclared hole is
worse than a wider honest one. It detects a process that did not get a core. It
does NOT detect memory-bandwidth contention, which slows the CPU time itself,
so a ratio of 1.0 bounds scheduling contention only and is not a certificate
that the box was quiet. A window that reads clean here is not proven clean; a
window that reads dirty here IS proven dirty, which is the direction that
matters for refusing to price on it.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import statistics
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
# Where solves actually write. The registry holds the launcher's own logs; the
# runs tree holds everything launched any other way, and the second is larger,
# which is itself the finding in section 2 of the report below.
ROOTS = [Path.home() / "certonomous-runs",
         REPO / "demo-output" / "website" / "solve_registry"]

_EXEC = re.compile(rb"ExecutionTime\s*=\s*([0-9.]+)\s*s")
_CLOCK = re.compile(rb"ClockTime\s*=\s*([0-9.]+)\s*s")
# Only the tail of a log is read. A finished OpenFOAM run prints its totals at
# the end, and some of these logs are 20 MB.
_TAIL_BYTES = 200_000
# Below this the wall clock is contention enough that it must not be quoted as
# a cost. 0.95 is not derived from anything -- it is a round number chosen so
# that a five percent inflation is tolerated, and it is stated here rather than
# buried so that changing it is a visible act.
USABLE_RATIO = 0.95


def _scan(roots: list[Path]) -> list[dict]:
    rows, seen = [], set()
    for root in roots:
        if not root.is_dir():
            continue
        # BOTH conventions, because this lab uses both and the first pass of
        # this file matched only one: OpenFOAM tutorials write `log.simpleFoam`
        # while the DPW5 committee-grid probe writes
        # `hybrid_base_sa_incompressible_a2.11_solve.log`. Globbing `log*`
        # alone missed all 34 logs of the largest overrun on record.
        for path in sorted(set(root.rglob("log*")) | set(root.rglob("*.log"))):
            if not path.is_file():
                continue
            try:
                real = str(path.resolve())
                if real in seen:
                    continue
                seen.add(real)
                size = path.stat().st_size
                with path.open("rb") as handle:
                    if size > _TAIL_BYTES:
                        handle.seek(size - _TAIL_BYTES)
                    tail = handle.read()
            except OSError:
                continue
            cpu, wall = _EXEC.findall(tail), _CLOCK.findall(tail)
            if not (cpu and wall):
                continue
            cpu_s, wall_s = float(cpu[-1]), float(wall[-1])
            if wall_s <= 0 or cpu_s <= 0:
                continue
            rows.append({
                "log": str(path),
                # mtime is when the log stopped being written, i.e. when the
                # run ended. It is the only timestamp these logs carry, and it
                # is stated as such rather than called a start time.
                "ended": dt.datetime.fromtimestamp(path.stat().st_mtime,
                                                   dt.timezone.utc),
                "cpu_s": cpu_s, "wall_s": wall_s,
                "cpu_to_wall": cpu_s / wall_s,
                "wall_s_lost": max(0.0, wall_s - cpu_s)})
    rows.sort(key=lambda r: r["ended"])
    return rows


def analyse(window: tuple[dt.datetime, dt.datetime] | None = None) -> dict:
    rows = _scan(ROOTS)
    if window:
        lo, hi = window
        rows = [r for r in rows if lo <= r["ended"] <= hi]
    if not rows:
        return {"logs": 0, "rows": []}
    cpu = sum(r["cpu_s"] for r in rows)
    wall = sum(r["wall_s"] for r in rows)
    by_day: dict[str, list[float]] = defaultdict(lambda: [0.0, 0.0])
    for row in rows:
        bucket = by_day[row["ended"].date().isoformat()]
        bucket[0] += row["cpu_s"]
        bucket[1] += row["wall_s"]
    return {
        "logs": len(rows),
        "cpu_hours": round(cpu / 3600, 2),
        "wall_hours": round(wall / 3600, 2),
        # Time-weighted, not the median of ratios: a two-second log and a
        # three-hour log are not one vote each when the question is how much
        # measured time was contention.
        "contention_fraction_of_wall": round(1 - cpu / wall, 4),
        "median_cpu_to_wall": round(statistics.median(
            r["cpu_to_wall"] for r in rows), 3),
        "below_usable_ratio": sum(1 for r in rows
                                  if r["cpu_to_wall"] < USABLE_RATIO),
        "usable_ratio": USABLE_RATIO,
        "worst": sorted(({"log": r["log"],
                          "cpu_to_wall": round(r["cpu_to_wall"], 3),
                          "wall_min": round(r["wall_s"] / 60, 1),
                          "wall_min_lost": round(r["wall_s_lost"] / 60, 1),
                          "ended": r["ended"].isoformat(timespec="minutes")}
                         for r in rows), key=lambda r: -r["wall_min_lost"])[:12],
        "by_day": {day: {"cpu_hours": round(c / 3600, 2),
                         "wall_hours": round(w / 3600, 2),
                         "contention_fraction": round(1 - c / w, 4)}
                   for day, (c, w) in sorted(by_day.items())},
        "rows": rows,
    }


def report(state: dict, window: tuple | None) -> None:
    print("Contention audit: how much measured wall time was not work")
    print("=" * 78)
    if not state["logs"]:
        print("no log in the scanned roots carries an "
              "ExecutionTime/ClockTime pair"
              + (" inside that window" if window else ""))
        return
    if window:
        print(f"window         {window[0].isoformat()} .. "
              f"{window[1].isoformat()}")
    print(f"logs           {state['logs']} carry both clocks")
    print(f"totals         {state['cpu_hours']} CPU-hours inside "
          f"{state['wall_hours']} wall-hours")
    print(f"contention     {100 * state['contention_fraction_of_wall']:.1f}% "
          f"of all measured wall time, time-weighted")
    print(f"median run     cpu_to_wall {state['median_cpu_to_wall']}; "
          f"{state['below_usable_ratio']} run(s) below "
          f"{state['usable_ratio']} and so not quotable as a cost")
    print()
    print("WORST, BY WALL MINUTES LOST TO CONTENTION")
    print("-" * 78)
    for row in state["worst"]:
        print(f"  {row['wall_min_lost']:8.1f} min lost  ratio "
              f"{row['cpu_to_wall']:5.3f}  of {row['wall_min']:8.1f} min  "
              f"{row['ended']}")
        print(f"           {row['log']}")
    print()
    print("BY DAY (a log is dated by when it stopped being written)")
    print("-" * 78)
    for day, cut in state["by_day"].items():
        flag = "  <-- above 5%" if cut["contention_fraction"] > 0.05 else ""
        print(f"  {day}  {cut['cpu_hours']:6.2f} CPU-h in "
              f"{cut['wall_hours']:6.2f} wall-h   "
              f"{100 * cut['contention_fraction']:5.1f}% contention{flag}")
    print()
    print("A window that reads clean here is not PROVEN clean: this ratio sees "
          "a process denied a core and cannot see memory-bandwidth contention. "
          "A window that reads dirty IS proven dirty.")


def _parse(stamp: str) -> dt.datetime:
    value = dt.datetime.fromisoformat(stamp)
    return value if value.tzinfo else value.replace(tzinfo=dt.timezone.utc)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--window", nargs=2, metavar=("START", "END"),
                        help="ISO stamps; restrict to runs that ENDED inside")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    window = (_parse(args.window[0]), _parse(args.window[1])) \
        if args.window else None
    state = analyse(window)
    if args.json:
        state.pop("rows", None)
        print(json.dumps(state, indent=1))
    else:
        report(state, window)
    # 1 when some run in scope is not quotable as a cost, so a caller can gate.
    return 1 if state.get("below_usable_ratio") else 0


if __name__ == "__main__":
    raise SystemExit(main())
