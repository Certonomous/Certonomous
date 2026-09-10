#!/usr/bin/env python3
"""
SUBOFF_R1 -- BUILD one level of the axisymmetric-wedge DARPA SUBOFF bare-hull
(DTRC Model 5470, zero incidence) incompressible-RANS simpleFoam case.

GEOMETRY PROVENANCE (rule 15, title-verified).  The axisymmetric hull profile is
generated STRICTLY from TABLE 1 (report p.4) of the title-page-verified source
  N.C. Groves, T.T. Huang, M.S. Chang, "Geometric Characteristics of DARPA SUBOFF
  Models (DTRC Model Nos. 5470 and 5471)", David Taylor Research Center,
  DTRC/SHD-1298-01, March 1989 (AD-A210 642, approved for public release),
filed at docs/papers/benchmark_test_cases/groves_1989_dtrc_shd1298_darpa_suboff_geometry.pdf.
NO recalled or alternate profile is used.  x and R below are in FEET, model scale
(the units of the source equations); vertices are emitted in METRES (x0.3048).

TOPOLOGY.  Axisymmetric flow as a thin 2*ALPHA_DEG wedge revolved about the x-axis
(lineage: F29_CONE_TM/build_cone.py, OpenFOAM movingCone convention).  front/back
planes type `wedge`, the true axis (r=0) type `empty`, the hull type `wall` named
`hull` (the patch the grader integrates drag on).  Blocks: one upstream block on
the axis, ONE BLOCK PER HULL AXIAL SEGMENT (bottom edge = the straight chord
between two hull stations -- so NO curved edge and NO two-polyLines-between-one-
vertex-pair collision at the collapsed nose/tail), one downstream block on the
axis.  Hull x-stations are cosine-clustered at nose and tail.

MESH ADMISSIBILITY (MESH_STANDARD sec.3).  After blockMesh this runs checkMesh and
REFUSES (exit 2) unless max non-orthogonality < 70, max skewness < 4.0, zero
negative-volume cells, and `Mesh OK`.  It REFUSES to build over a launched case
(rule-4 age-guard sibling) or into the tracked template dir.

Aref.  forceCoeffs Aref is set to the BUILT hull-patch (wedge sector) area read
back from constant/polyMesh, so the reported drag coefficient is normalised on the
same area the grader cross-checks.  The full-revolution equivalent (sector x
360/2ALPHA_DEG) is reported for the supervisor to compare with the analytic
5.988 m^2 and to pin reference.Aref at freeze.  THIS SCRIPT DOES NOT edit the
reference JSON.

ZERO `assert` (L-332).  Refusals are `raise`/`sys.exit(2)`.  Hard `-O` refusal.
"""
import sys

if not __debug__:
    sys.stderr.write("REFUSED: build_suboff.py must not run under `python3 -O`.\n")
    sys.exit(2)

import os
import re
import math
import json
import argparse
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
FT2M = 0.3048

# ---- FROZEN hull geometry: Groves/Huang/Chang 1989 TABLE 1 (feet) -----------------
RMAX_FT      = 5.0 / 6.0        # ft  (max body radius; max diameter 1.666667 ft = 0.508 m)
L_BOW_END    = 3.333333         # ft  forebody end / parallel-middle-body start
L_PMB_END    = 10.645833        # ft  parallel-middle-body end / afterbody start
L_AFT_PERP   = 13.979167        # ft  aft perpendicular (afterbody equation end)
L_TOTAL_FT   = 14.291667        # ft  total body length (= 4.3561 m)
AFT_RH, AFT_KO, AFT_K1 = 0.1175, 10.0, 44.6244   # afterbody polynomial constants


def hull_R_ft(x):
    """Model-scale hull radius R (ft) at axial station x (ft), TABLE 1 exactly."""
    if x < 0.0 or x > L_TOTAL_FT:
        return 0.0
    if x <= L_BOW_END:                                   # BOW  (exponent 1/2.1)
        t = 0.3 * x - 1.0
        inner = (1.126395101 * x * t**4
                 + 0.442874707 * x * x * t**3
                 + 1.0 - (t**4) * (1.2 * x + 1.0))
        inner = max(inner, 0.0)
        return RMAX_FT * inner ** (1.0 / 2.1)
    if x <= L_PMB_END:                                   # PARALLEL MIDDLE BODY
        return RMAX_FT
    if x <= L_AFT_PERP:                                  # AFTERBODY
        xi = (L_AFT_PERP - x) / 3.333333
        rh, Ko, K1 = AFT_RH, AFT_KO, AFT_K1
        poly = (rh * rh
                + rh * Ko * xi * xi
                + (20 - 20 * rh * rh - 4 * rh * Ko - (1.0 / 3.0) * K1) * xi**3
                + (-45 + 45 * rh * rh + 6 * rh * Ko + K1) * xi**4
                + (36 - 36 * rh * rh - 4 * rh * Ko - K1) * xi**5
                + (-10 + 10 * rh * rh + rh * Ko + (1.0 / 3.0) * K1) * xi**6)
        poly = max(poly, 0.0)
        return RMAX_FT * poly ** 0.5
    inner = 1.0 - (3.2 * x - 44.733333) ** 2            # AFTERBODY CAP (ellipsoidal)
    inner = max(inner, 0.0)
    return 0.1175 * RMAX_FT * inner ** 0.5


