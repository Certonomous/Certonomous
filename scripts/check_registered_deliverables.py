#!/usr/bin/env python3
r"""Registered-deliverables close-out check -- an artefact a pre-registration
promises is either PRESENT at close-out, or a dated departure names it.

WHY THIS EXISTS (docket D473; the R4 finding of 2026-08-23)
===========================================================
R4's frozen pre-registration section 7 registered a deliverable in prose --
`COVERAGE.md`, "ships with `MODEL.md`", at
`cases/RANS_LES_closure_models/R4_sparta_build/PREREGISTRATION.md:199-201`. It
was never delivered, and its non-delivery was never disclosed among the rung's
thirteen dated departures. No control fired, and none could have:

  * a prose-registered deliverable is not a GATE, so no gate row ever counted it;
  * the departure discipline only catches departures somebody NOTICED.

The class -- **registered deliverable absent and undisclosed at close-out** --
is checkable by construction: the frozen pre-registration is on disk, the
artefacts it names either exist at close-out or do not, and a departure section
either names an absent one or does not. That is the shape of a check, not of a
review habit.

The spec this file implements is frozen at
`docs/REGISTERED_DELIVERABLES_CHECK_PROPOSAL.md` section 2. **The binding
charter clause is a DRAFT in that document's section 3 and is NOT in force.**
Nothing here is wired into a gate, into CI, or into any charter. Adoption is
Sanaa's alone.

THE TWO MODES, AND WHY THERE ARE TWO
====================================
VERIFICATION_CHARTER section 17a: a rule over-reaches as easily as it
under-reaches, and only over-reach looks like rigour while it is happening. Old
pre-registrations never promised a machine-readable deliverables list, and prose
parsing over them WILL have false reads. So:

  DECLARED MODE (binding, prospective).  The pre-registration carries a fenced
      block headed `## REGISTERED DELIVERABLES`, one repo-relative path per
      line, optionally annotated. Every listed path must at close-out be either
      PRESENT on disk (and, where the line says `committed`, present in the
      close-out commit) or named in a DATED departure/disclosure section of the
      close-out record. Any listed path ABSENT-UNDISCLOSED refuses close-out,
      exit 2. The block is frozen with the pre-registration, so the checker
      hashes the pre-registration against its committed blob first (CLAUDE.md
      rule 2's own verification, reused).

  HEURISTIC MODE (report-only, retrospective).  Where no block exists,
      candidate deliverables are extracted from prose: backtick-quoted tokens of
      artefact shape (`*.md`, `*.json`, `*.py`, `*.csv`, `artefacts/*`) in
      sentences carrying a commitment verb, outside code fences, excluding
      artefacts that already existed at the pre-registration's own commit (those
      are INPUTS, not products). Each is classified PRESENT / ABSENT-DISCLOSED /
      ABSENT-UNDISCLOSED / CANNOT-PARSE and REPORTED. A heuristic finding never
      exits non-zero until adoption is ruled; `--strict` is the switch a
      ratification would flip, and it is off by default.

THE PLANTED-ZERO CONTROL, WHICH IS THE ONE THAT MATTERS (CLAUDE.md rule 3)
==========================================================================
A zero from a reader not shown able to see a non-zero is not evidence. The
dangerous failure of a prose parser is not a wrong classification -- it is a
document the parser cannot read returning "no deliverables promised" and being
counted as a clean pass over an empty population.

So a SECOND, INDEPENDENT reader runs on every document: the BACKSTOP. It looks
for artefact-shaped tokens in commitment sentences with every backticked span
REMOVED first, so it can only see what the primary extractor structurally
cannot. If the primary extractor returns zero candidates and the backstop
returns any, the document is **CANNOT-PARSE and the checker REFUSES** (exit 2)
-- in either mode. The same refusal covers a `REGISTERED DELIVERABLES` heading
whose fenced block is missing, empty, or carries an unreadable path.

`--report-only` suppresses the non-zero exit for an archive replay, and when it
does it PRINTS the count it suppressed. A suppressed refusal is still on the
page; that is the difference between report-only and silence.

WHERE THIS CHECK DOES NOT REACH, stated so nobody re-derives it by spending
==========================================================================
  * It cannot tell a deliverable that was silently RENAMED from one never
    written. A path that moved reads ABSENT.
  * It cannot read a deliverable's CONTENT. A promised `COVERAGE.md` that ships
    empty reads PRESENT. (R4's own D-14 pair makes this concrete: the late
    `COVERAGE.md` shipped, and a separate finding -- N-B38 -- is that a clip
    blinds the coverage instrument. This check sees the first and not the
    second.)
  * A rung with no close-out record is NOT-CLOSED-OUT, never a fire. Section 17a:
    ask first whether the demanded quantity can exist for that case at all.
  * **It reads inside the repository only, and the lab deliberately keeps large
    run data OUTSIDE it** (`/home/ubuntu/{closure-data, certonomous-runs,
    closure-challenge-benchmark}/`, per CLAUDE.md's WHERE THINGS LIVE). A
    promised artefact that shipped to one of those roots reads ABSENT. Measured
    on the 2026-08-23 replay: of ten fired tokens, at least three were confirmed
    present outside the repository -- `fields_report.json` at
    `/home/ubuntu/closure-data/aposteriori/wu2018/`, and the ladder-b run
    ledgers under `/home/ubuntu/certonomous-runs/`. This is the single largest
    false-fire source in heuristic mode and it is a reason the retrospective
    mode is report-only.
  * Heuristic mode measures prose, and prose was never written to be parsed. Its
    fire rate is published before anyone is asked to believe it (charter
    section 5: replay a new detection rule against the archive before adopting
    it, and publish its fire rate).

DEPARTURES FROM THE LITERAL SPEC, all in the direction of LESS over-reach
========================================================================
  1. The commitment-verb list is exactly the spec's five lemmas -- ship, is
     written, is committed, lands, is recorded -- and is NOT extended (not to
     "delivered", not to "produced"), because the spec is the frozen document.
  2. "ship" is required to be VERBAL: `shipped`/`shipping`/`ships` immediately
     preceded by a determiner (the/a/an/its/their/our/this/that) is adjectival
     ("the shipped baseline", "the shipped hump field") and does not count.
  3. "land" is required to carry a preposition (`lands in`, `landed at`), since
     bare "land" is a noun in this repository's prose.
  Each tightening lowers the fire rate; each is named here so the replay number
  is read against the rule that produced it.

EXIT CODES
==========
  0  clean, or report-only
  1  usage / no such file
  2  REFUSAL -- declared-mode ABSENT-UNDISCLOSED, freeze mismatch in declared
     mode, or CANNOT-PARSE in either mode (and heuristic ABSENT-UNDISCLOSED
     under `--strict`)

Every rule carries a planted control exercised by `--selftest`, which builds a
throwaway git repository of synthetic rungs so the freeze hash, the close-out
commit and the input-exclusion machinery are all exercised for real.
"""

from __future__ import annotations

