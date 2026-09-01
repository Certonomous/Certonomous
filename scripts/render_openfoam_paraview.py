"""Publication-quality ParaView renders of a solved 2-D extruded OpenFOAM case.

WHY THIS EXISTS.  Sanaa's directive of 2026-09-01 (~21:10Z, recorded verbatim in
``etc/sessions/2026-09-01T2110Z_sanaa_paraview_everywhere.md``) retires the
in-browser canvas as a VISUAL SOURCE for act content: "Going forward all acts use
paraview.  Never that trashy canvas you were using before."  Every geometry, mesh
and field picture an act shows is therefore rendered by ParaView from the real
case files on disk.

WHAT IS POLISH AND WHAT IS NOT.  Polish is camera, framing, colormap, line weight,
background and time selection.  Polish is NEVER the data.  Nothing here smooths,
decimates, synthesises or substitutes geometry: every panel is drawn from the
case's own ``constant/polyMesh`` and its own time directories.  The one filter
that changes topology is a ``Slice`` at the mid-span plane of the extrusion, which
is how a 2-D extruded mesh is correctly viewed down its extrusion axis -- and its
polygon count is asserted equal to the mesh's cell count (see ``--expect-cells``),
so a slice that silently triangulated or dropped cells stops the render.

THE MIXED-GRID TRAP THIS GUARDS.  The JF1 campaign has two grids -- a 39,984-cell
O-mesh and a 46,180-cell C-mesh -- on reference areas differing by a factor of
100.  A picture of one beside a number from the other misreports lift by 100x.
``--expect-cells`` makes that a refusal rather than a caption error, and every
render drops a sidecar JSON carrying the case path and the cell count it actually
read, so whatever displays the image can assert the count on screen is the count
in the picture.

RULE 3 (planted-zero control).  A renderer that sees nothing produces a uniform
background, and a uniform background is a zero.  Every panel is read back off disk
and its ink fraction measured; a panel below ``--min-ink`` is REFUSED (exit 2)
rather than shipped.  ``--selftest`` proves that checker can see both outcomes: it
renders one framed panel (must read non-blank) and one panel with the camera
parked in empty space outside the domain (must read blank), and exits 2 if either
verdict fails to appear.

HOW TO RUN.  Under the distro ParaView 5.11.2 at /usr/bin/pvbatch, with a virtual
framebuffer -- the official 5.13.2 osmesa tarball segfaults at Render on this box:

    xvfb-run -a pvbatch scripts/render_openfoam_paraview.py --case <case> --out <dir>

``scripts/render_jf1_paraview.sh`` is the JF1 jet-flap invocation, with the case,
the cell-count guard and the output directory already filled in.
"""

import argparse
import datetime
import hashlib
import json
import math
import os
import re
import sys

from paraview.simple import (
    ColorBy,
    CreateRenderView,
    GetColorTransferFunction,
    GetScalarBar,
    Hide,
    Line,
    OpenFOAMReader,
    SaveScreenshot,
    Show,
    Slice,
    Text,
    Tube,
)

# --------------------------------------------------------------------------
# Palette.  The control room is a dark surface (``--bg: #060708`` in
# sdk/chief_engineer/control_room.html), so a render dropped into its viewport
# must sit on the same ground or it reads as a pasted-in white rectangle.  The
# light theme is kept for print.
# --------------------------------------------------------------------------
THEMES = {
    "dark": {
        "background": (0.024, 0.027, 0.031),   # #060708, the viewport ground
        "fluid": (0.043, 0.055, 0.066),        # mesh panels: dark, so edges carry
        "domain": (0.105, 0.125, 0.145),       # geometry panel: lifted, so the
                                               # airfoil hole reads as a body
        "edges": (0.400, 0.510, 0.600),        # cell edges: legible, not shouting
        "body": (0.870, 0.900, 0.930),         # the wall outline
        "slot": (0.949, 0.416, 0.361),         # #f26a5c, the control room's accent
        "text": (0.850, 0.880, 0.910),
    },
    "light": {
        "background": (1.0, 1.0, 1.0),
        "fluid": (0.945, 0.955, 0.965),
        "domain": (0.878, 0.898, 0.918),
        "edges": (0.250, 0.310, 0.370),
        "body": (0.070, 0.090, 0.110),
        "slot": (0.780, 0.180, 0.130),
        "text": (0.100, 0.120, 0.140),
    },
}

#: Panels this script knows how to draw, in the order ``--panels all`` draws them.
ALL_PANELS = ("geometry", "mesh", "mesh_zoom", "field_u", "field_p")

#: Colormaps.  Sequential magnitudes get a perceptually uniform, colour-vision-
#: deficiency-safe map; a signed field gets a diverging map rendered symmetric
#: about zero, so the sign of the pressure is read from the hue and not guessed.
PRESET_SEQUENTIAL = "Viridis (matplotlib)"
PRESET_DIVERGING = "Cool to Warm (Extended)"


# ==========================================================================
# Image readback -- the planted-zero control
# ==========================================================================

def say(line):
    """Report a line straight to fd 1.

    pvbatch installs its own capture over ``sys.stdout`` which is only drained
    at a normal interpreter exit -- and this script deliberately does not have
    one (see the ``__main__`` block). Measured: with ``print`` the entire report
    vanished when stdout was a file, while the images were written correctly. An
    unbuffered write is what makes the run readable by whoever ran it.
    """
    os.write(1, (line + "\n").encode())


def ink_fraction(path, background):
    """Fraction of pixels in ``path`` that differ visibly from ``background``.

    This is the whole zero control.  It reads the PNG BACK OFF DISK rather than
    trusting the render call's return, because the failure being guarded against
    -- a pipeline that builds and a GL layer that draws nothing -- returns
    success and writes a perfectly valid uniform image.
    """
    from vtkmodules.vtkIOImage import vtkPNGReader
    from paraview.vtk.util.numpy_support import vtk_to_numpy

    reader = vtkPNGReader()
    reader.SetFileName(path)
    reader.Update()
    image = reader.GetOutput()
    if image is None or image.GetNumberOfPoints() == 0:
        raise RuntimeError("could not read back the PNG just written: %s" % path)
    pixels = vtk_to_numpy(image.GetPointData().GetScalars())
    if pixels.ndim == 1:
        pixels = pixels.reshape(-1, 1)
    rgb = pixels[:, :3].astype("int16")
    bg = [int(round(c * 255.0)) for c in background]
    deviation = abs(rgb - bg).max(axis=1)
    return float((deviation > 8).mean())


def assert_not_blank(path, background, min_ink, label):
    frac = ink_fraction(path, background)
    if frac < min_ink:
        sys.stderr.write(
            "REFUSED: panel %r rendered blank -- ink fraction %.6f is below the "
            "floor %.6f. The pipeline may have built and drawn nothing; the image "
            "at %s is not evidence of an empty case.\n" % (label, frac, min_ink, path))
        raise SystemExit(2)
    return frac


# ==========================================================================
# Camera
# ==========================================================================

