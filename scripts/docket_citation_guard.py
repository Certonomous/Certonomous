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
CITE = re.compile(r"\bD(\d+)\b")

#: The cue that makes a candidate a docket citation. Also matches the path
#: `docs/DOCKET.md`, which is how several citations name their target.
CUE = re.compile(r"docket", re.I)

#: How far from the cue a citation may sit, in characters, on the same line.
CUE_WINDOW = 60

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
            if CUE.search(line[lo:hi]):
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
