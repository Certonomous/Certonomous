"""A stated Ahmed slant angle reaches the body that actually has that slant.

The act runs a family of configurations and stages a surface for each, but its
default is the 25 degree body. A prompt naming 35 degrees used to reach the act
with no surface at all, solve the 25 degree body, and say so. Honest, and the
wrong answer to the question asked.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))

from chief_engineer.router import AHMED_BODY, classify  # noqa: E402
from workflows.ahmed_body import identify_configuration  # noqa: E402

TWENTY_FIVE = ("Solve the Ahmed body with the 25 degree slant and check the "
               "drag against the wind tunnel.")


class SlantResolutionTests(unittest.TestCase):
    def test_thirty_five_degrees_resolves_to_the_thirty_five_degree_body(self):
        for prompt in ("Solve the Ahmed body with the 35 degree slant and "
                       "check the drag against the wind tunnel.",
                       "Run the Ahmed body at a 35 degree rear slant.",
                       "Ahmed body, slant: 35 degrees."):
            with self.subTest(prompt=prompt):
                route = classify(prompt)
                self.assertEqual(route.intent, AHMED_BODY)
                self.assertEqual(route.params.get("surface"), "ahmed_35.stl")

    def test_twenty_five_degrees_still_resolves_to_its_own_body(self):
        route = classify(TWENTY_FIVE)
        self.assertEqual(route.intent, AHMED_BODY)
        self.assertEqual(route.params.get("surface"), "ahmed_25.stl")

    def test_the_rehearsed_prompt_keeps_its_confidence_number(self):
        # The resolution touches params only, never the scores, so the number
        # the route panel puts on camera for the rehearsed prompt is the one
        # it has always shown.
        self.assertEqual(classify(TWENTY_FIVE).confidence, 0.51)

    def test_an_angle_with_no_staged_body_says_so_instead_of_substituting(self):
        route = classify("Solve the Ahmed body with a 40 degree slant.")
        self.assertEqual(route.intent, AHMED_BODY)
        self.assertIsNone(route.params.get("surface"))
        self.assertIn("40 degree", route.params.get("surface_unavailable", ""))

    def test_naming_no_angle_leaves_the_act_its_own_default(self):
        route = classify("Solve the Ahmed body and check the drag.")
        self.assertEqual(route.intent, AHMED_BODY)
        self.assertIsNone(route.params.get("surface"))

    def test_the_resolved_surface_is_what_the_act_then_measures(self):
        # The act never trusts the resolution: it measures the slant off the
        # surface it receives. These two must agree or the label would lie.
        for prompt, angle in ((TWENTY_FIVE, 25.0),
                              ("Run the Ahmed body at a 35 degree rear "
                               "slant.", 35.0)):
            with self.subTest(angle=angle):
                surface = classify(prompt).params.get("surface")
                _, label, measured, refusal = identify_configuration(surface)
                self.assertEqual(refusal, "")
                self.assertEqual(measured, angle)
                self.assertEqual(label, f"ahmed_{int(angle)}")

    def test_passing_the_default_surface_matches_passing_nothing(self):
        # Why the 25 degree act cannot move: the act resolves an explicit
        # ahmed_25.stl to exactly what it resolves None to.
        self.assertEqual(identify_configuration("ahmed_25.stl"),
                         identify_configuration(None))


if __name__ == "__main__":
    unittest.main()
