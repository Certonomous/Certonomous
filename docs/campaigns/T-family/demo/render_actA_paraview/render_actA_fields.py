#!/usr/bin/env pvbatch
"""Act A, Screen 6: the temperature field across all three regions, ParaView.

    xvfb-run -a pvbatch render_actA_fields.py [--out DIR]

WHY ALL THREE REGIONS IN ONE RENDER
------------------------------------
The physics of this act is conjugate: the heated core, the housing wall and the
cooling air are solved together, so the metal and the air set each other's
temperature. A single-region render tells the wrong story. This draws core,
housing and fluid in one view on one Celsius colour scale, so the gradient
through the housing wall and the plume in the air read as one continuous field.

WHAT IS MEASURED HERE RATHER THAN ASSUMED
------------------------------------------
* Each region's cell count is asserted against ``T23_T24_MESH_FACTS.json``
  before anything is painted. The wrong-mesh failure this defends against is
  real and is documented in ``_actA_render_common``.
* The colour range is READ from ``actA_screen_data.json``, so the four airspeed
  renders share one scale and can honestly be compared.
* The graded run tree is fingerprinted before and after and must not have moved.

The fields on disk are in kelvin; every Act A screen is in Celsius, so a
Calculator converts and the colour bar carries Celsius.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _actA_render_common import (AXISYMMETRY_PLANE_LINE, END_TIME,  # noqa: E402
                                 PRIMARY, REGIONS, RenderRefusal, announce,
                                 assert_paraview_version,
                                 assert_run_tree_untouched, caption,
                                 field_range_degC, frame_axial_plane,
                                 open_region, run_tree_fingerprint,
                                 save_screenshot, to_celsius, white_background)

DEFAULT_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def render_temperature(case_dir: str, out_dir: str) -> str:
    from paraview.simple import (ColorBy, CreateRenderView, GetColorTransferFunction,
                                 GetScalarBar, Show)

    before = run_tree_fingerprint(case_dir)

    view = CreateRenderView()
    view.ViewSize = [1600, 900]
    view.OrientationAxesVisibility = 0
    white_background(view)

    scratch = []
    converted = []
    try:
        for region in REGIONS:
            reader, root, n_cells = open_region(case_dir, region, ["T"])
            scratch.append(root)
            announce(f"  {region:<8} {n_cells:>7,} cells, checked against the "
                     f"mesh record")
            celsius = to_celsius(reader, "T")
            celsius.UpdatePipeline(10000.0)
            converted.append(celsius)
            disp = Show(celsius, view)
            ColorBy(disp, ("CELLS", "T_degC"))
            disp.SetScalarBarVisibility(view, region == "core")

        # MEASURED across all three regions, so the air is not clamped to black.
        lo, hi = field_range_degC(converted)
        announce(f"  colour range measured across the three regions: "
                 f"{lo:.1f} to {hi:.1f} degC")

        lut = GetColorTransferFunction("T_degC")
        lut.ApplyPreset("Inferno (matplotlib)", True)
        lut.RescaleTransferFunction(lo, hi)

        bar = GetScalarBar(lut, view)
        bar.Title = "Temperature"
        bar.ComponentTitle = "degC"
        bar.AutomaticLabelFormat = 0
        bar.LabelFormat = "%.0f"
        # Min and max appear as the colour bar's end ticks and nowhere else,
        # per the figure standard.
        bar.UseCustomLabels = 1
        bar.CustomLabels = [lo, (lo + hi) / 2.0, hi]

        frame_axial_plane(view)
        caption(view, AXISYMMETRY_PLANE_LINE)

        path = os.path.join(out_dir, "actA_temperature_field_paraview.png")
        n = save_screenshot(view, path)
        announce(f"  wrote {os.path.basename(path)} ({n:,} bytes)")
        assert_run_tree_untouched(case_dir, before)
        return path
    finally:
        for root in scratch:
            shutil.rmtree(root, ignore_errors=True)


def render_velocity(case_dir: str, out_dir: str) -> str:
    """Air speed in the fluid region. The solids are not painted with it."""
    from paraview.simple import (ColorBy, CreateRenderView, GetColorTransferFunction,
                                 GetScalarBar, Show)

    before = run_tree_fingerprint(case_dir)
    view = CreateRenderView()
    view.ViewSize = [1600, 900]
    view.OrientationAxesVisibility = 0
    white_background(view)

    reader, root, n_cells = open_region(case_dir, "fluid", ["U"])
    try:
        announce(f"  fluid    {n_cells:>7,} cells, checked against the mesh record")
        disp = Show(reader, view)
        ColorBy(disp, ("CELLS", "U", "Magnitude"))
        disp.RescaleTransferFunctionToDataRange(True, False)
        disp.SetScalarBarVisibility(view, True)

        lut = GetColorTransferFunction("U")
        lut.ApplyPreset("Viridis (matplotlib)", True)
        bar = GetScalarBar(lut, view)
        bar.Title = "Air speed"
        bar.ComponentTitle = "m/s"

        frame_axial_plane(view)
        caption(view, AXISYMMETRY_PLANE_LINE)

        path = os.path.join(out_dir, "actA_velocity_field_paraview.png")
        n = save_screenshot(view, path)
        announce(f"  wrote {os.path.basename(path)} ({n:,} bytes)")
        assert_run_tree_untouched(case_dir, before)
        return path
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default=PRIMARY)
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()

    try:
        announce(f"ParaView {assert_paraview_version()}, pinned")
        announce(f"case {os.path.basename(args.case)} at t = {END_TIME}")
        announce("temperature, all three regions:")
        render_temperature(args.case, args.out)
        announce("air speed, fluid region:")
        render_velocity(args.case, args.out)
    except RenderRefusal as exc:
        sys.stderr.write(f"REFUSED: {exc}\n")
        return 2
    announce("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
