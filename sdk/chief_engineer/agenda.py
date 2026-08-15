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
     hard_criterion, status: proposed|approved|approved-queued|dismissed|done,
     created_at, decided_at?, dismiss_reason?, outcome?, mission_id?,
     launch_prompt?, archive_replay?}

``hard_criterion`` is the case-selection charter's hardness floor made a
field (P-3.1, carried out 2026-08-05): every proposal filed from
``SCHEMA_REQUIRED_FROM`` names the numbered HARD criterion it satisfies, or
one of the closed set of answers that charter's own text already allows, and
an absent or unrecognised value is refused at intake. Proposals created
before that date are grandfathered where they stand: the 221 docket entries
of 2026-08-04 are not rewritten, and three of them state their criterion in
prose only, which the grandfather line accepts and the field now forbids.

``archive_replay`` is charter 1 disqualifier 10 made a field (P-1.4,
carried out 2026-08-05): a proposal that adds a detection or monitor rule,
a log signature or a detector — anything that will fire on the lab's own
work — carries a record of what it does to the archive before it is
adopted, or it is refused at intake. See ``archive_replay_violations`` for
the required fields and the S12 replay that is the pattern.

A proposal marked ``done`` carries an ``outcome``: one sentence saying what
the work actually found, with the numbers in it. Without that field a done
card on the panel shows only what the lab hoped to learn and never what it
learned, which is the same defect as a mission that reports no result.

Cost honesty: ``est_core_min`` is either derived from measured history (the
ledger's wall seconds for the same evaluation family, or a prior graded solve
of the same body) with the derivation quoted in ``cost_basis``, or it is a
default that ``cost_basis`` plainly labels an estimate. No cost is ever
presented as measured unless a record backs it.

One exception, and it is not a small one. A prior graded solve of the same
body stops being measured history the moment the proposal exists to replace
that solve. A repair is not the same job as the run it repairs, and a run
that is out of band or withdrawn is often cheap BECAUSE it stopped being
right early, so its wall time is not conservative in any known direction.
The NACA 0012 gap was priced at 3.04 core-minutes from exactly that field
against 180 to 240 measured on the NACA 4412 precedent that repaired the
same defect, a factor of 15 under. ``cost_basis_violations`` refuses such a
basis at intake and names the run; ``refused_cost_bases`` keeps the refusals
visible so a refusal is never a silent drop.

Ranking heuristic (deterministic, the whole of it):

* Each proposal earns gain points by source kind, from `_GAIN_POINTS`, which
  covers every kind in use: challenge 4, measurement and gate 3, capability,
  ledger, reading and inbox 2, report 1. An unrecognised kind is a proposal
  violation at intake from `SCHEMA_REQUIRED_FROM` (P-1.1, carried out
  2026-08-05); rows grandfathered before that date still rank on the default
  and are recorded in `unscored_kinds()` rather than silently.
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

from . import uq
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
    "inbox": 2.0,          # read_inbox's default for a file naming no kind;
                           # it was always documented as scoring 2 and was
                           # never in this table, so it scored 2 by falling
                           # through. Stated now (P-1.1, 2026-08-05).
}
_GAIN_DEFAULT = 2.0

# The date the two intake refusals below start binding (P-1.1 and P-3.1,
# both carried out 2026-08-05 under the standing charter-iteration
# directive). Proposals created before this date are grandfathered where
# they stand: the docket's existing entries are never rewritten and never
# refused retroactively, they only stop being the pattern for new ones. A
# proposal carrying no created_at at all is treated as new, because every
# path that builds one stamps the date and a dateless record has nothing to
# be grandfathered by.
SCHEMA_REQUIRED_FROM = "2026-08-05"

