"""Controls for `scripts/hunk_check.py`, both halves (L-84), on real repositories.

Every case builds a throwaway `git init` under `tempfile` and drives the SHIPPED
ENTRY POINT `main()` -- not its helpers. A test file that exercises only helpers
is the recompute-instead-of-drive shape, and this lab has one measured instance
of 34 green tests over a function that could have returned an empty result
unconditionally.

The module under test is located through `HUNK_CHECK_PATH` so that a mutation
cell can point the whole file at a MUTATED COPY in a scratch directory. Nothing
here ever writes to a tracked path: a harness that mutates `scripts/*.py` in
place leaves a window in which any concurrent agent's commit captures the
mutant, and `git status` reads clean throughout because the harness's `finally`
restores the worktree. That is the defect this module exists to catch, and
building its own tests that way would be the joke telling itself.

EXPECTED BEHAVIOUR IS DERIVED FROM THE SPECIFICATION IN `hunk_check.py`'s
DOCSTRING AND FROM MEASURED GIT SEMANTICS, never by reading what the code
currently does. The two git facts each case rests on were measured in a scratch
repository before a line of the check was written:

  1. `git commit -F msg -- <paths>` takes those paths FROM THE WORKING TREE and
     ignores the index.
  2. `git update-ref <ref> <new> <old>` is an atomic compare-and-swap.
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_DEFAULT = Path(__file__).resolve().parents[2] / "scripts" / "hunk_check.py"
_TARGET = Path(os.environ.get("HUNK_CHECK_PATH", _DEFAULT))
_spec = importlib.util.spec_from_file_location("hunk_check_under_test", _TARGET)
hc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hc)

PASS, FAIL, UNKNOWN = 0, 1, 3


def git(root, *args, **kw):
    cp = subprocess.run(["git", "-C", str(root), *args],
                        capture_output=True, text=True, **kw)
    if cp.returncode and not kw.get("ok_fail"):
        pass
    return cp


class RepoCase(unittest.TestCase):
    """A fresh repository per test, with two committed files."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        git(self.root, "init", "-q", "-b", "main", ".")
        git(self.root, "config", "user.email", "t@t.t")
        git(self.root, "config", "user.name", "t")
        (self.root / "d.md").write_text("r1\nr2\n")
        (self.root / "o.txt").write_text("o\n")
        git(self.root, "add", "d.md", "o.txt")
        git(self.root, "commit", "-qm", "base")

    def tearDown(self):
        self._tmp.cleanup()

    def run_check(self, *decl, at=None):
        argv = list(decl) + ["--root", str(self.root)]
        if at:
            argv += ["--at", at]
        return hc.main(argv)

    def commit_pathspec(self, msg, *paths):
        """The lab's mandated form: add, then commit with the SAME pathspec."""
        git(self.root, "add", *paths)
        git(self.root, "commit", "-q", "-m", msg, "--", *paths)
        return git(self.root, "rev-parse", "HEAD").stdout.strip()


