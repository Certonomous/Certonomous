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
        # Re-aimed 2026-08-18. This anchored on the key followed immediately by
        # the closing brace; the returned dict later grew keys after it, the
        # literal stopped occurring, and the mutation went unapplied for as long
        # as it took someone to notice the harness was scoring it a survivor.
        # Anchored on the single line now, which survives the dict growing.
        '        "id_pattern": ID_PATTERN,',
        '        "id_pattern": "",',
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
    (
        "M11-duplicate-check-disabled",
        "the duplicate-id branch stops firing, so two rows wearing one id read "
        "as reconciled -- the exact state two lanes reached on 2026-08-18, when "
        "both wrote a row numbered D406 and this check returned PASS. Every "
        "later citation of a duplicated id is ambiguous, and the docket is "
        "append-only, so the ambiguity never expires.",
        "    elif committed_dupes or worktree_dupes:",
        "    elif False:",
        (
            "test_a_duplicate_id_in_the_worktree_is_a_fail",
            "test_a_duplicate_id_already_committed_is_a_fail",
            "test_a_duplicate_is_not_reported_as_unlanded_work",
        ),
    ),
    (
        "M12-tool-allocated-ids-unseen",
        "the reader reverts to the LEGACY pattern alone, which is what this "
        "module held before Sanaa's PLUMBING FREEZE directive of 2026-08-31 was "
        "built. `append_record.py --allocate-id` mints "
        "`| D-20260831T154707.481920Z-a3f91c4d |`, and `[A-G]\\d` cannot match "
        "it -- a hyphen stands where a digit must be. Every tool-allocated row "
        "then goes unseen IN BOTH DIRECTIONS, so the differences cancel and a "
        "docket carrying unlanded work reads PASS. This is the dead-lever "
        "mutant: if it survives, ids are being written that nothing reads.",
        "    return [m.group(1) if m.group(1) is not None else m.group(2)\n"
        "            for m in _COMBINED_ID_RE.finditer(text)]",
        "    return re.compile(ID_PATTERN, re.M).findall(text)",
        (
            "test_a_tool_allocated_row_is_parsed_as_a_row",
            "test_a_tool_allocated_row_only_in_the_worktree_is_unlanded_work",
            "test_a_tool_allocated_row_only_in_head_is_writeback_owed",
            "test_legacy_and_tool_rows_reconcile_together",
        ),
    ),
    (
        "M13-tool-pattern-unanchored",
        "the tool-id reader is taken from the UNANCHORED helper instead of the "
        "entry-position anchor, so a tool id is recognised anywhere on a line. "
        "`allocate_into_rows` fills EVERY placeholder on a line by design, so a "
        "row citing its own id is then counted twice and this module returns "
        "FAIL-DUPLICATE on a correct docket; a mid-sentence mention becomes a "
        "row as well. The anchor is the property, not a detail of spelling.\n"
        "        THE IDENTITY ASSERT IS MUTATED WITH IT, DELIBERATELY, and the "
        "first spelling of this mutant is why: swapping the pattern alone "
        "tripped that assert at IMPORT, so the suite reported one module-level "
        "ERROR named `sdk.tests.test_docket_reconciliation` and NOT ONE of the "
        "aimed method names -- the harness scored SURVIVED against a defect it "
        "had in fact prevented outright. A mutant that CRASHES the subject "
        "proves nothing about the tests; it has to INJECT the defect and leave "
        "the module importable. Measured 2026-08-31: 13 killed / 1 survived / "
        "0 new failures on the aimed set, which is the crash signature, not a "
        "weak-test signature.",
        "TOOL_ID_PATTERN = append_record.ANCHORED_TOOL_ID[DEFAULT_PATH]\n"
        "assert TOOL_ID_PATTERN is append_record.ANCHORED_TOOL_ID[DEFAULT_PATH], (",
        "TOOL_ID_PATTERN = append_record.tool_id_pattern(DEFAULT_PATH)\n"
        "assert isinstance(TOOL_ID_PATTERN, str), (",
        (
            "test_a_row_citing_its_own_id_in_its_own_cell_is_ONE_row",
            "test_a_tool_id_mentioned_in_prose_is_not_a_row",
            "test_the_tool_pattern_is_the_minting_modules_own_object",
        ),
    ),
    (
        "M14-tool-pattern-not-published",
        "the tool-id pattern stops being reported, so a reader inherits a "
        "verdict over TWO id spaces while being shown only one of them -- the "
        "M8 defect, in the space M8 did not know about.",
        '        "tool_id_pattern": TOOL_ID_PATTERN,\n'
        '        "n_tool_committed": sum(1 for i in committed_ids',
        '        "tool_id_pattern": "",\n'
        '        "n_tool_committed": sum(1 for i in committed_ids',
        ("test_the_tool_pattern_is_printed_in_both_output_modes",),
    ),
    (
        "M15-unreachable-append-record-degrades-silently",
        "the REFUSAL that fires when `append_record` cannot be imported becomes "
        "a silent fallback to a tool-id pattern that matches nothing. The "
        "module then loads, prints a verdict, and is blind to every "
        "tool-allocated row -- and it is blind EXACTLY in the configuration "
        "where the coupling has broken, which is the worst moment to go quiet. "
        "This is the fail-open shape in its purest form: not a wrong answer, a "
        "confident one produced by a reader that stopped being able to see.",
        "    raise SystemExit(\n"
        '        "REFUSED: scripts/check_docket_reconciliation.py cannot import "',
        "    import types\n"
        "    return types.SimpleNamespace(\n"
        '        ANCHORED_TOOL_ID={"docs/DOCKET.md": r"(?!)"},\n'
        "        is_tool_id=lambda row_id: False)\n"
        "    raise SystemExit(\n"
        '        "REFUSED: scripts/check_docket_reconciliation.py cannot import "',
        ("test_an_unreachable_append_record_REFUSES_and_never_falls_back",),
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

        # NOT-APPLIED IS NOT SURVIVED, and conflating them is how a mutation
        # harness rots silently. 2026-08-18: M8's anchor
        # (`"id_pattern": ID_PATTERN,` immediately followed by the closing brace)
        # had stopped existing -- the returned dict grew keys after it -- so the
        # mutation was NEVER APPLIED, and the harness reported it as a SURVIVOR.
        # "No test caught this defect" and "this defect was never injected" are
        # opposite facts and were printed with the same word.
        #
        # The same day, M2's anchor went the other way: a copy of its literal was
        # inserted ABOVE it, so the mutation WAS applied, to the wrong line, on a
        # branch no test exercised. Coverage fell 9 killed to 8 and the harness
        # still exited 1, so nothing in the exit code moved.
        #
        # Between them those two are the whole failure mode: a mutation anchored
        # to a source literal silently retargets or silently vanishes as the
        # subject evolves, and a harness that reports only killed/survived cannot
        # tell you which happened. NOT_APPLIED is now its own bucket and is a
        # HARNESS failure, not a subject failure -- the subject may be perfectly
        # tested; it is the proof that has decayed.
        killed, survived, not_applied = [], [], []
        for name, why, old, new, aimed in MUTANTS:
            if old not in original:
                print(f"{name}: ANCHOR NOT FOUND -- mutation could not be applied")
                not_applied.append((name, "anchor missing -- the literal this mutation aims at no longer occurs in the subject"))
                continue
            mutated = original.replace(old, new, 1)
            if mutated == original:
                print(f"{name}: NO-OP mutation")
                not_applied.append((name, "no-op -- the substitution changed nothing"))
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

        print(f"\n{len(killed)} killed, {len(survived)} survived, "
              f"{len(not_applied)} NOT APPLIED, {len(MUTANTS)} total")
        for name, detail in survived:
            print(f"  SURVIVOR {name}: {detail}")
        for name, detail in not_applied:
            print(f"  NOT APPLIED {name}: {detail}")
        if not_applied:
            print("\n  A mutation that was never applied proves NOTHING about the")
            print("  subject. These are defects in this harness, not in the code it")
            print("  grades: re-aim each anchor at the line it was written for, and")
            print("  do not read the killed count as coverage until they are aimed.")
        return 0 if not (survived or not_applied) else 1
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
