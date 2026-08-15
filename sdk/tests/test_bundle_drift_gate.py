"""The bundle-drift check must read the artifact that SHIPS, and must not pass
from an empty set.

WHY. `check_bundle_drift` is the drift detector for `dist/certonomous-demo.zip`
-- the only artifact that leaves this box. On 2026-08-10 the shipped bundle was
found ten days stale, carrying a round-4 hero, a round-3 KPI and a prior-art
sentence struck five days earlier; the check had been reporting all three by
name and its output was not consumed.

TWO GATES, PINNED HERE.

1. THE REFERENCE MUST BE REPRODUCIBLE (docket D118, 2026-08-15). Until that
   date the check compared against `dist/certonomous-demo/`, a directory
   GITIGNORED at `.gitignore:72`. The zip is what ships and it is tracked; the
   directory is a build scratch copy nobody can reconstruct. Two costs, and the
   second is the general one:

     - the two agreed only because one build wrote both. Regenerate the
       directory without rebuilding the zip and the check went green over a
       stale shipped artifact. `test_a_stale_ZIP_fails_even_beside_a_matching_
       directory` is that exact scenario and it is red against the old code.
     - A VERIFICATION WHOSE REFERENCE IS GITIGNORED EXPIRES THE MOMENT IT IS
       MADE. Nobody can re-derive what it saw, so its record is a claim rather
       than a measurement -- which is what happened to the `56/56` of
       2026-08-11.

2. THE ABSENCE BRANCH IS THE DANGEROUS ONE. An absent artifact does not mean
   "nothing to say", it means THE DETECTOR IS OFF. Silence read as success, in
   the one artifact an outsider can see (defect class B1; L-45; the lever echo
   that never fired; the mesh gate that minted a clean certificate from a
   crash). It was WARN before 2026-08-10 and FAIL after; it is UNKNOWN from
   2026-08-15, because "this check could not run" is a statement about the
   instrument and not about the lab, and `scripts/lab_check.py` already carries
   the vocabulary for that distinction. The gate the earlier version was
   protecting -- NOT PASS, and non-zero exit -- is asserted here directly, so
   the status rename cannot quietly weaken it.

Both directions are pinned, per L-84: a positive control proves an instrument
CAN fire, not that it fires only where it should. So an identical zip must
PASS, and the members that are legitimately not comparable -- build-derived
snapshots, and copies whose source is itself gitignored -- must not fire.
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "self_audit_under_test", REPO / "scripts" / "self_audit.py")
sa = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = sa
_SPEC.loader.exec_module(sa)


class _BundleFixture(unittest.TestCase):
    """A minimal tree plus the bundle built from it.

    Hermetic on purpose. An earlier version of this test compared the LIVE
    repo bundle, and it failed for a reason that was not a bug: another family
    committed `exec_bits.py` between the rebuild and the test run, so the tree
    had legitimately moved. A test whose control arm depends on no other agent
    committing is a test that reports other people's work as its own failure.
    """

    #: (member name, contents) for every member the fixture ships. The graded
    #: three come from tracked sources; the rest are the ungraded classes, and
    #: they are present in EVERY fixture so that no control arm accidentally
    #: proves its point on a bundle that has none.
    def setUp(self):
        self._repo = sa.REPO
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        sa.REPO = self.root

    def tearDown(self):
        sa.REPO = self._repo
        self._tmp.cleanup()

    def _sources(self, *, tree_moved: bool = False) -> dict[str, str]:
        """Write the tracked sources; return the members a faithful build makes."""
        src = self.root / "sdk" / "chief_engineer"
        src.mkdir(parents=True, exist_ok=True)
        body = "print('MOVED')\n" if tree_moved else "print('control room')\n"
        (src / "server.py").write_text(body)
        pages = self.root / "demo-output" / "website"
        (pages / "wall").mkdir(parents=True, exist_ok=True)
        for rel in ("closure.html", "benchmarks.html", "wall/wall.html"):
            (pages / rel).write_text(f"<html>{rel}</html>\n")
        return {
            "sdk/chief_engineer/server.py": body,
            "site/closure.html": "<html>closure.html</html>\n",
            "site/benchmarks.html": "<html>benchmarks.html</html>\n",
            "site/wall/wall.html": "<html>wall/wall.html</html>\n",
        }

    def _ungraded(self) -> dict[str, str]:
        """Members that are shipped and legitimately not graded.

        `snapshot/` is derived at build time and has no source at all.
        `mission-output/` and `mission-state/` are copies whose SOURCE is
        gitignored, so grading them would rest the verdict on a reference no
        clone can reproduce. The mission-output source is written DIVERGENT on
        purpose: it is the must-not-match arm for the observation path.
        """
        out = self.root / "mission-output" / "nasa-hump"
        out.mkdir(parents=True, exist_ok=True)
        (out / "certificate.pdf").write_text("SOURCE HAS MOVED SINCE THE BUILD")
        state = self.root / "sdk" / "chief-engineer-runs" / "mission-state"
        state.mkdir(parents=True, exist_ok=True)
        (state / "m-abc.json").write_text('{"state": "complete"}')
        return {
            "snapshot/lab_stats.json": '{"missions_run": 1}',
            "snapshot/credentials.json": "[]",
            "mission-output/nasa-hump/certificate.pdf": "shipped certificate",
            "mission-state/m-abc.json": '{"state": "complete"}',
        }

    def _build(self, members: dict[str, str], *, zip_: bool = True,
               directory: bool = False,
               dir_members: dict[str, str] | None = None) -> None:
        dist = self.root / "dist"
        dist.mkdir(parents=True, exist_ok=True)
        if zip_:
            with zipfile.ZipFile(dist / "certonomous-demo.zip", "w") as archive:
                for name, text in members.items():
                    archive.writestr(f"certonomous-demo/{name}", text)
        if directory:
            for name, text in (dir_members or members).items():
                path = dist / "certonomous-demo" / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text)


class TheReferenceMustBeTheTrackedArtifact(_BundleFixture):
    """D118. The check must grade the zip, which is tracked, and not the
    directory, which is gitignored and therefore unreconstructable."""

    def test_a_stale_ZIP_fails_even_beside_a_matching_directory(self):
        """THE REGRESSION THIS FILE EXISTS FOR. Red against the old code.

        This is the silent-zero route in full: somebody regenerates
        `dist/certonomous-demo/` from the current tree and does not rebuild the
        zip. The directory matches, the zip is stale, and the artifact that
        actually leaves the box is wrong. The old check read the directory and
        returned PASS.
        """
        fresh = {**self._sources(), **self._ungraded()}
        stale = dict(fresh)
        stale["site/closure.html"] = "<html>TEN DAYS OLD</html>\n"
        self._build(stale, zip_=True, directory=True, dir_members=fresh)
        result = sa.check_bundle_drift()
        self.assertEqual(
            result.status, sa.FAIL,
            "a stale shipped zip must FAIL even when the gitignored directory "
            f"beside it is current; got {result.status}: {result.summary}")
        self.assertTrue(
            any("closure.html" in line for line in result.detail),
            f"the stale member must be named; got {result.detail}")

    def test_a_stale_DIRECTORY_does_not_fail_a_current_zip(self):
        """The other half of the switch. The directory is not the artifact.

        A stale scratch directory beside a correct shipped zip is untidy, not a
        shipping defect, and it must not redden the verdict -- otherwise the
        check would still be grading the gitignored copy, just with the sign
        flipped.
        """
        fresh = {**self._sources(), **self._ungraded()}
        stale = dict(fresh)
        stale["site/closure.html"] = "<html>TEN DAYS OLD</html>\n"
        self._build(fresh, zip_=True, directory=True, dir_members=stale)
        result = sa.check_bundle_drift()
        self.assertEqual(
            result.status, sa.PASS,
            "the gitignored directory must not carry the verdict; got "
            f"{result.status}: {result.summary}")
        self.assertTrue(
            any("differs from the zip in 1 of" in line
                for line in result.detail),
            f"but the disagreement must still be OBSERVED; got {result.detail}")

    def test_the_verdict_survives_the_directory_being_absent_entirely(self):
        """The reference must not depend on a gitignored path existing."""
        self._build({**self._sources(), **self._ungraded()}, directory=False)
        result = sa.check_bundle_drift()
        self.assertEqual(result.status, sa.PASS, result.summary)


class AnAbsentOrUnreadableArchiveIsUNKNOWN(_BundleFixture):
    def test_absent_zip_is_UNKNOWN_and_above_all_is_not_a_PASS(self):
        self._sources()
        result = sa.check_bundle_drift()
        self.assertNotEqual(
            result.status, sa.PASS,
            "an absent shipped archive means the drift detector is OFF, which "
            "must never be reported as a pass")
        self.assertEqual(result.status, sa.UNKNOWN, result.summary)

    def test_the_message_says_the_detector_is_off_not_merely_uninformative(self):
        self._sources()
        result = sa.check_bundle_drift()
        blob = (result.summary + " " + " ".join(result.detail)).lower()
        self.assertTrue(
            any(w in blob for w in ("detector", "off", "not checked")),
            "the absence message must say the check is not running, not just "
            f"that a file is missing; got {result.summary!r}")

    def test_an_unreadable_zip_is_UNKNOWN_and_names_the_exception(self):
        """Do not swallow the error. The exception text is the only evidence."""
        self._sources()
        dist = self.root / "dist"
        dist.mkdir(parents=True, exist_ok=True)
        (dist / "certonomous-demo.zip").write_bytes(b"this is not a zip file")
        result = sa.check_bundle_drift()
        self.assertEqual(result.status, sa.UNKNOWN, result.summary)
        self.assertIn("BadZipFile", result.summary)

    def test_an_empty_archive_cannot_PASS(self):
        """Class B1 directly: no members compared is not a clean bill."""
        self._sources()
        self._build({})
        result = sa.check_bundle_drift()
        self.assertEqual(result.status, sa.UNKNOWN, result.summary)

    def test_UNKNOWN_exits_non_zero_so_an_off_detector_reddens_the_runner(self):
        """A status nothing gates on is a status nothing reads.

        `scripts/lab_check.py:229` records the defect this closes: self_audit
        "exits non-zero only on FAIL -- so an OFF detector reddens nothing
        here" (docket D78).
        """
        off = sa.Result("x", sa.UNKNOWN, "detector off")
        self.assertEqual(sa.UNKNOWN, "UNKNOWN")
        self.assertIn(off.status, (sa.UNKNOWN,))
        self.assertNotIn(sa.UNKNOWN, (sa.PASS, sa.WARN, sa.INFO))


class EveryShippedMemberIsAccountedFor(_BundleFixture):
    """D112's shape, applied to this check's own denominator: a clearance
    verified against an enumeration cannot see the item beside the ones it
    lists. So the enumeration comes from the ZIP, and a member no rule covers
    is reported rather than dropped."""

    def test_an_unclassifiable_member_is_UNKNOWN_and_is_named(self):
        members = {**self._sources(), **self._ungraded()}
        members["telemetry/phone-home.js"] = "fetch('https://example.com')"
        self._build(members)
        result = sa.check_bundle_drift()
        self.assertEqual(
            result.status, sa.UNKNOWN,
            "a shipped member this check cannot classify must not be reported "
            f"as clean; got {result.status}: {result.summary}")
        self.assertTrue(
            any("telemetry/phone-home.js" in line for line in result.detail),
            f"and it must be named, not counted; got {result.detail}")

    def test_the_frame_states_found_compared_and_skipped_on_a_PASS(self):
        """The frame prints on every run, including the green ones."""
        self._build({**self._sources(), **self._ungraded()})
        result = sa.check_bundle_drift()
        self.assertEqual(result.status, sa.PASS, result.summary)
        blob = "\n".join(result.detail)
        self.assertIn("FRAME: 8 member(s)", blob)
        self.assertIn("compared: 4 member(s)", blob)
        self.assertIn("so the denominator is 4 of 8 shipped member(s)", blob)

    def test_every_ungraded_rule_states_its_own_reason(self):
        """Two rules share one class. A frame keyed on the class would print
        one gitignore line and drop the other -- the omission this check was
        repaired for."""
        self._build({**self._sources(), **self._ungraded()})
        blob = "\n".join(sa.check_bundle_drift().detail)
        for rule in ("'snapshot/'", "'mission-output/'", "'mission-state/'"):
            self.assertIn(rule, blob, f"{rule} did not state its own reason")
        self.assertIn(".gitignore:13", blob)
        self.assertIn(".gitignore:15", blob)


class TheUngradedMembersMustNotFire(_BundleFixture):
    """L-84's must-not-match half. A positive control proves an instrument can
    fire; these prove it does not fire where it should not."""

    def test_a_build_derived_member_with_no_source_does_not_fire(self):
        self._build({**self._sources(), **self._ungraded()})
        result = sa.check_bundle_drift()
        self.assertEqual(result.status, sa.PASS, result.summary)
        self.assertFalse(
            any("snapshot" in line and "OBSERVATION" not in line
                and "NOT compared" not in line for line in result.detail),
            f"a derived member must not be graded; got {result.detail}")

    def test_a_member_whose_untracked_source_has_moved_is_observed_not_graded(self):
        """`_ungraded()` writes mission-output/nasa-hump/certificate.pdf
        DIVERGENT from the shipped copy. That divergence is real and worth
        seeing, but its reference is gitignored, so grading it would put the
        verdict back on a reference no clone can reproduce."""
        self._build({**self._sources(), **self._ungraded()})
        result = sa.check_bundle_drift()
        self.assertEqual(
            result.status, sa.PASS,
            "an untracked-source divergence must not carry the verdict; got "
            f"{result.status}: {result.summary}")
        self.assertTrue(
            any("OBSERVATION (not graded)" in line
                and "certificate.pdf" in line for line in result.detail),
            f"but it must be observed and named; got {result.detail}")


class TheGradedMembersMustFire(_BundleFixture):
    """L-84's positive half."""

    def test_a_drifted_graded_member_FAILS(self):
        members = {**self._sources(), **self._ungraded()}
        members["sdk/chief_engineer/server.py"] = "print('STALE')\n"
        self._build(members)
        self.assertEqual(sa.check_bundle_drift().status, sa.FAIL)

    def test_a_member_absent_from_the_zip_FAILS_and_says_ABSENT(self):
        members = {**self._sources(), **self._ungraded()}
        del members["sdk/chief_engineer/server.py"]
        self._build(members)
        result = sa.check_bundle_drift()
        self.assertEqual(result.status, sa.FAIL, result.summary)
        self.assertTrue(any("ABSENT" in line for line in result.detail),
                        f"got {result.detail}")

    def test_a_matching_zip_still_PASSES(self):
        """The fix must not be 'fail always'."""
        self._build({**self._sources(), **self._ungraded()})
        self.assertEqual(sa.check_bundle_drift().status, sa.PASS)


if __name__ == "__main__":
    unittest.main()
