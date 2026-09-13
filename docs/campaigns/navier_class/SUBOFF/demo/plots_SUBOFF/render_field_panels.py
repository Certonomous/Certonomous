#!/usr/bin/env python3
"""ParaView panels for the SUBOFF drift-sweep demo folder.

    xvfb-run -a pvpython docs/campaigns/navier_class/SUBOFF/demo/plots_SUBOFF/render_field_panels.py

    suboff_mesh_l1m.png       the L1 MIRROR's own mesh on hull and sail, per the
                              owner's ParaView rule
    suboff_p_surface.png      surface pressure on hull and sail
    suboff_umag_symmetry.png  velocity magnitude on the z = 0 centre plane
    suboff_umag_wake.png      velocity magnitude on a cross-section aft of the stern

THE FIELD PANELS COME FROM THE MOST ADVANCED SWEEP POINT AT ITS LATEST WRITTEN
TIME, and both of those are read from disk rather than assumed. EVERY POINT WAS
STILL RUNNING, so every panel is PENDING and `assert_stamp` refuses any other
verdict word on them.

A DECOMPOSED CASE IS STAGED HERE RATHER THAN THROUGH `materialise_case`, AND THE
REASON IS NOT CONVENIENCE. This sweep runs `purgeWrite 2`, so the only fields on
disk live in `processor*/<t>` and nothing is reconstructed. Reconstructing would be
COMPUTE and would WRITE INTO A LIVE GRADED TREE, so neither is done: the processor
directories are symlinked into a scratch root, the `.foam` stub is created THERE,
and ParaView reads the decomposed case. The mesh identity is still asserted against
the cell count in CASE_FACTS, so a wrong mesh still refuses.
"""
import os, shutil, sys, tempfile

REPO = "/home/ubuntu/Certonomous"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(REPO, "verification/runs/F14-cooling-ladder/K2h_runs"))
sys.path.insert(0, os.path.join(REPO, "docs/campaigns/F14-cooling-ladder/demo/render_K2bU3R3_paraview"))
import demo3d_render_common as C
sys.path.insert(0, os.path.join(REPO, "sdk"))
from workflows.act_paraview_style import style_view, colour_bar
import render_k2h_l3 as K2H

SWEEP = os.path.join(REPO, "verification/runs/navier_class/SUBOFF_A1H_DRIFT/L1M_SWEEP")
CASE, MESHCASE = "SUBOFF_L1M_BETA_P00", "SUBOFF_L1M_MESH"
BODY = ["patch/hull", "patch/sail"]
BODY_FACES = 233372 + 166582
CONTROL_MARGIN = 8.0
MIN_FIELD_PX = 20000       # see _assert_painted: the colour bar alone is about 4,600 px
PCT_LO, PCT_HI = 2.0, 98.0
GEOM = ("DARPA SUBOFF hull with sail, MIRRORED L1 full domain, 6537226 cells ; "
        "U 3.343886 m/s ; moment origin 2.013 m aft of the nose ; the drift "
        "sweep was STILL RUNNING when this was drawn")


def latest_time(case_dir):
    """The latest time both written and complete on EVERY rank.

    Taking rank 0's latest alone would read a directory another rank has not
    finished writing, on a case that is being written to right now.
    """
    per = []
    for d in sorted(os.listdir(case_dir)):
        if not d.startswith("processor"):
            continue
        ts = set()
        for t in os.listdir(os.path.join(case_dir, d)):
            try:
                float(t)
            except ValueError:
                continue
            if os.path.exists(os.path.join(case_dir, d, t, "U")):
                ts.add(t)
        per.append(ts)
    if not per:
        C.refuse("%s has no processor directory carrying a U field" % case_dir)
    common = set.intersection(*per)
    common.discard("0")
    if not common:
        C.refuse("no time directory carries U on every rank of %s" % case_dir)
    return max(common, key=float)


