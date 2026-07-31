"""The A2 wing's shape history, prepared for the control-room viewport.

This module is the act-time half of the shape replay. It reads the static
artifact ``A2_shape_frames.json`` that :mod:`scripts.build_a2_shape_frames`
baked offline and turns it into the viewport payloads the control room
already knows how to render. It imports nothing but the standard library:
the act must run on a laptop with no OpenFOAM, no DAFoam, no pyGeo and no
network, so no part of the deformation is recomputed here. Every surface it
writes came out of the optimizer's own parameterization, offline, once.

Nothing here scales, amplifies or smooths anything. Every surface that
reaches the screen is at TRUE SCALE, and every number on the legend is a true
millimetre. The shape change is made legible two ways, both of which are
honest because neither touches a coordinate: a displacement field painted on
the wing, and a second pass on the inboard 2.2 m of span with its own camera,
where the same true-scale change is framed about four times tighter.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_LADDER = (Path(__file__).resolve().parents[2]
           / "demo-output" / "website" / "dafoam" / "ladder-a")
FRAMES_FILE = _LADDER / "A2_shape_frames.json"

# Chordwise stations for the true-scale section figure, in metres of span.
# Root, mid-semispan and outboard: enough to show that the change is not one
# local dent, few enough that each section stays legible.
SECTION_Z = (0.0, 4.5, 9.0)

# ------------------------------------------------------------- the close-up
# The whole wing is 14 m of span against a 186 mm shape change, so framed to
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
    """The baked shape history, or None if this host does not carry it."""
    try:
        return json.loads(FRAMES_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


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
            "name": "displacement from baseline, outward normal (mm)",
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
    fig, axes = plt.subplots(len(SECTION_Z), 1, figsize=(11.4, 6.2), dpi=150)
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
        t.style_axes(ax, "x, chordwise (m)" if z == SECTION_Z[-1] else "",
                     "y (m)", f"span station z = {z:g} m")
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
    t.style_axes(ax, "Spanwise position of the reference-axis station, z (m)",
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
