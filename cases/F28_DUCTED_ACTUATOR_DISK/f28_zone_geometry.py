#!/usr/bin/env python3
"""F28 -- ZONE GEOMETRY READER for the H5 spatial-residual localisation gate.

WHAT THIS IS FOR.  The H5 arm (see
`verification/campaign/F28G_H5_RESIDUAL_FIELD_PILOT_AND_ARM_PREREGISTRATION.md`)
gates on WHERE the cell-wise gating residual lives.  A location gate is only a
gate if its zones are frozen BEFORE the run, in coordinates a later reader can
check.  This script produces those coordinates from the mesh that will actually
be used -- the graded rung's OWN `constant/polyMesh`, 35,544 cells -- and its
output is quoted into the frozen registration.

IT IS A READER.  It launches nothing, writes nothing into any run directory,
and takes no verdict.  It reads `points`, `faces` and `boundary` and prints
per-patch bounding boxes in the wedge (x, r) plane, plus the near-axis cell
scale.

COORDINATES.  The case is an axisymmetric WEDGE about the x axis.  `y` is the
radial direction in the wedge mid-plane and `z` is the small out-of-plane
offset (domain |z| <= 0.1635727 at the outer radius).  The radius used
throughout is r = sqrt(y^2 + z^2), NOT y, because the wedge faces are rotated
+/-2.5 degrees out of plane and a y-only reading understates r by cos(2.5 deg)
on the wedge patches.

STANDING RULE 3 -- PLANTED CONTROL.  A geometry reader that silently reads
nothing would print a plausible-looking empty answer.  `--selftest` builds a
tiny synthetic polyMesh with KNOWN patch extents, reads it back through the
same code path, and REFUSES (exit 2) unless the known extents come back.  It
also runs a negative limb: a patch whose faces are removed must NOT report a
bounding box.  Run `--selftest` on any edit to this file.
"""

import math
import os
import re
import sys
import tempfile

HEADER_END = re.compile(r"^// \* \* \*")


def _strip_header(text):
    """Return the body of a FoamFile, after the banner and the FoamFile dict."""
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if HEADER_END.match(ln):
            return "\n".join(lines[i + 1:])
    return text


def read_points(path):
    body = _strip_header(open(path).read())
    # body: <count> \n ( \n (x y z) ... ) \n
    m = re.search(r"(\d+)\s*\(", body)
    if not m:
        raise RuntimeError("points: no count/open-paren found in %s" % path)
    n = int(m.group(1))
    pts = re.findall(r"\(([^()]*)\)", body[m.end() - 1:])
    if len(pts) < n:
        raise RuntimeError("points: expected %d, parsed %d" % (n, len(pts)))
    out = []
    for s in pts[:n]:
        a, b, c = s.split()
        out.append((float(a), float(b), float(c)))
    return out


def read_faces(path):
    body = _strip_header(open(path).read())
    m = re.search(r"(\d+)\s*\(", body)
    if not m:
        raise RuntimeError("faces: no count/open-paren found in %s" % path)
    n = int(m.group(1))
    rest = body[m.end():]
    # Each face is  k(p0 p1 ... pk-1)
    faces = re.findall(r"\d+\(([^()]*)\)", rest)
    if len(faces) < n:
        raise RuntimeError("faces: expected %d, parsed %d" % (n, len(faces)))
    return [[int(t) for t in s.split()] for s in faces[:n]]


def read_boundary(path):
    """Return [(name, nFaces, startFace), ...] in file order."""
    body = _strip_header(open(path).read())
    out = []
    for m in re.finditer(
        r"(\w+)\s*\{([^{}]*)\}", body
    ):
        name, blk = m.group(1), m.group(2)
        nf = re.search(r"nFaces\s+(\d+)\s*;", blk)
        sf = re.search(r"startFace\s+(\d+)\s*;", blk)
        if nf and sf:
            out.append((name, int(nf.group(1)), int(sf.group(1))))
    return out


def radius(p):
    return math.sqrt(p[1] * p[1] + p[2] * p[2])


def patch_bbox(points, faces, nFaces, startFace):
    """(xmin, xmax, rmin, rmax) over the points of a patch's faces, or None."""
    if nFaces == 0:
        return None
    xs, rs = [], []
    for f in range(startFace, startFace + nFaces):
        for ip in faces[f]:
            p = points[ip]
            xs.append(p[0])
            rs.append(radius(p))
    return (min(xs), max(xs), min(rs), max(rs))


def report(case):
    pm = os.path.join(case, "constant", "polyMesh")
    points = read_points(os.path.join(pm, "points"))
    faces = read_faces(os.path.join(pm, "faces"))
    bnd = read_boundary(os.path.join(pm, "boundary"))

    rows = []
    for name, nf, sf in bnd:
        rows.append((name, nf, patch_bbox(points, faces, nf, sf)))

    # Near-axis scale: the smallest strictly-positive point radius in the mesh.
    pos = sorted(r for r in (radius(p) for p in points) if r > 1e-12)
    return points, faces, bnd, rows, pos


