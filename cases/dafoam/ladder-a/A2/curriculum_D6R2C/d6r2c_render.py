#!/usr/bin/env pvbatch
"""D6R2C completion render -- EXTERNAL WING.  OFFSCREEN.  ZERO COMPUTE.  READ-ONLY input.

RETARGETED FROM MP_A5R.  What carried over is the discipline, not the pictures: the
bbox-corner camera fit, ONE source for the frame size, ColorBy(...,None) so a shape is a
shape, the legend fitted with the data, copy-never-the-graded-tree, and judging success by
IMAGES COUNTED ON DISK.

WHAT DID NOT CARRY OVER, AND WAS NOT PORTED.  MP_A5R is an internal duct, where a surface
view of internalMesh shows the WALL and hides the core, so it got a midplane slice.  THE
PRINCIPLE CARRIES -- show the flow the optimisation is actually changing -- THE REALISATION
DOES NOT.  For an EXTERNAL wing the same mistake wears the opposite costume: a surface view
of internalMesh shows the FARFIELD BOX, and the body is inside it.  So every surface view
here is taken on `patch/wing`, and the flow is shown on spanwise sections THROUGH the wing.

ZERO COMPUTE, AND STRICTER THAN THE PRECEDENT.  d6r2_render_prep.sh ran reconstructPar in a
container.  This reads the DECOMPOSED case directly (CaseType='Decomposed Case'), so no
reconstruct, no container, no solver binary runs at all.

M-INFINITY IS MEASURED HERE, NOT ASSUMED.  The item is registered as "the 3D TRANSONIC
multipoint optimisation", and its own run script carries U0=100, T0=300 -> M_inf = 0.288,
which is SUBSONIC.  A render built to show "the shock" would then be a picture captioned as
something the data does not contain -- the same defect class as colouring a shape render
with a stale turbulence field.  So local Mach is COMPUTED from the fields and its measured
range is written into the report, and the caption follows the measurement.

A RENDER IS NOT A GATE.  Exits 0 even on failure.
"""
import argparse, json, math, os, sys

ap = argparse.ArgumentParser()
ap.add_argument("--case", required=True, help="an OpenFOAM case COPY, never a graded tree")
ap.add_argument("--out", required=True)
ap.add_argument("--tag", required=True)
ap.add_argument("--U0", type=float, default=100.0)
ap.add_argument("--p0", type=float, default=101325.0)
ap.add_argument("--T0", type=float, default=300.0)
ap.add_argument("--width", type=int, default=1600)
ap.add_argument("--decomposed", action="store_true")
args = ap.parse_args()

from paraview.simple import *  # noqa: E402
paraview.simple._DisableFirstRenderCameraReset()

RHO0 = args.p0 / (args.T0 * 287.0)
QINF = 0.5 * RHO0 * args.U0 * args.U0
AINF = math.sqrt(1.4 * 287.0 * args.T0)
MINF = args.U0 / AINF

os.makedirs(args.out, exist_ok=True)
rep = {"tag": args.tag, "case": os.path.abspath(args.case), "images": [], "errors": [],
       "level_label": "single-level",
       "level_note": ("D6R2C optimises on ONE mesh across three lift conditions. It has no grid "
                      "family, so 'coarse mesh / fine-mesh fields' has no referent here. Naming "
                      "this mesh 'coarse' to match the instruction's shape would be a label that "
                      "looks compliant and is false."),
       "freestream": {"U0": args.U0, "p0": args.p0, "T0": args.T0, "rho0": RHO0,
                      "q_inf": QINF, "a_inf": AINF, "M_inf": MINF},
       "Cp_definition": "(p - p0) / q_inf, q_inf = 0.5*rho0*U0^2"}

foam = os.path.join(args.case, "case.foam")
if not os.path.exists(foam):
    open(foam, "w").close()

src = OpenFOAMReader(registrationName="case", FileName=foam)
src.CaseType = "Decomposed Case" if args.decomposed else "Reconstructed Case"
src.UpdatePipelineInformation()
# `list(src.MeshRegions)` is the CURRENT SELECTION, not the catalogue.  Reading it and
# concluding "no patch/wing in this case" is how the first run of this script rendered the
# FARFIELD DOME and captioned it as the wing -- the exact mistake the docstring above warns
# about, committed three lines after writing the warning.  `.Available` is the catalogue.
avail = list(src.MeshRegions.Available)
rep["mesh_regions_available"] = avail
WING = "patch/wing" if "patch/wing" in avail else None
src.MeshRegions = ["internalMesh"]
src.UpdatePipelineInformation()
times = list(src.TimestepValues) or [0.0]
t = max(times)
rep["time_rendered"] = t
UpdatePipeline(time=t, proxy=src)

