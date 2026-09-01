"""DEMO MODE — the one interface every act plugs into.

Sanaa's directive of 2026-09-01 ~03:40Z (captured verbatim at
``etc/sessions/2026-09-01T0340Z_sanaa_demo_mode_binding.md``, commit
``4905abdd``) is binding for every act:

    A demo act is the live GUI pipeline fed by a completed run tree. It looks
    and behaves exactly like a user running the case: every stage renders in
    its normal place and its normal order. The only difference from a fresh
    run is that the solver stage replays the stored logs at accelerated pace
    instead of computing. Every number, field and figure is the real run's;
    nothing is invented.

This module is the CONTRACT, not the act. It says exactly what an act must
supply for each mandatory stage, in types that can be imported and checked.
The sequencer (``demo_sequencer``, same package) consumes a :class:`DemoAct`
and drives the stages in fixed order; the replay of the solver stage is built
separately and reached through :class:`SolveReplay`.

WHY IT IS TYPED RATHER THAN DESCRIBED
-------------------------------------
Three of the failures this interface exists to prevent are failures of
authorship, not of judgement, and every one of them has already reached a
screen carrying this lab's numbers:

* a number whose artifact was gone by the time anyone looked. Every quantity
  crosses this interface as a :class:`Measured`, which carries the file it was
  read out of, and :func:`validate_act` refuses an act whose sources are not
  on disk. A number without a live source cannot be handed over at all.

* an on-screen phrase from her NEVER-list surviving a human sweep. There is no
  committed jargon checker in this repository; R5 compliance has rested on a
  manual grep, which is exactly how those strings survived. :func:`check_demo_language`
  is that checker, and :func:`validate_act` runs it over every string an act
  offers, so a banned phrase fails at authorship instead of on camera.

* "No surface loaded". :class:`Geometry` cannot be constructed without an STL
  path, and the validator refuses one that is absent, empty, or not the solved
  geometry the act names.

WHAT AN ACT OWNS AND WHAT THE SEQUENCER OWNS
--------------------------------------------
The act owns FACTS: which run tree, which STL, which logs, which series, which
figures, which numbers and where each was read. The sequencer owns ORDER,
PACE and WORDING MECHANICS: stage sequence, the accelerated replay, the
control-room events, and the language checks. An act never emits an event and
never composes a stage header; it answers eight questions.

INTERNAL-ONLY FIELDS
--------------------
Two things in this module are internal and never reach a screen: the
``presentation of run X`` flag (:attr:`RunRecord.presentation_of`) and every
``Measured.source`` path. Both are attributes of the record, not of the
display. :func:`assert_screen_safe` is applied by the sequencer to every
payload before it is published, and refuses either one.

Provenance for the numbers-and-costs rules used here: CLAUDE.md rule 12
(core-minutes is the unit; the box cannot read its own billing, so any dollar
figure is derived and must say so) and rule 4 (a run is done only if all of
the completion clauses hold).
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Sequence

__all__ = [
    "Measured", "RunRecord", "Prompt", "Restatement", "Assumption", "Geometry",
    "GeometryMatch", "MeshPlan", "Feasibility", "SolveReplay", "SeriesSpec",
    "ElapsedClock", "GatesAndChecks", "Results", "Figure", "Table", "DemoAct",
    "DemoContractError", "check_demo_language", "check_running_line",
    "assert_screen_safe", "screen_refusal_class", "validate_act",
    "core_minutes", "cost_line",
    "STAGES", "BANNERS", "NEVER_PHRASES", "RATE_USD_PER_CORE_HOUR",
    "SERVED_GEOMETRY_DIR", "register_act", "registered_acts",
]


class DemoContractError(Exception):
    """An act does not satisfy the demo-mode contract.

    Raised at authorship or validation time, never during a shoot. The
    sequencer refuses to start an act that raises this, exactly as the
    comparators refuse rather than degrade (CLAUDE.md rule 4).
    """


#: The mandatory stages, in the order they render. Sanaa: "every stage renders
#: in its normal place and its normal order". The sequencer walks this list and
#: nothing else; an act cannot reorder, skip, or add a stage.
STAGES: tuple[str, ...] = (
    "prompt",        # professional wording, as the user typed it
    "restatement",   # restatement, confidence, cost estimate
    "assumption",    # exactly one user-assumption check
    "geometry",      # the uploaded STL renders; it IS the solved geometry
    "meshing",       # the real mesher, drawn cell by cell, wall-layer zoom
    "feasibility",   # "30-second check before committing budget", with result
    "solving",       # stored logs replayed at accelerated pace
    "gates",         # reader checks, conservation, grid statement, in tables
    "results",       # fields, plots, tables, verification lines, caveats, cost
)

#: The banner states, in order, from Sanaa's pacing amendment (``aaed6498``):
#: forming team, planning, fleet at work, meshing, feasibility, solving,
#: results. The banner must match what the screen is ACTUALLY showing at every
#: moment — no banner ahead of or behind its content — so the mapping from
#: stage to banner is fixed here rather than chosen per act.
BANNERS: Mapping[str, str] = {
    "prompt": "forming team",
    "restatement": "planning",
    "assumption": "planning",
    "geometry": "fleet at work",
    "meshing": "meshing",
    "feasibility": "feasibility",
    "solving": "solving",
    "gates": "solving",
    "results": "results",
}

#: The directory the control-room server actually serves a body from:
#: ``sdk/geometry``. Measured, not assumed — ``server.py`` resolves a named
#: geometry at line 351 and lands an upload at line 671, both as
#: ``HERE.parent / "geometry"`` with ``HERE`` the ``chief_engineer`` package.
#:
#: This is NOT where the demo-surface generator writes (that is
#: ``cases/demo-surfaces``); the two agree today only because someone copied by
#: hand. An act therefore declares the SERVED copy, and :func:`validate_act`
#: checks that copy, so a regenerated surface cannot silently serve a stale
#: body. Related divergence worth a supervisor's eye: the staging helper at
#: ``server.py:73`` honours ``CERTONOMOUS_STAGING`` while the two serving
#: paths do not, so setting that variable moves the staging view without
#: moving what is served.
SERVED_GEOMETRY_DIR = Path(__file__).resolve().parents[1] / "geometry"

#: The lab's recorded rate. Owner-stated 2026-08-21/22 and corroborated at
#: ``Xiao2016_EnKF/PREREGISTRATION.md:197``. Any dollar figure derived from it
#: is DERIVED, never measured: the box cannot read its own billing
#: (COMPUTE_BUDGET_CHARTER §5).
RATE_USD_PER_CORE_HOUR = 0.0513


# ---------------------------------------------------------------------------
# Language: her NEVER-list, enforced mechanically
# ---------------------------------------------------------------------------

#: Verbatim from the 2026-09-01 ~03:40Z capture, lines 35-38: "Never:
#: 'already finished', 'presenting', 'nothing new is solved', 'no compute
#: booked', 'screens come from', 'reference body', 'surface on file', 'not
#: meshed by this screen', any path, any 'two grids were built'."
#:
#: Each entry is (regex, what to say instead). The regexes are deliberately
#: narrow: a checker that fires on innocent prose gets switched off, and a
#: checker that is switched off is how these strings survived a manual grep.
NEVER_PHRASES: tuple[tuple[str, str], ...] = (
    # THE REMEDY USED TO READ "say what was solved, in the past tense", and
    # that is very probably why three past-tense strings reached the filmed
    # screen in one day: the instrument built to catch them was advising
    # authors to write them. Sanaa's 04:20Z order is "no past tense", later
    # and stricter than the 03:40Z zone rule quoted at _RUNNING_SHAPES below,
    # so present tense is the intersection and is what a remedy may recommend.
    # A guard that recommends the defect it exists to catch is worse than no
    # guard: it is a defect with an authority attached.
    (r"already\s+finish(ed|es)?", "name the solve and its result, in the "
                                  "present tense"),
    (r"\bpresent(ing|s|ed)\b(?!\s+tense)", "say what the run did"),
    (r"nothing\s+new\s+is\s+solved", "state the solve as fact"),
    (r"no\s+compute\s+(is\s+)?booked", "state this run's real cost"),
    (r"screens?\s+come\s+from", "state the solve as fact"),
    (r"reference\s+bod(y|ies)", "the uploaded surface IS the solved geometry"),
    (r"surface\s+on\s+file", "the uploaded surface IS the solved geometry"),
    # Widened past her literal wording deliberately: the phrase actually live
    # in this package reads "not meshed or solved by this screen"
    # (``__init__.acknowledge_reference_surface``), which her exact string
    # would have missed. A checker that cannot see the instance already in the
    # repository is not a checker.
    (r"not\s+meshed\s+(or\s+solved\s+)?by\s+this\s+screen",
     "the mesher runs on this screen"),
    (r"\b(two|2)\s+grids?\s+(were|was|are|is)\s+built", "one grid on screen"),
    (r"\bre[- ]?display(ed|s|ing)?\b", "state the solve as fact"),
    (r"\bno\s+new\s+solve\b", "state the solve as fact"),
    (r"\breplay(ed|ing|s)?\b", "state the solve as fact"),
    (r"\bsolver:\s*none\b", "name the solver of the run"),
    (r"\bnot\s+recorded\s+in\s+this\s+bundle\b", "state the recorded fact"),
    (r"\bsource\s+case\b", "state the solve as fact"),
    # DEMO STANDARD R5: "Tier words, case ids, rule numbers, docket/lesson ids,
    # patch/defect talk: NEVER user-visible." Added after testing this checker
    # against the replay stage's REAL payload, where a case id reaches the
    # screen through the `labels` list and every string-level check passed it.
    # A case id is a token carrying an underscore, a digit and a capital at
    # once (JF1_L1_BLOWN_CMU020_A0, F17c_KV40_FLOOR, M1_kOmegaSST_null__AR_10).
    # "chtMultiRegionSimpleFoam" has no underscore and "p_rgh" no digit or
    # capital, so neither fires.
    (r"(?<![\w])(?=[\w]*_)(?=[\w]*\d)(?=[\w]*[A-Z])[A-Za-z0-9_]{4,}(?![\w])",
     "give the point a plain-English label, not a case id"),
    (r"\bL-\d+\b", "a lesson id is never user-visible"),
    (r"\bD-?\d{3,}\b", "a docket id is never user-visible"),
    (r"\btier[-\s]?\d\b", "tier words are never user-visible"),
    (r"\bBLOCKED-GPU\b", "say what could not run, in plain words"),
    (r"\bpre-?registration\b", "say 'success criteria fixed before running'"),
    # THREE MORE CLASSES OF INTERNAL IDENTIFIER, added 2026-09-01 after
    # MEASURING what this checker refused: it caught case ids, gate words,
    # tier words, lesson ids, docket ids and paths, and ALLOWED a process id,
    # a commit hash and a port number. Sanaa's rule is "no internal
    # information", and a machine that enforces six of nine classes while
    # reading as complete is how the other three reach a screen.
    #
    # Each is deliberately narrow, for the reason the block above gives: a
    # checker that fires on innocent prose gets switched off.
    (r"\bpid\s*[:#]?\s*\d+\b", "a process id is never user-visible"),
    (r"\bport\s+\d{2,5}\b", "a port number is never user-visible"),
    # A commit hash: seven to forty hex characters carrying BOTH a digit and a
    # letter a-f. Both lookaheads are load-bearing under this checker's
    # IGNORECASE. Without the digit clause, ordinary words spelt from the hex
    # alphabet match ("defaced", "cabbaged"); without the letter clause, any
    # seven-digit number matches, and an iteration count is seven digits.
    (r"(?<![\w])(?=[0-9a-f]*[a-f])(?=[0-9a-f]*\d)[0-9a-f]{7,40}(?![\w])",
     "a commit hash is never user-visible"),
)

#: The gate vocabulary. R5 bans the verdict vocabulary appearing AS A VERDICT
#: on a customer surface; it does not ban the English language. "NOT A RESULT"
#: as a token or a label is the lab's gate word and must never appear; "it is
#: not a result" inside a sentence is the honest way to say the thing, and a
#: checker that cannot tell them apart forces an act to choose between the
#: rule and the truth.
#:
#: Multi-word gate phrases are refused in upper case, in title case, and as a
#: standalone label. Single words (PASS, BLOCKED, PENDING) are refused in
#: upper case and as a standalone label ONLY: "blocked" and "pending" are
#: ordinary English, and "Pass 1 of 2" starts a sentence in title case for
#: reasons that have nothing to do with a gate.
_GATE_PHRASES: tuple[str, ...] = (
    "NOT A RESULT", "GATE REACHED", "GATE FAIL", "PASS", "BLOCKED", "PENDING",
)

#: TRAILING-BOUNDARY BLINDNESS, and it is the second instance in this lab.
#: ``\bPASS\b`` does NOT match "PASSED": the trailing ``\b`` needs a
#: non-word character, and "ED" is word characters. Measured on the filmed
#: surface -- four planted-control lines rendered on the gates table as
#: "coefficient control PASSED", "elapsed control PASSED" and two more, and
#: every one of them walked through this checker untouched.
#:
#: THE IDENTICAL DEFECT was found and fixed hours earlier in a DIFFERENT file
#: (``vocab_sweep_jf1.py``, where ``\b(defect|...)\b`` missed "defects"), and
#: nobody looked here because the first instance had been fixed. Two
#: independent guards, one blindness. The lesson is not "add PASSED"; it is
#: that a word-boundary vocabulary check is blind to every inflection of every
#: word in it, in every file that has one.
#:
#: So the final word of each phrase carries its uppercase inflections. Upper
#: case ONLY, as before: "the flow passes over the slot" is ordinary English
#: and stays legal, while "PASSED" as a label does not.
_GATE_TAIL = r"(?:ED|ES|S)?"


def _check_gate_words(text: str) -> None:
    """Refuse the gate vocabulary used as a verdict; allow it as English."""
    stripped = text.strip().strip(".:;,").strip()
    for phrase in _GATE_PHRASES:
        words = phrase.split()
        pattern = (r"\b" + r"\s+".join(words[:-1] + [words[-1] + _GATE_TAIL])
                   if len(words) > 1 else r"\b" + words[0] + _GATE_TAIL)
        pattern += r"\b"
        # The token itself, in the case the ledger writes it.
        if re.search(pattern, text):
            raise DemoContractError(
                f"the gate word {phrase!r} is the lab's verdict vocabulary and "
                f"is never user-visible; translate it per R5, or say the same "
                f"thing in ordinary lower-case English inside a sentence")
        # A label wearing a hat: the whole string IS the phrase.
        if stripped.lower() == phrase.lower():
            raise DemoContractError(
                f"{text!r} is the gate word {phrase!r} used as a label; "
                f"translate it per R5")
        # Title case, for multi-word phrases only.
        if len(words) > 1:
            title = r"\b" + r"\s+".join(w.capitalize() for w in words) + r"\b"
            if re.search(title, text):
                raise DemoContractError(
                    f"{phrase!r} in title case is the gate word wearing a hat; "
                    f"translate it per R5")


#: The fidelity chips, and what each one MEANS in plain English. Taken from
#: the definitions written beside them at ``chief_engineer.lab`` lines 181-186,
#: not composed here: a paraphrase invented at the display layer would drift
#: from what the chip is awarded for.
#:
#: TRANSLATED, NEVER STRIPPED. The chip is real information about how well a
#: number is backed, and deleting it makes the screen say less than the lab
#: knows. The record keeps the token verbatim; the screen carries its meaning.
CHIP_TRANSLATIONS: Mapping[str, str] = {
    "VALIDATED": ("checked against a published experiment and inside its "
                  "band"),
    "SOLVER-BACKED": ("produced by a full solve; no experimental comparison "
                      "is available for this configuration"),
    "RESEARCH MODEL": "from a fast sizing model rather than a full solve",
    "UNCONVERGED": ("the solve did not settle, so this number is not evidence "
                    "yet"),
}


def translate_chips(text: str) -> str:
    """Replace any fidelity chip with its plain-English meaning.

    Applied by the sequencer before a payload is guarded, so an act does not
    have to reimplement the translation and cannot ship a raw chip. Longest
    token first, so "RESEARCH MODEL" is not half-matched.
    """
    if not isinstance(text, str):
        return text
    for token in sorted(CHIP_TRANSLATIONS, key=len, reverse=True):
        if token in text:
            text = text.replace(token, CHIP_TRANSLATIONS[token])
    return text

#: A path is anything with a filesystem root, a repository root segment, or a
#: recognised extension. "lift/drag" and "2D/axisymmetric" are not paths and do
#: not fire; ``/home/ubuntu/...``, ``cases/demo-surfaces/x.stl`` and
#: ``log.simpleFoam`` do.
_PATH_PATTERNS: tuple[str, ...] = (
    r"(?<![\w.])[~/]\S*/\S+",
    r"(?<![\w.])(?:cases|verification|docs|sdk|models|scripts|demo-output|"
    r"mission-output|etc)/\S+",
    r"(?<![\w])[\w][\w.-]*\.(?:stl|obj|vtk|vtp|py|md|json|csv|dat|txt|log|"
    r"html|pdf|png|svg|foam|gz|yaml|yml|sh)\b",
    r"(?<![\w])log\.\w+",
    r"[A-Za-z]:\\\S+",
)

#: Allowed ONLY inside the limitations box, and nowhere else. Sanaa: "if a flow
#: picture exists only on the finer grid, the sheet says 'flow picture from a
#: finer companion grid' in the limitations box and nowhere else."
_FINER_GRID = r"finer\s+companion\s+grid"


def check_demo_language(text: str, *, zone: str = "screen") -> None:
    """Refuse a string that breaks the on-screen language rules.

    ``zone`` is ``"screen"`` for anything a viewer reads, or ``"limitations"``
    for the caveat box, which is the one place the finer-companion-grid
    sentence is permitted. ``zone="internal"`` skips the path rule only, for
    strings that live in the run record and never render.

    Raises :class:`DemoContractError` naming the offending phrase and what to
    say instead. It does not warn and it does not sanitise: a phrase this
    checker catches is an authorship bug, and rewriting it silently would put
    a sentence on camera that nobody chose.
    """
    if not isinstance(text, str):
        raise DemoContractError(f"expected a string, got {type(text).__name__}")
    if zone not in {"screen", "limitations", "internal"}:
        raise DemoContractError(f"unknown zone {zone!r}")

    for pattern, remedy in NEVER_PHRASES:
        hit = re.search(pattern, text, flags=re.IGNORECASE)
        if hit:
            raise DemoContractError(
                f"banned on-screen phrase {hit.group(0)!r} in {text!r}; "
                f"instead: {remedy}")

    if zone != "internal":
        for pattern in _PATH_PATTERNS:
            hit = re.search(pattern, text)
            if hit:
                raise DemoContractError(
                    f"a path is never on screen: {hit.group(0)!r} in {text!r}")

    _check_gate_words(text)

    if zone == "screen" and re.search(_FINER_GRID, text, flags=re.IGNORECASE):
        raise DemoContractError(
            f"'finer companion grid' belongs in the limitations box and "
            f"nowhere else: {text!r}")

    # The package's older doctrine still binds where it does not conflict:
    # no dash characters, no banned register, bullets start capitalised.
    from . import check_wording

    try:
        check_wording(text)
    except ValueError as exc:
        # One guard, one exception type. The older doctrine raises ValueError;
        # letting that escape would mean a caller who correctly handles a
        # refusal still crashes on half the refusals, which is how a guard
        # ends up wrapped in a bare except.
        raise DemoContractError(str(exc)) from exc


#: A running line is progressive. Sanaa: 'Progressive tense while running
#: ("Meshing", "Solving, iteration 4,000 of 20,000", "Sweep point 3 of 5"),
#: past tense for results.' Two shapes are accepted: a leading -ing verb, or a
#: counted-progress line ("Sweep point 3 of 5", "Point 3 of 5").
#:
#: THE QUOTED CLAUSE "past tense for results" IS SUPERSEDED and is kept only
#: because it is her wording and it is what these shapes were built from. Her
#: 04:20Z order says flatly "no past tense", which is later and is not
#: zone-aware. Nothing in this module may RECOMMEND past tense on the strength
#: of the quote above; the running-line shapes are unaffected, because
#: progressive satisfies both directives.
_RUNNING_SHAPES: tuple[str, ...] = (
    r"^[A-Z][a-z]+ing\b",
    r"^(Sweep\s+point|Point|Operating\s+point|Case)\s+\d[\d,]*\s+of\s+\d[\d,]*\b",
)

#: A results line states a finished fact and must not promise. These are the
#: tells that a running line was pasted into a results slot.
#:
#: THE FOUR PATTERNS ARE UNCHANGED; ONLY THE ADVICE IS. Each remedy read
#: "results are past tense", which is the superseded 03:40Z rule, and these
#: strings are what an author is handed at the moment they are rewriting a
#: line. Every one of them pushed the author toward the exact wording the
#: 04:20Z order forbids. The mechanism is untouched: "will", "is being", "are
#: being" and "we are ...ing" are still refused in a results slot, and a
#: present-tense finished fact ("All 5 sweep points complete, ...") passes
#: exactly as a past-tense one did.
_RESULT_FORBIDDEN = (
    (r"\bwill\s+\w+", "a results line states a fact, not a promise"),
    (r"\bis\s+being\b",
     "a results line states the finished fact, in the present tense"),
    (r"\bare\s+being\b",
     "a results line states the finished fact, in the present tense"),
    (r"\bwe\s+are\s+\w+ing\b",
     "a results line states the finished fact, in the present tense"),
)


def check_running_line(text: str, *, tense: str) -> None:
    """Refuse a stage line whose tense does not match its moment.

    ``tense`` is ``"progressive"`` for a line shown while a stage runs, or
    ``"past"`` for a line shown with a result. Applies
    :func:`check_demo_language` first, so one call covers both rules.

    ``"past"`` IS A SLOT NAME, NOT AN INSTRUCTION, and the name is now
    misleading. It selects the RESULTS slot, whose rule is "state a finished
    fact, do not promise" -- see :data:`_RESULT_FORBIDDEN`, which forbids
    "will", "is being", "are being" and "we are ...ing" and says nothing about
    the verb form of the fact itself. A present-tense results line passes.
    Passing ``tense="past"`` does NOT license writing past tense, and under
    Sanaa's 04:20Z "no past tense" it must not. The literal is left alone
    rather than renamed because it is a public argument value used by acts
    outside this team (``dmr_act``, ``adjoint_act``); renaming it is a
    cross-team call, and it is flagged rather than taken here.
    """
    check_demo_language(text)
    if tense == "progressive":
        if not any(re.search(p, text) for p in _RUNNING_SHAPES):
            raise DemoContractError(
                f"a running line is progressive tense: {text!r} does not "
                f"start with an -ing verb or a counted-progress phrase")
    elif tense == "past":
        for pattern, remedy in _RESULT_FORBIDDEN:
            hit = re.search(pattern, text, flags=re.IGNORECASE)
            if hit:
                raise DemoContractError(
                    f"{hit.group(0)!r} in a results line: {remedy}: {text!r}")
    else:
        raise DemoContractError(f"unknown tense {tense!r}")


#: A viewer-readable NOUN for each identifier class, keyed by the remedy the
#: pattern carries. Only the identifier classes are mapped: everything else in
#: NEVER_PHRASES is a matter of WORDING rather than a thing embedded in the
#: text, and telling a viewer their request "contains state the solve as fact"
#: would be nonsense. Unmapped remedies fall back to a wording sentence.
_REFUSAL_CLASS_NOUNS: Mapping[str, str] = {
    "give the point a plain-English label, not a case id": "a case identifier",
    "a lesson id is never user-visible": "an internal note identifier",
    "a docket id is never user-visible": "an internal note identifier",
    "tier words are never user-visible": "an internal grading word",
    "say what could not run, in plain words": "an internal status word",
    "say 'success criteria fixed before running'": "an internal process word",
    "a process id is never user-visible": "a process identifier",
    "a port number is never user-visible": "a port number",
    "a commit hash is never user-visible": "a commit identifier",
}


def screen_refusal_class(text: str) -> str | None:
    """WHICH CLASS of forbidden content ``text`` carries, never the value.

    THE DEFECT THIS EXISTS FOR. :func:`check_demo_language` quotes the string
    it refused, which is right for an authorship fault -- the author needs to
    see what they wrote. It is exactly wrong for text a USER typed: the
    sequencer publishes a refusal as ``mission.failed`` with the reason on it,
    so a guard built to keep a filesystem path off the screen would put that
    very path on the screen through its own error message. A leak by way of
    the error is the classic failure of a guard of this kind, and it is worse
    than no guard because it arrives wearing the guard's authority.

    Returns a short class noun -- "a file path", "a case id" -- or ``None``
    when the text is clean. It is ORDERED EXACTLY AS :func:`check_demo_language`
    checks, so the two can never disagree about which rule fired.
    """
    if not isinstance(text, str):
        return "text this screen cannot read"

    for pattern, remedy in NEVER_PHRASES:
        if re.search(pattern, text, flags=re.IGNORECASE):
            # The remedies quote nothing, so they are safe -- but they are
            # written as INSTRUCTIONS TO AN AUTHOR ("give the point a
            # plain-English label"), and splicing one into a sentence aimed at
            # a viewer produces "it contains give the point a plain-English
            # label". Measured on the real path before this map existed. The
            # identifier classes therefore get a noun phrase a viewer can
            # read; everything else is wording rather than an identifier, and
            # says so.
            return _REFUSAL_CLASS_NOUNS.get(
                remedy, "wording the screen rules do not allow")
    for pattern in _PATH_PATTERNS:
        if re.search(pattern, text):
            return "a file path"
    for phrase in _GATE_PHRASES:
        words = phrase.split()
        if re.search(r"\b" + r"\s+".join(words) + r"\b", text):
            return "one of the lab's internal result labels"
        if text.strip().strip(".:;,").strip().lower() == phrase.lower():
            return "one of the lab's internal result labels"
        if len(words) > 1 and re.search(
                r"\b" + r"\s+".join(w.capitalize() for w in words) + r"\b",
                text):
            return "one of the lab's internal result labels"
    if re.search(_FINER_GRID, text, flags=re.IGNORECASE):
        return "a sentence that belongs only in the caveat box"

    from . import check_wording

    try:
        check_wording(text)
    except ValueError:
        return "wording the screen rules do not allow"
    return None


def assert_screen_safe(payload: Mapping) -> None:
    """Refuse a control-room payload carrying an internal-only field.

    The ``presentation of run X`` flag and every ``Measured.source`` path live
    in the run record. This is the sequencer's last gate before publishing, so
    neither can reach a screen through a payload nobody re-read.
    """
    #: Keys whose values are machine identifiers rather than screen text: an
    #: event name, a table's id, a beat name. They are carried so a banner and
    #: the content it describes can be AUDITED as a pair, and they never
    #: render. Checking them as prose would refuse "demo.prompt" for containing
    #: a banned word, which is how a guard earns a reputation for crying wolf
    #: and gets switched off.
    audit_keys = {"for_event", "table_id", "beat", "event", "stage_id",
                  "url", "file"}

    def walk(node, trail: str, zone: str) -> None:
        if isinstance(node, Mapping):
            for key, value in node.items():
                if str(key) in audit_keys:
                    continue
                if str(key) in {"presentation_of", "source", "run_root",
                                "internal", "case_dir"}:
                    raise DemoContractError(
                        f"internal-only field {trail}.{key} would reach the "
                        f"screen; strip it in the act, not in the renderer")
                # The zone is a property of WHERE the text lands on screen,
                # and the payload key is what names that place. Found by
                # assembling a whole act and guarding what it really
                # published: the caveat box is the one place the finer
                # companion grid may be named, and a flat screen-zone walk
                # refused the act's own limitations list.
                walk(value, f"{trail}.{key}",
                     "limitations" if str(key) == "limitations" else zone)
        elif isinstance(node, (list, tuple)):
            for i, value in enumerate(node):
                walk(value, f"{trail}[{i}]", zone)
        elif isinstance(node, str):
            check_demo_language(node, zone=zone)

    walk(payload, "payload", "screen")


# ---------------------------------------------------------------------------
# The unit of every number that crosses this interface
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Measured:
    """One number, its unit, and the artifact it was read out of.

    ``basis`` is ``"measured"`` when the value was read from a run artifact, or
    ``"derived"`` when it was computed from measured values at a recorded rate
    or constant. A dollar figure is ALWAYS derived: the box cannot read its own
    billing (CLAUDE.md rule 12). ``source`` is internal and never renders.
    """

    value: float | int | str
    unit: str
    source: Path
    basis: str = "measured"
    note: str = ""

    def __post_init__(self) -> None:
        if self.basis not in {"measured", "derived"}:
            raise DemoContractError(
                f"basis is 'measured' or 'derived', not {self.basis!r}")
        if not str(self.source):
            raise DemoContractError("every number names the artifact it came from")

    def on_screen(self, fmt: str = "") -> str:
        """The rendered value with its unit. The source never appears."""
        body = format(self.value, fmt) if fmt else str(self.value)
        return f"{body} {self.unit}".strip()


def core_minutes(wall_seconds: float, ranks: int) -> float:
    """The lab's compute unit: wall seconds x ranks / 60 (CLAUDE.md rule 12)."""
    if wall_seconds < 0 or ranks < 1:
        raise DemoContractError("wall seconds >= 0 and ranks >= 1")
    return wall_seconds * ranks / 60.0


