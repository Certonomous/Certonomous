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

THE ID ASSERTION, AND WHY THE TAIL IS CONSULTED FOR ARITHMETIC ONLY
==================================================================
The first ID in the rows being appended must equal max + 1 for its own series.
Series-aware, because `docs/NUMERICS_KNOWLEDGE.md` numbers per lane -- N-B, N-D,
N-K, N-X, N-T -- and `N-B26` follows `N-B25` regardless of what N-T is up to.
Never from a number remembered from earlier in the session, which is the
L-43/L-52 trap (CLAUDE.md rule 11: the maximum existing number, never a count).

That assert used to read HEAD's blob ALONE. But the merge above lands HEAD's
blob PLUS the preserved worktree tail plus your rows, so an assert that reads
only HEAD is asserting against a different document than the one it writes.

That gap is the THIRD BITE of the D369 family, found by the closure team at
`52e5de39`: HEAD's `docs/DOCKET.md` maxed at D470, a peer's unlanded
`| D471 | ... |` sat in the worktree tail, and a caller appending D471 passed
the assert because 471 == 470 + 1. The merged file then carried D471 twice --
a duplicate minted by the very module written to stop this family of loss.

So the effective maximum is taken over HEAD's ids AND the ids parsed out of the
PRESERVED TAIL, with the same pattern and per series:

    effective max = max(max over HEAD's ids, max over the preserved tail's ids)

and the tail additionally REFUSES (exit 6) whenever it already holds an id AT OR
ABOVE the first id being appended, printing that series' tail ids and the correct
next number. It refuses rather than renumbering, for two reasons: renumbering the
caller's rows would silently change what the caller believes it filed, and the
tail's rows are somebody else's work -- `check_docket_reconciliation`'s own rule
is ASK, never renumber. The caller re-derives and retries, at commit time and in
the same shell invocation; that is rule 11 discipline, not a courtesy.

THE TAIL IS AN ARITHMETIC INPUT, NEVER AN ID AUTHORITY FOR WHAT IS COMMITTED.
Nothing about what gets written changed: the merge order is unchanged, the tail
is still preserved verbatim ahead of the appended rows, never renumbered and
never dropped, and a preserved tail is still not permission to commit somebody
else's bytes. The tail's ids are read for exactly one purpose -- to know which
numbers are already spoken for IN THE FILE THIS MODULE IS ABOUT TO WRITE -- and
for no other. A tail id is never treated as landed, never licenses an append,
and never crosses series: a tail id in a DIFFERENT series is arithmetically
irrelevant and is deliberately ignored, because `D3` cannot collide with `G7`.

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
  * WHICH IDS A TAIL HOLDS WHEN THE PREFIX TEST HAS ALREADY FAILED. There is no
    trustworthy tail in that case, so the id arithmetic falls back to HEAD alone
    and the run refuses with exit 2 anyway. Nothing is written on either path,
    so no duplicate can escape through the gap -- but the id report on such a
    run is HEAD-only and says so rather than pretending otherwise.

EXIT CONTRACT
=============
    0  OK        merged and written (or --dry-run and it would have been)
    2  REFUSED   the worktree disagrees with HEAD inside HEAD's own bytes
    3  REFUSED   the first appended id is not max + 1 for its series, over
                 HEAD's ids and the preserved tail's ids together
    4  UNKNOWN   a side could not be read, or the pattern parsed zero ids
    5  SELFTEST  a planted control did not behave as required
    6  REFUSED   the PRESERVED WORKTREE TAIL already holds that id, or a higher
                 one in the same series -- appending would land a duplicate in
                 the merged file. Re-derive the next id and retry; the tail is
                 neither renumbered nor dropped (closure `52e5de39`, D369 family)

An id refusal is reported BEFORE a prefix refusal, so 3 and 6 keep precedence
over 2 exactly as 3 did before this repair.

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
EXIT_REFUSED_TAIL_ID = 6

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


