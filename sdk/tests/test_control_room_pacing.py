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
"""
from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
HARNESS = Path(__file__).resolve().parent / "control_room_pacing_harness.js"
CONTROL_ROOM = SDK / "chief_engineer" / "control_room.html"
NODE = shutil.which("node") or shutil.which("nodejs")


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


if __name__ == "__main__":
    unittest.main()