#: What the compute figure is CALLED on a customer screen. The quantity is
#: unchanged and is still CLAUDE.md rule 12's core-minutes -- wall seconds x
#: ranks / 60 -- and the record, the ledgers and every cost calibration keep
#: saying core-minutes. Only the screen's word changes: "core-minutes" is this
#: lab's internal unit, and Sanaa's live-demo standard keeps internal
#: information off the customer surface. A viewer reads "processor-minutes"
#: without having to know what a core is, and it is the same minute on the
#: same processor.
SCREEN_COMPUTE_UNIT = "processor-minutes"


@dataclass(frozen=True)
class HardwareProjection:
    """A compute figure carried onto hardware this box is not.

    Sanaa, 2026-09-01: "i ran this on my station after moving dafoam linear
    solves to gpu and this is the speedup i have so we can already show that
    instead". The screen therefore shows the projected figure. What it may
    NEVER do is show it bare.

    WHY THE BASIS IS A REQUIRED FIELD AND NOT A DOCSTRING. A bare "23.5
    processor-minutes" is a measurement claim, and this box did not make it:
    117.5 is what this hardware measured and 23.5 is a projection from
    another machine, stated by its owner. CLAUDE.md rule 12 is explicit that a
    cost is never called measured unless a record backs it -- the same footing
    as the $0.0513 per core-hour rate, which is owner-stated and labelled so
    everywhere it is used. ``basis`` is the sentence that renders beside the
    number, and :func:`cost_line` refuses a projection without one, so the
    label cannot be dropped by an edit that only touches the number.

    NO DOLLAR FIGURE IS DERIVED FOR A PROJECTION, deliberately. The recorded
    rate prices THIS instance; applying it to minutes on somebody else's
    workstation with a graphics processor in it would manufacture a second
    unfounded number out of the first, and the currency figure is the one
    place this lab has already had to write "derived, not measured" on
    everything it prints.
    """

    factor: float
    hardware: str            # what the projected figure describes, in plain words
    basis: str               # why that number, and whose measurement it rests on

    def __post_init__(self) -> None:
        if self.factor <= 0:
            raise DemoContractError("a projection factor is positive")
        if not self.hardware.strip() or not self.basis.strip():
            raise DemoContractError(
                "a projected compute figure states the hardware it describes "
                "and the basis of the projection; a bare number is a "
                "measurement claim this box cannot support")

    def apply(self, cm: float) -> float:
        return cm / self.factor


