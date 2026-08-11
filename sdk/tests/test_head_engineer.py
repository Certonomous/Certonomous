import sys
import unittest
from types import SimpleNamespace
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))

from chief_engineer.head_engineer import (
    CASE_CODE_DIRECTIVES,
    CASE_CODE_PATTERN,
    HeadEngineer,
    LogMonitor,
    VETTED_SYSTEM_OPERATION_CASES,
    envelope_statistics,
    parse_coefficient_history,
    vetted_case_reason,
)
from chief_engineer.log_signatures import SEVERITY_CONFIGURATION_RISK


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
    """Monitor Standard S6/S8/S9 wired into the LogMonitor hooks.

    S7 was wired in here too until 2026-08-01, when it was withdrawn. What
    remains of it is one test asserting the monitor can no longer raise it.
    """

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

    def test_withdrawn_s7_raises_nothing_however_the_residual_oscillates(self):
        # S7 is WITHDRAWN (ruling R1, conflict C-2 option B). These are the
        # exact series that used to make it flag and then go fatal: a residual
        # plateau at 1e-2 with an alternating deviation growing 2 percent and
        # then 5 percent per iteration. The monitor must now raise nothing of
        # that kind on either, with or without a residual target.
        for rate in (1.02, 1.05):
            for target in (1e-6, None):
                with self.subTest(rate=rate, residual_target=target):
                    monitor = LogMonitor(residual_target=target)
                    series = [1e-2 + 1e-4 * (rate ** i) * (-1) ** i
                              for i in range(60)]
                    self._residuals(monitor, series)
                    self.assertNotIn("oscillatory-divergence",
                                     [a.kind for a in monitor.anomalies])
                    self.assertFalse(monitor.summary()["fatal"])

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
        # healthy and finished, and S7 called it divergent five times before
        # it was withdrawn.
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

    def test_the_monitor_default_is_the_approved_threshold(self):
        # The approved rule says 10 times the running 99th percentile. This
        # entry point kept a literal 20.0 after the shared constant was
        # corrected, so a caller taking the default judged on a threshold
        # nobody approved. The default is now the constant itself.
        import inspect

        from chief_engineer.log_signatures import FLAG_MULTIPLE

        default = inspect.signature(
            LogMonitor.check_wall_time).parameters["flag_multiple"].default
        self.assertEqual(default, FLAG_MULTIPLE)
        self.assertEqual(FLAG_MULTIPLE, 10.0)

    def test_a_run_between_the_two_thresholds_is_seen_by_default(self):
        # 15x the p99 is an excursion under the approved rule and was invisible
        # under the 20x default this test guards against.
        monitor = LogMonitor()
        envelope = {"k": {"p50": 1.0, "p99": 2.0, "count": 500.0}}
        finding = monitor.check_wall_time("solve", "k", 30.0,
                                          envelope=envelope)
        self.assertIsNotNone(finding)
        self.assertEqual(finding["severity"], "flag")


