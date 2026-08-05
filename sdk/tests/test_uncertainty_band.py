"""Band composition: the doctrine's four rules, as behaviour rather than prose."""
from __future__ import annotations

import math
import unittest

from chief_engineer import uncertainty_band as ub


class Composition(unittest.TestCase):
    def test_rss_matches_the_one_function(self):
        band = ub.compose({"input": 0.003, "numerical": 0.004, "model": 0.012},
                          working_value=0.1, quantity="Cd")
        self.assertAlmostEqual(band.combined,
                               math.sqrt(0.003 ** 2 + 0.004 ** 2 + 0.012 ** 2),
                               places=12)
        self.assertTrue(band.complete)
        self.assertEqual(band["largest"]["term"], "model")
        self.assertAlmostEqual(band["combined_95_pct"], 100 * band.combined / 0.1)

    def test_unquantified_is_not_zero(self):
        band = ub.compose({"numerical": 0.0002, "model": 0.220, "input": None},
                          quantity="separation x/c")
        # The NASA hump's worked numbers: the total is the two channels that
        # carry a figure, and the third is absent from the sum, not zero in it.
        self.assertAlmostEqual(band.combined,
                               math.sqrt(0.0002 ** 2 + 0.220 ** 2), places=12)
        self.assertEqual(band["missing"], ["input"])
        self.assertFalse(band.complete)
        self.assertIn("unquantified", band["coverage_statement"])
        self.assertNotIn("input", band["contributions"])

    def test_a_record_with_no_figure_is_unquantified_not_an_error(self):
        band = ub.compose({"numerical": {"method": "study pending"},
                           "model": 0.5})
        self.assertEqual(band["missing"], ["input", "numerical"])
        self.assertEqual(band.combined, 0.5)

    def test_band_rel_uses_the_working_value(self):
        band = ub.compose({"model": {"band_rel": 0.05, "method": "transferred"}},
                          working_value=0.4)
        self.assertAlmostEqual(band.combined, 0.02, places=12)

    def test_shared_evaluation_is_withheld_with_its_reason(self):
        # The valve case: the numerical channel is the same arithmetic on the
        # same waveform as a member of the model channel's family.
        band = ub.compose({
            "model": 40.0,
            "numerical": {"band_abs": 1252.8, "independent_of_numerical": False,
                          "shared_evaluation": "is the same arithmetic on the "
                                               "same waveform as the cd = 0.62 "
                                               "correlation member"},
        }, quantity="pressure drop")
        self.assertEqual(band.combined, 40.0)
        self.assertIn("numerical", band["withheld"])
        self.assertIn("same waveform", band["coverage_statement"])
        self.assertNotIn("numerical", band["contributions"])

    def test_nothing_is_quantified(self):
        band = ub.compose({"input": None, "numerical": None, "model": None})
        self.assertIsNone(band.combined)
        self.assertIsNone(band["largest"])
        self.assertIn("no total", band["coverage_statement"])

    def test_unknown_channel_is_refused(self):
        with self.assertRaises(ValueError):
            ub.compose({"turbulence": 0.1})


class CoefficientInterval(unittest.TestCase):
    def test_carried_alongside_never_inside(self):
        interval = ub.coefficient_interval(low=0.00264, high=0.00314,
                                           working=0.002834, n_samples=42,
                                           citations=["Schaefer et al. 2017"])
        band = ub.compose({"numerical": 0.00002, "model": 0.00010},
                          working_value=0.002834,
                          coefficient_band=interval, quantity="Cd")
        # The interval is several times the combined band and still stays out of it.
        self.assertGreater(interval["width"], 4 * band.combined)
        self.assertAlmostEqual(band.combined,
                               math.sqrt(0.00002 ** 2 + 0.00010 ** 2), places=12)
        self.assertFalse(band["coefficient_interval"]["in_quadrature"])
        self.assertTrue(band["coefficient_interval"]["working_inside"])
        self.assertNotIn("coefficient", " ".join(band["contributions"]))

    def test_inverted_interval_is_refused(self):
        with self.assertRaises(ValueError):
            ub.coefficient_interval(low=1.0, high=0.5)

    def test_width_percentage_is_of_the_working_value(self):
        interval = ub.coefficient_interval(low=0.9, high=1.1, working=1.0)
        self.assertAlmostEqual(interval["width_pct_of_working"], 20.0, places=9)


class ChannelTable(unittest.TestCase):
    def test_every_channel_gets_a_row_in_a_fixed_order(self):
        band = ub.compose({
            "model": 0.01,
            "numerical": {"band_abs": 0.5, "independent_of_numerical": False},
        })
        rows = ub.as_channel_table(band)
        self.assertEqual([r["channel"] for r in rows],
                         ["input", "numerical", "model"])
        state = {r["channel"]: r["state"] for r in rows}
        self.assertEqual(state, {"input": "unquantified",
                                 "numerical": "withheld",
                                 "model": "quantified"})

    def test_no_term_in_the_total_is_absent_from_the_table(self):
        band = ub.compose({"input": 0.1, "numerical": 0.2, "model": 0.3})
        shown = {r["channel"] for r in ub.as_channel_table(band)
                 if r["state"] == "quantified"}
        self.assertEqual(shown, set(band["contributions"]))

    def test_screening_estimates_stay_labelled_through_composition(self):
        band = ub.compose({"model": {"band_abs": 0.02,
                                     "method": "inter-closure spread",
                                     "screening_estimate": True}})
        row = [r for r in ub.as_channel_table(band) if r["channel"] == "model"][0]
        self.assertTrue(row["screening_estimate"])
        self.assertEqual(row["method"], "inter-closure spread")


if __name__ == "__main__":
    unittest.main()
