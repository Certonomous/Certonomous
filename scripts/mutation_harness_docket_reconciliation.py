#!/usr/bin/env python3
"""Mutation proof for `scripts/check_docket_reconciliation.py`.

WHY THIS FILE IS TRACKED. A mutation result quoted in a commit message expires
the moment it is made: the next reader cannot re-run it. `docs/AGENT_ATTRIBUTION`
carried "12 mutants, all killed" with no harness anywhere in the tree, and D173
measured that. So the proof is a file a later reader can RUN.

WHAT A MUTATION PROOF IS AND IS NOT. It shows a test detects A change, never
that it detects the RIGHT change. Two ways that has failed in this lab, both
guarded against here: a guard written by reading an already-mutated file
asserted the mutant and passed its own proof; and a probe survived an inverted
comparison because it asserted a COUNT rather than an IDENTITY. Every mutant
below names the DEFECT it reintroduces, and every aimed test asserts on which
IDs went in which direction.

HOW IT IS JUDGED. The control runs FIRST over the whole aimed set and must be
GREEN. A mutant is scored killed only when a test IT NAMED is in the
NEW-FAILURE set -- the failure-count delta against that green control.
`killed = returncode != 0` is never used: against a red control it scores every
survivor a kill, which is exactly how a clean bill of health gets manufactured.

THE MUTANT NEVER TOUCHES THE WORKING TREE. Agents share this checkout. Each cell
builds a MIRROR -- a temp root of symlinks back to the repository with the one
mutated file a real copy -- so no tracked file is ever held mutated. The
subject's sha256 is asserted unchanged at the end, in a `finally`.
`__pycache__` is purged before every cell in BOTH trees: `PYTHONDONTWRITEBYTECODE`
does NOT fix stale bytecode here and has inverted results in this lab.

Run:  python3 scripts/mutation_harness_docket_reconciliation.py
      python3 scripts/mutation_harness_docket_reconciliation.py --list
Exit: 0 when the control is green AND every mutant reddened a test it aimed at.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TARGET = "scripts/check_docket_reconciliation.py"
TEST_MODULE = "sdk.tests.test_docket_reconciliation"

# Each mutant: (name, defect it reintroduces, old, new, tests it must redden)
MUTANTS: list[tuple[str, str, str, str, tuple[str, ...]]] = [
    (
        "M1-directions-swapped",
        "the two directions are exchanged, so a landed row reads as unlanded "
        "and the check tells an agent to land a row that is already committed "
        "-- and, worse, calls genuinely unlanded work safe. Every count is "
        "preserved by this mutation, which is why the tests assert identity.",
        '    head_only = sorted(committed_set - worktree_set, key=sort_key)\n'
        '    worktree_only = sorted(worktree_set - committed_set, key=sort_key)',
        '    head_only = sorted(worktree_set - committed_set, key=sort_key)\n'
        '    worktree_only = sorted(committed_set - worktree_set, key=sort_key)',
        (
            "test_a_row_in_head_and_not_the_worktree_is_named_in_the_head_only_direction",
            "test_a_row_only_in_the_worktree_is_named_in_the_worktree_only_direction",
            "test_the_two_directions_are_not_interchangeable",
        ),
    ),
    (
        "M2-unlanded-downgraded",
        "unlanded work is reported with the write-back exit code, losing the "
        "distinction between a row that is safe in a commit and a row that "
        "exists nowhere but one working tree.",
        '        verdict, code = "FAIL", EXIT_FAIL_UNLANDED',
        '        verdict, code = "FAIL", EXIT_FAIL_WRITEBACK_OWED',
        (
            "test_a_row_only_in_the_worktree_is_named_in_the_worktree_only_direction",
            "test_unlanded_work_outranks_writeback_owed_when_both_are_present",
            "test_the_two_directions_are_not_interchangeable",
        ),
    ),
    (
        "M3-empty-side-passes",
        "a side that parses to zero ids reads PASS instead of UNKNOWN, so a "
        "shape change in the file or the pattern is indistinguishable from "
        "agreement -- the fail-open shape this lab keeps rediscovering.",
        "    if not committed_ids or not worktree_ids:\n"
        '        verdict, code = "UNKNOWN", EXIT_UNKNOWN',
        "    if False:\n"
        '        verdict, code = "UNKNOWN", EXIT_UNKNOWN',
        (
            "test_a_side_that_parses_to_zero_ids_is_unknown_not_pass",
            "test_zero_ids_on_one_side_only_is_unknown_rather_than_a_huge_divergence",
        ),
    ),
    (
        "M4-note-rows-become-ids",
        "the cell anchor is dropped, so `| D19-D20 note |` yields the id `D19` "
        "and the check invents rows that duplicate real ones. This is the "
        "widely-copied recipe's actual defect.",
        r'ID_PATTERN = r"^\|\s*(?:\*\*|~~)*\s*([A-G]\d+[a-z]?)\s*(?:~~|\*\*)*\s*\|"',
        r'ID_PATTERN = r"^\|\s*(?:\*\*|~~)*\s*([A-G]\d+[a-z]?)"',
        ("test_a_note_row_is_not_an_id",),
    ),
    (
        "M5-decoration-blind",
        "bold and struck ids stop being recognised, so a struck row present on "
        "one side only reads as reconciled -- silence in the direction the "
        "docket's own strike-and-keep rule guarantees will occur.",
        r'ID_PATTERN = r"^\|\s*(?:\*\*|~~)*\s*([A-G]\d+[a-z]?)\s*(?:~~|\*\*)*\s*\|"',
        r'ID_PATTERN = r"^\|\s*([A-G]\d+[a-z]?)\s*\|"',
        (
            "test_bold_and_struck_ids_are_recognised",
            "test_a_struck_row_present_on_one_side_only_is_still_a_divergence",
        ),
    ),
    (
        "M6-d-section-only",
        "only `D` rows are scanned, so an A/B/C/E/F/G row that diverges is "
        "invisible. The docket has seven lettered sections and the write-back "
        "gap is indifferent to which one a row is in.",
        r'([A-G]\d+[a-z]?)',
        r'(D\d+[a-z]?)',
        ("test_every_lettered_section_is_in_scope",),
    ),
    (
        "M7-lexical-sort",
        "ids are ordered lexically, so `D99` is reported after `D146`. Section "
        "11 of the guide records that exact defect being run as written and "
        "allocating an id that had been taken weeks earlier.",
        "    return (match.group(1), int(match.group(2)), match.group(3))",
        "    return (match.group(1), match.group(2), match.group(3))",
        ("test_ids_are_ordered_numerically_not_lexically",),
    ),
    (
        "M8-pattern-not-published",
        "the pattern stops being reported, so a reader inherits a divergence "
        "verdict with no way to reproduce which rows it counted -- the defect "
        "that produced three different, all-defensible row totals for one "
        "commit on 2026-08-16.",
        '        "id_pattern": ID_PATTERN,\n    }',
        '        "id_pattern": "",\n    }',
        ("test_the_pattern_is_printed_in_both_output_modes",),
    ),
    (
        "M9-unreadable-side-passes",
        "an unreadable commit side returns PASS instead of UNKNOWN, so a "
        "broken git invocation clears the docket.",
        "def _unknown(args: argparse.Namespace, why: str, repo: Path) -> int:",
        "def _unknown(args: argparse.Namespace, why: str, repo: Path) -> int:\n"
        "    return EXIT_PASS  # MUTANT",
        (
            "test_an_unreadable_commit_side_is_unknown_not_pass",
            "test_a_missing_worktree_file_is_unknown_not_pass",
        ),
    ),
    (
        "M10-order-decides",
        "the comparison becomes order-sensitive, so a docket whose rows were "
        "reordered but not changed reads as a total divergence and the real "
        "signal is buried in noise.",
        "    committed_set = set(committed_ids)\n    worktree_set = set(worktree_ids)",
        "    committed_set = list(committed_ids)\n    worktree_set = list(worktree_ids)",
        ("test_equal_sets_pass_even_when_the_row_order_differs",),
    ),
]


def purge_pycache(root: Path) -> None:
    for cache in root.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)


def _real_dir(mirror: Path, rel: str) -> Path:
    """Make *rel* a REAL directory in the mirror, its entries symlinked.

    Any directory on the path from the mirror root down to a file that must be
    a real copy has to be a real directory itself, or `Path.resolve()` inside
    the test escapes the mirror and lands back on the repository.
    """
    target = mirror / rel
    if target.is_symlink():
        target.unlink()
    target.mkdir(parents=True, exist_ok=True)
    for entry in (REPO / rel).iterdir():
        link = target / entry.name
        if not link.exists() and not link.is_symlink():
            link.symlink_to(entry)
    return target


def build_mirror(tmp: Path, mutated_source: str) -> Path:
    """A symlink mirror of the repo with the mutated file a REAL copy.

    THE TRAP THIS EXISTS TO AVOID, and it fired here on the first run. The test
    module locates its subject with `Path(__file__).resolve().parents[2]`.
    `resolve()` follows symlinks, so when the test file is a symlink into the
    repository it resolves to the REPOSITORY path and the suite loads the real,
    unmutated script no matter what the mirror contains. The first run of this
    harness scored 0 killed and 10 survived with ZERO new failures on any
    mutant -- the signature of a subject that was never substituted, not of ten
    weak tests. So both the script and the test file are real copies here, and
    every directory above them is a real directory.
    """
    mirror = tmp / "mirror"
    mirror.mkdir()
    for entry in REPO.iterdir():
        if entry.name == ".git":
            continue
        (mirror / entry.name).symlink_to(entry)

    scripts = _real_dir(mirror, "scripts")
    (scripts / Path(TARGET).name).unlink()
    (scripts / Path(TARGET).name).write_text(mutated_source)

    _real_dir(mirror, "sdk")
    tests = _real_dir(mirror, "sdk/tests")
    test_rel = TEST_MODULE.replace(".", "/") + ".py"
    (tests / Path(test_rel).name).unlink()
    (tests / Path(test_rel).name).write_text((REPO / test_rel).read_text())
    return mirror


def run_tests(cwd: Path) -> tuple[int, set[str]]:
    """Run the aimed suite; return (returncode, set of failing test names)."""
    purge_pycache(REPO)
    purge_pycache(cwd)
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", TEST_MODULE, "-v"],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": str(cwd)},
    )
    failing: set[str] = set()
    for line in completed.stderr.splitlines():
        if line.startswith(("FAIL: ", "ERROR: ")):
            failing.add(line.split(": ", 1)[1].split(" ")[0])
    return completed.returncode, failing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="list mutants and exit")
    args = parser.parse_args()

    if args.list:
        for name, why, _, _, aimed in MUTANTS:
            print(f"{name}\n    reintroduces: {why}\n    aimed at: {', '.join(aimed)}\n")
        return 0

    target_path = REPO / TARGET
    original = target_path.read_text()
    before = hashlib.sha256(target_path.read_bytes()).hexdigest()

    try:
        print("CONTROL (must be GREEN before any mutant is scored)")
        code, control_failures = run_tests(REPO)
        if code != 0 or control_failures:
            print(f"  CONTROL RED: rc={code} failures={sorted(control_failures)}")
            print("  Refusing to score mutants against a red control.")
            return 1
        print("  control GREEN, 0 failures\n")

        killed, survived = [], []
        for name, why, old, new, aimed in MUTANTS:
            if old not in original:
                print(f"{name}: ANCHOR NOT FOUND -- mutation could not be applied")
                survived.append((name, "anchor missing"))
                continue
            mutated = original.replace(old, new, 1)
            if mutated == original:
                print(f"{name}: NO-OP mutation")
                survived.append((name, "no-op"))
                continue
            with tempfile.TemporaryDirectory() as tmp:
                mirror = build_mirror(Path(tmp), mutated)
                _, failures = run_tests(mirror)
            new_failures = failures - control_failures
            hit = sorted(set(aimed) & new_failures)
            if hit:
                killed.append(name)
                print(f"{name}: KILLED by {', '.join(hit)}")
            else:
                survived.append((name, f"new failures: {sorted(new_failures)}"))
                print(f"{name}: SURVIVED -- aimed at {aimed}, new failures {sorted(new_failures)}")

        print(f"\n{len(killed)} killed, {len(survived)} survived, {len(MUTANTS)} total")
        for name, detail in survived:
            print(f"  SURVIVOR {name}: {detail}")
        return 0 if not survived else 1
    finally:
        after = hashlib.sha256(target_path.read_bytes()).hexdigest()
        if after != before:  # pragma: no cover - the guard that must never fire
            target_path.write_text(original)
            print("SUBJECT WAS MODIFIED AND HAS BEEN RESTORED -- investigate")
            return 1
        print(f"subject sha256 unchanged: {before[:16]}")
        purge_pycache(REPO)


if __name__ == "__main__":
    sys.exit(main())
