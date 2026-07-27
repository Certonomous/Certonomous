"""The lab as an organization: who is working, what it costs, what it learned.

The mission kernel already produces the evidence.  This module gives that
evidence the shape a laboratory would recognise — a roster of people and their
current activity, a ledger of compute spent and compute avoided, a trust tier
on every reported quantity, the literature a recommendation rests on, and a
closing memo written in the structure of a research report.

Nothing here invents findings.  Every number is passed in from a real run; the
module's job is to frame, total, and phrase.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

# --------------------------------------------------------------------------
# Research structure
# --------------------------------------------------------------------------

HYPOTHESIS = "Hypothesis"
PLAN = "Experiment plan"
EVIDENCE = "Evidence"
CONCLUSION = "Conclusion"
PHASES = (HYPOTHESIS, PLAN, EVIDENCE, CONCLUSION)


# --------------------------------------------------------------------------
# Roster
# --------------------------------------------------------------------------

CHIEF_ENGINEER = "Chief Engineer"
CHIEF_RESEARCHER = "Chief Researcher"
NUMERICIST = "Numericist"
MONITOR = "Monitoring agent"

ROLE_BLURB = {
    CHIEF_ENGINEER: "runs the mission end to end",
    CHIEF_RESEARCHER: "governs approximations and validity",
    NUMERICIST: "audits the numerics, proposes faster routes",
    MONITOR: "watches solver output for trouble",
}


@dataclass
class Member:
    role: str
    blurb: str
    activity: str = "standing by"
    status: str = "idle"          # idle | working | watching | blocked

    def as_dict(self) -> dict[str, str]:
        return {"role": self.role, "blurb": self.blurb,
                "activity": self.activity, "status": self.status}


class Roster:
    """Who is in the room, and what each of them is doing right now."""

    def __init__(self, emit=None):
        self.emit = emit
        self.members: dict[str, Member] = {
            role: Member(role, blurb) for role, blurb in ROLE_BLURB.items()
        }
        self.workers = 0
        self.worker_activity = ""

    def set(self, role: str, activity: str, status: str = "working") -> None:
        member = self.members.get(role)
        if member is None:
            return
        member.activity = activity
        member.status = status
        self._publish()

    def idle(self, role: str) -> None:
        self.set(role, "standing by", "idle")

    def all_idle(self) -> None:
        for member in self.members.values():
            member.activity, member.status = "standing by", "idle"
        self.workers = 0
        self.worker_activity = ""
        self._publish()

    def set_workers(self, count: int, activity: str = "") -> None:
        self.workers = max(0, int(count))
        self.worker_activity = activity
        self._publish()

    def as_dict(self) -> dict[str, Any]:
        return {
            "members": [member.as_dict() for member in self.members.values()],
            "workers": self.workers,
            "worker_activity": self.worker_activity,
        }

    def _publish(self) -> None:
        if self.emit:
            self.emit("roster.update", self.as_dict())


# --------------------------------------------------------------------------
# Compute stewardship
# --------------------------------------------------------------------------

@dataclass
class ComputeLedger:
    """Core-seconds actually burned, and core-seconds the lab avoided burning.

    Savings are only ever recorded against a *measured* alternative: the cost
    of the designs a surrogate covered, or of the fine mesh a validated
    closure stood in for. An unmeasured saving is not recorded.
    """

    emit: Any = None
    spent: float = 0.0
    saved: float = 0.0
    notes: list[str] = field(default_factory=list)

    def spend(self, core_seconds: float, what: str = "") -> None:
        self.spent += max(0.0, float(core_seconds))
        if what:
            self.notes.append(f"spent {core_seconds / 60:.1f} core-min · {what}")
        self._publish()

    def save(self, core_seconds: float, why: str) -> None:
        self.saved += max(0.0, float(core_seconds))
        self.notes.append(f"avoided {core_seconds / 60:.1f} core-min · {why}")
        self._publish()

    @property
    def efficiency(self) -> float:
        total = self.spent + self.saved
        return (self.saved / total) if total else 0.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "spent_core_minutes": round(self.spent / 60, 2),
            "saved_core_minutes": round(self.saved / 60, 2),
            "efficiency": round(self.efficiency, 3),
            # A mission that approximated nothing did not fail to save — it
            # chose full fidelity. Distinguish that from a missing figure.
            "full_fidelity": self.saved <= 0.0,
            "notes": list(self.notes[-6:]),
        }

    def _publish(self) -> None:
        if self.emit:
            self.emit("compute.update", self.as_dict())


# --------------------------------------------------------------------------
# Trust tiers
# --------------------------------------------------------------------------

# Fidelity chips: one or two words that say what stands behind a number.
# VALIDATED — graded against a published experiment and inside its band.
# SOLVER-BACKED — a real solve produced it; no experimental comparison (or
#   the comparison is not like-for-like). Specifics live in the channel table.
# RESEARCH MODEL — a sizing/reduced-order model, honestly labeled.
# UNCONVERGED — the solve did not settle; the number is not evidence yet.
# Honesty is carried by the value ± CI, the chip, and the uncertainty
# channels — never by hedging prose.
VALIDATED = "VALIDATED"
SOLVER_BACKED = "SOLVER-BACKED"
CONCEPTUAL = "RESEARCH MODEL"
UNCONVERGED = "UNCONVERGED"
# Retired labels, kept only so historical records still map to a chip.
LEGACY_CHIPS = {"TREND ONLY": SOLVER_BACKED,
                "REFERENCE REGIME MISMATCH": SOLVER_BACKED,
                "NEEDS WORK": UNCONVERGED}
# Backwards-compatible aliases for older call sites/tests.
TREND_ONLY = SOLVER_BACKED
NEEDS_WORK = UNCONVERGED
REGIME_MISMATCH = SOLVER_BACKED


def trust(*, relative_error: float | None = None, converged: bool = True,
          in_validated_regime: bool = True, calibrated: bool = True,
          solver_backed: bool = True, tight_threshold: float = 0.02,
          why: str = "") -> dict[str, str]:
    """Assign the fidelity chip a reported quantity has earned, and say why.

    The chip is derived, never asserted: every branch is a measured fact
    about this run. ``solver_backed=False`` marks results produced by a
    conceptual or reduced-order model rather than a solve — nothing is
    upgraded that was not earned. Caveat detail belongs in the uncertainty
    channels; ``reason`` stays one crisp factual clause.
    """
    if not converged:
        return {"tier": UNCONVERGED,
                "reason": why or "the solve did not settle; the number is not evidence yet"}
    if not solver_backed:
        return {"tier": CONCEPTUAL,
                "reason": why or "produced by a stated research model, not a solve"}
    if not in_validated_regime or not calibrated:
        return {"tier": SOLVER_BACKED,
                "reason": why or "a selected-solver result without a like-for-like experimental comparison"}
    # VALIDATED is earned only against a published experiment — that path is
    # validate_against_reference(). A tight envelope alone stays SOLVER-BACKED.
    if relative_error is None:
        return {"tier": SOLVER_BACKED,
                "reason": why or "a selected-solver result; no envelope computed for this quantity"}
    return {"tier": SOLVER_BACKED,
            "reason": why or f"a selected-solver result; envelope {relative_error * 100:.1f}% of value"}


def uncertainty_channels(*, input_2sigma: float | None = None,
                         numerical: float | None = None,
                         model: float | None = None,
                         input_note: str = "",
                         numerical_note: str = "", model_note: str = "") -> dict:
    """The three V&V-20 uncertainty channels, reported separately.

    Each channel is a number when the lab has measured it and an explicit
    "not quantified" with a reason when it has not — the visible signature of
    structured UQ rather than a single fudge factor.  ``input_2sigma`` is the
    aleatory spread propagated from input uncertainty; ``numerical`` is the
    discretization component; ``model`` is turbulence/closure model-form error.
    Each channel always renders with a value or a crisp measured-status clause;
    the ``*_note`` overrides carry the act-specific reason so no channel is left
    on a generic placeholder (ASME V&V 20 asks for all three, named).
    """
    def channel(name, value, note):
        if value is None:
            return {"name": name, "value": None, "quantified": False, "note": note}
        return {"name": name, "value": round(value, 5), "quantified": True, "note": note}

    return {
        "channels": [
            channel("input", input_2sigma,
                    input_note or "propagated from the stated input uncertainty (aleatory)"),
            channel("numerical", numerical,
                    numerical_note or "discretization error, needs a grid-refinement study"),
            channel("model", model,
                    model_note or "turbulence/closure model-form error, not yet estimated"),
        ],
    }


def _rebase(measured_cd: float, reference: dict, *,
            planform_area: float | None, frontal_area: float | None) -> tuple[float, str]:
    """Put the measured coefficient on the reference's area basis.

    The solver reports drag on the measured planform area. A handbook value is
    usually on frontal area, and a coefficient is only comparable once both use
    the same reference area, so the measured value is rescaled by the ratio of
    the two silhouettes before anything is called validated.
    """
    basis = str(reference.get("area_basis", "planform")).lower()
    if basis == "frontal" and planform_area and frontal_area:
        return (measured_cd * planform_area / frontal_area,
                "rebased from the measured planform area onto frontal area")
    return measured_cd, "already on the reference's planform-area basis"


def _regime_label(reference: dict) -> str:
    """The primary regime's name — supports both the structured and legacy forms."""
    reg = reference.get("regime")
    if isinstance(reg, dict):
        return reg.get("label", "the reference regime")
    return reg or "the reference regime"


