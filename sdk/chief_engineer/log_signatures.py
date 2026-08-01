"""Pure detection functions for solver-log signatures S6 to S10.

Implements the Monitor Standard rules adopted from the reading program's
agenda (``docs/standards/MONITOR_STANDARD.md``):

- S6 residual stall: a residual plateau without convergence progress while
  the iteration cap approaches. The run exits looking calm; it is not
  converged.
- S7 oscillatory divergence: WITHDRAWN 2026-08-01 and removed from this
  module. It fired on 68 of the lab's 106 archived steady solver logs and
  reached fatal on 65, all completed runs; four measured tightenings gave 68,
  40, 59 and 23; and it could not separate the two logs of the case it was
  written for, 22 firings on the sick one against 20 on the healthy one. The
  measurements are kept beside the entry in the Monitor Standard. There is
  deliberately no gated, disabled or dead-code version of it here: a detector
  left in the module gets rewired.
- S8 Courant excursion: a transient run whose reported maximum Courant
  number exceeds its case limit by more than the tolerance an adaptive
  time step explains, or which grows monotonically at a fixed time step.
- S9 wall-time excursion: a run whose wall time exceeds a configurable
  multiple of the learned 99th percentile for its solver kind. The
  expected wall-time envelope is learned from the mega-batch ledger
  (``demo-output/website/mega-batch/ledger.jsonl``).
- S10 divergence behind a converged residual: a field that has left the
  physical range while the number the run reports as its residual reads
  converged. Three independent branches, each measured against the lab's
  archived logs before adoption.
- S11 system operations allowed: the solver's own report that the host is
  configured to let a case compile and execute its own code. The only rule
  here whose severity is about the machine rather than the numbers.

Every detector is a pure function over plain numbers and sequences, so each
is unit-testable without a solver. Detectors only name findings, each with a
severity and a prescribed action; they never alter a result. The ledger
percentiles are computed lazily on first use and memoized per file version.
"""

from __future__ import annotations

import json
import math
import os
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

# Severity vocabulary, matching docs/standards/MONITOR_STANDARD.md.
SEVERITY_WATCH = "watch"
SEVERITY_FLAG = "flag"
SEVERITY_FATAL = "fatal"
# S11. Not a numerical severity at all: the run is arithmetically fine and the
# result stands, but the box was configured to let the case execute code. It
# must not be collapsed into "nothing fatal", because "nothing fatal" is a
# statement about the numbers and this is a statement about the host.
SEVERITY_CONFIGURATION_RISK = "configuration risk"

STALL_ACTION = (
    "treat the result as unconverged; run the regime check "
    "(steady versus unsteady) before buying more iterations"
)
COURANT_ACTION = (
    "reduce the time step or enable adaptive stepping; a transient result "
    "computed above its Courant limit is not evidence"
)
WALL_TIME_ACTION = (
    "stop and investigate; capture host state and separate solver cost "
    "from infrastructure stalls before trusting the record"
)
DIVERGENCE_ACTION = (
    "stop and investigate; no quantity computed from this state is evidence, "
    "and any number already published from it is withdrawn"
)

# The thresholds the owner approved on r1-monitor-walltime-rule, in the words
# of the proposal: "flag any run beyond 10 times its solver's running 99th
# percentile, stop and investigate beyond 100 times". Measured against the full
# 208193-row mega-batch ledger, 10x costs almost nothing in noise over 20x: it
# flags 30 rows rather than 27, and the three extra are reduced-order rows whose
# absolute wall times are 0.05 to 0.43 s. Every wall-time excursion the ledger
# actually holds (the six ~16300 s rows across the cylinder and wing solvers)
# lands far past the fatal multiple either way.
FLAG_MULTIPLE = 10.0
FATAL_MULTIPLE = 100.0

