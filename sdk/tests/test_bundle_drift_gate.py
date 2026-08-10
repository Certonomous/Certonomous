"""The bundle-drift check must FAIL, not WARN, when the bundle is absent.

WHY. `check_bundle_drift` compares the extracted laptop bundle against the
tree. It is the drift detector for `dist/certonomous-demo.zip` -- the only
artifact that leaves this box. On 2026-08-10 the shipped bundle was found ten
days stale, carrying a round-4 hero, a round-3 KPI and a prior-art sentence
struck five days earlier; the check had been reporting all three by name and
its output was not consumed.

The absence branch is the dangerous one. If the bundle directory is missing the
check returned WARN "no bundle to compare" -- but an absent bundle does not mean
"nothing to say", it means THE DETECTOR IS OFF. Silence read as success, in the
one artifact an outsider can see. That is the class this lab spent 2026-08-10
closing everywhere else (L-45; the lever echo that never fired; the mesh gate
that minted a clean certificate from a crash).

These tests pin the gate in both directions: absent must FAIL, and a matching
bundle must still PASS, so the fix cannot be "make it fail always".
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "self_audit_under_test", REPO / "scripts" / "self_audit.py")
sa = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = sa
_SPEC.loader.exec_module(sa)


class BundleAbsenceIsAFailureTests(unittest.TestCase):
    def setUp(self):
        self._repo = sa.REPO

    def tearDown(self):
        sa.REPO = self._repo

    def test_absent_bundle_FAILS_because_an_absent_detector_is_not_good_news(self):
        """The regression this file exists for. Fails against the WARN code."""
        with tempfile.TemporaryDirectory() as tmp:
            sa.REPO = Path(tmp)          # a tree with no dist/certonomous-demo
            result = sa.check_bundle_drift()
        self.assertEqual(
            result.status, sa.FAIL,
            "an absent bundle means the drift detector is OFF, which must not "
            f"be reported as a warning; got {result.status}")

    def test_the_message_says_the_detector_is_off_not_merely_uninformative(self):
        with tempfile.TemporaryDirectory() as tmp:
            sa.REPO = Path(tmp)
            result = sa.check_bundle_drift()
        blob = (result.summary + " " + " ".join(result.detail)).lower()
        self.assertTrue(
            any(w in blob for w in ("detector", "off", "not checked")),
            "the absence message must say the check is not running, not just "
            f"that a file is missing; got {result.summary!r}")

    @staticmethod
    def _fixture(root: Path, *, drift: bool = False, bundle: bool = True):
        """A minimal tree plus a bundle built from it.

        Hermetic on purpose. An earlier version of this test compared the LIVE
        repo bundle, and it failed for a reason that was not a bug: another
        family committed `exec_bits.py` between the rebuild and the test run,
        so the tree had legitimately moved. A test whose control arm depends on
        no other agent committing is a test that reports other people's work as
        its own failure.
        """
        src = root / "sdk" / "chief_engineer"
        src.mkdir(parents=True)
        (src / "server.py").write_text("print('control room')\n")
        pages = root / "demo-output" / "website"
        (pages / "wall").mkdir(parents=True)
        for rel in ("closure.html", "benchmarks.html", "wall/wall.html"):
            (pages / rel).write_text(f"<html>{rel}</html>\n")
        if not bundle:
            return
        out = root / "dist" / "certonomous-demo"
        (out / "sdk" / "chief_engineer").mkdir(parents=True)
        (out / "sdk" / "chief_engineer" / "server.py").write_text(
            "print('STALE')\n" if drift else "print('control room')\n")
        (out / "site" / "wall").mkdir(parents=True)
        for rel, dst in (("closure.html", "site/closure.html"),
                         ("benchmarks.html", "site/benchmarks.html"),
                         ("wall/wall.html", "site/wall/wall.html")):
            (out / dst).write_text(f"<html>{rel}</html>\n")

    def test_a_matching_bundle_still_PASSES(self):
        """The fix must not be 'fail always'."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._fixture(root)
            sa.REPO = root
            self.assertEqual(sa.check_bundle_drift().status, sa.PASS)

    def test_a_drifted_bundle_still_FAILS(self):
        """The behaviour that already worked must survive the change."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._fixture(root, drift=True)
            sa.REPO = root
            self.assertEqual(sa.check_bundle_drift().status, sa.FAIL)


if __name__ == "__main__":
    unittest.main()
