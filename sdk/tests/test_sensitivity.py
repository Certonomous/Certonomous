"""Sobol sensitivity primitive: estimator truth, identities, determinism."""
from __future__ import annotations

import math
import random
import unittest

from chief_engineer import sensitivity as sb


class IshigamiTruth(unittest.TestCase):
    """The estimator must recover the closed-form benchmark before it is
    trusted on any lab model (the Innovation Standard's evidence posture)."""

    @classmethod
    def setUpClass(cls):
        cls.result = sb.sobol_indices(sb.ishigami_model, sb.ishigami_dists(),
                                      n_base=2048, seed=11)
        cls.truth = sb.ishigami_true_indices()

    def test_main_indices_near_closed_form(self):
        for est, true in zip(self.result.main, self.truth["main"]):
            self.assertAlmostEqual(est, true, delta=0.06)

    def test_total_indices_near_closed_form(self):
        for est, true in zip(self.result.total, self.truth["total"]):
            self.assertAlmostEqual(est, true, delta=0.06)

    def test_x3_has_no_main_effect_but_a_real_total(self):
        # The signature Ishigami structure: x3 acts only through interaction.
        self.assertAlmostEqual(self.result.main[2], 0.0, delta=0.05)
        self.assertGreater(self.result.total[2], 0.15)

    def test_identities_hold_within_ci(self):
        self.assertTrue(all(self.result.identity_report().values()))


class KnownLinearModel(unittest.TestCase):
    """f = 2*x1 + x2 with unit-normal inputs: shares are exactly 4/5, 1/5."""

    @classmethod
    def setUpClass(cls):
        dists = {"x1": sb.normal_input(0, 1), "x2": sb.normal_input(0, 1)}
        cls.result = sb.sobol_indices(lambda a, b: 2 * a + b, dists,
                                      n_base=4096, seed=3)

    def test_variance_shares(self):
        self.assertAlmostEqual(self.result.main[0], 0.8, delta=0.05)
        self.assertAlmostEqual(self.result.main[1], 0.2, delta=0.05)

    def test_additive_model_totals_equal_mains(self):
        for m, t in zip(self.result.main, self.result.total):
            self.assertAlmostEqual(m, t, delta=0.05)

    def test_mapping_names_carried(self):
        self.assertEqual(self.result.names, ("x1", "x2"))

    def test_ranking_orders_by_main(self):
        self.assertEqual([r[0] for r in self.result.ranking()], ["x1", "x2"])

    def test_large_offset_does_not_destroy_the_estimate(self):
        # Regression: a raw output whose mean dwarfs its spread (the valve
        # loss in Pa) must not drown the main indices in product noise —
        # the estimator centers on the pooled mean.
        dists = {"x1": sb.normal_input(0, 1), "x2": sb.normal_input(0, 1)}
        shifted = sb.sobol_indices(lambda a, b: 1.0e6 + 2 * a + b, dists,
                                   n_base=4096, seed=3)
        self.assertAlmostEqual(shifted.main[0], 0.8, delta=0.05)
        self.assertAlmostEqual(shifted.main[1], 0.2, delta=0.05)


class Determinism(unittest.TestCase):
    def _run(self, seed: int) -> sb.SobolIndices:
        return sb.sobol_indices(sb.ishigami_model, sb.ishigami_dists(),
                                n_base=128, seed=seed, bootstrap=50)

    def test_same_seed_same_numbers_to_the_last_digit(self):
        a, b = self._run(7), self._run(7)
        self.assertEqual(a.main, b.main)
        self.assertEqual(a.total, b.total)
        self.assertEqual(a.main_ci, b.main_ci)
        self.assertEqual(a.total_ci, b.total_ci)

    def test_different_seed_different_draws(self):
        self.assertNotEqual(self._run(7).main, self._run(8).main)


class CostAndContract(unittest.TestCase):
    def test_cost_is_exactly_n_base_times_m_plus_2(self):
        calls = []
        dists = [sb.uniform_input(0, 1)] * 3

        def counted(a, b, c):
            calls.append(1)
            return a + b * c

        result = sb.sobol_indices(counted, dists, n_base=64, seed=1,
                                  bootstrap=10)
        self.assertEqual(len(calls), 64 * (3 + 2))
        self.assertEqual(result.n_evaluations, 64 * 5)

    def test_constant_model_refused(self):
        with self.assertRaises(ValueError):
            sb.sobol_indices(lambda a: 4.0, [sb.uniform_input(0, 1)],
                             n_base=32, seed=1)

    def test_empty_dists_refused(self):
        with self.assertRaises(ValueError):
            sb.sobol_indices(lambda: 1.0, [], n_base=32, seed=1)

    def test_ci_brackets_are_ordered_and_near_the_point(self):
        result = sb.sobol_indices(sb.ishigami_model, sb.ishigami_dists(),
                                  n_base=512, seed=5)
        for point, (lo, hi) in zip(result.main, result.main_ci):
            self.assertLessEqual(lo, hi)
            self.assertLessEqual(lo - 0.1, point)
            self.assertGreaterEqual(hi + 0.1, point)


class InputDistributions(unittest.TestCase):
    def test_uniform_sigma_input_matches_its_stated_sigma(self):
        # The valve-envelope convention: bounded uniform whose 1-sigma equals
        # the stated fractional spread.
        rng = random.Random(2)
        sampler = sb.uniform_sigma_input(1.0, 0.06)
        draws = [sampler(rng) for _ in range(20000)]
        mean = sum(draws) / len(draws)
        sigma = math.sqrt(sum((d - mean) ** 2 for d in draws) / len(draws))
        self.assertAlmostEqual(mean, 1.0, delta=0.005)
        self.assertAlmostEqual(sigma, 0.06, delta=0.003)
        self.assertLessEqual(max(draws), 1.0 + 0.06 * math.sqrt(3))
        self.assertGreaterEqual(min(draws), 1.0 - 0.06 * math.sqrt(3))


if __name__ == "__main__":
    unittest.main()
