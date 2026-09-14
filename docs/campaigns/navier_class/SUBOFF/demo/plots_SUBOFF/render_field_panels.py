#!/usr/bin/env python3
"""ParaView panels for the SUBOFF drift-sweep demo folder, v2.

    xvfb-run -a pvpython docs/campaigns/navier_class/SUBOFF/demo/plots_SUBOFF/render_field_panels.py

THE ACT IS GRADED `NOT A RESULT` (`L1M_GRADE/A1H_L1M_GRADE.json`, 2026-09-14T00:18Z):
all seven points fail the strict completion rule. Every panel here is a picture of an
INCOMPLETE SOLVE and the folder's SIDECAR.md says so on its first screen. The
`SUBOFF_L1M_*` CASE_FACTS rows own only `PENDING`, so `assert_stamp` refuses any other
verdict word on the stamps these drivers check before rendering.

NOTHING IS RECONSTRUCTED AND NOTHING IS WRITTEN INTO A GRADED TREE.
The brief allowed reconstructing each point's last time into a symlinked scratch. It
turned out not to be necessary, which is strictly better: ParaView reads the
DECOMPOSED case directly once `CaseType` is set AND the pipeline INFORMATION is
refreshed. **That refresh is the whole bug behind the blank panels of the first
attempt**: without it the reader reports `TimestepValues == [0.0]` on a case whose
processor directories plainly hold t = 2865 and 2880, and a panel asked for the
latest time silently drew the initial condition -- or nothing. The time actually
loaded is now ASSERTED to be in `TimestepValues` before a pixel is drawn.

Panels, all at each point's own last written time:
    suboff_mesh_l1m.png          the coarse mirror mesh on hull and sail
    suboff_mesh_sail_cut.png     a cut through the sail showing the wall layers
    suboff_p_side_b*.png         surface pressure, side view, at 0, +-8, +-12
    suboff_p_top_b*.png          surface pressure, from above, same angles
    suboff_umag_mid_b*.png       |U| on the mid-depth plane y = 0, same angles
    suboff_wake_stern_b*.png     cross-section aft of the stern, 0 and +12
    suboff_wake_sail_bp12.png    cross-section aft of the sail, +12
    suboff_streamlines_bp12.png  streamlines over the sail, +12
    suboff_q_bp12.png            Q-criterion iso-surface of the sail vortices, +12
"""
import os, shutil, sys, tempfile

REPO = "/home/ubuntu/Certonomous"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(REPO, "sdk"))
sys.path.insert(0, os.path.join(REPO, "verification/runs/F14-cooling-ladder/K2h_runs"))
sys.path.insert(0, os.path.join(REPO, "docs/campaigns/F14-cooling-ladder/demo/render_K2bU3R3_paraview"))
import demo3d_render_common as C
from workflows.act_paraview_style import style_view, colour_bar
import render_k2h_l3 as K2H

SWEEP = os.path.join(REPO, "verification/runs/navier_class/SUBOFF_A1H_DRIFT/L1M_SWEEP")
MESHCASE = "SUBOFF_L1M_MESH"
CASE = "SUBOFF_L1M_BETA_P00"          # the CASE_FACTS row every point is stamped through
CELLS = 6537226
BODY = ["patch/hull", "patch/sail"]
BODY_FACES = 233372 + 166582
CONTROL_MARGIN = 8.0
MIN_FIELD_PX = 20000
PCT_LO, PCT_HI = 2.0, 98.0
ANGLES = [("m12", -12), ("m08", -8), ("p00", 0), ("p08", 8), ("p12", 12)]
STAMP = "SUBOFF_L1M_BETA_P00 ; 6537226 cells ; simpleFoam ; PENDING"
MESH_STAMP = "SUBOFF_L1M_MESH ; 6537226 cells ; the L1 mirror ; PENDING"


