#!/usr/bin/env python3
"""ParaView panels for the CRM wing multipoint primals, MP_R2.

    xvfb-run -a pvpython docs/campaigns/dafoam/CRM_WING_M085/demo/plots_CRM_MP/render_field_panels.py

    crm_mesh_wing.png        the wing wall patch AS MESHED, one panel -- all three
                             conditions share this mesh
    crm_mesh_symmetry.png    a symmetry-plane cut showing the volume mesh
    crm_p_cl04.png           wall-patch pressure, C_L target 0.400, alpha 1.32496937 deg
    crm_p_cl05.png                              C_L target 0.500, alpha 2.11023869 deg
    crm_p_cl06.png                              C_L target 0.600, alpha 2.88211463 deg

THE THREE PRESSURE PANELS SHARE ONE CAMERA AND ONE COLOUR RANGE, measured across all
three, so they compare. A per-panel autoscale would make three conditions look alike
that are not.

BASELINE GEOMETRY AT THREE TRIMMED LIFT CONDITIONS. No design iteration has ever
completed in this item; these are ITERATION-ZERO fields. Nothing is captioned
optimised, improved or before/after, and no text is drawn on any image at all.

READ-ONLY, AND SAFE WHILE THE RUN IS LIVE. Each condition writes ONCE, at the end of
its primal (`writeControl timeStep`, `writeInterval 2000`, `purgeWrite 0`), and all
three completed before this ran, so the `2000` directories are static. The live part
of the run is the adjoint and does not touch them. Nothing is reconstructed: the
decomposed case is read directly, and `constant/polyMesh` is fingerprint-asserted
unchanged afterwards.
"""
import os, shutil, sys, tempfile

REPO = "/home/ubuntu/Certonomous"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(REPO, "sdk"))
sys.path.insert(0, os.path.join(REPO, "verification/runs/F14-cooling-ladder/K2h_runs"))
import demo3d_render_common as C
from workflows.act_paraview_style import style_view, colour_bar
import render_k2h_l3 as K2H

CELLS = 579072
WING = ["patch/wing"]
TIME = "2000"
CONDS = [("MP04", "cl04", 0.400, 1.32496937),
         ("MP05", "cl05", 0.500, 2.11023869),
         ("MP06", "cl06", 0.600, 2.88211463)]
CONTROL_MARGIN = 8.0
MIN_FIELD_PX = 20000
PCT_LO, PCT_HI = 2.0, 98.0


def stage(case_dir, name):
    root = tempfile.mkdtemp(prefix="crm_%s_" % name)
    for sub in ("constant", "system"):
        src = os.path.join(case_dir, sub)
        if not os.path.isdir(src):
            shutil.rmtree(root, ignore_errors=True)
            C.refuse("%s has no %s" % (case_dir, sub))
        os.symlink(src, os.path.join(root, sub))
    n = 0
    for d in sorted(os.listdir(case_dir)):
        if d.startswith("processor"):
            os.symlink(os.path.join(case_dir, d), os.path.join(root, d)); n += 1
    if n == 0:
        shutil.rmtree(root, ignore_errors=True)
        C.refuse("%s has no processor directories" % case_dir)
    foam = os.path.join(root, "%s.foam" % name)
    open(foam, "w").close()
    return root, foam, n


def open_case(key, name, arrays):
    """Open the decomposed case and PROVE the mesh, the time and the fields.

    `Refresh()` before reading `TimestepValues` is not optional: without it the
    reader reports `[0.0]` on a case whose processor directories hold 2000, and a
    panel asked for the latest time silently draws the initial condition.
    """
    from paraview.simple import OpenFOAMReader, UpdatePipeline
    case_dir = C.facts(key)["case_dir"]
    root, foam, nproc = stage(case_dir, name)
    r = OpenFOAMReader(FileName=foam)
    r.CaseType = "Decomposed Case"
    r.Decomposepolyhedra = 0
    r.Refresh(); r.UpdatePipelineInformation()
    # TAKE THE LATEST NON-ZERO TIME THE READER ACTUALLY OFFERS -- DO NOT ASK FOR 2000.
    # MEASURED: this driver refused on `cl06` with "t = 2000 is not among the reader's
    # times [0.0001]". Nothing was lost -- DAFoam RESETS runTime for the adjoint and the
    # converged directory was RENAMED from `2000` to `0.0001`, files untouched (their
    # own mtimes are the primal's finish, only the parent directory's changed). A
    # hard-coded time is a reader that cannot survive a clock reset. The assertion is
    # KEPT and WIDENED: exactly one non-zero time must exist, and it must not be 0 --
    # so an initial condition still cannot be drawn and labelled the answer.
    times = sorted(float(t) for t in list(r.TimestepValues or []))
    nonzero = [t for t in times if t > 0.0]
    if len(nonzero) != 1:
        shutil.rmtree(root, ignore_errors=True)
        C.refuse("%s: expected exactly one non-zero time, the reader offers %r"
                 % (name, times))
    t_use = nonzero[0]
    r.MeshRegions = ["internalMesh"]
    r.CellArrays = list(arrays)
    UpdatePipeline(time=t_use, proxy=r)
    n = r.GetDataInformation().GetNumberOfCells()
    if n != CELLS:
        shutil.rmtree(root, ignore_errors=True)
        C.refuse("%s loaded %d cells where the record says %d" % (name, n, CELLS))
    for a in arrays:
        if r.GetDataInformation().GetCellDataInformation().GetArrayInformation(a) is None:
            shutil.rmtree(root, ignore_errors=True)
            C.refuse("%s carries no field %r at t = %s" % (name, a, TIME))
    C.announce("  %s: %s cells, %d ranks, drawing t = %g (times offered %r)"
               % (name, format(n, ","), nproc, t_use, times))
    return r, root, t_use


