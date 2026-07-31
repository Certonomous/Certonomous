"""Validation-hierarchy tiers and the credibility scorecard.

Two approved agenda items live here, and they answer the same question from
two directions: what is the ceiling on the trust this result may carry, and
what does the fidelity chip not tell you about it.

**r1-validation-tier-labels.** Oberkampf and Trucano organize validation as a
building-block hierarchy: unit problems, benchmark cases, subsystem cases,
complete system. The quantity and accuracy of experimental information
degrades radically up the tiers, with complete-system data essentially always
very limited. Labelling a case with its tier states *structurally* why it
stops where it stops. The airliner does not sit below VALIDATED because
someone hedged; it sits there because complete-system validation data barely
exists, and that is a fact about the world rather than about our solver.

**r1-credibility-scorecard.** Mapping the lab's four chips onto NASA-STD-7009B
shows the chips already encode validation status, solver backing and
convergence. Two of the standard's results-assessment factors are invisible:
input pedigree, so a run on poorly traced inputs can wear the same chip as one
on measured inputs, and results robustness, so sensitivity knowledge never
reaches the certificate. This module scores both on the standard's 0 to 4
scale.

WHAT IS QUOTED AND WHAT IS OURS
-------------------------------
Honesty about provenance matters more here than anywhere, because the whole
point of the module is stating how well things are known.

- The tier NAMES and the claim that data quality degrades up the tiers are
  Oberkampf and Trucano's. The lab's portfolio mapping (cylinder as a unit
  problem, flat plate and motorcycle as benchmark cases, valve as a subsystem
  case, airliner as complete system) is recorded in the lab's own reading of
  that report; the remaining bodies are placed here by the same construction,
  and every entry carries its basis.
- The 0 to 4 scale, the two factor names, and requirement M&S 26 placarding
  are NASA-STD-7009B's. **The level definitions in ``PEDIGREE_LEVELS`` and
  ``ROBUSTNESS_LEVELS`` are the lab's own mapping onto that scale, not
  quotations from the standard.** The lab's reading records the shape of the
  standard's leveling (robustness levels turn on how many key sensitivities
  are actually known) but not its clause-by-clause wording, so inventing
  quotations would be fabricating a citation. Each level below is written in
  terms of evidence this lab can actually produce and check.

NOTHING HERE CHANGES A CHIP. The four fidelity chips keep their meanings and
their decision path in ``lab.py`` exactly as they are. The tier and the
scorecard are additional named fields that sit beside a chip and explain it.
The tier field is called ``validation_tier`` and never ``tier``, because
``tier`` already means the fidelity chip everywhere in this codebase.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

# --------------------------------------------------------------------------
# The validation hierarchy (Oberkampf and Trucano, SAND2002-0529)
# --------------------------------------------------------------------------

UNIT_PROBLEM = "UNIT PROBLEM"
BENCHMARK_CASE = "BENCHMARK CASE"
SUBSYSTEM_CASE = "SUBSYSTEM CASE"
COMPLETE_SYSTEM = "COMPLETE SYSTEM"

VALIDATION_TIERS = (
    UNIT_PROBLEM, BENCHMARK_CASE, SUBSYSTEM_CASE, COMPLETE_SYSTEM)

OBERKAMPF_CITATION = (
    "Verification And Validation In Computational Fluid Dynamics, Oberkampf "
    "And Trucano, Sandia Report SAND2002-0529")

# What each tier means for the data that can exist, and therefore for the
# trust a result at that tier may carry. Ordered by increasing complexity and
# decreasing data quality, which is the hierarchy's whole point.
TIER_NOTES: dict[str, dict[str, str]] = {
    UNIT_PROBLEM: {
        "data": "Simple geometry and a single dominant physics, gradeable "
                "against an analytic or highly accurate solution.",
        "ceiling": "The richest evidence available anywhere in the hierarchy. "
                   "A result here can be graded tightly and can reach the top "
                   "chip on its own merits.",
        "unlocks": "Nothing further is needed from an experiment; what limits "
                   "a unit problem is our own numerics.",
    },
    BENCHMARK_CASE: {
        "data": "A canonical geometry with dedicated published measurements, "
                "usually taken to validate models rather than to test a "
                "product.",
        "ceiling": "Can reach the top chip where the published measurement "
                   "matches the solved conditions and carries its own "
                   "uncertainty.",
        "unlocks": "A published measurement at our solved conditions, with "
                   "stated measurement uncertainty, moves this case to the "
                   "top chip.",
    },
    SUBSYSTEM_CASE: {
        "data": "A real component in isolation. Measurements exist but are "
                "sparser, and the conditions are characterized less fully "
                "than in a benchmark experiment.",
        "ceiling": "Held below the top chip while the reference data cannot "
                   "pin the operating conditions we solved.",
        "unlocks": "A component-level measurement with characterized inlet "
                   "conditions would lift this case toward the top chip.",
    },
    COMPLETE_SYSTEM: {
        "data": "The whole configuration. Experimental information is "
                "essentially always very limited and often carries no "
                "uncertainty analysis at all.",
        "ceiling": "Structurally below the top chip however tight the "
                   "envelope. The limit is the data that exists in the world, "
                   "not the quality of the solve.",
        "unlocks": "Only a characterized measurement of the complete "
                   "configuration in its operating environment, which is the "
                   "scarcest data in the hierarchy.",
    },
}

# Every case the lab holds, with the basis for its placement. The first five
# entries are the mapping recorded in the lab's own reading of the report; the
# rest are placed by the same construction and say so.
_RECORDED = "Recorded in the lab's reading of the hierarchy."

_CASE_TIERS: dict[str, tuple[str, str]] = {
    # Recorded mapping
    "cylinder": (UNIT_PROBLEM, _RECORDED),
    "flat_plate": (BENCHMARK_CASE, _RECORDED),
    "motorbike": (BENCHMARK_CASE, _RECORDED),
    "valve": (SUBSYSTEM_CASE, _RECORDED),
    "airliner": (COMPLETE_SYSTEM, _RECORDED),
    # Placed by the same construction
    "sphere": (UNIT_PROBLEM,
               "Simple geometry with a single dominant physics, graded "
               "against a classical drag correlation."),
    "cube": (UNIT_PROBLEM,
             "Simple geometry with a single dominant physics, graded against "
             "a classical drag correlation."),
    "plate": (BENCHMARK_CASE,
              "The verification program grades this body against published "
              "reference code ladders."),
    "cylinder_shedding": (UNIT_PROBLEM,
                          "Simple geometry, one unsteady mechanism, graded "
                          "against the published shedding correlation."),
    "hypersonic_cylinder": (UNIT_PROBLEM,
                            "Simple geometry with one dominant mechanism at "
                            "the leading edge."),
    "supersonic_wedge": (UNIT_PROBLEM,
                         "Graded against an analytic solution."),
    "supersonic_cone": (UNIT_PROBLEM,
                        "Graded against an analytic solution."),
    "diamond_airfoil": (UNIT_PROBLEM,
                        "Graded against an analytic solution."),
    "naca0012_wing": (BENCHMARK_CASE,
                      "A canonical section with dedicated published section "
                      "data."),
    "naca4412_wing": (BENCHMARK_CASE,
                      "A canonical section with dedicated published section "
                      "data."),
    "naca0015_sail": (BENCHMARK_CASE,
                      "A canonical section with dedicated published section "
                      "data."),
    "mach_tutorial_wing": (BENCHMARK_CASE,
                           "A canonical rectangular wing in isolation, "
                           "carried as the reference configuration of a "
                           "published tutorial."),
    "airliner_wing_span52": (SUBSYSTEM_CASE,
                             "A transport wing in isolation, one component "
                             "of the complete configuration it belongs to."),
    "ahmed_25": (BENCHMARK_CASE,
                 "A reference body whose published measurements were taken "
                 "to validate models."),
    "ahmed_35": (BENCHMARK_CASE,
                 "A reference body whose published measurements were taken "
                 "to validate models."),
    "b52": (COMPLETE_SYSTEM,
            "A whole airframe, where characterized measurements of the "
            "configuration are scarcest."),
    "crm_wingbody": (COMPLETE_SYSTEM,
                     "A full transport configuration, graded against a "
                     "published workshop campaign."),
    "onera_m6": (BENCHMARK_CASE,
                 "A canonical wing with a dedicated published pressure "
                 "campaign."),
    "nasa_hump": (BENCHMARK_CASE,
                  "A canonical separated-flow geometry with a dedicated "
                  "published campaign."),
}

# Aliases that resolve to the same case, matching the display-name registry's
# key conventions so a caller can pass whichever slug it already holds.
_ALIASES = {
    "aortic_valve": "valve",
    "valve_study": "valve",
    "naca0012": "naca0012_wing",
    "naca4412": "naca4412_wing",
    "naca0015": "naca0015_sail",
    "aircraft_optimization": "airliner",
    "motorcycle": "motorbike",
}


def _slug(key: str | None) -> str:
    """Same normalization the display-name registry uses."""
    text = str(key or "").strip()
    if any(sep in text for sep in ("/", "\\", ".")):
        text = Path(text).stem
    text = text.strip().lower().replace(" ", "_").replace("-", "_")
    return _ALIASES.get(text, text)


def validation_tier(case_key: str | None) -> str | None:
    """The case's tier in the validation hierarchy, or None if unregistered.

    None is a real answer and must not be papered over: an unregistered case
    has not been placed in the hierarchy by anyone, and guessing a tier for it
    would be exactly the fabrication this module exists to prevent.
    """
    entry = _CASE_TIERS.get(_slug(case_key))
    return entry[0] if entry else None


def validation_tier_basis(case_key: str | None) -> str | None:
    """Why the case sits at the tier it does."""
    entry = _CASE_TIERS.get(_slug(case_key))
    return entry[1] if entry else None


def tier_label(case_key: str | None) -> dict[str, Any] | None:
    """The full labelled tier for one case, ready to sit beside a chip."""
    tier = validation_tier(case_key)
    if tier is None:
        return None
    notes = TIER_NOTES[tier]
    return {
        "validation_tier": tier,
        "rank": VALIDATION_TIERS.index(tier) + 1,
        "of": len(VALIDATION_TIERS),
        "basis": validation_tier_basis(case_key),
        "data_available": notes["data"],
        "ceiling": notes["ceiling"],
        "unlocked_by": notes["unlocks"],
        "citation": OBERKAMPF_CITATION,
    }


def labelled_cases() -> dict[str, str]:
    """Every case the lab has placed in the hierarchy, slug to tier."""
    return {key: value[0] for key, value in sorted(_CASE_TIERS.items())}


# --------------------------------------------------------------------------
# The credibility scorecard (NASA-STD-7009B results-assessment factors)
# --------------------------------------------------------------------------

NASA_CITATION = (
    "NASA-STD-7009B, Standard For Models And Simulations, NASA 2024")

INPUT_PEDIGREE = "Input pedigree"
RESULTS_ROBUSTNESS = "Results robustness"

MAX_LEVEL = 4

# The lab's mapping onto the standard's 0 to 4 scale. See the module docstring
# on what is quoted and what is ours: these words are ours, written in terms of
# evidence this lab can produce and check.
PEDIGREE_LEVELS: dict[int, str] = {
    0: "Inputs are not traceable.",
    1: "Inputs are assumed, with the assumption stated on the record.",
    2: "Inputs come from a handbook, a correlation or a standard condition.",
    3: "Inputs are traced to the published configuration this result is "
       "graded against, with the solved operating point recorded.",
    4: "Inputs are measured on the system being simulated.",
}

ROBUSTNESS_LEVELS: dict[int, str] = {
    0: "No sensitivity of the answer is known.",
    1: "Sensitivity was probed but the study did not settle.",
    2: "Grid sensitivity is measured on a settled ladder.",
    3: "Grid sensitivity is measured and the input spreads are propagated to "
       "a band.",
    4: "Output variance is apportioned across every known input spread.",
}


def _pedigree_level(record: Mapping[str, Any]) -> tuple[int, str]:
    """Input pedigree, read off what the record actually carries."""
    comparison = record.get("comparison") or {}
    source = record.get("reference_source") or comparison.get("source")
    solved_point = (comparison.get("solved_reynolds")
                    or record.get("solved_reynolds"))
    regime = str(comparison.get("regime") or record.get("regime") or "")
    basis = record.get("basis_note") or record.get("area_basis")

    if source and solved_point and regime and "mismatch" not in regime.lower():
        return 3, PEDIGREE_LEVELS[3]
    if source:
        return 2, PEDIGREE_LEVELS[2]
    if basis:
        return 1, PEDIGREE_LEVELS[1]
    return 0, PEDIGREE_LEVELS[0]


def _robustness_level(record: Mapping[str, Any]) -> tuple[int, str]:
    """Results robustness, read off what the record actually carries."""
    study = record.get("grid_study") or {}
    rungs = study.get("rungs") or []
    settled = bool(study.get("grid_conclusive"))
    has_band = record.get("envelope") is not None
    apportioned = bool(record.get("sobol_indices")
                       or record.get("variance_shares"))

    if apportioned:
        return 4, ROBUSTNESS_LEVELS[4]
    if settled and has_band:
        return 3, ROBUSTNESS_LEVELS[3]
    if settled:
        return 2, ROBUSTNESS_LEVELS[2]
    if rungs:
        return 1, ROBUSTNESS_LEVELS[1]
    return 0, ROBUSTNESS_LEVELS[0]


def scorecard(record: Mapping[str, Any] | None,
              *, placard: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """The compact credibility scorecard that backs one fidelity chip.

    Covers the two results-assessment factors the chips do not encode, each on
    the standard's 0 to 4 scale. ``placard`` carries a requirement M&S 26
    statement where a result is used outside its validated domain: the type of
    limit exceeded, its extent, and the assessed consequences.

    The chip itself is untouched and is not an input here. A scorecard
    explains a chip; it never overrides one.
    """
    record = record or {}
    pedigree, pedigree_note = _pedigree_level(record)
    robustness, robustness_note = _robustness_level(record)
    out: dict[str, Any] = {
        "citation": NASA_CITATION,
        "scale": f"0 to {MAX_LEVEL}",
        "factors": [
            {"factor": INPUT_PEDIGREE, "level": pedigree, "of": MAX_LEVEL,
             "note": pedigree_note},
            {"factor": RESULTS_ROBUSTNESS, "level": robustness,
             "of": MAX_LEVEL, "note": robustness_note},
        ],
    }
    if placard:
        out["placard"] = dict(placard)
    return out


def domain_placard(limit: str, extent: str, consequences: str) -> dict[str, str]:
    """A requirement M&S 26 placard for use outside the validated domain.

    The standard requires three things and this function refuses to build a
    placard missing any of them: the type of limit exceeded, its extent, and
    the assessed consequences. The valve screening cap is the lab's worked
    example, and it already behaved this way before the standard was read.
    """
    if not (limit and extent and consequences):
        raise ValueError(
            "a placard states the limit, its extent, and the consequences")
    return {"limit": limit, "extent": extent, "consequences": consequences}


def credibility_block(case_key: str | None,
                      record: Mapping[str, Any] | None = None,
                      *, placard: Mapping[str, Any] | None = None,
                      ) -> dict[str, Any]:
    """Everything this module adds beside a fidelity chip, in one object.

    The chip stays where it is and means what it meant. This block answers the
    two questions the chip does not: where the case sits in the validation
    hierarchy, and how well its inputs and its sensitivities are known.
    """
    block: dict[str, Any] = {"credibility": scorecard(record, placard=placard)}
    tier = tier_label(case_key)
    if tier:
        block["validation_tier"] = tier
    return block
