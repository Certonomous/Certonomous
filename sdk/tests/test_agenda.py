"""The operational research agenda: drafting, ranking, persistence, the
human veto endpoints, and the GUI rails.

Covered here:

* drafting proposals from fixture records (reports, an inconclusive ladder,
  a graded body outside its band, the fleet-ledger study, the inbox);
* dedupe by objective and ranking determinism;
* atomic docket persistence;
* style rails on every user-visible proposal field, for fixtures and for the
  real repository state (the seeded docket);
* the approve/dismiss endpoints: approving launches through the ordinary
  mission path only when the compute audit says yes, queues honestly when it
  says no, and dismissing always requires a reason;
* the control-room agenda renderer: syntax-checked and executed under node
  against a fixture docket, using only classes the stylesheet already has.
"""
from __future__ import annotations

import http.client
import json
import os
import random
import re
import shutil
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path

from chief_engineer import agenda

SDK = Path(__file__).resolve().parents[1]
CONTROL_ROOM = SDK / "chief_engineer" / "control_room.html"

_ENV_KEYS = (
    "CERTONOMOUS_AGENDA_DIR", "CERTONOMOUS_REPORT_ROOTS",
    "CERTONOMOUS_TMR_CARD", "CERTONOMOUS_UQ_STUDIES",
    "CERTONOMOUS_CREDENTIALS", "CERTONOMOUS_LEDGER_STUDY",
    "CHIEF_ENGINEER_STATE_DIR", "CHIEF_ENGINEER_WORKDIR",
)


class _EnvMixin:
    """Save/restore the agenda-related environment around each test."""

    def _snap_env(self):
        self._saved = {key: os.environ.get(key) for key in _ENV_KEYS}
        self.addCleanup(self._restore_env)

    def _restore_env(self):
        for key, value in self._saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def _clear_env(self):
        for key in _ENV_KEYS:
            os.environ.pop(key, None)


def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _fixture_records(root: Path) -> None:
    """A miniature lab record set that genuinely supports proposals."""
    reports = root / "reports"
    _write_json(reports / "study.events.json", {"events": [{
        "event": "report.ready",
        "payload": {
            "title": "Fixture study: test wing",
            "next_investigations": [
                "Harmonic-balance cycle solve: resolve the coupled harmonics "
                "of one cycle instead of independent phase points",
                "Sweep the approach angle: map how the force builds as the "
                "body meets the flow off-axis",
            ]}}]})
    _write_json(root / "uq" / "b52.json", {
        "body": "b52",
        "levels": [
            {"tag": "coarse", "cells": 40656, "cd": 0.0551},
            {"tag": "medium", "cells": 107489, "cd": 0.0448},
            {"tag": "production", "cells": 193880, "cd": 0.0472},
        ],
        "numerical": {"conclusive": False,
                      "method": "rungs not monotone; conservative band, "
                                "largest spread times 1.25"}})
    _write_json(root / "results" / "naca0012_wing.json", {
        "name": "naca0012_wing", "tier": "TREND ONLY",
        "cd_compared": 0.0223, "reference_cd": 0.009,
        "reference_source": "Abbott and von Doenhoff, Theory of Wing "
                            "Sections (1959), NACA 0012 section data",
        "wall_minutes": 3.0})
    _write_json(root / "learned_study.json", {
        "families": {"reduced-order": {"attempted": 13055,
                                       "wall_seconds": 12.8}},
        "valve": {
            "n": 13055,
            "best": {"opening_angle_deg": 84.99,
                     "cycle_weighted_loss_Pa": 1267.28,
                     "ledger_index": 11072},
            "trend_loss_vs_angle": {"fit": {"slope": -148.69, "r2": 0.75,
                                            "n": 13055}}}})
    _write_json(root / "tmr_card.json", {
        "grids": [
            {"level": "coarse", "cells": 816, "cd": 0.0026687,
             "wall_seconds": 7.2},
            {"level": "medium", "cells": 3264, "cd": 0.0027812,
             "wall_seconds": 23.9},
            {"level": "fine", "cells": 13056, "cd": 0.0028343,
             "wall_seconds": 278.4},
        ],
        "comparison": {"cfl3d_cd_ladder": [0.0027062, 0.0027851,
                                           0.0028260]}})
    inbox = root / "agenda" / "proposals"
    _write_json(inbox / "reading-1.json", {
        "id": "r-fixture-1",
        "objective": "Adopt a Sobol sensitivity mission type",
        "rationale": "Reading program proposal from a cited method text.",
        "citations": ["Saltelli, Global Sensitivity Analysis"],
        "est_core_min": 6, "source_kind": "reading",
        "expected_knowledge_gain": "Variance apportioned across inputs"})
    # Duplicate objective of the ledger drafter's proposal: must dedupe.
    _write_json(inbox / "dupe.json", {
        "objective": "Extend the valve opening-angle sweep past 80 degrees",
        "rationale": "Duplicate of a drafted proposal."})
    # Violates the style rails (raw URL): must be skipped, never rendered.
    _write_json(inbox / "bad.json", {
        "objective": "Read this website",
        "rationale": "See https://example.com for details."})


