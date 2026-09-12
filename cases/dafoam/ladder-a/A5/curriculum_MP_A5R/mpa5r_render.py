#!/usr/bin/env pvpython
"""MP_A5R completion render.  OFFSCREEN.  ZERO SOLVER COMPUTE.  READ-ONLY on its input.

Sanaa 2026-09-12 ~20:30Z, byte-exact: "whenever a run completes, i want the paraview
visualization of its mesh saved. (when the run is complete). The paraview should show the
coarse mesh (or meidum mesh if the coarse isnt converged). But all fields should be stored
as the fine mesh result fields (whenever we have it)."

WHAT THAT MEANS HERE, SAID HONESTLY RATHER THAN BY INVENTING A HIERARCHY.  MP_A5R is an
OPTIMISATION ON ONE U-BEND MESH ACROSS THREE SCENARIOS.  IT HAS NO GRID FAMILY: there is no
coarse, no medium, no fine, so "the coarse mesh" and "the fine mesh result fields" have no
referents to choose between.  Every output therefore carries `single-level` in its name and
the sidecar says so in words.  NAMING THE ONE MESH `coarse` TO MATCH THE DIRECTIVE'S SHAPE
WOULD BE A LABEL THAT LOOKS COMPLIANT AND IS FALSE.

THE CAMERA IS FITTED TO THE DATA, NOT RESET.  A sibling lane reviewed ten M6 renders and
found five wasting 35-45% of frame on white margin and one leading-edge view that rendered
the wing as a ONE-PIXEL SLIVER.  Both come from the same cause: ResetCamera() plus a fixed
square image, on geometry that is neither square nor axis-friendly.  Here the view axis is
chosen as the SHORTEST extent (so the largest face of the bounding box is what you see),
the image aspect is matched to the two remaining extents, and the parallel scale is the
half-height plus a 3% margin -- so the geometry fills the frame by construction.

A RENDER IS NOT A GATE.  Nothing here can change a verdict; failures are reported and the
exit code is deliberately 0 on render failure so a wrapper cannot mistake it for a result.
"""
import glob, json, os, sys, argparse

ap = argparse.ArgumentParser()
ap.add_argument("--case", required=True, help="OpenFOAM case directory (a COPY, never a graded tree)")
ap.add_argument("--out", required=True, help="output directory for PNGs")
ap.add_argument("--tag", required=True, help="case id + arm + scenario, goes in every filename")
ap.add_argument("--width", type=int, default=1600)
args = ap.parse_args()

from paraview.simple import *  # noqa: E402
paraview.simple._DisableFirstRenderCameraReset()

os.makedirs(args.out, exist_ok=True)
report = {"tag": args.tag, "case": os.path.abspath(args.case), "images": [], "errors": [],
          "level_label": "single-level (no grid family: one mesh, three scenarios)"}

# --- the .foam handle.  Written into the COPY, which is the only thing we may write to.
foam = os.path.join(args.case, "case.foam")
if not os.path.exists(foam):
    open(foam, "w").close()

src = OpenFOAMReader(registrationName="case", FileName=foam)
src.MeshRegions = ["internalMesh"]
src.CaseType = "Reconstructed Case"
src.UpdatePipelineInformation()

times = list(src.TimestepValues) if src.TimestepValues else [0.0]
t_latest = max(times)
report["times_available"] = times
report["time_rendered"] = t_latest
report["time_rendered_is_latest"] = True

cell_arrays = [a.Name for a in src.CellData] if hasattr(src, "CellData") else []
point_arrays = [a.Name for a in src.PointData] if hasattr(src, "PointData") else []
report["arrays_cell"] = cell_arrays
report["arrays_point"] = point_arrays