def _matching_alternate(reference: dict, cd_cmp: float) -> dict | None:
    """An alternate regime of the same body whose Cd band contains the measurement.

    A body like the sphere has more than one physical regime (subcritical vs
    supercritical). When a solve's coefficient lands on a regime other than the
    reference's, this finds it so the verdict can name it rather than failing
    blindly against the wrong branch.
    """
    reg = reference.get("regime")
    alternates = reg.get("alternates", []) if isinstance(reg, dict) else []
    for alt in alternates:
        band = alt.get("cd_range")
        if band and float(band[0]) <= cd_cmp <= float(band[1]):
            return alt
    return None


def _reynolds_mismatch_note(reference: dict, solved_reynolds: float | None) -> str:
    """State the Reynolds mismatch when there is one; stay silent when there isn't.

    The sphere and cylinder here solve *inside* their subcritical Reynolds band
    yet read supercritical because fully-turbulent RANS delays separation — that
    is a model-form regime shift, not a Reynolds one, so this only cites Re when
    the solve genuinely sits outside the reference's validity band.
    """
    reg = reference.get("regime")
    valid = reg.get("reynolds_valid") if isinstance(reg, dict) else None
    if solved_reynolds is None or not valid:
        return ""
    lo, hi = float(valid[0]), float(valid[1])
    if lo <= solved_reynolds <= hi:
        return ""
    return (f"; solved at Re {solved_reynolds:.1e}, reference valid for "
            f"Re {lo:.0e}-{hi:.0e}")


