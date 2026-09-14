#!/usr/bin/env python3
"""ParaView field panels for the DrivAer demo folder.

    xvfb-run -a pvpython docs/campaigns/navier_class/DRIVAER/demo/plots_DRIVAER/render_field_panels.py

FIELDS FROM THE COARSE CASE, WHICH IS COMPLETE AND GRADED PASS. The fine case was
STILL RUNNING when this was written, so it contributes ONE panel -- its mesh -- and
no field panel at all. When it lands, the field panels are regenerated from it.

    drivaer_p_side.png        surface pressure, side view
    drivaer_p_top.png         surface pressure, from above
    drivaer_p_rear.png        surface pressure, from behind
    drivaer_umag_symmetry.png velocity magnitude on the symmetry plane
    drivaer_umag_midheight.png velocity magnitude on a horizontal plane at mid body height
    drivaer_umag_wake.png     velocity magnitude on a cross-section one body-length aft
    drivaer_streamlines.png   streamlines through the wake, coloured by velocity
    drivaer_mesh_coarse.png   THEIR COARSE MESH on the body, 669,416 cells
    drivaer_mesh_fine.png     THEIR FINE MESH on the body, 4,048,483 cells

NOTHING IS WRITTEN INTO EITHER RUN TREE. `demo3d_render_common` stages a case as
symlinks and puts the `.foam` stub in the scratch root. `fine_R1` IS LIVE, so its
tree fingerprint is asserted over `constant/polyMesh` ALONE -- the part this render
reads and the part a running solver does not touch. Fingerprinting the whole live
tree would fail on the solver's own log and time writes, which would be a FALSE
ALARM rather than a breach, and a guard that cries wolf gets switched off.

Every coloured panel carries the planted colour control at the DrivAer 8x margin,
measured through `render_k2h_l3._colour_spread`. Captions, mesh edges and scalar
bars are added AFTER the measurement: they are dark pixels inside the "not the
white ground" body mask and would give the CONSTANT arm a spread that belongs to
the lettering rather than to the picture. Mesh panels carry an ink guard instead.
"""
import os, shutil, sys

REPO = "/home/ubuntu/Certonomous"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(REPO, "docs/campaigns/F14-cooling-ladder/demo/render_K2bU3R3_paraview"))
sys.path.insert(0, os.path.join(REPO, "verification/runs/F14-cooling-ladder/K2h_runs"))
import demo3d_render_common as C
sys.path.insert(0, os.path.join(REPO, "sdk"))
from workflows.act_paraview_style import style_view, colour_bar
import render_k2h_l3 as K2H

COARSE, COARSE_T = "WD_DRIVAER_COARSE", "1000"
FINE, FINE_T = "WD_DRIVAER_FINE", "0"
BODY = ["patch/body2", "patch/ruotaant", "patch/ruotapost"]
CONTROL_MARGIN = 8.0
MIN_FIELD_PX = 20000       # see _assert_painted: the colour bar alone is about 4,600 px
PCT_LO, PCT_HI = 2.0, 98.0
PRESET_P, PRESET_U = "Cool to Warm", "Viridis (matplotlib)"

# --- THE THREE PRESSURE PANELS, RE-RENDERED 2026-09-14 on the owner's order ----
# The old panels were percentile-windowed, framed with the caption band still
# reserved, and the top view was framed with `up = +x`, which puts the car's long
# axis VERTICAL -- the "narrow vertical strip" the owner sent back. What is fixed
# here, and every one of these is asserted rather than assumed:
#
#   * ONE colour range for all three, taken from the DATA RANGE of `p` on the
#     body and wheel patches at t = 1000 -- not a percentile window and not the
#     view's own range -- then rounded OUTWARD to a span that divides into four
#     equal round steps, so the bar carries exactly five round ticks;
#   * ORTHOGRAPHIC cameras whose parallel scale is derived from the body bounds
#     so the body fills the frame to a 5 % margin on each side of the LIMITING
#     axis, and the fill fraction is COMPUTED FROM THE SAME NUMBERS and refused
#     if it is not 0.90;
#   * NOSE ON THE LEFT in the side and top views, asserted as
#     `dot(camera right, +x) > 0`: the nose of this body is at MIN x -- the inlet
#     is `ffminx` and `0/U` is `uniform (30 0 0)`, so the flow runs +x -- and a
#     camera whose right vector is +x therefore lands min x on the left.
#     `up = (0, 1, 0)` for the top view is what turns the strip on its side.
P_SIZE_LANDSCAPE = (1920, 1080)      # side and top
P_SIZE_REAR = (1600, 1200)           # 4:3
P_MARGIN = 0.05                      # each side of the limiting axis
P_PAD = 1.0 / (1.0 - 2.0 * P_MARGIN) # so the body spans 1 - 2*margin of the frame
P_FILL = 1.0 - 2.0 * P_MARGIN
P_NTICKS = 5
P_BAR_TITLE = "p [m²/s²]"          # the glyphs are MEASURED, see _assert_bar_title
P_BODY_FACES = 32913                 # body2 20359 + ruotaant 6284 + ruotapost 6270

STAMP_C = ("WD_DRIVAER_COARSE ; 669416 cells ; simpleFoam ; iteration 1000 ; PASS")
STAMP_F = ("WD_DRIVAER_FINE ; 4048483 cells ; simpleFoam ; mesh only, the run is "
           "still going ; PENDING")
GEOM = ("Wolf Dynamics DrivAer, HALF model, symmetry at y = 0 ; U 30 m/s ; "
        "rotating wheels and moving ground ; domain -10 to 20 m by 0 to 4 m by "
        "0 to 6.4 m")
REPRO = ("REPRODUCTION of their shipped case, NOT an independent validation: our "
         "forceCoeffs output is byte-identical to theirs")


def _view(size=(1600, 1000)):
    from paraview.simple import CreateRenderView, Render
    v = CreateRenderView(); style_view(v, size); Render(v)
    return v


def _flat(disp):
    disp.Ambient, disp.Diffuse, disp.Specular = 1.0, 0.0, 0.0


def _bar(view, lut, label):
    return colour_bar(view, lut, label)



def _percentiles(src, name):
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
        for att in (b.GetPointData(), b.GetCellData()):
            a = att.GetArray(name)
            if a is None:
                continue
            x = numpy_support.vtk_to_numpy(a)
            if x.ndim > 1:
                x = np.linalg.norm(x, axis=1)
            vals.append(x)
            break
    if not vals:
        C.refuse("no %s array was fetched; no window can be measured" % name)
    a = np.concatenate(vals)
    return float(np.percentile(a, PCT_LO)), float(np.percentile(a, PCT_HI))


def _spread_core(path, thr=0.25):
    import numpy as np
    from paraview.vtk.util import numpy_support
    from paraview.vtk.vtkIOImage import vtkPNGReader
    r = vtkPNGReader(); r.SetFileName(path); r.Update()
    a = numpy_support.vtk_to_numpy(r.GetOutput().GetPointData().GetScalars())
    rgb = a[:, :3].astype(float) / 255.0
    body = (1.0 - rgb).max(axis=1) > thr
    if body.sum() < 500:
        C.refuse("%s has only %d interior pixels" % (os.path.basename(path), int(body.sum())))
    mx = np.maximum(rgb[body].max(axis=1), 1e-6)
    return float(((rgb[body, 0] - rgb[body, 2]) / mx).std()), int(body.sum())