# ---------------------------------------------------------------- staging, read-only
def stage(case_dir, name):
    root = tempfile.mkdtemp(prefix="suboff_%s_" % name)
    for sub in ("constant", "system"):
        os.symlink(os.path.join(case_dir, sub), os.path.join(root, sub))
    for d in sorted(os.listdir(case_dir)):
        if d.startswith("processor"):
            os.symlink(os.path.join(case_dir, d), os.path.join(root, d))
    foam = os.path.join(root, "%s.foam" % name)
    open(foam, "w").close()
    return root, foam


def open_decomposed(case_dir, name, arrays):
    """Open a decomposed case and PROVE both the mesh and the time.

    `Refresh()` before reading `TimestepValues` is not optional -- see the module
    docstring. The time is then asserted present, so a panel can never be drawn at a
    time the reader silently fell back to.
    """
    from paraview.simple import OpenFOAMReader, UpdatePipeline
    root, foam = stage(case_dir, name)
    r = OpenFOAMReader(FileName=foam)
    r.CaseType = "Decomposed Case"
    r.Decomposepolyhedra = 0
    r.Refresh()
    r.UpdatePipelineInformation()
    times = [t for t in list(r.TimestepValues or []) if t > 0]
    if not times:
        shutil.rmtree(root, ignore_errors=True)
        C.refuse("%s: the reader found no time beyond 0; a field panel would be the "
                 "initial condition" % name)
    t = max(times)
    r.MeshRegions = ["internalMesh"]
    r.CellArrays = list(arrays)
    UpdatePipeline(time=float(t), proxy=r)
    n = r.GetDataInformation().GetNumberOfCells()
    if n != CELLS:
        shutil.rmtree(root, ignore_errors=True)
        C.refuse("%s loaded %d cells where the mesh record says %d" % (name, n, CELLS))
    for a in arrays:
        if r.GetDataInformation().GetCellDataInformation().GetArrayInformation(a) is None:
            shutil.rmtree(root, ignore_errors=True)
            C.refuse("%s carries no field %r at t = %s" % (name, a, t))
    C.announce("  %s: %s cells at t = %g (times seen: %s)"
               % (name, format(n, ","), t, times))
    return r, root, t


# ---------------------------------------------------------------- view furniture
def _view(size=(1600, 1000)):
    from paraview.simple import CreateRenderView, Render
    v = CreateRenderView(); style_view(v, size); Render(v)
    return v


def _flat(d):
    d.Ambient, d.Diffuse, d.Specular = 1.0, 0.0, 0.0


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
            vals.append(x); break
    if not vals:
        C.refuse("no %s array was fetched" % name)
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
    if body.sum() < 100:
        return 0.0, int(body.sum())
    mx = np.maximum(rgb[body].max(axis=1), 1e-6)
    return float(((rgb[body, 0] - rgb[body, 2]) / mx).std()), int(body.sum())


def _assert_painted(pos, neg, field):
    p, npx = K2H._colour_spread(pos)
    n, _ = K2H._colour_spread(neg)
    cp, _ = _spread_core(pos)
    cn, _ = _spread_core(neg)
    C.announce("      control %s: %.5f over %s px vs %.5f (%.1fx) ; interior %.5f vs "
               "%.5f (%.1fx)" % (field, p, format(npx, ","), n, p / max(n, 1e-9),
                                 cp, cn, cp / max(cn, 1e-9)))
    if npx < MIN_FIELD_PX:
        C.refuse("BLANK FRAME for %r: %s pixels, below the %s floor"
                 % (field, format(npx, ","), format(MIN_FIELD_PX, ",")))
    if n <= 0.0:
        C.refuse("NO CONTROL for %r: the constant arm spread is exactly zero" % field)
    if cp < CONTROL_MARGIN * max(cn, 1e-9):
        C.refuse("COLOUR CONTROL FAILED for %r: interior %.5f vs %.5f" % (field, cp, cn))


