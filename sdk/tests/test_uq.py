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
