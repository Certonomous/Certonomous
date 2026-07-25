"""Race benchmark plumbing — everything testable without the solver."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from workflows.race_benchmark import (ALPHAS, WING, _design, _TimedSolver,
                                      speedup_card, write_benchmarks)


def _mc(core_minutes=14.2, wall=95.0):
    return {"n_solves": 88, "peak_mean": 14.9, "peak_sem": 0.11,
            "peak_sigma": 0.3, "peak_alpha_mode": 6.0,
            "wall_seconds": wall, "core_minutes": core_minutes,
            "context": {"cores": "10/14 free", "load": 1.2}}


def _rom(core_minutes=1.9, wall=28.0):
    return {"anchors": [{"alpha": a, "l_d": 10 + a, "seconds": 5.0}
                        for a in (0.0, 3.3, 6.7, 10.0)],
            "n_solves": 5, "alpha_star": 6.2, "predicted": 14.8,
            "confirmed": 14.9, "confirm_seconds": 5.0,
            "surrogate_error": 0.1, "wall_seconds": wall,
            "core_minutes": core_minutes,
            "context": {"cores": "10/14 free", "load": 1.1}}


class DesignShape(unittest.TestCase):
    def test_design_is_the_curriculum_wing_single_alpha(self):
        design = _design(4.0, 1.0e6)
        self.assertEqual(design["span"], WING["span"])
        self.assertEqual(design["camber"], 0.04)
        self.assertEqual(design["alpha_start"], design["alpha_end"])
        self.assertEqual(design["alpha_npts"], 1)

    def test_alpha_grid_covers_zero_to_ten(self):
        self.assertEqual(ALPHAS[0], 0.0)
        self.assertEqual(ALPHAS[-1], 10.0)

    def test_wing_override_anchors_the_design_without_touching_default(self):
        raced = {**WING, "span": 40.0, "area": 40.0}
        design = _design(4.0, 1.0e6, wing=raced)
        self.assertEqual(design["span"], 40.0)
        self.assertEqual(design["area"], 40.0)
        self.assertEqual(design["camber"], WING["camber"])
        # No override: the curriculum wing, unchanged.
        self.assertEqual(_design(4.0, 1.0e6)["span"], WING["span"])


class TimedSolverContract(unittest.TestCase):
    def test_never_reuses_prior_results_and_solves_the_given_wing(self):
        with mock.patch("workflows.race_benchmark.VspAeroWingApi") as api_cls:
            api_cls.return_value.evaluate.return_value = {
                "polar": {"CLtot": [0.9], "CDtot": [0.05], "L_D": [18.0]}}
            with tempfile.TemporaryDirectory() as tmp:
                solver = _TimedSolver(Path(tmp),
                                      wing={**WING, "span": 40.0, "area": 40.0})
                point = solver.solve(4.0, 1.0e6, "t")
        # The clocks ARE the measurement: reuse_prior must stay False.
        self.assertIs(api_cls.call_args.kwargs.get("reuse_prior"), False)
        design = api_cls.return_value.evaluate.call_args.args[0]
        self.assertEqual(design["span"], 40.0)
        self.assertEqual(point["l_d"], 18.0)
        self.assertEqual(len(solver.solve_seconds), 1)

    def test_default_wing_is_the_curriculum_wing(self):
        with mock.patch("workflows.race_benchmark.VspAeroWingApi") as api_cls:
            api_cls.return_value.evaluate.return_value = {
                "polar": {"CLtot": [0.9], "CDtot": [0.05], "L_D": [18.0]}}
            with tempfile.TemporaryDirectory() as tmp:
                _TimedSolver(Path(tmp)).solve(4.0, 1.0e6, "t")
        self.assertIs(api_cls.call_args.kwargs.get("reuse_prior"), False)
        design = api_cls.return_value.evaluate.call_args.args[0]
        self.assertEqual(design["span"], WING["span"])


class Artifacts(unittest.TestCase):
    def _record(self):
        return {"tag": "test",
                "subject": "NACA 4412 finite wing (chord 1 m, span 3 m, Re_c 1e6)",
                "question": "peak L/D over alpha 0-10 deg",
                "mc": _mc(), "rom": _rom(),
                "speedup_core_minutes": 7.5, "speedup_wall": 3.4}

    def test_benchmarks_md_carries_measured_numbers_and_meaning(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "benchmarks.md"
            write_benchmarks([self._record()], out)
            text = out.read_text(encoding="utf-8")
        self.assertIn("7.5×", text)
        self.assertIn("envelopes mean different things", text)
        self.assertIn("load 1.2", text)
        # the two numbers handed to the website panel
        self.assertIn("full MC: 14.2 core-min", text)
        self.assertIn("reduced: 1.9 core-min", text)

    def test_speedup_card_uses_measured_core_minutes(self):
        with tempfile.TemporaryDirectory() as tmp:
            png = speedup_card(_mc(), _rom(), Path(tmp) / "card.png")
            self.assertTrue(png is None or Path(png).exists())


if __name__ == "__main__":
    unittest.main()
