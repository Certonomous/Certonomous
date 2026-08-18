#!/usr/bin/env python3
"""build_cases.py -- generate every K2e case from one table.  F14 rung K2e.

    python3 build_cases.py [OUTDIR]      # default: the directory holding this file

WHAT THIS BUILDS
----------------
The pre-registered sweep of K2e_PREREGISTRATION.md: the de Vahl Davis square
cavity at a FIXED Ra = 1e5, solved at nine values of eps = beta.dT = dT/300
under TWO solvers -- buoyantBoussinesqSimpleFoam and buoyantSimpleFoam -- on a
mandatory two-mesh pair (48x48 and 96x96, refinement factor 2.0).

THE KNOB IS dT AT FIXED Ra, AND THAT IS THE WHOLE DESIGN
--------------------------------------------------------
K0c set Ra by moving dT at fixed nu.  If K2e did that, Ra would rise with dT and
any separation between the two solvers would be confounded with a change of
Rayleigh number.  So Ra is pinned and nu moves with dT:

    Ra = g.beta.dT.L^3 / (nu.alpha),  alpha = nu/Pr,  beta = 1/TRef
    =>  nu(dT) = sqrt( g . beta . dT . L^3 . Pr / Ra )

In non-dimensional form the BOUSSINESQ problem depends only on (Ra, Pr), so its
answer is identical at every point of this sweep -- a flat line by construction,
and control C-1 of the pre-registration.  The VARIABLE-DENSITY problem depends
on (Ra, Pr, eps), so every departure from that flat line is a non-Boussinesq
effect at fixed Rayleigh number.  At dT = 1.088162239 K the formula returns
nu = 1.589461e-05, K0c's own Ra = 1e5 number; that is a check on this generator.

LIKE WITH LIKE, CONSTRUCTED NOT ASSUMED
---------------------------------------
The two solvers share neither a temperature datum nor an equation of state.
Four anchors, all written by this one script from one table so they cannot drift
apart (pre-registration section 2):

  1. Absolute K in both, with T_hot and T_cold written from the same numbers.
  2. `equationOfState incompressiblePerfectGas` with pRef fixed at 101325 Pa.
     Then rho = pRef/(R.T) and beta_true = 1/T, which at TRef = 300 K is exactly
     the Boussinesq case's beta.  The Boussinesq model IS the first-order Taylor
     expansion of this EOS about TRef, so what is measured is the truncation of
     that expansion and not a difference of fluid.
     `perfectGas` was REJECTED: in a sealed cavity its thermodynamic pressure
     moves to conserve mass, shifting rho_ref ~1.4 % and Ra ~2.8 % at dT = 120 K
     -- the same order as the effect being measured.  The price of
     incompressiblePerfectGas is that sealed-cavity mass is not held fixed; that
     price is paid deliberately to keep Ra exactly on the axis being swept.
  3. rho_ref = pRef/(R.TRef) is a CONSTANT, and mu(dT) = nu(dT).rho_ref, so Ra,
     Pr and beta are identical between solvers and across the sweep.
  4. k = mu.Cp/Pr with mu, Cp, Pr constant, so the variable-density thermal
     diffusivity equals nu/Pr at 300 K and varies off it -- which is part of the
     physics being measured, not a mismatch.  Constant k also means the
     temperature-gradient Nusselt and the heat-flux Nusselt are the same number,
     so Q1 has no definitional choice in it.

CONVERGENCE IS WITNESSED IN THE LOG, NOT ASSERTED
-------------------------------------------------
Every case carries function objects that make the RUNNING solver print, every
`monitor_sample_interval_iterations` (50) outer iterations and into its own log:

  * `hotT`, `coldT`   -- area-average T on each isothermal wall: the in-log
    witness that the intended dT was actually imposed, for BOTH solvers, which
    is control C-5 (a log states what ran; a dictionary states an intent).
  * `hotFlux`, `coldFlux` -- integral of n.grad(T) over each wall, from a `grad`
    function object evaluated in the same pass so it carries the scheme's own
    snGrad wall correction.  This is the live Nusselt history that
    scripts/check_convergence.py --monitor-regex gates the peak-to-peak spread
    of, against physics_rules.yaml thermal.monitor_peak_to_peak_max_pct.
  * `Umax`, `Tcentre` -- monitored on the same schedule and reported ungated.

The grad result carries the private name `k2eGradT` for the reason recorded in
scripts/heat_balance.py: a default name ('grad(T)') collides with files left by
a previous pass and can be silently satisfied by a stale one.

TIME-DIRECTORY HYGIENE
----------------------
Nothing here or in run_cases.sh globs for time directories.  A previous pass on
this repo cleaned cases with `rm -rf <case>/[0-9]*`, which matches `0.orig` --
the initial-condition directory the case is REBUILT from -- and deleted every
one of them in the K0b tree.  Old times are removed by `foamListTimes -rm`.
"""
from __future__ import annotations

