"""Act 3 — the idealized valve: geometry, waveform, and the multi-point screen."""

import sys
import unittest
from pathlib import Path

_VALVE = Path(__file__).resolve().parents[2] / "models" / "curriculum" / "aortic_valve"
for _p in (str(_VALVE.parent), str(_VALVE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import generate_valve  # noqa: E402
import waveform  # noqa: E402


class GeometryTests(unittest.TestCase):
    def test_orifice_area_grows_with_opening_angle(self):
        areas = [generate_valve.effective_orifice_area(a) for a in (35, 50, 65, 80)]
        self.assertEqual(areas, sorted(areas))
        self.assertTrue(all(x > 0 for x in areas))

    def test_valve_builds_a_valid_triangle_mesh(self):
        V, F = generate_valve.build_valve(65.0)
        self.assertGreater(len(F), 0)
        self.assertTrue((F >= 0).all() and (F < len(V)).all())
        self.assertGreaterEqual(len(F), 3)

    def test_orifice_is_a_few_hundred_mm2_at_scale(self):
        area_mm2 = generate_valve.effective_orifice_area(80.0) * 1e6
        self.assertGreater(area_mm2, 100)
        self.assertLess(area_mm2, 500)


class WaveformTests(unittest.TestCase):
    def test_three_phase_points_weights_sum_to_one(self):
        phases = waveform.phase_points()
        self.assertEqual(len(phases), 3)
        self.assertAlmostEqual(sum(p.weight for p in phases), 1.0, places=9)

    def test_phases_are_ordered_accel_peak_decel(self):
        taus = [p.tau for p in waveform.phase_points()]
        self.assertEqual(taus, sorted(taus))
        weights = [p.weight for p in waveform.phase_points()]
        self.assertEqual(max(range(3), key=lambda i: weights[i]), 1)

    def test_womersley_is_the_high_aortic_value(self):
        alpha = waveform.womersley(0.0115)
        self.assertGreater(alpha, 10)   # aortic root is inertially unsteady
        self.assertLess(alpha, 25)


class WorkflowTests(unittest.TestCase):
    def test_multipoint_screen_grades_conceptual_model(self):
        from workflows.valve_study import main
        events = {}
        verdict = {}
        agenda = {}

        def emit(e, p):
            events[e] = events.get(e, 0) + 1
            if e == "result.verdict":
                verdict.update(p)
            if e == "agenda.updated":
                agenda.update(p)

        rc = main(request="minimise valve pressure loss over the cardiac cycle", emit=emit)
        self.assertEqual(rc, 0)
        # 4 candidates -> 4 cycle-weighted landscape points
        self.assertEqual(events.get("landscape.point"), 4)
        self.assertEqual(events.get("report.ready"), 1)
        self.assertEqual(events.get("uncertainty.channels"), 1)
        # hard cap
        self.assertEqual(verdict.get("tier"), "CONCEPTUAL MODEL")
        # agenda carries the three deferred capabilities
        self.assertEqual(len(agenda.get("entries", [])), 3)
        for entry in agenda["entries"]:
            self.assertIn("title", entry)
            self.assertIn("scope", entry)
            self.assertIn("cost", entry)

    def test_router_sends_valve_prompts_to_the_valve_study(self):
        from chief_engineer.router import classify, VALVE_STUDY
        route = classify("optimize the valve opening angle to minimise pressure "
                         "loss over the cardiac cycle")
        self.assertEqual(route.intent, VALVE_STUDY)


if __name__ == "__main__":
    unittest.main()
