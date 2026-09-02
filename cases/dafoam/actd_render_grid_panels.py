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
    # Flat per-face colour, her wing-view spec: no smooth gradient across a
    # face may suggest geometry the face list does not hold.
    display.Interpolation = "Flat"


#: Sanaa's wing-view spec, verbatim (2026-09-02 ~05:40Z): every wing view in
#: this act draws the solver's wall patch face by face. This caption rides
#: every wall-patch panel's sidecar and payload.
WALL_CAPTION = "the solver's wall patch, 1,008 faces, drawn face by face."
EXPECT_WALL_FACES = 1008
EXPECT_WALL_POINTS = 1031

#: The stored per-iteration surfaces (the optimiser's own shape history) and
#: the iterations the acts show while the solve narration runs. Stride 6 plus
#: the last recorded major: enough frames that the wing visibly walks the
#: optimisation IN STEP with the narration, few enough that the page's paced
#: reveal queue cannot fall behind the script (measured: 48 frames burst in
#: 3 s of emission took the whole reveal past the end of the act).
SHAPE_FRAMES = Path(__file__).resolve().parents[1] / "dafoam" / "ladder-a" \
    / "A2_shape_frames.json"
FRAME_ITERS = (0, 6, 12, 18, 24, 30, 36, 42, 47)


def _patch_quads(case: Path) -> tuple[list, list]:
    """The wing patch's own 1,008 quad faces, off the polyMesh, remapped.

    Returns ``(points, quads)`` where points are the stored shape-history
    vertex order (so a frame's displacements apply by index) and quads are
    the patch's faces re-indexed into that order. The mapping is by exact
    coordinate match at the shape record's own 1e-6 m rounding, and every
    one of the 1,031 patch points must map or this refuses -- a face drawn
    on mismapped points would be a picture of a wing nobody solved.
    """
    import json as _json
    import re as _re

    doc = _json.loads(SHAPE_FRAMES.read_text())
    base = doc["base_vertices"]
    if len(base) != EXPECT_WALL_POINTS:
        raise SystemExit(f"REFUSED: shape record holds {len(base)} points, "
                         f"expected {EXPECT_WALL_POINTS}")
    # Tolerance match at 1e-4 m, bucketed at 1e-3: the stored vertices are
    # rounded to 1e-6 m and the polyMesh points are full precision, so one
    # of the 1,031 points misses an exact 6-dp match (measured); at 1e-4 all
    # 1,031 match the BASELINE surface and zero match the final one, which
    # also proves the landed polyMesh holds the undeformed baseline shape.
    from collections import defaultdict
    buckets = defaultdict(list)
    for i, v in enumerate(base):
        buckets[tuple(round(c, 3) for c in v)].append(i)

    def lookup_pt(c):
        kx, ky, kz = (round(x, 3) for x in c)
        for bx in (round(kx - 0.001, 3), kx, round(kx + 0.001, 3)):
            for by in (round(ky - 0.001, 3), ky, round(ky + 0.001, 3)):
                for bz in (round(kz - 0.001, 3), kz, round(kz + 0.001, 3)):
                    for i in buckets.get((bx, by, bz), ()):
                        v = base[i]
                        if max(abs(v[j] - c[j]) for j in range(3)) < 1e-4:
                            return i
        return None
    poly = case / "constant" / "polyMesh"
    bnd = (poly / "boundary").read_text()
    m = _re.search(r"wing\s*\{[^}]*nFaces\s+(\d+);[^}]*startFace\s+(\d+);",
                   bnd)
    n, start = int(m.group(1)), int(m.group(2))
    if n != EXPECT_WALL_FACES:
        raise SystemExit(f"REFUSED: wing patch holds {n} faces, the caption "
                         f"says {EXPECT_WALL_FACES}")
    pts_lines = (poly / "points").read_text().splitlines()
    i = 0
    while pts_lines[i].strip() != "(":
        i += 1
    coords = []
    for line in pts_lines[i + 1:]:
        s = line.strip()
        if s == ")":
            break
        if s.startswith("("):
            coords.append([float(x) for x in s.strip("()").split()])
    face_lines = (poly / "faces").read_text().splitlines()
    i = 0
    while face_lines[i].strip() != "(":
        i += 1
    quads = []
    for line in face_lines[i + 1 + start:i + 1 + start + n]:
        s = line.strip()
        arity, rest = s.split("(", 1)
        if arity != "4":
            raise SystemExit("REFUSED: a wall face is not a quad; the "
                             "caption says quad faces")
        idx = [int(x) for x in rest.rstrip(")").split()]
        quad = []
        for p in idx:
            hit = lookup_pt(coords[p])
            if hit is None:
                raise SystemExit(f"REFUSED: patch point {p} at {coords[p]} "
                                 f"is not in the stored shape history; the "
                                 f"frames cannot be drawn on the solver's "
                                 f"own patch")
            quad.append(hit)
        quads.append(quad)
    return base, quads


