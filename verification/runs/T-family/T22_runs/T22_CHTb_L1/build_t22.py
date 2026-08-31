#!/usr/bin/env python3
"""BUILD ONLY -- Case 3 variant (b) annulus, L1, three regions.  LAUNCHES NOTHING.

Sanaa's directive `etc/sessions/2026-08-30T2300Z_sanaa_four_new_case_families.md`
sections 3.2-3.5, variant (b): actuator disk ABSENT, annulus velocity imposed by
U_inf.  One benign operating point, P_loss = 300 W, U_inf = 20 m/s.

This script writes the case tree and (phase A) drives blockMesh /
splitMeshRegions / checkMesh, which are MESHING AND INSPECTION utilities and not
solves.  It never invokes chtMultiRegionSimpleFoam.

DECLARED SCOPE LIMITS, in the case rather than in a report:
  * The nose and tail cones of directive 3.2 are REMOVED.  The centrebody is a
    constant-radius r_o = 0.0375 m tube over the whole axial extent; only its
    middle 0.125 m is the conjugate housing.  Upstream and downstream of the
    housing the same radius is a plain adiabatic wall.  This is the "plain
    annular duct" the brief asked for: no blunt faces, no separation, no second
    conduction path.
  * The duct wall is adiabatic (directive 3.3, "adiabatic for the duct itself").
  * Radiation OFF, radiationModel none in all three regions (directive 3.3, a
    disclosed omission).
  * g = (0 0 0).  See the note in write_g().
"""
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"

# ----------------------------------------------------------------- geometry
D_DUCT = 0.25            # m, duct diameter                    [REGISTERED-by-owner, directive 3.2]
R_DUCT = D_DUCT / 2.0    # 0.125 m
R_O = 0.3 * D_DUCT / 2.0  # 0.0375 m, housing outer radius
WALL_T = 0.004           # m, housing wall thickness
R_I = R_O - WALL_T       # 0.0335 m
L_HOUS = 0.5 * D_DUCT    # 0.125 m, housing length

# axial stations, m.  z = 0 is the housing leading edge.
Z0, Z1, Z2, Z3 = -0.250, 0.0, L_HOUS, 0.500
# radial stations, m
# R0 IS A SHAFT BORE, NOT THE AXIS.  MEASURED REASON, not a preference: the first
# build put the core block on the axis with a collapsed edge, and
# `checkMesh -region core` on that mesh returned THREE failures --
#   ***Zero or negative face area detected.  Minimum area: 0
#   ***Max skewness = 9.2966987286e+146, 140 highly skew faces
#   ***Total number of faces on empty patches is not divisible by nCells
# -- while fluid and housing were "Mesh OK" on the same run.  The 140 zero-area
# faces are the degenerate axis faces of the 140 axial cells.  A 6 mm shaft bore
# with an adiabatic wall removes the degeneracy entirely, is what a real motor
# has, and does NOT change the source power: `volumeMode absolute` makes
# OpenFOAM divide the entered watts by the volume IT measures, so V_core is
# never a hand-typed number in this case.
R_BORE = 0.006
R0, R1, R2 = R_BORE, R_I, R_O
R3 = 0.0475              # fluid inner boundary-layer band outer edge
R4 = 0.1150              # fluid outer boundary-layer band inner edge
R5 = R_DUCT

WEDGE_TOTAL_DEG = 5.0
HALF = math.radians(WEDGE_TOTAL_DEG / 2.0)

# ----------------------------------------------------------------- mesh (L1)
NR_BL_IN, GR_BL_IN = 40, 40.0     # fluid inner BL: 40 cells, last/first = 40
NR_MID, GR_MID = 40, 1.0          # fluid core band
NR_BL_OUT, GR_BL_OUT = 30, 1.0 / 40.0   # fluid outer BL, contracting to the duct wall
NR_HOUS = 8                       # >= 8 across the 4 mm wall (directive 3.5)
NR_CORE = 24
NZ_UP, NZ_MID, NZ_DOWN = 80, 140, 100

