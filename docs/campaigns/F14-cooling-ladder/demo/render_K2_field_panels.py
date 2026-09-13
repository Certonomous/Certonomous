#!/usr/bin/env python3
"""ParaView field panels for BOTH K2 demo plot folders, in one run.

    xvfb-run -a pvpython docs/campaigns/F14-cooling-ladder/demo/render_K2_field_panels.py

SIX PANELS, on the owner's 2026-09-13 instruction:

  plots_K2_steady/   (fields from K2f_L3, the FINE steady level, at t = 803)
    k2_plane_mid.png            temperature, horizontal plane at rack mid-height
    k2_plane_mid_velocity.png   velocity magnitude, the same plane
    k2_hot_cloud.png            oblique 3-D, the 27 degC iso-surface over the hot aisle

  plots_K2_transient/  (fields from K2h_L3, the TRANSIENT fine level, at t = 110)
    k2t_plane_mid.png           TMean, the same plane, captioned with the averaging window
    k2t_plane_mid_velocity.png  UMean magnitude, the same plane
    k2t_plane_t110.png          INSTANTANEOUS T at the last written time, captioned with it

ONE RUN FOR BOTH FOLDERS, AND THAT IS THE POINT OF THE FILE: the owner asked for
consistent colour maps and ranges per family, and a range shared across two
folders cannot be shared by two scripts that never meet. The temperature window
is measured once over BOTH cases' planes and used on all four temperature panels;
the velocity window likewise.

THE CAPTION IS BUILT FROM THE FIELD'S OWN TIME, never from a constant. That is a
deliberate departure from `render_k2h_l3.fig_mean_field`, which writes "mean over
simulated 42 to <t> s" whatever field it is handed -- true of TMean, false of an
instantaneous T, and the reason this file exists rather than another re-point.
The averaging window is read from `GRADE.K2h_L3.json`'s own accumulator block.

Guards: the graded trees are staged as symlinks and their fingerprints asserted
unchanged; every coloured panel carries the planted colour control at the DrivAer
8x margin; the iso-surface panel carries an ink guard instead, because a colour
control on a SINGLE-VALUED surface would be meaningless by construction.
"""
import json, os, shutil, sys

REPO = "/home/ubuntu/Certonomous"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(HERE, "render_K2bU3R3_paraview"))
sys.path.insert(0, os.path.join(REPO, "verification/runs/F14-cooling-ladder/K2h_runs"))
import demo3d_render_common as C
import render_k2bU3R3 as K2B          # geometry constants and view helpers
import render_k2h_l3 as K2H           # its COMMITTED colour-control measurement

STEADY_DIR = os.path.join(HERE, "plots_K2_steady")
TRANS_DIR = os.path.join(HERE, "plots_K2_transient")
GRADE = json.JSONDecoder().raw_decode(
    open(os.path.join(REPO, "verification/runs/F14-cooling-ladder/K2h_runs",
                      "GRADE.K2h_L3.json")).read(), 0)[0]

CONTROL_MARGIN = 8.0
PCT_LO, PCT_HI = 2.0, 98.0
Z_MID = K2B.RACK_Z1 / 2.0             # 1.0 m, rack mid-height, from build_k2b H_R
T_ISO = 300.15                        # 27 degC, the ASHRAE A1 recommended limit
PRESET_T = "Inferno (matplotlib)"
PRESET_U = "Viridis (matplotlib)"

STEADY = dict(case="K2f_L3", time="803", verdict="NOT A RESULT",
              scalar="T", vector="U",
              stamp="K2f_L3 ; 664848 cells ; buoyantBoussinesqSimpleFoam ; "
                    "t = 803 of endTime 2000 ; NOT A RESULT")
WINDOW = GRADE["D_COMPLETE"]["detail"]["MEASURED_COVERED_WINDOW"]
TRANS = dict(case="K2h_L3", time="110", verdict="PASS",
             scalar="TMean", vector="UMean",
             stamp="K2h_L3 ; 664848 cells ; buoyantBoussinesqPimpleFoam ; "
                   "t = 110 ; PASS")
GEOM = ("Room 3.6 x 3.5 x 2.7 m ; 4 racks ; rack row spans x = 0.6 to 3.0 m ; "
        "cold aisle y below 1.2 m, hot aisle y above 2.3 m")


# ---------------------------------------------------------------------------
def _view(size=(1600, 1000)):
    from paraview.simple import CreateRenderView, Render
    v = CreateRenderView()
    v.ViewSize = list(size)
    v.OrientationAxesVisibility = 0
    C.white_background(v)
    Render(v)
    return v


