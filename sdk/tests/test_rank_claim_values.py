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

    def test_the_shipped_best_on_board_count_is_reached_at_last(self):
        """D236, on the artifact and not on a fixture.

        Member line 341-342 wraps mid-claim: "and our best-on-board count" /
        "drops <b>5 of 8 -> 4 of 8</b>". V14's ruling recorded this as
        "structurally unreachable by any board arithmetic ... needs a human
        reading"; its author withdrew that at `b2668906` once the obstruction
        was executed and turned out to be the line break. Against the live
        board the count is 2 of 8 and the count belonging to our model is 0,
        so `4 of 8` is false and must fault.

        WHEN `dist/` IS REBUILT this control goes green-by-absence, exactly as
        its neighbours in this class do -- the tracked source already carries
        the correction at `demo-output/website/closure.html:358`. That is the
        residual on V14's face, not a defect in this test.
        """
        faults, _ = grade(self._member())
        named = [m for line, rule, m in faults
                 if rule == "best-on-board count"]
        self.assertTrue(
            named,
            "the wrapped best-on-board claim in the shipping member went "
            "ungraded; that is the newline defect D236 repaired")
        self.assertTrue(any("`4 of eight`" in m for m in named),
                        f"the rule fired on the wrong value: {named}")

    def _member(self):
        archives = sa._shipping_archives()
        self.assertTrue(archives, "there is no shipping archive to control on")
        with zipfile.ZipFile(archives[0]) as zf:
            return zf.read(self.MEMBER).decode("utf-8")

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

    def test_the_count_rule_crosses_a_soft_wrap(self):
        """D236. The obstruction was a newline, not board arithmetic.

        THE SPECIFICATION THIS IS DERIVED FROM, and it is not the pattern:
        V14's ruling `9b9951a1` called the shipped sentence "structurally
        unreachable by any board arithmetic ... that one needs a human
        reading", and its author withdrew that at `b2668906` because the only
        obstruction was a 25-character gap containing a line break. So the
        claim must be graded when it wraps, and the value it must name is the
        one the sentence asserts.
        """
        # The shipped shape: the noun phrase ends one line, the count begins
        # the next, inside an inline tag. Written out rather than read from
        # `dist/`, because a test that reads the artifact under repair cannot
        # say whether the artifact or the rule moved.
        text = ("On the closure leaderboard the tie is gone and our "
                "best-on-board count\ndrops <b>4 of 8</b> today.\n")
        faults, _ = grade(text)
        self.assertIn("best-on-board count", rules(faults),
                      "a wrapped best-on-board claim went ungraded, which is "
                      "the defect D236 repaired")
        # NAME the thing, do not count it: an assertion on the number of faults
        # survives a rule that fires on the wrong value.
        self.assertTrue(
            any("`4 of eight`" in m for _, r, m in faults
                if r == "best-on-board count"),
            f"the rule fired but did not name the claimed value: {faults}")

    def test_the_same_claim_unwrapped_grades_identically(self):
        # The two readings must agree, or the repair has made the verdict
        # depend on where the line happens to break.
        wrapped = ("On the closure leaderboard the tie is gone and our "
                   "best-on-board count\ndrops <b>4 of 8</b> today.\n")
        flat = wrapped.replace("count\ndrops", "count drops")
        self.assertEqual(
            [(r, m) for _, r, m in grade(wrapped)[0]],
            [(r, m) for _, r, m in grade(flat)[0]],
            "the wrapped and unwrapped spellings of one claim graded "
            "differently")

    def test_the_gap_stops_at_a_block_boundary(self):
        """THE BOUND, and this half is the proof of it (L-84).

        A newline is not the only thing that ends a claim. Deleting the
        exclusion outright lets `best` in one block bind to a count in the
        next, which manufactures a fault out of two unrelated sentences --
        strictly worse than the miss it repairs, because a false fault is what
        gets a guard switched off. Every case below is a SUBJECT and a COUNT
        that belong to different blocks, and none of them may match.
        """
        hazards = {
            "paragraph break":
                "we are best on the ducts of the board.\n\nSeparately, Yang "
                "wins 4 of 8 cases",
            "blank line carrying whitespace":
                "our best-on-board count is settled\n   \nYang takes 4 of 8 "
                "cases on the board",
            "table row boundary":
                "| metric | best-on-board |\n| Yang wins | 4 of 8 |",
            "markdown heading":
                "which board entrant is best\n## Yang takes 4 of 8 cases",
            "bullet":
                "the best board entrants are ranked\n- Yang wins 4 of 8 cases",
            "ordered list item":
                "the best board entrants are ranked\n1. Yang wins 4 of 8",
            "blockquote":
                "we are best on the board\n> Yang wins 4 of 8 cases",
            "html block opens":
                "we are best on the board\n<p>Yang wins 4 of 8 cases</p>",
            "html block closes":
                "we are best on the board\n</p><p>Yang wins 4 of 8 cases",
            "sentence boundary":
                "we are best on the board. Yang wins 4 of 8 cases",
            "the 80-character budget still binds":
                "best on the board " + "x" * 60 + "\n" + "y" * 30 + " 4 of 8",
        }
        for name, text in hazards.items():
            with self.subTest(hazard=name):
                self.assertIsNone(
                    sa._BEST_COUNT.search(text),
                    f"the count rule bound a subject to a count across a "
                    f"{name}; the gap may cross a SOFT WRAP and nothing else")

    def test_a_soft_wrap_is_still_allowed_inside_the_block(self):
        # The other half of the bound: it must not be so tight that it
        # re-creates the defect. Each of these is ONE claim that happens to
        # wrap, and each must match.
        for text in ("our best-on-board count is\nstill **4 of 8** today",
                     "our best-on-board count\ndrops <b>4 of 8</b> today",
                     "we are best on the board on\nfour of the eight cases"):
            with self.subTest(text=text):
                self.assertIsNotNone(sa._BEST_COUNT.search(text))

    def test_the_denominator_of_eight_is_not_a_decimal(self):
        """The sibling defect `f4c531cb` closed on `_VALUE_BOARD_SIZE`.

        `\\b` succeeds between `8` and `.`, so `of 8.5` used to read as a board
        of eight cases. Residual 4 on V14's face; closed here by the same
        `(?![.,]\\d)` guard.
        """
        for text in ("we are best on the board on 4 of 8.5 cases",
                     "we are best on the board on 4 of 8,5 cases"):
            with self.subTest(text=text):
                self.assertIsNone(
                    sa._BEST_COUNT.search(text),
                    "the integer part of a decimal was read as the board of "
                    "eight cases")
        # And the numerator needs no guard of its own -- MEASURED, not assumed:
        # the gap class still excludes `.`, so it cannot reach across `0.`
        self.assertIsNone(
            sa._BEST_COUNT.search("we are best on the board on 0.5 of 8"))
        self.assertIsNotNone(
            sa._BEST_COUNT.search("we are best on the board on 4 of 8 cases"),
            "and the honest claim must still be graded")

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


