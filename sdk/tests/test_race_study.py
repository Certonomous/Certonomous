"""Race-study workflow — the streaming twin, tested without the real solver.

The lanes' event choreography (race.init, per-lane trace points and progress,
the speedup card, the agreement) must hold regardless of the solver, so a
deterministic stub solver stands in for VSPAERO here. Every measured number in
the events still comes from the stub's timings — the test asserts the SHAPE of
the evidence, never fabricates a magnitude.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

import workflows.race_study as rs


class _StubSolver:
    """Deterministic stand-in: an L/D curve peaking near alpha 2, cheap timings."""

    def __init__(self, work_root):
        self.work_root = Path(work_root)
        self.solve_seconds: list[float] = []

    def solve(self, alpha, re_cref, tag):
        # A concave curve so the quadratic surface has an interior vertex; the
        # Reynolds sample nudges it so MC peaks scatter a little.
        l_d = 18.0 - 0.10 * (alpha - 2.0) ** 2 + (re_cref - 1.0e6) / 1.0e6 * 0.4
        # A representative per-solve cost so the measured core-minutes on both
        # lanes survive rounding — the speedup then reflects the solve counts.
        self.solve_seconds.append(0.5)
        return {"alpha": alpha, "re_cref": re_cref, "cl": 0.5, "cd": 0.03,
                "l_d": l_d, "seconds": 0.5}


def _run(**kw):
    events: list[tuple[str, dict]] = []
    with tempfile.TemporaryDirectory() as tmp:
        with mock.patch.object(rs, "_TimedSolver", _StubSolver), \
             mock.patch.object(rs, "OUT_ROOT", Path(tmp)):
            rc = rs.main(request="race test",
                         params={"mc_samples": 3},
                         emit=lambda e, p=None: events.append((e, p or {})),
                         **kw)
    return rc, events


class RaceStudyEvents(unittest.TestCase):
    def setUp(self):
        self.rc, self.events = _run(seed=7)
        self.by = {}
        for name, payload in self.events:
            self.by.setdefault(name, []).append(payload)

    def test_completes(self):
        self.assertEqual(self.rc, 0)

    def test_race_init_declares_both_lanes(self):
        init = self.by["race.init"][0]
        keys = {l["key"] for l in init["lanes"]}
        self.assertEqual(keys, {"mc", "rom"})
        # MC total is samples x alphas; ROM is anchors + one confirm.
        totals = {l["key"]: l["total"] for l in init["lanes"]}
        self.assertEqual(totals["mc"], 3 * len(rs.ALPHAS))
        self.assertEqual(totals["rom"], len(rs.ANCHOR_ALPHAS) + 1)

    def test_both_lanes_report_done(self):
        done = {p["lane"] for p in self.by["race.lane"] if p.get("state") == "done"}
        self.assertEqual(done, {"mc", "rom"})

    def test_per_lane_trace_points_stream(self):
        series = {p["series"] for p in self.by["trace.point"]}
        self.assertEqual(series, {"mc", "rom"})
        # The nominal-Reynolds sample is flagged for the running-answer line.
        self.assertTrue(any(p.get("nominal") for p in self.by["trace.point"]
                            if p["series"] == "mc"))
        # ROM emits an anchor set and exactly one confirmation.
        rom_kinds = [p.get("kind") for p in self.by["trace.point"]
                     if p["series"] == "rom"]
        self.assertEqual(rom_kinds.count("confirm"), 1)
        self.assertEqual(rom_kinds.count("anchor"), len(rs.ANCHOR_ALPHAS))

    def test_rom_emits_a_fitted_surface(self):
        curve = self.by["race.curve"][0]
        self.assertEqual(curve["lane"], "rom")
        self.assertEqual(len(curve["coefficients"]), 3)

    def test_result_card_carries_measured_speedup_and_agreement(self):
        result = self.by["race.result"][0]
        self.assertIn("speedup_core_min", result)
        self.assertIn("speedup_wall", result)
        self.assertIn("agreement_pct", result)
        # The MC lane does more solves than the reduced-order lane, so the
        # measured speedup is a real number greater than 1.
        self.assertGreater(result["mc"]["n_solves"], result["rom"]["n_solves"])
        self.assertGreater(result["speedup_core_min"], 1.0)

    def test_verdict_is_solver_backed(self):
        verdict = self.by["result.verdict"][0]
        self.assertEqual(verdict["tier"], "SOLVER-BACKED")

    def test_certificate_is_issued_for_the_race_act(self):
        # Every act must carry a Certonomous certificate; the race's headline
        # results are the measured speedup and the agreement, on the NACA wing.
        self.assertIn("certificate.ready", self.by)
        cert = self.by["certificate.ready"][0]
        # The PDF is written under the (temp) OUT_ROOT the harness cleans up, so
        # assert the target rather than a surviving file.
        self.assertTrue(cert["path"].endswith("certificate.pdf"))
        self.assertEqual(cert["dir"], "race-study")
        self.assertEqual(cert["tier"], "SOLVER-BACKED")
        self.assertTrue(cert.get("certificate_no", "").startswith("C-"))
        # The seal is a 64-hex SHA-256.
        self.assertEqual(len(cert["hash"]), 64)


class RaceStudyConfig(unittest.TestCase):
    def test_worker_cap_is_four(self):
        self.assertEqual(rs.MAX_WORKERS, 4)

    def test_mc_reynolds_leads_with_the_nominal(self):
        res = rs._mc_reynolds(4, seed=1)
        self.assertEqual(res[0], rs.RE_NOMINAL)
        self.assertEqual(len(res), 4)


if __name__ == "__main__":
    unittest.main()