def frame(view, xlo, xhi, ylo, yhi, resolution):
    """Park the camera down the extrusion axis over the given world rectangle.

    A 2-D extruded section viewed with the default camera is a slab seen
    corner-on, which is the picture this script exists to replace.  Parallel
    projection down -Z with +Y up is the only honest view of such a mesh: no
    perspective foreshortening, so a cell that measures twice another on screen
    is twice its size.
    """
    cx, cy = 0.5 * (xlo + xhi), 0.5 * (ylo + yhi)
    half_x, half_y = 0.5 * (xhi - xlo), 0.5 * (yhi - ylo)
    width, height = resolution
    # CameraParallelScale is the HALF-HEIGHT of the view; widen it if the
    # requested x-range would otherwise be cropped by the aspect ratio.
    view.CameraParallelProjection = 1
    view.CameraParallelScale = max(half_y, half_x * float(height) / float(width))
    view.CameraPosition = [cx, cy, 10.0]
    view.CameraFocalPoint = [cx, cy, 0.0]
    view.CameraViewUp = [0.0, 1.0, 0.0]
    return {"centre": [cx, cy], "x_range": [xlo, xhi], "y_range": [ylo, yhi],
            "projection": "parallel", "view_up": [0, 1, 0],
            "parallel_scale": view.CameraParallelScale}


def domain_box(bounds, margin):
    """The world rectangle a DOMAIN-framed panel covers: the mesh's own bounds.

    WHY THIS EXISTS, AND IT IS A MEASURED DEFECT AND NOT A PREFERENCE.  The
    body-patch framing below this line is an AIRFOIL framing: it opens the
    camera by fractions of the CHORD (0.55 chord to the left, 0.85 to the
    right, 0.62 up and down), which is right when the body is small and the
    far field is large, and catastrophic when the "body" IS the domain's own
    floor.  Measured on the double-Mach-reflection channel, whose domain is
    4.000 x 1.000 m and whose wall patch runs x = 0.1667 .. 4.000 (chord
    3.833): the body framing produces a 8.050 x 4.217 m window, so the channel
    covers 49.7% of the frame width, 23.7% of its height and 11.8% of its
    area.  That is a coin in an empty panel, and no ink-fraction check can see
    it -- 11.8% of a frame is a great deal of ink.

    So a case whose subject is the DOMAIN frames on the domain: the mesh's own
    x-y bounds, plus one small uniform margin so the boundary line weight is
    not clipped by the edge of the image.  The margin is a fraction of the
    LONGER side, so a 4:1 channel is not padded four times harder vertically
    than horizontally.
    """
    xlo, xhi, ylo, yhi = bounds[0], bounds[1], bounds[2], bounds[3]
    pad = margin * max(xhi - xlo, yhi - ylo)
    return (xlo - pad, xhi + pad, ylo - pad, yhi + pad)


def fit_resolution(box, width):
    """An image whose ASPECT is the framed rectangle's, so no pixel is wasted.

    ``frame`` never crops -- it widens the parallel scale when the requested
    x-range would not fit the viewport's aspect -- so a 4:1 channel asked for
    in a 16:9 image is drawn correctly and surrounded by dark bands that are
    part of the file.  Those bands are not wrong, but they are dead pixels: they
    dilute the ink fraction and they are what a viewer reads as "empty panel".
    Sizing the image to the rectangle removes them at the source; the display
    letterboxes with ``object-fit: contain`` and the on-screen size is
    unchanged, so this costs the viewer nothing and costs the file nothing.
    """
    xlo, xhi, ylo, yhi = box
    span_x, span_y = xhi - xlo, yhi - ylo
    if span_x <= 0 or span_y <= 0:
        raise SystemExit("REFUSED: the framing rectangle has no extent.")
    height = int(round(width * span_y / span_x))
    height += height % 2                       # even, for any downstream encoder
    return [int(width), max(2, height)]


# ==========================================================================
# The initial-condition discontinuity, READ FROM THE CASE
# ==========================================================================

#: Everything the initial-condition expression is allowed to contain once
#: ``pos().y()`` has become ``y``.  A reader that will evaluate a string out of
#: a case file is a reader that must be able to REFUSE one, so the character
#: set is a whitelist and anything outside it stops the render rather than
#: being evaluated.
_IC_SAFE = re.compile(r"^[0-9yeE+\-*/(). ]*(?:(?:sqrt|tan|cos|sin|pi)"
                      r"[0-9yeE+\-*/(). ]*)*$")

#: ``pos().x() <op> <expression in y>`` -- the form an OpenFOAM setExprFields
#: initial condition takes when it splits a domain along a line.  The capture
#: stops at the ``?`` of the ternary, which is where the condition ends.
_IC_CONDITION = re.compile(
    r"pos\(\)\.x\(\)\s*(<=|>=|<|>)\s*(.+?)\s*\)\s*\?")


def read_initial_line(dict_path, ylo, yhi):
    """The initial discontinuity as two endpoints, off the case's own dict.

    THE POSITION IS READ, NEVER TYPED.  The double-Mach-reflection shock sits
    at ``x = 1/6 + y/sqrt(3)`` and a renderer that hard-codes those numbers is
    a renderer that will keep drawing them after somebody moves the shock.  So
    the line comes out of ``system/setExprFieldsDict`` -- the same file the
    solver initialised from -- and the expression it was read from travels into
    the sidecar, so the drawing can be checked against its source without
    trusting this function.

    Returns ``(p_lo, p_hi, raw_expression)`` in the x-y plane, or raises.
    """
    with open(dict_path, "r") as handle:
        text = handle.read()
    hit = _IC_CONDITION.search(text)
    if hit is None:
        raise ValueError(
            "no 'pos().x() <op> <expression>' condition in %s -- this case does "
            "not declare an initial discontinuity this reader can draw"
            % dict_path)
    raw = hit.group(2).strip()
    expr = raw.replace("pos().y()", "y")
    if "pos()" in expr:
        raise ValueError(
            "the initial condition %r depends on a coordinate other than y; "
            "this reader draws a line in x = f(y) and nothing else" % raw)
    if not _IC_SAFE.match(expr):
        raise ValueError(
            "the initial condition %r contains something outside the arithmetic "
            "whitelist; it is refused rather than evaluated" % raw)
    namespace = {"__builtins__": {}, "sqrt": math.sqrt, "tan": math.tan,
                 "cos": math.cos, "sin": math.sin, "pi": math.pi}
    try:
        x_lo = float(eval(expr, namespace, {"y": float(ylo)}))    # noqa: S307
        x_hi = float(eval(expr, namespace, {"y": float(yhi)}))    # noqa: S307
    except Exception as exc:                                     # noqa: BLE001
        raise ValueError("the initial condition %r would not evaluate: %s"
                         % (raw, exc)) from None
    # The operator travels with the expression: "x 1/6 + y/sqrt(3)" is not a
    # condition, and a sidecar that records one cannot be checked against the
    # dict it came from.
    return (x_lo, float(ylo)), (x_hi, float(yhi)), "%s %s" % (hit.group(1), raw)


# ==========================================================================
# Pipeline pieces
# ==========================================================================

