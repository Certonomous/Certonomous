"""Language/register regression tests (GUI-2b register round).

Two house rules pinned here:

1. **No em dash in user-visible strings.** The transcript, reports, agenda
   scopes, and verdict reasons are read on camera; an em dash reads as an
   LLM-ism the product owner explicitly banned ("I have told you to drop the
   dashes ... I don't ever want to see them"). Rewritten with commas, colons,
   periods, or semicolons instead. Docstrings and code comments are not
   user-visible, so they are exempt from the scan (comments are invisible to
   the AST entirely; module/class/function docstrings are located and
   excluded explicitly below).

2. **No self-grading narration.** An agent must never lecture the viewer
   about its own fidelity chip, tier, or grade, or cite a validation standard
   as a defense of its own result (see G2 in docs/HANDOFF-GUI2.md). The chip
   is still computed and stored; it is simply never spoken.
"""
from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
EM_DASH = "—"

# The exact surface the owner named: every workflow, plus the five
# chief_engineer modules whose strings feed transcript bullets, report
# sections, verdict reasons, agenda scopes, and channel notes.
_WORKFLOWS_DIR = SDK / "workflows"
_CHIEF_ENGINEER_FILES = ("researcher.py", "lab.py", "server.py",
                         "head_engineer.py", "chief_researcher.py",
                         "display_names.py", "uq.py")


def _target_files() -> list[Path]:
    files = sorted(_WORKFLOWS_DIR.glob("*.py"))
    files += [SDK / "chief_engineer" / name for name in _CHIEF_ENGINEER_FILES]
    return files


def _docstring_node_ids(tree: ast.AST) -> set[int]:
    """id() of every string-constant node that IS a docstring (module,
    class, or function/async-function), so the scan can skip them."""
    ids: set[int] = set()
    candidates: list[ast.AST] = [tree] + [
        node for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    ]
    for node in candidates:
        body = getattr(node, "body", None)
        if (body and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)):
            ids.add(id(body[0].value))
    return ids


def _non_docstring_string_literals(path: Path):
    """Yield (lineno, value) for every string-constant node that is not a
    docstring. Comments never reach this scan at all (the tokenizer drops
    them before the AST exists), and f-string literal segments are Constant
    nodes too, so they are covered."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    doc_ids = _docstring_node_ids(tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) in doc_ids:
                continue
            yield node.lineno, node.value


class NoEmDashInUserVisibleStrings(unittest.TestCase):
    """G-EMDASH: the owner's dash purge, regression-tested at the source."""

    def test_workflows_and_chief_engineer_core_carry_no_em_dash(self):
        offenders = []
        for path in _target_files():
            for lineno, value in _non_docstring_string_literals(path):
                if EM_DASH in value:
                    offenders.append(f"{path.relative_to(SDK)}:{lineno}: {value!r}")
        self.assertEqual(
            offenders, [],
            "Em dash found in a non-docstring string literal (user-visible "
            "narration/report text). Rewrite with a comma, colon, period, or "
            "semicolon instead:\n" + "\n".join(offenders))


class NoSelfGradingNarration(unittest.TestCase):
    """G-GRADE: agents state findings and next steps, never their own chip."""

    # Phrases that mean "I am now lecturing you about my own trust tier".
    # Matched as substrings so "grade" inside an unrelated word ("upgrade")
    # is not the target class of phrase, but the check below narrows on
    # word boundaries via simple containment of the exact banned phrase.
    _SELF_GRADE_PHRASES = (
        "grade: SOLVER-BACKED", "grade: RESEARCH MODEL", "grade: VALIDATED",
        "grade: UNCONVERGED", "the tier says", "the chip says",
        "per the ASME V&V 20 validation-uncertainty standard",
    )

    def test_no_self_grading_lecture_strings(self):
        offenders = []
        for path in _target_files():
            for lineno, value in _non_docstring_string_literals(path):
                for phrase in self._SELF_GRADE_PHRASES:
                    if phrase in value:
                        offenders.append(
                            f"{path.relative_to(SDK)}:{lineno}: {phrase!r} in {value!r}")
        self.assertEqual(
            offenders, [],
            "Self-grading narration found (agent lecturing about its own "
            "tier/chip/grade). State the finding and next step instead:\n"
            + "\n".join(offenders))


