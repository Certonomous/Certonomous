"""Tests for the pure log-signature detectors (Monitor Standard S6, S7, S9).

The wall-time envelope tests run against a fixture slice of the real
mega-batch ledger (``tests/fixtures/ledger_slice.jsonl``): 400 rows per
solver kind sampled evenly through the ledger, plus every real excursion row
(wall time near 16300 s), all copied verbatim.
"""

import re
import sys
import unittest
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))

from chief_engineer.log_signatures import (
    COURANT_TOLERANCE,
    DEAD_FIELD_FLOOR,
    FATAL_MULTIPLE,
    FLAG_MULTIPLE,
    RESIDUAL_NORM_ORDERS,
    classify_bound_line,
    classify_wall_time,
    detect_ceiling_clip,
    detect_courant_excursion,
    detect_normalisation_collapse,
    detect_oscillatory_divergence,
    detect_residual_norm_contradiction,
    detect_residual_stall,
    percentile,
    wall_time_percentiles,
    wall_time_record_field,
)

LEDGER_SLICE = Path(__file__).resolve().parent / "fixtures" / "ledger_slice.jsonl"

# The lab's archived transient runs, used as the healthy-baseline evidence for
# S8. Four unsteady cylinder cases, requested maximum Courant number 1.5.
TRANSIENT_LOGS = sorted(
    (Path(__file__).resolve().parents[2] / "demo-output" / "website"
     / "mega-batch" / "work" / "cylinder-unsteady").glob(
        "*/log.pimpleFoam"))
TRANSIENT_LIMIT = 1.5
_COURANT_LINE = re.compile(
    r"Courant Number mean: ([0-9.eE+-]+) max: ([0-9.eE+-]+)")


