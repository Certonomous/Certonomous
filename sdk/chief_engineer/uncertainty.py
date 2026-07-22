"""Epistemic uncertainty quantification for chief-engineer missions.

Every mission already produces an ensemble of solver evaluations at different
designs.  This layer treats that evidence as training data for a Gaussian
process surrogate per metric and reports how well the design region around a
chosen design (usually the winner) is actually pinned down: the calibrated GP
posterior spread is the *epistemic* uncertainty — what the mission's evidence
does not determine — as opposed to solver noise, which is negligible for the
deterministic backends Certonomous drives.

The layer is pure standard library, deterministic, and inspectable, matching
the rest of the chief kernel: no numpy, no sampling, no hidden state.  The
chief narrates the result per metric — "here I am sure / here I am NOT sure" —
always with the numbers attached.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Mapping, Sequence

from .models import MetricSpec, ParameterSpec

CONFIDENCE_SURE = "sure"
CONFIDENCE_MODERATE = "moderately-sure"
CONFIDENCE_UNSURE = "not-sure"
CONFIDENCE_UNKNOWN = "insufficient-evidence"

# Relative epistemic spread thresholds for the confidence verdicts.
_SURE_BELOW = 0.02
_MODERATE_BELOW = 0.10
# Minimum distinct designs before a surrogate assessment is attempted.
_MIN_SAMPLES = 4
# Probe offset around the assessed design, as a fraction of each normalized
# design-space dimension: the neighborhood the chief's claim is about.
_PROBE_DELTA = 0.10


@dataclass(frozen=True)
class MetricUncertainty:
    """Calibrated epistemic uncertainty of one metric at one design."""

    metric: str
    value: float
    std: float
    ci95: tuple[float, float]
    relative: float
    confidence: str
    n_samples: int
    unit: str = ""
    statement: str = ""

    def as_dict(self) -> dict:
        return {
            "metric": self.metric,
            "value": self.value,
            "std": self.std,
            "ci95": [self.ci95[0], self.ci95[1]],
            "relative": self.relative,
            "confidence": self.confidence,
            "n_samples": self.n_samples,
            "unit": self.unit,
            "statement": self.statement,
        }


@dataclass(frozen=True)
class UncertaintyReport:
    """Per-metric epistemic uncertainty plus the chief's spoken verdict."""

    design_id: str
    n_designs: int
    metrics: tuple[MetricUncertainty, ...]
    thin_directions: tuple[str, ...]
    narration: str

    def as_dict(self) -> dict:
        return {
            "design_id": self.design_id,
            "n_designs": self.n_designs,
            "metrics": [item.as_dict() for item in self.metrics],
            "thin_directions": list(self.thin_directions),
            "narration": self.narration,
        }


def assess(
    samples: Sequence[tuple[Mapping[str, float], Mapping[str, float]]],
    at_design: Mapping[str, float],
    at_metrics: Mapping[str, float],
    *,
    design_id: str = "winner",
    parameter_specs: Sequence[ParameterSpec] = (),
    metric_specs: Sequence[MetricSpec] = (),
    metric_names: Sequence[str] | None = None,
) -> UncertaintyReport:
    """Assess epistemic uncertainty at ``at_design`` from mission evidence.

    ``samples`` is the mission's evidence pool: (design, metrics) pairs from
    every successful solver evaluation.  Metrics that name design parameters
    are skipped — inputs the mission set directly carry no epistemic spread.
    """
    parameter_names = {spec.name for spec in parameter_specs}
    units = {spec.name: spec.unit for spec in metric_specs}
    names = [
        name for name in (metric_names or list(at_metrics))
        if name not in parameter_names and name not in at_design
    ]

    dims, points, rows = _design_matrix(samples, at_design, parameter_specs)
    target = _normalize_point(at_design, dims)
    n_designs = len(points)

    assessments: list[MetricUncertainty] = []
    for name in names:
        value = float(at_metrics[name])
        observed = [
            (points[index], float(metrics[name]))
            for index, (_design, metrics) in enumerate(rows)
            if name in metrics
        ]
        assessments.append(_assess_metric(
            name, value, observed, target, units.get(name, ""),
        ))

    thin = _thin_directions(dims, points, target) if len(points) >= _MIN_SAMPLES else ()
    narration = _narrate(design_id, n_designs, assessments, thin)
    return UncertaintyReport(design_id, n_designs, tuple(assessments), thin, narration)