def paint(view, src, disp, out, field, label, lut):
    """Negative arm, positive arm, guard, then the bar. No text on the image."""
    from paraview.simple import Calculator, Show, Hide, Render, ColorBy, UpdatePipeline
    flat = Calculator(Input=src)
    flat.AttributeType = "Point Data"
    flat.ResultArrayName = "CONTROL_CONSTANT"; flat.Function = "1.0"
    UpdatePipeline(proxy=flat)
    Hide(src, view); disp.SetScalarBarVisibility(view, False)
    dn = Show(flat, view); ColorBy(dn, ("POINTS", "CONTROL_CONSTANT")); _flat(dn)
    dn.SetScalarBarVisibility(view, False); Render(view)
    neg = os.path.join(HERE, "_control", "NEG_" + os.path.basename(out))
    C.save_screenshot(view, neg, size=(1600, 1000))
    Hide(flat, view); Show(src, view); Render(view)
    pos = os.path.join(HERE, "_control", "POS_" + os.path.basename(out))
    C.save_screenshot(view, pos, size=(1600, 1000))
    _assert_painted(pos, neg, field)
    disp.SetScalarBarVisibility(view, True)
    colour_bar(view, lut, label)
    Render(view)
    n = C.save_screenshot(view, out, size=(1600, 1000))
    C.announce("  wrote %s (%s bytes)" % (os.path.basename(out), format(n, ",")))
    return n


def ink_only(view, out, what):
    from paraview.simple import Render
    Render(view)
    n = C.save_screenshot(view, out, size=(1600, 1000))
    _, px = K2H._colour_spread(out)
    if px < MIN_FIELD_PX:
        C.refuse("%s drew only %d body pixels" % (os.path.basename(out), px))
    C.announce("  wrote %s (%s bytes, %s body px)"
               % (os.path.basename(out), format(n, ","), format(px, ",")))
    return n


# ---------------------------------------------------------------- panels
def surface_panels(r, t, tag, out_side, out_top, prange):
    from paraview.simple import (MergeBlocks, Show, Render, ColorBy,
                                 GetColorTransferFunction, UpdatePipeline)
    total = 0
    r.MeshRegions = BODY
    UpdatePipeline(time=float(t), proxy=r)
    surf = MergeBlocks(Input=r); UpdatePipeline(time=float(t), proxy=surf)
    info = surf.GetDataInformation()
    if info.GetNumberOfCells() != BODY_FACES:
        C.refuse("hull+sail rendered %d faces, not %d"
                 % (info.GetNumberOfCells(), BODY_FACES))
    b = info.GetBounds()
    for out, direction, up in ((out_side, (0.0, 0.0, -1.0), (0.0, 1.0, 0.0)),
                               (out_top, (0.0, 1.0, 0.0), (-1.0, 0.0, 0.0))):
        v = _view()
        d = Show(surf, v); _flat(d)
        ColorBy(d, ("CELLS", "p"))
        # VIRIDIS AND NOT COOL-TO-WARM on this body: the hull is a streamlined shape whose
        # surface p varies little over most of its length, and Cool to Warm puts WHITE in
        # the middle, so the real field measured only 5.7x against the constant arm on an
        # 8x floor. Viridis runs blue to yellow, a much larger red/blue swing, and the
        # SAME field then measures far above the floor. THE FLOOR WAS NOT MOVED.
        lut = GetColorTransferFunction("p"); lut.ApplyPreset("Viridis (matplotlib)", True)
        lut.RescaleTransferFunction(*prange)
        C.frame_by_extent(v, [(b[0] + b[1]) / 2, (b[2] + b[3]) / 2, (b[4] + b[5]) / 2],
                          direction, up=up, bounds=b, pad=1.04)
        total += paint(v, surf, d, out, "p", "p  [m2/s2]", lut)
    return total, b


