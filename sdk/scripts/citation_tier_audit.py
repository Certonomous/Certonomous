#!/usr/bin/env python3
"""Tier discipline over the lab's citations: the half of P-2.1 that was left.

WHAT THIS IS. `scripts/self_audit.py` already resolves every repo-rooted
citation path against disk, which was the half of the proposed citation audit
that was about PATHS. This is the half that was about TIERS. It reads the
records for citations that carry a provenance tier below READ IN FULL and
reports where one of them is doing work the literature charter reserves for a
full read.

WHY IT EXISTS, AND THE INCIDENT IT IS BUILT ON. On 2026-08-05 the papers
agent read the DAFoam journal paper in full and found the lab's own record
asserting, from an abstract-tier citation, "adjoint derivative error under 0.1
percent at 1536 cores". The full text says no such thing: the 1536 cores is
Table 2, runtime only, on a 10.1M-cell structured mesh, and the under-0.1
percent is Table 3, a 102,912-cell accuracy study at an unstated core count.
One sentence of an abstract had joined two disjoint experiments, and the lab
had built an upstream bug report's framing on the join, in the words "this
report, if filed, contradicts that published claim on a measured case". The
citation, the liaison memo it came from and the proposal that carried it were
all corrected the same day (`DAFOAM_PAPERS_VERIFICATION_PROTOCOLS.md` section
5, commit `bf6ac53b`). What nothing caught was the tier: the string carried
"tier SEARCH-EXCERPT ... abstract only" beside the number the whole time, and
that is exactly the first NEVER in `LITERATURE_CHARTER.md` section 7.

THE THREE RULES, and each one names the charter clause it reads.

1. **A number asserted beside a below-full tier.** Section 7: "Assert anything
   from an abstract that the abstract does not literally say." A checker
   cannot read the abstract, so it cannot know whether the assertion is
   literal. What it can see is the shape the defect always takes: a quantity
   standing in the same block as a tier that does not license quantities. This
   is the live-defect rule and it is the reason the file exists.

2. **A tier the charter does not define.** Section 2: "A source that fits none
   of these tiers is not a source. There is no fourth tier." SEARCH-EXCERPT is
   a fourth tier. It was invented in a liaison memo, it reads as narrower than
   PAYWALLED and it is not in the charter's table, so a reader cannot tell
   what may be asserted from it without finding the memo that coined it.
   Reported, never rewritten: whether the charter gains the tier or the
   records lose it is the owner's call, and both are one edit.

3. **An untiered citation inside a document that runs the discipline.
   MEASURED AND NOT ADOPTED; it ships behind `--untiered` and is off.** The
   P-2.1 half as she asked it: a citation-shaped string with no tier in its
   block, scoped to files that carry tiers elsewhere so a report that never
   claimed the discipline is not held to it.

   **The archive replay, which is what charter 1 disqualifier 10 requires of
   any new detection rule and which this file therefore owes for its own
   rules.** Corpus: 392 records under the charters, the standards, the docket
   and the website, 2026-08-05. Rule 1 fires on 4 blocks, rule 2 on 3, and
   both are gradeable by hand against the charter's own tier table. Rule 3
   fires on 24, and 19 of them are one file, `F5a_cylinder_reynolds_ladder`,
   where 15 are rows of published reference-comparison tables: a Strouhal
   number beside "Norberg (1994)" in a column of literature values. That is
   the false-positive family the charter's own P-2.1 entry predicted, and it
   is the shape of C-2's withdrawn S7 rule, which fired on 68 of 106
   completed runs and could not separate the case it was written for. **A
   rule whose hits are dominated by one file's reference table has not been
   shown to discriminate**, so it is measured, recorded and left off by
   default rather than adopted quietly. What would make it adoptable is a
   way to tell a reference-comparison row from a claim carried forward, and
   nobody has one.

WHAT IT DOES NOT DO. It never checks truth, only discipline, and it never
edits a record. A block carrying a dated correction or a supersession note is
already repaired and is not reported again, which is the same rule
`agenda.cost_basis_violations` uses to tell disclosure from pricing.

TUNING, and the asymmetry is the opposite of `self_audit.py`'s. There a false
positive costs one reading. Here a false positive accuses a record of a
citation defect, so every rule is written to prefer a miss, and the findings
are WARN by the charter's own recommendation: exit status stays 0 unless
`--strict` is given.

    python3 sdk/scripts/citation_tier_audit.py            # human-readable
    python3 sdk/scripts/citation_tier_audit.py --json     # machine-readable
    python3 sdk/scripts/citation_tier_audit.py --strict   # exit 1 on findings

THIS AUDIT FAILS CLOSED. It printed its own reach -- "(0 records, 0 finding(s))"
-- and exited 0 anyway, even under --strict, because an empty corpus has no
findings by definition. A misspelt path therefore cleared every charter and
standard in the lab while saying on screen that it had read none of them.
0 records now prints RED and exits 2 with no verdict, in --json too, and that
is independent of --strict: --strict is a policy choice about FINDINGS and the
charter's WARN default is deliberate, but whether the audit ran at all is not
a matter of policy.

Exit codes:  0 = read >=1 record; findings reported, WARN by charter default
             1 = findings, under --strict
             2 = no records read                 (RED -- verdict withheld)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

# The one module that names this repository's tree (MOVE_MAP batch 3).
# Every name it exports is bound to a legacy/successor PAIR resolved
# against the filesystem at import, so the constants below are correct
# before the move, between batches and after it, with no edit here.
import sys as _sys  # noqa: E402
import pathlib as _pathlib  # noqa: E402
_LAB_PATHS_DIR = str(_pathlib.Path(__file__).resolve().parents[2]
                     / "scripts")
if _LAB_PATHS_DIR not in _sys.path:
    _sys.path.insert(0, _LAB_PATHS_DIR)
import lab_paths  # noqa: E402

REPO = Path(__file__).resolve().parents[2]

# The charter's own tier table, section 2. A tier at or above this line
# licenses a quantity; anything below it licenses only what the excerpt
# literally says.
FULL_TIERS = (
    re.compile(r"READ[\s-]IN[\s-]FULL", re.I),
    re.compile(r"INTERNAL,?\s+already\s+read", re.I),
)

# Tiers below a full read. PAYWALLED and abstract-only are the charter's;
# SEARCH-EXCERPT is not, which is rule 2's whole content.
#
# THE TOKENS ARE MATCHED AS THE CHARTER WRITES THEM, in capitals, and that is
# not fussiness. Measured over the records on 2026-08-05, a case-insensitive
# match on "paywalled" fires on six blocks that are reporting a paywall rather
# than declaring a tier -- an availability check that came back closed, a
# reference swapped out BECAUSE it was paywalled, a note that a source is
# paywalled from this box. Those blocks are the charter's section 2
# availability discipline working, and flagging them would be the audit
# accusing a record of the defect it was written to avoid. The lowercase word
# is prose; the capitalised token is a tier.
BELOW_FULL_TIERS = (
    re.compile(r"PAYWALLED"),
    re.compile(r"abstract[\s-]only", re.I),
    re.compile(r"SEARCH[\s-]EXCERPT"),
    re.compile(r"tier[:\s]+\S*\bpaywalled\b", re.I),
)

# The tier that is not in the charter's table.
UNDEFINED_TIERS = {"SEARCH-EXCERPT": re.compile(r"SEARCH[\s-]EXCERPT")}

# A block already carrying a dated correction, a supersession or an explicit
# tier upgrade has been repaired and is not a finding. Same rule as the cost
# rail's `_SUPERSESSION_DISCLOSED`: naming a defect in order to disclose it is
# the opposite of committing it.
_REPAIRED = re.compile(
    r"\bCORRECTION\b|\bcorrected\b|\bsupersed|\bwithdraw|"
    r"\bsince READ IN FULL\b|\bupgradeable to READ IN FULL\b", re.I)

# A block that names the undefined tier IN ORDER TO REPORT IT is discussing the
# vocabulary rather than citing at it, and rule 2 firing there would grow its
# own hit count every time somebody writes about the problem -- which happened
# the day this file landed: the charter clause and the proposals entry
# describing the finding each tripped the rule they were describing.
#
# THE TEST IS THE SENTENCE, NEVER THE FILENAME. Exempting a document by path
# would let a real citation defect hide inside a charter, which is the one
# place a defect would be believed. So the exemption is earned by saying the
# thing: a block that states the tier is undefined, or is asking whether the
# charter should define it, has already told the reader everything this rule
# would have told them.
_DISCUSSES_THE_TIER = re.compile(
    r"\bdoes not define\b|\bnot in the\b[^.]{0,60}\btable\b|"
    r"\bfourth tier\b|\bundefined tier\b|"
    r"\bthe charter gains\b|\bthe records lose it\b", re.I)

# Locators are not claims. A section, table, figure, equation or page number
# beside a citation is how the charter asks for citations to be written, so
# they come out before any quantity is looked for. So does the citation's own
# machinery: a DOI, an arXiv identifier and a volume-issue-page string are all
# digit-shaped and none of them is a measurement. Measured on the same pass, a
# scan that kept them reported "asserts 10.1016, 10.1017" on bibliography
# blocks that assert nothing at all.
_IDENTIFIERS = re.compile(
    r"10\.\d{4,}/\S+"                       # DOI
    r"|\barxiv[:\s]*\d{4}\.\d{4,}(?:v\d+)?"  # arXiv identifier
    r"|\b\d{4}\.\d{4,}(?:v\d+)?\b"           # bare arXiv identifier
    r"|\b\d+\s*\(\d+\)\s*:?\s*\d+(?:\s*(?:-|to)\s*\d+)?"  # 47(1):75-98
    r"|10\.\d{4,}", re.I)
_LOCATORS = re.compile(
    r"(?:§|section|sec\.|table|tab\.|figure|fig\.|equation|eq\.|page|p\.|"
    r"pp\.|chapter|ch\.|item|rule|lesson|commit|version|v)\s*"
    r"[A-Za-z]?\d+(?:\.\d+)*", re.I)
# Years, reference identities (NACA 0012, RAE 2822) and lesson or docket tags
# are names, not measurements.
_NON_QUANTITIES = (
    re.compile(r"\b(?:19|20)\d{2}\b"),
    re.compile(r"\b(?:NACA|RAE|ONERA|DLR|M)\s?\d{3,4}\b", re.I),
    re.compile(r"\b[A-Z]-\d+\b"),
    re.compile(r"\bv\d+(?:\.\d+)*\b", re.I),
)
# What a quantity looks like: a decimal, a percentage, a scientific-notation
# figure, or a magnitude with a unit the lab actually publishes in.
_QUANTITY = re.compile(
    r"\d+\.\d+"
    r"|\d+\s*(?:%|percent\b)"
    r"|\d+(?:\.\d+)?[eE][-+]?\d+"
    r"|\b\d[\d,]*\s*(?:cores?|cells?|core[\s-]min(?:utes?)?|"
    r"core[\s-]hours?|iterations?|seconds?|degrees?)\b", re.I)

# A citation-shaped string for rule 3: a surname carrying a parenthesised
# year, which is the one form that cannot be a date. An earlier draft accepted
# a bare year and fired on "Added 2026", "Attempted 2026-08-02" and "Re 2000",
# which is the false-positive family this file's own tuning note forbids.
_CITATION_SHAPE = re.compile(
    r"\b[A-Z][A-Za-z'`-]{2,}"
    r"(?:\s*(?:,|and|&)\s*[A-Z][A-Za-z'`.-]+)*"
    r"(?:\s+et al\.?)?\s*\((?:19|20)\d{2}\)")

_LIST_ITEM = re.compile(r"(?:[-*+]|\d+\.)\s+\S")

SEVERITY = "WARN"


@dataclass
class Finding:
    rule: str
    path: str
    line: int
    excerpt: str
    why: str


def _blocks(text: str) -> list[tuple[int, str]]:
    """(first line number, block text) over a record.

    A block is a paragraph. A table row and a list item are each their own
    block, because a tier belongs to one citation and reading a whole table
    or a whole bibliography as one block lets one entry's full read cover the
    next entry's abstract. Measured: without the list rule, one bibliography
    in which a single entry is PAYWALLED reported the numbers of every other
    entry in the list as asserted at that tier.
    """
    out: list[tuple[int, str]] = []
    current: list[str] = []
    start = 1
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("|") or _LIST_ITEM.match(stripped):
            if current:
                out.append((start, "\n".join(current)))
            current = [line]
            start = number
            continue
        if current and _LIST_ITEM.match(current[0].strip()):
            # A continuation line of the list item that opened this block.
            if stripped:
                current.append(line)
                continue
            out.append((start, "\n".join(current)))
            current = []
            continue
        if not stripped:
            if current:
                out.append((start, "\n".join(current)))
                current = []
            continue
        if not current:
            start = number
        current.append(line)
    if current:
        out.append((start, "\n".join(current)))
    return out


def _json_blocks(data, path: str = "") -> list[tuple[str, str]]:
    """(field path, string) for every string in a JSON record.

    A proposal's citation list is the unit here: each citation string carries
    its own tier and its own claim, which is how the w4 defect was written.
    """
    out: list[tuple[str, str]] = []
    if isinstance(data, dict):
        for key, value in data.items():
            out.extend(_json_blocks(value, f"{path}.{key}" if path else key))
    elif isinstance(data, list):
        for index, value in enumerate(data):
            out.extend(_json_blocks(value, f"{path}[{index}]"))
    elif isinstance(data, str):
        out.append((path, data))
    return out


def _has_full_tier(block: str) -> bool:
    return any(pattern.search(block) for pattern in FULL_TIERS)


def _below_full_tier(block: str) -> str | None:
    for pattern in BELOW_FULL_TIERS:
        match = pattern.search(block)
        if match:
            return match.group(0)
    return None


def quantities(block: str) -> list[str]:
    """Every quantity in the block that is not a locator, a year or a name."""
    text = _LOCATORS.sub(" ", _IDENTIFIERS.sub(" ", block))
    for pattern in _NON_QUANTITIES:
        text = pattern.sub(" ", text)
    return [m.group(0).strip() for m in _QUANTITY.finditer(text)]


def _excerpt(block: str, limit: int = 160) -> str:
    flat = re.sub(r"\s+", " ", block).strip()
    return flat if len(flat) <= limit else flat[:limit - 3] + "..."


def check_block(block: str, where: str, line) -> list[Finding]:
    """The three rules, over one block."""
    found: list[Finding] = []
    if _REPAIRED.search(block):
        return found
    tier = _below_full_tier(block)
    if tier and not _has_full_tier(block):
        values = quantities(block)
        if values:
            found.append(Finding(
                "quantity asserted at a below-full tier", where, line,
                _excerpt(block),
                f"the block carries tier {tier!r} and asserts "
                f"{', '.join(values[:4])}; LITERATURE_CHARTER section 2 lets "
                f"an excerpt tier support only what the excerpt literally "
                f"states, and section 7's first NEVER forbids the rest. This "
                f"is the shape of the 2026-08-05 defect: a 1536-core runtime "
                f"and an under-0.1-percent accuracy figure, joined by one "
                f"abstract sentence, from two disjoint experiments"))
    for name, pattern in UNDEFINED_TIERS.items():
        if pattern.search(block) and not _DISCUSSES_THE_TIER.search(block):
            found.append(Finding(
                "a tier the charter does not define", where, line,
                _excerpt(block),
                f"{name} is not in the LITERATURE_CHARTER section 2 table, "
                f"and that section says there is no fourth tier; a reader "
                f"cannot tell what may be asserted from it without finding "
                f"the memo that coined it"))
    return found


def check_untiered_citations(text: str, where: str) -> list[Finding]:
    """Rule 3, and only inside a document that already runs the discipline."""
    if not any(pattern.search(text) for pattern in FULL_TIERS):
        return []
    found: list[Finding] = []
    for line, block in _blocks(text):
        if _REPAIRED.search(block):
            continue
        if _has_full_tier(block) or _below_full_tier(block):
            continue
        match = _CITATION_SHAPE.search(block)
        if not match or not quantities(block):
            continue
        found.append(Finding(
            "a citation carrying no tier, in a file that tiers", where, line,
            _excerpt(block),
            f"the block cites {match.group(0).strip()!r} beside a quantity "
            f"and states no provenance tier, in a record that states tiers "
            f"elsewhere; LITERATURE_CHARTER section 2 requires one per "
            f"citation, and P-2.1's WARN is exactly this case"))
    return found


DEFAULT_ROOTS = (
    Path("docs/charters"),
    Path("docs/standards"),
    lab_paths.AGENDA.relative_to(lab_paths.REPO),
    lab_paths.DAFOAM.relative_to(lab_paths.REPO),
    lab_paths.CAMPAIGN.relative_to(lab_paths.REPO),
)


def _iter_files(roots) -> list[Path]:
    out: list[Path] = []
    for root in roots:
        path = root if root.is_absolute() else REPO / root
        if path.is_file():
            out.append(path)
        elif path.is_dir():
            out.extend(sorted(p for p in path.rglob("*")
                              if p.suffix in (".md", ".json") and p.is_file()))
    return out


def audit(roots=DEFAULT_ROOTS, untiered: bool = False) -> list[Finding]:
    findings: list[Finding] = []
    for path in _iter_files(roots):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        try:
            where = str(path.relative_to(REPO))
        except ValueError:
            where = str(path)
        if path.suffix == ".json":
            try:
                data = json.loads(text)
            except ValueError:
                continue
            for field, value in _json_blocks(data):
                findings.extend(check_block(value, where, field))
            continue
        for line, block in _blocks(text):
            findings.extend(check_block(block, where, line))
        if untiered:
            findings.extend(check_untiered_citations(text, where))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="records to audit; the "
                        "charters, standards, docket and website records by "
                        "default")
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable findings")
    parser.add_argument("--strict", action="store_true",
                        help="exit 1 when anything is found; the charter "
                        "recommends WARN, so the default exit is 0")
    parser.add_argument("--untiered", action="store_true",
                        help="also run rule 3, which was replayed against "
                        "the records and NOT adopted: 24 hits, 19 in one "
                        "file, 15 of them rows of reference-comparison "
                        "tables. See the module docstring")
    args = parser.parse_args()

    roots = [Path(p) for p in args.paths] if args.paths else DEFAULT_ROOTS

    # --- fail closed --------------------------------------------------------
    # Counted before anything is judged. This audit already PRINTED its reach
    # -- "(0 records, 0 finding(s))" -- and then exited 0 anyway, even under
    # --strict, whose own help text promises "exit 1 when anything is found".
    # Nothing is found in an empty corpus by definition, so a misspelt path
    # cleared every charter and standard in the lab while stating on screen
    # that it had read none of them. Printing the number and acting on it are
    # different properties; this had the first.
    #
    # RED here is independent of --strict. --strict is a policy choice about
    # FINDINGS, and the charter's WARN default is a deliberate one; whether
    # the audit ran at all is not a matter of policy.
    scanned = _iter_files(roots)
    if not scanned:
        print("  RED: this audit read no records.", file=sys.stderr)
        print("       Looked for *.md and *.json under:", file=sys.stderr)
        for root in roots:
            path = root if root.is_absolute() else REPO / root
            state = ("file" if path.is_file() else
                     "directory" if path.is_dir() else "DOES NOT EXIST")
            print(f"         {path} -- {state}", file=sys.stderr)
        print("  No verdict. 0 records scanned, so no citation tier is "
              "cleared and none is challenged.", file=sys.stderr)
        return 2

    findings = audit(roots, untiered=args.untiered)

    if args.json:
        print(json.dumps([asdict(f) for f in findings], indent=1))
    else:
        rules = 3 if args.untiered else 2
        print(f"Citation tier audit  ({len(scanned)} records, "
              f"{rules} rules, "
              f"{len(findings)} finding(s), severity {SEVERITY})")
        print("=" * 78)
        by_rule: dict[str, list[Finding]] = {}
        for finding in findings:
            by_rule.setdefault(finding.rule, []).append(finding)
        for rule, rows in by_rule.items():
            print(f"\n{rule}  ({len(rows)})")
            for row in rows:
                print(f"  [{SEVERITY}] {row.path}:{row.line}")
                print(f"         {row.excerpt}")
                print(f"         why: {row.why}")
        if not findings:
            # The reach rides with the verdict. "nothing found" alone reads
            # identically over 1 record and over 800.
            print(f"\nnothing found -- {len(scanned)} record(s) read, "
                  f"{rules} rule(s) applied")
        print("\n" + "=" * 78)
        print("This audit reports and never repairs. Whether a record is "
              "corrected, or the charter gains the tier, is the owner's call.")
    return 1 if (findings and args.strict) else 0


if __name__ == "__main__":
    sys.exit(main())