# --------------------------------------------------------------------------
# Evidence geometry
# --------------------------------------------------------------------------

def _design_matrix(samples, at_design, parameter_specs):
    """Normalize evidence designs to the unit box over the varying dimensions.

    Bounds come from adapter-declared parameter specs when available and from
    the observed evidence extent otherwise.  Dimensions that never vary are
    dropped; duplicate design points keep their first observation (the solver
    backends are deterministic).
    """
    declared = {spec.name: (spec.minimum, spec.maximum) for spec in parameter_specs}
    keys: list[str] = []
    for design, _metrics in list(samples) + [(at_design, {})]:
        for key in design:
            if key not in keys:
                keys.append(key)

    bounds: dict[str, tuple[float, float]] = {}
    for key in keys:
        observed = [float(design[key]) for design, _ in samples if key in design]
        if key in at_design:
            observed.append(float(at_design[key]))
        low, high = declared.get(key, (min(observed), max(observed)))
        if key not in declared and high - low <= 0.0:
            continue
        if high - low <= 0.0:
            continue
        bounds[key] = (float(low), float(high))
    dims = {key: span for key, span in bounds.items()}

    points: list[list[float]] = []
    rows: list[tuple[Mapping[str, float], Mapping[str, float]]] = []
    seen: set[tuple[float, ...]] = set()
    for design, metrics in samples:
        point = _normalize_point(design, dims)
        key = tuple(round(coordinate, 9) for coordinate in point)
        if key in seen:
            continue
        seen.add(key)
        points.append(point)
        rows.append((design, metrics))
    return dims, points, rows


def _normalize_point(design: Mapping[str, float], dims: Mapping[str, tuple[float, float]]):
    point = []
    for key, (low, high) in dims.items():
        raw = float(design.get(key, low))
        point.append((raw - low) / (high - low))
    return point


def _thin_directions(dims, points, target):
    """Dimensions where the evidence around the assessed design is weak."""
    thin: list[str] = []
    for axis, key in enumerate(dims):
        coordinates = sorted(point[axis] for point in points)
        distinct = len({round(value, 6) for value in coordinates})
        span = coordinates[-1] - coordinates[0]
        near_edge = span > 0.0 and (
            target[axis] <= coordinates[0] + 0.1 * span
            or target[axis] >= coordinates[-1] - 0.1 * span
        )
        if distinct < 3 or near_edge:
            thin.append(key)
    return tuple(thin)


# --------------------------------------------------------------------------
# Gaussian-process surrogate (pure stdlib, small-n)
# --------------------------------------------------------------------------

def _assess_metric(name, value, observed, target, unit):
    n = len(observed)
    scale = _relative_scale(value, [y for _x, y in observed])
    if n < _MIN_SAMPLES:
        spread = _population_std([y for _x, y in observed]) if n > 1 else 0.0
        return MetricUncertainty(
            metric=name, value=value, std=spread,
            ci95=(value - 1.96 * spread, value + 1.96 * spread),
            relative=spread / scale, confidence=CONFIDENCE_UNKNOWN,
            n_samples=n, unit=unit,
            statement=(
                f"I cannot quantify my uncertainty on {name} yet — "
                f"only {n} evaluation{'s' if n != 1 else ''} in evidence."
            ),
        )

    xs = [x for x, _y in observed]
    ys = [y for _x, y in observed]
    std = _gp_local_std(xs, ys, target)
    relative = std / scale
    confidence = (
        CONFIDENCE_SURE if relative < _SURE_BELOW
        else CONFIDENCE_MODERATE if relative < _MODERATE_BELOW
        else CONFIDENCE_UNSURE
    )
    ci = (value - 1.96 * std, value + 1.96 * std)
    body = (
        f"{name} = {_fmt(value)}{_unit(unit)} ± {_fmt(std)} "
        f"({relative * 100.0:.1f}%, 95% CI [{_fmt(ci[0])}, {_fmt(ci[1])}], n={n})"
    )
    if confidence == CONFIDENCE_SURE:
        statement = f"Here I am sure: {body}."
    elif confidence == CONFIDENCE_MODERATE:
        statement = f"Here I am fairly sure: {body}."
    else:
        statement = f"Here I am NOT sure: {body} — treat this number as provisional."
    return MetricUncertainty(name, value, std, ci, relative, confidence, n, unit, statement)


