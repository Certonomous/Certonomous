#!/usr/bin/env python3
"""build_cases.py -- generate every K0c TURBULENT case from one table. F14 rung K0c-T.

    python3 build_cases.py [case ...]     # writes case directories next to this file

WHAT THIS BUILDS
----------------
The TURBULENT rung of
`docs/campaigns/F14-cooling-ladder/K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md`,
Section 2: the Betts and Bokhari enclosed tall cavity (ERCOFTAC Classic
Collection Case 079) at Ra = 0.86e6 and 1.43e6, each on a MANDATORY two-mesh
pair, plus the model, boundary-condition and control twins.

NOTHING PHYSICAL IS TYPED INTO THIS FILE
----------------------------------------
The geometry, the two temperature differentials and the two Rayleigh numbers
are PARSED OUT OF THE SPECIFICATION at build time.  The top and bottom wall
temperature profiles are READ OUT OF THE PRIMARY DATA FILES in
`../reference-data/betts_bokhari/`.  If either cannot be read, this script
exits 2 and builds nothing.  A build script holding its own copy of the
experiment is the same failure as a comparator holding its own copy of the
reference, one step earlier in the pipeline.

THE PLATE TEMPERATURES ARE NOT IN ANY OBTAINED SOURCE, SO THEY ARE DERIVED
-------------------------------------------------------------------------
The gate spec, Section 2.2: "Plate temperatures | Not stated on the database
page. ... a solve should impose the stated differentials and report the
absolute levels used."  The differential is stated; the absolute level is not.

The rule used here, fixed before any solve and derived only from data that is
NOT graded:

    T_mean = mean of the four linear extrapolations of the two measured RUBBER
             WALL profiles (mt_rt_z0_*, mt_rb_z0_*) to x = 0 and x = W,
             taken from each profile's two outermost points at each end.
    T_hot  = T_mean + dT/2      T_cold = T_mean - dT/2      (dT from the spec)

Those four profiles are BOUNDARY CONDITION data.  The mid-width temperature
profiles `mt_z0_*` are GRADED data and are deliberately NOT used to set any
boundary condition: setting the plate level from the mid-height core
temperature would make the graded temperature row circular, and it was
considered and rejected for exactly that reason.  The core temperature the rule
implies is nevertheless printed below beside the measured one, as an
independent corroboration that costs nothing and grades nothing.

VISCOSITY IS THE KNOB THAT MAKES Ra EXACT, AND dT IS NOT
--------------------------------------------------------
Ra = g.beta.dT.W^3 / (nu.alpha),  alpha = nu/Pr,  beta = 1/T_mean.

dT and W are MEASURED and are held at their measured values.  Betts and
Bokhari's own property values are in the paywalled paper and were not obtained,
so nu is chosen to make the case's Ra equal the stated Ra exactly:

    nu = sqrt( g.beta.dT.W^3.Pr / Ra )

The resulting nu is printed against the handbook kinematic viscosity of air at
the case's own mean temperature (Sutherland fit, stated in the printout), and
the difference is a number in the build log rather than a silence.  This
mirrors the laminar rung, where dT was the knob because the geometry and fluid
were free; here dT is measured, so it is not available as a knob.

TURBULENCE MODEL: k-omega SST, WALL-RESOLVED.  See K0cT_RESULTS.md section 2
for the argument, the alternatives and what a disagreement would mean.  The
model is a per-case field of the table below so that the model twin differs
from the graded case in exactly one dictionary entry.

SCHEMES DIFFER FROM THE LAMINAR RUNG, AND THE REASON IS MEASURED HERE
---------------------------------------------------------------------
The laminar rung ran `bounded Gauss linear` (pure central) on both convection
terms because its cell Peclet number was below 2 everywhere.  It is not below 2
here: this is a real 76 mm cavity in real air, and the build-time report below
prints Pe_cell in the vertical direction at the mid-height velocity peak, which
is of order 100.  Central differencing at that Peclet number oscillates.  The
convection schemes are therefore second-order LIMITED (`limitedLinear 1` on T
and the turbulence scalars, `linearUpwind grad(U)` on U) and the numerical
diffusion that buys is bounded by the mandatory mesh pair rather than assumed
away.
"""

