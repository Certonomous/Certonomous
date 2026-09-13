#!/usr/bin/env python3
"""yplus_area_weighted.py -- per-FACE y+ and EXACT per-face areas for DRIVAER.

WHY THIS EXISTS.  Gate Y1 (DRIVAER_R2_LAYERED_PREREGISTRATION.md sec."Gate Y1") is
registered as the **AREA-WEIGHTED MEDIAN y+ over LAYERED VEHICLE WALL FACES**, band
[30, 300].  A patch-average y+ read off a solver log CANNOT evaluate that gate:
it is unweighted and it is per-patch, not per-face.  This module supplies the two
missing inputs -- per-face y+ from the written yPlus field, and per-face area
computed from the mesh by Newell's formula -- so that the registered statistic can
be produced as registered, rather than a different statistic wearing its name.

IT DOES NOT DECIDE Y1.  Y1 additionally needs the LAYERED/UNLAYERED classification
for the level, which is a separate measurement and not this module's to invent.
This module refuses to emit a group statistic without an explicit classification.

IT IS NOT WIRED INTO grade_drivaer.py (hash-pinned) OR SUBOFF's comparator.

CONTROLS (CLAUDE.md rule 3), all driven before any number is emitted:
  * COUNT control -- per patch, len(y+ values) must equal the mesh's nFaces for
    that patch.  A mismatch means the field and the mesh are not the same object
    and the reader REFUSES rather than zipping two lists of different length.
  * AREA control -- a face of known area is planted into a copy of the points
    file is NOT possible without perturbing the mesh, so instead the computed
    areas are checked against an independent closure identity: for a CLOSED
    mesh the sum of outward area VECTORS over all boundary faces is zero.  A
    face-area routine that is wrong in magnitude or winding breaks that identity.
  * PLANT control -- a known y+ is planted into a COPY of the yPlus field at a
    named patch and face index, read back through the same parser, and required
    to appear at exactly that face with nothing else moved.
"""
import os
import re
import sys
import math
import json
import argparse

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))
from yplus_reader_guard import YPlusReaderBlind

PLANT_VALUE = 8.675309e+02


def _strip(path):
    """Yield payload lines of an OpenFOAM ASCII file (header/comments removed)."""
    with open(path, errors="replace") as fh:
        txt = fh.read()
    txt = re.sub(r"/\*.*?\*/", " ", txt, flags=re.S)
    txt = re.sub(r"//[^\n]*", " ", txt)
    txt = re.sub(r"FoamFile\s*\{.*?\}", " ", txt, flags=re.S)
    return txt


def read_boundary(path):
    txt = _strip(path)
    body = txt[txt.index("("):]
    out, depth, i = [], 0, 0
    for m in re.finditer(r"(\w[\w.\-]*)\s*\{(.*?)\}", body, flags=re.S):
        name, blk = m.group(1), m.group(2)
        nf = re.search(r"nFaces\s+(\d+)\s*;", blk)
        sf = re.search(r"startFace\s+(\d+)\s*;", blk)
        ty = re.search(r"\btype\s+(\w+)\s*;", blk)
        if nf and sf:
            out.append({"patch": name, "nFaces": int(nf.group(1)),
                        "startFace": int(sf.group(1)),
                        "type": ty.group(1) if ty else "?"})
    if not out:
        raise YPlusReaderBlind("%s: no patch block parsed." % path)
    return out


def read_points(path):
    txt = _strip(path)
    n = int(re.search(r"(\d+)\s*\(", txt).group(1))
    num = r"[-+0-9.eEdD]+"
    pts = [(float(a), float(b), float(c)) for a, b, c in
           re.findall(r"\((%s)\s+(%s)\s+(%s)\)" % (num, num, num), txt)]
    if len(pts) != n:
        raise YPlusReaderBlind("%s: header says %d points, parsed %d."
                               % (path, n, len(pts)))
    return pts


def read_faces_from(path, first):
    """Parse the faces list, returning only faces with index >= first."""
    txt = _strip(path)
    m = re.search(r"(\d+)\s*\(", txt)
    n = int(m.group(1))
    out, idx = {}, 0
    for fm in re.finditer(r"(\d+)\s*\(([^)]*)\)", txt[m.end():]):
        if idx >= first:
            out[idx] = [int(x) for x in fm.group(2).split()]
        idx += 1
    if idx != n:
        raise YPlusReaderBlind("%s: header says %d faces, parsed %d."
                               % (path, n, idx))
    return out


