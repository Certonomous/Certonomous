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


def _patch_cell_values(vtp_path: str | Path, field: str) -> list[float] | None:
    """The solver's OWN per-wall-face values for one patch, or None.

    ``_read_patch`` above prefers the per-POINT array because interpolating
    it to face centres gives the smooth surface the viewport wants. That
    averaging is a display choice, and it is lossy at exactly the place that
    matters: a stagnation peak sits on one wall face, and every node of that
    face is shared with cooler neighbours, so the nodal round trip shaves the
    peak before any decimation has even run. Measured on the NACA 4412 wing,
    the solver's own wall maximum is p/rho 100.09 and the nodal-averaged
    version of the same patch reads 95.66, which at q 112.5 is Cp 0.889
    against 0.850.

    So the reported physics is read from ``CellData`` instead: those are the
    finite-volume wall values the solver actually wrote, one per boundary
    face, with no interpolation anywhere in the path. Returns one value per
    source polygon (not per fan triangle, which is the same set of numbers
    and therefore the same extremes), or None when the file carries no cell
    array for this field, in which case the caller falls back to the nodal
    per-face values.
    """
    try:
        text = Path(vtp_path).read_text(errors="replace")
    except OSError:
        return None
    header_bytes = 8 if (_HEADER_TYPE.search(text) or [""])[0] == "UInt64" or \
        "header_type='UInt64'" in text else 4
    cell_section = _CELLDATA.search(text)
    if not cell_section:
        return None
    values = _named(cell_section.group(0), field, header_bytes)
    return list(values) if values else None


# The incompressible stagnation bound. With p_inf as the reference pressure
# and q = U^2/2 the kinematic dynamic pressure, no point in a steady
# incompressible flow with no energy addition can exceed Cp = 1: that is the
# whole freestream kinetic energy converted to pressure. A wall value above it
# is not a pressure, it is a numerical artifact, and in practice it means
# degenerate cells.
CP_STAGNATION_BOUND = 1.0
# There is NO corresponding hard lower bound. Incompressible potential flow
# over a circular cylinder already reaches Cp -3, and real accelerating
# corners go lower, so a large negative Cp is not by itself a defect. This
# threshold is therefore a mesh-degeneracy SIGNAL, not a violation test: it
# counts how much of the surface sits in territory that is possible but
# strongly suggestive of sliver cells when it appears on a handful of faces.
CP_SUCTION_OUTLIER = -2.0


def cp_bound_report(values, *, q: float, p_inf: float = 0.0,
                    bound: float = CP_STAGNATION_BOUND,
                    suction_outlier: float = CP_SUCTION_OUTLIER
                    ) -> dict[str, Any] | None:
    """Check a wall field's reported extremes against the Cp = 1 bound.

    ``values`` are the solver's own per-wall-face kinematic pressures, the
    same undecimated list the reported physical range is taken from. Cp is
    ``(p - p_inf) / q``.

    This never alters a measured value. It is a disclosure: the physical
    range must stay exactly what the solver wrote, and a consumer that is
    about to display it needs to know when that number is outside what
    incompressible flow permits. A bound-violating maximum means the mesh has
    degenerate faces, so the report carries what a caller needs to choose
    between the two honest presentations:

    * the robust colour window (``color_min``/``color_max``) with the
      violation disclosed, or
    * the raw extreme with ``caveat`` attached as the mesh caveat.

    ``max_cp_within_bound`` supports a third, narrower option: the largest
    value on the body that IS physically admissible, which on the motorbike
    is the real stagnation peak of Cp 0.992 sitting under a single sliver-cell
    face at 1.119.

    Returns None when ``q`` is missing or not positive, since Cp is undefined
    without it.
    """
    if not values or not q or q <= 0:
        return None
    total = len(values)
    cps = [(v - p_inf) / q for v in values]
    over = [c for c in cps if c > bound]
    under = [c for c in cps if c < suction_outlier]
    within = [c for c in cps if c <= bound]
    cp_max, cp_min = max(cps), min(cps)
    report: dict[str, Any] = {
        "q_kinematic": q,
        "p_inf": p_inf,
        "faces": total,
        "min": cp_min,
        "max": cp_max,
        "stagnation_bound": bound,
        # The headline flag. False means the reported physical maximum is not
        # a physically attainable pressure.
        "within_stagnation_bound": not over,
        "over_bound": {
            "count": len(over),
            "fraction": len(over) / total,
            "extreme_cp": cp_max if over else None,
            "max_cp_within_bound": max(within) if within else None,
        },
        "suction_outliers": {
            "threshold_cp": suction_outlier,
            "count": len(under),
            "fraction": len(under) / total,
            "extreme_cp": cp_min if under else None,
            "note": ("Cp has no hard lower bound (potential flow over a "
                     "cylinder reaches -3), so this is a mesh-degeneracy "
                     "signal, not a bound violation."),
        },
    }
    if over:
        report["caveat"] = (
            f"Reported physical maximum Cp {cp_max:.3f} exceeds the "
            f"incompressible stagnation bound of {bound:g} on {len(over)} of "
            f"{total} wall faces ({100 * len(over) / total:.3f}%). Values "
            "above the bound are degenerate sliver cells, a mesh quality "
            "defect, not a physical pressure. The highest bound-respecting "
            f"value on this body is Cp {max(within):.3f}. Present either the "
            "robust colour window with this disclosed, or the raw extreme "
            "with this caveat attached.")
    return report


