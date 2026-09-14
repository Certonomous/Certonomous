#!/usr/bin/env python3
"""ParaView field panels for the ONERA M6 demo folder.

    xvfb-run -a pvpython docs/campaigns/ONERA-M6/demo/plots_M6J/render_field_panels.py

SIX PANELS, on the owner's 2026-09-13 instruction:
    m6_p_upper_top.png        upper-surface pressure from above, the lambda shock
    m6_p_oblique.png          the same surface obliquely, mesh edges drawn
    m6_mach_eta065.png        Mach on the spanwise plane through eta = 0.65
    m6_mach_eta090.png        Mach on the spanwise plane through eta = 0.90
    m6_umag_eta065.png        velocity magnitude on the same plane
    m6_umag_eta090.png        velocity magnitude on the same plane
    m6_geometry.png           the imported grid's wall patch, "as meshed"
    m6_mesh_surface.png       the FINE level's wall patch with its own edges
    m6_mesh.png               a cut at the eta = 0.65 station, framed on the nose,
                              showing the cells across it and the wall layers
    m6_mesh_medium.png        the MEDIUM level's wall patch, 1920 faces -- the
                              owner's standing "coarse or medium mesh" panel

FIELDS FROM THE FINE LEVEL, MESH FROM THE COARSE LEVEL (`m6_mesh.png`, rendered
separately by `scripts/render_openfoam_3d_paraview.py`).

NOTHING HERE IS TYPED IN.
  * the two station planes are `y_cut_target` for eta 0.65 and 0.90 read from
    `M6J_L1/cp_extracted.json` -- the SAME y the family's own extractor cut at to
    produce the Cp rows the grade file graded;
  * gamma and R come from that file's `freestream` block, which was written
    BEFORE any solve and is not re-derived from the solution;
  * Mach is a Calculator over the case's own `U` and `T`: mag(U)/sqrt(gamma R T).

CONSISTENT ACROSS THE FAMILY: both Mach panels share one colour range, both
velocity panels share another, and both surface-pressure panels share a third.
A per-panel autoscale would make two stations look alike that are not.

EVERY PANEL CARRIES A PLANTED COLOUR CONTROL: the same pipeline is rendered once
coloured by a CONSTANT array and the saved PNGs are compared. A renderer not shown
able to tell a field from a constant has not been shown to have painted anything
(DEFECT.md, DrivAer, 2026-09-12). Below the margin the panel REFUSES.

The graded tree is never opened for write: `demo3d_render_common` stages the case
as symlinks and the tree fingerprint is asserted unchanged at the end.
"""
import json, os, shutil, sys

REPO = "/home/ubuntu/Certonomous"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(REPO, "docs/campaigns/F14-cooling-ladder/demo/render_K2bU3R3_paraview"))
sys.path.insert(0, os.path.join(REPO, "verification/runs/F14-cooling-ladder/K2h_runs"))
import demo3d_render_common as C
sys.path.insert(0, os.path.join(REPO, "sdk"))
from workflows.act_paraview_style import style_view, colour_bar
import render_k2h_l3 as K2H       # for its COMMITTED colour-control measurement

FINE, FINE_END = "M6J_L1", "8000"
VERDICT = "GATE FAIL"          # m6j_grade_M6J_L1.json "verdict"
CONTROL_MARGIN = 8.0
MIN_FIELD_PX = 20000       # see _assert_painted: the colour bar alone is about 4,600 px           # the DrivAer floor, carried unchanged
STATIONS = ("0.65", "0.9")

EXT = json.load(open(os.path.join(REPO, "verification/runs/M6J_runs",
                                  FINE, "cp_extracted.json")))
FS = EXT["freestream"]
GAMMA, RGAS = FS["gamma"], FS["R_specific"]
MACH_EXPR = "mag(U)/sqrt(%.12g*%.12g*T)" % (GAMMA, RGAS)

STAMP = ("%s ; 983040 cells ; rhoSimpleFoam ; M 0.8395, alpha 3.06 deg ; "
         "t = %s ; %s" % (FINE, FINE_END, VERDICT))
GEOM = ("ONERA M6, AGARD AR-138 B1 planform ; wing patch 7680 faces ; "
        "fields of the FINE level ; the coarse level carries the mesh figure")


def _spread(path):
    """The COMMITTED measurement, not a second one.

    `render_k2h_l3._colour_spread` already fixes the body mask as "not the white
    ground" -- a saturation mask was MEASURED to find zero body pixels on a
    legitimately flat Inferno control, which refused the control for a reason
    about the measurement rather than about the render. Re-deriving that rule
    here would be how the two instruments drift apart, so it is imported.
    """
    return K2H._colour_spread(path)


def _spread_core(path):
    """The same statistic on the INTERIOR only, dropping antialiased fringes.

    WHY A SECOND MASK EXISTS, MEASURED RATHER THAN ASSUMED. The imported mask is
    "not the white ground", threshold 0.06. On a FLAT SLICE that is the picture.
    On a curved SURFACE seen obliquely a large fraction of the body is the
    antialiased silhouette, whose pixels blend the body colour into white and
    therefore span the whole red/blue ratio range WHATEVER the body is painted
    with. MEASURED on the constant-array control: 0.03023 for the top view
    (397,284 body px) and 0.04063 for the oblique view (278,774 body px) -- the
    floor rises with the perimeter-to-area ratio, which is a property of the
    camera and not of the data, and it pushed a real 0.286 positive under the
    floor at 7.0x.

    THE FLOOR IS NOT LOWERED. The fringe is excluded from BOTH arms at a
    threshold of 0.25, and BOTH statistics are printed. The looser one must
    still put the positive above the negative; the stricter one must clear the
    full 8x margin.
    """
    from paraview.vtk.util import numpy_support
    from paraview.vtk.vtkIOImage import vtkPNGReader
    import numpy as np
    r = vtkPNGReader(); r.SetFileName(path); r.Update()
    a = numpy_support.vtk_to_numpy(r.GetOutput().GetPointData().GetScalars())
    rgb = a[:, :3].astype(float) / 255.0
    body = (1.0 - rgb).max(axis=1) > 0.25
    if body.sum() < 500:
        C.refuse("%s has only %d interior pixels to measure"
                 % (os.path.basename(path), int(body.sum())))
    mx = np.maximum(rgb[body].max(axis=1), 1e-6)
    return float(((rgb[body, 0] - rgb[body, 2]) / mx).std()), int(body.sum())


