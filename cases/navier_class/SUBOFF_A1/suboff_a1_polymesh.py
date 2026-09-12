#!/usr/bin/env python3
"""
SUBOFF_A1 -- MINIMAL ASCII polyMesh READER, SHARED BY THE REFERENCE BUILDER AND
THE GRADER.

It exists for ONE measured number: the AREA of a named wall patch of a BUILT mesh,
which is Gate D2's `Aref` (SUBOFF_A1_PREREGISTRATION.md 5.3: "half-model => Aref =
analytic / 2, READ BACK FROM THE BUILT WALL PATCHES").

RULE 3.  `patch_area()` is exercised by `plant_and_verify()`, which WRITES a synthetic
ASCII polyMesh of EXACTLY KNOWN area to disk, READS IT BACK with the same function,
and REFUSES (exit 2) unless the returned area matches to 1e-12 relative.  The plant
carries a DECOY patch of a different area at startFace 0, so a reader that ignores
`startFace` fails the plant instead of passing it.  A zero or a wrong area from this
reader is therefore never mistaken for a property of the mesh.

MEMORY.  `faces` is 345 MB at L1 and ~1 GB at L2 in ASCII.  Only the BOUNDARY faces
(the tail of the list, from min(startFace)) are materialised; `points` is held as a
flat `array('d')`, not as tuples.  Peak stays a few hundred MB so that a build or a
solve belonging to another team is never pushed toward the OOM killer.

READ-ONLY ON THE GRADED TREE.  Nothing here writes into a case directory.

ZERO `assert` (L-332).
"""
import sys
if not __debug__:
    sys.stderr.write("REFUSED: must not run under python3 -O.\n"); sys.exit(2)
import os, re, math
from array import array

PLANT_AREA = 12.34500000            # m^2, the known-area plant (rule 3)
PLANT_TOL_REL = 1.0e-12


def _open_payload(path):
    """Open `path` positioned just past the FoamFile banner."""
    f = open(path, "r")
    for line in f:
        if line.startswith("// * * *"):
            return f
    f.close()
    sys.stderr.write(f"REFUSED: no FoamFile banner in {path}\n"); sys.exit(2)


def read_points(case):
    """Flat array('d') of length 3*nPoints."""
    f = _open_payload(os.path.join(case, "constant", "polyMesh", "points"))
    pts = array("d")
    started = False
    with f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            if not started:
                if s == "(":
                    started = True
                elif s.startswith("("):
                    started = True
                    s = s[1:]
                else:
                    continue            # the count line
                if not s or s == "(":
                    continue
            if s.startswith(")"):
                break
            for tok in s.replace("(", " ").replace(")", " ").split():
                pts.append(float(tok))
    if len(pts) == 0 or len(pts) % 3 != 0:
        sys.stderr.write("REFUSED: points payload empty or not a multiple of 3.\n")
        sys.exit(2)
    return pts


_FACE_RE = re.compile(r"(\d+)\s*\(([^)]*)\)")


def read_faces_from(case, first):
    """Faces with global index >= `first`, as a list of index tuples.  Faces before
    `first` are counted and discarded, never materialised."""
    f = _open_payload(os.path.join(case, "constant", "polyMesh", "faces"))
    out, n = [], -1          # n counts faces seen; -1 until the opening '('
    with f:
        for line in f:
            s = line.strip()
            if n < 0:
                if s == "(" or s.startswith("("):
                    n = 0
                continue
            if s.startswith(")"):
                break
            for m in _FACE_RE.finditer(s):
                idx = m.group(2).split()
                if len(idx) != int(m.group(1)):
                    sys.stderr.write("REFUSED: face vertex count disagrees with its "
                                     "label.\n"); sys.exit(2)
                if n >= first:
                    out.append(tuple(int(v) for v in idx))
                n += 1
    if n <= 0:
        sys.stderr.write("REFUSED: faces list parsed to zero faces.\n"); sys.exit(2)
    return out, n


def read_boundary(case):
    """{patchName: {'nFaces': n, 'startFace': s, 'type': t}}"""
    f = _open_payload(os.path.join(case, "constant", "polyMesh", "boundary"))
    with f:
        inner = f.read()
    i = inner.find("(")
    j = inner.rfind(")")
    out = {}
    for m in re.finditer(r"(\w+)\s*\{([^}]*)\}", inner[i + 1:j]):
        name, blk = m.group(1), m.group(2)
        nf = re.search(r"nFaces\s+(\d+)\s*;", blk)
        sf = re.search(r"startFace\s+(\d+)\s*;", blk)
        ty = re.search(r"type\s+(\w+)\s*;", blk)
        if nf and sf:
            out[name] = {"nFaces": int(nf.group(1)), "startFace": int(sf.group(1)),
                         "type": ty.group(1) if ty else "?"}
    if not out:
        sys.stderr.write("REFUSED: boundary parsed to zero patches.\n"); sys.exit(2)
    return out