def _view(size=(1600, 1000)):
    from paraview.simple import CreateRenderView, Render
    v = CreateRenderView(); style_view(v, size); Render(v)
    return v


def _flat(d):
    d.Ambient, d.Diffuse, d.Specular = 1.0, 0.0, 0.0


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


def ink_only(view, out):
    from paraview.simple import Render
    Render(view)
    n = C.save_screenshot(view, out, size=(1600, 1000))
    _, px = K2H._colour_spread(out)
    if px < MIN_FIELD_PX:
        C.refuse("%s drew only %d body pixels" % (os.path.basename(out), px))
    C.announce("  wrote %s (%s bytes, %s body px)"
               % (os.path.basename(out), format(n, ","), format(px, ",")))
    return n


def wing_surface(r, T_USE, size=(1600, 1000)):
    from paraview.simple import MergeBlocks, UpdatePipeline
    r.MeshRegions = WING
    UpdatePipeline(time=float(T_USE), proxy=r)
    s = MergeBlocks(Input=r); UpdatePipeline(time=float(T_USE), proxy=s)
    info = s.GetDataInformation()
    if info.GetNumberOfCells() == 0:
        C.refuse("the wing patch rendered no faces")
    return s, info


def p_range(src):
    """The range of p ON THE WALL, fetched from the surface actually being drawn.

    MEASURED, AND IT IS THE SAME FAULT TWICE IN ONE NIGHT. `GetComponentRange` on the
    extracted surface reported 40,802.8 to 153,352 Pa -- the VOLUME's range, carrying
    the shock and the stagnation point. The wall itself spans about 97,000 to 120,300
    Pa, so painting it on a 40.8-153.4 kPa ramp squeezed every wall panel into the
    middle third of the colour map and the colour control refused at 6.1x on an 8x
    floor. The wing surface is ~29,000 cells, so fetching it is cheap and gives the
    range of the thing on screen rather than of the thing it was cut from.
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
        for att in (b.GetCellData(), b.GetPointData()):
            a = att.GetArray("p")
            if a is not None:
                vals.append(numpy_support.vtk_to_numpy(a)); break
    if not vals:
        C.refuse("no p array fetched from the wing surface")
    a = np.concatenate(vals)
    # A DISPLAY WINDOW AT THE 2nd/98th PERCENTILE, the same convention every other
    # folder in this repository uses, and for the same measured reason. The wall's FULL
    # range is 40,803 to 153,352 Pa, but those extremes live in a few cells at the
    # suction peak and the leading-edge stagnation point; stretched to them, the bulk of
    # the wing paints in the middle third of the ramp and the colour control refused at
    # 6.1x on an 8x floor. The window is printed on this run's own output and stated in
    # the sidecar; nothing is removed from the data and the ends are clamped.
    lo, hi = float(np.percentile(a, PCT_LO)), float(np.percentile(a, PCT_HI))
    C.announce("      wall p: full %.6g..%.6g Pa ; display window %.6g..%.6g "
               "(percentiles %g/%g)" % (a.min(), a.max(), lo, hi, PCT_LO, PCT_HI))
    return lo, hi


def main():
    C.assert_paraview_version()
    for key, tag, cl, al in CONDS:
        C.assert_stamp("CRM_MP_%s ; 579072 cells ; DARhoSimpleCFoam ; PENDING" % key,
                       "CRM_MP_%s" % key)
    before = {}
    for key, tag, cl, al in CONDS:
        d = os.path.join(C.facts("CRM_MP_%s" % key)["case_dir"], "constant", "polyMesh")
        before[d] = C.run_tree_fingerprint(d)

    total = 0
    # ---- ONE shared pressure range, measured over ALL THREE conditions ----
    lo = hi = None
    bnds = None
    for key, tag, cl, al in CONDS:
        r, root, T_USE = open_case("CRM_MP_%s" % key, tag, ["p", "U"])
        try:
            s, info = wing_surface(r, T_USE)
            a, b = p_range(s)
            lo = a if lo is None else min(lo, a)
            hi = b if hi is None else max(hi, b)
            if bnds is None:
                bnds = info.GetBounds()
        finally:
            shutil.rmtree(root, ignore_errors=True)
    C.announce("  SHARED p range MEASURED over all three conditions: %.6g to %.6g Pa"
               % (lo, hi))
    C.announce("  wing bounds x %.4f..%.4f y %.4f..%.4f z %.4f..%.4f" % bnds)

    focal = [(bnds[0] + bnds[1]) / 2, (bnds[2] + bnds[3]) / 2, (bnds[4] + bnds[5]) / 2]
    view_dir, view_up = (0.35, -0.45, 0.82), (0.0, 0.0, 1.0)

    # ---- the mesh panels, from the first condition (all three share the mesh) ----
    from paraview.simple import (Show, Render, UpdatePipeline, Slice, ColorBy,
                                 GetColorTransferFunction)
    r, root, T_USE = open_case("CRM_MP_MP04", "mesh", ["p"])
    try:
        s, info = wing_surface(r, T_USE)
        v = _view()
        d = Show(s, v); _flat(d)
        d.ColorArrayName = [None, ""]
        d.DiffuseColor = [0.66, 0.69, 0.74]; d.AmbientColor = [0.66, 0.69, 0.74]
        d.Representation = "Surface With Edges"
        d.EdgeColor = [0.12, 0.12, 0.12]; d.LineWidth = 0.3
        C.frame_by_extent(v, focal, view_dir, up=view_up, bounds=info.GetBounds(),
                          pad=1.05)
        total += ink_only(v, os.path.join(HERE, "crm_mesh_wing.png"))

        r.MeshRegions = ["internalMesh"]
        UpdatePipeline(time=float(T_USE), proxy=r)
        cut = Slice(Input=r); cut.SliceType = "Plane"
        cut.SliceType.Origin = [0.0, max(bnds[2], 0.0) + 1e-4, 0.0]
        cut.SliceType.Normal = [0.0, 1.0, 0.0]
        UpdatePipeline(time=float(T_USE), proxy=cut)
        ncut = cut.GetDataInformation().GetNumberOfCells()
        if ncut == 0:
            C.refuse("the symmetry-plane cut is empty")
        C.announce("  symmetry cut: %s cells in the plane" % format(ncut, ","))
        v2 = _view()
        d2 = Show(cut, v2); _flat(d2)
        d2.ColorArrayName = [None, ""]
        d2.DiffuseColor = [0.90, 0.91, 0.93]; d2.AmbientColor = [0.90, 0.91, 0.93]
        d2.Representation = "Surface With Edges"
        d2.EdgeColor = [0.10, 0.10, 0.10]; d2.LineWidth = 0.3
        cb = cut.GetDataInformation().GetBounds()
        C.frame_by_extent(v2, [(cb[0] + cb[1]) / 2, cb[2], (cb[4] + cb[5]) / 2],
                          (0.0, -1.0, 0.0), up=(0.0, 0.0, 1.0),
                          bounds=(bnds[0] - 2.0, bnds[1] + 4.0, cb[2], cb[2],
                                  bnds[4] - 3.0, bnds[5] + 3.0), pad=1.04)
        total += ink_only(v2, os.path.join(HERE, "crm_mesh_symmetry.png"))
    finally:
        shutil.rmtree(root, ignore_errors=True)

    # ---- the three pressure panels, same camera, one shared range ----
    for key, tag, cl, al in CONDS:
        r, root, T_USE = open_case("CRM_MP_%s" % key, tag, ["p", "U"])
        try:
            s, info = wing_surface(r, T_USE)
            v = _view()
            d = Show(s, v); _flat(d)
            ColorBy(d, ("CELLS", "p"))
            lut = GetColorTransferFunction("p")
            lut.ApplyPreset("Cool to Warm", True)
            lut.RescaleTransferFunction(lo, hi)
            C.frame_by_extent(v, focal, view_dir, up=view_up, bounds=info.GetBounds(),
                              pad=1.05)
            total += paint(v, s, d, os.path.join(HERE, "crm_p_%s.png" % tag),
                           "p", "p  [Pa]", lut)
        finally:
            shutil.rmtree(root, ignore_errors=True)

    for d, fp in before.items():
        C.assert_run_tree_untouched(d, fp)
    C.announce("  all three constant/polyMesh trees PROVED unchanged")
    C.announce("  %s bytes written" % format(total, ","))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except C.RenderRefusal as exc:
        C.announce_error("REFUSED: %s" % exc)
        sys.exit(2)
