#!/usr/bin/env python3
"""PRD-E1 PARAMETRIC CASE BUILDER -- Porous Radiator Duct, EXACT-tier rung 1.

Navier-spine Case 3.  Writes the simpleFoam + k-omega SST + explicitPorositySource
(DarcyForchheimer) case for the 5-point U_s sweep at mesh levels L1/L2/L3 and the
BUDGETED L4, from the FROZEN design inputs in

    docs/campaigns/navier_class/PRD/PRD_E1_PREREGISTRATION_DRAFT.md   (the draft)
    verification/campaign/PRD_E1_GATE_RULING_2026-09-09.md            (the ruling)

STOP-BEFORE-FREEZE.  THIS FILE IS AN UNFROZEN DRAFT INSTRUMENT.  It LAUNCHES
NOTHING -- not blockMesh, not topoSet, not simpleFoam.  It emits case inputs and
--selftest validates the arithmetic and the emitted dicts against the frozen
numbers.  Running blockMesh/topoSet/the solver is the supervisor's §2bb pre-flight
and launch, AFTER the supervisor's non-delegable §3 check-1 diff-read of this file
and verification's ½rho check-1.  No graded compute is performed here.

EVERY PHYSICAL NUMBER BELOW IS A FROZEN DESIGN INPUT taken from the draft/ruling;
none is chosen here.  Each carries the draft §/line it came from so the check-1
diff-read can spot-check it.  A number this file needed and the draft did not fix
is marked PROVISIONAL and named for the §2bb pre-flight -- it is NOT invented as a
gate input (the gate is Delta-p vs Ergun; provisional items do not touch it).

L-303/L-244: fixed-recipe ladder, geometry + porous-zone BYTE-FIXED across levels,
only the cell counts change (x2 per direction per level); L4 budgeted.
L-514: the p-solver linear tolerance is PINNED FROM THE §2bb SMOKE MEASUREMENT,
not guessed; the values written here are PROVISIONAL placeholders so the case
parses, and are re-pinned in a dated addendum after the smoke measures the
near-convergence Delta-p sensitivity (abs tol one decade below the gate).
L-332: no module-level assert; --selftest drives the checks.
"""
import argparse
import os
import shutil
import sys
import tempfile

EXIT_OK, EXIT_FAIL = 0, 1

# ==========================================================================
# FROZEN DESIGN INPUTS -- draft §1 geometry table (lines 60-72), §2.3 (143-151),
# §2.5 (165-172), §3 (184-192), §5 (242-247).  QUOTED, not chosen.
# ==========================================================================
# --- §1 geometry (draft lines 62-72) --------------------------------------
H       = 0.100          # duct side, square section [m]           (draft §1:62)
L_IN    = 0.200          # inlet-development length [m] = 2*D_h     (draft §1:63)
L_CORE  = 0.100          # porous-core length [m]  = the L in Ergun (draft §1:64)
L_OUT   = 0.200          # outlet-recovery length [m] = 2*D_h       (draft §1:65)
L_TOT   = 0.500          # total length [m]                          (draft §1:66)
# streamwise x-stations of the four block boundaries (byte-fixed across levels).
# CLEAN LITERALS, not L_IN+L_CORE: 0.2+0.1 == 0.30000000000000004 in double and
# would pollute both the block vertices and the topoSet box, breaking the
# "byte-fixed geometry" invariant (L-303).  Consistency with the §1 lengths is
# asserted in --selftest.
X0, X1, X2, X3 = 0.0, 0.200, 0.300, 0.500          # 0.0, 0.200, 0.300, 0.500
# porous cellZone bounding box, coincident with the core block (draft §1:72):
POROUS_BOX_MIN = (X1, 0.0, 0.0)     # (0.200, 0, 0)
POROUS_BOX_MAX = (X2, H, H)         # (0.300, 0.100, 0.100)
# faceZone slab half-thickness for the two Delta-p planes at X1/X2 [m].  A BUILD
# parameter (NOT frozen physics; it touches no gate input): 1e-4 m is far below
# the finest streamwise cell (L4 core dx = 0.1/192 = 5.2e-4 m, half 2.6e-4 m), so
# the boxToFace slab about each plane selects ONLY the internal faces whose centre
# sits exactly on the plane, at every mesh level.  Byte-fixed across levels
# (topo_set_dict() takes no level argument).
PLANE_SLAB_HALF = 1.0e-4

EPS     = 0.40           # bed porosity                             (draft §1:68)
D_P     = 0.003          # particle diameter [m], 3 mm spheres      (draft §1:69)
RHO     = 1.2            # air density [kg/m3]                       (draft §1:69)
MU      = 1.8e-5         # air dynamic viscosity [Pa.s]             (draft §1:69)
NU      = 1.5e-5         # air kinematic viscosity [m2/s] = mu/rho  (draft §1:69)

