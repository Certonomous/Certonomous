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
        out = uq.ladder_band(cells, values, dim=3)
        self.assertTrue(out["conclusive"])
        self.assertAlmostEqual(out["observed_order"], 2.0, places=2)
        # GCI band on the fine mesh: 1.25*|e21|/(r^p-1)
        e21 = abs(values[2] - values[1])
        self.assertAlmostEqual(out["band_abs"], 1.25 * e21 / (2 ** 2 - 1), places=10)
        self.assertIn("observed order p = 2.00", out["method"])

    def test_non_monotone_ladder_says_the_sentence(self):
        out = uq.ladder_band([1000, 8000, 64000], [1.0, 1.2, 1.1], dim=3)
        self.assertFalse(out["conclusive"])
        self.assertIsNone(out["observed_order"])
        self.assertEqual(out["method"], uq.INCONCLUSIVE)
        # Conservative fallback: factor 3 on the observed range.
        self.assertAlmostEqual(out["band_abs"], 3.0 * 0.2, places=10)

    def test_wild_order_gets_conservative_band(self):
        # Nearly stalled coarse pair -> huge apparent order -> factor-3 band.
        out = uq.ladder_band([1000, 8000, 64000], [1.5, 1.00001, 1.0], dim=3)
        self.assertFalse(out["conclusive"])
        self.assertGreaterEqual(out["band_abs"], 3.0 * 0.49)


