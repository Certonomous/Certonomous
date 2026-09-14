#!/usr/bin/env python3
"""render_k2t_panels.py -- the five ParaView panels of the K2 TRANSIENT set, and
the one mesh figure both K2 demo folders share. RUN WITH pvpython.

    xvfb-run -a pvpython docs/campaigns/F14-cooling-ladder/demo/plots_K2_transient/render_k2t_panels.py

EVERY PANEL IS K2bU3R3_D59 -- the 137,000-cell four-rack room, 80 s transient
record -- and every field on them is the WINDOW MEAN over 50 -> 80 s, which on this
run means the mean of the two written times 60 and 80 (the run carries no
`fieldAverage`; see `k2t_window.py`). The mean is taken by ParaView's own
`TemporalStatistics` over a scratch case holding exactly those two time directories,
and the timestep list is ASSERTED to be [60, 80] before anything is drawn.

    k2t_mesh.png              surface mesh of the four cabinets, the tiles and the
                              floor, ISO. Also written to plots_K2_steady/k2_mesh.png.
    k2t_plane_mid.png         window-mean T at rack mid-height, 27 degC contour, TOP
    k2t_plane_mid_velocity.png window-mean |U| on the same plane, TOP
    k2t_plane_hot.png         window-mean T on the vertical plane through the hot
                              aisle, spanning the row
    k2t_streamlines.png       60 streamlines seeded over all four tiles, coloured
                              by T, ISO

WHAT IS ON EVERY FIELD PANEL, because the order says the reader must see the whole
row: four cabinets as grey blocks, the floor outlined, the four tiles outlined and
the four ceiling return openings outlined. All of that is GEOMETRY, drawn from the
builders' own constants (`build_k2b.py`, `build_k2bU3.py` via `render_k2bU3R3.py`),
never from field data.

NOTHING IS WRITTEN ON ANY IMAGE. White ground, no orientation triad, one colour bar
a quarter of the frame high titled by symbol and unit. Temperature is in degC on the
figures and the fields are in K, so a Calculator subtracts 273.15 -- the bar's range
is the order's 16 to 33 degC and |U| 0 to 1.5 m/s on every panel.

THE COLD AISLE IS AT LOW y, AND THAT IS READ, NOT ASSUMED. `k2t_window` reads the
`tile` patch face centres off the mesh and this module ASSERTS they lie below the
rack row's y before the TOP camera is pointed; the TOP view is then set up so that
+y is up in the image, which puts the cold aisle at the bottom and the hot aisle at
the top as ordered.

Planted colour control on every coloured panel, at the 8x margin the other demo
folders use: the same frame is rendered first with a CONSTANT array, and the panel
is REFUSED unless the real field's colour spread beats it by 8x over at least
20,000 painted pixels (CLAUDE.md rule 3).
"""
import os
import shutil
import sys

REPO = "/home/ubuntu/Certonomous"
HERE = os.path.dirname(os.path.abspath(__file__))
STEADY = os.path.join(REPO, "docs/campaigns/F14-cooling-ladder/demo/plots_K2_steady")
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(REPO, "sdk"))
sys.path.insert(0, os.path.join(REPO, "docs/campaigns/F14-cooling-ladder/demo/render_K2bU3R3_paraview"))
sys.path.insert(0, os.path.join(REPO, "verification/runs/F14-cooling-ladder/K2h_runs"))
sys.path.insert(0, HERE)

import demo3d_render_common as C                      # noqa: E402
from workflows.act_paraview_style import style_view, colour_bar   # noqa: E402
import render_k2bU3R3 as K2B                          # geometry constants  # noqa: E402
import render_k2h_l3 as K2H                           # _colour_spread      # noqa: E402
import k2t_window as W                                # the window definition

CASE = "K2bU3R3_D59"
TIMES = ["60", "80"]
SIZE = (1600, 1000)

