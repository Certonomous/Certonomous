"""The VSPAERO adapter seam — everything testable without the solver installed."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
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


def _complete_result(cl: float = 0.47) -> dict:
    """A result.json with everything the workflow consumes, as the current
    worker schema writes it."""
    return {
        "built": {"span": 64.0, "area": 240.0},
        "polar": {
            "Alpha": [0.0, 2.0, 4.0, 6.0, 8.0],
            "CLtot": [0.10, 0.30, 0.50, 0.70, 0.90],
            "CDi": [0.001, 0.002, 0.003, 0.005, 0.008],
            "CDo": [0.0055, 0.0055, 0.0054, 0.0056, 0.0058],
            "CDtot": [0.0065, 0.0075, 0.0084, 0.0106, 0.0138],
            "L_D": [15.0, 40.0, 60.0, 66.0, 65.0],
            "E": [0.8, 0.8, 0.8, 0.8, 0.8],
        },
        "matched": {"alpha": 3.9, "cl": cl, "cdi": 0.0023,
                    "cdo_wing": 0.0055, "span_efficiency": 0.8,
                    "extrapolated": False},
        "stl": "wing.stl", "solver": "VSPAERO", "solver_version": "3.x",
    }


class StaleResultReuse(unittest.TestCase):
    """The result-reuse path must never return a prior that lacks anything the
    caller consumes — stale files from killed runs or older schemas re-solve."""

    DESIGN = {"span": 64.0, "area": 240.0, "sweep": 25.0, "taper": 0.3,
              "cl_target": 0.47, "re_cref": 2.29e7, "tag_hint": "case-a"}

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="vspaero-reuse-"))
        self.api = vspaero.VspAeroWingApi(self.tmp, run_prefix="")
        self.case = self.tmp / "case-a"
        self.case.mkdir()
        (self.case / "wing.stl").write_text("solid wing\nendsolid wing\n")

    def _write_prior(self, prior: dict) -> None:
        (self.case / "result.json").write_text(json.dumps(prior),
                                               encoding="utf-8")

    def _fresh_solver(self):
        """A stand-in for the worker subprocess: writes a complete result."""
        def run(command, stdout=None, stderr=None, timeout=None, cwd=None):
            (Path(cwd) / "wing.stl").write_text("solid wing\nendsolid wing\n")
            (Path(cwd) / "result.json").write_text(
                json.dumps(_complete_result()), encoding="utf-8")
        return mock.patch("chief_engineer.vspaero.subprocess.run",
                          side_effect=run)

    def test_complete_prior_is_reused_without_a_solve(self):
        self._write_prior(_complete_result())
        with mock.patch("chief_engineer.vspaero.subprocess.run") as run:
            result = self.api.evaluate(self.DESIGN)
        run.assert_not_called()
        self.assertEqual(result["matched"]["cdi"], 0.0023)
        self.assertEqual(result["case_dir"], str(self.case))

    def test_prior_missing_matched_and_polar_is_resolved_fresh(self):
        # The killed-run/older-schema shape that broke the airliner finalists.
        self._write_prior({"built": {"span": 64.0}, "stl": "wing.stl"})
        with self._fresh_solver() as run:
            result = self.api.evaluate(self.DESIGN)
        run.assert_called_once()
        self.assertIn("matched", result)
        self.assertIn("polar", result)

    def test_prior_with_null_matched_is_resolved_fresh(self):
        # A single-point solve writes matched: null — unusable for a cruise match.
        prior = _complete_result()
        prior["matched"] = None
        self._write_prior(prior)
        with self._fresh_solver() as run:
            self.api.evaluate(self.DESIGN)
        run.assert_called_once()

    def test_prior_with_scrubbed_nan_polar_is_resolved_fresh(self):
        # NaNs are scrubbed to null at the source; null cannot be interpolated.
        prior = _complete_result()
        prior["polar"]["CDi"][2] = None
        self._write_prior(prior)
        with self._fresh_solver() as run:
            self.api.evaluate(self.DESIGN)
        run.assert_called_once()

    def test_prior_matched_at_another_cl_target_is_resolved_fresh(self):
        # Same planform, different mission weight: the matched point is wrong.
        self._write_prior(_complete_result(cl=0.61))
        with self._fresh_solver() as run:
            self.api.evaluate(self.DESIGN)
        run.assert_called_once()

    def test_dead_worker_does_not_resurrect_a_stale_result(self):
        # The worker dies before writing: the leftover stale file must not be
        # read back as if this run produced it.
        self._write_prior({"built": {"span": 64.0}, "stl": "wing.stl"})
        with mock.patch("chief_engineer.vspaero.subprocess.run"):
            with self.assertRaises(RuntimeError):
                self.api.evaluate(self.DESIGN)

    def test_cache_can_be_disabled(self):
        self._write_prior(_complete_result())
        with mock.patch.dict(os.environ, {"CERTONOMOUS_SOLVER_CACHE": "0"}):
            with self._fresh_solver() as run:
                self.api.evaluate(self.DESIGN)
        run.assert_called_once()

    # ---- elapsed_s stamping: the measured first-run duration rides along ----

    def test_fresh_solve_stamps_measured_elapsed_into_result_and_file(self):
        with self._fresh_solver() as run:
            result = self.api.evaluate(self.DESIGN)
        run.assert_called_once()
        self.assertIn("elapsed_s", result)
        self.assertGreaterEqual(result["elapsed_s"], 0.0)
        on_disk = json.loads((self.case / "result.json").read_text(encoding="utf-8"))
        self.assertEqual(on_disk["elapsed_s"], result["elapsed_s"])
        # The in-memory reuse marker is never persisted.
        self.assertNotIn("reused_prior", on_disk)

    def test_prior_without_elapsed_s_is_still_reused(self):
        # elapsed_s is optional garnish, not evidence: an older-schema prior
        # that carries everything the caller consumes must still be reused.
        self._write_prior(_complete_result())
        with mock.patch("chief_engineer.vspaero.subprocess.run") as run:
            result = self.api.evaluate(self.DESIGN)
        run.assert_not_called()
        self.assertTrue(result.get("reused_prior"))
        self.assertNotIn("elapsed_s", result)

    def test_reused_prior_returns_its_stamped_first_run_duration(self):
        prior = _complete_result()
        prior["elapsed_s"] = 84.2
        self._write_prior(prior)
        with mock.patch("chief_engineer.vspaero.subprocess.run") as run:
            result = self.api.evaluate(self.DESIGN)
        run.assert_not_called()
        self.assertEqual(result["elapsed_s"], 84.2)
        self.assertTrue(result.get("reused_prior"))


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
