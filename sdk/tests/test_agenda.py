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
from unittest import mock

from chief_engineer import agenda

# The one module that names this repository's tree (MOVE_MAP batch 3).
# Every name it exports is bound to a legacy/successor PAIR resolved
# against the filesystem at import, so the constants below are correct
# before the move, between batches and after it, with no edit here.
import sys as _sys  # noqa: E402
import pathlib as _pathlib  # noqa: E402
_LAB_PATHS_DIR = str(_pathlib.Path(__file__).resolve().parents[2]
                     / "scripts")
if _LAB_PATHS_DIR not in _sys.path:
    _sys.path.insert(0, _LAB_PATHS_DIR)
import lab_paths  # noqa: E402

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
        "hard_criterion": "no-case",
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

    def test_a_rail_tripped_naca_draft_is_dropped_not_none(self):
        # Finding A-1, family supervision pass 2026-08-07: _proposal returns
        # None on a style-rail trip, and the NACA 0012 branch used to hand
        # that None straight into draft_all, which crashes on
        # proposal["objective"]. A rail-trip is a dropped proposal, never a
        # crashed refresh.
        _write_json(self.root / "bump_sst.json", {
            "grids": [{"cells": 3520, "wall_seconds": 102.0}]})
        with mock.patch.object(agenda, "_draft_tmr_naca0012",
                               return_value=None):
            self.assertEqual(agenda.draft_tmr_proposals(), [])
            for proposal in agenda.draft_all():  # must not raise
                self.assertIsInstance(proposal, dict)

    def test_a_skipped_inbox_file_is_recorded_not_silent(self):
        # Finding A-3, family supervision pass 2026-08-07: nineteen of
        # fifty-six real inbox files were being silently dropped at intake.
        # A refusal is visible or it is a filter nobody can question.
        agenda.read_inbox()
        refused = {entry["file"]: entry for entry in agenda.refused_inbox()}
        self.assertIn("bad.json", refused)
        self.assertTrue(refused["bad.json"]["violations"])
        self.assertEqual(refused["bad.json"]["objective"], "Read this website")
        # An accepted file is not in the refused ledger.
        self.assertNotIn("reading-1.json", refused)

    def test_an_inbox_done_without_outcome_is_refused_at_intake(self):
        # Finding A-2, family supervision pass 2026-08-07: the module's own
        # done-requires-outcome rule bound only in set_status, so an inbox
        # file arriving already closed but with no outcome rode through.
        _write_json(self.root / "agenda" / "proposals" / "closed.json", {
            "objective": "Close this quietly",
            "rationale": "r", "citations": [],
            "source_kind": "reading", "hard_criterion": "no-case",
            "status": "done",
            "created_at": "2026-08-07T00:00:00+00:00"})
        objectives = {p["objective"] for p in agenda.read_inbox()}
        self.assertNotIn("Close this quietly", objectives)
        refused = {entry["file"] for entry in agenda.refused_inbox()}
        self.assertIn("closed.json", refused)

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

    def test_every_draft_names_its_hardness_floor_answer(self):
        """P-3.1: a drafted proposal is a new proposal, so every one carries
        a machine-readable hard_criterion from the closed list."""
        allowed = set(agenda.HARD_CRITERIA) | set(agenda.HARD_CRITERION_WORDS)
        for proposal in agenda.draft_all():
            self.assertIn(proposal.get("hard_criterion"), allowed,
                          f"{proposal['objective']}: hard_criterion "
                          f"{proposal.get('hard_criterion')!r}")

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