def _face_area(pts, f):
    """Magnitude of the polygon area vector, OpenFOAM's fan-about-centroid form."""
    n = len(f)
    if n < 3:
        return 0.0
    cx = cy = cz = 0.0
    for v in f:
        cx += pts[3 * v]; cy += pts[3 * v + 1]; cz += pts[3 * v + 2]
    cx /= n; cy /= n; cz /= n
    ax = ay = az = 0.0
    for k in range(n):
        p = f[k]; q = f[(k + 1) % n]
        ux, uy, uz = pts[3 * p] - cx, pts[3 * p + 1] - cy, pts[3 * p + 2] - cz
        vx, vy, vz = pts[3 * q] - cx, pts[3 * q + 1] - cy, pts[3 * q + 2] - cz
        ax += uy * vz - uz * vy
        ay += uz * vx - ux * vz
        az += ux * vy - uy * vx
    return 0.5 * math.sqrt(ax * ax + ay * ay + az * az)


_CACHE = {}


def _load(case, patches):
    key = os.path.abspath(case)
    if key in _CACHE:
        return _CACHE[key]
    bnd = read_boundary(case)
    want = [p for p in patches if p in bnd] or list(bnd)
    first = min(bnd[p]["startFace"] for p in want)
    faces, nfaces = read_faces_from(case, first)
    pts = read_points(case)
    _CACHE[key] = (pts, faces, first, nfaces, bnd)
    return _CACHE[key]


def patch_area(case, patch, patches=()):
    """THE GRADED FUNCTION.  Area [m^2] of one boundary patch of a built mesh."""
    pts, faces, first, nfaces, bnd = _load(case, tuple(patches) or (patch,))
    if patch not in bnd:
        sys.stderr.write(f"REFUSED: patch '{patch}' absent from {case}.\n"); sys.exit(2)
    s, n = bnd[patch]["startFace"], bnd[patch]["nFaces"]
    if n <= 0:
        sys.stderr.write(f"REFUSED: patch '{patch}' has nFaces={n}.\n"); sys.exit(2)
    if s < first:
        sys.stderr.write(f"REFUSED: patch '{patch}' starts at {s}, before the loaded "
                         f"window {first}.\n"); sys.exit(2)
    if s - first + n > len(faces):
        sys.stderr.write(f"REFUSED: patch '{patch}' runs past the loaded faces.\n")
        sys.exit(2)
    return sum(_face_area(pts, faces[k - first]) for k in range(s, s + n))


_HDR = ("FoamFile\n{{\n    version 2.0;\n    format ascii;\n    class {cls};\n"
        "    object {obj};\n}}\n"
        "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n")


def plant_and_verify(scratch_dir):
    """RULE 3.  Write a synthetic polyMesh of EXACTLY `PLANT_AREA` to disk, read it
    back with `patch_area`, and REFUSE (exit 2) if the reader cannot see it.
    Returns the dict that goes verbatim into the record."""
    case = os.path.join(scratch_dir, "RULE3_PLANT")
    d = os.path.join(case, "constant", "polyMesh")
    os.makedirs(d, exist_ok=True)
    a = math.sqrt(PLANT_AREA)                    # unit-area side
    b = math.sqrt(0.5 * PLANT_AREA)              # DECOY of a DIFFERENT area
    P = [(0, 0, 0), (a, 0, 0), (a, a, 0), (0, a, 0),
         (0, 0, 1), (b, 0, 1), (b, b, 1), (0, b, 1)]
    with open(os.path.join(d, "points"), "w") as f:
        f.write(_HDR.format(cls="vectorField", obj="points"))
        f.write(f"{len(P)}\n(\n")
        for p in P:
            f.write(f"({p[0]:.17g} {p[1]:.17g} {p[2]:.17g})\n")
        f.write(")\n")
    # face 0 is the DECOY (half the planted area) at startFace 0; face 1 is PLANTED.
    # A reader that ignores startFace reads the decoy and FAILS the plant.
    F = [(4, 5, 6, 7), (0, 3, 2, 1)]
    with open(os.path.join(d, "faces"), "w") as f:
        f.write(_HDR.format(cls="faceList", obj="faces"))
        f.write(f"{len(F)}\n(\n")
        for fc in F:
            f.write(f"{len(fc)}({' '.join(str(v) for v in fc)})\n")
        f.write(")\n")
    with open(os.path.join(d, "boundary"), "w") as f:
        f.write(_HDR.format(cls="polyBoundaryMesh", obj="boundary"))
        f.write("2\n(\n"
                "    decoy { type wall; nFaces 1; startFace 0; }\n"
                "    PLANTED { type wall; nFaces 1; startFace 1; }\n"
                ")\n")
    _CACHE.pop(os.path.abspath(case), None)
    got = patch_area(case, "PLANTED", patches=("decoy", "PLANTED"))
    rel = abs(got - PLANT_AREA) / PLANT_AREA
    if rel > PLANT_TOL_REL:
        sys.stderr.write("REFUSED (rule 3): the patch-area reader could not see the "
                         f"planted {PLANT_AREA} m^2; it returned {got!r} "
                         f"(rel err {rel:.3e}).  A zero or a number from this reader "
                         "is NOT evidence.\n")
        sys.exit(2)
    return {"PLANT_AREA_m2": PLANT_AREA, "returned_m2": got, "decoy_area_m2": b * b,
            "rel_err": rel, "tol_rel": PLANT_TOL_REL, "verdict": "ARMED"}


if __name__ == "__main__":
    import json
    sd = sys.argv[1] if len(sys.argv) > 1 else "."
    print(json.dumps(plant_and_verify(sd), indent=2))