ROOM = K2B.ROOM                       # 3.6 x 3.5 x 2.7 m
RACK_Y0, RACK_Y1 = K2B.RACK_Y0, K2B.RACK_Y1          # 1.2, 2.3
RACK_Z1 = K2B.RACK_Z1                                # 2.0
TILE_Y0, TILE_Y1 = K2B.COLD_Y0, K2B.COLD_Y1          # 0.6, 1.2
RET_Y0, RET_Y1 = K2B.RETURN_Y0, K2B.RETURN_Y1        # 2.6, 3.2
RACK_X = W.RACK_X                                    # four 0.6 m columns, 0.6 -> 3.0
Z_MID = RACK_Z1 / 2.0                                # 1.0 m
HOT_Y = (RACK_Y1 + ROOM[1]) / 2.0                    # 2.9 m, mid hot aisle

T_LO_C, T_HI_C = 16.0, 33.0           # degC, the order's range, every panel
U_LO, U_HI = 0.0, 1.5                 # m/s, the order's range, every panel
T_ISO_C = 27.0                        # the one limit contour
PRESET_T = "Cool to Warm"
PRESET_U = "Viridis (matplotlib)"
CONTROL_MARGIN = 8.0
MIN_FIELD_PX = 20000

GREY = [0.62, 0.64, 0.68]
LINE = [0.22, 0.24, 0.28]

#: Camera directions. `direction` is the offset FROM the focal point TO the camera,
#: so the view runs the other way -- the convention of C.frame_by_extent.
CAM_TOP = ((0.0, 0.0, 1.0), (0.0, 1.0, 0.0))          # down; +y up in frame
CAM_ISO = ((-0.55, -0.80, 0.42), (0.0, 0.0, 1.0))     # three-quarter, cold side
CAM_HOT = ((0.0, 1.0, 0.0), (0.0, 0.0, 1.0))          # normal to the hot-aisle plane


# --------------------------------------------------------------------------
def view():
    from paraview.simple import CreateRenderView, SetActiveView, Render
    v = CreateRenderView()
    SetActiveView(v)
    style_view(v, SIZE)
    Render(v)
    return v


def assert_cold_aisle_is_low_y():
    """READ which side is cold, never assume it. The tile patch is the supply."""
    c = W.Case()
    tile = c.centres("tile")
    if tile[:, 1].max() >= RACK_Y0:
        C.refuse("the `tile` patch reaches y = %.3f, at or beyond the rack row's "
                 "y = %.3f: the cold aisle is NOT the low-y side of this mesh and "
                 "the TOP camera would put it at the wrong edge of the frame"
                 % (tile[:, 1].max(), RACK_Y0))
    ret = c.centres("return")
    if ret[:, 1].min() <= RACK_Y1:
        C.refuse("the `return` patch reaches y = %.3f, at or below the rack row's "
                 "y = %.3f; the hot aisle is not the high-y side"
                 % (ret[:, 1].min(), RACK_Y1))
    C.announce("  cold aisle READ from the mesh: `tile` spans y %.2f to %.2f, "
               "`return` spans y %.2f to %.2f, rack row y %.2f to %.2f -> cold is "
               "low y, hot is high y"
               % (tile[:, 1].min(), tile[:, 1].max(), ret[:, 1].min(),
                  ret[:, 1].max(), RACK_Y0, RACK_Y1))


def flat_outline(v, x0, x1, y0, y1, z, width=2.4, xz=None):
    """A flat rectangle drawn as an outline.

    Normally a z = const rectangle (x0..x1, y0..y1). `xz` instead draws an
    x-z rectangle (x0..x1, xz[0]..xz[1]) at the constant y given by `z`.
    """
    from paraview.simple import Box, Show
    b = Box()
    b.XLength = x1 - x0
    if xz is None:
        b.YLength = y1 - y0
        b.ZLength = 0.0
        b.Center = [(x0 + x1) / 2.0, (y0 + y1) / 2.0, z]
    else:
        b.YLength = 0.0
        b.ZLength = xz[1] - xz[0]
        b.Center = [(x0 + x1) / 2.0, z, (xz[0] + xz[1]) / 2.0]
    d = Show(b, v)
    d.Representation = "Outline"
    d.AmbientColor = LINE
    d.DiffuseColor = LINE
    d.LineWidth = width
    return b


