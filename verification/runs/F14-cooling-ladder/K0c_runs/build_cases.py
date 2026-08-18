#!/usr/bin/env python3
"""build_cases.py -- generate every K0c case from one table, F14 rung K0c.

    python3 build_cases.py            # writes case directories next to this file

WHAT THIS BUILDS
----------------
The laminar rung of `docs/campaigns/F14-cooling-ladder/K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md`,
Section 1: the de Vahl Davis square cavity at Ra = 1e3, 1e4, 1e5, 1e6, each on a
MANDATORY two-mesh pair (Section 1.4: refinement factor >= 1.5 in each direction,
coarse solved first, both values reported, grading on the fine mesh only).

Plus three control twins.  Their design and their predictions are registered in
the docstring of `analyse_k0c.py`, which was written BEFORE any solver ran.

HOW Ra IS SET, AND WHY dT IS THE KNOB
-------------------------------------
Ra = g.beta.dT.L^3 / (nu.alpha), alpha = nu/Pr   (gate Section 1.2, Gjesdal 2003).

Geometry, gravity and the fluid are held fixed across all four rungs and only dT
moves.  That keeps one mesh family, one property set and one Boussinesq check for
the whole ladder, and it makes the Ra plant a change to a boundary value that the
RUNNING SOLVER reports back in its own log (see the `hotT`/`coldT` function
objects below) rather than a number that only ever exists in a dictionary.

  L    = 0.10 m            (as K0b, so the K0b mesh study and this gate share a case class)
  g    = 9.81 m/s2 downward
  TRef = 300 K, beta = 1/TRef exactly
  Pr   = 0.71              (gate Section 1.2: "Boussinesq fluid, Pr = 0.71")
  nu   = 1.589461e-05 m2/s (air at 300 K; carried over from K0a/K0b unchanged)
  dT   = Ra . nu . alpha / (g . beta . L^3)

Note Pr here is 0.71 exactly, the gate's number, NOT K0b's 0.706814.  K0b was a
capability rung with air properties; this rung is graded against a benchmark
that specifies Pr = 0.71, so the benchmark's value is used and the difference is
recorded rather than absorbed.

SCHEMES, AND WHY THEY DIFFER FROM K0b
-------------------------------------
K0b used `bounded Gauss limitedLinear 1` on div(phi,T) and `linearUpwind` on
div(phi,U): robust, upwind-biased, and diffusive.  The reference is a
second-order CENTRAL difference benchmark with Richardson extrapolation (gate
Section 1.1).  Grading a limiter-damped solution against it would compare two
different discretisations and blame the difference on the physics, so this rung
runs `bounded Gauss linear` on both convection terms.

That choice is only admissible if the cell Peclet number stays near or below 2,
which is checked here rather than assumed.  Pe_cell = u* / N with u* the
non-dimensional velocity and N the cell count per side; using the reference
u2max values (gate Section 1.3) the fine meshes give

    Ra 1e3, N=64  : Pe = 3.697/64   = 0.06
    Ra 1e4, N=80  : Pe = 19.617/80  = 0.25
    Ra 1e5, N=128 : Pe = 68.22/128  = 0.53
    Ra 1e6, N=192 : Pe = 219.36/192 = 1.14

and the coarse meshes 0.12 / 0.49 / 1.07 / 1.71.  All below 2.  This is printed
by the script at build time so the claim travels with the cases.

CONVERGENCE IS WITNESSED, NOT ASSERTED
--------------------------------------
K0b ran 4000 iterations and never reached its own residualControl; the residuals
plateaued at ~1e-7.  A plateau is not a criterion.  Every case here therefore
carries function objects that make the RUNNING SOLVER print, every 50
iterations and into log.buoyantBoussinesqSimpleFoam itself:

  * `hotT`, `coldT`   -- area-average T on each isothermal wall.  This is the
    in-log witness that the intended Ra was actually imposed.  For the C2
    control it is the witness that the plant is in the solver and not just in
    0.orig/T.
  * `hotFlux`, `coldFlux` -- integral of n.grad(T) over each wall, computed by
    the `grad` function object IN THE SAME PASS, so it carries the scheme's own
    snGrad wall correction.  These give a live Nusselt history: convergence is
    then a statement about the graded quantity, not about a residual.

The `grad` result field carries the private name `k0cGradT` for the reason
recorded in scripts/heat_balance.py: a default name ('grad(T)') collides with
files left by a previous pass and can be silently satisfied by a stale one.
"""

