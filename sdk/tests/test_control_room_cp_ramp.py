"""Cp = 0 is the neutral colour, and pressure paints exactly as it did.

Katie, 2026-07-31. Cp painting is live on the hump, the Ahmed body and the
B-52. The values arrive normalised across a clipped percentile window and the
diverging ramp puts its neutral off white stop in the middle of that WINDOW.
Every one of those bodies has deeper suction than stagnation, so the middle of
the window is not Cp = 0:

    hump   colour window [-0.808, 0.286]   Cp = 0 sat at 73.9% of the ramp
    ahmed  colour window [-0.915, 0.646]   Cp = 0 sat at 58.6%
    b52    colour window [-0.368, 0.227]   Cp = 0 sat at 61.8%

and undisturbed flow rendered warm — rgb(232,150,112) on the hump — which the
eye reads as "something is happening here" where nothing is.

The ramp is now anchored: the two sides are scaled independently to their own
extreme so Cp = 0 lands on the neutral stop. Measured after the change, by
rendering: 50.0% on all three, and the face nearest Cp = 0 paints
rgb(242,242,242) on all three.

This applies ONLY where the payload carries ``quantity: "cp"``. Pressure is a
solver quantity in its own units whose zero is a gauge against an arbitrary
reference, so it keeps the linear window it has always had. The harness pins
that: it paints three recorded pressure bodies through the real page and
compares the whole colour sequence, triangle by triangle, against a digest
taken from the page before the change.

The harness does not read the source. It evaluates the real page script against
a stub DOM whose canvas records every ``fillStyle`` that reaches a ``fill()``,
serves the recorded field payloads off disk through a stubbed fetch, and reads
back the colours the body was painted with.
"""
from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
HARNESS = Path(__file__).resolve().parent / "control_room_ramp_harness.js"
GOLDEN = Path(__file__).resolve().parent / "fixtures" / "pressure_paint_golden.json"
CONTROL_ROOM = SDK / "chief_engineer" / "control_room.html"
NODE = shutil.which("node") or shutil.which("nodejs")


@unittest.skipUnless(NODE, "node is needed to run the control room page script")
class ControlRoomCpRamp(unittest.TestCase):

    def test_zero_is_the_neutral_midpoint_and_pressure_is_unchanged(self):
        self.assertTrue(GOLDEN.exists(), f"missing pressure golden {GOLDEN}")
        done = subprocess.run([NODE, str(HARNESS), str(CONTROL_ROOM)],
                              capture_output=True, text=True, timeout=600)
        self.assertEqual(
            done.returncode, 0,
            "the surface colour ramp is wrong:\n" + done.stdout + done.stderr)
        # The reported measurement is part of the evidence, not just the exit
        # code: every Cp body must land on the midpoint.
        for body in ("hump", "ahmed", "b52"):
            self.assertRegex(
                done.stdout, rf"{body}\b.*now at 50\.0%",
                f"{body} did not report Cp = 0 at the ramp midpoint:\n{done.stdout}")
        self.assertIn("byte for byte identical to the golden", done.stdout)


if __name__ == "__main__":
    unittest.main()