def _bar(view, lut, label):
    from paraview.simple import GetScalarBar
    b = GetScalarBar(lut, view)
    b.Visibility = 1
    b.Title = label
    b.ComponentTitle = ""
    b.TitleColor = [0.15, 0.15, 0.15]
    b.LabelColor = [0.15, 0.15, 0.15]
    b.TitleFontSize = 11
    b.LabelFontSize = 10


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
        arr = b.GetPointData().GetArray(name)
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


def _assert_painted(pos, neg, field):
    p, npx = K2H._colour_spread(pos)
    n, _ = K2H._colour_spread(neg)
    C.announce("      colour control %s: %.5f over %s px against a CONSTANT "
               "array's %.5f, ratio %.1fx (floor %gx)"
               % (field, p, format(npx, ","), n, p / max(n, 1e-9), CONTROL_MARGIN))
    if p < CONTROL_MARGIN * max(n, 1e-9):
        C.refuse("COLOUR CONTROL FAILED for %r: %.5f against a constant array's "
                 "%.5f" % (field, p, n))


def _mid_plane_panel(reader, case, end, out, stamp, note, name, expr, preset,
                     rng, label):
    """A horizontal x-y plane at rack mid-height, coloured by a derived scalar."""
    from paraview.simple import (CellDatatoPointData, Calculator, Slice, Show,
                                 Hide, Render, ColorBy, GetColorTransferFunction,
                                 UpdatePipeline)
    v = _view()
    p2c = CellDatatoPointData(Input=reader)
    p2c.CellDataArraytoprocess = list(reader.CellArrays)
    UpdatePipeline(time=float(end), proxy=p2c)
    calc = Calculator(Input=p2c)
    calc.AttributeType = "Point Data"
    calc.ResultArrayName = name
    calc.Function = expr
    UpdatePipeline(time=float(end), proxy=calc)
    s = Slice(Input=calc)
    s.SliceType = "Plane"
    s.SliceType.Origin = [0.0, 0.0, Z_MID]
    s.SliceType.Normal = [0.0, 0.0, 1.0]
    UpdatePipeline(time=float(end), proxy=s)
    if s.GetDataInformation().GetNumberOfCells() == 0:
        C.refuse("the rack mid-height plane is empty; nothing would be drawn")

    # negative arm first, exactly as the committed renderer orders it
    flat = Calculator(Input=s)
    flat.AttributeType = "Point Data"
    flat.ResultArrayName = "CONTROL_CONSTANT"
    flat.Function = "1.0"
    UpdatePipeline(time=float(end), proxy=flat)
    a = flat.GetPointDataInformation().GetArray("CONTROL_CONSTANT")
    lo, hi = a.GetComponentRange(0)
    if abs(hi - lo) > 1e-12:
        C.refuse("the control array spans %g to %g and is not constant" % (lo, hi))
    dn = Show(flat, v)
    ColorBy(dn, ("POINTS", "CONTROL_CONSTANT"))
    dn.SetScalarBarVisibility(v, False)
    C.frame_by_extent(v, (K2B.ROOM[0] / 2, K2B.ROOM[1] / 2, Z_MID),
                      (0.0, 0.0, 1.0), up=(0.0, 1.0, 0.0),
                      bounds=(0.0, K2B.ROOM[0], 0.0, K2B.ROOM[1], Z_MID, Z_MID),
                      pad=1.08, bottom_band=0.12)
    Render(v)
    neg = os.path.join(os.path.dirname(out), "_control",
                       "NEGATIVE_constant_" + os.path.basename(out))
    C.save_screenshot(v, neg, size=(1600, 1000))
    Hide(flat, v)

    d = Show(s, v)
    ColorBy(d, ("POINTS", name))
    lut = GetColorTransferFunction(name)
    lut.ApplyPreset(preset, True)
    lut.RescaleTransferFunction(*rng)
    d.SetScalarBarVisibility(v, True)
    _bar(v, lut, label)
    Render(v)
    pos = os.path.join(os.path.dirname(out), "_control",
                       "POSITIVE_uncaptioned_" + os.path.basename(out))
    C.save_screenshot(v, pos, size=(1600, 1000))
    _assert_painted(pos, neg, name)

    C.caption(v, stamp, case, position=(0.02, 0.055), size=10)
    C.caption(v, note, case, position=(0.02, 0.018), size=8, check_stamp=False)
    Render(v)
    n = C.save_screenshot(v, out, size=(1600, 1000))
    C.announce("  wrote %s (%s bytes)" % (os.path.basename(out), format(n, ",")))
    return n