# ------------------------------------------------------------- operating point
P_LOSS = 300.0           # W, FULL 360-degree motor loss       [REGISTERED-by-owner, directive 3.3]
U_INF = 20.0             # m/s                                  [REGISTERED-by-owner, directive 3.3]
T_INF = 288.0            # K
P_ABS = 1.0e5            # Pa, absolute reference pressure      [ASSUMED]
# THE WEDGE POWER FACTOR.  The wedge is WEDGE_TOTAL_DEG/360 of the motor, so the
# source that must be entered is the SECTOR's share.  Computed here once, from
# the same HALF that generates the mesh -- never typed twice.
P_SECTOR = P_LOSS * (2.0 * HALF) / (2.0 * math.pi)

# air, directive 3.3
RHO_AIR, CP_AIR, K_AIR, MU_AIR = 1.2, 1005.0, 0.026, 1.8e-5
PR_AIR = MU_AIR * CP_AIR / K_AIR          # 0.695769..., so k is EXACTLY 0.026
MW_AIR = 28.9                             # only used by specie bookkeeping under rhoConst
# aluminium housing, directive 3.3
RHO_AL, CP_AL, K_AL = 2700.0, 900.0, 167.0
# core, directive 3.2 (declared representative, not any real motor's)
RHO_CO, CP_CO, K_CO = 7000.0, 450.0, 40.0

# inlet turbulence
TI = 0.05
K_IN = 1.5 * (U_INF * TI) ** 2
DH = D_DUCT - 2.0 * R_O                   # hydraulic diameter of the annulus, m
L_TURB = 0.07 * DH
OMEGA_IN = math.sqrt(K_IN) / (0.09 ** 0.25 * L_TURB)

N_ITER = 5000

