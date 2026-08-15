"""The rank-claim guard must grade VALUE, not only FORM.

THE DEFECT THESE TESTS PIN, reproduced at HEAD `82fb3d46` before any repair.
`check_rank_claim_surfaces` DOES open `dist/certonomous-demo.zip`, DOES read
member `certonomous-demo/site/closure.html`, DOES recognise its line 502 as a
rank claim -- and reported

    [WARN] rank claims carry their probability
           every travelling surface complies; 27 lab record(s) claim rank 1
           without what V8 requires

over the sentence "rank 1 of 5 is our local scoring at a pinned benchmark
commit, with a seed-uncertainty bound comparable to its margin." Against the
live six-entry board that is rank 1 of SEVEN, and the bound is 177% of the
margin -- it exceeds what it is called comparable to. Perfectly formed,
entirely false, and the verdict said compliant.

**A false clean is worse than a blind spot.** A blind spot reports nothing. A
form check on a stale artifact reports agreement, and the report gets quoted
as reassurance.

WHAT THIS SUITE ASSERTS, and the halves it keeps apart:

  * FORM AND VALUE ARE TWO VERDICTS. A test that accepts one merged verdict
    would pass on a merge, and a merge is how a green on one hides a red on
    the other.
  * THE POSITIVE CONTROL IS THE SHIPPED ARTIFACT. Not a fixture: the real
    member of the real archive, which must now FAIL.
  * THE MUST-NOT-MATCH HALF IS THE HARDER ONE (L-84). A positive control
    proves an instrument can fire, not that it fires only where it should. A
    correct current claim must PASS, and **a correctly dated historical claim
    must not fail** -- this corpus is full of legitimate four-entry records
    and a check that reddens on dated history is unusable within a week.
  * NO FIGURE IS TYPED HERE. The board is driven synthetically in the
    derivation tests, so a guard that satisfies them by holding `7` as a
    constant fails: the count must follow the board it is given.

Against the code as it stood before 2026-08-15 every test below errors at
`check_rank_claim_values`, which did not exist.
"""

from __future__ import annotations

import copy
import importlib.util
import io
import sys
import unittest
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "self_audit_rank_values", REPO / "scripts" / "self_audit.py")
sa = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = sa
_SPEC.loader.exec_module(sa)

CDF, _WHY = sa._derived_figures()


def facts_now():
    return copy.deepcopy(sa._closure_facts())


def grade(text, facts=None, ratio=(177.12, 178.82)):
    """(faults, ungraded) for one surface, against the live board by default."""
    return sa._rank_value_faults(text, CDF, facts or facts_now(), *ratio)


def rules(faults):
    return sorted(rule for _, rule, _ in faults)


#: A whole-corpus sweep is ~20,500 files and the suite asks for the unpatched
#: verdict five times. Memoised HERE and not in the audit: a cache inside the
#: check would be one more thing that can go stale between a patched call and
#: an unpatched one, which is the class of defect this suite exists for.
_VERDICTS: dict = {}


def verdict(check):
    if check.__name__ not in _VERDICTS:
        _VERDICTS[check.__name__] = check()
    return _VERDICTS[check.__name__]


class TheFormGuardDoesNotGradeValueTests(unittest.TestCase):
    """The defect itself, kept as an executable statement of it."""

    def test_the_form_guard_clears_a_well_formed_falsehood(self):
        # This is not a bug report about the form guard. It is the reason the
        # value guard exists, and it must keep being true: form and value are
        # different questions and the form guard answers only one.
        false_but_formed = (
            "Our 0.0566 is rank 1 of 5 on the published board, scored locally "
            "at deb91557 against the closure challenge leaderboard.\n"
            f"P(rank 1) = {sa._closure_facts()['p_rank1']}%, and eight cases "
            f"cannot pin that tighter than {sa._rank_interval_phrase()}.\n"
            "The leads over Yang and Reissmann are not statistically decided.\n")
        self.assertEqual(sa._rank_companions_missing(false_but_formed), [],
                         "the planted sentence must be FORM-CLEAN, or this "
                         "test is not about the defect")
        self.assertTrue(sa._rank_claim_lines(false_but_formed),
                        "and it must be recognised as a rank claim")
        faults, _ = grade(false_but_formed)
        self.assertIn("our placement", rules(faults))

    def test_the_two_verdicts_are_separate_results(self):
        form = verdict(sa.check_rank_claim_surfaces)
        value = verdict(sa.check_rank_claim_values)
        self.assertNotEqual(form.name, value.name)
        self.assertIn(sa.check_rank_claim_values, sa.CHECKS)
        self.assertIn("check_rank_claim_values", sa.BASIS)
        self.assertIn("check_rank_claim_values", sa.REMEDIES)

    def test_the_form_verdict_says_it_is_about_form(self):
        # The sentence that got quoted as reassurance was "every travelling
        # surface complies". It must never again read as a statement that a
        # page is right.
        form = verdict(sa.check_rank_claim_surfaces)
        blob = (form.summary + " " + " ".join(form.detail)).lower()
        self.assertIn("form", blob)


