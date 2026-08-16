#!/usr/bin/env python3
"""Mutation proof for `scripts/hunk_check.py`'s index-freedom repair.

WHY IT IS TRACKED. A mutation result quoted in a commit message cannot be
re-run by the next reader. This one can.

WHAT IT PROVES AND WHAT IT DOES NOT. It shows each assertion CAN fail, never
that it asserts the right thing. The stronger evidence for this repair is
recorded separately and is not a mutation at all: the new suite was run against
the PRISTINE (pre-repair) subject and 12 of its tests reddened, so it catches
the historical defect rather than merely exercising the new code.

HOW IT IS JUDGED. The control runs FIRST over both suites and must be GREEN. A
mutant is killed only when a test IT NAMED is in the NEW-FAILURE set --
failure-count delta against that green control. `returncode != 0` is never used
as the kill criterion: against a red control it scores every survivor a kill.

THE resolve() TRAP, which fired on the sibling harness earlier tonight and is
guarded here. Both test modules locate their subject with
`Path(__file__).resolve().parents[2]`, and `resolve()` FOLLOWS SYMLINKS. A
mirror made of symlinks therefore resolves back to the real repository and the
suite loads the real, unmutated subject: the signature is every mutant
surviving with ZERO new failures. So `scripts/` and `sdk/tests/` are REAL
directories here with the subject and both test files REAL copies.

`__pycache__` is purged before every cell in both trees --
`PYTHONDONTWRITEBYTECODE` does not fix stale bytecode here and has inverted
results in this lab. No tracked file is ever held mutated; the subject's sha256
is asserted unchanged in a `finally`.

Run:  python3 scripts/mutation_harness_hunk_check.py
      python3 scripts/mutation_harness_hunk_check.py --list
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
TARGET = "scripts/hunk_check.py"
TEST_MODULES = (
    "sdk.tests.test_hunk_check_is_index_free",
    "sdk.tests.test_hunk_check",
)

MUTANTS: list[tuple[str, str, str, str, tuple[str, ...]]] = [
    (
        "M1-restore-the-index-walk",
        "THE ORIGINAL DEFECT. The worktree mode goes back to `git diff HEAD`, "
        "which walks the index, so any path with no index entry reads as a "
        "whole-file deletion -- the state this lab's private-index protocol "
        "creates for every new file it lands.",
        '    actual = worktree_numstat(root, "HEAD", declared)',
        '    actual = parse_numstat(_git(root, "diff", "--numstat",\n'
        '        "--no-renames", "HEAD", "--", *sorted(declared)).stdout)',
        (
            "test_one_removed_line_grades_as_one_removed_line",
            "test_one_added_line_grades_as_one_added_line",
            "test_the_end_to_end_declaration_passes_for_the_true_numbers",
            "test_an_untracked_new_file_is_all_additions",
        ),
    ),
    (
        "M2-added-and-removed-swapped",
        "the two numbers are exchanged. Every COUNT of findings survives this, "
        "which is why the assertions name the pair.",
        '        return (None if a == "-" else int(a), None if r == "-" else int(r))',
        '        return (None if r == "-" else int(r), None if a == "-" else int(a))',
        (
            "test_one_removed_line_grades_as_one_removed_line",
            "test_one_added_line_grades_as_one_added_line",
        ),
    ),
    (
        "M3-new-file-is-not-first-class",
        "a path absent from the rev stops being reported as wholly added, so a "
        "declared new file reads as 'nothing changed' and is never graded.",
        "        if not in_rev:\n"
        '            with open(disk, "rb") as fh:\n'
        "                actual[path] = (_count_lines(fh.read()), 0)\n"
        "            continue",
        "        if not in_rev:\n"
        "            continue",
        (
            "test_an_untracked_new_file_is_all_additions",
            "test_a_new_file_with_no_trailing_newline_counts_its_last_line",
        ),
    ),
    (
        "M4-missing-final-line-dropped",
        "a file whose last line has no trailing newline loses that line, so "
        "the declaration is off by one for every such file.",
        r'    return data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)',
        r'    return data.count(b"\n")',
        ("test_a_new_file_with_no_trailing_newline_counts_its_last_line",),
    ),
    (
        "M5-deletion-not-counted",
        "a file in the rev and gone from disk reports no removals, so deleting "
        "a file entirely passes an undeclared-deletion through the gate.",
        "        if not on_disk:\n"
        "            actual[path] = (0, _count_lines(blob.stdout))\n"
        "            continue",
        "        if not on_disk:\n"
        "            continue",
        ("test_a_file_in_head_and_deleted_from_disk_is_all_removals",),
    ),
    (
        "M6-no-entry-called-staged",
        "a path with no index entry is reported as a peer's STAGED edit, "
        "sending the reader hunting for an agent who never touched the file -- "
        "and burying the real by-product of the commit protocol.",
        "        (missing if path not in tracked else staged).add(path)",
        "        staged.add(path)",
        ("test_no_index_entry_is_reported_as_such_and_not_as_a_peers_staged_edit",),
    ),
    (
        "M7-unchanged-file-graded",
        "an unchanged file is graded 0+/0- instead of staying absent, which "
        "turns the B1 clause -- nothing changed at the declared path is "
        "UNKNOWN -- into a FAIL. This regression was made and caught for real "
        "during the repair, by running the pre-existing suite.",
        "        if delta == (0, 0):\n            continue",
        "        if False:\n            continue",
        (
            "test_an_unchanged_file_is_absent_and_is_never_reported_as_a_deletion",
            "test_an_unchanged_file_declared_as_changed_is_UNKNOWN_not_a_deletion",
            "test_nothing_changed_at_the_declared_path_is_UNKNOWN_and_not_PASS",
        ),
    ),
    (
        "M8-gate-turned-off",
        "a wrong declaration stops being a finding, which is the whole gate.",
        "            elif want[i] != got[i]:",
        "            elif False:",
        (
            "test_a_wrong_declaration_still_fails_on_the_failing_case",
        ),
    ),
    (
        "M9-at-mode-reads-the-worktree",
        "`--at` stops grading the commit object and grades the worktree "
        "instead, so a post-hoc audit of a landed commit silently becomes a "
        "reading of whatever is on disk now.",
        '        cp = _git(root, "show", "--numstat", "--no-renames", "--format=", rev)\n'
        '        return parse_numstat(cp.stdout), (set(), set()), f"commit {rev}"',
        '        return worktree_numstat(root, "HEAD", declared), (set(), set()), f"commit {rev}"',
        ("test_at_mode_grades_the_commit_object_and_ignores_the_shared_index",),
    ),
]


def purge_pycache(root: Path) -> None:
    for cache in root.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)


def _real_dir(mirror: Path, rel: str) -> Path:
    target = mirror / rel
    if target.is_symlink():
        target.unlink()
    target.mkdir(parents=True, exist_ok=True)
    for entry in (REPO / rel).iterdir():
        link = target / entry.name
        if not link.exists() and not link.is_symlink():
            link.symlink_to(entry)
    return target


def build_mirror(tmp: Path, mutated: str) -> Path:
    """Real copies where `resolve()` would otherwise escape the mirror."""
    mirror = tmp / "mirror"
    mirror.mkdir()
    for entry in REPO.iterdir():
        if entry.name == ".git":
            continue
        (mirror / entry.name).symlink_to(entry)
    scripts = _real_dir(mirror, "scripts")
    (scripts / Path(TARGET).name).unlink()
    (scripts / Path(TARGET).name).write_text(mutated)
    _real_dir(mirror, "sdk")
    tests = _real_dir(mirror, "sdk/tests")
    for module in TEST_MODULES:
        rel = module.replace(".", "/") + ".py"
        (tests / Path(rel).name).unlink()
        (tests / Path(rel).name).write_text((REPO / rel).read_text())
    return mirror


def run_tests(cwd: Path) -> tuple[int, set[str]]:
    purge_pycache(REPO)
    purge_pycache(cwd)
    failing: set[str] = set()
    worst = 0
    for module in TEST_MODULES:
        done = subprocess.run(
            [sys.executable, "-m", "unittest", module, "-v"],
            cwd=str(cwd), capture_output=True, text=True,
            env={**os.environ, "PYTHONPATH": str(cwd)},
        )
        worst = worst or done.returncode
        for line in done.stderr.splitlines():
            if line.startswith(("FAIL: ", "ERROR: ")):
                failing.add(line.split(": ", 1)[1].split(" ")[0])
    return worst, failing


def main() -> int:
    parser = argparse.ArgumentParser(description="Mutation proof for hunk_check.")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    if args.list:
        for name, why, _, _, aimed in MUTANTS:
            print(f"{name}\n    reintroduces: {why}\n    aimed at: {', '.join(aimed)}\n")
        return 0

    path = REPO / TARGET
    original = path.read_text()
    before = hashlib.sha256(path.read_bytes()).hexdigest()

    try:
        print("CONTROL (must be GREEN before any mutant is scored)")
        code, control = run_tests(REPO)
        if code != 0 or control:
            print(f"  CONTROL RED: rc={code} failures={sorted(control)}")
            return 1
        print("  control GREEN, 0 failures\n")

        killed, survived = [], []
        for name, why, old, new, aimed in MUTANTS:
            if old not in original:
                print(f"{name}: ANCHOR NOT FOUND")
                survived.append((name, "anchor missing"))
                continue
            mutated = original.replace(old, new, 1)
            with tempfile.TemporaryDirectory() as tmp:
                mirror = build_mirror(Path(tmp), mutated)
                _, failures = run_tests(mirror)
            hit = sorted(set(aimed) & (failures - control))
            if hit:
                killed.append(name)
                print(f"{name}: KILLED by {', '.join(hit)}")
            else:
                survived.append((name, f"new failures {sorted(failures - control)}"))
                print(f"{name}: SURVIVED -- {sorted(failures - control)}")

        print(f"\n{len(killed)} killed, {len(survived)} survived, {len(MUTANTS)} total")
        for name, detail in survived:
            print(f"  SURVIVOR {name}: {detail}")
        return 0 if not survived else 1
    finally:
        after = hashlib.sha256(path.read_bytes()).hexdigest()
        if after != before:  # pragma: no cover
            path.write_text(original)
            print("SUBJECT WAS MODIFIED AND HAS BEEN RESTORED -- investigate")
        else:
            print(f"subject sha256 unchanged: {before[:16]}")
        purge_pycache(REPO)


if __name__ == "__main__":
    sys.exit(main())
