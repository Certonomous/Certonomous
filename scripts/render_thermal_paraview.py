#!/usr/bin/env python3
"""ParaView renders for the two THERMAL demo acts (motor duct, battery module).

Run under ``/opt/paraview/bin/pvpython`` (5.13.3 EGL, headless). The shared
``render_openfoam_paraview.py`` slices at the mid plane of a z extrusion; the
motor case is an axisymmetric WEDGE whose thin direction is x, so this script
takes the slice axis as an argument instead of assuming one.

WHAT IS DRAWN IS THE CASE'S OWN MESH AND ITS OWN FIELDS, read-only. For a
conjugate (multi-region) case the reader's ``internalMesh`` is the PRE-SPLIT
mesh, whose cell count is exactly the count the acts print on screen, and
that equality is ASSERTED (``--expect-cells``) rather than trusted. For a
FIELD panel the pre-split mesh carries no fields, so the named regions are
staged into a throwaway per-region scratch case (constant/<region>/polyMesh
and <time>/<region>/* copied under a plain single-region layout), opened,
asserted to sum to the pre-split count, rendered, and deleted.

Every panel writes a sidecar JSON beside it carrying the case path and the
cell count actually read, so whatever serves the image can assert the count
on screen is the count in the picture. A panel whose rendered ink fraction is
below ``--min-ink`` is REFUSED (exit 2): a renderer that saw nothing produces
a uniform background, and a uniform background is a zero (CLAUDE.md rule 3).

Output goes only under ``--out``; nothing in the case tree is modified other
than the zero-byte ``case.foam`` stub the reader requires.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import shutil
import sys
import tempfile

from paraview.simple import (  # noqa: E402
    CreateRenderView, GetColorTransferFunction, GetScalarBar, Hide,
    OpenFOAMReader, SaveScreenshot, Show, Slice,
)

#: The control room is a dark surface (--bg #060708); a render dropped into
#: its viewport must sit on the same ground.
BACKGROUND = (0.024, 0.027, 0.031)
FLUID = (0.043, 0.055, 0.066)
EDGES = (0.400, 0.510, 0.600)


def say(text):
    os.write(1, (text + "\n").encode())


def open_case(case_dir, regions=("internalMesh",)):
    foam = os.path.join(case_dir, "case.foam")
    if not os.path.exists(foam):
        open(foam, "w").close()
    reader = OpenFOAMReader(FileName=foam)
    reader.MeshRegions = list(regions)
    reader.UpdatePipelineInformation()
    return reader


def latest_time(reader):
    times = [float(t) for t in reader.TimestepValues or []]
    return times[-1] if times else 0.0


def slice_mid(source, axis, position=None):
    bounds = source.GetDataInformation().GetBounds()
    i = {"x": 0, "y": 1, "z": 2}[axis]
    mid = position if position is not None else 0.5 * (bounds[2 * i]
                                                       + bounds[2 * i + 1])
    cut = Slice(Input=source)
    cut.SliceType = "Plane"
    origin = [0.0, 0.0, 0.0]
    origin[i] = mid
    normal = [0.0, 0.0, 0.0]
    normal[i] = 1.0
    cut.SliceType.Origin = origin
    cut.SliceType.Normal = normal
    cut.Triangulatetheslice = 0
    cut.UpdatePipeline()
    return cut


def make_view(axis, bounds, zoom=None, resolution=(1920, 1080)):
    """A parallel-projection view looking down ``axis`` at the section."""
    view = CreateRenderView()
    view.ViewSize = list(resolution)
    view.Background = list(BACKGROUND)
    view.UseColorPaletteForBackground = 0
    view.OrientationAxesVisibility = 0
    view.CameraParallelProjection = 1
    plane = {"x": (2, 1), "y": (0, 2), "z": (0, 1)}[axis]
    h, v = plane
    if zoom is None:
        lo_h, hi_h = bounds[2 * h], bounds[2 * h + 1]
        lo_v, hi_v = bounds[2 * v], bounds[2 * v + 1]
    else:
        (lo_h, hi_h), (lo_v, hi_v) = zoom
    ch, cv = 0.5 * (lo_h + hi_h), 0.5 * (lo_v + hi_v)
    span_h, span_v = hi_h - lo_h, hi_v - lo_v
    aspect = resolution[0] / resolution[1]
    scale = max(span_v / 2.0, span_h / (2.0 * aspect)) * 1.04
    i = {"x": 0, "y": 1, "z": 2}[axis]
    centre = [0.0, 0.0, 0.0]
    centre[{"x": 0, "y": 1, "z": 2}[axis]] = 0.5 * (bounds[2 * i]
                                                    + bounds[2 * i + 1])
    centre[h] = ch
    centre[v] = cv
    eye = list(centre)
    eye[i] += 1.0
    view.CameraFocalPoint = centre
    view.CameraPosition = eye
    view.CameraViewUp = {0: [0, 0, 1], 1: [0, 0, 1], 2: [0, 1, 0]}[h] \
        if False else ([0, 0, 1] if v == 2 else [0, 1, 0])
    view.CameraParallelScale = scale
    return view


def ink_fraction(path):
    from PIL import Image

    img = Image.open(path).convert("RGB")
    bg = tuple(int(round(255 * c)) for c in BACKGROUND)
    pixels = img.getdata()
    ink = sum(1 for p in pixels
              if abs(p[0] - bg[0]) + abs(p[1] - bg[1]) + abs(p[2] - bg[2]) > 18)
    return ink / float(img.width * img.height)


def sidecar(path, case_dir, panel, cells, extra):
    record = {
        "image": os.path.basename(path),
        "case": os.path.abspath(case_dir),
        "case_name": os.path.basename(os.path.abspath(case_dir)),
        "panel": panel,
        "cells": int(cells),
        "paraview": "5.13.3 EGL (/opt/paraview/bin/pvpython)",
        "script": "scripts/render_thermal_paraview.py",
        "script_sha256": hashlib.sha256(
            open(os.path.abspath(__file__), "rb").read()).hexdigest(),
        "generated_utc": datetime.datetime.utcnow().strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
        "data_provenance": ("rendered from the case's own constant/polyMesh "
                            "and time directories; nothing synthesised, "
                            "smoothed or decimated"),
        "ink_fraction": ink_fraction(path),
    }
    record.update(extra)
    with open(os.path.splitext(path)[0] + ".json", "w") as fh:
        json.dump(record, fh, indent=2, sort_keys=True)
    return record


def render(view, path, min_ink, label):
    SaveScreenshot(path, view, ImageResolution=view.ViewSize)
    frac = ink_fraction(path)
    if frac < min_ink:
        os.write(2, (f"REFUSED: {label} rendered {frac:.5f} ink, below "
                     f"{min_ink}; a blank panel is a zero nobody read\n"
                     ).encode())
        os._exit(2)
    say(f"  {label}: ink {frac:.4f} -> {path}")
    return frac


def mesh_panels(args, prefix):
    reader = open_case(args.case)
    t = latest_time(reader)
    reader.UpdatePipeline(t)
    info = reader.GetDataInformation()
    n_cells = info.GetNumberOfCells()
    if args.expect_cells is not None and n_cells != args.expect_cells:
        os.write(2, (f"REFUSED: mesh has {n_cells} cells, expected "
                     f"{args.expect_cells}\n").encode())
        os._exit(2)
    cut = slice_mid(reader, args.axis)
    polys = cut.GetDataInformation().GetNumberOfCells()
    if polys != n_cells:
        os.write(2, (f"REFUSED: the section shows {polys} polygons against "
                     f"{n_cells} cells; the slice is not one cell of every "
                     f"column\n").encode())
        os._exit(2)
    bounds = reader.GetDataInformation().GetBounds()

    for panel, zoom in (("mesh", None), ("mesh_zoom", args.zoom_window)):
        view = make_view(args.axis, bounds, zoom=zoom)
        show = Show(cut, view)
        show.Representation = "Surface With Edges"
        show.AmbientColor = list(FLUID)
        show.DiffuseColor = list(FLUID)
        show.EdgeColor = list(EDGES)
        show.LineWidth = 1.0
        path = os.path.join(args.out, f"{prefix}_{panel}.png")
        render(view, path, args.min_ink, panel)
        sidecar(path, args.case, panel, n_cells, {
            "slice_polygons": polys, "axis": args.axis,
            "zoom_window": zoom, "time": t,
        })
        Hide(cut, view)


def field_panel(args, prefix):
    """Temperature over the named regions at ``--field-time``.

    The pre-split mesh carries no fields, so each region is staged into a
    throwaway single-region case (its polyMesh plus its own field files under
    the chosen time), opened, and rendered; the region cell counts must sum
    to the pre-split count.
    """
    regions = [r for r in args.field_regions.split(",") if r]
    time_name = args.field_time
    scratch = tempfile.mkdtemp(prefix="thermal_field_")
    readers = []
    total = 0
    try:
        for region in regions:
            root = os.path.join(scratch, region)
            os.makedirs(os.path.join(root, "constant"))
            shutil.copytree(
                os.path.join(args.case, "constant", region, "polyMesh"),
                os.path.join(root, "constant", "polyMesh"))
            shutil.copytree(
                os.path.join(args.case, time_name, region),
                os.path.join(root, time_name))
            reader = open_case(root)
            reader.UpdatePipeline(float(time_name))
            n = reader.GetDataInformation().GetNumberOfCells()
            total += n
            readers.append((region, reader))
        if args.expect_cells is not None and total != args.expect_cells:
            os.write(2, (f"REFUSED: the regions sum to {total} cells against "
                         f"the pre-split {args.expect_cells}\n").encode())
            os._exit(2)

        lut = GetColorTransferFunction("T")
        lut.ApplyPreset("Inferno (matplotlib)", True)
        lo, hi = None, None
        cuts = []
        for region, reader in readers:
            cut = slice_mid(reader, args.axis)
            arrays = cut.GetCellDataInformation()
            t_info = arrays.GetArray("T")
            if t_info is None:
                os.write(2, f"REFUSED: no T on region {region}\n".encode())
                os._exit(2)
            rlo, rhi = t_info.GetComponentRange(0)
            lo = rlo if lo is None else min(lo, rlo)
            hi = rhi if hi is None else max(hi, rhi)
            cuts.append(cut)
        lut.RescaleTransferFunction(lo, hi)

        bounds = [None] * 6
        for _, reader in readers:
            b = reader.GetDataInformation().GetBounds()
            for i in range(3):
                bounds[2 * i] = b[2 * i] if bounds[2 * i] is None else \
                    min(bounds[2 * i], b[2 * i])
                bounds[2 * i + 1] = b[2 * i + 1] if bounds[2 * i + 1] is None \
                    else max(bounds[2 * i + 1], b[2 * i + 1])
        view = make_view(args.axis, bounds)
        shows = []
        for cut in cuts:
            show = Show(cut, view)
            show.Representation = "Surface"
            show.ColorArrayName = ["CELLS", "T"]
            show.LookupTable = lut
            shows.append(show)
        bar = GetScalarBar(lut, view)
        bar.Title = "T (K)"
        bar.ComponentTitle = ""
        bar.Visibility = 1
        shows[0].SetScalarBarVisibility(view, True)
        path = os.path.join(args.out, f"{prefix}_field_T.png")
        render(view, path, args.min_ink, "field_T")
        sidecar(path, args.case, "field_T", total, {
            "regions": regions, "time": float(time_name),
            "T_range_K": [lo, hi], "axis": args.axis,
        })
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--axis", required=True, choices=("x", "y", "z"),
                        help="Normal of the section plane, which is the thin "
                             "or extruded direction of the case.")
    parser.add_argument("--expect-cells", type=int, default=None)
    parser.add_argument("--panels", default="mesh",
                        help="Comma list from: mesh (writes mesh and "
                             "mesh_zoom), field (writes field_T).")
    parser.add_argument("--zoom", default=None,
                        help="h0,h1,v0,v1 window, in the section plane's "
                             "horizontal and vertical coordinates, for "
                             "mesh_zoom. Required with the mesh panels.")
    parser.add_argument("--field-regions", default="")
    parser.add_argument("--field-time", default=None)
    parser.add_argument("--min-ink", type=float, default=0.01)
    args = parser.parse_args()
    args.case = os.path.abspath(args.case)
    args.out = os.path.abspath(args.out)
    os.makedirs(args.out, exist_ok=True)
    prefix = os.path.basename(args.case)

    wanted = [p for p in args.panels.split(",") if p]
    if "mesh" in wanted:
        if not args.zoom:
            os.write(2, b"--zoom is required with the mesh panels\n")
            os._exit(2)
        h0, h1, v0, v1 = [float(v) for v in args.zoom.split(",")]
        args.zoom_window = ((h0, h1), (v0, v1))
        mesh_panels(args, prefix)
    if "field" in wanted:
        if not args.field_regions or not args.field_time:
            os.write(2, b"field panel needs --field-regions and --field-time\n")
            os._exit(2)
        field_panel(args, prefix)
    say("done")
    os._exit(0)


main()
