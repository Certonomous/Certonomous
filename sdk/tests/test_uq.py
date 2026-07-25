"""UQ studies: ladder math, spreads, combination, and the honesty rails."""
from __future__ import annotations

import math
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from chief_engineer import uq
from chief_engineer.lab import VALIDATED, trust


class LadderMath(unittest.TestCase):
    def test_clean_second_order_ladder(self):
        # Manufactured phi = 1 + 4 h^2 on an r=2 ladder: p must come back ~2.
        cells = [1000, 8000, 64000]           # h ratio 2 per level
        h = [(1.0 / n) ** (1 / 3) for n in cells]
        values = [1.0 + 4.0 * hh ** 2 for hh in h]
        out = uq.ladder_band(cells, values)
        self.assertTrue(out["conclusive"])
        self.assertAlmostEqual(out["observed_order"], 2.0, places=2)
        # GCI band on the fine mesh: 1.25*|e21|/(r^p-1)
        e21 = abs(values[2] - values[1])
        self.assertAlmostEqual(out["band_abs"], 1.25 * e21 / (2 ** 2 - 1), places=10)
        self.assertIn("observed order p = 2.00", out["method"])

    def test_non_monotone_ladder_says_the_sentence(self):
        out = uq.ladder_band([1000, 8000, 64000], [1.0, 1.2, 1.1])
        self.assertFalse(out["conclusive"])
        self.assertIsNone(out["observed_order"])
        self.assertEqual(out["method"], uq.INCONCLUSIVE)
        # Conservative fallback: factor 3 on the observed range.
        self.assertAlmostEqual(out["band_abs"], 3.0 * 0.2, places=10)

    def test_wild_order_gets_conservative_band(self):
        # Nearly stalled coarse pair -> huge apparent order -> factor-3 band.
        out = uq.ladder_band([1000, 8000, 64000], [1.5, 1.00001, 1.0])
        self.assertFalse(out["conclusive"])
        self.assertGreaterEqual(out["band_abs"], 3.0 * 0.49)


class DegenerateLadder(unittest.TestCase):
    def test_identical_meshes_collapse_to_the_honest_sentence(self):
        out = uq.ladder_band([67826, 67826, 137569],
                             [0.02892, 0.02892, 0.02167])
        self.assertFalse(out["conclusive"])
        self.assertEqual(out["method"], uq.DEGENERATE)
        self.assertAlmostEqual(out["band_abs"], 3.0 * (0.02892 - 0.02167), places=8)

    def test_four_levels_use_last_three_distinct(self):
        cells = [1000, 1000, 8000, 64000]
        h = [(1.0 / n) ** (1 / 3) for n in (1000, 8000, 64000)]
        vals = [1.0 + 4.0 * h[0] ** 2, 1.0 + 4.0 * h[0] ** 2,
                1.0 + 4.0 * h[1] ** 2, 1.0 + 4.0 * h[2] ** 2]
        out = uq.ladder_band(cells, vals)
        self.assertTrue(out["conclusive"])
        self.assertAlmostEqual(out["observed_order"], 2.0, places=2)
        self.assertIn("band_abs_middle", out)
        self.assertGreater(out["band_abs_middle"], out["band_abs"])