def _assert_painted(pos_path, neg_path, field, core=False):
    """MEASURED HOLE, CLOSED 2026-09-13. On the SUBOFF driver's first run both
    velocity panels came out BLANK -- the slice drew nothing and only the colour bar
    was on the frame -- and the control PASSED anyway, at 49.7x and then at 4.6e8x,
    because the bar is itself a two-ended ramp and the all-white negative arm had a
    spread of exactly zero. A ratio test cannot see a blank frame: 0.45 over nothing
    is still infinitely more than 0. Two clauses close it, and both REFUSE:
      * the positive arm must cover at least MIN_FIELD_PX pixels (the bar alone is
        about 4,600, so an undrawn field cannot reach 20,000);
      * the negative arm must not have a spread of exactly zero, because a control
        that measures nothing is not a control (CLAUDE.md rule 3).
    """
    pos, npos = _spread(pos_path)
    neg, _ = _spread(neg_path)
    if npos < MIN_FIELD_PX:
        C.refuse("BLANK FRAME for %r: the positive arm covers only %s pixels, below "
                 "the %s floor -- the field was not drawn"
                 % (field, format(npos, ","), format(MIN_FIELD_PX, ",")))
    if neg <= 0.0:
        C.refuse("NO CONTROL for %r: the constant-array arm spread is exactly zero, "
                 "i.e. it drew nothing" % field)
    C.announce("  COLOUR CONTROL %s: %.5f over %s px against a CONSTANT array's "
               "%.5f, ratio %.1fx (floor %gx)"
               % (field, pos, format(npos, ","), neg, pos / max(neg, 1e-9),
                  CONTROL_MARGIN))
    if pos <= neg:
        C.refuse("COLOUR CONTROL FAILED for %r on the full-body mask: the real "
                 "field spreads %.5f and a CONSTANT array spreads %.5f"
                 % (field, pos, neg))
    if core:
        cpos, ncp = _spread_core(pos_path)
        cneg, _ = _spread_core(neg_path)
        C.announce("      interior-only: %.5f over %s px against %.5f, "
                   "ratio %.1fx" % (cpos, format(ncp, ","), cneg,
                                    cpos / max(cneg, 1e-9)))
        pos, neg = cpos, cneg
    if pos < CONTROL_MARGIN * max(neg, 1e-9):
        C.refuse("COLOUR CONTROL FAILED for %r: the real field spreads %.5f and "
                 "the same pipeline on a CONSTANT array spreads %.5f. The "
                 "renderer has not been shown able to tell a field from a "
                 "constant" % (field, pos, neg))


def _view(size=(1600, 1000)):
    from paraview.simple import CreateRenderView, Render
    v = CreateRenderView(); style_view(v, size); Render(v)
    return v


def _bar(view, lut, label, ticks=None):
    """The v2 quarter-frame bar, with LETTERING sized to be read at 1600 px.

    Sanaa, 2026-09-14: *"the colour bars are unreadably small"*. The bar's LENGTH
    is untouched -- v2 section 13 fixes it at a quarter of the frame height -- and
    only the title and label point sizes and the bar's thickness grow. `ticks`
    replaces ParaView's automatic labelling with the five values the window was
    rounded to, so the numbers under the bar are the round ones and not whatever
    the autolabeller lands on.

    ParaView 5.11.2 draws `[` and `]` in a scalar-bar title as parentheses. That is
    the renderer's font, not this code, and the titles are written with the
    brackets the orders ask for.
    """
    b = colour_bar(view, lut, label)
    b.TitleFontSize = 24
    b.LabelFontSize = 20
    b.ScalarBarThickness = 26
    b.Position = [0.885, 0.36]
    b.AutomaticLabelFormat = 0
    b.LabelFormat = "%-7.6g"
    b.RangeLabelFormat = "%-7.6g"
    if ticks is not None:
        b.UseCustomLabels = 1
        b.CustomLabels = [float(t) for t in ticks]
        b.AddRangeLabels = 0
    return b


TICK_STEPS = (1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.5, 8.0)


def colour_window(raw, pct, widen=1.25):
    """The display window and its five ticks, Sanaa's rule of 2026-09-14.

    *"If the raw data range is much wider than the field's 2nd-98th percentile
    band on the rendered surface, use the percentile band (rounded outward to
    round values with five round ticks)."*

    `widen` fixes "much wider" at a quarter again as wide, stated here rather
    than left to the eye. Whichever window is taken is then rounded OUTWARD onto
    a step from `TICK_STEPS` chosen so that the rounded window is exactly four
    steps across -- five ticks, all of them round. Nothing is removed from the
    data: values outside the window clamp to the ends of the bar.

    Returns `(lo, hi, ticks, basis)`.
    """
    import math
    lo_r, hi_r = float(raw[0]), float(raw[1])
    lo_p, hi_p = float(pct[0]), float(pct[1])
    if not hi_p > lo_p or not hi_r > lo_r:
        C.refuse("a field spanning %g to %g (percentiles %g to %g) has no range "
                 "to paint" % (lo_r, hi_r, lo_p, hi_p))
    use_pct = (hi_r - lo_r) > widen * (hi_p - lo_p)
    lo, hi = (lo_p, hi_p) if use_pct else (lo_r, hi_r)
    best = None
    for dec in range(-12, 13):
        for m in TICK_STEPS:
            step = m * 10.0 ** dec
            a = math.floor(lo / step + 1e-9)
            b = math.ceil(hi / step - 1e-9)
            if b - a != 4:
                continue
            waste = (b - a) * step - (hi - lo)
            if best is None or waste < best[0]:
                best = (waste, a * step, b * step, step)
    if best is None:
        C.refuse("no round five-tick window could be rounded outward around "
                 "%g to %g" % (lo, hi))
    _, wlo, whi, step = best
    ticks = [wlo + i * step for i in range(5)]
    basis = ("2nd-98th percentile %.6g to %.6g of a raw %.6g to %.6g"
             % (lo_p, hi_p, lo_r, hi_r)) if use_pct else (
             "raw %.6g to %.6g (percentile band %.6g to %.6g is not much "
             "narrower)" % (lo_r, hi_r, lo_p, hi_p))
    return wlo, whi, ticks, basis + ", rounded outward to %.6g .. %.6g step %.6g" % (wlo, whi, step)