# ---- derived fields.  Cp and Mach are CALCULATED, never read from a field that is not there.
mach = Calculator(registrationName="Mach", Input=src)
mach.AttributeType = "Cell Data"
mach.ResultArrayName = "Mach"
mach.Function = "mag(U)/sqrt(1.4*287.0*T)"
UpdatePipeline(time=t, proxy=mach)
cp = Calculator(registrationName="Cp", Input=mach)
cp.AttributeType = "Cell Data"
cp.ResultArrayName = "Cp"
cp.Function = "(p - %.6f)/%.6f" % (args.p0, QINF)
UpdatePipeline(time=t, proxy=cp)

def rng(proxy, name):
    try:
        ai = proxy.GetCellDataInformation().GetArray(name)
        return [ai.GetRange()[0], ai.GetRange()[1]] if ai else None
    except Exception:
        return None

rep["Mach_range_measured"] = rng(cp, "Mach")
rep["Cp_range_measured"] = rng(cp, "Cp")
mr = rep["Mach_range_measured"]
rep["shock_present_by_data"] = (
    "NO LOCAL SUPERSONIC REGION: max local Mach %.3f < 1. The item id says 'transonic'; its own "
    "U0/T0 give M_inf %.3f. THE CAPTION FOLLOWS THE MEASUREMENT." % (mr[1], MINF)
    if mr and mr[1] < 1.0 else
    ("LOCAL SUPERSONIC REGION PRESENT: max local Mach %.3f >= 1" % mr[1] if mr else "UNMEASURED"))

view = CreateView("RenderView")
view.UseColorPaletteForBackground = 0
view.Background = [1.0, 1.0, 1.0]
view.OrientationAxesVisibility = 0
view.CameraParallelProjection = 1

def project_half_extents(bounds, cam, focal, up_in):
    """Half-width and half-height of the bbox AS PROJECTED at this camera angle.

    fit_scale alone only guarantees the box FITS.  It cannot remove margin, because a box
    whose projected aspect is A, drawn in a frame whose aspect is B, must leave slack on one
    axis -- and my first wing view hardcoded the frame at 0.66 while fitting the camera, so
    the wing filled about 35% of the width.  THAT IS THE SAME WHITE-MARGIN DEFECT AGAIN, one
    level up: the first time the ZOOM was guessed, this time the FRAME SHAPE was.
    Measuring both and letting the frame follow the projection leaves ~3% on both axes.
    """
    fwd = [focal[i] - cam[i] for i in range(3)]
    n = math.sqrt(sum(c * c for c in fwd)) or 1.0
    fwd = [c / n for c in fwd]
    up = list(up_in)
    dd = sum(up[i] * fwd[i] for i in range(3))
    up = [up[i] - dd * fwd[i] for i in range(3)]
    n = math.sqrt(sum(c * c for c in up)) or 1.0
    up = [c / n for c in up]
    right = [fwd[1]*up[2]-fwd[2]*up[1], fwd[2]*up[0]-fwd[0]*up[2], fwd[0]*up[1]-fwd[1]*up[0]]
    hs, ws = [], []
    for xi in (bounds[0], bounds[1]):
        for yi in (bounds[2], bounds[3]):
            for zi in (bounds[4], bounds[5]):
                v = [xi-focal[0], yi-focal[1], zi-focal[2]]
                hs.append(abs(sum(v[i]*up[i] for i in range(3))))
                ws.append(abs(sum(v[i]*right[i] for i in range(3))))
    return max(ws), max(hs)


def frame_for(bounds, cam, focal, up_in, width, margin=1.03):
    """(ViewSize, ParallelScale) with the FRAME SHAPE TAKEN FROM THE PROJECTION."""
    hw, hh = project_half_extents(bounds, cam, focal, up_in)
    if hh <= 0 or hw <= 0:
        return [int(width), int(width)], (max(hh, hw) or 1.0) * margin
    a = hw / hh
    if a >= 1.0:
        W = int(width); H = max(240, int(round(width / a)))
    else:
        H = int(width); W = max(240, int(round(width * a)))
    return [W, H], hh * margin


