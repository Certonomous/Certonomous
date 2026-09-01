"""Shared machinery for Act A's ParaView renders. REFUSES rather than renders.

WHY THIS FILE EXISTS AT ALL
---------------------------
Under SANAA-DIRECT 2026-09-01 ~21:10Z every act's geometry, mesh and field
visuals are ParaView-rendered from the real case files and the in-browser canvas
is retired as a visual source. This module is the part every Act A render script
shares: it materialises a read-only view of a graded run, proves the thing it
loaded is the thing it meant to load, and refuses when it cannot.

THE THREE REFUSALS THAT ARE THE POINT OF THIS MODULE
----------------------------------------------------
1. **NOTHING IS EVER WRITTEN INTO A GRADED RUN TREE.** Not a ``.foam`` file, not
   a symlink, not a temp file, not a ``touch``. These cases are under the strict
   completion rule and its age guard, whose whole content is that every field at
   ``endTime`` is newer than the case's own ``0/T``. A render tool dropping a
   file into the case directory invites precisely the "is this still the artefact
   that ran" question the guard exists to answer, and the answer would then be
   "we cannot tell". :func:`materialise_region` builds a SCRATCH case of symlinks
   and puts the ``.foam`` there; :func:`assert_run_tree_untouched` proves
   afterwards that the case directory did not move.

2. **THE MESH MUST BE THE REGION'S MESH, AND THAT IS MEASURED.** This is not
   defensive padding — it is a bug that was caught in this case, on this box.
   A ``.foam`` placed beside the case's own ``constant/`` reads the TOP-LEVEL
   ``constant/polyMesh``, which is the pre-split 39,680-cell mesh of all three
   regions combined, and then offers the fluid field names beside it. It renders.
   It looks entirely plausible. It is the wrong mesh.
   So every reader asserts its cell count against the count recorded in
   ``T23_T24_MESH_FACTS.json`` for that region, and refuses on mismatch. The
   per-region scratch layout below is what makes the counts come out right:
   35,200 fluid, 1,120 housing, 3,360 core.

3. **A RENDER THAT SILENTLY PRODUCES AN EMPTY OR STALE IMAGE IS A FALSE ZERO.**
   Every write goes through :func:`save_screenshot`, which refuses a file that
   does not appear, is suspiciously small, or is a leftover from a previous run.

AND THE DECLARATION THAT IS NOT OPTIONAL
-----------------------------------------
The solve is ONE CELL over a five-degree wedge. A render that rotationally
extrudes it into a full 360-degree body is showing geometry that was never
solved — the same class of defect as the retired surface this act used to serve.
:data:`AXISYMMETRY_REVOLVE_LINE` is stamped on every render of an
extruded body, and :data:`AXISYMMETRY_PLANE_LINE` on every render of the solved
plane. The declaration must describe the picture actually drawn.
Extrusion is permitted; SILENT extrusion is not.

Nothing here chooses a number. Colour ranges, cell counts and temperatures are
read from the artifacts the heat-transfer family already wrote.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile

# ParaView 5.11.2, pinned. A render that moves with the reader version is not
# reproducible, and the version is asserted rather than hoped for.
REQUIRED_PARAVIEW = "5.11"

# render_actA_paraview -> demo -> T-family -> campaigns -> docs -> repo root
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                    "..", "..", "..", "..", ".."))
T23_RUNS = os.path.join(REPO, "verification", "runs", "T-family", "T23_runs")
T24_RUNS = os.path.join(REPO, "verification", "runs", "T-family", "T24_runs")
MESH_FACTS = os.path.join(T23_RUNS, "T23_T24_MESH_FACTS.json")
SCREEN_DATA = os.path.join(REPO, "docs", "campaigns", "T-family", "demo",
                           "figures_actA", "actA_screen_data.json")
DISPLAY_SURFACE = os.path.join(T23_RUNS, "display_surface")
PARTS_MANIFEST = os.path.join(DISPLAY_SURFACE, "t23_solved_geometry_parts.json")

#: The copy the control-room server actually reads, and therefore the one a
#: render must draw. NOT the generator's copy: naming that one would let a
#: regenerated surface be rendered while the screen served a stale body.
SOLVED_STL = os.path.join(REPO, "sdk", "geometry", "t23_solved_geometry.stl")

#: The generator's own copy, beside the solved case. Used ONLY as the identity
#: reference the served copy is hashed against.
GENERATED_STL_FOR_CHECK = os.path.join(DISPLAY_SURFACE,
                                       "t23_solved_geometry.stl")

#: The point Act A's record is written against.
PRIMARY = os.path.join(T23_RUNS, "T23_P305_U20")
#: The converged time directory these renders read.
END_TIME = "10000"

REGIONS = ("fluid", "housing", "core")

#: THE DECLARATION MUST MATCH WHAT IS ACTUALLY DRAWN, so there are two of them.
#: Stamping the revolve sentence on a plane view would be false in the opposite
#: direction -- claiming a display choice that was not made -- and a caption that
#: does not describe its own picture is the defect this pair exists to prevent.
#:
#: Sanaa's never-list bans narration about the lab's current state; both lines
#: are PHYSICS facts about the geometry, which her rule preserves and phrases as
#: fact rather than apology.

#: For a view of the solved plane through the axis. No extrusion, nothing added.
AXISYMMETRY_PLANE_LINE = ("The motor is axisymmetric. This is the plane through "
                          "its axis, as solved.")

#: For a view of the body revolved for legibility. Permitted, never silent.
AXISYMMETRY_REVOLVE_LINE = ("The motor is axisymmetric. It was solved on a "
                            "five-degree wedge and the body shown here is a "
                            "revolve of it.")

#: Axial extent of the solved domain, z0..z3, from the parts manifest.
#: Read rather than typed by :func:`axis_extent`.
AXIS_KEY = "axial_stations_Z0_Z3"

#: Absolute zero in Celsius, for the K -> degC conversion. The fields on disk
#: are in kelvin; every Act A screen is in Celsius.
KELVIN_OFFSET = 273.15

MIN_IMAGE_BYTES = 5000


class RenderRefusal(RuntimeError):
    """Raised instead of producing a picture nobody can defend."""


def refuse(message: str):
    raise RenderRefusal(message)


# ---------------------------------------------------------------------------
# Recorded facts. No defaults: a missing key refuses where it is asked for.
# ---------------------------------------------------------------------------

def _load(path: str, what: str) -> dict:
    if not os.path.isfile(path):
        refuse(f"the {what} is not on disk at {path}, so this render has no "
               f"facts behind it and will not invent any")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def mesh_facts() -> dict:
    return _load(MESH_FACTS, "mesh record")


def screen_data() -> dict:
    return _load(SCREEN_DATA, "Act A screen record")


def expected_cells(region: str) -> int:
    """The region's cell count, READ from the mesh record.

    This is the number the cell-count guard compares against, and it is the
    whole defence against the wrong-mesh bug described in this module's
    docstring.
    """
    facts = mesh_facts()
    by_region = facts.get("cells")
    if not isinstance(by_region, dict) or region not in by_region:
        refuse(f"the mesh record carries no cell count for the {region} region, "
               f"so a render of it cannot be checked against anything")
    return int(by_region[region])


def colour_range_degC(which: str) -> tuple[float, float]:
    """``(minimum, maximum)`` in Celsius, READ, never chosen per render.

    ``which`` is ``"core"`` or ``"housing"``. The four airspeed renders must
    share one range or the comparison between them means nothing.
    """
    key = {"core": "map_colour_range_degC",
           "housing": "map_colour_range_housing_degC"}.get(which)
    if key is None:
        refuse(f"no recorded colour range is named {which!r}")
    block = screen_data().get(key)
    if not isinstance(block, dict) or "minimum" not in block or "maximum" not in block:
        refuse(f"the screen record carries no colour range under {key}, so this "
               f"render will not pick one of its own")
    return float(block["minimum"]), float(block["maximum"])


# ---------------------------------------------------------------------------
# The read-only scratch case
# ---------------------------------------------------------------------------

def _tree_fingerprint(root: str) -> set:
    """Names, sizes and mtimes under a directory, one level of entries deep.

    Used to prove the graded run tree did not move while we read it.
    """
    out = set()
    for entry in sorted(os.listdir(root)):
        path = os.path.join(root, entry)
        try:
            st = os.lstat(path)
        except OSError:
            continue
        out.add((entry, st.st_size, int(st.st_mtime)))
    return out


def materialise_region(case_dir: str, region: str, time_dir: str = END_TIME):
    """A scratch case for ONE region, built entirely of symlinks.

    Returns ``(scratch_root, foam_file)``. The caller removes ``scratch_root``.

    THE LAYOUT IS THE FIX. ParaView's reader wants ``constant/polyMesh`` and
    time directories holding fields. A ``.foam`` beside the real case gives it
    the pre-split combined mesh; this layout gives it the region's own mesh and
    the region's own fields, and the cell-count guard proves which one arrived.

    NOTHING IS WRITTEN INSIDE ``case_dir``. Every path below is created under a
    fresh temporary directory.
    """
    if region not in REGIONS:
        refuse(f"{region!r} is not one of this case's regions {REGIONS}")
    if not os.path.isdir(case_dir):
        refuse(f"the case directory {case_dir} is not on disk")

    mesh_src = os.path.join(case_dir, "constant", region, "polyMesh")
    fields_src = os.path.join(case_dir, time_dir, region)
    system_src = os.path.join(case_dir, "system")
    for path, what in ((mesh_src, f"the {region} mesh"),
                       (fields_src, f"the {region} fields at t = {time_dir}"),
                       (system_src, "the case dictionaries")):
        if not os.path.isdir(path):
            refuse(f"{what} is not on disk at {path}; this render will not "
                   f"substitute another region's data for it")

    root = tempfile.mkdtemp(prefix=f"actA_render_{region}_")
    os.makedirs(os.path.join(root, "constant"))
    os.makedirs(os.path.join(root, time_dir))
    os.symlink(mesh_src, os.path.join(root, "constant", "polyMesh"))
    os.symlink(system_src, os.path.join(root, "system"))
    for name in sorted(os.listdir(fields_src)):
        os.symlink(os.path.join(fields_src, name),
                   os.path.join(root, time_dir, name))

    foam = os.path.join(root, f"{region}.foam")
    with open(foam, "w", encoding="utf-8"):
        pass
    return root, foam


def assert_run_tree_untouched(case_dir: str, before: set) -> None:
    """Prove the graded case did not move while we rendered from it."""
    after = _tree_fingerprint(case_dir)
    if after != before:
        added = after - before
        removed = before - after
        refuse(f"the graded run tree at {case_dir} CHANGED during rendering "
               f"(added {sorted(added)[:3]}, removed {sorted(removed)[:3]}). A "
               f"render must never write into a case under the completion rule")


def run_tree_fingerprint(case_dir: str) -> set:
    return _tree_fingerprint(case_dir)


# ---------------------------------------------------------------------------
# Reading, with the cell-count guard
# ---------------------------------------------------------------------------

def open_region(case_dir: str, region: str, arrays, time_dir: str = END_TIME):
    """Open one region and PROVE it is that region's mesh.

    Returns ``(reader, scratch_root, n_cells)``.
    """
    from paraview.simple import OpenFOAMReader, UpdatePipeline

    root, foam = materialise_region(case_dir, region, time_dir)
    reader = OpenFOAMReader(FileName=foam)
    reader.MeshRegions = ["internalMesh"]
    reader.CellArrays = list(arrays)
    UpdatePipeline(time=float(time_dir), proxy=reader)

    info = reader.GetDataInformation()
    n_cells = info.GetNumberOfCells()
    want = expected_cells(region)
    if n_cells != want:
        shutil.rmtree(root, ignore_errors=True)
        refuse(
            f"the {region} render loaded {n_cells:,} cells where the mesh "
            f"record says {want:,}. This is the wrong mesh -- a .foam file "
            f"placed beside the case reads the pre-split combined mesh of all "
            f"three regions and renders a plausible picture from it. Refusing "
            f"rather than showing it")

    for name in arrays:
        arr = info.GetCellDataInformation().GetArrayInformation(name)
        if arr is None:
            shutil.rmtree(root, ignore_errors=True)
            refuse(f"the {region} region carries no field {name!r} at "
                   f"t = {time_dir}, so nothing will be painted with it")
    return reader, root, n_cells


def to_celsius(reader, field: str = "T"):
    """A Calculator converting kelvin on disk to the Celsius on every screen."""
    from paraview.simple import Calculator

    calc = Calculator(Input=reader)
    calc.AttributeType = "Cell Data"
    calc.ResultArrayName = f"{field}_degC"
    calc.Function = f"{field} - {KELVIN_OFFSET}"
    return calc


# ---------------------------------------------------------------------------
# Writing, with the empty/stale-image refusal
# ---------------------------------------------------------------------------

def field_range_degC(readers_celsius, array="T_degC") -> tuple[float, float]:
    """The Celsius range spanning EVERY reader passed in, measured from the data.

    WHY THIS EXISTS BESIDE :func:`colour_range_degC`. The recorded map ranges are
    the ranges of the SIXTEEN PEAK values -- ``map_colour_range_degC`` runs
    24.7 to 107.7 degC, which is the span of peak core temperature across the
    map. They are the right scale for the map figure and the WRONG scale for a
    field picture: the cooling air enters at about 15 degC, below that minimum,
    so painting a whole field on the map range clamps most of the domain to the
    bottom colour and renders a black body. That is what the first version of
    this renderer produced.

    So a field render measures its own range across every region and every case
    it is going to show, and every one of those renders then shares it. Passing
    the four airspeed cases together is what makes them honestly comparable;
    passing one case gives that case's own range. The range is MEASURED and
    reported, never typed.
    """
    lo = float("inf")
    hi = float("-inf")
    for reader in readers_celsius:
        info = reader.GetDataInformation().GetCellDataInformation()
        arr = info.GetArrayInformation(array)
        if arr is None:
            refuse(f"a reader in this set carries no {array!r}, so no shared "
                   f"colour range can be measured across the set")
        a, b = arr.GetComponentRange(0)
        lo = min(lo, float(a))
        hi = max(hi, float(b))
    if not (lo < hi):
        refuse(f"the measured {array} range came out as {lo}..{hi}, which is "
               f"not a range; nothing will be painted with it")
    return lo, hi


def geometry_m() -> dict:
    """The solved dimensions, from the parts manifest the generator wrote."""
    manifest = _load(PARTS_MANIFEST, "geometry parts manifest")
    block = manifest.get("geometry_m")
    if not isinstance(block, dict):
        refuse("the parts manifest carries no geometry_m block, so this render "
               "cannot frame the body against its solved dimensions")
    return block


def axis_extent() -> tuple[float, float, float]:
    """``(z_min, z_max, r_max)`` in metres, READ from the manifest.

    Used to frame the camera. Typing these would let a changed case leave a
    stale constant behind in a render script.
    """
    block = geometry_m()
    stations = block.get(AXIS_KEY)
    if not isinstance(stations, list) or len(stations) < 2:
        refuse(f"the parts manifest carries no {AXIS_KEY}, so the camera cannot "
               f"be framed on the solved extent")
    r_max = float(block.get("duct_inner_radius", 0.0))
    if r_max <= 0:
        refuse("the parts manifest carries no duct inner radius")
    return float(min(stations)), float(max(stations)), r_max


def frame_axial_plane(view, pad: float = 1.06) -> None:
    """Look square at the r-z plane, with parallel projection.

    The solve is one cell over a five-degree wedge about the z axis. Viewed in
    perspective from a default camera it is an edge-on sliver a few pixels wide
    -- which is what the first version of this renderer produced. Looking along
    -y at the x-z plane, in parallel projection, shows the field the way the
    case was actually solved.
    """
    z_lo, z_hi, r_max = axis_extent()
    z_mid = 0.5 * (z_lo + z_hi)
    r_mid = 0.5 * r_max

    # THE AXIS CONVENTION, MEASURED FROM THE MESH RATHER THAN ASSUMED.
    # The bounds of the three solved regions are:
    #     x  -0.0055 .. 0.0055   the five-degree WEDGE THICKNESS
    #     y   0.0060 .. 0.1249   the RADIUS
    #     z  -0.2500 .. 0.5000   the AXIS
    # so the solved plane is the y-z plane and it is viewed along x. An earlier
    # version of this function assumed radius on x and looked along -y, which
    # points straight THROUGH the radial direction and renders the wedge
    # edge-on as a hairline a few pixels tall. It produced a picture that was
    # not obviously broken at a glance, which is the dangerous kind.
    view.CameraParallelProjection = 1
    view.CameraPosition = [-1.0, r_mid, z_mid]
    view.CameraFocalPoint = [0.0, r_mid, z_mid]
    view.CameraViewUp = [0.0, 1.0, 0.0]      # radius up, axis across the frame

    # CameraParallelScale is the HALF-HEIGHT of the window in metres. The
    # vertical is the radius; the axial extent still has to fit across, so the
    # scale is whichever of the two demands more.
    width, height = view.ViewSize
    aspect = float(width) / float(height) if height else 1.0
    half_from_radius = 0.5 * r_max
    half_from_axis = 0.5 * (z_hi - z_lo) / aspect
    view.CameraParallelScale = max(half_from_radius, half_from_axis) * pad


def white_background(view) -> None:
    """A white ground, actually applied.

    ParaView 5.11 ignores ``view.Background`` while the colour palette owns the
    background, so setting Background alone leaves the default slate grey --
    which is exactly what the first version of this renderer shipped.
    """
    view.UseColorPaletteForBackground = 0
    view.Background = [1.0, 1.0, 1.0]
    view.Background2 = [1.0, 1.0, 1.0]


def caption(view, text: str, position=(0.02, 0.02), size=9):
    """One caption line burned into the render."""
    from paraview.simple import Show, Text

    src = Text(Text=text)
    disp = Show(src, view)
    disp.WindowLocation = "Any Location"
    disp.Position = list(position)
    disp.FontSize = size
    disp.Color = [0.15, 0.15, 0.15]
    return src


def verify_written_image(path: str) -> int:
    """REFUSE an image that is missing or too small to be a real picture.

    Split out from :func:`save_screenshot` so the guard itself can be driven
    directly by the self-test. Testing it through ``save_screenshot`` meant
    passing a broken view, and ParaView raised its own ``ValueError`` before
    this logic was ever reached -- so the check looked tested and was not. That
    is the self-test earning its place on its first run.
    """
    if not os.path.isfile(path):
        refuse(f"the render wrote no file at {path}")
    n = os.path.getsize(path)
    if n < MIN_IMAGE_BYTES:
        refuse(f"the render at {path} is {n} bytes, below the {MIN_IMAGE_BYTES} "
               f"a real image occupies; an all-blank frame will not be shown")
    return n


def save_screenshot(view, path: str, size=(1600, 900)) -> int:
    """Write a render and REFUSE an image that is empty, missing or stale.

    A render script that silently produces an empty or stale picture is the
    visual form of a false zero, and the demo is where a plausible-looking
    wrong picture costs most.
    """
    from paraview.simple import SaveScreenshot

    if view is None:
        refuse(f"no view was given to render {os.path.basename(path)} into, so "
               f"nothing would have been drawn")
    if os.path.exists(path):
        os.remove(path)          # never let a previous run's image stand in
    os.makedirs(os.path.dirname(path), exist_ok=True)
    SaveScreenshot(path, view, ImageResolution=list(size))
    return verify_written_image(path)


def assert_paraview_version() -> str:
    from paraview import simple

    version = simple.GetParaViewVersion()
    text = f"{version.major}.{version.minor}"
    if text != REQUIRED_PARAVIEW:
        refuse(f"these renders are pinned to ParaView {REQUIRED_PARAVIEW} and "
               f"this is {text}; a render that moves with the reader version "
               f"is not reproducible")
    return f"{text}.{version.build}" if hasattr(version, "build") else text


def announce(message: str) -> None:
    """Write a progress line straight to file descriptor 1.

    NOT ``print`` and NOT ``sys.stdout``, and the reason is a bug this module
    shipped and then caught:

    ``paraview.simple`` replaces ``sys.stdout`` with a wrapper that only reaches
    the real file descriptor at interpreter finalisation. The self-test and the
    renderers end in ``os._exit`` -- deliberately, so ParaView's GLX teardown
    crash cannot overwrite a computed verdict -- and ``os._exit`` skips
    finalisation. The two together SILENTLY DISCARDED EVERY PROGRESS LINE: the
    geometry renderer ran correctly end to end, wrote its image, and printed
    absolutely nothing, on both streams, while exiting 0.

    A run that does its work and reports nothing is indistinguishable from a run
    that did nothing, which is the same family as an empty image and a false
    zero. ``os.write`` bypasses both the wrapper and the buffering, so a line
    that was written is a line that appears.
    """
    os.write(1, (message + "\n").encode("utf-8", "replace"))


def announce_error(message: str) -> None:
    """The same, on file descriptor 2, for refusals."""
    os.write(2, (message + "\n").encode("utf-8", "replace"))


def part_ranges() -> dict:
    """``{part name: (first facet, last facet exclusive)}`` from the manifest.

    The STL's facets are ordered by part and the manifest records the ranges,
    so a part can be isolated without trusting the two-byte STL attribute that
    most readers discard.
    """
    manifest = _load(PARTS_MANIFEST, "geometry parts manifest")
    parts = manifest.get("parts")
    if not isinstance(parts, dict) or not parts:
        refuse("the parts manifest carries no part ranges, so the duct cannot "
               "be separated from the motor inside it")
    return {name: (int(lo), int(hi)) for name, (lo, hi) in parts.items()}


def split_parts(stl_path: str):
    """Write the duct, the motor body and the heated housing as three scratch
    STL files, and return ``({name: path}, scratch_dir)``.

    WHY BY BYTES AND NOT BY A FILTER. The obvious ParaView route --
    ``GenerateIds`` then ``Threshold`` on the cell id -- aborted the process
    with SIGABRT on 5.11.2 here. A binary STL is a fixed 84-byte header and
    then 50 bytes per facet, and the manifest records each part's facet range,
    so slicing the file is both simpler and immune to filter API drift between
    ParaView versions.

    NOTHING IS WRITTEN BESIDE THE SOURCE SURFACE. The slices land in a fresh
    temporary directory the caller removes.
    """
    ranges = part_ranges()
    for needed in ("duct", "housing_heated"):
        if needed not in ranges:
            refuse(f"the parts manifest names no {needed!r} range")

    raw = open(stl_path, "rb").read()
    if len(raw) < 84:
        refuse(f"{stl_path} is too short to be a binary STL")
    n_facets = int.from_bytes(raw[80:84], "little")
    expected = 84 + 50 * n_facets
    if len(raw) != expected:
        refuse(f"{stl_path} declares {n_facets} facets, which needs {expected} "
               f"bytes, but the file is {len(raw)}; it is not the binary STL "
               f"this slicer expects and will not be cut up blindly")

    def slice_out(lo, hi):
        lo, hi = int(lo), int(hi)
        if not (0 <= lo < hi <= n_facets):
            refuse(f"facet band {lo}..{hi} is outside the surface's "
                   f"{n_facets} facets")
        body = raw[84 + 50 * lo: 84 + 50 * hi]
        return (b"actA render slice".ljust(80, b"\0")
                + (hi - lo).to_bytes(4, "little") + body)

    heat_lo, heat_hi = ranges["housing_heated"]
    up = ranges.get("centrebody_upstream", (heat_lo, heat_lo))
    down = ranges.get("centrebody_downstream", (heat_hi, heat_hi))

    wanted = {
        "duct": ranges["duct"],
        "housing_heated": (heat_lo, heat_hi),
        "motor": (min(up[0], heat_lo), max(down[1], heat_hi)),
    }

    root = tempfile.mkdtemp(prefix="actA_parts_")
    out = {}
    for name, (lo, hi) in wanted.items():
        path = os.path.join(root, f"{name}.stl")
        with open(path, "wb") as fh:
            fh.write(slice_out(lo, hi))
        out[name] = path
    return out, root


def frame_isometric(view, pad: float = 1.25) -> None:
    """A three-quarter view of the whole body, fitted to it.

    The r-z parallel framing used by the field renders is right for a plane and
    wrong for a solid: it looks straight at the side of a cylinder and shows a
    rectangle.

    Two things here were got wrong first and are fixed deliberately:

    * **Radius is UP, so the axis lies ACROSS the frame.** With the axis up, a
      0.750 m body in a 16:9 frame runs off the top and bottom.
    * **The distance is FITTED, not computed by hand.** The first version put
      the camera at a hand-derived offset and the body overflowed the frame.
      Setting the direction and letting ``ResetCamera`` fit the visible bounds
      is what makes this robust to a changed geometry.
    """
    from paraview.simple import ResetCamera

    z_lo, z_hi, r_max = axis_extent()
    z_mid = 0.5 * (z_lo + z_hi)
    reach = max(z_hi - z_lo, 4.0 * r_max)

    view.CameraParallelProjection = 0
    view.CameraViewAngle = 30.0
    view.CameraFocalPoint = [0.0, 0.0, z_mid]
    # Mostly side-on (down -x), lifted and swung so the body reads as a solid
    # rather than a silhouette. Radius up puts the axis across the frame.
    view.CameraPosition = [-1.00 * reach, 0.42 * reach, z_mid - 0.55 * reach]
    view.CameraViewUp = [0.0, 1.0, 0.0]

    ResetCamera(view)                 # fit the data, keeping that direction
    # Ease off so the body does not touch the edges.
    focal = list(view.CameraFocalPoint)
    pos = list(view.CameraPosition)
    view.CameraPosition = [f + (p - f) * pad for f, p in zip(focal, pos)]


def announce_line(*parts) -> None:
    """``print``-alike that reaches fd 1 even after ``os._exit``.

    The self-test used the builtin ``print`` and, because ``paraview.simple``
    wraps ``sys.stdout`` and ``os._exit`` skips finalisation, it produced the
    correct exit code and NO REPORT AT ALL. A suite whose verdict text vanishes
    is the same failure as a render that writes a blank image.
    """
    announce(" ".join(str(p) for p in parts))


def announce_err_line(*parts) -> None:
    announce_error("".join(str(p) for p in parts).rstrip("\n"))