def validate_against_reference(*, measured_cd: float, reference: dict,
                               planform_area: float | None = None,
                               frontal_area: float | None = None,
                               converged: bool = True,
                               in_validated_regime: bool = True,
                               calibrated: bool = True,
                               grid_conclusive: bool | None = None,
                               solved_reynolds: float | None = None) -> dict[str, Any]:
    """Grade a measured drag coefficient against a published experiment.

    This is the path that can reach VALIDATED: with a real reference in hand, a
    converged force that lands inside the reference's tolerance band earns it,
    and the reason names the source and the number so the tier reads as a
    measured comparison rather than a label. Outside the band but converged is a
    trend — unless the value lands squarely on a *different* known regime of the
    same body, in which case it is a REFERENCE REGIME MISMATCH: the comparison
    is not like-for-like, and the verdict names the regime the measurement
    actually matches rather than quietly failing against the wrong one. An
    unconverged or off-regime solve never validates on agreement alone. The
    measured value is always rebased onto the reference area first.

    Landing inside the band is necessary but not sufficient: a reference can
    only validate a solve when the reference itself is trustworthy and the
    solve's own grid sensitivity is settled. ``reference["confidence"]``
    marked "low" means the number being compared against was never itself a
    solid measurement (a hand-set estimate, a wide guess), so agreement with
    it proves nothing; and when a grid-refinement study exists for this exact
    setup (``grid_conclusive`` not None) and it came back inconclusive, the
    solve has not settled onto a mesh-independent value yet, so there is
    nothing stable to call validated. Either condition, on an otherwise
    in-band result, drops the tier to SOLVER-BACKED rather than VALIDATED --
    the comparison is still reported, honestly, as insufficient to validate.
    """
    cd_ref = float(reference["cd"])
    tolerance = float(reference.get("tolerance", 0.15))
    source = reference.get("source", "the cited reference")
    cd_cmp, basis_note = _rebase(measured_cd, reference,
                                 planform_area=planform_area, frontal_area=frontal_area)
    relative_error = abs(cd_cmp - cd_ref) / abs(cd_ref) if cd_ref else None
    # A reference can only validate a solve when it is itself trustworthy and
    # the ladder behind the solve has settled. Both checks are driven purely
    # by the reference and study metadata passed in -- no per-body special case.
    low_confidence = str(reference.get("confidence", "")).strip().lower() == "low"
    grid_inconclusive = grid_conclusive is False

    comparison = {
        "measured_cd": round(measured_cd, 4),
        "compared_cd": round(cd_cmp, 4),
        "reference_cd": cd_ref,
        "relative_error": None if relative_error is None else round(relative_error, 4),
        "tolerance": tolerance,
        "area_basis": reference.get("area_basis", "planform"),
        "basis_note": basis_note,
        "source": source,
        "solved_reynolds": solved_reynolds,
        "regime": _regime_label(reference),
    }

    if not converged:
        verdict = {"tier": UNCONVERGED,
                   "reason": "the solve did not settle; nothing to compare "
                             "against the reference yet"}
    elif not in_validated_regime:
        verdict = {"tier": SOLVER_BACKED,
                   "reason": (f"mesh quality outside the acceptance band; the numerical "
                              f"channel carries the residual, not a comparison with {source}")}
    elif not calibrated:
        verdict = {"tier": SOLVER_BACKED,
                   "reason": (f"mesh skewness above guidance; the numerical channel "
                              f"carries the residual, not a comparison with {source}")}
    elif (relative_error is not None and relative_error <= tolerance
          and not low_confidence and not grid_inconclusive):
        verdict = {"tier": VALIDATED,
                   "reason": (f"within {relative_error * 100:.0f}% of {source}, "
                              f"Cd {cd_ref:g} (band ±{tolerance * 100:.0f}%)")}
    elif relative_error is not None and relative_error <= tolerance:
        blockers = []
        if low_confidence:
            blockers.append("that reference is itself a low-confidence estimate, "
                            "not a settled measurement")
        if grid_inconclusive:
            blockers.append("the grid-refinement study for this setup came back inconclusive")
        verdict = {"tier": SOLVER_BACKED,
                   "reason": (f"within {relative_error * 100:.0f}% of {source}, "
                              f"Cd {cd_ref:g} (band ±{tolerance * 100:.0f}%), but "
                              + " and ".join(blockers)
                              + "; not enough to call it validated")}
    else:
        alt = _matching_alternate(reference, cd_cmp)
        if alt:
            primary = _regime_label(reference)
            re_note = _reynolds_mismatch_note(reference, solved_reynolds)
            cause = alt.get("cause")
            comparison["matched_regime"] = alt.get("label")
            verdict = {"tier": SOLVER_BACKED,
                       "reason": (f"measured Cd {cd_cmp:.3f} matches the {alt.get('label')} regime "
                                  f"(Cd ~{float(alt['cd']):g}, {alt.get('source', source)}), not the "
                                  f"{primary} reference Cd {cd_ref:g}"
                                  + re_note
                                  + (f"; {cause}" if cause else "")
                                  + "; no like-for-like comparison available")}
        else:
            pct = "n/a" if relative_error is None else f"{relative_error * 100:.0f}%"
            verdict = {"tier": SOLVER_BACKED,
                       "reason": (f"measured Cd {cd_cmp:.3f} is {pct} from {source}, "
                                  f"Cd {cd_ref:g}, outside the ±{tolerance * 100:.0f}% band")}
    verdict["comparison"] = comparison
    return verdict