class ThePositiveControlIsTheShippedArtifactTests(unittest.TestCase):

    MEMBER = "certonomous-demo/site/closure.html"

    def test_the_shipped_bundle_member_is_read_and_now_fails(self):
        archives = sa._shipping_archives()
        self.assertTrue(archives, "there is no shipping archive to control on")
        with zipfile.ZipFile(archives[0]) as zf:
            text = zf.read(self.MEMBER).decode("utf-8")
        self.assertIn(502, sa._rank_claim_lines(text),
                      "the form guard must still SEE the claim; a value guard "
                      "that only works where the form guard is blind proves "
                      "nothing about this defect")
        faults, _ = grade(text)
        lines = {line for line, _, _ in faults}
        self.assertIn(502, lines, "the shipped `rank 1 of 5` must FAIL")
        self.assertTrue({"our placement", "bound vs margin"} <= set(rules(faults)),
                        f"both withdrawn claims in that sentence must fire; "
                        f"got {rules(faults)}")

    def test_the_whole_check_fails_and_names_the_member(self):
        result = verdict(sa.check_rank_claim_values)
        self.assertEqual(result.status, sa.FAIL)
        named = [d for d in result.detail if self.MEMBER in d]
        self.assertTrue(named, "the FAIL must name the member, not a count")

    def test_a_planted_well_formed_falsehood_fails(self):
        planted = (
            "On the live leaderboard our entry is rank 1 of 5 and the "
            "seed-uncertainty bound is comparable to the margin over the "
            "published leader.\n")
        faults, _ = grade(planted)
        self.assertEqual(rules(faults), ["bound vs margin", "our placement"])