import math
import os
import sys

# --------------------------------------------------------------------------
# THE ONE TABLE.  Every dictionary this script writes is derived from here.
# --------------------------------------------------------------------------
L        = 0.10          # m, cavity side (as K0b, K0c)
DEPTH    = 0.01          # m, one cell, empty front/back
GY       = -9.81         # m/s2
TREF     = 300.0         # K
BETA     = 1.0 / TREF    # 1/K, exactly, as for an ideal gas
PR       = 0.71          # K0c's benchmark Pr, not air's 0.706814
PRT      = 0.85          # physics_rules.yaml thermal.turbulent_prandtl_default
RA       = 1.0e5         # HELD FIXED across the whole sweep

# compressible side
MOLWEIGHT = 28.96        # kg/kmol, as the v2606 buoyantCavity tutorial
RR        = 8314.462618  # J/(kmol K), OpenFOAM's universal gas constant
R_SPEC    = RR / MOLWEIGHT
P_REF     = 101325.0     # Pa, FIXED: this is what pins rho_ref and hence Ra
CP        = 1004.4       # J/(kg K), as the v2606 buoyantCavity tutorial
RHO_REF   = P_REF / (R_SPEC * TREF)

# eps = beta.dT = dT/300.  Nine points, bracketing physics_rules.yaml's 0.1.
DT_SWEEP = [0.3, 3.0, 10.0, 15.0, 20.0, 25.0, 30.0, 45.0, 60.0, 90.0, 120.0]

MESHES = {"m48": 48, "m96": 96}
FINE_DT = [10.0, 20.0, 30.0, 90.0]   # eps = 0.03333, 0.06667, 0.10000, 0.30000

MONITOR_INTERVAL = 50             # physics_rules.yaml monitor_sample_interval_iterations

# Iteration caps.  These are properties of the PATH to the fixed point, not of
# the fixed point, and check_convergence.py -- not this number -- is what
# decides whether a case converged.  Calibrated on one pilot solve
# (m48_dT30_vd, the variable-density solver at the rule point, which is the
# harder of the two solvers): the governed peak-to-peak criterion of 0.02 %
# over a trailing 400-iteration window was first met between iteration 500
# (0.305 %) and 750 (0.000160 %), and sat at 0.000002 % from 1000 onward.  The
# caps below are ~3x that on the coarse mesh; the fine cap carries the ~4x
# iteration factor for a 2x mesh refinement that K0c measured and that
# NUMERICS_KNOWLEDGE.md records, plus the same ~3x headroom.  A run that misses
# the criterion anyway is reported NOT_CONVERGED and struck from the curve.
END_TIME = {"m48": 3000, "m96": 6000}
# One measured exception, and BOTH members of the pair take it so that the two
# solvers at a given eps always run the SAME iteration count.  At eps = 0.001 the
# variable-density case was still inside its final exponential approach at
# iteration 3000 and read a peak-to-peak spread of 0.0203 % against the governed
# 0.02 % -- the only run of the first pass to miss.  Nothing else about the case
# changes; an iteration count is a property of the path to the fixed point.
END_TIME_OVERRIDE = {("m48", 0.3): 8000}


def end_time(mesh: str, dT: float) -> int:
    return END_TIME_OVERRIDE.get((mesh, dT), END_TIME[mesh])



def nu_of(dT: float) -> float:
    """nu that holds Ra fixed at RA for this dT.  See the module docstring."""
    return math.sqrt(-GY * BETA * dT * L**3 * PR / RA)