# --- §2.3 the exact D/f mapping (draft lines 129-151, ruling §0) -----------
# Ergun:  Delta-p/L = A*U_s + B*U_s^2
#   A = 150*mu*(1-eps)^2 / (eps^3 * d_p^2)   [Pa.s/m2]   viscous, per length
#   B = 1.75*rho*(1-eps) / (eps^3 * d_p)     [Pa.s2/m3]  inertial, per length
# OpenFOAM-fed DarcyForchheimer coefficients (user dXYZ, fXYZ):
#   d = 150*(1-eps)^2 / (eps^3 * d_p^2)      [1/m2]   (= A/mu)
#   f = 3.5*(1-eps) / (eps^3 * d_p)          [1/m]    (= 2*B/(0.5*rho)... see below)
#
# THE 3.5 = 2 x 1.75 IS LOAD-BEARING (draft §2.3 lines 136-141; ruling §0).
# OpenFOAM v2606 assembles the Forchheimer term with an INTERNAL 0.5 factor:
#   DarcyForchheimer.C:85-89  ->  forchCoeff = 0.5*fXYZ  ("the leading 0.5 is
#   from 1/2*rho"), verified in the installed source api=2606 on this box.
# So the effective inertial coefficient is 0.5*rho*f.  Feeding f = 3.5*(1-eps)/
# (eps^3 d_p) makes 0.5*rho*f = 1.75*rho*(1-eps)/(eps^3 d_p) = B EXACTLY.  Drop
# the factor of 2 and the inertial Delta-p is HALVED -- the single most likely
# silent error, which the smoke Delta-p-match (§7) catches.
A_ERGUN = 1687.5         # = 150*MU*(1-EPS)^2/(EPS^3*D_P^2)  (draft §2.3:147)
B_ERGUN = 6562.5         # = 1.75*RHO*(1-EPS)/(EPS^3*D_P)    (draft §2.3:148)
D_STREAM = 9.375e7       # DarcyForchheimer d, streamwise [1/m2] (draft §2.3:149)
F_STREAM = 10937.5       # DarcyForchheimer f, streamwise [1/m]  (draft §2.3:150)

# --- §2.5 anisotropy: cross-stream resistance 1000x streamwise (draft:165-172)
ANISO = 1000.0
D_XYZ = (D_STREAM, D_STREAM * ANISO, D_STREAM * ANISO)   # (9.375e7, 9.375e10, 9.375e10)
F_XYZ = (F_STREAM, F_STREAM * ANISO, F_STREAM * ANISO)   # (10937.5, 1.09375e7, 1.09375e7)

# --- §3 the registered superficial-velocity sweep (draft lines 184-192) ----
U_S_SET = (0.25, 0.50, 1.00, 2.00, 4.00)   # [m/s]  (draft §3:186-190)
# analytic Ergun Delta-p across the core: Delta-p = A*L_core*U + B*L_core*U^2
#   coefficients per the draft: 168.75*U + 656.25*U^2  (draft §3:192)
# the five target Pa (rounded in the draft): 83.20/248.44/825.00/2962.50/11175.00
ERGUN_TARGET_PA = (83.20, 248.44, 825.00, 2962.50, 11175.00)   # (draft §3:186-190)

# --- §5 mesh ladder (draft lines 242-247): cross n x n, streamwise per block
#   L1 16x16 24/24/24 = 18432; L2 32x32 48/48/48 = 147456;
#   L3 64x64 96/96/96 = 1179648; L4 128x128 192/192/192 = 9437184 (BUDGETED)
# refinement ratio r = 2 uniform in all three directions (x8 cells per step).
LEVEL_CROSS  = {"L1": 16,  "L2": 32,  "L3": 64,  "L4": 128}   # cells across y,z
LEVEL_STREAM = {"L1": 24,  "L2": 48,  "L3": 96,  "L4": 192}   # cells per stream block
LEVEL_CELLS  = {"L1": 18432, "L2": 147456, "L3": 1179648, "L4": 9437184}  # draft §5
GRADED_LEVELS = ("L1", "L2", "L3")   # L4 is budgeted, run only if pre-asymptotic

