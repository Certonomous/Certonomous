"""The VSPAERO adapter seam — everything testable without the solver installed."""
from __future__ import annotations

import os
import unittest
from unittest import mock

from chief_engineer import vspaero
from chief_engineer.geometry import wing_surface
from workflows.aircraft_optimization import evaluate_design, parse_requirements


class Availability(unittest.TestCase):
    def test_not_available_without_prefix_or_install(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("OPENVSP_RUN_PREFIX", None)
            with mock.patch("chief_engineer.vspaero.Path.exists",
                            return_value=False):
                self.assertFalse(vspaero.available())

    def test_available_with_run_prefix(self):
        with mock.patch.dict(os.environ,
                             {"OPENVSP_RUN_PREFIX": "wsl -d Ubuntu --"}):
            self.assertTrue(vspaero.available())


class EvaluateMany(unittest.TestCase):
    def _api(self, tmp="mission-output/test-vspaero"):
        return vspaero.VspAeroWingApi(tmp, run_prefix="")

    def test_results_keep_input_order_and_failures_become_none(self):
        api = self._api()
        designs = [{"span": s} for s in (40.0, 46.0, 52.0)]

        def fake_evaluate(design, analyses=()):
            if design["span"] == 46.0:
                raise RuntimeError("solver refused")
            return {"matched": {"cdi": 0.01}, "built": dict(design)}

        seen: list[tuple[int, bool]] = []
        with mock.patch.object(api, "evaluate", side_effect=fake_evaluate):
            results = api.evaluate_many(
                designs, max_workers=3,
                on_result=lambda i, r, e: seen.append((i, e is None)))
        self.assertEqual(results[0]["built"], {"span": 40.0})
        self.assertIsNone(results[1])
        self.assertEqual(results[2]["built"], {"span": 52.0})
        self.assertEqual({(0, True), (1, False), (2, True)}, set(seen))


class WingSurface(unittest.TestCase):
    def test_planform_is_exact(self):
        span, area, taper = 52.0, 360.0, 0.3
        payload = wing_surface(span, area, taper=taper)
        bounds = payload["bounds"]
        self.assertAlmostEqual(bounds["max"][1] - bounds["min"][1], span)
        root = 2.0 * area / (span * (1.0 + taper))
        # The root station's chord extent matches the derived root chord.
        ys = [v[1] for v in payload["vertices"]]
        xs_root = [v[0] for v in payload["vertices"] if abs(v[1]) < 1e-9]
        self.assertAlmostEqual(max(xs_root) - min(xs_root), root, places=4)
        self.assertTrue(payload["faces"])

    def test_candidates_visibly_differ(self):
        small = wing_surface(34.0, 240.0)
        large = wing_surface(64.0, 420.0)
        self.assertNotEqual(small["bounds"], large["bounds"])


class FinalistInputs(unittest.TestCase):
    def test_cl_cruise_is_reported_for_the_solver_target(self):
        reqs = parse_requirements(
            "300 passengers, 6000 km range, take-off at 85 m/s, landing at 72 m/s")
        design = evaluate_design(64.0, 300.0, 27.5, reqs)
        self.assertIn("cl_cruise", design)
        self.assertGreater(design["cl_cruise"], 0.2)
        self.assertLess(design["cl_cruise"], 1.2)


if __name__ == "__main__":
    unittest.main()