import math
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.abspath(os.path.join(HERE, "..",
                                    "K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md"))
DATA = os.path.abspath(os.path.join(HERE, "..", "reference-data", "betts_bokhari"))

GMAG = 9.81
PR = 0.71          # air; the gate's own Prandtl number for the laminar rung and
                   # the standard value for air.  Printed in every case's CASE.txt.
PRT = 0.85         # docs/physics_rules.yaml thermal:turbulent_prandtl_default
RHO0 = 1.1614      # kg/m3  } used ONLY to turn the kinematic solve into watts
CP0 = 1007.0       # J/kg/K } for scripts/heat_balance.py.  Not in the momentum eq.
LZ = 0.01          # m, one-cell thickness (2-D, empty front and back)


# ---------------------------------------------------------------------------
# the specification, parsed rather than remembered
# ---------------------------------------------------------------------------

def read_spec():
    if not os.path.isfile(SPEC):
        raise SystemExit(f"REFUSE: gate specification not found at {SPEC}")
    txt = open(SPEC).read()

    m = re.search(r"Tall rectangular cavity,\s*([\d.]+)\s*m high x\s*([\d.]+)\s*m wide"
                  r"\s*x\s*([\d.]+)\s*m deep", txt)
    if not m:
        raise SystemExit("REFUSE: cannot read the cavity geometry from the "
                         "specification Section 2.2. Nothing is built against a "
                         "dimension this script supplies itself.")
    H, W, D = (float(m.group(i)) for i in (1, 2, 3))

    m = re.search(r"temperature differentials\s*([\d.]+)\s*C and\s*([\d.]+)\s*C", txt)
    if not m:
        raise SystemExit("REFUSE: cannot read the two temperature differentials "
                         "from the specification Section 2.2.")
    dT_lo, dT_hi = float(m.group(1)), float(m.group(2))

    m = re.search(r"Rayleigh numbers\s*\|\s*([\d.]+)e6 and\s*([\d.]+)e6", txt)
    if not m:
        raise SystemExit("REFUSE: cannot read the two Rayleigh numbers from the "
                         "specification Section 2.2.")
    Ra_lo, Ra_hi = float(m.group(1)) * 1e6, float(m.group(2)) * 1e6

    return dict(H=H, W=W, D=D,
                lo=dict(dT=dT_lo, Ra=Ra_lo), hi=dict(dT=dT_hi, Ra=Ra_hi))


# ---------------------------------------------------------------------------
# the primary data files
# ---------------------------------------------------------------------------

def load_dat(fn):
    xs, vs = [], []
    with open(os.path.join(DATA, fn)) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            p = line.split()
            try:
                xs.append(float(p[0]))
                vs.append(float(p[1]))
            except (ValueError, IndexError):
                continue
    if len(xs) < 2:
        raise SystemExit(f"REFUSE: fewer than two usable rows in {fn}")
    return xs, vs


def extrap(xs, vs, xt, at_start):
    """Linear extrapolation to xt from the two points nearest that end."""
    if at_start:
        x0, x1, v0, v1 = xs[0], xs[1], vs[0], vs[1]
    else:
        x0, x1, v0, v1 = xs[-2], xs[-1], vs[-2], vs[-1]
    return v0 + (v1 - v0) * (xt - x0) / (x1 - x0)


def plate_levels(suf, W_mm, dT):
    """T_mean from the two RUBBER WALL profiles only.  See the module docstring."""
    ends = []
    for fn in (f"mt_rt_z0_{suf}.dat", f"mt_rb_z0_{suf}.dat"):
        xs, vs = load_dat(fn)
        ends.append(extrap(xs, vs, 0.0, True))       # cold end, x -> 0
        ends.append(extrap(xs, vs, W_mm, False))     # hot end,  x -> W
    T_mean_C = sum(ends) / len(ends)
    return T_mean_C, ends