# The closed value set for `hard_criterion`. The six numbers are the owner's
# six HARD criteria (CASE_SELECTION_CHARTER.md section 2; the list is hers
# and closed). The five words are not new policy: each one is an answer the
# case-selection charter's own text already allows, rendered filable so that
# requiring the field does not refuse work the charter permits.
HARD_CRITERIA = ("1", "2", "3", "4", "5", "6")
HARD_CRITERION_WORDS = (
    # Extends a family already on the record. Charter 3 section 4 binds
    # families "the lab has not run before"; the floor for this one was
    # answered when the family entered, and the follow-on says so.
    "existing-family",
    # Charter 3 section 3's two allowed cylinder-class purposes, which
    # section 9 already requires labelled at launch rather than afterwards.
    "regression-test",
    "instrument-check",
    # The proposal starts no flow case at all: a reading, a report rewrite,
    # a process or protocol change. Charter 3 governs which CASES the lab
    # starts; a proposal that starts none says so, and if pursuing it later
    # starts a family, that filing owes its own criterion.
    "no-case",
    # A new family genuinely below the floor, said out loud so the written
    # approval it needs is asked for rather than discovered. This is
    # recommendation A's own cost sentence made a filable value.
    "below-floor",
)
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


# --------------------------------------------------------------------------
# Premise rail -- charter 4 disqualifiers 11 and 12
# --------------------------------------------------------------------------
#
# WHY IT IS SEPARATE FROM proposal_violations AND ADVISORY. Replayed against
# the docket on 2026-08-02 these two shapes fire on 22 proposals. Ten of the
# thirteen that shape 1 catches were wrong on arrival (four dismissed, six
# closed only after the agent corrected the premise), and nine of the nine that
# shape 2 catches never became runnable work. That is good enough to write down
# and NOT good enough to refuse on, for a reason that has nothing to do with
# the hit rate: shape 1 asks a proposal to cite the file holding the numbers it
# quotes, and _BANNED_PATTERNS forbids a file reference in a citation. 202
# citations on the current docket already break that rail. The two rules are in
# direct conflict, the conflict is older than this function, and picking a
# winner is the owner's call rather than this file's. So this reports.
#
# A stored VERDICT is not the record. The file that stores the rungs is.
_QUOTED_SEQUENCE = re.compile(
    r"(?<![\d.])\d+\.\d+\s*,\s*\d+\.\d+\s*,\s*\d+\.\d+")
_TRANSCRIBED = re.compile(r"^\s*filed under next investigations\b", re.I)
_CITED_FILE = re.compile(
    r"[\w./-]+\.(?:json|jsonl|md|py|dat|csv)\b", re.I)


def premise_violations(proposal: dict, repo: Path | None = None) -> list[str]:
    """Premises a proposal asserts that nobody checked before filing.

    Advisory, not a refusal. See the note above for why, and charter 4
    disqualifiers 11 and 12 for the measured archive replay behind both.
    """
    found: list[str] = []
    rationale = str(proposal.get("rationale") or "")
    if _QUOTED_SEQUENCE.search(rationale):
        root = repo or Path(__file__).resolve().parents[2]
        resolved = any(
            (root / match.group(0)).exists()
            for citation in (proposal.get("citations") or [])
            for match in [_CITED_FILE.search(str(citation))] if match)
        if not resolved:
            found.append(
                "rationale: quotes a stored numeric sequence and no citation "
                "resolves to a file in the tree, so the premise was not read "
                "at drafting (charter 4 disqualifier 11)")
    if _TRANSCRIBED.search(rationale):
        found.append(
            "rationale: transcribed from another document's next steps, so it "
            "is a topic rather than a proposal and names no instrument "
            "(charter 4 disqualifier 12)")
    return found


def _schema_binds(proposal: dict) -> bool:
    """Whether the 2026-08-05 intake refusals apply to this proposal.

    The grandfather line is the created_at date, which is machine-decidable
    and honest about what it is: a migration boundary, not a security
    boundary. Old records stand as filed; new ones carry the fields.
    """
    created = str(proposal.get("created_at") or "")[:10]
    return not created or created >= SCHEMA_REQUIRED_FROM


def source_kind_violations(proposal: dict) -> list[str]:
    """Refuse an unrecognised source_kind instead of scoring it silently.

    P-1.1's measured failure: three kinds in real use fell through to the
    default and 24 of 55 proposals ranked on a number nobody had stated,
    including every challenge-aligned proposal, which axis C exists to
    promote. Any stated value is better than an unstated one, so a kind the
    gain table does not carry is a violation at intake rather than a default
    at ranking time. Grandfathered rows still rank on the default (see
    gain_points) so an old docket never stops loading.
    """
    if not _schema_binds(proposal):
        return []
    kind = str(proposal.get("source_kind") or "")
    if kind in _GAIN_POINTS:
        return []
    stated = ", ".join(sorted(_GAIN_POINTS))
    return [f"source_kind: {kind or '<absent>'} carries no stated gain "
            f"score and would rank on a silent default; the stated kinds "
            f"are {stated}"]


