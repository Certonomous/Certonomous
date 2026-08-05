"""Chaos expansion and process surrogate, checked against answers known in closed form."""
from __future__ import annotations

import math
import unittest

import numpy as np

from chief_engineer import pce_surrogate as ps


def ishigami(x: np.ndarray, a: float = 7.0, b: float = 0.1) -> np.ndarray:
    x = np.atleast_2d(x)
    return (np.sin(x[:, 0]) + a * np.sin(x[:, 1]) ** 2
            + b * x[:, 2] ** 4 * np.sin(x[:, 0]))


class Basis(unittest.TestCase):
    def test_multi_index_count_is_the_textbook_one(self):
        for dim, order in ((5, 2), (3, 3), (2, 4)):
            expected = math.comb(dim + order, order)
            self.assertEqual(len(ps.multi_indices(dim, order)), expected)

    def test_first_index_is_the_constant_term(self):
        self.assertEqual(ps.multi_indices(4, 2)[0], (0, 0, 0, 0))

    def test_legendre_products_are_orthonormal_under_the_uniform_measure(self):
        rng = np.random.default_rng(3)
        x = rng.uniform(-1.0, 3.0, size=(200000, 2))
        indices = ps.multi_indices(2, 2)
        design = ps.legendre_design(x, [-1.0, -1.0], [3.0, 3.0], indices)
        gram = design.T @ design / len(x)
        np.testing.assert_allclose(gram, np.eye(len(indices)), atol=0.02)


class ChaosExpansion(unittest.TestCase):
    def test_a_quadratic_response_is_recovered_exactly(self):
        rng = np.random.default_rng(7)
        x = rng.uniform([0.0, 2.0], [1.0, 5.0], size=(60, 2))
        y = 3.0 + 2.0 * x[:, 0] - 0.5 * x[:, 1] + 4.0 * x[:, 0] * x[:, 1]
        fit = ps.fit_pce(x, y, lower=[0.0, 2.0], upper=[1.0, 5.0],
                         names=["a", "b"], order=2)
        self.assertLess(fit.fit_rmse, 1e-10)
        self.assertGreater(fit.loo_q2, 1.0 - 1e-8)
        np.testing.assert_allclose(fit.predict(x), y, atol=1e-9)

    def test_analytic_mean_and_variance_of_a_linear_response(self):
        # y = 1 + 2u over u ~ U[0,1]: mean 2, variance 4/12.
        u = np.linspace(0.0, 1.0, 40)[:, None]
        fit = ps.fit_pce(u, 1.0 + 2.0 * u.ravel(), lower=[0.0], upper=[1.0],
                         names=["u"], order=1)
        self.assertAlmostEqual(fit.mean, 2.0, places=6)
        self.assertAlmostEqual(fit.variance, 4.0 / 12.0, places=6)

    def test_sobol_indices_recover_the_ishigami_shares(self):
        rng = np.random.default_rng(11)
        lo, hi = [-math.pi] * 3, [math.pi] * 3
        x = rng.uniform(lo, hi, size=(900, 3))
        fit = ps.fit_pce(x, ishigami(x), lower=lo, upper=hi,
                         names=["x1", "x2", "x3"], order=8)
        a, b = 7.0, 0.1
        var = a ** 2 / 8 + b * math.pi ** 4 / 5 + b ** 2 * math.pi ** 8 / 18 + 0.5
        v1 = 0.5 * (1 + b * math.pi ** 4 / 5) ** 2
        v2 = a ** 2 / 8
        self.assertAlmostEqual(fit.sobol_first["x1"], v1 / var, places=2)
        self.assertAlmostEqual(fit.sobol_first["x2"], v2 / var, places=2)
        # x3 acts only through its interaction with x1: no main effect, real total.
        self.assertLess(fit.sobol_first["x3"], 0.01)
        self.assertGreater(fit.sobol_total["x3"], 0.15)

    def test_shares_sum_sensibly(self):
        rng = np.random.default_rng(5)
        x = rng.uniform(0.0, 1.0, size=(80, 3))
        y = x[:, 0] + 2 * x[:, 1] + 0.3 * x[:, 0] * x[:, 2]
        fit = ps.fit_pce(x, y, lower=[0.0] * 3, upper=[1.0] * 3,
                         names=list("abc"), order=2)
        self.assertLessEqual(sum(fit.sobol_first.values()), 1.0 + 1e-9)
        for name in "abc":
            self.assertGreaterEqual(fit.sobol_total[name] + 1e-12,
                                    fit.sobol_first[name])

    def test_underdetermined_fit_is_refused_not_least_normed(self):
        rng = np.random.default_rng(2)
        x = rng.uniform(0.0, 1.0, size=(10, 5))          # 21 terms, 10 samples
        with self.assertRaises(ValueError) as caught:
            ps.fit_pce(x, rng.normal(size=10), lower=[0.0] * 5, upper=[1.0] * 5,
                       names=list("abcde"), order=2)
        self.assertIn("21 terms", str(caught.exception))

    def test_a_response_the_basis_cannot_reach_says_so(self):
        x = np.linspace(0.0, 1.0, 30)[:, None]
        y = np.sign(x.ravel() - 0.5)                      # a step: order 1 cannot
        fit = ps.fit_pce(x, y, lower=[0.0], upper=[1.0], names=["u"], order=1)
        self.assertLess(fit.loo_q2, 0.9)
        self.assertTrue(fit.notes)
        self.assertIn("leave-one-out", fit.notes[0])


