"""A check that RANKS must not read a referent that SCORES. (D55, 2026-08-14.)

WHAT WAS WRONG
--------------
`scripts/self_audit.py` had ONE board. It came from the benchmark clone frozen
at `deb9155`, which is pinned deliberately: rung V1 needs the eight case scores
to recompute identically, and `BOARD_MOVED_2026-08-11.md` section 4 says the
pin must not be moved. That same frozen file was also answering a question that
has nothing to do with score -- HOW MANY POSITIONS THE BOARD HAS, and therefore
whether a rank a sentence names exists at all. The pin lists four entrants; the
live board has six. So the guard told a correct sentence that rank 5 "is a
position this board does not have".

THE REPAIR IS A SECOND REFERENT, NOT A MOVED PIN
------------------------------------------------
`_ranking_board()` reads a committed, dated record of the live board with
exactly the machinery that reads the pin. The pin stays where it is and keeps
every question about who is who. This file proves the two are DISTINGUISHED and
INDEPENDENT: moving one must not move the other, in either direction, because
the whole failure being repaired was two questions silently sharing one answer.

WHAT WAS DELIBERATELY NOT DONE, and it is asserted here so it cannot drift in
quietly: the name-to-rank BINDING was not re-pointed. Re-executed at
`48d3f05a` across the tracked corpus (1455 opened surfaces), swapping it to the
live board takes rule-A faults **from 2 to 68 over disjoint sets** -- both
current faults CLEAR, and 68 wholly new ones appear. This file was first
written calling that "the 66 additions", which is wrong twice: the sets do not
overlap, and the 68 are not one kind. 50 are dated records this check has no
way to tell from a live claim; **18 are the check's own measuring apparatus**
(14 in `sdk/tests/test_rank_claim_surfaces.py`, 3 in `scripts/self_audit.py`,
1 in `campaign/V16_AUTHOR_HELDOUT_SET.py`), which is D55's stated reason for
the gate showing up in the measurement: move the binding and you move the ruler
along with the sample.

TWO GUARDS, BECAUSE ONE WAS NOT ENOUGH AND THAT WAS MEASURED.
`test_the_binding_still_reads_the_scoring_pin` hands the pin to
`board_placement_faults` itself, so it catches a re-point made INSIDE that
function -- mutation-proved. It does NOT catch a re-point at the CALL SITE in
`check_board_placement_words`, which is where the move would most naturally be
taken; that mutation left all 18 tests here and in
`test_fault_message_matches_rule.py` green.
`test_the_check_passes_the_scoring_pin_as_the_binding` watches the call site.

WHAT THIS FILE DOES NOT SETTLE. D55's gate is written against **option 3 as a
whole** -- "option 3 must not be built until someone builds a rule-A held-out
set of LIVE-BOARD sentences" -- and option 3 is the second referent, which is
what was built here. The reason the row gives for the gate is that reach and
precision are graded against sets defined by whatever `_published_board`
returns, and this work does not touch `_published_board`: the binding, the
held-out sets and every published reach and precision figure are untouched, and
the second referent changes no verdict on today's corpus: measured at
`48d3f05a`, the sweep faults the same surfaces with and without a ranking
referent (2 rule-A, 3 rule-B either way) because **not one fault in the corpus
reaches the existence clause at all**. What moved is the frame text and what
happens the next time a live-board placement is written. So the gate's REASON
does not bite here -- there is no reach or precision figure to regrade. Its
WORDING
does. That is the fleet's call to make on the row, not this file's, and it is
recorded in D55's closing note rather than resolved by silence.
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
    "self_audit_for_referent_tests", REPO / "scripts" / "self_audit.py")
sa = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = sa
_SPEC.loader.exec_module(sa)

PIN = {"reissmann": 1, "wu": 2, "liu": 3, "montoya": 4}
LIVE = {"yang": 1, "reissmann": 2, "wu": 3, "tian": 4, "liu": 5, "montoya": 6}

_DECOY_RECORD = """# A different world

| Rank | Authors | Overall |
|---|---|---|
| 1 | Alpha | 0.01 |
| 2 | Beta | 0.02 |
| 3 | Gamma | 0.03 |
"""

_DECOY_README = """# Benchmark

