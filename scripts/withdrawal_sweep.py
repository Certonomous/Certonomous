#!/usr/bin/env python3
"""The weekly sweep that SUPERVISION_CHARTER §3a names as its own enforcement.

    "A superseded entry whose author is gone is withdrawn by the current family
     supervisor, within the cycle. A weekly sweep asserts zero unowned
     supersessions."   -- Katie, 2026-08-11, SUPERVISION_CHARTER.md §3a (v1.1)

§3a ends: "A rule without a sweep is a preference." This module is the sweep.
It answers exactly one question -- **are there supersessions in this repo with
no owning ROLE?** -- and it answers it in three values, PASS / FAIL / UNKNOWN.

--------------------------------------------------------------------------
1. THE TWO DEFINITIONS, TAKEN FROM THE CHARTER CORPUS AND NOT FROM CONVENIENCE
--------------------------------------------------------------------------

**What a supersession IS, on disk.** §3a does not say. It names three states --
"every **withdrawn, retracted or superseded** entry" -- and stops. The on-disk
form is fixed elsewhere, by `docs/MEMORY_ARCHITECTURE.md` §8.1 ("amended in
place, dated, with the original text retained -- never a silent edit, and never
a deletion") and, operationally, by §8.2, which measures the corpus with a
five-token marker vocabulary and reports 36 markers across 27 files at
2026-08-10:

    [AMENDED   [CORRECTED   [WITHDRAWN   [SUPERSEDED   [RETRACTED

So a supersession on disk is **a bracketed in-place marker drawn from that
vocabulary**. This module does not invent the vocabulary; §8.2 already
published it and already counted with it.

**The gated subset is §3a's own three words, and that is deliberate.** §3a says
"withdrawn, retracted or superseded". `[AMENDED` and `[CORRECTED` are the
§8.1 amendment forms -- an author repairing their own record in place -- and
§3a does not put a withdrawal duty on them. Gating on all five would be my
convenience, not the charter's text, and would swamp a real signal with
self-repairs. So:

    GATED  set: WITHDRAWN, RETRACTED, SUPERSEDED   (§3a's literal three)
    WIDER  set: + AMENDED, CORRECTED               (§8.2's five, REPORTED only)

Both counts print. The verdict is taken on the gated set.

**What "unowned" means, and the trap in defining it.** §3a fixes the owner by
RULE: "the **family supervisor for the record's family** owns the withdrawal,
and the chief owns it where no family does." Read literally that makes every
supersession owned by construction -- derive the family from the path, apply
the rule, and the answer is always "owned". **A gate whose quantity is
derivable by construction from its own inputs is an identity, not a control**
(VERIFICATION_CHARTER §2a, W-2). A sweep built on the literal reading could not
fail, and a sweep that cannot fail is a green light wired to nothing.

So this sweep measures the only thing about ownership that CAN fail: whether
the record **names** one. §3a's own sweep clause asks for exactly that word --
"every withdrawn, retracted or superseded entry has a **named** current owner".
Naming is the observable; the rule's mapping is not.

    OWNED        -- the marker's own block (or, in a docket table, its row)
                    names a durable ROLE: chief / chief supervisor / a family
                    supervisor / Katie / the owner / fleet.
    SESSION_ONLY -- it names only a session, author, agent or review round.
                    §3a exists BECAUSE "authors here are sessions and sessions
                    end", so a session attribution is a name that points at a
                    ghost. Counted as unowned, reported as its own class.
    UNOWNED      -- it names nobody at all.

**What §3a leaves genuinely unpinned, reported rather than papered over:**

  (a) No owner FIELD exists anywhere in the corpus convention. §8.1/§8.2 fix
      the marker and the date; neither fixes a place to write the owner. This
      sweep therefore reads prose, and prose is a weaker instrument than a
      field would be. The durable fix is a field, not a better regex.
  (b) "fleet" is in `docs/DOCKET.md`'s own owner vocabulary (fleet / chief /
      Katie) but §3a reasons explicitly against diffuse ownership -- "the item
      would be everybody's and therefore nobody's, which is the failure this
      rule exists to close". It is counted OWNED here, because the docket
      sanctions it, and broken out separately as DIFFUSE so the chief can rule.
  (c) §3a's SECOND clause -- "every refutation filed against a live claim has a
      withdrawal either done or assigned" -- is NOT swept. See §3 below.

--------------------------------------------------------------------------
2. WHY THE VERDICT HAS THREE VALUES AND NOT TWO
--------------------------------------------------------------------------

Docket B1 is the silent-zero defect class: a sweep whose filter produced the
zero, reporting it as a clean bill. This sweep returns UNKNOWN, never PASS, on
every one of these:

  * zero candidate supersessions found          -- an empty set is not a clean
                                                   corpus, it is a dead
                                                   instrument
  * the underlying `scripts.sweep` verdict is UNKNOWN (a selected file raised
    on read, or the walk failed)
  * the positive control did not fire           -- the instrument is not known
                                                   to work on this run
  * the must-not-match control DID fire         -- L-84: firing everywhere is
                                                   not the same as firing right
  * a marker block could not be terminated within the scan cap, leaving its
    ownership indeterminate (UNKNOWN only if nothing else already FAILs)

PASS requires: candidates > 0, both controls correct, sweep complete, and zero
unowned in the gated set.

--------------------------------------------------------------------------
3. WHAT THIS SWEEP CANNOT SEE -- printed in its own output, per L-84
--------------------------------------------------------------------------

L-84: "A positive control proves an instrument can fire. It does not prove its
reach, and it does not prove it fires only where it should." Both controls run
below. Neither closes these, and none of them is closable by a better regex:

  R1. **A supersession with no marker at all.** A silent edit or a deletion --
      the thing §8.1 forbids -- leaves nothing to match. This sweep measures
      ownership among records that already complied with §8.1. It is blind, by
      construction, to the non-compliant. This is the largest blind spot and it
      has L-84's exact shape: no true positive inside the frame can reveal it.
  R2. **Records outside the frame.** The frame is tracked markdown. Untracked
      records, and durable records that are not markdown (JSON ledgers, Python
      docstrings, the outside-version-control store of §3.1), are not swept.
      The four-frame table printed below states the size of that gap in files.
  R3. **§3a clause two** -- refutations against live claims. Nothing on disk
      marks a claim "live", so the set cannot be enumerated mechanically. A
      refutation that never produced a marker is invisible here.
  R4. **A named owner that is WRONG.** This checks that a role is named, not
      that it is the right role for that record's family. §2.3 of
      MEMORY_ARCHITECTURE maps four families to four directories, but three of
      the four roots overlap or are unstated, so path-to-family is not
      mechanical today.
  R5. **A quoted marker, quoted WITHOUT a code span.** A marker inside
      backticks is excluded as a citation, not an occurrence -- see
      `_in_code_span`, controlled by plant Q, and earned: the first live run of
      this sweep reported three "unowned" supersessions that were two
      `LADDER_V_V15_ROUND4.md` grading rows quoting `PRODUCT_LIST.md`'s marker
      and one copy of §8.2's own vocabulary list. All three were citations.
      A marker quoted in *plain prose* still reads as an occurrence here, and
      nothing distinguishes it. Docket D3 records the same confusion for a
      different guard.
  R6. **Ownership recorded away from the marker.** If a withdrawal's owner is
      assigned in some other file, this sweep calls the marker unowned. That is
      a false positive by design: §3a's cost is the time a claim spends
      readable, and a reader of the record cannot follow a pointer that is not
      written down.

USAGE

    python3 scripts/withdrawal_sweep.py                 # controls + live sweep
    python3 scripts/withdrawal_sweep.py --frame tracked
    python3 scripts/withdrawal_sweep.py --wider         # gate on all five

Exit status: 0 PASS, 1 FAIL, 3 UNKNOWN.
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
from typing import Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.sweep import FRAMES, sweep  # noqa: E402

# --------------------------------------------------------------------------
# The marker vocabulary. Not invented here -- MEMORY_ARCHITECTURE.md §8.2
# publishes these five and counts the corpus with them.
# --------------------------------------------------------------------------

GATED_MARKERS = ("WITHDRAWN", "RETRACTED", "SUPERSEDED")   # §3a's literal three
WIDER_MARKERS = GATED_MARKERS + ("AMENDED", "CORRECTED")   # §8.2's five

MARKER_RE = r"\[(?:%s)\b"

#: How far forward a marker block is followed looking for its closing bracket.
#: A block that does not close inside this is INDETERMINATE, not assumed owned.
BLOCK_LINE_CAP = 25
BLOCK_CHAR_CAP = 4000

# Durable ROLES. Drawn from SUPERVISION_CHARTER §4 (the chief), §2.3 of
# MEMORY_ARCHITECTURE (the four family supervisors), and DOCKET.md's stated
# owner vocabulary (fleet / chief / Katie).
ROLE_RE = re.compile(
    r"\b("
    r"chief(?:\s+supervisor)?"
    r"|family\s+supervisor"
    r"|supervisor(?:'s)?\s+ruling"
    r"|owner(?:'s)?\s+ruling"
    r"|Katie"
    r"|the\s+owner\b"
    r"|fleet"
    r")\b",
    re.IGNORECASE,
)

DIFFUSE_RE = re.compile(r"\bfleet\b", re.IGNORECASE)

# Names that point at something that ENDS. §3a: "authors here are sessions and
# sessions end ... a rule that names nobody is not enforcement".
SESSION_RE = re.compile(
    r"\b("
    r"its\s+own\s+author"
    r"|the\s+author"
    r"|by\s+its\s+author"
    r"|session"
    r"|subject\s+`"
    r"|grade\s+round"
    r"|round\s+\d+"
    r"|V1[0-9]\s+round"
    r"|auditing\s+agent"
    r"|an?\s+\w+\s+agent"
    r")\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Supersession:
    """One marker occurrence, with the block that decides its ownership."""

    path: str
    lineno: int
    marker: str
    block: str
    scope: str          # "block" or "table-row" -- what text was read for owner
    terminated: bool

    @property
    def classification(self) -> str:
        if not self.terminated:
            return "INDETERMINATE"
        if ROLE_RE.search(self.block):
            return "OWNED"
        if SESSION_RE.search(self.block):
            return "SESSION_ONLY"
        return "UNOWNED"

    @property
    def diffuse(self) -> bool:
        return self.classification == "OWNED" and bool(DIFFUSE_RE.search(self.block)) \
            and not re.search(r"\b(chief|family\s+supervisor|Katie)\b", self.block, re.I)

    def excerpt(self, width: int = 150) -> str:
        flat = " ".join(self.block.split())
        return flat[:width] + ("…" if len(flat) > width else "")


def _in_code_span(line: str, pos: int) -> bool:
    """True when `pos` sits inside a backtick code span on this line.

    A marker inside backticks is a CITATION of a marker, not one. This is not a
    convenience: the sweep's own first live run flagged three "unowned"
    supersessions that were two grading rows quoting another document's marker
    and one copy of MEMORY_ARCHITECTURE §8.2's vocabulary list. Excluding them
    narrows the instrument, so it carries its own control -- plant Q, which
    must not be counted at all. Widening or narrowing without a must-not-match
    set is an unmeasured trade (L-84).
    """
    inside = False
    i = 0
    while i < pos and i < len(line):
        if line[i] == "`":
            run = 0
            while i < len(line) and line[i] == "`":
                run += 1
                i += 1
            if i > pos:
                return inside
            inside = not inside
            continue
        i += 1
    return inside


def _block_at(lines: Sequence[str], idx: int, col: int) -> tuple[str, bool]:
    """Follow bracket depth forward from the marker's `[` to its match.

    Returns (text, terminated). Nested brackets are counted, because markdown
    links and code spans put `[` inside these blocks routinely. A block that
    does not close inside the caps comes back terminated=False, which drives
    INDETERMINATE rather than a guess.
    """
    depth = 0
    out: list[str] = []
    chars = 0
    for k in range(idx, min(idx + BLOCK_LINE_CAP, len(lines))):
        line = lines[k]
        start = col if k == idx else 0
        # strip blockquote / list decoration on continuation lines only
        seg = line[start:] if k == idx else re.sub(r"^[>\s*\-]*", "", line)
        for ch in seg:
            out.append(ch)
            chars += 1
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    return ("".join(out), True)
            if chars >= BLOCK_CHAR_CAP:
                return ("".join(out), False)
        out.append(" ")
    return ("".join(out), False)


def collect(root: str, frame: str, markers: Sequence[str],
            include: Sequence[str] = ("*.md",)
            ) -> tuple[list[Supersession], object, list[str]]:
    """Find every marker occurrence in `frame`, with its ownership block.

    Returns (occurrences, raw sweep result, citations excluded as code spans).
    """
    pattern = MARKER_RE % "|".join(markers)
    res = sweep(pattern, root=root, frame=frame, regex=True, include=list(include))

    rootp = Path(root).resolve()
    found: list[Supersession] = []
    cited: list[str] = []
    by_file: dict[str, list[str]] = {}
    for hit in res.hits:
        if hit.path not in by_file:
            by_file[hit.path] = (rootp / hit.path).read_text(
                encoding="utf-8", errors="replace").splitlines()
        lines = by_file[hit.path]
        raw = lines[hit.lineno - 1]
        for m in re.finditer(pattern, raw):
            if _in_code_span(raw, m.start()):
                cited.append(f"{hit.path}:{hit.lineno} "
                             f"{re.sub(r'[^A-Z]', '', m.group(0))}")
                continue
            block, terminated = _block_at(lines, hit.lineno - 1, m.start())
            scope = "block"
            # A docket-style table row carries its owner in the last cell, which
            # is outside the bracket. Read the whole row for those.
            if raw.lstrip().startswith("|") and raw.rstrip().endswith("|"):
                block = block + " || ROW-OWNER-CELL: " + raw.rsplit("|", 2)[-2]
                scope = "table-row"
            found.append(Supersession(
                path=hit.path, lineno=hit.lineno,
                marker=re.sub(r"[^A-Z]", "", m.group(0)),
                block=block, scope=scope, terminated=terminated))
    return found, res, cited


# --------------------------------------------------------------------------
# The two controls. Both plant into the LIVE repo frame, then remove -- a
# control run against a toy tree would prove the regex works and prove nothing
# about this repo's reach (L-84, failure one).
# --------------------------------------------------------------------------

CONTROL_BODY = """# Synthetic control plant -- withdrawal_sweep.py

