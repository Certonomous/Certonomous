"""Pins for `scripts/control_kind.py` and its first adopter.

WHAT THESE ASSERT, AND WHY IT IS NOT THE LABEL
==============================================
The whole point of the module is that a caller CANNOT declare a control to be a
recognition control -- the kind is derived from the evidence supplied. So the
central tests plant evidence and assert the DERIVED kind, and one of them names
a control "recognition control" while supplying reachability evidence and
requires the module to disagree with it.

THE FIXTURE IS THE MEASURED FAILURE ITSELF. A sweep returned a false zero
because *"the tie is lost"* and *"the tie was lost"* share no 5-gram. That pair
is used verbatim below: a literal sweep for the first form has a reachability
control that FIRES and a recognition control that FAILS, and the tests assert
the module tells those two situations apart rather than reporting "the control
fired" for both.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts"


def load(name: str, filename: str):
    """Load by explicit path; `resolve()` follows symlinks so a harness mirror
    must be able to substitute the file under test."""
    env = os.environ.get(f"{name.upper()}_PATH")
    target = Path(env) if env else SCRIPTS / filename
    spec = importlib.util.spec_from_file_location(f"_{name}", target)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"_{name}"] = module
    spec.loader.exec_module(module)
    return module


CK = load("control_kind", "control_kind.py")
RECON = load("check_docket_reconciliation", "check_docket_reconciliation.py")


# --- the measured failure, as a sweep -------------------------------------
CORPUS = "the report says the tie was lost during the second round"
LITERAL_PATTERN = "the tie is lost"          # what the sweep actually searched


def literal_sweep(text: str) -> bool:
    return LITERAL_PATTERN in text


class TheIsWasFailureIsToldApart(unittest.TestCase):
    """One inflected verb. A reachability control fires; recognition does not."""

    def test_the_sweep_really_returns_a_false_zero_on_this_corpus(self):
        """The fixture must be a genuine false zero or the rest is theatre."""
        self.assertFalse(literal_sweep(CORPUS))     # the sweep finds nothing
        self.assertIn("tie was lost", CORPUS)       # yet the claim IS present

    def test_a_reachability_control_fires_and_does_not_earn_the_zero(self):
        ledger = CK.ControlLedger(claim_class="a lost-tie claim")
        ledger.plant("can the reader open the corpus",
                     vocabulary="plain prose",
                     planted={LITERAL_PATTERN: literal_sweep(
                         CORPUS + " " + LITERAL_PATTERN)})
        self.assertEqual(ledger.kind, CK.REACHABILITY)
        verdict, why = ledger.verdict_for(0)
        self.assertEqual(verdict, CK.ZERO_IS_UNSUPPORTED)
        self.assertIn("not a measurement of absence", why)

    def test_a_recognition_control_on_the_same_sweep_is_BROKEN(self):
        """The variant the sweep cannot see is exactly what must be planted."""
        ledger = CK.ControlLedger(claim_class="a lost-tie claim")
        ledger.plant("does the pattern recognise the claim class",
                     vocabulary="the claim's own wording",
                     planted={
                         "the tie is lost": literal_sweep("the tie is lost"),
                         "the tie was lost": literal_sweep("the tie was lost"),
                     })
        self.assertEqual(ledger.kind, CK.BROKEN)
        verdict, why = ledger.verdict_for(0)
        self.assertEqual(verdict, CK.ZERO_IS_UNSUPPORTED)
        self.assertIn("the tie was lost", why)

    def test_the_two_kinds_produce_different_output(self):
        """The report must not render both as 'the control fired'."""
        reach = CK.ControlLedger(claim_class="a lost-tie claim")
        reach.plant("reader", vocabulary="prose",
                    planted={LITERAL_PATTERN: True})
        recog = CK.ControlLedger(claim_class="a lost-tie claim")
        recog.plant("pattern", vocabulary="the claim's own wording",
                    planted={"the tie is lost": True,
                             "the tie was lost": True})
        self.assertIn(CK.REACHABILITY, reach.render(0))
        self.assertIn(CK.RECOGNITION, recog.render(0))
        self.assertNotEqual(reach.render(0), recog.render(0))
        self.assertIn("ZERO_IS_UNSUPPORTED", reach.render(0))
        self.assertIn("ZERO_IS_A_MEASUREMENT", recog.render(0))


class TheCallerDoesNotDecideTheKind(unittest.TestCase):
    """The kind is derived from evidence, never from what it is called."""

    def test_naming_a_control_recognition_does_not_make_it_one(self):
        ledger = CK.ControlLedger(claim_class="anything")
        ledger.plant("recognition control", vocabulary="recognition",
                     planted={"one planted literal": True})
        self.assertEqual(ledger.kind, CK.REACHABILITY)
        self.assertIn("only one form was planted",
                      ledger.controls[0].classify()[1])

    def test_two_forms_that_are_substrings_are_not_independent(self):
        """`tie lost` inside `the tie lost` proves nothing about recognition."""
        ledger = CK.ControlLedger(claim_class="anything")
        ledger.plant("two forms", vocabulary="prose",
                     planted={"tie lost": True, "the tie lost": True})
        self.assertEqual(ledger.kind, CK.REACHABILITY)
        self.assertIn("substring", ledger.controls[0].classify()[1])

    def test_two_mutually_independent_forms_are_recognition(self):
        ledger = CK.ControlLedger(claim_class="anything")
        ledger.plant("two forms", vocabulary="prose",
                     planted={"the tie is lost": True,
                              "the tie was lost": True})
        self.assertEqual(ledger.kind, CK.RECOGNITION)

    def test_a_negative_form_that_matches_makes_the_control_BROKEN(self):
        ledger = CK.ControlLedger(claim_class="anything")
        ledger.plant("too loose", vocabulary="prose",
                     planted={"alpha one": True, "beta two": True},
                     negative={"this must not match": True})
        self.assertEqual(ledger.kind, CK.BROKEN)
        self.assertIn("too loose", ledger.controls[0].classify()[1])

    def test_no_control_at_all_is_not_a_measurement(self):
        ledger = CK.ControlLedger(claim_class="anything")
        self.assertEqual(ledger.kind, CK.NONE)
        verdict, why = ledger.verdict_for(0)
        self.assertEqual(verdict, CK.ZERO_IS_UNSUPPORTED)
        self.assertIn("NO control was run", why)

    def test_hits_make_the_zero_question_moot(self):
        ledger = CK.ControlLedger(claim_class="anything")
        ledger.plant("one", vocabulary="prose", planted={"x y z": True})
        verdict, _ = ledger.verdict_for(3)
        self.assertEqual(verdict, CK.NOT_A_ZERO)


class TheAdopterRefusesAnUnearnedZero(unittest.TestCase):
    """End to end through `check_docket_reconciliation`."""

    HEADER = "# d\n\n| id | f |\n| --- | --- |\n"

    def _docket(self, *ids):
        return self.HEADER + "".join(f"| {i} | x |\n" for i in ids)

    def test_its_own_control_is_recognition_and_the_zero_passes(self):
        result = RECON.reconcile(self._docket("D1", "D2"),
                                 self._docket("D1", "D2"))
        self.assertEqual(result["control_kind"], CK.RECOGNITION)
        self.assertEqual(result["verdict"], "PASS")

    def test_a_reachability_only_control_turns_the_same_pass_into_unknown(self):
        """THE PIN. Identical inputs; only the control kind differs."""
        weak = CK.ControlLedger(claim_class="a docket row id")
        weak.plant("reader only", vocabulary="docket rows",
                   planted={"| D9001 | a bare row |": True})
        result = RECON.reconcile(self._docket("D1", "D2"),
                                 self._docket("D1", "D2"), ledger=weak)
        self.assertEqual(result["control_kind"], CK.REACHABILITY)
        self.assertEqual(result["verdict"], "UNKNOWN")
        self.assertEqual(result["exit_code"], RECON.EXIT_UNKNOWN)
        self.assertIn("not a measurement of absence", result["zero_because"])

    def test_a_real_divergence_is_still_reported_under_a_weak_control(self):
        """The control gates the ZERO, never a finding the sweep did make."""
        weak = CK.ControlLedger(claim_class="a docket row id")
        weak.plant("reader only", vocabulary="docket rows",
                   planted={"| D9001 | a bare row |": True})
        result = RECON.reconcile(self._docket("D1", "D2"),
                                 self._docket("D1"), ledger=weak)
        self.assertEqual(result["head_only"], ["D2"])
        self.assertEqual(result["verdict"], "FAIL")

    def test_the_control_block_is_printed_on_every_run(self):
        result = RECON.reconcile(self._docket("D1"), self._docket("D1"))
        text = RECON.render(result, "HEAD", "docs/DOCKET.md",
                            Path("docs/DOCKET.md"))
        self.assertIn("CONTROL KIND:", text)
        self.assertIn(CK.RECOGNITION, text)

    def test_the_adopters_own_planted_forms_are_mutually_independent(self):
        """If they were not, its control would silently be reachability."""
        ledger = RECON.run_controls()
        control = ledger.controls[0]
        self.assertGreaterEqual(len(control.distinct_forms), 2)
        self.assertEqual(control.classify()[0], CK.RECOGNITION)
        self.assertTrue(control.negatives_held)


if __name__ == "__main__":
    unittest.main()
