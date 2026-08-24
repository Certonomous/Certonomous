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

THE CONTROL WAS SHAPED FOR TWO RECORDS AND RAN ON FOUR (repaired 2026-08-24)
============================================================================
`RECORDS` grew `docs/DOCKET.md` and `docs/COST_CALIBRATION.md`, whose ids are
TABLE ROWS (`| D486 |`, `| C-40 |`), not headings. The control below did not
grow with it: it planted lesson forms for `docs/LESSONS.md` and NUMERICS forms
-- `**N-B9001.`, `## N-X9002.` -- for **everything else**. A `| C-40 |` row can
never match `^(?:\*\*|## )(N-[A-Z]+\d+)\.`, so on those two ledgers every planted
form read NOT FOUND, the ledger classified BROKEN, and the run printed
`ZERO_IS_UNSUPPORTED` -- while still returning its reconciliation exit code as
though the reading stood. Three lanes hit it in one day (`docs/COST_CALIBRATION.md`
rows C-36, C-39, C-40). That is CLAUDE.md rule 3 exactly: a zero from a reader
not shown able to see a non-zero is not evidence.

The repair has three parts, and the first is the one that stops the defect
recurring:

  1. **A control form table with ONE ENTRY PER RECORD, keyed by the same keys as
     the pattern table, asserted equal at import.** A record added to `RECORDS`
     with no control forms REFUSES; it can no longer fall through to another
     record's shapes. The fall-through WAS the defect -- nothing was missing, the
     wrong thing was silently substituted.
  2. **A per-kind DISK control.** Each kind plants a row of its own shape into a
     temp copy of the committed blob and a different one into a temp copy of the
     working file, then reads both back through the production readers
     (`git show` for the committed side, `read_text` for the worktree side) and
     requires the check to NAME each plant on the correct side.
  3. **A refusal.** A BROKEN ledger now exits 5 instead of reporting a verdict
     over a reader that was not shown able to read (rule 4: refuse, never
     degrade).

ONE PATTERN TABLE, IMPORTED, NEVER COPIED (CLAUDE.md rule 14)
=============================================================
`RECORDS` is defined once, in `scripts/append_record.py` (lines 153-184 at
`eb2a534b`), and imported here -- so the writer and the reconciler cannot drift
apart, because there is nothing to drift. This module holds NO pattern literal of
its own, and the identity assert below is what keeps it that way: a second copy
appearing here would have to disagree silently to do any harm, and an import
cannot. Everything this module adds is keyed BY that table.

EXIT CONTRACT -- identical to the docket module, deliberately
=============================================================
    0  PASS      the id sets are equal
    1  FAIL      entries in HEAD are missing from the worktree; write-back owed
    2  FAIL      entries in the worktree are in no commit -- UNLANDED WORK
    3  UNKNOWN   a side could not be read, or parsed to zero ids
    4  FAIL      a duplicate id on either side
    5  REFUSED   a planted control did not fire, so this reader is NOT known to
                 be able to see the ids it would report absent. No reconciliation
                 verdict is issued. `--selftest` uses this code too.
                 (2026-08-24. The brief that ordered this repair asked for the
                 refusal at exit 2; 2 is already UNLANDED WORK in the docket
                 module's contract, which this one copies deliberately, so the
                 refusal took 5 -- `append_record.py`'s own `EXIT_SELFTEST`.
                 Disclosed rather than renumbered.)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import control_kind  # noqa: E402
import append_record  # noqa: E402
from append_record import RECORDS, parse_ids, split_id  # noqa: E402

# CLAUDE.md rule 14, made mechanical: the id pattern table is THE table in
# append_record.py, imported. If a second copy is ever pasted into this module
# the two instruments can disagree about what an id is, and the reconciliation
# would then be graded under a pattern the writer never used. There is nothing
# to pick between and nothing to reconcile -- there is one object.
assert RECORDS is append_record.RECORDS, (
    "the id pattern table must be the imported append_record.RECORDS, never a "
    "second copy in this module (CLAUDE.md rule 14)")

