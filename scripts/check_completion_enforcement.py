#!/usr/bin/env python3
"""
check_completion_enforcement.py -- the STANDING INSTRUMENT for VERIFICATION_CHARTER
§2ay (v1.70, commit 606e658b).  Sanaa ordered "fix until it runs" made executable,
"now and going forward."  This is that instrument.

REFINEMENT 2026-09-07 (verification-supervisor, own instrument; two cross-team blind
spots reported by heat-transfer and dafoam, both STRENGTHENINGS -- they surface more
fails and clear FALSE flags on genuinely-worked ones; no verdict is moved, no gate
widened, §2ay.4 intact):
  * dafoam enumeration -- cases/dafoam/MATRIX_CONTRIBUTION.md added to the sources, and
    CASE_ID_RE grew G-/O- (that matrix's OWN row ids), D#, and SO# branches.  Without the
    G-/O- branch _row_case silently fell through the id cell and mis-keyed 18 rows onto a
    claim-cell ladder rung; the branch keys each row to its own id.
  * recorded-lineage successor reader (§2ay.2(b): "a landed passing successor WHOSE
    LINEAGE IS RECORDED"; "a registered next attempt") -- a fail is state (b) when a
    REGISTRATION (a *PREREGISTRATION*/*SUCCESSOR* file with a line-leading
    `Predecessor:`/`Supersedes:` field, or a gate_*.json "supersedes" key) names it as the
    attempt it supersedes.  This is the SIBLING-RUNG successor the id-suffix pattern cannot
    see (T3d->T3e; and today: T19->T19b, K0eR2->K0eR3 via gate JSONs).  Read ONLY from
    registrations/gate-JSONs, never boards or prose.  Trust boundary declared at the reader.
  * plant extended: a lineage limb (2d), a dafoam-id enumeration limb (1c), and a TARGETED
    RED-2 sub-drive that cripples ONLY the lineage finder and confirms the lineage-only
    fails re-flag -- proving the new path is load-bearing (§28.8 for the new guard).

RECOGNISER PASS 2026-09-07 (verification-supervisor, BOUNDED ADDITIVE, own instrument):
CASE_ID_RE could not parse three REAL heat-transfer rung ids -- an unparsable id is a
SILENT UNDER-FLAG (same defect class as the K0cS fix).  Two pure-recognition supersets:
  * the T-branch grew a single-trailing-letter tail into a multi-letter tail plus an optional
    uppercase-letter-then-digits so multi-letter rungs (T9aD, T9aH, T9a-D, T23G2) key to their
    own id instead of falling to the unparsed channel; verified a SUPERSET (T3,T8,T1b,T1c,T10a,
    T1b-L4,T10a-R2,T10a-VF all match identically) -- see the T-branch line in _CASE_ID_BODY;
  * an E-family branch was ADDED (same shape, E-prefixed) for E4a and the DISTINCT sibling
    E4a2 -- the required digit immediately after E keeps it out of "1.58e9"/"1E5"/ERCOFTAC/EnKF.
These flow into CASE_ID_RE, CASE_ID_ANCHORED_RE (shared _CASE_ID_BODY) and the filename-first
rule.  This ADMITS MORE ids and AUTO-CLEARS NOTHING; surfacing a hidden under-flag can RAISE
the flagged count (the correct direction, §2ay.6).  A RED-4 sub-drive reverts the regex to the
old narrow body and confirms T9aD/T9aH/E4a re-vanish -- proving the branches are load-bearing.

SOURCE-SCOPING PASS 2026-09-07 (verification-supervisor, own instrument): the dafoam-specific
token classes ([GO]-, [ABSW], D#, SO#) were firing on heat-transfer §4.3 data-row labels
B0/B2/B4/B6 in the NON-dafoam source docs/campaigns/T-family/MATRIX_CONTRIBUTION.md, which were
then SPURIOUSLY cleared by a dafoam successor draft (A1WRT2_SUCCESSOR_DRAFT.md) that merely
CONTAINS the string "B2" -- a false clear = UNDER-FLAG (the dangerous direction).  Fix: the
fallback first-cell scan in _row_case is now SOURCE-SCOPED -- it uses the full pattern only for
sources under cases/dafoam/, and CASE_ID_RE_NONDAFOAM (dafoam classes omitted) everywhere else.
The filename-first rule is NOT scoped (full anchored validator) so a legitimately-cited dafoam
results file still validates in any source.  Result: B0/B2/B4/B6 in a non-dafoam source become
honestly UNPARSED (not falsely covered, not falsely flagged).  A RED-5 sub-drive removes the
gate and confirms the B6 under-flag returns -- proving the gate is load-bearing (§28.8).

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
    "cases/dafoam/MATRIX_CONTRIBUTION.md",
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
# The alternation BODY is factored into a constant so the same pattern drives both
# the \b-wrapped scan (CASE_ID_RE) and the ^...$-anchored validation used by the
# authoritative filename-first keying rule in _row_case (CASE_ID_ANCHORED_RE) --
# §2ay.4: one body, no drift between "found a case id" and "this basename token IS
# a whole case id".
# The body is factored into THREE segments so the four dafoam-SPECIFIC token classes
# can be SOURCE-SCOPED (see CASE_ID_RE_NONDAFOAM below).  Concatenated HEAD+DAFOAM+TAIL
# they reproduce the EXACT original body byte-for-byte (order preserved: the cfd F-branch
# stays LAST), so CASE_ID_RE / CASE_ID_ANCHORED_RE are unchanged.
_CASE_ID_BODY_HEAD = (
    r"FIX\d{3}(?:[-_][A-Za-z0-9]+)*"          # synthetic ids used ONLY by --selftest fixtures
    r"|VMFLGPU\d{3}(?:[-_][A-Za-z0-9]+)*"     # ansys GPU cases
    r"|VMFL\d{3}(?:[-_][A-Za-z0-9]+)*"        # ansys cases
    r"|K(?:\d+[a-z]*[A-Z]?|V\d+)(?:R\d+)?"     # F14/K-family rungs: K0,K0c,K0cS,K0cG,K0cT,K0cX,K2b,K2c,K2e,K0eR3,KV1 (SUPERSET of old K0[a-z]?(?:R\d+)?, pure recognition)
    r"|T\d+[a-z]*[A-Z]?\d*(?:[-_][A-Za-z0-9]+)*"  # T-family rungs (SUPERSET of old T\d+[a-z]?: T1b,T1c,T10a,T10a-R2,T23G2 unchanged; ADDS multi-letter T9aD,T9aH,T9a-D)
    r"|E\d+[a-z]*[A-Z]?\d*(?:[-_][A-Za-z0-9]+)*"  # heat-transfer E-family rungs (E4a, E4a2)
    r"|R\d+[a-z]?(?:[-_][A-Za-z0-9]+)*"        # closure R-ladder
    r"|FS\d+(?:[-_][A-Za-z0-9]+)*"             # feature ladder
)
# DAFOAM-SPECIFIC classes -- meaningful ONLY in dafoam sources (cases/dafoam/).  In a
# NON-dafoam source they COLLIDE with heat-transfer §4.3 data-row labels B0/B2/B4/B6
# ([ABSW]\d+) and with scenario labels, FALSELY clearing them (an under-flag: the
# dangerous direction).  Omitted from CASE_ID_RE_NONDAFOAM used for the fallback scan of
# non-dafoam sources.  ORDER within is unchanged from the original body.
_DAFOAM_BRANCHES = (
    r"|SO[-_]?\d+(?:[-_][A-Za-z0-9]+)*"        # dafoam super-optimisation ids (SO-3, SO3, SO3DR)
    r"|D\d+[A-Za-z]*\d*(?:[-_][A-Za-z0-9]+)*"  # dafoam curriculum ids (D6R, D6RF4, D19R, D12R2, D9)
    r"|[GO]-\d+(?:[-_][A-Za-z0-9]+)*"          # dafoam MATRIX_CONTRIBUTION row ids (G-01, O-13)
    r"|[ABSW]\d+(?:[-_][A-Za-z0-9]+)*"         # dafoam ladders (A1, B3, S1, W4)
)
_CASE_ID_BODY_TAIL = (
    r"|F\d+[a-z]?(?:[-_][A-Za-z0-9]+)*"        # cfd F-campaigns (NON-dafoam; stays LAST as in the original body)
)
# FULL body (dafoam sources + filename-first validator): EXACT original value.
_CASE_ID_BODY = _CASE_ID_BODY_HEAD + _DAFOAM_BRANCHES + _CASE_ID_BODY_TAIL
# NON-DAFOAM body: the dafoam-specific classes removed (F-branch and dafoam classes are
# disjoint in leading char, so the F-branch's position change is semantically inert).
_CASE_ID_BODY_CORE = _CASE_ID_BODY_HEAD + _CASE_ID_BODY_TAIL
CASE_ID_RE = re.compile(r"\b(" + _CASE_ID_BODY + r")\b")
# Whole-token validation for the filename-first rule: the basename's <CASEID> part
# (split on the FIRST '_') must be a case id in its ENTIRETY, e.g. K0cS validates.
# Anchored with ^...$ so it does NOT rely on \b, which cannot terminate a
# multi-letter suffix immediately before the '_' of a results-file basename.  Uses the
# FULL body: a legitimately-cited dafoam results file must validate regardless of source.
CASE_ID_ANCHORED_RE = re.compile(r"^(?:" + _CASE_ID_BODY + r")$")
# SOURCE-SCOPED fallback pattern (§2ay.4): used by _row_case's first-cell fallback ONLY
# for NON-dafoam sources, so a dafoam-shaped label (B2) in docs/campaigns/T-family/... is
# NOT mis-keyed to a dafoam id and then falsely cleared by a dafoam draft that merely
# mentions the string "B2".  Filename-first (above) is unaffected and still fires first.
CASE_ID_RE_NONDAFOAM = re.compile(r"\b(" + _CASE_ID_BODY_CORE + r")\b")


def _is_dafoam_source(rel: str) -> bool:
    """A source is a DAFOAM source iff its repo-relative path is under cases/dafoam/.
    Only in a dafoam source do the dafoam-specific token classes ([GO]-, [ABSW], D#, SO#)
    fire in the fallback scan; everywhere else they are omitted (CASE_ID_RE_NONDAFOAM)."""
    return "cases/dafoam/" in rel.replace("\\", "/")

# Authoritative results-file suffixes for the filename-first keying rule.  A row
# that cites `<CASEID>_<SUFFIX>.md` is stating its OWN validating record; that
# citation is more authoritative than any scenario row-label in another cell.
# Case-sensitive UPPERCASE; the multi-word suffixes carry internal underscores and
# are matched AFTER splitting the basename on its FIRST '_' (so <CASEID> is the head).
RESULTS_FILE_SUFFIXES = frozenset({
    "RESULTS", "PREREGISTRATION", "REGRADE", "GATE", "SYNTHESIS",
    "PILOT_RESULTS", "NUSSELT_REGRADE", "UNSTEADINESS_PREREGISTRATION",
})

# A successor id extends a base id with a re-run / model suffix.
SUCCESSOR_SUFFIX_RE = re.compile(r"^(.*?)[-_](R\d+|M\d+|L\d+|S\d+|b|c)(?:[-_].*)?$")

# A line-leading RECORDED-LINEAGE field: a registration declares the attempt it
# supersedes.  §2ay.2(b) recognises "a landed passing successor whose lineage is
# RECORDED" and "a registered next attempt"; the id-suffix pattern above sees only
# <case>-R2 shapes and MISSES a SIBLING-RUNG successor (T3d -> T3e).  This reads the
# lineage the successor's OWN registration declares.  LINE-LEADING label only (after
# optional markdown decoration): a passing prose mention of "predecessor" mid-sentence
# does NOT clear a flag, and the field is read ONLY from registration records
# (build_repo_index gates on the *PREREGISTRATION*/*SUCCESSOR* filename), never boards.
LINEAGE_MD_RE = re.compile(
    r"^\s*[>#*_\s]*\b(?:predecessor|supersedes|succeeds)\b\s*[:=]",
    re.IGNORECASE,
)


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


# Path-basename token: a run of non-whitespace, non-cell-delimiter, non-bracket
# characters ending in `.md` (so a markdown link `](../K0cS_RESULTS.md)` yields the
# bare basename after the last '/').
_MD_TOKEN_RE = re.compile(r"[^\s|()\[\]]+\.md")


def _authoritative_case_from_results_file(cells: list[str]) -> str | None:
    """AUTHORITATIVE FILENAME-FIRST keying (§2ay.4): scan ALL cells for an artifact
    path whose basename is `<CASEID>_<SUFFIX>.md`, where SUFFIX is one of the
    RESULTS_FILE_SUFFIXES (case-sensitive UPPERCASE) and <CASEID> matches CASE_ID_RE
    in its ENTIRETY (CASE_ID_ANCHORED_RE, so K0cS validates).  Return that CASEID.

    Precedence rationale: a row's explicit results-file citation is more
    authoritative than a scenario row-label (e.g. `**S4**`) sitting in another cell.
    Defect it repairs: a heat-transfer fail whose real id (K0cS) appears ONLY inside
    a path -- terminated by '_' -- can never be extracted by the \\b-anchored
    first-matching-cell scan (\\b cannot fire before '_', a word char), so _row_case
    fell through to a scenario label (dafoam `[ABSW]\\d+` branch grabbing `S4`) or to
    the artifact DIRECTORY name (`F14-cooling-ladder`).  Basename split on the FIRST
    '_' bypasses the underscore-boundary problem entirely -- no reliance on \\b inside
    the path.  Returns None if no cell carries such an authoritative basename, and the
    caller then uses the EXISTING first-matching-cell logic unchanged.
    """
    for c in cells:
        for tok in _MD_TOKEN_RE.findall(c):
            base = tok.rsplit("/", 1)[-1]
            if "_" not in base:
                continue
            candidate, rest = base.split("_", 1)
            if not rest.endswith(".md"):
                continue
            suffix = rest[:-len(".md")]
            if suffix in RESULTS_FILE_SUFFIXES and CASE_ID_ANCHORED_RE.match(candidate):
                return candidate
    return None


def _row_case(row_text: str, dafoam_source: bool = True) -> str | None:
    """Extract the case id from a table row.

    FIRST an AUTHORITATIVE filename-first pass: if a cell cites a
    `<CASEID>_<SUFFIX>.md` results/registration file, that CASEID governs (a row's
    own results-file citation outranks a scenario row-label).  ONLY if no such
    authoritative basename is found does it fall back to the first-case-id match in
    the cells (skipping the leading index cell, e.g. `**1**`).

    SOURCE-SCOPING (§2ay.4): the fallback scan uses the FULL pattern for dafoam
    sources but the NON-dafoam pattern (dafoam-specific classes omitted) otherwise,
    so a dafoam-shaped label (B2/B4/B6, S4) in a heat-transfer register is NOT
    mis-keyed to a dafoam id.  `dafoam_source` defaults to True -- the SAFE default:
    a forgotten flag errs toward MORE matching (toward flagging), never toward a
    silent under-flag.  Filename-first is NOT source-scoped: it uses the full
    validator so a legitimately-cited dafoam results file still validates anywhere."""
    if "|" not in row_text:
        return None
    cells = [_strip_wrappers(c) for c in row_text.split("|")]
    # (1) authoritative filename-first (FULL validator, not source-scoped)
    auth = _authoritative_case_from_results_file(cells)
    if auth is not None:
        return auth
    # (2) fallback: first case-id match in a cell, with the SOURCE-SCOPED pattern
    scan_re = CASE_ID_RE if dafoam_source else CASE_ID_RE_NONDAFOAM
    for c in cells:
        # skip pure row-index cells like "1", "#1", ""
        if re.fullmatch(r"#?\d+", c) or c == "":
            continue
        m = scan_re.search(c)
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
        daf = _is_dafoam_source(rel)
        for i, line in enumerate(src.read_text(errors="replace").splitlines(), 1):
            v = _row_verdict(line)
            if v is None:
                continue
            case = _row_case(line, dafoam_source=daf)
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
    lineage_preds: dict[str, str] = field(default_factory=dict)  # predecessor case id -> evidence string


def _canon_lineage_id(s: str) -> str:
    """Canonicalize a case id for LINEAGE-EDGE comparison ONLY: strip hyphens so an
    edge keyed hyphenated (`T10a-R`) and a row keyed un-hyphenated (`T10aR`, from
    filename-first T10aR_RESULTS.md) compare equal.  Applied SYMMETRICALLY -- to the
    STORE key (both extraction sites) AND the LOOKUP key (_find_lineage_successor) --
    so same-hyphenation rows (T10a-VF row + `Predecessor: T10a-VF`) still match
    canon-to-canon.  Dehyphenate only; do NOT uppercase (casing already matches;
    folding case would risk new conflation).  Root cause + referral
    (verification-supervisor, 2026-09-07): the mismatch is asymmetric hyphen SPELLING
    between the row key and the pred key, NOT regex truncation -- CASE_ID_RE already
    captures the full hyphenated id.  Touches neither _row_case nor CASE_ID_RE."""
    return s.replace("-", "")


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
    # ONE pass over *.md per root: candidate desk-marked gap filings (§2ay.4, stored
    # per-line so co-occurrence is tested within a window, not anywhere-in-file) AND
    # recorded-lineage predecessors.  Both EXCLUDE boards/indexes.  Raw text is read
    # once: gap detection needs lowercase, lineage-id extraction needs true case.
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
                raw = f.read_text(errors="replace").splitlines()
            except OSError:
                continue
            low = [l.lower() for l in raw]
            if any(any(re.search(m, l) for m in DESK_MARKERS) for l in low):
                idx.gap_files.append((f.name, low))
            # recorded lineage: ONLY from a REGISTRATION record (a *PREREGISTRATION* or
            # *SUCCESSOR* file), never arbitrary prose -- §2ay.2(b) requires a REGISTERED
            # next attempt, and a bare prose mention of "predecessor" is not one.
            up = f.name.upper()
            if "PREREGISTRATION" in up or "SUCCESSOR" in up:
                for l in raw:
                    if LINEAGE_MD_RE.match(l):
                        pm = CASE_ID_RE.search(l)
                        if pm:
                            idx.lineage_preds.setdefault(
                                _canon_lineage_id(pm.group(1)),  # canon KEY (see _canon_lineage_id); evidence keeps raw form
                                f"registration {f.name} names it predecessor ({l.strip()[:80]})",
                            )
    # gate_*.json "supersedes" keys -- the one STRUCTURED lineage field in the repo
    # (recon 2026-09-07: gate_t19b.json "supersedes":"T19"; K0eR3's gate JSON likewise).
    for root in search_roots:
        if not root.exists() or not root.is_dir():
            continue
        for jf in root.rglob("gate_*.json"):
            if ".git" in jf.parts or not jf.is_file():
                continue
            try:
                txt = jf.read_text(errors="replace")
            except OSError:
                continue
            for mo in re.finditer(r'"supersedes"\s*:\s*"([^"]+)"', txt):
                pm = CASE_ID_RE.search(mo.group(1))
                if pm:
                    idx.lineage_preds.setdefault(
                        _canon_lineage_id(pm.group(1)),  # canon KEY (see _canon_lineage_id); evidence keeps raw form
                        f'gate JSON {jf.name} "supersedes":"{mo.group(1)}"'
                    )
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


def _find_lineage_successor(case: str, idx: RepoIndex) -> str | None:
    """State (b) via RECORDED LINEAGE (§2ay.2(b)): a registration -- a *PREREGISTRATION*/
    *SUCCESSOR* file's line-leading `Predecessor:`/`Supersedes:` field, or a gate_*.json
    "supersedes" key -- names `case` as the attempt it supersedes.  This is the
    SIBLING-RUNG / continuation successor the id-suffix pattern cannot see (T3d -> T3e).

    Trust boundary, DECLARED (§2ay.4): the EDGE is taken from the successor's OWN
    registration, which had to be created to run; a fabricated lineage edge is a deeper
    integrity fault the cross-team gate audit backstops, not something this check can
    detect.  What this reader does NOT do is trust a board or a prose mention -- only a
    registration or a gate JSON, gated in build_repo_index."""
    ev = idx.lineage_preds.get(_canon_lineage_id(case))  # canon LOOKUP key -- symmetric with the store side
    return f"recorded-lineage successor -- {ev}" if ev else None


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
    # (b) recorded-lineage successor -- sibling-rung / continuation attempt whose
    # lineage a registration declares (§2ay.2(b) "whose lineage is recorded")
    lin = _find_lineage_successor(row.case, idx)
    if lin:
        return Coverage(state="b", why="active fix-successor via recorded lineage", evidence=lin)
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
        daf = _is_dafoam_source(rel)
        for i, line in enumerate(src.read_text(errors="replace").splitlines(), 1):
            if "|" not in line:
                continue
            for c in line.split("|"):
                s = _strip_wrappers(c).upper()
                if s in PASS_VERDICTS or s.startswith("PASS ") or s.startswith("GATE REACHED"):
                    case = _row_case(line, dafoam_source=daf)
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
    print("    * successors registered in a shape other than <case>-R/_R/-M dirs, *SUCCESSOR*")
    print("      files, a *PREREGISTRATION*/*SUCCESSOR* line-leading Predecessor:/Supersedes: field,")
    print("      or a gate_*.json \"supersedes\" key (a sibling-rung link in PROSE only is NOT read).")
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
    # The main register is placed UNDER cases/dafoam/ so it is a DAFOAM source: every
    # existing arm (LIMB 1c dafoam ids, the S4 [ABSW] mis-key resurrected by RED-3, RED-4's
    # full-body revert) then behaves EXACTLY as before the source-scoping pass -- the full
    # pattern applies to it.  The NEW source-scoping arm lives in a separate NON-dafoam
    # source (docs/T_FAMILY_MATRIX.md) written below.
    dafoam_dir = cases / "dafoam"
    dafoam_dir.mkdir(parents=True, exist_ok=True)
    register = dafoam_dir / "FIXTURE_REGISTER.md"
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
        "| **7** | **FIX006** | **`GATE FAIL`** | superseded by a SIBLING rung; lineage in its prereg |\n"
        "| **8** | **FIX008** | **`GATE FAIL`** | superseded via a gate JSON supersedes key |\n"
        "| **9** | **G-90** | **`NOT A RESULT`** | dafoam matrix-shaped id -- must ENUMERATE |\n"
        "| **10** | **D6RF9** | **`GATE FAIL`** | dafoam curriculum-shaped id -- must ENUMERATE |\n"
        "| **11** | **SO-9** | **`NOT A RESULT`** | dafoam SO-shaped id -- must ENUMERATE |\n"
        # --- filename-first keying arms (PART 2 / §2ay.4) ---
        # ARM (a): a SCENARIO-LABEL row **S4** whose REAL case (K0cS) is cited ONLY in
        # its results-file path.  MUST key to K0cS (filename-first), NOT the S4 label.
        # Covered by a Predecessor: K0cS registration (GREEN).  With filename-first
        # DISABLED (RED-3) it mis-keys to S4 (the [ABSW]\\d+ branch) -> re-flagged.
        f"| **12** | **S4** | **`GATE FAIL`** | scenario label; real case at {base.name}/K0cS_RESULTS.md |\n"
        # ARM (b): a heat-transfer row cited via K2b_PILOT_RESULTS.md, NO S-label, path
        # under an F14-cooling-ladder directory.  MUST key to K2b.  With filename-first
        # DISABLED it mis-keys to the DIRECTORY fragment F14-cooling-ladder -> re-flagged.
        "| **13** | Nusselt regrade | **`GATE FAIL`** | see runs/F14-cooling-ladder/K2b_PILOT_RESULTS.md |\n"
        # ARM (c): a dafoam matrix row (G-11) whose cited path is NOT a <CASEID>_<SUFFIX>.md
        # shape.  filename-first MUST NOT fire; MUST still key to G-11 (no-regression guard).
        "| **14** | **G-11** | **`NOT A RESULT`** | dafoam row -> cases/dafoam/ladder-a/A3/grading/RESULTS.md |\n"
        # --- RECOGNISER-PASS rows (2026-09-07): REAL heat-transfer rung ids the OLD
        # CASE_ID_RE could not parse.  Multi-letter T (T9aD/T9aH) and the E-family (E4a,
        # and the DISTINCT sibling E4a2).  Each cites its OWN <CASEID>_RESULTS.md so
        # filename-first keys it to its real id; T9aD/T9aH/E4a are each CLEARED by a
        # Predecessor: registration (GREEN), while E4a2 gets NONE and MUST stay flagged --
        # proving E4a's clearing does not leak onto the sibling id.  Under the OLD narrow
        # body (RED-4) none of T9aD/T9aH/E4a can be extracted, so they VANISH.
        f"| **15** | multi-letter T rung | **`GATE FAIL`**    | see {base.name}/T9aD_RESULTS.md |\n"
        f"| **16** | multi-letter T rung | **`NOT A RESULT`** | see {base.name}/T9aH_RESULTS.md |\n"
        f"| **17** | E-family rung       | **`GATE FAIL`**    | see {base.name}/E4a_RESULTS.md |\n"
        f"| **18** | E-family sibling    | **`GATE FAIL`**    | DISTINCT from E4a; see {base.name}/E4a2_RESULTS.md |\n"
        # --- SYMMETRIC hyphen-canon lineage rows (2026-09-07) ---
        # (row 19) ASYMMETRIC: row keys UN-hyphenated (T10aR) but its ONLY coverage is a
        # registration whose Predecessor is HYPHENATED (`T10a-R`).  Symmetric canon clears
        # it; RED (canon->identity) re-flags it.  (This is the real-repo T10aR @1179 case.)
        "| **19** | **T10aR** | **`GATE FAIL`** | cleared ONLY by a HYPHENATED `Predecessor: T10a-R` registration |\n"
        # (row 20) NO-REGRESSION: row AND pred both HYPHENATED (T10a-VF / `Predecessor:
        # T10a-VF`).  MUST stay covered under the fix AND under the RED drive (identity canon
        # still matches hyphen-to-hyphen) -- this is the exact class the one-sided strip broke.
        "| **20** | **T10a-VF** | **`GATE FAIL`** | row hyphenated; cleared by `Predecessor: T10a-VF` (same spelling both sides) |\n"
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

    # LIMB 2d(i): a REGISTRATION whose line-leading Predecessor field names FIX006 -- a
    # sibling-rung successor the id-suffix pattern cannot see.  Filename carries
    # PREREGISTRATION so the lineage gate in build_repo_index admits it.  FIX006 has NO
    # id-suffix successor, NO passing successor, NO gap filing: it is covered ONLY by this.
    (cases / "FIX006x_PREREGISTRATION.md").write_text(
        "# FIX006x pre-registration\n"
        "Predecessor: **FIX006**\n"
        "A sibling-rung next attempt that changes the numerics scheme and re-runs.\n"
    )
    # LIMB 2d(ii): a gate JSON declaring supersedes -> FIX008 (the one STRUCTURED form).
    (cases / "gate_fix008.json").write_text('{\n  "supersedes": "FIX008"\n}\n')

    # ARM (a) lineage: a registration whose line-leading Predecessor field names K0cS.
    # K0cS has NO id-suffix successor, NO passing successor, NO gap filing -- once the
    # filename-first rule keys the S4 row to K0cS, this registration CLEARS it (GREEN).
    (cases / "K0cSx_PREREGISTRATION.md").write_text(
        "# K0cSx pre-registration\n"
        "Predecessor: **K0cS**\n"
        "A next attempt on the K0cS rung that changes the numerics scheme and re-runs.\n"
    )
    # ARM (b) lineage: a registration naming K2b as its predecessor.
    (cases / "K2bx_PREREGISTRATION.md").write_text(
        "# K2bx pre-registration\n"
        "Predecessor: **K2b**\n"
        "A next attempt on the K2b rung that re-runs against the same frozen gate.\n"
    )
    # RECOGNISER-PASS lineage (2026-09-07): Predecessor registrations that CLEAR the
    # multi-letter-T and E-family fails once the new branches key them.  E4a2 gets NONE
    # -- it MUST stay flagged, proving E4a's clearing does not leak onto the sibling id.
    (cases / "T9aDx_PREREGISTRATION.md").write_text(
        "# T9aDx pre-registration\n"
        "Predecessor: **T9aD**\n"
        "A next attempt on the T9aD rung that re-runs against the same frozen gate.\n"
    )
    (cases / "T9aHx_PREREGISTRATION.md").write_text(
        "# T9aHx pre-registration\n"
        "Predecessor: **T9aH**\n"
        "A next attempt on the T9aH rung that re-runs against the same frozen gate.\n"
    )
    (cases / "E4ax_PREREGISTRATION.md").write_text(
        "# E4ax pre-registration\n"
        "Predecessor: **E4a**\n"
        "A next attempt on the E4a rung that re-runs against the same frozen gate.\n"
    )
    # SYMMETRIC hyphen-canon (2026-09-07): ASYMMETRIC spelling -- HYPHENATED pred `T10a-R`
    # clears the UN-hyphenated row T10aR (row 19).  Canon store+lookup makes them match.
    (cases / "T10aR2_PREREGISTRATION.md").write_text(
        "# T10aR2 pre-registration\n"
        "Predecessor: `T10a-R` (explicit, for §2ay linkage).\n"
        "A next attempt on the T10a-R rung that re-runs against the same frozen gate.\n"
    )
    # NO-REGRESSION: SAME hyphen spelling both sides -- HYPHENATED pred `T10a-VF` clears the
    # HYPHENATED row T10a-VF (row 20).  Covered under the fix (canon-to-canon) AND under the
    # RED identity drive (hyphen-to-hyphen) -- the class the one-sided strip broke.
    (cases / "T10aVFx_PREREGISTRATION.md").write_text(
        "# T10aVFx pre-registration\n"
        "Predecessor: `T10a-VF` (explicit, for §2ay linkage).\n"
        "A next attempt on the T10a-VF rung that re-runs against the same frozen gate.\n"
    )

    # ---- SOURCE-SCOPING arm (2026-09-07): dafoam-specific token classes must fire ONLY in
    # dafoam sources.  Live defect fixed: heat-transfer §4.3 data-row labels B0/B2/B4/B6 in
    # docs/campaigns/T-family/MATRIX_CONTRIBUTION.md (a NON-dafoam source) were matched by
    # [ABSW]\d+ and then SPURIOUSLY cleared by the DAFOAM draft A1WRT2_SUCCESSOR_DRAFT.md,
    # which merely CONTAINS the string "B2" -- a false clear = under-flag (the dangerous
    # direction).  These three fixtures reproduce that exactly.
    docs = base / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    # (i) NON-dafoam source whose ONLY token is a dafoam-shaped label (B6).  Under source
    # scoping it MUST become UNPARSED -- not enumerated, not falsely covered, not flagged.
    nondaf_src = docs / "T_FAMILY_MATRIX.md"
    nondaf_src.write_text(
        "# heat-transfer matrix (NON-dafoam source)\n"
        "| # | Case | Verdict | note |\n"
        "|---|---|---|---|\n"
        "| **1** | B6 | **`NOT A RESULT`** | heat-transfer 4.3 data-row unit label; collides with a dafoam ladder id |\n"
    )
    # (ii) DAFOAM source: genuine dafoam ladder rungs A1/B2 that MUST still enumerate.
    dafoam_src = dafoam_dir / "LADDER_MATRIX.md"
    dafoam_src.write_text(
        "# dafoam ladder matrix (DAFOAM source)\n"
        "| # | Case | Verdict | note |\n"
        "|---|---|---|---|\n"
        "| **1** | **A1** | **`GATE FAIL`** | genuine dafoam ladder rung -- must ENUMERATE |\n"
        "| **2** | **B2** | **`GATE FAIL`** | genuine dafoam ladder rung -- must ENUMERATE |\n"
    )
    # (iii) the DAFOAM successor-draft that merely MENTIONS B6 (the exact under-flag being
    # fixed): a *SUCCESSOR* file whose TEXT contains the token "b6" (its name carries A1WRT2,
    # but the coverage-finder searches the TEXT, and "a1wrt2" is not the token "a1", so the
    # genuine A1 row stays flagged).  Gate ON: the non-dafoam B6 row is UNPARSED so this
    # draft never clears it.  Gate OFF (RED-5): B6 re-enumerates via [ABSW] and this draft
    # SPURIOUSLY covers it -- proving the source-gate is load-bearing (§28.8).
    (dafoam_dir / "A1WRT2_SUCCESSOR_DRAFT.md").write_text(
        "# A1WRT2 successor draft (dafoam)\n"
        "This dafoam A1WRT2 attempt also touches the B6 sub-case.\n"
    )
    return [register, nondaf_src, dafoam_src], [cases, desk]


def selftest() -> int:
    """Drive the planted control RED-then-GREEN.  Returns 0 iff every limb fired GREEN
    and BOTH red drives were seen to blind the checker; else 2.  Limbs: 1 (bare +
    mechanism-only fail flagged), 1c (dafoam-shaped ids enumerated), 2 (successor /
    discharged / gap-filing not flagged), 2d (recorded-lineage successor not flagged)."""
    global _find_lineage_successor, _authoritative_case_from_results_file, _canon_lineage_id
    global CASE_ID_RE, CASE_ID_ANCHORED_RE, CASE_ID_RE_NONDAFOAM
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
        # LIMB 2d: recorded-lineage coverage (the NEW path).  FIX006 (md Predecessor field)
        # and FIX008 (gate JSON supersedes) have NO id-suffix successor, NO passing
        # successor, NO gap filing -- they are covered ONLY by recorded lineage.
        lineage_cases = {"FIX006", "FIX008"}
        lineage_ok = lineage_cases.isdisjoint(flagged) and lineage_cases <= covered
        # LIMB 2d-hyphen (2026-09-07, SYMMETRIC canon):
        #  (i) ASYMMETRIC: un-hyphenated row T10aR cleared by HYPHENATED pred `T10a-R`.
        #  (ii) NO-REGRESSION: same-spelling row T10a-VF cleared by HYPHENATED pred `T10a-VF`
        #       -- MUST also stay covered (the class the one-sided strip broke).
        hyphen_case = "T10aR"
        noregress_case = "T10a-VF"
        hyphen_ok = (hyphen_case in covered) and (hyphen_case not in flagged)
        noregress_ok = (noregress_case in covered) and (noregress_case not in flagged)
        # LIMB 1c: dafoam-shaped ids MUST be ENUMERATED (extracted, not dropped to the
        # unparsed channel) -- proving the CASE_ID_RE G-/D/SO branches.  They carry no
        # successor so they are ALSO flagged; the assertion is that they were SEEN.
        dafoam_ids = {"G-90", "D6RF9", "SO-9"}
        dafoam_enumerated = dafoam_ids <= set(by_case)
        dafoam_flagged = dafoam_ids <= flagged

        # ARMS (a)/(b): filename-first keying.  The S4 row and the Nusselt-regrade row
        # MUST enumerate under their REAL ids K0cS / K2b (NOT the S4 label, NOT the
        # F14-cooling-ladder directory) and be CLEARED by their Predecessor: registrations.
        fnfirst_cases = {"K0cS", "K2b"}
        fnfirst_enumerated = fnfirst_cases <= set(by_case)
        fnfirst_covered = fnfirst_cases <= covered
        # the phantom keys must NOT appear now (proves the mis-key is gone, not merely
        # that the real id ALSO appears)
        no_phantom = {"S4", "F14-cooling-ladder"}.isdisjoint(set(by_case))
        fnfirst_ok = fnfirst_enumerated and fnfirst_covered and no_phantom
        # ARM (c): a dafoam matrix row whose path is NOT a <CASEID>_<SUFFIX>.md shape MUST
        # still key to G-11 (filename-first does not fire; existing logic governs).
        dafoam_nofire_ok = "G-11" in by_case

        # RECOGNISER PASS (2026-09-07): multi-letter-T (T9aD/T9aH) and E-family (E4a) ids
        # MUST enumerate under their REAL ids (filename-first via <CASEID>_RESULTS.md) and
        # be CLEARED by their Predecessor: registrations.  E4a and E4a2 MUST be DISTINCT
        # keys, and E4a's clearing MUST NOT leak onto E4a2 (E4a2 has no successor -> stays
        # flagged).  Under the OLD narrow body (RED-4) T9aD/T9aH/E4a re-vanish.
        newT_cases = {"T9aD", "T9aH"}
        newT_enumerated = newT_cases <= set(by_case)
        newT_covered = newT_cases <= covered
        efam_enumerated = {"E4a", "E4a2"} <= set(by_case)
        efam_distinct = (efam_enumerated
                         and by_case["E4a"].row.case == "E4a"
                         and by_case["E4a2"].row.case == "E4a2")
        e4a_covered = "E4a" in covered
        e4a2_distinct_flagged = "E4a2" in flagged   # NOT cleared by / conflated with E4a
        recog_ok = (newT_enumerated and newT_covered and efam_enumerated
                    and efam_distinct and e4a_covered and e4a2_distinct_flagged)

        # SOURCE-SCOPING (2026-09-07): dafoam-specific classes fire ONLY in dafoam sources.
        # (1) the NON-dafoam B6 row MUST be UNPARSED (seen as a fail token, no case id
        #     extracted) -- NOT enumerated, so it cannot be falsely covered.
        # (2) the genuine DAFOAM A1/B2 rows MUST still ENUMERATE (dafoam source, full pattern).
        b6_unparsed = ("B6" not in by_case) and any(
            p.replace("\\", "/").endswith("docs/T_FAMILY_MATRIX.md") for p, _ln, _w in unparsed)
        dafoam_scoped_ids = {"A1", "B2"}
        dafoam_scoped_enum = dafoam_scoped_ids <= set(by_case)
        dafoam_scoped_src_ok = all(
            "cases/dafoam/" in by_case[c].row.source.replace("\\", "/")
            for c in dafoam_scoped_ids if c in by_case)
        srcscope_ok = b6_unparsed and dafoam_scoped_enum and dafoam_scoped_src_ok

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
        print(f"  LIMB 2d (lineage, must NOT flag {sorted(lineage_cases)})  : "
              f"{'GREEN' if lineage_ok else 'FAILED'}")
        for c in sorted(lineage_cases):
            r = by_case.get(c)
            if r:
                print(f"      {c}: flagged={r.flagged}  state=({r.coverage.state}) {r.coverage.evidence}")
        print(f"  LIMB 2d-hyphen (SYMMETRIC canon: hyphenated pred clears both un-hyphenated "
              f"{hyphen_case} AND same-spelling {noregress_case}): "
              f"{'GREEN' if (hyphen_ok and noregress_ok) else 'FAILED'}  "
              f"[T10aR cleared={hyphen_ok}, T10a-VF no-regression={noregress_ok}]")
        for c in [hyphen_case, noregress_case]:
            r = by_case.get(c)
            if r:
                print(f"      {c}: flagged={r.flagged}  state=({r.coverage.state}) {r.coverage.evidence}")
            else:
                print(f"      {c}: MISSING (not enumerated)")
        print(f"  LIMB 1c (dafoam ids {sorted(dafoam_ids)} enumerated): "
              f"{'GREEN' if dafoam_enumerated else 'FAILED'}  "
              f"[all flagged (no successor): {'yes' if dafoam_flagged else 'NO'}]")
        for c in sorted(dafoam_ids):
            print(f"      {c}: {'ENUMERATED' if c in by_case else 'MISSING (dropped to unparsed)'}")
        print(f"  ARMS a/b (filename-first keys {sorted(fnfirst_cases)}, phantoms S4/F14 gone, cleared): "
              f"{'GREEN' if fnfirst_ok else 'FAILED'}  "
              f"[phantom keys absent: {'yes' if no_phantom else 'NO'}]")
        for c in sorted(fnfirst_cases):
            r = by_case.get(c)
            if r:
                print(f"      {c}: flagged={r.flagged}  state=({r.coverage.state}) {r.coverage.evidence}")
            else:
                print(f"      {c}: MISSING (row mis-keyed -- filename-first did not fire)")
        print(f"  ARM c (dafoam G-11 path is NOT results-file shape; still keys G-11): "
              f"{'GREEN' if dafoam_nofire_ok else 'FAILED'}")
        print(f"  RECOGNISER (multi-letter T {sorted(newT_cases)} + E-family E4a/E4a2 distinct): "
              f"{'GREEN' if recog_ok else 'FAILED'}  "
              f"[E4a covered={e4a_covered}, E4a2 distinct+flagged={e4a2_distinct_flagged}]")
        for c in ["T9aD", "T9aH", "E4a", "E4a2"]:
            r = by_case.get(c)
            if r:
                print(f"      {c}: ENUMERATED flagged={r.flagged} state=({r.coverage.state}) "
                      f"{r.coverage.evidence or r.coverage.why}")
            else:
                print(f"      {c}: MISSING (not enumerated -- new branch did not fire)")
        print(f"  SOURCE-SCOPING (non-dafoam B6 UNPARSED; dafoam A1/B2 still enumerate): "
              f"{'GREEN' if srcscope_ok else 'FAILED'}  "
              f"[B6 unparsed in non-dafoam src={b6_unparsed}, dafoam A1/B2 enumerate={dafoam_scoped_enum}]")
        print(f"      non-dafoam B6 in by_case (must be False): {'B6' in by_case}")
        for c in sorted(dafoam_scoped_ids):
            r = by_case.get(c)
            print(f"      {c}: {'ENUMERATED from ' + r.row.source if r else 'MISSING'}")

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

        # ---------- RED-2: cripple ONLY the recorded-lineage finder ----------
        # The whole-coverage RED above blinds everything.  This narrower drive proves
        # the NEW lineage path is itself load-bearing (§28.8 for the new guard): with
        # only the lineage finder blinded, the lineage-only fails MUST re-flag.  If they
        # do not, some OTHER path is silently clearing them and the lineage limb above
        # was vacuous.
        _saved_lin = _find_lineage_successor
        _find_lineage_successor = lambda case, idx: None
        try:
            red2_results, _ = scan(sources, base, roots)
        finally:
            _find_lineage_successor = _saved_lin
        red2_flagged = {r.row.case for r in red2_results if r.flagged}
        lineage_red_ok = lineage_cases <= red2_flagged
        print(f"\nRED-2 run (ONLY the recorded-lineage finder crippled):")
        print(f"  lineage-only fails flagged now: "
              f"{sorted(lineage_cases & red2_flagged) if (lineage_cases & red2_flagged) else '(none)'}")
        print(f"  LIMB 2d fails re-flag with lineage blinded: "
              f"{'YES -- the lineage path is load-bearing' if lineage_red_ok else 'NO'}")

        # ---------- RED-3: cripple ONLY the filename-first keying rule ----------
        # Proves the NEW filename-first path is load-bearing (§28.8): with only the
        # authoritative-filename keyer disabled, the S4 row mis-keys back to its scenario
        # label (S4) and the Nusselt row to the directory fragment (F14-cooling-ladder) --
        # neither of which has a Predecessor registration -- so both RE-FLAG, and the REAL
        # ids K0cS / K2b vanish from the enumeration.  If they did NOT re-break, the GREEN
        # coverage above would have been reachable without the filename rule (vacuous arm).
        _saved_auth = _authoritative_case_from_results_file
        _authoritative_case_from_results_file = lambda cells: None
        try:
            red3_results, _ = scan(sources, base, roots)
        finally:
            _authoritative_case_from_results_file = _saved_auth
        red3_cases = {r.row.case for r in red3_results}
        red3_flagged = {r.row.case for r in red3_results if r.flagged}
        # the real ids must have DISAPPEARED (mis-keyed away) and the phantom mis-keys
        # must now be present AND flagged.
        fnfirst_red_ok = (
            fnfirst_cases.isdisjoint(red3_cases)
            and "S4" in red3_flagged
            and "F14-cooling-ladder" in red3_flagged
        )
        print(f"\nRED-3 run (ONLY the filename-first keying rule crippled):")
        print(f"  real ids {sorted(fnfirst_cases)} still enumerated: "
              f"{sorted(fnfirst_cases & red3_cases) if (fnfirst_cases & red3_cases) else '(none -- mis-keyed away, as expected)'}")
        print(f"  phantom mis-keys now flagged: "
              f"{sorted({'S4','F14-cooling-ladder'} & red3_flagged)}")
        print(f"  ARMS a/b re-break with filename-first blinded: "
              f"{'YES -- the filename-first path is load-bearing' if fnfirst_red_ok else 'NO'}")

        # ---------- RED-4: revert CASE_ID_RE / CASE_ID_ANCHORED_RE to the OLD NARROW body ----------
        # Proves the NEW recogniser branches are load-bearing (§28.8): with the T-branch
        # back to a SINGLE trailing letter and NO E-branch, the multi-letter-T and E-family
        # ids can no longer be extracted (anchored filename-first fails to validate them,
        # and the \b scan cannot terminate a multi-letter/E token before the '_' of the
        # results-file basename) -- so T9aD/T9aH/E4a VANISH from enumeration.  If they did
        # NOT vanish, some OTHER path was extracting them and the RECOGNISER arm above would
        # be vacuous.  The narrow body is derived from the LIVE _CASE_ID_BODY by reversing
        # exactly the two edits, with asserts so a future branch-text drift breaks loudly.
        _old_T = r"T\d+[a-z]?(?:[-_][A-Za-z0-9]+)*"
        _new_T = r"T\d+[a-z]*[A-Z]?\d*(?:[-_][A-Za-z0-9]+)*"
        _new_E = r"|E\d+[a-z]*[A-Z]?\d*(?:[-_][A-Za-z0-9]+)*"
        narrow_body = _CASE_ID_BODY.replace(_new_T, _old_T).replace(_new_E, "")
        assert _new_T in _CASE_ID_BODY, "RED-4: new T-branch not found in _CASE_ID_BODY (drift)"
        assert _new_E in _CASE_ID_BODY, "RED-4: new E-branch not found in _CASE_ID_BODY (drift)"
        assert narrow_body != _CASE_ID_BODY, "RED-4: narrow body identical to new body (revert failed)"
        assert _new_E[1:] not in narrow_body, "RED-4: E-branch not removed from narrow body"
        _saved_re, _saved_anchored = CASE_ID_RE, CASE_ID_ANCHORED_RE
        CASE_ID_RE = re.compile(r"\b(" + narrow_body + r")\b")
        CASE_ID_ANCHORED_RE = re.compile(r"^(?:" + narrow_body + r")$")
        try:
            red4_results, _ = scan(sources, base, roots)
        finally:
            CASE_ID_RE, CASE_ID_ANCHORED_RE = _saved_re, _saved_anchored
        red4_cases = {r.row.case for r in red4_results}
        recog_targets = {"T9aD", "T9aH", "E4a"}
        recog_red_ok = recog_targets.isdisjoint(red4_cases)
        print(f"\nRED-4 run (CASE_ID_RE/ANCHORED reverted to the OLD narrow body -- "
              f"T\\d+[a-z]? and no E-branch):")
        print(f"  recogniser ids {sorted(recog_targets)} still enumerated: "
              f"{sorted(recog_targets & red4_cases) if (recog_targets & red4_cases) else '(none -- unparsable under the narrow body, as expected)'}")
        print(f"  RECOGNISER ids re-break with the old body: "
              f"{'YES -- the new branches are load-bearing' if recog_red_ok else 'NO'}")

        # ---------- RED-5: REMOVE the source gate (non-dafoam pattern := full pattern) ----------
        # Proves the source-gate is load-bearing (§28.8): with the non-dafoam fallback pattern
        # made equal to the FULL pattern, the dafoam-specific [ABSW]\d+ class fires again in the
        # NON-dafoam source, so the B6 row RE-ENUMERATES and is then SPURIOUSLY covered by the
        # dafoam A1WRT2 draft that merely mentions "B6" -- the exact under-flag being fixed.  If
        # B6 did NOT re-enumerate-and-cover, the source-scoping arm above would be vacuous.
        _saved_nd = CASE_ID_RE_NONDAFOAM
        CASE_ID_RE_NONDAFOAM = CASE_ID_RE
        try:
            red5_results, _ = scan(sources, base, roots)
        finally:
            CASE_ID_RE_NONDAFOAM = _saved_nd
        red5_by = {r.row.case: r for r in red5_results}
        b6_reenum = "B6" in red5_by
        b6_spuriously_covered = b6_reenum and not red5_by["B6"].flagged
        srcscope_red_ok = b6_reenum and b6_spuriously_covered
        print(f"\nRED-5 run (source gate removed -- non-dafoam pattern := full pattern):")
        print(f"  non-dafoam B6 re-enumerates via [ABSW]: {b6_reenum}")
        print(f"  and is SPURIOUSLY covered by the dafoam A1WRT2 draft: {b6_spuriously_covered}"
              + (f"  [{red5_by['B6'].coverage.evidence}]" if b6_reenum else ""))
        print(f"  SOURCE-GATE is load-bearing (the under-flag returns when removed): "
              f"{'YES' if srcscope_red_ok else 'NO'}")

        # ---------- RED-6: cripple ONLY the lineage-id canonicalization (canon -> identity) ----------
        # Proves the SYMMETRIC canon is load-bearing for the asymmetric case AND does not
        # break the same-spelling case (§28.8).  With _canon_lineage_id reverted to identity:
        #  - the un-hyphenated row T10aR no longer matches the hyphenated pred `T10a-R` (edge
        #    stored raw `T10a-R`, lookup raw `T10aR`) -> T10aR RE-FLAGS (load-bearing);
        #  - the same-spelling row T10a-VF still matches its `T10a-VF` pred hyphen-to-hyphen
        #    -> STAYS COVERED (proving the canon is not what covered it, so symmetric canon
        #    introduces NO regression on same-hyphenation rows -- the class the one-sided
        #    strip broke).
        _saved_canon = _canon_lineage_id
        _canon_lineage_id = lambda s: s
        try:
            red6_results, _ = scan(sources, base, roots)
        finally:
            _canon_lineage_id = _saved_canon
        red6_flagged = {r.row.case for r in red6_results if r.flagged}
        hyphen_red_ok = hyphen_case in red6_flagged            # asymmetric row re-flags
        noregress_red_ok = noregress_case not in red6_flagged  # same-spelling row unaffected
        print(f"\nRED-6 run (ONLY the lineage-id canonicalization crippled to identity):")
        print(f"  asymmetric {hyphen_case} re-flags: {'YES' if hyphen_red_ok else 'NO'}  "
              f"(canon is load-bearing)")
        print(f"  same-spelling {noregress_case} STAYS covered: {'YES' if noregress_red_ok else 'NO'}  "
              f"(symmetric canon introduces no regression)")

        both_green = (limb1_ok and mech_ok and limb2_ok and lineage_ok and hyphen_ok and noregress_ok
                      and dafoam_enumerated and fnfirst_ok and dafoam_nofire_ok and recog_ok
                      and srcscope_ok)
        red_ok = (red_blinded and lineage_red_ok and fnfirst_red_ok and recog_red_ok
                  and srcscope_red_ok and hyphen_red_ok and noregress_red_ok)
        print("\n" + "=" * 78)
        if both_green and red_ok:
            print("PLANT VERDICT: BOTH LIMBS FIRED GREEN, AND THE RED DRIVE BLINDED THE CHECKER.")
            print("The instrument is shown able to see a violation and to be blinded when its")
            print("coverage-finder is crippled -- rule 3 satisfied.  A zero from this checker is")
            print("now admissible evidence (subject to the supervisor's diff-read, §2ay.7).")
            print("=" * 78)
            return 0
        print("PLANT VERDICT: REFUSED -- the planted control did NOT fire as required.")
        print(f"  all limbs GREEN: {both_green}  (limb1={limb1_ok} mech={mech_ok} "
              f"limb2={limb2_ok} lineage={lineage_ok} hyphen={hyphen_ok} noregress={noregress_ok} "
              f"dafoam-enum={dafoam_enumerated} "
              f"fnfirst={fnfirst_ok} dafoam-nofire={dafoam_nofire_ok} recog={recog_ok} "
              f"srcscope={srcscope_ok})")
        print(f"  all RED drives blinded checker: {red_ok}  "
              f"(whole-coverage={red_blinded} lineage-only={lineage_red_ok} "
              f"filename-first-only={fnfirst_red_ok} recogniser-body={recog_red_ok} "
              f"source-gate={srcscope_red_ok} hyphen-canon={hyphen_red_ok} "
              f"noregress={noregress_red_ok})")
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