| Rank | Authors | Overall |
|---|---|---|
| 1 | Delta | 0.01 |
| 2 | Epsilon | 0.02 |
| 3 | Zeta | 0.03 |
"""


class _Env:
    """Set env vars for a block and put them back, whatever happens."""

    def __init__(self, **kv):
        self.kv = kv
        self.old: dict[str, str | None] = {}

    def __enter__(self):
        for k, v in self.kv.items():
            self.old[k] = os.environ.get(k)
            os.environ[k] = v
        return self

    def __exit__(self, *exc):
        for k, v in self.old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        return False


class TheTwoReferentsAreDifferentObjectsTests(unittest.TestCase):

    def test_both_referents_are_readable_and_they_disagree(self):
        """If they agreed there would be nothing to separate, and no proof.

        The disagreement is the point: the pin is four entrants led by
        Reissmann, the ranking record is six led by Yang.
        """
        scoring, _ = sa._published_board()
        ranking, note = sa._ranking_board()
        self.assertIsNotNone(scoring, "the scoring pin is not readable")
        self.assertIsNotNone(ranking, f"the ranking referent is OFF: {note}")
        self.assertNotEqual(
            scoring, ranking,
            "the two referents returned the same board, so this test cannot "
            "tell whether they are two objects or one read twice")
        self.assertEqual(1, ranking["yang"], "live board: Yang leads")
        self.assertEqual(1, scoring["reissmann"], "pin: Reissmann leads")
        self.assertGreater(len(ranking), len(scoring))

    def test_the_ranking_referent_is_tracked_and_carries_a_date(self):
        """A referent whose age cannot be read is the pin's defect again.

        It has to be IN the tree (a self-audit that needs the network is off
        whenever the network is) and it has to be able to say how old it is.
        """
        tracked = subprocess.run(
            ["git", "ls-files", "--", sa._RANKING_RECORD], cwd=REPO,
            capture_output=True, text=True, timeout=60).stdout.strip()
        self.assertEqual(sa._RANKING_RECORD, tracked,
                         "the ranking record is not tracked, so the verdict is "
                         "not reproducible from the tree")
        self.assertRegex(
            sa._ranking_board_date(), r"^\d{4}-\d{2}-\d{2}$",
            "the ranking referent cannot state its own date; a referent that "
            "exists to be current must never misreport its age")

    def test_the_verdict_names_which_referent_answered_which_question(self):
        result = sa.check_board_placement_words()
        blob = result.summary + " " + " ".join(result.detail)
        self.assertIn("TWO REFERENTS", blob,
                      "the verdict does not disclose that it reads two boards")
        self.assertIn(sa._RANKING_RECORD, blob,
                      "the verdict does not name the ranking referent")


class MovingOneReferentDoesNotMoveTheOtherTests(unittest.TestCase):
    """The independence proof, run in both directions.

    One artifact serving two purposes is the defect. Two names for one artifact
    would be the same defect with better documentation, so it is not enough
    that the code has two functions -- moving one has to leave the other
    exactly where it was.
    """

    def test_moving_the_ranking_record_leaves_the_scoring_pin_untouched(self):
        before, before_head = sa._published_board()
        with tempfile.TemporaryDirectory() as td:
            decoy = Path(td) / "record.md"
            decoy.write_text(_DECOY_RECORD)
            with _Env(**{sa._RANKING_RECORD_ENV: str(decoy)}):
                moved, _ = sa._ranking_board()
                still, still_head = sa._published_board()
        self.assertEqual({"alpha": 1, "beta": 2, "gamma": 3}, moved,
                         "the ranking referent did not follow its own record")
        self.assertEqual(before, still,
                         "moving the RANKING referent moved the SCORING pin")
        self.assertEqual(before_head, still_head,
                         "moving the RANKING referent moved the pin's commit")

    def test_moving_the_scoring_pin_leaves_the_ranking_referent_untouched(self):
        before, _ = sa._ranking_board()
        with tempfile.TemporaryDirectory() as td:
            clone = Path(td) / "clone"
            clone.mkdir()
            (clone / "README.md").write_text(_DECOY_README)
            with _Env(**{sa._BOARD_DIR_ENV: str(clone)}):
                moved, why = sa._published_board()
                still, _ = sa._ranking_board()
        self.assertEqual({"delta": 1, "epsilon": 2, "zeta": 3}, moved,
                         f"the scoring pin did not follow its own clone: {why}")
        self.assertEqual(before, still,
                         "moving the SCORING pin moved the RANKING referent")

    def test_an_unreadable_ranking_record_is_OFF_with_a_reason(self):
        """Absence must be loud, and it must not fall back silently."""
        with _Env(**{sa._RANKING_RECORD_ENV: "/nonexistent/ranking.md"}):
            board, why = sa._ranking_board()
        self.assertIsNone(board)
        self.assertIn("not readable", why)
        self.assertIn(sa._RANKING_RECORD_ENV, why,
                      "the reason must say where it looked")

    def test_a_ranking_record_with_two_boards_refuses_to_choose(self):
        """Same discipline as the pin: a referent that guesses is worse than
        one that is OFF, because being checkable is the whole job."""
        with tempfile.TemporaryDirectory() as td:
            twice = Path(td) / "record.md"
            twice.write_text(_DECOY_RECORD + "\n" + _DECOY_README)
            with _Env(**{sa._RANKING_RECORD_ENV: str(twice)}):
                board, why = sa._ranking_board()
        self.assertIsNone(board)
        self.assertIn("will not choose", why)


class TheRankingQuestionMovedAndTheScoringQuestionDidNotTests(unittest.TestCase):

    #: Montoya sits at 6 on the live board and at 4 on the pin. A sentence
    #: placing them at 6 asks a question about how many positions exist.
    PROBE = "Montoya is now rank 6 on the published board."

    def test_the_existence_clause_now_reads_the_ranking_referent(self):
        """The regression this file exists for. Fails against unmodified HEAD,
        where `board_placement_faults` takes no ranking referent at all."""
        with_ranking, _ = sa.board_placement_faults(self.PROBE, PIN, LIVE)
        self.assertEqual(1, len(with_ranking), with_ranking)
        self.assertNotIn(
            "position this board does not have", with_ranking[0],
            "rank 6 exists on the live board of six entrants, and the check "
            f"still says it does not:\n  {with_ranking[0]}")

    def test_without_a_ranking_referent_the_pin_answers_and_says_so(self):
        """The fallback is honest rather than absent.

        A check that quietly used the pin for a standing question is what D55
        was filed about; using it LOUDLY when nothing better can be read is a
        different thing.
        """
        pin_only, _ = sa.board_placement_faults(self.PROBE, PIN)
        self.assertEqual(1, len(pin_only))
        self.assertIn("position this board does not have", pin_only[0])
        self.assertIn("frozen scoring pin", pin_only[0],
                      "the fault does not name the referent that answered")

    def test_the_fault_names_the_live_record_when_the_live_record_answered(self):
        # A rank past the END of both boards, pinned on an entrant the rule can
        # bind, so what is being read is the position count and nothing else.
        probe = "Montoya is ranked 9th on the published board."
        faults, _ = sa.board_placement_faults(probe, PIN, LIVE)
        self.assertTrue(faults)
        self.assertIn("live-board record", faults[0],
                      f"the fault does not name which referent it used: "
                      f"{faults[0]}")

    def test_the_check_passes_the_scoring_pin_as_the_binding(self):
        """D55's gate at the CALL SITE, which the probe below cannot reach.

        `test_the_binding_still_reads_the_scoring_pin` calls
        `board_placement_faults` directly and hands it the pin itself, so it
        can only catch a re-point made INSIDE that function. Mutation-proved at
        `48d3f05a`: re-pointing inside it reddens that test, but re-pointing at
        the call site instead -- `board_placement_faults(text, ranking or
        board, ranking)` in `check_board_placement_words`, which is where a
        maintainer taking the gated move would most naturally take it -- left
        all 18 tests in this file and `test_fault_message_matches_rule.py`
        green. This test watches what the check actually passes.
        """
        seen = []
        real = sa.board_placement_faults

        def spy(text, board, ranking=None):
            seen.append((dict(board),
                         None if ranking is None else dict(ranking)))
            return real(text, board, ranking)

        sa.board_placement_faults = spy
        try:
            sa.check_board_placement_words()
        finally:
            sa.board_placement_faults = real

        self.assertTrue(seen, "the check swept no surface, so this test saw "
                              "nothing and must not be read as a pass")
        pin, _ = sa._published_board()
        live, _ = sa._ranking_board()
        self.assertNotEqual(pin, live, "the two referents agree, so this test "
                                       "cannot tell which one was passed")
        for board, ranking in seen:
            self.assertEqual(
                pin, board,
                "the check is binding names to ranks against something other "
                "than the scoring pin. That is D55's gated move and it needs a "
                "live-board held-out set first")
            self.assertEqual(
                live, ranking,
                "the check is not passing the ranking referent as the ranking "
                "referent")

    def test_the_binding_still_reads_the_scoring_pin(self):
        """D55's gate, asserted rather than promised.

        Wu is 2 on the pin and 3 on the live board. This sentence must stay
        SILENT, because the name-to-rank binding was deliberately not
        re-pointed: doing so takes this corpus from 2 rule-A faults to 68,
        almost all of them dated history, and there is no held-out set of
        live-board sentences to measure the change against.
        """
        silent, _ = sa.board_placement_faults(
            "Wu is rank 2 on the published board.", PIN, LIVE)
        self.assertEqual(
            [], silent,
            "the name-to-rank binding appears to have been re-pointed at the "
            "live board. That is D55's gated move and it needs a live-board "
            f"held-out set first: {silent}")


if __name__ == "__main__":
    unittest.main()