def plane_panel(r, t, out, origin, normal, direction, up, bounds, urange, name="Umag"):
    from paraview.simple import (CellDatatoPointData, Calculator, Slice, Show,
                                 Render, ColorBy, GetColorTransferFunction,
                                 UpdatePipeline)
    r.MeshRegions = ["internalMesh"]
    UpdatePipeline(time=float(t), proxy=r)
    p2c = CellDatatoPointData(Input=r)
    p2c.CellDataArraytoprocess = ["U", "p"]
    UpdatePipeline(time=float(t), proxy=p2c)
    cc = Calculator(Input=p2c); cc.AttributeType = "Point Data"
    cc.ResultArrayName = name; cc.Function = "mag(U)"
    UpdatePipeline(time=float(t), proxy=cc)
    if cc.GetPointDataInformation().GetArray(name) is None:
        C.refuse("the %s calculator produced no array" % name)
    s = Slice(Input=cc); s.SliceType = "Plane"
    s.SliceType.Origin = list(origin); s.SliceType.Normal = list(normal)
    UpdatePipeline(time=float(t), proxy=s)
    if s.GetDataInformation().GetNumberOfCells() == 0:
        C.refuse("the plane at %r is empty" % (origin,))
    v = _view()
    d = Show(s, v); _flat(d)
    ColorBy(d, ("POINTS", name))
    lut = GetColorTransferFunction(name); lut.ApplyPreset("Viridis (matplotlib)", True)
    lut.RescaleTransferFunction(*urange)
    C.frame_by_extent(v, [(bounds[0] + bounds[1]) / 2, (bounds[2] + bounds[3]) / 2,
                          (bounds[4] + bounds[5]) / 2], direction, up=up,
                      bounds=bounds, pad=1.04)
    return paint(v, s, d, out, name, "|U|  [m/s]", lut)


def streamlines_panel(r, t, out, bbox, urange):
    from paraview.simple import (CellDatatoPointData, Calculator, StreamTracer, Tube,
                                 Show, Render, ColorBy, GetColorTransferFunction,
                                 UpdatePipeline)
    r.MeshRegions = ["internalMesh"]
    UpdatePipeline(time=float(t), proxy=r)
    p2c = CellDatatoPointData(Input=r); p2c.CellDataArraytoprocess = ["U"]
    UpdatePipeline(time=float(t), proxy=p2c)
    cc = Calculator(Input=p2c); cc.AttributeType = "Point Data"
    cc.ResultArrayName = "Umag"; cc.Function = "mag(U)"
    UpdatePipeline(time=float(t), proxy=cc)
    st = StreamTracer(Input=cc, SeedType="Line")
    st.Vectors = ["POINTS", "U"]
    st.MaximumStreamlineLength = 8.0
    st.SeedType.Point1 = [0.9, 0.30, -0.25]
    st.SeedType.Point2 = [0.9, 0.30, 0.25]
    st.SeedType.Resolution = 240
    UpdatePipeline(time=float(t), proxy=st)
    if st.GetDataInformation().GetNumberOfPoints() == 0:
        C.refuse("no streamline was integrated over the sail")
    # RADIUS 0.014, NOT 0.006, AND THE REASON IS THE CONTROL RATHER THAN TASTE. At
    # 0.006 the tubes are so thin that most of their pixels are antialiased EDGE, which
    # carries colour in the constant-array arm too: the control measured 5.2x on an 8x
    # floor with a real positive of 0.175. Thicker tubes are mostly interior, so the
    # same field measures clear of the floor. THE FLOOR WAS NOT MOVED.
    tube = Tube(Input=st); tube.Radius = 0.014
    UpdatePipeline(time=float(t), proxy=tube)
    v = _view()
    d = Show(tube, v); _flat(d)
    ColorBy(d, ("POINTS", "Umag"))
    lut = GetColorTransferFunction("Umag"); lut.ApplyPreset("Viridis (matplotlib)", True)
    lut.RescaleTransferFunction(*urange)
    C.frame_by_extent(v, [1.6, 0.15, 0.0], (0.35, 0.55, -0.76), up=(0.0, 1.0, 0.0),
                      bounds=(0.6, 3.0, -0.35, 0.60, -0.45, 0.45), pad=1.05)
    return paint(v, tube, d, out, "Umag", "|U|  [m/s]", lut)


