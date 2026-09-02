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
    Calculator, Clip, CreateRenderView, GetColorTransferFunction,
    GetScalarBar, Hide, OpenFOAMReader, SaveScreenshot, Show, Slice,
    STLReader,
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


#: Composite geometry of the mesh page: one 1920x1080 canvas carrying the
#: fit-to-extents section AND a zoom inset at the wall, bottom-right, with a
#: locator rectangle on the main panel showing where the inset lives. Sanaa
#: 06:10Z (motor): "the solved polyMesh section, cell by cell, horizontal,
#: fit-to-extents, wall-layer grading visible, with a zoom inset at the
#: housing wall"; 06:50Z (battery): "Fit-to-extents so all seven bands are
#: visible, then a zoom inset on one channel showing the wall layers -- same
#: pattern as the motor's mesh page."
CANVAS = (1920, 1080)
INSET = (760, 430)
MARGIN = 40


def _show_edges(cut, view):
    show = Show(cut, view)
    show.Representation = "Surface With Edges"
    show.AmbientColor = list(FLUID)
    show.DiffuseColor = list(FLUID)
    show.EdgeColor = list(EDGES)
    show.LineWidth = 1.0
    return show


def _composite_with_inset(main_path, inset_path, out_path, axis, bounds,
                          zoom_window, main_res):
    """Paste the fit-to-extents section and the zoom inset onto one canvas.

    The locator rectangle is drawn with :func:`make_view`'s own world-to-pixel
    map (parallel scale = max(span_v/2, span_h/(2*aspect)) * 1.04 about the
    section centre, scale being the view's half height), so the rectangle on
    the main panel is the inset's window by construction, not by eye.
    """
    from PIL import Image, ImageDraw

    bg = tuple(int(round(255 * c)) for c in BACKGROUND)
    line = tuple(int(round(255 * c)) for c in EDGES)
    canvas = Image.new("RGB", CANVAS, bg)
    main = Image.open(main_path).convert("RGB")
    inset = Image.open(inset_path).convert("RGB")

    main_w, main_h = main.size
    wide = main_w / main_h >= CANVAS[0] / CANVAS[1]
    main_at = ((CANVAS[0] - main_w) // 2, MARGIN) if wide \
        else (MARGIN, (CANVAS[1] - main_h) // 2)
    inset_at = (CANVAS[0] - INSET[0] - MARGIN, CANVAS[1] - INSET[1] - MARGIN)
    # The inset must sit on background, never on the section it locates.
    overlap_x = main_at[0] + main_w > inset_at[0] - MARGIN
    overlap_y = main_at[1] + main_h > inset_at[1] - MARGIN
    if overlap_x and overlap_y:
        os.write(2, (b"REFUSED: the mesh composite would paste the inset "
                     b"over the section; pick a smaller main panel\n"))
        os._exit(2)
    canvas.paste(main, main_at)
    canvas.paste(inset, inset_at)

    draw = ImageDraw.Draw(canvas)
    # Locator rectangle: world -> main-panel pixels, make_view's map.
    plane = {"x": (2, 1), "y": (0, 2), "z": (0, 1)}[axis]
    h, v = plane
    ch = 0.5 * (bounds[2 * h] + bounds[2 * h + 1])
    cv = 0.5 * (bounds[2 * v] + bounds[2 * v + 1])
    span_h = bounds[2 * h + 1] - bounds[2 * h]
    span_v = bounds[2 * v + 1] - bounds[2 * v]
    aspect = main_res[0] / main_res[1]
    scale = max(span_v / 2.0, span_h / (2.0 * aspect)) * 1.04
    per_px = (main_res[1] / 2.0) / scale        # pixels per world unit

    def to_px(wh, wv):
        return (main_at[0] + main_w / 2.0 + (wh - ch) * per_px,
                main_at[1] + main_h / 2.0 - (wv - cv) * per_px)

    (h0, h1), (v0, v1) = zoom_window
    x0, y1 = to_px(h0, v0)
    x1, y0 = to_px(h1, v1)
    locator = [x0, y0, x1, y1]
    draw.rectangle(locator, outline=line, width=3)
    draw.rectangle([inset_at[0] - 2, inset_at[1] - 2,
                    inset_at[0] + INSET[0] + 2, inset_at[1] + INSET[1] + 2],
                   outline=line, width=3)
    # A leader from the locator to the inset, so the eye pairs them.
    draw.line([x1, (y0 + y1) / 2.0, inset_at[0] - 2,
               inset_at[1] + INSET[1] / 2.0], fill=line, width=2)
    canvas.save(out_path)
    return {"main_px": [main_at[0], main_at[1], main_w, main_h],
            "inset_px": [inset_at[0], inset_at[1], INSET[0], INSET[1]],
            "locator_px": [round(p, 1) for p in locator]}


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

    # The served mesh panel is the COMPOSITE: fit-to-extents section at its
    # own content aspect plus the wall zoom inset, one canvas. The separate
    # full-size zoom stays as the mesh_zoom panel exactly as before.
    plane = {"x": (2, 1), "y": (0, 2), "z": (0, 1)}[args.axis]
    h, v = plane
    span_h = bounds[2 * h + 1] - bounds[2 * h]
    span_v = bounds[2 * v + 1] - bounds[2 * v]
    inset_room = (CANVAS[0] - INSET[0] - 3 * MARGIN,
                  CANVAS[1] - INSET[1] - 3 * MARGIN)
    if span_h / span_v >= CANVAS[0] / CANVAS[1]:
        main_res = (CANVAS[0] - 2 * MARGIN,
                    max(64, int(round((CANVAS[0] - 2 * MARGIN)
                                      * span_v / span_h))))
        if main_res[1] > inset_room[1]:
            main_res = (max(64, int(round(inset_room[1] * span_h / span_v))),
                        inset_room[1])
    else:
        main_res = (max(64, int(round((CANVAS[1] - 2 * MARGIN)
                                      * span_h / span_v))),
                    CANVAS[1] - 2 * MARGIN)
        if main_res[0] > inset_room[0]:
            main_res = (inset_room[0],
                        max(64, int(round(inset_room[0] * span_v / span_h))))

    scratch_main = os.path.join(args.out, f"{prefix}_mesh_main_tmp.png")
    view = make_view(args.axis, bounds, resolution=list(main_res))
    _show_edges(cut, view)
    render(view, scratch_main, 0.0, "mesh main (composite half)")
    Hide(cut, view)

    scratch_inset = os.path.join(args.out, f"{prefix}_mesh_inset_tmp.png")
    view = make_view(args.axis, bounds, zoom=args.zoom_window,
                     resolution=list(INSET))
    _show_edges(cut, view)
    render(view, scratch_inset, 0.0, "mesh inset (composite half)")
    Hide(cut, view)

    path = os.path.join(args.out, f"{prefix}_mesh.png")
    geometry = _composite_with_inset(scratch_main, scratch_inset, path,
                                     args.axis, bounds, args.zoom_window,
                                     main_res)
    os.remove(scratch_main)
    os.remove(scratch_inset)
    frac = ink_fraction(path)
    if frac < args.min_ink:
        os.write(2, (f"REFUSED: mesh composite rendered {frac:.5f} ink, "
                     f"below {args.min_ink}\n").encode())
        os._exit(2)
    say(f"  mesh composite: ink {frac:.4f} -> {path}")
    sidecar(path, args.case, "mesh", n_cells, {
        "slice_polygons": polys, "axis": args.axis,
        "zoom_window": args.zoom_window, "time": t,
        "composite": geometry,
    })

    view = make_view(args.axis, bounds, zoom=args.zoom_window)
    _show_edges(cut, view)
    path = os.path.join(args.out, f"{prefix}_mesh_zoom.png")
    render(view, path, args.min_ink, "mesh_zoom")
    sidecar(path, args.case, "mesh_zoom", n_cells, {
        "slice_polygons": polys, "axis": args.axis,
        "zoom_window": args.zoom_window, "time": t,
    })
    Hide(cut, view)


def volume_cut_panel(args, prefix):
    """One section of a THREE-DIMENSIONAL volume mesh at a declared plane.

    INSERTED (never replacing ``mesh_panels``) for the adjoint wing's
    symmetry-plane cut, Sanaa 0540Z item 5: "the symmetry-plane slice of the
    38,304-cell volume mesh showing the wall layers growing off the wing,
    rendered cell by cell by the same renderer the motor act uses."

    WHY ``mesh_panels`` CANNOT DRAW IT: that path's polygons==cells equality
    is built for one-cell-thick meshes, where a mid-plane cut crosses every
    cell exactly once. On a 3-D mesh a plane cut crosses one CELL COLUMN of
    the extrusion, so the honest count is the number of cells the plane
    passes through, and nothing in the case can tell the renderer what that
    should be. So the caller DECLARES the plane (``--slice-at``) and the
    expected polygon count (``--expect-slice-polys``); this refuses without
    both, and refuses when the cut disagrees with the declaration. For the
    wing: the sym patch holds 1,672 faces, and a plane just inside it
    (z = 0.01) cuts exactly the 1,672 adjacent cells (measured on this box
    before this function was written).
    """
    if args.slice_at is None or args.expect_slice_polys is None:
        os.write(2, b"REFUSED: volume_cut needs --slice-at and "
                    b"--expect-slice-polys; a 3-D mesh's plane cut has no "
                    b"self-evident polygon count to assert against\n")
        os._exit(2)
    reader = open_case(args.case)
    t = latest_time(reader)
    reader.UpdatePipeline(t)
    info = reader.GetDataInformation()
    n_cells = info.GetNumberOfCells()
    if args.expect_cells is not None and n_cells != args.expect_cells:
        os.write(2, (f"REFUSED: mesh has {n_cells} cells, expected "
                     f"{args.expect_cells}\n").encode())
        os._exit(2)
    cut = slice_mid(reader, args.axis, position=args.slice_at)
    polys = cut.GetDataInformation().GetNumberOfCells()
    if polys != args.expect_slice_polys:
        os.write(2, (f"REFUSED: the section shows {polys} polygons against "
                     f"the declared {args.expect_slice_polys}; the plane is "
                     f"not cutting the cell layer the caller named\n"
                     ).encode())
        os._exit(2)
    bounds = reader.GetDataInformation().GetBounds()
    view = make_view(args.axis, bounds, zoom=args.zoom_window)
    show = Show(cut, view)
    show.Representation = "Surface With Edges"
    show.AmbientColor = list(FLUID)
    show.DiffuseColor = list(FLUID)
    show.EdgeColor = list(EDGES)
    show.LineWidth = 1.0
    path = os.path.join(args.out, f"{prefix}_volume_cut.png")
    render(view, path, args.min_ink, "volume_cut")
    sidecar(path, args.case, "volume_cut", n_cells, {
        "slice_polygons": polys, "expected_slice_polygons":
            args.expect_slice_polys, "slice_at": args.slice_at,
        "axis": args.axis, "zoom_window": args.zoom_window, "time": t,
        **({"caption": args.caption} if args.caption else {}),
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

        # CELSIUS ON SCREEN (Sanaa 07:05Z: "Units mix across figures ...
        # Pick C everywhere on screen"). The case's own T is kelvin; a
        # Calculator subtracts the exact offset and the bar is titled in C.
        # The sidecar keeps the kelvin range beside the celsius one, so the
        # figure stays checkable against the run's own files.
        lut = GetColorTransferFunction("T_C")
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
            calc = Calculator(Input=cut)
            calc.AttributeType = "Cell Data"
            calc.ResultArrayName = "T_C"
            calc.Function = "T - 273.15"
            calc.UpdatePipeline()
            c_info = calc.GetCellDataInformation().GetArray("T_C")
            if c_info is None:
                os.write(2, (f"REFUSED: the celsius conversion produced no "
                             f"array on region {region}\n").encode())
                os._exit(2)
            clo, chi = c_info.GetComponentRange(0)
            if abs(clo - (rlo - 273.15)) > 1e-6 \
                    or abs(chi - (rhi - 273.15)) > 1e-6:
                os.write(2, (f"REFUSED: T_C range ({clo}, {chi}) is not "
                             f"T - 273.15 of ({rlo}, {rhi}) on region "
                             f"{region}\n").encode())
                os._exit(2)
            cuts.append(calc)
        lut.RescaleTransferFunction(lo - 273.15, hi - 273.15)

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
            show.ColorArrayName = ["CELLS", "T_C"]
            show.LookupTable = lut
            shows.append(show)
        bar = GetScalarBar(lut, view)
        bar.Title = "T (C)"
        bar.ComponentTitle = ""
        # Plain decimals at the ends, not scientific notation: the min and
        # max a viewer reads are "20.0" and "22.2", never "2.2e+01".
        bar.RangeLabelFormat = "%.1f"
        bar.LabelFormat = "%.1f"
        bar.AutomaticLabelFormat = 0
        bar.Visibility = 1
        shows[0].SetScalarBarVisibility(view, True)
        path = os.path.join(args.out, f"{prefix}_field_T.png")
        render(view, path, args.min_ink, "field_T")
        sidecar(path, args.case, "field_T", total, {
            "regions": regions, "time": float(time_name),
            "T_range_K": [lo, hi],
            "T_range_C": [lo - 273.15, hi - 273.15],
            "colour_bar_units": "C", "axis": args.axis,
        })
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def geometry_panel(args, prefix):
    """The act's body as a ParaView render of its measured surface.

    Sanaa's orders of 2026-09-02: every visual is a ParaView render, no
    client tessellation ("ALL runs show ParaView, no tessellation"), and the
    motor's centrebody must VISIBLY run the full duct length, which the
    straight-on view hid. The surface rendered is the file the act's own
    geometry guard measures against the solved case; the sidecar carries its
    hash beside the case and cell count the served panel is asserted with.

    ``--clip-plane x`` cuts the body open along the axis so the interior is
    visible for its whole length (the motor's duct hides its centrebody
    otherwise); the battery module needs no cut. The camera is an oblique
    view built from ``--view-dir`` so the long axis lies across the frame.
    """
    stl = os.path.abspath(args.stl)
    reader = STLReader(FileNames=[stl])
    reader.UpdatePipeline()
    source = reader
    if args.clip_plane:
        i = {"x": 0, "y": 1, "z": 2}[args.clip_plane]
        bounds = reader.GetDataInformation().GetBounds()
        cut = Clip(Input=reader)
        cut.ClipType = "Plane"
        origin = [0.5 * (bounds[0] + bounds[1]),
                  0.5 * (bounds[2] + bounds[3]),
                  0.5 * (bounds[4] + bounds[5])]
        origin[i] = args.clip_at if args.clip_at is not None else origin[i]
        normal = [0.0, 0.0, 0.0]
        normal[i] = 1.0
        cut.ClipType.Origin = origin
        cut.ClipType.Normal = normal
        cut.Invert = 1
        cut.UpdatePipeline()
        source = cut

    bounds = source.GetDataInformation().GetBounds()
    centre = [0.5 * (bounds[0] + bounds[1]), 0.5 * (bounds[2] + bounds[3]),
              0.5 * (bounds[4] + bounds[5])]
    spans = [bounds[1] - bounds[0], bounds[3] - bounds[2],
             bounds[5] - bounds[4]]
    reach = max(spans) * 2.2
    direction = [float(v) for v in args.view_dir.split(",")]
    norm = max(sum(v * v for v in direction) ** 0.5, 1e-12)
    eye = [c + reach * v / norm for c, v in zip(centre, direction)]

    view = CreateRenderView()
    view.ViewSize = [1920, 1080]
    view.Background = list(BACKGROUND)
    view.UseColorPaletteForBackground = 0
    view.OrientationAxesVisibility = 0
    view.CameraParallelProjection = 0
    view.CameraFocalPoint = centre
    view.CameraPosition = eye
    view.CameraViewUp = [float(v) for v in args.view_up.split(",")]
    show = Show(source, view)
    show.Representation = "Surface"
    show.AmbientColor = [0.105, 0.125, 0.145]
    show.DiffuseColor = [0.42, 0.52, 0.62]
    view.ResetCamera(False)

    path = os.path.join(args.out, f"{prefix}_geometry.png")
    render(view, path, args.min_ink, "geometry")
    sidecar(path, args.case, "geometry", args.expect_cells, {
        "surface": stl,
        "surface_sha256": hashlib.sha256(open(stl, "rb").read()).hexdigest(),
        "clip_plane": args.clip_plane,
        "view_dir": args.view_dir,
        "note": ("the rendered file is the surface the act's geometry stage "
                 "measures against the solved case; the cell count beside it "
                 "is the solved grid the act prints, carried so the served "
                 "panel is asserted against the same number"),
    })
    Hide(source, view)


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
                             "mesh_zoom), field (writes field_T), "
                             "volume_cut (one declared-plane section of a "
                             "3-D mesh; needs --slice-at, "
                             "--expect-slice-polys and --zoom).")
    parser.add_argument("--slice-at", type=float, default=None,
                        help="volume_cut only: the section plane's position "
                             "on --axis, declared by the caller.")
    parser.add_argument("--expect-slice-polys", type=int, default=None,
                        help="volume_cut only: the polygon count the "
                             "declared plane must cut, asserted; a 3-D "
                             "mesh's cut has no self-evident count.")
    parser.add_argument("--caption", default=None,
                        help="volume_cut only: caption recorded in the "
                             "panel's provenance sidecar.")
    parser.add_argument("--zoom", default=None,
                        help="h0,h1,v0,v1 window, in the section plane's "
                             "horizontal and vertical coordinates, for "
                             "mesh_zoom. Required with the mesh panels.")
    parser.add_argument("--field-regions", default="")
    parser.add_argument("--field-time", default=None)
    parser.add_argument("--stl", default=None,
                        help="Surface file for the geometry panel: the file "
                             "the act's geometry guard measures.")
    parser.add_argument("--clip-plane", default=None, choices=("x", "y", "z"),
                        help="Cut the geometry open along this axis so the "
                             "interior shows for its full length.")
    parser.add_argument("--clip-at", type=float, default=None)
    parser.add_argument("--view-dir", default="1,0.55,0.85",
                        help="Camera direction (from the body towards the "
                             "eye), comma separated.")
    parser.add_argument("--view-up", default="0,1,0")
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
    if "volume_cut" in wanted:
        if not args.zoom:
            os.write(2, b"--zoom is required with the volume_cut panel\n")
            os._exit(2)
        h0, h1, v0, v1 = [float(v) for v in args.zoom.split(",")]
        args.zoom_window = ((h0, h1), (v0, v1))
        volume_cut_panel(args, prefix)
    if "geometry" in wanted:
        if not args.stl:
            os.write(2, b"the geometry panel needs --stl\n")
            os._exit(2)
        geometry_panel(args, prefix)
    say("done")
    os._exit(0)


main()
