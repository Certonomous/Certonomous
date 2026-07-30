"""The lab's research agenda: proposals drafted from the lab's own records.

The agenda panel is operational, not decorative. This module reads what the
laboratory has actually recorded — mission reports' next-investigation lists,
the verification card that names its own next case, refinement ladders that
ended inconclusive, graded bodies still outside their validation band, and the
fleet ledger's learned study — and drafts one proposal object per genuine
follow-on. Other overnight agents drop proposal JSONs into an inbox directory
and those ride the same docket.

Initiative comes from the lab; the veto stays with the human. Nothing in this
module launches compute. A proposal changes status only when the owner clicks
Approve or Dismiss in the control room (served by server.py), and even an
approval only starts a mission when the compute audit says the machine has
room.

Proposal schema (drafted and inbox alike)::

    {id, objective, rationale, citations: [display titles only],
     est_core_min, cost_basis, expected_knowledge_gain, source_kind,
     status: proposed|approved|approved-queued|dismissed|done,
     created_at, decided_at?, dismiss_reason?, mission_id?, launch_prompt?}

Cost honesty: ``est_core_min`` is either derived from measured history (the
ledger's wall seconds for the same evaluation family, or a prior graded solve
of the same body) with the derivation quoted in ``cost_basis``, or it is a
default that ``cost_basis`` plainly labels an estimate. No cost is ever
presented as measured unless a record backs it.

Ranking heuristic (deterministic, the whole of it):

* Each proposal earns gain points by source kind — closing a failed or
  inconclusive gate is worth 3, unlocking a deferred capability or extending
  a measured ledger trend is worth 2, a report follow-on is worth 1, and an
  inbox proposal from another agent defaults to 2.
* rank value = gain points / max(est_core_min, 1.0). The 1-core-minute floor
  keeps near-zero screening costs from dividing to infinity.
* Sort: rank value descending, then objective (case-folded) ascending, then
  id ascending. Same docket in, same order out, every time.

The docket persists at ``demo-output/website/agenda/docket.json`` via atomic
replace, and proposals are deduplicated by normalized objective text.
"""

from __future__ import annotations

import json
import os
import re
import threading
from datetime import datetime, timezone
from hashlib import sha1
from pathlib import Path
from typing import Any, Iterable

from .display_names import display_name

_HERE = Path(__file__).resolve()
_REPO_ROOT = _HERE.parents[2]

_LOCK = threading.Lock()

STATUSES = ("proposed", "approved", "approved-queued", "dismissed", "done")
OPEN_STATUSES = ("proposed", "approved-queued")

# Gain points per source kind. This dict IS the heuristic, so a kind missing
# from it is not a small omission: it silently scores the default and the
# ranking stops meaning what it says.
#
# That happened. Three kinds actually in use -- measurement, reading and
# challenge -- were absent, so 24 of 55 proposals ranked on the default. The
# damage was not uniform: the standing priority order puts the UQ layer and the
# challenge FIRST, W1 ladder work below them. But "gate" scored 3.0 and
# "challenge" fell through to 2.0, so ladder work outranked challenge work by
# 50% on every tie. The heuristic was inverting the order it was meant to serve.
#
# Points below follow the standing priority: challenge and UQ measurement lead,
# ladder gates fill compute, reading fills compute-idle time.
_GAIN_POINTS = {
    "challenge": 4.0,      # W5, joint-first: externally verified credential
    "measurement": 3.0,    # W3, joint-first: the uncertainty layer
    "gate": 3.0,           # W1, fills compute
    "capability": 2.0,
    "ledger": 2.0,
    "reading": 2.0,        # W2, fills compute-idle; cheap and it unblocks W1
    "report": 1.0,
}
_GAIN_DEFAULT = 2.0
# Ranking floor in core-minutes: a near-free screen must not rank at infinity.
RANK_FLOOR_CORE_MIN = 1.0

# Default cost estimates (core-minutes) where no measured history applies;
# cost_basis labels every one of these an estimate.
_EST_CAPABILITY_CORE_MIN = 60.0
_EST_REPORT_CORE_MIN = 20.0
_EST_LADDER_RUNG_CORE_MIN = 20.0
_EST_TMR_BUMP_CORE_MIN = 30.0


