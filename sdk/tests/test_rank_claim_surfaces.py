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

    # The REAL sentence that justifies whole-text matching, reproduced from
    # `latex/closure_challenge_report.tex` with its break where it falls: after
    # the participle and before the ordinal. The first justification offered
    # for whole-text -- the parent instance on the lab record -- was WRONG and
    # is retracted; that one breaks inside the entrant's name, after the
    # surname this check keys on, so a line reader catches it too. This one a
    # line reader cannot see. The sentence is correct, which is luck.
    REAL_WRAP = ("The published entry ranked\nsecond before round 5 --- Wu "
                 "and Zhang's SST-QCRC --- carries the same untrained "
                 "QCR2000 term.")

    def test_the_real_wrap_in_the_report_source_needs_whole_text(self):
        board, reason = sa._published_board()
        if board is None:
            self.skipTest(f"detector OFF, not a silent pass: {reason}")
        names = sa._board_names(board)
        whole = sa._placements(self.REAL_WRAP, names, board)
        line_bounded = [p for line in self.REAL_WRAP.splitlines()
                        for p in sa._placements(line, names, board)]
        self.assertEqual(1, len(whole), "whole-text missed the report's wrap")
        self.assertEqual(0, len(line_bounded),
                         "the control is void: a line reader sees this one too")
        self.assertEqual(([], []), sa.board_placement_faults(
            self.REAL_WRAP, board), "the report's sentence is correct")

    def test_the_retracted_justification_is_retracted_in_the_code(self):
        """The parent instance is NOT defeated by its own reflow. The comment
        that said it was is the copy a rule-author reads."""
        board, reason = sa._published_board()
        if board is None:
            self.skipTest(f"detector OFF, not a silent pass: {reason}")
        names = sa._board_names(board)
        parent = ("A measured consistency check, not designed for: the "
                  f"{_WRONG} entry (Wu &\nZhang) runs SST-QCRC.")
        line_bounded = [p for line in parent.splitlines()
                        for p in sa._placements(line, names, board)]
        self.assertEqual(1, len(line_bounded),
                         "if this is 0 the old justification was right after "
                         "all and the retraction should itself be retracted")
        source = (REPO / "scripts" / "self_audit.py").read_text(
            encoding="utf-8")
        self.assertIn("first justification for this was WRONG", source)


# Assembled, like every other fixture here, for the reason this file already
# gives: it is a tracked surface and the live guard sweeps it. Writing these
# sentences out in full made this file carry twelve real faults, which the
# widened guard reported within a minute of being widened -- the use/mention
# limit biting its own test file, and the remedy is the one the guard
# recommends: a placement word cannot state a wrong placement if it is not
# there.
_ORD = "four" + "th"        # Wu & Zhang are rank 2; every fixture below says 4
_NUM = "4"
_TOP = "to" + "p"


