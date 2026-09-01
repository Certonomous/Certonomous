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
that by painting three recorded pressure bodies through the real page.

WHAT THE PRESSURE PIN IS, AND WHAT IT USED TO BE (changed 2026-09-01). It used
to be a sha256 of the colour SEQUENCE, triangle by triangle. That pin broke
twice on changes that were both correct — the depth-sort repair reordered the
paint on b52 and motorBike without altering one colour, and back-face culling
halved the cube's painted facets on a body measured closed and consistently
wound. A sequence digest cannot tell either of those from a defect. It is now a
pin on the PROPERTIES of the painted surface:

    cullSense per body      culling only on a body MEASURED closed; b52 and
                            motorBike return 0 and must never be culled
    colour multiset         every colour and its facet count, order-independent,
                            so a legitimate re-sort cannot red it
    silhouette coverage     the culled body still covers every cell the whole
                            body covered — 0 lost
    z-buffer, interior      the facet nearest the camera at each covered cell is
                            one the cull KEPT, 0 interior disagreements

The last clause is the load-bearing one. Silhouette coverage cannot tell the
near half of a closed body from the far half — both project to the same
outline — so a cull that kept exactly the wrong side would still score 0 lost.
Only the z-buffer separates them. The fixture carries the measurements and the
reason each threshold is what it is.

The harness does not read the source for these. It evaluates the real page
script against a stub DOM whose canvas records every ``fillStyle`` that reaches
a ``fill()``, serves the recorded field payloads off disk through a stubbed
fetch, and instruments the page's OWN paint loop — recomputing the projection in
the harness could go green on a body the page draws wrongly.

NEITHER THIS FILE NOR THE HARNESS CAN SAY THE SURFACE LOOKS RIGHT. Nothing on
this box executes CSS layout or WebGL. They say which facets were painted and in
what colours. Whether it reads on camera is Sanaa's eye.
"""
from __future__ import annotations

import re
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
        # The pressure pin is on the PROPERTIES of the painted surface, not on
        # the order the triangles were drawn in. The old assertion here read
        # "byte for byte identical to the golden" against a digest of the colour
        # SEQUENCE, and that pin broke twice on changes that were both correct:
        # the depth-sort repair reordered b52 and motorBike without altering a
        # colour, and back-face culling halved the cube on a body measured
        # closed. See the `_why_it_was_regenerated` block in the fixture.
        for body in ("b52 pressure", "motorBike pressure", "cube pressure"):
            self.assertRegex(
                done.stdout,
                rf"{re.escape(body)}\b.*colour multiset matches the golden",
                f"{body} did not match the golden colour multiset:\n{done.stdout}")
        # The cube is the culled one: its surface clauses must have actually run
        # and reported, or the geometry evidence is vacuous.
        self.assertRegex(done.stdout, r"cells covered, 0 lost, .* 0 interior")


if __name__ == "__main__":
    unittest.main()
