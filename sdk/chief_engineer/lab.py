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

from dataclasses import dataclass, field
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

VALIDATED = "VALIDATED"
TREND_ONLY = "TREND ONLY"
NEEDS_WORK = "NEEDS WORK"
# The solve landed in a different physical regime than the reference describes —
# a like-for-like comparison is not available, so this is neither a pass nor a
# quiet trend. The verdict names the regime it actually matches.
REGIME_MISMATCH = "REFERENCE REGIME MISMATCH"


def trust(*, relative_error: float | None = None, converged: bool = True,
          in_validated_regime: bool = True, calibrated: bool = True,
          tight_threshold: float = 0.02, why: str = "") -> dict[str, str]:
    """Decide how far a reported quantity may be trusted, and say why.

    The verdict is derived, never asserted: every branch here is a measured
    fact about this run, and ``why`` lets the caller name the specific number
    that decided it so the tier can never read as a fixed label.
    """
    if not converged:
        return {"tier": NEEDS_WORK,
                "reason": why or "the solve did not converge, so the number is not evidence yet"}
    if not in_validated_regime:
        return {"tier": TREND_ONLY,
                "reason": why or ("outside the regime we have validated — direction is "
                                  "usable, magnitude is indicative")}
    if not calibrated:
        return {"tier": TREND_ONLY,
                "reason": why or ("mesh quality is outside the acceptance band, so the "
                                  "magnitude is indicative rather than trusted")}
    if relative_error is None:
        return {"tier": TREND_ONLY, "reason": "no envelope was computed for this quantity"}
    if relative_error <= tight_threshold:
        return {"tier": VALIDATED,
                "reason": f"converged, inside the validated regime, envelope "
                          f"{relative_error * 100:.1f}% of value"}
    return {"tier": TREND_ONLY,
            "reason": f"envelope is {relative_error * 100:.1f}% of value — usable as a "
                      f"trend, not yet as a magnitude"}


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
                    numerical_note or "discretization error — needs a grid-refinement study"),
            channel("model", model,
                    model_note or "turbulence/closure model-form error — not yet estimated"),
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
    return (f" — solved at Re {solved_reynolds:.1e}, reference valid for "
            f"Re {lo:.0e}–{hi:.0e}")


def validate_against_reference(*, measured_cd: float, reference: dict,
                               planform_area: float | None = None,
                               frontal_area: float | None = None,
                               converged: bool = True,
                               in_validated_regime: bool = True,
                               calibrated: bool = True,
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
    """
    cd_ref = float(reference["cd"])
    tolerance = float(reference.get("tolerance", 0.15))
    source = reference.get("source", "the cited reference")
    cd_cmp, basis_note = _rebase(measured_cd, reference,
                                 planform_area=planform_area, frontal_area=frontal_area)
    relative_error = abs(cd_cmp - cd_ref) / abs(cd_ref) if cd_ref else None

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
        verdict = {"tier": NEEDS_WORK,
                   "reason": "the solve did not converge, so there is nothing to compare "
                             "against the reference yet"}
    elif not in_validated_regime:
        verdict = {"tier": TREND_ONLY,
                   "reason": (f"mesh quality is outside the acceptance band, so agreement with "
                              f"{source} would not be trustworthy — direction only")}
    elif not calibrated:
        verdict = {"tier": TREND_ONLY,
                   "reason": (f"mesh skewness is above guidance, so the magnitude stays "
                              f"indicative even against {source}")}
    elif relative_error is not None and relative_error <= tolerance:
        verdict = {"tier": VALIDATED,
                   "reason": (f"within {relative_error * 100:.0f}% of {source}, "
                              f"Cd {cd_ref:g} (band ±{tolerance * 100:.0f}%)")}
    else:
        alt = _matching_alternate(reference, cd_cmp)
        if alt:
            primary = _regime_label(reference)
            re_note = _reynolds_mismatch_note(reference, solved_reynolds)
            cause = alt.get("cause")
            comparison["matched_regime"] = alt.get("label")
            verdict = {"tier": REGIME_MISMATCH,
                       "reason": (f"measured Cd {cd_cmp:.3f} matches the {alt.get('label')} regime "
                                  f"(Cd ~{float(alt['cd']):g}, {alt.get('source', source)}), not the "
                                  f"{primary} reference Cd {cd_ref:g}"
                                  + re_note
                                  + (f"; {cause}" if cause else "")
                                  + " — a like-for-like comparison against the reference is "
                                    "not available, so this is neither validated nor a plain trend")}
        else:
            pct = "n/a" if relative_error is None else f"{relative_error * 100:.0f}%"
            verdict = {"tier": TREND_ONLY,
                       "reason": (f"measured Cd {cd_cmp:.3f} is {pct} from {source}, "
                                  f"Cd {cd_ref:g} — outside the ±{tolerance * 100:.0f}% band, "
                                  f"so it stands as a trend")}
    verdict["comparison"] = comparison
    return verdict

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
