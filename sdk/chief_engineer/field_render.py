"""Paint a solved field onto the mission's surface for the viewport.

After a case is solved, ``foamToVTK -surfaceFields`` writes the body patch with
its pressure field attached.  This module reads that ``.vtp`` (VTK XML with
base64-encoded binary arrays), reduces it to a wireframe payload the browser
already knows how to draw, and adds a per-face pressure-coefficient value so
the viewport can colour the geometry by the real solution rather than by depth
alone.

Pure standard library: the base64 arrays are decoded by hand, so nothing here
needs VTK or numpy on the controller.
"""

from __future__ import annotations

import base64
import re
import struct
from pathlib import Path
from typing import Any

from .geometry import _package

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
                       max_faces: int = 12000, name: str = "surface") -> dict[str, Any]:
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
    payload = _package(all_v, all_f, max_faces, name)
    _attach_field(payload, all_f, all_field, field)
    return payload


def _attach_field(payload: dict[str, Any], original_faces, face_values, field: str) -> None:
    """Carry a normalised field value per kept face, plus its physical range."""
    if not face_values:
        payload["field"] = None
        return
    # _package decimates by keeping every Nth face; mirror that here.
    total = len(original_faces)
    kept = payload["triangles_shown"]
    stride = max(1, total // max(1, payload.get("triangles_total", total)))
    sampled = face_values[::stride][:len(payload["faces"])]
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


# Patches that are the domain, not the body — never painted.
_DOMAIN_PATCHES = ("farfield", "frontandback", "inlet", "outlet",
                   "defaultfaces", "domain", "atmosphere", "ground")


def extract_and_paint(remote_case: str, out_path: str | Path, wsl_prefix,
                      *, field: str = "p", name: str = "surface") -> str | None:
    """Run foamToVTK, merge every body patch, and write a painted-surface JSON.

    The body may be one patch (``body``) or a group of dozens (the motorBike's
    ``motorBike_*`` sub-patches). Everything that is not a domain boundary is
    collected and merged, so this works for any geometry. Returns the local
    JSON path, or None if no field surface could be produced.
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
    patches = [p for p in staging.glob("*.vtp")
               if p.stem.lower() not in _DOMAIN_PATCHES]
    if not patches:
        return None
    payload = load_field_surface(patches, field=field, name=name)
    if not payload.get("field"):
        return None
    out_path.write_text(json.dumps(payload), encoding="utf-8")
    return str(out_path)


def _wsl_out(path: Path) -> str:
    text = str(path).replace("\\", "/")
    if len(text) > 1 and text[1] == ":":
        text = "/mnt/" + text[0].lower() + text[2:]
    return text