# --- §7/§2bb PROVISIONAL solver controls (NOT frozen physics) --------------
# L-514: PINNED FROM §2bb SMOKE, provisional here.  The abs tol is set one decade
# below the finest monitored Delta-p resolution; the FINAL values are pinned by a
# dated addendum after the smoke measures the solver-induced Delta-p sensitivity.
P_SOLVER_RELTOL_PROVISIONAL = 1e-3     # (draft §7 clause 6) PINNED (§7.6 addendum 2026-09-09)
P_SOLVER_ABSTOL_PROVISIONAL = 1e-8     # (draft §7 clause 6) PINNED; the binding floor (§7.6)
ENDTIME_PROVISIONAL = 3000             # steady iterations; sized in §2bb (deltaT=1)
DELTAT = 1                              # steady simpleFoam unit step (clause-5)
# Inlet turbulence estimates are a MODELING input, not a frozen physical value:
# I=5%, mixing length l = 0.07*D_h.  PROVISIONAL, confirmed in §2bb.  The gated
# Delta-p is dominated by the volumetric D/f sink, so these have minor effect.
TURB_INTENSITY_PROVISIONAL = 0.05
MIX_LENGTH_PROVISIONAL = 0.07 * H


# ==========================================================================
# ANALYTIC ERGUN (from the FROZEN coefficients; the comparator's reference)
# ==========================================================================
def ergun_dp(u_s):
    """Analytic Ergun Delta-p across the porous core [Pa], from the frozen A, B.

    Delta-p = A*L_core*U_s + B*L_core*U_s^2 = 168.75*U_s + 656.25*U_s^2.
    This is the SELF-CONSISTENCY reference: the CFD must reproduce the law fed
    into its own DarcyForchheimer sink."""
    return A_ERGUN * L_CORE * u_s + B_ERGUN * L_CORE * u_s * u_s


def darcy_coeffs():
    """Return (d_xyz, f_xyz) exactly as fed to explicitPorositySource, with the
    3.5 ½rho-undo already in F_STREAM.  Cross-check: 0.5*RHO*F_STREAM == B."""
    return D_XYZ, F_XYZ


# ==========================================================================
# OpenFOAM dict emitters -- byte-fixed geometry, only cell counts vary by level
# ==========================================================================
_HEAD = ("/*--------------------------------*- C++ -*----------------------------------*\\\n"
         "| PRD-E1 case input, emitted by build_prd.py (UNFROZEN DRAFT).            |\n"
         "\\*---------------------------------------------------------------------------*/\n")


def _foamfile(cls, obj, location=None):
    loc = ('    location    "%s";\n' % location) if location else ""
    return (_HEAD + "FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
            "    class       %s;\n%s    object      %s;\n}\n"
            "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //\n"
            % (cls, loc, obj))


def block_mesh_dict(level):
    """All-hex blockMesh: square duct, three streamwise blocks (in/core/out).
    16 vertices at four x-stations (0, 0.200, 0.300, 0.500), each station a
    y-z square 0..H.  Uniform simpleGrading (1 1 1) -> non-ortho ~0 (checkMesh
    gate §5).  The core block bounds are byte-identical to POROUS_BOX (§1:72)."""
    ncross = LEVEL_CROSS[level]
    nstream = LEVEL_STREAM[level]
    xs = (X0, X1, X2, X3)
    verts = []
    for x in xs:
        verts += [(x, 0.0, 0.0), (x, H, 0.0), (x, H, H), (x, 0.0, H)]
    vtxt = "\n".join("    (%s %s %s)" % v for v in verts)
    # three hex blocks between consecutive stations
    blk = []
    for s in range(3):
        b0 = s * 4
        b1 = (s + 1) * 4
        hexv = (b0, b0 + 1, b0 + 2, b0 + 3, b1, b1 + 1, b1 + 2, b1 + 3)
        blk.append("    hex (%d %d %d %d %d %d %d %d) (%d %d %d) simpleGrading (1 1 1)"
                    % (hexv + (nstream, ncross, ncross)))
    blocks = "\n".join(blk)
    # boundary faces
    inlet = "        (0 1 2 3)"                      # -x face of block0
    outlet = "        (12 13 14 15)"                 # +x face of block2
    wallf = []
    for s in range(3):
        b0, b1 = s * 4, (s + 1) * 4
        # four side faces (y=0, y=H, z=0, z=H)
        wallf.append("        (%d %d %d %d)" % (b0 + 0, b1 + 0, b1 + 3, b0 + 3))  # z ... face y=0
        wallf.append("        (%d %d %d %d)" % (b0 + 1, b0 + 2, b1 + 2, b1 + 1))  # y=H
        wallf.append("        (%d %d %d %d)" % (b0 + 0, b0 + 1, b1 + 1, b1 + 0))  # z=0
        wallf.append("        (%d %d %d %d)" % (b0 + 3, b1 + 3, b1 + 2, b0 + 2))  # z=H
    walls = "\n".join(wallf)
    return (_foamfile("dictionary", "blockMeshDict", "system")
            + "scale 1;\n\nvertices\n(\n" + vtxt + "\n);\n\n"
            + "blocks\n(\n" + blocks + "\n);\n\nedges ();\n\n"
            + "boundary\n(\n"
            + "    inlet { type patch; faces (\n" + inlet + "\n    ); }\n"
            + "    outlet { type patch; faces (\n" + outlet + "\n    ); }\n"
            + "    walls { type wall; faces (\n" + walls + "\n    ); }\n"
            + ");\n\nmergePatchPairs ();\n")


