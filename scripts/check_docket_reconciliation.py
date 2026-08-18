#!/usr/bin/env python3
r"""Did a docket row land in a commit and never reach the worktree, or the reverse.

WHY THIS EXISTS (docket D221, D240; docs/USING_THIS_LAB.md section 11b item 8)
==============================================================================
`docs/DOCKET.md` is written by many agents at once, so a pathspec commit of it
takes the WORKING TREE copy and swallows every foreign row sitting in it. The
protocol that replaces the pathspec form rebuilds the blob as **HEAD's docket
plus the author's own rows**, selected by row ID, and lands it with a
compare-and-swap. That form is correct and it has one by-product: it never
writes the row back into the working copy, so every conforming commit widens the
gap between HEAD and the worktree.

The guide documents a manual reconciliation step. Documentation did not stop it:
`D241` diverged at `a703f972`, and `D242`/`D243` diverged again at `6097856c`
within the same hour, after the step was published. A manual step in a document
is a hope, not a control. This module is the control.

WHAT DIVERGENCE COSTS, IN EACH DIRECTION
========================================
The two directions are not two halves of one fault. They have opposite meanings
and opposite repairs, and collapsing them into a count destroys the distinction:

    IN HEAD, NOT IN THE WORKTREE   A row landed by private index and never
                                   written back. The row is safe -- it is in a
                                   commit. HEAD WINS. Restore it into the
                                   worktree by inserting it in numeric order by
                                   ID. Do not commit it again.

    IN THE WORKTREE, NOT IN HEAD   UNLANDED WORK. Somebody's finding lives in
                                   no commit, is invisible to `git log`, and is
                                   destroyed outright by `git checkout --
                                   docs/DOCKET.md`, `git stash` or `git reset
                                   --hard` -- all four forbidden here
                                   (ESCALATION_CHARTER.md section 3). Land it BY
                                   ID through the private-index form. Never by
                                   copying the worktree file into a commit,
                                   which is the capture the form exists to
                                   prevent.

The second is strictly the more dangerous, which is why it carries its own exit
code rather than sharing one.

SETS, NEVER TOTALS
==================
This module compares ID **sets** and reports the symmetric difference by name.
It never reports "HEAD has N rows, the worktree has M". That is deliberate and
it is a measured lesson rather than a preference: on 2026-08-16 three separate
row totals for the same commit -- 244, 242 and 278 -- were all defensible,
because they came from three different ID patterns, and a total published
without its pattern sent two agents chasing a divergence that the set difference
located exactly (one row, `D241`). A count is not reproducible without its
regex. A set difference names its members and needs no regex to be believed.

So this module PRINTS THE PATTERN IT USED, on every run, in both output modes.

THE PATTERN, AND THE TRAP IT WAS BUILT AROUND
=============================================
An ID must be the WHOLE first cell of a table row, modulo `**bold**` and
`~~strike~~` decoration, in any order and any nesting. Anchoring to the whole
cell is not tidiness. `docs/DOCKET.md` contains rows whose first cell is
`D19-D20 note` and `D167-D169 note`, which are commentary rows and not docket
items; the widely-copied recipe `^\| \*{0,2}D[0-9]+` matches `D19` inside the
first of them and invents an ID that duplicates a real row. Measured at
`c2cd83bf`: 273 bare IDs, 7 bold, 0 struck, 2 note rows correctly excluded.
Struck IDs are tolerated because section 11's rule is that superseded IDs are
struck in place and kept, though none was observed at that commit.

WHAT THIS CHECK CANNOT SEE
==========================
  * WHETHER A ROW'S CONTENT DIVERGED. It compares the ID sets. Two rows with
    the same ID and different bodies read as reconciled here. Use
    `git diff HEAD -- docs/DOCKET.md` for content -- and see the next point
    before you do.
  * ANY OTHER FILE. The write-back gap is a property of the private-index
    protocol, which is used on `docs/DOCKET.md` and, so far, nowhere else.
  * WHETHER AN UNLANDED ROW IS ABANDONED OR IN FLIGHT. A worktree-only row may
    be an agent's live work seconds from being committed. This check reports the
    fact and never the intent, and it must not be read as an instruction to land
    somebody else's row without asking them.
  * THE INDEX. It compares a COMMIT against the WORKING TREE, deliberately, and
    never uses `git diff` without an explicit revision. `git diff -- <path>`
    compares against the shared `.git/index`, which any other agent's `git add`
    can poison: measured at `5a0127d3`, `git diff --stat -- docs/DOCKET.md`
    reported 8 insertions on a file that was byte-identical to HEAD.

EXIT CONTRACT
=============
    0  PASS      the ID sets are equal
    1  FAIL      rows in HEAD are missing from the worktree; write-back owed
    2  FAIL      rows in the worktree are in no commit -- UNLANDED WORK at risk
                 (also used when both directions are non-empty: the worse of the
                 two decides)
    3  UNKNOWN   a side could not be read: git failed, the file is absent, or a
                 side parsed to zero IDs, which means the pattern or the file
                 changed shape rather than that the docket is empty

No status is ever taken through a pipe inside this module. Every subprocess is
run with a list argument and its `returncode` is read from the completed
process, because a pipe replaces the exit status of the command that produced
it with that of the last stage.
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

EXIT_PASS = 0
EXIT_FAIL_WRITEBACK_OWED = 1
EXIT_FAIL_UNLANDED = 2
EXIT_UNKNOWN = 3
# A duplicate id is NOT unlanded work and must not share its code. Reusing
# EXIT_FAIL_UNLANDED for it (as the first version of this rule did) also
# duplicated the assignment line that sets FAIL with the unlanded code, and the
# mutation harness anchors M2 on exactly that line -- so the mutation silently
# retargeted onto the new branch, which no test exercised, and M2 went from
# KILLED to SURVIVED while the harness still exited 1 and nothing looked wrong.
# Coverage fell and no exit code moved. A mutation anchored to a source literal
# retargets when a copy is inserted above it.
EXIT_FAIL_DUPLICATE = 4

DEFAULT_PATH = "docs/DOCKET.md"
DEFAULT_REV = "HEAD"

#: The ID must be the entire first cell, modulo bold/strike decoration.
#: See "THE PATTERN, AND THE TRAP IT WAS BUILT AROUND" above.
ID_PATTERN = r"^\|\s*(?:\*\*|~~)*\s*([A-G]\d+[a-z]?)\s*(?:~~|\*\*)*\s*\|"

_ID_RE = re.compile(ID_PATTERN, re.M)


def parse_ids(text: str) -> list[str]:
    """Every docket row ID in *text*, in the order the rows appear.

    Duplicates are preserved here so a caller can see them; the comparison
    itself is over sets.
    """
    return _ID_RE.findall(text)


def sort_key(row_id: str) -> tuple[str, int, str]:
    """Docket order: section letter, then the number NUMERICALLY, then suffix.

    `sort -u` on these sorts lexically, which puts `D99` after `D146`. The
    guide's own section 11 records that defect being run as written and
    allocating an ID that had been taken weeks earlier.
    """
    match = re.match(r"([A-G])(\d+)([a-z]?)", row_id)
    if match is None:  # pragma: no cover - parse_ids cannot produce this
        return ("Z", 0, row_id)
    return (match.group(1), int(match.group(2)), match.group(3))


def read_committed(repo: Path, rev: str, path: str) -> tuple[str | None, str]:
    """The blob at *rev*:*path*, or (None, reason).

    `subprocess.run` with a list and an explicit `returncode` read -- never a
    shell pipeline, whose status would be the last stage's.
    """
    completed = subprocess.run(
        ["git", "-C", str(repo), "show", f"{rev}:{path}"],
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip().splitlines()
        reason = detail[-1] if detail else f"git exited {completed.returncode}"
        return None, f"could not read {rev}:{path} -- {reason}"
    return completed.stdout, ""


def read_worktree(worktree_file: Path) -> tuple[str | None, str]:
    """The working copy, or (None, reason)."""
    if not worktree_file.is_file():
        return None, f"no such file in the working tree: {worktree_file}"
    try:
        return worktree_file.read_text(), ""
    except OSError as exc:
        return None, f"could not read {worktree_file}: {exc}"


def run_controls() -> control_kind.ControlLedger:
    """Plant the docket's OWN id vocabulary and check the pattern finds it.

    WHY THIS CHECK NEEDS A RECOGNITION CONTROL AND NOT A REACHABILITY ONE.
    This module's PASS is a zero: an empty symmetric difference. A pattern that
    failed to recognise one decoration would drop that id from BOTH sides, the
    difference would cancel, and the run would report a false PASS -- so a row
    landed bold and never written back would be invisible to the very check
    written to catch it. Proving the module can READ both files would not touch
    that failure. So the forms below are planted in the docket's own row
    vocabulary, mutually independent (no one of them is a substring of
    another), and the note row is planted as a NEGATIVE form because a pattern
    loose enough to match it invents ids that duplicate real rows.
    """
    forms = {
        "| D9001 | a bare row |": "D9001",
        "| **D9002** | a bold row |": "D9002",
        "| ~~D9003~~ | a struck row |": "D9003",
        "| **~~D9004~~** | a bold struck row |": "D9004",
        "| B9005a | a lettered row with a suffix |": "B9005a",
    }
    planted = {form: (expect in parse_ids(form)) for form, expect in forms.items()}
    negative_form = "| D9006-D9007 note | commentary, not a row |"
    ledger = control_kind.ControlLedger(claim_class="a docket row id")
    ledger.plant("docket id decorations",
                 vocabulary="docs/DOCKET.md table rows",
                 planted=planted,
                 negative={negative_form: bool(parse_ids(negative_form))})
    return ledger


def reconcile(committed_text: str, worktree_text: str,
              ledger: "control_kind.ControlLedger | None" = None) -> dict:
    """The comparison itself. Pure, so the tests can drive it on fixtures.

    *ledger* is injectable so a test can drive a REACHABILITY-only control
    through the same path and see the zero refused.
    """
    committed_ids = parse_ids(committed_text)
    worktree_ids = parse_ids(worktree_text)
    committed_set = set(committed_ids)
    worktree_set = set(worktree_ids)

    head_only = sorted(committed_set - worktree_set, key=sort_key)
    worktree_only = sorted(worktree_set - committed_set, key=sort_key)

    # DUPLICATE IDS, ON EITHER SIDE. Added 2026-08-18 after a live collision: two
    # lanes independently wrote a row numbered D406, and this check returned
    # PASS. A set difference CANNOT see a duplicate -- `{D001,D002,D002,D003}`
    # and `{D001,D002,D003}` are the same set -- so the one thing an ID-keyed
    # ledger most needs a reconciliation to catch was precisely the thing it
    # could not. The row counts were already printed (3 against 4) and were
    # explicitly labelled "diagnostic only", so the evidence was on screen and
    # carried no weight, which is worse than not printing it.
    #
    # Proved by planting rather than by reading: a scratch repository whose
    # worktree carried a second row wearing D002 exited 0 / PASS before this
    # block existed.
    #
    # A duplicate is a FAIL on the side that carries it. Two different findings
    # wearing one name means every later citation of that ID is ambiguous, and
    # the docket is append-only, so the ambiguity is permanent unless caught here.
    committed_dupes = sorted({i for i in committed_ids if committed_ids.count(i) > 1}, key=sort_key)
    worktree_dupes = sorted({i for i in worktree_ids if worktree_ids.count(i) > 1}, key=sort_key)

    ledger = run_controls() if ledger is None else ledger
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
    elif zero_verdict != control_kind.ZERO_IS_A_MEASUREMENT:
        # THE TEETH. An empty symmetric difference is a ZERO, and this module
        # refuses to present a zero as PASS unless its own pattern has been
        # shown to RECOGNISE the claim class -- not merely to have read the
        # files. Weaken the pattern and the control degrades to REACHABILITY
        # (or BROKEN), and PASS stops being reachable at all.
        verdict, code = "UNKNOWN", EXIT_UNKNOWN
    else:
        verdict, code = "PASS", EXIT_PASS

    return {
        "verdict": verdict,
        "exit_code": code,
        "head_only": head_only,
        "worktree_only": worktree_only,
        "committed_dupes": committed_dupes,
        "worktree_dupes": worktree_dupes,
        "committed_row_count": len(committed_ids),
        "worktree_row_count": len(worktree_ids),
        "id_pattern": ID_PATTERN,
        "control_kind": ledger.kind,
        "zero_verdict": zero_verdict,
        "zero_because": zero_why,
        "control_report": ledger.render(hits),
    }


def render(result: dict, rev: str, path: str, worktree_file: Path) -> str:
    """The human report. The pattern is printed whether or not anything failed."""
    width = 78
    out: list[str] = []
    out.append("=" * width)
    out.append("DOCKET RECONCILIATION -- committed rows against the working copy")
    out.append("=" * width)
    out.append(f"  committed side   : {rev}:{path}")
    out.append(f"  worktree side    : {worktree_file}")
    out.append(f"  id pattern       : {result['id_pattern']}")
    out.append(
        "  rows parsed      : "
        f"{result['committed_row_count']} committed, "
        f"{result['worktree_row_count']} in the working copy "
        "(counts are diagnostic only -- the verdict is over ID SETS)"
    )
    for side, dupes in (("HEAD", result.get("committed_dupes") or []),
                        ("THE WORKTREE", result.get("worktree_dupes") or [])):
        if dupes:
            out.append("-" * width)
            out.append(f"DUPLICATE IDS IN {side} ({len(dupes)}): " + ", ".join(dupes))
            out.append("    TWO ROWS WEAR ONE NAME. Every later citation of this id is ambiguous,")
            out.append("    and the docket is append-only, so the ambiguity does not expire. The")
            out.append("    later writer takes the next free id; renumbering another agent's row")
            out.append("    is that agent's call, so ASK rather than renumbering it for them.")
    out.append("-" * width)

    if result["verdict"] == "UNKNOWN":
        out.append("VERDICT: UNKNOWN")
        out.append(
            "BECAUSE: a side parsed to ZERO ids. That is a shape change in the "
            "file or in the pattern, not an empty docket, and it is reported as "
            "UNKNOWN rather than PASS so an unreadable surface can never be "
            "mistaken for a reconciled one."
        )
        out.append("-" * width)
        out.append(f"id pattern used: {result['id_pattern']}")
        return "\n".join(out)

    if result["head_only"]:
        out.append(
            f"IN HEAD, NOT IN THE WORKTREE ({len(result['head_only'])}): "
            + ", ".join(result["head_only"])
        )
        out.append(
            "    A row landed by private index and never written back. The row "
            "is SAFE -- it is in a commit. HEAD WINS: restore it into the "
            "worktree by inserting it in NUMERIC order by ID. Do NOT commit it "
            "again."
        )
    if result["worktree_only"]:
        out.append(
            f"IN THE WORKTREE, NOT IN HEAD ({len(result['worktree_only'])}): "
            + ", ".join(result["worktree_only"])
        )
        out.append(
            "    UNLANDED WORK. This finding lives in no commit, is invisible "
            "to `git log`, and is destroyed outright by `git checkout -- "
            f"{path}`, `git stash` or `git reset --hard`. Land it BY ID through "
            "the private-index form; never by committing the worktree file, "
            "which captures every other agent's row sitting in it. If it is not "
            "yours, ASK before landing it -- this check reports the fact and "
            "cannot see the intent."
        )
    if not result["head_only"] and not result["worktree_only"]:
        out.append("Both sides carry the same set of row IDs.")

    if result.get("control_report"):
        out.append(result["control_report"])
    out.append("-" * width)
    out.append(f"VERDICT: {result['verdict']}")
    out.append(
        "CANNOT SEE: whether a row's CONTENT diverged (same ID, different body "
        "reads as reconciled here); any file other than the docket; whether an "
        "unlanded row is abandoned or in flight; and the index, which this "
        "check deliberately never consults."
    )
    out.append(f"id pattern used: {result['id_pattern']}")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compare the docket row-ID set in a commit against the working copy."
        )
    )
    parser.add_argument("--repo", default=".", help="repository to read")
    parser.add_argument(
        "--rev",
        default=DEFAULT_REV,
        help="the committed side (default HEAD). Also used to reconstruct a "
        "past divergence: --rev <sha> --worktree-from <sha>~1",
    )
    parser.add_argument("--path", default=DEFAULT_PATH, help="docket path in the repo")
    parser.add_argument(
        "--worktree-file",
        default=None,
        help="override the working-copy side (default <repo>/<path>)",
    )
    parser.add_argument(
        "--worktree-from",
        default=None,
        help="read the working-copy side from a REVISION instead of disk. For "
        "reconstructing a historical divergence and for this module's own "
        "controls, which must not depend on the working tree they run in.",
    )
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args(argv)

    repo = Path(args.repo).resolve()

    committed_text, why = read_committed(repo, args.rev, args.path)
    if committed_text is None:
        return _unknown(args, why, repo)

    if args.worktree_from is not None:
        worktree_label = f"{args.worktree_from}:{args.path}"
        worktree_text, why = read_committed(repo, args.worktree_from, args.path)
    else:
        worktree_file = (
            Path(args.worktree_file)
            if args.worktree_file
            else repo / args.path
        )
        worktree_label = str(worktree_file)
        worktree_text, why = read_worktree(worktree_file)
    if worktree_text is None:
        return _unknown(args, why, repo)

    result = reconcile(committed_text, worktree_text)
    result["rev"] = args.rev
    result["path"] = args.path
    result["worktree_side"] = worktree_label

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(render(result, args.rev, args.path, Path(worktree_label)))
    return int(result["exit_code"])


def _unknown(args: argparse.Namespace, why: str, repo: Path) -> int:
    """An unreadable side is UNKNOWN, never PASS and never FAIL."""
    payload = {
        "verdict": "UNKNOWN",
        "exit_code": EXIT_UNKNOWN,
        "because": why,
        "id_pattern": ID_PATTERN,
        "rev": args.rev,
        "path": args.path,
        "repo": str(repo),
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("VERDICT: UNKNOWN")
        print(f"BECAUSE: {why}")
        print(f"id pattern used: {ID_PATTERN}")
    return EXIT_UNKNOWN


if __name__ == "__main__":
    sys.exit(main())
