#!/usr/bin/env python3
"""A claim and its own restatement, inside ONE document, graded against each other.

WHY THIS EXISTS (docket D141, filed 2026-08-15 at `a20a720b`)
=============================================================
A summary block can go stale against the section it summarises **with neither
one being edited**. The defect is the ABSENCE of an edit, so nothing reddens in
a commit, nothing shows in a diff, and both regions stay byte-identical to what
one commit wrote months of edits earlier.

The instance that named the class: the currency block of
`demo-output/website/CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` carried a row

    | **4.8** | leaderboard position is current | **HOLDS ON ITS OWN TERMS ...
      re-verifying it needs a network read this pass did not perform.** | ...

while **section 4.8, 212 lines below in the same file**, had been headed
`### 4.8 Leaderboard position is current -- ~~VERIFIED~~ **FALSIFIED
2026-08-11**` since `5c9c63fb`. The network read the row said was not performed
HAD been performed, and it falsified the section the row was grading.

BYTE-IDENTITY DECIDES NOTHING, IN EITHER DIRECTION
==================================================
This is the observation that shapes the whole design, and it is measured rather
than assumed. When the block was repaired at `87324012`, all eleven rows were
compared against their sections by execution:

    the stale row (4.8)          byte-identical to `472f9f92` AND WRONG
    ten other rows              byte-identical to `472f9f92` AND STILL RIGHT

So `unchanged since X` is not a signal for staleness and not a signal for
currency. Any check built on "has this text moved" is measuring the wrong
thing. This one compares the summary's CLAIM against the section's CURRENT
STATE, and never looks at a diff.

Every other instrument in this lab has a different unit: `check_derived_figures`
grades a figure against the machine record it is derived from, `self_audit`'s
`_best_on_board_faults` grades a count against a board, `board_placement_faults`
grades an ordinal against a board, `check_absolutes` grades a sentence. None of
them takes TWO REGIONS OF ONE DOCUMENT as its unit. That gap is this file.

HOW THE PAIRS ARE FOUND -- MECHANICALLY, AND NEVER FROM A LIST
==============================================================
A hand-maintained register of "the summary blocks in this lab" would be the
same defect one level up. This lab has been bitten by that repeatedly: the
exec-bit waiver register that went stale the day after it was dated, the
"twelve rows" grade over an eleven-row block, a cross-surface sweep whose
principled exclusion was falsified by the repair pass editing the excluded
file. **A clearance verified against an enumeration cannot see the item beside
the ones it lists.** So there is no list here.

A pair is derived from document STRUCTURE, in two halves:

  SECTIONS   every ATX heading (`#`..`######`), including inside a blockquote,
             carrying a dotted section number at the head of its text
             (`### 4.8 Leaderboard position ...` -> `4.8`) or an explicit
             anchor (`<a id="x">`, `{#x}`).

  SUMMARIES  a TABLE ROW whose LEADING CELL is a section identifier and nothing
             else (`| **4.8** | ...`, `| **4.1** *(citations)* | ...`,
             `| [4.8](#4-8) | ...`), or a BULLET that names a section
             identifier in its first 60 characters (`- **Sec 4.8** -- HOLDS`).

The leading-cell rule is the load-bearing one and it is deliberately narrow. A
`SS4.8` deep inside a body cell is a CITATION of that section, not a summary of
it, and pairing on every mention produced 40x the pairs and no additional true
positive when it was tried. What makes a region a summary is that the
identifier is what the region is ABOUT -- structurally, its subject column.

WHAT IS GRADED, AND WHAT IS NOT
===============================
GRADED -- the verdict word, which is where the real instance lived. D141 names
seven; three more sit on the DENY side because they are exactly the withdrawal
verbs the section-side predicate already reads, and two sides of one comparison
must not speak different vocabularies. Read ALL-CAPS only:

    AFFIRM   HOLDS  VERIFIED
    DENY     FALSIFIED  SUPERSEDED  MOOT  WITHDRAWN  STRUCK  RETRACTED
    NEUTRAL  RESOLVED  OPEN

MEASURED, not assumed, before those three were kept: over the full corpus the
seven graded 1 pair of 92 and the ten grade 2 of 95. A wider trawl was also
measured and REJECTED -- adding `PARTIAL`, `PENDING`, `AMENDED`, `CORRECTED`,
`EXTENDED`, `CLOSED` as further NEUTRALs took the graded count to ZERO, because
the one real instance's repaired row contains the word `CORRECTED` and would
have been swallowed by its own mixed polarity. A vocabulary that grades less
the more words it knows is a vocabulary being tuned rather than derived.

A hit is an AFFIRM in the live summary against a DENY in the live section, or a
DENY in the summary against an AFFIRM in the section. Everything else --
NEUTRAL on either side, mixed polarity on either side, no verdict word on
either side -- is UNDECIDABLE with the reason printed. The polarity classes are
narrow on purpose: `RESOLVED` against `FALSIFIED` is not obviously a
contradiction (a defect can be resolved in a section that was falsified), and a
checker that forces a verdict there is a checker being tuned toward a prettier
number.

GRADED -- the STATUS MARKER on the section side, and it reuses the masker's own
predicate rather than a second one: a heading that `check_derived_figures`'s
`_STRUCK_HEAD` matches (`STRUCK`, `WITHDRAWN`, `SUPERSEDED`, `RETRACTED`,
`FALSIFIED`) is a section that declares itself withdrawn, and counts as DENY
even when the word is not in the seven. That is how `### 6.1 STRUCK,
2026-08-14` is graded at all.

NOT GRADED -- figures. `parse_written` from `check_derived_figures` is imported
and available, and it was tried: a row and its section routinely state
different numbers ABOUT DIFFERENT THINGS (the 4.8 row's `0.0676` is round 3's
score; 4.8's own body states a rank and a date), so pairing them needs an
anchor-phrase match, which is exactly what `check_derived_figures` already does
against MACHINE RECORDS -- a strictly stronger comparison than row-against-
section. Grading a figure here would duplicate that check while being weaker
than it. Stated as a coverage gap, printed on every run, rather than shipped as
a source of false positives.

NOT GRADED -- lowercase verdict words. `the rule holds` in running prose is
common, and admitting it multiplied candidate verdicts without adding a true
positive. The count of pairs that would become gradeable under the loose rule
is printed every run, so the size of what this rule forgoes is visible.

A FALSE POSITIVE ON STRUCK TEXT IS WORSE THAN A MISS
====================================================
A summary row wrapped in `~~...~~` and kept is a legitimate historical record,
and a check that flags it trains its readers to ignore it. So exemption is
decided by `check_derived_figures.mask_exempt`, IMPORTED, never reimplemented:
that corpus carries 252 strike spans of which **69 are multi-line and 8 cross
blockquote continuations**, and a line-by-line masker is wrong on all 77. Two
authors' first cuts here were line-by-line.

The masker is used on both sides but not identically, and the asymmetry is
deliberate:

  SUMMARY SIDE  the whole-document mask. If the row's verdict word is blanked,
                the row is EXEMPT and is counted as exempt, not as clean.

  SECTION SIDE  the heading line alone, with its `#` and `>` markers neutered
                so `_STRUCK_HEAD` cannot fire and blank it. What must survive
                on this side is the LIVE half of a corrected heading:
                `~~VERIFIED~~ **FALSIFIED 2026-08-11**` must read as FALSIFIED,
                not as nothing. Whether the heading is struck AS A WHOLE is
                then asked of `_STRUCK_HEAD` again, over the MASKED heading
                with one `#` put back -- not over the raw line. Asking the raw
                line is wrong in the other direction: `### 9.2 The widget --
                ~~FALSIFIED~~ **VERIFIED 2026-08-12**` matches the predicate
                while being a section that is not withdrawn at all, and reading
                it as withdrawn would flag every correct summary of it.

THREE-VALUED, AND IT CANNOT PASS FROM AN EMPTY SET (defect class B1)
====================================================================
    PASS         pairs were found, at least one was GRADED, none disagreed.
    FAIL         at least one graded pair disagreed.
    UNKNOWN      zero documents opened; or zero pairs found; or pairs found but
                 NONE gradeable (nothing was actually compared); or a control
                 misfired.

Zero pairs is UNKNOWN with a reason, never PASS. So is "eleven pairs, all
undecidable" -- an instrument that compared nothing has cleared nothing.

CONTROLS BOTH WAYS, EVERY RUN (lesson L-84)
===========================================
A positive control proves an instrument CAN fire. It does not prove it fires
only where it should, and this check's whole job is a discrimination, so the
must-not-match half is the important half. Both halves run in-process on every
invocation, against two IMMUTABLE git blobs named by commit:

  PRE  = `87324012~1:demo-output/website/CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md`
  POST = `87324012:` the same path

  P1  PRE, target 4.8 -- the real defect at its real pre-repair state. MUST FIRE.
  N1  PRE, the OTHER TEN ROWS of that same block -- byte-identical to the stale
      one's provenance and STILL RIGHT. MUST NOT FIRE. This is the exact
      discrimination the check exists to make, and it is the control that would
      be missing from a check tuned to fire.
  N2  POST, target 4.8 -- the repaired row. MUST NOT FIRE.
  P2  synthetic: a `HOLDS` row over a `FALSIFIED` section. MUST FIRE.
  N3  synthetic: the same row struck (`~~ ... ~~`) over the same FALSIFIED
      section -- a correctly kept historical record. MUST NOT FIRE, and must be
      reported as EXEMPT rather than as clean.

A control that misfires makes the whole run UNKNOWN. The instrument does not
get to report on the lab while it is failing to report on itself.

USAGE
=====
    scripts/check_summary_consistency.py              # tracked prose (default)
    scripts/check_summary_consistency.py --arm all    # + untracked + gitignored
    scripts/check_summary_consistency.py --extra-root /home/ubuntu/certonomous-runs
    scripts/check_summary_consistency.py --verbose    # every pair and its grade
    scripts/check_summary_consistency.py --json

Exit codes follow `scripts/lab_check.py`'s published contract: 0 PASS, 1 FAIL,
3 UNKNOWN. Nothing here writes, no network, no solver, no scoring call.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_derived_figures as cdf  # noqa: E402  (mask_exempt, _STRUCK_HEAD)

# The one module that names this repository's tree (MOVE_MAP batch 3).
# Every name it exports is bound to a legacy/successor PAIR resolved
# against the filesystem at import, so the constants below are correct
# before the move, between batches and after it, with no edit here.
import sys as _sys  # noqa: E402
import pathlib as _pathlib  # noqa: E402
_LAB_PATHS_DIR = str(_pathlib.Path(__file__).resolve().parents[1]
                     / "scripts")
if _LAB_PATHS_DIR not in _sys.path:
    _sys.path.insert(0, _LAB_PATHS_DIR)
import lab_paths  # noqa: E402

PASS, FAIL, UNKNOWN = "PASS", "FAIL", "UNKNOWN"
EXIT = {PASS: 0, FAIL: 1, UNKNOWN: 3}

#: The commit that repaired the D141 instance. Its parent holds the defect.
CONTROL_COMMIT = "87324012"
CONTROL_PATH = str(lab_paths.web_file(
    "CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md").relative_to(lab_paths.REPO))

# ---------------------------------------------------------------------------
# Verdict vocabulary
# ---------------------------------------------------------------------------

#: D141 names seven. `WITHDRAWN`, `STRUCK` and `RETRACTED` are added to DENY
#: for ONE reason, and it is not that they seemed useful: they are exactly the
#: withdrawal verbs `check_derived_figures._STRUCK_HEAD` already treats as a
#: section declaring itself out, and this check reads that predicate on the
#: section side. Leaving them off the summary side would mean the two sides of
#: one comparison spoke different vocabularies. The effect was MEASURED before
#: it was kept -- see the docstring's design note.
AFFIRM = ("HOLDS", "VERIFIED")
DENY = ("FALSIFIED", "SUPERSEDED", "MOOT", "WITHDRAWN", "STRUCK", "RETRACTED")
NEUTRAL = ("RESOLVED", "OPEN")
VERDICTS = AFFIRM + DENY + NEUTRAL
POLARITY = dict([(w, "AFFIRM") for w in AFFIRM]
                + [(w, "DENY") for w in DENY]
                + [(w, "NEUTRAL") for w in NEUTRAL])

#: ALL-CAPS only. `HOLDS` is a verdict; `holds` is a verb. Word-bounded so
#: `UPHOLDS` and `HOLDS-ON` behave, and `MOOTNESS` does not match.
_VERDICT_RE = re.compile(r"\b(" + "|".join(VERDICTS) + r")\b")
_VERDICT_LOOSE = re.compile(r"\b(" + "|".join(VERDICTS) + r")\b", re.I)

# ---------------------------------------------------------------------------
# Structure
# ---------------------------------------------------------------------------

#: An ATX heading, optionally inside a blockquote. Group 1 is the marker run.
_HEAD_RE = re.compile(r"^([ \t]*(?:>[ \t]*)*)(#{1,6})[ \t]+(.*)$")

#: A dotted section number at the head of a heading's text, after any emphasis
#: or strike markers. At least one dot is required: a bare `4` collides with
#: every "4." ordered-list item and every year-like token in the corpus.
_HEAD_NUM = re.compile(r"^[\s*_~`§#]*((?:\d+\.)+\d+)[\s.:)—-]")

#: `<a id="x">`, `<a name="x">`, `{#x}` -- an explicit anchor on a heading.
_ANCHOR_RE = re.compile(r"<a\s[^>]*(?:id|name)=[\"']([^\"']+)[\"']|\{#([^}\s]+)\}")

#: A table row: leading blockquote markers, then a pipe. Two pipes minimum.
_ROW_RE = re.compile(r"^[ \t]*(?:>[ \t]*)*\|")
_SEP_RE = re.compile(r"^[ \t]*(?:>[ \t]*)*\|[\s|:-]*\|[\s|:-]*$")

#: A bullet or a numbered list item, optionally inside a blockquote.
_BULLET_RE = re.compile(r"^[ \t]*(?:>[ \t]*)*(?:[-*+]|\d+\.)[ \t]+(.*)$")

#: A leading cell that IS a section identifier and nothing else. The trailing
#: parenthetical is real: `| **4.1** *(citations)* |` is the second row the
#: eleven-row block spends on section 4.1, and dropping it loses a pair.
_CELL_NUM = re.compile(
    r"^[\s*_~`]*§?[\s*_~`]*((?:\d+\.)+\d+)[\s*_~`]*"
    r"(?:[\s*_~`(\[][^|]{0,40})?$")

#: `| [4.8](#4-8) |` or `| #4-8 |` -- an anchor as the leading cell.
_CELL_ANCHOR = re.compile(r"^[\s*_~`]*(?:\[[^\]]*\]\(#([^)]+)\)|#([\w.-]+))[\s*_~`]*$")

#: In a bullet's opening run: `SS4.8`, `Sec 4.8`, `section 4.8`, `[..](#slug)`.
_BULLET_REF = re.compile(
    r"§[\s*_~`]*((?:\d+\.)+\d+)"
    r"|\b(?:sec|sect|section)\.?[\s*_~`]*((?:\d+\.)+\d+)"
    r"|\]\(#([\w.-]+)\)", re.I)
BULLET_HEAD_CHARS = 60


def slug(text: str) -> str:
    """GitHub's heading slug, near enough for matching an in-document anchor."""
    t = re.sub(r"<[^>]*>", "", text)
    t = re.sub(r"[`*_~]", "", t).strip().lower()
    t = re.sub(r"[^\w\s-]", "", t)
    return re.sub(r"[\s]+", "-", t).strip("-")