HDR = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2606                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       %(cls)s;
%(loc)s    object      %(obj)s;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
"""


def w(relpath, cls, obj, body, location=None):
    p = os.path.join(HERE, relpath)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    loc = '    location    "%s";\n' % location if location else ""
    with open(p, "w") as f:
        f.write(HDR % dict(cls=cls, obj=obj, loc=loc))
        f.write("\n")
        f.write(body.rstrip() + "\n\n")
        f.write("// *********************************************************"
                "**************** //\n")
    return p


# =========================================================== blockMeshDict
def build_block_mesh_dict():
    """Eleven blocks.  The core block reaches the axis with a collapsed edge."""
    verts, vindex = [], {}

    def V(r, z, side):
        """side: 0 = back (-x), 1 = front (+x).  At r = 0 both coincide."""
        key = (round(r, 12), round(z, 12), side)
        if key in vindex:
            return vindex[key]
        x = (1 if side else -1) * r * math.sin(HALF)
        y = r * math.cos(HALF)
        vindex[key] = len(verts)
        verts.append((x, y, z))
        return vindex[key]

    blocks, faces = [], {}

    def add(ra, rb, za, zb, nr, nz, gr, zone):
        v = [V(ra, za, 0), V(rb, za, 0), V(rb, zb, 0), V(ra, zb, 0),
             V(ra, za, 1), V(rb, za, 1), V(rb, zb, 1), V(ra, zb, 1)]
        blocks.append((v, nr, nz, gr, zone))
        i = len(blocks) - 1
        # face vertex orderings derived so each normal points OUT of the block
        faces[(i, "zmin")] = (v[0], v[1], v[5], v[4])
        faces[(i, "zmax")] = (v[3], v[7], v[6], v[2])
        faces[(i, "rmin")] = (v[0], v[4], v[7], v[3])
        faces[(i, "rmax")] = (v[1], v[2], v[6], v[5])
        faces[(i, "back")] = (v[0], v[3], v[2], v[1])
        faces[(i, "front")] = (v[4], v[5], v[6], v[7])
        return i

    #                 ra  rb  za  zb   nr         nz        grading      zone
    B_up_bl = add(R2, R3, Z0, Z1, NR_BL_IN, NZ_UP, GR_BL_IN, "fluid")
    B_up_md = add(R3, R4, Z0, Z1, NR_MID, NZ_UP, GR_MID, "fluid")
    B_up_ot = add(R4, R5, Z0, Z1, NR_BL_OUT, NZ_UP, GR_BL_OUT, "fluid")

    B_co = add(R0, R1, Z1, Z2, NR_CORE, NZ_MID, 1.0, "core")
    B_ho = add(R1, R2, Z1, Z2, NR_HOUS, NZ_MID, 1.0, "housing")
    B_md_bl = add(R2, R3, Z1, Z2, NR_BL_IN, NZ_MID, GR_BL_IN, "fluid")
    B_md_md = add(R3, R4, Z1, Z2, NR_MID, NZ_MID, GR_MID, "fluid")
    B_md_ot = add(R4, R5, Z1, Z2, NR_BL_OUT, NZ_MID, GR_BL_OUT, "fluid")

    B_dn_bl = add(R2, R3, Z2, Z3, NR_BL_IN, NZ_DOWN, GR_BL_IN, "fluid")
    B_dn_md = add(R3, R4, Z2, Z3, NR_MID, NZ_DOWN, GR_MID, "fluid")
    B_dn_ot = add(R4, R5, Z2, Z3, NR_BL_OUT, NZ_DOWN, GR_BL_OUT, "fluid")

    allb = range(len(blocks))
    patches = [
        ("inlet", "patch", [(B_up_bl, "zmin"), (B_up_md, "zmin"), (B_up_ot, "zmin")]),
        ("outlet", "patch", [(B_dn_bl, "zmax"), (B_dn_md, "zmax"), (B_dn_ot, "zmax")]),
        ("duct_wall", "wall", [(B_up_ot, "rmax"), (B_md_ot, "rmax"), (B_dn_ot, "rmax")]),
        ("centrebody_up", "wall", [(B_up_bl, "rmin")]),
        ("centrebody_down", "wall", [(B_dn_bl, "rmin")]),
        ("housing_ends", "wall", [(B_ho, "zmin"), (B_ho, "zmax")]),
        ("core_ends", "wall", [(B_co, "zmin"), (B_co, "zmax")]),
        ("core_bore", "wall", [(B_co, "rmin")]),
        ("front", "wedge", [(i, "front") for i in allb]),
        ("back", "wedge", [(i, "back") for i in allb]),
    ]

    L = ["scale   1;", "", "vertices", "("]
    for x, y, z in verts:
        L.append("    (%.12g %.12g %.12g)" % (x, y, z))
    L += [");", "", "blocks", "("]
    for v, nr, nz, gr, zone in blocks:
        L.append("    hex (%s) %s (%d %d 1) simpleGrading (%.12g 1 1)"
                 % (" ".join(str(i) for i in v), zone, nr, nz, gr))
    L += [");", "", "edges", "(", ");", "", "boundary", "("]
    for name, ptype, fl in patches:
        L += ["    %s" % name, "    {", "        type            %s;" % ptype,
              "        faces", "        ("]
        for bi, side in fl:
            L.append("            (%s)" % " ".join(str(i) for i in faces[(bi, side)]))
        L += ["        );", "    }", ""]
    L += [");", "", "mergePatchPairs", "(", ");"]
    return "\n".join(L)


# ================================================================ constants
def write_g():
    """g = (0 0 0) -- REGISTERED CHOICE, with the reason in the file.

    The chtMultiRegion family reads constant/g UNCONDITIONALLY at file scope
    (createFluidFields.H:35, before the fluid loop opens at :38), so this file
    must exist whenever a fluid region does.  Its VALUE is zero here because:
      (1) a wedge is axisymmetric by construction and a gravity vector with any
          RADIAL component is inconsistent with that symmetry -- it would make
          the single wedge sector unrepresentative of the annulus;
      (2) an AXIAL gravity would model a vertically-mounted duct, which the
          directive does not specify;
      (3) the fluid uses equationOfState rhoConst at rho = 1.2 kg/m3, so density
          does not respond to temperature and buoyancy is absent from the
          equations regardless of g.  Directive 3.3 states the flow is
          "Boussinesq-free since forced convection dominates".
    The Richardson number that justifies (3) is computed in the build report."""
    w("constant/g", "uniformDimensionedVectorField", "g",
      "dimensions      [0 1 -2 0 0 0 0];\n\nvalue           (0 0 0);",
      location="constant")


def write_region_properties():
    w("constant/regionProperties", "dictionary", "regionProperties",
      "regions\n(\n    fluid       (fluid)\n    solid       (housing core)\n);",
      location="constant")


def write_fluid_thermo():
    w("constant/fluid/thermophysicalProperties", "dictionary",
      "thermophysicalProperties", """thermoType
{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState rhoConst;
    specie          specie;
    energy          sensibleEnthalpy;
}

