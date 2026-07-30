#!/usr/bin/env python3
"""
check_convergence_sweep.py -- run check_convergence.py over every log in
scripts/../demo-output/website/solve_registry/ (and optionally other
directories passed on the command line), and report anything that is not
CONVERGED, sorted so NOT_CONVERGED comes first.

This is the deliberate, one-time sweep this project had never run before
2026-07-30: every previous catch of an unconverged-but-quoted number (L-14,
L-15, the hump corners, A4, the TMR bump, the wall.json credentials) was
found by someone looking at something else. This script looks at everything,
on purpose.

Usage:
    check_convergence_sweep.py [DIR ...]        # defaults to solve_registry
    check_convergence_sweep.py --json > sweep.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from check_convergence import classify  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
DEFAULT_DIR = REPO / "demo-output" / "website" / "solve_registry"


def case_for_log(log_path: Path) -> str | None:
    """Best-effort: find the matching .done file (same stem) and pull its
    'case:' line, so the residualControl enrichment has somewhere to look."""
    done = log_path.with_suffix(".done")
    if not done.exists():
        return None
    try:
        for line in done.read_text(errors="replace").splitlines():
            m = re.match(r"case:\s*(\S.*)$", line)
            if m:
                case = m.group(1).strip()
                p = Path(case)
                if not p.is_absolute():
                    p = REPO / case
                return str(p) if p.exists() else None
    except OSError:
        return None
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="*", default=[str(DEFAULT_DIR)])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    logs: list[Path] = []
    for d in args.dirs:
        logs.extend(sorted(Path(d).glob("*.log")))
        logs.extend(sorted(Path(d).rglob("log.*")))  # OpenFOAM-style log.simpleFoam etc.

    logs = sorted(set(logs))
    results = []
    for log in logs:
        case = case_for_log(log)
        r = classify(str(log), case)
        r["case_used"] = case
        results.append(r)

    order = {"NOT_CONVERGED": 0, "CANNOT_TELL": 1, "CONVERGED": 2}
    results.sort(key=lambda r: (order.get(r["status"], 9), r["log"]))

    if args.json:
        print(json.dumps(results, indent=2, default=str))
        return 0

    counts = {"CONVERGED": 0, "NOT_CONVERGED": 0, "CANNOT_TELL": 0}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1

    print(f"Swept {len(results)} logs under {args.dirs}")
    print(f"  CONVERGED:     {counts['CONVERGED']}")
    print(f"  NOT_CONVERGED: {counts['NOT_CONVERGED']}")
    print(f"  CANNOT_TELL:   {counts['CANNOT_TELL']}")
    print()

    for status in ("NOT_CONVERGED", "CANNOT_TELL"):
        rows = [r for r in results if r["status"] == status]
        if not rows:
            continue
        print(f"=== {status} ({len(rows)}) ===")
        for r in rows:
            print(f"  {Path(r['log']).name}")
            print(f"      type:   {r.get('solver_type')}")
            print(f"      reason: {r.get('reason')}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