# ---- domain + wedge (metres) ------------------------------------------------------
L_M      = L_TOTAL_FT * FT2M    # 4.3561 m
X_MIN    = -2.0                 # m  upstream of the nose (nose at x=0)
X_MAX    = 9.0                  # m  downstream of the tail (tail at x=L_M)
R_FAR    = 3.0                  # m  farfield radius (~ 12 R_max, ~ 0.69 L)
ALPHA_DEG = 2.5                 # wedge half-angle (total wedge 5 deg)
TANA     = math.tan(math.radians(ALPHA_DEG))
Y1_TARGET = 1.0e-3             # m  DEFAULT first radial cell height at mid-hull (y+ ~ 100).
#   Per-level override lives in LEVELS[...]['y1'].  A family that pins this at a FIXED
#   absolute value across levels is NOT geometrically similar (MESH_STANDARD sec.9.2 and
#   SUBOFF_R1_PREREGISTRATION sec.4 require first-cell height and expansion ratio to SCALE
#   WITH THE MESH).  The `reg_*` family below scales y1 as 1/r; the legacy r=2 family does
#   not, and is kept unchanged only so the already-built r=2 evidence stays reproducible.

# freestream (SI) -- registered normalisation
U_INF    = 2.893               # m/s
NU       = 1.05e-6             # m^2/s
RHO      = 1000.0             # kg/m^3
L_REF    = 4.356               # m  (registered lRef; grader asserts ==4.356)
TI       = 0.02               # freestream turbulence intensity (smoke initial)

# LEGACY r=2 family.  Each direction refines x2 => x4 cells per level
# (7,600 / 30,400 / 121,600).  This is NOT the family registered in
# verification/campaign/SUBOFF_R1_PREREGISTRATION.md sec.4, and it is NOT
# geometrically similar: y1 is pinned at a fixed absolute 1.0e-3 m at every
# level.  Kept unchanged so the already-built r=2 evidence stays reproducible.
LEGACY_LEVELS = (
    ("coarse", dict(nx_up=30,  nx_hull=100, nx_down=60,  nr=40,  y1=1.0e-3)),
    ("medium", dict(nx_up=60,  nx_hull=200, nx_down=120, nr=80,  y1=1.0e-3)),
    ("fine",   dict(nx_up=120, nx_hull=400, nx_down=240, nr=160, y1=1.0e-3)),
)

# REGISTERED family -- SUBOFF_R1_PREREGISTRATION.md sec.4 "MESH PLAN":
#   "Target ~40k / 90k / 202.5k cells (2.25x per level => r ~ 1.5 in h ~ 1/sqrt(N)
#    for a 2-D-like refinement)" and "Geometric similarity is mandatory: first-cell
#    height and expansion ratio SCALE WITH THE MESH, recipe otherwise fixed".
# Every direction count x1.5 per level (exactly integral); y1 x(1/1.5) per level, so
# the radial cell-size envelope is one continuous grading function sampled r times
# finer at each level and the total expansion ratio is level-invariant.
# Built cells: 116x344 = 39,904 / 174x516 = 89,784 / 261x774 = 202,014
# (-0.24% from each registered target; ratio EXACTLY 2.25 per level).
REGISTERED_LEVELS = (
    ("reg_coarse", dict(nx_up=20, nx_hull=60,  nx_down=36, nr=344, y1=1.0e-3)),
    ("reg_medium", dict(nx_up=30, nx_hull=90,  nx_down=54, nr=516, y1=1.0e-3 / 1.5)),
    ("reg_fine",   dict(nx_up=45, nx_hull=135, nx_down=81, nr=774, y1=1.0e-3 / 2.25)),
)

LEVELS = LEGACY_LEVELS + REGISTERED_LEVELS
LEVELS_D = dict(LEVELS)

NONORTHO_MAX = 70.0
SKEWNESS_MAX = 4.0
OPENFOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"