#: The THIRD pairing rule, and the one that reaches sections this corpus does
#: not number: a leading cell that repeats the section's HEADING STRING.
#: `| S3 residual spike |` against `### S3. Residual spike`, `| **Out of
#: scope** -- the exception path ... |` against `### 5. Out of scope -- the
#: exception path ...`. Both sides are normalised the same way: any leading
#: ordinal is dropped, and everything after the first em-dash is dropped
#: because THAT IS WHERE THE VERDICT LIVES (`### S7. Oscillatory divergence --
#: **WITHDRAWN 2026-08-01**`) and keying on it would make a heading match only
#: a row that already agrees with it.
HEAD_KEY_MIN = 8


def head_key(text: str) -> str:
    t = re.sub(r"^[\s*_~`#§]*(?:\d+\.)*\d+[\s.:)—-]+", "", text)
    t = re.split(r"\s+[—–-]{1,2}\s+", t)[0]
    return slug(t)


@dataclasses.dataclass
class Section:
    line: int          # 0-based line index of the heading
    level: int
    text: str          # heading text, markers stripped
    idents: tuple      # every identifier this heading answers to


@dataclasses.dataclass
class Summary:
    line: int
    kind: str          # "table-row" | "bullet" | "table-row/heading-string"
    ident: str
    raw: str
    space: str = "id"  # "id" (number or anchor) | "head" (heading string)