def _assert_painted(pos, neg, field):
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
    p, npx = K2H._colour_spread(pos)
    n, _ = K2H._colour_spread(neg)
    cp, ncp = _spread_core(pos)
    cn, _ = _spread_core(neg)
    if npx < MIN_FIELD_PX:
        C.refuse("BLANK FRAME for %r: the positive arm covers only %s pixels, below "
                 "the %s floor -- the field was not drawn"
                 % (field, format(npx, ","), format(MIN_FIELD_PX, ",")))
    if n <= 0.0 or cn <= 0.0:
        C.refuse("NO CONTROL for %r: the constant-array arm spread is exactly zero"
                 % field)
    C.announce("      colour control %s: full-body %.5f over %s px against %.5f "
               "(%.1fx) ; interior %.5f over %s px against %.5f (%.1fx) ; floor %gx"
               % (field, p, format(npx, ","), n, p / max(n, 1e-9),
                  cp, format(ncp, ","), cn, cp / max(cn, 1e-9), CONTROL_MARGIN))
    if p <= n:
        C.refuse("COLOUR CONTROL FAILED for %r on the full-body mask: %.5f "
                 "against a constant array's %.5f" % (field, p, n))
    if cp < CONTROL_MARGIN * max(cn, 1e-9):
        C.refuse("COLOUR CONTROL FAILED for %r: interior spread %.5f against a "
                 "constant array's %.5f" % (field, cp, cn))


def _render_with_control(view, src, disp, out, field, add_caption, size=(1600, 1000),
                         control_value=None, control_preset=None,
                         control_range=None):
    """Render the panel, and the SAME panel with the field replaced by a constant.

    ``control_value``, ``control_preset`` and ``control_range`` make the null arm
    a FAIR one, and they were added 2026-09-14 on a MEASURED confound. Until then
    the constant arm was painted `1.0` through whatever lookup table ParaView
    hands a brand-new array, which on the pressure panels came out a SATURATED
    BLUE silhouette: every edge pixel of it ran from saturated blue to white, so
    the null arm's own colour spread was set by how vivid an unrelated colour map
    happened to be, not by the picture under test. Measured on
    `drivaer_p_side.png`: null spread 0.01466 with the arbitrary map, against
    0.00302-class numbers on the panels this floor was calibrated against.

    Given a value, the null is instead the SAME field array name, the SAME preset
    and the SAME fixed range, held constant at the field's own MEAN. That is the
    exact null the control is for -- "this picture if p did not vary" -- and it is
    a HARDER test than the old one, not an easier one: the null now carries the
    panel's own colour and its own edge contrast, so the only thing left to
    separate the two arms is the spatial variation of the field itself.
    """
    from paraview.simple import (Calculator, Show, Hide, Render, ColorBy,
                                 GetColorTransferFunction, UpdatePipeline)
    flat = Calculator(Input=src)
    flat.AttributeType = "Point Data"
    flat.ResultArrayName = "CONTROL_CONSTANT"
    flat.Function = "1.0" if control_value is None else repr(float(control_value))
    UpdatePipeline(proxy=flat)
    arr = flat.GetPointDataInformation().GetArray("CONTROL_CONSTANT")
    lo, hi = arr.GetComponentRange(0)
    if abs(hi - lo) > 1e-12:
        C.refuse("the control array spans %g to %g and is not constant" % (lo, hi))
    Hide(src, view)
    disp.SetScalarBarVisibility(view, False)
    dn = Show(flat, view)
    ColorBy(dn, ("POINTS", "CONTROL_CONSTANT"))
    if control_preset is not None:
        clut = GetColorTransferFunction("CONTROL_CONSTANT")
        clut.ApplyPreset(control_preset, True)
        clut.RescaleTransferFunction(*control_range)
        dn.SetScalarBarVisibility(view, False)
    _flat(dn)
    dn.SetScalarBarVisibility(view, False)
    Render(view)
    neg = os.path.join(HERE, "_control", "NEGATIVE_constant_" + os.path.basename(out))
    C.save_screenshot(view, neg, size=size)
    Hide(flat, view)
    Show(src, view)
    disp.SetScalarBarVisibility(view, True)
    Render(view)
    pos = os.path.join(HERE, "_control", "POSITIVE_uncaptioned_" + os.path.basename(out))
    C.save_screenshot(view, pos, size=size)
    _assert_painted(pos, neg, field)
    add_caption(view)
    Render(view)
    n = C.save_screenshot(view, out, size=size)
    C.announce("  wrote %s (%s bytes)" % (os.path.basename(out), format(n, ",")))
    return n


def _caption(view, case, stamp, second):
    """NOTHING IS WRITTEN ON THE IMAGE (v2 section 13). The case, the time,
    the geometry and the verdict live in the folder SIDECAR.md and in the act
    beside the figure. `C.assert_stamp` still ran on `stamp` before any pixel
    was drawn, so the verdict guard is kept and only its printing is dropped."""
    return None




# ---------------------------------------------------------------------------
# The pressure panels: data range, round ticks, derived cameras
# ---------------------------------------------------------------------------

def _data_range(src, name, assoc="CELLS"):
    """The DATA range of `name`, taken two independent ways and cross-checked.

    ParaView's array information reports a range computed by the reader; numpy
    over the fetched array is an independent read of the same values. A window
    that only one of them can see is not a window, so they must agree.
    """
    import numpy as np
    from paraview import servermanager as sm
    from paraview.vtk.util import numpy_support
    info = (src.GetCellDataInformation() if assoc == "CELLS"
            else src.GetPointDataInformation())
    arr = info.GetArray(name)
    if arr is None:
        C.refuse("no %s array on the %s of the rendered surface; there is no "
                 "range to take" % (name, assoc))
    lo, hi = arr.GetComponentRange(0)
    d = sm.Fetch(src)
    vals = []
    blocks = []
    if hasattr(d, "GetNumberOfBlocks"):
        it = d.NewIterator(); it.InitTraversal()
        while not it.IsDoneWithTraversal():
            blocks.append(it.GetCurrentDataObject()); it.GoToNextItem()
    else:
        blocks = [d]
    for b in blocks:
        att = b.GetCellData() if assoc == "CELLS" else b.GetPointData()
        a = att.GetArray(name)
        if a is not None:
            vals.append(numpy_support.vtk_to_numpy(a))
    if not vals:
        C.refuse("the fetched surface carries no %s array" % name)
    a = np.concatenate(vals)
    nlo, nhi = float(a.min()), float(a.max())
    tol = 1e-6 * max(1.0, abs(nlo), abs(nhi))
    if abs(nlo - lo) > tol or abs(nhi - hi) > tol:
        C.refuse("the reader reports %s in [%.6g, %.6g] and numpy over the same "
                 "fetched values reports [%.6g, %.6g]; a range two readers "
                 "disagree about is not a range" % (name, lo, hi, nlo, nhi))
    C.announce("  %s DATA RANGE on %d values: %.6g to %.6g (reader and numpy "
               "agree to %.1e)" % (name, a.size, nlo, nhi, tol))
    return nlo, nhi


