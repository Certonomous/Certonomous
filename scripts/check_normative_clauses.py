#!/usr/bin/env python3
"""NORMATIVE-CLAUSE CHECK. Grades DIRECTIVES, not assertions.

WHY THIS EXISTS (docket D119, from D114/D116/D117)
==================================================
Every check in this lab grades an assertion: *is this sentence true?*  None
grades a directive: *does this rule, if obeyed, produce a true sentence?*

That gap has a measured cost. `CLOSURE_FAMILY_SUPERVISION_GUIDELINES.md` §4
clause (b) was a MANDATORY rule telling every claim-bearing surface to state the
seed bound as *comparable to* the margin, and it named one specific existing
sentence as *"the reference wording"*. Both halves were computed against the
FOUR-entry board. Against the six-entry board retrieved 2026-08-11T23:33Z the
bound is 177% of the margin, not comparable to it. The clause was repaired five
times *in its copies* and the copies kept coming back, because the clause is a
CLAIM GENERATOR: it manufactures new copies faster than a sweep removes them.
Its own §4(e) had already recorded it as an understatement and left it standing
and binding, which is the whole shape of the defect -- an observation filed
beside a mandate loses to the mandate, because the mandate is what the next
author obeys.

A second instance of the same shape sits at `LADDER_V_V13_CLOSEOUT.md:216`,
under an instruction to *"hand over the number that proves you already knew"*.

WHAT IT CHECKS -- three rules, and what each one is for
======================================================
  W1  MANDATED WORDING.  A directive that designates a fixed SENTENCE as the
      thing to copy (`X is the reference wording`, `the wording to copy`, `hand
      over the number that proves ...`). A designated sentence is a claim
      generator with its arithmetic hidden inside a pointer, and no arithmetic
      instrument in this lab can follow the pointer. Graded FALSE when the
      designated wording is quoted inline and its figures disagree with the
      records; UNDECIDABLE when the designation is a CROSS-DOCUMENT POINTER,
      which is the common case and the honest verdict.

  W2  MANDATED FIGURE.  A directive that pins a LITERAL figure to one of the
      registered claim quantities (the margin, the seed bound, the overall,
      P(rank 1)). Graded against the same machine records
      `check_derived_figures` derives from. This is the rule that fires on
      clause (b): `the 0.0029 rank-1 margin` inside `Rank 1 is never stated
      without ...`.

  W3  MANDATED QUALITATIVE RELATION.  A directive that pins a quantity to a
      COMPARATIVE with no numeral in it (`comparable to its margin`,
      `of comparable size`). Always UNDECIDABLE, never PASS, never FAIL:
      an arithmetic predicate has nothing to grade here, and after five passes
      removed the literal `84%` this is the claim's main remaining vector
      (D116, D117). Reporting these as UNDECIDABLE-with-reason is the point of
      the rule; a checker that silently returned PASS over them is what
      happened for five passes.

WHY IT IS ANCHORED TO A QUANTITY REGISTRY, AND THE MEASUREMENT THAT DECIDED IT
=============================================================================
An unanchored version was built first and MEASURED before being rejected. Rule:
*any markdown block carrying a mandate marker, and any decimal or percentage
inside it that is not a threshold and not a date.* Over the 404 prose files this
check opened AT THAT TIME it returned **561 hits in 95 files**, and inspection of the head and
tail of that list found essentially none of them normative-figure defects: they
were dated result tables inside a paragraph that happened to also contain the
word `must`, checklist rows, `control_room.html` JavaScript, and literature
readings. Co-occurrence in a block is not a syntactic link, and a 561-hit list
is not a check. This lab already ships one instrument with a 74% false-positive
rate (`check_absolutes.py`) and the measured cost of that is that readers ignore
it, so the unanchored sweep's MEASUREMENT is recorded here instead of shipped.

WHAT THIS BUYS OVER `check_derived_figures.py`, MEASURED
========================================================
It is not a widening of that check. Nothing in it is modified; `mask_exempt` is
imported and reused, and so is its quantity registry, because two maskers and
two registries would drift.

  * Its `live_margin` anchors ALL REQUIRE THE WORD `Yang`. A clause that pins
    the SUPERSEDED margin never names Yang -- by construction, since Yang was
    not on the board it was computed against. So `the 0.0029 rank-1 margin`
    inside clause (b) is invisible to R1 and visible here. Verified as a
    control on this invocation (POS-2).
  * R3's coverage idiom needs a percentage. W3 fires on the numberless form,
    which is the form that survived five passes.
  * Nothing there reads a POINTER to a wording (W1). `closure.html`'s stability
    note is the reference wording` is not a figure at all.

A CLAUSE THAT MANDATES A PROCEDURE IS NOT A DEFECT
==================================================
`every figure must carry its board` is a good rule. `every figure must say 84%`
is a claim generator. The discriminator implemented here is not a word list, it
is the OBJECT of the mandate: W2 requires a LITERAL figure bound to a registered
quantity NAME inside the mandate's own clause. A mandate whose object is a KIND
(`its board`, `its interval`, `a triple`, `where it came from`) carries no
literal and cannot fire. NEG-1 and NEG-6 are that discriminator under test on
every run: the repaired clause (b-1) mandates the margin triple and MUST NOT
fault, and the third prohibition of §4(e) (`no surface may state the figure
without its BOARD`) MUST NOT fault.

READING ONLY UNSTRUCK TEXT
==========================
`check_derived_figures.mask_exempt` is imported and used unmodified. That corpus
has 252 strike spans, 69 of them multi-line and 8 crossing blockquote
continuations, so a line-by-line masker is wrong and two authors' first cuts
were. A struck clause is a legitimate historical record; flagging one is a false
positive, and here a false positive is WORSE THAN A MISS because it trains
readers to ignore the check. NEG-2 is a correctly struck copy of the very clause
POS-2 fires on.

THREE-VALUED, AND IT NEVER PASSES FROM AN EMPTY SET
===================================================
THE EMPTY SET IS THE SET THAT WAS DECIDED, NOT THE SET THAT WAS LOOKED AT. Zero
clauses DECIDED is UNKNOWN with a reason, not PASS (defect class B1) -- and the
reason names which of three ways the run got there: EMPTY-1 no clause matched at
all, EMPTY-2 clauses matched but none was gradeable, EMPTY-3 a source could not
be read so the emptiness is unattributable. Both numbers, examined and decided,
are printed in the DECISION SET block above the verdict.

This paragraph used to be true only of `examined`, and the check shipped a PASS
over 887 examined and 0 decided (LADDER_V_V15_ROUND8 F1, 2026-08-15). The guard
now gates on the DECIDED set: the findings, PLUS the clauses graded and found
compliant. That second half is not decoration. A compliant clause is silent by
design (control NEG-6), so a guard that counted findings alone would return
UNKNOWN on a PERFECT corpus and PASS only while defects remained -- an
instrument that punishes repair, which is the failure mode on the other side of
B1. `scan` collects them into `cleared` and the DECISION SET block prints the
count. An unreadable source record is UNKNOWN, and so is a misfired control.
stderr is not swallowed: `git ls-files`'s stderr is captured and PRINTED in the
frame, and a non-zero return code is UNKNOWN rather than an empty file list.

WHAT IT IS BLIND TO
===================
Printed on every run, above the verdict, because an unstated blind spot is the
same defect as a silent skip.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import re
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

# Reused, never reimplemented: one masker and one registry, or they drift.
from check_derived_figures import (          # noqa: E402
    mask_exempt, read_sources, build_registry, agrees, written_digits,
)

PASS, FAIL, UNKNOWN = "PASS", "FAIL", "UNKNOWN"
EXIT = {PASS: 0, FAIL: 1, UNKNOWN: 3}

#: THE FRAME MOVED, 2026-08-16, measured at HEAD `faa02f80`. Stated rather
#: than swapped, because a frame count is quoted by other documents and a
#: silent change strands every one of them. BOTH SIDES OF THE PAIR BELOW ARE
#: ANCHORED: the tracked corpus itself grows several files an hour here, so
#: the live count moved again (481/429) while this note was being written.
#: An unanchored frame count in this lab is stale within the hour; that is a
#: property of the corpus, not of this change.
#: `*.tex` was ADDED here; every figure in this docstring above predates
#: that and is left at the value it was measured at.
#:
#:      before  478 considered / 426 opened /  974 clauses   (globs md, html)
#:      after   480 considered / 428 opened / 1011 clauses   (globs md, html, tex)
#:      cost    0 new faults, 0 new UNDECIDABLE; verdict PASS both sides
#:
#: The 1011 was measured BEFORE this note existed. Writing it moved the live
#: count to 1013, because this check reads its own source and these lines carry
#: mandate markers. The measured value is left at 1011 rather than restated: a
#: count edited to match a later run is no longer a measurement, and the two
#: extra clauses are this comment.
#:
#: WHY, and why only `*.tex`. Both standing instruments globbed `*.md`/`*.html`
#: only, so the two tracked `.tex` files had never been opened by anything -- a
#: silent zero at the level of the corpus definition rather than of a sweep.
#: Adding `*.pdf` was measured at the same time and REJECTED: it cost 0 new
#: faults too, and the widened check then returned PASS on
#: `demo-output/website/latex/closure_challenge_report.pdf`, an artifact
#: carrying `rank 1 of 5` and `P(rank 1) = 68%` five days after its own source
#: was repaired. This check grades DIRECTIVES; a withdrawn ordinal is not one,
#: so the wider glob would have shipped a green frame over the defect that
#: motivated widening it -- worse than the gap, because a gap is visible and a
#: green frame is not. The PDF arm has its own instrument,
#: `scripts/check_pdf_surfaces.py`, which grades it on its own claim class.
PROSE_GLOBS = ("*.md", "*.html", "*.tex")
MAX_BYTES = 2_000_000

#: 53 of 57 tracked HTML files are DAFoam-generated OpenMDAO reports carrying
#: minified d3; they hold no prose. Excluded by path and COUNTED in the frame.
GENERATED_HTML = re.compile(r"/reports/.*\.html$")

#: This check reads its own source for the controls, so it must not grade
#: itself: the control fixtures below are, by construction, the exact strings it
#: is looking for. It is not a `*.md`/`*.html` file so the frame already
#: excludes it; this is belt and braces and it is stated rather than assumed.
SELF = Path(__file__).name


# ---------------------------------------------------------------------------
# The mandate marker, and the clause it governs
# ---------------------------------------------------------------------------

#: Modal vocabulary, enumerated FROM the corpus (git grep over the modal set the
#: brief names) rather than assumed. `required` alone is excluded: in this tree
#: it is overwhelmingly descriptive ("the required mesh", "as required by").
MANDATE = re.compile(
    # `\b` and not `\s+` after the modal: this corpus writes `**must**` with the
    # bold markers abutting the word, and an early cut of this pattern required
    # whitespace and silently matched none of them (POS-1 caught it).
    r"\b(?:"
    r"must\b(?:\s*\**\s*(?:not|never)\b)?"
    r"|shall\b(?:\s*\**\s*not\b)?"
    r"|may\s*\**\s*not\b|may\s*\**\s*never\b"
    r"|is\s+never\s+(?:stated|quoted|written)\s+without"
    r"|never\s+stated\s+without"
    r"|MANDATORY|is\s+mandatory|are\s+mandatory"
    r"|no\s+(?:document|surface|agent|act|record|figure|sentence|entry|page"
    r"|claim|check|script|run|reader|author)\s+may\b"
    r"|is\s+required\s+to\b|are\s+required\s+to\b"
    r"|is\s+prohibited\b|are\s+prohibited\b"
    r"|hand\s+over\s+the\b"
    r")", re.I)

#: A clause is bounded by a blank line, a heading, or the next list marker at
#: the same or shallower indent. Bounded, because an unbounded clause swallows
#: the dated record three paragraphs down and that is how the unanchored cut
#: reached 561 hits.
_ITEM = re.compile(r"^(?P<ind>[ \t]*)(?:[-*+]\s|\d+\.\s|#{1,6}\s)")
MAX_CLAUSE = 1600


def clause_at(live: str, lines: list[str], starts: list[int], li: int) -> tuple:
    """(start_offset, text) of the list item / paragraph containing line `li`."""
    def indent_of(i):
        m = _ITEM.match(lines[i])
        return len(m.group("ind")) if m else None

    top = li
    while top > 0:
        if not lines[top].strip():
            top += 1
            break
        if indent_of(top) is not None:
            break
        top -= 1
    own = indent_of(top)
    bot = top + 1
    while bot < len(lines):
        ln = lines[bot]
        if not ln.strip():
            break
        ind = indent_of(bot)
        if ind is not None and (own is None or ind <= own):
            break
        bot += 1
    start = starts[top]
    end = starts[bot] if bot < len(starts) else len(live)
    return start, live[start:min(end, start + MAX_CLAUSE)]


# ---------------------------------------------------------------------------
# The three rules
# ---------------------------------------------------------------------------

#: W1. A DESIGNATION of a fixed wording. Deliberately narrow: `verbatim` is NOT
#: here. Measured: `verbatim` matches 252 times in this corpus and is a CITATION
#: idiom ("quoted verbatim from the abstract"), not a mandate, so including it
#: would have made W1 a 252-hit false-positive engine on its own.
W1_RX = re.compile(
    r"(?:is|are|remains?)\s+the\s+reference\s+wording"
    r"|the\s+reference\s+wording\s+is"
    r"|the\s+wording\s+to\s+copy"
    r"|the\s+sentence\s+to\s+(?:use|copy|quote)"
    r"|the\s+standard\s+sentence\s+is"
    r"|copy\s+(?:the|this)\s+(?:sentence|wording)\s+(?:exactly|verbatim)"
    r"|hand\s+over\s+the\s+number\s+that\s+proves", re.I)

#: A cross-document pointer inside the designation: a backticked path, a §ref,
#: or a named note. When the designation points elsewhere the honest verdict is
#: UNDECIDABLE -- this check does not resolve pointers across documents.
W1_POINTER = re.compile(r"`[^`]+\.(?:html|md|json|py|tex)`|§\s*\d|\bnote\b"
                        r"|\bsentence\s+(?:above|below|at)\b", re.I)

#: W2/W3. The quantity NAMES this check can bind a literal to. Kept to the
#: registered claim family on purpose: this is the coverage statement, it is
#: printed on every run, and a normative clause about anything else is OUT OF
#: REACH rather than silently clean.
QNAME = {
    "live_margin": re.compile(
        r"\b(?:rank[- ]?1\s+margin|margin\s+over\s+the\s+(?:published\s+)?"
        r"leader|our\s+margin|the\s+margin)\b", re.I),
    "seed_bound": re.compile(
        r"\b(?:seed[- ](?:bound|uncertainty|spread)|truth[- ]free\s+bound"
        r"|seed[- ]spread\s+bound)\b", re.I),
    "ours_overall": re.compile(r"\bour\s+(?:overall|entry|score)\b", re.I),
    # `[^.]` and not `[^.\n]`: this corpus wraps `covers 84% of the\n margin`
    # and a newline-free class saw the one-line fixture and not the artifact.
    "coverage_pct": re.compile(r"\bcovers?\b[^.]{0,30}?\bmargin\b", re.I),
}

#: A bare literal. `(?<![\w.$§/-])` keeps §4.2, D114, v1.2, 2026-08-11 and
#: 0.056647191704213645-inside-a-path out.
LITERAL = re.compile(r"(?<![\w.$§/-])(?P<v>\d{1,3}(?:\.\d+)?\s*%|0\.\d{3,})"
                     r"(?![\w-])")

#: Thresholds are PROCEDURE, not claim: `at least 0.0030`, `0.0030 caps the
#: seed bound`, `must stay under 0.0030`. A gate figure is the good kind of
#: mandated number -- it is the rule, not a claim about the world -- so it must
#: never be a finding.
#:
#: UNANCHORED, and scanned on BOTH sides of the literal. An earlier cut anchored
#: this at `$` (immediately before the literal) and also carried the symbol
#: forms `[<>≤≥] + ±`. Two mutation rounds showed the symbols were dead code:
#: `_FILL` admits word characters only, so `≥` breaks the bind before any
#: threshold test runs, and the anchored form was subsumed. Both are gone rather
#: than kept as decoration -- a predicate that cannot fire is a predicate a
#: reader will believe is protecting them.
THRESH_WORD = re.compile(
    r"\b(?:at\s+least|at\s+most|no\s+more\s+than|no\s+less\s+than|within"
    r"|below|above|under|over|exceeds?|caps?|floors?|bounds?\s+the"
    r"|tolerance|threshold)\b", re.I)

#: The triple that clause (b-1) and the submission draft's binding rule mandate.
#: A figure carrying it is not a bare pinned figure, it is a properly qualified
#: one, and it must not fault. A COMMIT ANCHOR IS NOT ADMISSIBLE here, exactly
#: as those rules say: `deb91557` scores but does not rank.
ENTRANT = re.compile(r"\b(?:Yang|Reissmann|Wu\s*&?\s*Zhang|Liu|Montoya|Tian"
                     r"|Buchanan|Hickel|Dwight|Sandberg|Fang)\b")
BOARDCOUNT = re.compile(r"\b(?:four|six|seven|4|6|7)[- ]entry\b", re.I)
RETRIEVED = re.compile(r"\b20\d\d-\d\d-\d\d")

#: W3. A comparative with no numeral in it.
QUALITATIVE = re.compile(
    r"\bcomparable\s+(?:to|in\s+size|size|scale|in\s+magnitude)"
    r"|\bof\s+comparable\s+(?:size|scale|magnitude)"
    r"|\bsits?\s+inside\s+the\s+margin"
    r"|\b(?:about|roughly)\s+the\s+same\s+size"
    r"|\bon\s+the\s+order\s+of\s+the\s+margin", re.I)


#: How close a literal must sit to the quantity NAME to count as pinned to it.
#: This is the whole difference between a check and a 561-hit list. Measured:
#: at a +-90 character window the corpus returned six FALSE findings of which
#: five were co-occurrence inside one long checklist item (`PRODUCT_LIST.md:63`
#: bound `0.0580` to `the margin` across 40 words of unrelated prose). At a
#: bound of 18 characters of connective filler on either side, only a genuine
#: `<literal> <name>` / `<name> is <literal>` construction survives.
BIND = 18
_LIT = r"(?<![\w.$§/-])(?P<v>\d{1,3}(?:\.\d+)?\s*%|0\.\d{3,})(?![\w-])"

#: The filler between literal and name may contain WORDS ONLY -- no `,` `;` `)`
#: `(` `->` `|`. Every remaining false positive at the +-18 bound crossed a
#: punctuation boundary: `(Yang, 0.0580); our margin over Yang` bound Yang's
#: OVERALL to the word `margin` eighteen characters later, and
#: `(t = -0.495, dispersion 5x the margin` bound a t-statistic to it. Four
#: corpus findings, all four false, all four killed by this one restriction.
#: `\n` IS allowed in the filler and the omission was caught by a test, not by
#: reading: the in-memory control fixture held `the 0.0029 rank-1 margin` on one
#: line, the real file at `5bec65f0^` wraps it as `the 0.0029\n  rank-1 margin`,
#: and a newline-free filler saw the fixture and not the artifact. `mask_exempt`
#: preserves offsets and blanks blockquote prefixes, so a wrapped claim inside a
#: `> ` banner is spanned too. Punctuation is still refused, which is what keeps
#: the bind tight; the line break is not a clause boundary in this corpus.
_FILL = r"[\w \t\r\n*_-]{0," + str(BIND) + r"}"
_LEFT = re.compile(_LIT + _FILL + r"$")
_RIGHT = re.compile(r"^" + _FILL + r"?" + _LIT)


def _unit_ok(written: str, unit: str) -> bool:
    """A `%` literal may only bind to a `%` quantity, and vice versa.

    Measured, on the real corpus: without this the sentence *"the two inputs
    differ by 9x10^-6, about **0.3% of the margin**"* bound `0.3%` to
    `live_margin` and was graded FALSE against an ABSOLUTE margin of 0.001365.
    It is a ratio, correctly stated, inside a clause that happens to carry
    `must not`. One false positive out of one finding is a 100% false-positive
    rate, which is not a check.
    """
    return written.rstrip().endswith("%") == (unit == "%")


def bind_literal(clause: str, nm: re.Match, unit: str = ""):
    """(written, side) for a literal syntactically bound to the quantity name.

    INSIDE is `covers 84% of the margin`, where the idiom's own regex spans the
    figure. LEFT is `the 0.0029 rank-1 margin` / `0.0024 seed bound`. RIGHT is
    `the margin is 0.001365`. Thresholds (`>= 0.85`, `cap +0.010`) are
    procedure, not a claim, and are refused on every side.
    """
    for m in LITERAL.finditer(nm.group(0)):
        pre = nm.group(0)[max(0, m.start() - 24):m.start()]
        if not THRESH_WORD.search(pre) and _unit_ok(m.group("v"), unit):
            return m.group("v").replace(" ", ""), "inside"
    left = clause[max(0, nm.start() - (BIND + 12)):nm.start()]
    m = _LEFT.search(left)
    if m and _unit_ok(m.group("v"), unit):
        pre = left[max(0, m.start() - 24):m.start()]
        # The threshold word can sit on EITHER side of the literal in a
        # left-bound construction -- `at least 0.0030 for the margin` and
        # `0.0030 caps the seed bound` are both gates. Checking only the text
        # before the literal caught the first and missed the second.
        if not THRESH_WORD.search(pre) \
                and not THRESH_WORD.search(left[m.end("v"):]):
            return m.group("v").replace(" ", ""), "left"
    right = clause[nm.end():nm.end() + BIND + 12]
    m = _RIGHT.search(right)
    if m and _unit_ok(m.group("v"), unit):
        pre = right[:m.start("v")]
        if not THRESH_WORD.search(pre):
            return m.group("v").replace(" ", ""), "right"
    return None


@dataclasses.dataclass
class Clause:
    rule: str
    path: str
    line: int
    verdict: str
    quantity: str
    written: str
    why: str
    excerpt: str


def _excerpt(text: str, n: int = 170) -> str:
    return re.sub(r"\s+", " ", text).strip()[:n]


def grade_literal(q, written: str) -> tuple[str, str]:
    """(verdict, why) for a literal pinned to a registered quantity."""
    if q is None:
        return UNKNOWN, "quantity not in the registry -- out of reach"
    ok, note = q.verdict(written)
    if ok:
        return PASS, f"agrees with {note}"
    n = written_digits(written)
    over = [b for b in q.bases if n > b.digits]
    if over and len(over) == len(q.bases):
        return FAIL, (f"{n} significant digits written; the stated basis "
                      f"supports {max(b.digits for b in q.bases)} (D104)")
    return FAIL, (f"obeying this directive writes {written}; the records hold "
                  f"{note}")


def scan(live: str, rel: str, qs, out: list, cleared: list | None = None) -> int:
    """Append findings for one masked file. Returns clauses examined.

    `cleared`, if given, collects the clauses that were GRADED AND FOUND
    COMPLIANT -- a correct literal carrying its full board triple. Those are
    deliberately NOT findings (control NEG-6 pins that: reporting an obeyed
    mandate trains readers to ignore the check), but they ARE decisions, and a
    verdict that cannot see them has no positive evidence to rest on.
    """
    lines = live.split("\n")
    starts, pos = [], 0
    for ln in lines:
        starts.append(pos)
        pos += len(ln) + 1
    byqid = {q.qid: q for q in qs}

    seen: set[int] = set()
    examined = 0
    for m in MANDATE.finditer(live):
        li = live.count("\n", 0, m.start())
        start, clause = clause_at(live, lines, starts, li)
        if start in seen:
            continue
        seen.add(start)
        examined += 1
        base_line = live.count("\n", 0, start) + 1

        # --- W1 ---------------------------------------------------------
        for w in W1_RX.finditer(clause):
            tail = clause[w.start():w.start() + 260]
            head = clause[max(0, w.start() - 200):w.start()]
            if W1_POINTER.search(head) or W1_POINTER.search(tail):
                v, why = (UNKNOWN,
                          "the mandated wording is a CROSS-DOCUMENT POINTER; "
                          "this check does not resolve pointers, and no "
                          "arithmetic instrument in this lab follows one "
                          "either -- adjudicate by hand")
            else:
                v, why = (UNKNOWN,
                          "a fixed wording is designated but not quoted "
                          "inline; nothing here to grade arithmetically")
            out.append(Clause("W1", rel,
                              base_line + clause.count("\n", 0, w.start()),
                              v, "-", _excerpt(w.group(0), 60), why,
                              _excerpt(clause)))

        # --- W2 ---------------------------------------------------------
        for qid, rx in QNAME.items():
            for nm in rx.finditer(clause):
                q = byqid.get(qid)
                hit = bind_literal(clause, nm, q.unit if q else "")
                if hit is None:
                    continue
                written, side = hit
                has_triple = bool(ENTRANT.search(clause)
                                  and BOARDCOUNT.search(clause)
                                  and RETRIEVED.search(clause))
                v, why = grade_literal(q, written)
                if v == PASS and has_triple:
                    # THE TRIPLE, OBEYED. Not a FINDING -- NEG-6 is the control
                    # that says so and it must keep holding -- but it IS a
                    # DECISION, and it is now recorded as one.
                    #
                    # Until 2026-08-15 this was a bare `continue` and the
                    # clause vanished. That threw away this check's only
                    # positive evidence: a corpus in which every mandate is
                    # obeyed produced an EMPTY graded set, which is why the B1
                    # guard had to gate on `examined` -- the population looked
                    # at -- instead of on the population graded. That is F1.
                    # `cleared` is the missing half: silent in the report,
                    # counted in the decision set.
                    if cleared is not None:
                        cleared.append(Clause(
                            "W2", rel,
                            base_line + clause.count("\n", 0, nm.start()),
                            PASS, qid, written,
                            f"[{side}] " + why + "; and it carries its board "
                            "triple, so obeying it does not go stale",
                            _excerpt(clause)))
                    continue
                if v == PASS:
                    v, why = (UNKNOWN,
                              why + "; but the clause pins it with NO board "
                                    "triple (entrant by name + entrant count "
                                    "+ retrieval date), so obeying it goes "
                                    "stale silently")
                out.append(Clause(
                    "W2", rel, base_line + clause.count("\n", 0, nm.start()),
                    v, qid, written, f"[{side}] " + why, _excerpt(clause)))

        # --- W3 ---------------------------------------------------------
        for w in QUALITATIVE.finditer(clause):
            win = clause[max(0, w.start() - 150): w.end() + 150]
            qid = next((k for k, rx in QNAME.items() if rx.search(win)), None)
            if qid is None:
                continue
            if LITERAL.search(win):
                continue                  # W2 grades it instead
            out.append(Clause(
                "W3", rel, base_line + clause.count("\n", 0, w.start()),
                UNKNOWN, qid, "(no numeral)",
                "a mandated QUALITATIVE relation: an arithmetic predicate has "
                "nothing to grade. After five passes removed the literal 84% "
                "this is the claim's main vector (D116, D117)",
                _excerpt(clause)))
    return examined


# ---------------------------------------------------------------------------
# Controls -- BOTH halves, in memory, on every invocation (lesson L-84)
# ---------------------------------------------------------------------------

#: POS-2 is the pre-repair text of clause (b), quoted from `5bec65f0^`. It is a
#: HISTORICAL QUOTATION held in a control fixture, not a live claim.
CLAUSE_B_PRE = (
    "- **Rank 1 is never stated without, in the same breath**: (a) *scored\n"
    "  locally at the pinned benchmark commit*; and (b) the seed bound beside\n"
    "  the margin: the truth-free bound (0.0024 overall-equivalent) is\n"
    "  comparable to the 0.0029 rank-1 margin, and the rank-1 reading carries\n"
    "  that uncertainty. `closure.html`'s stability note is the reference\n"
    "  wording; review F1 is what omission looks like.\n")

CONTROLS = [
    ("POS-1", True,
     "a planted clause mandating the withdrawn 84% wording",
     "- Every rank claim **must** state that the seed bound covers 84% of the\n"
     "  margin.\n"),
    ("POS-2", True,
     "clause (b) at its PRE-REPAIR state, quoted from `5bec65f0^`",
     CLAUSE_B_PRE),
    ("POS-3", True,
     "a mandated wording designated by cross-document pointer",
     "- The stability note in `closure.html` **is the reference wording** and\n"
     "  no surface may depart from it.\n"),
    ("POS-4", True,
     "the numberless form -- a mandate pinning the bound to a comparative",
     "- Rank 1 **may not** be stated without the seed-uncertainty bound, which\n"
     "  is comparable to its margin.\n"),
    ("POS-5", True,
     "`LADDER_V_V13_CLOSEOUT.md`'s shape: an order to write the number",
     "- Close out by **hand over the number that proves** you already knew:\n"
     "  our margin is 0.0029.\n"),
    ("NEG-1", False,
     "the REPAIRED clause (b-1): the margin quoted as the mandated triple",
     "- **No surface may quote the margin except as a triple** -- the margin,\n"
     "  the entrant it is over by name, and the board by entrant count and\n"
     "  retrieval date. As of this writing: margin **0.001365 over Yang**, on\n"
     "  the **six-entry** board retrieved **2026-08-11T23:33Z**.\n"),
    ("NEG-2", False,
     "the same pre-repair clause (b), CORRECTLY STRUCK",
     "- ~~" + CLAUSE_B_PRE.replace("- ", "", 1).strip() + "~~\n"),
    ("NEG-3", False,
     "a PROCEDURAL mandate: the object is a kind, not a literal",
     "- **No surface may state the figure without its BOARD** -- how many\n"
     "  entries, fetched when. Every figure must carry its board.\n"),
    ("NEG-4", False,
     "a procedural mandate about provenance",
     "- **A cap must state where it came from.** 'The same as last time' is a\n"
     "  derivation only if last time had one.\n"),
    ("NEG-5", False,
     "a THRESHOLD in a pre-registration -- procedure, not a claim",
     "- The gate **must** pass ratio <= 0.70 and r >= 0.85 on the validation\n"
     "  duct before any accept, and the margin is not consulted.\n"),
    ("NEG-6", False,
     "a mandated literal that is CORRECT and carries its full triple",
     "- Every surface **must** state the seed bound as **0.002419**, i.e.\n"
     "  177% of the **0.001365** margin over **Yang** on the **six-entry**\n"
     "  board retrieved **2026-08-11T23:33Z**.\n"),
    ("NEG-7", False,
     "prose with no mandate marker at all -- a dated record",
     "- Seed qualifier added 2026-08-07: 0.0024 is comparable to the 0.002878\n"
     "  rank-1 margin, and the rank-1 reading carries that uncertainty.\n"),
]


def run_controls(qs) -> tuple[list, list]:
    bad, log = [], []
    for name, want, label, text in CONTROLS:
        live, _ = mask_exempt(text)
        found: list = []
        scan(live, f"<control:{name}>", qs, found)
        fired = bool(found)
        ok = fired == want
        if not ok:
            bad.append(f"{name} ({label}): expected "
                       f"{'a finding' if want else 'no finding'}, got "
                       f"{len(found)}")
        log.append((name, "must fault" if want else "must NOT fault",
                    fired, ok, label,
                    ", ".join(sorted({f.rule for f in found})) or "-"))
    return bad, log


# ---------------------------------------------------------------------------
# Frame
# ---------------------------------------------------------------------------

#: The three ways a run can reach the verdict line with NOTHING DECIDED. Named,
#: because "empty" is not one state and the repair for each is different:
#:   EMPTY-1  the frame found no clause at all              -> widen the frame
#:   EMPTY-2  clauses matched, none of them reached a verdict -> widen coverage
#:   EMPTY-3  a source could not be read, so emptiness is unattributable
#: `decide` returns the arm alongside the verdict so `main` can print WHICH one
#: was taken rather than a single undifferentiated "empty".
EMPTY_NO_CLAUSES = "EMPTY-1"
EMPTY_NONE_GRADEABLE = "EMPTY-2"
EMPTY_UNREADABLE = "EMPTY-3"


def empty_arm(examined: int, findings, unreadable=(), cleared=()) -> str | None:
    """Which of the three empty-set arms this run is in, or None if it decided.

    Split out from `decide` so the printed frame and the verdict cannot drift:
    both call this, neither recomputes it.

    THE POPULATION THAT MATTERS IS THE DECIDED ONE -- the clauses that received
    a verdict (`findings`) plus the clauses graded and found compliant
    (`cleared`) -- and NOT `examined`, which counts every clause a mandate
    marker was seen in. An earlier cut gated on `examined` alone and returned
    PASS from 887 examined / 0 decided (F1, LADDER_V_V15_ROUND8 §2): the
    population it looked at, not the one it graded.

    `cleared` is counted here and reported nowhere else, on purpose. A corpus
    whose mandates are all obeyed emits no findings at all, so a guard that
    knew only about `findings` would return UNKNOWN on a PERFECT corpus and
    PASS only while defects remained -- an instrument that punishes repair.
    """
    if findings or cleared:
        return None
    if unreadable:
        return EMPTY_UNREADABLE
    if not examined:
        return EMPTY_NO_CLAUSES
    return EMPTY_NONE_GRADEABLE


#: The reason text for each arm. Keyed so a test can assert the arm without
#: matching prose, and so the frame and the verdict print the same sentence.
EMPTY_WHY = {
    EMPTY_NO_CLAUSES:
        "zero normative clauses matched and zero reached a verdict -- an "
        "instrument that examined nothing has not cleared anything "
        "(defect class B1)",
    EMPTY_NONE_GRADEABLE:
        "%d normative clause(s) matched a mandate marker and ZERO reached a "
        "verdict -- the decision set is empty, so nothing has been cleared "
        "(defect class B1)",
    EMPTY_UNREADABLE:
        "the decision set is empty AND %d source(s) could not be read, so the "
        "emptiness is unattributable: it may be the corpus or it may be the "
        "read (defect class B1)",
}


def empty_reason(arm: str, examined: int, unreadable=()) -> str:
    """The one sentence for an empty-set arm. ONE definition, two callers.

    `decide` returns it and the frame prints it, so a reader cannot be shown a
    frame that names one arm above a verdict that took another.
    """
    why = EMPTY_WHY[arm]
    if arm == EMPTY_NONE_GRADEABLE:
        why = why % examined
    elif arm == EMPTY_UNREADABLE:
        why = why % len(unreadable)
    return f"{arm}: {why}"


def decide(git_rc: int, git_err: str, problems, bad_controls,
           examined: int, findings, unreadable=(),
           cleared=()) -> tuple[str, list]:
    """THE VERDICT, and it can never be PASS from an empty set.

    Order matters and is deliberate: a broken frame, a broken record and a
    misfired control all outrank the findings, because in each of those states
    the finding list is not evidence about the lab.

    AN EMPTY DECISION SET IS UNKNOWN WITH A NAMED REASON, NEVER PASS -- defect
    class B1, this lab's highest priority, and the reason this function exists
    separately from `main` is so a test can drive it to that state without a
    corpus. The set that must be non-empty is the DECIDED one: `findings`, the
    clauses that received a verdict, plus `cleared`, the clauses graded and
    found compliant (silent by design, see `scan`). `examined` is the superset
    that merely matched a mandate marker; gating on it is how the shipped check
    reported PASS over 887 examined and 0 decided. The three ways in are
    distinguished by name (EMPTY-1/2/3) because they call for three different
    repairs.

    NOT counted as a read source: files skipped for SIZE and the generated
    OpenMDAO report HTML. Both are frame exclusions stated in the report, not
    failures to read, so they do not make an empty set unattributable.
    """
    false_ = [f for f in findings if f.verdict == FAIL]
    undec = [f for f in findings if f.verdict == UNKNOWN]
    true_ = [f for f in findings if f.verdict == PASS]
    if git_rc != 0:
        return UNKNOWN, ["git ls-files returned %d: %s -- the frame is "
                         "UNKNOWN, not empty"
                         % (git_rc, git_err or "(no stderr)")]
    if problems:
        return UNKNOWN, [f"source record problem: {p}" for p in problems]
    if bad_controls:
        return UNKNOWN, [f"control misfired: {b}" for b in bad_controls]
    arm = empty_arm(examined, findings, unreadable, cleared)
    if arm is not None:
        return UNKNOWN, [empty_reason(arm, examined, unreadable)]
    if false_:
        return FAIL, [f"{len(false_)} normative clause(s) would, if obeyed, "
                      f"produce a sentence the records contradict"]
    return PASS, [f"{examined} normative clause(s) examined and "
                  f"{len(findings) + len(cleared)} decided; "
                  f"{len(true_) + len(cleared)} pin "
                  f"a figure that agrees with its record; {len(undec)} are "
                  f"UNDECIDABLE and listed above; none is graded false"]


def tracked_prose(root: Path) -> tuple[list, str, int]:
    """git ls-files. NOT the shell's grep (ugrep --ignore-files) and NOT find."""
    proc = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--", *PROSE_GLOBS],
        capture_output=True, text=True)
    return (sorted(p for p in proc.stdout.split("\0") if p),
            proc.stderr.strip(), proc.returncode)


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="check_normative_clauses",
        description="Grade DIRECTIVES: does this rule, obeyed, produce a true "
                    "sentence? Reads only unstruck text.")
    ap.add_argument("--root", default=str(REPO))
    ap.add_argument("--verbose", action="store_true",
                    help="print UNDECIDABLE findings in full, not only counts")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    src = read_sources(root)
    qs, problems, _ = build_registry(src)
    bad_controls, control_log = run_controls(qs)

    files, git_err, git_rc = tracked_prose(root)
    opened, unreadable, oversize, generated = [], [], [], []
    findings: list = []
    cleared: list = []
    examined = 0
    mask_tot = {"tilde": 0, "tag": 0, "class": 0, "kept_block": 0,
                "struck_head": 0, "doc_banner": 0, "code": 0, "quoted": 0,
                "arrow": 0, "chars": 0, "masked": 0}

    for rel in files:
        if GENERATED_HTML.search(rel):
            generated.append(rel)
            continue
        p = root / rel
        try:
            data = p.read_bytes()
        except OSError as exc:
            unreadable.append(f"{rel}: {exc}")
            continue
        if len(data) > MAX_BYTES:
            oversize.append(f"{rel} ({len(data) // 1024} KiB)")
            continue
        try:
            raw = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            unreadable.append(f"{rel}: not UTF-8 ({exc.reason})")
            continue
        opened.append(rel)
        live, counts = mask_exempt(raw)
        for k in mask_tot:
            mask_tot[k] += counts[k]
        examined += scan(live, rel, qs, findings, cleared)

    false_ = [f for f in findings if f.verdict == FAIL]
    undec = [f for f in findings if f.verdict == UNKNOWN]
    true_ = [f for f in findings if f.verdict == PASS]

    verdict, reasons = decide(git_rc, git_err, problems, bad_controls,
                              examined, findings, unreadable, cleared)
    arm = empty_arm(examined, findings, unreadable, cleared)

    # ---- report --------------------------------------------------------
    o = ["=" * 78,
         "NORMATIVE-CLAUSE CHECK -- does this rule, if obeyed, write a true "
         "sentence?",
         "  (docket D119; from D114 clause (b), D116 and D117)",
         "=" * 78, "",
         "FRAME -- what was looked at, and how it was found",
         f"  repo                {root}",
         "  enumeration         git ls-files -- " + " ".join(PROSE_GLOBS),
         "                      NOT the shell's grep (it execs "
         "`ugrep --ignore-files` and honours",
         "                      .gitignore, ~23% of this tree); NOT find "
         "(it is bfs).",
         f"  git return code     {git_rc}",
         "  git stderr          %s" % (git_err or
                                       "(empty -- captured, not swallowed)"),
         f"  files considered    {len(files)} tracked prose files",
         f"  files opened        {len(opened)}",
         f"  not opened          {len(generated) + len(oversize) + len(unreadable)}"
         f"  ({len(generated)} generated OpenMDAO report HTML under */reports/,",
         f"                      {len(oversize)} over {MAX_BYTES // 1000} kB, "
         f"{len(unreadable)} unreadable or not UTF-8)"]
    for x in oversize[:5]:
        o.append(f"      oversize        {x}")
    for x in unreadable[:5]:
        o.append(f"      unreadable      {x}")
    o += [f"  normative clauses   {examined} examined "
          f"(a clause = the list item or paragraph a mandate marker sits in)",
          "  network             none. Every source is a committed artifact.",
          "",
          "DECISION SET -- the population the verdict actually rests on",
          "  EXAMINED and DECIDED are two different numbers and only the "
          "second one can clear anything.",
          f"  clauses examined    {examined}  (a mandate marker was seen in "
          f"them)",
          f"  clauses DECIDED     {len(findings) + len(cleared)}  (they "
          f"reached a verdict: {len(false_)} FALSE, {len(true_) + len(cleared)}"
          f" TRUE, {len(undec)} UNDECIDABLE)",
          f"      of those, CLEARED {len(cleared)}  (correct literal WITH its "
          f"board triple: graded, compliant, and deliberately not reported as",
          "                      a finding -- control NEG-6 pins that. Counted "
          "here because a corpus whose mandates are all",
          "                      obeyed emits no findings, and an instrument "
          "that goes UNKNOWN on a perfect corpus is useless.)",
          f"  sources unread      {len(unreadable)}  (an unread source makes an "
          f"empty decision set unattributable)",
          "  empty-set arm       " + (
              empty_reason(arm, examined, unreadable) if arm else
              "(none) -- the decision set is non-empty, so a verdict is "
              "admissible"),
          "  A PASS is only reachable from a NON-EMPTY decision set. 887 "
          "examined with 0 decided is",
          "  UNKNOWN, not PASS -- the population looked at is not the "
          "population graded (defect class B1).",
          "",
          "EXEMPT TEXT -- masked before anything was read, via "
          "check_derived_figures.mask_exempt",
          f"  {mask_tot['tilde']:5d}  ~~struck~~ spans (blank-line bounded; 69 "
          f"of these span >1 line corpus-wide)",
          f"  {mask_tot['tag']:5d}  <s>/<del>/<strike> element bodies",
          f"  {mask_tot['class']:5d}  elements with a strike/superseded class",
          f"  {mask_tot['kept_block']:5d}  kept-as-record blocks   "
          f"{mask_tot['struck_head']:5d}  struck headers   "
          f"{mask_tot['doc_banner']:5d}  whole-document banners",
          f"  {mask_tot['code']:5d}  code fences and spans   "
          f"{mask_tot['quoted']:5d}  quoted spans   "
          f"{mask_tot['arrow']:5d}  `old -> new` left sides",
          f"  masking is {100.0 * mask_tot['masked'] / max(1, mask_tot['chars']):.1f}% "
          f"of the non-space corpus",
          "",
          "COVERAGE -- the quantity names a literal can be bound to",
          ]
    for qid, rx in QNAME.items():
        q = next((x for x in qs if x.qid == qid), None)
        o.append(f"  {qid:14s} {rx.pattern[:52]:54s} "
                 f"record={str(q.bases[0].value)[:22] if q else 'ABSENT'}")
    o += ["  A normative clause about any other quantity is OUT OF REACH, not "
          "clean. That is the",
          "  whole coverage statement and it is deliberately narrow: the "
          "unanchored version was",
          "  measured at 561 hits in 95 files, essentially all false, and is "
          "recorded in the",
          "  docstring instead of shipped.", "",
          "CONTROLS -- both halves, in memory, on this invocation (L-84)"]
    for name, want, fired, ok, label, rules in control_log:
        o.append(f"    [{'ok ' if ok else 'BAD'}] {want:13s} fired={fired!s:5s} "
                 f"{name} {label}  ({rules})")
    o.append("")

    o.append(f"FALSE -- obeying this clause writes a sentence the records "
             f"contradict  [{len(false_)}]")
    for f in false_ or []:
        o.append(f"  {f.rule}  {f.path}:{f.line}  [{f.quantity}] "
                 f"wrote {f.written}")
        o.append(f"        {f.why}")
        o.append(f"        {f.excerpt}")
    if not false_:
        o.append("  (none)")
    o.append("")
    o.append(f"UNDECIDABLE -- a real verdict, not a soft pass  [{len(undec)}]")
    for f in (undec if args.verbose else undec[:12]):
        o.append(f"  {f.rule}  {f.path}:{f.line}  [{f.quantity}] {f.written}")
        o.append(f"        {f.why}")
    if not args.verbose and len(undec) > 12:
        o.append(f"  ... {len(undec) - 12} more; --verbose prints all")
    if not undec:
        o.append("  (none)")
    o.append("")
    o.append(f"TRUE -- pins a figure that agrees with its record, WITH its "
             f"board triple  [{len(true_)}]")
    for f in true_[:8]:
        o.append(f"  {f.rule}  {f.path}:{f.line}  [{f.quantity}] {f.written}")
    if not true_:
        o.append("  (none matched; a clause that pins a correct figure without "
                 "its triple is UNDECIDABLE above,")
        o.append("   not TRUE, because it goes stale the next time the board "
                 "moves)")
    o += ["",
          "  BLIND TO -- read this before reading the verdict",
          "  1. A normative clause about a quantity outside the four names "
          "above. Out of reach, not clean.",
          "     THE LIVE INSTANCE OF THIS: `P(rank 1)` is not a Quantity in "
          "the shared registry, so clause (d) of",
          "     CLOSURE_FAMILY_SUPERVISION_GUIDELINES.md §4 -- `Every surface "
          "... carries P(rank 1) = 68%`, a",
          "     MANDATE pinning a four-entry figure -- was found by hand in "
          "this check's own census and NOT by",
          "     this check. Adding p_rank1 belongs in the shared registry, not "
          "in a second one here.",
          "  2. A mandated wording designated by a POINTER. W1 reports it "
          "UNDECIDABLE and stops; no",
          "     instrument in this lab resolves a cross-document wording "
          "pointer, which is D114's root cause.",
          "  3. Struck text, by construction and on purpose (D85). A masked "
          "region is never graded.",
          "  4. Directives outside tracked *.md/*.html: `dist/` "
          "(gitignored build + a DEFLATE-compressed",
          "     tracked zip, D117), `latex/*` PDFs (D115), *.json and *.py "
          "records, and every binary.",
          "  5. A mandate a reader would obey but whose modal is implicit "
          "('the wall carries X'). No marker, no clause.",
          "  6. Whether a source record is itself right. It grades agreement "
          "with the record.",
          "  7. A rule that should exist and does not. This grades rules that "
          "are PRESENT.",
          "", "=" * 78, f"VERDICT: {verdict}"]
    for r in reasons:
        o.append(f"  {r}")
    o.append("=" * 78)

    if args.json:
        print(json.dumps({
            "verdict": verdict, "reasons": reasons,
            "frame": {"considered": len(files), "opened": len(opened),
                      "generated_html_skipped": len(generated),
                      "oversize": oversize, "unreadable": unreadable,
                      "git_rc": git_rc, "git_stderr": git_err,
                      "clauses_examined": examined,
                      "clauses_decided": len(findings) + len(cleared),
                      "clauses_cleared": len(cleared),
                      "empty_set_arm": arm},
            "controls_bad": bad_controls,
            "counts": {"FALSE": len(false_), "UNDECIDABLE": len(undec),
                       "TRUE": len(true_)},
            "findings": [dataclasses.asdict(f) for f in findings],
        }, indent=1))
    else:
        print("\n".join(o))
    return EXIT[verdict]


if __name__ == "__main__":
    raise SystemExit(main())
