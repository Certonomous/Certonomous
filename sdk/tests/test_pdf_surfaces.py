#!/usr/bin/env python3
"""Pins for `scripts/check_pdf_surfaces.py`.

WHY THESE ASSERT ON IDENTITY AND NEVER ON COUNTS
------------------------------------------------
A peer proved tonight why this is not boilerplate: a pinning test asserting a
rule "opens no file at all" PASSED while the rule opened four, and it could not
have failed for two independent reasons at once — the spy watched `read_bytes`
while the code read text, and `setUp` had already replaced the function under
test with a lambda. A count assertion ("one finding") is satisfied by the wrong
finding. Every assertion below names the document, the source, the claim class
or the page it is about, so a test that passes has seen the thing it is named
for.

The check is driven for real. Nothing here stubs `pdftotext`, git, or the
grader, because the defect these pins exist to catch is an instrument that
cannot return the negative.
"""
from __future__ import annotations

import hashlib
import importlib.util
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
CHECK = REPO / "scripts" / "check_pdf_surfaces.py"

STALE_PDF = "demo-output/website/latex/closure_challenge_report.pdf"
STALE_SRC = "demo-output/website/latex/closure_challenge_report.tex"
CLEAN_PDFS = (
    "demo-output/website/certificates/b52-certificate-current.pdf",
    "demo-output/acts/round3/naca_certificate.pdf",
    "docs/papers/pope_jfm1975_effective_viscosity_hypothesis.pdf",
)
#: The heading that was V10 blocker C2. It WRAPS between "entire" and "public",
#: and a literal-space pattern returns 0 on the file whose heading it is.
BLOCKER_HEADING = "Cases where we lead the entire\npublic leaderboard."


def purge_pycache() -> None:
    """Stale bytecode inverts mutation tests: clean control fails, mutated
    case passes. PYTHONDONTWRITEBYTECODE does not fix it."""
    for d in REPO.rglob("__pycache__"):
        shutil.rmtree(d, ignore_errors=True)