def archived_max_courant(path: Path) -> list[float]:
    """Every reported per-step maximum Courant number in an archived log."""
    out = []
    with open(path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            match = _COURANT_LINE.search(line)
            if match:
                out.append(float(match.group(2)))
    return out


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


class CourantExcursionTests(unittest.TestCase):
    def test_run_inside_its_limit_is_healthy(self):
        self.assertIsNone(detect_courant_excursion(
            [0.4, 0.6, 0.9, 1.1, 0.8], limit=1.5))

    def test_run_past_its_limit_is_flagged(self):
        finding = detect_courant_excursion([0.5, 1.2, 2.4, 1.1], limit=1.5)
        self.assertIsNotNone(finding)
        self.assertEqual(finding["kind"], "courant-excursion")
        self.assertEqual(finding["severity"], "flag")
        self.assertAlmostEqual(finding["peak"], 2.4)
        self.assertEqual(finding["exceedances"], 1)

    def test_adaptive_overshoot_inside_tolerance_is_healthy(self):
        # An adaptive stepper sets the step from the previous step's Courant
        # number, so a small overshoot of the target is the stepper working.
        self.assertIsNone(detect_courant_excursion(
            [1.5 * (1.0 + COURANT_TOLERANCE / 2)] * 40, limit=1.5))

    def test_monotone_growth_at_a_fixed_step_is_fatal(self):
        series = [0.1 + 0.01 * i for i in range(40)]
        finding = detect_courant_excursion(
            series, limit=1.5, fixed_time_step=True)
        self.assertIsNotNone(finding)
        self.assertEqual(finding["severity"], "fatal")
        self.assertIn("monotonic", finding["reason"])

    def test_monotone_growth_is_not_judged_when_the_step_adapts(self):
        series = [0.1 + 0.01 * i for i in range(40)]
        self.assertIsNone(detect_courant_excursion(
            series, limit=1.5, fixed_time_step=False))

    def test_no_limit_means_no_judgment(self):
        self.assertIsNone(detect_courant_excursion([9.9] * 40, limit=0.0))
        self.assertIsNone(detect_courant_excursion([], limit=1.5))


class CourantAgainstArchivedRunsTests(unittest.TestCase):
    """Offline evidence for S8 against the lab's own archived transient runs.

    The Monitor Standard requires a new rule to be measured against archived
    logs before adoption. These four runs are the only real transient data the
    lab holds, they all finished, and the rule must call none of them an
    excursion.
    """

    def test_the_archive_is_present(self):
        self.assertTrue(TRANSIENT_LOGS, "archived transient logs are missing")

    def test_no_healthy_archived_run_is_called_an_excursion(self):
        for path in TRANSIENT_LOGS:
            series = archived_max_courant(path)
            self.assertGreater(len(series), 100, path.parent.name)
            # Every one of these runs adapts its time step, so the monotone
            # branch is inapplicable by construction; the limit branch must
            # stay silent on its own.
            self.assertIsNone(
                detect_courant_excursion(series, limit=TRANSIENT_LIMIT),
                f"{path.parent.name} was wrongly called an excursion")

    def test_a_strict_comparison_would_have_flagged_every_one(self):
        # Why the tolerance exists, measured rather than asserted: a rule
        # written as a strict comparison against the limit fires on a large
        # fraction of the steps of every healthy run in the archive.
        for path in TRANSIENT_LOGS:
            series = archived_max_courant(path)
            strict = sum(1 for value in series if value > TRANSIENT_LIMIT)
            self.assertGreater(strict / len(series), 0.2, path.parent.name)
            self.assertIsNotNone(
                detect_courant_excursion(
                    series, limit=TRANSIENT_LIMIT, tolerance=0.0),
                path.parent.name)

    def test_healthy_overshoot_stays_well_inside_the_tolerance(self):
        for path in TRANSIENT_LOGS:
            series = archived_max_courant(path)
            overshoot = max(series) / TRANSIENT_LIMIT - 1.0
            self.assertLess(overshoot, COURANT_TOLERANCE / 2, path.parent.name)

    def test_a_real_excursion_on_top_of_an_archived_run_is_caught(self):
        # The rule has to stay sensitive, not merely quiet: the same series
        # with one genuinely over-limit step is an excursion.
        series = archived_max_courant(TRANSIENT_LOGS[0]) + [4.0]
        finding = detect_courant_excursion(series, limit=TRANSIENT_LIMIT)
        self.assertIsNotNone(finding)
        self.assertEqual(finding["severity"], "flag")


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
        self.assertIsNone(classify_wall_time("k", 16.0, envelope))    # 8x
        flagged = classify_wall_time("k", 30.0, envelope)             # 15x
        self.assertEqual(flagged["severity"], "flag")
        fatal = classify_wall_time("k", 300.0, envelope)              # 150x
        self.assertEqual(fatal["severity"], "fatal")

    def test_default_thresholds_are_the_approved_ones(self):
        # The owner approved "beyond 10 times ... stop and investigate beyond
        # 100 times" on r1-monitor-walltime-rule. The defaults are those
        # numbers, not a house variant of them.
        self.assertEqual(FLAG_MULTIPLE, 10.0)
        self.assertEqual(FATAL_MULTIPLE, 100.0)
        envelope = {"k": {"p50": 1.0, "p99": 2.0, "count": 100.0}}
        self.assertIsNone(classify_wall_time("k", 20.0, envelope))     # 10x
        self.assertIsNotNone(classify_wall_time("k", 22.0, envelope))  # 11x

    def test_excursion_becomes_a_named_record_field(self):
        # The approved rule requires the excursion to survive on the record so
        # fleet learning can separate solver cost from infrastructure stalls.
        field = wall_time_record_field(
            "openfoam-cylinder", 16310.017, self.envelope)
        self.assertIsNotNone(field)
        self.assertEqual(field["severity"], "fatal")
        self.assertGreater(field["multiple"], 100.0)
        self.assertGreater(field["envelope_samples"], 0)
        self.assertGreater(field["p99_seconds"], 0.0)

    def test_ordinary_run_carries_no_field_at_all(self):
        # An ordinary row must stay exactly as it was: no empty field, no null.
        self.assertIsNone(
            wall_time_record_field("openfoam-cylinder", 4.1, self.envelope))

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


class BoundLineTests(unittest.TestCase):
    """S10a: which end of its range the field was held at is the finding."""

    def test_a_ceiling_clip_is_read_as_a_ceiling(self):
        bound = classify_bound_line("Bounding omega<1e+16")
        self.assertEqual(bound["field"], "omega")
        self.assertEqual(bound["direction"], "ceiling")
        self.assertEqual(bound["bound"], 1e16)

    def test_a_floor_clip_is_read_as_a_floor(self):
        for line in ("Bounding k>1e-16",
                     "bounding epsilon, min: -1 max: 3 average: 1"):
            self.assertEqual(classify_bound_line(line)["direction"], "floor",
                             line)

    def test_an_ordinary_line_is_not_a_bound(self):
        self.assertIsNone(classify_bound_line(
            "smoothSolver:  Solving for k, Initial residual = 0.1"))

    def test_only_a_ceiling_clip_is_a_divergence_finding(self):
        self.assertIsNone(detect_ceiling_clip("Bounding k>1e-16"))
        finding = detect_ceiling_clip("Bounding omega<1e+16")
        self.assertEqual(finding["severity"], "fatal")
        self.assertEqual(finding["field"], "omega")


class NormalisationCollapseTests(unittest.TestCase):
    """S10b: a residual that collapsed rather than converged."""

    def _collapsed(self, alive=5, dead=200):
        return [1.0] * alive + [1e-31] * dead

    def test_a_field_that_died_after_working_is_caught(self):
        finding = detect_normalisation_collapse(
            self._collapsed(), peer_residuals=[2e-4])
        self.assertIsNotNone(finding)
        self.assertEqual(finding["kind"], "normalisation-collapse")
        self.assertEqual(finding["severity"], "flag")
        self.assertGreaterEqual(finding["iterations_at_floor"], 100)

    def test_a_field_that_was_never_alive_is_not_a_finding(self):
        # A conserved variable updated explicitly reports exactly zero from
        # first iteration to last. Five such series sit in the lab's archive
        # and this condition is the only thing that passes over them.
        self.assertIsNone(detect_normalisation_collapse(
            [0.0] * 300, peer_residuals=[2e-4]))

    def test_a_solve_that_finished_everywhere_is_not_a_contradiction(self):
        self.assertIsNone(detect_normalisation_collapse(
            self._collapsed(), peer_residuals=[1e-31, 1e-30]))

    def test_an_ordinary_converged_field_is_not_a_collapse(self):
        # Converging to 1e-09 is convergence. The floor sits twelve orders
        # below the tightest target any of the lab's cases asks for.
        self.assertGreater(1e-9, DEAD_FIELD_FLOOR)
        self.assertIsNone(detect_normalisation_collapse(
            [1.0] * 5 + [1e-9] * 200, peer_residuals=[2e-4]))

    def test_a_short_series_gives_no_judgment(self):
        self.assertIsNone(detect_normalisation_collapse(
            [1.0] * 5 + [1e-31] * 40, peer_residuals=[2e-4]))


class ResidualNormContradictionTests(unittest.TestCase):
    """S10c: the unnormalised norms contradict the reported convergence."""

    def test_the_withdrawn_runs_norms_are_a_contradiction(self):
        # Verbatim from the withdrawn run's own end-of-run block.
        finding = detect_residual_norm_contradiction({
            "U": 6876.645, "p": 701.77652, "omega": 1.1347097e35,
            "k": 1.4648128e8, "phi": 18.937782})
        self.assertIsNotNone(finding)
        self.assertEqual(finding["field"], "omega")
        self.assertEqual(finding["severity"], "fatal")
        self.assertGreater(finding["orders_of_magnitude"], 30.0)

    def test_the_healthy_solve_of_the_same_case_is_not(self):
        # Verbatim from the healthy coarse run. Its worst ratio is 3.6 orders,
        # the largest anywhere in the 157 archived blocks, against a threshold
        # of 10.
        finding = detect_residual_norm_contradiction({
            "U": 0.4264852, "p": 0.0063069121, "omega": 1848.2911,
            "k": 14.319406, "phi": 0.002601756})
        self.assertIsNone(finding)
        self.assertEqual(RESIDUAL_NORM_ORDERS, 10.0)

    def test_a_non_finite_norm_is_a_contradiction(self):
        finding = detect_residual_norm_contradiction(
            {"U": 1.0, "omega": float("inf")})
        self.assertEqual(finding["field"], "omega")

    def test_no_reference_field_means_no_judgment(self):
        self.assertIsNone(detect_residual_norm_contradiction({"omega": 1e30}))
        self.assertIsNone(detect_residual_norm_contradiction(
            {"U": 0.0, "omega": 1e30}))


class ArchiveSweepTests(unittest.TestCase):
    """S10 against every solver log the lab has archived.

    A rule that names a healthy run is worse than no rule, so the whole
    corpus is swept rather than a chosen sample. All three branches together
    name exactly one log, and it is the run whose drag was withdrawn.
    """

    ROOT = Path(__file__).resolve().parents[2] / "demo-output"
    WITHDRAWN = "A4_fine_primal_par4.log"

    _RESIDUAL = re.compile(
        r"Solving for (\w+),.*Initial residual = ([0-9.eE+-]+)")
    _NORM = re.compile(
        r"^\s*(\w[\w.]*) Residual Norm2: (?:\(([^)]*)\)|([0-9.eE+-]+))")

    def _sweep(self, path):
        series, norms, ceiling = {}, {}, set()
        with open(path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                match = self._RESIDUAL.search(line)
                if match:
                    series.setdefault(match.group(1), []).append(
                        float(match.group(2)))
                    continue
                match = self._NORM.match(line)
                if match:
                    if match.group(1).lower() != "total":
                        raw = match.group(2) or match.group(3)
                        norms[match.group(1)] = max(
                            abs(float(token)) for token in raw.split())
                    continue
                bound = classify_bound_line(line)
                if bound and bound["direction"] == "ceiling":
                    ceiling.add(bound["field"])
        found = set()
        if ceiling:
            found.add("ceiling-clip")
        latest = {name: values[-1] for name, values in series.items()}
        for name, values in series.items():
            peers = [v for other, v in latest.items() if other != name]
            if detect_normalisation_collapse(values, peer_residuals=peers):
                found.add("normalisation-collapse")
        if detect_residual_norm_contradiction(norms):
            found.add("residual-norm-contradiction")
        return found

    def test_exactly_one_archived_log_is_named_and_it_is_the_withdrawn_one(self):
        logs = sorted(self.ROOT.rglob("*.log"))
        self.assertGreater(len(logs), 300, "the log archive did not resolve")
        named = {}
        for path in logs:
            found = self._sweep(path)
            if found:
                named[path.name] = found
        self.assertEqual(sorted(named), [self.WITHDRAWN])
        self.assertEqual(
            named[self.WITHDRAWN],
            {"ceiling-clip", "normalisation-collapse",
             "residual-norm-contradiction"})


if __name__ == "__main__":
    unittest.main()