def cabinet(v, x0, x1, edges=True):
    from paraview.simple import Box, Show
    b = Box()
    b.XLength = x1 - x0
    b.YLength = RACK_Y1 - RACK_Y0
    b.ZLength = RACK_Z1
    b.Center = [(x0 + x1) / 2.0, (RACK_Y0 + RACK_Y1) / 2.0, RACK_Z1 / 2.0]
    d = Show(b, v)
    d.Representation = "Surface With Edges" if edges else "Surface"
    d.ColorArrayName = [None, ""]
    d.AmbientColor = GREY
    d.DiffuseColor = GREY
    d.EdgeColor = LINE
    d.LineWidth = 1.6
    d.Opacity = 1.0
    return b


def cabinet_outline(v, x0, x1):
    """The cabinet's own edges, so four adjacent 0.6 m cabinets read as FOUR."""
    from paraview.simple import Box, Show
    b = Box()
    b.XLength = x1 - x0
    b.YLength = RACK_Y1 - RACK_Y0
    b.ZLength = RACK_Z1
    b.Center = [(x0 + x1) / 2.0, (RACK_Y0 + RACK_Y1) / 2.0, RACK_Z1 / 2.0]
    d = Show(b, v)
    d.Representation = "Outline"
    d.AmbientColor = LINE
    d.DiffuseColor = LINE
    d.LineWidth = 2.0
    return b


def the_row_on_plane(v, y):
    """The row drawn IN a vertical cut plane, as an elevation projection at `y`.

    The hot-aisle cut sits at y = 2.9 m and the cabinets at y = 1.2 to 2.3 m, so on
    a face-on view of that cut the row is BEHIND the field and is not visible at
    all -- the first render of `k2t_plane_hot.png` came out with no geometry on it
    whatsoever. Painting the cabinets as grey blocks in the cut's own plane would
    hide the field where the row is NOT, which is worse: the hot aisle is exactly
    where this panel's physics lives. So the row is drawn here as its ELEVATION
    OUTLINE -- four cabinet footprints, the floor line, the four tile footprints and
    the four return openings, each at its true x and z -- 2 mm in front of the cut.
    It marks where the row is; it paints nothing over the field. SIDECAR.md says so
    on this figure's row.
    """
    # CAM_HOT places the camera at LARGE y looking towards -y, so "in front of the
    # cut" is y + eps. Drawn at y - eps the outlines sat BEHIND the plane and the
    # panel came out with no geometry on it at all -- measured, first render.
    yy = y + 0.002
    flat_outline(v, 0.0, ROOM[0], 0, 0, yy, width=2.0, xz=(0.0, ROOM[2]))   # room
    for x0, x1 in RACK_X:
        flat_outline(v, x0, x1, 0, 0, yy, xz=(0.0, RACK_Z1))                # cabinet
        flat_outline(v, x0, x1, 0, 0, yy, xz=(0.0, 0.012))                  # tile
        flat_outline(v, x0, x1, 0, 0, yy, xz=(ROOM[2] - 0.012, ROOM[2]))    # return


def the_row(v, cabinets=True, project_z=None, returns=True, lift=0.0):
    """The whole row: four cabinets, the floor, the four tiles, the four returns.

    `project_z` DRAWS THE FLOOR AND TILE OUTLINES AT THAT HEIGHT INSTEAD OF AT THE
    FLOOR, and it exists for one measured reason. On the TOP panels the cut is at
    z = 1.0 m and the tiles are at z = 0, so in an orthographic view looking down
    the cut sits between the camera and the tiles and HIDES THEM COMPLETELY -- the
    first render of `k2t_plane_mid.png` showed the return openings (above the cut)
    and no tiles at all. A plan view carries no depth, so the outline is drawn in
    the cut's own plane as a PLAN PROJECTION of the tile footprint; it marks where
    the tile is in x and y, which is exactly what it marks at z = 0. This is stated
    on those figures' rows in SIDECAR.md. Nothing else is moved, and no field value
    is touched.
    """
    if cabinets:
        for x0, x1 in RACK_X:
            cabinet(v, x0, x1)
    else:
        for x0, x1 in RACK_X:
            cabinet_outline(v, x0, x1)
    z_floor = project_z if project_z is not None else lift
    flat_outline(v, 0.0, ROOM[0], 0.0, ROOM[1], z_floor, width=2.0)       # floor
    for x0, x1 in RACK_X:
        flat_outline(v, x0, x1, TILE_Y0, TILE_Y1, z_floor)                # tiles
        if returns:
            flat_outline(v, x0, x1, RET_Y0, RET_Y1, ROOM[2])              # return