import argparse
import json
import os
import posixpath
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

ROOT_DEFAULT = Path(__file__).resolve().parent.parent

EXIT_CLEAN = 0
EXIT_USAGE = 1
EXIT_REFUSE = 2

PRESENT = "PRESENT"
ABSENT_DISCLOSED = "ABSENT-DISCLOSED"
ABSENT_UNDISCLOSED = "ABSENT-UNDISCLOSED"
CANNOT_PARSE = "CANNOT-PARSE"
INPUT_EXCLUDED = "INPUT-EXCLUDED"
NOT_CLOSED_OUT = "NOT-CLOSED-OUT"


# ---------------------------------------------------------------------------
# git access
# ---------------------------------------------------------------------------

class Git:
    """Read-only git access, with per-commit tree caches.

    Every method is a read. This checker never writes to the index, never
    stages, never commits (CLAUDE.md rule 10).
    """

    def __init__(self, root: Path):
        self.root = Path(root)
        self._trees: dict[str, set[str] | None] = {}
        self._add_commit: dict[str, str | None] = {}

    def _run(self, *args: str) -> tuple[int, str]:
        p = subprocess.run(
            ["git", "-C", str(self.root), *args],
            capture_output=True, text=True,
        )
        return p.returncode, p.stdout

    def available(self) -> bool:
        rc, _ = self._run("rev-parse", "--git-dir")
        return rc == 0

    def resolve(self, rev: str) -> str | None:
        rc, out = self._run("rev-parse", "--verify", "--quiet", rev + "^{commit}")
        return out.strip() or None if rc == 0 else None

    def tree(self, commit: str) -> set[str] | None:
        """The full set of repo-relative paths in `commit`, cached."""
        if commit not in self._trees:
            rc, out = self._run("ls-tree", "-r", "--name-only", commit)
            self._trees[commit] = set(out.splitlines()) if rc == 0 else None
        return self._trees[commit]

    def add_commit(self, relpath: str) -> str | None:
        """The commit that ADDED `relpath` -- the pre-registration's freeze."""
        if relpath not in self._add_commit:
            rc, out = self._run(
                "log", "--diff-filter=A", "--format=%H", "--follow", "--", relpath
            )
            lines = out.split() if rc == 0 else []
            self._add_commit[relpath] = lines[-1] if lines else None
        return self._add_commit[relpath]

    def last_commit(self, relpath: str) -> str | None:
        rc, out = self._run("log", "-1", "--format=%H", "--", relpath)
        return out.strip() or None if rc == 0 else None

    def blob_id(self, commit: str, relpath: str) -> str | None:
        rc, out = self._run("rev-parse", "--verify", "--quiet", f"{commit}:{relpath}")
        return out.strip() or None if rc == 0 else None

    def hash_object(self, path: Path) -> str | None:
        rc, out = self._run("hash-object", "--", str(path))
        return out.strip() or None if rc == 0 else None

    def show(self, commit: str, relpath: str) -> str | None:
        p = subprocess.run(
            ["git", "-C", str(self.root), "show", f"{commit}:{relpath}"],
            capture_output=True, text=True,
        )
        return p.stdout if p.returncode == 0 else None

    def ls_files(self) -> list[str]:
        rc, out = self._run("ls-files")
        return out.splitlines() if rc == 0 else []


# ---------------------------------------------------------------------------
# markdown surgery
# ---------------------------------------------------------------------------

_FENCE = re.compile(r"^\s{0,3}(```+|~~~+)")


def strip_code_fences(text: str) -> str:
    """Blank out fenced code blocks, preserving line count (and so line numbers)."""
    out: list[str] = []
    fence: str | None = None
    for line in text.splitlines():
        m = _FENCE.match(line)
        if fence is None:
            if m:
                fence = m.group(1)[:3]
                out.append("")
                continue
            out.append(line)
        else:
            out.append("")
            if m and m.group(1).startswith(fence):
                fence = None
    return "\n".join(out)


_ABBREV = {
    "sec", "secs", "eq", "eqs", "fig", "figs", "tab", "tabs", "no", "vs",
    "cf", "ref", "refs", "approx", "p", "pp", "al", "ca", "min", "max",
    "vol", "ch", "app", "art", "para", "e.g", "i.e", "etc", "inc", "st",
}


def split_sentences(paragraph: str) -> list[str]:
    """Split on sentence terminators, guarding this repository's abbreviations.

    `sec. 2.1`, `Eqs. (9)-(10)`, `p. 8` and bare initials do not end sentences.
    Over-splitting is conservative in both directions here: a candidate counts
    only when a commitment verb sits in the SAME sentence, so a spurious split
    can only lose a candidate, never invent one.
    """
    out: list[str] = []
    start = 0
    for m in re.finditer(r"[.!?][\"')\]]*(?=\s|$)", paragraph):
        end = m.end()
        head = paragraph[start:end]
        wm = re.search(r"([A-Za-z0-9.]+)[.!?][\"')\]]*$", head)
        word = wm.group(1).rstrip(".").lower() if wm else ""
        if word in _ABBREV or len(word) <= 1 or word.isdigit():
            continue
        piece = paragraph[start:end].strip()
        if piece:
            out.append(piece)
        start = end
    tail = paragraph[start:].strip()
    if tail:
        out.append(tail)
    return out


_TABLE_ROW = re.compile(r"^\s*\|")


def sentences_of(prose: str) -> list[str]:
    """Every sentence of the document, paragraph by paragraph.

    A markdown TABLE ROW is its own sentence and is never joined to its
    neighbours. Measured on this archive: joining table rows lets a commitment
    verb in one row attach to a path cited in another, and that single mechanism
    accounted for a large share of the replay's false fires. A table is a list
    of independent statements, so it is read as one.
    """
    result: list[str] = []
    for para in re.split(r"\n\s*\n", prose):
        run: list[str] = []
        for ln in para.splitlines():
            if not ln.strip():
                continue
            if _TABLE_ROW.match(ln):
                if run:
                    result.extend(split_sentences(" ".join(run)))
                    run = []
                result.extend(split_sentences(ln.strip()))
            else:
                run.append(ln.strip())
        if run:
            result.extend(split_sentences(" ".join(run)))
    return result


# ---------------------------------------------------------------------------
# the commitment-verb reader, and the artefact-shape reader
# ---------------------------------------------------------------------------

# Exactly the spec's five lemmas. See DEPARTURES in the module docstring for the
# two tightenings (verbal `ship`, prepositional `land`).
_DETERMINER = r"(?:the|a|an|its|their|our|this|that|these|those)"
_COMMIT_VERB = re.compile(
    r"""
      \bship(?:s|ped|ping)?\b
    | (?:\b(?:is|are|was|were|will\s+be|shall\s+be|to\s+be|being)\s+
         (?:written|committed|recorded)\b)
    | (?:\b(?:written|committed|recorded)\s+
         (?:to|in|into|as|with|alongside|beside)\b)
    | (?:\bland(?:s|ed|ing)?\s+
         (?:in|at|on|as|beside|under|with|alongside|next)\b)
    """,
    re.I | re.X,
)