def q_panel(r, t, out, urange):
    """Q-criterion iso-surface of the sail vortices, coloured by speed."""
    from paraview.simple import (CellDatatoPointData, Gradient, Contour, Calculator,
                                 Clip, Show, Render, ColorBy,
                                 GetColorTransferFunction, UpdatePipeline)
    r.MeshRegions = ["internalMesh"]
    UpdatePipeline(time=float(t), proxy=r)
    p2c = CellDatatoPointData(Input=r); p2c.CellDataArraytoprocess = ["U"]
    UpdatePipeline(time=float(t), proxy=p2c)
    clip = Clip(Input=p2c); clip.ClipType = "Box"
    clip.ClipType.Position = [0.6, -0.35, -0.45]
    clip.ClipType.Length = [2.6, 1.0, 0.9]
    clip.Invert = 1
    UpdatePipeline(time=float(t), proxy=clip)
    g = Gradient(Input=clip)
    g.ScalarArray = ["POINTS", "U"]
    g.ComputeQCriterion = 1
    g.QCriterionArrayName = "Q"
    UpdatePipeline(time=float(t), proxy=g)
    if g.GetPointDataInformation().GetArray("Q") is None:
        C.refuse("the Gradient filter produced no Q array")
    qlo, qhi = _percentiles(g, "Q")
    level = max(qhi, 1.0)
    C.announce("      Q window %.4g to %.4g ; iso at %.4g" % (qlo, qhi, level))
    cont = Contour(Input=g); cont.ContourBy = ["POINTS", "Q"]
    cont.Isosurfaces = [level]
    UpdatePipeline(time=float(t), proxy=cont)
    ncell = cont.GetDataInformation().GetNumberOfCells()
    if ncell == 0:
        C.refuse("the Q = %g iso-surface is empty" % level)
    C.announce("      Q iso-surface: %s triangles" % format(ncell, ","))
    calc = Calculator(Input=cont); calc.AttributeType = "Point Data"
    calc.ResultArrayName = "Umag"; calc.Function = "mag(U)"
    UpdatePipeline(time=float(t), proxy=calc)
    v = _view()
    d = Show(calc, v); _flat(d)
    ColorBy(d, ("POINTS", "Umag"))
    lut = GetColorTransferFunction("Umag"); lut.ApplyPreset("Viridis (matplotlib)", True)
    lut.RescaleTransferFunction(*urange)
    C.frame_by_extent(v, [1.7, 0.15, 0.0], (0.35, 0.55, -0.76), up=(0.0, 1.0, 0.0),
                      bounds=(0.6, 3.2, -0.35, 0.60, -0.45, 0.45), pad=1.05)
    return paint(v, calc, d, out, "Umag", "|U|  [m/s]", lut)


