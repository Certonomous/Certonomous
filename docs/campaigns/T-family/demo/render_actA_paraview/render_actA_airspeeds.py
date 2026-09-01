#!/usr/bin/env pvbatch
"""Act A: the same body at four duct airspeeds, on ONE MEASURED SCALE.

    xvfb-run -a pvbatch render_actA_airspeeds.py [--out DIR]

WHY THE SHARED SCALE IS THE WHOLE POINT
----------------------------------------
The claim this set makes is comparative: faster air cools the housing and
shrinks the hot region behind it. That claim is only legible if all four frames
are painted on the SAME colour scale. Four frames each auto-scaled to their own
range would look nearly identical and would silently destroy the comparison --
the hottest case and the coolest case would both run black-to-yellow.

So every case is opened first, the Celsius range is MEASURED across all four at
once with ``field_range_degC``, and only then is anything painted. The range is
reported on screen so a viewer can see what the colours mean.

The recorded ``map_colour_range_degC`` is NOT used here: it spans the sixteen
PEAK values (24.7 to 107.7 degC) and painting a whole field on it clamps the
~15 degC cooling air to the bottom colour. That is a different quantity's range.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _actA_render_common import (AXISYMMETRY_PLANE_LINE, END_TIME,  # noqa: E402
                                 REGIONS, T23_RUNS, RenderRefusal, announce,
                                 announce_error, assert_paraview_version,
                                 assert_run_tree_untouched, caption,
                                 field_range_degC, frame_axial_plane,
                                 open_region, refuse, run_tree_fingerprint,
                                 save_screenshot, to_celsius, white_background)

DEFAULT_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

#: The four solved airspeeds at 305 W. Discovered on disk, never assumed.
AIRSPEEDS = (10, 20, 30, 40)
POWER_W = 305


def case_dir(speed: int) -> str:
    path = os.path.join(T23_RUNS, f"T23_P{POWER_W}_U{speed}")
    if not os.path.isdir(path):
        refuse(f"the {speed} m/s point is not on disk at {path}, so this "
               f"comparison will not be drawn with one of its four members "
               f"missing")
    return path


def main() -> int:
    from paraview.simple import (ColorBy, CreateRenderView,
                                 GetColorTransferFunction, GetScalarBar, Show)

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()

    roots: list[str] = []
    try:
        announce(f"ParaView {assert_paraview_version()}, pinned")
        cases = [(u, case_dir(u)) for u in AIRSPEEDS]
        before = {u: run_tree_fingerprint(d) for u, d in cases}

        # PASS ONE: open every case and MEASURE the shared range before any
        # frame is painted.
        loaded = {}
        for speed, path in cases:
            per_region = []
            for region in REGIONS:
                reader, root, n_cells = open_region(path, region, ["T"])
                roots.append(root)
                celsius = to_celsius(reader, "T")
                celsius.UpdatePipeline(float(END_TIME))
                per_region.append(celsius)
            loaded[speed] = per_region
            announce(f"  {speed:>2} m/s loaded, three regions checked")

        every = [c for group in loaded.values() for c in group]
        lo, hi = field_range_degC(every)
        announce(f"  ONE scale measured across all four cases: "
                 f"{lo:.1f} to {hi:.1f} degC")

        # PASS TWO: paint each case on that one scale.
        written = []
        for speed, per_region in loaded.items():
            view = CreateRenderView()
            view.ViewSize = [1600, 900]
            view.OrientationAxesVisibility = 0
            white_background(view)

            for index, celsius in enumerate(per_region):
                disp = Show(celsius, view)
                ColorBy(disp, ("CELLS", "T_degC"))
                disp.SetScalarBarVisibility(view, index == 0)

            lut = GetColorTransferFunction("T_degC")
            lut.ApplyPreset("Inferno (matplotlib)", True)
            lut.RescaleTransferFunction(lo, hi)
            bar = GetScalarBar(lut, view)
            bar.Title = "Temperature"
            bar.ComponentTitle = "degC"
            bar.AutomaticLabelFormat = 0
            bar.LabelFormat = "%.0f"

            frame_axial_plane(view)
            caption(view, f"Duct airspeed {speed} metres per second, "
                          f"{POWER_W} watts dissipated.")
            caption(view, AXISYMMETRY_PLANE_LINE, position=(0.02, 0.055))
            caption(view, f"All four frames share one scale, "
                          f"{lo:.0f} to {hi:.0f} degC.",
                    position=(0.02, 0.09))

            out = os.path.join(args.out,
                               f"actA_airspeed_U{speed}_paraview.png")
            n = save_screenshot(view, out)
            announce(f"  wrote {os.path.basename(out)} ({n:,} bytes)")
            written.append(out)

        for speed, path in cases:
            assert_run_tree_untouched(path, before[speed])
        announce(f"  {len(written)} frames, one measured scale, "
                 f"four graded run trees unchanged")

    except RenderRefusal as exc:
        announce_error(f"REFUSED: {exc}")
        os._exit(2)
    finally:
        for root in roots:
            shutil.rmtree(root, ignore_errors=True)

    announce("done")
    os._exit(0)


if __name__ == "__main__":
    main()
