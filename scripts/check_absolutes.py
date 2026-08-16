#!/usr/bin/env python3
"""An absolute claim is a claim about a population, written by someone who
checked a sample. This module finds them and asks what executed them.

WHY THIS EXISTS (L-76, docket B3). Six times in two days this lab shipped an
absolute that was false. The shape is constant:

  * "It cannot happen again, because the sentences are now IN THE REPOSITORY"
    -- true of three of four published figures, false of the fourth, and the
    fourth was the figure whose contradiction had made the table stale.
  * "Every linear-algebra `rank` in this corpus is a word" -- false, several
    are digits, and an exclusion rule was built on the claim.
  * "generated from one provenance table, so it cannot drift" -- the sentence
    containing that clause was itself a stale copy when it was read.
  * "All hold. No fourth absolute." -- overturned by the entry after it.
  * "the three `BaseException`s propagate exactly as documented" -- overstates
    by one.
  * fd855017: a crash-boundary absolute replaced by the width it actually has.

Two of those six had rules or code built on top of them, which is why blast
radius is part of the output and not a footnote.

THE RULE THIS MECHANISES. No absolute -- never / always / cannot / impossible
/ every / all / none / must not / no X can / guaranteed / no longer -- ships in
a docstring, comment, report or camera surface without an executed check named
beside it.

WHAT "NAMED BESIDE IT" MEANS, in one sentence, and it is a design decision
rather than a discovery: a check is named beside a claim when the ENCLOSING
PROSE UNIT -- one docstring, one contiguous comment block, or one paragraph --
contains a test name that EXISTS in the tracked test corpus, a
`<path>.py:<function>` reference whose path is tracked, or a runnable command.
Three consequences, each of them executed rather than promised:

  * the unit is the window. A test named two paragraphs away does not back a
    claim, because a reader of the paragraph does not see it.
    Evidence: `test_a_check_named_in_another_paragraph_does_not_back_the_claim`.
  * the name must resolve. A cited test that does not exist is reported as its
    own class, `CITES_MISSING_CHECK`, and is counted as unbacked -- a name that
    resolves to nothing is a worse claim than none. A MIXED unit, citing one
    name that resolves and one that does not, is `CITES_MISSING_CHECK` too:
    the reader who spot-checks one citation and finds it good stops checking.
    That rule is the more severe of the two available and the reason string
    says when it fired on a mixed unit, so the call stays reviewable.
    Evidence: `test_a_cited_test_that_does_not_exist_is_not_backing`,
    `test_a_dangling_name_beside_a_runnable_command_still_fires`,
    `test_a_dangling_name_beside_a_resolving_test_still_fires`, and the
    must-not-match control
    `test_a_unit_whose_every_citation_resolves_is_not_flagged`.
  * backing is unit-level, not sentence-level. One named test backs every
    absolute in its paragraph. That is coarse in the lab's favour and it is a
    stated source of false negatives, measured in the sample below rather than
    argued about. Evidence: `test_backing_is_unit_level_and_that_is_stated`.

WHY THIS IS NOT A GREP. The corpus is full of legitimate absolutes, and a
checker that flags them gets switched off inside a day -- after which it is
worse than nothing, because it looks like coverage. Five exemption classes,
each mechanical, each checkable, each a measured cost:

  QUOTED        the keyword sits inside backticks or quotation marks, or on a
                blockquote line. Quoting a rule is stating the rule.
  HEDGED        a retraction, attribution or negation marker sits near the
                keyword: "an earlier version said", "turned out", "not true".
  RULE          the sentence is normative, not descriptive -- it opens with an
                imperative absolute or carries a deontic modal (must, shall,
                may not, is required to). A rule is an instruction about the
                future, not a claim about the present.
  DEFINITIONAL  "by definition", "by construction", "identically", "trivially".
  BACKED        a check is named in the unit, as defined above.

Everything else is UNBACKED, and UNBACKED is the only class that is reported as
a defect.

THE FALSE-POSITIVE RATE IS MEASURED, NOT ASSERTED. A hand-labelled sample of
real corpus claims lives at `sdk/tests/fixtures/absolute_claims_labelled.json`,
each record carrying the prose unit, the suffix, a label and a reason. The
rate is recomputed from that file by `measure_against_sample()`; nothing is
typed into this docstring, because a typed figure goes stale the day a family
is added and every test still passes.
Evidence: `test_the_sample_measurement_is_recomputed_not_typed`.

A second citation stood here until 2026-08-11 and was STRUCK rather than
written -- a name promising that the published rate in the audit matched the
recomputed one. It is not repeated here even as a corpse, because this
module's own rule is that a name resolving to nothing reads as backing. It was
aspirational, and it was aspirational about a comparison that does not hold.
The rate published in docket B3a was measured on
`absolute_claims_labelled_second_instance.json`, a 75-record sample by a
different labeller; `SAMPLE_PATH` above is the 100-record sample, and replaying
that one here yields a different rate. Two samples, two rates, one docket row
-- filed as D50, not papered over with a test name.

VERDICTS, AND THE ORDER OF THE TWO QUESTIONS. "Did the check run?" is answered
before "what did it find?", and there are three answers, not two:

  UNKNOWN   a selected file could not be read or could not be parsed, or the
            file selection itself failed. A file that raised is not a file with
            no absolutes. Claims found before that point are still listed and
            the verdict is still UNKNOWN.
  FLAGGED   the sweep completed and found unbacked absolutes.
  CLEAN     the sweep completed and found none.
Evidence: `test_an_unreadable_file_yields_unknown_not_a_clean_zero`,
`test_an_unparseable_python_file_yields_unknown`.

THE FRAME IS DERIVED, NOT ENUMERATED. The file list comes from `git ls-files`
via `scripts/sweep.py`'s `TRACKED_ONLY` frame, filtered by suffix. A hand
enumeration is the same defect one level up: V16's author enumerated his
sweep's surfaces and a derived sweep found two he had missed.
Evidence: `test_a_surface_nobody_has_ever_named_is_in_frame`.

R-DEPTH. This module is an instrument. Its tests are an instrument checking an
instrument, which is depth 2 and the cap. A checker for this checker's checker
is filed, not executed.

USAGE

    python3 scripts/check_absolutes.py --frame tracked
    python3 scripts/check_absolutes.py --frame tracked --top 20
    python3 scripts/check_absolutes.py --paths scripts/check_absolutes.py
    python3 scripts/check_absolutes.py --measure-sample

    from scripts.check_absolutes import audit, classify_unit
    res = audit(frame="tracked")
    res.verdict          # "CLEAN" | "FLAGGED" | "UNKNOWN"
    print(res.report())  # frame block, verdict, then findings by blast radius
"""
from __future__ import annotations