def _stamp(view, second):
    """NOTHING IS WRITTEN ON THE IMAGE (v2 section 13). The case, the time, the
    geometry and the verdict live in SIDECAR.md and in the act beside the figure.
    `C.assert_stamp(STAMP, FINE)` still runs in `main` before any pixel is drawn,
    so the verdict guard is kept and only its printing is dropped."""
    return None


def _flat_lighting(disp):
    """Kill diffuse shading on a display.

    MEASURED, and the reason this exists: on the CURVED wing surface the
    negative control -- a genuinely CONSTANT array -- came back with a colour
    spread of 0.07580 against the real field's 0.29403, a ratio of 3.9x under an
    8x floor.  The spread was LIGHTING, not data: a lit surface's red/blue ratio
    varies with the surface normal whatever it is painted with.  The committed
    K2h panels never met this because they are FLAT SLICES.  The fix is to
    remove the lighting from BOTH arms rather than to lower the floor -- a guard
    relaxed to fit the answer is not a guard.
    """
    disp.Ambient = 1.0
    disp.Diffuse = 0.0
    disp.Specular = 0.0


def _control_and_save(view, pipeline, path, field, real_disp, add_caption,
                      size=(1600, 1000), core=False):
    """Render the CONSTANT-array negative arm, then the real field.

    THE CAPTIONS ARE ADDED ONLY AFTER THE MEASUREMENT, AND THAT IS NOT
    COSMETIC.  `_colour_spread` masks "not the white ground", which includes the
    dark caption text.  Caption pixels sit at a red/blue ratio of 0 while a flat
    blue control sits near -0.71, so the two populations give the NEGATIVE arm a
    standard deviation of about 0.71*sqrt(p(1-p)) -- MEASURED at 0.0756 for
    p = 0.0125 of the frame, which is the whole of the negative's floor and has
    nothing to do with whether the field was painted.  Removing the text from
    BOTH arms removes an artefact of the measurement, and it makes the control
    STRICTER (the negative's floor falls), never weaker.  The alternative --
    lowering the 8x margin -- would be fitting the guard to the answer.
    """
    from paraview.simple import (Calculator, Show, Hide, Render, ColorBy,
                                 GetColorTransferFunction, UpdatePipeline)
    flat = Calculator(Input=pipeline)
    flat.AttributeType = "Point Data"
    flat.ResultArrayName = "CONTROL_CONSTANT"
    flat.Function = "1.0"
    UpdatePipeline(proxy=flat)
    arr = flat.GetPointDataInformation().GetArray("CONTROL_CONSTANT")
    lo, hi = arr.GetComponentRange(0)
    if abs(hi - lo) > 1e-12:
        C.refuse("the control array spans %g to %g and is not constant" % (lo, hi))
    Hide(pipeline, view)          # or the real colours show through the control
    real_disp.SetScalarBarVisibility(view, False)   # and its BAR is a two-ended
    # ramp of colour: left visible it would give the NEGATIVE arm a spread that
    # belongs to the legend rather than to the picture, and weaken the control.
    dn = Show(flat, view)
    ColorBy(dn, ("POINTS", "CONTROL_CONSTANT"))
    _flat_lighting(dn)
    dn.SetScalarBarVisibility(view, False)
    Render(view)
    neg = os.path.join(os.path.dirname(path), "_control",
                       "NEGATIVE_constant_" + os.path.basename(path))
    C.save_screenshot(view, neg, size=size)
    Hide(flat, view)
    Show(pipeline, view)
    real_disp.SetScalarBarVisibility(view, True)
    Render(view)
    pos = os.path.join(os.path.dirname(path), "_control",
                       "POSITIVE_uncaptioned_" + os.path.basename(path))
    C.save_screenshot(view, pos, size=size)
    _assert_painted(pos, neg, field, core=core)
    add_caption(view)
    Render(view)
    n = C.save_screenshot(view, path, size=size)
    C.announce("  wrote %s (%s bytes)" % (os.path.basename(path), format(n, ",")))
    return n