#: The projection Sanaa timed on her own station, 2026-09-01, after moving the
#: adjoint linear solves onto its graphics processor. OWNER-STATED, NOT
#: MEASURED HERE -- this box has no graphics processor attached and cannot
#: reproduce the timing (CLAUDE.md rule 12; docs/GPU_CAPABILITY_STATE.md).
OWNER_GPU_STATION = HardwareProjection(
    factor=5.0,
    hardware=("a workstation running the linear solves on its graphics "
              "processor"),
    basis=("Five times faster than the machine these screens are served "
           "from, timed on that workstation by the engineer who runs it."))


def cost_line(cm: float, *, gross: bool = True,
              projection: "HardwareProjection | None" = None) -> str:
    """The screen's cost sentence for a run of ``cm`` core-minutes.

    Stated as THIS run's cost, because it is: Sanaa, "the run's real cost,
    shown as this run's cost, because it is". The dollar figure is derived at
    the recorded rate, and the sentence says so rather than implying the box
    read a bill.

    The ARGUMENT is core-minutes and the RENDERING is
    :data:`SCREEN_COMPUTE_UNIT`; the number is not touched.

    WITH A ``projection`` the number IS touched, and the sentence says so and
    says on what. See :class:`HardwareProjection`: the projected figure names
    the hardware it describes and carries its basis, and no currency figure is
    derived for it. Without one, byte-for-byte the sentence it always was.
    """
    basis = "gross" if gross else "cleaned"
    if projection is not None:
        shown = projection.apply(cm)
        return (f"Compute used: {shown:,.1f} {SCREEN_COMPUTE_UNIT} ({basis}) "
                f"on {projection.hardware}. {projection.basis}")
    usd = cm / 60.0 * RATE_USD_PER_CORE_HOUR
    return (f"Compute used: {cm:,.1f} {SCREEN_COMPUTE_UNIT} ({basis}), "
            f"about ${usd:,.2f}, derived at the recorded rate.")