def grade_drag_area(*, measured_cd: float, reference_area_m2: float,
                    reference: dict, converged: bool = True,
                    in_validated_regime: bool = True,
                    calibrated: bool = True) -> dict[str, Any]:
    """Grade a solved force against a published drag-area band.

    Drag area Cd * Aref is area-convention-proof: whatever reference area the
    case's force coefficients used, the product is the physical drag area in
    m² and compares like for like against published full-scale values. The
    reference carries ``drag_area_band`` [lo, hi] in m², a ``band_label``
    naming the population, and its ``source``.

    A population band is not an experiment on this specific geometry, so this
    path never grants VALIDATED; a positive comparison is stated on the
    record and the tier stays SOLVER-BACKED with the comparison as its reason.
    """
    lo, hi = (float(x) for x in reference["drag_area_band"])
    source = reference.get("source", "the cited reference")
    source_short = reference.get("source_short", source)
    label = reference.get("band_label", "published band")
    drag_area = float(measured_cd) * float(reference_area_m2)
    position = "inside" if lo <= drag_area <= hi else (
        "below" if drag_area < lo else "above")
    comparison = {
        "kind": "drag-area-band",
        "measured_cd": round(float(measured_cd), 4),
        "reference_area_m2": round(float(reference_area_m2), 4),
        "drag_area_m2": round(drag_area, 4),
        "band_lo": lo, "band_hi": hi,
        "band_label": label, "source": source, "source_short": source_short,
        "position": position,
    }
    if not converged:
        verdict = {"tier": UNCONVERGED,
                   "reason": "the solve did not settle; nothing to compare "
                             "against the published band yet"}
    elif not in_validated_regime:
        verdict = {"tier": SOLVER_BACKED,
                   "reason": ("mesh quality outside the acceptance band; the "
                              "numerical channel carries the residual, not a "
                              f"comparison with {source}")}
    elif not calibrated:
        verdict = {"tier": SOLVER_BACKED,
                   "reason": ("mesh skewness above guidance; the numerical "
                              "channel carries the residual, not a comparison "
                              f"with {source}")}
    elif position == "inside":
        verdict = {"tier": SOLVER_BACKED,
                   "reason": (f"drag area {drag_area:.2f} m² sits inside the "
                              f"{label}, {lo:g} to {hi:g} m² ({source_short}); "
                              f"a published band, not a geometry-specific "
                              f"experiment")}
    else:
        verdict = {"tier": SOLVER_BACKED,
                   "reason": (f"drag area {drag_area:.2f} m² sits {position} "
                              f"the {label}, {lo:g} to {hi:g} m² "
                              f"({source_short})")}
    verdict["comparison"] = comparison
    return verdict