def outcome_violations(proposal: dict) -> list[str]:
    """Refuse a done proposal that does not say what the work found.

    The module's own rule (docstring, and set_status enforces it): a
    proposal marked ``done`` carries an ``outcome``, or the panel shows what
    the lab hoped to learn and never what it learned. Until the 2026-08-07
    family supervision pass (finding A-2) the invariant bound only in
    set_status, so an inbox file arriving with status done and no outcome
    rode through intake; two such records reached the docket by direct edit.
    Same grandfather line as the other schema rails: old records stand as
    filed, new ones carry the field.
    """
    if not _schema_binds(proposal):
        return []
    if (str(proposal.get("status") or "") == "done"
            and not str(proposal.get("outcome") or "").strip()):
        return ["status: done with no outcome; a proposal cannot be closed "
                "without saying what closing it found"]
    return []


def hard_criterion_violations(proposal: dict) -> list[str]:
    """Refuse a proposal that does not name its hardness-floor answer.

    P-3.1: the floor moves from discipline into the harness, the same move
    D12 made for orphaned collectors after writing the rule down failed to
    change the rate. The value is one of the owner's six criteria by number,
    or one of the closed answers charter 3's own text allows (see
    HARD_CRITERION_WORDS). Prose in the rationale, which is how the three
    2026-08-04 proposals stated it, no longer satisfies the field.
    """
    if not _schema_binds(proposal):
        return []
    value = proposal.get("hard_criterion")
    normalised = str(value).strip() if value is not None else ""
    if normalised in HARD_CRITERIA or normalised in HARD_CRITERION_WORDS:
        return []
    allowed = ("1 to 6 (CASE_SELECTION_CHARTER.md section 2) or one of "
               + ", ".join(HARD_CRITERION_WORDS))
    if not normalised:
        return [f"hard_criterion: absent; every proposal names the "
                f"hardness-floor answer it rides on: {allowed}"]
    return [f"hard_criterion: {normalised!r} is outside the closed list: "
            f"{allowed}"]


# --------------------------------------------------------------------------
# Archive-replay rail -- charter 1 disqualifier 10 (P-1.4)
# --------------------------------------------------------------------------
#
# A rule is an instrument, and an instrument that was never pointed at the
# archive is a hypothesis in a uniform. S7 is the measured reason: adopted on
# reasoning alone, later replayed firing on 68 of 106 archived steady logs
# and reaching FATAL on 65, every one a completed run whose results are on
# the record (C-2, withdrawn). The pattern a new rule follows instead is
# S12's: before adoption it was replayed over 760 quantity-histories from
# 380 archived coefficient.dat files, 718 gradeable, and the record states
# the corpus, the fire count (36, 4.74 percent), the fatal count (0) and its
# behaviour on the motivating case (fires on the flat-plate rung stopped at
# 15000, silent on the same case settled at 21000). MONITOR_STANDARD.md
# section 3.1 carries that line, and this rail requires every new
# detection-rule proposal to arrive with one of its own.
#
# The trigger is textual because the source kinds are a closed set and none
# of them is "detection rule": a proposal that proposes one says so in its
# objective or rationale. The patterns are deliberately tight -- "rule",
# "gate" and "check" alone appear all over ordinary proposals -- so a false
# negative slips a rule past intake to be caught at review, while a false
# positive would refuse honest work, which is the worse error here.
_DETECTION_RULE_SHAPE = re.compile(
    r"\b(?:detection|detector|monitor(?:ing)?)\s+rule\b"
    r"|\blog[\s-]signatures?\b"
    r"|\bnew\s+(?:signature|detector)\b"
    r"|\b(?:add|adds|adding|adopt|adopts|introduce|introduces)\b"
    r"[^.!?]{0,80}\b(?:detection rule|signature|detector)\b", re.I)