def refuse(msg):
    sys.stderr.write("REFUSED: %s\n" % msg)
    sys.exit(2)


def foam_header(cls, obj):
    return ("FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
            "    class       %s;\n    object      %s;\n}\n" % (cls, obj))


def radial_grading(nr, y1=Y1_TARGET):
    """simpleGrading r-ratio (last/first cell) giving ~y1 first cell over the
    mid-hull thickness (R_FAR - RMAX).  Solved for the per-cell ratio then powered."""
    thick = R_FAR - RMAX_FT * FT2M
    lo, hi = 1.0 + 1e-6, 1.5
    for _ in range(200):
        g = 0.5 * (lo + hi)
        first = thick * (g - 1.0) / (g ** nr - 1.0)
        if first > y1:
            lo = g
        else:
            hi = g
    g = 0.5 * (lo + hi)
    return g ** (nr - 1)


def hull_stations(nx_hull):
    """Uniform x stations (ft) over the hull, i=0..nx_hull (nose..tail).

    Uniform (not cosine-clustered): the bow and stern-cap have vertical tangents
    (dR/dx -> infinity at r=0), so clustering axially there drives the first chord
    near-vertical and, with vertical radial extrusion, the wall non-orthogonality
    toward 90 deg.  Uniform spacing keeps the nose/tail chord slope bounded.  The
    residual nose/tail non-orthogonality still GROWS as the axial step shrinks under
    refinement -- a known limitation of vertical-line extrusion over a rounded nose,
    reported for the supervisor's freeze/triple decision."""
    return [L_TOTAL_FT * i / nx_hull for i in range(nx_hull + 1)]


class VertexBook:
    def __init__(self):
        self.verts = []
        self.idx = {}

    def get(self, key, coord):
        if key in self.idx:
            return self.idx[key]
        i = len(self.verts)
        self.verts.append(coord)
        self.idx[key] = i
        return i


def fv(x, r):      # front wedge plane (z>0), metres
    return (x, r, r * TANA)


def bv(x, r):      # back wedge plane (z<0), metres
    return (x, r, -r * TANA)