def face_area_vector(pts, verts):
    """Newell's formula -> outward area VECTOR; |v| is the exact polygon area."""
    ax = ay = az = 0.0
    k = len(verts)
    for i in range(k):
        x1, y1, z1 = pts[verts[i]]
        x2, y2, z2 = pts[verts[(i + 1) % k]]
        ax += (y1 - y2) * (z1 + z2)
        ay += (z1 - z2) * (x1 + x2)
        az += (x1 - x2) * (y1 + y2)
    return (0.5 * ax, 0.5 * ay, 0.5 * az)


def read_yplus_field(path):
    """Per-face y+ per patch from the written volScalarField boundaryField."""
    txt = _strip(path)
    bf = txt.index("boundaryField")
    body = txt[bf:]
    out = {}
    for m in re.finditer(r"(\w[\w.\-]*)\s*\{(.*?)\}", body, flags=re.S):
        name, blk = m.group(1), m.group(2)
        nu = re.search(r"nonuniform\s+List<scalar>\s*(\d+)\s*\((.*?)\)",
                       blk, flags=re.S)
        if nu:
            vals = [float(x) for x in nu.group(2).split()]
            if len(vals) != int(nu.group(1)):
                raise YPlusReaderBlind(
                    "%s patch %s: list header says %s, parsed %d."
                    % (path, name, nu.group(1), len(vals)))
            out[name] = vals
            continue
        un = re.search(r"uniform\s+([-\d.eE+]+)\s*;", blk)
        if un:
            out[name] = ("uniform", float(un.group(1)))
    if not out:
        raise YPlusReaderBlind("%s: no boundaryField entry parsed." % path)
    return out