class LadderAsymptoticGuards(unittest.TestCase):
    """ladder_band gets the same two guards as eca_hoekstra_band.

    Monotone plus an in-window observed order is not sufficient here either:
    ladder_band's window is wider ([0.5, 4.0], not [0.5, 2.5]), but the same
    2026-07-27 B-52 near-miss (monotone, p = 2.25, growing increments, a
    Richardson extrapolation far outside the measured range) would have been
    certified conclusive by the order-window check alone. The TMR flat plate
    proves the guards do not reject a genuinely converging ladder.
    """

    # B-52, same-recipe rungs 3/4/5/6 (cells 135779, 193880, 255358, 330950;
    # only the last three are distinct-and-monotone-fit-eligible here).
    B52_CELLS = [135779, 193880, 255358, 330950]
    B52_CD = [0.049053, 0.047196, 0.049573, 0.052275]

    # TMR 2D zero-pressure-gradient flat plate, the full five-rung ladder as
    # measured (demo-output/website/tmr/flatplate_sst.json,
    # convergence_extended.ladder_cells / .cd_ladder; the 208896 rung was
    # solved 2026-07-31). Fitted dim=2, which is what that module uses and
    # what NASA's own drag_convergence_sstv.dat header declares.
    #
    # This fixture used to stop at 52224, four rungs, and asserted that the
    # ladder certifies. It certified for the wrong reason: the fit was the
    # 3264/13056/52224 triple, whose Richardson value overshoots its own
    # measured range by 21.16% and should have been declined -- the coarse
    # 816 rung, which never entered the fit, widened the range the guard
    # measures against until the overshoot read 8.48%. The good case is now
    # the finest triple, which passes the guard on its own three rungs.
    TMR_CELLS = [816, 3264, 13056, 52224, 208896]
    TMR_CD = [0.0026686916613, 0.0027811695632, 0.0028342538677,
              0.0028564381699, 0.0028635838023]
    TMR_DIM = 2
    # The SAME ladder's skin friction at x/c = 0.97, same file,
    # convergence_extended.cf_097_ladder. The corpus sweep of 2026-08-01
    # found it carries the identical call-shape flip that Cd does, and the
    # recalibration comment on EXTRAPOLATION_TOL_FRAC was read off Cd alone.
    # It is the second accepted fixture, and it is the THIN one.
    TMR_CF = [0.002529462373594013, 0.0026270458521110126,
              0.0026747849116543518, 0.0026968874014089953,
              0.0027045510419338643]

    def test_b52_increments_grow_and_are_rejected(self):
        # Increments (magnitudes) GROW: 0.00186 -> 0.00238 -> 0.00270, the
        # opposite of asymptotic shrinkage.
        increments = [abs(b - a) for a, b in
                     zip(self.B52_CD, self.B52_CD[1:])]
        self.assertLess(increments[0], increments[1])
        self.assertLess(increments[1], increments[2])

        out = uq.ladder_band(self.B52_CELLS, self.B52_CD, dim=3)
        # Monotone, and p lands inside ladder_band's own [0.5, 4.0] window,
        # so the order-window check alone would have certified this.
        self.assertTrue(out["monotone"])
        self.assertAlmostEqual(out["observed_order"], 2.253, places=2)
        self.assertFalse(out["conclusive"])
        self.assertEqual(out["method"], uq.LADDER_GROWING_INCREMENT_NOTE)
        # The conservative fallback stands: factor-3 on the range of the FIT
        # TRIPLE, not the (much tighter, and wrong) fitted GCI band. On this
        # fixture the fit triple's range happens to equal the four-rung
        # range, so the number is the same either way; the assertion is
        # written on the three rungs the fit used, which is what the band is
        # now defined over.
        spread = max(self.B52_CD[-3:]) - min(self.B52_CD[-3:])
        self.assertAlmostEqual(out["band_abs"], 3.0 * spread, places=10)

    def test_b52_richardson_value_is_far_outside_the_measured_range(self):
        out = uq.ladder_band(self.B52_CELLS, self.B52_CD, dim=3)
        lo, hi = min(self.B52_CD[-3:]), max(self.B52_CD[-3:])
        self.assertIsNotNone(out["richardson_extrapolated"])
        self.assertGreater(out["richardson_extrapolated"], hi)
        width = hi - lo
        self.assertGreater(out["richardson_extrapolated"] - hi, width)

    def test_tmr_flat_plate_still_certifies(self):
        # Increments shrink at every one of the four steps:
        # 1.1248e-4 -> 5.3084e-5 -> 2.2184e-5 -> 7.1456e-6.
        increments = [abs(b - a) for a, b in
                     zip(self.TMR_CD, self.TMR_CD[1:])]
        for coarser, finer in zip(increments, increments[1:]):
            self.assertGreater(coarser, finer)

        out = uq.ladder_band(self.TMR_CELLS, self.TMR_CD, dim=self.TMR_DIM)
        self.assertTrue(out["monotone"])
        self.assertTrue(out["conclusive"])
        self.assertIn("GCI band, Fs = 1.25", out["method"])
        lo, hi = min(self.TMR_CD[-3:]), max(self.TMR_CD[-3:])
        self.assertGreater(out["richardson_extrapolated"], hi)
        self.assertLess(out["richardson_extrapolated"] - hi, 0.25 * (hi - lo))

    def test_the_verdict_does_not_depend_on_how_many_rungs_were_passed(self):
        # The fix. The fit uses the finest three rungs; the guard tolerance
        # and the fallback band must therefore be measured over those three
        # and no others, or the same fit answers two ways.
        fit = uq.ladder_band(self.TMR_CELLS[-3:], self.TMR_CD[-3:],
                             dim=self.TMR_DIM)
        for n in range(3, len(self.TMR_CELLS) + 1):
            out = uq.ladder_band(self.TMR_CELLS[-n:], self.TMR_CD[-n:],
                                 dim=self.TMR_DIM)
            self.assertEqual(out["conclusive"], fit["conclusive"], n)
            self.assertEqual(out["band_abs"], fit["band_abs"], n)
            self.assertEqual(out["observed_order"], fit["observed_order"], n)

    def test_the_declined_middle_triple_stays_declined_with_a_rung_in_front(self):
        # The reproduction. 3264/13056/52224 extrapolates to 0.00287237,
        # 21.16% of its own range width above the top of it, so it is
        # declined. Handing the same fit the coarse 816 rung used to widen
        # the range until that read 8.48% and the ladder certified at a band
        # of 1.99087e-5, 0.70% of the drag.
        three = uq.ladder_band(self.TMR_CELLS[1:4], self.TMR_CD[1:4],
                               dim=self.TMR_DIM)
        four = uq.ladder_band(self.TMR_CELLS[0:4], self.TMR_CD[0:4],
                              dim=self.TMR_DIM)
        self.assertFalse(three["conclusive"])
        self.assertFalse(four["conclusive"])
        self.assertIsNone(uq.reportable_band(three))
        self.assertIsNone(uq.reportable_band(four))
        self.assertEqual(uq.not_conclusive_reason(three),
                         uq.not_conclusive_reason(four))
        self.assertEqual(three["band_abs"], four["band_abs"])

    def test_the_skin_friction_ladder_carries_the_same_flip(self):
        # Found by the corpus sweep, 2026-08-01. The recalibration that set
        # EXTRAPOLATION_TOL_FRAC was read off Cd; cf_097 on the same five
        # rungs flips the same way at the same call shape and nobody had
        # looked. Locked here so the second fixture cannot go missing again.
        three = uq.ladder_band(self.TMR_CELLS[1:4], self.TMR_CF[1:4],
                               dim=self.TMR_DIM)
        four = uq.ladder_band(self.TMR_CELLS[0:4], self.TMR_CF[0:4],
                              dim=self.TMR_DIM)
        self.assertFalse(three["conclusive"])
        self.assertFalse(four["conclusive"])
        self.assertEqual(three["band_abs"], four["band_abs"])
        lo, hi = min(self.TMR_CF[1:4]), max(self.TMR_CF[1:4])
        excess = (three["richardson_extrapolated"] - hi) / (hi - lo)
        self.assertAlmostEqual(excess, 0.2728, places=3)
        # And the all-five-rungs range would have read 11.38%, under 0.15.
        lo4, hi4 = min(self.TMR_CF[0:4]), max(self.TMR_CF[0:4])
        old_excess = (three["richardson_extrapolated"] - hi4) / (hi4 - lo4)
        self.assertLess(old_excess, uq.EXTRAPOLATION_TOL_FRAC)

    def test_the_accepted_skin_friction_triple_is_the_thin_margin(self):
        # The finest cf_097 triple must be certified -- it is a genuinely
        # converging ladder -- but it clears the tolerance by only 1.10x,
        # not the 1.30x the Cd fixture measures. That is the real margin of
        # this corpus and it is asserted rather than left in a comment.
        out = uq.ladder_band(self.TMR_CELLS[-3:], self.TMR_CF[-3:],
                             dim=self.TMR_DIM)
        self.assertTrue(out["conclusive"])
        lo, hi = min(self.TMR_CF[-3:]), max(self.TMR_CF[-3:])
        excess = (out["richardson_extrapolated"] - hi) / (hi - lo)
        self.assertAlmostEqual(excess, 0.1367, places=3)
        self.assertLess(excess, uq.EXTRAPOLATION_TOL_FRAC)
        self.assertLess(uq.EXTRAPOLATION_TOL_FRAC / excess, 1.15)


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
        out = uq.ladder_band([50000, 50000, 100000], [0.4, 0.4, 0.3], dim=3)
        self.assertFalse(out["conclusive"])
        self.assertEqual(out["method"], uq.DEGENERATE)
        self.assertAlmostEqual(out["band_abs"], 3.0 * (0.4 - 0.3), places=8)

    def test_four_levels_use_last_three_distinct(self):
        cells = [1000, 1000, 8000, 64000]
        h = [(1.0 / n) ** (1 / 3) for n in (1000, 8000, 64000)]
        vals = [1.0 + 4.0 * h[0] ** 2, 1.0 + 4.0 * h[0] ** 2,
                1.0 + 4.0 * h[1] ** 2, 1.0 + 4.0 * h[2] ** 2]
        out = uq.ladder_band(cells, vals, dim=3)
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
        out = uq.eca_hoekstra_band(cells, values, dim=3)
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
            [0.47066928, 0.4201672083333333, 0.4155770166666667], dim=3)
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
        out = uq.eca_hoekstra_band(cells, values, dim=3)
        self.assertTrue(out["clamped"])
        self.assertEqual(out["order_used"], 0.5)

    def test_non_monotone_falls_back_to_spread_times_1_25(self):
        out = uq.eca_hoekstra_band([1000, 8000, 64000], [1.0, 1.2, 1.1], dim=3)
        self.assertFalse(out["monotone"])
        self.assertIsNone(out["observed_order"])
        self.assertAlmostEqual(out["band_abs"], 1.25 * 0.2, places=10)
        self.assertEqual(out["method"], uq.NON_MONOTONE_NOTE)

    def test_identical_meshes_refuse_a_band(self):
        out = uq.eca_hoekstra_band([67826, 67826, 137569],
                                   [0.0289, 0.0289, 0.0217], dim=3)
        self.assertIsNone(out["band_abs"])
        self.assertFalse(out["conclusive"])
        self.assertEqual(out["method"], uq.DEGENERATE)

    def test_method_carries_no_em_dash_or_arrow(self):
        for args in (([1000, 8000, 64000], [1.0, 1.1, 1.15]),
                     ([1000, 8000, 64000], [1.0, 1.2, 1.1]),
                     ([1000, 1000, 64000], [1.0, 1.0, 1.1])):
            out = uq.eca_hoekstra_band(*args, dim=3)
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

    # TMR 2D flat plate, the full five-rung ladder as measured
    # (demo-output/website/tmr/flatplate_sst.json, convergence_extended).
    # See LadderAsymptoticGuards for why this fixture no longer stops at
    # four rungs: the four-rung reading certified a fit that its own three
    # rungs decline.
    TMR_CELLS = [816, 3264, 13056, 52224, 208896]
    TMR_CD = [0.0026686916613, 0.0027811695632, 0.0028342538677,
              0.0028564381699, 0.0028635838023]
    TMR_DIM = 2

    def test_b52_increments_grow_and_are_rejected(self):
        # Sanity on the raw numbers before the gate even runs: the human's
        # first reason. Increments (magnitudes) GROW: 0.00186 -> 0.00238 ->
        # 0.00270, the opposite of asymptotic shrinkage.
        increments = [abs(b - a) for a, b in
                     zip(self.B52_CD, self.B52_CD[1:])]
        self.assertEqual(len(increments), 3)
        self.assertLess(increments[0], increments[1])
        self.assertLess(increments[1], increments[2])

        out = uq.eca_hoekstra_band(self.B52_CELLS, self.B52_CD, dim=3)
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
        out = uq.eca_hoekstra_band(self.B52_CELLS, self.B52_CD, dim=3)
        lo, hi = min(self.B52_CD[-3:]), max(self.B52_CD[-3:])
        self.assertIsNotNone(out["richardson_extrapolated"])
        self.assertGreater(out["richardson_extrapolated"], hi)
        # It's not just outside -- it's outside by multiples of the whole
        # measured range, i.e. a divergence, not a marginal overshoot.
        width = hi - lo
        self.assertGreater(out["richardson_extrapolated"] - hi, width)

    def test_tmr_flat_plate_still_certifies(self):
        # Increments shrink at every step: 1.1248e-4, 5.3084e-5, 2.2184e-5,
        # 7.1456e-6.
        increments = [abs(b - a) for a, b in
                     zip(self.TMR_CD, self.TMR_CD[1:])]
        for coarser, finer in zip(increments, increments[1:]):
            self.assertGreater(coarser, finer)

        out = uq.eca_hoekstra_band(self.TMR_CELLS, self.TMR_CD,
                                   dim=self.TMR_DIM)
        self.assertTrue(out["monotone"])
        self.assertFalse(out["clamped"])
        self.assertTrue(out["conclusive"])
        self.assertIn("Eca and Hoekstra 2014", out["method"])
        # The band the flat plate published on 2026-07-31: 4.244e-6 on a Cd
        # of 0.0028635838023, 0.148% of the value.
        self.assertAlmostEqual(uq.reportable_band(out), 4.244064059104043e-06,
                               places=12)
        # The Richardson value (0.00286698) sits just above the measured
        # range of the FIT TRIPLE (up to 0.0028635838023) -- 11.58% of that
        # range's width, close enough that the guard must accept it, unlike
        # the B-52 case's multi-range-width overshoot.
        lo, hi = min(self.TMR_CD[-3:]), max(self.TMR_CD[-3:])
        self.assertGreater(out["richardson_extrapolated"], hi)
        self.assertLess(out["richardson_extrapolated"] - hi, 0.15 * (hi - lo))

    def test_the_guard_measures_against_the_rungs_it_fitted(self):
        # A certifier must not answer two ways to one fit. Every call shape
        # that fits the same finest triple must return the same verdict and
        # the same width.
        fit = uq.eca_hoekstra_band(self.TMR_CELLS[-3:], self.TMR_CD[-3:],
                                   dim=self.TMR_DIM)
        self.assertTrue(fit["conclusive"])
        for n in range(3, len(self.TMR_CELLS) + 1):
            out = uq.eca_hoekstra_band(self.TMR_CELLS[-n:], self.TMR_CD[-n:],
                                       dim=self.TMR_DIM)
            self.assertEqual(out["conclusive"], fit["conclusive"], n)
            self.assertEqual(out["band_abs"], fit["band_abs"], n)
            self.assertEqual(uq.reportable_band(out), uq.reportable_band(fit), n)

        # And the fit that must NOT certify does not, at either call shape.
        # 3264/13056/52224 was declined on three rungs and certified at
        # 1.99087e-5 on four; that was the defect.
        three = uq.eca_hoekstra_band(self.TMR_CELLS[1:4], self.TMR_CD[1:4],
                                     dim=self.TMR_DIM)
        four = uq.eca_hoekstra_band(self.TMR_CELLS[0:4], self.TMR_CD[0:4],
                                    dim=self.TMR_DIM)
        self.assertFalse(three["conclusive"])
        self.assertFalse(four["conclusive"])
        self.assertIsNone(uq.reportable_band(four))
        self.assertEqual(three["band_abs"], four["band_abs"])
        self.assertEqual(uq.not_conclusive_reason(three),
                         uq.not_conclusive_reason(four))


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
        out = uq.eca_hoekstra_band(self.CELLS, self.CD, dim=3)
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
        # AND SO IS THE BAND. The envelope is published beside a frontal-area
        # value, so it has to be a frontal-area envelope: 0.001 on the rungs'
        # planform basis is 0.0035 on the card's. Printing the study's raw
        # 0.001 there understates it by the whole area ratio.
        self.assertEqual(shown["envelope"],
                         "±0.0035 across the 3-mesh refinement study")