# ---------------------------------------------------------------------------
# L-84 first half: the check must FIRE on the defect
# ---------------------------------------------------------------------------
class TheCheckFires(RepoCase):

    def test_an_extra_hunk_captured_into_a_declared_file_FAILS(self):
        """The `0a3e82d7` shape: one intended edit, a second swept in."""
        (self.root / "d.md").write_text("r1\nMINE\n")        # intended: 1+/1-
        (self.root / "d.md").write_text("r1\nMINE\nFOREIGN\n")  # captured: +1
        sha = self.commit_pathspec("mine", "d.md")
        self.assertEqual(self.run_check("d.md:1-1", at=sha), FAIL)

    def test_an_extra_FILE_carried_into_the_commit_FAILS(self):
        (self.root / "d.md").write_text("r1\nr2\nMINE\n")
        (self.root / "o.txt").write_text("o\nSOMEONE ELSE\n")
        sha = self.commit_pathspec("mine", "d.md", "o.txt")
        self.assertEqual(self.run_check("d.md:1", at=sha), FAIL)

    def test_contiguous_appended_rows_FAIL_although_they_are_ONE_hunk(self):
        """The `49b36e57` shape. Five adjacent added lines are one `@@` hunk at
        any -U, so a hunk-counting check misses this and a LINE count catches
        it. This is why the declaration counts lines."""
        (self.root / "d.md").write_text("r1\nr2\nMINE\nA\nB\nC\nD\n")
        sha = self.commit_pathspec("mine", "d.md")
        hunks = git(self.root, "show", "-U0", "--format=", sha).stdout
        self.assertEqual(hunks.count("\n@@"), 1, "one hunk, five rows")
        self.assertEqual(self.run_check("d.md:1", at=sha), FAIL)

    def test_a_path_another_agent_STAGED_into_the_shared_index_FAILS(self):
        """One `.git/index` is shared by every agent in this repository."""
        (self.root / "d.md").write_text("r1\nr2\nMINE\n")
        (self.root / "o.txt").write_text("o\nTHEIR WORK\n")
        git(self.root, "add", "o.txt")                # the other agent's add
        self.assertEqual(self.run_check("d.md:1"), FAIL)

    def test_the_INDEX_is_not_the_truth_for_a_pathspec_commit(self):
        """Measured git semantics: `git commit -- <path>` re-reads the WORKING
        TREE. A check that read `git diff --cached` would PASS this and the
        commit would land the foreign line, so the default mode reads the
        worktree and this case is the proof it does."""
        (self.root / "d.md").write_text("r1\nMINE\n")
        git(self.root, "add", "d.md")
        (self.root / "d.md").write_text("r1\nMINE\nFOREIGN\n")   # after the add
        staged = git(self.root, "diff", "--cached", "--numstat", "HEAD").stdout
        self.assertIn("1\t1\td.md", staged, "the index still reads 1+/1-")
        self.assertEqual(self.run_check("d.md:1-1"), FAIL)

    def test_a_STALE_private_index_that_reverts_another_commit_FAILS(self):
        """The private-index technique's worst failure mode, measured: if HEAD
        moves between `git read-tree HEAD` and the commit, the commit silently
        DELETES the intervening work. Strictly worse than a capture."""
        head = git(self.root, "rev-parse", "HEAD").stdout.strip()
        idx = str(self.root / ".pidx")
        env = dict(os.environ, GIT_INDEX_FILE=idx)
        subprocess.run(["git", "-C", str(self.root), "read-tree", head],
                       env=env, check=True)
        (self.root / "n.txt").write_text("agent2\n")     # concurrent commit
        self.commit_pathspec("agent2", "n.txt")
        blob = (self.root / ".mine")
        blob.write_text("r1\nr2\nMINE\n")
        oid = git(self.root, "hash-object", "-w", str(blob)).stdout.strip()
        subprocess.run(["git", "-C", str(self.root), "update-index", "--add",
                        "--cacheinfo", f"100644,{oid},d.md"], env=env, check=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-q", "-m",
                        "private"], env=env, check=True)
        sha = git(self.root, "rev-parse", "HEAD").stdout.strip()
        self.assertNotIn("n.txt", git(self.root, "ls-tree", "-r", "--name-only",
                                      sha).stdout, "the revert really happened")
        self.assertEqual(self.run_check("d.md:1", at=sha), FAIL)

    def test_a_private_index_that_DROPS_the_authors_own_second_edit_FAILS(self):
        """`HEAD's version + my row` silently discards any other edit the same
        author made to that file. The worktree keeps it, so it looks done."""
        (self.root / "d.md").write_text("r1\nFIXED\nMINE\n")   # 2 edits: 2+/1-
        blob = self.root / ".mine"
        blob.write_text(git(self.root, "show", "HEAD:d.md").stdout + "MINE\n")
        oid = git(self.root, "hash-object", "-w", str(blob)).stdout.strip()
        idx = str(self.root / ".pidx")
        env = dict(os.environ, GIT_INDEX_FILE=idx)
        for cmd in (["read-tree", "HEAD"],
                    ["update-index", "--add", "--cacheinfo", f"100644,{oid},d.md"],
                    ["commit", "-q", "-m", "private"]):
            subprocess.run(["git", "-C", str(self.root), *cmd], env=env, check=True)
        sha = git(self.root, "rev-parse", "HEAD").stdout.strip()
        self.assertEqual(self.run_check("d.md:2-1", at=sha), FAIL)