# The named field a record carries for a wall-time excursion, so fleet learning
# can separate genuine solver cost from infrastructure stalls.
WALL_TIME_FIELD = "wall_time_excursion"

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
# S7: oscillatory divergence — WITHDRAWN 2026-08-01, detector removed
#
# `detect_oscillatory_divergence` used to live here. It fired when, over the
# last 50 residuals, consecutive changes alternated in sign at least 60 percent
# of the time and the peak-to-trough envelope of the later half exceeded the
# earlier half by 1.25x, escalating to fatal at 2x.
#
# WHY IT IS GONE, and why this comment is not a disabled function. Replayed
# ungated over every steady solver log the lab has archived, 106 of them, it
# fires on 68 and reaches fatal on 65, and every one of those runs completed
# with its results on the record. Four tightenings were measured and none
# rescued it: requiring the residual level to stop improving still fires on 68,
# full-window persistence 40, a 200 iteration growth baseline 59, a fourfold
# growth factor 23. On the case it was written for it fires 22 times on the
# sick log and 20 times on the healthy one, so it does not separate them.
#
# The cause is structural rather than a bad threshold: a converged field sits
# flat with small noise, and the ratio of one noise envelope to the next is
# close to a coin toss, which a run of thousands of iterations wins somewhere.
# The fire rate is therefore a function of run length, not of run health.
#
# It shipped behind a gate requiring a `residual_target`, and that gate was
# never measured: the archived logs do not record the target each run aimed
# for, so the corpus cannot be replayed with the gate in place. A detection
# rule nobody can validate is worse than no rule, because it is trusted.
#
# Withdrawn by supervisor ruling R1, answering conflict C-2 in
# `docs/charters/PROPOSALS_OPEN.md` with option B. Full record and all five
# measurements: `docs/standards/MONITOR_STANDARD.md`, the S7 entry and 3.2.
#
# WHAT IS NOW UNCOVERED: the growing-oscillation half of graceful degradation
# in a steady solve past its regime. S6 still covers the stalled-residual half.
# A replacement must be replayed against the archive first and must be shown to
# separate the two logs of its own motivating case; that last test is the one
# S7 failed and the one nobody applied before adopting it.
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# S8: Courant excursion
# --------------------------------------------------------------------------

# An adaptive time step is set from the PREVIOUS step's Courant number, so the
# reported maximum routinely lands a little above the requested limit. Measured
# on the lab's archived transient runs (the four unsteady cylinder cases under
# the mega-batch work tree, 13308 time steps at maxCo 1.5): 42 percent of all
# healthy steps sit strictly above the limit, and the largest overshoot anywhere
# in the four runs is 0.403 percent. A rule written as a strict comparison would
# therefore have called every healthy transient run in the lab an excursion. The
# default tolerance below is 2 percent, five times the largest measured healthy
# overshoot, so ordinary adaptive stepping never trips it.
COURANT_TOLERANCE = 0.02

# Longest monotone rising run of the reported maximum in those same healthy
# archived runs: 17 consecutive steps. The Monitor Standard's window of 20 sits
# above that, and the monotone rule additionally requires a fixed time step,
# which none of those runs had.
COURANT_GROWTH_WINDOW = 20


def detect_courant_excursion(
    max_courant: Sequence[float],
    *,
    limit: float,
    tolerance: float = COURANT_TOLERANCE,
    window: int = COURANT_GROWTH_WINDOW,
    fixed_time_step: bool = False,
) -> dict[str, Any] | None:
    """Courant excursion in a transient run (Monitor Standard S8).

    Two conditions, in severity order:

    * FATAL: the reported maximum grew monotonically across ``window``
      consecutive time steps while the time step was fixed. A fixed step with
      a climbing Courant number means the flow is accelerating into the cell
      size and nothing is holding it back.
    * FLAG: the reported maximum exceeds ``limit * (1 + tolerance)``. The
      tolerance exists because adaptive stepping overshoots its own target by
      construction; see ``COURANT_TOLERANCE`` for the measurement behind the
      default.

    ``limit`` is the case's own requested maximum (``maxCo``). Returns a
    finding dict or ``None``. Pure function: no I/O, no state.
    """
    if limit <= 0 or not max_courant:
        return None
    series = [float(v) for v in max_courant]
    threshold = limit * (1.0 + tolerance)
    peak = max(series)

    if fixed_time_step and window >= 2 and len(series) >= window:
        run = 1
        for earlier, later in zip(series, series[1:]):
            run = run + 1 if later > earlier else 1
            if run >= window:
                return {
                    "kind": "courant-excursion",
                    "severity": SEVERITY_FATAL,
                    "action": COURANT_ACTION,
                    "reason": "monotonic growth at a fixed time step",
                    "limit": float(limit),
                    "threshold": threshold,
                    "peak": peak,
                    "window": window,
                    "steps": len(series),
                }

    if peak > threshold:
        exceedances = sum(1 for value in series if value > threshold)
        return {
            "kind": "courant-excursion",
            "severity": SEVERITY_FLAG,
            "action": COURANT_ACTION,
            "reason": "reported maximum above the case limit",
            "limit": float(limit),
            "threshold": threshold,
            "peak": peak,
            "exceedances": exceedances,
            "steps": len(series),
        }
    return None


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
    flag_multiple: float = FLAG_MULTIPLE,
    fatal_multiple: float = FATAL_MULTIPLE,
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


