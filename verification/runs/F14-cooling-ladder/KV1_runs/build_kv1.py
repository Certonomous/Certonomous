#!/usr/bin/env python3
"""build_kv1.py -- the KV1 open-duct control pair, F14 cooling ladder.

    python3 build_kv1.py            # writes case directories next to this file

WHAT THIS BUILDS, AND WHY IT IS A PAIR
--------------------------------------
KV1 is specified in `K2a_RACK_ROW_MODULE_SPEC.md` section 8, lines 378-381:

    KV1 -- a straight duct with imposed mdot, inlet T, and a planted volumetric
    source of known watts; the audited net must recover the plant within
    `heat_balance_source_recovery_tol_pct` (0.1%).

That is the POSITIVE control and it is `KV1a_duct_source` below.  It is built
with its NEGATIVE twin `KV1b_duct_nosource`, identical in every byte except
`constant/fvOptions`, for the reason already on this campaign's record: at K1c
the no-source negative control was the case that fired S15, and without it the
control set would have been quietly worthless (see `scripts/heat_balance.py`,
`fvoptions_witness`, "THIS IS NOT HYPOTHETICAL").  A positive control run
without its negative twin cannot tell "the instrument recovered the plant" from
"the instrument returns that number for anything".

The two also answer two different questions, and neither answers the other's:

  KV1a  the ledger's NET must recover -5.000e-03 W.  With a source present the
        balance is not supposed to close, and it does not -- `Q_net` is the
        plant.  This is the RECOVERY test, graded in watts.
  KV1b  with no source the balance must CLOSE, and the imbalance percentage is
        then a verdict on an open case.  Graded in percent against
        `heat_balance_tol_pct`.
  KV1c  added AFTER KV1b was run, for the reason below.  It is the case the
        mutation harness is run on.

WHY THERE IS A KV1c: KV1b CLOSES WITHOUT BEING ABLE TO FAIL
------------------------------------------------------------
KV1b was built with ADIABATIC walls and no source, and it converges to a duct
whose temperature is EXACTLY 305 K everywhere -- inlet value, initial value,
outlet value, all the same number, because nothing in the case can change it.
Its balance closes, and the closure is worth nothing, for a reason that is a
close relative of the sealed-case identity this whole rung exists to get past:

    Q_adv(inlet) = +0.146 W and Q_adv(outlet) = -0.146 W, so the ADVECTIVE SUM
    IS ZERO.  Flip the sign of the advective term and the sum is still zero.
    Scale it by two and the sum is still zero.  The mutations cannot bite,
    because there is nothing for them to bite on.

That is "a term that is computed but never able to fail" -- the identity defect
wearing a new name -- and it would have been easy to write KV1b up as a passing
open-case closure and move on.  KV1b is KEPT, not replaced, precisely because
the contrast is the finding: it is the NEGATIVE control for the mutation
harness, the case where the mutations are correctly invisible.

KV1c gives the ledger two INDEPENDENT non-zero terms that must cancel each
other: heat enters by CONDUCTION through a hot bottom wall and leaves by
ADVECTION through the outlet.  Closure there is a genuine cross-term
constraint, and a wrong advective term breaks it.  KV1c is where the
fail-and-close demonstration is done.

GEOMETRY AND REGIME
-------------------
  L x H x depth  = 0.30 x 0.05 x 0.01 m, mesh 60 x 20 x 1 = 1200 cells
  U_in           = 0.05 m/s uniform      -> Re_H = U.H/nu = 157, laminar
  fluid          = K0c's air, unchanged: nu = 1.589461e-05, Pr = 0.71,
                   rho0 = 1.1614, cp0 = 1007.0, TRef = 300 K
  g              = 0.  FORCED convection deliberately: buoyancy would couple
                   the temperature field back into the flow and make the
                   through-flow a solved quantity rather than an imposed one.
                   KV1 is validating a BOOKKEEPING term, and the cheapest case
                   that exercises it is the right one.  Precedent for g = 0 on
                   this ladder is K0c's C1 control.

WHY THE INLET RUNS AT 305 K AND NOT AT 300 K
--------------------------------------------
This is the one design choice that is not obvious and it decides whether the
control can test anything.

The advective enthalpy flux is referred to a DATUM, and `heat_balance.py` uses
the case's own `TRef` (300 K).  With an inlet AT the datum the inlet's advective
term is identically zero, no patch carries heat inward, and the imbalance ratio
is UNDEFINED by the P1 rule -- the case fails with no number, exactly as K0c's
C3 does, and the CLOSURE half of KV1 could not be tested at all.

Running the inlet 5 K above the datum puts

    Q_in = rho.cp.(T_in - TRef).Vdot = 1169.5298 * 5 * 2.5e-05 = 0.146191 W

of genuine advected heat into the ledger, so the ratio has a denominator and a
closure percentage means something.  5 K is small enough that beta.dT = 0.0167
leaves Boussinesq satisfied by a factor of six even though g = 0 makes it moot.

THE PLANT, AND THE ARITHMETIC THAT SETS IT
------------------------------------------
`scalarSemiImplicitSource` on the T equation is KINEMATIC: `volumeMode
absolute` takes the total over the cell set in K.m3/s.  Watts are

    Q = rho.cp.S    ->    S = Q / (rho.cp) = 5.000e-03 / 1169.5298

which is the same 4.275222401345e-06 K.m3/s K0c's C3 plants, because the fluid
is the same.  The expected temperature rise across the duct is

    dT = Q / (mdot.cp) = 5.000e-03 / (2.903500e-05 * 1007) = 0.171 K

so the outlet should read about 305.171 K, and that is checked in the SOLVER'S
OWN LOG by the `outletT` function object below rather than inferred afterwards.

CONVERGENCE IS WITNESSED, NOT ASSERTED, AND THE SNAPSHOTS ARE THE POINT
----------------------------------------------------------------------
`writeInterval 20` is not tidiness.  The claim KV1 has to support is that an
open-case closure is CONVERGENCE-SENSITIVE -- unlike the sealed-case closure,
which K0b measured at 0.0128 percent at iteration 10 and which never rose above
0.13 percent at any iteration.  That claim can only be made by auditing the SAME
case at early and late iterations, so the early time directories have to exist.
"""

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- the one table every number below comes from --------------------------
NU = 1.589461e-05          # m2/s, air at 300 K; K0a/K0b/K0c value unchanged
PR = 0.71                  # K0c's benchmark value
PRT = 0.85
TREF = 300.0
BETA = 3.333333333e-03
RHO0 = 1.1614              # kg/m3
CP0 = 1007.0               # J/kg/K
LX, LY, LZ = 0.30, 0.05, 0.01
NX, NY = 60, 20
U_IN = 0.05                # m/s
T_IN = 305.0               # K -- 5 K ABOVE the datum; see the docstring
T_HOT = 315.0              # K -- KV1c only: the heated bottom wall
Q_PLANT_W = 5.000e-03      # W, the planted volumetric source
END_TIME = 1000
WRITE_INTERVAL = 20