EXIT_PASS = 0
EXIT_FAIL_WRITEBACK_OWED = 1
EXIT_FAIL_UNLANDED = 2
EXIT_UNKNOWN = 3
EXIT_FAIL_DUPLICATE = 4
EXIT_CONTROL_REFUSED = 5

DEFAULT_PATHS = ["docs/LESSONS.md", "docs/NUMERICS_KNOWLEDGE.md"]
DEFAULT_REV = "HEAD"

#: PLANTED CONTROL FORMS, one entry per record in `RECORDS`, each written in
#: THAT record's own vocabulary -- headings for the two prose records, table rows
#: for the two ledgers. Before 2026-08-24 this table did not exist and every
#: non-LESSONS record was given NUMERICS forms; see the module docstring.
#:
#:   forms          shapes the pattern MUST parse, id it must yield. Two or more,
#:                  mutually non-substring, or `control_kind` demotes the control
#:                  to REACHABILITY and the zero stops being a measurement.
#:   negatives      shapes the pattern MUST NOT parse. For the two ledgers these
#:                  are the table's own header and `|---|` separator: a looser
#:                  pattern would mint ids out of table furniture.
#:   base/head_only/worktree_only
#:                  the disk control's plants. `base` lands on both sides,
#:                  `head_only` in the commit alone, `worktree_only` in the
#:                  working copy alone, so one planted repo exercises both
#:                  directions of the difference at once.
CONTROL_FORMS = {
    "docs/LESSONS.md": {
        "forms": {
            "## L-9001. a lesson heading": "L-9001",
            "## L-9002. another, three digits over": "L-9002",
        },
        "negatives": [
            "a mid-sentence mention of L-9003 in prose",
            "## L-43, second corollary. a second block under an existing id",
            "### L-63 - CORRECTION, an h3 amendment",
        ],
        "base": "# Lessons\n\n## L-9000. on both sides, must not appear in either difference\n",
        "head_only": "\n## L-9101. planted in the committed blob only\n",
        "worktree_only": "\n## L-9102. planted in the working copy only\n",
    },
    "docs/NUMERICS_KNOWLEDGE.md": {
        # Kept exactly as it was: both live entry forms and both series, because
        # a pattern blind to one FORM drops that form from both sides and the
        # symmetric difference cancels into a false PASS.
        "forms": {
            "**N-B9001. a bold entry**": "N-B9001",
            "## N-X9002. an h2 entry": "N-X9002",
            "**N-T9003. a third series, bold**": "N-T9003",
        },
        "negatives": [
            "a mid-sentence mention of N-B9004 in prose",
            "  **N-B9005. an indented entry, not at column 0**",
        ],
        "base": "# Numerics\n\n**N-B9000. on both sides, must not appear in either difference**\n",
        "head_only": "\n## N-X9101. planted in the committed blob only\n",
        "worktree_only": "\n**N-B9102. planted in the working copy only**\n",
    },
    "docs/DOCKET.md": {
        # Rows, not headings. The bold form is live in the file and is the form
        # a pattern "tidied" down to `^\|\s*([A-G]\d+)` would silently drop.
        "forms": {
            "| D9001 | a docket row |": "D9001",
            "| **G9002** | a bold row, another series |": "G9002",
            "| D9003a | a lettered-suffix row |": "D9003a",
        },
        "negatives": [
            "a mid-sentence mention of D9004 in prose",
            "| id | item | owner |",
            "|---|---|---|",
            # The exclusion `check_docket_reconciliation`'s pattern was written
            # around: a range in the first cell is one note, not two rows.
            "| D19-D20 note | a range, not an id |",
        ],
        "base": ("| id | item | owner |\n|---|---|---|\n"
                 "| D9000 | on both sides, must not appear in either difference | lane |\n"),
        "head_only": "| D9101 | planted in the committed blob only | lane |\n",
        "worktree_only": "| D9102 | planted in the working copy only | lane |\n",
    },
    "docs/COST_CALIBRATION.md": {
        # TRAP, carried over from the pattern's own comment in append_record.py:
        # the id carries a HYPHEN. A pattern tidied to `C\d+` parses NOTHING
        # here, which is precisely the shape of the defect this table repairs.
        "forms": {
            "| C-9001 | 2026-08-24 | verification | a cost row |": "C-9001",
            "| **C-9002** | 2026-08-24 | verification | a bold cost row |": "C-9002",
        },
        "negatives": [
            "a mid-sentence mention of C-9003 in prose",
            "| id | date | team | process |",
            "|---|---|---|---|",
        ],
        "base": ("| id | date | team | process |\n|---|---|---|---|\n"
                 "| C-9000 | 2026-08-24 | verification | on both sides | \n"),
        "head_only": "| C-9101 | 2026-08-24 | verification | committed blob only |\n",
        "worktree_only": "| C-9102 | 2026-08-24 | verification | working copy only |\n",
    },
}