# What an archive-replay record states, each the disqualifier's own words:
# the corpus it was replayed against, the number of logs it fires on, the
# number it calls fatal, and its behaviour on the case that motivated it.
ARCHIVE_REPLAY_FIELDS = ("corpus", "fires", "fatal", "motivating_case")


def is_detection_rule_proposal(proposal: dict) -> bool:
    """Whether the proposal's own text says it adds a rule that will fire
    on the lab's work."""
    text = (str(proposal.get("objective") or "") + " "
            + str(proposal.get("rationale") or ""))
    return bool(_DETECTION_RULE_SHAPE.search(text))


def archive_replay_violations(proposal: dict) -> list[str]:
    """Refuse a detection-rule proposal that has not met the archive.

    P-1.4: disqualifier 10 moves from review discipline into the harness,
    the same move P-3.1 made for the hardness floor. A proposal whose text
    proposes a detection or monitor rule carries an ``archive_replay``
    record naming the corpus, the fire count, the fatal count and the
    behaviour on the motivating case -- the four things the disqualifier
    names, and the four things S12's replay line states. Fires may be zero
    is a finding too (S2 fires on nothing); what is refused is arriving
    without the measurement, which is exactly how S7 got in.
    """
    if not _schema_binds(proposal) or not is_detection_rule_proposal(proposal):
        return []
    pattern = ("the S12 unsettled-stop replay is the pattern: 760 "
               "quantity-histories from 380 archived coefficient files, "
               "36 fires, 0 fatal, and the motivating rung fired on while "
               "its settled sibling stayed silent")
    replay = proposal.get("archive_replay")
    if not isinstance(replay, dict) or not replay:
        return [f"archive_replay: absent on a detection-rule proposal; "
                f"a rule states what it does to the archive before "
                f"adoption ({pattern})"]
    missing = [name for name in ARCHIVE_REPLAY_FIELDS
               if str(replay.get(name) if replay.get(name) is not None
                      else "").strip() == ""]
    if missing:
        return [f"archive_replay: states no {', '.join(missing)}; every "
                f"replay record carries {', '.join(ARCHIVE_REPLAY_FIELDS)} "
                f"({pattern})"]
    return []


def proposal_violations(proposal: dict) -> list[str]:
    """Style-rail violations across every visible field of a proposal."""
    found: list[str] = []
    for field in _VISIBLE_FIELDS:
        for label in text_violations(str(proposal.get(field) or "")):
            found.append(f"{field}: {label}")
    for citation in proposal.get("citations") or []:
        for label in text_violations(str(citation)):
            found.append(f"citation: {label}")
    found.extend(cost_basis_violations(proposal))
    found.extend(source_kind_violations(proposal))
    found.extend(hard_criterion_violations(proposal))
    found.extend(archive_replay_violations(proposal))
    found.extend(outcome_violations(proposal))
    return found


# --------------------------------------------------------------------------
# Cost rail — a price may not be drawn from a run the record has since
# superseded, withdrawn or graded out of band
# --------------------------------------------------------------------------

# Runs the record itself has superseded, withdrawn or replaced. Each entry is
# (pattern, run as the record names it, where the record says so). Nothing is
# listed here on an agent's opinion: every entry quotes a field or a row that
# already exists in the tree.
_SUPERSEDED_RUNS: tuple[tuple[re.Pattern, str, str], ...] = (
    (re.compile(r"prior graded solve of (?:this|the same) body", re.I),
     "the graded solve the proposal exists to replace",
     "the graded body is outside its validation band, which is the whole "
     "reason the proposal was drafted"),
    (re.compile(r"\b67,?826[\s-]cell\b", re.I),
     "the 67,826-cell NACA 4412 credential solve",
     "the credential record's own previous_credential entry supersedes it: "
     "layer addition was off at chord Reynolds 1e6, so there are no "
     "boundary-layer cells, and no mesh was archived"),
    (re.compile(r"\b45,?760[\s-]cell\b", re.I),
     "the 45,760-cell Ahmed adjoint primal",
     "the research board withdraws it: the turbulence field diverged while "
     "the normalised residual read as converged"),
)

