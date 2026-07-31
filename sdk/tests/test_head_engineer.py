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


class MonitorStandardRuleTests(unittest.TestCase):
    """Monitor Standard S6/S7/S9 wired into the LogMonitor hooks."""

    LEDGER_SLICE = Path(__file__).resolve().parent / "fixtures" / "ledger_slice.jsonl"

    def _residuals(self, monitor, values, field="p"):
        for value in values:
            monitor.feed("simpleFoam",
                         f"Solving for {field}, Initial residual = {value}, "
                         f"Final residual = 1e-9")

    def test_stall_is_raised_once_per_field(self):
        monitor = LogMonitor(residual_target=1e-6, iteration_cap=250)
        self._residuals(monitor, [1e-3] * 220)
        kinds = [a.kind for a in monitor.anomalies]
        self.assertEqual(kinds.count("residual-stall"), 1)
        self.assertFalse(monitor.summary()["fatal"])  # a stall flags, never kills

    def test_stall_needs_a_residual_target(self):
        # Without the residualControl target a plateau at the solver floor is
        # indistinguishable from a stall, so the check stays off by default.
        monitor = LogMonitor()
        self._residuals(monitor, [1e-3] * 220)
        self.assertNotIn("residual-stall", [a.kind for a in monitor.anomalies])

    def test_growing_oscillation_is_flagged(self):
        monitor = LogMonitor()
        series = [1e-2 + 1e-4 * (1.02 ** i) * (-1) ** i for i in range(60)]
        self._residuals(monitor, series)
        oscillation = [a for a in monitor.anomalies
                       if a.kind == "oscillatory-divergence"]
        self.assertTrue(oscillation)
        self.assertFalse(monitor.summary()["fatal"])

    def test_doubling_oscillation_envelope_is_fatal(self):
        monitor = LogMonitor()
        series = [1e-2 + 1e-4 * (1.05 ** i) * (-1) ** i for i in range(60)]
        self._residuals(monitor, series)
        severities = {a.severity for a in monitor.anomalies
                      if a.kind == "oscillatory-divergence"}
        self.assertIn("fatal", severities)
        self.assertTrue(monitor.summary()["fatal"])

    def _courant(self, monitor, values, *, delta_t=None):
        for index, value in enumerate(values):
            if delta_t is not None:
                monitor.feed("pimpleFoam", f"deltaT = {delta_t(index)}")
            monitor.feed("pimpleFoam",
                         f"Courant Number mean: {value / 10:.6f} max: {value}")

    def test_courant_excursion_is_flagged_once(self):
        monitor = LogMonitor(courant_limit=1.5)
        self._courant(monitor, [0.9] * 20 + [3.0] * 20)
        kinds = [a.kind for a in monitor.anomalies]
        self.assertEqual(kinds.count("courant-excursion"), 1)

    def test_courant_needs_a_case_limit(self):
        # A reported maximum means nothing without the limit it was asked to
        # respect, so the check stays off by default.
        monitor = LogMonitor()
        self._courant(monitor, [9.9] * 40)
        self.assertNotIn("courant-excursion",
                         [a.kind for a in monitor.anomalies])

    def test_archived_transient_run_raises_nothing(self):
        # The lab's own archived transient runs are healthy and must stay so.
        monitor = LogMonitor(courant_limit=1.5)
        log = (Path(__file__).resolve().parents[2] / "demo-output" / "website"
               / "mega-batch" / "work" / "cylinder-unsteady")
        paths = sorted(log.glob("*/log.pimpleFoam"))
        self.assertTrue(paths)
        with open(paths[0], encoding="utf-8", errors="replace") as handle:
            for line in handle:
                monitor.feed("pimpleFoam", line)
        self.assertNotIn("courant-excursion",
                         [a.kind for a in monitor.anomalies])
        # The steady-solve rules must stay silent here too: this run is
        # healthy and finished, and S7 used to call it divergent five times.
        self.assertEqual(monitor.summary()["by_kind"], {})

    def test_steady_rules_are_scoped_off_once_a_run_is_transient(self):
        monitor = LogMonitor(residual_target=1e-6, iteration_cap=250)
        monitor.feed("pimpleFoam", "Courant Number mean: 0.01 max: 0.4")
        self._residuals(monitor, [1e-3] * 220)
        self.assertNotIn("residual-stall",
                         [a.kind for a in monitor.anomalies])

    def test_wall_time_excursion_against_real_ledger_rows(self):
        # 16310.017 s is a real ledger row, recorded ok with no flag: over
        # 800x the 99th percentile for its solver kind.
        monitor = LogMonitor()
        finding = monitor.check_wall_time(
            "solve", "openfoam-cylinder", 16310.017,
            ledger_path=self.LEDGER_SLICE)
        self.assertIsNotNone(finding)
        self.assertEqual(finding["severity"], "fatal")
        self.assertGreater(finding["multiple"], 100.0)
        self.assertIn("wall-time-excursion", [a.kind for a in monitor.anomalies])
        self.assertTrue(monitor.summary()["fatal"])

    def test_ordinary_wall_time_raises_nothing(self):
        monitor = LogMonitor()
        finding = monitor.check_wall_time(
            "solve", "openfoam-cylinder", 4.1, ledger_path=self.LEDGER_SLICE)
        self.assertIsNone(finding)
        self.assertEqual(monitor.summary()["anomalies"], 0)


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