def _fit_parallel_scale(bounds, cam_pos, focal, view_up, aspect, margin=1.03):
    """Half-height that makes the bounding box FILL the frame at this camera angle.

    THIS EXISTS BECAUSE I REPRODUCED THE EXACT DEFECT I WAS WARNED ABOUT.  The oblique
    shape view was first zoomed with a guessed constant (diag/2 * 0.62) and came out with
    the body occupying about 40% of frame width -- the same 35-45% white margin a sibling
    lane found in five of ten M6 renders.  A GUESSED ZOOM FACTOR IS THE DEFECT, not the
    number chosen: the projected size of a box depends on the viewing angle, so no single
    constant fits both an axis-aligned view and an oblique one.

    So project the eight corners onto the camera's own right/up axes and measure.  No
    constant to tune, and it is correct for any angle by construction.
    """
    import math
    fwd = [focal[i] - cam_pos[i] for i in range(3)]
    n = math.sqrt(sum(c * c for c in fwd)) or 1.0
    fwd = [c / n for c in fwd]
    up = list(view_up)
    d = sum(up[i] * fwd[i] for i in range(3))
    up = [up[i] - d * fwd[i] for i in range(3)]
    n = math.sqrt(sum(c * c for c in up)) or 1.0
    up = [c / n for c in up]
    right = [fwd[1] * up[2] - fwd[2] * up[1],
             fwd[2] * up[0] - fwd[0] * up[2],
             fwd[0] * up[1] - fwd[1] * up[0]]
    hs, ws = [], []
    for xi in (bounds[0], bounds[1]):
        for yi in (bounds[2], bounds[3]):
            for zi in (bounds[4], bounds[5]):
                v = [xi - focal[0], yi - focal[1], zi - focal[2]]
                hs.append(abs(sum(v[i] * up[i] for i in range(3))))
                ws.append(abs(sum(v[i] * right[i] for i in range(3))))
    half_h, half_w = max(hs), max(ws)
    return max(half_h, (half_w / aspect) if aspect else half_h) * margin

view = CreateView("RenderView")
view.UseColorPaletteForBackground = 0
view.Background = [1.0, 1.0, 1.0]
view.OrientationAxesVisibility = 0
view.CameraParallelProjection = 1

UpdatePipeline(time=t_latest, proxy=src)
b = src.GetDataInformation().GetBounds()
ext = [b[1] - b[0], b[3] - b[2], b[5] - b[4]]
ctr = [(b[0] + b[1]) / 2.0, (b[2] + b[3]) / 2.0, (b[4] + b[5]) / 2.0]
report["bounds"] = list(b)
report["extents"] = ext

# view along the SHORTEST extent -> the largest face of the bbox faces the camera.
axis = ext.index(min(ext))
plane = [i for i in (0, 1, 2) if i != axis]
w_ext, h_ext = ext[plane[0]], ext[plane[1]]
if w_ext <= 0 or h_ext <= 0:
    w_ext = h_ext = max(ext) or 1.0
MARGIN = 1.03
aspect = (w_ext / h_ext) if h_ext else 1.0
W = int(args.width)
H = max(240, int(round(W / aspect))) if aspect >= 1 else W
if aspect < 1:
    H = int(args.width); W = max(240, int(round(H * aspect)))
report["view_axis"] = "xyz"[axis]
report["image_size"] = [W, H]
report["aspect_from_geometry"] = aspect

up = [0, 0, 0]; up[plane[1]] = 1
pos = list(ctr); pos[axis] = b[2 * axis + 1] + max(ext) * 3.0
view.ViewSize = [W, H]
view.CameraPosition = pos
view.CameraFocalPoint = ctr
view.CameraViewUp = up
view.CameraParallelScale = _fit_parallel_scale(b, pos, ctr, up, float(W) / float(H), MARGIN)

def shoot(name, note):
    """THE SAVED RESOLUTION IS READ FROM THE VIEW, NEVER FROM THE CAPTURED W/H.

    THIRD INSTANCE TONIGHT OF ONE QUANTITY LIVING IN TWO PLACES WITH ONE UPDATED
    (L-221/L-222).  This function captured W and H from the axis-aligned setup and passed
    them to every SaveScreenshot.  The oblique shape view then set view.ViewSize to
    [1600, 992] and fitted its camera for aspect 1.61 -- and was SAVED at [1600, 358],
    aspect 4.47.  The camera was fitted for a frame that was never rendered, so the body
    under-filled by exactly the ratio between the two aspects.  MEASURED: the report said
    the shape frame was [1600, 992]; the PNG header said 1600x358.

    The fix is not a better constant, it is removing the second copy.
    """
    res = [int(view.ViewSize[0]), int(view.ViewSize[1])]
    path = os.path.join(args.out, "%s_%s.png" % (args.tag, name))
    try:
        SaveScreenshot(path, view, ImageResolution=res, TransparentBackground=0)
        ok = os.path.exists(path) and os.path.getsize(path) > 0
        report["images"].append({"name": name, "path": path, "note": note,
                                 "resolution": res,
                                 "bytes": os.path.getsize(path) if ok else 0})
        print("RENDER_WROTE %s %d bytes" % (path, os.path.getsize(path) if ok else 0))
    except Exception as exc:                       # a render is not a gate
        report["errors"].append("%s: %r" % (name, exc))
        print("RENDER_FAILED %s: %r" % (name, exc))