def bar(v, lut, title):
    return colour_bar(v, lut, title)


def frame(v, cam, focal=None, bounds=None, pad=1.06):
    direction, up = cam
    if focal is None:
        focal = (ROOM[0] / 2.0, ROOM[1] / 2.0, ROOM[2] / 2.0)
    if bounds is None:
        bounds = (0.0, ROOM[0], 0.0, ROOM[1], 0.0, ROOM[2])
    return C.frame_by_extent(v, focal, direction, up=up, bounds=bounds, pad=pad,
                             bottom_band=0.0)


def control(pos, neg, what):
    p, npx = K2H._colour_spread(pos)
    n, _ = K2H._colour_spread(neg)
    if npx < MIN_FIELD_PX:
        C.refuse("BLANK FRAME for %r: the positive arm covers only %s pixels, "
                 "below the %s floor" % (what, format(npx, ","), format(MIN_FIELD_PX, ",")))
    if n <= 0.0:
        C.refuse("NO CONTROL for %r: the constant-array arm spread is exactly zero" % what)
    C.announce("      colour control %s: %.5f over %s px against a CONSTANT array's "
               "%.5f, ratio %.1fx (floor %gx)"
               % (what, p, format(npx, ","), n, p / max(n, 1e-9), CONTROL_MARGIN))
    if p < CONTROL_MARGIN * max(n, 1e-9):
        C.refuse("COLOUR CONTROL FAILED for %r: %.5f against %.5f" % (what, p, n))


def ctrl_path(out, arm):
    return os.path.join(os.path.dirname(out), "_control", arm + os.path.basename(out))


# --------------------------------------------------------------------------
def mean_fields(reader):
    """TemporalStatistics over EXACTLY the two written times, as point data."""
    from paraview.simple import TemporalStatistics, CellDatatoPointData, UpdatePipeline
    ts = list(reader.TimestepValues)
    if [float(x) for x in ts] != [float(t) for t in TIMES]:
        C.refuse("the scratch case offers timesteps %r where the window mean needs "
                 "exactly %r; an average over the wrong set is not the ordered "
                 "window" % (ts, TIMES))
    st = TemporalStatistics(Input=reader)
    st.ComputeMinimum = 0
    st.ComputeMaximum = 0
    st.ComputeStandardDeviation = 0
    UpdatePipeline(proxy=st)
    p2c = CellDatatoPointData(Input=st)
    p2c.CellDataArraytoprocess = ["T_average", "U_average"]
    UpdatePipeline(proxy=p2c)
    return p2c


def scalar(src, name, expr):
    from paraview.simple import Calculator, UpdatePipeline
    c = Calculator(Input=src)
    c.AttributeType = "Point Data"
    c.ResultArrayName = name
    c.Function = expr
    UpdatePipeline(proxy=c)
    return c