def midspan_slice(source, z):
    """The 2-D section of an extruded mesh, one polygon per cell.

    ``Triangulatetheslice`` is off on purpose: a triangulated slice doubles the
    polygon count and the caller's assertion that polygons == cells -- the check
    that the picture is the solved grid -- would no longer hold.
    """
    sl = Slice(Input=source)
    sl.SliceType = "Plane"
    sl.SliceType.Origin = [0.0, 0.0, z]
    sl.SliceType.Normal = [0.0, 0.0, 1.0]
    sl.Triangulatetheslice = 0
    return sl


def patch_names(reader):
    """The reader's boundary patches, whatever this build calls the property.

    The list of selectable mesh regions is ``MeshRegions.Available`` in some
    ParaView builds and ``PatchArrays.Available`` in others.  Guessing one and
    letting the other raise would make the domain drawing a version-specific
    feature; asking both and refusing only when NEITHER answers keeps the
    failure honest and loud.
    """
    for attribute in ("MeshRegions", "PatchArrays"):
        holder = getattr(reader, attribute, None)
        available = getattr(holder, "Available", None) if holder is not None else None
        if available:
            found = [p for p in available if str(p).startswith("patch/")]
            if found:
                return found
    raise SystemExit(
        "REFUSED: this ParaView build exposes no boundary-patch list on the "
        "OpenFOAM reader, so the domain outline cannot be drawn from the case.")


def outline_of(patch, z, radius):
    """The wall profile as a drawable curve of a chosen line weight.

    The wall patch of a 2-D extruded case is a ribbon standing normal to the
    screen; viewed exactly down the extrusion axis it is degenerate and renders
    as nothing.  Slicing it at mid-span recovers the real profile curve, and
    tubing that curve gives it a line weight.  The radius is line weight -- it
    is drawn from the case's own points and moves no vertex.
    """
    sl = midspan_slice(patch, z)
    tube = Tube(Input=sl)
    tube.Radius = radius
    tube.NumberofSides = 12
    return tube


def flat(display):
    """Unshaded surface colour.

    Diffuse lighting on a flat 2-D slice darkens the surface away from the light,
    so a pixel's colour would no longer be the colour the scalar bar assigns to
    its value.  For a field panel that is not a style choice, it is a false
    colourbar; ambient-only keeps the mapping truthful.
    """
    display.Ambient = 1.0
    display.Diffuse = 0.0
    display.Specular = 0.0


def solid(display, colour):
    """Paint a source one flat colour, with no scalar mapping at all.

    ``ColorArrayName = [None, ""]`` is how a representation is detached from
    every array; leaving an array bound would colour the wall outline by
    whatever field happened to be active.
    """
    display.ColorArrayName = [None, ""]
    display.AmbientColor = list(colour)
    display.DiffuseColor = list(colour)
    flat(display)


def clear_view(ctx, displays):
    """Return the view to empty between panels.

    Both halves matter: a scalar bar left standing would appear over the next
    panel and label it with the previous panel's field, and a source left shown
    would put the previous framing's geometry into the next image.
    """
    view = ctx["view"]
    for disp in displays:
        # Only a display actually bound to an array owns a scalar bar; asking a
        # solid-coloured one to hide its bar makes ParaView hunt for a lookup
        # table that was never created and warn about not finding it.
        # A text representation has no ColorArrayName at all, and asking one for
        # it raises rather than returning empty -- so the guard tests for the
        # property, not just for its value.
        array_name = getattr(disp, "ColorArrayName", None)
        if array_name is not None and list(array_name)[0]:
            disp.SetScalarBarVisibility(view, False)
    for key in ("slice_internal", "outline_body", "outline_zoom",
                "initial_line"):
        source = ctx.get(key)
        if source is not None:
            Hide(source, view)
    # The domain drawing's boundary lines and its text are per-panel sources of
    # their own; a boundary line left shown would put the geometry stage's
    # bright wall over a field panel that never asked for one.
    for source, _colour, _weight in ctx.get("domain_edges", ()):
        Hide(source, view)
    for source in ctx.get("annotations", ()):
        Hide(source, view)


def set_if(proxy, name, value):
    """Set a proxy property when this ParaView build has it.

    The scalar bar's backdrop properties moved between ParaView versions; a
    missing one must not take the render down, because the picture is still
    correct without it.
    """
    if not hasattr(proxy, name):
        return False
    try:
        setattr(proxy, name, value)
    except RuntimeError:
        # Some colour properties are RGB in one ParaView and RGBA in the next;
        # 5.11 wants four values for the scalar bar's backdrop. Retry with an
        # alpha rather than losing the backdrop over a property shape.
        if isinstance(value, list) and len(value) == 3:
            proxy_value = list(value) + [1.0]
            try:
                setattr(proxy, name, proxy_value)
                return True
            except RuntimeError:
                return False
        return False
    return True


def style_scalar_bar(bar, title, units, theme):
    """A scalar bar that stays readable over whatever field is behind it.

    THE BACKDROP IS NOT DECORATION.  Measured on the pressure panel: a diverging
    map is near-white at its midpoint, and light text laid straight onto it was
    barely legible -- a scalar bar whose numbers cannot be read is a field plot
    with no units on screen at all.  The bar is drawn on its own opaque ground so
    its legibility does not depend on the values underneath it.

    Horizontal, because a vertical bar puts its title on its side, and a title
    the viewer has to tilt their head to read is not a caption.
    """
    bar.Title = title
    bar.ComponentTitle = units
    bar.TitleColor = list(theme["text"])
    bar.LabelColor = list(theme["text"])
    bar.TitleFontSize = 20
    bar.LabelFontSize = 16
    bar.ScalarBarLength = 0.30
    bar.ScalarBarThickness = 16
    bar.Orientation = "Horizontal"
    bar.WindowLocation = "Lower Right Corner"
    bar.AutomaticLabelFormat = 0
    bar.LabelFormat = "%-#.3g"
    bar.RangeLabelFormat = "%-#.3g"
    set_if(bar, "DrawBackground", 1)
    set_if(bar, "BackgroundColor", list(theme["background"]) + [0.82])
    set_if(bar, "BackgroundPadding", 8)


# ==========================================================================
# Panels
# ==========================================================================

def draw_geometry(ctx):
    """The solved section: the fluid domain, the wall profile, the slot.

    The airfoil is a HOLE in this O-mesh -- no solid body is meshed -- so the
    section is drawn as the fluid it actually is, with the wall profile laid over
    it and the blowing slot picked out in the accent colour.  Nothing is filled
    in where the case has no cells.
    """
    view, theme, geom = ctx["view"], ctx["theme"], ctx["geometry"]
    fluid = Show(ctx["slice_internal"], view)
    fluid.Representation = "Surface"
    # The lifted fill is what makes this read as a section: the airfoil is a HOLE
    # in this O-mesh -- no solid body is meshed -- so the profile is visible only
    # as the unfilled shape the fluid leaves behind, and that needs the fluid to
    # be plainly lighter than the ground behind it.
    solid(fluid, theme["domain"])
    shown = [fluid]
    for key, colour in (("body", theme["body"]), ("zoom", theme["slot"])):
        src = ctx.get("outline_" + key)
        if src is None:
            continue
        disp = Show(src, view)
        disp.Representation = "Surface"
        solid(disp, colour)
        shown.append(disp)
    chord = geom["chord"]
    cam = frame(view,
                geom["xlo"] - 0.10 * chord, geom["xhi"] + 0.14 * chord,
                geom["ymid"] - 0.26 * chord, geom["ymid"] + 0.26 * chord,
                ctx["resolution"])
    return shown, cam, {"field": None}