# --------------------------------------------------------------------------
# Credential propagation: the finest rung on record is the one displayed
# --------------------------------------------------------------------------

CURRICULUM_DIR = (Path(__file__).resolve().parents[2] / "models" / "curriculum")

_CELLS_IN_TEXT = re.compile(r"([\d,]+)\s*cells")


def reference_on_disk(body: str) -> dict[str, Any] | None:
    """The curriculum reference for a body, read fresh from its own file.

    Read at display time rather than trusted from a stored record, so a
    reference that has since been corrected (a band tightened, a confidence
    marked low) governs the tier the surface shows.
    """
    path = CURRICULUM_DIR / body / "reference.yaml"
    if not path.exists():
        return None
    try:
        import yaml
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    data.setdefault("name", body)
    return data


def recorded_cells(record: dict) -> int | None:
    """The mesh a stored credential was measured on, read from its own record."""
    for item in record.get("report_results") or []:
        if str(item.get("quantity", "")).strip().lower() == "mesh":
            found = _CELLS_IN_TEXT.search(str(item.get("value", "")))
            if found:
                return int(found.group(1).replace(",", ""))
    return None


def finest_rung(record: dict, study: dict | None) -> dict | None:
    """The finest mesh of a refinement ladder anchored to this credential.

    A stored ladder counts as this credential's own only when one of its rungs
    ran on the credential's mesh, the same anchoring rule the in-act ladder
    applies before it replays a stored study. When the anchored ladder reaches
    further than the recorded mesh, its finest rung is a later and better
    measurement of the same case, and it is the one the wall owes the reader.
    Returns None when there is no anchored ladder or nothing finer on it.
    """
    levels = [lv for lv in (study or {}).get("levels", [])
              if lv.get("cells") and lv.get("cd") is not None]
    if not levels:
        return None
    mine = recorded_cells(record)
    if mine is None or not any(int(lv["cells"]) == int(mine) for lv in levels):
        return None
    best = max(levels, key=lambda lv: int(lv["cells"]))
    if int(best["cells"]) <= int(mine):
        return None
    return {"cells": int(best["cells"]), "cd": float(best["cd"]),
            "mission": best.get("mission"), "recorded_cells": int(mine)}