def plane_panel(src, out, name, expr, preset, rng, title, cut, cam,
                contour_at=None):
    """One cut plane over the WHOLE room, with the row drawn and the control armed."""
    from paraview.simple import (Slice, Contour, Show, Hide, Render, ColorBy,
                                 GetColorTransferFunction, Calculator, UpdatePipeline)
    axis, at = cut
    v = view()
    calc = scalar(src, name, expr)
    s = Slice(Input=calc)
    s.SliceType = "Plane"
    if axis == "z":
        s.SliceType.Origin = [0.0, 0.0, at]; s.SliceType.Normal = [0.0, 0.0, 1.0]
        bounds = (0.0, ROOM[0], 0.0, ROOM[1], at, at)
        focal = (ROOM[0] / 2.0, ROOM[1] / 2.0, at)
    else:
        s.SliceType.Origin = [0.0, at, 0.0]; s.SliceType.Normal = [0.0, 1.0, 0.0]
        bounds = (0.0, ROOM[0], at, at, 0.0, ROOM[2])
        focal = (ROOM[0] / 2.0, at, ROOM[2] / 2.0)
    UpdatePipeline(proxy=s)
    if s.GetDataInformation().GetNumberOfCells() == 0:
        C.refuse("the %s = %g plane is empty; nothing would be drawn" % (axis, at))

    flat = Calculator(Input=s)
    flat.AttributeType = "Point Data"
    flat.ResultArrayName = "CONTROL_CONSTANT"
    flat.Function = "1.0"
    UpdatePipeline(proxy=flat)
    a = flat.GetPointDataInformation().GetArray("CONTROL_CONSTANT")
    lo, hi = a.GetComponentRange(0)
    if abs(hi - lo) > 1e-12:
        C.refuse("the control array spans %g to %g and is not constant" % (lo, hi))
    dn = Show(flat, v)
    ColorBy(dn, ("POINTS", "CONTROL_CONSTANT"))
    dn.SetScalarBarVisibility(v, False)
    frame(v, cam, focal=focal, bounds=bounds)
    Render(v)
    neg = ctrl_path(out, "NEGATIVE_constant_")
    C.save_screenshot(v, neg, size=SIZE)
    Hide(flat, v)

    d = Show(s, v)
    ColorBy(d, ("POINTS", name))
    lut = GetColorTransferFunction(name)
    lut.ApplyPreset(preset, True)
    lut.RescaleTransferFunction(*rng)
    d.SetScalarBarVisibility(v, True)
    bar(v, lut, title)
    Render(v)
    pos = ctrl_path(out, "POSITIVE_uncaptioned_")
    C.save_screenshot(v, pos, size=SIZE)
    control(pos, neg, name)

    if contour_at is not None:
        cont = Contour(Input=s)
        cont.ContourBy = ["POINTS", name]
        cont.Isosurfaces = [contour_at]
        UpdatePipeline(proxy=cont)
        n = cont.GetDataInformation().GetNumberOfCells()
        C.announce("      %g contour: %s segments" % (contour_at, format(n, ",")))
        if n == 0:
            C.refuse("the %g contour is empty on this plane and the order asks for "
                     "it drawn; refusing to ship the panel without it" % contour_at)
        cd = Show(cont, v)
        cd.ColorArrayName = [None, ""]
        cd.AmbientColor = [0.05, 0.05, 0.05]
        cd.DiffuseColor = [0.05, 0.05, 0.05]
        cd.LineWidth = 2.6

    if axis == "z":
        the_row(v, project_z=at + 0.002)
    else:
        the_row_on_plane(v, at)
    lut.RescaleTransferFunction(*rng)
    frame(v, cam, focal=focal, bounds=bounds)
    Render(v)
    got = list(lut.RGBPoints)[0], list(lut.RGBPoints)[-4]
    if abs(got[0] - rng[0]) > 1e-9 or abs(got[1] - rng[1]) > 1e-9:
        C.refuse("the colour bar spans %g to %g where the order says %g to %g"
                 % (got[0], got[1], rng[0], rng[1]))
    nb = C.save_screenshot(v, out, size=SIZE)
    C.announce("  wrote %s (%s bytes)" % (os.path.basename(out), format(nb, ",")))
    return nb


def streamlines_panel(src, out, title):
    """60 streamlines seeded over ALL FOUR tiles, coloured by temperature, ISO."""
    from paraview.simple import (StreamTracerWithCustomSource, Plane, Tube, Show,
                                 Render, ColorBy, GetColorTransferFunction,
                                 UpdatePipeline)
    v = view()
    calc = scalar(src, "T_C", "T_average - 273.15")
    seed = Plane()
    seed.Origin = [RACK_X[0][0] + 0.03, W.T_SUP * 0 + K2B.COLD_Y0 + 0.03, 0.03]
    seed.Point1 = [RACK_X[-1][1] - 0.03, K2B.COLD_Y0 + 0.03, 0.03]
    seed.Point2 = [RACK_X[0][0] + 0.03, K2B.COLD_Y1 - 0.03, 0.03]
    seed.XResolution = 9          # 10 x 6 = 60 seed points, over all four tiles
    seed.YResolution = 5
    UpdatePipeline(proxy=seed)
    npts = seed.GetDataInformation().GetNumberOfPoints()
    if npts != 60:
        C.refuse("the tile seed carries %d points where the order asks for 60" % npts)
    st = StreamTracerWithCustomSource(Input=calc, SeedSource=seed)
    st.Vectors = ["POINTS", "U_average"]
    st.MaximumStreamlineLength = 25.0
    UpdatePipeline(proxy=st)
    if st.GetDataInformation().GetNumberOfPoints() == 0:
        C.refuse("no streamline was integrated from the tile seed")
    tube = Tube(Input=st)
    tube.Radius = 0.012
    UpdatePipeline(proxy=tube)
    d = Show(tube, v)
    ColorBy(d, ("POINTS", "T_C"))
    lut = GetColorTransferFunction("T_C")
    lut.ApplyPreset(PRESET_T, True)
    lut.RescaleTransferFunction(T_LO_C, T_HI_C)
    d.SetScalarBarVisibility(v, True)
    bar(v, lut, title)
    the_row(v)
    frame(v, CAM_ISO)
    Render(v)
    nb = C.save_screenshot(v, out, size=SIZE)
    _, npx = K2H._colour_spread(out)
    if npx < MIN_FIELD_PX:
        C.refuse("%s drew only %s body pixels" % (os.path.basename(out), format(npx, ",")))
    C.announce("  wrote %s (%s bytes, %s px of ink, %d seeds)"
               % (os.path.basename(out), format(nb, ","), format(npx, ","), npts))
    return nb