class TheBareOrdinalIsInsideTheRegexNowTests(unittest.TestCase):
    """Chief ruling `9b9951a1` on V14's denominator gap, measured at `86dd1866`.

    `_VALUE_BOARD_SIZE` required the literal token `rank`, so `2nd of 5` fell
    outside its REGEX and not outside its arithmetic. Four of the five
    four-entry claims a repo-wide denominator measurement found in the shipping
    archive carry no `rank` token. The ruling: widen this one pattern; a second
    instrument would duplicate a working arithmetic core to reach a string form.

    THE MUST-NOT-MATCH HALF IS THE HARDER ONE (L-84), and for this widening it
    is harder still, because the numerator of a bare ordinal is UNDECIDABLE:
    `4th of 7` is the correct live per-case ordinal for one duct and the wrong
    overall one. A widening that graded it against the overall sort would fault
    a CORRECT travelling claim, which is the outcome the ruling itself names as
    reversing it. So the denominator is graded and the numerator is not, and
    both halves are asserted here.
    """

    ARCHIVE_MEMBER = "certonomous-demo/site/closure.html"

    def _member(self):
        archives = sa._shipping_archives()
        self.assertTrue(archives, "there is no shipping archive to control on")
        with zipfile.ZipFile(archives[0]) as zf:
            return zf.read(self.ARCHIVE_MEMBER).decode("utf-8")

    # ---- the aimed test: the widening's own positive control ----------------

    def test_the_shipped_bare_ordinal_now_faults(self):
        """The widening's own positive control, on the real shipped member.

        `dist/certonomous-demo.zip!certonomous-demo/site/closure.html:341`
        reads "the case falls to 3rd of 5". Against the live six-entry board
        there is no placement out of five.

        THIS PROBE NAMES ITS CLAIM RATHER THAN COUNTING THE LINE'S FAULTS, and
        it was rewritten on 2026-08-16 (D236) because the counting form was
        wrong in a way that mattered. It asserted the line's fault list equalled
        exactly `[(341, "board size")]`, which reads as "the bare ordinal is
        graded as a denominator" and actually says "no other rule may ever fault
        this line". Those are different sentences, and the second is not this
        class's specification: line 341 also carries "our best-on-board count
        drops 5 of 8 -> 4 of 8", a SECOND and DIFFERENT wrong claim that
        `_BEST_COUNT` could not reach while its gap class excluded the newline
        it wraps on. When that was repaired the count fault appeared here and
        reddened a test whose stated intent it satisfies. An over-specified
        probe fails on correct changes, and the cheapest way to green it is to
        undo the repair.
        """
        faults, _ = grade(self._member())
        at_341 = {rule for line, rule, _ in faults if line == 341}
        self.assertIn("board size", at_341,
                      f"the shipped `3rd of 5` must fault; got {sorted(faults)}")
        # ... and as a DENOMINATOR fault. The numerator of a bare ordinal is
        # undecidable (see this class's docstring), so grading it against the
        # overall sort would fault a correct travelling claim -- the outcome
        # the ruling names as reversing the widening.
        self.assertNotIn("our placement", at_341,
                         "the bare ordinal was graded against the overall "
                         "sort; only its DENOMINATOR is decidable")
        self.assertTrue(
            any("`3rd of 5`" in m for line, rule, m in faults
                if line == 341 and rule == "board size"),
            "the denominator fault did not name the claim it is about")

    def test_a_bare_ordinal_with_a_wrong_denominator_faults(self):
        facts = facts_now()
        # No pin token in this sentence: `deb91557` would make it a claim
        # about the FOUR-entry board and the check would decline it, which the
        # frozen-pin control below asserts separately.
        text = (f"On the closure challenge leaderboard the case falls to 3rd "
                f"of {facts['entries'] - 1}.\n")
        self.assertIn("board size", rules(grade(text, facts)[0]))

    def test_the_denominator_follows_the_board_for_bare_ordinals_too(self):
        # A guard that satisfies the control by holding `7` fails here.
        for entries in (3, 4, 6, 9):
            with self.subTest(entries=entries):
                facts = facts_now()
                facts["entries"] = entries
                right = (f"On the closure challenge board the duct sits 2nd "
                         f"of {entries + 1}.\n")
                wrong = (f"On the closure challenge board the duct sits 2nd "
                         f"of {entries + 2}.\n")
                self.assertEqual(grade(right, facts)[0], [],
                                 "an admissible denominator must not fault")
                self.assertIn("board size", rules(grade(wrong, facts)[0]))

    def test_the_rank_branch_is_unchanged_by_the_widening(self):
        # The widening inserted an alternative; it must not have moved the
        # branch that was already working.
        text = ("Our entry is rank 1 of 5 on the published board at "
                "deb91557.\n")
        self.assertIn("our placement", rules(grade(text)[0]))

    # ---- the must-not-match half (L-84) ------------------------------------

    def test_a_correct_current_bare_ordinal_does_not_fault(self):
        # THE REVERSAL CONDITION the ruling names, as an executable statement:
        # a travelling surface whose CORRECT claim this predicate faults. The
        # live per-case ordinals are 2, 2, 1, 1, 3, 4, 4 and 7 of seven, so
        # every one of these is right and none may fault.
        facts = facts_now()
        for n in (1, 2, 3, 4, 7):
            with self.subTest(n=n):
                text = (f"On the closure challenge leaderboard this case is "
                        f"{n}{'st' if n == 1 else 'nd' if n == 2 else 'rd' if n == 3 else 'th'} "
                        f"of {facts['entries'] + 1}.\n")
                faults, ungraded = grade(text, facts)
                self.assertEqual(faults, [],
                                 f"a correct live ordinal faulted: {faults}")
                self.assertTrue(
                    any("NUMERATOR is not graded" in u for u in ungraded),
                    "and the check must SAY which half it declined to grade, "
                    "not go quiet about it")

    def test_a_correctly_dated_historical_bare_ordinal_does_not_fault(self):
        dated = (
            "## 4. Per-case standings\n"
            "\n"
            "> **Superseded 2026-08-11, see the six-entry board.** The record "
            "below stands unchanged as the four-entry record.\n"
            "\n"
            "On the published board the aspect-ratio-1 duct was 2nd of 5 and "
            "the aspect-ratio-3 duct 3rd of 5, scored locally.\n")
        faults, ungraded = grade(dated)
        self.assertEqual(faults, [],
                         f"a dated historical section must not fault: {faults}")
        self.assertTrue(any("dated historical section" in u for u in ungraded))

    def test_a_bare_ordinal_bound_to_the_frozen_pin_is_declined(self):
        text = ("On the frozen scoring pin `deb91557` the aspect-ratio-1 duct "
                "is 2nd of 4 on the published board.\n")
        faults, ungraded = grade(text)
        self.assertEqual(faults, [])
        self.assertTrue(any("FROZEN SCORING PIN" in u for u in ungraded))

    def test_the_adjoint_iteration_counter_does_not_match_at_all(self):
        # The measurement behind the ruling found a single adjoint progress
        # counter contributing 7,671 of 7,685 gitignored faults. It carries no
        # ordinal suffix, so the widened pattern cannot see it -- and neither
        # can the cheap trigger, which is asserted separately because a rule
        # that never runs is not the same as a rule that declines.
        for counter in ("Major iteration 31 of 47, C_d 0.021 on the board",
                        "Major iteration 5 of 47 on the leaderboard",
                        "FD3 select shape: argmax|g| index 115 of 120"):
            with self.subTest(counter=counter):
                self.assertIsNone(sa._VALUE_BOARD_SIZE.search(counter))
                faults, _ = grade(counter + "\n")
                self.assertEqual(faults, [], f"{counter}: {faults}")

    # ---- word boundaries, proved rather than read (the `duct`/`product`
    #      substring class the measurement found inside its own instrument) ---

    def test_the_ordinal_is_taken_whole_and_never_as_a_substring(self):
        m = sa._VALUE_BOARD_SIZE.search("the 21st of 50 samples")
        self.assertIsNotNone(m)
        self.assertEqual(m.group("o"), "21",
                         "a leading `\\b` must take `21st` whole; taking `1st` "
                         "out of `21st` is the `68%`-inside-`1.68%` defect")
        self.assertEqual(m.group(0), "21st of 50")

    def test_an_ordinal_glued_into_a_longer_token_does_not_match(self):
        for glued in ("v3rd of 5", "x21st of 50", "3rdx of 5", "1sts of 5",
                      "rev2nd of 5"):
            with self.subTest(glued=glued):
                self.assertIsNone(sa._VALUE_BOARD_SIZE.search(glued),
                                  f"{glued} matched; the boundaries are wrong")

    #: The exact sentence, byte for byte, from
    #: `demo-output/website/latex/closure_challenge_report.tex:1890`. It is a
    #: claim about a MARGIN and about nothing else.
    TEX_1890 = "  seed, against a gap to rank 2 of 0.0030."

    def test_a_margin_is_not_a_denominator(self):
        """V16 round 11 (`94419cc8`, D189-D194).

        `\\b` after `\\d{1,3}` falls between the `0` and the decimal point, so
        this pattern used to read `rank 2 of 0` out of a sentence about a gap
        and grade `0` as the size of the board. On the real file it was held
        back by ONE gate -- `_in_board_context` -- and not by the strike masker,
        which leaves that passage byte-identical. The bare-ordinal branch this
        suite exists for makes that surface bigger, so the two are controlled
        together.
        """
        self.assertIsNone(sa._VALUE_BOARD_SIZE.search(self.TEX_1890),
                          "a margin was read as a board size")

    def test_a_margin_is_not_a_denominator_even_beside_the_word_board(self):
        # The gate that held it is one word away from opening. This must hold
        # when it does, because the .tex IS a document about a leaderboard.
        for sentence in (
                self.TEX_1890.rstrip(".") + " on the published board.",
                "the duct closes a gap to 2nd of 0.0030 on the board",
                "the case sits 3rd of 0.0592 behind the board leader",
                "a lead of rank 2 of 100.5 on the leaderboard"):
            with self.subTest(sentence=sentence[:40]):
                self.assertIsNone(sa._VALUE_BOARD_SIZE.search(sentence),
                                  "a decimal was read as a denominator")
                self.assertEqual(grade(sentence + "\n")[0], [],
                                 "and it must not reach a verdict either")

    def test_an_integer_denominator_ending_a_clause_still_matches(self):
        # The lookahead must exclude decimals and NOTHING else: a denominator
        # is allowed to end a sentence or a clause.
        for sentence in ("Our entry is rank 1 of 5.",
                         "Our entry is rank 1 of 5, on the published board.",
                         "the duct sits 3rd of 5."):
            with self.subTest(sentence=sentence):
                self.assertIsNotNone(sa._VALUE_BOARD_SIZE.search(sentence))

    def test_the_bare_branch_cannot_swallow_rule_v2s_spans(self):
        # The measurement found its own ordinal family eating its count family,
        # so the CORRECT `2 of 8` best-on-board count was reported as a wrong
        # denominator. The ordinal suffix is what keeps them disjoint.
        for count in ("4 of 8", "2 of 8", "5 of 8", "6 of the eight rows"):
            with self.subTest(count=count):
                self.assertIsNone(
                    sa._VALUE_BOARD_SIZE.search(f"best on the board on {count}"),
                    f"the ordinal rule matched `{count}`, which belongs to the "
                    f"best-on-board rule")
        self.assertIsNotNone(
            sa._BEST_COUNT.search("we are best on the board on 4 of 8 cases"),
            "and the count rule must still hold its own family")

    def test_the_correction_arrow_still_retires_its_left_operand(self):
        text = ("On the six-entry board the duct falls from 2nd of 5 to 3rd "
                "of 7 on the leaderboard.\n")
        faults, _ = grade(text)
        self.assertEqual(faults, [],
                         f"the announcement of a correction faulted: {faults}")

    # ---- the blindfold: take the evidence away and the verdict must move ----

    def test_blindfolding_the_board_removes_the_new_fault(self):
        """`fb30e00f`'s rule, applied to this widening.

        An identical verdict with the named source record removed means the
        check was not using it. For a pattern widening that is the whole risk:
        a rule that fires on the STRING `3rd of 5` rather than on arithmetic
        over the board would survive the blindfold, and that is the
        form-over-value defect this entire line of work exists to remove.

        `_PROB_SCRIPT` is repointed at a path that does not exist, which is how
        the record actually becomes unreadable -- `_module_literal` reads it
        with `Path.read_text`, so nothing here depends on import machinery.
        Every `lru_cache` in the chain is cleared on the way in AND on the way
        out; a cache left warm would hand the blinded run the sighted answer
        and the test would pass for the wrong reason.
        """
        member = self._member()
        sighted = [(l, r) for l, r, _ in grade(member)[0] if r == "board size"]
        self.assertIn((341, "board size"), sighted,
                      "the sighted run must produce the fault being tested")

        original = sa._PROB_SCRIPT
        caches = (sa._closure_facts, sa._live_ranks)
        try:
            sa._PROB_SCRIPT = original.with_name("no-such-board-record.py")
            for cache in caches:
                cache.cache_clear()
            blind = sa._closure_facts()
            self.assertTrue(blind["stale"],
                            "the blindfold did not actually blind anything")
            blind_faults, _ = sa._rank_value_faults(
                member, CDF, blind, 177.12, 178.82)
            self.assertEqual(
                [(l, r) for l, r, _ in blind_faults if r == "board size"], [],
                "the denominator fault SURVIVED the board being removed, so "
                "it is matching text and not grading arithmetic")
            result = sa.check_rank_claim_values()
            self.assertEqual(result.status, sa.UNKNOWN,
                             "and the whole check must say it graded nothing, "
                             "not report a clean corpus")
        finally:
            sa._PROB_SCRIPT = original
            for cache in caches:
                cache.cache_clear()
        self.assertFalse(sa._closure_facts()["stale"],
                         "the board must be readable again after the test")

    # ---- the cheap prefilter must stay a superset of the rule ---------------

    def test_the_trigger_admits_what_the_rule_now_grades(self):
        # `_VALUE_TRIGGER` runs FIRST and a surface it skips is never masked
        # and never graded. A widened rule behind an un-widened trigger is
        # inert on exactly the files it was widened for.
        bare_only = ("On the closure challenge leaderboard the duct sits 3rd "
                     "of 5.\n")
        self.assertIsNotNone(sa._VALUE_BOARD_SIZE.search(bare_only),
                             "the rule must reach this sentence")
        self.assertIsNotNone(sa._VALUE_TRIGGER.search(bare_only),
                             "and so must the gate in front of it")
        self.assertIsNone(sa._VALUE_TRIGGER.search(
            "Major iteration 31 of 47 on the board\n"),
            "and the gate must not have been widened past the rule")


