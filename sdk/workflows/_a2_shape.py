"""The A2 wing's shape history, prepared for the control-room viewport.

This module is the act-time half of the shape replay. It reads the static
artifact ``A2_shape_frames.json`` that :mod:`scripts.build_a2_shape_frames`
baked offline and turns it into the viewport payloads the control room
already knows how to render. Outside the standard library it reaches for one
thing only, the surface reader that serves the viewport, and that is for
measuring a surface the control room took in. The act must run on a laptop
with no OpenFOAM, no DAFoam, no pyGeo and no network, so no part of the
deformation is recomputed here. Every surface it writes came out of the
optimizer's own parameterization, offline, once.

Nothing here scales, amplifies or smooths anything. Every surface that
reaches the screen is at TRUE SCALE, and every number on the legend is a true
millimetre. The shape change is made legible two ways, both of which are
honest because neither touches a coordinate: a displacement field painted on
the wing, and a second pass on the inboard 2.2 m of span with its own camera,
where the same true-scale change is framed about four times tighter.
"""
from __future__ import annotations

import json
import struct
from pathlib import Path
from typing import Any

# The one module that names this repository's tree (MOVE_MAP batch 3).
# Every name it exports is bound to a legacy/successor PAIR resolved
# against the filesystem at import, so the constants below are correct
# before the move, between batches and after it, with no edit here.
import sys as _sys  # noqa: E402
import pathlib as _pathlib  # noqa: E402
_LAB_PATHS_DIR = str(_pathlib.Path(__file__).resolve().parents[2]
                     / "scripts")
if _LAB_PATHS_DIR not in _sys.path:
    _sys.path.insert(0, _LAB_PATHS_DIR)
import lab_paths  # noqa: E402

_LADDER = lab_paths.DAFOAM / "ladder-a"
FRAMES_FILE = _LADDER / "A2_shape_frames.json"

# The baseline wing, written out as a surface anyone can upload. It exists so
# the wing that carries this act's numbers can be handed to the control room
# through the ordinary upload path, instead of the viewer having to take on
# faith that the surface on screen is the one the result belongs to.
BASELINE_STL = "mach_tutorial_wing.stl"
# `surfaces/` holds NO tracked file, so `git mv` never reaches it: it is
# one of the two HAND-CARRY trees (`scripts/hand_carry.py`, batch 7H).
# `lab_paths.SURFACES` is bound to where the 2.18 MB actually is.
BASELINE_STL_PATH = lab_paths.SURFACES / BASELINE_STL

# ITEM 5 (owner, 2026-07-31): ONE canonical reference for surface motion, so
# the act never puts three near-miss millimetre figures on screen and leaves a
# viewer to guess which one is the shape change. The reference is the FINAL
# surface measured against the baseline, unscaled, at the point that moved
# most, and it is that point's TOTAL motion. Every other millimetre figure the
# act shows (the fixed colour window, a frame's own legend extremes) is a
# figure about the pass rather than the shape change, and is labelled against
# this reference where it is shown.
#
# ITEM 2 (owner, 2026-07-31): the reference is unchanged, and it is now named
# for the quantity it is. The painted field is a different quantity, the
# outward normal COMPONENT of that motion averaged over each face, so its
# extremes are smaller and the legend says which is which.
DISP_REFERENCE = "final surface against baseline, unscaled"

# ITEM 2 (owner, 2026-07-31): the act says on screen that it is handing the
# received wing to a sub-agent to confirm, so a confirmation genuinely runs and
# genuinely reports back. It is a MEASUREMENT, not a filename comparison: the
# surface that arrived is read and its overall dimensions are compared against
# the same three dimensions measured off the wing this act's numbers belong to.
# A file arriving under the right name carrying a different body disagrees
# here, which is the whole reason the check is not done on the name.
#
# The tolerance is deliberately tight. These are overall extents of the same
# body written by the same writer, so agreement is a rounding artefact and
# anything else is a different surface; there is no grey band to tune.
IDENT_TOLERANCE_PCT = 1.0
# Where the control room puts a surface it has taken in.
GEOMETRY_DIR = Path(__file__).resolve().parents[1] / "geometry"