# --------------------------------------------------------------------------
# Paths — every root is env-overridable so tests run on fixtures
# --------------------------------------------------------------------------

def _agenda_dir() -> Path:
    env = os.environ.get("CERTONOMOUS_AGENDA_DIR")
    if env:
        return Path(env).resolve()
    return (_REPO_ROOT / "demo-output" / "website" / "agenda").resolve()


def docket_path() -> Path:
    return _agenda_dir() / "docket.json"


def inbox_dir() -> Path:
    return _agenda_dir() / "proposals"


def _report_roots() -> list[Path]:
    env = os.environ.get("CERTONOMOUS_REPORT_ROOTS")
    if env:
        return [Path(part).resolve() for part in env.split(os.pathsep) if part]
    return [(_REPO_ROOT / "demo-output" / "acts").resolve(),
            (_REPO_ROOT / "mission-output").resolve()]


def _tmr_card_path() -> Path:
    env = os.environ.get("CERTONOMOUS_TMR_CARD")
    if env:
        return Path(env).resolve()
    return (_REPO_ROOT / "demo-output" / "website" / "tmr"
            / "flatplate_sst.json").resolve()


def _uq_studies_root() -> Path:
    env = os.environ.get("CERTONOMOUS_UQ_STUDIES")
    if env:
        return Path(env).resolve()
    return (_REPO_ROOT / "models" / "curriculum" / "uq-studies").resolve()


def _results_root() -> Path:
    env = os.environ.get("CERTONOMOUS_CREDENTIALS")
    if env:
        return Path(env).resolve()
    return (_REPO_ROOT / "models" / "curriculum" / "results").resolve()


def _ledger_study_path() -> Path:
    env = os.environ.get("CERTONOMOUS_LEDGER_STUDY")
    if env:
        return Path(env).resolve()
    return (_REPO_ROOT / "demo-output" / "website" / "mega-batch"
            / "learned_study.json").resolve()


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


# --------------------------------------------------------------------------
# Style rails — user-visible proposal text obeys the house register
# --------------------------------------------------------------------------

# Patterns that must never reach a proposal card. Checked on every visible
# field of every proposal, drafted or inbox.
_BANNED_PATTERNS: tuple[tuple[re.Pattern, str], ...] = (
    (re.compile("[–—]"), "a dash"),
    (re.compile(r"\blive\b", re.I), "the word live"),
    (re.compile(r"\bsolver[\s-]backed\b", re.I), "solver backed"),
    (re.compile(r"\bconceptual model\b", re.I), "conceptual model"),
    (re.compile(r"https?://|www\.", re.I), "a raw URL"),
    (re.compile(r"\.(?:md|py|html|jsonl|json|stl|obj|txt|yaml|yml|cfg|toml)\b",
                re.I),
     "an internal file reference"),
    (re.compile(r"[A-Za-z0-9_.-]+[\\/][A-Za-z0-9_.-]+[\\/]"), "a file path"),
)

_VISIBLE_FIELDS = ("objective", "rationale", "expected_knowledge_gain",
                   "cost_basis", "dismiss_reason")


def text_violations(text: str) -> list[str]:
    """Every banned token the given user-visible text carries."""
    found = []
    for pattern, label in _BANNED_PATTERNS:
        if pattern.search(text or ""):
            found.append(label)
    return found


def proposal_violations(proposal: dict) -> list[str]:
    """Style-rail violations across every visible field of a proposal."""
    found: list[str] = []
    for field in _VISIBLE_FIELDS:
        for label in text_violations(str(proposal.get(field) or "")):
            found.append(f"{field}: {label}")
    for citation in proposal.get("citations") or []:
        for label in text_violations(str(citation)):
            found.append(f"citation: {label}")
    return found


def _clean(text: str) -> str:
    """Typography normalization only: long dashes become hyphens, whitespace
    collapses. Content is never rewritten."""
    text = str(text or "").replace("–", "-").replace("—", "-")
    return re.sub(r"\s+", " ", text).strip()