class TheAuditMustNotSHIPAMutantTests(unittest.TestCase):
    """Both mutants that were live in HEAD for 65 minutes on 2026-08-15.

    `fb30e00f` captured `scripts/self_audit.py` mid-mutation from a concurrent
    census that writes the real file in place and restores its snapshot in a
    `finally`. Two mutants rode into the commit: `if not lines:` became
    `if False:` in `check_rank_claim_surfaces`, disabling the skip guard so
    every decoded surface counted as claiming; and the fall-through `UNKNOWN`
    became `PASS`, which is defect class B1 -- the empty set reported as
    agreement -- re-introduced into the shipped audit. Restored at `0a3e82d7`.

    **NOTHING CAUGHT EITHER ONE, and the reason is the whole point.** No test
    failed, because no test ran against the committed text: the census restored
    the working tree in its `finally`, so `git status` read CLEAN while `HEAD`
    was wrong, and every subsequent agent diffed against a working tree that
    already agreed with them. The only witness is the committed source itself.

    Two assertions over that source, and they are deliberately not clever. A
    property test would be better and would not have existed today.
    """

    SOURCE = (REPO / "scripts" / "self_audit.py").read_text(encoding="utf-8")

    def test_no_branch_in_the_shipped_audit_is_disabled(self):
        # A permanently-false branch in an audit is either dead code or a
        # captured mutant. Neither belongs in the file, and telling them apart
        # after the fact costs more than forbidding both.
        for disabled in ("if False:", "if 0:", "if None:"):
            with self.subTest(disabled=disabled):
                self.assertNotIn(
                    disabled, self.SOURCE,
                    f"{disabled} is in the shipped audit: either dead code or "
                    f"a mutation captured by a commit, as happened at "
                    f"fb30e00f and was restored at 0a3e82d7")

    def test_the_compliant_fall_through_is_PASS_and_not_UNKNOWN(self):
        """The SECOND mutant, and the first draft of this test asserted it.

        This class was written believing the chief's diagnosis that
        `fb30e00f` mutated `UNKNOWN -> PASS`. Executed, the history says the
        opposite: `847b4492`, `fb30e00f` AND `9b9951a1` all carry **PASS** on
        the compliant fall-through, the census spec records `PASS` as the
        ORIGINAL and `UNKNOWN` as its mutant, and
        `test_rank_claim_surfaces.py::test_a_compliant_unlisted_surface_passes`
        has been asserting `PASS` all along. The `UNKNOWN` arrived at
        `0a3e82d7` -- the restore itself captured a live mutant, from the same
        harness and the same window as the defect it was repairing.

        **So the first version of this test enshrined the mutant as the
        invariant**, and it was green while doing it. It is written the other
        way round now, and it is the direction that has evidence: three
        commits, the harness's own spec, and a sibling test.

        Why it matters beyond tidiness: `lab_check`'s EXIT_CONTRACT treats
        UNKNOWN as BLOCKING, so the mutant turns the everything-complies path
        into a hard stop -- a fail-CLOSED regression on the one branch that is
        supposed to mean "nothing is wrong".
        """
        start = self.SOURCE.index("def check_rank_claim_surfaces(")
        end = self.SOURCE.index("\ndef ", start + 1)
        body = self.SOURCE[start:end]
        tail = body[body.rindex(
            'return Result("rank claims carry their probability",'):]
        self.assertIn("PASS", tail.split("\n")[0],
                      "the compliant fall-through must be PASS; UNKNOWN there "
                      "is census mutant RC10, and it BLOCKS lab_check")
        self.assertNotIn("UNKNOWN", tail.split("\n")[0])

    def test_the_empty_set_is_still_UNKNOWN_in_both_rank_checks(self):
        # The executable half of the same pair. Kept beside the source
        # assertions because a source check alone would pass on a rewrite that
        # spells the defect differently.
        for check in (sa.check_rank_claim_surfaces, sa.check_rank_claim_values):
            with self.subTest(check=check.__name__):
                tracked, archives = sa._tracked_files, sa._shipping_archives
                sa._tracked_files, sa._shipping_archives = (lambda: []), (lambda: [])
                try:
                    self.assertEqual(check().status, sa.UNKNOWN)
                finally:
                    sa._tracked_files, sa._shipping_archives = tracked, archives


if __name__ == "__main__":
    unittest.main()