class HonestyRails(unittest.TestCase):
    def test_channels_never_upgrade_the_chip(self):
        # A perfect channel set still cannot make plain trust() say VALIDATED.
        verdict = trust(relative_error=0.0001, converged=True,
                        in_validated_regime=True, calibrated=True)
        self.assertNotEqual(verdict["tier"], VALIDATED)

    def test_method_label_mandatory(self):
        out = uq.ladder_band([1000, 8000, 64000], [1.0, 1.1, 1.15], dim=3)
        self.assertTrue(out["method"])
        spread = uq.spread_estimate({"a": 1, "b": 2}, label="model-form vs solver anchors")
        self.assertTrue(spread["method"])


class DimensionalityDecidesOneThing(unittest.TestCase):
    """VERIFICATION_CHARTER section 3.1, made checkable.

    The charter claims that changing the assumed dimensionality divides every
    observed order by exactly 1.5 and leaves the extrapolated value and a
    conclusive ladder's band untouched. These tests are that claim; if the
    arithmetic ever stops satisfying them the charter is wrong and says so
    here first.
    """

    # Ladders built to a known order on a 3D reading of the cell counts. The
    # non-constant-ratio case matters: the fixed point solve carries a q
    # correction, and the invariance has to survive it.
    CASES = {
        "constant ratio, p = 2": ([10000, 80000, 640000], 2.0),
        "non-constant ratio, p = 1.7": ([12000, 73000, 610000], 1.7),
        "steep, p = 3.6": ([9000, 72000, 576000], 3.6),
        "shallow, p = 0.9": ([5000, 40000, 320000], 0.9),
    }

    @staticmethod
    def _values(cells, order, *, phi0=0.42, amp=0.05):
        h = [(1.0 / n) ** (1.0 / 3.0) for n in cells]
        return [phi0 + amp * ((x / h[-1]) ** order) for x in h]

    def test_dimensionality_is_required_not_defaulted(self):
        cells, values = [1000, 8000, 64000], [1.0, 1.1, 1.15]
        for fit in (uq.ladder_band, uq.eca_hoekstra_band):
            with self.subTest(fit=fit.__name__):
                with self.assertRaises(ValueError) as caught:
                    fit(cells, values)
                self.assertIn("unstated", str(caught.exception))

    def test_order_scales_by_exactly_one_and_a_half(self):
        for label, (cells, order) in self.CASES.items():
            values = self._values(cells, order)
            for fit in (uq.ladder_band, uq.eca_hoekstra_band):
                with self.subTest(case=label, fit=fit.__name__):
                    p3 = fit(cells, values, dim=3)["observed_order"]
                    p2 = fit(cells, values, dim=2)["observed_order"]
                    # Stored orders are rounded to three places, so the check
                    # is on the unrounded ratio implied by them, to a
                    # tolerance the rounding itself sets.
                    self.assertAlmostEqual(p3 / p2, 1.5, places=2)

    def test_extrapolated_value_does_not_move(self):
        for label, (cells, order) in self.CASES.items():
            values = self._values(cells, order)
            for fit in (uq.ladder_band, uq.eca_hoekstra_band):
                with self.subTest(case=label, fit=fit.__name__):
                    a = fit(cells, values, dim=3)["richardson_extrapolated"]
                    b = fit(cells, values, dim=2)["richardson_extrapolated"]
                    self.assertIsNotNone(a)
                    self.assertLess(abs(a - b) / abs(a), 1e-12)

    def test_a_conclusive_band_does_not_move(self):
        checked = 0
        for label, (cells, order) in self.CASES.items():
            values = self._values(cells, order)
            for fit in (uq.ladder_band, uq.eca_hoekstra_band):
                three = fit(cells, values, dim=3)
                two = fit(cells, values, dim=2)
                if not (three["conclusive"] and two["conclusive"]):
                    continue
                checked += 1
                with self.subTest(case=label, fit=fit.__name__):
                    self.assertLess(
                        abs(three["band_abs"] - two["band_abs"])
                        / abs(three["band_abs"]), 1e-12)
        self.assertGreater(checked, 0, "no case was conclusive both ways")

    def test_what_the_assumption_can_change_is_the_verdict(self):
        # The other half of the claim, and the reason the preflight exists.
        # The real cylinder vortex-shedding rungs: p = 3.63 read as three
        # dimensional, 2.42 read on the two dimensional mesh it actually is.
        cells, values = [2496, 5032, 8640], [0.1245, 0.1490, 0.1578]
        three = uq.eca_hoekstra_band(cells, values, dim=3)
        two = uq.eca_hoekstra_band(cells, values, dim=2)
        self.assertTrue(three["clamped"])
        self.assertFalse(two["clamped"])
        # And the verdict still does not move, because a guard that owes
        # nothing to dimensionality holds it either way.
        self.assertFalse(three["conclusive"])
        self.assertFalse(two["conclusive"])


