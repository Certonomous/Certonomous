#!/usr/bin/env pvbatch
"""Drive Act A's render machinery to REFUSE, and prove it can still render.

    xvfb-run -a pvbatch selftest_render_actA.py

WHY BOTH ARMS, AND WHY THAT IS THE WHOLE POINT
-----------------------------------------------
A render script that silently produces an empty, stale or wrong-mesh image is
the visual form of a false zero, and the demo is the one place where a
plausible-looking wrong picture costs most. So every guard is driven with an
input it must reject.

But a suite of refusals proves nothing on its own. A module that refused
EVERYTHING would pass a refusal-only sweep perfectly while being incapable of
drawing anything at all -- and this lab has just recorded that exact failure in
a different form: a check that reported "no such directory" for three
directories that were present, because it had guessed their names and then
confirmed its own guess rather than the disk (`ACT_A_GUI_CONTENT_SPEC.md`
section 9.7a). A negative is two claims -- about the world, and that the query
could have seen the world.

So this file carries a POSITIVE arm too: it renders a real image from the real
graded case and asserts the image is non-trivial. A refusal is only evidence
when the thing refusing is otherwise able to say yes.

Exit 0 = every guard fired on its own bad input AND the renderer produced a
real picture. Exit 2 = a guard was asleep, or the renderer cannot draw.
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _actA_render_common as C                                   # noqa: E402

FAILURES: list[str] = []
CHECKS = 0


def expect_refusal(label: str, fn) -> None:
    """The guard must refuse. Anything else is the guard being asleep."""
    global CHECKS
    CHECKS += 1
    try:
        fn()
    except C.RenderRefusal as exc:
        C.announce_line(f"  refused  {label}\n             -> {str(exc)[:110]}")
        return
    except Exception as exc:                                     # noqa: BLE001
        FAILURES.append(f"{label}: raised {type(exc).__name__} instead of a "
                        f"refusal ({str(exc)[:80]})")
        C.announce_line(f"  WRONG    {label}: {type(exc).__name__}, not a refusal")
        return
    FAILURES.append(f"{label}: DID NOT REFUSE")
    C.announce_line(f"  ASLEEP   {label}: did not refuse")


def expect_success(label: str, fn):
    global CHECKS
    CHECKS += 1
    try:
        value = fn()
    except Exception as exc:                                     # noqa: BLE001
        FAILURES.append(f"{label}: {type(exc).__name__}: {str(exc)[:110]}")
        C.announce_line(f"  FAILED   {label}: {type(exc).__name__}: {str(exc)[:80]}")
        return None
    C.announce_line(f"  ok       {label}")
    return value


# ---------------------------------------------------------------------------
# NEGATIVE ARM -- every guard, driven with the input it exists to reject
# ---------------------------------------------------------------------------

def negative_arm() -> None:
    C.announce_line("\nNEGATIVE ARM -- each guard must refuse its own bad input")

    expect_refusal(
        "a case directory that does not exist",
        lambda: C.materialise_region("/nonexistent/case/T23_NOPE", "fluid"))

    expect_refusal(
        "a region this case does not have",
        lambda: C.materialise_region(C.PRIMARY, "stator"))

    expect_refusal(
        "a time directory the case never wrote",
        lambda: C.materialise_region(C.PRIMARY, "fluid", time_dir="999999"))

    expect_refusal(
        "a field the region does not carry (U in the solid core)",
        lambda: C.open_region(C.PRIMARY, "core", ["U"]))

    expect_refusal(
        "a colour range that is not in the record",
        lambda: C.colour_range_degC("flywheel"))

    # THE WRONG-MESH GUARD, driven with the exact bug it was written for: a
    # .foam beside the case reads the pre-split 39,680-cell combined mesh and
    # renders a plausible picture of the wrong thing.
    def naive_scratch():
        from paraview.simple import OpenFOAMReader, UpdatePipeline
        root = tempfile.mkdtemp(prefix="actA_naive_")
        try:
            for name in ("constant", "system", C.END_TIME):
                os.symlink(os.path.join(C.PRIMARY, name),
                           os.path.join(root, name))
            foam = os.path.join(root, "naive.foam")
            with open(foam, "w", encoding="utf-8"):
                pass
            reader = OpenFOAMReader(FileName=foam)
            reader.MeshRegions = ["internalMesh"]
            reader.CellArrays = ["T"]
            UpdatePipeline(time=float(C.END_TIME), proxy=reader)
            got = reader.GetDataInformation().GetNumberOfCells()
            want = C.expected_cells("fluid")
            if got != want:
                C.refuse(f"the naive layout loaded {got:,} cells where the "
                         f"fluid region has {want:,} -- this is the combined "
                         f"pre-split mesh, not the region's own")
        finally:
            shutil.rmtree(root, ignore_errors=True)

    # NOTE ON WHAT THE ABOVE IS AND IS NOT. It DEMONSTRATES the bug -- the naive
    # layout really does hand back 39,680 cells -- but it calls `refuse` itself,
    # so it exercises its own arithmetic rather than the guard inside
    # `open_region`. A mutation run proved that: disabling the real guard left
    # this check passing. A control derived from the thing it controls is not a
    # control, so it is labelled a demonstration and the REAL guard is driven
    # separately, below.
    expect_refusal("DEMONSTRATION: the naive .foam layout loads the combined mesh",
                   naive_scratch)

    # THE REAL CELL-COUNT GUARD, driven through open_region itself by making the
    # recorded expectation disagree with the mesh on disk. Disabling the guard
    # makes this check fail, which is the property the demonstration above
    # lacked.
    def wrong_expected_count():
        original = C.expected_cells
        C.expected_cells = lambda region: 12345          # noqa: E731
        try:
            reader, root, _n = C.open_region(C.PRIMARY, "fluid", ["T"])
            shutil.rmtree(root, ignore_errors=True)
        finally:
            C.expected_cells = original

    expect_refusal("open_region's own cell-count guard (recorded count disagrees)",
                   wrong_expected_count)

    expect_refusal(
        "an image that was never written",
        lambda: C.verify_written_image(
            os.path.join(tempfile.gettempdir(), "actA_selftest_absent.png")))

    def tiny_image():
        path = os.path.join(tempfile.gettempdir(), "actA_selftest_tiny.png")
        with open(path, "wb") as fh:
            fh.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 64)
        try:
            C.verify_written_image(path)
        finally:
            os.remove(path)

    expect_refusal("an image too small to be a real picture", tiny_image)

    expect_refusal(
        "a render asked for with no view to draw into",
        lambda: C.save_screenshot(
            None, os.path.join(tempfile.gettempdir(), "actA_selftest_noview.png")))

    # The run-tree guard must notice a change.
    def moved_tree():
        before = C.run_tree_fingerprint(C.PRIMARY)
        tampered = set(before)
        tampered.add(("a_file_that_appeared", 1, 1))
        C.assert_run_tree_untouched(C.PRIMARY, tampered)

    expect_refusal("a graded run tree that changed under the render", moved_tree)

    # THE DROPPED-GLYPH GUARD. `|` is printable ASCII, so an ASCII or
    # printable-character check would pass it -- and it renders as NOTHING,
    # producing a caption whose fields run together on screen while the source
    # string is perfectly correct.
    expect_refusal(
        "a caption using a glyph the font silently drops ('|')",
        lambda: C.assert_caption_renderable("L = 0.750 m | duct r = 0.125 m"))

    expect_refusal(
        "a caption using a glyph never measured to render (degree sign)",
        lambda: C.assert_caption_renderable("T = 25 \u00b0C"))

    # THE RETIRED BODY. This is the guard that matters most on Screen 1: the
    # retired surface renders perfectly well and nothing about the picture says
    # which body it is. It must refuse by IDENTITY, before anything is drawn.
    import render_actA_geometry as G

    retired = os.path.join(C.REPO, "sdk", "geometry", "motor_in_duct.stl")
    if os.path.isfile(retired):
        expect_refusal(
            "the RETIRED body offered as the geometry to draw",
            lambda: G.assert_is_the_solved_surface(retired))
    else:
        C.announce_line("  skipped  the retired body is no longer on disk (it was "
              "quarantined); nothing to drive this guard with")

    expect_refusal(
        "a file that is not a binary STL, offered to the part slicer",
        lambda: C.split_parts(os.path.join(C.REPO, "docs", "campaigns",
                                           "T-family", "demo",
                                           "render_actA_paraview",
                                           "README.md")))


# ---------------------------------------------------------------------------
# POSITIVE ARM -- the module must still be able to say yes
# ---------------------------------------------------------------------------

def positive_arm() -> None:
    C.announce_line("\nPOSITIVE ARM -- the same module must still produce a real picture")

    expect_success("ParaView version is the pinned one",
                   C.assert_paraview_version)

    def solved_surface_accepted():
        import render_actA_geometry as G
        return G.assert_is_the_solved_surface(C.SOLVED_STL)[:16]

    expect_success("the SOLVED surface is accepted by the same guard",
                   solved_surface_accepted)

    def live_captions_render():
        live = [C.AXISYMMETRY_PLANE_LINE, C.AXISYMMETRY_REVOLVE_LINE,
                "L = 0.750 m ; heated housing 0.125 m (orange) ; "
                "duct r = 0.125 m, opacity 0.22",
                "20 mm window at r = 37.5 mm ; y+ = 0.73-0.75 on the heated "
                "housing",
                "U_inf = 10 m/s ; P = 305 W",
                "4 frames ; one scale 14.8-107.7 degC"]
        for text in live:
            C.assert_caption_renderable(text)
        return len(live)

    expect_success("every live caption clears the glyph guard",
                   live_captions_render)

    def parts_split():
        parts, root = C.split_parts(C.SOLVED_STL)
        try:
            sizes = {k: os.path.getsize(v) for k, v in parts.items()}
        finally:
            shutil.rmtree(root, ignore_errors=True)
        if len(sizes) != 3 or any(v < 200 for v in sizes.values()):
            raise AssertionError(f"part slices look wrong: {sizes}")
        return sizes

    expect_success("the surface splits into duct, motor and heated housing",
                   parts_split)

    for region, want in (("fluid", 35200), ("housing", 1120), ("core", 3360)):
        def load(region=region, want=want):
            reader, root, n = C.open_region(C.PRIMARY, region, ["T"])
            shutil.rmtree(root, ignore_errors=True)
            if n != want:
                raise AssertionError(f"{region} loaded {n}, expected {want}")
            return n
        expect_success(f"{region} loads its own mesh ({want:,} cells)", load)

    # And an actual render, asserted non-trivial. Without this, every refusal
    # above would be consistent with a module that cannot draw at all.
    def render_and_measure():
        from paraview.simple import (ColorBy, CreateRenderView, GetColorTransferFunction,
                                     Show)

        view = CreateRenderView()
        view.ViewSize = [800, 450]
        view.OrientationAxesVisibility = 0
        C.white_background(view)

        roots, converted = [], []
        try:
            for region in C.REGIONS:
                reader, root, _n = C.open_region(C.PRIMARY, region, ["T"])
                roots.append(root)
                celsius = C.to_celsius(reader, "T")
                celsius.UpdatePipeline(float(C.END_TIME))
                converted.append(celsius)
                disp = Show(celsius, view)
                ColorBy(disp, ("CELLS", "T_degC"))
            lo, hi = C.field_range_degC(converted)
            GetColorTransferFunction("T_degC").RescaleTransferFunction(lo, hi)
            C.frame_axial_plane(view)
            C.caption(view, C.AXISYMMETRY_PLANE_LINE)

            out = os.path.join(tempfile.gettempdir(), "actA_selftest_render.png")
            n_bytes = C.save_screenshot(view, out, size=(800, 450))

            # Non-trivial: a real field render is not one flat colour.
            from PIL import Image
            with Image.open(out) as im:
                colours = im.convert("RGB").getcolors(maxcolors=1 << 20)
            distinct = len(colours or [])
            os.remove(out)
            if distinct < 50:
                raise AssertionError(
                    f"the render carries only {distinct} distinct colours, "
                    f"which is a blank or flat frame, not a field")
            return n_bytes, distinct, lo, hi

        finally:
            for root in roots:
                shutil.rmtree(root, ignore_errors=True)

    result = expect_success(
        "a real three-region render, non-blank and non-flat", render_and_measure)
    if result:
        n_bytes, distinct, lo, hi = result
        C.announce_line(f"             -> {n_bytes:,} bytes, {distinct:,} distinct "
              f"colours, {lo:.1f} to {hi:.1f} degC")


def main() -> int:
    C.announce_line("Act A ParaView render machinery -- refusal and capability self-test")
    negative_arm()
    positive_arm()

    C.announce_line(f"\n{CHECKS} checks run")
    if FAILURES:
        C.announce_err_line(f"\nREFUSE: {len(FAILURES)} check(s) failed:\n")
        for line in FAILURES:
            C.announce_err_line(f"  {line}\n")
        return 2
    C.announce_line("PASS -- every guard fired on its own bad input, and the same "
          "machinery still rendered a real picture")
    return 0


if __name__ == "__main__":
    rc = main()
    sys.stdout.flush()
    sys.stderr.flush()
    # DELIBERATE, AND NOT A WAY OF HIDING A FAILURE. ParaView 5.11.2 under
    # xvfb tears its GLX context down after the interpreter is finished and
    # the process dies with GLXBadContext or SIGSEGV -- AFTER every check has
    # run and the verdict is printed. Left alone it overwrites this script's
    # own exit code, so a caller checking `rc` would read a clean PASS as a
    # failure and, worse, could read a real FAILURE as some other number.
    # `rc` here is the verdict computed above and nothing else; the teardown
    # is infrastructure and does not get a vote on the result.
    os._exit(rc)