def _gp_local_std(xs, ys, target):
    """Calibrated GP posterior spread in the neighborhood of ``target``.

    Squared-exponential kernel on the normalized design box; lengthscale from
    the median pairwise distance; signal variance from the evidence variance;
    leave-one-out z-scores inflate the posterior when the surrogate is
    overconfident.  The reported number is the RMS posterior standard
    deviation over axis-aligned probes one ``_PROBE_DELTA`` away from the
    assessed design — the region the chief's verdict is about.
    """
    n = len(xs)
    mean_y = sum(ys) / n
    centered = [y - mean_y for y in ys]
    signal = max(_population_std(ys) ** 2, 1e-18)
    lengthscale = _median_distance(xs)
    nugget = signal * 1e-6 + 1e-15

    kernel = [
        [signal * _rbf(xs[i], xs[j], lengthscale) + (nugget if i == j else 0.0) for j in range(n)]
        for i in range(n)
    ]
    lower = _cholesky(kernel)
    alpha = _solve_upper(_transpose(lower), _solve_lower(lower, centered))
    inverse_diagonal = _inverse_diagonal(lower)
    inflation = _loo_inflation(alpha, inverse_diagonal)

    probes = _probe_points(target)
    variances = []
    for probe in probes:
        cross = [signal * _rbf(probe, xs[i], lengthscale) for i in range(n)]
        intermediate = _solve_lower(lower, cross)
        variance = signal - sum(value * value for value in intermediate)
        variances.append(max(variance, 0.0))
    return math.sqrt(sum(variances) / len(variances)) * inflation


def _probe_points(target):
    probes = []
    for axis in range(len(target)):
        for direction in (-_PROBE_DELTA, _PROBE_DELTA):
            probe = list(target)
            probe[axis] = min(1.0, max(0.0, probe[axis] + direction))
            probes.append(probe)
    return probes or [list(target)]


def _loo_inflation(alpha, inverse_diagonal):
    """Leave-one-out calibration factor: >1 when the GP is overconfident."""
    scores = []
    for residual_scaled, precision in zip(alpha, inverse_diagonal):
        if precision <= 0.0:
            continue
        residual = residual_scaled / precision
        variance = 1.0 / precision
        scores.append(residual * residual / variance)
    if not scores:
        return 1.0
    return max(1.0, math.sqrt(sum(scores) / len(scores)))


def _rbf(a, b, lengthscale):
    distance2 = sum((u - v) ** 2 for u, v in zip(a, b))
    return math.exp(-0.5 * distance2 / (lengthscale * lengthscale))


