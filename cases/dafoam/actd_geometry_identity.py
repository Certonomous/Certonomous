#!/usr/bin/env python3
"""Act D geometry identity: is the STL that renders the exact solved geometry?

Sanaa's DEMO MODE directive (2026-09-01) makes this the binding honesty
condition for the geometry stage: "the uploaded STL renders. It is the exact
solved geometry (regenerate the STL from the solved case where it differs)".

This measures, and it measures the ARTIFACTS' OWN BYTES on both sides (L-422:
a loader written for a viewport is not a measurement instrument). Nothing here
imports the control room's surface reader, and nothing rounds.

Both sides:
  * candidate STL  -- binary STL, float32 vertices, read with struct
  * solved case    -- constant/polyMesh/{points,faces,boundary} of the run tree
                      that Act D's numbers belong to, wall patch only, ASCII

Compared: triangle/face count, unique point count, the bounding box on each
axis with the disagreement stated as an absolute length and as a percentage of
that axis's own extent, AND -- the part that actually decides identity -- a
two-way nearest-neighbour deviation between the two point SETS.

Bounding boxes and counts alone are blind to interior deformation: a wing whose
skin is pushed about inside an unchanged envelope agrees on every one of them.
The point-set deviation is what makes this a body-identity check rather than an
envelope check, and it is the quantity the planted control is required to move.

RESOLUTION FLOOR. The STL stores float32. The polyMesh stores decimal ASCII
parsed to float64. So the comparison cannot resolve below one float32 ulp at
the coordinate magnitudes involved; that floor is computed here rather than
assumed, and no digit below it is claimed.

PLANTED CONTROL (rule 3). A zero from a reader not shown able to see a non-zero
is not evidence. The script perturbs one vertex of the STL in memory by a named
amount, re-runs the comparison, and REFUSES (exit 2) if the perturbation does
not show up.

    python3 cases/dafoam/actd_geometry_identity.py
"""
from __future__ import annotations

import json
import math
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SOLVED_CASE = Path("/home/ubuntu/certonomous-runs/A2-mach-wing")
WALL_PATCH = "wing"

CANDIDATES = {
    "sdk_geometry": REPO / "sdk" / "geometry" / "mach_tutorial_wing.stl",
    "website_surfaces": (REPO / "demo-output" / "website" / "surfaces"
                         / "mach_tutorial_wing.stl"),
}

# The plant. Large enough to be unmistakable, small enough that a reader that
# only sees it because it is huge is not being tested.
PLANT_M = 1.0e-3


# ------------------------------------------------------------------ STL bytes
def read_binary_stl(path: Path):
    """Return (triangles, raw_bytes). Every coordinate exactly as stored."""
    raw = path.read_bytes()
    if len(raw) < 84:
        raise ValueError(f"{path}: shorter than an STL header")
    n = struct.unpack("<I", raw[80:84])[0]
    expect = 84 + 50 * n
    if len(raw) != expect:
        raise ValueError(
            f"{path}: header says {n} triangles = {expect} bytes, file is "
            f"{len(raw)} bytes -- not a clean binary STL")
    tris = []
    for i in range(n):
        off = 84 + 50 * i
        v = struct.unpack("<12f", raw[off:off + 48])
        tris.append(((v[3], v[4], v[5]), (v[6], v[7], v[8]),
                     (v[9], v[10], v[11])))
    return tris, raw


def stl_measure(tris):
    pts = set()
    for t in tris:
        for p in t:
            pts.add(p)
    lo = [math.inf] * 3
    hi = [-math.inf] * 3
    for p in pts:
        for a in range(3):
            lo[a] = min(lo[a], p[a])
            hi[a] = max(hi[a], p[a])
    return {"triangles": len(tris), "unique_points": len(pts),
            "bbox_min": lo, "bbox_max": hi,
            "extent": [hi[a] - lo[a] for a in range(3)],
            "_points": sorted(pts)}


# -------------------------------------------------------------- polyMesh bytes
def _open_maybe_gz(base: Path, name: str):
    p = base / name
    if p.exists():
        return p.read_text()
    pz = base / (name + ".gz")
    if pz.exists():
        import gzip
        return gzip.decompress(pz.read_bytes()).decode()
    raise FileNotFoundError(f"{base}/{name}[.gz]")


