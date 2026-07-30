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
EN_DASH = "–"

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


# WHY THIS FILE GOT WIDER (owner, 2026-07-30). The dash rule regressed while
# every test above it stayed green, because the checks only ever looked at
# transcript prose. Dashes had moved onto surfaces no check watched: viewport
# and field labels ("MACH tutorial wing, baseline — C_d 0.029620"), plot
# titles and axis labels, dispatch slot text, roster blurbs, certificate
# lines. The coverage was narrower than the rule, so the rule rotted where the
# coverage ended.
#
# Two widenings close it, and they are deliberately different in kind:
#
#   * SOURCE-WIDE (below): every module under workflows/ and chief_engineer/,
#     not a hand-kept list of seven. A new act inherits the rails the moment
#     it is written, with no test edit required.
#   * PAYLOAD-WIDE (further down): every string in every field of every event
#     an act emits, not a hand-kept list of field names. A new act that
#     invents a new label field is covered the day it invents it.
#
# Both are default-deny. That is the whole point: the previous design was
# default-allow, and default-allow is what let the labels through.

def _all_source_files() -> list[Path]:
    """Every module that can put a string on a camera surface."""
    return sorted(SDK.glob("workflows/*.py")) + sorted(SDK.glob("chief_engineer/*.py"))


def _is_dash_machinery(value: str) -> bool:
    """True for a literal that DETECTS or folds dashes rather than speaking.

    The sanitizers have to name the characters they strip: ``"—"`` as a
    replace() source, ``"[–—]"`` as a banned pattern, ``" -—:·,"`` as a strip
    set. Prose always carries letters or digits, so "no alphanumerics" tells
    the two apart exactly, with no allow-list to keep up to date.
    """
    return not any(ch.isalnum() for ch in value)


# A rule's own detector has to spell the thing it forbids. `_BANNED_PHRASES`
# in workflows/__init__.py literally contains "solver backed" and "conceptual
# model"; `_GLYPH_FOLD` in certificate.py contains the dash characters it
# folds. Scanning those as if they were speech is what left this suite red
# (four checks, including the em-dash one, were failing at HEAD on nothing but
# their own vocabulary, so a real regression had nowhere to stand out).
# Assignments whose target name says "this is a list of forbidden things" are
# therefore exempt, and nothing else is.
_DETECTOR_NAME = re.compile(
    r"BANNED|GLYPH|LEGACY|RETIRED|FORBIDDEN|_PATTERNS?$|ALIAS", re.IGNORECASE)


def _detector_literal_ids(tree: ast.AST) -> set[int]:
    """id() of every string constant that is part of a detector's vocabulary."""
    ids: set[int] = set()
    for node in ast.walk(tree):
        targets: list[ast.AST] = []
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        else:
            continue
        names = [t.id for t in targets if isinstance(t, ast.Name)]
        if not any(_DETECTOR_NAME.search(n) for n in names):
            continue
        for child in ast.walk(node):
            if isinstance(child, ast.Constant) and isinstance(child.value, str):
                ids.add(id(child))
    return ids


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
    skip = _docstring_node_ids(tree) | _detector_literal_ids(tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) in skip:
                continue
            yield node.lineno, node.value


class NoEmDashInUserVisibleStrings(unittest.TestCase):
    """G-EMDASH: the owner's dash purge, regression-tested at the source."""

    def test_workflows_and_chief_engineer_core_carry_no_em_dash(self):
        offenders = []
        for path in _target_files():
            for lineno, value in _non_docstring_string_literals(path):
                # A bare "—" is the dash guard in check_wording naming the
                # character it rejects, not narration.
                if EM_DASH in value and not _is_dash_machinery(value):
                    offenders.append(f"{path.relative_to(SDK)}:{lineno}: {value!r}")
        self.assertEqual(
            offenders, [],
            "Em dash found in a non-docstring string literal (user-visible "
            "narration/report text). Rewrite with a comma, colon, period, or "
            "semicolon instead:\n" + "\n".join(offenders))

    def test_every_module_that_can_reach_a_camera_surface_is_dash_free(self):
        """The wide net: every module, em dash AND en dash.

        The narrow test above passes over a file list written by hand. This
        one takes the whole of workflows/ and chief_engineer/, so a module
        added tomorrow is covered without anyone remembering to add it, and
        so a label that never touches the transcript (a viewport caption, a
        plot title, a dispatch blurb) is covered too.
        """
        offenders = []
        for path in _all_source_files():
            for lineno, value in _non_docstring_string_literals(path):
                if _is_dash_machinery(value):
                    continue
                for glyph, name in ((EM_DASH, "em dash"), (EN_DASH, "en dash")):
                    if glyph in value:
                        offenders.append(
                            f"{path.relative_to(SDK)}:{lineno}: [{name}] {value!r}")
        self.assertEqual(
            offenders, [],
            "A dash reached a string that can be rendered on camera. This is "
            "the rule that keeps regressing, so read the guidance: rewrite the "
            "sentence, do not swap in another dash character. A comma, a full "
            "stop, or a restructured clause. Ranges read 'lo to hi'. Genuine "
            "compound words keep a plain hyphen (well-posed, wall-mounted).\n"
            + "\n".join(offenders))


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