import math
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# fixed physics
# ---------------------------------------------------------------------------
L      = 0.10          # m, cavity side
LZ     = 0.01          # m, one-cell thickness (2-D, empty front/back)
GMAG   = 9.81          # m/s2
TREF   = 300.0         # K
BETA   = 1.0 / TREF    # 1/K, exactly
PR     = 0.71          # gate Section 1.2
NU     = 1.589461e-05  # m2/s
ALPHA  = NU / PR
RHO0   = 1.1614        # kg/m3   } only used to turn the kinematic solve into
CP0    = 1007.0        # J/kg/K  } watts for scripts/heat_balance.py

# reference u2max, used ONLY for the build-time cell-Peclet report above
U2MAX_REF = {1e3: 3.697, 1e4: 19.617, 1e5: 68.22, 1e6: 219.36}


def dT_for(Ra):
    """dT that makes Ra = g.beta.dT.L^3/(nu.alpha) hold exactly."""
    return Ra * NU * ALPHA / (GMAG * BETA * L ** 3)


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


def w(case, loc, obj, cls, body):
    d = os.path.join(case, loc)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, obj), "w") as fh:
        fh.write(HEADER.format(cls=cls, loc=loc, obj=obj) + body + FOOTER)


# ---------------------------------------------------------------------------
# dictionaries
# ---------------------------------------------------------------------------

def blockmesh(n):
    return f"""
scale   1;

vertices
(
    (0.00000 0.00000 0.00000)
    ({L:.5f} 0.00000 0.00000)
    (0.00000 {L:.5f} 0.00000)
    ({L:.5f} {L:.5f} 0.00000)
    (0.00000 0.00000 {LZ:.5f})
    ({L:.5f} 0.00000 {LZ:.5f})
    (0.00000 {L:.5f} {LZ:.5f})
    ({L:.5f} {L:.5f} {LZ:.5f})
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
"""


# The function-object block. `gradT` MUST come first: OpenFOAM executes function
# objects in dictionary order and the two flux integrals consume its result.
FUNCTIONS = """
functions
{
    gradT
    {
        type            grad;
        libs            (fieldFunctionObjects);
        field           T;
        result          k0cGradT;
        executeControl  timeStep;
        executeInterval 50;
        writeControl    none;
        log             false;
    }
    hotFlux
    {
        type            surfaceFieldValue;
        libs            (fieldFunctionObjects);
        regionType      patch;
        name            hotWall;
        operation       areaNormalIntegrate;
        fields          (k0cGradT);
        writeFields     false;
        writeToFile     true;
        log             true;
        executeControl  timeStep;
        executeInterval 50;
        writeControl    timeStep;
        writeInterval   50;
    }
    coldFlux
    {
        type            surfaceFieldValue;
        libs            (fieldFunctionObjects);
        regionType      patch;
        name            coldWall;
        operation       areaNormalIntegrate;
        fields          (k0cGradT);
        writeFields     false;
        writeToFile     true;
        log             true;
        executeControl  timeStep;
        executeInterval 50;
        writeControl    timeStep;
        writeInterval   50;
    }
    hotT
    {
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
        executeInterval 50;
        writeControl    timeStep;
        writeInterval   50;
    }
    coldT
    {
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
        executeInterval 50;
        writeControl    timeStep;
        writeInterval   50;
    }
}
"""


def controldict(end_time):
    return f"""
application     buoyantBoussinesqSimpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {end_time};
deltaT          1;
writeControl    timeStep;
writeInterval   {end_time};
purgeWrite      0;
writeFormat     ascii;
writePrecision  16;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;
{FUNCTIONS}"""


# See the SCHEMES note in the module docstring: central differencing on both
# convection terms, to match the discretisation class of the reference.
FVSCHEMES = """
ddtSchemes
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
"""

FVSOLUTION = """
solvers
{
    p_rgh
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-10;
        relTol          0.01;
    }

    "(U|T)"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-12;
        relTol          0.01;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 0;
    pRefCell        0;
    pRefValue       0;

    residualControl
    {
        p_rgh           1e-07;
        U               1e-08;
        T               1e-08;
    }
}

relaxationFactors
{
    fields
    {
        p_rgh           0.7;
    }
    equations
    {
        U               0.3;
        T               0.5;
    }
}
"""


def transport():
    return f"""
transportModel  Newtonian;

nu              {NU:.6e};
beta            {BETA:.9e};
TRef            {TREF:.1f};
Pr              {PR:.6f};
Prt             0.85;
"""


