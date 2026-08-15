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
* A DIVERGENCE THIS LAB MAY NOT REPAIR ITSELF is DECLARED, never silenced
  (D65, 2026-08-14). `/usr/local/bin/auto-stop.sh` is the box's power control
  and docket A4 puts it with Katie and Sanaa, so a reviewed fix to it waits in
  the tree. `PendingInstall` carries the reason, the owner, an expiry, and the
  sha256 of what is expected to still be installed; the pair reads PENDING
  inside that window and FAILS outside it. Every one of those fragilities is
  planted and shown to fire in `ThePendingWaiverIsShownToBeFragileTests`,
  because a waiver never seen to fail is a mute button with paperwork.
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
                  normalize: str = "text",
                  pending: "reg.PendingInstall | None" = None
                  ) -> tuple[reg.Deployment, Path]:
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
        pending=pending,
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


class PendingInstallWaiversTests(unittest.TestCase):
    """The declared-divergence door, live and planted (D65, 2026-08-14).

    Some installed artifacts are not the fleet's to write --
    `/usr/local/bin/auto-stop.sh` is the box's power control and docket row A4
    puts it with Katie and Sanaa. So a reviewed repair can sit in the tree,
    legitimately uninstalled, and the drift check is RIGHT to see a difference.
    The waiver is how that is declared without silencing the check that exists
    because a repaired gate once sat uninstalled for thirteen days.

    It has to be fragile in three specific ways or it is just a mute button,
    and all three are planted below: it expires, it pins the hash of what the
    installed copy is expected to still be, and it is reported once it has
    stopped excusing anything.
    """

    @classmethod
    def setUpClass(cls):
        cls.findings = reg.report()

    def test_every_pending_install_waiver_is_visible_in_the_run(self):
        """A green suite must not hide that the box runs an older reviewed copy.

        This is the whole hazard of allowing the waiver at all: the machine is
        knowingly running something the tree has already superseded, and the
        only defence against that becoming normal is that it is stated on every
        run and that it expires.
        """
        for f in self.findings:
            if f.state == reg.PENDING:
                print(f"\n[installed-vs-tracked] PENDING INSTALL "
                      f"{f.dep.name}: {f.dep.tracked} -> "
                      f"{f.dep.installed_where}\n         {f.detail.strip()}")
        for dep in reg.DEPLOYMENTS:
            if dep.pending is None:
                continue
            with self.subTest(dep.name):
                self.assertTrue(dep.pending.reason.strip(),
                                "a waiver with no reason is a mute button")
                self.assertTrue(dep.pending.owner.strip(),
                                "a waiver must name who can lift it")
                self.assertRegex(dep.pending.expires, r"^\d{4}-\d{2}-\d{2}$",
                                 "a waiver must expire on a date")
                self.assertRegex(dep.pending.installed_sha256, r"^[0-9a-f]{64}$",
                                 "a waiver must pin what is actually running")

    def test_no_pending_install_waiver_has_quietly_stopped_excusing_anything(self):
        stale = reg.stale_waivers(self.findings)
        self.assertEqual(
            [], stale,
            "pending-install waiver(s) left behind after the fix was "
            "installed. A waiver sitting on a pair that now matches would "
            "meet the NEXT real divergence already switched off:\n"
            + "\n".join(f"{n}: {w}" for n, w in stale))