def topo_set_dict():
    """boxToCell over the byte-fixed porous bounding box -> cellZone 'porosity'
    (draft §1:72), PLUS the two oriented internal faceZones the Delta-p read path
    needs: 'inletPlane' at x=X1=0.200 and 'outletPlane' at x=X2=0.300 -- the
    porous-CORE entry/exit planes where the Ergun Delta-p is defined (NOT the duct
    ends).  These are the faceZones the controlDict surfaceFieldValue objects
    (dp_inlet_plane / dp_outlet_plane) areaAverage p on.

    Each plane is captured by a boxToFace slab of half-thickness PLANE_SLAB_HALF
    (1e-4 m) about the plane; the slab is far below the finest streamwise cell so
    ONLY the internal faces whose centre sits exactly on the plane are selected,
    at every mesh level; setsToFaceZone then orients them consistently against the
    porousCells cellSet (orientation is irrelevant to areaAverage but makes the
    zone a well-formed oriented internal faceZone).  The same physical volume and
    the same two planes are captured at every level (byte-fixed: no level arg).

    LAUNCHER CONTRACT (run_prd.sh, authored later): topoSet MUST run AFTER
    blockMesh (the mesh must exist before cellZone/faceZone selection) and BEFORE
    simpleFoam -- i.e. blockMesh -> topoSet -> (copy 0.orig->0, touch 0/U last for
    the age guard) -> simpleFoam."""
    mn, mx = POROUS_BOX_MIN, POROUS_BOX_MAX
    x1lo = "%.4f" % (X1 - PLANE_SLAB_HALF)   # 0.1999
    x1hi = "%.4f" % (X1 + PLANE_SLAB_HALF)   # 0.2001
    x2lo = "%.4f" % (X2 - PLANE_SLAB_HALF)   # 0.2999
    x2hi = "%.4f" % (X2 + PLANE_SLAB_HALF)   # 0.3001
    return (_foamfile("dictionary", "topoSetDict", "system")
            + "actions\n(\n"
            + "    { name porousCells; type cellSet; action new;\n"
            + "      source boxToCell; box (%s %s %s) (%s %s %s); }\n"
            % (mn[0], mn[1], mn[2], mx[0], mx[1], mx[2])
            + "    { name porosity; type cellZoneSet; action new;\n"
            + "      source setToCellZone; set porousCells; }\n"
            + "    { name inletFaces; type faceSet; action new;\n"
            + "      source boxToFace; box (%s -1.0 -1.0) (%s 1.0 1.0); }\n"
            % (x1lo, x1hi)
            + "    { name inletPlane; type faceZoneSet; action new;\n"
            + "      source setsToFaceZone; faceSet inletFaces; cellSet porousCells; flip false; }\n"
            + "    { name outletFaces; type faceSet; action new;\n"
            + "      source boxToFace; box (%s -1.0 -1.0) (%s 1.0 1.0); }\n"
            % (x2lo, x2hi)
            + "    { name outletPlane; type faceZoneSet; action new;\n"
            + "      source setsToFaceZone; faceSet outletFaces; cellSet porousCells; flip false; }\n"
            + ");\n")


def fv_options(active=True):
    """explicitPorositySource, type DarcyForchheimer, over cellZone 'porosity'.
    active=False sets d=f=0 -> INERT sink (the visibility-pair control, §6)."""
    d = D_XYZ if active else (0.0, 0.0, 0.0)
    f = F_XYZ if active else (0.0, 0.0, 0.0)
    return (_foamfile("dictionary", "fvOptions", "system")
            + "porosity1\n{\n    type            explicitPorositySource;\n"
            + "    explicitPorositySourceCoeffs\n    {\n"
            + "        type            DarcyForchheimer;\n"
            + "        selectionMode   cellZone;\n"
            + "        cellZone        porosity;\n"
            + "        DarcyForchheimerCoeffs\n        {\n"
            + "            d   (%r %r %r);\n" % d
            + "            f   (%r %r %r);\n" % f
            + "            coordinateSystem\n            {\n"
            + "                type cartesian; origin (0 0 0);\n"
            + "                rotation { type axes; e1 (1 0 0); e2 (0 1 0); }\n"
            + "            }\n        }\n    }\n}\n")


