"""The KPI numerals must move in lockstep with the operations on screen.

Katie's standing rule is "KPIs must read live DURING runs, in lockstep with
the paced narration". On 2026-07-30 she reported the opposite: "the number of
agents and numbers of workers must appear at the same time as the operations
that are shown".

The cause was that `agent.started`, `worker.provisioned` and `worker.released`
mutated the KPI row the instant they arrived off the SSE stream, while
everything the viewer actually watches (narration, transcript tables,
geometry, fields, plots, traces, landscape points, dispatch, roster) went
through `enqueue(...)` and revealed on the paced queue. The counters therefore
ran ahead of the beats that explained them.

Checking that from Python by grepping the page for the word "enqueue" would
prove nothing about behaviour. The harness this test drives evaluates the REAL
page script against a stub DOM and a virtual clock, so it can step the reveal
queue one beat at a time and read the KPI row between beats. It asserts:

  * a burst of counter events does not land all at once (only the head of an
    idle queue applies synchronously, which is correct: the queue must not add
    latency to a mission's first beat);
  * the numerals climb as the queue drains, and rest on the right values;
  * releases bring the count back down, and it stays down;
  * a mission whose backend finishes early does not close out on a stale
    count, because `finish()` waits for the queue to be empty and done;
  * a counter event sandwiched between two narration beats is revealed
    between them, which is what "in lockstep" actually means.

Run against the pre-fix page this harness reports seven failures, including
"7 of 7 counter events applied before the queue paced them".

2026-07-31. Katie reported the SAME symptom again on every act, and on the
Monte Carlo race in particular: "the workers should appear as soon as either
reduced or mc start". The synthetic tests above still passed, because they
feed the three events the page had been taught to pace. No recorded mission
emits any of them: real streams carry the counts on `roster.update`, which
rides the queue behind a dozen front loaded narration beats, so the fleet
numeral surfaced tens of seconds after the fleet was visibly working.

The replay test below settles that on recorded streams instead of synthetic
ones. It pushes a real mission through `dispatch` at its real inter event
timing and measures, for every fleet size the backend put on the wire, how
long before that number is on screen. Measured against the pre-fix page:

    race   worst wire to screen lag 18.3 s (fleet numeral first moves at
           18.6 s, while the race lanes started at 0.2 s)
    act    worst lag 26.8 s
    sweep  worst lag 19.6 s

and against the fixed page: 2.9 s, 3.7 s, 3.7 s.

2026-07-31, again. "Reverify that the worker count is exactly in sync with the
meshing/solving." A few seconds is not in sync, and a separate run of the
harness on four more acts found something worse than lag: on the NASA hump and
the adjoint acts the Workers numeral never left zero at all until finish()
restored the peak. Both acts declare their fleet and stand it down on ONE
timestamp, and the time-based catch-up then applied the rise and the release in
the same frame, so the numeral read 0 for the whole run.

Measured on those four acts plus the original three, against the pre-fix page:

    hump     numeral first moves at 64.4 s of a 64.4 s run, held non zero 0.0 s
    adjoint  numeral first moves at 47.2 s of a 47.2 s run, held non zero 0.0 s
    b52      worst rise lag 3.7 s, ahmed 2.6 s, race 2.9 s, act 3.7 s, sweep 3.7 s

and against the fixed page: the worst wire-to-screen lag on a fleet RISE is
0.0 s on all seven streams, and the numeral stands at a fleet size for 20% to
97% of each run.

2026-07-31, third time. "The worker count is still not synchro, it goes from 6
to 0 to 6 again whereas it should be 6 when the meshing/run starts and go to 0
when the run is complete." The shape she asked for is 0, then the fleet, then 0,
once. The bounce was NOT the acts: replayed, every one of the seven streams puts
a clean 0 -> N -> 0 on the wire (only the screening sweep declares two fleets,
12 and then 9, which is what that act does). The third value was the page's:
`finish()` restored the mission's PEAK to the KPI row on completion, so a run
that had honestly stood its fleet down to 0 climbed back to 6 the moment it
ended. The peak restore is gone; the fleet numeral now rests where the machine
does. The harness asserts the shape directly and prints wire-versus-screen, so a
bounce can be attributed to the act that emitted it.
"""
from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
HARNESS = Path(__file__).resolve().parent / "control_room_pacing_harness.js"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
CONTROL_ROOM = SDK / "chief_engineer" / "control_room.html"
NODE = shutil.which("node") or shutil.which("nodejs")