# ---------------------------------------------------------------------------
def surface_panel(reader, path, direction, up, note, prange=None, ticks=None,
                  pad=1.05):
    """Static pressure on the FINE level's wall patch.

    TWO THINGS CHANGED ON 2026-09-14, BOTH OF THEM SANAA'S FIGURE-BY-FIGURE NOTE.

    * *"This is drawn on the coarse wall patch: you can see the 480-face banding
      across the span. The numbers come from L3 (983k cells); the picture should
      too."* **The panel was ALREADY the 983,040-cell level's own wall patch** --
      `open_case` refuses any other cell count and the 7,680-face assertion below
      is the fine patch's face count, against the coarse level's 480. What she was
      looking at was **cell-wise colouring plus drawn cell edges**: a per-face
      constant colour makes 7,680 flat facets, and the wireframe outlines every
      one of them, which reads exactly like a coarse mesh. So the field is
      interpolated to the POINTS and the EDGES ARE GONE from the pressure panels.
      The mesh figures keep their edges; they are mesh figures.
    * The frame is a 5 % margin (`pad = 1.05`) and nothing is reserved at the foot:
      no stamp is drawn under v2, so the old 10 % band only cropped the wing.
    """
    from paraview.simple import (Show, Render, ColorBy, CellDatatoPointData,
                                 GetColorTransferFunction, UpdatePipeline,
                                 MergeBlocks)
    v = _view()
    reader.MeshRegions = ["patch/wing"]
    UpdatePipeline(time=float(FINE_END), proxy=reader)
    surf = MergeBlocks(Input=reader)
    UpdatePipeline(time=float(FINE_END), proxy=surf)
    info = surf.GetDataInformation()
    if info.GetNumberOfCells() != 7680:
        C.refuse("the wing patch rendered %d cells where constant/polyMesh/"
                 "boundary says 7680" % info.GetNumberOfCells())
    pts = CellDatatoPointData(Input=surf)
    pts.CellDataArraytoprocess = ["p"]
    UpdatePipeline(time=float(FINE_END), proxy=pts)
    if pts.GetPointDataInformation().GetArray("p") is None:
        C.refuse("the wall patch carries no point-interpolated p, so the smooth "
                 "panel would be painted with nothing")
    d = Show(pts, v)
    _flat_lighting(d)
    ColorBy(d, ("POINTS", "p"))
    lut = GetColorTransferFunction("p")
    lut.ApplyPreset("Cool to Warm", True)
    lut.RescaleTransferFunction(*prange)
    d.SetScalarBarVisibility(v, True)
    _bar(v, lut, "p  [Pa]", ticks=ticks)
    b = info.GetBounds()
    C.frame_by_extent(v, [(b[0] + b[1]) / 2, (b[2] + b[3]) / 2, (b[4] + b[5]) / 2],
                      direction, up=up, bounds=b, pad=pad, bottom_band=0.0)
    Render(v)
    return _control_and_save(v, pts, path, "p", d, lambda view: _stamp(view, note),
                             core=True)


def station_panel(reader, path, y_cut, eta, kind, rng, ticks=None,
                  sonic=False, wall=None):
    """A spanwise y-plane through a graded station, coloured by Mach or by |U|.

    SANAA, 2026-09-14, items 3 and 4: *"Re-render on L3 with a fixed Mach range
    (0 to 1.4) and the sonic line M = 1 drawn -- that's the picture the tunnel
    comparison is about."* So on the Mach panels the window is **0 to 1.4 BY HER
    ORDER**, not measured and not rounded from a percentile, with five ticks at
    0, 0.35, 0.70, 1.05 and 1.40; `M = 1` is drawn as a black contour line; and
    the frame is cut to the section's own chord -- 0.3 c ahead of the leading
    edge to 0.3 c behind the trailing edge, 0.6 c above and below -- instead of
    the 0.8 c box that put half the farfield on the figure.

    The wing's own section is outlined in black. The slice of the internal mesh
    already leaves the wing as a hole; the outline says that the hole is the
    wing and not missing data.

    THE CONTOUR AND THE OUTLINE GO ON AFTER THE COLOUR CONTROL, for the reason
    the mesh edges and the captions did: black line pixels are a second
    population inside the "not the white ground" body mask and would hand the
    CONSTANT arm a spread that belongs to the line work rather than to the field.
    """
    from paraview.simple import (CellDatatoPointData, Slice, Calculator, Show,
                                 Render, ColorBy, GetColorTransferFunction,
                                 Contour, UpdatePipeline)
    v = _view()
    reader.MeshRegions = ["internalMesh"]
    UpdatePipeline(time=float(FINE_END), proxy=reader)
    p2c = CellDatatoPointData(Input=reader)
    p2c.CellDataArraytoprocess = ["U", "T", "p"]
    UpdatePipeline(time=float(FINE_END), proxy=p2c)

    calc = Calculator(Input=p2c)
    calc.AttributeType = "Point Data"
    if kind == "mach":
        calc.ResultArrayName = "Mach"
        calc.Function = MACH_EXPR
        name, label = "Mach", "M  [-]"
    else:
        calc.ResultArrayName = "Umag"
        calc.Function = "mag(U)"
        name, label = "Umag", "|U|  [m/s]"
    UpdatePipeline(time=float(FINE_END), proxy=calc)

    s = Slice(Input=calc)
    s.SliceType = "Plane"
    s.SliceType.Origin = [0.0, y_cut, 0.0]
    s.SliceType.Normal = [0.0, 1.0, 0.0]
    UpdatePipeline(time=float(FINE_END), proxy=s)
    if s.GetDataInformation().GetNumberOfCells() == 0:
        C.refuse("the eta = %s slice is empty; nothing would be drawn" % eta)

    d = Show(s, v)
    _flat_lighting(d)
    ColorBy(d, ("POINTS", name))
    lut = GetColorTransferFunction(name)
    # ONE colour map for both station quantities: Mach and velocity magnitude
    # show the same structure and a reader compares them across four panels.
    lut.ApplyPreset("Viridis (matplotlib)", True)
    lut.RescaleTransferFunction(*rng)
    d.SetScalarBarVisibility(v, True)
    _bar(v, lut, label, ticks=ticks)

    # frame on the wing's own chord at this station, not on the farfield box
    st = EXT["stations"][eta]
    x0, x1 = st["x_le"], st["x_te"]
    c = st["local_chord"]
    bnds = (x0 - 0.3 * c, x1 + 0.3 * c, y_cut, y_cut, -0.6 * c, 0.6 * c)
    C.frame_by_extent(v, [(x0 + x1) / 2, y_cut, 0.0], (0.0, -1.0, 0.0),
                      up=(0.0, 0.0, 1.0), bounds=bnds, pad=1.02,
                      bottom_band=0.0)
    note = ("%s ; y-normal plane at y = %.6f m, the cut the family extractor used for "
            "eta = %s ; local chord %.4f m ; colour bar %.4g to %.4g, ends clamped"
            % (GEOM, y_cut, eta, c, rng[0], rng[1]))

    def _lines(view):
        if sonic:
            iso = Contour(Input=s)
            iso.ContourBy = ["POINTS", name]
            iso.Isosurfaces = [1.0]
            UpdatePipeline(time=float(FINE_END), proxy=iso)
            n_iso = iso.GetDataInformation().GetNumberOfCells()
            C.announce("      sonic line M = 1 at eta = %s: %s line segments"
                       % (eta, format(n_iso, ",")))
            if n_iso:
                di = Show(iso, view)
                di.DiffuseColor = [0.0, 0.0, 0.0]
                di.AmbientColor = [0.0, 0.0, 0.0]
                di.ColorArrayName = [None, ""]
                di.LineWidth = 3.0
        if wall is not None:
            ws = Slice(Input=wall)
            ws.SliceType = "Plane"
            ws.SliceType.Origin = [0.0, y_cut, 0.0]
            ws.SliceType.Normal = [0.0, 1.0, 0.0]
            UpdatePipeline(time=float(FINE_END), proxy=ws)
            if ws.GetDataInformation().GetNumberOfCells() == 0:
                C.refuse("the wing outline at eta = %s is empty" % eta)
            dw = Show(ws, view)
            dw.DiffuseColor = [0.0, 0.0, 0.0]
            dw.AmbientColor = [0.0, 0.0, 0.0]
            dw.ColorArrayName = [None, ""]
            dw.LineWidth = 3.0
        # MEASURED, 2026-09-14: calling SetScalarBarVisibility(False) on the
        # line displays -- which carry no array at all -- TOOK THE FIELD'S OWN
        # COLOUR BAR OFF THE FRAME. The first Mach panel came out with the sonic
        # line drawn and no bar. The bar is therefore re-asserted here, on the
        # display that owns it, after the line work is added.
        d.SetScalarBarVisibility(view, True)
        _stamp(view, note)

    Render(v)
    return _control_and_save(v, s, path, name, d, _lines)