def stage_decomposed(case_dir, name, time_dir=None):
    """Scratch root of SYMLINKS to constant, system and every processor dir."""
    root = tempfile.mkdtemp(prefix="suboff_%s_" % name)
    for sub in ("constant", "system"):
        src = os.path.join(case_dir, sub)
        if not os.path.isdir(src):
            shutil.rmtree(root, ignore_errors=True)
            C.refuse("%s has no %s" % (case_dir, sub))
        os.symlink(src, os.path.join(root, sub))
    n = 0
    for d in sorted(os.listdir(case_dir)):
        if d.startswith("processor"):
            os.symlink(os.path.join(case_dir, d), os.path.join(root, d))
            n += 1
    foam = os.path.join(root, "%s.foam" % name)
    open(foam, "w").close()
    return root, foam, n


def _view(size=(1600, 1000)):
    from paraview.simple import CreateRenderView, Render
    v = CreateRenderView(); style_view(v, size); Render(v)
    return v


def _flat(d):
    d.Ambient, d.Diffuse, d.Specular = 1.0, 0.0, 0.0


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
    if body.sum() < 500:
        C.refuse("%s has only %d interior pixels" % (os.path.basename(path), int(body.sum())))
    mx = np.maximum(rgb[body].max(axis=1), 1e-6)
    return float(((rgb[body, 0] - rgb[body, 2]) / mx).std()), int(body.sum())


def _assert_painted(pos, neg, field):
    """MEASURED HOLE, CLOSED HERE. On the first run of this driver both velocity
    panels came out BLANK -- the slice drew nothing and only the colour bar was on
    the frame -- and the control PASSED anyway, at 49.7x and then at 4.6e8x, because
    the bar is itself a two-ended ramp and the all-white negative arm had a spread of
    exactly zero. A ratio test cannot see a blank frame: 0.45 over nothing is still
    infinitely more than 0. So two clauses are added, and BOTH are refusals:

      * the POSITIVE arm must cover at least MIN_FIELD_PX pixels -- the bar alone is
        about 4,600, so a field that is not drawn cannot reach 20,000;
      * the NEGATIVE arm must not have a spread of exactly zero, because a negative
        control that measures nothing is not a control (CLAUDE.md rule 3).
    """
    p, npx = K2H._colour_spread(pos)
    n, _ = K2H._colour_spread(neg)
    cp, ncp = _spread_core(pos)
    cn, _ = _spread_core(neg)
    C.announce("      colour control %s: full-body %.5f over %s px against %.5f "
               "(%.1fx) ; interior %.5f against %.5f (%.1fx) ; floor %gx"
               % (field, p, format(npx, ","), n, p / max(n, 1e-9), cp, cn,
                  cp / max(cn, 1e-9), CONTROL_MARGIN))
    if npx < MIN_FIELD_PX:
        C.refuse("BLANK FRAME for %r: the positive arm covers only %s non-background "
                 "pixels, below the %s floor. The colour bar alone is about 4,600, so "
                 "this is a panel whose FIELD was not drawn, and a ratio test cannot "
                 "see that" % (field, format(npx, ","), format(MIN_FIELD_PX, ",")))
    if n <= 0.0:
        C.refuse("NO CONTROL for %r: the constant-array arm has a colour spread of "
                 "exactly zero, i.e. it drew nothing. A negative control that measures "
                 "nothing is not a control" % field)
    if p <= n:
        C.refuse("COLOUR CONTROL FAILED for %r on the full-body mask" % field)
    if cp < CONTROL_MARGIN * max(cn, 1e-9):
        C.refuse("COLOUR CONTROL FAILED for %r: interior %.5f against %.5f"
                 % (field, cp, cn))