# Words that turn naming a superseded run from a price into a disclosure. A
# basis that says the run was superseded is not pricing from it, it is saying
# why it did not. This is a weaker test than reading the sentence and it is
# stated as one: the rail distinguishes the two cases by these words alone.
_SUPERSESSION_DISCLOSED = re.compile(
    r"supersed|withdraw|defect|not priced from|is a floor", re.I)

# Bases refused at intake, kept so a refusal is visible rather than a silent
# drop. Same reasoning as _UNSCORED_KINDS below: a filter nobody can see is a
# filter nobody can question.
_REFUSED_COST_BASES: list[dict] = []


def refused_cost_bases() -> list[dict]:
    """Every cost basis this process refused, with the run each one named."""
    return [dict(entry) for entry in _REFUSED_COST_BASES]


def cost_basis_violations(proposal: dict) -> list[str]:
    """Refuse a price taken from a run the lab has since superseded.

    The charter's measured-history clause allows a prior graded solve of the
    same body. That clause has one hole, and the lab has already fallen
    through it: when the proposal exists to REPLACE that solve, the solve is
    not history, it is the defect. A repair is a different job, and a
    defective run is cheap partly because it stopped being right early, so
    the error has no known direction. Naming the run in order to disclose it
    is the opposite of pricing from it and is allowed.
    """
    basis = str(proposal.get("cost_basis") or "")
    if not basis or _SUPERSESSION_DISCLOSED.search(basis):
        return []
    found = []
    for pattern, run, why in _SUPERSEDED_RUNS:
        if pattern.search(basis):
            found.append(f"cost_basis: priced from {run}, which the record "
                         f"has superseded ({why})")
            _REFUSED_COST_BASES.append({
                "id": str(proposal.get("id") or ""),
                "objective": str(proposal.get("objective") or ""),
                "run": run, "why": why, "cost_basis": basis})
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
              hard_criterion: str,
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
        "hard_criterion": str(hard_criterion).strip(),
        "status": "proposed",
        "created_at": _now_iso(),
    }
    if launch_prompt:
        item["launch_prompt"] = _clean(launch_prompt)
    if proposal_violations(item):
        return None
    return item


# Kinds that fell through to the default, recorded so the gap is visible.
# From SCHEMA_REQUIRED_FROM an unknown kind is refused at intake
# (source_kind_violations), so this ledger's remaining job is the
# grandfathered rows: entries already on the docket rank on the default and
# are recorded here rather than silently, because an old docket must always
# load and rank, and a filter nobody can see is a filter nobody can question.
_UNSCORED_KINDS: set[str] = set()


