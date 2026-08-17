#!/usr/bin/env python3
"""Does every docket citation in this repo resolve to a docket row that exists?

    python3 scripts/docket_citation_guard.py            # verdict + the citations
    python3 scripts/docket_citation_guard.py --json
    python3 scripts/docket_citation_guard.py --controls # controls only, no sweep

Exit contract, the one `scripts/lab_check.py` publishes:
0 PASS, 1 FAIL, 3 UNKNOWN. A traceback is UNKNOWN, not FAIL.

WHY THIS EXISTS -- the defect is a citation that RESOLVES, not one that dangles
=============================================================================
`docs/DOCKET.md` allocates IDs `D1, D2, ...` append-only. An agent that writes
"see docket D63" for a finding it has not filed yet has not made a dangling
pointer -- it has made a pointer that will silently come TRUE, aimed at whatever
row a different agent files at that number in the meantime. It happened: the
orphaned rule-B work cited `D63` while it sat uncommitted, and the fleet
allocated D63 to an unrelated S1 pre-registration finding. The citation still
resolves. Nothing about it looks wrong. `S1_ZEROCOMPUTE_TRIAGE_2026-08-14.md`
records the general case -- "D63-D66 were all taken by concurrent sessions while
this work was running".

The lab already holds the same class as a filed row: **D43**, where a
renumbering left `V16_GRADE_ROUND5.md` citing "docket D5" and "docket D6" at two
rows that had become D19 and D20, while D5 and D6 had meanwhile been filed as
two live, unrelated, unfixed defects. Both citations resolve. Both are wrong.

Under W-4 (Katie, 2026-08-11) IDs are append-only, never reused and NEVER
renumbered, so the ID space cannot be repaired after the fact -- D43's two
pointers are wrong permanently and the commits carrying them are immutable.
Allocation and citation discipline is therefore the only lever, and this file is
the executable half of it.

THE RULE THIS ENFORCES, and why it is not "cite only committed IDs"
===================================================================
Naive forward-citation rules fire on correct work. It is entirely legitimate to
write a row and cite it in the same unit of work, before either is committed --
that is what "allocate before you cite" LOOKS like, and a guard that reddened it
would train agents to cite last, which is the behaviour that caused the defect.

So the frame is the WORKING TREE, not HEAD:

    a citation is resolved if `docs/DOCKET.md` **on disk right now** has a row
    for that ID.

Allocated-and-uncommitted resolves. Allocated-by-someone-else resolves (that is
the whole point of append-only IDs). Only a citation to an ID that NO ONE has
written a row for anywhere is unresolved -- which is exactly the reserved-by-
citation move, caught at the moment it is made rather than after a stranger has
taken the number.

PRECISION, MEASURED, AND THE RECALL IT COSTS
============================================
A bare `\\bD\\d+\\b` is unusable in this corpus. Measured over tracked `*.py`,
the overwhelming majority of matches are format placeholders and locals from the
board-placement fixtures -- `{D4}`, `The rank-{D3}`, `D3=_D3, D1` -- not docket
citations at all. A guard built on it would FAIL on every run, and a guard that
always fails is a guard that gets ignored.

This one requires a docket CUE within a window on the same line: the substring
"docket" (any case, which also catches the path `docs/DOCKET.md`). That admits
the forms the corpus actually uses -- `docket D1`, `docketed as D37`,
`docket row named below as D8`, `D31 (docs/DOCKET.md)`, `D43 | **Two docket` --
and rejects every `{D4}` in the fixtures, because none of them names the docket.

STATED COVERAGE GAP, in the direction that costs recall rather than truth: a
citation with no cue anywhere near it -- a bare `(D12)` in running prose whose
paragraph never says "docket" -- is NOT seen by this guard. That is deliberate.
A false FAIL here is a checker crying wolf about a fixture placeholder; a false
PASS is one uncaught reserved-by-citation. The gap is recall, and it is named
rather than hidden, per B5.

THREE-VALUED, AND IT CANNOT PASS FROM AN EMPTY SET (defect class B1)
===================================================================
D62's class -- "a corpus replay that would return clean having never opened the
four records it exists to examine" -- is the highest-ranked defect here. Two
separate empty sets would produce a silent zero, and both are UNKNOWN:

  * no docket rows parsed (the docket moved, or its row format changed)
  * no citations matched (the cue regex rotted, or the frame is empty)

CONTROLS RUN ON EVERY INVOCATION, not in a test file somebody remembers
======================================================================
Four cells run before the live sweep, on in-memory fixtures, and a failure of
any of them is UNKNOWN -- an instrument that cannot detect its own planted
defect has no standing to report on the tree.

  POS   a planted citation to an unallocated ID   MUST flag
  NEG1  a citation to an allocated ID (L-84)      MUST NOT flag
  NEG2  a citation to an ID allocated in the
        worktree but not committed (L-84)         MUST NOT flag
  NEG3  the fixture placeholders `{D4}`/`D3=_D3`  MUST NOT even be seen

NEG2 is the one that matters. It is the control that stops this guard becoming
the too-strict rule described above, and it is the reason the frame is the
worktree.

THIS FILE NEVER WRITES. The controls are in-memory strings, not planted files,
so the guard is admitted by `lab_check.py` against the LIVE tree rather than
being deferred to snapshot mode as a writer. That was a design constraint, not
an accident: a guard about concurrent writers must not itself write into a tree
ten agents are working in.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DOCKET = "docs/DOCKET.md"

PASS, FAIL, UNKNOWN = "PASS", "FAIL", "UNKNOWN"
EXIT = {PASS: 0, FAIL: 1, UNKNOWN: 3}

#: A docket row. One markdown line, `| D<n> | ...`. `D8b` exists because a
#: collision was resolved by suffixing rather than renumbering, so the trailing
#: letter is part of the ID and not noise.
#:
#: The emphasis markers are load-bearing, not tidiness. `D1a`'s row is written
#: `| **D1a** |`, and an earlier cut of this pattern -- which required a bare
#: `| D1a |` -- did not see it. That is a FALSE-FAIL generator in the one
#: direction that matters: a row someone allocates in bold reads as unallocated,
#: so the guard would redden a citation to a row that exists. Control NEG4 pins
#: it. Found by an independent sweep of this corpus, not by me.
ROW = re.compile(r"^\|\s*[*_`]{0,3}\s*(D\d+[a-z]?)\s*[*_`]{0,3}\s*\|", re.M)

#: A candidate citation. Deliberately loose; the cue below does the deciding.
#:
#: The lookahead excludes a FILENAME. `docs/docket/D0083.md` is a path, not a
#: citation of D83, and it sits three words from the token "docket" so the cue
#: cannot tell them apart. This is not hypothetical: the sharding proposal
#: written in this same round uses exactly that form for its example shards, and
#: this guard returned FAIL on three of them the moment that document landed --
#: correct by its own letter, wrong about what a citation is. Control NEG5 pins
#: it, and the fix matters beyond the one document: if the shard migration ever
#: happens, every row becomes such a filename.
CITE = re.compile(r"\bD(\d+)\b(?!\.[A-Za-z]{1,4}\b)")

#: The cue that makes a candidate a docket citation. Also matches the path
#: `docs/DOCKET.md`, which is how several citations name their target.
#:
#: THE LEFT BOUNDARY IS LOAD-BEARING. The cue was a bare substring, so it
#: matched inside an IDENTIFIER: `TempDocketRepo`, the throwaway-repo fixture
#: class in `sdk/tests/test_docket_reconciliation.py`, supplied a "docket" cue
#: to the synthetic IDs on its own line and reddened them. The resulting
#: behaviour was arbitrary rather than merely strict -- in that one file some
#: fixture lines escaped and others did not, decided entirely by how far the
#: identifier happened to sit from each ID. A lookbehind for a letter fixes
#: it: prose forms (`docket D1`, `docketed as D37`) and the path form
#: (`docs/DOCKET.md`, whose `D` follows a slash) all still match, because none
#: of them has a LETTER immediately before the cue. Control NEG7 pins it.
#: Recall cost, measured rather than assumed: a citation whose only cue is
#: glued to the back of a word -- `subdocket D5` -- is no longer seen, and the
#: only occurrence of that shape in the corpus is this comment's own example.
#: Every candidate the boundary drops is a `TempDocketRepo(...)` fixture line,
#: which is the target.
CUE = re.compile(r"(?<![A-Za-z])docket", re.I)

#: How far from the cue a citation may sit, in characters, on the same line.
CUE_WINDOW = 60

#: AN ID SAID TO BE ABSENT IS MENTIONED, NOT CITED, and this is the guard's
#: own question turned on it: it asks "does every cited D<n> have a row?", so
#: a sentence whose whole content is that a number has NO row is the inverse of
#: the defect, not an instance of it. Measured case: `LADDER_V_V16_ROUND12.md`
#: reports the docket's ID census at a named frame as "one gap (D188)". That
#: number has never been a row -- a `git log --all -S` pickaxe for it over the
#: docket file is empty across every ref, and the ID sequence at HEAD has
#: exactly that one hole. (This paragraph states the number once, above,
#: inside the absence language that excludes it; naming it again beside a bare
#: cue would make this very comment an unresolved citation, which is how the
#: first cut of it reddened its own file.) The hole is deliberate: an ID block
#: was asserted and aborted under concurrency, and the settlement record for
#: that round states it "was deliberately NOT filled ... Nothing was reused or
#: renumbered".
#:
#: So neither available repair was legitimate before this: W-4 forbids
#: renumbering and the standing rule forbids creating a row to satisfy a
#: citation, while editing the sentence would delete a TRUE measurement to
#: appease a checker. The citing text is correct and the guard was wrong.
#: Control NEG6 pins it. Recall cost, stated: an author who writes "D<n> is
#: missing from the docket" while meaning to cite a row that ought to exist is
#: no longer flagged. That is the intended trade -- the guard exists to stop a
#: citation SILENTLY reserving a number, and a sentence asserting the number is
#: empty reserves nothing.
ABSENCE = re.compile(
    r"\b(?:gaps?|missing|absent|unallocated|no row|"
    r"never (?:allocated|filled|used)|not (?:filled|allocated|used))\b", re.I)

#: MUCH tighter than CUE_WINDOW, and the number was measured rather than
#: picked. At 40 characters this over-reached in exactly the way a suppression
#: rule must not: it dropped a genuine citation to the allocated row D35
#: because the phrase "the smallest gap in the data" sat 21 characters away --
#: a gap in the DATA, nothing to do with the ID sequence -- and it matched a
#: section name of the form "GAP-B" as though it were absence language.
#: Absence language binds TIGHTLY to the token it is about ("one gap (D188)"
#: puts 5 characters between them; "D188 is a gap" puts 9), so 12 keeps every
#: real form and drops both over-matches. Re-measured after the change: the
#: exclusion fires on the census sentence this rule exists for, and on the two
#: places in this file that quote it, and on nothing else in the corpus.
ABSENCE_WINDOW = 12

#: Text files only. A `.gz` solve log and a PDF both contain the byte sequence
#: "D63" and neither is a citation of anything.
TEXT_SUFFIXES = {".md", ".py", ".txt", ".yaml", ".yml", ".json", ".sh", ".cfg",
                 ".toml", ".rst", ".tex", ".csv"}


# ---------------------------------------------------------------------------
# The core. Pure functions over strings -- this is what the controls exercise
# and what the mutation harness mutates.
# ---------------------------------------------------------------------------

def allocated_ids(docket_text: str) -> set[str]:
    """Every ID that has a row. The frame is whatever text is handed in; the
    live caller hands in the WORKING TREE copy, which is what makes an
    allocated-but-uncommitted row resolve."""
    return set(ROW.findall(docket_text))


def citations_in(text: str) -> list[tuple[int, str, str]]:
    """(line number, ID, the line) for every cue-qualified docket citation.

    The cue must sit within CUE_WINDOW characters of the citation ON THE SAME
    LINE. Same-line is doing real work: docket rows are one line each, so a
    window that crossed lines would borrow the neighbouring row's cue and admit
    every `{D4}` that happened to sit under a docket paragraph.
    """
    found = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for m in CITE.finditer(line):
            lo = max(0, m.start() - CUE_WINDOW)
            hi = min(len(line), m.end() + CUE_WINDOW)
            if not CUE.search(line[lo:hi]):
                continue
            alo = max(0, m.start() - ABSENCE_WINDOW)
            ahi = min(len(line), m.end() + ABSENCE_WINDOW)
            if ABSENCE.search(line[alo:ahi]):
                continue  # mentioned as absent -> not a citation. See ABSENCE.
            found.append((lineno, "D" + m.group(1), line.strip()))
    return found


def unresolved(cites: list[tuple[int, str, str]], allocated: set[str]) -> list:
    """The verdict-bearing set: cited, and no row anywhere for it."""
    return [c for c in cites if c[1] not in allocated]


# ---------------------------------------------------------------------------
# Controls. In-memory, every invocation. A failure here is UNKNOWN.
# ---------------------------------------------------------------------------

_COMMITTED = "| D1 | a row |\n| D43 | another row |\n| **D44** | a row whose ID is bold |\n"
_WORKTREE = _COMMITTED + "| D80 | a row this agent just wrote, not yet committed |\n"


def run_controls() -> tuple[bool, list[str]]:
    lines, ok = [], True

    def cell(name: str, got: bool, want: bool, note: str) -> None:
        nonlocal ok
        good = got is want
        ok = ok and good
        lines.append(f"  [{'ok' if good else 'BROKEN'}] {name:<5} "
                     f"fired={str(got):<5} expected={str(want):<5} {note}")

    alloc_c = allocated_ids(_COMMITTED)
    alloc_w = allocated_ids(_WORKTREE)

    # POSITIVE CONTROL -- the defect this guard exists for, planted.
    #
    # ASSEMBLED FROM SPLIT TOKENS, and that is not decoration. This file is
    # tracked, so the live sweep reads it too: written as one literal, the
    # control string IS an unresolved citation in the tree, and the guard
    # flagged itself and returned FAIL on its first run after the row-parser
    # fix. That is D3's shape exactly -- a record becoming an instance of the
    # thing it describes -- and D3's own remedy is the one used here, the same
    # convention `sdk/tests/test_rank_claim_surfaces.py` already uses: state the
    # shape, do not reproduce the string.
    pos = "see docket D" + "999" + " for the finding this work will file"
    cell("POS", bool(unresolved(citations_in(pos), alloc_w)), True,
         "citation to an ID no row exists for -> must flag")

    # MUST-NOT-MATCH 1 (L-84) -- an ordinary, correct citation.
    neg1 = "this is the class docket D43 already records"
    cell("NEG1", bool(unresolved(citations_in(neg1), alloc_w)), False,
         "citation to an allocated ID -> must not flag")

    # MUST-NOT-MATCH 2 (L-84) -- the control that keeps the rule from being
    # too strict. D80 has a row on disk and no commit. Correct work.
    neg2 = "filed as docket D80 in this same unit of work"
    cell("NEG2", bool(unresolved(citations_in(neg2), alloc_w)), False,
         "allocated in worktree, uncommitted -> must not flag")
    # ...and the same string against the COMMITTED-only frame is what the
    # too-strict rule would have done. Recorded so the difference is visible.
    strict = bool(unresolved(citations_in(neg2), alloc_c))
    lines.append(f"  [info] NEG2  the HEAD-only frame would have flagged it: "
                 f"{strict} -- which is why the frame is the worktree")

    # MUST-NOT-MATCH 3 -- the corpus's real false-positive shape.
    neg3 = "return t.format(RK=_RK, D1=_D[1], D2=_D[2]) # The rank-{D3} token"
    cell("NEG3", bool(citations_in(neg3)), False,
         "fixture placeholders with no cue -> must not even be seen")

    # MUST-NOT-MATCH 4 -- a row whose ID is written in bold, as D1a's is.
    # This is the false-FAIL direction: miss the row and the guard reddens a
    # citation to something that exists.
    neg4 = "this is the class docket D44 already records"
    cell("NEG4", bool(unresolved(citations_in(neg4), alloc_w)), False,
         "citation to a bold-written row (| **D44** |) -> must not flag")

    # MUST-NOT-MATCH 5 -- a shard FILENAME is a path, not a citation.
    neg5 = "the docket shard `docs/docket/D0083.md` holds that row"
    cell("NEG5", bool(citations_in(neg5)), False,
         "a D<n>.md filename near the cue -> must not be read as a citation")

    # MUST-NOT-MATCH 6 -- an ID MENTIONED AS ABSENT. The census sentence that
    # forced this: a record stating the docket's ID range at a named frame and
    # naming the one hole in it. Split tokens, for the reason POS gives.
    gap_id = "D" + "188"
    neg6 = (f"docket IDs at that frame: 244 distinct, min D1, one gap "
            f"({gap_id}) over docs/DOCKET.md")
    cell("NEG6", bool(citations_in(neg6)), False,
         "an ID named as a GAP -> mentioned, not cited; must not be seen")

    # ...and its POSITIVE twin. The same unallocated ID, the same cue, with the
    # absence language removed. If this stopped firing, NEG6 would be a
    # blinding of the class rather than a narrowing of it.
    pos6 = f"docket {gap_id} settles this, over docs/DOCKET.md"
    cell("POS6", bool(unresolved(citations_in(pos6), alloc_w)), True,
         "same ID, same cue, no absence language -> must still flag")

    # MUST-NOT-MATCH 7 -- the cue glued to the back of an IDENTIFIER. The
    # fixture class name that forced this builds a throwaway repo in a temp
    # directory; its IDs are chosen out of range precisely so they cannot
    # collide with real ones, and it makes no claim about the real docket.
    fixture_id = "D" + "901"
    neg7 = f'    repo = TempDocketRepo(rows("D1", "{fixture_id}"))'
    cell("NEG7", bool(citations_in(neg7)), False,
         "cue inside an identifier (TempDocketRepo) -> must not be seen")

    # ...and its POSITIVE twin, so the left boundary is shown to have cost the
    # cue nothing it should keep: the same out-of-range ID beside a real cue.
    pos7 = f"filed under docket {fixture_id} as the governing ruling"
    cell("POS7", bool(unresolved(citations_in(pos7), alloc_w)), True,
         "same ID beside a word-boundary cue -> must still flag")

    return ok, lines


# ---------------------------------------------------------------------------
# The live sweep
# ---------------------------------------------------------------------------

def tracked_text_files() -> list[str]:
    """`git ls-files`, never the shell's `grep`/`find`. This shell aliases grep
    to `ugrep --ignore-files`, which honours `.gitignore` and therefore cannot
    see about 23% of this tree; that discrepancy has produced false findings
    here before."""
    out = subprocess.run(["git", "-C", str(REPO), "ls-files"],
                         capture_output=True, text=True, check=True).stdout
    return [p for p in out.splitlines() if Path(p).suffix.lower() in TEXT_SUFFIXES]


def sweep() -> dict:
    docket = REPO / DOCKET
    if not docket.is_file():
        return dict(verdict=UNKNOWN, reason=f"{DOCKET} is not on disk",
                    allocated=0, cites=0, unresolved=[], files=0)

    allocated = allocated_ids(docket.read_text(encoding="utf-8", errors="replace"))
    if not allocated:
        return dict(verdict=UNKNOWN,
                    reason=f"parsed 0 docket rows out of {DOCKET} -- the row "
                           "format changed, or the file moved. Reporting "
                           "UNKNOWN rather than passing an empty set (B1).",
                    allocated=0, cites=0, unresolved=[], files=0)

    paths = tracked_text_files()
    all_cites, bad = [], []
    for rel in paths:
        p = REPO / rel
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            continue
        cites = citations_in(text)
        all_cites += [(rel,) + c for c in cites]
        bad += [(rel,) + c for c in unresolved(cites, allocated)]

    if not all_cites:
        return dict(verdict=UNKNOWN,
                    reason="0 docket citations matched over "
                           f"{len(paths)} tracked text files -- the cue regex "
                           "rotted or the frame is empty. An examination that "
                           "examined nothing is not a pass (B1, D62).",
                    allocated=len(allocated), cites=0, unresolved=[],
                    files=len(paths))

    return dict(
        verdict=FAIL if bad else PASS,
        reason=(f"{len(bad)} citation(s) resolve to no docket row"
                if bad else
                f"every one of {len(all_cites)} docket citations resolves to a "
                f"row in the working tree's {DOCKET}"),
        allocated=len(allocated), cites=len(all_cites),
        unresolved=[dict(path=b[0], line=b[1], id=b[2], text=b[3][:200]) for b in bad],
        files=len(paths))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="machine-readable")
    ap.add_argument("--controls", action="store_true",
                    help="run the controls and stop, no live sweep")
    args = ap.parse_args()

    ctl_ok, ctl_lines = run_controls()

    if args.controls:
        if not args.json:
            print("CONTROLS")
            print("\n".join(ctl_lines))
            print(f"VERDICT: {PASS if ctl_ok else UNKNOWN}")
        else:
            print(json.dumps(dict(controls_ok=ctl_ok, lines=ctl_lines), indent=2))
        return EXIT[PASS] if ctl_ok else EXIT[UNKNOWN]

    if not ctl_ok:
        res = dict(verdict=UNKNOWN,
                   reason="the guard's own controls did not behave. An "
                          "instrument that cannot detect its planted defect has "
                          "no standing to report on the tree.",
                   allocated=0, cites=0, unresolved=[], files=0)
    else:
        res = sweep()

    if args.json:
        print(json.dumps(dict(res, controls_ok=ctl_ok, lines=ctl_lines), indent=2))
        return EXIT[res["verdict"]]

    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    print("=" * 74)
    print("DOCKET CITATION GUARD -- does every cited D<n> have a row?")
    print("=" * 74)
    print("\nFRAME")
    print(f"  repo            {REPO}")
    print(f"  HEAD            {head}")
    print(f"  docket          {DOCKET}, read from the WORKING TREE")
    print(f"  enumeration     git ls-files, text suffixes only "
          f"(never the shell's grep/find)")
    print(f"  files swept     {res['files']}")
    print(f"  rows allocated  {res['allocated']}")
    print(f"  citations       {res['cites']}  (cue-qualified; bare D<n> with no "
          f"nearby 'docket' is a stated recall gap)")
    print("\nCONTROLS")
    print("\n".join(ctl_lines))

    if res["unresolved"]:
        print("\nUNRESOLVED CITATIONS -- cited, and no row anywhere for the ID")
        for u in res["unresolved"]:
            print(f"  {u['path']}:{u['line']}  {u['id']}")
            print(f"      {u['text']}")

    print(f"\n{res['reason']}")
    print(f"\nVERDICT: {res['verdict']}")
    return EXIT[res["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