# Recorded missions, kept whole so the replay carries the real burst shape.
# The last four are the acts Katie films, added because the first three all
# passed while the hump and the adjoint showed nothing: a stream whose whole
# fleet lifetime is one timestamp fails differently from one that is merely
# backed up, and only a real recording of it shows that.
STREAMS = [
    FIXTURES / "control_room_race_stream.jsonl",    # Monte Carlo vs reduced order
    FIXTURES / "control_room_act_stream.jsonl",     # a narrated act, 137 s
    FIXTURES / "control_room_sweep_stream.jsonl",   # a short fan out sweep, 40 s
    FIXTURES / "control_room_hump_stream.jsonl",    # NASA wall mounted hump
    FIXTURES / "control_room_adjoint_stream.jsonl", # discrete adjoint on the wing
    FIXTURES / "control_room_b52_stream.jsonl",     # B-52 external aerodynamics
    FIXTURES / "control_room_ahmed_stream.jsonl",   # Ahmed body, 25 degree slant
]


@unittest.skipUnless(NODE, "node is needed to run the control room page script")
class ControlRoomPacing(unittest.TestCase):

    def test_counters_reveal_in_lockstep_with_the_paced_narration(self):
        done = subprocess.run([NODE, str(HARNESS), str(CONTROL_ROOM)],
                              capture_output=True, text=True, timeout=180)
        self.assertEqual(
            done.returncode, 0,
            "the control room's KPI counters are out of step with the paced "
            "reveal queue:\n" + done.stdout + done.stderr)

    def test_the_page_script_still_parses(self):
        """A syntax error here blanks the whole control room on camera."""
        done = subprocess.run([NODE, str(HARNESS), str(CONTROL_ROOM)],
                              capture_output=True, text=True, timeout=180)
        self.assertNotIn("did not evaluate", done.stderr,
                         "the control room script failed to evaluate:\n"
                         + done.stderr)

    def test_the_kpis_read_live_on_recorded_missions(self):
        """The numerals must climb while the work is on screen, not after it.

        Katie's whole objection is that a demo whose numbers arrive at the end
        "looks hardcoded". The bar the harness enforces per stream:

          * the fleet numeral leaves zero in the first half of the run;
          * a fleet RISE reaches the numeral within 0.5 s of the backend
            declaring it, whatever the narration queue is doing, so the
            numeral is up while the mesh and the solve are on screen;
          * a fleet stand down is paced, and still lands before the run ends;
          * the numeral STANDS at a fleet size for at least 15% of the run
            rather than flashing it (the failure that hid on the hump and the
            adjoint, where it stood at a fleet size for 0.0 s);
          * every fleet size declared reaches the numeral;
          * the race lanes and the worker count start together;
          * the Agents and Cycle numerals each move at least twice;
          * the run ends on 0 whenever the mission stood its fleet down;
          * every number on camera is one the mission put on the wire, and the
            screen bounces no more than the wire does.
        """
        for stream in STREAMS:
            self.assertTrue(stream.exists(), f"missing replay fixture {stream}")
        args = [NODE, str(HARNESS), str(CONTROL_ROOM)]
        for stream in STREAMS:
            args += ["--replay", str(stream)]
        done = subprocess.run(args, capture_output=True, text=True, timeout=600)
        self.assertEqual(
            done.returncode, 0,
            "replaying recorded missions shows the KPI row lagging the work "
            "it reports:\n" + done.stdout + done.stderr)