def unscored_kinds() -> set[str]:
    """Source kinds seen that carry no explicit gain score.

    Non-empty means the ranking is partly running on the default for
    grandfathered rows and `_GAIN_POINTS` needs a decision, not that
    anything has crashed. New proposals cannot add to this set: an unknown
    kind is refused at intake from SCHEMA_REQUIRED_FROM.
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
                source_kind="capability" if deferred else "report",
                # A report's next-investigation line is a topic, not a case:
                # it selects no geometry, no regime and no instrument
                # (charter 1 disqualifier 12 measured nine of nine such
                # items never becoming runnable work). The filing that turns
                # one into a case owes the criterion; this one starts none.
                hard_criterion="no-case")
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
        # _proposal returns None when a style rail trips, so the guard the
        # flat-plate branch has always had applies here too: a rail-trip is
        # a dropped proposal, never a None riding into draft_all to crash
        # the whole docket refresh (found in the 2026-08-07 family
        # supervision pass, finding A-1).
        naca = _draft_tmr_naca0012(bump)
        return [naca] if naca else []
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
        source_kind="capability",
        # The next case of the verification sequence already on the record:
        # the flat plate is measured, the resource card names this one.
        hard_criterion="existing-family")
    return [proposal] if proposal else []


def _draft_tmr_naca0012(bump: dict) -> dict | None:
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
        source_kind="capability",
        hard_criterion="existing-family")


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
            # A RUNG IS NOT A RUNG UNLESS IT IS A MESH. This branch drafts one
            # thing only -- "add another refinement rung" -- and that sentence
            # is nonsense for a channel that has no meshes to refine. The test
            # is the study's own structural guard plus the rungs themselves:
            # a mesh rung records a cell count and a functional, and a level
            # that records neither cannot be the finest of anything.
            #
            # THIS WAS LATENT, AND ONE COINCIDENCE DEEP. The aortic valve
            # declines on `not_a_discretization_ladder` -- its levels are
            # k = 3/5/9 segments of a half-sine waveform, closed-form, no mesh
            # anywhere -- and the only reason this drafter never proposed a
            # fourth grid rung for it is that it stored no `levels` at all.
            # Give that record the rungs it owes its reader (2026-08-01) and
            # the drafter reaches it. Measured then: the proposal is still not
            # emitted, but only because the method string it quotes contains
            # the literal "3/5/9", which the style rails read as a file path
            # and drop. Reword the method and the proposal ships. A guard that
            # holds on a slash in someone else's sentence is not a guard.
            guards_failed = numerical.get("guards_failed") or []
            if uq.GUARD_NOT_A_DISCRETIZATION_LADDER in guards_failed:
                continue
            if not all(lv.get("cells") and lv.get("cd") is not None
                       for lv in levels):
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
            # THE HALF THIS DRAFTER CANNOT PRICE, AND NOW SAYS SO. Every
            # proposal it has ever emitted priced the grid, because a stored
            # ladder records cells per rung and records no iterations at all.
            # The flat plate's finest rung came in at 1.48x its estimate and
            # the whole overrun was settling: it was asked for 15,000
            # iterations and took 36,000. Measured on this lab's own ledger,
            # cost carries an exponent of essentially one on iterations, in
            # both families that record them, while cells barely vary within a
            # family. So the term that overruns is exactly the term nobody was
            # writing down, and an omission stated is a question somebody can
            # answer before the rung is queued.
            iteration_note = (
                "the iteration count is NOT priced here: this ladder stores "
                "cells per rung and no iterations, and measured cost rises "
                "about linearly with iterations while cells barely move within "
                "a family, so this figure prices the grid alone and the "
                "settling is the term that can overrun")
            proposal = _proposal(
                objective=f"Add a {next_rung} refinement rung to the {body} "
                          f"grid ladder",
                rationale=(f"The refinement study ended inconclusive: Cd "
                           f"{cds} across the rungs, and the record states "
                           f"the verdict as: {method}. A further rung can "
                           f"settle the observed order."),
                citations=[f"{body} grid-refinement study"],
                est_core_min=_EST_LADDER_RUNG_CORE_MIN,
                cost_basis=f"estimate; {cells_note}. {iteration_note}",
                expected_knowledge_gain=(
                    f"A conclusive observed order and a tighter numerical "
                    f"band for the {body} drag"),
                source_kind="gate",
                # A further rung on a ladder the record already holds; the
                # floor was answered when the family entered.
                hard_criterion="existing-family")
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
            # This record is OUT OF BAND, which is the entire reason the
            # proposal is being drafted. Its own wall time is therefore the
            # wall time of the run the proposal exists to replace, and this
            # drafter used to hand that straight over as "measured". It is
            # not history, it is the defect, and the lab has the receipts
            # both ways: the NACA 0012 gap went out at 3.04 core-minutes
            # from this field against 180 to 240 measured on the NACA 4412
            # precedent that repaired the same layerless mesh, 15x under;
            # and the 4412 record's own 4.64 belonged to a superseded
            # refinement-2 act, while one rung of the ladder that produced
            # its graded drag measured 1,574.2 s of meshing plus 278.6 s of
            # solve at 4 ranks. That field was corrected at the record on
            # 2026-08-01 and now reads 2.8, the graded rung's own span, so
            # the sentence below is true of the graded solve where it used
            # to be true of nothing. The prior wall time is a floor on the repair
            # and is reported as one. The price is the charter default,
            # labelled an estimate, which is an empty number honestly
            # labelled rather than a false one.
            est = _EST_REPORT_CORE_MIN
            wall_minutes = data.get("wall_minutes")
            if wall_minutes:
                basis = (f"estimate; not priced from the graded solve of "
                         f"this body, which is the run this proposal exists "
                         f"to replace. That solve ran "
                         f"{float(wall_minutes):.1f} minutes of wall time, "
                         f"which is a floor on the repair and not a price "
                         f"for it")
            else:
                basis = "estimate"
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
                hard_criterion="existing-family",
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
        source_kind="ledger",
        # Extends the sweep of a family the ledger already measures.
        hard_criterion="existing-family")
    return [proposal] if proposal else []


# Inbox files refused at intake, keyed by filename so one read's refusals can
# be looked up by name. A skipped file used to vanish without a trace, and on
# 2026-08-07 nineteen of fifty-six inbox files were being silently dropped, two
# of them filed that same day and destined never to reach the docket with
# nothing anywhere saying so (family supervision pass, finding A-3). A filter
# nobody can see is a filter nobody can question.
#
# WHAT THIS LEDGER'S LIFETIME IS, and why it is stated here rather than left to
# be inferred (docket D111). It is ONE READ. Until 2026-08-15 it was the
# lifetime of the PROCESS: every `read_inbox()` wrote into this dict and none of
# them took anything out, so it accumulated across reads of different
# directories. A filename is meaningless without the directory it came from --
# `bad.json` in a test's temporary agenda root and `bad.json` in the live corpus
# are one key -- so refusals from a deleted temporary tree stayed in the ledger
# and were counted by `scripts/calibration_scorecard.py`'s live reconcile: 131
# files on disk against 128 admitted + 7 refused, with an EMPTY residual,
# because three of the refusals named files that were not on that disk at all.
# Guarded by `sdk/tests/test_refused_inbox_lifecycle.py`.
_REFUSED_INBOX: dict[str, dict] = {}

#: The directory the ledger above describes, so a filename in it is anchored to
#: something. `None` until the first read of this process.
_REFUSED_INBOX_ROOT: str | None = None


def _publish_refused_inbox(root: Path, refused: dict[str, dict]) -> None:
    """Replace the refusal ledger with one read's result, wholesale (D111).

    Called at every exit from ``read_inbox()``, including the one where the
    inbox directory is absent, so whatever this process did earlier the ledger
    afterwards describes THIS read of THIS directory and nothing else. That is
    what ``refused_inbox()`` has claimed since it was written; from 2026-08-15
    it is also what happens.

    `scripts/check_derived_figures.py`'s `build_registry()` clears
    `P_RANK1_NOT_SHIPPED` on the same principle and at the same point: a ledger
    a read fills is a ledger that read owns.
    """
    global _REFUSED_INBOX_ROOT
    _REFUSED_INBOX.clear()
    _REFUSED_INBOX.update(refused)
    _REFUSED_INBOX_ROOT = str(root)


def refused_inbox_root() -> str | None:
    """Which directory ``refused_inbox()`` is answering about, or None if this
    process has not read one. Exported so an empty answer below is inspectable
    rather than a filter nobody can see."""
    return _REFUSED_INBOX_ROOT


def refused_inbox() -> list[dict]:
    """Every inbox file the LAST read refused, with its violations.

    Empty when the last read refused nothing -- and also when the last read was
    of a different directory than ``inbox_dir()`` names now, because a refusal
    is a statement about a file in the directory that was read, and handing one
    directory's refusals to a caller asking about another is exactly the defect
    D111 records. ``refused_inbox_root()`` says which directory the ledger holds,
    so the two cases are told apart by asking rather than by guessing.
    """
    if _REFUSED_INBOX_ROOT != str(inbox_dir()):
        return []
    return [dict(entry) for _, entry in sorted(_REFUSED_INBOX.items())]


def read_inbox() -> list[dict]:
    """Proposals other overnight agents dropped as JSON files. Each file is
    schema-checked and style-checked; a file that breaks the rails is skipped
    rather than displayed, and the skip is recorded in ``refused_inbox()``.

    The refusals are collected locally and published at the end, so the ledger
    is replaced by this read rather than added to by it (D111).
    """
    root = inbox_dir()
    refused: dict[str, dict] = {}
    if not root.exists():
        _publish_refused_inbox(root, refused)
        return []
    out: list[dict] = []
    for path in sorted(root.glob("*.json")):
        data = _load_json(path)
        if not isinstance(data, dict):
            refused[path.name] = {
                "file": path.name, "id": "", "objective": "",
                "violations": ["file: not a JSON object"]}
            continue
        objective = _clean(data.get("objective") or "")
        if not objective:
            refused[path.name] = {
                "file": path.name, "id": str(data.get("id") or ""),
                "objective": "", "violations": ["objective: absent"]}
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
        # The hardness-floor field rides in from the file when it carries
        # one. A file created from SCHEMA_REQUIRED_FROM without it is
        # refused below by hard_criterion_violations; older files are
        # grandfathered on their own created_at, which is why the field is
        # optional here and not defaulted: defaulting it would answer the
        # floor question on the filer's behalf.
        hard = data.get("hard_criterion")
        if hard is not None and str(hard).strip():
            item["hard_criterion"] = str(hard).strip()
        # The archive-replay record rides in whole when the file carries
        # one, for the same reason hard_criterion is not defaulted: a
        # detection-rule file that arrives without it is refused below by
        # archive_replay_violations rather than quietly excused, and the
        # replay is the filer's measurement, never this reader's to invent.
        replay = data.get("archive_replay")
        if isinstance(replay, dict) and replay:
            item["archive_replay"] = {str(k): v for k, v in replay.items()}
        launch_prompt = _clean(data.get("launch_prompt") or "")
        if launch_prompt:
            item["launch_prompt"] = launch_prompt
        # The decision fields. This reader used to copy the ten proposal keys
        # above and nothing else, so a file arriving with a decision already
        # on it lost the decision on ingest: the status survived, the reason
        # for it did not. A dismissed proposal with no dismiss_reason and a
        # done proposal with no outcome both read as complete records, which
        # is the failure this whole module's `done` rule exists to prevent.
        # These are the fields the docket schema (module docstring) declares
        # optional; anything else in an inbox file is still not carried,
        # deliberately, and _INBOX_NOT_CARRIED names why.
        for key in ("decided_at", "dismiss_reason", "outcome", "mission_id"):
            value = data.get(key)
            if value in (None, ""):
                continue
            item[key] = (_clean(str(value)) if key != "decided_at"
                         else str(value))
        violations = proposal_violations(item)
        if violations:
            refused[path.name] = {
                "file": path.name, "id": item["id"],
                "objective": item["objective"], "violations": violations}
            continue
        # No `pop` here any more. It used to remove a name a PREVIOUS read had
        # refused, which was the whole of the old invalidation and covered only
        # the one case where the same directory was read twice and the file had
        # been repaired in between. Publishing the local dict below covers that
        # case and the three it missed: the file deleted, the directory
        # replaced, and the directory gone (D111).
        out.append(item)
    _publish_refused_inbox(root, refused)
    return out


# What an inbox file may carry that the docket deliberately does not keep, and
# why. Named rather than dropped in silence: a filter nobody can see is a
# filter nobody can question, and this one used to swallow every decision
# field an agent wrote.
_INBOX_NOT_CARRIED = {
    "rank": "the docket ranks its own proposals; a filed rank is an opinion",
    "score": "same, and a stale score outranks a fresh one",
    "notes": "not a docket field; say it in rationale, which is displayed",
}


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
               outcome: str | None = None,
               mission_id: str | None = None) -> dict | None:
    """Record a human decision (or a launch) on the docket, atomically.

    ``done`` requires an ``outcome`` unless the proposal already carries one:
    a proposal cannot be closed without saying what closing it found.
    """
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
        if status == "done" and not (outcome or target.get("outcome")):
            raise ValueError(
                "a proposal marked done must carry an outcome saying what "
                "the work found")
        target["status"] = status
        target["decided_at"] = _now_iso()
        if dismiss_reason is not None:
            target["dismiss_reason"] = _clean(dismiss_reason)
        if outcome is not None:
            target["outcome"] = _clean(outcome)
        if mission_id is not None:
            target["mission_id"] = mission_id
        save_docket(ranked(proposals))
        return target
