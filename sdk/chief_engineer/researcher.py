"""The Chief Researcher's method-selection memo.

Before any optimization or study runs, the Chief Researcher puts a method choice
on the record: how the problem classifies, what strategy that classification
picks, what was rejected and why, and the condition under which the chosen
method is admissible. The memo is GENERATED FROM MISSION PROPERTIES, not
templated per geometry — a smooth low-dimensional design space and a single
mesh-gated body produce structurally similar but substantively different memos.

House transcript style: short and sweet, bullets, always. Each memo entry is
1–3 bullets of ≲14 words; no prose paragraphs. Method language only — the
reasoning is stated in terms of the mathematics (smoothness, gradients,
ensembles, regimes), never a tool or vendor.
"""

from __future__ import annotations

from dataclasses import dataclass


ENGINEER_ACK = "On it."

BULLET = "•"


def bullets(*items: str) -> str:
    """Join memo points into one bulleted transcript entry."""
    return " ".join(f"{BULLET} {item.rstrip('.')}." for item in items if item)


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


def _core_entry(p: MissionProperties) -> str:
    """Classification → strategy → rejected, as one 3-bullet entry."""
    if p.kind == "single-body-study":
        return bullets(
            f"Single fixed body, {p.regime} — a measurement, not an optimisation",
            "One gated solve; the only freedom is mesh and convergence",
            "Rejected: pricing by analogy (wrong wake); an ungated coarser mesh")
    if p.kind == "one-parameter-sweep":
        return bullets(
            f"One {p.smoothness} parameter, {p.regime} regime — a few anchors pin the curve",
            "Ensemble bracketing the range, fitted to a response surface",
            "Rejected: single point (prices one setting as the range); a fine grid (cost, no info)")
    # parametric-optimization
    if p.smoothness == "smooth" and p.regime.startswith("steady"):
        return bullets(
            f"Smooth {p.dimensionality}-parameter space, {p.regime} regime → map it, don't hunt it",
            "Ensemble sweep chosen; gradients admissible but unnecessary at this dimensionality",
            "Rejected: single point (blind to the trade); high-fidelity everywhere (cost, no info)")
    return bullets(
        f"{p.dimensionality}-parameter space, {p.regime} regime, {p.smoothness} objective",
        "Ensemble of steady evaluations, weighted toward the region that matters",
        "Rejected: single point (blind to the trade); exhaustive high fidelity (cost, no info)")


def _admissibility_entry(p: MissionProperties) -> str:
    if p.admissibility_cite:
        return bullets(
            f"Admissible {p.admissibility_cite} — a published threshold, not self-grading")
    if p.smoothness == "smooth" and p.regime.startswith("steady"):
        return bullets(
            "Admissible while smooth and steady hold — descent and ensemble read the same surface",
            f"Model fidelity ({p.fidelity}) caps the tier, not the search")
    return bullets(
        f"Valid while the regime stays {p.regime}; outside it, trend only")


def method_memo(p: MissionProperties) -> list[str]:
    """The Chief Researcher memo: one core entry, one admissibility entry."""
    return [_core_entry(p), _admissibility_entry(p)]
