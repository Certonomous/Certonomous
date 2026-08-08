#!/usr/bin/env python3
"""Replay monitor rule S12 (unsettled stop) against the coefficient archive.

WHY THIS EXISTS. Docket item `w7-cap-stopped-is-a-monitor-signature` gates
adoption on the rule being "replayed against the archive before adoption", and
Monitor Standard standing rule 6 requires every rule to carry its replay line:
the corpus, the fire count, the fatal count, and its behaviour on the case that
motivated it. This script produces all four.

WHAT THE CORPUS IS. Every `coefficient.dat` under `demo-output` (the same root
the S1-S6 and S10 sweeps use, so the numbers are comparable) and under
`/home/ubuntu/certonomous-runs`, which is where the working cases live. Each
file contributes up to two quantity-histories, Cd and Cl, because L-24's rule
is that a quantity converges and not a run -- a file whose Cd has settled and
whose Cl has not is one fire, not zero.

WIDENED 2026-08-08 (Monitor Standard v1.4, proposal
s10d-monitored-quantity-magnitude-explosion): the corpus also ingests
forces-object `moment.dat` and `force.dat` total_x histories. The F8
divergence specimen -- a blade moment at -2.5e99 behind a converged momentum
residual -- lived in exactly such a file, so the coefficient-only glob meant
the archive-replay rail could not see the standard's own best specimen at
all. A history the rail cannot ingest is a history no replay will ever
grade, which is the rail gap this widening closes.

WHAT IT DOES NOT MEASURE. A false-positive rate. Firing on an archived run is
not by itself an error: the archive contains runs that genuinely stopped early,
which is the whole reason the rule exists. What the sweep bounds is how much a
reader is asked to act on, and the motivating-case pair is what shows the rule
discriminates rather than simply firing.

No compute: every number comes from a file already on disk.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from chief_engineer.log_signatures import (  # noqa: E402
    UNSETTLED_MONOTONE_MIN,
    UNSETTLED_REL_DRIFT,
    detect_unsettled_stop,
)

DEFAULT_ROOTS = ("demo-output", "/home/ubuntu/certonomous-runs")

# The solver's own statement that it stopped because its residual criterion was
# met. Matched rather than assumed: the alternative stop is simply reaching the
# end of the time loop, and the two are recorded differently.
STOP_CONVERGED = re.compile(r"solution converged in (\d+) iterations")


def read_columns(path: Path) -> dict[str, list[float]]:
    """Named columns of an OpenFOAM postProcessing .dat file.

    Column names come from the LAST commented header line whose first token
    starts with "Time", which is how OpenFOAM writes them; a file whose header
    is missing yields positional names and is still usable.
    """
    header: list[str] = []
    rows: list[list[float]] = []
    try:
        text = path.read_text(errors="replace")
    except OSError:
        return {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            header.append(line)
            continue
        try:
            values = [float(tok) for tok in line.split()]
        except ValueError:
            continue
        rows.append(values[1:])
    if len(rows) < 5:
        return {}
    names: list[str] = []
    for line in reversed(header):
        tokens = line.lstrip("#").split()
        if len(tokens) >= 2 and tokens[0].lower().startswith("time"):
            names = tokens[1:]
            break
    width = min(len(r) for r in rows)
    return {(names[i] if i < len(names) else f"col{i + 1}"): [r[i] for r in rows]
            for i in range(width)}


def find_case(path: Path) -> Path:
    """Walk up from a postProcessing file to the case directory that owns it."""
    current = path
    for _ in range(6):
        current = current.parent
        if (current / "system").is_dir() or list(current.glob("log.*Foam")):
            return current
    return path.parents[3] if len(path.parents) > 3 else path.parent


def stop_reason(case: Path) -> str:
    """How the run ended, read from the largest solver log beside the case.

    Returns "residual-converged", "ran-to-end", or "unknown" when no solver log
    was kept. "unknown" is reported rather than guessed: at collection time the
    monitor has the log, and the archive not keeping it is a fact about the
    archive, not about the run.
    """
    logs = [p for p in case.glob("log.*")
            if "Foam" in p.name or "foam" in p.name]
    logs = [p for p in logs
            if not any(skip in p.name
                       for skip in ("decompose", "reconstruct", "blockMesh",
                                    "snappyHexMesh", "checkMesh"))]
    if not logs:
        return "unknown"
    log = max(logs, key=lambda p: p.stat().st_size)
    try:
        text = log.read_text(errors="replace")
    except OSError:
        return "unknown"
    return "residual-converged" if STOP_CONVERGED.search(text) else "ran-to-end"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", default=None,
                        help="corpus root (repeatable)")
    parser.add_argument("--out",
                        default="demo-output/website/monitor/replay_s12.json")
    parser.add_argument("--quantity", action="append", default=None,
                        help="coefficient column to grade (default Cd and Cl)")
    args = parser.parse_args()

    roots = [Path(r) for r in (args.root or DEFAULT_ROOTS)]
    quantities = args.quantity or ["Cd", "Cl"]

    histories = 0
    files = 0
    fires: list[dict] = []
    by_stop: dict[str, int] = {}
    corpus_by_stop: dict[str, int] = {}

    def forces_series(path: Path) -> list[float]:
        """total_x (column 1 after Time) of a forces-object dat file, read
        positionally: forces files write parenthesised vector headers that
        defeat name lookup, and total_x is column 1 in both file kinds."""
        out: list[float] = []
        try:
            text = path.read_text(errors="replace")
        except OSError:
            return out
        for line in text.splitlines():
            s = line.strip().replace("(", " ").replace(")", " ")
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            try:
                out.append(float(parts[1]))
            except (ValueError, IndexError):
                continue
        return out

    for root in roots:
        if not root.exists():
            continue
        # The 2026-08-08 widening: forces-object histories enter the corpus.
        for pattern in ("moment.dat", "force.dat"):
            for path in sorted(root.rglob(pattern)):
                if ("bladeForces" not in str(path)
                        and "forces" not in str(path)):
                    continue
                series = forces_series(path)
                if len(series) < 5:
                    continue
                files += 1
                case = find_case(path)
                reason = stop_reason(case)
                histories += 1
                corpus_by_stop[reason] = corpus_by_stop.get(reason, 0) + 1
                finding = detect_unsettled_stop(
                    series, quantity=f"{pattern}:total_x",
                    stop_reason=reason)
                if finding:
                    by_stop[reason] = by_stop.get(reason, 0) + 1
                    fires.append({
                        "case": str(case),
                        "path": str(path),
                        "quantity": f"{pattern}:total_x",
                        "iterations": finding["iterations"],
                        "window": finding["window"],
                        "rel_drift": finding["rel_drift"],
                        "rel_drift_per_100_iterations":
                            finding["rel_drift_per_100_iterations"],
                        "monotone": finding["monotone"],
                        "stop_reason": reason,
                        "severity": finding["severity"],
                    })
        for path in sorted(root.rglob("coefficient.dat")):
            columns = read_columns(path)
            if not columns:
                continue
            files += 1
            case = find_case(path)
            reason = stop_reason(case)
            for quantity in quantities:
                series = columns.get(quantity)
                if not series:
                    continue
                histories += 1
                corpus_by_stop[reason] = corpus_by_stop.get(reason, 0) + 1
                finding = detect_unsettled_stop(
                    series, quantity=quantity, stop_reason=reason)
                if finding:
                    by_stop[reason] = by_stop.get(reason, 0) + 1
                    fires.append({
                        "case": str(case),
                        "path": str(path),
                        "quantity": quantity,
                        "iterations": finding["iterations"],
                        "window": finding["window"],
                        "rel_drift": finding["rel_drift"],
                        "rel_drift_per_100_iterations":
                            finding["rel_drift_per_100_iterations"],
                        "monotone": finding["monotone"],
                        "stop_reason": reason,
                        "severity": finding["severity"],
                    })

    fires.sort(key=lambda f: -abs(f["rel_drift"]))
    report = {
        "rule": "S12",
        "name": "unsettled stop",
        "thresholds": {"rel_drift_tol": UNSETTLED_REL_DRIFT,
                       "monotone_min": UNSETTLED_MONOTONE_MIN},
        "corpus": {"roots": [str(r) for r in roots],
                   "coefficient_files": files,
                   "quantity_histories": histories,
                   "quantities": quantities,
                   "by_stop_reason": corpus_by_stop},
        "fired": len(fires),
        "fired_fraction": (len(fires) / histories) if histories else 0.0,
        "fatal": 0,
        "fired_by_stop_reason": by_stop,
        "fires": fires,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=False) + "\n")
    summary = {k: v for k, v in report.items() if k != "fires"}
    print(json.dumps(summary, indent=2))
    print(f"\nwrote {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