# Span stations for the true-scale section figure, in metres of span.
# Five span stations, not three: the section overlays are the act's main
# visual now, so they have to cover the wing rather than sample its inboard
# two thirds. Four of the five sit at reference-axis stations that carry a
# twist design variable, so the section figure and the twist figure can be
# read against each other station by station.
SECTION_Z = (0.0, 3.0, 7.2, 10.9, 13.5)

# Every three-dimensional frame carries this, verbatim, so that no still taken
# from the act can travel without the mesh it belongs to. The wording is fixed:
# it names the mesh, says why it was chosen, and says what was NOT done.
#
# THE WORDS ARE THE OWNER'S OWN (2026-09-01, captured at
# etc/sessions/2026-09-01T0043Z_sanaa_actD_visuals.md): "caption every 3D
# frame '38,304-cell mesh, chosen for speed - grid independence not assessed;
# result relative to this mesh.'"
#
# TWO OF HER OWN ORDERS COLLIDE ON ONE CHARACTER, AND THE COLLISION IS REAL.
# She dictated this caption with an EM DASH. Her standing demo convention bans
# em dashes from anything user-visible ("I don't ever want to see them"), and
# cfd's viewport wiring now renders this string on every filmed Act D frame --
# so the one place the em dash was quoted exactly is also the one place her ban
# most clearly bites. This carried the em dash until 2026-09-01 on the reading
# that a directive quoted verbatim is quoted exactly or it is not quoted.
#
# RULED BY THE CHIEF, [lab-attributed], disclosed to her to overturn: the
# SEMANTIC CONTENT is what she mandated and is preserved word for word; the
# TYPOGRAPHY falls under her ban. The em dash becomes a semicolon. EVERY WORD
# IS UNCHANGED and no claim moves -- it still names the mesh, says why it was
# chosen, and says what was NOT done. If she prefers the em dash back, this is
# one character and the record above says exactly what was traded for what.
MESH_CAPTION = ("38,304-cell mesh, chosen for speed; grid independence "
                "not assessed; result relative to this mesh.")

# VISUALS ITEM 1 (owner, 2026-09-01): "Confirm the surface render is the
# computational surface (1,008 faces)."
#
# CONFIRMED BY COUNTING, not by reading the artifact's own description of
# itself. The run's own constant/polyMesh/boundary declares
#
#     wing { type wall; nFaces 1008; startFace 113068; }
#
# and those 1008 faces are all four-sided over 1031 unique points. The surface
# this module streams carries the same 1031 points and 2016 triangles, exactly
# two per solver face, and its bounding box agrees with the mesh patch's to
# better than 4e-7 m on every axis. The check is
# cases/dafoam/ladder-a/geometry_audit/mesh_surface_check.py, run against
# /home/ubuntu/certonomous-runs/A2-mach-wing/constant/polyMesh.
#
# The assert below is what stops that from silently ceasing to be true. A
# decimated, re-meshed or capped surface would still draw perfectly well and
# would no longer be the thing the numbers were computed on, which is the
# whole substance of the owner's question.
SURFACE_QUAD_FACES = 1008
SURFACE_POINTS = 1031

# The axis roles of THIS act's wing, fixed by the mesh it was extracted from:
# chord along x, span along z, thickness along y. Stated as data rather than
# assumed inside a measurement, so that a surface which does not share it is
# noticed instead of mis-read.
ACT_AXES = (0, 2, 1)

