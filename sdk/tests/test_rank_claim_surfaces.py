"""The rank-claim guard must cover every surface that makes a rank claim.

WHY. Ladder V rung V8, as amended 2026-08-10, binds EVERY surface: any rank
claim, internal or external, carries P(rank 1), its 2-100% at 95% interval and
the pairs that are `not statistically decided`. A bare 68% is a worse claim
than none, because 68% sounds settled and eight cases do not support settled.

THE DEFECT THESE TESTS PIN. The guard for that rule read ONE string --
`our_entry` on the credentials wall. Four external surfaces were brought into
compliance and were guarded. `closure.html`, the most prominent page in the
shipping bundle, went on making rank claims with no probability and no interval
and nothing caught it, because it was not on the list. The list was the defect.

So the tests below do not check that closure.html in particular is covered.
They check that the SET IS DERIVED: a file nobody ever named, invented inside
the test, must be found the moment it makes a claim. A guard that passes these
by adding a filename to a list has not passed them.

Three more properties, each of which has failed in this ladder at least once:

  * the literal token must be found ON ONE LINE. `not statistically decided`
    has been broken across a line by reflowing prose three times here --
    present to a reader, invisible to the line-bounded grep that sweeps for it.
    A guard that reads the whole text as one string returns a false clean.
  * MPI rank 1 is not a rank claim. The solver logs say "MPI_ABORT was invoked
    on rank 1"; a guard that fires on those gets switched off within a week,
    and then it is guarding nothing.
  * a fault on a surface that TRAVELS is a different severity from the same
    fault on a lab record, and both are reported.

Against the code as it stood before 2026-08-11 every test in this file errors
at import of `check_rank_claim_surfaces`, which did not exist.
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "self_audit_rank_claims", REPO / "scripts" / "self_audit.py")
sa = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = sa
_SPEC.loader.exec_module(sa)

# closure.html's banner, hero card and leaderboard row EXACTLY as they read
# before 2026-08-11: the not-decided pairs present, the figure and the bound
# absent. This is the text the old guard could not see.
CLOSURE_HTML_BEFORE = """<div class="banner">
  <span class="tag t-good">RANK 1 OF 5 - SCORED LOCALLY</span>
  <div>Our entry of record scores <b>0.0566 - the best overall number on the board</b> as of benchmark
  commit <code>deb91557</code>, scored on our own hardware.</div>
  <div><b>And the lead is not statistically decided.</b> Our 0.002878 margin over Reissmann sits
  against a per-case spread five times larger.</div>
</div>
<div class="f">45.3% closer to reality than the standard solve - rank 1 of 5 scored locally,
not an official placement</div>
<tr class="us"><td>Certonomous, round 5</td><td>0.0566</td><td><span class="tag t-gold">UNSUBMITTED
 · RANK 1 OF 5 SCORED LOCALLY · NO OFFICIAL RANK</span></td></tr>