class TheWidenedFamiliesTests(unittest.TestCase):
    """Each family added 2026-08-11 after the first grade measured the reach of
    the original two at 11%. Every sentence here pins a WRONG placement on a
    NAMED entrant, so every one must be caught. Each family was measured for
    false positives across the whole repository before it was kept."""

    def _one_fault(self, sentence):
        rule_a, _ = _faults(sentence)
        self.assertEqual(1, len(rule_a), f"{sentence!r} -> {rule_a}")

    def test_participle_and_verb_forms_of_rank(self):
        for sentence in (
                f"The published entry ranked {_ORD} is Wu and Zhang.",
                f"Wu and Zhang, ranked {_ORD} before round 5, run the term.",
                f"Wu and Zhang ranks {_ORD} on the published board.",
                f"The {_ORD}-ranked entry, Wu and Zhang, runs SST-QCRC."):
            self._one_fault(sentence)

    def test_verbal_placements(self):
        for verb in ("placed", "finished", "came", "took", "sits at",
                     "stands at"):
            self._one_fault(f"Wu and Zhang {verb} {_ORD} on the board.")

    def test_bare_predicates(self):
        for sentence in (f"Wu and Zhang are {_ORD} overall on the board.",
                         f"Wu and Zhang are the {_ORD}-best published entry."):
            self._one_fault(sentence)

    def test_designators(self):
        for sentence in (
                f"The {_ORD} entry, Wu and Zhang, runs SST-QCRC.",
                f"The {_ORD} submission, Wu and Zhang, carries QCR2000.",
                f"The board's {_ORD} slot belongs to Wu and Zhang.",
                f"Wu and Zhang hold position {_NUM} on the published board."):
            self._one_fault(sentence)

    def test_the_family_that_was_measured_and_then_removed(self):
        """`No. N` was added, measured across the repository, and taken back
        out: it fired on a journal issue number in a third-party bibliography
        next to a `Wu` citation. One held-out sentence is not worth an
        unbounded false-positive source, and a guard that cries wolf gets
        switched off. Recorded as a test so the removal is a decision with a
        reason rather than a gap someone re-fills."""
        self.assertEqual(([], []), _faults(
            f"No. {_NUM} on the published board is Wu and Zhang."))
        self.assertEqual(([], []), _faults(
            "J. Fluid Mech., Vol. 812, No. 4, Wu and co-workers, 2017."))

    def test_topping_the_board(self):
        """The phrasing the digit-anchored sibling names as its own blind
        spot, in the form where it is bound to an entrant and checkable."""
        for sentence in (f"Wu and Zhang {_TOP} the published board.",
                         f"Wu and Zhang sit at the {_TOP} of the board."):
            self._one_fault(sentence)

    def test_rule_b_was_widened_too(self):
        """Nine families had gone to rule A and NONE to rule B, so "the miss
        rate fell" described one of two rules while reading as a statement
        about the check. Four of these five passed clean before 2026-08-11."""
        second = "second" + "-place"          # assembled, for the third time
        front = "front" + "-runner"            # and for the same reason
        leader = "lead" + "er"
        for sentence in (
                f"Our margin over the {_POSITION_WORD} is 0.0028863.",
                f"We beat the {_POSITION_WORD} by 0.0029 on the overall.",
                f"We finished clear of the {second} submission.",
                f"The gap between us and the {front} is 0.0029.",
                f"Our margin over the {leader} is 0.0029."):
            _, rule_b = _faults(sentence)
            self.assertEqual(1, len(rule_b), f"{sentence!r} -> {rule_b}")

    def test_rule_b_stays_narrower_than_rule_a_on_purpose(self):
        """It has no adjudication clause, so every widening costs precision
        with no way to clear a quotation. The idiom stays out."""
        for sentence in (
                "which is how the round-4 text went stale in the first place",
                "the study wrote to a third place, so the accounting missed it",
                "the gap to first place lives in the ducts"):
            self.assertEqual([], _faults(sentence)[1], sentence)

    def test_the_families_deliberately_left_out_stay_out(self):
        """Not an oversight. A numbered table row is not distinguishable from
        any numbered list, and the benchmark's own board is one; medals, roman
        numerals and German are registers this lab does not write."""
        for sentence in (f"| {_NUM} | Wu and Zhang | 0.0624 |",
                         f"{_NUM},Wu and Zhang,0.0624",
                         "Wu and Zhang take silver on the published board.",
                         "Rank IV on the published board is Wu and Zhang.",
                         "Wu and Zhang liegen auf Platz vier der Tabelle."):
            self.assertEqual(([], []), _faults(sentence), sentence)


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