class WhichGuardHeldTheVerdict(unittest.TestCase):
    def test_a_declined_ladder_records_the_guard_that_held_it(self):
        cells, values = [2496, 5032, 8640], [0.1245, 0.1490, 0.1578]
        two = uq.eca_hoekstra_band(cells, values, dim=2)
        self.assertEqual(two["not_conclusive_guard"], uq.GUARD_EXTRAPOLATION)
        self.assertIs(two["guards"][uq.GUARD_EXTRAPOLATION], False)
        self.assertIs(two["guards"][uq.GUARD_ORDER_WINDOW], True)

    def test_every_guard_is_evaluated_even_when_one_already_decided(self):
        # Read three dimensionally the same ladder is declined on its order,
        # but the extrapolation guard is still run and still recorded as
        # failing, so the record shows the verdict does not rest on the order.
        cells, values = [2496, 5032, 8640], [0.1245, 0.1490, 0.1578]
        three = uq.eca_hoekstra_band(cells, values, dim=3)
        self.assertEqual(three["not_conclusive_guard"], uq.GUARD_ORDER_WINDOW)
        self.assertEqual(uq.guards_holding(three),
                         [uq.GUARD_ORDER_WINDOW, uq.GUARD_EXTRAPOLATION])
        # And it no longer claims to be asymptotic without having asked.
        self.assertFalse(three["asymptotic"])

    def test_the_reason_names_the_recorded_guard_not_a_re_derivation(self):
        band = {"conclusive": False, "observed_order": 1.9,
                "clamped": False, "monotone": True,
                "method": "3-mesh study, observed order p = 1.90",
                "not_conclusive_guard": uq.GUARD_INCREMENT_TREND,
                "guards": {uq.GUARD_INCREMENT_TREND: False},
                "guards_failed": [uq.GUARD_INCREMENT_TREND]}
        # Nothing in the numbers says "increments grow"; only the record does.
        self.assertEqual(uq.not_conclusive_reason(band),
                         "successive increments grow with refinement")

    def test_a_conclusive_ladder_records_no_guard(self):
        cells = [10000, 80000, 640000]
        values = DimensionalityDecidesOneThing._values(cells, 2.0)
        out = uq.eca_hoekstra_band(cells, values, dim=3)
        self.assertTrue(out["conclusive"])
        self.assertIsNone(out["not_conclusive_guard"])
        self.assertEqual(uq.guards_holding(out), [])
        self.assertIsNone(uq.not_conclusive_reason(out))