# `the shipped baseline`, `its shipping list`, `A6's shipped runScript.py` --
# adjectival, not a promise. A possessive counts as a determiner here.
_ADJECTIVAL_SHIP = re.compile(
    r"(?:\b" + _DETERMINER + r"|\b[\w.-]+['’]s)\s+shipp(?:ed|ing)\b", re.I
)

_ART_EXT = re.compile(r"\.(md|json|py|csv)$", re.I)
_BAD_CHARS = set("*?[]{}<>|\"'`$ \t")


def has_commitment_verb(sentence: str) -> bool:
    """Does this sentence promise something, in the spec's vocabulary.

    A determiner immediately before `shipped`/`shipping` makes it adjectival
    ("the shipped baseline", "its shipping list"), so those spans are removed
    before the verb reader runs. Everything else is the spec's five lemmas.
    """
    return bool(_COMMIT_VERB.search(_ADJECTIVAL_SHIP.sub(" ", sentence)))


def is_artefact_shape(token: str) -> bool:
    """`*.md`, `*.json`, `*.py`, `*.csv`, `artefacts/*` -- the spec's shapes."""
    tok = token.strip()
    if not tok or tok.startswith("/"):
        return False
    if any(c in _BAD_CHARS for c in tok):
        return False
    if _ART_EXT.search(tok):
        return True
    if re.match(r"^(?:[\w.-]+/)*artefacts/.+", tok):
        return True
    return False


_BACKTICK = re.compile(r"`([^`\n]+)`")
_BARE_ART = re.compile(
    r"(?<![\w/.-])((?:[\w.-]+/)*[\w][\w.-]*\.(?:md|json|py|csv))(?![\w])", re.I
)


def backticked_artefacts(sentence: str) -> list[str]:
    return [m.group(1).strip() for m in _BACKTICK.finditer(sentence)
            if is_artefact_shape(m.group(1))]


def backstop_hits(sentences: Iterable[str]) -> list[str]:
    """The SECOND, INDEPENDENT reader (CLAUDE.md rule 3).

    Backticked spans are removed FIRST, so this reader can only see artefacts
    the primary extractor structurally cannot. A non-empty result beside an
    empty primary result is the planted-zero refusal.
    """
    # MUTATION-POINT: backstop
    found: list[str] = []
    for s in sentences:
        if not has_commitment_verb(s):
            continue
        bare = _BACKTICK.sub(" ", s)
        for m in _BARE_ART.finditer(bare):
            tok = m.group(1)
            if is_artefact_shape(tok):
                found.append(tok)
    return found


# ---------------------------------------------------------------------------
# the declared block
# ---------------------------------------------------------------------------

_DECLARED_HEADING = re.compile(r"^(#{1,6})\s*REGISTERED\s+DELIVERABLES\s*$", re.I)
_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")


@dataclass
class DeclaredEntry:
    path: str
    committed: bool
    description: str
    line: int


@dataclass
class DeclaredBlock:
    entries: list[DeclaredEntry]
    heading_line: int
    problems: list[str] = field(default_factory=list)


def parse_declared_block(text: str) -> DeclaredBlock | None:
    """Find `## REGISTERED DELIVERABLES` and read its fenced block.

    Returns None when the heading is absent (that rung is heuristic-mode).
    Returns a block with `problems` set when the heading IS present but the
    block cannot be read -- a declared population the parser cannot see is a
    refusal, never a silent pass.
    """
    lines = text.splitlines()
    head_idx = None
    head_level = 0
    for i, line in enumerate(lines):
        m = _DECLARED_HEADING.match(line.strip())
        if m:
            head_idx = i
            head_level = len(m.group(1))
            break
    if head_idx is None:
        return None

    block = DeclaredBlock(entries=[], heading_line=head_idx + 1)

    # The first fenced block after the heading, before the next heading of the
    # same or higher level.
    fence: str | None = None
    body: list[tuple[int, str]] = []
    closed = False
    for j in range(head_idx + 1, len(lines)):
        line = lines[j]
        hm = _HEADING.match(line)
        if fence is None and hm and len(hm.group(1)) <= head_level:
            break
        fm = _FENCE.match(line)
        if fence is None:
            if fm:
                fence = fm.group(1)[:3]
            continue
        if fm and fm.group(1).startswith(fence):
            closed = True
            break
        body.append((j + 1, line))

    if fence is None:
        block.problems.append(
            f"heading at line {head_idx + 1} carries no fenced block"
        )
        return block
    if not closed:
        block.problems.append(
            f"fenced block opened after line {head_idx + 1} is never closed"
        )
        return block

    for lineno, raw in body:
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        path = parts[0]
        rest = parts[1:]
        committed = any(t.lower().strip(",;.") == "committed" for t in rest)
        desc = " ".join(t for t in rest if t.lower().strip(",;.") != "committed")
        norm = posixpath.normpath(path)
        if (path.startswith("/") or norm.startswith("..")
                or any(c in _BAD_CHARS for c in path)):
            block.problems.append(
                f"line {lineno}: {path!r} is not a readable repo-relative path"
            )
            continue
        block.entries.append(DeclaredEntry(norm, committed, desc, lineno))

    if not block.entries and not block.problems:
        block.problems.append(
            f"declared block at line {head_idx + 1} parses to zero deliverables"
        )
    return block


# ---------------------------------------------------------------------------
# the disclosure reader
# ---------------------------------------------------------------------------

_DISCLOSURE_HEADING = re.compile(
    r"(departure|addend(?:um|a)|disclosure|correction\s+of\s+record|amendment|"
    r"errat(?:um|a)|(?:never|not)\s+(?:deliver|ship|writt)|late\s+delivery|"
    r"what\s+did\s+not\s+ship|struck)",
    re.I,
)
_DATE = re.compile(r"\b(?:19|20)\d{2}-\d{2}-\d{2}\b")


@dataclass
class DisclosureSection:
    heading: str
    line: int
    dated: bool
    body: str


def disclosure_sections(text: str) -> list[DisclosureSection]:
    """Every departure / disclosure / dated-addendum section of a close-out record."""
    lines = text.splitlines()
    heads: list[tuple[int, int, str]] = []
    for i, line in enumerate(lines):
        m = _HEADING.match(line)
        if m:
            heads.append((i, len(m.group(1)), m.group(2).strip()))

    out: list[DisclosureSection] = []
    for k, (idx, level, title) in enumerate(heads):
        if not _DISCLOSURE_HEADING.search(title):
            continue
        end = len(lines)
        for idx2, level2, _ in heads[k + 1:]:
            if level2 <= level:
                end = idx2
                break
        body = "\n".join(lines[idx:end])
        dated = bool(_DATE.search(title)) or bool(_DATE.search(body[:4000]))
        out.append(DisclosureSection(title, idx + 1, dated, body))
    return out


