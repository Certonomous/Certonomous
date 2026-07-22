"""Surface geometry for the control-room viewport.

The viewport shows the mission's actual geometry.  Real surfaces arrive as OBJ
or STL (binary or ASCII) — the airplane will land here exactly as the
motorBike does — and parametric cases generate their surface from the design
variables the mission is optimizing.

Meshes are decimated server-side before they reach the browser: a 132k-vertex
motorBike is 10 MB of text that no canvas needs in order to draw a readable
wireframe.  Decimation keeps whole triangles and remaps only the vertices they
reference, so the silhouette survives while the payload drops by ~30x.
"""

from __future__ import annotations

import math
import struct
from pathlib import Path
from typing import Any

DEFAULT_MAX_FACES = 9000


def load_surface(path: str | Path, *, max_faces: int = DEFAULT_MAX_FACES) -> dict[str, Any]:
    """Read an OBJ or STL surface and return a decimated wireframe payload."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".obj":
        vertices, faces = _read_obj(path)
    elif suffix == ".stl":
        vertices, faces = _read_stl(path)
    else:
        raise ValueError(f"unsupported surface format: {suffix!r}")
    if not vertices or not faces:
        raise ValueError(f"{path.name} contains no drawable surface")
    return _package(vertices, faces, max_faces, path.stem)


def _read_obj(path: Path) -> tuple[list[list[float]], list[list[int]]]:
    vertices: list[list[float]] = []
    faces: list[list[int]] = []
    with path.open("r", errors="replace") as stream:
        for line in stream:
            if line.startswith("v "):
                parts = line.split()
                vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif line.startswith("f "):
                indices = []
                for token in line.split()[1:]:
                    raw = token.split("/")[0]
                    if not raw:
                        continue
                    index = int(raw)
                    # OBJ indices are 1-based; negatives count back from the end.
                    indices.append(index - 1 if index > 0 else len(vertices) + index)
                if len(indices) >= 3:
                    # Fan-triangulate polygons so the viewport only handles triangles.
                    for k in range(1, len(indices) - 1):
                        faces.append([indices[0], indices[k], indices[k + 1]])
    return vertices, faces


def _read_stl(path: Path) -> tuple[list[list[float]], list[list[int]]]:
    data = path.read_bytes()
    if _looks_ascii(data):
        return _read_stl_ascii(data.decode("ascii", errors="replace"))
    return _read_stl_binary(data)


def _looks_ascii(data: bytes) -> bool:
    head = data[:256].lstrip().lower()
    if not head.startswith(b"solid"):
        return False
    # A binary STL may still begin with "solid" in its 80-byte header; the
    # declared triangle count is the reliable discriminator.
    if len(data) >= 84:
        count = struct.unpack("<I", data[80:84])[0]
        if len(data) == 84 + count * 50:
            return False
    return b"facet" in data[:2048].lower()


def _read_stl_ascii(text: str) -> tuple[list[list[float]], list[list[int]]]:
    vertices: list[list[float]] = []
    faces: list[list[int]] = []
    current: list[int] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("vertex"):
            parts = stripped.split()
            vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
            current.append(len(vertices) - 1)
        elif stripped.startswith("endfacet"):
            if len(current) >= 3:
                faces.append(current[:3])
            current = []
    return vertices, faces


def _read_stl_binary(data: bytes) -> tuple[list[list[float]], list[list[int]]]:
    if len(data) < 84:
        raise ValueError("STL file is too short to be valid")
    count = struct.unpack("<I", data[80:84])[0]
    vertices: list[list[float]] = []
    faces: list[list[int]] = []
    offset = 84
    for _ in range(count):
        if offset + 50 > len(data):
            break
        values = struct.unpack_from("<12f", data, offset)
        base = len(vertices)
        vertices.append(list(values[3:6]))
        vertices.append(list(values[6:9]))
        vertices.append(list(values[9:12]))
        faces.append([base, base + 1, base + 2])
        offset += 50
    return vertices, faces


def _cluster(vertices, faces, resolution: int):
    """Vertex-cluster decimation: snap to a grid, then rebuild the triangles.

    Dropping every Nth triangle would keep isolated slivers that no longer
    touch each other — filled, they read as confetti rather than a surface.
    Clustering merges nearby vertices instead, so the reduced mesh stays
    connected and the shape survives.
    """
    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    zs = [v[2] for v in vertices]
    low = (min(xs), min(ys), min(zs))
    high = (max(xs), max(ys), max(zs))
    size = max(high[i] - low[i] for i in range(3)) or 1.0
    cell = size / max(1, resolution)

    cells: dict[tuple[int, int, int], int] = {}
    sums: list[list[float]] = []
    counts: list[int] = []
    owner: list[int] = []
    for vertex in vertices:
        key = tuple(int((vertex[i] - low[i]) // cell) for i in range(3))
        index = cells.get(key)
        if index is None:
            index = len(sums)
            cells[key] = index
            sums.append([0.0, 0.0, 0.0])
            counts.append(0)
        for i in range(3):
            sums[index][i] += vertex[i]
        counts[index] += 1
        owner.append(index)

    out_vertices = [[sums[i][k] / counts[i] for k in range(3)] for i in range(len(sums))]
    seen: set[tuple[int, int, int]] = set()
    out_faces: list[list[int]] = []
    for face in faces:
        if len(face) < 3:
            continue
        try:
            mapped = [owner[face[0]], owner[face[1]], owner[face[2]]]
        except IndexError:
            continue
        # A triangle whose corners collapsed into the same cell has no area.
        if mapped[0] == mapped[1] or mapped[1] == mapped[2] or mapped[0] == mapped[2]:
            continue
        key = tuple(sorted(mapped))
        if key in seen:
            continue
        seen.add(key)
        out_faces.append(mapped)
    return out_vertices, out_faces


def _package(vertices, faces, max_faces: int, name: str) -> dict[str, Any]:
    total = len(faces)
    out_vertices, out_faces = vertices, faces
    if total > max_faces:
        # Search a grid resolution that lands near the target triangle count.
        resolution = 56
        for _ in range(6):
            out_vertices, out_faces = _cluster(vertices, faces, resolution)
            if len(out_faces) > max_faces * 1.35:
                resolution = max(8, int(resolution * 0.78))
            elif len(out_faces) < max_faces * 0.45:
                resolution = int(resolution * 1.3)
            else:
                break
        # Only drop whole triangles if clustering still overshoots.
        if len(out_faces) > max_faces:
            keep = max(1, math.ceil(len(out_faces) / max_faces))
            out_faces = out_faces[::keep]

    xs = [v[0] for v in out_vertices] or [0.0]
    ys = [v[1] for v in out_vertices] or [0.0]
    zs = [v[2] for v in out_vertices] or [0.0]
    return {
        "name": name,
        "vertices": [[round(c, 5) for c in v] for v in out_vertices],
        "faces": out_faces,
        "triangles_total": total,
        "triangles_shown": len(out_faces),
        "bounds": {"min": [min(xs), min(ys), min(zs)],
                   "max": [max(xs), max(ys), max(zs)]},
    }


def cylinder_surface(diameter: float = 1.0, *, span: float = 2.0,
                     segments: int = 64) -> dict[str, Any]:
    """Generate the parametric cylinder a 2D mission is actually solving."""
    radius = max(diameter, 1e-6) / 2.0
    half = span / 2.0
    vertices: list[list[float]] = []
    faces: list[list[int]] = []
    for index in range(segments):
        angle = 2 * math.pi * index / segments
        x, y = radius * math.cos(angle), radius * math.sin(angle)
        vertices.append([x, y, -half])
        vertices.append([x, y, half])
    for index in range(segments):
        a = 2 * index
        b = 2 * ((index + 1) % segments)
        faces.append([a, a + 1, b + 1])
        faces.append([a, b + 1, b])
    return {
        "name": f"cylinder D={diameter:.3g} m",
        "vertices": [[round(c, 5) for c in v] for v in vertices],
        "faces": faces,
        "triangles_total": len(faces),
        "triangles_shown": len(faces),
        "bounds": {"min": [-radius, -radius, -half], "max": [radius, radius, half]},
    }


def available_surfaces(root: str | Path) -> list[str]:
    root = Path(root)
    if not root.exists():
        return []
    return sorted(p.name for p in root.iterdir()
                  if p.suffix.lower() in {".obj", ".stl"})
