#!/usr/bin/env python3
"""Act C geometry, mesh and field visuals, RENDERED BY PARAVIEW FROM THE REAL
CASE FILES -- and refusing rather than emitting a picture it cannot stand behind.

Sanaa, 2026-09-01 ~20:14Z: "EVERYTHING should be paraview."  Every
geometry/mesh/field visual on this act is rendered here, from the served
surface and from the run's own mesh.  The three gate figures are LINE AND BAR
PLOTS and stay in matplotlib: ParaView replaces the canvas, not the plotting.

    pvpython render_actC_paraview.py geometry
    pvpython render_actC_paraview.py mesh
    pvpython render_actC_paraview.py field      -> REFUSES today, by design
    pvpython render_actC_paraview.py all

Run it with plain `python3` and it re-executes itself under a virtual
framebuffer (`xvfb-run pvbatch`), which this build needs -- see the
headless note at the foot of the file.

==========================================================================
THE THREE CONSTRAINTS, AND WHERE EACH ONE IS ENFORCED
==========================================================================

1. NO RENDER PIPELINE EVER WRITES INTO A GRADED RUN TREE.  Not a `.foam`, not
   a symlink into it, not a touch.  The age guard's entire content is that
   every field is newer than the case's own `0/T`, so a render that stamped a
   single mtime in that tree would invalidate the completion evidence this act
   is built on.  So: a SCRATCH case is materialised elsewhere, the run tree is
   only ever READ, and `run_tree_fingerprint()` asserts as a POST-CONDITION
   that not one mtime, size or name under it moved.  Measured before and after
   every render, not assumed.

2. A RENDER SCRIPT REFUSES RATHER THAN EMITTING A STALE OR EMPTY IMAGE.  An
   empty render is the visual form of a false zero: it looks like a picture,
   it opens in a viewer, and it says nothing.  So every image is read back off
   disk and must clear a spread floor, and the output file is REMOVED before
   the render so a failed pass cannot leave the previous one looking current.
   That second clause is not theoretical -- the same defect was measured in
   this act's sheet builder the same day, where a failed compile left the
   previous PDF on disk and the build reported success over it.

3. ⛔ A FIELD RENDER CARRIES ABSOLUTE KELVIN ON ITS COLOUR BAR, AND NO PDF OR
   STRING SWEEP CAN READ A PNG.  A picture is the one route around the entire
   withholding design: the text refuses to say how hot the module got and a
   colour bar says it anyway.  So `field` calls
   `actC_graded_admission.derive()` and REFUSES while the derived set is
   empty, which is the state today.  It is written that way from the first
   line rather than retrofitted, and the refusal is the default.

==========================================================================
TWO FINDINGS TAKEN FROM THE ACT A LANE RATHER THAN REDISCOVERED
==========================================================================

* OPENING A REGIONED CASE THE OBVIOUS WAY SILENTLY READS THE WRONG MESH and
  renders a plausible picture of it.  This case has two regions, `module` and
  `coolant`, with 3,840 and 12,768 cells.  Rather than trust a multi-region
  reader's region selection, each region is staged as its OWN single-region
  scratch case -- `constant/polyMesh` and nothing else -- so the reader has
  exactly one mesh it could possibly open.  The cell count is then ASSERTED
  against the mesh record, per region, and a mismatch refuses.  Belt and
  braces, because a plausible wrong picture is the failure that survives
  review.

* `os._exit` AROUND `paraview.simple` DISCARDS ALL OUTPUT: the stdout wrapper
  only flushes at interpreter finalisation.  So this module writes progress
  and refusals to file descriptors 1 and 2 DIRECTLY through `say()` and
  `refuse()`, never through a buffered `print`.  That is what makes the one
  deliberate `os._exit` at the foot of the file safe rather than reckless --
  it is used to leave with THIS script's exit code before ParaView's teardown
  raises `GLXBadContext` against the virtual display and turns a clean render
  into a non-zero exit.  The finding is not "never call `os._exit`"; it is
  "never call it with output still sitting in a wrapper", and this module has
  none.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, HERE)

RUNS = os.path.join(REPO, "verification", "runs", "T-family",
                    "T25R2_MODULE_runs")
CASE = os.path.join(RUNS, "T25R2_L1_OC20")
SERVED_STL = os.path.join(REPO, "sdk", "geometry", "battery_module_8cell.stl")
OUTDIR = os.path.join(HERE, "figures_actC_paraview")

#: Cells per region, READ from the mesh record rather than typed here, so the
#: assertion cannot agree with a stale number this file carries.
MESH_RECORD = os.path.join(RUNS, "MESH_VERIFICATION.txt")

#: Below this, an image is flat enough that it is not showing anything. A real
#: render of a mesh or a surface spans most of the range; a failed one is one
#: colour. Stated as a floor on the standard deviation of the greyscale, 0-255.
MIN_IMAGE_SPREAD = 6.0

#: And a floor on how much of the frame the subject occupies, so a correct
#: render of a speck in the corner is refused too.
MIN_INK_FRACTION = 0.02


# ---------------------------------------------------------------------------
# UNBUFFERED OUTPUT.  See the module docstring: a buffered print around
# paraview.simple can be discarded entirely.
# ---------------------------------------------------------------------------

def say(msg):
    os.write(1, (msg + "\n").encode())


def refuse(msg):
    os.write(2, ("REFUSE: " + msg + "\n").encode())
    raise SystemExit(2)


# ---------------------------------------------------------------------------
# CONSTRAINT 1 -- the run tree is read, never written
# ---------------------------------------------------------------------------

def run_tree_fingerprint(root=CASE):
    """Name, size and mtime of every file under the graded run tree.

    The whole tree, not a sample: a render that touched one file would
    otherwise have a 1-in-N chance of being caught, and the age guard this
    protects is decided by the single tightest margin over 1,810 field files.
    """
    h = hashlib.sha256()
    count = 0
    for base, dirs, files in os.walk(root):
        dirs.sort()
        for name in sorted(files):
            p = os.path.join(base, name)
            try:
                st = os.stat(p)
            except OSError:
                continue
            h.update(os.path.relpath(p, root).encode())
            h.update(b"%d:%d" % (st.st_size, int(st.st_mtime * 1000)))
            count += 1
    return h.hexdigest(), count


def assert_run_tree_untouched(before, label):
    after = run_tree_fingerprint()
    if after != before:
        refuse("the render CHANGED the graded run tree during %s "
               "(%d files before, %d after). Nothing in a render pipeline may "
               "write there: the completion evidence for this act is that "
               "every field is newer than the case's own start mark, and one "
               "stamped mtime invalidates it." % (label, before[1], after[1]))
    say("  run tree untouched: %d files, fingerprint %s"
        % (after[1], after[0][:12]))


# ---------------------------------------------------------------------------
# The mesh record, read
# ---------------------------------------------------------------------------

def region_cell_counts():
    import re
    text = open(MESH_RECORD).read()
    m = re.search(r"^=+\nT25R2_L1_OC20\b.*?\n=+\n(.*?)(?=\n=+\n|\Z)",
                  text, re.S | re.M)
    if not m:
        refuse("the mesh record carries no block for this run, so there is "
               "nothing to assert a rendered cell count against")
    q = re.search(r"cells\s+module\s+(\d+)\s+\+\s+coolant\s+(\d+)\s+=\s+(\d+)",
                  m.group(1))
    if not q:
        refuse("the mesh record carries no cell counts")
    return {"module": int(q.group(1)), "coolant": int(q.group(2)),
            "total": int(q.group(3))}


# ---------------------------------------------------------------------------
# The scratch case.  COPIED, never symlinked into the run tree.
# ---------------------------------------------------------------------------

CONTROLDICT = """FoamFile { version 2.0; format ascii; class dictionary;
object controlDict; }
application     none;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         0;
deltaT          1;
writeControl    timeStep;
writeInterval   1;
"""


def stage_region(region, workdir):
    """One region as its OWN single-region case, so the reader cannot pick the
    wrong mesh -- there is only one for it to pick."""
    src = os.path.join(CASE, "constant", region, "polyMesh")
    if not os.path.isdir(src):
        refuse("no mesh on disk for the %s region" % region)
    dst = os.path.join(workdir, region)
    os.makedirs(os.path.join(dst, "constant"), exist_ok=True)
    os.makedirs(os.path.join(dst, "system"), exist_ok=True)
    shutil.copytree(src, os.path.join(dst, "constant", "polyMesh"))
    with open(os.path.join(dst, "system", "controlDict"), "w") as fh:
        fh.write(CONTROLDICT)
    # The .foam handle lives HERE, in the scratch, and never in the run tree.
    foam = os.path.join(dst, "%s.foam" % region)
    open(foam, "w").close()
    return foam


# ---------------------------------------------------------------------------
# CONSTRAINT 2 -- an image is read back and must show something
# ---------------------------------------------------------------------------

def assert_image_shows_something(path, label):
    try:
        import numpy as np
        from PIL import Image
    except Exception as exc:                                    # noqa: BLE001
        refuse("cannot read the rendered image back (%s). An image nobody "
               "read is not evidence that anything rendered." % exc)
    if not os.path.exists(path):
        refuse("%s produced no image at all" % label)
    arr = np.asarray(Image.open(path).convert("L"), dtype=float)
    spread = float(arr.std())
    bg = float(np.median(arr))
    ink = float((np.abs(arr - bg) > 12).mean())
    if spread < MIN_IMAGE_SPREAD or ink < MIN_INK_FRACTION:
        refuse("%s rendered a near-empty frame: spread %.2f (floor %.2f), "
               "subject covers %.3f of the frame (floor %.3f). An empty image "
               "is the visual form of a false zero -- it opens in a viewer and "
               "says nothing." % (label, spread, MIN_IMAGE_SPREAD, ink,
                                  MIN_INK_FRACTION))
    say("  %s: %dx%d, spread %.1f, subject covers %.1f%% of the frame"
        % (label, arr.shape[1], arr.shape[0], spread, ink * 100))
    return {"spread": spread, "ink_fraction": ink,
            "width": arr.shape[1], "height": arr.shape[0]}


def fresh(path):
    """Remove an existing image BEFORE rendering, so a failed pass cannot
    leave the previous one looking current."""
    if os.path.exists(path):
        os.remove(path)


# ---------------------------------------------------------------------------
# THE RENDERS
# ---------------------------------------------------------------------------

def _pv():
    from paraview import simple
    simple._DisableFirstRenderCameraReset()
    return simple


def render_geometry(out):
    """The served surface: 8 cell blocks, 7 channel gaps, inside its housing.

    The housing is not decoration -- the act's assumption beat is that the
    user drew one and this run does not conduct through it -- so it is
    rendered rather than cropped away, and named in the geometry table. See
    the note in the body for what this render does not do.
    """
    simple = _pv()
    fresh(out)
    stl = simple.STLReader(FileNames=[SERVED_STL])
    view = simple.CreateRenderView()
    view.ViewSize = [1280, 900]
    view.Background = [1.0, 1.0, 1.0]
    view.UseColorPaletteForBackground = 0
    view.OrientationAxesVisibility = 0

    simple.UpdatePipeline(proxy=stl)
    bounds = stl.GetDataInformation().GetBounds()
    # ⚠ WHAT THIS RENDER DOES AND DOES NOT DO, STATED RATHER THAN OVERSOLD.
    # The housing IS visible -- it is the enclosing plate the eight cell
    # blocks and their seven gaps sit inside -- but it is NOT colour-coded
    # apart from the stack, because the surface is one solid body and a box
    # clip that isolated the shell would cut the stack with it. The
    # distinction the act's assumption beat turns on is therefore carried by
    # the geometry table ("housing shell found: not conducted through in this
    # run") and by the beat itself, not by a colour here. Colour-coding it
    # needs the surface regenerated as two named solids, which is a change to
    # the served geometry and is not this script's to make.
    d = simple.Show(stl, view)
    d.Representation = "Surface With Edges"
    d.AmbientColor = [0.15, 0.15, 0.15]
    d.DiffuseColor = [0.72, 0.76, 0.82]
    d.EdgeColor = [0.25, 0.28, 0.33]
    d.LineWidth = 0.6
    view.CameraPosition = [bounds[1] * 6, bounds[3] * 0.5, bounds[5] * 8]
    view.CameraFocalPoint = [(bounds[0] + bounds[1]) / 2,
                             (bounds[2] + bounds[3]) / 2,
                             (bounds[4] + bounds[5]) / 2]
    simple.ResetCamera(view)
    simple.Render(view)
    simple.SaveScreenshot(out, view, ImageResolution=[1280, 900])
    return assert_image_shows_something(out, "geometry")


def render_mesh(out_prefix, workdir):
    """The real grid, cell by cell, one region at a time, cell count asserted."""
    simple = _pv()
    want = region_cell_counts()
    results = {}
    for region in ("module", "coolant"):
        foam = stage_region(region, workdir)
        out = "%s_%s.png" % (out_prefix, region)
        fresh(out)
        rd = simple.OpenFOAMReader(FileName=foam)
        rd.MeshRegions = ["internalMesh"]
        rd.CellArrays = []
        simple.UpdatePipeline(proxy=rd)
        info = rd.GetDataInformation()
        got = int(info.GetNumberOfCells())
        if got != want[region]:
            refuse("the %s mesh rendered %d cells; the mesh record registers "
                   "%d. A regioned case opened the obvious way reads the WRONG "
                   "mesh and draws a perfectly plausible picture of it, which "
                   "is why this is asserted rather than trusted."
                   % (region, got, want[region]))
        say("  %s mesh: %d cells, matches the record" % (region, got))
        view = simple.CreateRenderView()
        view.ViewSize = [1280, 900]
        view.Background = [1.0, 1.0, 1.0]
        view.UseColorPaletteForBackground = 0
        view.OrientationAxesVisibility = 0
        disp = simple.Show(rd, view)
        disp.Representation = "Surface With Edges"
        disp.DiffuseColor = ([0.80, 0.82, 0.86] if region == "module"
                             else [0.72, 0.84, 0.92])
        disp.EdgeColor = [0.20, 0.22, 0.26]
        disp.LineWidth = 0.4
        # LOOK DOWN THE DEPTH AXIS, AND SET THE ZOOM RATHER THAN RESETTING IT.
        # The solve is two-dimensional at unit depth, so the mesh on disk is a
        # 1 m extrusion of a 0.1 x 0.261 m section. MEASURED, in this order:
        # letting the camera fit all three extents gave the cells 2.8% of the
        # frame; turning the camera to face the section and then calling
        # ResetCamera made it WORSE at 1.6%, because ResetCamera fits the
        # depth into the parallel scale whatever direction the camera faces.
        # So the scale is computed from the section's own extents and the
        # frame's aspect, and ResetCamera is not called at all.
        b = info.GetBounds()
        cx, cy, cz = ((b[0] + b[1]) / 2, (b[2] + b[3]) / 2, (b[4] + b[5]) / 2)
        aspect = 1280.0 / 900.0
        view.CameraPosition = [cx, cy, b[5] + max(1.0, b[5] - b[4])]
        view.CameraFocalPoint = [cx, cy, cz]
        view.CameraViewUp = [0.0, 1.0, 0.0]
        view.CameraParallelProjection = 1
        view.CameraParallelScale = 0.54 * max(b[3] - b[2],
                                              (b[1] - b[0]) / aspect)
        simple.Render(view)
        simple.SaveScreenshot(out, view, ImageResolution=[1280, 900])
        results[region] = assert_image_shows_something(out, "%s mesh" % region)
        results[region]["cells"] = got
        simple.Delete(rd)
    results["total_cells"] = sum(results[r]["cells"]
                                 for r in ("module", "coolant"))
    if results["total_cells"] != want["total"]:
        refuse("the two regions rendered %d cells together; the record "
               "registers %d" % (results["total_cells"], want["total"]))
    return results


def render_field(out):
    """⛔ GATED ON THE GRADED ARTEFACT. Refuses while nothing is graded.

    A colour bar carries absolute kelvin at its end ticks, and neither the PDF
    guard nor the act-string sweep can read a PNG. This is the one surface that
    could put a withheld temperature on screen without any sweep noticing, so
    it consults the SAME derivation the guard and the act consult, and refuses
    while the derived set is empty.
    """
    import actC_graded_admission as ADMIT
    values, note = ADMIT.derive()
    say("  admissibility source: %s" % note)
    if not values:
        refuse("no field is rendered: nothing is graded, so a colour bar here "
               "would put an absolute temperature on screen that the text is "
               "refusing to state. No sweep can read a PNG, so this refusal is "
               "the only thing standing between the withholding rule and a "
               "picture that breaks it. The act's convergence-study ending is "
               "what plays instead.")
    refuse("a graded set exists (%d value(s)) but the field render itself is "
           "not built yet. Building it is the next step and it must colour "
           "ONLY from graded quantities, with the colour bar ticks checked "
           "against the same allowlist." % len(values))


# ---------------------------------------------------------------------------

def main(argv):
    mode = argv[0] if argv else "all"
    if mode not in ("geometry", "mesh", "field", "all"):
        refuse("mode is geometry, mesh, field or all")
    for p in (CASE, SERVED_STL, MESH_RECORD):
        if not os.path.exists(p):
            refuse("a source this render needs is not on disk: %s"
                   % os.path.basename(p))
    os.makedirs(OUTDIR, exist_ok=True)

    say("Act C -- ParaView renders from the real case files")
    before = run_tree_fingerprint()
    say("  run tree fingerprinted before: %d files, %s"
        % (before[1], before[0][:12]))

    import tempfile
    workdir = tempfile.mkdtemp(prefix="actC_render_")
    report = {}
    try:
        if mode in ("geometry", "all"):
            report["geometry"] = render_geometry(
                os.path.join(OUTDIR, "actC_geometry.png"))
            assert_run_tree_untouched(before, "the geometry render")
        if mode in ("mesh", "all"):
            report["mesh"] = render_mesh(
                os.path.join(OUTDIR, "actC_mesh"), workdir)
            assert_run_tree_untouched(before, "the mesh render")
        if mode == "field":
            render_field(os.path.join(OUTDIR, "actC_field.png"))
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

    assert_run_tree_untouched(before, "the whole run")
    with open(os.path.join(OUTDIR, "render_report.json"), "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    say("wrote %s" % OUTDIR)
    return 0


def _exit_before_paraview_teardown(rc):
    """Leave with OUR exit code, before ParaView tears its GL context down.

    MEASURED ON THIS BOX: every render above completed, every assertion
    passed, the report was written -- and the process then exited 1 because
    ParaView's teardown raised `GLXBadContext` against the virtual display.
    An exit code that reports a teardown error as a render failure is a check
    that cries wolf, and a check that cries wolf gets ignored on the day it is
    right.

    ⚠ THIS USES `os._exit`, WHICH THE ACT A LANE MEASURED AS DISCARDING ALL
    OUTPUT -- and it is safe HERE for the specific reason that finding names.
    The output is discarded because the stdout WRAPPER only flushes at
    interpreter finalisation, which `os._exit` skips. This module never writes
    through that wrapper: `say()` and `refuse()` write to file descriptors 1
    and 2 directly, so there is nothing buffered to lose. The scratch
    directory is removed by the caller before this is reached, because
    `os._exit` also skips `finally`.
    """
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(rc)


if __name__ == "__main__":
    # THE TEST IS "CAN WE RENDER", NOT "CAN WE IMPORT", AND THAT DISTINCTION
    # COST A CRASH. `paraview.simple` imports perfectly under plain `python3`
    # on this box; it is the first `Render()` that segfaults, because there is
    # no display for `vtkXRenderWindowInteractor` to attach to. A guard that
    # asked whether the module imports therefore answered yes and let the
    # process walk into the crash. So the condition is an explicit sentinel:
    # unless we are already the re-executed child, re-execute under a virtual
    # framebuffer regardless of what imports.
    if os.environ.get("ACTC_RENDER_HEADLESS") != "1":
        # HEADLESS, AND NOT OPTIONAL ON THIS BOX. Measured: this ParaView
        # build has no working offscreen path -- `pvpython` segfaults in
        # `vtkXRenderWindowInteractor::Initialize` and `pvbatch
        # --force-offscreen-rendering` aborts in `CreateAWindow` -- so a
        # virtual framebuffer is what makes a render possible at all. Stated
        # here rather than left as a mysterious crash for the next reader.
        pvb = shutil.which("pvbatch")
        xvfb = shutil.which("xvfb-run")
        if not pvb:
            refuse("pvbatch is not on PATH, so no ParaView render can run")
        if not xvfb:
            refuse("xvfb-run is not on PATH and this ParaView build has no "
                   "working offscreen path (measured: pvpython segfaults and "
                   "pvbatch --force-offscreen-rendering aborts)")
        env = dict(os.environ, ACTC_RENDER_HEADLESS="1")
        os.execve(xvfb, [xvfb, "-a", "-s", "-screen 0 1600x1200x24", pvb,
                         os.path.abspath(__file__)] + sys.argv[1:], env)
    try:
        _rc = main(sys.argv[1:])
    except SystemExit as exc:
        _rc = exc.code if isinstance(exc.code, int) else 2
    _exit_before_paraview_teardown(_rc)