class TheParseFailsSafeTests(unittest.TestCase):
    """Four ways the board parse broke, found by the first independent grade.

    THE STANDARD, and it is not "these do not happen today": a parse either
    returns a board it has checked or returns the reason it has none. It never
    returns a board it is unsure of, and it never raises -- an exception in one
    check takes every OTHER check in `self_audit` down with it, which is a
    guard doing more damage than the defect it exists to find.

    Three of the four used to be SILENT, and a silent mis-parse is worse than a
    miss: two of them manufacture false positives on correct prose, which
    discredits the instrument rather than merely failing to help it.
    """

    HEADER = ("# Current leaderboard\n"
              "|   Rank | Authors | Overall |\n"
              "|---|---|---|\n")

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

    def _write(self, body):
        (Path(self._dir.name) / "README.md").write_text(body, encoding="utf-8")
        return sa._published_board()

    def _rows(self, *authors):
        return "".join(f"|      {i} | [{a}](http://x{i}) | 0.0{i} |\n"
                       for i, a in enumerate(authors, 1))

    def test_a_second_numbered_table_no_longer_moves_a_rank(self):
        """Any `| N | [text` line anywhere used to be read as a board row, last
        one wins. A decoy table moved an entrant a whole rank, silently."""
        board, _ = self._write(
            self.HEADER + self._rows("Reissmann, Fang", "Wu and Zhang")
            + "\n# Cases\n| N | Case |\n|---|---|\n"
              "|      3 | [Wu and Zhang](http://z) |\n")
        self.assertEqual({"reissmann": 1, "wu": 2}, board)

    def test_a_shared_first_author_surname_is_OFF_not_a_dropped_entrant(self):
        """The dict used to collapse two entrants into one key and then fault
        CORRECT prose about the survivor."""
        board, reason = self._write(
            self.HEADER + self._rows("Zhang, Li", "Zhang, Chen"))
        self.assertIsNone(board)
        self.assertIn("share the first-author surname", reason)

    def test_ranks_that_are_not_one_through_n_are_OFF(self):
        board, reason = self._write(
            self.HEADER + "|      2 | [A, B](http://x) | 0.05 |\n"
                          "|      4 | [Wu and Zhang](http://y) | 0.06 |\n")
        self.assertIsNone(board)
        self.assertIn("not 1..N", reason)

    def test_a_readme_with_no_table_at_all_is_OFF(self):
        board, reason = self._write("# Something else\nprose only\n")
        self.assertIsNone(board)
        self.assertIn("no table rows at all", reason)

    def test_a_metacharacter_in_a_surname_does_not_raise(self):
        """`Fox[a` used to raise re.error out of this check and end the run."""
        for bad in ("Fox[a, Smith", "Fox(, Smith", "Fox+?, Smith"):
            board, _ = self._write(
                self.HEADER + self._rows(bad, "Wu and Zhang"))
            self.assertIsNotNone(board)
            faults = sa.board_placement_faults(
                "The rank-2 entry, Wu and Zhang, runs it.", board)
            self.assertEqual(([], []), faults, bad)

    def test_a_particle_surname_keys_on_the_name_not_the_particle(self):
        """`van Dijk` used to key the board on `van`, which then bound to every
        occurrence of that word in prose -- a false-positive generator."""
        board, _ = self._write(
            self.HEADER + self._rows("van Dijk, Smith", "Wu and Zhang"))
        self.assertEqual({"dijk": 1, "wu": 2}, board)

    # --- the second grade's three, all of which returned an UNCHECKED board
    # --- with no warning. The root cause was one sentence: the first repair
    # --- anchored to A heading and took the first table after it, and never
    # --- asked whether what it read was a leaderboard. It asks now, and the
    # --- heading plays no part at all.

    def test_a_numbered_legend_between_heading_and_board_is_not_the_board(self):
        board, _ = self._write(
            self.HEADER.split("|")[0]          # just the heading line
            + "\n| N | Case |\n|---|---|\n|      1 | [case](http://x) |\n\n"
            + self.HEADER + self._rows("Reissmann, Fang", "Wu and Zhang"))
        self.assertEqual({"reissmann": 1, "wu": 2}, board)

    def test_an_earlier_heading_that_also_says_leaderboard_is_not_the_board(self):
        board, _ = self._write(
            "## Archived leaderboard (2024)\n| N | Who |\n|---|---|\n"
            "|      1 | [ghost](http://g) |\n\n"
            + self.HEADER + self._rows("Reissmann, Fang", "Wu and Zhang"))
        self.assertEqual({"reissmann": 1, "wu": 2}, board)

    def test_a_blank_line_inside_the_board_is_OFF_not_a_dropped_entrant(self):
        """It used to return the rows above the blank line and say nothing.
        Silent blindness: an entrant disappears and stops being checked."""
        board, reason = self._write(
            self.HEADER + "|      1 | [Reissmann, Fang](http://a) | 0.05 |\n\n"
                          "|      2 | [Wu and Zhang](http://b) | 0.06 |\n")
        self.assertIsNone(board)
        self.assertIn("not distinguishable from a decoy", reason)

    def test_two_tables_that_both_look_like_boards_is_OFF_not_a_choice(self):
        rows = self._rows("Reissmann, Fang", "Wu and Zhang")
        board, reason = self._write(
            self.HEADER + rows + "\n# Another\n" + self.HEADER + rows)
        self.assertIsNone(board)
        self.assertIn("will not choose", reason)

    def test_the_heading_plays_no_part(self):
        """The parse used to depend on finding the word `leaderboard`. It does
        not any more, which is why two of the three above now read the RIGHT
        board rather than merely refusing."""
        no_heading = self.HEADER.split("\n", 1)[1]        # the table rows only
        board, reason = self._write(
            no_heading + self._rows("Reissmann, Fang", "Wu and Zhang"))
        self.assertEqual({"reissmann": 1, "wu": 2}, board, reason)

    def test_a_table_that_is_not_a_leaderboard_is_rejected_by_its_header(self):
        board, reason = self._write(
            "# Cases\n| N | Case | Notes |\n|---|---|---|\n"
            "|      1 | [alpha](http://x) | a |\n"
            "|      2 | [beta](http://y) | b |\n")
        self.assertIsNone(board)
        self.assertIn("not a rank", reason)

    def test_a_generational_suffix_keys_on_the_name_not_the_suffix(self):
        """The mirror of the particle bug: the last-token rule that fixed
        `van Dijk` broke `Reissmann Jr.` into its suffix. Both ends now."""
        board, _ = self._write(
            self.HEADER + self._rows("Reissmann Jr., Fang", "Wu and Zhang"))
        self.assertEqual({"reissmann": 1, "wu": 2}, board)

    def test_both_ends_of_the_name_stay_handled_together(self):
        for cell, expected in (("[van Dijk, Smith](u)", "Dijk"),
                               ("[Reissmann Jr., Fang](u)", "Reissmann"),
                               ("[de la Cruz III, Ono](u)", "Cruz"),
                               ("[Wu and Zhang](u)", "Wu")):
            self.assertEqual(expected, sa._first_author_surname(cell), cell)

    def test_the_off_reason_reaches_the_verdict(self):
        """A detector that is off must say WHY, not merely that it is."""
        self._write(self.HEADER + self._rows("Zhang, Li", "Zhang, Chen"))
        result = sa.check_board_placement_words()
        self.assertEqual(sa.WARN, result.status)
        self.assertIn("OFF", result.summary)
        self.assertIn("share the first-author surname", result.summary)


