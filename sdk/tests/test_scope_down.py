"""A run must say what it cannot do, and must never close out as though it did.

The failure these pin happened on camera: a prompt asking for a blown slot
routed to the plain single-body study, the study solved the unblown baseline,
and the screen said the mission was complete at high confidence over a request
most of which was never run.

Two halves are pinned, and the second matters as much as the first: a matched
prompt must NOT acquire a scope-down it does not deserve.
"""

import re
import shutil
import subprocess
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

        AMENDED 2026-09-02: the tripwire this docstring promised ("if routing
        ever improves, this fails loudly") FIRED, exactly as written. The
        jet-flap demo act registered its route, and the bare "Airfoil blown
        slot" prompt now classifies to jet-flap-display (measured 0.74) --
        the one route scope.CAPABILITIES declares able to BLOW -- so that
        prompt moved to its own test below, which pins the improvement. The
        sweep-phrased prompt here still lands on the generic study (measured
        0.99) with the blowing ask unmet, so the mismatch stays reachable and
        the scope-down tests above still test something. Regression controls
        measured unmoved at the amendment: DMR 0.99, adjoint 0.90, motor
        0.91, battery 0.99 on their registered prompts.
        """
        route = apply_surface(classify(_BLOWING_PROMPT), "airfoil.stl")
        self.assertEqual(route.intent, GEOMETRY_STUDY, _BLOWING_PROMPT)
        self.assertTrue(scope.unmet_asks(_BLOWING_PROMPT, route.intent),
                        _BLOWING_PROMPT)

    def test_the_bare_blown_slot_prompt_routes_to_the_act_that_blows(self):
        """The other half of the fired tripwire, pinned in the new direction.

        "Airfoil blown slot" is the exact prompt that once became an unblown
        3D baseline on camera. It now routes to the jet-flap act, whose
        capability declaration (scope.CAPABILITIES[JET_FLAP_DISPLAY] carries
        BLOWING -- an explicit promise, not the undeclared-run vacuous case)
        means the blowing ask is MET there: unmet_asks must be empty. If
        routing ever regresses this prompt back to the generic study, this
        fails loudly, symmetric to the amended test above.
        """
        from chief_engineer.router import JET_FLAP_DISPLAY

        prompt = "Airfoil blown slot"
        route = apply_surface(classify(prompt), "airfoil.stl")
        self.assertEqual(route.intent, JET_FLAP_DISPLAY, prompt)
        self.assertEqual(scope.unmet_asks(prompt, route.intent), (), prompt)

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
    """The page must not invent the verdict, and must not keep it either.

    THIS CLASS USED TO GREP THE HTML, AND THAT CERTIFIED NOTHING. It held four
    `assertIn` checks against the page source: the scoped headline expression,
    the `case 'mission.scoped':` label, the argument list at the finish() call
    site, and `state.scope = null;`. No JavaScript ever ran, so nothing was
    proven about what the screen shows.

    Two findings retired them, reached independently and from opposite
    directions. An audit of the dispatch layer found a request the lab openly
    DECLINES to run still closing under MISSION COMPLETE, because the page
    read a literal at the call site instead of the status the backend sent,
    and every check here passed throughout. A cross-team mutation audit then
    hard-wired MISSION COMPLETE into the page while leaving the asserted
    substrings alive in a dead comment, and the whole suite stayed green.

    A grep for a substring survives any mutation that keeps the substring. So
    the interface half is certified by EXECUTING the page against a stub DOM,
    in the harness below, which drives all four closing states and carries
    planted controls that must go red when the behaviour is reverted. Run
    against the pre-fix page it reports the defect in three lines.

    THIS CERTIFICATION IS FAIL-OPEN WITHOUT NODE, AND THAT IS SAID OUT LOUD.
    The test below SKIPS when no node binary is present, and a skip is not a
    pass: on such a box the suite reports green with the page uncertified,
    which is the exact state this class was rewritten to end. Node is present
    on the lab box (/usr/bin/node), so the page is certified here today. If
    you are reading a green suite somewhere else, check for the skip before
    believing the page was executed at all.
    """

    def test_the_page_is_certified_by_running_it_not_by_reading_it(self):
        node = shutil.which("node") or shutil.which("nodejs")
        if not node:
            # FAIL-OPEN, deliberately and visibly. See the class docstring.
            self.skipTest("node is needed to execute the control room page: "
                          "the page is NOT certified in this run")
        harness = Path(__file__).resolve().parent / "control_room_pacing_harness.js"
        done = subprocess.run([node, str(harness), str(CONTROL_ROOM)],
                              capture_output=True, text=True, timeout=300)
        self.assertEqual(
            done.returncode, 0,
            "the control room's closing states are wrong on the running page. "
            "A clean run, a scoped run, a declined request and a failed run "
            "must each close under their own label, and none of them may read "
            "as a completion the mission did not earn:\n"
            + done.stdout + done.stderr)

    def test_no_backend_status_reaches_the_page_unnamed(self):
        """A status the page does not name inherits MISSION COMPLETE silently.

        The page closes a mission on `(p && p.status) || 'complete'`, so any
        status it has no branch for falls through to MISSION COMPLETE. For
        today's statuses that is correct. A fifth one added to the backend
        would be asserted as a success without a word being said, and found on
        camera, which is the shape of L-221/L-222: an entry is inserted with
        an assert, never left to a default.

        So the default is not left to trust. This reads the statuses the
        backend REALLY publishes on a terminal mission event, out of the AST
        rather than out of a comment, and fails when one appears that the page
        does not distinguish. The fix when it fails is to teach finish() the
        new status and add it to the harness's closing-state set, not to widen
        the set here.
        """
        import ast

        server_py = CONTROL_ROOM.parent / "server.py"
        tree = ast.parse(server_py.read_text())
        published = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or len(node.args) < 2:
                continue
            name = (node.func.attr if isinstance(node.func, ast.Attribute)
                    else getattr(node.func, "id", None))
            event = node.args[0]
            if name != "publish" or not isinstance(event, ast.Constant):
                continue
            if not str(event.value).startswith("mission."):
                continue
            body = node.args[1]
            if not isinstance(body, ast.Dict):
                continue
            for key, value in zip(body.keys, body.values):
                if (isinstance(key, ast.Constant) and key.value == "status"
                        and isinstance(value, ast.Constant)):
                    published.add(value.value)

        # Plant a control: a walk that found nothing would pass vacuously.
        self.assertIn("complete", published,
                      "the AST walk found no published status at all, so this "
                      "check proves nothing. Fix the walk, not the assertion.")
        # 'complete' is the page's fallback; 'incomplete' has its own branch.
        self.assertEqual(
            published - {"complete", "incomplete"}, set(),
            "the backend publishes a mission status the control room does not "
            "name, so it will close under MISSION COMPLETE without a word "
            "being said. Give it a branch in finish() and a case in the "
            "closing-state set in control_room_pacing_harness.js.")


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
