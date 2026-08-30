#!/usr/bin/env python3
"""
F23b -- READERS AND WRITERS.  Two families, both used from disk only.

  (1) OpenFOAM ascii volVectorField / volScalarField.  Lineage
      cases/F23_HP_WEDGE/foam_io_f23.py, carried forward with ONE change: the
      internalField list is parsed by a VECTORISED tokeniser instead of one
      regex match per entry.  The change is a speed change and nothing else, and
      it is not taken on trust -- grade_f23b.py's control
      `control_fast_parser_agrees_with_the_F23_reference_parser` reads a REAL
      solver-written file with BOTH parsers and requires the arrays to be
      BIT-IDENTICAL, and requires the reference parser to be importable so the
      comparison cannot silently become a self-comparison.

  (2) `constant/polyMesh` -- points, a face range, the boundary file, the
      OpenFOAM face-area-vector construction, and G-WEDGE's limb-1 reading.
      This is the input the wedge guard grades (prereg section 4.3), so it is a
      PHYSICS_CRITICAL reader and it carries its own plant
      (`plant_points_z_into_copy`).

WHY LIMB 1 NEVER CALLS `acos` (prereg section 4.2, MEASURED).  `wedgePolyPatch`
stores `cosAngle_ = centreNormal_ & n_` with `n_` the ARITHMETIC MEAN of the unit
face normals, NEVER RENORMALISED.  Summing N nearly-identical unit vectors
accumulates rounding, so |n_bar| lands below 1, and `d(acos)/dc = -1/sin(a) =
-1432` turns that deficit into an angle.  F23 died on a FIXED ABSOLUTE tolerance
over that quantity.  `wedge_limb1` instead takes the angle of EVERY FACE to the
cardinal normal in the well-conditioned form `atan2(hypot(n_x, n_y), |n_z|)`,
which never evaluates `acos` near 1 and is a per-face maximum -- order
independent, so no summation error can enter it at all.

`checkmesh_cos_angle` is the OTHER thing: a faithful reimplementation of what
`wedgePolyPatch` computes and `checkMesh` prints, SEQUENTIAL SUMMATION INCLUDED
(`numpy.add.accumulate`, which accumulates left to right; `numpy.sum` uses
pairwise summation and would be MORE accurate than OpenFOAM and so would NOT
reproduce it).  It is a PROVENANCE control -- it proves this module is reading
the same geometry the mesher wrote -- and it is NOT the gating path.  Limb 2
reads checkMesh's own printed number out of the level's own `log.checkMesh`,
which is ONE NAMED ARTIFACT.

Refusals are `raise`; zero `assert` (L-332).  This module carries a HARD `-O`
REFUSAL AT IMPORT even though it is a library and has no gate of its own: cfd
measured that asserts, refusals, planted controls and gates all vanish under -O,
and a library that imports cleanly under -O is the hole every module above it
would fall through.  `python3 -O foam_io_f23b.py` exits 2, and so does any
importer.
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: foam_io_f23b.py must not be imported or run under `python3 -O` "
                     "(L-332); every reader above it depends on refusals -O would blind.\n")
    sys.exit(2)

import math
import os
import re

import numpy as np

_NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"


class FieldFormatError(Exception):
    pass


def _strip_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//[^\n]*", "", text)
    return text


def _parse_list(text, start, kind):
    """Parse `N ( ... )` beginning at text[start:], kind in ('vector','scalar').
    Returns (ndarray, end_index).  Entry-at-a-time; used for the small patch
    value lists, where the per-entry regex is not a cost."""
    m = re.compile(r"\s*(\d+)\s*\(", re.S).match(text, start)
    if not m:
        raise FieldFormatError("expected `N (` at offset %d" % start)
    n = int(m.group(1))
    pos = m.end()
    if kind == "vector":
        pat = re.compile(r"\s*\(\s*(%s)\s+(%s)\s+(%s)\s*\)" % (_NUM, _NUM, _NUM))
        out = np.empty((n, 3))
        for k in range(n):
            mm = pat.match(text, pos)
            if not mm:
                raise FieldFormatError("vector list: bad entry %d of %d" % (k, n))
            out[k] = (float(mm.group(1)), float(mm.group(2)), float(mm.group(3)))
            pos = mm.end()
    else:
        pat = re.compile(r"\s*(%s)" % _NUM)
        out = np.empty(n)
        for k in range(n):
            mm = pat.match(text, pos)
            if not mm:
                raise FieldFormatError("scalar list: bad entry %d of %d" % (k, n))
            out[k] = float(mm.group(1))
            pos = mm.end()
    mm = re.compile(r"\s*\)").match(text, pos)
    if not mm:
        raise FieldFormatError("list of %d entries not closed" % n)
    return out, mm.end()


def _parse_list_fast(text, start, kind):
    """The same list, tokenised in one pass.  `text` must END at or before the
    list's own closing paren -- callers hand it the slice before
    `boundaryField`, which every OpenFOAM field file places after the
    internalField.  Refuses on any count mismatch: a tokeniser that silently
    returns the wrong number of values is worse than one that fails."""
    m = re.compile(r"\s*(\d+)\s*\(", re.S).match(text, start)
    if not m:
        raise FieldFormatError("expected `N (` at offset %d" % start)
    n = int(m.group(1))
    body = text[m.end():]
    end = body.rfind(")")
    if end < 0:
        raise FieldFormatError("list of %d entries not closed" % n)
    toks = body[:end].replace("(", " ").replace(")", " ").split()
    per = 3 if kind == "vector" else 1
    if len(toks) != per * n:
        raise FieldFormatError("list of %d %ss carries %d numbers, expected %d"
                               % (n, kind, len(toks), per * n))
    arr = np.array(toks, dtype=float)
    return (arr.reshape(n, 3) if kind == "vector" else arr), m.end() + end + 1


def read_field(path, _reference_parser=False):
    """Return dict(kind, internal=ndarray, patches={name: ndarray|None}).

    `_reference_parser=True` forces the entry-at-a-time path -- the control in
    grade_f23b.py drives BOTH on the same real file and requires bit equality."""
    text = _strip_comments(open(path).read())
    m = re.search(r"class\s+(volVectorField|volScalarField)\s*;", text)
    if not m:
        raise FieldFormatError("%s: no volVectorField/volScalarField class" % path)
    kind = "vector" if m.group(1) == "volVectorField" else "scalar"
    bidx = text.find("boundaryField")
    head = text if bidx < 0 else text[:bidx]
    m = re.search(r"internalField\s+nonuniform\s+List<(vector|scalar)>", head)
    if not m:
        mu = re.search(r"internalField\s+uniform\s+", head)
        if not mu:
            raise FieldFormatError("%s: no internalField" % path)
        internal, uniform = None, True
    else:
        if _reference_parser:
            internal, _pos = _parse_list(head, m.end(), kind)
        else:
            internal, _pos = _parse_list_fast(head, m.end(), kind)
        uniform = False
    patches = {}
    if bidx >= 0:
        body = text[bidx + len("boundaryField"):]
        for pm in re.finditer(r"(\w+)\s*\{([^{}]*)\}", body):
            name, inner = pm.group(1), pm.group(2)
            mv = re.search(r"value\s+nonuniform\s+List<(vector|scalar)>", inner)
            if mv:
                arr, _ = _parse_list(inner, mv.end(), kind)
                patches[name] = arr
            else:
                patches[name] = None
    return dict(kind=kind, internal=internal, uniform=uniform, patches=patches, path=path)


def fmt_list(arr, kind):
    if kind == "vector":
        body = "\n".join("(%.17g %.17g %.17g)" % tuple(r) for r in arr)
    else:
        body = "\n".join("%.17g" % v for v in arr)
    return "%d\n(\n%s\n)" % (len(arr), body)


def write_from_template(template_path, out_path, replacements):
    text = open(template_path).read()
    for key, val in replacements.items():
        if key not in text:
            raise FieldFormatError("template %s lacks placeholder %s" % (template_path, key))
        text = text.replace(key, val)
    if "__" in re.sub(r"//[^\n]*", "", text):
        raise FieldFormatError("template %s still carries an unfilled placeholder" % template_path)
    open(out_path, "w").write(text)


def plant_into_vector_file(src, dst, comp, delta):
    """Copy an ascii volVectorField file adding `delta` to component `comp` of
    EVERY internalField entry, rewriting only that list.  Returns rows changed."""
    text = open(src).read()
    m = re.search(r"internalField\s+nonuniform\s+List<vector>\s*(\d+)\s*\(", text)
    if not m:
        raise FieldFormatError("%s: no nonuniform vector internalField to plant into" % src)
    n = int(m.group(1))
    pos = m.end()
    pat = re.compile(r"\s*\(\s*(%s)\s+(%s)\s+(%s)\s*\)" % (_NUM, _NUM, _NUM))
    pieces = [text[:pos]]
    for k in range(n):
        mm = pat.match(text, pos)
        if not mm:
            raise FieldFormatError("plant: bad entry %d" % k)
        vals = [float(mm.group(1)), float(mm.group(2)), float(mm.group(3))]
        vals[comp] += delta
        pieces.append("\n(%.17g %.17g %.17g)" % tuple(vals))
        pos = mm.end()
    pieces.append(text[pos:])
    open(dst, "w").write("".join(pieces))
    return n


def plant_into_scalar_file(src, dst, delta):
    """Copy an ascii volScalarField file adding `delta` to EVERY internalField
    entry, rewriting only that list.  Returns rows changed."""
    text = open(src).read()
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*(\d+)\s*\(", text)
    if not m:
        raise FieldFormatError("%s: no nonuniform scalar internalField to plant into" % src)
    n = int(m.group(1))
    pos = m.end()
    pat = re.compile(r"\s*(%s)" % _NUM)
    pieces = [text[:pos]]
    for k in range(n):
        mm = pat.match(text, pos)
        if not mm:
            raise FieldFormatError("plant: bad entry %d" % k)
        pieces.append("\n%.17g" % (float(mm.group(1)) + delta))
        pos = mm.end()
    pieces.append(text[pos:])
    open(dst, "w").write("".join(pieces))
    return n


# ---------------------------------------------------------------------------
# constant/polyMesh -- G-WEDGE's input (PHYSICS_CRITICAL, prereg section 7)
# ---------------------------------------------------------------------------
_LIST_OPEN = re.compile(rb"\s*(\d+)\s*\(", re.S)


def _foam_list_head(raw):
    """(N, index just after the `N (` that opens the top-level list)."""
    i = raw.find(b"// * * *")
    m = _LIST_OPEN.search(raw, raw.find(b"\n", i) if i >= 0 else 0)
    if not m:
        raise FieldFormatError("no `N (` list opener")
    return int(m.group(1)), m.end()


def read_points(path):
    """constant/polyMesh/points as an (N, 3) float64 array."""
    raw = open(path, "rb").read()
    n, pos = _foam_list_head(raw)
    end = raw.rfind(b")")
    if end <= pos:
        raise FieldFormatError("%s: point list not closed" % path)
    toks = raw[pos:end].replace(b"(", b" ").replace(b")", b" ").split()
    if len(toks) != 3 * n:
        raise FieldFormatError("%s: %d numbers for %d points" % (path, len(toks), n))
    return np.array(toks, dtype=float).reshape(n, 3)


def write_points(src_points_path, dst_points_path, P, precision=12):
    """Rewrite a points file with the SAME header and a new coordinate array, at
    the case's own `writePrecision` (12).  The plant that travels through this
    writer must survive it -- C-4 measures the round trip and refuses above
    1e-14 absolute."""
    raw = open(src_points_path, "rb").read()
    n, pos = _foam_list_head(raw)
    if P.shape != (n, 3):
        raise FieldFormatError("point array is %s, the file carries %d points" % (P.shape, n))
    fmt = "(%%.%dg %%.%dg %%.%dg)" % (precision, precision, precision)
    body = "\n".join(fmt % (P[i, 0], P[i, 1], P[i, 2]) for i in range(n))
    open(dst_points_path, "wb").write(raw[:pos] + b"\n" + body.encode() + b"\n)\n")


def read_boundary(path):
    """{patch: dict(type, nFaces, startFace)} from constant/polyMesh/boundary."""
    text = _strip_comments(open(path, errors="replace").read())
    out = {}
    for m in re.finditer(r"(\w+)\s*\{(.*?)\}", text, re.S):
        name, body = m.group(1), m.group(2)
        mt = re.search(r"type\s+(\w+)\s*;", body)
        mn = re.search(r"nFaces\s+(\d+)\s*;", body)
        ms = re.search(r"startFace\s+(\d+)\s*;", body)
        if mt and mn and ms:
            out[name] = dict(type=mt.group(1), nFaces=int(mn.group(1)), startFace=int(ms.group(1)))
    if not out:
        raise FieldFormatError("%s: no patches parsed" % path)
    return out


def read_face_range(path, start, count):
    """Faces [start, start+count) as (tri_index_array, quad_index_array).

    A wedge patch on this case carries triangles at the axis (blockMesh collapses
    the repeated axis vertices) and quadrilaterals everywhere else, so both
    shapes are real and both are returned.  Any other polygon count REFUSES
    rather than being dropped -- a face silently skipped is a face the guard
    never looked at."""
    raw = open(path, "rb").read()
    n, pos = _foam_list_head(raw)
    if start + count > n:
        raise FieldFormatError("%s: face range [%d, %d) beyond the %d faces present"
                               % (path, start, start + count, n))
    tri, quad = [], []
    idx = 0
    for m in re.compile(rb"(\d+)\s*\(([^)]*)\)").finditer(raw, pos):
        if idx >= start + count:
            break
        if idx >= start:
            k = int(m.group(1))
            v = m.group(2).split()
            if k == 3 and len(v) == 3:
                tri.append(v)
            elif k == 4 and len(v) == 4:
                quad.append(v)
            else:
                raise FieldFormatError("%s: face %d declares %d points and carries %d"
                                       % (path, idx, k, len(v)))
        idx += 1
    T = np.array(tri, dtype=np.int64).reshape(-1, 3)
    Q = np.array(quad, dtype=np.int64).reshape(-1, 4)
    if T.shape[0] + Q.shape[0] != count:
        raise FieldFormatError("%s: parsed %d faces of the %d requested"
                               % (path, T.shape[0] + Q.shape[0], count))
    return T, Q


def face_area_normals(P, T, Q):
    """OpenFOAM's `face::areaNormal`, vectorised, in its own operand order.

    A triangle is the direct 0.5 ((b-a) ^ (c-a)).  A polygon is the CENTRAL
    DECOMPOSITION: the centre point is the arithmetic mean of the face's points
    and the area vector is the sum over edges of `triPointRef(p[i], p[i+1],
    centre).areaNormal()`, the centre point last, exactly as OpenFOAM writes it.
    """
    out = []
    if T.shape[0]:
        a, b, c = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]
        out.append(0.5 * np.cross(b - a, c - a))
    if Q.shape[0]:
        p = [P[Q[:, k]] for k in range(4)]
        ctr = (((p[0] + p[1]) + p[2]) + p[3]) / 4.0
        n = None
        for k in range(4):
            t = 0.5 * np.cross(p[(k + 1) % 4] - p[k], ctr - p[k])
            n = t if n is None else n + t
        out.append(n)
    if not out:
        raise FieldFormatError("no faces to take an area normal of")
    return np.vstack(out)


def unit_face_normals(mesh_dir, patch):
    b = read_boundary(os.path.join(mesh_dir, "boundary"))
    if patch not in b:
        raise FieldFormatError("%s: no patch %r (present: %s)"
                               % (mesh_dir, patch, sorted(b)))
    spec = b[patch]
    if spec["nFaces"] <= 0:
        raise FieldFormatError("%s: patch %r carries no faces" % (mesh_dir, patch))
    P = read_points(os.path.join(mesh_dir, "points"))
    T, Q = read_face_range(os.path.join(mesh_dir, "faces"), spec["startFace"], spec["nFaces"])
    S = face_area_normals(P, T, Q)
    mag = np.sqrt((S * S).sum(axis=1))
    if np.any(mag <= 0.0):
        raise FieldFormatError("%s: patch %r has a zero-area face" % (mesh_dir, patch))
    return S / mag[:, None], spec


def wedge_limb1(mesh_dir, patch, half_angle_deg):
    """G-WEDGE LIMB 1 (prereg section 4.3), the PRIMARY, well-conditioned guard.

    For EVERY face of the patch, the angle to the componentwise-snapped cardinal
    normal as degrees(atan2(hypot(n_x, n_y), |n_z|)).  `acos` is never called.
    Returns the maximum over faces of |angle / HALF_ANGLE_DEG - 1|."""
    if half_angle_deg <= 0.0:
        raise FieldFormatError("half angle must be positive, got %r" % half_angle_deg)
    U, spec = unit_face_normals(mesh_dir, patch)
    ang = np.degrees(np.arctan2(np.hypot(U[:, 0], U[:, 1]), np.abs(U[:, 2])))
    rel = np.abs(ang / half_angle_deg - 1.0)
    return dict(patch=patch, n_faces=int(spec["nFaces"]), mesh_dir=mesh_dir,
                max_rel_dev=float(np.max(rel)), max_angle_deg=float(np.max(ang)),
                min_angle_deg=float(np.min(ang)),
                form="degrees(atan2(hypot(n_x, n_y), |n_z|)) per face; acos is never called")


def checkmesh_cos_angle(mesh_dir, patch):
    """PROVENANCE CONTROL, NOT THE GATE.  `wedgePolyPatch::calcGeometry`
    reproduced: the arithmetic mean of the unit face normals SUMMED
    SEQUENTIALLY, the componentwise-snapped `centreNormal_`, and
    `acos(centreNormal_ & n_)` -- the number `checkMesh` prints.

    `numpy.add.accumulate(...)[-1]` is used rather than `numpy.sum`, which is
    pairwise and therefore MORE accurate than the C++ loop; reproducing the
    mesher means reproducing its summation order too.
    """
    U, spec = unit_face_normals(mesh_dir, patch)
    N = U.shape[0]
    nbar = np.array([float(np.add.accumulate(U[:, k])[-1]) for k in range(3)]) / N
    cn = np.array([math.copysign(max(abs(v), 0.5) - 0.5, v) for v in nbar])
    m = math.sqrt(float(cn @ cn))
    if m <= 0.0:
        raise FieldFormatError("%s/%s: the snapped centre normal is null; this is not a wedge patch"
                               % (mesh_dir, patch))
    cn = cn / m
    cos_a = float(cn @ nbar)
    mag = math.sqrt(float(nbar @ nbar))
    return dict(patch=patch, n_faces=N, n_bar=nbar.tolist(), mag_n_bar=mag,
                one_minus_mag_n_bar=1.0 - mag, centre_normal=cn.tolist(), cos_angle=cos_a,
                angle_deg=math.degrees(math.acos(min(1.0, max(-1.0, cos_a)))))


def plant_points_z_into_copy(src_mesh_dir, dst_mesh_dir, p, precision=12):
    """Plant a MIS-BUILT WEDGE by scaling every point's z by (1 + p) -- which is
    exactly a wedge built at half angle a(1 + p) -- into a COPY, and read the
    copy back through the real reader.  Nothing is written into any run root.

    Returns the round-trip max |dz| through the file format: a plant that cannot
    survive its own file format is not a plant (C-4)."""
    if os.path.realpath(src_mesh_dir) == os.path.realpath(dst_mesh_dir):
        raise FieldFormatError("the plant destination is the source; the control never writes "
                               "into a real mesh")
    os.makedirs(dst_mesh_dir, exist_ok=True)
    for f in ("faces", "boundary"):
        s = os.path.join(src_mesh_dir, f)
        if not os.path.isfile(s):
            raise FieldFormatError("no %s under %s" % (f, src_mesh_dir))
        open(os.path.join(dst_mesh_dir, f), "wb").write(open(s, "rb").read())
    P = read_points(os.path.join(src_mesh_dir, "points"))
    want = P.copy()
    want[:, 2] = P[:, 2] * (1.0 + p)
    write_points(os.path.join(src_mesh_dir, "points"),
                 os.path.join(dst_mesh_dir, "points"), want, precision=precision)
    back = read_points(os.path.join(dst_mesh_dir, "points"))
    return float(np.max(np.abs(back[:, 2] - want[:, 2])))


CHECKMESH_WEDGE_RE = re.compile(r"Wedge (wedge[0-9]+) with angle ([0-9.eE+-]+) degrees")


def checkmesh_wedge_angles(log_path):
    """G-WEDGE LIMB 2's input: the angles `checkMesh` ITSELF printed, read from
    ONE NAMED ARTIFACT -- the level's own `log.checkMesh`.

    NEVER `grep ... log.* | tail -1`.  `grep` on this box is a shell function
    over ugrep, which searches files on PARALLEL WORKER THREADS, so the file
    order in a multi-file result is a race; `-J1` and `--sort` make it
    deterministic AND STILL WRONG, because `log.writeCellCentres` sorts last and
    its only `Time =` line is a zero.  One measurement, one named file."""
    if not os.path.isfile(log_path):
        raise FieldFormatError("no checkMesh log at %s" % log_path)
    text = open(log_path, errors="replace").read()
    hits = CHECKMESH_WEDGE_RE.findall(text)
    if not hits:
        raise FieldFormatError("%s carries no `Wedge <name> with angle <x> degrees` line" % log_path)
    return dict((nm, float(v)) for nm, v in hits)


def _selftest():
    """A library's own two-limb check: the vectorised list parser must AGREE
    BIT-FOR-BIT with the entry-at-a-time reference parser on REAL solver output
    written by OpenFOAM on this box, and must REFUSE a declared count that
    disagrees with the body.  Zero compute; read-only."""
    import shutil
    import tempfile
    repo = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    real = os.path.join(repo, "verification", "runs", "ansys_verification",
                        "VMFL019", "L1_30", "5", "U")
    if not os.path.isfile(real):
        sys.stderr.write("REFUSED: the real solver output the format is pinned against is absent: "
                         "%s\n" % real)
        return 2
    fast = read_field(real)["internal"]
    ref = read_field(real, _reference_parser=True)["internal"]
    same = bool(np.array_equal(fast, ref)) and fast.shape == (120, 3)
    tmp = tempfile.mkdtemp(prefix="f23b_io_")
    fired = False
    try:
        p = os.path.join(tmp, "U")
        open(p, "w").write(open(real).read().replace(
            "internalField   nonuniform List<vector> \n120",
            "internalField   nonuniform List<vector> \n119", 1))
        try:
            read_field(p)
        except FieldFormatError:
            fired = True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("  vectorised parser == entry-at-a-time reference parser, bit for bit   %s   (%s, %d vectors)"
          % ("ok" if same else "FAIL", os.path.relpath(real, repo), fast.shape[0]))
    print("  a declared count that disagrees with the body REFUSES                %s"
          % ("FIRED" if fired else "DID NOT FIRE -- IT IS MEASURING NOTHING"))
    if same and fired:
        print("SELFTEST OK: 1 control, driven BOTH ways, 0 failures.")
        return 0
    return 1


if __name__ == "__main__":
    import argparse
    _ap = argparse.ArgumentParser(description="F23b readers and writers")
    _ap.add_argument("--selftest", action="store_true")
    _a = _ap.parse_args()
    sys.exit(_selftest() if _a.selftest else 0)
