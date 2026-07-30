"""Chief Researcher: governs approximations, not execution.

Two decisions, deliberately narrow:

**Decision A — run selection under scarcity.**  When the compute audit says
the requested fan-out does not fit, the Chief Researcher picks which runs are
worth full-fidelity solver time.  The strategy is bracket-and-centre: anchor
on the incumbent, bracket the range of the most influential parameters (the
ends carry the most information about a monotone trend), then take an interior
point that exposes curvature.  Everything not selected is covered by the
reduced-order ensemble the Chief Engineer fits to those anchors.

**Decision B — closure approval.**  Certonomous only applies a closure model
where that model has been *calibrated and validated on this repository's own
evidence*.  The registry below carries validity envelopes taken from real runs
(see ``docs/NUMERICS_KNOWLEDGE.md``).  Outside an envelope the answer is no,
and the rejection carries orders: run coarse, state the uncertainty loudly,
and execute the diagnostics that shrink it.

Both decisions return structured objects that render as named transcript
entries with rationale and citations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

KNOWLEDGE = "the numerics knowledge base"
LESSONS = "the lab's lessons memory"


# --------------------------------------------------------------------------
# Decision A — run selection under scarcity
# --------------------------------------------------------------------------

@dataclass
class SelectedRun:
    name: str
    design: dict[str, float]
    rationale: str

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "design": dict(self.design), "rationale": self.rationale}


@dataclass
class RunSelection:
    runs: list[SelectedRun]
    covered_by_rom: int
    strategy: str
    citations: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "runs": [run.as_dict() for run in self.runs],
            "covered_by_rom": self.covered_by_rom,
            "strategy": self.strategy,
            "citations": list(self.citations),
        }

    def headline(self) -> str:
        return (
            f"Selected {len(self.runs)} full-fidelity run(s) under the compute "
            f"constraint; the remaining {self.covered_by_rom} design(s) will be "
            f"covered by a reduced-order ensemble fitted to these anchors. "
            f"Strategy: {self.strategy}"
        )


def select_runs(baseline: dict[str, float],
                parameters: Sequence[Any],
                *, capacity: int, requested: int,
                objective: str = "the objective") -> RunSelection:
    """Pick the most informative ``capacity`` runs from a larger sweep.

    ``parameters`` are adapter-declared ``ParameterSpec``-like records
    (``name``, ``minimum``, ``maximum``, optional ``description``).  Selection
    order — anchor, then brackets of each parameter by declared influence,
    then an interior point — is the classical screening design: with a tiny
    budget, the ends of a range identify a trend and the centre exposes
    curvature, which is exactly what a surrogate needs to interpolate the
    designs that never get solved.
    """
    budget = max(1, int(capacity))
    runs: list[SelectedRun] = [SelectedRun(
        "anchor", dict(baseline),
        "Incumbent design, anchors the surrogate and gives every later run a "
        "reference to be compared against.",
    )]

    # Widest declared range first: the parameter with the most room to move is
    # the one a screening design can least afford to leave unsampled.
    ordered = sorted(
        parameters,
        key=lambda spec: (float(spec.maximum) - float(spec.minimum))
        / max(abs(float(baseline.get(spec.name, spec.minimum))), 1e-9),
        reverse=True,
    )

    for spec in ordered:
        if len(runs) >= budget:
            break
        name = spec.name
        low, high = float(spec.minimum), float(spec.maximum)
        current = float(baseline.get(name, (low + high) / 2))
        # Bracket within the declared bounds, stepping far enough to separate
        # signal from solver noise but staying inside validated territory.
        lo_value = max(low, current - 0.35 * (current - low)) if current > low else low
        hi_value = min(high, current + 0.35 * (high - current)) if current < high else high
        for value, side in ((lo_value, "lower"), (hi_value, "upper")):
            if len(runs) >= budget or abs(value - current) < 1e-12:
                continue
            runs.append(SelectedRun(
                f"{name}-{side}",
                {**baseline, name: value},
                f"Brackets {name} on the {side} side ({current:.4g} to {value:.4g}) "
                f"to establish the sign and slope of its effect on {objective} "
                f"before any surrogate is trusted to interpolate it.",
            ))

    if len(runs) < budget and ordered:
        spec = ordered[0]
        midpoint = (float(spec.minimum) + float(spec.maximum)) / 2
        runs.append(SelectedRun(
            f"{spec.name}-interior", {**baseline, spec.name: midpoint},
            f"Interior point on {spec.name}: three levels are the minimum that "
            f"can distinguish curvature from a straight line, which decides "
            f"whether the ensemble may extrapolate or must stay inside the hull.",
        ))

    runs = runs[:budget]
    return RunSelection(
        runs=runs,
        covered_by_rom=max(0, requested - len(runs)),
        strategy="bracket-and-centre screening, widest relative range first",
        citations=(f"{KNOWLEDGE} #2 (grid-convergence evidence)",
                   f"{LESSONS} L-001 (sample until irreducible)"),
    )


# --------------------------------------------------------------------------
# Decision B — closure approval
# --------------------------------------------------------------------------

@dataclass
class ClosureModel:
    """A correction calibrated on this repository's own validated runs."""
    name: str
    quantity: str
    correction: str
    calibration: str
    citation: str
    regime: dict[str, Any]