def draw_domain(ctx):
    """The STL-LESS geometry stage: the domain itself, drawn from the case.

    WHAT THIS REPLACES.  ``draw_geometry`` above is a BODY drawing: it exists
    for a case whose subject is an object immersed in a large far field, and it
    frames on that object.  A channel case has no such object -- the double-Mach
    reflection is a box with a wall along part of its floor and a shock line
    across it -- and asking the act for a body produced a served surface that is
    not the case's geometry at all.  Sanaa, 2026-09-01: "The geometry stage for
    STL-less cases must draw the domain: channel outline, wall segment, initial
    shock position."

    So this draws exactly those three things and each of them comes off disk:

      * the DOMAIN, as the mid-span section of the case's own ``polyMesh`` --
        which is the channel outline, filled, with whatever real shape it has;
      * every BOUNDARY patch as a line, with the patches named on the command
        line drawn bright and thick: the wall segment, marked;
      * the INITIAL DISCONTINUITY, read out of the case's own
        ``setExprFieldsDict`` by :func:`read_initial_line` and drawn in the
        accent colour.

    Nothing here is synthesised and nothing is typed.  A case with no initial
    discontinuity gets the first two and its sidecar says so.
    """
    view, theme = ctx["view"], ctx["theme"]
    fluid = Show(ctx["slice_internal"], view)
    fluid.Representation = "Surface"
    solid(fluid, theme["domain"])
    shown = [fluid]

    for source, colour, weight in ctx["domain_edges"]:
        disp = Show(source, view)
        disp.Representation = "Surface"
        solid(disp, colour)
        shown.append(disp)

    meta = {"field": None,
            "domain_extent": [ctx["domain_span"][0], ctx["domain_span"][1]],
            "marked_patches": ctx["marked_patches"],
            "boundary_patches": ctx["boundary_patches"]}
    if ctx.get("initial_line") is not None:
        line = Show(ctx["initial_line"], view)
        line.Representation = "Surface"
        solid(line, theme["slot"])
        shown.append(line)
        meta["initial_condition"] = ctx["initial_meta"]

    # The key lines, stacked down from inside the top-left of the frame. Placed
    # by explicit position rather than by a named window corner, because two
    # labels sent to the same corner draw on top of each other and the second
    # one is invisible in a way no return code reports.
    #
    # THE TYPE IS SIZED FOR THE STAGE, NOT FOR THE FILE. A domain-fitted panel
    # is short -- this channel renders 2560 x 714 -- and it is displayed
    # `object-fit: contain` inside a viewport about half its pixel width, so a
    # 15 pt label measured 7 px on screen and could not be read. It is set as a
    # fraction of the image HEIGHT so a taller domain does not get giant type.
    colours = ctx.get("annotation_colours", ())
    height = ctx["resolution"][1]
    size = max(14, int(round(0.045 * height)))
    step = 1.75 * size / float(height)
    # THE KEY IS PLACED WHERE IT CANNOT OVERDRAW THE THING IT DESCRIBES, and
    # the place is computed, not chosen: the initial-condition line is the only
    # feature crossing the domain's interior, so the key starts to the right of
    # its rightmost point. Left at the frame edge it ran straight through the
    # shock line at the top of this channel.
    anchor = 0.016
    if ctx.get("initial_meta"):
        xlo, xhi = ctx["wide_box"][0], ctx["wide_box"][1]
        far = max(p[0] for p in ctx["initial_meta"]["endpoints"])
        anchor = min(0.55, max(anchor, (far - xlo) / (xhi - xlo) + 0.018))
    for index, label in enumerate(ctx.get("annotations", ())):
        disp = Show(label, view)
        disp.Color = list(colours[index] if index < len(colours) else theme["text"])
        set_if(disp, "FontSize", size)
        set_if(disp, "WindowLocation", "Any Location")
        # The first line starts nearly two full line-heights BELOW the top edge,
        # so no label is cropped by, or laid over, the boundary it describes.
        set_if(disp, "Position", [anchor, 1.0 - step * (index + 1.9)])
        shown.append(disp)

    cam = frame(view, *ctx["wide_box"], ctx["resolution"])
    return shown, cam, meta


def draw_mesh(ctx, zoom=False):
    """The real polyMesh, cell by cell, as surface-with-edges.

    The polygons drawn here are the case's own cells: the slice's polygon count
    is asserted equal to the mesh's cell count before anything is written.
    """
    view, theme, geom = ctx["view"], ctx["theme"], ctx["geometry"]
    cells = Show(ctx["slice_internal"], view)
    cells.Representation = "Surface With Edges"
    solid(cells, theme["fluid"])
    cells.EdgeColor = list(theme["edges"])
    cells.LineWidth = 1.6 if zoom else 1.0
    shown = [cells]
    if ctx["frame_mode"] == "domain":
        # THE WALL IS MARKED ON THE GRID TOO. Sanaa asked for the grid picture
        # to show "cell edges visible, the wall marked", and a wall that is a
        # boundary of the mesh is otherwise indistinguishable from the three
        # boundaries that are not it.
        # LINE WEIGHT IS SET BY THE FRAME, NOT BY THE DOMAIN. The wall drawn at
        # the domain's weight is 3.4% of this channel's height in the wide panel
        # and 13% of the zoom's height in the close one -- at which point it
        # swallows the two rows of cells the zoom exists to show. Each frame
        # therefore gets its own outline of the same patches; nothing about the
        # patch moves, only how thickly it is stroked.
        edges = ctx["zoom_marked_edges"] if zoom else ctx["marked_edges"]
        for source, colour, _ in edges:
            disp = Show(source, view)
            disp.Representation = "Surface"
            solid(disp, colour)
            shown.append(disp)
        box = ctx["zoom_box"] if zoom else ctx["wide_box"]
        if box is None:
            raise SystemExit(
                "REFUSED: the zoom panel was asked for in domain framing with "
                "no --zoom-box; a zoom frame guessed from a chord is the defect "
                "this mode exists to remove.")
        return shown, frame(view, *box, ctx["resolution"]), {"field": None}
    if ctx.get("outline_zoom") is not None:
        slot = Show(ctx["outline_zoom"], view)
        slot.Representation = "Surface"
        solid(slot, theme["slot"])
        shown.append(slot)
    chord = geom["chord"]
    if zoom:
        # The wall-layer and slot zoom: centred on the blowing slot when the case
        # names one, otherwise on the trailing edge.
        zc = ctx.get("zoom_centre") or [geom["xhi"], geom["ymid"]]
        half = ctx["zoom_half_width"] * chord
        cam = frame(view, zc[0] - 1.55 * half, zc[0] + 0.45 * half,
                    zc[1] - half, zc[1] + half, ctx["resolution"])
    else:
        cam = frame(view,
                    geom["xlo"] - 0.55 * chord, geom["xhi"] + 0.85 * chord,
                    geom["ymid"] - 0.62 * chord, geom["ymid"] + 0.62 * chord,
                    ctx["resolution"])
    return shown, cam, {"field": None}


