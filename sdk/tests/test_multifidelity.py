"""MFMC math: correlation, allocation, variance ratio, fused estimator."""
from __future__ import annotations

import math
import random
import statistics
import unittest

from chief_engineer import multifidelity as mf


class Correlation(unittest.TestCase):
    def test_affine_lanes_are_perfectly_correlated(self):
        hi = [1.0, 2.0, 3.0, 4.0]
        lo = [2 * v + 1 for v in hi]
        self.assertAlmostEqual(mf.pearson(hi, lo), 1.0, places=12)

    def test_anticorrelation_signed(self):
        hi = [1.0, 2.0, 3.0]
        self.assertAlmostEqual(mf.pearson(hi, [-v for v in hi]), -1.0,
                               places=12)

    def test_constant_lane_refused_not_zeroed(self):
        # Pretending rho = 0 would hide a broken pairing (the race's
        # fixed-alpha estimand is exactly this degenerate case).
        with self.assertRaises(ValueError):
            mf.pearson([1.0, 2.0, 3.0], [5.0, 5.0, 5.0])

    def test_length_mismatch_refused(self):
        with self.assertRaises(ValueError):
            mf.pearson([1.0, 2.0], [1.0])

    def test_alpha_recovers_the_affine_slope(self):
        lo = [1.0, 2.0, 3.0, 4.0]
        hi = [2 * v + 7 for v in lo]
        self.assertAlmostEqual(mf.control_variate_alpha(hi, lo), 2.0,
                               places=12)


class VarianceRatio(unittest.TestCase):
    def test_uncorrelated_surrogate_buys_nothing(self):
        self.assertAlmostEqual(mf.variance_ratio(0.0, 10.0, 1.0), 1.0,
                               places=12)

    def test_hand_computed_value(self):
        # rho = 0.9, w = 100: (sqrt(1-0.81) + sqrt(0.81/100))^2
        expected = (math.sqrt(0.19) + math.sqrt(0.0081)) ** 2
        self.assertAlmostEqual(mf.variance_ratio(0.9, 100.0, 1.0), expected,
                               places=12)

    def test_free_surrogate_floor_is_one_minus_rho_squared(self):
        self.assertAlmostEqual(mf.variance_ratio(0.99, 1e9, 1e-3),
                               1 - 0.99 ** 2, delta=1e-4)

    def test_bad_costs_refused(self):
        with self.assertRaises(ValueError):
            mf.variance_ratio(0.5, 1.0, 2.0)     # cheap lane dearer
        with self.assertRaises(ValueError):
            mf.variance_ratio(0.5, 1.0, 0.0)

    def test_pays_condition(self):
        # Survey admissibility: cost_lo/cost_hi < rho^2/(1-rho^2).
        self.assertTrue(mf.mfmc_pays(0.99, 1000.0, 1.0))
        self.assertFalse(mf.mfmc_pays(0.1, 1.0, 1.0))


class Allocation(unittest.TestCase):
    def test_optimal_ratio_formula(self):
        plan = mf.optimal_allocation(0.9, 100.0, 1.0, budget=10_000.0)
        expected_r = math.sqrt(0.81 / 0.19 * 100.0)
        self.assertAlmostEqual(plan.r_optimal, expected_r, places=9)
        self.assertGreaterEqual(plan.n_lo, plan.n_hi)
        self.assertLessEqual(plan.spent(), 10_000.0 + 100.0 + 1.0)
        self.assertTrue(plan.pays)
        self.assertAlmostEqual(plan.speedup_equal_error,
                               1.0 / plan.variance_ratio, places=9)

    def test_high_fidelity_stays_in_the_loop(self):
        # A budget too small for one solve is refused, never silently
        # answered surrogate-only.
        with self.assertRaises(ValueError):
            mf.optimal_allocation(0.9, 100.0, 1.0, budget=50.0)

    def test_perfect_correlation_refused(self):
        with self.assertRaises(ValueError):
            mf.optimal_allocation(1.0, 100.0, 1.0, budget=1000.0)


class FusedEstimator(unittest.TestCase):
    def test_no_extra_surrogate_reduces_to_plain_mean(self):
        hi = [3.0, 5.0, 7.0]
        lo = [2.9, 5.2, 6.8]
        fused = mf.mfmc_estimate(hi, lo, [], alpha=1.0)
        self.assertAlmostEqual(fused["estimate"], statistics.fmean(hi),
                               places=12)

    def test_shift_direction_and_bookkeeping(self):
        hi = [10.0, 12.0]
        lo = [1.0, 2.0]
        fused = mf.mfmc_estimate(hi, lo, [3.0, 4.0], alpha=2.0)
        # lo_all mean 2.5, lo_paired mean 1.5 -> shift +2.0 on hi mean 11.
        self.assertAlmostEqual(fused["estimate"], 13.0, places=12)
        self.assertEqual(fused["n_hi"], 2)
        self.assertEqual(fused["n_lo"], 4)

    def test_too_few_pairs_refused(self):
        with self.assertRaises(ValueError):
            mf.mfmc_estimate([1.0], [1.0], [])

    def test_fusion_beats_plain_mc_on_correlated_synthetic_lanes(self):
        # The whole point, demonstrated end to end: correlated lanes, a
        # small solve budget, many replays — the fused estimator's RMSE
        # must undercut same-budget MC, near the analytic ratio.
        rng = random.Random(42)
        population = []
        for _ in range(4000):
            base = rng.gauss(10.0, 2.0)
            population.append((base + rng.gauss(0.0, 0.4), base))  # (hi, lo)
        hi_all = [p[0] for p in population]
        lo_all = [p[1] for p in population]
        truth = statistics.fmean(hi_all)
        rho = mf.pearson(hi_all, lo_all)
        alpha = mf.control_variate_alpha(hi_all, lo_all)
        n = 12
        mc_err, mfmc_err = [], []
        for _ in range(600):
            rows = [rng.randrange(len(population)) for _ in range(n)]
            hi = [hi_all[r] for r in rows]
            lo = [lo_all[r] for r in rows]
            mc_err.append(statistics.fmean(hi) - truth)
            fused = mf.mfmc_estimate(hi, lo, lo_all, alpha=alpha)
            mfmc_err.append(fused["estimate"] - truth)
        var_mc = statistics.fmean(e * e for e in mc_err)
        var_mf = statistics.fmean(e * e for e in mfmc_err)
        self.assertLess(var_mf, var_mc)
        # With an effectively free surrogate the floor is 1 - rho^2; allow
        # generous replay slack either side.
        self.assertLess(var_mf / var_mc, 3.0 * (1.0 - rho * rho) + 0.05)


if __name__ == "__main__":
    unittest.main()