def displayed_credential(record: dict, *, reference: dict | None = None,
                         study: dict | None = None) -> dict[str, Any]:
    """What a stored credential should show today, re-derived from measurement.

    A result file is the as-run archive of one mission: the mesh it solved, the
    force it measured, and the tier the grading rules gave it that night. Two
    things move afterwards. A refinement ladder can measure the SAME case on a
    finer mesh hours later, and the grading rules themselves can tighten.
    Neither used to reach the displayed credential, so a wall could keep
    showing the coarsest rung of a finished ladder under a tier the current
    rules would refuse. This re-derives the display from measurement only: the
    finest anchored rung wins, the area basis carries over from the record's
    own rebasing, and the verdict is re-graded against the reference as it
    stands on disk. No number is invented here and none is edited; the stored
    record keeps its own history untouched.
    """
    body = record.get("name", "")
    if reference is None:
        reference = reference_on_disk(body)
    if study is None:
        from chief_engineer import uq as uq_studies
        study = uq_studies.load_study(body)

    raw = record.get("cd_measured")
    try:
        measured = None if raw is None else float(raw)
    except (TypeError, ValueError):
        measured = None
    compared = record.get("cd_compared")
    # The record's own basis note says whether a rebase happened; when it did,
    # the planform-to-frontal ratio is a property of the geometry and carries
    # straight over to any other mesh of the same body.
    note = str(record.get("basis_note") or "")
    ratio = 1.0
    if note.startswith("rebased") and measured and compared:
        ratio = float(compared) / measured

    numerical = (study or {}).get("numerical") or {}
    grid_conclusive = numerical.get("conclusive") if numerical else None
    rung = finest_rung(record, study)

    display: dict[str, Any] = {
        "measured": record.get("cd_measured"),
        "on_reference_basis": record.get("cd_measured"),
        "envelope": record.get("envelope"),
        "cells": recorded_cells(record),
        "superseded": False,
        "provenance": None,
        "tier": record.get("tier") or UNCONVERGED,
        "reason": record.get("reason"),
        "relative_error": record.get("relative_error"),
        "reference_cd": (reference or {}).get("cd", record.get("reference_cd")),
        "source": (reference or {}).get("source", record.get("reference_source")),
        "area_basis": record.get("area_basis"),
        "basis_note": record.get("basis_note"),
    }

    if rung:
        measured = rung["cd"]
        display.update({
            "measured": f"{measured:.4g}",
            "cells": rung["cells"],
            "superseded": True,
            "provenance": rung.get("mission"),
        })
        band = numerical.get("band_abs")
        rungs = len((study or {}).get("levels") or [])
        display["envelope"] = (
            f"±{float(band):.2g} across the {rungs}-mesh refinement study"
            if band else f"finest mesh on record, {rung['cells']:,} cells")
    else:
        # Nothing finer on record: a ladder that is not anchored to this
        # credential's mesh says nothing about this solve, so it must not gate
        # its tier either.
        if not (study or {}).get("levels") or recorded_cells(record) is None:
            grid_conclusive = None
        elif not any(int(lv.get("cells", 0)) == int(recorded_cells(record))
                     for lv in (study or {}).get("levels", [])):
            grid_conclusive = None

    display["grid_conclusive"] = grid_conclusive
    # ONE consistently rebased number: the figure a surface prints and the
    # percentage it prints beside it have to come from the same measurement on
    # the same area basis, whichever rung is being shown.
    if measured is not None:
        display["on_reference_basis"] = f"{measured * ratio:.4g}"

    if reference and reference.get("cd") is not None and measured is not None:
        verdict = validate_against_reference(
            measured_cd=measured * ratio, reference=reference,
            converged=bool(record.get("ok", True)),
            grid_conclusive=grid_conclusive)
        comparison = verdict.get("comparison") or {}
        display.update({
            "tier": verdict["tier"],
            "reason": verdict["reason"],
            "relative_error": comparison.get("relative_error"),
            "compared": comparison.get("compared_cd"),
        })
        if ratio != 1.0:
            display["basis_note"] = note
    return display