# REFUSE ON DISAGREEMENT, never pick one. The two tables are keyed the same or
# this module does not load: a record that gains a pattern but no control forms
# would otherwise be graded under some other record's shapes, which is the
# 2026-08-24 defect verbatim.
_MISSING = sorted(set(RECORDS) - set(CONTROL_FORMS))
_EXTRA = sorted(set(CONTROL_FORMS) - set(RECORDS))
if _MISSING or _EXTRA:  # pragma: no cover - a load-time refusal
    raise SystemExit(
        f"REFUSED: the control form table and append_record.RECORDS disagree. "
        f"Records with a pattern but no planted control forms: {_MISSING or 'none'}. "
        f"Control forms for no registered record: {_EXTRA or 'none'}. "
        f"Add the missing forms IN THAT RECORD'S OWN VOCABULARY -- do not let a "
        f"record borrow another's shapes (CLAUDE.md rule 3, rule 14).")


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


def _plant_repo(box: Path, path: str, committed: str, worktree: str) -> Path:
    """A one-commit repo whose worktree copy of *path* differs from its blob.

    The shared `.git/index` is never touched: this is a fresh repository in a
    temp directory with its own index, and the env below strips any inherited
    `GIT_INDEX_FILE`/`GIT_DIR`/`GIT_WORK_TREE` so a caller running under the
    private-index protocol cannot have its index caught in here (CLAUDE.md
    rule 10). The `git add` is by explicit pathspec, never `-A`.
    """
    repo = box / "repo"
    env = {k: v for k, v in os.environ.items()
           if k not in ("GIT_INDEX_FILE", "GIT_DIR", "GIT_WORK_TREE")}
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull

    def run(args: list[str], cwd: Path) -> None:
        done = subprocess.run(args, cwd=str(cwd), env=env,
                              capture_output=True, text=True)
        if done.returncode != 0:
            raise RuntimeError(f"{' '.join(args)} -> {done.returncode}: "
                               f"{done.stderr.strip()[:200]}")

    repo.mkdir(parents=True)
    run(["git", "init", "-q", "."], repo)
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(committed)
    run(["git", "add", "--", path], repo)
    run(["git", "-c", "user.name=control", "-c", "user.email=control@localhost",
         "commit", "-q", "-m", "planted control commit", "--", path], repo)
    target.write_text(worktree)          # the worktree now diverges, by design
    return repo