class DivergenceBehindAConvergedResidualTests(unittest.TestCase):
    """Monitor Standard S10, against the run it was designed on.

    The Ahmed body primal on the 45760-cell mesh ran to its iteration cap,
    printed a drag coefficient, and that number was published and later
    withdrawn: the turbulence field had diverged while the number the log
    reports as its residual read as converged. The same case on its coarse
    mesh is healthy, so the two logs are a matched pair and the rules must
    separate them.
    """

    LOGS = (Path(__file__).resolve().parents[2] / "demo-output" / "website"
            / "dafoam" / "ladder-a" / "logs_A4")
    WITHDRAWN = LOGS / "A4_fine_primal_par4.log"
    HEALTHY = LOGS / "A4_coarse_primal_par4.log"

    def _run(self, path):
        monitor = LogMonitor()
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                monitor.feed("DASimpleFoam", line)
        return monitor

    def test_the_withdrawn_run_is_caught_and_is_fatal(self):
        self.assertTrue(self.WITHDRAWN.exists())
        monitor = self._run(self.WITHDRAWN)
        kinds = monitor.summary()["by_kind"]
        # All three branches fire, and the run is fatal, so no quantity
        # computed from that state can be presented as evidence.
        self.assertGreaterEqual(kinds.get("ceiling-clip", 0), 1)
        self.assertEqual(kinds.get("normalisation-collapse", 0), 1)
        self.assertEqual(kinds.get("residual-norm-contradiction", 0), 1)
        self.assertTrue(monitor.summary()["fatal"])

    def test_the_healthy_solve_of_the_same_case_stays_quiet(self):
        self.assertTrue(self.HEALTHY.exists())
        monitor = self._run(self.HEALTHY)
        self.assertEqual(monitor.summary()["by_kind"], {})
        self.assertFalse(monitor.summary()["fatal"])

    def test_none_of_the_older_rules_saw_the_withdrawn_run(self):
        # This is why S10 was needed. The rules that existed before it are
        # silent on this log: no NaN, no exception, no spike, and the residual
        # is far BELOW its target rather than stalled above it.
        monitor = self._run(self.WITHDRAWN)
        for kind in ("nan", "fpe", "residual-spike", "residual-stall",
                     "courant-excursion"):
            self.assertNotIn(kind, monitor.summary()["by_kind"], kind)

    def test_the_collapsed_field_is_named_with_what_it_did(self):
        monitor = self._run(self.WITHDRAWN)
        collapse = [a for a in monitor.anomalies
                    if a.kind == "normalisation-collapse"][0]
        self.assertEqual(collapse.severity, "fatal")
        self.assertIn("omega", collapse.detail)
        clip = [a for a in monitor.anomalies if a.kind == "ceiling-clip"][0]
        self.assertIn("omega", clip.detail)
        self.assertEqual(clip.severity, "fatal")

    def test_a_floor_clip_stays_the_ordinary_watch_it_always_was(self):
        # Turbulence quantities are held off zero on healthy runs everywhere.
        monitor = LogMonitor()
        monitor.feed("DASimpleFoam", "Bounding k>1e-16")
        monitor.feed("simpleFoam", "bounding epsilon, min: -1 max: 2 average: 1")
        kinds = monitor.summary()["by_kind"]
        self.assertEqual(kinds, {"bounding": 2})
        self.assertFalse(monitor.summary()["fatal"])

    def test_the_solver_total_is_not_double_counted(self):
        monitor = LogMonitor()
        monitor.feed("DASimpleFoam", "U Residual Norm2: 1.0")
        monitor.feed("DASimpleFoam", "Total Residual Norm2: 1e+30")
        self.assertEqual(monitor.summary()["by_kind"], {})


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


class SystemOperationsTests(unittest.TestCase):
    """S11: allowSystemOperations is a configuration risk, and staging refuses
    an unvetted case that could use it."""

    # The exact text each build prints. v2606 on the host wraps it in a
    # warning; the older OpenFOAM in the DAFoam container does not, which is
    # why S11 cannot ride on the first-seen-warning rule.
    HOST_LINE = ("--> FOAM Warning : allowSystemOperations : Allowing "
                 "user-supplied system call operations.")
    CONTAINER_LINE = ("allowSystemOperations : Allowing user-supplied system "
                      "call operations")
    OFF_LINE = ("allowSystemOperations : Disallowing user-supplied system "
                "call operations")

    def test_recorded_on_every_run_not_only_novel_mode(self):
        for line in (self.HOST_LINE, self.CONTAINER_LINE):
            with self.subTest(line=line):
                monitor = LogMonitor(novel=False)
                monitor.feed("simpleFoam", line)
                risks = monitor.summary()["configuration_risk"]
                self.assertEqual(len(risks), 1)
                self.assertEqual(risks[0]["severity"],
                                 SEVERITY_CONFIGURATION_RISK)

    def test_switch_off_records_nothing(self):
        monitor = LogMonitor(novel=True)
        monitor.feed("simpleFoam", self.OFF_LINE)
        self.assertEqual(monitor.summary()["configuration_risk"], [])

    def test_never_fatal_and_never_an_anomaly(self):
        monitor = LogMonitor(novel=False)
        monitor.feed("simpleFoam", self.HOST_LINE)
        summary = monitor.summary()
        # The solve is untouched, so the anomaly count, the by-kind table and
        # the fatal verdict must all be exactly what they were.
        self.assertFalse(summary["fatal"])
        self.assertEqual(summary["anomalies"], 0)
        self.assertEqual(summary["by_kind"], {})

    def test_novel_mode_bullet_is_unchanged_but_carries_the_severity(self):
        seen = []
        monitor = LogMonitor(novel=True, on_anomaly=seen.append)
        monitor.feed("simpleFoam", self.HOST_LINE)
        self.assertEqual(len(seen), 1)
        self.assertEqual(seen[0].kind, "novel-warning")   # transcript unchanged
        self.assertEqual(seen[0].severity, SEVERITY_CONFIGURATION_RISK)

    def test_repeated_lines_are_one_finding(self):
        monitor = LogMonitor()
        for _ in range(5):
            monitor.feed("simpleFoam", self.CONTAINER_LINE)
        self.assertEqual(len(monitor.summary()["configuration_risk"]), 1)

    def test_case_code_patterns_agree(self):
        """The grep spelling and the Python spelling are one rule."""
        import re
        import subprocess
        corpus = {
            'aref #calc "pow($a, 0.5)";': True,
            "value #codeStream { code #{ os << 1; #};":  True,
            "    type            codedFixedValue;": True,
            "    type            codedMixedValue;": True,
            "    type            codedFunctionObject;": True,
            "    type coded;": True,
            "    functions { sc { type systemCall; } }": True,
            # #eval is parsed by the expression evaluator, never compiled, so
            # it is not gated by the switch and must not be caught here.
            'aref #eval "pow($a, 0.5)";': False,
            "    type            fixedValue;": False,
            "    #include \"../caseDef\"": False,
            "// calculated variables": False,
        }
        for text, expected in corpus.items():
            with self.subTest(text=text):
                self.assertEqual(bool(CASE_CODE_PATTERN.search(text)), expected)
                grep = subprocess.run(
                    ["grep", "-qE", CASE_CODE_DIRECTIVES],
                    input=text, text=True)
                self.assertEqual(grep.returncode == 0, expected)

    def test_unvetted_case_carrying_code_is_refused(self):
        engineer = HeadEngineer.__new__(HeadEngineer)
        with self.assertRaises(RuntimeError) as caught:
            engineer.assert_case_code_vetted(
                "/tmp/a-case-someone-emailed-us",
                ["/tmp/a-case-someone-emailed-us/system/controlDict"])
        self.assertIn("external source", str(caught.exception))

    def test_case_without_code_passes_whatever_the_host_allows(self):
        engineer = HeadEngineer.__new__(HeadEngineer)
        engineer.assert_case_code_vetted("/tmp/a-case-someone-emailed-us", [])

    def test_vetted_case_passes_and_records_its_reason(self):
        engineer = HeadEngineer.__new__(HeadEngineer)
        template = ("/home/ubuntu/Certonomous/demo-output/website/dafoam/"
                    "f6a_nasa_hump/case_template")
        engineer.assert_case_code_vetted(template, [f"{template}/caseDef"])
        self.assertIn("act 7", vetted_case_reason(template))

    def test_every_vetted_entry_states_a_reason(self):
        self.assertTrue(VETTED_SYSTEM_OPERATION_CASES)
        for case, reason in VETTED_SYSTEM_OPERATION_CASES.items():
            with self.subTest(case=case):
                self.assertGreater(len(reason.split()), 5, case)


