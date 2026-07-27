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
                # Every batch is a learning opportunity: the session-end
                # distiller must have written the learned study beside it.
                study_path = ledger.parent / "learned_study.json"
                self.assertTrue(study_path.exists())
                study = json.loads(study_path.read_text(encoding="utf-8"))
                self.assertEqual(study["provenance"]["row_count"], 7)
                self.assertEqual(study["valve"]["n"], 7)
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

    def test_research_programs_are_real_and_structured(self):
        # The credentials ACTIVE RESEARCH section is data-driven (R5): closure
        # board, public challenge targets, and the reduced-order speed program
        # all come back structured, with real numbers and no invented "our
        # score". The discretization-ladder card is retired from the wall by
        # owner curation, so no "uq" key may reach the payload.
        r = lab_stats.research_programs()
        self.assertEqual(
            set(r),
            {"closure", "speed", "fleet_learning", "queued", "challenges"},
        )

        closure = r["closure"]
        self.assertEqual(closure["target_rank"], 4)
        self.assertEqual(len(closure["target_per_case"]), 8)
        self.assertIn("rmcconke/closure-challenge-benchmark", closure["repo"])
        # our_score is not invented: it is a zero-training RANS-identity
        # reference floor, measured through the benchmark's own unmodified
        # scoring code (evidence: demo-output/website/
        # closure_challenge_rans_floor.json, sdk/scripts/
        # run_closure_challenge_evidence.py). No entry has been submitted and
        # no model has been trained, and the entry text says so plainly every
        # time this card is rendered.
        self.assertEqual(closure["our_score"], 0.1036)
        self.assertEqual(len(closure["our_per_case"]), 8)
        self.assertEqual(
            closure["our_entry"],
            "No entry submitted. Measured a zero-training RANS reference floor of "
            "0.1036 overall, scored by the benchmark's own unmodified code; worse "
            "than every published entry, since it reflects no learned correction",
        )
        for forbidden in ("trend", "indicative", "real solve"):
            self.assertNotIn(forbidden, closure["our_entry"].lower())
        self.assertNotIn("—", closure["our_entry"])  # no em dashes

        self.assertGreater(r["speed"]["speedup_x"], 1.0)
        # Internal working notes never reach the wall: the speed card carries
        # no provenance string pointing at repo files.
        self.assertNotIn("source", r["speed"])
        self.assertTrue(r["queued"], "the valve agenda seeds the queued research")

    def test_research_challenges_are_real_public_targets(self):
        # The challenges list carries real, public benchmarks the lab honestly
        # targets. Every entry keeps the same shape, cites a host and URL, and
        # NEVER asserts a score, rank, or result.
        challenges = lab_stats.research_challenges()
        self.assertGreaterEqual(len(challenges), 3)
        # research_challenges() must hand back copies, not the module constant.
        challenges[0]["title"] = "mutated"
        self.assertNotEqual(lab_stats.research_challenges()[0]["title"], "mutated")

        shape = {"title", "host", "url", "what", "status", "entry", "lead"}
        text_keys = shape - {"lead"}
        seen_hosts = set()
        for c in lab_stats.research_challenges():
            self.assertEqual(set(c), shape)
            for key in text_keys:
                self.assertTrue(str(c[key]).strip(), f"{key} must be non-empty")
            self.assertIsInstance(c["lead"], bool)
            # A host and a URL: cited external data, like the closure exemplar.
            self.assertTrue(c["url"], "every challenge cites a URL")
            seen_hosts.add(c["host"])
            # No invented result may masquerade as a status.
            self.assertNotIn("rank", c["status"].lower())
            for forbidden in ("rank #", "score", "1st", "won", "beat"):
                self.assertNotIn(forbidden, c["entry"].lower())
        self.assertGreaterEqual(len(seen_hosts), 3, "distinct hosts, not one board")

        # The four verified programmes are present by host or URL.
        blob = json.dumps(lab_stats.research_challenges()).lower()
        for token in ("aiaa-dpw", "turbmodels", "fda", "autocfd"):
            self.assertIn(token, blob, f"expected the {token} challenge")

    def test_research_challenge_order_is_owner_directed(self):
        # Deterministic wall order: the Drag Prediction Workshop leads, the
        # NASA Turbulence Modeling Resource follows, and only those two carry
        # the lead flag that places them directly after the closure card.
        challenges = lab_stats.research_challenges()
        self.assertIn("Drag Prediction Workshop", challenges[0]["title"])
        self.assertIn("Turbulence Modeling Resource", challenges[1]["title"])
        self.assertTrue(challenges[0]["lead"])
        self.assertTrue(challenges[1]["lead"])
        for c in challenges[2:]:
            self.assertFalse(c["lead"], f"unexpected lead flag on {c['title']}")

    def test_research_challenges_obey_the_style_rules(self):
        # The challenge cards are visible content, so they must stay on-message:
        # no em dash, no "demo", no cached/stored/saved/pre-computed language.
        # (Internal file paths in other cards are not visible and out of scope.)
        blob = json.dumps(lab_stats.research_challenges())
        self.assertNotIn("—", blob, "no em dashes in the challenge cards")
        low = blob.lower()
        for banned in ("demo", "cached", "stored", "saved", "pre-computed",
                       "precomputed", "recorded", "trend"):
            self.assertNotIn(banned, low, f"banned word surfaced: {banned}")


if __name__ == "__main__":
    unittest.main()