def wall_time_record_field(
    solver_kind: str,
    wall_seconds: float,
    envelope: Mapping[str, Mapping[str, float]] | None = None,
    *,
    ledger_path: str | os.PathLike[str] | None = None,
    flag_multiple: float = FLAG_MULTIPLE,
    fatal_multiple: float = FATAL_MULTIPLE,
) -> dict[str, Any] | None:
    """The compact named field a record carries when a run is an excursion.

    The approved rule requires the excursion to survive as a named field on
    the record, so fleet learning can separate genuine solver cost from
    infrastructure stalls rather than averaging the two together. Returns the
    value for ``WALL_TIME_FIELD``, or ``None`` when the run is ordinary and
    the record should carry no such field at all.

    The envelope this was judged against travels with the finding, because a
    multiple means nothing without the percentile and the sample count behind
    it, and both move as the ledger grows.
    """
    finding = classify_wall_time(
        solver_kind, wall_seconds, envelope, ledger_path=ledger_path,
        flag_multiple=flag_multiple, fatal_multiple=fatal_multiple)
    if not finding:
        return None
    return {
        "severity": finding["severity"],
        "multiple": round(finding["multiple"], 1),
        "p99_seconds": round(finding["p99"], 4),
        "envelope_samples": finding["samples"],
        "action": finding["action"],
    }


# --------------------------------------------------------------------------
# S10: divergence behind a converged residual
# --------------------------------------------------------------------------
#
# THE RUN THIS FAMILY WAS DESIGNED AGAINST. The Ahmed body primal on the
# 45760-cell mesh (ladder rung A4) ran to its iteration cap, printed a drag
# coefficient, and that number was published and later withdrawn. Its
# turbulence field had diverged: omega was pegged against the upper end of its
# clipping range from iteration 100 onward, and its unnormalised residual norm
# finished at 1.13e+35 against 6.9e+03 for momentum. The number the log
# reports as the omega residual finished at 5.9e-31, which reads as converged
# to every rule the monitor had. A normalised residual is a ratio, and when
# the field blows up the denominator blows up with it, so the ratio collapses
# toward zero exactly when the field is worst. None of S1 to S9 sees this: no
# NaN, no exception, no spike, no stall (the residual is far BELOW target, not
# above it), no oscillation, no Courant line, and 18 s of wall time.
#
# Each branch below was measured over every solver log the lab has archived,
# 379 of them, before adoption. Each fires on exactly one: the withdrawn run.

# A normalised residual at or below this is not convergence, it is a field
# that has stopped being a ratio of anything meaningful. The tightest
# residualControl target anywhere in the lab's cases is 1e-08; this floor sits
# twelve orders below that, so no case can converge into it legitimately.
DEAD_FIELD_FLOOR = 1e-20

# Consecutive iterations at the floor before the reading is called an
# artefact. Measured: the withdrawn run holds it for 497 of its 500
# iterations, and no other archived log reaches 50 at this floor. The window
# is set at 100, and the survey shows the finding is identical at 50 and 200.
DEAD_FIELD_WINDOW = 100

