#!/usr/bin/env python3
"""Read an OpenFOAM ascii constant/polyMesh and return per-patch AREA and the
projected (x-normal) area.  Pure python: the comparator must be able to verify the
mesh geometry that the frozen Aref assumes WITHOUT trusting the solver or any
function object.  Imported by grade_vmfl036.py; runnable standalone for a check.
"""
import os
import re


def _tokens(path):
    txt = open(path).read()
    txt = re.sub(r"/\*.*?\*/", " ", txt, flags=re.S)
    txt = re.sub(r"//[^\n]*", " ", txt)
    i = txt.find("FoamFile")
    if i < 0:
        raise ValueError("no FoamFile header in %s" % path)
    j = txt.index("}", txt.index("{", i))
    return txt[j + 1:]


def read_points(mesh_dir):
    body = _tokens(os.path.join(mesh_dir, "points"))
    vals = re.findall(r"\(\s*([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s*\)", body)
    return [(float(a), float(b), float(c)) for a, b, c in vals]


def read_faces(mesh_dir):
    body = _tokens(os.path.join(mesh_dir, "faces"))
    out = []
    # NOTE: no \s* between the count and "(" -- that is what separates a
    # face entry "4(1 5 7 3)" from the outer list header "12400\n(".
    for m in re.finditer(r"(\d+)\(([^)]*)\)", body):
        out.append([int(t) for t in m.group(2).split()])
    return out


def read_boundary(mesh_dir):
    body = _tokens(os.path.join(mesh_dir, "boundary"))
    out = {}
    for m in re.finditer(r"(\w+)\s*\{([^}]*)\}", body):
        d = dict(re.findall(r"(\w+)\s+([^;]+);", m.group(2)))
        if "nFaces" in d and "startFace" in d:
            out[m.group(1)] = {"type": d.get("type", "").strip(),
                               "nFaces": int(d["nFaces"]),
                               "startFace": int(d["startFace"])}
    return out


def face_area_vector(pts, f):
    """Newell's method -- exact for planar polygons, robust for warped quads."""
    n = len(f)
    c = [sum(pts[i][k] for i in f) / n for k in range(3)]
    ax = ay = az = 0.0
    for i in range(n):
        p = pts[f[i]]
        q = pts[f[(i + 1) % n]]
        u = (p[0] - c[0], p[1] - c[1], p[2] - c[2])
        v = (q[0] - c[0], q[1] - c[1], q[2] - c[2])
        ax += u[1] * v[2] - u[2] * v[1]
        ay += u[2] * v[0] - u[0] * v[2]
        az += u[0] * v[1] - u[1] * v[0]
    return (0.5 * ax, 0.5 * ay, 0.5 * az)


def patch_areas(mesh_dir):
    pts = read_points(mesh_dir)
    faces = read_faces(mesh_dir)
    bnd = read_boundary(mesh_dir)
    out = {}
    for name, b in bnd.items():
        tot = 0.0
        proj_pos = 0.0
        for k in range(b["startFace"], b["startFace"] + b["nFaces"]):
            a = face_area_vector(pts, faces[k])
            mag = (a[0] ** 2 + a[1] ** 2 + a[2] ** 2) ** 0.5
            tot += mag
            if a[0] > 0:
                proj_pos += a[0]
        out[name] = {"type": b["type"], "nFaces": b["nFaces"],
                     "area": tot, "proj_x_pos": proj_pos}
    return out


if __name__ == "__main__":
    import sys
    for k, v in sorted(patch_areas(sys.argv[1]).items()):
        print("%-12s type=%-8s nFaces=%-6d area=%.12g  proj_x+=%.12g"
              % (k, v["type"], v["nFaces"], v["area"], v["proj_x_pos"]))
