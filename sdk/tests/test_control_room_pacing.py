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
  * releases bring the count back down while `peakWorkers` remembers the peak
    for the end-of-mission summary;
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
          * the resting count after the queue drains is the mission's peak.
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


if __name__ == "__main__":
    unittest.main()