# S10c compares a field's unnormalised residual norm against momentum. Over
# the 157 archived runs that print such a block, the largest healthy ratio is
# 3.6 orders of magnitude (a turbulence field on the healthy coarse mesh of
# the very same case). The withdrawn run sits at 31.2 orders. The threshold is
# 10 orders: six above anything healthy, twenty one below the failure.
RESIDUAL_NORM_ORDERS = 10.0

# The three forms a clipping message takes in the lab's solvers. The first two
# are the DAFoam form and carry the direction of the clip, which is the whole
# point: a field held UP off a floor is ordinary, a field dragged DOWN off a
# ceiling has left the physical range. The third is the classic OpenFOAM form,
# which clips from below only and stays an S4 watch.
_BOUND_CEILING = re.compile(r"^\s*Bounding (\w[\w.]*)<([0-9.eE+-]+)")
_BOUND_FLOOR = re.compile(r"^\s*Bounding (\w[\w.]*)>([0-9.eE+-]+)")
_BOUND_CLASSIC = re.compile(r"^\s*bounding (\w[\w.]*),")

CEILING = "ceiling"
FLOOR = "floor"


def classify_bound_line(line: str) -> dict[str, Any] | None:
    """Which end of its clipping range a field was held at (Monitor Standard S10a).

    Returns ``{"field", "direction", "bound"}`` or ``None``. ``direction`` is
    ``"ceiling"`` when the solver clipped the field DOWN from above and
    ``"floor"`` when it held the field UP from below.

    The distinction is the finding. Turbulence quantities are held off zero on
    almost every healthy run, and S4 already watches that. Being clipped at
    the top of the range is different in kind: an eddy frequency at 1e+16 is
    not a small numerical difference, it is a field that has diverged and is
    being stopped from taking the run down with it.

    CALIBRATION CORRECTED 2026-08-01, and the correction matters more than the
    number. This docstring used to say "measured over the lab's 379 archived
    logs, a ceiling clip appears in exactly one of them". Over the archive as
    it now stands (452 logs) it appears in five. The four new ones are S1 FIML
    finite-difference probe points under
    ``demo-output/website/dafoam/ladder-b/S1_work/logs/fd_points``.

    That census was never a census of solves. It is a census of what solvers
    PRINTED. DAFoam gates its bound message on ``printInterval``, so a log
    written at the default ``printInterval 100`` reports clipping from 1% of
    its iterations. Re-running the S1 baseline point unchanged except for
    ``printInterval: 1`` (2026-08-01, logs under
    ``/home/ubuntu/certonomous-runs/S1-fiml/ramp_kw_clipcheck/fdlogs/``)
    returns a BIT-IDENTICAL objective, 1.3816040076915038e-02, and prints 20
    ceiling clips where the archived log prints none. The archived count is a
    sampling floor, not a measurement, and so is this one.

    What survived the correction is the direction test. What did not survive is
    the assumption that any ceiling clip anywhere in a log condemns the run.
    The withdrawn A4 run clips at every printed iteration INCLUDING ITS LAST
    (``omega<1e+16`` at 100/200/300/400/500 of 500), so its final state is the
    clipped one. The S1 points clip only across iterations 35 to 137 of runs
    1774 to 2307 iterations long, and the bound is inactive for the last ~93%
    and at the converged state the objective is read from. Persistence to the
    final iterate is the discriminator this rule does not yet implement; see
    ``docs/standards/MONITOR_STANDARD.md`` section 3. Severity is deliberately
    left FATAL pending that change.
    """
    match = _BOUND_CEILING.match(line)
    if match:
        return {"field": match.group(1), "direction": CEILING,
                "bound": float(match.group(2))}
    match = _BOUND_FLOOR.match(line) or _BOUND_CLASSIC.match(line)
    if match:
        bound = float(match.group(2)) if match.re is _BOUND_FLOOR else None
        return {"field": match.group(1), "direction": FLOOR, "bound": bound}
    return None