def is_disclosed(
    tokens: Iterable[str], sections: list[DisclosureSection]
) -> tuple[bool, str]:
    """Is any spelling of this artefact NAMED in a DATED disclosure section.

    The spec's clause is "named in a dated departure/disclosure section". A
    naming inside an UNDATED section is reported as such and does not satisfy
    the clause -- the date is what makes a departure a record rather than a
    remark.
    """
    # MUTATION-POINT: disclosed
    undated_hit = ""
    toks = [t for t in tokens if t]
    for sec in sections:
        for tok in toks:
            pat = re.compile(r"(?<![\w./-])" + re.escape(tok) + r"(?![\w])")
            if pat.search(sec.body):
                where = f'"{sec.heading}" (line {sec.line})'
                if sec.dated:
                    return True, f"named in dated section {where}"
                undated_hit = f"named only in UNDATED section {where}"
    return False, undated_hit or "named in no departure or disclosure section"


# ---------------------------------------------------------------------------
# presence
# ---------------------------------------------------------------------------

def make_exists(root: Path, git: Git, at: str | None) -> Callable[[str], bool]:
    """Path-presence reader.

    Without `--at` this is the working tree. With `--at <commit>` it is that
    commit's tree, which is how a historical close-out is replayed without
    touching the working tree.
    """
    if at:
        tree = git.tree(at) or set()

        def _exists_tree(rel: str) -> bool:
            if rel in tree:
                return True
            prefix = rel.rstrip("/") + "/"
            return any(p.startswith(prefix) for p in tree)

        return _exists_tree

    def _exists_disk(rel: str) -> bool:
        return (root / rel).exists()

    return _exists_disk


def present_at_closeout(exists: Callable[[str], bool], rel: str) -> bool:
    """Did the promised artefact exist at close-out.

    Deliberately a separate entry point from `exists`, which also locates the
    close-out record: the planted control for PRESENT must be breakable without
    also breaking the checker's ability to find the record at all, or the
    mutation evidence for that control proves nothing specific.
    """
    # MUTATION-POINT: exists
    return exists(rel)


def make_suffix_index(root: Path, git: Git, at: str | None) -> dict[str, list[str]]:
    """basename -> every tracked path with that basename.

    Prose in this repository names a document by the shortest unambiguous
    fragment -- `DAFOAM_CHARTER.md`, `analyse_t10a.py`, `T10a_runs/exact.py` --
    while the file lives where the FILING_CHARTER puts it, which is usually not
    the rung's own directory. Resolving a token to the UNIQUE tracked path whose
    tail matches it is what the sentence means. Ambiguous tokens are left
    unresolved rather than guessed.
    """
    paths = sorted(git.tree(at) or []) if at else git.ls_files()
    index: dict[str, list[str]] = {}
    for p in paths:
        index.setdefault(posixpath.basename(p), []).append(p)
    return index


def resolve_by_unique_suffix(token: str, index: dict[str, list[str]]) -> str | None:
    """The one tracked path whose tail is `token`, or None if 0 or many."""
    tok = token.lstrip("./")
    hits = [p for p in index.get(posixpath.basename(tok), [])
            if p == tok or p.endswith("/" + tok)]
    return hits[0] if len(hits) == 1 else None


# ---------------------------------------------------------------------------
# the rung
# ---------------------------------------------------------------------------

_CLOSEOUT_SUFFIXES = ("RESULTS.md", "RESULT.md", "CLOSEOUT.md", "RECORD.md")


def closeout_candidates(prereg_rel: str) -> list[str]:
    d = posixpath.dirname(prereg_rel)
    name = posixpath.basename(prereg_rel)
    cands: list[str] = []

    def add(rel: str) -> None:
        rel = posixpath.normpath(rel)
        if rel != prereg_rel and rel not in cands:
            cands.append(rel)

    m = re.match(r"^(.*?)PREREGISTRATION(.*)\.md$", name, re.I)
    if m:
        stem = m.group(1)
        for suffix in _CLOSEOUT_SUFFIXES:
            add(posixpath.join(d, stem + suffix))
        add(posixpath.join(d, re.sub(r"PREREGISTRATION", "RESULTS", name)))
        add(posixpath.join(d, re.sub(r"PREREGISTRATION", "RESULT", name)))
    for suffix in _CLOSEOUT_SUFFIXES:
        add(posixpath.join(d, suffix))
    return cands


@dataclass
class Finding:
    token: str
    path: str
    verdict: str
    detail: str
    source_line: int = 0


@dataclass
class RungReport:
    prereg: str
    closeout: str | None
    mode: str
    freeze: str
    findings: list[Finding] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    refusals: list[str] = field(default_factory=list)
    fired: list[str] = field(default_factory=list)
    scanned: bool = True
    backstop_seen: int = 0
    raw_candidates: int = 0

    @property
    def fires(self) -> bool:
        return bool(self.fired)


def _line_of(text: str, token: str) -> int:
    pat = re.compile(r"(?<![\w./-])" + re.escape(token) + r"(?![\w])")
    for i, line in enumerate(text.splitlines(), 1):
        if pat.search(line):
            return i
    return 0


def resolve_token(token: str, prereg_rel: str, exists: Callable[[str], bool]) -> str:
    """Repo-relative path for a prose token, preferring one that exists.

    Prose writes a path relative to whatever directory the author had in mind:
    the case (`COVERAGE.md`), a sibling case (`../Schmelzer2020_SpaRTA/RESULTS.md`),
    or the family root (`_common/features/FS2_DEGENERACY_REPORT.md`, written from
    `cases/RANS_LES_closure_models/R4_sparta_build/`). So the resolver walks the
    pre-registration's directory and then each ANCESTOR up to the repository root,
    and finally reads the token as repo-root-relative.

    Every extra candidate can only turn an ABSENT into a PRESENT, never the
    reverse, so this resolution lowers the fire rate and cannot manufacture one.
    """
    d = posixpath.dirname(prereg_rel)
    cands: list[str] = []

    def add(rel: str) -> None:
        rel = posixpath.normpath(rel)
        if not rel.startswith("..") and rel not in cands:
            cands.append(rel)

    add(posixpath.join(d, token))
    if "/" in token.strip("./"):
        # A token carrying a directory fragment may be written from an ancestor
        # (the family root). A BARE filename means "in this rung" and gets no
        # ancestor walk -- otherwise an unrelated same-named file higher up
        # would read as the promised deliverable.
        parts = d.split("/") if d else []
        for k in range(len(parts) - 1, -1, -1):
            add(posixpath.join("/".join(parts[:k]), token) if k else token)
    for c in cands:
        if exists(c):
            return c
    return cands[0] if cands else posixpath.normpath(posixpath.join(d, token))


