"""UQ studies: ladder math, spreads, combination, and the honesty rails."""
from __future__ import annotations

import math
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from chief_engineer import lab, uq
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
    """Two distinct meshes are not a ladder.

    This used to be written with the NACA 4412 numbers and a duplicated coarse
    rung, which asserted that the 4412 ladder is degenerate. It is not: that
    body has three distinct rungs, 67,826 / 137,569 / 337,334 cells, and they
    fall monotonically. The degeneracy rule is a property of the math, so it is
    exercised on neutral numbers here, and the real 4412 ladder is measured for
    what it is in RealNaca4412Ladder below.
    """

    def test_identical_meshes_collapse_to_the_honest_sentence(self):
        out = uq.ladder_band([50000, 50000, 100000], [0.4, 0.4, 0.3])
        self.assertFalse(out["conclusive"])
        self.assertEqual(out["method"], uq.DEGENERATE)
        self.assertAlmostEqual(out["band_abs"], 3.0 * (0.4 - 0.3), places=8)

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


class AsymptoticGuards(unittest.TestCase):
    """Monotone plus an in-window observed order is not sufficient.

    The 2026-07-27 B-52 near-miss: the (production, fine-uq, finer2) triple
    is nominally monotone with p = 2.25, inside [0.5, 2.5], and the old gate
    would have certified it at +/-0.0157. A human rejected it for two
    reasons the gate did not check: the Cd increments GROW with refinement
    (the opposite of asymptotic shrinkage), and the Richardson extrapolation
    lands far outside the whole measured range. Both are now hard guards
    that downgrade the verdict; the TMR flat plate proves the guards do not
    reject a genuinely converging ladder.
    """

    # B-52, same-recipe rungs 3/4/5/6 (cells 135779, 193880, 255358, 330950;
    # only the last three are distinct-and-monotone-fit-eligible here).
    B52_CELLS = [135779, 193880, 255358, 330950]
    B52_CD = [0.049053, 0.047196, 0.049573, 0.052275]

    # TMR flat plate: cells 816, 3264, 13056, 52224.
    TMR_CELLS = [816, 3264, 13056, 52224]
    TMR_CD = [0.0026686916613, 0.0027811695632, 0.0028342538677,
              0.0028564381699]

    def test_b52_increments_grow_and_are_rejected(self):
        # Sanity on the raw numbers before the gate even runs: the human's
        # first reason. Increments (magnitudes) GROW: 0.00186 -> 0.00238 ->
        # 0.00270, the opposite of asymptotic shrinkage.
        increments = [abs(b - a) for a, b in
                     zip(self.B52_CD, self.B52_CD[1:])]
        self.assertEqual(len(increments), 3)
        self.assertLess(increments[0], increments[1])
        self.assertLess(increments[1], increments[2])

        out = uq.eca_hoekstra_band(self.B52_CELLS, self.B52_CD)
        # The triple used is the last three by cells: monotone, and p would
        # land inside the accept window on the order test alone.
        self.assertTrue(out["monotone"])
        self.assertAlmostEqual(out["observed_order"], 2.253, places=2)
        # The old gate's own logic would have called this conclusive on the
        # order test alone; the new guard must not.
        self.assertFalse(out["conclusive"])
        self.assertEqual(out["method"], uq.GROWING_INCREMENT_NOTE)
        # The conservative band stands: max spread * 1.25 on the fit triple,
        # not the (much tighter, and wrong) fitted GCI band of ~0.0157.
        spread = max(self.B52_CD[-3:]) - min(self.B52_CD[-3:])
        self.assertAlmostEqual(out["band_abs"], 1.25 * spread, places=10)
        self.assertGreater(out["band_abs"], 0.006)

    def test_b52_richardson_value_is_far_outside_the_measured_range(self):
        # The human's second, independent reason: even ignoring the
        # increment trend, the extrapolated "limit" is not a limit.
        out = uq.eca_hoekstra_band(self.B52_CELLS, self.B52_CD)
        lo, hi = min(self.B52_CD[-3:]), max(self.B52_CD[-3:])
        self.assertIsNotNone(out["richardson_extrapolated"])
        self.assertGreater(out["richardson_extrapolated"], hi)
        # It's not just outside -- it's outside by multiples of the whole
        # measured range, i.e. a divergence, not a marginal overshoot.
        width = hi - lo
        self.assertGreater(out["richardson_extrapolated"] - hi, width)

    def test_tmr_flat_plate_still_certifies(self):
        # Increments shrink: 0.000112 -> 0.0000531 -> 0.0000222.
        increments = [abs(b - a) for a, b in
                     zip(self.TMR_CD, self.TMR_CD[1:])]
        self.assertGreater(increments[0], increments[1])
        self.assertGreater(increments[1], increments[2])

        out = uq.eca_hoekstra_band(self.TMR_CELLS, self.TMR_CD)
        self.assertTrue(out["monotone"])
        self.assertFalse(out["clamped"])
        self.assertTrue(out["conclusive"])
        self.assertIn("Eca and Hoekstra 2014", out["method"])
        # The Richardson value (~0.0028724) sits just above the measured
        # range (up to 0.0028564381699) -- close enough that the guard must
        # accept it, unlike the B-52 case's multi-range-width overshoot.
        lo, hi = min(self.TMR_CD[-3:]), max(self.TMR_CD[-3:])
        self.assertGreater(out["richardson_extrapolated"], hi)
        self.assertLess(out["richardson_extrapolated"] - hi, 0.25 * (hi - lo))


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