class EcaHoekstraBand(unittest.TestCase):
    """The in-act refinement band: clamp, non-monotone fallback, degeneracy."""

    def test_clean_second_order_triplet(self):
        cells = [1000, 8000, 64000]
        h = [(1.0 / n) ** (1 / 3) for n in cells]
        values = [1.0 + 4.0 * hh ** 2 for hh in h]
        out = uq.eca_hoekstra_band(cells, values)
        self.assertTrue(out["monotone"])
        self.assertFalse(out["clamped"])
        self.assertAlmostEqual(out["observed_order"], 2.0, places=2)
        e21 = abs(values[2] - values[1])
        self.assertAlmostEqual(out["band_abs"], 1.25 * e21 / (2 ** 2 - 1),
                               places=10)
        self.assertIn("Eca and Hoekstra 2014", out["method"])

    def test_silly_observed_order_is_clamped_and_says_so(self):
        # The real overnight motorbike ladder: p = 4.82, outside [0.5, 2.5].
        out = uq.eca_hoekstra_band(
            [14714, 66316, 353578],
            [0.47066928, 0.4201672083333333, 0.4155770166666667])
        self.assertTrue(out["clamped"])
        self.assertAlmostEqual(out["observed_order"], 4.824, places=2)
        self.assertEqual(out["order_used"], 2.5)
        self.assertIn(uq.ORDER_CLAMP_NOTE, out["method"])
        # Band uses the clamped order, so it stays sane (not the raw-p band).
        self.assertLess(out["band_abs"], 0.01)
        self.assertGreater(out["band_abs"], 0.0005)

    def test_low_order_clamps_from_below(self):
        cells = [1000, 8000, 64000]
        h = [(1.0 / n) ** (1 / 3) for n in cells]
        values = [1.0 + 0.5 * hh ** 0.2 for hh in h]     # apparent p ~ 0.2
        out = uq.eca_hoekstra_band(cells, values)
        self.assertTrue(out["clamped"])
        self.assertEqual(out["order_used"], 0.5)

    def test_non_monotone_falls_back_to_spread_times_1_25(self):
        out = uq.eca_hoekstra_band([1000, 8000, 64000], [1.0, 1.2, 1.1])
        self.assertFalse(out["monotone"])
        self.assertIsNone(out["observed_order"])
        self.assertAlmostEqual(out["band_abs"], 1.25 * 0.2, places=10)
        self.assertEqual(out["method"], uq.NON_MONOTONE_NOTE)

    def test_identical_meshes_refuse_a_band(self):
        out = uq.eca_hoekstra_band([67826, 67826, 137569],
                                   [0.0289, 0.0289, 0.0217])
        self.assertIsNone(out["band_abs"])
        self.assertFalse(out["conclusive"])
        self.assertEqual(out["method"], uq.DEGENERATE)

    def test_method_carries_no_em_dash_or_arrow(self):
        for args in (([1000, 8000, 64000], [1.0, 1.1, 1.15]),
                     ([1000, 8000, 64000], [1.0, 1.2, 1.1]),
                     ([1000, 1000, 64000], [1.0, 1.0, 1.1])):
            out = uq.eca_hoekstra_band(*args)
            self.assertNotIn("—", out["method"])
            self.assertNotIn("→", out["method"])


class Spreads(unittest.TestCase):
    def test_spread_is_half_range_and_labeled(self):
        out = uq.spread_estimate(
            {"kOmegaSST": 0.40, "kEpsilon": 0.44, "SpalartAllmaras": 0.41},
            label="inter-closure spread (screening estimate)")
        self.assertAlmostEqual(out["band_abs"], 0.02)
        self.assertTrue(out["screening_estimate"])
        self.assertIn("screening estimate", out["method"])

    def test_spread_never_called_a_bound(self):
        out = uq.spread_estimate({"a": 1.0, "b": 2.0}, label="correlation-family spread")
        self.assertNotIn("bound", out["method"].lower())


class Combination(unittest.TestCase):
    def test_rss(self):
        out = uq.combine_expanded(input_2sigma=3.0, numerical_abs=4.0, model_abs=None)
        self.assertAlmostEqual(out["combined_95"], 5.0)
        self.assertEqual(out["missing"], ["model"])
        self.assertEqual(set(out["contributions"]), {"input", "numerical"})

    def test_all_missing_is_none_not_zero(self):
        out = uq.combine_expanded(input_2sigma=None, numerical_abs=None, model_abs=None)
        self.assertIsNone(out["combined_95"])