def detect_ceiling_clip(line: str) -> dict[str, Any] | None:
    """A field clipped at the top of its permitted range (Monitor Standard S10a).

    Severity fatal. A clipped ceiling is not a warning about the solve, it is
    the statement that the field is no longer physical, and every quantity
    integrated from it afterwards inherits that.
    """
    bound = classify_bound_line(line)
    if not bound or bound["direction"] != CEILING:
        return None
    return {
        "kind": "ceiling-clip",
        "severity": SEVERITY_FATAL,
        "action": DIVERGENCE_ACTION,
        "field": bound["field"],
        "bound": bound["bound"],
    }


def detect_normalisation_collapse(
    residuals: Sequence[float],
    *,
    peer_residuals: Sequence[float] = (),
    floor: float = DEAD_FIELD_FLOOR,
    window: int = DEAD_FIELD_WINDOW,
) -> dict[str, Any] | None:
    """A residual reading that collapsed rather than converged (S10b).

    Fires when a field's normalised residual has sat at or below ``floor`` for
    the last ``window`` iterations, having been above it earlier in the run,
    while at least one other field in the same solve is still working above
    the floor.

    All three conditions carry weight. Sitting at the floor is the symptom.
    Having been above it earlier is what separates a diverged field from one
    the solver never solves at all: a conserved variable updated explicitly
    reports a residual of exactly zero from the first iteration to the last,
    and five such series in the archive are correctly passed over on this
    condition alone. A working peer is what makes the reading a contradiction
    rather than a finished solve.

    Returns a finding dict or ``None``. Pure function: no I/O, no state.
    """
    if window < 8 or len(residuals) < window:
        return None
    series = [float(value) for value in residuals]
    trailing = 0
    for value in reversed(series):
        if value <= floor:
            trailing += 1
        else:
            break
    if trailing < window:
        return None
    if max(series) <= floor:
        return None  # never alive: this field is not being solved
    peers = [float(value) for value in peer_residuals]
    if peers and not any(value > floor for value in peers):
        return None  # the whole solve is at the floor, so nothing contradicts
    return {
        "kind": "normalisation-collapse",
        "severity": SEVERITY_FLAG,
        "action": DIVERGENCE_ACTION,
        "floor": floor,
        "window": window,
        "iterations_at_floor": trailing,
        "iterations_seen": len(series),
        "peak": max(series),
    }


def detect_residual_norm_contradiction(
    norms: Mapping[str, float],
    *,
    reference_field: str = "U",
    orders: float = RESIDUAL_NORM_ORDERS,
) -> dict[str, Any] | None:
    """Unnormalised residual norms that contradict the reported convergence (S10c).

    Some solvers print the unnormalised residual norm of every field at the
    end of a run. That block is the honest one: it is not divided by anything
    that can blow up with the field. Fires when any field's norm exceeds the
    momentum norm by more than ``orders`` orders of magnitude, which means the
    equations were never jointly satisfied whatever the reported residuals
    said.

    ``norms`` maps field name to residual norm. Returns a finding dict for the
    worst offending field, or ``None``. Pure function: no I/O, no state.
    """
    reference = norms.get(reference_field)
    if reference is None or not math.isfinite(reference) or reference <= 0:
        return None
    worst_field, worst_ratio = None, 0.0
    for field, value in norms.items():
        if field == reference_field:
            continue
        value = abs(float(value))
        if not math.isfinite(value):
            worst_field, worst_ratio = field, math.inf
            break
        ratio = value / reference
        if ratio > worst_ratio:
            worst_field, worst_ratio = field, ratio
    if worst_field is None or worst_ratio <= 0:
        return None
    decades = math.inf if worst_ratio == math.inf else math.log10(worst_ratio)
    if decades <= orders:
        return None
    return {
        "kind": "residual-norm-contradiction",
        "severity": SEVERITY_FATAL,
        "action": DIVERGENCE_ACTION,
        "field": worst_field,
        "reference_field": reference_field,
        "orders_of_magnitude": decades,
        "threshold_orders": orders,
    }


# --------------------------------------------------------------------------
# S11. System operations allowed (configuration risk)
# --------------------------------------------------------------------------

