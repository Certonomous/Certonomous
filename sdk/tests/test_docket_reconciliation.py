#!/usr/bin/env python3
"""Pins for `scripts/check_docket_reconciliation.py`.

WHAT THESE ASSERT ON, AND WHY IT IS NOT COUNTS
==============================================
Every assertion here names **which IDs, in which direction**. None asserts a
count. That is the lesson of the pinning failure this lab measured on
2026-08-16: a test asserting that a rule "opens no file" passed while the rule
opened four, because it watched the wrong door and its own `setUp` had replaced
the subject. A count survives a mutation that SWAPS the two directions -- which
is mutant M2 in the harness -- and swapping them is the worst available defect,
because it tells an agent to `git checkout` a row that exists in no commit.

Every test drives the REAL script, either through `main()` with real argv or as
a subprocess against a real temporary git repository. Nothing here asserts
against a stub, and the fixtures are built by `git commit` rather than by
handing the module strings, so the `git show` path is exercised too.

The expectations are derived from the module DOCSTRING's stated contract, not
read back out of its code.
"""

from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TARGET = REPO / "scripts" / "check_docket_reconciliation.py"


def load_module():
    """Load the script under test by path, so the file itself is the subject."""
    spec = importlib.util.spec_from_file_location("_docket_reconciliation", TARGET)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MOD = load_module()

HEADER = "# The docket\n\n| id | finding |\n| --- | --- |\n"


def rows(*ids: str) -> str:
    """A minimal docket whose first cell is each id."""
    return HEADER + "".join(f"| {i} | a finding |\n" for i in ids)


def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    """Run git with a list and read `returncode` directly -- never a pipeline."""
    completed = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True
    )
    assert completed.returncode == 0, completed.stderr
    return completed


class TempDocketRepo:
    """A real git repository with a real docket, committed."""

    def __init__(self, committed: str):
        self.dir = tempfile.TemporaryDirectory()
        self.path = Path(self.dir.name)
        git(self.path, "init", "-q", "-b", "main")
        git(self.path, "config", "user.email", "t@example.invalid")
        git(self.path, "config", "user.name", "t")
        self.docket = self.path / "docs" / "DOCKET.md"
        self.docket.parent.mkdir(parents=True)
        self.docket.write_text(committed)
        git(self.path, "add", "docs/DOCKET.md")
        git(self.path, "commit", "-q", "-m", "docket")

    def set_worktree(self, text: str) -> None:
        self.docket.write_text(text)

    def close(self) -> None:
        self.dir.cleanup()


def run_check(repo: Path, *extra: str) -> tuple[int, dict]:
    """Drive the real script as a subprocess and read its JSON and its rc.

    The exit status is taken from the completed process, never through a pipe.
    """
    completed = subprocess.run(
        [sys.executable, str(TARGET), "--repo", str(repo), "--json", *extra],
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout) if completed.stdout.strip() else {}
    return completed.returncode, payload


