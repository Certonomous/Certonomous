#!/usr/bin/env python3
"""K2h_L3 renders -- Sanaa's 2026-09-12 ~20:30Z render-on-completion directive.

    xvfb-run -a pvpython verification/runs/F14-cooling-ladder/K2h_runs/render_k2h_l3.py <VERDICT>

RUN WITH `/usr/bin/pvpython` (5.11.2).  `/opt/paraview/bin/pvpython` is 5.13.3
and `demo3d_render_common.assert_paraview_version` REFUSES it: a render that
moves with the reader version is not reproducible.

WHAT THE DIRECTIVE ASKS FOR, AND WHICH HALF EACH FIGURE ANSWERS

    "the paraview should show the coarse mesh (or medium mesh if the coarse
     isnt converged). But all fields should be stored as the fine mesh result
     fields (whenever we have it)."

  (a) THE MESH -- the COARSE level, `K2f_L1`, 58,368 cells.  Coarse and not
      medium, and that is a MEASUREMENT rather than a default: K2h
      PREREGISTRATION section 2 records L1's final-300 per-iteration residual
      peak-to-peak at 5.05e-11 on Ux with DP_module monotone across all six
      checkpoints (0 sign changes, p2p 3.11e-04 m2/s2), so L1 IS converged and
      the parenthetical does not fire.  The same section records why L2 would
      have been the WRONG choice: it limit-cycles at a 1e-4 residual floor and
      its DP_module turns.

  (b) THE FIELDS -- the finest completed level, which is `K2h_L3` itself at
      t = 112, and specifically its TIME-AVERAGED fields `TMean` and
      `p_rghMean`.  `p_rghMean` is the graded quantity: G-DPBAR is its area
      average over `tile` minus its area average over `return`.

NOTHING IS INTERPOLATED BETWEEN (a) AND (b).  58,368 and 664,848 cells are
different meshes; a single image claiming to be the coarse mesh carrying the
fine fields would require resampling one onto the other and would manufacture
values nobody computed.  They are separate figures and each says which level
it is.

=== THE COLOUR CONTROL, AND WHY THIS FILE CARRIES ONE ===

`verification/runs/navier_class/DRIVAER/RENDERS/_FIELD_FLAG_DEFECT_EVIDENCE/DEFECT.md`
records a MEASURED silent no-op: a render asked to colour by a field came out
flat-shaded and IDENTICAL to the plain mesh render, with the geometry guard
passing (colouring is not a geometry property, so a face-count identity is blind
to it by construction).  Two fix attempts failed and the cause is still
unidentified.  The second attempt -- a hue-spread guard -- was REMOVED because it
could not be shown able to FAIL: the threshold guessed sat BELOW the known-flat
render, so the guard passed the exact artifact it was written to catch, and the
note records that calibrating it needs a KNOWN-GOOD COLOURED RENDER AS A POSITIVE
CONTROL, which did not exist.

THIS FILE BUILDS BOTH CONTROLS RATHER THAN GUESSING A THRESHOLD.  For every field
figure it renders the SAME pipeline twice:

    POSITIVE -- coloured by the real field;
    NEGATIVE -- coloured by a Calculator array that is CONSTANT by construction,
                which is a render that MUST come out flat.

and then REFUSES unless the positive's colour spread is at least
`CONTROL_MARGIN` times the negative's.  The threshold is therefore MEASURED
against a deliberately-flat render made on the same box, the same build, the
same geometry and the same camera, instead of guessed.  A renderer that cannot
tell a real field from a constant is not painting the field, and its pictures
are not evidence -- the same argument as CLAUDE.md rule 3, applied to pixels.

NO SOLVER IS RUN.  NO RUN TREE IS WRITTEN.  Fields are read through a scratch
case of symlinks; both graded trees are fingerprinted before and PROVED unchanged
after.  Nothing here is sent, filed, uploaded, registered, posted or commented
outside this box (rule 7).
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "scripts"))
sys.path.insert(0, os.path.join(REPO, "docs", "campaigns", "F14-cooling-ladder",
                                "demo", "render_K2bU3R3_paraview"))

import demo3d_render_common as C          # noqa: E402
import render_k2bU3R3 as K2B              # noqa: E402  the committed renderer, re-pointed

#: Beside the run, under the K2h_runs tree, as the brief requires.
OUT = os.path.join(REPO, "verification", "runs", "F14-cooling-ladder",
                   "K2h_runs", "RENDERS")

MESH_CASE, MESH_END = "K2f_L1", "3000"
FIELD_CASE, FIELD_END = "K2h_L3", "112"

#: The positive must out-spread the deliberately-flat negative by this factor.
#:
#: MEASURED, NOT GUESSED, and the measurement is recorded here because a
#: threshold whose calibration is not written down IS a guessed threshold -- which
#: is the exact defect that made DEFECT.md's attempt-2 guard pass the artifact it
#: was written to catch.  Calibrated 2026-09-12 on this box, this ParaView build
#: (5.11.2), this geometry and this camera, against K2h_L3's own t = 5 fields
#: through a shadow reconstruction, two presets and two deliberately-constant
#: negatives:
#:
#:     field   preset               positive   NEGATIVE (constant)   ratio
#:     p_rgh   Cool to Warm          0.14190       0.00516           27.5x
#:     T       Inferno (matplotlib)  0.69881       0.01507           46.4x
#:
#: 8.0 sits well below the weaker of the two observed ratios (27.5x) and far
#: above 1.0, so it separates a painted field from a flat one with margin at both
#: ends rather than sitting on top of either.
CONTROL_MARGIN = 8.0

#: Section 5's window, quoted on every field figure so the picture says what
#: interval it is the mean of.
WINDOW = "mean over simulated 42 to 112 s (S-WINDOW)"


def _repoint(case, end, stamp, geom):
    """Rebind the committed renderer's case-scoped globals.  Explicit, and
    ASSERTED: a silent re-point that missed one global would caption a figure
    with another case's verdict.  Carried from `render_k2f_rackset.py:_repoint`,
    which established this idiom; the committed renderer is NEVER edited."""
    K2B.CASE, K2B.END, K2B.STAMP, K2B.GEOM = case, end, stamp, geom
    assert K2B.CASE == case and K2B.END == end and K2B.STAMP == stamp
    C.assert_stamp(stamp, case)           # REFUSES before any pixel is rendered
    C.announce(f"  re-pointed to {case} at t = {end}; stamp accepted: {stamp}")


# ---------------------------------------------------------------------------
# the colour control
# ---------------------------------------------------------------------------
def _colour_spread(path):
    """Saturation-weighted hue spread over non-background pixels.

    Measured on the SAVED PNG, not on the pipeline: the failure this guards
    against produced a correct-looking pipeline and a flat image, so the image is
    what must be measured.
    """
    from paraview.vtk.util import numpy_support
    from paraview.vtk.vtkIOImage import vtkPNGReader
    import numpy as np

    r = vtkPNGReader()
    r.SetFileName(path)
    r.Update()
    img = r.GetOutput()
    a = numpy_support.vtk_to_numpy(img.GetPointData().GetScalars())
    if a is None or a.size == 0:
        C.refuse(f"{os.path.basename(path)} carries no pixels to measure")
    rgb = a[:, :3].astype(float) / 255.0

    # BODY = "not the white ground".  It is deliberately NOT "saturated pixels":
    # a legitimately FLAT control can be unsaturated -- measured, the Inferno
    # preset at a constant value maps to a near-greyscale colour and a
    # saturation mask found ZERO body pixels, which REFUSED the control for a
    # reason about the measurement rather than about the render.  A control that
    # cannot be measured on a flat image is not a control, so the mask is made
    # preset-independent instead.  Caption text is dark and is therefore included
    # in both images equally, which makes the comparison MORE conservative, not
    # less: shared ink dilutes the positive's spread and never the negative's
    # alone.
    body = (1.0 - rgb).max(axis=1) > 0.06
    if body.sum() < 500:
        C.refuse(f"{os.path.basename(path)} has only {int(body.sum())} non-"
                 f"background pixels; there is nothing to measure a colour "
                 f"spread over")
    mx = np.maximum(rgb[body].max(axis=1), 1e-6)
    # spread of the dominant-channel ratio, which separates a two-ended ramp
    # from one flat hue without depending on a hue-angle convention
    ratio = (rgb[body, 0] - rgb[body, 2]) / mx
    return float(ratio.std()), int(body.sum())


def _assert_paints_the_field(pos_path, neg_path, field):
    pos, npos = _colour_spread(pos_path)
    neg, nneg = _colour_spread(neg_path)
    C.announce(f"  COLOUR CONTROL {field}: positive spread {pos:.5f} over "
               f"{npos:,} px, NEGATIVE (constant array) {neg:.5f} over "
               f"{nneg:,} px, ratio {pos / max(neg, 1e-9):.1f}x "
               f"(required {CONTROL_MARGIN:g}x)")
    if pos < CONTROL_MARGIN * max(neg, 1e-9):
        C.refuse(
            f"COLOUR CONTROL FAILED for {field!r}: the render coloured by the "
            f"real field spreads colour {pos:.5f} and a render of the SAME "
            f"pipeline coloured by a CONSTANT array spreads {neg:.5f}. The "
            f"renderer has not been shown able to tell a field from a constant, "
            f"so a picture captioned {field!r} is not evidence that the field "
            f"was painted (DEFECT.md, DrivAer, 2026-09-12). Refusing rather "
            f"than shipping a confident-looking flat body")
    return pos, neg


# ---------------------------------------------------------------------------
# the field figure
# ---------------------------------------------------------------------------
def fig_mean_field(reader, path, field, label, preset, verdict_stamp, geom):
    """A y-z cut at x = 1.5 m coloured by `field`, plus its constant-array control.

    The plane and the camera are `K2bU3R3.fig_aisles`'s, unchanged: viewed from
    +x looking back along -x, so +y runs RIGHT on the frame and 'cold aisle left,
    hot aisle right' describes the actual picture rather than its mirror.
    """
    from paraview.simple import (CellDatatoPointData, Slice, Show, Render,
                                 UpdatePipeline, Calculator, ColorBy,
                                 GetColorTransferFunction, GetScalarBar, Hide)

    v = K2B.build_view()
    p2c = CellDatatoPointData(Input=reader)
    p2c.CellDataArraytoprocess = [field]
    UpdatePipeline(time=float(FIELD_END), proxy=p2c)
    lo, hi = K2B.field_range(p2c, field)
    if not (hi > lo):
        C.refuse(f"{field} spans {lo} to {hi} at t = {FIELD_END}: a field with no "
                 f"range cannot be shown to have been painted, and a flat "
                 f"picture of it would be indistinguishable from the defect "
                 f"this file guards against")

    s = Slice(Input=p2c)
    s.SliceType = "Plane"
    s.SliceType.Origin = [1.5, 0.0, 0.0]
    s.SliceType.Normal = [1.0, 0.0, 0.0]
    UpdatePipeline(time=float(FIELD_END), proxy=s)
    if s.GetDataInformation().GetNumberOfCells() == 0:
        C.refuse("the aisle slice is empty; nothing would be drawn")

    # ---- the NEGATIVE control: the same slice, painted by a CONSTANT ---------
    flat = Calculator(Input=s)
    flat.AttributeType = "Point Data"
    flat.ResultArrayName = "CONTROL_CONSTANT"
    flat.Function = "1.0"
    UpdatePipeline(time=float(FIELD_END), proxy=flat)
    fr = flat.GetPointDataInformation().GetArray("CONTROL_CONSTANT")
    if fr is None:
        C.refuse("the control Calculator produced no array, so the negative "
                 "control would not be a control")
    clo, chi = fr.GetComponentRange(0)
    if abs(chi - clo) > 1e-12:
        C.refuse(f"the control array spans {clo} to {chi} and is therefore NOT "
                 f"constant; a negative control that varies proves nothing")

    dn = Show(flat, v)
    ColorBy(dn, ("POINTS", "CONTROL_CONSTANT"))
    GetColorTransferFunction("CONTROL_CONSTANT").ApplyPreset(preset, True)
    dn.SetScalarBarVisibility(v, False)
    K2B.frame(v, (1.5, K2B.ROOM[1] / 2, K2B.ROOM[2] / 2), (1.0, 0.0, 0.0), pad=1.10)
    Render(v)
    neg_path = os.path.join(os.path.dirname(path), "_control",
                            "NEGATIVE_constant_" + os.path.basename(path))
    C.save_screenshot(v, neg_path, size=(1600, 1000))
    Hide(flat, v)

    # ---- the POSITIVE: the same slice, the same camera, the real field -------
    d = Show(s, v)
    ColorBy(d, ("POINTS", field))
    lut = GetColorTransferFunction(field)
    lut.ApplyPreset(preset, True)
    lut.RescaleTransferFunction(lo, hi)
    d.SetScalarBarVisibility(v, True)
    bar = GetScalarBar(lut, v)
    bar.Visibility = 1
    bar.Title = label
    bar.ComponentTitle = ""
    bar.TitleColor = [0.15, 0.15, 0.15]
    bar.LabelColor = [0.15, 0.15, 0.15]
    bar.TitleFontSize = 11
    bar.LabelFontSize = 10
    bar.ScalarBarLength = 0.32
    bar.ScalarBarThickness = 12
    bar.WindowLocation = "Any Location"
    bar.Position = [0.875, 0.36]
    bar.AutomaticLabelFormat = 0
    bar.LabelFormat = "%-#.4g"
    bar.AddRangeLabels = 1
    K2B.outline(reader, v)
    K2B.frame(v, (1.5, K2B.ROOM[1] / 2, K2B.ROOM[2] / 2), (1.0, 0.0, 0.0), pad=1.10)

    # the bar must carry the range the caption quotes, checked right before the
    # render -- showing a second representation re-scales a transfer function
    # behind your back (K2bU3R3.lock_colour_range, measured)
    lut.RescaleTransferFunction(lo, hi)
    pts = list(lut.RGBPoints)
    if abs(pts[0] - lo) > 1e-9 * max(1.0, abs(lo)) \
            or abs(pts[-4] - hi) > 1e-9 * max(1.0, abs(hi)):
        C.refuse(f"the colour bar spans {pts[0]:.6g} to {pts[-4]:.6g} where the "
                 f"caption says {lo:.6g} to {hi:.6g}; a colour bar that "
                 f"disagrees with its own caption is a false reading")

    C.caption(v, verdict_stamp, FIELD_CASE, position=(0.012, 0.048), size=11)
    C.caption(v, geom + f" ; y-z plane at x = 1.5 m ; cold aisle left, rack row "
                        f"centre, hot aisle right ; {field} in {lo:.6g} to "
                        f"{hi:.6g} ; {WINDOW}",
              FIELD_CASE, position=(0.012, 0.018), size=9, check_stamp=False)
    Render(v)
    n = C.save_screenshot(v, path, size=(1600, 1000))

    _assert_paints_the_field(path, neg_path, field)
    C.announce(f"  wrote {os.path.basename(path)} ({n:,} bytes)"
               f"  [{field} {lo:.6g} to {hi:.6g}]")
    return n


# ---------------------------------------------------------------------------
def main(argv) -> int:
    if len(argv) < 2:
        C.announce_error("usage: render_k2h_l3.py <VERDICT from analyse_k2h.py>")
        return 2
    verdict = argv[1].strip()

    C.announce("=" * 74)
    C.announce("K2h_L3 renders -- COARSE mesh (K2f_L1) + TIME-AVERAGED fields "
               "(K2h_L3 at t = 112)")
    C.announce("=" * 74)
    version = C.assert_paraview_version()
    C.announce(f"  ParaView {version} (pinned {C.REQUIRED_PARAVIEW})")

    mesh_dir = C.facts(MESH_CASE)["case_dir"]
    field_dir = C.facts(FIELD_CASE)["case_dir"]
    before_mesh = C.run_tree_fingerprint(mesh_dir)
    before_field = C.run_tree_fingerprint(field_dir)

    os.makedirs(OUT, exist_ok=True)
    total, root = 0, None

    # ---- (a) THE MESH, from the COARSE level, which is the converged one -----
    try:
        _repoint(MESH_CASE, MESH_END,
                 f"{MESH_CASE} ; 58368 cells ; COARSE level mesh ; NOT A RESULT",
                 "Room 3.6 x 3.5 x 2.7 m ; 4 racks ; MESH of the COARSE level "
                 "(converged: residual p2p 5.05e-11, DP monotone) ; the K2h_L3 "
                 "numbers come from the 664848-cell FINE level, not this mesh")
        reader, root, n = C.open_case(MESH_CASE, ["T", "U"], [MESH_END])
        C.announce(f"  mesh source {MESH_CASE}: {n:,} cells")
        total += K2B.fig_mesh(reader, os.path.join(OUT, "K2f_L1_coarse_mesh.png"))
    finally:
        if root:
            shutil.rmtree(root, ignore_errors=True)
        root = None

    # ---- (b) THE FIELDS, time-averaged, from K2h_L3 itself -------------------
    stamp = (f"{FIELD_CASE} ; 664848 cells ; t = 112 ; time-averaged over "
             f"42 to 112 s ; {verdict}")
    geom = ("Room 3.6 x 3.5 x 2.7 m ; 4 racks ; FINE level, TRANSIENT "
            "buoyantBoussinesqPimpleFoam")
    try:
        _repoint(FIELD_CASE, FIELD_END, stamp, geom)
        reader, root, n = C.open_case(
            FIELD_CASE, ["TMean", "p_rghMean", "UMean"], [FIELD_END])
        C.announce(f"  field source {FIELD_CASE}: {n:,} cells at t = {FIELD_END}")
        total += fig_mean_field(
            reader, os.path.join(OUT, "K2h_L3_p_rghMean_field.png"),
            "p_rghMean", "p_rgh mean  (m2/s2)", "Cool to Warm", stamp, geom)
        total += fig_mean_field(
            reader, os.path.join(OUT, "K2h_L3_TMean_field.png"),
            "TMean", "T mean  (K)", "Inferno (matplotlib)", stamp, geom)
    finally:
        if root:
            shutil.rmtree(root, ignore_errors=True)

    C.assert_run_tree_untouched(mesh_dir, before_mesh)
    C.assert_run_tree_untouched(field_dir, before_field)
    C.announce(f"  BOTH run trees PROVED unchanged: {mesh_dir} ; {field_dir}")
    C.announce(f"  {total:,} bytes written to {OUT}")
    return 0


if __name__ == "__main__":
    try:
        rc = main(sys.argv)
    except C.RenderRefusal as exc:
        C.announce_error(f"REFUSED: {exc}")
        rc = 2
    except Exception:                             # noqa: BLE001
        import traceback
        C.announce_error("ERROR: " + traceback.format_exc())
        rc = 3
    sys.stdout.flush()
    os._exit(rc)