def _mean(src, name, assoc="CELLS"):
    """The arithmetic mean of the field over the rendered faces -- the value the
    null arm of the colour control is held at. Face-area weighting would be more
    physical; this number is never reported as a physical mean, it only has to be
    a representative colour, so the plain mean is used and said to be one."""
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
        att = b.GetCellData() if assoc == "CELLS" else b.GetPointData()
        a = att.GetArray(name)
        if a is not None:
            vals.append(numpy_support.vtk_to_numpy(a))
    if not vals:
        C.refuse("the fetched surface carries no %s array to average" % name)
    m = float(np.concatenate(vals).mean())
    C.announce("  %s unweighted face mean %.6g (the null arm is held here)"
               % (name, m))
    return m


def _nice_range(lo, hi, n=P_NTICKS):
    """Round OUTWARD to a span of n-1 equal round steps, so n round ticks land.

    Every tick is an exact multiple of the step, the step comes from the 1/2/2.5/5
    ladder, and the rounded range CONTAINS the data range -- checked below rather
    than trusted. Because the data straddles zero, zero is necessarily one of the
    ticks: all ticks are multiples of the step and the range spans zero.
    """
    import math
    if not hi > lo:
        C.refuse("a colour range needs hi > lo, not [%r, %r]" % (lo, hi))
    k = n - 1
    base = (hi - lo) / float(k)
    e0 = int(math.floor(math.log10(base)))
    for e in range(e0, e0 + 5):
        for m in (1.0, 2.0, 2.5, 5.0):
            q = m * 10.0 ** e
            if q < base * (1.0 - 1e-12):
                continue
            t = lo / q
            t = round(t) if abs(t - round(t)) < 1e-9 else math.floor(t)
            rlo = t * q
            rhi = rlo + k * q
            if rhi >= hi - 1e-9 * max(1.0, abs(hi)):
                ticks = [(t + i) * q for i in range(n)]
                if ticks[0] > lo + 1e-9 or ticks[-1] < hi - 1e-9:
                    continue
                return ticks[0], ticks[-1], ticks
    C.refuse("no round %d-tick range was found around [%.6g, %.6g]" % (n, lo, hi))


def _tick_format(ticks):
    for dec in (0, 1, 2, 3):
        fmt = "%%.%df" % dec
        if all(abs(float(fmt % t) - t) <= 1e-9 * max(1.0, abs(t)) for t in ticks):
            return fmt
    C.refuse("no plain-decimal format prints %r without losing a digit" % (ticks,))


#: Glyphs MEASURED on this box, 2026-09-14, by rendering a scalar-bar title in
#: ParaView 5.11.2 under xvfb and reading the written PNG back (the probe and its
#: three frames were scratch and are gone; what it established is recorded here,
#: and `_assert_bar_title` re-checks every character against it):
#:
#:   * U+00B2, the superscript two, RENDERS CORRECTLY in the scalar-bar title --
#:     `p [m²/s²]` reaches the screen with both exponents. It is NOT one of the
#:     dropped glyphs, so the unit is written the way the order writes it;
#:   * `[` and `]` are DRAWN AS `(` AND `)` by this build. A title written with
#:     square brackets appears on the image with round ones, and nothing in the
#:     pipeline says so. That is a DISPLAY substitution this lane cannot defeat
#:     from the API, so it is disclosed here and in SIDECAR.md rather than hidden:
#:     the source says `p [m²/s²]` and the pixels say `p (m²/s²)`, which is also
#:     what every other ParaView panel in this lab already shows.
BAR_TITLE_GLYPHS = set(C.SAFE_CAPTION_CHARS) | set("[]²")


def _assert_bar_title(text):
    """The bar title is the ONLY text on these images, so its glyphs are checked.

    Against BAR_TITLE_GLYPHS above -- the set measured to render here -- and
    against the module's own dropped-glyph table. A character outside both is
    refused rather than drawn, because a unit that loses an exponent on screen
    looks deliberate and is simply wrong.
    """
    for ch in text:
        if ch in C.KNOWN_DROPPED_GLYPHS:
            C.refuse("the colour-bar title uses %r, which is %s"
                     % (ch, C.KNOWN_DROPPED_GLYPHS[ch]))
        if ch not in BAR_TITLE_GLYPHS:
            C.refuse("the colour-bar title uses %r (U+%04X), which is not in the "
                     "glyph set measured to render on this box: %r"
                     % (ch, ord(ch), text))
    return text


def _bar_fixed(view, lut, title, ticks):
    """One bar, a quarter of the frame high, on the right, five custom labels."""
    b = _bar(view, lut, _assert_bar_title(title))
    b.AutomaticLabelFormat = 0
    b.LabelFormat = _tick_format(ticks)
    b.RangeLabelFormat = b.LabelFormat
    b.AddRangeLabels = 0                 # the ends are already two of the five
    b.UseCustomLabels = 1
    b.CustomLabels = [float(t) for t in ticks]
    # UPPER RIGHT, and the same on all three panels. NOT hand-picked: with the
    # body filling 90 % of its limiting axis, a right-hand bar at mid-height sits
    # ON the car in the side and top views (measured: the tail reaches 94 % of
    # frame width in the side view, the bar strip sits at 88.5 %). The body's
    # projected extents are known from `_assert_framing` -- side 0.259..0.741 of
    # frame height, top 0.326..0.674, rear 0.257..0.743 of frame WIDTH -- so a
    # quarter-height bar at y = 0.70 clears the body in ALL THREE, at ONE
    # position, which is what "the same bar on all three panels" asks for.
    b.Position = [0.885, 0.70]
    if int(b.UseCustomLabels) != 1 or len(b.CustomLabels) != len(ticks):
        C.refuse("the scalar bar did not take the %d custom labels" % len(ticks))
    return b


def _axes(direction, up):
    """The camera's right and up vectors, by the same arithmetic frame_by_extent
    uses. Used to ASSERT which way the nose points on the finished frame."""
    import math

    def _norm(v):
        n = math.sqrt(sum(c * c for c in v))
        if n == 0:
            C.refuse("a zero-length camera vector cannot define a view")
        return [c / n for c in v]

    def _cross(a, b):
        return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
                a[0] * b[1] - a[1] * b[0]]

    d = _norm(direction)
    view_dir = [-c for c in d]
    right = _norm(_cross(view_dir, up))
    true_up = _norm(_cross(right, view_dir))
    return right, true_up, view_dir