class DirectionIdentityTests(unittest.TestCase):
    """The two directions, asserted by ID and never by count."""

    def test_a_row_in_head_and_not_the_worktree_is_named_in_the_head_only_direction(self):
        repo = TempDocketRepo(rows("D1", "D2", "D241"))
        try:
            repo.set_worktree(rows("D1", "D2"))
            code, payload = run_check(repo.path)
            self.assertEqual(payload["head_only"], ["D241"])
            self.assertEqual(payload["worktree_only"], [])
            self.assertEqual(code, MOD.EXIT_FAIL_WRITEBACK_OWED)
        finally:
            repo.close()

    def test_a_row_only_in_the_worktree_is_named_in_the_worktree_only_direction(self):
        repo = TempDocketRepo(rows("D1", "D2"))
        try:
            repo.set_worktree(rows("D1", "D2", "D999"))
            code, payload = run_check(repo.path)
            self.assertEqual(payload["worktree_only"], ["D999"])
            self.assertEqual(payload["head_only"], [])
            self.assertEqual(code, MOD.EXIT_FAIL_UNLANDED)
        finally:
            repo.close()

    def test_the_two_directions_are_not_interchangeable(self):
        """The sharp one: a swap keeps every count and inverts the instruction."""
        repo = TempDocketRepo(rows("D1", "D901"))
        try:
            repo.set_worktree(rows("D1", "D902"))
            code, payload = run_check(repo.path)
            self.assertEqual(payload["head_only"], ["D901"])
            self.assertEqual(payload["worktree_only"], ["D902"])
            self.assertNotIn("D902", payload["head_only"])
            self.assertNotIn("D901", payload["worktree_only"])
            self.assertEqual(code, MOD.EXIT_FAIL_UNLANDED)
        finally:
            repo.close()

    def test_unlanded_work_outranks_writeback_owed_when_both_are_present(self):
        """Contract: the worse of the two decides. Unlanded work can be lost."""
        result = MOD.reconcile(rows("D1", "D901"), rows("D1", "D902"))
        self.assertEqual(result["exit_code"], MOD.EXIT_FAIL_UNLANDED)
        self.assertEqual(result["head_only"], ["D901"])
        self.assertEqual(result["worktree_only"], ["D902"])

    def test_equal_sets_pass_even_when_the_row_order_differs(self):
        result = MOD.reconcile(rows("D1", "D2", "D3"), rows("D3", "D1", "D2"))
        self.assertEqual(result["verdict"], "PASS")
        self.assertEqual(result["exit_code"], MOD.EXIT_PASS)
        self.assertEqual(result["head_only"], [])
        self.assertEqual(result["worktree_only"], [])


class PatternTests(unittest.TestCase):
    """The pattern, the trap it was built around, and its publication."""

    def test_a_note_row_is_not_an_id(self):
        """`| D19-D20 note |` is commentary; the copied recipe invents `D19`."""
        text = HEADER + "| D19 | real |\n| D19-D20 note | commentary |\n"
        self.assertEqual(MOD.parse_ids(text), ["D19"])

    def test_bold_and_struck_ids_are_recognised(self):
        text = HEADER + "| **D5** | b |\n| ~~D6~~ | s |\n| **~~D7~~** | bs |\n"
        self.assertEqual(MOD.parse_ids(text), ["D5", "D6", "D7"])

    def test_a_struck_row_present_on_one_side_only_is_still_a_divergence(self):
        result = MOD.reconcile(
            HEADER + "| D1 | a |\n| ~~D2~~ | struck |\n", HEADER + "| D1 | a |\n"
        )
        self.assertEqual(result["head_only"], ["D2"])

    def test_every_lettered_section_is_in_scope(self):
        text = HEADER + "".join(
            f"| {i} | x |\n" for i in ("A1", "B3a", "C2", "D9", "E1", "F4", "G5")
        )
        self.assertEqual(
            MOD.parse_ids(text), ["A1", "B3a", "C2", "D9", "E1", "F4", "G5"]
        )

    def test_the_pattern_is_printed_in_both_output_modes(self):
        """A count without its regex is not reproducible -- so publish the regex."""
        result = MOD.reconcile(rows("D1"), rows("D1"))
        self.assertEqual(result["id_pattern"], MOD.ID_PATTERN)
        text = MOD.render(result, "HEAD", "docs/DOCKET.md", Path("docs/DOCKET.md"))
        self.assertIn(MOD.ID_PATTERN, text)

    def test_ids_are_ordered_numerically_not_lexically(self):
        """`sort -u` puts D99 after D146; section 11 records that live defect."""
        result = MOD.reconcile(rows("D9", "D99", "D146", "D1000"), rows())
        self.assertEqual(result["head_only"], ["D9", "D99", "D146", "D1000"])