# Which quantity a painted payload is carrying, stated on the payload itself
# as ``field["quantity"]`` rather than inferred from the legend string. A
# consumer must never have to guess whether it is holding a pressure or a
# coefficient: the two differ by an offset and a scale, and reading one as
# the other misstates every number on the legend.
QUANTITY_PRESSURE = "pressure"
QUANTITY_CP = "cp"
# The legend name carried when the coefficient is the one being drawn. The
# control room prints this string verbatim, so it has to read as a
# dimensionless coefficient and never as pressure in Pa. It is written in the
# same underscore form every table cell uses, so the symbol typesets with its
# subscript wherever the label is rendered.
CP_FIELD_NAME = "C_p"


def load_field_surface(sources, *, field: str = "p",
                       max_faces: int = 30000, name: str = "surface",
                       q_kinematic: float | None = None,
                       p_inf: float = 0.0, as_cp: bool = False,
                       view: dict[str, Any] | None = None) -> dict[str, Any]:
    """Read one patch file or merge several into a painted wireframe payload.

    ``q_kinematic`` (and optionally ``p_inf``) turn on the Cp bound check on
    the reported physical range, attached as ``field["cp"]``. Without them Cp
    is undefined, so the block is simply absent and the payload is exactly
    what it was before.

    ``as_cp`` is a separate switch, and it is the only thing that changes a
    displayed number. It normalises the field to the pressure coefficient
    ``(p - p_inf) / q`` before anything downstream sees it, so the drawn
    faces, the colour window and the reported physical extremes are all the
    coefficient and cannot disagree with each other.

    It is a TOGGLE, not a migration. Pressure is the default and stays fully
    supported: a caller that does not ask gets the pressure it got before,
    value for value. The two are equally first class, and either can be
    chosen per act.

    The choice is never left to be inferred. The payload states which
    quantity it is carrying as ``field["quantity"]``, one of
    :data:`QUANTITY_PRESSURE` or :data:`QUANTITY_CP`, so a legend can be
    labelled from the payload rather than from a guess. Asking for the
    coefficient without a positive ``q_kinematic`` is not an error and not a
    warning: Cp is undefined without it, so the pressure is drawn instead and
    ``field["quantity"]`` says ``pressure``. A caller that narrates what it
    drew reads that key rather than assuming it got what it asked for.

    The bound check is deliberately NOT folded into the conversion. It keeps
    running on the pressures the solver wrote, with ``q_kinematic`` and
    ``p_inf`` as given, so ``field["cp"]`` reports the same numbers and raises
    the same flag whichever quantity is on the screen.

    ``view`` is the control room's optional camera hint (``flat``, ``axes``),
    passed straight through onto the payload. Omitted when None, which is what
    every caller that does not pass one still sends.
    """
    paths = [sources] if isinstance(sources, (str, Path)) else list(sources)
    all_v: list[list[float]] = []
    all_f: list[list[int]] = []
    all_field: list[float] = []
    all_physical: list[float] = []
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
        # The reported physics comes from the solver's own wall-face values
        # where the file carries them, and only falls back to the nodal path
        # when it does not.
        cell_values = _patch_cell_values(path, field)
        if cell_values:
            all_physical.extend(cell_values)
        elif values and len(values) == len(faces):
            all_physical.extend(values)
    # The pressures the solver wrote, kept aside whatever the display does
    # with them: the bound check below is graded on these and only these.
    raw_field, raw_physical = all_field, all_physical
    to_cp = bool(as_cp) and bool(q_kinematic) and q_kinematic > 0
    if to_cp:
        # Normalise BEFORE the packager: the decimated display values are a
        # mean over merged source faces, and a mean commutes with this affine
        # map, so converting here and converting after clustering give the
        # same drawn face. Converting here also means the undecimated list the
        # physical range is read from is the same coefficient as the picture,
        # which is the whole point: the legend's extremes and the colours
        # cannot drift into different units.
        all_field = [(v - p_inf) / q_kinematic for v in all_field]
        all_physical = [(v - p_inf) / q_kinematic for v in all_physical]
    payload, display_values = _package_painted(all_v, all_f, all_field, max_faces, name)
    # The reported physical extremes are taken UNDECIMATED and UNINTERPOLATED,
    # before clustering has seen the data, so no display simplification can
    # change the physics the JSON claims to carry. ``display_values`` must
    # never be the source: for any body over ``max_faces`` those have already
    # been through vertex-clustering aggregation, which averages a stagnation
    # peak into its cooler neighbours (see ``_package_painted``'s docstring).
    source = all_physical or all_field
    physical_range = (min(source), max(source)) if source else None
    # The bound check runs on the very same undecimated population the
    # reported range comes from, so the flag can never describe a different
    # set of faces than the number it qualifies. It reads the pressures, not
    # the normalised display, so its own arithmetic is unchanged by ``as_cp``.
    cp_report = (cp_bound_report(raw_physical or raw_field,
                                 q=q_kinematic, p_inf=p_inf)
                 if q_kinematic else None)
    _attach_field(payload, display_values,
                  CP_FIELD_NAME if to_cp else field,
                  physical_range=physical_range, cp_report=cp_report,
                  # A coefficient lives in a span of about two, so one decimal
                  # would collapse the whole legend into three or four labels.
                  decimals=3 if to_cp else 1,
                  quantity=QUANTITY_CP if to_cp else QUANTITY_PRESSURE)
    if view:
        payload["view"] = view
    return payload