def analyse_rung(
    prereg_rel: str,
    root: Path,
    git: Git,
    at: str | None = None,
    mode: str = "auto",
    no_suffix_resolution: bool = False,
    suffix_index: dict[str, list[str]] | None = None,
) -> RungReport:
    """One rung: the frozen pre-registration plus its close-out record."""
    exists = make_exists(root, git, at)
    have_git = git.available()
    if suffix_index is None:
        suffix_index = {} if no_suffix_resolution else make_suffix_index(root, git, at)

    if at:
        text = git.show(at, prereg_rel)
        if text is None:
            rep = RungReport(prereg_rel, None, "n/a", "n/a", scanned=False)
            rep.notes.append(f"not present in tree {at[:8]}")
            return rep
    else:
        p = root / prereg_rel
        if not p.exists():
            rep = RungReport(prereg_rel, None, "n/a", "n/a", scanned=False)
            rep.notes.append("no such file")
            return rep
        text = p.read_text(encoding="utf-8", errors="replace")

    # -- freeze verification (CLAUDE.md rule 2, reused) ---------------------
    freeze = "no git"
    if have_git:
        add_c = git.add_commit(prereg_rel)
        if at:
            here = git.blob_id(at, prereg_rel)
            there = git.blob_id(add_c, prereg_rel) if add_c else None
            if here and there and here == there:
                freeze = f"UNCHANGED since freeze {add_c[:8]}"
            elif here and there:
                freeze = f"CHANGED since freeze {add_c[:8]} (blob {here[:8]})"
            else:
                freeze = "freeze commit not resolvable"
        else:
            head_blob = git.blob_id("HEAD", prereg_rel)
            disk_blob = git.hash_object(root / prereg_rel)
            if head_blob is None:
                freeze = "UNTRACKED at HEAD"
            elif disk_blob == head_blob:
                freeze = f"matches committed blob {head_blob[:8]}"
            else:
                freeze = f"MISMATCH: disk {(disk_blob or '?')[:8]} vs HEAD {head_blob[:8]}"

    # -- close-out record ---------------------------------------------------
    closeout = None
    for cand in closeout_candidates(prereg_rel):
        if exists(cand):
            closeout = cand
            break
    if closeout is None:
        # A close-out record the pre-registration names by hand -- but ONLY in
        # the rung's own directory. The spec's unit of analysis is one rung, and
        # a sibling rung's RESULTS.md is a different rung's record: pairing a
        # pre-registration with it reads that rung's departures as this one's,
        # which is worse than finding no record at all.
        own_dir = posixpath.dirname(prereg_rel)
        prose_probe = strip_code_fences(text)
        for m in _BACKTICK.finditer(prose_probe):
            tok = m.group(1).strip()
            if re.search(r"RESULTS?[^/]*\.md$", tok, re.I):
                cand = posixpath.normpath(posixpath.join(own_dir, tok))
                if (posixpath.dirname(cand) == own_dir and cand != prereg_rel
                        and exists(cand)):
                    closeout = cand
                    break

    block = parse_declared_block(text)
    declared = block is not None and mode in ("auto", "declared")
    if mode == "declared" and block is None:
        rep = RungReport(prereg_rel, closeout, "declared", freeze, scanned=False)
        rep.notes.append("no REGISTERED DELIVERABLES block; declared mode not applicable")
        return rep
    if mode == "heuristic":
        declared = False

    rep = RungReport(
        prereg_rel, closeout,
        "declared (binding)" if declared else "heuristic (report-only)",
        freeze,
    )

    if closeout is None:
        rep.notes.append(
            "NOT-CLOSED-OUT: no close-out record found beside the pre-registration; "
            "nothing to grade (charter 17a -- ask first whether the quantity can exist)"
        )
        rep.scanned = False
        return rep

    record_text = (
        git.show(at, closeout) if at else (root / closeout).read_text(
            encoding="utf-8", errors="replace")
    ) or ""
    sections = disclosure_sections(record_text)
    rep.notes.append(
        f"{len(sections)} disclosure section(s), "
        f"{sum(1 for s in sections if s.dated)} dated"
    )

    # -- DECLARED MODE ------------------------------------------------------
    if declared:
        assert block is not None
        if block.problems:
            for prob in block.problems:
                rep.findings.append(
                    Finding("<declared block>", "-", CANNOT_PARSE, prob,
                            block.heading_line)
                )
                rep.refusals.append(f"CANNOT-PARSE: {prob}")
            return rep
        if have_git and freeze.startswith("MISMATCH"):
            rep.refusals.append(
                f"FREEZE MISMATCH: {freeze} -- the declared block is not the block "
                "that was frozen, so it is not evidence"
            )
        if have_git and freeze.startswith("UNTRACKED"):
            rep.refusals.append(
                "FREEZE UNVERIFIABLE: the pre-registration is untracked at HEAD, "
                "so its declared block was never frozen"
            )

        closeout_commit = git.last_commit(closeout) if have_git else None
        for e in block.entries:
            if present_at_closeout(exists, e.path):
                if e.committed:
                    if not have_git:
                        rep.findings.append(Finding(
                            e.path, e.path, CANNOT_PARSE,
                            "line says `committed` but there is no git to check it",
                            e.line))
                        rep.refusals.append(
                            f"CANNOT-PARSE: {e.path} declared `committed`, no git")
                        continue
                    if closeout_commit is None:
                        rep.findings.append(Finding(
                            e.path, e.path, CANNOT_PARSE,
                            "line says `committed` but the close-out record is "
                            "uncommitted, so there is no close-out commit to read",
                            e.line))
                        rep.refusals.append(
                            f"CANNOT-PARSE: {e.path} declared `committed`, "
                            "close-out record uncommitted")
                        continue
                    if git.blob_id(closeout_commit, e.path) is None:
                        rep.findings.append(Finding(
                            e.path, e.path, ABSENT_UNDISCLOSED,
                            f"on disk but NOT in the close-out commit "
                            f"{closeout_commit[:8]}, and the line says `committed`",
                            e.line))
                        rep.fired.append(e.path)
                        rep.refusals.append(
                            f"{ABSENT_UNDISCLOSED}: {e.path} (declared `committed`)")
                        continue
                rep.findings.append(
                    Finding(e.path, e.path, PRESENT, "present at close-out", e.line))
                continue
            ok, why = is_disclosed([e.path, posixpath.basename(e.path)], sections)
            if ok:
                rep.findings.append(
                    Finding(e.path, e.path, ABSENT_DISCLOSED, why, e.line))
            else:
                rep.findings.append(
                    Finding(e.path, e.path, ABSENT_UNDISCLOSED, why, e.line))
                rep.fired.append(e.path)
                rep.refusals.append(f"{ABSENT_UNDISCLOSED}: {e.path} -- {why}")
        return rep

    # -- HEURISTIC MODE -----------------------------------------------------
    prose = strip_code_fences(text)
    sents = sentences_of(prose)
    raw: list[tuple[str, str]] = []      # (token, sentence)
    seen: set[str] = set()
    for s in sents:
        if not has_commitment_verb(s):
            continue
        for tok in backticked_artefacts(s):
            if tok in seen:
                continue
            seen.add(tok)
            raw.append((tok, s))

    hits = backstop_hits(sents)
    rep.backstop_seen = len(hits)
    rep.raw_candidates = len(raw)
    if not raw and hits:
        detail = (
            "extraction returned zero candidates while the independent backstop "
            f"reader saw {len(hits)}: {', '.join(sorted(set(hits))[:5])}"
        )
        rep.findings.append(Finding("<document>", "-", CANNOT_PARSE, detail, 0))
        rep.refusals.append(f"CANNOT-PARSE: {detail}")
        return rep

    if not raw:
        rep.notes.append("no promised artefact found in prose (backstop agrees)")
        return rep

    freeze_commit = git.add_commit(prereg_rel) if have_git else None
    freeze_tree = git.tree(freeze_commit) if freeze_commit else None

    for tok, _sent in raw:
        path = resolve_token(tok, prereg_rel, exists)
        line = _line_of(text, tok)
        if path in (prereg_rel, closeout):
            rep.findings.append(Finding(
                tok, path, INPUT_EXCLUDED,
                "the rung's own pre-registration or close-out record", line))
            continue
        if freeze_tree is not None and path in freeze_tree:
            rep.findings.append(Finding(
                tok, path, INPUT_EXCLUDED,
                f"already existed at the pre-registration's own commit "
                f"{freeze_commit[:8]} -- an input, not a product", line))
            continue
        if present_at_closeout(exists, path):
            rep.findings.append(
                Finding(tok, path, PRESENT, "present at close-out", line))
            continue
        if not no_suffix_resolution:
            elsewhere = resolve_by_unique_suffix(tok, suffix_index)
            if elsewhere and present_at_closeout(exists, elsewhere):
                if freeze_tree is not None and elsewhere in freeze_tree:
                    rep.findings.append(Finding(
                        tok, elsewhere, INPUT_EXCLUDED,
                        f"resolved by unique path-tail match; already existed at "
                        f"the pre-registration's own commit {freeze_commit[:8]} "
                        f"-- an input, not a product", line))
                else:
                    rep.findings.append(Finding(
                        tok, elsewhere, PRESENT,
                        "present at close-out, at the one tracked path whose "
                        "tail matches the token", line))
                continue
        ok, why = is_disclosed([tok, path, posixpath.basename(path)], sections)
        if ok:
            rep.findings.append(Finding(tok, path, ABSENT_DISCLOSED, why, line))
        else:
            rep.findings.append(Finding(tok, path, ABSENT_UNDISCLOSED, why, line))
            rep.fired.append(path)
    return rep