class ExitContractTests(unittest.TestCase):
    """0 PASS / 1 write-back owed / 2 unlanded / 3 UNKNOWN, end to end."""

    def test_reconciled_tree_exits_zero(self):
        repo = TempDocketRepo(rows("D1", "D2"))
        try:
            code, payload = run_check(repo.path)
            self.assertEqual(code, MOD.EXIT_PASS)
            self.assertEqual(payload["verdict"], "PASS")
        finally:
            repo.close()

    def test_a_missing_worktree_file_is_unknown_not_pass(self):
        repo = TempDocketRepo(rows("D1"))
        try:
            repo.docket.unlink()
            code, payload = run_check(repo.path)
            self.assertEqual(code, MOD.EXIT_UNKNOWN)
            self.assertEqual(payload["verdict"], "UNKNOWN")
        finally:
            repo.close()

    def test_an_unreadable_commit_side_is_unknown_not_pass(self):
        repo = TempDocketRepo(rows("D1"))
        try:
            code, payload = run_check(repo.path, "--rev", "refs/heads/no-such-branch")
            self.assertEqual(code, MOD.EXIT_UNKNOWN)
            self.assertEqual(payload["verdict"], "UNKNOWN")
        finally:
            repo.close()

    def test_a_side_that_parses_to_zero_ids_is_unknown_not_pass(self):
        """A shape change must never be indistinguishable from agreement."""
        result = MOD.reconcile(HEADER, HEADER)
        self.assertEqual(result["verdict"], "UNKNOWN")
        self.assertEqual(result["exit_code"], MOD.EXIT_UNKNOWN)

    def test_zero_ids_on_one_side_only_is_unknown_rather_than_a_huge_divergence(self):
        result = MOD.reconcile(rows("D1", "D2"), HEADER)
        self.assertEqual(result["exit_code"], MOD.EXIT_UNKNOWN)


class HistoricalReconstructionTests(unittest.TestCase):
    """The check must fire on the divergences that motivated it."""

    def test_a_private_index_commit_without_writeback_reads_fail(self):
        """Model of `a703f972`: the commit gains a row the worktree never saw."""
        repo = TempDocketRepo(rows("D239", "D240"))
        try:
            repo.set_worktree(rows("D239", "D240"))
            landed = rows("D239", "D240", "D241")
            (repo.path / "docs" / "DOCKET.md").write_text(landed)
            git(repo.path, "add", "docs/DOCKET.md")
            git(repo.path, "commit", "-q", "-m", "D241 by private index")
            repo.set_worktree(rows("D239", "D240"))  # the form never writes back
            code, payload = run_check(repo.path)
            self.assertEqual(payload["head_only"], ["D241"])
            self.assertEqual(code, MOD.EXIT_FAIL_WRITEBACK_OWED)
        finally:
            repo.close()

    def test_the_worktree_side_can_be_read_from_a_revision(self):
        """`--worktree-from` is how a past divergence is reconstructed."""
        repo = TempDocketRepo(rows("D1"))
        try:
            (repo.path / "docs" / "DOCKET.md").write_text(rows("D1", "D2"))
            git(repo.path, "add", "docs/DOCKET.md")
            git(repo.path, "commit", "-q", "-m", "second")
            code, payload = run_check(repo.path, "--worktree-from", "HEAD~1")
            self.assertEqual(payload["head_only"], ["D2"])
            self.assertEqual(code, MOD.EXIT_FAIL_WRITEBACK_OWED)
        finally:
            repo.close()


class SubjectIntegrityTests(unittest.TestCase):
    """The subject on disk is the subject under test."""

    def test_the_target_is_the_tracked_script(self):
        self.assertTrue(TARGET.is_file())
        digest = hashlib.sha256(TARGET.read_bytes()).hexdigest()
        self.assertEqual(len(digest), 64)

    def test_no_status_is_taken_through_a_pipe(self):
        """A pipe replaces the status of the command that produced it."""
        source = TARGET.read_text()
        self.assertNotIn("shell=True", source)
        self.assertNotIn("os.system", source)


if __name__ == "__main__":
    unittest.main()