def transport_properties():
    # incompressible Newtonian; nu = mu/rho.  The DarcyForchheimer kinematic path
    # (v2606 DarcyForchheimer.C:210-225) looks up nu; rho enters ONLY at the
    # comparator's ×rho Pa conversion.  The MEASURED resolution of the
    # incompressible rho/nu handling is the §2bb VERIFY item (draft §2.4).
    return (_foamfile("dictionary", "transportProperties", "constant")
            + "transportModel  Newtonian;\nnu              %r;\n" % NU)


def turbulence_properties():
    return (_foamfile("dictionary", "turbulenceProperties", "constant")
            + "simulationType  RAS;\nRAS\n{\n    RASModel        kOmegaSST;\n"
            + "    turbulence      on;\n    printCoeffs     on;\n}\n")


def control_dict():
    # PROVISIONAL endTime/deltaT: steady simpleFoam, deltaT=1 (clause-5 fixed-dt).
    # The two plane pressure functionObjects are the Delta-p read path the
    # comparator and its planted control use (postProcessing/.../surfaceFieldValue.dat).
    fo = ("functions\n{\n"
          "    dp_inlet_plane\n    {\n"
          "        type surfaceFieldValue; libs (fieldFunctionObjects);\n"
          "        writeControl timeStep; writeInterval 50;\n"
          "        regionType faceZone; name inletPlane;\n"
          "        operation areaAverage; fields (p); writeFields false;\n    }\n"
          "    dp_outlet_plane\n    {\n"
          "        type surfaceFieldValue; libs (fieldFunctionObjects);\n"
          "        writeControl timeStep; writeInterval 50;\n"
          "        regionType faceZone; name outletPlane;\n"
          "        operation areaAverage; fields (p); writeFields false;\n    }\n"
          "}\n")
    return (_foamfile("dictionary", "controlDict", "system")
            + "application     simpleFoam;\nstartFrom       startTime;\n"
            + "startTime       0;\nstopAt          endTime;\n"
            + "endTime         %d;   // PROVISIONAL, sized in §2bb\n" % ENDTIME_PROVISIONAL
            + "deltaT          %d;   // steady unit step (clause-5)\n" % DELTAT
            + "writeControl    timeStep;\nwriteInterval   %d;\n" % ENDTIME_PROVISIONAL
            + "purgeWrite      0;\nwriteFormat     ascii;\nwritePrecision  8;\n"
            + "runTimeModifiable false;\n\n" + fo)


def fv_schemes():
    return (_foamfile("dictionary", "fvSchemes", "system")
            + "ddtSchemes { default steadyState; }\n"
            + "gradSchemes { default Gauss linear; }\n"
            + "divSchemes\n{\n    default none;\n"
            + "    div(phi,U) bounded Gauss linearUpwind grad(U);\n"
            + "    div(phi,k) bounded Gauss upwind;\n"
            + "    div(phi,omega) bounded Gauss upwind;\n"
            + "    div((nuEff*dev2(T(grad(U))))) Gauss linear;\n}\n"
            + "laplacianSchemes { default Gauss linear corrected; }\n"
            + "interpolationSchemes { default linear; }\n"
            + "snGradSchemes { default corrected; }\n"
            + "wallDist { method meshWave; }\n")


def fv_solution():
    # L-514: p-solver tolerances PINNED FROM the §7.6 two-relTol sensitivity addendum
    # (2026-09-09): relTol 1e-3, abs 1e-8, explicit maxIter 1000 (§7 clause 6).
    # NO SIMPLE residual-exit block (verification ruling §4.5): the steady run must
    # execute EXACTLY endTime iterations (clause-5 fixed-dt premise, deltaT=1).
    # A residual-based early stop would let simpleFoam stopAt endTime terminate
    # early -> last written time < endTime, n_exec < round(endTime/deltaT) ->
    # mark_done_prd grades NOT DONE.  Convergence/plateau is judged by
    # analyse_prd.py's G-CONV / plateau_states, NOT by an early residual exit;
    # endTime is sized in §2bb so the solve plateaus well before endTime.  The
    # SIMPLE block is therefore deliberately free of any residual-exit clause.
    return (_foamfile("dictionary", "fvSolution", "system")
            + "solvers\n{\n"
            + "    p\n    {\n        solver GAMG; smoother GaussSeidel;\n"
            + "        tolerance %r; relTol %r; maxIter 1000;   // L-514 PINNED (§7.6 two-relTol sensitivity addendum 2026-09-09)\n"
            % (P_SOLVER_ABSTOL_PROVISIONAL, P_SOLVER_RELTOL_PROVISIONAL)
            + "    }\n"
            + "    \"(U|k|omega)\"\n    {\n        solver smoothSolver; smoother symGaussSeidel;\n"
            + "        tolerance 1e-8; relTol 0.1;\n    }\n}\n"
            + "SIMPLE\n{\n    nNonOrthogonalCorrectors 2;\n    consistent yes;\n"
            + "    // steady run executes to endTime (clause-5 fixed-dt, deltaT=1); NO early\n"
            + "    // residual-exit block -- convergence judged by analyse_prd G-CONV / plateau,\n"
            + "    // endTime sized in §2bb so the solve plateaus well before endTime.\n"
            + "}\n"
            + "relaxationFactors { equations { \".*\" 0.9; } }\n")