def _iso_panel(reader, case, end, out, stamp, note, scalar):
    """Oblique 3-D view of the 27 degC iso-surface, with the rack row drawn.

    NO COLOUR CONTROL HERE, AND THE REASON IS STRUCTURAL RATHER THAN CONVENIENT:
    an iso-surface is SINGLE-VALUED in the field that defines it, so colouring it
    by that field paints it one colour BY CONSTRUCTION and a control comparing it
    with a constant array could never pass. The guard is an ink guard instead --
    the surface must occupy a measured number of non-background pixels, so an
    EMPTY iso-surface (the failure that matters here: no volume above the limit)
    refuses rather than shipping an empty room.
    """
    from paraview.simple import (CellDatatoPointData, Contour, Show, Render,
                                 ColorBy, UpdatePipeline)
    v = _view()
    p2c = CellDatatoPointData(Input=reader)
    p2c.CellDataArraytoprocess = list(reader.CellArrays)
    UpdatePipeline(time=float(end), proxy=p2c)
    iso = Contour(Input=p2c)
    iso.ContourBy = ["POINTS", scalar]
    iso.Isosurfaces = [T_ISO]
    UpdatePipeline(time=float(end), proxy=iso)
    ncell = iso.GetDataInformation().GetNumberOfCells()
    if ncell == 0:
        C.refuse("the %g K iso-surface is empty at t = %s: no volume above the "
                 "limit, and an empty room will not be shipped as one"
                 % (T_ISO, end))
    C.announce("      iso-surface at %.2f K: %s triangles" % (T_ISO, format(ncell, ",")))
    d = Show(iso, v)
    ColorBy(d, None)
    d.DiffuseColor = [0.82, 0.29, 0.09]
    d.Opacity = 0.85
    K2B.rack_block(v)
    K2B.outline(reader, v)
    C.frame_by_extent(v, (K2B.ROOM[0] / 2, K2B.ROOM[1] / 2, K2B.ROOM[2] / 2),
                      (-0.55, -0.80, 0.42), up=(0.0, 0.0, 1.0),
                      bounds=(0.0, K2B.ROOM[0], 0.0, K2B.ROOM[1], 0.0, K2B.ROOM[2]),
                      pad=1.06, bottom_band=0.12)
    C.caption(v, stamp, case, position=(0.02, 0.055), size=10)
    C.caption(v, note, case, position=(0.02, 0.018), size=8, check_stamp=False)
    Render(v)
    n = C.save_screenshot(v, out, size=(1600, 1000))
    _, npx = K2H._colour_spread(out)
    if npx < 20000:
        C.refuse("%s has only %d non-background pixels" % (os.path.basename(out), npx))
    C.announce("  wrote %s (%s bytes, %s body px)"
               % (os.path.basename(out), format(n, ","), format(npx, ",")))
    return n


# ---------------------------------------------------------------------------
def _open(spec):
    fields = [spec["scalar"], spec["vector"]]
    return C.open_case(spec["case"], fields, [spec["time"]])


