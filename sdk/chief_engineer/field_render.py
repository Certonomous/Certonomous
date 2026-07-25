"""Paint a solved field onto the mission's surface for the viewport.

After a case is solved, ``foamToVTK -surfaceFields`` writes the body patch with
its pressure field attached.  This module reads that ``.vtp`` (VTK XML with
base64-encoded binary arrays), reduces it to a wireframe payload the browser
already knows how to draw, and adds a per-face pressure-coefficient value so
the viewport can colour the geometry by the real solution rather than by depth
alone.

Pure standard library: the base64 arrays are decoded by hand, so nothing here
needs VTK or numpy on the controller.

The mid-span pressure-slice renderer at the bottom of this module is the one
exception: it reads the case's volume output (``internal.vtu``, written by the
same ``foamToVTK`` call as the surface patches) and renders a filled contour of
the static pressure in the fluid around the body, so it imports numpy and
matplotlib lazily. The wireframe/paint path above stays stdlib-only.
"""

from __future__ import annotations

import base64
import logging
import math
import re
import struct
from pathlib import Path
from typing import Any

from .geometry import _cluster, _package

_log = logging.getLogger(__name__)

_ARRAY = re.compile(
    r"<DataArray\b([^>]*)>(.*?)</DataArray>", re.S)
_ATTR = re.compile(r"(\w+)\s*=\s*'([^']*)'")
_HEADER_TYPE = re.compile(r"header_type\s*=\s*'([^']+)'")
_POINTDATA = re.compile(r"<PointData\b.*?</PointData>", re.S)
_CELLDATA = re.compile(r"<CellData\b.*?</CellData>", re.S)
_POINTS = re.compile(r"<Points\b.*?</Points>", re.S)
_POLYS = re.compile(r"<Polys\b.*?</Polys>", re.S)

_TYPE_FMT = {"Float32": ("f", 4), "Float64": ("d", 8),
             "Int32": ("i", 4), "Int64": ("q", 8),
             "UInt32": ("I", 4), "UInt64": ("Q", 8)}


def _decode(attrs: str, body: str, header_bytes: int) -> list[float]:
    """Decode one base64 binary DataArray into a flat list of numbers."""
    meta = dict(_ATTR.findall(attrs))
    fmt, size = _TYPE_FMT[meta["type"]]
    raw = base64.b64decode("".join(body.split()))
    # VTK XML binary prefixes each array with a header giving its byte length.
    head_fmt = "Q" if header_bytes == 8 else "I"
    payload = raw[header_bytes:]
    count = len(payload) // size
    return list(struct.unpack(f"<{count}{fmt}", payload[:count * size]))


def _named(section: str, name: str, header_bytes: int) -> list[float] | None:
    for attrs, body in _ARRAY.findall(section):
        meta = dict(_ATTR.findall(attrs))
        if meta.get("Name") == name:
            return _decode(attrs, body, header_bytes)
    return None


def _read_patch(vtp_path: str | Path, field: str):
    """Parse one .vtp patch into (vertices, faces, per-face field values)."""
    text = Path(vtp_path).read_text(errors="replace")
    header_bytes = 8 if (_HEADER_TYPE.search(text) or [""])[0] == "UInt64" or \
        "header_type='UInt64'" in text else 4

    points_section = _POINTS.search(text).group(0)
    flat_points = _named(points_section, "Points", header_bytes)
    vertices = [list(flat_points[i:i + 3]) for i in range(0, len(flat_points), 3)]

    polys = _POLYS.search(text).group(0)
    connectivity = [int(v) for v in _named(polys, "connectivity", header_bytes)]
    offsets = [int(v) for v in _named(polys, "offsets", header_bytes)]

    faces: list[list[int]] = []
    start = 0
    for end in offsets:
        poly = connectivity[start:end]
        # Fan-triangulate so the viewport only handles triangles.
        for k in range(1, len(poly) - 1):
            faces.append([poly[0], poly[k], poly[k + 1]])
        start = end

    # Pressure: prefer per-point (smooth), fall back to per-cell.
    values_by_vertex: list[float] | None = None
    point_section = _POINTDATA.search(text)
    if point_section:
        values_by_vertex = _named(point_section.group(0), field, header_bytes)

    face_values: list[float] = []
    if values_by_vertex:
        for face in faces:
            face_values.append(sum(values_by_vertex[i] for i in face) / 3.0)
    else:
        cell_section = _CELLDATA.search(text)
        per_cell = _named(cell_section.group(0), field, header_bytes) if cell_section else None
        if per_cell:
            # offsets index polygons; each polygon fanned into (len-2) triangles.
            expanded: list[float] = []
            start = 0
            for poly_index, end in enumerate(offsets):
                tris = max(1, (end - start) - 2)
                expanded.extend([per_cell[poly_index]] * tris)
                start = end
            face_values = expanded[:len(faces)]

    return vertices, faces, face_values


