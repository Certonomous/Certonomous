#!/usr/bin/env python3
"""
T1c builder: fully developed laminar pipe flow, against closed-form theory.

Written to the specification in
docs/campaigns/T-family/T1_FORCED_CONVECTION_CANON_PREREGISTRATION.md 2,
BEFORE any case was solved.

DESIGN NOTES THAT ARE DECISIONS, NOT DEFAULTS:

  * AXISYMMETRIC WEDGE, not a 2D slab.  The reference constants 3.657 and 48/11
    are for a CIRCULAR pipe.  A planar duct has different constants entirely
    (7.541 and 8.235), so a slab mesh would be graded against the wrong number
    and would look like a model error.

  * THE GRADED QUANTITY NEEDS NO PROPERTY CONSTANTS.  Both wall conditions
    reduce to  Nu = D (dT/dn)_wall / (T_wall - T_bulk), so density, specific
    heat and conductivity cancel identically.  Nothing can be wrong because a
    property was mistyped.

  * L = 50 D against a thermal entry length of 0.05 Re Pr D = 3.55 D.  Nusselt
    is sampled at x/D = 40, which is more than eleven entry lengths downstream.
    The margin is deliberate: the whole point of this rung is that the answer is
    the FULLY DEVELOPED constant, and an entrance contamination would masquerade
    as a discretisation error.

  * THREE MESH LEVELS at a ratio of 1.6, because a two-level ladder cannot
    produce an observed order.  K0cS has two levels and that gap is the entire
    reason K0cG exists; this rung does not repeat it.

  * writeInterval STRICTLY LESS THAN endTime (D432 / LESSONS.md L-140).  A run
    whose only field write is at endTime loses everything to one interruption.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- physical setup --------------------------------------------------------
D = 0.02                 # pipe diameter [m]
R = D / 2.0
L = 50.0 * D             # 1.0 m
NU = 1.5e-5              # kinematic viscosity [m2/s]
PR = 0.71                # Prandtl number (air)
RE = 100.0               # Reynolds number, safely laminar (transition ~2300)
U = RE * NU / D          # bulk velocity [m/s]
T_IN = 300.0             # inlet temperature [K]
T_WALL = 310.0           # constant-wall-temperature case [K]
DTDN = 500.0             # constant-flux case: wall temperature gradient [K/m]
WEDGE_DEG = 5.0

# ---- mesh ladder, ratio 1.6 ------------------------------------------------
LEVELS = {"c": (20, 200), "m": (32, 320), "f": (51, 512)}   # (radial, axial)

END_TIME = 6000
WRITE_INTERVAL = 1000     # STRICTLY < END_TIME.  See L-140.

CASES = {}
for lvl, (nr, nx) in LEVELS.items():
    CASES[f"L_Ts_{lvl}"] = dict(level=lvl, nr=nr, nx=nx, wall="fixedTemperature")
    CASES[f"L_q_{lvl}"] = dict(level=lvl, nr=nr, nx=nx, wall="fixedFlux")


def header(cls, obj, loc):
    return f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       {cls};
    location    "{loc}";
    object      {obj};
}}
"""


def block_mesh(nr, nx):
    import math
    h = math.radians(WEDGE_DEG / 2.0)
    y = R * math.cos(h)
    z = R * math.sin(h)
    return header("dictionary", "blockMeshDict", "system") + f"""
scale 1;

vertices
(
    (0            0             0)
    ({L:.8f}      0             0)
    ({L:.8f}      {y:.10f}      {-z:.10f})
    (0            {y:.10f}      {-z:.10f})
    (0            {y:.10f}      {z:.10f})
    ({L:.8f}      {y:.10f}      {z:.10f})
);

blocks
(
    hex (0 1 2 3 0 1 5 4) ({nx} {nr} 1) simpleGrading (1 1 1)
);

edges ();

boundary
(
    inlet   {{ type patch; faces ( (0 3 4 0) ); }}
    outlet  {{ type patch; faces ( (1 2 5 1) ); }}
    wall    {{ type wall;  faces ( (3 2 5 4) ); }}
    front   {{ type wedge; faces ( (0 1 5 4) ); }}
    back    {{ type wedge; faces ( (0 1 2 3) ); }}
    axis    {{ type empty; faces ( ); }}
);

mergePatchPairs ();
"""


