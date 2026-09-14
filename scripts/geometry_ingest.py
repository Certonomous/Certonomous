#!/usr/bin/env python3
"""Geometry ingest for the Certonomous lab — any run can start from a file.

Sanaa's order, 2026-09-14: *"ok now for all the runs, i need tobe able to load
a real stl file. or even better a cad file then stl"*.

This module takes a user-supplied surface or CAD file, converts it to a **binary
STL** in the place the case will actually read it from, and writes a JSON sidecar
that says what was found: source sha256, units (detected or declared), bounding
box, triangle count, watertightness, shell count, degenerate triangles, and the
path to a 512 px headless preview PNG.

It is deliberately honest about the two things that decide whether a mesh will
build: a surface that is **not closed** is refused for a snappyHexMesh case
unless ``--allow-open`` is passed, and the refusal reason is written into the
JSON rather than left in a terminal somebody has already closed. Units are never
silently corrected: the heuristic records what it thinks, an explicit
``--units`` overrides it, and rescaling happens only when it is asked for.

Accepted inputs
---------------
``.stl`` (ascii or binary), ``.obj``, ``.step`` / ``.stp``, ``.iges`` / ``.igs``.
Gzipped variants of the mesh formats (``.stl.gz``, ``.obj.gz``) are accepted too,
because that is how several published OpenFOAM setups on this box ship them.

CAD conversion
--------------
STEP and IGES are tessellated with whatever is installed. The probe order is
gmsh (python module, then the CLI — the CLI build on this box carries
OpenCASCADE 7.6.3), then FreeCAD (``freecadcmd``), then cadquery/OCP. The tool
that actually ran, and how long it took, are recorded in the sidecar.

Dependencies
------------
Hard: numpy. Soft, each with a fallback: scipy (connected components — falls
back to vectorised pointer-jumping), matplotlib (preview — omitted if absent),
trimesh and pyvista (used when present, never required). Nothing was pip
installed to make this work; see ``docs/GEOMETRY_INGEST_2026-09-14.md``.

CLI
---
    python3 scripts/geometry_ingest.py INPUT --case CASE_ID [options]

Importable
----------
    from geometry_ingest import ingest
    report = ingest(source, case_id="DRIVAER", units="auto")
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
import re
import shutil
import struct
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

# ---------------------------------------------------------------------------
# Where things land
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]

#: The majority convention on this box, measured 2026-09-14: every meshing case
#: under ``cases/`` and ``verification/runs/`` that consumes a surface reads it
#: from ``<case>/constant/triSurface/``.  ``<case>/geometry/`` exists in exactly
#: one place (``cases/F28_DUCTED_ACTUATOR_DISK/case/geometry``), so triSurface
#: is the default and geometry/ is reachable with ``--out-subdir geometry``.
CASE_SURFACE_SUBDIR = "constant/triSurface"

MESH_SUFFIXES = {".stl", ".obj"}
CAD_SUFFIXES = {".step", ".stp", ".iges", ".igs"}
ACCEPTED_SUFFIXES = MESH_SUFFIXES | CAD_SUFFIXES

#: Units a length may be declared in, as a multiplier onto metres.
UNIT_TO_METRE = {"m": 1.0, "mm": 1e-3, "cm": 1e-2, "in": 0.0254, "ft": 0.3048}

PREVIEW_PX = 512
#: Triangles drawn in the preview after back-face culling.  Above this the
#: preview is a uniform random subsample — stated in the sidecar so nobody reads
#: the picture as the full surface.
PREVIEW_MAX_FACES = 600_000


class IngestError(RuntimeError):
    """Raised for anything the caller did wrong or the box cannot do."""


# ---------------------------------------------------------------------------
# Readers
# ---------------------------------------------------------------------------

def _open_maybe_gzip(path: Path):
    if path.suffix.lower() == ".gz":
        return gzip.open(path, "rb")
    return open(path, "rb")


def _effective_suffix(path: Path) -> str:
    """``a.stl.gz`` -> ``.stl``; ``a.STP`` -> ``.stp``."""
    name = path.name.lower()
    if name.endswith(".gz"):
        name = name[:-3]
    return Path(name).suffix


def _read_stl(path: Path) -> tuple[np.ndarray, str]:
    """Return (triangles as (N, 3, 3) float64, ``"binary"`` or ``"ascii"``).

    The format test is structural, not textual: a binary STL whose 80-byte
    header happens to begin with the word ``solid`` is a real and common file,
    and sniffing the first five bytes gets it wrong.  We trust the triangle
    count in the header only when it accounts for the file exactly.
    """
    with _open_maybe_gzip(path) as handle:
        blob = handle.read()
    if len(blob) < 84:
        raise IngestError(f"{path.name}: too short to be an STL ({len(blob)} bytes)")

    count = struct.unpack("<I", blob[80:84])[0]
    if len(blob) == 84 + 50 * count:
        raw = np.frombuffer(blob, dtype=np.dtype([
            ("normal", "<f4", 3), ("verts", "<f4", (3, 3)), ("attr", "<u2"),
        ]), count=count, offset=84)
        return raw["verts"].astype(np.float64), "binary"

    text = blob.decode("utf-8", errors="replace")
    values = re.findall(
        r"vertex\s+(\S+)\s+(\S+)\s+(\S+)", text)
    if not values:
        raise IngestError(
            f"{path.name}: neither a binary STL of the declared size "
            f"({count} triangles would be {84 + 50 * count} bytes, file is "
            f"{len(blob)}) nor an ascii STL with any 'vertex' line")
    flat = np.array(values, dtype=np.float64)
    if flat.shape[0] % 3:
        raise IngestError(
            f"{path.name}: ascii STL has {flat.shape[0]} vertices, not a multiple of 3")
    return flat.reshape(-1, 3, 3), "ascii"


def _read_obj(path: Path) -> tuple[np.ndarray, str]:
    """Wavefront OBJ.  Polygons are fan-triangulated; only ``v``/``f`` matter."""
    verts: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int]] = []
    with _open_maybe_gzip(path) as handle:
        for line in handle:
            if line[:2] == b"v ":
                parts = line.split()
                verts.append((float(parts[1]), float(parts[2]), float(parts[3])))
            elif line[:2] == b"f ":
                idx = []
                for token in line.split()[1:]:
                    first = token.split(b"/")[0]
                    if not first:
                        continue
                    value = int(first)
                    idx.append(value - 1 if value > 0 else len(verts) + value)
                for k in range(1, len(idx) - 1):
                    faces.append((idx[0], idx[k], idx[k + 1]))
    if not faces:
        raise IngestError(f"{path.name}: no triangulable faces found")
    array = np.asarray(verts, dtype=np.float64)
    return array[np.asarray(faces, dtype=np.int64)], "obj"


# ---------------------------------------------------------------------------
# CAD -> STL
# ---------------------------------------------------------------------------

def cad_converters_available() -> list[dict[str, Any]]:
    """Probe, in the order the brief fixes, what this box can tessellate with.

    Returns one entry per candidate with ``available`` and a ``detail`` string,
    so the sidecar and the doc can both say what *is not* here as well as what
    is.  Nothing is imported that would be expensive to import.
    """
    found: list[dict[str, Any]] = []

    detail = "not importable"
    ok = False
    try:  # pragma: no cover - depends on the box
        import gmsh  # type: ignore # noqa: F401
        ok, detail = True, "python module"
    except Exception as exc:
        detail = f"not importable ({type(exc).__name__})"
    found.append({"tool": "gmsh-python", "available": ok, "detail": detail})

    binary = shutil.which("gmsh")
    if binary:
        try:
            probe = subprocess.run([binary, "-info"], capture_output=True,
                                   text=True, timeout=60)
            info = (probe.stdout or "") + (probe.stderr or "")
            occ = re.search(r"OCC version\s*:\s*(\S+)", info)
            version = re.search(r"Version\s*:\s*(\S+)", info)
            if occ:
                found.append({"tool": "gmsh-cli", "available": True,
                              "detail": f"gmsh {version.group(1) if version else '?'}"
                                        f", OpenCASCADE {occ.group(1)} at {binary}"})
            else:
                found.append({"tool": "gmsh-cli", "available": False,
                              "detail": f"{binary} built without OpenCASCADE — "
                                        "it cannot read STEP or IGES"})
        except Exception as exc:
            found.append({"tool": "gmsh-cli", "available": False,
                          "detail": f"{binary} would not report ({exc})"})
    else:
        found.append({"tool": "gmsh-cli", "available": False, "detail": "not on PATH"})

    freecad = shutil.which("freecadcmd") or shutil.which("FreeCADCmd")
    found.append({"tool": "freecad", "available": bool(freecad),
                  "detail": freecad or "freecadcmd not on PATH"})

    for name in ("cadquery", "OCP"):
        try:  # pragma: no cover - depends on the box
            __import__(name)
            found.append({"tool": name, "available": True, "detail": "python module"})
        except Exception as exc:
            found.append({"tool": name, "available": False,
                          "detail": f"not importable ({type(exc).__name__})"})
    return found


def _cad_to_stl(source: Path, workdir: Path, clscale: float,
                angle_deg: float, reuse: bool = False) -> tuple[Path, str, float]:
    """Tessellate STEP/IGES to STL.  Returns (stl path, tool name, seconds).

    ``reuse`` takes an intermediate already sitting in ``workdir`` instead of
    meshing again. A CAD tessellation here runs into the tens of minutes, and
    re-running one because a later step of the SAME ingest needed fixing is
    pure waste. The sidecar says when an intermediate was reused, so a reader
    can tell a measured conversion time from a borrowed one.
    """
    workdir.mkdir(parents=True, exist_ok=True)
    target = workdir / (source.stem + "_cad.stl")
    if reuse and target.is_file() and target.stat().st_size > 84:
        return target, "reused intermediate (not re-tessellated)", 0.0

    # -- gmsh, python module first (it can drive the same OCC kernel in-process)
    try:  # pragma: no cover - not installed on this box
        import gmsh  # type: ignore

        started = time.time()
        gmsh.initialize()
        try:
            gmsh.option.setNumber("General.Terminal", 0)
            gmsh.option.setNumber("Mesh.CharacteristicLengthFactor", clscale)
            gmsh.option.setNumber("Mesh.StlLinearDeflection", 0.0)
            gmsh.option.setNumber("Mesh.AngleToleranceFacetOverlap", angle_deg)
            gmsh.merge(str(source))
            gmsh.model.mesh.generate(2)
            gmsh.write(str(target))
        finally:
            gmsh.finalize()
        if target.exists():
            return target, "gmsh-python", time.time() - started
    except ImportError:
        pass

    binary = shutil.which("gmsh")
    if binary:
        started = time.time()
        proc = subprocess.run(
            [binary, str(source), "-2", "-format", "stl", "-o", str(target),
             "-clscale", str(clscale),
             "-setnumber", "Mesh.Binary", "1",
             "-setnumber", "Mesh.StlOneSolidPerSurface", "0",
             "-nopopup", "-v", "2"],
            capture_output=True, text=True, timeout=7200)
        elapsed = time.time() - started
        if target.exists() and target.stat().st_size > 84:
            return target, f"gmsh-cli ({binary})", elapsed
        raise IngestError(
            f"gmsh could not tessellate {source.name} (rc={proc.returncode}): "
            f"{(proc.stderr or proc.stdout or '').strip()[-500:]}")

    freecad = shutil.which("freecadcmd") or shutil.which("FreeCADCmd")
    if freecad:  # pragma: no cover - not installed on this box
        script = workdir / "_freecad_convert.py"
        script.write_text(
            "import FreeCAD, Import, Mesh, MeshPart\n"
            f"doc = FreeCAD.newDocument('c')\n"
            f"Import.insert({str(source)!r}, 'c')\n"
            "shapes = [o for o in doc.Objects if hasattr(o, 'Shape')]\n"
            "meshes = [MeshPart.meshFromShape(Shape=o.Shape, LinearDeflection=0.1,"
            " AngularDeflection=0.5, Relative=True) for o in shapes]\n"
            "merged = meshes[0]\n"
            "for m in meshes[1:]:\n    merged.addMesh(m)\n"
            f"merged.write({str(target)!r})\n")
        started = time.time()
        proc = subprocess.run([freecad, str(script)], capture_output=True,
                              text=True, timeout=7200)
        if target.exists():
            return target, f"freecad ({freecad})", time.time() - started
        raise IngestError(f"FreeCAD could not convert {source.name}: "
                          f"{(proc.stderr or proc.stdout or '').strip()[-500:]}")

    try:  # pragma: no cover - not installed on this box
        import cadquery as cq  # type: ignore

        started = time.time()
        shape = cq.importers.importStep(str(source))
        cq.exporters.export(shape, str(target), exportType="STL")
        if target.exists():
            return target, "cadquery", time.time() - started
    except ImportError:
        pass

    raise IngestError(
        "no CAD tessellator on this box. Probed, in order: "
        + "; ".join(f"{c['tool']}={c['detail']}" for c in cad_converters_available()))


#: STEP SI prefix -> multiplier onto metres, for SI_UNIT(.<prefix>.,.METRE.)
_STEP_SI_PREFIX = {"": 1.0, "MILLI": 1e-3, "CENTI": 1e-2, "DECI": 1e-1,
                   "KILO": 1e3, "MICRO": 1e-6}
#: What a declared unit name maps onto in UNIT_TO_METRE.
_UNIT_ALIASES = {"INCH": "in", "IN": "in", "MM": "mm", "MILLIMETRE": "mm",
                 "MILLIMETER": "mm", "M": "m", "METRE": "m", "METER": "m",
                 "CM": "cm", "CENTIMETRE": "cm", "FT": "ft", "FOOT": "ft"}


def cad_declared_unit(path: Path, scan_bytes: int = 64 << 20) -> dict[str, Any]:
    """Read the length unit the CAD file declares about ITSELF.

    This exists because the caller's ``--units`` is a belief and the file's own
    declaration is evidence, and they can disagree by a factor of 25.4. The NASA
    CRM wing STEP is the case in point: it comes from a NASA page whose sibling
    IGES files are all in INCH, and the STEP itself declares
    ``SI_UNIT(.MILLI.,.METRE.)``. Believing the page over the file would have
    scaled that wing by 25.4.

    STEP keeps the unit in the DATA section, not the header, so this scans (a
    bounded prefix of) the file. IGES keeps it in Global parameter 14.
    """
    suffix = _effective_suffix(path)
    out: dict[str, Any] = {"unit": None, "evidence": None, "source": None}
    try:
        with _open_maybe_gzip(path) as handle:
            blob = handle.read(scan_bytes)
    except Exception as exc:
        out["evidence"] = f"unreadable: {exc}"
        return out
    text = blob.decode("utf-8", errors="replace")

    if suffix in {".step", ".stp"}:
        flat = re.sub(r"\s+", " ", text)
        m = re.search(r"LENGTH_UNIT\s*\(\s*\)[^;]{0,200}?"
                      r"SI_UNIT\s*\(\s*\.?([A-Z]*)\.?\s*,\s*\.METRE\.", flat)
        if m:
            prefix = m.group(1).strip(".") or ""
            factor = _STEP_SI_PREFIX.get(prefix)
            if factor is not None:
                out.update(unit={1e-3: "mm", 1.0: "m", 1e-2: "cm"}.get(factor, None),
                           evidence=m.group(0)[:200], source="STEP SI_UNIT")
                if out["unit"] is None:
                    out["unit_factor"] = factor
                return out
        m = re.search(r"CONVERSION_BASED_UNIT\s*\(\s*'([A-Z ]+)'", flat)
        if m:
            out.update(unit=_UNIT_ALIASES.get(m.group(1).strip().upper()),
                       evidence=m.group(0)[:200],
                       source="STEP CONVERSION_BASED_UNIT")
            return out
        out["evidence"] = "no LENGTH_UNIT found in the scanned prefix"
        return out

    if suffix in {".iges", ".igs"}:
        glob = "".join(line[:72] for line in text.splitlines()
                       if len(line) > 72 and line[72] == "G")
        m = re.search(r"\d+H(INCH|IN|MM|M|CM|FT|MIL)\b", glob, re.I)
        if m:
            out.update(unit=_UNIT_ALIASES.get(m.group(1).upper()),
                       evidence=m.group(0), source="IGES Global parameter 14")
        else:
            out["evidence"] = "no unit H-string in the Global record"
        return out

    out["evidence"] = f"not a CAD format ({suffix})"
    return out


def cad_title_block(path: Path) -> dict[str, Any]:
    """Read a CAD file's own header and say what it claims to be.

    L-144 in this lab: a retrieved file is verified from its title page, never
    from its filename or its hash. For CAD that title page is the STEP HEADER
    section or the IGES Start/Global records, which carry the originating
    system, the author's own path for the part, the date and -- decisively for
    a CFD ingest -- the **declared unit**. None of that can be forged by
    renaming a download.
    """
    suffix = _effective_suffix(path)
    member = None
    if suffix == ".zip":
        import zipfile
        with zipfile.ZipFile(path) as archive:
            names = [n for n in archive.namelist()
                     if Path(n.lower()).suffix in CAD_SUFFIXES]
            if not names:
                return {"kind": "zip with no CAD member",
                        "members": archive.namelist()[:20]}
            member = sorted(names, key=lambda n: -archive.getinfo(n).file_size)[0]
            with archive.open(member) as handle:
                head = handle.read(4096).decode("utf-8", errors="replace")
            suffix = Path(member.lower()).suffix
    else:
        with _open_maybe_gzip(path) as handle:
            head = handle.read(4096).decode("utf-8", errors="replace")
    info: dict[str, Any] = {"read_bytes": len(head)}
    if member:
        info["archive_member"] = member

    if suffix in {".step", ".stp"}:
        info["kind"] = "STEP (ISO-10303-21)"
        info["is_step"] = head.lstrip().startswith("ISO-10303-21")
        for field, pattern in (("file_description", r"FILE_DESCRIPTION\((.*?)\);"),
                               ("file_name", r"FILE_NAME\((.*?)\);"),
                               ("file_schema", r"FILE_SCHEMA\((.*?)\);")):
            m = re.search(pattern, head, re.S)
            if m:
                info[field] = " ".join(m.group(1).split())[:600]
        m = re.search(r"PRODUCT\('([^']*)'", head)
        if m:
            info["product"] = m.group(1)
        info["units_declared"] = (
            "not in the HEADER -- STEP carries units in the DATA section "
            "(SI_UNIT / CONVERSION_BASED_UNIT), so --units settles it here")
    elif suffix in {".iges", ".igs"}:
        info["kind"] = "IGES"
        glob = "".join(line[:72] for line in head.splitlines()
                       if len(line) > 72 and line[72] == "G")
        info["global_record"] = glob[:600]
        fields = glob.split(",")
        info["is_iges"] = bool(glob)
        # IGES Global parameter 14 is the unit name, as an H-string.
        m = re.search(r"\d+H(INCH|IN|MM|M|CM|FT|MIL|UM|KM|MIL)\b", glob, re.I)
        if m:
            info["units_declared"] = m.group(1).upper()
        for label, idx in (("sending_system", 3), ("preprocessor_version", 4)):
            if len(fields) > idx:
                info[label] = fields[idx][:200]
    else:
        info["kind"] = f"not a CAD format ({suffix})"
    return info


# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------

def write_binary_stl(path: Path, tris: np.ndarray, header: str = "") -> None:
    """Write (N, 3, 3) triangles as a binary STL with recomputed normals."""
    tris = np.ascontiguousarray(tris, dtype=np.float32)
    count = tris.shape[0]
    normals = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    lengths = np.linalg.norm(normals, axis=1)
    safe = lengths > 0
    normals[safe] /= lengths[safe, None]
    normals[~safe] = 0.0

    record = np.zeros(count, dtype=np.dtype([
        ("normal", "<f4", 3), ("verts", "<f4", (3, 3)), ("attr", "<u2")]))
    record["normal"] = normals.astype(np.float32)
    record["verts"] = tris
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(header.encode("ascii", "replace")[:80].ljust(80, b"\0"))
        handle.write(struct.pack("<I", count))
        handle.write(record.tobytes())


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def _weld(tris: np.ndarray, tol: float) -> tuple[np.ndarray, int]:
    """Snap vertices onto a ``tol`` grid and return (face index array, n verts).

    The quantised triple is viewed as one opaque 24-byte key so the unique pass
    is a 1-D sort — ``np.unique(..., axis=0)`` on eighteen million rows is the
    difference between seconds and minutes on the big surfaces here.
    """
    verts = tris.reshape(-1, 3)
    keys = np.ascontiguousarray(np.rint(verts / tol).astype(np.int64))
    view = keys.view(np.dtype((np.void, keys.dtype.itemsize * 3))).ravel()
    _, inverse = np.unique(view, return_inverse=True)
    n_unique = int(inverse.max()) + 1 if inverse.size else 0
    return inverse.reshape(-1, 3), n_unique


def _components(n_nodes: int, edges: np.ndarray) -> int:
    """Connected components of the welded-vertex graph."""
    if n_nodes == 0:
        return 0
    try:
        from scipy.sparse import coo_matrix
        from scipy.sparse.csgraph import connected_components

        data = np.ones(edges.shape[0], dtype=np.int8)
        graph = coo_matrix((data, (edges[:, 0], edges[:, 1])),
                           shape=(n_nodes, n_nodes))
        return int(connected_components(graph, directed=False)[0])
    except ImportError:
        pass
    # Vectorised pointer-jumping: label-min propagation to a fixed point. Same
    # answer as a union-find, without a per-edge Python loop.
    label = np.arange(n_nodes, dtype=np.int64)
    a, b = edges[:, 0], edges[:, 1]
    while True:
        nxt = label.copy()
        np.minimum.at(nxt, a, label[b])
        np.minimum.at(nxt, b, label[a])
        nxt = nxt[nxt]
        if np.array_equal(nxt, label):
            break
        label = nxt
    return int(np.unique(label).size)


def analyse(tris: np.ndarray, weld_tol: float | None = None) -> dict[str, Any]:
    """Bounding box, areas, degeneracy, manifoldness and shell count."""
    verts = tris.reshape(-1, 3)
    lo = verts.min(axis=0)
    hi = verts.max(axis=0)
    size = hi - lo
    diagonal = float(np.linalg.norm(size))

    cross = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    areas = 0.5 * np.linalg.norm(cross, axis=1)
    # A triangle is degenerate when its area is negligible against the model,
    # not against an absolute epsilon: the same shape in mm and in m must give
    # the same answer.
    area_floor = max((diagonal ** 2) * 1e-14, np.finfo(np.float64).tiny)
    degenerate = int(np.count_nonzero(areas <= area_floor))

    tol = weld_tol if weld_tol is not None else max(diagonal * 1e-9, 1e-12)
    faces, n_verts = _weld(tris, tol)

    edges = np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
    undirected = np.sort(edges, axis=1)
    # Degenerate edges (both ends welded to one vertex) are not evidence of a
    # hole; they are counted separately and excluded from the manifold test.
    collapsed = int(np.count_nonzero(undirected[:, 0] == undirected[:, 1]))
    live = undirected[undirected[:, 0] != undirected[:, 1]]
    keys = np.ascontiguousarray(live).view(
        np.dtype((np.void, live.dtype.itemsize * 2))).ravel()
    _, counts = np.unique(keys, return_counts=True)
    boundary_edges = int(np.count_nonzero(counts == 1))
    nonmanifold_edges = int(np.count_nonzero(counts > 2))

    watertight = boundary_edges == 0 and nonmanifold_edges == 0

    # Signed volume via the divergence theorem — meaningful only when closed,
    # and its sign says whether the normals point out.
    signed_volume = float(np.einsum(
        "ij,ij->", tris[:, 0], np.cross(tris[:, 1], tris[:, 2])) / 6.0)

    return {
        "triangles": int(tris.shape[0]),
        "vertices_welded": n_verts,
        "weld_tolerance": float(tol),
        "bbox_min": [float(v) for v in lo],
        "bbox_max": [float(v) for v in hi],
        "bbox_size": [float(v) for v in size],
        "bbox_diagonal": diagonal,
        "surface_area": float(areas.sum()),
        "degenerate_triangles": degenerate,
        "collapsed_edges": collapsed,
        "boundary_edges": boundary_edges,
        "nonmanifold_edges": nonmanifold_edges,
        "watertight": bool(watertight),
        "watertight_method": "edge-manifold (every live edge used exactly twice)",
        "shells": _components(n_verts, live),
        "signed_volume": signed_volume,
        "normals_outward": bool(signed_volume > 0) if watertight else None,
    }


def _trimesh_cross_check(path: Path) -> dict[str, Any] | None:
    """If trimesh is installed, say what it thinks — never instead of us."""
    try:  # pragma: no cover - not installed on this box
        import trimesh  # type: ignore
    except ImportError:
        return None
    mesh = trimesh.load(str(path), process=False, force="mesh")
    return {"library": f"trimesh {trimesh.__version__}",
            "watertight": bool(mesh.is_watertight),
            "shells": int(len(mesh.split(only_watertight=False))),
            "triangles": int(len(mesh.faces))}


# ---------------------------------------------------------------------------
# Units
# ---------------------------------------------------------------------------

def infer_units(diagonal: float) -> tuple[str, str]:
    """Guess the unit of a model whose bounding-box diagonal is ``diagonal``.

    A heuristic and labelled as one.  Engineering hardware ingested here spans
    roughly 0.05 m to 100 m; the same object in millimetres reads 50 to 100000.
    The band between 100 and 1000 is genuinely ambiguous (a 5 m car in metres
    is 5, in mm is 5000; a 300 mm propeller in mm is 300) so it is reported as
    ambiguous and the caller is told to pass ``--units``.
    """
    if diagonal <= 0 or not math.isfinite(diagonal):
        return "unknown", "degenerate bounding box"
    if diagonal < 100.0:
        return "m", (f"bbox diagonal {diagonal:.4g} < 100 — reads as metres "
                     "(the same body in mm would be a 100 km object)")
    if diagonal > 1000.0:
        return "mm", (f"bbox diagonal {diagonal:.6g} > 1000 — reads as "
                      "millimetres (in metres this would be a >1 km body)")
    return "ambiguous", (f"bbox diagonal {diagonal:.6g} falls in 100-1000, where "
                         "metres and millimetres are both physically plausible — "
                         "pass --units to settle it")


# ---------------------------------------------------------------------------
# Preview
# ---------------------------------------------------------------------------

def render_preview(tris: np.ndarray, path: Path, title: str,
                   px: int = PREVIEW_PX) -> dict[str, Any]:
    """Headless 512 px preview.  Returns a note dict; never raises."""
    note: dict[str, Any] = {"path": None, "renderer": None, "faces_drawn": 0}
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.collections import PolyCollection
    except Exception as exc:
        note["renderer"] = f"unavailable ({type(exc).__name__}: {exc})"
        return note

    centre = 0.5 * (tris.reshape(-1, 3).min(axis=0) + tris.reshape(-1, 3).max(axis=0))
    pts = tris - centre

    # Fixed three-quarter view so every act's preview is directly comparable.
    az, el = math.radians(-55.0), math.radians(22.0)
    forward = np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az),
                        math.sin(el)])
    up = np.array([0.0, 0.0, 1.0])
    right = np.cross(forward, up)
    right /= np.linalg.norm(right)
    true_up = np.cross(right, forward)
    basis = np.stack([right, true_up, forward])
    view = pts @ basis.T

    normals = np.cross(view[:, 1] - view[:, 0], view[:, 2] - view[:, 0])
    lengths = np.linalg.norm(normals, axis=1)
    keep = lengths > 0
    normals = normals[keep] / lengths[keep, None]
    view = view[keep]
    if view.shape[0] == 0:
        note["renderer"] = "no non-degenerate faces to draw"
        return note
    # NO back-face culling, and the shading is two-sided. A surface tessellated
    # out of CAD by OCC/gmsh has ARBITRARY per-face orientation -- measured on
    # the PPTC STEP: 48.7% of faces point one way, which is a coin flip -- so
    # culling by normal sign deletes roughly half of every blade and draws a
    # spiky ruin of a perfectly good surface. Depth sorting alone resolves
    # occlusion; culling was only ever an optimisation.
    note["front_facing_fraction"] = float((normals[:, 2] < 0).mean())

    if view.shape[0] > PREVIEW_MAX_FACES:
        note["subsampled_from"] = int(view.shape[0])
        pick = np.random.default_rng(0).choice(
            view.shape[0], PREVIEW_MAX_FACES, replace=False)
        view, normals = view[pick], normals[pick]

    # Key light slightly above and left of the camera, plus a constant fill, so
    # a dark-bodied surface still shows its curvature at 512 px.
    light = np.array([-0.35, 0.45, -0.82])
    light /= np.linalg.norm(light)
    shade = np.abs(normals @ light) ** 0.75 * 0.72 + 0.28

    order = np.argsort(view[:, :, 2].mean(axis=1))[::-1]   # painter's algorithm
    polys = view[order][:, :, :2]
    colours = plt.get_cmap("bone")(shade[order])
    colours[:, 3] = 1.0

    fig = plt.figure(figsize=(px / 100.0, px / 100.0), dpi=100)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_facecolor("#0e1116")
    fig.patch.set_facecolor("#0e1116")
    ax.add_collection(PolyCollection(polys, facecolors=colours, edgecolors="none",
                                     antialiaseds=False))
    span = float(np.abs(view[:, :, :2]).max()) * 1.08
    ax.set_xlim(-span, span)
    ax.set_ylim(-span, span)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.text(0.02, 0.975, title, transform=ax.transAxes, va="top", ha="left",
            color="#cfd6e4", fontsize=7, family="monospace")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)

    note["path"] = str(path)
    note["renderer"] = f"matplotlib {matplotlib.__version__} (Agg, painter's algorithm)"
    note["faces_drawn"] = int(view.shape[0])
    return note


# ---------------------------------------------------------------------------
# The ingest itself
# ---------------------------------------------------------------------------

def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def case_surface_dir(case_id: str, case_root: Path | None = None,
                     out_subdir: str = CASE_SURFACE_SUBDIR) -> Path:
    root = Path(case_root) if case_root else REPO_ROOT / "cases"
    return (root / case_id / out_subdir).resolve()


def ingest(source: str | Path, case_id: str, *,
           extra: list[str | Path] | None = None,
           case_root: str | Path | None = None,
           out_dir: str | Path | None = None,
           out_subdir: str = CASE_SURFACE_SUBDIR,
           name: str | None = None,
           units: str = "auto",
           convert_to_m: bool = False,
           scale: float | None = None,
           consumer: str = "snappy",
           allow_open: bool = False,
           preview: bool = True,
           clscale: float = 1.0,
           angle_deg: float = 15.0,
           source_url: str | None = None,
           source_note: str | None = None,
           record_only: bool = False,
           force_units: bool = False,
           reuse_tessellation: bool = False,
           workdir: str | Path | None = None) -> dict[str, Any]:
    """Ingest one geometry file for one case and return the sidecar dict.

    The return value is written verbatim to ``<stem>.ingest.json`` beside the
    STL.  ``accepted`` is the field a caller should branch on: it is False when
    an open surface was handed to a snappyHexMesh case without ``--allow-open``,
    and ``refusal_reason`` then says why in words.
    """
    source = Path(source).expanduser().resolve()
    if not source.is_file():
        raise IngestError(f"no such file: {source}")
    suffix = _effective_suffix(source)
    # --record-only files a CAD original for provenance rather than reading it,
    # so it accepts the archive exactly as the publisher served it (.zip, .gz):
    # re-packing a download would change the sha256 that ties the file to its URL.
    if suffix not in ACCEPTED_SUFFIXES and not record_only:
        raise IngestError(
            f"{source.name}: unsupported extension {suffix!r}. Accepted: "
            + ", ".join(sorted(ACCEPTED_SUFFIXES)) + " (optionally .gz for mesh formats)")

    started = time.time()
    report: dict[str, Any] = {
        "schema": "certonomous.geometry_ingest/1",
        "ingested_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "case_id": case_id,
        "source_path": str(source),
        "source_name": source.name,
        "source_bytes": source.stat().st_size,
        "source_sha256": sha256_of(source),
        "source_format": suffix.lstrip("."),
        "consumer": consumer,
        "source_url": source_url,
        "source_note": source_note,
    }
    if suffix in CAD_SUFFIXES or (record_only and suffix in {".zip", ".gz"}):
        report["cad_title_block"] = cad_title_block(source)
    if suffix in CAD_SUFFIXES:
        # What the FILE says about its own unit, read before anything is scaled.
        report["cad_declared_unit"] = cad_declared_unit(source)

    if record_only:
        # File a CAD original that is NOT being tessellated here: the sha256 and
        # the file's own title block are recorded so the provenance stands on
        # its own, and the sidecar says plainly that no STL was produced.
        stem_ro = re.sub(r"[^A-Za-z0-9_.-]", "_",
                         Path(name).stem if name else source.name.split(".")[0])
        directory = (Path(out_dir).resolve() if out_dir
                     else case_surface_dir(case_id, case_root, out_subdir))
        directory.mkdir(parents=True, exist_ok=True)
        report.update({
            "record_only": True,
            "accepted": True,
            "refusal_reason": None,
            "stl_path": None,
            "case_reads_from": None,
            "preview": {"path": None, "renderer": "not rendered (--record-only)"},
            "conversion": {"kind": "none -- CAD original filed unconverted",
                           "tool": None, "seconds": 0.0},
            "cad_converters": cad_converters_available(),
            "seconds_total": round(time.time() - started, 3),
        })
        sidecar_ro = directory / f"{stem_ro}.ingest.json"
        sidecar_ro.write_text(json.dumps(report, indent=2) + "\n")
        report["sidecar_path"] = str(sidecar_ro)
        return report

    scratch = Path(workdir) if workdir else Path(
        os.environ.get("TMPDIR", "/tmp")) / f"geometry_ingest_{os.getpid()}"
    scratch.mkdir(parents=True, exist_ok=True)

    # ---- read, converting CAD on the way in -------------------------------
    if suffix in CAD_SUFFIXES:
        tess, tool, seconds = _cad_to_stl(source, scratch, clscale, angle_deg,
                                          reuse=reuse_tessellation)
        report["conversion"] = {
            "kind": "CAD tessellation",
            "tool": tool,
            "seconds": round(seconds, 3),
            "clscale": clscale,
            "intermediate_bytes": tess.stat().st_size,
        }
        tris, encoding = _read_stl(tess)
        report["intermediate_encoding"] = encoding
    else:
        read_started = time.time()
        tris, encoding = (_read_stl(source) if suffix == ".stl" else _read_obj(source))
        report["conversion"] = {
            "kind": "mesh re-encode",
            "tool": f"geometry_ingest ({encoding} reader, numpy {np.__version__})",
            "seconds": round(time.time() - read_started, 3),
        }
        report["source_encoding"] = encoding

    if tris.shape[0] == 0:
        raise IngestError(f"{source.name}: contains no triangles")

    # ---- extra parts of the same body -------------------------------------
    # Several published setups ship one physical body as several part files
    # (the MB13 marine propeller is a tip plus three stems). Merging them here
    # keeps one STL per act while every constituent keeps its own sha256, so
    # the provenance of the merged surface is not lost.
    if extra:
        merged = [tris]
        parts = [{"path": str(source), "sha256": report["source_sha256"],
                  "triangles": int(tris.shape[0])}]
        for item in extra:
            part = Path(item).expanduser().resolve()
            if not part.is_file():
                raise IngestError(f"--extra: no such file: {part}")
            part_suffix = _effective_suffix(part)
            if part_suffix in CAD_SUFFIXES:
                tess, tool, seconds = _cad_to_stl(part, scratch, clscale, angle_deg)
                part_tris, _ = _read_stl(tess)
            elif part_suffix == ".stl":
                part_tris, _ = _read_stl(part)
            elif part_suffix == ".obj":
                part_tris, _ = _read_obj(part)
            else:
                raise IngestError(f"--extra: unsupported extension {part_suffix!r}")
            merged.append(part_tris)
            parts.append({"path": str(part), "sha256": sha256_of(part),
                          "triangles": int(part_tris.shape[0])})
        tris = np.concatenate(merged, axis=0)
        report["merged_parts"] = parts
        report["merged_part_count"] = len(parts)

    # ---- units ------------------------------------------------------------
    raw = analyse(tris)
    detected, why = infer_units(raw["bbox_diagonal"])

    # The file's own declaration outranks both the heuristic and the caller.
    from_file = (report.get("cad_declared_unit") or {}).get("unit")
    if from_file:
        detected = from_file
        why = ("declared by the CAD file itself ({}: {})".format(
            report["cad_declared_unit"]["source"],
            report["cad_declared_unit"]["evidence"]))

    declared = units.lower()
    if from_file and declared not in ("auto", from_file) and not force_units:
        raise IngestError(
            f"--units {declared!r} contradicts the file's own declaration "
            f"{from_file!r} ({report['cad_declared_unit']['source']}: "
            f"{report['cad_declared_unit']['evidence']}). That is a factor of "
            f"{UNIT_TO_METRE.get(declared, float('nan')) / UNIT_TO_METRE[from_file]:.6g} "
            "on every coordinate. Drop --units to trust the file, or pass "
            "--force-units to override it deliberately.")
    if declared == "auto":
        assumed = detected if detected in UNIT_TO_METRE else "unknown"
        source_of_units = "heuristic"
    elif declared in UNIT_TO_METRE:
        assumed, source_of_units = declared, "--units flag (declared by caller)"
    else:
        raise IngestError(f"--units {units!r} is not one of "
                          + ", ".join(sorted(UNIT_TO_METRE)) + ", auto")

    factor = 1.0
    if scale is not None:
        factor = float(scale)
        scaling = f"--scale {scale} applied verbatim"
    elif convert_to_m:
        if assumed not in UNIT_TO_METRE:
            raise IngestError(
                "--convert-to-m needs a known unit, and the heuristic says "
                f"{detected!r} ({why}). Pass --units.")
        factor = UNIT_TO_METRE[assumed]
        scaling = f"{assumed} -> m (x{factor})"
    else:
        scaling = "none — coordinates written exactly as read"

    if factor != 1.0:
        tris = tris * factor

    geometry = analyse(tris) if factor != 1.0 else raw
    report["units"] = {
        "detected": detected,
        "detection_basis": why,
        "assumed": assumed,
        "assumed_from": source_of_units,
        "scale_applied": factor,
        "scaling": scaling,
        "bbox_diagonal_as_read": raw["bbox_diagonal"],
    }
    report["geometry"] = geometry
    report["bbox_min"] = geometry["bbox_min"]
    report["bbox_max"] = geometry["bbox_max"]
    report["triangles"] = geometry["triangles"]
    report["watertight"] = geometry["watertight"]
    report["shells"] = geometry["shells"]
    report["degenerate_triangles"] = geometry["degenerate_triangles"]

    cross = _trimesh_cross_check(source) if suffix == ".stl" and factor == 1.0 else None
    report["cross_check"] = cross or {
        "library": None,
        "note": "trimesh not installed on this box; the edge-manifold test above "
                "is this tool's own and is what the verdict rests on",
    }

    # ---- the snappyHexMesh gate -------------------------------------------
    accepted, refusal = True, None
    if consumer == "snappy" and not geometry["watertight"] and not allow_open:
        accepted = False
        refusal = (
            f"REFUSED for a snappyHexMesh case: the surface is not closed — "
            f"{geometry['boundary_edges']} boundary edge(s) used once and "
            f"{geometry['nonmanifold_edges']} edge(s) used more than twice, across "
            f"{geometry['shells']} shell(s). snappyHexMesh castellation leaks through "
            f"an open surface and the resulting mesh has no inside, so this is refused "
            f"here rather than after an hour of meshing. Pass --allow-open to ingest it "
            f"anyway (legitimate for refinement boxes, baffles and external-domain walls), "
            f"or repair the surface first.")
    report["accepted"] = accepted
    report["refusal_reason"] = refusal

    # ---- write ------------------------------------------------------------
    stem = Path(name).stem if name else source.name.split(".")[0]
    stem = re.sub(r"[^A-Za-z0-9_.-]", "_", stem)
    target_dir = (Path(out_dir).resolve() if out_dir
                  else case_surface_dir(case_id, case_root, out_subdir))
    stl_path = target_dir / f"{stem}.stl"
    json_path = target_dir / f"{stem}.ingest.json"
    png_path = target_dir / f"{stem}.preview.png"

    if accepted:
        write_binary_stl(stl_path, tris,
                         header=f"certonomous geometry_ingest {case_id} {stem}")
        report["stl_path"] = str(stl_path)
        report["stl_bytes"] = stl_path.stat().st_size
        report["stl_sha256"] = sha256_of(stl_path)
        report["stl_encoding"] = "binary"
        report["case_reads_from"] = str(stl_path)
    else:
        target_dir.mkdir(parents=True, exist_ok=True)
        report["stl_path"] = None
        report["case_reads_from"] = None

    if preview:
        report["preview"] = render_preview(
            tris, png_path,
            title=f"{case_id} / {stem}\n{geometry['triangles']:,} tri  "
                  f"{'CLOSED' if geometry['watertight'] else 'OPEN'}")
    else:
        report["preview"] = {"path": None, "renderer": "disabled (--no-preview)"}

    report["seconds_total"] = round(time.time() - started, 3)
    report["cad_converters"] = cad_converters_available()

    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n")
    report["sidecar_path"] = str(json_path)
    return report


def refresh_preview(sidecar: str | Path) -> dict[str, Any]:
    """Re-render the preview of an already-ingested surface.

    The point is to fix a rendering bug without paying for the conversion
    again -- a CAD tessellation that cost twelve minutes of gmsh is not redone
    to redraw a PNG. Only the ``preview`` block of the sidecar is rewritten;
    every measured quantity in it is left exactly as it was.
    """
    path = Path(sidecar).resolve()
    report = json.loads(path.read_text())
    stl = report.get("stl_path")
    if not stl or not Path(stl).is_file():
        raise IngestError(f"{path.name}: names no STL on disk to re-render")
    tris, _ = _read_stl(Path(stl))
    g = report["geometry"]
    png = Path(report["preview"]["path"]) if report.get("preview", {}).get("path") \
        else path.with_suffix("").with_suffix(".preview.png")
    report["preview"] = render_preview(
        tris, png,
        title=f"{report['case_id']} / {Path(stl).stem}\n"
              f"{g['triangles']:,} tri  "
              f"{'CLOSED' if g['watertight'] else 'OPEN'}")
    report["preview"]["rerendered_utc"] = time.strftime(
        "%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    path.write_text(json.dumps(report, indent=2) + "\n")
    return report


def annotate(sidecar: str | Path, *, source_url: str | None = None,
             source_note: str | None = None) -> dict[str, Any]:
    """Attach provenance to a sidecar that has already been written.

    For the case where the conversion is expensive and the provenance arrives
    afterwards -- a twelve-minute tessellation is not repeated to record a URL.
    It writes ONLY the provenance fields and stamps when it did so; no measured
    quantity is touched, and an existing value is not silently replaced.
    """
    path = Path(sidecar).resolve()
    report = json.loads(path.read_text())
    changed = []
    for key, value in (("source_url", source_url), ("source_note", source_note)):
        if value is None:
            continue
        if report.get(key) not in (None, "", value):
            raise IngestError(
                f"{path.name}: {key} is already {report[key]!r}; refusing to "
                "overwrite provenance that is already on record")
        report[key] = value
        changed.append(key)
    if not changed:
        raise IngestError("--annotate needs --source-url and/or --source-note")
    report["annotated_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    report["annotated_fields"] = changed
    path.write_text(json.dumps(report, indent=2) + "\n")
    return report


def list_ingested(case_id: str, case_root: str | Path | None = None,
                  out_subdir: str = CASE_SURFACE_SUBDIR) -> list[dict[str, Any]]:
    """Every sidecar already written for a case, newest first."""
    directory = case_surface_dir(case_id, case_root, out_subdir)
    entries: list[dict[str, Any]] = []
    if not directory.is_dir():
        return entries
    for sidecar in sorted(directory.glob("*.ingest.json")):
        try:
            payload = json.loads(sidecar.read_text())
        except Exception as exc:
            entries.append({"sidecar_path": str(sidecar),
                            "error": f"unreadable sidecar: {exc}"})
            continue
        payload["sidecar_path"] = str(sidecar)
        entries.append(payload)
    entries.sort(key=lambda e: e.get("ingested_utc", ""), reverse=True)
    return entries


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="geometry_ingest.py",
        description="Ingest an STL/OBJ/STEP/IGES file as a case-ready binary STL "
                    "with a JSON sidecar and a preview PNG.")
    parser.add_argument("source", nargs="?", help="the .stl/.obj/.step/.iges file")
    parser.add_argument("--case", dest="case_id", help="case id, e.g. DRIVAER")
    parser.add_argument("--extra", action="append", default=None, metavar="FILE",
                        help="another part of the same body, merged into one STL; "
                             "repeatable, each part's sha256 is recorded")
    parser.add_argument("--case-root", default=None,
                        help="parent of the case directory (default: <repo>/cases)")
    parser.add_argument("--out-dir", default=None,
                        help="write straight here instead of <case>/constant/triSurface")
    parser.add_argument("--out-subdir", default=CASE_SURFACE_SUBDIR,
                        help=f"subdirectory inside the case (default {CASE_SURFACE_SUBDIR})")
    parser.add_argument("--name", default=None, help="output stem (default: source stem)")
    parser.add_argument("--units", default="auto",
                        choices=["auto", *sorted(UNIT_TO_METRE)],
                        help="declare the source unit instead of guessing")
    parser.add_argument("--force-units", action="store_true",
                        help="let --units override the unit the CAD file declares "
                             "about itself (refused by default)")
    parser.add_argument("--convert-to-m", action="store_true",
                        help="rescale into metres using the declared/detected unit")
    parser.add_argument("--scale", type=float, default=None,
                        help="multiply every coordinate by this (overrides --convert-to-m)")
    parser.add_argument("--consumer", default="snappy", choices=["snappy", "generic"],
                        help="snappy enforces the watertight gate (default)")
    parser.add_argument("--allow-open", action="store_true",
                        help="ingest a non-watertight surface for a snappy case anyway")
    parser.add_argument("--no-preview", action="store_true")
    parser.add_argument("--clscale", type=float, default=1.0,
                        help="CAD tessellation length factor; smaller is finer")
    parser.add_argument("--workdir", default=None, help="scratch for CAD conversion")
    parser.add_argument("--reuse-tessellation", action="store_true",
                        help="take the intermediate STL already in --workdir "
                             "instead of tessellating the CAD again")
    parser.add_argument("--source-url", default=None,
                        help="where the file was retrieved from; recorded in the sidecar")
    parser.add_argument("--source-note", default=None,
                        help="free text about provenance; recorded in the sidecar")
    parser.add_argument("--record-only", action="store_true",
                        help="file a CAD original with its sha256 and title block "
                             "but do not tessellate it")
    parser.add_argument("--list", dest="list_case", default=None,
                        metavar="CASE_ID", help="list what a case already has")
    parser.add_argument("--annotate", default=None, metavar="SIDECAR",
                        help="attach --source-url / --source-note to an existing "
                             "*.ingest.json without redoing the conversion")
    parser.add_argument("--repreview", default=None, metavar="SIDECAR",
                        help="re-render the preview named by an existing "
                             "*.ingest.json, without redoing the conversion")
    parser.add_argument("--probe", action="store_true",
                        help="report which CAD converters this box has, and exit")
    parser.add_argument("--json", action="store_true", help="print the sidecar to stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.probe:
        print(json.dumps(cad_converters_available(), indent=2))
        return 0
    if args.annotate:
        report = annotate(args.annotate, source_url=args.source_url,
                          source_note=args.source_note)
        print(f"annotated     {args.annotate}  ({', '.join(report['annotated_fields'])})")
        return 0
    if args.repreview:
        report = refresh_preview(args.repreview)
        print(f"preview       {report['preview'].get('path')}  "
              f"({report['preview'].get('faces_drawn', 0):,} faces)")
        return 0
    if args.list_case:
        print(json.dumps(list_ingested(args.list_case, args.case_root,
                                       args.out_subdir), indent=2))
        return 0
    if not args.source or not args.case_id:
        build_parser().print_usage(sys.stderr)
        print("error: a source file and --case are both required", file=sys.stderr)
        return 2

    try:
        report = ingest(
            args.source, args.case_id, extra=args.extra, case_root=args.case_root,
            out_dir=args.out_dir,
            out_subdir=args.out_subdir, name=args.name, units=args.units,
            convert_to_m=args.convert_to_m, scale=args.scale, consumer=args.consumer,
            allow_open=args.allow_open, preview=not args.no_preview,
            clscale=args.clscale, source_url=args.source_url,
            source_note=args.source_note, record_only=args.record_only,
            force_units=args.force_units,
            reuse_tessellation=args.reuse_tessellation, workdir=args.workdir)
    except IngestError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, indent=2))
    elif report.get("record_only"):
        print(f"source        {report['source_name']}  "
              f"({report['source_format']}, {report['source_bytes']:,} B)")
        print(f"sha256        {report['source_sha256']}")
        print(f"url           {report['source_url']}")
        for k, v in report.get("cad_title_block", {}).items():
            print(f"  {k:<22} {v}")
        print(f"sidecar       {report['sidecar_path']}  (CAD filed, not tessellated)")
    else:
        geometry = report["geometry"]
        lo, hi = geometry["bbox_min"], geometry["bbox_max"]
        print(f"source        {report['source_name']}  "
              f"({report['source_format']}, {report['source_bytes']:,} B)")
        print(f"sha256        {report['source_sha256']}")
        print(f"tool          {report['conversion']['tool']}  "
              f"{report['conversion']['seconds']} s")
        print(f"units         detected {report['units']['detected']}, "
              f"assumed {report['units']['assumed']} "
              f"({report['units']['assumed_from']}); {report['units']['scaling']}")
        print("bbox          [{:.6g} {:.6g} {:.6g}] .. [{:.6g} {:.6g} {:.6g}]".format(*lo, *hi))
        print(f"triangles     {geometry['triangles']:,}   "
              f"degenerate {geometry['degenerate_triangles']:,}")
        print(f"watertight    {geometry['watertight']}  "
              f"(boundary edges {geometry['boundary_edges']:,}, "
              f"non-manifold {geometry['nonmanifold_edges']:,})")
        print(f"shells        {geometry['shells']}")
        print(f"preview       {report['preview'].get('path')}")
        print(f"sidecar       {report['sidecar_path']}")
        if report["accepted"]:
            print(f"case reads    {report['case_reads_from']}")
        else:
            print(f"REFUSED       {report['refusal_reason']}")
    return 0 if report["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