import argparse
import ast
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import tokenize
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

REPO = Path(__file__).resolve().parents[1]

__all__ = [
    "ABSOLUTE_FAMILIES",
    "PROSE_SUFFIXES",
    "Claim",
    "ProseUnit",
    "AuditResult",
    "audit",
    "classify_unit",
    "extract_units",
    "known_test_names",
    "measure_against_sample",
    "SAMPLE_PATH",
]

# scripts/sweep.py is another agent's sanctioned frame-stating sweep helper.
# The file selection and the three-verdict discipline are reused from it rather
# than rewritten; it is loaded by path because `scripts/` is not a package.
_SWEEP_SPEC = importlib.util.spec_from_file_location(
    "certonomous_sweep_for_absolutes", REPO / "scripts" / "sweep.py")
sweep_mod = importlib.util.module_from_spec(_SWEEP_SPEC)
sys.modules[_SWEEP_SPEC.name] = sweep_mod
_SWEEP_SPEC.loader.exec_module(sweep_mod)

SAMPLE_PATH = REPO / "sdk" / "tests" / "fixtures" / "absolute_claims_labelled.json"
DEFAULT_SIZE_CAP = 4 * 1024 * 1024

# --------------------------------------------------------------------------
# What counts as an absolute
# --------------------------------------------------------------------------
# Declaration order is match precedence: two families overlapping on the same
# offset resolve to the one declared first, so `must not` is not also counted
# as `none`. Every word the docket names has a family here, including the two
# broad ones (`all`, `every`); their cost is measured per family in the sample
# rather than guessed at, and a caller who wants them off passes --families.
ABSOLUTE_FAMILIES: dict[str, str] = {
    "must-not": r"\bmust\s+(?:not|never)\b",
    "no-x-can": r"\bno\s+\w+\s+(?:can|could|will|would|may|ever)\b",
    "no-longer": r"\bno\s+longer\b",
    "never": r"\bnever\b",
    "always": r"\balways\b",
    "cannot": r"\b(?:cannot|can\s+not|can['’]t)\b",
    "impossible": r"\bimpossibl[ey]\b",
    "guaranteed": r"\bguarantee(?:s|d)?\b",
    "every": r"\bevery(?:one|thing|where)?\b",
    "none": r"\b(?:none|nothing|nobody|no\s+one)\b",
    "all": r"\ball\b",
}

_FAMILY_RE = {name: re.compile(pat, re.IGNORECASE)
              for name, pat in ABSOLUTE_FAMILIES.items()}

#: `could not` / `couldn't` are deliberately NOT in the `cannot` family. In
#: this corpus they overwhelmingly narrate a past event ("the guard could not
#: have seen any of them"), which is a report, not a claim about a population.
#: That is a stated blind spot, priced in the sample's false-negative column
#: rather than argued about.
PAST_TENSE_MODALS_EXCLUDED = ("could not", "couldn't")

# --------------------------------------------------------------------------
# Gates. A naive absolute-hunter is useless on this corpus: the first run of
# this module over the tracked frame returned 12,478 flags, and the top of the
# list was `or None when the increments change sign` -- a Python literal in a
# return-value docstring. Three gates below reduce that, each one mechanical,
# each one reported as its own non-defect class so the reader can count what
# was dropped and disagree with it.
# --------------------------------------------------------------------------
QUANTIFIER_FAMILIES = ("every", "all", "none")
CODE_SUFFIXES = (".py", ".js", ".sh")

#: `all`/`every` inside a fixed idiom is not a quantifier over a population.
IDIOMS = (
    "at all", "after all", "first of all", "all right", "all along",
    "all in all", "above all", "all the way", "all of a sudden", "in all",
    "all but", "all over", "every time", "every other", "every now",
    "every so often", "none the", "nothing but",
)
_CARDINAL = (r"(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten|"
             r"eleven|twelve)")
#: `all three cases pass` quantifies over an enumerated, countable set. It is
#: a checkable claim, but it is not the defect class L-76 records -- that class
#: is a claim about a population the author could not enumerate. Out of scope,
#: and said so.
_BOUNDED_RE = re.compile(
    rf"\b(?:all|every|none)\b(?:\s+of)?(?:\s+(?:the|these|those|its|his|her|"
    rf"their|our|my))?\s+{_CARDINAL}\b", re.IGNORECASE)
#: A universal quantifier makes a CLAIM only when it predicates something.
#: `reverse every face's winding` is an instruction; `every rank in this
#: corpus is a word` is the L-76 defect. The discriminator is a verb of state
#: or of holding, occurring AFTER the quantifier in the same sentence.
_PREDICATION_RE = re.compile(
    r"\b(?:is|are|was|were|isn['’]t|aren['’]t|has|have|had|holds?|does|do|did|"
    r"remains?|stays?|carries|carried|passes|passed|fails?|failed|returns?|"
    r"reaches|covers|matches|means|becomes?|shows?|proves?|agrees?|"
    r"contains?|includes?|can|cannot|will|would|must|should|never|always)\b",
    re.IGNORECASE)

