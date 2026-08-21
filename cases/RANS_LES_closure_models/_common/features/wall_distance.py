#!/usr/bin/env python3
"""Wall distance from the polyMesh, for cases that do not ship `walldist`.

Nearest distance from each cell centre to any face centre on a patch whose type
is `wall`. This is a lower bound on the true normal distance and is exact in the
median for a body-fitted mesh; it is used only for the q1 feature, which itself
saturates at 2.
"""
from __future__ import annotations
import os, re
import numpy as np
from scipy.spatial import cKDTree


def _strip(t):
    return re.sub(r"/\*.*?\*/", "", t, flags=re.S)


def _read_list(path):
    """Read an OpenFOAM points or faces file as a python list of arrays."""
    t = _strip(open(path).read())
    body = t[t.index("(", t.index("\n(") if "\n(" in t else 0):]
    return body


def read_points(mesh):
    t = _strip(open(os.path.join(mesh, "points")).read())
    m = re.search(r"^\s*(\d+)\s*\n\(", t, re.M)
    n = int(m.group(1)); start = m.end()
    vals = np.fromstring(t[start:].replace("(", " ").replace(")", " ")[: ],
                         sep=" ", count=3 * n)
    return vals.reshape(n, 3)


def read_faces(mesh):
    t = _strip(open(os.path.join(mesh, "faces")).read())
    m = re.search(r"^\s*(\d+)\s*\n\(", t, re.M)
    n = int(m.group(1)); pos = m.end()
    faces = []
    for _ in range(n):
        a = t.index("(", pos); b = t.index(")", a)
        faces.append(np.fromstring(t[a + 1:b], sep=" ", dtype=int))
        pos = b + 1
    return faces


def wall_patches(mesh):
    t = _strip(open(os.path.join(mesh, "boundary")).read())
    body = t[t.index("("):t.rindex(")")]
    out = []
    for m in re.finditer(r"(\w+)\s*\{(.*?)\}", body, re.S):
        d = m.group(2)
        ty = re.search(r"type\s+(\w+)\s*;", d)
        nf = re.search(r"nFaces\s+(\d+)\s*;", d)
        sf = re.search(r"startFace\s+(\d+)\s*;", d)
        if ty and nf and sf and ty.group(1) == "wall":
            out.append((m.group(1), int(nf.group(1)), int(sf.group(1))))
    return out


def wall_distance(case_dir, C):
    mesh = os.path.join(case_dir, "constant", "polyMesh")
    pts = read_points(mesh)
    faces = read_faces(mesh)
    wp = wall_patches(mesh)
    if not wp:
        return None, []
    centres = []
    for _, nf, sf in wp:
        for f in faces[sf:sf + nf]:
            centres.append(pts[f].mean(axis=0))
    centres = np.asarray(centres)
    d, _ = cKDTree(centres).query(C, k=1)
    return d, [n for n, _, _ in wp]