# --------------------------------------------------------------------------
# Literature the Numericist reads
# --------------------------------------------------------------------------

LITERATURE = {
    "grid-uncertainty": "the grid-refinement uncertainty procedure (Eca & Hoekstra, 2014)",
    "vv20": "the ASME V&V 20 validation-uncertainty standard",
    "verification": "Oberkampf & Roy on verification and validation",
    "gp-error": "the GP error-quantification study (Xia et al., 2025)",
    "gp-closure": "our own sparse and deep GP closure work (Mouzahir & Lermusiaux)",
    "openfoam-validation": "the Francis-turbine validation study (Salehi & Nilsson, 2021)",
    "multifidelity": "the multifidelity methods survey (Peherstorfer, Willcox & Gunzburger)",
    "rom": "the projection-based model-reduction survey (Benner, Gugercin & Willcox)",
    "gp": "Gaussian Processes for Machine Learning (Rasmussen & Williams)",
    "mesh-quality": "OpenFOAM mesh-quality guidance",
    "cfd-2030": "the NASA CFD Vision 2030 study",
}


def per(key: str) -> str:
    """Phrase a literature reference the way a researcher would say it."""
    source = LITERATURE.get(key)
    return f"per {source}" if source else ""


# --------------------------------------------------------------------------
# Knowledge growth
# --------------------------------------------------------------------------

class KnowledgeBase:
    """Counts what the lab knows, and announces the moment it learns more."""

    def __init__(self, emit=None, *, entries: int = 7, lessons: int = 1):
        self.emit = emit
        self.entries = entries
        self.lessons = lessons
        self.added: list[dict[str, str]] = []
        # Announce what the lab already knows, so the counters are populated
        # before anything is learned rather than reading as missing data.
        if emit:
            emit("knowledge.state", self.as_dict())

    def add(self, title: str, kind: str = "knowledge") -> None:
        if kind == "lesson":
            self.lessons += 1
        else:
            self.entries += 1
        record = {"title": title, "kind": kind}
        self.added.append(record)
        if self.emit:
            self.emit("knowledge.added", {**record, **self.as_dict()})

    def as_dict(self) -> dict[str, Any]:
        return {"entries": self.entries, "lessons": self.lessons,
                "added": list(self.added)}


# --------------------------------------------------------------------------
# Closing memo
# --------------------------------------------------------------------------

def lab_report(*, title: str, abstract: Iterable[str], methods: Iterable[str],
               results: Iterable[dict], uncertainty: Iterable[str],
               next_investigations: Iterable[str],
               compute: dict | None = None) -> dict:
    """Assemble the closing memo in the structure of a research report.

    ``next_investigations`` is fed from the mission's research agenda: new
    questions and extensions, phrased as ambitions. It must never carry
    remediations of the shown result ("refine the grid", "run a real solve to
    validate this") — honesty about limits lives in the tier and the
    uncertainty channels, and only there.
    """
    return {
        "title": title,
        "abstract": [line for line in abstract if line],
        "methods": [line for line in methods if line],
        # each result: {quantity, value, envelope, tier, reason}
        "results": [dict(item) for item in results],
        "uncertainty": [line for line in uncertainty if line],
        "next_investigations": [line for line in next_investigations if line],
        "compute": dict(compute or {}),
    }
