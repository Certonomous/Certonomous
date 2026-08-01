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
"""

from __future__ import annotations

import argparse
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", metavar="REPORT", required=True,
                        help="the morning report file to validate")
    parser.add_argument("--repo", default=str(REPO),
                        help="root the Source: paths are relative to")
    args = parser.parse_args()

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