# ------------------------------------------------------------- the close-up
# The whole wing is 14 m of span against the 186 mm reference shape change
# (DISP_REFERENCE above: final against baseline, unscaled), so framed to
# its span the change moves the outline about 4 px and has to be carried by
# the field painted on it. The inboard 2.2 m, given its own camera, is framed
# roughly four times tighter and the same TRUE-SCALE change moves the outline
# 23.6 px. That is a zoom, not a multiplier: not one coordinate is touched.
#
# Amplification was measured as the alternative and rejected. It is capped at
# x1.995 by the run's own active thickness constraint (thinnest recorded
# station 0.4988 of baseline against a 0.5 floor; past that the upper and
# lower surfaces touch and the wing passes through itself), and even at that
# ceiling it reaches only about 8 px. A true-scale shot that reads is strictly
# better than an amplified one that needs a label to defend it.
CLOSEUP_SPAN_M = 2.2
AMPLIFY_CEILING = 1.995        # kept: the act states why it did not amplify
# Camera hint for the close-up, honoured by control_room.html's drawGeometry.
#   axes: (thickness, span, chord) into the fixed camera's own frame. An EVEN
#         permutation, i.e. a proper rotation: the body is turned to face the
#         camera, never mirrored.
#   flat: pinned, not inferred. This wing's thickness-to-chord ratio is ~12%,
#         sitting exactly on the viewport's own 0.12 planform threshold, so an
#         inferred camera flips partway through the morph as the section
#         thickens, and snaps the shot. Pinning fixes that at the root.
CLOSEUP_VIEW = {"axes": [1, 2, 0], "flat": True}
# Silhouette motion, measured with the viewport's own projection at 760x460.
TRUE_SCALE_PX = 4.1
CLOSEUP_PX = 23.6