# ---------------------------------------------------------------------------
# Stage payloads: exactly what an act supplies, stage by stage
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RunRecord:
    """Stage 0, internal. The completed run tree this act is fed from.

    Nothing here renders. ``presentation_of`` is the flag Sanaa requires in the
    run record and forbids on screen; it is written to ``record_path`` by the
    act's own bookkeeping and refused by :func:`assert_screen_safe` if it ever
    reaches a payload.

    ``completion_evidence`` is the artifact that shows the run satisfied the
    strict completion rule (rc=0, an End line, last time == endTime, fields
    present, and every field newer than the case's own ``0/T`` — CLAUDE.md
    rule 4). The validator checks that this artifact EXISTS. It does not
    re-derive the physics: an act claiming completion must point at the marker
    its own family wrote, and a missing marker is a refusal.
    """

    run_id: str
    run_root: Path
    solver: str                      # e.g. "OpenFOAM simpleFoam"
    physics: str                     # plain-English physics of the source run
    completion_evidence: Path
    presentation_of: str             # "presentation of run <run_id>" — internal
    record_path: Path                # where that flag is written

    def __post_init__(self) -> None:
        check_demo_language(self.solver, zone="internal")
        check_demo_language(self.physics, zone="internal")
        if not self.presentation_of.startswith("presentation of run "):
            raise DemoContractError(
                "the internal flag reads 'presentation of run <id>'")

    def solver_header(self) -> str:
        """The header line Sanaa mandates: solver plus plain physics.

        Her 2026-09-01 ~03:10Z standard makes the header the ONE place the
        solver binary and turbulence model may appear, stated once. "Solver:
        none" is never shown on a results screen.
        """
        return f"Solver: {self.solver}, {self.physics}."


@dataclass(frozen=True)
class Prompt:
    """Stage 1. The user's request, in professional wording.

    For the jet-flap act this string is fixed by Sanaa and is not the act's to
    reword: "Blown-wing high-lift: sweep the trailing-edge jet momentum
    coefficient from 0 to 0.4 and report lift against blowing with the
    classical jet-flap theory."
    """

    text: str

    def __post_init__(self) -> None:
        check_demo_language(self.text)


@dataclass(frozen=True)
class Restatement:
    """Stage 2. What the lab understood, how sure it is, what it will cost.

    ``cost_estimate`` is the UPFRONT estimate the user is quoted before
    spending (DEMO STANDARD R8: every result states compute used AND the
    upfront estimate). It is not the actual; the actual arrives in
    :class:`Results`, and the two are compared in the completion record per
    CLAUDE.md rule 12.
    """

    restatement: str
    confidence: str                  # plain English, no tier words (R5)
    cost_estimate: Measured          # core-minutes, basis "derived"

    def __post_init__(self) -> None:
        check_demo_language(self.restatement)
        check_demo_language(self.confidence)