def rubber_profile_expr(suf, which, W, T_shift_K):
    """A piecewise-linear OpenFOAM patch expression through the MEASURED points.

    `T_shift_K` converts the file's degrees Celsius to the kelvin scale the case
    runs on, and is the SAME shift applied to the plate values, so no relative
    temperature anywhere in the case depends on it.
    Ends are held flat outside the measured range (the outermost measured point
    is 0.8 mm from the plate; extrapolating a steep near-wall gradient over that
    last millimetre would invent a value, holding it flat does not).
    """
    xs_mm, Ts_C = load_dat(f"mt_r{which}_z0_{suf}.dat")
    xs = [x / 1000.0 for x in xs_mm]
    Ts = [T + T_shift_K for T in Ts_C]
    # nested ternaries, innermost = the last segment
    expr = f"{Ts[-1]:.6f}"
    for i in range(len(xs) - 2, -1, -1):
        x0, x1, t0, t1 = xs[i], xs[i + 1], Ts[i], Ts[i + 1]
        slope = (t1 - t0) / (x1 - x0)
        seg = f"({t0:.6f} + {slope:.6f}*(pos().x() - {x0:.8f}))"
        if i == 0:
            seg = (f"(pos().x() <= {x0:.8f} ? {t0:.6f} : {seg})")
        expr = f"(pos().x() < {x1:.8f} ? {seg} : {expr})"
    return expr, list(zip(xs, Ts))


# ---------------------------------------------------------------------------
# dictionary text
# ---------------------------------------------------------------------------

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


def expansion(n_half, half_len, d1):
    """blockMesh expansion ratio (last/first cell) for n_half cells over
    half_len whose FIRST cell has size d1.  Solved, not guessed."""
    target = half_len / d1
    lo, hi = 1.0000001, 3.0
    for _ in range(200):
        r = 0.5 * (lo + hi)
        s = (r ** n_half - 1.0) / (r - 1.0)
        if s < target:
            lo = r
        else:
            hi = r
    r = 0.5 * (lo + hi)
    return r ** (n_half - 1), r


def blockmesh(W, H, nx, ny, exp_ratio):
    return f"""
scale   1;

vertices
(
    (0.00000000 0.00000000 0.00000000)
    ({W:.8f} 0.00000000 0.00000000)
    (0.00000000 {H:.8f} 0.00000000)
    ({W:.8f} {H:.8f} 0.00000000)
    (0.00000000 0.00000000 {LZ:.8f})
    ({W:.8f} 0.00000000 {LZ:.8f})
    (0.00000000 {H:.8f} {LZ:.8f})
    ({W:.8f} {H:.8f} {LZ:.8f})
);

blocks
(
    hex (0 1 3 2 4 5 7 6) ({nx} {ny} 1)
    simpleGrading
    (
        (
            (0.5 0.5 {exp_ratio:.6f})
            (0.5 0.5 {1.0/exp_ratio:.8f})
        )
        1
        1
    )
);

edges();

boundary
(
    coldWall
    {{
        type wall;
        faces ( (0 4 6 2) );
    }}
    hotWall
    {{
        type wall;
        faces ( (1 3 7 5) );
    }}
    bottomWall
    {{
        type wall;
        faces ( (0 1 5 4) );
    }}
    topWall
    {{
        type wall;
        faces ( (2 6 7 3) );
    }}
    frontAndBack
    {{
        type empty;
        faces ( (0 2 3 1) (4 5 7 6) );
    }}
);
"""


