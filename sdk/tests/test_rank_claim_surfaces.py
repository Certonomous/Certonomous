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

------------------------------------------------------------------------------
SECOND RUNG, 2026-08-11 (the V8 fix round): THE WORD-FORM GUARD.

The guard above is DIGIT-ANCHORED. It fires on `rank 1 of 5`, on `P(rank 1)`,
on `best overall number on the board` -- all of them claims about US, all of
them carrying a digit. On 2026-08-11 three defects were found and fixed that it
could not have seen, because each states someone ELSE's placement:

  * `DESCRIPTION_DOCUMENT.md:54`   "The rank-3 entry, Wu & Zhang's SST-QCRC"
  * `CLOSURE_CHALLENGE_STATUS.md:559`  the same sentence, its parent
  * `DESCRIPTION_DOCUMENT.md:202`  the entrant designated by a position word
                                   rather than named

Wu & Zhang are rank 2 on the published board and Reissmann is rank 1, so each
of those is only true in a five-way list with our own unsubmitted entry on top:
a rank claim for ourselves, wearing a competitor's name, carrying none of the
three things V8 requires. `TheWordFormGuardTests` below is that rung, and the
three defects are its test set -- the guard must fire on all three as they were
and on none of them as they now are.

Two properties it must have that the digit guard did not:

  * the board is PARSED from the benchmark's own README table, not typed in
    here, so a board that changes changes the verdict.
  * matching is over WHOLE TEXT with whitespace collapsed. A line-bounded
    reader is defeated by a reflow, and the positive control below is a pair of
    texts differing only in where the line breaks.

