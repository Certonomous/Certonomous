"""Retrospective wall-time assessment over the mega-batch ledger.

WHAT THIS IS, AND WHAT IT IS NOT
--------------------------------
This is an ASSESSMENT applied after the fact. It reads the durable ledger and
reports what the Monitor Standard's S9 rule WOULD have said about each row had
the rule existed when the row was written. It is not a record of what the
monitor saw at the time. The monitor saw nothing: every one of these rows was
recorded ok with no flag anywhere, and that silence is the whole reason the
rule was proposed.

Nothing here rewrites history. The ledger is never opened for writing, no
recorded field is altered, and no row is reclassified. The output is a separate
artifact, written next to the ledger, whose every entry is explicitly labelled
an assessment.

Going forward the rule runs live: ``run_task`` in ``workflows/mega_batch.py``
stamps ``wall_time_excursion`` onto a row as it is written, and that field IS
what the monitor saw.

Usage::

    python3 sdk/scripts/assess_ledger_wall_times.py [--ledger PATH] [--out PATH]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))

from chief_engineer.log_signatures import (  # noqa: E402
    FATAL_MULTIPLE,
    FLAG_MULTIPLE,
    classify_wall_time,
    wall_time_percentiles,
)

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

DEFAULT_LEDGER = (
    lab_paths.MEGA_BATCH / "ledger.jsonl")
ASSESSMENT_BASENAME = "wall_time_assessment.json"

DISCLAIMER = (
    "Retrospective assessment, not monitor history. Every row below was "
    "recorded ok with no flag at the time it was written, because the rule "
    "did not exist yet. This artifact states what the rule would have said, "
    "and changes no record."
)


def assess(ledger_path: Path) -> dict:
    envelope = wall_time_percentiles(ledger_path, refresh=True)
    rows = 0
    judged = 0
    findings: list[dict] = []
    per_solver: dict[str, dict] = {}

    with open(ledger_path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            rows += 1
            solver = row.get("solver")
            wall = row.get("wall_seconds")
            if not isinstance(solver, str) or not isinstance(wall, (int, float)):
                continue
            judged += 1
            counts = per_solver.setdefault(
                solver, {"rows": 0, "flag": 0, "fatal": 0})
            counts["rows"] += 1
            finding = classify_wall_time(solver, float(wall), envelope)
            if not finding:
                continue
            counts[finding["severity"]] += 1
            findings.append({
                "assessment": True,
                "recorded_ok_at_the_time": bool(row.get("ok")),
                "monitor_flagged_at_the_time": False,
                "index": row.get("index"),
                "solver": solver,
                "timestamp": row.get("timestamp"),
                "wall_seconds": float(wall),
                "would_have_been": finding["severity"],
                "multiple_of_p99": round(finding["multiple"], 1),
            })

    findings.sort(key=lambda f: -f["wall_seconds"])
    return {
        "artifact": "wall-time assessment",
        "disclaimer": DISCLAIMER,
        "assessed_at": datetime.now(timezone.utc).isoformat(
            timespec="seconds"),
        "ledger_rows_read": rows,
        "rows_with_a_solver_and_a_wall_time": judged,
        "rule": {
            "standard": "Certonomous Monitor Standard S9",
            "proposal": "r1-monitor-walltime-rule",
            "flag_multiple_of_p99": FLAG_MULTIPLE,
            "fatal_multiple_of_p99": FATAL_MULTIPLE,
        },
        "envelope_learned_from_this_ledger": {
            kind: {
                "p50_seconds": round(stats["p50"], 4),
                "p99_seconds": round(stats["p99"], 4),
                "runs": int(stats["count"]),
            }
            for kind, stats in sorted(envelope.items())
        },
        "per_solver": {
            kind: counts for kind, counts in sorted(per_solver.items())},
        "would_have_been_flagged": sum(
            1 for f in findings if f["would_have_been"] == "flag"),
        "would_have_been_fatal": sum(
            1 for f in findings if f["would_have_been"] == "fatal"),
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(argv)

    if not args.ledger.exists():
        print(f"no ledger at {args.ledger}")
        return 1
    report = assess(args.ledger)
    out = args.out or args.ledger.parent / ASSESSMENT_BASENAME
    staging = out.with_suffix(".json.tmp")
    staging.write_text(json.dumps(report, indent=1), encoding="utf-8")
    staging.replace(out)

    print(f"assessed {report['ledger_rows_read']} ledger rows")
    print(f"would have been flagged: {report['would_have_been_flagged']}")
    print(f"would have been fatal:   {report['would_have_been_fatal']}")
    print(f"written to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