# --------------------------------------------------------------------------
# Proposal construction, identity, ranking
# --------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def normalize_objective(objective: str) -> str:
    return re.sub(r"\s+", " ", str(objective or "")).strip().casefold()


def proposal_id(objective: str) -> str:
    digest = sha1(normalize_objective(objective).encode("utf-8")).hexdigest()
    return "agp-" + digest[:12]


def _proposal(*, objective: str, rationale: str, citations: list[str],
              est_core_min: float | None, cost_basis: str,
              expected_knowledge_gain: str, source_kind: str,
              launch_prompt: str | None = None) -> dict | None:
    """Build one schema-complete proposal; a proposal whose text breaks the
    style rails is dropped (never silently rewritten into something the
    record does not say)."""
    item = {
        "id": proposal_id(objective),
        "objective": _clean(objective),
        "rationale": _clean(rationale),
        "citations": [_clean(c) for c in citations if _clean(c)],
        "est_core_min": round(float(est_core_min), 2) if est_core_min else None,
        "cost_basis": _clean(cost_basis),
        "expected_knowledge_gain": _clean(expected_knowledge_gain),
        "source_kind": source_kind,
        "status": "proposed",
        "created_at": _now_iso(),
    }
    if launch_prompt:
        item["launch_prompt"] = _clean(launch_prompt)
    if proposal_violations(item):
        return None
    return item


# Kinds that fell through to the default, recorded so the gap is visible.
# Refusing an unknown kind outright would be the stricter fix, but agents file
# proposals continuously and a hard refusal drops work on the floor. Ranking on
# the default is survivable; ranking on the default and nobody KNOWING is what
# let three kinds sit unscored across 24 proposals.
_UNSCORED_KINDS: set[str] = set()


def unscored_kinds() -> set[str]:
    """Source kinds seen that carry no explicit gain score.

    Non-empty means the ranking is partly running on the default and
    `_GAIN_POINTS` needs a decision, not that anything has crashed.
    """
    return set(_UNSCORED_KINDS)


def gain_points(proposal: dict) -> float:
    kind = str(proposal.get("source_kind"))
    if kind not in _GAIN_POINTS:
        _UNSCORED_KINDS.add(kind)
    return _GAIN_POINTS.get(kind, _GAIN_DEFAULT)


def rank_value(proposal: dict) -> float:
    """Expected knowledge gain per core-minute (the documented heuristic)."""
    est = proposal.get("est_core_min")
    try:
        cost = float(est) if est else RANK_FLOOR_CORE_MIN
    except (TypeError, ValueError):
        cost = RANK_FLOOR_CORE_MIN
    return gain_points(proposal) / max(cost, RANK_FLOOR_CORE_MIN)


def ranked(proposals: Iterable[dict]) -> list[dict]:
    """Deterministic order: gain per core-minute descending, objective, id."""
    return sorted(proposals, key=lambda p: (
        -rank_value(p),
        normalize_objective(p.get("objective", "")),
        str(p.get("id", ""))))


# --------------------------------------------------------------------------
# Drafters — one per kind of real record
# --------------------------------------------------------------------------

# Report lines that describe a deferred capability rather than a follow-on
# measurement with today's tooling.
_CAPABILITY_HINT = re.compile(
    r"harmonic[\s-]balance|fluid[\s-]structure|non[\s-]?newtonian|"
    r"full[\s-]configuration|unsteady", re.I)


def _iter_report_payloads() -> Iterable[tuple[str, list[str]]]:
    """Yield (report title, next-investigation lines) from every report event
    artifact under the report roots. Both event encodings are read: a JSON
    file holding a list (or {events: []}) and a JSONL file of one event per
    line."""
    for root in _report_roots():
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.events.json")):
            data = _load_json(path)
            events = data.get("events") if isinstance(data, dict) else data
            yield from _report_events(events or [])
        for path in sorted(root.rglob("*.events.jsonl")):
            events = []
            try:
                for line in path.read_text(encoding="utf-8",
                                           errors="replace").splitlines():
                    line = line.strip()
                    if line:
                        events.append(json.loads(line))
            except Exception:
                continue
            yield from _report_events(events)


