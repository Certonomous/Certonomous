"""Ledger-learning distiller tests, on a small synthetic ledger fixture.

The fixture plants known laws in the rows (wing L/D linear in aspect ratio,
cylinder Cd a clean power of Re, valve loss falling with opening angle) so the
distiller's fits, best/worst picks, failure stats, and provenance can be
checked exactly. Also covers the lab_stats fleet-learning card and the
on-camera style rules (no em dashes, no banned words).
"""

import json
import math
import os
import tempfile
import unittest
from pathlib import Path

from chief_engineer import lab_stats, ledger_learning
from workflows import mega_batch

BANNED_WORDS = ("cached", "stored", "saved", "pre-computed", "precomputed",
                "recorded")


def _write_ledger(path: Path) -> dict:
    """Synthetic ledger with known trends; returns ground truth."""
    rows = []
    index = 0

    # 12 wing rows: L/D = 2*AR + 5 exactly; implied span efficiency 0.85.
    e_true = 0.85
    for i in range(12):
        ar = 6.0 + i
        span = 30.0
        area = span * span / ar
        cl = 0.5
        cdi = cl * cl / (math.pi * ar * e_true)
        rows.append({
            "index": index, "solver": "vspaero-wing", "label": "real-solve",
            "design": {"span": span, "area": area, "sweep": 5.0 + i,
                       "taper": 0.4, "cl_target": cl},
            "timestamp": f"2026-07-24T00:00:{index:02d}Z",
            "metrics": {"cl": cl, "cdi": cdi, "cdo_wing": 0.006,
                        "cd_total": cdi + 0.006, "L_D": 2.0 * ar + 5.0,
                        "alpha": 4.0},
            "ok": True, "wall_seconds": 7.0})
        index += 1
    best_wing_index = index - 1  # highest AR has highest L/D

    # 10 cylinder rows: Cd = 10 * Re^-0.5; nine converged, one not.
    for i in range(10):
        re = 10.0 + 3.5 * i
        rows.append({
            "index": index, "solver": "openfoam-cylinder", "label": "real-solve",
            "design": {"cylinder_diameter": 1.0, "inlet_velocity": 1.0,
                       "kinematic_viscosity": 1.0 / re, "mesh_refinement": 1.0},
            "timestamp": f"2026-07-24T00:01:{index:02d}Z",
            "metrics": {"Cd": 10.0 * re ** -0.5, "Re": re,
                        "converged": 1.0 if i < 9 else 0.0,
                        "solver_iterations": 400.0},
            "ok": True, "wall_seconds": 15.0})
        index += 1

    # 6 valve rows: loss falls with angle; lowest loss at the widest angle.
    for i in range(6):
        angle = 40.0 + 8.0 * i
        rows.append({
            "index": index, "solver": "reduced-order",
            "label": "reduced-order-eval",
            "design": {"opening_angle_deg": angle},
            "timestamp": f"2026-07-24T00:02:{index:02d}Z",
            "metrics": {"cycle_weighted_loss_Pa": 8000.0 - 80.0 * angle,
                        "feasible": True, "phase_points": 3},
            "ok": True, "wall_seconds": 0.01})
        index += 1
    best_valve_index = index - 1

    # 2 failures: one wing, one cylinder.
    for solver in ("vspaero-wing", "openfoam-cylinder"):
        rows.append({
            "index": index, "solver": solver, "label": "real-solve",
            "design": {}, "timestamp": f"2026-07-24T00:03:{index:02d}Z",
            "metrics": {}, "ok": False, "error": "RuntimeError: solver down",
            "wall_seconds": 1.0})
        index += 1

    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    return {"total": len(rows), "best_wing_index": best_wing_index,
            "best_valve_index": best_valve_index}


class DistillerTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.ledger = Path(self._tmp.name) / "ledger.jsonl"
        self.truth = _write_ledger(self.ledger)
        self.study = ledger_learning.distill(self.ledger)

    def tearDown(self):
        self._tmp.cleanup()

    def test_provenance_is_complete(self):
        prov = self.study["provenance"]
        self.assertEqual(prov["row_count"], self.truth["total"])
        self.assertEqual(prov["ok_rows"], self.truth["total"] - 2)
        self.assertEqual(prov["failed_rows"], 2)
        self.assertEqual(prov["ledger_path"], str(self.ledger.resolve()))
        self.assertTrue(prov["first_timestamp"].startswith("2026-07-24"))
        self.assertIn("generated_at", self.study)

    def test_family_counts_and_failure_rates(self):
        fam = self.study["families"]
        self.assertEqual(fam["vspaero-wing"]["ok"], 12)
        self.assertEqual(fam["vspaero-wing"]["failed"], 1)
        self.assertEqual(fam["vspaero-wing"]["attempted"], 13)
        self.assertAlmostEqual(fam["vspaero-wing"]["failure_rate"], 1 / 13, places=3)
        self.assertEqual(fam["openfoam-cylinder"]["ok"], 10)
        self.assertEqual(fam["reduced-order"]["failed"], 0)

    def test_wing_trend_measured_not_asserted(self):
        wing = self.study["wing"]
        self.assertEqual(wing["n"], 12)
        trend = wing["trend_LD_vs_aspect_ratio"]
        self.assertAlmostEqual(trend["fit"]["slope"], 2.0, places=3)
        self.assertGreater(trend["fit"]["r2"], 0.999)
        self.assertEqual(trend["quality"], "strong")
        self.assertEqual(wing["best"]["ledger_index"],
                         self.truth["best_wing_index"])
        self.assertGreater(wing["best"]["L_D"], wing["worst"]["L_D"])
        e = wing["implied_span_efficiency"]
        self.assertAlmostEqual(e["mean"], 0.85, places=2)

    def test_cylinder_power_law_recovered(self):
        cyl = self.study["cylinder"]
        self.assertEqual(cyl["n"], 10)
        fit = cyl["trend_logCd_vs_logRe"]["fit"]
        self.assertAlmostEqual(fit["slope"], -0.5, places=3)
        self.assertEqual(cyl["trend_logCd_vs_logRe"]["quality"], "strong")
        self.assertAlmostEqual(cyl["converged_fraction"], 0.9, places=4)

    def test_valve_best_and_trend(self):
        valve = self.study["valve"]
        self.assertEqual(valve["n"], 6)
        self.assertEqual(valve["best"]["ledger_index"],
                         self.truth["best_valve_index"])
        self.assertLess(valve["trend_loss_vs_angle"]["fit"]["slope"], 0.0)
        self.assertEqual(valve["feasible_fraction"], 1.0)

    def test_learned_sentences_cite_real_numbers(self):
        learned = self.study["learned"]
        self.assertTrue(learned)
        blob = " ".join(learned)
        self.assertIn("12 wing polars", blob)
        self.assertIn("10 cylinder solves", blob)
        self.assertIn("2 of 30 attempted evaluations failed", blob)

    def test_style_rules_no_em_dash_no_banned_words(self):
        visible = self.study["learned"] + [self.study["study"]]
        for text in visible:
            self.assertNotIn("—", text)
            lowered = text.lower()
            for word in BANNED_WORDS:
                self.assertNotIn(word, lowered, f"banned word in: {text}")

    def test_empty_ledger_is_honest(self):
        empty = Path(self._tmp.name) / "empty.jsonl"
        study = ledger_learning.distill(empty)
        self.assertEqual(study["provenance"]["row_count"], 0)
        self.assertEqual(study["wing"], {"n": 0})
        # No sentence may claim anything when there is nothing to claim.
        self.assertEqual(study["learned"], [])

    def test_distill_to_file_writes_json(self):
        out = Path(self._tmp.name) / "study.json"
        ledger_learning.distill_to_file(self.ledger, out)
        data = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(data["study"], "fleet-ledger-learning")
        self.assertEqual(data["provenance"]["row_count"], self.truth["total"])

    def test_runner_hook_never_raises(self):
        # A broken ledger path must not sink the batch.
        bogus = Path(self._tmp.name)  # a directory, not a file
        mega_batch.distill_learning(bogus / "missing" / "ledger.jsonl",
                                    log=lambda *_: None)
        mega_batch.distill_learning(bogus, log=lambda *_: None)


class FleetLearningCardTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.ledger = Path(self._tmp.name) / "ledger.jsonl"
        self.truth = _write_ledger(self.ledger)
        self.study_path = Path(self._tmp.name) / "learned_study.json"
        ledger_learning.distill_to_file(self.ledger, self.study_path)
        self._old_env = os.environ.get("CERTONOMOUS_LEDGER_STUDY")
        os.environ["CERTONOMOUS_LEDGER_STUDY"] = str(self.study_path)

    def tearDown(self):
        if self._old_env is None:
            os.environ.pop("CERTONOMOUS_LEDGER_STUDY", None)
        else:
            os.environ["CERTONOMOUS_LEDGER_STUDY"] = self._old_env
        self._tmp.cleanup()

    def test_card_shows_real_ledger_numbers(self):
        card = lab_stats.research_programs()["fleet_learning"]
        self.assertTrue(card["available"])
        self.assertEqual(card["status"], "ACTIVE RESEARCH")
        self.assertEqual(card["row_count"], self.truth["total"])
        self.assertEqual(card["ok_rows"], self.truth["total"] - 2)
        self.assertEqual(card["failed_rows"], 2)
        self.assertEqual(card["source"], str(self.ledger.resolve()))
        self.assertTrue(card["highlights"])
        solvers = {f["solver"]: f for f in card["families"]}
        self.assertEqual(solvers["vspaero-wing"]["ok"], 12)
        self.assertEqual(solvers["openfoam-cylinder"]["failed"], 1)
        self.assertEqual(card["best_wing"]["ledger_index"],
                         self.truth["best_wing_index"])

    def test_card_style_rules(self):
        card = lab_stats.research_programs()["fleet_learning"]
        visible = [card["title"], card["summary"]] + card["highlights"]
        for text in visible:
            self.assertNotIn("—", text)
            lowered = text.lower()
            for word in BANNED_WORDS:
                self.assertNotIn(word, lowered, f"banned word in: {text}")

    def test_existing_cards_untouched(self):
        r = lab_stats.research_programs()
        for key in ("closure", "uq", "speed", "queued"):
            self.assertIn(key, r)
        self.assertEqual(r["closure"]["target_rank"], 4)
        self.assertTrue(r["queued"])

    def test_missing_study_is_pending_with_no_numbers(self):
        os.environ["CERTONOMOUS_LEDGER_STUDY"] = str(
            Path(self._tmp.name) / "nope.json")
        card = lab_stats.research_programs()["fleet_learning"]
        self.assertFalse(card["available"])
        self.assertEqual(card["status"], "PENDING")
        self.assertNotIn("row_count", card)
        self.assertNotIn("—", card["summary"])


if __name__ == "__main__":
    unittest.main()