"""

COMPLIANT = """On the published board our 0.0566 is rank 1 of 5, scored locally at deb91557.
P(rank 1) = 68%, and eight cases cannot pin that tighter than 2-100% at 95%.
The leads over Reissmann and over Wu and Zhang are not statistically decided.
"""

# The same compliant text with ONE difference: the token reflowed across a line
# break. A reader sees no change. A line-bounded sweep sees the token vanish.
WRAPPED = COMPLIANT.replace(
    "are not statistically decided.", "are not\nstatistically decided.")

MPI_LOG = """[0]PETSC ERROR: Run with -malloc_debug to check for corruption.
MPI_ABORT was invoked on rank 1 in communicator MPI_COMM_WORLD with errorcode 1.
benchmark closure challenge board overall score
"""


class RankClaimDetectionTests(unittest.TestCase):
    """What counts as a rank claim, and what does not."""

    def test_pre_fix_closure_html_is_caught(self):
        lines = sa._rank_claim_lines(CLOSURE_HTML_BEFORE)
        self.assertTrue(lines, "the page's rank claims were not detected")
        missing = sa._rank_companions_missing(CLOSURE_HTML_BEFORE)
        self.assertIn("P(rank 1)", missing)
        self.assertTrue(any("2-100%" in m for m in missing),
                        f"the interval was not required: {missing}")

    def test_compliant_surface_is_clean(self):
        self.assertTrue(sa._rank_claim_lines(COMPLIANT))
        self.assertEqual([], sa._rank_companions_missing(COMPLIANT))

    def test_wrapped_token_is_a_fault_and_says_so(self):
        """The positive control: a fault an instrument CAN produce.

        If this test passes while `test_compliant_surface_is_clean` also
        passes, the token check is line-bounded and can tell the two apart.
        A whole-text `in` would call both clean.
        """
        missing = sa._rank_companions_missing(WRAPPED)
        self.assertEqual(1, len(missing), missing)
        self.assertIn("wrapped", missing[0])
        self.assertIn("UNBROKEN on one line", missing[0])

    def test_mpi_rank_one_is_not_a_rank_claim(self):
        self.assertEqual([], sa._rank_claim_lines(MPI_LOG))

    def test_a_rank_mentioned_without_being_claimed_is_not_a_claim(self):
        """`docket.json` says the deficit TO rank 1; the charter orders BY
        rank 1. Neither asserts we hold a placement."""
        for text in (
                "The deficit to rank 1 is +0.005913 on the overall and it is "
                "not spread across the board.",
                "As drafted it is strict: rank 1 settles before rank 2 is "
                "looked at, on the benchmark board.",
                "run tree /home/ubuntu/certonomous-runs/w3-qcr-rank1/ on the "
                "closure challenge benchmark board"):
            self.assertEqual([], sa._rank_claim_lines(text), text)

    def test_the_live_page_carries_what_the_rule_requires(self):
        """closure.html in the tree, not a fixture. This is the regression."""
        page = (REPO / "demo-output" / "website" / "closure.html"
                ).read_text(encoding="utf-8")
        self.assertTrue(sa._rank_claim_lines(page))
        self.assertEqual([], sa._rank_companions_missing(page))


class TheSurfaceSetIsDerivedNotListedTests(unittest.TestCase):
    """A file nobody has ever named must be covered the day it claims."""

    def setUp(self):
        self._repo, self._tracked = sa.REPO, sa._tracked_files
        self._travelling, self._archives = (sa._travelling_names,
                                            sa._shipping_archives)
        self._dir = tempfile.TemporaryDirectory()
        sa.REPO = Path(self._dir.name)
        sa._shipping_archives = lambda: []

    def tearDown(self):
        sa.REPO, sa._tracked_files = self._repo, self._tracked
        sa._travelling_names, sa._shipping_archives = (self._travelling,
                                                       self._archives)
        self._dir.cleanup()

    def _surface(self, name: str, text: str, travels: bool = False) -> Path:
        path = sa.REPO / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        sa._tracked_files = lambda: [path]
        sa._travelling_names = lambda: ({name} if travels else set())
        return path

    def test_an_unlisted_lab_record_is_found_and_warned(self):
        name = "a-surface-no-list-has-ever-contained.md"
        self._surface(name, CLOSURE_HTML_BEFORE)
        result = sa.check_rank_claim_surfaces()
        self.assertEqual(sa.WARN, result.status, result.summary)
        self.assertTrue(any(name in d for d in result.detail), result.detail)

    def test_the_same_fault_on_a_surface_that_travels_fails(self):
        name = "also-on-no-list.html"
        self._surface(name, CLOSURE_HTML_BEFORE, travels=True)
        result = sa.check_rank_claim_surfaces()
        self.assertEqual(sa.FAIL, result.status, result.summary)
        self.assertIn("TRAVEL", result.summary)

    def test_a_compliant_unlisted_surface_passes(self):
        """So the fix cannot be 'make it fail always'."""
        self._surface("compliant-and-unlisted.md", COMPLIANT, travels=True)
        result = sa.check_rank_claim_surfaces()
        self.assertEqual(sa.PASS, result.status, result.detail)

    def test_the_verdict_states_the_frame_it_examined(self):
        self._surface("anything.md", COMPLIANT)
        result = sa.check_rank_claim_surfaces()
        frame = [d for d in result.detail if d.startswith("frame:")]
        self.assertEqual(1, len(frame), result.detail)
        self.assertIn("Blind to", frame[0])

    def test_git_unavailable_is_reported_as_a_detector_that_is_off(self):
        sa._tracked_files = lambda: None
        sa._travelling_names = lambda: set()
        result = sa.check_rank_claim_surfaces()
        self.assertEqual(sa.WARN, result.status)
        self.assertIn("OFF", result.summary)


class TheGuardIsRegisteredTests(unittest.TestCase):
    """A check that is not in CHECKS, BASIS and REMEDIES does not run."""

    def test_registered_in_all_three_tables(self):
        name = "check_rank_claim_surfaces"
        self.assertIn(name, {c.__name__ for c in sa.CHECKS})
        self.assertIn(name, sa.BASIS)
        self.assertIn(name, sa.REMEDIES)

    def test_the_declared_blind_spots_name_the_real_ones(self):
        _, _, blind, _ = sa.BASIS["check_rank_claim_surfaces"]
        for owed in ("UTF-8", "untracked", "per file"):
            self.assertIn(owed, blind)


if __name__ == "__main__":
    unittest.main()
