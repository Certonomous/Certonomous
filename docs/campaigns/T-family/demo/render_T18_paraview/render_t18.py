#!/usr/bin/env python3
"""render_t18.py -- ParaView renders of T18_CU_f, the lab's 3-D transient
conduction case. RUN WITH pvpython.

    xvfb-run -a pvpython docs/campaigns/T-family/demo/render_T18_paraview/render_t18.py

WHAT THIS CASE IS, AND THE DECLARATION THAT IS NOT OPTIONAL
-----------------------------------------------------------
T18_CU_f is 512,000 cells (80 x 80 x 80), laplacianFoam, transient conduction to
Fo = 0.2. It is one of exactly two genuinely three-dimensional solved cases the
lab owns whose verdict permits it to be shown as a verified result, and until
this script it had no rendered asset at all.

**THE SOLVED DOMAIN IS AN OCTANT, NOT A CUBE.** ``build_t18.py`` lines 4-6 and
``T18_registered.json`` /physics/L_half_side_m are explicit: the mesh spans
0..L in each direction with L = 0.01 m, carrying ZERO-GRADIENT SYMMETRY PLANES
at x = 0, y = 0 and z = 0 and CONVECTIVE ROBIN FACES at x = L, y = L and z = L.
The physical body it represents is a cube of side 2L with six Robin faces; the
solve has three Robin faces and three symmetry planes.

That distinction is this case's version of Act A's wedge, and it is handled the
same way. Act A's ``_actA_render_common.py`` carries two declarations --
``AXISYMMETRY_PLANE_LINE`` for the solved plane and ``AXISYMMETRY_REVOLVE_LINE``
for the 360-degree display body -- with the comment that stamping the revolve
sentence on a plane view "would be false in the opposite direction". So this
module carries the same pair:

* :data:`OCTANT_AS_SOLVED` goes on every view of the octant as solved;
* :data:`OCTANT_MIRRORED` goes on the ONE view that mirrors it into the full
  cube for legibility.

Mirroring is permitted. SILENT mirroring is not, and captioning a mirrored cube
with "six Robin faces" would claim a solve that never happened.

AND THE ASSERTION THAT EARNED ITS PLACE ON THE FIRST RUN
--------------------------------------------------------
The first version of this script captioned the mesh figure "corner removed to
show the interior" and rendered an UNCUT cube: ParaView's Box clip takes
``Position`` as the box CENTRE, not its minimum corner, so the box swallowed the
whole domain and the clip removed nothing. The caption was false and the picture
was plausible -- the precise failure Act A's declaration pair exists to prevent,
arriving through geometry rather than through a verdict word.

A caption is not evidence. So :func:`corner_cutaway` MEASURES the cut: it
asserts the clipped cell count against the count the geometry implies
(512,000 - 40 x 40 x 40 = 448,000) and REFUSES if the corner is still there.
The figure now cannot ship with that caption unless the corner actually went.

THE VERDICT
-----------
Graded rows G1, G2 and G3 are PASS (``T18_GRADE_OUTPUT_20260831T151113Z.txt``).
The rung's registered ceiling is GATE REACHED (``T18_registered.json``
/ceiling): the reference is an EXACT analytic series, so the rung scores V and
never P. Both halves are stamped, and neither is upgraded. The reference being
an analytic series is also why nothing here may be called validation -- there is
no experiment in this rung, and ``assert_stamp`` refuses the word.

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

# The SAME frozen analytic reference the grade used, imported rather than
# re-derived. It is what assert_rendered_time() measures the picture against.
sys.path.insert(0, os.path.join(REPO, "verification", "runs", "T-family",
                                "T18_runs"))
from exact_t18 import Series        # noqa: E402

CASE = "T18_CU_f"
OUT = os.path.join(REPO, "docs", "campaigns", "T-family", "demo", "figures_T18")

L = 0.01            # m, half-side; T18_registered.json /physics/L_half_side_m
N = 80              # cells per side on the fine level
FO = {"1": 0.1, "2": 0.2}          # alpha t / L^2 with alpha = 1e-5, L = 0.01

#: One colour range for EVERY theta figure, so the Fo = 0.1 and Fo = 0.2 panels
#: are comparable and the front is seen to move rather than the colour bar. The
#: bounds are the analytic extremes over the two rendered times, from
#: exact_t18.Series: theta(0,0,0 ; Fo=0.1) = 0.9795 and
#: theta(1,1,1 ; Fo=0.2) = 0.2663. Stated in every caption that uses it.
THETA_LO, THETA_HI = 0.26, 0.98

#: THE DECLARATION MUST DESCRIBE THE PICTURE ACTUALLY DRAWN, so there are two.
OCTANT_AS_SOLVED = ("Octant as solved ; symmetry at x=0 y=0 z=0 ; "
                    "Robin faces at x=L y=L z=L ; L=0.010 m")
OCTANT_MIRRORED = ("Octant solved ; mirrored to the full cube of side 2L ; "
                   "display only")

STAMP = ("T18_CU_f ; 512000 cells (80 x 80 x 80) ; laplacianFoam ; "
         "rows G1 G2 G3: PASS ; rung ceiling: GATE REACHED")

SCALE = "theta range on the colour bar: %.2f to %.2f" % (THETA_LO, THETA_HI)

#: The frozen analytic series, Bi = 1 (T18_registered.json /physics/Bi).
SERIES = Series(1.0)


def build_view(time_value: float, size=(1500, 1000)):
    """A view pinned to an EXPLICIT time.

    ``ViewTime`` is set here because ParaView renders at the VIEW's time, not at
    whatever time some upstream proxy was last updated with. Leaving it default
    is how the Fo = 0.2 isosurface figure came to be drawn from Fo = 0.1 data --
    see :func:`assert_rendered_time`.
    """
    from paraview.simple import CreateRenderView, SetActiveView
    v = CreateRenderView()
    SetActiveView(v)
    C.white_background(v)
    v.ViewSize = list(size)
    v.ViewTime = float(time_value)
    return v


#: Relative tolerance on the time check. The two rendered times differ by 14 %
#: in peak theta (0.9795 vs 0.8591), so 1e-3 separates them by two orders of
#: magnitude while comfortably admitting the ~5e-5 discretisation offset
#: measured between the fine mesh and the analytic series.
TIME_CHECK_RTOL = 1e-3


def assert_rendered_time(src, time_dir: str, what: str):
    """PROVE the data about to be drawn is the time the caption claims.

    THIS ASSERTION EXISTS BECAUSE THE BUG HAPPENED. ``UpdatePipeline(proxy=...)``
    with no ``time`` argument resolves to the pipeline's first timestep, not to
    the time the reader was opened at. The isosurface figure captioned
    "Fo = 0.2" was therefore built from the Fo = 0.1 field: it rendered, it
    looked entirely correct, and the only outward sign was that the two
    supposedly different PNGs came out three bytes apart.

    The check is against the frozen analytic reference, not against a number
    typed here: theta at the cube centre is f(0,Fo)^3 from exact_t18.Series,
    and the peak cell value of a converged fine mesh must sit on it.
    """
    di = src.GetDataInformation()
    for assoc in ("cell", "point"):
        info = (di.GetCellDataInformation() if assoc == "cell"
                else di.GetPointDataInformation()).GetArrayInformation("T")
        if info is not None:
            lo, hi = info.GetComponentRange(0)
            break
    else:
        C.refuse(f"{what}: no T array to check the rendered time against")

    fo = FO[time_dir]
    want = SERIES.theta(0.0, 0.0, 0.0, fo)      # peak theta, at the origin
    if abs(hi - want) > TIME_CHECK_RTOL * want:
        other = {k: SERIES.theta(0.0, 0.0, 0.0, v) for k, v in FO.items()}
        C.refuse(
            f"{what} is captioned Fo = {fo}, whose analytic peak theta is "
            f"{want:.6f}, but the data about to be drawn peaks at {hi:.6f}. "
            f"The peaks of the available times are {other}. This figure would "
            f"have shipped showing the wrong time under a correct-looking "
            f"caption -- which is exactly what happened before this check "
            f"existed")
    return lo, hi


def colour_by_theta(disp, view, show_bar=False):
    from paraview.simple import ColorBy, GetColorTransferFunction, GetScalarBar
    ColorBy(disp, ("POINTS", "T"))
    lut = GetColorTransferFunction("T")
    # Cool to Warm, not Inferno: this field spans theta 0.27 to 0.86 and
    # Inferno spends its bottom third in near-black, which rendered the Robin
    # faces as an unreadable dark mass on a white page. A diverging blue-to-red
    # map keeps both ends bright and is the conventional reading for a thermal
    # front. The MAPPING is unchanged -- only its legibility.
    lut.ApplyPreset("Cool to Warm", True)
    lut.RescaleTransferFunction(THETA_LO, THETA_HI)
    disp.SetScalarBarVisibility(view, bool(show_bar))
    if show_bar:
        bar = GetScalarBar(lut, view)
        bar.Visibility = 1
        bar.Title = "theta"
        bar.ComponentTitle = ""
        bar.TitleColor = [0.15, 0.15, 0.15]
        bar.LabelColor = [0.15, 0.15, 0.15]
        bar.TitleFontSize = 11
        bar.LabelFontSize = 10
        bar.ScalarBarLength = 0.33
        bar.ScalarBarThickness = 12
        bar.WindowLocation = "Any Location"
        bar.Position = [0.855, 0.34]
        bar.AutomaticLabelFormat = 0
        bar.LabelFormat = "%-#.2f"
        bar.AddRangeLabels = 1
    return lut


def isometric(view, focal, pad=1.06, direction=(1.0, 1.0, 0.62),
              bounds=(0.0, L, 0.0, L, 0.0, L), bottom_band=0.09):
    """Frame the octant through the shared, asserted framer.

    This used to take a hand-typed parallel scale and set it before a single
    Render. Both halves were wrong: the number was a guess, and a fresh view's
    FIRST render performs an automatic reset that overwrote it, so every T18
    figure was in fact framed by that reset rather than by the value beside it.
    See demo3d_render_common.frame_by_extent.
    """
    return C.frame_by_extent(view, focal, direction, up=(0.0, 0.0, 1.0),
                             pad=pad, bounds=bounds, bottom_band=bottom_band)


def stamp(view, second_line: str):
    """The verdict stamp, plus the geometry declaration for THIS picture."""
    C.caption(view, STAMP, CASE, position=(0.015, 0.048), size=11)
    C.caption(view, second_line, CASE, position=(0.015, 0.018), size=9,
              check_stamp=False)


def outline(src, view):
    from paraview.simple import Outline, Show
    o = Show(Outline(Input=src), view)
    o.ColorArrayName = [None, ""]
    o.AmbientColor = [0.25, 0.25, 0.25]
    o.DiffuseColor = [0.25, 0.25, 0.25]
    return o


#: How far the kept-cell count may sit from the geometric target before the
#: cutaway is refused. NOT slack for convenience -- it is the measured width of
#: a real effect, and it is far tighter than the failure it must catch.
#:
#: ParaView's Box clip is an IMPLICIT function evaluated at cell points, so the
#: layer of cells whose faces lie exactly on the cutting plane at x = y = z =
#: L/2 is resolved by a >= test rather than by cell topology. Measured on this
#: box, ParaView 5.11.2: an exact clip keeps 452,805 cells and a crinkle clip
#: 452,681, against the 448,000 that pure cell counting gives. That is +1.07 %,
#: and it is a property of the reader, not of the mesh.
#:
#: 2 % therefore admits the boundary layer and still refuses the defect this
#: assertion was written for -- a clip that cuts NOTHING and leaves all 512,000
#: cells under a caption that says a corner was removed, which is +14.3 % away.
CUTAWAY_TOL = 0.02


def corner_cutaway(src, time_value: float, crinkle: bool = False):
    """Remove the octant nearest (L,L,L), and PROVE it was removed.

    Returns ``(clip, cells_kept)``.

    ParaView's Box clip takes ``Position`` as the box MINIMUM CORNER and
    ``Invert = 1`` keeps what is INSIDE it -- both measured on this box, because
    the first version of this script assumed the opposite on both counts and
    rendered an UNCUT cube under a caption reading "corner removed to show the
    interior". The caption was false and the picture was entirely plausible.

    ``crinkle`` keeps whole cells rather than cutting them, which is what a MESH
    figure wants: a cut hexahedron renders as a stray polygon and reads as a
    meshing fault that is not there. The field figure takes the flat exact cut.
    """
    from paraview.simple import Clip, UpdatePipeline

    clip = Clip(Input=src)
    clip.ClipType = "Box"
    clip.ClipType.Position = [L / 2, L / 2, L / 2]   # MINIMUM corner of the box
    clip.ClipType.Length = [L, L, L]                 # spans L/2 .. 3L/2
    clip.ClipType.Rotation = [0.0, 0.0, 0.0]
    clip.Invert = 0                                  # keep what is OUTSIDE
    clip.Exact = 1
    clip.Crinkleclip = 1 if crinkle else 0
    UpdatePipeline(time=float(time_value), proxy=clip)

    got = clip.GetDataInformation().GetNumberOfCells()
    full = N ** 3                                    # 512 000
    want = full - (N // 2) ** 3                      # 448 000

    if got >= full:
        C.refuse(
            f"the corner cutaway kept {got:,} of {full:,} cells -- it removed "
            f"NOTHING. Every figure using it is captioned 'corner octant "
            f"removed', so the caption would be false while the picture stayed "
            f"plausible. That is the exact defect this assertion exists to "
            f"catch, and it is the one that actually happened here")
    if abs(got - want) > CUTAWAY_TOL * want:
        C.refuse(
            f"the corner cutaway kept {got:,} cells, {100.0*(got-want)/want:+.2f} % "
            f"from the {want:,} that removing the (L/2..L) octant implies, "
            f"outside the {100*CUTAWAY_TOL:.0f} % that the reader's "
            f"boundary-cell handling accounts for. The geometry is not what the "
            f"caption will say it is")
    return clip, got


# ---------------------------------------------------------------------------

def fig_field_cutaway(reader, time_dir, path):
    """The corner-cutaway octant coloured by theta.

    The single figure that carries this case: the three Robin faces are cold,
    the exposed interior faces run hot toward the origin, and the cut surface
    shows the front THROUGH the solid rather than only on its skin. Its geometry
    is the same cutaway as the mesh figure, deliberately, so the two read as one
    pair -- the same body, once as cells and once as field.
    """
    from paraview.simple import (CellDatatoPointData, Show, Render,
                                 UpdatePipeline)

    tv = float(time_dir)
    v = build_view(tv)
    p2c = CellDatatoPointData(Input=reader)
    p2c.CellDataArraytoprocess = ["T"]
    UpdatePipeline(time=tv, proxy=p2c)
    assert_rendered_time(p2c, time_dir, os.path.basename(path))
    clip, n_kept = corner_cutaway(p2c, tv, crinkle=False)

    d = Show(clip, v)
    d.Representation = "Surface"
    colour_by_theta(d, v, show_bar=True)
    outline(reader, v)

    isometric(v, (L / 2, L / 2, L / 2), pad=1.07)
    stamp(v, OCTANT_AS_SOLVED + " ; Fo = %.1f ; corner octant removed, %s of "
          "512 000 cells shown" % (FO[time_dir], f"{n_kept:,}".replace(",", " ")))
    Render(v)
    n = C.save_screenshot(v, path, size=(1500, 1000))
    C.announce(f"  wrote {os.path.basename(path)} ({n:,} bytes)")
    return n


def fig_isosurfaces(reader, time_dir, path):
    """Nested isosurfaces -- the cooling front as shells marching inward.

    theta = 1 initially everywhere and T_inf = 0, so the cold front enters
    through the three Robin faces and the surviving hot core hugs the symmetry
    corner at the origin, which is the CENTRE of the full cube. The shells are
    the front, and their nesting only exists in three dimensions.

    The same four theta levels are drawn at both times ON PURPOSE: the shells
    are then directly comparable between the Fo = 0.1 and Fo = 0.2 panels, and
    what the reader sees move is the front, not the contour choice.
    """
    from paraview.simple import (CellDatatoPointData, Contour, Show, Render,
                                 UpdatePipeline)
    tv = float(time_dir)
    v = build_view(tv)
    p2c = CellDatatoPointData(Input=reader)
    p2c.CellDataArraytoprocess = ["T"]
    UpdatePipeline(time=tv, proxy=p2c)
    lo, hi = assert_rendered_time(p2c, time_dir, os.path.basename(path))

    levels = [0.35, 0.50, 0.65, 0.80]
    opacities = [0.18, 0.30, 0.55, 1.0]
    drew = []
    for i, lev in enumerate(levels):
        c = Contour(Input=p2c)
        c.ContourBy = ["POINTS", "T"]
        c.Isosurfaces = [lev]
        UpdatePipeline(time=tv, proxy=c)
        if c.GetDataInformation().GetNumberOfCells() == 0:
            # This level genuinely does not exist in the field at this time --
            # at Fo = 0.1 the coldest cell is still at theta = 0.386, so a 0.35
            # shell has not formed yet. Skipping it is correct; drawing an empty
            # contour and captioning it would not be. The caption lists the
            # levels ACTUALLY drawn, which is why it is built from `drew`.
            continue
        drew.append(lev)
        d = Show(c, v)
        colour_by_theta(d, v, show_bar=(len(drew) == 1))
        d.Opacity = opacities[i]

    if not drew:
        C.refuse(f"no isosurface in {levels} exists at t = {time_dir}; an empty "
                 f"frame will not be shown")
    outline(reader, v)

    isometric(v, (L / 2, L / 2, L / 2), pad=1.07)
    stamp(v, OCTANT_AS_SOLVED + " ; Fo = %.1f ; field theta in %.3f to %.3f ; "
          "isosurfaces theta = %s"
          % (FO[time_dir], lo, hi, " ".join(f"{x:.2f}" for x in drew)))
    Render(v)
    n = C.save_screenshot(v, path, size=(1500, 1000))
    C.announce(f"  wrote {os.path.basename(path)} ({n:,} bytes)"
               f"  [levels drawn: {drew}]")
    return n


def fig_mesh(reader, path):
    """The mesh itself, cut open -- the figure that answers 'is it really 3-D'.

    A five-degree wedge cannot produce this picture. The cut face carries
    80 x 80 cells and the direction into the page carries 80 more, and the
    cutaway is measured by :func:`corner_cutaway` rather than asserted in prose.
    """
    from paraview.simple import Show, Render
    v = build_view(2.0)
    clip, n_kept = corner_cutaway(reader, 2.0, crinkle=True)

    d = Show(clip, v)
    d.Representation = "Surface With Edges"
    d.ColorArrayName = [None, ""]
    d.DiffuseColor = [0.80, 0.84, 0.90]
    d.AmbientColor = [0.80, 0.84, 0.90]
    d.EdgeColor = [0.20, 0.24, 0.30]
    d.LineWidth = 0.35

    isometric(v, (L / 2, L / 2, L / 2), pad=1.07)
    stamp(v, OCTANT_AS_SOLVED + " ; hexahedral mesh ; corner octant removed, "
          "%s of 512 000 cells shown" % f"{n_kept:,}".replace(",", " "))
    Render(v)
    n = C.save_screenshot(v, path, size=(1500, 1000))
    C.announce(f"  wrote {os.path.basename(path)} ({n:,} bytes)")
    return n


def fig_mirrored(reader, time_dir, path):
    """The ONLY view that mirrors the octant into the full cube.

    Permitted, and never silent: it carries OCTANT_MIRRORED rather than
    OCTANT_AS_SOLVED. Stamping the as-solved line here would be false in the
    opposite direction -- it would deny a display choice that WAS made -- which
    is the exact symmetry Act A's two-declaration pair was built to preserve.

    The mirrored body is also MEASURED: three reflections must multiply the cell
    count by eight, and a reflection that silently did nothing would otherwise
    ship a caption claiming a cube while showing an octant.
    """
    from paraview.simple import (CellDatatoPointData, Reflect, Contour, Show,
                                 Render, UpdatePipeline)
    tv = float(time_dir)
    v = build_view(tv)
    p2c = CellDatatoPointData(Input=reader)
    p2c.CellDataArraytoprocess = ["T"]
    UpdatePipeline(time=tv, proxy=p2c)
    assert_rendered_time(p2c, time_dir, os.path.basename(path))

    m = p2c
    for plane in ("X Min", "Y Min", "Z Min"):
        m = Reflect(Input=m)
        m.Plane = plane
        m.CopyInput = 1
    UpdatePipeline(time=tv, proxy=m)
    assert_rendered_time(m, time_dir, os.path.basename(path) + " (mirrored)")

    got = m.GetDataInformation().GetNumberOfCells()
    want = 8 * N ** 3
    if got != want:
        C.refuse(f"three reflections produced {got:,} cells where the full cube "
                 f"needs {want:,}. This figure claims a mirrored cube in its "
                 f"caption and must not show anything else")

    for i, lev in enumerate((0.35, 0.50, 0.65)):
        c = Contour(Input=m)
        c.ContourBy = ["POINTS", "T"]
        c.Isosurfaces = [lev]
        UpdatePipeline(time=tv, proxy=c)
        d = Show(c, v)
        colour_by_theta(d, v, show_bar=(i == 0))
        d.Opacity = [0.18, 0.35, 1.0][i]

    outline(m, v)
    isometric(v, (0, 0, 0), pad=1.06,
              bounds=(-L, L, -L, L, -L, L))   # the MIRRORED body's bounds
    stamp(v, OCTANT_MIRRORED + " ; Fo = %.1f ; all six faces of the mirrored "
          "body are Robin faces ; only three were solved" % FO[time_dir])
    Render(v)
    n = C.save_screenshot(v, path, size=(1500, 1000))
    C.announce(f"  wrote {os.path.basename(path)} ({n:,} bytes)"
               f"  [{got:,} cells after 3 reflections]")
    return n


def main() -> int:
    C.announce("=" * 74)
    C.announce("T18_CU_f renders -- 3-D transient conduction, 512,000 cells")
    C.announce("=" * 74)
    version = C.assert_paraview_version()
    C.announce(f"  ParaView {version} (pinned {C.REQUIRED_PARAVIEW})")

    # The stamp is checked BEFORE any compute, so a bad verdict word costs
    # nothing and cannot reach an image.
    C.assert_stamp(STAMP, CASE)
    C.announce(f"  stamp accepted: {STAMP}")

    case_dir = C.facts(CASE)["case_dir"]
    before = C.run_tree_fingerprint(case_dir)

    os.makedirs(OUT, exist_ok=True)
    roots = []
    total = 0
    try:
        for td in ("1", "2"):
            reader, root, n_cells = C.open_case(CASE, ["T"], ["1", "2"],
                                                time_value=float(td))
            roots.append(root)
            C.announce(f"  t = {td} s (Fo = {FO[td]}): loaded {n_cells:,} cells")
            tag = f"Fo{FO[td]:.1f}"
            total += fig_field_cutaway(reader, td,
                                       os.path.join(OUT, f"T18_temperature_field_{tag}.png"))
            total += fig_isosurfaces(reader, td,
                                     os.path.join(OUT, f"T18_isosurfaces_{tag}.png"))
            if td == "2":
                total += fig_mesh(reader, os.path.join(OUT, "T18_mesh.png"))
                total += fig_mirrored(reader, td,
                                      os.path.join(OUT, "T18_full_cube_mirrored.png"))
    finally:
        for r in roots:
            shutil.rmtree(r, ignore_errors=True)

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
    os._exit(rc)      # ParaView's GLX teardown must not overwrite this code