def fit_parallel(view, cam, pts, direction, margin):
    """Aim a parallel-projection camera so ``pts`` FILL the frame.

    Sanaa 1620Z: "can we make the geometry and its color bar bigger pls? rn
    its so small inside a big box ... a lot of empty space around it." A
    hand-tuned dolly leaves whatever margin the tuning day left, so the
    frame is computed instead: every point is projected onto the view
    plane's right/up axes, the focal point is the centre of that footprint
    and the parallel scale is the half-extent containing all of it times
    ``margin``. The geometry fills the frame by construction, whatever the
    eye direction.
    """
    dn = (sum(c * c for c in direction)) ** 0.5
    d = tuple(c / dn for c in direction)
    # screen-up = world +Y minus its component along the view axis;
    # screen-right = up x view-axis (both unit, orthogonal).
    uy = (-d[0] * d[1], 1.0 - d[1] * d[1], -d[1] * d[2])
    un = (sum(c * c for c in uy)) ** 0.5
    uy = tuple(c / un for c in uy)
    rx = (uy[1] * d[2] - uy[2] * d[1],
          uy[2] * d[0] - uy[0] * d[2],
          uy[0] * d[1] - uy[1] * d[0])
    sr = [sum(p[i] * rx[i] for i in range(3)) for p in pts]
    su = [sum(p[i] * uy[i] for i in range(3)) for p in pts]
    mid_r, mid_u = ((max(sr) + min(sr)) / 2, (max(su) + min(su)) / 2)
    half_r, half_u = ((max(sr) - min(sr)) / 2, (max(su) - min(su)) / 2)
    aspect = RESOLUTION[0] / RESOLUTION[1]
    scale = max(half_u, half_r / aspect, 1e-9) * margin
    reach = 2.0 * max(half_r, half_u, 1.0)
    focal = tuple(mid_r * rx[i] + mid_u * uy[i] for i in range(3))
    view.CameraParallelProjection = 1
    cam.SetFocalPoint(*focal)
    cam.SetPosition(*(focal[i] + reach * d[i] for i in range(3)))
    cam.SetViewUp(0.0, 1.0, 0.0)
    cam.SetParallelScale(scale)


def _frame_polydata(points, quads, values):
    """One wall-patch surface as VTK polydata, per-face scalars optional."""
    from paraview.vtk import (vtkCellArray, vtkFloatArray, vtkPoints,
                              vtkPolyData, vtkQuad)

    vp = vtkPoints()
    for x, y, z in points:
        vp.InsertNextPoint(x, y, z)
    cells = vtkCellArray()
    for q in quads:
        quad = vtkQuad()
        for j, p in enumerate(q):
            quad.GetPointIds().SetId(j, p)
        cells.InsertNextCell(quad)
    pd = vtkPolyData()
    pd.SetPoints(vp)
    pd.SetPolys(cells)
    if values is not None:
        arr = vtkFloatArray()
        arr.SetName("val")
        for v in values:
            arr.InsertNextValue(float(v))
        pd.GetCellData().SetScalars(arr)
    return pd