@unittest.skipUnless(NODE, "node is needed to run the control room page script")
class TheMeshCaptionOnScreenIsTheBackendConstant(unittest.TestCase):
    """The caption the viewer reads must BE the backend's string, not a copy.

    The mesh caption is owner-mandated wording that qualifies what the frame
    on screen is worth, and it is emitted on every painted frame of the shape
    optimisation act. The page rendered it on none of them: the field had no
    reader at all.

    A harness holding its own copy of the caption text would go green while
    the screen displayed something else, which is the same class of defect as
    a grep that survives the mutation it was meant to catch. So the text lives
    in exactly one place, and these tests carry it from there to the screen
    rather than restating it: the JS harness proves presence and placement on
    a synthetic string, and the identity of the rendered text against the
    module constant is proven here, where the import lives.
    """

    def _caption(self) -> str:
        from workflows._a2_shape import MESH_CAPTION

        return MESH_CAPTION

    def test_the_rendered_caption_is_byte_identical_to_the_module_constant(self):
        caption = self._caption()
        # Plant a control: an empty constant would make the comparison vacuous.
        self.assertTrue(caption.strip(), "the caption constant is empty")
        harness = Path(__file__).resolve().parent / "control_room_pacing_harness.js"
        done = subprocess.run(
            [NODE, str(harness), str(CONTROL_ROOM), "--caption", caption],
            capture_output=True, text=True, timeout=300)
        self.assertEqual(
            done.returncode, 0,
            "the mesh caption does not reach the screen intact:\n"
            + done.stdout + done.stderr)

    def test_the_workflow_emits_the_constant_by_reference_not_a_literal(self):
        """A literal at the emit site is a copy that drifts the day one is
        edited and the other is not."""
        import ast

        source = (SDK / "workflows" / "adjoint_optimization.py").read_text()
        captions = [
            value for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.Dict)
            for key, value in zip(node.keys, node.values)
            if isinstance(key, ast.Constant) and key.value == "caption"
        ]
        self.assertTrue(
            captions,
            "no caption is emitted at all: the act would paint uncaptioned "
            "frames and this whole class would pass vacuously.")
        for value in captions:
            self.assertNotIsInstance(
                value, ast.Constant,
                "the caption is emitted as a literal string rather than as the "
                "shared constant, so the screen and the module can drift apart.")

    def test_no_second_copy_of_the_caption_text_exists(self):
        """One definition, and the tests carry it. Any second copy is a place
        the wording can be edited without the screen following."""
        # The constant is written as two adjacent string literals, so the text
        # never appears contiguously in the raw source, not even in its own
        # definition. A plain substring sweep therefore finds NOTHING anywhere
        # and passes for the exact wrong reason. Python's parser joins adjacent
        # literals into one constant, so .py files are read through the AST,
        # which sees the assembled string however it was wrapped. Other file
        # types are normalised by dropping the quote and concatenation
        # characters before collapsing whitespace, so `"half" + "half"` is
        # caught as well as a single pasted string.
        #
        # HONEST LIMIT: for non-python files this is a normalised text sweep,
        # not a parse. A copy assembled at run time from pieces, or built by
        # interpolation, would not be found. It catches the realistic failure,
        # which is somebody pasting the sentence into a test or a template to
        # avoid an import. The .py path has no such limit: the AST sees the
        # assembled constant however the source was wrapped.
        import ast
        import re

        caption = self._caption()

        def normalise(text):
            return " ".join(re.sub(r"""["'`+\\]""", " ", text).split())

        needle = normalise(caption)

        def holds(path):
            text = path.read_text(errors="ignore")
            if path.suffix == ".py":
                try:
                    tree = ast.parse(text)
                except SyntaxError:
                    return False
                return any(isinstance(node, ast.Constant)
                           and isinstance(node.value, str)
                           and caption in node.value
                           for node in ast.walk(tree))
            return needle in normalise(text)

        # SOURCE ONLY, and the exclusion is the point rather than a speed-up.
        # sdk/chief-engineer-runs/ holds persisted mission events, and a run of
        # the shape optimisation act writes the caption into them because the
        # backend really did emit it. That is the system working, not a copy of
        # the wording. Sweeping run output would turn this test red the first
        # time the act it protects is actually run.
        roots = [SDK / name for name in ("chief_engineer", "workflows",
                                         "tests", "scripts")]
        holders = sorted(
            str(path.relative_to(SDK))
            for root in roots for path in root.rglob("*")
            if path.is_file() and path.suffix in {".py", ".js", ".html", ".json"}
            and "__pycache__" not in path.parts and holds(path))
        # The definition itself must be found: a search that matches nothing
        # would certify nothing, which is how the raw-substring version of
        # this test passed while proving the opposite of what it claimed.
        self.assertEqual(
            holders, ["workflows/_a2_shape.py"],
            "the caption text is written out in more than one place. Import "
            "the constant instead: a second copy goes stale silently, and a "
            "test holding one certifies its own copy rather than the screen.")


if __name__ == "__main__":
    unittest.main()