# Gate outcomes. Not defects, and each one counted separately in the verdict.
CODE_TOKEN = "CODE_TOKEN"
IDIOM = "IDIOM"
BOUNDED = "BOUNDED"
NOT_A_PREDICATION = "NOT_A_PREDICATION"

# --------------------------------------------------------------------------
# What counts as a named check
# --------------------------------------------------------------------------
TEST_NAME_RE = re.compile(r"\btest_[A-Za-z0-9_]{3,}\b")
TEST_CLASS_RE = re.compile(r"\b[A-Z][A-Za-z0-9]{3,}Tests?\b")
FILE_FUNC_RE = re.compile(r"\b([\w./-]+\.(?:py|sh|js))::?([A-Za-z_]\w*)")
COMMAND_RE = re.compile(
    r"(?:^|[`$(\s])(?:python3?\s+-m\s+\S+|python3?\s+\S+\.py|pytest\b|"
    r"unittest\b|bash\s+\S+\.sh|make\s+\w+|\./scripts/\S+|\./sdk/\S+)")

# --------------------------------------------------------------------------
# Exemption vocabularies. Narrow on purpose: every widening buys precision
# with false negatives, and the sample below prices both directions.
# --------------------------------------------------------------------------
HEDGE_MARKERS = (
    "not true", "no longer true", "turned out", "turns out", "retract",
    "overturn", "was false", "is false", "proved false", "an earlier version",
    "used to say", "used to read", "used to claim", "wrongly", "falsif",
    "we thought", "i thought", "the claim that", "claimed", "claims that",
    "asserted", "wrote that", "records that", "which was wrong", "was wrong",
    "is wrong", "mistaken", "did not hold", "does not hold", "counterexample",
    "the old claim", "the previous claim", "would have said",
)
RULE_MARKERS = (
    " must ", " must,", " shall ", " may not ", " is required", " are required",
    " is forbidden", " is banned", "the rule is", "rule:", " do not ",
    " don't ", " refuses to ", " may only ", " ought to ", " is to be ",
)
RULE_OPENERS = re.compile(
    r"^\s*(?:[-*>#]+\s*)?(?:\*\*)?(?:never|always|no|none|do not|don['’]t)\b",
    re.IGNORECASE)
DEFINITIONAL_MARKERS = (
    "by definition", "by construction", "definitionally", "identically",
    "trivially", "tautolog", "axiom", "theorem", "a proof", "algebraically",
)

# Verdict names for a single claim.
BACKED = "BACKED"
QUOTED = "QUOTED"
HEDGED = "HEDGED"
RULE = "RULE"
DEFINITIONAL = "DEFINITIONAL"
UNBACKED = "UNBACKED"
CITES_MISSING_CHECK = "CITES_MISSING_CHECK"

#: The classes that count as a defect. `CITES_MISSING_CHECK` is here because a
#: name that resolves to nothing reads as backing to every human who sees it.
DEFECT_CLASSES = (UNBACKED, CITES_MISSING_CHECK)


# --------------------------------------------------------------------------
# Surfaces. Suffix -> extractor name; stated in the frame block, derived from
# `git ls-files`, never enumerated by path.
# --------------------------------------------------------------------------
PROSE_SUFFIXES: dict[str, str] = {
    ".py": "python docstrings and comment blocks",
    ".md": "markdown paragraphs outside fenced code",
    ".html": "html comments and tag-stripped text",
    ".tex": "latex comments and paragraphs",
    ".sh": "shell comment blocks",
    ".js": "javascript comment blocks",
    ".txt": "plain-text paragraphs",
}


@dataclass(frozen=True)
class ProseUnit:
    """One docstring, one contiguous comment block, or one paragraph."""

    path: str
    lineno: int
    kind: str
    text: str


@dataclass(frozen=True)
class Claim:
    path: str
    lineno: int
    kind: str
    family: str
    keyword: str
    sentence: str
    verdict: str
    reason: str
    blast: int
    blast_words: str

    @property
    def is_defect(self) -> bool:
        return self.verdict in DEFECT_CLASSES

    def line(self) -> str:
        return (f"{self.path}:{self.lineno} [{self.verdict}] "
                f"blast {self.blast} ({self.blast_words}) "
                f"<{self.family}> {self.sentence[:180]}")


# --------------------------------------------------------------------------
# Extraction
# --------------------------------------------------------------------------

def _blank(text: str, pattern: re.Pattern) -> str:
    """Replace each match with spaces, preserving length and line numbers."""
    def repl(m: re.Match) -> str:
        return "".join("\n" if c == "\n" else " " for c in m.group(0))
    return pattern.sub(repl, text)


_FENCE_RE = re.compile(r"^(?P<f>```|~~~).*?(?:^(?P=f).*?$|\Z)",
                       re.MULTILINE | re.DOTALL)
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_SCRIPT_RE = re.compile(r"<(script|style)\b.*?</\1>", re.DOTALL | re.IGNORECASE)
_TAG_RE = re.compile(r"<[^>]*>", re.DOTALL)
_JS_BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)


def _paragraphs(text: str, path: str, kind: str) -> list[ProseUnit]:
    """Blank-line separated paragraphs, each carrying its first line number."""
    units: list[ProseUnit] = []
    lines = text.splitlines()
    buf: list[str] = []
    start = 1
    for i, line in enumerate(lines, start=1):
        if line.strip():
            if not buf:
                start = i
            buf.append(line)
        elif buf:
            units.append(ProseUnit(path, start, kind, "\n".join(buf)))
            buf = []
    if buf:
        units.append(ProseUnit(path, start, kind, "\n".join(buf)))
    return units