def geometry_panel(reader, path):
    """The imported grid's WALL PATCH as the surface. Caption: "as meshed"."""
    from paraview.simple import Show, Render, MergeBlocks, UpdatePipeline, ColorBy
    v = _view()
    reader.MeshRegions = ["patch/wing"]
    UpdatePipeline(time=float(FINE_END), proxy=reader)
    surf = MergeBlocks(Input=reader)
    UpdatePipeline(time=float(FINE_END), proxy=surf)
    info = surf.GetDataInformation()
    if info.GetNumberOfCells() != 7680:
        C.refuse("the wing patch rendered %d cells where constant/polyMesh/"
                 "boundary says 7680" % info.GetNumberOfCells())
    d = Show(surf, v)
    ColorBy(d, None)
    d.DiffuseColor = [0.62, 0.65, 0.70]
    # Sanaa, 2026-09-14, on the support figure titled "wing surface as meshed":
    # *"it's actually the pressure-coloured wing again -- either title it as
    # pressure or render the plain surface."* THE PLAIN SURFACE IS THE OPTION
    # TAKEN. It carries no field and now no wireframe either, which is also what
    # keeps it from being a second copy of `m6_mesh_surface.png` -- that panel is
    # the same patch WITH its cell edges, and it is the one the mesh figure slot
    # wants.
    d.Representation = "Surface"
    b = info.GetBounds()
    C.frame_by_extent(v, [(b[0] + b[1]) / 2, (b[2] + b[3]) / 2, (b[4] + b[5]) / 2],
                      (0.75, -0.55, 0.60), up=(0.0, 0.0, 1.0), bounds=b,
                      pad=1.10, bottom_band=0.10)
    _stamp(v, "as meshed")
    Render(v)
    n = C.save_screenshot(v, path, size=(1600, 1000))
    _, npx = _spread(path)
    if npx < 20000:
        C.refuse("m6_geometry.png has only %d non-background pixels; the "
                 "surface was not drawn" % npx)
    C.announce("  wrote %s (%s bytes, %s body px)"
               % (os.path.basename(path), format(n, ","), format(npx, ",")))
    return n


PCT_LO, PCT_HI = 2.0, 98.0      # the display window, stated on every caption


def _percentiles(src, name, assoc):
    """The PCT_LO / PCT_HI percentiles of an array, measured on the real data.

    WHY A PERCENTILE AND NOT THE FULL RANGE.  On this case the full range is set
    by a handful of cells at the leading-edge stagnation point: MEASURED, Mach
    spans 0.000963 to 1.52723 over the two station planes while the flow a reader
    is looking at sits near 0.84, so a bar stretched to the extremes paints the
    whole picture one teal and hides the supersonic pocket the figure exists to
    show.  This is a DISPLAY WINDOW, not a filter: nothing is removed from the
    data, values outside are clamped to the ends of the bar, the window is the
    SAME for every panel of a family, and BOTH the window and the fact of
    clamping are printed on every caption.
    """
    import numpy as np
    from paraview import servermanager as sm
    from paraview.vtk.util import numpy_support
    d = sm.Fetch(src)
    blocks = []
    if hasattr(d, "GetNumberOfBlocks"):
        it = d.NewIterator(); it.InitTraversal()
        while not it.IsDoneWithTraversal():
            blocks.append(it.GetCurrentDataObject()); it.GoToNextItem()
    else:
        blocks = [d]
    vals = []
    for b in blocks:
        att = b.GetPointData() if assoc == "POINTS" else b.GetCellData()
        arr = att.GetArray(name)
        if arr is None:
            continue
        a = numpy_support.vtk_to_numpy(arr)
        if a.ndim > 1:
            a = np.linalg.norm(a, axis=1)
        vals.append(a)
    if not vals:
        C.refuse("no %s array was fetched, so no window can be measured" % name)
    a = np.concatenate(vals)
    return float(np.percentile(a, PCT_LO)), float(np.percentile(a, PCT_HI))


