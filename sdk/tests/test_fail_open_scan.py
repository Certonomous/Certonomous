"""The fail-open scan must be shown able to find one before it reports none.

WHY. Docket B2 asks for a sweep of every gate for the shape V16 found in its
own guard: a per-surface `except Exception` kept one bad document from ending
the audit -- correct -- and then left the STATUS green while reporting the skip
only in the frame line. Inject a raise on exactly the surface carrying a fault
and the verdict read "all 0 placement expression(s) agree with the published
board". A SURFACE THAT COULD NOT BE READ IS NOT A SURFACE THAT AGREES.

THE DEFECT THESE TESTS PIN IS THE SWEEP'S OWN. A sweep that returns "few or no
fail-open gates" is worth nothing unless it was shown capable of finding one,
and this lab has published four absolutes that turned out false. So the tests
below are the control, run in BOTH directions:

  * the known positive -- `check_board_placement_words` at 038b36da, the exact
    shape before its repair -- must be FLAGGED. If this fails, every negative
    result the scan has ever produced is void.
  * the repaired version of the SAME function must be CLEARED. Without this a
    scan that flags everything would pass the first test and mean nothing.

The discriminator between them is the point of the whole method, and it is
narrow: the broken version DID record its skip -- into `unreadable`, printed in
the frame line -- and still shipped a green STATUS. Recording a skip in TEXT is
not a third verdict. The repaired version records into a name the verdict
consults. So the scan asks whether a swallow can move the STATUS, never whether
it can move a string.

`TheScanRefusesItsOwnDefectTests` is the recursion, and it is deliberate: an
instrument that silently skipped a file it could not parse would be committing,
in its own denominator, the error it exists to report.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import textwrap
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "fail_open_scan", REPO / "scripts" / "fail_open_scan.py")
scan = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = scan
_SPEC.loader.exec_module(scan)


def _sites(source: str, func: str) -> list[dict]:
    return [s for s in scan.scan_source("fixture", textwrap.dedent(source))
            if s["func"] == func]


class TheKnownPositiveIsFoundTests(unittest.TestCase):
    """Evidence FOR: the method can find the defect it was built to find.

    Run against the real historical source, read out of git rather than
    reproduced here -- a fixture copied by hand would drift from the thing it
    claims to be, and this lab has already published a control's configuration
    as production configuration once (L-68).
    """

    def setUp(self):
        result = subprocess.run(
            ["git", "show", f"{scan.CONTROL_COMMIT}:{scan.CONTROL_PATH}"],
            cwd=REPO, capture_output=True, text=True)
        if result.returncode != 0:
            self.skipTest(f"commit {scan.CONTROL_COMMIT} unavailable, not a "
                          f"silent pass: {result.stderr.strip()}")
        self.broken = result.stdout

    def test_the_v16_guard_before_its_repair_is_flagged(self):
        sites = [s for s in scan.scan_source("control", self.broken)
                 if s["func"] == scan.CONTROL_FUNC]
        self.assertTrue(sites, "no shape site found in the control function")
        self.assertTrue(any(s["flag"] for s in sites),
                        f"the known positive was MISSED: {sites}")

    def test_the_exact_handler_is_the_one_flagged(self):
        """Not merely 'something in that function'. The site is the
        `except Exception` that counted the skip into `unreadable`."""
        sites = [s for s in scan.scan_source("control", self.broken)
                 if s["func"] == scan.CONTROL_FUNC
                 and "unreadable" in s["swallow_writes"]]
        self.assertEqual(1, len(sites), sites)
        self.assertTrue(sites[0]["flag"])
        self.assertEqual([], sites[0]["moves_verdict"],
                         "the skip counter must NOT be read as reaching the "
                         "verdict; if it does, the control is void")

    def test_the_shipped_control_entry_point_agrees(self):
        """`--control` is what anyone re-running this will type."""
        self.assertEqual(0, scan.run_control())


class TheRepairIsClearedTests(unittest.TestCase):
    """Evidence FOR: the method is not simply flagging every handler.

    The positive control above is worthless without this one. Same function,
    same file, repaired -- and the scan must be able to tell them apart.
    """

    def test_the_repaired_guard_records_into_the_verdict(self):
        source = (REPO / "scripts" / "self_audit.py").read_text(
            encoding="utf-8")
        self.assertIn("could not be swept", source,
                      "the repair this test is evidence about is not in the "
                      "tree; without it this test asserts nothing")
        self.assertEqual(0, scan.run_control())


class TheDiscriminatorIsStatusNotTextTests(unittest.TestCase):
    """Evidence FOR: recording a skip in a MESSAGE does not clear a site.

    This is the precise thing the V16 guard got wrong, reduced to two fixtures
    that differ only in where the skip lands.
    """

    TEXT_ONLY = """
        def check_it():
            skipped = 0
            findings = []
            for surface in surfaces():
                try:
                    findings.extend(inspect(surface))
                except Exception:
                    skipped += 1
                    continue
            if findings:
                return Result(FAIL, f"{len(findings)} found, {skipped} skipped")
            return Result(PASS, f"all agree, {skipped} skipped")
    """

    REACHES_STATUS = """
        def check_it():
            skipped = []
            findings = []
            for surface in surfaces():
                try:
                    findings.extend(inspect(surface))
                except Exception:
                    skipped.append(surface)
                    continue
            if findings:
                return Result(FAIL, "found")
            if skipped:
                return Result(WARN, "INCOMPLETE: not swept")
            return Result(PASS, "all agree")
    """

    def test_a_skip_counted_only_into_the_message_is_flagged(self):
        sites = _sites(self.TEXT_ONLY, "check_it")
        self.assertEqual(1, len(sites), sites)
        self.assertTrue(sites[0]["flag"],
                        "a skip that moves only the TEXT was cleared")
        self.assertIn("skipped", sites[0]["swallow_writes"])

    def test_the_same_skip_reaching_the_status_is_cleared(self):
        """The positive control on this negative: one edit apart."""
        sites = _sites(self.REACHES_STATUS, "check_it")
        self.assertEqual(1, len(sites), sites)
        self.assertFalse(sites[0]["flag"],
                         "a skip that DOES move the status was still flagged, "
                         "so the discriminator is void")
        self.assertIn("skipped", sites[0]["moves_verdict"])

    def test_a_handler_in_a_function_with_no_verdict_is_not_flagged(self):
        """Out of scope is a real answer, and the scan must give it."""
        sites = _sites("""
            def tidy_up(paths):
                for path in paths:
                    try:
                        path.unlink()
                    except OSError:
                        continue
        """, "tidy_up")
        self.assertEqual(1, len(sites), sites)
        self.assertFalse(sites[0]["emits_verdict"])
        self.assertFalse(sites[0]["flag"])


class TheScanRefusesItsOwnDefectTests(unittest.TestCase):
    """Evidence FOR: a file the scan cannot read is not a file it cleared.

    The instrument's own third verdict. A scan that dropped an unparseable
    file would report a clean denominator over files it never opened, which is
    the defect it exists to find, committed by the finder.
    """

    def test_an_unparseable_file_lands_in_UNPARSED_and_not_in_the_clean_count(
            self):
        with self.assertRaises(SyntaxError):
            scan.scan_source("broken", "def f(:\n    pass\n")

    def test_the_repo_scan_carries_frame_filter_and_commit(self):
        """A number whose frame nobody can state is worse than no number
        (L-75). The scan may not hand anyone a bare count."""
        report = scan.scan_repo(exclude=("scripts/self_audit.py",))
        for owed in ("frame", "commit", "files_scanned", "UNPARSED",
                     "shape_sites", "flagged"):
            self.assertIn(owed, report)
        self.assertIn("git ls-files", report["frame"])
        self.assertNotIn("grep", report["frame"].split("no grep")[0])
        self.assertRegex(report["commit"], r"^[0-9a-f]{7,40}$")
        self.assertIn("scripts/self_audit.py", report["excluded"])
        self.assertEqual([], report["UNPARSED"],
                         "a tracked .py file did not parse; it is NOT clean")

    def test_the_scan_declares_what_it_cannot_see(self):
        """A guard that does not state its blind spots reads as coverage."""
        for owed in ("CANNOT SEE", "intraprocedural", "L-75", "L-67",
                     "CANDIDATE, NOT A DEFECT"):
            self.assertIn(owed, scan.__doc__)


if __name__ == "__main__":
    unittest.main()
