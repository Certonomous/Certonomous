#!/usr/bin/env python3
"""Extract the `wing` wall patch from an OpenFOAM polyMesh and compare it,
by face count and by bounding box, against a candidate STL surface.

This is the 'is the render the computational surface' check, done by COUNTING
and by MEASURING, not by assuming.
"""
import gzip
import os
import re
import struct
import sys


def _open(path):
    if os.path.exists(path):
        return open(path, "rb")
    if os.path.exists(path + ".gz"):
        return gzip.open(path + ".gz", "rb")
    raise FileNotFoundError(path)


def read_foam_list(path):
    """Read an OpenFOAM list body. Returns list of raw token strings per entry."""
    with _open(path) as fh:
        txt = fh.read().decode("ascii", "replace")
    # strip header dict
    i = txt.find("// *")
    j = txt.find("\n", i)
    body = txt[j:]
    # find "<count>\n(" ... ")"
    m = re.search(r"^\s*(\d+)\s*\(", body, re.M)
    if not m:
        raise ValueError("no list in " + path)
    n = int(m.group(1))
    start = m.end()
    depth = 1
    k = start
    while k < len(body) and depth:
        if body[k] == "(":
            depth += 1
        elif body[k] == ")":
            depth -= 1
        k += 1
    return n, body[start:k - 1]


def read_points(path):
    n, body = read_foam_list(path)
    pts = []
    for m in re.finditer(r"\(([^)]*)\)", body):
        a = m.group(1).split()
        pts.append((float(a[0]), float(a[1]), float(a[2])))
    assert len(pts) == n, f"points {len(pts)} != {n}"
    return pts


def read_faces(path):
    n, body = read_foam_list(path)
    faces = []
    for m in re.finditer(r"(\d+)\s*\(([^)]*)\)", body):
        faces.append([int(x) for x in m.group(2).split()])
    assert len(faces) == n, f"faces {len(faces)} != {n}"
    return faces


def read_boundary(path):
    with _open(path) as fh:
        txt = fh.read().decode("ascii", "replace")
    out = {}
    for m in re.finditer(r"(\w+)\s*\{([^}]*)\}", txt):
        d = dict(re.findall(r"(\w+)\s+([^;]+);", m.group(2)))
        if "nFaces" in d:
            out[m.group(1)] = (int(d["nFaces"]), int(d["startFace"]))
    return out


def bbox(pts):
    lo = [min(p[i] for p in pts) for i in range(3)]
    hi = [max(p[i] for p in pts) for i in range(3)]
    return lo, hi


def read_stl(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    n = struct.unpack_from("<I", raw, 80)[0]
    assert 84 + 50 * n == len(raw), "not binary STL"
    tris = []
    off = 84
    for _ in range(n):
        v = struct.unpack_from("<12f", raw, off)
        tris.append((v[3:6], v[6:9], v[9:12]))
        off += 50
    return tris


def main(mesh_dir, patch, stl_path):
    bnd = read_boundary(os.path.join(mesh_dir, "boundary"))
    print("PATCHES COUNTED FROM boundary:")
    for k, (nf, sf) in bnd.items():
        print(f"  {k:10s} nFaces={nf:8d} startFace={sf}")
    nf, sf = bnd[patch]
    faces = read_faces(os.path.join(mesh_dir, "faces"))
    pts = read_points(os.path.join(mesh_dir, "points"))
    patch_faces = faces[sf:sf + nf]
    print(f"\nCOUNTED patch '{patch}': {len(patch_faces)} faces "
          f"(boundary declared {nf})")
    sizes = {}
    for f in patch_faces:
        sizes[len(f)] = sizes.get(len(f), 0) + 1
    print(f"  face vertex counts: {sizes}")
    ids = sorted({i for f in patch_faces for i in f})
    ppts = [pts[i] for i in ids]
    lo, hi = bbox(ppts)
    print(f"  unique surface points: {len(ids)}")
    for i, ax in enumerate("XYZ"):
        print(f"  mesh {ax}: min {lo[i]: .6f} max {hi[i]: .6f} "
              f"extent {hi[i]-lo[i]: .6f}")

    tris = read_stl(stl_path)
    slo, shi = bbox([v for t in tris for v in t])
    print(f"\nSTL {stl_path}: {len(tris)} triangles "
          f"= {len(tris)/2:.1f} quads")
    for i, ax in enumerate("XYZ"):
        print(f"  stl  {ax}: min {slo[i]: .6f} max {shi[i]: .6f} "
              f"extent {shi[i]-slo[i]: .6f}")
    print("\nAGREEMENT (mesh patch vs STL):")
    print(f"  triangles / mesh faces = {len(tris)}/{nf} = {len(tris)/nf:.4f}")
    for i, ax in enumerate("XYZ"):
        d = max(abs(lo[i] - slo[i]), abs(hi[i] - shi[i]))
        print(f"  {ax} max corner difference = {d:.3e} m")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