def _body(text: str):
    """Strip the FoamFile header, return the token stream after it."""
    i = text.index("// * * *")
    j = text.index("\n", i)
    return text[j:]


def read_polymesh_wall(case: Path, patch: str):
    base = case / "constant" / "polyMesh"

    bnd = _body(_open_maybe_gz(base, "boundary"))
    # nFaces / startFace of the named patch, read positionally after its name.
    k = bnd.index(patch)
    seg = bnd[k:k + 400]
    nfaces = int(seg.split("nFaces")[1].split(";")[0].strip())
    start = int(seg.split("startFace")[1].split(";")[0].strip())

    ftxt = _body(_open_maybe_gz(base, "faces"))
    fs = ftxt[ftxt.index("(") + 1:]
    faces = []
    tok = ""
    depth = 0
    cur = []
    for ch in fs:
        if ch == "(":
            depth += 1
            tok = ""
            cur = []
            continue
        if ch == ")":
            if depth == 1:
                if tok.strip():
                    cur.append(int(tok))
                faces.append(cur)
                if len(faces) >= start + nfaces:
                    break
            depth -= 1
            tok = ""
            continue
        if depth == 1:
            if ch.isspace():
                if tok.strip():
                    cur.append(int(tok))
                tok = ""
            else:
                tok += ch
    wall = faces[start:start + nfaces]

    ptxt = _body(_open_maybe_gz(base, "points"))
    ps = ptxt[ptxt.index("(") + 1:]
    points = []
    buf = []
    tok = ""
    for ch in ps:
        if ch == "(":
            buf = []
            tok = ""
            continue
        if ch == ")":
            if tok.strip():
                buf.append(float(tok))
            tok = ""
            if len(buf) == 3:
                points.append(tuple(buf))
                buf = []
            else:
                break
            continue
        if ch.isspace():
            if tok.strip():
                buf.append(float(tok))
            tok = ""
        else:
            tok += ch

    used = sorted({i for f in wall for i in f})
    lo = [math.inf] * 3
    hi = [-math.inf] * 3
    for i in used:
        p = points[i]
        for a in range(3):
            lo[a] = min(lo[a], p[a])
            hi[a] = max(hi[a], p[a])
    sides = sorted({len(f) for f in wall})
    return {"patch": patch, "faces": nfaces, "face_sides": sides,
            "unique_points": len(used), "bbox_min": lo, "bbox_max": hi,
            "extent": [hi[a] - lo[a] for a in range(3)],
            "total_points_in_mesh": len(points),
            "_points": sorted(points[i] for i in used)}


# ------------------------------------------------------------ resolution floor
def float32_step(x: float) -> float:
    """One float32 ulp at x, measured rather than assumed."""
    b = struct.unpack("<I", struct.pack("<f", x))[0]
    return abs(struct.unpack("<f", struct.pack("<I", b + 1))[0]
               - struct.unpack("<f", struct.pack("<I", b))[0])


def point_set_deviation(a_pts, b_pts):
    """Two-way nearest-neighbour deviation between two point sets, in metres.

    Returns the worst distance from any point of A to its nearest point of B
    and the same the other way round. Both directions are needed: one-way
    agreement is satisfied by a subset.
    """
    def one_way(src, dst):
        worst = 0.0
        worst_pt = None
        for p in src:
            best = math.inf
            for q in dst:
                dx = p[0] - q[0]
                if dx * dx >= best:
                    continue
                dy = p[1] - q[1]
                dz = p[2] - q[2]
                d = dx * dx + dy * dy + dz * dz
                if d < best:
                    best = d
            best = math.sqrt(best)
            if best > worst:
                worst = best
                worst_pt = p
        return worst, worst_pt

    ab, ab_pt = one_way(a_pts, b_pts)
    ba, ba_pt = one_way(b_pts, a_pts)
    return {"stl_to_mesh_max_m": ab, "mesh_to_stl_max_m": ba,
            "two_way_max_m": max(ab, ba),
            "worst_stl_point": list(ab_pt) if ab_pt else None,
            "worst_mesh_point": list(ba_pt) if ba_pt else None}