def field_U():
    return header("volVectorField", "U", "0") + f"""
dimensions      [0 1 -1 0 0 0 0];
internalField   uniform ({U:.10g} 0 0);
boundaryField
{{
    inlet   {{ type fixedValue; value uniform ({U:.10g} 0 0); }}
    outlet  {{ type zeroGradient; }}
    wall    {{ type noSlip; }}
    front   {{ type wedge; }}
    back    {{ type wedge; }}
}}
"""


def field_p():
    return header("volScalarField", "p_rgh", "0") + """
dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0;
boundaryField
{
    inlet   { type zeroGradient; }
    outlet  { type fixedValue; value uniform 0; }
    wall    { type zeroGradient; }
    front   { type wedge; }
    back    { type wedge; }
}
"""


def field_T(wall):
    if wall == "fixedTemperature":
        wb = f"{{ type fixedValue; value uniform {T_WALL:.10g}; }}"
    else:
        wb = (f"{{ type fixedGradient; gradient uniform {DTDN:.10g}; }}")
    return header("volScalarField", "T", "0") + f"""
dimensions      [0 0 0 1 0 0 0];
internalField   uniform {T_IN:.10g};
boundaryField
{{
    inlet   {{ type fixedValue; value uniform {T_IN:.10g}; }}
    outlet  {{ type zeroGradient; }}
    wall    {wb}
    front   {{ type wedge; }}
    back    {{ type wedge; }}
}}
"""


def field_alphat():
    return header("volScalarField", "alphat", "0") + """
dimensions      [0 2 -1 0 0 0 0];
internalField   uniform 0;
boundaryField
{
    inlet   { type calculated; value uniform 0; }
    outlet  { type calculated; value uniform 0; }
    wall    { type fixedValue; value uniform 0; }
    front   { type wedge; }
    back    { type wedge; }
}
"""


def transport():
    return header("dictionary", "transportProperties", "constant") + f"""
transportModel  Newtonian;
nu              {NU:.10g};
beta            0;
TRef            {T_IN:.10g};
Pr              {PR:.10g};
Prt             0.85;
"""


def turbulence_properties():
    # THE DICTIONARY NAME IS FORK-SPECIFIC AND THE FIRST BUILD GOT IT WRONG.
    # `constant/momentumTransport` is the OpenFOAM Foundation (.org) name; the
    # solver installed here is ESI OpenFOAM v2606, which reads
    # `constant/turbulenceProperties` and dies at "Creating turbulence model"
    # without it.  All six cases failed identically at startup, before any
    # iteration, on the first build.
    #
    # Checked against this lab's OWN working cases rather than against a memory
    # of which fork uses which name: K0cT/T_hi_c and the K0cG cases running at
    # the time both carry constant/turbulenceProperties, as does the shipped
    # buoyantBoussinesqSimpleFoam/hotRoom tutorial.  For a laminar run the ESI
    # form is the bare `simulationType laminar;` with no sub-dictionary.
    return header("dictionary", "turbulenceProperties", "constant") + """
simulationType  laminar;
"""


def gravity():
    # ZERO GRAVITY IS THE POINT.  buoyantBoussinesqSimpleFoam with g = 0 is pure
    # forced convection, and its momentum solution must then be independent of
    # the temperature field entirely -- the control registered in K0e 4.2.
    return header("uniformDimensionedVectorField", "g", "constant") + """
dimensions      [0 1 -2 0 0 0 0];
value           (0 0 0);
"""


