"""The fresh-clone preflight: a shebang without an exec bit.

The defect this guards was latent from the day the files were created and was
invisible on this box, because every working copy carried the mode bit locally
while the committed tree did not. Only the COMMIT travels to a clone, so every
assertion here reads `git ls-tree -r HEAD` -- never `os.access`, and never the
index either: this checker's first draft read `git ls-files -s` and passed on a
mode that was staged and never committed (`0462b45b`).

Each check is exercised against a PLANTED specimen in a throwaway repository
before it is trusted against the real one. A checker that has never been seen to
fire is not a detector, and this whole audit exists because a parser that could
only ever return "clean" was mistaken for one.
"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from chief_engineer import exec_bits


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=str(repo), capture_output=True,
                          text=True, check=True).stdout


def _scratch_repo(files: dict[str, tuple[str, bool]]) -> Path:
    """A throwaway repo with one COMMIT. *files* maps path -> (contents,
    executable). Committed, not merely staged, because HEAD is the authority."""
    repo = Path(tempfile.mkdtemp(prefix="exec-bits-"))
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "audit@example.invalid")
    _git(repo, "config", "user.name", "audit")
    _git(repo, "config", "core.filemode", "true")
    for name, (text, executable) in files.items():
        target = repo / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        if executable:
            target.chmod(0o755)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "fixture")
    return repo


SHEBANG = "#!/usr/bin/env bash\necho hi\n"
PLAIN = "not a script at all\n"


class TrackedShebangScriptsTests(unittest.TestCase):
    """The instrument itself, before anything is concluded with it."""

    def test_it_finds_a_shebang_script_and_reports_the_committed_mode(self):
        repo = _scratch_repo({
            "run.sh": (SHEBANG, False),
            "go.sh": (SHEBANG, True),
            "notes.txt": (PLAIN, False),
        })
        found = exec_bits.tracked_shebang_scripts(repo)
        self.assertEqual(found, {"run.sh": "100644", "go.sh": "100755"},
                         "the instrument must see both modes and skip non-scripts")

    def test_it_reads_head_not_the_working_tree(self):
        """The exact shape that hid the real defect: the file on disk is
        executable, the commit says it is not, and only the commit travels."""
        repo = _scratch_repo({"run.sh": (SHEBANG, False)})
        (repo / "run.sh").chmod(0o755)
        found = exec_bits.tracked_shebang_scripts(repo)
        self.assertEqual(found["run.sh"], "100644",
                         "reading the working tree would have called this fixed")

    def test_it_reads_head_not_the_index(self):
        """The near-miss this checker had itself. A `git update-index --chmod`
        is real in the index and absent from the commit when core.filemode is
        false -- and a clone gets the commit."""
        repo = _scratch_repo({"run.sh": (SHEBANG, False)})
        _git(repo, "update-index", "--chmod=+x", "run.sh")
        self.assertIn("100755", _git(repo, "ls-files", "-s", "run.sh"),
                      "fixture failed: the index was supposed to be staged +x")
        found = exec_bits.tracked_shebang_scripts(repo)
        self.assertEqual(found["run.sh"], "100644",
                         "a staged-but-uncommitted mode must not read as fixed")


class AuditFiresOnPlantedSpecimensTests(unittest.TestCase):
    """Positive controls. Each of the three verdicts is SEEN to fire."""

    def _audit_with(self, repo: Path, required, waived):
        before = (exec_bits.REQUIRED_EXECUTABLE, exec_bits.WAIVED_NO_EXEC_BIT)
        exec_bits.REQUIRED_EXECUTABLE = required
        exec_bits.WAIVED_NO_EXEC_BIT = waived
        try:
            return exec_bits.audit(repo)
        finally:
            exec_bits.REQUIRED_EXECUTABLE, exec_bits.WAIVED_NO_EXEC_BIT = before

    def test_a_required_script_without_its_bit_is_caught(self):
        repo = _scratch_repo({"scripts/launcher.sh": (SHEBANG, False)})
        result = self._audit_with(repo, {"scripts/launcher.sh": "why"}, ())
        self.assertEqual(result["missing_required"], ["scripts/launcher.sh"])

    def test_a_required_script_with_its_bit_is_not_caught(self):
        """The negative half: the check must not fire on the fixed state."""
        repo = _scratch_repo({"scripts/launcher.sh": (SHEBANG, True)})
        result = self._audit_with(repo, {"scripts/launcher.sh": "why"}, ())
        self.assertEqual(result["missing_required"], [])

    def test_a_new_unregistered_script_without_its_bit_is_caught(self):
        """This is the ratchet: the 234 known ones are waived, but a NEW one
        cannot be added silently."""
        repo = _scratch_repo({
            "old.sh": (SHEBANG, False),
            "brand_new.sh": (SHEBANG, False),
        })
        result = self._audit_with(repo, {}, ("old.sh",))
        self.assertEqual(result["unregistered"], ["brand_new.sh"])

    def test_a_waiver_that_has_been_fixed_is_reported_stale(self):
        """A register nobody prunes stops describing the tree it claims to."""
        repo = _scratch_repo({"fixed.sh": (SHEBANG, True)})
        result = self._audit_with(repo, {}, ("fixed.sh",))
        self.assertEqual(result["stale_waivers"], ["fixed.sh"])

    def test_a_waiver_for_a_deleted_file_is_reported_stale(self):
        repo = _scratch_repo({"kept.sh": (SHEBANG, False)})
        result = self._audit_with(repo, {}, ("kept.sh", "deleted.sh"))
        self.assertEqual(result["stale_waivers"], ["deleted.sh"])

    # --- the register against a tree that has been REORGANISED --------------
    #
    # The register is a list of PATHS. MOVE_MAP batch 6 renames the tree under
    # 137 of them in ONE commit, and batch 7 renames more. Matched by string
    # equality against `git ls-tree -r HEAD`, every one of those reports twice
    # -- once as a stale waiver at the old spelling and once as an
    # unregistered file at the new one -- and the two CANCEL in any total, so
    # a reader comparing counts sees nothing move. `exec_bits._spellings`
    # matches through `lab_paths`; these three tests are what stop that
    # matcher from degenerating into "everything is covered".

    LEGACY_MOVED = "demo-output/website/dafoam/ladder-a/logs_A3/compare_cp.py"

    def test_a_waived_path_is_still_matched_after_its_tree_moves(self):
        successor = exec_bits.lab_paths.redirect(self.LEGACY_MOVED)
        self.assertEqual(
            successor, "cases/dafoam/ladder-a/logs_A3/compare_cp.py",
            "R22's destination is the premise of this test; if the map moved, "
            "this test has to be re-read rather than re-pointed")
        repo = _scratch_repo({successor: (SHEBANG, False)})
        result = self._audit_with(repo, {}, (self.LEGACY_MOVED,))
        self.assertEqual(result["stale_waivers"], [])
        self.assertEqual(result["unregistered"], [])

    def test_a_waived_path_that_is_nowhere_under_either_spelling_is_still_stale(self):
        """The must-not-match control. A matcher that answered "covered" to
        every waived path would satisfy the test above and register nothing."""
        repo = _scratch_repo({"kept.sh": (SHEBANG, False)})
        result = self._audit_with(repo, {}, ("kept.sh", self.LEGACY_MOVED))
        self.assertEqual(result["stale_waivers"], [self.LEGACY_MOVED])

    def test_a_moved_waiver_that_gained_its_bit_is_still_stale(self):
        """The second control: following the map must not also swallow the
        finding the register exists to make. A waived file that is executable
        at its NEW path is a stale waiver, exactly as at its old one."""
        successor = exec_bits.lab_paths.redirect(self.LEGACY_MOVED)
        repo = _scratch_repo({successor: (SHEBANG, True)})
        result = self._audit_with(repo, {}, (self.LEGACY_MOVED,))
        self.assertEqual(result["stale_waivers"], [self.LEGACY_MOVED])


class ThisRepositoryTests(unittest.TestCase):
    """The real tree. Runs only after the checks above proved they can fire."""

    def setUp(self):
        self.result = exec_bits.audit()

    def test_a_fresh_clone_can_run_the_sanctioned_launchers(self):
        self.assertEqual(
            self.result["missing_required"], [],
            "these are tracked non-executable, so `git clone && run` fails: "
            + ", ".join(self.result["missing_required"]))

    def test_no_shebang_script_is_both_unexecutable_and_unregistered(self):
        self.assertEqual(
            self.result["unregistered"], [],
            "new shebang-bearing tracked file(s) with no exec bit and no entry "
            "in exec_bits.WAIVED_NO_EXEC_BIT. Either `git update-index "
            "--chmod=+x` them, or add them to the register with their owning "
            "family: " + ", ".join(self.result["unregistered"]))

    def test_the_waiver_register_still_describes_the_tree(self):
        self.assertEqual(
            self.result["stale_waivers"], [],
            "waived path(s) that have since gained an exec bit or been deleted; "
            "prune them from exec_bits.WAIVED_NO_EXEC_BIT: "
            + ", ".join(self.result["stale_waivers"]))

    def test_the_register_is_split_across_families_and_says_so(self):
        """The register is a routing document, not just a count -- a supervisor
        must be able to read off whose files these are without re-deriving it."""
        split = exec_bits.waived_by_owner()
        self.assertEqual(sum(len(v) for v in split.values()),
                         len(exec_bits.WAIVED_NO_EXEC_BIT))
        self.assertNotIn("UNASSIGNED", split,
                         "a waived path with no owning family cannot be routed")


class LaunchSolvePreflightGateTests(unittest.TestCase):
    """The gate that made the missing bit dangerous rather than untidy.

    `launch_solve.sh` used to run the preflight only `if [ -x "$PF" ]`, so a
    preflight that was present but not executable was SKIPPED and the launch
    proceeded -- silence read as success. These assertions are on the script's
    text because running the real launcher launches a real solve.
    """

    GATE = Path("/home/ubuntu/Certonomous/scripts/launch_solve.sh")

    def setUp(self):
        if not self.GATE.exists():
            self.skipTest("launch_solve.sh not present")
        self.text = self.GATE.read_text()

    def test_the_gate_no_longer_skips_on_a_missing_exec_bit(self):
        self.assertNotIn('if [ -x "$PF" ] && [ -d "$CASE" ]; then', self.text,
                         "the fail-false condition is back: a non-executable "
                         "preflight would skip the gate silently")

    def test_a_present_but_unexecutable_preflight_is_still_run(self):
        self.assertIn('bash "$PF" "$CASE" --quiet', self.text,
                      "a missing mode bit must not be read as a clean bill")

    def test_an_absent_preflight_gets_its_own_verdict(self):
        """Third state. `checked and clean` and `never checked` are different
        facts and must not print the same way."""
        self.assertIn("PREFLIGHT NOT RUN", self.text)
        self.assertIn("REFUSING TO LAUNCH", self.text)
        self.assertNotEqual(
            self.text.count("PREFLIGHT NOT RUN"), 0,
            "the unknown verdict must exist separately from the failure verdict")


if __name__ == "__main__":
    unittest.main()
