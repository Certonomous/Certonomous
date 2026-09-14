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


def _render_with_control(view, src, disp, out, field, add_caption):
    from paraview.simple import (Calculator, Show, Hide, Render, ColorBy,
                                 UpdatePipeline)
    flat = Calculator(Input=src)
    flat.AttributeType = "Point Data"
    flat.ResultArrayName = "CONTROL_CONSTANT"
    flat.Function = "1.0"
    UpdatePipeline(proxy=flat)
    arr = flat.GetPointDataInformation().GetArray("CONTROL_CONSTANT")
    lo, hi = arr.GetComponentRange(0)
    if abs(hi - lo) > 1e-12:
        C.refuse("the control array spans %g to %g and is not constant" % (lo, hi))
    Hide(src, view)
    disp.SetScalarBarVisibility(view, False)
    dn = Show(flat, view)
    ColorBy(dn, ("POINTS", "CONTROL_CONSTANT"))
    _flat(dn)
    dn.SetScalarBarVisibility(view, False)
    Render(view)
    neg = os.path.join(HERE, "_control", "NEGATIVE_constant_" + os.path.basename(out))
    C.save_screenshot(view, neg, size=(1600, 1000))
    Hide(flat, view)
    Show(src, view)
    disp.SetScalarBarVisibility(view, True)
    Render(view)
    pos = os.path.join(HERE, "_control", "POSITIVE_uncaptioned_" + os.path.basename(out))
    C.save_screenshot(view, pos, size=(1600, 1000))
    _assert_painted(pos, neg, field)
    add_caption(view)
    Render(view)
    n = C.save_screenshot(view, out, size=(1600, 1000))
    C.announce("  wrote %s (%s bytes)" % (os.path.basename(out), format(n, ",")))
    return n


def _caption(view, case, stamp, second):
    """NOTHING IS WRITTEN ON THE IMAGE (v2 section 13). The case, the time,
    the geometry and the verdict live in the folder SIDECAR.md and in the act
    beside the figure. `C.assert_stamp` still ran on `stamp` before any pixel
    was drawn, so the verdict guard is kept and only its printing is dropped."""
    return None



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
    st.SeedType.Point1 = [bbox[0] - 1.5, 0.02, 0.02]
    st.SeedType.Point2 = [bbox[0] - 1.5, 0.02, bbox[5] * 1.15]
    st.SeedType.Resolution = 240
    UpdatePipeline(time=float(COARSE_T), proxy=st)
    if st.GetDataInformation().GetNumberOfPoints() == 0:
        C.refuse("no streamline was integrated; nothing would be drawn")
    tube = Tube(Input=st); tube.Radius = 0.012
    UpdatePipeline(time=float(COARSE_T), proxy=tube)
    d = Show(tube, v); _flat(d)
    ColorBy(d, ("POINTS", "Umag"))
    lut = GetColorTransferFunction("Umag"); lut.ApplyPreset(PRESET_U, True)
    lut.RescaleTransferFunction(*urange)
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


def main(argv=()):
    only_fine = "fine-mesh-only" in argv
    only_wake = "wake-only" in argv
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

    if not only_fine:
        total += mesh_panel(COARSE, COARSE_T, os.path.join(HERE, "drivaer_mesh_coarse.png"),
                            STAMP_C, GEOM + " ; THEIR COARSE MESH on the body "
                            "and wheel patches, 669416 cells in the volume", 32913)
    total += mesh_panel(FINE, FINE_T, os.path.join(HERE, "drivaer_mesh_fine.png"),
                        STAMP_F, GEOM + " ; THEIR FINE MESH on the body and wheel "
                        "patches ; the solve on this mesh had not finished when "
                        "this was drawn, so no field panel is taken from it", 101603,
                        arrays=())

    if not only_fine:
        C.assert_run_tree_untouched(cdir, before)
        C.announce("  coarse run tree PROVED unchanged: %s" % cdir)
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