HEADER = """/*--------------------------------*- C++ -*----------------------------------*\\
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

FOOTER = "\n// ************************************************************************* //\n"


def w(path: str, cls: str, loc: str, obj: str, body: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(HEADER.format(cls=cls, loc=loc, obj=obj))
        fh.write("\n" + body.strip("\n") + "\n")
        fh.write(FOOTER)


def block_mesh(case: str, n: int) -> None:
    w(f"{case}/system/blockMeshDict", "dictionary", "system", "blockMeshDict", f"""
scale   1;

vertices
(
    (0.00000 0.00000 0.00000)
    ({L:.5f} 0.00000 0.00000)
    (0.00000 {L:.5f} 0.00000)
    ({L:.5f} {L:.5f} 0.00000)
    (0.00000 0.00000 {DEPTH:.5f})
    ({L:.5f} 0.00000 {DEPTH:.5f})
    (0.00000 {L:.5f} {DEPTH:.5f})
    ({L:.5f} {L:.5f} {DEPTH:.5f})
);

blocks
(
    hex (0 1 3 2 4 5 7 6) ({n} {n} 1) simpleGrading (1 1 1)
);

edges();

boundary
(
    hotWall
    {{
        type wall;
        faces ( (0 4 6 2) );
    }}
    coldWall
    {{
        type wall;
        faces ( (1 3 7 5) );
    }}
    adiabaticWalls
    {{
        type wall;
        faces ( (0 1 5 4) (2 6 7 3) );
    }}
    frontAndBack
    {{
        type empty;
        faces ( (0 2 3 1) (4 5 7 6) );
    }}
);
""")


def functions_block(monitor_fields: str) -> str:
    """Function objects.  Identical schedule and identical operations for both
    solvers, so the monitored quantities are the same measurement twice."""
    ei = MONITOR_INTERVAL
    return f"""
functions
{{
    gradT
    {{
        type            grad;
        libs            (fieldFunctionObjects);
        field           T;
        result          k2eGradT;
        executeControl  timeStep;
        executeInterval {ei};
        writeControl    none;
        log             false;
    }}
    hotFlux
    {{
        type            surfaceFieldValue;
        libs            (fieldFunctionObjects);
        regionType      patch;
        name            hotWall;
        operation       areaNormalIntegrate;
        fields          (k2eGradT);
        writeFields     false;
        writeToFile     true;
        log             true;
        executeControl  timeStep;
        executeInterval {ei};
        writeControl    timeStep;
        writeInterval   {ei};
    }}
    coldFlux
    {{
        type            surfaceFieldValue;
        libs            (fieldFunctionObjects);
        regionType      patch;
        name            coldWall;
        operation       areaNormalIntegrate;
        fields          (k2eGradT);
        writeFields     false;
        writeToFile     true;
        log             true;
        executeControl  timeStep;
        executeInterval {ei};
        writeControl    timeStep;
        writeInterval   {ei};
    }}
    hotT
    {{
        type            surfaceFieldValue;
        libs            (fieldFunctionObjects);
        regionType      patch;
        name            hotWall;
        operation       areaAverage;
        fields          (T);
        writeFields     false;
        writeToFile     true;
        log             true;
        executeControl  timeStep;
        executeInterval {ei};
        writeControl    timeStep;
        writeInterval   {ei};
    }}
    coldT
    {{
        type            surfaceFieldValue;
        libs            (fieldFunctionObjects);
        regionType      patch;
        name            coldWall;
        operation       areaAverage;
        fields          (T);
        writeFields     false;
        writeToFile     true;
        log             true;
        executeControl  timeStep;
        executeInterval {ei};
        writeControl    timeStep;
        writeInterval   {ei};
    }}
    magU
    {{
        type            mag;
        libs            (fieldFunctionObjects);
        field           U;
        result          k2eMagU;
        executeControl  timeStep;
        executeInterval {ei};
        writeControl    none;
        log             false;
    }}
    Umax
    {{
        type            volFieldValue;
        libs            (fieldFunctionObjects);
        regionType      all;
        operation       max;
        fields          (k2eMagU);
        writeFields     false;
        writeToFile     true;
        log             true;
        executeControl  timeStep;
        executeInterval {ei};
        writeControl    timeStep;
        writeInterval   {ei};
    }}
    Tcentre
    {{
        type            probes;
        libs            (fieldFunctionObjects);
        fields          (T);
        probeLocations  (({L/2:.6f} {L/2:.6f} {DEPTH/2:.6f}));
        writeToFile     true;
        log             true;
        executeControl  timeStep;
        executeInterval {ei};
        writeControl    timeStep;
        writeInterval   {ei};
    }}
{monitor_fields}}}
"""


# --------------------------------------------------------------------------
# Boussinesq case
# --------------------------------------------------------------------------
def build_boussinesq(case: str, n: int, dT: float, end: int) -> None:
    nu = nu_of(dT)
    th, tc = TREF + dT / 2.0, TREF - dT / 2.0
    block_mesh(case, n)

    w(f"{case}/constant/transportProperties", "dictionary", "constant", "transportProperties", f"""