def load_check():
    purge_pycache()
    spec = importlib.util.spec_from_file_location("cps_under_test", CHECK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestWrapSafety(unittest.TestCase):
    """The property 0 of 28 audited grading records ever declared."""

    def setUp(self):
        self.m = load_check()

    def test_every_claim_pattern_has_a_hand_written_wrapped_probe(self):
        missing = sorted(set(self.m.CLAIM_PATTERNS) - set(self.m.WRAP_PROBES))
        self.assertEqual(
            missing, [],
            f"claim patterns with no wrapped probe (unproven): {missing}")

    def test_every_repair_token_has_a_hand_written_wrapped_probe(self):
        missing = sorted(set(self.m.REPAIR_TOKENS) - set(self.m.REPAIR_PROBES))
        self.assertEqual(
            missing, [],
            f"repair tokens with no wrapped probe (unproven): {missing}")

    def test_selftest_names_each_pattern_and_passes(self):
        ok, log = self.m.wrap_safety_selftest()
        blob = "\n".join(log)
        for name in list(self.m.CLAIM_PATTERNS) + list(self.m.REPAIR_TOKENS):
            self.assertIn(name, blob,
                          f"{name} is not named in the wrap-safety log")
        self.assertTrue(ok, f"wrap-safety self-test failed:\n{blob}")

    def test_the_blocker_heading_matches_across_its_wrap(self):
        import re
        pat = self.m.CLAIM_PATTERNS["lead_whole_board"]
        self.assertRegex(
            BLOCKER_HEADING, pat,
            "lead_whole_board does not match the V10-C2 heading across its "
            "line break -- this is the literal-space defect")

    def test_a_literal_space_pattern_is_proven_blind_to_that_heading(self):
        """The control that makes the previous test mean something."""
        import re
        literal = r"lead the entire public leaderboard"
        self.assertIsNone(
            re.search(literal, BLOCKER_HEADING, re.I),
            "the literal-space pattern was expected to MISS the wrapped "
            "heading; if it matches, this control no longer discriminates")


class TestRepairTokenAdjudication(unittest.TestCase):
    """An ambiguous repair token silently downgrades a true FAIL."""

    def setUp(self):
        self.m = load_check()

    def test_two_of_eight_is_not_a_repair_token(self):
        self.assertNotIn(
            "two_of_eight", self.m.REPAIR_TOKENS,
            "'two of eight' was adjudicated OUT: the report PDF contains "
            "'two of the eight test cases the uncorrected baseline beats all "
            "four published entries', a four-entry decline-gate claim, so the "
            "token cannot certify a six-entry repair")

    def test_repair_tokens_name_the_six_entry_board_or_its_entrant(self):
        import re
        stale_prose = ("on exactly two of the eight test cases the uncorrected "
                       "baseline beats all four published entries")
        fired = [n for n, p in self.m.REPAIR_TOKENS.items()
                 if re.search(p, stale_prose, re.I)]
        self.assertEqual(
            fired, [],
            f"repair tokens {fired} fire on four-entry-era prose, so their "
            f"presence would wrongly clear a stale artifact")


class TestFindsTheStaleArtifactByName(unittest.TestCase):

    def setUp(self):
        self.m = load_check()
        self.res = self.m.grade(REPO, do_render=False, render_dir=Path("/tmp"))

    def _kinds_for(self, rel):
        return {f["kind"] for f in self.res["findings"] if f["rel"] == rel}

    def test_report_pdf_is_named_as_outliving_its_named_source(self):
        hits = [f for f in self.res["findings"]
                if f["rel"] == STALE_PDF and f["kind"] == "OUTLIVED_ITS_INPUT"]
        self.assertTrue(
            hits, f"{STALE_PDF} not reported as OUTLIVED_ITS_INPUT")
        self.assertEqual(
            hits[0]["source"], STALE_SRC,
            "the finding must name the source it outlived")

    def test_report_pdf_is_named_stale_by_the_one_sided_discriminator(self):
        self.assertIn("STALE_BY_DISCRIMINATOR", self._kinds_for(STALE_PDF))

    def test_the_stale_finding_names_the_withdrawn_claim_classes(self):
        hits = [f for f in self.res["findings"]
                if f["rel"] == STALE_PDF
                and f["kind"] == "STALE_BY_DISCRIMINATOR"]
        self.assertTrue(hits)
        claims = hits[0]["claims"]
        for expected in ("rank_1_of_5", "our_model_leads", "p_rank1_68"):
            self.assertIn(
                expected, claims,
                f"the stale finding must name the {expected} claim class")

    def test_clean_artifacts_are_not_named_in_any_finding(self):
        flagged = {f["rel"] for f in self.res["findings"]}
        for rel in CLEAN_PDFS:
            self.assertNotIn(
                rel, flagged,
                f"{rel} carries no withdrawn board claim and must not be "
                f"flagged")

    def test_the_frame_names_the_ungraded_gitignored_arm(self):
        self.assertGreater(
            len(self.res["ignored_pdfs"]), 0,
            "the gitignored PDF arm must be counted and named, not silently "
            "dropped")


class TestExitContract(unittest.TestCase):

    def test_control_failure_outranks_findings(self):
        """A broken instrument must not report a content verdict."""
        m = load_check()
        self.assertEqual((m.PASS, m.FAIL, m.CONTROL_FAIL, m.UNKNOWN),
                         (0, 1, 2, 3))

    def test_real_run_exits_1_and_names_the_report_on_stdout(self):
        purge_pycache()
        pr = subprocess.run([sys.executable, str(CHECK)],
                            capture_output=True, text=True, cwd=str(REPO))
        rc = pr.returncode
        self.assertEqual(rc, 1, f"expected FAIL(1), got {rc}\n{pr.stdout[-800:]}")
        self.assertIn(STALE_PDF, pr.stdout,
                      "the failing run must name the artifact it failed on")
        self.assertIn("OUTLIVED_ITS_INPUT", pr.stdout)


class TestDoesNotMutateTheRepo(unittest.TestCase):

    def test_check_leaves_the_graded_artifact_byte_identical(self):
        target = REPO / STALE_PDF
        before = hashlib.sha256(target.read_bytes()).hexdigest()
        try:
            purge_pycache()
            subprocess.run([sys.executable, str(CHECK)],
                           capture_output=True, text=True, cwd=str(REPO))
        finally:
            after = hashlib.sha256(target.read_bytes()).hexdigest()
        self.assertEqual(before, after,
                         "the check must not modify the artifact it grades")


if __name__ == "__main__":
    unittest.main(verbosity=2)