# Calibrated from the Re = 20 grid study recorded in NUMERICS_KNOWLEDGE.md #2:
# Cd 2.191 (600 cells) → 2.156 (asymptote, 21600 cells) = +1.6% coarse-grid bias.
CLOSURE_REGISTRY: tuple[ClosureModel, ...] = (
    ClosureModel(
        name="coarse-grid-cylinder-Cd",
        quantity="Cd",
        correction="multiply coarse-grid Cd by 0.984 (remove the measured "
                   "+1.6% coarse-grid bias)",
        calibration="Re = 20 grid study, 600 to 21600 cells, Cd 2.191 to 2.156",
        citation=f"{KNOWLEDGE} #2 (grid convergence, this machine)",
        regime={"geometry": "cylinder-2d", "flow": "steady-laminar",
                "reynolds": (5.0, 47.0), "cells": (600, 21600)},
    ),
)


@dataclass
class ClosureDecision:
    approved: bool
    model: ClosureModel | None
    rationale: str
    citations: tuple[str, ...]
    orders: tuple[str, ...] = ()
    uncertainty_language: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "approved": self.approved,
            "model": self.model.name if self.model else None,
            "rationale": self.rationale,
            "citations": list(self.citations),
            "orders": list(self.orders),
            "uncertainty_language": self.uncertainty_language,
        }

    def headline(self) -> str:
        verdict = "APPROVED" if self.approved else "REJECTED"
        model = f" [{self.model.name}]" if self.model else ""
        return f"Closure {verdict}{model}: {self.rationale}"


def approve_closure(*, geometry: str, flow: str, reynolds: float,
                    cells: int, deadline_minutes: float | None = None) -> ClosureDecision:
    """Approve or reject closure-model use for one time-constrained case."""
    for model in CLOSURE_REGISTRY:
        regime = model.regime
        if regime["geometry"] != geometry or regime["flow"] != flow:
            continue
        re_lo, re_hi = regime["reynolds"]
        cell_lo, cell_hi = regime["cells"]
        if not (re_lo <= reynolds <= re_hi):
            return ClosureDecision(
                approved=False, model=None,
                rationale=(
                    f"Re = {reynolds:.0f} is outside the validated envelope "
                    f"[{re_lo:.0f}, {re_hi:.0f}] of {model.name!r}. Above Re ≈ 47 the "
                    f"steady wake is unstable: a converged steady solve lands on a "
                    f"branch the physical flow does not follow, so a correction "
                    f"calibrated in the steady regime would transfer a bias of "
                    f"unknown sign. No closure."),
                citations=(f"{KNOWLEDGE} #3 (convergence ≠ physical validity)",
                           f"{KNOWLEDGE} #4 (degradation past the regime)"),
                orders=(
                    "Run the coarse mesh as requested to respect the deadline.",
                    "Report the result with an explicitly widened envelope and "
                    "the regime caveat stated in the headline, not a footnote.",
                    "Run the grid-sensitivity probe (one refinement step) to "
                    "measure, not guess, the discretization component.",
                    "Run the oscillation diagnostic on the coefficient history "
                    "to detect unsteadiness the steady solver is suppressing.",
                ),
                uncertainty_language=(
                    "UNVALIDATED REGIME: the number is reported with a widened "
                    "envelope and an explicit warning; treat magnitudes as "
                    "bounded by the stated grid difference until an unsteady run "
                    "confirms it."),
            )
        if not (cell_lo <= cells <= cell_hi):
            return ClosureDecision(
                approved=False, model=None,
                rationale=(
                    f"{cells} cells is outside the calibration range "
                    f"[{cell_lo}, {cell_hi}] of {model.name!r}; the correction was "
                    f"never measured at this resolution and extrapolating a "
                    f"discretization bias is exactly the error it exists to fix."),
                citations=(f"{KNOWLEDGE} #2 (grid convergence)",),
                orders=(
                    "Run coarse, report with a widened envelope.",
                    "Run the grid-sensitivity probe to calibrate this resolution "
                    "so the closure becomes usable next time.",
                ),
                uncertainty_language=(
                    "UNCALIBRATED RESOLUTION: envelope widened; the probe result "
                    "will convert this into a measured correction."),
            )
        return ClosureDecision(
            approved=True, model=model,
            rationale=(
                f"Case sits inside the validated envelope of {model.name!r} "
                f"(Re {re_lo:.0f} to {re_hi:.0f}, {cell_lo} to {cell_hi} cells, {flow}). "
                f"The correction is not a fitted guess: it was measured on this "
                f"machine ({model.calibration}). Applying it removes a known bias "
                f"instead of leaving it in the answer."
                + (f" Deadline {deadline_minutes:.0f} min is met by the coarse mesh "
                   f"plus correction." if deadline_minutes else "")),
            citations=(model.citation,),
            orders=(f"Apply {model.name}: {model.correction}.",
                    "Report the corrected value with the residual calibration "
                    "spread folded into the envelope."),
            uncertainty_language=(
                "VALIDATED CLOSURE: corrected value reported with the "
                "calibration residual included in the envelope; the coarse mesh "
                "costs speed, not trust."),
        )

    return ClosureDecision(
        approved=False, model=None,
        rationale=(f"No closure model in the registry covers "
                   f"{geometry}/{flow}. Certonomous does not invent corrections "
                   f"for regimes it has never measured."),
        citations=(f"{KNOWLEDGE} (registry)",),
        orders=("Run coarse and report with an explicitly widened envelope.",
                "Run the grid-sensitivity probe to begin calibrating a closure "
                "for this configuration."),
        uncertainty_language=(
            "NO CALIBRATION AVAILABLE: envelope widened and flagged; this run "
            "becomes the first calibration point for this configuration."),
    )