class GaussianProcess(unittest.TestCase):
    def test_it_interpolates_a_smooth_response_it_has_seen(self):
        rng = np.random.default_rng(1)
        x = rng.uniform(0.0, 1.0, size=(40, 2))
        y = np.sin(3 * x[:, 0]) + 0.5 * x[:, 1] ** 2
        fit = ps.fit_gp(x, y, lower=[0.0, 0.0], upper=[1.0, 1.0],
                        names=["a", "b"], seed=1)
        np.testing.assert_allclose(fit.predict(x), y, atol=5e-3)
        self.assertGreater(fit.loo_q2, 0.95)

    def test_posterior_spread_grows_away_from_the_evidence(self):
        x = np.linspace(0.0, 0.4, 25)[:, None]
        fit = ps.fit_gp(x, np.sin(6 * x.ravel()), lower=[0.0], upper=[1.0],
                        names=["u"], seed=2)
        _, near = fit.predict(np.array([[0.2]]), with_std=True)
        _, far = fit.predict(np.array([[1.0]]), with_std=True)
        self.assertGreater(far[0], 5 * near[0])

    def test_an_irrelevant_input_gets_a_long_lengthscale(self):
        rng = np.random.default_rng(4)
        x = rng.uniform(0.0, 1.0, size=(50, 2))
        fit = ps.fit_gp(x, np.sin(4 * x[:, 0]), lower=[0.0, 0.0],
                        upper=[1.0, 1.0], names=["used", "ignored"], seed=3)
        scales = fit.as_dict()["lengthscales_unit_box"]
        self.assertGreater(scales["ignored"], 3 * scales["used"])


class BandReading(unittest.TestCase):
    def test_both_readings_are_returned_together(self):
        band = ps.band_from_samples([1.0, 2.0, 3.0, 4.0, 5.0], reference=3.0)
        self.assertEqual((band["min"], band["max"]), (1.0, 5.0))
        self.assertEqual(band["envelope_width"], 4.0)
        self.assertIn("percentile_5", band)
        self.assertIn("std", band)
        self.assertTrue(band["reference_inside_envelope"])
        self.assertAlmostEqual(band["envelope_pct_of_reference"], 400.0 / 3.0)

    def test_the_envelope_never_narrower_than_the_central_span(self):
        rng = np.random.default_rng(6)
        band = ps.band_from_samples(rng.normal(size=200))
        self.assertGreaterEqual(band["envelope_width"], band["central_90_width"])

    def test_one_sample_is_not_a_band(self):
        with self.assertRaises(ValueError):
            ps.band_from_samples([1.0])


if __name__ == "__main__":
    unittest.main()