def gravity(gy):
    return f"""
dimensions      [0 1 -2 0 0 0 0];
value           (0 {gy:.6f} 0);
"""


def field_T(Th, Tc):
    return f"""
dimensions      [0 0 0 1 0 0 0];

internalField   uniform {TREF:.1f};

boundaryField
{{
    hotWall
    {{
        type            fixedValue;
        value           uniform {Th:.9f};
    }}
    coldWall
    {{
        type            fixedValue;
        value           uniform {Tc:.9f};
    }}
    adiabaticWalls
    {{
        type            zeroGradient;
    }}
    frontAndBack
    {{
        type            empty;
    }}
}}
"""


FIELD_U = """
dimensions      [0 1 -1 0 0 0 0];

internalField   uniform (0 0 0);

boundaryField
{
    hotWall         { type noSlip; }
    coldWall        { type noSlip; }
    adiabaticWalls  { type noSlip; }
    frontAndBack    { type empty; }
}
"""

FIELD_PRGH = """
dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    hotWall         { type fixedFluxPressure; value uniform 0; }
    coldWall        { type fixedFluxPressure; value uniform 0; }
    adiabaticWalls  { type fixedFluxPressure; value uniform 0; }
    frontAndBack    { type empty; }
}
"""

FIELD_ALPHAT = """
dimensions      [0 2 -1 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    hotWall         { type calculated; value uniform 0; }
    coldWall        { type calculated; value uniform 0; }
    adiabaticWalls  { type calculated; value uniform 0; }
    frontAndBack    { type empty; }
}
"""


def fvoptions(power_W):
    """A uniform volumetric heat source of exactly `power_W` watts.

    Units: the Boussinesq temperature equation is kinematic (it never sees rho
    or cp), so a scalarSemiImplicitSource on T injects K.m3/s, not watts.  The
    conversion is  S[K.m3/s] = P[W] / (rho.cp).  That is the same rho.cp
    scripts/heat_balance.py uses to turn the same equation into watts, so the
    planted number and the recovered number are in one system of units by
    construction rather than by coincidence.
    """
    S = power_W / (RHO0 * CP0)
    return f"""
heatPlant
{{
    type            scalarSemiImplicitSource;
    selectionMode   all;
    volumeMode      absolute;
    sources
    {{
        T           ({S:.12e} 0);
    }}
}}
"""


# ---------------------------------------------------------------------------
# the case table
# ---------------------------------------------------------------------------
# name -> (Ra, N, endTime, gy, Ra_multiplier_on_dT, planted_source_W)
CASES = {}
GRADED = {}   # Ra -> (coarse case name, fine case name)

for Ra, ncoarse, nfine, end_c, end_f in (
    (1e3, 32, 64, 3000, 3000),
    (1e4, 40, 80, 4000, 4000),
    (1e5, 64, 128, 6000, 6000),
    (1e6, 128, 192, 12000, 12000),
):
    tag = f"Ra{Ra:.0e}".replace("+0", "").replace("e0", "e")
    c = f"{tag}_m{ncoarse}"
    f = f"{tag}_m{nfine}"
    CASES[c] = dict(Ra=Ra, n=ncoarse, end=end_c, gy=-GMAG, mult=1.0, src=None)
    CASES[f] = dict(Ra=Ra, n=nfine, end=end_f, gy=-GMAG, mult=1.0, src=None)
    GRADED[Ra] = (c, f)

# --- controls.  Predictions are registered in analyse_k0c.py's docstring. ----
# C1 RECOGNITION: gravity off on an exact twin of the Ra 1e5 fine case.
CASES["C1_Ra1e5_m128_g0"] = dict(Ra=1e5, n=128, end=3000, gy=0.0, mult=1.0, src=None)
# C2 RECOGNITION AT THE GATE'S OWN SCALE: dT (hence Ra) raised by exactly 10%.
CASES["C2_Ra1e5_m128_dT110"] = dict(Ra=1e5, n=128, end=6000, gy=-GMAG, mult=1.10, src=None)
# C3 REACHABILITY of the energy-balance row: a planted volumetric source.
CASES["C3_Ra1e5_m64_source"] = dict(Ra=1e5, n=64, end=4000, gy=-GMAG, mult=1.0,
                                    src=5.0e-03)


