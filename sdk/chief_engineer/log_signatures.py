"""Pure detection functions for solver-log signatures S6, S7, and S9.

Implements the Monitor Standard rules adopted from the reading program's
agenda (``docs/standards/MONITOR_STANDARD.md``):

- S6 residual stall: a residual plateau without convergence progress while
  the iteration cap approaches. The run exits looking calm; it is not
  converged.
- S7 oscillatory divergence: alternating-sign residual changes with a
  growing envelope. Flag on growth, fatal when the envelope doubles.
- S9 wall-time excursion: a run whose wall time exceeds a configurable
  multiple of the learned 99th percentile for its solver kind. The
  expected wall-time envelope is learned from the mega-batch ledger
  (``demo-output/website/mega-batch/ledger.jsonl``).

Every detector is a pure function over plain numbers and sequences, so each
is unit-testable without a solver. Detectors only name findings, each with a
severity and a prescribed action; they never alter a result. The ledger
percentiles are computed lazily on first use and memoized per file version.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping, Sequence

# Severity vocabulary, matching docs/standards/MONITOR_STANDARD.md.
SEVERITY_FLAG = "flag"
SEVERITY_FATAL = "fatal"

STALL_ACTION = (
    "treat the result as unconverged; run the regime check "
    "(steady versus unsteady) before buying more iterations"
)
OSCILLATION_ACTION = (
    "stop the steady solve; the prescribed fix is the unsteady track, "
    "not more iterations"
)
WALL_TIME_ACTION = (
    "stop and investigate; capture host state and separate solver cost "
    "from infrastructure stalls before trusting the record"
)

# The mega-batch ledger, resolved relative to the repository root.
DEFAULT_LEDGER_PATH = (
    Path(__file__).resolve().parents[2]
    / "demo-output" / "website" / "mega-batch" / "ledger.jsonl"
)

# Memoized envelopes keyed by (path, mtime_ns, size) so a rewritten ledger
# is re-read while repeated calls against the same file cost nothing.
_ENVELOPE_MEMO: dict[tuple[str, int, int], dict[str, dict[str, float]]] = {}


# --------------------------------------------------------------------------
# Shared numeric helpers
# --------------------------------------------------------------------------

def percentile(values: Sequence[float], q: float) -> float:
    """Linear-interpolation percentile (the numpy default), pure Python.

    ``q`` is in [0, 100]. Raises ``ValueError`` on an empty sequence.
    """
    if not values:
        raise ValueError("percentile of an empty sequence")
    if not 0.0 <= q <= 100.0:
        raise ValueError(f"percentile q={q} outside [0, 100]")
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = q / 100.0 * (len(ordered) - 1)
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _median(values: Sequence[float]) -> float:
    return percentile(values, 50.0)


# --------------------------------------------------------------------------
# S6: residual stall
# --------------------------------------------------------------------------

def detect_residual_stall(
    residuals: Sequence[float],
    *,
    target: float,
    window: int = 200,
    improvement_factor: float = 2.0,
    iterations_done: int | None = None,
    iteration_cap: int | None = None,
    cap_fraction: float = 0.8,
) -> dict[str, Any] | None:
    """Residual plateau without convergence progress (Monitor Standard S6).

    Fires when the rolling median over the last ``window`` residuals has
    improved by less than ``improvement_factor`` while the residual still
    sits above ``target``, and, when ``iteration_cap`` is known, the run has
    consumed at least ``cap_fraction`` of it. A steady solver applied past
    its regime degrades without ever spiking, so the spike rule stays
    silent; this rule names the calm-looking failure.

    Returns a finding dict (kind, severity, action, medians, improvement)
    or ``None``. Pure function: no I/O, no state.
    """
    if window < 16 or len(residuals) < window:
        return None
    if iteration_cap is not None:
        done = len(residuals) if iterations_done is None else iterations_done
        if done < cap_fraction * iteration_cap:
            return None
    recent = list(residuals[-window:])
    sub = max(5, window // 8)
    median_early = _median(recent[:sub])
    median_late = _median(recent[-sub:])
    if median_late <= 0 or median_late <= target:
        return None  # converged, or at the solver floor: not a stall
    improvement = median_early / median_late
    if improvement >= improvement_factor:
        return None  # still making progress
    return {
        "kind": "residual-stall",
        "severity": SEVERITY_FLAG,
        "action": STALL_ACTION,
        "window": window,
        "median_early": median_early,
        "median_late": median_late,
        "improvement": improvement,
        "target": target,
    }


# --------------------------------------------------------------------------
# S7: oscillatory divergence
# --------------------------------------------------------------------------

def detect_oscillatory_divergence(
    residuals: Sequence[float],
    *,
    window: int = 50,
    min_alternation: float = 0.6,
    growth_factor: float = 1.25,
    fatal_growth: float = 2.0,
) -> dict[str, Any] | None:
    """Growing oscillation envelope in a residual series (Monitor Standard S7).

    Fires when, over the last ``window`` residuals, consecutive changes
    alternate in sign at least ``min_alternation`` of the time and the
    peak-to-trough envelope of the later half exceeds the earlier half by
    ``growth_factor``. Severity escalates to fatal when the envelope has at
    least doubled (``fatal_growth``).

    Returns a finding dict (kind, severity, action, envelopes, growth,
    alternation) or ``None``. Pure function: no I/O, no state.
    """
    if window < 8 or len(residuals) < window:
        return None
    recent = list(residuals[-window:])
    deltas = [b - a for a, b in zip(recent, recent[1:]) if b != a]
    if len(deltas) < window // 2:
        return None  # too flat to oscillate
    flips = sum(1 for a, b in zip(deltas, deltas[1:]) if (a > 0) != (b > 0))
    alternation = flips / (len(deltas) - 1)
    half = window // 2
    envelope_early = max(recent[:half]) - min(recent[:half])
    envelope_late = max(recent[half:]) - min(recent[half:])
    if envelope_early <= 0:
        return None
    growth = envelope_late / envelope_early
    if alternation < min_alternation or growth < growth_factor:
        return None
    severity = SEVERITY_FATAL if growth >= fatal_growth else SEVERITY_FLAG
    return {
        "kind": "oscillatory-divergence",
        "severity": severity,
        "action": OSCILLATION_ACTION,
        "window": window,
        "envelope_early": envelope_early,
        "envelope_late": envelope_late,
        "growth": growth,
        "alternation": alternation,
    }


# --------------------------------------------------------------------------
# S9: wall-time excursion
# --------------------------------------------------------------------------

def wall_time_percentiles(
    ledger_path: str | os.PathLike[str] | None = None,
    *,
    refresh: bool = False,
) -> dict[str, dict[str, float]]:
    """Per-solver-kind wall-time envelope learned from the ledger.

    Reads the mega-batch ledger (one JSON object per line, with ``solver``
    and ``wall_seconds`` fields) and returns
    ``{kind: {"p50": ..., "p99": ..., "count": ...}}``. The result is
    memoized per (path, mtime, size); pass ``refresh=True`` to force a
    re-read. A missing ledger yields an empty mapping, which downstream
    classification treats as "no envelope, no judgment".
    """
    path = Path(ledger_path) if ledger_path is not None else DEFAULT_LEDGER_PATH
    try:
        stat = path.stat()
    except OSError:
        return {}
    key = (str(path.resolve()), stat.st_mtime_ns, stat.st_size)
    if not refresh and key in _ENVELOPE_MEMO:
        return _ENVELOPE_MEMO[key]
    samples: dict[str, list[float]] = {}
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            kind = row.get("solver")
            wall = row.get("wall_seconds")
            if isinstance(kind, str) and isinstance(wall, (int, float)):
                samples.setdefault(kind, []).append(float(wall))
    envelope = {
        kind: {
            "p50": percentile(values, 50.0),
            "p99": percentile(values, 99.0),
            "count": float(len(values)),
        }
        for kind, values in samples.items()
    }
    _ENVELOPE_MEMO[key] = envelope
    return envelope


def classify_wall_time(
    solver_kind: str,
    wall_seconds: float,
    envelope: Mapping[str, Mapping[str, float]] | None = None,
    *,
    flag_multiple: float = 20.0,
    fatal_multiple: float = 100.0,
    min_samples: int = 20,
    ledger_path: str | os.PathLike[str] | None = None,
) -> dict[str, Any] | None:
    """Wall-time excursion against the learned envelope (Monitor Standard S9).

    A run whose wall time exceeds ``flag_multiple`` times the learned 99th
    percentile for its solver kind is a wall-time excursion: severity flag,
    action stop and investigate. At ``fatal_multiple`` the severity is
    fatal. When the envelope has no entry for the kind, or fewer than
    ``min_samples`` runs behind it, no judgment is made: a threshold from
    thin evidence would be a made-up number.

    ``envelope`` defaults to :func:`wall_time_percentiles` over
    ``ledger_path`` (which itself defaults to the mega-batch ledger).
    Returns a finding dict or ``None``. Never alters the record.
    """
    if envelope is None:
        envelope = wall_time_percentiles(ledger_path)
    stats = envelope.get(solver_kind)
    if not stats:
        return None
    p99 = float(stats.get("p99", 0.0))
    count = int(stats.get("count", 0))
    if p99 <= 0.0 or count < min_samples:
        return None
    multiple = wall_seconds / p99
    if multiple <= flag_multiple:
        return None
    severity = SEVERITY_FATAL if multiple >= fatal_multiple else SEVERITY_FLAG
    return {
        "kind": "wall-time-excursion",
        "severity": severity,
        "action": WALL_TIME_ACTION,
        "solver": solver_kind,
        "wall_seconds": float(wall_seconds),
        "p50": float(stats.get("p50", 0.0)),
        "p99": p99,
        "multiple": multiple,
        "samples": count,
    }
