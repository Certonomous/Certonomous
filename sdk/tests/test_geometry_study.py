"""The geometry act after Katie's motorbike review (2026-07-24).

Everything here runs without OpenFOAM/WSL: pure rung-budget derivation, the
Eca & Hoekstra replay path against a study record on disk, the drag-area
grading against a published band, the coefficient-table emission, and a
register-style scan that keeps em dashes and arrows out of every narration
string this act can emit.
"""
from __future__ import annotations

import ast
import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from chief_engineer import lab, uq
from chief_engineer.lab import (ComputeLedger, Roster, SOLVER_BACKED,
                                UNCONVERGED, VALIDATED, grade_drag_area)
from chief_engineer.transcript import Transcript
from workflows import geometry_study as gs

SDK = Path(__file__).resolve().parents[1]

_BAND_REFERENCE = {
    "drag_area_band": [0.30, 0.70],
    "band_label": "published motorcycle-with-rider band",
    "source": "Cossalter, Motorcycle Dynamics (2006); "
              "Hoerner, Fluid-Dynamic Drag (1965)",
    "source_short": "Cossalter 2006; Hoerner 1965",
}


# --------------------------------------------------------------------------
# Rung budgets
# --------------------------------------------------------------------------

class RungBudgetTests(unittest.TestCase):
    def _knob(self, spec):
        return (spec["surface"], spec["block_scale"])

    def test_familiar_rungs_sit_below_the_production_levels(self):
        specs = gs.refinement_rungs(familiar=True)
        self.assertEqual(len(specs), 2)
        for spec in specs:
            # Production is surface level (5 6): every rung must be cheaper.
            self.assertLess(spec["surface"][1], 6)
        self.assertNotEqual(self._knob(specs[0]), self._knob(specs[1]))

    def test_unfamiliar_rungs_are_distinct_from_production_and_each_other(self):
        for refinement in (2, 3, 4, 5):
            specs = gs.refinement_rungs(familiar=False, refinement=refinement)
            production_knob = ((max(2, refinement), max(2, refinement) + 1), None)
            knobs = [self._knob(s) for s in specs]
            self.assertEqual(len(set(knobs)), 2, f"refinement {refinement}")
            for knob in knobs:
                self.assertNotEqual(knob, production_knob,
                                    f"refinement {refinement}: rung equals "
                                    f"the production mesh knob")

    def test_floor_collision_engages_the_background_scale(self):
        # The B-52 lesson: refinement 3 floors both rungs to surface level 2,
        # so the coarse rung must move a second, real knob.
        specs = gs.refinement_rungs(familiar=False, refinement=3)
        coarse = next(s for s in specs if s["tag"] == "coarse")
        self.assertIsNotNone(coarse["block_scale"])

    def test_rung_iterations_fraction_and_floor(self):
        self.assertEqual(gs.rung_iterations(300), 180)
        self.assertEqual(gs.rung_iterations(100), gs.RUNG_ITERATION_FLOOR)


# --------------------------------------------------------------------------
# The in-act ladder: replay, refusal, skip, graceful failure
# --------------------------------------------------------------------------