class TheOrdinalVocabularyIsDerivedTests(unittest.TestCase):
    """A literal survived inside the thing built to remove literals.

    `_PLACE` covered 1-5 because today's board has four rows, so every
    placement past fifth was unmatched on a longer board -- silently. The board
    grew from three rows to four during this campaign.
    """

    SEVEN = {f"name{i}": i for i in range(1, 8)}

    def test_word_and_digit_forms_exist_past_fifth_on_a_longer_board(self):
        tokens = sa._place_tokens(len(self.SEVEN) + sa._PLACE_OVER)
        for token, position in (("6", 6), ("sixth", 6), ("6th", 6),
                                ("seven", 7), ("seventh", 7), ("11", 11)):
            self.assertEqual(position, tokens[token], token)

    def test_a_correct_placement_past_fifth_is_matched_and_cleared(self):
        self.assertEqual(
            ([], []),
            sa.board_placement_faults(
                "The rank-6 entry, Name6, runs the same term.", self.SEVEN))
        self.assertEqual(
            ([], []),
            sa.board_placement_faults(
                "The sixth-place entry, Name6, runs it.", self.SEVEN))

    def test_a_wrong_placement_past_fifth_is_caught(self):
        rule_a, _ = sa.board_placement_faults(
            "The rank-2 entry, Name6, runs it.", self.SEVEN)
        self.assertEqual(1, len(rule_a), rule_a)
        self.assertIn("rank 6", rule_a[0])

    def test_an_ordinal_naming_a_position_the_board_lacks_says_so(self):
        """The margin past the board's length is the point: `the rank-9 entry`
        on a seven-row board is a fault of its own kind."""
        rule_a, _ = sa.board_placement_faults(
            "The rank-9 entry, Name6, runs it.", self.SEVEN)
        self.assertEqual(1, len(rule_a), rule_a)
        self.assertIn("position this board does not have", rule_a[0])

    def test_the_vocabulary_tracks_the_board_rather_than_a_constant(self):
        small = len(sa._place_tokens(len(BOARD) + sa._PLACE_OVER))
        large = len(sa._place_tokens(len(self.SEVEN) + sa._PLACE_OVER))
        self.assertGreater(large, small,
                           "the ordinal range did not grow with the board")


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
                     "any placement phrased outside this check's",
                     "RULE-A patterns",
                     "derived from the parsed board", "4 MB"):
            self.assertIn(owed, blind)

    def test_the_verdict_names_its_DOMINANT_blind_spot_not_only_the_tidy_ones(
            self):
        """The exception that cost V16 a clean pass on its first grade.

        The verdict line listed relational comparatives and archive members and
        said nothing about the largest gap of all -- every placement phrased
        outside its regexes, which an independent grade measured at 89% of
        held-out sentences and my own set at 80%, widened since to 30% but
        never to nothing. The digit-anchored guard this one supersedes makes
        that admission about itself; dropping it while inheriting the same
        limitation is how a narrow guard comes to read as coverage. So the
        frame line must carry it, and must say that green is not coverage.
        """
        result = sa.check_board_placement_words()
        frame = [d for d in result.detail if d.startswith("frame:")]
        self.assertEqual(1, len(frame), result.detail)
        self.assertIn("BLIND TO", frame[0])
        self.assertIn("placement expression(s) found in those", frame[0])
        self.assertIn("that pair is the denominator and its selection rule",
                      frame[0])
        for owed in ("ANY placement phrased outside this check's",
                     "RULE-A patterns",
                     "derived from this board's length",
                     "GREEN HERE IS NOT COVERAGE", "4 MB", "QUOTING"):
            self.assertIn(owed, frame[0], "the verdict understates its reach")

    def test_no_reach_figure_or_pattern_count_is_typed_into_a_surface(self):
        """The literal problem one level above the ordinal vocabulary.

        The count `eleven` and three miss rates were typed into the docstring,
        the frame line and BASIS separately. Add a family and all three state a
        wrong count while every test still passes, because the tests asserted
        the STRING was present, not that it was true. Everything is derived
        now: the count from the compiled pattern's own named groups, the
        sentences from `_PLACE_REACH`. This test fails if anyone types one back.
        """
        doc = sa.check_board_placement_words.__doc__
        _, _, blind, _ = sa.BASIS["check_board_placement_words"]
        frame = [d for d in sa.check_board_placement_words().detail
                 if d.startswith("frame:")][0]
        self.assertNotRegex(doc, r"\b(eleven|twelve|thirteen)\b")
        self.assertNotRegex(doc, r"\d+%")
        for name, _who, _blind, n, was, now in sa._PLACE_REACH:
            for surface in (blind, frame):
                self.assertIn(name, surface)
                self.assertIn(f"{now} of {n}", surface)
                if was is not None:
                    self.assertIn(f"{was} of {n}", surface)

    def test_the_pattern_count_is_counted_not_claimed(self):
        """Add a twelfth family and the number moves by itself."""
        counted = sa._place_family_count()
        alternatives = sa._place_pattern(sa._PLACE_OVER + 1).groupindex
        self.assertEqual(len(alternatives), counted)
        _, _, blind, _ = sa.BASIS["check_board_placement_words"]
        self.assertIn(f"{counted} RULE-A patterns", blind)

    def test_the_headline_pair_is_one_fixed_sample_measured_twice(self):
        """The second grade's exception 2. The first published pair was an
        OUTSIDE measurement of the old patterns beside an INSIDE measurement of
        the new -- different samples, and nothing said so. The headline must be
        a single set measured at both ends, and every row must name who built
        it and whether they had seen the patterns."""
        sentence = sa._place_reach_sentence()
        self.assertIn("ONE FIXED SET measured before and after", sentence)
        head = sa._PLACE_REACH[0]
        self.assertIn(f"{head[4]} of {head[3]}", sentence)
        self.assertIn(f"{head[5]} of {head[3]}", sentence)
        for _n, who, blind, *_ in sa._PLACE_REACH:
            self.assertIn(who, sentence)
            self.assertIn("BLIND" if blind else "WITH the pattern list",
                          sentence)
        self.assertIn("RULE B separately", sentence)

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
        """The precise regression: the files themselves, read off the tree.

        ABSENCE FAILS. An earlier version `continue`d past a missing file, so
        on a checkout without the website tree this test reported a pass having
        asserted nothing about any of the three -- a green that means "I looked
        at nothing", which is the shape of finding this whole rung exists to
        refuse. A missing regression surface is a broken test, not a skipped
        one. (A missing benchmark clone is different in kind: the detector is
        genuinely OFF and says so, so that one skips and names itself.)
        """
        board, reason = sa._published_board()
        if board is None:
            self.skipTest(f"detector OFF, not a silent pass: {reason}")
        checked = 0
        for rel in ("demo-output/website/closure_challenge_submission_round5"
                    "/DESCRIPTION_DOCUMENT.md",
                    "demo-output/website/CLOSURE_CHALLENGE_STATUS.md",
                    "demo-output/website/CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md"):
            path = REPO / rel
            self.assertTrue(path.exists(),
                            f"the regression surface {rel} is gone; this test "
                            f"asserts nothing without it")
            rule_a, rule_b = sa.board_placement_faults(
                path.read_text(encoding="utf-8"), board)
            self.assertEqual(([], []), (rule_a, rule_b), rel)
            checked += 1
        self.assertEqual(3, checked)


if __name__ == "__main__":
    unittest.main()
