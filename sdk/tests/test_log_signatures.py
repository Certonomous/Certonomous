"""Tests for the pure log-signature detectors (Monitor Standard S6, S7, S9).

The wall-time envelope tests run against a fixture slice of the real
mega-batch ledger (``tests/fixtures/ledger_slice.jsonl``): 400 rows per
solver kind sampled evenly through the ledger, plus every real excursion row
(wall time near 16300 s), all copied verbatim.
"""

import sys
import unittest
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))

from chief_engineer.log_signatures import (
    classify_wall_time,
    detect_oscillatory_divergence,
    detect_residual_stall,
    percentile,
    wall_time_percentiles,
)

LEDGER_SLICE = Path(__file__).resolve().parent / "fixtures" / "ledger_slice.jsonl"


def oscillating_series(count: int, base: float, seed_amp: float, rate: float):
    """Residual plateau at ``base`` with alternating-sign deviation growing
    geometrically at ``rate`` per iteration."""
    return [base + seed_amp * (rate ** i) * (-1) ** i for i in range(count)]


class PercentileTests(unittest.TestCase):
    def test_single_value(self):
        self.assertEqual(percentile([7.0], 99), 7.0)

    def test_linear_interpolation(self):
        self.assertAlmostEqual(percentile([1.0, 2.0, 3.0, 4.0], 50), 2.5)
        self.assertAlmostEqual(percentile([1.0, 2.0, 3.0, 4.0], 100), 4.0)

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            percentile([], 50)


class ResidualStallTests(unittest.TestCase):
    def test_plateau_above_target_is_a_stall(self):
        finding = detect_residual_stall([1e-3] * 200, target=1e-6)
        self.assertIsNotNone(finding)
        self.assertEqual(finding["kind"], "residual-stall")
        self.assertEqual(finding["severity"], "flag")
        self.assertLess(finding["improvement"], 2.0)

    def test_converging_series_is_not_a_stall(self):
        series = [1e-2 * 0.99 ** i for i in range(200)]
        self.assertIsNone(detect_residual_stall(series, target=1e-8))

    def test_plateau_below_target_is_convergence_not_stall(self):
        self.assertIsNone(detect_residual_stall([1e-9] * 200, target=1e-6))

    def test_short_series_gives_no_judgment(self):
        self.assertIsNone(detect_residual_stall([1e-3] * 150, target=1e-6))

    def test_cap_far_away_defers_the_call(self):
        # Same plateau, but the run still has most of its iteration budget:
        # the rule waits until the cap approaches before naming a stall.
        self.assertIsNone(detect_residual_stall(
            [1e-3] * 200, target=1e-6, iteration_cap=1000, iterations_done=200))

    def test_cap_approaching_names_the_stall(self):
        finding = detect_residual_stall(
            [1e-3] * 200, target=1e-6, iteration_cap=250, iterations_done=210)
        self.assertIsNotNone(finding)


class OscillatoryDivergenceTests(unittest.TestCase):
    def test_growing_envelope_is_flagged(self):
        series = oscillating_series(60, 1e-2, 1e-4, 1.02)
        finding = detect_oscillatory_divergence(series)
        self.assertIsNotNone(finding)
        self.assertEqual(finding["kind"], "oscillatory-divergence")
        self.assertEqual(finding["severity"], "flag")
        self.assertGreaterEqual(finding["growth"], 1.25)

    def test_doubled_envelope_is_fatal(self):
        series = oscillating_series(60, 1e-2, 1e-4, 1.05)
        finding = detect_oscillatory_divergence(series)
        self.assertIsNotNone(finding)
        self.assertEqual(finding["severity"], "fatal")
        self.assertGreaterEqual(finding["growth"], 2.0)

    def test_decaying_oscillation_is_healthy(self):
        series = oscillating_series(60, 1e-2, 1e-3, 0.98)
        self.assertIsNone(detect_oscillatory_divergence(series))

    def test_monotone_convergence_is_healthy(self):
        series = [1e-2 * 0.97 ** i for i in range(60)]
        self.assertIsNone(detect_oscillatory_divergence(series))

    def test_flat_series_gives_no_judgment(self):
        self.assertIsNone(detect_oscillatory_divergence([1e-3] * 60))

    def test_short_series_gives_no_judgment(self):
        series = oscillating_series(30, 1e-2, 1e-4, 1.05)
        self.assertIsNone(detect_oscillatory_divergence(series))