def _point_env_at(root: Path) -> None:
    os.environ["CERTONOMOUS_AGENDA_DIR"] = str(root / "agenda")
    os.environ["CERTONOMOUS_REPORT_ROOTS"] = str(root / "reports")
    os.environ["CERTONOMOUS_TMR_CARD"] = str(root / "tmr_card.json")
    os.environ["CERTONOMOUS_UQ_STUDIES"] = str(root / "uq")
    os.environ["CERTONOMOUS_CREDENTIALS"] = str(root / "results")
    os.environ["CERTONOMOUS_LEDGER_STUDY"] = str(root / "learned_study.json")


class DraftingFromRecords(_EnvMixin, unittest.TestCase):
    def setUp(self):
        self._snap_env()
        self._clear_env()
        self.root = Path(tempfile.mkdtemp(prefix="agenda-fixture-"))
        self.addCleanup(shutil.rmtree, self.root, True)
        _fixture_records(self.root)
        _point_env_at(self.root)

    def test_every_record_kind_drafts_a_proposal(self):
        proposals = agenda.draft_all()
        kinds = {p["source_kind"] for p in proposals}
        self.assertLessEqual({"report", "capability", "gate", "ledger",
                              "reading"}, kinds)
        objectives = {p["objective"] for p in proposals}
        self.assertIn("Extend the valve opening-angle sweep past 80 degrees",
                      objectives)
        self.assertIn("Harmonic-balance cycle solve", objectives)
        self.assertIn("Close the validation gap on the NACA 0012 finite wing",
                      objectives)
        self.assertTrue(any("fourth refinement rung" in o
                            for o in objectives))
        self.assertTrue(any("bump-in-channel" in o for o in objectives))

    def test_tmr_sequence_advances_once_bump_is_measured(self):
        # With a measured bump card beside the flat-plate card, the drafter
        # proposes the sequence's next case (NACA 0012), not the bump again.
        _write_json(self.root / "bump_sst.json", {
            "grids": [{"cells": 3520, "wall_seconds": 102.0},
                      {"cells": 14080, "wall_seconds": 815.0},
                      {"cells": 56320, "wall_seconds": 7120.0}]})
        objectives = {p["objective"] for p in agenda.draft_all()}
        self.assertTrue(any("NACA 0012" in o for o in objectives))
        self.assertFalse(any("bump-in-channel verification case" in o
                             for o in objectives))
        naca = next(p for p in agenda.draft_all()
                    if "NACA 0012" in p["objective"])
        # Cost is anchored to the measured bump ladder, never invented.
        self.assertIn("core minutes on this machine", naca["cost_basis"])

    def test_rationales_cite_the_actual_record(self):
        by_objective = {p["objective"]: p for p in agenda.draft_all()}
        report_kid = by_objective["Harmonic-balance cycle solve"]
        self.assertIn("Fixture study: test wing", report_kid["rationale"])
        self.assertEqual(report_kid["citations"],
                         ["Fixture study: test wing"])
        ladder = next(p for p in by_objective.values()
                      if "refinement rung" in p["objective"])
        self.assertIn("rungs not monotone", ladder["rationale"])
        valve = by_objective[
            "Extend the valve opening-angle sweep past 80 degrees"]
        self.assertIn("1267 Pa at 85.0 degrees", valve["rationale"])

    def test_costs_are_measured_or_labeled_estimate(self):
        for proposal in agenda.draft_all():
            basis = proposal["cost_basis"]
            self.assertTrue(
                basis.startswith("measured") or "estimate" in basis,
                f"{proposal['objective']}: cost basis {basis!r} is neither "
                f"measured history nor labeled an estimate")

    def test_launchable_gate_carries_a_prompt(self):
        by_objective = {p["objective"]: p for p in agenda.draft_all()}
        naca = by_objective[
            "Close the validation gap on the NACA 0012 finite wing"]
        self.assertIn("NACA 0012", naca["launch_prompt"])

    def test_a_repair_is_not_priced_from_the_run_it_repairs(self):
        """The fixture body is out of band and its record carries a 3.0
        minute wall time. That is the run this proposal exists to replace,
        so it is a floor and never the price."""
        by_objective = {p["objective"]: p for p in agenda.draft_all()}
        naca = by_objective[
            "Close the validation gap on the NACA 0012 finite wing"]
        basis = naca["cost_basis"]
        self.assertFalse(basis.startswith("measured"), basis)
        self.assertIn("estimate", basis)
        self.assertIn("3.0 minutes of wall time", basis)
        self.assertIn("floor", basis)
        self.assertNotEqual(naca["est_core_min"], 3.0)
        # And the basis it replaced would not survive intake today.
        self.assertEqual(agenda.cost_basis_violations(naca), [])
        self.assertTrue(agenda.cost_basis_violations({
            "id": "x", "objective": "y",
            "cost_basis": "measured: the prior graded solve of this body "
                          "ran 3.0 minutes of wall time"}))

    def test_a_superseded_run_is_refused_at_intake_and_named(self):
        refused = agenda.cost_basis_violations({
            "id": "x", "objective": "y",
            "cost_basis": "measured: the 67,826-cell run took 1.8 minutes"})
        self.assertEqual(len(refused), 1)
        self.assertIn("NACA 4412", refused[0])
        self.assertIn("cost_basis", refused[0])
        # The refusal is visible, not a silent drop.
        self.assertTrue(any(entry["id"] == "x"
                            for entry in agenda.refused_cost_bases()))
        # A basis that names the run in order to disclose it is not pricing
        # from it and is allowed.
        self.assertEqual(agenda.cost_basis_violations({
            "cost_basis": "measured on the 4412 precedent; the superseded "
                          "67,826-cell run is not what this is priced from"}),
            [])

    def test_a_defective_cost_basis_never_reaches_a_proposal(self):
        bad = {"objective": "o", "rationale": "r", "citations": ["c"],
               "est_core_min": 3.04, "expected_knowledge_gain": "g",
               "cost_basis": "measured: the prior graded solve of this body "
                             "ran 3.0 minutes of wall time",
               "source_kind": "gate"}
        self.assertTrue(agenda.proposal_violations(bad))

    def test_dedupe_by_objective(self):
        proposals = agenda.draft_all()
        objectives = [agenda.normalize_objective(p["objective"])
                      for p in proposals]
        self.assertEqual(len(objectives), len(set(objectives)))
        # The inbox duplicate lost to the drafted original (drafters first).
        valve = next(p for p in proposals if p["objective"] ==
                     "Extend the valve opening-angle sweep past 80 degrees")
        self.assertEqual(valve["source_kind"], "ledger")

    def test_rail_breaking_inbox_proposal_is_skipped(self):
        objectives = {p["objective"] for p in agenda.draft_all()}
        self.assertNotIn("Read this website", objectives)

    def test_refresh_persists_and_preserves_decisions(self):
        first = agenda.refresh_docket()
        self.assertTrue(agenda.docket_path().exists())
        target = first[0]["id"]
        agenda.set_status(target, "dismissed", dismiss_reason="fixture veto")
        second = agenda.refresh_docket()
        decided = next(p for p in second if p["id"] == target)
        self.assertEqual(decided["status"], "dismissed")
        self.assertEqual(decided["dismiss_reason"], "fixture veto")
        self.assertIn("decided_at", decided)