def run_disk_control(path: str) -> dict:
    """Plant an id on ONE SIDE ONLY and read it back through this check's readers.

    The string control below proves the pattern recognises the record's entry
    FORMS. It does not prove this module can carry a difference from disk to the
    printed report: the committed side comes out of `git show` and the worktree
    side out of `read_text`, and either could be wired to the wrong file, the
    wrong revision, or a pattern that never sees the plant. So one planted repo
    carries three ids -- one on both sides, one committed-only, one
    worktree-only -- and all three claims are read back through
    `read_committed()` and `reconcile()`, the production path, not a fixture.

    The both-sides id is the NEGATIVE form: if it surfaces in either difference
    the reader is inventing differences rather than measuring them, which is the
    false-hit failure the false-zero controls cannot see.

    Any failure to build or read the planted repo lands as a NOT FOUND control,
    which classifies the ledger BROKEN and makes the caller refuse. A control
    that could not run is never scored as one that passed.
    """
    spec = CONTROL_FORMS[path]
    head_id = parse_ids(spec["head_only"], RECORDS[path])
    wt_id = parse_ids(spec["worktree_only"], RECORDS[path])
    base_id = parse_ids(spec["base"], RECORDS[path])
    names = {
        "committed": f"an id planted in the committed blob of {path} only, read "
                     f"back with git show, is named IN HEAD NOT IN THE WORKTREE",
        "worktree": f"a different id planted in the working copy of {path} only "
                    f"is named IN THE WORKTREE NOT IN HEAD",
        "exit": f"the worktree-only plant in {path} drives the exit code to "
                f"UNLANDED WORK, not to PASS",
    }
    planted = {v: False for v in names.values()}
    negative = {f"an id present on BOTH sides of {path} is reported as a "
                f"difference": False}
    # Plant the zero on the plants themselves: an unreadable plant and a reader
    # that cannot see it look identical from the outside, and only one of them
    # is this module failing.
    if not (head_id and wt_id and base_id):
        return {"planted": planted, "negative": negative}

    box = Path(tempfile.mkdtemp(prefix="recrec_"))
    try:
        committed = spec["base"] + spec["head_only"]
        worktree = spec["base"] + spec["worktree_only"]
        repo = _plant_repo(box, path, committed, worktree)
        head_text, why = read_committed(repo, "HEAD", path)
        if head_text is None:
            return {"planted": planted, "negative": negative}
        wt_text = (repo / path).read_text()
        got = reconcile(head_text, wt_text, path,
                        ledger=control_kind.ControlLedger(
                            claim_class="the planted control's own run"))
        planted[names["committed"]] = head_id[0] in got["head_only"]
        planted[names["worktree"]] = wt_id[0] in got["worktree_only"]
        planted[names["exit"]] = got["exit"] == EXIT_FAIL_UNLANDED
        negative[next(iter(negative))] = bool(
            set(base_id) & (set(got["head_only"]) | set(got["worktree_only"])))
    except (RuntimeError, OSError):
        # Left as NOT FOUND -- see the docstring. Refusing is the point.
        pass
    finally:
        shutil.rmtree(box, ignore_errors=True)
    return {"planted": planted, "negative": negative}


def run_controls(path: str, *, deep: bool = True) -> control_kind.ControlLedger:
    """Plant the record's OWN entry vocabulary and prove the pattern finds it.

    RECOGNITION, not reachability, and for the docket module's reason: a PASS
    here is a ZERO -- an empty symmetric difference. A pattern blind to one
    entry FORM drops that entry from both sides, the difference cancels, and the
    check reports PASS on a file it cannot read. Proving it can open both files
    would not touch that. The negative forms are shapes that must NOT be read as
    entries: a mid-sentence mention, table furniture for the two ledgers, and
    (for lessons) the two real lines this module declares it cannot see.

    Every form comes from `CONTROL_FORMS[path]` -- this function no longer
    decides a record's vocabulary by testing its name, which is how two ledgers
    came to be graded under NUMERICS shapes.
    """
    pattern = RECORDS[path]
    spec = CONTROL_FORMS[path]
    planted = {f: (want in parse_ids(f, pattern))
               for f, want in spec["forms"].items()}
    ledger = control_kind.ControlLedger(claim_class=f"an id in {path}")
    ledger.plant(f"{Path(path).stem} entry forms",
                 vocabulary=f"{path} entries",
                 planted=planted,
                 negative={n: bool(parse_ids(n, pattern))
                           for n in spec["negatives"]})
    if deep:
        ledger.plant(f"{Path(path).stem} plants read back from disk",
                     vocabulary=f"{path} rows planted on ONE SIDE ONLY",
                     **run_disk_control(path))
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

    if ledger.kind == control_kind.BROKEN:
        # Refuse, never degrade (CLAUDE.md rule 4). Before 2026-08-24 a BROKEN
        # ledger printed ZERO_IS_UNSUPPORTED and the run still returned a
        # reconciliation code, so a reader who trusted the exit status was
        # trusting a reader that had just failed to see its own plant.
        verdict, code = "REFUSED", EXIT_CONTROL_REFUSED
    elif not committed_ids or not worktree_ids:
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
    if result["verdict"] == "REFUSED":
        print("REFUSED: a planted control did not fire, so this reader is not "
              "known to be able to see the ids it would report absent. The id "
              "sets printed above are NOT a reconciliation verdict and must not "
              "be quoted as one (CLAUDE.md rule 3).")
    print(f"VERDICT: {result['verdict']}")
    print("CANNOT SEE: content divergence under a shared id; entries written as "
          "`## L-43, second corollary.` or `### L-63 - CORRECTION` (declared, "
          "not matched); CONTENT THAT MATCHES NO ID PATTERN AT ALL, which is "
          "D369's actual loss and is closed by scripts/append_record.py, not by "
          "this module; whether unlanded work is abandoned or in flight; and "
          "the index, which this check deliberately never consults.")