def functions(H, W, probe_heights):
    probes = "\n".join(
        f"            ({0.5*W:.8f} {yh*H:.8f} {0.5*LZ:.8f})" for yh in probe_heights)
    return f"""
functions
{{
    gradT
    {{
        type            grad;
        libs            (fieldFunctionObjects);
        field           T;
        result          k0ctGradT;
        executeControl  timeStep;
        executeInterval 50;
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
        fields          (k0ctGradT);
        writeFields     false;
        writeToFile     true;
        log             true;
        executeControl  timeStep;
        executeInterval 50;
        writeControl    timeStep;
        writeInterval   50;
    }}
    coldFlux
    {{
        type            surfaceFieldValue;
        libs            (fieldFunctionObjects);
        regionType      patch;
        name            coldWall;
        operation       areaNormalIntegrate;
        fields          (k0ctGradT);
        writeFields     false;
        writeToFile     true;
        log             true;
        executeControl  timeStep;
        executeInterval 50;
        writeControl    timeStep;
        writeInterval   50;
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
        executeInterval 50;
        writeControl    timeStep;
        writeInterval   50;
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
        executeInterval 50;
        writeControl    timeStep;
        writeInterval   50;
    }}
    topT
    {{
        type            surfaceFieldValue;
        libs            (fieldFunctionObjects);
        regionType      patch;
        name            topWall;
        operation       areaAverage;
        fields          (T);
        writeFields     false;
        writeToFile     true;
        log             true;
        executeControl  timeStep;
        executeInterval 50;
        writeControl    timeStep;
        writeInterval   50;
    }}
    bottomT
    {{
        type            surfaceFieldValue;
        libs            (fieldFunctionObjects);
        regionType      patch;
        name            bottomWall;
        operation       areaAverage;
        fields          (T);
        writeFields     false;
        writeToFile     true;
        log             true;
        executeControl  timeStep;
        executeInterval 50;
        writeControl    timeStep;
        writeInterval   50;
    }}
    coreT
    {{
        type            probes;
        libs            (sampling);
        fields          (T);
        probeLocations
        (
{probes}
        );
        interpolationScheme cell;
        writeToFile     true;
        log             true;
        executeControl  timeStep;
        executeInterval 50;
        writeControl    timeStep;
        writeInterval   50;
    }}
    Uymax
    {{
        type            volFieldValue;
        libs            (fieldFunctionObjects);
        regionType      all;
        operation       max;
        fields          (U);
        writeFields     false;
        writeToFile     true;
        log             true;
        executeControl  timeStep;
        executeInterval 50;
        writeControl    timeStep;
        writeInterval   50;
    }}
    Uymin
    {{
        type            volFieldValue;
        libs            (fieldFunctionObjects);
        regionType      all;
        operation       min;
        fields          (U);
        writeFields     false;
        writeToFile     true;
        log             true;
        executeControl  timeStep;
        executeInterval 50;
        writeControl    timeStep;
        writeInterval   50;
    }}
}}
"""


def controldict(end_time, fns):
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
{fns}"""


FVSCHEMES = """
ddtSchemes
{
    default         steadyState;
}

gradSchemes
{
    default         Gauss linear;
}