def _assert_framing(name, bounds, focal, direction, up, scale, size, nose_left):
    """REFUSE a frame that clips the body, mis-fills it, or puts the nose right.

    The fill fraction is recomputed from the measured bounds and the parallel
    scale actually in force, so this is a check on the finished camera and not a
    restatement of the request.
    """
    right, true_up, _ = _axes(direction, up)
    x0, x1, y0, y1, z0, z1 = bounds
    hs, vs = [], []
    for cx in (x0, x1):
        for cy in (y0, y1):
            for cz in (z0, z1):
                r = [cx - focal[0], cy - focal[1], cz - focal[2]]
                hs.append(sum(r[i] * right[i] for i in range(3)))
                vs.append(sum(r[i] * true_up[i] for i in range(3)))
    half_h = max(abs(min(hs)), abs(max(hs)))
    half_v = max(abs(min(vs)), abs(max(vs)))
    aspect = float(size[0]) / float(size[1])
    fw = half_h / (scale * aspect)
    fh = half_v / scale
    C.announce("  %s fills %.1f %% of frame width and %.1f %% of frame height "
               "(limiting axis %.1f %%, target %.1f %%)"
               % (name, fw * 100.0, fh * 100.0, max(fw, fh) * 100.0,
                  P_FILL * 100.0))
    if fw > 1.0 or fh > 1.0:
        C.refuse("%s CLIPS the body: it spans %.1f %% of width and %.1f %% of "
                 "height" % (name, fw * 100.0, fh * 100.0))
    if abs(max(fw, fh) - P_FILL) > 2e-3:
        C.refuse("%s fills %.3f of its limiting axis where %.3f was asked for; "
                 "the margin on this frame is not the margin the order names"
                 % (name, max(fw, fh), P_FILL))
    if nose_left:
        # The nose is at MIN x (inlet ffminx, 0/U uniform (30 0 0)), so it lands
        # on the left exactly when the camera's right vector points along +x.
        if right[0] <= 0.5:
            C.refuse("%s would put the nose on the RIGHT: the camera right "
                     "vector is %r and the nose is at min x" % (name, right))
        C.announce("    nose LEFT asserted: camera right vector %.3f %.3f %.3f "
                   "(+x to the right of frame, nose at x = %.3f)"
                   % (right[0], right[1], right[2], x0))
    return fw, fh


def p_surface_panel(reader, out, direction, up, prange, ticks, size, nose_left,
                    pmean):
    from paraview.simple import (MergeBlocks, Show, Render, ColorBy,
                                 GetColorTransferFunction, UpdatePipeline)
    v = _view(size)
    reader.MeshRegions = BODY
    UpdatePipeline(time=float(COARSE_T), proxy=reader)
    surf = MergeBlocks(Input=reader)
    UpdatePipeline(time=float(COARSE_T), proxy=surf)
    info = surf.GetDataInformation()
    n = info.GetNumberOfCells()
    if n != P_BODY_FACES:
        C.refuse("the body patches rendered %d faces where constant/polyMesh/"
                 "boundary sums to %d" % (n, P_BODY_FACES))
    d = Show(surf, v); _flat(d)
    ColorBy(d, ("CELLS", "p"))
    lut = GetColorTransferFunction("p"); lut.ApplyPreset(PRESET_P, True)
    lut.RescaleTransferFunction(*prange)
    _bar_fixed(v, lut, P_BAR_TITLE, ticks)
    b = info.GetBounds()
    focal = [(b[0] + b[1]) / 2.0, (b[2] + b[3]) / 2.0, (b[4] + b[5]) / 2.0]
    scale = C.frame_by_extent(v, focal, direction, up=up, bounds=b, pad=P_PAD,
                              bottom_band=0.0)
    _assert_framing(os.path.basename(out), b, focal, direction, up, scale, size,
                    nose_left)
    Render(v)
    C.announce("  %s: parallel scale %.4f, view %dx%d, camera direction %r, "
               "up %r" % (os.path.basename(out), scale, size[0], size[1],
                          tuple(direction), tuple(up)))
    return _render_with_control(v, surf, d, out, "p", lambda view: None,
                                size=size, control_value=pmean,
                                control_preset=PRESET_P,
                                control_range=prange), scale


