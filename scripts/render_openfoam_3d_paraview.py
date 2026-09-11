"""3-D surface/patch renders of a solved OpenFOAM case, with a guard that can fail.

WHY THIS EXISTS.  ``scripts/render_openfoam_paraview.py`` is 2-D-EXTRUDED-ONLY BY
CONSTRUCTION: its one topology-changing filter is a mid-span Slice, and it asserts
the slice's polygon count equals the mesh's cell count.  On a genuine 3-D mesh that
identity can never hold -- measured on F25-DUCT3D fine, the mid-span slice produced
32,768 polygons for a 2,097,152-cell mesh (1.56 % of the grid) and the script
REFUSED.  THAT REFUSAL IS CORRECT and is not routed around here: a mid-span slice of
a 3-D domain is not the solved grid.  This is a second instrument for a different
class of case, not a loosening of the first.  The 2-D script remains the tool for
2-D extruded cases.

WHAT IS POLISH AND WHAT IS NOT.  Polish is camera, colormap, background, resolution.
Polish is NEVER the data.  Nothing here decimates, smooths or substitutes geometry.

=== RULE 3, AND WHY THE GUARD IS THE POINT OF THIS FILE ===

A renderer that draws a decimated, clipped or WRONG case still produces a
confident-looking picture.  So every render asserts:

    sum over rendered patches of (rendered surface cells) == sum of nFaces for
    those patches, read from the case's own constant/polyMesh/boundary

SCOPE OF THAT GUARD, STATED HONESTLY: it is a SUM identity, not a per-patch one.
It catches a reader that drops whole patches -- measured: DrivAer r1_fine returned
13,734 of 379,519 faces with 48 of 52 patches silently zero -- because dropped
patches change the total.  It would NOT catch a COMPENSATING error in which two
patches exchanged counts.  UPGRADED 2026-09-11: the guard is NOW a PER-PATCH identity
(rendered[p] == nFaces[p] for every p) as well as a sum, so the compensating
error IS caught.  --selftest drives that limb with a SWAP control and also
asserts that the SUM is blind to the same swap, so the stronger limb is shown
to be doing work the weaker one cannot.

MEASURED, NOT ASSUMED.  The ratio was established by measurement before this
assertion's form was fixed (probe on F25-DUCT3D fine, 2026-09-11):

    inlet   nFaces 4096    rendered 4096    ratio 1.000000
    outlet  nFaces 4096    rendered 4096    ratio 1.000000
    wall    nFaces 131072  rendered 131072  ratio 1.000000

ParaView's OpenFOAM reader does NOT triangulate patch faces, so the relationship is
EXACT EQUALITY and equality is what is asserted.  It was not assumed to be equality
and then loosened when it failed -- that would be fitting a guard to the answer.
If a future ParaView build triangulates, this guard FAILS LOUDLY, which is correct:
re-measure the multiple and assert that, do not relax the test.

--selftest DRIVES the refusal rather than describing it, because a guard asserted
but never driven is not a guard.  Two negative controls, both of which MUST refuse:
  (a) WRONG-CASE control: the expected face count is perturbed by +1.  Must refuse.
  (b) DECIMATED-SURFACE control: a Decimate filter is applied to the rendered
      surface.  Must refuse.
And one positive control:
  (c) the unperturbed render.  Must PASS -- so the checker is shown able to return
      both verdicts.  A guard that only ever refuses is as useless as one that
      never does.
--selftest exits 2 unless all three verdicts appear.

=== READ-ONLY BY CONSTRUCTION, NOT BY PROMISE ===

The graded tree is NEVER opened for write.  The case is staged into a scratch
directory as SYMLINKS to its constant/, system/ and time directories, and the
``case.foam`` stub ParaView's reader requires is created IN THE STAGE.

This matters because it is a measured hazard, not a theoretical one.  The 2-D
script writes ``case.foam`` INTO the graded case directory (line 841), and on
2026-09-11 a zero-byte ``case.foam`` appeared in
verification/runs/F25_DUCT3D_runs/fine as a result.  Harmless there -- zero bytes,
not in 0/, not a field at endTime, so rule 4's age guard was untouched -- but the
property was breached, and it is the THIRD instrument found writing into graded
trees in this territory.

The read-only property is PROVEN, not promised: --selftest takes an mtime+inode
census of the case tree before and after and REFUSES if it changed.

CENSUS INTEGRITY, AND THIS COST A FALSE POSITIVE TO LEARN.  The census MUST sort.
An unsorted ``find -printf | md5sum`` is NON-DETERMINISTIC -- find does not
guarantee traversal order, so two censuses of an UNCHANGED tree can differ and
report a write that never happened.  That is exactly what happened on 2026-09-11
before this was fixed.  The census here sorts, and --selftest proves it BOTH ways:
it must return identical hashes on an untouched tree AND must detect a planted
touch.  A census that cannot see a plant is not evidence (rule 3).

HOW TO RUN.  ParaView 5.11.2 at /usr/bin/pvbatch is an X11/GLX-only build, so it
needs a virtual framebuffer:

    xvfb-run -a pvbatch scripts/render_openfoam_3d_paraview.py --case <case> --out <dir>

NEVER pass --force-offscreen-rendering.  It ABORTS even with a healthy display on
this build, and that single flag cost an ansys lane seven failed attempts and a
false "ParaView cannot render on this box" conclusion (L-545).  This script does
not accept the flag and does not set it.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import sys

if not __debug__:
    sys.stderr.write("REFUSED: must not run under python3 -O; asserts carry the guard.\n")
    sys.exit(2)


# ----------------------------------------------------------------------------
# The case's own boundary file -- the ground truth the guard compares against.
# ----------------------------------------------------------------------------
def parse_boundary(case):
    """{patch: (nFaces, type)} read from constant/polyMesh/boundary.

    Read from the CASE, never from a manifest: a manifest can be internally
    consistent and externally false.
    """
    path = os.path.join(case, "constant", "polyMesh", "boundary")
    if not os.path.isfile(path):
        sys.stderr.write("REFUSED: no constant/polyMesh/boundary under %s\n" % case)
        sys.exit(2)
    txt = open(path).read()
    txt = re.sub(r"/\*.*?\*/", "", txt, flags=re.S)
    txt = re.sub(r"//[^\n]*", "", txt)
    body = txt[txt.index("(") + 1: txt.rindex(")")]
    out = {}
    for m in re.finditer(r"([A-Za-z_][\w.\-]*)\s*\{", body):
        name = m.group(1)
        depth, j = 1, m.end()
        while depth and j < len(body):
            if body[j] == "{":
                depth += 1
            elif body[j] == "}":
                depth -= 1
            j += 1
        blk = body[m.end():j - 1]
        nf = re.search(r"\bnFaces\s+(\d+)\s*;", blk)
        ty = re.search(r"\btype\s+(\w+)\s*;", blk)
        if nf:
            out[name] = (int(nf.group(1)), ty.group(1) if ty else "unknown")
    if not out:
        sys.stderr.write("REFUSED: parsed zero patches from %s -- the reader is blind.\n" % path)
        sys.exit(2)
    return out


# ----------------------------------------------------------------------------
# Census -- MUST sort, and MUST be shown able to see a plant.
# ----------------------------------------------------------------------------
def census(root):
    """Deterministic mtime+inode census of a tree.

    SORTED.  An unsorted walk is non-deterministic and produces false positives;
    see the module docstring.

    STATED LIMIT, so a successor does not assume total coverage: this keys on
    mtime + inode + path.  A write that PRESERVED both mtime and inode would be
    invisible to it.  That is a real blind spot, not a theoretical one -- a tool
    that restores timestamps after writing would defeat this census.
    """
    rows = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for n in sorted(filenames) + sorted(dirnames):
            p = os.path.join(dirpath, n)
            try:
                st = os.lstat(p)
                rows.append("%.6f %d %s" % (st.st_mtime, st.st_ino, p))
            except OSError:
                rows.append("MISSING %s" % p)
    return hashlib.md5("\n".join(sorted(rows)).encode()).hexdigest()


# ----------------------------------------------------------------------------
# Read-only staging.  case.foam goes in the STAGE, never in the graded tree.
# ----------------------------------------------------------------------------
def stage_readonly(case, stage_dir):
    if os.path.exists(stage_dir):
        shutil.rmtree(stage_dir)
    os.makedirs(stage_dir)
    for entry in os.listdir(case):
        if entry == "case.foam":
            continue          # never propagate a stub found in a graded tree
        os.symlink(os.path.abspath(os.path.join(case, entry)),
                   os.path.join(stage_dir, entry))
    foam = os.path.join(stage_dir, "case.foam")
    open(foam, "w").close()
    return foam


# ----------------------------------------------------------------------------
# THE GUARD.
# ----------------------------------------------------------------------------
def rendered_face_count(foam, patches, decimate=False):
    """Total rendered surface cells over `patches`, read back from the pipeline."""
    from paraview.simple import (OpenFOAMReader, Decimate, ExtractSurface,
                                 Triangulate)
    # === ONE READER FOR ALL PATCHES. MEASURED DEFECT, 2026-09-11. ===
    # This was written as one OpenFOAMReader PER PATCH.  On DrivAer r1_fine (52
    # wall patches) that returned 13,734 faces against 379,519 declared: only the
    # FIRST FOUR patches alphabetically produced geometry and the other 48
    # returned EXACTLY ZERO -- silently, with no exception and no warning.  It
    # would have rendered a car from four body panels, which reads as a styling
    # crop rather than as a broken render, and rc would have been 0.
    # ONLY THE FACE-COUNT IDENTITY CAUGHT IT.
    # A single reader carrying all 52 MeshRegions returns 379,519 == 379,519,
    # measured.  So the per-patch total is built from ONE reader, and per-patch
    # figures are reported by reading each region off that same reader only when
    # a breakdown is asked for.
    # BOTH PATHS USE THE SINGLE READER.  An earlier version guarded the fast path
    # with `if not decimate:` and left decimate=True falling through to the
    # per-patch form -- so the DECIMATION CONTROL ran through the known
    # under-reading reader.  That control asserts the guard REFUSES on a decimated
    # surface; driven through an under-reading counter it could have gone green
    # BECAUSE THE READER UNDER-READ rather than because decimation worked, and the
    # two are indistinguishable from the verdict line.  It was safe only because
    # the selftest fixture has few patches -- an accident of the fixture, not a
    # property of the control.  NO PATH KEEPS THE DEFECTIVE FORM.
    total, per = 0, {}
    r = OpenFOAMReader(FileName=foam)
    r.MeshRegions = ["patch/" + n for n in patches]
    r.UpdatePipeline()
    if not decimate:
        total = r.GetDataInformation().GetNumberOfCells()
        # PER-PATCH BREAKDOWN FROM THE SAME (GOOD) READER OBJECT.
        # MEASURED 2026-09-11: re-setting MeshRegions on ONE reader gives correct
        # per-patch counts -- DrivAer r1_fine returned 52 of 52 patches matching
        # and a total of 379,519 == 379,519.  The defect was constructing 52
        # SEPARATE readers, not querying 52 regions.  ParaView 5.11 removed
        # GetCompositeDataInformation, so this is the available route.
        # THIS UPGRADES THE GUARD FROM A SUM IDENTITY TO A PER-PATCH IDENTITY,
        # which is strictly stronger: a SUM cannot see a COMPENSATING error in
        # which two patches exchange counts; a per-patch identity can.
        for n in patches:
            r.MeshRegions = ["patch/" + n]
            r.UpdatePipeline()
            per[n] = r.GetDataInformation().GetNumberOfCells()
        r.MeshRegions = ["patch/" + n for n in patches]
        r.UpdatePipeline()
        return total, per
    for name in [None]:
        src = r
        if decimate:
            # MEASURED GOTCHA, 2026-09-11: vtkDecimatePro REFUSES non-triangle
            # polygons ("DecimatePro does not accept polygons that are not
            # triangles"), and OpenFOAM patch faces are quads.  Decimate alone was
            # therefore a SILENT NO-OP and the negative control passed 139,264
            # faces through unchanged -- i.e. the control did not control anything.
            # Caught only because --selftest DRIVES it.  Triangulate first so the
            # decimation is real.
            #
            # SECOND TRAP, SAME CONTROL, 2026-09-11 -- AN ARITHMETIC COINCIDENCE.
            # Triangulate DOUBLES a quad surface (131,072 -> 262,144) and
            # TargetReduction=0.5 HALVES it, so the round trip returned EXACTLY
            # the original 131,072 and the "decimated" control again reported the
            # PASSING number -- by a different mechanism than the first no-op and
            # equally invisible.  TargetReduction is 0.9 (measured: 262,144 ->
            # 26,213) so the control cannot coincide with the true count.
            # THE LESSON, since this control produced a false PASS twice: a
            # negative control must be CHECKED TO DIFFER from the positive one,
            # never assumed to differ because of what the filter is named.
            src = Decimate(Input=Triangulate(Input=ExtractSurface(Input=r)),
                           TargetReduction=0.9)
            src.UpdatePipeline()
        n = src.GetDataInformation().GetNumberOfCells()
        per["__decimated_all_patches__"] = n
        total += n
    return total, per


def assert_per_patch_identity(boundary, patches, per_patch, where):
    """REFUSE unless rendered[p] == nFaces[p] for EVERY p.

    Strictly stronger than the sum identity: the sum cannot see a COMPENSATING
    error in which two patches exchange counts.  Measured achievable 2026-09-11
    (DrivAer r1_fine, 52 of 52).
    """
    bad = []
    for p in patches:
        exp = boundary[p][0]
        got = per_patch.get(p)
        if got != exp:
            bad.append((p, got, exp))
    if bad:
        sys.stderr.write(
            "REFUSED (%s): per-patch identity failed for %d of %d patches. "
            "rendered != nFaces from the case's own boundary file:\n" %
            (where, len(bad), len(patches)))
        for p, got, exp in bad[:12]:
            sys.stderr.write("    %-32s rendered=%s nFaces=%s\n" % (p, got, exp))
        return False
    return True


def assert_surface_is_the_mesh(expected, measured, per_patch, where):
    """REFUSE unless the rendered surface IS the case's own boundary surface.

    Equality is asserted because equality was MEASURED (module docstring).
    """
    if measured != expected:
        sys.stderr.write(
            "REFUSED: the rendered surface carries %d faces but the case's own "
            "constant/polyMesh/boundary declares %d for the rendered patches "
            "(%s). The picture would not be the solved mesh surface.\n"
            "  per-patch rendered: %s\n" % (measured, expected, where, per_patch))
        return False
    return True


def measure_ink(path):
    """Fraction of pixels differing from the modal (background) colour.

    Read BACK OFF DISK, not from the pipeline: the question is what is in the
    file somebody will look at, not what the renderer believed it drew.
    """
    from paraview.vtk.vtkIOImage import vtkPNGReader
    from paraview.vtk.util import numpy_support
    r = vtkPNGReader()
    r.SetFileName(path)
    r.Update()
    img = r.GetOutput()
    arr = numpy_support.vtk_to_numpy(img.GetPointData().GetScalars())
    if arr.size == 0:
        return 0.0
    import numpy as np
    rgb = arr[:, :3].astype(np.int32)
    packed = (rgb[:, 0] << 16) | (rgb[:, 1] << 8) | rgb[:, 2]
    vals, counts = np.unique(packed, return_counts=True)
    return float(len(packed) - counts.max()) / float(len(packed))


def assert_three_dimensional(case):
    """REFUSE any case that is not genuinely 3-D.  Returns (ok, detail).

    WHY THIS IS A STRUCTURAL GUARD AND NOT AN INK THRESHOLD.  On 2026-09-11 an
    axisymmetric WEDGE case (SUP_BOOSTER E2) was ordered onto a 3-D render list
    and rendered.  Its wall patch carries 165 faces and the resulting sliver
    passed --min-ink 0.0020 at 0.0026 -- by 30 %.  A guard a wedge clears by 30 %
    will not catch the next one, so the ink floor is NOT the instrument for this.

    TWO READINGS, AND DISAGREEMENT IS ITSELF A REFUSAL:
      (1) constant/polyMesh/boundary must contain NO patch of type 'wedge' or
          'empty'.  Those two types ARE the axisymmetric/2-D signature.
      (2) where a checkMesh log is present, its
          'Mesh has N geometric (non-empty/wedge) directions' line must read 3.
    If the two disagree the case is REFUSED rather than either reading being
    preferred -- a disagreement means one of them is wrong and we do not know
    which.  NOTE the trap this encodes: checkMesh prints a 'solution
    (non-empty) directions' line four lines away that reads 3 for a wedge, so a
    reader matching the wrong line certifies a wedge as 3-D.  The GEOMETRIC line
    is the test (SUBOFF_A1_PREREGISTRATION.md 5.1 M-c).
    """
    b = parse_boundary(case)
    bad = [(n, t) for n, (nf, t) in b.items() if t in ("wedge", "empty")]

    geom = None
    import glob as _glob
    for log in sorted(_glob.glob(os.path.join(case, "log.checkMesh*"))):
        for line in open(log, errors="replace"):
            m = re.search(r"Mesh has (\d+) geometric \(non-empty/wedge\) directions", line)
            if m:
                geom = int(m.group(1))
                break
        if geom is not None:
            break

    from_boundary_3d = not bad
    if geom is not None and (geom == 3) != from_boundary_3d:
        return False, ("READINGS DISAGREE: boundary file says %s, checkMesh says "
                       "%d geometric directions. Refusing rather than preferring "
                       "either." % ("3-D" if from_boundary_3d else "not 3-D", geom))
    if bad:
        return False, ("case is NOT 3-D: patches %s carry axisymmetric/2-D types. "
                       "checkMesh geometric directions = %s."
                       % (bad, geom if geom is not None else "not logged"))
    if geom is not None and geom != 3:
        return False, "checkMesh reports %d geometric directions, not 3." % geom
    return True, "3-D confirmed (no wedge/empty patch%s)" % (
        "; checkMesh geometric directions = 3" if geom == 3 else "")


# ----------------------------------------------------------------------------
def do_selftest(case, out):
    """Drive every verdict.  Describing a guard is not driving it."""
    stage = os.path.join(out, "_selftest_stage")
    verdicts = {}

    # --- census, both directions (rule 3 applied to the census itself) -------
    c1 = census(case)
    c2 = census(case)
    verdicts["census_deterministic"] = (c1 == c2)

    plant = os.path.join(out, "_selftest_plant")
    if os.path.exists(plant):
        shutil.rmtree(plant)
    os.makedirs(plant)
    f = os.path.join(plant, "planted.txt")
    open(f, "w").write("x")
    p1 = census(plant)
    os.utime(f, (0, 0))
    p2 = census(plant)
    verdicts["census_sees_plant"] = (p1 != p2)

    # --- the guard, all three controls --------------------------------------
    b = parse_boundary(case)
    patches = sorted(b)
    expected = sum(n for n, _ in b.values())

    before = census(case)
    foam = stage_readonly(case, stage)

    measured, per = rendered_face_count(foam, patches)
    verdicts["guard_passes_on_true_render"] = assert_surface_is_the_mesh(
        expected, measured, per, "positive control")

    verdicts["guard_refuses_wrong_case"] = not assert_surface_is_the_mesh(
        expected + 1, measured, per, "WRONG-CASE control (expected+1)")

    # PER-PATCH IDENTITY, driven both ways.
    verdicts["per_patch_identity_passes"] = assert_per_patch_identity(
        b, patches, per, "positive control")
    # COMPENSATING-ERROR control: swap two patches' counts.  The SUM is unchanged,
    # so the sum identity CANNOT see this -- that is exactly the gap the
    # per-patch identity closes, and it is DRIVEN rather than asserted.
    # THE PAIR MUST HAVE DIFFERENT COUNTS OR THE SWAP IS A NO-OP.
    # MEASURED 2026-09-11: taking patches[0], patches[1] on F25 picked inlet and
    # outlet, BOTH 4096 faces -- swapping equal counts changes nothing, so the
    # control tested nothing.  A control whose fixture makes it a no-op is the
    # same defect as vtkDecimatePro silently passing quads through.  The pair is
    # now SEARCHED FOR and the search failing is a FAIL, never a skip.
    pair = None
    for i in range(len(patches)):
        for j in range(i + 1, len(patches)):
            if per.get(patches[i]) != per.get(patches[j]):
                pair = (patches[i], patches[j])
                break
        if pair:
            break
    if pair:
        p0, p1 = pair
        swapped = dict(per)
        swapped[p0], swapped[p1] = per[p1], per[p0]
        verdicts["sum_is_blind_to_swap"] = (
            sum(swapped.values()) == sum(per.values()))
        verdicts["per_patch_refuses_swap"] = not assert_per_patch_identity(
            b, patches, swapped, "SWAP control (%s<->%s, %d<->%d)"
            % (p0, p1, per[p0], per[p1]))
    else:
        verdicts["sum_is_blind_to_swap"] = False
        verdicts["per_patch_refuses_swap"] = False
        print("  NO PATCH PAIR WITH DIFFERING COUNTS -- the swap control could not "
              "be driven, so these verdicts are FAIL, not skipped.")

    dmeasured, dper = rendered_face_count(foam, patches, decimate=True)
    # The control must actually BE a control: if decimation did not change the
    # count, the "refusal" below would be testing nothing.  Twice on 2026-09-11
    # it did not (a no-op filter, then an arithmetic coincidence), so this is
    # asserted rather than trusted.
    verdicts["decimation_control_is_a_control"] = (dmeasured != measured)
    verdicts["guard_refuses_decimated"] = not assert_surface_is_the_mesh(
        expected, dmeasured, dper, "DECIMATED control")

    after = census(case)
    verdicts["graded_tree_untouched"] = (before == after)

    # DIMENSIONALITY GUARD, driven both ways.  Positive: this case must pass.
    # Negative: a REAL wedge case must be REFUSED -- described is not driven.
    ok_pos, d_pos = assert_three_dimensional(case)
    verdicts["dim_guard_passes_on_3d"] = ok_pos
    wedge = os.environ.get(
        "RENDER3D_WEDGE_FIXTURE",
        "verification/runs/navier_class/SUP_BOOSTER/graded_e2/fine")
    if os.path.isfile(os.path.join(wedge, "constant", "polyMesh", "boundary")):
        ok_neg, d_neg = assert_three_dimensional(wedge)
        verdicts["dim_guard_refuses_wedge"] = (not ok_neg)
        print("  wedge fixture %s -> %s" % (wedge, d_neg))
    else:
        verdicts["dim_guard_refuses_wedge"] = False
        print("  WEDGE FIXTURE ABSENT at %s -- the negative control could not be "
              "driven, so this verdict is FAIL, not skipped." % wedge)

    print("\n=== SELFTEST VERDICTS ===")
    for k, v in verdicts.items():
        print("  %-34s %s" % (k, "PASS" if v else "FAIL"))
    print("  expected faces = %d   rendered = %d   decimated = %d"
          % (expected, measured, dmeasured))
    print("  census before = %s\n  census after  = %s" % (before, after))
    if not all(verdicts.values()):
        sys.stderr.write("\nREFUSED: selftest did not produce every required verdict.\n")
        return 2
    print("\nSELFTEST OK: the guard was shown able to PASS and to REFUSE, the census "
          "was shown deterministic and able to see a plant, and the graded tree was "
          "proven untouched.")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(
        description="3-D surface/patch render of a solved OpenFOAM case, guarded.")
    ap.add_argument("--case", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--patches", default=None,
                    help="Comma-separated patches to render. Default: every wall patch; "
                         "if none is typed 'wall', every patch.")
    ap.add_argument("--time", default="latest")
    ap.add_argument("--clip", default=None,
                    help="Optional clip as 'ox,oy,oz,nx,ny,nz' (origin + normal).")
    ap.add_argument("--field", default=None, help="Cell/point field to colour by.")
    ap.add_argument("--up", default="y", choices=("x", "y", "z"),
                    help="Which axis is 'up' for this case. OpenFOAM cases do not "
                         "agree: F25/PRD/MRF are y-up, DrivAer is z-up (automotive "
                         "convention). A generic camera CANNOT know, and guessing "
                         "renders a car upside down -- measured 2026-09-11.")
    ap.add_argument("--resolution", default="1920x1080")
    ap.add_argument("--min-ink", type=float, default=0.002)
    ap.add_argument("--prefix", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv[1:])

    if any("force-offscreen" in x for x in argv):
        sys.stderr.write("REFUSED: --force-offscreen-rendering aborts on this "
                         "X11/GLX-only ParaView 5.11.2 build (L-545).\n")
        return 2

    case = os.path.abspath(a.case)
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)

    if a.selftest:
        return do_selftest(case, out)

    ok, detail = assert_three_dimensional(case)
    if not ok:
        sys.stderr.write("REFUSED: %s\n  This renderer is for 3-D cases. A wedge "
                         "or 2-D case must never be presented as 3-D geometry.\n"
                         % detail)
        return 2
    print("dimensionality: %s" % detail)

    b = parse_boundary(case)
    if a.patches:
        patches = [p.strip() for p in a.patches.split(",") if p.strip()]
        missing = [p for p in patches if p not in b]
        if missing:
            sys.stderr.write("REFUSED: patches not in the case's boundary file: %s\n"
                             % missing)
            return 2
    else:
        walls = [k for k, (n, t) in b.items() if t == "wall"]
        patches = sorted(walls) if walls else sorted(b)

    expected = sum(b[p][0] for p in patches)
    before = census(case)
    stage = os.path.join(out, "_stage")
    foam = stage_readonly(case, stage)

    measured, per = rendered_face_count(foam, patches)
    if not assert_surface_is_the_mesh(expected, measured, per, "render"):
        return 2
    if not assert_per_patch_identity(b, patches, per, "render"):
        return 2

    from paraview.simple import (OpenFOAMReader, CreateRenderView, Show, Render,
                                 SaveScreenshot, Clip, ExtractSurface)
    view = CreateRenderView()
    w, h = (int(x) for x in a.resolution.lower().split("x"))
    view.ViewSize = [w, h]
    view.Background = [0.07, 0.07, 0.09]

    reader = OpenFOAMReader(FileName=foam)
    reader.MeshRegions = ["patch/" + p for p in patches]
    reader.UpdatePipeline()
    src = reader
    if a.clip:
        v = [float(x) for x in a.clip.split(",")]
        c = Clip(Input=ExtractSurface(Input=reader))
        c.ClipType.Origin = v[0:3]
        c.ClipType.Normal = v[3:6]
        c.UpdatePipeline()
        src = c

    d = Show(src, view)
    # Sanaa's directive asks for the MESH, not a silhouette: a flat-shaded solid
    # is a picture of the body, not of the grid.  'Surface With Edges' draws the
    # actual face edges, so what is on screen is the discretisation.
    d.Representation = "Surface With Edges"
    d.EdgeColor = [0.0, 0.0, 0.0]
    d.LineWidth = 0.5
    if a.field:
        from paraview.simple import ColorBy
        ColorBy(d, ("POINTS", a.field))
        d.RescaleTransferFunctionToDataRange(True)
    # Isometric three-quarter view, then fit.  A long thin body viewed down a
    # principal axis fills a sliver of the frame and its grid reads as moire;
    # an oblique view uses the diagonal.  Camera only -- no data is touched.
    view.ResetCamera()
    fp = list(view.CameraFocalPoint)
    import math
    diag = max(view.CameraPosition[i] - fp[i] for i in range(3)) or 1.0
    r = abs(diag) * 1.8
    up = {"x": [1.0, 0.0, 0.0], "y": [0.0, 1.0, 0.0], "z": [0.0, 0.0, 1.0]}[a.up]
    off = {"x": [0.55, 0.9, 0.75], "y": [0.75, 0.55, 0.9],
           "z": [0.75, 0.9, 0.55]}[a.up]
    view.CameraPosition = [fp[i] + r * off[i] for i in range(3)]
    view.CameraViewUp = up
    Render()

    prefix = a.prefix or os.path.basename(case.rstrip("/"))
    img = os.path.join(out, "%s_surface.png" % prefix)
    SaveScreenshot(img, view, ImageResolution=[w, h], TransparentBackground=0)

    # === RULE 3, AND THIS WAS A DEFECT IN THIS FILE ===
    # --min-ink was DECLARED AS AN ARGUMENT AND NEVER READ: a guard that exists
    # only in the help text.  That is the same class of defect this tool was
    # written to catch, found in the tool itself on its first real render.
    # A renderer that sees nothing produces a uniform background, and a uniform
    # background is a zero.  The image is read BACK OFF DISK and its non-background
    # fraction measured; below --min-ink it is REFUSED, not shipped.
    ink = measure_ink(img)
    if ink < a.min_ink:
        sys.stderr.write("REFUSED: rendered image ink fraction %.6f is below "
                         "--min-ink %.6f -- the picture is effectively blank.\n"
                         % (ink, a.min_ink))
        return 2

    after = census(case)
    if before != after:
        sys.stderr.write("REFUSED: the graded tree at %s CHANGED during rendering. "
                         "census %s -> %s\n" % (case, before, after))
        return 2

    side = {
        "tool": os.path.basename(__file__),
        "case": case,
        "patches": patches,
        "expected_faces_from_boundary": expected,
        "rendered_faces_measured": measured,
        "per_patch": per,
        "guard": "rendered surface cells == sum(nFaces) over rendered patches; "
                 "equality MEASURED, not assumed",
        "graded_tree_census_before": before,
        "graded_tree_census_after": after,
        "graded_tree_untouched": True,
        "image": img,
        "utc": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with open(os.path.join(out, "%s_surface.json" % prefix), "w") as fh:
        json.dump(side, fh, indent=2)
    shutil.rmtree(stage, ignore_errors=True)   # the stage is scratch, not output
    print("WROTE %s  (%d faces, ink %.4f, guard PASS, graded tree untouched)"
          % (img, measured, ink))
    if measured > 200000:
        print("NOTE: %d faces at this resolution puts cells near or below one "
              "pixel, so 'Surface With Edges' saturates and the grid reads as "
              "moire. That is a LEGIBILITY limit of a full-body view, not a "
              "defect -- use --clip or a coarser level for a legible mesh "
              "picture. The guard proves the RIGHT mesh was drawn; it cannot "
              "prove the picture is READABLE." % measured)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