def _median_distance(xs):
    """Kernel lengthscale from the median nearest-neighbor spacing.

    Nearest-neighbor spacing tracks how densely the evidence tiles the design
    box; a global pairwise median would stretch the lengthscale across empty
    gaps and make the surrogate confidently interpolate regions it has never
    seen.  The 3x factor keeps neighboring samples correlated without bridging
    unexplored territory.
    """
    nearest = []
    for i in range(len(xs)):
        best = None
        for j in range(len(xs)):
            if i == j:
                continue
            distance = math.sqrt(sum((u - v) ** 2 for u, v in zip(xs[i], xs[j])))
            if distance > 0.0 and (best is None or distance < best):
                best = distance
        if best is not None:
            nearest.append(best)
    if not nearest:
        return 0.5
    nearest.sort()
    spacing = nearest[len(nearest) // 2]
    return min(max(3.0 * spacing, 1e-3), 1.0)


# --------------------------------------------------------------------------
# Small dense linear algebra
# --------------------------------------------------------------------------

def _cholesky(matrix):
    n = len(matrix)
    lower = [[0.0] * n for _ in range(n)]
    jitter = 0.0
    for attempt in range(6):
        try:
            for i in range(n):
                for j in range(i + 1):
                    accumulated = sum(lower[i][k] * lower[j][k] for k in range(j))
                    if i == j:
                        pivot = matrix[i][i] + jitter - accumulated
                        if pivot <= 0.0:
                            raise ArithmeticError("matrix is not positive definite")
                        lower[i][j] = math.sqrt(pivot)
                    else:
                        lower[i][j] = (matrix[i][j] - accumulated) / lower[j][j]
            return lower
        except ArithmeticError:
            jitter = (jitter or 1e-12) * 100.0
            lower = [[0.0] * n for _ in range(n)]
    raise ArithmeticError("Cholesky factorization failed after jitter escalation")


def _solve_lower(lower, rhs):
    n = len(rhs)
    solution = [0.0] * n
    for i in range(n):
        solution[i] = (rhs[i] - sum(lower[i][k] * solution[k] for k in range(i))) / lower[i][i]
    return solution


def _solve_upper(upper, rhs):
    n = len(rhs)
    solution = [0.0] * n
    for i in reversed(range(n)):
        solution[i] = (rhs[i] - sum(upper[i][k] * solution[k] for k in range(i + 1, n))) / upper[i][i]
    return solution


def _transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def _inverse_diagonal(lower):
    """Diagonal of K^-1 from its Cholesky factor."""
    n = len(lower)
    diagonal = [0.0] * n
    identity_column = [0.0] * n
    for j in range(n):
        for k in range(n):
            identity_column[k] = 1.0 if k == j else 0.0
        column = _solve_upper(_transpose(lower), _solve_lower(lower, list(identity_column)))
        diagonal[j] = column[j]
    return diagonal


# --------------------------------------------------------------------------
# Verdicts and narration
# --------------------------------------------------------------------------

def _relative_scale(value, ys):
    span = (max(ys) - min(ys)) if ys else 0.0
    return max(abs(value), 0.01 * span, 1e-12)


def _population_std(ys):
    n = len(ys)
    if n < 2:
        return 0.0
    mean = sum(ys) / n
    return math.sqrt(sum((y - mean) ** 2 for y in ys) / (n - 1))


def _fmt(value: float) -> str:
    if value == 0.0:
        return "0"
    magnitude = abs(value)
    if magnitude >= 1000.0 or magnitude < 1e-3:
        return f"{value:.3g}"
    return f"{value:.4g}"


def _unit(unit: str) -> str:
    return f" {unit}" if unit else ""


def _narrate(design_id, n_designs, assessments, thin_directions):
    if not assessments:
        return (
            f"No output metrics were available to assess for {design_id}; "
            "epistemic uncertainty is unquantified."
        )
    ordered = sorted(assessments, key=lambda item: (
        [CONFIDENCE_SURE, CONFIDENCE_MODERATE, CONFIDENCE_UNSURE, CONFIDENCE_UNKNOWN]
        .index(item.confidence)
    ))
    lines = [
        f"Uncertainty assessment for {design_id} from {n_designs} evaluated designs:"
    ]
    lines.extend(item.statement for item in ordered)
    if thin_directions:
        listed = ", ".join(thin_directions)
        lines.append(
            f"Evidence is thin along {listed} — sampling there would tighten these bounds."
        )
    return " ".join(lines)