@dataclass(frozen=True)
class Assumption:
    """Stage 3. Exactly one user-assumption check.

    DEMO STANDARD R9: the lab's intelligence is shown only through correcting
    a user assumption, saving the user compute, or stating understanding and
    confidence before spending. This is the first of those. ``correction`` is
    empty when the user's assumption held, and the act says so plainly.
    """

    assumption: str
    finding: str
    correction: str = ""

    def __post_init__(self) -> None:
        for text in (self.assumption, self.finding, self.correction):
            if text:
                check_demo_language(text)


@dataclass(frozen=True)
class GeometryMatch:
    """One measured comparison between the served surface and the solved body.

    The act does not promise the surface is the solved geometry; it MEASURES
    it, one quantity at a time, and the sentence "solved on this geometry" is
    rendered only when every comparison agrees inside its tolerance.

    The shape this exists for is already measured on Act B: the demo surface is
    chord 0.991114 m against the solved 1.000000 m, and slot height ratio
    0.005045 against 0.005000 — the same profile, 0.9% apart in scale. Under
    this type that act cannot render the sentence until the surface is
    regenerated from the solved case, which is exactly Sanaa's parenthetical.
    """

    quantity: str                    # e.g. "chord", "slot height ratio"
    solved: Measured
    supplied: Measured
    tolerance: float
    relative: bool = True            # False for an absolute tolerance

    def __post_init__(self) -> None:
        check_demo_language(self.quantity, zone="internal")
        if self.tolerance < 0:
            raise DemoContractError("tolerance >= 0")

    @classmethod
    def from_module(cls, quantity: str, module, *, solved_attr: str,
                    tolerance_attr: str, supplied: float, source: Path,
                    unit: str = "", relative: bool = False) -> "GeometryMatch":
        """Build a match by PULLING the solved constant and tolerance out of
        the module that owns the surface, never by retyping them.

        A check that travels away from its subject acquires a copy of the
        subject's constants, and then the two drift silently. So the act names
        the owning module and the attribute; it does not name the number.
        For the jet flap that module is ``workflows._jf1_geometry``, whose
        ``measure_blown_slot`` produced ``supplied`` in the first place.

        ``relative`` defaults to FALSE here because the owning module's
        tolerance is normally an absolute one, and reading an absolute
        tolerance as a relative one is its own silent drift: the jet flap's
        1e-6 m on a chord of 1.0 m and on a height ratio of 0.005 are the same
        absolute number and two relative numbers two hundred times apart.
        """
        try:
            solved_value = float(getattr(module, solved_attr))
            tolerance = float(getattr(module, tolerance_attr))
        except AttributeError as exc:
            raise DemoContractError(
                f"{getattr(module, '__name__', module)} does not own "
                f"{exc.args[0] if exc.args else solved_attr!r}; the solved "
                f"constant must come from the module that writes the surface")
        return cls(quantity=quantity,
                   solved=Measured(solved_value, unit,
                                   Path(getattr(module, "__file__", source))),
                   supplied=Measured(supplied, unit, source),
                   tolerance=tolerance, relative=relative)

    def _gap(self) -> float:
        solved = float(self.solved.value)
        supplied = float(self.supplied.value)
        absolute = abs(supplied - solved)
        if not self.relative:
            return absolute
        return absolute / abs(solved) if solved else float("inf")

    def agrees(self) -> bool:
        try:
            return self._gap() <= self.tolerance
        except (TypeError, ValueError):
            return False

    def disagreement(self) -> str:
        solved = float(self.solved.value)
        supplied = float(self.supplied.value)
        gap = self._gap()
        if self.relative:
            spread = f"{gap * 100:.2f}% apart, tolerance {self.tolerance * 100:.2f}%"
        else:
            spread = f"{gap:.6g} apart, tolerance {self.tolerance:.6g}"
        return (f"{self.quantity}: served {supplied:.6g} {self.supplied.unit} "
                f"against solved {solved:.6g} {self.solved.unit}, {spread}")


@dataclass(frozen=True)
class Geometry:
    """Stage 4. The STL that renders, which IS the exact solved geometry.

    Sanaa: "the uploaded STL renders. It is the exact solved geometry
    (regenerate the STL from the solved case where it differs). 'No surface
    loaded' never appears."

    ``served_stl`` is the copy the CONTROL-ROOM SERVER reads, under
    :data:`SERVED_GEOMETRY_DIR` — not the copy a generator wrote. Those are two
    different files today and they agree only because someone copied by hand;
    naming the generator's copy here would let a regenerated surface serve a
    stale body with nothing failing. The validator refuses a ``served_stl``
    outside the served directory.

    ``matches`` carries the measured comparisons against the solved case.
    :meth:`solved_geometry_sentence` raises unless every one agrees, so an act
    that cannot assert the surface is the solved body is UNABLE to render the
    sentence rather than merely discouraged from it.

    ``regenerated_from`` names the solved case the STL was regenerated out of,
    when it was.
    """

    served_stl: Path
    display_label: str
    matches: Sequence[GeometryMatch]
    regenerated_from: Path | None = None

    def __post_init__(self) -> None:
        check_demo_language(self.display_label)
        if not self.matches:
            raise DemoContractError(
                "the geometry stage measures the served surface against the "
                "solved body; supply at least one GeometryMatch")

    def is_solved_geometry(self) -> bool:
        return all(m.agrees() for m in self.matches)

    def solved_geometry_sentence(self, cells: Measured) -> str:
        """The on-screen fact, or a refusal.

        Her Act A pattern: "16 operating points solved on this geometry, 39,680
        cells." Rendering it is conditional on the measurement, not on intent.

        THE PATTERN IS HERS AND THE TENSE IS HERS TOO, AND THEY DISAGREE. The
        sentence rendered "Solved on this geometry, 39,984 cells." -- read off
        the live event log of a real mission, not off this source -- and her
        04:20Z order is "no past tense", later and stricter than the Act A
        pattern it collides with. Present is the intersection, which is the
        same resolution the replay stage's elapsed line already took for the
        same conflict. So the leading verb goes and nothing else does: the
        measurement, the refusal above it, and the cell count are untouched,
        and the sentence still says only what was measured.

        Recorded rather than silently rewritten, because the struck wording is
        quoted in her own pattern one paragraph up and a reader who finds the
        two different needs to know which is current and why.
        """
        bad = [m.disagreement() for m in self.matches if not m.agrees()]
        if bad:
            raise DemoContractError(
                "the served surface is not the solved geometry, so the "
                "sentence may not be rendered; regenerate the surface from the "
                "solved case. " + "; ".join(bad))
        return f"This geometry, {cells.on_screen()}."


@dataclass(frozen=True)
class MeshPlan:
    """Stage 5. What the real mesher runs on, live, and what it draws.

    Sanaa: "Meshing runs live (2D/axisymmetric cases mesh in seconds to a
    minute): the real mesher on the uploaded STL, the computational grid drawn
    cell by cell, wall-layer zoom, slot/wall resolution table."

    ``command`` is the mesher the sequencer actually invokes on ``Geometry.stl``
    inside ``work_dir``. It is a real mesh, not a picture of one; the act
    supplies the case skeleton the mesher needs. ``cell_count`` is the count
    the run itself used, read from its own artifact, and the validator refuses
    a mismatch larger than ``cell_tolerance`` between the live mesh and it —
    a live mesh that does not reproduce the solved grid is a finding, not a
    detail.

    ``resolution_rows`` is the wall/slot resolution table, already in table
    form (R1: numbers live in tables, never in prose).
    """

    command: Sequence[str]
    work_dir: Path
    cell_count: Measured
    resolution_headers: Sequence[str]
    resolution_rows: Sequence[Sequence[str]]
    wall_zoom_hint: str              # what the wall-layer zoom should frame
    expected_seconds: float
    cell_tolerance: float = 0.0

    def __post_init__(self) -> None:
        check_demo_language(self.wall_zoom_hint)
        for header in self.resolution_headers:
            check_demo_language(str(header))
        if not self.command:
            raise DemoContractError("the meshing stage names a real mesher")


@dataclass(frozen=True)
class Feasibility:
    """Stage 6. The "30-second check before committing budget", and its result.

    Sanaa names this beat and requires its RESULT on screen, not merely its
    existence. ``check`` is what was checked in plain English; ``result`` is
    what it said; ``verdict_for_user`` is the plain-English go/no-go the user
    reads. No tier words, no gate vocabulary on screen (R5): the internal
    verdict, if the act has one, stays in the run record.
    """

    check: str
    result: Measured
    verdict_for_user: str
    seconds: float = 30.0

    def __post_init__(self) -> None:
        check_demo_language(self.check)
        check_demo_language(self.verdict_for_user)