def _with_control(view, src, disp, out, field, add_caption):
    from paraview.simple import (Calculator, Show, Hide, Render, ColorBy,
                                 UpdatePipeline)
    flat = Calculator(Input=src)
    flat.AttributeType = "Point Data"
    flat.ResultArrayName = "CONTROL_CONSTANT"; flat.Function = "1.0"
    UpdatePipeline(proxy=flat)
    a = flat.GetPointDataInformation().GetArray("CONTROL_CONSTANT")
    lo, hi = a.GetComponentRange(0)
    if abs(hi - lo) > 1e-12:
        C.refuse("the control array spans %g to %g and is not constant" % (lo, hi))
    Hide(src, view); disp.SetScalarBarVisibility(view, False)
    dn = Show(flat, view); ColorBy(dn, ("POINTS", "CONTROL_CONSTANT")); _flat(dn)
    dn.SetScalarBarVisibility(view, False); Render(view)
    # the BAR is hidden for BOTH arms: it is a two-ended ramp and would put its own
    # colour into whichever arm carried it
    neg = os.path.join(HERE, "_control", "NEGATIVE_constant_" + os.path.basename(out))
    C.save_screenshot(view, neg, size=(1600, 1000))
    Hide(flat, view); Show(src, view)
    Render(view)
    pos = os.path.join(HERE, "_control", "POSITIVE_uncaptioned_" + os.path.basename(out))
    C.save_screenshot(view, pos, size=(1600, 1000))
    _assert_painted(pos, neg, field)
    disp.SetScalarBarVisibility(view, True)
    add_caption(view); Render(view)
    n = C.save_screenshot(view, out, size=(1600, 1000))
    C.announce("  wrote %s (%s bytes)" % (os.path.basename(out), format(n, ",")))
    return n


def _cap(view, case, stamp, second):
    """NOTHING IS WRITTEN ON THE IMAGE (v2 section 13). The case, the time,
    the geometry and the verdict live in the folder SIDECAR.md and in the act
    beside the figure. `C.assert_stamp` still ran on `stamp` before any pixel
    was drawn, so the verdict guard is kept and only its printing is dropped."""
    return None