def mesh_panels(out_body, out_cut):
    from paraview.simple import (OpenFOAMReader, MergeBlocks, Slice, Show, Render,
                                 UpdatePipeline)
    mesh_dir = C.facts(MESHCASE)["case_dir"]
    root, foam = stage(mesh_dir, "mesh")
    total = 0
    try:
        r = OpenFOAMReader(FileName=foam)
        r.CaseType = "Reconstructed Case"; r.Decomposepolyhedra = 0
        r.MeshRegions = ["internalMesh"]
        UpdatePipeline(proxy=r)
        n = r.GetDataInformation().GetNumberOfCells()
        if n != CELLS:
            C.refuse("the mirror loaded %d cells, not %d" % (n, CELLS))
        C.announce("  %s: %s cells" % (MESHCASE, format(n, ",")))
        r.MeshRegions = BODY
        UpdatePipeline(proxy=r)
        surf = MergeBlocks(Input=r); UpdatePipeline(proxy=surf)
        info = surf.GetDataInformation()
        if info.GetNumberOfCells() != BODY_FACES:
            C.refuse("hull+sail rendered %d faces, not %d"
                     % (info.GetNumberOfCells(), BODY_FACES))
        v = _view()
        d = Show(surf, v); _flat(d)
        d.ColorArrayName = [None, ""]
        d.DiffuseColor = [0.66, 0.69, 0.74]; d.AmbientColor = [0.66, 0.69, 0.74]
        d.Representation = "Surface With Edges"
        d.EdgeColor = [0.12, 0.12, 0.12]; d.LineWidth = 0.25
        b = info.GetBounds()
        C.announce("  body bbox x %.3f..%.3f y %.3f..%.3f z %.3f..%.3f" % b)
        C.frame_by_extent(v, [(b[0] + b[1]) / 2, (b[2] + b[3]) / 2, (b[4] + b[5]) / 2],
                          (0.35, 0.45, -0.82), up=(0.0, 1.0, 0.0), bounds=b, pad=1.04)
        total += ink_only(v, out_body, "mirror mesh")

        # the cut through the sail, framed on the sail and its wall layers
        r.MeshRegions = ["internalMesh"]
        UpdatePipeline(proxy=r)
        s = Slice(Input=r); s.SliceType = "Plane"
        s.SliceType.Origin = [0.0, 0.0, 0.0]; s.SliceType.Normal = [0.0, 0.0, 1.0]
        UpdatePipeline(proxy=s)
        ncut = s.GetDataInformation().GetNumberOfCells()
        if ncut == 0:
            C.refuse("the sail cut is empty")
        C.announce("  sail cut: %s cells in the plane" % format(ncut, ","))
        v2 = _view()
        d2 = Show(s, v2); _flat(d2)
        d2.ColorArrayName = [None, ""]
        d2.DiffuseColor = [0.90, 0.91, 0.93]; d2.AmbientColor = [0.90, 0.91, 0.93]
        d2.Representation = "Surface With Edges"
        d2.EdgeColor = [0.10, 0.10, 0.10]; d2.LineWidth = 0.3
        C.frame_by_extent(v2, [1.35, 0.34, 0.0], (0.0, 0.0, -1.0), up=(0.0, 1.0, 0.0),
                          bounds=(0.85, 1.85, 0.10, 0.58, 0.0, 0.0), pad=1.02)
        total += ink_only(v2, out_cut, "sail cut")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    return total


