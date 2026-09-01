#!/usr/bin/env python3
"""Turn a one-cell-thick OpenFOAM ``polyMesh`` into a grid the control room can
draw CELL BY CELL.

WHY THIS EXISTS. The demo panel could show a body and it could show a field,
and between them the meshing stage published ``drawn: False`` -- it said it had
meshed and put no mesh on screen. A picture of a mesh (a rendered PNG) would
have closed the gap in appearance only: a raster cannot be zoomed to the wall
layers, and the wall layers are the whole point of showing a grid at all.

WHAT IS READ, AND WHAT IS NOT. The cells come from the ``back`` (or ``front``)
empty patch of a 2-D case, which carries exactly one quadrilateral face per
cell, so the quad list IS the cell list and no topology is inferred. The
airfoil and slot outlines come from the boundary file's own patch ranges. NO
NUMBER IS COMPUTED HERE: the cell count this emits is ``len(quads)``, read off
the patch, and a caller that wants to check it against a solved grid compares
it against that grid's own record rather than against anything written here.

REFUSES RATHER THAN GUESSES. A mesh with more than two z planes is not a 2-D
case and no slice of it is the grid the solver ran on; a patch whose face count
does not equal the cell count would mean the assumption above is wrong. Both
raise. A payload that silently described some OTHER grid is the failure this
guards -- the campaign it was written for has two grids whose reference areas
differ by a hundred.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


class SliceRefused(Exception):
    """The mesh is not one this can honestly slice."""


def _count_and_body(text: str) -> tuple[int, int]:
    match = re.search(r"^(\d+)\s*\n\(", text, re.M)
    if match is None:
        raise SliceRefused("no <count>\\n( list header in this file")
    return int(match.group(1)), match.end()


def read_points(path: Path) -> list[tuple[float, float, float]]:
    text = path.read_text()
    n, start = _count_and_body(text)
    out: list[tuple[float, float, float]] = []
    for line in text[start:].split("\n"):
        line = line.strip()
        if line == ")":
            break
        if not line.startswith("("):
            continue
        a, b, c = line[1:-1].split()
        out.append((float(a), float(b), float(c)))
    if len(out) != n:
        raise SliceRefused(f"{path} declares {n} points and lists {len(out)}")
    return out


def read_faces(path: Path) -> list[tuple[int, ...]]:
    text = path.read_text()
    n, start = _count_and_body(text)
    out: list[tuple[int, ...]] = []
    for line in text[start:].split("\n"):
        line = line.strip()
        if line == ")":
            break
        if "(" not in line:
            continue
        _, rest = line.split("(", 1)
        out.append(tuple(int(x) for x in rest[: rest.rindex(")")].split()))
    if len(out) != n:
        raise SliceRefused(f"{path} declares {n} faces and lists {len(out)}")
    return out


def read_boundary(path: Path) -> dict[str, tuple[int, int]]:
    text = path.read_text()
    found = re.findall(
        r"(\w+)\s*\{[^}]*?nFaces\s+(\d+);\s*startFace\s+(\d+);", text, re.S)
    return {name: (int(n), int(s)) for name, n, s in found}


def slice_payload(poly: Path, *, wall_patch: str = "airfoil",
                  slot_patch: str = "jetSlot") -> dict:
    points = read_points(poly / "points")
    faces = read_faces(poly / "faces")
    patches = read_boundary(poly / "boundary")

    planes = sorted({round(p[2], 12) for p in points})
    if len(planes) != 2:
        raise SliceRefused(
            f"this mesh has {len(planes)} z planes; only a one-cell-thick 2-D "
            f"case has a slice that IS its cell list")
    z_back = planes[0]

    plane_patch = next((n for n in ("back", "front") if n in patches), None)
    if plane_patch is None:
        raise SliceRefused("no back/front empty patch, so there is no per-cell "
                           "face list to read the cells off")
    n_faces, start = patches[plane_patch]
    plane_faces = faces[start:start + n_faces]
    if any(len(f) != 4 for f in plane_faces):
        raise SliceRefused("a cell face on the empty patch is not a quad")

    node_of: dict[int, int] = {}
    nodes: list[list[float]] = []

    def nid(i: int) -> int:
        got = node_of.get(i)
        if got is None:
            got = node_of[i] = len(nodes)
            nodes.append([round(points[i][0], 6), round(points[i][1], 6)])
        return got

    quads = [[nid(i) for i in f] for f in plane_faces]

    def outline(name: str) -> list[list[int]]:
        if name not in patches:
            return []
        n, s = patches[name]
        edges = []
        for face in faces[s:s + n]:
            on = [i for i in face if abs(points[i][2] - z_back) < 1e-9]
            if len(on) == 2:
                edges.append([nid(on[0]), nid(on[1])])
        return edges

    wall = outline(wall_patch)
    slot = outline(slot_patch)

    xs = [n[0] for n in nodes]
    ys = [n[1] for n in nodes]
    slot_pts = [nodes[i] for e in slot for i in e] or [nodes[i] for e in wall
                                                       for i in e]
    return {
        "cells": len(quads),
        "nodes": nodes,
        "quads": quads,
        "wall": wall,
        "slot": slot,
        "bounds": [min(xs), min(ys), max(xs), max(ys)],
        # Where the two reveal frames look. Both are derived from the wall and
        # slot outlines this file just read, never typed: a grid whose body sits
        # somewhere else frames itself correctly.
        "body_box": _box([nodes[i] for e in wall for i in e], pad=0.55)
        if wall else [min(xs), min(ys), max(xs), max(ys)],
        # Padded to about ten slot heights. A window the size of the slot shows
        # the slot and NOT the wall layers packed against it, and the wall
        # layers are the half a viewer cannot see anywhere else.
        "slot_box": _box(slot_pts, pad=4.5) if slot_pts else None,
    }


def _box(pts: list[list[float]], *, pad: float) -> list[float]:
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    span = max(x1 - x0, y1 - y0) or 1.0
    m = pad * span
    return [x0 - m, y0 - m, x1 + m, y1 + m]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("polymesh", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--wall-patch", default="airfoil")
    ap.add_argument("--slot-patch", default="jetSlot")
    args = ap.parse_args()
    payload = slice_payload(args.polymesh, wall_patch=args.wall_patch,
                            slot_patch=args.slot_patch)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, separators=(",", ":")))
    print(f"{payload['cells']} cells, {len(payload['nodes'])} nodes, "
          f"{args.out.stat().st_size / 1e6:.2f} MB -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