class TheMustNotMatchHalfTests(unittest.TestCase):
    """L-84: a positive control proves an instrument can fire, not that it
    fires only where it should."""

    def test_a_correct_current_claim_passes(self):
        facts = facts_now()
        correct = (
            f"On the published board our 0.0566 is rank 1 of "
            f"{facts['entries'] + 1} counting us, scored locally at "
            f"deb91557. Best-on-board is {len(facts['best'])} of 8 and the "
            f"count belonging to our model is {len(facts['earned'])} of 8. "
            f"The seed bound is 177% of the margin, so it exceeds it.\n")
        faults, _ = grade(correct)
        self.assertEqual(faults, [], f"a correct claim must not fault: {faults}")

    def test_correctly_dated_history_does_not_fail(self):
        dated = (
            "## 3. Standings\n"
            "\n"
            "> **Superseded 2026-08-11, see the six-entry board.** The record "
            "below stands unchanged as the four-entry record.\n"
            "\n"
            "Our 0.0566 was rank 1 of 5 on the published board, best-on-board "
            "4 of 8, scored locally at deb91557.\n")
        faults, ungraded = grade(dated)
        self.assertEqual(faults, [],
                         f"a dated historical section must not fault: {faults}")
        self.assertTrue(any("dated historical section" in u for u in ungraded),
                        "and it must SAY it declined to grade it, not go quiet")

    def test_the_same_history_UNDATED_still_fails(self):
        # The discriminator is the DATE. Without it the exemption would clear
        # every stale claim that says the word "superseded" anywhere near it,
        # which is most of this corpus.
        undated = (
            "## 3. Standings\n"
            "\n"
            "> **Superseded, see the six-entry board.** The record below "
            "stands unchanged.\n"
            "\n"
            "Our 0.0566 was rank 1 of 5 on the published board, scored "
            "locally at deb91557.\n")
        faults, _ = grade(undated)
        self.assertIn("our placement", rules(faults))

    def test_the_banner_itself_is_live_text_and_is_graded(self):
        # D150 / CLOSURE_CHALLENGE_STATUS.md:691. A supersession banner is
        # written in the PRESENT TENSE about the CURRENT record; the notes
        # BELOW it are history. Masking from the heading swallowed a live
        # wrong claim for four days.
        text = (
            "## 3. Our overall number and position\n"
            "\n"
            "> **Superseded again 2026-08-07, see the round-5 section.** The "
            "entry of record is now round 5: overall 0.0566, **rank 1 of 5 "
            "scored locally at benchmark commit `deb91557`**. The notes below "
            "stand as the superseded round-3 record.\n"
            "\n"
            "Our 0.0654 was rank 3 of 5 on the published board at deb91557.\n")
        faults, _ = grade(text)
        lines = {line for line, _, _ in faults}
        self.assertIn(3, lines, "the banner's own live claim must fault")
        self.assertNotIn(5, lines, "the history below it must not")

    def test_a_quoted_defect_is_not_a_fresh_defect(self):
        # D71: a docket row that quotes its own false positive files a fresh
        # fault. Every sweep document in this corpus enumerates stale figures.
        quoting = (
            'The shipped page still reads "rank 1 of 5 scored locally at '
            'deb91557 on the board", which is wrong.\n')
        faults, _ = grade(quoting)
        self.assertEqual(faults, [])

    def test_a_struck_claim_is_not_a_live_one(self):
        for struck in (
                "~~Our 0.0566 is rank 1 of 5 on the published board at "
                "deb91557.~~\n",
                "<s>Our 0.0566 is rank 1 of 5 on the published board at "
                "deb91557.</s>\n",
                "Our count \\sout{\\textbf{rank 1 of 5}} on the board at "
                "deb91557.\n"):
            with self.subTest(struck=struck[:20]):
                faults, _ = grade(struck)
                self.assertEqual(faults, [], f"struck text faulted: {faults}")

    def test_somebody_elses_placement_on_the_frozen_pin_is_declined(self):
        text = ("On the frozen scoring pin `deb91557` Reissmann is rank 1 of "
                "four on the published board.\n")
        faults, ungraded = grade(text)
        self.assertEqual(faults, [])
        self.assertTrue(any("FROZEN SCORING PIN" in u for u in ungraded))

    def test_a_third_partys_published_board_reading_passes(self):
        ranks = sa._live_ranks()
        facts = facts_now()
        last = max((n for n in ranks if n), key=lambda n: ranks[n])
        published = ranks[last] - 1 if ranks[last] > ranks[""] else ranks[last]
        text = (f"{last} is now rank {published} of {facts['entries']} on the "
                f"published board of the closure challenge.\n")
        faults, _ = grade(text)
        self.assertEqual(faults, [], f"a correct third-party claim: {faults}")

    def test_a_third_partys_wrong_placement_fails(self):
        ranks = sa._live_ranks()
        last = max((n for n in ranks if n), key=lambda n: ranks[n])
        facts = facts_now()
        text = (f"{last} is rank 2 of {facts['entries']} on the published "
                f"board of the closure challenge.\n")
        faults, _ = grade(text)
        self.assertIn("third-party placement", rules(faults))

    def test_the_left_of_a_correction_is_the_retired_value(self):
        text = ("On the six-entry board the best-on-board count falls from 4 "
                "of 8 to 2 of 8 on the leaderboard.\n")
        faults, _ = grade(text)
        self.assertEqual(faults, [], f"the correction faulted: {faults}")

    def test_measured_false_positive_rate_is_reported_not_assumed(self):
        # Not a threshold. The corpus run must PRODUCE a triage-able list --
        # every fault carries a file, a line and a named rule -- because a
        # count with no addresses cannot be triaged and gets ignored.
        result = verdict(sa.check_rank_claim_values)
        addressed = [d for d in result.detail
                     if not d.startswith(("frame:", "ungraded:", "NOT GRADED"))]
        self.assertTrue(addressed)
        for entry in addressed:
            self.assertRegex(entry, r":\d+ \[[a-z\- ]+\] ")


class TheEmptySetIsNotAgreementTests(unittest.TestCase):
    """Defect class B1, on the check that arrived at a false clean."""

    def test_no_claims_found_is_UNKNOWN_not_PASS(self):
        for check in (sa.check_rank_claim_surfaces, sa.check_rank_claim_values):
            with self.subTest(check=check.__name__):
                tracked, archives = sa._tracked_files, sa._shipping_archives
                sa._tracked_files = lambda: []
                sa._shipping_archives = lambda: []
                try:
                    result = check()
                finally:
                    sa._tracked_files = tracked
                    sa._shipping_archives = archives
                self.assertEqual(result.status, sa.UNKNOWN,
                                 "a check that examined nothing must not PASS")

    def test_git_unavailable_is_UNKNOWN_not_WARN(self):
        for check in (sa.check_rank_claim_surfaces, sa.check_rank_claim_values):
            with self.subTest(check=check.__name__):
                original = sa._tracked_files
                sa._tracked_files = lambda: None
                try:
                    result = check()
                finally:
                    sa._tracked_files = original
                self.assertEqual(result.status, sa.UNKNOWN)

    def test_an_unreadable_archive_is_not_a_clean_member(self):
        # It used to be appended as a surface whose text was the empty string.
        # An empty string makes no claim, raises no fault, and reads on the
        # report as a clean member.
        original = sa._shipping_archives
        broken = REPO / "sdk" / "tests" / "fixtures"
        sa._shipping_archives = lambda: [broken / "no-such-archive.zip"]
        sa._travelling_names.cache_clear() if hasattr(
            sa._travelling_names, "cache_clear") else None
        try:
            result = sa.check_rank_claim_values()
        finally:
            sa._shipping_archives = original
        self.assertNotEqual(result.status, sa.PASS)
        self.assertTrue(any("could not be opened" in d or "unreadable" in d
                            for d in result.detail),
                        "the unopened archive must reach the verdict")

    def test_the_arithmetic_module_missing_is_UNKNOWN(self):
        original = sa._derived_figures
        sa._derived_figures = lambda: (None, "driven failure")
        try:
            result = sa.check_rank_claim_values()
        finally:
            sa._derived_figures = original
        self.assertEqual(result.status, sa.UNKNOWN)
        self.assertTrue(any("driven failure" in d for d in result.detail))