def build_topology(level):
    """Return (vertices, blocks, patch_faces) for blockMeshDict.  All lengths in m."""
    p = LEVELS_D[level]
    nx_up, nx_hull, nx_down, nr = p["nx_up"], p["nx_hull"], p["nx_down"], p["nr"]
    y1 = p.get("y1", Y1_TARGET)
    xs_ft = hull_stations(nx_hull)
    xs_m = [x * FT2M for x in xs_ft]
    Rs_m = [hull_R_ft(x) * FT2M for x in xs_ft]     # hull radius (m) per station
    N = nx_hull

    vb = VertexBook()

    def axis(sid, xm):
        return vb.get(("axis", sid), (xm, 0.0, 0.0))

    def topF(sid, xm):
        return vb.get(("topF", sid), fv(xm, R_FAR))

    def topB(sid, xm):
        return vb.get(("topB", sid), bv(xm, R_FAR))

    def botF(i):
        return vb.get(("botF", i), fv(xs_m[i], Rs_m[i]))

    def botB(i):
        return vb.get(("botB", i), bv(xs_m[i], Rs_m[i]))

    blocks = []        # (v0..v7, nx, nr, rgrad)
    hull_faces, farfield_faces, axis_faces = [], [], []
    front_faces, back_faces = [], []
    inlet_faces, outlet_faces = [], []
    rgrad = radial_grading(nr, y1)

    # ---- upstream block A: xmin -> h0 (nose), bottom on axis ----
    a_xmin, a_h0 = axis("xmin", X_MIN), axis("h0", xs_m[0])
    tBxmin, tBh0 = topB("xmin", X_MIN), topB("h0", xs_m[0])
    tFxmin, tFh0 = topF("xmin", X_MIN), topF("h0", xs_m[0])
    v = (a_xmin, a_h0, tBh0, tBxmin, a_xmin, a_h0, tFh0, tFxmin)
    blocks.append((v, nx_up, nr, rgrad))
    inlet_faces.append((v[0], v[3], v[7], v[4]))       # l_x=0
    axis_faces.append((v[0], v[1], v[5], v[4]))        # l_y=0 (collapsed)
    farfield_faces.append((v[3], v[2], v[6], v[7]))    # l_y=1
    back_faces.append((v[0], v[1], v[2], v[3]))        # l_z=0
    front_faces.append((v[4], v[5], v[6], v[7]))       # l_z=1

    # ---- hull blocks B_i: h_i -> h_{i+1}, one axial cell each ----
    for i in range(N):
        # left corner (station i)
        if i == 0:
            BBL = BFL = axis("h0", xs_m[0])            # nose tip on axis (collapsed)
        else:
            BBL, BFL = botB(i), botF(i)
        # right corner (station i+1)
        if i + 1 == N:
            BBR = BFR = axis("hN", xs_m[N])            # tail tip on axis (collapsed)
        else:
            BBR, BFR = botB(i + 1), botF(i + 1)
        TBL, TFL = topB("h%d" % i, xs_m[i]), topF("h%d" % i, xs_m[i])
        TBR, TFR = topB("h%d" % (i + 1), xs_m[i + 1]), topF("h%d" % (i + 1), xs_m[i + 1])
        v = (BBL, BBR, TBR, TBL, BFL, BFR, TFR, TFL)
        blocks.append((v, 1, nr, rgrad))
        hull_faces.append((v[0], v[1], v[5], v[4]))    # l_y=0 -> hull wall
        farfield_faces.append((v[3], v[2], v[6], v[7]))# l_y=1
        back_faces.append((v[0], v[1], v[2], v[3]))    # l_z=0
        front_faces.append((v[4], v[5], v[6], v[7]))   # l_z=1

    # ---- downstream block C: hN (tail) -> xmax, bottom on axis ----
    c_hN, c_xmax = axis("hN", xs_m[N]), axis("xmax", X_MAX)
    tBhN, tBxmax = topB("h%d" % N, xs_m[N]), topB("xmax", X_MAX)
    tFhN, tFxmax = topF("h%d" % N, xs_m[N]), topF("xmax", X_MAX)
    v = (c_hN, c_xmax, tBxmax, tBhN, c_hN, c_xmax, tFxmax, tFhN)
    blocks.append((v, nx_down, nr, rgrad))
    outlet_faces.append((v[1], v[2], v[6], v[5]))      # l_x=1
    axis_faces.append((v[0], v[1], v[5], v[4]))        # l_y=0 (collapsed)
    farfield_faces.append((v[3], v[2], v[6], v[7]))    # l_y=1
    back_faces.append((v[0], v[1], v[2], v[3]))        # l_z=0
    front_faces.append((v[4], v[5], v[6], v[7]))       # l_z=1

    patches = dict(inlet=("patch", inlet_faces), outlet=("patch", outlet_faces),
                   farfield=("patch", farfield_faces), hull=("wall", hull_faces),
                   axis=("empty", axis_faces),
                   frontWedge=("wedge", front_faces), backWedge=("wedge", back_faces))
    return vb.verts, blocks, patches


def blockmesh_dict(level):
    verts, blocks, patches = build_topology(level)
    vtxt = "\n".join("    (%.10f %.10f %.10f)" % v for v in verts)
    btxt = "\n".join(
        "    hex (%d %d %d %d %d %d %d %d) (%d %d 1) simpleGrading (1 %.6f 1)"
        % (v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7], nx, nr, rg)
        for (v, nx, nr, rg) in blocks)
    ptxt = ""
    for name, (ptype, faces) in patches.items():
        ftxt = "\n".join("            (%d %d %d %d)" % f for f in faces)
        ptxt += ("    %s\n    {\n        type %s;\n        faces\n        (\n%s\n        );\n    }\n"
                 % (name, ptype, ftxt))
    return ("%s\nscale 1;\n\nvertices\n(\n%s\n);\n\nblocks\n(\n%s\n);\n\nedges\n(\n);\n\n"
            "boundary\n(\n%s);\n\nmergePatchPairs\n(\n);\n"
            % (foam_header("dictionary", "blockMeshDict"), vtxt, btxt, ptxt))


# ---- 0.orig fields ---------------------------------------------------------------
K0 = 1.5 * (TI * U_INF) ** 2
OMEGA0 = math.sqrt(K0) / (0.09 ** 0.25 * 0.07 * 0.508)


def _field(cls, obj, dim, internal, bf):
    return ("%sdimensions      %s;\n\ninternalField   uniform %s;\n\nboundaryField\n{\n%s}\n"
            % (foam_header(cls, obj), dim, internal, bf))


def field_U():
    bf = ("    inlet    { type fixedValue; value uniform (%g 0 0); }\n"
          "    outlet   { type inletOutlet; inletValue uniform (0 0 0); value uniform (%g 0 0); }\n"
          "    farfield { type slip; }\n"
          "    hull     { type noSlip; }\n"
          "    axis     { type empty; }\n"
          "    frontWedge { type wedge; }\n    backWedge  { type wedge; }\n"
          % (U_INF, U_INF))
    return _field("volVectorField", "U", "[0 1 -1 0 0 0 0]", "(%g 0 0)" % U_INF, bf)