## Plant P (POSITIVE, must be flagged UNOWNED)

**[WITHDRAWN 2026-08-13 -- the paragraph below is retained per the supersession
rule. It was wrong about the wake and the number came from the wrong column.]**

Some superseded prose.

## Plant N (MUST-NOT-MATCH, properly owned, must NOT be flagged)

**[WITHDRAWN 2026-08-13 by the chief supervisor, ruling `deadbeef`. Retained in
full and struck, per MEMORY_ARCHITECTURE.md 8.1.]**

Some other superseded prose.

## Plant S (boundary, session-attributed only -- must be flagged, not OWNED)

**[RETRACTED 2026-08-13 by its own author, subject `cafe1234`.]**

Third block.

## Plant Q (MUST-NOT-MATCH, a CITATION in a code span -- must not be counted)

That document now carries `**[SUPERSEDED 2026-08-13 - beef9999]**` in its header,
which is a quotation of somebody else's marker and not a supersession of this file.
"""


def _git(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *args],
                          capture_output=True, text=True, check=False)


@dataclass
class ControlReport:
    positive_fired: bool = False
    mustnot_stayed_silent: bool = False
    session_classified: bool = False
    citation_excluded: bool = False
    detail: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return (self.positive_fired and self.mustnot_stayed_silent
                and self.session_classified and self.citation_excluded)


def run_controls(root: str, frame: str) -> ControlReport:
    """Plant, sweep, assert, remove. Cleanup is in a finally block."""
    rootp = Path(root).resolve()
    rep = ControlReport()
    tmpdir = rootp / ".withdrawal_sweep_control"
    plant = tmpdir / "CONTROL_PLANT.md"
    tracked_frame = frame in ("tracked",)
    try:
        tmpdir.mkdir(exist_ok=True)
        plant.write_text(CONTROL_BODY, encoding="utf-8")
        if tracked_frame:
            # The tracked frame is `git ls-files`; an unstaged file is outside
            # it. --intent-to-add puts the plant in the index without staging
            # content. That this step is REQUIRED is itself the reach finding.
            _git(rootp, "add", "--intent-to-add", str(plant.relative_to(rootp)))

        found, _, cited = collect(str(rootp), frame, GATED_MARKERS)
        mine = [s for s in found if "CONTROL_PLANT.md" in s.path]
        mine_cited = [c for c in cited if "CONTROL_PLANT.md" in c]
        rep.detail.append(f"control plant produced {len(mine)} counted marker(s) and "
                          f"{len(mine_cited)} excluded citation(s) in frame "
                          f"'{frame}' (expected 3 and 1)")
        pos = [s for s in mine if "wrong about the wake" in s.block]
        neg = [s for s in mine if "chief supervisor" in s.block]
        ses = [s for s in mine if "cafe1234" in s.block]

        rep.positive_fired = bool(pos) and pos[0].classification == "UNOWNED"
        rep.mustnot_stayed_silent = bool(neg) and neg[0].classification == "OWNED"
        rep.session_classified = bool(ses) and ses[0].classification == "SESSION_ONLY"
        rep.citation_excluded = (len(mine_cited) == 1
                                 and not any("beef9999" in s.block for s in mine))
        for name, group, want in (("POSITIVE  P", pos, "UNOWNED"),
                                  ("MUST-NOT  N", neg, "OWNED"),
                                  ("BOUNDARY  S", ses, "SESSION_ONLY")):
            got = group[0].classification if group else "NOT FOUND"
            rep.detail.append(f"  {name}: want {want:<13} got {got:<13} "
                              f"{'ok' if got == want else 'CONTROL FAILED'}")
        rep.detail.append(
            f"  MUST-NOT  Q: want {'not counted':<13} got "
            f"{('excluded as citation' if rep.citation_excluded else 'COUNTED'):<13} "
            f"{'ok' if rep.citation_excluded else 'CONTROL FAILED'}")
    finally:
        if tracked_frame:
            _git(rootp, "rm", "--cached", "--force", "--quiet",
                 str(plant.relative_to(rootp)))
        if plant.exists():
            plant.unlink()
        if tmpdir.exists():
            try:
                tmpdir.rmdir()
            except OSError:
                pass
    return rep


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------

def frame_table(root: str) -> str:
    """All four frames sized on the same include filter, so the choice is legible."""
    from scripts.sweep import select_files
    rows = ["  frame              markdown files selected"]
    for name in ("everything", "worktree", "tracked", "ignore-honouring"):
        try:
            n = len(select_files(FRAMES[name], root, include=["*.md"]))
        except Exception as exc:                       # pragma: no cover
            rows.append(f"  {name:<18} UNKNOWN ({type(exc).__name__})")
            continue
        rows.append(f"  {name:<18} {n}")
    return "\n".join(rows)


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="withdrawal_sweep",
        description="SUPERVISION_CHARTER §3a weekly sweep: zero unowned supersessions.")
    p.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    p.add_argument("--frame", default="tracked", choices=sorted(FRAMES))
    p.add_argument("--wider", action="store_true",
                   help="gate on all five §8.2 markers, not §3a's literal three")
    p.add_argument("--no-controls", action="store_true",
                   help="skip the plant/remove controls (verdict is then UNKNOWN)")
    args = p.parse_args(argv)

    markers = WIDER_MARKERS if args.wider else GATED_MARKERS
    out: list[str] = []
    out.append("=" * 78)
    out.append("WEEKLY SWEEP -- zero unowned supersessions (SUPERVISION_CHARTER §3a)")
    out.append("=" * 78)
    out.append("")
    out.append("DEFINITIONS IN FORCE (see this module's docstring for their sources)")
    out.append("  supersession : a bracketed in-place marker from the vocabulary")
    out.append("                 MEMORY_ARCHITECTURE §8.2 publishes and counts with.")
    out.append(f"  gated on     : {', '.join(markers)}"
               + ("   (§8.2's five, --wider)" if args.wider
                  else "   (§3a's literal three)"))
    out.append("  unowned      : the marker's own block -- and, in a table row, that")
    out.append("                 row's owner cell -- names no durable ROLE.")
    out.append("                 A session/author/round is NOT a role: §3a exists")
    out.append("                 because sessions end.")
    out.append("")

    # -- controls first: a sweep whose instrument is unproven has no verdict --
    if args.no_controls:
        controls = ControlReport(detail=["controls SKIPPED by --no-controls"])
    else:
        controls = run_controls(args.root, args.frame)
    out.append("CONTROLS (L-84: firing is half a control; the other half is not firing)")
    out.extend("  " + d for d in controls.detail)
    out.append(f"  controls verdict : {'OK' if controls.ok else 'NOT OK'}")
    out.append("")

    found, res, cited = collect(args.root, args.frame, markers)

    out.append(res.frame_block())
    out.append("")
    out.append("FRAME CHOICE -- markdown files each frame would have selected")
    out.append(frame_table(args.root))
    out.append("  chosen: '%s'. Precedent: MEMORY_ARCHITECTURE §8.2 measured this"
               % args.frame)
    out.append("  corpus over tracked markdown (36 markers / 27 files, 2026-08-10).")
    out.append("")

    buckets: dict[str, list[Supersession]] = {}
    for s in found:
        buckets.setdefault(s.classification, []).append(s)
    unowned = buckets.get("UNOWNED", []) + buckets.get("SESSION_ONLY", [])
    indet = buckets.get("INDETERMINATE", [])
    diffuse = [s for s in found if s.diffuse]

    out.append("CANDIDATES")
    out.append(f"  supersession markers found : {len(found)}"
               f" in {len({s.path for s in found})} files")
    by_marker: dict[str, int] = {}
    for s in found:
        by_marker[s.marker] = by_marker.get(s.marker, 0) + 1
    out.append("  by marker word             : "
               + ", ".join(f"{k}={v}" for k, v in sorted(by_marker.items())))
    out.append(f"  OWNED (role named)         : {len(buckets.get('OWNED', []))}"
               f"   of which DIFFUSE ('fleet' only): {len(diffuse)}")
    out.append(f"  SESSION_ONLY (a ghost)     : {len(buckets.get('SESSION_ONLY', []))}")
    out.append(f"  UNOWNED (nobody named)     : {len(buckets.get('UNOWNED', []))}")
    out.append(f"  INDETERMINATE (block open) : {len(indet)}")
    out.append(f"  excluded as CITATIONS      : {len(cited)}"
               "  (marker inside a code span -- a quotation, not an occurrence)")
    for c in cited:
        out.append(f"      {c}")
    out.append("")

    if unowned:
        out.append("UNOWNED SUPERSESSIONS -- each needs an owner assigned on the spot")
        out.append("(§3a: 'the assignment is the deliverable, not a plan to assign')")
        for s in sorted(unowned, key=lambda x: (x.path, x.lineno)):
            out.append(f"  [{s.classification}] {s.path}:{s.lineno}  ({s.marker},"
                       f" scope={s.scope})")
            out.append(f"      {s.excerpt()}")
        out.append("")
    if indet:
        out.append("INDETERMINATE -- block did not close within the scan cap")
        for s in indet:
            out.append(f"  {s.path}:{s.lineno} ({s.marker})")
        out.append("")

    # -- verdict ----------------------------------------------------------
    reasons: list[str] = []
    if not controls.ok:
        reasons.append("the controls did not both come out right, so the "
                       "instrument is not known to work on this run")
    if res.verdict == "UNKNOWN":
        reasons.append("the underlying frame sweep returned UNKNOWN: "
                       + res.verdict_line())
    if not found:
        reasons.append("ZERO candidate supersessions were found. An empty set is "
                       "not a clean corpus; it is a dead instrument or a wrong "
                       "frame (docket B1, silent-zero sweeps). A sweep does not "
                       "get to PASS from nothing.")

    if reasons:
        verdict, rc = "UNKNOWN", 3
    elif unowned:
        verdict, rc = "FAIL", 1
        reasons.append(f"{len(unowned)} supersession(s) in the gated set name no "
                       f"durable owning role")
    elif indet:
        verdict, rc = "UNKNOWN", 3
        reasons.append(f"{len(indet)} marker block(s) could not be terminated, so "
                       f"their ownership was not read")
    else:
        verdict, rc = "PASS", 0
        reasons.append(f"{len(found)} supersessions examined, every one names a "
                       f"durable owning role")

    out.append("REACH -- what a PASS here would NOT mean (L-84)")
    for line in ("R1 a supersession with NO marker (a silent edit or deletion, the "
                 "thing §8.1 forbids) leaves nothing to match and is invisible here",
                 "R2 records outside the frame: untracked markdown, and durable "
                 "records that are not markdown, are not swept -- see the frame table",
                 "R3 §3a clause two (a refutation against a LIVE claim has a "
                 "withdrawal done or assigned) is not swept: nothing on disk marks "
                 "a claim live",
                 "R4 a named owner that is the WRONG role still counts as named",
                 "R5 a marker quoted inside a code span is excluded as a citation "
                 "(plant Q controls that); a marker quoted in PLAIN PROSE is still "
                 "counted as an occurrence and nothing here distinguishes it",
                 "R6 an owner assigned somewhere other than the record reads as "
                 "unowned here -- deliberately: a reader cannot follow an "
                 "unwritten pointer"):
        out.append("  " + line)
    out.append("")
    out.append("=" * 78)
    out.append(f"VERDICT: {verdict}")
    for r in reasons:
        out.append(f"  because {r}")
    out.append("=" * 78)
    print("\n".join(out))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
