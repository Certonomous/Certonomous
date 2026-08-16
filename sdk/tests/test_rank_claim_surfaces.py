"""The rank-claim guard must cover every surface that makes a rank claim.

WHY. Ladder V rung V8, as amended 2026-08-10, binds EVERY surface: any rank
claim, internal or external, carries P(rank 1), the current 95% interval on it,
and the pairs that are `not statistically decided`. A bare probability is a
worse claim than none, because a bare probability sounds settled and eight
cases do not support settled.

NO FIGURE IS TYPED INTO THIS FILE ANY MORE, and that is the point of the
2026-08-12 rung below. The fixtures used to read `P(rank 1) = 68%` and
`2-100% at 95%`, which were the figures against a FOUR-entry board. The board
went to six entries on 2026-08-11, the figures became 50% and 0-97%, and this
suite stayed green through the change -- a compliant fixture that carries dead
numbers proves only that the guard agrees with the fixture. The fixtures are
built from `sdk/scripts/probability_of_rank_record.json` now, so they move when
the board moves, and the assertions that decide anything are the NEGATIVE ones:
the superseded interval must now be REJECTED.

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

import ast
import importlib.util
import json
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

# The figures the fixtures below must carry, read from the SAME committed
# record the guard reads -- not typed here, and not asked of the guard. If the
# board moves and the record is regenerated, these move with it; if the record
# is regenerated and the guard does not follow, the tests below go red, which
# is the direction that matters.
_RECORD = json.loads(
    (REPO / "sdk" / "scripts" / "probability_of_rank_record.json"
     ).read_text(encoding="utf-8"))
_P1 = round(100 * _RECORD["p_rank1"])
_LO = round(100 * _RECORD["double95"][0])
_HI = round(100 * _RECORD["double95"][1])

COMPLIANT = f"""On the published board our 0.0566 is rank 1 of 7, scored locally at deb91557.
P(rank 1) = {_P1}%, and eight cases cannot pin that tighter than {_LO}-{_HI}% at 95%.
The leads over Yang and over Reissmann are not statistically decided.
"""

# The SAME sentence with the figures of the superseded four-entry board. This
# is the fixture that used to be called COMPLIANT, kept verbatim: until
# 2026-08-12 the suite asserted that this text was clean, which is how a guard
# demanding a dead interval stayed green through a board move.
SUPERSEDED = """On the published board our 0.0566 is rank 1 of 5, scored locally at deb91557.
P(rank 1) = 68%, and eight cases cannot pin that tighter than 2-100% at 95%.
The leads over Reissmann and over Wu and Zhang are not statistically decided.
"""

# Everything inside <s>...</s> on a published page: text STRUCK and KEPT under
# L-76. A guard may never be satisfied by a tombstone.
_STRUCK = re.compile(r"<s>.*?</s>", re.S)

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
        self.assertTrue(any(f"{_LO}-{_HI}% at 95%" in m for m in missing),
                        f"the CURRENT interval was not required: {missing}")

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

    def test_the_superseded_figures_are_no_longer_compliant(self):
        """The fixture this suite used to call COMPLIANT must now fault.

        `SUPERSEDED` is the four-entry board's sentence, unchanged. It carries
        P(rank 1) and the not-decided token, so the ONLY thing that can fault
        it is the interval -- and until 2026-08-12 nothing did, because the
        guard was still asking for exactly the interval this text carries.
        """
        self.assertTrue(sa._rank_claim_lines(SUPERSEDED))
        missing = sa._rank_companions_missing(SUPERSEDED)
        self.assertEqual(1, len(missing), missing)
        self.assertIn("95%", missing[0])
        self.assertNotIn("2-100%", missing[0])

    def test_the_live_page_carries_what_the_rule_requires(self):
        """closure.html in the tree, not a fixture. This is the regression."""
        page = (REPO / "demo-output" / "website" / "closure.html"
                ).read_text(encoding="utf-8")
        self.assertTrue(sa._rank_claim_lines(page))
        self.assertEqual([], sa._rank_companions_missing(page))

    def test_the_live_page_complies_without_its_struck_text(self):
        """The live sentence must be the thing that satisfies the rule.

        THE DEFECT THIS PINS, and it is the reason this rung exists. Until
        2026-08-12 the test above passed for an accidental reason.
        At 41e813df `closure.html` stated its interval as `0-97% at 95%`,
        which the guard could not recognise at all -- the guard wanted
        `2-100%`. What satisfied it was two lines of text the page had already
        STRUCK and kept under L-76:

            <s>P(rank 1) = 68%, 2-100% at 95%</s> - struck 2026-08-11 ...

        The tombstone of the superseded figure was the only thing on the page
        matching the guard, so the page was certified compliant on the strength
        of a claim it had publicly withdrawn. Delete every <s>...</s> and the
        page must STILL carry what the rule asks; if it does not, the guard is
        reading the dead text again.
        """
        page = (REPO / "demo-output" / "website" / "closure.html"
                ).read_text(encoding="utf-8")
        live = _STRUCK.sub("", page)
        self.assertNotEqual(page, live, "the page carries no struck text at "
                                        "all; this control is not exercising "
                                        "anything")
        self.assertTrue(sa._rank_claim_lines(live))
        self.assertEqual([], sa._rank_companions_missing(live),
                         "the page satisfies V8 only through struck text")


class TheClosureFiguresAreDerivedNotTypedTests(unittest.TestCase):
    """The rung of 2026-08-12.

    Two facts used to be literals inside `scripts/self_audit.py`: the
    best-on-board count ("round 5 records four of eight") and the interval on
    P(rank 1) ("2-100% at 95%"). On 2026-08-11 the public board went from four
    entries to six. The count became 2 of 8, the interval became 0-97%, and the
    guard reported nothing -- it cannot, because a guard holding a copy of the
    fact it guards has no way to learn the fact moved. Worse than silent: the
    guard went on FAILING surfaces that did not say "four of eight" and
    CERTIFYING a credentials wall that did.

    So the tests here are not "does the guard know the number". They are "does
    the number follow its source". The derivation is driven with synthetic
    boards, because a derivation that can only ever run against the one true
    board on disk is indistinguishable from a constant.
    """

    CASES = ["c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8"]

    def _entry(self, ours, floor=None):
        per = {c: v for c, v in zip(self.CASES, ours)}
        return {"official_test_harness_result": {
            "round5_per_case_full": per,
            "round5_per_case": {c: round(v, 4) for c, v in per.items()},
            "rans_identity_floor_per_case": floor or {}}}

    def _board(self, rows):
        return {"fetched": "T", "entrants": rows}

    def _record(self, entries, overall):
        return {"frame": {"entries": entries, "fetched": "T",
                          "our_overall": overall},
                "p_rank1": 0.5, "double95": [0.0025, 0.969]}

    def test_the_count_follows_the_board_and_is_not_a_constant(self):
        """The same entry against two boards must give two counts."""
        ours = [0.05] * 8
        entry = self._entry(ours)
        beaten = self._board({"rival": [0.09] * 8})
        winning = self._board({"rival": [0.01] * 8})
        low = sa._derive_closure_facts(
            beaten, self.CASES, entry, self._record(1, 0.05))
        high = sa._derive_closure_facts(
            winning, self.CASES, entry, self._record(1, 0.05))
        self.assertEqual(8, len(low["best"]), low)
        self.assertEqual(0, len(high["best"]), high)

    def test_one_added_entrant_moves_the_count(self):
        """The 2026-08-11 event in miniature: the board gains a leader and the
        count falls without our own numbers changing by a digit."""
        ours = [0.05] * 8
        entry = self._entry(ours)
        four = self._board({"rival": [0.09] * 8})
        six = self._board({"rival": [0.09] * 8,
                           "newcomer": [0.01, 0.01, 0.09, 0.09,
                                        0.01, 0.01, 0.01, 0.01]})
        before = sa._derive_closure_facts(
            four, self.CASES, entry, self._record(1, 0.05))
        after = sa._derive_closure_facts(
            six, self.CASES, entry, self._record(2, 0.05))
        self.assertEqual(8, len(before["best"]))
        self.assertEqual(2, len(after["best"]), after["best"])

    def test_a_declined_row_is_not_credited_to_our_model(self):
        """A case whose score EQUALS its RANS-identity floor is the organisers'
        own field passed through by the gate. It counts as best-on-board and it
        does not count as ours, and `earned` is the difference."""
        ours = [0.05] * 8
        floor = {c: round(0.05, 4) for c in self.CASES[:2]}
        facts = sa._derive_closure_facts(
            self._board({"rival": [0.09] * 8}), self.CASES,
            self._entry(ours, floor), self._record(1, 0.05))
        self.assertEqual(8, len(facts["best"]))
        self.assertEqual(2, len(facts["declined"]))
        self.assertEqual(6, len(facts["earned"]))

    def test_when_every_best_row_was_declined_our_model_earns_none(self):
        """Which is the lab's actual position on the six-entry board."""
        ours = [0.01, 0.01] + [0.09] * 6
        floor = {c: round(0.01, 4) for c in self.CASES[:2]}
        facts = sa._derive_closure_facts(
            self._board({"rival": [0.05] * 8}), self.CASES,
            self._entry(ours, floor), self._record(1, sum(ours) / 8))
        self.assertEqual(2, len(facts["best"]))
        self.assertEqual([], facts["earned"], facts)

    def test_the_live_derivation_reproduces_the_board_on_disk(self):
        """Not an identity: the expected values come from the benchmark's live
        board and our scoring record, and the assertion is that our model's own
        best-on-board count is ZERO -- the disclosure the whole rule is for."""
        facts = sa._closure_facts()
        self.assertEqual([], facts["stale"], facts["stale"])
        self.assertEqual(6, facts["entries"])
        self.assertEqual("Yang", facts["leader"])
        self.assertEqual(["alpha_05_4071_4048", "alpha_05_4071_2024"],
                         facts["best"])
        self.assertEqual(facts["best"], facts["declined"],
                         "both best-on-board rows are the organisers' own "
                         "unmodified RANS field")
        self.assertEqual([], facts["earned"])

    # -- the provenance check on the one number that cannot be recomputed ----

    def test_a_record_from_a_different_board_is_reported_stale(self):
        facts = sa._derive_closure_facts(
            self._board({"a": [0.09] * 8, "b": [0.09] * 8}), self.CASES,
            self._entry([0.05] * 8), self._record(4, 0.05))
        self.assertTrue(facts["stale"], facts)
        self.assertTrue(any("4-entry board" in s for s in facts["stale"]),
                        facts["stale"])
        self.assertIsNone(facts["interval"],
                          "a stale record must not hand out an interval")

    def test_a_record_from_a_different_entry_is_reported_stale(self):
        facts = sa._derive_closure_facts(
            self._board({"a": [0.09] * 8}), self.CASES,
            self._entry([0.05] * 8), self._record(1, 0.061))
        self.assertTrue(any("now scores" in s for s in facts["stale"]),
                        facts["stale"])

    def test_a_missing_record_is_reported_not_swallowed(self):
        facts = sa._derive_closure_facts(
            self._board({"a": [0.09] * 8}), self.CASES,
            self._entry([0.05] * 8), None)
        self.assertTrue(facts["stale"], facts)
        self.assertIsNone(facts["interval"])

    def test_the_committed_record_matches_the_board_on_disk(self):
        """The control that will redden the DAY the board moves again -- which
        is the job the hard-coded interval could not do."""
        self.assertEqual([], sa._closure_facts()["stale"])

    # -- the interval the guard demands --------------------------------------

    def test_the_superseded_interval_is_rejected(self):
        self.assertFalse(sa._states_the_interval("pinned no tighter than "
                                                 "2-100% at 95%"))

    def test_the_current_interval_is_accepted_however_it_is_spelled(self):
        for text in (f"{_LO}-{_HI}% at 95%", f"{_LO}–{_HI}% at 95%",
                     f"{_LO} - {_HI} %"):
            self.assertTrue(sa._states_the_interval(text), text)

    def test_a_neighbouring_interval_is_rejected(self):
        """So "accepts anything with a dash and a percent" cannot pass."""
        self.assertFalse(sa._states_the_interval(f"{_LO}-{_HI + 3}% at 95%"))

    def test_the_guard_names_the_current_interval_when_it_faults(self):
        self.assertEqual(f"{_LO}-{_HI}% at 95%", sa._rank_interval_phrase())