class SchemaRails(unittest.TestCase):
    """P-1.1 and P-3.1, carried out 2026-08-05: an unknown source_kind and a
    missing or unrecognised hard_criterion are proposal violations at intake
    for new proposals, and grandfathered rows keep loading and ranking."""

    @staticmethod
    def _proposal(created="2026-08-05T08:00:00+00:00", kind="gate",
                  hard="existing-family"):
        item = {"id": "agp-schema-fixture", "objective": "o",
                "rationale": "r", "citations": ["c"], "est_core_min": 2.0,
                "cost_basis": "estimate", "expected_knowledge_gain": "g",
                "source_kind": kind, "status": "proposed",
                "created_at": created}
        if hard is not None:
            item["hard_criterion"] = hard
        return item

    def test_a_compliant_new_proposal_passes(self):
        self.assertEqual(agenda.proposal_violations(self._proposal()), [])

    def test_an_unknown_source_kind_is_refused_not_defaulted(self):
        found = agenda.proposal_violations(self._proposal(kind="vibes"))
        self.assertTrue(any(f.startswith("source_kind:") for f in found),
                        found)

    def test_every_kind_in_use_carries_a_stated_score(self):
        """The docket in use carries these eight kinds; every one scores
        explicitly, so no new proposal ranks on the silent default."""
        for kind in ("gate", "capability", "ledger", "report", "measurement",
                     "reading", "challenge", "inbox"):
            self.assertEqual(
                agenda.proposal_violations(self._proposal(kind=kind)), [],
                f"{kind} refused at intake")

    def test_a_missing_hard_criterion_is_refused(self):
        found = agenda.proposal_violations(self._proposal(hard=None))
        self.assertTrue(any(f.startswith("hard_criterion:") for f in found),
                        found)

    def test_a_value_outside_the_closed_list_is_refused(self):
        for bad in ("7", "0", "hardish", "criterion 3"):
            found = agenda.proposal_violations(self._proposal(hard=bad))
            self.assertTrue(
                any(f.startswith("hard_criterion:") for f in found),
                f"{bad!r} was accepted")

    def test_the_six_numbers_pass_as_int_or_string(self):
        for good in ("1", "6", 3, "existing-family", "regression-test",
                     "instrument-check", "no-case", "below-floor"):
            self.assertEqual(
                agenda.proposal_violations(self._proposal(hard=good)), [],
                f"{good!r} refused")

    def test_grandfathered_rows_are_not_refused_retroactively(self):
        """The 221 docket entries of 2026-08-04 are never rewritten: an old
        created_at exempts a row from both new field checks, and it still
        ranks (on the default, recorded in unscored_kinds)."""
        old = self._proposal(created="2026-08-04T12:00:00+00:00",
                             kind="somekind-nobody-scored", hard=None)
        self.assertEqual(agenda.proposal_violations(old), [])
        self.assertEqual(agenda.rank_value(old),
                         agenda._GAIN_DEFAULT / 2.0)
        self.assertIn("somekind-nobody-scored", agenda.unscored_kinds())

    def test_a_done_proposal_without_an_outcome_is_refused(self):
        # Finding A-2, 2026-08-07: the docstring's done-requires-outcome
        # rule now binds at intake for schema-bound records, not only in
        # set_status.
        item = self._proposal()
        item["status"] = "done"
        found = agenda.proposal_violations(item)
        self.assertTrue(any(f.startswith("status: done") for f in found),
                        found)
        item["outcome"] = "the work found the number and it is stated"
        self.assertEqual(agenda.proposal_violations(item), [])

    def test_a_grandfathered_done_row_is_not_refused_for_its_outcome(self):
        old = self._proposal(created="2026-08-04T12:00:00+00:00")
        old["status"] = "done"
        self.assertEqual(agenda.proposal_violations(old), [])

    def test_a_dateless_proposal_is_new_by_assumption(self):
        found = agenda.proposal_violations(self._proposal(created="",
                                                          hard=None))
        self.assertTrue(any(f.startswith("hard_criterion:") for f in found))

    def test_the_real_docket_still_loads_and_ranks(self):
        """Grandfathering is only real if the seeded docket, two of whose
        rows carry no source_kind at all, ranks without a refusal."""
        docket = lab_paths.AGENDA / "docket.json"
        if not docket.exists():
            self.skipTest("no docket in this tree")
        rows = json.loads(docket.read_text(encoding="utf-8"))["proposals"]
        ranked_rows = agenda.ranked(rows)
        self.assertEqual(len(ranked_rows), len(rows))