def main():
    C.assert_paraview_version()
    for spec in (STEADY, TRANS):
        C.assert_stamp(spec["stamp"], spec["case"])
    dirs = {C.facts(s["case"])["case_dir"]: None for s in (STEADY, TRANS)}
    before = {d: C.run_tree_fingerprint(d) for d in dirs}

    # ---- ONE temperature window and ONE velocity window for BOTH cases ----
    from paraview.simple import (CellDatatoPointData, Calculator, Slice,
                                 UpdatePipeline)
    t_lo = t_hi = u_lo = u_hi = None
    roots = []
    try:
        for spec in (STEADY, TRANS):
            reader, root, n = _open(spec)
            roots.append(root)
            p2c = CellDatatoPointData(Input=reader)
            p2c.CellDataArraytoprocess = list(reader.CellArrays)
            UpdatePipeline(time=float(spec["time"]), proxy=p2c)
            calc = Calculator(Input=p2c)
            calc.AttributeType = "Point Data"
            calc.ResultArrayName = "Umag"
            calc.Function = "mag(%s)" % spec["vector"]
            UpdatePipeline(time=float(spec["time"]), proxy=calc)
            s = Slice(Input=calc)
            s.SliceType = "Plane"
            s.SliceType.Origin = [0.0, 0.0, Z_MID]
            s.SliceType.Normal = [0.0, 0.0, 1.0]
            UpdatePipeline(time=float(spec["time"]), proxy=s)
            a, b = _percentiles(s, spec["scalar"])
            c, e = _percentiles(s, "Umag")
            t_lo = a if t_lo is None else min(t_lo, a)
            t_hi = b if t_hi is None else max(t_hi, b)
            u_lo = c if u_lo is None else min(u_lo, c)
            u_hi = e if u_hi is None else max(u_hi, e)
    finally:
        for r in roots:
            shutil.rmtree(r, ignore_errors=True)
    T_RNG, U_RNG = (t_lo, t_hi), (u_lo, u_hi)
    C.announce("  SHARED windows, measured over BOTH cases' mid-height planes at "
               "percentiles %g/%g: T %.3f to %.3f K ; U %.4f to %.4f m/s"
               % (PCT_LO, PCT_HI, t_lo, t_hi, u_lo, u_hi))

    total = 0
    # ---- the steady folder ------------------------------------------------
    root = None
    try:
        reader, root, n = _open(STEADY)
        C.announce("  %s: %s cells at t = %s" % (STEADY["case"], format(n, ","),
                                                 STEADY["time"]))
        base = (GEOM + " ; x-y plane at z = %.1f m (rack mid-height) ; "
                       "fields at t = 803, the last written time of a "
                       "registered endTime 2000" % Z_MID)
        total += _mid_plane_panel(
            reader, STEADY["case"], STEADY["time"],
            os.path.join(STEADY_DIR, "k2_plane_mid.png"), STEADY["stamp"],
            base + " ; colour bar %.2f to %.2f K, ends clamped" % T_RNG,
            "Tplot", STEADY["scalar"] + "*1.0", PRESET_T, T_RNG, "T  (K)")
        total += _mid_plane_panel(
            reader, STEADY["case"], STEADY["time"],
            os.path.join(STEADY_DIR, "k2_plane_mid_velocity.png"), STEADY["stamp"],
            base + " ; colour bar %.3f to %.3f m/s, ends clamped" % U_RNG,
            "Umag", "mag(%s)" % STEADY["vector"], PRESET_U, U_RNG,
            "U magnitude  (m/s)")
        total += _iso_panel(
            reader, STEADY["case"], STEADY["time"],
            os.path.join(STEADY_DIR, "k2_hot_cloud.png"), STEADY["stamp"],
            GEOM + " ; iso-surface at %.2f K (27 degC, ASHRAE A1 recommended) ; "
                   "oblique view from the hot aisle ; fields at t = 803" % T_ISO,
            STEADY["scalar"])
    finally:
        if root:
            shutil.rmtree(root, ignore_errors=True)

    # ---- the transient folder --------------------------------------------
    root = None
    try:
        reader, root, n = _open(TRANS)
        C.announce("  %s: %s cells at t = %s" % (TRANS["case"], format(n, ","),
                                                 TRANS["time"]))
        win = ("time-averaged over %.3f to %.1f s (fieldAverage totalTime "
               "%.6f s, totalIter %d, read from GRADE.K2h_L3.json)"
               % (WINDOW["covered_start_MEASURED"], WINDOW["covered_end"],
                  WINDOW["totalTime"], WINDOW["totalIter"]))
        base = (GEOM + " ; x-y plane at z = %.1f m (rack mid-height) ; " % Z_MID)
        total += _mid_plane_panel(
            reader, TRANS["case"], TRANS["time"],
            os.path.join(TRANS_DIR, "k2t_plane_mid.png"), TRANS["stamp"],
            base + win + " ; colour bar %.2f to %.2f K, ends clamped" % T_RNG,
            "Tplot", TRANS["scalar"] + "*1.0", PRESET_T, T_RNG, "T mean  (K)")
        total += _mid_plane_panel(
            reader, TRANS["case"], TRANS["time"],
            os.path.join(TRANS_DIR, "k2t_plane_mid_velocity.png"), TRANS["stamp"],
            base + win + " ; colour bar %.3f to %.3f m/s, ends clamped" % U_RNG,
            "Umag", "mag(%s)" % TRANS["vector"], PRESET_U, U_RNG,
            "U mean magnitude  (m/s)")
    finally:
        if root:
            shutil.rmtree(root, ignore_errors=True)

    # the INSTANTANEOUS panel -- a separate open, because it needs T not TMean
    root = None
    try:
        reader, root, n = C.open_case(TRANS["case"], ["T", "U"], [TRANS["time"]])
        total += _mid_plane_panel(
            reader, TRANS["case"], TRANS["time"],
            os.path.join(TRANS_DIR, "k2t_plane_t110.png"), TRANS["stamp"],
            base + ("INSTANTANEOUS T at t = %s s, the last written time -- NOT a "
                    "time average ; colour bar %.2f to %.2f K, ends clamped"
                    % (TRANS["time"], T_RNG[0], T_RNG[1])),
            "Tplot", "T*1.0", PRESET_T, T_RNG, "T at t = 110 s  (K)")
    finally:
        if root:
            shutil.rmtree(root, ignore_errors=True)

    for d, fp in before.items():
        C.assert_run_tree_untouched(d, fp)
        C.announce("  run tree PROVED unchanged: %s" % d)
    C.announce("  %s bytes written" % format(total, ","))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except C.RenderRefusal as exc:
        C.announce_error("REFUSED: %s" % exc)
        sys.exit(2)