def _report_events(events: list) -> Iterable[tuple[str, list[str]]]:
    for event in events:
        if not isinstance(event, dict):
            continue
        if (event.get("event") or event.get("type")) != "report.ready":
            continue
        payload = event.get("payload") or event
        title = _clean(payload.get("title") or "")
        lines = [_clean(line) for line in
                 (payload.get("next_investigations") or []) if _clean(line)]
        if title and lines:
            yield title, lines


def draft_report_proposals() -> list[dict]:
    """One proposal per next-investigation line a mission report filed."""
    out: list[dict] = []
    for title, lines in _iter_report_payloads():
        for line in lines:
            head = line.split(":", 1)[0].strip()
            objective = head if len(head) >= 8 else line
            deferred = bool(_CAPABILITY_HINT.search(line))
            proposal = _proposal(
                objective=objective,
                rationale=(f'Filed under next investigations by the mission '
                           f'report "{title}": {line}.'),
                citations=[title],
                est_core_min=(_EST_CAPABILITY_CORE_MIN if deferred
                              else _EST_REPORT_CORE_MIN),
                cost_basis="estimate",
                expected_knowledge_gain=(
                    "A capability the report deferred becomes runnable in "
                    "this lab" if deferred else
                    "Answers a follow-on question the mission report filed "
                    "on the record"),
                source_kind="capability" if deferred else "report")
            if proposal:
                out.append(proposal)
    return out


def draft_tmr_proposals() -> list[dict]:
    """The verification program's next unmeasured case, read from the card
    artifacts themselves (canonical sequence: flat plate, bump-in-channel,
    NACA 0012). Hermetic: only the card path decides, never module state."""
    card = _load_json(_tmr_card_path())
    if not isinstance(card, dict) or not card.get("grids"):
        return []
    bump = _load_json(_tmr_card_path().parent / "bump_sst.json")
    if isinstance(bump, dict) and bump.get("grids"):
        return [_draft_tmr_naca0012(bump)]
    grids = card["grids"]
    fine = grids[-1] if grids else {}
    comparison = card.get("comparison") or {}
    cfl3d_ladder = comparison.get("cfl3d_cd_ladder") or []
    wall_core_min = sum(float(g.get("wall_seconds") or 0) for g in grids) / 60.0
    fine_cd = fine.get("cd")
    cfl3d_fine = cfl3d_ladder[-1] if cfl3d_ladder else None
    versus = (f"fine-grid Cd {float(fine_cd):.6f} vs CFL3D "
              f"{float(cfl3d_fine):.6f} on the same grid size"
              if fine_cd is not None and cfl3d_fine is not None
              else "with the ladder graded against the reference codes")
    proposal = _proposal(
        objective="Run the bump-in-channel verification case on a "
                  "three-grid ladder",
        rationale=(f"The flat plate is measured on a three-grid ladder, "
                   f"{versus}, and the resource card names bump-in-channel "
                   f"as the next verification case."),
        citations=["NASA Turbulence Modeling Resource verification cases",
                   "Flat-plate verification card, k-omega SST"],
        est_core_min=_EST_TMR_BUMP_CORE_MIN,
        cost_basis=(f"estimate; the measured flat-plate three-grid ladder "
                    f"ran {wall_core_min:.1f} core minutes on this machine "
                    f"and the bump grids carry more cells"),
        expected_knowledge_gain=(
            "A second verification case earned against the reference "
            "ladders, adding a curved wall and pressure gradient to the "
            "verified set"),
        source_kind="capability")
    return [proposal] if proposal else []


