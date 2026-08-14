"""G-RULE: EVERY GATE DIFFS INSTALLED AGAINST TRACKED.

WHY THIS FILE EXISTS (D53, 2026-08-14)
--------------------------------------
`sdk/tests/test_autostop_gate.py` proved one pair -- `scripts/auto-stop.sh`
against `/usr/local/bin/auto-stop.sh` -- with the two paths typed into it. That
closed the incident and not the class. On 2026-07-30 a repaired gate was
committed and never installed, the box ran the broken one for thirteen days,
and the reason nothing caught it is that NOTHING WAS COMPARING WHAT WAS
REVIEWED AGAINST WHAT WAS RUNNING. Any other artifact with a copy outside the
tree had, and until this file had still, the identical unguarded gap.

So the pairs are DATA (`scripts/installed_registry.py:DEPLOYMENTS`) and this is
the one mechanism that reads them. Adding a gate later is a registry entry, not
another test file -- which is the whole point, because a class of defect that
needs a new file each time it recurs is not closed.

WHAT IS ASSERTED, AND WHY EACH ASSERTION IS HERE
------------------------------------------------
* Drift is REFUSED. That is the 2026-07-30 failure itself.
* Absence is TOLERATED. A laptop has no root crontab; nothing is powering that
  box off, so there is nothing to drift. But absence must SAY SO -- a skip that
  reads like a pass is how a detector goes quiet.
* A DANGLING entry -- registered tracked path missing from the tree -- FAILS.
  A registry pointing at nothing is a checker that can never fire, and a
  checker that cannot fire is not a detector (L-84).
* EVERY BRANCH IS SHOWN TO FIRE against planted drift in a scratch directory
  before it is trusted. `test_planted_drift_is_refused` and its siblings are
  the positive controls; without them this file is an assertion that the world
  is fine, made by an instrument nobody has seen work.
* NO TRACKED STAGING GHOST may sit beside a registered artifact. This is the
  rule that `scripts/auto-stop.sh.proposed` earned: a committed `.proposed`
  copy makes the tree LOOK repaired and points every reader at the wrong pair.

WHAT THIS FILE CANNOT SEE, stated rather than discovered later:
`sudo -n crontab -l` needs passwordless sudo. Where that is not available the
root crontab entry reads ABSENT and drift in the schedule that runs the
auto-stop gate would go unnoticed on that host. `test_the_pairs_this_host_can
_actually_see_are_reported` exists so that reach is printed rather than
assumed, and `test_the_box_that_runs_the_gate_must_compare_it` refuses the
specific case of a production box skipping its own gate.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "installed_registry_under_test", REPO / "scripts" / "installed_registry.py")
reg = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = reg
_SPEC.loader.exec_module(reg)


def _scratch_pair(tmp: Path, tracked_text: str, installed_text: str | None,
                  normalize: str = "text") -> tuple[reg.Deployment, Path]:
    """A registry entry pointing entirely at a scratch tree.

    The installed side is redirected through the entry's own env override --
    the same door a real check uses -- so what these controls exercise is the
    production code path and not a test-only shim.
    """
    repo = tmp / "repo"
    (repo / "scripts").mkdir(parents=True, exist_ok=True)
    (repo / "scripts" / "thing.sh").write_text(tracked_text)
    dep = reg.Deployment(
        name="scratch pair",
        tracked="scripts/thing.sh",
        source=str(tmp / "installed.sh"),
        why="a control",
        reinstall="cp scripts/thing.sh /nowhere",
        normalize=normalize,
    )
    if installed_text is not None:
        (tmp / "installed.sh").write_text(installed_text)
    return dep, repo


class InstalledMatchesTrackedTests(unittest.TestCase):
    """The live registry, against this host."""

    @classmethod
    def setUpClass(cls):
        cls.findings = reg.report()

    def test_no_registered_artifact_has_drifted_from_its_tracked_copy(self):
        drifted = [f for f in self.findings if f.state == reg.DRIFT]
        self.assertEqual(
            [], drifted,
            "an installed artifact differs from the reviewed copy in the tree. "
            "This is the 2026-07-30 failure exactly -- the machine is running "
            "something nobody reviewed, or ignoring something somebody did:\n"
            + "\n\n".join(f"{f.dep.name}: {f.dep.tracked} -> "
                          f"{f.dep.installed_where}\n{f.detail}\n"
                          f"reinstall: {f.dep.reinstall}" for f in drifted))

    def test_no_registry_entry_points_at_a_tracked_file_that_is_missing(self):
        dangling = [f for f in self.findings if f.state == reg.DANGLING]
        self.assertEqual(
            [], dangling,
            "registry entr(ies) whose TRACKED side does not exist. This is not "
            "a skip: the pair can never be compared, so the entry is a green "
            "light wired to nothing:\n"
            + "\n".join(f"{f.dep.name}: {f.detail}" for f in dangling))

    def test_every_entry_says_what_breaks_and_how_to_repair_it(self):
        """A drift report nobody can act on is a fault message, not a fix.

        The 2026-07-30 incident ended with a correct file in the tree and no
        instruction anywhere that it had to be installed.
        """
        for dep in reg.DEPLOYMENTS:
            with self.subTest(dep.name):
                self.assertTrue(dep.why.strip(), f"{dep.name} states no stake")
                self.assertTrue(dep.reinstall.strip(),
                                f"{dep.name} states no repair command")

    def test_the_pairs_this_host_can_actually_see_are_reported(self):
        """Reach, printed rather than assumed (L-84).

        This test does not fail on a laptop where everything is absent -- it
        exists so the reach is visible in the run, because a suite that skipped
        every pair is green and blind.
        """
        seen = reg.reached(self.findings)
        skipped = [(f.dep.name, f.detail) for f in self.findings
                   if f.state == reg.ABSENT]
        print(f"\n[installed-vs-tracked] compared on this host: "
              f"{', '.join(seen) or 'NOTHING'}")
        for name, why in skipped:
            print(f"[installed-vs-tracked] SKIPPED {name}: {why}")
        for _, why in skipped:
            self.assertTrue(why.strip(),
                            "an absent pair must carry the reason it is absent")

    def test_the_box_that_runs_the_gate_must_compare_it(self):
        """On the production box, skipping is not an option.

        If `/usr/local/bin/auto-stop.sh` exists then this IS the machine the
        gate powers off, and a run that skipped the comparison here would be
        the original defect wearing a green suite.
        """
        if not Path("/usr/local/bin/auto-stop.sh").exists():
            self.skipTest("not the box that runs the auto-stop gate")
        self.assertIn(
            "auto-stop gate", reg.reached(self.findings),
            "this host runs /usr/local/bin/auto-stop.sh but the registry did "
            "not compare it -- the one machine that must not skip did skip")


class TheCheckIsShownToFireTests(unittest.TestCase):
    """Positive controls. Every branch, planted, in a scratch tree.

    A checker never seen to fail is not a detector. These plant the defect and
    require the mechanism to redden -- and they are separate from the live
    registry tests on purpose, so that a green run on a laptop with nothing
    installed still exercises the comparator itself.
    """

    def test_planted_drift_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            dep, repo = _scratch_pair(tmp, "echo reviewed\n", "echo RUNNING\n")
            os.environ.pop(dep.env_override, None)
            finding = reg.compare(dep, repo)
        self.assertEqual(reg.DRIFT, finding.state,
                         "an installed copy differing from the tracked one was "
                         f"not reported as drift; got {finding.state}")
        self.assertIn("RUNNING", finding.detail,
                      "the drift report must show what is actually running")

    def test_a_matching_pair_is_not_reported_as_drift(self):
        """The other direction, so the fix cannot be 'fail always'."""
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            dep, repo = _scratch_pair(tmp, "echo same\n", "echo same\n")
            finding = reg.compare(dep, repo)
        self.assertEqual(reg.MATCH, finding.state, finding.detail)

    def test_planted_absence_is_tolerated_and_carries_its_reason(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            dep, repo = _scratch_pair(tmp, "echo reviewed\n", None)
            finding = reg.compare(dep, repo)
        self.assertEqual(reg.ABSENT, finding.state,
                         "a host with no installed copy must skip, not fail")
        self.assertFalse(finding.is_failure)
        self.assertIn("does not exist", finding.detail)

    def test_a_dangling_tracked_side_is_a_failure_not_a_skip(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            dep, repo = _scratch_pair(tmp, "echo reviewed\n", "echo reviewed\n")
            (repo / "scripts" / "thing.sh").unlink()
            finding = reg.compare(dep, repo)
        self.assertEqual(reg.DANGLING, finding.state)
        self.assertTrue(finding.is_failure,
                        "a registry entry with no reviewed copy must fail: it "
                        "is a check that can never fire")

    def test_a_command_source_that_fails_reads_as_absent_with_the_reason(self):
        """`crontab -l` exits non-zero when there is no crontab.

        That must read as ABSENT-with-reason, never as an empty installed copy
        that happens to match an empty tracked one.
        """
        dep = reg.Deployment(
            name="failing command", tracked="scripts/auto-stop.sh",
            source=("false",), why="a control", reinstall="none")
        text, why = reg.installed_text(dep)
        self.assertIsNone(text)
        self.assertIn("exited 1", why)

    def test_a_missing_binary_reads_as_absent_rather_than_raising(self):
        dep = reg.Deployment(
            name="missing binary", tracked="scripts/auto-stop.sh",
            source=("certonomous-no-such-binary",), why="a control",
            reinstall="none")
        text, why = reg.installed_text(dep)
        self.assertIsNone(text)
        self.assertIn("could not be run", why)

    def test_crontab_header_noise_is_not_drift_but_a_changed_schedule_is(self):
        """Both halves, because a normaliser is a place to hide a real change.

        `crontab` regenerates three header comments carrying an install
        timestamp on every install, so comparing them raw would cry drift after
        a no-op reinstall. Muffling them must not also muffle the schedule.
        """
        installed = ("# DO NOT EDIT THIS FILE - edit the master and reinstall.\n"
                     "# (- installed on Tue Jul 28 05:27:14 2026)\n"
                     "# (Cron version -- $Id: crontab.c,v 2.13 ...)\n"
                     "*/5 * * * * /usr/local/bin/auto-stop.sh\n")
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            dep, repo = _scratch_pair(
                tmp, "*/5 * * * * /usr/local/bin/auto-stop.sh\n", installed,
                normalize="crontab")
            self.assertEqual(reg.MATCH, reg.compare(dep, repo).state,
                             "regenerated crontab headers were read as drift")
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            dep, repo = _scratch_pair(
                tmp, "*/5 * * * * /usr/local/bin/auto-stop.sh\n",
                installed.replace("*/5", "*/1"), normalize="crontab")
            self.assertEqual(reg.DRIFT, reg.compare(dep, repo).state,
                             "the schedule changed from every 5 minutes to "
                             "every 1 and the normaliser swallowed it")

    def test_the_env_override_that_makes_planting_possible_actually_redirects(self):
        """The door the controls above use, asserted directly.

        If the override silently did nothing, every planted-drift control would
        be reading the REAL installed file and passing for the wrong reason --
        the exact shape L-84 warns about: an instrument seen to fire, but not
        where anyone thought it was looking.
        """
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            planted = tmp / "planted.sh"
            planted.write_text("echo planted\n")
            dep = reg.DEPLOYMENTS[0]
            os.environ[dep.env_override] = str(planted)
            try:
                text, why = reg.installed_text(dep)
            finally:
                os.environ.pop(dep.env_override, None)
        self.assertEqual("echo planted\n", text,
                         f"{dep.env_override} did not redirect the read")


class NoTrackedGhostBesideARegisteredArtifactTests(unittest.TestCase):
    """The rule `scripts/auto-stop.sh.proposed` earned.

    A committed staging copy beside a registered artifact is what made
    2026-07-30 invisible for thirteen days: the tree looks repaired, and a
    reader who diffs `scripts/auto-stop.sh.proposed` against the backup -- the
    natural pair to reach for -- learns nothing about what is running.
    """

    def test_no_registered_artifact_has_a_tracked_staging_sibling(self):
        ghosts = reg.staging_ghosts()
        self.assertEqual(
            [], ghosts,
            "tracked staging cop(ies) of a registered artifact. A fix that "
            "lives only in the repo cannot be assumed to be running, and a "
            "file named like a pending one is worse than none: it makes the "
            "tree look repaired. Install it and delete it, or delete it -- git "
            "history keeps it either way:\n"
            + "\n".join(f"{g} (beside {a})" for g, a in ghosts))

    def test_the_ghost_rule_is_shown_to_fire(self):
        """Planted, because the live assertion above passes by being empty.

        An empty list is what a broken detector returns too.
        """
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            (repo / "scripts").mkdir(parents=True)
            (repo / "scripts" / "thing.sh").write_text("echo real\n")
            (repo / "scripts" / "thing.sh.proposed").write_text("echo ghost\n")
            (repo / "scripts" / "thing.sh.notes.md").write_text("not a ghost\n")
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(["git", "add", "--", "scripts"], cwd=repo,
                           check=True)
            dep = reg.Deployment(
                name="scratch", tracked="scripts/thing.sh",
                source="/nowhere", why="a control", reinstall="none")
            ghosts = reg.staging_ghosts(repo, (dep,))
        self.assertEqual(
            [("scripts/thing.sh.proposed", "scripts/thing.sh")], ghosts,
            "the ghost rule did not catch a planted `.proposed` sibling, or it "
            f"caught a file that is not one; got {ghosts}")


if __name__ == "__main__":
    unittest.main()
