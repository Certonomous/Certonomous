#!/usr/bin/env pvbatch
"""Act A, Screens 4/5: the mesh drawn as REAL CELLS, plus the wall-layer zoom.

    xvfb-run -a pvbatch render_actA_mesh.py [--out DIR]

Sanaa's Screen 5 asks for the computational grid shown cell by cell, in place of
a tessellation, with a wall zoom and a resolution table. This draws the actual
polyMesh of all three solved regions with their cell edges, and then a zoom on
the air lying against the heated housing, which is where the heat leaves the
metal and where the near-wall resolution has to be earned.

Every region's cell count is asserted against ``T23_T24_MESH_FACTS.json`` before
it is drawn, so a wrong mesh refuses rather than rendering (see
``_actA_render_common``). The graded run tree is never written to.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _actA_render_common import (AXISYMMETRY_PLANE_LINE, END_TIME,  # noqa: E402
                                 PRIMARY, REGIONS, RenderRefusal, announce,
                                 announce_error, assert_paraview_version,
                                 assert_run_tree_untouched, caption,
                                 frame_axial_plane, geometry_m, open_region,
                                 run_tree_fingerprint, save_screenshot,
                                 white_background)

DEFAULT_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

#: One flat colour per region, so the eye separates metal from air without a
#: colour bar. These are display choices and carry no physical meaning.
REGION_COLOUR = {
    "fluid":   [0.80, 0.86, 0.92],
    "housing": [0.55, 0.60, 0.66],
    "core":    [0.36, 0.40, 0.45],
}


def _show_regions(view, case_dir, line_width=0.5):
    """Draw all three region meshes as real cells. Returns scratch roots."""
    from paraview.simple import Show

    roots = []
    for region in REGIONS:
        reader, root, n_cells = open_region(case_dir, region, ["T"])
        roots.append(root)
        announce(f"  {region:<8} {n_cells:>7,} cells, checked against the "
                 f"mesh record")
        disp = Show(reader, view)
        disp.Representation = "Surface With Edges"
        disp.DiffuseColor = REGION_COLOUR[region]
        disp.EdgeColor = [0.15, 0.18, 0.22]
        disp.LineWidth = line_width
    return roots


def render_whole(case_dir: str, out_dir: str) -> str:
    from paraview.simple import CreateRenderView

    before = run_tree_fingerprint(case_dir)
    view = CreateRenderView()
    view.ViewSize = [1600, 900]
    view.OrientationAxesVisibility = 0
    white_background(view)

    roots = _show_regions(view, case_dir)
    try:
        frame_axial_plane(view)
        caption(view, AXISYMMETRY_PLANE_LINE)
        out = os.path.join(out_dir, "actA_mesh_paraview.png")
        n = save_screenshot(view, out)
        announce(f"  wrote {os.path.basename(out)} ({n:,} bytes)")
        assert_run_tree_untouched(case_dir, before)
        return out
    finally:
        for root in roots:
            shutil.rmtree(root, ignore_errors=True)


def render_wall_zoom(case_dir: str, out_dir: str) -> str:
    """The air against the heated housing, close enough to count layers."""
    from paraview.simple import CreateRenderView

    before = run_tree_fingerprint(case_dir)
    block = geometry_m()
    r_house_outer = float(block["housing_inner_radius"]) + float(
        block["housing_wall_thickness"])
    z0, z1 = 0.0, float(block["heated_section_length"])

    view = CreateRenderView()
    view.ViewSize = [1600, 900]
    view.OrientationAxesVisibility = 0
    white_background(view)

    roots = _show_regions(view, case_dir, line_width=1.0)
    try:
        # A tight window straddling the housing surface: a few millimetres of
        # metal below, the first few millimetres of air above.
        half = 0.010
        view.CameraParallelProjection = 1
        view.CameraPosition = [-1.0, r_house_outer, 0.5 * (z0 + z1)]
        view.CameraFocalPoint = [0.0, r_house_outer, 0.5 * (z0 + z1)]
        view.CameraViewUp = [0.0, 1.0, 0.0]
        view.CameraParallelScale = half

        caption(view, "20 mm window at r = 37.5 mm ; y+ = 0.73-0.75 on the "
                      "heated housing")
        caption(view, AXISYMMETRY_PLANE_LINE, position=(0.02, 0.055))

        out = os.path.join(out_dir, "actA_mesh_wall_zoom_paraview.png")
        n = save_screenshot(view, out)
        announce(f"  wrote {os.path.basename(out)} ({n:,} bytes)")
        assert_run_tree_untouched(case_dir, before)
        return out
    finally:
        for root in roots:
            shutil.rmtree(root, ignore_errors=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default=PRIMARY)
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()
    try:
        announce(f"ParaView {assert_paraview_version()}, pinned")
        announce(f"mesh, real cells, {os.path.basename(args.case)}:")
        render_whole(args.case, args.out)
        announce("wall-layer zoom at the heated housing:")
        render_wall_zoom(args.case, args.out)
    except RenderRefusal as exc:
        announce_error(f"REFUSED: {exc}")
        os._exit(2)
    announce("done")
    os._exit(0)


if __name__ == "__main__":
    main()