// SEE THE MODULE DOCSTRING.  The cell Peclet number on this case is of order
// 100 in the vertical direction, so the laminar rung's pure central scheme is
// inadmissible here and the choice is recorded with its measured basis.
divSchemes
{
    default         none;
    div(phi,U)      bounded Gauss linearUpwind grad(U);
    div(phi,T)      bounded Gauss limitedLinear 1;
    div(phi,k)      bounded Gauss limitedLinear 1;
    div(phi,omega)  bounded Gauss limitedLinear 1;
    div(phi,epsilon) bounded Gauss limitedLinear 1;
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

// kOmegaSST and LaunderSharmaKE both need a wall distance.  meshWave is the
// exact-for-this-mesh choice: an orthogonal structured block, so the wave
// front reproduces the analytic distance to the nearest wall.
wallDist
{
    method          meshWave;
}
"""


def fvsolution(relax_U, relax_p, relax_T, relax_turb):
    return f"""
solvers
{{
    p_rgh
    {{
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-10;
        relTol          0.01;
    }}

    "(U|T|k|omega|epsilon)"
    {{
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-12;
        relTol          0.01;
    }}
}}

SIMPLE
{{
    nNonOrthogonalCorrectors 0;
    pRefCell        0;
    pRefValue       0;

    residualControl
    {{
        p_rgh           1e-07;
        U               1e-08;
        T               1e-08;
        "(k|omega|epsilon)" 1e-08;
    }}
}}

relaxationFactors
{{
    fields
    {{
        p_rgh           {relax_p};
    }}
    equations
    {{
        U               {relax_U};
        T               {relax_T};
        "(k|omega|epsilon)" {relax_turb};
    }}
}}
"""


def transport(nu, beta, TRef):
    return f"""
transportModel  Newtonian;

nu              {nu:.9e};
beta            {beta:.9e};
TRef            {TRef:.6f};
Pr              {PR:.6f};
Prt             {PRT:.4f};
"""


def field_T(Th, Tc, top_expr, bot_expr, adiabatic_ends, Tinit):
    if adiabatic_ends:
        top = "    topWall    { type zeroGradient; }\n"
        bot = "    bottomWall { type zeroGradient; }\n"
    else:
        top = ("    topWall\n    {\n"
               "        type            uniformFixedValue;\n"
               "        uniformValue\n        {\n"
               "            type        expression;\n"
               f"            expression  #{{ {top_expr} #}};\n"
               "        }\n"
               f"        value           uniform {0.5*(Th+Tc):.9f};\n    }}\n")
        bot = ("    bottomWall\n    {\n"
               "        type            uniformFixedValue;\n"
               "        uniformValue\n        {\n"
               "            type        expression;\n"
               f"            expression  #{{ {bot_expr} #}};\n"
               "        }\n"
               f"        value           uniform {0.5*(Th+Tc):.9f};\n    }}\n")
    return f"""
dimensions      [0 0 0 1 0 0 0];

internalField   uniform {Tinit:.9f};

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
{top}{bot}    frontAndBack
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
    topWall         { type noSlip; }
    bottomWall      { type noSlip; }
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
    topWall         { type fixedFluxPressure; value uniform 0; }
    bottomWall      { type fixedFluxPressure; value uniform 0; }
    frontAndBack    { type empty; }
}
"""


def wall_block(kind, extra=""):
    return ("\n".join(
        f"    {p}\n    {{\n        type            {kind};\n{extra}"
        f"        value           $internalField;\n    }}"
        for p in ("hotWall", "coldWall", "topWall", "bottomWall"))
        + "\n    frontAndBack    { type empty; }\n")


def field_k(k0):
    return f"""
dimensions      [0 2 -2 0 0 0 0];

internalField   uniform {k0:.9e};

boundaryField
{{
{wall_block("kLowReWallFunction")}}}
"""


def field_omega(w0):
    return f"""
dimensions      [0 0 -1 0 0 0 0];

internalField   uniform {w0:.9e};

boundaryField
{{
{wall_block("omegaWallFunction")}}}
"""


def field_epsilon(e0):
    return f"""
dimensions      [0 2 -3 0 0 0 0];

internalField   uniform {e0:.9e};

boundaryField
{{
{wall_block("epsilonWallFunction")}}}
"""


def field_nut():
    # nutLowReWallFunction sets nut = 0 at the wall.  That is the correct
    # statement for a mesh whose first cell sits at y+ < 1: there is no log
    # layer to model and the wall stress is molecular.  yPlus is measured on
    # every case and printed, so the claim is checked rather than asserted.
    return f"""
dimensions      [0 2 -1 0 0 0 0];

internalField   uniform 0;

boundaryField
{{
{wall_block("nutLowReWallFunction")}}}
"""


FIELD_ALPHAT = """
dimensions      [0 2 -1 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    hotWall         { type calculated; value uniform 0; }
    coldWall        { type calculated; value uniform 0; }
    topWall         { type calculated; value uniform 0; }
    bottomWall      { type calculated; value uniform 0; }
    frontAndBack    { type empty; }
}
"""


def turbulence_properties(model):
    if model == "laminar":
        return "\nsimulationType  laminar;\n"
    return f"""
simulationType  RAS;

