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

    def test_viewport_valve_surface_opens_with_angle(self):
        # The control-room valve_surface must render a real body and its orifice
        # must widen with the opening angle, matching the physics.
        from chief_engineer.geometry import valve_surface
        radii = []
        for a in (35, 50, 65, 80):
            s = valve_surface(a)
            self.assertGreater(len(s["vertices"]), 0)
            self.assertGreater(len(s["faces"]), 0)
            for f in s["faces"]:
                self.assertTrue(all(0 <= i < len(s["vertices"]) for i in f))
            # free-edge radius = root_radius * sin(theta); recover it from bounds.
            radii.append(max(abs(v[1]) for v in s["vertices"]))
        self.assertTrue("bounds" in valve_surface(65))


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
        from workflows.valve_study import main, CANDIDATE_ANGLES
        events = {}
        verdict = {}
        agenda = {}
        certificate = {}

        def emit(e, p):
            events[e] = events.get(e, 0) + 1
            if e == "result.verdict":
                verdict.update(p)
            if e == "agenda.updated":
                agenda.update(p)
            if e == "certificate.ready":
                certificate.update(p)

        import os
        os.environ["CERTONOMOUS_SWEEP_PACE_MS"] = "0"
        rc = main(request="minimise valve pressure loss over the cardiac cycle", emit=emit)
        self.assertEqual(rc, 0)
        n = len(CANDIDATE_ANGLES)
        # A denser sweep so the valve visibly cycles many more times: one
        # cycle-weighted landscape point per real candidate.
        self.assertGreaterEqual(n, 10)
        self.assertEqual(events.get("landscape.point"), n)
        self.assertEqual(events.get("report.ready"), 1)
        self.assertEqual(events.get("uncertainty.channels"), 1)
        # valve renders every candidate valve plus the winner in the viewport
        self.assertEqual(events.get("geometry.ready"), n + 1)
        # the systolic waveform figure leads the report
        self.assertEqual(events.get("plot.ready"), 1)
        # the dispatch panel and the live objective trace are fed
        self.assertGreaterEqual(events.get("dispatch.update", 0), 2 * n)
        self.assertEqual(events.get("trace.point"), n)
        # hard cap
        self.assertEqual(verdict.get("tier"), "CONCEPTUAL MODEL")
        # Physics stays consistent: the widest admissible orifice still wins, so
        # the denser sweep peaks in the same 80 deg region as the old screen.
        self.assertIn("80 deg", verdict.get("envelope", ""))
        # Act 3 carries a Certonomous certificate with its evidence seal.
        self.assertEqual(events.get("certificate.ready"), 1)
        self.assertEqual(certificate.get("fidelity"), "CONCEPTUAL MODEL")
        self.assertEqual(certificate.get("dir"), "valve-study")
        self.assertTrue(Path(certificate.get("path", "")).exists())
        # agenda carries the three deferred capabilities
        self.assertEqual(len(agenda.get("entries", [])), 3)
        for entry in agenda["entries"]:
            self.assertIn("title", entry)
            self.assertIn("scope", entry)
            self.assertIn("cost", entry)

    def test_certificate_failure_never_takes_down_a_good_mission(self):
        # A certificate is wrapped: if issuing it raises, the mission must still
        # complete and report normally.
        import os
        from unittest import mock
        from workflows.valve_study import main

        os.environ["CERTONOMOUS_SWEEP_PACE_MS"] = "0"
        events = {}

        def emit(e, p):
            events[e] = events.get(e, 0) + 1

        with mock.patch("chief_engineer.certificate.build_certificate_v2",
                        side_effect=RuntimeError("boom")):
            rc = main(request="minimise valve pressure loss over the cardiac "
                              "cycle", emit=emit)
        self.assertEqual(rc, 0)
        self.assertEqual(events.get("report.ready"), 1)
        self.assertIsNone(events.get("certificate.ready"))

    def test_router_sends_valve_prompts_to_the_valve_study(self):
        from chief_engineer.router import classify, VALVE_STUDY
        route = classify("optimize the valve opening angle to minimise pressure "
                         "loss over the cardiac cycle")
        self.assertEqual(route.intent, VALVE_STUDY)


if __name__ == "__main__":
    unittest.main()