@dataclass(frozen=True)
class SeriesSpec:
    """One monitor series the solving stage animates from a stored log.

    ``log`` is the real log file the run wrote. ``column`` names the series
    inside it. ``drives`` says which on-screen instrument this series moves,
    and is one of ``"iteration"``, ``"residual"``, ``"force"``,
    ``"temperature"`` or ``"sweep"``. The replay stage reads the log; it never
    synthesises a curve, and a series whose log is missing is a refusal, not
    an empty plot.
    """

    log: Path
    column: str
    drives: str
    label: str
    unit: str = ""

    def __post_init__(self) -> None:
        allowed = {"iteration", "residual", "force", "temperature", "sweep"}
        if self.drives not in allowed:
            raise DemoContractError(
                f"drives is one of {sorted(allowed)}, not {self.drives!r}")
        check_demo_language(self.label)


@dataclass(frozen=True)
class ElapsedClock:
    """The elapsed figure shown on screen, and the sentence that sources it.

    Sanaa's mode spec sets the default: "Elapsed time shown is the run's real
    wall time." Her amendment of 2026-09-01 (``68b10335``) makes the source
    PER-ACT CONFIGURABLE — Act D shows 20 minutes everywhere on screen, which
    supersedes real wall time for that act alone.

    A configurable clock that accepted a bare number would be the mechanism
    that strips the basis off a figure: the first act to override the default
    would put an unsourced number on camera, and the mode itself would be the
    hole. So the parameter is a PAIR. ``basis`` is not a debug field; it is the
    sentence a viewer reads beside the figure. It is mandatory, and an override
    that is not the measured wall time must say what it is instead — Act D's
    20 minutes is a projection for the production configuration with the linear
    solvers on GPU, and is legitimate only when stated with that basis. The
    run itself took 3601 s; the two numbers are different things and the
    sentence is what keeps them apart.

    Use :meth:`real_wall_time` for the default. Construct directly only to
    override, and then both halves are required.

    THE COST LINE IS NOT COVERED BY THIS OVERRIDE. It is a separate field
    (:attr:`Results.cost_actual`) and stays the run's real cost, shown as this
    run's cost, because it is. An act that overrides its clock does not thereby
    get to override its cost, and keeping them independent is what stops anyone
    assuming one follows the other.
    """

    seconds: float
    basis: str
    measured: bool
    source: Path | None = None       # internal; never on screen

    def __post_init__(self) -> None:
        if self.seconds < 0:
            raise DemoContractError("elapsed seconds >= 0")
        if not self.basis.strip():
            raise DemoContractError(
                "the elapsed clock carries its basis, not just a number; "
                "an override must supply the sentence that says what it is")
        check_demo_language(self.basis)
        if self.measured and self.source is None:
            raise DemoContractError(
                "a measured clock names the artifact its wall time came from")
        if not self.measured and len(self.basis.split()) < 5:
            raise DemoContractError(
                f"an overridden clock states the configuration it is a figure "
                f"for; {self.basis!r} is not a basis a viewer can source")

    @classmethod
    def real_wall_time(cls, wall: Measured) -> "ElapsedClock":
        """The default: this run's own measured wall time."""
        if wall.basis != "measured":
            raise DemoContractError(
                "the default clock is the run's REAL wall time and is measured")
        return cls(seconds=float(wall.value),
                   basis="Measured wall time of this run.",
                   measured=True, source=wall.source)

    def on_screen(self) -> str:
        """The elapsed figure with its basis sentence, as the viewer reads it."""
        minutes = self.seconds / 60.0
        figure = (f"{minutes:,.0f} minutes" if minutes >= 2
                  else f"{self.seconds:,.0f} seconds")
        return f"{figure}. {self.basis.rstrip('.')}."


@dataclass(frozen=True)
class SolveReplay:
    """Stage 7. The stored logs, the series they drive, and the REAL cost.

    Sanaa: "monitors advance in real time from the stored logs at accelerated
    pace: iteration counter, residuals, lift/drag or temperature curves moving;
    progress across the sweep points. Elapsed time shown is the run's real wall
    time."

    So two clocks run at once and the interface keeps them apart. The SHOOT
    clock is compressed by ``pace``; the ELAPSED TIME ON SCREEN is
    ``wall_seconds``, the run's own, because that is what the run took.
    ``ranks`` and ``wall_seconds`` together give the core-minutes and, at the
    recorded rate, the derived dollar figure — this run's cost, shown as this
    run's cost, because it is.

    ``total_iterations`` and ``sweep_points`` feed the progressive-tense lines
    ("Solving, iteration 4,000 of 20,000", "Sweep point 3 of 5"). The act
    supplies the counts; the sequencer composes and checks the wording.

    ``cases`` is the seam with the replay reader
    (``chief_engineer.replay_history``), which is a MEASUREMENT script with
    planted controls on every channel: a reader that cannot see its plant
    refuses. Supply the ``(label, case_dir)`` pairs its ``read_run_history``
    takes and the sequencer calls it; ``series`` then says which instrument
    each channel drives. Two lanes must not build two readers, and the one
    with the plants is the one that reads. ``cases`` is optional only so acts
    already written against v1 keep working; an act with no ``cases`` must say
    to its supervisor how its logs are read instead.
    """

    series: Sequence[SeriesSpec]
    wall_seconds: Measured           # the run's REAL wall time, always measured
    ranks: int
    total_iterations: int
    sweep_points: int = 1
    pace: float = 1.0                # shoot-clock compression, never on screen
    elapsed_clock: ElapsedClock | None = None   # None means the default
    cases: Sequence[tuple[str, Path]] = ()      # -> replay_history.read_run_history
    #: What the compute figure on screen DESCRIBES, when that is not this box.
    #: Declared by the act, applied by the sequencer and by the replay stage's
    #: closing sentence, so the two surfaces that state a cost state the same
    #: one. ``None`` -- every act but the jet-flap today -- leaves both
    #: byte-identical to what they were. The MEASURED core-minutes are
    #: untouched everywhere they are recorded: ``core_minutes()`` below,
    #: ``solve.end``'s ``core_min_measured``, and the cost-calibration ledger
    #: all keep reporting what this hardware actually did.
    cost_projection: "HardwareProjection | None" = None

    def __post_init__(self) -> None:
        if not self.series:
            raise DemoContractError("the solving stage replays at least one series")
        if self.ranks < 1:
            raise DemoContractError("ranks >= 1")
        if self.pace <= 0:
            raise DemoContractError("pace > 0")
        if self.total_iterations < 1:
            raise DemoContractError("total_iterations >= 1")
        if self.sweep_points < 1:
            raise DemoContractError("sweep_points >= 1")

    def clock(self) -> ElapsedClock:
        """The elapsed figure this act shows, defaulting to real wall time."""
        if self.elapsed_clock is not None:
            return self.elapsed_clock
        return ElapsedClock.real_wall_time(self.wall_seconds)

    def core_minutes(self) -> float:
        """Always from the REAL wall time, never from an overridden clock."""
        return core_minutes(float(self.wall_seconds.value), self.ranks)

    def cost_sentence(self) -> str:
        return cost_line(self.core_minutes(), projection=self.cost_projection)

    def progress_line(self, iteration: int, sweep_point: int = 1) -> str:
        """The progressive-tense running line, composed and checked here.

        Her examples: "Solving, iteration 4,000 of 20,000", "Sweep point 3 of 5".
        """
        line = f"Solving, iteration {iteration:,} of {self.total_iterations:,}"
        if self.sweep_points > 1:
            line = (f"Sweep point {sweep_point} of {self.sweep_points}. "
                    f"{line}")
        check_running_line(line.split(". ")[0], tense="progressive")
        return line


@dataclass(frozen=True)
class Table:
    """A rendered table. R1: numbers live in tables, with units and, where the
    act has one, an uncertainty column."""

    title: str
    headers: Sequence[str]
    rows: Sequence[Sequence[str]]
    table_id: str
    role: str = "NUMERICIST"

    def __post_init__(self) -> None:
        check_demo_language(self.title)
        for header in self.headers:
            check_demo_language(str(header))


@dataclass(frozen=True)
class Figure:
    """A rendered figure, under Sanaa's 2026-09-01 ~03:10Z figure standard.

    Title at most 10 words; axis labels with units; a colour bar with numeric
    ticks and the unit only; a legend inside the axes; one caption line of at
    most 20 words. Every explanation moves to the sheet text. Min and max
    appear as the colour bar's end ticks and nowhere else. The limits are
    enforced here rather than reviewed.
    """

    path: Path
    title: str
    caption: str
    beat: str

    def __post_init__(self) -> None:
        check_demo_language(self.title)
        check_demo_language(self.caption)
        if len(self.title.split()) > 10:
            raise DemoContractError(
                f"figure title is at most 10 words: {self.title!r}")
        if len(self.caption.split()) > 20:
            raise DemoContractError(
                f"figure caption is one line of at most 20 words: {self.caption!r}")
        if "\n" in self.caption:
            raise DemoContractError("a figure caption is one line")


@dataclass(frozen=True)
class GatesAndChecks:
    """Stage 8. Reader checks, conservation, grid statement, in tables.

    ``planted_checks`` is the planted-perturbation evidence: CLAUDE.md rule 3,
    a zero from a reader not shown able to see a non-zero is not evidence.
    Each row names the reader, the perturbation planted, and what it read back.
    An act with no planted check does not get this stage waived; it says so to
    its supervisor.

    ``grid_statement`` is the plain-English sentence about grids. For the
    jet-flap act it is one grid on screen (the 39,984-cell force grid) for
    fields, pressures and the lift table alike, and the finer companion grid
    is named only in ``Results.limitations``.
    """

    planted_checks: Table
    conservation: Table | None
    grid_statement: str

    def __post_init__(self) -> None:
        check_demo_language(self.grid_statement)


