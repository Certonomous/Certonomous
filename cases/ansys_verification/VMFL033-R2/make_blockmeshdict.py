#!/usr/bin/env python3
"""VMFL033 blockMeshDict generator -- annular sector, VM2026R1 p.119 geometry.

r1 = 1 m (inner, stationary), r2 = 2 m (outer, Omega2 = 0.5 rad/s).
A SECTOR with ROTATIONAL CYCLIC sides: the exact solution is theta-invariant, so
the azimuthal direction carries no discretisation error and is held FIXED across
the grid triple; only the RADIAL direction is refined (r = 2).

NOTHING geometric is constructed downstream from nr/dr -- the comparator reads
every radius back from OpenFOAM's own C field.  This file only WRITES the mesh.
"""
import math, sys

R1, R2 = 1.0, 2.0
HALF_ANGLE_DEG = 10.0          # sector spans -10..+10 deg
NTHETA = 8                     # FIXED at every level (see docstring)
THICK = 0.1                    # z-thickness; frontAndBack are `empty` (2-D planar)

HDR = """/*--------------------------------*- C++ -*----------------------------------*\\
| VMFL033 -- Viscous Heating in an Annulus.  GENERATED, do not hand-edit.      |
\\*---------------------------------------------------------------------------*/
FoamFile { version 2.0; format ascii; class dictionary; object blockMeshDict; }
"""

def write(nr, path):
    a = math.radians(HALF_ANGLE_DEG)
    ca, sa = math.cos(a), math.sin(a)
    pts = []
    for z in (0.0, THICK):
        pts += [(R1*ca, -R1*sa, z), (R2*ca, -R2*sa, z),
                (R2*ca,  R2*sa, z), (R1*ca,  R1*sa, z)]
    # pts order: 0..3 at z=0, 4..7 at z=THICK  (0,4 inner -a ; 3,7 inner +a ; 1,5 outer -a ; 2,6 outer +a)
    body = [HDR, "scale 1;", "", "vertices", "("]
    for p in pts:
        body.append("    (%.15g %.15g %.15g)" % p)
    body += [");", "", "blocks", "(",
             "    hex (0 1 2 3 4 5 6 7) (%d %d 1) simpleGrading (1 1 1)" % (nr, NTHETA),
             ");", "", "edges", "("]
    body += ["    arc 0 3 (%.15g 0 0)" % R1,
             "    arc 1 2 (%.15g 0 0)" % R2,
             "    arc 4 7 (%.15g 0 %.15g)" % (R1, THICK),
             "    arc 5 6 (%.15g 0 %.15g)" % (R2, THICK),
             ");", "", "boundary", "("]
    body += ["    innerWall { type wall; faces ((0 4 7 3)); }",
             "    outerWall { type wall; faces ((1 2 6 5)); }",
             "    sideMinus",
             "    {",
             "        type cyclic; neighbourPatch sidePlus;",
             "        transform rotational; rotationAxis (0 0 1); rotationCentre (0 0 0);",
             "        faces ((0 1 5 4));",
             "    }",
             "    sidePlus",
             "    {",
             "        type cyclic; neighbourPatch sideMinus;",
             "        transform rotational; rotationAxis (0 0 1); rotationCentre (0 0 0);",
             "        faces ((3 7 6 2));",
             "    }",
             "    frontAndBack { type empty; faces ((0 3 2 1) (4 5 6 7)); }",
             ");", ""]
    open(path, "w").write("\n".join(body))

if __name__ == "__main__":
    write(int(sys.argv[1]), sys.argv[2])
    print("wrote %s with nr=%s, ntheta=%d" % (sys.argv[2], sys.argv[1], NTHETA))
