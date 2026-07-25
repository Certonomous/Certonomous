"""Quantitative validation of the two published NACA pressure-slice fields.

The owner is publishing the mid-span pressure-slice images for the NACA 4412
wing and the NACA 0015 sail. This script validates the pressure FIELDS behind
those images against hard physics invariants and published experimental data,
and renders the evidence plots for the validation note. It never edits the
slice pipeline; it reads the same solver output (``body.vtp`` boundary patch
and ``internal.vtu`` volume) the pipeline itself consumed.

Checks
------
NACA 0015 sail (symmetric section, zero incidence, U = 75 m/s):
  * upper/lower surface Cp mirror symmetry (max and mean residual),
  * leading-edge stagnation Cp approaching 1.0,
  * far-field decay of the pressure disturbance at 1c and 2c laterally,
  * suction-peak magnitude and location against 2D section references,
    with the finite-span (AR 1.5) relief direction stated.

NACA 4412 wing (cambered, geometric incidence from the case itself,
U = 15 m/s):
  * mid-span surface Cp(x/c) against Pinkerton, NACA Report 563 (1936),
    Table I, at the tabulated angle whose section lift is nearest ours,
  * RMS and max deviation per surface, with the finite-wing caveat.

Cp convention: the solver is incompressible, p is kinematic (m^2/s^2), so
Cp = (p - p_inf) / (0.5 * U_inf^2) with no density factor. p_inf is measured
from the far field of the same solved volume and reported.

Pure computation functions live at the top of this module so the unit tests
exercise them without any solver output on disk.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------
# Pinkerton, NACA Report 563 (1936), "Calculated and Measured Pressure
# Distributions over the Midspan Section of the NACA 4412 Airfoil", Table I.
# Columns transcribed from the printed table (NASA NTRS scan, document
# 19930091638, page 15): orifice station (percent chord from the leading
# edge), ordinate (percent chord above the chord line), and the measured
# pressure coefficient P = (p - p_inf)/q at geometric angles of attack of
# -2, 0, and +2 degrees. Test conditions: variable-density tunnel, average
# Reynolds number 3,100,000, rectangular 5 by 30 inch model (aspect ratio 6),
# midspan section.
PINKERTON_R563_TABLE_I = [
    # (station %c, ordinate %c, P at -2 deg, P at 0 deg, P at +2 deg)
    (100.00, 0.00, 0.207, 0.200, 0.181),
    (97.92, -0.16, 0.180, 0.183, 0.164),
    (94.86, -0.16, 0.158, 0.166, 0.154),
    (89.90, -0.22, 0.140, 0.156, 0.152),
    (84.94, -0.28, 0.098, 0.118, 0.118),
    (74.92, -0.52, 0.095, 0.126, 0.136),
    (64.94, -0.84, 0.062, 0.104, 0.120),
    (54.48, -1.24, 0.021, 0.072, 0.100),
    (49.98, -1.44, -0.005, 0.050, 0.091),
    (44.90, -1.64, -0.017, 0.048, 0.088),
    (39.98, -1.86, -0.041, 0.031, 0.071),
    (34.90, -2.10, -0.073, 0.010, 0.066),
    (29.96, -2.30, -0.105, -0.011, 0.048),
    (24.90, -2.54, -0.165, -0.054, 0.025),
    (19.98, -2.76, -0.244, -0.111, -0.011),
    (14.94, -2.90, -0.348, -0.180, -0.053),
    (9.96, -2.86, -0.501, -0.279, -0.111),
    (7.38, -2.72, -0.596, -0.333, -0.131),
    (4.94, -2.46, -0.777, -0.428, -0.150),
    (2.92, -2.06, -0.932, -0.467, -0.098),
    (1.66, -1.60, -1.059, -0.436, 0.028),
    (0.92, -1.20, -0.995, -0.266, 0.254),
    (0.36, -0.70, -0.631, 0.156, 0.639),
    (0.00, 0.00, 0.356, 0.834, 0.989),
    (0.00, 0.68, 0.945, 1.010, 0.854),
    (0.44, 1.56, 0.948, 0.720, 0.336),
    (0.94, 2.16, 0.770, 0.468, 0.055),
    (1.70, 2.78, 0.569, 0.246, -0.148),
    (2.94, 3.64, 0.332, 0.018, -0.336),
    (4.90, 4.68, 0.110, -0.179, -0.485),
    (7.50, 5.74, -0.066, -0.312, -0.568),
    (9.96, 6.56, -0.168, -0.388, -0.623),
    (12.58, 7.34, -0.271, -0.468, -0.676),
    (14.92, 7.88, -0.309, -0.500, -0.700),
    (17.44, 8.40, -0.360, -0.537, -0.721),
    (19.96, 8.80, -0.402, -0.568, -0.740),
    (22.44, 9.16, -0.452, -0.609, -0.769),
    (24.92, 9.52, -0.454, -0.599, -0.746),
    (27.44, 9.62, -0.471, -0.606, -0.742),
    (29.88, 9.76, -0.469, -0.594, -0.722),
    (34.98, 9.90, -0.473, -0.596, -0.693),
    (39.90, 9.84, -0.447, -0.542, -0.635),
    (44.80, 9.64, -0.439, -0.519, -0.639),
    (49.92, 9.22, -0.389, -0.455, -0.525),
    (54.92, 8.76, -0.351, -0.406, -0.471),
    (59.94, 8.16, -0.342, -0.391, -0.438),
    (64.90, 7.54, -0.296, -0.334, -0.378),
    (69.86, 6.76, -0.250, -0.282, -0.319),
    (74.90, 5.88, -0.200, -0.222, -0.252),
    (79.92, 4.92, -0.155, -0.169, -0.191),
    (84.88, 3.88, -0.094, -0.101, -0.116),
    (89.88, 2.74, -0.016, -0.017, -0.026),
    (94.90, 1.48, 0.078, 0.082, 0.076),
    (98.00, 0.68, 0.147, 0.150, 0.143),
]

# Report 563, Table II: integrated section lift coefficient at the same
# geometric angles, and the effective 2D angle after the tunnel/induced
# correction Pinkerton reports (alpha_0 = alpha - alpha_i).
PINKERTON_ALPHAS = {
    -2.0: {"column": 2, "cl": 0.146, "alpha_effective": -2.2},
    0.0: {"column": 3, "cl": 0.338, "alpha_effective": -0.5},
    2.0: {"column": 4, "cl": 0.501, "alpha_effective": 1.2},
}
PINKERTON_SOURCE = ("Pinkerton, NACA Report 563 (1936), Table I, "
                    "midspan section, Re 3.1e6, aspect ratio 6 model")

# 2D references for the NACA 0015 suction peak at zero incidence: published
# panel-method and section data put the 2D minimum near -0.55 to -0.65 at
# x/c of roughly 0.2 to 0.3 (equivalent to a peak velocity ratio v/V of
# about 1.25 to 1.28 in Abbott and von Doenhoff style velocity tables).
NACA0015_2D_CPMIN_BAND = (-0.65, -0.55)
NACA0015_2D_CPMIN_XC = (0.20, 0.30)


# ---------------------------------------------------------------------------
# Pure computation (unit-tested; no I/O, no solver output needed)
# ---------------------------------------------------------------------------

def cp_from_kinematic(p, p_inf: float, u_inf: float):
    """Pressure coefficient from kinematic pressure (p already p over rho).

    Cp = (p - p_inf) / (0.5 * U_inf^2); with p in m^2/s^2 the density never
    appears, which is the correct incompressible-solver form.
    """
    import numpy as np

    q = 0.5 * float(u_inf) * float(u_inf)
    if q <= 0.0:
        raise ValueError("u_inf must be positive")
    return (np.asarray(p, dtype=np.float64) - float(p_inf)) / q


def polygon_geometry(vertices, polys):
    """Centroid, outward normal (unit), and area of each polygon.

    ``vertices`` is (N, 3); ``polys`` a list of vertex-index sequences in the
    patch's own winding (outward for an OpenFOAM boundary patch). Normals use
    Newell's method, exact for planar polygons and stable for the near-planar
    quads snappyHexMesh emits. Returns (centroids (M,3), normals (M,3),
    areas (M,)).
    """
    import numpy as np

    verts = np.asarray(vertices, dtype=np.float64)
    centroids = np.empty((len(polys), 3))
    normals = np.empty((len(polys), 3))
    areas = np.empty(len(polys))
    for i, poly in enumerate(polys):
        pts = verts[list(poly)]
        centroids[i] = pts.mean(axis=0)
        # Newell: sum of cross products of consecutive vertices.
        rolled = np.roll(pts, -1, axis=0)
        n = np.sum(np.cross(pts, rolled), axis=0)
        mag = np.linalg.norm(n)
        areas[i] = 0.5 * mag
        normals[i] = n / mag if mag > 0.0 else 0.0
    return centroids, normals, areas


def midspan_band(span_coords, station: float, start_half_width: float,
                 min_count: int = 200, widenings: int = 6):
    """Boolean mask of faces within a band about the mid-span station.

    Starts at ``start_half_width`` and doubles up to ``widenings`` times
    until at least ``min_count`` faces are inside, so a coarse patch still
    yields a section. Returns (mask, half_width_used).
    """
    import numpy as np

    coords = np.asarray(span_coords, dtype=np.float64)
    half = float(start_half_width)
    mask = np.abs(coords - station) <= half
    for _ in range(widenings):
        if int(mask.sum()) >= min_count:
            break
        half *= 2.0
        mask = np.abs(coords - station) <= half
    return mask, half


def cosine_edges(n_bins: int):
    """Bin edges on [0, 1] clustered toward both ends by the cosine map.

    Surface pressure varies steepest at the leading edge; uniform bins smear
    the stagnation spike and the suction knee, so the survey bins cluster
    where the physics does.
    """
    import numpy as np

    theta = np.linspace(0.0, math.pi, int(n_bins) + 1)
    return 0.5 * (1.0 - np.cos(theta))


def chord_fraction(x, x_le: float, x_te: float):
    """Normalise a chordwise coordinate to x/c in [0, 1]."""
    import numpy as np

    span = float(x_te) - float(x_le)
    if span <= 0.0:
        raise ValueError("x_te must exceed x_le")
    return (np.asarray(x, dtype=np.float64) - float(x_le)) / span


def binned_curve(xc, cp, edges):
    """Mean Cp per x/c bin. Returns (centers, mean_cp, counts) for non-empty
    bins only, in ascending x/c order."""
    import numpy as np

    xc = np.asarray(xc, dtype=np.float64)
    cp = np.asarray(cp, dtype=np.float64)
    edges = np.asarray(edges, dtype=np.float64)
    idx = np.digitize(xc, edges) - 1
    centers, means, counts = [], [], []
    for b in range(len(edges) - 1):
        sel = idx == b
        n = int(sel.sum())
        if n == 0:
            continue
        centers.append(0.5 * (edges[b] + edges[b + 1]))
        means.append(float(cp[sel].mean()))
        counts.append(n)
    return (np.asarray(centers), np.asarray(means),
            np.asarray(counts, dtype=np.int64))


def symmetry_residual(xc_a, cp_a, xc_b, cp_b, edges):
    """Mirror-symmetry residual between two surfaces of a symmetric body.

    Bins both sides on the same x/c edges and differences the bin means where
    both sides have data. Returns a dict with the per-bin arrays and the
    max/mean absolute residual.
    """
    import numpy as np

    ca, ma, _ = binned_curve(xc_a, cp_a, edges)
    cb, mb, _ = binned_curve(xc_b, cp_b, edges)
    common, ia, ib = np.intersect1d(ca, cb, return_indices=True)
    if common.size == 0:
        return {"xc": common, "delta": common, "max_abs": float("nan"),
                "mean_abs": float("nan"), "bins_compared": 0}
    delta = ma[ia] - mb[ib]
    return {"xc": common, "delta": delta,
            "max_abs": float(np.max(np.abs(delta))),
            "mean_abs": float(np.mean(np.abs(delta))),
            "bins_compared": int(common.size)}


def normal_force_from_cp(xc_upper, cp_upper, xc_lower, cp_lower,
                         n_points: int = 200):
    """Section normal-force coefficient cn = integral of (Cp_l - Cp_u) d(x/c).

    Both surfaces are interpolated onto a common x/c grid restricted to the
    overlap of the two surveys. At small effective incidence cn is close to
    the section lift coefficient cl.
    """
    import numpy as np

    xu = np.asarray(xc_upper, dtype=np.float64)
    cu = np.asarray(cp_upper, dtype=np.float64)
    xl = np.asarray(xc_lower, dtype=np.float64)
    cl = np.asarray(cp_lower, dtype=np.float64)
    iu = np.argsort(xu)
    il = np.argsort(xl)
    lo = max(float(xu[iu].min()), float(xl[il].min()))
    hi = min(float(xu[iu].max()), float(xl[il].max()))
    if hi <= lo:
        raise ValueError("surfaces do not overlap in x/c")
    grid = np.linspace(lo, hi, n_points)
    upper = np.interp(grid, xu[iu], cu[iu])
    lower = np.interp(grid, xl[il], cl[il])
    return float(np.trapezoid(lower - upper, grid))


def deviation_stats(x_ref, cp_ref, x_ours, cp_ours):
    """RMS and max absolute deviation of our curve sampled at the reference
    stations (restricted to the x/c range our survey covers)."""
    import numpy as np

    xr = np.asarray(x_ref, dtype=np.float64)
    cr = np.asarray(cp_ref, dtype=np.float64)
    xo = np.asarray(x_ours, dtype=np.float64)
    co = np.asarray(cp_ours, dtype=np.float64)
    order = np.argsort(xo)
    xo, co = xo[order], co[order]
    inside = (xr >= xo.min()) & (xr <= xo.max())
    if not inside.any():
        return {"rms": float("nan"), "max_abs": float("nan"),
                "n_stations": 0, "worst_xc": float("nan")}
    ours_at_ref = np.interp(xr[inside], xo, co)
    delta = ours_at_ref - cr[inside]
    worst = int(np.argmax(np.abs(delta)))
    return {"rms": float(np.sqrt(np.mean(delta ** 2))),
            "max_abs": float(np.max(np.abs(delta))),
            "n_stations": int(inside.sum()),
            "worst_xc": float(xr[inside][worst]),
            "delta": delta, "xc": xr[inside]}


def pinkerton_surfaces(column: int):
    """Split Table I into (upper, lower) as (x/c, P) arrays for one alpha
    column. Upper orifices have positive ordinates; the two leading-edge
    rows anchor their own sides (ordinate 0.68 upper, 0.00 lower)."""
    import numpy as np

    upper, lower = [], []
    for row in PINKERTON_R563_TABLE_I:
        station, ordinate = row[0] / 100.0, row[1]
        target = upper if ordinate > 0.0 else lower
        target.append((station, row[column]))
    upper.sort()
    lower.sort()
    return (np.asarray(upper, dtype=np.float64),
            np.asarray(lower, dtype=np.float64))


def nearest_pinkerton_alpha(section_cl: float) -> float:
    """The tabulated geometric alpha whose section cl is nearest ours."""
    return min(PINKERTON_ALPHAS,
               key=lambda a: abs(PINKERTON_ALPHAS[a]["cl"] - section_cl))


# ---------------------------------------------------------------------------
# Solver-output extraction (reuses field_render's readers; read-only)
# ---------------------------------------------------------------------------

def read_patch_polys(vtp_path, field: str = "p"):
    """Vertices, polygons, and per-polygon cell values from a boundary .vtp.

    Unlike field_render._read_patch this keeps the original polygons (no fan
    triangulation) and takes the CELL value of the field: for a zeroGradient
    wall that is the solver's own wall-face pressure, which is the honest
    quantity for surface Cp.
    """
    import numpy as np

    from chief_engineer import field_render as fr

    text = Path(vtp_path).read_text(errors="replace")
    header_bytes = 8 if "header_type='UInt64'" in text else 4
    points_section = fr._POINTS.search(text).group(0)
    flat = fr._named(points_section, "Points", header_bytes)
    vertices = np.asarray(flat, dtype=np.float64).reshape(-1, 3)

    polys_section = fr._POLYS.search(text).group(0)
    connectivity = [int(v) for v in
                    fr._named(polys_section, "connectivity", header_bytes)]
    offsets = [int(v) for v in
               fr._named(polys_section, "offsets", header_bytes)]
    polys = []
    start = 0
    for end in offsets:
        polys.append(connectivity[start:end])
        start = end

    cell_section = fr._CELLDATA.search(text)
    values = fr._named(cell_section.group(0), field, header_bytes)
    if values is None or len(values) != len(polys):
        raise ValueError(f"no per-cell '{field}' on {vtp_path}")
    return vertices, polys, np.asarray(values, dtype=np.float64)


def extract_section(vtp_path, *, span_axis: int, station: float,
                    chord_axis: int, lift_axis: int, u_inf: float,
                    p_inf: float, start_half_width: float):
    """Mid-span surface Cp survey from the body patch.

    Returns a dict with per-face x/c, Cp, side split (by outward-normal sign
    along the lift axis), chord geometry, and the stagnation reading.
    """
    import numpy as np

    vertices, polys, p_wall = read_patch_polys(vtp_path, "p")
    centroids, normals, areas = polygon_geometry(vertices, polys)
    mask, half_used = midspan_band(centroids[:, span_axis], station,
                                   start_half_width)
    c = centroids[mask]
    n = normals[mask]
    p = p_wall[mask]

    x_le = float(c[:, chord_axis].min())
    x_te = float(c[:, chord_axis].max())
    xc = chord_fraction(c[:, chord_axis], x_le, x_te)
    cp = cp_from_kinematic(p, p_inf, u_inf)
    # Invariant over the WHOLE patch, not only the band: incompressible wall
    # pressure can never exceed stagnation, so max Cp must stay at or below
    # 1.0 (cell-centred sampling keeps it a little under).
    global_max_cp = float(cp_from_kinematic(p_wall, p_inf, u_inf).max())

    # An OpenFOAM boundary patch winds its faces outward from the fluid,
    # i.e. INTO the body, so the upper surface is the group whose normals
    # point down the lift axis (verified against face-centroid positions).
    upper = n[:, lift_axis] < 0.0
    le_i = int(np.argmin(c[:, chord_axis]))
    te_i = int(np.argmax(c[:, chord_axis]))
    alpha_geom = math.degrees(math.atan2(
        c[le_i, lift_axis] - c[te_i, lift_axis], x_te - x_le))

    stag_i = int(np.argmax(cp))
    return {
        "xc": xc, "cp": cp, "upper": upper,
        "chord": x_te - x_le, "x_le": x_le, "x_te": x_te,
        "alpha_geometric_deg": alpha_geom,
        "band_half_width": half_used, "faces": int(mask.sum()),
        "stagnation_cp": float(cp[stag_i]),
        "stagnation_xc": float(xc[stag_i]),
        "global_max_cp": global_max_cp,
        "lift_coord_le": float(c[le_i, lift_axis]),
        "lift_coord_te": float(c[te_i, lift_axis]),
    }


def farfield_pressure(vtu_path, *, span_axis: int, station: float,
                      body_center, chord: float, plane_axes,
                      probe_axis: int, probe_center: float,
                      span_extent: float):
    """p_inf and lateral decay from the case's own volume output.

    Slices the volume at the same mid-span station the published image used
    (field_render.pick_slice, the exact machinery of the image), then:
      * p_inf = median cell p at more than 3 chords lateral distance,
      * decay = mean |p - p_inf| in lateral shells at 1c and 2c,
    reported in Cp units. ``probe_axis`` is the in-plane lateral axis and
    ``probe_center`` the body's coordinate on it.
    """
    import numpy as np

    from chief_engineer import field_render as fr

    volume = fr.read_volume_field(vtu_path, "p")
    if volume is None:
        raise ValueError(f"no volume field in {vtu_path}")
    points, connectivity, offsets, values = volume
    centres, extents = fr.cell_centres(points, connectivity, offsets)
    values = values[:len(centres)]
    keep, _ = fr.pick_slice(
        centres, extents, axis=span_axis, station=station,
        half_thickness=fr.SLICE_HALF_THICKNESS_FRACTION * span_extent)
    sl_c = centres[keep]
    sl_p = values[keep]

    axis_u, axis_v = plane_axes
    du = sl_c[:, axis_u] - body_center[0]
    dv = sl_c[:, axis_v] - body_center[1]
    radial = np.hypot(du, dv)

    far = radial > 3.0 * chord
    p_inf = float(np.median(sl_p[far])) if far.any() else 0.0

    lateral = np.abs(sl_c[:, probe_axis] - probe_center)
    # Keep the probe shells over the body's chordwise footprint so the shell
    # reads the disturbance beside the body, not the far wake.
    chordwise = np.abs(sl_c[:, axis_u] - body_center[0]) <= 0.75 * chord
    decay = {}
    for label, dist in (("1c", 1.0 * chord), ("2c", 2.0 * chord)):
        shell = chordwise & (np.abs(lateral - dist) <= 0.1 * chord)
        decay[label] = (float(np.mean(np.abs(sl_p[shell] - p_inf)))
                        if shell.any() else float("nan"))
    return {"p_inf": p_inf, "decay_abs_p": decay,
            "slice_cells": int(keep.size), "far_cells": int(far.sum())}


# ---------------------------------------------------------------------------
# Figures (control-room theme, evidence for the validation note)
# ---------------------------------------------------------------------------

def _cp_axes(plt, figsize=(11.4, 6.4)):
    fig, ax = plt.subplots(figsize=figsize, dpi=150)
    ax.invert_yaxis()  # aero convention: suction up
    return fig, ax


def render_4412_figure(section, ref_upper, ref_lower, stats_u, stats_l, *,
                       alpha_ref: float, section_cn: float, out_png):
    """Our mid-span Cp(x/c) with the Pinkerton distribution overlaid."""
    import numpy as np

    from chief_engineer.plot_theme import (DIM, INK, LIVE, MUTED, TREND,
                                           _pyplot, style_axes)

    plt = _pyplot()
    fig, ax = _cp_axes(plt)

    edges = cosine_edges(72)
    for side, color, label in ((section["upper"], LIVE, "upper surface"),
                               (~section["upper"], TREND, "lower surface")):
        cx, cm, _ = binned_curve(section["xc"][side], section["cp"][side],
                                 edges)
        ax.plot(cx, cm, color=color, linewidth=2.2,
                label=f"This solve, {label}")
    ax.plot(ref_upper[:, 0], ref_upper[:, 1], linestyle="none", marker="o",
            markersize=7, markerfacecolor="none", markeredgecolor=LIVE,
            markeredgewidth=1.6, label="Pinkerton R-563, upper")
    ax.plot(ref_lower[:, 0], ref_lower[:, 1], linestyle="none", marker="s",
            markersize=6.5, markerfacecolor="none", markeredgecolor=TREND,
            markeredgewidth=1.6, label="Pinkerton R-563, lower")
    ax.axhline(0.0, color=DIM, linewidth=0.9)

    ax.annotate(
        (f"upper: RMS {stats_u['rms']:.3f}, max {stats_u['max_abs']:.3f}\n"
         f"lower: RMS {stats_l['rms']:.3f}, max {stats_l['max_abs']:.3f}\n"
         f"stagnation $C_p$ = {section['stagnation_cp']:.3f}"),
        xy=(0.97, 0.05), xycoords="axes fraction", ha="right", va="bottom",
        fontsize=11.5, color=INK, weight="bold",
        bbox={"boxstyle": "round,pad=0.5", "facecolor": "#0f1315",
              "edgecolor": DIM, "alpha": 0.9})

    style_axes(ax, r"chordwise position  $x/c$",
               r"pressure coefficient  $C_p$",
               "NACA 4412 wing, mid-span surface pressure against "
               "published measurement")
    leg = ax.legend(frameon=False, fontsize=10.5, loc="lower center",
                    ncol=2, bbox_to_anchor=(0.5, 0.16))
    for text in leg.get_texts():
        text.set_color(INK)

    note = (f"Reference: {PINKERTON_SOURCE},\n"
            f"alpha {alpha_ref:g} deg column, section cl "
            f"{PINKERTON_ALPHAS[alpha_ref]['cl']:.3f}, chosen as nearest to "
            f"our mid-span section cn {section_cn:.3f}. Finite wing, aspect "
            "ratio 3, geometric incidence "
            f"{section['alpha_geometric_deg']:.2f} deg.")
    fig.text(0.01, 0.008, note, color=MUTED, fontsize=8.5,
             family="monospace", va="bottom")
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    out_png = Path(out_png)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png)
    plt.close(fig)
    return str(out_png)


def render_0015_figure(section, sym, farfield, u_inf: float, *, out_png):
    """Invariant checks for the symmetric sail: mirror symmetry, stagnation,
    suction peak against the 2D band, far-field decay."""
    import numpy as np

    from chief_engineer.plot_theme import (DIM, INK, LIVE, MUTED, NEEDS,
                                           TREND, VALID, _pyplot, style_axes)

    plt = _pyplot()
    fig, (ax, ax2) = plt.subplots(
        2, 1, figsize=(11.4, 8.2), dpi=150, sharex=True,
        gridspec_kw={"height_ratios": [3.0, 1.15], "hspace": 0.08})
    ax.invert_yaxis()

    edges = cosine_edges(72)
    sides = ((section["upper"], LIVE, "side A (y > 0)", "-"),
             (~section["upper"], TREND, "side B (y < 0)", (0, (5, 4))))
    for side, color, label, dash in sides:
        cx, cm, _ = binned_curve(section["xc"][side], section["cp"][side],
                                 edges)
        # Side B rides on top of side A almost exactly; the dashed stroke
        # keeps both visible so the mirror symmetry is seen, not asserted.
        ax.plot(cx, cm, color=color, linewidth=2.2, linestyle=dash,
                label=label)
    ax.axhline(0.0, color=DIM, linewidth=0.9)

    # 2D reference band for the suction peak, with the finite-span note.
    ax.fill_between(NACA0015_2D_CPMIN_XC, NACA0015_2D_CPMIN_BAND[0],
                    NACA0015_2D_CPMIN_BAND[1], color=MUTED, alpha=0.22,
                    linewidth=0)
    ax.annotate("2D section suction band\n(published, infinite span)",
                xy=(NACA0015_2D_CPMIN_XC[1],
                    0.5 * sum(NACA0015_2D_CPMIN_BAND)),
                xytext=(0.42, 0.88), textcoords="axes fraction",
                fontsize=10, color=MUTED, va="top",
                arrowprops={"arrowstyle": "-", "color": MUTED,
                            "linewidth": 0.9, "alpha": 0.8})

    cp_min = float(section["cp"].min())
    xc_at_min = float(section["xc"][int(np.argmin(section["cp"]))])
    ax.annotate(
        (f"stagnation $C_p$ = {section['stagnation_cp']:.3f}\n"
         f"suction peak $C_p$ = {cp_min:.3f} at x/c = {xc_at_min:.2f}"),
        xy=(0.97, 0.05), xycoords="axes fraction", ha="right", va="bottom",
        fontsize=11.5, color=INK, weight="bold",
        bbox={"boxstyle": "round,pad=0.5", "facecolor": "#0f1315",
              "edgecolor": DIM, "alpha": 0.9})

    style_axes(ax, "", r"pressure coefficient  $C_p$",
               "NACA 0015 sail, zero incidence: mirror symmetry and "
               "invariant checks")
    ax.tick_params(labelbottom=False)
    leg = ax.legend(frameon=False, fontsize=10.5, loc="lower center", ncol=2,
                    bbox_to_anchor=(0.5, 0.14))
    for text in leg.get_texts():
        text.set_color(INK)

    # Residual panel: the two sides differenced bin by bin.
    color = VALID if sym["max_abs"] < 0.06 else NEEDS
    ax2.bar(sym["xc"], np.abs(sym["delta"]), width=0.014, color=color,
            alpha=0.85)
    ax2.axhline(sym["mean_abs"], color=INK, linewidth=1.0,
                linestyle=(0, (4, 3)))
    ax2.annotate(
        (f"asymmetry: mean {sym['mean_abs']:.4f}, "
         f"max {sym['max_abs']:.4f} ({sym['bins_compared']} stations)"),
        xy=(0.97, 0.82), xycoords="axes fraction", ha="right",
        fontsize=10.5, color=INK, weight="bold")
    style_axes(ax2, r"chordwise position  $x/c$",
               r"$|\Delta C_p|$", "")
    ax2.set_ylim(0, max(0.05, sym["max_abs"] * 1.5))

    q = 0.5 * u_inf * u_inf
    d1 = farfield["decay_abs_p"]["1c"] / q
    d2 = farfield["decay_abs_p"]["2c"] / q
    note = (f"Far-field decay on the image's own slice: mean |Cp| "
            f"{d1:.4f} at 1 chord lateral, {d2:.4f} at 2 chords; "
            f"p_inf = {farfield['p_inf']:.1f} m2/s2 "
            "(median beyond 3 chords).\n"
            "Finite span, aspect ratio 1.5 with free tips: milder suction "
            "than the 2D band is the expected direction of the offset.")
    fig.text(0.01, 0.008, note, color=MUTED, fontsize=8.5,
             family="monospace", va="bottom")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    out_png = Path(out_png)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png)
    plt.close(fig)
    return str(out_png)


# ---------------------------------------------------------------------------
# Case runners
# ---------------------------------------------------------------------------

def validate_naca4412(staging: Path, out_dir: Path) -> dict:
    """NACA 4412 wing: solve at 15 m/s (registry hint), chord 1 m, span 3 m,
    span axis y, mid-span station y = 0."""
    import numpy as np

    u_inf = 15.0
    far = farfield_pressure(
        staging / "internal.vtu", span_axis=1, station=0.0,
        body_center=(0.5, 0.0349), chord=1.0, plane_axes=(0, 2),
        probe_axis=2, probe_center=0.0349, span_extent=3.0)
    section = extract_section(
        staging / "body.vtp", span_axis=1, station=0.0, chord_axis=0,
        lift_axis=2, u_inf=u_inf, p_inf=far["p_inf"],
        start_half_width=0.02)

    xc, cp, upper = section["xc"], section["cp"], section["upper"]
    section_cn = normal_force_from_cp(xc[upper], cp[upper],
                                      xc[~upper], cp[~upper])
    alpha_ref = nearest_pinkerton_alpha(section_cn)
    column = PINKERTON_ALPHAS[alpha_ref]["column"]
    ref_upper, ref_lower = pinkerton_surfaces(column)

    edges = cosine_edges(72)
    cu_x, cu_v, _ = binned_curve(xc[upper], cp[upper], edges)
    cl_x, cl_v, _ = binned_curve(xc[~upper], cp[~upper], edges)
    stats_u = deviation_stats(ref_upper[:, 0], ref_upper[:, 1], cu_x, cu_v)
    stats_l = deviation_stats(ref_lower[:, 0], ref_lower[:, 1], cl_x, cl_v)
    # Split the comparison at 5 percent chord: the leading-edge region mixes
    # the steepest gradients with the largest sensitivity to the small lift
    # mismatch between the two wings, so the aft-body agreement is reported
    # separately as the cleaner like-for-like number.
    aft_u = ref_upper[ref_upper[:, 0] >= 0.05]
    aft_l = ref_lower[ref_lower[:, 0] >= 0.05]
    stats_u_aft = deviation_stats(aft_u[:, 0], aft_u[:, 1], cu_x, cu_v)
    stats_l_aft = deviation_stats(aft_l[:, 0], aft_l[:, 1], cl_x, cl_v)

    png = render_4412_figure(section, ref_upper, ref_lower, stats_u, stats_l,
                             alpha_ref=alpha_ref, section_cn=section_cn,
                             out_png=out_dir / "naca4412_wing_cp_validation.png")
    return {
        "body": "naca4412_wing", "u_inf": u_inf,
        "q_kinematic": 0.5 * u_inf * u_inf,
        "p_inf": far["p_inf"], "farfield": far,
        "alpha_geometric_deg": section["alpha_geometric_deg"],
        "chord": section["chord"], "band_half_width":
            section["band_half_width"], "faces": section["faces"],
        "stagnation_cp": section["stagnation_cp"],
        "stagnation_xc": section["stagnation_xc"],
        "cp_min_upper": float(cp[upper].min()),
        "xc_cp_min_upper": float(cu_x[int(np.argmin(cu_v))]),
        "section_cn": section_cn,
        "reference_alpha_deg": alpha_ref,
        "reference_cl": PINKERTON_ALPHAS[alpha_ref]["cl"],
        "reference_alpha_effective_deg":
            PINKERTON_ALPHAS[alpha_ref]["alpha_effective"],
        "reference_source": PINKERTON_SOURCE,
        "rms_upper": stats_u["rms"], "max_dev_upper": stats_u["max_abs"],
        "worst_xc_upper": stats_u["worst_xc"],
        "rms_lower": stats_l["rms"], "max_dev_lower": stats_l["max_abs"],
        "worst_xc_lower": stats_l["worst_xc"],
        "rms_upper_aft_5pct": stats_u_aft["rms"],
        "max_dev_upper_aft_5pct": stats_u_aft["max_abs"],
        "rms_lower_aft_5pct": stats_l_aft["rms"],
        "max_dev_lower_aft_5pct": stats_l_aft["max_abs"],
        "global_max_cp": section["global_max_cp"],
        "n_ref_stations": stats_u["n_stations"] + stats_l["n_stations"],
        "plot": png,
    }


def validate_naca0015(staging: Path, out_dir: Path) -> dict:
    """NACA 0015 sail: solve at 75 m/s, chord 1.2 m, span 1.8 m along z,
    mid-span station z = 0.9, lateral axis y."""
    import numpy as np

    u_inf = 75.0
    far = farfield_pressure(
        staging / "internal.vtu", span_axis=2, station=0.9,
        body_center=(0.6, 0.0), chord=1.2, plane_axes=(0, 1),
        probe_axis=1, probe_center=0.0, span_extent=1.8)
    section = extract_section(
        staging / "body.vtp", span_axis=2, station=0.9, chord_axis=0,
        lift_axis=1, u_inf=u_inf, p_inf=far["p_inf"],
        start_half_width=0.02)

    xc, cp, upper = section["xc"], section["cp"], section["upper"]
    edges = cosine_edges(72)
    sym = symmetry_residual(xc[upper], cp[upper], xc[~upper], cp[~upper],
                            edges)
    q = 0.5 * u_inf * u_inf
    png = render_0015_figure(section, sym, far, u_inf,
                             out_png=out_dir / "naca0015_sail_cp_validation.png")
    cx_all, cm_all, _ = binned_curve(xc, cp, edges)
    i_min = int(np.argmin(cm_all))
    return {
        "body": "naca0015_sail", "u_inf": u_inf, "q_kinematic": q,
        "p_inf": far["p_inf"], "farfield": far,
        "alpha_geometric_deg": section["alpha_geometric_deg"],
        "chord": section["chord"],
        "band_half_width": section["band_half_width"],
        "faces": section["faces"],
        "stagnation_cp": section["stagnation_cp"],
        "stagnation_xc": section["stagnation_xc"],
        "global_max_cp": section["global_max_cp"],
        "cp_min": float(cm_all[i_min]), "xc_cp_min": float(cx_all[i_min]),
        "cp_min_2d_band": NACA0015_2D_CPMIN_BAND,
        "xc_cp_min_2d_band": NACA0015_2D_CPMIN_XC,
        "symmetry_max_abs": sym["max_abs"],
        "symmetry_mean_abs": sym["mean_abs"],
        "symmetry_bins": sym["bins_compared"],
        "decay_cp_1c": far["decay_abs_p"]["1c"] / q,
        "decay_cp_2c": far["decay_abs_p"]["2c"] / q,
        "plot": png,
    }


def main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate the NACA pressure-slice fields against "
                    "invariants and published data.")
    parser.add_argument("--staging", required=True, type=Path,
                        help="directory holding naca4412/ and naca0015/ "
                             "subdirectories with body.vtp + internal.vtu")
    parser.add_argument("--out-dir", required=True, type=Path,
                        help="directory for the validation plots and JSON")
    args = parser.parse_args(argv)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    for name, sub, runner in (
            ("naca4412_wing", "naca4412", validate_naca4412),
            ("naca0015_sail", "naca0015", validate_naca0015)):
        results[name] = runner(args.staging / sub, args.out_dir)
        printable = {k: v for k, v in results[name].items()
                     if k not in ("farfield",)}
        print(json.dumps(printable, indent=2, default=str))

    out_json = args.out_dir / "validation_numbers.json"
    out_json.write_text(json.dumps(results, indent=2, default=str),
                        encoding="utf-8")
    print(f"numbers: {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
