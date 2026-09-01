"""A run must say what it cannot do, and must never close out as though it did.

The failure these pin happened on camera: a prompt asking for a blown slot
routed to the plain single-body study, the study solved the unblown baseline,
and the screen said the mission was complete at high confidence over a request
most of which was never run.

Two halves are pinned, and the second matters as much as the first: a matched
prompt must NOT acquire a scope-down it does not deserve.
"""

import re
import unittest
from pathlib import Path

from chief_engineer import scope
from chief_engineer.router import (AIRCRAFT_OPTIMIZATION,
                                   CYLINDER_VORTEX_SHEDDING, GEOMETRY_STUDY,
                                   SHAPE_OPTIMIZATION, apply_surface, classify)

_BLOWING_PROMPT = ("Run a blowing sweep on this airfoil: vary the jet slot "
                   "momentum coefficient and give me lift against C-mu.")
_PLAIN_PROMPT = "Give me a trustworthy drag coefficient for this wing."

CONTROL_ROOM = Path(__file__).resolve().parents[1] / "chief_engineer" / "control_room.html"


class TheMismatchIsDetected(unittest.TestCase):
    def test_a_blowing_sweep_on_the_generic_study_is_unmet(self):
        unmet = scope.unmet_asks(_BLOWING_PROMPT, GEOMETRY_STUDY)
        self.assertEqual([ask.tag for ask in unmet], [scope.BLOWING])

    def test_a_thermal_ask_on_the_generic_study_is_unmet(self):
        unmet = scope.unmet_asks(
            "Solve the temperature field and give me the heat flux.",
            GEOMETRY_STUDY)
        self.assertEqual([ask.tag for ask in unmet], [scope.THERMAL])

    def test_the_blowing_prompt_really_does_route_to_the_generic_study(self):
        """The mismatch is only reachable if dispatch sends this prompt to the
        study that cannot serve it. This is the ON-CAMERA path: a surface is
        uploaded with the prompt, and an uploaded surface takes anything that
        is not already an optimisation through the plain single-body study --
        which is how "Airfoil blown slot" became an unblown 3D baseline.

        If routing ever improves, this fails loudly rather than leaving the
        scope-down above testing nothing.
        """
        for prompt in (_BLOWING_PROMPT, "Airfoil blown slot"):
            route = apply_surface(classify(prompt), "airfoil.stl")
            self.assertEqual(route.intent, GEOMETRY_STUDY, prompt)
            self.assertTrue(scope.unmet_asks(prompt, route.intent), prompt)

    def test_several_unmet_asks_are_all_reported(self):
        unmet = scope.unmet_asks(
            "Blown slot, and I want the transient temperature history.",
            GEOMETRY_STUDY)
        self.assertEqual({ask.tag for ask in unmet},
                         {scope.BLOWING, scope.THERMAL, scope.UNSTEADY})


class TheMatchedPromptDoesNotRegress(unittest.TestCase):
    def test_a_plain_drag_prompt_raises_nothing(self):
        self.assertEqual(scope.unmet_asks(_PLAIN_PROMPT, GEOMETRY_STUDY), ())

    def test_a_design_search_on_an_optimiser_raises_nothing(self):
        for intent in (SHAPE_OPTIMIZATION, AIRCRAFT_OPTIMIZATION):
            self.assertEqual(
                scope.unmet_asks("Optimise the shape for maximum L/D", intent),
                (), intent)

    def test_an_unsteady_ask_on_the_unsteady_case_raises_nothing(self):
        self.assertEqual(
            scope.unmet_asks("Give me the vortex shedding frequency",
                             CYLINDER_VORTEX_SHEDDING), ())

    def test_an_undeclared_run_never_manufactures_a_mismatch(self):
        """An unknown capability set is an unknown, not an incapacity."""
        self.assertNotIn("not-a-real-intent", scope.CAPABILITIES)
        self.assertEqual(
            scope.unmet_asks(_BLOWING_PROMPT, "not-a-real-intent"), ())

    def test_an_empty_prompt_raises_nothing(self):
        self.assertEqual(scope.unmet_asks("", GEOMETRY_STUDY), ())
        self.assertEqual(scope.unmet_asks(None, GEOMETRY_STUDY), ())


class TheWordingIsSaidAndIsPlain(unittest.TestCase):
    def setUp(self):
        self.unmet = scope.unmet_asks(_BLOWING_PROMPT, GEOMETRY_STUDY)

    def test_the_commit_line_names_the_gap_and_the_run_that_closes_it(self):
        line = scope.commit_line(self.unmet)
        self.assertIn("blowing sweep", line)
        self.assertIn("unblown baseline only", line)
        self.assertIn("blown-slot case", line)

    def test_the_conclusion_line_says_what_was_not_run(self):
        line = scope.conclusion_line(self.unmet)
        self.assertIn("Not run", line)
        self.assertIn("blowing sweep", line)
        self.assertIn("that part alone", line)

    def test_a_matched_prompt_produces_no_lines_at_all(self):
        none = scope.unmet_asks(_PLAIN_PROMPT, GEOMETRY_STUDY)
        self.assertEqual(scope.commit_line(none), "")
        self.assertEqual(scope.conclusion_line(none), "")
        self.assertEqual(scope.completion(none), {"scoped": False})

    def test_no_internal_vocabulary_reaches_the_screen(self):
        """Plain English only: no route names, rule numbers or case ids."""
        spoken = " ".join([scope.commit_line(self.unmet),
                           scope.conclusion_line(self.unmet),
                           scope.SCOPED_HEADLINE])
        for banned in ("geometry-study", "intent", "workflow", "router",
                       "GATE", "PASS", "NOT A RESULT", "pre-registration",
                       "docket", "L-", "sdk/", ".py"):
            self.assertNotIn(banned, spoken, banned)
        self.assertIsNone(re.search(r"\bR\d+\b", spoken))

    def test_two_asks_are_joined_as_english_not_as_a_list_dump(self):
        unmet = scope.unmet_asks("Blown slot with a transient run.",
                                 GEOMETRY_STUDY)
        self.assertEqual(len(unmet), 2)
        self.assertIn(" and ", scope.commit_line(unmet))
        self.assertNotIn("[", scope.commit_line(unmet))


