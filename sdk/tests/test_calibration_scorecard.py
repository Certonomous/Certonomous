"""The instrument that grades this lab's forecasts, graded.

`scripts/calibration_scorecard.py` reports whether the lab's compute forecasts
are any good, and its output is quoted into dispatch briefs. A defect here does
not produce one wrong number; it produces a wrong self-assessment that every
other decision is priced against. Three defects were found and fixed on
2026-08-14, and each one has a mutation test below: reintroduce the defect and
the matching test reddens.

Each fix also carries a MUST-NOT-MATCH control (L-84: a positive control proves
an instrument can fire, not that it fires only where it should).

  (1) intake reconciliation -- refusals visible and COUNTED, so the next
      silently-dropped record announces itself as arithmetic rather than
      waiting for an audit. Control: the fix must not start ADMITTING records
      that are genuinely malformed.
  (2) the exact-zero class -- a forecast of 0 that cost 0 was printed `inf%
      off`. Control: it must not be scored as a hit either.
  (3) time ordering -- "three consecutive" was evaluated over filename order.
      Control: the fix must not reorder records that were already in order.
"""
from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "calibration_scorecard.py"


def _load():
    spec = importlib.util.spec_from_file_location("_calscore", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cs = _load()


def _pair(name, est, meas, created="2026-08-01T00:00:00Z"):
    rec = {"_file": f"{name}.json", "status": "done",
           "est_core_min": est, "measured_core_min": meas}
    if created is not None:
        rec["created_at"] = created
    return rec


class ExactZeroIsItsOwnClass(unittest.TestCase):
    """Defect (2). Zero forecast, zero spent: not a miss, and not a hit."""

    def test_a_zero_forecast_that_cost_zero_is_not_a_miss(self):
        # THE MUTATION: restore `err = ... if meas else float("inf")` and drop
        # the EXACT_ZERO branch, and this reddens -- the pair comes back as a
        # MISS with rel_error inf, which is what the instrument printed at
        # e9a02d31 for two perfectly correct forecasts.
        out = cs.score([_pair("zed", 0, 0)])
        pair = out["pairs"][0]
        self.assertEqual(pair["class"], cs.EXACT_ZERO)
        self.assertIsNone(pair["rel_error"],
                          "relative error is undefined when measured is 0, "
                          "never infinity")
        self.assertIsNot(pair["hit"], False,
                         "the most exactly-right forecast available scored "
                         "as a miss is defect class B2, a fail-false")

    def test_and_is_not_scored_as_a_hit_either(self):
        # MUST-NOT-MATCH CONTROL for (2). The obvious over-correction is to
        # count 0->0 as a hit. That inflates the headline on records that
        # priced no compute AND makes §4's auto-approve gate reachable by
        # filing three zero-cost proposals in a row. Neither numerator nor
        # denominator may move.
        out = cs.score([_pair("zed", 0, 0), _pair("z2", 0, 0),
                        _pair("real", 100, 100)])
        self.assertIsNone(out["pairs"][0]["hit"])
        self.assertEqual(out["graded"], ["real"],
                         "an exact-zero pair is not graded evidence")
        self.assertEqual(out["hit_rate"], 1.0,
                         "1 of 1 graded, not 3 of 3")
        self.assertEqual(sorted(out["exact_zero"]), ["z2", "zed"])

    def test_exact_zero_pairs_cannot_open_the_auto_approve_gate(self):
        # The reason the class exists rather than the aesthetics of it: three
        # zero-cost records in a row must NOT satisfy 3-for-3.
        out = cs.score([_pair("z1", 0, 0, "2026-08-01T00:00:00Z"),
                        _pair("z2", 0, 0, "2026-08-02T00:00:00Z"),
                        _pair("z3", 0, 0, "2026-08-03T00:00:00Z")])
        self.assertFalse(out["rule_runnable"])
        self.assertIsNot(out["rule_satisfied"], True)

    def test_a_nonzero_forecast_that_measured_zero_is_still_a_miss(self):
        # The distinction the third class must not blur: budgeting compute for
        # work that cost none is a real forecasting error.
        out = cs.score([_pair("overbudget", 50, 0)])
        self.assertEqual(out["pairs"][0]["class"], cs.ZERO_MEASURED)
        self.assertFalse(out["pairs"][0]["hit"])


class ConsecutiveIsEvaluatedInTime(unittest.TestCase):
    """Defect (3). A rule about time, evaluated about time."""

    def test_the_window_is_time_ordered_not_filename_ordered(self):
        # THE MUTATION: restore `pairs[-CONSECUTIVE_HITS_REQUIRED:]` and this
        # reddens. Filenames sort z,y,x against dates that run the other way,
        # so the two windows are disjoint -- exactly the shape found in the
        # real corpus, where filename order scored three w4-* records while
        # the three most recent forecasts were s1/kfamily/pydafoam.
        # `load()` hands `score()` its records in filename order, so the
        # fixture arrives sorted by name with dates running the other way.
        # The two windows are then fully disjoint -- and, so the mutation
        # bites rather than merely differs, the filename window is three
        # straight HITS while the true last three contain a miss. Restore
        # `pairs[-3:]` and this instrument reports the lab as PASSING §4 on
        # three records chosen by alphabet.
        recs = [_pair("a", 10, 99, "2026-08-06T00:00:00Z"),   # newest, MISS
                _pair("b", 10, 10, "2026-08-05T00:00:00Z"),
                _pair("c", 10, 10, "2026-08-04T00:00:00Z"),
                _pair("d", 10, 10, "2026-08-03T00:00:00Z"),
                _pair("e", 10, 10, "2026-08-02T00:00:00Z"),
                _pair("f", 10, 10, "2026-08-01T00:00:00Z")]   # oldest
        out = cs.score(recs)
        self.assertEqual(out["consecutive_window"], ["c", "b", "a"])
        self.assertEqual(out["filename_order_window"], ["d", "e", "f"])
        self.assertFalse(set(out["consecutive_window"])
                         & set(out["filename_order_window"]),
                         "the two windows must be demonstrably disjoint")
        # The verdict follows the time-ordered window, not the alphabet.
        self.assertFalse(out["rule_satisfied"])
        # And the alphabet's window really would have passed, which is what
        # makes the old behaviour a fail-true and not just a different sort.
        by_id = {p["id"]: p for p in out["pairs"]}
        self.assertTrue(all(by_id[i]["hit"]
                            for i in out["filename_order_window"]))

    def test_already_ordered_records_are_not_reordered(self):
        # MUST-NOT-MATCH CONTROL for (3). A sort keyed on the wrong field, or
        # an unstable one, would also "fix" the disjoint-window symptom while
        # scrambling corpora that were already correct. When filename order
        # and date order agree, the fix must be a no-op.
        recs = [_pair("a", 10, 10, "2026-08-01T00:00:00Z"),
                _pair("b", 10, 10, "2026-08-02T00:00:00Z"),
                _pair("c", 10, 10, "2026-08-03T00:00:00Z"),
                _pair("d", 10, 10, "2026-08-04T00:00:00Z")]
        out = cs.score(recs)
        self.assertEqual(out["consecutive_window"],
                         out["filename_order_window"],
                         "already-ordered records must not move")
        self.assertEqual(out["consecutive_window"], ["b", "c", "d"])
        self.assertTrue(out["rule_satisfied"],
                        "and a genuine 3-for-3 must still be able to pass")

    def test_an_undated_record_is_unknown_never_sorted_to_an_end(self):
        # Three-valued. A record with no created_at could sort anywhere,
        # including into the last three, so the verdict is UNKNOWN rather than
        # a False that pretends to knowledge. THE MUTATION: default the sort
        # key to "" or "9999" and this reddens.
        recs = [_pair("a", 10, 10, "2026-08-01T00:00:00Z"),
                _pair("b", 10, 10, "2026-08-02T00:00:00Z"),
                _pair("c", 10, 10, "2026-08-03T00:00:00Z"),
                _pair("nodate", 10, 99, None)]
        out = cs.score(recs)
        self.assertEqual(out["undated"], ["nodate"])
        self.assertIsNone(out["rule_satisfied"],
                          "UNKNOWN, not False and not True")
        self.assertNotIn("nodate", out["consecutive_window"])

    def test_a_blank_date_is_undated_not_a_valid_key(self):
        self.assertIsNone(cs._sort_key({"created_at": "   "}))
        self.assertIsNone(cs._sort_key({}))
        self.assertEqual(cs._sort_key({"created_at": "2026-08-01"}),
                         "2026-08-01")


class IntakeIsReconciled(unittest.TestCase):
    """Defect (1). Refusals visible and counted -- structurally, not per-record."""

    def setUp(self):
        self.records, _ = cs.load()
        self.intake = cs.intake(self.records)
        # Deliberately NOT skipTest on an unimportable agenda: a suite that
        # skips itself when the thing it guards goes missing is the fail-open
        # shape this whole repair is about.
        self.assertTrue(self.intake.get("available"),
                        f"inbox reader unimportable: "
                        f"{self.intake.get('error')}")

    def test_the_refusal_ledger_has_a_caller_outside_the_tests(self):
        # THE FINDING BEHIND THE FIX. refused_inbox() was written expressly
        # against "a filter nobody can see" and then wired to nothing outside
        # sdk/tests/ -- the same silence one indirection further out. THE
        # MUTATION: unwire intake() from collect() and this reddens, because
        # it asserts on what the SHIPPED entry point returns, not on a helper
        # the test called itself.
        shipped = cs.collect()["intake"]
        self.assertTrue(shipped["available"],
                        "collect() no longer calls the refusal ledger")
        self.assertIsInstance(shipped["refused_count"], int)
        self.assertIn("reconciles", shipped)

    def test_files_on_disk_equal_admitted_plus_refused(self):
        # The invariant is the deliverable. Patching the three known-bad
        # filenames would leave the fourth to be found by the next audit;
        # arithmetic that must balance makes the fourth announce itself.
        k = cs.collect()["intake"]
        self.assertTrue(
            k["reconciles"],
            f"{k['files_on_disk']} on disk != {k['admitted']} admitted + "
            f"{k['refused_count']} refused; residual {k['residual_files']}")
        self.assertEqual(k["files_on_disk"],
                         k["admitted"] + k["refused_count"])

    def test_a_record_dropped_with_no_refusal_recorded_is_caught(self):
        # The invariant EXERCISED, not recomputed. An earlier version of this
        # test did the arithmetic itself and so passed against an intake()
        # hardcoded to `reconciles = True` -- it proved only that subtraction
        # works. This one drives the real reader: make read_inbox() drop a
        # record while writing no refusal, and intake() must refuse to
        # reconcile and main() must exit nonzero.
        import sys
        sys.path.insert(0, str(REPO / "sdk"))
        from chief_engineer import agenda
        real = agenda.read_inbox
        try:
            agenda.read_inbox = lambda: real()[:-1]   # one vanishes, silently
            k = cs.intake(self.records)
            self.assertFalse(k["reconciles"],
                             "a silently dropped record must break the "
                             "arithmetic, not be absorbed by it")
            self.assertEqual(k["unreconciled_by"], 1)
            self.assertEqual(cs.main([]), 2,
                             "an unreconciled intake must not exit 0")
        finally:
            agenda.read_inbox = real
        # ...and with the reader honest again, it balances.
        self.assertTrue(cs.intake(self.records)["reconciles"])
        self.assertEqual(cs.main([]), 0)

    def test_every_refusal_names_a_file_and_at_least_one_violation(self):
        for entry in self.intake["refused"]:
            self.assertTrue(entry["file"])
            self.assertTrue(entry["violations"],
                            f"{entry['file']} refused with no stated reason")

    def test_the_fix_does_not_admit_genuinely_malformed_records(self):
        # MUST-NOT-MATCH CONTROL for (1), and the trap the brief names: the
        # fix must make refusals VISIBLE, not make them stop happening. The
        # three refused records in the real corpus stay refused; reporting
        # them is not admitting them.
        self.assertGreater(self.intake["refused_count"], 0,
                           "corpus has known-refused records; if this is 0 "
                           "the reader started admitting malformed files")
        admitted_ids = set()
        import sys
        sys.path.insert(0, str(REPO / "sdk"))
        from chief_engineer import agenda
        for p in agenda.read_inbox():
            admitted_ids.add(p["id"])
        for entry in self.intake["refused"]:
            self.assertNotIn(
                entry["file"][:-5], admitted_ids,
                f"{entry['file']} is refused AND admitted -- the reporting "
                f"fix must not have re-opened the rails")

    def test_a_silently_coerced_status_is_named_and_costed(self):
        # `status if status in STATUSES else "proposed"` is the same silence
        # one field down: the file says one thing and the reader returns
        # another. Named and costed, so 807 core-min of queued work does not
        # read back as merely proposed with nothing saying so.
        for c in self.intake["status_coerced"]:
            self.assertNotEqual(c["status_on_disk"], c["read_back_as"])
            self.assertTrue(c["file"])


class TheRealCorpusResultsHold(unittest.TestCase):
    """The result that had to survive the repair, asserted so it keeps doing so."""

    def setUp(self):
        self.data = cs.collect()

    def test_the_three_consecutive_rule_is_not_satisfied(self):
        # A repair that flipped this green would have been the suspicious
        # outcome. Verified at 2026-08-14: the longest all-hit run in time
        # order is 2, against 3 required -- and it is 2 under every treatment
        # of the exact-zero class, so no scoring choice here manufactured it.
        self.assertIsNot(self.data["rule_satisfied"], True,
                         "the scorecard now reports the lab as PASSING its "
                         "own calibration rule -- do not ship this quietly")

    def test_the_longest_hit_run_is_short_of_the_bar(self):
        ordered = sorted((p for p in self.data["pairs"]
                          if p["class"] != cs.EXACT_ZERO),
                         key=lambda p: (p["dated"] or ""))
        best = cur = 0
        for p in ordered:
            cur = cur + 1 if p["hit"] else 0
            best = max(best, cur)
        self.assertLess(best, cs.CONSECUTIVE_HITS_REQUIRED)

    def test_a_newer_uncosted_record_displaces_the_window_and_is_named(self):
        # Ordering by date fixes WHICH recorded pairs are scored; it cannot
        # conjure pairs that were never recorded. If done work newer than the
        # window's start carries no cost, the "last three" is the last three
        # RECORDED, and the instrument must say so rather than imply a tail it
        # does not have. Synthetic, so it binds regardless of corpus drift.
        recs = [_pair("a", 10, 10, "2026-08-01T00:00:00Z"),
                _pair("b", 10, 10, "2026-08-02T00:00:00Z"),
                _pair("c", 10, 10, "2026-08-03T00:00:00Z"),
                {"_file": "newer-but-uncosted.json", "status": "done",
                 "est_core_min": 40, "measured_core_min": None,
                 "created_at": "2026-08-09T00:00:00Z"}]
        out = cs.score(recs)
        self.assertEqual(out["consecutive_window"], ["a", "b", "c"])
        self.assertEqual(out["window_displaced_by"], ["newer-but-uncosted"])
        # MUST-NOT-MATCH: an uncosted record OLDER than the window does not
        # displace it, so this does not fire on every gap in the corpus.
        recs[-1]["created_at"] = "2026-07-01T00:00:00Z"
        self.assertEqual(cs.score(recs)["window_displaced_by"], [])

    def test_the_record_gap_is_reported_and_is_the_larger_problem(self):
        # The honest headline. More completed work recorded no cost at all
        # than the forecasting has graded pairs to be wrong about.
        done = self.data["done"]
        unpaired = len(self.data["unpaired_done"])
        self.assertGreater(done, 0)
        self.assertEqual(unpaired + len(self.data["pairs"]), done,
                         "every done record is either paired or named as "
                         "carrying no measured cost")


if __name__ == "__main__":
    unittest.main()
