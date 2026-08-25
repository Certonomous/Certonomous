#!/usr/bin/env python3
"""VMFL036 -- emit system/blockMeshDict.template (axisymmetric polar wedge, sphere).

Geometry, verbatim from the manual (VMFL036, p.125): sphere diameter D = 1 m,
"the circular fluid domain around the sphere has a radius of 50 D", modelled
"in 2D with axisymmetric boundary conditions".

TOPOLOGY.  Two blocks in a half-plane polar grid (r, theta); theta measured from
the +x axis, theta = 180 deg = upstream stagnation line, theta = 0 = downstream
wake line.  Both blocks run theta DECREASING.

THE AXIS.  The half-plane points at theta = 0 and theta = 180 have y = 0, so
their two wedge copies are the SAME point.  They are therefore emitted as ONE
SHARED VERTEX and the block hexes reference that single label twice.  This is the
pattern OpenFOAM's own axisymmetric tutorials use -- e.g.
tutorials/combustion/reactingFoam/RAS/SandiaD_LTS/system/blockMeshDict, whose
axis patch reads `type empty; faces ( (0 7 7 0) ... )`.  Emitting two coincident
vertices instead would leave duplicate points that blockMesh does NOT merge under
the default `mergeType topology`, which is the failure this file was rewritten to
avoid.

PATCH FACE ORDERING is the blockMesh standard outward set for a hex (0..7):
    x-min (0 4 7 3)   x-max (1 2 6 5)
    y-min (0 1 5 4)   y-max (3 7 6 2)
    z-min (0 3 2 1)   z-max (4 5 6 7)
Every patch below is written in that order so its normal points OUT of the fluid.
Checked by hand for the sphere (normal points INTO the sphere, i.e. out of the
fluid) and the farField (normal points away from the origin).

REFINEMENT FAMILY -- EXACTLY NESTED, r = 2 BY CONSTRUCTION.  The radial grading is
a FIXED continuous stretching map r(xi) = r_in + L*(K^xi - 1)/(K - 1), xi = i/N,
with K frozen (K = 400).  For that map the blockMesh total expansion ratio at N
cells is R(N) = K^((N-1)/N), which is why the launcher computes R per level
instead of holding R fixed: holding R fixed does NOT halve h exactly, holding K
fixed makes every L2 node at even index coincide EXACTLY with an L1 node.  The
theta direction is uniform, so doubling NT halves h_theta exactly too.
"""
import math
import sys

ALPHA_DEG = 2.5                      # wedge HALF-angle; full wedge angle 5 deg
R_IN = 0.5                           # sphere radius, D/2 with D = 1 m
R_OUT = 50.0                         # 50 D, manual p.125
c = math.cos(math.radians(ALPHA_DEG))
s = math.sin(math.radians(ALPHA_DEG))


def wedge(x, y, sign):
    """Half-plane point (x, y) -> the wedge copy on the sign*alpha plane."""
    return (x, y * c, sign * y * s)


# ---- vertices.  Axis points (y = 0) are SHARED: one label, not two. ----------
#  0  A0   theta = 0    r = R_IN    (downstream axis)
#  1  A1-  theta = 90   r = R_IN    z-
#  2  A1+  theta = 90   r = R_IN    z+
#  3  A2   theta = 180  r = R_IN    (upstream axis)
#  4  B0   theta = 0    r = R_OUT
#  5  B1-  theta = 90   r = R_OUT   z-
#  6  B1+  theta = 90   r = R_OUT   z+
#  7  B2   theta = 180  r = R_OUT
V = [
    (R_IN, 0.0, 0.0),                 # 0  A0
    wedge(0.0, R_IN, -1),             # 1  A1-
    wedge(0.0, R_IN, +1),             # 2  A1+
    (-R_IN, 0.0, 0.0),                # 3  A2
    (R_OUT, 0.0, 0.0),                # 4  B0
    wedge(0.0, R_OUT, -1),            # 5  B1-
    wedge(0.0, R_OUT, +1),            # 6  B1+
    (-R_OUT, 0.0, 0.0),               # 7  B2
]
NAMES = ["A0", "A1-", "A1+", "A2", "B0", "B1-", "B1+", "B2"]


def arcmid(r, theta_deg, sign):
    x = r * math.cos(math.radians(theta_deg))
    y = r * math.sin(math.radians(theta_deg))
    return wedge(x, y, sign)


def f(v):
    return "(%.12g %.12g %.12g)" % v


L = []
L.append("""/*--------------------------------*- C++ -*----------------------------------*\\
| VMFL036 -- Laminar Flow Past Sphere.  Axisymmetric wedge, GENERATED FILE.     |
| Emitted by make_blockmeshdict_template.py; __NT__, __NR__ and __RGRAD__ are   |
| substituted by run_vmfl036.sh.  DO NOT HAND-EDIT.                             |
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
for i, v in enumerate(V):
    L.append("    %-38s // %d  %s" % (f(v), i, NAMES[i]))
L.append(");")
L.append("")
L.append("blocks")
L.append("(")
# block 1: theta 90 -> 0 .  local x = theta, y = radial, z = wedge thickness.
L.append("    hex (1 0 4 5 2 0 4 6) (__NT__ __NR__ 1) simpleGrading (1 __RGRAD__ 1)  // theta  90 -> 0")
# block 2: theta 180 -> 90
L.append("    hex (3 1 5 7 3 2 6 7) (__NT__ __NR__ 1) simpleGrading (1 __RGRAD__ 1)  // theta 180 -> 90")
L.append(");")
L.append("")
L.append("edges")
L.append("(")
for (a, b, r, th, sign) in [
        (1, 0, R_IN, 45.0, -1), (2, 0, R_IN, 45.0, +1),
        (5, 4, R_OUT, 45.0, -1), (6, 4, R_OUT, 45.0, +1),
        (3, 1, R_IN, 135.0, -1), (3, 2, R_IN, 135.0, +1),
        (7, 5, R_OUT, 135.0, -1), (7, 6, R_OUT, 135.0, +1)]:
    L.append("    arc %d %d %s" % (a, b, f(arcmid(r, th, sign))))
L.append(");")
L.append("")
L.append("""boundary
(
    sphere
    {
        // y-min of each block, ordering (0 1 5 4): normal points INTO the sphere,
        // i.e. OUT of the fluid domain.  Hand-checked.
        type wall;
        faces ( (1 0 0 2) (3 1 2 3) );
    }
    farField
    {
        // y-max of each block, ordering (3 7 6 2): normal points AWAY from the
        // origin.  Hand-checked.
        type patch;
        faces ( (5 6 4 4) (7 7 6 5) );
    }
    axis
    {
        // The collapsed wedge axis: every vertex has y = z = 0, so these faces
        // have EXACTLY zero area.  Declared empty, per the OpenFOAM axisymmetric
        // convention and the SandiaD_LTS tutorial's `(0 7 7 0)` pattern.
        // block 1 x-max (1 2 6 5) -> theta = 0 ; block 2 x-min (0 4 7 3) -> theta = 180.
        type empty;
        faces ( (0 4 4 0) (3 3 7 7) );
    }
    front
    {
        // z-max (4 5 6 7): the +alpha wedge plane.
        type wedge;
        faces ( (2 0 4 6) (3 2 6 7) );
    }
    back
    {
        // z-min (0 3 2 1): the -alpha wedge plane.
        type wedge;
        faces ( (1 5 4 0) (3 7 5 1) );
    }
);

mergePatchPairs ();
// ************************************************************************* //""")

open(sys.argv[1], "w").write("\n".join(L) + "\n")
print("wrote", sys.argv[1])
