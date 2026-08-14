"""A fault message may not claim more than the rule tested. (D54, 2026-08-14.)

WHAT WAS WRONG
--------------
Rule B (`_place_unnamed` in `scripts/self_audit.py`) faulted with the sentence
*"compares us to a board position without naming who holds it"*. "Without
naming who holds it" is a claim about the SURROUNDINGS of the phrase, and rule
B has no surroundings: it is a bare regex over whitespace-flattened text with
no proximity window and no adjudication clause at any distance. Executed
against `5c9c63fb`, `"Yang: our margin over the leader is 0.0027."` -- the
holder's name one character outside the match -- faulted identically to a
surface naming nobody anywhere. The message was therefore FALSE of at least 9
of the live occurrences it was printed against.

THE DENOMINATOR IS 14, NOT 13. This file was written saying "9 of the 13",
taking the 13 from D54's row. Re-executed at `48d3f05a` against a worktree of
`5c9c63fb` itself, rule B has **14** occurrences there, not 13: the numerator
9 reproduces exactly, and so do the four D54 names as non-Yang
(`benchmarks.json`, `wall/wall.json`, the second occurrence in
`latex/closure_challenge_report.tex`, `sdk/scripts/build_benchmarks.py`), but
a fourteenth surface D54 did not list -- `docs/INSTRUMENT_INTEGRITY_LEDGER.md`,
*"Our margin over the runner-up"* -- is a fifth non-Yang occurrence. It is a
`runner-up` phrase where the other thirteen are `leader` phrases, which is the
likely reason it was not counted. The row is a dated measurement and is left
as it stands; this is the number the re-execution produced.

WHAT WAS DONE, AND WHAT WAS DELIBERATELY NOT
--------------------------------------------
The MESSAGE was narrowed to the rule. The RULE was not widened to the message.
Retuning a detector so that its author's own prose passes is how a guard gets
tuned to a number, and rule B in particular has no held-out sample in this lab
against which a proximity-clearing clause could be shown not to lose the
anonymous cases it exists to catch (D54's own costing). Whether it SHOULD have
an adjudication clause is filed as its own row (**D77**) rather than smuggled
in behind a message fix. That row number is not the one this file was written
with: it said D63, an ID this work reserved by CITATION while it sat
uncommitted through a usage-limit kill, and which the fleet allocated to an
unrelated auto-stop defect hours before the work was recovered. A citation is
not a claim on an append-only register.

`test_the_rule_still_has_no_window_at_any_distance` is the half of this file
that guards the change from its own author: if a proximity clause is ever added
without that row being settled, it reddens.

AND IT DOES NOT REDDEN FOR EVERY SUCH CLAUSE, which was measured rather than
assumed. Mutation-proved at `48d3f05a`: a window keyed on any capitalised
proper noun reddens it at all five distances, but a window keyed on
`_board_names(board)` -- the way rule A's own adjudication is keyed, and so the
likelier way someone would write it -- left all 18 tests in this file and
`test_two_board_referents.py` GREEN while silencing a real fault. The reason is
that every probe here names **Yang**, who leads the LIVE board and is not on
the scoring pin these probes pass, so a board-keyed clause can never fire on
them. `test_a_window_keyed_on_the_BOARD_is_caught_too` closes that hole with a
holder the passed board actually carries.

WHAT THIS FILE CANNOT SEE. It detects the specific widening D54 forbids -- a
proximity or adjudication clause -- because that is the one that would make the
old sentence true. It does not detect every possible widening of rule B's match
families; those are measured by the reach sets in
`sdk/tests/test_rank_claim_surfaces.py`, not here.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "self_audit_for_message_tests", REPO / "scripts" / "self_audit.py")
sa = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = sa
_SPEC.loader.exec_module(sa)

BOARD = {"reissmann": 1, "wu": 2, "liu": 3, "montoya": 4}

#: The holder named one character outside the matched phrase.
NAMED_ADJACENT = "Yang: our margin over the leader is 0.0027."
#: The holder named nowhere at all.
NAMED_NOWHERE = "Our margin over the leader is 0.0027."


def _rule_b(text: str) -> list[str]:
    return sa.board_placement_faults(text, BOARD)[1]


class TheMessageSaysWhatTheRuleTestedTests(unittest.TestCase):

    def test_the_message_does_not_claim_the_holder_is_unnamed(self):
        """The regression this file exists for. Fails against the old text.

        The name `Yang` sits one character from the match. Any message saying
        the surface does not name who holds the position is simply false here,
        and it was printed against nine live occurrences in exactly this shape.
        """
        faults = _rule_b(NAMED_ADJACENT)
        self.assertEqual(1, len(faults), f"expected one rule-B fault: {faults}")
        message = faults[0]
        self.assertNotIn(
            "without naming who holds it", message,
            "the fault message claims the holder is not named, on a surface "
            f"that names Yang one character away:\n  {message}")

    def test_the_message_discloses_that_it_looked_at_the_phrase_only(self):
        """Narrowing a claim is not the same as deleting it.

        A message that merely dropped the false half would leave a reader
        guessing what WAS tested. It has to say.
        """
        message = _rule_b(NAMED_ADJACENT)[0]
        low = message.lower()
        self.assertIn("phrase", low,
                      f"the message does not say what it examined:\n{message}")
        self.assertTrue(
            "no proximity window" in low or "proximity" in low,
            f"the message does not disclose that there is no window:\n{message}")

    def test_the_same_text_is_printed_whether_or_not_the_holder_is_named(self):
        """Because the rule cannot tell those two surfaces apart.

        If the messages ever differ, the rule has grown a distinction its
        pattern does not have, and the message is again claiming more than was
        tested -- the same defect in the other direction.
        """
        adjacent = _rule_b(NAMED_ADJACENT)[0]
        nowhere = _rule_b(NAMED_NOWHERE)[0]
        # Drop the quoted excerpt itself, which legitimately differs -- one
        # surface capitalises `Our`. What must not differ is the CLAIM.
        strip = lambda m: m.split("' ", 1)[-1]                      # noqa: E731
        self.assertEqual(
            strip(adjacent), strip(nowhere),
            "rule B faults these two surfaces identically, so it must not "
            f"describe them differently:\n  {adjacent}\n  {nowhere}")

    def test_the_message_still_names_the_phrase_that_faulted(self):
        """The half of the old message that was true, kept.

        A fault a reader cannot locate is a fault they cannot repair.
        """
        self.assertIn("'our margin over the leader'", _rule_b(NAMED_ADJACENT)[0])


class TheRuleWasNotWidenedToEarnTheMessageTests(unittest.TestCase):
    """D54's load-bearing constraint, asserted rather than promised."""

    def test_the_name_one_character_away_still_faults(self):
        self.assertEqual(
            1, len(_rule_b(NAMED_ADJACENT)),
            "rule B stopped faulting a surface it faulted before the message "
            "was corrected. The message was the thing to fix; widening the "
            "rule so the author's own prose passes is how a guard gets tuned "
            "to a number (D54, and it is D77's question, not this one's)")

    def test_the_rule_still_has_no_window_at_any_distance(self):
        """No adjudication clause was added quietly at any radius.

        Rule A clears a wrong ordinal adjudicated within `_PLACE_ADJUDICATED`
        characters. Rule B has no such clause, and these distances -- inside
        that window, at its edge, and beyond it -- must all still fault.
        """
        for gap in (1, 50, 300, sa._PLACE_ADJUDICATED - 1,
                    sa._PLACE_ADJUDICATED + 1):
            with self.subTest(distance=gap):
                text = ("Yang holds the top score." + " x" * (gap // 2)
                        + " Our margin over the leader is 0.0027.")
                self.assertEqual(
                    1, len(_rule_b(text)),
                    f"a proximity clause appears to have been added at {gap} "
                    "characters. That is a rule change and needs its own row "
                    "and its own held-out set, not a message fix")

    def test_a_window_keyed_on_the_BOARD_is_caught_too(self):
        """The probe above cannot see the likelier mutation. Measured.

        Every other probe in this file names `Yang`, who is not on `BOARD` --
        he leads the LIVE six-entry board, and these probes pass the four-entry
        scoring pin. So a proximity clause written the way rule A's is, keyed
        on `_board_names(board)`, never fires on them: applied at `48d3f05a` it
        took `"Wu holds the top score. Our margin over the leader is 0.0027."`
        from one rule-B fault to zero while all 18 tests in this file and
        `test_two_board_referents.py` stayed green.

        The holder here is `Wu`, whom `BOARD` carries, so the clause fires and
        this reddens. Distances are the same five, for the same reason.
        """
        for gap in (1, 50, 300, sa._PLACE_ADJUDICATED - 1,
                    sa._PLACE_ADJUDICATED + 1):
            with self.subTest(distance=gap):
                text = ("Wu holds the top score." + " x" * (gap // 2)
                        + " Our margin over the leader is 0.0027.")
                self.assertEqual(
                    1, len(_rule_b(text)),
                    f"a board-keyed proximity clause appears to have been "
                    f"added at {gap} characters. That is a rule change and "
                    "needs its own row (D77) and its own held-out set, not a "
                    "message fix")

    def test_a_name_inside_the_phrase_is_still_the_only_thing_that_clears_it(self):
        self.assertEqual([], _rule_b("Our margin over Yang is 0.0027."),
                         "naming the entrant inside the phrase must still "
                         "clear rule B -- that is the whole rule")


if __name__ == "__main__":
    unittest.main()
