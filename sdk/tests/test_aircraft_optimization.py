"""Aircraft L/D optimization: requirement parsing, sizing, and routing (#1)."""

import os
import unittest
from pathlib import Path

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
    def setUp(self):
        # Keep CI fast: the on-camera pacing (~120 ms/candidate) is off in tests.
        os.environ["CERTONOMOUS_SWEEP_PACE_MS"] = "0"

    def test_main_runs_and_reports_a_feasible_optimum(self):
        events = {}
        verdict = {}
        certificate = {}

        def emit(event, payload):
            events[event] = events.get(event, 0) + 1
            if event == "result.verdict":
                verdict.update(payload)
            if event == "certificate.ready":
                certificate.update(payload)

        rc = main(request="Optimize the L/D of an airliner for 300 passengers, "
                          "6000 km range, takeoff 85 m/s, landing 72 m/s", emit=emit)
        self.assertEqual(rc, 0)
        self.assertGreater(events.get("landscape.point", 0), 10)
        self.assertEqual(events.get("report.ready"), 1)
        self.assertEqual(verdict.get("tier"), "CONCEPTUAL MODEL")
        self.assertNotEqual(verdict.get("value"), "none")
        # The dispatch panel and the live trace are fed as the grid is screened.
        self.assertGreater(events.get("dispatch.update", 0), 20)
        self.assertGreater(events.get("trace.point", 0), 0)
        # Act 1 carries a Certonomous certificate with its evidence seal. On a
        # solver-less run the finalists are not solved, so the fidelity is the
        # conceptual screen; the seal and human number are still issued.
        self.assertEqual(events.get("certificate.ready"), 1)
        self.assertEqual(certificate.get("dir"), "aircraft-optimization")
        self.assertTrue(certificate.get("certificate_no", "").startswith("C-"))
        self.assertTrue(Path(certificate.get("path", "")).exists())

    def test_router_sends_aircraft_ld_prompts_here(self):
        route = classify("optimize the lift-to-drag of this airplane for 250 passengers")
        self.assertEqual(route.intent, AIRCRAFT_OPTIMIZATION)

    # The short demo-day directive: hyphenated "lift-drag", a constraints list,
    # a spoken time budget, and a compute-headroom ask. It must route to the
    # aircraft act and carry BOTH live constraints as params.
    SHORT_DIRECTIVE = (
        "Optimize lift-drag ratio of a twin-aisle airliner with following "
        "constraints: - 300 passengers -6000 km range, take off speed: 85 m/s , "
        "landing speed 72 m/s. Also I want this to be super quick because I am "
        "shooting a demo right now so 2 min at most. I am running locally so "
        "don't use all my workers.")

    def test_short_demo_directive_routes_with_live_constraints(self):
        route = classify(self.SHORT_DIRECTIVE)
        self.assertEqual(route.intent, AIRCRAFT_OPTIMIZATION)
        self.assertEqual(route.params.get("deadline_minutes"), 2.0)
        self.assertTrue(route.params.get("hold_workers_back"))

    def test_short_demo_directive_requirements_parse(self):
        from workflows.aircraft_optimization import parse_requirements
        reqs = parse_requirements(self.SHORT_DIRECTIVE)
        self.assertEqual(reqs["passengers"], 300)
        self.assertEqual(reqs["range_km"], 6000.0)
        self.assertEqual(reqs["takeoff_speed"], 85.0)
        self.assertEqual(reqs["landing_speed"], 72.0)
        self.assertTrue(all(reqs[k] for k in (
            "passengers_stated", "range_stated", "takeoff_stated", "landing_stated")))

    def test_worker_cap_and_time_budget_are_on_the_record(self):
        from workflows.aircraft_optimization import main
        lines = []
        rc = main(request=self.SHORT_DIRECTIVE,
                  params={"deadline_minutes": 2.0, "hold_workers_back": True},
                  emit=lambda e, p: lines.append((e, p)))
        self.assertEqual(rc, 0)
        said = " ".join(p.get("message", "") for e, p in lines
                        if e == "transcript.entry")
        self.assertIn("leave headroom", said)
        self.assertIn("Time budget on the record: 2 minutes", said)


if __name__ == "__main__":
    unittest.main()