# ---------------------------------------------------------------------------
# reporting
# ---------------------------------------------------------------------------

def print_rung(rep: RungReport, verbose: bool = True) -> None:
    print(f"RUNG  {rep.prereg}")
    print(f"  close-out : {rep.closeout or '-'}")
    print(f"  mode      : {rep.mode}")
    print(f"  freeze    : {rep.freeze}")
    for n in rep.notes:
        print(f"  note      : {n}")
    for f in rep.findings:
        if not verbose and f.verdict in (PRESENT, INPUT_EXCLUDED):
            continue
        mark = "  <- FIRE" if f.verdict == ABSENT_UNDISCLOSED else ""
        loc = f":{f.source_line}" if f.source_line else ""
        print(f"  {f.verdict:<18} {f.token}{mark}")
        print(f"      path {f.path}   (named at {rep.prereg}{loc})")
        print(f"      {f.detail}")


def run_one(
    prereg_rel: str, root: Path, git: Git, at: str | None, mode: str,
    strict: bool, report_only: bool, verbose: bool = True,
    no_suffix_resolution: bool = False,
) -> int:
    rep = analyse_rung(prereg_rel, root, git, at, mode,
                       no_suffix_resolution=no_suffix_resolution)
    print_rung(rep, verbose)
    refusals = list(rep.refusals)
    if strict and "heuristic" in rep.mode:
        refusals += [f"{ABSENT_UNDISCLOSED}: {p} (--strict)" for p in rep.fired]
    if refusals:
        print()
        for r in refusals:
            print(f"  REFUSE: {r}")
    if rep.fired and not refusals:
        print()
        print(f"  FIRE: {len(rep.fired)} registered deliverable(s) absent and "
              f"undisclosed -- {', '.join(rep.fired)}")
        print("  REPORT-ONLY (heuristic mode, charter 17a): exit 0. "
              "--strict would refuse.")
    if refusals:
        if report_only:
            print(f"  REPORT-ONLY: {len(refusals)} refusal(s) suppressed, "
                  "listed above, exit 0")
            return EXIT_CLEAN
        return EXIT_REFUSE
    return EXIT_CLEAN


def run_replay(
    root: Path, git: Git, at: str | None, strict: bool, report_only: bool,
    as_json: bool, verbose: bool, no_suffix_resolution: bool = False,
) -> int:
    if at:
        tree = git.tree(at) or set()
        files = sorted(f for f in tree if re.search(r"PREREGISTRATION.*\.md$", f))
    else:
        files = sorted(f for f in git.ls_files()
                       if re.search(r"PREREGISTRATION.*\.md$", f))

    index = {} if no_suffix_resolution else make_suffix_index(root, git, at)
    reports = [
        analyse_rung(f, root, git, at, "auto",
                     no_suffix_resolution=no_suffix_resolution,
                     suffix_index=index)
        for f in files
    ]

    graded = [r for r in reports if r.scanned]
    skipped = [r for r in reports if not r.scanned]
    fired = [r for r in graded if r.fires]
    cannot = [r for r in graded
              if any(f.verdict == CANNOT_PARSE for f in r.findings)]
    declared = [r for r in graded if r.mode.startswith("declared")]

    if verbose:
        for r in reports:
            if r.fires or any(f.verdict == CANNOT_PARSE for f in r.findings):
                print_rung(r, verbose=False)
                print()

    n_graded = len(graded)
    rate = (len(fired) / n_graded * 100.0) if n_graded else 0.0

    print("=" * 72)
    print("ARCHIVE REPLAY -- charter section 5 (replay before adoption, publish "
          "the fire rate)")
    print("=" * 72)
    print(f"  pre-registrations found          : {len(reports)}")
    print(f"  NOT-CLOSED-OUT / unreadable      : {len(skipped)}  (not graded)")
    print(f"  records scanned (graded)         : {n_graded}")
    print(f"  declared-mode rungs              : {len(declared)}")
    print(f"  heuristic-mode rungs             : {n_graded - len(declared)}")
    print(f"  CANNOT-PARSE refusals            : {len(cannot)}")
    backstop_live = [r for r in graded if r.backstop_seen]
    extractor_live = [r for r in graded if r.raw_candidates]
    print(f"  -- the zero above, planted (rule 3):")
    print(f"     documents where the primary extractor saw a candidate : "
          f"{len(extractor_live)}")
    print(f"     documents where the INDEPENDENT backstop saw one      : "
          f"{len(backstop_live)}")
    print(f"     (a CANNOT-PARSE is backstop-sees-and-extractor-does-not; both "
          f"readers are shown live on this corpus, so the zero is a reading, "
          f"not a blind spot)")
    print(f"  FIRES (>=1 ABSENT-UNDISCLOSED)   : {len(fired)}")
    print(f"  FIRE RATE                        : {len(fired)}/{n_graded} "
          f"= {rate:.1f}%")
    print()
    print("  fired paths:")
    for r in fired:
        print(f"    {r.prereg}")
        for p in r.fired:
            print(f"        -> {p}")
    if cannot:
        print()
        print("  CANNOT-PARSE (refusal, planted-zero principle):")
        for r in cannot:
            print(f"    {r.prereg}")

    if as_json:
        print()
        print(json.dumps({
            "found": len(reports),
            "not_graded": len(skipped),
            "scanned": n_graded,
            "declared": len(declared),
            "cannot_parse": len(cannot),
            "fires": len(fired),
            "fire_rate_pct": round(rate, 2),
            "fired_paths": {r.prereg: r.fired for r in fired},
            "cannot_parse_paths": [r.prereg for r in cannot],
        }, indent=2))

    total_refusals = sum(len(r.refusals) for r in graded)
    if strict:
        total_refusals += sum(len(r.fired) for r in graded
                              if "heuristic" in r.mode)
    if total_refusals and not report_only:
        return EXIT_REFUSE
    if total_refusals:
        print()
        print(f"  REPORT-ONLY: {total_refusals} refusal(s) suppressed, "
              "listed above, exit 0")
    return EXIT_CLEAN