@dataclass(frozen=True)
class Results:
    """Stage 9. Fields, plots, tables, verification lines, limitations, cost.

    ``verification_lines`` are R6 statements: explicit, sourced, in plain
    words, with the internal verdict vocabulary already translated per R5
    ("verified against [reference] within [X]%", "run rejected: [plain
    reason]"). The gate words themselves never appear on screen.

    ``limitations`` is the visible plain-English caveat box (R7) and is checked
    in the ``limitations`` zone, which is the one place the finer-companion-grid
    sentence is permitted. Compactness is never a licence to drop a caveat: the
    validator refuses an empty box, and an act that cannot fit a caveat raises
    it with its supervisor rather than blurring it.

    ``cost_actual`` is this run's real cost. ``cost_estimate_from_stage_2`` is
    carried through so the screen can show both, per R8, and so the completion
    record can state the ratio actual/predicted per CLAUDE.md rule 12.
    """

    fields: Sequence[Figure]
    plots: Sequence[Figure]
    tables: Sequence[Table]
    verification_lines: Sequence[str]
    limitations: Sequence[str]
    cost_actual: Measured            # core-minutes, basis "measured"
    cost_estimate_from_stage_2: Measured

    def __post_init__(self) -> None:
        for line in self.verification_lines:
            check_demo_language(line)
        if not self.limitations:
            raise DemoContractError(
                "the limitations box is never empty; if a caveat will not fit, "
                "say so to the supervisor rather than dropping it")
        for line in self.limitations:
            check_demo_language(line, zone="limitations")


@dataclass(frozen=True)
class Closing:
    """The tail of stage 9. THE ACT ENDS IN A REPORT, NOT A TABLE.

    Sanaa, 2026-09-01: "Conclusion and Report tabs populated; nothing ends on
    a table." Before this the jet-flap act's last publication was
    ``demo.results`` and its last visible artifact was the lift table; the
    Report tab stayed hidden for the whole act because nothing ever published
    a ``report.ready``, and the digest never reached its Conclusion heading
    because no phase was ever opened. Both are events, not layout: the page
    has always been able to render them and no act was sending them.

    WHAT EACH FIELD REACHES.

    * ``conclusion_lines`` open the Conclusion phase in the digest, which also
      advances the cycle counter and the masthead. Spoken as bullets, so every
      line is checked by ``workflows.check_wording`` AT EMISSION -- a body
      that does not begin with a capital throws there and nowhere earlier.
    * ``title``, ``abstract``, ``methods``, ``results``, ``uncertainty`` and
      ``next_investigations`` become the Report tab through
      ``chief_engineer.lab.lab_report``. Its own rule holds and is not this
      act's to relax: ``next_investigations`` carries new questions, never
      remediations of the shown result. "Refine the grid" is a limitation and
      belongs in the limitations box, which already has it.
    * ``certificate_state`` is a REQUIRED sentence saying whether a sealed
      certificate was issued FOR THIS RUN, and it is rendered rather than
      inferred. See below: this field is the whole of the certificate block,
      and it is a string on purpose.

    NO RESULT ROW CARRIES A TIER. ``lab_report`` accepts one and the page will
    draw a badge from it; the demo standard forbids verdict-shaped words on a
    customer surface, so these rows carry quantity, value, envelope and reason
    and no verdict. The row is refused here if one is passed, rather than
    being quietly dropped downstream where the next author would re-add it.

    WHY THE CERTIFICATE BLOCK IS A SENTENCE AND NOT A LINK, and this is the
    part of this class that was designed against two measured defects rather
    than in the abstract:

    1. ``chief_engineer.certificate`` carries ``_LEGACY_TIER_ALIAS`` (lines
       49-50), which maps "TREND ONLY" and "REFERENCE REGIME MISMATCH" onto
       "SOLVER-BACKED", and text rails at 73-74 that rewrite the same words on
       the sealed page. A run that earned a weaker tier therefore PRINTS as
       solver-backed. An inflated tier is not an optimistic rendering of a
       future platform; it is a false claim about work already done, and a
       certificate is the artifact this lab is for.
    2. Certificates are written to ``mission-output/<intent>/certificate.pdf``
       and are last-writer-wins. Three different bodies have overwritten one
       such file. A surface that resolves a certificate BY PATH, mission name
       or intent can therefore render a document belonging to a different run.

    So no act here mints or links one. ``certificate_state`` is an explicit
    statement of whether this run has a sealed certificate, carried in the
    act's own record and rendered as written. A blank is honest; a neighbour's
    certificate is not.
    """

    title: str
    abstract: Sequence[str]
    methods: Sequence[str]
    results: Sequence[Mapping[str, str]]
    uncertainty: Sequence[str]
    next_investigations: Sequence[str]
    conclusion_lines: Sequence[str]
    certificate_state: str

    def __post_init__(self) -> None:
        if not self.certificate_state.strip():
            raise DemoContractError(
                "an act states whether this run carries a sealed certificate; "
                "silence would be read as one having been issued, and the "
                "certificate store is keyed by intent and is "
                "last-writer-wins, so silence is the dangerous default")
        check_demo_language(self.certificate_state)
        if not self.conclusion_lines:
            raise DemoContractError(
                "an act that ends in a report says something at the end of "
                "it; an empty conclusion is a table with a heading over it")
        for line in self.conclusion_lines:
            check_demo_language(line)
        check_demo_language(self.title)
        for group, zone in ((self.abstract, "screen"),
                            (self.methods, "screen"),
                            (self.uncertainty, "limitations"),
                            (self.next_investigations, "screen")):
            for line in group:
                check_demo_language(line, zone=zone)
        for row in self.results:
            if "tier" in row:
                raise DemoContractError(
                    "a report row on a customer screen carries no tier; the "
                    "honesty lives in the envelope, the reason and the "
                    "limitations box")
            for key, value in row.items():
                if isinstance(value, str):
                    check_demo_language(value)


# ---------------------------------------------------------------------------
# The interface itself
# ---------------------------------------------------------------------------

class DemoAct(ABC):
    """One act, plugged into DEMO MODE.

    Implement the nine methods below. Each returns facts, already read off the
    completed run tree. None of them emits an event, composes a stage header,
    paces anything, or decides an order: the sequencer does all of that, once,
    for all four acts.

    Every method is called exactly once, in :data:`STAGES` order, before
    anything renders — so a contract violation surfaces at validation time,
    with the screen still dark.

    Minimal shape::

        class MotorThermalAct(DemoAct):
            name = "motor-in-duct thermal map"

            def run_record(self) -> RunRecord: ...
            def prompt(self) -> Prompt: ...
            def restatement(self) -> Restatement: ...
            def assumption(self) -> Assumption: ...
            def geometry(self) -> Geometry: ...
            def mesh_plan(self) -> MeshPlan: ...
            def feasibility(self) -> Feasibility: ...
            def solve_replay(self) -> SolveReplay: ...
            def gates(self) -> GatesAndChecks: ...
            def results(self) -> Results: ...

        validate_act(MotorThermalAct())      # refuses before the shoot
    """

    #: Short act name for the mission log. Internal; the screen shows the
    #: prompt and the solver header, not this.
    name: str = ""

    @abstractmethod
    def run_record(self) -> RunRecord:
        """The completed run tree, and the internal presentation flag."""

    @abstractmethod
    def prompt(self) -> Prompt:
        """The user's request, in professional wording."""

    @abstractmethod
    def restatement(self) -> Restatement:
        """Restatement, confidence, upfront cost estimate."""

    @abstractmethod
    def assumption(self) -> Assumption:
        """Exactly one user-assumption check."""

    @abstractmethod
    def geometry(self) -> Geometry:
        """The STL that renders, which IS the exact solved geometry."""

    @abstractmethod
    def mesh_plan(self) -> MeshPlan:
        """What the real mesher runs, and what the live draw shows."""

    @abstractmethod
    def feasibility(self) -> Feasibility:
        """The 30-second check before committing budget, and its result."""

    @abstractmethod
    def solve_replay(self) -> SolveReplay:
        """The stored logs, the driven series, the real wall time and cost."""

    @abstractmethod
    def gates(self) -> GatesAndChecks:
        """Planted-reader checks, conservation, grid statement."""

    @abstractmethod
    def results(self) -> Results:
        """Fields, plots, tables, verification lines, limitations, cost."""

    # -- the discussion and the tail: concrete and optional ------------------

    #: The transcript roles an act may speak a discussion beat as. The
    #: control room gives each one its own colour accent, which is what makes
    #: a sequence of them read as several people rather than one narrator.
    DISCUSSION_ROLES = ("engineer", "researcher", "numericist", "monitor")

    def discussions(self) -> Mapping[str, Sequence[tuple]]:
        """Expert-agent discussion beats, keyed by the stage they follow.

        Sanaa, 2026-09-01: the user "will see discussions of the different
        expert agent letting choosing/deciding on turbulence models,
        acknowledging the physics, summarizing the geometry, summarizing user
        defined / lab assumption numbers/quantities".

        THE BOUNDARY, AND IT IS NOT NEGOTIABLE. The demo depicts the future
        platform's experience; it does not invent measurements or
        deliberations. A beat may narrate a decision that WAS ACTUALLY TAKEN
        and physics that IS ACTUALLY TRUE, in the conversational form the
        built platform will have. It may not invent a decision nobody made or
        a justification that is not real. Every number a beat states comes
        from the same readers the rest of the act uses, never from a literal
        typed beside it.

        Returns ``{stage: [(role, [line, ...]), ...]}``. Each entry is spoken
        as one bulleted transcript entry in that role, after the stage's own
        content and before the next stage opens, so the discussion sits where
        the decision belongs. An unknown stage name is a refusal rather than a
        beat that silently never plays.
        """
        return {}

    def closing(self) -> "Closing | None":
        """The report the act ends in, or ``None`` to end on the results stage.

        NOT ABSTRACT, deliberately. Four acts are already wired against this
        interface and a tenth abstract method would break every one of them at
        import; an act that has not written its report yet keeps the behaviour
        it has today and says so to its supervisor rather than shipping an
        empty Report tab. The jet-flap act overrides it.
        """
        return None

    # -- pacing and banners: concrete, override only where the act differs ---

    def banners(self) -> Mapping[str, str]:
        """Stage-to-banner map. Fixed by default; override at your peril.

        Sanaa's pacing amendment (``aaed6498``) requires the banner state to
        match what the screen is actually showing at every moment, with no
        banner ahead of or behind its content. The sequencer sets the banner
        from this map as it enters each stage, so the synchronisation is a
        property of the sequencer rather than of an act's discipline.
        """
        return dict(BANNERS)

    def agent_census(self) -> Sequence[tuple[str, int]]:
        """How many agents the act's narrative has working, stage by stage.

        Sanaa (``aaed6498``): any on-screen agent counter matches the agents
        the narrative has working AT THAT MOMENT, moving as the team forms and
        lanes spawn. Never a static number.

        The count reaches zero at the end, which also keeps the fleet numeral's
        existing attributed convention (Katie, 2026-07-31: the numeral ends at
        zero). What changes under Sanaa's instruction is the MIDDLE: no longer
        a static N appearing at meshing, but a count that moves with the
        narrative from team formation onward. That reading is the supervisor's;
        this default encodes it, and an act whose narrative differs overrides.

        The validator refuses a static census and refuses one that does not end
        at zero.
        """
        return (("prompt", 1), ("restatement", 2), ("assumption", 3),
                ("geometry", 3), ("meshing", 4), ("feasibility", 4),
                ("solving", 4), ("gates", 2), ("results", 0))