transportModel  Newtonian;

nu              {nu:.9e};
beta            {BETA:.12e};
TRef            {TREF:.1f};
Pr              {PR:.6f};
Prt             {PRT:.2f};
""")
    w(f"{case}/constant/g", "uniformDimensionedVectorField", "constant", "g", f"""
dimensions      [0 1 -2 0 0 0 0];
value           (0 {GY:.6f} 0);
""")
    w(f"{case}/constant/turbulenceProperties", "dictionary", "constant", "turbulenceProperties",
      "simulationType  laminar;\n")

    # Read ONLY by scripts/heat_balance.py, never by either solver.  rho0 and
    # cp0 are the variable-density case's OWN reference density and Cp, written
    # identically into both halves of every pair so that the auditor's watts are
    # the same physical watts on both sides and can be compared directly.
    w(f"{case}/constant/thermalAuditProperties", "dictionary", "constant",
      "thermalAuditProperties", f"""
rho0            {RHO_REF:.6f};
cp0             {CP};
""")

    w(f"{case}/0.orig/T", "volScalarField", "0.orig", "T", f"""
dimensions      [0 0 0 1 0 0 0];

internalField   uniform {TREF:.1f};

boundaryField
{{
    hotWall         {{ type fixedValue; value uniform {th:.9f}; }}
    coldWall        {{ type fixedValue; value uniform {tc:.9f}; }}
    adiabaticWalls  {{ type zeroGradient; }}
    frontAndBack    {{ type empty; }}
}}
""")
    w(f"{case}/0.orig/U", "volVectorField", "0.orig", "U", """
dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{
    hotWall         { type noSlip; }
    coldWall        { type noSlip; }
    adiabaticWalls  { type noSlip; }
    frontAndBack    { type empty; }
}
""")
    w(f"{case}/0.orig/p_rgh", "volScalarField", "0.orig", "p_rgh", """
dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    hotWall         { type fixedFluxPressure; value uniform 0; }
    coldWall        { type fixedFluxPressure; value uniform 0; }
    adiabaticWalls  { type fixedFluxPressure; value uniform 0; }
    frontAndBack    { type empty; }
}
""")
    w(f"{case}/0.orig/alphat", "volScalarField", "0.orig", "alphat", """
dimensions      [0 2 -1 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    hotWall         { type calculated; value uniform 0; }
    coldWall        { type calculated; value uniform 0; }
    adiabaticWalls  { type calculated; value uniform 0; }
    frontAndBack    { type empty; }
}
""")
    w(f"{case}/system/fvSchemes", "dictionary", "system", "fvSchemes", """
ddtSchemes      { default steadyState; }
gradSchemes     { default Gauss linear; }

divSchemes
{
    default         none;
    div(phi,U)      bounded Gauss linear;
    div(phi,T)      bounded Gauss linear;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes    { default Gauss linear corrected; }
interpolationSchemes{ default linear; }
snGradSchemes       { default corrected; }
""")
    w(f"{case}/system/fvSolution", "dictionary", "system", "fvSolution", """
solvers
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
    pRefCell        0;
    pRefValue       0;

    // NO residualControl.  Every K2e case runs a FIXED iteration count and is
    // graded by the governed peak-to-peak criterion on Nu_h instead
    // (physics_rules.yaml thermal.monitor_*).  K0c measured four fine meshes
    // that met their own residualControl while the graded quantity was still
    // drifting 2.19 to 4.67 %, so residualControl is not the gate here; and an
    // early residual exit would give the two solvers DIFFERENT iteration
    // counts, which is a like-with-like defect in a comparison rung.
}