# ---------------------------------------------------------------- main
def main(argv=()):
    only_extras = "p12-extras-only" in argv
    C.assert_paraview_version()
    C.assert_stamp(STAMP, CASE)
    C.assert_stamp(MESH_STAMP, MESHCASE)
    mesh_dir = C.facts(MESHCASE)["case_dir"]
    mesh_before = C.run_tree_fingerprint(os.path.join(mesh_dir, "constant", "polyMesh"))
    sweep_before = {os.path.join(SWEEP, "BETA_%s" % tag):
                    C.run_tree_fingerprint(os.path.join(SWEEP, "BETA_%s" % tag))
                    for tag, _ in ANGLES}

    total = 0
    if not only_extras:
        total += mesh_panels(os.path.join(HERE, "suboff_mesh_l1m.png"),
                             os.path.join(HERE, "suboff_mesh_sail_cut.png"))

    # ONE display window per quantity across ALL angles, measured on the +12 case:
    # a per-angle autoscale would make five angles look alike that are not.
    prange = urange = None
    for tag, beta in ANGLES:
        if only_extras and tag != "p12":
            continue
        cdir = os.path.join(SWEEP, "BETA_%s" % tag)
        r, root, t = open_decomposed(cdir, "beta_%s" % tag, ["p", "U"])
        try:
            from paraview.simple import (MergeBlocks, UpdatePipeline,
                                         CellDatatoPointData, Calculator, Slice)
            if prange is None:
                r.MeshRegions = BODY
                UpdatePipeline(time=float(t), proxy=r)
                sfc = MergeBlocks(Input=r); UpdatePipeline(time=float(t), proxy=sfc)
                prange = _percentiles(sfc, "p")
                r.MeshRegions = ["internalMesh"]
                UpdatePipeline(time=float(t), proxy=r)
                p2c = CellDatatoPointData(Input=r); p2c.CellDataArraytoprocess = ["U"]
                UpdatePipeline(time=float(t), proxy=p2c)
                cc = Calculator(Input=p2c); cc.AttributeType = "Point Data"
                cc.ResultArrayName = "Umag"; cc.Function = "mag(U)"
                UpdatePipeline(time=float(t), proxy=cc)
                sl = Slice(Input=cc); sl.SliceType = "Plane"
                sl.SliceType.Origin = [0.0, 0.0, 0.0]
                sl.SliceType.Normal = [0.0, 1.0, 0.0]
                UpdatePipeline(time=float(t), proxy=sl)
                urange = _percentiles(sl, "Umag")
                C.announce("  SHARED windows: p %.4g..%.4g m2/s2 ; |U| %.4g..%.4g m/s"
                           % (prange + urange))
            if only_extras:
                from paraview.simple import MergeBlocks as _MB
                r.MeshRegions = BODY
                UpdatePipeline(time=float(t), proxy=r)
                _s = _MB(Input=r); UpdatePipeline(time=float(t), proxy=_s)
                prange = _percentiles(_s, "p")
                b = _s.GetDataInformation().GetBounds()
                total += streamlines_panel(r, t, os.path.join(HERE, "suboff_streamlines_bp12.png"), b, urange)
                total += q_panel(r, t, os.path.join(HERE, "suboff_q_bp12.png"), urange)
                continue
            n, b = surface_panels(r, t, tag,
                                  os.path.join(HERE, "suboff_p_side_b%s.png" % tag),
                                  os.path.join(HERE, "suboff_p_top_b%s.png" % tag),
                                  prange)
            total += n
            total += plane_panel(r, t,
                                 os.path.join(HERE, "suboff_umag_mid_b%s.png" % tag),
                                 [0.0, 0.0, 0.0], [0.0, 1.0, 0.0],
                                 (0.0, 1.0, 0.0), (-1.0, 0.0, 0.0),
                                 (b[0] - 0.6, b[1] + 2.2, 0.0, 0.0, -0.8, 0.8),
                                 urange)
            if tag in ("p00", "p12"):
                xw = b[1] + 0.30
                total += plane_panel(r, t,
                                     os.path.join(HERE, "suboff_wake_stern_b%s.png" % tag),
                                     [xw, 0.0, 0.0], [1.0, 0.0, 0.0],
                                     (-1.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                                     (xw, xw, -0.5, 0.7, -0.6, 0.6), urange)
            if tag == "p12":
                total += plane_panel(r, t,
                                     os.path.join(HERE, "suboff_wake_sail_bp12.png"),
                                     [2.00, 0.0, 0.0], [1.0, 0.0, 0.0],
                                     (-1.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                                     (2.00, 2.00, -0.5, 0.7, -0.6, 0.6), urange)
                total += streamlines_panel(r, t,
                                           os.path.join(HERE, "suboff_streamlines_bp12.png"),
                                           b, urange)
                total += q_panel(r, t, os.path.join(HERE, "suboff_q_bp12.png"), urange)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    C.assert_run_tree_untouched(os.path.join(mesh_dir, "constant", "polyMesh"),
                                mesh_before)
    for d, fp in sweep_before.items():
        C.assert_run_tree_untouched(d, fp)
    C.announce("  all five graded trees and the mirror PROVED unchanged")
    C.announce("  %s bytes written" % format(total, ","))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except C.RenderRefusal as exc:
        C.announce_error("REFUSED: %s" % exc)
        sys.exit(2)