# ---------------------------------------------------------------------------
# planted controls
# ---------------------------------------------------------------------------

F = "```"


def _write(p: Path, s: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True, capture_output=True, text=True,
    )


def _build_control_repo(repo: Path) -> None:
    """A throwaway git repository of synthetic rungs.

    It is a REAL repository so the freeze hash, the close-out commit and the
    input-exclusion tree are exercised for real rather than stubbed.
    """
    repo.mkdir(parents=True, exist_ok=True)
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "control@localhost")
    _git(repo, "config", "user.name", "planted control")

    dec = lambda body: f"## REGISTERED DELIVERABLES\n\n{F}\n{body}\n{F}\n"

    # ---- commit 1: the freeze. Inputs exist; products do not. -------------
    _write(repo / "cases/h2/BASELINES.md", "# baselines\n\nAn INPUT.\n")

    _write(repo / "cases/c1/PREREGISTRATION.md",
           "# PREREGISTRATION -- control C1\n\nFrozen 2026-08-23.\n\n"
           "## 7. Deliverables\n\nThe model card ships with the fit.\n\n"
           + dec("cases/c1/MODEL.md    the frozen term set and coefficients"))
    _write(repo / "cases/c2/PREREGISTRATION.md",
           "# PREREGISTRATION -- control C2\n\nFrozen 2026-08-23.\n\n"
           "## 7. Deliverables\n\nThe coverage note ships with the model card.\n\n"
           + dec("cases/c2/COVERAGE.md    feature ranges per training family"))
    _write(repo / "cases/c3/PREREGISTRATION.md",
           "# PREREGISTRATION -- control C3\n\nFrozen 2026-08-23.\n\n"
           "## 7. Deliverables\n\nThe coverage note ships with the model card.\n\n"
           + dec("cases/c3/COVERAGE.md    feature ranges per training family"))
    _write(repo / "cases/c4/PREREGISTRATION.md",
           "# PREREGISTRATION -- control C4\n\nFrozen 2026-08-23.\n\n"
           "## 7. Coverage\n\n"
           "The coverage note COVERAGE.md ships with the model card, and states "
           "each selected feature's range on each training family.\n")
    _write(repo / "cases/c5/PREREGISTRATION.md",
           "# PREREGISTRATION -- control C5\n\nFrozen 2026-08-23.\n\n"
           "## REGISTERED DELIVERABLES\n\n"
           "cases/c5/COVERAGE.md -- the coverage note\n\n"
           "## 8. Compute\n\nZero.\n")
    _write(repo / "cases/c6/PREREGISTRATION.md",
           "# PREREGISTRATION -- control C6\n\nFrozen 2026-08-23.\n\n"
           + dec("cases/c6/MODEL.md    the frozen term set"))
    _write(repo / "cases/h1/PREREGISTRATION.md",
           "# PREREGISTRATION -- control H1\n\nFrozen 2026-08-23.\n\n"
           "## 4. The freeze\n\n"
           "The selected term set is frozen per model class and written to "
           "`MODEL.md` before any propagation run.\n")
    _write(repo / "cases/h2/PREREGISTRATION.md",
           "# PREREGISTRATION -- control H2\n\nFrozen 2026-08-23.\n\n"
           "## 2. Baselines\n\n"
           "The reference values are recorded in `BASELINES.md` and are read, "
           "never rewritten.\n")
    _git(repo, "add", "--", "cases")
    _git(repo, "commit", "-q", "-m", "freeze: the pre-registrations and the inputs")

    # ---- commit 2: close-out. Some products ship, some do not. ------------
    _write(repo / "cases/c1/MODEL.md", "# MODEL\n\nDelivered.\n")
    _write(repo / "cases/c1/RESULTS.md",
           "# RESULTS -- C1\n\n## 0. VERDICT\n\nPASS\n\n"
           "## 9. Departures from the preregistration -- dated 2026-08-23\n\n"
           "None.\n")
    _write(repo / "cases/c2/RESULTS.md",
           "# RESULTS -- C2\n\n## 0. VERDICT\n\nGATE FAIL\n\n"
           "## 9. Departures from the preregistration -- dated 2026-08-23\n\n"
           "D1. `COVERAGE.md` was NOT written. The lane ended at the freeze and "
           "the coverage note is deferred to the next rung.\n")
    _write(repo / "cases/c3/RESULTS.md",
           "# RESULTS -- C3\n\n## 0. VERDICT\n\nGATE FAIL\n\n"
           "## 9. Departures from the preregistration -- dated 2026-08-23\n\n"
           "D1. The seed count dropped from three to one on the propagation "
           "runs, and the reduction is reported in section 10.\n")
    _write(repo / "cases/c4/RESULTS.md",
           "# RESULTS -- C4\n\n## 0. VERDICT\n\nPASS\n\n"
           "## 9. Departures -- dated 2026-08-23\n\nNone.\n")
    _write(repo / "cases/c5/RESULTS.md",
           "# RESULTS -- C5\n\n## 0. VERDICT\n\nPASS\n\n"
           "## 9. Departures -- dated 2026-08-23\n\nNone.\n")
    _write(repo / "cases/c6/MODEL.md", "# MODEL\n\nDelivered.\n")
    _write(repo / "cases/c6/RESULTS.md",
           "# RESULTS -- C6\n\n## 0. VERDICT\n\nPASS\n\n"
           "## 9. Departures -- dated 2026-08-23\n\nNone.\n")
    _write(repo / "cases/h1/MODEL.md", "# MODEL\n\nDelivered.\n")
    _write(repo / "cases/h1/RESULTS.md",
           "# RESULTS -- H1\n\n## 0. VERDICT\n\nPASS\n\n"
           "## 9. Departures -- dated 2026-08-23\n\nNone.\n")
    _write(repo / "cases/h2/RESULTS.md",
           "# RESULTS -- H2\n\n## 0. VERDICT\n\nPASS\n\n"
           "## 9. Departures -- dated 2026-08-23\n\nNone.\n")
    _git(repo, "add", "--", "cases")
    _git(repo, "commit", "-q", "-m", "close-out records")

    # ---- C6 only: the frozen file is edited on disk after the freeze ------
    p = repo / "cases/c6/PREREGISTRATION.md"
    p.write_text(p.read_text() + "\nA line added after the freeze.\n",
                 encoding="utf-8")