relaxationFactors
{
    fields    { p_rgh 0.3; }
    equations { U 0.7; T 0.9; }
}
""")
    w(f"{case}/system/controlDict", "dictionary", "system", "controlDict",
      f"""
application     buoyantBoussinesqSimpleFoam;
startFrom       latestTime;
startTime       0;
stopAt          endTime;
endTime         {end};
deltaT          1;
writeControl    timeStep;
writeInterval   {end};
purgeWrite      1;
writeFormat     ascii;
writePrecision  16;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;
""" + functions_block(""))


# --------------------------------------------------------------------------
# variable-density case
# --------------------------------------------------------------------------
def build_variable_density(case: str, n: int, dT: float, end: int) -> None:
    nu = nu_of(dT)
    mu = nu * RHO_REF
    th, tc = TREF + dT / 2.0, TREF - dT / 2.0
    block_mesh(case, n)

    w(f"{case}/constant/thermophysicalProperties", "dictionary", "constant",
      "thermophysicalProperties", f"""
thermoType
{{
    type            heRhoThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState incompressiblePerfectGas;
    specie          specie;
    energy          sensibleEnthalpy;
}}

mixture
{{
    specie
    {{
        molWeight       {MOLWEIGHT};
    }}
    equationOfState
    {{
        pRef            {P_REF:.1f};
    }}
    thermodynamics
    {{
        Cp              {CP};
        Hf              0;
    }}
    transport
    {{
        mu              {mu:.9e};
        Pr              {PR:.6f};
    }}
}}
""")
    w(f"{case}/constant/g", "uniformDimensionedVectorField", "constant", "g", f"""
dimensions      [0 1 -2 0 0 0 0];
value           (0 {GY:.6f} 0);
""")
    w(f"{case}/constant/turbulenceProperties", "dictionary", "constant", "turbulenceProperties",
      "simulationType  laminar;\n")

    # Read ONLY by scripts/heat_balance.py, never by either solver.  rho0 and
    # cp0 are the variable-density case's OWN reference density and Cp, written
    # identically into both halves of every pair so that the auditor's watts are
    # the same physical watts on both sides and can be compared directly.
    w(f"{case}/constant/thermalAuditProperties", "dictionary", "constant",
      "thermalAuditProperties", f"""
rho0            {RHO_REF:.6f};
cp0             {CP};
""")

    w(f"{case}/0.orig/T", "volScalarField", "0.orig", "T", f"""
dimensions      [0 0 0 1 0 0 0];

internalField   uniform {TREF:.1f};

boundaryField
{{
    hotWall         {{ type fixedValue; value uniform {th:.9f}; }}
    coldWall        {{ type fixedValue; value uniform {tc:.9f}; }}
    adiabaticWalls  {{ type zeroGradient; }}
    frontAndBack    {{ type empty; }}
}}
""")
    w(f"{case}/0.orig/U", "volVectorField", "0.orig", "U", """
dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{
    hotWall         { type noSlip; }
    coldWall        { type noSlip; }
    adiabaticWalls  { type noSlip; }
    frontAndBack    { type empty; }
}
""")
    w(f"{case}/0.orig/p", "volScalarField", "0.orig", "p", f"""
dimensions      [1 -1 -2 0 0 0 0];

internalField   uniform {P_REF:.1f};

boundaryField
{{
    hotWall         {{ type calculated; value uniform {P_REF:.1f}; }}
    coldWall        {{ type calculated; value uniform {P_REF:.1f}; }}
    adiabaticWalls  {{ type calculated; value uniform {P_REF:.1f}; }}
    frontAndBack    {{ type empty; }}
}}
""")
    w(f"{case}/0.orig/p_rgh", "volScalarField", "0.orig", "p_rgh", f"""
dimensions      [1 -1 -2 0 0 0 0];

internalField   uniform {P_REF:.1f};

boundaryField
{{
    hotWall         {{ type fixedFluxPressure; value uniform {P_REF:.1f}; }}
    coldWall        {{ type fixedFluxPressure; value uniform {P_REF:.1f}; }}
    adiabaticWalls  {{ type fixedFluxPressure; value uniform {P_REF:.1f}; }}
    frontAndBack    {{ type empty; }}
}}
""")
    w(f"{case}/0.orig/alphat", "volScalarField", "0.orig", "alphat", """
