"""The Chief Researcher's method-selection memo.

Before any optimization or study runs, the Chief Researcher puts a method choice
on the record: how the problem classifies, what strategy that classification
picks, what was rejected and why, and the condition under which the chosen
method is admissible. The memo is GENERATED FROM MISSION PROPERTIES, not
templated per geometry — a smooth low-dimensional design space and a single
mesh-gated body produce structurally similar but substantively different memos.

The generator returns plain researcher lines; the workflow emits them as
CHIEF RESEARCHER transcript entries, and the Chief Engineer answers ``ENGINEER_ACK``.
Method language only — the reasoning is stated in terms of the mathematics
(smoothness, gradients, ensembles, regimes), never a tool or vendor.
"""

from __future__ import annotations

from dataclasses import dataclass, field


ENGINEER_ACK = "On it."


@dataclass
class MissionProperties:
    """What the mission IS, in the terms the method choice turns on."""

    # "parametric-optimization" | "single-body-study" | "one-parameter-sweep"
    kind: str
    objective: str                       # human phrase, e.g. "maximise lift-to-drag"
    dimensionality: int                  # count of free design parameters (0 = a fixed body)
    regime: str                          # e.g. "steady", "steady turbulent (RANS)"
    smoothness: str                      # "smooth" | "gated" | "discrete"
    fidelity: str                        # e.g. "a conceptual sizing model", "a solved field"
    constraints: tuple[str, ...] = ()    # human-language constraint names
    # An admissibility condition already sourced by the caller from the physics
    # rules or the knowledge base (e.g. "per the mesh-quality acceptance band").
    # Left empty, the memo falls back to the method-terms basis for the regime.
    admissibility_cite: str = ""


def _classification(p: MissionProperties) -> str:
    if p.kind == "single-body-study":
        return (
            f"Problem classification: a single fixed body, {p.regime} — no design "
            f"space to search, so this is a measurement, not an optimisation. The "
            f"only freedom is numerical: the mesh and the convergence of one solve.")
    dims = (f"{p.dimensionality}-parameter" if p.dimensionality else "fixed")
    return (
        f"Problem classification: a {dims} design space, {p.regime}, and {p.smoothness} "
        f"in the objective. That combination is what picks the method — a "
        f"{p.smoothness} response over a handful of variables is mapped, not hunted.")


def _strategy(p: MissionProperties) -> str:
    if p.kind == "single-body-study":
        return (
            "Chosen strategy: one steady solve on the body, gated on mesh quality, "
            "with the force read from a settled window. There is nothing to "
            "optimise — the method question is only whether the discretisation is "
            "good enough to believe the number.")
    if p.kind == "one-parameter-sweep":
        return (
            "Chosen strategy: an ensemble of steady solves bracketing the single "
            "parameter, fitted to a response surface. One variable and a smooth "
            "regime means a few real points pin the curve; the surface covers the "
            "rest for free.")
    # parametric-optimization
    if p.smoothness == "smooth" and p.regime.startswith("steady"):
        return (
            "Chosen strategy: an ensemble of steady evaluations across the design "
            "space. The space is smooth and the regime steady, so the gradient is "
            "cheap and admissible — backpropagation would descend it directly; at "
            "this dimensionality a direct ensemble sweep maps the whole trade "
            "without needing to, and it shows the losers as well as the winner.")
    return (
        "Chosen strategy: an ensemble of steady evaluations across the design "
        "space, weighted toward the region the objective cares about.")


def _rejected(p: MissionProperties) -> str:
    if p.kind == "single-body-study":
        return (
            "Rejected: pricing this body by analogy from a nearer one we have "
            "solved — it is not this geometry, and the wake is where bodies differ. "
            "Rejected: a coarser mesh to save time — it would leave the number "
            "ungated, which is the one thing this study exists to check.")
    if p.kind == "one-parameter-sweep":
        return (
            "Rejected: a single design point — it prices one setting as the whole "
            "range and is blind to the trade. Rejected: a fine grid of real solves "
            "across the parameter — unaffordable and unnecessary when a smooth "
            "curve is fixed by a few bracketing anchors.")
    return (
        "Rejected: a single design point — blind to the trade the mission is "
        "asking about. Rejected: an unsteady or high-fidelity solve at every "
        "candidate — the space is smooth and steady, so that fidelity buys nothing "
        "the ensemble does not already resolve, at many times the cost.")


def _admissibility(p: MissionProperties) -> str:
    if p.admissibility_cite:
        return (
            f"Admissibility: the method holds {p.admissibility_cite} — the "
            f"condition is external and stated up front, so the mesh (or the model) "
            f"is judged against a published threshold, not against whatever it "
            f"happens to produce.")
    if p.smoothness == "smooth" and p.regime.startswith("steady"):
        return (
            "Admissibility: this rests on the design space being smooth and the "
            "regime steady — the local linearisation the gradient relies on holds, "
            "so the ensemble and any descent over it read the same surface. Where "
            "the model itself is reduced ("
            f"{p.fidelity}), that caps the tier, not the search.")
    return (
        f"Admissibility: stated in method terms — the approximation is valid while "
        f"the regime stays {p.regime}; outside it the result is a trend, not a "
        f"magnitude, and the tier is capped to say so.")


def method_memo(p: MissionProperties) -> list[str]:
    """The ordered Chief Researcher memo lines for this mission."""
    return [_classification(p), _strategy(p), _rejected(p), _admissibility(p)]
