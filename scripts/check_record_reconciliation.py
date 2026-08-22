#!/usr/bin/env python3
r"""Did an entry land in a commit and never reach the worktree, or the reverse --
for `docs/LESSONS.md` and `docs/NUMERICS_KNOWLEDGE.md`.

WHY THIS EXISTS (docket D369; docs/USING_THIS_LAB.md section 8.5)
================================================================
`scripts/check_docket_reconciliation.py` guards `docs/DOCKET.md` against the
write-back gap the private-index protocol opens. D369 records that the same
guard is **owed** to `docs/LESSONS.md` and does not exist -- and it says so in
the row that documents `LESSONS.md` losing bytes:

    "the merge form is owed to section 8.5 and to
     `scripts/check_docket_reconciliation.py`'s sibling for `LESSONS.md`,
     which does not exist."

This is that sibling. `docs/NUMERICS_KNOWLEDGE.md` is carried in the same module
because the shape is identical -- an append-only record, many authors, ids that
are the whole heading token -- and a second copy of this file would be a second
place for the pattern to rot.

DOES THE SAME SHAPE REALLY WORK ON BOTH? YES, WITH THREE DIFFERENCES, NAMED
==========================================================================
  1. TWO ENTRY FORMS IN NUMERICS. Entries are written either bold (`**N-B26.`)
     or as an h2 (`## N-X1.`), and both are live: 50 bold against 20 headings at
     the time of writing. A pattern that accepted only one would drop half the
     file from BOTH sides, the symmetric difference would cancel, and the run
     would report a false PASS. That is why the control below is a RECOGNITION
     control and plants both forms.
  2. IDS ARE SERIES-SCOPED IN NUMERICS. `N-B`, `N-D`, `N-K`, `N-X`, `N-T` are
     independent lanes, so `N-B26` follows `N-B25` no matter what `N-T` is up
     to. Reconciliation compares SETS and does not care, but the ordering used
     for display does, and `append_record.py`'s max+1 assertion very much does.
  3. LESSONS HAS TWO SHAPES THIS DELIBERATELY DOES NOT MATCH -- see CANNOT SEE.

SETS, NEVER TOTALS -- the same rule, for the same reason
========================================================
The docket module records that on 2026-08-16 three different row totals for one
commit were all defensible because they came from three different patterns. This
module prints the pattern it used on every run and reports the symmetric
difference BY NAME. Counts appear once, labelled diagnostic.

WHAT THIS CHECK CANNOT SEE
==========================
  * `## L-43, second corollary.` and `### L-63 - CORRECTION, ...`. Both are real
    lines in `docs/LESSONS.md`. The pattern is anchored to `^## L-<n>.` -- h2,
    digits, literal period -- so neither is matched. Matching the first would
    make `L-43` a DUPLICATE id and fail every clean run; matching the second
    would file an amendment as a lesson. They are declared here rather than made
    to fit, and an entry added under either shape is invisible to this check.
  * WHETHER AN ENTRY'S CONTENT DIVERGED. Same id, different body reads as
    reconciled.
  * CONTENT THAT MATCHES NO ID PATTERN AT ALL -- an in-progress paragraph, a
    partial line, a trailing edit. **This is D369's actual loss**, and no
    ID-set reconciliation can see it in either direction. That gap is closed by
    `scripts/append_record.py`, which merges rather than overwrites; this module
    is its complement, not its replacement. Neither alone is sufficient.
  * WHETHER UNLANDED WORK IS ABANDONED OR IN FLIGHT. It reports the fact, never
    the intent, and must not be read as licence to land somebody else's entry.
  * THE INDEX. It compares a COMMIT against the WORKING TREE and never uses
    `git diff` without an explicit revision -- the shared `.git/index` is
    poisoned by any peer's `git add`, and was measured strictly stale here on
    2026-08-22 (225 lessons against 237, 44 numerics entries against 70).

EXIT CONTRACT -- identical to the docket module, deliberately
=============================================================
    0  PASS      the id sets are equal
    1  FAIL      entries in HEAD are missing from the worktree; write-back owed
    2  FAIL      entries in the worktree are in no commit -- UNLANDED WORK
    3  UNKNOWN   a side could not be read, or parsed to zero ids
    4  FAIL      a duplicate id on either side
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import control_kind  # noqa: E402
from append_record import RECORDS, parse_ids, split_id  # noqa: E402

EXIT_PASS = 0
EXIT_FAIL_WRITEBACK_OWED = 1
EXIT_FAIL_UNLANDED = 2
EXIT_UNKNOWN = 3
EXIT_FAIL_DUPLICATE = 4

DEFAULT_PATHS = ["docs/LESSONS.md", "docs/NUMERICS_KNOWLEDGE.md"]
DEFAULT_REV = "HEAD"


def sort_key(entry_id: str) -> tuple[str, int, str]:
    """Series prefix, then the number NUMERICALLY, then suffix.

    Lexical sort puts `L-99` after `L-146` and `N-B9` after `N-B26`; the docket
    module records that defect allocating an id taken weeks earlier.
    """
    return split_id(entry_id)


def read_committed(repo: Path, rev: str, path: str) -> tuple[str | None, str]:
    completed = subprocess.run(
        ["git", "-C", str(repo), "show", f"{rev}:{path}"],
        capture_output=True, text=True,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip().splitlines()
        reason = detail[-1] if detail else f"git exited {completed.returncode}"
        return None, f"could not read {rev}:{path} -- {reason}"
    return completed.stdout, ""


def run_controls(path: str) -> control_kind.ControlLedger:
    """Plant the record's OWN entry vocabulary and prove the pattern finds it.

    RECOGNITION, not reachability, and for the docket module's reason: a PASS
    here is a ZERO -- an empty symmetric difference. A pattern blind to one
    entry FORM drops that entry from both sides, the difference cancels, and the
    check reports PASS on a file it cannot read. Proving it can open both files
    would not touch that. The negative forms are shapes that must NOT be read as
    entries: a mid-sentence mention, and (for lessons) the two real lines this
    module declares it cannot see.
    """
    pattern = RECORDS[path]
    if path == "docs/LESSONS.md":
        forms = {
            "## L-9001. a lesson heading": "L-9001",
            "## L-9002. another, three digits over": "L-9002",
        }
        negatives = [
            "a mid-sentence mention of L-9003 in prose",
            "## L-43, second corollary. a second block under an existing id",
            "### L-63 - CORRECTION, an h3 amendment",
        ]
    else:
        forms = {
            "**N-B9001. a bold entry**": "N-B9001",
            "## N-X9002. an h2 entry": "N-X9002",
            "**N-T9003. a third series, bold**": "N-T9003",
        }
        negatives = [
            "a mid-sentence mention of N-B9004 in prose",
            "  **N-B9005. an indented entry, not at column 0**",
        ]
    planted = {f: (want in parse_ids(f, pattern)) for f, want in forms.items()}
    ledger = control_kind.ControlLedger(claim_class=f"an id in {path}")
    ledger.plant(f"{Path(path).stem} entry forms",
                 vocabulary=f"{path} entries",
                 planted=planted,
                 negative={n: bool(parse_ids(n, pattern)) for n in negatives})
    return ledger


def reconcile(committed_text: str, worktree_text: str, path: str,
              ledger: "control_kind.ControlLedger | None" = None) -> dict:
    """Pure, so the controls and any test can drive it on fixtures."""
    pattern = RECORDS[path]
    committed_ids = parse_ids(committed_text, pattern)
    worktree_ids = parse_ids(worktree_text, pattern)
    committed_set, worktree_set = set(committed_ids), set(worktree_ids)

    head_only = sorted(committed_set - worktree_set, key=sort_key)
    worktree_only = sorted(worktree_set - committed_set, key=sort_key)
    committed_dupes = sorted({i for i in committed_ids
                              if committed_ids.count(i) > 1}, key=sort_key)
    worktree_dupes = sorted({i for i in worktree_ids
                             if worktree_ids.count(i) > 1}, key=sort_key)

    ledger = run_controls(path) if ledger is None else ledger
    hits = len(head_only) + len(worktree_only)
    zero_verdict, zero_why = ledger.verdict_for(hits)

    if not committed_ids or not worktree_ids:
        verdict, code = "UNKNOWN", EXIT_UNKNOWN
    elif committed_dupes or worktree_dupes:
        verdict, code = "FAIL", EXIT_FAIL_DUPLICATE
    elif worktree_only:
        verdict, code = "FAIL", EXIT_FAIL_UNLANDED
    elif head_only:
        verdict, code = "FAIL", EXIT_FAIL_WRITEBACK_OWED
    else:
        verdict, code = "PASS", EXIT_PASS

    return {
        "path": path, "pattern": pattern, "verdict": verdict, "exit": code,
        "n_committed": len(committed_ids), "n_worktree": len(worktree_ids),
        "head_only": head_only, "worktree_only": worktree_only,
        "committed_duplicates": committed_dupes,
        "worktree_duplicates": worktree_dupes,
        "zero_verdict": zero_verdict, "zero_because": zero_why,
        "ledger": ledger, "hits": hits,
    }


def render(result: dict, rev: str, worktree_file: Path) -> None:
    print("=" * 78)
    print(f"RECORD RECONCILIATION -- {result['path']}")
    print("=" * 78)
    print(f"  committed side   : {rev}:{result['path']}")
    print(f"  worktree side    : {worktree_file}")
    print(f"  id pattern       : {result['pattern']}")
    print(f"  entries parsed   : {result['n_committed']} committed, "
          f"{result['n_worktree']} in the working copy (counts are diagnostic "
          f"only -- the verdict is over ID SETS)")
    print("-" * 78)
    if result["head_only"]:
        print("IN HEAD, NOT IN THE WORKTREE -- landed and never written back. "
              "The entry is safe; HEAD WINS. Restore it in numeric order; do "
              "not commit it again:")
        print("    " + " ".join(result["head_only"]))
    if result["worktree_only"]:
        print("IN THE WORKTREE, NOT IN HEAD -- UNLANDED WORK. It lives in no "
              "commit and is destroyed by checkout/stash/reset, all forbidden "
              "here. Land it BY ID through the private-index form:")
        print("    " + " ".join(result["worktree_only"]))
    if result["committed_duplicates"] or result["worktree_duplicates"]:
        print("DUPLICATE IDS -- two findings wearing one name; every later "
              "citation is ambiguous and the record is append-only:")
        if result["committed_duplicates"]:
            print("    committed: " + " ".join(result["committed_duplicates"]))
        if result["worktree_duplicates"]:
            print("    worktree : " + " ".join(result["worktree_duplicates"]))
    if not (result["head_only"] or result["worktree_only"]
            or result["committed_duplicates"] or result["worktree_duplicates"]):
        print("Both sides carry the same set of entry ids, with no duplicates.")
    print("-" * 78)
    print(result["ledger"].render(result["hits"]))
    print("-" * 78)
    print(f"VERDICT: {result['verdict']}")
    print("CANNOT SEE: content divergence under a shared id; entries written as "
          "`## L-43, second corollary.` or `### L-63 - CORRECTION` (declared, "
          "not matched); CONTENT THAT MATCHES NO ID PATTERN AT ALL, which is "
          "D369's actual loss and is closed by scripts/append_record.py, not by "
          "this module; whether unlanded work is abandoned or in flight; and "
          "the index, which this check deliberately never consults.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--path", action="append", dest="paths",
                    help="record to check; repeatable (default: lessons and "
                         "numerics)")
    ap.add_argument("--rev", default=DEFAULT_REV)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    repo = Path(args.repo).resolve()
    paths = args.paths or DEFAULT_PATHS
    worst, blobs = EXIT_PASS, []
    for path in paths:
        if path not in RECORDS:
            print(f"UNKNOWN: {path} is not a registered append-only record. "
                  f"Known: {', '.join(sorted(RECORDS))}", file=sys.stderr)
            return EXIT_UNKNOWN
        head_text, why = read_committed(repo, args.rev, path)
        wt_file = repo / path
        if head_text is None or not wt_file.is_file():
            print(f"UNKNOWN: {why or f'no such file: {wt_file}'}",
                  file=sys.stderr)
            return EXIT_UNKNOWN
        result = reconcile(head_text, wt_file.read_text(), path)
        blobs.append({k: v for k, v in result.items() if k != "ledger"})
        if not args.json:
            render(result, args.rev, wt_file)
            print()
        # The worse of the codes decides, and UNLANDED outranks write-back-owed.
        order = {EXIT_PASS: 0, EXIT_FAIL_WRITEBACK_OWED: 1,
                 EXIT_FAIL_DUPLICATE: 2, EXIT_FAIL_UNLANDED: 3,
                 EXIT_UNKNOWN: 4}
        if order[result["exit"]] > order[worst]:
            worst = result["exit"]
    if args.json:
        print(json.dumps(blobs, indent=1))
    return worst


if __name__ == "__main__":
    sys.exit(main())