# --------------------------------------------------------------------------
# The act corpus: real event streams, run once and shared
# --------------------------------------------------------------------------
# Every act here runs end to end with no solver attached, so the suite stays
# fast and hermetic. It is a module-level cache rather than one class's
# setUpClass because more than one TestCase reads it and unittest gives no
# ordering guarantee between classes.
_ACTS: dict[str, list] = {}


def run_acts() -> dict[str, list]:
    """Run the solver-less acts once and return {act name: [(event, payload)]}."""
    if _ACTS:
        return _ACTS
    import os
    from unittest import mock
    os.environ["CERTONOMOUS_SWEEP_PACE_MS"] = "0"

    def collect(fn, **kwargs) -> list:
        events: list = []
        rc = fn(emit=lambda e, p: events.append((e, p)), **kwargs)
        assert rc == 0, f"{fn.__module__} returned {rc}"
        return events

    from workflows import valve_study
    _ACTS["valve"] = collect(
        valve_study.main,
        request="minimise valve pressure loss over the cardiac cycle")
    # The upload variant: the reference-body acknowledgment strings ride the
    # same rails as everything else the act emits.
    _ACTS["valve-upload"] = collect(
        valve_study.main,
        request="minimise valve pressure loss over the cardiac cycle",
        params={"surface": "patient_valve.stl"})

    from workflows import aircraft_optimization as aopt
    with mock.patch.object(aopt.vspaero, "available", return_value=False):
        _ACTS["airliner"] = collect(
            aopt.main,
            request="Optimize the L/D of an airliner for 180 passengers "
                    "and 5000 km range")

    # The adjoint act is in the corpus because it is where the dash
    # regression actually lived: its viewport and field labels are the
    # densest label surface any act produces (about a hundred frames), and
    # it replays baked artifacts, so it needs no solver to run here.
    try:
        from workflows import adjoint_optimization
        _ACTS["adjoint"] = collect(
            adjoint_optimization.main,
            request="Cut the drag on the wing with the discrete adjoint and "
                    "verify the gradient against finite differences.")
    except Exception as exc:            # pragma: no cover - artifact absent
        raise AssertionError(
            "the adjoint act could not be replayed for the register sweep, so "
            "its ~100 viewport labels went unchecked: " + repr(exc)) from exc
    return _ACTS


# --------------------------------------------------------------------------
# Payload-wide camera surface walk
# --------------------------------------------------------------------------
# `_prose_surfaces` above reads a hand-written list of eight event types and
# their named fields. That list is what the dash regression walked straight
# past: `geometry.ready` and `field.ready` are not in it, so their `label`
# was never read, so "MACH tutorial wing, baseline — C_d 0.029620" sat on the
# viewport under a green suite. The walk below takes the opposite stance and
# reads EVERY string in EVERY field of EVERY event.

# The only keys skipped, and why: each addresses a machine, not a viewer.
# `url`/`png`/`path`/`workspace`/`image`/`container` are locations, the `*_id`
# family and `series` are join keys, `values`/`vertices`/`faces` are raw
# numeric payloads. Nothing here is ever rendered as a sentence. Every other
# key in every payload is treated as camera text by default, which is what
# makes a newly invented label field covered on the day it is invented.
_NON_CAMERA_KEYS = frozenset({
    "url", "png", "path", "paths", "file", "image", "workspace", "container",
    "runtime", "mission_id", "worker_id", "agent_id", "table_id", "id",
    "series", "values", "vertices", "faces", "view", "axes",
})


def _camera_strings(events):
    """Every string an act put on a camera surface, keyed by where it sat.

    Yields (event_name, key_path, text) so a failure names the exact field to
    fix rather than leaving someone to grep for the sentence.
    """
    out: list[tuple[str, str, str]] = []

    def walk(node, event: str, trail: str, key: str | None):
        if isinstance(node, str):
            if key not in _NON_CAMERA_KEYS:
                out.append((event, trail, node))
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, event, f"{trail}.{k}" if trail else str(k), str(k))
        elif isinstance(node, (list, tuple)):
            for v in node:
                walk(v, event, f"{trail}[]", key)

    for event, payload in events:
        walk(payload or {}, str(event), "", None)
    return out


