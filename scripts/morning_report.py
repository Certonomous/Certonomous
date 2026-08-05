#!/usr/bin/env python3
"""Validate a morning report against the frame in REPORTING_CHARTER section 2.

WHY THIS EXISTS. The charter names six sections and, until this file, gave
nobody a way to tell a report that skipped one from a report with nothing to
say. Section 12 said so out loud: "the frame in section 2 is unchecked until
the checker below exists". This is that checker, and it is deliberately the
smaller half of the old generator proposal: it reads a report a human wrote by
hand this morning and needs no emitter to exist first.

WHAT IT CHECKS, and each finding names the charter rule it comes from.

  Header    The opening block: the title line, `Date:` as YYYY-MM-DD,
            `Assembled:` as a UTC timestamp, `Sections: N of 6`, `Missing:`.
  Rule 1    The six headings are fixed strings, matched literally, once each,
            in order.
  Rule 2    Nothing is added at the top level. A seventh heading is a fault,
            not a bonus.
  Rule 3    `Sections: N of 6` is recounted from the headings rather than
            believed, and `Missing:` must name exactly the absent sections.
  Rule 4    An empty section prints the single reserved word `nothing`.
  Rule 5    An unreadable source prints `PENDING: <path>` and nothing else.
  Rule 6    Every section carrying content ends with a `Source:` line of
            repository-relative paths.
  Rule 7    A cited artifact that is not on disk is a finding in the report.

TWO READINGS THIS FILE MAKES, stated because the charter does not spell them
out and a checker cannot stay silent about its own interpretation:

  * A `nothing` section still needs its `Source:` line. Rule 4 defines the word
    to mean "the section was assembled, its source was read, and there was
    nothing in it", and the only evidence for "its source was read" is the line
    naming the source.
  * A `PENDING` section does not. Rule 5 says the token prints "and nothing
    else", and the point of the token is that the source could not be read, so
    demanding a `Source:` line under it would demand the thing that failed.

EXIT CODES. 0 clean; 1 the report is malformed against the frame; 2 the frame
holds but the report cites at least one artifact that is not on disk.

  python3 scripts/morning_report.py --check <report>

THE EMITTER, added 2026-08-04, the larger half of P-8.1. `--emit` assembles
the six sections from the named sources and writes one file per morning under
the campaign, then runs the checker above over its own output before anything
is kept. Its one hard rule is the charter's: no figure is printed that was not
read from a file, and a source that cannot be read prints `PENDING: <path>`
rather than a remembered number. Where a source carries prose rather than a
field the charter asks for, the emitter reproduces the source's own words and
says so; it never fills a column by judgement.

  python3 scripts/morning_report.py --emit [--date YYYY-MM-DD] [--out DIR]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

TITLE = "CERTONOMOUS MORNING REPORT"

HEADINGS = (
    "## 1. SPEND",
    "## 2. LADDER POSITIONS",
    "## 3. GATES",
    "## 4. FD TABLES",
    "## 5. REFILLED QUEUE",
    "## 6. WAITING LIST",
)

EMPTY_TOKEN = "nothing"
PENDING = re.compile(r"^PENDING:\s+(\S.*)$")

DATE = re.compile(r"^Date:\s+(\d{4}-\d{2}-\d{2})\s*$")
ASSEMBLED = re.compile(
    r"^Assembled:\s+(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?"
    r"(Z|\+00:00|\s+UTC))\s*$")
SECTIONS = re.compile(r"^Sections:\s+(\d+) of 6\s*$")
MISSING = re.compile(r"^Missing:\s+(.+?)\s*$")
SOURCE = re.compile(r"^Source:\s+(\S.*)$")
TOP_LEVEL = re.compile(r"^#{1,2}\s+\S")


@dataclass
class Finding:
    rule: str
    message: str
    section: str = ""

    def __str__(self) -> str:
        where = f" [{self.section}]" if self.section else ""
        return f"{self.rule}{where}: {self.message}"


def _split_sections(lines: list[str]) -> tuple[list[str], list[tuple[str, list[str]]]]:
    """The header block, then (heading line, body lines) for each top-level
    heading in the order they appear."""
    header: list[str] = []
    sections: list[tuple[str, list[str]]] = []
    current: list[str] | None = None
    for line in lines:
        if TOP_LEVEL.match(line):
            current = []
            sections.append((line.rstrip(), current))
            continue
        (current if current is not None else header).append(line.rstrip())
    return header, sections


def check_report(text: str, *, repo: Path = REPO) -> tuple[list[Finding],
                                                           list[Finding]]:
    """Every way this report breaks the frame, and every artifact it cites
    that is not on disk. Returns (malformed, citations)."""
    lines = text.splitlines()
    header, sections = _split_sections(lines)
    faults: list[Finding] = []
    citations: list[Finding] = []

    # -- the opening block -------------------------------------------------
    stripped = [line for line in header if line.strip()]
    if not stripped or stripped[0].strip() != TITLE:
        faults.append(Finding(
            "HEADER", f"the report does not open with {TITLE!r}; it opens with "
                      f"{(stripped[0].strip() if stripped else '<empty file>')!r}"))
    for label, pattern in (("Date:", DATE), ("Assembled:", ASSEMBLED)):
        matched = [line for line in stripped if pattern.match(line)]
        present = [line for line in stripped if line.startswith(label)]
        if not present:
            faults.append(Finding("HEADER", f"no {label} line"))
        elif not matched:
            faults.append(Finding(
                "HEADER", f"{label} line is not in the frame's form: "
                          f"{present[0]!r}"))

    printed_count = None
    for line in stripped:
        found = SECTIONS.match(line)
        if found:
            printed_count = int(found.group(1))
            break
    if printed_count is None:
        faults.append(Finding("HEADER", "no `Sections: N of 6` line"))

    printed_missing = None
    for line in stripped:
        found = MISSING.match(line)
        if found:
            printed_missing = found.group(1).strip()
            break
    if printed_missing is None:
        faults.append(Finding("HEADER", "no `Missing:` line"))

    # -- rule 1, the six headings ------------------------------------------
    seen = [heading for heading, _ in sections]
    known = [heading for heading in seen if heading in HEADINGS]
    for heading in HEADINGS:
        count = seen.count(heading)
        if count == 0:
            faults.append(Finding("RULE 1", f"missing heading {heading!r}"))
        elif count > 1:
            faults.append(Finding(
                "RULE 1", f"heading {heading!r} appears {count} times; each "
                          f"appears once"))
    order = [HEADINGS.index(heading) for heading in known]
    if order != sorted(order):
        faults.append(Finding(
            "RULE 1", f"the headings are out of order: "
                      f"{[heading for heading in known]}"))

    # -- rule 2, nothing added at the top level ----------------------------
    for heading in seen:
        if heading not in HEADINGS:
            faults.append(Finding(
                "RULE 2", f"top-level heading {heading!r} is not one of the "
                          f"six; a seventh thing goes inside the section it "
                          f"belongs to, or in section 6, or not in the report"))

    # -- rule 3, the count is recounted ------------------------------------
    counted = len({heading for heading in known})
    if printed_count is not None and printed_count != counted:
        faults.append(Finding(
            "RULE 3", f"the report prints `Sections: {printed_count} of 6` and "
                      f"carries {counted}; the count is computed from the "
                      f"headings, never typed"))
    absent = [str(index + 1) for index, heading in enumerate(HEADINGS)
              if heading not in known]
    if printed_missing is not None:
        want = "none" if not absent else ", ".join(absent)
        normalised = re.sub(r"\s+", " ", printed_missing.replace(",", " ")).strip()
        want_normalised = re.sub(r"\s+", " ", want.replace(",", " ")).strip()
        if normalised != want_normalised:
            faults.append(Finding(
                "RULE 3", f"the report prints `Missing: {printed_missing}` and "
                          f"the headings say {want!r}"))

    # -- rules 4, 5, 6, 7, per section -------------------------------------
    for heading, body in sections:
        if heading not in HEADINGS:
            continue
        content = [line for line in body if line.strip()]
        source_lines = [line for line in content if SOURCE.match(line.strip())]
        pending = [line for line in content if PENDING.match(line.strip())]
        payload = [line for line in content
                   if line not in source_lines and line not in pending]

        if pending:
            if len(content) != 1:
                faults.append(Finding(
                    "RULE 5", "a PENDING section prints the token and nothing "
                              "else; this one carries "
                              f"{len(content)} non-empty line(s)", heading))
            continue

        if not content:
            faults.append(Finding(
                "RULE 4", "the section is empty; an empty section prints the "
                          f"reserved word {EMPTY_TOKEN!r} on its own line, and "
                          "an unreadable source prints `PENDING: <path>`",
                heading))
            continue

        if not source_lines:
            faults.append(Finding(
                "RULE 6", "the section carries content and no `Source:` line",
                heading))
        elif len(source_lines) > 1:
            faults.append(Finding(
                "RULE 6", f"{len(source_lines)} `Source:` lines; a section "
                          f"names its sources on one", heading))

        if payload and payload[0].strip() == EMPTY_TOKEN and len(payload) > 1:
            faults.append(Finding(
                "RULE 4", f"the reserved word {EMPTY_TOKEN!r} is printed beside "
                          f"{len(payload) - 1} other line(s) of content; it "
                          f"means the section was assembled and held nothing",
                heading))

        # -- rule 7, the paths a section cites
        for line in source_lines:
            raw = SOURCE.match(line.strip()).group(1)
            for token in re.split(r"[,\s]+", raw):
                token = token.strip("`'\"()")
                if not token or "/" not in token and "." not in token:
                    continue
                if not (repo / token).exists():
                    citations.append(Finding(
                        "RULE 7", f"cites {token}, which is not on disk",
                        heading))
    return faults, citations


# ---------------------------------------------------------------------------
# The emitter. P-8.1's larger half: assemble the six sections from the named
# sources. Every builder returns the section's body lines; a builder whose
# source cannot be read returns exactly [PENDING: <path>] per rule 5, and a
# builder with a readable source and nothing to say returns [] so the reserved
# word `nothing` is printed per rule 4.
# ---------------------------------------------------------------------------

WEB = "demo-output/website"
SRC_LEDGER = f"{WEB}/mega-batch/ledger.jsonl"
SRC_BOARD = f"{WEB}/ACTIVE_RESEARCH.md"
SRC_GATES = f"{WEB}/campaign/NINE_ACT_GATE_TABLE.md"
SRC_DOCKET = f"{WEB}/agenda/docket.json"
SRC_BLOCKERS = f"{WEB}/agenda/BLOCKERS.md"
REPORTS_DIR = f"{WEB}/campaign/reports"

# scripts/self_audit.py's cleaning rule: a ledger row over 3600 wall seconds
# is host stall, not solver cost. Named here because the charter requires the
# spend header to say which rule cleaned a cleaned figure.
STALL_SECONDS = 3600.0

# What a running solver looks like in the process table; the spend header's
# "left running" line is checked against this, not assumed.
SOLVER_PROCESS_PATTERN = (r"[A-Za-z]+Foam\b|mpirun|snappyHexMesh|blockMesh|"
                          r"vspaero|decomposePar|reconstructPar")

OPEN_STATUSES = ("proposed", "approved", "approved-queued")
QUEUE_STATUSES = ("proposed", "approved", "approved-queued", "dismissed",
                  "done")

STRIKE = re.compile(r"~~.*?~~", re.DOTALL)
VERDICT_WORD = re.compile(r"\b(PASS|CONDITIONAL|FAIL)\b")
PERCENT = re.compile(r"(\d+(?:\.\d+)?)\s*%")
SIGN_FLIP = re.compile(r"sign[\s-]?flip", re.IGNORECASE)


def _typography(text: str) -> str:
    """The agenda's rule, reused: long dashes become hyphens, nothing else is
    rewritten. The charter bans em and en dashes on every surface."""
    return str(text or "").replace("–", "-").replace("—", "-")


def _cell(text: str) -> str:
    """One table cell: typography, collapsed whitespace, pipes escaped."""
    text = _typography(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.replace("|", "\\|")


def _read(repo: Path, rel: str) -> str | None:
    try:
        return (repo / rel).read_text(encoding="utf-8")
    except OSError:
        return None


def _first_table(lines: list[str], start: int = 0) -> list[str]:
    """The rows of the first markdown table at or after `start`, or []. A
    blank line inside a table does not end it if rows continue after the gap;
    the consolidated FD table on the research board carries such a gap and a
    reader who stopped there would silently drop its A4 and A5 rows."""
    index = start
    while index < len(lines) and not lines[index].lstrip().startswith("|"):
        if lines[index].startswith("## ") and index > start:
            return []
        index += 1
    rows: list[str] = []
    while index < len(lines):
        line = lines[index].lstrip()
        if line.startswith("|"):
            rows.append(lines[index])
            index += 1
            continue
        if not line:
            skip = index
            while skip < len(lines) and not lines[skip].strip():
                skip += 1
            if skip < len(lines) and lines[skip].lstrip().startswith("|"):
                index = skip
                continue
        break
    return rows


def _split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _scan_processes() -> list[str]:
    """Solver-shaped command lines in the live process table. A measurement of
    the host at assembly time, reported as such."""
    import subprocess
    try:
        out = subprocess.run(["ps", "-eo", "args"], capture_output=True,
                             text=True, timeout=10).stdout
    except Exception:
        return ["process table unreadable"]
    pattern = re.compile(SOLVER_PROCESS_PATTERN)
    hits = [line.strip() for line in out.splitlines()[1:]
            if pattern.search(line) and "morning_report" not in line
            and "ps -eo args" not in line]
    # The report names what is running; the full command lines live in the
    # process table, not here.
    return [hit if len(hit) <= 140 else hit[:140] + " ..." for hit in hits]


def _minutes(seconds: float) -> str:
    """Wall minutes, printed to the thousandth, never tidied further."""
    return f"{seconds / 60.0:.3f}"


def _build_spend(repo: Path, date: str,
                 scan=_scan_processes) -> tuple[list[str], list[str]]:
    text = _read(repo, SRC_LEDGER)
    if text is None:
        return [f"PENDING: {SRC_LEDGER}"], []
    from datetime import date as date_type, timedelta
    day = date_type.fromisoformat(date)
    night_lo = (day - timedelta(days=1)).isoformat()
    night_hi = date
    week_lo = (day - timedelta(days=day.weekday())).isoformat()

    torn = 0
    newest = ""
    night: list[dict] = []
    week_seconds = 0.0
    for raw in text.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            row = json.loads(raw)
        except ValueError:
            torn += 1
            continue
        stamp = str(row.get("timestamp") or "")
        if stamp > newest:
            newest = stamp
        seconds = float(row.get("wall_seconds") or 0.0)
        if week_lo <= stamp[:10] < night_hi:
            week_seconds += seconds
        if night_lo <= stamp[:10] < night_hi:
            night.append(row)

    gross = sum(float(r.get("wall_seconds") or 0.0) for r in night)
    useful = sum(float(r.get("wall_seconds") or 0.0) for r in night
                 if r.get("ok"))
    wasted = gross - useful
    wasted_on = sorted({f"{r.get('solver')}/{r.get('label')}" for r in night
                        if not r.get("ok")})
    stall_rows = [r for r in night
                  if float(r.get("wall_seconds") or 0.0) > STALL_SECONDS]
    stall_seconds = sum(float(r.get("wall_seconds") or 0.0)
                        for r in stall_rows)

    running = scan()
    if running:
        left = (f"{len(running)} solver-shaped process(es) in the process "
                f"table at assembly: " + "; ".join(_cell(r) for r in running))
    else:
        left = ("nothing, checked by reading the live process table at "
                "assembly for solver command names (pattern "
                f"`{SOLVER_PROCESS_PATTERN}`), not assumed")

    of_which = f"{_minutes(useful)} useful, {_minutes(wasted)} wasted"
    if wasted_on:
        of_which += " on " + ", ".join(wasted_on)

    # P-6.2, carried out 2026-08-05: every core-minute figure printed below
    # carries its basis inline, gross or cleaned, per COMPUTE_BUDGET_CHARTER
    # section 2, which defines the two terms once. A figure without a basis
    # label is a bug in this builder, and the emitter tests check for one.
    lines = [
        f"SPEND, {night_lo} to {night_hi}",
        f"Last night:     {_minutes(gross)} core-minutes (basis: gross) "
        f"across {len(night)} runs recorded in the ledger",
        f"Of which:       {of_which} (basis: gross)",
        f"Cleaned:        {_minutes(gross - stall_seconds)} core-minutes "
        f"(basis: cleaned; {len(stall_rows)} stall row(s) removed by the "
        f"{STALL_SECONDS:.0f} second rule)",
        f"Left running:   {left}",
        f"Week to date:   {_minutes(week_seconds)} core-minutes "
        f"(basis: gross; from {week_lo}, the Monday of this ISO week)",
        "Dollar spend:   not readable from this instance, see waiting list",
        "",
        "Basis, per the compute budget charter section 2: gross sums every "
        "ledger row with a timestamp in the stated window; cleaned is gross "
        "minus the rows the stall rule matches (a row over 3600 wall "
        "seconds is host stall, scripts/self_audit.py). Last night is "
        f"{night_lo} 00:00 UTC to {night_hi} 00:00 UTC. The stall rule "
        f"matched {len(stall_rows)} row(s) in the night window"
        + (f" carrying {_minutes(stall_seconds)} core-minutes."
           if stall_rows else ", so gross and cleaned are the same figure "
                              "there.")
        + " The week figure is gross; its cleaned counterpart is not "
          "printed because the audit reports the week's stall contamination "
          "itself.",
        "The ledger records wall seconds per row and no rank count, so rows "
        "are counted at one rank and these core-minutes are wall-minutes, a "
        "lower bound. Runs not recorded in the ledger are not counted here; "
        "the newest ledger row is dated "
        + (newest if newest else "nothing, the ledger is empty")
        + (f". {torn} torn line(s) were skipped and are counted in no figure."
           if torn else "."),
    ]
    return lines, [SRC_LEDGER]


def _build_ladders(repo: Path, date: str) -> tuple[list[str], list[str]]:
    text = _read(repo, SRC_BOARD)
    if text is None:
        return [f"PENDING: {SRC_BOARD}"], []
    lines = text.splitlines()
    out: list[str] = [
        "Rung sense, per section 2 rule 1: the tables below are the lettered "
        "program tracks with numbered cases; the per-case maturity climb and "
        "the mesh refinement ladders live inside the case records the rows "
        "cite. The source board carries no moved-last-night field, so none "
        "is printed here.",
    ]
    for index, line in enumerate(lines):
        heading = re.match(r"^## (Ladder .+)$", line)
        if not heading:
            continue
        table = _first_table(lines, index + 1)
        if not table:
            continue
        header = _split_row(table[0])
        note = ""
        drop = None
        if "Headline measured result" in header:
            drop = header.index("Headline measured result")
            note = (" (columns reproduced: "
                    + ", ".join(c for c in header if c !=
                                "Headline measured result")
                    + "; the headline measured result column is in the "
                    "source)")
        out.append("")
        out.append(f"**{_cell(heading.group(1))}**{note}")
        for row in table:
            cells = _split_row(row)
            if drop is not None and len(cells) > drop:
                cells = cells[:drop] + cells[drop + 1:]
            out.append("| " + " | ".join(_cell(c) for c in cells) + " |")
    if len(out) == 1:
        return [], [SRC_BOARD]
    return out, [SRC_BOARD]


def _build_gates(repo: Path, date: str) -> tuple[list[str], list[str]]:
    text = _read(repo, SRC_GATES)
    if text is None:
        return [f"PENDING: {SRC_GATES}"], []
    lines = text.splitlines()
    table = _first_table(lines)
    if not table:
        return [], [SRC_GATES]
    out = [_typography(line.rstrip()) for line in table]
    count = next((line.strip() for line in lines
                  if re.match(r"^\d+ of \d+ acts", line.strip())), "")
    if count:
        out += ["", _typography(count)]
    # Rule 7, applied in the section that cites the artifact: the table's own
    # artifact column is checked against the disk, row by row.
    findings = []
    for row in table[2:]:
        cells = _split_row(row)
        if len(cells) < 7:
            continue
        artifact = cells[-1].strip("`")
        if artifact and not (repo / artifact).exists():
            findings.append(f"Row {_cell(cells[0])}: cites {artifact}, "
                            "which is not on disk.")
    if findings:
        out += [""] + findings
    out += ["", "The Ahmed body row: the source directs readers to "
            f"{WEB}/campaign/AHMED_BODY_RECONCILIATION.md before narrating "
            "it."]
    return out, [SRC_GATES]


def _grade_fd_row(cell_text: str) -> str:
    """The grade column. A verdict word already in the row is the source's
    own and is reproduced; a row stating only a percentage is regraded
    against the current standard, marked with an asterisk; a row stating
    neither says so rather than being guessed at."""
    live = STRIKE.sub(" ", cell_text)
    verdicts = []
    for word in VERDICT_WORD.findall(live):
        if word not in verdicts:
            verdicts.append(word)
    if verdicts:
        return " / ".join(verdicts)
    percent = PERCENT.search(live)
    if percent:
        value = float(percent.group(1))
        flagged = bool(SIGN_FLIP.search(live))
        if flagged or value > 15.0:
            return "FAIL*"
        if value > 5.0:
            return "CONDITIONAL*"
        return "PASS*"
    return "not stated in source row"


def _build_fd(repo: Path, date: str) -> tuple[list[str], list[str]]:
    text = _read(repo, SRC_BOARD)
    if text is None:
        return [f"PENDING: {SRC_BOARD}"], []
    lines = text.splitlines()
    anchor = next((i for i, line in enumerate(lines)
                   if line.startswith("### Consolidated FD verification")),
                  -1)
    if anchor < 0:
        return [], [SRC_BOARD]
    table = _first_table(lines, anchor + 1)
    if not table:
        return [], [SRC_BOARD]
    out = [
        "The consolidated view, reproduced from the source. Per-component "
        "tables live in the case records the rows cite; the sources read "
        "carry no machine-readable record of which rung moved last night, "
        "so no per-rung movement table is printed and the consolidated view "
        "stands alone.",
        "",
        "| Rung | derivative | analytic vs FD, relative error | grade |",
        "| --- | --- | --- | --- |",
    ]
    graded_by_standard = False
    for row in table[2:]:
        cells = _split_row(row)
        if len(cells) < 3:
            continue
        grade = _grade_fd_row(cells[2])
        graded_by_standard = graded_by_standard or grade.endswith("*")
        out.append("| " + " | ".join(_cell(c) for c in cells[:3])
                   + f" | {grade} |")
    tail = [
        "",
        "A grade without an asterisk is the source row's own verdict "
        "wording, reproduced; where a row carries more than one verdict "
        "word the row's full text beside it says which stands.",
    ]
    if graded_by_standard:
        tail.append(
            "A grade marked * is recomputed from the row's stated relative "
            "error against the current standard (PASS at 5 percent or "
            "better with no flagged component, CONDITIONAL from 5 to 15 "
            "percent, FAIL above 15 percent or on any sign-flipped "
            "component), per section 7 rule 3.")
    return out + tail, [SRC_BOARD]


def _cost_basis_kind(basis: str) -> str:
    basis = (basis or "").lower()
    if "estimate" in basis:
        return "estimate"
    if "measur" in basis:
        return "measured"
    return "unstated in row"


def _build_queue(repo: Path, date: str) -> tuple[list[str], list[str]]:
    text = _read(repo, SRC_DOCKET)
    if text is None:
        return [f"PENDING: {SRC_DOCKET}"], []
    try:
        docket = json.loads(text)
    except ValueError:
        return [f"PENDING: {SRC_DOCKET}"], []
    proposals = docket.get("proposals", [])

    import sys as _sys
    sdk = str((Path(__file__).resolve().parents[1] / "sdk"))
    if sdk not in _sys.path:
        _sys.path.insert(0, sdk)
    from chief_engineer.agenda import ranked  # noqa: E402

    counts = {status: 0 for status in QUEUE_STATUSES}
    for item in proposals:
        status = str(item.get("status"))
        if status in counts:
            counts[status] += 1
    open_items = ranked([p for p in proposals
                         if str(p.get("status")) in OPEN_STATUSES])
    if not open_items:
        return [], [SRC_DOCKET]

    costed = [float(p["est_core_min"]) for p in open_items
              if p.get("est_core_min")]
    out = [
        "Count by status: " + ", ".join(
            f"{status} {counts[status]}" for status in QUEUE_STATUSES) + ".",
        f"Refill totals: {len(open_items)} open items (proposed, approved, "
        f"approved-queued), {sum(costed):g} core-minutes costed over the "
        f"{len(costed)} rows carrying an estimate; "
        f"{len(open_items) - len(costed)} rows carry none.",
        "Rank order is the ranking function's: expected knowledge gain per "
        "core-minute descending, then case-folded objective, then id "
        "(sdk/chief_engineer/agenda.py).",
        "",
        "| Rank | id | objective | source_kind | est_core_min | cost_basis "
        "kind | status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for rank, item in enumerate(open_items, start=1):
        status = str(item.get("status"))
        note = " ".join(str(item.get(k) or "") for k in
                        ("decision_note", "decision"))
        if "standing authorization" in note.lower() or \
                "blanket" in note.lower():
            status += " (standing authorization)"
        est = item.get("est_core_min")
        out.append("| " + " | ".join([
            str(rank),
            _cell(item.get("id")),
            _cell(item.get("objective")),
            _cell(item.get("source_kind")),
            f"{float(est):g}" if est else "none",
            _cost_basis_kind(str(item.get("cost_basis") or "")),
            _cell(status),
        ]) + " |")
    return out, [SRC_DOCKET]


def _build_waiting(repo: Path, date: str) -> tuple[list[str], list[str]]:
    text = _read(repo, SRC_BLOCKERS)
    if text is None:
        return [f"PENDING: {SRC_BLOCKERS}"], []
    lines = text.splitlines()
    entries: list[tuple[str, str, list[str]]] = []
    current: list[str] | None = None
    for line in lines:
        heading = re.match(r"^## (B-\d+)\.\s*(.*)$", line)
        if heading:
            current = []
            entries.append((heading.group(1), heading.group(2), current))
        elif current is not None:
            current.append(line)

    rows = []
    for blocker_id, title, body in entries:
        if "CLOSED" in title:
            continue
        body_text = "\n".join(body)
        what = _cell(STRIKE.sub(" ", title).strip(" .-"))
        bolds = [b for b in re.findall(r"\*\*(.+?)\*\*", body_text, re.DOTALL)
                 if not b.lstrip().startswith("Unblock")]
        verified = next((b for b in bolds if "block" in b.lower()
                         or "waiting" in b.lower()),
                        bolds[0] if bolds else "see source entry")
        unblock = re.search(
            r"\*\*Unblock[^*]*\*\*:?\s*(.*?)(?:\n\s*\n|\Z)", body_text,
            re.DOTALL)
        since = re.search(
            r"(?:Opened|Recorded|Measured|Found)\s+(\d{4}-\d{2}-\d{2})",
            body_text)
        rows.append("| " + " | ".join([
            blocker_id,
            what,
            _cell(verified.rstrip(".:")),
            _cell(unblock.group(1)) if unblock else "not stated in source",
            since.group(1) if since else "not dated in source",
        ]) + " |")
    if not rows:
        return [], [SRC_BLOCKERS]
    out = [
        "Everything verified blocked on her, from the consolidated blockers "
        "file; entries the file marks CLOSED are not waiting and are not "
        "listed. Decisions waiting on her live in the same file and ride "
        "the same rows.",
        "",
        "| id | What is blocked | Verified blocked how | Unblock action | "
        "Since |",
        "| --- | --- | --- | --- | --- |",
    ] + rows
    return out, [SRC_BLOCKERS]


def build_morning_report(repo: Path, date: str, assembled: str,
                         scan=_scan_processes) -> str:
    """The whole report, as one string ending in a newline. Deterministic
    given the repository state, the date and the assembled stamp; the one
    live measurement is the process scan, injectable for tests."""
    builders = [
        ("## 1. SPEND", lambda: _build_spend(repo, date, scan=scan)),
        ("## 2. LADDER POSITIONS", lambda: _build_ladders(repo, date)),
        ("## 3. GATES", lambda: _build_gates(repo, date)),
        ("## 4. FD TABLES", lambda: _build_fd(repo, date)),
        ("## 5. REFILLED QUEUE", lambda: _build_queue(repo, date)),
        ("## 6. WAITING LIST", lambda: _build_waiting(repo, date)),
    ]
    sections: list[str] = []
    for heading, build in builders:
        body, sources = build()
        pending = len(body) == 1 and PENDING.match(body[0])
        if not body and not pending:
            body = [EMPTY_TOKEN]
        block = [heading, ""] + body
        if not pending:
            block += ["", "Source: " + ", ".join(sources)]
        sections.append("\n".join(block))

    count = sum(1 for heading in HEADINGS
                if any(section.startswith(heading) for section in sections))
    absent = [str(i + 1) for i, heading in enumerate(HEADINGS)
              if not any(section.startswith(heading)
                         for section in sections)]
    header = "\n".join([
        TITLE,
        f"Date:       {date}",
        f"Assembled:  {assembled}",
        f"Sections:   {count} of 6",
        "Missing:    " + (", ".join(absent) if absent else "none"),
    ])
    report = header + "\n\n" + "\n\n".join(sections) + "\n"
    for banned in ("–", "—"):
        if banned in report:
            raise AssertionError(
                "an em or en dash reached the assembled report; the charter "
                "bans both on every surface")
    return report


def emit(repo: Path, date: str, out_dir: Path, assembled: str,
         force: bool = False) -> int:
    report = build_morning_report(repo, date, assembled)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"MORNING_REPORT_{date}.md"
    if path.exists() and not force:
        print(f"REFUSED: {path} already exists and a morning report is "
              "never overwritten (charter section 2 rule 8); pass --force "
              "only to replace a draft")
        return 1
    faults, citations = check_report(report, repo=repo)
    if faults:
        print(f"NOT WRITTEN: the emitter's own output is malformed, "
              f"{len(faults)} rule(s) failed")
        for finding in faults:
            print(f"  {finding}")
        return 1
    path.write_text(report, encoding="utf-8")
    if citations:
        print(f"WRITTEN with findings: {path} holds the frame and cites "
              f"{len(citations)} artifact(s) that are not on disk")
        for finding in citations:
            print(f"  {finding}")
        return 2
    print(f"WRITTEN: {path} holds the frame, six sections, every cited "
          "artifact on disk")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", metavar="REPORT",
                      help="the morning report file to validate")
    mode.add_argument("--emit", action="store_true",
                      help="assemble this morning's report from the named "
                           "sources, self-check it, and write it")
    parser.add_argument("--repo", default=str(REPO),
                        help="root the Source: paths are relative to")
    parser.add_argument("--date", default=None,
                        help="report date, YYYY-MM-DD; defaults to today "
                             "in UTC")
    parser.add_argument("--out", default=None,
                        help=f"directory the report is written to; defaults "
                             f"to {REPORTS_DIR} under the repo")
    parser.add_argument("--assembled", default=None,
                        help="override the Assembled stamp, for "
                             "reproducible runs")
    parser.add_argument("--force", action="store_true",
                        help="replace an existing report file for this date")
    args = parser.parse_args()

    if args.emit:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        date = args.date or now.strftime("%Y-%m-%d")
        assembled = args.assembled or now.strftime("%Y-%m-%dT%H:%M:%SZ")
        repo = Path(args.repo)
        out_dir = Path(args.out) if args.out else repo / REPORTS_DIR
        return emit(repo, date, out_dir, assembled, force=args.force)

    path = Path(args.check)
    if not path.exists():
        print(f"REJECTED: {path} does not exist")
        return 1
    faults, citations = check_report(path.read_text(encoding="utf-8",
                                                    errors="replace"),
                                     repo=Path(args.repo))
    if faults:
        print(f"REJECTED: {path} is malformed against REPORTING_CHARTER "
              f"section 2, {len(faults)} rule(s) failed")
        for finding in faults:
            print(f"  {finding}")
        for finding in citations:
            print(f"  {finding}")
        return 1
    if citations:
        print(f"ACCEPTED with findings: {path} holds the frame and cites "
              f"{len(citations)} artifact(s) that are not on disk")
        for finding in citations:
            print(f"  {finding}")
        return 2
    print(f"ACCEPTED: {path} holds the frame, six sections, every cited "
          f"artifact on disk")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