// Directive 3.3: rho 1.2, cp 1005, k 0.026, mu 1.8e-5 -- CONSTANT properties.
// Pr is DERIVED as mu*cp/k so that k is EXACTLY 0.026 W/mK rather than a
// rounded 0.7 giving k = 0.02585.
mixture
{
    specie
    {
        molWeight       %(mw).6g;
    }
    thermodynamics
    {
        Cp              %(cp).10g;
        Hf              0;
    }
    transport
    {
        mu              %(mu).10g;
        Pr              %(pr).12g;
    }
    equationOfState
    {
        rho             %(rho).10g;
    }
}""" % dict(mw=MW_AIR, cp=CP_AIR, mu=MU_AIR, pr=PR_AIR, rho=RHO_AIR),
      location="constant/fluid")


def write_solid_thermo(region, rho, cp, kappa, mw):
    w("constant/%s/thermophysicalProperties" % region, "dictionary",
      "thermophysicalProperties", """thermoType
{
    type            heSolidThermo;
    mixture         pureMixture;
    transport       constIso;
    thermo          hConst;
    equationOfState rhoConst;
    specie          specie;
    energy          sensibleEnthalpy;
}

mixture
{
    specie
    {
        molWeight       %(mw).6g;
    }
    transport
    {
        kappa           %(k).10g;
    }
    thermodynamics
    {
        Hf              0;
        Cp              %(cp).10g;
    }
    equationOfState
    {
        rho             %(rho).10g;
    }
}""" % dict(mw=mw, k=kappa, cp=cp, rho=rho),
      location="constant/%s" % region)


def write_turbulence():
    w("constant/fluid/turbulenceProperties", "dictionary", "turbulenceProperties",
      "simulationType  RAS;\n\nRAS\n{\n    RASModel        kOmegaSST;\n"
      "    turbulence      on;\n    printCoeffs     on;\n}",
      location="constant/fluid")


def write_radiation(region):
    w("constant/%s/radiationProperties" % region, "dictionary",
      "radiationProperties",
      "// Directive 3.3: radiation OFF and DISCLOSED.\nradiation       off;\n"
      "radiationModel  none;", location="constant/%s" % region)


def write_fv_options():
    """THE HEAT SOURCE.  Three corrections to directive 3.3, each checked against
    the installed v2606 tree and cited in the file:

    1. FIELD `h`, NOT `T`.  The solid energy equation is in ENTHALPY:
       chtMultiRegionSimpleFoam/solid/solveSolid.H:4-9 builds
           fvScalarMatrix hEqn(-thermo.heatDiffusion(betav, h) == fvOptions(rho, h));
       An entry on `T` is never matched to that equation and is NEVER APPLIED.
       OpenFOAM emits one non-fatal warning (fvOption.C:134-146,
       "defined for field T but never used") at exactly one iteration
       (fvOptionList.C:72,88 -- timeIndex == startTimeIndex + 2) and the run then
       converges cleanly to a uniform-temperature solid.  That is a SILENT ZERO
       SOURCE and it is what CLAUDE.md standing rule 3 exists for.
       THERMAL_K0_runs/K0a_heated_box_source/constant/fvOptions:31 uses `T`
       CORRECTLY, because that case runs a kinematic-T solver; copied into a
       solid region it reproduces the silent zero.

    2. `injectionRate` DOES NOT EXIST at v2606.  SemiImplicitSource.H accepts
       `sources { <field> (Su Sp); }` (2206+, :59-83) or the legacy
       `injectionRateSuSp` (:86-104).  grep over src/fvOptions returns four hits,
       all `injectionRateSuSp`.

    3. `volumeMode` IS MANDATORY AND DECIDES THE UNITS.  SemiImplicitSource.C:534
       does `volumeModeTypeNames_.get("volumeMode", coeffs_)` -- a missing key is
       a fatal read.  :537-540 sets `VDash_ = V_` for `absolute`, and every value
       is divided by VDash_ (:500, :516).  The wrong mode is a SILENT scale error
       by exactly the zone volume.  `absolute` is used here so the entered number
       is in WATTS and OpenFOAM divides by the volume IT measured
       (cellSetOption.C:145-157), which is the same volume a heat balance would
       audit against.  cellSetOption.C:166-168 PRINTS that volume to the log.

    4. THE WEDGE POWER FACTOR.  Directive 3.3's P_loss is the FULL 360-degree
       motor loss.  This case is a 5-degree sector, so the source entered is
       P_loss * theta/(2 pi).  Computed once from the same HALF that builds the
       mesh."""
    w("constant/core/fvOptions", "dictionary", "fvOptions", """// Uniform volumetric loss in the motor core.  See build_t22.py:write_fv_options