def fit_scale(bounds, cam, focal, up_in, aspect, margin=1.03):
    """Half-height that makes the box FILL the frame at THIS angle.  No constant to tune:
    a guessed zoom factor cannot fit both an axis-aligned and an oblique view, which is the
    defect that put 35-45% white margin into the M6 set and into my own first attempt."""
    fwd = [focal[i] - cam[i] for i in range(3)]
    n = math.sqrt(sum(c * c for c in fwd)) or 1.0
    fwd = [c / n for c in fwd]
    up = list(up_in)
    d = sum(up[i] * fwd[i] for i in range(3))
    up = [up[i] - d * fwd[i] for i in range(3)]
    n = math.sqrt(sum(c * c for c in up)) or 1.0
    up = [c / n for c in up]
    right = [fwd[1]*up[2]-fwd[2]*up[1], fwd[2]*up[0]-fwd[0]*up[2], fwd[0]*up[1]-fwd[1]*up[0]]
    hs, ws = [], []
    for xi in (bounds[0], bounds[1]):
        for yi in (bounds[2], bounds[3]):
            for zi in (bounds[4], bounds[5]):
                v = [xi-focal[0], yi-focal[1], zi-focal[2]]
                hs.append(abs(sum(v[i]*up[i] for i in range(3))))
                ws.append(abs(sum(v[i]*right[i] for i in range(3))))
    return max(max(hs), (max(ws)/aspect) if aspect else max(hs)) * margin

def shoot(name, note):
    """Resolution READ FROM THE VIEW.  One quantity, one place (L-221/L-222)."""
    res = [int(view.ViewSize[0]), int(view.ViewSize[1])]
    path = os.path.join(args.out, "%s_%s.png" % (args.tag, name))
    try:
        SaveScreenshot(path, view, ImageResolution=res, TransparentBackground=0)
        rep["images"].append({"name": name, "path": path, "note": note, "resolution": res,
                              "bytes": os.path.getsize(path)})
        print("RENDER_WROTE %s" % path)
    except Exception as exc:
        rep["errors"].append("%s: %r" % (name, exc))
        print("RENDER_FAILED %s: %r" % (name, exc))

def legend(fld, title):
    lut = GetColorTransferFunction(fld)
    bar = GetScalarBar(lut, view)
    bar.Orientation = "Horizontal"; bar.WindowLocation = "Any Location"
    bar.Position = [0.30, 0.04]; bar.ScalarBarLength = 0.40; bar.ScalarBarThickness = 12
    bar.Title = title; bar.ComponentTitle = ""
    bar.TitleColor = [0, 0, 0]; bar.LabelColor = [0, 0, 0]
    bar.TitleFontSize = 14; bar.LabelFontSize = 12
    return bar

# ---- THE BODY, not the farfield box.
if WING:
    # A DEDICATED READER SELECTING ONLY THE WING PATCH, instead of extracting a block out of
    # a multiblock and hoping the selector string matches.  The ExtractBlock spelling failed
    # SILENTLY on this case and the fallback rendered the farfield.  A reader that is given
    # one region cannot hand back another.
    wsrc = OpenFOAMReader(registrationName="wingonly", FileName=foam)
    wsrc.CaseType = src.CaseType
    wsrc.MeshRegions = [WING]
    wsrc.UpdatePipelineInformation()
    wm = Calculator(registrationName="wMach", Input=wsrc)
    wm.AttributeType = "Cell Data"; wm.ResultArrayName = "Mach"
    wm.Function = "mag(U)/sqrt(1.4*287.0*T)"
    wc = Calculator(registrationName="wCp", Input=wm)
    wc.AttributeType = "Cell Data"; wc.ResultArrayName = "Cp"
    wc.Function = "(p - %.6f)/%.6f" % (args.p0, QINF)
    UpdatePipeline(time=t, proxy=wc)
    target = wc
else:
    rep["errors"].append("no patch/wing in this case; falling back to the whole domain")
    target = cp