# ---------------------------------------------------------------------------
# L-84 second half: the check must NOT fire on legitimate work.
# A check that fails everything is not a gate, it is an off switch.
# ---------------------------------------------------------------------------
class TheCheckDoesNotFire(RepoCase):

    def test_a_clean_single_author_commit_PASSES(self):
        (self.root / "d.md").write_text("r1\nr2\nMINE\n")
        sha = self.commit_pathspec("mine", "d.md")
        self.assertEqual(self.run_check("d.md:1", at=sha), PASS)

    def test_two_files_LEGITIMATELY_intended_and_declared_PASS(self):
        (self.root / "d.md").write_text("r1\nr2\nMINE\n")
        (self.root / "o.txt").write_text("o\nALSO MINE\n")
        sha = self.commit_pathspec("mine", "d.md", "o.txt")
        self.assertEqual(self.run_check("d.md:1", "o.txt:1", at=sha), PASS)

    def test_a_removal_declared_PASSES(self):
        (self.root / "d.md").write_text("r1\n")
        sha = self.commit_pathspec("mine", "d.md")
        self.assertEqual(self.run_check("d.md:0-1", at=sha), PASS)

    def test_a_CORRECT_private_index_commit_PASSES_beside_foreign_worktree_rows(self):
        """The technique working as intended: two other agents' rows sit
        uncommitted in the worktree and neither is captured."""
        (self.root / "d.md").write_text("r1\nr2\nTHEIRS_A\nMINE\nTHEIRS_B\n")
        blob = self.root / ".mine"
        blob.write_text(git(self.root, "show", "HEAD:d.md").stdout + "MINE\n")
        oid = git(self.root, "hash-object", "-w", str(blob)).stdout.strip()
        env = dict(os.environ, GIT_INDEX_FILE=str(self.root / ".pidx"))
        for cmd in (["read-tree", "HEAD"],
                    ["update-index", "--add", "--cacheinfo", f"100644,{oid},d.md"],
                    ["commit", "-q", "-m", "private"]):
            subprocess.run(["git", "-C", str(self.root), *cmd], env=env, check=True)
        sha = git(self.root, "rev-parse", "HEAD").stdout.strip()
        self.assertEqual(self.run_check("d.md:1", at=sha), PASS)
        self.assertIn("THEIRS_A", (self.root / "d.md").read_text())

    def test_an_UNTRACKED_new_file_is_counted_as_wholly_added(self):
        """`git diff HEAD -- <path>` is blind to an untracked path, so a
        declared new file read as `nothing changed`. Found by dogfooding this
        check on its own first commit. The count asserted here is git's own:
        the file is committed afterwards and `--numstat` must agree."""
        (self.root / "n.md").write_text("a\nb\nc\n")
        self.assertEqual(self.run_check("n.md:3"), PASS)
        sha = self.commit_pathspec("new", "n.md")
        self.assertIn("3\t0\tn.md",
                      git(self.root, "show", "--numstat", "--format=",
                          sha).stdout)

    def test_a_new_file_with_no_trailing_newline_matches_gits_own_count(self):
        (self.root / "n.md").write_text("a\nb")
        self.assertEqual(self.run_check("n.md:2"), PASS)

    def test_an_unrelated_dirty_worktree_does_NOT_fail_the_check(self):
        """Ten agents write here; the docket is permanently dirty. A check that
        reddens on another agent's UNSTAGED file is a check nobody can pass."""
        (self.root / "d.md").write_text("r1\nr2\nMINE\n")
        (self.root / "o.txt").write_text("o\nTHEIR UNSTAGED DRAFT\n")
        self.assertEqual(self.run_check("d.md:1"), PASS)


# ---------------------------------------------------------------------------
# Defect class B1: it must never PASS from an empty set
# ---------------------------------------------------------------------------
class EmptySetIsNotAgreement(RepoCase):

    def test_no_declaration_is_UNKNOWN_and_not_PASS(self):
        (self.root / "d.md").write_text("r1\nr2\nMINE\n")
        self.assertEqual(self.run_check(""), UNKNOWN)

    def test_nothing_changed_at_the_declared_path_is_UNKNOWN_and_not_PASS(self):
        self.assertEqual(self.run_check("d.md:1"), UNKNOWN)

    def test_a_question_mark_is_UNGRADED_and_therefore_UNKNOWN(self):
        (self.root / "d.md").write_text("r1\nr2\nMINE\n")
        sha = self.commit_pathspec("mine", "d.md")
        self.assertEqual(self.run_check("d.md:?", at=sha), UNKNOWN)

    def test_a_question_mark_still_FAILS_on_an_undeclared_path(self):
        """`?` buys the author no forgiveness anywhere but that one number."""
        (self.root / "d.md").write_text("r1\nr2\nMINE\n")
        (self.root / "o.txt").write_text("o\nFOREIGN\n")
        sha = self.commit_pathspec("mine", "d.md", "o.txt")
        self.assertEqual(self.run_check("d.md:?", at=sha), FAIL)

    def test_an_unparseable_declaration_is_UNKNOWN_and_not_PASS(self):
        self.assertEqual(self.run_check("d.md=1"), UNKNOWN)

    def test_the_exit_contract_matches_lab_checks(self):
        self.assertEqual(hc.EXIT, {"PASS": 0, "FAIL": 1, "UNKNOWN": 3})


if __name__ == "__main__":
    unittest.main()
