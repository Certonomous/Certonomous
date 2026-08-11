"""A withdrawal that could not happen may not be published as a withdrawal.

WHY. Docket B2: every gate and parser answers "did the check run?" before
"what did it find?", with a third verdict for unknown. The rung opened on
V16's own guard, where a per-surface `except Exception` left the STATUS green
and reported the skip only in the frame line.

THE DEFECT THESE TESTS PIN is the same shape one step over, in the acts rather
than in a guard. Every workflow in this package opened its certificate block
with

    try:
        cert_path.unlink()
    except OSError:
        pass

and then published, with no condition attached, "The previous run's
certificate is withdrawn, so nothing out of date is served." Two outcomes were
modelled -- removed, and nothing-there -- and the third was not: the page is
there and CANNOT be removed. On that path the sentence is false, and it is
false on a camera surface.

THE INJECTION THAT SETTLED IT, and it is the one `test_a_refused_unlink_is_not
_published_as_a_withdrawal` runs: plant a certificate from an earlier mission,
make `Path.unlink` raise `PermissionError`, make `build_certificate_v2` raise
so no new page lands on top, and run `valve_study.main`. Before the fix the
transcript read "The previous run's certificate is withdrawn, so nothing out of
date is served." while the earlier mission's file sat on disk BYTE FOR BYTE
unchanged. That is a published claim of an action that did not occur.

WHY THE MIDDLE CASE MATTERS, and why the two-valued form looked right for so
long: on almost every run there is no previous page at all, `unlink` raises
`FileNotFoundError`, and swallowing it IS correct -- nothing stale is served.
A fix that turned every miss into a warning would be wrong, would be switched
off within a week, and would then be guarding nothing. So
`TheThreeOutcomesTests` pins all three, and every negative here carries the
positive control that the clean sentence still gets published when the
withdrawal really did happen.

NOT COVERED, stated rather than discovered later: this checks what the act
PUBLISHES, not whether the web server would in fact serve the stale page, and
it does not cover the five acts in this package that call `unlink` unguarded
behind an `exists()` check -- those raise out of `main` instead of swallowing,
which is a different failure and is filed, not fixed, here.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
if str(REPO / "sdk") not in sys.path:
    sys.path.insert(0, str(REPO / "sdk"))

import workflows  # noqa: E402
from workflows import WITHDRAWN_SENTENCE, withdraw_certificate  # noqa: E402

STALE = b"%PDF-1.4 CERTIFICATE FROM AN EARLIER MISSION\n"


class TheThreeOutcomesTests(unittest.TestCase):
    """Evidence FOR: the helper distinguishes three outcomes, not two."""

    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self.path = Path(self._dir.name) / "certificate.pdf"

    def tearDown(self):
        self._dir.cleanup()

    def test_a_page_that_was_there_and_is_gone_is_withdrawn(self):
        self.path.write_bytes(STALE)
        withdrawn, sentence = withdraw_certificate(self.path)
        self.assertTrue(withdrawn)
        self.assertEqual(WITHDRAWN_SENTENCE, sentence)
        self.assertFalse(self.path.exists())

    def test_no_page_to_withdraw_is_also_a_withdrawal(self):
        """The common case, and the reason the two-valued form survived. If
        this ever fails the fix has become 'warn on every run', which is how a
        guard gets switched off."""
        self.assertFalse(self.path.exists())
        withdrawn, sentence = withdraw_certificate(self.path)
        self.assertTrue(withdrawn)
        self.assertEqual(WITHDRAWN_SENTENCE, sentence)

    def test_a_page_that_could_not_be_removed_is_NOT_a_withdrawal(self):
        """The third outcome, which did not exist before this rung."""
        self.path.write_bytes(STALE)

        def refuse(self_path, *args, **kwargs):
            raise PermissionError(13, "injected: read-only medium")

        with mock.patch.object(Path, "unlink", refuse):
            withdrawn, sentence = withdraw_certificate(self.path)
        self.assertFalse(withdrawn)
        self.assertNotEqual(WITHDRAWN_SENTENCE, sentence)
        self.assertIn("COULD NOT be withdrawn", sentence)
        self.assertIn("PermissionError", sentence)
        self.assertIn("out-of-date page may still be served", sentence)
        self.assertTrue(self.path.exists(), "the injection did not bite")

    def test_a_non_OSError_is_also_not_a_silent_success(self):
        """A boundary, not a list of exception types. The guard one layer up
        from this one was fixed twice by adding an exception class and needed
        a third; anything the removal raises becomes a stated failure."""

        def explode(self_path, *args, **kwargs):
            raise RuntimeError("injected: something no one listed")

        self.path.write_bytes(STALE)
        with mock.patch.object(Path, "unlink", explode):
            withdrawn, sentence = withdraw_certificate(self.path)
        self.assertFalse(withdrawn)
        self.assertIn("RuntimeError", sentence)

    def test_it_does_not_raise_on_any_of_them(self):
        """A certificate must never take down a good mission -- which is the
        rule that made swallowing look correct, and the reason the failure has
        to be SAID instead."""
        for setup in (lambda: None,
                      lambda: self.path.write_bytes(STALE)):
            setup()
            withdraw_certificate(self.path)          # must not raise


class TheActPublishesWhatHappenedTests(unittest.TestCase):
    """Evidence FOR: the injection that produced the false claim no longer
    produces it, run end to end through a real act."""

    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self._root = Path(self._dir.name)
        import os
        os.environ["CERTONOMOUS_SWEEP_PACE_MS"] = "0"
        from workflows import valve_study
        self.valve_study = valve_study
        self._real_root = valve_study.OUT_ROOT
        valve_study.OUT_ROOT = self._root
        self.out = self._root / "valve-study"
        self.out.mkdir(parents=True)
        self.stale = self.out / "certificate.pdf"

    def tearDown(self):
        self.valve_study.OUT_ROOT = self._real_root
        self._dir.cleanup()

    def _run(self, refuse_unlink: bool):
        real_unlink = Path.unlink

        def maybe_refuse(path, *args, **kwargs):
            if refuse_unlink and path.name == "certificate.pdf":
                raise PermissionError(13, "injected: read-only medium")
            return real_unlink(path, *args, **kwargs)

        with mock.patch.object(Path, "unlink", maybe_refuse), \
                mock.patch("chief_engineer.certificate.build_certificate_v2",
                           side_effect=RuntimeError("injected: renderer down")):
            rc = self.valve_study.main(
                request="minimise valve pressure loss over the cardiac cycle")
        return rc, (self.out / "transcript.txt").read_text(encoding="utf-8")

    def test_a_refused_unlink_is_not_published_as_a_withdrawal(self):
        """THE INJECTION. Before the fix this transcript carried the clean
        sentence while the earlier mission's page sat on disk unchanged."""
        self.stale.write_bytes(STALE)
        rc, transcript = self._run(refuse_unlink=True)
        self.assertEqual(0, rc, "a certificate took down a good mission")
        self.assertTrue(self.stale.exists() and
                        self.stale.read_bytes() == STALE,
                        "the injection did not bite: the stale page is gone, "
                        "so this test proves nothing")
        self.assertNotIn(WITHDRAWN_SENTENCE, transcript,
                         "the act published a withdrawal that did not happen")
        self.assertIn("COULD NOT be withdrawn", transcript)

    def test_a_real_withdrawal_is_still_published_as_one(self):
        """The positive control on the test above. Without it the fix could be
        'never claim a withdrawal again', which states nothing."""
        self.stale.write_bytes(STALE)
        rc, transcript = self._run(refuse_unlink=False)
        self.assertEqual(0, rc)
        self.assertFalse(self.stale.exists(),
                         "the page was not withdrawn, so the control is void")
        self.assertIn(WITHDRAWN_SENTENCE, transcript)
        self.assertNotIn("COULD NOT be withdrawn", transcript)

    def test_a_run_with_no_previous_page_says_nothing_alarming(self):
        """The common case stays quiet: no stale page, no warning."""
        self.assertFalse(self.stale.exists())
        rc, transcript = self._run(refuse_unlink=False)
        self.assertEqual(0, rc)
        self.assertIn(WITHDRAWN_SENTENCE, transcript)
        self.assertNotIn("COULD NOT be withdrawn", transcript)


