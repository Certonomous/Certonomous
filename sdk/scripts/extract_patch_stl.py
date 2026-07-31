#!/usr/bin/env python3
"""Extract one boundary patch of an OpenFOAM polyMesh as a binary STL.

This is how Acts 6, 8 and 9 got their sdk/geometry/*.stl files: read straight
out of the constant/polyMesh that was actually meshed and solved (the NASA
hump's "bottom" wall, the ONERA M6 and CRM wings' "wing" patch), never a
redrawn or looked-up lookalike. Plain-text parser, no OpenFOAM install
required; handles both ascii and gzip-compressed polyMesh files.

    python3 extract_patch_stl.py <polyMesh_dir> <patch_name> <out.stl> [--scale S]
"""
from __future__ import annotations

import gzip
import re
import struct
import sys
from pathlib import Path


def _read_text(polymesh: Path, name: str) -> str:
    plain = polymesh / name
    gz = polymesh / f"{name}.gz"
    if plain.exists():
        return plain.read_text(errors="replace")
    if gz.exists():
        with gzip.open(gz, "rt", errors="replace") as fh:
            return fh.read()
    raise FileNotFoundError(f"{name}(.gz) not found in {polymesh}")


def _strip_foam_header(text: str) -> str:
    # Drop the banner comment and the FoamFile{...} block; keep everything
    # from the first top-level list/scalar count onward.
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"FoamFile\s*\{.*?\}", "", text, flags=re.S)
    # Strip // line comments (never inside data, points/faces have none).
    text = re.sub(r"//.*", "", text)
    return text


def _parse_points(text: str) -> list[tuple[float, float, float]]:
    text = _strip_foam_header(text)
    match = re.search(r"\(\s*(\(.*?\))\s*\)\s*$", text, flags=re.S)
    body = match.group(1) if match else text
    nums = re.findall(r"\(([^()]*)\)", body)
    points = []
    for triple in nums:
        parts = triple.split()
        if len(parts) == 3:
            points.append((float(parts[0]), float(parts[1]), float(parts[2])))
    return points


def _parse_faces(text: str) -> list[list[int]]:
    text = _strip_foam_header(text)
    # Each face is "N(i0 i1 ... iN-1)" -- capture the count and the index list.
    faces = []
    for m in re.finditer(r"(\d+)\s*\(([^()]*)\)", text):
        n = int(m.group(1))
        idx = [int(x) for x in m.group(2).split()]
        if len(idx) == n and n >= 3:
            faces.append(idx)
    return faces


def _parse_boundary(text: str) -> dict[str, tuple[int, int]]:
    text = _strip_foam_header(text)
    patches: dict[str, tuple[int, int]] = {}
    for m in re.finditer(
            r"(\w+)\s*\{([^{}]*)\}", text):
        name, body = m.group(1), m.group(2)
        nf = re.search(r"nFaces\s+(\d+)\s*;", body)
        sf = re.search(r"startFace\s+(\d+)\s*;", body)
        if nf and sf:
            patches[name] = (int(sf.group(1)), int(nf.group(1)))
    return patches


def extract(polymesh_dir: str, patch: str, out_path: str, scale: float = 1.0) -> dict:
    polymesh = Path(polymesh_dir)
    points = _parse_points(_read_text(polymesh, "points"))
    faces = _parse_faces(_read_text(polymesh, "faces"))
    boundary = _parse_boundary(_read_text(polymesh, "boundary"))
    if patch not in boundary:
        raise KeyError(f"patch {patch!r} not in boundary: {sorted(boundary)}")
    start, count = boundary[patch]
    patch_faces = faces[start:start + count]
    if len(patch_faces) != count:
        raise RuntimeError(
            f"expected {count} faces for {patch!r} at offset {start}, "
            f"got {len(patch_faces)} (faces list has {len(faces)} entries)")

    triangles: list[tuple[tuple[float, float, float], ...]] = []
    for face in patch_faces:
        verts = [points[i] for i in face]
        # Fan triangulation from vertex 0 -- exact for the planar-ish quads
        # and simple polygons snappyHexMesh/pyHyp write for a wall patch.
        for i in range(1, len(verts) - 1):
            triangles.append((verts[0], verts[i], verts[i + 1]))

    if scale != 1.0:
        triangles = [tuple((x * scale, y * scale, z * scale) for x, y, z in tri)
                     for tri in triangles]

    _write_binary_stl(out_path, triangles)
    xs = [p[0] for tri in triangles for p in tri]
    ys = [p[1] for tri in triangles for p in tri]
    zs = [p[2] for tri in triangles for p in tri]
    return {"patch": patch, "faces": len(patch_faces), "triangles": len(triangles),
            "bounds": {"x": [min(xs), max(xs)], "y": [min(ys), max(ys)],
                       "z": [min(zs), max(zs)]}}


def _write_binary_stl(out_path: str, triangles) -> None:
    with open(out_path, "wb") as fh:
        header = b"Certonomous patch-extracted STL"
        fh.write((header + b" " * 80)[:80])
        fh.write(struct.pack("<I", len(triangles)))
        for a, b, c in triangles:
            ux, uy, uz = _normal(a, b, c)
            fh.write(struct.pack("<3f", ux, uy, uz))
            for v in (a, b, c):
                fh.write(struct.pack("<3f", *v))
            fh.write(struct.pack("<H", 0))


def _normal(a, b, c):
    ux = (b[1] - a[1]) * (c[2] - a[2]) - (b[2] - a[2]) * (c[1] - a[1])
    uy = (b[2] - a[2]) * (c[0] - a[0]) - (b[0] - a[0]) * (c[2] - a[2])
    uz = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    length = (ux * ux + uy * uy + uz * uz) ** 0.5
    if length == 0:
        return (0.0, 0.0, 0.0)
    return (ux / length, uy / length, uz / length)


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("polymesh_dir")
    ap.add_argument("patch")
    ap.add_argument("out_stl")
    ap.add_argument("--scale", type=float, default=1.0)
    args = ap.parse_args()
    info = extract(args.polymesh_dir, args.patch, args.out_stl, args.scale)
    print(info)