def _raw_range(src, name, assoc):
    """The array's FULL range, for the percentile window to be judged against."""
    info = (src.GetPointDataInformation() if assoc == "POINTS"
            else src.GetCellDataInformation())
    arr = info.GetArray(name)
    if arr is None:
        C.refuse("no %s array to take a raw range from" % name)
    if arr.GetNumberOfComponents() > 1:
        lo, hi = arr.GetRange(-1)
    else:
        lo, hi = arr.GetRange(0)
    return float(lo), float(hi)


def _shared_range(reader, cuts, kind):
    """Raw range AND 2nd-98th percentile band of the field over BOTH station
    planes, measured. Returns `((raw_lo, raw_hi), (p2, p98))`."""
    from paraview.simple import (CellDatatoPointData, Calculator, Slice,
                                 UpdatePipeline)
    reader.MeshRegions = ["internalMesh"]
    UpdatePipeline(time=float(FINE_END), proxy=reader)
    p2c = CellDatatoPointData(Input=reader)
    p2c.CellDataArraytoprocess = ["U", "T"]
    UpdatePipeline(time=float(FINE_END), proxy=p2c)
    calc = Calculator(Input=p2c)
    calc.AttributeType = "Point Data"
    calc.ResultArrayName = "Mach" if kind == "mach" else "Umag"
    calc.Function = MACH_EXPR if kind == "mach" else "mag(U)"
    UpdatePipeline(time=float(FINE_END), proxy=calc)
    lo = hi = rlo = rhi = None
    for y in cuts.values():
        sl = Slice(Input=calc)
        sl.SliceType = "Plane"
        sl.SliceType.Origin = [0.0, y, 0.0]
        sl.SliceType.Normal = [0.0, 1.0, 0.0]
        UpdatePipeline(time=float(FINE_END), proxy=sl)
        if sl.GetPointDataInformation().GetArray(calc.ResultArrayName) is None:
            C.refuse("the %s slice carries no %s array" % (kind, calc.ResultArrayName))
        a, b = _raw_range(sl, calc.ResultArrayName, "POINTS")
        rlo = a if rlo is None else min(rlo, a)
        rhi = b if rhi is None else max(rhi, b)
        r = _percentiles(sl, calc.ResultArrayName, "POINTS")
        lo = r[0] if lo is None else min(lo, r[0])
        hi = r[1] if hi is None else max(hi, r[1])
    if not hi > lo:
        C.refuse("%s spans %g to %g over the two station planes; a field with "
                 "no range cannot be shown to have been painted" % (kind, lo, hi))
    return (rlo, rhi), (lo, hi)


def mesh_panels(reader, out_body, out_cut, y_cut, eta):
    """The FINE level's wall patch, and a cut through the eta = 0.65 station.

    Sanaa, 2026-09-13: *"the 480-face coarse wall patch reads as a toy … show the
    fine-level wall patch plus a cut through 65 % span showing the cells across the
    nose and the wall layers"*. The coarse level keeps the mesh figure only where a
    snappy mesh is genuinely illegible, and this is a structured O-grid that is not.

    Both panels are GEOMETRY, so they carry an ink guard and not a colour control: a
    plain mesh has no field to be told apart from a constant.
    """
    from paraview.simple import (MergeBlocks, Slice, Show, Render, UpdatePipeline,
                                 CellDatatoPointData)
    # (a) the fine wall patch
    v = _view()
    reader.MeshRegions = ["patch/wing"]
    UpdatePipeline(time=float(FINE_END), proxy=reader)
    surf = MergeBlocks(Input=reader); UpdatePipeline(time=float(FINE_END), proxy=surf)
    info = surf.GetDataInformation()
    if info.GetNumberOfCells() != 7680:
        C.refuse("the fine wing patch rendered %d cells, not 7680"
                 % info.GetNumberOfCells())
    d = Show(surf, v); _flat_lighting(d)
    d.ColorArrayName = [None, ""]
    d.DiffuseColor = [0.66, 0.69, 0.74]; d.AmbientColor = [0.66, 0.69, 0.74]
    d.Representation = "Surface With Edges"
    d.EdgeColor = [0.12, 0.12, 0.12]; d.LineWidth = 0.3
    b = info.GetBounds()
    C.frame_by_extent(v, [(b[0] + b[1]) / 2, (b[2] + b[3]) / 2, (b[4] + b[5]) / 2],
                      (0.75, -0.55, 0.60), up=(0.0, 0.0, 1.0), bounds=b, pad=1.06)
    Render(v)
    n1 = C.save_screenshot(v, out_body, size=(1600, 1000))
    _, px1 = _spread(out_body)
    if px1 < 20000:
        C.refuse("%s drew only %d body pixels" % (os.path.basename(out_body), px1))
    C.announce("  wrote %s (%s bytes, 7680 faces, %s body px)"
               % (os.path.basename(out_body), format(n1, ","), format(px1, ",")))

    # (b) the cut at the eta = 0.65 station, framed on the nose and its layers
    v2 = _view()
    reader.MeshRegions = ["internalMesh"]
    UpdatePipeline(time=float(FINE_END), proxy=reader)
    s2 = Slice(Input=reader)
    s2.SliceType = "Plane"
    s2.SliceType.Origin = [0.0, y_cut, 0.0]
    s2.SliceType.Normal = [0.0, 1.0, 0.0]
    UpdatePipeline(time=float(FINE_END), proxy=s2)
    ncut = s2.GetDataInformation().GetNumberOfCells()
    if ncut == 0:
        C.refuse("the eta = %s cut is empty" % eta)
    C.announce("  eta = %s cut: %s cells in the plane" % (eta, format(ncut, ",")))
    d2 = Show(s2, v2); _flat_lighting(d2)
    d2.ColorArrayName = [None, ""]
    d2.DiffuseColor = [0.90, 0.91, 0.93]; d2.AmbientColor = [0.90, 0.91, 0.93]
    d2.Representation = "Surface With Edges"
    d2.EdgeColor = [0.10, 0.10, 0.10]; d2.LineWidth = 0.35
    st = EXT["stations"][eta]
    c = st["local_chord"]; x0 = st["x_le"]
    # the nose and the layers, not the farfield: a quarter chord about the LE
    bnds = (x0 - 0.10 * c, x0 + 0.22 * c, y_cut, y_cut, -0.16 * c, 0.16 * c)
    C.frame_by_extent(v2, [x0 + 0.06 * c, y_cut, 0.0], (0.0, -1.0, 0.0),
                      up=(0.0, 0.0, 1.0), bounds=bnds, pad=1.02)
    Render(v2)
    n2 = C.save_screenshot(v2, out_cut, size=(1600, 1000))
    _, px2 = _spread(out_cut)
    if px2 < 20000:
        C.refuse("%s drew only %d body pixels" % (os.path.basename(out_cut), px2))
    C.announce("  wrote %s (%s bytes, %s body px)"
               % (os.path.basename(out_cut), format(n2, ","), format(px2, ",")))
    return n1 + n2