class ArchiveReplayRail(_EnvMixin, unittest.TestCase):
    """P-1.4, carried out 2026-08-05: a proposal whose own text adds a
    detection or monitor rule carries an archive-replay record naming the
    corpus, the fires, the fatals and the motivating case, or it is refused
    at intake. S12's replay over 760 quantity-histories is the pattern;
    S7, adopted without one and measured firing on 68 of 106 completed
    runs, is the reason."""

    REPLAY = {
        "corpus": "760 quantity-histories from 380 archived coefficient "
                  "files, 718 gradeable",
        "fires": 36, "fatal": 0,
        "motivating_case": "fires on the flat-plate rung stopped at 15000, "
                           "silent on the same case settled at 21000"}

    @staticmethod
    def _proposal(rationale, created="2026-08-05T08:00:00+00:00",
                  replay=None):
        item = {"id": "agp-replay-fixture", "objective": "o",
                "rationale": rationale, "citations": ["c"],
                "est_core_min": 2.0, "cost_basis": "estimate",
                "expected_knowledge_gain": "g", "source_kind": "gate",
                "hard_criterion": "no-case", "status": "proposed",
                "created_at": created}
        if replay is not None:
            item["archive_replay"] = replay
        return item

    DETECTION = ("Adds a monitor rule that stops a run when the residual "
                 "history goes quiet before its target.")

    def test_a_detection_rule_without_a_replay_is_refused(self):
        found = agenda.proposal_violations(self._proposal(self.DETECTION))
        self.assertTrue(any(f.startswith("archive_replay:") for f in found),
                        found)
        self.assertTrue(any("S12" in f for f in found), found)

    def test_a_detection_rule_with_a_full_replay_passes(self):
        item = self._proposal(self.DETECTION, replay=dict(self.REPLAY))
        self.assertEqual(agenda.proposal_violations(item), [])

    def test_a_zero_fire_replay_is_a_measurement_not_an_omission(self):
        """S2 fires on nothing and that replay line stands; 0 is stated."""
        replay = dict(self.REPLAY, fires=0)
        item = self._proposal(self.DETECTION, replay=replay)
        self.assertEqual(agenda.proposal_violations(item), [])

    def test_an_incomplete_replay_names_what_it_is_missing(self):
        replay = {k: v for k, v in self.REPLAY.items() if k != "fatal"}
        found = agenda.proposal_violations(
            self._proposal(self.DETECTION, replay=replay))
        self.assertTrue(any(f.startswith("archive_replay:") and "fatal" in f
                            for f in found), found)

    def test_an_ordinary_proposal_owes_no_replay(self):
        item = self._proposal("The refinement study ended inconclusive and "
                              "a further rung can settle the observed order.")
        self.assertEqual(agenda.proposal_violations(item), [])
        self.assertFalse(agenda.is_detection_rule_proposal(item))

    def test_grandfathered_rows_are_not_refused_retroactively(self):
        old = self._proposal(self.DETECTION,
                             created="2026-08-04T12:00:00+00:00")
        self.assertEqual(agenda.proposal_violations(old), [])

    def test_the_inbox_carries_a_replay_record_through(self):
        """A compliant detection-rule file keeps its measurement on ingest;
        the same file without one is skipped, never quietly excused."""
        self._snap_env()
        self._clear_env()
        root = Path(tempfile.mkdtemp(prefix="agenda-replay-"))
        self.addCleanup(shutil.rmtree, root, True)
        _point_env_at(root)
        inbox = root / "agenda" / "proposals"
        _write_json(inbox / "with-replay.json", {
            "objective": "Detect the quiet stall",
            "rationale": self.DETECTION, "citations": ["Monitor standard"],
            "est_core_min": 1.0, "source_kind": "measurement",
            "hard_criterion": "no-case",
            "expected_knowledge_gain": "A measured rule",
            "archive_replay": dict(self.REPLAY)})
        _write_json(inbox / "without-replay.json", {
            "objective": "Detect the loud stall",
            "rationale": self.DETECTION, "citations": ["Monitor standard"],
            "est_core_min": 1.0, "source_kind": "measurement",
            "hard_criterion": "no-case",
            "expected_knowledge_gain": "An unmeasured rule"})
        loaded = agenda.read_inbox()
        objectives = {p["objective"] for p in loaded}
        self.assertIn("Detect the quiet stall", objectives)
        self.assertNotIn("Detect the loud stall", objectives)
        kept = next(p for p in loaded
                    if p["objective"] == "Detect the quiet stall")
        self.assertEqual(kept["archive_replay"]["fires"], 36)


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


class PremiseRailTests(unittest.TestCase):
    """Charter 4 disqualifiers 11 and 12, replayed against the real docket.

    This runs in the suite rather than only when somebody remembers, because
    the whole point of the rule is that nobody remembered to open the record.
    """

    DOCKET = lab_paths.AGENDA / "docket.json"

    def setUp(self):
        if not self.DOCKET.exists():
            self.skipTest("no docket in this tree")
        data = json.loads(self.DOCKET.read_text(encoding="utf-8"))
        self.rows = data.get("proposals") if isinstance(data, dict) else data

    def test_it_catches_ten_of_the_twelve_dismissals(self):
        dismissed = {p["id"] for p in self.rows
                     if p.get("status") == "dismissed"}
        caught = {p["id"] for p in self.rows if agenda.premise_violations(p)}
        # Measured 2026-08-02: 12 dismissals, 10 of them carry one of the two
        # shapes. The two it misses are a duplicate filing and an item whose
        # estimate was short by orders of magnitude, neither of which is a
        # premise-reading failure. If a future docket drops below this the
        # rule has stopped covering what it was written for.
        self.assertGreaterEqual(len(dismissed & caught), 10,
                                "the premise rail no longer covers the "
                                "dismissals it was measured against")

    def test_it_does_not_fire_on_everything(self):
        """Charter 4 disqualifier 10: a rule that fires on everything cannot
        come out more than one way."""
        fired = sum(1 for p in self.rows if agenda.premise_violations(p))
        self.assertLess(fired, len(self.rows) // 4,
                        "the premise rail fires on over a quarter of the "
                        "docket and has stopped discriminating")

    def test_a_cited_file_that_exists_clears_the_stored_premise_shape(self):
        proposal = {"rationale": "Cd 0.0551, 0.0448, 0.0491 across the rungs",
                    "citations": ["demo-output/website/agenda/docket.json"]}
        self.assertEqual(agenda.premise_violations(proposal), [])
        proposal["citations"] = ["a ladder somebody remembers"]
        self.assertEqual(len(agenda.premise_violations(proposal)), 1)


if __name__ == "__main__":
    unittest.main()