class EveryActThatClaimsAWithdrawalEarnsItTests(unittest.TestCase):
    """Evidence FOR: the fix did not land in one copy and miss the rest.

    This lab has now published six stale prose copies of one corrected figure
    (L-79) and a search-and-replace that reported success on zero matches
    (L-67). The set is DERIVED from the source here, not typed in, so an act
    added tomorrow that publishes the claim without earning it fails this.
    """

    ACTS = Path(REPO / "sdk" / "workflows")
    CLAIM = "certificate is withdrawn, so nothing out"

    def _sources(self):
        return {path.name: path.read_text(encoding="utf-8")
                for path in sorted(self.ACTS.glob("*.py"))
                if path.name != "__init__.py"}

    def test_no_act_states_the_claim_as_a_literal_beside_a_swallowed_unlink(
            self):
        offenders = []
        for name, source in self._sources().items():
            swallows = ("cert_path.unlink()\n    except OSError:\n"
                        "        pass" in source
                        or '(out / "certificate.pdf").unlink()\n'
                           "        except OSError:\n            pass" in source)
            if swallows and self.CLAIM in source:
                offenders.append(name)
        self.assertEqual([], offenders,
                         f"these acts publish a withdrawal they did not earn: "
                         f"{offenders}")

    def test_every_act_that_withdraws_publishes_the_outcome(self):
        """The derivation: any act calling the helper must also publish what
        it returned, and the counts must balance."""
        for name, source in self._sources().items():
            assigns = source.count("_withdrawal = withdraw_certificate")
            uses = source.count("{_withdrawal}")
            self.assertEqual(assigns, uses,
                             f"{name}: {assigns} withdrawal(s) computed but "
                             f"{uses} published")

    def test_the_helper_is_reachable_from_the_package_every_act_imports(self):
        self.assertTrue(callable(workflows.withdraw_certificate))
        self.assertIn("three outcomes",
                      workflows.withdraw_certificate.__doc__)


if __name__ == "__main__":
    unittest.main()