def draw_field(ctx, array, component, title, units, preset, symmetric):
    """A solved field on the mid-span plane, at one explicitly chosen time."""
    view, theme, geom = ctx["view"], ctx["theme"], ctx["geometry"]
    disp = Show(ctx["slice_internal"], view)
    disp.Representation = "Surface"
    flat(disp)
    ColorBy(disp, ("POINTS", array, component))
    lut = GetColorTransferFunction(array)
    lut.ApplyPreset(preset, True)

    override = ctx.get("field_range")
    if override is not None:
        lo, hi = override
    else:
        # Read the range off the pipeline AT THE CHOSEN TIME. Asking the proxy
        # for its arrays without this re-update returns whatever time the view
        # last drew, which is how a panel ends up scaled to one time and
        # captioned with another.
        source = ctx["slice_internal"]
        source.UpdatePipeline(ctx["time"])
        info = source.GetPointDataInformation().GetArray(array)
        if info is None:
            raise SystemExit(
                "REFUSED: the case has no point array %r at time %g -- this panel "
                "cannot be drawn from this run." % (array, ctx["time"]))
        lo, hi = info.GetRange(-1 if component == "Magnitude" else 0)
        if symmetric:
            extent = max(abs(lo), abs(hi))
            lo, hi = -extent, extent
    lut.RescaleTransferFunction(lo, hi)

    disp.SetScalarBarVisibility(view, True)
    style_scalar_bar(GetScalarBar(lut, view), title, units, theme)

    shown = [disp]
    for key, colour in (("body", theme["body"]), ("zoom", theme["slot"])):
        src = ctx.get("outline_" + key)
        if src is None:
            continue
        over = Show(src, view)
        over.Representation = "Surface"
        solid(over, colour)
        shown.append(over)

    if ctx["frame_mode"] == "domain":
        cam = frame(view, *ctx["wide_box"], ctx["resolution"])
    else:
        chord = geom["chord"]
        cam = frame(view,
                    geom["xlo"] - 0.55 * chord, geom["xhi"] + 0.85 * chord,
                    geom["ymid"] - 0.62 * chord, geom["ymid"] + 0.62 * chord,
                    ctx["resolution"])
    meta = {"field": array, "component": component,
            "range": [float(lo), float(hi)], "colormap": preset,
            "range_basis": ("operator override" if override is not None
                            else ("symmetric about zero over the data range"
                                  if symmetric else "full data range at this time")),
            "lighting": "ambient only -- pixel colour is the scalar bar's colour"}
    return shown, cam, meta


PANEL_DRAW = {
    # THE GEOMETRY STAGE BRANCHES ON WHAT THE CASE ACTUALLY IS, and the branch
    # is taken from an explicit command-line mode rather than sniffed, so a
    # case can never fall into the wrong drawing because a patch was named
    # something unexpected.
    "geometry": lambda ctx: (draw_domain(ctx) if ctx["geometry_mode"] == "domain"
                             else draw_geometry(ctx)),
    "mesh": lambda ctx: draw_mesh(ctx, zoom=False),
    "mesh_zoom": lambda ctx: draw_mesh(ctx, zoom=True),
    "field_u": lambda ctx: draw_field(
        ctx, "U", "Magnitude", "velocity magnitude", "m/s",
        PRESET_SEQUENTIAL, symmetric=False),
    "field_p": lambda ctx: draw_field(
        ctx, "p", "", "kinematic pressure  p/rho", "m2/s2",
        PRESET_DIVERGING, symmetric=True),
}


# ==========================================================================
# Driver
# ==========================================================================