class RankingAndPersistence(_EnvMixin, unittest.TestCase):
    def setUp(self):
        self._snap_env()
        self._clear_env()
        self.root = Path(tempfile.mkdtemp(prefix="agenda-rank-"))
        self.addCleanup(shutil.rmtree, self.root, True)
        os.environ["CERTONOMOUS_AGENDA_DIR"] = str(self.root)

    @staticmethod
    def _proposal(objective, kind, est):
        return {"id": agenda.proposal_id(objective), "objective": objective,
                "rationale": "r", "citations": [], "est_core_min": est,
                "cost_basis": "estimate", "expected_knowledge_gain": "g",
                "source_kind": kind, "status": "proposed",
                "created_at": "2026-07-24T00:00:00+00:00"}

    def test_ranking_is_gain_per_core_min_and_deterministic(self):
        items = [
            self._proposal("cheap gate", "gate", 1.0),        # 3.0
            self._proposal("cheap ledger", "ledger", 1.0),    # 2.0
            self._proposal("mid gate", "gate", 10.0),         # 0.3
            self._proposal("costly capability", "capability", 60.0),  # 0.033
            self._proposal("report item", "report", 20.0),    # 0.05
            self._proposal("free screen", "ledger", 0.2),     # floored: 2.0
        ]
        expected = ["cheap gate", "cheap ledger", "free screen", "mid gate",
                    "report item", "costly capability"]
        for seed in (1, 7, 42):
            shuffled = items[:]
            random.Random(seed).shuffle(shuffled)
            self.assertEqual([p["objective"] for p in agenda.ranked(shuffled)],
                             expected)

    def test_rank_floor_stops_divide_by_nearly_zero(self):
        cheap = self._proposal("free", "ledger", 0.001)
        self.assertEqual(agenda.rank_value(cheap), 2.0)
        missing = self._proposal("no estimate", "ledger", None)
        self.assertEqual(agenda.rank_value(missing), 2.0)

    def test_docket_saves_atomically(self):
        proposals = [self._proposal("one", "gate", 2.0)]
        agenda.save_docket(proposals)
        path = agenda.docket_path()
        self.assertTrue(path.exists())
        self.assertEqual(len(agenda.load_docket()), 1)
        leftovers = list(path.parent.glob("*.tmp"))
        self.assertEqual(leftovers, [], "staging file left behind")
        # A second save replaces cleanly.
        agenda.save_docket(proposals + [self._proposal("two", "gate", 2.0)])
        self.assertEqual(len(agenda.load_docket()), 2)


