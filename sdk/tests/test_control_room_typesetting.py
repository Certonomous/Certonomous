"""Every variable on a camera surface is typeset, not just table cells.

Katie, 2026-07-31: latexify every variable. The acts emit ``C_d``, ``C_L`` and
``C_p`` in narration, table captions, viewport labels, legend names, trace
titles, landscape titles and canvas axis labels. Only table headers and cells
ran through the page's ``subScript``; every other surface is ``textContent`` or
canvas, so it rendered the literal underscore.

Reading the page source for the word ``subScript`` would prove nothing about
what is drawn. The harness this test drives evaluates the REAL page script
against a stub DOM whose canvas records every ``fillText`` call, pushes an act's
worth of events through ``dispatch``, drains the paced reveal queue, and reads
back what landed: the markup surfaces must carry a ``<sub>`` tag and no raw
underscore, and a canvas variable must have been drawn as two runs, the index
smaller than the symbol and dropped below its baseline.

Run against the pre-fix page the harness reports ten failures, including
``a canvas label was drawn with a raw underscore: ["C_d","C_d","C_d"]``.
"""
from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
HARNESS = Path(__file__).resolve().parent / "control_room_typeset_harness.js"
CONTROL_ROOM = SDK / "chief_engineer" / "control_room.html"
NODE = shutil.which("node") or shutil.which("nodejs")


@unittest.skipUnless(NODE, "node is needed to run the control room page script")
class ControlRoomTypesetting(unittest.TestCase):

    def test_every_camera_surface_typesets_its_variables(self):
        done = subprocess.run([NODE, str(HARNESS), str(CONTROL_ROOM)],
                              capture_output=True, text=True, timeout=180)
        self.assertEqual(
            done.returncode, 0,
            "a control room surface rendered a raw underscore where the act "
            "wrote a variable:\n" + done.stdout + done.stderr)


if __name__ == "__main__":
    unittest.main()