def selftest():
    """Plant a mesh with KNOWN patch extents; refuse unless both limbs fire."""
    d = tempfile.mkdtemp(prefix="f28zone_")
    pm = os.path.join(d, "constant", "polyMesh")
    os.makedirs(pm)
    hdr = "FoamFile{version 2.0;format ascii;}\n// * * *\n"

    # Eight points of a unit box, x in [0,1], y in [0,2], z = 0.
    pts = [(0, 0, 0), (1, 0, 0), (1, 2, 0), (0, 2, 0),
           (0, 0, 1), (1, 0, 1), (1, 2, 1), (0, 2, 1)]
    open(os.path.join(pm, "points"), "w").write(
        hdr + "%d\n(\n" % len(pts)
        + "\n".join("(%g %g %g)" % p for p in pts) + "\n)\n")

    # Two faces.  Face 0 is the PLANT: its four points span x [0,1], r [0,2].
    fcs = [[0, 1, 2, 3], [4, 5, 6, 7]]
    open(os.path.join(pm, "faces"), "w").write(
        hdr + "%d\n(\n" % len(fcs)
        + "\n".join("%d(%s)" % (len(f), " ".join(map(str, f))) for f in fcs)
        + "\n)\n")

    def write_boundary(n_plant):
        open(os.path.join(pm, "boundary"), "w").write(
            hdr + "2\n(\n"
            "    plantPatch { type patch; nFaces %d; startFace 0; }\n"
            "    emptyPatch { type empty; nFaces 0; startFace 2; }\n"
            ")\n" % n_plant)

    # POSITIVE LIMB: the plant patch has one face and MUST report its extents.
    write_boundary(1)
    _, _, _, rows, pos = report(d)
    got = dict((r[0], r[2]) for r in rows)
    want = (0.0, 1.0, 0.0, 2.0)
    if got.get("plantPatch") is None:
        print("SELFTEST REFUSED: positive limb read no bounding box for the "
              "planted patch -- the reader cannot see a patch that is there.")
        return 2
    if tuple(round(v, 9) for v in got["plantPatch"]) != want:
        print("SELFTEST REFUSED: positive limb read %r, planted %r."
              % (got["plantPatch"], want))
        return 2
    # The empty patch must NOT report a box even on the positive limb.
    if got.get("emptyPatch") is not None:
        print("SELFTEST REFUSED: a 0-face patch reported a bounding box %r."
              % (got["emptyPatch"],))
        return 2
    # And the near-axis scale must skip the four r=0 points and return the
    # smallest strictly-positive radius.  In the plant that is 1.0, from the
    # points (0,0,1) and (1,0,1), whose radius is carried ENTIRELY by z.
    # This value is the negative control on the radius formula itself: a
    # reader that used r = |y| would report 2.0 here, so an assertion of 1.0
    # fails loudly if the z term is ever dropped.  (Recorded because the first
    # draft of this selftest asserted 2.0 and the reader correctly refused it.)
    if not pos or abs(min(pos) - 1.0) > 1e-9:
        print("SELFTEST REFUSED: near-axis limb read %r, expected min 1.0 "
              "(radius carried by z); a reading of 2.0 means r = |y|."
              % (pos[:3] if pos else None))
        return 2

    # NEGATIVE LIMB: remove the plant's faces; the box must go away.
    write_boundary(0)
    _, _, _, rows2, _ = report(d)
    got2 = dict((r[0], r[2]) for r in rows2)
    if got2.get("plantPatch") is not None:
        print("SELFTEST REFUSED: negative limb still reported %r after the "
              "planted faces were removed -- the reader is not reading."
              % (got2["plantPatch"],))
        return 2

    print("SELFTEST PASS: positive limb read the planted extents "
          "(x 0..1, r 0..2); negative limb went silent when the faces were "
          "removed; a 0-face patch reported nothing on either limb.")
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if len(argv) < 2:
        print(__doc__)
        print("usage: f28_zone_geometry.py <caseDir> | --selftest")
        return 1
    case = argv[1]
    points, faces, bnd, rows, pos = report(case)

    print("case            : %s" % case)
    print("points          : %d" % len(points))
    print("faces           : %d" % len(faces))
    print("radius          : r = sqrt(y^2 + z^2)  (wedge; z is the out-of-plane"
          " offset, NOT ignored)")
    print("")
    print("%-12s %7s  %12s %12s  %12s %12s"
          % ("patch", "nFaces", "x_min", "x_max", "r_min", "r_max"))
    for name, nf, bb in rows:
        if bb is None:
            print("%-12s %7d  %s" % (name, nf, "(no faces -- no bounding box)"))
        else:
            print("%-12s %7d  %12.7f %12.7f  %12.7f %12.7f"
                  % (name, nf, bb[0], bb[1], bb[2], bb[3]))
    print("")
    print("near-axis scale : smallest strictly-positive POINT radius in the "
          "mesh = %.9f" % pos[0])
    print("                  next three: %.9f %.9f %.9f"
          % (pos[1], pos[2], pos[3]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
