#!/usr/bin/env python3
r"""Does each Ladder V verdict cell still say what its own grade record says.

WHY THIS EXISTS (docket D338; third instance on one table)
==========================================================
The status ledger in `demo-output/website/campaign/LADDER_V_TRIPLE_VERIFICATION.md`
is hand-maintained, and it rots SILENTLY, because nothing reads a verdict cell
back against the record it names. Three instances, all found by a rung rather
than by a check:

    V13's unpark finding   The table described six rungs as "waits for unpark"
                           after they had executed.
    V15 round 9, F2        The V15 row stopped at round 7 while two further
                           rounds ran, and the file was edited ten times after
                           round 8 landed without absorbing it.
    D338, 2026-08-17       V9 read `FAIL -> FIXED` and V12 read `DELIVERED`
                           while both rungs had been graded PASS by non-authors
                           the day before.

The third instance carried a second fault the first two did not. `FIXED` and
`DELIVERED` are not verdicts. The vocabulary is fixed at
`docs/charters/VERIFICATION_CHARTER.md:95-96` and restated at
`docs/charters/REPORTING_CHARTER.md:210-211`, and section 16's negative-verdict
sweep (`VERIFICATION_CHARTER.md:1390-1393`) works BY ENUMERATING IT: it can find
the FAILs because the set is enumerable. A cell holding a word outside the
vocabulary is therefore invisible to that sweep BY CONSTRUCTION -- the same
structural ground on which `PASS WITH EXCEPTIONS` and `PASS WITH RESIDUALS` were
withdrawn (D249, `7c44cbe2`).

And the shape D338 exposed is worse than staleness: `ad4d2315` wrote a PASS into
the row's CONFIRMATION column and left the VERDICT column reading `DELIVERED`,
so the row contradicted itself across its own two cells. A per-cell reading
cannot see that. It lives in the agreement between cells, which is the same
lesson V10 took five grades to learn: a per-site check cannot see a defect that
lives in the agreement between sites.

WHAT THIS MODULE DOES NOT DO
============================
It does not grade a rung and it does not decide whether a verdict is correct.
It asks one question only: does the cell agree with the record it cites, and is
the word it uses a verdict at all. A rung's correctness is a grader's job.

THE ONE DISCREPANCY IT REFUSES TO RESOLVE
=========================================
The charter vocabulary says **GATE FAIL**. Every rung cell says bare **FAIL**.
Both readings are defensible -- a ladder rung is a gate, or it is not -- and
picking one here would encode a ruling in an instrument rather than in a
charter. So bare FAIL is accepted and REPORTED, under `--strict-fail`, as a
question for a ruling. An instrument that silently resolves an ambiguity is
worse than one that names it.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

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

REPO = Path(__file__).resolve().parent.parent
LEDGER = lab_paths.CAMPAIGN / "LADDER_V_TRIPLE_VERIFICATION.md"
CAMPAIGN = lab_paths.CAMPAIGN

# VERIFICATION_CHARTER.md:95-96, REPORTING_CHARTER.md:210-211, plus PENDING for
# a row whose act has not run (REPORTING_CHARTER.md:206). Longest first, so
# "GATE FAIL" is never truncated to "FAIL" by an earlier alternative.
VOCABULARY = [
    "NOT A RESULT",
    "GATE REACHED",
    "GATE FAIL",
    "BLOCKED",
    "PENDING",
    "PASS",
    "FAIL",
]

# Labels known to have been used in a verdict cell and known not to be verdicts.
# Each earned its place by appearing in a shipped cell.
KNOWN_ILLEGAL = [
    "PASS WITH EXCEPTIONS",
    "PASS WITH RESIDUALS",
    "INDETERMINATE",
    "DELIVERED",
    "FIXED",
]

# Uppercase runs that are prose, not labels. Kept deliberately short: anything
# not listed is REPORTED as unknown rather than assumed harmless.
NOT_A_LABEL = {
    "YES", "NO", "AND", "OR", "NOT", "BUT", "THE", "ALL", "TRUE", "FALSE",
    "WITHDRAWN", "STRUCK", "OPEN", "CLOSED", "HOLDS", "NONE", "NEW", "ONE",
    "TWO", "ZERO", "HEAD", "PDF", "CSV", "JSON", "ID", "IDS", "SHA",
}

_ALT = "|".join(
    l.replace(" ", r"\s+") for l in sorted(VOCABULARY + KNOWN_ILLEGAL, key=len, reverse=True)
)
# The inflection tail is not decoration. `LADDER_V_V8_REVERIFICATION_2026-08-14.md`
# states `**Verdict: V8 FAILS**`, and a pattern anchored on the bare lemma reads
# that record as stating no verdict at all. One inflected verb has produced a
# false zero in this lab before.
LABEL_RE = re.compile(r"\b(" + _ALT + r")(?:E?[SD])?\b")
VERDICT_ANCHOR_RE = re.compile(r"verdict", re.IGNORECASE)
# The withdrawal narrative in a repaired cell is an italic parenthetical, and it
# NAMES the label it is withdrawing. Those names are mentions, not uses.
GROUNDS_RE = re.compile(r"\*\((.*?)\)\*", re.S)
QUOTED_RE = re.compile(r"\"(.*?)\"|“(.*?)”", re.S)
# How far into a bold span a label may sit and still count as ASSERTED rather
# than mentioned. "round 9 FAIL" puts it at 8; V12's closing span mentions its
# labels well past any such opening.
ASSERTION_WINDOW = 40
DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
RECORD_RE = re.compile(r"`([A-Za-z0-9_./-]+\.md)`")
UPPER_RUN_RE = re.compile(r"\b[A-Z][A-Z ]{2,}[A-Z]\b|\b[A-Z]{3,}\b")


def blank_code_spans(text: str) -> str:
    """Overwrite backtick-span CONTENTS with spaces, offsets preserved.

    Used ONLY for strike-marker detection. A ``~~`` written inside a code span is
    a MENTION -- the V12 cell discusses "34 ``~~`` markers" -- and counting it as
    a marker opens a strike span that swallows live text. It must NOT be used for
    verdict extraction, because every verdict in this corpus is written inside
    backticks and blanking them would erase the thing being measured. Two
    questions, two preprocessings.
    """
    out = list(text)
    for m in re.finditer(r"(`+)(.*?)(\1)", text, re.S):
        for i in range(m.start(2), m.end(2)):
            if out[i] != "\n":
                out[i] = " "
    return "".join(out)


def strike_spans(text: str) -> list[tuple[int, int]]:
    """Ranges covered by a strike, found on code-span-blanked text.

    Markers are located on the blanked copy so mentions cannot open a span, but
    the ranges returned index the ORIGINAL string.
    """
    probe = blank_code_spans(text)
    spans: list[tuple[int, int]] = []
    for m in re.finditer(r"~~(.*?)~~", probe, re.S):
        spans.append((m.start(), m.end()))
    for tag in ("s", "del"):
        for m in re.finditer(rf"<{tag}>(.*?)</{tag}>", probe, re.S | re.I):
            spans.append((m.start(), m.end()))
    return spans


def blank_strikes(text: str) -> str:
    """Overwrite struck spans with spaces, same length, newlines untouched."""
    out = list(text)
    for lo, hi in strike_spans(text):
        for i in range(lo, hi):
            if out[i] != "\n":
                out[i] = " "
    return "".join(out)


def strike_balance(text: str) -> int:
    """Unclosed ``~~`` openers, counted on code-span-blanked text."""
    return blank_code_spans(text).count("~~") % 2


def labels_in(text: str) -> list[tuple[int, str]]:
    """(offset, canonical label) for every label, inflection tolerated."""
    return [(m.start(), re.sub(r"\s+", " ", m.group(1)).upper()) for m in LABEL_RE.finditer(text)]


def blank_mentions(text: str) -> str:
    """Blank the spans where a label is NAMED rather than ASSERTED.

    Two spans, both offset-preserving. The italic parenthetical carries a
    repair's grounds, and a repair's grounds necessarily quote the label being
    withdrawn -- the V9 cell names `FIXED`, `PASS WITH EXCEPTIONS` and `PASS
    WITH RESIDUALS` precisely to say that none of them is a verdict. Reading
    those as uses convicts the cell of the defect it just repaired. The same
    goes for a label inside quotation marks.

    What this CANNOT do is blank a mention written in bare prose with no
    parenthetical and no quotes. That is this instrument's blind class and it is
    named in the report rather than left implicit.
    """
    out = list(text)
    for rx in (GROUNDS_RE, QUOTED_RE):
        for m in rx.finditer(text):
            for g in range(1, (m.re.groups or 0) + 1):
                if m.group(g) is None:
                    continue
                for i in range(m.start(g), m.end(g)):
                    if out[i] != "\n":
                        out[i] = " "
    return "".join(out)


def operative_label(cell_live: str) -> str | None:
    """The verdict the cell ASSERTS, as opposed to every label it contains.

    Two readings were tried and both were wrong, in opposite directions:

        LAST LABEL IN THE CELL     reads V12 as FAIL, because that cell closes
                                   by naming the prior `FAIL` its non-author
                                   grade overturned.
        FIRST LABEL AFTER THE LAST
        ARROW                      reads V7 as FAIL, because that cell appends
                                   each successive grade with an EM-DASH, not
                                   an arrow, so the last arrow sits before a
                                   2026-08-16 FAIL and three later grades --
                                   including the PASS -- follow it.

    What actually marks an assertion in this house style is a BOLD SPAN that
    OPENS on its verdict. A label mentioned in passing sits mid-clause or
    outside bold entirely. So: the last bold span whose first label falls within
    its opening, and the label is that one.
    """
    text = blank_mentions(cell_live)
    best: str | None = None
    for m in re.finditer(r"\*\*(.+?)\*\*", text, re.S):
        span = m.group(1)
        found = labels_in(span)
        if found and found[0][0] <= ASSERTION_WINDOW:
            best = found[0][1]
    if best:
        return best
    found = labels_in(text)
    return found[-1][1] if found else None


def uncited_newer(rung: str, cited: list[Path]) -> list[Path]:
    """Records for this rung that landed AFTER the newest one the cell cites.

    THIS CLOSES THE INSTRUMENT'S ORIGINAL BLIND SPOT, and it was found by a
    grader rather than by the author. The cell-versus-record check compares
    against the newest record the cell NAMES, so a cell that simply fails to
    name a newer grade passes it silently. That is not hypothetical: on
    2026-08-17 the V8 row recorded a 2026-08-15 PASS while a GATE FAIL and its
    repair had both landed since, and this checker reported the row clean
    because the newer records were nowhere in the cell to be compared against.

    A check whose blind class is "the thing it is supposed to detect, when the
    author omits the citation" is worth very little, since omission is exactly
    what staleness looks like.
    """
    m = re.match(r"(V\d{1,2})\b", rung)
    if not m:
        return []
    tag = m.group(1)
    pat = re.compile(rf"(?:^|[_-]){tag}(?:[_-]|\.)")
    newest_cited = _landed(cited[-1]) if cited else 0
    out: list[Path] = []
    skipped: list[str] = []
    for p in sorted(CAMPAIGN.glob("*.md")):
        if not pat.search(p.name) or p in cited:
            continue
        if _landed(p) <= newest_cited:
            continue
        ok, why = is_grade_record(p)
        if ok:
            out.append(p)
        else:
            skipped.append(f"{p.name} ({why})")
    return out, skipped


def _history_spellings(p: Path) -> list[str]:
    """Every name this repository has had, or will have, for one path.

    A MOVE RE-DATES A RECORD FOR ANY INSTRUMENT THAT READS HISTORY BY PATH, and
    that is the same defect `_landed` below was written to close, arriving by a
    different door.  `git log --diff-filter=A -- <path>` reports a RENAME as an
    ADD at the new path, so MOVE_MAP batch 7 (R21) would have re-dated all 264
    campaign records to the move commit and, in the window between the `git mv`
    and the commit, returned NO history at all -- `_landed` fell back to 0,
    every record read as newer than every other, and this check went
    PASS -> FAIL with two CELL-VS-RECORD findings that are artefacts of the
    move rather than of the ledger.

    The fix is the one `sdk/chief_engineer/exec_bits.py:_spellings` already
    uses: teach the MATCH the map instead of re-writing history.  The EARLIEST
    add across every spelling is taken, which is the same rule the docstring
    below already states for a path added more than once.
    """
    out = [str(p)]
    try:
        rel = str(Path(p).resolve().relative_to(REPO))
    except ValueError:
        return out
    for other in (lab_paths.unredirect(rel), lab_paths.redirect(rel)):
        if other:
            cand = str(REPO / other)
            if cand not in out:
                out.append(cand)
    return out


def _landed(p: Path) -> int:
    """When this grade LANDED -- the commit that ADDED it, not the last to touch it.

    THIS WAS WRONG AND A GRADER'S OWN COMMIT PROVED IT (2026-08-17, D356).
    `git log -1` returns the most recent commit touching the path, which is the
    last EDIT, not the landing. The two are the same only until somebody amends a
    grade record -- and amending one is exactly what this instrument's own
    findings ask for. On 2026-08-17 a non-author amended the withdrawn label in
    `LADDER_V_V6_V10_REGRADE_2026-08-15.md` and
    `LADDER_V_V12_V13_V14_GRADE_2026-08-15.md`, and both files instantly read as
    though they had been GRADED that afternoon. Three rungs the amendment never
    touched -- V10, V12 and V14 -- were reported stale or contradicted against
    2026-08-15 grades that had not moved, and V14's cell was convicted of
    disagreeing with a record that agrees with it. **Repairing a record must not
    re-date it**, or the instrument punishes the repair it asked for.

    The ledger already uses the word this way and is the reason it is decidable:
    its cells read *"landed `60073572`"* and `60073572` is the ADD commit at
    19:34:11Z, not the amendment at 19:34:20Z two days later. So this is the
    corpus's own sense of "landed", not a new convention invented here.
    """
    try:
        adds = []
        for spelling in _history_spellings(p):
            out = subprocess.run(
                ["git", "log", "--diff-filter=A", "--format=%ct", "--", spelling],
                cwd=REPO, capture_output=True, text=True, timeout=30,
            ).stdout.split()
            if out:
                adds.append(int(out[-1]))  # earliest ADD at this spelling
        if adds:
            return min(adds)               # ...and the earliest across spellings
        # No add commit in history (a path only ever modified, or unreadable
        # history): fall back to last-touch rather than silently returning 0,
        # which would make every record for the rung look newer than it.
        lasts = []
        for spelling in _history_spellings(p):
            last = subprocess.run(
                ["git", "log", "-1", "--format=%ct", "--", spelling],
                cwd=REPO, capture_output=True, text=True, timeout=30,
            ).stdout.strip()
            if last:
                lasts.append(int(last))
        return min(lasts) if lasts else 0
    except (OSError, ValueError, subprocess.SubprocessError):
        return 0


@dataclass
class Row:
    rung: str
    line_no: int
    verdict_cell: str
    confirm_cell: str
    findings: list[tuple[str, str, str]] = field(default_factory=list)

    def add(self, tier: str, code: str, msg: str) -> None:
        self.findings.append((tier, code, msg))


def parse_rows(ledger_text: str) -> list[Row]:
    rows: list[Row] = []
    for i, line in enumerate(ledger_text.splitlines(), start=1):
        m = re.match(r"^\|\s*(V\d{1,2})\b([^|]*)\|(.*)\|([^|]*)\|\s*$", line)
        if not m:
            continue
        cells = line.split("|")
        if len(cells) < 4:
            continue
        rows.append(
            Row(
                rung=(m.group(1) + m.group(2)).strip(),
                line_no=i,
                verdict_cell=cells[2],
                confirm_cell=cells[3],
            )
        )
    return rows


# A document can be named for a rung, sit in the campaign directory, and still
# not be a grade of it. `V16_C4_AMENDMENT_PROPOSAL.md` says so on its own face:
# NOT IN FORCE, FORWARD ONLY, and it regrades nothing. Binding records to rungs
# by FILENAME alone made this checker report that the V16 cell disagreed with a
# document that decides nothing about V16 -- a false FAIL, and the same
# use-versus-mention failure one level up: a file ABOUT a rung is not a VERDICT
# on it. The same defect is latent on V2, where a case file `DPW8_V2_joukowski.md`
# matches the V2 pattern.
NOT_A_GRADE_RE = re.compile(
    r"\bNOT\s+IN\s+FORCE\b|\bFORWARD[- ]ONLY\b|\bPROPOSAL\b|"
    r"\bdoes\s+not\s+re-?grade\b|\bgrades\s+no\s+rung\b",
    re.IGNORECASE,
)


def is_grade_record(path: Path) -> tuple[bool, str]:
    """Is this a grade of a rung, or merely a document naming one.

    Returns (verdict, reason). Exclusions are REPORTED, never silent: a control
    that drops a case without saying so is how K0c's C5 witness list hid two
    missing rows, and 'failed the criterion' became indistinguishable from 'was
    never considered'.
    """
    try:
        head = path.read_text(errors="replace")[:4000]
    except OSError:
        return False, "unreadable"
    m = NOT_A_GRADE_RE.search(head)
    if m:
        return False, f"declares itself {m.group(0).strip()!r}"
    if record_verdict(path) is None:
        return False, "states no verdict"
    return True, ""


def record_verdict(path: Path) -> str | None:
    """The verdict a grade record states about itself.

    Anchored on the word "verdict" and searched in a WINDOW after it, because
    records do not agree on shape: one writes ``**Verdict: `PASS`.**``, another
    ``## VERDICT`` with the label on a later line, a third ``**Verdict: V8
    FAILS**`` with a rung name interposed and the verb inflected. A pattern
    demanding the label immediately after the colon reads two of those three as
    verdict-less.

    Read WHOLE, not a head window. An 8,000-byte window reported four real grade
    records as stating no verdict, because they state it past that point. A
    reader that gives up early and a document that says nothing produce the same
    output, which is the truncation failure this lab has now met in four guises.
    """
    try:
        head = path.read_text(errors="replace")
    except OSError:
        return None
    for anchor in VERDICT_ANCHOR_RE.finditer(head):
        window = head[anchor.end():anchor.end() + 300]
        found = labels_in(window)
        if found:
            return found[0][1]
    return None


def newest_cited(cell: str) -> list[Path]:
    """Cited .md records that exist under campaign/, newest-dated last."""
    names = [n.split("/")[-1] for n in RECORD_RE.findall(cell)]
    paths = []
    for n in dict.fromkeys(names):
        p = CAMPAIGN / n
        if p.exists():
            paths.append(p)

    def key(p: Path):
        """Landing date from git, NOT from the filename.

        Most V15 round records carry no date in their name, so a filename sort
        degenerates to an alphabetical one and calls `V15_ROUND5_...` newer than
        `LADDER_V_V15_ROUND10.md` -- five rounds and two days wrong, and it
        convicted the V15 cell on the strength of it. Git knows when the file
        landed; the filename only knows how it was typed. Filename date is the
        fallback for a record git has never seen.
        """
        ts = _landed(p)
        if ts:
            return (1, ts, p.name)
        d = DATE_RE.search(p.name)
        return (0, d.group(0) if d else "", p.name)

    return sorted(paths, key=key)


def check(strict_fail: bool, ledger_text: str | None = None) -> list[Row]:
    text = ledger_text if ledger_text is not None else LEDGER.read_text(errors="replace")
    rows = parse_rows(text)
    for row in rows:
        live = blank_strikes(row.verdict_cell)
        live_confirm = blank_strikes(row.confirm_cell)

        if strike_balance(row.verdict_cell):
            row.add("FAIL", "STRIKE-BALANCE",
                    "verdict cell has an unclosed ~~ opener; a span may be "
                    "swallowing live text")

        # C1 -- is the word the cell ASSERTS a verdict at all. Scoped to the
        # operative label only: a repaired cell necessarily names the illegal
        # label it withdrew, and firing on every occurrence convicts the repair.
        operative = operative_label(live)
        if operative is None:
            row.add("FAIL", "NO-VERDICT", "no verdict label in the live cell")
        elif operative in KNOWN_ILLEGAL:
            row.add("FAIL", "ILLEGAL-LABEL",
                    f"the cell asserts {operative!r}, which is not in the verdict "
                    f"vocabulary and is invisible to section 16's sweep by "
                    f"construction")

        if strict_fail and operative == "FAIL":
            row.add("QUERY", "BARE-FAIL",
                    "cell says FAIL; the charter vocabulary says GATE FAIL. "
                    "Not resolved here -- this needs a ruling, not an instrument")

        # C4 / C2 -- does the cell agree with the record it cites
        cited = newest_cited(live)
        if not cited:
            named = RECORD_RE.findall(live)
            if named:
                row.add("WARN", "RECORD-MISSING",
                        f"cites {len(named)} record name(s), none resolve under "
                        f"campaign/: {', '.join(n.split('/')[-1] for n in named[:3])}")
        else:
            newest = cited[-1]
            stated = record_verdict(newest)
            if stated is None:
                row.add("WARN", "RECORD-UNREADABLE",
                        f"{newest.name} states no verdict this reader can find")
            elif operative and stated != operative:
                row.add("FAIL", "CELL-VS-RECORD",
                        f"cell says {operative}; its newest cited record "
                        f"{newest.name} says {stated}")

        # The blind spot a grader found: a cell cannot disagree with a record
        # it never names, so staleness by OMISSION passed silently until now.
        #
        # A cell citing NOTHING is a separate finding and must not be reported
        # as this one. With no citation the newest-cited timestamp is zero, so
        # every record for the rung dates "after" it and the row reads as
        # eleven-deep stale when the true defect is that it names no source at
        # all. Reporting the wrong one sends the repair to the wrong place.
        missed, skipped = uncited_newer(row.rung, cited)
        if skipped:
            row.add("INFO", "NOT-A-GRADE",
                    f"{len(skipped)} newer file(s) named for this rung are not "
                    f"grades and were excluded: {'; '.join(skipped[:3])}")
        if not cited:
            n = len(missed)
            row.add("FAIL", "NO-CITATION",
                    f"cell names no grade record; {n} exist(s) for this rung"
                    if n else "cell names no grade record, and none was found")
        elif missed:
            names = ", ".join(p.name for p in missed[:3])
            more = f" (+{len(missed) - 3} more)" if len(missed) > 3 else ""
            verdicts = {record_verdict(p) for p in missed} - {None}
            row.add("FAIL", "UNCITED-NEWER",
                    f"{len(missed)} record(s) for this rung landed after the "
                    f"newest one the cell cites, saying "
                    f"{'/'.join(sorted(verdicts)) or 'no verdict found'}: "
                    f"{names}{more}")

        # C3 -- the intra-row contradiction ad4d2315 created. Heuristic by
        # construction: a confirmation column may legitimately narrate an
        # OVERTURNED earlier verdict, so this warns and quotes rather than fails.
        confirm_labels = {
            l for _, l in labels_in(blank_mentions(live_confirm)) if l in VOCABULARY
        }
        if operative and confirm_labels and operative not in confirm_labels:
            row.add("WARN", "INTRA-ROW",
                    f"verdict cell says {operative}; confirmation column states "
                    f"{'/'.join(sorted(confirm_labels))} -- read the row whole")
    return rows


# Three timestamps for the planted history below. Chosen far apart and in
# ascending order so that no coincidence between an ADD, a MOVE and an EDIT can
# make a wrong reduction rule look right -- the coincidence that made the
# corpus-side landing control vacuous is exactly what this must not reproduce.
PLANT_ADD_CT = 1600000000   # the true landing, at the ORIGINAL spelling
PLANT_MOVE_CT = 1700000000  # the rename: an ADD at the NEW spelling (R21 class)
PLANT_EDIT_CT = 1800000000  # a later amendment: last-touch (D356 class)


def plant_moved_history(root: Path) -> tuple[str, str]:
    """Build a throwaway repo whose one record was ADDED, MOVED, then EDITED.

    A landing reader that has never been shown a history in which the earliest
    add and the latest add DIFFER has not been shown able to see the re-dating
    defect at all -- it is the planted-zero rule applied to a timestamp. The
    corpus can supply such a history only by accident (it does today, because
    R21 moved these records), so the discriminating case is MANUFACTURED here
    and the control no longer depends on the corpus keeping it.

    Returns the two spellings, relative to `root`.
    """
    old_rel, new_rel = "legacy/GRADE.md", "successor/GRADE.md"
    env = dict(os.environ)
    env.update({
        # Neutralise every ambient config: a global hooksPath or a template dir
        # must not be able to reach into a control.
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_AUTHOR_NAME": "plant", "GIT_AUTHOR_EMAIL": "plant@invalid",
        "GIT_COMMITTER_NAME": "plant", "GIT_COMMITTER_EMAIL": "plant@invalid",
    })

    def git(*args: str, when: int | None = None) -> None:
        e = dict(env)
        if when is not None:
            # %ct, which `_landed` reads, is the COMMITTER date.
            e["GIT_AUTHOR_DATE"] = e["GIT_COMMITTER_DATE"] = f"{when} +0000"
        r = subprocess.run(["git", *args], cwd=root, env=e,
                           capture_output=True, text=True, timeout=60)
        if r.returncode:
            raise RuntimeError(f"git {' '.join(args)} -> rc={r.returncode}")

    (root / "legacy").mkdir(parents=True, exist_ok=True)
    (root / old_rel).write_text("**Verdict: `PASS`.**\n")
    git("init", "-q")
    git("add", "--", old_rel)
    git("commit", "-q", "-m", "add the grade", when=PLANT_ADD_CT)

    (root / "successor").mkdir(parents=True, exist_ok=True)
    git("mv", old_rel, new_rel)
    git("commit", "-q", "-m", "move the grade (R21 class)", when=PLANT_MOVE_CT)

    (root / new_rel).write_text("**Verdict: `PASS`.** (label amended)\n")
    git("add", "--", new_rel)
    git("commit", "-q", "-m", "amend the grade (D356 class)", when=PLANT_EDIT_CT)
    return old_rel, new_rel


def selftest() -> int:
    """Plant each defect class and require the checker to fire on it.

    This is a RECOGNITION control, not a reachability control. Proving the
    reader could open the ledger earns nothing; each plant is written in the
    defect's own vocabulary, and the struck plant must stay SILENT -- that is
    what proves the instrument distinguishes live text from withdrawn text.
    """
    base = LEDGER.read_text(errors="replace")
    plants = [
        ("ILLEGAL-LABEL",
         "| V1 clean-environment re-score | **DELIVERED** | YES |"),
        ("NO-VERDICT",
         "| V1 clean-environment re-score | looks fine to me | YES |"),
        ("CELL-VS-RECORD",
         "| V1 clean-environment re-score | **BLOCKED** "
         "(`LADDER_V_V15_ROUND10.md`) | YES |"),
        ("STRIKE-BALANCE",
         "| V1 clean-environment re-score | ~~**PASS** | YES |"),
    ]
    lines = base.splitlines()
    target = next(i for i, l in enumerate(lines) if re.match(r"^\|\s*V1\b", l))

    failures = 0
    for code, planted in plants:
        mutated = lines[:]
        mutated[target] = planted
        rows = check(False, "\n".join(mutated))
        v1 = next(r for r in rows if r.rung.startswith("V1"))
        codes = {c for _, c, _ in v1.findings}
        ok = code in codes
        print(f"  {'FIRED  ' if ok else 'SILENT '} plant {code:<16} "
              f"-> {sorted(codes) or 'nothing'}")
        failures += 0 if ok else 1

    # Negative controls. Each is a defect-shaped string that must NOT fire,
    # and each corresponds to a false positive this instrument actually
    # produced on its first live run.
    negatives = [
        ("struck",
         "| V1 clean-environment re-score | ~~**DELIVERED**~~ **PASS** | YES |"),
        ("mention-in-grounds",
         "| V1 clean-environment re-score | ~~**DELIVERED**~~ *(struck; "
         "`DELIVERED` is not a verdict, on the ground that withdrew \"PASS WITH "
         "RESIDUALS\")* **→ `PASS`** "
         "(`LADDER_V_V9_REGRADE_2026-08-16.md`) | YES |"),
        ("trailing-prior-verdict",
         "| V1 clean-environment re-score | **→ `PASS`** overturning the prior "
         "`FAIL` (`LADDER_V_V9_REGRADE_2026-08-16.md`) | YES |"),
    ]
    for name, planted in negatives:
        mutated = lines[:]
        mutated[target] = planted
        rows = check(False, "\n".join(mutated))
        v1 = next(r for r in rows if r.rung.startswith("V1"))
        codes = {c for _, c, _ in v1.findings}
        quiet = not ({"ILLEGAL-LABEL", "CELL-VS-RECORD"} & codes)
        print(f"  {'SILENT ' if quiet else 'FIRED  '} negative control {name:<22} "
              f"-> {sorted(codes) or 'nothing'}")
        failures += 0 if quiet else 1

    # Recognition control for the record reader: three real records, three
    # different shapes, one of them inflected.
    shapes = [
        ("LADDER_V_V8_REVERIFICATION_2026-08-14.md", "FAIL"),   # **Verdict: V8 FAILS**
        ("LADDER_V_V9_REGRADE_2026-08-16.md", "PASS"),          # **Verdict: `PASS`.**
        ("LADDER_V_V7_GRADE_5_2026-08-17.md", "PASS"),          # ## VERDICT / label below
    ]
    for name, want in shapes:
        got = record_verdict(CAMPAIGN / name)
        ok = got == want
        print(f"  {'READ   ' if ok else 'MISSED '} record shape {name[:38]:<40} "
              f"-> {got}")
        failures += 0 if ok else 1

    # Recognition controls for _landed. A control that merely proves `_landed`
    # returns a number earns nothing -- the OLD reader returned a number too,
    # and the wrong one. TWO defect classes must be discriminated and they pull
    # in OPPOSITE directions:
    #
    #   D356  re-dating by AMENDMENT  reads the last touch instead of the add.
    #   R21   re-dating by MOVE       reads the add at the NEW spelling, because
    #                                 `git log --diff-filter=A` reports a rename
    #                                 as an add there.
    #
    # `_landed`'s rule -- the EARLIEST ADD ACROSS SPELLINGS -- is the only one
    # that survives both, and it is the correct one: for
    # LADDER_V_V12_V13_V14_GRADE it returns 2026-08-15T21:00:12, matching the
    # record's own filename date. The control written here previously POOLED the
    # adds and demanded the LATEST, i.e. the move commit -- it demanded exactly
    # the defect `_history_spellings` exists to prevent. With one spelling the
    # two rules coincided and the disagreement was invisible; R21 broke the
    # coincidence and the control started failing a correct implementation. The
    # CONTROL was the wrong half. Both halves now state the same rule.
    #
    # (1) THE PLANTED HISTORY. Manufactured, so the discriminating case cannot
    #     be lost to corpus churn, and so a wrong rule has a wrong answer
    #     available to give: earliest add, latest add and last touch are three
    #     different planted timestamps.
    n_planted = 1
    plant_root = Path(tempfile.mkdtemp(prefix="check_verdict_cells_landing_")).resolve()
    saved_repo, saved_spellings = REPO, _history_spellings
    try:
        old_rel, new_rel = plant_moved_history(plant_root)
        # CURRENT SPELLING FIRST, exactly as `_history_spellings` orders them
        # (`out = [str(p)]`, then the map's alternates). Ordering is not
        # cosmetic: a reduction that takes `adds[0]` rather than the minimum
        # is a live defect class, and a plant that happened to list the oldest
        # spelling first would let it through.
        both = [str(plant_root / new_rel), str(plant_root / old_rel)]
        globals()["REPO"] = plant_root
        globals()["_history_spellings"] = lambda _p: both
        try:
            got = _landed(plant_root / new_rel)
        finally:
            globals()["REPO"] = saved_repo
            globals()["_history_spellings"] = saved_spellings
        ok = got == PLANT_ADD_CT
        tell = {PLANT_MOVE_CT: " -- reads the MOVE commit (R21 re-dating)",
                PLANT_EDIT_CT: " -- reads the last EDIT (D356 re-dating)"}
        print(f"  {'HELD   ' if ok else 'BROKE  '} landing control "
              f"{'planted moved+amended history':<38} "
              f"-> add={PLANT_ADD_CT} move={PLANT_MOVE_CT} "
              f"edit={PLANT_EDIT_CT} _landed={got}"
              f"{'' if ok else tell.get(got, ' -- reads none of the three planted commits')}")
        failures += 0 if ok else 1
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        # A control that cannot be built is a FAILURE, never a skip. Switching
        # itself off quietly is the disease, not the remedy.
        globals()["REPO"] = saved_repo
        globals()["_history_spellings"] = saved_spellings
        print(f"  BROKE   landing control {'planted moved+amended history':<38} "
              f"-> could not build the planted history: {exc}")
        failures += 1
    finally:
        shutil.rmtree(plant_root, ignore_errors=True)

    # (2) THE CORPUS CONTROLS. Same rule, asserted against real records.
    n_landing = 0
    for name in ("LADDER_V_V6_V10_REGRADE_2026-08-15.md",
                 "LADDER_V_V12_V13_V14_GRADE_2026-08-15.md"):
        p = CAMPAIGN / name
        # THE CONTROL READS THE SAME SPELLINGS `_landed` DOES.  Reading only the
        # literal path made this control print `SKIP ... no history` the moment
        # R21 moved the record -- a control switching itself off in the batch
        # that made it necessary.
        adds, lasts = [], []
        for spelling in _history_spellings(p):
            out = subprocess.run(["git", "log", "--diff-filter=A",
                                  "--format=%ct", "--", spelling], cwd=REPO,
                                 capture_output=True, text=True).stdout.split()
            if out:
                adds.append(int(out[-1]))   # earliest ADD at THIS spelling
            one = subprocess.run(["git", "log", "-1", "--format=%ct", "--",
                                  spelling], cwd=REPO, capture_output=True,
                                 text=True).stdout.strip()
            if one:
                lasts.append(int(one))
        if not adds or not lasts:
            print(f"  SKIP    landing control {name[:36]:<38} -> no history")
            continue
        earliest_add, latest_add = min(adds), max(adds)
        last_touch = max(lasts)
        # Vacuity is decided BEFORE the denominator moves. The old code counted
        # the control and THEN discovered it could not discriminate, so a
        # control that cannot fail was still scored as a control that passed.
        if earliest_add == latest_add == last_touch:
            print(f"  VACUOUS landing control {name[:36]:<38} -> earliest add "
                  f"== latest add == last touch; never moved, never amended, "
                  f"nothing to distinguish (NOT counted as a control)")
            continue
        n_landing += 1
        got = _landed(p)
        ok = got == earliest_add
        # A control blind to one of the two classes says so, rather than
        # letting a partial discrimination read as a full one.
        blind = " [blind to move-redating: only one spelling has an add]" \
            if earliest_add == latest_add else ""
        tell = ""
        if not ok:
            tell = (" -- reads the MOVE commit (R21 re-dating)" if got == latest_add
                    else " -- reads the last touch (D356 re-dating)" if got == last_touch
                    else " -- reads none of the record's own commits")
        print(f"  {'HELD   ' if ok else 'BROKE  '} landing control {name[:36]:<38} "
              f"-> earliest_add={earliest_add} latest_add={latest_add} "
              f"last_touch={last_touch} _landed={got} "
              f"(delta {last_touch - earliest_add}s the old reader would have "
              f"added){blind}{tell}")
        failures += 0 if ok else 1

    total = len(plants) + len(negatives) + len(shapes) + n_planted + n_landing
    print(f"\nselftest: {total - failures}/{total} controls correct")
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--strict-fail", action="store_true",
                    help="report bare FAIL against the charter's GATE FAIL")
    ap.add_argument("--selftest", action="store_true",
                    help="planted-error control test; earns the zero")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    rows = check(args.strict_fail)
    if not rows:
        print("FAIL: no rung rows parsed -- the table shape changed", file=sys.stderr)
        return 2

    n_fail = n_warn = n_query = 0
    for row in rows:
        if not row.findings:
            continue
        print(f"\n{row.rung}  (ledger line {row.line_no})")
        for tier, code, msg in row.findings:
            print(f"  {tier:<5} {code:<16} {msg}")
            n_fail += tier == "FAIL"
            n_warn += tier == "WARN"
            n_query += tier == "QUERY"

    print(f"\n{len(rows)} rung rows read. "
          f"{n_fail} FAIL, {n_warn} WARN, {n_query} QUERY.")
    print("Blind class: this reads the ledger's own table only. A verdict "
          "asserted in prose elsewhere, or a rung with no row at all, is "
          "invisible to it.")
    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
