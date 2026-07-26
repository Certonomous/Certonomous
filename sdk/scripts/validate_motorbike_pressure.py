"""Triple-check of the motorbike surface-pressure field before it stays on camera.

The owner reports the motorbike's pressure field "looks much different than
before". Two things changed underneath it, and this script verifies both
instead of asserting either:

  * the mesh was rebuilt on 2026-07-25 under the boundary-skewness gate
    (max skew 8.94 -> 3.99) and re-solved (Cd 0.4164 -> 0.4201), and
  * the painted-surface pipeline was fixed on 2026-07-25 (commit b203327):
    before the fix, a decimated body's display faces were painted with the
    FIRST-N source values (no correspondence), and the colour window came
    from that same truncated subset.

Checks, all quantitative, against the solver's own output (``foamToVTK``
boundary patches and volume file — exactly what the GUI paint and the
website slice consumed):

1. Physics invariants on the current field: kinematic wall pressure against
   the stagnation bound p_inf + U^2/2 (U = 20 m/s from the case's own
   force-coefficient header); top-percentile pressure faces clustered on
   forward-facing surfaces (face normals against the flow direction);
   strongest suction on crown/shoulder surfaces tangent to the flow;
   far-field decay of the slice-plane pressure toward p_inf.
2. Old vs new, separated into (a) physics — the re-solved field of the
   pre-remesh case compared against the current one on the same survey,
   and (b) rendering — the pre-fix display pipeline reproduced faithfully
   (same stride arithmetic as commit 7608e28) and scored against the fixed
   one by spatial autocorrelation of neighbouring display-face values.
3. Display-pipeline integrity: the motorbike IS decimated (101,137 source
   triangles -> 19,110 display faces, above the 30,000 threshold), so the
   served GUI JSON is recomputed from the case and compared value-for-value,
   and the aggregation is verified the way the sail's was: neighbouring
   display faces must correlate like a smooth physical field, not noise.

Pure computation lives at the top of the module so the unit tests exercise
it without any solver output on disk. Extraction reuses the machinery of
``validate_pressure_fields`` and ``chief_engineer.field_render`` read-only.
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))


def _load_sibling(name: str):
    spec = importlib.util.spec_from_file_location(
        name, Path(__file__).resolve().parent / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Case constants, read off the case's own files (documented, not guessed)
# ---------------------------------------------------------------------------
# postProcessing/forceCoeffs1/0/coefficient.dat header: magUInf 20, lRef 1.42,
# dragDir (1 0 0). 0.orig/include/initialConditions: flowVelocity (20 0 0).
U_INF = 20.0
Q_KINEMATIC = 0.5 * U_INF * U_INF          # 200 m^2/s^2
L_REF = 1.42                               # m, the case's own lRef
# Drag of the two staged solves, the mean over the final 60 iterations of each
# case's own postProcessing/forceCoeffs1/0/coefficient.dat: 0.415577 for the
# pre-remesh case study-motorBike-a7b3bf (the 0.4156 on Katie's round-2
# screenshot and the kOmegaSST closure in models/curriculum/uq-studies), and
# 0.420113 for the remeshed study-motorBike-54767f (the 0.4201 in the current
# study report).
CD_OLD = 0.4156
CD_NEW = 0.4201
FLOW_AXIS = 0                              # +x
SPAN_AXIS = 1                              # y
UP_AXIS = 2                                # z

# Named regions of the body, boxes in metres measured from the meshed body
# bounds (x -0.29..1.75, y +/-0.35, z 0..1.35). First match wins, so the
# brake-disc gap — a sub-box of the front wheel — is listed first: that is
# the one place the wall pressure spikes past the stagnation bound, inside
# the millimetre channel between the front brake disc and the fork/caliper.
MOTORBIKE_REGIONS = (
    ("front_brake_disc_gap", (-0.31, -0.09, 0.10), (0.00, -0.03, 0.50)),
    ("front_wheel", (-0.31, -0.40, 0.00), (0.28, 0.40, 0.62)),
    ("front_fairing_forks", (-0.16, -0.40, 0.62), (0.30, 0.40, 1.06)),
    ("rider_helmet_screen", (0.10, -0.40, 1.06), (1.10, 0.40, 1.40)),
    ("rider_torso_tank", (0.30, -0.40, 0.62), (1.10, 0.40, 1.06)),
)


# ---------------------------------------------------------------------------
# Pure computation (unit-tested; no I/O, no solver output needed)
# ---------------------------------------------------------------------------

def alignment_stats(normals, flow_axis: int = FLOW_AXIS):
    """How forward-facing a set of boundary faces is, from the patch normals.

    An OpenFOAM boundary patch winds its faces outward from the fluid, i.e.
    INTO the body, so a surface that faces the oncoming flow has a patch
    normal with a POSITIVE component along the flow axis. Returns the
    fraction of faces with that component positive, and the mean/median
    component — near +1 for a face-on stagnation surface.
    """
    import numpy as np

    n = np.asarray(normals, dtype=np.float64)
    if n.ndim != 2 or n.shape[0] == 0:
        raise ValueError("normals must be a non-empty (N, 3) array")
    dots = n[:, flow_axis]
    return {"frac_forward": float((dots > 0.0).mean()),
            "mean_dot": float(dots.mean()),
            "median_dot": float(np.median(dots)),
            "count": int(len(dots))}


def area_weighted_percentiles(values, areas, qs):
    """Percentiles of a per-face field weighted by face area.

    Sorting by value and interpolating on the cumulative area puts every
    quantile where the SURFACE sits, not where the mesh happens to be fine:
    an unweighted percentile over-counts the refined regions.
    """
    import numpy as np

    v = np.asarray(values, dtype=np.float64)
    a = np.asarray(areas, dtype=np.float64)
    if v.shape != a.shape or v.size == 0:
        raise ValueError("values and areas must be equal-length and non-empty")
    order = np.argsort(v)
    v = v[order]
    cum = np.cumsum(a[order])
    grid = (cum - 0.5 * a[order]) / cum[-1]
    return [float(np.interp(q / 100.0, grid, v)) for q in qs]


def binned_mean_profile(x, values, weights, edges):
    """Weighted mean of a field per x-bin. Returns (centers, means, counts)
    for non-empty bins, ascending."""
    import numpy as np

    x = np.asarray(x, dtype=np.float64)
    v = np.asarray(values, dtype=np.float64)
    w = np.asarray(weights, dtype=np.float64)
    edges = np.asarray(edges, dtype=np.float64)
    idx = np.digitize(x, edges) - 1
    centers, means, counts = [], [], []
    for b in range(len(edges) - 1):
        sel = idx == b
        n = int(sel.sum())
        if n == 0:
            continue
        centers.append(0.5 * (edges[b] + edges[b + 1]))
        means.append(float(np.average(v[sel], weights=w[sel])))
        counts.append(n)
    return (np.asarray(centers), np.asarray(means),
            np.asarray(counts, dtype=np.int64))


def profile_delta(centers_a, means_a, centers_b, means_b):
    """RMS and max |A - B| over the bins the two profiles share."""
    import numpy as np

    ca = np.asarray(centers_a)
    cb = np.asarray(centers_b)
    common, ia, ib = np.intersect1d(ca, cb, return_indices=True)
    if common.size == 0:
        return {"rms": float("nan"), "max_abs": float("nan"), "bins": 0,
                "worst_x": float("nan")}
    delta = np.asarray(means_a)[ia] - np.asarray(means_b)[ib]
    worst = int(np.argmax(np.abs(delta)))
    return {"rms": float(np.sqrt(np.mean(delta ** 2))),
            "max_abs": float(np.max(np.abs(delta))),
            "bins": int(common.size), "worst_x": float(common[worst])}


def face_edge_pairs(faces):
    """Pairs of face indices that share an edge, from triangle connectivity.

    Interior manifold edges pair exactly two faces; boundary edges (one
    face) contribute nothing; an edge listed more than twice keeps its
    first pairing only, which is the conservative choice for a correlation.
    """
    edges: dict[tuple[int, int], int] = {}
    pairs: list[tuple[int, int]] = []
    for fi, face in enumerate(faces):
        if len(face) < 3:
            continue
        for a, b in ((face[0], face[1]), (face[1], face[2]),
                     (face[2], face[0])):
            key = (a, b) if a < b else (b, a)
            other = edges.get(key)
            if other is None:
                edges[key] = fi
            elif other >= 0:
                pairs.append((other, fi))
                edges[key] = -1
    return pairs


def neighbor_correlation(faces, values):
    """Pearson correlation of a per-face field across shared-edge neighbours.

    A physical surface field is spatially smooth: adjacent faces carry
    nearly the same pressure, so r approaches 1. Values assigned to faces
    with no spatial correspondence (the pre-fix truncation paint) decorrelate;
    a random permutation is indistinguishable from 0. Returns (r, n_pairs).
    """
    import numpy as np

    pairs = face_edge_pairs(faces)
    if not pairs:
        return float("nan"), 0
    idx = np.asarray(pairs)
    v = np.asarray(values, dtype=np.float64)
    a, b = v[idx[:, 0]], v[idx[:, 1]]
    if a.std() == 0.0 or b.std() == 0.0:
        return float("nan"), int(len(pairs))
    return float(np.corrcoef(a, b)[0, 1]), int(len(pairs))


def percentile_window(values):
    """The display pipeline's robust colour window: the 2nd/98th entries of
    the sorted list, by the exact index arithmetic of ``_attach_field``."""
    if not len(values):
        raise ValueError("values must be non-empty")
    ordered = sorted(values)
    lo = ordered[max(0, int(0.02 * len(ordered)))]
    hi = ordered[min(len(ordered) - 1, int(0.98 * len(ordered)))]
    return float(lo), float(hi)


def legacy_display_values(all_face_values, triangles_total: int,
                          n_display_faces: int):
    """Reproduce the pre-fix (commit 7608e28) display paint, faithfully.

    The old ``_attach_field`` computed ``stride = max(1, total //
    triangles_total)`` — always 1, since ``triangles_total`` IS the source
    total — then took ``face_values[:n_display]``: the first N source values
    laid onto N decimated display faces that have no relationship to them.
    Its colour window then came from that truncated subset. Returns
    (values, lo, hi) exactly as the old pipeline displayed them.
    """
    total = len(all_face_values)
    stride = max(1, total // max(1, triangles_total))
    sampled = list(all_face_values[::stride][:n_display_faces])
    if not sampled:
        raise ValueError("no display values to sample")
    lo, hi = percentile_window(sampled)
    return sampled, lo, hi


def region_shares(centroids, mask, regions=MOTORBIKE_REGIONS):
    """Share of the selected faces inside each named box; first match wins.

    ``regions`` is a sequence of (name, (xlo, ylo, zlo), (xhi, yhi, zhi)).
    Returns {name: fraction} including an ``elsewhere`` bucket; fractions
    sum to 1 over the selected faces.
    """
    import numpy as np

    c = np.asarray(centroids, dtype=np.float64)[np.asarray(mask, dtype=bool)]
    shares = {name: 0 for name, _, _ in regions}
    shares["elsewhere"] = 0
    unclaimed = np.ones(len(c), dtype=bool)
    for name, lo, hi in regions:
        inside = unclaimed.copy()
        for axis in range(3):
            inside &= (c[:, axis] >= lo[axis]) & (c[:, axis] <= hi[axis])
        shares[name] = int(inside.sum())
        unclaimed &= ~inside
    shares["elsewhere"] = int(unclaimed.sum())
    n = max(1, len(c))
    return {name: count / n for name, count in shares.items()}


def component_sizes(vertices, faces, quantum_fraction: float = 1e-5):
    """Connected-component face counts, position-quantized like the GUI.

    Mirrors ``dropOrphanIslands`` in ``control_room.html``: vertices are
    quantized to 1e-5 of the bounding span (so vertex soups unify), then a
    union-find over the triangle edges groups the faces. Returns the face
    count per component, descending, and the per-face component root ids.
    """
    if not faces:
        return [], []
    spans = []
    for axis in range(3):
        coords = [v[axis] for v in vertices]
        spans.append(max(coords) - min(coords))
    q = (max(spans) or 1.0) * quantum_fraction
    key: dict[tuple[int, int, int], int] = {}
    vid = []
    for v in vertices:
        k = (round(v[0] / q), round(v[1] / q), round(v[2] / q))
        vid.append(key.setdefault(k, len(key)))
    parent = list(range(len(key)))

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for f in faces:
        parent[find(vid[f[0]])] = find(vid[f[1]])
        parent[find(vid[f[1]])] = find(vid[f[2]])
    roots = [find(vid[f[0]]) for f in faces]
    sizes: dict[int, int] = {}
    for r in roots:
        sizes[r] = sizes.get(r, 0) + 1
    return sorted(sizes.values(), reverse=True), roots


def drop_orphan_islands(vertices, faces, values=None, frac: float = 0.01,
                        cap_frac: float = 0.03):
    """Python mirror of the GUI's display-only orphan-island filter.

    Step for step the same as ``dropOrphanIslands`` in ``control_room.html``,
    including the early-out guards, the 1%-of-faces component threshold, the
    3% total cap that stops real geometry ever being cut, the value filter
    that runs IN THE SAME LOOP as the face filter, and the vertex re-pack
    that keeps auto-framing off the dropped island. Returns a dict with the
    filtered display mesh plus ``kept`` (source face index per output face),
    so the caller can prove the surviving faces still carry their own values
    and their own corner positions.
    """
    n_faces = len(faces)
    identity = {"vertices": list(vertices), "faces": list(faces),
                "values": None if values is None else list(values),
                "kept": list(range(n_faces)), "dropped": 0,
                "component_sizes": [], "filtered": False}
    if values is not None and len(values) != n_faces:
        raise ValueError("values must be one per face")
    # The GUI leaves tiny payloads alone rather than reason about them.
    if len(vertices) < 3 or n_faces < 8:
        return identity
    sizes, roots = component_sizes(vertices, faces)
    identity["component_sizes"] = sizes
    if len(sizes) < 2:
        return identity
    counts: dict[int, int] = {}
    for r in roots:
        counts[r] = counts.get(r, 0) + 1
    cut = frac * n_faces
    doomed = {r for r, n in counts.items() if n < cut}
    doomed_faces = sum(counts[r] for r in doomed)
    if not doomed or doomed_faces > cap_frac * n_faces:
        return identity

    kept: list[int] = []
    kept_faces: list[list[int]] = []
    kept_values: list[float] | None = [] if values is not None else None
    for i in range(n_faces):
        if roots[i] in doomed:
            continue
        kept.append(i)
        kept_faces.append(list(faces[i]))
        if kept_values is not None:
            kept_values.append(values[i])
    # Re-pack the vertex list exactly as the GUI does.
    remap: dict[int, int] = {}
    out_vertices: list = []
    out_faces: list[list[int]] = []
    for face in kept_faces:
        row = []
        for ix in face:
            nix = remap.get(ix)
            if nix is None:
                nix = len(out_vertices)
                out_vertices.append(vertices[ix])
                remap[ix] = nix
            row.append(nix)
        out_faces.append(row)
    return {"vertices": out_vertices, "faces": out_faces,
            "values": kept_values, "kept": kept, "dropped": doomed_faces,
            "component_sizes": sizes, "filtered": True}


def orphan_filter_alignment(vertices, faces, values, filtered):
    """Prove the display filter left the survivors' data untouched.

    For every output face, its per-face value must still be the value of the
    source face it came from, and its three corners must still sit at the
    same positions after the vertex re-pack. Returns the two booleans and
    the worst position error seen, so a silent off-by-one in either the
    value filter or the re-map cannot pass as 'aligned'.
    """
    kept = filtered["kept"]
    out_faces = filtered["faces"]
    out_vertices = filtered["vertices"]
    out_values = filtered["values"]
    values_ok = (out_values is None) if values is None else (
        len(out_values) == len(kept)
        and all(out_values[k] == values[src] for k, src in enumerate(kept)))
    worst = 0.0
    geometry_ok = len(out_faces) == len(kept)
    if geometry_ok:
        for k, src in enumerate(kept):
            for out_ix, src_ix in zip(out_faces[k], faces[src]):
                for axis in range(3):
                    d = abs(out_vertices[out_ix][axis] - vertices[src_ix][axis])
                    if d > worst:
                        worst = d
        geometry_ok = worst == 0.0
    return {"values_aligned": bool(values_ok),
            "corner_positions_preserved": bool(geometry_ok),
            "worst_corner_error": float(worst),
            "faces_in": len(faces), "faces_out": len(out_faces),
            "dropped": filtered["dropped"]}


def exceedance_stats(p, areas, centroids, limit: float):
    """Faces whose wall pressure exceeds ``limit``: count, area, area share,
    and bounding box — the evidence for 'where and how much'."""
    import numpy as np

    p = np.asarray(p, dtype=np.float64)
    a = np.asarray(areas, dtype=np.float64)
    c = np.asarray(centroids, dtype=np.float64)
    over = p > limit
    if not over.any():
        return {"count": 0, "area_m2": 0.0, "area_fraction": 0.0,
                "bbox": None, "max_p": float(p.max())}
    return {"count": int(over.sum()),
            "area_m2": float(a[over].sum()),
            "area_fraction": float(a[over].sum() / a.sum()),
            "bbox": [[float(v) for v in c[over].min(axis=0)],
                     [float(v) for v in c[over].max(axis=0)]],
            "max_p": float(p.max())}


# ---------------------------------------------------------------------------
# Extraction (reuses validate_pressure_fields + field_render, read-only)
# ---------------------------------------------------------------------------

def merge_body_walls(case_dir: Path):
    """Merge every body patch of a staged case into one wall survey.

    Patch selection is the display pipeline's own (``_body_patches``), so
    the survey covers exactly the surface that is painted. Returns a dict of
    per-face centroids, patch normals (into-body winding), areas, and the
    solver's cell-centred wall pressure.
    """
    import numpy as np

    from chief_engineer import field_render as fr

    vpf = _load_sibling("validate_pressure_fields")
    patches = fr._body_patches(sorted(Path(case_dir).glob("*.vtp")))
    if not patches:
        raise ValueError(f"no body patches under {case_dir}")
    cs, ns, as_, ps = [], [], [], []
    for patch in patches:
        vertices, polys, values = vpf.read_patch_polys(patch, "p")
        c, n, a = vpf.polygon_geometry(vertices, polys)
        cs.append(c)
        ns.append(n)
        as_.append(a)
        ps.append(values)
    return {"centroids": np.vstack(cs), "normals": np.vstack(ns),
            "areas": np.concatenate(as_), "p": np.concatenate(ps),
            "patches": [p.stem for p in patches]}


def farfield_and_decay(vtu_path: Path, *, body_center_x: float,
                       body_center_z: float, length: float = L_REF):
    """p_inf from the mid-span plane and the 3D decay of |p - p_inf|.

    p_inf is the median cell pressure beyond 3 body lengths in-plane radius
    on a slab about y = 0 (the published slice's own plane); the slab widens
    until the far annulus is populated, because the tutorial's outer cells
    are metre-scale. Median, so the wake cells inside the annulus cannot
    drag it. Decay is then read on full 3D spherical shells at 1, 2 and 3
    body lengths, restricted to the upstream/lateral hemisphere (dx <= 0,
    excluding the wake, which decays on its own longer scale) and above the
    ground boundary layer (z > 0.1 m).
    """
    import numpy as np

    from chief_engineer import field_render as fr

    volume = fr.read_volume_field(vtu_path, "p")
    if volume is None:
        raise ValueError(f"no volume field in {vtu_path}")
    points, connectivity, offsets, values = volume
    centres, _ = fr.cell_centres(points, connectivity, offsets)
    values = values[:len(centres)]

    half = 0.05
    for _ in range(6):
        slab = np.abs(centres[:, SPAN_AXIS]) <= half
        radial = np.hypot(centres[slab, FLOW_AXIS] - body_center_x,
                          centres[slab, UP_AXIS] - body_center_z)
        if int((radial > 3.0 * length).sum()) >= 500:
            break
        half *= 2.0
    far = radial > 3.0 * length
    p_inf = float(np.median(values[slab][far]))

    center = np.array([body_center_x, 0.0, body_center_z])
    rel = centres - center
    r = np.linalg.norm(rel, axis=1)
    keep = (rel[:, FLOW_AXIS] <= 0.0) & (centres[:, UP_AXIS] > 0.1)
    decay = {}
    for label, dist in (("1L", 1.0), ("2L", 2.0), ("3L", 3.0)):
        shell = keep & (np.abs(r - dist * length) <= 0.15 * length)
        decay[label] = {
            "mean_abs_cp": (float(np.mean(np.abs(values[shell] - p_inf)))
                            / Q_KINEMATIC if shell.any() else float("nan")),
            "cells": int(shell.sum())}
    return {"p_inf": p_inf, "slab_half_width": float(half),
            "slab_cells": int(slab.sum()), "far_cells": int(far.sum()),
            "decay": decay}


def painted_payload(case_dir: Path):
    """The display payload exactly as the GUI pipeline builds it, plus the
    merged per-triangle source values (for the legacy reproduction)."""
    from chief_engineer import field_render as fr

    patches = fr._body_patches(sorted(Path(case_dir).glob("*.vtp")))
    payload = fr.load_field_surface(patches, field="p", name="motorBike")
    merged: list[float] = []
    for patch in patches:
        try:
            _, faces, vals = fr._read_patch(patch, "p")
        except Exception:
            continue
        merged.extend(vals if (vals and len(vals) == len(faces))
                      else [0.0] * len(faces))
    return payload, merged


# ---------------------------------------------------------------------------
# Evidence figure
# ---------------------------------------------------------------------------

def _paint_panel(ax, payload, values01, *, title, note, INK, MUTED, DIM,
                 note_corner="lower right"):
    """One painted-body panel: display mesh projected to x-z, far side first."""
    import numpy as np
    from matplotlib.collections import PolyCollection
    from matplotlib import colormaps

    verts = np.asarray(payload["vertices"], dtype=np.float64)
    faces = np.asarray(payload["faces"], dtype=np.int64)
    vals = np.asarray(values01, dtype=np.float64)
    order = np.argsort(verts[faces].mean(axis=1)[:, SPAN_AXIS])
    tri_xz = verts[faces][:, :, [FLOW_AXIS, UP_AXIS]][order]
    colors = colormaps["coolwarm"](vals[order])
    ax.add_collection(PolyCollection(tri_xz, facecolors=colors,
                                     edgecolors="none"))
    ax.set_xlim(-0.55, 2.0)
    ax.set_ylim(-0.04, 1.62)
    ax.set_aspect("equal")
    ax.grid(False)
    ax.set_title(title, color=INK, fontsize=11, loc="left", pad=8)
    if note_corner == "upper left":
        xy, ha, va = (0.01, 0.99), "left", "top"
    else:
        xy, ha, va = (0.99, 0.02), "right", "bottom"
    ax.annotate(note, xy=xy, xycoords="axes fraction", ha=ha, va=va,
                fontsize=9.0, color=INK,
                bbox={"boxstyle": "round,pad=0.4", "facecolor": "#0f1315",
                      "edgecolor": DIM, "alpha": 0.9})
    for spine in ax.spines.values():
        spine.set_color(DIM)
    ax.tick_params(colors=MUTED, labelsize=8)


def render_evidence_figure(new_wall, results, payload_new, payload_old,
                           legacy_vals01, out_png):
    """Four panels: the checked field with the checked regions marked; the
    pre-fix paint reproduced; old-vs-new surface Cp; far-field decay."""
    import numpy as np

    from chief_engineer.plot_theme import (DIM, INK, LIVE, MUTED, TREND,
                                           VALID, _pyplot, style_axes)

    plt = _pyplot()
    fig, axes = plt.subplots(2, 2, figsize=(13.6, 9.4), dpi=150,
                             gridspec_kw={"height_ratios": [1.5, 1.0],
                                          "hspace": 0.30, "wspace": 0.16})
    (ax_a, ax_b), (ax_c, ax_d) = axes

    inv = results["invariants"]
    # Panel A: current paint with the checked regions annotated.
    _paint_panel(
        ax_a, payload_new, payload_new["field"]["values"],
        title="Current paint (fixed pipeline), checked regions",
        note=(f"neighbour-face correlation r = "
              f"{results['rendering']['r_new_pipeline']:.2f}\n"
              f"colour window [{payload_new['field']['min']:.0f}, "
              f"{payload_new['field']['max']:.0f}] m$^2$/s$^2$"),
        INK=INK, MUTED=MUTED, DIM=DIM, note_corner="upper left")
    c = new_wall["centroids"]
    p = new_wall["p"]
    hi_thr = np.quantile(p, 0.995)
    lo_thr = np.quantile(p, 0.005)
    stag = p >= hi_thr
    suck = p <= lo_thr
    ax_a.plot(c[stag, FLOW_AXIS], c[stag, UP_AXIS], linestyle="none",
              marker="o", markersize=3.4, markerfacecolor="none",
              markeredgecolor="#ffd166", markeredgewidth=0.8,
              label="top 0.5% pressure (stagnation)")
    ax_a.plot(c[suck, FLOW_AXIS], c[suck, UP_AXIS], linestyle="none",
              marker="v", markersize=3.4, markerfacecolor="none",
              markeredgecolor="#4cc9f0", markeredgewidth=0.8,
              label="bottom 0.5% pressure (suction)")
    gap = inv["exceedance"]["bbox"]
    if gap:
        gx = 0.5 * (gap[0][0] + gap[1][0])
        gz = 0.5 * (gap[0][2] + gap[1][2])
        ax_a.annotate(
            f"1 face > bound: brake-disc gap\np/ρ = "
            f"{inv['exceedance']['max_p']:.0f} "
            f"({inv['exceedance']['area_fraction'] * 100:.4f}% of area)",
            xy=(gx, gz), xytext=(0.44, 0.03), fontsize=8.5, color=INK,
            bbox={"boxstyle": "round,pad=0.3", "facecolor": "#0f1315",
                  "edgecolor": DIM, "alpha": 0.9},
            arrowprops={"arrowstyle": "-", "color": MUTED, "linewidth": 0.9})
    for text, xy, xytext in (
            ("front wheel", (-0.27, 0.30), (-0.52, 0.55)),
            ("fairing nose", (-0.07, 0.79), (-0.50, 1.02)),
            ("visor / screen", (0.42, 1.13), (-0.34, 1.14)),
            ("helmet crown + shoulders\n(suction)", (0.62, 1.32),
             (1.02, 1.46))):
        ax_a.annotate(text, xy=xy, xytext=xytext, fontsize=8.5, color=MUTED,
                      arrowprops={"arrowstyle": "-", "color": MUTED,
                                  "linewidth": 0.8, "alpha": 0.8})
    leg = ax_a.legend(frameon=False, fontsize=8.5, loc="upper right",
                      bbox_to_anchor=(1.0, 0.82))
    for t in leg.get_texts():
        t.set_color(INK)

    # Panel B: the pre-fix paint, reproduced from the pre-remesh case.
    _paint_panel(
        ax_b, payload_old, legacy_vals01,
        title="Pre-fix pipeline reproduced (before 2026-07-25 14:26)",
        note=(f"neighbour-face correlation r = "
              f"{results['rendering']['r_legacy_pipeline']:.2f}"
              f" (random paint = 0)\ncolour window "
              f"[{results['rendering']['legacy_window'][0]:.0f}, "
              f"{results['rendering']['legacy_window'][1]:.0f}] m$^2$/s$^2$ "
              "from the truncated subset"),
        INK=INK, MUTED=MUTED, DIM=DIM)

    # Panel C: surface pressure old vs new solve, area-weighted profile.
    prof = results["physics_old_vs_new"]
    ax_c.plot(prof["centers"], prof["cp_new"], color=LIVE, linewidth=2.0,
              label=f"new mesh (skew 3.99, Cd {CD_NEW:.4f})")
    ax_c.plot(prof["centers_old"], prof["cp_old"], color=TREND,
              linewidth=2.0, linestyle=(0, (5, 4)),
              label=f"old mesh (skew 8.94, Cd {CD_OLD:.4f})")
    ax_c.axhline(0.0, color=DIM, linewidth=0.9)
    ax_c.annotate(
        (f"RMS ΔCp = {prof['delta']['rms']:.4f}, "
         f"max {prof['delta']['max_abs']:.4f}\n"
         f"colour-window shift < "
         f"{prof['window_shift_percent']:.1f}% of span"),
        xy=(0.97, 0.06), xycoords="axes fraction", ha="right", va="bottom",
        fontsize=9.5, color=INK, weight="bold",
        bbox={"boxstyle": "round,pad=0.4", "facecolor": "#0f1315",
              "edgecolor": DIM, "alpha": 0.9})
    style_axes(ax_c, "streamwise position x [m]",
               "area-weighted mean surface $C_p$",
               "Remesh physics change: barely measurable")
    leg = ax_c.legend(frameon=False, fontsize=8.5, loc="upper right")
    for t in leg.get_texts():
        t.set_color(INK)

    # Panel D: invariants — stagnation bound and far-field decay.
    far = results["farfield"]
    labels = ["1 L", "2 L", "3 L"]
    vals = [far["decay"][k]["mean_abs_cp"] for k in ("1L", "2L", "3L")]
    bars = ax_d.bar(range(len(vals)), vals, width=0.5, color=VALID,
                    alpha=0.85)
    for rect, v in zip(bars, vals):
        ax_d.annotate(f"{v:.4f}", xy=(rect.get_x() + rect.get_width() / 2,
                                      rect.get_height()),
                      xytext=(0, 4), textcoords="offset points", ha="center",
                      fontsize=9.5, color=INK, weight="bold")
    ax_d.set_xticks(range(len(vals)), labels)
    ax_d.annotate(
        (f"stagnation bound p$_\\infty$ + U$^2$/2 = "
         f"{inv['stagnation_limit']:.1f} m$^2$/s$^2$\n"
         f"max wall p/ρ outside brake gap = "
         f"{inv['max_p_outside_gap']:.1f}  "
         f"(C$_p$ {inv['cp_max_outside_gap']:.3f} ≤ 1)\n"
         f"stagnation faces forward-facing: "
         f"{inv['stagnation_alignment']['frac_forward'] * 100:.1f}%"),
        xy=(0.97, 0.95), xycoords="axes fraction", ha="right", va="top",
        fontsize=9.5, color=INK, weight="bold",
        bbox={"boxstyle": "round,pad=0.5", "facecolor": "#0f1315",
              "edgecolor": DIM, "alpha": 0.9})
    style_axes(ax_d, "spherical shell radius, body lengths (L = 1.42 m)",
               "mean |$C_p$| in the shell",
               "Far-field decay toward p$_\\infty$ (upstream hemisphere)")
    ax_d.set_ylim(0, max(vals) * 2.1)

    note = ("Solver output read directly (foamToVTK boundary + volume, the "
            "same files the GUI paint and website slice consumed). U = 20 "
            "m/s from the case's own coefficient header; p kinematic "
            "(m2/s2).\nOld case study-motorBike-a7b3bf (pre-remesh, skew "
            "8.94), new case study-motorBike-54767f (skewness-gated remesh, "
            "skew 3.99).")
    fig.text(0.01, 0.006, note, color=MUTED, fontsize=8.0,
             family="monospace", va="bottom")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    out_png = Path(out_png)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png)
    plt.close(fig)
    return str(out_png)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(staging: Path, served_json: Path, out_dir: Path) -> dict:
    import numpy as np

    results: dict = {
        "u_inf": U_INF, "q_kinematic": Q_KINEMATIC, "l_ref": L_REF,
        # Read off the two cases' own polyMesh/owner headers, checkMesh logs
        # and coefficient.dat files; carried here so the verdict cites one
        # place. The geometry is byte-identical between them — only the mesh
        # was rebuilt under the boundary-skewness gate.
        "case_provenance": {
            "old_case": "study-motorBike-a7b3bf",
            "new_case": "study-motorBike-54767f",
            "cells_old": 353578, "cells_new": 353688,
            "max_skewness_old": 8.94, "max_skewness_new": 3.99457,
            "cd_old": CD_OLD, "cd_new": CD_NEW,
            "cd_shift_percent": 100.0 * (CD_NEW / CD_OLD - 1.0),
            "geometry_rescaled": False,
        }}

    new_wall = merge_body_walls(staging / "new")
    old_wall = merge_body_walls(staging / "old")

    far = farfield_and_decay(
        staging / "new" / "internal.vtu",
        body_center_x=float(new_wall["centroids"][:, FLOW_AXIS].mean()),
        body_center_z=float(new_wall["centroids"][:, UP_AXIS].mean()))
    results["farfield"] = far
    p_inf = far["p_inf"]

    far_old = farfield_and_decay(
        staging / "old" / "internal.vtu",
        body_center_x=float(old_wall["centroids"][:, FLOW_AXIS].mean()),
        body_center_z=float(old_wall["centroids"][:, UP_AXIS].mean()))
    results["farfield_old"] = far_old

    # ---- Invariant 1: stagnation bound --------------------------------
    p = new_wall["p"]
    c = new_wall["centroids"]
    limit = p_inf + Q_KINEMATIC
    exc = exceedance_stats(p, new_wall["areas"], c, limit)
    gap_name, gap_lo, gap_hi = MOTORBIKE_REGIONS[0]
    in_gap = np.ones(len(c), dtype=bool)
    for axis in range(3):
        in_gap &= (c[:, axis] >= gap_lo[axis]) & (c[:, axis] <= gap_hi[axis])
    max_outside = float(p[~in_gap].max())
    results["invariants"] = {
        "p_inf": p_inf,
        "stagnation_limit": limit,
        "max_wall_p": float(p.max()),
        "cp_max": float((p.max() - p_inf) / Q_KINEMATIC),
        "exceedance": exc,
        "max_p_outside_gap": max_outside,
        "cp_max_outside_gap": float((max_outside - p_inf) / Q_KINEMATIC),
        "gap_faces": int(in_gap.sum()),
        "wall_faces": int(len(p)),
        "wetted_area_m2": float(new_wall["areas"].sum()),
    }

    # ---- Invariant 2 and 3: where the extremes sit ---------------------
    hi_thr = float(np.quantile(p, 0.995))
    lo_thr = float(np.quantile(p, 0.005))
    stag = p >= hi_thr
    suck = p <= lo_thr
    inv = results["invariants"]
    inv["stagnation_alignment"] = alignment_stats(new_wall["normals"][stag])
    inv["stagnation_threshold_cp"] = (hi_thr - p_inf) / Q_KINEMATIC
    inv["stagnation_regions"] = region_shares(c, stag)
    inv["suction_threshold_cp"] = (lo_thr - p_inf) / Q_KINEMATIC
    inv["suction_regions"] = region_shares(c, suck)
    inv["suction_alignment"] = alignment_stats(new_wall["normals"][suck])
    inv["suction_median_abs_flow_dot"] = float(
        np.median(np.abs(new_wall["normals"][suck][:, FLOW_AXIS])))

    # ---- Old vs new physics -------------------------------------------
    edges = np.linspace(-0.30, 1.76, 42)
    cn, mn, _ = binned_mean_profile(
        c[:, FLOW_AXIS], (p - p_inf) / Q_KINEMATIC, new_wall["areas"], edges)
    co, mo, _ = binned_mean_profile(
        old_wall["centroids"][:, FLOW_AXIS],
        (old_wall["p"] - far_old["p_inf"]) / Q_KINEMATIC,
        old_wall["areas"], edges)
    delta = profile_delta(cn, mn, co, mo)
    pct_new = area_weighted_percentiles(
        (p - p_inf) / Q_KINEMATIC, new_wall["areas"], [2, 25, 50, 75, 98])
    pct_old = area_weighted_percentiles(
        (old_wall["p"] - far_old["p_inf"]) / Q_KINEMATIC,
        old_wall["areas"], [2, 25, 50, 75, 98])
    results["physics_old_vs_new"] = {
        "centers": [float(v) for v in cn], "cp_new": [float(v) for v in mn],
        "centers_old": [float(v) for v in co],
        "cp_old": [float(v) for v in mo],
        "delta": delta,
        "area_weighted_cp_percentiles_new": pct_new,
        "area_weighted_cp_percentiles_old": pct_old,
    }

    # ---- Rendering: served JSON, legacy reproduction, autocorrelation --
    payload_new, _merged_new = painted_payload(staging / "new")
    payload_old, merged_old = painted_payload(staging / "old")

    served = json.loads(Path(served_json).read_text(encoding="utf-8"))
    sv = np.asarray(served["field"]["values"], dtype=np.float64)
    nv = np.asarray(payload_new["field"]["values"], dtype=np.float64)
    served_match = (
        len(sv) == len(nv)
        and served["triangles_shown"] == payload_new["triangles_shown"]
        and math.isclose(served["field"]["min"], payload_new["field"]["min"],
                         rel_tol=1e-9)
        and math.isclose(served["field"]["max"], payload_new["field"]["max"],
                         rel_tol=1e-9))
    max_diff = float(np.max(np.abs(sv - nv))) if len(sv) == len(nv) else None

    legacy_vals, legacy_lo, legacy_hi = legacy_display_values(
        merged_old, payload_old["triangles_total"],
        payload_old["triangles_shown"])
    span = (legacy_hi - legacy_lo) or 1.0
    legacy01 = [min(1.0, max(0.0, (v - legacy_lo) / span))
                for v in legacy_vals]

    r_new, pairs = neighbor_correlation(payload_new["faces"],
                                        payload_new["field"]["values"])
    r_old_fixed, _ = neighbor_correlation(payload_old["faces"],
                                          payload_old["field"]["values"])
    r_legacy, _ = neighbor_correlation(payload_old["faces"], legacy_vals)
    rng = np.random.default_rng(0)
    r_shuffled, _ = neighbor_correlation(
        payload_new["faces"], rng.permutation(nv))

    new_win = (payload_new["field"]["min"], payload_new["field"]["max"])
    old_win = (payload_old["field"]["min"], payload_old["field"]["max"])
    win_span = new_win[1] - new_win[0]
    results["physics_old_vs_new"]["window_shift_percent"] = 100.0 * max(
        abs(new_win[0] - old_win[0]), abs(new_win[1] - old_win[1])) / win_span
    results["rendering"] = {
        "triangles_total": payload_new["triangles_total"],
        "triangles_shown": payload_new["triangles_shown"],
        "decimated": payload_new["triangles_total"] > 30000,
        "served_json_matches_recompute": bool(served_match),
        "served_json_max_value_diff": max_diff,
        "r_new_pipeline": r_new,
        "r_old_case_new_pipeline": r_old_fixed,
        "r_legacy_pipeline": r_legacy,
        "r_shuffled_baseline": r_shuffled,
        "neighbour_pairs": pairs,
        "window_new_pipeline": list(new_win),
        "window_old_case_new_pipeline": list(old_win),
        "legacy_window": [legacy_lo, legacy_hi],
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    png = render_evidence_figure(new_wall, results, payload_new, payload_old,
                                 legacy01,
                                 out_dir / "motorBike_cp_validation.png")
    results["plot"] = png
    out_json = out_dir / "motorbike_validation_numbers.json"
    out_json.write_text(json.dumps(results, indent=2, default=str),
                        encoding="utf-8")
    results["numbers"] = str(out_json)
    return results


# ---------------------------------------------------------------------------
# B-52 (same discipline; the body's own axes and change causes)
# ---------------------------------------------------------------------------
# Case setup, read off the cases themselves: magUInf 100 m/s along +z
# (dragDir (0 0 1)), nu 1.5e-5, single `body` patch. Old case lRef 50 m /
# Aref 638.323 m^2 (generic length basis); new case lRef 48.5 m / Aref
# 600.598 m^2 (published length) — the meshed geometry itself is rescaled by
# exactly 0.97, so Re drops from 3.33e8 to 3.23e8 (-3.0%).
B52_U_INF = 100.0
B52_Q = 0.5 * B52_U_INF * B52_U_INF        # 5000 m^2/s^2
B52_FLOW_AXIS = 2                          # +z
B52_LENGTH_NEW = 48.5
B52_LENGTH_OLD = 50.0
B52_NU = 1.5e-5
# Mean Cd over the final 60 iterations of each case's own coefficient.dat.
B52_CD_OLD = 0.0464
B52_CD_NEW = 0.0472

# Named regions in the NEW case's coordinates (body x 27.8..83.4 span,
# y 43.9..55.7 height, z 0.02..48.3 length, nose at z = 0). First match wins.
B52_REGIONS = (
    ("nose_cockpit", (49.0, 43.0, 0.0), (62.0, 56.5, 7.0)),
    ("tail_fin", (49.0, 43.0, 36.0), (62.0, 56.5, 49.0)),
    ("wings_and_pods", (27.0, 43.0, 7.0), (49.0, 56.5, 36.0)),
    ("wings_and_pods_stbd", (62.0, 43.0, 7.0), (84.0, 56.5, 36.0)),
    ("fuselage_mid", (49.0, 43.0, 7.0), (62.0, 56.5, 36.0)),
)


def b52_farfield_and_decay(vtu_path: Path, *, body_center, length: float):
    """p_inf and 3D shell decay for a free-air body (no ground plane).

    p_inf is the median cell pressure beyond 3 body lengths radius; decay is
    the mean |p - p_inf| on spherical shells at 1, 2 and 3 lengths over the
    upstream hemisphere (dz <= 0, excluding the wake).
    """
    import numpy as np

    from chief_engineer import field_render as fr

    volume = fr.read_volume_field(vtu_path, "p")
    if volume is None:
        raise ValueError(f"no volume field in {vtu_path}")
    points, connectivity, offsets, values = volume
    centres, _ = fr.cell_centres(points, connectivity, offsets)
    values = values[:len(centres)]
    rel = centres - np.asarray(body_center, dtype=np.float64)
    r = np.linalg.norm(rel, axis=1)
    far = r > 3.0 * length
    p_inf = float(np.median(values[far]))
    upstream = rel[:, B52_FLOW_AXIS] <= 0.0
    decay = {}
    for label, dist in (("1L", 1.0), ("2L", 2.0), ("3L", 3.0)):
        shell = upstream & (np.abs(r - dist * length) <= 0.15 * length)
        decay[label] = {
            "mean_abs_cp": (float(np.mean(np.abs(values[shell] - p_inf)))
                            / B52_Q if shell.any() else float("nan")),
            "cells": int(shell.sum())}
    return {"p_inf": p_inf, "far_cells": int(far.sum()), "decay": decay}


def _b52_planform_panel(ax, payload, values01, *, title, note, INK, MUTED,
                        DIM, highlight=None):
    """Painted planform (span x against length z), highest surfaces last."""
    import numpy as np
    from matplotlib import colormaps
    from matplotlib.collections import PolyCollection

    verts = np.asarray(payload["vertices"], dtype=np.float64)
    faces = np.asarray(payload["faces"], dtype=np.int64)
    vals = np.asarray(values01, dtype=np.float64)
    order = np.argsort(verts[faces].mean(axis=1)[:, 1])
    tri = verts[faces][:, :, [0, 2]][order]
    colors = colormaps["coolwarm"](vals[order])
    ax.add_collection(PolyCollection(tri, facecolors=colors,
                                     edgecolors="none"))
    if highlight is not None and len(highlight):
        hi_tri = verts[faces[highlight]][:, :, [0, 2]]
        ax.add_collection(PolyCollection(
            hi_tri, facecolors="none", edgecolors="#ffd166", linewidths=1.2))
    ax.set_xlim(18.0, 90.0)
    ax.set_ylim(-4.0, 54.0)
    ax.set_aspect("equal")
    ax.grid(False)
    ax.invert_yaxis()  # nose (z = 0) at the top, flow down the page
    ax.set_title(title, color=INK, fontsize=11, loc="left", pad=8)
    ax.annotate(note, xy=(0.99, 0.01), xycoords="axes fraction", ha="right",
                va="bottom", fontsize=9.0, color=INK,
                bbox={"boxstyle": "round,pad=0.4", "facecolor": "#0f1315",
                      "edgecolor": DIM, "alpha": 0.9})
    for spine in ax.spines.values():
        spine.set_color(DIM)
    ax.tick_params(colors=MUTED, labelsize=8)


def render_b52_figure(new_wall, results, payload_new, wire_payload,
                      wire_kept, out_png):
    """Evidence panels for the B-52: painted planform with checked regions,
    the wireframe orphan island, old-vs-new physics, far-field decay."""
    import numpy as np

    from chief_engineer.plot_theme import (DIM, INK, LIVE, MUTED, TREND,
                                           VALID, _pyplot, style_axes)

    plt = _pyplot()
    fig, axes = plt.subplots(2, 2, figsize=(13.6, 10.6), dpi=150,
                             gridspec_kw={"height_ratios": [1.6, 1.0],
                                          "hspace": 0.28, "wspace": 0.16})
    (ax_a, ax_b), (ax_c, ax_d) = axes

    inv = results["invariants"]
    _b52_planform_panel(
        ax_a, payload_new, payload_new["field"]["values"],
        title="Current paint (planform, nose up), checked regions",
        note=(f"served JSON == recompute (max value diff "
              f"{results['rendering']['served_json_max_value_diff']:.0f})\n"
              f"{results['rendering']['triangles_total']} source faces shown "
              "1:1 — below the 30,000 face\ndecimation threshold, so the "
              "2026-07-25 pipeline fix is a no-op here\n"
              f"neighbour-face correlation r = "
              f"{results['rendering']['r_new_pipeline']:.2f}; window "
              f"[{payload_new['field']['min']:.0f}, "
              f"{payload_new['field']['max']:.0f}] m$^2$/s$^2$"),
        INK=INK, MUTED=MUTED, DIM=DIM)
    c = new_wall["centroids"]
    p = new_wall["p"]
    stag = p >= np.quantile(p, 0.995)
    suck = p <= np.quantile(p, 0.005)
    ax_a.plot(c[stag, 0], c[stag, 2], linestyle="none", marker="o",
              markersize=3.4, markerfacecolor="none",
              markeredgecolor="#ffd166", markeredgewidth=0.8,
              label="top 0.5% pressure (stagnation)")
    ax_a.plot(c[suck, 0], c[suck, 2], linestyle="none", marker="v",
              markersize=3.4, markerfacecolor="none",
              markeredgecolor="#4cc9f0", markeredgewidth=0.8,
              label="bottom 0.5% pressure (suction)")
    for text, xy, xytext in (
            ("nose + cockpit", (55.5, 1.0), (64.0, 2.0)),
            ("wing leading edges", (33.0, 16.5), (20.0, 13.0)),
            ("wing crowns\n(suction)", (39.0, 25.0), (19.5, 31.0)),
            ("tail fin", (55.0, 41.0), (27.0, 39.0))):
        ax_a.annotate(text, xy=xy, xytext=xytext, fontsize=8.5, color=MUTED,
                      arrowprops={"arrowstyle": "-", "color": MUTED,
                                  "linewidth": 0.8, "alpha": 0.8})
    leg = ax_a.legend(frameon=False, fontsize=8.5, loc="upper left")
    for t in leg.get_texts():
        t.set_color(INK)

    # Panel B: the display-only orphan island on the wireframe payload. This
    # mesh is the raw STL in its own units, so it gets its own limits.
    wire_verts = np.asarray(wire_payload["vertices"], dtype=np.float64)
    wire_faces = np.asarray(wire_payload["faces"], dtype=np.int64)
    kept_set = set(wire_kept)
    dropped = [i for i in range(len(wire_faces)) if i not in kept_set]
    from matplotlib.collections import PolyCollection
    tri = wire_verts[wire_faces][:, :, [0, 2]]
    ax_b.add_collection(PolyCollection(
        tri[wire_kept], facecolors="none", edgecolors=MUTED,
        linewidths=0.25, alpha=0.65))
    lo = wire_verts.min(axis=0)
    hi = wire_verts.max(axis=0)
    pad = 0.05 * max(hi[0] - lo[0], hi[2] - lo[2])
    if dropped:
        ax_b.add_collection(PolyCollection(
            tri[dropped], facecolors="#e5484d", edgecolors="#e5484d",
            linewidths=1.0))
        blob = wire_verts[wire_faces[dropped]].reshape(-1, 3)
        bx, bz = float(blob[:, 0].mean()), float(blob[:, 2].mean())
        ax_b.annotate(
            f"orphan island: {len(dropped)} faces\ndropped from DISPLAY "
            "only\n(values filtered in the same loop)",
            xy=(bx, bz),
            xytext=(lo[0] + 0.06 * (hi[0] - lo[0]),
                    lo[2] + 0.30 * (hi[2] - lo[2])),
            fontsize=9.0, color=INK,
            arrowprops={"arrowstyle": "-", "color": "#e5484d",
                        "linewidth": 1.0})
    ax_b.set_xlim(lo[0] - pad, hi[0] + pad)
    ax_b.set_ylim(lo[2] - pad, hi[2] + pad)
    ax_b.set_aspect("equal")
    ax_b.grid(False)
    ax_b.invert_yaxis()
    ax_b.set_title("Wireframe display mesh and the orphan-island filter",
                   color=INK, fontsize=11, loc="left", pad=8)
    wire_align = results["rendering"]["wire_orphan_alignment"]
    paint_align = results["rendering"]["painted_orphan_alignment"]
    ax_b.annotate(
        (f"wireframe {wire_payload['triangles_shown']} display faces -> "
         f"{len(wire_kept)} kept\n"
         f"painted body {paint_align['faces_in']} -> "
         f"{paint_align['faces_out']} kept "
         f"({paint_align['dropped']} faces, "
         f"{100.0 * paint_align['dropped'] / paint_align['faces_in']:.2f}%)\n"
         f"survivor values aligned: {paint_align['values_aligned']}; "
         f"corner positions preserved: "
         f"{paint_align['corner_positions_preserved']}\n"
         f"neighbour-face correlation after filter r = "
         f"{results['rendering']['r_survivors_after_filter']:.2f}"),
        xy=(0.99, 0.01), xycoords="axes fraction", ha="right", va="bottom",
        fontsize=8.5, color=INK,
        bbox={"boxstyle": "round,pad=0.4", "facecolor": "#0f1315",
              "edgecolor": DIM, "alpha": 0.9})
    for spine in ax_b.spines.values():
        spine.set_color(DIM)
    ax_b.tick_params(colors=MUTED, labelsize=8)

    # Panel C: old vs new surface pressure in scaled coordinates.
    prof = results["physics_old_vs_new"]
    ax_c.plot(prof["centers"], prof["cp_new"], color=LIVE, linewidth=2.0,
              label="new (48.5 m basis, skew 3.91, Re 3.23e8)")
    ax_c.plot(prof["centers_old"], prof["cp_old"], color=TREND,
              linewidth=2.0, linestyle=(0, (5, 4)),
              label="old (50 m basis, skew 5.06, Re 3.33e8)")
    ax_c.axhline(0.0, color=DIM, linewidth=0.9)
    ax_c.annotate(
        (f"RMS ΔCp = {prof['delta']['rms']:.4f}, "
         f"max {prof['delta']['max_abs']:.4f}\n"
         f"Re shift -3.0% (rescale); window shift "
         f"{prof['window_shift_percent']:.1f}% of span"),
        xy=(0.97, 0.06), xycoords="axes fraction", ha="right", va="bottom",
        fontsize=9.5, color=INK, weight="bold",
        bbox={"boxstyle": "round,pad=0.4", "facecolor": "#0f1315",
              "edgecolor": DIM, "alpha": 0.9})
    style_axes(ax_c, "length fraction z/L (nose to tail)",
               "area-weighted mean surface $C_p$",
               "Rescale + remesh physics change")
    leg = ax_c.legend(frameon=False, fontsize=8.5, loc="upper right")
    for t in leg.get_texts():
        t.set_color(INK)

    # Panel D: invariants and decay.
    far = results["farfield"]
    labels = ["1 L", "2 L", "3 L"]
    vals = [far["decay"][k]["mean_abs_cp"] for k in ("1L", "2L", "3L")]
    bars = ax_d.bar(range(len(vals)), vals, width=0.5, color=VALID,
                    alpha=0.85)
    for rect, v in zip(bars, vals):
        ax_d.annotate(f"{v:.5f}", xy=(rect.get_x() + rect.get_width() / 2,
                                      rect.get_height()),
                      xytext=(0, 4), textcoords="offset points", ha="center",
                      fontsize=9.5, color=INK, weight="bold")
    ax_d.set_xticks(range(len(vals)), labels)
    ax_d.annotate(
        (f"stagnation bound p$_\\infty$ + U$^2$/2 = "
         f"{inv['stagnation_limit']:.0f} m$^2$/s$^2$\n"
         f"max wall p/ρ = {inv['max_wall_p']:.0f}  "
         f"(C$_p$ {inv['cp_max']:.3f} ≤ 1), "
         f"{inv['exceedance']['count']} faces above bound\n"
         f"stagnation faces forward-facing: "
         f"{inv['stagnation_alignment']['frac_forward'] * 100:.1f}% "
         f"(mean n·x̂ {inv['stagnation_alignment']['mean_dot']:.2f})\n"
         f"peak faces are {inv['stagnation_face_scale_m']:.2f} m across "
         f"({inv['stagnation_face_scale_over_length'] * 100:.1f}% of L):\n"
         f"the nose peak is under-resolved, so C$_p$ under-shoots 1"),
        xy=(0.97, 0.95), xycoords="axes fraction", ha="right", va="top",
        fontsize=9.5, color=INK, weight="bold",
        bbox={"boxstyle": "round,pad=0.5", "facecolor": "#0f1315",
              "edgecolor": DIM, "alpha": 0.9})
    style_axes(ax_d, "spherical shell radius, body lengths (L = 48.5 m)",
               "mean |$C_p$| in the shell",
               "Far-field decay toward p$_\\infty$ (upstream hemisphere)")
    ax_d.set_ylim(0, max(vals) * 2.1)

    note = ("Solver output read directly (foamToVTK boundary + volume). "
            "U = 100 m/s along +z from the case's own coefficient header; "
            "p kinematic (m2/s2).\nOld case study-b52-9414fb (50 m basis, "
            "skew 5.06), new case study-b52-f686c4 (48.5 m published "
            "length, skewness-gated remesh, skew 3.91).")
    fig.text(0.01, 0.006, note, color=MUTED, fontsize=8.0,
             family="monospace", va="bottom")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    out_png = Path(out_png)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png)
    plt.close(fig)
    return str(out_png)


def run_b52(staging: Path, served_json: Path, out_dir: Path) -> dict:
    import numpy as np

    from chief_engineer import geometry as geo

    results: dict = {
        "u_inf": B52_U_INF, "q_kinematic": B52_Q,
        "l_new": B52_LENGTH_NEW, "l_old": B52_LENGTH_OLD,
        "re_new": B52_U_INF * B52_LENGTH_NEW / B52_NU,
        "re_old": B52_U_INF * B52_LENGTH_OLD / B52_NU,
        # From the two cases' controlDict force blocks, checkMesh logs and
        # coefficient.dat files, plus the bounds of each case's own
        # constant/triSurface/b52.stl: same 13,784 facets, spans
        # (57.4095, 12.7845, 50.0) m and (55.6873, 12.4010, 48.5) m — a
        # uniform 0.97 rescale of one geometry, not a new geometry.
        "case_provenance": {
            "old_case": "study-b52-9414fb",
            "new_case": "study-b52-f686c4",
            "cells_old": 193815, "cells_new": 193880,
            "max_skewness_old": 5.0580476, "max_skewness_new": 3.9117873,
            "max_non_ortho_old": 57.143823, "max_non_ortho_new": 54.3,
            "cd_old": B52_CD_OLD, "cd_new": B52_CD_NEW,
            "cd_shift_percent": 100.0 * (B52_CD_NEW / B52_CD_OLD - 1.0),
            "geometry_rescaled": True,
            "geometry_scale_factor": B52_LENGTH_NEW / B52_LENGTH_OLD,
            "stl_facets_old": 13784, "stl_facets_new": 13784,
            "aref_old": 638.323, "aref_new": 600.598,
        }}

    new_wall = merge_body_walls(staging / "new")
    old_wall = merge_body_walls(staging / "old")

    far = b52_farfield_and_decay(
        staging / "new" / "internal.vtu",
        body_center=new_wall["centroids"].mean(axis=0),
        length=B52_LENGTH_NEW)
    far_old = b52_farfield_and_decay(
        staging / "old" / "internal.vtu",
        body_center=old_wall["centroids"].mean(axis=0),
        length=B52_LENGTH_OLD)
    results["farfield"] = far
    results["farfield_old"] = far_old
    p_inf = far["p_inf"]

    p = new_wall["p"]
    c = new_wall["centroids"]
    limit = p_inf + B52_Q
    exc = exceedance_stats(p, new_wall["areas"], c, limit)
    hi_thr = float(np.quantile(p, 0.995))
    lo_thr = float(np.quantile(p, 0.005))
    stag = p >= hi_thr
    suck = p <= lo_thr
    # The stagnation Cp of a coarse mesh under-shoots 1: the wall value is the
    # adjacent cell's, and the nose is resolved by a handful of cells. Record
    # the size of the faces carrying the peak, as a fraction of body length,
    # so the shortfall is attributable instead of merely observed.
    stag_scale = float(np.median(np.sqrt(new_wall["areas"][stag])))
    results["invariants"] = {
        "p_inf": p_inf,
        "stagnation_limit": limit,
        "max_wall_p": float(p.max()),
        "cp_max": float((p.max() - p_inf) / B52_Q),
        "exceedance": exc,
        "stagnation_alignment": alignment_stats(new_wall["normals"][stag],
                                                B52_FLOW_AXIS),
        "stagnation_threshold_cp": (hi_thr - p_inf) / B52_Q,
        "stagnation_regions": region_shares(c, stag, B52_REGIONS),
        "stagnation_face_scale_m": stag_scale,
        "stagnation_face_scale_over_length": stag_scale / B52_LENGTH_NEW,
        "suction_threshold_cp": (lo_thr - p_inf) / B52_Q,
        "suction_regions": region_shares(c, suck, B52_REGIONS),
        "suction_alignment": alignment_stats(new_wall["normals"][suck],
                                             B52_FLOW_AXIS),
        "suction_median_abs_flow_dot": float(np.median(
            np.abs(new_wall["normals"][suck][:, B52_FLOW_AXIS]))),
        "cp_min": float((p.min() - p_inf) / B52_Q),
        "wall_faces": int(len(p)),
    }
    p_old = old_wall["p"]
    results["invariants"]["cp_max_old_mesh"] = float(
        (p_old.max() - far_old["p_inf"]) / B52_Q)
    results["invariants"]["cp_min_old_mesh"] = float(
        (p_old.min() - far_old["p_inf"]) / B52_Q)

    # Old vs new physics, in each body's own scaled length coordinate.
    edges = np.linspace(0.0, 1.0, 42)
    z_new = c[:, B52_FLOW_AXIS]
    zf_new = (z_new - z_new.min()) / (z_new.max() - z_new.min())
    co_ = old_wall["centroids"][:, B52_FLOW_AXIS]
    zf_old = (co_ - co_.min()) / (co_.max() - co_.min())
    cn, mn, _ = binned_mean_profile(
        zf_new, (p - p_inf) / B52_Q, new_wall["areas"], edges)
    co, mo, _ = binned_mean_profile(
        zf_old, (old_wall["p"] - far_old["p_inf"]) / B52_Q,
        old_wall["areas"], edges)
    delta = profile_delta(cn, mn, co, mo)
    pct_new = area_weighted_percentiles(
        (p - p_inf) / B52_Q, new_wall["areas"], [2, 25, 50, 75, 98])
    pct_old = area_weighted_percentiles(
        (old_wall["p"] - far_old["p_inf"]) / B52_Q,
        old_wall["areas"], [2, 25, 50, 75, 98])

    payload_new, _ = painted_payload(staging / "new")
    payload_old, _ = painted_payload(staging / "old")
    served = json.loads(Path(served_json).read_text(encoding="utf-8"))
    sv = np.asarray(served["field"]["values"], dtype=np.float64)
    nv = np.asarray(payload_new["field"]["values"], dtype=np.float64)
    served_match = (
        len(sv) == len(nv)
        and served["triangles_shown"] == payload_new["triangles_shown"]
        and math.isclose(served["field"]["min"], payload_new["field"]["min"],
                         rel_tol=1e-9)
        and math.isclose(served["field"]["max"], payload_new["field"]["max"],
                         rel_tol=1e-9))
    max_diff = float(np.max(np.abs(sv - nv))) if len(sv) == len(nv) else None

    r_new, pairs = neighbor_correlation(payload_new["faces"],
                                        payload_new["field"]["values"])
    new_win = (payload_new["field"]["min"], payload_new["field"]["max"])
    old_win = (payload_old["field"]["min"], payload_old["field"]["max"])
    win_span = new_win[1] - new_win[0]

    # Orphan-island filter, run on the SERVED payloads the browser fetches:
    # the painted body and the wireframe display mesh. Both go through the
    # same mirror of the GUI's dropOrphanIslands, and both are then proved
    # to have carried their survivors' values and corner positions through.
    paint_filtered = drop_orphan_islands(
        served["vertices"], served["faces"], served["field"]["values"])
    paint_align = orphan_filter_alignment(
        served["vertices"], served["faces"], served["field"]["values"],
        paint_filtered)
    wire_payload = geo.load_surface(SDK / "geometry" / "b52.stl")
    wire_filtered = drop_orphan_islands(
        wire_payload["vertices"], wire_payload["faces"], None)
    wire_align = orphan_filter_alignment(
        wire_payload["vertices"], wire_payload["faces"], None, wire_filtered)
    # The surviving surface must still read as a smooth field, not as a
    # re-indexed scramble: correlate the filtered payload in its own frame.
    r_survivors, _ = neighbor_correlation(paint_filtered["faces"],
                                          paint_filtered["values"])
    wire_kept = wire_filtered["kept"]

    results["physics_old_vs_new"] = {
        "centers": [float(v) for v in cn], "cp_new": [float(v) for v in mn],
        "centers_old": [float(v) for v in co],
        "cp_old": [float(v) for v in mo],
        "delta": delta,
        "window_shift_percent": 100.0 * max(
            abs(new_win[0] - old_win[0]),
            abs(new_win[1] - old_win[1])) / win_span,
        "re_shift_percent": 100.0 * (B52_LENGTH_NEW / B52_LENGTH_OLD - 1.0),
        "cf_shift_percent_re_power_law": 100.0 * (
            (B52_LENGTH_NEW / B52_LENGTH_OLD) ** (-1.0 / 7.0) - 1.0),
        "area_weighted_cp_percentiles_new": pct_new,
        "area_weighted_cp_percentiles_old": pct_old,
    }
    results["rendering"] = {
        "triangles_total": payload_new["triangles_total"],
        "triangles_shown": payload_new["triangles_shown"],
        # Below the 30,000-face decimation threshold the painted pipeline is
        # a pass-through, so the 2026-07-25 decimation-correspondence fix
        # cannot have changed one pixel of this body.
        "decimated": payload_new["triangles_total"] > 30000,
        "served_json_matches_recompute": bool(served_match),
        "served_json_max_value_diff": max_diff,
        "r_new_pipeline": r_new,
        "neighbour_pairs": pairs,
        "window_new": list(new_win),
        "window_old": list(old_win),
        "painted_component_sizes": paint_filtered["component_sizes"][:6],
        "painted_orphan_faces_dropped": paint_filtered["dropped"],
        "painted_orphan_alignment": paint_align,
        "r_survivors_after_filter": r_survivors,
        "wire_display_faces": wire_payload["triangles_shown"],
        "wire_component_sizes": wire_filtered["component_sizes"][:6],
        "wire_orphan_faces_dropped": wire_filtered["dropped"],
        "wire_orphan_alignment": wire_align,
        "wire_faces_kept": len(wire_kept),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    png = render_b52_figure(new_wall, results, payload_new, wire_payload,
                            wire_kept, out_dir / "b52_cp_validation.png")
    results["plot"] = png
    out_json = out_dir / "b52_validation_numbers.json"
    out_json.write_text(json.dumps(results, indent=2, default=str),
                        encoding="utf-8")
    results["numbers"] = str(out_json)
    return results


def main(argv=None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate the motorbike and B-52 surface-pressure "
                    "fields against invariants, the pre-remesh solves, and "
                    "the display pipeline.")
    parser.add_argument("--staging", type=Path, default=None,
                        help="motorbike staging directory holding new/ and "
                             "old/ with the boundary .vtp files and "
                             "internal.vtu of the post- and pre-remesh cases")
    parser.add_argument("--served-json", type=Path, default=None,
                        help="the GUI's served motorbike painted-surface "
                             "JSON (mission-output/geometry-study/"
                             "motorBike_field.json)")
    parser.add_argument("--staging-b52", type=Path, default=None,
                        help="B-52 staging directory, same layout")
    parser.add_argument("--served-json-b52", type=Path, default=None,
                        help="the GUI's served B-52 painted-surface JSON")
    parser.add_argument("--out-dir", required=True, type=Path,
                        help="directory for the evidence plots and JSON")
    args = parser.parse_args(argv)

    ran = False
    if args.staging and args.served_json:
        results = run(args.staging, args.served_json, args.out_dir)
        printable = {k: v for k, v in results.items()
                     if k not in ("physics_old_vs_new",)}
        printable["physics_delta"] = results["physics_old_vs_new"]["delta"]
        printable["window_shift_percent"] = (
            results["physics_old_vs_new"]["window_shift_percent"])
        print(json.dumps(printable, indent=2, default=str))
        print(f"numbers: {results['numbers']}")
        ran = True
    if args.staging_b52 and args.served_json_b52:
        results = run_b52(args.staging_b52, args.served_json_b52,
                          args.out_dir)
        printable = {k: v for k, v in results.items()
                     if k not in ("physics_old_vs_new",)}
        printable["physics_delta"] = results["physics_old_vs_new"]["delta"]
        print(json.dumps(printable, indent=2, default=str))
        print(f"numbers: {results['numbers']}")
        ran = True
    if not ran:
        parser.error("provide --staging/--served-json and/or "
                     "--staging-b52/--served-json-b52")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
