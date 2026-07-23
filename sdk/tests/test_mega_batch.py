"""Mega-batch runner + lifetime-counter tests (CI-safe: no external solvers).

The valve path is a pure in-repo reduced-order model, so ``run_task`` on a valve
index runs anywhere. Determinism, ledger durability, resume, and the lab-stats
counters are all exercised without OpenFOAM or VSPAERO.
"""

import json
import tempfile
import unittest
from pathlib import Path

from workflows import mega_batch
from chief_engineer import lab_stats


class DesignStreamTests(unittest.TestCase):
    def test_three_way_interleave(self):
        solvers = [mega_batch.design_for_index(i)["solver"] for i in range(9)]
        self.assertEqual(solvers, [
            mega_batch.CYLINDER, mega_batch.WING, mega_batch.VALVE,
            mega_batch.CYLINDER, mega_batch.WING, mega_batch.VALVE,
            mega_batch.CYLINDER, mega_batch.WING, mega_batch.VALVE,
        ])

    def test_deterministic(self):
        self.assertEqual(mega_batch.design_for_index(42),
                         mega_batch.design_for_index(42))

    def test_ranges_sane(self):
        cyl = mega_batch.design_for_index(0)["design"]
        self.assertTrue(0.5 <= cyl["cylinder_diameter"] <= 2.0)
        self.assertTrue(0.01 <= cyl["kinematic_viscosity"] <= 0.2)
        wing = mega_batch.design_for_index(1)["design"]
        self.assertTrue(20.0 <= wing["span"] <= 70.0)
        valve = mega_batch.design_for_index(2)["design"]
        self.assertTrue(35.0 <= valve["opening_angle_deg"] <= 85.0)


class ValveTaskTests(unittest.TestCase):
    def test_valve_run_task_is_labelled_reduced_order(self):
        with tempfile.TemporaryDirectory() as d:
            record = mega_batch.run_task(2, Path(d))
        self.assertTrue(record["ok"])
        self.assertEqual(record["solver"], mega_batch.VALVE)
        self.assertEqual(record["label"], "reduced-order-eval")
        m = record["metrics"]
        self.assertGreater(m["cycle_weighted_loss_Pa"], 0.0)
        self.assertGreater(m["orifice_area_mm2"], 0.0)
        self.assertIn("womersley_alpha", m)


class LedgerTests(unittest.TestCase):
    def test_append_and_resume(self):
        with tempfile.TemporaryDirectory() as d:
            ledger = Path(d) / "ledger.jsonl"
            for i in (0, 1, 2):
                mega_batch.append_ledger(ledger, {"index": i, "solver": "x", "ok": True})
            done = mega_batch.load_done_indices(ledger)
            self.assertEqual(done, {0, 1, 2})
            # A malformed line must not break the resume read.
            with ledger.open("a", encoding="utf-8") as fh:
                fh.write("{ not json\n")
            self.assertEqual(mega_batch.load_done_indices(ledger), {0, 1, 2})

    def test_run_batch_valve_only_resumes(self):
        # Force a valve-only stream so the batch needs no external solver.
        with tempfile.TemporaryDirectory() as d:
            ledger = Path(d) / "ledger.jsonl"
            work = Path(d) / "work"
            original = mega_batch.design_for_index

            def valve_only(index):
                return {"solver": mega_batch.VALVE,
                        "design": {"opening_angle_deg": 40.0 + (index % 40)}}

            mega_batch.design_for_index = valve_only
            try:
                mega_batch.run_batch(ledger, work, workers=2, max_tasks=4, log=lambda *_: None)
                first = mega_batch.load_done_indices(ledger)
                self.assertEqual(len(first), 4)
                mega_batch.run_batch(ledger, work, workers=2, max_tasks=3, log=lambda *_: None)
                second = mega_batch.load_done_indices(ledger)
                self.assertEqual(len(second), 7)
                # No index repeated across the two sessions.
                rows = [json.loads(x) for x in ledger.read_text().splitlines() if x.strip()]
                indices = [r["index"] for r in rows]
                self.assertEqual(len(indices), len(set(indices)))
            finally:
                mega_batch.design_for_index = original


class LabStatsTests(unittest.TestCase):
    def test_lifetime_counters_from_ledger(self):
        with tempfile.TemporaryDirectory() as d:
            ledger = Path(d) / "ledger.jsonl"
            mega_batch.append_ledger(ledger, {
                "index": 0, "solver": "openfoam-cylinder", "ok": True,
                "wall_seconds": 12.0, "timestamp": "2026-07-23T00:00:00Z"})
            mega_batch.append_ledger(ledger, {
                "index": 1, "solver": "vspaero-wing", "ok": True,
                "wall_seconds": 6.0, "timestamp": "2026-07-23T00:00:10Z"})
            mega_batch.append_ledger(ledger, {
                "index": 2, "solver": "reduced-order", "ok": False,
                "wall_seconds": 0.1, "timestamp": "2026-07-23T00:00:11Z"})
            summary = lab_stats.ledger_summary(ledger)
            self.assertEqual(summary["evaluations_ok"], 2)
            self.assertEqual(summary["evaluations_failed"], 1)
            self.assertAlmostEqual(summary["core_hours"], 18.0 / 3600.0, places=6)
            counters = lab_stats.lifetime_counters(ledger)
            self.assertEqual(counters["missions_run"], 2)
            self.assertGreaterEqual(counters["knowledge_entries"], 1)


if __name__ == "__main__":
    unittest.main()