@dataclasses.dataclass
class Pair:
    path: str
    sum_line: int
    sec_line: int
    kind: str
    ident: str
    grade: str         # "AGREE" | "DISAGREE" | "UNDECIDABLE" | "EXEMPT"
    reason: str
    sum_verdicts: tuple = ()
    sec_verdicts: tuple = ()
    excerpt: str = ""
    head: str = ""


def find_sections(raw: str) -> list:
    out = []
    for i, ln in enumerate(raw.split("\n")):
        m = _HEAD_RE.match(ln)
        if not m:
            continue
        text = m.group(3).rstrip()
        idents = []
        n = _HEAD_NUM.match(text + " ")
        if n:
            idents.append(n.group(1))
        for a in _ANCHOR_RE.finditer(ln):
            idents.append((a.group(1) or a.group(2)).lower())
        s = slug(text)
        if s:
            idents.append(s)
        out.append(Section(i, len(m.group(2)), text, tuple(idents)))
    return out


def _cells(line: str) -> list:
    body = re.sub(r"^[ \t]*(?:>[ \t]*)*", "", line).strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    return body.split("|")


def find_summaries(raw: str) -> list:
    """Table rows and bullets whose SUBJECT is a section identifier."""
    lines = raw.split("\n")
    out = []
    for i, ln in enumerate(lines):
        if _ROW_RE.match(ln) and ln.count("|") >= 2:
            if _SEP_RE.match(ln):
                continue
            # The header row is the one immediately above a separator row.
            if i + 1 < len(lines) and _SEP_RE.match(lines[i + 1]):
                continue
            cells = _cells(ln)
            if len(cells) < 2:
                continue
            lead = cells[0]
            m = _CELL_NUM.match(lead)
            if m:
                out.append(Summary(i, "table-row", m.group(1), ln))
                continue
            a = _CELL_ANCHOR.match(lead)
            if a:
                out.append(Summary(i, "table-row",
                                   (a.group(1) or a.group(2)).lower(), ln))
                continue
            key = head_key(lead)
            if len(key) >= HEAD_KEY_MIN:
                out.append(Summary(i, "table-row/heading-string", key, ln,
                                   "head"))
            continue
        b = _BULLET_RE.match(ln)
        if b:
            head = b.group(1)[:BULLET_HEAD_CHARS]
            r = _BULLET_REF.search(head)
            if r:
                ident = r.group(1) or r.group(2) or (r.group(3) or "").lower()
                out.append(Summary(i, "bullet", ident, ln))
    return out


