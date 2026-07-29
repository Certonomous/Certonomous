"""Minimal, dependency-free OpenFOAM ASCII list/dict parsers used for the F6b
gate analysis (bottomWall face centroids + boundaryField vector lists).
Written for this rung; not a general-purpose library.
"""
from __future__ import annotations
import re
import numpy as np


def _read_after_foamfile(path):
    with open(path, "r", errors="ignore") as f:
        return f.read()


def read_points(points_path):
    text = _read_after_foamfile(points_path)
    # find the count line followed by '(' then N '(x y z)' entries
    m = re.search(r"\n(\d+)\s*\n\s*\(\s*\n(.*?)\n\s*\)", text, re.S)
    n = int(m.group(1))
    body = m.group(2)
    vals = re.findall(r"\(([^()]*)\)", body)
    assert len(vals) == n, f"points: expected {n}, got {len(vals)}"
    pts = np.array([[float(x) for x in v.split()] for v in vals])
    return pts


def read_faces(faces_path):
    text = _read_after_foamfile(faces_path)
    m = re.search(r"\n(\d+)\s*\n\s*\(\s*\n(.*?)\n\s*\)\s*\n*\s*(?://.*)?$", text, re.S)
    n = int(m.group(1))
    body = m.group(2)
    # entries like: 4(0 1 2 3)
    entries = re.findall(r"\d+\(([^()]*)\)", body)
    assert len(entries) == n, f"faces: expected {n}, got {len(entries)}"
    faces = [[int(x) for x in e.split()] for e in entries]
    return faces


def read_boundary(boundary_path):
    text = _read_after_foamfile(boundary_path)
    # crude block parser: name { ... nFaces N; startFace S; ... }
    patches = {}
    for m in re.finditer(r"(\w+)\s*\{([^{}]*)\}", text):
        name, body = m.group(1), m.group(2)
        nf = re.search(r"nFaces\s+(\d+);", body)
        sf = re.search(r"startFace\s+(\d+);", body)
        if nf and sf:
            patches[name] = (int(sf.group(1)), int(nf.group(1)))
    return patches


def face_centroids(points, faces, start, count):
    cents = np.zeros((count, 3))
    for i in range(count):
        verts = faces[start + i]
        cents[i] = points[verts].mean(axis=0)
    return cents


def read_vector_boundary_field(field_path, patch_name):
    """Return Nx3 array of a volVectorField's boundaryField values for one patch
    (handles 'nonuniform List<vector>' and 'uniform (x y z)')."""
    text = _read_after_foamfile(field_path)
    m = re.search(patch_name + r"\s*\{(.*?)\n\s*\}", text, re.S)
    assert m, f"patch {patch_name} not found in {field_path}"
    body = m.group(1)
    mu = re.search(r"uniform\s*\(([^()]*)\)\s*;", body)
    if mu and "nonuniform" not in body:
        v = [float(x) for x in mu.group(1).split()]
        return None, np.array(v)  # caller should broadcast using known face count
    mn = re.search(r"nonuniform\s+List<vector>\s*\n(\d+)\s*\n\s*\(\s*\n(.*?)\n\s*\)", body, re.S)
    assert mn, f"could not parse nonuniform vector list for {patch_name} in {field_path}"
    n = int(mn.group(1))
    vals = re.findall(r"\(([^()]*)\)", mn.group(2))
    assert len(vals) == n
    arr = np.array([[float(x) for x in v.split()] for v in vals])
    return arr, None


def read_internal_field(field_path):
    """Robust internalField reader for scalar or vector volFields (handles the
    trailing-space-after-')' quirk in some benchmark-shipped files that trips
    up Ofpp's naive slice-based vector parser)."""
    text = _read_after_foamfile(field_path)
    m = re.search(r"internalField\s+nonuniform\s+List<(scalar|vector)>\s*\n(\d+)\s*\n\s*\(\s*\n(.*?)\n\s*\)\s*\n\s*;", text, re.S)
    if m:
        kind, n, body = m.group(1), int(m.group(2)), m.group(3)
        if kind == "scalar":
            vals = [float(x) for x in body.split()]
            assert len(vals) == n, f"{field_path}: expected {n} scalars, got {len(vals)}"
            return np.array(vals)
        else:
            vals = re.findall(r"\(([^()]*)\)", body)
            assert len(vals) == n, f"{field_path}: expected {n} vectors, got {len(vals)}"
            return np.array([[float(x) for x in v.split()] for v in vals])
    mu = re.search(r"internalField\s+uniform\s+\(([^()]*)\)\s*;", text)
    if mu:
        return np.array([float(x) for x in mu.group(1).split()])
    mu2 = re.search(r"internalField\s+uniform\s+([\-0-9.eE]+)\s*;", text)
    if mu2:
        return float(mu2.group(1))
    raise ValueError(f"could not parse internalField in {field_path}")


def read_scalar_boundary_field(field_path, patch_name):
    text = _read_after_foamfile(field_path)
    m = re.search(patch_name + r"\s*\{(.*?)\n\s*\}", text, re.S)
    assert m, f"patch {patch_name} not found in {field_path}"
    body = m.group(1)
    mu = re.search(r"uniform\s+([\-0-9.eE]+)\s*;", body)
    if mu and "nonuniform" not in body:
        return None, float(mu.group(1))
    mn = re.search(r"nonuniform\s+List<scalar>\s*\n(\d+)\s*\n\s*\(\s*\n(.*?)\n\s*\)", body, re.S)
    assert mn, f"could not parse nonuniform scalar list for {patch_name} in {field_path}"
    n = int(mn.group(1))
    body2 = mn.group(2)
    vals = [float(x) for x in body2.split()]
    assert len(vals) == n
    return np.array(vals), None