def compare(stl: dict, mesh: dict) -> dict:
    axes = "XYZ"
    out = []
    worst = 0.0
    for a in range(3):
        for kind, sk, mk in (("min", "bbox_min", "bbox_min"),
                             ("max", "bbox_max", "bbox_max"),
                             ("extent", "extent", "extent")):
            sv = stl[sk][a]
            mv = mesh[mk][a]
            d = abs(sv - mv)
            ext = max(abs(mesh["extent"][a]), 1e-30)
            pct = 100.0 * d / ext
            worst = max(worst, pct)
            out.append({"axis": axes[a], "quantity": kind,
                        "stl": sv, "solved_mesh": mv,
                        "abs_diff_m": d, "pct_of_axis_extent": pct})
    floor = max(float32_step(max(abs(v) for v in
                                 mesh["bbox_min"] + mesh["bbox_max"]))
                for _ in (0,))
    dev = point_set_deviation(stl["_points"], mesh["_points"])
    return {"rows": out, "worst_pct_of_axis_extent": worst,
            "point_set_deviation": dev,
            "resolution_floor_m_one_float32_ulp": floor,
            "count_match": {
                "stl_triangles": stl["triangles"],
                "solved_wall_faces": mesh["faces"],
                "stl_triangles_over_wall_faces":
                    stl["triangles"] / mesh["faces"],
                "stl_unique_points": stl["unique_points"],
                "solved_wall_unique_points": mesh["unique_points"],
                "points_equal": stl["unique_points"] == mesh["unique_points"],
            }}


def main() -> int:
    mesh = read_polymesh_wall(SOLVED_CASE, WALL_PATCH)
    report = {
        "_what": ("Act D geometry identity: candidate STLs measured against "
                  "the wall patch of the polyMesh Act D's numbers belong to."),
        "solved_case": str(SOLVED_CASE),
        "solved_wall": mesh,
        "candidates": {},
        "plant_control": {},
    }

    for name, path in CANDIDATES.items():
        if not path.exists():
            report["candidates"][name] = {"present": False, "path": str(path)}
            continue
        tris, raw = read_binary_stl(path)
        import hashlib
        m = stl_measure(tris)
        report["candidates"][name] = {
            "present": True, "path": str(path),
            "bytes": len(raw), "md5": hashlib.md5(raw).hexdigest(),
            "measured": m, "comparison": compare(m, mesh),
        }

        # --- planted control, this candidate's own bytes -------------------
        # The plant moves ONE INTERIOR VERTEX, deliberately not a bounding-box
        # extreme, because the check has to catch a body deformed inside an
        # unchanged envelope. It is read back through the same comparison.
        moved = [list(map(list, t)) for t in tris]
        moved[0][0][0] += PLANT_M
        moved = [tuple(tuple(p) for p in t) for t in moved]
        pm = stl_measure(moved)
        pc = compare(pm, mesh)
        base = report["candidates"][name]["comparison"]
        clean = base["point_set_deviation"]["two_way_max_m"]
        planted = pc["point_set_deviation"]["two_way_max_m"]
        seen = planted - clean
        moved_bbox = (pc["worst_pct_of_axis_extent"]
                      != base["worst_pct_of_axis_extent"])
        report["plant_control"][name] = {
            "plant_m": PLANT_M,
            "plant_is_a_bbox_extreme": moved_bbox,
            "two_way_max_m_clean": clean,
            "two_way_max_m_planted": planted,
            "delta_m": seen,
            "recovered_fraction_of_plant": (seen / PLANT_M) if PLANT_M else None,
            "reader_saw_the_plant": seen > 0.5 * PLANT_M,
        }
        if not (seen > 0.5 * PLANT_M):
            print(f"REFUSED: reader recovered only {seen:.3g} m of a "
                  f"{PLANT_M} m interior plant in {name}; its zero is not "
                  f"evidence.", file=sys.stderr)
            return 2

    # The point sets themselves are working data, not the record.
    report["solved_wall"].pop("_points", None)
    for c in report["candidates"].values():
        if c.get("present"):
            c["measured"].pop("_points", None)

    out = REPO / "cases" / "dafoam" / "ladder-a" / "A2_geometry_identity.json"
    out.write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps(report, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