def field_p():
    bf = ("    inlet    { type zeroGradient; }\n"
          "    outlet   { type fixedValue; value uniform 0; }\n"
          "    farfield { type zeroGradient; }\n"
          "    hull     { type zeroGradient; }\n"
          "    axis     { type empty; }\n"
          "    frontWedge { type wedge; }\n    backWedge  { type wedge; }\n")
    return _field("volScalarField", "p", "[0 2 -2 0 0 0 0]", "0", bf)


def field_k():
    bf = ("    inlet    { type fixedValue; value uniform %g; }\n"
          "    outlet   { type inletOutlet; inletValue uniform %g; value uniform %g; }\n"
          "    farfield { type zeroGradient; }\n"
          "    hull     { type kqRWallFunction; value uniform %g; }\n"
          "    axis     { type empty; }\n"
          "    frontWedge { type wedge; }\n    backWedge  { type wedge; }\n"
          % (K0, K0, K0, K0))
    return _field("volScalarField", "k", "[0 2 -2 0 0 0 0]", "%g" % K0, bf)


def field_omega():
    bf = ("    inlet    { type fixedValue; value uniform %g; }\n"
          "    outlet   { type inletOutlet; inletValue uniform %g; value uniform %g; }\n"
          "    farfield { type zeroGradient; }\n"
          "    hull     { type omegaWallFunction; value uniform %g; }\n"
          "    axis     { type empty; }\n"
          "    frontWedge { type wedge; }\n    backWedge  { type wedge; }\n"
          % (OMEGA0, OMEGA0, OMEGA0, OMEGA0))
    return _field("volScalarField", "omega", "[0 0 -1 0 0 0 0]", "%g" % OMEGA0, bf)


def field_nut():
    bf = ("    inlet    { type calculated; value uniform 0; }\n"
          "    outlet   { type calculated; value uniform 0; }\n"
          "    farfield { type calculated; value uniform 0; }\n"
          "    hull     { type nutkWallFunction; value uniform 0; }\n"
          "    axis     { type empty; }\n"
          "    frontWedge { type wedge; }\n    backWedge  { type wedge; }\n")
    return _field("volScalarField", "nut", "[0 2 -1 0 0 0 0]", "0", bf)


def transport_properties():
    return ("%stransportModel  Newtonian;\n\nnu              %g;\n"
            % (foam_header("dictionary", "transportProperties"), NU))


def turbulence_properties():
    return ("%ssimulationType  RAS;\n\nRAS\n{\n    RASModel        kOmegaSST;\n"
            "    turbulence      on;\n    printCoeffs     on;\n}\n"
            % foam_header("dictionary", "turbulenceProperties"))


def fvschemes():
    return ("%sddtSchemes { default steadyState; }\n\n"
            "gradSchemes\n{\n    default Gauss linear;\n    grad(U) cellLimited Gauss linear 1;\n}\n\n"
            "divSchemes\n{\n    default none;\n"
            "    div(phi,U)      bounded Gauss linearUpwind grad(U);\n"
            "    div(phi,k)      bounded Gauss upwind;\n"
            "    div(phi,omega)  bounded Gauss upwind;\n"
            "    div((nuEff*dev2(T(grad(U))))) Gauss linear;\n}\n\n"
            "laplacianSchemes { default Gauss linear corrected; }\n"
            "interpolationSchemes { default linear; }\n"
            "snGradSchemes { default corrected; }\n"
            "wallDist { method meshWave; }\n"
            % foam_header("dictionary", "fvSchemes"))


def fvsolution():
    return ("%ssolvers\n{\n"
            "    p { solver GAMG; smoother GaussSeidel; tolerance 1e-7; relTol 0.05; }\n"
            '    "(U|k|omega)" { solver smoothSolver; smoother symGaussSeidel; '
            "tolerance 1e-8; relTol 0.1; nSweeps 1; }\n}\n\n"
            "SIMPLE\n{\n    nNonOrthogonalCorrectors 1;\n    consistent no;\n}\n\n"
            "relaxationFactors\n{\n    fields { p 0.3; }\n"
            '    equations { U 0.7; "(k|omega)" 0.7; }\n}\n'
            % foam_header("dictionary", "fvSolution"))


