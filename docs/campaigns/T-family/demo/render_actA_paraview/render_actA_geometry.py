#!/usr/bin/env pvbatch
"""Act A, Screen 1: the solved body renders on load. ParaView, from the STL.

    xvfb-run -a pvbatch render_actA_geometry.py [--out DIR]

WHICH SURFACE, AND WHY THAT IS CHECKED RATHER THAN TRUSTED
-----------------------------------------------------------
The served surface is ``sdk/geometry/t23_solved_geometry.stl``. A DIFFERENT
surface -- ``motor_in_duct.stl``, sha256 ``131aab8e...`` -- sits on this box at
two paths and was RETIRED: it is dimensioned from a different case, 0.200 m
axial against the solved 0.750 m, with three struts and a nose and tail the
solve does not have. It renders perfectly well. Nothing about a rendered picture
tells you which of the two you are looking at.

So this script does not name a file and hope. It hashes the surface it is about
to draw and refuses unless the digest matches the one the generator wrote beside
the solved case, and it re-measures the axial extent against the parts manifest
before anything reaches a frame.

THE REVOLVE IS DECLARED, BECAUSE THIS ONE IS A REVOLVE
------------------------------------------------------
Unlike the field renders, which show the solved plane, this surface IS a
display revolve: the manifest records ``revolve_segments_DISPLAY_CHOICE: 180``
of an axisymmetric five-degree wedge solve, and requires that the axisymmetry be
stated wherever the surface is shown. :data:`AXISYMMETRY_REVOLVE_LINE` is
therefore the caption here, and the plane line would be false.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _actA_render_common import (AXISYMMETRY_REVOLVE_LINE,  # noqa: E402
                                 GENERATED_STL_FOR_CHECK, PARTS_MANIFEST,
                                 RenderRefusal, SOLVED_STL, announce,
                                 announce_error,
                                 assert_paraview_version, axis_extent, caption,
                                 frame_isometric, refuse, save_screenshot, split_parts,
                                 white_background)

DEFAULT_OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")


def assert_is_the_solved_surface(path: str) -> str:
    """Refuse any surface that is not the one the solved case generates.

    Identity, not shape. A regenerated surface never copied across would pass
    every dimension check while the screen showed the old body, and the retired
    body would pass none of them but only if someone thought to look.
    """
    for candidate, what in ((path, "the served surface"),
                            (GENERATED_STL_FOR_CHECK,
                             "the surface the solved case generates")):
        if not os.path.isfile(candidate):
            refuse(f"{what} is not on disk at {candidate}")

    served = hashlib.sha256(open(path, "rb").read()).hexdigest()
    generated = hashlib.sha256(
        open(GENERATED_STL_FOR_CHECK, "rb").read()).hexdigest()
    if served != generated:
        refuse(f"the surface at {path} is not byte-identical to the one the "
               f"solved case generates ({served[:12]}... against "
               f"{generated[:12]}...), so it may be a stale or retired body and "
               f"will not be drawn")

    manifest = json.loads(open(PARTS_MANIFEST, encoding="utf-8").read())
    retired = (manifest.get("retires") or {}).get("sha256")
    if retired and served == retired:
        refuse(f"the surface at {path} IS the retired body ({retired[:12]}...), "
               f"which is dimensioned from a different case and carries struts, "
               f"a nose and a tail the solve does not have")
    return served


def render(path_stl: str, out_dir: str) -> str:
    from paraview.simple import CreateRenderView, STLReader, Show

    digest = assert_is_the_solved_surface(path_stl)
    announce(f"  surface digest {digest[:16]}..., matches the solved case")

    reader = STLReader(FileNames=[path_stl])
    reader.UpdatePipeline()
    info = reader.GetDataInformation()
    n_cells = info.GetNumberOfCells()
    if n_cells < 1:
        refuse("the surface carries no facets")
    announce(f"  {n_cells:,} facets")

    # The drawn body must be the solved extent. The manifest is the authority.
    z_lo, z_hi, _r = axis_extent()
    bounds = info.GetBounds()
    drawn_axial = bounds[5] - bounds[4]
    solved_axial = z_hi - z_lo
    if abs(drawn_axial - solved_axial) > 1e-3:
        refuse(f"the surface spans {drawn_axial:.3f} m axially where the solved "
               f"case spans {solved_axial:.3f} m; this is not the solved body")
    announce(f"  axial extent {drawn_axial:.3f} m, matches the solved case")

    view = CreateRenderView()
    view.ViewSize = [1600, 900]
    view.OrientationAxesVisibility = 0
    white_background(view)

    # THE DUCT IS DRAWN TRANSLUCENT, AND THAT IS NOT DECORATION. An opaque
    # 0.125 m duct is a featureless grey tube that hides the entire motor
    # inside it -- which is what the first version of this renderer produced,
    # passing every check while showing the viewer nothing. The part the user
    # asked about is the motor, so the duct is a shell you see through.
    parts, parts_dir = split_parts(path_stl)

    duct = Show(STLReader(FileNames=[parts["duct"]]), view)
    duct.Representation = "Surface"
    duct.DiffuseColor = [0.62, 0.67, 0.72]
    duct.Opacity = 0.22

    body = Show(STLReader(FileNames=[parts["motor"]]), view)
    body.Representation = "Surface"
    body.DiffuseColor = [0.42, 0.47, 0.53]
    body.Opacity = 1.0

    heated = Show(STLReader(FileNames=[parts["housing_heated"]]), view)
    heated.Representation = "Surface"
    heated.DiffuseColor = [0.86, 0.42, 0.20]     # the heated section, named below
    heated.Opacity = 1.0

    frame_isometric(view)
    caption(view, AXISYMMETRY_REVOLVE_LINE)
    caption(view, "L = 0.750 m ; heated housing 0.125 m (orange) ; "
                  "duct r = 0.125 m, opacity 0.22",
            position=(0.02, 0.055))

    out = os.path.join(out_dir, "actA_geometry_paraview.png")
    n = save_screenshot(view, out)
    announce(f"  wrote {os.path.basename(out)} ({n:,} bytes)")
    shutil.rmtree(parts_dir, ignore_errors=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stl", default=SOLVED_STL)
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()
    try:
        announce(f"ParaView {assert_paraview_version()}, pinned")
        announce("geometry, the solved body:")
        render(args.stl, args.out)
    except RenderRefusal as exc:
        announce_error(f"REFUSED: {exc}")
        os._exit(2)
    announce("done")
    os._exit(0)


if __name__ == "__main__":
    main()