class _LadderHarness(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        patcher = mock.patch.object(uq, "STUDIES_DIR", Path(tmp.name))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.out = Path(tmp.name) / "out"
        self.out.mkdir()
        self.script = Transcript("test", echo=None)
        self.roster = Roster(None)
        self.ledger = ComputeLedger()
        self.events: list[tuple[str, dict]] = []

    def emit(self, event, payload):
        self.events.append((event, payload))

    def run_ladder(self, **overrides):
        kwargs = dict(engineer=None, label="testbody", familiar=True,
                      params={}, iterations=300, production_cells=353578,
                      production_cd=0.41558, study_fp="fp-match",
                      script=self.script, roster=self.roster,
                      ledger=self.ledger, emit=self.emit, out=self.out)
        kwargs.update(overrides)
        return gs._run_refinement_ladder(**kwargs)

    def entries_text(self):
        return " ".join(entry.message for entry in self.script.entries)


class LadderReplayTests(_LadderHarness):
    LEVELS = [
        {"tag": "coarse", "cells": 14714, "cd": 0.47067, "mission": "m-coarse"},
        {"tag": "mid", "cells": 66316, "cd": 0.42017, "mission": "m-mid"},
        {"tag": "fine", "cells": 353578, "cd": 0.41558, "mission": "m-fine"},
    ]

    def test_matching_study_replays_rungs_and_measures_the_band(self):
        uq.save_study("testbody", {"fingerprint": "fp-match",
                                   "levels": self.LEVELS,
                                   "model": {"band_abs": 0.0018,
                                             "method": "inter-closure spread "
                                                       "(screening estimate)"}})
        result = self.run_ladder()
        self.assertIsNotNone(result)
        self.assertTrue(result["replay"])
        self.assertIsNotNone(result["band_abs"])
        # Three rows through the same transcript.table event the airliner uses.
        tables = [p for e, p in self.events if e == "transcript.table"]
        self.assertTrue(tables)
        self.assertEqual(tables[0]["headers"], ["Mesh", "Cells", "C_d"])
        rows = [row for p in tables for row in p["rows"]]
        self.assertEqual(len(rows), 3)
        # Cheapest mesh first: the table reads down as a refinement sequence.
        self.assertEqual([row[0] for row in rows],
                         ["Coarse rung", "Middle rung", "Production mesh"])
        self.assertIn(["Production mesh", "353,578", "0.4156"], rows)
        self.assertTrue(any(p["append"] for p in tables[1:]))
        # The band bullet cites the procedure and the clamp guard fires on
        # this real ladder (observed order 4.8).
        text = self.entries_text()
        self.assertIn("Eca & Hoekstra 2014", text)
        self.assertIn("Observed order limited to the theoretical range", text)
        # The study record now carries the in-act numerical band and keeps
        # the model spread it already had.
        study = uq.load_study("testbody")
        self.assertAlmostEqual(study["numerical"]["band_abs"],
                               result["band_abs"])
        self.assertTrue(study["numerical"]["clamped"])
        self.assertIn("model", study)
        # And the certificate lookup finds it under the same fingerprint.
        lookup = uq.channels_for("testbody", "fp-match")
        self.assertFalse(lookup["pending"])
        self.assertIsNotNone(lookup["numerical"])

    def test_mismatched_fingerprint_does_not_replay_a_stale_ladder(self):
        uq.save_study("testbody", {"fingerprint": "fp-other",
                                   "levels": self.LEVELS})
        with mock.patch.object(gs, "refinement_rungs",
                               side_effect=RuntimeError("no solver here")):
            result = self.run_ladder()
        # The stale ladder is never replayed; the fresh path fails closed
        # with the honest line instead of quoting another setup's band.
        self.assertIsNone(result)
        self.assertIn("did not complete", self.entries_text())
        self.assertTrue(uq.channels_for("testbody", "fp-match")["pending"])


class LadderGuardTests(_LadderHarness):
    def test_degenerate_stored_ladder_never_replays(self):
        # The old B-52 record carries two IDENTICAL rungs (the refinement
        # floor bug). It must not replay as a study; the act attempts a fresh
        # ladder instead (which fails closed here, solverless).
        uq.save_study("testbody", {"fingerprint": "fp-match", "levels": [
            {"tag": "coarse", "cells": 66316, "cd": 0.4300},
            {"tag": "mid", "cells": 66316, "cd": 0.4302},
            {"tag": "fine", "cells": 353578, "cd": 0.41558},
        ]})
        from chief_engineer.head_engineer import HeadEngineer
        stub = mock.Mock()
        stub.remote_case = "~/certonomous-runs/nowhere"
        stub.monitor.on_anomaly = None
        with mock.patch.object(HeadEngineer, "clone_case_from",
                               return_value=False):
            result = self.run_ladder(engineer=stub)
        self.assertIsNone(result)
        self.assertIn("did not complete", self.entries_text())
        # No stored-degenerate rows were presented as a ladder, and the
        # fresh attempt put nothing on screen before it failed closed.
        rows = [row for e, p in self.events if e == "transcript.table"
                for row in p["rows"]]
        self.assertEqual(rows, [])

    def test_unanchored_stored_ladder_never_replays(self):
        # Three distinct stored rungs, but none of them IS this run's
        # production mesh (the mesh changed, e.g. a quality-gate fix): the
        # on-screen table must never show a production row that differs from
        # the mesh actually solved, so the act runs a fresh ladder instead.
        uq.save_study("testbody", {"fingerprint": "fp-match", "levels": [
            {"tag": "coarse", "cells": 14714, "cd": 0.4707},
            {"tag": "mid", "cells": 66316, "cd": 0.4202},
            {"tag": "fine", "cells": 353578, "cd": 0.41558},
        ]})
        from chief_engineer.head_engineer import HeadEngineer
        stub = mock.Mock()
        stub.remote_case = "~/certonomous-runs/nowhere"
        stub.monitor.on_anomaly = None
        with mock.patch.object(HeadEngineer, "clone_case_from",
                               return_value=False):
            result = self.run_ladder(engineer=stub, production_cells=353688)
        self.assertIsNone(result)
        self.assertIn("did not complete", self.entries_text())

    def test_env_kill_switch_skips_everything(self):
        with mock.patch.dict(os.environ, {gs.REFINEMENT_ENV: "0"}):
            result = self.run_ladder()
        self.assertIsNone(result)
        self.assertEqual(self.events, [])
        self.assertEqual(self.script.entries, [])

    def test_solverless_environment_degrades_gracefully(self):
        # No study record, no compute node: the fresh path must fail closed
        # with one honest line, never an exception out of the act.
        from chief_engineer.head_engineer import HeadEngineer

        stub = mock.Mock()
        stub.remote_case = "~/certonomous-runs/nowhere"
        stub.monitor.on_anomaly = None
        with mock.patch.object(HeadEngineer, "clone_case_from",
                               return_value=False):
            result = self.run_ladder(engineer=stub)
        self.assertIsNone(result)
        self.assertIn("did not complete", self.entries_text())


# --------------------------------------------------------------------------
# Drag-area grading against the published band
# --------------------------------------------------------------------------

class DragAreaGradingTests(unittest.TestCase):
    def test_motorbike_number_lands_inside_the_published_band(self):
        # The act's real numbers: Cd 0.4156 on the case's Aref 0.75 m².
        verdict = grade_drag_area(measured_cd=0.41558, reference_area_m2=0.75,
                                  reference=_BAND_REFERENCE)
        c = verdict["comparison"]
        self.assertEqual(verdict["tier"], SOLVER_BACKED)
        self.assertEqual(c["position"], "inside")
        self.assertAlmostEqual(c["drag_area_m2"], 0.3117, places=4)
        self.assertIn("inside the published motorcycle-with-rider band",
                      verdict["reason"])
        self.assertIn("Cossalter 2006", verdict["reason"])

    def test_band_comparison_never_grants_validated(self):
        verdict = grade_drag_area(measured_cd=0.6, reference_area_m2=0.75,
                                  reference=_BAND_REFERENCE)
        self.assertNotEqual(verdict["tier"], VALIDATED)

    def test_below_and_above_are_stated_not_hidden(self):
        low = grade_drag_area(measured_cd=0.2, reference_area_m2=0.75,
                              reference=_BAND_REFERENCE)
        high = grade_drag_area(measured_cd=1.2, reference_area_m2=0.75,
                               reference=_BAND_REFERENCE)
        self.assertEqual(low["comparison"]["position"], "below")
        self.assertIn("below", low["reason"])
        self.assertEqual(high["comparison"]["position"], "above")
        self.assertIn("above", high["reason"])

    def test_gates_still_cap_the_comparison(self):
        unconverged = grade_drag_area(measured_cd=0.4, reference_area_m2=0.75,
                                      reference=_BAND_REFERENCE,
                                      converged=False)
        self.assertEqual(unconverged["tier"], UNCONVERGED)
        gated = grade_drag_area(measured_cd=0.4, reference_area_m2=0.75,
                                reference=_BAND_REFERENCE,
                                in_validated_regime=False)
        self.assertEqual(gated["tier"], SOLVER_BACKED)
        self.assertIn("mesh quality", gated["reason"])

    def test_drag_area_is_area_convention_proof(self):
        # Same physical drag, two Aref conventions: identical drag area.
        a = grade_drag_area(measured_cd=0.4, reference_area_m2=0.75,
                            reference=_BAND_REFERENCE)
        b = grade_drag_area(measured_cd=0.2, reference_area_m2=1.5,
                            reference=_BAND_REFERENCE)
        self.assertEqual(a["comparison"]["drag_area_m2"],
                         b["comparison"]["drag_area_m2"])


# --------------------------------------------------------------------------
# Surface acceptance and the coefficient table
# --------------------------------------------------------------------------

class SurfaceAcceptanceTests(unittest.TestCase):
    def test_shells_are_expected_not_issues(self):
        line, shells = gs.surface_acceptance(
            {"closed": True, "issues": ["4 unconnected parts"]},
            "Motorcycle with rider, highway configuration")
        self.assertEqual(shells, 4)
        self.assertIn("4 separate closed shells", line)
        self.assertIn("mesh together as one flow body", line)
        self.assertNotIn("Issues:", line)
        self.assertNotIn("unconnected", line)

    def test_real_defects_still_reach_the_screen(self):
        line, shells = gs.surface_acceptance(
            {"closed": False, "issues": ["12 open edges",
                                         "3 unconnected parts"]}, "X")
        self.assertEqual(shells, 3)
        self.assertIn("12 open edges", line)

    def test_clean_surface_says_so(self):
        line, shells = gs.surface_acceptance({"closed": True, "issues": []}, "X")
        self.assertIsNone(shells)
        self.assertIn("No defects reported", line)


class CoefficientTableTests(unittest.TestCase):
    def test_emit_table_streams_and_mirrors(self):
        events = []
        script = Transcript("t", echo=None)
        gs._emit_table(lambda e, p: events.append((e, p)), script,
                       role="CHIEF ENGINEER",
                       title="Force coefficients over the settled window",
                       headers=("Coefficient", "Value", "Band (95%)", "Window"),
                       rows=[["C_d", "0.4164", "±0.0011", "final 60 iterations"],
                             ["C_L", "0.06432", "±0.00088", "final 60 iterations"]],
                       table_id="coefficients-motorBike")
        self.assertEqual(len(events), 1)
        event, payload = events[0]
        self.assertEqual(event, "transcript.table")
        self.assertEqual(payload["headers"],
                         ["Coefficient", "Value", "Band (95%)", "Window"])
        self.assertEqual(payload["rows"][0][0], "C_d")
        self.assertEqual(payload["rows"][1][0], "C_L")
        self.assertFalse(payload["append"])
        # Mirrored into the on-disk transcript, numbers intact.
        blob = " ".join(entry.message for entry in script.entries)
        self.assertIn("0.4164", blob)
        self.assertIn("0.06432", blob)

    def test_act_source_replaced_the_settling_sentence_with_the_table(self):
        source = (SDK / "workflows" / "geometry_study.py").read_text(
            encoding="utf-8")
        self.assertNotIn("Drag settles at", source)
        self.assertIn("Force coefficients over the settled window", source)
        self.assertIn('"C_d"', source)
        self.assertIn('"C_L"', source)


# --------------------------------------------------------------------------
# Scale basis: published dimensions for named bodies
# --------------------------------------------------------------------------

class ScaleBasisTests(unittest.TestCase):
    def test_b52_uses_its_published_length_with_the_source_stated(self):
        reference, lines = gs.scale_basis("b52.stl", 358.0, {})
        self.assertEqual(reference, 48.5)
        blob = " ".join(lines)
        self.assertIn("358 units long", blob)
        self.assertIn("Published length of this aircraft: 48.5 m; "
                      "working to that", blob)

    def test_stated_reference_length_still_wins(self):
        reference, lines = gs.scale_basis("b52.stl", 358.0,
                                          {"reference_length": 47.0})
        self.assertEqual(reference, 47.0)
        self.assertIn("you stated", " ".join(lines))

    def test_unnamed_upload_keeps_the_generic_50_m_fallback(self):
        reference, lines = gs.scale_basis("mystery_body.stl", 358.0, {})
        self.assertEqual(reference, 50.0)
        self.assertIn("not a plausible size", " ".join(lines))

    def test_plausible_units_are_taken_as_metres(self):
        reference, lines = gs.scale_basis("mystery_body.stl", 12.0, {})
        self.assertEqual(reference, 12.0)
        self.assertIn("dimensionally plausible", " ".join(lines))

    def test_every_basis_bullet_starts_with_a_capital(self):
        for surface, raw, params in (("b52.stl", 358.0, {}),
                                     ("x.stl", 358.0, {}),
                                     ("x.stl", 12.0, {}),
                                     ("x.stl", 12.0, {"reference_length": 3})):
            for line in gs.scale_basis(surface, raw, params)[1]:
                self.assertTrue(line[0].isupper(), line)


# --------------------------------------------------------------------------
# Channel notes (uncertainty doctrine)
# --------------------------------------------------------------------------

class ChannelNoteTests(unittest.TestCase):
    LOOKUP = {"numerical": {"band_abs": 0.0019, "observed_order": 4.824,
                            "clamped": True, "method": "3-mesh study"},
              "model": None, "pending": False,
              "provenance": ["motorBike-rung-coarse"],
              "levels": [{"tag": "coarse", "cells": 14714, "cd": 0.4707},
                         {"tag": "medium", "cells": 66316, "cd": 0.4202},
                         {"tag": "production", "cells": 353578, "cd": 0.4156}]}

    def _channels(self, lookup):
        return gs.certificate_channels(
            settle_2sigma=0.001, window=60, velocity=20.0, lookup=lookup,
            cells=353578, non_ortho_s="65.0°", skew_s="8.94")

    def test_input_channel_is_the_exact_assumption_sentence(self):
        inp = self._channels(self.LOOKUP)["channels"][0]
        self.assertEqual(inp["note"],
                         "No input uncertainty was assumed for this problem.")
        self.assertEqual(gs.INPUT_ASSUMED_NOTE, inp["note"])

    def test_numerical_channel_is_three_clean_bullets(self):
        num = self._channels(self.LOOKUP)["channels"][1]
        self.assertEqual(num["note"].count("•"), 3)
        self.assertIn("14,714, 66,316, 353,578 cells", num["note"])
        self.assertIn("Observed order 4.82", num["note"])
        self.assertIn("limited to the theoretical range", num["note"])
        self.assertIn("±0.0019", num["note"])
        # Generic register (owner rule, 2026-07-24): the certificate never
        # states a method by name; transcript citations stay in the
        # transcript, never in a channel note.
        self.assertIn("default numerical consistency method", num["note"])
        for banned in ("checkMesh", "uq-", "GCI", "rung-coarse", "Eca",
                       "Hoekstra", "least-squares"):
            self.assertNotIn(banned, num["note"])
        # Every bullet opens with a capital letter.
        for part in num["note"].split("•"):
            part = part.strip()
            if part:
                self.assertTrue(part[0].isupper(), part)

    def test_model_channel_transfers_from_validation_history_when_no_study(self):
        # Doctrine fallback: a body with no closure study of its own still
        # quantifies the model channel, from the lab's measured history.
        transfer = {"band_abs": 0.0133, "band_rel": 0.282,
                    "method": uq.TRANSFER_METHOD,
                    "members": {"motorBike": 0.00426,
                                "naca4412_wing": 0.28206},
                    "screening_estimate": True, "transferred": True}
        channels = gs.certificate_channels(
            settle_2sigma=0.001, window=60, velocity=100.0,
            lookup={"numerical": None, "model": None, "pending": True,
                    "provenance": [], "levels": []},
            cells=193880, non_ortho_s="65.0°", skew_s="3.20",
            transfer=transfer)
        mod = channels["channels"][2]
        self.assertTrue(mod["quantified"])
        self.assertEqual(mod["value"], 0.0133)
        self.assertIn("estimated from the lab's validation history",
                      mod["note"])
        self.assertIn("screening estimate", mod["note"])
        for banned in ("GP", "Gaussian", "regression", "uq-"):
            self.assertNotIn(banned, mod["note"])

    def test_direct_study_still_wins_over_the_transfer(self):
        lookup = dict(self.LOOKUP)
        lookup["model"] = {"band_abs": 0.0018,
                           "method": "inter-closure spread "
                                     "(screening estimate)"}
        channels = gs.certificate_channels(
            settle_2sigma=0.001, window=60, velocity=20.0, lookup=lookup,
            cells=353578, non_ortho_s="65.0°", skew_s="3.20",
            transfer={"band_abs": 9.9, "method": uq.TRANSFER_METHOD})
        mod = channels["channels"][2]
        self.assertEqual(mod["value"], 0.0018)
        self.assertIn("inter-closure spread", mod["note"])

    def test_no_channel_note_carries_mesh_gate_figures(self):
        blob = " ".join(c["note"] for c in self._channels(self.LOOKUP)["channels"])
        self.assertNotIn("65.0", blob)
        self.assertNotIn("8.94", blob)

    def test_pending_note_quotes_no_foreign_band(self):
        num = self._channels({"numerical": None, "model": None,
                              "pending": True, "provenance": [],
                              "levels": []})["channels"][1]
        self.assertIsNone(num["value"])
        self.assertIn("study pending", num["note"])
        self.assertIn("No band is quoted", num["note"])


class ChannelsForLevels(unittest.TestCase):
    def test_matching_study_exposes_its_levels(self):
        import tempfile
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        with mock.patch.object(uq, "STUDIES_DIR", Path(tmp.name)):
            uq.save_study("x", {"fingerprint": "fp",
                                "numerical": {"band_abs": 1.0, "method": "m"},
                                "levels": [{"tag": "coarse", "cells": 10,
                                            "cd": 1.0}]})
            hit = uq.channels_for("x", "fp")
            miss = uq.channels_for("x", "other")
        self.assertEqual(len(hit["levels"]), 1)
        self.assertEqual(miss["levels"], [])


# --------------------------------------------------------------------------
# Mesh caveats: regression per body path (the meshes were fixed 2026-07-24)
# --------------------------------------------------------------------------

class MeshCaveatRegressionTests(unittest.TestCase):
    """The mesh-channel caveat lines cannot fire when the mesh check passes.

    One representative passing stat set per body path the act carries:
    motorbike (familiar tutorial), B-52 and NACA 4412 (curriculum uploads),
    and a generic unnamed upload."""

    PASSING = {
        "motorBike": (65.0, 3.99),        # measured after the skewness fix
        "b52": (65.2, 3.20),
        "naca4412_wing": (60.1, 2.85),
        "uploaded_body": (69.9, 4.0),     # exactly on both gates still passes
    }

    def test_no_caveat_when_the_mesh_check_passes(self):
        for body, (non_ortho, skew) in self.PASSING.items():
            self.assertTrue(gs.mesh_gates_pass(non_ortho, skew), body)
            self.assertEqual(gs.mesh_caveat_lines(non_ortho, skew), [], body)

    def test_certificate_mesh_block_carries_no_caveat_on_a_passing_mesh(self):
        from chief_engineer.certificate import _mesh_rows
        for body, (non_ortho, skew) in self.PASSING.items():
            rows = _mesh_rows(gs.mesh_validity(193880, non_ortho, skew))
            for name, measured, verdict, ok in rows:
                self.assertTrue(ok, f"{body}: {name} {measured}")
                self.assertNotEqual(verdict, "caveat", f"{body}: {name}")

    def test_caveats_fire_only_above_the_gates(self):
        both = gs.mesh_caveat_lines(75.0, 8.94)
        self.assertEqual(len(both), 2)
        self.assertIn("non-orthogonality 75.0°", both[0])
        self.assertIn("skewness 8.94", both[1])
        self.assertEqual(len(gs.mesh_caveat_lines(65.0, 8.94)), 1)
        self.assertEqual(gs.mesh_caveat_lines(None, None), [])


# --------------------------------------------------------------------------
# The keep-trying rule: gates fail -> tighten and remesh, up to twice
# --------------------------------------------------------------------------

class KeepTryingRuleTests(unittest.TestCase):
    GOOD = {"cells": 353688, "max_non_orthogonality": 65.0,
            "max_skewness": 3.99}
    BAD = {"cells": 353688, "max_non_orthogonality": 65.0,
           "max_skewness": 8.94}

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        patcher = mock.patch.dict(os.environ,
                                  {"CERTONOMOUS_LESSONS_DIR": tmp.name})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.narrated: list[str] = []
        self.remeshes: list[int] = []

    def _engineer(self, stats_after):
        engineer = mock.Mock()
        engineer.collect_mesh_stats.side_effect = list(stats_after)
        return engineer

    def test_failing_gates_trigger_one_honest_retry_that_passes(self):
        engineer = self._engineer([self.GOOD])
        stats, retries, passed = gs.retry_mesh_quality(
            engineer, dict(self.BAD), narrate=self.narrated.append,
            remesh=self.remeshes.append)
        self.assertEqual(retries, 1)
        self.assertTrue(passed)
        self.assertEqual(stats["max_skewness"], 3.99)
        self.assertEqual(self.remeshes, [1])
        # The narration says the mesh is being made again; the control it
        # tightens is a mesh-construction setting and stays off camera.
        self.assertEqual(self.narrated[0],
                         "• Mesh quality below standard; meshing again.")
        self.assertNotIn("skewness limit", " ".join(self.narrated))
        engineer.enforce_boundary_skewness.assert_called_once_with(4.0)
        # The retry is a lesson the team reads back.
        from chief_engineer.lessons import learned_lessons
        lessons = {item["mission_id"] for item in learned_lessons()}
        self.assertIn("mesh-quality-keep-trying", lessons)

    def test_passing_gates_never_retry_and_record_no_lesson(self):
        engineer = self._engineer([])
        stats, retries, passed = gs.retry_mesh_quality(
            engineer, dict(self.GOOD), narrate=self.narrated.append,
            remesh=self.remeshes.append)
        self.assertEqual(retries, 0)
        self.assertTrue(passed)
        self.assertEqual(self.narrated, [])
        engineer.enforce_boundary_skewness.assert_not_called()
        from chief_engineer.lessons import learned_lessons
        self.assertEqual(learned_lessons(), [])

    def test_two_failed_retries_proceed_with_the_caveat_on_the_record(self):
        engineer = self._engineer([dict(self.BAD), dict(self.BAD)])
        stats, retries, passed = gs.retry_mesh_quality(
            engineer, dict(self.BAD), narrate=self.narrated.append,
            remesh=self.remeshes.append)
        self.assertEqual(retries, gs.MESH_RETRY_LIMIT)
        self.assertFalse(passed)
        self.assertEqual(self.remeshes, [1, 2])
        # Each retry tightens further: 4.0 first, then 3.5.
        calls = [c.args[0] for c in
                 engineer.enforce_boundary_skewness.call_args_list]
        self.assertEqual(calls, [4.0, 3.5])
        # The caveat machinery still fires afterwards, as measured.
        self.assertEqual(len(gs.mesh_caveat_lines(
            stats["max_non_orthogonality"], stats["max_skewness"])), 1)


# --------------------------------------------------------------------------
# Mesh-quality gate (the skewness fix, measured 2026-07-24)
# --------------------------------------------------------------------------

class SkewnessGateTests(unittest.TestCase):
    def test_familiar_path_enforces_the_boundary_skewness_gate(self):
        source = (SDK / "workflows" / "geometry_study.py").read_text(
            encoding="utf-8")
        self.assertIn("engineer.enforce_boundary_skewness(MAX_SKEWNESS)", source)

    def test_generated_cases_bake_the_gate_into_the_quality_dict(self):
        from chief_engineer.external_aero import _MESH_QUALITY
        self.assertIn("maxBoundarySkewness 4;", _MESH_QUALITY)
        self.assertNotIn("maxBoundarySkewness 20;", _MESH_QUALITY)

    def test_enforce_boundary_skewness_appends_and_verifies(self):
        from chief_engineer.head_engineer import HeadEngineer
        eng = HeadEngineer.__new__(HeadEngineer)
        eng.remote_case = "~/certonomous-runs/case"
        calls = []

        def fake_wsl(cmd, timeout=600.0):
            calls.append(cmd)
            return mock.Mock(stdout="GATED\n")
        eng._wsl = fake_wsl
        self.assertTrue(eng.enforce_boundary_skewness(4.0))
        self.assertIn("maxBoundarySkewness 4;", calls[0])
        eng._wsl = lambda cmd, timeout=600.0: mock.Mock(stdout="")
        self.assertFalse(eng.enforce_boundary_skewness(4.0))


# --------------------------------------------------------------------------
# Display-mesh orphan islands (the B-52 blob)
# --------------------------------------------------------------------------

def _components(verts, faces):
    """Python mirror of the GUI's position-quantized component finder."""
    span = max(max(v[i] for v in verts) - min(v[i] for v in verts)
               for i in range(3)) or 1.0
    q = span * 1e-5
    key, vid = {}, []
    for v in verts:
        k = (round(v[0] / q), round(v[1] / q), round(v[2] / q))
        vid.append(key.setdefault(k, len(key)))
    parent = list(range(len(key)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for f in faces:
        parent[find(vid[f[0]])] = find(vid[f[1]])
        parent[find(vid[f[1]])] = find(vid[f[2]])
    sizes = {}
    for f in faces:
        r = find(vid[f[0]])
        sizes[r] = sizes.get(r, 0) + 1
    return sorted(sizes.values(), reverse=True)


class OrphanIslandTests(unittest.TestCase):
    def test_b52_display_mesh_carries_exactly_one_tiny_island(self):
        # The measured fact behind the GUI filter: the B-52 viewport payload
        # is one dominant component plus one detached island under 1%.
        from chief_engineer.geometry import load_surface
        payload = load_surface(SDK / "geometry" / "b52.stl")
        comps = _components(payload["vertices"], payload["faces"])
        total = len(payload["faces"])
        self.assertGreater(comps[0] / total, 0.99)
        for tiny in comps[1:]:
            self.assertLess(tiny / total, 0.01)

    def test_gui_filter_exists_and_is_display_only(self):
        html = (SDK / "chief_engineer" / "control_room.html").read_text(
            encoding="utf-8")
        self.assertIn("function dropOrphanIslands", html)
        self.assertIn("dropOrphanIslands({ verts:", html)
        # The filter must never appear server-side where solves read geometry.
        for solver_file in ("head_engineer.py", "external_aero.py"):
            self.assertNotIn("dropOrphanIslands",
                             (SDK / "chief_engineer" / solver_file).read_text(
                                 encoding="utf-8"))


class GuiRenderingPins(unittest.TestCase):
    def test_bullets_render_as_lines_with_capitals(self):
        html = (SDK / "chief_engineer" / "control_room.html").read_text(
            encoding="utf-8")
        self.assertIn("function bulletHTML", html)
        self.assertIn("const capBullet", html)
        self.assertIn(".bline { display: block; }", html)

    def test_viewport_label_lost_its_dashed_tail(self):
        html = (SDK / "chief_engineer" / "control_room.html").read_text(
            encoding="utf-8")
        self.assertNotIn("' — solved field'", html)

    def test_report_embeds_clickable_plots(self):
        html = (SDK / "chief_engineer" / "control_room.html").read_text(
            encoding="utf-8")
        self.assertIn('target="_blank" rel="noopener"><img', html)
        self.assertIn("if (state.report) renderMemo(state.report);", html)
        # The memo figure strip unions the report's own manifest with the
        # streamed plots, so no act depends on paced-queue timing.
        self.assertIn("rep.plots || []", html)

    def test_geometry_report_carries_its_plot_manifest(self):
        source = (SDK / "workflows" / "geometry_study.py").read_text(
            encoding="utf-8")
        self.assertIn('report_doc["plots"] = report_plots', source)
        self.assertIn('"url": f"/api/plot/geometry-study/{target.name}"', source)

    def test_nothing_says_live_anymore(self):
        html = (SDK / "chief_engineer" / "control_room.html").read_text(
            encoding="utf-8")
        self.assertNotIn("Objective trace, live", html)
        self.assertNotIn("+ ', live'", html)

    def test_no_coefficient_plot_says_rolling_mean(self):
        source = (SDK / "chief_engineer" / "head_engineer.py").read_text(
            encoding="utf-8")
        self.assertNotIn('label=f"rolling mean', source)
        self.assertNotIn('"rolling mean', source)

    def test_race_verdict_renders_core_minutes_only(self):
        # The race card's verdict quotes the act's own headline unit
        # ("Measured speedup Xx in core-minutes."); the wall figure stays in
        # the payload as measured data but is never rendered on the card.
        html = (SDK / "chief_engineer" / "control_room.html").read_text(
            encoding="utf-8")
        self.assertIn("Measured speedup <b>${esc(p.speedup_core_min)}"
                      "×</b> in core-minutes.", html)
        self.assertNotIn("p.speedup_wall", html)


# --------------------------------------------------------------------------
# Result card (owner review, 2026-07-25)
# --------------------------------------------------------------------------

class ResultCardPins(unittest.TestCase):
    """The result card: content vertically centered inside an unchanged box,
    and no settle-share clause one line under the headline band. The share
    ("envelope N% of value") measures how flat the settled history is; it is
    a different number from the headline's combined 95% band, and the two
    side by side misread as a contradiction. The clause is dropped on the
    card only; reports, transcripts and certificates keep the full reason."""

    _HTML = SDK / "chief_engineer" / "control_room.html"
    # Python mirror of the exact strip renderResult applies to the verdict
    # reason; the literal pin below keeps the two from drifting apart.
    _STRIP = r";\s*envelope\s+[\d.]+%\s+of\s+value\s*$"

    def test_card_content_is_vertically_centered(self):
        html = self._HTML.read_text(encoding="utf-8")
        rule = re.search(r"\.result-card \{([^}]*)\}", html).group(1)
        self.assertIn("flex-direction: column", rule)
        self.assertIn("justify-content: center", rule)
        # Outer box untouched: same margin, padding and border as before.
        self.assertIn("margin: 0 18px 10px; padding: 10px 14px;", rule)
        # The headline row keeps its old inline layout inside the column.
        self.assertIn(".result-card .r-head { display: flex; "
                      "align-items: baseline; gap: 10px; flex-wrap: wrap; }",
                      html)
        self.assertIn('<div class="r-head">', html)

    def test_card_drops_the_envelope_share_clause(self):
        html = self._HTML.read_text(encoding="utf-8")
        # The JS literal and the Python mirror must stay identical.
        self.assertIn(
            r".replace(/;\s*envelope\s+[\d.]+%\s+of\s+value\s*$/, '')", html)
        from chief_engineer.lab import trust
        # The exact reason the B-52 card carried: settle scatter near zero
        # under a 0.0472 ± 0.019 headline.
        reason = trust(relative_error=1e-6)["reason"]
        self.assertIn("envelope 0.0% of value", reason)
        self.assertEqual(re.sub(self._STRIP, "", reason),
                         "a selected-solver result")
        # Any share value strips, not just the 0.0% case.
        wider = trust(relative_error=0.402)["reason"]
        self.assertIn("envelope 40.2% of value", wider)
        self.assertEqual(re.sub(self._STRIP, "", wider),
                         "a selected-solver result")

    def test_reasons_without_the_share_clause_pass_through(self):
        from chief_engineer.lab import trust
        for reason in (
                trust(relative_error=None)["reason"],
                trust(converged=False)["reason"],
                trust(in_validated_regime=False)["reason"],
                "every evaluation on both lanes ran the selected solver; "
                "the paths agree to 98%"):
            self.assertEqual(re.sub(self._STRIP, "", reason), reason)


# --------------------------------------------------------------------------
# Pacing
# --------------------------------------------------------------------------

class PacingTests(unittest.TestCase):
    def test_warm_replay_default_dropped_to_14_seconds(self):
        self.assertEqual(gs.SOLVE_REPLAY_DEFAULT_S, 14.0)
        # The env override stays wired to the constant.
        source = (SDK / "workflows" / "geometry_study.py").read_text(
            encoding="utf-8")
        self.assertIn("CERTONOMOUS_SOLVE_REPLAY_S", source)
        self.assertIn("SOLVE_REPLAY_DEFAULT_S", source)

    def test_cold_run_streams_up_to_two_points_per_second(self):
        self.assertEqual(gs.LIVE_CD_MIN_INTERVAL_S, 0.5)


# --------------------------------------------------------------------------
# Register: no em dash, no arrow, no banned vocabulary in this act's strings
# --------------------------------------------------------------------------

_ACT_FILES = (
    SDK / "workflows" / "geometry_study.py",
    SDK / "chief_engineer" / "researcher.py",
    SDK / "chief_engineer" / "display_names.py",
    SDK / "chief_engineer" / "head_engineer.py",
    SDK / "chief_engineer" / "lab.py",
    SDK / "chief_engineer" / "uq.py",
)


def _docstring_node_ids(tree):
    ids = set()
    candidates = [tree] + [
        node for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef))]
    for node in candidates:
        body = getattr(node, "body", None)
        if (body and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)):
            ids.add(id(body[0].value))
    return ids