def check_first_id(head_ids: list[str], tail_ids: list[str],
                   new_ids: list[str]) -> dict:
    """Judge the first appended id against HEAD **and the preserved tail**.

    Pure, so the planted controls drive it on fixtures rather than on a repo.

    The tail is an ARITHMETIC input only (see the module docstring): its ids say
    which numbers are already spoken for in the file the merge is about to
    write. They are never treated as landed and never cross series.

    Returns a dict; `ok` False means REFUSE with `code`:
      * `EXIT_REFUSED_TAIL_ID` -- the tail already holds this id or a higher one
        in the same series. This is checked FIRST, because it is the actionable
        diagnosis: the caller must re-derive, and the numbers it needs are the
        tail's own ids and the combined next id.
      * `EXIT_REFUSED_ID` -- the first id is not max + 1 over the two sides.
    """
    series, first_n, _ = split_id(new_ids[0])
    head_max = max_for_series(head_ids, series)
    tail_max = max_for_series(tail_ids, series)
    tail_in_series = [i for i in tail_ids if split_id(i)[0] == series]
    known = [n for n in (head_max, tail_max) if n is not None]
    effective = max(known) if known else None
    out = {
        "ok": True, "code": EXIT_OK, "reason": "",
        "series": series, "first_n": first_n,
        "head_max": head_max, "tail_max": tail_max, "effective_max": effective,
        "tail_in_series": tail_in_series,
        "next_id": f"{series}{(effective if effective is not None else 0) + 1}",
    }
    if tail_max is not None and tail_max >= first_n:
        out.update(ok=False, code=EXIT_REFUSED_TAIL_ID, reason=(
            f"the PRESERVED WORKTREE TAIL already holds {series}-series id(s) "
            f"{tail_in_series} -- at or above the first appended id "
            f"{new_ids[0]!r}. The merge lands HEAD's blob, that tail AND your "
            f"rows, so appending here would write two rows with the same id "
            f"(closure 52e5de39, the D369 family's third bite). The correct "
            f"next id over HEAD (max {head_max}) and the tail (max {tail_max}) "
            f"together is {out['next_id']}. Re-derive and retry -- the tail is "
            f"neither renumbered nor dropped, because renumbering another "
            f"agent's row is that agent's call (ASK, never renumber)."))
        return out
    if effective is None or first_n != effective + 1:
        out.update(ok=False, code=EXIT_REFUSED_ID, reason=(
            f"first appended id {new_ids[0]!r} is not max+1 ({out['next_id']}) "
            f"for its series over HEAD (max {head_max}) and the preserved "
            f"worktree tail (max {tail_max})"))
    return out


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

    A SECOND control was added for the tail-id repair (closure `52e5de39`, the
    D369 family's third bite). Its claim is the opposite shape -- not "bytes
    survived" but "a collision was refused" -- so it plants peer tails that DO
    carry ids and requires a refusal with `EXIT_REFUSED_TAIL_ID` while the tail
    is still preserved verbatim, with a cross-series tail as the negative form
    that must NOT block. Both id forms are asserted VISIBLE to the pattern
    first: a refusal that failed to fire and a reader that could not see the id
    look identical from the outside, and only one of them is this module working.
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
    pattern = RECORDS["docs/DOCKET.md"]
    planted, notes = {}, []
    for name, tail in forms.items():
        wt = head + tail
        got = merge(head, wt, rows)
        preserved = bool(got["ok"]) and tail.rstrip("\n") in (got["merged"] or "")
        # Control (d) after the tail-id repair: an ID-LESS tail must still merge,
        # still be preserved, AND still not block the append. A repair that made
        # the id assert tail-aware could easily have made an invisible tail
        # refuse; this asserts it did not.
        id_ok = check_first_id(parse_ids(head, pattern),
                               parse_ids(got["tail"] or "", pattern),
                               parse_ids(rows, pattern))["ok"] if got["ok"] \
            else False
        planted[name] = bool(preserved and id_ok)
        if got["ok"] and got["separator_inserted"]:
            notes.append(f"    separator inserted for {name!r} (partial line)")
        # And the id pattern genuinely cannot see it -- that is the claim.
        assert not parse_ids(tail, RECORDS["docs/DOCKET.md"]), name

    # NEGATIVE: the overwrite form. It must DROP every one of them.
    overwrite_kept = any(
        tail.rstrip("\n") and tail.rstrip("\n") in (head + rows)
        for tail in forms.values())

    # ---- the id arithmetic, planted against the tail (closure 52e5de39) ----
    # The defect: HEAD max D2, a peer's unlanded row in the worktree tail, and a
    # caller appending the id that peer already used. Old assert read HEAD only,
    # so 3 == 2 + 1 passed and the merged file carried D3 twice. Each form below
    # must REFUSE with EXIT_REFUSED_TAIL_ID **and** still preserve the tail --
    # refusing by dropping somebody's row would be a different defect.
    id_forms = {
        "a peer tail carrying the would-be next id":
            "| D3 | peer, unlanded, same number |\n",
        "a peer tail already several numbers ahead":
            "| D7 | peer, unlanded, further ahead |\n",
    }
    id_planted = {}
    for name, tail in id_forms.items():
        # Plant the zero: the reader must be shown able to SEE this id, or a
        # refusal that failed to fire would be indistinguishable from blindness.
        assert parse_ids(tail, pattern), name
        got_id = merge(head, head + tail, rows)
        v = check_first_id(parse_ids(head, pattern),
                           parse_ids(got_id["tail"] or "", pattern),
                           parse_ids(rows, pattern))
        refused = (not v["ok"]) and v["code"] == EXIT_REFUSED_TAIL_ID
        preserved_too = bool(got_id["ok"]) and tail in (got_id["merged"] or "")
        id_planted[name] = bool(refused and preserved_too)
        if refused:
            notes.append(
                f"    id refusal proved ({name}): exit {v['code']}, tail ids "
                f"{v['tail_in_series']}, HEAD max {v['head_max']}, tail max "
                f"{v['tail_max']}, correct next id {v['next_id']}; tail still "
                f"preserved verbatim: {preserved_too}")

    # NEGATIVE FORM: a tail id in a DIFFERENT series must NOT block this append.
    # Ids are per-series (rule 11; N-B26 follows N-B25 whatever N-T is doing), so
    # `G7` cannot collide with `D3` and the append must proceed. Asserting the
    # pattern DOES see `G7` is what stops this from being a vacuous pass.
    cross_tail = "| G7 | another series, unlanded |\n"
    assert parse_ids(cross_tail, pattern) == ["G7"], "cross-series form vacuous"
    cross_m = merge(head, head + cross_tail, rows)
    cross_v = check_first_id(parse_ids(head, pattern),
                             parse_ids(cross_m["tail"] or "", pattern),
                             parse_ids(rows, pattern))
    cross_blocked = not cross_v["ok"]
    if not cross_blocked:
        notes.append(
            "    cross-series decision proved: the tail's 'G7' IS parsed by the "
            "pattern and is deliberately ignored for the D-series arithmetic "
            f"(effective max {cross_v['effective_max']}), so the D3 append "
            "proceeds -- a tail id in another series is arithmetically "
            "irrelevant and must not block")

    ledger = control_kind.ControlLedger(
        claim_class="worktree-only bytes that match no id pattern")
    ledger.plant("merge preserves the invisible tail",
                 vocabulary="append-only record worktree tails",
                 planted=planted,
                 negative={"the overwrite form drops it": overwrite_kept})
    ledger.plant("the id assert judges HEAD AND the preserved tail",
                 vocabulary="peer rows sitting unlanded in a worktree tail",
                 planted=id_planted,
                 negative={"a tail id in a DIFFERENT series blocks the append":
                           cross_blocked})

    failures = [n for n, ok in planted.items() if not ok]
    if overwrite_kept:
        failures.append("the overwrite form did NOT drop the tail")
    failures += [f"tail-id control did not refuse-and-preserve: {n}"
                 for n, ok in id_planted.items() if not ok]
    if cross_blocked:
        failures.append("a tail id in a DIFFERENT series blocked the append")

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
                         "it is max+1 for its series over the committed blob "
                         "AND the preserved worktree tail")
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

    # The merge is computed HERE, before the id assert, so the arithmetic can
    # see the very bytes this module is about to write: HEAD's blob plus the
    # preserved tail. The REFUSAL ORDER is deliberately unchanged -- an id
    # refusal is still reported before a prefix refusal, so exit 3 keeps its
    # precedence over exit 2 exactly as it had before this repair. When the
    # prefix test has failed there is no trustworthy tail, so the arithmetic
    # falls back to HEAD alone and the run refuses with 2 below regardless;
    # nothing is written on either path.
    got = merge(head_text, worktree_text, rows_text)
    tail_text = got["tail"] if got["ok"] else ""
    tail_ids = parse_ids(tail_text, pattern)

    print("=" * 78)
    print("append_record.py -- MERGE (D369's repair, not the overwrite)")
    print("=" * 78)
    print(f"  record           : {args.path}")
    print(f"  committed side   : {args.rev}:{args.path}  "
          f"({len(head_text)} bytes, {len(head_ids)} ids)")
    print(f"  worktree side    : {wt_file}  ({len(worktree_text)} bytes)")
    print(f"  id pattern       : {pattern}")
    print(f"  appending        : {new_ids if new_ids else '(no ids parsed)'}")
    if got["ok"]:
        print(f"  tail ids         : "
              f"{tail_ids if tail_ids else '(none in the preserved tail)'}")
    else:
        print("  tail ids         : (not read -- the prefix test failed, so "
              "there is no trustworthy tail; the id report below is HEAD-only "
              "and this run refuses either way)")

    if new_ids:
        v = check_first_id(head_ids, tail_ids, new_ids)
        print(f"  series {v['series']!r}: maximum existing number -- committed "
              f"blob {v['head_max']}, preserved worktree tail {v['tail_max']}, "
              f"EFFECTIVE {v['effective_max']}")
        if not v["ok"]:
            print(f"REFUSED: {v['reason']}", file=sys.stderr)
            return v["code"]
        if args.expect_first_id and args.expect_first_id != new_ids[0]:
            print(f"REFUSED: --expect-first-id {args.expect_first_id!r} but the "
                  f"rows begin {new_ids[0]!r}", file=sys.stderr)
            return EXIT_REFUSED_ID
        print(f"  ID ASSERT ok     : {new_ids[0]} == max+1 over HEAD AND the "
              f"preserved tail")

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