class StyleRails(_EnvMixin, unittest.TestCase):
    def setUp(self):
        self._snap_env()

    def test_banned_tokens_are_flagged(self):
        self.assertTrue(agenda.text_violations("a dash — here"))
        self.assertTrue(agenda.text_violations("watch it live tonight"))
        self.assertTrue(agenda.text_violations("a solver backed number"))
        self.assertTrue(agenda.text_violations("our conceptual model"))
        self.assertTrue(agenda.text_violations("see https://example.com"))
        self.assertTrue(agenda.text_violations("read the HANDOFF.md note"))
        self.assertTrue(agenda.text_violations("in docs/physics_rules.yaml"))
        self.assertEqual(agenda.text_violations(
            "a delivered, reduced-order screen at 85 degrees"), [])

    def test_real_repo_drafts_pass_the_rails_and_seed_six(self):
        """The seeded docket: the real records support at least six clean
        proposals, every field on the rails."""
        self._clear_env()
        proposals = agenda.draft_all()
        self.assertGreaterEqual(len(proposals), 6)
        for proposal in proposals:
            self.assertEqual(
                agenda.proposal_violations(proposal), [],
                f"{proposal['objective']}: banned text reached a proposal")
            for field in ("objective", "rationale",
                          "expected_knowledge_gain", "cost_basis"):
                self.assertTrue(str(proposal.get(field) or "").strip(),
                                f"{proposal['objective']}: empty {field}")
            self.assertTrue(proposal["citations"],
                            f"{proposal['objective']}: no citation")