def load_field_surface(sources, *, field: str = "p",
                       max_faces: int = 30000, name: str = "surface") -> dict[str, Any]:
    """Read one patch file or merge several into a painted wireframe payload."""
    paths = [sources] if isinstance(sources, (str, Path)) else list(sources)
    all_v: list[list[float]] = []
    all_f: list[list[int]] = []
    all_field: list[float] = []
    for path in paths:
        try:
            vertices, faces, values = _read_patch(path, field)
        except Exception:
            continue
        base = len(all_v)
        all_v.extend(vertices)
        all_f.extend([[i + base for i in face] for face in faces])
        if values and len(values) == len(faces):
            all_field.extend(values)
        else:
            all_field.extend([0.0] * len(faces))
    payload, display_values = _package_painted(all_v, all_f, all_field, max_faces, name)
    _attach_field(payload, display_values, field)
    return payload


def _package_painted(vertices, faces, face_values, max_faces: int, name: str):
    """Package a mesh for the viewport with field values tracking the decimation.

    Returns ``(payload, display_values)`` where ``display_values`` has exactly
    one value per face in ``payload["faces"]``.

    Below the decimation threshold this defers to :func:`geometry._package`
    unchanged and passes the per-face values straight through — the pipeline
    for non-decimated bodies (motorbike, B-52) is byte-identical, which is the
    frozen-rendering acceptance bar.

    Above the threshold ``_package`` decimates by vertex clustering, so source
    face *i* has no relationship to display face *i*: sampling the value list
    by index painted the decimated sail as salt-and-pepper noise. Here the
    clustering is mirrored step for step (same resolution search, same grid
    math as ``geometry._cluster``) so every source face can be mapped to the
    display face its corners collapsed into, and each display face carries the
    mean of the source faces that merged into it — a smooth physical field.
    ``test_field_render`` pins the mirrored geometry against ``_package``'s
    own output, so any change to the decimation in ``geometry.py`` fails a
    test here instead of silently drifting.
    """
    total = len(faces)
    have_values = bool(face_values) and len(face_values) == total
    if total <= max_faces or not have_values:
        payload = _package(vertices, faces, max_faces, name)
        values = face_values[:len(payload["faces"])] if have_values else []
        return payload, values

    # -- Mirror of geometry._package's decimation branch ---------------------
    out_vertices, out_faces = vertices, faces
    resolution = used_resolution = 56
    for _ in range(6):
        used_resolution = resolution
        out_vertices, out_faces = _cluster(vertices, faces, resolution)
        if len(out_faces) > max_faces * 1.35:
            resolution = max(8, int(resolution * 0.78))
        elif len(out_faces) < max_faces * 0.45:
            resolution = int(resolution * 1.3)
        else:
            break
    if len(out_faces) > max_faces:
        keep = max(1, math.ceil(len(out_faces) / max_faces))
        out_faces = out_faces[::keep]

    # -- Source-vertex -> display-vertex owner map (same grid as _cluster) ---
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    zs = [v[2] for v in vertices]
    low = (min(xs), min(ys), min(zs))
    high = (max(xs), max(ys), max(zs))
    size = max(high[i] - low[i] for i in range(3)) or 1.0
    cell = size / max(1, used_resolution)
    cells: dict[tuple[int, int, int], int] = {}
    owner: list[int] = []
    for vertex in vertices:
        key = tuple(int((vertex[i] - low[i]) // cell) for i in range(3))
        index = cells.get(key)
        if index is None:
            index = len(cells)
            cells[key] = index
        owner.append(index)

    # -- Aggregate: mean of the source faces merged into each display face ---
    merged: dict[tuple[int, int, int], list[float]] = {}
    for face, value in zip(faces, face_values):
        if len(face) < 3:
            continue
        try:
            mapped = (owner[face[0]], owner[face[1]], owner[face[2]])
        except IndexError:
            continue
        if mapped[0] == mapped[1] or mapped[1] == mapped[2] or mapped[0] == mapped[2]:
            continue  # collapsed to zero area; _cluster drops it too
        key = tuple(sorted(mapped))
        slot = merged.get(key)
        if slot is None:
            merged[key] = [value, 1.0]
        else:
            slot[0] += value
            slot[1] += 1.0
    display_values = []
    for face in out_faces:
        slot = merged.get(tuple(sorted(face)))
        display_values.append(slot[0] / slot[1] if slot else 0.0)

    # -- Payload assembly, identical to _package's ---------------------------
    pxs = [v[0] for v in out_vertices] or [0.0]
    pys = [v[1] for v in out_vertices] or [0.0]
    pzs = [v[2] for v in out_vertices] or [0.0]
    payload = {
        "name": name,
        "vertices": [[round(c, 5) for c in v] for v in out_vertices],
        "faces": out_faces,
        "triangles_total": total,
        "triangles_shown": len(out_faces),
        "bounds": {"min": [min(pxs), min(pys), min(pzs)],
                   "max": [max(pxs), max(pys), max(pzs)]},
    }
    return payload, display_values


def _attach_field(payload: dict[str, Any], face_values, field: str) -> None:
    """Carry a normalised field value per kept face, plus its physical range.

    ``face_values`` must already be one-to-one with ``payload["faces"]`` —
    :func:`_package_painted` guarantees that for both the decimated and the
    untouched path.
    """
    if not face_values:
        payload["field"] = None
        return
    sampled = face_values
    # Clip to robust percentiles: a single stagnation spike would otherwise
    # flatten the whole surface to one colour. The 2nd/98th keep the real
    # pressure variation across the wings and body visible.
    ordered = sorted(sampled)
    lo = ordered[max(0, int(0.02 * len(ordered)))]
    hi = ordered[min(len(ordered) - 1, int(0.98 * len(ordered)))]
    span = (hi - lo) or 1.0
    payload["field"] = {
        "name": field,
        "min": lo,
        "max": hi,
        # 0..1 per drawn face, for the colormap in the browser.
        "values": [round(min(1.0, max(0.0, (v - lo) / span)), 4) for v in sampled],
        "display_min": round(lo, 1), "display_max": round(hi, 1),
    }


# Names of patches that are the flow domain — the wind-tunnel / farfield box —
# not the body. The body is whatever is left once these are removed. Matched
# case-insensitively against the patch (file) stem.
_DOMAIN_NAMES = frozenset({
    "inlet", "outlet", "ground", "floor", "sky", "ceiling", "roof",
    "front", "back", "frontandback", "farfield", "freestream",
    "defaultfaces", "domain", "atmosphere", "wall", "walls",
    "lowerwall", "upperwall", "fixedwalls", "movingwall",
    "top", "bottom", "left", "right", "side", "sides",
})
# Prefixes that are always domain, whatever the suffix: symmetry planes
# (sym, symmetry, symPlane, symFront…) and decomposition (processor) patches.
_DOMAIN_PREFIXES = ("sym", "proc")


def _is_domain_patch(stem: str) -> bool:
    """True when a patch name is a flow-domain boundary, not the body."""
    s = stem.strip().lower()
    return s in _DOMAIN_NAMES or s.startswith(_DOMAIN_PREFIXES)


def _body_patches(patches: list[Path]) -> list[Path]:
    """Reduce a list of ``.vtp`` patch files to only the body patches.

    Two tiers, so this is right for both the motorBike (a ``motorBike_*`` group
    of dozens of sub-patches inside a wind-tunnel box) and a single-patch body
    like the B-52. First drop every known domain boundary. Then, if the
    survivors form a dominant ``<body>_<part>`` group (the motorBike case), keep
    only that group — so an unknown domain name that slipped the blocklist can't
    poison the merge and paint a flat rectangle instead of the vehicle.
    """
    kept = [p for p in patches if not _is_domain_patch(p.stem)]
    if len(kept) <= 1:
        return kept
    from collections import Counter

    groups: Counter[str] = Counter()
    for p in kept:
        if "_" in p.stem:
            groups[p.stem.split("_", 1)[0].lower()] += 1
    if groups:
        top, n = groups.most_common(1)[0]
        # A real group is two or more parts sharing a prefix; a single stray
        # underscore is not enough to override the blocklist result.
        if n >= 2:
            grouped = [p for p in kept if p.stem.lower().startswith(top + "_")]
            if len(grouped) >= n:
                return grouped
    return kept


def extract_and_paint(remote_case: str, out_path: str | Path, wsl_prefix,
                      *, field: str = "p", name: str = "surface",
                      input_triangles: int | None = None,
                      min_fraction: float = 0.15) -> str | None:
    """Run foamToVTK, merge every body patch, and write a painted-surface JSON.

    The body may be one patch (``body``) or a group of dozens (the motorBike's
    ``motorBike_*`` sub-patches). Every patch that is not a domain boundary is
    collected and merged, so this works for any geometry. Returns the local
    JSON path, or None if no field surface could be produced.

    Safeguard against painting the wrong surface: if ``input_triangles`` is
    given and the merged body carries fewer than ``min_fraction`` of that many
    faces, the selection is treated as suspect (almost certainly a couple of
    flat domain rectangles rather than the vehicle) — it is flagged in the log
    and None is returned so the caller keeps the wireframe rather than painting
    the wrong thing.

    ``min_fraction`` calibration: snappyHexMesh remeshes the surface, so the
    painted body face count is NOT one-to-one with the input triangle count.
    Measured on the motorBike, the correct body is 101,235 faces against a
    331,653-triangle input — 31%. The bug this guards against selected two flat
    domain rectangles: 5,747 faces, 1.7%. The floor is set well between those
    two populations (comfortable margin above the real body, wide margin above
    the failure) rather than at a literal fraction that would sit one point
    under the real body and false-positive on any mesh variation.
    """
    import json
    import subprocess
    import tempfile

    out_path = Path(out_path).with_suffix(".json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp())
    local_boundary = str(staging).replace("\\", "/")
    if len(local_boundary) > 1 and local_boundary[1] == ":":
        local_boundary = "/mnt/" + local_boundary[0].lower() + local_boundary[2:]
    # No command substitution: the wsl.exe argument layer eats $(...), so this
    # relies on cd + a glob, both of which pass through intact. foamToVTK writes
    # VTK/ into the case's own directory.
    command = (
        f"cd {remote_case} && "
        f"openfoam2606 foamToVTK -latestTime -surfaceFields >/dev/null 2>&1; "
        f"cp VTK/*/boundary/*.vtp '{local_boundary}/' 2>/dev/null && echo OK")
    result = subprocess.run([*wsl_prefix, "bash", "-c", command],
                            capture_output=True, text=True, timeout=600)
    if "OK" not in result.stdout:
        return None
    patches = _body_patches(list(staging.glob("*.vtp")))
    if not patches:
        _log.warning("field-paint patch selection suspect: no body patch left "
                     "after excluding domain boundaries — falling back to wireframe")
        return None
    payload = load_field_surface(patches, field=field, name=name)
    if not payload.get("field"):
        return None
    # Face-count sanity check: the painted body should be a large fraction of
    # the input surface, not a handful of flat domain rectangles.
    body_faces = int(payload.get("triangles_total", 0))
    if input_triangles:
        fraction = body_faces / max(1, input_triangles)
        if fraction < min_fraction:
            _log.warning(
                "field-paint patch selection suspect: painted body has %d faces, "
                "only %.0f%% of the %d input triangles (floor %.0f%%) from patches "
                "%s — falling back to wireframe",
                body_faces, 100 * fraction, input_triangles, 100 * min_fraction,
                sorted(p.stem for p in patches))
            return None
        _log.info("field-paint: painted body has %d faces from %d patches "
                  "(%.0f%% of %d input triangles)",
                  body_faces, len(patches), 100 * fraction, input_triangles)
    out_path.write_text(json.dumps(payload), encoding="utf-8")
    return str(out_path)


def _wsl_out(path: Path) -> str:
    text = str(path).replace("\\", "/")
    if len(text) > 1 and text[1] == ":":
        text = "/mnt/" + text[0].lower() + text[2:]
    return text


# ---------------------------------------------------------------------------
# Mid-span pressure slice: the field AROUND the body, from the volume output
# ---------------------------------------------------------------------------
# People read external aerodynamics from a 2D pressure-field slice: stagnation
# warmth at the nose, the blue suction bubble over the upper surface. The
# painted body above shows pressure ON the surface; this section shows the
# static pressure IN the fluid on a plane normal to the span axis at mid-span,
# extracted from the cell-centre field of the case's own volume output.

_CELLS = re.compile(r"<Cells\b.*?</Cells>", re.S)

# numpy dtypes for the same VTK binary types _TYPE_FMT covers.
_NP_TYPES = {"Float32": "<f4", "Float64": "<f8", "Int32": "<i4",
             "Int64": "<i8", "UInt8": "u1", "UInt32": "<u4", "UInt64": "<u8"}

SLICE_TITLE = "Static pressure, mid-span slice"
# Slab thickness: ~2% of the body span (1% half-thickness each side).
SLICE_HALF_THICKNESS_FRACTION = 0.01

# Diverging pressure map for the control-room theme: plot_theme's panel blue
# and alert red at the poles (red high, blue low, the same convention as the
# painted body), brightened at the extremes so the stagnation and suction
# regions carry the eye, through a neutral dark grey at zero pressure so the
# near-freestream field recedes into the panel. The midpoint is a neutral,
# never a hue; the body cross-section shows as the darker figure background.
_SLICE_ANCHORS = ("#8ec8ff", "#57a5ff", "#3a4147", "#f26a5c", "#ffb2a1")


def _named_array(section: str, name: str, header_bytes: int):
    """Decode one base64 binary DataArray into a numpy array (volume path).

    Same wire format as :func:`_decode` (base64 over header+payload), but the
    byte-count header is honoured exactly and the payload lands in numpy,
    because a volume file carries millions of values where the per-face loop
    above carries thousands.
    """
    import numpy as np

    for attrs, body in _ARRAY.findall(section):
        meta = dict(_ATTR.findall(attrs))
        if meta.get("Name") != name:
            continue
        raw = base64.b64decode("".join(body.split()))
        head_fmt = "<Q" if header_bytes == 8 else "<I"
        (length,) = struct.unpack(head_fmt, raw[:header_bytes])
        payload = raw[header_bytes:header_bytes + length]
        return np.frombuffer(payload, dtype=_NP_TYPES[meta["type"]])
    return None


def read_volume_field(vtu_path: str | Path, field: str = "p"):
    """Read points, cell connectivity, and one cell-centred field from a .vtu.

    Returns ``(points (N,3), connectivity, offsets, values (C,))`` as numpy
    arrays, or None when any part is missing. The cell-centre values are the
    solver's own finite-volume unknowns, so no interpolation happens here.
    """
    text = Path(vtu_path).read_text(errors="replace")
    header_bytes = 8 if "header_type='UInt64'" in text or \
        (_HEADER_TYPE.search(text) or [""])[0] == "UInt64" else 4

    points_section = _POINTS.search(text)
    cells_section = _CELLS.search(text)
    cell_data = _CELLDATA.search(text)
    if not (points_section and cells_section and cell_data):
        return None
    points = _named_array(points_section.group(0), "Points", header_bytes)
    connectivity = _named_array(cells_section.group(0), "connectivity", header_bytes)
    offsets = _named_array(cells_section.group(0), "offsets", header_bytes)
    values = _named_array(cell_data.group(0), field, header_bytes)
    if points is None or connectivity is None or offsets is None or values is None:
        return None
    return points.reshape(-1, 3).astype("f8"), connectivity, offsets, values.astype("f8")


def cell_centres(points, connectivity, offsets):
    """Cell centres and per-axis extents from raw VTK unstructured-grid arrays.

    Pure function over the arrays :func:`read_volume_field` returns. The
    centre is the mean of the cell's vertices and the extent its axis-aligned
    bounding box, which is exact for the hex-dominant snappy meshes here and
    plenty for picking and framing a display slice (no polyhedral face
    machinery needed). Returns ``(centres (C,3), extents (C,3))``.
    """
    import numpy as np

    offsets = np.asarray(offsets, dtype=np.int64)
    if offsets.size == 0:
        return (np.zeros((0, 3)), np.zeros((0, 3)))
    starts = np.empty_like(offsets)
    starts[0] = 0
    starts[1:] = offsets[:-1]
    cell_points = np.asarray(points, dtype=np.float64)[
        np.asarray(connectivity, dtype=np.int64)]
    counts = (offsets - starts).astype(np.float64)
    centres = np.add.reduceat(cell_points, starts, axis=0) / counts[:, None]
    extents = (np.maximum.reduceat(cell_points, starts, axis=0)
               - np.minimum.reduceat(cell_points, starts, axis=0))
    return centres, extents


def pick_slice(centres, extents, *, axis: int, station: float,
               half_thickness: float, min_cells: int = 200,
               widenings: int = 4):
    """Indices of the cell layer the mid-span plane passes through.

    A cell is kept when the plane crosses the cell's own extent along the
    slice axis. That gives exactly one cell per in-plane position: the fine
    near-body layers never stack (stacked layers project onto each other and
    render as checkerboard noise, seen on the B-52 nose with a plain slab),
    while the far field stays covered because its huge cells reach the plane
    from far away — an effective slab of about one local cell size, thinner
    than the nominal ~2% of span everywhere the mesh is refined. The nominal
    ``half_thickness`` serves only as the widening fallback: when a sparse
    volume leaves the cut starved the slab grows, doubling up to
    ``widenings`` times, so an older, coarser held case still yields a
    picture. Returns ``(indices, half_thickness_used)`` where a used value of
    0.0 means the pure one-layer cut.
    """
    import numpy as np

    centres = np.asarray(centres, dtype=np.float64)
    extents = np.asarray(extents, dtype=np.float64)
    distance = np.abs(centres[:, axis] - station)
    reach = 0.5 * extents[:, axis]
    used = 0.0
    keep = np.flatnonzero(distance <= reach)
    for _ in range(widenings):
        if keep.size >= min_cells:
            break
        used = half_thickness if used == 0.0 else used * 2.0
        keep = np.flatnonzero(distance <= reach + used)
    return keep, used


def render_slice_figure(u, v, values, footprint, out_png: str | Path, *,
                        xlabel: str, ylabel: str, body_label: str = "",
                        station_note: str = "", view_box=None,
                        figsize=(11.4, 6.2), dpi: int = 150) -> dict | None:
    """Render the filled pressure contour around the body silhouette.

    ``u``/``v`` are in-plane cell-centre coordinates in metres, ``values`` the
    cell-centre kinematic pressure (the incompressible solver's p, which is
    already p over rho, in m^2/s^2), ``footprint`` each cell's in-plane size.
    The triangulation is masked wherever a triangle spans farther than a few
    local cell sizes, which is exactly the body cross-section (and any other
    hole in the fluid), so the body shows as the dark panel background.
    Returns metadata about what was drawn, including every string placed on
    the figure so tests can hold the register.
    """
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
    from matplotlib.tri import Triangulation

    from .plot_theme import BG, DIM, INK, MUTED, _pyplot, style_axes

    u = np.asarray(u, dtype=np.float64)
    v = np.asarray(v, dtype=np.float64)
    values = np.asarray(values, dtype=np.float64)
    footprint = np.asarray(footprint, dtype=np.float64)
    if u.size < 3:
        return None

    if view_box is None:
        view_box = (float(u.min()), float(u.max()),
                    float(v.min()), float(v.max()))
    u_lo, u_hi, v_lo, v_hi = view_box

    # Work on the view neighbourhood only (30% margin): the colour range and
    # the triangulation both stay local to what the figure shows.
    margin_u = 0.3 * (u_hi - u_lo)
    margin_v = 0.3 * (v_hi - v_lo)
    near = ((u >= u_lo - margin_u) & (u <= u_hi + margin_u)
            & (v >= v_lo - margin_v) & (v <= v_hi + margin_v))
    if near.sum() < 3:
        return None
    u, v, values, footprint = u[near], v[near], values[near], footprint[near]

    triangulation = Triangulation(u, v)
    tris = triangulation.triangles
    edge = np.zeros(len(tris))
    for a, b in ((0, 1), (1, 2), (2, 0)):
        edge = np.maximum(edge, np.hypot(u[tris[:, a]] - u[tris[:, b]],
                                         v[tris[:, a]] - v[tris[:, b]]))
    # A triangle whose longest edge outruns the local cell size bridges a
    # hole in the fluid: the body cross-section. Masked triangles are simply
    # not drawn, so the silhouette shows as the dark figure background.
    local = footprint[tris].max(axis=1)
    triangulation.set_mask(edge > 2.6 * np.maximum(local, 1e-12))

    # Robust colour range about zero gauge pressure: percentiles keep one
    # stagnation spike from flattening the whole field, and the diverging map
    # is anchored at p = 0 so blue is always suction and red always
    # compression, matching the painted body.
    in_view = ((u >= u_lo) & (u <= u_hi) & (v >= v_lo) & (v <= v_hi))
    ranged = values[in_view] if in_view.sum() >= 16 else values
    lo = float(np.percentile(ranged, 1.0))
    hi = float(np.percentile(ranged, 99.5))
    tiny = max(1e-9, 1e-4 * (abs(lo) + abs(hi)))
    lo = min(lo, -tiny)
    hi = max(hi, tiny)

    plt = _pyplot()
    cmap = LinearSegmentedColormap.from_list("controlroom-pressure",
                                             list(_SLICE_ANCHORS))
    norm = TwoSlopeNorm(vmin=lo, vcenter=0.0, vmax=hi)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    levels = np.concatenate([np.linspace(lo, 0.0, 21)[:-1],
                             np.linspace(0.0, hi, 21)])
    contour = ax.tricontourf(triangulation, values, levels=levels, cmap=cmap,
                             norm=norm, extend="both")

    # One annotated key value: the stagnation peak, the warmest point of the
    # whole field, where the flow comes to rest on the nose.
    peak_pool = np.flatnonzero(in_view) if in_view.sum() >= 16 else np.arange(values.size)
    peak = int(peak_pool[np.argmax(values[peak_pool])])
    annotation = (rf"stagnation peak  $p/\rho$ = {values[peak]:,.0f}"
                  r" $\mathrm{m^2/s^2}$")
    ax.annotate(annotation, xy=(u[peak], v[peak]),
                xytext=(0.03, 0.94), textcoords="axes fraction",
                ha="left", va="top", fontsize=12, color=INK, weight="bold",
                arrowprops={"arrowstyle": "-", "color": MUTED,
                            "linewidth": 0.9, "alpha": 0.8})

    title = SLICE_TITLE + (f": {body_label}" if body_label else "")
    style_axes(ax, xlabel, ylabel, title)
    ax.grid(False)  # gridlines over a filled field are clutter, ticks stay
    ax.set_xlim(u_lo, u_hi)
    ax.set_ylim(v_lo, v_hi)
    ax.set_aspect("equal", adjustable="box")

    colorbar_label = (r"static pressure  $p/\rho$  [$\mathrm{m^2/s^2}$]")
    cbar = fig.colorbar(contour, ax=ax, pad=0.02, fraction=0.05)
    cbar.set_label(colorbar_label, color=INK, fontsize=11)
    cbar.ax.tick_params(colors=MUTED, labelsize=9)
    cbar.outline.set_edgecolor(DIM)

    # Units stated plainly: the incompressible solver carries p over rho.
    note = ("Incompressible solve: p is kinematic pressure, p over rho; "
            "multiply by rho = 1.2 kg/m3 (air) for Pa.\n"
            "Red high, blue low; the dark silhouette is the body "
            "cross-section." + (f" {station_note}" if station_note else ""))
    fig.text(0.01, 0.008, note, color=MUTED, fontsize=8.5,
             family="monospace", va="bottom")

    fig.tight_layout(rect=(0, 0.05, 1, 1))
    out_png = Path(out_png)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png)
    plt.close(fig)
    return {"path": str(out_png), "title": title, "xlabel": xlabel,
            "ylabel": ylabel, "colorbar": colorbar_label, "note": note,
            "annotation": annotation, "stagnation": float(values[peak]),
            "value_range": (lo, hi)}


_AXIS_NAMES = "xyz"


def render_pressure_slice(vtu_path: str | Path, out_png: str | Path, *,
                          span_axis: int, plane_axes=None, body_bounds=None,
                          body_label: str = "", figsize=(11.4, 6.2),
                          dpi: int = 150, field: str = "p") -> dict | None:
    """Extract the mid-span slab from a volume file and render the contour.

    ``span_axis`` is the axis the slicing plane is normal to; ``plane_axes``
    the (horizontal, vertical) in-plane axes, defaulting to the remaining two
    in order. ``body_bounds`` (the painted-surface payload's ``bounds``) sets
    the slice station at the body's own mid-span and frames the view on the
    body; without it both fall back to the fluid domain itself.
    """
    import numpy as np

    volume = read_volume_field(vtu_path, field)
    if volume is None:
        return None
    points, connectivity, offsets, values = volume
    centres, extents = cell_centres(points, connectivity, offsets)
    if len(centres) == 0 or len(values) < len(centres):
        return None
    values = values[:len(centres)]

    if plane_axes is None:
        plane_axes = tuple(a for a in range(3) if a != span_axis)
    axis_u, axis_v = plane_axes

    if body_bounds:
        b_lo, b_hi = body_bounds["min"], body_bounds["max"]
        station = 0.5 * (b_lo[span_axis] + b_hi[span_axis])
        span = max(b_hi[span_axis] - b_lo[span_axis], 1e-9)
    else:
        domain_lo = points.min(axis=0)
        domain_hi = points.max(axis=0)
        station = 0.5 * (domain_lo[span_axis] + domain_hi[span_axis])
        span = max(domain_hi[span_axis] - domain_lo[span_axis], 1e-9)

    keep, half_used = pick_slice(
        centres, extents, axis=span_axis, station=station,
        half_thickness=SLICE_HALF_THICKNESS_FRACTION * span)
    if keep.size < 3:
        return None

    u = centres[keep, axis_u]
    v = centres[keep, axis_v]
    footprint = np.maximum(extents[keep, axis_u], extents[keep, axis_v])

    if body_bounds:
        # Frame on the body: room ahead and above, more behind for the wake.
        lu = max(b_hi[axis_u] - b_lo[axis_u], 1e-9)
        lv = max(b_hi[axis_v] - b_lo[axis_v], 1e-9)
        cv = 0.5 * (b_lo[axis_v] + b_hi[axis_v])
        half_v = 0.65 * max(lu, lv)
        view = [b_lo[axis_u] - 0.50 * lu, b_hi[axis_u] + 0.90 * lu,
                cv - half_v, cv + half_v]
    else:
        # No body bounds on file: frame on the refined region, which hugs the
        # body (the finest cells are the ones snapped to the surface).
        fine = footprint <= 4.0 * max(float(footprint.min()), 1e-12)
        fu, fv = (u[fine], v[fine]) if fine.sum() >= 8 else (u, v)
        lu = max(float(fu.max() - fu.min()), 1e-9)
        lv = max(float(fv.max() - fv.min()), 1e-9)
        view = [float(fu.min()) - 0.3 * lu, float(fu.max()) + 0.5 * lu,
                float(fv.min()) - 0.3 * lv, float(fv.max()) + 0.3 * lv]
    # The view never reaches outside the fluid that was actually sliced.
    view[0] = max(view[0], float(u.min()))
    view[1] = min(view[1], float(u.max()))
    view[2] = max(view[2], float(v.min()))
    view[3] = min(view[3], float(v.max()))

    station_note = (f"Slice: {_AXIS_NAMES[span_axis]} = {station:.2f} m, "
                    + ("the cell layer crossing the plane."
                       if half_used == 0.0 else
                       f"slab widened to {2 * half_used:.3g} m."))
    return render_slice_figure(
        u, v, values[keep], footprint, out_png,
        xlabel=f"{_AXIS_NAMES[axis_u]}  [m]",
        ylabel=f"{_AXIS_NAMES[axis_v]}  [m]",
        body_label=body_label, station_note=station_note, view_box=view,
        figsize=figsize, dpi=dpi)


def extract_pressure_slice(remote_case: str, out_png: str | Path, wsl_prefix,
                           *, span_axis: int, plane_axes=None,
                           body_bounds=None, body_label: str = "") -> str | None:
    """Fetch the case's volume output and render the mid-span pressure slice.

    The volume file (``internal.vtu``) comes from the same ``foamToVTK`` run
    :func:`extract_and_paint` already performed, so this never re-solves and
    never re-meshes; it only copies one file out of the compute node. A held
    case with no volume output on disk (runs older than the volume writer)
    returns None and the act simply carries no slice plot.
    """
    import subprocess
    import tempfile

    staging = Path(tempfile.mkdtemp())
    local = _wsl_out(staging)
    # Same constraint as extract_and_paint: the wsl argument layer eats $
    # expressions, so this is a plain glob copy. foamToVTK -latestTime writes
    # exactly one time directory with a volume file, so the glob is single.
    command = (f"cd {remote_case} && "
               f"cp VTK/*/internal.vtu '{local}/volume.vtu' 2>/dev/null; "
               f"test -s '{local}/volume.vtu' && echo OK")
    try:
        result = subprocess.run([*wsl_prefix, "bash", "-c", command],
                                capture_output=True, text=True, timeout=600)
    except Exception:
        return None
    if "OK" not in result.stdout:
        return None
    try:
        meta = render_pressure_slice(
            staging / "volume.vtu", out_png, span_axis=span_axis,
            plane_axes=plane_axes, body_bounds=body_bounds,
            body_label=body_label)
    except Exception:
        _log.warning("pressure-slice render failed for %s", remote_case,
                     exc_info=True)
        return None
    finally:
        try:
            (staging / "volume.vtu").unlink()
        except OSError:
            pass
    return meta["path"] if meta else None
