"""The Chief Researcher method-selection memo branches on mission properties."""

import unittest

from chief_engineer.researcher import (BULLET, ENGINEER_ACK, MissionProperties,
                                       method_memo)

_VENDOR_WORDS = ("openfoam", "vspaero", "openvsp", "simplefoam", "snappyhexmesh",
                 "pytorch", "tensorflow", "scipy", "numpy", "docker")


def _optimization():
    return MissionProperties(kind="parametric-optimization", objective="maximise L/D",
                             dimensionality=2, regime="steady", smoothness="smooth",
                             fidelity="a conceptual sizing model")


def _single_body():
    return MissionProperties(kind="single-body-study", objective="a trustworthy drag",
                             dimensionality=0, regime="steady turbulent (RANS)",
                             smoothness="gated", fidelity="a solved field",
                             admissibility_cite="against the standard mesh-quality band")


def _bullets(entry: str) -> list[str]:
    return [b.strip() for b in entry.split(BULLET) if b.strip()]


class MemoStructureTests(unittest.TestCase):
    def test_memo_is_two_bulleted_entries(self):
        memo = method_memo(_optimization())
        self.assertEqual(len(memo), 2)
        for entry in memo:
            self.assertTrue(entry.startswith(BULLET))

    def test_house_style_one_to_three_bullets_of_fourteen_words(self):
        for props in (_optimization(), _single_body()):
            for entry in method_memo(props):
                items = _bullets(entry)
                self.assertTrue(1 <= len(items) <= 3, items)
                for item in items:
                    self.assertLessEqual(len(item.split()), 15, item)

    def test_optimization_and_single_body_differ_substantively(self):
        opt = method_memo(_optimization())
        one = method_memo(_single_body())
        self.assertNotEqual(opt[0], one[0])
        self.assertNotEqual(opt[1], one[1])
        self.assertIn("2-parameter space", opt[0])
        self.assertIn("Single fixed body", one[0])
        self.assertIn("measurement, not an optimisation", one[0])
        self.assertIn("Rejected:", opt[0])
        self.assertIn("Rejected:", one[0])

    def test_smooth_steady_optimization_speaks_the_gradient_in_method_terms(self):
        core = method_memo(_optimization())[0].lower()
        self.assertIn("gradient", core)
        self.assertIn("ensemble", core)

    def test_admissibility_uses_the_cited_basis_when_supplied(self):
        self.assertIn("standard mesh-quality band", method_memo(_single_body())[1])

    def test_no_tool_or_vendor_names_anywhere(self):
        for props in (_optimization(), _single_body()):
            blob = " ".join(method_memo(props)).lower()
            for word in _VENDOR_WORDS:
                self.assertNotIn(word, blob)

    def test_engineer_ack_is_terse(self):
        self.assertEqual(ENGINEER_ACK, "On it.")


if __name__ == "__main__":
    unittest.main()