Against the code as it stood before this rung every test in the new class
errors on `check_board_placement_words`, which did not exist.
"""
from __future__ import annotations

import importlib.util
import re
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


# The published board at benchmark commit deb91557, as the guard parses it:
# first author -> rank. Tests use this fixture rather than the clone, so they
# run on a box that has no clone; `TheBoardIsParsedTests` covers the parse.
BOARD = {"reissmann": 1, "wu": 2, "liu": 3, "montoya": 4}

# THE FIXTURES ARE ASSEMBLED AT RUN TIME, and that is not fussiness.
#
# This file is a tracked surface, so the live guard sweeps it. A fixture that
# is a defect written out in full makes this file a defect, and the guard would
# be right to say so. Rule A has an adjudication clause and could be relied on
# to clear a quotation that states the truth beside it; rule B has no such
# clause and cannot get one, because there is no correct form of a position
# word to sit next to. Assembling both kinds the same way keeps the string
# under test EXACTLY the defect while the source file contains no defect at
# all -- which is also the fix the guard recommends: a placement word cannot
# state a wrong placement if it is not there.
_WRONG = "rank-" + "3"          # Wu & Zhang are rank 2 on the published board
_RIGHT = "rank-" + "2"
_POSITION_WORD = "runner" + "-" + "up"

DEFECT_A_WAS = ("It has no training range, which is exactly why it was chosen. "
                f"The {_WRONG} entry, Wu & Zhang's SST-QCRC, carries the same "
                "term; our three duct scores land within 0.0004 of theirs.")
DEFECT_A_NOW = DEFECT_A_WAS.replace(_WRONG, _RIGHT)

# The parent instance, reproduced with its real line break: the ordinal ends
# one line and the name begins the next.
DEFECT_B_WAS = ("**A measured consistency check, not designed for**: the "
                f"{_WRONG} entry (Wu &\nZhang) runs SST-QCRC, which carries "
                "the same untrained QCR2000 term.")
DEFECT_B_NOW = DEFECT_B_WAS.replace(_WRONG, _RIGHT)

DEFECT_C_WAS = ("The truth-free bound on the overall is 0.002419. Our margin "
                f"over the {_POSITION_WORD} is 0.0028863. The seed bound "
                "covers 84% of the margin.")
DEFECT_C_NOW = ("The truth-free bound on the overall is 0.002419. Our margin "
                "over Reissmann, Fang & Sandberg -- rank 1 on the published "
                "board -- is 0.0028863. The seed bound covers 84%.")


def _faults(text):
    return sa.board_placement_faults(text, BOARD)


class TheWordFormGuardTests(unittest.TestCase):
    """The three defects of 2026-08-11 are the test set."""

    def test_defect_a_wrong_ordinal_on_a_competitor(self):
        rule_a, _ = _faults(DEFECT_A_WAS)
        self.assertEqual(1, len(rule_a), rule_a)
        self.assertIn("rank 2", rule_a[0])
        self.assertEqual(([], []), _faults(DEFECT_A_NOW))

    def test_defect_b_the_same_ordinal_wrapped_across_a_line(self):
        rule_a, _ = _faults(DEFECT_B_WAS)
        self.assertEqual(1, len(rule_a), rule_a)
        self.assertEqual(([], []), _faults(DEFECT_B_NOW))

    def test_defect_c_a_position_word_where_a_name_belonged(self):
        _, rule_b = _faults(DEFECT_C_WAS)
        self.assertEqual(1, len(rule_b), rule_b)
        self.assertEqual(([], []), _faults(DEFECT_C_NOW))

    def test_the_digit_guard_could_not_have_seen_any_of_them(self):
        """Why this rung exists at all, asserted rather than asserted about."""
        for text in (DEFECT_A_WAS, DEFECT_B_WAS, DEFECT_C_WAS):
            self.assertEqual([], sa._rank_claim_lines(text), text)


class WholeTextNotLinesTests(unittest.TestCase):
    """The positive control: two texts differing only in a line break."""

    CLEAN = (f"On the ducts the {_WRONG} entry, Wu and Zhang, runs SST-QCRC "
             "and we do not.")
    WRAPPED = CLEAN.replace(f"{_WRONG} entry", f"{_WRONG}\nentry")

    def test_the_wrap_is_a_fault_and_line_bounded_reading_misses_it(self):
        whole = len(_faults(self.WRAPPED)[0])
        line_bounded = sum(len(_faults(line)[0])
                           for line in self.WRAPPED.splitlines())
        self.assertEqual(1, whole, "whole-text matching missed the wrap")
        self.assertEqual(0, line_bounded,
                         "the control is void: a line-bounded reader would "
                         "have caught this too, so it proves nothing")

    def test_the_unwrapped_twin_is_caught_the_same(self):
        """So the guard is not merely reacting to the newline."""
        self.assertEqual(1, len(_faults(self.CLEAN)[0]))


class HomonymsOfTheWordTests(unittest.TestCase):
    """Senses of `rank` that are not placements. Each was met in this corpus,
    and a guard that fires on them gets switched off within a week."""

    def test_a_probability_is_not_a_placement(self):
        self.assertEqual(([], []), _faults(
            "Delete our only last-place case and P(rank 1) goes to 91%. That "
            "0.0632 against Wu & Zhang's 0.0364 costs 0.0034 of overall."))

    def test_our_own_rank_n_of_5_belongs_to_the_other_guard(self):
        self.assertEqual(([], []), _faults(
            "Round 4 stood at rank 3 of 5, gap to rank 2 (Wu & Zhang, 0.0624) "
            "cut 0.0052 to 0.0030."))

    def test_linear_algebra_rank_is_not_a_placement(self):
        for text in (
                "gradU is then a rank-one pure-shear tensor and every "
                "invariant of it reduces to one shear magnitude; Wu & Zhang "
                "solve a modified equation instead.",
                "the ten basis tensors have pointwise rank exactly three, not "
                "five, on the duct field Reissmann also trains on"):
            self.assertEqual(([], []), _faults(text), text)

    def test_mpi_rank_is_not_a_placement(self):
        self.assertEqual(([], []), _faults(
            "MPI_ABORT was invoked on rank 1 in communicator MPI_COMM_WORLD; "
            "the Reissmann comparison never ran."))

    def test_a_sentence_boundary_does_not_bind(self):
        """`...lists them at rank 2. Rank 3 is Liu, Wang, Zhao & Xiao.` -- the
        rank 2 belongs to the previous sentence, not to Liu."""
        self.assertEqual(([], []), _faults(
            "The published board lists them at rank 2. Rank 3 is Liu, Wang, "
            "Zhao and Xiao, whose method paper we read in full."))

    def test_a_wrong_ordinal_beside_the_right_one_is_adjudication(self):
        """An audit record that names a defect and states the truth beside it
        is correcting a claim, not making one."""
        self.assertEqual(([], []), _faults(
            'The document calls it "the rank-3 entry, Wu & Zhang\'s SST-QCRC". '
            "The published board puts Wu & Zhang at rank 2."))

    def test_rule_b_does_not_fire_on_the_idiom_or_on_a_location(self):
        """Measured against this corpus before shipping: the broad form of
        rule B returned 11 hits and all 11 were these."""
        for text in (
                "which is how the round-4 text went stale in the first place",
                "the study wrote to a third place, so the accounting missed it",
                "the duct deficit is where the remaining gap to first place "
                "lives, against Reissmann's published overall",
                "0.0675 - ahead of third place on the public board"):
            self.assertEqual([], _faults(text)[1], text)


class TheBoardIsParsedTests(unittest.TestCase):
    """EVIDENCE, not a transcription: change the board, change the verdict."""

    def setUp(self):
        self._dir = tempfile.TemporaryDirectory()
        self._env = sa.os.environ.get(sa._BOARD_DIR_ENV)
        sa.os.environ[sa._BOARD_DIR_ENV] = self._dir.name

    def tearDown(self):
        if self._env is None:
            sa.os.environ.pop(sa._BOARD_DIR_ENV, None)
        else:
            sa.os.environ[sa._BOARD_DIR_ENV] = self._env
        self._dir.cleanup()

    def _readme(self, first, second):
        (Path(self._dir.name) / "README.md").write_text(
            "# Current leaderboard\n"
            "|   Rank | Authors | Overall |\n"
            "|---|---|---|\n"
            f"|      1 | [{first}](http://x) | 0.0595 |\n"
            f"|      2 | [{second}](http://y) | 0.0624 |\n",
            encoding="utf-8")

    def test_the_table_is_read_off_the_benchmarks_own_readme(self):
        self._readme("Reissmann, Fang, and Sandberg", "Wu and Zhang")
        board, _ = sa._published_board()
        self.assertEqual({"reissmann": 1, "wu": 2}, board)

    def test_a_different_board_gives_a_different_verdict(self):
        """The check cannot be passing on a constant typed into self_audit."""
        self._readme("Wu and Zhang", "Reissmann, Fang, and Sandberg")
        board, _ = sa._published_board()
        text = "The rank-2 entry, Wu and Zhang, runs SST-QCRC."
        self.assertEqual([], sa.board_placement_faults(text, BOARD)[0])
        self.assertEqual(1, len(sa.board_placement_faults(text, board)[0]))

    def test_no_clone_is_a_detector_that_is_off(self):
        sa.os.environ[sa._BOARD_DIR_ENV] = str(
            Path(self._dir.name) / "not-cloned-here")
        result = sa.check_board_placement_words()
        self.assertEqual(sa.WARN, result.status)
        self.assertIn("OFF", result.summary)

    def test_the_pinned_commit_is_read_off_the_package_not_typed_here(self):
        pinned = sa._pinned_board_commit()
        self.assertRegex(pinned, r"^[0-9a-f]{40}$")


class TheWordFormGuardIsRegisteredTests(unittest.TestCase):
    """A check that is not in CHECKS, BASIS and REMEDIES does not run."""

    def test_registered_in_all_three_tables(self):
        name = "check_board_placement_words"
        self.assertIn(name, {c.__name__ for c in sa.CHECKS})
        self.assertIn(name, sa.BASIS)
        self.assertIn(name, sa.REMEDIES)

    def test_it_is_evidence_and_says_what_it_cannot_see(self):
        basis, _, blind, _ = sa.BASIS["check_board_placement_words"]
        self.assertEqual(sa.EVIDENCE, basis)
        for owed in ("ahead of", "co-author", "QUOTING", "untracked",
                     "outside this check's two patterns", "past fifth",
                     "4 MB"):
            self.assertIn(owed, blind)

    def test_the_verdict_names_its_DOMINANT_blind_spot_not_only_the_tidy_ones(
            self):
        """The exception that cost V16 a clean pass on its first grade.

        The verdict line listed relational comparatives and archive members and
        said nothing about the largest gap of all -- every placement phrased
        outside two regexes, which an independent grade measured at 89% of
        held-out sentences. The digit-anchored guard this one supersedes makes
        that admission about itself; dropping it while inheriting the same
        limitation is how a narrow guard comes to read as coverage. So the
        frame line must carry it, and must say that green is not coverage.
        """
        result = sa.check_board_placement_words()
        frame = [d for d in result.detail if d.startswith("frame:")]
        self.assertEqual(1, len(frame), result.detail)
        self.assertIn("BLIND TO", frame[0])
        self.assertIn("placement expression(s) surveyed", frame[0])
        for owed in ("outside this check's patterns", "past fifth",
                     "GREEN HERE IS NOT COVERAGE", "4 MB", "QUOTING"):
            self.assertIn(owed, frame[0], "the verdict understates its reach")

    def test_the_sibling_guards_admission_is_not_dropped_by_its_successor(self):
        """Whatever the older guard admits about pattern reach, this one must
        admit too -- it has the same limitation at a measured 89%."""
        _, _, sibling_blind, _ = sa.BASIS["check_rank_claim_surfaces"]
        _, _, mine, _ = sa.BASIS["check_board_placement_words"]
        self.assertIn("phrased outside", sibling_blind)
        self.assertIn("phrased outside", mine)

    def test_no_travelling_surface_disagrees_with_the_board(self):
        """The regression that matters, and it is deliberately NOT `the whole
        repository passes`.

        An earlier draft asserted PASS on the live tree. It went red within the
        hour -- not on a defect, but because another agent wrote a record that
        QUOTES the three defects in order to name them, which is a mention and
        not a use, and which rule B by construction cannot tell apart. A test
        that any other writer can turn red by documenting a defect correctly
        teaches the lab to stop documenting defects. So the assertion is the
        one the guard actually makes: nothing that TRAVELS may carry a wrong
        placement. Lab-record WARNs are the documented use/mention class.
        """
        result = sa.check_board_placement_words()
        self.assertNotEqual(sa.FAIL, result.status, result.detail)

    def test_the_three_surfaces_fixed_on_2026_08_11_stay_fixed(self):
        """The precise regression: the files themselves, read off the tree."""
        for rel in ("demo-output/website/closure_challenge_submission_round5"
                    "/DESCRIPTION_DOCUMENT.md",
                    "demo-output/website/CLOSURE_CHALLENGE_STATUS.md",
                    "demo-output/website/CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md"):
            path = REPO / rel
            if not path.exists():          # a checkout without the website tree
                continue
            board = sa._published_board()
            if board is None:              # no benchmark clone on this box
                self.skipTest("benchmark clone absent; detector is OFF")
            rule_a, rule_b = sa.board_placement_faults(
                path.read_text(encoding="utf-8"), board[0])
            self.assertEqual(([], []), (rule_a, rule_b), rel)


if __name__ == "__main__":
    unittest.main()