class StudyRecords(unittest.TestCase):
    def _tmp_studies(self):
        tmp = tempfile.TemporaryDirectory()
        patcher = mock.patch.object(uq, "STUDIES_DIR", Path(tmp.name))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(tmp.cleanup)

    def test_fingerprint_mismatch_is_pending_never_stale(self):
        self._tmp_studies()
        fp = uq.setup_fingerprint(body="x", solver="openfoam", closure="kOmegaSST",
                                  velocity=20.0, refinement=3, iterations=300)
        uq.save_study("x", {"fingerprint": fp,
                            "numerical": {"band_abs": 0.01, "method": "3-mesh"},
                            "provenance": ["m-1"]})
        other = uq.setup_fingerprint(body="x", solver="openfoam", closure="kOmegaSST",
                                     velocity=25.0, refinement=3, iterations=300)
        hit = uq.channels_for("x", fp)
        miss = uq.channels_for("x", other)
        self.assertFalse(hit["pending"]) ; self.assertIsNotNone(hit["numerical"])
        self.assertTrue(miss["pending"]) ; self.assertIsNone(miss["numerical"])

    def test_missing_study_is_pending(self):
        self._tmp_studies()
        out = uq.channels_for("nobody", "deadbeef")
        self.assertTrue(out["pending"])


class TransferredModelBand(unittest.TestCase):
    """Doctrine fallback: a body with no closure study borrows a conservative
    pool statistic from the lab's own measured spread history."""

    def _tmp_studies(self):
        tmp = tempfile.TemporaryDirectory()
        patcher = mock.patch.object(uq, "STUDIES_DIR", Path(tmp.name))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(tmp.cleanup)

    def _seed_pool(self):
        uq.save_study("bikey", {
            "numerical": {"band_abs": 0.0005, "value_working": 0.42},
            "model": {"band_abs": 0.0018, "method": "inter-closure spread"}})
        uq.save_study("wingy", {
            "numerical": {"band_abs": 0.003, "value_working": 0.0217},
            "model": {"band_abs": 0.0061, "method": "inter-closure spread"}})
        # A study with a spread but no working value contributes nothing.
        uq.save_study("valvey", {
            "numerical": {"band_abs": 81.0},
            "model": {"band_abs": 104.8, "method": "correlation-family"}})

    def test_pool_statistic_is_mean_plus_sigma_never_below_the_max(self):
        self._tmp_studies()
        self._seed_pool()
        out = uq.transferred_model_band(0.05)
        self.assertIsNotNone(out)
        rels = [0.0018 / 0.42, 0.0061 / 0.0217]
        mean = sum(rels) / 2
        sigma = math.sqrt(sum((r - mean) ** 2 for r in rels))
        expected_rel = max(mean + sigma, max(rels))
        self.assertAlmostEqual(out["band_rel"], round(expected_rel, 5),
                               places=5)
        self.assertAlmostEqual(out["band_abs"], expected_rel * 0.05, places=6)
        self.assertEqual(set(out["members"]), {"bikey", "wingy"})
        self.assertTrue(out["screening_estimate"])
        self.assertTrue(out["transferred"])
        self.assertIn("validation history", out["method"])

    def test_exclude_keeps_a_body_out_of_its_own_pool(self):
        self._tmp_studies()
        self._seed_pool()
        out = uq.transferred_model_band(0.05, exclude="wingy")
        self.assertEqual(set(out["members"]), {"bikey"})
        self.assertAlmostEqual(out["band_rel"],
                               round(0.0018 / 0.42, 5), places=5)

    def test_no_pool_or_no_value_means_no_invented_band(self):
        self._tmp_studies()
        self.assertIsNone(uq.transferred_model_band(0.05))
        self._seed_pool()
        self.assertIsNone(uq.transferred_model_band(None))
        self.assertIsNone(uq.transferred_model_band(0.0))


class HonestyRails(unittest.TestCase):
    def test_channels_never_upgrade_the_chip(self):
        # A perfect channel set still cannot make plain trust() say VALIDATED.
        verdict = trust(relative_error=0.0001, converged=True,
                        in_validated_regime=True, calibrated=True)
        self.assertNotEqual(verdict["tier"], VALIDATED)

    def test_method_label_mandatory(self):
        out = uq.ladder_band([1000, 8000, 64000], [1.0, 1.1, 1.15])
        self.assertTrue(out["method"])
        spread = uq.spread_estimate({"a": 1, "b": 2}, label="model-form vs solver anchors")
        self.assertTrue(spread["method"])


if __name__ == "__main__":
    unittest.main()