def controldict(endtime, deltat, write_interval, aref):
    return ("%sapplication     simpleFoam;\nstartFrom       startTime;\nstartTime       0;\n"
            "stopAt          endTime;\nendTime         %g;\ndeltaT          %g;\n"
            "writeControl    timeStep;\nwriteInterval   %d;\npurgeWrite      0;\n"
            "writeFormat     ascii;\nwritePrecision  16;\nwriteCompression off;\n"
            "timeFormat      general;\ntimePrecision   10;\nrunTimeModifiable false;\n\n"
            "functions\n{\n"
            "    forceCoeffs\n    {\n"
            "        type            forceCoeffs;\n        libs            (forces);\n"
            "        writeControl    timeStep;\n        writeInterval   1;\n        log             true;\n"
            "        patches         (hull);\n"
            "        rho             rhoInf;\n        rhoInf          %g;\n"
            "        magUInf         %g;\n        lRef            %g;\n        Aref            %.10g;\n"
            "        liftDir         (0 0 1);\n        dragDir         (1 0 0);\n"
            "        CofR            (0 0 0);\n        pitchAxis       (0 1 0);\n    }\n}\n"
            % (foam_header("dictionary", "controlDict"), endtime, deltat, write_interval,
               RHO, U_INF, L_REF, aref))


# ---- built-mesh hull-patch (wedge sector) area, read from polyMesh ----------------
def _read(path):
    return open(path, "r", errors="replace").read()


def parse_points(case):
    txt = _read(os.path.join(case, "constant/polyMesh/points"))
    m = re.search(r"\n(\d+)\s*\(", txt)
    if not m:
        refuse("cannot parse points header")
    start = m.end()
    depth = 1
    i = start
    while i < len(txt) and depth:
        if txt[i] == "(":
            depth += 1
        elif txt[i] == ")":
            depth -= 1
        i += 1
    body = txt[start:i - 1]
    pts = [tuple(float(x) for x in t.split())
           for t in re.findall(r"\(([^()]*)\)", body)]
    return pts


def parse_faces(case):
    txt = _read(os.path.join(case, "constant/polyMesh/faces"))
    m = re.search(r"\n(\d+)\s*\(", txt)
    if not m:
        refuse("cannot parse faces header")
    body = txt[m.end():]
    faces = []
    for fm in re.finditer(r"(\d+)\s*\(([^()]*)\)", body):
        faces.append([int(v) for v in fm.group(2).split()])
    return faces


def parse_boundary_patch(case, patch):
    txt = _read(os.path.join(case, "constant/polyMesh/boundary"))
    m = re.search(patch + r"\s*\{[^}]*?nFaces\s+(\d+);[^}]*?startFace\s+(\d+);", txt, re.S)
    if not m:
        refuse("no '%s' patch in polyMesh/boundary" % patch)
    return int(m.group(1)), int(m.group(2))


def polygon_area(pts):
    """Magnitude of the vector area of a (possibly collapsed) planar polygon in 3D."""
    ax = ay = az = 0.0
    n = len(pts)
    for i in range(n):
        x1, y1, z1 = pts[i]
        x2, y2, z2 = pts[(i + 1) % n]
        ax += y1 * z2 - z1 * y2
        ay += z1 * x2 - x1 * z2
        az += x1 * y2 - y1 * x2
    return 0.5 * math.sqrt(ax * ax + ay * ay + az * az)


def hull_sector_area(case):
    pts = parse_points(case)
    faces = parse_faces(case)
    nF, sF = parse_boundary_patch(case, "hull")
    tot = 0.0
    for fi in range(sF, sF + nF):
        tot += polygon_area([pts[v] for v in faces[fi]])
    return tot, nF


# ---- graded values READ BACK from the built mesh (MESH_STANDARD sec.9.2) ---------
def radial_column(case, x_target):
    """Sorted radial coordinates (m) of the built point column on the front wedge
    plane nearest axial station x_target.  Read from constant/polyMesh/points."""
    pts = parse_points(case)
    front = [p for p in pts if p[2] > 1e-12]
    if not front:
        refuse("no front-wedge points found in %s" % case)
    xs = sorted({p[0] for p in front})
    xsel = min(xs, key=lambda x: abs(x - x_target))
    ys = sorted(p[1] for p in front if abs(p[0] - xsel) < 1e-12)
    return xsel, ys


def graded_readback(case, x_target=2.0):
    """(x, first cell height, last cell height, total expansion ratio) at x_target."""
    xsel, ys = radial_column(case, x_target)
    if len(ys) < 3:
        refuse("radial column at x=%g has only %d points in %s" % (xsel, len(ys), case))
    first = ys[1] - ys[0]
    last = ys[-1] - ys[-2]
    return xsel, first, last, (last / first if first > 0 else float("nan"))