def verdicts_in(text: str) -> tuple:
    return tuple(sorted({w.upper() for w in _VERDICT_RE.findall(text)}))


def polarities(words) -> set:
    return {POLARITY[w] for w in words}


def neuter_heading(line: str) -> str:
    """`#` and `>` markers -> spaces, offsets preserved.

    `mask_exempt` blanks a whole section under a heading its `_STRUCK_HEAD`
    matches, which is right for figures and wrong here: what this check needs
    off a corrected heading is its LIVE half. Neutering the markers makes the
    line ordinary text to the masker, so `~~VERIFIED~~ **FALSIFIED**` masks
    down to `FALSIFIED` instead of to nothing. Whether the section is struck
    AS A WHOLE is asked separately, by `_STRUCK_HEAD` on the untouched line.
    """
    return re.sub(r"[#>]", " ", line)


def grade_document(raw: str, path: str) -> tuple:
    """Every summary/section pair in one document, each with its grade."""
    masked, mcounts = cdf.mask_exempt(raw)
    mlines = masked.split("\n")
    rlines = raw.split("\n")
    sections = find_sections(raw)
    summaries = find_summaries(raw)

    index, hindex = {}, {}
    for s in sections:
        for ident in s.idents:
            index.setdefault(ident, []).append(s)
        k = head_key(s.text)
        if len(k) >= HEAD_KEY_MIN:
            hindex.setdefault(k, []).append(s)

    pairs, unresolved, loose_only = [], 0, 0
    for su in summaries:
        if su.space == "head":
            hits = hindex.get(su.ident) or []
        else:
            hits = index.get(su.ident) or index.get(su.ident.lower()) or []
        hits = [h for h in hits if h.line != su.line]
        if not hits:
            unresolved += 1
            continue
        if len(hits) > 1:
            pairs.append(Pair(path, su.line, hits[0].line, su.kind, su.ident,
                              "UNDECIDABLE",
                              f"ambiguous target: {len(hits)} headings answer "
                              f"to {su.ident!r}",
                              excerpt=su.raw[:200], head=hits[0].text[:160]))
            continue
        sec = hits[0]

        live_row = mlines[su.line] if su.line < len(mlines) else ""
        sv = verdicts_in(live_row)
        raw_sv = verdicts_in(su.raw)
        if raw_sv and not sv:
            pairs.append(Pair(path, su.line, sec.line, su.kind, su.ident,
                              "EXEMPT",
                              "summary's verdict word is struck / kept-as-record "
                              "/ quoted -- a struck row is a historical record",
                              raw_sv, (), su.raw[:200], sec.text[:160]))
            continue

        head_live, _ = cdf.mask_exempt(neuter_heading(rlines[sec.line]))
        cv = verdicts_in(head_live)
        # The STATUS MARKER, read off the LIVE heading rather than the raw one.
        # `_STRUCK_HEAD` matches any heading containing a withdrawal verb, so
        # on `### 9.2 The widget -- ~~FALSIFIED~~ **VERIFIED 2026-08-12**` --
        # a correction in the OTHER direction -- the raw line matches and the
        # section is not withdrawn at all. Re-prefixing one `#` onto the masked
        # heading asks the imported predicate about the text that still stands.
        live_struck = cdf._STRUCK_HEAD.match("#" + head_live) is not None
        if live_struck and "DENY" not in polarities(cv or ()):
            cv = tuple(sorted(set(cv) | {"SUPERSEDED"}))

        if not sv:
            if _VERDICT_LOOSE.search(live_row):
                loose_only += 1
            pairs.append(Pair(path, su.line, sec.line, su.kind, su.ident,
                              "UNDECIDABLE",
                              "no ALL-CAPS verdict word in the live summary",
                              sv, cv, su.raw[:200], sec.text[:160]))
            continue
        if not cv:
            if _VERDICT_LOOSE.search(head_live):
                loose_only += 1
            pairs.append(Pair(path, su.line, sec.line, su.kind, su.ident,
                              "UNDECIDABLE",
                              "no verdict word and no struck-heading marker in "
                              "the section's heading",
                              sv, cv, su.raw[:200], sec.text[:160]))
            continue

        sp, cp = polarities(sv), polarities(cv)
        if "NEUTRAL" in sp or "NEUTRAL" in cp:
            pairs.append(Pair(path, su.line, sec.line, su.kind, su.ident,
                              "UNDECIDABLE",
                              "verdict word carries no polarity "
                              "(RESOLVED / OPEN)",
                              sv, cv, su.raw[:200], sec.text[:160]))
            continue
        if len(sp) > 1 or len(cp) > 1:
            pairs.append(Pair(path, su.line, sec.line, su.kind, su.ident,
                              "UNDECIDABLE",
                              "mixed verdict polarity -- summary "
                              f"{sorted(sp)}, section {sorted(cp)}",
                              sv, cv, su.raw[:200], sec.text[:160]))
            continue
        if sp != cp:
            pairs.append(Pair(path, su.line, sec.line, su.kind, su.ident,
                              "DISAGREE",
                              f"summary says {'/'.join(sv)} ({sp.pop()}); "
                              f"section {su.ident} at line {sec.line + 1} says "
                              f"{'/'.join(cv)} ({cp.pop()})",
                              sv, cv, su.raw[:200], sec.text[:160]))
            continue
        pairs.append(Pair(path, su.line, sec.line, su.kind, su.ident, "AGREE",
                          f"both {'/'.join(sorted(sp))}",
                          sv, cv, su.raw[:200], sec.text[:160]))

    return pairs, len(sections), len(summaries), unresolved, loose_only, mcounts