def load() -> dict[str, Any] | None:
    """The baked shape history, or None if this host does not carry it.

    THE SOLE FUNNEL, and therefore where the computational-surface check
    belongs. Every consumer in this act reaches the shape history through
    here, so an assertion here is one every call site inherits rather than
    one each call site has to remember (the standing rule: a lesson is not
    applied until every call site asserts it).

    A missing file is a host without the data and returns None, which the act
    already handles by playing without the viewport. A file that is PRESENT
    but is not the solver's own wing patch is a different thing entirely and
    RAISES: drawing a decimated or re-meshed surface while the act says the
    numbers belong to it is a silent substitution, and this act exists partly
    because of one.
    """
    try:
        doc = json.loads(FRAMES_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    n_quad = doc.get("n_quad_faces")
    n_tri = len(doc.get("faces") or ())
    n_pts = len(doc.get("base_vertices") or ())
    if (n_quad != SURFACE_QUAD_FACES or n_tri != 2 * SURFACE_QUAD_FACES
            or n_pts != SURFACE_POINTS):
        raise ValueError(
            f"{FRAMES_FILE} is not the computational wing patch: "
            f"{n_quad} quad faces, {n_tri} display triangles, {n_pts} points, "
            f"against the solver's {SURFACE_QUAD_FACES} / "
            f"{2 * SURFACE_QUAD_FACES} / {SURFACE_POINTS} counted from "
            f"constant/polyMesh/boundary. Refusing to draw it.")
    return doc


def dimensions(vertices: list, *, axes_hint: tuple | None = None
               ) -> dict[str, float]:
    """The three overall extents of a wing surface, in metres.

    Ordered as a reader reads a wing: how far it reaches across, how far it
    reaches back, how thick it gets.

    THE AXIS CONVENTION IS NOT ASSUMED. It used to be: this function read span
    off z, chord off x and thickness off y, and its docstring called that "the
    one every surface in this act shares". An uploaded wing did not share it --
    it used the ordinary aerospace convention, chord x, span y, thickness z --
    and so a perfectly good 1 m x 3 m x 0.12 m wing was reported as "span
    0.12 m, chord 1.0 m, thickness 3.0 m" and read as impossible. The file was
    right; the reading was wrong. A measurement that assumes an orientation
    cannot detect a file that does not have it, so this one works the
    orientation out from the shape instead.

    `axes_hint` is `(chord_axis, span_axis, thickness_axis)` and is used only
    when the caller already knows the orientation -- for this act's own wing,
    whose axes are fixed by the mesh it came from.
    """
    if axes_hint is None:
        from .geometry_admission import Surface, discover_axes
        found = discover_axes(Surface("<vertices>", vertices, [[0, 1, 2]]))
        c, s, t = (found["chord_axis"], found["span_axis"],
                   found["thickness_axis"])
    else:
        c, s, t = axes_hint
    axes = [[v[axis] for v in vertices] for axis in range(3)]
    return {"Span": max(axes[s]) - min(axes[s]),
            "Streamwise extent": max(axes[c]) - min(axes[c]),
            "Maximum thickness": max(axes[t]) - min(axes[t])}


def _float32_step(value: float) -> float:
    """One float32 step at ``value``: the finest difference an STL can hold.

    Computed from the format rather than assumed: the value is rounded to
    float32, its bit pattern incremented by one, and the difference taken. No
    table of magic epsilons and no dependency on numpy.
    """
    v = struct.unpack("<f", struct.pack("<f", abs(value)))[0]
    bits = struct.unpack("<I", struct.pack("<f", v))[0]
    nxt = struct.unpack("<f", struct.pack("<I", bits + 1))[0]
    return nxt - v


def identify(doc: dict, surface: str,
             directory: Path | None = None) -> dict[str, Any] | None:
    """Measure a received surface against this act's own wing.

    Returns the two sets of dimensions, the widest relative disagreement
    between them, and whether that clears :data:`IDENT_TOLERANCE_PCT`. Returns
    None when the file cannot be read at all, so the caller can say what
    happened rather than announce a check it could not run.
    """
    from .geometry_admission import _read, admit

    path = Path(directory or GEOMETRY_DIR) / Path(str(surface)).name
    # THE SAME READER THE ADMISSION DECISION USED, and the same coordinates.
    #
    # This used to call chief_engineer.geometry.load_surface directly, under a
    # comment reading "No decimation: a merged vertex moves an extent, and an
    # extent is the measurement. The whole surface is read exactly as it
    # arrived." The guard against decimation was right and is kept. The claim
    # of exactness was FALSE in the last decimal, and for a reason worth
    # naming: load_surface rounds every coordinate to 5 decimals to keep the
    # JSON it streams to a viewport small, so this identity check was
    # measuring a display copy while admit(), one line below, measured the
    # file. A rounding that belongs to the viewport had no business deciding
    # what a customer's file measures. Reading through _read fixes both: the
    # bytes are the file's, and the two measurements are now taken from ONE
    # reading rather than two independent ones that could disagree.
    surf = _read(path)
    if surf is None:
        return None

    # Admission first. A surface that cannot be run is not measured against
    # this act's wing and then quietly run as this act's wing: the caller is
    # handed the refusal and stops. Nothing is ever substituted in silence.
    decision = admit(path)
    if not decision["admitted"]:
        return {"measured": None, "known": None, "worst_pct": None,
                "match": False, "admitted": False, "decision": decision}

    a = decision["axes"]
    measured = dimensions(surf.vertices,
                          axes_hint=(a["chord_axis"], a["span_axis"],
                                     a["thickness_axis"]))
    # This act's own wing has a known orientation, fixed by the mesh it was
    # extracted from: chord along x, span along z, thickness along y.
    known = dimensions(doc["base_vertices"], axes_hint=ACT_AXES)
    worst = max(abs(measured[key] - known[key]) / known[key] * 100.0
                for key in known)
    # HOW FINE A DISAGREEMENT THIS COMPARISON CAN EVEN SEE. A binary STL
    # stores float32, so two representations of one body cannot be compared
    # closer than one float32 step at that size. Quoting more significant
    # figures than that is quoting the storage format, not the geometry --
    # which is exactly what the old reading did: through the rounded copy the
    # reference wing "disagreed with itself" by 3.3e-04%, 118 times larger
    # than the 2.8e-06% it actually does, and that figure was an artefact of
    # the fifth decimal place rather than a measurement of anything.
    floor = max(_float32_step(known[key]) / known[key] * 100.0
                for key in known)
    return {"measured": measured, "known": known, "worst_pct": worst,
            "resolution_pct": floor, "at_resolution_floor": worst <= floor,
            "match": worst <= IDENT_TOLERANCE_PCT, "admitted": True,
            "decision": decision, "orientation": a["convention"],
            "same_orientation_as_act": (a["chord_axis"], a["span_axis"],
                                        a["thickness_axis"]) == ACT_AXES}


def _surface(doc: dict, verts: list, field: dict | None, *,
             faces: list | None = None, view: dict | None = None) -> dict:
    faces = doc["faces"] if faces is None else faces
    payload = {"name": "A2 wing", "vertices": verts, "faces": faces,
               "triangles_total": len(faces), "triangles_shown": len(faces)}
    if field is not None:
        payload["field"] = field
    if view is not None:
        # Camera hint only. It turns the fixed camera onto the body; it never
        # changes a coordinate, and the viewport ignores it if it is not a
        # proper rotation.
        payload["view"] = view
    return payload


def closeup_index(doc: dict) -> tuple[list[int], list[list[int]], list[int]]:
    """The inboard span of the wing: kept points, re-indexed faces, face mask.

    A subset of the solver's own faces, whole. Nothing is re-meshed, capped or
    interpolated at the cut; the beat is a zoom onto part of the same surface.
    """
    inboard = {i for i, v in enumerate(doc["base_vertices"])
               if v[2] <= CLOSEUP_SPAN_M}
    keep = [i for i, f in enumerate(doc["faces"]) if inboard.issuperset(f)]
    ids = sorted({i for k in keep for i in doc["faces"][k]})
    remap = {g: i for i, g in enumerate(ids)}
    return ids, [[remap[i] for i in doc["faces"][k]] for k in keep], keep


def _normalise(values, lo: float, hi: float) -> list[float]:
    """0..1 per DRAWN face against a FIXED window.

    The artifact carries one value per quadrilateral solver face; the viewport
    draws each of those as two triangles, so each value is repeated for the
    pair. No triangle is ever given a value its own face did not have.

    The window is fixed across every frame on purpose: a per-frame rescale
    would make a wing that has barely moved look exactly like the finished
    one, which is the visual equivalent of a lie.
    """
    span = (hi - lo) or 1.0
    out = []
    for value in values:
        scaled = round(min(1.0, max(0.0, (value - lo) / span)), 4)
        out.append(scaled)
        out.append(scaled)
    return out


def frame_vertices(doc: dict, frame: dict) -> list[list[float]]:
    """Baseline plus this iteration's displacement. True scale, no factor.

    There is deliberately no way to ask this for an amplified surface. The
    act does not have that option, so neither does this function.
    """
    return [[round(b0 + d0, 6), round(b1 + d1, 6), round(b2 + d2, 6)]
            for (b0, b1, b2), (d0, d1, d2)
            in zip(doc["base_vertices"], frame["disp"])]


def write_baseline_stl(doc: dict, out_stl: Path = BASELINE_STL_PATH) -> Path:
    """Write the baseline wing patch as a binary STL and return its path.

    The vertices are the baseline surface's own, unchanged, and the triangles
    are the same ones the viewport draws, so the file and the surface on
    screen are one body. Every facet normal is computed from its own three
    corners rather than left at zero, so a reader that trusts the normal gets
    the same geometry as one that recomputes it.
    """
    verts = doc["base_vertices"]
    faces = doc["faces"]
    out_stl = Path(out_stl)
    out_stl.parent.mkdir(parents=True, exist_ok=True)
    header = b"Reference wing, baseline surface".ljust(80, b" ")
    body = bytearray(header + struct.pack("<I", len(faces)))
    for a, b, c in faces:
        pa, pb, pc = verts[a], verts[b], verts[c]
        ux, uy, uz = (pb[0] - pa[0], pb[1] - pa[1], pb[2] - pa[2])
        vx, vy, vz = (pc[0] - pa[0], pc[1] - pa[1], pc[2] - pa[2])
        nx, ny, nz = (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)
        length = (nx * nx + ny * ny + nz * nz) ** 0.5
        if length:
            nx, ny, nz = nx / length, ny / length, nz / length
        body += struct.pack("<12fH", nx, ny, nz, *pa, *pb, *pc, 0)
    out_stl.write_bytes(bytes(body))
    return out_stl


def write_surfaces(doc: dict, out: Path) -> dict[str, str]:
    """Write every viewport payload the act streams, and return their names.

    One baseline, one gradient-painted baseline, and one per major iteration.
    Roughly three megabytes of JSON and about a third of a second: it stays
    on the act's critical path deliberately, so the files served are always
    the ones this artifact describes rather than a stale leftover.
    """
    out.mkdir(parents=True, exist_ok=True)
    names: dict[str, str] = {}

    base = [list(v) for v in doc["base_vertices"]]
    (out / "a2_wing_baseline.json").write_text(
        json.dumps(_surface(doc, base, None), separators=(",", ":")),
        encoding="utf-8")
    names["baseline"] = "a2_wing_baseline.json"

    grad = doc["gradient"]
    glo, ghi = grad["window_mm_per_step"]
    # Symmetric about zero so the colour map's white sits exactly on "the
    # gradient asks for nothing here", and red/blue mean push out / pull in.
    gmax = max(abs(glo), abs(ghi))
    (out / "a2_wing_gradient.json").write_text(
        json.dumps(_surface(doc, base, {
            "name": "adjoint descent step, outward normal (mm per unit step)",
            "min": glo, "max": ghi,
            "color_min": round(-gmax, 2), "color_max": round(gmax, 2),
            "display_min": round(-gmax, 2), "display_max": round(gmax, 2),
            "values": _normalise(grad["values_mm_per_step"], -gmax, gmax),
        }), separators=(",", ":")), encoding="utf-8")
    names["gradient"] = "a2_wing_gradient.json"

    dlo, dhi = doc["disp_window_mm"]
    dmax = max(abs(dlo), abs(dhi))
    ids, near_faces, keep = closeup_index(doc)
    for frame in doc["frames"]:
        # Two passes over the same iteration, both at true scale: the whole
        # wing, then the inboard span on its own camera. Same surface, same
        # millimetres, same fixed colour window; only the framing differs.
        values = _normalise(frame["disp_n_mm"], -dmax, dmax)
        field = {
            # ITEM 2 (owner, 2026-07-31): the legend names the quantity it is
            # painting, down to the averaging. This field is the outward
            # NORMAL COMPONENT of the displacement, averaged over each
            # quadrilateral face, so its extremes sit inside the reference
            # (which is the largest TOTAL motion of any single point). Without
            # "per face" on the legend the two read as the same measurement
            # disagreeing, when they are two measurements agreeing.
            "name": "displacement from baseline, outward normal per face (mm)",
            # The convention rides with the payload so the legend and the act
            # cannot drift apart about what a millimetre on this bar means.
            "reference": DISP_REFERENCE,
            "min": min(frame["disp_n_mm"]), "max": max(frame["disp_n_mm"]),
            "color_min": round(-dmax, 1), "color_max": round(dmax, 1),
            "display_min": round(-dmax, 1), "display_max": round(dmax, 1),
            "values": values,
        }
        verts = frame_vertices(doc, frame)
        name = f"a2_wing_iter_{frame['iter']:02d}.json"
        (out / name).write_text(
            json.dumps(_surface(doc, verts, dict(field)),
                       separators=(",", ":")), encoding="utf-8")
        names[f"iter{frame['iter']}"] = name

        near = f"a2_wing_near_{frame['iter']:02d}.json"
        # `keep` indexes drawn triangles, and `values` is already one per
        # drawn triangle, so a kept triangle carries its own value across.
        near_values = [values[k] for k in keep]
        (out / near).write_text(
            json.dumps(_surface(doc, [verts[i] for i in ids],
                                dict(field, values=near_values),
                                faces=near_faces, view=CLOSEUP_VIEW),
                       separators=(",", ":")), encoding="utf-8")
        names[f"near{frame['iter']}"] = near
    return names


# --------------------------------------------------------------- true-scale
def slice_at(doc: dict, verts: list, z: float) -> list[tuple]:
    """Segments where the plane z = const cuts the wing surface.

    A plane cut of the surface triangulation itself: each crossing edge is
    interpolated linearly, which is exactly what the surface is between its
    own vertices. Nothing is fitted.
    """
    segs = []
    for tri in doc["faces"]:
        pts = [verts[i] for i in tri]
        hit = []
        for a, b in ((0, 1), (1, 2), (2, 0)):
            za, zb = pts[a][2], pts[b][2]
            if (za - z) * (zb - z) > 0 or za == zb:
                continue
            t = (z - za) / (zb - za)
            if 0.0 <= t <= 1.0:
                hit.append((pts[a][0] + t * (pts[b][0] - pts[a][0]),
                            pts[a][1] + t * (pts[b][1] - pts[a][1])))
        if len(hit) == 2:
            segs.append((hit[0], hit[1]))
    return segs


def section_figure(doc: dict, out_png: Path) -> str | None:
    """Baseline against the optimized shape, at true scale, equal aspect.

    This is the figure that answers "did the shape really change" without
    any amplification: at section scale a change of a few percent of chord
    is plainly visible, where on the whole three-dimensional wing it is a
    few pixels.
    """
    from chief_engineer import plot_theme as t

    plt = t._pyplot()
    if plt is None:
        return None
    from matplotlib.collections import LineCollection

    base = [list(v) for v in doc["base_vertices"]]
    final = frame_vertices(doc, doc["frames"][-1])
    fig, axes = plt.subplots(len(SECTION_Z), 1, figsize=(11.4, 10.4), dpi=150)
    for ax, z in zip(axes, SECTION_Z):
        for verts, colour, width, label in (
                (base, t.MUTED, 1.4, "baseline"),
                (final, t.LIVE, 1.8, "optimized, major iteration "
                                     f"{doc['frames'][-1]['iter']}")):
            segs = slice_at(doc, verts, z)
            ax.add_collection(LineCollection(segs, colors=colour,
                                             linewidths=width, label=label))
        ax.autoscale()
        ax.set_aspect("equal")     # true scale: the claim depends on this
        t.style_axes(ax, r"$x$, chordwise (m)" if z == SECTION_Z[-1] else "",
                     r"$y$ (m)", f"span station $z$ = {z:g} m")
    handles, labels = axes[0].get_legend_handles_labels()
    leg = fig.legend(handles, labels, frameon=False, fontsize=10,
                     labelcolor=t.INK, loc="upper right",
                     bbox_to_anchor=(0.995, 0.995))
    for text in leg.get_texts():
        text.set_color(t.INK)
    fig.suptitle("Wing sections, unscaled, no exaggeration applied",
                 color=t.INK, fontsize=14, x=0.012, y=0.985, ha="left",
                 va="top", weight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    fig.savefig(out_png)
    plt.close(fig)
    return str(out_png)


def twist_figure(doc: dict, out_png: Path) -> str | None:
    """The twist the optimizer put into the wing, station by station."""
    from chief_engineer import plot_theme as t

    plt = t._pyplot()
    if plt is None:
        return None
    z = doc["refaxis_z_m"]
    final = doc["frames"][-1]["twist_deg"]
    fig, ax = plt.subplots(figsize=(11.4, 4.0), dpi=150)
    ax.axhline(0.0, color=t.MUTED, linewidth=1.2, linestyle="--",
               label="baseline (untwisted)")
    ax.plot(z, [0.0] + list(final), color=t.LIVE, linewidth=2.0, marker="o",
            markersize=7, markeredgecolor=t.INK, markeredgewidth=0.8,
            label=f"optimized, major iteration {doc['frames'][-1]['iter']}")
    ax.annotate("root station carries no design variable",
                xy=(z[0], 0.0), xytext=(z[0] + 0.8, -0.45), color=t.MUTED,
                fontsize=9, arrowprops={"arrowstyle": "-", "color": t.DIM})
    t.style_axes(ax, r"Spanwise position of the reference-axis station, $z$ (m)",
                 "Twist, quarter chord (deg)",
                 "Twist the optimizer added, read from the recorded design "
                 "variables. Negative is nose down")
    leg = ax.legend(frameon=False, fontsize=10, labelcolor=t.INK, loc="best")
    for text in leg.get_texts():
        text.set_color(t.INK)
    fig.tight_layout()
    fig.savefig(out_png)
    plt.close(fig)
    return str(out_png)
