#!/usr/bin/env python3
r"""Append rows to an append-only record by MERGE, never by overwrite.

WHY THIS EXISTS (docket D369, D461/D-13; docs/USING_THIS_LAB.md section 8.5)
===========================================================================
The private-index protocol rebuilds an append-only file as **HEAD's blob plus
the author's own rows** and then, "as part of the protocol, not an
afterthought", writes that result into the working tree. That last step is a
plain OVERWRITE, and it destroys anything the worktree held beyond HEAD's blob.

It has now bitten twice.

  * `D369`: applied at `12b7ed42` to a `docs/LESSONS.md` whose worktree copy was
    LONGER than HEAD's blob. `cmp` reported "EOF on - after byte 313171"; the
    trailing bytes were destroyed and are not recoverable. D369 closes with the
    repair -- "**The write-back must be a MERGE, not an overwrite**: rebuild
    HEAD's blob plus your rows, then re-apply whatever the worktree held beyond
    HEAD's blob, and refuse if the two disagree anywhere inside HEAD's own
    bytes" -- and records it as **OPEN**, owed to section 8.5.
  * `D461` / `RESULTS.md` departure D-13: the R4 lane was instructed to use the
    overwrite form and did. Nothing was lost, as far as every ID-level check can
    see -- and that qualifier is the whole problem, because D369's loss was
    bytes that matched no ID regex.

Sanaa's standing rule (H-7, the L-221 rule) is that a defect class which has
bitten twice gets an ASSERT AT EVERY CALL SITE, never a paragraph in a report.
This module is that assert. The paragraph has been written twice already.

WHAT "DISAGREE INSIDE HEAD'S OWN BYTES" MEANS, AND WHY IT IS A REFUSAL
=====================================================================
An append-only record's worktree copy should be HEAD's blob with zero or more
bytes appended. So the test is a PREFIX test:

    worktree[:len(head)] == head        -> tail = worktree[len(head):]
    anything else                       -> REFUSE, write nothing

The second case means somebody edited or truncated content that is already
committed. That is not an append, and this module has no way to know whose edit
it is or whether it is deliberate, so it stops rather than guessing. Refusing is
cheap; the alternative is the D369 outcome.

ORDER OF THE MERGE
==================
    HEAD's blob  +  the worktree's own tail  +  your rows

The tail goes BEFORE the rows because the tail is somebody else's work that was
already sitting there, and an append-only record is chronological. If the tail
does not end in a newline it is a partial line -- somebody is mid-edit -- so a
separator is inserted and the fact is REPORTED, never silently fixed.

THE ID ASSERTION
================
The first ID in the rows being appended must equal max + 1 for its own series,
read from THE SAME HEAD BLOB the merge is built on. Not from the worktree, which
may carry a peer's unlanded row, and not from a number remembered from earlier
in the session, which is the L-43/L-52 trap (CLAUDE.md rule 11: the maximum
existing number, never a count). Series-aware, because `docs/NUMERICS_KNOWLEDGE.md`
numbers per lane -- N-B, N-D, N-K, N-X, N-T -- and `N-B26` follows `N-B25`
regardless of what N-T is up to.

WHAT THIS MODULE CANNOT SEE
===========================
  * WHETHER THE TAIL IT PRESERVED IS WANTED. A worktree-only paragraph may be a
    peer's live work or an abandoned scrap. This module preserves it and reports
    it; it never judges it, and a preserved tail is not permission to commit
    somebody else's bytes.
  * A REORDERING INSIDE HEAD'S BYTES that happens to preserve length and
    content -- there is none, the prefix test is exact -- but equally, an edit
    that HEAD already carries because a peer landed it between your `git show`
    and your write. Capture HEAD ONCE and pass the same revision here that you
    pass to `commit-tree -p`.
  * ANYTHING ABOUT THE COMMIT. This module touches the working tree only. The
    private-index sequence, the compare-and-swap and the post-commit
    verification are still the caller's.

EXIT CONTRACT
=============
    0  OK        merged and written (or --dry-run and it would have been)
    2  REFUSED   the worktree disagrees with HEAD inside HEAD's own bytes
    3  REFUSED   the first appended id is not max + 1 for its series
    4  UNKNOWN   a side could not be read, or the pattern parsed zero ids
    5  SELFTEST  a planted control did not behave as required

No status is ever taken through a pipe: every subprocess is run with a list
argument and its `returncode` read from the completed process.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import control_kind  # noqa: E402

EXIT_OK = 0
EXIT_REFUSED_DISAGREES = 2
EXIT_REFUSED_ID = 3
EXIT_UNKNOWN = 4
EXIT_SELFTEST = 5

#: One entry per append-only record this lab keeps. The pattern must match the
#: record's OWN id vocabulary; the traps each one is anchored around are in the
#: comments, because a pattern without its trap is copied wrongly.
RECORDS = {
    # The whole first cell, modulo bold/strike -- `check_docket_reconciliation`'s
    # pattern, unchanged, including its `D19-D20 note` exclusion.
    "docs/DOCKET.md": r"^\|\s*(?:\*\*|~~)*\s*([A-G]\d+[a-z]?)\s*(?:~~|\*\*)*\s*\|",
    # `## L-<n>.` at h2 with a literal period. This deliberately does NOT match
    # `## L-43, second corollary.` (a second block under an existing id, which
    # would read as a duplicate) or `### L-63 - CORRECTION` (an h3 amendment).
    # Both exist in the file; both are declared in CANNOT SEE rather than made
    # to fit.
    "docs/LESSONS.md": r"^## (L-\d+)\.",
    # Entries are written either bold or as an h2, and both forms are live:
    # 50 bold and 20 headings at the time of writing.
    "docs/NUMERICS_KNOWLEDGE.md": r"^(?:\*\*|## )(N-[A-Z]+\d+)\.",
}


def split_id(row_id: str) -> tuple[str, int, str]:
    """('N-B26') -> ('N-B', 26, ''). Series prefix, number, optional suffix."""
    m = re.match(r"^(.*?)(\d+)([a-z]?)$", row_id)
    if m is None:  # pragma: no cover - the patterns cannot produce this
        return (row_id, 0, "")
    return (m.group(1), int(m.group(2)), m.group(3))


def parse_ids(text: str, pattern: str) -> list[str]:
    """Every id in *text*, in order. Duplicates preserved for the caller."""
    return re.compile(pattern, re.M).findall(text)


def max_for_series(ids: list[str], series: str) -> int | None:
    """The MAXIMUM EXISTING NUMBER in *series*, never a count (CLAUDE.md 11)."""
    nums = [n for (p, n, _) in map(split_id, ids) if p == series]
    return max(nums) if nums else None


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


def merge(head_text: str, worktree_text: str, rows_text: str) -> dict:
    """The merge itself. Pure, so the controls can drive it on fixtures.

    Returns a dict; `ok` False means REFUSE and `merged` is None.
    """
    if not worktree_text.startswith(head_text):
        # Locate the first differing byte so the refusal is actionable.
        limit = min(len(head_text), len(worktree_text))
        at = next((i for i in range(limit)
                   if head_text[i] != worktree_text[i]), limit)
        return {
            "ok": False,
            "reason": (
                "the worktree disagrees with the committed blob inside the "
                f"committed blob's own bytes, first at byte {at} of "
                f"{len(head_text)}"
                + ("; the worktree is SHORTER than the blob, which is a "
                   "truncation, not an append"
                   if len(worktree_text) < len(head_text) else "")),
            "merged": None, "tail": None, "separator_inserted": False,
        }
    tail = worktree_text[len(head_text):]
    separator = bool(tail) and not tail.endswith("\n")
    merged = head_text + tail + ("\n" if separator else "") + rows_text
    return {"ok": True, "reason": "", "merged": merged, "tail": tail,
            "separator_inserted": separator}


# --------------------------------------------------------------- controls
def run_controls() -> tuple[control_kind.ControlLedger, int, list[str]]:
    """Plant D369's OWN invisible case and prove BOTH forms on it.

    WHY THIS NEEDS A RECOGNITION CONTROL, NOT A REACHABILITY ONE. This module's
    success is a zero: zero worktree bytes lost. Proving it can read the two
    files would not touch that. What has to be shown is that the merge PRESERVES
    content the id pattern cannot see -- because that is exactly what D369 lost,
    and exactly what every ID-set reconciliation is blind to. So each planted
    form below is worktree-only content that matches NO id pattern, and the
    NEGATIVE form is the overwrite itself: if the overwrite did not drop them,
    this module would have no reason to exist.
    """
    head = "# R\n\n| D1 | one |\n| D2 | two |\n"
    rows = "| D3 | three |\n"
    forms = {
        "an id-less paragraph": "\nAn in-progress paragraph naming no row id.\n",
        # A row whose first cell is not yet CLOSED. `| D9 | half-written`
        # would not do: the docket pattern matches it, so it is not invisible
        # and the control below rejected it -- which is the control working.
        "a partial row, first cell unclosed": "| D9 mid-typing, no closing pipe",
        "a bare trailing blank line": "\n",
        "a fenced block naming no id": "\n```\nscratch\n```\n",
    }
    planted, notes = {}, []
    for name, tail in forms.items():
        wt = head + tail
        got = merge(head, wt, rows)
        preserved = bool(got["ok"]) and tail.rstrip("\n") in (got["merged"] or "")
        planted[name] = preserved
        if got["ok"] and got["separator_inserted"]:
            notes.append(f"    separator inserted for {name!r} (partial line)")
        # And the id pattern genuinely cannot see it -- that is the claim.
        assert not parse_ids(tail, RECORDS["docs/DOCKET.md"]), name

    # NEGATIVE: the overwrite form. It must DROP every one of them.
    overwrite_kept = any(
        tail.rstrip("\n") and tail.rstrip("\n") in (head + rows)
        for tail in forms.values())

    ledger = control_kind.ControlLedger(
        claim_class="worktree-only bytes that match no id pattern")
    ledger.plant("merge preserves the invisible tail",
                 vocabulary="append-only record worktree tails",
                 planted=planted,
                 negative={"the overwrite form drops it": overwrite_kept})

    failures = [n for n, ok in planted.items() if not ok]
    if overwrite_kept:
        failures.append("the overwrite form did NOT drop the tail")

    # Two further refusals, proved rather than asserted in prose.
    edited = merge(head.replace("| D2 | two |", "| D2 | EDITED |"),
                   head, rows)
    if edited["ok"]:
        failures.append("an edit inside the committed bytes was not refused")
    else:
        notes.append("    refusal proved: edit inside committed bytes -> "
                     + edited["reason"].split(",")[0])
    truncated = merge(head, head[:-12], rows)
    if truncated["ok"]:
        failures.append("a truncated worktree was not refused")
    else:
        notes.append("    refusal proved: truncated worktree -> REFUSED")
    ids = parse_ids(head, RECORDS["docs/DOCKET.md"])
    if max_for_series(ids, "D") != 2:
        failures.append("max_for_series is not the maximum existing number")
    else:
        notes.append("    id assertion proved: max existing D = 2, so the only "
                     "acceptable first id is D3")
    return ledger, len(failures), notes + [f"    FAILURE: {f}" for f in failures]


def selftest() -> int:
    ledger, n_fail, notes = run_controls()
    print("=" * 78)
    print("append_record.py -- PLANTED CONTROL SELF-TEST")
    print("=" * 78)
    print(ledger.render(n_fail))
    for line in notes:
        print(line)
    print("-" * 78)
    verdict = "PASS" if n_fail == 0 else "FAIL"
    print(f"VERDICT: {verdict}   ({n_fail} control failure(s))")
    print("CANNOT SEE: whether a preserved tail is wanted or abandoned; any "
          "commit (this module touches the working tree only); or a peer "
          "landing between your `git show` and your write -- capture HEAD once "
          "and pass the same rev here that you pass to `commit-tree -p`.")
    return EXIT_OK if n_fail == 0 else EXIT_SELFTEST


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true",
                    help="run the planted controls and exit")
    ap.add_argument("--path", help="record file, repo-relative")
    ap.add_argument("--rows", help="file holding the rows to append")
    ap.add_argument("--rev", default="HEAD",
                    help="the revision to merge onto; pass the SAME one you "
                         "pass to `commit-tree -p` (default HEAD)")
    ap.add_argument("--repo", default=".", help="repository root")
    ap.add_argument("--expect-first-id",
                    help="assert the first appended id equals this, and that "
                         "it is max+1 for its series in the committed blob")
    ap.add_argument("--dry-run", action="store_true",
                    help="report and write nothing")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()
    if not args.path or not args.rows:
        ap.error("--path and --rows are required unless --selftest")

    repo = Path(args.repo).resolve()
    pattern = RECORDS.get(args.path)
    if pattern is None:
        print(f"UNKNOWN: {args.path} is not a registered append-only record. "
              f"Known: {', '.join(sorted(RECORDS))}", file=sys.stderr)
        return EXIT_UNKNOWN

    head_text, why = read_committed(repo, args.rev, args.path)
    if head_text is None:
        print(f"UNKNOWN: {why}", file=sys.stderr)
        return EXIT_UNKNOWN
    wt_file = repo / args.path
    if not wt_file.is_file():
        print(f"UNKNOWN: no such file in the working tree: {wt_file}",
              file=sys.stderr)
        return EXIT_UNKNOWN
    worktree_text = wt_file.read_text()
    rows_text = Path(args.rows).read_text()

    head_ids = parse_ids(head_text, pattern)
    if not head_ids:
        print(f"UNKNOWN: the pattern parsed zero ids from {args.rev}:{args.path}"
              " -- the pattern or the file changed shape", file=sys.stderr)
        return EXIT_UNKNOWN
    new_ids = parse_ids(rows_text, pattern)

    print("=" * 78)
    print("append_record.py -- MERGE (D369's repair, not the overwrite)")
    print("=" * 78)
    print(f"  record           : {args.path}")
    print(f"  committed side   : {args.rev}:{args.path}  "
          f"({len(head_text)} bytes, {len(head_ids)} ids)")
    print(f"  worktree side    : {wt_file}  ({len(worktree_text)} bytes)")
    print(f"  id pattern       : {pattern}")
    print(f"  appending        : {new_ids if new_ids else '(no ids parsed)'}")

    if new_ids:
        series, first_n, _ = split_id(new_ids[0])
        top = max_for_series(head_ids, series)
        print(f"  series {series!r}: maximum existing number in the committed "
              f"blob = {top}")
        if top is None or first_n != top + 1:
            print(f"REFUSED: first appended id {new_ids[0]!r} is not max+1 "
                  f"({series}{(top or 0) + 1}) for its series in "
                  f"{args.rev}:{args.path}", file=sys.stderr)
            return EXIT_REFUSED_ID
        if args.expect_first_id and args.expect_first_id != new_ids[0]:
            print(f"REFUSED: --expect-first-id {args.expect_first_id!r} but the "
                  f"rows begin {new_ids[0]!r}", file=sys.stderr)
            return EXIT_REFUSED_ID
        print(f"  ID ASSERT ok     : {new_ids[0]} == max+1")

    got = merge(head_text, worktree_text, rows_text)
    if not got["ok"]:
        print(f"REFUSED: {got['reason']}", file=sys.stderr)
        print("Nothing was written. Inspect the difference -- never revert it "
              "(ESCALATION_CHARTER.md section 3).", file=sys.stderr)
        return EXIT_REFUSED_DISAGREES

    tail = got["tail"]
    if tail:
        print(f"  WORKTREE TAIL    : {len(tail)} bytes beyond the committed "
              f"blob, PRESERVED ahead of the appended rows")
        preview = tail if len(tail) <= 200 else tail[:200] + " ..."
        for line in preview.splitlines()[:6]:
            print(f"      | {line}")
        if got["separator_inserted"]:
            print("  NOTE             : the tail did not end in a newline (a "
                  "partial line -- somebody is mid-edit); a separator was "
                  "inserted and is reported here rather than fixed silently")
    else:
        print("  WORKTREE TAIL    : none -- the worktree equals the committed "
              "blob, so merge and overwrite coincide on this run")

    if args.dry_run:
        print("  --dry-run: nothing written")
    else:
        wt_file.write_text(got["merged"])
        print(f"  WROTE            : {wt_file} ({len(got['merged'])} bytes)")
    print("-" * 78)
    print("VERDICT: OK")
    print("CANNOT SEE: whether a preserved tail is wanted or abandoned; any "
          "commit -- the private-index sequence, the CAS and the post-commit "
          "verification remain the caller's.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