class TheBestOnBoardDisclosureTests(unittest.TestCase):
    """`check_closure_entry_of_record` had NO test of any kind before
    2026-08-12, which is how it came to assert a superseded count as ground
    truth and hold it for a day after the board moved."""

    FACTS = {"stale": [], "entries": 6, "cases": ["c%d" % i for i in range(8)],
             "best": ["a", "b"], "declined": ["a", "b"], "earned": [],
             "interval": (0, 97), "p_rank1": 50, "our_overall": 0.0566,
             "leader": "Yang"}

    def setUp(self):
        self._real = sa._closure_facts
        sa._closure_facts = lambda: self.FACTS
        self.addCleanup(lambda: setattr(sa, "_closure_facts", self._real))

    def test_the_derived_count_with_both_disclosures_is_clean(self):
        text = ("Best result on the public board on two of the eight test "
                "cases - but both are the organisers' own unmodified RANS "
                "field, so the count belonging to our own model is zero of "
                "eight.")
        self.assertEqual([], sa._best_on_board_faults(text))

    def test_a_stale_count_is_faulted_and_the_new_one_is_named(self):
        """The live credentials wall's actual defect on 2026-08-12."""
        text = ("Best result on the public board on four of the eight test "
                "cases - but two of those four are the organisers' own "
                "unmodified RANS field, so the count belonging to our own "
                "model is zero of eight.")
        faults = sa._best_on_board_faults(text)
        self.assertEqual(1, len(faults), faults)
        self.assertIn("is 2 of eight", faults[0])

    def test_the_count_may_not_travel_without_the_baseline_disclosure(self):
        """Asserted on THIS fault, not on any fault mentioning the gate.

        As first written this test looked for `decline gate` anywhere in the
        fault list, and a mutation that deleted the baseline-disclosure rule
        outright left it green -- the zero-earned fault names the gate too, so
        the test was reading its neighbour's output and calling it a pass.
        That is the same species of accident as the struck-text pass above,
        found the same way, and it is what mutation-proving is for.
        """
        text = "Best result on the public board on two of the eight cases."
        faults = sa._best_on_board_faults(text)
        self.assertTrue(
            any(f.startswith("our_entry states a best-on-board count without "
                             "the disclosure") for f in faults), faults)

    def test_a_zero_earned_count_must_say_zero(self):
        text = ("Best result on the public board on two of the eight cases, "
                "and the credit there belongs to the baseline.")
        faults = sa._best_on_board_faults(text)
        self.assertTrue(any("zero of eight" in f for f in faults), faults)

    def test_a_text_making_no_best_on_board_claim_is_not_faulted(self):
        """So the fix cannot be 'fault everything'."""
        self.assertEqual([], sa._best_on_board_faults(
            "Our entry scores 0.0566 overall and won four of eight cases "
            "against Yang."))

    def test_nothing_is_judged_while_the_instrument_is_stale(self):
        sa._closure_facts = lambda: dict(self.FACTS, stale=["board moved"])
        self.assertEqual([], sa._best_on_board_faults(
            "Best on the board on four of the eight cases."))

    def test_the_declared_blind_spot_names_the_CALLER_and_not_the_pattern(self):
        """D129/D236. The frame of this rule is its caller, not its regex.

        `_best_on_board_faults` is reached from exactly one place, and that
        place hands it ONE whitespace-collapsed string out of `wall.json`. It
        opens no SURFACE. Until 2026-08-16 the declared blind spot instead
        named `_BEST_COUNT`'s inability to cross a line break -- a real limit,
        and the flattering one to confess, because repairing it changes nothing
        about how many surfaces this check reads.

        THE FIRST VERSION OF THIS TEST PROVED NOTHING, and it is worth saying
        why in the file it was written in. It asserted "opens no file" by
        spying on `sa.Path.read_bytes` from inside a class whose `setUp`
        replaces `_closure_facts` with a lambda. Two independent reasons it
        could not fail: the rule's file reads go through `Path.read_text`
        (`_load_json` and `_module_literal` both read TEXT), and the only
        function that makes them was stubbed out. Measured on 2026-08-16 with
        the real `_closure_facts` and a cold cache, the rule opens FOUR files.
        They are the BOARD it grades against, never a surface that could carry
        a claim, and that is the sentence the blind-spot line has to earn.
        """
        line = sa._blind_best_on_board()
        self.assertIn("THE FRAME IS THE CALLER, NOT THE PATTERN", line)
        self.assertIn("It opens no SURFACE of its own", line)
        self.assertIn("check_rank_claim_", line,
                      "the line must send the reader to the check that does "
                      "sweep the corpus, or the limit reads as a dead end")
        # And the claim must be TRUE, not recited. Drive the rule with its REAL
        # board reader on a cold cache, spying on every API it could open a
        # file through, and assert that everything it touches is a board
        # record. A surface appearing in this list is the day the frame moved.
        opened = []
        real_facts = self._real
        sa._closure_facts = real_facts
        if hasattr(real_facts, "cache_clear"):
            real_facts.cache_clear()
        real_bytes, real_text, real_open = (sa.Path.read_bytes,
                                            sa.Path.read_text, sa.Path.open)

        def spy(fn):
            def wrapped(self_path, *a, **k):
                opened.append(str(self_path))
                return fn(self_path, *a, **k)
            return wrapped

        sa.Path.read_bytes = spy(real_bytes)
        sa.Path.read_text = spy(real_text)
        sa.Path.open = spy(real_open)
        try:
            sa._best_on_board_faults(
                "Best result on the public board on four of the eight cases.")
        finally:
            (sa.Path.read_bytes, sa.Path.read_text,
             sa.Path.open) = real_bytes, real_text, real_open
            sa._closure_facts = lambda: self.FACTS
        board = {str(sa._PROB_SCRIPT), str(sa._PROB_RECORD),
                 str(sa._ENTRY_OF_RECORD)}
        # THE SPY MUST FIRE, or this test is the vacuous one it replaced: an
        # empty list here means the probe is watching an API nothing calls.
        self.assertTrue(opened,
                        "the file-open probe recorded nothing at all, so it "
                        "is not watching the API the rule reads through")
        self.assertEqual(
            [], sorted(set(opened) - board),
            f"the rule opened something that is not a board record, so the "
            f"declared frame is wrong; it opened {sorted(set(opened))}")


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
        """WHICH CHANGE MOVED THIS, and why UNKNOWN is the right verdict.

        This asserted WARN and the word "OFF" in the summary until 847b4492,
        which converted the branch to `_no_evidence` and made it UNKNOWN. The
        expectation was stale, not the change, and the reason is written at the
        call site: WARN is not a blocking status. `scripts/lab_check.py` records
        at its own line 229 that self_audit "exits non-zero only on FAIL -- so
        an OFF detector reddens nothing here" (docket D78). A guard that could
        not enumerate its own corpus examined nothing, and under this file's B1
        rule a check that examined nothing returns UNKNOWN, which exits 3 and
        which lab_check's EXIT_CONTRACT reads as UNKNOWN and treats as
        blocking. So the detector being off now reddens the runner instead of
        sitting beside the passes.

        THE TEST'S INTENT SURVIVES AND IS ASSERTED HARDER. The point was never
        the string "OFF"; it was that the report must say the detector did not
        look, rather than that there was nothing to find. That is asserted
        below on the real text -- the source it could not read is NAMED, and
        the B1 sentence is present -- rather than on one word. The assertion is
        NOT relaxed to accept either status: UNKNOWN is required and WARN now
        fails.
        """
        sa._tracked_files = lambda: None
        sa._travelling_names = lambda: set()
        result = sa.check_rank_claim_surfaces()
        self.assertEqual(sa.UNKNOWN, result.status, result.summary)
        self.assertIn("no surface was opened", result.summary)
        self.assertIn("not read: git ls-files", result.detail)
        self.assertTrue(
            any("an empty sweep is not agreement" in d for d in result.detail),
            result.detail)


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

# AND THE CONVENTION HAS TO BE RE-APPLIED TO EVERY NEW FIXTURE, which is a
# sentence worth its own measurement rather than its own adjective. The
# fourth-grade round added boundary and linear-algebra fixtures written out in
# full. Executed, on the tracked corpus:
#
#   at HEAD before the round : WARN, 2 lab-record faults (both in
#                              docs/INSTRUMENT_INTEGRITY_LEDGER.md)
#   with the fixtures literal: WARN, 10 -- the eight new ones ALL in this file
#
# The guard's own test file had become a corpus of eight real wrong placements
# about a real entrant, and the guard reported them, correctly, against the
# lab. Assembled below; the count is back to 2 and the sentences under test are
# unchanged.
_R4 = "rank " + "4"             # Wu is rank 2, so any of these is a defect
_R4C = "Rank " + "4"
_R4H = "rank-" + "4"
_R3C = "Rank " + "3"
_O4C = "Four" + "th"

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

    def test_a_boundary_binds_nothing_even_when_the_name_starts_the_sentence(
            self):
        """Found by EXECUTING the comment that claims a boundary blocks the
        bind, rather than reading it. A sentence ends at ". " plus a capital,
        and when the entrant's own surname IS that capital the slice between
        the ordinal and the name stops one character short of the evidence --
        so "They are at rank 4. Wu and Zhang run SST-QCRC." bound across the
        full stop. My own sweep's find, on my own claim.

        AND IT IS SYMMETRIC. The first repair patched the right-hand side
        only; on the left the capital closing the boundary is the ORDINAL's
        own first letter, and "Wu and Zhang did the duct case. Rank 4 is
        Montoya's." bound across the stop for the identical reason. Executed
        against the patched-right/unpatched-left build: the three L cases
        below all returned one rule-A fault each.
        """
        # name first after the stop (right-hand side)
        self.assertEqual(([], []), _faults(
            f"They are at {_R4}. Wu and Zhang run SST-QCRC."))
        self.assertEqual(([], []), _faults(
            f"The duct scores land at {_R4}! Reissmann and colleagues differ."))
        # ORDINAL first after the stop (left-hand side, the symmetric twin)
        self.assertEqual(([], []), _faults(
            f"Wu and Zhang did the duct case. {_R4C} is Montoya's."))
        self.assertEqual(([], []), _faults(
            f"We read Reissmann in full. {_R3C} belongs to someone else."))
        self.assertEqual(([], []), _faults(
            f"Wu and Zhang wrote it. {_O4C} place went to another team."))
        # POSITIVE CONTROLS: the guard has not simply stopped binding after
        # every full stop, and still binds in both directions.
        for live in (f"Wu and Zhang are the {_R4H} entry on the board.",
                     f"{_R4C} is where the board puts Wu and Zhang.",
                     f"The board's {_R4} slot is Wu and Zhang's."):
            rule_a, _ = _faults(live)
            self.assertEqual(1, len(rule_a), (live, rule_a))

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