def wmedian(values, weights):
    """Weighted median: smallest v where cumulative weight reaches half."""
    pairs = sorted(zip(values, weights))
    tot = sum(weights)
    if tot <= 0:
        raise YPlusReaderBlind("weighted median over zero total weight.")
    acc = 0.0
    for v, w in pairs:
        acc += w
        if acc >= 0.5 * tot:
            return v
    return pairs[-1][0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", required=True)
    ap.add_argument("--time", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--groups", help="JSON {group_name: [patch, ...]}; the "
                    "area-weighted median is then POOLED OVER FACES within each "
                    "group, which is the shape Gate Y1 is registered in. Without "
                    "it no group statistic is emitted -- the classification is "
                    "not this module's to invent.")
    a = ap.parse_args()
    os.makedirs(a.scratch, exist_ok=True)
    mesh = os.path.join(a.case, "constant", "polyMesh")
    ypath = os.path.join(a.case, a.time, "yPlus")

    bnd = read_boundary(os.path.join(mesh, "boundary"))
    first = min(p["startFace"] for p in bnd)
    pts = read_points(os.path.join(mesh, "points"))
    faces = read_faces_from(os.path.join(mesh, "faces"), first)
    yf = read_yplus_field(ypath)

    # ---- AREA control: closed-surface identity sum(Sf) ~ 0 over ALL boundary
    tot = [0.0, 0.0, 0.0]
    scale = 0.0
    for p in bnd:
        for i in range(p["startFace"], p["startFace"] + p["nFaces"]):
            v = face_area_vector(pts, faces[i])
            tot[0] += v[0]; tot[1] += v[1]; tot[2] += v[2]
            scale += math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    resid = math.sqrt(sum(x * x for x in tot)) / scale
    area_ctrl = {"identity": "sum of outward boundary area VECTORS == 0 on a "
                             "closed mesh", "relative_residual": resid,
                 "total_boundary_area_m2": scale,
                 "passed": resid < 1e-9}
    if not area_ctrl["passed"]:
        print(json.dumps({"REFUSED": "AREA control failed", "area_control":
                          area_ctrl}, indent=1), file=sys.stderr)
        return 2

    # ---- COUNT control + per-patch statistics
    per, count_fail, face_rows = [], [], []
    for p in bnd:
        name = p["patch"]
        vals = yf.get(name)
        if vals is None:
            continue
        if isinstance(vals, tuple):
            vals = [vals[1]] * p["nFaces"]
        if len(vals) != p["nFaces"]:
            count_fail.append({"patch": name, "mesh_nFaces": p["nFaces"],
                               "field_values": len(vals)})
            continue
        areas = [math.sqrt(sum(c * c for c in face_area_vector(pts, faces[i])))
                 for i in range(p["startFace"], p["startFace"] + p["nFaces"])]
        A = sum(areas)
        for _v, _w in zip(vals, areas):
            face_rows.append((name, _v, _w))
        per.append({"patch": name, "type": p["type"], "nFaces": p["nFaces"],
                    "area_m2": A,
                    "yplus_area_weighted_median": wmedian(vals, areas),
                    "yplus_area_weighted_mean": sum(v * w for v, w in
                                                    zip(vals, areas)) / A,
                    "yplus_min": min(vals), "yplus_max": max(vals),
                    "yplus_face_mean": sum(vals) / len(vals)})
    if count_fail:
        print(json.dumps({"REFUSED": "COUNT control failed -- field and mesh "
                          "disagree on face counts", "mismatches": count_fail},
                         indent=1), file=sys.stderr)
        return 2

    # ---- PLANT control on the field reader
    target = max((p for p in per if p["nFaces"] > 10),
                 key=lambda p: p["nFaces"])["patch"]
    raw = open(ypath, errors="replace").read()
    mm = re.search(r"(\n\s*%s\s*\{.*?nonuniform\s+List<scalar>\s*\d+\s*\(\s*)"
                   r"(\S+)" % re.escape(target), raw, flags=re.S)
    if not mm:
        print(json.dumps({"REFUSED": "PLANT control could not place a plant on "
                          "patch %s" % target}, indent=1), file=sys.stderr)
        return 2
    planted_path = os.path.join(a.scratch, "PLANTED_yPlus")
    with open(planted_path, "w") as fh:
        fh.write(raw[:mm.start(2)] + repr(PLANT_VALUE) + raw[mm.end(2):])
    y2 = read_yplus_field(planted_path)
    seen = y2[target][0]
    base_first = yf[target][0]
    others_moved = sum(1 for k in yf
                       if k != target and yf[k] != y2.get(k))
    plant_ctrl = {"passed": abs(seen - PLANT_VALUE) < 1e-9 and others_moved == 0,
                  "patch": target, "face_index": 0, "planted": PLANT_VALUE,
                  "read_back": seen, "value_before_plant": base_first,
                  "other_patches_moved": others_moved,
                  "artifact": planted_path}
    if not plant_ctrl["passed"]:
        print(json.dumps({"REFUSED": "PLANT control failed",
                          "plant_control": plant_ctrl}, indent=1),
              file=sys.stderr)
        return 2

    out = {"instrument": os.path.relpath(os.path.abspath(__file__), _ROOT),
           "case": a.case, "time": a.time,
           "mesh_is_symlink_to": (os.path.realpath(mesh)
                                  if os.path.islink(mesh) else None),
           "gate_Y1_registered_statistic":
               "AREA-WEIGHTED MEDIAN y+ over LAYERED VEHICLE WALL FACES, "
               "band [30,300] (DRIVAER_R2_LAYERED_PREREGISTRATION.md, Gate Y1)",
           "gate_Y1_NOT_DECIDED_HERE":
               "the layered/unlayered classification for this level is a "
               "separate measurement and is not invented by this module",
           "controls": {"area_closure": area_ctrl,
                        "count": {"passed": True, "n_patches": len(per)},
                        "plant": plant_ctrl},
           "per_patch": sorted(per, key=lambda r: -r["area_m2"])}
    dump = os.path.splitext(a.report)[0] + "_FACES.csv"
    with open(dump, "w") as fh:
        fh.write("patch,yplus,area_m2\n")
        for n, v, w in face_rows:
            fh.write("%s,%.10g,%.10g\n" % (n, v, w))
    out["face_level_dump"] = dump
    out["n_faces_dumped"] = len(face_rows)

    if a.groups:
        groups = json.load(open(a.groups))
        assigned = {}
        for gname, plist in groups.items():
            for pn in plist:
                if pn in assigned:
                    raise YPlusReaderBlind(
                        "patch %r assigned to both %r and %r; a face cannot be "
                        "in two groups and the statistic would double-count."
                        % (pn, assigned[pn], gname))
                assigned[pn] = gname
        known = set(r["patch"] for r in per)
        missing = sorted(p for p in assigned if p not in known)
        if missing:
            raise YPlusReaderBlind(
                "grouping names patches absent from this mesh/field: %s. "
                "REFUSING rather than silently grouping a subset." % missing)
        gs = {}
        for gname in groups:
            sel = [(v, w) for n, v, w in face_rows if assigned.get(n) == gname]
            if not sel:
                raise YPlusReaderBlind("group %r selected no face." % gname)
            vv = [x[0] for x in sel]
            ww = [x[1] for x in sel]
            A = sum(ww)
            gs[gname] = {"n_patches": sum(1 for p in assigned
                                          if assigned[p] == gname),
                         "n_faces": len(sel), "area_m2": A,
                         "yplus_area_weighted_median_OVER_FACES":
                             wmedian(vv, ww),
                         "yplus_area_weighted_mean":
                             sum(v * w for v, w in sel) / A,
                         "yplus_min": min(vv), "yplus_max": max(vv)}
        out["groups"] = gs
        out["ungrouped_patches"] = sorted(known - set(assigned))

    with open(a.report, "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "per_patch"}, indent=1))
    print("per_patch rows: %d -> %s" % (len(per), a.report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