class EveryGuardThatHoldsALadderIsNamed(unittest.TestCase):
    """The supersonic wedge rungs: 1800/7200/28800 cells, shock angle in deg.

    ``BETA`` is the ladder AS THE ACT PRINTS IT, rounded at the third decimal,
    which is what the two-dimensional ladder refit fitted. ``BETA_SOLVED`` is
    what the act actually fits, carried at full precision out of its own solve
    and captured 2026-08-01. Both are here because they do not agree on the
    digit: at an observed order this close to zero the extrapolation amplifies
    the finest increment by more than forty, so rounding the rungs moves the
    extrapolated shock angle by 2.02 degrees. They agree on everything that
    decides anything: the same two guards fail and the verdict is the same.
    """

    CELLS = [1800, 7200, 28800]
    BETA = [47.588, 46.123, 44.693]
    BETA_SOLVED = [47.58767882153372, 46.12330850878531, 44.692792746510406]

    def test_rounding_the_rungs_moves_the_digit_and_not_the_verdict(self):
        rounded = uq.eca_hoekstra_band(self.CELLS, self.BETA, dim=2)
        solved = uq.eca_hoekstra_band(self.CELLS, self.BETA_SOLVED, dim=2)
        self.assertAlmostEqual(rounded["richardson_extrapolated"],
                               -13.732714, places=5)
        self.assertAlmostEqual(solved["richardson_extrapolated"],
                               -15.753301, places=5)
        self.assertEqual(rounded["guards_failed"], solved["guards_failed"])
        self.assertEqual(rounded["conclusive"], solved["conclusive"])
        self.assertIsNone(uq.reportable_band(solved))

    def _band(self):
        return uq.eca_hoekstra_band(self.CELLS, self.BETA, dim=2)

    def test_two_guards_hold_the_wedge_and_the_reason_names_both(self):
        band = self._band()
        self.assertEqual(uq.guards_holding(band),
                         [uq.GUARD_ORDER_WINDOW, uq.GUARD_EXTRAPOLATION])
        reason = uq.not_conclusive_reason(band)
        self.assertIn("outside the credible range", reason)
        self.assertIn("outside the range it measured", reason)

    def test_one_failing_guard_reads_exactly_as_it_did_before(self):
        # The single-guard sentence is the common case and it does not change:
        # naming every guard must not reword a ladder that only has one.
        band = uq.eca_hoekstra_band(self.CELLS, self.BETA, dim=2)
        band = dict(band, guards_failed=[uq.GUARD_MONOTONE],
                    not_conclusive_guard=uq.GUARD_MONOTONE)
        self.assertEqual(uq.not_conclusive_reason(band),
                         "the three rungs do not move one way under refinement")

    def test_an_impossible_extrapolation_leads_and_replaces_its_guard(self):
        band = self._band()
        impossible = uq.impossible_extrapolation(
            band, quantity="the shock angle",
            why="which is not a shock angle any flow can have",
            floor=0.0, unit="deg")
        self.assertIn("minus 13.733 deg", impossible)
        reason = uq.not_conclusive_reason(band, impossible=impossible)
        self.assertTrue(reason.startswith("the shock angle the ladder "
                                          "extrapolates to is minus 13.733"))
        # The generic extrapolation clause is gone: the sharper statement of
        # the same failure replaced it rather than being said twice.
        self.assertNotIn("outside the range it measured", reason)
        self.assertIn("outside the credible range", reason)

    def test_a_value_inside_its_domain_says_nothing(self):
        # The supersonic cone extrapolates to 26.226 deg, which is a shock
        # angle a flow can have. The clause is silence, not a hedge.
        band = uq.eca_hoekstra_band([1800, 7200, 28800],
                                    [29.514, 28.113, 27.309], dim=2)
        self.assertIsNone(uq.impossible_extrapolation(
            band, quantity="the shock angle", why="which cannot be negative",
            floor=0.0, unit="deg"))

    def test_no_bound_given_means_no_opinion(self):
        band = self._band()
        self.assertIsNone(uq.impossible_extrapolation(
            band, quantity="the shock angle", why="which cannot be negative"))

    def test_the_holding_note_appears_only_when_more_than_one_guard_binds(self):
        two = self._band()
        self.assertIn("Two guards", uq.guards_holding_note(two))
        one = dict(two, guards_failed=[uq.GUARD_MONOTONE])
        self.assertIsNone(uq.guards_holding_note(one))
        three = dict(two, guards_failed=[uq.GUARD_ORDER_WINDOW,
                                         uq.GUARD_INCREMENT_TREND,
                                         uq.GUARD_EXTRAPOLATION])
        self.assertIn("Three guards", uq.guards_holding_note(three))

    def test_naming_every_guard_never_moves_a_verdict(self):
        # The whole change is about which reason is stated. Nothing it touches
        # may reach `conclusive` or the band the ladder is allowed to report.
        for cells, values, dim in (
                (self.CELLS, self.BETA, 2),
                ([2496, 5032, 8640], [0.1245, 0.1490, 0.1578], 3),
                ([10000, 80000, 640000],
                 DimensionalityDecidesOneThing._values(
                     [10000, 80000, 640000], 2.0), 3)):
            band = uq.eca_hoekstra_band(cells, values, dim=dim)
            self.assertEqual(uq.reportable_band(band),
                             band["band_abs"] if band["conclusive"] else None)