def control_dict():
    return header("dictionary", "controlDict", "system") + f"""
application     buoyantBoussinesqSimpleFoam;
startFrom       latestTime;
startTime       0;
stopAt          endTime;
endTime         {END_TIME};
deltaT          1;
writeControl    timeStep;
writeInterval   {WRITE_INTERVAL};
purgeWrite      2;
writeFormat     ascii;
writePrecision  16;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;
"""


def fv_schemes():
    return header("dictionary", "fvSchemes", "system") + """
ddtSchemes      { default steadyState; }
gradSchemes     { default Gauss linear; }
divSchemes
{
    default         none;
    div(phi,U)      bounded Gauss linear;
    div(phi,T)      bounded Gauss linear;
    div(phi,k)      bounded Gauss limitedLinear 1;
    div(phi,epsilon) bounded Gauss limitedLinear 1;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes   { default corrected; }
"""


def fv_solution():
    return header("dictionary", "fvSolution", "system") + """
solvers
{
    p_rgh
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-12;
        relTol          0.001;
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
    residualControl { p_rgh 1e-9; U 1e-9; T 1e-9; }
}
relaxationFactors
{
    fields { p_rgh 0.3; }
    equations { U 0.7; T 0.7; }
}
"""


def case_txt(name, c):
    import math
    le_h = 0.05 * RE * D
    le_t = 0.05 * RE * PR * D
    return f"""case              {name}
rung              T1c (fully developed laminar pipe, closed-form reference)
level             {c['level']}  ({c['nr']} radial x {c['nx']} axial)
wall_condition    {c['wall']}
D                 {D} m
R                 {R} m
L                 {L} m  ({L/D:.1f} D)
nu                {NU} m2/s
Pr                {PR}
Re                {RE}
U                 {U:.10g} m/s
T_in              {T_IN} K
T_wall            {T_WALL} K   (used only by the fixedTemperature arm)
dTdn_wall         {DTDN} K/m   (used only by the fixedFlux arm)
entry_hydro       {le_h:.6g} m  ({le_h/D:.2f} D)
entry_thermal     {le_t:.6g} m  ({le_t/D:.2f} D)
sample_x          {40.0*D:.6g} m  (40 D, {40.0*D/le_t:.1f} thermal entry lengths)
endTime           {END_TIME}
writeInterval     {WRITE_INTERVAL}
reference_Nu_Ts   3.6567934  (first Graetz eigenvalue / 2)
reference_Nu_q    4.3636364  (48/11)
reference_fRe     64
"""


def main():
    made = []
    for name, c in sorted(CASES.items()):
        d = os.path.join(HERE, name)
        if os.path.exists(d):
            shutil.rmtree(d)
        for sub in ("0.orig", "constant", "system"):
            os.makedirs(os.path.join(d, sub))
        w = lambda rel, txt: open(os.path.join(d, rel), "w").write(txt)
        w("system/blockMeshDict", block_mesh(c["nr"], c["nx"]))
        w("system/controlDict", control_dict())
        w("system/fvSchemes", fv_schemes())
        w("system/fvSolution", fv_solution())
        w("constant/transportProperties", transport())
        w("constant/turbulenceProperties", turbulence_properties())
        w("constant/g", gravity())
        w("0.orig/U", field_U())
        w("0.orig/p_rgh", field_p())
        w("0.orig/T", field_T(c["wall"]))
        w("0.orig/alphat", field_alphat())
        w("CASE.txt", case_txt(name, c))
        made.append((name, c["nr"] * c["nx"], c["wall"]))

    print(f"T1c: {len(made)} cases built in {HERE}")
    print(f"  Re = {RE}, U = {U:.6g} m/s, Pr = {PR}, L/D = {L/D:.0f}")
    print(f"  thermal entry length {0.05*RE*PR*D/D:.2f} D; Nu sampled at 40 D")
    print(f"  endTime {END_TIME}, writeInterval {WRITE_INTERVAL} (STRICTLY less)")
    print(f"\n  {'case':12s} {'cells':>8s}  wall condition")
    for n, cells, wall in made:
        print(f"  {n:12s} {cells:8d}  {wall}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