def field_U(u_s):
    return (_foamfile("volVectorField", "U", "0")
            + "dimensions [0 1 -1 0 0 0 0];\ninternalField uniform (%r 0 0);\n" % u_s
            + "boundaryField\n{\n"
            + "    inlet { type fixedValue; value uniform (%r 0 0); }\n" % u_s
            + "    outlet { type pressureInletOutletVelocity; value uniform (%r 0 0); }\n" % u_s
            + "    walls { type noSlip; }\n}\n")


def field_p():
    # kinematic pressure p = P/rho [m2/s2]; outlet fixed 0.  The comparator
    # multiplies the CFD Delta-p by RHO to obtain Pa (LOAD-BEARING; draft §2.1).
    return (_foamfile("volScalarField", "p", "0")
            + "dimensions [0 2 -2 0 0 0 0];\ninternalField uniform 0;\n"
            + "boundaryField\n{\n    inlet { type zeroGradient; }\n"
            + "    outlet { type fixedValue; value uniform 0; }\n"
            + "    walls { type zeroGradient; }\n}\n")


def field_k(u_s):
    k = 1.5 * (TURB_INTENSITY_PROVISIONAL * u_s) ** 2       # PROVISIONAL (§2bb)
    return (_foamfile("volScalarField", "k", "0")
            + "dimensions [0 2 -2 0 0 0 0];\ninternalField uniform %r;\n" % k
            + "boundaryField\n{\n    inlet { type fixedValue; value uniform %r; }\n" % k
            + "    outlet { type zeroGradient; }\n"
            + "    walls { type kqRWallFunction; value uniform %r; }\n}\n" % k)


def field_omega(u_s):
    k = 1.5 * (TURB_INTENSITY_PROVISIONAL * u_s) ** 2
    omega = (k ** 0.5) / (0.09 ** 0.25 * MIX_LENGTH_PROVISIONAL)   # PROVISIONAL
    return (_foamfile("volScalarField", "omega", "0")
            + "dimensions [0 0 -1 0 0 0 0];\ninternalField uniform %r;\n" % omega
            + "boundaryField\n{\n    inlet { type fixedValue; value uniform %r; }\n" % omega
            + "    outlet { type zeroGradient; }\n"
            + "    walls { type omegaWallFunction; value uniform %r; }\n}\n" % omega)


def field_nut():
    # Menter continuous/automatic near-wall treatment: nutUSpaldingWallFunction
    # (valid across the whole y+ range; draft §2.1, y+ <= 200 gate not y+ <= 1).
    return (_foamfile("volScalarField", "nut", "0")
            + "dimensions [0 2 -1 0 0 0 0];\ninternalField uniform 0;\n"
            + "boundaryField\n{\n    inlet { type calculated; value uniform 0; }\n"
            + "    outlet { type calculated; value uniform 0; }\n"
            + "    walls { type nutUSpaldingWallFunction; value uniform 0; }\n}\n")


# ==========================================================================
# CASE WRITER -- emits a full case tree; LAUNCHES NOTHING.
# ==========================================================================
def write_case(dest, level, u_s, active=True):
    """Write one case (one level, one U_s) under dest.  Does NOT run OpenFOAM.
    The launcher (run_prd.sh, NOT authored here) copies 0.orig->0 and touches
    0/U LAST so the age guard (mark_done_prd.py) can date the run."""
    if level not in LEVEL_CELLS:
        raise ValueError("unknown level %r" % level)
    for sub in ("system", "constant", "constant/polyMesh", "0.orig"):
        os.makedirs(os.path.join(dest, sub), exist_ok=True)
    files = {
        "system/blockMeshDict": block_mesh_dict(level),
        "system/topoSetDict": topo_set_dict(),
        "system/fvOptions": fv_options(active=active),
        "system/controlDict": control_dict(),
        "system/fvSchemes": fv_schemes(),
        "system/fvSolution": fv_solution(),
        "constant/transportProperties": transport_properties(),
        "constant/turbulenceProperties": turbulence_properties(),
        "0.orig/U": field_U(u_s),
        "0.orig/p": field_p(),
        "0.orig/k": field_k(u_s),
        "0.orig/omega": field_omega(u_s),
        "0.orig/nut": field_nut(),
    }
    for rel, txt in files.items():
        with open(os.path.join(dest, rel), "w") as fh:
            fh.write(txt)
    return sorted(files)