// for the four corrections to directive 3.3 that produced this dictionary and
// for the v2606 file:line citation behind each one.
//
//   P_loss (FULL 360 deg motor) = %(pfull).10g W        [REGISTERED-by-owner, directive 3.3]
//   wedge angle                 = %(deg).10g deg
//   P_sector = P_loss * theta/(2 pi) = %(psec).12g W    [DERIVED]
//
// volumeMode absolute => the value below is the TOTAL power over the selected
// cells, in W.  OpenFOAM divides by the volume it measures itself.
// The field is `h` (enthalpy), NOT `T`.  An entry on `T` is silently ignored.

motorLoss
{
    type            scalarSemiImplicitSource;
    active          yes;
    selectionMode   all;
    volumeMode      absolute;
    sources
    {
        h           (%(psec).12g 0);
    }
}""" % dict(pfull=P_LOSS, deg=WEDGE_TOTAL_DEG, psec=P_SECTOR),
      location="constant/core")


# ================================================================== system
def write_control_dict():
    w("system/controlDict", "dictionary", "controlDict", """application     chtMultiRegionSimpleFoam;

startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         %(n)d;
deltaT          1;

writeControl    timeStep;
writeInterval   %(n)d;
purgeWrite      0;

// writePrecision 12, NOT the default 6.  At T ~ 288 K, six significant figures
// leave a 1 mK write quantum, which is larger than the temperature differences
// this case family gates on.  See docs/campaigns/T-family/T21_PREREGISTRATION.md
// section 2.4.
writeFormat     ascii;
writePrecision  12;
writeCompression off;
timeFormat      general;
timePrecision   12;
runTimeModifiable false;

maxCo           1;