CONTROLS: list[tuple[str, str, str, set[str], int]] = [
    # id, prereg, what it plants, expected verdicts, expected exit
    ("C1  (spec) declared, deliverable PRESENT",
     "cases/c1/PREREGISTRATION.md",
     "a prereg naming an existing file -> silent",
     {PRESENT}, EXIT_CLEAN),
    ("C2  (spec) declared, ABSENT but DISCLOSED",
     "cases/c2/PREREGISTRATION.md",
     "a prereg naming a missing file the departure section names -> silent",
     {ABSENT_DISCLOSED}, EXIT_CLEAN),
    ("C3  (spec) declared, ABSENT and UNDISCLOSED",
     "cases/c3/PREREGISTRATION.md",
     "a prereg naming a missing, undisclosed file -> MUST FIRE",
     {ABSENT_UNDISCLOSED}, EXIT_REFUSE),
    ("C4  (spec) planted zero: extraction blind, backstop sees",
     "cases/c4/PREREGISTRATION.md",
     "a prereg visibly naming a deliverable on which extraction returns zero "
     "candidates -> CANNOT-PARSE, refuse",
     {CANNOT_PARSE}, EXIT_REFUSE),
    ("C5  (extra) declared heading, unreadable block",
     "cases/c5/PREREGISTRATION.md",
     "a REGISTERED DELIVERABLES heading with no fenced block -> CANNOT-PARSE",
     {CANNOT_PARSE}, EXIT_REFUSE),
    ("C6  (extra) declared block not frozen",
     "cases/c6/PREREGISTRATION.md",
     "the pre-registration on disk differs from its committed blob -> refuse",
     {PRESENT}, EXIT_REFUSE),
    ("H1  (extra) heuristic, deliverable PRESENT",
     "cases/h1/PREREGISTRATION.md",
     "prose 'written to `MODEL.md`', delivered -> silent, and the extractor is "
     "shown able to see a backticked deliverable",
     {PRESENT}, EXIT_CLEAN),
    ("H2  (extra) heuristic, INPUT not mistaken for a product",
     "cases/h2/PREREGISTRATION.md",
     "prose 'recorded in `BASELINES.md`' where the file predates the freeze -> "
     "excluded as an input, and NOT a false CANNOT-PARSE",
     {INPUT_EXCLUDED}, EXIT_CLEAN),
]


def selftest(verbose: bool = False) -> int:
    """Build the planted controls and assert each one behaves as registered."""
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="rdc_selftest_") as tmp:
        repo = Path(tmp) / "repo"
        _build_control_repo(repo)
        git = Git(repo)

        print("PLANTED CONTROLS -- check_registered_deliverables.py")
        print("=" * 72)
        for name, prereg, what, want_verdicts, want_exit in CONTROLS:
            rep = analyse_rung(prereg, repo, git, None, "auto")
            got = {f.verdict for f in rep.findings}
            refusals = list(rep.refusals)
            got_exit = EXIT_REFUSE if refusals else EXIT_CLEAN
            ok = (want_verdicts <= got) and got_exit == want_exit
            print(f"{'ok  ' if ok else 'FAIL'}  {name}")
            print(f"        plants   : {what}")
            print(f"        verdicts : {', '.join(sorted(got)) or '(none)'}")
            print(f"        exit     : {got_exit} (expected {want_exit})")
            if refusals:
                print(f"        refusal  : {refusals[0]}")
            if verbose:
                print_rung(rep)
            if not ok:
                failures.append(
                    f"{name}: verdicts {sorted(got)} (wanted {sorted(want_verdicts)}"
                    f" subset), exit {got_exit} (wanted {want_exit})"
                )
        print("=" * 72)

    if failures:
        print(f"SELFTEST FAILED -- {len(failures)} control(s) did not behave as "
              "registered:")
        for f in failures:
            print(f"  {f}")
        return EXIT_USAGE
    print(f"SELFTEST PASSED -- {len(CONTROLS)} planted controls, "
          f"{sum(1 for c in CONTROLS if c[0].startswith(('C1', 'C2', 'C3', 'C4')))}"
          " of them the four the spec requires.")
    return EXIT_CLEAN


# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--root", default=str(ROOT_DEFAULT),
                    help="repository root (default: this script's repository)")
    ap.add_argument("--prereg", help="repo-relative path of one pre-registration")
    ap.add_argument("--replay", action="store_true",
                    help="archive replay over every tracked *PREREGISTRATION*.md")
    ap.add_argument("--at", metavar="COMMIT",
                    help="read the rung from this commit's tree instead of the "
                         "working tree -- how a historical close-out is replayed "
                         "without touching the working tree")
    ap.add_argument("--mode", choices=("auto", "declared", "heuristic"),
                    default="auto")
    ap.add_argument("--strict", action="store_true",
                    help="promote heuristic ABSENT-UNDISCLOSED findings to "
                         "refusals; OFF by default, and the switch a "
                         "ratification would flip")
    ap.add_argument("--report-only", action="store_true",
                    help="print every refusal but exit 0, naming the count "
                         "suppressed")
    ap.add_argument("--selftest", action="store_true",
                    help="build the planted controls and assert each fires")
    ap.add_argument("--no-suffix-resolution", action="store_true",
                    help="do not resolve a prose token to the unique tracked "
                         "path whose tail matches it; the stricter resolver, "
                         "kept so both fire rates can be published")
    ap.add_argument("--json", action="store_true",
                    help="emit the replay summary as JSON as well")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest(args.verbose)

    root = Path(args.root).resolve()
    git = Git(root)
    at = None
    if args.at:
        at = git.resolve(args.at)
        if at is None:
            print(f"error: cannot resolve commit {args.at!r}", file=sys.stderr)
            return EXIT_USAGE

    if args.replay:
        return run_replay(root, git, at, args.strict, args.report_only,
                          args.json, True, args.no_suffix_resolution)
    if args.prereg:
        rel = args.prereg
        if os.path.isabs(rel):
            rel = os.path.relpath(rel, root)
        rel = posixpath.normpath(rel.replace(os.sep, "/"))
        return run_one(rel, root, git, at, args.mode, args.strict,
                       args.report_only, True, args.no_suffix_resolution)

    ap.print_help()
    return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