def build(only=None):
    """Build every case, or only the named ones.

    `only` exists because Ra1e6_m192 had to be discarded and rebuilt on its own
    after a watcher script raced and started a second solver in it from time 0
    while the first was still running.  Rebuilding the whole tree to repair one
    case would have thrown away eight good solves, so the selector is the safe
    form of the repair rather than a convenience.
    """
    print("=" * 74)
    print("K0c case build -- F14 cooling ladder, laminar differentially heated cavity")
    print("=" * 74)
    print(f"  L = {L} m   g = {GMAG} m/s2   TRef = {TREF} K   beta = {BETA:.9e} 1/K")
    print(f"  nu = {NU:.6e} m2/s   Pr = {PR}   alpha = nu/Pr = {ALPHA:.6e} m2/s")
    print(f"  rho0 = {RHO0} kg/m3   cp0 = {CP0} J/kg/K   (watts conversion only)")
    print("-" * 74)
    print(f"{'case':<26}{'Ra':>10}{'N':>6}{'dT K':>12}{'beta.dT':>11}{'Pe_cell':>10}{'iters':>8}")
    for name, c in CASES.items():
        if only and name not in only:
            continue
        dT = dT_for(c["Ra"]) * c["mult"]
        Ra_eff = c["Ra"] * c["mult"] * (0.0 if c["gy"] == 0.0 else 1.0)
        pe = U2MAX_REF[c["Ra"]] / c["n"]
        print(f"{name:<26}{Ra_eff:>10.3e}{c['n']:>6}{dT:>12.6f}"
              f"{BETA*dT:>11.5f}{pe:>10.3f}{c['end']:>8}")
        assert BETA * dT < 0.1, f"{name}: beta.dT = {BETA*dT} is not << 1"

        case = os.path.join(HERE, name)
        if os.path.isdir(case):
            shutil.rmtree(case)
        Th = TREF + 0.5 * dT
        Tc = TREF - 0.5 * dT
        w(case, "system", "blockMeshDict", "dictionary", blockmesh(c["n"]))
        w(case, "system", "controlDict", "dictionary", controldict(c["end"]))
        w(case, "system", "fvSchemes", "dictionary", FVSCHEMES)
        w(case, "system", "fvSolution", "dictionary", FVSOLUTION)
        w(case, "constant", "transportProperties", "dictionary", transport())
        w(case, "constant", "g", "uniformDimensionedVectorField", gravity(c["gy"]))
        w(case, "constant", "turbulenceProperties", "dictionary",
          "\nsimulationType  laminar;\n")
        w(case, "constant", "thermalAuditProperties", "dictionary",
          f"\nrho0            {RHO0};\ncp0             {CP0};\n")
        if c["src"] is not None:
            w(case, "constant", "fvOptions", "dictionary", fvoptions(c["src"]))
        w(case, "0.orig", "T", "volScalarField", field_T(Th, Tc))
        w(case, "0.orig", "U", "volVectorField", FIELD_U)
        w(case, "0.orig", "p_rgh", "volScalarField", FIELD_PRGH)
        w(case, "0.orig", "alphat", "volScalarField", FIELD_ALPHAT)

        with open(os.path.join(case, "CASE.txt"), "w") as fh:
            fh.write(
                f"case            {name}\n"
                f"Ra_target       {c['Ra']:.6e}\n"
                f"dT_multiplier   {c['mult']:.6f}\n"
                f"Ra_effective    {c['Ra']*c['mult']:.6e}"
                f"{'  (gravity OFF: buoyancy inactive, effective Ra = 0)' if c['gy']==0 else ''}\n"
                f"mesh            {c['n']} x {c['n']} x 1 uniform\n"
                f"dT              {dT:.9f} K\n"
                f"T_hot           {Th:.9f} K\n"
                f"T_cold          {Tc:.9f} K\n"
                f"g_y             {c['gy']:.6f} m/s2\n"
                f"planted_source  {c['src'] if c['src'] is not None else 'none'} W\n"
                f"endTime         {c['end']}\n")
    print("-" * 74)
    print("  Pe_cell = u2max_ref / N, the cell Peclet number on the T equation.")
    print("  All values above are < 2, which is the condition under which the")
    print("  central-difference convection scheme used here is admissible.")
    print("=" * 74)
    print(f"  graded pairs (coarse, fine): "
          + ", ".join(f"Ra{k:.0e}: {v[0]}/{v[1]}" for k, v in GRADED.items()))
    print("=" * 74)


if __name__ == "__main__":
    build(sys.argv[1:] or None)
    sys.exit(0)