# THE BODY MUST NOT BE THE DOMAIN.  A wing whose bbox is the farfield box means the wrong
# thing is being rendered, and the caption would be false rather than merely ugly.
_tb = target.GetDataInformation().GetBounds()
_te = [_tb[1]-_tb[0], _tb[3]-_tb[2], _tb[5]-_tb[4]]
_ib = cp.GetDataInformation().GetBounds()
_ie = [_ib[1]-_ib[0], _ib[3]-_ib[2], _ib[5]-_ib[4]]
rep["domain_extents"] = _ie
if WING and max(_te) > 0.5 * max(_ie):
    rep["errors"].append(
        "REFUSING THE CAPTION: the 'wing' target spans %.1f against a domain of %.1f -- that is "
        "the farfield, not the body." % (max(_te), max(_ie)))
    print("RENDER_REFUSE wing target is the farfield: %s vs domain %s" % (_te, _ie))

b = target.GetDataInformation().GetBounds()
ext = [b[1]-b[0], b[3]-b[2], b[5]-b[4]]
ctr = [(b[0]+b[1])/2, (b[2]+b[3])/2, (b[4]+b[5])/2]
rep["wing_bounds"] = list(b); rep["wing_extents"] = ext
diag = math.sqrt(sum(e*e for e in ext)) or 1.0

# PLANFORM, DERIVED FROM THE BOUNDING BOX RATHER THAN ASSUMED.
# I hardcoded this as "looking down -z" and it was wrong: MEASURED on this wing the extents
# are x=9.00 (chord), y=0.70 (thickness), z=14.04 (span), so the planform looks down Y and
# the span is Z.  The duct renderer derived its view axis from the geometry and was right;
# I dropped that rule when porting and immediately rendered the wing edge-on.  A rule that
# is abandoned at the port is not a rule.
THICK = ext.index(min(ext))            # planform is viewed down the THINNEST axis
SPAN = ext.index(max(ext))             # sections are cut along the LONGEST axis
CHORD = [i for i in (0, 1, 2) if i not in (THICK, SPAN)][0]
rep["axes_derived"] = {"chord": "xyz"[CHORD], "span": "xyz"[SPAN], "thickness": "xyz"[THICK],
                       "extents": ext}
cam = list(ctr); cam[THICK] = ctr[THICK] + diag * 3.0
up_pf = [0.0, 0.0, 0.0]; up_pf[CHORD] = 1.0
vs, ps = frame_for(b, cam, ctr, up_pf, args.width)
view.ViewSize = vs
view.CameraPosition = cam; view.CameraFocalPoint = ctr; view.CameraViewUp = up_pf
view.CameraParallelScale = ps
rep["planform_frame"] = vs

d = Show(target, view)
d.SetRepresentationType("Surface With Edges")
ColorBy(d, None)
d.DiffuseColor = [0.80, 0.83, 0.88]; d.EdgeColor = [0.10, 0.10, 0.13]; d.Opacity = 1.0
Render(); shoot("mesh_wing_single-level", "the WING SURFACE mesh -- an external case's "
                                          "internalMesh surface is the FARFIELD BOX, not the body")

for fld, title in (("Cp", "Cp = (p - p_inf)/q_inf"), ("Mach", "local Mach")):
    try:
        d.SetRepresentationType("Surface")
        ColorBy(d, ("CELLS", fld))
        d.RescaleTransferFunctionToDataRange(True, False)
        legend(fld, title); d.SetScalarBarVisibility(view, True)
        Render(); shoot("field_%s_wing-surface_t%s" % (fld, t),
                        "%s on the wing surface at the latest time" % fld)
        d.SetScalarBarVisibility(view, False)
    except Exception as exc:
        rep["errors"].append("wing %s: %r" % (fld, exc))

