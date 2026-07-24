"""Ask-the-lab: answer a question from what the lab has actually recorded.

Directive 3 (feature #39), built once and served twice: the triage stage routes
``lab-query`` and ``advice`` prompts here, and Track A's GUI chat will call the
same :func:`answer` function later. The interface is deliberately narrow —
a question in, a grounded answer plus citations out.

Answers are grounded ONLY in what this repository holds: the case memory of runs
actually executed, the numerics knowledge base, the operating lessons, the
physics-rules thresholds, and any mission reports on disk. Every answer cites
its sources by mission id and by human display title (never a file path or a
lesson id on screen — the rendering goes through ``citations.display``). When a
question cannot be grounded, the answerer says so plainly rather than inventing
a number.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import citations, claude_lab
from .case_memory import CASE_MEMORY
from .lessons import LESSONS, learned_lessons

_STOPWORDS = {
    "the", "a", "an", "of", "on", "in", "at", "to", "for", "and", "or", "is",
    "are", "was", "were", "do", "does", "did", "we", "our", "us", "what", "how",
    "why", "which", "when", "with", "about", "have", "has", "had", "can", "could",
    "should", "would", "it", "this", "that", "run", "ran", "get", "got", "tell",
    "me", "give", "know", "many", "much", "any", "some", "from", "over", "into",
}


def _tokens(text: str) -> set[str]:
    # Keep words longer than two characters, but also keep short numeric tokens
    # (e.g. the "35" in "ahmed_35") — the digit is what distinguishes ahmed_35
    # from ahmed_25, so dropping it collapses distinct bodies into one.
    return {w for w in re.findall(r"[a-z0-9]+", (text or "").lower())
            if (len(w) > 2 or (len(w) == 2 and any(c.isdigit() for c in w)))
            and w not in _STOPWORDS}


@dataclass
class Source:
    """One retrievable fact, its searchable text, and how to cite it."""
    kind: str          # case | lesson | knowledge | physics | mission
    text: str          # searchable content
    detail: str        # the answer sentence shown to a reader
    citation: str      # raw citation string, rendered by citations.display


@dataclass
class Answer:
    grounded: bool
    text: str
    citations: list[str] = field(default_factory=list)
    sources: list[dict[str, str]] = field(default_factory=list)
    # "record" = the deterministic listing of grounded facts; "synthesized" = an
    # LLM reasoned over ONLY those same facts. Provenance is identical either way.
    mode: str = "record"

    def to_dict(self) -> dict[str, Any]:
        return {"grounded": self.grounded, "text": self.text,
                "citations": list(self.citations),
                "sources": list(self.sources), "mode": self.mode}


# --------------------------------------------------------------------------
# Optional LLM answer-synthesis
# --------------------------------------------------------------------------
#
# The deterministic layer above RETRIEVES the facts and guards provenance; the
# LLM only REASONS over the facts it is handed — comparing bodies, converting a
# coefficient to a force, focusing a dump into an answer. It is given ONLY the
# retrieved source details, never the whole corpus, so it cannot introduce a
# number the record does not hold, and it must cite exactly what retrieval
# cited. A solid record answer is kept as-is; the model is consulted only when
# the record listing alone is thin, or when the question asks for reasoning
# (rank, compare) the listing cannot do. All calls go through the shared
# ``claude_lab`` client: no key, a kill switch, or any failure means None and
# the caller keeps the deterministic behaviour — the demo never depends on the
# model.

_SYNTHESIS_SYSTEM = (
    "You answer strictly from the facts you are given, reasoning over them "
    "but never beyond them. Plain prose, no preamble, no em dashes (use "
    "commas). Never describe a result as cached, stored, saved, or "
    "pre-computed.")


def _synthesis_enabled() -> bool:
    if os.environ.get("CERTONOMOUS_ASK_LLM", "").strip() == "0":
        return False
    return claude_lab.enabled()


def _synthesize(question: str, facts: list[str]) -> str | None:
    """Reason over the retrieved facts with the shared lab model, or None.

    The model is handed the question and the retrieved facts and nothing
    else, and is told to use only those facts — so the answer stays inside
    what the lab has actually recorded. When the facts cannot answer the
    question the model says UNANSWERABLE and the caller keeps its honest
    refusal instead.
    """
    if not facts or not _synthesis_enabled():
        return None
    catalogue = "\n".join(f"- {fact}" for fact in facts)
    instructions = (
        "You are the voice of an autonomous CFD lab answering a question about "
        "its own work. Use ONLY the facts below — they are the complete record "
        "you may draw on. Do not introduce any number, body, or claim that is "
        "not present in them. If the question asks you to compare, rank, or "
        "convert (for example a drag coefficient into a force), do the reasoning "
        "explicitly from these facts and state any standard constant you use. If "
        "the facts do not answer the question, reply with the single word "
        "UNANSWERABLE. Keep it to a few sentences, precise and honest; never "
        "soften a trust caveat or agree to a value the record contradicts.\n\n"
        f"FACTS FROM THE LAB'S RECORD:\n{catalogue}\n\nQUESTION: {question}")
    reply = claude_lab.complete(_SYNTHESIS_SYSTEM, instructions,
                                max_tokens=700, effort="low")
    if not reply:
        return None
    reply = reply.replace("—", ",").strip()
    if not reply or reply.upper().startswith("UNANSWERABLE"):
        return None
    return reply


def _coverage(query: set[str], chosen: list[Source]) -> float:
    """How much of the question the chosen sources actually cover, 0..1."""
    covered: set[str] = set()
    for source in chosen:
        covered |= query & _tokens(source.text)
    return len(covered) / max(1, len(query))


def _mission_state_root() -> Path:
    workdir = Path(os.environ.get("CHIEF_ENGINEER_WORKDIR", "./chief-engineer-runs"))
    return Path(os.environ.get(
        "CHIEF_ENGINEER_STATE_DIR", str(workdir.resolve() / "mission-state")))


def _mission_sources() -> list[Source]:
    """Mission reports on disk, if any — cited by mission id + request title."""
    sources: list[Source] = []
    root = _mission_state_root()
    try:
        paths = sorted(root.glob("m-*.json"))
    except OSError:
        return sources
    for path in paths:
        try:
            item = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        mission_id = str(item.get("mission_id", "")).strip()
        request = str(item.get("request", "")).strip()
        state = str(item.get("state", "")).strip()
        if not mission_id or not request:
            continue
        sources.append(Source(
            kind="mission",
            text=f"{request} {state}",
            detail=f"{mission_id} — “{request}” finished as {state or 'unknown'}.",
            citation=mission_id))
    return sources


def _credential_sources() -> list[Source]:
    """The curriculum's graded bodies — the lab's standing validation credentials.

    Every body the lab has solved and graded against a published experiment is a
    record; this makes "what have we validated?" and "what do we know about the
    sphere?" answerable from the wall rather than by analogy.
    """
    sources: list[Source] = []
    root = Path(__file__).resolve().parents[2] / "models" / "curriculum" / "results"
    try:
        paths = sorted(root.glob("*.json"))
    except OSError:
        return sources
    for path in paths:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        name = str(data.get("name", "")).strip()
        if not name:
            continue
        pretty = name.replace("_", " ")
        tier = data.get("tier", "")
        source = data.get("reference_source", "")
        reason = data.get("reason", "")
        sources.append(Source(
            kind="credential",
            text=f"{pretty} drag coefficient cd lift validated tier reference "
                 f"experiment credential wall {tier} {source}",
            detail=(f"{pretty}: measured Cd {data.get('cd_measured')} against "
                    f"{source or 'the reference'} Cd {data.get('reference_cd')} — {tier}."
                    + (f" {reason}" if reason else "")),
            citation=f"Validation wall — {pretty}"))
    return sources


def _static_sources() -> list[Source]:
    sources: list[Source] = list(_credential_sources())

    # Real solver runs the lab has executed. The searchable text carries the
    # plain-language synonyms of the reported coefficients (Cd -> drag, Cl ->
    # lift) so a question phrased in words still finds the case.
    for case in CASE_MEMORY:
        synonyms = "reynolds coefficient"
        if "Cd" in case.results:
            synonyms += " drag"
        if "Cl" in case.results:
            synonyms += " lift"
        sources.append(Source(
            kind="case",
            text=f"{case.name} {case.geometry} {case.dimensionality} {case.body_type} "
                 f"{case.flow} {case.results} {case.validated_against} {synonyms}",
            detail=f"{case.geometry} ({case.flow}, Re {case.reynolds[0]:.0f}-"
                   f"{case.reynolds[1]:.0f}): {case.results}; validated against "
                   f"{case.validated_against}.",
            citation=case.source))

    # Operating lessons.
    for lesson in LESSONS.values():
        sources.append(Source(
            kind="lesson",
            text=f"{lesson.rule} {lesson.full}",
            detail=lesson.full,
            citation=f"LESSONS.md {lesson.id}"))

    # Numerics knowledge base, one entry per titled fact.
    for number, title in citations.KNOWLEDGE_TITLES.items():
        sources.append(Source(
            kind="knowledge",
            text=title,
            detail=title,
            citation=f"NUMERICS_KNOWLEDGE.md #{number}"))

    # Physics-routing thresholds, so regime questions are answerable.
    try:
        from .compiler import load_physics_rules

        rules = load_physics_rules()
        regime = rules.get("regime", {})
        mesh = rules.get("mesh_quality", {})
        per_geometry = regime.get("critical_reynolds_by_geometry", {}) or {}
        onset = ", ".join(f"{name} ~ Re {value:g}" for name, value in per_geometry.items())
        sources.append(Source(
            kind="physics",
            text=f"vortex shedding onset critical reynolds cylinder sphere wake "
                 f"unsteady steady {onset}",
            detail=f"Vortex shedding onset by geometry: {onset or 'not tabulated'}; "
                   f"the default onset is Re {regime.get('shedding_onset_reynolds', '?')}, "
                   f"and the flow is treated as turbulent above Re "
                   f"{regime.get('laminar_max_reynolds', '?')}.",
            citation="NUMERICS_KNOWLEDGE.md #3 (convergence ≠ physical validity)"))
        sources.append(Source(
            kind="physics",
            text="mesh quality acceptance gate non-orthogonality skewness cells",
            detail=f"Mesh acceptance gates: non-orthogonality "
                   f"{mesh.get('max_non_orthogonality_deg', '?')} deg, skewness "
                   f"{mesh.get('max_skewness', '?')}, minimum {mesh.get('min_cells', '?')} cells.",
            citation="NUMERICS_KNOWLEDGE.md (mesh-quality guidance)"))
    except Exception:
        pass

    return sources


def _learned_sources() -> list[Source]:
    """Lessons the debrief loop earned from finished missions, cited by the
    mission id that taught them."""
    return [Source(kind="lesson", text=item["text"], detail=item["text"],
                   citation=item["mission_id"])
            for item in learned_lessons()]


def _corpus() -> list[Source]:
    return _static_sources() + _learned_sources() + _mission_sources()


# An aggregation over the whole record — "rank/list/compare/summarise", or a
# reference to everything the lab has run. For these the relevant sources ARE the
# runs themselves, so retrieval draws on the full case memory rather than needing
# tight word overlap with any single record.
_AGGREGATE_INTENT = re.compile(
    r"\b(rank|list|compare|summari[sz]e|tabulate|aggregate|overview|inventory|"
    r"catalogu?e|everything|all\s+(?:the\s+)?(?:cases|runs|geometr|bodies)|"
    r"every\s+(?:case|run)|which\s+(?:of\s+)?(?:our|the)\s+(?:cases|runs))\b", re.I)


def _aggregate_answer(text: str, query: set[str]) -> Answer:
    """Answer an aggregation over the body of work from the full record.

    The relevant sources are the runs themselves — both the case-memory runs and
    the curriculum credentials (the validation-wall bodies), so a "compare" or
    "rank" question sees every body the lab has actually solved, not just the
    subset in case memory.
    """
    cases = [source for source in _static_sources()
             if source.kind in ("case", "credential")]
    # Rank by relevance to the question when it overlaps, else present the record
    # in the order it is held; every case carries its own +/- envelope, which is
    # the confidence the question asks for.
    cases.sort(key=lambda source: len(query & _tokens(source.text)), reverse=True)
    if not cases:
        return _ungrounded()
    facts = [source.detail for source in cases]
    body = ("From the lab's body of work (each value carries the +/- envelope "
            "that is its confidence): " + " ".join(facts))
    # A rank/compare/summarise question asks for reasoning the raw listing
    # cannot do, so the model is always offered the excerpts here; the listing
    # remains the fallback whenever it has nothing to add.
    synthesized = _synthesize(text, facts)
    return Answer(
        grounded=True,
        text=synthesized or body,
        citations=citations.display_all(source.citation for source in cases),
        sources=[{"kind": source.kind,
                  "citation_display": citations.display(source.citation)}
                 for source in cases],
        mode="synthesized" if synthesized else "record")


def answer(question: str, *, max_sources: int = 3) -> Answer:
    """Answer ``question`` from the lab's record, or say it cannot be grounded."""
    text = (question or "").strip()
    query = _tokens(text)
    if not query:
        return _ungrounded()

    if _AGGREGATE_INTENT.search(text):
        return _aggregate_answer(text, query)

    scored: list[tuple[float, Source]] = []
    for source in _corpus():
        overlap = query & _tokens(source.text)
        if not overlap:
            continue
        # Score by how much of the question the source covers, with a small
        # bonus for absolute overlap so a rich match outranks a one-word one.
        score = len(overlap) + len(overlap) / max(1, len(query))
        scored.append((score, source))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    # Require at least two shared meaningful words, unless the question itself is
    # a single meaningful word (then one match is enough to be responsive).
    threshold = 2.0 if len(query) >= 2 else 1.0
    chosen = [source for score, source in scored[:max_sources] if score >= threshold]
    if not chosen:
        # Retrieval surfaced record excerpts but none cleared the grounding
        # bar. Hand those same excerpts — and nothing else — to the model; if
        # it can answer from them it does, with the same citations, otherwise
        # the honest refusal stands exactly as before.
        near = [source for _score, source in scored[:max_sources]]
        synthesized = _synthesize(text, [source.detail for source in near]) if near else None
        if synthesized:
            return Answer(
                grounded=True,
                text=synthesized,
                citations=citations.display_all(source.citation for source in near),
                sources=[{"kind": source.kind,
                          "citation_display": citations.display(source.citation)}
                         for source in near],
                mode="synthesized")
        return _ungrounded()

    facts = [source.detail for source in chosen]
    lead = facts[0]
    rest = " ".join(facts[1:])
    body = f"From the lab's record: {lead}" + (f" {rest}" if rest else "")
    # A solid record answer stands on its own. The model is brought in only
    # when the retrieved excerpts cover less than half of the question — the
    # listing alone would then read as a non-answer — and it reasons over
    # exactly the excerpts the deterministic layer chose.
    synthesized = _synthesize(text, facts) if _coverage(query, chosen) < 0.5 else None
    return Answer(
        grounded=True,
        text=synthesized or body,
        citations=citations.display_all(source.citation for source in chosen),
        sources=[{"kind": source.kind, "citation_display": citations.display(source.citation)}
                 for source in chosen],
        mode="synthesized" if synthesized else "record")


def _ungrounded() -> Answer:
    return Answer(
        grounded=False,
        text=("I could not ground an answer to that in the lab's mission reports, "
              "run history, knowledge base, or lessons, so I will not invent one. "
              "What I can answer from: the cylinder and motorBike cases we have "
              "actually solved, the numerics knowledge base, the physics-routing "
              "thresholds, and the operating lessons. Ask about one of those, or "
              "name a body to run."),
        citations=[],
        sources=[])