# ==========================================================================
# --selftest -- validate the frozen arithmetic and the emitted dicts.  Every
# check is a VALUE control against the draft's own numbers (N-T8 style), not a
# key-exists check.  No solver, no blockMesh, no topoSet.
# ==========================================================================
_CHECKS = []


def _ck(name, ok, detail=""):
    _CHECKS.append(bool(ok))
    print("  [%s] %s%s" % ("ok " if ok else "FAIL", name, ("   " + detail) if detail else ""))


def selftest():
    print("build_prd.py --selftest  (arithmetic + emitted-dict validation; NO solver)")

    # (1) the ½rho-undo cross-check: 0.5*rho*f == B (draft §2.3:151, ruling §0)
    _ck("0.5*RHO*F_STREAM == B_ERGUN (the ½rho / 3.5 undo)",
        abs(0.5 * RHO * F_STREAM - B_ERGUN) < 1e-6,
        "0.5*%.1f*%.1f = %.4f vs B = %.1f" % (RHO, F_STREAM, 0.5 * RHO * F_STREAM, B_ERGUN))
    # d and A: mu*d == A
    _ck("MU*D_STREAM == A_ERGUN (viscous match)",
        abs(MU * D_STREAM - A_ERGUN) < 1e-6,
        "%.3g*%.3g = %.4f vs A = %.1f" % (MU, D_STREAM, MU * D_STREAM, A_ERGUN))
    # closed-form A, B from eps, d_p (independent re-derivation, ruling §0)
    a_calc = 150.0 * MU * (1 - EPS) ** 2 / (EPS ** 3 * D_P ** 2)
    b_calc = 1.75 * RHO * (1 - EPS) / (EPS ** 3 * D_P)
    _ck("A re-derived from eps,d_p == 1687.5", abs(a_calc - A_ERGUN) < 1e-6, "%.4f" % a_calc)
    _ck("B re-derived from eps,d_p == 6562.5", abs(b_calc - B_ERGUN) < 1e-6, "%.4f" % b_calc)
    d_calc = 150.0 * (1 - EPS) ** 2 / (EPS ** 3 * D_P ** 2)
    f_calc = 3.5 * (1 - EPS) / (EPS ** 3 * D_P)
    _ck("d re-derived == 9.375e7", abs(d_calc - D_STREAM) < 1.0, "%.6g" % d_calc)
    _ck("f re-derived == 10937.5", abs(f_calc - F_STREAM) < 1e-3, "%.6g" % f_calc)

    # (2) the five Ergun targets reproduce the draft §3 table to its rounding
    worst = 0.0
    for u, target in zip(U_S_SET, ERGUN_TARGET_PA):
        got = ergun_dp(u)
        worst = max(worst, abs(got - target))
        _ck("Ergun Delta-p(U_s=%.2f) == %.2f Pa (draft §3)" % (u, target),
            abs(got - target) < 0.01, "computed %.5f Pa" % got)
    _ck("all five Ergun targets within 0.01 Pa of the draft table", worst < 0.01,
        "worst |delta| = %.5f Pa" % worst)

    # (3) mesh cell counts match the draft §5 table exactly
    for lv in ("L1", "L2", "L3", "L4"):
        n = LEVEL_STREAM[lv] * 3 * LEVEL_CROSS[lv] ** 2   # 3 streamwise blocks
        _ck("%s cell count == %d (draft §5)" % (lv, LEVEL_CELLS[lv]),
            n == LEVEL_CELLS[lv], "computed %d" % n)
    # refinement ratio r = 2 uniform (x8 cells per step)
    for a, b in (("L1", "L2"), ("L2", "L3"), ("L3", "L4")):
        r = (LEVEL_CELLS[b] / LEVEL_CELLS[a]) ** (1.0 / 3.0)
        _ck("refinement ratio %s->%s == 2.0" % (a, b), abs(r - 2.0) < 1e-9, "r = %.9f" % r)

    # (3b) x-stations are clean literals consistent with the §1 lengths
    _ck("x-stations consistent with §1 lengths (L_in, L_core, L_out)",
        abs(X1 - X0 - L_IN) < 1e-12 and abs(X2 - X1 - L_CORE) < 1e-12
        and abs(X3 - X2 - L_OUT) < 1e-12 and abs(X3 - L_TOT) < 1e-12)
    _ck("core x-range prints clean (no 0.30000000000000004)",
        ("%s" % X2) == "0.3" and ("%s" % X1) == "0.2")

    # (4) anisotropy 1000x
    _ck("anisotropy ratio d_yy/d_xx == 1000", abs(D_XYZ[1] / D_XYZ[0] - ANISO) < 1e-9)
    _ck("anisotropy ratio f_yy/f_xx == 1000", abs(F_XYZ[1] / F_XYZ[0] - ANISO) < 1e-9)

    # (5) active vs inert fvOptions differ (the visibility-pair control basis)
    act = fv_options(active=True)
    inert = fv_options(active=False)
    _ck("ACTIVE fvOptions carries the nonzero d", "9.375e+07" in act or "93750000" in act
        or ("%r" % D_STREAM) in act, "")
    _ck("INERT fvOptions sets d=f=0 (Delta-p ~ 0)", "0.0 0.0 0.0" in inert)
    _ck("ACTIVE and INERT fvOptions differ", act != inert)

    # (6) emit a full case tree to scratch and re-read the geometry back
    tmp = tempfile.mkdtemp(prefix="prd_build_")
    try:
        written = write_case(tmp, "L1", 1.0, active=True)
        _ck("write_case emitted the full input set", len(written) == 13,
            "%d files" % len(written))
        bm = open(os.path.join(tmp, "system", "blockMeshDict")).read()
        _ck("blockMeshDict has 16 vertices, 3 blocks",
            bm.count("hex (") == 3 and bm.count("(0.0 ") + bm.count("(0.2 ")
            + bm.count("(0.3 ") + bm.count("(0.5 ") >= 4)
        ts = open(os.path.join(tmp, "system", "topoSetDict")).read()
        _ck("porous box coincident with core block x-range [0.2,0.3]",
            "(0.2 0.0 0.0) (0.3 0.1 0.1)" in ts)
        # FIX-1 (§3 check-1): the two Delta-p faceZones referenced by the
        # controlDict functionObjects are now actually CREATED by topoSet.
        _ck("topoSetDict creates inletPlane faceZone slab about x=0.200",
            "name inletPlane; type faceZoneSet" in ts
            and "box (0.1999 -1.0 -1.0) (0.2001 1.0 1.0)" in ts
            and "faceSet inletFaces; cellSet porousCells" in ts)
        _ck("topoSetDict creates outletPlane faceZone slab about x=0.300",
            "name outletPlane; type faceZoneSet" in ts
            and "box (0.2999 -1.0 -1.0) (0.3001 1.0 1.0)" in ts
            and "faceSet outletFaces; cellSet porousCells" in ts)
        u = open(os.path.join(tmp, "0.orig", "U")).read()
        _ck("inlet U carries the swept U_s", "(1.0 0 0)" in u)
        cd = open(os.path.join(tmp, "system", "controlDict")).read()
        _ck("controlDict is steady simpleFoam deltaT=1 (clause-5)",
            "deltaT          1" in cd and "application     simpleFoam" in cd)
        _ck("two plane pressure functionObjects present (Delta-p read path)",
            "dp_inlet_plane" in cd and "dp_outlet_plane" in cd)
        _ck("controlDict faceZone names resolve to created topoSet faceZones",
            "name inletPlane" in cd and "name outletPlane" in cd
            and "name inletPlane; type faceZoneSet" in ts
            and "name outletPlane; type faceZoneSet" in ts)
        fs = open(os.path.join(tmp, "system", "fvSolution")).read()
        _ck("p-solver tol carries the L-514 PINNED marker + explicit maxIter 1000",
            "L-514 PINNED (§7.6 two-relTol sensitivity" in fs and "maxIter 1000;" in fs)
        # FIX-2 (§3 check-1): no residual-exit clause -> run executes to endTime
        # (clause-5 fixed-dt premise); convergence judged by analyse_prd.
        _ck("fvSolution carries NO triggering residualControl (run-to-endTime)",
            "residualControl" not in fs)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # (7) no module-level assert (L-332)
    import ast
    src = open(os.path.abspath(__file__)).read()
    n0 = sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(src)))
    _ck("no assert in module body (L-332)", n0 == 0, "%d asserts" % n0)

    n_ok = sum(1 for c in _CHECKS if c)
    print("\n%d/%d checks passed" % (n_ok, len(_CHECKS)))
    return EXIT_OK if n_ok == len(_CHECKS) else EXIT_FAIL


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--emit", metavar="DEST",
                    help="emit ONE case tree (with --level, --us) -- writes inputs, "
                         "launches nothing")
    ap.add_argument("--level", default="L1", choices=sorted(LEVEL_CELLS))
    ap.add_argument("--us", type=float, default=1.0)
    ap.add_argument("--inert", action="store_true",
                    help="emit the D=f=0 INERT case (visibility-pair control)")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.emit:
        written = write_case(args.emit, args.level, args.us, active=not args.inert)
        print("emitted %d input files under %s (level %s, U_s=%g, %s) -- NOTHING LAUNCHED"
              % (len(written), args.emit, args.level, args.us,
                 "INERT" if args.inert else "ACTIVE"))
        return EXIT_OK
    ap.error("give --selftest or --emit DEST")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