def _package_painted(vertices, faces, face_values, max_faces: int, name: str):
    """Package a mesh for the viewport with field values tracking the decimation.

    Returns ``(payload, display_values)`` where ``display_values`` has exactly
    one value per face in ``payload["faces"]``.

    Below the decimation threshold this defers to :func:`geometry._package`
    unchanged and passes the per-face values straight through — the pipeline
    for non-decimated bodies (the B-52's 15,684 merged patch faces, the NACA
    sections) is byte-identical, which is the frozen-rendering acceptance bar.
    The motorbike is NOT one of them: its 72 patches merge to 101,137 faces
    and take the decimated branch below.

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


def _attach_field(payload: dict[str, Any], face_values, field: str, *,
                  physical_range: tuple[float, float] | None = None,
                  cp_report: dict[str, Any] | None = None,
                  decimals: int = 1,
                  quantity: str = QUANTITY_PRESSURE) -> None:
    """Carry a normalised field value per kept face, plus two distinct ranges.

    ``face_values`` must already be one-to-one with ``payload["faces"]`` —
    :func:`_package_painted` guarantees that for both the decimated and the
    untouched path.

    Two ranges are reported, and a future consumer must not confuse them:

    * ``min``/``max``: the PHYSICAL range, the true extremes of the solved
      field, i.e. what the solver actually computed. When ``physical_range``
      is given (the caller's undecimated, pre-clustering per-face values)
      that is what is reported; a decimated body's averaged display faces
      never get to define the physical extremes, since clustering dilutes a
      sharp stagnation peak into its cooler neighbours. When the caller has
      no undecimated data to hand (e.g. a direct unit-test call), this falls
      back to the true min/max of ``face_values`` itself, never to the
      clipped percentiles below, so this key is always an unclipped extreme.
    * ``color_min``/``color_max`` (aliased as ``display_min``/``display_max``
      for the existing GUI legend): a robust 2nd/98th percentile CLIP, so a
      single stagnation spike does not flatten the whole surface to one
      colour. This is a display device only. Anything that renders a
      colorbar must label it as the display/color-mapping range, never as
      the field's maximum. A colorbar stating the clipped high as "the"
      maximum misinforms the viewer about the true peak pressure.

    ``cp_report`` (from :func:`cp_bound_report`) rides along as ``cp`` when
    given: it does not change any reported value, it discloses whether the
    physical maximum is inside the Cp = 1 stagnation bound.

    ``decimals`` rounds the colour-window labels only. One decimal is right
    for a kinematic pressure in the hundreds and useless for a coefficient
    that spans about two, so a caller drawing a coefficient asks for more.

    ``quantity`` states which of the two the numbers above are, so nothing
    downstream has to infer it from the legend name.
    """
    if not face_values:
        payload["field"] = None
        return
    sampled = face_values
    # Clip to robust percentiles for the COLOUR MAP only: a single stagnation
    # spike would otherwise flatten the whole surface to one colour. The
    # 2nd/98th keep the real pressure variation across the wings and body
    # visible. This clipped pair must never be reported as the field's
    # physical min/max (that was the bug: it understated every published
    # peak pressure by clipping away the real extreme and then mislabeling
    # the clipped value as the maximum).
    ordered = sorted(sampled)
    color_lo = ordered[max(0, int(0.02 * len(ordered)))]
    color_hi = ordered[min(len(ordered) - 1, int(0.98 * len(ordered)))]
    span = (color_hi - color_lo) or 1.0
    if physical_range is not None:
        true_min, true_max = physical_range
    else:
        true_min, true_max = min(sampled), max(sampled)
    payload["field"] = {
        "name": field,
        # Pressure or coefficient, stated rather than inferred.
        "quantity": quantity,
        # Physical range: the solver's own unclipped extremes. This is what
        # any reported/published Cp_max or Cp_min must be read from.
        "min": true_min,
        "max": true_max,
        # 0..1 per drawn face, for the colormap in the browser. Normalised
        # against the CLIPPED color range, not the physical one, so one
        # stagnation spike does not wash out the rest of the surface.
        "values": [round(min(1.0, max(0.0, (v - color_lo) / span)), 4)
                   for v in sampled],
        # Color-mapping range only (clipped percentiles): label any colorbar
        # built from this as the display range, not the field's maximum.
        "color_min": round(color_lo, decimals), "color_max": round(color_hi, decimals),
        "display_min": round(color_lo, decimals), "display_max": round(color_hi, decimals),
    }
    if cp_report is not None:
        # A disclosure attached to the physical range, never a correction to
        # it: the values above stay exactly what the solver wrote.
        payload["field"]["cp"] = cp_report


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
                      min_fraction: float = 0.15,
                      q_kinematic: float | None = None,
                      p_inf: float = 0.0, as_cp: bool = False,
                      view: dict[str, Any] | None = None,
                      patches: tuple[str, ...] | None = None) -> str | None:
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

    ``patches`` names the patch stems to paint outright, bypassing the
    domain-boundary reduction above. It exists for the wall-bounded cases: on
    the NASA hump the body IS the tunnel floor, and the floor is called
    ``bottom``, which the blocklist correctly reads as a domain boundary for
    every free-flying body and wrongly for this one. Naming the patch is
    honest and specific; loosening the blocklist would let a flat domain
    rectangle through on every other act. Omitted, the automatic reduction
    runs exactly as before.

    ``as_cp`` and ``view`` are forwarded to :func:`load_field_surface`; see
    there for why the coefficient is opt-in.
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
    available = list(staging.glob("*.vtp"))
    if patches:
        wanted = {stem.strip().lower() for stem in patches}
        selected = [p for p in available if p.stem.lower() in wanted]
        if not selected:
            _log.warning("field-paint: none of the named patches %s were "
                         "written for this case, falling back to wireframe",
                         sorted(wanted))
            return None
    else:
        selected = _body_patches(available)
    if not selected:
        _log.warning("field-paint patch selection suspect: no body patch left "
                     "after excluding domain boundaries, falling back to wireframe")
        return None
    payload = load_field_surface(selected, field=field, name=name,
                                 q_kinematic=q_kinematic, p_inf=p_inf,
                                 as_cp=as_cp, view=view)
    if not payload.get("field"):
        return None
    cp = (payload.get("field") or {}).get("cp")
    if cp and not cp["within_stagnation_bound"]:
        # Surfaced in the log as well as the JSON: a bound-violating wall
        # value is a mesh quality signal and should not need a JSON reader to
        # be noticed.
        _log.warning("field-paint: %s reported physical Cp_max %.3f exceeds "
                     "the stagnation bound on %d of %d wall faces (%.3f%%) - "
                     "degenerate cells; highest admissible value is Cp %.3f",
                     name, cp["max"], cp["over_bound"]["count"], cp["faces"],
                     100 * cp["over_bound"]["fraction"],
                     cp["over_bound"]["max_cp_within_bound"])
    # Face-count sanity check: the painted body should be a large fraction of
    # the input surface, not a handful of flat domain rectangles.
    body_faces = int(payload.get("triangles_total", 0))
    if input_triangles:
        fraction = body_faces / max(1, input_triangles)
        if fraction < min_fraction:
            _log.warning(
                "field-paint patch selection suspect: painted body has %d faces, "
                "only %.0f%% of the %d input triangles (floor %.0f%%) from patches "
                "%s, falling back to wireframe",
                body_faces, 100 * fraction, input_triangles, 100 * min_fraction,
                sorted(q.stem for q in selected))
            return None
        _log.info("field-paint: painted body has %d faces from %d patches "
                  "(%.0f%% of %d input triangles)",
                  body_faces, len(selected), 100 * fraction, input_triangles)
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

# Diverging pressure map: the classic cool-to-warm CFD ramp (deep blue
# through a light neutral midpoint to deep red), the same character as the
# approved painted-sail render and the standard solver-viewer look. Red is
# high, blue is low, matching the painted-body convention; the midpoint is a
# neutral, never a hue; the body cross-section is a dark filled silhouette.
_SLICE_CMAP = "coolwarm"
# The interpolation grid the slice field is resampled onto before shading:
# fine enough that the field reads as a continuous physical gradient, not
# poster bands of raw solver cells.
SLICE_GRID_SHAPE = (800, 1200)


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


def load_surface_mesh(path: str | Path, scale: float = 1.0):
    """Load an STL/OBJ surface as numpy ``(vertices, faces)`` for slicing.

    Reuses the act's own surface readers, then applies the same uniform scale
    the case build applied, so the cross-section lands in solved-case
    coordinates. Returns None when the surface cannot be read.
    """
    import numpy as np

    from .geometry import _read_obj, _read_stl

    path = Path(path)
    try:
        if path.suffix.lower() == ".obj":
            vertices, faces = _read_obj(path)
        elif path.suffix.lower() == ".stl":
            vertices, faces = _read_stl(path)
        else:
            return None
    except Exception:
        return None
    if not vertices or not faces:
        return None
    return (np.asarray(vertices, dtype=np.float64) * float(scale),
            np.asarray(faces, dtype=np.int64))


def surface_cross_section(vertices, faces, *, axis: int, station: float,
                          plane_axes) -> list:
    """The body's exact cross-section: surface mesh intersected with a plane.

    Every triangle crossing ``axis = station`` contributes one segment; the
    segments are chained end to end (by quantized coordinates, so the
    unwelded duplicate vertices STL files carry do not break the chain) into
    ordered loops. The loops are the true section outline - a NACA profile
    comes out as the textbook shape - independent of how coarsely the volume
    mesh sampled the fluid around it. Returns a list of (K, 2) point loops
    in ``plane_axes`` coordinates; watertight surfaces yield closed loops.
    """
    import numpy as np
    from collections import defaultdict

    verts = np.asarray(vertices, dtype=np.float64)
    tris = np.asarray(faces, dtype=np.int64)
    if len(verts) == 0 or len(tris) == 0:
        return []
    span = float(verts[:, axis].max() - verts[:, axis].min()) or 1.0
    d = verts[:, axis] - station
    # A vertex exactly on the plane would make a degenerate zero-length
    # segment; nudging it to one side keeps every crossing a clean two-point
    # cut without moving anything visibly (a billionth of the span).
    d = np.where(d == 0.0, 1e-9 * span, d)

    ax_u, ax_v = plane_axes
    face_ids: list = []
    cut_pts: list = []
    for a, b in ((0, 1), (1, 2), (2, 0)):
        da, db = d[tris[:, a]], d[tris[:, b]]
        crossing = (da * db) < 0.0
        if not crossing.any():
            continue
        t = (da[crossing] / (da[crossing] - db[crossing]))[:, None]
        pa = verts[tris[crossing, a]]
        pb = verts[tris[crossing, b]]
        cut = pa + t * (pb - pa)
        face_ids.append(np.flatnonzero(crossing))
        cut_pts.append(cut[:, [ax_u, ax_v]])
    if not face_ids:
        return []
    face_ids = np.concatenate(face_ids)
    cut_pts = np.concatenate(cut_pts)

    per_face: dict[int, list] = defaultdict(list)
    for face, point in zip(face_ids.tolist(), cut_pts):
        per_face[face].append(point)
    segments = [pair for pair in per_face.values() if len(pair) == 2]
    if not segments:
        return []

    # Chain segments into loops by quantized endpoints.
    diag = float(np.hypot(cut_pts[:, 0].max() - cut_pts[:, 0].min(),
                          cut_pts[:, 1].max() - cut_pts[:, 1].min())) or 1.0
    tol = 1e-6 * diag

    def keyed(point) -> tuple[int, int]:
        return (int(round(point[0] / tol)), int(round(point[1] / tol)))

    links: dict[tuple[int, int], list] = defaultdict(list)
    for index, (p, q) in enumerate(segments):
        links[keyed(p)].append((index, 0))
        links[keyed(q)].append((index, 1))

    used = [False] * len(segments)
    loops: list = []
    for start in range(len(segments)):
        if used[start]:
            continue
        used[start] = True
        p, q = segments[start]
        chain = [p, q]
        cursor = keyed(q)
        home = keyed(p)
        while cursor != home:
            follow = next(((i, e) for i, e in links[cursor] if not used[i]),
                          None)
            if follow is None:
                break  # an open chain from a non-watertight patch: kept as-is
            index, end = follow
            used[index] = True
            nxt = segments[index][1 - end]
            chain.append(nxt)
            cursor = keyed(nxt)
        if cursor == home:
            chain = chain[:-1] if len(chain) > 1 and keyed(chain[-1]) == home \
                else chain
        if len(chain) >= 3:
            loops.append(np.asarray(chain, dtype=np.float64))
    return loops


def _box_sum(grid, radius: int, axis: int):
    """Windowed sum over ``2*radius + 1`` samples along one axis (zero pad)."""
    import numpy as np

    pad = [(0, 0), (0, 0)]
    pad[axis] = (radius + 1, radius)
    summed = np.cumsum(np.pad(grid, pad), axis=axis)
    window = 2 * radius + 1
    if axis == 0:
        return summed[window:, :] - summed[:-window, :]
    return summed[:, window:] - summed[:, :-window]


def _smooth_grid(filled, weight, radius: int = 3, passes: int = 2):
    """Gentle normalized smoothing of the resampled field.

    A separable box blur repeated ``passes`` times (a triangular kernel, close
    to a small gaussian) with the data-coverage ``weight`` blurred alongside,
    so regions without data pull no value in and edges stay honest. Pure
    numpy: the demo machine carries no scipy. This is what removes the
    single-cell freckles the near-wall layers leave in the resampled field
    while leaving the real gradients (a stagnation spot is dozens of grid
    cells wide) untouched.
    """
    import numpy as np

    smoothed = filled * weight
    mass = weight.astype(np.float64)
    for _ in range(passes):
        for axis in (0, 1):
            smoothed = _box_sum(smoothed, radius, axis)
            mass = _box_sum(mass, radius, axis)
    return np.where(mass > 1e-12, smoothed / np.maximum(mass, 1e-12), 0.0)


# ---------------------------------------------------------------------------
# Streamline overlay: the flow's own paths over the pressure shading
# ---------------------------------------------------------------------------
# The volume output carries U alongside p, so the same mid-span slice that
# shades the static pressure can carry the flow's actual paths: a handful of
# thin, translucent strokes seeded on an upstream column, denser toward the
# body so the bending around the section is where the eye lands, integrated
# left to right by matplotlib's streamplot on the same fine grid as the
# pressure fill. The strokes stay quiet so they never fight the colour field.
_STREAM_COLOR = "#545a61"    # plot_theme.DIM: slate strokes over the field
STREAM_LINEWIDTH = 0.8
STREAM_ALPHA = 0.6
STREAM_SEEDS = 15            # odd, so the stagnation streamline is seeded
STREAM_DENSITY = 3.0


def silhouette_mask(points_xy, silhouette):
    """Even-odd inside mask of flat (N, 2) points against the section loops.

    The exact body mask of the slice figure, extracted pure so the pressure
    fill and the streamline velocity mask share one definition: a point is
    inside when an odd number of loops contain it, so a loop inside a loop
    (a hub inside a tyre) carves fluid back out. Returns a bool (N,) array.
    """
    import numpy as np
    from matplotlib.path import Path as MplPath

    flat = np.asarray(points_xy, dtype=np.float64)
    inside = np.zeros(len(flat), dtype=bool)
    for loop in silhouette or []:
        loop = np.asarray(loop, dtype=np.float64)
        if len(loop) < 3:
            continue
        boxed = ((flat[:, 0] >= loop[:, 0].min())
                 & (flat[:, 0] <= loop[:, 0].max())
                 & (flat[:, 1] >= loop[:, 1].min())
                 & (flat[:, 1] <= loop[:, 1].max()))
        if not boxed.any():
            continue
        hits = MplPath(loop).contains_points(flat[boxed])
        inside[np.flatnonzero(boxed)[hits]] ^= True
    return inside


def read_volume_vector(vtu_path: str | Path, field: str = "U"):
    """Read points, cells, and one cell-centred VECTOR field from a .vtu.

    Same reader as :func:`read_volume_field`; the flat value stream is
    reshaped to (C, 3), which is how foamToVTK writes U. Returns
    ``(points (N,3), connectivity, offsets, vectors (C,3))`` or None.
    """
    volume = read_volume_field(vtu_path, field)
    if volume is None:
        return None
    points, connectivity, offsets, values = volume
    if values.size == 0 or values.size % 3 != 0:
        return None
    return points, connectivity, offsets, values.reshape(-1, 3)


def inplane_velocity_grid(u, v, vel_u, vel_v, grid_x, grid_y, body_mask=None):
    """Interpolate scattered in-plane velocity components onto the fine grid.

    The same linear triangulated interpolation the pressure shading uses,
    applied to both in-plane components of the cell-centre velocity. Grid
    points with no data (outside the slice's hull) or inside the body mask
    come out NaN, so the streamline integrator terminates there instead of
    stepping through the section. Returns ``(uu, vv)`` float arrays of shape
    ``(len(grid_y), len(grid_x))``.
    """
    import numpy as np
    from matplotlib.tri import LinearTriInterpolator, Triangulation

    u = np.asarray(u, dtype=np.float64)
    v = np.asarray(v, dtype=np.float64)
    triangulation = Triangulation(u, v)
    mesh_x, mesh_y = np.meshgrid(np.asarray(grid_x, dtype=np.float64),
                                 np.asarray(grid_y, dtype=np.float64))
    uu = LinearTriInterpolator(
        triangulation, np.asarray(vel_u, dtype=np.float64))(mesh_x, mesh_y)
    vv = LinearTriInterpolator(
        triangulation, np.asarray(vel_v, dtype=np.float64))(mesh_x, mesh_y)
    uu = uu.filled(np.nan)
    vv = vv.filled(np.nan)
    if body_mask is not None:
        uu[body_mask] = np.nan
        vv[body_mask] = np.nan
    return uu, vv


def streamline_seeds(view_box, *, center_v: float | None = None,
                     n_lines: int = STREAM_SEEDS, x_fraction: float = 0.02,
                     cluster: float = 2.2):
    """Seed points on an upstream column, denser toward the body centreline.

    Seeds sit just inside the left edge of the view so every line flows left
    to right. Their vertical spacing follows a sinh map about ``center_v``
    (the body's own centreline): tight near the body where the flow bends,
    sparse in the far field where the lines run straight. ``n_lines`` is
    forced odd so the exact centreline (the stagnation streamline) is always
    seeded. Returns an (n, 2) array of (x, y) points inside the view.
    """
    import numpy as np

    u_lo, u_hi, v_lo, v_hi = (float(x) for x in view_box)
    if center_v is None:
        center_v = 0.5 * (v_lo + v_hi)
    n = max(3, int(n_lines) | 1)
    x0 = u_lo + float(x_fraction) * (u_hi - u_lo)
    t = np.linspace(-1.0, 1.0, n)
    shaped = np.sinh(cluster * t) / math.sinh(cluster)
    half = max(v_hi - center_v, center_v - v_lo)
    ys = center_v + half * shaped
    pad = 0.02 * (v_hi - v_lo)
    keep = (ys >= v_lo + pad) & (ys <= v_hi - pad)
    return np.column_stack([np.full(int(keep.sum()), x0), ys[keep]])


def render_slice_figure(u, v, values, footprint, out_png: str | Path, *,
                        xlabel: str, ylabel: str, body_label: str = "",
                        station_note: str = "", view_box=None,
                        silhouette=None, grid_shape=SLICE_GRID_SHAPE,
                        velocity=None, seed_points=None,
                        figsize=(11.4, 6.2), dpi: int = 150) -> dict | None:
    """Render the smooth pressure field around the exact body silhouette.

    ``u``/``v`` are in-plane cell-centre coordinates in metres, ``values`` the
    cell-centre kinematic pressure (the incompressible solver's p, which is
    already p over rho, in m^2/s^2), ``footprint`` each cell's in-plane size.
    The scattered cell centres are linearly interpolated onto a fine regular
    grid and shaded continuously, so the field reads as a smooth physical
    gradient rather than the raw solver cells. ``silhouette`` is the body's
    exact cross-section from :func:`surface_cross_section`: it is drawn as a
    crisp dark filled outline and the interpolated field is masked inside it
    (even-odd over the loops, so a loop inside a loop is fluid again).
    Without a silhouette the body mask falls back to hole-bridging triangles
    of the cell triangulation. ``velocity`` is an optional pair of scattered
    in-plane velocity components aligned one-to-one with ``u``/``v``: when
    given, streamlines of that field are overlaid on the pressure shading
    (thin translucent strokes, seeded from ``seed_points`` or an upstream
    column from :func:`streamline_seeds`, masked by the same silhouette as
    the fill). Returns metadata about what was drawn, including every string
    placed on the figure so tests hold the register.
    """
    import numpy as np
    from matplotlib.cm import ScalarMappable
    from matplotlib.colors import TwoSlopeNorm, to_rgba
    from matplotlib.tri import LinearTriInterpolator, Triangulation

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
    if velocity is not None:
        velocity = (np.asarray(velocity[0], dtype=np.float64)[near],
                    np.asarray(velocity[1], dtype=np.float64)[near])

    triangulation = Triangulation(u, v)

    # Continuous field: resample the scattered cell centres onto a fine
    # regular grid. The interpolation is linear inside the data's hull and
    # blank outside it, so open regions (below the ground plane, outside the
    # domain) stay dark panel.
    grid_ny, grid_nx = grid_shape
    grid_x = np.linspace(u_lo, u_hi, grid_nx)
    grid_y = np.linspace(v_lo, v_hi, grid_ny)
    mesh_x, mesh_y = np.meshgrid(grid_x, grid_y)
    field = LinearTriInterpolator(triangulation, values)(mesh_x, mesh_y)
    no_data = np.ma.getmaskarray(field)
    filled = _smooth_grid(field.filled(0.0), (~no_data).astype(np.float64))

    if silhouette:
        # Exact body mask: even-odd over the section loops, so nested loops
        # (a hub inside a tyre) carve fluid back out.
        flat = np.column_stack([mesh_x.ravel(), mesh_y.ravel()])
        body_mask = silhouette_mask(flat, silhouette).reshape(mesh_x.shape)
    else:
        # No surface on file: mask grid points that fall in hole-bridging
        # triangles (longest edge far beyond the local cell size), which is
        # where the body was in the fluid.
        tris = triangulation.triangles
        edge = np.zeros(len(tris))
        for a, b in ((0, 1), (1, 2), (2, 0)):
            edge = np.maximum(edge, np.hypot(u[tris[:, a]] - u[tris[:, b]],
                                             v[tris[:, a]] - v[tris[:, b]]))
        local = footprint[tris].max(axis=1)
        bridging = edge > 2.6 * np.maximum(local, 1e-12)
        owner = triangulation.get_trifinder()(mesh_x, mesh_y)
        body_mask = (owner >= 0) & bridging[np.clip(owner, 0, len(bridging) - 1)]

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
    cmap = plt.get_cmap(_SLICE_CMAP)
    norm = TwoSlopeNorm(vmin=lo, vcenter=0.0, vmax=hi)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    # One composed image: smooth shaded field, dark panel where there is no
    # fluid data, dark body inside the silhouette. Composing the RGBA pixels
    # directly keeps the mask and the fill pixel-identical by construction.
    shaded = cmap(norm(np.clip(filled, lo, hi)))
    shaded[no_data] = to_rgba(BG)
    shaded[body_mask] = to_rgba(BG)
    ax.imshow(shaded, extent=(u_lo, u_hi, v_lo, v_hi), origin="lower",
              interpolation="bilinear", zorder=1)
    if silhouette:
        # The crisp outline of the exact section, over the fill.
        for loop in silhouette:
            loop = np.asarray(loop, dtype=np.float64)
            ring = np.vstack([loop, loop[:1]])
            ax.plot(ring[:, 0], ring[:, 1], color=INK, linewidth=1.0,
                    alpha=0.9, zorder=3, solid_joinstyle="round")

    # Streamline overlay: the in-plane velocity resampled onto the very same
    # grid as the pressure fill, NaN inside the silhouette and outside the
    # data hull so the integrator can never step through the body. Thin
    # translucent strokes between the fill (1) and the outline (3).
    stream_meta = None
    if velocity is not None:
        vel_uu, vel_vv = inplane_velocity_grid(
            u, v, velocity[0], velocity[1], grid_x, grid_y,
            body_mask=(body_mask | no_data))
        seeds = np.asarray(seed_points if seed_points is not None
                           else streamline_seeds((u_lo, u_hi, v_lo, v_hi)),
                           dtype=np.float64)
        stroke = to_rgba(_STREAM_COLOR, STREAM_ALPHA)
        stream = ax.streamplot(
            grid_x, grid_y, np.ma.masked_invalid(vel_uu),
            np.ma.masked_invalid(vel_vv), start_points=seeds,
            density=STREAM_DENSITY, integration_direction="both",
            broken_streamlines=False, color=stroke,
            linewidth=STREAM_LINEWIDTH, arrowsize=0.8, zorder=2)
        segments = [np.asarray(s, dtype=np.float64)
                    for s in stream.lines.get_segments()]
        speed = np.hypot(vel_uu, vel_vv)
        finite = np.isfinite(speed)
        stream_meta = {
            "n_seeds": int(len(seeds)),
            "seed_points": seeds,
            "segments": segments,
            "speed_max": (float(np.nanmax(speed)) if finite.any() else 0.0),
            "speed_min": (float(np.nanmin(speed)) if finite.any() else 0.0),
        }

    # One annotated key value: the stagnation peak, the warmest point of the
    # whole field, where the flow comes to rest on the nose.
    peak_pool = np.flatnonzero(in_view) if in_view.sum() >= 16 else np.arange(values.size)
    peak = int(peak_pool[np.argmax(values[peak_pool])])
    annotation = (rf"stagnation peak  $p/\rho$ = {values[peak]:,.0f}"
                  r" $\mathrm{m^2/s^2}$")
    # The label rides a dark panel chip so it reads over the light field.
    ax.annotate(annotation, xy=(u[peak], v[peak]),
                xytext=(0.03, 0.94), textcoords="axes fraction",
                ha="left", va="top", fontsize=12, color=INK, weight="bold",
                zorder=4,
                bbox={"boxstyle": "round,pad=0.45", "facecolor": BG,
                      "edgecolor": DIM, "alpha": 0.88},
                arrowprops={"arrowstyle": "-", "color": MUTED,
                            "linewidth": 0.9, "alpha": 0.8})

    title = SLICE_TITLE + (f": {body_label}" if body_label else "")
    style_axes(ax, xlabel, ylabel, title)
    ax.grid(False)  # gridlines over a filled field are clutter, ticks stay
    ax.set_xlim(u_lo, u_hi)
    ax.set_ylim(v_lo, v_hi)
    ax.set_aspect("equal", adjustable="box")

    colorbar_label = (r"static pressure  $p/\rho$  [$\mathrm{m^2/s^2}$]")
    cbar = fig.colorbar(ScalarMappable(norm=norm, cmap=cmap), ax=ax,
                        pad=0.02, fraction=0.05)
    cbar.set_label(colorbar_label, color=INK, fontsize=11)
    cbar.ax.tick_params(colors=MUTED, labelsize=9)
    cbar.outline.set_edgecolor(DIM)

    # Units stated plainly: the incompressible solver carries p over rho.
    note = ("Incompressible solve: p is kinematic pressure, p over rho; "
            "multiply by rho = 1.2 kg/m3 (air) for Pa.\n"
            "Red high, blue low; the dark silhouette is the body "
            "cross-section." + (f" {station_note}" if station_note else "")
            + ("\nThin strokes: streamlines of the in-plane velocity from "
               "the same solved volume field, seeded upstream."
               if stream_meta else ""))
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
            "value_range": (lo, hi), "renderer": "smooth-grid",
            "grid_shape": tuple(grid_shape),
            "view_box": (u_lo, u_hi, v_lo, v_hi),
            "streamlines": stream_meta,
            "silhouette_loops": len(silhouette or [])}


_AXIS_NAMES = "xyz"


def render_pressure_slice(vtu_path: str | Path, out_png: str | Path, *,
                          span_axis: int, plane_axes=None, body_bounds=None,
                          body_label: str = "", surface_mesh=None,
                          figsize=(11.4, 6.2), dpi: int = 150,
                          field: str = "p",
                          overlay_velocity_field: str | None = None) -> dict | None:
    """Extract the mid-span slab from a volume file and render the field.

    ``span_axis`` is the axis the slicing plane is normal to; ``plane_axes``
    the (horizontal, vertical) in-plane axes, defaulting to the remaining two
    in order. ``body_bounds`` (the painted-surface payload's ``bounds``) sets
    the slice station at the body's own mid-span and frames the view on the
    body; without it both fall back to the fluid domain itself.
    ``surface_mesh`` is the body's own triangle mesh in case coordinates
    (from :func:`load_surface_mesh`): when given, the silhouette is the exact
    plane cross-section of that surface rather than anything inferred from
    the volume cells. ``overlay_velocity_field`` names a vector field in the
    same volume file (``"U"``): when given and present, its in-plane
    components on the same slice cells ride the figure as streamlines.
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

    # In-plane velocity on the same slice cells, for the streamline overlay.
    velocity = None
    if overlay_velocity_field:
        vector = read_volume_vector(vtu_path, overlay_velocity_field)
        if vector is not None and len(vector[3]) >= len(centres):
            vectors = vector[3][:len(centres)]
            velocity = (vectors[keep, axis_u], vectors[keep, axis_v])

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

    # The exact body cross-section, cut from the body's own surface mesh at
    # this station: the silhouette is the true section shape however coarse
    # the volume sampling is.
    silhouette = None
    if surface_mesh is not None:
        try:
            silhouette = surface_cross_section(
                surface_mesh[0], surface_mesh[1], axis=span_axis,
                station=station, plane_axes=(axis_u, axis_v)) or None
        except Exception:
            silhouette = None

    station_note = (f"Slice: {_AXIS_NAMES[span_axis]} = {station:.2f} m, "
                    + ("the cell layer crossing the plane."
                       if half_used == 0.0 else
                       f"slab widened to {2 * half_used:.3g} m."))
    # Streamline seeds cluster about the body's own centreline when the
    # bounds are known; otherwise about the middle of the view.
    seed_points = None
    if velocity is not None and body_bounds:
        seed_points = streamline_seeds(
            tuple(view), center_v=0.5 * (b_lo[axis_v] + b_hi[axis_v]))
    return render_slice_figure(
        u, v, values[keep], footprint, out_png,
        xlabel=f"{_AXIS_NAMES[axis_u]}  [m]",
        ylabel=f"{_AXIS_NAMES[axis_v]}  [m]",
        body_label=body_label, station_note=station_note, view_box=view,
        silhouette=silhouette, velocity=velocity, seed_points=seed_points,
        figsize=figsize, dpi=dpi)


def extract_pressure_slice(remote_case: str, out_png: str | Path, wsl_prefix,
                           *, span_axis: int, plane_axes=None,
                           body_bounds=None, body_label: str = "",
                           surface_path=None,
                           surface_scale: float = 1.0) -> str | None:
    """Fetch the case's volume output and render the mid-span pressure slice.

    The volume file (``internal.vtu``) comes from the same ``foamToVTK`` run
    :func:`extract_and_paint` already performed, so this never re-solves and
    never re-meshes; it only copies one file out of the compute node. A held
    case with no volume output on disk (runs older than the volume writer)
    returns None and the act simply carries no slice plot. ``surface_path``
    plus ``surface_scale`` give the body's own surface file and the uniform
    scale the case build applied, for the exact silhouette cut.
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
    surface_mesh = None
    if surface_path is not None:
        surface_mesh = load_surface_mesh(surface_path, surface_scale)
    try:
        meta = render_pressure_slice(
            staging / "volume.vtu", out_png, span_axis=span_axis,
            plane_axes=plane_axes, body_bounds=body_bounds,
            body_label=body_label, surface_mesh=surface_mesh)
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
