"""The seam between a worker and the engineering tool it drives.

``SimulationApi`` is the contract every solver adapter satisfies: hand it a
design and a list of analyses, get structured metrics back. The real adapters
(the OpenFOAM cylinder solver, the geometry-study pipeline) live in their own
modules; this file holds the protocol plus one lightweight synthetic evaluator
used for local development and for exercising the worker fleet without spinning
up a mesh.
"""

from __future__ import annotations

import time
from typing import Any, Callable, Mapping, Protocol, Sequence

# A worker may push incremental progress dicts back to the control room.
ProgressSink = Callable[[dict[str, Any]], None]


class SimulationApi(Protocol):
    """What a worker needs from any engineering tool: evaluate, close, artifacts."""

    def evaluate(self, design: Mapping[str, float],
                 analyses: Sequence[str]) -> Mapping[str, float]:
        ...

    def close(self) -> None:
        ...

    def artifacts(self) -> list[dict[str, Any]]:
        ...


# Reference wing geometry the synthetic evaluator perturbs around.
_BASELINE_WING = {
    "wing_span": 10.0,
    "wing_sweep": 25.0,
    "wing_taper": 0.55,
    "wing_twist": -1.0,
    "htail_span": 7.0,
    "htail_area": 8.0,
    "htail_arm": 5.0,
    "cg_shift": 0.0,
    "skin_thickness": 0.08,
}


class SyntheticApi:
    """A deterministic stand-in evaluator — analytic, not a physics solver.

    It maps a wing design to a repeatable set of aero/stability/mass numbers so
    the orchestration and the worker fleet can be developed and tested without a
    real solve. The relationships are the textbook ones (lift-to-drag climbs with
    aspect ratio, parasite drag grows with sweep, tail volume sets static margin)
    but the constants are illustrative, not calibrated.
    """

    def __init__(self, defaults: Mapping[str, float] | None = None,
                 latency_s: float = 0.0):
        self.baseline = dict(_BASELINE_WING)
        if defaults:
            self.baseline.update({k: float(v) for k, v in defaults.items()})
        self.latency_s = max(0.0, float(latency_s))

    def evaluate(self, design: Mapping[str, float],
                 analyses: Sequence[str]) -> Mapping[str, float]:
        if self.latency_s:
            time.sleep(self.latency_s)
        wing = {**self.baseline, **{k: float(v) for k, v in design.items()}}

        aspect_ratio = wing["wing_span"] ** 2 / 48.0
        drag = (0.017
                + 0.045 / max(aspect_ratio, 0.1)
                + 0.00018 * (wing["wing_sweep"] - 20.0) ** 2
                + 0.0005 * (wing["wing_twist"] + 1.0) ** 2)
        lift = (0.52
                + 0.002 * (wing["wing_span"] - 10.0)
                - 0.001 * abs(wing["wing_sweep"] - 25.0))

        tail_volume = wing["htail_area"] * (wing["htail_span"] / self.baseline["htail_span"])
        static_margin = 0.015 * tail_volume * wing["htail_arm"] - 0.025 * wing["cg_shift"] - 0.06
        mass = (400.0
                + 18.0 * wing["wing_span"]
                + 2.6 * tail_volume
                + 120.0 * wing["skin_thickness"])

        return {
            "L_D": round(lift / drag, 6),
            "CL": round(lift, 6),
            "CD": round(drag, 6),
            "static_margin": round(static_margin, 6),
            "mass": round(mass, 6),
            "wing_span": wing["wing_span"],
        }

    def close(self) -> None:
        return None

    def artifacts(self) -> list[dict[str, Any]]:
        return []