# ---- 1. THE MESH, which is the thing Sanaa asked for by name.
d = Show(src, view)
d.SetRepresentationType("Surface With Edges")
ColorBy(d, None)
d.AmbientColor = [0.15, 0.15, 0.18]
d.DiffuseColor = [0.78, 0.82, 0.88]
d.EdgeColor = [0.12, 0.12, 0.15]
d.LineWidth = 1.0
d.Opacity = 1.0          # NOT translucent: the M6 set washed its field flat that way
Render()
shoot("mesh_single-level", "surface with edges; the ONE mesh -- this item has no grid family")

# ---- 2. FIELDS at the latest time = the finest state that exists for this item.
for fld, comp in (("U", "Magnitude"), ("p", None), ("T", None), ("nut", None)):
    if fld not in cell_arrays and fld not in point_arrays:
        report["errors"].append("field %s absent from the case" % fld)
        continue
    try:
        ColorBy(d, ("CELLS", fld, comp) if comp else ("CELLS", fld))
        d.SetRepresentationType("Surface")
        d.RescaleTransferFunctionToDataRange(True, False)
        lut = GetColorTransferFunction(fld)
        bar = GetScalarBar(lut, view)
        # DEFECT FOUND BY LOOKING AT THE FIRST RENDER, NOT BY REASONING ABOUT IT: on a
        # frame whose aspect is taken FROM THE GEOMETRY, a very wide short image leaves
        # no room for ParaView's default VERTICAL bar on the right -- it rendered half
        # off-frame with its title clipped.  Fitting the camera to the data and leaving
        # the legend at its default is fitting only half the picture.
        bar.Orientation = "Horizontal"
        bar.WindowLocation = "Any Location"
        bar.Position = [0.30, 0.03]
        bar.ScalarBarLength = 0.40
        bar.ScalarBarThickness = 12
        bar.Title = fld + (" magnitude" if comp else "")
        bar.ComponentTitle = ""          # else ParaView appends "Component" to the title
        bar.TitleColor = [0, 0, 0]; bar.LabelColor = [0, 0, 0]
        bar.TitleFontSize = 14; bar.LabelFontSize = 12
        d.SetScalarBarVisibility(view, True)
        Render()
        shoot("field_%s_wall_latest-t%s" % (fld, t_latest),
              "cell field %s on the WALL surface at the latest time %s" % (fld, t_latest))
        d.SetScalarBarVisibility(view, False)
    except Exception as exc:
        report["errors"].append("field %s: %r" % (fld, exc))