def _hash_comment_blocks(text: str, path: str, kind: str,
                         marker: str = "#") -> list[ProseUnit]:
    units: list[ProseUnit] = []
    buf: list[str] = []
    start = 1
    prev = -10
    for i, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith(marker):
            body = stripped[len(marker):].strip()
            if not buf or i != prev + 1:
                if buf:
                    units.append(ProseUnit(path, start, kind, "\n".join(buf)))
                buf, start = [], i
            buf.append(body)
            prev = i
        elif buf and i != prev:
            continue
    if buf:
        units.append(ProseUnit(path, start, kind, "\n".join(buf)))
    return units


def _python_units(text: str, path: str) -> list[ProseUnit]:
    """Docstrings via `ast`, comment blocks via `tokenize`.

    A file that will not parse raises, and the caller turns that into UNKNOWN
    rather than into an absence of absolutes.
    """
    units: list[ProseUnit] = []
    tree = ast.parse(text)
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef,
                                 ast.AsyncFunctionDef)):
            continue
        doc = ast.get_docstring(node, clean=False)
        if not doc:
            continue
        first = node.body[0]
        units.append(ProseUnit(path, getattr(first, "lineno", 1),
                               "docstring", doc))
    comments: list[tuple[int, str]] = []
    for tok in tokenize.generate_tokens(io.StringIO(text).readline):
        if tok.type == tokenize.COMMENT:
            comments.append((tok.start[0], tok.string.lstrip("#").strip()))
    buf: list[str] = []
    start = 0
    prev = -10
    for lineno, body in comments:
        if buf and lineno != prev + 1:
            units.append(ProseUnit(path, start, "comment", "\n".join(buf)))
            buf = []
        if not buf:
            start = lineno
        buf.append(body)
        prev = lineno
    if buf:
        units.append(ProseUnit(path, start, "comment", "\n".join(buf)))
    return units


def extract_units(text: str, suffix: str, path: str = "<text>") -> list[ProseUnit]:
    """The prose units of one file. Raises on a file that will not parse."""
    if suffix == ".py":
        return _python_units(text, path)
    if suffix == ".md":
        return _paragraphs(_blank(text, _FENCE_RE), path, "paragraph")
    if suffix in (".sh",):
        return _hash_comment_blocks(text, path, "comment")
    if suffix == ".js":
        body = _blank(text, _JS_BLOCK_COMMENT_RE)
        units = _hash_comment_blocks(body, path, "comment", marker="//")
        units += [ProseUnit(path, 1, "block-comment", m.group(0))
                  for m in _JS_BLOCK_COMMENT_RE.finditer(text)]
        return units
    if suffix == ".tex":
        return (_hash_comment_blocks(text, path, "comment", marker="%")
                + _paragraphs(_blank(text, re.compile(r"^%.*$", re.MULTILINE)),
                              path, "paragraph"))
    if suffix == ".html":
        units = [ProseUnit(path, text[:m.start()].count("\n") + 1,
                           "html-comment", m.group(0))
                 for m in _HTML_COMMENT_RE.finditer(text)]
        body = _blank(text, _SCRIPT_RE)
        body = _blank(body, _HTML_COMMENT_RE)
        body = _blank(body, _TAG_RE)
        return units + _paragraphs(body, path, "page-text")
    return _paragraphs(text, path, "paragraph")


# --------------------------------------------------------------------------
# Classification
# --------------------------------------------------------------------------
_QUOTE_SPANS = (
    re.compile(r"`{1,3}[^`]*`{1,3}", re.DOTALL),
    re.compile(r'"[^"\n]{0,400}"'),
    re.compile(r"[“”][^“”\n]{0,400}[“”]"),
    re.compile(r"«[^»\n]{0,400}»"),
)
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?:;])\s+")


def _flat(text: str) -> str:
    """Lower-cased, whitespace-collapsed, space-padded, for marker matching.

    A marker list matched against raw text is defeated by a line break, which
    is how a reflowed rule sentence read as an unbacked claim in this module's
    own first corpus run.
    """
    return " " + " ".join(text.lower().split()) + " "


def _quote_ranges(text: str) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    for pat in _QUOTE_SPANS:
        ranges.extend((m.start(), m.end()) for m in pat.finditer(text))
    # a blockquote or a markdown quote line is a quotation of its whole line
    pos = 0
    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith(">"):
            ranges.append((pos, pos + len(line)))
        pos += len(line)
    return ranges


def _sentence_around(text: str, index: int) -> tuple[str, int, int]:
    start = 0
    for piece in _SENTENCE_SPLIT.split(text):
        end = start + len(piece)
        if start <= index < end + 1:
            return piece, start, end
        start = text.find(piece, start) + len(piece)
        while start < len(text) and text[start].isspace():
            start += 1
    return text, 0, len(text)


