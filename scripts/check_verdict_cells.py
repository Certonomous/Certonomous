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
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "demo-output/website/campaign/LADDER_V_TRIPLE_VERIFICATION.md"
CAMPAIGN = REPO / "demo-output/website/campaign"

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
    out = []
    for p in sorted(CAMPAIGN.glob("*.md")):
        if not pat.search(p.name):
            continue
        if p in cited:
            continue
        if _landed(p) > newest_cited:
            out.append(p)
    return out


def _landed(p: Path) -> int:
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", str(p)],
            cwd=REPO, capture_output=True, text=True, timeout=30,
        ).stdout.strip()
        return int(out) if out else 0
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


def record_verdict(path: Path) -> str | None:
    """The verdict a grade record states about itself.

    Anchored on the word "verdict" and searched in a WINDOW after it, because
    records do not agree on shape: one writes ``**Verdict: `PASS`.**``, another
    ``## VERDICT`` with the label on a later line, a third ``**Verdict: V8
    FAILS**`` with a rung name interposed and the verb inflected. A pattern
    demanding the label immediately after the colon reads two of those three as
    verdict-less.
    """
    try:
        head = path.read_text(errors="replace")[:8000]
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
        try:
            out = subprocess.run(
                ["git", "log", "-1", "--format=%ct", "--", str(p)],
                cwd=REPO, capture_output=True, text=True, timeout=30,
            ).stdout.strip()
            if out:
                return (1, int(out), p.name)
        except (OSError, ValueError, subprocess.SubprocessError):
            pass
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
        missed = uncited_newer(row.rung, cited)
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

    total = len(plants) + len(negatives) + len(shapes)
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