class ThePendingWaiverIsShownToBeFragileTests(unittest.TestCase):
    """Planted. A waiver never seen to fail is indistinguishable from a skip."""

    _SHA = "9f" * 32

    def _waiver(self, expires: str, sha: str) -> reg.PendingInstall:
        return reg.PendingInstall(reason="a control", owner="nobody",
                                  expires=expires, installed_sha256=sha)

    def test_a_live_waiver_over_the_exact_pinned_content_reads_as_pending(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            installed = "echo OLD\n"
            sha = reg._sha(reg._normalize("text", installed))
            dep, repo = _scratch_pair(
                tmp, "echo NEW\n", installed,
                pending=self._waiver("2099-01-01", sha))
            finding = reg.compare(dep, repo)
        self.assertEqual(reg.PENDING, finding.state, finding.detail)
        self.assertFalse(finding.is_failure,
                         "a declared, dated, hash-pinned divergence inside its "
                         "window must not fail the suite")
        self.assertIn("2099-01-01", finding.detail,
                      "the pending report must say when the waiver lapses")

    def test_an_expired_waiver_fails_and_names_itself(self):
        """Ageing must not be a way to go quiet -- that IS the 2026-07-30 bug."""
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            installed = "echo OLD\n"
            sha = reg._sha(reg._normalize("text", installed))
            dep, repo = _scratch_pair(
                tmp, "echo NEW\n", installed,
                pending=self._waiver("2000-01-01", sha))
            finding = reg.compare(dep, repo)
        self.assertEqual(reg.DRIFT, finding.state)
        self.assertTrue(finding.is_failure)
        self.assertIn("EXPIRED", finding.detail)

    def test_a_waiver_does_not_cover_an_installed_copy_it_was_not_written_for(self):
        """The narrowness that separates a waiver from an exemption.

        If someone edits the installed copy by hand, the waiver must not carry
        that too -- otherwise declaring one divergence licenses every later one
        on the same pair, which is a hole in the exact check D53 built.
        """
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            dep, repo = _scratch_pair(
                tmp, "echo NEW\n", "echo SOMETHING ELSE ENTIRELY\n",
                pending=self._waiver("2099-01-01", self._SHA))
            finding = reg.compare(dep, repo)
        self.assertEqual(reg.DRIFT, finding.state,
                         "a waiver excused an installed copy it never pinned")
        self.assertTrue(finding.is_failure)
        self.assertIn("NOT the version this pending-install waiver",
                      finding.detail)

    def test_a_waiver_on_a_pair_that_now_matches_is_reported_stale(self):
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            dep, repo = _scratch_pair(
                tmp, "echo same\n", "echo same\n",
                pending=self._waiver("2099-01-01", self._SHA))
            findings = [reg.compare(dep, repo)]
        self.assertEqual(reg.MATCH, findings[0].state)
        self.assertEqual(1, len(reg.stale_waivers(findings)),
                         "an installed fix left its waiver behind unreported")

    def test_a_pending_pair_still_counts_as_compared(self):
        """Reach must not shrink because a difference was declared.

        A PENDING pair was read, diffed and hashed. If it dropped out of
        `reached()`, the box that runs the gate could skip its own gate and
        `test_the_box_that_runs_the_gate_must_compare_it` would go green on a
        machine nobody had checked.
        """
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            installed = "echo OLD\n"
            sha = reg._sha(reg._normalize("text", installed))
            dep, repo = _scratch_pair(
                tmp, "echo NEW\n", installed,
                pending=self._waiver("2099-01-01", sha))
            findings = [reg.compare(dep, repo)]
        self.assertEqual(["scratch pair"], reg.reached(findings))


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


class EveryFindingTheRunPrintsReachesTheExitCode(unittest.TestCase):
    """V15 round 7 F6 / docket D95, and both halves of it (L-84).

    `main()` used to end `return 1 if any(f.is_failure ...) else 0`, so GHOST
    and STALE were computed, printed, and dropped. A finding that reaches
    stdout and not the exit code is invisible to every caller that composes
    this module -- `lab_check.py` among them, which reported
    `[PASS] scripts/installed_registry.py`.

    The classes that must NOT fail are asserted here too, in the same place, so
    that widening this rule later has to argue with a test rather than with a
    comment: ABSENT and PENDING are declared states with stated reasons, and a
    registry that fails on a laptop with no root crontab is a registry nobody
    runs on a laptop.
    """

    DEP = None

    def setUp(self):
        self.DEP = reg.Deployment(
            name="scratch pair", tracked="scripts/thing.sh",
            source="/nowhere", why="a control", reinstall="none")

    def _f(self, state, dep=None):
        return reg.Finding(dep or self.DEP, state, "detail")

    def test_a_clean_run_has_no_failures(self):
        """The must-not-match half."""
        self.assertEqual(reg.failures([self._f(reg.MATCH)], [], []), [])

    def test_drift_and_a_dangling_tracked_side_fail(self):
        self.assertEqual(len(reg.failures([self._f(reg.DRIFT)], [], [])), 1)
        self.assertEqual(len(reg.failures([self._f(reg.DANGLING)], [], [])), 1)

    def test_a_tracked_ghost_reaches_the_exit_code(self):
        bad = reg.failures([self._f(reg.MATCH)],
                           [("scripts/thing.sh.proposed", "scripts/thing.sh")],
                           [])
        self.assertEqual(len(bad), 1, bad)
        self.assertIn("GHOST", bad[0])

    def test_a_stale_waiver_reaches_the_exit_code(self):
        bad = reg.failures([self._f(reg.MATCH)], [],
                           [("scratch pair", "the fix was installed")])
        self.assertEqual(len(bad), 1, bad)
        self.assertIn("STALE", bad[0])

    def test_main_ACTUALLY_consumes_the_rule_and_not_just_prints_it(self):
        """The pin that matters: `failures()` being right is worth nothing if
        `main()` still returns its own answer. Driven through the shipped entry
        point, with one ghost planted into the sweep and nothing else changed.
        """
        real_ghosts = reg.staging_ghosts
        try:
            reg.staging_ghosts = lambda *a, **k: [
                ("scripts/thing.sh.proposed", "scripts/thing.sh")]
            self.assertEqual(
                reg.main(), 1,
                "a GHOST was printed by the run and the process still exited "
                "0, so no caller composing this module can see it")
        finally:
            reg.staging_ghosts = real_ghosts
        # ...and with the sweep honest again, the live tree's own answer.
        self.assertEqual(reg.main(), 0 if not reg.staging_ghosts() else 1)

    def test_absence_and_a_declared_pending_install_do_NOT_fail(self):
        """The line this repair must not cross. Both are argued at length in
        `installed_registry`'s docstring; asserting them here means widening
        the rule has to come with a reason."""
        self.assertEqual(reg.failures([self._f(reg.ABSENT)], [], []), [])
        self.assertEqual(reg.failures([self._f(reg.PENDING)], [], []), [])


if __name__ == "__main__":
    unittest.main()