class TheCompletionIsQualified(unittest.TestCase):
    def test_an_unfulfilled_request_never_closes_out_unqualified(self):
        done = scope.completion(scope.unmet_asks(_BLOWING_PROMPT,
                                                 GEOMETRY_STUDY))
        self.assertIs(done["scoped"], True)
        self.assertNotEqual(done["headline"], "MISSION COMPLETE")
        self.assertIn("NOT RUN", done["headline"])
        self.assertEqual(done["not_run"], ["a blowing sweep"])

    def test_a_fulfilled_request_carries_no_headline_override(self):
        done = scope.completion(())
        self.assertIs(done["scoped"], False)
        self.assertNotIn("headline", done)


class TheInterfaceObeysTheBackend(unittest.TestCase):
    """The page must not invent the verdict, and must not keep it either."""

    def setUp(self):
        self.html = CONTROL_ROOM.read_text()

    def test_the_completion_label_defers_to_the_scoped_headline(self):
        self.assertIn("(state.scope && state.scope.headline) || 'MISSION COMPLETE'",
                      self.html)

    def test_the_page_listens_for_the_scope_event(self):
        self.assertIn("case 'mission.scoped':", self.html)

    def test_the_completion_payload_is_passed_to_finish(self):
        self.assertIn("finish('complete', p)", self.html)

    def test_a_scope_down_does_not_survive_into_the_next_mission(self):
        self.assertIn("state.scope = null;", self.html)


class TheDispatchLayerActuallySaysIt(unittest.TestCase):
    """The pure checks above prove the wording. They prove nothing about
    whether dispatch CALLS it, which is where the failure actually lived. This
    drives the real `_run_workflow` with a stand-in workflow module and reads
    the events the interface would have received.
    """

    def _run(self, request):
        import os
        import sys
        import tempfile
        import types
        import unittest.mock

        from chief_engineer import server
        from chief_engineer.events import EventBus
        from chief_engineer.router import GEOMETRY_STUDY, Route

        # `_run_workflow` persists the record. Left alone that writes a fake
        # mission into the LIVE state directory, where the running control room
        # would list it. The state root is redirected for the duration.
        tmp = tempfile.mkdtemp(prefix="scope-test-")
        patched = unittest.mock.patch.dict(
            os.environ, {"CHIEF_ENGINEER_STATE_DIR": tmp})
        patched.start()
        self.addCleanup(patched.stop)

        name = "workflows._scope_down_stub"
        stub = types.ModuleType(name)
        stub.main = lambda **kwargs: None      # a run that does its job fine
        sys.modules[name] = stub
        self.addCleanup(sys.modules.pop, name, None)

        record = server.MissionRecord("m-scope-test", request,
                                      EventBus("m-scope-test"))
        route = Route(GEOMETRY_STUDY, 0.99, "stub route", (), {})
        server._run_workflow(record, route,
                             {"module": name, "output": "geometry-study"})
        self.assertEqual(record.state, "complete")
        return [(e.event, e.payload) for e in record.bus.snapshot()]

    def test_a_blowing_prompt_is_scoped_down_at_commit_and_at_the_end(self):
        events = self._run(_BLOWING_PROMPT)
        kinds = [name for name, _ in events]

        # Said at commit time, on the interpretation screen, BEFORE the run.
        self.assertIn("mission.scoped", kinds)
        self.assertLess(kinds.index("mission.scoped"),
                        kinds.index("mission.completed"))

        spoken = [p["message"] for name, p in events
                  if name == "transcript.entry"]
        self.assertEqual(len(spoken), 2, spoken)
        self.assertIn("cannot do that", spoken[0])
        self.assertIn("blown-slot case", spoken[0])
        self.assertIn("Not run", spoken[1])

        # And the completion is never unqualified.
        done = dict(events[-1][1])
        self.assertEqual(events[-1][0], "mission.completed")
        self.assertIs(done["scoped"], True)
        self.assertEqual(done["headline"], scope.SCOPED_HEADLINE)

    def test_a_matched_prompt_is_untouched(self):
        events = self._run(_PLAIN_PROMPT)
        kinds = [name for name, _ in events]
        self.assertNotIn("mission.scoped", kinds)
        self.assertNotIn("transcript.entry", kinds)
        done = dict(events[-1][1])
        self.assertIs(done["scoped"], False)
        self.assertNotIn("headline", done)


if __name__ == "__main__":
    unittest.main()