def mesh_panel(root, outs):
    """The SURFACE MESH -- real cell edges -- of the four cabinets, the tiles and
    the floor, ISO. The cabinets are VOIDS in this mesh, so their surface is the
    rack patches themselves: rack{i}_in, rack{i}_out, rack_top and rack_end."""
    from paraview.simple import OpenFOAMReader, Show, Render, UpdatePipeline
    v = view()
    foam = os.path.join(root, "%s.foam" % CASE)
    r = OpenFOAMReader(FileName=foam)
    want = ["patch/floor", "patch/tile"] + \
           ["patch/rack%d_in" % i for i in range(4)] + \
           ["patch/rack%d_out" % i for i in range(4)] + \
           ["patch/rack_top", "patch/rack_end"]
    have = set(r.MeshRegions.Available)
    missing = [w for w in want if w not in have]
    if missing:
        C.refuse("the reader does not offer %r; the mesh figure will not be drawn "
                 "from a substitute surface" % missing)
    r.MeshRegions = want
    r.CellArrays = []
    UpdatePipeline(time=80.0, proxy=r)
    ncell = r.GetDataInformation().GetNumberOfCells()
    if ncell < 1000:
        C.refuse("the patch surface carries %d faces; that is not the four-rack "
                 "row's mesh" % ncell)
    d = Show(r, v)
    d.Representation = "Surface With Edges"
    d.ColorArrayName = [None, ""]
    d.AmbientColor = GREY
    d.DiffuseColor = GREY
    d.EdgeColor = LINE
    d.LineWidth = 1.0
    # The cabinets ARE the mesh here, so they are outlined rather than filled;
    # the tile and floor outlines are lifted 12 mm off z = 0 because an outline
    # coplanar with the floor patch z-fights with it and disappears.
    the_row(v, cabinets=False, returns=False, lift=0.012)
    frame(v, CAM_ISO, focal=(ROOM[0] / 2.0, ROOM[1] / 2.0, RACK_Z1 / 2.0),
          bounds=(0.0, ROOM[0], 0.0, ROOM[1], 0.0, RACK_Z1))
    Render(v)
    first = outs[0]
    nb = C.save_screenshot(v, first, size=SIZE)
    _, npx = K2H._colour_spread(first)
    if npx < MIN_FIELD_PX:
        C.refuse("the mesh figure drew only %s pixels of ink" % format(npx, ","))
    for other in outs[1:]:
        shutil.copyfile(first, other)
        C.verify_written_image(other)
    C.announce("  wrote %s (%s bytes, %s px of ink, %s patch faces) and copied to %s"
               % (os.path.basename(first), format(nb, ","), format(npx, ","),
                  format(ncell, ","), ", ".join(os.path.basename(o) for o in outs[1:])))
    return nb


# --------------------------------------------------------------------------
PROV = os.path.join(HERE, "PROVENANCE.tsv")
PANEL_FIGS = ("k2t_mesh.png", "k2t_plane_mid.png", "k2t_plane_mid_velocity.png",
              "k2t_plane_hot.png", "k2t_streamlines.png")
WINDOW_WORDS = "50 to 80 s: mean of written times 60, 80"