def _grab(out, pat, cast=float):
    m = re.search(pat, out)
    return cast(m.group(1)) if m else None


def write_birth_certificate(case_dir, level, out, cells, nonortho, skew,
                            hull_faces, sector, full_area):
    """birth_certificate.json for this level (PREREGISTRATION sec.4 / MESH_STANDARD
    sec.9.2, sec.11).  Graded values are READ BACK from the built mesh, never from the
    requested parameter.  Written at the case root (not inside polyMesh) so it is
    trackable while the polyMesh tree stays untracked."""
    p = LEVELS_D[level]
    xsel, first, last, expansion = graded_readback(case_dir)
    cert = dict(
        case=os.path.abspath(case_dir), level=level,
        requested=dict(nx_up=p["nx_up"], nx_hull=p["nx_hull"], nx_down=p["nx_down"],
                       nr=p["nr"], y1_requested_m=p.get("y1", Y1_TARGET),
                       simpleGrading_r=radial_grading(p["nr"], p.get("y1", Y1_TARGET))),
        readback=dict(x_station_m=xsel, first_cell_m=first, last_cell_m=last,
                      total_expansion_ratio=expansion),
        checkMesh=dict(
            cells=cells, hull_patch_faces=hull_faces,
            max_nonOrthogonality_deg=nonortho, max_skewness=skew,
            max_aspect_ratio=_grab(out, r"Max aspect ratio = ([0-9.eE+\-]+)"),
            # non-greedy + explicit sentence terminator: checkMesh prints
            # "Min volume = 5.2e-09. Max volume = ..." and a greedy class would
            # swallow the terminating '.' into the float.
            min_volume=_grab(out, r"Min volume = ([0-9.eE+\-]+?)\.\s"),
            max_volume=_grab(out, r"Max volume = ([0-9.eE+\-]+?)\.\s"),
            total_volume=_grab(out, r"Total volume = ([0-9.eE+\-]+?)\.\s"),
            mesh_ok=("Mesh OK" in out),
            failed_checks=_grab(out, r"Failed (\d+) mesh checks", int) or 0,
            severely_nonortho_faces=_grab(
                out, r"Number of severely non-orthogonal \(> 70 degrees\) faces: (\d+)", int) or 0,
        ),
        gates=dict(nonortho_max=NONORTHO_MAX, nonortho_pass=(nonortho < NONORTHO_MAX),
                   skew_max=SKEWNESS_MAX, skew_pass=(skew < SKEWNESS_MAX)),
        area=dict(hull_sector_area_m2=sector, wedge_total_deg=2 * ALPHA_DEG,
                  full_revolution_area_m2=full_area, analytic_m2=5.988,
                  pct_diff_from_analytic=100.0 * (full_area - 5.988) / 5.988),
    )
    path = os.path.join(case_dir, "birth_certificate.json")
    open(path, "w").write(json.dumps(cert, indent=2, sort_keys=True) + "\n")
    return cert


# ---- write / mesh / measure ------------------------------------------------------
def guard_target(case_dir):
    for d in (os.listdir(case_dir) if os.path.isdir(case_dir) else []):
        if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d) and d != "0":
            refuse("target %s already holds numeric time dir %r -- refusing to overwrite a run"
                   % (case_dir, d))
    if os.path.isfile(os.path.join(case_dir, "rc")):
        refuse("target %s already holds an rc sidecar -- refusing to rebuild a launched case" % case_dir)


def write_case(case_dir, level, endtime, deltat, wi):
    guard_target(case_dir)
    for sub in ("0.orig", "constant", "system"):
        os.makedirs(os.path.join(case_dir, sub), exist_ok=True)
    open(os.path.join(case_dir, "system", "blockMeshDict"), "w").write(blockmesh_dict(level))
    open(os.path.join(case_dir, "system", "fvSchemes"), "w").write(fvschemes())
    open(os.path.join(case_dir, "system", "fvSolution"), "w").write(fvsolution())
    # placeholder Aref for meshing; rewritten after the built sector area is measured
    open(os.path.join(case_dir, "system", "controlDict"), "w").write(
        controldict(endtime, deltat, wi, 1.0))
    open(os.path.join(case_dir, "constant", "transportProperties"), "w").write(transport_properties())
    open(os.path.join(case_dir, "constant", "turbulenceProperties"), "w").write(turbulence_properties())
    open(os.path.join(case_dir, "0.orig", "U"), "w").write(field_U())
    open(os.path.join(case_dir, "0.orig", "p"), "w").write(field_p())
    open(os.path.join(case_dir, "0.orig", "k"), "w").write(field_k())
    open(os.path.join(case_dir, "0.orig", "omega"), "w").write(field_omega())
    open(os.path.join(case_dir, "0.orig", "nut"), "w").write(field_nut())