if __name__ == "__main__":
    unittest.main()


REACHABLE_FVSOLUTION = """solvers
{
    p { solver GAMG; tolerance 1e-08; }
    U { solver PBiCG; tolerance 1e-09; }
}
SIMPLE
{
    residualControl { p 1e-4; U 1e-5; }
}
"""

SENTINEL_FVSOLUTION = """solvers
{
    p { solver GAMG; tolerance 1e-12; }
}
SIMPLE
{
    residualControl { p 1e-15;//1e-4; }
}
"""


class S6ArmingTests(unittest.TestCase):
    """S6 is armed from the case's OWN residual controls, and the sentinel
    class is excluded by construction.

    WHY THIS EXISTS. S6 could not fire on any production run: it returns early
    without a `residual_target` and `HeadEngineer.__init__` had no parameter
    by which one could be supplied, while the standard said both approved
    proposals were "in force". Pre-registered in
    `campaign/S6_WIRING_PREREGISTRATION.md` before any of this code was
    written.
    """

    def _engineer(self, fvsolution: str):
        from chief_engineer.head_engineer import HeadEngineer
        eng = HeadEngineer.__new__(HeadEngineer)
        eng.remote_case = "/run/case"
        eng.monitor = LogMonitor()
        eng.on_event = None
        eng._wsl = lambda cmd, timeout=600.0: SimpleNamespace(
            stdout=fvsolution if "fvSolution" in cmd else "", stderr="")
        return eng

    def test_the_target_comes_from_the_cases_own_fvsolution(self):
        eng = self._engineer(REACHABLE_FVSOLUTION)
        rec = eng.arm_residual_gate()
        self.assertTrue(rec["armed"])
        # The LOOSEST reachable target: the most conservative gate.
        self.assertEqual(rec["target"], 1e-4)
        self.assertEqual(eng.monitor.residual_target, 1e-4)

    def test_a_target_below_its_own_solver_tolerance_is_excluded(self):
        """Condition 2, by construction: the outer residual cannot be driven
        below what the inner solve resolves, so gating on such a target would
        measure the declaration rather than the solve."""
        eng = self._engineer(SENTINEL_FVSOLUTION)
        rec = eng.arm_residual_gate()
        self.assertFalse(rec["armed"])
        self.assertIsNone(eng.monitor.residual_target)
        self.assertIn("p", rec["excluded_unreachable"])
        self.assertEqual(rec["excluded_unreachable"]["p"],
                         {"target": 1e-15, "solver_tolerance": 1e-12})

    def test_the_live_value_is_read_not_the_commented_out_one(self):
        """The motivating case is literally `p 1e-15;//1e-4;` -- a real target
        commented out and replaced. A parser ignoring comments would read the
        DEAD value here and the live one elsewhere."""
        from chief_engineer.head_engineer import _residual_controls
        self.assertEqual(_residual_controls(SENTINEL_FVSOLUTION), {"p": 1e-15})

    def test_a_missing_fvsolution_leaves_s6_disarmed_and_says_so(self):
        eng = self._engineer("")
        rec = eng.arm_residual_gate()
        self.assertFalse(rec["armed"])
        self.assertIsNone(eng.monitor.residual_target)
        self.assertIn("disarmed", rec["reason"])

    def test_a_field_with_no_declared_tolerance_is_not_gated_on(self):
        """Reachability cannot be established, so it is not asserted."""
        eng = self._engineer("SIMPLE { residualControl { p 1e-4; } }")
        rec = eng.arm_residual_gate()
        self.assertFalse(rec["armed"])

    def test_arming_makes_s6_actually_able_to_fire(self):
        """The point of the whole exercise: before this, the rule returned
        early on every production run."""
        eng = self._engineer(REACHABLE_FVSOLUTION)
        self.assertIsNone(eng.monitor.residual_target)
        eng.arm_residual_gate()
        self.assertIsNotNone(eng.monitor.residual_target)