#: MUTATION HARNESS -- one mutant per record kind, in the style of
#: `check_stamp_vs_commit.py`'s C6. A selftest that cannot be driven non-zero is
#: decoration, and that is exactly what this module had: the NUMERICS forms it
#: planted for the two ledgers could not fail any harder than they already were.
#: Each mutant breaks ONE record's pattern in the way that record is actually at
#: risk of being "tidied", and the site is asserted to occur EXACTLY ONCE before
#: it is applied -- a first-occurrence replace that lands in a docstring mutates
#: prose and lets the mutant pass, which is a stale harness reporting on itself.
MUTANTS = [
    ("LESSONS: the literal period dropped, so `## L-9001.` stops matching",
     "append_record.py",
     '    "docs/LESSONS.md": r"^## (L-\\d+)\\.",',
     '    "docs/LESSONS.md": r"^## (L-\\d+)!",'),
    ("NUMERICS: the bold entry form dropped, so half the file goes unseen",
     "append_record.py",
     '    "docs/NUMERICS_KNOWLEDGE.md": r"^(?:\\*\\*|## )(N-[A-Z]+\\d+)\\.",',
     '    "docs/NUMERICS_KNOWLEDGE.md": r"^(?:## )(N-[A-Z]+\\d+)\\.",'),
    ("DOCKET: the bold/strike wrapper tidied away, so `| **G9002** |` is lost",
     "append_record.py",
     '    "docs/DOCKET.md": r"^\\|\\s*(?:\\*\\*|~~)*\\s*([A-G]\\d+[a-z]?)\\s*(?:~~|\\*\\*)*\\s*\\|",',
     '    "docs/DOCKET.md": r"^\\|\\s*([A-G]\\d+[a-z]?)\\s*\\|",'),
    ("COST_CALIBRATION: the id's hyphen tidied away -- the trap named in the "
     "pattern's own comment; it then parses nothing at all",
     "append_record.py",
     '    "docs/COST_CALIBRATION.md": r"^\\|\\s*(?:\\*\\*|~~)*\\s*(C-\\d+)\\s*(?:~~|\\*\\*)*\\s*\\|",',
     '    "docs/COST_CALIBRATION.md": r"^\\|\\s*(?:\\*\\*|~~)*\\s*(C\\d+)\\s*(?:~~|\\*\\*)*\\s*\\|",'),
    # Not a pattern mutant: the fall-through that WAS the 2026-08-24 defect.
    # Give one record another record's forms and the selftest must go non-zero.
    # ANCHORED BY THE PRECEDING LINE, and the harness proved why on its first
    # run: the bare form line occurs TWICE in this file, once in CONTROL_FORMS
    # and once here, so a first-occurrence replace mutated this list instead of
    # the table and the mutant passed. The `\n` below is an escape sequence in
    # THIS source, so the two-line target it builds occurs only in the table.
    ("the 2026-08-24 defect itself: COST_CALIBRATION handed NUMERICS forms",
     "check_record_reconciliation.py",
     '        "forms": {\n            "| C-9001 | 2026-08-24 | verification | a cost row |": "C-9001",',
     '        "forms": {\n            "**N-B9001. a bold entry**": "N-B9001",'),
]