def _draft_tmr_naca0012(bump: dict) -> dict:
    """With flat plate and bump both measured, the sequence's next case."""
    grids = bump.get("grids") or []
    wall_core_min = sum(float(g.get("wall_seconds") or 0) for g in grids) / 60.0
    # Three alpha points per the reference tables, plus headroom for the
    # tighter airfoil convergence; anchored to the measured bump ladder.
    est = round(wall_core_min * 3 * 1.5, 0) if wall_core_min else 600.0
    return _proposal(
        objective=("Run the TMR 2D NACA 0012 airfoil case on the three "
                   "coarsest reference grid sizes at 0, 10, and 15 degrees "
                   "and compare lift, drag, and surface pressure against "
                   "the published CFL3D and FUN3D values"),
        rationale=("Flat plate and bump-in-channel are both measured on "
                   "three-grid ladders against the reference codes; the "
                   "resource's verification sequence names the NACA 0012 "
                   "airfoil as the next case."),
        citations=["NASA Turbulence Modeling Resource verification cases",
                   "Bump-in-channel verification card, k-omega SST"],
        est_core_min=est,
        cost_basis=(f"estimate; the measured bump three-grid ladder ran "
                    f"{wall_core_min:.1f} core minutes on this machine, "
                    f"scaled for three alpha points with headroom"
                    if wall_core_min else
                    "estimate; anchored to the measured bump ladder"),
        expected_knowledge_gain=(
            "A lifting-surface verification credential with published "
            "reference polars, completing the resource's core sequence"),
        source_kind="capability")


# Bodies the router can stage from a plain-language prompt, so an approval
# can launch the exact mission the proposal describes. Anything absent here
# is drafted without a launch prompt and approval simply puts it on record.
_LAUNCHABLE_BODIES = {
    "naca0012_wing": "Mesh and solve the NACA 0012 wing and report the drag "
                     "with its envelope.",
    "naca4412_wing": "Mesh and solve the NACA 4412 wing and report the drag "
                     "with its envelope.",
}


def draft_gate_proposals() -> list[dict]:
    """Failed or inconclusive gates: refinement ladders that ended without a
    conclusive band, and graded bodies still outside their validation band."""
    out: list[dict] = []

    # (a) grid-refinement studies whose numerical verdict is inconclusive
    root = _uq_studies_root()
    if root.exists():
        for path in sorted(root.glob("*.json")):
            data = _load_json(path)
            if not isinstance(data, dict):
                continue
            numerical = data.get("numerical") or {}
            levels = data.get("levels") or []
            if numerical.get("conclusive") is not False or len(levels) < 3:
                continue
            body = display_name(data.get("body") or path.stem)
            cds = ", ".join(f"{float(lv.get('cd')):.4f}" for lv in levels
                            if lv.get("cd") is not None)
            # The rationale quotes the study's OWN recorded verdict, never a
            # blanket diagnosis: a non-monotone ladder and an out-of-range
            # observed order are different findings and each record says
            # which one it made.
            method = _clean(numerical.get("method") or
                            "the study recorded no conclusive band")
            ordinals = {3: "fourth", 4: "fifth", 5: "sixth"}
            next_rung = ordinals.get(len(levels), f"{len(levels) + 1}th")
            top_cells = levels[-1].get("cells")
            cells_note = (f"the finest rung holds {int(top_cells):,} cells "
                          f"and the next roughly doubles it"
                          if top_cells else "the next rung refines further")
            proposal = _proposal(
                objective=f"Add a {next_rung} refinement rung to the {body} "
                          f"grid ladder",
                rationale=(f"The refinement study ended inconclusive: Cd "
                           f"{cds} across the rungs, and the record states "
                           f"the verdict as: {method}. A further rung can "
                           f"settle the observed order."),
                citations=[f"{body} grid-refinement study"],
                est_core_min=_EST_LADDER_RUNG_CORE_MIN,
                cost_basis=f"estimate; {cells_note}",
                expected_knowledge_gain=(
                    f"A conclusive observed order and a tighter numerical "
                    f"band for the {body} drag"),
                source_kind="gate")
            if proposal:
                out.append(proposal)

    # (b) graded bodies outside their validation band (regime-mismatch rows
    # are excluded: their next step is a matched reference, not a re-solve)
    results = _results_root()
    if results.exists():
        for path in sorted(results.glob("*.json")):
            data = _load_json(path)
            if not isinstance(data, dict):
                continue
            tier = str(data.get("tier") or "")
            if tier in ("", "VALIDATED") or "MISMATCH" in tier:
                continue
            name = data.get("name") or path.stem
            body = display_name(name)
            compared = data.get("cd_compared")
            reference = data.get("reference_cd")
            source = data.get("reference_source")
            if compared is None or not reference or not source:
                continue
            pct = abs(float(compared) - float(reference)) / abs(
                float(reference)) * 100.0
            wall_minutes = data.get("wall_minutes")
            if wall_minutes:
                est, basis = float(wall_minutes), (
                    f"measured: the prior graded solve of this body ran "
                    f"{float(wall_minutes):.1f} minutes of wall time")
            else:
                est, basis = _EST_REPORT_CORE_MIN, "estimate"
            proposal = _proposal(
                objective=f"Close the validation gap on the {body}",
                rationale=(f"The graded record stands at Cd "
                           f"{float(compared):.4g} against the reference "
                           f"{float(reference):.3g}, {pct:.0f} percent off "
                           f"and outside the validation band; a refined "
                           f"near-wall setup can close the gap or explain "
                           f"it on the record."),
                citations=[f"Graded curriculum record, {body}",
                           str(source)],
                est_core_min=est,
                cost_basis=basis,
                expected_knowledge_gain=(
                    f"Either a validated credential for the {body} or a "
                    f"measured account of why the setup misses the "
                    f"reference"),
                source_kind="gate",
                launch_prompt=_LAUNCHABLE_BODIES.get(str(name)))
            if proposal:
                out.append(proposal)
    return out