dimensions      [1 -1 -1 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    hotWall         { type calculated; value uniform 0; }
    coldWall        { type calculated; value uniform 0; }
    adiabaticWalls  { type calculated; value uniform 0; }
    frontAndBack    { type empty; }
}
""")
    w(f"{case}/system/fvSchemes", "dictionary", "system", "fvSchemes", """
ddtSchemes      { default steadyState; }
gradSchemes     { default Gauss linear; }

divSchemes
{
    default         none;
    div(phi,U)      bounded Gauss linear;
    div(phi,h)      bounded Gauss linear;
    div(phi,K)      bounded Gauss linear;
    div(phi,Ekp)    bounded Gauss linear;
    div(((rho*nuEff)*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes    { default Gauss linear corrected; }
interpolationSchemes{ default linear; }
snGradSchemes       { default corrected; }
""")
    w(f"{case}/system/fvSolution", "dictionary", "system", "fvSolution", f"""
solvers
{{
    p_rgh
    {{
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-10;
        relTol          0.001;
    }}
    "(U|h|e)"
    {{
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-12;
        relTol          0.001;
    }}
}}

SIMPLE
{{
    nNonOrthogonalCorrectors 0;
    pRefCell        0;
    pRefValue       {P_REF:.1f};
    rhoMin          0.1;
    rhoMax          10.0;

    // NO residualControl -- see the Boussinesq fvSolution for the reason.
}}

relaxationFactors
{{
    fields    {{ rho 1.0; p_rgh 0.3; }}
    equations {{ U 0.7; h 0.9; }}
}}
""")
    w(f"{case}/system/controlDict", "dictionary", "system", "controlDict",
      f"""
application     buoyantSimpleFoam;
startFrom       latestTime;
startTime       0;
stopAt          endTime;
endTime         {end};
deltaT          1;
writeControl    timeStep;
writeInterval   {end};
purgeWrite      1;
writeFormat     ascii;
writePrecision  16;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;
""" + functions_block(""))


def main() -> int:
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1
                          else os.path.dirname(os.path.abspath(__file__)))
    os.makedirs(out, exist_ok=True)

    print(f"K2e case generator -- Ra held at {RA:g}, Pr {PR}, TRef {TREF} K, "
          f"beta {BETA:.9e} 1/K")
    print(f"rho_ref = pRef/(R.TRef) = {P_REF:.1f}/({R_SPEC:.4f} x {TREF:.1f}) "
          f"= {RHO_REF:.6f} kg/m3   [constant across the sweep, by design]")
    print()
    print(f"{'case':34s} {'dT K':>8s} {'eps=b.dT':>9s} {'nu m2/s':>13s} "
          f"{'mu Pa.s':>13s} {'T_hot K':>9s} {'Pe_cell':>8s}")

    built = []
    for name, n in MESHES.items():
        dts = DT_SWEEP if name == "m48" else FINE_DT
        for dT in dts:
            eps = BETA * dT
            nu = nu_of(dT)
            tag = f"dT{dT:g}".replace(".", "p")
            for model, fn in (("bou", build_boussinesq), ("vd", build_variable_density)):
                case = os.path.join(out, f"{name}_{tag}_{model}")
                fn(case, n, dT, end_time(name, dT))
                built.append(case)
                print(f"{os.path.basename(case):34s} {dT:8.3f} {eps:9.5f} "
                      f"{nu:13.6e} {nu*RHO_REF:13.6e} {TREF+dT/2:9.4f} "
                      f"{68.22/n:8.3f}")

    # The generator's own check: the sweep must pass through K0c's Ra = 1e5 nu.
    probe = nu_of(1.088162239)
    print()
    print(f"generator check: nu(dT = 1.088162239 K) = {probe:.9e}  "
          f"(K0c Ra1e5 transportProperties: 1.589461e-05)  "
          f"{'OK' if abs(probe - 1.589461e-05) < 1e-11 else 'MISMATCH'}")
    print(f"cell Peclet number (u2max_ref 68.22 / N) is below 2 on both meshes; "
          f"K0c's admissibility condition for `bounded Gauss linear`.")
    print(f"\n{len(built)} cases written under {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