def render_wing_frames(case: Path) -> int:
    """Every wing view the acts show, as face-by-face wall-patch renders.

    Baseline, the gradient on the skin, and the shown iterations of the
    optimisation walk, each twice: the whole wing and the inboard span on a
    closer camera. Per-face CELL scalars, so the colour is flat on each face
    by construction; edges drawn; no triangle anywhere -- the polydata is
    built quad by quad from the patch's own face list.
    """
    import json as _json
    import shutil
    import tempfile

    from paraview.simple import OpenDataFile

    doc = _json.loads(SHAPE_FRAMES.read_text())
    points, quads = _patch_quads(case)
    out = case / "paraview" / "wing"
    out.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="actd_wing_"))
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ")
    me = Path(__file__).resolve()
    sha = hashlib.sha256(me.read_bytes()).hexdigest()

    grad = doc["gradient"]
    gmax = max(abs(v) for v in grad["window_mm_per_step"])
    dlo, dhi = doc["disp_window_mm"]
    dmax = max(abs(dlo), abs(dhi))
    frames = {f["iter"]: f for f in doc["frames"]}
    # The inboard viewing convention the act narrates, from the module that
    # computes it (2.2 m of span), not retyped as a guess.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "sdk"))
    from workflows._a2_shape import CLOSEUP_SPAN_M
    closeup_z = float(CLOSEUP_SPAN_M)

    view = new_view()
    cam = GetActiveCamera()

    def bounds_of(pts):
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        zs = [p[2] for p in pts]
        return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)

    def one(name, pts, values, window, close, bar_title=None, caption=None):
        from paraview.simple import (ColorBy, Delete,
                                     GetColorTransferFunction, GetScalarBar,
                                     Render, Show)
        from paraview.vtk.vtkIOXML import vtkXMLPolyDataWriter

        pd = _frame_polydata(pts, quads, values)
        vtp = tmp / f"{name}.vtp"
        writer = vtkXMLPolyDataWriter()
        writer.SetFileName(str(vtp))
        writer.SetInputData(pd)
        writer.Write()
        src = OpenDataFile(str(vtp))
        disp = Show(src, view)
        disp.Representation = "Surface With Edges"
        disp.EdgeColor = list(EDGES)
        disp.LineWidth = 1.0
        if values is not None:
            ColorBy(disp, ("CELLS", "val"))
            lut = GetColorTransferFunction("val")
            lut.ApplyPreset("Cool to Warm", True)
            lut.RescaleTransferFunction(-window, window)
            # THE MILLIMETRE SCALE RENDERS BESIDE EVERY COLOURED VIEW
            # (Sanaa 1100Z: "a field-coloured surface with no scale is the
            # one thing left that could read as decoration"). The bar was
            # explicitly off; each coloured call now names its quantity and
            # the bar carries it.
            bar = GetScalarBar(lut, view)
            bar.Title = bar_title or "outward normal motion (mm)"
            bar.ComponentTitle = ""
            bar.TitleColor = [0.85, 0.88, 0.92]
            bar.LabelColor = [0.85, 0.88, 0.92]
            # BIGGER, per her 1620Z ("see ... the color bar big as well"):
            # the defaults drew a sliver nobody could read on a filmed
            # frame. Parked in the upper right corner because the fitted
            # wing runs on the lower-left-to-right diagonal in both eye
            # directions and the default mid-right slot sat ON the tip.
            # Sized and looked at, not assumed.
            bar.WindowLocation = "Upper Right Corner"
            bar.ScalarBarLength = 0.5
            bar.ScalarBarThickness = 40
            bar.TitleFontSize = 28
            bar.LabelFontSize = 24
            disp.SetScalarBarVisibility(view, True)
        else:
            disp.DiffuseColor = [0.30, 0.36, 0.42]
            disp.AmbientColor = [0.105, 0.126, 0.147]
        # BOTH CAMERAS ARE FITTED, NOT TUNED (Sanaa 1100Z on the close
        # frame's cropping, then 1620Z on the whole family: "the geometry
        # itself is small but we have a lot of empty space around it").
        # Hand-picked dollies and parallel scales went through five rounds
        # and each still left either a cropped edge or a small wing in a
        # big box; `fit_parallel` projects every vertex of this frame's own
        # surface and fills the frame by construction. The two passes keep
        # their two eye directions, so the walk and the close view stay
        # distinct conventions; margins leave room for the scalar bar.
        fit_parallel(view, cam, pts,
                     (-0.30, 0.85, 0.60) if close else (-0.9, 0.65, 0.55),
                     1.06 if close else 1.04)
        Render(view)
        png = out / f"{name}.png"
        SaveScreenshot(str(png), view, ImageResolution=RESOLUTION)
        ink = ink_fraction(png)
        if ink < MIN_INK:
            say(f"REFUSED: {png.name} reads ink {ink:.4f}")
            raise SystemExit(2)
        (out / f"{name}.json").write_text(_json.dumps({
            "image": png.name, "caption": caption or WALL_CAPTION,
            "wall_faces": EXPECT_WALL_FACES,
            "wall_points": EXPECT_WALL_POINTS,
            "colour_window": None if values is None else [-window, window],
            "source_shape_history": str(SHAPE_FRAMES),
            "source_patch": str(case / "constant" / "polyMesh"),
            "data_provenance": (
                "the solver's own wall patch, quad by quad off its face "
                "list; frame vertices are the stored shape history's, "
                "displacements applied by index; per-face cell scalars, "
                "flat by construction; no triangle anywhere"),
            "script": me.name, "script_sha256": sha,
            "paraview": "5.13.3 EGL (/opt/paraview/bin/pvbatch)",
            "resolution": list(RESOLUTION), "theme": "dark",
            "ink_fraction": ink, "generated_utc": stamp,
        }, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        say(f"wing/{png.name}: ink {ink:.3f}")
        Delete(src)

    # Bar titles name each frame's own coloured quantity (Sanaa 1100Z): the
    # gradient frame's colour is millimetres of skin motion PER UNIT STEP,
    # the walk frames' colour is the outward normal motion in millimetres.
    # The inboard zoom's caption names the quantity too, because that view
    # is all warm tones and a viewer cannot infer it from contrast (her
    # words); the sentence is her wall-patch caption plus the colour clause.
    NEAR_CAPTION = WALL_CAPTION + " Colour: outward normal motion, mm."
    one("wing_baseline", points, None, 0.0, False)
    one("wing_gradient", points, grad["values_mm_per_step"], gmax, False,
        bar_title="descent direction (mm per unit step)")
    for it in FRAME_ITERS:
        f = frames[it]
        pts = [[b[0] + d[0], b[1] + d[1], b[2] + d[2]]
               for b, d in zip(points, f["disp"])]
        one(f"wing_iter_{it:02d}", pts, f["disp_n_mm"], dmax, False,
            bar_title="outward normal motion (mm)")
        one(f"wing_near_{it:02d}", pts, f["disp_n_mm"], dmax, True,
            bar_title="outward normal motion (mm)", caption=NEAR_CAPTION)
    shutil.rmtree(tmp, ignore_errors=True)
    say(f"PASS: {2 + 2 * len(FRAME_ITERS)} wall-patch frames rendered")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--expect-cells", type=int, required=True)
    ap.add_argument("--wing-frames", action="store_true",
                    help="render the face-by-face wall-patch wing views "
                         "(baseline, gradient, shown iterations) instead of "
                         "the grid panels")
    args = ap.parse_args()
    if args.wing_frames:
        return render_wing_frames(Path(args.case).resolve())
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

    def save(panel: str, view, caption: str = "") -> None:
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
            "caption": caption,
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

    # -- geometry: the body itself, shaded, no grid and no tessellation -----
    # Sanaa 2026-09-02 ~04:55Z: "make sure ALL runs show the paraview no
    # tesselation pls". With this panel on disk and declared, the sequencer's
    # geometry beat serves it and the page's client-side triangle canvas
    # never runs for this act (demo_sequencer.run: panel first, canvas only
    # where there is no panel).
    # Lifted well above the palette's domain tone: at (0.105, 0.125, 0.145)
    # the first render read as a silhouette on the dark ground (looked at,
    # not assumed), and a geometry beat whose body cannot be seen is the
    # blank-panel failure with better ink numbers.
    # HER WING-VIEW SPEC APPLIES TO THE GEOMETRY BEAT TOO (2026-09-02
    # ~05:40Z): the wall patch face by face, true edges, flat per-face
    # colour. The smooth-shaded body this replaced is recorded in this
    # file's history.
    wall_faces = wing.GetDataInformation().GetNumberOfCells()
    if wall_faces != 1008:
        say(f"REFUSED: the wall patch reads {wall_faces} faces; the caption "
            f"says 1,008")
        return 2
    DOMAIN = (0.30, 0.36, 0.42)
    disp = Show(wing, view)
    disp.Representation = "Surface With Edges"
    disp.DiffuseColor = list(DOMAIN)
    disp.AmbientColor = [c * 0.35 for c in DOMAIN]
    disp.EdgeColor = list(EDGES)
    disp.LineWidth = 1.0
    disp.Interpolation = "Flat"
    # FITTED, NOT DOLLIED (Sanaa 1620Z: the geometry fills the frame; see
    # `fit_parallel`). A first cut fitted the bbox CORNERS and the wing
    # still sat small in the frame: the tapered wing is a thin diagonal in
    # its own box, so corners the surface never reaches inflated the
    # footprint (rendered and looked at, which is how the shortcut was
    # caught). The vertex set used is the stored shape history's baseline
    # wall points, which `_patch_quads` proves map one to one onto this
    # very patch at 1e-4 m.
    import json as _json
    _pts = _json.loads(SHAPE_FRAMES.read_text())["base_vertices"]
    fit_parallel(view, cam, _pts, (-0.9, 0.65, 0.55), 1.04)
    Render(view)
    save("geometry", view, caption=WALL_CAPTION)
    Hide(wing, view)

    # -- mesh: the wing's skin as the volume grid holds it ------------------
    # Same fitted three-quarter eye as the geometry panel (Sanaa 1620Z).
    disp = Show(wing, view)
    style(disp)
    fit_parallel(view, cam, _pts, (-0.9, 0.65, 0.55), 1.04)
    Render(view)
    save("mesh", view, caption=WALL_CAPTION)
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