class ASkipIsNotAnAgreementTests(unittest.TestCase):
    """A defect in the guard's OWN logic must not return PASS.

    A per-surface `except Exception` kept one bad document from ending the
    audit -- right -- and then reported the skip in the frame while leaving the
    STATUS green. Injecting a raise on exactly the surface carrying a fault
    returned "all 0 placement expression(s) agree with the published board".
    That is the green that means "I looked at nothing", which this check
    refuses in its own words. The surfaces a guard cannot read are the unusual
    ones, so their absence has to move the status, not only a number.
    """

    def setUp(self):
        self._real = sa._placements

    def tearDown(self):
        sa._placements = self._real

    def test_a_raise_on_every_surface_is_not_a_pass(self):
        sa._placements = lambda *a, **k: (_ for _ in ()).throw(
            RuntimeError("injected: the pattern blew up"))
        result = sa.check_board_placement_words()
        self.assertNotEqual(sa.PASS, result.status, result.summary)
        self.assertIn("not swept", result.summary)

    def test_a_raise_on_only_the_faulty_surface_is_not_a_pass(self):
        """The realistic shape: a partial break drops precisely the documents
        that break it."""
        real = self._real

        def selective(text, names, board):
            if "INSTRUMENT_INTEGRITY" in text:
                raise ValueError("injected: catastrophic backtracking")
            return real(text, names, board)

        sa._placements = selective
        result = sa.check_board_placement_words()
        self.assertNotEqual(sa.PASS, result.status, result.summary)
        named = [d for d in result.detail if "could not be swept" in d]
        self.assertTrue(named, "the skipped surface was not named")
        self.assertIn("NOT counted as agreeing", named[0])

    def test_an_empty_sweep_is_not_agreement_either(self):
        sa._placements = lambda *a, **k: []
        result = sa.check_board_placement_words()
        self.assertNotEqual(sa.PASS, result.status, result.summary)
        self.assertIn("empty sweep", result.summary)

    def test_the_healthy_run_still_reaches_a_verdict(self):
        """So the fix is not 'never pass again'."""
        self.assertIn(sa.check_board_placement_words().status,
                      (sa.PASS, sa.WARN, sa.FAIL))


class LinearAlgebraRankIsNotAPlacementTests(unittest.TestCase):
    """The exclusion was narrowed on a FALSE premise.

    Its comment said "every linear-algebra `rank` in this corpus is a word",
    and restricted the left-context exclusion to word numerals on that basis.
    A fourth grade swept the corpus and found four written as DIGITS. None
    faulted, by luck of layout alone -- none sat within the binding window of a
    board surname -- in a turbulence lab whose four entrants are turbulence
    authors. The discriminator is not the numeral form; it is whether a
    linear-algebra object is being discussed.
    """

    def test_digit_form_linear_algebra_is_excluded(self):
        for sentence in (
                "Wu and Zhang show the tensor basis is rank 3, not five.",
                "On the duct field Wu and Zhang report pointwise rank 3.",
                "Wu and Zhang compute a stress that is rank 3 almost "
                "everywhere.",
                "Wu and Zhang note the Reynolds stress is a rank-2 tensor."):
            self.assertEqual(([], []), _faults(sentence), sentence)

    def test_word_form_linear_algebra_is_still_excluded(self):
        self.assertEqual(([], []), _faults(
            "Wu and Zhang show the tensor basis is rank three, not five."))

    def test_a_placement_in_the_same_grammar_still_faults(self):
        """`are rank N` is the form the adjudication clause depends on, and it
        must survive an exclusion that now reaches digits."""
        rule_a, _ = _faults(f"Wu and Zhang are {_R4} on the published board.")
        self.assertEqual(1, len(rule_a), rule_a)

    def test_a_turbulence_noun_in_the_clause_does_not_mute_a_placement(self):
        """THE ADVERSARIAL CASE, and it was not hypothetical.

        The first repair of the false-premise defect replaced the numeral-form
        discriminator with a plain 80-character window on BOTH sides. Executed
        against that build, every sentence below returned zero faults -- three
        wrong placements about a real entrant, muted by a turbulence noun
        sitting elsewhere in the same clause, in a lab whose four entrants are
        turbulence authors. Trading a latent false positive for a live false
        negative is the worse trade: the false positive is loud.

        Nearest-wins, left-hand only, is what these pin.
        """
        for sentence in (
                f"Wu and Zhang are {_R4} on the published board, and their "
                f"tensor basis method is neural.",
                f"Their tensor-basis neural network is well known; Wu and "
                f"Zhang are {_R4} on the board.",
                f"The tensor basis paper is theirs. Wu and Zhang are {_R4}.",
                f"Wu and Zhang are {_R4} overall in the tensor-basis "
                f"category.",
                f"Wu and Zhang are {_R4}; the invariant set is Pope's."):
            rule_a, _ = _faults(sentence)
            self.assertEqual(1, len(rule_a), (sentence, rule_a))

    def test_the_adjudication_sentence_is_still_a_bound_placement(self):
        board, reason = sa._published_board()
        if board is None:
            self.skipTest(f"detector OFF, not a silent pass: {reason}")
        found = sa._placements("The published board puts Wu and Zhang at "
                               "rank 2.", sa._board_names(board), board)
        self.assertEqual([(2, "Wu")], [(n, who) for n, who, *_ in found])

    def test_the_real_corpus_instances_stay_clean(self):
        board, reason = sa._published_board()
        if board is None:
            self.skipTest(f"detector OFF, not a silent pass: {reason}")
        for rel in ("demo-output/website/campaign/"
                    "W2_POPE_1975_INTEGRITY_BASIS.md",
                    "sdk/scripts/pope_1975_basis_check.py"):
            path = REPO / rel
            if not path.exists():
                continue
            self.assertEqual(([], []), sa.board_placement_faults(
                path.read_text(encoding="utf-8", errors="replace"), board), rel)


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

    def test_a_who_column_matcher_that_is_not_anchored_makes_decoys_cheap(self):
        """`Filename`, `Hostname` and `Casename` all satisfied "a column
        naming who the entrants are", so `| Rank | Filename |` over two rows
        parsed as a board of two CSVs. Inside the stated concession, but a
        cheaper decoy is a likelier one."""
        for column in ("Filename", "Hostname", "Casename", "Codename"):
            board, reason = self._write(
                f"| Rank | {column} |\n|---|---|\n"
                "|      1 | alpha.csv |\n|      2 | beta.csv |\n")
            self.assertIsNone(board, f"{column} qualified as an author column")
            self.assertIn("names who the entrants are", reason)

    def test_a_real_who_column_still_qualifies(self):
        """So the anchoring is not just 'reject everything'."""
        for column in ("Authors", "Author", "Team", "Submitter", "Name",
                       "Entrants"):
            board, reason = self._write(
                f"| Rank | {column} | Overall |\n|---|---|---|\n"
                + self._rows("Reissmann, Fang", "Wu and Zhang"))
            self.assertEqual({"reissmann": 1, "wu": 2}, board, f"{column}: {reason}")

    def test_the_operating_margin_is_reported_and_is_one_edit_wide(self):
        """A live property a third grade measured: the real README has two
        table blocks and one qualifies. One more rank-headed two-row table in
        that third-party file and this detector goes OFF."""
        if self._env is None:
            sa.os.environ.pop(sa._BOARD_DIR_ENV, None)
        else:
            sa.os.environ[sa._BOARD_DIR_ENV] = self._env
        board, reason = sa._published_board()
        if board is None:
            self.skipTest(f"detector OFF, not a silent pass: {reason}")
        blocks, qualifying = sa._board_margin()
        self.assertGreaterEqual(blocks, qualifying)
        self.assertEqual(1, qualifying)
        frame = [d for d in sa.check_board_placement_words().detail
                 if d.startswith("frame:")][0]
        self.assertIn(f"{blocks} table block(s) and {qualifying} qualif", frame)
        self.assertIn("one edit from WRONG", frame)

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

    # --- the third grade's exception: `NEVER raises`, and it raised.
    # --- `read_text(encoding="utf-8")` sat inside `except OSError`, and
    # --- UnicodeDecodeError is a ValueError. One stray byte in a third-party
    # --- file of INTERNATIONAL AUTHOR NAMES took down the whole audit. It is
    # --- the same crash class already fixed once here through re.error, in the
    # --- same function, arriving by a different exception type -- so the fix
    # --- is a boundary, not another `except` clause.

    def test_a_non_utf8_byte_in_the_board_does_not_end_the_audit(self):
        good = (self.HEADER
                + self._rows("Reissmann, Fang", "Wu and Zhang")).encode()
        (Path(self._dir.name) / "README.md").write_bytes(
            good.replace(b"Fang", b"F\xe4ng"))
        board, reason = sa._published_board()
        self.assertIsNone(board)
        self.assertIn("UnicodeDecodeError", reason)
        result = sa.check_board_placement_words()          # must not raise
        self.assertEqual(sa.WARN, result.status)
        self.assertIn("OFF", result.summary)

    def test_nothing_the_third_party_file_can_contain_escapes(self):
        """A boundary, not a list of exception types. The first repair here
        escaped one metacharacter; the second would have caught one decode
        error; either invites a third. Anything the read or the parse raises
        becomes an OFF that names it."""
        for label, payload in (
                ("utf-16", "# x\n| Rank | Authors |\n".encode("utf-16")),
                ("random bytes", bytes(range(256)) * 4),
                ("lone surrogate", b"\xed\xa0\x80"),
                ("truncated multibyte", "Reißmann".encode()[:-1])):
            (Path(self._dir.name) / "README.md").write_bytes(payload)
            board, reason = sa._published_board()
            self.assertIsNone(board, label)
            self.assertTrue(reason, label)
            self.assertNotEqual(sa.FAIL,
                                sa.check_board_placement_words().status, label)

    def test_the_boundary_is_a_wrapper_and_not_a_wider_except(self):
        """The scope is deliberate and the docstring says so: only the
        read-and-parse of the file we do not control is wrapped. A check that
        caught everything everywhere would hide its own defects, which is the
        failure one layer up from the one being fixed."""
        self.assertTrue(hasattr(sa, "_parse_published_board"))
        doc = sa._published_board.__doc__
        self.assertIn("CANNOT RAISE", doc)
        self.assertIn("KeyboardInterrupt", doc)
        # "NEVER raises" may appear ONLY as the retracted claim, never as the
        # standing one -- the same treatment a struck figure gets: the number
        # goes, the record of having claimed it stays.
        for occurrence in re.finditer("NEVER raises", doc):
            context = doc[max(0, occurrence.start() - 40):occurrence.end() + 20]
            self.assertIn("An earlier version said", context)

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