def script_sha256():
    with open(os.path.abspath(__file__), "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def resolve_time(reader, requested):
    times = [float(t) for t in reader.TimestepValues]
    if not times:
        raise SystemExit("REFUSED: the reader found no time directories in this case.")
    if requested in (None, "latest"):
        return max(times), times
    value = float(requested)
    if value not in times:
        raise SystemExit(
            "REFUSED: time %g is not among the case's %d time directories "
            "(%g .. %g). The time is chosen explicitly, never defaulted silently."
            % (value, len(times), min(times), max(times)))
    return value, times


def main(argv):
    parser = argparse.ArgumentParser(
        description="Render a solved 2-D extruded OpenFOAM case with ParaView.")
    parser.add_argument("--case", required=True,
                        help="OpenFOAM case root (the directory holding constant/polyMesh).")
    parser.add_argument("--out", required=True, help="Directory to write PNGs and sidecars into.")
    parser.add_argument("--time", default="latest",
                        help="Time directory to render: a value, or 'latest' (default). "
                             "The resolved value is printed and recorded in every sidecar.")
    parser.add_argument("--panels", default="all",
                        help="Comma-separated subset of: %s" % ", ".join(ALL_PANELS))
    parser.add_argument("--body-patch", default="airfoil",
                        help="Wall patch whose bounds set the framing and whose profile is outlined. "
                             "Used by --frame body and --geometry-mode body only.")
    parser.add_argument("--frame", dest="frame_mode", default="body",
                        choices=("body", "domain"),
                        help="Where the camera comes from. 'body' opens by fractions of the body "
                             "patch's chord (an airfoil in a far field). 'domain' frames the mesh's "
                             "own bounds, which is the only correct framing when the domain IS the "
                             "subject -- a channel, a duct, a cavity.")
    parser.add_argument("--geometry-mode", default="body",
                        choices=("body", "domain"),
                        help="What the geometry panel draws. 'body' is the immersed-body section. "
                             "'domain' is the STL-less drawing: domain outline, marked wall patches "
                             "and the initial discontinuity read from the case.")
    parser.add_argument("--domain-margin", type=float, default=0.02,
                        help="Margin around the domain in --frame domain, as a fraction of the "
                             "domain's LONGER side (default 0.02).")
    parser.add_argument("--mark-patches", default=None,
                        help="Comma-separated boundary patches drawn bright and thick in the domain "
                             "drawing and over the domain-framed grid: the wall, marked.")
    parser.add_argument("--zoom-box", default=None,
                        help="Explicit world rectangle 'xlo,xhi,ylo,yhi' for the mesh_zoom panel "
                             "under --frame domain. Required for that panel in domain framing: a "
                             "zoom frame guessed from a chord is the defect this mode removes.")
    parser.add_argument("--initial-condition", default=None,
                        help="Path to the setExprFields-style dict the initial discontinuity is READ "
                             "from (e.g. <case>/system/setExprFieldsDict). Never a typed position.")
    parser.add_argument("--annotate", action="append", default=None,
                        help="A short numeric/symbolic key line drawn on the domain panel. Repeatable. "
                             "Numbers, symbols and units only -- caption prose belongs to the act.")
    parser.add_argument("--zoom-patch", default=None,
                        help="Patch the zoom panel centres on (e.g. jetSlot). Optional.")
    parser.add_argument("--zoom-half-width", type=float, default=0.075,
                        help="Half-height of the zoom frame, in chords (default 0.075).")
    parser.add_argument("--outline-radius", type=float, default=0.0022,
                        help="Wall-outline line weight, in chords. Line weight only: no vertex moves.")
    parser.add_argument("--expect-cells", type=int, default=None,
                        help="REFUSE unless the mesh has exactly this many cells. Use it to make "
                             "a wrong-grid render impossible rather than merely mis-captioned.")
    parser.add_argument("--field-range", default=None,
                        help="Override the field panel range as 'lo,hi'. Recorded in the sidecar.")
    parser.add_argument("--resolution", default="1920x1080",
                        help="WIDTHxHEIGHT, or 'fit:<width>' under --frame domain to size the image "
                             "to the framed domain's own aspect so no dead pixels are baked in.")
    parser.add_argument("--theme", default="dark", choices=sorted(THEMES))
    parser.add_argument("--min-ink", type=float, default=0.002,
                        help="Minimum fraction of non-background pixels for a panel to be accepted.")
    parser.add_argument("--prefix", default=None,
                        help="Filename prefix (default: the case directory's own name).")
    parser.add_argument("--selftest", action="store_true",
                        help="Prove the blank-check can see both outcomes, then exit.")
    args = parser.parse_args(argv)

    case = os.path.abspath(args.case)
    if not os.path.isdir(os.path.join(case, "constant", "polyMesh")):
        raise SystemExit("REFUSED: %s has no constant/polyMesh -- not an OpenFOAM case root." % case)
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    prefix = args.prefix or os.path.basename(case)
    theme = THEMES[args.theme]
    # 'fit:<width>' needs the domain, which needs the reader; the explicit form
    # is resolved here and the fitted form after the bounds are known.
    fitted_width = None
    if args.resolution.lower().startswith("fit:"):
        if args.frame_mode != "domain":
            raise SystemExit(
                "REFUSED: --resolution fit:<width> sizes the image to the FRAMED "
                "DOMAIN and is only meaningful with --frame domain.")
        fitted_width = int(args.resolution.split(":", 1)[1])
        resolution = [fitted_width, fitted_width]     # replaced below
    else:
        width, height = (int(v) for v in args.resolution.lower().split("x"))
        resolution = [width, height]

    # The OpenFOAM reader is addressed through a marker file in the case root.
    # It is empty, it is the documented way to open a case, and it touches no
    # field -- the strict completion rule's age guard compares fields against
    # 0/T and is unaffected by a zero-byte marker.
    foam = os.path.join(case, "case.foam")
    if not os.path.exists(foam):
        open(foam, "w").close()

    reader = OpenFOAMReader(FileName=foam)
    reader.MeshRegions = ["internalMesh"]
    reader.UpdatePipelineInformation()
    time_value, times = resolve_time(reader, args.time)
    reader.UpdatePipeline(time_value)

    info = reader.GetDataInformation()
    n_cells = info.GetNumberOfCells()
    bounds = info.GetBounds()
    if args.expect_cells is not None and n_cells != args.expect_cells:
        raise SystemExit(
            "REFUSED: this mesh has %d cells; --expect-cells demanded %d. This is the "
            "wrong grid for the numbers this picture will be shown beside." %
            (n_cells, args.expect_cells))

    z_mid = 0.5 * (bounds[4] + bounds[5])

    # THE BODY PATCH IS ONLY LOADED BY THE MODES THAT USE IT. A channel case
    # need not have a body at all, and demanding one would make this script
    # refuse exactly the cases the domain mode was added for.
    needs_body = args.frame_mode == "body" or args.geometry_mode == "body"
    body = None
    if needs_body:
        body = OpenFOAMReader(FileName=foam)
        body.MeshRegions = ["patch/" + args.body_patch]
        body.UpdatePipeline(time_value)
        b = body.GetDataInformation().GetBounds()
        if b[0] > b[1]:
            raise SystemExit("REFUSED: body patch %r is empty." % args.body_patch)
        chord = b[1] - b[0]
        geometry = {"xlo": b[0], "xhi": b[1], "ylo": b[2], "yhi": b[3],
                    "ymid": 0.5 * (b[2] + b[3]), "chord": chord}
    else:
        chord = max(bounds[1] - bounds[0], bounds[3] - bounds[2])
        geometry = {"xlo": bounds[0], "xhi": bounds[1],
                    "ylo": bounds[2], "yhi": bounds[3],
                    "ymid": 0.5 * (bounds[2] + bounds[3]), "chord": chord}

    slice_internal = midspan_slice(reader, z_mid)
    slice_internal.UpdatePipeline(time_value)
    n_polys = slice_internal.GetDataInformation().GetNumberOfCells()
    if n_polys != n_cells:
        raise SystemExit(
            "REFUSED: the mid-span slice produced %d polygons for a %d-cell mesh. The "
            "picture would not be the solved grid." % (n_polys, n_cells))

    # ------------------------------------------------------------------
    # DOMAIN FRAMING. The camera rectangle is the mesh's own bounds, and the
    # image is sized to it, so the subject fills the file rather than sitting
    # in it. Both numbers land in the sidecar.
    # ------------------------------------------------------------------
    wide_box = zoom_box = None
    if args.frame_mode == "domain":
        wide_box = domain_box(bounds, args.domain_margin)
        if fitted_width is not None:
            resolution = fit_resolution(wide_box, fitted_width)
        if args.zoom_box:
            parts = [float(v) for v in args.zoom_box.split(",")]
            if len(parts) != 4 or parts[1] <= parts[0] or parts[3] <= parts[2]:
                raise SystemExit(
                    "REFUSED: --zoom-box must be 'xlo,xhi,ylo,yhi' with xhi > xlo "
                    "and yhi > ylo.")
            zoom_box = tuple(parts)
    elif fitted_width is not None:                     # pragma: no cover
        raise SystemExit("REFUSED: fitted resolution needs --frame domain.")

    view = CreateRenderView()
    view.ViewSize = resolution
    view.UseColorPaletteForBackground = 0
    view.BackgroundColorMode = "Single Color"
    view.Background = list(theme["background"])
    view.OrientationAxesVisibility = 0
    view.CameraParallelProjection = 1
    # THE VIEW'S OWN CLOCK, and it is separate from the reader's. A render view
    # draws at ViewTime, which starts at 0 and so resolves to the FIRST timestep,
    # not the requested one. Left unset, every field panel would show the first
    # written time while its sidecar and its caption said the last -- exactly the
    # silent default that --time exists to prevent.
    view.ViewTime = time_value

    ctx = {"view": view, "theme": theme, "geometry": geometry, "time": time_value,
           "resolution": resolution, "slice_internal": slice_internal,
           "outline_radius": args.outline_radius * chord,
           "zoom_half_width": args.zoom_half_width,
           "outline_body": (outline_of(body, z_mid, args.outline_radius * chord)
                            if body is not None else None),
           "outline_zoom": None, "zoom_centre": None, "field_range": None,
           "frame_mode": args.frame_mode, "geometry_mode": args.geometry_mode,
           "wide_box": wide_box, "zoom_box": zoom_box,
           "domain_edges": [], "marked_edges": [], "zoom_marked_edges": [],
           "annotations": [],
           "marked_patches": [], "boundary_patches": [],
           "initial_line": None, "initial_meta": None,
           "domain_span": [bounds[1] - bounds[0], bounds[3] - bounds[2]]}

    # ------------------------------------------------------------------
    # THE DOMAIN DRAWING'S OWN SOURCES. Every one of them is a patch of the
    # case's own mesh or a line read out of the case's own dict.
    # ------------------------------------------------------------------
    if args.geometry_mode == "domain" or (args.frame_mode == "domain"
                                          and args.mark_patches):
        marked = [p.strip() for p in (args.mark_patches or "").split(",") if p.strip()]
        names = [p.split("/", 1)[1] for p in patch_names(reader)]
        missing = [p for p in marked if p not in names]
        if missing:
            raise SystemExit(
                "REFUSED: --mark-patches names %s, which this mesh does not "
                "have. Its patches are: %s" % (", ".join(missing), ", ".join(names)))
        # Line weights in metres, off the DOMAIN's longer side, so the drawing
        # reads the same on a 4 m channel and a 0.1 m duct.
        scale = max(bounds[1] - bounds[0], bounds[3] - bounds[2])
        thin, thick = 0.0016 * scale, 0.0042 * scale
        for name in names:
            patch = OpenFOAMReader(FileName=foam)
            patch.MeshRegions = ["patch/" + name]
            patch.UpdatePipeline(time_value)
            pb = patch.GetDataInformation().GetBounds()
            if pb[0] > pb[1]:
                continue                 # an empty patch draws nothing, quietly
            is_marked = name in marked
            radius = thick if is_marked else thin
            colour = theme["body"] if is_marked else theme["edges"]
            ctx["domain_edges"].append((outline_of(patch, z_mid, radius),
                                        colour, radius))
            ctx["boundary_patches"].append(name)
            if is_marked:
                ctx["marked_edges"].append(ctx["domain_edges"][-1])
                ctx["marked_patches"].append(
                    {"patch": name, "x_range": [pb[0], pb[1]],
                     "y_range": [pb[2], pb[3]]})
                if zoom_box is not None:
                    zoom_radius = 0.010 * (zoom_box[3] - zoom_box[2])
                    ctx["zoom_marked_edges"].append(
                        (outline_of(patch, z_mid, zoom_radius), colour,
                         zoom_radius))
        if args.initial_condition:
            p_lo, p_hi, raw = read_initial_line(
                args.initial_condition, bounds[2], bounds[3])
            span = math.hypot(p_hi[0] - p_lo[0], p_hi[1] - p_lo[1])
            if span <= 0.0:
                raise SystemExit(
                    "REFUSED: the initial condition read from %s is a point, not "
                    "a line; nothing would be drawn and the panel would claim a "
                    "shock position it never showed." % args.initial_condition)
            seg = Line()
            seg.Point1 = [p_lo[0], p_lo[1], z_mid]
            seg.Point2 = [p_hi[0], p_hi[1], z_mid]
            seg.Resolution = 2
            shock = Tube(Input=seg)
            shock.Radius = thick
            shock.NumberofSides = 12
            shock.UpdatePipeline(time_value)
            ctx["initial_line"] = shock
            ctx["initial_meta"] = {
                "source": os.path.abspath(args.initial_condition),
                "expression": "x %s" % raw,
                "endpoints": [[p_lo[0], p_lo[1]], [p_hi[0], p_hi[1]]],
                "length": span,
                "read_not_typed": True}
        # THE KEY IS COLOURED TO MATCH THE THING IT NAMES, which is the whole
        # point of a key: "rampWall" written in the same white as the wall line
        # marks the wall, and the same words in the body text colour merely
        # mention it.
        for line in (args.annotate or ()):
            key, _, body_text = line.partition("|")
            if not body_text:
                key, body_text = "text", line
            if key not in theme:
                raise SystemExit(
                    "REFUSED: --annotate colour key %r is not one of %s"
                    % (key, ", ".join(sorted(theme))))
            label = Text(Text=body_text)
            label.UpdatePipeline()
            ctx["annotations"].append(label)
            ctx.setdefault("annotation_colours", []).append(theme[key])

    if args.field_range:
        lo, hi = (float(v) for v in args.field_range.split(","))
        ctx["field_range"] = (lo, hi)
    if args.zoom_patch:
        zoom_src = OpenFOAMReader(FileName=foam)
        zoom_src.MeshRegions = ["patch/" + args.zoom_patch]
        zoom_src.UpdatePipeline(time_value)
        zb = zoom_src.GetDataInformation().GetBounds()
        if zb[0] > zb[1]:
            raise SystemExit("REFUSED: zoom patch %r is empty." % args.zoom_patch)
        ctx["zoom_centre"] = [0.5 * (zb[0] + zb[1]), 0.5 * (zb[2] + zb[3])]
        ctx["outline_zoom"] = outline_of(zoom_src, z_mid, args.outline_radius * chord)

    provenance = {
        "case": case,
        "case_name": os.path.basename(case),
        "cells": int(n_cells),
        "slice_polygons": int(n_polys),
        "time": time_value,
        "times_available": len(times),
        "time_range": [min(times), max(times)],
        "body_patch": args.body_patch if needs_body else None,
        "zoom_patch": args.zoom_patch,
        "chord": chord,
        "domain_bounds": list(bounds),
        # THE FRAMING IS PART OF THE PROVENANCE. A picture whose camera came
        # from a body patch and a picture whose camera came from the mesh are
        # different pictures of one grid, and a reader checking "does this fill
        # the frame" needs to know which rule drew it.
        "frame_mode": args.frame_mode,
        "geometry_mode": args.geometry_mode,
        "frame_box": list(wide_box) if wide_box else None,
        "zoom_box": list(zoom_box) if zoom_box else None,
        "domain_margin": args.domain_margin if args.frame_mode == "domain" else None,
        "marked_patches": [m["patch"] for m in ctx["marked_patches"]],
        "initial_condition": ctx["initial_meta"],
        "theme": args.theme,
        "background_rgb": list(theme["background"]),
        "resolution": resolution,
        "paraview": "5.11.2 (/usr/bin/pvbatch, xvfb-run)",
        "script": "scripts/render_openfoam_paraview.py",
        "script_sha256": script_sha256(),
        "generated_utc": datetime.datetime.now(
            datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "data_provenance": "rendered from the case's own constant/polyMesh and "
                           "time directory; no synthesised, smoothed or decimated geometry",
    }

    if args.selftest:
        return selftest(ctx, out, prefix, theme, args.min_ink, resolution)

    names = ALL_PANELS if args.panels == "all" else tuple(
        p.strip() for p in args.panels.split(",") if p.strip())
    unknown = [p for p in names if p not in PANEL_DRAW]
    if unknown:
        raise SystemExit("REFUSED: unknown panel(s) %s" % ", ".join(unknown))

    say("case         %s" % case)
    say("cells        %d (slice polygons %d)" % (n_cells, n_polys))
    say("time         %g   (chosen explicitly from %d times, %g .. %g)"
        % (time_value, len(times), min(times), max(times)))

    written = []
    for name in names:
        shown, cam, meta = PANEL_DRAW[name](ctx)
        image = os.path.join(out, "%s_%s.png" % (prefix, name))
        SaveScreenshot(image, view, ImageResolution=resolution,
                       TransparentBackground=0)
        frac = assert_not_blank(image, theme["background"], args.min_ink, name)
        clear_view(ctx, shown)
        record = dict(provenance, panel=name, image=os.path.basename(image),
                      camera=cam, ink_fraction=frac, **meta)
        sidecar = image[:-4] + ".json"
        with open(sidecar, "w") as handle:
            json.dump(record, handle, indent=2, sort_keys=True)
            handle.write("\n")
        written.append((name, image, frac))
        say("panel %-10s ink %.4f  ->  %s" % (name, frac, image))

    manifest = os.path.join(out, "%s_render_manifest.json" % prefix)
    with open(manifest, "w") as handle:
        json.dump(dict(provenance, panels=[
            {"panel": n, "image": os.path.basename(i), "ink_fraction": f}
            for n, i, f in written]), handle, indent=2, sort_keys=True)
        handle.write("\n")
    say("wrote %d panel(s), %d sidecar(s) and the manifest into %s"
        % (len(written), len(written), out))
    return 0


#: The initial-condition control.  A KNOWN line goes in and its endpoints must
#: come back; a dict with no x-condition must be REFUSED.  Rule 3 in the form
#: this reader needs it: the shock position it reports is only evidence if it
#: has been shown able to read a shock position and to fail to read one.
_IC_PLANT = """expressions ( pInit { field p; expression #{
    (pos().x() < 0.25 + pos().y()/sqrt(3.0)) ? 116.5 : 1.0 #}; } );"""
_IC_PLANT_BLANK = """expressions ( pInit { field p; expression #{
    (pos().y() < 0.5) ? 116.5 : 1.0 #}; } );"""
#: 0.25 + 1/sqrt(3) at y = 1, to 10 decimal places.
_IC_PLANT_X_AT_1 = 0.25 + 1.0 / math.sqrt(3.0)


def initial_line_control(directory):
    """Prove the initial-condition reader can produce BOTH of its verdicts."""
    failures = []
    live = os.path.join(directory, "_ic_plant_live.dict")
    dead = os.path.join(directory, "_ic_plant_blank.dict")
    with open(live, "w") as handle:
        handle.write(_IC_PLANT)
    with open(dead, "w") as handle:
        handle.write(_IC_PLANT_BLANK)
    try:
        p_lo, p_hi, raw = read_initial_line(live, 0.0, 1.0)
    except ValueError as exc:
        failures.append("the initial-condition reader could not read a PLANTED "
                        "line it was handed (%s); no shock position it reports "
                        "is evidence" % exc)
    else:
        errors = (abs(p_lo[0] - 0.25), abs(p_hi[0] - _IC_PLANT_X_AT_1))
        say("selftest ic    planted x(0)=%.10f x(1)=%.10f  err %.2e / %.2e"
            % (p_lo[0], p_hi[0], errors[0], errors[1]))
        if max(errors) > 1e-12:
            failures.append(
                "the initial-condition reader returned x(0)=%.12f x(1)=%.12f "
                "for a line planted at 0.25 and %.12f" %
                (p_lo[0], p_hi[0], _IC_PLANT_X_AT_1))
        if "sqrt" not in raw:
            failures.append("the reader did not carry the planted expression "
                            "through to the sidecar: %r" % raw)
    try:
        read_initial_line(dead, 0.0, 1.0)
    except ValueError:
        say("selftest ic    a dict with no x-condition was REFUSED, as required.")
    else:
        failures.append("the initial-condition reader accepted a dict that "
                        "declares no discontinuity in x, so it would draw a "
                        "shock line for a case that has none")
    return failures


def selftest(ctx, out, prefix, theme, min_ink, resolution):
    """Plant a visible panel and a deliberately empty one; require both verdicts.

    A blank check that has never refused anything is not a check.  This renders
    the mesh panel framed on the body (which must read NON-BLANK) and the same
    pipeline with the camera parked far outside the domain (which must read
    BLANK), and fails if either verdict does not appear.
    """
    directory = os.path.join(out, "_selftest")
    os.makedirs(directory, exist_ok=True)
    view = ctx["view"]
    ic_failures = initial_line_control(directory)

    shown, _, _ = draw_mesh(ctx, zoom=False)
    live = os.path.join(directory, "%s_selftest_live.png" % prefix)
    SaveScreenshot(live, view, ImageResolution=resolution, TransparentBackground=0)
    live_ink = ink_fraction(live, theme["background"])

    geom = ctx["geometry"]
    far = 400.0 * geom["chord"]
    frame(view, far, far + geom["chord"], far, far + geom["chord"], resolution)
    blank = os.path.join(directory, "%s_selftest_blank.png" % prefix)
    SaveScreenshot(blank, view, ImageResolution=resolution, TransparentBackground=0)
    blank_ink = ink_fraction(blank, theme["background"])
    clear_view(ctx, shown)

    say("selftest live  ink %.6f  (must be >= %.6f)" % (live_ink, min_ink))
    say("selftest blank ink %.6f  (must be <  %.6f)" % (blank_ink, min_ink))
    failures = list(ic_failures)
    if live_ink < min_ink:
        failures.append("the framed panel read BLANK -- the checker cannot see a "
                        "non-empty case, so no zero it reports is evidence")
    if blank_ink >= min_ink:
        failures.append("the empty-space panel read NON-BLANK -- the checker cannot "
                        "detect a blank render, so it would pass one")
    if failures:
        for line in failures:
            sys.stderr.write("PLANTED CONTROL DEAD: %s\n" % line)
        return 2
    say("PLANTED CONTROL LIVE: the blank check produced both verdicts.")
    return 0


if __name__ == "__main__":
    # ParaView 5.11 under xvfb tears its GLX context down badly at interpreter
    # exit ("X Error of failed request: GLXBadContext"), which turns a completed
    # render into a non-zero return code. Every image is on disk and every check
    # has run by this point, so the status below is the real one -- flush it and
    # leave before the teardown can overwrite it with a lie.
    # The refusal codes are carried across by hand: exit 2 for a blank panel or a
    # dead planted control must survive this path, or a refusal would reach the
    # caller looking like an ordinary error.
    try:
        STATUS = main(sys.argv[1:])
    except SystemExit as exc:
        if exc.code is None:
            STATUS = 0
        elif isinstance(exc.code, int):
            STATUS = exc.code
        else:
            sys.stderr.write("%s\n" % exc.code)
            STATUS = 1
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(int(STATUS))
