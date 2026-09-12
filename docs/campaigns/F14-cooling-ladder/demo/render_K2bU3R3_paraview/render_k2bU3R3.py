#!/usr/bin/env python3
"""render_k2bU3R3.py -- ParaView renders of K2bU3R3_D59, the lab's 3-D data
centre rack row. RUN WITH pvpython.

    xvfb-run -a pvpython docs/campaigns/F14-cooling-ladder/demo/render_K2bU3R3_paraview/render_k2bU3R3.py

WHAT THIS CASE IS
-----------------
137,000 cells, buoyantBoussinesqPimpleFoam, transient to t = 80 s. A room
3.6 x 3.5 x 2.7 m holding a row of FOUR racks with OPEN ROW ENDS: cold supply
through floor tiles in the cold aisle, hot discharge into the hot aisle, ceiling
return. Geometry from ``build_k2bU3.py`` (XS/YS/ZS, RACK_XI, TILE_YI,
RETURN_YI) and ``build_k2b.py`` (D_R, H_R, W_CA, W_HA, H_ROOM).

The open row ends are the reason this case exists. They are the spanwise path
around the end of the rack row -- air leaving the hot aisle can travel along x,
round the end of the row at x < 0.6 or x > 3.0, and re-enter the cold aisle.
**A TWO-DIMENSIONAL SLICE CANNOT HAVE THAT PATH AT ALL**, which is precisely why
the 2-D result needed testing in 3-D, and why a render of this case has to show
the ends rather than only a pretty aisle cross-section.

THE VERDICT, AND THE ONE WORD THAT MAY NEVER APPEAR
----------------------------------------------------
**GATE REACHED.** Final-window peak-to-peak 0.6058 K against 1.4414 K in the
preceding window, ratio 0.420 against a pre-registered DAMPS threshold of
ratio <= 0.5 (``K2bU3R3_GRADE.txt``).

**IT IS GATE REACHED AND NEVER PASS.** The gate is a survives/damps
DISCRIMINATOR: it asks which of two behaviours occurred, and returns SURVIVES,
DAMPS or UNDECIDABLE. ``PASS`` is a value-in-band term and this gate has no band
for a value to be inside. The verdict was deliberately corrected away from PASS
on 2026-09-09 under VERIFICATION_CHARTER section 2, and a figure captioned PASS
here would re-introduce exactly the defect that correction removed.

This is not left to the caption writer. ``demo3d_render_common.CASE_FACTS``
records ``allowed_verdicts = {"GATE REACHED"}`` for this case, and
``assert_stamp`` REFUSES any stamp carrying PASS -- before a single pixel is
rendered. The self-test drives that refusal in both arms.

NO SOLVER IS RUN. Fields are read from the graded tree through a scratch case of
symlinks; the graded tree is fingerprinted before and proved unchanged after.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "scripts"))

import demo3d_render_common as C   # noqa: E402

CASE = "K2bU3R3_D59"
OUT = os.path.join(REPO, "docs", "campaigns", "F14-cooling-ladder", "demo",
                   "figures_K2bU3R3")
END = "80"

# --- geometry, from the builders. Not typed from memory: see module docstring.
ROOM = (3.6, 3.5, 2.7)          # XS[-1], YS[-1], ZS[-1]
RACK_X0, RACK_X1 = 0.6, 3.0     # XS[RACK_XI[0]] .. XS[RACK_XI[-1]+1]
RACK_Y0, RACK_Y1 = 1.2, 2.3     # W_CA .. W_CA + D_R
RACK_Z1 = 2.0                   # H_R
COLD_Y0, COLD_Y1 = 0.6, 1.2     # YS[1] .. YS[2], tile on the floor between
RETURN_Y0, RETURN_Y1 = 2.6, 3.2  # YS[4] .. YS[5], return at the ceiling
T_SUP = 289.0                   # K, build_k2b.T_SUP

#: The colour range for every temperature figure. T_SUP = 289 K is the supply,
#: and the rack discharge sits ~12 K above it (build_k2b.DT_RACK = 12.0). The
#: top of the range is deliberately NOT the field maximum: a handful of cells on
#: the rack outlet patches reach 307 K and letting them set the scale flattens
#: the entire room to one colour. 305 K was chosen after 301 K was tried and
#: rendered the whole hot aisle as one flat red mass with no structure in it:
#: at t = 80 s most of that aisle is above 301 K. The bound is stated in every
#: caption that uses it, and the field's true range is printed beside it.
T_LO, T_HI = 289.0, 305.0

STAMP = ("K2bU3R3_D59 ; 137000 cells ; buoyantBoussinesqPimpleFoam ; "
         "GATE REACHED")

GEOM = ("Room 3.6 x 3.5 x 2.7 m ; 4 racks ; OPEN row ends ; transient, "
        "fields at t = 80 s as solved")


def build_view(size=(1600, 1000)):
    from paraview.simple import CreateRenderView, SetActiveView
    v = CreateRenderView()
    SetActiveView(v)
    C.white_background(v)
    v.ViewSize = list(size)
    v.ViewTime = float(END)
    return v


def colour_by_T(disp, view, show_bar=False, label="T  (K)"):
    from paraview.simple import ColorBy, GetColorTransferFunction, GetScalarBar
    ColorBy(disp, ("POINTS", "T"))
    lut = GetColorTransferFunction("T")
    lut.ApplyPreset("Cool to Warm", True)
    lut.RescaleTransferFunction(T_LO, T_HI)
    disp.SetScalarBarVisibility(view, bool(show_bar))
    if show_bar:
        bar = GetScalarBar(lut, view)
        bar.Visibility = 1
        bar.Title = label
        bar.ComponentTitle = ""
        bar.TitleColor = [0.15, 0.15, 0.15]
        bar.LabelColor = [0.15, 0.15, 0.15]
        bar.TitleFontSize = 11
        bar.LabelFontSize = 10
        bar.ScalarBarLength = 0.32
        bar.ScalarBarThickness = 12
        bar.WindowLocation = "Any Location"
        bar.Position = [0.885, 0.36]
        bar.AutomaticLabelFormat = 0
        bar.LabelFormat = "%-#.1f"
        bar.AddRangeLabels = 1
    return lut


def frame(view, focal, direction, up=(0.0, 0.0, 1.0), pad=1.08,
          bottom_band=0.10):
    """Frame the room through the shared, asserted framer.

    The three ways this was got wrong -- a hand-typed scale, ResetCamera's
    bounding SPHERE, and the automatic reset performed by a fresh view's first
    render -- are documented on demo3d_render_common.frame_by_extent, which both
    3-D cases now share because both met all three.
    """
    return C.frame_by_extent(view, focal, direction, up=up, pad=pad,
                             bottom_band=bottom_band,
                             bounds=(0.0, ROOM[0], 0.0, ROOM[1], 0.0, ROOM[2]))


#: Tolerance on the colour-bar range check, in kelvin.
RANGE_TOL_K = 1e-6


def lock_colour_range(view):
    """Re-apply the colour range and PROVE it took, right before the render.

    Showing a second representation re-scales a colour transfer function to the
    new data range behind your back: the row-end figure came out with a colour
    bar running to 307 K after a glyph was added, while the aisle figure beside
    it ran to 301 K, and every caption stating a range would have been reporting
    a number the picture did not use. Captions quote T_LO and T_HI, so T_LO and
    T_HI are what the bar must actually carry.
    """
    from paraview.simple import GetColorTransferFunction
    lut = GetColorTransferFunction("T")
    lut.RescaleTransferFunction(T_LO, T_HI)
    pts = list(lut.RGBPoints)
    lo, hi = pts[0], pts[-4]
    if abs(lo - T_LO) > RANGE_TOL_K or abs(hi - T_HI) > RANGE_TOL_K:
        C.refuse(f"the colour transfer function spans {lo:.4f} to {hi:.4f} K "
                 f"where every caption on this figure says {T_LO:.1f} to "
                 f"{T_HI:.1f} K. A colour bar that disagrees with its own "
                 f"caption is a false reading of the field")
    return lo, hi


def stamp(view, second_line: str):
    C.caption(view, STAMP, CASE, position=(0.012, 0.048), size=11)
    C.caption(view, second_line, CASE, position=(0.012, 0.018), size=9,
              check_stamp=False)


def outline(src, view):
    from paraview.simple import Outline, Show
    o = Show(Outline(Input=src), view)
    o.ColorArrayName = [None, ""]
    o.AmbientColor = [0.3, 0.3, 0.3]
    o.DiffuseColor = [0.3, 0.3, 0.3]
    return o


def rack_block(view):
    """Draw the rack row as an opaque grey body.

    The racks are VOIDS in this mesh -- ``build_k2bU3.void()`` removes those
    cells -- so without something drawn there the reader sees a hole and has no
    way to know it is the hardware. Nothing here is field data and it is
    labelled as geometry in every caption that shows it.
    """
    from paraview.simple import Box, Show
    b = Box()
    b.XLength = RACK_X1 - RACK_X0
    b.YLength = RACK_Y1 - RACK_Y0
    b.ZLength = RACK_Z1
    b.Center = [(RACK_X0 + RACK_X1) / 2, (RACK_Y0 + RACK_Y1) / 2, RACK_Z1 / 2]
    d = Show(b, view)
    d.Representation = "Surface"
    d.ColorArrayName = [None, ""]
    d.DiffuseColor = [0.62, 0.64, 0.68]
    d.AmbientColor = [0.62, 0.64, 0.68]
    d.Opacity = 1.0
    return b


def field_range(src, name="T"):
    di = src.GetDataInformation()
    for assoc in ("point", "cell"):
        info = (di.GetPointDataInformation() if assoc == "point"
                else di.GetCellDataInformation()).GetArrayInformation(name)
        if info is not None:
            return info.GetComponentRange(0)
    C.refuse(f"no {name} array to read a range from")


# ---------------------------------------------------------------------------

def fig_aisles(reader, path):
    """A vertical cut across the aisles -- the hot-aisle / cold-aisle structure.

    The plane is y-z at mid-row. It shows cold supply rising off the tile in the
    cold aisle, the rack row between, and hot discharge climbing the hot aisle
    to the ceiling return. This is the figure a 2-D slice could also produce,
    and it is here so the row-end figure has something to be compared against.
    """
    from paraview.simple import (CellDatatoPointData, Slice, Show, Render,
                                 UpdatePipeline)
    v = build_view()
    p2c = CellDatatoPointData(Input=reader)
    p2c.CellDataArraytoprocess = ["T", "U"]
    UpdatePipeline(time=float(END), proxy=p2c)
    lo, hi = field_range(p2c)

    s = Slice(Input=p2c)
    s.SliceType = "Plane"
    s.SliceType.Origin = [1.5, 0.0, 0.0]        # mid-row, through a rack
    s.SliceType.Normal = [1.0, 0.0, 0.0]
    UpdatePipeline(time=float(END), proxy=s)
    if s.GetDataInformation().GetNumberOfCells() == 0:
        C.refuse("the aisle slice is empty; nothing would be drawn")

    d = Show(s, v)
    colour_by_T(d, v, show_bar=True)
    outline(reader, v)

    # from +x looking back along -x, so +y runs RIGHT on the frame and the
    # caption's 'cold aisle left, hot aisle right' describes the actual picture.
    # Viewed from -x the image is mirrored and that caption is false.
    frame(v, (1.5, ROOM[1] / 2, ROOM[2] / 2), (1.0, 0.0, 0.0), pad=1.10)
    lock_colour_range(v)
    stamp(v, GEOM + " ; y-z plane at x = 1.5 m ; cold aisle left, rack row "
          "centre, hot aisle right ; field T in %.2f to %.2f K, colour bar "
          "%.0f to %.0f K" % (lo, hi, T_LO, T_HI))
    Render(v)
    n = C.save_screenshot(v, path, size=(1600, 1000))
    C.announce(f"  wrote {os.path.basename(path)} ({n:,} bytes)"
               f"  [T range {lo:.2f} to {hi:.2f} K]")
    return n


def fig_row_ends(reader, path):
    """THE figure this case exists for: the spanwise path round the open ends.

    A horizontal x-y plane at rack mid-height, with the in-plane velocity drawn
    as glyphs. The rack row spans x = 0.6 to 3.0; the gaps at x < 0.6 and
    x > 3.0 are the OPEN ROW ENDS, and flow crossing them from the hot aisle
    back into the cold aisle is the three-dimensional path a 2-D slice of this
    room does not possess.
    """
    from paraview.simple import (CellDatatoPointData, Slice, Show, Render,
                                 Glyph, UpdatePipeline)
    v = build_view()
    p2c = CellDatatoPointData(Input=reader)
    p2c.CellDataArraytoprocess = ["T", "U"]
    UpdatePipeline(time=float(END), proxy=p2c)
    lo, hi = field_range(p2c)

    z_mid = RACK_Z1 / 2.0
    s = Slice(Input=p2c)
    s.SliceType = "Plane"
    s.SliceType.Origin = [0.0, 0.0, z_mid]
    s.SliceType.Normal = [0.0, 0.0, 1.0]
    UpdatePipeline(time=float(END), proxy=s)
    if s.GetDataInformation().GetNumberOfCells() == 0:
        C.refuse("the row-end slice is empty; nothing would be drawn")

    d = Show(s, v)
    colour_by_T(d, v, show_bar=True)

    g = Glyph(Input=s, GlyphType="Arrow")
    g.OrientationArray = ["POINTS", "U"]
    g.ScaleArray = ["POINTS", "U"]
    g.ScaleFactor = 0.22
    g.GlyphMode = "Every Nth Point"
    g.Stride = 3
    UpdatePipeline(time=float(END), proxy=g)
    gd = Show(g, v)
    gd.ColorArrayName = [None, ""]
    gd.DiffuseColor = [0.12, 0.12, 0.12]
    gd.AmbientColor = [0.12, 0.12, 0.12]
    gd.Opacity = 0.85

    outline(reader, v)

    frame(v, (ROOM[0] / 2, ROOM[1] / 2, z_mid), (0.0, 0.0, 1.0),
          up=(0.0, 1.0, 0.0), pad=1.08)
    lock_colour_range(v)
    stamp(v, GEOM + " ; x-y plane at z = %.1f m (rack mid-height) ; rack row "
          "spans x = 0.6 to 3.0 m ; the gaps at x below 0.6 and above 3.0 are "
          "the OPEN ROW ENDS ; arrows are in-plane U ; colour bar %.0f to "
          "%.0f K" % (z_mid, T_LO, T_HI))
    Render(v)
    n = C.save_screenshot(v, path, size=(1600, 1000))
    C.announce(f"  wrote {os.path.basename(path)} ({n:,} bytes)")
    return n


def fig_streamlines(reader, path):
    """Streamlines seeded in the hot aisle -- the recirculation, if it is there.

    Seeded across the hot aisle at rack-outlet height and integrated BOTH ways,
    so a line that leaves the hot aisle, rounds a row end and returns to the
    cold aisle is drawn as one continuous path. If no such path exists the
    picture will simply not show one; nothing here forces the conclusion.
    """
    from paraview.simple import (CellDatatoPointData, StreamTracer, Show,
                                 Render, Tube, UpdatePipeline)
    v = build_view()
    p2c = CellDatatoPointData(Input=reader)
    p2c.CellDataArraytoprocess = ["T", "U"]
    UpdatePipeline(time=float(END), proxy=p2c)

    # "High Resolution Line Source" was renamed to "Line" in ParaView 5.7
    # and raises NotSupportedException here rather than silently degrading.
    st = StreamTracer(Input=p2c, SeedType="Line")
    st.Vectors = ["POINTS", "U"]
    st.SeedType.Point1 = [RACK_X0 + 0.05, RACK_Y1 + 0.12, 1.0]
    st.SeedType.Point2 = [RACK_X1 - 0.05, RACK_Y1 + 0.12, 1.0]
    st.SeedType.Resolution = 90
    st.IntegrationDirection = "BOTH"
    st.MaximumStreamlineLength = 40.0
    UpdatePipeline(time=float(END), proxy=st)
    n_pts = st.GetDataInformation().GetNumberOfPoints()
    if n_pts == 0:
        C.refuse("the stream tracer produced no points; an empty frame will "
                 "not be shown")

    tube = Tube(Input=st)
    tube.Scalars = ["POINTS", "T"]
    tube.Vectors = ["POINTS", "U"]
    tube.Radius = 0.012
    UpdatePipeline(time=float(END), proxy=tube)
    d = Show(tube, v)
    colour_by_T(d, v, show_bar=True)

    rack_block(v)
    outline(reader, v)

    frame(v, (ROOM[0] / 2, ROOM[1] / 2, 1.1), (-0.55, -0.80, 0.42), pad=1.06)
    lock_colour_range(v)
    stamp(v, GEOM + " ; streamlines seeded across the hot aisle at the rack "
          "outlets, integrated both ways ; grey body is the rack row as "
          "geometry, not field ; %d points traced ; colour bar %.0f to %.0f K"
          % (n_pts, T_LO, T_HI))
    Render(v)
    n = C.save_screenshot(v, path, size=(1600, 1000))
    C.announce(f"  wrote {os.path.basename(path)} ({n:,} bytes)"
               f"  [{n_pts:,} streamline points]")
    return n


def fig_mesh(reader, path):
    """The mesh, cut at mid-row -- the figure that answers 'is it really 3-D'.

    Crinkle-clipped so whole cells survive: a cut hexahedron renders as a stray
    polygon and reads as a meshing fault that is not there. The cut is MEASURED,
    because a clip that silently kept everything would ship under a caption
    saying it did not.
    """
    from paraview.simple import Clip, Show, Render, UpdatePipeline
    v = build_view()

    full = C.facts(CASE)["cells"]
    clip = Clip(Input=reader)
    clip.ClipType = "Plane"
    clip.ClipType.Origin = [1.8, 0.0, 0.0]
    clip.ClipType.Normal = [1.0, 0.0, 0.0]
    clip.Invert = 1                     # keep x < 1.8, the near half of the row
    clip.Crinkleclip = 1
    UpdatePipeline(time=float(END), proxy=clip)
    kept = clip.GetDataInformation().GetNumberOfCells()
    if not (0.30 * full < kept < 0.75 * full):
        C.refuse(
            f"the mid-row clip kept {kept:,} of {full:,} cells. Cutting the "
            f"room at x = 1.8 m of 3.6 m must keep roughly half; a count "
            f"outside 30-75 % means the clip did not do what this figure's "
            f"caption says it did")

    d = Show(clip, v)
    d.Representation = "Surface With Edges"
    d.ColorArrayName = [None, ""]
    d.DiffuseColor = [0.82, 0.86, 0.91]
    d.AmbientColor = [0.82, 0.86, 0.91]
    d.EdgeColor = [0.24, 0.28, 0.34]
    d.LineWidth = 0.4

    outline(reader, v)
    # From +x, so the camera faces the CUT PLANE at x = 1.8 m. Viewed from -x
    # the cut face is on the far side and the render is a featureless solid
    # block -- which is what shipped first, under a caption promising a notch
    # where the rack void is. The caption was true of the geometry and false of
    # the picture.
    frame(v, (1.5, ROOM[1] / 2, ROOM[2] / 2), (0.62, -0.70, 0.42), pad=1.06)
    stamp(v, GEOM + " ; hexahedral mesh, crinkle-cut at x = 1.8 m ; %s of "
          "%s cells shown ; the notch in the row is the rack void"
          % (f"{kept:,}".replace(",", " "), f"{full:,}".replace(",", " ")))
    Render(v)
    n = C.save_screenshot(v, path, size=(1600, 1000))
    C.announce(f"  wrote {os.path.basename(path)} ({n:,} bytes)"
               f"  [{kept:,} of {full:,} cells]")
    return n


def main() -> int:
    C.announce("=" * 74)
    C.announce("K2bU3R3_D59 renders -- 3-D data centre rack row, 137,000 cells")
    C.announce("=" * 74)
    version = C.assert_paraview_version()
    C.announce(f"  ParaView {version} (pinned {C.REQUIRED_PARAVIEW})")

    # Checked BEFORE any compute. If this stamp ever said PASS the run would
    # stop here, having rendered nothing.
    C.assert_stamp(STAMP, CASE)
    C.announce(f"  stamp accepted: {STAMP}")

    case_dir = C.facts(CASE)["case_dir"]
    before = C.run_tree_fingerprint(case_dir)

    os.makedirs(OUT, exist_ok=True)
    root = None
    total = 0
    try:
        reader, root, n_cells = C.open_case(CASE, ["T", "U"], [END])
        C.announce(f"  t = {END} s: loaded {n_cells:,} cells")
        total += fig_aisles(reader, os.path.join(OUT, "K2bU3R3_temperature_field.png"))
        total += fig_row_ends(reader, os.path.join(OUT, "K2bU3R3_open_row_ends.png"))
        total += fig_streamlines(reader, os.path.join(OUT, "K2bU3R3_recirculation.png"))
        total += fig_mesh(reader, os.path.join(OUT, "K2bU3R3_mesh.png"))
    finally:
        if root:
            shutil.rmtree(root, ignore_errors=True)

    C.assert_run_tree_untouched(case_dir, before)
    C.announce(f"  graded run tree PROVED unchanged: {case_dir}")
    C.announce(f"  {total:,} bytes of imagery written to {OUT}")
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except C.RenderRefusal as exc:
        C.announce_error(f"REFUSED: {exc}")
        rc = 2
    except Exception:                             # noqa: BLE001
        import traceback
        C.announce_error("ERROR: " + traceback.format_exc())
        rc = 3
    sys.stdout.flush()
    os._exit(rc)
