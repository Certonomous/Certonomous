"""Pins for `scripts/hunk_check.py`'s index-freedom (the B2 fail-false repair).

WHY THIS FILE EXISTS AND WHY IT IS NOT test_hunk_check.py
========================================================
A test that exercised `hunk_check` on an ORDINARY tracked file would have
passed throughout the entire period the gate was broken. The defect only shows
on a file that is in HEAD and has NO entry in the shared `.git/index` -- which
is not an exotic state here, it is what this lab's own private-index commit
protocol creates for every new file it lands. `git diff HEAD -- <path>` walks
the index, so such a file read as a whole-file DELETION: measured at
`1a9f7f12`, a declared `0+/1-` was graded against an actual `0+/288-`.

So every fixture below BUILDS THAT STATE with a real `GIT_INDEX_FILE` commit,
and the assertions name the NUMBERS for that file in that mode. None asserts a
count of findings, of paths, or of anything else -- a count survives the
mutation that swaps added for removed, and it survives a mode that grades the
wrong file.
"""

from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TARGET = REPO / "scripts" / "hunk_check.py"


def load_module():
    spec = importlib.util.spec_from_file_location("_hunk_check", TARGET)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MOD = load_module()


def git(repo: Path, *args: str, env=None) -> subprocess.CompletedProcess:
    """Run git with a list; read `returncode` directly, never through a pipe."""
    full = {**os.environ, **(env or {})}
    done = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, env=full
    )
    assert done.returncode == 0, f"{args}: {done.stderr}"
    return done


class Scratch:
    """A real repository, with a real private-index commit in its history."""

    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)
        git(self.path, "init", "-q", "-b", "main")
        git(self.path, "config", "user.email", "t@example.invalid")
        git(self.path, "config", "user.name", "t")
        (self.path / "seed.txt").write_text("seed\n")
        git(self.path, "add", "seed.txt")
        git(self.path, "commit", "-q", "-m", "seed")

    def land_by_private_index(self, rel: str, text: str) -> None:
        """Commit *rel* WITHOUT touching the shared index -- the real protocol.

        This is the fixture the whole file turns on: afterwards the path is in
        HEAD, is on disk, and has NO shared-index entry.
        """
        target = self.path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        blob = git(self.path, "hash-object", "-w", rel).stdout.strip()
        idx = str(self.path / ".git" / "private-index")
        env = {"GIT_INDEX_FILE": idx}
        head = git(self.path, "rev-parse", "HEAD").stdout.strip()
        git(self.path, "read-tree", head, env=env)
        git(self.path, "update-index", "--add", "--cacheinfo",
            f"100644,{blob},{rel}", env=env)
        tree = git(self.path, "write-tree", env=env).stdout.strip()
        new = git(self.path, "commit-tree", tree, "-p", head, "-m",
                  "landed by private index", env=env).stdout.strip()
        git(self.path, "update-ref", "refs/heads/main", new, head)
        os.remove(idx)

    def has_index_entry(self, rel: str) -> bool:
        done = subprocess.run(
            ["git", "-C", str(self.path), "ls-files", "-s", rel],
            capture_output=True, text=True,
        )
        return bool(done.stdout.strip())

    def close(self):
        self.tmp.cleanup()


def run(repo: Path, *decl: str) -> tuple[int, str]:
    done = subprocess.run(
        [sys.executable, str(TARGET), "--root", str(repo), *decl],
        capture_output=True, text=True,
    )
    return done.returncode, done.stdout


