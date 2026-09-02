#!/usr/bin/env python3
"""ParaView panels of the adjoint wing's REAL volume grid, with provenance.

WHAT THIS RENDERS AND FROM WHAT. The two panels the adjoint-wing act's meshing
stage serves (``mesh``: the wing's skin as the volume grid holds it, cell edges
drawn; ``mesh_zoom``: the symmetry-plane section through the same grid, closed
on the wall layers marched off the leading edge). Both are drawn from the
served read-only copy of the landed A2 run's own ``constant/polyMesh`` at
``verification/runs/actD_runs/A2_wing_grid`` -- nothing is synthesised,
smoothed, decimated or substituted, per Sanaa's directive that every act shows
the REAL mesh rendered with ParaView and never the old canvas.

THE COUNT IN THE SIDECAR IS THE READER'S, NOT A DOCUMENT'S. The internal mesh
is loaded and its cell count asserted against ``--expect-cells`` before any
panel is saved; the sidecar written beside each PNG carries that count and the
case path, and ``demo_sequencer._panel`` refuses to serve a panel whose sidecar
count differs from the count the screen prints or from the ``owner`` file on
disk at drive time. Three independent readings of one number.

PLANTED-BLANK CONTROL (CLAUDE.md rule 3). A renderer that sees nothing
produces a uniform image, and a uniform image is a zero. Every panel is read
back off disk and its ink fraction measured; before any verdict is trusted,
one deliberately empty view (camera parked outside the domain, geometry
hidden) is rendered and must read BLANK, or this script refuses its own ink
reader and exits 2.

TOOLCHAIN, BY ABSOLUTE PATH, per ``ACTD_PARAVIEW_RENDER_PASS_PREREGISTRATION``:
the 5.13.3 EGL build renders headless on this box and a bare ``pvbatch``
silently selects the older 5.11.2:

    /opt/paraview/bin/pvbatch cases/dafoam/actd_render_grid_panels.py \
        --case verification/runs/actD_runs/A2_wing_grid --expect-cells 38304

Output goes to fd 1/2 directly: pvbatch exits through ``os._exit`` and
swallows buffered ``paraview.simple`` stdout (measured on this box).
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import sys
from pathlib import Path

from paraview.simple import (CreateRenderView, GetActiveCamera, Hide,
                             OpenFOAMReader, Render, SaveScreenshot, Show)

# The control room is a dark surface (--bg: #060708 in control_room.html); a
# panel on any other ground reads as a pasted-in rectangle. Same palette as
# scripts/render_openfoam_paraview.py.
BACKGROUND = (0.024, 0.027, 0.031)
FLUID = (0.043, 0.055, 0.066)
EDGES = (0.400, 0.510, 0.600)
RESOLUTION = (2560, 714)

#: Where the grid in these panels came from: the landed run's own mesh, of
#: which ``--case`` holds a gunzipped byte-for-byte copy (made by
#: ``actd_reproduce_a2_grid.py``'s source constant). Recorded in every sidecar.
SOURCE_POLYMESH = "/home/ubuntu/certonomous-runs/A2-mach-wing/constant/polyMesh"

MIN_INK = 0.02          # a real panel carries at least this much non-ground
MAX_BLANK_INK = 0.005   # the planted empty view must read at most this


def say(text: str) -> None:
    os.write(1, (text + "\n").encode())


def ink_fraction(png: Path) -> float:
    """Fraction of pixels that are not the background ground, read off disk."""
    from paraview import servermanager
    from paraview.vtk.vtkIOImage import vtkPNGReader
    from paraview.vtk.util.numpy_support import vtk_to_numpy

    del servermanager  # imported for its side effect of a full vtk build
    reader = vtkPNGReader()
    reader.SetFileName(str(png))
    reader.Update()
    img = reader.GetOutput()
    arr = vtk_to_numpy(img.GetPointData().GetScalars())
    bg = [round(c * 255) for c in BACKGROUND]
    close = (abs(arr[:, 0] - bg[0]) <= 8) & (abs(arr[:, 1] - bg[1]) <= 8) \
        & (abs(arr[:, 2] - bg[2]) <= 8)
    return float(1.0 - close.sum() / len(arr))


def new_view():
    view = CreateRenderView()
    view.ViewSize = list(RESOLUTION)
    view.Background = list(BACKGROUND)
    view.UseColorPaletteForBackground = 0
    view.OrientationAxesVisibility = 0
    return view


def style(display):
    display.Representation = "Surface With Edges"
    display.DiffuseColor = list(FLUID)
    display.AmbientColor = list(FLUID)
    display.EdgeColor = list(EDGES)
    display.LineWidth = 1.0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--expect-cells", type=int, required=True)
    args = ap.parse_args()
    case = Path(args.case).resolve()
    out = case / "paraview"
    out.mkdir(exist_ok=True)
    foam = case / f"{case.name}.foam"
    foam.touch()

    # -- the count, from the reader itself, before anything is drawn --------
    reader = OpenFOAMReader(FileName=str(foam))
    reader.MeshRegions = ["internalMesh"]
    reader.UpdatePipeline()
    cells = reader.GetDataInformation().GetNumberOfCells()
    points = reader.GetDataInformation().GetNumberOfPoints()
    if cells != args.expect_cells:
        say(f"REFUSED: ParaView reads {cells} cells; expected "
            f"{args.expect_cells}")
        return 2
    say(f"internal mesh: {cells} cells, {points} points")

    # -- planted-blank control: prove the ink reader can see a zero ---------
    view = new_view()
    wing = OpenFOAMReader(FileName=str(foam))
    wing.MeshRegions = ["patch/wing"]
    wing.UpdatePipeline()
    disp = Show(wing, view)
    style(disp)
    Hide(wing, view)
    cam = GetActiveCamera()
    cam.SetPosition(5000.0, 5000.0, 5000.0)
    cam.SetFocalPoint(6000.0, 6000.0, 6000.0)
    Render(view)
    blank = out / "_planted_blank.png"
    SaveScreenshot(str(blank), view, ImageResolution=RESOLUTION)
    got = ink_fraction(blank)
    blank.unlink()
    if got > MAX_BLANK_INK:
        say(f"REFUSED: the planted empty view reads ink {got:.4f}; the ink "
            f"reader cannot be trusted to see a blank")
        return 2
    say(f"planted blank read back at ink {got:.4f}: the reader sees a zero")

    stamp = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    me = Path(__file__).resolve()
    sha = hashlib.sha256(me.read_bytes()).hexdigest()

    def save(panel: str, view) -> None:
        png = out / f"{case.name}_{panel}.png"
        SaveScreenshot(str(png), view, ImageResolution=RESOLUTION)
        ink = ink_fraction(png)
        if ink < MIN_INK:
            say(f"REFUSED: {png.name} reads ink {ink:.4f}; a blank panel "
                f"does not ship")
            png.unlink()
            raise SystemExit(2)
        sidecar = {
            "panel": panel,
            "image": png.name,
            # The two keys demo_sequencer._panel asserts on: the count the
            # reader measured off this very mesh, and the case it is of.
            "cells": int(cells),
            "case": str(case),
            "points": int(points),
            "source_polymesh": SOURCE_POLYMESH,
            "data_provenance": (
                "rendered from the case's own constant/polyMesh, a gunzipped "
                "byte-for-byte copy of the landed A2-mach-wing run's grid; "
                "no synthesised, smoothed or decimated geometry"),
            "script": str(me.relative_to(me.parents[2])),
            "script_sha256": sha,
            "paraview": "5.13.3 EGL (/opt/paraview/bin/pvbatch)",
            "resolution": list(RESOLUTION),
            "theme": "dark",
            "ink_fraction": ink,
            "generated_utc": stamp,
        }
        (out / f"{case.name}_{panel}.json").write_text(
            json.dumps(sidecar, indent=1, sort_keys=True) + "\n",
            encoding="utf-8")
        say(f"{png.name}: ink {ink:.3f}, {cells} cells")

    # -- mesh: the wing's skin as the volume grid holds it ------------------
    Show(wing, view)
    b = wing.GetDataInformation().GetBounds()
    cx, cy, cz = ((b[0] + b[1]) / 2, (b[2] + b[3]) / 2, (b[4] + b[5]) / 2)
    span = b[5] - b[4]
    cam.SetFocalPoint(cx, cy, cz)
    # Three-quarter view from above and ahead of the leading edge, span
    # running across the wide frame.
    cam.SetPosition(cx - 0.9 * span, cy + 0.65 * span, cz + 0.55 * span)
    cam.SetViewUp(0.0, 1.0, 0.0)
    view.CameraParallelProjection = 0
    Render(view)
    view.ResetCamera()
    cam.Dolly(2.7)
    Render(view)
    save("mesh", view)
    Hide(wing, view)

    # -- mesh_zoom: the symmetry-plane section, closed on the wall layers ---
    sym = OpenFOAMReader(FileName=str(foam))
    sym.MeshRegions = ["patch/sym"]
    sym.UpdatePipeline()
    disp = Show(sym, view)
    style(disp)
    wb = wing.GetDataInformation().GetBounds()
    le_x = wb[0]                       # leading edge at the root section
    view.CameraParallelProjection = 1
    frame_h = (RESOLUTION[1] / RESOLUTION[0]) * 3.6   # metres tall for 3.6 wide
    # Camera on the +z side looking back through the plane, so x runs to the
    # RIGHT of the frame and the leading edge sits at the left, the
    # conventional reading; from -z the section renders mirrored.
    cam.SetFocalPoint(le_x + 1.2, 0.0, 0.0)
    cam.SetPosition(le_x + 1.2, 0.0, 50.0)
    cam.SetViewUp(0.0, 1.0, 0.0)
    cam.SetParallelScale(frame_h / 2.0)
    Render(view)
    save("mesh_zoom", view)
    say("PASS: both panels rendered with provenance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