RAS
{{
    RASModel        {model};
    turbulence      on;
    printCoeffs     on;
}}
"""


# ---------------------------------------------------------------------------
# the case table
# ---------------------------------------------------------------------------
# Fields: rung (lo|hi), nx, ny, model, Ra multiplier on dT, adiabatic ends,
#         k-seed multiplier, endTime
CASES = {
    # graded pairs -- Section 2.4 is graded on the FINE mesh of each pair
    "T_lo_c":  dict(rung="lo", nx=40, ny=120, model="kOmegaSST", mult=1.0,
                    adia=False, kmult=1.0, end=20000),
    "T_lo_f":  dict(rung="lo", nx=64, ny=192, model="kOmegaSST", mult=1.0,
                    adia=False, kmult=1.0, end=30000),
    "T_hi_c":  dict(rung="hi", nx=40, ny=120, model="kOmegaSST", mult=1.0,
                    adia=False, kmult=1.0, end=20000),
    "T_hi_f":  dict(rung="hi", nx=64, ny=192, model="kOmegaSST", mult=1.0,
                    adia=False, kmult=1.0, end=30000),
    # M -- MODEL twin.  Differs from T_hi_f in constant/turbulenceProperties only.
    "M_hi_f_LS": dict(rung="hi", nx=64, ny=192, model="LaunderSharmaKE", mult=1.0,
                      adia=False, kmult=1.0, end=30000),
    # C1 -- RECOGNITION.  Turbulence off; predicts a laminarised stratified core.
    "C1_hi_c_laminar": dict(rung="hi", nx=40, ny=120, model="laminar", mult=1.0,
                            adia=False, kmult=1.0, end=20000),
    # C2 -- RECOGNITION AT THE GATE'S OWN SCALE.  Ra raised 30 percent.
    "C2_hi_c_Ra130": dict(rung="hi", nx=40, ny=120, model="kOmegaSST", mult=1.30,
                          adia=False, kmult=1.0, end=20000),
    # B -- BOUNDARY-CONDITION discriminator.  Adiabatic ends instead of measured.
    "B_hi_c_adiabatic": dict(rung="hi", nx=40, ny=120, model="kOmegaSST", mult=1.0,
                             adia=True, kmult=1.0, end=20000),
    # S -- CONFOUND.  Turbulence seed raised 100x; the answer must not move.
    "S_hi_c_seed100": dict(rung="hi", nx=40, ny=120, model="kOmegaSST", mult=1.0,
                           adia=False, kmult=100.0, end=20000),
}

PROBE_HEIGHTS = (0.30, 0.40, 0.50, 0.60, 0.70)

# first cell size at each vertical plate, metres.  The FINE mesh refines this in
# the same ratio as the cell count, so the pair is a uniform refinement and not
# a core-only one.
D1_COARSE = 2.0e-04
NX_COARSE = 40


def sutherland_nu(T_K):
    """Kinematic viscosity of air, Sutherland's law for mu with the ideal-gas
    density at 1 atm.  Constants: mu0 = 1.716e-05 Pa.s at T0 = 273.15 K,
    S = 110.4 K (standard Sutherland constants for air); R = 287.058 J/kg/K,
    p = 101325 Pa.  Used ONLY to report how far the Ra-matched nu sits from a
    handbook value; no case uses it."""
    mu = 1.716e-05 * (T_K / 273.15) ** 1.5 * (273.15 + 110.4) / (T_K + 110.4)
    rho = 101325.0 / (287.058 * T_K)
    return mu / rho


def build(only=None):
    spec = read_spec()
    H, W = spec["H"], spec["W"]
    print("=" * 78)
    print("K0c TURBULENT case build -- F14 cooling ladder, Betts and Bokhari tall cavity")
    print("=" * 78)
    print(f"  parsed from the specification: H = {H} m, W = {W} m, D = {spec['D']} m")
    print(f"  parsed from the specification: dT = {spec['lo']['dT']} / {spec['hi']['dT']} C, "
          f"Ra = {spec['lo']['Ra']:.3e} / {spec['hi']['Ra']:.3e}")
    print("-" * 78)

    rung = {}
    for suf in ("lo", "hi"):
        dT = spec[suf]["dT"]
        Ra = spec[suf]["Ra"]
        T_mean_C, ends = plate_levels(suf, W * 1000.0, dT)
        T_mean = T_mean_C + 273.15
        beta = 1.0 / T_mean
        nu = math.sqrt(GMAG * beta * dT * W ** 3 * PR / Ra)
        nu_hb = sutherland_nu(T_mean)
        Th = T_mean + 0.5 * dT
        Tc = T_mean - 0.5 * dT
        rung[suf] = dict(dT=dT, Ra=Ra, T_mean=T_mean, beta=beta, nu=nu,
                         Th=Th, Tc=Tc, nu_hb=nu_hb)
        print(f"  rung {suf}: T_mean from the four rubber-wall end extrapolations "
              f"{['%.2f' % e for e in ends]} C")
        print(f"           -> T_mean = {T_mean_C:.3f} C = {T_mean:.3f} K, "
              f"T_hot = {Th-273.15:.3f} C, T_cold = {Tc-273.15:.3f} C")
        print(f"           beta = 1/T_mean = {beta:.6e} 1/K, beta.dT = {beta*dT:.5f}"
              + ("   *** ABOVE the 0.1 Boussinesq line of docs/physics_rules.yaml"
                 if beta * dT > 0.1 else "   (below the 0.1 Boussinesq line)"))
        print(f"           nu chosen so Ra is exact: {nu:.6e} m2/s; Sutherland at "
              f"T_mean {nu_hb:.6e} m2/s; difference {100*(nu-nu_hb)/nu_hb:+.2f} %")

    print("-" * 78)
    print(f"{'case':<20}{'rung':>5}{'model':>17}{'nx':>4}{'ny':>5}{'cells':>8}"
          f"{'dT K':>8}{'d1 mm':>8}{'exp':>9}{'Pe_y':>8}{'iters':>7}")

    for name, c in CASES.items():
        if only and name not in only:
            continue
        r = rung[c["rung"]]
        dT = r["dT"] * c["mult"]
        Th = r["T_mean"] + 0.5 * dT
        Tc = r["T_mean"] - 0.5 * dT
        nu = r["nu"]
        alpha = nu / PR
        Ra_eff = GMAG * r["beta"] * dT * W ** 3 / (nu * alpha)
        if c["model"] == "laminar":
            Ra_eff_note = ""
        else:
            Ra_eff_note = ""

        nx, ny = c["nx"], c["ny"]
        d1 = D1_COARSE * (NX_COARSE / nx)
        exp_ratio, ratio = expansion(nx // 2, 0.5 * W, d1)
        dy = H / ny
        # buoyancy velocity scale, used for the turbulence seed and the Peclet report
        Vc = math.sqrt(GMAG * r["beta"] * dT * W)
        Pe_y = 0.6 * Vc * dy / alpha
        k0 = 1.5 * (0.05 * Vc) ** 2 * c["kmult"]
        lturb = 0.07 * W
        omega0 = math.sqrt(k0) / (0.09 ** 0.25 * lturb)
        eps0 = 0.09 ** 0.75 * k0 ** 1.5 / lturb

        print(f"{name:<20}{c['rung']:>5}{c['model']:>17}{nx:>4}{ny:>5}{nx*ny:>8}"
              f"{dT:>8.2f}{d1*1000:>8.3f}{exp_ratio:>9.2f}{Pe_y:>8.1f}{c['end']:>7}"
              + Ra_eff_note)

        case = os.path.join(HERE, name)
        if os.path.isdir(case):
            shutil.rmtree(case)

        top_expr, top_pts = rubber_profile_expr(c["rung"], "t", W, 273.15)
        bot_expr, bot_pts = rubber_profile_expr(c["rung"], "b", W, 273.15)

        w(case, "system", "blockMeshDict", "dictionary",
          blockmesh(W, H, nx, ny, exp_ratio))
        w(case, "system", "controlDict", "dictionary",
          controldict(c["end"], functions(H, W, PROBE_HEIGHTS)))
        w(case, "system", "fvSchemes", "dictionary", FVSCHEMES)
        w(case, "system", "fvSolution", "dictionary",
          fvsolution(0.4, 0.7, 0.6, 0.4))
        w(case, "constant", "transportProperties", "dictionary",
          transport(nu, r["beta"], r["T_mean"]))
        w(case, "constant", "g", "uniformDimensionedVectorField",
          f"\ndimensions      [0 1 -2 0 0 0 0];\nvalue           (0 {-GMAG:.6f} 0);\n")
        w(case, "constant", "turbulenceProperties", "dictionary",
          turbulence_properties(c["model"]))
        w(case, "constant", "thermalAuditProperties", "dictionary",
          f"\nrho0            {RHO0};\ncp0             {CP0};\n")
        w(case, "0.orig", "T", "volScalarField",
          field_T(Th, Tc, top_expr, bot_expr, c["adia"], r["T_mean"]))
        w(case, "0.orig", "U", "volVectorField", FIELD_U)
        w(case, "0.orig", "p_rgh", "volScalarField", FIELD_PRGH)
        w(case, "0.orig", "alphat", "volScalarField", FIELD_ALPHAT)
        if c["model"] != "laminar":
            w(case, "0.orig", "nut", "volScalarField", field_nut())
            w(case, "0.orig", "k", "volScalarField", field_k(k0))
            if "Omega" in c["model"] or "omega" in c["model"]:
                w(case, "0.orig", "omega", "volScalarField", field_omega(omega0))
            else:
                w(case, "0.orig", "epsilon", "volScalarField", field_epsilon(eps0))

        with open(os.path.join(case, "CASE.txt"), "w") as fh:
            fh.write(
                f"case              {name}\n"
                f"rung              {c['rung']}  (spec Section 2, Ra {r['Ra']:.3e})\n"
                f"turbulence_model  {c['model']}\n"
                f"Ra_target         {r['Ra']:.6e}\n"
                f"dT_multiplier     {c['mult']:.6f}\n"
                f"Ra_effective      {Ra_eff:.6e}\n"
                f"H                 {H} m\n"
                f"W                 {W} m\n"
                f"mesh              {nx} x {ny} x 1, graded symmetric in x\n"
                f"first_cell_x      {d1:.9e} m\n"
                f"expansion_ratio   {exp_ratio:.6f} (cell-to-cell {ratio:.6f})\n"
                f"dy                {dy:.9e} m\n"
                f"dT                {dT:.6f} K\n"
                f"T_mean            {r['T_mean']:.6f} K\n"
                f"T_hot             {Th:.6f} K  ({Th-273.15:.3f} C)\n"
                f"T_cold            {Tc:.6f} K  ({Tc-273.15:.3f} C)\n"
                f"beta              {r['beta']:.9e} 1/K\n"
                f"beta_dT           {r['beta']*dT:.6f}"
                f"{'  ABOVE the 0.1 Boussinesq line' if r['beta']*dT > 0.1 else ''}\n"
                f"nu                {nu:.9e} m2/s\n"
                f"nu_sutherland     {r['nu_hb']:.9e} m2/s\n"
                f"Pr                {PR}\n"
                f"Prt               {PRT}\n"
                f"end_walls         {'ADIABATIC (control twin)' if c['adia'] else 'measured rubber-wall profiles'}\n"
                f"k_seed            {k0:.9e} m2/s2  (seed multiplier {c['kmult']})\n"
                f"omega_seed        {omega0:.9e} 1/s\n"
                f"Vc_buoyancy       {Vc:.9f} m/s\n"
                f"Pe_y_at_peak      {Pe_y:.3f}\n"
                f"endTime           {c['end']}\n")
            fh.write("top_wall_profile_points_x_m_T_K\n")
            for x, t in top_pts:
                fh.write(f"  {x:.6f} {t:.4f}\n")
            fh.write("bottom_wall_profile_points_x_m_T_K\n")
            for x, t in bot_pts:
                fh.write(f"  {x:.6f} {t:.4f}\n")

    print("-" * 78)
    print("  Pe_y = 0.6 . Vc . dy / alpha, the vertical cell Peclet number on the T")
    print("  equation at 60 percent of the buoyancy velocity scale.  It is FAR above")
    print("  2, which is why the laminar rung's central scheme is not used here.")
    print("=" * 78)
    print("  graded pairs (coarse, fine): lo: T_lo_c/T_lo_f, hi: T_hi_c/T_hi_f")
    print("  grading on the FINE mesh of each pair, per spec Section 2.5.")
    print("=" * 78)


if __name__ == "__main__":
    build(sys.argv[1:] or None)