class _FakeAudit:
    def __init__(self, fits: bool):
        self.fits = fits

    def panel(self):
        return {"verdict": "FITS" if self.fits else "CONSTRAINED",
                "requested": 4, "capacity": 4 if self.fits else 0,
                "reason": "fixture audit"}


class AgendaEndpoints(_EnvMixin, unittest.TestCase):
    """The human veto over live HTTP: nothing runs without the click, and
    the click itself respects the compute audit."""

    def setUp(self):
        self._snap_env()
        self._clear_env()
        self.root = Path(tempfile.mkdtemp(prefix="agenda-http-"))
        self.addCleanup(shutil.rmtree, self.root, True)
        # Point every drafter at empty fixture ground so the docket holds
        # exactly the fixtures below.
        for sub in ("agenda", "reports", "uq", "results"):
            (self.root / sub).mkdir(parents=True, exist_ok=True)
        _point_env_at(self.root)
        os.environ["CHIEF_ENGINEER_STATE_DIR"] = str(self.root / "state")
        os.environ["CHIEF_ENGINEER_WORKDIR"] = str(self.root / "work")

        self.launchable = {
            "id": "agp-fixture-run", "objective": "Fixture runnable mission",
            "rationale": "Backed by a fixture record.",
            "citations": ["Fixture record"], "est_core_min": 2.0,
            "cost_basis": "estimate", "expected_knowledge_gain": "gain",
            "source_kind": "gate", "status": "proposed",
            "created_at": "2026-07-24T00:00:00+00:00",
            "launch_prompt": "zzz qqq unrouteable fixture prompt"}
        self.unlaunchable = {
            "id": "agp-fixture-idea", "objective": "Fixture capability idea",
            "rationale": "No runnable workflow maps to this yet.",
            "citations": ["Fixture record"], "est_core_min": 60.0,
            "cost_basis": "estimate", "expected_knowledge_gain": "gain",
            "source_kind": "capability", "status": "proposed",
            "created_at": "2026-07-24T00:00:00+00:00"}
        agenda.save_docket([self.launchable, self.unlaunchable])

        from chief_engineer import server as server_mod
        self.server_mod = server_mod
        self._real_audit = server_mod._agenda_audit
        self.addCleanup(setattr, server_mod, "_agenda_audit",
                        self._real_audit)
        self.httpd = server_mod.ThreadingHTTPServer(
            ("127.0.0.1", 0), server_mod.Handler)
        threading.Thread(target=self.httpd.serve_forever,
                         daemon=True).start()
        self.addCleanup(self.httpd.server_close)
        self.addCleanup(self.httpd.shutdown)
        self.port = self.httpd.server_address[1]

    def _request(self, method, path, payload=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        body = json.dumps(payload) if payload is not None else None
        headers = {"Content-Type": "application/json"} if body else {}
        conn.request(method, path, body=body, headers=headers)
        response = conn.getresponse()
        data = json.loads(response.read() or b"{}")
        conn.close()
        return response.status, data

    def test_get_agenda_returns_docket_and_launches_nothing(self):
        before = len(self.server_mod._missions)
        status, data = self._request("GET", "/api/agenda")
        self.assertEqual(status, 200)
        ids = [p["id"] for p in data["proposals"]]
        self.assertIn("agp-fixture-run", ids)
        self.assertIn("agp-fixture-idea", ids)
        values = [agenda.rank_value(p) for p in data["proposals"]]
        self.assertEqual(values, sorted(values, reverse=True))
        self.assertEqual(len(self.server_mod._missions), before)

    def test_approve_without_capacity_queues_honestly(self):
        self.server_mod._agenda_audit = lambda workers: _FakeAudit(False)
        before = len(self.server_mod._missions)
        status, data = self._request("POST", "/api/agenda/approve",
                                     {"id": "agp-fixture-run"})
        self.assertEqual(status, 200)
        self.assertFalse(data["launched"])
        self.assertEqual(data["proposal"]["status"], "approved-queued")
        self.assertEqual(data["audit"]["verdict"], "CONSTRAINED")
        self.assertEqual(len(self.server_mod._missions), before,
                         "a constrained approval must not start a mission")
        # Still open: a later click may launch it once capacity exists.
        self.assertIn(agenda.get_proposal("agp-fixture-run")["status"],
                      agenda.OPEN_STATUSES)

    def test_approve_with_capacity_launches_through_the_mission_path(self):
        self.server_mod._agenda_audit = lambda workers: _FakeAudit(True)
        status, data = self._request("POST", "/api/agenda/approve",
                                     {"id": "agp-fixture-run"})
        self.assertEqual(status, 202)
        self.assertTrue(data["launched"])
        mission_id = data["mission_id"]
        record = self.server_mod._record(mission_id)
        self.assertIsNotNone(record, "mission not registered on the real "
                                     "mission path")
        self.assertEqual(record.request,
                         self.launchable["launch_prompt"])
        self.assertIn("route", data)
        updated = agenda.get_proposal("agp-fixture-run")
        self.assertEqual(updated["status"], "approved")
        self.assertEqual(updated["mission_id"], mission_id)
        # The launched mission is visible on the ordinary mission API.
        status, detail = self._request("GET", f"/api/missions/{mission_id}")
        self.assertEqual(status, 200)
        self.assertEqual(detail["request"],
                         self.launchable["launch_prompt"])

    def test_approve_without_prompt_records_and_runs_nothing(self):
        self.server_mod._agenda_audit = lambda workers: _FakeAudit(True)
        before = len(self.server_mod._missions)
        status, data = self._request("POST", "/api/agenda/approve",
                                     {"id": "agp-fixture-idea"})
        self.assertEqual(status, 200)
        self.assertFalse(data["launched"])
        self.assertEqual(data["proposal"]["status"], "approved")
        self.assertEqual(len(self.server_mod._missions), before)

    def test_dismiss_requires_a_reason(self):
        status, data = self._request("POST", "/api/agenda/dismiss",
                                     {"id": "agp-fixture-idea"})
        self.assertEqual(status, 400)
        self.assertIn("reason", data["error"])
        self.assertEqual(agenda.get_proposal("agp-fixture-idea")["status"],
                         "proposed")

    def test_dismiss_archives_with_the_reason(self):
        status, data = self._request(
            "POST", "/api/agenda/dismiss",
            {"id": "agp-fixture-idea", "reason": "not this quarter"})
        self.assertEqual(status, 200)
        self.assertEqual(data["proposal"]["status"], "dismissed")
        self.assertEqual(data["proposal"]["dismiss_reason"],
                         "not this quarter")
        # A second decision on a decided proposal is refused.
        status, data = self._request(
            "POST", "/api/agenda/dismiss",
            {"id": "agp-fixture-idea", "reason": "again"})
        self.assertEqual(status, 400)

    def test_unknown_proposal_is_a_404(self):
        status, _ = self._request("POST", "/api/agenda/approve",
                                  {"id": "agp-nope"})
        self.assertEqual(status, 404)


_NODE = shutil.which("node")


class AgendaGui(unittest.TestCase):
    """The control-room agenda content: valid script, cards rendered from a
    fixture docket, and zero new CSS or geometry."""

    @classmethod
    def setUpClass(cls):
        cls.html = CONTROL_ROOM.read_text(encoding="utf-8")
        cls.script = cls.html.split("<script>", 1)[1].split("</script>", 1)[0]
        cls.style = cls.html.split("<style>", 1)[1].split("</style>", 1)[0]

    def test_agenda_endpoints_are_wired(self):
        self.assertIn("/api/agenda", self.script)
        self.assertIn("/api/agenda/approve", self.script)
        self.assertIn("/api/agenda/dismiss", self.script)
        self.assertIn("Morning digest", self.script)

    @unittest.skipUnless(_NODE, "node not installed")
    def test_whole_script_parses_under_node(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "control_room_script.js"
            path.write_text(self.script, encoding="utf-8")
            done = subprocess.run([_NODE, "--check", str(path)],
                                  capture_output=True, text=True, timeout=60)
            self.assertEqual(done.returncode, 0, done.stderr)

    def _render_block(self):
        match = re.search(r"// AGENDA-RENDER-BEGIN\n(.*?)// AGENDA-RENDER-END",
                          self.script, re.S)
        self.assertIsNotNone(match, "agenda render block markers missing")
        esc_line = next(line for line in self.script.splitlines()
                        if line.strip().startswith("const esc ="))
        # The docket cards are typeset like every other camera surface, so the
        # renderer calls subHTML. Carry the typesetter in with `esc`: without
        # it the block runs against a name that is not there and the fixture
        # fails on the page's own house style rather than on the agenda.
        typeset = re.search(
            r"const SUB_GROUPS = .*?^function subHTML\(text\) \{.*?\}$",
            self.script, re.S | re.M)
        self.assertIsNotNone(typeset, "the subscript typesetter moved")
        return esc_line + "\n" + typeset.group(0) + "\n" + match.group(1)

    @unittest.skipUnless(_NODE, "node not installed")
    def test_renderer_builds_cards_from_a_fixture_docket(self):
        docket = {"proposals": [
            {"id": "p1", "objective": "Fixture objective one",
             "rationale": "Because the record says so.",
             "citations": ["Some report title"], "est_core_min": 3.0,
             "cost_basis": "measured: the prior solve ran 3.0 minutes",
             "expected_knowledge_gain": "A validated credential",
             "source_kind": "gate", "status": "proposed",
             "launch_prompt": "Mesh and solve the fixture"},
            {"id": "p2", "objective": "Fixture objective two",
             "rationale": "Also on the record.", "citations": [],
             "est_core_min": None, "cost_basis": "estimate",
             "expected_knowledge_gain": "", "source_kind": "report",
             "status": "dismissed", "dismiss_reason": "not now"},
        ]}
        js = (self._render_block()
              + f"\nconst out = renderAgendaDocket({json.dumps(docket)});"
              + "\nconsole.log(out);")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "render_fixture.js"
            path.write_text(js, encoding="utf-8")
            done = subprocess.run([_NODE, str(path)], capture_output=True,
                                  text=True, timeout=60)
        self.assertEqual(done.returncode, 0, done.stderr)
        out = done.stdout
        self.assertIn("Morning digest", out)
        self.assertIn("Fixture objective one", out)
        self.assertIn('data-agenda-act="approve"', out)
        self.assertIn('data-agenda-act="dismiss"', out)
        self.assertIn("data-id=\"p1\"", out)
        self.assertIn("Some report title", out)
        self.assertIn("not now", out)          # dismissal reason shown
        # Decided proposals carry no buttons.
        self.assertNotIn('data-id="p2"', out)
        self._assert_no_new_css(out)

    def _assert_no_new_css(self, rendered: str):
        """Zero layout change: the rendered agenda uses only classes the
        frozen stylesheet already defines, and no inline geometry."""
        self.assertNotIn("style=", rendered)
        for token in set(re.findall(r'class="([^"]+)"', rendered)):
            for cls in token.split():
                self.assertIn(f".{cls}", self.style,
                              f"agenda markup invented a new class: {cls}")

    def test_no_agenda_rules_were_added_to_the_stylesheet(self):
        """The <style> block stays free of agenda-specific rules: the cards
        ride existing classes only."""
        for needle in ("agenda-docket", "proposal-card", "morning",
                       "approve", "dismiss"):
            self.assertNotIn(needle, self.style.lower())


if __name__ == "__main__":
    unittest.main()