class S6ArmedThroughStagingTests(unittest.TestCase):
    """The gate must get ARMED, not merely work when armed.

    WHY THIS EXISTS. Every other S6 test builds its engineer with
    `HeadEngineer.__new__` and calls `arm_residual_gate` directly. Those prove
    the gate works when armed and can say NOTHING about whether it gets armed
    on any real path -- a test that reaches past the constructor cannot see a
    constructor that never calls the thing. That blind spot let a false
    coverage sentence stand in `MONITOR_STANDARD.md` for six hours: it claimed
    S6 fired on the Ahmed act, whose runner never calls `stage_case` and so
    never arms the gate. This test goes through the real staging path.
    """

    FVSOLUTION = ("solvers { p { solver GAMG; tolerance 1e-08; } }\n"
                  "SIMPLE { residualControl { p 1e-4; } }\n")

    def _engineer(self, tmp):
        from chief_engineer.head_engineer import HeadEngineer
        eng = HeadEngineer("s6-staging", tmp)
        calls = []

        def fake_wsl(command, timeout=600.0):
            calls.append(command)
            if "fvSolution" in command:
                return SimpleNamespace(stdout=self.FVSOLUTION, stderr="")
            if "echo STAGED" in command:
                return SimpleNamespace(stdout="STAGED\n", stderr="")
            return SimpleNamespace(stdout="", stderr="")

        eng._wsl = fake_wsl
        return eng, calls

    def test_staging_a_case_arms_s6_without_the_caller_asking(self):
        import tempfile, shutil
        tmp = Path(tempfile.mkdtemp(prefix="s6-stage-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        eng, _ = self._engineer(tmp)
        self.assertIsNone(eng.monitor.residual_target,
                          "a fresh engineer must start with S6 disarmed")
        eng.stage_case("/tutorials/incompressible/simpleFoam/motorBike")
        self.assertEqual(eng.monitor.residual_target, 1e-4,
                         "stage_case did not arm S6 -- the gate is reachable "
                         "only through this path, so a runner that stages a "
                         "case another way gets no S6 at all")

    def test_the_gate_is_reachable_from_exactly_one_production_path(self):
        """Pins the fact the corrected coverage sentence rests on. If a second
        arming site appears, the enumeration in MONITOR_STANDARD.md is stale
        and this fails until it is updated."""
        import inspect
        from chief_engineer import head_engineer as he
        src = inspect.getsource(he)
        sites = [ln.strip() for ln in src.splitlines()
                 if "arm_residual_gate()" in ln and "def " not in ln]
        self.assertEqual(len(sites), 1, f"expected one arming site, got {sites}")
        self.assertIn("arm_residual_gate()",
                      inspect.getsource(he.HeadEngineer.stage_case))