class TheFailingCaseTests(unittest.TestCase):
    """A file in HEAD with no shared-index entry. The defect's home ground."""

    def setUp(self):
        self.s = Scratch()
        self.addCleanup(self.s.close)
        self.s.land_by_private_index("pkg/thing.py", "".join(
            f"line {i}\n" for i in range(1, 21)))

    def test_the_fixture_really_has_no_index_entry(self):
        """If this ever passes trivially, every test below is vacuous."""
        self.assertFalse(self.s.has_index_entry("pkg/thing.py"))
        self.assertTrue((self.s.path / "pkg" / "thing.py").is_file())

    def test_one_removed_line_grades_as_one_removed_line(self):
        """The exact shape that graded 0+/288- before the repair."""
        p = self.s.path / "pkg" / "thing.py"
        p.write_text("".join(f"line {i}\n" for i in range(2, 21)))
        actual = MOD.worktree_numstat(str(self.s.path), "HEAD", ["pkg/thing.py"])
        self.assertEqual(actual["pkg/thing.py"], (0, 1))

    def test_one_added_line_grades_as_one_added_line(self):
        p = self.s.path / "pkg" / "thing.py"
        p.write_text(p.read_text() + "line 21\n")
        actual = MOD.worktree_numstat(str(self.s.path), "HEAD", ["pkg/thing.py"])
        self.assertEqual(actual["pkg/thing.py"], (1, 0))

    def test_an_unchanged_file_is_absent_and_is_never_reported_as_a_deletion(self):
        """The defect's exact signature was a DELETION here. It must be gone.

        Absent rather than `(0, 0)`: the B1 clause requires "nothing changed at
        the declared path" to reach `reconcile`'s UNKNOWN branch. Grading it as
        a real 0+/0- turns that clause into a FAIL, which is a regression this
        assertion exists to hold shut.
        """
        actual = MOD.worktree_numstat(str(self.s.path), "HEAD", ["pkg/thing.py"])
        self.assertNotIn("pkg/thing.py", actual)

    def test_an_unchanged_file_declared_as_changed_is_UNKNOWN_not_a_deletion(self):
        """End to end: the B1 clause survives the index-freedom repair."""
        code, out = run(self.s.path, "pkg/thing.py:1")
        self.assertNotIn("actual 0+/20-", out)
        self.assertEqual(code, MOD.EXIT[MOD.UNKNOWN])

    def test_the_end_to_end_declaration_passes_for_the_true_numbers(self):
        p = self.s.path / "pkg" / "thing.py"
        p.write_text("".join(f"line {i}\n" for i in range(2, 21)))
        code, out = run(self.s.path, "pkg/thing.py:0-1")
        self.assertIn("declared 0+/1-", out)
        self.assertIn("actual 0+/1-", out)
        self.assertEqual(code, MOD.EXIT[MOD.PASS])

    def test_a_wrong_declaration_still_fails_on_the_failing_case(self):
        """The repair must not have turned the gate off."""
        p = self.s.path / "pkg" / "thing.py"
        p.write_text("".join(f"line {i}\n" for i in range(2, 21)))
        code, out = run(self.s.path, "pkg/thing.py:0-7")
        self.assertIn("removed lines declared 7, actual 1", out)
        self.assertEqual(code, MOD.EXIT[MOD.FAIL])

    def test_no_index_entry_is_reported_as_such_and_not_as_a_peers_staged_edit(self):
        """Two states `git diff --cached` renders identically, kept apart."""
        staged, missing = MOD.index_anomalies(str(self.s.path), [])
        self.assertIn("pkg/thing.py", missing)
        self.assertNotIn("pkg/thing.py", staged)


class NewFileIsFirstClassTests(unittest.TestCase):
    """A path absent from the rev and present on disk is N+/0-, not a diff."""

    def setUp(self):
        self.s = Scratch()
        self.addCleanup(self.s.close)

    def test_an_untracked_new_file_is_all_additions(self):
        (self.s.path / "fresh.txt").write_text("a\nb\nc\n")
        actual = MOD.worktree_numstat(str(self.s.path), "HEAD", ["fresh.txt"])
        self.assertEqual(actual["fresh.txt"], (3, 0))

    def test_a_new_file_with_no_trailing_newline_counts_its_last_line(self):
        (self.s.path / "fresh.txt").write_text("a\nb")
        actual = MOD.worktree_numstat(str(self.s.path), "HEAD", ["fresh.txt"])
        self.assertEqual(actual["fresh.txt"], (2, 0))

    def test_a_file_in_head_and_deleted_from_disk_is_all_removals(self):
        self.s.land_by_private_index("gone.txt", "x\ny\n")
        os.remove(self.s.path / "gone.txt")
        actual = MOD.worktree_numstat(str(self.s.path), "HEAD", ["gone.txt"])
        self.assertEqual(actual["gone.txt"], (0, 2))

    def test_a_path_in_neither_side_is_absent_rather_than_zero(self):
        actual = MOD.worktree_numstat(str(self.s.path), "HEAD", ["nowhere.txt"])
        self.assertNotIn("nowhere.txt", actual)


class ModeSoundnessTests(unittest.TestCase):
    """Which mode was broken, and which was not."""

    def setUp(self):
        self.s = Scratch()
        self.addCleanup(self.s.close)

    def test_at_mode_grades_the_commit_object_and_ignores_the_shared_index(self):
        """`--at` was never broken; this is the assertion that says so."""
        self.s.land_by_private_index("pkg/a.py", "1\n2\n3\n")
        sha = git(self.s.path, "rev-parse", "HEAD").stdout.strip()
        self.assertFalse(self.s.has_index_entry("pkg/a.py"))
        done = subprocess.run(
            [sys.executable, str(TARGET), "--root", str(self.s.path),
             "--at", sha, "pkg/a.py:3-0"],
            capture_output=True, text=True,
        )
        self.assertIn("actual 3+/0-", done.stdout)
        self.assertEqual(done.returncode, MOD.EXIT[MOD.PASS])

    def test_the_worktree_mode_never_invokes_a_diff_against_the_index(self):
        """Immunity is by construction, so it is asserted on the source."""
        source = TARGET.read_text()
        body = source.split('"""', 2)[-1]  # exclude the docstring's prose
        self.assertNotIn('"diff", "--numstat", "--no-renames", "HEAD"', body)
        self.assertNotIn('"diff-index", "--numstat"', body)
        self.assertIn('"--no-index"', body)


class SubjectIntegrityTests(unittest.TestCase):
    def test_the_subject_is_the_tracked_script(self):
        self.assertTrue(TARGET.is_file())
        self.assertEqual(len(hashlib.sha256(TARGET.read_bytes()).hexdigest()), 64)


if __name__ == "__main__":
    unittest.main()
