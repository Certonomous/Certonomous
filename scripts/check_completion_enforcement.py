#!/usr/bin/env python3
"""
check_completion_enforcement.py -- the STANDING INSTRUMENT for VERIFICATION_CHARTER
§2ay (v1.70, commit 606e658b).  Sanaa ordered "fix until it runs" made executable,
"now and going forward."  This is that instrument.

WHAT IT DOES  (§2ay.2)
----------------------
It ENUMERATES every landed `GATE FAIL` and `NOT A RESULT` it can read from the
declared RECORDS and REGISTERS, and FLAGS any that is not in one of the two
acceptable states:

  (a) PROVEN A GENUINE OpenFOAM CAPABILITY GAP -- unrecoverability MEASURED, with
      each of the five §2an process classes (bug / solver-selection /
      preconditioner / numerics-scheme / config) AND model-form EXPLICITLY ruled
      out, and the gap FILED ON SANAA'S DESK; or
  (b) CARRYING AN ACTIVE, DATED FIX-SUCCESSOR -- a registered next attempt (a
      successor registration or a closure-ladder rung) that changes what failed
      and re-runs -- or its terminal form: DISCHARGED by a landed passing
      successor whose lineage is recorded.

Anything in NEITHER state is a STANDING VIOLATION and is flagged.

WHAT IT IS NOT  (§2ay.4 -- every boundary is §2at/§2an law restated)
-------------------------------------------------------------------
  * IT FLAGS ONLY.  It never widens a gate, composes a verdict, converts a fail
    to a pass, or edits any graded record.  Its only output is a report.
  * IT READS VERDICTS FROM RECORDS AND REGISTERS, NOT FROM BOARDS.  Where a record
    and its board disagree, the ARTIFACT governs -- so the source list below is
    registers and records, and docs/LAB_STATE.md (a board) is deliberately NOT a
    verdict source.
  * IT DOES NOT RE-GRADE.  It reads what is already graded and asks whether the
    fail is being worked.

⚠ §2ay.3 -- "DIAGNOSED TO A MECHANISM" IS NOT "PROVEN UNRECOVERABLE"
-------------------------------------------------------------------
State (a) is reachable ONLY when every one of the five process classes AND
model-form has been ruled out AT SOURCE, the unrecoverability is MEASURED, and
the filing is on her desk.  A mechanism-diagnosis with no successor and no
five-point rule-out is a VIOLATION, not a capability gap -- and this check flags
it as one and labels the WHY `mechanism-diagnosis-only`.  A model-form diagnosis
routes into the closure ladder, which is an ACTIVE SUCCESSOR (state b), never a
capability-gap filing (state a).

⚡⚡ THE PLANTED CONTROL  (§2ay.5, §28.8, rule 3)
------------------------------------------------
`--selftest` drives a TWO-LIMB planted control, RED-then-GREEN, in a throwaway
fixture tree:
  LIMB 1 -- a landed fail with NO successor and NO gap-filing MUST be flagged.
  LIMB 2 -- a properly-covered fail (a dated successor / a discharging passing
            successor / a capability-gap filing) MUST NOT be flagged.
It then DRIVES THE DETECTOR RED by crippling the coverage-finder to always-true
and confirms LIMB 1 stops flagging -- i.e. it proves the plant catches a blind
checker.  A zero-violations output from this instrument is believed ONLY when
both limbs fired GREEN and the RED drive was seen to blind it (§2ay.5, rule 3).

NON-VACUITY ON THE REAL SCAN  (rule 3, §2ay.7)
----------------------------------------------
The real scan prints, alongside any zero, WHAT IT COULD NOT SEE: fail-token
files repo-wide that are not in its source list, rows from which no case id could
be extracted, and the coverage fraction against a broad manual sweep.  A first
scan is a DRAFT until the verification-supervisor has diff-read this instrument
(§2ay.7); the scan says so in its own header.

Exit codes:  0 = ran and reported (flags are DATA, not a failing exit -- a flag is
a measurement, not a rebuke, §2ay.6);  2 = the instrument REFUSED (empty
population, or --selftest plant did not fire both limbs).  A refusal is never a
clean bill (rule 3; check_comparator_freeze.py's 2p.2 posture).

This file is diff-read by the verification-supervisor before its output is
believed (§2ay.7, SUPERVISION §3 check 1).  It writes nothing outside its own
scratch fixture tree and it moves no verdict.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

# --------------------------------------------------------------------------
# CONFIGURATION -- the declared verdict SOURCES (records and registers, never
# boards).  §2ay.4: verdicts are read from records and registers; where a record
# and its board disagree the artifact governs, so a board is never a source here.
# The list is deliberately explicit and auditable rather than "walk everything":
# a walk of all 924 fail-token .md files would drown landed verdicts in prose
# mentions.  Non-vacuity reporting (below) names exactly what this list omits.
# --------------------------------------------------------------------------
DEFAULT_SOURCES = [
    "verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md",
    "docs/capability/ansys_ROWS.md",
    "docs/campaigns/T-family/T23G2_RESULTS.md",
    "docs/campaigns/T-family/MATRIX_CONTRIBUTION.md",
    "cases/RANS_LES_closure_models/MATRIX_CONTRIBUTION.md",
    "docs/CAPABILITY_GRID.md",
]

# The five §2an process classes plus model-form.  State (a) requires ALL of these
# ruled out at source in the filing.  Each maps to a set of source-text markers.
FIVE_PLUS_MODELFORM = {
    "bug": [r"\bbug\b", r"code[- ]?defect", r"ruled out.*bug"],
    "solver-selection": [r"solver[- ]?selection", r"solver choice", r"\bsolver\b.*ruled"],
    "preconditioner": [r"preconditioner", r"\bprecond"],
    "numerics-scheme": [r"numerics[- ]?scheme", r"discretis", r"\bscheme\b.*ruled"],
    "config": [r"\bconfig\b", r"configuration", r"setup.*ruled"],
    "model-form": [r"model[- ]?form"],
}

# A desk-filing must carry an explicit "on Sanaa's desk" marker.  There is no
# canonical desk directory in the repo (surveyed 2026-09-06), so recognition is
# by an explicit in-file marker, kept strict on purpose: an enforcer errs toward
# FLAGGING, never toward a false clear.
DESK_MARKERS = [
    r"on sanaa'?s desk",
    r"filed on (?:her|sanaa'?s) desk",
    r"capability[- ]?gap fil",
]

# §2ay.4: VERDICTS AND COVERAGE ARE READ FROM RECORDS AND REGISTERS, NOT FROM
# BOARDS.  A "capability-gap filing on Sanaa's desk" is a dedicated per-case
# artifact, never a mention scattered through a board or a knowledge index.  These
# basenames are EXCLUDED as gap-filing sources: a megafile trips the six-token
# rule-out test merely by containing all those words SOMEWHERE, which would clear
# a fail that is not genuinely covered -- an enforcer erring toward clearing, the
# exact §2ay disease.  Excluding them makes the check err toward FLAGGING (safe).
BOARD_OR_INDEX_FILES = {
    "LAB_STATE.md", "DOCKET.md", "LESSONS.md", "NUMERICS_KNOWLEDGE.md",
    "CROSS_TEAM_GATE_AUDIT.md", "FAIL_OPEN_GATE_AUDIT.md", "CAPABILITY_GRID.md",
    "LOCATIONS.md", "MEMORY_ARCHITECTURE.md", "COST_CALIBRATION.md",
}

# For a gap filing to CLEAR a case into state (a), the case id, a desk marker AND
# all six rule-out token-classes must CO-OCCUR within this many lines of each
# other -- not merely appear anywhere in the same file.
GAP_WINDOW_LINES = 40

# Cause / mechanism-diagnosis language, used ONLY to LABEL a flagged row's WHY as
# `mechanism-diagnosis-only` (§2ay.3).  It never clears a flag.
MECHANISM_MARKERS = [
    r"\bbecause\b", r"diverg", r"wall treatment", r"limiter", r"\bmechanism\b",
    r"\bdiagnos", r"root cause", r"attributabl",
]

# Verdict tokens this instrument enumerates.  Backtick / bold wrappers stripped
# before matching.  Only these two are landed FAILS under §2ay.
FAIL_VERDICTS = ("GATE FAIL", "NOT A RESULT")
PASS_VERDICTS = ("PASS", "GATE REACHED")

# Case-id patterns, ordered most-specific first.  A row's case id is the first
# match in its content.  Suffixes -R2 / _R2 / -M2 / -L1 etc are part of the id.
CASE_ID_RE = re.compile(
    r"\b("
    r"FIX\d{3}(?:[-_][A-Za-z0-9]+)*"          # synthetic ids used ONLY by --selftest fixtures
    r"|VMFLGPU\d{3}(?:[-_][A-Za-z0-9]+)*"     # ansys GPU cases
    r"|VMFL\d{3}(?:[-_][A-Za-z0-9]+)*"        # ansys cases
    r"|K0[a-z]?(?:R\d+)?"                       # F14 cooling rungs (K0, K0c, K0eR3)
    r"|T\d+[a-z]?(?:[-_][A-Za-z0-9]+)*"        # T-family rungs (T1b, T23G2)
    r"|R\d+[a-z]?(?:[-_][A-Za-z0-9]+)*"        # closure R-ladder
    r"|FS\d+(?:[-_][A-Za-z0-9]+)*"             # feature ladder
    r"|[ABSW]\d+(?:[-_][A-Za-z0-9]+)*"         # dafoam ladders
    r"|F\d+[a-z]?(?:[-_][A-Za-z0-9]+)*"        # cfd F-campaigns
    r")\b"
)

# A successor id extends a base id with a re-run / model suffix.
SUCCESSOR_SUFFIX_RE = re.compile(r"^(.*?)[-_](R\d+|M\d+|L\d+|S\d+|b|c)(?:[-_].*)?$")


# --------------------------------------------------------------------------
# DATA MODEL
# --------------------------------------------------------------------------
@dataclass
class FailRow:
    case: str
    verdict: str
    source: str          # repo-relative path
    line: int
    text: str            # the row text (trimmed)


@dataclass
class Coverage:
    state: str           # "a", "b", or ""  ("" == not covered)
    why: str             # human-readable reason
    evidence: str        # path[:line] / directory / sha


@dataclass
class Result:
    row: FailRow
    coverage: Coverage
    flagged: bool


# --------------------------------------------------------------------------
# ENUMERATION -- read landed fails from the declared sources
# --------------------------------------------------------------------------
def _strip_wrappers(cell: str) -> str:
    """Remove markdown bold/backtick/whitespace wrappers from a table cell."""
    return cell.replace("**", "").replace("`", "").strip()


def _row_verdict(row_text: str) -> str | None:
    """Return the fail verdict token in a table row, or None.

    A verdict TOKEN is a whole backtick- or bold-wrapped cell equal to a fail
    verdict, OR a bare fail phrase standing in a table cell.  We do NOT match a
    verdict that appears inside a longer sentence in the same cell (that is prose
    ABOUT a verdict, not the row's own verdict) unless the cell is exactly it.
    """
    if "|" not in row_text:
        # Not a table row -- §2ay reads records/registers as rows; prose lines are
        # reported as UNPARSED in the non-vacuity channel, never silently graded.
        return None
    cells = [c for c in row_text.split("|")]
    for c in cells:
        stripped = _strip_wrappers(c)
        up = stripped.upper()
        for v in FAIL_VERDICTS:
            # exact cell, or cell that STARTS with the token then whitespace/em-dash
            if up == v or up.startswith(v + " ") or up.startswith(v + "—") or up.startswith(v + " —"):
                return v
    return None


def _row_case(row_text: str) -> str | None:
    """Extract the case id from a table row: first case-id match in its cells,
    skipping the leading index cell (e.g. `**1**`)."""
    if "|" not in row_text:
        return None
    cells = [_strip_wrappers(c) for c in row_text.split("|")]
    for c in cells:
        # skip pure row-index cells like "1", "#1", ""
        if re.fullmatch(r"#?\d+", c) or c == "":
            continue
        m = CASE_ID_RE.search(c)
        if m:
            return m.group(1)
    return None


def enumerate_fails(sources: list[Path], repo: Path) -> tuple[list[FailRow], list[tuple[str, int, str]]]:
    """Return (fail_rows, unparsed) where unparsed is (path,line,reason) for lines
    that carry a fail verdict token but no extractable case id -- the honest
    'could not parse' channel (rule 3)."""
    fails: list[FailRow] = []
    unparsed: list[tuple[str, int, str]] = []
    for src in sources:
        if not src.exists():
            unparsed.append((str(src.relative_to(repo)) if src.is_absolute() else str(src), 0, "SOURCE MISSING"))
            continue
        rel = str(src.relative_to(repo)) if src.is_absolute() and str(src).startswith(str(repo)) else str(src)
        for i, line in enumerate(src.read_text(errors="replace").splitlines(), 1):
            v = _row_verdict(line)
            if v is None:
                continue
            case = _row_case(line)
            if case is None:
                unparsed.append((rel, i, f"fail verdict {v!r} but no case id extractable"))
                continue
            fails.append(FailRow(case=case, verdict=v, source=rel, line=i, text=line.strip()[:240]))
    return fails, unparsed


# --------------------------------------------------------------------------
# COVERAGE -- for each fail, is it in state (a) or (b)?
#
# This is the function the RED drive cripples: an enforcer whose coverage-finder
# is silently always-true clears every fail, which is the §28 disease at the law.
# --------------------------------------------------------------------------
def _find_passing_successor(case: str, all_rows: list[FailRow], pass_index: dict[str, list[tuple[str, int]]]) -> str | None:
    """A landed passing verdict for a case id that extends `case`."""
    for pid, locs in pass_index.items():
        if pid == case:
            continue
        m = SUCCESSOR_SUFFIX_RE.match(pid)
        base = m.group(1) if m else None
        if base == case or pid.startswith(case + "-") or pid.startswith(case + "_"):
            p, ln = locs[0]
            return f"passing successor {pid} at {p}:{ln}"
    return None


@dataclass
class RepoIndex:
    """Built ONCE per scan so coverage lookup is O(1) per row, not a repo rglob
    per row (which made the first draft take minutes)."""
    succ_dirs: dict[str, str] = field(default_factory=dict)      # base case -> "dir/PREREGISTRATION.md"
    succ_files: list[tuple[str, str]] = field(default_factory=list)  # (name, text-lower) of *SUCCESSOR* files
    gap_files: list[tuple[str, list[str]]] = field(default_factory=list)  # (name, lowercased line list) of desk-marked filings


def build_repo_index(repo: Path, search_roots: list[Path]) -> RepoIndex:
    idx = RepoIndex()
    # successor-shaped case directories under cases/
    cases = repo / "cases"
    if cases.exists():
        for parent in cases.rglob("PREREGISTRATION.md"):
            d = parent.parent.name
            m = SUCCESSOR_SUFFIX_RE.match(d)
            base = m.group(1) if m else None
            if base:
                idx.succ_dirs.setdefault(base, f"{d}/PREREGISTRATION.md")
    # *SUCCESSOR* files (read once)
    for root in search_roots:
        if not root.exists():
            continue
        for f in root.rglob("*SUCCESSOR*"):
            if ".git" in f.parts or not f.is_file():
                continue
            try:
                idx.succ_files.append((f.name, f.read_text(errors="replace").lower()))
            except OSError:
                continue
    # candidate desk-marked filings: .md files carrying a desk marker (read once),
    # EXCLUDING boards/indexes (§2ay.4).  Store per-line so co-occurrence can be
    # tested within a window rather than anywhere-in-file.
    for root in search_roots:
        if not root.exists():
            continue
        target = root.rglob("*.md") if root.is_dir() else [root]
        for f in target:
            if ".git" in f.parts or not f.is_file():
                continue
            if f.name in BOARD_OR_INDEX_FILES:
                continue
            try:
                lines = [l.lower() for l in f.read_text(errors="replace").splitlines()]
            except OSError:
                continue
            if any(any(re.search(m, l) for m in DESK_MARKERS) for l in lines):
                idx.gap_files.append((f.name, lines))
    return idx


def _case_token_re(case: str) -> re.Pattern:
    """Alnum-boundary match for a case id: 'R1' must not match 'R12' or 'for1'.
    Short ids (R1, S4, B0) substring-match all over prose otherwise -- a
    false-COVERAGE generator via a coincidental mention."""
    return re.compile(r"(?<![A-Za-z0-9])" + re.escape(case.lower()) + r"(?![A-Za-z0-9])")


def _find_successor_registration(case: str, idx: RepoIndex) -> str | None:
    if case in idx.succ_dirs:
        return f"successor registration {idx.succ_dirs[case]}"
    tok = _case_token_re(case)
    for name, low in idx.succ_files:
        if tok.search(low):
            return f"successor draft {name} names {case}"
    return None


def _find_gap_filing(case: str, idx: RepoIndex) -> str | None:
    """State (a): a capability-gap filing on Sanaa's desk that names the case and
    rules out ALL five process classes AND model-form, ALL CO-OCCURRING within a
    GAP_WINDOW_LINES span (not merely somewhere in the same file).  Strict on
    purpose: the loose 'anywhere in file' test cleared fails against megafiles,
    which is an enforcer erring toward a false clear (§2ay.3)."""
    tok = _case_token_re(case)
    for name, lines in idx.gap_files:
        n = len(lines)
        for i, line in enumerate(lines):
            if not tok.search(line):
                continue
            lo, hi = max(0, i - GAP_WINDOW_LINES), min(n, i + GAP_WINDOW_LINES + 1)
            window = "\n".join(lines[lo:hi])
            if not any(re.search(m, window) for m in DESK_MARKERS):
                continue
            if all(any(re.search(pat, window) for pat in pats)
                   for pats in FIVE_PLUS_MODELFORM.values()):
                return (f"capability-gap filing {name} (five-point + model-form + "
                        f"desk marker co-occurring within {GAP_WINDOW_LINES} lines of {case})")
    return None


def find_coverage(row: FailRow, idx: RepoIndex, all_rows: list[FailRow],
                  pass_index: dict[str, list[tuple[str, int]]]) -> Coverage:
    """Return the acceptable state for a fail row, or an empty state == flag it.

    Order: state (b) discharge-by-pass, then (b) registered successor, then (a)
    gap filing.  A mechanism diagnosis with none of these is NOT state (a)
    (§2ay.3) -- it falls through to the empty state and is flagged."""
    # (b) discharged by a landed passing successor
    disc = _find_passing_successor(row.case, all_rows, pass_index)
    if disc:
        return Coverage(state="b", why="discharged by landed passing successor", evidence=disc)
    # (b) active registered successor
    succ = _find_successor_registration(row.case, idx)
    if succ:
        return Coverage(state="b", why="active dated fix-successor registered", evidence=succ)
    # (a) capability-gap filing (five-point + model-form + desk)
    gap = _find_gap_filing(row.case, idx)
    if gap:
        return Coverage(state="a", why="proven OpenFOAM capability gap, filed", evidence=gap)
    # neither -- flagged.  Label WHY: mechanism-diagnosis-only vs bare.
    if any(re.search(m, row.text.lower()) for m in MECHANISM_MARKERS):
        why = "mechanism-diagnosis-only: cause named but NO successor and NO five-point gap filing (§2ay.3)"
    else:
        why = "no successor and no capability-gap filing"
    return Coverage(state="", why=why, evidence="")


def build_pass_index(sources: list[Path], repo: Path) -> dict[str, list[tuple[str, int]]]:
    """Index landed PASS / GATE REACHED rows by case id, for discharge lookup."""
    idx: dict[str, list[tuple[str, int]]] = {}
    for src in sources:
        if not src.exists():
            continue
        rel = str(src.relative_to(repo)) if src.is_absolute() and str(src).startswith(str(repo)) else str(src)
        for i, line in enumerate(src.read_text(errors="replace").splitlines(), 1):
            if "|" not in line:
                continue
            for c in line.split("|"):
                s = _strip_wrappers(c).upper()
                if s in PASS_VERDICTS or s.startswith("PASS ") or s.startswith("GATE REACHED"):
                    case = _row_case(line)
                    if case:
                        idx.setdefault(case, []).append((rel, i))
                    break
    return idx


# --------------------------------------------------------------------------
# SCAN
# --------------------------------------------------------------------------
def scan(sources: list[Path], repo: Path, search_roots: list[Path],
         coverage_fn=find_coverage) -> tuple[list[Result], list[tuple[str, int, str]]]:
    fails, unparsed = enumerate_fails(sources, repo)
    pass_index = build_pass_index(sources, repo)
    idx = build_repo_index(repo, search_roots)
    results: list[Result] = []
    for row in fails:
        cov = coverage_fn(row, idx, fails, pass_index)
        results.append(Result(row=row, coverage=cov, flagged=(cov.state == "")))
    return results, unparsed


def broad_sweep_count(repo: Path) -> int:
    """Count .md files repo-wide that carry a fail token (tracked files, via git
    grep -- ugrep skips gitignored files so git grep is the honest sweep here).
    This over-counts prose mentions; it is the DENOMINATOR for the coverage
    fraction and is labelled as an upper bound in the report."""
    try:
        out = subprocess.run(
            ["git", "grep", "-lE", "GATE FAIL|NOT A RESULT", "--", "*.md"],
            cwd=repo, capture_output=True, text=True, check=False,
        )
        return len([l for l in out.stdout.splitlines() if l.strip()])
    except OSError:
        return -1


# --------------------------------------------------------------------------
# REPORTING
# --------------------------------------------------------------------------
def report(results: list[Result], unparsed: list[tuple[str, int, str]],
           sources: list[Path], repo: Path, draft: bool = True) -> int:
    flagged = [r for r in results if r.flagged]
    covered = [r for r in results if not r.flagged]
    print("=" * 78)
    print("COMPLETION-ENFORCEMENT SCAN -- VERIFICATION_CHARTER §2ay")
    if draft:
        print("STATUS: DRAFT -- believed only after the verification-supervisor has")
        print("        diff-read this instrument AND its plant fired both limbs (§2ay.7).")
    print("A FLAG IS A MEASUREMENT THAT A FAIL IS NOT YET BEING WORKED, NOT A REBUKE (§2ay.6).")
    print("=" * 78)
    print(f"landed fails enumerated : {len(results)}")
    print(f"  FLAGGED (violations)  : {len(flagged)}")
    print(f"  covered (state a / b) : {len(covered)}")
    print()

    if flagged:
        print("-" * 78)
        print("FLAGGED -- standing violations (surfaced to owning team + chief):")
        print("-" * 78)
        for r in flagged:
            print(f"  [{r.row.verdict}] {r.row.case}")
            print(f"      read from : {r.row.source}:{r.row.line}")
            print(f"      why       : {r.coverage.why}")
    else:
        print("NO ROWS FLAGGED by the enumerator's source list.")

    if covered:
        print("-" * 78)
        print("COVERED -- in an acceptable state (NOT re-graded; verdict unchanged):")
        print("-" * 78)
        for r in covered:
            print(f"  [{r.row.verdict}] {r.row.case}  -> state ({r.coverage.state}) {r.coverage.why}")
            print(f"      read from : {r.row.source}:{r.row.line}")
            print(f"      covered by: {r.coverage.evidence}")

    # ---- NON-VACUITY: what the scan COULD NOT SEE (rule 3) ----
    print("-" * 78)
    print("NON-VACUITY -- what this scan COULD NOT SEE (rule 3, §2ay.7):")
    print("-" * 78)
    print(f"  sources read (records/registers, not boards): {len(sources)}")
    for s in sources:
        rel = str(s.relative_to(repo)) if s.is_absolute() and str(s).startswith(str(repo)) else str(s)
        print(f"      - {rel}{'' if s.exists() else '   [MISSING]'}")
    broad = broad_sweep_count(repo)
    if broad >= 0:
        print(f"  .md files repo-wide carrying a fail token (git grep, UPPER BOUND, incl. prose): {broad}")
        print(f"  source-list coverage fraction: {len(sources)}/{broad} of fail-token files "
              f"(= {100*len(sources)/broad:.1f}% of files, an UPPER-BOUND denominator: most of "
              f"those {broad} files are prose mentions, not landed verdict rows).")
    print(f"  fail-token lines seen but UNPARSED (no case id / missing source): {len(unparsed)}")
    for p, ln, why in unparsed[:40]:
        print(f"      - {p}:{ln}  {why}")
    if len(unparsed) > 40:
        print(f"      ... and {len(unparsed)-40} more")
    print("  KNOWN BLIND SPOTS (declared, not discovered):")
    print("    * verdicts recorded only in prose sentences (not table rows) are not enumerated.")
    print("    * successors registered in a shape other than <case>-R/_R/-M dirs or *SUCCESSOR* files.")
    print("    * gap filings without an explicit desk marker + all five §2an classes + model-form.")
    print("    * registers/records not in the source list above (add with --source).")
    print("=" * 78)
    # exit 0: flags are DATA (§2ay.6).  Empty population is a refusal, handled by caller.
    return 0


# ==========================================================================
# PLANTED CONTROL  (§2ay.5, rule 3) -- the point of the whole instrument
# ==========================================================================
def _write_fixture(base: Path) -> tuple[list[Path], list[Path]]:
    """Build a throwaway fixture tree: a register with four fail rows and a
    covering successor/filing set.  Returns (sources, search_roots)."""
    cases = base / "cases"
    cases.mkdir(parents=True, exist_ok=True)
    desk = base / "desk"
    desk.mkdir(parents=True, exist_ok=True)

    # The register: four landed fails + the discharging pass.
    #  FIX001  -> LIMB 1: no successor, no filing            -> MUST flag
    #  FIX002  -> LIMB 1b: mechanism-diagnosis-only          -> MUST flag (why=mechanism)
    #  FIX003  -> LIMB 2a: has a registered successor         -> MUST NOT flag (state b)
    #  FIX004  -> LIMB 2b: discharged by a passing successor  -> MUST NOT flag (state b)
    #  FIX005  -> LIMB 2c: capability-gap filing on the desk  -> MUST NOT flag (state a)
    register = base / "FIXTURE_REGISTER.md"
    register.write_text(
        "# fixture register\n"
        "| # | Case | Verdict | note |\n"
        "|---|---|---|---|\n"
        "| **1** | **FIX001** | **`GATE FAIL`** | bare fail, nobody has touched it |\n"
        "| **2** | **FIX002** | **`NOT A RESULT`** | diverges because of the wall treatment |\n"
        "| **3** | **FIX003** | **`GATE FAIL`** | first attempt, re-run registered |\n"
        "| **4** | **FIX004** | **`GATE FAIL`** | superseded by a pass |\n"
        "| **5** | **FIX004-R2** | **`PASS`** | the discharging re-run |\n"
        "| **6** | **FIX005** | **`NOT A RESULT`** | proven unrecoverable, filed |\n"
    )

    # LIMB 2a: a registered successor directory for FIX003
    succ_dir = cases / "FIX003-R2"
    succ_dir.mkdir(parents=True, exist_ok=True)
    (succ_dir / "PREREGISTRATION.md").write_text(
        "# FIX003-R2 pre-registration\nSuccessor to FIX003's GATE FAIL. Changes the "
        "numerics scheme and re-runs against the same frozen gate.\n"
    )

    # LIMB 2c: a capability-gap filing for FIX005 with ALL five classes + model-form + desk marker
    (desk / "FIX005_CAPABILITY_GAP.md").write_text(
        "# FIX005 -- capability gap, FILED ON SANAA'S DESK\n"
        "Unrecoverability MEASURED. Ruled out at source: bug (code-defect), "
        "solver-selection, preconditioner, numerics-scheme (discretisation), config "
        "(configuration), and model-form. This is a genuine OpenFOAM capability gap.\n"
    )
    return [register], [cases, desk]


def selftest() -> int:
    """Drive the two-limb planted control RED-then-GREEN.  Returns 0 iff both
    limbs fired GREEN and the RED drive was seen to blind the checker; else 2."""
    print("=" * 78)
    print("PLANTED CONTROL -- §2ay.5 / rule 3.  Two limbs, RED-then-GREEN.")
    print("An enforcer whose zero has not been shown able to become non-zero is worthless.")
    print("=" * 78)

    with tempfile.TemporaryDirectory(prefix="verif_enf_plant_") as td:
        base = Path(td)
        sources, roots = _write_fixture(base)

        # ---------- GREEN: the real detector ----------
        results, unparsed = scan(sources, base, roots)
        by_case = {r.row.case: r for r in results}
        flagged = {c for c, r in by_case.items() if r.flagged}
        covered = {c for c, r in by_case.items() if not r.flagged}

        print("\nGREEN run (the real coverage-finder):")
        print(f"  enumerated fails: {sorted(by_case)}")
        print(f"  flagged         : {sorted(flagged)}")
        print(f"  covered         : {sorted(covered)}")

        # LIMB 1: FIX001 (bare) and FIX002 (mechanism-only) MUST be flagged.
        limb1_cases = {"FIX001", "FIX002"}
        limb1_ok = limb1_cases <= flagged
        # confirm FIX002 carries the mechanism-diagnosis-only WHY (§2ay.3)
        mech_ok = "mechanism-diagnosis-only" in by_case.get("FIX002", Result(FailRow("", "", "", 0, ""), Coverage("", "", ""), False)).coverage.why
        # LIMB 2: FIX003 (successor), FIX004 (discharged), FIX005 (gap filing) MUST NOT be flagged.
        limb2_cases = {"FIX003", "FIX004", "FIX005"}
        limb2_ok = limb2_cases.isdisjoint(flagged) and limb2_cases <= covered

        print(f"\n  LIMB 1 (must flag {sorted(limb1_cases)})     : "
              f"{'GREEN' if limb1_ok else 'FAILED'}  "
              f"[mechanism WHY on FIX002: {'yes' if mech_ok else 'NO'}]")
        for c in sorted(limb1_cases):
            r = by_case.get(c)
            if r:
                print(f"      {c}: flagged={r.flagged}  why={r.coverage.why}")
        print(f"  LIMB 2 (must NOT flag {sorted(limb2_cases)}): "
              f"{'GREEN' if limb2_ok else 'FAILED'}")
        for c in sorted(limb2_cases):
            r = by_case.get(c)
            if r:
                print(f"      {c}: flagged={r.flagged}  state=({r.coverage.state}) {r.coverage.evidence}")

        # ---------- RED: cripple the coverage-finder to always-true ----------
        # This is the blind checker §2ay.5 warns of: if the coverage-finder always
        # returns "covered", NOTHING is flagged.  The plant MUST catch this.
        def blind_coverage(row, idx, all_rows, pass_index):
            return Coverage(state="b", why="BLINDED always-true", evidence="(crippled)")

        red_results, _ = scan(sources, base, roots, coverage_fn=blind_coverage)
        red_flagged = {r.row.case for r in red_results if r.flagged}
        red_blinded = red_flagged.isdisjoint(limb1_cases)  # limb 1 no longer flagged
        print(f"\nRED run (coverage-finder crippled to always-true):")
        print(f"  flagged now: {sorted(red_flagged) if red_flagged else '(none)'}")
        print(f"  LIMB 1 stopped flagging under the blind checker: "
              f"{'YES -- plant CATCHES a blind checker' if red_blinded else 'NO'}")

        both_green = limb1_ok and mech_ok and limb2_ok
        red_ok = red_blinded
        print("\n" + "=" * 78)
        if both_green and red_ok:
            print("PLANT VERDICT: BOTH LIMBS FIRED GREEN, AND THE RED DRIVE BLINDED THE CHECKER.")
            print("The instrument is shown able to see a violation and to be blinded when its")
            print("coverage-finder is crippled -- rule 3 satisfied.  A zero from this checker is")
            print("now admissible evidence (subject to the supervisor's diff-read, §2ay.7).")
            print("=" * 78)
            return 0
        print("PLANT VERDICT: REFUSED -- the planted control did NOT fire as required.")
        print(f"  both limbs GREEN: {both_green}   RED drive blinded checker: {red_ok}")
        print("A checker whose plant does not fire prints NO admissible zero (rule 3).")
        print("=" * 78)
        return 2


# --------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------
def repo_root() -> Path:
    here = Path(__file__).resolve()
    for p in [here.parent, *here.parents]:
        if (p / "CLAUDE.md").exists() and (p / ".git").exists():
            return p
    return here.parent.parent


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true",
                    help="drive the two-limb planted control (§2ay.5); exit 2 if it does not fire")
    ap.add_argument("--source", action="append", default=[],
                    help="add a verdict source (repo-relative); repeatable. Default: the §2ay source list.")
    ap.add_argument("--not-draft", action="store_true",
                    help="drop the DRAFT banner (set only after the supervisor's diff-read, §2ay.7)")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    repo = repo_root()
    src_names = args.source if args.source else DEFAULT_SOURCES
    sources = [(repo / s) for s in src_names]
    # search roots for successors / filings: the whole repo for successors is via
    # rglob inside the finders; gap filings are searched under these roots.
    search_roots = [repo / "cases", repo / "docs", repo / "verification", repo / "etc"]

    results, unparsed = scan(sources, repo, search_roots)

    # Empty population is a REFUSAL, never a clean bill (rule 3; 2p.2 posture).
    if not results and not unparsed:
        print("REFUSED (exit 2): the scan enumerated ZERO fail rows AND zero unparsed "
              "fail-token lines from the source list. A reach of zero is not evidence of "
              "a state of zero. Check the source list.", file=sys.stderr)
        return 2

    return report(results, unparsed, sources, repo, draft=not args.not_draft)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