# ---- SPANWISE SECTIONS.  For a wing this is the analogue of the duct's midplane slice.
Hide(target, view)
span_axis = SPAN                        # was hardcoded 1; the span is measured, not assumed
lo, hi = b[2*span_axis], b[2*span_axis+1]
fracs = [0.20, 0.50, 0.80]
try:
    sl = Slice(registrationName="span", Input=cp)
    sl.SliceType = "Plane"
    nrm = [0.0, 0.0, 0.0]; nrm[span_axis] = 1.0
    sl.SliceType.Normal = nrm
    _org = list(ctr); _org[span_axis] = lo + 0.5*(hi-lo)
    sl.SliceType.Origin = _org
    sl.SliceOffsetValues = [ (lo + f*(hi-lo)) - (lo + 0.5*(hi-lo)) for f in fracs ]
    # CLIP TO THE WING, or the "section" is a 540 x 270 slab of farfield with a 9-unit wing
    # somewhere inside it, and the camera fit -- correctly -- frames the farfield.
    box = Clip(registrationName="nearfield", Input=sl)
    box.ClipType = "Box"
    pad = [max(0.6*e, 0.25*max(ext)) for e in ext]
    try:
        box.ClipType.Position = [b[0]-pad[0], b[2]-pad[1], b[4]-pad[2]]
        box.ClipType.Length = [ext[0]+2*pad[0], ext[1]+2*pad[1], ext[2]+2*pad[2]]
        box.Invert = 1
    except Exception as exc:
        rep["errors"].append("nearfield clip: %r" % exc)
    UpdatePipeline(time=t, proxy=box)
    sl = box
    UpdatePipeline(time=t, proxy=sl)
    dsl = Show(sl, view)
    dsl.SetRepresentationType("Surface")
    sb = sl.GetDataInformation().GetBounds()
    sc = [(sb[0]+sb[1])/2, (sb[2]+sb[3])/2, (sb[4]+sb[5])/2]
    cam2 = list(sc); cam2[span_axis] = sb[2*span_axis] - diag*2.0
    # UP MUST NOT BE THE VIEW AXIS.  It was [0,0,1] while the camera looked along z --
    # a degenerate camera, and the render came out BLANK except for its legend.  A picture
    # with nothing in it passes every check that counts files.
    up_sec = [0.0, 0.0, 0.0]; up_sec[THICK] = 1.0
    vs3, ps3 = frame_for(sb, cam2, sc, up_sec, args.width)
    view.ViewSize = vs3
    view.CameraPosition = cam2; view.CameraFocalPoint = sc; view.CameraViewUp = up_sec
    view.CameraParallelScale = ps3
    rep["span_sections_at_fraction"] = fracs
    for fld, title in (("Mach", "local Mach"), ("Cp", "Cp = (p - p_inf)/q_inf")):
        ColorBy(dsl, ("CELLS", fld))
        dsl.RescaleTransferFunctionToDataRange(True, False)
        legend(fld, title); dsl.SetScalarBarVisibility(view, True)
        Render(); shoot("field_%s_spanwise-sections_t%s" % (fld, t),
                        "%s on spanwise sections at %s span -- the flow the optimisation moves"
                        % (fld, fracs))
        dsl.SetScalarBarVisibility(view, False)
    Hide(sl, view)
except Exception as exc:
    rep["errors"].append("spanwise sections: %r" % exc)

# ---- THE OPTIMISED SHAPE.  Solid, oblique, and NOT coloured by a leftover array.
try:
    ds = Show(target, view)
    ColorBy(ds, None)                      # without this the "shape" is a picture of a field
    ds.SetRepresentationType("Surface")
    ds.DiffuseColor = [0.85, 0.60, 0.25]; ds.Ambient = 0.25; ds.Diffuse = 0.75
    cam_ob = list(ctr)
    cam_ob[CHORD] -= diag*0.45; cam_ob[THICK] -= diag*0.75; cam_ob[SPAN] += diag*0.50
    vs2, ps2 = frame_for(b, cam_ob, ctr, [0, 0, 1], args.width)
    view.ViewSize = vs2
    view.CameraPosition = cam_ob; view.CameraFocalPoint = ctr; view.CameraViewUp = [0, 0, 1]
    view.CameraParallelScale = ps2
    rep["shape_frame"] = vs2
    Render(); shoot("shape_optimised-wing", "the wing surface at the latest time -- the design "
                                            "deliverable, in neither the mesh nor the field views")
except Exception as exc:
    rep["errors"].append("shape: %r" % exc)

with open(os.path.join(args.out, "%s_render_report.json" % args.tag), "w") as f:
    json.dump(rep, f, indent=2, sort_keys=True)
print("RENDER_REPORT %s images=%d errors=%d M_inf=%.3f Mach_range=%s"
      % (args.tag, len(rep["images"]), len(rep["errors"]), MINF, rep["Mach_range_measured"]))
sys.exit(0)
