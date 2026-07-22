import sys
import unittest
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))

from chief_engineer.head_engineer import (
    LogMonitor,
    envelope_statistics,
    parse_coefficient_history,
)


class LogMonitorTests(unittest.TestCase):
    def test_nan_and_fpe_are_fatal(self):
        monitor = LogMonitor()
        monitor.feed("simpleFoam", "smoothSolver:  Solving for Ux, Initial residual = nan, Final residual = nan")
        monitor.feed("simpleFoam", "Foam::sigFpe::sigHandler(int)")
        summary = monitor.summary()
        self.assertTrue(summary["fatal"])
        self.assertGreaterEqual(summary["anomalies"], 2)

    def test_fpe_trapping_banner_is_not_an_anomaly(self):
        monitor = LogMonitor()
        monitor.feed("blockMesh", "trapFpe: Floating point exception trapping - enabled (FOAM_SIGFPE).")
        self.assertEqual(monitor.summary()["anomalies"], 0)

    def _residuals(self, monitor, values, field="p"):
        for value in values:
            monitor.feed("simpleFoam",
                         f"Solving for {field}, Initial residual = {value}, "
                         f"Final residual = 1e-9")

    def test_sustained_rising_residual_is_flagged(self):
        monitor = LogMonitor()
        # A settled solve, then a genuine departure: three rising values well
        # above the recent median is what divergence actually looks like.
        self._residuals(monitor, [1e-5] * 30)
        self._residuals(monitor, [1e-3, 5e-3, 2e-2])
        self.assertIn("residual-spike", [a.kind for a in monitor.anomalies])

    def test_single_wobble_in_a_converging_solve_is_not_flagged(self):
        monitor = LogMonitor()
        # Comparing against the all-time minimum used to fire here on every
        # ordinary bump, burying real findings under hundreds of alerts.
        self._residuals(monitor, [1e-4 / (i + 1) for i in range(40)])
        self._residuals(monitor, [1e-3])
        self.assertEqual([a.kind for a in monitor.anomalies], [])

    def test_repeated_conditions_are_counted_not_repeated(self):
        monitor = LogMonitor()
        surfaced = []
        monitor.on_anomaly = lambda anomaly: surfaced.append(anomaly.kind)
        for _ in range(50):
            monitor.feed("simpleFoam", "bounding k, min: -1 max: 2 average: 0.5")
        summary = monitor.summary()
        self.assertEqual(summary["anomalies"], 50)
        self.assertLessEqual(len(surfaced), LogMonitor.REPORT_LIMIT)
        self.assertEqual(summary["suppressed"]["bounding"],
                         50 - LogMonitor.REPORT_LIMIT)

    def test_fatal_anomalies_are_never_suppressed(self):
        monitor = LogMonitor()
        surfaced = []
        monitor.on_anomaly = lambda anomaly: surfaced.append(anomaly.kind)
        for _ in range(10):
            monitor.feed("simpleFoam", "Foam::sigFpe::sigHandler(int)")
        self.assertEqual(len(surfaced), 10)

    def test_downward_residuals_raise_nothing(self):
        monitor = LogMonitor()
        for i in range(40):
            monitor.feed("simpleFoam",
                         f"Solving for Ux, Initial residual = {1e-2 / (i + 1)}, Final residual = 1e-8")
        self.assertEqual(monitor.summary()["anomalies"], 0)

    def test_novel_mode_collects_first_seen_warnings(self):
        monitor = LogMonitor(novel=True)
        monitor.feed("snappyHexMesh", "--> FOAM Warning : displacement of 12 points exceeded")
        monitor.feed("snappyHexMesh", "--> FOAM Warning : displacement of 15 points exceeded")
        summary = monitor.summary()
        self.assertEqual(len(summary["novel_observations"]), 1)  # deduped by pattern


class StatisticsTests(unittest.TestCase):
    HISTORY = (
        "# Time Cd Cs Cl\n"
        + "\n".join(f"{i} {0.4 + 0.001 * (i % 3)} 0 {0.1}" for i in range(1, 101))
    )

    def test_history_parser_returns_full_series(self):
        history = parse_coefficient_history(self.HISTORY)
        self.assertEqual(len(history["Time"]), 100)
        self.assertEqual(len(history["Cd"]), 100)

    def test_envelope_statistics_window(self):
        stats = envelope_statistics([1.0] * 80 + [2.0] * 20)
        self.assertAlmostEqual(stats["value"], 2.0)
        self.assertEqual(stats["window"], 20)
        self.assertLessEqual(stats["lo"], stats["value"])
        self.assertGreaterEqual(stats["hi"], stats["value"])


if __name__ == "__main__":
    unittest.main()