def p_panels(reader):
    """The three pressure panels on ONE range fixed from the side view's data."""
    import hashlib
    from paraview.simple import MergeBlocks, UpdatePipeline
    reader.MeshRegions = BODY
    UpdatePipeline(time=float(COARSE_T), proxy=reader)
    surf = MergeBlocks(Input=reader)
    UpdatePipeline(time=float(COARSE_T), proxy=surf)
    bbox = surf.GetDataInformation().GetBounds()
    C.announce("  body bounds MEASURED x %.4f..%.4f y %.4f..%.4f z %.4f..%.4f m"
               % bbox)
    raw_lo, raw_hi = _data_range(surf, "p", "CELLS")
    pmean = _mean(surf, "p", "CELLS")
    # DIAGNOSTIC ONLY, and acted on rather than filed: the window below is the
    # DATA range the order names, and these percentiles say how much of the body
    # that range spends on a handful of faces. They are reported upward with the
    # panels, never used to choose the window.
    p2, p98 = _percentiles(surf, "p")
    C.announce("  DIAGNOSTIC, NOT THE WINDOW: p 2nd/98th percentile %.4g to "
               "%.4g m2/s2 -- the data range below is %.1fx wider"
               % (p2, p98, (raw_hi - raw_lo) / (p98 - p2)))
    lo, hi, ticks = _nice_range(raw_lo, raw_hi)
    C.announce("  colour range FIXED %.6g to %.6g m2/s2 (rounded outward from "
               "%.6g to %.6g), ticks %s -- the SAME bar on all three panels"
               % (lo, hi, raw_lo, raw_hi,
                  ", ".join(_tick_format(ticks) % t for t in ticks)))

    plan = [("drivaer_p_side.png", (0.0, -1.0, 0.0), (0.0, 0.0, 1.0),
             P_SIZE_LANDSCAPE, True),
            ("drivaer_p_top.png", (0.0, 0.0, 1.0), (0.0, 1.0, 0.0),
             P_SIZE_LANDSCAPE, True),
            ("drivaer_p_rear.png", (1.0, 0.0, 0.0), (0.0, 0.0, 1.0),
             P_SIZE_REAR, False)]
    rows, total = [], 0
    for name, direction, up, size, nose_left in plan:
        nb, scale = p_surface_panel(reader, os.path.join(HERE, name), direction,
                                    up, (lo, hi), ticks, size, nose_left, pmean)
        total += nb
        _, _, view_dir = _axes(direction, up)
        rows.append((name, COARSE,
                     C.facts(COARSE)["case_dir"], COARSE_T,
                     "+".join(p.split("/")[-1] for p in BODY),
                     "camera on the (%g, %g, %g) axis from the body centre "
                     "(%.4f, %.4f, %.4f); VIEW DIRECTION (%g, %g, %g); "
                     "up (%g, %g, %g); orthographic, parallel scale %.4f"
                     % (tuple(direction)
                        + ((bbox[0] + bbox[1]) / 2.0, (bbox[2] + bbox[3]) / 2.0,
                           (bbox[4] + bbox[5]) / 2.0)
                        + tuple(round(c, 12) + 0.0 for c in view_dir)
                        + tuple(up) + (scale,)),
                     "%s to %s m2/s2, fixed, five ticks %s"
                     % (_tick_format(ticks) % lo, _tick_format(ticks) % hi,
                        "/".join(_tick_format(ticks) % t for t in ticks)),
                     "%dx%d" % size))

    field = os.path.join(C.facts(COARSE)["case_dir"], COARSE_T, "p")
    h = hashlib.sha256()
    with open(field, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    sha = h.hexdigest()
    prov = os.path.join(HERE, "PROVENANCE_PANELS.tsv")
    with open(prov, "w") as fh:
        fh.write("# ParaView panel provenance. SEPARATE from PROVENANCE.tsv "
                 "because build_plots.py REWRITES that file whole ('w'), so a "
                 "row appended there is destroyed by the next matplotlib build.\n")
        fh.write("figure\tcase\tcase_dir\ttime_dir\tpatches\tcamera\t"
                 "colour_range\timage_size\tfield_sha256\n")
        for r in rows:
            fh.write("\t".join(list(r) + [sha]) + "\n")
    C.announce("  wrote %s (%d rows, field sha256 %s)"
               % (os.path.basename(prov), len(rows), sha[:16]))
    return total


def surface_panel(reader, out, direction, up, note, prange):
    from paraview.simple import (MergeBlocks, Show, Render, ColorBy,
                                 GetColorTransferFunction, UpdatePipeline)
    v = _view()
    reader.MeshRegions = BODY
    UpdatePipeline(time=float(COARSE_T), proxy=reader)
    surf = MergeBlocks(Input=reader)
    UpdatePipeline(time=float(COARSE_T), proxy=surf)
    info = surf.GetDataInformation()
    n = info.GetNumberOfCells()
    if n != 32913:
        C.refuse("the body patches rendered %d cells where constant/polyMesh/"
                 "boundary sums to 32913 (body2 20359 + ruotaant 6284 + "
                 "ruotapost 6270)" % n)
    d = Show(surf, v); _flat(d)
    ColorBy(d, ("CELLS", "p"))
    lut = GetColorTransferFunction("p"); lut.ApplyPreset(PRESET_P, True)
    lut.RescaleTransferFunction(*prange)
    _bar(v, lut, "p  [m2/s2]")
    b = info.GetBounds()
    C.frame_by_extent(v, [(b[0] + b[1]) / 2, (b[2] + b[3]) / 2, (b[4] + b[5]) / 2],
                      direction, up=up, bounds=b, pad=1.10, bottom_band=0.12)
    Render(v)
    return _render_with_control(v, surf, d, out, "p",
                                lambda view: _caption(view, COARSE, STAMP_C, note))


def plane_panel(reader, out, origin, normal, direction, up, bounds, note, urange,
                outline_body=False):
    from paraview.simple import (CellDatatoPointData, Calculator, Slice, Show,
                                 Render, ColorBy, GetColorTransferFunction,
                                 UpdatePipeline)
    v = _view()
    reader.MeshRegions = ["internalMesh"]
    UpdatePipeline(time=float(COARSE_T), proxy=reader)
    p2c = CellDatatoPointData(Input=reader)
    p2c.CellDataArraytoprocess = ["U", "p"]
    UpdatePipeline(time=float(COARSE_T), proxy=p2c)
    calc = Calculator(Input=p2c)
    calc.AttributeType = "Point Data"
    calc.ResultArrayName = "Umag"; calc.Function = "mag(U)"
    UpdatePipeline(time=float(COARSE_T), proxy=calc)
    s = Slice(Input=calc)
    s.SliceType = "Plane"; s.SliceType.Origin = origin; s.SliceType.Normal = normal
    UpdatePipeline(time=float(COARSE_T), proxy=s)
    if s.GetDataInformation().GetNumberOfCells() == 0:
        C.refuse("the plane at %r is empty; nothing would be drawn" % (origin,))
    d = Show(s, v); _flat(d)
    ColorBy(d, ("POINTS", "Umag"))
    lut = GetColorTransferFunction("Umag"); lut.ApplyPreset(PRESET_U, True)
    lut.RescaleTransferFunction(*urange)
    _bar(v, lut, "|U|  [m/s]")
    C.frame_by_extent(v, [(bounds[0] + bounds[1]) / 2, (bounds[2] + bounds[3]) / 2,
                          (bounds[4] + bounds[5]) / 2], direction, up=up,
                      bounds=bounds, pad=1.06, bottom_band=0.12)
    Render(v)
    return _render_with_control(v, s, d, out, "Umag",
                                lambda view: _caption(view, COARSE, STAMP_C, note))


def streamline_panel(reader, out, bbox, note, urange):
    from paraview.simple import (CellDatatoPointData, Calculator, StreamTracer,
                                 Tube, Show, Render, ColorBy,
                                 GetColorTransferFunction, UpdatePipeline)
    v = _view()
    reader.MeshRegions = ["internalMesh"]
    UpdatePipeline(time=float(COARSE_T), proxy=reader)
    p2c = CellDatatoPointData(Input=reader)
    p2c.CellDataArraytoprocess = ["U"]
    UpdatePipeline(time=float(COARSE_T), proxy=p2c)
    calc = Calculator(Input=p2c)
    calc.AttributeType = "Point Data"
    calc.ResultArrayName = "Umag"; calc.Function = "mag(U)"
    UpdatePipeline(time=float(COARSE_T), proxy=calc)
    st = StreamTracer(Input=calc, SeedType="Line")
    st.Vectors = ["POINTS", "U"]
    st.MaximumStreamlineLength = 30.0
    # SEEDED UPSTREAM OVER THE BODY HEIGHT, on the symmetry plane -- the owner's
    # round-2 note. The old seed line ran diagonally across y AND z, which is why the
    # view came out skewed and a seed plane cut across the image.
    # ROUND 3: 40-60 lines, not 240 -- a readable ribbon count, the owner's rule.
    st.SeedType.Point1 = [bbox[0] - 1.5, 0.02, 0.02]
    st.SeedType.Point2 = [bbox[0] - 1.5, 0.02, bbox[5] * 1.15]
    st.SeedType.Resolution = 49
    UpdatePipeline(time=float(COARSE_T), proxy=st)
    if st.GetDataInformation().GetNumberOfPoints() == 0:
        C.refuse("no streamline was integrated; nothing would be drawn")
    # 50 RIBBONS need to be thicker than 240 did, or antialiased edges are most of
    # the ink and the constant-array control arm spreads on edge pixels alone.
    tube = Tube(Input=st); tube.Radius = 0.030
    UpdatePipeline(time=float(COARSE_T), proxy=tube)
    d = Show(tube, v); _flat(d)
    ColorBy(d, ("POINTS", "Umag"))
    lut = GetColorTransferFunction("Umag"); lut.ApplyPreset(PRESET_U, True)
    # THE LOOKUP TABLE SPANS WHAT THIS OBJECT ACTUALLY CARRIES -- a window taken
    # from some other object leaves the ribbons one flat colour (owner, round 2).
    ta = tube.GetPointDataInformation().GetArray("Umag")
    tlo, thi = ta.GetComponentRange(0)
    C.announce("  streamline |U| MEASURED %.4g to %.4g m/s (%d lines seeded)"
               % (tlo, thi, st.SeedType.Resolution + 1))
    lut.RescaleTransferFunction(tlo, thi)
    _bar(v, lut, "|U|  [m/s]")
    # CAMERA ON THE SYMMETRY PLANE, looking along -y, orthographic (frame_by_extent
    # sets CameraParallelProjection), the body centred.
    C.frame_by_extent(v, [(bbox[0] + bbox[1]) / 2, 0.0, (bbox[4] + bbox[5]) / 2],
                      (0.0, -1.0, 0.0), up=(0.0, 0.0, 1.0),
                      bounds=(bbox[0] - 1.8, bbox[1] + 3.0, 0.0, 0.0,
                              0.0, bbox[5] * 1.5),
                      pad=1.04)
    Render(v)
    return _render_with_control(v, tube, d, out, "Umag",
                                lambda view: _caption(view, COARSE, STAMP_C, note))


def mesh_panel(case, time, out, stamp, note, expect_faces, arrays=("U",)):
    """Body surface with its own edges. Ink guard, not a colour control: a plain
    mesh carries no field, so a field-versus-constant comparison has no meaning."""
    from paraview.simple import (MergeBlocks, Show, Render, ColorBy,
                                 UpdatePipeline)
    root = None
    try:
        # NO FIELD IS REQUESTED FOR A MESH PANEL, and for the fine case it must
        # not be: its only time directory is `0`, and ParaView's OpenFOAM reader
        # SKIPS t = 0 by default, so a field asked for there is reported absent on
        # a case that plainly has it. The mesh comes from constant/polyMesh either
        # way, so a mesh panel asks for nothing and the cell-count assertion still
        # proves it is the right mesh.
        reader, root, n = C.open_case(case, list(arrays), [time],
                                      decompose_polyhedra=False)
        C.announce("  %s: %s cells at t = %s" % (case, format(n, ","), time))
        v = _view()
        reader.MeshRegions = BODY
        UpdatePipeline(time=float(time), proxy=reader)
        surf = MergeBlocks(Input=reader)
        UpdatePipeline(time=float(time), proxy=surf)
        info = surf.GetDataInformation()
        got = info.GetNumberOfCells()
        if got != expect_faces:
            C.refuse("%s body patches rendered %d faces where the boundary file "
                     "sums to %d" % (case, got, expect_faces))
        d = Show(surf, v); _flat(d)
        d.ColorArrayName = [None, ""]      # ColorBy(d, None) is rejected by this build
        d.DiffuseColor = [0.66, 0.69, 0.74]
        d.AmbientColor = [0.66, 0.69, 0.74]
        d.Representation = "Surface With Edges"
        d.EdgeColor = [0.12, 0.12, 0.12]
        d.LineWidth = 0.3
        b = info.GetBounds()
        C.frame_by_extent(v, [(b[0] + b[1]) / 2, (b[2] + b[3]) / 2, (b[4] + b[5]) / 2],
                          (0.62, -0.72, 0.32), up=(0.0, 0.0, 1.0), bounds=b,
                          pad=1.10, bottom_band=0.12)
        _caption(v, case, stamp, note)
        Render(v)
        nb = C.save_screenshot(v, out, size=(1600, 1000))
        _, npx = K2H._colour_spread(out)
        if npx < 20000:
            C.refuse("%s has only %d non-background pixels" % (os.path.basename(out), npx))
        C.announce("  wrote %s (%s bytes, %s faces, %s body px)"
                   % (os.path.basename(out), format(nb, ","), format(got, ","),
                      format(npx, ",")))
        return nb
    finally:
        if root:
            shutil.rmtree(root, ignore_errors=True)


WAKE_MIN_WIDTH_FRAC = 0.40      # the body must fill at least this much of the frame


def wake_panel(reader, out, urange):
    """The wake cross-section, framed FROM MEASURED BOUNDS and asserted before saving.

    NOTHING HERE IS HAND-TYPED. Three attempts at this panel were framed by hand and
    all three put the car in a corner, because the camera's right vector is -y and a
    box written as "y from 0 to 2.2" therefore extends AWAY from a half-body that
    spans y 0 to 1.0. So the camera is now derived:

      * the body patch bounds are read from the data information AFTER UpdatePipeline;
      * the focal point is the body centre, at the wake plane's x;
      * the parallel scale is the measured half-extent with a 15 % margin, taken as
        max(half-height, half-width / aspect) so the body fits in BOTH directions;
      * and before the image is saved, the fraction of frame width the body spans is
        COMPUTED from those same numbers and REFUSED below WAKE_MIN_WIDTH_FRAC.

    A frame that puts the subject in a corner can no longer be written out, which is
    the only way this stops recurring.
    """
    from paraview.simple import (CellDatatoPointData, Calculator, Slice, Show, Render,
                                 ColorBy, GetColorTransferFunction, UpdatePipeline,
                                 MergeBlocks, OpenFOAMReader)
    size = (1200, 1000)          # near-square: a wake cross-section is not 16:9, and a
                                 # wide frame is what forced the body below 40 % before
    aspect = float(size[0]) / float(size[1])

    # --- the body, from a SECOND reader: re-pointing the slice's own reader pulls the
    # internalMesh out from under the Slice that is already on screen, which is why no
    # outline appeared on the previous attempt.
    root2, foam2 = C.materialise_case(COARSE, [COARSE_T])
    try:
        br = OpenFOAMReader(FileName=foam2)
        br.Decomposepolyhedra = 0
        br.MeshRegions = BODY
        UpdatePipeline(time=float(COARSE_T), proxy=br)
        body = MergeBlocks(Input=br); UpdatePipeline(time=float(COARSE_T), proxy=body)
        bb = body.GetDataInformation().GetBounds()
        if bb[1] <= bb[0]:
            C.refuse("the body surface reported degenerate bounds %r" % (bb,))
        C.announce("  body bounds MEASURED x %.3f..%.3f y %.3f..%.3f z %.3f..%.3f"
                   % bb)
        half_h = (bb[3] - bb[2]) / 2.0
        half_v = (bb[5] - bb[4]) / 2.0
        scale = max(half_v, half_h / aspect) * 1.15
        frac = (bb[3] - bb[2]) / (2.0 * scale * aspect)
        C.announce("  parallel scale %.4f from measured half-extents (%.4f, %.4f) ; "
                   "body spans %.1f %% of frame width" % (scale, half_h, half_v,
                                                          frac * 100.0))
        if frac < WAKE_MIN_WIDTH_FRAC:
            C.refuse("the body would span only %.1f %% of the frame width, below the "
                     "%.0f %% floor -- this is the corner-framing fault, refused before "
                     "the image is written" % (frac * 100.0, WAKE_MIN_WIDTH_FRAC * 100))

        xwake = bb[1] + 1.0
        # THE SYMMETRY PLANE AT THE FRAME EDGE. This is a HALF model: nothing exists at
        # y < 0, so centring on the body's own y-centre spends 0.46 m of frame on white.
        # Putting y = 0 at the right edge (the camera's right vector is -y) fills the
        # frame with data and keeps the same measured 52 % body width.
        fy = scale * aspect
        fz = (bb[4] + bb[5]) / 2.0

        reader.MeshRegions = ["internalMesh"]
        UpdatePipeline(time=float(COARSE_T), proxy=reader)
        p2c = CellDatatoPointData(Input=reader); p2c.CellDataArraytoprocess = ["U"]
        UpdatePipeline(time=float(COARSE_T), proxy=p2c)
        cc = Calculator(Input=p2c); cc.AttributeType = "Point Data"
        cc.ResultArrayName = "Umag"; cc.Function = "mag(U)"
        UpdatePipeline(time=float(COARSE_T), proxy=cc)
        sl = Slice(Input=cc); sl.SliceType = "Plane"
        sl.SliceType.Origin = [xwake, 0.0, 0.0]; sl.SliceType.Normal = [1.0, 0.0, 0.0]
        UpdatePipeline(time=float(COARSE_T), proxy=sl)
        if sl.GetDataInformation().GetNumberOfCells() == 0:
            C.refuse("the wake plane at x = %.3f is empty" % xwake)

        v = _view(size)
        d = Show(sl, v); _flat(d)
        ColorBy(d, ("POINTS", "Umag"))
        lut = GetColorTransferFunction("Umag")
        lut.ApplyPreset("Viridis (matplotlib)", True)
        lut.RescaleTransferFunction(*urange)
        bar = _bar(v, lut, "|U|  [m/s]")
        bar.Position = [0.855, 0.36]      # the 1200-wide frame clipped it at 0.90
        # the camera, set from the measurement rather than by frame_by_extent's box
        v.CameraParallelProjection = 1
        v.CameraPosition = [bb[0] - 8.0, fy, fz]
        v.CameraFocalPoint = [xwake, fy, fz]
        v.CameraViewUp = [0.0, 0.0, 1.0]
        v.CameraParallelScale = scale
        Render(v)
        got = v.CameraParallelScale
        if abs(got - scale) > 1e-6 * max(1.0, scale):
            v.CameraParallelScale = scale       # the first Render resets it; put it back
            Render(v)
            got = v.CameraParallelScale
        if abs(got - scale) > 1e-6 * max(1.0, scale):
            C.refuse("the parallel scale came back %.6f where %.6f was set; an "
                     "unasserted camera setting is a wish" % (got, scale))

        def _finish(view):
            # A SEMI-TRANSPARENT SILHOUETTE, not feature edges. The edge representation
            # draws every feature line of a detailed car -- mirrors, wheel arches,
            # underbody -- and projects them into scribble that reads as noise. A
            # translucent surface gives the outline the review asked for and still lets
            # the wake behind it be read.
            bd = Show(body, view)
            bd.Representation = "Surface"
            bd.ColorArrayName = [None, ""]
            bd.DiffuseColor = [0.18, 0.18, 0.20]; bd.AmbientColor = [0.18, 0.18, 0.20]
            bd.Ambient, bd.Diffuse, bd.Specular = 1.0, 0.0, 0.0
            bd.Opacity = 0.28
        return _render_with_control(v, sl, d, out, "Umag", _finish, size=size)
    finally:
        shutil.rmtree(root2, ignore_errors=True)


def main(argv=()):
    only_fine = "fine-mesh-only" in argv
    only_wake = "wake-only" in argv
    round3 = "round3" in argv
    only_p = "p-panels" in argv
    C.assert_paraview_version()
    C.assert_stamp(STAMP_C, COARSE)
    C.assert_stamp(STAMP_F, FINE)
    cdir = C.facts(COARSE)["case_dir"]
    before = C.run_tree_fingerprint(cdir)
    fine_mesh_dir = os.path.join(C.facts(FINE)["case_dir"], "constant", "polyMesh")
    fine_before = C.run_tree_fingerprint(fine_mesh_dir)

    total, root = 0, None
    try:
        if only_fine:
            raise StopIteration
        if only_p:
            reader, root, n = C.open_case(COARSE, ["p"], [COARSE_T],
                                          decompose_polyhedra=False)
            C.announce("  %s: %s cells at t = %s" % (COARSE, format(n, ","),
                                                     COARSE_T))
            total += p_panels(reader)
            raise StopIteration
        if round3:
            from paraview.simple import (CellDatatoPointData as _C2P,
                                         Calculator as _Cal, Slice as _Sl,
                                         MergeBlocks as _MB, UpdatePipeline as _U)
            reader, root, n = C.open_case(COARSE, ["p", "U"], [COARSE_T],
                                          decompose_polyhedra=False)
            reader.MeshRegions = BODY
            _U(time=float(COARSE_T), proxy=reader)
            _surf = _MB(Input=reader); _U(time=float(COARSE_T), proxy=_surf)
            bbox = _surf.GetDataInformation().GetBounds()
            C.announce("  body bounding box x %.3f to %.3f, y %.3f to %.3f, "
                       "z %.3f to %.3f m" % bbox)
            reader.MeshRegions = ["internalMesh"]
            _U(time=float(COARSE_T), proxy=reader)
            _p = _C2P(Input=reader); _p.CellDataArraytoprocess = ["U"]
            _U(time=float(COARSE_T), proxy=_p)
            _c = _Cal(Input=_p); _c.AttributeType = "Point Data"
            _c.ResultArrayName = "Umag"; _c.Function = "mag(U)"
            _U(time=float(COARSE_T), proxy=_c)
            _s = _Sl(Input=_c); _s.SliceType = "Plane"
            _s.SliceType.Origin = [0.0, 0.02, 0.0]; _s.SliceType.Normal = [0.0, 1.0, 0.0]
            _U(time=float(COARSE_T), proxy=_s)
            urange = _percentiles(_s, "Umag")
            C.announce("  velocity window %.4g..%.4g m/s" % urange)
            total += wake_panel(reader, os.path.join(HERE, "drivaer_umag_wake.png"),
                                urange)
            total += streamline_panel(
                reader, os.path.join(HERE, "drivaer_streamlines.png"), bbox,
                "", urange)
            raise StopIteration
        if only_wake:
            from paraview.simple import (CellDatatoPointData as _C2P,
                                         Calculator as _Cal, Slice as _Sl,
                                         UpdatePipeline as _U)
            reader, root, n = C.open_case(COARSE, ["p", "U"], [COARSE_T],
                                          decompose_polyhedra=False)
            _p = _C2P(Input=reader); _p.CellDataArraytoprocess = ["U"]
            _U(time=float(COARSE_T), proxy=_p)
            _c = _Cal(Input=_p); _c.AttributeType = "Point Data"
            _c.ResultArrayName = "Umag"; _c.Function = "mag(U)"
            _U(time=float(COARSE_T), proxy=_c)
            _s = _Sl(Input=_c); _s.SliceType = "Plane"
            _s.SliceType.Origin = [0.0, 0.02, 0.0]; _s.SliceType.Normal = [0.0, 1.0, 0.0]
            _U(time=float(COARSE_T), proxy=_s)
            urange = _percentiles(_s, "Umag")
            C.announce("  velocity window %.4g..%.4g m/s" % urange)
            total += wake_panel(reader, os.path.join(HERE, "drivaer_umag_wake.png"),
                                urange)
            raise StopIteration
        from paraview.simple import MergeBlocks, UpdatePipeline
        reader, root, n = C.open_case(COARSE, ["p", "U"], [COARSE_T],
                                      decompose_polyhedra=False)
        C.announce("  %s: %s cells at t = %s" % (COARSE, format(n, ","), COARSE_T))

        reader.MeshRegions = BODY
        UpdatePipeline(time=float(COARSE_T), proxy=reader)
        surf = MergeBlocks(Input=reader)
        UpdatePipeline(time=float(COARSE_T), proxy=surf)
        bbox = surf.GetDataInformation().GetBounds()
        prange = _percentiles(surf, "p")
        C.announce("  body bounding box x %.3f to %.3f, y %.3f to %.3f, z %.3f "
                   "to %.3f m" % bbox)
        C.announce("  surface p display window %.4g to %.4g m2/s2 (percentiles "
                   "%g/%g, shared by all three surface panels)"
                   % (prange + (PCT_LO, PCT_HI)))

        base = GEOM + " ; " + REPRO + " ; fields at iteration 1000"
        pnote = base + " ; colour bar %.4g to %.4g m2/s2, ends clamped" % prange
        total += surface_panel(reader, os.path.join(HERE, "drivaer_p_side.png"),
                               (0.0, -1.0, 0.0), (0.0, 0.0, 1.0),
                               pnote + " ; side view", prange)
        total += surface_panel(reader, os.path.join(HERE, "drivaer_p_top.png"),
                               (0.0, 0.0, 1.0), (1.0, 0.0, 0.0),
                               pnote + " ; from above", prange)
        total += surface_panel(reader, os.path.join(HERE, "drivaer_p_rear.png"),
                               (1.0, -0.25, 0.18), (0.0, 0.0, 1.0),
                               pnote + " ; from behind", prange)

        # ONE velocity window for all four velocity panels, measured on the
        # symmetry plane, which carries the whole range from stagnation to wake.
        from paraview.simple import (CellDatatoPointData, Calculator, Slice)
        reader.MeshRegions = ["internalMesh"]
        UpdatePipeline(time=float(COARSE_T), proxy=reader)
        p2c = CellDatatoPointData(Input=reader)
        p2c.CellDataArraytoprocess = ["U"]
        UpdatePipeline(time=float(COARSE_T), proxy=p2c)
        cc = Calculator(Input=p2c); cc.AttributeType = "Point Data"
        cc.ResultArrayName = "Umag"; cc.Function = "mag(U)"
        UpdatePipeline(time=float(COARSE_T), proxy=cc)
        sy = Slice(Input=cc); sy.SliceType = "Plane"
        sy.SliceType.Origin = [0.0, 0.02, 0.0]; sy.SliceType.Normal = [0.0, 1.0, 0.0]
        UpdatePipeline(time=float(COARSE_T), proxy=sy)
        urange = _percentiles(sy, "Umag")
        C.announce("  velocity display window %.4g to %.4g m/s (percentiles %g/%g, "
                   "shared by all four velocity panels)"
                   % (urange + (PCT_LO, PCT_HI)))
        unote = base + " ; colour bar %.4g to %.4g m/s, ends clamped" % urange

        zmid = (bbox[4] + bbox[5]) / 2.0
        xwake = bbox[1] + 1.0
        # THE WHOLE CROSS-SECTION, not a corner of it. The owner's round-2 note is
        # that this panel was "a blur; the plane is too close or the camera zoomed
        # into a corner" -- it was the camera: the frame was 2.0 m by 2.2 m on a
        # half-model whose domain is 4 m by 6.4 m, so the car filled one corner and
        # the rest was free stream. The frame is now the car's own height and
        # half-width with a margin, centred on the car.
        # THE CAR CENTRED, NOT THE FREE STREAM. Round 2 put the frame at y 0..2.2 on a
        # half-body that spans y 0..1.0, and the camera's right vector is -y, so the car
        # sat in one corner and the rest was undisturbed inflow -- which is what "a blur"
        # was. The frame is now the body's own half-width and height with a small margin.
        wb = (xwake, xwake, 0.0, bbox[3] * 1.5, 0.0, bbox[5] * 1.35)
        total += plane_panel(
            reader, os.path.join(HERE, "drivaer_umag_symmetry.png"),
            [0.0, 0.02, 0.0], [0.0, 1.0, 0.0], (0.0, -1.0, 0.0), (0.0, 0.0, 1.0),
            (bbox[0] - 2.5, bbox[1] + 5.0, 0.02, 0.02, 0.0, 2.6),
            unote + " ; symmetry plane at y = 0.02 m", urange)
        total += plane_panel(
            reader, os.path.join(HERE, "drivaer_umag_midheight.png"),
            [0.0, 0.0, zmid], [0.0, 0.0, 1.0], (0.0, 0.0, 1.0), (1.0, 0.0, 0.0),
            (bbox[0] - 2.5, bbox[1] + 5.0, 0.0, 2.5, zmid, zmid),
            unote + " ; horizontal plane at z = %.3f m, body mid-height" % zmid,
            urange)
        total += plane_panel(
            reader, os.path.join(HERE, "drivaer_umag_wake.png"),
            [xwake, 0.0, 0.0], [1.0, 0.0, 0.0], (-1.0, 0.0, 0.0), (0.0, 0.0, 1.0),
            wb,
            unote + " ; cross-section at x = %.3f m, 1.0 m aft of the body" % xwake,
            urange, outline_body=True)
        total += streamline_panel(
            reader, os.path.join(HERE, "drivaer_streamlines.png"), bbox,
            unote + " ; streamlines seeded 1.5 m upstream on a 220-point line",
            urange)
    except StopIteration:
        pass
    finally:
        if root:
            shutil.rmtree(root, ignore_errors=True)

    if not only_fine and not only_p:
        total += mesh_panel(COARSE, COARSE_T, os.path.join(HERE, "drivaer_mesh_coarse.png"),
                            STAMP_C, GEOM + " ; THEIR COARSE MESH on the body "
                            "and wheel patches, 669416 cells in the volume", 32913)
    if not only_p:
        total += mesh_panel(FINE, FINE_T, os.path.join(HERE, "drivaer_mesh_fine.png"),
                            STAMP_F, GEOM + " ; THEIR FINE MESH on the body and wheel "
                            "patches ; the solve on this mesh had not finished when "
                            "this was drawn, so no field panel is taken from it", 101603,
                            arrays=())

    if not only_fine:
        C.assert_run_tree_untouched(cdir, before)
        C.announce("  coarse run tree PROVED unchanged: %s" % cdir)
    if not only_p:
        C.assert_run_tree_untouched(fine_mesh_dir, fine_before)
        C.announce("  fine constant/polyMesh PROVED unchanged: %s" % fine_mesh_dir)
    C.announce("  %s bytes written" % format(total, ","))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except C.RenderRefusal as exc:
        C.announce_error("REFUSED: %s" % exc)
        sys.exit(2)
