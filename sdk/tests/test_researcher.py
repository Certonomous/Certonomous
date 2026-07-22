"""The Chief Researcher method-selection memo branches on mission properties."""

import unittest

from chief_engineer.researcher import ENGINEER_ACK, MissionProperties, method_memo

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


class MemoStructureTests(unittest.TestCase):
    def test_memo_has_the_four_parts_in_order(self):
        memo = method_memo(_optimization())
        self.assertEqual(len(memo), 4)
        self.assertTrue(memo[0].startswith("Problem classification"))
        self.assertTrue(memo[1].startswith("Chosen strategy"))
        self.assertTrue(memo[2].startswith("Rejected"))
        self.assertTrue(memo[3].startswith("Admissibility"))

    def test_optimization_and_single_body_differ_substantively(self):
        opt = method_memo(_optimization())
        one = method_memo(_single_body())
        # Structurally the same shape, materially different content.
        self.assertNotEqual(opt[0], one[0])   # classification
        self.assertNotEqual(opt[1], one[1])   # strategy
        self.assertNotEqual(opt[2], one[2])   # rejected
        self.assertIn("design space", opt[0])
        self.assertIn("single fixed body", one[0])
        self.assertIn("measurement, not an optimisation", one[0])
        self.assertIn("nothing to optimise", one[1])

    def test_smooth_steady_optimization_speaks_the_gradient_in_method_terms(self):
        strategy = method_memo(_optimization())[1]
        self.assertIn("gradient", strategy.lower())
        self.assertIn("backpropagation", strategy.lower())
        self.assertIn("ensemble", strategy.lower())

    def test_admissibility_uses_the_cited_basis_when_supplied(self):
        self.assertIn("standard mesh-quality band", method_memo(_single_body())[3])

    def test_no_tool_or_vendor_names_anywhere(self):
        for props in (_optimization(), _single_body()):
            blob = " ".join(method_memo(props)).lower()
            for word in _VENDOR_WORDS:
                self.assertNotIn(word, blob)

    def test_engineer_ack_is_terse(self):
        self.assertEqual(ENGINEER_ACK, "On it.")


if __name__ == "__main__":
    unittest.main()