def selftest(run_mutation: bool = True) -> int:
    """Every registered record's controls, then the mutants that must break them.

    Exit 0 only if every control in every record fired and every mutant drove a
    fresh selftest non-zero.
    """
    here = Path(__file__).resolve().parent
    failures: list[str] = []
    print("=" * 78)
    print("check_record_reconciliation.py -- PLANTED CONTROL SELF-TEST")
    print("=" * 78)
    print(f"  records under control : {len(CONTROL_FORMS)} "
          f"({', '.join(sorted(CONTROL_FORMS))})")
    print(f"  pattern table         : append_record.RECORDS, imported "
          f"(one table, CLAUDE.md rule 14)")
    for path in sorted(CONTROL_FORMS):
        ledger = run_controls(path)
        print("=" * 78)
        print(f"RECORD: {path}")
        print(f"  id pattern       : {RECORDS[path]}")
        print(ledger.render(0))
        if ledger.kind != control_kind.RECOGNITION:
            failures.append(f"{path}: CONTROL KIND is {ledger.kind}, not "
                            f"RECOGNITION")
        for control in ledger.controls:
            kind, why = control.classify()
            if kind != control_kind.RECOGNITION:
                failures.append(f"{path}: control {control.name!r} is {kind} "
                                f"-- {why}")

    n_mutants = 0
    if run_mutation:
        print("=" * 78)
        print("MUTATION HARNESS -- each mutant MUST drive this selftest non-zero")
        print("=" * 78)
        for name, target, old, new in MUTANTS:
            n_mutants += 1
            box = Path(tempfile.mkdtemp(prefix="recrecmut_"))
            try:
                for f in ("check_record_reconciliation.py", "append_record.py",
                          "control_kind.py"):
                    shutil.copy(here / f, box / f)
                src = (box / target).read_text()
                n_sites = src.count(old)
                if n_sites != 1:
                    failures.append(f"mutant {name!r}: site occurs {n_sites} "
                                    f"times in {target}, not once -- the harness "
                                    f"is stale, not the code")
                    print(f"  FAIL  {name}\n        site occurs {n_sites} times, "
                          f"not once")
                    continue
                (box / target).write_text(src.replace(old, new, 1))
                shutil.rmtree(box / "__pycache__", ignore_errors=True)
                done = subprocess.run(
                    [sys.executable, "-B",
                     str(box / "check_record_reconciliation.py"),
                     "--selftest", "--no-mutation"],
                    capture_output=True, text=True)
                ok = done.returncode != 0
                if not ok:
                    failures.append(f"mutant {name!r} did NOT drive the selftest "
                                    f"non-zero (exit 0)")
                print(f"  {'PASS' if ok else 'FAIL'}  {name}\n"
                      f"        mutated {target}, selftest exit {done.returncode}")
            finally:
                shutil.rmtree(box, ignore_errors=True)

    print("-" * 78)
    print(f"  {len(CONTROL_FORMS)} records x 2 controls each = "
          f"{2 * len(CONTROL_FORMS)} controls; {n_mutants} mutants; "
          f"{len(failures)} failure(s)")
    for line in failures:
        print(f"    FAILURE: {line}")
    print("-" * 78)
    print(f"VERDICT: {'PASS' if not failures else 'FAIL'}")
    print("CANNOT SEE: whether the planted forms are the RIGHT forms for a "
          "record whose shape changes tomorrow; content divergence under a "
          "shared id; and anything about the four ledgers' real contents -- "
          "this selftest runs entirely on planted temp repos.")
    return EXIT_PASS if not failures else EXIT_CONTROL_REFUSED


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--path", action="append", dest="paths",
                    help="record to check; repeatable (default: lessons and "
                         "numerics)")
    ap.add_argument("--rev", default=DEFAULT_REV)
    ap.add_argument("--repo", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true",
                    help="run every record's planted controls plus the mutation "
                         "harness, and exit")
    ap.add_argument("--no-mutation", action="store_true",
                    help="selftest without the mutation harness (used BY it)")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest(run_mutation=not args.no_mutation)

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
                 EXIT_UNKNOWN: 4, EXIT_CONTROL_REFUSED: 5}
        if order[result["exit"]] > order[worst]:
            worst = result["exit"]
    if args.json:
        print(json.dumps(blobs, indent=1))
    return worst


if __name__ == "__main__":
    sys.exit(main())
