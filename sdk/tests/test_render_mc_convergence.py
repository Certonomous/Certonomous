"""Pure-function coverage for the Monte-Carlo convergence panel script.

The script's estimator arithmetic (the act's 95 percent band, per-sample
peaks, the sequential resampled band, the power-law slope fit, the guarantee
line, the run-count staircase, and the reduced-order surface residual) is
exercised on synthetic data with known answers. No solver output, no reads
of the recorded mission artifacts, no rendering.
"""
from __future__ import annotations

import importlib.util
import math
import statistics
import unittest
from pathlib import Path

import numpy as np

SDK = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location(
        "render_mc_convergence",
        SDK / "scripts" / "render_mc_convergence.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mcc = _load()


class HalfWidthTests(unittest.TestCase):
    def test_matches_two_standard_errors(self):
        values = [1.0, 2.0, 3.0, 4.0]
        expected = 2.0 * statistics.stdev(values) / 2.0
        self.assertAlmostEqual(mcc.half_width_95(values), expected)

    def test_known_pair(self):
        # stdev of (0, 2) is sqrt(2), so 2 * sqrt(2) / sqrt(2) = 2 exactly.
        self.assertAlmostEqual(mcc.half_width_95([0.0, 2.0]), 2.0)

    def test_below_two_values_is_none(self):
        self.assertIsNone(mcc.half_width_95([1.0]))
        self.assertIsNone(mcc.half_width_95([]))


class SamplePeaksTests(unittest.TestCase):
    def test_peak_per_sample_in_sample_order(self):
        points = [
            {"sample": 1, "l_d": 5.0}, {"sample": 0, "l_d": 2.0},
            {"sample": 0, "l_d": 3.0}, {"sample": 1, "l_d": 4.0},
        ]
        self.assertEqual(mcc.sample_peaks(points), [3.0, 5.0])

    def test_single_point_samples(self):
        points = [{"sample": 0, "l_d": 1.5}, {"sample": 1, "l_d": 0.5}]
        self.assertEqual(mcc.sample_peaks(points), [1.5, 0.5])


class SequentialBandTests(unittest.TestCase):
    def test_full_ensemble_is_ordering_free(self):
        peaks = [10.0, 11.0, 9.5, 10.4, 10.8, 9.9, 10.1, 10.6]
        per = mcc.sequential_band_stats(peaks, orderings=50, seed=1)
        expected = mcc.half_width_95(peaks)
        final = per[len(peaks)]
        for key in ("rms", "median", "q25", "q75"):
            self.assertAlmostEqual(final[key], expected, places=12)

    def test_rms_tracks_one_over_sqrt_m(self):
        # The prefix sample variance is unbiased for the full-ensemble
        # variance under sampling without replacement, so the root mean
        # square curve must sit on 2 * stdev / sqrt(m) for every m.
        rng = np.random.default_rng(7)
        peaks = list(rng.normal(18.0, 0.2, size=8))
        sd = statistics.stdev(peaks)
        per = mcc.sequential_band_stats(peaks, orderings=60000, seed=3)
        for m, stats_m in per.items():
            self.assertAlmostEqual(stats_m["rms"], 2.0 * sd / math.sqrt(m),
                                   delta=0.012)

    def test_quartiles_bracket_median(self):
        peaks = [1.0, 2.0, 3.0, 4.0, 5.0]
        per = mcc.sequential_band_stats(peaks, orderings=500, seed=2)
        for stats_m in per.values():
            self.assertLessEqual(stats_m["q25"], stats_m["median"])
            self.assertLessEqual(stats_m["median"], stats_m["q75"])

    def test_rejects_below_two_members(self):
        with self.assertRaises(ValueError):
            mcc.sequential_band_stats([1.0])


class GuaranteeTests(unittest.TestCase):
    def test_anchored_at_the_full_run_count(self):
        # At N = members * runs-per-member the guarantee equals the act's
        # band statistic 2 * sd / sqrt(members).
        sd, members = 0.136, 8
        value = mcc.guarantee_half_width(sd, members * 11, runs_per_member=11)
        self.assertAlmostEqual(float(value), 2.0 * sd / math.sqrt(members))

    def test_exact_half_power(self):
        one = float(mcc.guarantee_half_width(0.2, 10.0, runs_per_member=5))
        four = float(mcc.guarantee_half_width(0.2, 40.0, runs_per_member=5))
        self.assertAlmostEqual(one / four, 2.0)


class BandAtRunsTests(unittest.TestCase):
    PER = {2: {"rms": 0.2}, 3: {"rms": 0.15}, 8: {"rms": 0.1}}

    def test_pending_below_two_members(self):
        self.assertEqual(mcc.band_at_runs(21, self.PER), (1, None))
        self.assertEqual(mcc.band_at_runs(2, self.PER), (0, None))

    def test_updates_on_member_boundaries(self):
        self.assertEqual(mcc.band_at_runs(22, self.PER), (2, 0.2))
        self.assertEqual(mcc.band_at_runs(32, self.PER), (2, 0.2))
        self.assertEqual(mcc.band_at_runs(33, self.PER), (3, 0.15))
        self.assertEqual(mcc.band_at_runs(88, self.PER), (8, 0.1))


class SlopeFitTests(unittest.TestCase):
    def test_recovers_exact_power_law(self):
        ns = [22, 33, 44, 55, 66, 77, 88]
        ys = [3.0 * n ** -0.5 for n in ns]
        self.assertAlmostEqual(mcc.fit_powerlaw_slope(ns, ys), -0.5, places=10)

    def test_flat_data_gives_zero(self):
        self.assertAlmostEqual(
            mcc.fit_powerlaw_slope([10, 20, 40], [2.0, 2.0, 2.0]), 0.0,
            places=10)


class QuadraticPeakResidualTests(unittest.TestCase):
    def test_zero_residual_on_the_surface(self):
        f = lambda x: -0.5 * (x - 4.0) ** 2 + 18.0        # noqa: E731
        xs = [0.0, 3.0, 7.0, 10.0]
        out = mcc.quadratic_peak_residual(
            xs, [f(x) for x in xs], f(4.0), x_lo=0.0, x_hi=10.0)
        self.assertAlmostEqual(out["alpha_star"], 4.0)
        self.assertAlmostEqual(out["residual"], 0.0, places=9)

    def test_residual_is_confirmation_minus_prediction(self):
        f = lambda x: -1.0 * (x - 5.0) ** 2 + 10.0        # noqa: E731
        xs = [2.0, 4.0, 6.0, 8.0]
        out = mcc.quadratic_peak_residual(
            xs, [f(x) for x in xs], f(5.0) - 0.25, x_lo=0.0, x_hi=10.0)
        self.assertAlmostEqual(out["residual"], 0.25, places=9)

    def test_convex_fit_falls_back_to_the_higher_end(self):
        f = lambda x: (x - 5.0) ** 2                       # noqa: E731
        xs = [0.0, 3.0, 7.0, 10.0]
        out = mcc.quadratic_peak_residual(
            xs, [f(x) for x in xs], f(0.0), x_lo=0.0, x_hi=10.0)
        # Both ends predict equally; the low end wins ties, as in the act.
        self.assertAlmostEqual(out["alpha_star"], 0.0)
        self.assertAlmostEqual(out["residual"], 0.0, places=9)

    def test_vertex_clamped_and_rounded_to_the_grid(self):
        f = lambda x: -0.3 * (x - 12.0) ** 2 + 20.0        # noqa: E731
        xs = [0.0, 3.3, 6.7, 10.0]
        out = mcc.quadratic_peak_residual(
            xs, [f(x) for x in xs], f(10.0), x_lo=0.0, x_hi=10.0)
        self.assertAlmostEqual(out["alpha_star"], 10.0)
        self.assertAlmostEqual(out["residual"], 0.0, places=9)


if __name__ == "__main__":
    unittest.main()
