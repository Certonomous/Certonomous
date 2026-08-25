#!/usr/bin/env python3
"""VMFL023 -- emit system/blockMeshDict.template (2D O-grid around a cylinder).

Geometry from the manual (VMFL023, p.89): "Diameter of the cylinder = 2 m".
The manual states NO outer domain, so the outer radius is a DECLARED MODELLING
CHOICE, frozen in PREREGISTRATION.md line 7 and named as the principal risk on
line 9.

TOPOLOGY.  A full 360-degree O-grid in four 90-degree blocks.  Local block axes
are (radial, azimuthal, z) -- radial FIRST, because the naive (azimuthal, radial)
ordering is LEFT-handed here and blockMesh rejects it (checked by hand:
(v1-v0)x(v3-v0).(v4-v0) = -59 < 0 for the azimuthal-first form, +59 for this one).

PATCH FACE ORDERING is the blockMesh standard outward set for a hex (0..7):
    x-min (0 4 7 3)   x-max (1 2 6 5)
    y-min (0 1 5 4)   y-max (3 7 6 2)
    z-min (0 3 2 1)   z-max (4 5 6 7)
so x-min is the cylinder and x-max the far field.

REFINEMENT FAMILY -- EXACTLY NESTED, r = 2 BY CONSTRUCTION.  Identical scheme to
VMFL036: the radial grading is the FIXED continuous map
r(xi) = r_in + L*(K^xi - 1)/(K - 1), xi = i/N, K frozen, so the blockMesh total
expansion ratio at N cells is R(N) = K^((N-1)/N) and doubling N halves h EXACTLY.
Azimuthal is uniform, so it halves exactly too.
"""
import math
import sys

R_IN = 1.0        # cylinder radius; D = 2 m, manual p.89
R_OUT = 60.0      # 30 D -- DECLARED, see the pre-registration
THICK = 1.0       # 2D extrusion depth (empty direction); cancels out of St

def pt(r, deg, z):
    return (r * math.cos(math.radians(deg)), r * math.sin(math.radians(deg)), z)

V = []
for z in (0.0, THICK):
    for r in (R_IN, R_OUT):
        for deg in (0.0, 90.0, 180.0, 270.0):
            V.append((r, deg, z))
# index map: iz*8 + ir*4 + itheta
def vid(ir, ith, iz):
    return iz * 8 + ir * 4 + (ith % 4)

def f(v):
    return "(%.12g %.12g %.12g)" % v

L = []
L.append("""/*--------------------------------*- C++ -*----------------------------------*\\
| VMFL023 -- Oscillating Laminar Flow Around a Circular Cylinder.               |
| 2D O-grid, GENERATED FILE.  Emitted by make_blockmeshdict_template.py;        |
| __NT__, __NR__ and __RGRAD__ are substituted by run_vmfl023.sh.               |
| DO NOT HAND-EDIT.                                                             |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

scale   1;

vertices
(""")
for i, (r, deg, z) in enumerate(V):
    L.append("    %-34s // %2d  r=%g theta=%g z=%g" % (f(pt(r, deg, z)), i, r, deg, z))
L.append(");")
L.append("")
L.append("blocks")
L.append("(")
for k in range(4):
    a, b = k, (k + 1) % 4
    L.append("    hex (%d %d %d %d  %d %d %d %d) (__NR__ __NT__ 1) "
             "simpleGrading (__RGRAD__ 1 1)  // theta %d -> %d"
             % (vid(0, a, 0), vid(1, a, 0), vid(1, b, 0), vid(0, b, 0),
                vid(0, a, 1), vid(1, a, 1), vid(1, b, 1), vid(0, b, 1),
                90 * k, 90 * (k + 1)))
L.append(");")
L.append("")
L.append("edges")
L.append("(")
for iz, z in enumerate((0.0, THICK)):
    for ir, r in enumerate((R_IN, R_OUT)):
        for k in range(4):
            a, b = k, (k + 1) % 4
            L.append("    arc %-2d %-2d %s" % (vid(ir, a, iz), vid(ir, b, iz),
                                               f(pt(r, 90 * k + 45.0, z))))
L.append(");")
L.append("")
L.append("boundary")
L.append("(")
L.append("    cylinder")
L.append("    {")
L.append("        type wall;")
L.append("        faces")
L.append("        (")
for k in range(4):   # x-min (0 4 7 3)
    a, b = k, (k + 1) % 4
    L.append("            (%d %d %d %d)" % (vid(0, a, 0), vid(0, a, 1),
                                            vid(0, b, 1), vid(0, b, 0)))
L.append("        );")
L.append("    }")
L.append("    farField")
L.append("    {")
L.append("        type patch;")
L.append("        faces")
L.append("        (")
for k in range(4):   # x-max (1 2 6 5)
    a, b = k, (k + 1) % 4
    L.append("            (%d %d %d %d)" % (vid(1, a, 0), vid(1, b, 0),
                                            vid(1, b, 1), vid(1, a, 1)))
L.append("        );")
L.append("    }")
L.append("    frontAndBack")
L.append("    {")
L.append("        type empty;")
L.append("        faces")
L.append("        (")
for k in range(4):   # z-min (0 3 2 1) and z-max (4 5 6 7)
    a, b = k, (k + 1) % 4
    L.append("            (%d %d %d %d)" % (vid(0, a, 0), vid(0, b, 0),
                                            vid(1, b, 0), vid(1, a, 0)))
    L.append("            (%d %d %d %d)" % (vid(0, a, 1), vid(1, a, 1),
                                            vid(1, b, 1), vid(0, b, 1)))
L.append("        );")
L.append("    }")
L.append(");")
L.append("")
L.append("mergePatchPairs ();")
L.append("// ************************************************************************* //")
open(sys.argv[1], "w").write("\n".join(L) + "\n")
print("wrote", sys.argv[1])