class GlobalRegisterRails(unittest.TestCase):
    """The overnight register rails (owner order, 2026-07-24), pinned at the
    source for every workflow and the narration-feeding chief modules:

    - no arrow glyph and no prose double hyphen in any emitted string;
    - "conceptual model" is retired (the tier is RESEARCH MODEL);
    - no raw URLs in narration (links render as source hyperlinks);
    - no internal file/path references (docs/..., anything/...*.md);
    - "solver backed" never appears in prose (the tier chip carries it).

    Docstrings and comments are exempt as before; exact CLI flags and the
    matplotlib "--" linestyle token are not prose and do not match the prose
    double-hyphen pattern.
    """

    _PROSE_DOUBLE_HYPHEN = re.compile(r"(?:\s--\s|\w--\w)")
    _MD_PATH = re.compile(r"(?:docs/|[\w.-]+/[\w./-]*\.md\b)")
    _RAW_URL = re.compile(r"https?://")
    _SOLVER_BACKED_PROSE = re.compile(r"solver[ -]backed")   # lowercase only

    def _offenders(self, check):
        out = []
        for path in _target_files():
            for lineno, value in _non_docstring_string_literals(path):
                if check(value):
                    out.append(f"{path.relative_to(SDK)}:{lineno}: {value!r}")
        return out

    def test_no_arrow_glyph(self):
        self.assertEqual(self._offenders(lambda s: "→" in s), [])

    def test_no_prose_double_hyphen(self):
        self.assertEqual(
            self._offenders(lambda s: bool(self._PROSE_DOUBLE_HYPHEN.search(s))),
            [])

    def test_no_conceptual_model(self):
        # The exact uppercase constant is the legacy-alias KEY that maps the
        # retired label onto RESEARCH MODEL at render time; the rule targets
        # the retired term ever being SPOKEN, so prose casing is what fails.
        self.assertEqual(
            self._offenders(lambda s: "conceptual model" in s.lower()
                            and s != "CONCEPTUAL MODEL"), [])

    def test_no_raw_urls(self):
        self.assertEqual(
            self._offenders(lambda s: bool(self._RAW_URL.search(s))), [])

    def test_no_internal_md_or_docs_paths(self):
        self.assertEqual(
            self._offenders(lambda s: bool(self._MD_PATH.search(s))), [])

    def test_no_solver_backed_prose(self):
        # The uppercase SOLVER-BACKED tier chip is exempt; lowercase prose
        # reassurance is not.
        self.assertEqual(
            self._offenders(
                lambda s: bool(self._SOLVER_BACKED_PROSE.search(s))), [])


def _prose_surfaces(events):
    """Every user-visible prose string one act emitted, by surface."""
    surfaces: list[str] = []
    channel_notes: list[str] = []
    tiers: list[str] = []
    for event, payload in events:
        payload = payload or {}
        if event == "transcript.entry":
            surfaces.append(payload.get("message", ""))
        elif event == "transcript.table":
            surfaces.append(payload.get("title", ""))
            surfaces += [str(c) for c in payload.get("headers", [])]
            surfaces += [str(c) for row in payload.get("rows", [])
                         for c in row]
        elif event == "uncertainty.channels":
            for ch in payload.get("channels", []):
                channel_notes.append(str(ch.get("note", "")))
                surfaces.append(str(ch.get("name", "")))
        elif event == "result.verdict":
            tiers.append(str(payload.get("tier", "")))
            surfaces += [str(payload.get(k, ""))
                         for k in ("quantity", "envelope", "reason")]
        elif event == "report.ready":
            for key in ("abstract", "methods", "uncertainty"):
                surfaces += [str(line) for line in payload.get(key, [])]
            for item in payload.get("results", []):
                tiers.append(str(item.get("tier", "")))
                surfaces += [str(item.get(k, ""))
                             for k in ("quantity", "value", "envelope",
                                       "reason")]
        elif event == "agenda.updated":
            for entry in payload.get("entries", []):
                surfaces += [str(entry.get(k, ""))
                             for k in ("title", "scope", "cost")]
        elif event == "knowledge.added":
            surfaces.append(str(payload.get("title", "")))
    return surfaces, channel_notes, tiers