def of_run(case_dir, cmd):
    full = "set +u; source %s >/dev/null 2>&1; set -u; %s" % (OPENFOAM_BASHRC, cmd)
    return subprocess.run(["bash", "-c", full], cwd=case_dir, capture_output=True, text=True)


def mesh_and_check(case_dir, level, endtime, deltat, wi):
    bm = of_run(case_dir, "blockMesh > log.blockMesh 2>&1; echo rc=$?")
    if "rc=0" not in bm.stdout:
        tail = _read(os.path.join(case_dir, "log.blockMesh"))[-2500:]
        refuse("blockMesh failed in %s:\n%s" % (case_dir, tail))
    cm = of_run(case_dir, "checkMesh -constant > log.checkMesh 2>&1; echo rc=$?")
    out = _read(os.path.join(case_dir, "log.checkMesh"))
    if "Mesh OK" not in out:
        refuse("checkMesh did not report `Mesh OK` in %s:\n%s" % (case_dir, out[-2500:]))
    m_no = re.search(r"non-orthogonality Max:\s+([0-9.eE+\-]+)", out)
    m_sk = re.search(r"Max skewness = ([0-9.eE+\-]+)", out)
    m_nc = re.search(r"cells:\s+(\d+)", out)
    neg = re.search(r"(\d+)\s+cells with negative volume", out) or re.search(r"negative volume", out)
    if not (m_no and m_sk):
        refuse("could not parse checkMesh non-ortho/skew in %s" % case_dir)
    nonortho, skew = float(m_no.group(1)), float(m_sk.group(1))
    ncells = int(m_nc.group(1)) if m_nc else None
    sector, nhull = hull_sector_area(case_dir)
    wedge_frac = (2.0 * ALPHA_DEG) / 360.0
    full_area = sector / wedge_frac
    # Measurements and the birth certificate are written BEFORE the admissibility
    # gates, so that a level which BREACHES a gate still leaves its evidence on disk
    # for the supervisor.  The gates themselves are unchanged and still refuse.
    write_birth_certificate(case_dir, level, out, ncells, nonortho, skew,
                            nhull, sector, full_area)
    if nonortho >= NONORTHO_MAX:
        refuse("max non-orthogonality %.3f >= gate %.1f" % (nonortho, NONORTHO_MAX))
    if skew >= SKEWNESS_MAX:
        refuse("max skewness %.3f >= gate %.1f" % (skew, SKEWNESS_MAX))
    # rewrite controlDict with the BUILT sector area as forceCoeffs Aref
    open(os.path.join(case_dir, "system", "controlDict"), "w").write(
        controldict(endtime, deltat, wi, sector))
    mesh_line = ("checkMesh: Mesh OK; cells=%s; hullFaces=%d; maxNonOrtho=%.4f (<%.0f); "
                 "maxSkewness=%.4f (<%.1f); negVol=%s"
                 % (ncells, nhull, nonortho, NONORTHO_MAX, skew, SKEWNESS_MAX,
                    "yes" if neg else "no"))
    area_line = ("hull sector area (built, wedge %g deg) = %.8e m^2; wedge fraction = %.8f; "
                 "full-revolution equivalent = %.6f m^2; analytic (Groves TABLE 1) = 5.988 m^2; "
                 "forceCoeffs Aref set to sector = %.8e m^2"
                 % (2 * ALPHA_DEG, sector, wedge_frac, full_area, sector))
    open(os.path.join(case_dir, "MESH_LINE.txt"), "w").write(mesh_line + "\n" + area_line + "\n")
    return dict(cells=ncells, nonortho=nonortho, skew=skew, hull_faces=nhull,
                sector_area=sector, full_area=full_area, mesh_line=mesh_line, area_line=area_line)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", required=True, choices=[n for n, _ in LEVELS])
    ap.add_argument("--dir", required=True)
    ap.add_argument("--endtime", type=float, default=50.0, help="controlDict endTime (iters, deltaT=1)")
    ap.add_argument("--mesh", action="store_true", help="run blockMesh + checkMesh and enforce gates")
    a = ap.parse_args(argv)
    endtime, deltat, wi = a.endtime, 1.0, int(a.endtime)
    write_case(a.dir, a.level, endtime, deltat, wi)
    print("WROTE %s level %s" % (a.dir, a.level))
    if a.mesh:
        r = mesh_and_check(a.dir, a.level, endtime, deltat, wi)
        print(r["mesh_line"])
        print(r["area_line"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
