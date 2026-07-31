"""The Sobol sensitivity mission: routing, gates, and what it puts on record.

Covers the three things that can silently go wrong with a variance
apportionment on camera: the prompt landing on the wrong act, a ranking read
off overlapping intervals, and first-order shares summing past the whole
variance because the base sample was too small.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))

import yaml  # noqa: E402

from chief_engineer.router import (SOBOL_SENSITIVITY, UNCERTAINTY_REDUCTION,  # noqa: E402
                                   VALVE_STUDY, WORKFLOWS, classify)
from chief_engineer.sensitivity import (sobol_indices,  # noqa: E402
                                        uniform_sigma_input)
from workflows import sobol_sensitivity as act  # noqa: E402

APPROVED_PROMPT = (
    "Run a Sobol sensitivity mission on the valve screen: inputs are flow "
    "amplitude (sigma 5 percent) and discharge coefficient (sigma 6 "
    "percent); evaluate the cycle-weighted loss through the reduced-order "
    "orifice path with a pick-and-freeze design, N 200, cost N times (M plus "
    "2) equals 800 evaluations; report main and total effect indices with "
    "bootstrap confidence intervals.")


class RoutingTests(unittest.TestCase):
    def test_the_approved_launch_prompt_reaches_this_act(self):
        # The prompt names the valve, which scores the valve study 1.7. The
        # decomposition has to outrank the act whose spreads it decomposes.
        self.assertEqual(classify(APPROVED_PROMPT).intent, SOBOL_SENSITIVITY)

    def test_plain_language_asks_reach_it_too(self):
        for prompt in ("Which input owns the variance in the valve envelope?",
                       "Apportion the output variance across the input "
                       "spreads before we price the reduction campaign.",
                       "Run a global sensitivity study on the airliner "
                       "spreads."):
            with self.subTest(prompt=prompt):
                self.assertEqual(classify(prompt).intent, SOBOL_SENSITIVITY)

    def test_it_steals_no_existing_act(self):
        self.assertEqual(
            classify("Find the valve opening angle that minimizes pressure "
                     "loss over the cardiac cycle.").intent, VALVE_STUDY)
        self.assertEqual(
            classify("How sure are we about the drag? Tighten the error "
                     "bars.").intent, UNCERTAINTY_REDUCTION)

    def test_the_route_dispatches_to_a_module_that_exists(self):
        entry = WORKFLOWS[SOBOL_SENSITIVITY]
        self.assertEqual(entry["module"], "workflows.sobol_sensitivity")
        self.assertEqual(entry["output"], "sobol-sensitivity")


class GateTests(unittest.TestCase):
    def test_gates_come_from_the_governed_physics_file(self):
        rules = yaml.safe_load(
            (SDK.parent / "docs" / "physics_rules.yaml").read_text(
                encoding="utf-8"))["sobol"]
        gates = act._gates()
        for key in ("identity_slack", "min_base_samples", "max_base_samples"):
            self.assertEqual(gates[key], rules[key])

    def test_the_opening_budget_is_the_one_the_proposal_priced(self):
        self.assertEqual(act._gates()["min_base_samples"], 200)

    def test_overlapping_intervals_are_not_separated(self):
        # The valve case at the approved budget: the two shares cannot be
        # told apart, which is exactly the case the gate exists to catch.
        case = act._valve_case()
        opening = sobol_indices(case["model"], case["dists"], n_base=200,
                                seed=case["seed"])
        self.assertFalse(act._separated(opening))
        self.assertFalse(act._admissible(opening, act._gates()))

    def test_the_ladder_escalates_until_the_gate_clears(self):
        gates = act._gates()
        rungs, resolved = act._ladder(act._valve_case(), gates)
        self.assertTrue(resolved)
        self.assertGreater(len(rungs), 1)
        self.assertEqual(rungs[0].n_base, gates["min_base_samples"])
        # Doubling, never an arbitrary jump.
        for earlier, later in zip(rungs, rungs[1:]):
            self.assertEqual(later.n_base, earlier.n_base * 2)
        # Nothing escalates past the ceiling the physics file states.
        self.assertLessEqual(rungs[-1].n_base, gates["max_base_samples"])

    def test_shares_that_sum_past_the_whole_variance_fail_the_gate(self):
        gates = act._gates()
        for case in (act._valve_case(), act._airliner_case()):
            with self.subTest(case=case["key"]):
                rungs, _ = act._ladder(case, gates)
                final = rungs[-1]
                self.assertLessEqual(sum(final.main),
                                     1.0 + gates["identity_slack"])
                for main, total in zip(final.main, final.total):
                    self.assertLessEqual(main, total + gates["identity_slack"])

    def test_a_constant_model_has_no_shares_to_apportion(self):
        with self.assertRaises(ValueError):
            sobol_indices(lambda a, b: 1.0,
                          {"a": uniform_sigma_input(1.0, 0.05),
                           "b": uniform_sigma_input(1.0, 0.05)},
                          n_base=32, seed=1)


class RecordTests(unittest.TestCase):
    def test_the_cases_carry_each_act_own_published_spreads(self):
        from workflows import valve_study as vs
        from workflows.aircraft_optimization import (_SIGMA_CD0_NONWING,
                                                     _SIGMA_PAYLOAD)

        valve = act._valve_case()
        self.assertEqual(valve["sigmas"]["flow amplitude"], vs.FLOW_SIGMA)
        self.assertEqual(valve["sigmas"]["discharge coefficient"], vs.CD_SIGMA)
        airliner = act._airliner_case()
        self.assertEqual(airliner["sigmas"]["payload mass"], _SIGMA_PAYLOAD)
        self.assertEqual(airliner["sigmas"]["non-wing drag"],
                         _SIGMA_CD0_NONWING)

    def test_the_corner_check_moves_the_leading_input_only(self):
        case = act._valve_case()
        rungs, _ = act._ladder(case, act._gates())
        corner = act._corner_check(case, rungs[-1])
        self.assertEqual(corner["input"], "discharge coefficient")
        # A higher discharge coefficient passes more flow for less loss, so
        # the high edge must sit below the nominal, not above it.
        self.assertLess(corner["high"], corner["nominal"])
        self.assertGreater(corner["low"], corner["nominal"])
        self.assertGreater(corner["relative"], 0.0)

    def test_the_mission_runs_and_records_its_shares(self):
        events: list[tuple] = []
        rc = act.main(request="Which input owns the variance?",
                      emit=lambda name, payload: events.append((name, payload)))
        self.assertEqual(rc, 0)
        kinds = [name for name, _ in events]
        self.assertIn("report.ready", kinds)
        self.assertIn("result.verdict", kinds)
        report = next(p for n, p in events if n == "report.ready")
        self.assertTrue(report["results"])
        self.assertEqual(len(report.get("plots", [])), 2)
        # Every reported share carries its interval.
        for row in report["results"]:
            self.assertIn("95%", row["envelope"])
        # Two figures on disk, one per case.
        out = act.OUT_ROOT / "sobol-sensitivity"
        self.assertTrue((out / "variance_share_valve.png").exists())
        self.assertTrue((out / "variance_share_airliner.png").exists())
        self.assertTrue((out / "transcript.txt").exists())


if __name__ == "__main__":
    unittest.main()