# OpenFOAM announces this state itself, in two shapes. v2606 on the host wraps
# it in a warning:
#     --> FOAM Warning : allowSystemOperations : Allowing user-supplied system
#                        call operations.
# the older build inside the DAFoam container prints it bare, with no warning
# prefix at all:
#     allowSystemOperations : Allowing user-supplied system call operations
# The bare form is why this cannot ride on the S5 first-seen-warning rule: in
# the container that line is not a warning, so S5 never sees it.
SYSTEM_OPERATIONS = re.compile(
    r"allowSystemOperations\s*:\s*Allowing", re.IGNORECASE)

SYSTEM_OPERATIONS_ACTION = (
    "no number is in doubt; the host is. The case just ran with "
    "#codeStream / #calc / coded boundary conditions and the systemCall "
    "function object enabled, which means a case file can compile and run "
    "arbitrary code on this machine. Required for a named, vetted case, "
    "never for one that arrived from outside"
)


def detect_system_operations(line: str) -> dict[str, Any] | None:
    """The solver's own report that case-supplied code execution is enabled (S11).

    This is not banner text in the sense the Monitor Standard forbids matching
    (rule 3). ``argList`` prints it only inside ``if
    (dynamicCode::allowSystemOperations)`` — the line exists because the switch
    is on, so it is a measured state, exactly like a handler firing. With the
    switch off the solver prints "Disallowing" instead and this returns None.

    Severity is ``configuration risk``, not ``flag`` and not ``fatal``: the
    solve is unaffected, so calling it fatal would be false, and calling it
    "nothing fatal" hides that the box is executing case-supplied code.
    """
    if not SYSTEM_OPERATIONS.search(line):
        return None
    return {
        "kind": "system-operations-allowed",
        "severity": SEVERITY_CONFIGURATION_RISK,
        "action": SYSTEM_OPERATIONS_ACTION,
        "line": line.strip(),
    }


# --------------------------------------------------------------------------
# S4 bounding warnings: the severity ladder, and the key normaliser S5 shares
# --------------------------------------------------------------------------

# The startup window the Monitor Standard documented for S4 from version 1.1
# onward: WATCH inside it, FLAG past it. It is kept as a named constant because
# it was replayed and RETIRED on the measurement, and a retired threshold that
# leaves no trace gets reinvented. Over the 158 archived logs that carry a
# floor-bound message, 76 have an iteration axis to grade against, and this
# window calls 74 of those 76 FLAG. A rule that flags 97 percent of the lab's
# completed work is measuring the population, not the defect
# (VERIFICATION_CHARTER section 5, and the test S7 was withdrawn on).
BOUNDING_DOCUMENTED_STARTUP_FRACTION = 0.10

# The window actually in force. A bound is graded by whether it is still active
# in the final decile of the run -- the iterations the reported answer is read
# from. This is not a new threshold: it is the same ten percent, applied at the
# end of the run instead of the start, and it is the discriminator the S10a
# printInterval audit arrived at independently ("persistence to the final
# iterate is the discriminator this rule does not yet implement"). Replayed
# over the same 76 gradeable logs it separates 48 FLAG from 28 WATCH.
BOUNDING_FINAL_FRACTION = 0.90

BOUNDING_WATCH_ACTION = (
    "no action beyond the debrief count; the clipping had stopped well before "
    "the iterations the answer is read from, so the reported state is not a "
    "clipped state"
)
BOUNDING_FLAG_ACTION = (
    "mark the record and cap trust until resolved; the field was still being "
    "held physical by force at the iterations the reported quantity is read "
    "from, so the answer was read off a clipped state. Check the "
    "discretization and the turbulence initialization before trusting it"
)
BOUNDING_UNGRADED_ACTION = (
    "not graded, and deliberately not defaulted to either severity: this log "
    "prints no residual block, so it carries no iteration axis to place the "
    "clipping on. Re-run with residual printing on, or grade it by hand"
)


