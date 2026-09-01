#!/usr/bin/env python3
"""Tests for the log-replay solver stage and the reader underneath it.

The reader is a measurement script: if it goes blind it does not crash, it
draws a smooth convincing curve of nothing. So the tests that matter here are
not "does it return a number" but "can it still tell when it is wrong":

  * the planted controls fire on the real run tree, and
  * the pressure control CATCHES a reader mutated back into the L-419 bug.

A control that has never been shown to fail is not evidence.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))

from chief_engineer.replay_history import (          # noqa: E402
    PLANT, PLANT_SECOND_PASS, ReaderRefused, downsample,
    read_coefficient_history, read_non_orthogonal_correctors,
    read_run_status, read_solve_history, self_check)
from chief_engineer.replay_stage import (            # noqa: E402
    ReplaySpec, ReplayStage, banner_for)

RUNS = Path("/home/ubuntu/Certonomous/verification/runs/JF1_jet_flap")
CASE = RUNS / "JF1_L1_BLOWN_CMU020_A0"
SWEEP = [("C_mu 0.00", RUNS / "JF1_L1_UNBLOWN_A0"),
         ("C_mu 0.05", RUNS / "JF1_L1_BLOWN_CMU005_A0"),
         ("C_mu 0.10", RUNS / "JF1_L1_BLOWN_CMU010_A0"),
         ("C_mu 0.20", RUNS / "JF1_L1_BLOWN_CMU020_A0"),
         ("C_mu 0.40", RUNS / "JF1_L1_BLOWN_CMU040_A0")]

available = CASE.is_dir()


def _virtual_stage(**kwargs) -> tuple:
    """A stage on a virtual clock: same values, no waiting."""
    spec = ReplaySpec(cases=SWEEP, max_frames=kwargs.pop("max_frames", 40),
                      seconds_per_point=kwargs.pop("seconds_per_point", 9.0),
                      **kwargs)
    now = [0.0]
    stage = ReplayStage(spec, sleep=lambda s: now.__setitem__(0, now[0] + s),
                        clock=lambda: now[0])
    events: list = []
    return stage, events, (lambda name, payload: events.append((name, payload)))


@unittest.skipUnless(available, "JF1 run tree not on this box")
class ThePressureDoubleSolve(unittest.TestCase):
    """The one that cost the lab a defect tonight (L-419)."""

    def test_the_case_really_does_solve_p_twice(self):
        """The premise of every other test here, asserted rather than assumed."""
        self.assertEqual(read_non_orthogonal_correctors(CASE), 1)
        text = (CASE / "log.simpleFoam").read_text(errors="replace")
        self.assertEqual(text.count("Solving for p,"), 16000)
        self.assertEqual(text.count("Solving for k,"), 8000)
        self.assertEqual(text.count("Solving for omega,"), 8000)
        self.assertEqual(text.count("\nTime = "), 8000)

    def test_reader_takes_the_first_pass(self):
        history = read_solve_history(CASE)
        self.assertEqual(history["p_pass_taken"], 1)
        self.assertEqual(history["p_passes_per_iteration"], 2)
        # Measured off the final iteration of this case: pass 1 is
        # 2.323244216e-05 and pass 2 is 1.176285151e-06. Taking the last
        # match would report a run twenty times better converged than it is.
        self.assertEqual(history["residuals"]["p"][-1], 2.323244216e-05)
        self.assertNotEqual(history["residuals"]["p"][-1], 1.176285151e-06)

    def test_solver_info_corroborates_every_iteration(self):
        history = read_solve_history(CASE)
        self.assertIn("8000/8000", history["solver_info_cross_check"])

    def test_the_control_catches_a_last_match_reader(self):
        """Mutate the reader into the L-419 bug; the plant must refuse.

        Done by patching the module's parse step rather than by editing a
        copy on disk, so a stale ``__pycache__`` cannot invert the result.
        """
        from chief_engineer import replay_history as module

        original = module.read_solve_history

        def mutated(case_dir, fields=module.RESIDUAL_FIELDS, *, cross_check=True):
            history = original(case_dir, fields, cross_check=cross_check)
            # The bug: take the LAST 'Solving for p' of each step.
            steps = module._parse_steps(Path(case_dir) / "log.simpleFoam")
            history["residuals"]["p"] = [s.solves["p"][-1] for s in steps]
            return history

        module.read_solve_history = mutated
        try:
            with self.assertRaises(ReaderRefused) as caught:
                module._plant_pressure_passes(CASE)
            self.assertIn("returned the SECOND", str(caught.exception))
        finally:
            module.read_solve_history = original


@unittest.skipUnless(available, "JF1 run tree not on this box")
class PlantedControls(unittest.TestCase):

    def test_all_four_controls_pass_on_the_real_tree(self):
        results = self_check(CASE)
        self.assertEqual(len(results), 4)
        for line in results:
            self.assertIn("PASSED", line)

    def test_coefficient_reader_refuses_an_absent_column(self):
        with self.assertRaises(ReaderRefused):
            read_coefficient_history(CASE, "Cl_that_does_not_exist")

    def test_two_sentinels_are_distinguishable(self):
        self.assertNotEqual(PLANT, PLANT_SECOND_PASS)


@unittest.skipUnless(available, "JF1 run tree not on this box")
class RealTimeAndRealCost(unittest.TestCase):

    def test_elapsed_comes_from_the_run_not_the_screen(self):
        history = read_solve_history(CASE, cross_check=False)
        status = read_run_status(CASE)
        # The log's own final ExecutionTime, and the wrapper's measured wall.
        self.assertAlmostEqual(history["elapsed_s"][-1], 1338.06, places=2)
        self.assertEqual(status["wall_s"], 1340.0)
        self.assertEqual(status["core_min_measured"], 22.3333)
        self.assertIn("NOT measured", status["cost_basis"])

    def test_no_sweep_total_is_published_as_a_duration(self):
        """The points ran concurrently; their sum is not an elapsed time."""
        stage, events, emit = _virtual_stage()
        record = stage.run(emit=emit)
        self.assertTrue(record["ran_concurrently"])
        self.assertNotIn("wall_s_sum", record)
        self.assertEqual(record["wall_clock_span_s"], 2813.0)
        self.assertIn("concurrently", record["wall_clock_span_basis"])
        self.assertAlmostEqual(record["core_min_measured"], 117.4833, places=4)


@unittest.skipUnless(available, "JF1 run tree not on this box")
class DownSamplingIsSelectionNotSmoothing(unittest.TestCase):

    def test_every_frame_is_a_real_row(self):
        history = read_solve_history(CASE, cross_check=False)
        coefficients = {"Cl": read_coefficient_history(CASE, "Cl")}
        frames, provenance = downsample(history, coefficients, max_frames=40)
        self.assertLessEqual(len(frames), 41)
        for frame in frames:
            row = frame.source_row
            self.assertEqual(frame.iteration, history["iterations"][row])
            self.assertEqual(frame.elapsed_s, history["elapsed_s"][row])
            self.assertEqual(frame.residuals["p"], history["residuals"]["p"][row])
            self.assertEqual(frame.coefficients["Cl"], coefficients["Cl"][row])
        self.assertEqual(frames[0].source_row, 0)
        self.assertEqual(frames[-1].source_row, history["n"] - 1)
        self.assertIn("no averaging", provenance["rule"])

    def test_envelope_brackets_the_rows_stridden_past(self):
        history = read_solve_history(CASE, cross_check=False)
        frames, _ = downsample(history, {}, max_frames=40)
        for frame in frames:
            low, high = frame.envelope["p"]
            self.assertLessEqual(low, frame.residuals["p"])
            self.assertGreaterEqual(high, frame.residuals["p"])


@unittest.skipUnless(available, "JF1 run tree not on this box")
class TheStage(unittest.TestCase):

    def test_monitors_advance_progressively(self):
        stage, events, emit = _virtual_stage()
        record = stage.run(emit=emit)
        self.assertGreater(record["progressive"]["events"], 100)
        self.assertGreater(record["progressive"]["span_s"], 0)
        # Neither half of the stage may hold nearly everything.
        self.assertGreater(record["progressive"]["first_half_share"], 0.2)
        self.assertLess(record["progressive"]["first_half_share"], 0.8)

    def test_iteration_counter_and_sweep_progress_both_move(self):
        stage, events, emit = _virtual_stage()
        stage.run(emit=emit)
        frames = [p for name, p in events if name == "solve.frame"]
        self.assertEqual(frames[0]["iteration"], 1)
        self.assertEqual(frames[-1]["iteration"], 8000)
        self.assertEqual(frames[0]["point_index"], 1)
        self.assertEqual(frames[-1]["point_index"], 5)
        self.assertGreater(len(frames), 200)
        # All five points ran the same 8000 iterations, so they share one
        # iteration grid; the counter is checked per point, not across the
        # concatenation, where 41 distinct values is the correct answer.
        for point in range(1, 6):
            mine = [f["iteration"] for f in frames if f["point_index"] == point]
            self.assertGreater(len(set(mine)), 30)
            self.assertEqual(mine, sorted(mine))
            self.assertEqual(mine[0], 1)
            self.assertEqual(mine[-1], 8000)

    def test_banner_never_drifts_from_its_content(self):
        stage, events, emit = _virtual_stage()
        stage.run(emit=emit)
        pairs = 0
        for earlier, later in zip(events, events[1:]):
            if earlier[0] != "stage.banner" and later[0] == "stage.banner":
                pairs += 1
                self.assertEqual(later[1]["text"], earlier[1]["banner"])
                self.assertEqual(later[1]["for_event"], earlier[0])
        self.assertGreater(pairs, 100)

    def test_banner_is_a_pure_function_of_the_frame(self):
        state = {"point_index": 3, "points": 5, "iteration": 4000,
                 "iterations": 8000}
        self.assertEqual(banner_for(state),
                         "Solving, iteration 4,000 of 8,000, sweep point 3 of 5")
        self.assertEqual(banner_for(dict(state)), banner_for(dict(state)))
        self.assertEqual(banner_for({"finished": True}), "Solved")

    def test_a_burst_is_refused(self):
        """A stage that emitted everything at one instant must not pass."""
        stage, events, emit = _virtual_stage()
        stage.clock = lambda: 0.0          # a clock that never advances
        with self.assertRaises(ReaderRefused):
            stage.run(emit=emit)

    def test_prepare_runs_the_controls_before_any_frame(self):
        stage, events, emit = _virtual_stage()
        history = stage.prepare()
        self.assertEqual(events, [])
        self.assertEqual(len(history.controls), 4)
        for line in history.controls:
            self.assertIn("PASSED", line)


if __name__ == "__main__":
    unittest.main(verbosity=2)