class TheStructuralBoundaryIsNotAPunctuationMarkTests(unittest.TestCase):
    """Grade round 6's regression, and the controls that keep the fix honest.

    The subject-NP fallback was added in round 6 so that an ordinal predicated
    by a copula still binds when its subject sits beyond `_PLACE_BIND`. Its
    comment said it "cannot reach across a sentence: the phrase is cut at
    `_PLACE_CLAUSE` first". `_PLACE_CLAUSE` was `[.!?;:]`, whitespace is
    collapsed before any of it runs, and A HEADING, A LIST ITEM AND A TABLE
    ROW END WITHOUT PUNCTUATION -- in a corpus written in markdown. So what it
    could not cross was a punctuation mark, and the inference from that to
    "a sentence" is the whole defect. Three shapes crossed one, at gaps of 65,
    69 and 54 characters against a `_PLACE_BIND` of 40, so the ordinary bind
    was not what fired.

    THE FIX IS NOT DELETING THE FALLBACK, and the last two tests here are why:
    it exists for two round-5 false negatives that must keep faulting. The
    boundary is preserved instead -- `_place_flatten` writes a markdown
    structural break as one newline where the plain collapse wrote a space,
    and `_PLACE_CLAUSE` cuts on it.

    Assembled at run time, as everything in this file is.
    """

    _RK = "ra" + "nk"
    _D2 = "2"

    def _p(self, template):
        return template.format(RK=self._RK, D2=self._D2)

    def test_a_heading_is_a_boundary_though_it_carries_no_punctuation(self):
        self.assertEqual(([], []), _faults(self._p(
            "## Liu wins the duct case study\n\nThe entrant we must beat "
            "overall is {RK} {D2} today.")))

    def test_a_list_item_is_a_boundary(self):
        self.assertEqual(([], []), _faults(self._p(
            "- Liu ran the duct case on a coarse mesh\n- The entrant to beat "
            "here is {RK} {D2}\n")))

    def test_a_table_cell_is_a_boundary(self):
        self.assertEqual(([], []), _faults(self._p(
            "| Liu | duct case, coarse mesh | the entrant to beat is "
            "{RK} {D2} |")))

    def test_the_punctuated_twins_were_always_silent_and_stay_silent(self):
        """The author's stated boundary DOES hold where the punctuation is, and
        the finding was never that it does not."""
        for text in (
            "Liu wins the duct case study.\n\nThe entrant we must beat "
            "overall is {RK} {D2} today.",
            "Liu ran the duct case on the coarse mesh; the front-runner is "
            "{RK} {D2}.",
        ):
            self.assertEqual(([], []), _faults(self._p(text)), text)

    def test_the_two_false_negatives_the_fallback_exists_for_still_fault(self):
        """Or this would be a demand to delete the fallback, which would put
        round 5's E2 false negatives straight back."""
        for text in (
            "Montoya, who rebuilt the anisotropy tensor from the strain "
            "invariant, is {RK} {D2} overall.",
            "Liu and Montoya, whose Reynolds stress tensor closure won the "
            "duct case, are {RK} {D2} on the board.",
        ):
            rule_a, _ = _faults(self._p(text))
            self.assertEqual(1, len(rule_a), f"{text} -> {rule_a}")

    def test_a_reflow_still_joins_which_is_what_the_collapse_is_for(self):
        """`_place_flatten` must distinguish a STRUCTURAL break from a line
        wrapped mid-paragraph. If it stopped joining reflows it would undo the
        property `WholeTextNotLinesTests` pins and lose the live instance in
        the report source."""
        wrapped = f"The {_WRONG} entry (Wu &\nZhang) runs SST-QCRC."
        flat = sa._place_flatten(wrapped)
        self.assertNotIn("\n", flat, flat)
        self.assertEqual(len(wrapped), len(flat))
        self.assertEqual(1, len(_faults(wrapped)[0]))

    def test_the_marked_collapse_moves_no_offset(self):
        """One run, one character, either way -- so the adjudication window,
        the context slices and the excerpt in the fault message are unmoved,
        and the only consumer that can tell is `_PLACE_CLAUSE`."""
        for text in (DEFECT_A_WAS, DEFECT_B_WAS, DEFECT_C_WAS,
                     "# H\n\n- a\n- b\n\n| x | y |\n\nplain wrapped\nprose\n"):
            marked = sa._place_flatten(text)
            plain = re.sub(r"\s+", " ", text)
            self.assertEqual(len(plain), len(marked), text)
            self.assertEqual(plain, marked.replace("\n", " "), text)


