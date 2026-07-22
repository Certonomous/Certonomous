"""Aircraft L/D optimization: requirement parsing, sizing, and routing (#1)."""

import unittest

from chief_engineer.router import AIRCRAFT_OPTIMIZATION, classify
from workflows.aircraft_optimization import (evaluate_design, main,
                                             parse_requirements)


class RequirementParsingTests(unittest.TestCase):
    def test_extracts_all_stated_requirements(self):
        reqs = parse_requirements(
            "optimize L/D for 300 passengers, 6000 km range, takeoff 85 m/s, landing 72 m/s")
        self.assertEqual(reqs["passengers"], 300)
        self.assertAlmostEqual(reqs["range_km"], 6000.0)
        self.assertAlmostEqual(reqs["takeoff_speed"], 85.0)
        self.assertAlmostEqual(reqs["landing_speed"], 72.0)
        self.assertTrue(reqs["range_stated"] and reqs["takeoff_stated"])

    def test_missing_requirements_get_flagged_defaults(self):
        reqs = parse_requirements("optimize the lift to drag of this airliner")
        self.assertFalse(reqs["range_stated"])
        self.assertFalse(reqs["passengers_stated"])
        self.assertGreater(reqs["range_km"], 0)   # a default is supplied

    def test_knots_are_converted(self):
        reqs = parse_requirements("landing speed 140 knots for 200 pax")
        self.assertAlmostEqual(reqs["landing_speed"], 140 * 0.514444, places=2)


class SizingModelTests(unittest.TestCase):
    REQS = {"passengers": 300, "range_km": 6000.0, "takeoff_speed": 85.0,
            "landing_speed": 72.0, "passengers_stated": True, "range_stated": True,
            "takeoff_stated": True, "landing_stated": True}

    def test_l_over_d_is_in_a_sane_airliner_band(self):
        r = evaluate_design(58.0, 360.0, 27.5, self.REQS)
        self.assertGreater(r["L_D"], 8)
        self.assertLess(r["L_D"], 30)
        self.assertGreater(r["mtow_kg"], 80_000)   # 300 pax is a heavy jet

    def test_a_tiny_wing_fails_the_landing_speed(self):
        # Small area -> high stall speed -> infeasible on landing.
        r = evaluate_design(64.0, 200.0, 27.5, self.REQS)
        self.assertFalse(r["feasible"])
        self.assertTrue(any("landing" in v or "approach" in v for v in r["violations"]))

    def test_higher_aspect_ratio_raises_l_over_d(self):
        low_ar = evaluate_design(40.0, 360.0, 27.5, self.REQS)["L_D"]
        high_ar = evaluate_design(58.0, 360.0, 27.5, self.REQS)["L_D"]
        self.assertGreater(high_ar, low_ar)


class WorkflowTests(unittest.TestCase):
    def test_main_runs_and_reports_a_feasible_optimum(self):
        events = {}
        verdict = {}

        def emit(event, payload):
            events[event] = events.get(event, 0) + 1
            if event == "result.verdict":
                verdict.update(payload)

        rc = main(request="Optimize the L/D of an airliner for 300 passengers, "
                          "6000 km range, takeoff 85 m/s, landing 72 m/s", emit=emit)
        self.assertEqual(rc, 0)
        self.assertGreater(events.get("landscape.point", 0), 10)
        self.assertEqual(events.get("report.ready"), 1)
        self.assertEqual(verdict.get("tier"), "TREND ONLY")
        self.assertNotEqual(verdict.get("value"), "none")

    def test_router_sends_aircraft_ld_prompts_here(self):
        route = classify("optimize the lift-to-drag of this airplane for 250 passengers")
        self.assertEqual(route.intent, AIRCRAFT_OPTIMIZATION)


if __name__ == "__main__":
    unittest.main()