class WallTimeEnvelopeTests(unittest.TestCase):
    """Envelope learning and classification against real ledger rows."""

    @classmethod
    def setUpClass(cls):
        cls.envelope = wall_time_percentiles(LEDGER_SLICE)

    def test_fixture_exists(self):
        self.assertTrue(LEDGER_SLICE.exists())

    def test_envelope_covers_every_solver_kind(self):
        self.assertEqual(
            sorted(self.envelope),
            ["openfoam-cylinder", "reduced-order", "vspaero-wing"])
        for stats in self.envelope.values():
            self.assertGreater(stats["p50"], 0.0)
            self.assertGreaterEqual(stats["p99"], stats["p50"])
            self.assertGreaterEqual(stats["count"], 400)

    def test_p99_is_not_dominated_by_the_excursions(self):
        # The three real ~16300 s rows sit far outside the 99th percentile
        # band for both solvers that recorded them.
        self.assertLess(self.envelope["openfoam-cylinder"]["p99"], 100.0)
        self.assertLess(self.envelope["vspaero-wing"]["p99"], 100.0)

    def test_result_is_memoized_per_file_version(self):
        self.assertIs(wall_time_percentiles(LEDGER_SLICE),
                      wall_time_percentiles(LEDGER_SLICE))

    def test_real_excursion_rows_classify_fatal(self):
        # These wall times are real ledger rows, recorded ok with no flag:
        # the exact failure the rule exists to catch.
        for kind, wall in [("openfoam-cylinder", 16310.017),
                           ("vspaero-wing", 16304.611)]:
            finding = classify_wall_time(kind, wall, self.envelope)
            self.assertIsNotNone(finding, kind)
            self.assertEqual(finding["kind"], "wall-time-excursion")
            self.assertEqual(finding["severity"], "fatal")
            self.assertGreater(finding["multiple"], 100.0)

    def test_ordinary_wall_times_pass(self):
        self.assertIsNone(
            classify_wall_time("openfoam-cylinder", 4.1, self.envelope))
        self.assertIsNone(
            classify_wall_time("vspaero-wing", 6.0, self.envelope))

    def test_unknown_kind_gives_no_judgment(self):
        self.assertIsNone(
            classify_wall_time("unheard-of-solver", 1e6, self.envelope))

    def test_thin_evidence_gives_no_judgment(self):
        thin = {"k": {"p50": 1.0, "p99": 2.0, "count": 5.0}}
        self.assertIsNone(classify_wall_time("k", 1e6, thin))

    def test_flag_band_between_thresholds(self):
        envelope = {"k": {"p50": 1.0, "p99": 2.0, "count": 100.0}}
        self.assertIsNone(classify_wall_time("k", 30.0, envelope))    # 15x
        flagged = classify_wall_time("k", 50.0, envelope)             # 25x
        self.assertEqual(flagged["severity"], "flag")
        fatal = classify_wall_time("k", 300.0, envelope)              # 150x
        self.assertEqual(fatal["severity"], "fatal")

    def test_threshold_multiple_is_configurable(self):
        envelope = {"k": {"p50": 1.0, "p99": 2.0, "count": 100.0}}
        self.assertIsNone(
            classify_wall_time("k", 50.0, envelope, flag_multiple=30.0))
        self.assertIsNotNone(
            classify_wall_time("k", 50.0, envelope, flag_multiple=10.0))

    def test_missing_ledger_yields_empty_envelope(self):
        self.assertEqual(wall_time_percentiles(LEDGER_SLICE / "nope"), {})
        self.assertIsNone(classify_wall_time(
            "openfoam-cylinder", 1e6, ledger_path=LEDGER_SLICE / "nope"))


if __name__ == "__main__":
    unittest.main()