class TheValuesAreDerivedNotTypedTests(unittest.TestCase):
    """A guard that satisfies the controls by holding `7` fails here."""

    def _synthetic(self, entries):
        facts = facts_now()
        facts["entries"] = entries
        return facts

    def test_the_denominator_follows_the_board_it_is_given(self):
        for entries in (3, 4, 6, 9):
            with self.subTest(entries=entries):
                facts = self._synthetic(entries)
                right = (f"Our entry is rank 1 of {entries + 1} on the "
                         f"published board at deb91557.\n")
                wrong = (f"Our entry is rank 1 of {entries + 2} on the "
                         f"published board at deb91557.\n")
                self.assertEqual(grade(right, facts)[0], [])
                self.assertIn("our placement", rules(grade(wrong, facts)[0]))

    def test_the_best_on_board_count_follows_the_entry_of_record(self):
        facts = facts_now()
        facts["best"] = ["a", "b", "c"]
        facts["earned"] = ["a"]
        for count, should_fault in ((3, False), (1, False), (4, True)):
            with self.subTest(count=count):
                text = (f"We hold the best score on the leaderboard on "
                        f"{count} of 8 cases at deb91557.\n")
                faults = grade(text, facts)[0]
                self.assertEqual(bool(faults), should_fault, f"{faults}")

    def test_comparable_is_graded_against_the_ratio_it_is_given(self):
        text = ("The seed-uncertainty bound on the board is comparable to the "
                "margin over the published leader at deb91557.\n")
        self.assertEqual(rules(grade(text, ratio=(177.12, 178.82))[0]),
                         ["bound vs margin"])
        self.assertEqual(grade(text, ratio=(83.0, 84.0))[0], [],
                         "a bound the margin covers is comparable to it")
        faults, ungraded = grade(text, ratio=(95.0, 105.0))
        self.assertEqual(faults, [], "a straddling ratio decides nothing")
        self.assertTrue(any("straddles 100%" in u for u in ungraded),
                        "and it must SAY it cannot decide")

    def test_the_arithmetic_and_the_masker_are_imported_not_copied(self):
        module, why = sa._derived_figures()
        self.assertIsNotNone(module, why)
        source = (REPO / "scripts" / "self_audit.py").read_text(
            encoding="utf-8")
        self.assertNotIn("def mask_exempt", source,
                         "the masker must be imported, not re-implemented")
        self.assertNotIn("def agrees(", source,
                         "the half-ulp predicate must be imported")
        self.assertIs(module.mask_exempt.__module__, module.__name__)


class TheDeferralHasAReceivingEndTests(unittest.TestCase):
    """D151: `_PLACE_OFN` deferred `rank N of M` to a sibling that did not
    grade it, so no instrument in this lab held a denominator predicate."""

    def test_the_deferred_class_is_now_graded(self):
        text = ("Our entry is rank 1 of 5 on the published board at "
                "deb91557.\n")
        self.assertTrue(sa._PLACE_OFN.match(" of 5"),
                        "the word-form guard still defers this shape")
        self.assertIn("our placement", rules(grade(text)[0]),
                      "and the receiver must actually grade it")

    def test_the_deferral_comment_names_a_check_that_exists(self):
        source = (REPO / "scripts" / "self_audit.py").read_text(
            encoding="utf-8")
        head = source.index("_PLACE_OFN = re.compile")
        near = source[head - 1200:head + 400]
        self.assertIn("check_rank_claim_values", near,
                      "a deferral must name a receiver that does the thing")


if __name__ == "__main__":
    unittest.main()