def draft_ledger_proposals() -> list[dict]:
    """Measured fleet-ledger trends pointing past the current sweep bounds."""
    study = _load_json(_ledger_study_path())
    if not isinstance(study, dict):
        return []
    valve = study.get("valve") or {}
    best = valve.get("best") or {}
    angle = best.get("opening_angle_deg")
    loss = best.get("cycle_weighted_loss_Pa")
    if angle is None or loss is None or float(angle) < 80.0:
        return []
    fit = (valve.get("trend_loss_vs_angle") or {}).get("fit") or {}
    n_rows = valve.get("n") or fit.get("n") or 0
    trend = ""
    if fit.get("slope") is not None and fit.get("r2") is not None:
        trend = (f"; the measured trend is {float(fit['slope']):.0f} Pa per "
                 f"degree (r squared {float(fit['r2']):.2f}) over "
                 f"{int(n_rows)} evaluations")
    family = (study.get("families") or {}).get("reduced-order") or {}
    attempted = family.get("attempted")
    wall = family.get("wall_seconds")
    if attempted and wall is not None:
        basis = (f"measured: {int(attempted)} reduced-order valve "
                 f"evaluations on the ledger totalled {float(wall):.0f} "
                 f"seconds; an extension screen rounds up to one core "
                 f"minute")
    else:
        basis = "estimate"
    proposal = _proposal(
        objective="Extend the valve opening-angle sweep past 80 degrees",
        rationale=(f"The fleet ledger's reduced-order screen finds its "
                   f"lowest cycle-weighted loss, {float(loss):.0f} Pa at "
                   f"{float(angle):.1f} degrees, past the engineering "
                   f"sweep's 80 degree bound{trend}."),
        citations=["Fleet-ledger learned study",
                   "Mega-batch ledger, reduced-order valve family"],
        est_core_min=RANK_FLOOR_CORE_MIN,
        cost_basis=basis,
        expected_knowledge_gain=(
            "Confirms or bounds the loss trend where the current sweep "
            "stops, and relocates the optimum if it lies past 80 degrees"),
        source_kind="ledger")
    return [proposal] if proposal else []