# ---- 2b. THE MIDPLANE SLICE.  THE WALL SURFACE IS NOT THE FLOW.
# Looking at the first field render showed the obvious thing the code had not: this is an
# INTERNAL duct, so a surface view of internalMesh shows the WALL, and the core flow -- the
# thing the optimisation is actually changing -- is behind it.  The slice is cut normal to
# the SHORTEST extent, i.e. the same axis the camera already looks down, so it needs no
# second camera and cannot disagree with the mesh view's framing.
try:
    Hide(src, view)
    sl = Slice(registrationName="midplane", Input=src)
    sl.SliceType = "Plane"
    sl.SliceType.Origin = ctr
    nrm = [0.0, 0.0, 0.0]; nrm[axis] = 1.0
    sl.SliceType.Normal = nrm
    dsl = Show(sl, view)
    dsl.SetRepresentationType("Surface")
    for fld, comp in (("U", "Magnitude"), ("p", None)):
        if fld not in cell_arrays and fld not in point_arrays:
            continue
        try:
            ColorBy(dsl, ("CELLS", fld, comp) if comp else ("CELLS", fld))
            dsl.RescaleTransferFunctionToDataRange(True, False)
            lut = GetColorTransferFunction(fld)
            bar = GetScalarBar(lut, view)
            bar.Orientation = "Horizontal"; bar.WindowLocation = "Any Location"
            bar.Position = [0.30, 0.03]; bar.ScalarBarLength = 0.40
            bar.ScalarBarThickness = 12
            bar.Title = fld + (" magnitude" if comp else ""); bar.ComponentTitle = ""
            bar.TitleColor = [0, 0, 0]; bar.LabelColor = [0, 0, 0]
            bar.TitleFontSize = 14; bar.LabelFontSize = 12
            dsl.SetScalarBarVisibility(view, True)
            Render()
            shoot("field_%s_midplane-slice_latest-t%s" % (fld, t_latest),
                  "cell field %s on the midplane slice -- THE CORE FLOW, which the wall "
                  "surface view hides" % fld)
            dsl.SetScalarBarVisibility(view, False)
        except Exception as exc:
            report["errors"].append("slice %s: %r" % (fld, exc))
    Hide(sl, view)
except Exception as exc:
    report["errors"].append("midplane slice: %r" % exc)

# ---- 3. THE OPTIMISED SHAPE -- implied by neither the mesh view nor the field views.
try:
    Hide(src, view)
    surf = ExtractSurface(registrationName="surf", Input=src)
    ds = Show(surf, view)
    # DEFECT FOUND BY OPENING THE IMAGE: the first version set DiffuseColor on a NEW
    # display and never called ColorBy(ds, None), so the "shape" render came out painted
    # with whatever field was coloured last -- a picture of nut captioned as the design
    # deliverable.  Setting a solid colour does nothing while an array is still mapped.
    ColorBy(ds, None)
    ds.SetRepresentationType("Surface")
    ds.DiffuseColor = [0.85, 0.60, 0.25]
    ds.Ambient = 0.25; ds.Diffuse = 0.75
    ds.Opacity = 1.0

    # SECOND DEFECT IN THIS SAME IMAGE, AND THE FIRST FIX REVEALED IT RATHER THAN CAUSING IT.
    # With the stale field colouring gone, the shape render came out a FLAT TAN SILHOUETTE:
    # correct, solid-coloured, and carrying no information about the shape it is named after.
    # Looking down the shortest axis is right for a mesh and for a slice and WRONG for a
    # body -- an orthographic plan view of a duct shows an outline, not a form.  A render you
    # open and learn nothing from fails the same test as one nobody opened.  So the shape
    # gets its OWN oblique camera and its own frame.
    diag = (ext[0] ** 2 + ext[1] ** 2 + ext[2] ** 2) ** 0.5
    SW = int(args.width); SH = int(round(args.width * 0.62))
    view.ViewSize = [SW, SH]
    view.CameraPosition = [ctr[0] - diag * 0.55, ctr[1] - diag * 0.85, ctr[2] + diag * 0.60]
    view.CameraFocalPoint = ctr
    view.CameraViewUp = [0.0, 0.0, 1.0]
    view.CameraParallelScale = _fit_parallel_scale(
        b, view.CameraPosition, ctr, [0.0, 0.0, 1.0], float(SW) / float(SH))
    report["shape_view"] = {"oblique": True, "image_size": [SW, SH],
                            "why": "an orthographic plan view of a duct is an outline, not a form"}
    Render()
    shoot("shape_optimised-boundary", "the deformed boundary surface at the latest time, "
                                      "OBLIQUE so the form reads -- the design deliverable, "
                                      "visible in neither the mesh nor the field views")
except Exception as exc:
    report["errors"].append("shape: %r" % exc)

with open(os.path.join(args.out, "%s_render_report.json" % args.tag), "w") as f:
    json.dump(report, f, indent=2, sort_keys=True)
print("RENDER_REPORT %s images=%d errors=%d" %
      (args.tag, len(report["images"]), len(report["errors"])))
sys.exit(0)   # DELIBERATE: a render failure is never a run verdict