// INSTRUMENTS.  Every operation name below was read out of
// surfaceFieldValue.C:77-104 before this file was written, because a function
// object with an unknown operation aborts at CONSTRUCTION and would throw away
// the whole solve.
//
// Heat balance, exact for constant c_p:
//     H_out - H_in = c_p * ( sum_outlet(phi_f T_f) + sum_inlet(phi_f T_f) )
// phi is the MASS flux [kg/s] and is NEGATIVE on an inflow face, so the two
// weightedSum rows ADD rather than subtract.  That must equal the registered
// source power, %(psec).12g W.
functions
{
    inlet_mdot
    {
        type            surfaceFieldValue;
        libs            (fieldFunctionObjects);
        region          fluid;
        regionType      patch;
        name            inlet;
        operation       sum;
        fields          (phi);
        writeControl    timeStep;
        writeInterval   100;
        writeFields     false;
        log             false;
    }
    outlet_mdot
    {
        $inlet_mdot;
        name            outlet;
    }
    inlet_phiT
    {
        $inlet_mdot;
        name            inlet;
        operation       weightedSum;
        weightField     phi;
        fields          (T);
    }
    outlet_phiT
    {
        $inlet_phiT;
        name            outlet;
    }
    housing_T
    {
        type            fieldMinMax;
        libs            (fieldFunctionObjects);
        region          housing;
        mode            magnitude;
        fields          (T);
        writeControl    timeStep;
        writeInterval   100;
        log             false;
    }
    core_T
    {
        $housing_T;
        region          core;
    }
    fluid_T
    {
        $housing_T;
        region          fluid;
    }
}
""" % dict(n=N_ITER, psec=P_SECTOR), location="system")


TOP_SCHEMES = """ddtSchemes      { default steadyState; }
gradSchemes     { default Gauss linear; }
divSchemes      { default none; }
laplacianSchemes{ default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes   { default corrected; }"""

TOP_SOLUTION = """solvers { }"""

FLUID_SCHEMES = """ddtSchemes
{
    default         steadyState;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default         none;
    div(phi,U)      bounded Gauss linearUpwind grad(U);
    div(phi,K)      bounded Gauss upwind;
    div(phi,h)      bounded Gauss upwind;
    div(phi,k)      bounded Gauss upwind;
    div(phi,omega)  bounded Gauss upwind;
    div(phid,p)     bounded Gauss upwind;
    div(((rho*nuEff)*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}

wallDist
{
    method          meshWave;
    nRequired       false;
}"""

FLUID_SOLUTION = """solvers
{
    rho
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-08;
        relTol          0;
    }

    p_rgh
    {
        solver          GAMG;
        tolerance       1e-08;
        relTol          0.01;
        smoother        GaussSeidel;
    }

    "(U|h|k|omega)"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-09;
        relTol          0.01;
    }
}

SIMPLE
{
    momentumPredictor true;
    nNonOrthogonalCorrectors 0;
    frozenFlow      false;
    // NO residualControl: an early exit leaves the last time directory below
    // endTime and CLAUDE.md rule 4 conjunct 3 then fails.  Convergence is an
    // assertion on the log, never a stopping rule.
}

relaxationFactors
{
    fields
    {
        p_rgh           0.3;
        rho             1;
    }
    equations
    {
        U               0.7;
        h               0.7;
        "(k|omega)"     0.7;
    }
}"""

SOLID_SCHEMES = """ddtSchemes      { default steadyState; }
gradSchemes     { default Gauss linear; }
divSchemes      { default none; }
laplacianSchemes{ default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes   { default corrected; }"""

SOLID_SOLUTION = """solvers
{
    h
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-12;
        relTol          0;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 0;
}

relaxationFactors
{
    equations
    {
        h               1;
    }
}"""


# ================================================================== fields
def field(region, obj, dims, internal, patches):
    body = ["dimensions      %s;" % dims, "",
            "internalField   uniform %s;" % internal, "",
            "boundaryField", "{",
            "    #includeEtc \"caseDicts/setConstraintTypes\""]
    for name, spec in patches:
        body.append("    %s" % name)
        body.append("    {")
        for line in spec:
            body.append("        %s" % line)
        body.append("    }")
    body.append("}")
    cls = "volVectorField" if internal.startswith("(") else "volScalarField"
    w("0.orig/%s/%s" % (region, obj), cls, obj, "\n".join(body),
      location='"0.orig/%s"' % region)


def write_fluid_fields(pw):
    """pw: the actual fluid->housing coupled patch name, read off the split mesh."""
    walls = ["duct_wall", "centrebody_up", "centrebody_down", pw]

    field("fluid", "U", "[0 1 -1 0 0 0 0]", "(0 0 %.10g)" % U_INF,
          [("inlet", ["type            fixedValue;",
                      "value           uniform (0 0 %.10g);" % U_INF]),
           ("outlet", ["type            inletOutlet;",
                       "inletValue      uniform (0 0 0);",
                       "value           $internalField;"])]
          + [(p, ["type            noSlip;"]) for p in walls])

    field("fluid", "p_rgh", "[1 -1 -2 0 0 0 0]", "%.10g" % P_ABS,
          [("inlet", ["type            zeroGradient;"]),
           ("outlet", ["type            fixedValue;",
                       "value           uniform %.10g;" % P_ABS])]
          + [(p, ["type            fixedFluxPressure;",
                  "value           $internalField;"]) for p in walls])

    field("fluid", "p", "[1 -1 -2 0 0 0 0]", "%.10g" % P_ABS,
          [(p, ["type            calculated;", "value           $internalField;"])
           for p in ["inlet", "outlet"] + walls])

    field("fluid", "T", "[0 0 0 1 0 0 0]", "%.10g" % T_INF,
          [("inlet", ["type            fixedValue;",
                      "value           uniform %.10g;" % T_INF]),
           ("outlet", ["type            inletOutlet;",
                       "inletValue      uniform %.10g;" % T_INF,
                       "value           $internalField;"]),
           # directive 3.3: only the housing is conjugate; the duct is adiabatic
           ("duct_wall", ["type            zeroGradient;"]),
           ("centrebody_up", ["type            zeroGradient;"]),
           ("centrebody_down", ["type            zeroGradient;"]),
           (pw, ["type            compressible::turbulentTemperatureRadCoupledMixed;",
                 "Tnbr            T;",
                 "qrNbr           none;",
                 "qr              none;",
                 "kappaMethod     fluidThermo;",
                 "useImplicit     true;",
                 "value           $internalField;"])])

    field("fluid", "k", "[0 2 -2 0 0 0 0]", "%.10g" % K_IN,
          [("inlet", ["type            fixedValue;",
                      "value           uniform %.10g;" % K_IN]),
           ("outlet", ["type            inletOutlet;",
                       "inletValue      uniform %.10g;" % K_IN,
                       "value           $internalField;"])]
          + [(p, ["type            kLowReWallFunction;",
                  "value           $internalField;"]) for p in walls])

    field("fluid", "omega", "[0 0 -1 0 0 0 0]", "%.10g" % OMEGA_IN,
          [("inlet", ["type            fixedValue;",
                      "value           uniform %.10g;" % OMEGA_IN]),
           ("outlet", ["type            inletOutlet;",
                       "inletValue      uniform %.10g;" % OMEGA_IN,
                       "value           $internalField;"])]
          + [(p, ["type            omegaWallFunction;",
                  "value           $internalField;"]) for p in walls])

    field("fluid", "nut", "[0 2 -1 0 0 0 0]", "0",
          [("inlet", ["type            calculated;", "value           uniform 0;"]),
           ("outlet", ["type            calculated;", "value           uniform 0;"])]
          + [(p, ["type            nutLowReWallFunction;",
                  "value           uniform 0;"]) for p in walls])

    field("fluid", "alphat", "[1 -1 -1 0 0 0 0]", "0",
          [("inlet", ["type            calculated;", "value           uniform 0;"]),
           ("outlet", ["type            calculated;", "value           uniform 0;"])]
          + [(p, ["type            compressible::alphatWallFunction;",
                  "Prt             0.85;",
                  "value           uniform 0;"]) for p in walls])


def write_solid_fields(region, adiabatic, coupled):
    cpl = []
    for p in coupled:
        cpl.append((p, ["type            compressible::turbulentTemperatureRadCoupledMixed;",
                        "Tnbr            T;",
                        "qrNbr           none;",
                        "qr              none;",
                        "kappaMethod     solidThermo;",
                        "useImplicit     true;",
                        "value           $internalField;"]))
    field(region, "T", "[0 0 0 1 0 0 0]", "%.10g" % T_INF,
          [(p, ["type            zeroGradient;"]) for p in adiabatic] + cpl)
    field(region, "p", "[1 -1 -2 0 0 0 0]", "%.10g" % P_ABS,
          [(p, ["type            zeroGradient;"]) for p in adiabatic + coupled])


# ============================================================ mesh utilities
def foam(cmd, log):
    """Run one OpenFOAM MESHING/INSPECTION utility.  Never a solver."""
    banned = ("Foam", "chtMultiRegion", "simpleFoam", "solidFoam")
    tool = cmd.split()[0]
    if any(tool.endswith(b) or tool == b for b in ("chtMultiRegionSimpleFoam",
                                                   "chtMultiRegionFoam",
                                                   "solidFoam", "simpleFoam")):
        raise SystemExit("REFUSE: build_t22.py never launches a solver (%s)" % tool)
    full = "set -o pipefail; . %s >/dev/null 2>&1; cd %s && %s > %s 2>&1" % (
        FOAM_BASHRC, HERE, cmd, log)
    r = subprocess.run(["bash", "-c", full], capture_output=True, text=True)
    return r.returncode


def read_patch_names(region):
    p = os.path.join(HERE, "constant", region, "polyMesh", "boundary")
    names = []
    with open(p) as f:
        txt = f.read()
    depth, i, cur = 0, 0, None
    import re
    body = txt[txt.index(")", txt.index("(")) if False else 0:]
    # simple structural scan: a word at brace-depth 1 that is followed by '{'
    toks = re.findall(r'[A-Za-z_][A-Za-z0-9_.:-]*|[{}();]', txt)
    depth = 0
    prev = None
    for t in toks:
        if t == "{":
            if depth == 1 and prev:
                names.append(prev)
            depth += 1
        elif t == "}":
            depth -= 1
        elif t == "(":
            depth += 1
        elif t == ")":
            depth -= 1
        else:
            prev = t
    return names


# ==================================================================== main
def main():
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"

    if phase in ("all", "A"):
        w("system/blockMeshDict", "dictionary", "blockMeshDict",
          build_block_mesh_dict(), location="system")
        write_control_dict()
        w("system/fvSchemes", "dictionary", "fvSchemes", TOP_SCHEMES, location="system")
        w("system/fvSolution", "dictionary", "fvSolution", TOP_SOLUTION, location="system")
        for reg, sch, sol in (("fluid", FLUID_SCHEMES, FLUID_SOLUTION),
                              ("housing", SOLID_SCHEMES, SOLID_SOLUTION),
                              ("core", SOLID_SCHEMES, SOLID_SOLUTION)):
            w("system/%s/fvSchemes" % reg, "dictionary", "fvSchemes", sch,
              location="system/%s" % reg)
            w("system/%s/fvSolution" % reg, "dictionary", "fvSolution", sol,
              location="system/%s" % reg)
        write_g()
        write_region_properties()
        write_fluid_thermo()
        write_solid_thermo("housing", RHO_AL, CP_AL, K_AL, 26.98)
        write_solid_thermo("core", RHO_CO, CP_CO, K_CO, 55.85)
        write_turbulence()
        for reg in ("fluid", "housing", "core"):
            write_radiation(reg)
        write_fv_options()
        print("phase A: dictionaries written")

    if phase in ("all", "B"):
        rc = foam("blockMesh", "log.blockMesh")
        print("blockMesh rc=%d" % rc)
        if rc:
            return rc
        rc = foam("splitMeshRegions -cellZones -overwrite", "log.splitMeshRegions")
        print("splitMeshRegions rc=%d" % rc)
        if rc:
            return rc

    if phase in ("all", "C"):
        pats = {r: read_patch_names(r) for r in ("fluid", "housing", "core")}
        for r, n in pats.items():
            print("%-8s patches: %s" % (r, n))
        pw = [p for p in pats["fluid"] if p.startswith("fluid_to_")]
        if len(pw) != 1:
            raise SystemExit("REFUSE: expected exactly one fluid_to_* patch, got %r" % pw)
        write_fluid_fields(pw[0])
        write_solid_fields("housing", ["housing_ends"],
                           sorted(p for p in pats["housing"] if p.startswith("housing_to_")))
        write_solid_fields("core", ["core_ends", "core_bore"],
                           sorted(p for p in pats["core"] if p.startswith("core_to_")))
        print("phase C: 0.orig fields written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