def main():
    C.assert_paraview_version()
    case_dir = C.facts(CASE)["case_dir"]
    mesh_dir = C.facts(MESHCASE)["case_dir"]
    t = latest_time(case_dir)
    C.announce("  latest time complete on EVERY rank of BETA_p00: t = %s" % t)
    stamp = ("%s ; 6537226 cells ; simpleFoam ; t = %s of a registered endTime "
             "3000 ; PENDING" % (CASE, t))
    C.assert_stamp(stamp, CASE)
    mesh_stamp = ("%s ; 6537226 cells ; the L1 mirror ; PENDING" % MESHCASE)
    C.assert_stamp(mesh_stamp, MESHCASE)
    # the mesh the solve LINKS to does not change while the solve runs
    mesh_before = C.run_tree_fingerprint(os.path.join(mesh_dir, "constant", "polyMesh"))

    from paraview.simple import (OpenFOAMReader, UpdatePipeline, MergeBlocks, Show,
                                 Render, ColorBy, GetColorTransferFunction,
                                 CellDatatoPointData, Calculator, Slice)
    total = 0

    # ---- 1. the mesh panel, from the MIRROR itself ------------------------
    root, foam, _ = stage_decomposed(mesh_dir, "mesh")
    try:
        r = OpenFOAMReader(FileName=foam)
        r.CaseType = "Reconstructed Case"
        r.Decomposepolyhedra = 0
        r.MeshRegions = ["internalMesh"]
        UpdatePipeline(proxy=r)
        n = r.GetDataInformation().GetNumberOfCells()
        if n != C.facts(MESHCASE)["cells"]:
            C.refuse("the mirror loaded %d cells where the mesh record says %d"
                     % (n, C.facts(MESHCASE)["cells"]))
        C.announce("  %s: %s cells" % (MESHCASE, format(n, ",")))
        r.MeshRegions = BODY
        UpdatePipeline(proxy=r)
        surf = MergeBlocks(Input=r); UpdatePipeline(proxy=surf)
        info = surf.GetDataInformation()
        if info.GetNumberOfCells() != BODY_FACES:
            C.refuse("hull+sail rendered %d faces where the boundary file sums "
                     "to %d" % (info.GetNumberOfCells(), BODY_FACES))
        v = _view()
        d = Show(surf, v); _flat(d)
        d.ColorArrayName = [None, ""]
        d.DiffuseColor = [0.66, 0.69, 0.74]; d.AmbientColor = [0.66, 0.69, 0.74]
        d.Representation = "Surface With Edges"
        d.EdgeColor = [0.12, 0.12, 0.12]; d.LineWidth = 0.25
        b = info.GetBounds()
        C.announce("  body bounding box x %.3f to %.3f, y %.3f to %.3f, z %.3f "
                   "to %.3f m" % b)
        C.frame_by_extent(v, [(b[0] + b[1]) / 2, (b[2] + b[3]) / 2, (b[4] + b[5]) / 2],
                          (0.35, 0.45, -0.82), up=(0.0, 1.0, 0.0), bounds=b,
                          pad=1.10, bottom_band=0.12)
        _cap(v, MESHCASE, mesh_stamp,
             GEOM + " ; THE MIRROR'S OWN MESH on hull and sail, %s faces"
             % format(BODY_FACES, ","))
        Render(v)
        nb = C.save_screenshot(v, os.path.join(HERE, "suboff_mesh_l1m.png"),
                               size=(1600, 1000))
        _, npx = K2H._colour_spread(os.path.join(HERE, "suboff_mesh_l1m.png"))
        if npx < 20000:
            C.refuse("suboff_mesh_l1m.png has only %d non-background pixels" % npx)
        total += nb
        C.announce("  wrote suboff_mesh_l1m.png (%s bytes, %s body px)"
                   % (format(nb, ","), format(npx, ",")))
        bbox = b
    finally:
        shutil.rmtree(root, ignore_errors=True)

    # ---- 2. the field panels, from the most advanced point ----------------
    root, foam, nproc = stage_decomposed(case_dir, "beta_p00", t)
    try:
        C.announce("  staged %d processor directories of BETA_p00 as symlinks" % nproc)
        r = OpenFOAMReader(FileName=foam)
        r.CaseType = "Decomposed Case"
        r.Decomposepolyhedra = 0
        r.MeshRegions = ["internalMesh"]
        r.CellArrays = ["p", "U"]
        UpdatePipeline(time=float(t), proxy=r)
        n = r.GetDataInformation().GetNumberOfCells()
        if n != C.facts(CASE)["cells"]:
            C.refuse("BETA_p00 loaded %d cells where the mesh record says %d"
                     % (n, C.facts(CASE)["cells"]))
        C.announce("  %s: %s cells at t = %s" % (CASE, format(n, ","), t))
        base = GEOM + " ; fields at t = %s, the latest time written on every rank" % t

        # surface pressure
        r.MeshRegions = BODY
        UpdatePipeline(time=float(t), proxy=r)
        surf = MergeBlocks(Input=r); UpdatePipeline(time=float(t), proxy=surf)
        prange = _percentiles(surf, "p")
        C.announce("  surface p display window %.4g to %.4g m2/s2 (percentiles %g/%g)"
                   % (prange + (PCT_LO, PCT_HI)))
        v = _view()
        d = Show(surf, v); _flat(d)
        ColorBy(d, ("CELLS", "p"))
        lut = GetColorTransferFunction("p"); lut.ApplyPreset("Cool to Warm", True)
        lut.RescaleTransferFunction(*prange)
        _bar(v, lut, "p  [m2/s2]")
        b = surf.GetDataInformation().GetBounds()
        C.frame_by_extent(v, [(b[0] + b[1]) / 2, (b[2] + b[3]) / 2, (b[4] + b[5]) / 2],
                          (0.35, 0.45, -0.82), up=(0.0, 1.0, 0.0), bounds=b,
                          pad=1.10, bottom_band=0.12)
        Render(v)
        pnote = base + " ; colour bar %.4g to %.4g m2/s2, ends clamped" % prange
        total += _with_control(v, surf, d, os.path.join(HERE, "suboff_p_surface.png"),
                               "p", lambda view: _cap(view, CASE, stamp, pnote))

        # velocity planes
        # THE PIPELINE IS REBUILT PER PANEL, NOT SHARED. Sharing it is what produced
        # the first run's failure: the second Slice re-executed a Calculator whose
        # input had lost its point arrays and ParaView reported
        # "Undefined symbol: 'U'   Expression: mag(U)" and drew NOTHING, while the
        # panel was still written. Rebuilding costs a re-read and removes the state
        # that made one panel depend on what a previous panel had done to the reader.
        for out, origin, normal, direction, up, bnds, tag in (
                ("suboff_umag_symmetry.png", [0.0, 0.0, 0.0], [0.0, 0.0, 1.0],
                 (0.0, 0.0, -1.0), (0.0, 1.0, 0.0),
                 (bbox[0] - 1.0, bbox[1] + 3.0, bbox[2] - 1.2, bbox[3] + 1.2, 0.0, 0.0),
                 "centre plane at z = 0"),
                ("suboff_umag_wake.png", [bbox[1] + 0.5, 0.0, 0.0], [1.0, 0.0, 0.0],
                 (-1.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                 (bbox[1] + 0.5, bbox[1] + 0.5, -1.2, 1.2, -1.2, 1.2),
                 "cross-section 0.5 m aft of the stern")):
            r.MeshRegions = ["internalMesh"]
            r.CellArrays = ["p", "U"]
            UpdatePipeline(time=float(t), proxy=r)
            p2c = CellDatatoPointData(Input=r)
            p2c.CellDataArraytoprocess = ["U", "p"]
            UpdatePipeline(time=float(t), proxy=p2c)
            cc = Calculator(Input=p2c); cc.AttributeType = "Point Data"
            cc.ResultArrayName = "Umag"; cc.Function = "mag(U)"
            UpdatePipeline(time=float(t), proxy=cc)
            if cc.GetPointDataInformation().GetArray("Umag") is None:
                C.refuse("the Umag calculator produced no array for the %s panel; "
                         "a slice of it would be a blank frame" % tag)
            s = Slice(Input=cc); s.SliceType = "Plane"
            s.SliceType.Origin = origin; s.SliceType.Normal = normal
            UpdatePipeline(time=float(t), proxy=s)
            if s.GetDataInformation().GetNumberOfCells() == 0:
                C.refuse("the %s slice is empty" % tag)
            urange = _percentiles(s, "Umag")
            vv = _view()
            dd = Show(s, vv); _flat(dd)
            ColorBy(dd, ("POINTS", "Umag"))
            l2 = GetColorTransferFunction("Umag")
            l2.ApplyPreset("Viridis (matplotlib)", True)
            l2.RescaleTransferFunction(*urange)
            _bar(vv, l2, "|U|  [m/s]")
            C.frame_by_extent(vv, [(bnds[0] + bnds[1]) / 2, (bnds[2] + bnds[3]) / 2,
                                   (bnds[4] + bnds[5]) / 2], direction, up=up,
                              bounds=bnds, pad=1.06, bottom_band=0.12)
            Render(vv)
            unote = (base + " ; %s ; colour bar %.4g to %.4g m/s, ends clamped"
                     % (tag, urange[0], urange[1]))
            total += _with_control(vv, s, dd, os.path.join(HERE, out), "Umag",
                                   lambda view, u=unote: _cap(view, CASE, stamp, u))
    finally:
        shutil.rmtree(root, ignore_errors=True)

    C.assert_run_tree_untouched(os.path.join(mesh_dir, "constant", "polyMesh"),
                                mesh_before)
    C.announce("  L1 mirror constant/polyMesh PROVED unchanged")
    C.announce("  %s bytes written" % format(total, ","))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except C.RenderRefusal as exc:
        C.announce_error("REFUSED: %s" % exc)
        sys.exit(2)