def _string_literals(path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    doc_ids = _docstring_node_ids(tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) not in doc_ids:
                yield node.lineno, node.value


class ActRegisterTests(unittest.TestCase):
    def test_no_em_dash_or_arrow_in_any_act_string(self):
        offenders = []
        for path in _ACT_FILES:
            for lineno, value in _string_literals(path):
                for glyph in ("—", "→"):
                    if glyph in value:
                        offenders.append(f"{path.name}:{lineno}: {value!r}")
        self.assertEqual(offenders, [], "em dash / arrow reached a narration "
                                        "string:\n" + "\n".join(offenders))

    def test_no_banned_vocabulary_in_the_act_narration(self):
        banned = re.compile(
            r"\b(demo|stored|saved|cached|recorded|pre-computed|real solves?)\b",
            re.IGNORECASE)
        offenders = []
        path = SDK / "workflows" / "geometry_study.py"
        for lineno, value in _string_literals(path):
            hit = banned.search(value)
            if hit:
                offenders.append(f"{path.name}:{lineno}: {hit.group(0)!r} "
                                 f"in {value!r}")
        self.assertEqual(offenders, [], "banned vocabulary in narration:\n"
                         + "\n".join(offenders))

    def test_the_cut_fragments_never_come_back(self):
        source = (SDK / "workflows" / "geometry_study.py").read_text(
            encoding="utf-8")
        memo = (SDK / "chief_engineer" / "researcher.py").read_text(
            encoding="utf-8")
        for fragment in ("a measurement, not an optimisation",
                         "a measurement, not a sweep",
                         "low over the upper wing",
                         "Magnitude not independently validated",
                         "self-consistency is not validation",
                         "one mesh cannot give it",
                         "Still unknown: mesh sensitivity",
                         "would roughly double"):
            self.assertNotIn(fragment, source, fragment)
            self.assertNotIn(fragment, memo, fragment)


class ReplayLevelsTests(unittest.TestCase):
    """A stored refinement study written by the standalone uq scripts carries
    refinement indices and no tags. The replay path must render it rather than
    take the act down, with every cell count and Cd untouched.

    The NACA 4412 fixture below is the ladder as it stands on record: three
    DISTINCT rungs, falling monotonically. It used to be written here with a
    duplicated 67,826-cell rung, which made the lab's own reference ladder read
    as a degenerate two-mesh record; that expectation was wrong and is gone.
    Duplicate-rung handling is still covered, on numbers that are not this
    body's, in test_duplicate_cell_counts_collapse.
    """

    _UQ_SCRIPT_LEVELS = [
        {"cells": 67826, "cd": 0.02892, "mission": "uq-x-r1", "refinement": 1},
        {"cells": 137569, "cd": 0.02167, "mission": "uq-x-r3", "refinement": 3},
        {"cells": 337334, "cd": 0.01892, "mission": "uq-x-r4", "refinement": 4},
    ]

    def test_uq_script_levels_without_tags_are_renderable(self):
        from workflows.geometry_study import _ladder_rows, _replay_levels
        levels = _replay_levels(self._UQ_SCRIPT_LEVELS,
                                production_cells=337334)
        self.assertEqual([lv["cells"] for lv in levels],
                         [67826, 137569, 337334])
        self.assertEqual([lv["tag"] for lv in levels],
                         ["coarse", "medium", "production"])
        self.assertEqual([lv["cd"] for lv in levels],
                         [0.02892, 0.02167, 0.01892])
        rows = _ladder_rows(levels)
        self.assertEqual([row[0] for row in rows],
                         ["Coarse rung", "Middle rung", "Production mesh"])
        self.assertEqual(rows[-1][1], "337,334")

    def test_duplicate_cell_counts_collapse(self):
        from workflows.geometry_study import _replay_levels
        stored = [{"cells": 5000, "cd": 0.5, "refinement": 1},
                  {"cells": 5000, "cd": 0.5, "refinement": 2},
                  {"cells": 20000, "cd": 0.45, "refinement": 3},
                  {"cells": 80000, "cd": 0.43, "refinement": 4}]
        levels = _replay_levels(stored, production_cells=80000)
        self.assertEqual([lv["cells"] for lv in levels], [5000, 20000, 80000])

    def test_in_act_levels_keep_their_own_tags(self):
        from workflows.geometry_study import _replay_levels
        stored = [{"cells": 100, "cd": 0.1, "tag": "production"},
                  {"cells": 50, "cd": 0.11, "tag": "medium"},
                  {"cells": 20, "cd": 0.12, "tag": "coarse"}]
        levels = _replay_levels(stored, production_cells=100)
        self.assertEqual([lv["tag"] for lv in levels],
                         ["coarse", "medium", "production"])


class GridEvidenceGovernsTheChip(unittest.TestCase):
    """The mission's own refinement study decides whether the chip may say
    VALIDATED, and it decides on THIS run's ladder.

    The act used to hand ``converged=True`` to the grader and stop there, so a
    case whose study recorded conclusive false, a band of 16.3 percent of the
    value, and an observed order clamped down from 4.6 still read VALIDATED on
    agreement alone. The grid outcome now reaches the grader, and because the
    ladder runs after the first pass at the verdict, a fresh ladder that
    disagrees with the stored flag re-grades the verdict before it is emitted.
    """

    def test_the_grader_is_told_the_grid_outcome(self):
        source = (SDK / "workflows" / "geometry_study.py").read_text(
            encoding="utf-8")
        self.assertIn("grid_conclusive=grid_conclusive", source)
        # And the ladder's own result governs afterwards, not only a stored one.
        self.assertIn('refine.get("conclusive") is not None', source)
        self.assertIn('refine["conclusive"] != grid_conclusive', source)

    def test_a_measured_inconclusive_ladder_refuses_the_chip(self):
        # The ladder as measured on this lab's NACA 4412 case.
        band = uq.eca_hoekstra_band([67826, 137569, 337334],
                                    [0.02892, 0.02167, 0.01892])
        self.assertFalse(band["conclusive"])
        reference = {"cd": 0.030, "tolerance": 0.35, "confidence": "medium",
                     "source": "a published measurement"}
        chip = lab.validate_against_reference(
            measured_cd=0.02892, reference=reference,
            converged=True, grid_conclusive=band["conclusive"])
        self.assertEqual(chip["tier"], lab.SOLVER_BACKED)
        # The same agreement with a settled ladder behind it still validates,
        # so the gate is the grid evidence, not a blanket refusal.
        clean = uq.eca_hoekstra_band([1000, 8000, 64000],
                                     [1.04, 1.01, 1.0025])
        self.assertTrue(clean["conclusive"])
        self.assertEqual(
            lab.validate_against_reference(
                measured_cd=0.02892, reference=reference,
                converged=True,
                grid_conclusive=clean["conclusive"])["tier"],
            lab.VALIDATED)


class FreestreamBasisTests(unittest.TestCase):
    """A Reynolds number stated in the prompt reaches the solve: it converts
    to the freestream speed through the working reference length and the
    case's air viscosity, with the derivation narrated. An explicit velocity
    always wins; neither stated leaves the generic default."""

    def test_explicit_velocity_wins_over_a_stated_reynolds(self):
        from workflows.geometry_study import freestream_basis
        velocity, line = freestream_basis({"velocity": 30.0,
                                           "reynolds": 6e6}, 1.2)
        self.assertEqual(velocity, 30.0)
        self.assertEqual(line, "")

    def test_stated_reynolds_sets_the_speed_through_the_chord(self):
        from workflows.geometry_study import (AIR_KINEMATIC_VISCOSITY,
                                              freestream_basis)
        velocity, line = freestream_basis({"reynolds": 6e6}, 1.2)
        self.assertAlmostEqual(velocity,
                               6e6 * AIR_KINEMATIC_VISCOSITY / 1.2)
        self.assertAlmostEqual(velocity, 75.0)
        self.assertIn("You stated Reynolds 6e+06", line)
        self.assertIn("1.2 m", line)
        self.assertIn("75.0 m/s", line)

    def test_neither_stated_keeps_the_generic_default(self):
        from workflows.geometry_study import freestream_basis
        velocity, line = freestream_basis({}, 5.0)
        self.assertEqual(velocity, 100.0)
        self.assertEqual(line, "")

    def test_stated_chord_reaches_the_scale_basis(self):
        # The router's reference_length param (stated as "chord 1.2 m") wins
        # the scale basis, so the solved body is scaled to the stated chord.
        from workflows.geometry_study import scale_basis
        reference, lines = scale_basis("naca0015_sail.stl", 5.0,
                                       {"reference_length": 1.2})
        self.assertEqual(reference, 1.2)
        self.assertTrue(any("you stated a reference length of 1.2 m" in line
                            for line in lines), lines)


if __name__ == "__main__":
    unittest.main()