class RealNaca4412Ladder(unittest.TestCase):
    """The measured NACA 4412 ladder, and what it is allowed to certify.

    Three distinct meshes of one case, falling monotonically: 0.02892 at
    67,826 cells, 0.02167 at 137,569, 0.01892 at 337,334. The band lands at
    16.3 percent of the working value and the observed order comes out at 4.6
    from a second-order scheme, so it is clamped and the study is NOT
    conclusive. That is the state the tier logic has to honour.
    """

    CELLS = [67826, 137569, 337334]
    CD = [0.02892, 0.02167, 0.01892]

    def test_the_ladder_is_monotone_and_three_distinct_rungs(self):
        self.assertEqual(len(set(self.CELLS)), 3)
        self.assertTrue(self.CD[0] > self.CD[1] > self.CD[2])

    def test_band_is_clamped_and_inconclusive(self):
        out = uq.eca_hoekstra_band(self.CELLS, self.CD)
        self.assertTrue(out["monotone"])
        self.assertAlmostEqual(out["observed_order"], 4.625, places=2)
        self.assertTrue(out["clamped"])
        self.assertFalse(out["conclusive"])
        self.assertAlmostEqual(out["band_abs"] / self.CD[-1], 0.16342, places=4)

    def test_a_clamped_ladder_cannot_certify_the_reference(self):
        # The corrected expectation. Agreement inside the band used to be the
        # whole test for VALIDATED; a reference whose own confidence is low,
        # or a grid study that came back inconclusive, now blocks the chip and
        # the result reads SOLVER-BACKED instead.
        reference = {"cd": 0.030, "tolerance": 0.35, "confidence": "low",
                     "source": "a hand-set estimate"}
        verdict = lab.validate_against_reference(
            measured_cd=self.CD[0], reference=reference, grid_conclusive=False)
        self.assertEqual(verdict["tier"], lab.SOLVER_BACKED)
        self.assertIn("low-confidence estimate", verdict["reason"])
        self.assertIn("inconclusive", verdict["reason"])
        # The comparison is still reported in full; only the chip is refused.
        self.assertAlmostEqual(verdict["comparison"]["relative_error"], 0.036,
                               places=3)

    def test_each_blocker_stands_on_its_own(self):
        solid = {"cd": 0.030, "tolerance": 0.35, "confidence": "high",
                 "source": "a published measurement"}
        self.assertEqual(
            lab.validate_against_reference(measured_cd=self.CD[0],
                                           reference=solid,
                                           grid_conclusive=True)["tier"],
            VALIDATED)
        self.assertEqual(
            lab.validate_against_reference(measured_cd=self.CD[0],
                                           reference=solid,
                                           grid_conclusive=False)["tier"],
            lab.SOLVER_BACKED)
        # No ladder on record for this setup is not evidence of a problem.
        self.assertEqual(
            lab.validate_against_reference(measured_cd=self.CD[0],
                                           reference=solid,
                                           grid_conclusive=None)["tier"],
            VALIDATED)
        low = dict(solid, confidence="low")
        self.assertEqual(
            lab.validate_against_reference(measured_cd=self.CD[0],
                                           reference=low,
                                           grid_conclusive=True)["tier"],
            lab.SOLVER_BACKED)

    def test_the_finest_rung_is_what_the_credential_displays(self):
        # The propagation gap: the credential was written on the coarsest rung
        # and the ladder finished later, so the wall kept showing 0.02892 on a
        # 67,826-cell mesh while 0.01892 on 337,334 cells sat on disk.
        record = {
            "name": "naca4412_wing", "ok": True,
            "cd_measured": "0.02892", "cd_compared": 0.0289,
            "basis_note": "already on the reference's planform-area basis",
            "tier": VALIDATED, "reason": "within 4% of the reference",
            "report_results": [{"quantity": "Mesh", "value": "67,826 cells"}],
        }
        study = {
            "levels": [{"cells": c, "cd": v, "mission": f"uq-r{i}"}
                       for i, (c, v) in enumerate(zip(self.CELLS, self.CD), 1)],
            "numerical": {"conclusive": False, "band_abs": 0.00309},
        }
        reference = {"cd": 0.030, "tolerance": 0.35, "confidence": "low",
                     "source": "a hand-set estimate"}
        shown = lab.displayed_credential(record, reference=reference,
                                         study=study)
        self.assertTrue(shown["superseded"])
        self.assertEqual(shown["measured"], "0.01892")
        self.assertEqual(shown["cells"], 337334)
        self.assertEqual(shown["tier"], lab.SOLVER_BACKED)
        self.assertNotEqual(shown["tier"], VALIDATED)

    def test_a_ladder_that_is_not_this_credentials_never_moves_it(self):
        # A stored study whose rungs never touched this credential's mesh is a
        # different setup; it may neither supply the displayed value nor gate
        # the tier.
        record = {
            "name": "naca4412_wing", "ok": True,
            "cd_measured": "0.02892", "cd_compared": 0.0289,
            "basis_note": "already on the reference's planform-area basis",
            "report_results": [{"quantity": "Mesh", "value": "40,000 cells"}],
        }
        study = {
            "levels": [{"cells": c, "cd": v} for c, v in zip(self.CELLS, self.CD)],
            "numerical": {"conclusive": False, "band_abs": 0.00309},
        }
        reference = {"cd": 0.030, "tolerance": 0.35, "confidence": "high",
                     "source": "a published measurement"}
        shown = lab.displayed_credential(record, reference=reference,
                                         study=study)
        self.assertFalse(shown["superseded"])
        self.assertEqual(shown["measured"], "0.02892")
        self.assertIsNone(shown["grid_conclusive"])
        self.assertEqual(shown["tier"], VALIDATED)

    def test_a_rebased_credential_keeps_its_area_ratio_on_the_finer_rung(self):
        record = {
            "name": "ahmed_25", "ok": True,
            "cd_measured": "0.1", "cd_compared": 0.35,
            "basis_note": "rebased from the measured planform area onto frontal area",
            "report_results": [{"quantity": "Mesh", "value": "1,000 cells"}],
        }
        study = {"levels": [{"cells": 1000, "cd": 0.1},
                            {"cells": 2000, "cd": 0.09},
                            {"cells": 4000, "cd": 0.08}],
                 "numerical": {"conclusive": True, "band_abs": 0.001}}
        reference = {"cd": 0.28, "tolerance": 0.15, "confidence": "high",
                     "area_basis": "frontal", "source": "a published measurement"}
        shown = lab.displayed_credential(record, reference=reference,
                                         study=study)
        self.assertEqual(shown["measured"], "0.08")
        # 0.08 carried onto frontal area by the record's own 3.5x ratio.
        self.assertAlmostEqual(shown["compared"], 0.28, places=2)
        self.assertEqual(shown["tier"], VALIDATED)


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