class StudyWritersCopyWhatTheyAreGiven(unittest.TestCase):
    def test_a_new_fit_field_reaches_the_stored_block_unaided(self):
        band = uq.eca_hoekstra_band([2496, 5032, 8640],
                                    [0.1245, 0.1490, 0.1578], dim=2)
        band["a_field_invented_after_every_writer_was_written"] = 7
        numerical = uq.study_numerical(band, value_working=0.1578)
        self.assertEqual(
            numerical["a_field_invented_after_every_writer_was_written"], 7)
        self.assertEqual(numerical["dim"], 2)
        self.assertEqual(numerical["not_conclusive_guard"],
                         uq.GUARD_EXTRAPOLATION)
        self.assertEqual(numerical["value_working"], 0.1578)

    def test_what_is_dropped_is_named_on_the_record(self):
        band = uq.eca_hoekstra_band([10000, 80000, 640000],
                                    [1.22, 0.62, 0.47], dim=3)
        numerical = uq.study_numerical(band)
        for key in uq.STUDY_NUMERICAL_DROPS:
            self.assertNotIn(key, numerical)
        self.assertEqual(numerical["dropped_from_fit"],
                         sorted(k for k in uq.STUDY_NUMERICAL_DROPS
                                if k in band))
        self.assertTrue(numerical["dropped_from_fit"])


if __name__ == "__main__":
    unittest.main()
