"""The A2 wing's shape history, prepared for the control-room viewport.

This module is the act-time half of the shape replay. It reads the static
artifact ``A2_shape_frames.json`` that :mod:`scripts.build_a2_shape_frames`
baked offline and turns it into the viewport payloads the control room
already knows how to render. It imports nothing but the standard library:
the act must run on a laptop with no OpenFOAM, no DAFoam, no pyGeo and no
network, so no part of the deformation is recomputed here. Every surface it
writes came out of the optimizer's own parameterization, offline, once.

Nothing here smooths or reshapes anything. The default everywhere is true
scale, and the pass the result is graded on is at true scale; what makes a
change of a few millimetres per hundred readable there is the field painted
on the surface, not a stretched shape. One clearly separated second pass
applies :data:`EXAGGERATION` to the displacement so the outline moves, and
the act names that factor on screen on every frame of it. No measurement is
ever amplified: the displacement colour bar stays in true millimetres in both
passes.
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

# The amplification used by the SECOND morph pass, after the true-scale one.
#
# It is not a free choice. The optimizer drove its own thickness constraint
# onto its lower bound: the smallest thickness it ever recorded is 0.4988 of
# the baseline thickness, against a constraint floor of 0.5. Surface
# displacement here is 96% thickness-direction motion and the FFD map
# is linear in the shape variables, so amplifying the displacement by k scales
# that thickness ratio to 1 + k*(0.4988 - 1). It reaches ZERO -- the upper and
# lower surfaces touching, i.e. the wing passing through itself -- at
# k = 1.995. That is a hard ceiling read off the run's own recorded
# constraint values, not a judgement call.
#
# 1.75 leaves the thinnest station at 12.3% of its baseline thickness: still a
# wing, nowhere self-intersecting, with real margin to the ceiling. It buys
# very little on screen (see EXAGGERATION_PX) because the ceiling is so low,
# and the act says so out loud rather than pretending otherwise.
EXAGGERATION = 1.75
EXAGGERATION_CEILING = 1.995
EXAGGERATION_MIN_THICKNESS_PCT = 12.3
# Silhouette motion this buys in the control-room viewport, measured with that
# viewport's own projection at 760x460: 4.1 px at true scale, 7.6 px here.
EXAGGERATION_PX = 7.6
TRUE_SCALE_PX = 4.1


def load() -> dict[str, Any] | None:
    """The baked shape history, or None if this host does not carry it."""
    try:
        return json.loads(FRAMES_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _surface(doc: dict, verts: list, field: dict | None) -> dict:
    payload = {"name": "A2 wing", "vertices": verts, "faces": doc["faces"],
               "triangles_total": len(doc["faces"]),
               "triangles_shown": len(doc["faces"])}
    if field is not None:
        payload["field"] = field
    return payload


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


def frame_vertices(doc: dict, frame: dict, factor: float = 1.0) -> list[list[float]]:
    """Baseline plus this iteration's displacement, times ``factor``.

    ``factor`` defaults to 1.0 -- true scale, the default everywhere. It is
    only ever passed as :data:`EXAGGERATION`, by the one clearly labelled
    second pass, and that pass names the number on screen for every frame it
    shows.
    """
    if factor == 1.0:
        return [[round(b0 + d0, 6), round(b1 + d1, 6), round(b2 + d2, 6)]
                for (b0, b1, b2), (d0, d1, d2)
                in zip(doc["base_vertices"], frame["disp"])]
    return [[round(b0 + factor * d0, 6), round(b1 + factor * d1, 6),
             round(b2 + factor * d2, 6)]
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
    for frame in doc["frames"]:
        # Two passes over the same iteration: true scale, then the labelled
        # amplification. The FIELD is the true displacement in millimetres in
        # both, so the legend never inherits the factor -- only the geometry
        # does, and only in the pass whose every label names it.
        field = {
            "name": "displacement from baseline, outward normal (mm)",
            "min": min(frame["disp_n_mm"]), "max": max(frame["disp_n_mm"]),
            "color_min": round(-dmax, 1), "color_max": round(dmax, 1),
            "display_min": round(-dmax, 1), "display_max": round(dmax, 1),
            "values": _normalise(frame["disp_n_mm"], -dmax, dmax),
        }
        for key, suffix, factor in (
                (f"iter{frame['iter']}", "", 1.0),
                (f"x{frame['iter']}", "_x", EXAGGERATION)):
            name = f"a2_wing_iter_{frame['iter']:02d}{suffix}.json"
            (out / name).write_text(
                json.dumps(_surface(doc, frame_vertices(doc, frame, factor),
                                    dict(field)), separators=(",", ":")),
                encoding="utf-8")
            names[key] = name
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
    fig.suptitle("Wing sections at true scale, no exaggeration",
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