# ---------------------------------------------------------------------------
# Registration: the entry point an act module exposes
# ---------------------------------------------------------------------------

_REGISTRY: dict[str, DemoAct] = {}


def register_act(key: str, act: DemoAct) -> DemoAct:
    """Register one act under ``key`` and return it.

    THE ENTRY POINT. An act module ends with exactly one call::

        from .demo_mode import DemoAct, register_act

        class MotorThermalAct(DemoAct):
            name = "motor-in-duct thermal map"
            ...

        ACT = register_act("motor-thermal", MotorThermalAct())

    The sequencer resolves an act by key, calls :func:`validate_act` on it, and
    refuses to start if the returned list is non-empty. An act never calls the
    sequencer and never emits; registration is the whole of its coupling to
    DEMO MODE.

    Registering the same key twice raises rather than overwriting: two acts
    answering to one key is how a shoot ends up showing the wrong run.
    """
    if not isinstance(act, DemoAct):
        raise DemoContractError(
            f"{type(act).__name__} does not implement DemoAct")
    if key in _REGISTRY and _REGISTRY[key] is not act:
        raise DemoContractError(f"an act is already registered as {key!r}")
    _REGISTRY[key] = act
    return act


def registered_acts() -> Mapping[str, DemoAct]:
    """The acts registered so far, by key."""
    return dict(_REGISTRY)


# ---------------------------------------------------------------------------
# Conformance: run this before the shoot, not during it
# ---------------------------------------------------------------------------

def _require_file(path: Path, what: str, problems: list[str]) -> None:
    try:
        p = Path(path)
    except TypeError:
        problems.append(f"{what}: not a path ({path!r})")
        return
    if not p.exists():
        problems.append(f"{what}: not on disk ({p})")
    elif p.is_file() and p.stat().st_size == 0:
        problems.append(f"{what}: empty file ({p})")


def validate_act(act: DemoAct, *, check_files: bool = True) -> list[str]:
    """Walk every stage of ``act`` and return the list of problems found.

    An empty list means the act satisfies the contract as far as this checker
    can see, which is: every stage present and well-typed, every string clear
    of the never-list and of paths, every figure inside the title and caption
    limits, and — when ``check_files`` is true — every artifact a number or a
    figure cites actually on disk, non-empty.

    What it does NOT check, and no lane should claim it does: whether the
    numbers are right, whether the run converged, whether the STL truly equals
    the solved geometry (it checks that the act SAYS how that was established,
    and that the file exists), or whether a grid triple is CONVERGING. Those
    are the supervisor's and the comparators' business.

    Raising is deliberate for a malformed stage — a dataclass refuses at
    construction — while a missing artifact or a bad string is collected, so
    one run of this returns the whole list rather than the first fault.
    """
    problems: list[str] = []

    stages = {}
    for stage, method in (
        ("run_record", act.run_record), ("prompt", act.prompt),
        ("restatement", act.restatement), ("assumption", act.assumption),
        ("geometry", act.geometry), ("mesh_plan", act.mesh_plan),
        ("feasibility", act.feasibility), ("solve_replay", act.solve_replay),
        ("gates", act.gates), ("results", act.results),
    ):
        try:
            stages[stage] = method()
        except DemoContractError as exc:
            problems.append(f"{stage}: {exc}")
        except Exception as exc:                                # noqa: BLE001
            problems.append(f"{stage}: {type(exc).__name__}: {exc}")

    if not check_files:
        return problems

    record = stages.get("run_record")
    if record is not None:
        _require_file(record.run_root, "run_record.run_root", problems)
        _require_file(record.completion_evidence,
                      "run_record.completion_evidence", problems)

    geometry = stages.get("geometry")
    if geometry is not None:
        served = Path(geometry.served_stl)
        _require_file(served, "geometry.served_stl", problems)
        try:
            served.resolve().relative_to(SERVED_GEOMETRY_DIR.resolve())
        except ValueError:
            problems.append(
                f"geometry.served_stl is outside the directory the server "
                f"reads ({SERVED_GEOMETRY_DIR}); name the served copy, not "
                f"the copy a generator wrote, or a regenerated surface will "
                f"serve a stale body with nothing failing")
        for match in geometry.matches:
            if not match.agrees():
                problems.append(
                    f"geometry: the served surface is not the solved body. "
                    f"{match.disagreement()}. Regenerate the surface from the "
                    f"solved case; the sentence cannot be rendered until then")
        if geometry.regenerated_from is not None:
            _require_file(geometry.regenerated_from,
                          "geometry.regenerated_from", problems)

    mesh = stages.get("mesh_plan")
    if mesh is not None:
        _require_file(mesh.work_dir, "mesh_plan.work_dir", problems)
        _require_file(mesh.cell_count.source, "mesh_plan.cell_count", problems)

    replay = stages.get("solve_replay")
    if replay is not None:
        for i, spec in enumerate(replay.series):
            _require_file(spec.log, f"solve_replay.series[{i}].log", problems)
        _require_file(replay.wall_seconds.source,
                      "solve_replay.wall_seconds", problems)
        if replay.wall_seconds.basis != "measured":
            problems.append(
                "solve_replay.wall_seconds is the run's REAL wall time and is "
                "measured, not derived")
        try:
            clock = replay.clock()
            if clock.measured and clock.source is not None:
                _require_file(clock.source, "solve_replay clock source", problems)
        except DemoContractError as exc:
            problems.append(f"solve_replay.elapsed_clock: {exc}")

    census = list(act.agent_census())
    if census:
        counts = [n for _, n in census]
        if counts[-1] != 0:
            problems.append(
                "the agent counter ends at zero: a complete run has no agents "
                "working (Katie, 2026-07-31, and Sanaa aaed6498 does not "
                "contradict it)")
        if len(set(counts)) == 1:
            problems.append(
                "the agent counter is never a static number; it moves as the "
                "team forms and lanes spawn (Sanaa, aaed6498)")
        unknown = [stage for stage, _ in census if stage not in STAGES]
        if unknown:
            problems.append(f"agent_census names unknown stages: {unknown}")

    banners = act.banners()
    missing = [stage for stage in STAGES if stage not in banners]
    if missing:
        problems.append(f"banners: no banner state for stages {missing}")

    results = stages.get("results")
    if results is not None:
        for figure in list(results.fields) + list(results.plots):
            _require_file(figure.path, f"results figure {figure.title!r}", problems)
        _require_file(results.cost_actual.source, "results.cost_actual", problems)
        if results.cost_actual.basis != "measured":
            problems.append(
                "results.cost_actual is this run's real cost, read from the "
                "run's own record: basis 'measured'")

    return problems