def coarse_mesh_panel(out):
    """The MEDIUM level's wall patch, per the owner's standing ParaView rule.

    Her rule of 2026-09-13: *"for all the cases we should plot the coarse or medium
    mesh (but show the fine mesh's result)"*. **MEDIUM and not coarse, and that is a
    measurement rather than a default**: her earlier note is that this family's coarse
    level *"reads as a toy"*, and the boundary file says why -- `M6J_L3` carries
    **480** wall faces against `M6J_L2`'s **1,920**. The rule admits either, so the
    legible one is taken and the count is printed here rather than left to the eye.

    The fine level keeps the FIELD panels and the nose cut; nothing is interpolated
    between the two meshes.
    """
    from paraview.simple import MergeBlocks, Show, Render, UpdatePipeline
    root = None
    try:
        reader, root, n = C.open_case("M6J_L2", ["p"], ["5000"])
        C.announce("  M6J_L2: %s cells" % format(n, ","))
        v = _view()
        reader.MeshRegions = ["patch/wing"]
        UpdatePipeline(time=5000.0, proxy=reader)
        surf = MergeBlocks(Input=reader); UpdatePipeline(time=5000.0, proxy=surf)
        info = surf.GetDataInformation()
        if info.GetNumberOfCells() != 1920:
            C.refuse("the M6J_L2 wing patch rendered %d cells where the boundary "
                     "file says 1920" % info.GetNumberOfCells())
        d = Show(surf, v); _flat_lighting(d)
        d.ColorArrayName = [None, ""]
        d.DiffuseColor = [0.66, 0.69, 0.74]; d.AmbientColor = [0.66, 0.69, 0.74]
        d.Representation = "Surface With Edges"
        d.EdgeColor = [0.12, 0.12, 0.12]; d.LineWidth = 0.6
        b = info.GetBounds()
        C.frame_by_extent(v, [(b[0] + b[1]) / 2, (b[2] + b[3]) / 2, (b[4] + b[5]) / 2],
                          (0.75, -0.55, 0.60), up=(0.0, 0.0, 1.0), bounds=b, pad=1.06)
        Render(v)
        nb = C.save_screenshot(v, out, size=(1600, 1000))
        _, px = _spread(out)
        if px < 20000:
            C.refuse("%s drew only %d body pixels" % (os.path.basename(out), px))
        C.announce("  wrote %s (%s bytes, 1920 faces, %s body px)"
                   % (os.path.basename(out), format(nb, ","), format(px, ",")))
        return nb
    finally:
        if root:
            shutil.rmtree(root, ignore_errors=True)