class TheAbbreviationPeriodIsNotASentenceEndTests(unittest.TestCase):
    """Round 6's second regression: the boundary constant is unconditionally
    uppercase.

    Round 5's boundary defect was that `_PLACE_SENTENCE` closes a boundary only
    on an uppercase character and neither appended character reliably is one.
    The repair appended a CONSTANT standing for "a new token starts here",
    under a comment saying "the character's identity was never doing any work".
    It was doing exactly one job: separating an abbreviation-final period from
    a sentence-final one. With the constant always `A`, every `et al. ` became
    a sentence boundary and two real wrong placements went silent.

    The direction is the cheap one -- a missed fault, not a false one -- but it
    is a regression this rung introduced, and the ruling does not forgive it.
    """

    _RK = "ra" + "nk"
    _D4 = "4"
    _S4 = "4" + "th"
    _P = "pl" + "ace"

    def _p(self, template):
        return template.format(RK=self._RK, D4=self._D4, S4=self._S4,
                               P=self._P)

    def test_a_wrong_placement_after_an_abbreviation_faults_again(self):
        for text in ("Wu et al. {RK} {D4} overall on the duct case.",
                     "Wu et al. {S4} {P} overall on the duct."):
            rule_a, _ = _faults(self._p(text))
            self.assertEqual(1, len(rule_a), f"{text} -> {rule_a}")

    def test_the_round_five_boundary_shapes_are_not_reopened(self):
        """The whole point of the constant was that six shapes bound across a
        full stop. An abbreviation exception that let them back would trade a
        missed fault for six false ones, which is the wrong direction."""
        for text in (
            f"Liu ran the duct case. {self._S4} {self._P} is still open.",
            f"Liu ran the duct case. {self._RK} {self._D4} is still open.",
            f"They are at {self._RK} {self._D4}. liu et al. ran SST-QCRC.",
            f"Montoya closed the hump case. {_O4C} {self._P} is still open.",
        ):
            self.assertEqual(([], []), _faults(text), text)

    def test_a_bare_initial_is_still_read_as_a_sentence_end(self):
        """Named because it is a DECISION, not an oversight. Adding
        `\\b[A-Z]\\.` would catch the citation form `Wu, J. rank 4 ...` and
        would also read a genuine sentence end after any one-letter word as an
        abbreviation -- a false FAULT bought with a missed fault. The missed
        fault is kept, and counted."""
        self.assertEqual(
            ([], []), _faults(f"Reported by Wu, J. {self._RK} {self._D4} "
                              f"overall on the duct case."))
        self.assertIsNone(sa._PLACE_ABBREV.search("Wu, J."))

    def test_the_predicate_is_asked_directly_not_read_off_a_character(self):
        """`_place_sentence_break` must answer on the abbreviation, not on the
        case of the next character -- or the round-5 defect returns by the
        other door."""
        self.assertTrue(sa._place_sentence_break(" did the duct case. A"))
        self.assertFalse(sa._place_sentence_break(" et al. A"))
        self.assertFalse(sa._place_sentence_break(" et al. a"))


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

    def test_the_verdict_admits_it_cannot_tell_its_board_is_stale(self):
        """D48's settlement, and the reason it is GENERATED and not typed.

        Eleven blind-spot items described how this guard reads a SENTENCE.
        None described its REFERENT. Item 9 names the symmetric hazard one
        level down -- whether a placement is dated history -- so the shape of
        the omission was already in the list: the guard could say "this
        sentence may be about an old board" and could not say "my own board
        may be an old board". The clone is pinned at a commit from months back
        and the live board has since grown by two entrants and changed leader
        (`campaign/BOARD_MOVED_2026-08-11.md`), so the disclosure is not
        hypothetical.

        THE PIN VALUES MUST COME FROM THE PIN. A typed commit or a typed date
        in an item whose entire subject is staleness would be the defect
        performing itself, so this asserts the item carries what
        `_published_board` and `_board_pin_date` actually return -- change the
        clone and the item follows it or this reddens.
        """
        board, reason = sa._published_board()
        if board is None:
            self.skipTest(f"detector OFF, not a silent pass: {reason}")
        _b, head = sa._published_board()
        frame = [d for d in sa.check_board_placement_words().detail
                 if d.startswith("frame:")][0]
        self.assertIn("(12) WHETHER ITS OWN BOARD IS STILL CURRENT", frame)
        self.assertIn(f"The {len(board)} entrants above were read from a clone "
                      f"frozen at {head[:8]}", frame,
                      "item 12's pin is not the pin the check actually used")
        pinned_on = sa._board_pin_date()
        if pinned_on:
            self.assertIn(f"dated {pinned_on}", frame,
                          "item 12 states a date the clone does not have")
        # Both directions of the error, which is the whole content of the
        # disclosure: naming only the false FAULT would understate it.
        self.assertIn("the error runs BOTH ways", frame)
        self.assertIn("stays SILENT", frame)
        # And it must not read as an instruction to move the pin, which is the
        # one response `BOARD_MOVED` §4 rules out.
        self.assertIn("NOT a defect to repair here", frame)

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

    def _held_out(self, name):
        path = (REPO / "demo-output" / "website" / "campaign" / name)
        self.assertTrue(path.exists(),
                        f"{name} is the evidence behind a published figure; "
                        f"without it this test asserts nothing")
        spec = importlib.util.spec_from_file_location(name[:-3], path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        return mod

    def test_every_published_reach_figure_recomputes_from_its_sentences(self):
        """The third grade's exception 2, and the end of the class.

        The figures were made GENERATED so they could not drift between
        surfaces, and then went stale in the commit that installed them: rule B
        was widened in the same commit, four of the grader's rule-B sentences
        moved from missed to caught, and nothing re-measured. The table
        contradicted its own rule-B row about those same five sentences.
        Generation stopped one level short of the measurement.

        So the measurement is recomputed here from sentences that live in the
        repository. A number recorded without its inputs can always go stale;
        one recomputed from them cannot.
        """
        board, reason = sa._published_board()
        if board is None:
            self.skipTest(f"detector OFF, not a silent pass: {reason}")
        grader = self._held_out("V16_GRADE_HELDOUT_SETS.py")
        author = self._held_out("V16_AUTHOR_HELDOUT_SET.py")
        measured = {}
        measured.update(grader.measure(board, sa.board_placement_faults))
        measured.update(author.measure(board, sa.board_placement_faults))
        published = {name: (now, n)
                     for name, _who, _blind, n, _was, now in sa._PLACE_REACH}
        for key, table_key in (("FIRST", "the grader's first set"),
                               ("AUTHOR", "the author's set"),
                               ("ADVERSARIAL",
                                "the grader's adversarial set")):
            self.assertEqual(
                measured[key], published[table_key],
                f"_PLACE_REACH says {published[table_key]} for "
                f"{table_key!r}; the committed sentences measure "
                f"{measured[key]}. The published figure is stale.")
        # RULE B'S ROW TOO. It was the one published figure with no committed
        # sentences and no recompute, sitting in the same generated paragraph
        # as the three above under a comment saying it could not happen again.
        caught, n = measured["RULE_B_CAUGHT"]
        self.assertEqual(
            (caught, n), tuple(sa._PLACE_REACH_B[:2]),
            f"_PLACE_REACH_B says {sa._PLACE_REACH_B[:2]}; the committed "
            f"rule-B sentences measure {(caught, n)}. Stale.")

    def test_the_adversarial_controls_are_still_caught(self):
        """So the adversarial set cannot be rigged to miss: it carries three
        positive controls that a working guard must catch."""
        board, reason = sa._published_board()
        if board is None:
            self.skipTest(f"detector OFF, not a silent pass: {reason}")
        grader = self._held_out("V16_GRADE_HELDOUT_SETS.py")
        missed, n = grader.measure(
            board, sa.board_placement_faults)["ADVERSARIAL_CONTROLS"]
        self.assertEqual(0, missed, f"{missed} of {n} controls missed")

    def test_the_round_five_probes_all_agree_with_the_live_guard(self):
        """E2 and E4 of grade round 5, wired in so they cannot regress quietly.

        The probes were committed executable and then run only by hand. That
        makes them a record of a past state rather than a guard on the current
        one -- their own module docstring says `main` recomputes them against
        the live guard, and until this test existed nothing did. Twelve of the
        twenty disagreed with the guard when they were filed: six shapes that
        bound an ordinal across a full stop, four sentences whose subject is a
        tensor and were faulted anyway, and two wrong placements that were
        muted. All twenty agree now.
        """
        board, reason = sa._published_board()
        if board is None:
            self.skipTest(f"detector OFF, not a silent pass: {reason}")
        probes = self._held_out("V16_GRADE_ROUND5_PROBES.py")
        measured = probes.measure(board, sa.board_placement_faults)
        wrong = {lab: f"want {want}, got {got}"
                 for lab, (want, got) in measured.items() if want != got}
        self.assertEqual({}, wrong,
                         f"{len(wrong)} of {len(measured)} round-5 probes "
                         f"disagree with what the guard ought to do")

    def test_the_round_five_probes_carry_their_own_positive_controls(self):
        """Or the test above would also pass against a guard wedged shut.

        Most of the twenty assert SILENCE, and a guard that never fires is
        silent on everything. These five assert the opposite direction, so the
        set cannot be satisfied by switching the detector off.
        """
        board, reason = sa._published_board()
        if board is None:
            self.skipTest(f"detector OFF, not a silent pass: {reason}")
        probes = self._held_out("V16_GRADE_ROUND5_PROBES.py")
        measured = probes.measure(board, sa.board_placement_faults)
        must_fault = sorted(lab for lab, (want, _) in measured.items()
                            if want == "FAULT")
        self.assertEqual(5, len(must_fault), must_fault)
        for lab in must_fault:
            self.assertEqual("FAULT", measured[lab][1], lab)

    def _outside_precision(self, board):
        """The grader's set, reduced to what the round-7 figure is over.

        Only ADMITTED sentences -- ones in which the guard actually FINDS a
        placement expression, `len(_placements(...)) > 0` -- are scored.
        Returns (labels admitted, labels falsely faulted).

        THIS DOCSTRING SAID "which is the author's own admission rule applied
        unchanged" AND THAT WAS THE DEFECT (D49). The author's set was scored
        over every sentence a rule-A pattern merely MATCHED, which is strictly
        looser: it skips the homonym list, the probability form, the of-N form
        and the linear-algebra subject-head discriminator. Both sets now use
        the predicate named above, and `_author_precision` below is this method
        made symmetric so the pairing cannot silently come apart again.
        """
        grader = self._held_out("V16_GRADE_ROUND7_PRECISION_SET.py")
        seen = grader.admission(board, sa._placements, sa._board_names)
        admitted = {lab for lab, n in seen.items() if n}
        measured = grader.measure(board, sa.board_placement_faults)
        bad = set(measured["FALSE_FAULT_LABELS"])
        self.assertTrue(bad <= admitted,
                        "a false FAULT on a sentence the guard was measured "
                        "not to look at; the admission rule is not being "
                        "applied consistently")
        return admitted, bad

    def _author_precision(self, board):
        """The author's set under THE SAME predicate as `_outside_precision`.

        The whole of D49 is that this method did not exist: the author's row
        was scored by `measure` over all 41 sentences while the grader's was
        scored over the 25 the guard examines, and the 27-point spread the
        verdict published was mostly that difference. Returns
        (labels admitted, dict of measured results over the admitted subset).

        The `bad <= admitted` assertion is the one that would have caught it,
        and it is made on BOTH sides now rather than only on the outside one.
        """
        author = self._held_out("V16_PRECISION_SET.py")
        admitted = author.admitted_labels(board, sa._placements,
                                          sa._board_names)
        got = author.measure(board, sa.board_placement_faults, admitted)
        bad = {lab.split(": ", 1)[1] for lab in got["FALSE_FAULT_LABELS"]}
        self.assertTrue(bad <= admitted,
                        "a false FAULT on a sentence the guard was measured "
                        "not to look at; the admission rule is not being "
                        "applied consistently")
        return admitted, got

    def test_both_precision_rows_are_admitted_by_one_predicate(self):
        """D49, executed: the defect was a PAIRING, so this is its test.

        Each row recomputing correctly from its own sentences -- which both
        always did -- cannot see this. Two rows can each be internally right
        and still be incomparable, and the verdict compares them. So the
        property under test is not "each row is correct" but "both rows were
        admitted by the same rule", and the rule is named here rather than
        inherited from whichever module was read first.

        A future editor who scores either row over its full set, or over a raw
        pattern match, reddens this.
        """
        board, reason = sa._published_board()
        if board is None:
            self.skipTest(f"detector OFF, not a silent pass: {reason}")
        rows = {name: (total, n) for name, _w, _b, total, n, _bad
                in sa._PLACE_PRECISION}

        a_admitted, a_got = self._author_precision(board)
        self.assertEqual(
            rows["the author's non-placement set"], (a_got["TOTAL"],
                                                     len(a_admitted)),
            "the author's row's denominators disagree with its sentences")

        g_admitted, _bad = self._outside_precision(board)
        grader = self._held_out("V16_GRADE_ROUND7_PRECISION_SET.py")
        g_total = grader.measure(board, sa.board_placement_faults)["TOTAL"]
        self.assertEqual(
            rows["the grader's non-placement set"], (g_total, len(g_admitted)),
            "the grader's row's denominators disagree with its sentences")

        # The predicate itself, asserted rather than assumed: every admitted
        # label on both sides is one the guard finds a placement in, and no
        # unadmitted label is. Without this the two sets could agree on a
        # count while disagreeing on which sentences produced it.
        pat = sa._board_names(board)
        author = self._held_out("V16_PRECISION_SET.py")
        for cls, lab, sentence in author.NON_PLACEMENTS:
            found = bool(sa._placements(sentence, pat, board))
            self.assertEqual(found, lab in a_admitted, f"{cls}: {lab}")
        for lab, _cls, text in grader.sentences(board):
            found = bool(sa._placements(text, pat, board))
            self.assertEqual(found, lab in g_admitted, lab)

    def test_the_precision_spread_is_measured_under_both_rules(self):
        """`_PLACE_ADMISSION` recomputes, so the sensitivity cannot go stale.

        The verdict no longer claims the two samples differ in their builder
        and in nothing else. It reports the range the ADMISSION RULE is worth,
        and a range that is written down rather than measured is the same L-79
        hazard that put stale reach figures in this file. So both rules are
        executed here against the committed sentences.

        IT ALSO EXECUTES THE CLAIM THE STRIKE RESTS ON. "Worst case on hard
        sentences" stays struck because the grader's rate exceeds the author's
        under EVERY rule, not because of any one p-value -- so that is asserted
        for every row of `_PLACE_ADMISSION` rather than argued in a comment.
        """
        board, reason = sa._published_board()
        if board is None:
            self.skipTest(f"detector OFF, not a silent pass: {reason}")
        author = self._held_out("V16_PRECISION_SET.py")
        grader = self._held_out("V16_GRADE_ROUND7_PRECISION_SET.py")
        pat = sa._board_names(board)

        strict = author.admitted_labels(board, sa._placements, sa._board_names)
        upto = 4 + sa._PLACE_OVER
        loose = {lab for _cls, lab, s in author.NON_PLACEMENTS
                 if sa._place_pattern(upto).search(sa._place_flatten(s))}
        self.assertTrue(strict < loose,
                        "`_placements` is meant to be STRICTLY narrower than a "
                        "raw match; if it is not, the two rules are the same "
                        "rule and this table is describing a difference that "
                        "does not exist")

        g_bad = set(grader.measure(
            board, sa.board_placement_faults)["FALSE_FAULT_LABELS"])
        g_strict = {lab for lab, _c, t in grader.sentences(board)
                    if sa._placements(t, pat, board)}
        g_loose = {lab for lab, _c, t in grader.sentences(board)
                   if sa._place_pattern(upto).search(sa._place_flatten(t))}

        measured = []
        for admitted, g_admitted in ((strict, g_strict), (loose, g_loose)):
            a = author.measure(board, sa.board_placement_faults, admitted)
            ak, an = a["PRECISION"]
            gk, gn = len(g_bad & g_admitted), len(g_admitted)
            measured.append((an, ak, gn, gk))
            self.assertGreater(
                round(100 * gk / gn), round(100 * ak / an),
                "the grader's rate does not exceed the author's under this "
                "admission rule -- the struck 'worst case' hedge rests on it "
                "doing so under EVERY rule, and that is now false")
        self.assertEqual(
            measured, [tuple(r[1:]) for r in sa._PLACE_ADMISSION],
            "`_PLACE_ADMISSION` disagrees with the committed sentences; the "
            "sensitivity published in the verdict is stale")

        # The numerator must NOT move with the rule. If it did, the 13
        # sentences the strict rule drops would not all be true negatives and
        # the choice of predicate would be a choice about the FIGURE rather
        # than about the denominator.
        self.assertEqual(measured[0][1], measured[1][1],
                         "the false-FAULT count moved with the admission "
                         "rule; the dropped sentences are not all true "
                         "negatives")

    def test_both_published_precision_figures_recompute_from_their_sentences(
            self):
        """THE ROUND'S CENTRE, and the closing condition the ruling set.

        Four published figures, all of them recall. Nothing measured how often
        the guard faults a sentence that is not a placement at all, and that
        asymmetry is why six rounds of false FAULTs arrived as surprises: the
        instrument could not report its own worst failure mode. This recomputes
        the figures from committed sentences, exactly like the reach rows, so
        they cannot go stale the way those did (L-79).

        TWO ROWS, NOT ONE. The first was measured by the party being measured
        and is the optimistic one by 27 points; the second was built blind by
        an independent grader. Both recompute here, so neither can be quietly
        dropped or edited into agreement with the other.
        """
        board, reason = sa._published_board()
        if board is None:
            self.skipTest(f"detector OFF, not a silent pass: {reason}")
        rows = {name: (bad, n) for name, _w, _b, _t, n, bad
                in sa._PLACE_PRECISION}
        self.assertEqual(
            2, len(sa._PLACE_PRECISION),
            "a precision row was added or removed; a single row is a "
            "self-report, and this test is the reason there are two")

        _admitted, got = self._author_precision(board)
        measured = got["PRECISION"]
        published = rows["the author's non-placement set"]
        self.assertEqual(
            published, measured,
            f"_PLACE_PRECISION says {published} for the author's set; the "
            f"committed sentences measure {measured}. The figure is stale.")

        admitted, bad = self._outside_precision(board)
        published = rows["the grader's non-placement set"]
        self.assertEqual(
            published, (len(bad), len(admitted)),
            f"_PLACE_PRECISION says {published} for the grader's set; the "
            f"committed sentences measure {(len(bad), len(admitted))}. The "
            f"figure is stale.")

    def test_the_precision_set_cannot_be_padded_or_wedged(self):
        """Two ways to fake a precision figure, both closed.

        A set of sentences that must all be SILENT is satisfied perfectly by a
        guard that has been switched off, and a set can be made to look clean
        by filling it with sentences no pattern matches. So every sentence must
        match a rule-A pattern, and five positive controls must all fault.
        """
        board, reason = sa._published_board()
        if board is None:
            self.skipTest(f"detector OFF, not a silent pass: {reason}")
        precision = self._held_out("V16_PRECISION_SET.py")
        self.assertEqual([], precision.matches_a_pattern(sa),
                         "a precision set may not contain sentences the guard "
                         "never examines")
        missed, total = precision.measure(
            board, sa.board_placement_faults)["CONTROLS_MISSED"]
        self.assertEqual(0, missed, f"{missed} of {total} controls missed")

    def test_every_false_fault_class_is_counted_and_named(self):
        """The ruling permits a shape to be KNOWINGLY ACCEPTED rather than
        fixed, PROVIDED it is counted in the precision figure and named in the
        blind-spot list. This is that proviso, executed: the enumeration and
        the measurement are the same numbers or the suite reddens.

        AND IT BINDS AGAINST A SET THIS SUITE'S AUTHOR DID NOT BUILD, which is
        the whole difference between this version and the one grade round 7
        filed as D28. That version was tight -- dict equality both ways plus a
        sum -- and computed BOTH sides over the author's own set, so a test
        named "every false-FAULT class is counted and named" could only ever
        see classes the author had already thought of. The L-74 circularity was
        not fixed by measuring the figure; it moved up one level, onto the test
        guarding the figure. A proviso that can only confirm what its author
        already listed is not a proviso.

        The second source is the grader's blind set. Every false FAULT it
        produces must be assigned to an enumerated class, and the per-class
        totals must equal what the guard publishes. A sentence built outside
        this lab, faulting in a shape nobody here enumerated, reddens this --
        which is exactly how `other-named-board` and `negated-or-questioned`
        came to be in the table.
        """
        board, reason = sa._published_board()
        if board is None:
            self.skipTest(f"detector OFF, not a silent pass: {reason}")
        for cls, _what, a, g in sa._PLACE_FALSE_FAULT:
            self.assertTrue(a or g, f"{cls} is enumerated but counted in no "
                                    f"sample; an unmeasured class in this "
                                    f"table is a description, not a cost")
        named = {cls for cls, _what, _a, _g in sa._PLACE_FALSE_FAULT}
        declared_author = {cls: a for cls, _w, a, _g in sa._PLACE_FALSE_FAULT
                           if a}
        declared_outside = {cls: g for cls, _w, _a, g in sa._PLACE_FALSE_FAULT
                            if g}

        _admitted, got = self._author_precision(board)
        by_class = got["BY_CLASS"]
        self.assertEqual(by_class, declared_author,
                         "a false-FAULT shape is counted in the author's "
                         "figure and missing from the enumeration, or the "
                         "reverse")

        admitted, bad = self._outside_precision(board)
        unnamed = sorted(lab for lab in bad
                         if lab not in sa._PLACE_FF_OUTSIDE)
        self.assertEqual(
            [], unnamed,
            f"the grader's set falsely faults on {unnamed}, which "
            f"`_PLACE_FF_OUTSIDE` assigns to no enumerated class. A shape "
            f"found by someone who could not see these patterns is counted in "
            f"no figure and named in no list -- which is the one thing the "
            f"KNOWINGLY ACCEPTED ruling does not permit.")
        gone = sorted(lab for lab in sa._PLACE_FF_OUTSIDE if lab not in bad)
        self.assertEqual(
            [], gone,
            f"`_PLACE_FF_OUTSIDE` classifies {gone}, which the grader's set no "
            f"longer falsely faults. The enumeration is carrying a cost the "
            f"guard has stopped paying -- correct the counts rather than the "
            f"record of what was once wrong.")
        measured_outside = {}
        for lab in bad:
            cls = sa._PLACE_FF_OUTSIDE[lab]
            self.assertIn(cls, named, f"{lab} is assigned to {cls!r}, which "
                                      f"is not a class in the enumeration")
            measured_outside[cls] = measured_outside.get(cls, 0) + 1
        self.assertEqual(measured_outside, declared_outside,
                         "a false-FAULT shape is counted in the grader's "
                         "figure and missing from the enumeration, or the "
                         "reverse")

        rows = {name: (bad_, n) for name, _w, _b, _t, n, bad_
                in sa._PLACE_PRECISION}
        self.assertEqual(sum(declared_author.values()),
                         rows["the author's non-placement set"][0])
        self.assertEqual(sum(declared_outside.values()),
                         rows["the grader's non-placement set"][0])
        self.assertEqual(len(bad), len(sa._PLACE_FF_OUTSIDE))

    def test_the_verdict_publishes_precision_beside_the_recall_figures(self):
        """A guard whose precision is unmeasured reads as more trustworthy than
        it is. The figures have to reach the reader, not only the constants.

        BOTH ROWS, EACH WITH ITS PROVENANCE. One row published alone is the
        measured party's self-report, and the reader has no way to see that the
        number depends on who built the sample. So every row's builder and
        blindness must appear, exactly as `_PLACE_REACH`'s rows do, and the
        reader must be told the rows disagree.

        AND BOTH DENOMINATORS, WHICH IS ROUND 10's ADDITION. A row saying
        "19 of 25" over a set of 43 sentences tells a reader the rate and hides
        the selection; the set's size and its admitted count are different
        numbers and both are published now. The sensitivity of the spread to
        that selection is asserted here too, because it is the replacement for
        an absolute this paragraph used to assert (D49).
        """
        _, _, blind, _ = sa.BASIS["check_board_placement_words"]
        frame = [d for d in sa.check_board_placement_words().detail
                 if d.startswith("frame:")][0]
        for surface in (blind, frame):
            for name, who, was_blind, total, n, bad in sa._PLACE_PRECISION:
                self.assertIn(f"falsely faults {bad} of {n}", surface)
                self.assertIn(f"out of the {total} the set holds", surface)
                self.assertIn(name, surface)
                self.assertIn(who, surface)
                self.assertIn("built BLIND" if was_blind
                              else "built WITH the pattern list", surface)
            self.assertIn("THEY DISAGREE BY", surface)
            self.assertIn("NEITHER IS A BOUND", surface)
            self.assertIn("THE BUILDER IS NOT THE ONLY VARIABLE", surface)
            self.assertIn("CONFOUNDED", surface)
            self.assertIn("ONE RULE, BOTH SAMPLES", surface)
            spreads = sorted(
                abs(round(100 * gb / gn) - round(100 * ab / an))
                for _r, an, ab, gn, gb in sa._PLACE_ADMISSION)
            self.assertIn(f"{spreads[0]}-to-{spreads[-1]} point range", surface)
            self.assertIn("ADVERSARIAL AND NOT REPRESENTATIVE", surface)
            self.assertIn("KNOWINGLY ACCEPTED", surface)
            for cls, _what, _a, _g in sa._PLACE_FALSE_FAULT:
                self.assertIn(cls, surface)

    #: The five absolutes this rung added and execution falsified. The fourth
    #: is the precision hedge: it was written to stop a reader overstating the
    #: number and it understated it instead, and no sweep of the
    #: author's own added lines could have found it -- falsifying it took
    #: building a second instrument.
    #:
    #: THE FIFTH IS THE FIRST ONE THAT SAT IN THE READER-FACING VERDICT rather
    #: than in a comment (D49). The generated precision paragraph asserted that
    #: its two samples "differ in that variable and in nothing else" and that
    #: "the same admission rule applies to both". Two different predicates
    #: implemented that one rule, and the pairing published was the only one of
    #: four that was not internally consistent, the one that maximised the gap,
    #: and the one whose Fisher p a chief ruling quoted. It took no new
    #: instrument to falsify -- only running the two admission rules against
    #: each other's sets, which nothing had done in three rounds because each
    #: row recomputed correctly from its own sentences and a per-row check
    #: cannot see a defect that lives in a PAIRING.
    _FALSIFIED = ("none of which is a false FAULT",
                  "cannot reach across a sentence",
                  "identity was never doing any work",
                  "a WORST CASE on hard sentences",
                  "in that variable and in nothing else",
                  "the same admission rule applies to")

    def test_the_falsified_absolutes_survive_only_as_quoted_history(self):
        """L-76 in the guard's own text, and the FIRST version of this test was
        itself wrong in an instructive way.

        It asserted the three strings were absent. But L-76 does not want a
        falsified claim DELETED -- deleting it loses the record of what was
        believed and why it was wrong, which is the whole value. It wants the
        claim to stop being ASSERTED. So the property is: each string may
        appear, and every appearance must sit beside its own falsification.
        A future editor who reinstates one as a claim, with no marker near it,
        turns this red; one who quotes it as history does not.

        The test also fails if a string VANISHES, because a repair that erases
        the mistake it repaired is the failure mode this whole rung documents.
        """
        source = (REPO / "scripts" / "self_audit.py").read_text(
            encoding="utf-8")
        flat = re.sub(r"\s+", " ", re.sub(r"(?m)^\s*#", "", source))
        markers = ("falsified", "round 6 executed", "ONCE READ",
                   "denied in an absolute", "The sentence that stood here",
                   "This comment read", "was an inference")
        for claim in self._FALSIFIED:
            at = [m.start() for m in re.finditer(re.escape(claim), flat)]
            self.assertTrue(at, f"{claim!r} was deleted rather than corrected; "
                                f"L-76 wants the falsified claim RECORDED")
            for start in at:
                window = flat[max(0, start - 340):start + 340]
                self.assertTrue(
                    any(k in window for k in markers),
                    f"{claim!r} appears with no falsification beside it -- it "
                    f"is being asserted again, not quoted:\n...{window}...")

    def test_the_round_six_probes_agree_or_are_declared_and_counted(self):
        """Round 6's twenty-four, wired in like round 5's twenty.

        Seventeen must agree outright: the twelve controls, the three
        structural-boundary shapes and the two abbreviation shapes, which were
        the round's two regressions. The remaining seven are the E2 shapes the
        ruling permits to stand KNOWINGLY ACCEPTED -- and they are pinned to
        that exact list, so a NEW E2 disagreement reddens this test just as
        loudly as a regression would.
        """
        board, reason = sa._published_board()
        if board is None:
            self.skipTest(f"detector OFF, not a silent pass: {reason}")
        probes = self._held_out("V16_GRADE_ROUND6_PROBES.py")
        measured = probes.measure(board, sa.board_placement_faults)
        disagree = {lab for lab, (want, got) in measured.items() if want != got}
        accepted = {
            "E2 reduced relative, relativizer dropped",
            "E2 reduced relative, past participle",
            "E2 reduced relative, present tense",
            "E2 head noun off the word list (kernel)",
            "E2 head noun off the word list (Gramian)",
            "E2 head noun off the word list (Laplacian)",
            "E2 coordinated subject, both conjuncts objects",
        }
        self.assertEqual(accepted, disagree,
                         "the knowingly-accepted set has changed: either a "
                         "regression, or a shape fixed without updating the "
                         "precision figure and the blind-spot enumeration")
        must_fault = sorted(lab for lab, (want, _) in measured.items()
                            if want == "FAULT")
        self.assertEqual(7, len(must_fault), must_fault)
        for lab in must_fault:
            self.assertEqual("FAULT", measured[lab][1], lab)

    def test_the_evidence_files_are_not_themselves_corpora_of_faults(self):
        """They are tracked surfaces the live guard sweeps. Written out in
        full they would be exactly the defects they describe -- which is the
        convention this lab has now had to re-apply six times in one night, the
        sixth being `V16_PRECISION_SET.py` itself, whose `front-runner` was
        unsplit until the live guard was run over it before commit.

        THE SET IS DERIVED, NOT LISTED, which is this file's founding
        principle applied to itself: it enumerated five names by hand, so the
        NEXT evidence file added would have been unguarded until someone
        remembered to edit this tuple. That is the same shape as the defect in
        the docstring at the top -- the list was the defect.
        """
        board, reason = sa._published_board()
        if board is None:
            self.skipTest(f"detector OFF, not a silent pass: {reason}")
        campaign = REPO / "demo-output" / "website" / "campaign"
        evidence = sorted(campaign.glob("V16_*.py"))
        self.assertGreaterEqual(len(evidence), 5, "the evidence files behind "
                                "the published figures are gone; this test "
                                "asserts nothing without them")
        for path in evidence:
            self.assertEqual(
                ([], []),
                sa.board_placement_faults(path.read_text(encoding="utf-8"),
                                          board), path.name)

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

    def test_the_benchmarks_generator_cannot_regenerate_an_unnamed_placement(self):
        """The half of this defect class that no published surface shows.

        `benchmarks.json` and `wall/wall.json` are WRITTEN by
        `sdk/scripts/build_benchmarks.py` out of a module-level `_CLOSURE`
        dict, so a placement corrected in the JSON survives exactly until the
        next regeneration. That is not a hypothetical: the generator's own
        comment records the round-5 session hand-updating both JSON files and
        leaving the literal at round 3, caught by rung V7 on 2026-08-08.

        NEITHER EXISTING ASSERTION REACHES IT. The generator does not travel,
        so its own fault is a WARN that nothing asserts on; and the three
        surfaces pinned by the test above do not include it. So this suite
        could stand green over a literal that re-publishes an anonymous
        comparison onto two travelling pages the next time anyone runs the
        build -- which is the shape of green that means "I looked at the copy
        and not at the thing that writes the copy".

        Asserted on the SHIPPED STRINGS ONLY, `_CLOSURE` read out of the
        generator's AST, so the surrounding comments -- which legitimately
        quote a defect in order to name it -- cannot redden it.
        """
        board, reason = sa._published_board()
        if board is None:
            self.skipTest(f"detector OFF, not a silent pass: {reason}")
        gen = REPO / "sdk" / "scripts" / "build_benchmarks.py"
        self.assertTrue(gen.exists(),
                        "the benchmarks generator is gone; this test asserts "
                        "nothing about anything without it")
        closure = None
        for node in ast.parse(gen.read_text(encoding="utf-8")).body:
            if (isinstance(node, ast.Assign) and len(node.targets) == 1
                    and getattr(node.targets[0], "id", None) == "_CLOSURE"):
                closure = ast.literal_eval(node.value)
        self.assertIsNotNone(closure,
                             "_CLOSURE is not in the generator: this test's "
                             "subject has moved and it is asserting nothing")

        def strings(value):
            if isinstance(value, str):
                return [value]
            if isinstance(value, dict):
                return [s for v in value.values() for s in strings(v)]
            if isinstance(value, (list, tuple)):
                return [s for v in value for s in strings(v)]
            return []

        shipped = "\n".join(strings(closure))
        self.assertTrue(shipped.strip(),
                        "_CLOSURE carries no text; nothing was examined")
        self.assertEqual(([], []), sa.board_placement_faults(shipped, board),
                         "the generator would write this onto benchmarks.json "
                         "and wall/wall.json on its next run")


class TheGraderPrecisionSetIsIndependentTests(unittest.TestCase):
    """Grade round 7, R-ISOLATE part 2: the precision denominator is checked by
    a set the author did not build.

    The rung's author named its own weakest point -- "the precision denominator
    is mine, built with the pattern list in hand, and a set built by someone
    else will give a different number." That is L-74: a check built with the
    same knowledge as the thing it checks measures transcription fidelity, not
    the world. `campaign/V16_GRADE_ROUND7_PRECISION_SET.py` is the external
    referent, written before its author's set or the `_place*` patterns were
    read.

    These tests do NOT pin the grader's figure. Pinning it would redden the
    suite when the guard IMPROVES, which is backwards. They pin the two
    properties that make the figure worth comparing at all: that the two
    samples are genuinely different sentences, and that the grader's set can be
    neither padded nor satisfied by a switched-off detector.
    """

    def _held_out(self, name):
        path = (REPO / "demo-output" / "website" / "campaign" / name)
        self.assertTrue(path.exists(),
                        f"{name} is the evidence behind a published figure; "
                        f"without it this test asserts nothing")
        spec = importlib.util.spec_from_file_location(name[:-3], path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        return mod

    @staticmethod
    def _norm(text):
        return re.sub(r"\s+", " ",
                      re.sub(r"[^a-z0-9 ]", "", text.lower())).strip()

    def test_the_author_and_grader_samples_are_disjoint(self):
        """R-ISOLATE part 2: ASSERTED disjoint, never trusted.

        Two figures computed over overlapping sentences are one figure counted
        twice, and an overlap is the signature of template reuse (L-66).
        """
        board, reason = sa._published_board()
        if board is None:
            self.skipTest(f"detector OFF, not a silent pass: {reason}")
        grader = self._held_out("V16_GRADE_ROUND7_PRECISION_SET.py")
        author = self._held_out("V16_PRECISION_SET.py")
        mine = {self._norm(s) for _lab, _cls, s in grader.sentences(board)}
        theirs = {self._norm(item[-1]) for item in author.NON_PLACEMENTS}
        self.assertEqual(set(), mine & theirs,
                         "the grader's precision set reuses author sentences; "
                         "the two figures are not independent")
        self.assertGreaterEqual(len(mine), 40)
        self.assertGreaterEqual(len(theirs), 40)

    def test_the_grader_set_cannot_be_padded_or_wedged(self):
        """The same two ways to fake a precision figure the author's set closes,
        closed here on the grader's set -- and one more.

        Padding: a sentence the guard never examines cannot falsify anything,
        so sentences with no rank-like expression are EXCLUDED from the
        denominator rather than counted as clean. The exclusion is measured,
        not assumed, and the admitted count is what the round-7 figure is over.

        Wedged shut: positive controls -- plain wrong placements -- must fault.
        Wedged OPEN: correct placements must stay SILENT. A guard that faults
        everything scores perfect recall and zero precision, and positive
        controls alone cannot tell it from a working one.
        """
        board, reason = sa._published_board()
        if board is None:
            self.skipTest(f"detector OFF, not a silent pass: {reason}")
        grader = self._held_out("V16_GRADE_ROUND7_PRECISION_SET.py")
        seen = grader.admission(board, sa._placements, sa._board_names)
        admitted = [lab for lab, n in seen.items() if n]
        self.assertGreaterEqual(
            len(admitted), 20,
            "too few of the grader's sentences carry a rank-like expression "
            "for the figure over them to mean anything")
        measured = grader.measure(board, sa.board_placement_faults)
        self.assertEqual([], measured["CONTROLS_MISSED"],
                         "a wrong placement stopped faulting: the precision "
                         "figure could now be improved by switching the "
                         "detector off")
        self.assertEqual([], measured["SILENT_CONTROLS_FAULTED"],
                         "a CORRECT placement now faults: the guard is wedged "
                         "open, which positive controls alone cannot see")
        # Every false FAULT must be one the guard actually looked at.
        self.assertTrue(set(measured["FALSE_FAULT_LABELS"]) <= set(admitted))


class TheIntervalIsReadInEveryMarkupDialectTests(unittest.TestCase):
    """The rung of 2026-08-12: a FALSE FAULT, caused by the instrument.

    `closure_challenge_report.tex` carries the current interval nine times and
    the guard reported it MISSING -- not wrong, missing. LaTeX spells an
    en-dash `--` and must escape the percent sign, so the file says `0--97\\%`,
    and the reader wanted one hyphen and a bare `%`. It found no interval pair
    anywhere in that file. `closure_challenge_round5_qcr.json` was failed the
    same way for writing `0-97 percent at 95 percent`.

    That is the failure mode the guard's own comments call the worst one: it
    failed two surfaces for being CORRECT, and the cheapest way to make it
    green is to edit the surface that was right.

    THE FIX MUST NOT BE "ACCEPT MORE". A reader that accepts anything with two
    numbers near a percent sign passes every surface in the tree and measures
    nothing, which is strictly worse than the bug -- the bug at least still
    faulted the surfaces that were genuinely silent. So the dialects are
    enumerated in `_INTERVAL_DIALECTS`, and this class drives BOTH directions
    separately: every dialect in the table is accepted, and a text with no
    interval, a neighbouring interval, or the superseded interval still faults
    in every one of those same dialects.
    """

    # Written against `_LO`/`_HI`, which come from the committed record, so
    # these move with the board instead of pinning today's digits.
    def _dialects(self):
        return {
            "plain hyphen, bare percent":      f"{_LO}-{_HI}% at 95%",
            "plain hyphen, spaced":            f"{_LO} - {_HI} %",
            "LaTeX `--` and escaped percent":  rf"\textbf{{{_LO}--{_HI}\% at 95\%}}",
            "LaTeX `---` em-dash":             rf"{_LO}---{_HI}\%",
            "unicode en-dash":                 f"{_LO}\u2013{_HI}% at 95%",
            "unicode em-dash":                 f"{_LO}\u2014{_HI}%",
            "unicode minus sign":              f"{_LO}\u2212{_HI}%",
            "the unit spelled as a word":      f"{_LO}-{_HI} percent at 95 percent",
            "word unit and unicode en-dash":   f"{_LO}\u2013{_HI} per cent",
            "HTML entity &ndash;":             f"{_LO}&ndash;{_HI}%",
            "HTML numeric entity &#8211;":     f"{_LO}&#8211;{_HI}%",
            "HTML percent entity &#37;":       f"{_LO}-{_HI}&#37;",
            "a percent sign on BOTH ends":     f"{_LO}%-{_HI}% at 95%",
            "both ends, unicode en-dash":      f"{_LO}%\u2013{_HI}%",
        }

    def test_every_enumerated_dialect_is_read(self):
        """Direction 1. Subtests, so one broken dialect names itself rather
        than hiding behind whichever the loop reached first."""
        for name, text in self._dialects().items():
            with self.subTest(dialect=name):
                self.assertTrue(sa._states_the_interval(text), text)

    def test_a_surface_with_no_interval_still_faults(self):
        """Direction 2, and the one that matters. A fix that makes everything
        pass is worse than the bug it replaces."""
        for name, text in (
                ("no interval at all",
                 "P(rank 1) = 50%, rank 1 of 7 scored locally at deb91557."),
                ("empty", ""),
                ("the figure with no band", "P(rank 1) = 50%"),
                ("two numbers, no separator", f"{_LO} {_HI}%"),
                ("two numbers, no unit", f"{_LO}--{_HI} at 95")):
            with self.subTest(case=name):
                self.assertFalse(sa._states_the_interval(text), text)

    def test_a_wrong_interval_faults_in_every_dialect_too(self):
        """The widening cannot be a back door: reading LaTeX must not mean
        reading the SUPERSEDED figure as if it were the current one."""
        for name, text in (
                ("superseded, plain", "no tighter than 2-100% at 95%"),
                ("superseded, LaTeX", r"no tighter than 2--100\% at 95\%"),
                ("superseded, word unit", "no tighter than 2-100 percent"),
                ("superseded, en-dash", "no tighter than 2\u2013100% at 95%"),
                ("neighbouring high", f"{_LO}--{_HI + 3}\\%"),
                ("neighbouring low", f"{_LO + 2}\u2013{_HI}%"),
                ("both ends off by one", f"{_LO + 1}-{_HI + 1} percent")):
            with self.subTest(case=name):
                self.assertFalse(sa._states_the_interval(text), text)

    def test_the_word_to_is_deliberately_not_a_dialect(self):
        """`docket.json` contains "830,000 to 970,000 cells", whose digits read
        as `0 to 97`. No surface here spells a range with "to", so accepting it
        would buy nothing and put a coincidence one unit-word away from
        certifying a surface that states no interval at all."""
        self.assertFalse(sa._states_the_interval(f"{_LO} to {_HI}%"))

    def test_the_dialect_table_marks_what_the_corpus_does_not_exercise(self):
        """The HTML entity rows are handled and are NOT used anywhere in this
        tree. That is recorded in the table rather than implied, so nobody
        later reads their presence as evidence a surface relies on them."""
        unexercised = [name for name, _p, _c, seen in sa._INTERVAL_DIALECTS
                       if not seen]
        self.assertTrue(unexercised, "every dialect claims to be in use; if "
                                     "that became true the claim needs "
                                     "re-measuring, not deleting")
        for name in unexercised:
            self.assertIn("HTML", name)

    def test_the_latex_report_states_the_interval_on_its_live_text(self):
        """The regression, read off the tree.

        AND NOT ON A TOMBSTONE. The report strikes the superseded figure with
        `\\sout{2--100\\%}` and keeps it under L-76. `closure.html` was once
        certified by exactly such a tombstone, so the assertion here is made
        twice: on the file, and on the file with every `\\sout{...}` removed.
        The second is the one with teeth.
        """
        tex = (REPO / "demo-output" / "website" / "latex"
               / "closure_challenge_report.tex").read_text(encoding="utf-8")
        sout = re.compile(r"\\sout\{[^{}]*\}")
        self.assertTrue(sout.search(tex), "the report carries no struck text; "
                                          "this control exercises nothing")
        self.assertTrue(sa._states_the_interval(tex))
        self.assertTrue(sa._states_the_interval(sout.sub("", tex)),
                        "the report states the interval only inside \\sout")
        self.assertFalse(
            sa._states_the_interval(" ".join(sout.findall(tex))),
            "the struck text alone satisfies the rule, which is the "
            "closure.html tombstone defect in a second file")

    def test_the_entry_of_record_states_the_interval_on_its_live_block(self):
        """`closure_challenge_round5_qcr.json` spells the unit as a word. Its
        superseded four-entry companion is KEPT as a sibling key, so the live
        block is the one that must carry the figure."""
        path = (REPO / "demo-output" / "website"
                / "closure_challenge_round5_qcr.json")
        record = json.loads(path.read_text(encoding="utf-8"))

        def holder(node):
            if isinstance(node, dict):
                if "rank_companion_2026_08_10" in node:
                    return node
                for value in node.values():
                    found = holder(value)
                    if found is not None:
                        return found
            return None

        parent = holder(record)
        self.assertIsNotNone(parent, "the superseded companion is gone; this "
                                     "test's control has been deleted")
        superseded = parent.pop("rank_companion_2026_08_10")
        self.assertFalse(sa._states_the_interval(superseded),
                         "the SUPERSEDED companion states the CURRENT "
                         "interval, so it is not what it says it is")
        self.assertTrue(sa._states_the_interval(json.dumps(record)),
                        "the entry of record states the current interval only "
                        "in the block it has superseded")


class TheBestOnBoardCountIsFixedAtItsGeneratorTests(unittest.TestCase):
    """Repairing the JSON buys exactly one build cycle.

    `benchmarks.json` and `wall/wall.json` do not hold `our_entry`; they are
    handed it. `build_benchmarks.py`'s module-level `_CLOSURE` is written into
    `benchmarks.json`, `lab_stats.research_programs()` reads it back out of
    that file, and `build_wall.py` writes it onto `wall/wall.json`. A count
    corrected in the two JSON files and not in the literal survives until the
    next `python sdk/scripts/build_benchmarks.py`, and this lab has already
    made that exact mistake once -- the generator's own comment records the
    round-5 session hand-updating both JSON files and leaving the literal at
    round 3, caught a day later by rung V7.

    So the assertion is not "the JSON is right". It is "the three copies are
    the same string", which is the only form of it a regeneration cannot
    quietly undo.
    """

    def _generator_entry(self) -> str:
        gen = REPO / "sdk" / "scripts" / "build_benchmarks.py"
        self.assertTrue(gen.exists(), "the generator is gone; this test "
                                      "asserts nothing without it")
        for node in ast.parse(gen.read_text(encoding="utf-8")).body:
            if (isinstance(node, ast.Assign) and len(node.targets) == 1
                    and getattr(node.targets[0], "id", None) == "_CLOSURE"):
                return ast.literal_eval(node.value)["our_entry"]
        self.fail("_CLOSURE is not a module-level literal in the generator: "
                  "this test's subject has moved and it is asserting nothing")

    @staticmethod
    def _entry_in(payload):
        if isinstance(payload, dict):
            if "our_entry" in payload:
                return payload["our_entry"]
            for value in payload.values():
                found = TheBestOnBoardCountIsFixedAtItsGeneratorTests \
                    ._entry_in(value)
                if found is not None:
                    return found
        return None

    def test_the_generator_and_both_files_it_feeds_carry_one_string(self):
        source = self._generator_entry()
        for rel in ("demo-output/website/benchmarks.json",
                    "demo-output/website/wall/wall.json"):
            path = REPO / rel
            self.assertTrue(path.exists(), f"{rel} is gone")
            written = self._entry_in(json.loads(path.read_text("utf-8")))
            self.assertEqual(source, written,
                             f"{rel} has drifted from the literal that writes "
                             f"it; the next build would revert it")

    def test_the_generator_would_not_write_a_stale_count(self):
        """Read through the SAME derivation the guard uses, so the count is
        never compared against a number typed into this test."""
        self.assertEqual([], sa._best_on_board_faults(self._generator_entry()))

    def test_the_live_wall_passes(self):
        result = sa.check_closure_entry_of_record()
        self.assertEqual(sa.PASS, result.status, result.detail)

    def test_the_wall_passes_without_its_struck_text(self):
        """The tombstone control, applied to the count this time.

        The superseded `four of the eight` is KEPT on the wall under L-76 and
        must be: the correction is the finding. But the wall must satisfy the
        rule on what it still ASSERTS, so both dated strikes are cut out and
        the verdict re-taken on what is left.
        """
        entry = self._generator_entry()
        live = re.sub(r"STRUCK 2026-08-11,.*?standings now\. ", "", entry,
                      flags=re.S)
        self.assertNotEqual(entry, live, "the strike this control cuts is not "
                                         "there; it is exercising nothing")
        self.assertNotIn("four of the eight", live,
                         "the superseded count survives outside the strike")
        self.assertEqual([], sa._best_on_board_faults(live))
        self.assertEqual([], sa._rank_companions_missing(live))

    def test_the_superseded_count_is_kept_and_not_deleted(self):
        """L-76 in the other direction: a falsified claim is STRUCK AND KEPT.
        Silently deleting it would also make the guard green, and that is the
        wrong green."""
        entry = self._generator_entry()
        self.assertIn("four of the eight test cases", entry)
        self.assertIn("STRUCK 2026-08-11", entry)


class TheSubmissionDraftHeadingCarriesTheCountTests(unittest.TestCase):
    """§4.7 is the document's own highest-priority disclosure, and its HEADING
    stated a count from the five-entry board of 2026-05-04.

    The correct figures existed -- in a banner 180 lines further down. A
    heading is the part of a section a reader takes away, so a live figure
    parked in a banner and a dead one in the heading is the disclosure failing
    in the one place it is most read. Both superseded counts ("two of five",
    then "four of eight") are kept struck under L-76; what this pins is that
    the heading now leads with the count the board actually supports, and that
    the number is the DERIVED one rather than a digit typed into this test.
    """

    def _heading(self) -> str:
        path = (REPO / "demo-output" / "website"
                / "CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md")
        self.assertTrue(path.exists(), "the draft is gone; this test asserts "
                                       "nothing without it")
        heads = [line for line in path.read_text(encoding="utf-8").splitlines()
                 if line.startswith("### 4.7 ")]
        self.assertEqual(1, len(heads), heads)
        return heads[0]

    def test_the_heading_states_the_derived_count(self):
        facts = sa._closure_facts()
        self.assertEqual([], facts["stale"], facts["stale"])
        words = {2: "two", 3: "three", 4: "four", 5: "five", 0: "zero"}
        best = words.get(len(facts["best"]), str(len(facts["best"])))
        self.assertIn(f"{best} of eight", self._heading().lower(),
                      "the heading does not state the count the board "
                      "supports")

    def test_the_superseded_headline_count_is_struck_not_deleted(self):
        self.assertIn("~~two of five~~", self._heading())

    def test_the_disclosure_is_not_only_in_a_banner(self):
        """The count in the heading must travel with the reason it matters --
        that every row it counts is the organisers' baseline. Otherwise the
        repair is a number swap and the section still under-discloses."""
        self.assertRegex(self._heading().lower(), r"baseline")


if __name__ == "__main__":
    unittest.main()