def grade_bounding_episode(field: str, event_iterations: Sequence[int],
                           iterations: int) -> dict[str, Any]:
    """Grade one field's floor-clipping episode in one log (Monitor Standard S4).

    ``event_iterations`` are the run's iteration numbers at which the solver
    printed a bounding message for ``field``; ``iterations`` is the total the
    run reached. Returns the episode as a finding -- one per field per log,
    rather than one per printed line -- carrying the span, the severity and
    the action.

    THE SEVERITY IS AN EPISODE PROPERTY AND CANNOT BE KNOWN WHILE STREAMING.
    Where a bound sits in a run is only meaningful against the length of the
    run, and a monitor reading line by line does not know that until the log
    ends. This is why the documented ladder was never implemented: there was
    nowhere in a streaming pass to put it. It is graded here, once, at the end.

    Two numbers from the archive replay are worth carrying next to this code:
    the documented "first ten percent" window flags 74 of the 76 gradeable
    logs, and the final-decile window in force flags 48. Both are measured over
    the same corpus by ``sdk/scripts/replay_monitor_rules.py``.

    A log with no iteration axis is returned UNGRADED rather than assigned a
    severity by default. 82 of the 158 archived bounding logs are in that state
    -- DAFoam runs that print ``Bounding nuTilda>...`` with no residual block --
    and guessing a severity for them would be inventing a finding.
    """
    events = list(event_iterations)
    count = len(events)
    first = min(events) if events else 0
    last = max(events) if events else 0
    finding: dict[str, Any] = {
        "kind": "bounding",
        "field": field,
        "events": count,
        "first_iteration": first,
        "last_iteration": last,
        "iterations": iterations,
    }
    if iterations <= 0:
        finding.update({
            "severity": "",
            "graded": False,
            "last_fraction": None,
            "persists_to_final_iterate": None,
            "action": BOUNDING_UNGRADED_ACTION,
        })
        return finding
    fraction = last / iterations
    persists = fraction >= BOUNDING_FINAL_FRACTION
    finding.update({
        "severity": SEVERITY_FLAG if persists else SEVERITY_WATCH,
        "graded": True,
        "last_fraction": fraction,
        "persists_to_final_iterate": persists,
        "action": BOUNDING_FLAG_ACTION if persists else BOUNDING_WATCH_ACTION,
        # Reported alongside, never used to grade. It is what the standard
        # documented before the replay retired it, and a reader comparing this
        # finding against version 1.1 of the standard needs to see both.
        "past_documented_startup_window": (
            last > BOUNDING_DOCUMENTED_STARTUP_FRACTION * iterations),
    })
    return finding


# The key normaliser S5 uses to decide whether it has seen a warning before.
#
# THE OLD PATTERN WAS ``[0-9.eE+-]+``, which is not a number pattern: it treats
# the letters e and E, the dot and the hyphen as number characters wherever
# they appear, with no digit required anywhere in the match. It rewrote
# ``allowSystemOperations`` to ``allowSyst#mOp#rations``, and any two warnings
# differing only in those characters keyed the same, so the second was
# suppressed as already seen. Measured over the lab's 449 archived logs, the
# whole vocabulary S5 could express was two keys.
#
# This pattern requires at least one digit, and refuses to match inside a word,
# so an identifier survives and a magnitude does not: ``at line 189`` and ``at
# line 185`` key the same, ``1e+16`` and ``2.4e-07`` key the same, and
# ``naca0012``, ``allowSystemOperations`` and ``fixA_kbounds`` are left alone.
_LOG_KEY_NUMBER = re.compile(
    r"(?<![A-Za-z0-9_])[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
    r"(?![A-Za-z0-9_])")


def normalise_log_key(text: str, limit: int = 200) -> str:
    """Collapse the varying magnitudes out of a log line, keeping the words.

    Used by S5 to tell one warning from another. Numbers are the part of a
    warning that changes between runs of the same warning; words are the part
    that identifies it. The old normaliser destroyed words too, which is why
    S5's vocabulary over the whole archive was two keys and both were defects
    of the key rather than facts about the logs.
    """
    return _LOG_KEY_NUMBER.sub("#", " ".join(text.split()))[:limit]