# The register rails, one place, applied by both the payload walk and the
# self-test below. Each is (name, predicate-on-a-string).
CAMERA_RULES = (
    ("em dash", lambda s: EM_DASH in s),
    ("en dash", lambda s: EN_DASH in s),
    ("arrow", lambda s: "→" in s),
    ("hyphen used as a sentence connector",
     lambda s: bool(re.search(r"\S\s+-\s+\S", s))),
    ("prose double hyphen",
     lambda s: bool(re.search(r"(?:\s--\s|\w--\w)", s))),
    ("conceptual model", lambda s: "conceptual model" in s.lower()),
    ("raw url", lambda s: bool(re.search(r"https?://", s))),
    ("internal path",
     lambda s: bool(re.search(r"(?:docs/|[\w.-]+/[\w./-]*\.md\b)", s))),
    ("solver-backed prose", lambda s: bool(re.search(r"solver[ -]backed", s))),
    ("live label", lambda s: s.strip().lower().endswith(", live")),
)


def camera_offenders(events) -> list[str]:
    """Every register violation on every camera surface of one act's stream."""
    found = []
    for event, trail, text in _camera_strings(events):
        for name, hit in CAMERA_RULES:
            if hit(text):
                found.append(f"[{name}] {event}.{trail}: {text!r}")
    return found


class CameraSurfaceRegister(unittest.TestCase):
    """Every rail, on every field of every event, for every act run here.

    This is the check that would have caught the viewport-label regression.
    """

    @classmethod
    def setUpClass(cls):
        cls.acts = run_acts()

    def test_no_dash_reaches_any_camera_surface(self):
        for act, events in self.acts.items():
            offenders = camera_offenders(events)
            self.assertEqual(
                offenders, [],
                f"{act}: text on a camera surface breaks the register. These "
                f"fields are rendered in the viewport, on plots, in tables, on "
                f"chips and on the certificate, so they obey the same rules as "
                f"the transcript:\n" + "\n".join(offenders))

    def test_the_walk_actually_reaches_viewport_and_plot_labels(self):
        """Coverage guard: prove the walk reads the fields that regressed.

        A walk that silently stopped reaching `geometry.ready.label` would
        make the test above pass for the wrong reason, which is exactly the
        failure mode being fixed. So assert the fields are in the swept set.
        """
        reached = {(e, t) for events in self.acts.values()
                   for e, t, _ in _camera_strings(events)}
        events_seen = {e for e, _ in reached}
        for required in ("geometry.ready", "transcript.entry",
                         "certificate.ready", "report.ready"):
            self.assertIn(required, events_seen,
                          f"the acts under test emit no {required}, so the "
                          f"camera walk proves nothing about it")
        self.assertIn(
            ("geometry.ready", "label"), reached,
            "geometry.ready.label is not being swept. That is the exact field "
            "the em dash regression hid in.")

    def test_a_new_act_introducing_a_dashed_label_fails_loudly(self):
        """The regression, reconstructed, must be caught.

        These are the real strings that were live on camera on 2026-07-30,
        replayed through the walk. Every one must be reported, and reported
        with the field name, so an act author sees what to fix.
        """
        regressed = [
            ("geometry.ready",
             {"url": "/api/field/x/y.json",
              "label": "MACH tutorial wing, baseline — C_d 0.029620 at C_L 0.5"}),
            ("field.ready",
             {"label": "Where the adjoint says to push — descent direction "
                       "on the skin, C_d at fixed C_L"}),
            ("trace.point",
             {"series": "Cd_history", "x": 3, "y": 0.026,
              "title": "Drag at fixed lift – C_L = 0.5",
              "x_label": "major iteration", "y_label": "C_d"}),
            ("plot.ready", {"title": "Skin friction — separation and reattachment"}),
            ("transcript.table",
             {"headers": ["Quantity", "Value"],
              "rows": [["Span", "34.1 m"], ["Sweep", "25 - 35 deg"]]}),
            ("dispatch.update", {"label": "worker 3 — solving finalist 7"}),
        ]
        offenders = camera_offenders(regressed)
        # One per dashed string: 2 labels, 1 trace title, 1 plot title,
        # 1 table cell, 1 dispatch label.
        self.assertEqual(len(offenders), 6, offenders)
        joined = "\n".join(offenders)
        for field in ("geometry.ready.label", "field.ready.label",
                      "trace.point.title", "plot.ready.title",
                      "transcript.table.rows[][]", "dispatch.update.label"):
            self.assertIn(field, joined,
                          f"the walk did not name {field} in its report")

    def test_machinery_literals_are_not_mistaken_for_prose(self):
        """The sanitizers name the characters they strip; that is not speech."""
        for literal in ("—", "–", "[–—]", " -—:·,", "→"):
            self.assertTrue(_is_dash_machinery(literal), literal)
        for prose in ("baseline — C_d 0.02", "Re 100–200", "a — b"):
            self.assertFalse(_is_dash_machinery(prose), prose)


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
        cls.acts = run_acts()

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