# ---------------------------------------------------------------------------
# Controls -- both halves, every run (L-84)
# ---------------------------------------------------------------------------

SYNTH_FIRE = """\
# A document

| section | claim | verdict |
|---|---|---|
| **9.2** | the widget is current | **HOLDS, and needs no re-read** |

### 9.2 The widget is current -- ~~VERIFIED~~ **FALSIFIED 2026-08-11**

The widget moved.
"""

SYNTH_STRUCK = """\
# A document

| section | claim | verdict |
|---|---|---|
| **9.2** | the widget is current | ~~**HOLDS, and needs no re-read**~~ *(struck 2026-08-11)* |

### 9.2 The widget is current -- ~~VERIFIED~~ **FALSIFIED 2026-08-11**

The widget moved.
"""


def _blob(commit: str, path: str) -> tuple:
    p = subprocess.run(["git", "-C", str(REPO), "show", f"{commit}:{path}"],
                       capture_output=True, text=True)
    if p.returncode != 0:
        return "", f"git show {commit}:{path} rc={p.returncode}: " \
                   f"{p.stderr.strip()}"
    return p.stdout, ""


def run_controls() -> tuple:
    """(misfires, log). A misfire makes the whole run UNKNOWN."""
    bad, log = [], []

    pre, err1 = _blob(CONTROL_COMMIT + "~1", CONTROL_PATH)
    post, err2 = _blob(CONTROL_COMMIT, CONTROL_PATH)
    if err1 or err2:
        return [e for e in (err1, err2) if e], \
               ["control corpus unreadable -- the two git blobs the controls "
                "run on could not be read"]

    def block(text, pairs):
        """The currency block: the CONTIGUOUS TABLE that holds the 4.8 row.

        Scoped by structure rather than by a row list, for the same reason the
        pairs themselves are: a control whose extent is typed out cannot see
        the row beside the ones it names. The block is grown from the 4.8 row
        outward while the lines are still table lines.
        """
        lines = text.split("\n")
        seed = next((p.sum_line for p in pairs if p.ident == "4.8"), None)
        if seed is None:
            return []
        lo = hi = seed
        while lo > 0 and _ROW_RE.match(lines[lo - 1]):
            lo -= 1
        while hi + 1 < len(lines) and _ROW_RE.match(lines[hi + 1]):
            hi += 1
        return [p for p in pairs if lo <= p.sum_line <= hi]

    pre_pairs = block(pre, grade_document(pre, "PRE")[0])
    post_pairs = block(post, grade_document(post, "POST")[0])

    # P1 -- the real defect at its real pre-repair state MUST fire.
    p1 = [p for p in pre_pairs if p.ident == "4.8" and p.grade == "DISAGREE"]
    log.append(f"P1  PRE {CONTROL_COMMIT}~1, target 4.8, must FIRE          "
               f"-> {len(p1)} hit(s)  {'OK' if len(p1) == 1 else 'MISFIRE'}")
    if len(p1) != 1:
        bad.append(f"P1: the pre-repair 4.8 row produced {len(p1)} hits, want 1")

    # N1 -- THE IMPORTANT ONE. Ten rows, byte-identical and still right.
    others = [p for p in pre_pairs if p.ident != "4.8"]
    n1 = [p for p in others if p.grade == "DISAGREE"]
    log.append(f"N1  PRE, the other {len(others)} rows of the same block, "
               f"must NOT fire -> {len(n1)} hit(s)  "
               f"{'OK' if not n1 else 'MISFIRE'}")
    if n1:
        bad.append(f"N1: {len(n1)} of the ten correct rows fired "
                   f"({', '.join(sorted(p.ident for p in n1))})")
    if len(others) < 8:
        bad.append(f"N1: only {len(others)} sibling rows were paired at all -- "
                   f"a must-not-match control over an empty set clears nothing")

    # N2 -- the repaired row must not fire.
    n2 = [p for p in post_pairs if p.ident == "4.8" and p.grade == "DISAGREE"]
    log.append(f"N2  POST {CONTROL_COMMIT}, target 4.8 repaired, must NOT "
               f"fire   -> {len(n2)} hit(s)  {'OK' if not n2 else 'MISFIRE'}")
    if n2:
        bad.append("N2: the repaired 4.8 row still fires")
    got48 = [p for p in post_pairs if p.ident == "4.8"]
    if not got48:
        bad.append("N2: the repaired 4.8 row was not paired at all")
    elif got48[0].grade != "AGREE":
        log.append(f"      (repaired 4.8 grades {got48[0].grade}: "
                   f"{got48[0].reason})")

    # P2 / N3 -- synthetic, both halves.
    sp = [p for p in grade_document(SYNTH_FIRE, "SYNTH")[0]
          if p.grade == "DISAGREE"]
    log.append(f"P2  synthetic HOLDS-over-FALSIFIED, must FIRE            "
               f"-> {len(sp)} hit(s)  {'OK' if len(sp) == 1 else 'MISFIRE'}")
    if len(sp) != 1:
        bad.append(f"P2: synthetic positive produced {len(sp)} hits, want 1")

    sn = grade_document(SYNTH_STRUCK, "SYNTH")[0]
    fired = [p for p in sn if p.grade == "DISAGREE"]
    exempt = [p for p in sn if p.grade == "EXEMPT"]
    log.append(f"N3  synthetic STRUCK row over the same section, must NOT "
               f"fire -> {len(fired)} hit(s), {len(exempt)} exempt  "
               f"{'OK' if not fired and exempt else 'MISFIRE'}")
    if fired:
        bad.append("N3: a correctly struck historical row fired")
    if not exempt:
        bad.append("N3: the struck row was not recognised as exempt -- "
                   "mask_exempt is not reaching it")
    return bad, log