def sha(p):
    import hashlib
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def write_provenance():
    """Keep every row this renderer did not draw, and rewrite its own."""
    kept = []
    if os.path.isfile(PROV):
        with open(PROV) as f:
            head = f.readline()
            for ln in f:
                if ln.split("\t")[0] not in PANEL_FIGS:
                    kept.append(ln.rstrip("\n"))
    else:
        head = ("figure\trun\tartifact\ttime_dir\twindow\tpatches\tcamera\t"
                "colour_range\tsha256")
    cd = W.CASE
    rows = []
    mesh_art = os.path.join(cd, "constant", "polyMesh", "owner")
    rows.append(("k2t_mesh.png", CASE, mesh_art, "constant", "-",
                 "floor, tile, rack0..3_in, rack0..3_out, rack_top, rack_end",
                 "ISO (three-quarter from the cold-aisle side)", "-"))
    for fig, field, rng, cam in (
            ("k2t_plane_mid.png", "T", "T 16 to 33 degC", "TOP (cold aisle at the foot of the frame)"),
            ("k2t_plane_mid_velocity.png", "U", "U 0 to 1.5 m/s", "TOP (cold aisle at the foot of the frame)"),
            ("k2t_plane_hot.png", "T", "T 16 to 33 degC", "hot-aisle plane normal (along -y from the hot side)"),
            ("k2t_streamlines.png", "T", "T 16 to 33 degC", "ISO (three-quarter from the cold-aisle side)")):
        for t in TIMES:
            rows.append((fig, CASE, os.path.join(cd, t, field), t, WINDOW_WORDS,
                         "tile, return, rack0..3_in, rack0..3_out (geometry only)",
                         cam, rng))
        if fig == "k2t_streamlines.png":
            for t in TIMES:
                rows.append((fig, CASE, os.path.join(cd, t, "U"), t, WINDOW_WORDS,
                             "tile (60 seed points)", cam, rng))
    with open(PROV, "w") as f:
        f.write(head.rstrip("\n") + "\n")
        for ln in kept:
            f.write(ln + "\n")
        for r in rows:
            f.write("\t".join(list(r) + [sha(r[2])]) + "\n")
    C.announce("  PROVENANCE.tsv: %d kept rows, %d panel rows" % (len(kept), len(rows)))


def main():
    C.assert_paraview_version()
    C.announce("K2 transient panels: %s, window %s s from written times %s"
               % (CASE, W.WINDOW, ", ".join(TIMES)))
    assert_cold_aisle_is_low_y()
    before = C.run_tree_fingerprint(W.CASE)
    reader, root, ncells = C.open_case(CASE, ("T", "U"), TIMES, time_value=80.0)
    C.announce("  opened %s: %s cells, timesteps %r"
               % (CASE, format(ncells, ","), list(reader.TimestepValues)))
    src = mean_fields(reader)

    T_TITLE = "T (degC)"
    U_TITLE = "U (m/s)"
    try:
        mesh_panel(root, [os.path.join(HERE, "k2t_mesh.png"),
                          os.path.join(STEADY, "k2_mesh.png")])
        plane_panel(src, os.path.join(HERE, "k2t_plane_mid.png"), "T_C",
                    "T_average - 273.15", PRESET_T, (T_LO_C, T_HI_C), T_TITLE,
                    ("z", Z_MID), CAM_TOP, contour_at=T_ISO_C)
        plane_panel(src, os.path.join(HERE, "k2t_plane_mid_velocity.png"), "Umag",
                    "mag(U_average)", PRESET_U, (U_LO, U_HI), U_TITLE,
                    ("z", Z_MID), CAM_TOP)
        plane_panel(src, os.path.join(HERE, "k2t_plane_hot.png"), "T_C",
                    "T_average - 273.15", PRESET_T, (T_LO_C, T_HI_C), T_TITLE,
                    ("y", HOT_Y), CAM_HOT, contour_at=T_ISO_C)
        streamlines_panel(src, os.path.join(HERE, "k2t_streamlines.png"), T_TITLE)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    write_provenance()
    C.assert_run_tree_untouched(W.CASE, before)
    C.announce("the graded run tree is unchanged; five panels and the mesh figure "
               "are written.")


if __name__ == "__main__":
    main()