def known_test_names(root: Path | None = None) -> set[str]:
    """Every test function and test class defined in the tracked corpus.

    Derived from `git ls-files`, not from a list of test files: a suite nobody
    has named must still be able to back a claim.
    """
    root = root or REPO
    proc = subprocess.run(["git", "-C", str(root), "ls-files", "-z"],
                          capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return set()
    names: set[str] = set()
    for rel in proc.stdout.split("\0"):
        if not rel.endswith(".py"):
            continue
        if "test" not in Path(rel).name and "/tests/" not in rel:
            continue
        try:
            body = (root / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        names.update(m.group(1) for m in
                     re.finditer(r"^\s*def\s+(test_\w+)", body, re.MULTILINE))
        names.update(m.group(1) for m in
                     re.finditer(r"^\s*class\s+(\w*Tests?)\b", body,
                                 re.MULTILINE))
    return names


def _named_checks(unit_text: str, known: set[str] | None,
                  tracked: set[str] | None) -> tuple[list[str], list[str]]:
    """(checks that resolve, checks that were named and do not resolve)."""
    resolved: list[str] = []
    dangling: list[str] = []
    for name in set(TEST_NAME_RE.findall(unit_text)) | set(
            TEST_CLASS_RE.findall(unit_text)):
        if known is None or name in known:
            resolved.append(name)
        else:
            dangling.append(name)
    for path, func in FILE_FUNC_RE.findall(unit_text):
        if tracked is None or path in tracked or (REPO / path).exists():
            resolved.append(f"{path}:{func}")
        else:
            dangling.append(f"{path}:{func}")
    if COMMAND_RE.search(unit_text):
        resolved.append("<command>")
    return sorted(resolved), sorted(dangling)


def _gate(unit_text: str, m: re.Match, family: str, suffix: str,
          sentence: str) -> tuple[str, str] | None:
    """Reject occurrences that are not claims about a population, or None.

    Four rejections, in order, each one costed in the labelled sample rather
    than asserted to be safe:
      CODE_TOKEN         a Python/JS literal or an identifier, not prose.
      IDIOM              `at all`, `every other`, and their kin.
      BOUNDED            `all three cases` -- an enumerable set, out of scope.
      NOT_A_PREDICATION  a quantifier inside an instruction rather than a
                         claim: `reverse every face's winding`.
    Evidence: `test_each_gate_rejects_and_a_positive_control_survives_it`.
    """
    token = m.group(0)
    before = unit_text[max(0, m.start() - 1):m.start()]
    after = unit_text[m.end():m.end() + 1]
    if suffix in CODE_SUFFIXES and token in ("None", "All", "Every"):
        if token == "None":
            return CODE_TOKEN, "capitalised `None` in a code surface"
    if before == "." or after in ("(", "_", "="):
        return CODE_TOKEN, "identifier or call syntax, not prose"
    low = _flat(sentence)
    around = _flat(unit_text[max(0, m.start() - 14):m.end() + 14])
    for idiom in IDIOMS:
        if idiom in around:
            return IDIOM, f"fixed idiom {idiom!r}"
    if family in QUANTIFIER_FAMILIES:
        bounded = _BOUNDED_RE.search(
            " ".join(unit_text[max(0, m.start() - 2):m.end() + 40].split()))
        if bounded:
            return BOUNDED, "quantifies over an enumerated, countable set"
        flat_token = _flat(token).strip()
        tail = low.split(flat_token, 1)[1] if flat_token in low else ""
        if not _PREDICATION_RE.search(tail):
            return NOT_A_PREDICATION, ("quantifier inside an instruction or a "
                                       "noun phrase, with nothing predicated "
                                       "of it")
    return None


def classify_unit(unit_text: str, suffix: str = ".md",
                  *, path: str = "<text>", lineno: int = 1,
                  kind: str = "paragraph",
                  known_tests: set[str] | None = None,
                  tracked_paths: set[str] | None = None,
                  families: Sequence[str] | None = None) -> list[Claim]:
    """Every absolute in one prose unit, each with its verdict.

    This is the single classification entry point: the file pipeline and the
    hand-labelled sample both go through it, so a rate measured on the sample
    is a rate measured on the same code that swept the corpus.
    Evidence: `test_the_sample_replays_through_the_same_entry_point`.
    """
    resolved, dangling = _named_checks(unit_text, known_tests, tracked_paths)
    quotes = _quote_ranges(unit_text)
    blast, blast_words = blast_radius(path, suffix, kind)
    wanted = list(families) if families else list(ABSOLUTE_FAMILIES)
    seen: set[int] = set()
    claims: list[Claim] = []
    for family in wanted:
        for m in _FAMILY_RE[family].finditer(unit_text):
            if m.start() in seen:
                continue
            seen.add(m.start())
            sentence, s_start, s_end = _sentence_around(unit_text, m.start())
            # WHITESPACE IS COLLAPSED BEFORE ANY MARKER IS MATCHED. Without
            # this, `must\nnever shorten` carries no ` must ` and a reflowed
            # rule sentence was classified UNBACKED -- found by executing this
            # module against the corpus, not by reading it, and it is the same
            # reflow defect the rank guard records three times.
            # Evidence: `test_a_reflowed_rule_is_still_a_rule`.
            window = _flat(unit_text[max(0, m.start() - 160):m.end() + 160])
            low_sentence = _flat(sentence)
            gate = _gate(unit_text, m, family, suffix, sentence)
            if gate is not None:
                verdict, reason = gate
            elif any(a <= m.start() < b for a, b in quotes):
                verdict, reason = QUOTED, "keyword inside a quotation span"
            # DANGLING IS ASKED BEFORE RESOLVED, AND A MIXED UNIT IS
            # `CITES_MISSING_CHECK`. Until 2026-08-11 these two branches were
            # the other way round, and the consequence was not a rounding
            # error: run on itself the module reported BACKED 15 and
            # CITES_MISSING_CHECK 0 while citing thirteen tests that existed
            # nowhere in the repo or its history, because ONE runnable command
            # in the same docstring laundered every one of them. The choice
            # being made here is that ANY dangling name condemns the unit even
            # when a sibling citation resolves, and the argument is about the
            # reader rather than about the arithmetic: a reader who checks one
            # of five citations and finds it good does not check the other
            # four, so a unit with four fictional names and one real one
            # misleads him MORE than a unit with no citation at all. The
            # alternative rule -- "one resolving name is enough, report the
            # dangling ones as a note" -- was rejected because a note is not a
            # verdict and nothing downstream counts it. The cost is stated
            # rather than hidden: this is strictly the more severe rule, so a
            # unit that cites a real test beside a typo is a defect here, and
            # the reason string names both sides so that call is reviewable.
            # Evidence: `test_a_dangling_name_beside_a_runnable_command_still_fires`,
            # `test_a_dangling_name_beside_a_resolving_test_still_fires`,
            # and the must-not-match control
            # `test_a_unit_whose_every_citation_resolves_is_not_flagged`.
            elif dangling:
                verdict = CITES_MISSING_CHECK
                reason = ("names a check that does not resolve: "
                          + ", ".join(dangling[:4]))
                if resolved:
                    reason += (f" (mixed unit: {len(resolved)} other citation"
                               f"(s) here do resolve, and that does not "
                               f"rescue it)")
            elif resolved:
                verdict = BACKED
                reason = "named beside it: " + ", ".join(resolved[:4])
            elif any(mk in window for mk in HEDGE_MARKERS):
                verdict, reason = HEDGED, "retraction/attribution marker nearby"
            elif (RULE_OPENERS.match(sentence)
                  or any(mk in low_sentence for mk in RULE_MARKERS)):
                verdict, reason = RULE, "normative sentence, not descriptive"
            elif any(mk in window for mk in DEFINITIONAL_MARKERS):
                verdict, reason = DEFINITIONAL, "definitional marker nearby"
            else:
                verdict, reason = UNBACKED, "no executed check named in the unit"
            line_offset = unit_text[:m.start()].count("\n")
            claims.append(Claim(
                path=path, lineno=lineno + line_offset, kind=kind,
                family=family, keyword=m.group(0),
                sentence=" ".join(sentence.split()),
                verdict=verdict, reason=reason,
                blast=blast, blast_words=blast_words))
    return claims


# --------------------------------------------------------------------------
# Blast radius: what is built ON the claim
# --------------------------------------------------------------------------
_RULE_SURFACE_RE = re.compile(
    r"(?:^|/)(?:CLAUDE\.md|LESSONS\.md|DOCKET\.md|.*CHARTER.*|.*STANDARD.*|"
    r"docs/charters/.*|docs/standards/.*|.*_RULES.*|.*DOCTRINE.*)$")
_SHIPPING_RE = re.compile(r"^(?:demo-output/website/|.*/latex/|.*\.tex$)")


def blast_radius(path: str, suffix: str, kind: str) -> tuple[int, str]:
    """How much is built on the claim, scored from the surface it sits on.

    An absolute a RULE or a piece of CODE stands on outranks one in a narrative
    paragraph, because the downstream artefact inherits the error. Scored, not
    ranked by feel: code +3, rule surface +3, shipping surface +1.
    Evidence: `test_code_and_rule_surfaces_outrank_narrative`.
    """
    score = 0
    words: list[str] = []
    if suffix in (".py", ".sh", ".js"):
        score += 3
        words.append("executable source")
    if _RULE_SURFACE_RE.search(path) or "/charters/" in path:
        score += 3
        words.append("rule surface")
    if _SHIPPING_RE.match(path) or suffix == ".html":
        score += 1
        words.append("ships/travels")
    if not words:
        words.append("narrative")
    return score, ", ".join(words)


# --------------------------------------------------------------------------
# The audit
# --------------------------------------------------------------------------

@dataclass
class Skips:
    binary: int = 0
    over_size_cap: int = 0
    unreadable: int = 0
    unparsed: int = 0
    not_a_regular_file: int = 0
    #: Caller-named paths that do not exist. BLINDING -- see `blinding`.
    missing: int = 0
    #: Caller-named paths that exist but carry no prose suffix. NOT blinding.
    out_of_frame: int = 0
    unreadable_paths: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return (self.binary + self.over_size_cap + self.unreadable
                + self.unparsed + self.not_a_regular_file
                + self.missing + self.out_of_frame)

    @property
    def blinding(self) -> int:
        """Skips that make the verdict UNKNOWN rather than merely narrower.

        `missing` is here and `out_of_frame` is not, and the line between them
        is the whole repair: EXISTENCE is the caller's contract -- a path
        handed to `--paths` asserts "this is the thing to audit", so one that
        does not resolve means the checker never read the subject and cannot
        call it clean. The prose-SUFFIX filter is this module's OWN frame, and
        narrowing a sweep by a rule the module publishes is not blindness.
        Evidence: `test_a_caller_named_path_that_does_not_exist_yields_unknown_not_pass`
        and its must-not-match control
        `test_an_existing_file_outside_the_prose_frame_is_narrower_not_blinder`.
        """
        return self.unreadable + self.unparsed + self.missing

    def words(self) -> str:
        return (f"{self.binary} binary, {self.over_size_cap} over size cap, "
                f"{self.unreadable} unreadable (raised), "
                f"{self.unparsed} unparseable, "
                f"{self.not_a_regular_file} not a regular file, "
                f"{self.missing} named but missing (raised), "
                f"{self.out_of_frame} named but outside the prose frame")


@dataclass
class AuditResult:
    root: str
    commit: str
    dirty: bool
    frame_name: str
    rule_words: str
    filter_words: str
    suffixes: tuple[str, ...]
    families: tuple[str, ...]
    considered: int
    in_frame: int
    read: int
    units: int
    skips: Skips
    claims: list[Claim]
    walk_error: str | None

    @property
    def verdict(self) -> str:
        if self.walk_error is not None or self.skips.blinding:
            return "UNKNOWN"
        return "FLAGGED" if self.defects else "CLEAN"

    @property
    def defects(self) -> list[Claim]:
        return [c for c in self.claims if c.is_defect]

    def by_class(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for c in self.claims:
            out[c.verdict] = out.get(c.verdict, 0) + 1
        return dict(sorted(out.items(), key=lambda kv: -kv[1]))

    def by_family(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for c in self.defects:
            out[c.family] = out.get(c.family, 0) + 1
        return dict(sorted(out.items(), key=lambda kv: -kv[1]))

    def ranked(self) -> list[Claim]:
        return sorted(self.defects,
                      key=lambda c: (-c.blast, c.path, c.lineno))

    def frame_block(self) -> str:
        return "\n".join([
            "FRAME",
            f"  root            : {self.root}",
            f"  commit          : {self.commit}"
            + (" +uncommitted changes" if self.dirty else ""),
            f"  frame           : {self.frame_name}",
            f"  selection rule  : {self.rule_words}",
            f"  filter applied  : {self.filter_words}",
            f"  suffixes        : {', '.join(self.suffixes)}",
            f"  families        : {', '.join(self.families)}",
            f"  files considered: {self.considered}",
            f"  files in frame  : {self.in_frame}",
            f"  files read      : {self.read}",
            f"  prose units     : {self.units}",
            f"  files skipped   : {self.skips.total} ({self.skips.words()})",
        ] + ([f"  walk error      : {self.walk_error}"]
             if self.walk_error else [])
          + ([f"  unreadable      : "
              + ", ".join(self.skips.unreadable_paths[:10])
              + (" ..." if len(self.skips.unreadable_paths) > 10 else "")]
             if self.skips.unreadable_paths else []))

    def verdict_line(self) -> str:
        base = (f"{self.verdict}: {len(self.defects)} unbacked absolute(s) in "
                f"{len({c.path for c in self.defects})} file(s), from "
                f"{len(self.claims)} absolute(s) found in {self.units} prose "
                f"unit(s) across {self.read} of {self.in_frame} in-frame files, "
                f"at {self.commit}{'+dirty' if self.dirty else ''}")
        if self.verdict == "UNKNOWN":
            # Every blinding reason is named here. A verdict line that reports
            # UNKNOWN while its stated cause reads `0 ... and 0 ...` sends the
            # reader looking for a failure the sentence has already hidden.
            why = self.walk_error or (
                f"{self.skips.unreadable} file(s) raised on read, "
                f"{self.skips.unparsed} would not parse and "
                f"{self.skips.missing} named path(s) do not exist")
            base += f"; UNKNOWN because {why}"
        return base

    def report(self, top: int = 40) -> str:
        out = [self.frame_block(), "", self.verdict_line(), "",
               "verdict counts  : " + ", ".join(
                   f"{k}={v}" for k, v in self.by_class().items()),
               "defects by family: " + ", ".join(
                   f"{k}={v}" for k, v in self.by_family().items()) or "none"]
        ranked = self.ranked()
        if ranked:
            out += ["", f"TOP {min(top, len(ranked))} BY BLAST RADIUS"]
            out += [f"  {c.line()}" for c in ranked[:top]]
            if len(ranked) > top:
                out.append(f"  ... {len(ranked) - top} further")
        return "\n".join(out)


def _head_commit(root: Path) -> tuple[str, bool]:
    def git(*a):
        return subprocess.run(["git", "-C", str(root), *a],
                              capture_output=True, text=True, check=False)
    proc = git("rev-parse", "--short", "HEAD")
    if proc.returncode != 0:
        return ("no-git", False)
    return (proc.stdout.strip(), bool(git("status", "--porcelain").stdout.strip()))


def audit(root: str | os.PathLike = REPO,
          frame: str = "tracked",
          *,
          paths: Iterable[str] | None = None,
          suffixes: Sequence[str] | None = None,
          families: Sequence[str] | None = None,
          size_cap: int | None = DEFAULT_SIZE_CAP,
          known_tests: set[str] | None = None) -> AuditResult:
    """Sweep a frame for absolute claims and report what backs each one."""
    rootp = Path(root).resolve()
    commit, dirty = _head_commit(rootp)
    suffixes = tuple(suffixes or PROSE_SUFFIXES)
    families = tuple(families or ABSOLUTE_FAMILIES)
    skips = Skips()
    claims: list[Claim] = []
    walk_error: str | None = None
    considered = 0
    unit_count = 0
    read = 0

    if paths is not None:
        selected = [rootp / p for p in paths]
        frame_name = "explicit-paths"
        rule_words = "paths named by the caller"
        filter_words = "none beyond the caller's list -- NOT a derived frame"
        # THE FAIL-OPEN THIS BRANCH USED TO CARRY, fixed rather than noted.
        # `in_frame` below filters on SUFFIX, and it used to do so before
        # anything was stat-ed. A caller-named path that did not exist was
        # therefore dropped without a trace unless its suffix happened to be
        # a prose one -- a missing `.md` raised FileNotFoundError and blinded
        # the verdict correctly, while a missing `.json`, `.png` or
        # extensionless path vanished and the audit returned CLEAN, exit 0,
        # PASS. Which of the two happened turned on the SPELLING of the
        # filename. A checker that reads nothing and reports PASS is counted
        # as coverage while guarding nothing, so the missing path is now
        # counted here, before the suffix filter can hide it, and it BLINDS.
        for p in selected:
            if not p.exists():
                skips.missing += 1
                skips.unreadable_paths.append(f"{p} (named but does not exist)")
            elif p.suffix not in suffixes:
                skips.out_of_frame += 1
    else:
        f = sweep_mod.FRAMES[frame]
        frame_name, rule_words = f.name, f.rule_words
        filter_words = f.filter_words + "; then filtered to prose suffixes"
        try:
            selected = sweep_mod.select_files(f, rootp)
        except Exception as exc:
            selected = []
            walk_error = f"{type(exc).__name__}: {exc}"

    considered = len(selected)
    in_frame = [p for p in selected if p.suffix in suffixes]
    if known_tests is None:
        known_tests = known_test_names(rootp)
    tracked_paths = {str(p.relative_to(rootp)) for p in selected
                     if _is_relative(p, rootp)}

    for path in in_frame:
        try:
            st = os.stat(path)
            if size_cap is not None and st.st_size > size_cap:
                skips.over_size_cap += 1
                continue
            raw = path.read_bytes()
        except (OSError, ValueError) as exc:
            skips.unreadable += 1
            skips.unreadable_paths.append(f"{path} ({type(exc).__name__})")
            continue
        if b"\x00" in raw[:8192]:
            skips.binary += 1
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("latin-1")
        rel = str(path.relative_to(rootp)) if _is_relative(path, rootp) else str(path)
        try:
            units = extract_units(text, path.suffix, rel)
        except Exception as exc:
            skips.unparsed += 1
            skips.unreadable_paths.append(f"{rel} ({type(exc).__name__}: {exc})")
            continue
        read += 1
        unit_count += len(units)
        for unit in units:
            claims.extend(classify_unit(
                unit.text, path.suffix, path=unit.path, lineno=unit.lineno,
                kind=unit.kind, known_tests=known_tests,
                tracked_paths=tracked_paths, families=families))

    return AuditResult(
        root=str(rootp), commit=commit, dirty=dirty, frame_name=frame_name,
        rule_words=rule_words, filter_words=filter_words, suffixes=suffixes,
        families=families, considered=considered, in_frame=len(in_frame),
        read=read, units=unit_count, skips=skips, claims=claims,
        walk_error=walk_error)


def _is_relative(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


# --------------------------------------------------------------------------
# The measured false-positive rate
# --------------------------------------------------------------------------

def measure_against_sample(sample_path: Path | None = None,
                           known_tests: set[str] | None = None) -> dict:
    """Replay the hand-labelled sample through `classify_unit` and score it.

    A record labelled `legitimate` that the checker calls a defect is a FALSE
    POSITIVE. A record labelled `needs-backing` that the checker exempts is a
    FALSE NEGATIVE. Both are reported, because a checker tuned only against
    the first becomes a checker that finds nothing.

    The sample is drawn from the corpus sweep itself, which is why the rate it
    yields is a rate over the checker's own output rather than over prose in
    general -- stated here because that distinction is the whole meaning of the
    number.

    That last sentence carried a citation -- a name promising a test that the
    sample was drawn from this checker's own output -- and on 2026-08-11 it was
    STRUCK rather than written. The name is not repeated here even as a corpse,
    because by this module's own rule a name resolving to nothing reads as
    backing to every human who sees it. What that name promised would have had
    to re-perform a past act: the draw happened at commit `8ebe2b8e`, and
    repeating it needs the corpus sweep that is out of this rung's scope. The
    fixture's `drawn_at_commit`, `frame` and per-record `stratum` fields are
    the sample's own testimony about its provenance, and a test asserting those
    fields are present checks that the testimony exists, not that it is true.
    Such a test is written, in this module's suite under `sdk/tests/`, and it
    is deliberately NOT named here: this module backs claims at unit level, so
    a name anywhere in this docstring would read as backing for the sentence
    above, which it does not back. That is the citation shape this module was
    built to catch, so it is not left standing over its own measurement.
    """
    path = Path(sample_path or SAMPLE_PATH)
    data = json.loads(path.read_text(encoding="utf-8"))
    records = data["records"]
    if known_tests is None:
        known_tests = known_test_names()
    tp = fp = tn = fn = 0
    disagreements: list[dict] = []
    for rec in records:
        got = classify_unit(rec["unit_text"], rec.get("suffix", ".md"),
                            path=rec.get("path", "<sample>"),
                            kind=rec.get("kind", "paragraph"),
                            known_tests=known_tests)
        target = [c for c in got
                  if c.family == rec["family"]
                  and rec["keyword"].lower() in c.keyword.lower()]
        flagged = any(c.is_defect for c in target)
        label = rec["label"]
        if label == "needs-backing":
            if flagged:
                tp += 1
            else:
                fn += 1
                disagreements.append({"id": rec["id"], "kind": "false-negative",
                                      "verdict": [c.verdict for c in target]})
        else:
            if flagged:
                fp += 1
                disagreements.append({"id": rec["id"], "kind": "false-positive",
                                      "verdict": [c.verdict for c in target]})
            else:
                tn += 1
    flagged_total = tp + fp
    return {
        "sample_path": str(path),
        "n": len(records),
        "true_positive": tp, "false_positive": fp,
        "true_negative": tn, "false_negative": fn,
        "flagged": flagged_total,
        "false_positive_rate_over_flagged":
            (fp / flagged_total) if flagged_total else None,
        "false_negative_rate_over_needs_backing":
            (fn / (tp + fn)) if (tp + fn) else None,
        "disagreements": disagreements,
        "sample_commit": data.get("drawn_at_commit"),
        "sample_frame": data.get("frame"),
    }


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="check_absolutes",
        description="Find absolute claims and report what executed check is "
                    "named beside each one.")
    p.add_argument("--frame", default="tracked",
                   choices=sorted(sweep_mod.FRAMES),
                   help="file selection rule; derived, never enumerated")
    p.add_argument("--root", default=str(REPO))
    p.add_argument("--paths", nargs="+", default=None,
                   help="explicit paths instead of a derived frame; the frame "
                        "block says so when you use this")
    p.add_argument("--suffix", action="append", default=None,
                   help="restrict the prose-suffix filter; repeatable")
    p.add_argument("--families", nargs="+", default=None,
                   choices=sorted(ABSOLUTE_FAMILIES))
    p.add_argument("--top", type=int, default=40)
    p.add_argument("--json", action="store_true")
    p.add_argument("--measure-sample", action="store_true",
                   help="replay the hand-labelled sample and print the rates")
    p.add_argument("--list-surfaces", action="store_true")
    return p


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.list_surfaces:
        for suffix, how in sorted(PROSE_SUFFIXES.items()):
            print(f"{suffix:8s} {how}")
        return 0
    if args.measure_sample:
        print(json.dumps(measure_against_sample(), indent=2))
        return 0
    res = audit(root=args.root, frame=args.frame, paths=args.paths,
                suffixes=args.suffix, families=args.families)
    if args.json:
        print(json.dumps({
            "frame": res.frame_block(), "verdict": res.verdict,
            "verdict_line": res.verdict_line(),
            "by_class": res.by_class(), "by_family": res.by_family(),
            "defects": [c.__dict__ for c in res.ranked()],
        }, indent=2))
    else:
        print(res.report(top=args.top))
    return {"CLEAN": 0, "FLAGGED": 1, "UNKNOWN": 3}[res.verdict]


if __name__ == "__main__":
    raise SystemExit(main())