# ---------------------------------------------------------------------------
# Corpus enumeration -- four arms, each named and counted
# ---------------------------------------------------------------------------

def _git_files(root: Path, args_) -> tuple:
    p = subprocess.run(["git", "-C", str(root), *args_],
                       capture_output=True, text=True)
    if p.returncode != 0:
        return [], f"git {' '.join(args_)} rc={p.returncode}: {p.stderr.strip()}"
    return sorted(x for x in p.stdout.split("\0") if x), p.stderr.strip()


PROSE = re.compile(r"\.(md|markdown|html?)$", re.I)

#: A machine-generated payload, recognised STRUCTURALLY rather than by name.
#: `check_derived_figures.GENERATED_HTML` names the DAFoam OpenMDAO reports by
#: their `*/reports/*.html` path, which is right for the tracked arm; the RUN
#: TREE carries hundreds more of the same payloads as `mphys.html`, outside any
#: `reports/` directory, and each costs about a second of regex time and holds
#: no prose. A file whose longest line is over 20k characters is minified
#: JavaScript, not a document. Counted in the frame, never silent.
MINIFIED_LINE = 20_000


def looks_minified(raw: str) -> bool:
    return any(len(ln) > MINIFIED_LINE for ln in raw.split("\n"))


def enumerate_corpus(root: Path, arm: str, extra_roots) -> tuple:
    """(list of (label, relpath), notes). Never shells out to grep or find."""
    files, notes = [], []
    tracked, e = _git_files(root, ["ls-files", "-z", "--", *cdf.PROSE_GLOBS])
    if e:
        notes.append(e)
    files += [("tracked", f) for f in tracked]
    if arm in ("all", "untracked"):
        un, e = _git_files(root, ["ls-files", "-z", "--others",
                                  "--exclude-standard"])
        if e:
            notes.append(e)
        files += [("untracked", f) for f in un if PROSE.search(f)]
    if arm in ("all", "ignored"):
        ig, e = _git_files(root, ["ls-files", "-z", "--others", "--ignored",
                                  "--exclude-standard"])
        if e:
            notes.append(e)
        files += [("gitignored", f) for f in ig if PROSE.search(f)]
    if arm == "untracked":
        files = [f for f in files if f[0] != "tracked"]
    if arm == "ignored":
        files = [f for f in files if f[0] != "tracked"]
    for er in extra_roots:
        base = Path(er)
        if not base.is_dir():
            notes.append(f"extra root not a directory: {er}")
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d != ".git"]
            for fn in filenames:
                if PROSE.search(fn):
                    files.append(("run-tree",
                                  str(Path(dirpath, fn))))
    return files, notes


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="check_summary_consistency",
        description="Grade a summary region against the section it summarises, "
                    "inside one document. Docket D141.")
    ap.add_argument("--root", default=str(REPO))
    ap.add_argument("--arm", default="tracked",
                    choices=("tracked", "untracked", "ignored", "all"))
    ap.add_argument("--extra-root", action="append", default=[],
                    help="a directory outside the repo (the run tree)")
    ap.add_argument("--verbose", action="store_true",
                    help="print every pair and its grade, not only the hits")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    bad_controls, control_log = run_controls()

    files, notes = enumerate_corpus(root, args.arm, args.extra_root)
    opened, unreadable, oversize, generated = [], [], [], []
    pairs = []
    n_sections = n_summaries = n_unresolved = n_loose = 0

    for label, rel in files:
        p = Path(rel) if label == "run-tree" else root / rel
        if cdf.GENERATED_HTML.search(rel):
            generated.append(rel)
            continue
        try:
            data = p.read_bytes()
        except OSError as exc:
            unreadable.append(f"{rel}: {exc}")
            continue
        if len(data) > cdf.MAX_BYTES:
            oversize.append(f"{rel} ({len(data) // 1024} KiB)")
            continue
        try:
            raw = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            unreadable.append(f"{rel}: not UTF-8 ({exc.reason})")
            continue
        if looks_minified(raw):
            generated.append(rel)
            continue
        opened.append(rel)
        ps, ns, nu, unres, loose, _ = grade_document(raw, rel)
        pairs += ps
        n_sections += ns
        n_summaries += nu if False else nu
        n_unresolved += unres
        n_loose += loose

    by = {g: [p for p in pairs if p.grade == g]
          for g in ("DISAGREE", "AGREE", "UNDECIDABLE", "EXEMPT")}
    graded = by["DISAGREE"] + by["AGREE"]

    reasons = []
    if bad_controls:
        verdict = UNKNOWN
        reasons += [f"control misfired: {b}" for b in bad_controls]
    elif not opened:
        verdict = UNKNOWN
        reasons.append("zero documents opened -- an instrument that read "
                       "nothing has cleared nothing (defect class B1)")
    elif not pairs:
        verdict = UNKNOWN
        reasons.append("zero summary/section pairs found -- nothing was "
                       "compared, so nothing is cleared (defect class B1)")
    elif not graded:
        verdict = UNKNOWN
        reasons.append(f"{len(pairs)} pairs found and NONE was gradeable -- an "
                       f"instrument that compared nothing has cleared nothing "
                       f"(defect class B1)")
    elif by["DISAGREE"]:
        verdict = FAIL
        reasons.append(f"{len(by['DISAGREE'])} summary region(s) disagree with "
                       f"the section they summarise")
    else:
        verdict = PASS
        reasons.append(f"{len(graded)} pair(s) graded, all agreeing; "
                       f"{len(by['UNDECIDABLE'])} not gradeable")

    out = []
    out.append("=" * 78)
    out.append("SUMMARY-CONSISTENCY CHECK -- a claim against its own "
               "restatement, in one document")
    out.append("  (docket D141; byte-identity decides nothing, so no diff is "
               "consulted anywhere)")
    out.append("=" * 78)
    out.append("")
    out.append("FRAME -- what was looked at, and how the pairs were found")
    out.append(f"  repo                {root}")
    out.append(f"  arm                 {args.arm}"
               + (f" + {len(args.extra_root)} extra root(s)"
                  if args.extra_root else ""))
    out.append("  enumeration         git ls-files (-z) + os.walk. NOT the "
               "shell's grep (it execs")
    out.append("                      ugrep --ignore-files and honours "
               ".gitignore) and NOT find (it is bfs)")
    out.append(f"  documents considered {len(files)}")
    out.append(f"  documents opened     {len(opened)}")
    out.append(f"  not opened           {len(generated) + len(oversize) + len(unreadable)}"
               f"  ({len(generated)} generated report HTML, "
               f"{len(oversize)} over {cdf.MAX_BYTES // 1000} kB, "
               f"{len(unreadable)} unreadable)")
    out.append(f"  headings indexed     {n_sections}")
    kinds = {}
    for p in pairs:
        kinds[p.kind] = kinds.get(p.kind, 0) + 1
    out.append(f"  pairs FOUND          {len(pairs)}   "
               f"-- three structural rules, no list anywhere:")
    out.append("                         table row whose LEADING CELL is a "
               "section id      "
               f"{kinds.get('table-row', 0)}")
    out.append("                         table row whose leading cell is the "
               "HEADING STRING  "
               f"{kinds.get('table-row/heading-string', 0)}")
    out.append(f"                         bullet naming a section in its "
               f"first {BULLET_HEAD_CHARS} chars      "
               f"{kinds.get('bullet', 0)}")
    out.append(f"  references dropped   {n_unresolved}  (named an identifier "
               f"no heading in the SAME document answers to)")
    out.append("")
    out.append("  pairs GRADED         "
               f"{len(graded)}   ({len(by['AGREE'])} agree, "
               f"{len(by['DISAGREE'])} disagree)")
    out.append(f"  pairs EXEMPT         {len(by['EXEMPT'])}   (the summary's "
               f"verdict word is struck / kept-as-record -- a struck row is a")
    out.append("                       legitimate historical record and "
               "flagging it teaches readers to ignore this check)")
    out.append(f"  pairs UNDECIDABLE    {len(by['UNDECIDABLE'])}   "
               f"-- by reason:")
    tally = {}
    for p in by["UNDECIDABLE"]:
        key = p.reason.split(" -- ")[0].split(":")[0]
        tally[key] = tally.get(key, 0) + 1
    for k, v in sorted(tally.items(), key=lambda kv: -kv[1]):
        out.append(f"                         {v:5d}  {k}")
    out.append("")
    out.append("WHAT THIS GRADES, AND WHAT IT DOES NOT")
    out.append("  GRADED    ALL-CAPS verdict word, summary against section "
               "heading:")
    out.append(f"              AFFIRM {'/'.join(AFFIRM)}   "
               f"DENY {'/'.join(DENY)}   NEUTRAL {'/'.join(NEUTRAL)}")
    out.append("            a hit is AFFIRM-over-DENY or DENY-over-AFFIRM. "
               "NEUTRAL or mixed is UNDECIDABLE.")
    out.append("  GRADED    the section's STATUS MARKER, via "
               "check_derived_figures._STRUCK_HEAD (imported):")
    out.append("            a heading declaring itself STRUCK / WITHDRAWN / "
               "SUPERSEDED / RETRACTED / FALSIFIED counts DENY.")
    out.append("  NOT GRADED  figures. A row and its section state different "
               "numbers about different things;")
    out.append("            pairing them needs an anchor match, which is "
               "check_derived_figures' own job against")
    out.append("            MACHINE RECORDS -- a stronger comparison than "
               "row-against-section. Stated, not shipped.")
    out.append(f"  NOT GRADED  lowercase verdict words. {n_loose} pair(s) "
               f"would become candidates under the loose rule;")
    out.append("            `the rule holds` in prose is a verb, and admitting "
               "it added no true positive here.")
    out.append("")
    out.append("CONTROLS -- both halves, in-process, every run (L-84)")
    for ln in control_log:
        out.append("  " + ln)
    out.append("  (N1 is the important one: those ten rows were "
               "BYTE-IDENTICAL to the stale row's provenance")
    out.append("   and STILL RIGHT. A check that fires on them is measuring "
               "byte-identity, which decides nothing.)")
    out.append("")
    if by["DISAGREE"]:
        out.append(f"HITS -- {len(by['DISAGREE'])} summary region(s) "
                   f"contradicting their own section")
        for p in sorted(by["DISAGREE"], key=lambda q: (q.path, q.sum_line)):
            out.append(f"  {p.path}:{p.sum_line + 1}  [{p.kind}] -> "
                       f"section {p.ident!r} at :{p.sec_line + 1}")
            out.append(f"      {p.reason}")
            out.append(f"      summary  {p.excerpt[:160]}")
            out.append(f"      section  {p.head}")
        out.append("")
    if args.verbose:
        out.append("EVERY PAIR")
        for p in sorted(pairs, key=lambda q: (q.grade, q.path, q.sum_line)):
            out.append(f"  {p.grade:12s} {p.path}:{p.sum_line + 1} "
                       f"-> :{p.sec_line + 1}  {p.ident!r}  {p.reason}")
        out.append("")
    if unreadable:
        out.append("UNREADABLE (named, not swallowed)")
        for u in unreadable[:20]:
            out.append("  " + u)
        out.append("")
    for n in notes:
        out.append("NOTE  " + n)
    out.append("BLIND TO -- read this before reading the verdict")
    out.append("  * a summary that names its section only in PROSE ('as "
               "section 4.8 found, ...') is not paired:")
    out.append("    the leading-cell rule is what distinguishes a summary "
               "from a citation.")
    out.append("  * a stale summary whose section carries no verdict word is "
               "UNDECIDABLE, not clean. Most are.")
    out.append("  * a summary of a section in a DIFFERENT document. The unit "
               "here is one document, deliberately.")
    out.append("  * whether the section itself is true. This grades a "
               "restatement against a heading, nothing more.")
    out.append("")
    for r in reasons:
        out.append("  " + r)
    out.append(f"VERDICT: {verdict}")

    if args.json:
        print(json.dumps({
            "check": "summary_consistency",
            "verdict": verdict,
            "reasons": reasons,
            "documents_considered": len(files),
            "documents_opened": len(opened),
            "pairs_found": len(pairs),
            "pairs_graded": len(graded),
            "agree": len(by["AGREE"]),
            "disagree": len(by["DISAGREE"]),
            "exempt": len(by["EXEMPT"]),
            "undecidable": len(by["UNDECIDABLE"]),
            "undecidable_by_reason": tally,
            "controls_bad": bad_controls,
            "hits": [dataclasses.asdict(p) for p in by["DISAGREE"]],
        }, indent=2))
    else:
        print("\n".join(out))
    return EXIT[verdict]


if __name__ == "__main__":
    sys.exit(main())