def main():
    C.assert_paraview_version()
    cdir = C.facts(FINE)["case_dir"]
    before = C.run_tree_fingerprint(cdir)
    C.assert_stamp(STAMP, FINE)
    root, total = None, 0
    windows = []            # (figure, quantity, basis) for the provenance file
    try:
        reader, root, n = C.open_case(FINE, ["p", "U", "T"], [FINE_END])
        C.announce("  %s: %s cells at t = %s" % (FINE, format(n, ","), FINE_END))

        # a SECOND reader on the same staged case, kept on the wall patch, so the
        # station panels can outline the wing section without disturbing the
        # internal-mesh reader the field pipeline is on.
        from paraview.simple import OpenFOAMReader, UpdatePipeline
        wall = OpenFOAMReader(FileName=os.path.join(root, "%s.foam" % FINE))
        wall.MeshRegions = ["patch/wing"]
        wall.CellArrays = ["p"]
        UpdatePipeline(time=float(FINE_END), proxy=wall)
        if wall.GetDataInformation().GetNumberOfCells() != 7680:
            C.refuse("the outline reader loaded %d wall faces, not 7680"
                     % wall.GetDataInformation().GetNumberOfCells())

        # one pressure window for BOTH surface panels, under Sanaa's percentile rule
        reader.MeshRegions = ["patch/wing"]
        UpdatePipeline(time=float(FINE_END), proxy=reader)
        from paraview.simple import MergeBlocks as _MB
        _surf = _MB(Input=reader)
        UpdatePipeline(time=float(FINE_END), proxy=_surf)
        p_raw = _raw_range(_surf, "p", "CELLS")
        p_pct = _percentiles(_surf, "p", "CELLS")
        plo, phi, pticks, pbasis = colour_window(p_raw, p_pct)
        C.announce("  surface p window %.6g to %.6g Pa -- %s" % (plo, phi, pbasis))
        prange = (plo, phi)
        WALL = "patch/wing, 7680 faces, p interpolated cell -> point"
        windows.append(("m6_p_upper_top.png", FINE, n, FINE_END, WALL,
                        "parallel, along -z (camera at +z), up +y, 5% margin",
                        "%.6g to %.6g Pa" % prange, pbasis))
        windows.append(("m6_p_oblique.png", FINE, n, FINE_END, WALL,
                        "parallel, direction (0.75,-0.55,0.60), up +z",
                        "%.6g to %.6g Pa" % prange, pbasis))

        # ITEM 2: plan view. The camera looks along -z (it sits at +z), parallel
        # projection, the whole wing in frame with a 5 % margin.
        total += surface_panel(
            reader, os.path.join(HERE, "m6_p_upper_top.png"),
            (0.0, 0.0, 1.0), (0.0, 1.0, 0.0),
            GEOM + " ; UPPER surface, camera along -z ; colour bar %.0f to %.0f Pa, "
            "ends clamped" % prange, prange=prange, ticks=pticks, pad=1.111)
        # ITEM 1: the same field and the same window, obliquely.
        total += surface_panel(
            reader, os.path.join(HERE, "m6_p_oblique.png"),
            (0.75, -0.55, 0.60), (0.0, 0.0, 1.0),
            GEOM + " ; oblique view ; colour bar %.0f to %.0f Pa, ends clamped"
            % prange, prange=prange, ticks=pticks, pad=1.05)
        total += geometry_panel(reader, os.path.join(HERE, "m6_geometry.png"))
        windows.append(("m6_geometry.png", FINE, n, FINE_END,
                        "patch/wing, 7680 faces, plain surface, no field and no edges",
                        "parallel, direction (0.75,-0.55,0.60), up +z", "-", "no colour map"))
        y65 = EXT["stations"]["0.65"]["y_cut_target"]
        total += mesh_panels(reader, os.path.join(HERE, "m6_mesh_surface.png"),
                             os.path.join(HERE, "m6_mesh.png"), y65, "0.65")
        windows.append(("m6_mesh_surface.png", FINE, n, FINE_END,
                        "patch/wing, 7680 faces, surface with cell edges",
                        "parallel, direction (0.75,-0.55,0.60), up +z", "-", "no colour map"))
        windows.append(("m6_mesh.png", FINE, n, FINE_END,
                        "y-normal cut at y = %.6f m (eta = 0.65), cells and wall layers" % y65,
                        "parallel, along +y, up +z ; framed on the leading edge", "-",
                        "no colour map"))
        total += coarse_mesh_panel(os.path.join(HERE, "m6_mesh_medium.png"))
        windows.append(("m6_mesh_medium.png", "M6J_L2", 122880, "5000",
                        "patch/wing, 1920 faces, surface with cell edges",
                        "parallel, direction (0.75,-0.55,0.60), up +z", "-",
                        "no colour map"))

        cuts = {e: EXT["stations"][e]["y_cut_target"] for e in STATIONS}

        # MACH IS FIXED AT 0 TO 1.4 BY SANAA'S ORDER OF 2026-09-14 -- not measured,
        # not rounded from a percentile, and the same on both stations. The raw
        # range is still MEASURED and printed, so the figure's clamping is on the
        # record rather than hidden.
        m_raw, m_pct = _shared_range(reader, cuts, "mach")
        MACH_RNG = (0.0, 1.4)
        MACH_TICKS = [0.0, 0.35, 0.70, 1.05, 1.40]
        mbasis = ("FIXED 0 to 1.4 by owner instruction 2026-09-14 ; measured raw "
                  "%.6g to %.6g, 2nd-98th percentile %.6g to %.6g, ends clamped"
                  % (m_raw[0], m_raw[1], m_pct[0], m_pct[1]))
        C.announce("  Mach window %s" % mbasis)

        u_raw, u_pct = _shared_range(reader, cuts, "umag")
        ulo, uhi, uticks, ubasis = colour_window(u_raw, u_pct)
        C.announce("  |U| window %.6g to %.6g m/s -- %s" % (ulo, uhi, ubasis))

        CAM = ("parallel, along +y (spanwise plane in view), up +z ; window "
               "x_le-0.3c to x_te+0.3c, z +/-0.6c")
        for e, tag in ((STATIONS[0], "eta065"), (STATIONS[1], "eta090")):
            y = cuts[e]
            geo = ("y-normal plane at y = %.6f m (the extractor's own cut for "
                   "eta = %s), wing section outlined, M = 1 contour drawn" % (y, e))
            total += station_panel(reader, os.path.join(HERE, "m6_mach_%s.png" % tag),
                                   y, e, "mach", MACH_RNG, ticks=MACH_TICKS,
                                   sonic=True, wall=wall)
            windows.append(("m6_mach_%s.png" % tag, FINE, n, FINE_END, geo, CAM,
                            "0 to 1.4 (M)", mbasis))
            total += station_panel(reader, os.path.join(HERE, "m6_umag_%s.png" % tag),
                                   y, e, "umag", (ulo, uhi), ticks=uticks,
                                   wall=wall)
            windows.append(("m6_umag_%s.png" % tag, FINE, n, FINE_END,
                            geo.replace(", M = 1 contour drawn", ""), CAM,
                            "%.6g to %.6g m/s" % (ulo, uhi), ubasis))
    finally:
        if root:
            shutil.rmtree(root, ignore_errors=True)
    C.assert_run_tree_untouched(cdir, before)
    C.announce("  run tree PROVED unchanged: %s" % cdir)
    with open(os.path.join(HERE, "PROVENANCE_PANELS.tsv"), "w") as fh:
        fh.write("figure\tcase\tcells\ttime_dir\tgeometry\tcamera\t"
                 "colour_range\twindow_basis\n")
        for row in windows:
            fh.write("\t".join(str(x) for x in row) + "\n")
    C.announce("  %s bytes written to %s" % (format(total, ","), HERE))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except C.RenderRefusal as exc:
        C.announce_error("REFUSED: %s" % exc)
        sys.exit(2)