def read_inbox() -> list[dict]:
    """Proposals other overnight agents dropped as JSON files. Each file is
    schema-checked and style-checked; a file that breaks the rails is skipped
    rather than displayed."""
    root = inbox_dir()
    if not root.exists():
        return []
    out: list[dict] = []
    for path in sorted(root.glob("*.json")):
        data = _load_json(path)
        if not isinstance(data, dict):
            continue
        objective = _clean(data.get("objective") or "")
        if not objective:
            continue
        est = data.get("est_core_min")
        try:
            est = round(float(est), 2) if est is not None else None
        except (TypeError, ValueError):
            est = None
        status = str(data.get("status") or "proposed")
        item = {
            "id": str(data.get("id") or proposal_id(objective)),
            "objective": objective,
            "rationale": _clean(data.get("rationale") or ""),
            "citations": [_clean(c) for c in (data.get("citations") or [])
                          if _clean(c)],
            "est_core_min": est,
            "cost_basis": _clean(data.get("cost_basis") or "estimate"),
            "expected_knowledge_gain": _clean(
                data.get("expected_knowledge_gain") or ""),
            "source_kind": str(data.get("source_kind") or "inbox"),
            "status": status if status in STATUSES else "proposed",
            "created_at": str(data.get("created_at") or _now_iso()),
        }
        launch_prompt = _clean(data.get("launch_prompt") or "")
        if launch_prompt:
            item["launch_prompt"] = launch_prompt
        if proposal_violations(item):
            continue
        out.append(item)
    return out


def draft_all() -> list[dict]:
    """Every proposal the current records support, deduplicated by objective.
    Drafters run before the inbox so a drafted proposal (which may carry a
    launch prompt) wins an objective tie against an inbox duplicate."""
    merged: dict[str, dict] = {}
    for proposal in (draft_tmr_proposals() + draft_gate_proposals()
                     + draft_ledger_proposals() + draft_report_proposals()
                     + read_inbox()):
        key = normalize_objective(proposal["objective"])
        if key and key not in merged:
            merged[key] = proposal
    return list(merged.values())


# --------------------------------------------------------------------------
# Docket persistence — atomic, deduplicated, decision-preserving
# --------------------------------------------------------------------------

def load_docket() -> list[dict]:
    data = _load_json(docket_path())
    if isinstance(data, dict):
        data = data.get("proposals")
    return [p for p in (data or []) if isinstance(p, dict) and p.get("id")]


def save_docket(proposals: list[dict]) -> None:
    """Atomic write: serialize to a staging file, then replace, so a crash
    can never leave a half-written docket."""
    path = docket_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"generated_at": _now_iso(), "proposals": list(proposals)}
    staging = path.with_suffix(".json.tmp")
    staging.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    staging.replace(path)


def refresh_docket() -> list[dict]:
    """Draft from the current records, merge with the persisted docket, save,
    and return the ranked result. Existing entries always win the merge: a
    decision (approved, dismissed, done) is never overwritten by a re-draft,
    and drafted text stays as first recorded."""
    with _LOCK:
        existing = load_docket()
        by_id = {p["id"]: p for p in existing}
        by_objective = {normalize_objective(p.get("objective", "")): p
                        for p in existing}
        for proposal in draft_all():
            if proposal["id"] in by_id:
                continue
            key = normalize_objective(proposal["objective"])
            if key in by_objective:
                continue
            by_id[proposal["id"]] = proposal
            by_objective[key] = proposal
        result = ranked(by_id.values())
        if result != existing:
            save_docket(result)
        return result


def docket_view() -> dict:
    """The JSON the control room reads: the refreshed docket in rank order."""
    proposals = refresh_docket()
    return {
        "proposals": proposals,
        "open_count": sum(1 for p in proposals
                          if p.get("status") in OPEN_STATUSES),
        "ranking": "expected knowledge gain per core minute, deterministic",
        "generated_at": _now_iso(),
    }


def get_proposal(proposal_id_: str) -> dict | None:
    with _LOCK:
        for proposal in load_docket():
            if proposal.get("id") == proposal_id_:
                return proposal
    return None


def set_status(proposal_id_: str, status: str, *,
               dismiss_reason: str | None = None,
               mission_id: str | None = None) -> dict | None:
    """Record a human decision (or a launch) on the docket, atomically."""
    if status not in STATUSES:
        raise ValueError(f"unknown status: {status}")
    with _LOCK:
        proposals = load_docket()
        target = None
        for proposal in proposals:
            if proposal.get("id") == proposal_id_:
                target = proposal
                break
        if target is None:
            return None
        target["status"] = status
        target["decided_at"] = _now_iso()
        if dismiss_reason is not None:
            target["dismiss_reason"] = _clean(dismiss_reason)
        if mission_id is not None:
            target["mission_id"] = mission_id
        save_docket(ranked(proposals))
        return target