class EmittedTextRegister(unittest.TestCase):
    """Walk the fast (solver-less) acts end to end and assert every register
    rule at once over the text they actually emit, so future acts inherit
    the rails rather than re-learning them."""

    # Method names that may never reach a channel note (they land on the
    # sealed page verbatim).
    _BANNED_IN_CHANNEL_NOTES = ("Monte-Carlo", "quadrature", "Eca",
                                "Hoekstra", "GCI", "least-squares", "uq-",
                                "checkMesh")

    @classmethod
    def setUpClass(cls):
        import os
        os.environ["CERTONOMOUS_SWEEP_PACE_MS"] = "0"
        cls.acts = {}
        from workflows import valve_study
        events = []
        rc = valve_study.main(
            request="minimise valve pressure loss over the cardiac cycle",
            emit=lambda e, p: events.append((e, p)))
        assert rc == 0
        cls.acts["valve"] = events
        # The upload variant: the reference-body acknowledgment strings ride
        # the same rails as everything else the act emits.
        events = []
        rc = valve_study.main(
            request="minimise valve pressure loss over the cardiac cycle",
            params={"surface": "patient_valve.stl"},
            emit=lambda e, p: events.append((e, p)))
        assert rc == 0
        cls.acts["valve-upload"] = events
        from unittest import mock
        from workflows import aircraft_optimization as aopt
        events = []
        with mock.patch.object(aopt.vspaero, "available", return_value=False):
            rc = aopt.main(request="Optimize the L/D of an airliner for 180 "
                                   "passengers and 5000 km range",
                           emit=lambda e, p: events.append((e, p)))
        assert rc == 0
        cls.acts["airliner"] = events

    def test_every_rule_on_every_emitted_prose_surface(self):
        rules = (
            ("em dash", lambda s: "—" in s),
            ("arrow", lambda s: "→" in s),
            ("prose double hyphen",
             lambda s: bool(re.search(r"(?:\s--\s|\w--\w)", s))),
            ("conceptual model", lambda s: "conceptual model" in s.lower()),
            ("raw url", lambda s: bool(re.search(r"https?://", s))),
            ("internal path",
             lambda s: bool(re.search(r"(?:docs/|[\w.-]+/[\w./-]*\.md\b)", s))),
            ("solver-backed prose",
             lambda s: bool(re.search(r"solver[ -]backed", s))),
            ("live label", lambda s: s.strip().lower().endswith(", live")),
        )
        for act, events in self.acts.items():
            surfaces, channel_notes, tiers = _prose_surfaces(events)
            self.assertTrue(surfaces, act)
            for text in surfaces + channel_notes:
                for name, hit in rules:
                    self.assertFalse(hit(text), f"{act}: [{name}] {text!r}")

    def test_channel_notes_never_name_a_method(self):
        for act, events in self.acts.items():
            _surfaces, channel_notes, _tiers = _prose_surfaces(events)
            self.assertTrue(channel_notes, act)
            for note in channel_notes:
                for banned in self._BANNED_IN_CHANNEL_NOTES:
                    self.assertNotIn(banned, note, f"{act}: {note!r}")

    def test_tier_is_research_model_never_conceptual(self):
        for act, events in self.acts.items():
            _surfaces, _notes, tiers = _prose_surfaces(events)
            for tier in tiers:
                self.assertNotEqual(tier.upper(), "CONCEPTUAL MODEL", act)


if __name__ == "__main__":
    unittest.main()