RHO_CP = RHO0 * CP0
S_PLANT = Q_PLANT_W / RHO_CP        # K.m3/s, what fvOptions actually takes
VDOT = U_IN * LY * LZ               # m3/s
MDOT = RHO0 * VDOT                  # kg/s
DT_EXPECTED = Q_PLANT_W / (MDOT * CP0)
Q_IN_EXPECTED = RHO_CP * (T_IN - TREF) * VDOT

HDR = """/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  v2606                                 |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       {cls};
    location    "{loc}";
    object      {obj};
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

"""

FOOT = "\n// ************************************************************************* //\n"


def w(case, rel, cls, obj, body):
    loc = os.path.dirname(rel)
    path = os.path.join(case, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(HDR.format(cls=cls, loc=loc, obj=obj) + body + FOOT)


def block_mesh_dict(heated):
    v = [(0, 0, 0), (LX, 0, 0), (0, LY, 0), (LX, LY, 0),
         (0, 0, LZ), (LX, 0, LZ), (0, LY, LZ), (LX, LY, LZ)]
    verts = "\n".join(f"    ({x:.5f} {y:.5f} {z:.5f})" for x, y, z in v)
    if heated:
        # bottom wall (0 1 5 4) is heated; top wall (2 6 7 3) stays adiabatic
        wallblk = ("hotWall\n    {\n        type wall;\n"
                   "        faces ( (0 1 5 4) );\n    }\n"
                   "    topWall\n    {\n        type wall;\n"
                   "        faces ( (2 6 7 3) );\n    }")
    else:
        wallblk = ("ductWalls\n    {\n        type wall;\n"
                   "        faces ( (0 1 5 4) (2 6 7 3) );\n    }")
    return f"""scale   1;

vertices
(
{verts}
);

blocks
(
    hex (0 1 3 2 4 5 7 6) ({NX} {NY} 1) simpleGrading (1 1 1)
);

edges();

boundary
(
    inlet
    {{
        type patch;
        faces ( (0 4 6 2) );
    }}
    outlet
    {{
        type patch;
        faces ( (1 3 7 5) );
    }}
    {wallblk}
    frontAndBack
    {{
        type empty;
        faces ( (0 2 3 1) (4 5 7 6) );
    }}
);
"""


def control_dict():
    # The in-log witnesses. `inletT`/`outletT` are the KV1 analogue of K0c's
    # `hotT`/`coldT`: they make the RUNNING SOLVER print the imposed inlet
    # temperature and the achieved rise, so the plant is witnessed in the log
    # and not only in a dictionary. `mdotOut` does the same for the mass flux
    # the whole advective term is built on.
    fos = []
    for nm, patch, op, fld in (("inletT", "inlet", "areaAverage", "T"),
                               ("outletT", "outlet", "areaAverage", "T"),
                               ("mdotOut", "outlet", "sum", "phi"),
                               ("mdotIn", "inlet", "sum", "phi")):
        fos.append(f"""    {nm}
    {{
        type            surfaceFieldValue;
        libs            (fieldFunctionObjects);
        regionType      patch;
        name            {patch};
        operation       {op};
        fields          ({fld});
        writeFields     false;
        writeToFile     true;
        log             true;
        executeControl  timeStep;
        executeInterval 20;
        writeControl    timeStep;
        writeInterval   20;
    }}""")
    body = "\n".join(fos)
    return f"""application     buoyantBoussinesqSimpleFoam;
startFrom       latestTime;
startTime       0;
stopAt          endTime;
endTime         {END_TIME};
deltaT          1;
writeControl    timeStep;
writeInterval   {WRITE_INTERVAL};
purgeWrite      0;
writeFormat     ascii;
writePrecision  16;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;

functions
{{
{body}
}}
"""


def build(name, with_source, heated=False):
    case = os.path.join(HERE, name)
    # The wall patch names and their T condition are the only thing the heated
    # variant changes. Everything else -- mesh, fluid, flow BCs, schemes,
    # solver settings, function objects -- is byte-identical across the three
    # cases, so a difference between them cannot come from anywhere else.
    if heated:
        walls = ("hotWall", "topWall")
        tw_T = (f"    hotWall\n    {{\n        type            fixedValue;\n"
                f"        value           uniform {T_HOT:.1f};\n    }}\n"
                "    topWall\n    {\n        type            zeroGradient;\n    }")
    else:
        walls = ("ductWalls",)
        tw_T = "    ductWalls\n    {\n        type            zeroGradient;\n    }"
    tw_U = "\n".join(f"    {n}       {{ type noSlip; }}" for n in walls)
    prgh_walls = "\n".join(
        f"    {n}\n    {{\n        type            fixedFluxPressure;\n"
        f"        value           uniform 0;\n    }}" for n in walls)
    alphat_walls = "\n".join(
        f"    {n}       {{ type calculated; value uniform 0; }}" for n in walls)
    w(case, "system/blockMeshDict", "dictionary", "blockMeshDict", block_mesh_dict(heated))
    w(case, "system/controlDict", "dictionary", "controlDict", control_dict())
    w(case, "system/fvSchemes", "dictionary", "fvSchemes", """ddtSchemes
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
    div(phi,U)      bounded Gauss linear;
    div(phi,T)      bounded Gauss linear;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
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
""")
    w(case, "system/fvSolution", "dictionary", "fvSolution", """solvers
{
    p_rgh
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-10;
        relTol          0.001;
    }

    "(U|T)"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-12;
        relTol          0.001;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 0;

    residualControl
    {
        p_rgh           1e-09;
        U               1e-10;
        T               1e-10;
    }
}

relaxationFactors
{
    fields
    {
        p_rgh           0.3;
    }
    equations
    {
        U               0.7;
        T               0.9;
    }
}
""")
    w(case, "constant/transportProperties", "dictionary", "transportProperties",
      f"""transportModel  Newtonian;

nu              {NU:.6e};
beta            {BETA:.9e};
TRef            {TREF:.1f};
Pr              {PR:.6f};
Prt             {PRT};
""")
    w(case, "constant/thermalAuditProperties", "dictionary", "thermalAuditProperties",
      f"""rho0            {RHO0};
cp0             {CP0};
""")
    w(case, "constant/turbulenceProperties", "dictionary", "turbulenceProperties",
      "simulationType  laminar;\n")
    w(case, "constant/g", "uniformDimensionedVectorField", "g",
      "dimensions      [0 1 -2 0 0 0 0];\nvalue           (0 0 0);\n")
    if with_source:
        # KINEMATIC source: volumeMode absolute takes K.m3/s over the cell set,
        # so the watts are rho.cp times this. Same arithmetic as K0c's C3.
        w(case, "constant/fvOptions", "dictionary", "fvOptions",
          f"""heatPlant
{{
    type            scalarSemiImplicitSource;
    selectionMode   all;
    volumeMode      absolute;
    sources
    {{
        T           ({S_PLANT:.12e} 0);
    }}
}}
""")

    w(case, "0.orig/T", "volScalarField", "T", f"""dimensions      [0 0 0 1 0 0 0];

internalField   uniform {T_IN:.1f};

boundaryField
{{
    inlet
    {{
        type            fixedValue;
        value           uniform {T_IN:.1f};
    }}
    outlet
    {{
        type            zeroGradient;
    }}
{tw_T}
    frontAndBack
    {{
        type            empty;
    }}
}}
""")
    w(case, "0.orig/U", "volVectorField", "U", f"""dimensions      [0 1 -1 0 0 0 0];

internalField   uniform ({U_IN} 0 0);

boundaryField
{{
    inlet
    {{
        type            fixedValue;
        value           uniform ({U_IN} 0 0);
    }}
    outlet
    {{
        type            zeroGradient;
    }}
{tw_U}
    frontAndBack    {{ type empty; }}
}}
""")
    w(case, "0.orig/p_rgh", "volScalarField", "p_rgh", f"""dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{{
    inlet
    {{
        type            fixedFluxPressure;
        value           uniform 0;
    }}
    outlet
    {{
        type            fixedValue;
        value           uniform 0;
    }}
{prgh_walls}
    frontAndBack    {{ type empty; }}
}}
""")
    w(case, "0.orig/alphat", "volScalarField", "alphat", f"""dimensions      [0 2 -1 0 0 0 0];

internalField   uniform 0;

boundaryField
{{
    inlet           {{ type calculated; value uniform 0; }}
    outlet          {{ type calculated; value uniform 0; }}
{alphat_walls}
    frontAndBack    {{ type empty; }}
}}
""")
    with open(os.path.join(case, "CASE.txt"), "w") as fh:
        fh.write(
            f"case             {name}\n"
            f"geometry         {LX} x {LY} x {LZ} m\n"
            f"mesh             {NX} x {NY} x 1 uniform ({NX * NY} cells)\n"
            f"U_in             {U_IN} m/s\n"
            f"Re_H             {U_IN * LY / NU:.1f}\n"
            f"T_in             {T_IN} K\n"
            f"TRef (datum)     {TREF} K\n"
            f"g                0 (forced convection)\n"
            f"Vdot             {VDOT:.6e} m3/s\n"
            f"mdot             {MDOT:.6e} kg/s\n"
            f"heated_wall      {(str(T_HOT) + ' K on hotWall') if heated else 'none (adiabatic)'}\n"
            f"planted_source   {Q_PLANT_W if with_source else 0.0} W\n"
            f"S_kinematic      {S_PLANT if with_source else 0.0:.12e} K.m3/s\n"
            f"dT_expected      {DT_EXPECTED if with_source else 0.0:.6f} K\n"
            f"Q_in_expected    {Q_IN_EXPECTED:.6e} W\n"
            f"endTime          {END_TIME}\n")
    return case


def main():
    print(f"rho.cp        = {RHO_CP:.6f} J/m3/K")
    print(f"S_plant       = {S_PLANT:.12e} K.m3/s  ({Q_PLANT_W} W)")
    print(f"Vdot          = {VDOT:.6e} m3/s")
    print(f"mdot          = {MDOT:.6e} kg/s")
    print(f"dT expected   = {DT_EXPECTED:.6f} K   -> T_out ~ {T_IN + DT_EXPECTED:.4f} K")
    print(f"Q_in expected = {Q_IN_EXPECTED:.6e} W  (inlet advection above datum)")
    print(f"Re_H          = {U_IN * LY / NU:.1f}   beta.dT(inlet-datum) = "
          f"{BETA * (T_IN - TREF):.6f}")
    for name, src, hot in (("KV1a_duct_source", True, False),
                           ("KV1b_duct_nosource", False, False),
                           ("KV1c_duct_heated", False, True)):
        c = build(name, src, hot)
        print(f"built {c}   fvOptions: {'heatPlant' if src else 'NONE'}   "
              f"walls: {'hotWall %g K + adiabatic topWall' % T_HOT if hot else 'adiabatic'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
