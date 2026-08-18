#!/usr/bin/env python3
"""build_cases.py -- build the F14 K0cS square-cavity turbulent cases.

    python3 build_cases.py            # writes every case directory

THE CASE IS BUILT FROM THE SPECIFICATION, NOT FROM CONSTANTS TYPED HERE
-----------------------------------------------------------------------
Geometry, plate temperatures, Rayleigh number and the measured horizontal-wall
temperature profile are parsed at run time out of

    docs/campaigns/F14-cooling-ladder/K0cS_SQUARE_CAVITY_GATE.md

Sections 1 and 2.3.  If the specification cannot be parsed this script exits 2
rather than fall back to anything.  The same discipline the K0cT rung used, for
the same reason: a builder holding its own copy of the case is a builder that
can drift away from the document that grades it.

THE HORIZONTAL WALLS ARE THE MEASURED PROFILE, NOT AN IDEALISATION
------------------------------------------------------------------
Specification Section 2.2 records that the adiabatic and perfectly conducting
idealisations differ from each other by 13 percent on average Nusselt (Beghein
et al. via Tian p. 861), which is larger than every band on the gate.  Choosing
either one would decide the verdict by a boundary condition.  Ampofo Table 4
(p. 3558) tabulates what the walls actually did, and that is what is imposed,
as a piecewise-linear uniformFixedValue expression on both horizontal walls.

BOUSSINESQ IS STRAINED ON THIS CASE AND THAT IS RECORDED, NOT HIDDEN
--------------------------------------------------------------------
beta.dT = 0.132 at T_mean, above the 0.1 line in docs/physics_rules.yaml.
Ampofo p. 3564 measured the consequence directly: the 40 K difference causes
about 11 percent density difference.  Two gate rows are reported rather than
graded for this reason and the specification says which (Section 3.3).
"""

import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
SPEC = os.path.join(REPO, "docs", "campaigns", "F14-cooling-ladder",
                    "K0cS_SQUARE_CAVITY_GATE.md")

GMAG = 9.81
PR = 0.71
PRT = 0.85

NX_COARSE, NY_COARSE = 120, 120
NX_FINE, NY_FINE = 192, 192
D1_COARSE = 2.5e-4          # first cell off every wall, coarse mesh, metres
REFINE = 1.6                # 192/120, the specification's minimum is 1.5

# mid-width stations for the stratification fit, specification Section 2.5:
# the window was FIXED at Y = 0.30 to 0.70 because the window sensitivity
# (0.16 in Sp) exceeds any model-to-model difference this rung can resolve.
PROBE_Y = (0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70)


def die(msg):
    sys.stderr.write(msg + "\n")
    raise SystemExit(2)


# ---------------------------------------------------------------------------
# the specification
# ---------------------------------------------------------------------------

def read_spec():
    if not os.path.isfile(SPEC):
        die(f"REFUSE: specification not found at {SPEC}")
    txt = open(SPEC).read()

    m = re.search(r"Geometry \| ([\d.]+) m high x ([\d.]+) m wide", txt)
    if not m:
        die("REFUSE: the Section 1 geometry row could not be read.")
    H, L = float(m.group(1)), float(m.group(2))
    if abs(H - L) > 1e-12:
        die("REFUSE: this builder is for a SQUARE cavity; the specification "
            f"gives {H} x {L}.")

    m = re.search(r"Hot wall \(x = 0\) \| Isothermal, ([\d.]+) \+/- ([\d.]+) C", txt)
    if not m:
        die("REFUSE: the Section 1 hot wall row could not be read.")
    Th_C = float(m.group(1))
    m = re.search(r"Cold wall \(x = L\) \| Isothermal, ([\d.]+) \+/- ([\d.]+) C", txt)
    if not m:
        die("REFUSE: the Section 1 cold wall row could not be read.")
    Tc_C = float(m.group(1))

    m = re.search(r"Rayleigh number \| Ra = ([\d.eE+-]+), based on cavity side", txt)
    if not m:
        die("REFUSE: the Section 1 Rayleigh number row could not be read.")
    Ra = float(m.group(1))

    # Ampofo Table 4, reproduced in specification Section 2.3 as a two-column
    # markdown table split across the page.  Parsed rather than retyped.
    #
    # SCOPED TO SECTION 2.3, AND THE SCOPE IS NOT COSMETIC.  A first version of
    # this parser swept every "| a | b | c |" line in the file and silently
    # swallowed two rows out of the Section 2.5 stratification table, which
    # happen to be three floats in [0, 1] side by side.  It reported 23
    # stations where the table has 21 and would have imposed a corrupted wall
    # temperature on every case.  It was caught by the station count below,
    # which is why the count is an exact equality and not a lower bound.
    m = re.search(r"### 2\.3 .*?\n(.*?)\n### ", txt, re.S)
    if not m:
        die("REFUSE: Section 2.3 could not be isolated in the specification.")
    prof = {}
    for line in m.group(1).splitlines():
        if not line.startswith("| "):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        for k in (0, 4):
            if len(cells) < k + 3:
                continue
            try:
                X = float(cells[k]); top = float(cells[k + 1]); bot = float(cells[k + 2])
            except ValueError:
                continue
            if 0.0 <= X <= 1.0 and 0.0 <= top <= 1.0 and 0.0 <= bot <= 1.0:
                if X in prof:
                    die(f"REFUSE: station X = {X} appeared twice in Section 2.3.")
                prof[X] = (top, bot)
    if len(prof) != 21:
        die(f"REFUSE: the Section 2.3 horizontal-wall profile parsed to "
            f"{len(prof)} stations; Ampofo Table 4 has exactly 21.")
    if abs(prof[0.0][0] - 1.0) > 1e-9 or abs(prof[1.0][0]) > 1e-9:
        die("REFUSE: the parsed horizontal-wall profile does not run from "
            "theta = 1 at X = 0 to theta = 0 at X = 1.")
    # Both measured profiles fall from the hot end to the cold end.  A parse
    # that scrambled the station order would break that and nothing else
    # downstream would notice.
    #
    # THE TOLERANCE IS THE INSTRUMENT'S, AND IT IS NOT SLACK.  A strict
    # monotonicity check REFUSED this table on its first run, at the top wall
    # between X = 0.00667 (theta 0.9333) and X = 0.0133 (theta 0.9342).  That
    # rise is 0.0009 in theta, which is 0.036 K, and Ampofo Table 1 (p. 3555)
    # states an air-temperature uncertainty of 0.10 K.  The non-monotonicity is
    # therefore IN THE MEASUREMENT and is smaller than the measurement can
    # resolve; it is not a parse error.  The tolerance below is exactly
    # 0.10 K / dT and no wider, so a genuinely scrambled parse still refuses.
    tol = 0.10 / (Th_C - Tc_C)
    for j, which in ((0, "top"), (1, "bottom")):
        vals = [v[j] for _, v in sorted(prof.items())]
        worst = max((b - a for a, b in zip(vals, vals[1:])), default=0.0)
        if worst > tol:
            die(f"REFUSE: the parsed {which}-wall profile rises by {worst:.4f} "
                f"in theta ({worst*(Th_C-Tc_C):.3f} K) against a tolerance of "
                f"{tol:.4f} ({0.10:.2f} K); the parse is scrambled.")
    return dict(H=H, L=L, Th_C=Th_C, Tc_C=Tc_C, Ra=Ra,
                prof=sorted(prof.items()))


# ---------------------------------------------------------------------------
# mesh grading
# ---------------------------------------------------------------------------

def expansion(n_half, half_len, d1):
    """Cell-to-cell ratio r and blockMesh total expansion for a half-block of
    n_half cells spanning half_len with first cell d1."""
    target = half_len / d1
    lo, hi = 1.0 + 1e-9, 2.0
    for _ in range(200):
        r = 0.5 * (lo + hi)
        s = n_half if abs(r - 1.0) < 1e-12 else (r ** n_half - 1.0) / (r - 1.0)
        if s < target:
            lo = r
        else:
            hi = r
    r = 0.5 * (lo + hi)
    return r ** (n_half - 1), r


# ---------------------------------------------------------------------------
# the measured horizontal-wall temperature, as an OpenFOAM expression
# ---------------------------------------------------------------------------

def wall_profile_expr(prof, which, L, Tc_K, dT):
    """Piecewise-linear interpolation of Ampofo Table 4 in absolute kelvin.

    Built as a nested ternary on pos().x().  Segment endpoints are the
    tabulated stations; nothing is smoothed and nothing is extrapolated."""
    j = 0 if which == "top" else 1
    pts = [(X * L, Tc_K + prof_v[j] * dT) for X, prof_v in prof]

    # FLAT SUM OF RAMPS, NOT NESTED TERNARIES, AND THE REASON IS MEASURED.
    # The obvious encoding of a 21-station piecewise-linear profile is 20
    # nested "? :" operators.  That was built first and OpenFOAM v2606's
    # expression parser REFUSED it with "Syntax error in expression at
    # position 1523", which lands on the eighteenth ternary: the parser has a
    # nesting limit and 20 exceeds it.  The K0cT rung never met this because
    # its profile had five segments.
    #
    # A piecewise-linear function is identically a flat sum of clamped ramps,
    #
    #     T(x) = T_0 + m_0.(x - x_0) + SUM_i (m_i - m_{i-1}).max(0, x - x_i)
    #
    # which has depth one at every station count.  It is the same function,
    # not an approximation of it, and build_cases.py asserts that below by
    # evaluating both forms at every tabulated station.
    slopes = [(pts[i + 1][1] - pts[i][1]) / (pts[i + 1][0] - pts[i][0])
              for i in range(len(pts) - 1)]
    terms = [f"{pts[0][1]:.6f}",
             f"({slopes[0]:.6f})*(pos().x() - {pts[0][0]:.8f})"]
    for i in range(1, len(slopes)):
        dm = slopes[i] - slopes[i - 1]
        terms.append(f"({dm:.6f})*max(0.0, pos().x() - {pts[i][0]:.8f})")
    expr = " + ".join(terms)

    # the assertion: the flat form reproduces every tabulated station exactly
    def flat(x):
        v = pts[0][1] + slopes[0] * (x - pts[0][0])
        for i in range(1, len(slopes)):
            v += (slopes[i] - slopes[i - 1]) * max(0.0, x - pts[i][0])
        return v
    for x, T in pts:
        if abs(flat(x) - T) > 1e-6:
            die(f"REFUSE: the flat ramp form of the {which} wall profile "
                f"disagrees with station x = {x} by {flat(x) - T:.3e} K.")
    return expr


# ---------------------------------------------------------------------------
# dictionary writers
# ---------------------------------------------------------------------------

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


def w(case, loc, obj, cls, body):
    d = os.path.join(case, loc)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, obj), "w") as fh:
        fh.write(HDR.format(cls=cls, loc=loc, obj=obj))
        fh.write(body)
        fh.write("\n\n// ******************************************************** //\n")


def blockmesh(L, nx, ny, ex_x, ex_y):
    z = 0.01
    return f"""scale   1;

vertices
(
    (0 0 0)
    ({L:.8f} 0 0)
    (0 {L:.8f} 0)
    ({L:.8f} {L:.8f} 0)
    (0 0 {z})
    ({L:.8f} 0 {z})
    (0 {L:.8f} {z})
    ({L:.8f} {L:.8f} {z})
);

blocks
(
    hex (0 1 3 2 4 5 7 6) ({nx} {ny} 1)
    simpleGrading
    (
        ( (0.5 0.5 {ex_x:.6f}) (0.5 0.5 {1.0/ex_x:.9f}) )
        ( (0.5 0.5 {ex_y:.6f}) (0.5 0.5 {1.0/ex_y:.9f}) )
        1
    )
);

edges();

boundary
(
    hotWall    {{ type wall;  faces ( (0 4 6 2) ); }}
    coldWall   {{ type wall;  faces ( (1 3 7 5) ); }}
    bottomWall {{ type wall;  faces ( (0 1 5 4) ); }}
    topWall    {{ type wall;  faces ( (2 6 7 3) ); }}
    frontAndBack {{ type empty; faces ( (0 2 3 1) (4 5 7 6) ); }}
);"""


def controldict(end, L, probe_y):
    probes = "\n".join(f"            ({0.5*L:.8f} {y*L:.8f} 0.005)" for y in probe_y)
    walls = ""
    for nm, patch in (("hotFlux", "hotWall"), ("coldFlux", "coldWall"),
                      ("botFlux", "bottomWall"), ("topFlux", "topWall")):
        walls += f"""
    {nm}
    {{
        type            surfaceFieldValue;
        libs            (fieldFunctionObjects);
        regionType      patch;
        name            {patch};
        operation       areaNormalIntegrate;
        fields          (k0csGradT);
        writeFields     false;
        writeToFile     true;
        log             true;
        executeControl  timeStep;
        executeInterval 50;
        writeControl    timeStep;
        writeInterval   50;
    }}"""
    return f"""application     buoyantBoussinesqSimpleFoam;
startFrom       latestTime;
startTime       0;
stopAt          endTime;
endTime         {end};
deltaT          1;
writeControl    timeStep;
writeInterval   {end};
purgeWrite      0;
writeFormat     ascii;
writePrecision  16;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;

functions
{{
    gradT
    {{
        type            grad;
        libs            (fieldFunctionObjects);
        field           T;
        result          k0csGradT;
        executeControl  timeStep;
        executeInterval 50;
        writeControl    none;
        log             false;
    }}{walls}
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
}}"""


FVSCHEMES = """ddtSchemes      { default steadyState; }
gradSchemes     { default Gauss linear; }

// Specification Section 2.7: the conductive layer is 2 mm and the vertical
// cell Peclet number in the core is far above 2, so the laminar rung's pure
// central scheme is inadmissible here.  Same choice, same reason, as K0cT.
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

laplacianSchemes     { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes        { default corrected; }

// Orthogonal structured block, so meshWave reproduces the analytic wall
// distance that kOmegaSST and LaunderSharmaKE both need.
wallDist { method meshWave; }"""


FVSOLUTION = """solvers
{
    p_rgh
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-10;
        relTol          0.01;
    }

    "(U|T|k|omega|epsilon)"
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

    // Convergence is judged by the peak-to-peak criterion registered in
    // K0cS_PREREGISTRATION.md, never by these.  They are set unreachable so a
    // residual dip cannot end a run early and be mistaken for convergence.
    residualControl
    {
        p_rgh           1e-30;
        U               1e-30;
        T               1e-30;
        "(k|omega|epsilon)" 1e-30;
    }
}

relaxationFactors
{
    fields    { p_rgh 0.7; }
    equations
    {
        U               0.4;
        T               0.6;
        "(k|omega|epsilon)" 0.4;
    }
}"""


def field_T(Th, Tc, top_expr, bot_expr, adiabatic, Tinit):
    if adiabatic:
        top = "    topWall    { type zeroGradient; }\n"
        bot = "    bottomWall { type zeroGradient; }\n"
    else:
        top = ("    topWall\n    {\n        type            uniformFixedValue;\n"
               "        uniformValue\n        {\n            type        expression;\n"
               f"            expression  #{{ {top_expr} #}};\n        }}\n"
               f"        value           uniform {Tinit:.9f};\n    }}\n")
        bot = ("    bottomWall\n    {\n        type            uniformFixedValue;\n"
               "        uniformValue\n        {\n            type        expression;\n"
               f"            expression  #{{ {bot_expr} #}};\n        }}\n"
               f"        value           uniform {Tinit:.9f};\n    }}\n")
    return (f"""dimensions      [0 0 0 1 0 0 0];

internalField   uniform {Tinit:.9f};

boundaryField
{{
    hotWall    {{ type fixedValue; value uniform {Th:.9f}; }}
    coldWall   {{ type fixedValue; value uniform {Tc:.9f}; }}
""" + top + bot + "    frontAndBack { type empty; }\n}")


def field_scalar(dim, val, wall_bc):
    walls = "".join(
        f"    {p}\n    {{\n        type            {wall_bc};\n"
        f"        value           $internalField;\n    }}\n"
        for p in ("hotWall", "coldWall", "topWall", "bottomWall"))
    return (f"dimensions      {dim};\n\ninternalField   uniform {val:.9e};\n\n"
            "boundaryField\n{\n" + walls + "    frontAndBack { type empty; }\n}")


def build():
    r = read_spec()
    L, Th_C, Tc_C, Ra = r["L"], r["Th_C"], r["Tc_C"], r["Ra"]
    dT = Th_C - Tc_C
    Tm_C = 0.5 * (Th_C + Tc_C)
    Tm = Tm_C + 273.15
    beta = 1.0 / Tm
    # nu chosen so Ra is EXACT.  Ra = g.beta.dT.L^3.Pr / nu^2
    nu = math.sqrt(GMAG * beta * dT * L ** 3 * PR / Ra)
    alpha = nu / PR
    # Sutherland at T_mean, for the honesty line in the log
    mu = 1.458e-6 * Tm ** 1.5 / (Tm + 110.4)
    rho = 101325.0 / (287.058 * Tm)
    nu_suth = mu / rho

    Vc = math.sqrt(GMAG * beta * dT * L)
    k0_base = 1.5 * (0.05 * Vc) ** 2
    lturb = 0.07 * L

    Th, Tc = Th_C + 273.15, Tc_C + 273.15
    top_expr = wall_profile_expr(r["prof"], "top", L, Tc, dT)
    bot_expr = wall_profile_expr(r["prof"], "bot", L, Tc, dT)

    print("=" * 78)
    print("K0cS SQUARE-CAVITY case build -- F14 cooling ladder")
    print("  Ampofo and Karayiannis 2003; Tian and Karayiannis 2000 Part I")
    print("=" * 78)
    print(f"  parsed from the specification: L = {L} m, Th = {Th_C} C, "
          f"Tc = {Tc_C} C, Ra = {Ra:.3e}")
    print(f"  parsed from the specification: {len(r['prof'])} horizontal-wall "
          f"profile stations (Ampofo Table 4, p. 3558)")
    print("-" * 78)
    print(f"  T_mean = {Tm_C:.3f} C = {Tm:.3f} K,  beta = {beta:.6e} 1/K")
    print(f"  beta.dT = {beta*dT:.5f}", end="")
    print("   *** ABOVE the 0.1 Boussinesq line of docs/physics_rules.yaml"
          if beta * dT > 0.1 else "   (below the 0.1 Boussinesq line)")
    print(f"  nu chosen so Ra is exact: {nu:.6e} m2/s; Sutherland at T_mean "
          f"{nu_suth:.6e} m2/s; difference {100*(nu-nu_suth)/nu_suth:+.2f} %")
    print(f"  Vc = sqrt(g.beta.dT.L) = {Vc:.4f} m/s   "
          f"(Ampofo p. 3557 states V0 = 1 m/s for the same definition)")
    print("-" * 78)
    print(f"{'case':<18}{'model':>17}{'nx':>5}{'ny':>5}{'cells':>8}"
          f"{'d1 mm':>8}{'exp':>9}{'Prt':>6}{'kmult':>8}{'iters':>8}")

    cases = {
        # graded two-mesh pairs, one per turbulence model
        "S_SST_c": dict(model="kOmegaSST",       fine=False, end=30000),
        "S_SST_f": dict(model="kOmegaSST",       fine=True,  end=40000),
        "S_KE_c":  dict(model="kEpsilon",        fine=False, end=30000),
        "S_KE_f":  dict(model="kEpsilon",        fine=True,  end=40000),
        "S_LS_c":  dict(model="LaunderSharmaKE", fine=False, end=30000),
        "S_LS_f":  dict(model="LaunderSharmaKE", fine=True,  end=40000),
        # controls and sensitivities, coarse mesh only and NOT graded
        "C1_laminar":   dict(model="laminar",   fine=False, end=30000),
        "C2_seed_d100": dict(model="kOmegaSST", fine=False, end=30000, kmult=0.01),
        "C3_prt128":    dict(model="kOmegaSST", fine=False, end=30000, prt=1.28),
        "C4_adiabatic": dict(model="kOmegaSST", fine=False, end=30000, adiabatic=True),
    }

    for name, c in sorted(cases.items()):
        nx = NX_FINE if c["fine"] else NX_COARSE
        ny = NY_FINE if c["fine"] else NY_COARSE
        d1 = D1_COARSE / (REFINE if c["fine"] else 1.0)
        ex_x, ratio_x = expansion(nx // 2, 0.5 * L, d1)
        ex_y, ratio_y = expansion(ny // 2, 0.5 * L, d1)
        prt = c.get("prt", PRT)
        kmult = c.get("kmult", 1.0)
        adiabatic = c.get("adiabatic", False)
        model = c["model"]
        k0 = k0_base * kmult
        omega0 = math.sqrt(k0) / (0.09 ** 0.25 * lturb)
        eps0 = 0.09 ** 0.75 * k0 ** 1.5 / lturb

        case = os.path.join(HERE, name)
        os.makedirs(case, exist_ok=True)
        w(case, "system", "blockMeshDict", "dictionary",
          blockmesh(L, nx, ny, ex_x, ex_y))
        w(case, "system", "controlDict", "dictionary",
          controldict(c["end"], L, PROBE_Y))
        w(case, "system", "fvSchemes", "dictionary", FVSCHEMES)
        w(case, "system", "fvSolution", "dictionary", FVSOLUTION)
        w(case, "constant", "g", "uniformDimensionedVectorField",
          "dimensions      [0 1 -2 0 0 0 0];\nvalue           (0 -9.81 0);")
        w(case, "constant", "transportProperties", "dictionary",
          f"transportModel  Newtonian;\n\nnu              {nu:.9e};\n"
          f"beta            {beta:.9e};\nTRef            {Tm:.6f};\n"
          f"Pr              {PR:.6f};\nPrt             {prt:.4f};")
        w(case, "constant", "turbulenceProperties", "dictionary",
          "simulationType  laminar;" if model == "laminar" else
          f"simulationType  RAS;\n\nRAS\n{{\n    RASModel        {model};\n"
          "    turbulence      on;\n    printCoeffs     on;\n}")

        w(case, "0.orig", "T", "volScalarField",
          field_T(Th, Tc, top_expr, bot_expr, adiabatic, Tm))
        w(case, "0.orig", "U", "volVectorField",
          "dimensions      [0 1 -1 0 0 0 0];\n\ninternalField   uniform (0 0 0);\n\n"
          "boundaryField\n{\n    hotWall { type noSlip; }\n"
          "    coldWall { type noSlip; }\n    topWall { type noSlip; }\n"
          "    bottomWall { type noSlip; }\n    frontAndBack { type empty; }\n}")
        w(case, "0.orig", "p_rgh", "volScalarField",
          "dimensions      [0 2 -2 0 0 0 0];\n\ninternalField   uniform 0;\n\n"
          "boundaryField\n{\n" + "".join(
              f"    {p} {{ type fixedFluxPressure; value uniform 0; }}\n"
              for p in ("hotWall", "coldWall", "topWall", "bottomWall")) +
          "    frontAndBack { type empty; }\n}")
        w(case, "0.orig", "alphat", "volScalarField",
          "dimensions      [0 2 -1 0 0 0 0];\n\ninternalField   uniform 0;\n\n"
          "boundaryField\n{\n" + "".join(
              f"    {p} {{ type calculated; value uniform 0; }}\n"
              for p in ("hotWall", "coldWall", "topWall", "bottomWall")) +
          "    frontAndBack { type empty; }\n}")

        if model != "laminar":
            # kEpsilon is the HIGH-Reynolds-number model and takes the
            # high-Re wall treatment; the other two are low-Re and take the
            # low-Re treatment.  Giving kEpsilon a low-Re treatment it does
            # not have damping functions for would be building a straw man.
            highRe = (model == "kEpsilon")
            w(case, "0.orig", "nut", "volScalarField",
              field_scalar("[0 2 -1 0 0 0 0]", 0.0,
                           "nutkWallFunction" if highRe else "nutLowReWallFunction"))
            w(case, "0.orig", "k", "volScalarField",
              field_scalar("[0 2 -2 0 0 0 0]", k0,
                           "kqRWallFunction" if highRe else "kLowReWallFunction"))
            if model == "kOmegaSST":
                w(case, "0.orig", "omega", "volScalarField",
                  field_scalar("[0 0 -1 0 0 0 0]", omega0, "omegaWallFunction"))
            else:
                w(case, "0.orig", "epsilon", "volScalarField",
                  field_scalar("[0 2 -3 0 0 0 0]", eps0, "epsilonWallFunction"))

        with open(os.path.join(case, "CASE.txt"), "w") as fh:
            fh.write(
                f"case              {name}\n"
                f"model             {model}\n"
                f"graded            {'yes' if name.startswith('S_') else 'no'}\n"
                f"mesh              {'fine' if c['fine'] else 'coarse'}\n"
                f"L                 {L:.9f} m\n"
                f"H                 {L:.9f} m\n"
                f"nx                {nx}\nny                {ny}\n"
                f"d1                {d1:.9e} m\n"
                f"cell_ratio_x      {ratio_x:.6f}\n"
                f"cell_ratio_y      {ratio_y:.6f}\n"
                f"T_hot             {Th:.9f} K\n"
                f"T_cold            {Tc:.9f} K\n"
                f"dT                {dT:.9f} K\n"
                f"Ra                {Ra:.9e}\n"
                f"nu                {nu:.9e} m2/s\n"
                f"alpha             {alpha:.9e} m2/s\n"
                f"beta              {beta:.9e} 1/K\n"
                f"Pr                {PR:.6f}\n"
                f"Prt               {prt:.6f}\n"
                f"Vc                {Vc:.9f} m/s\n"
                f"k_seed            {k0:.9e} m2/s2 (multiplier {kmult})\n"
                f"horizontal_walls  {'zeroGradient (CONTROL)' if adiabatic else 'Ampofo Table 4 measured profile'}\n"
                f"endTime           {c['end']}\n")

        print(f"{name:<18}{model:>17}{nx:>5}{ny:>5}{nx*ny:>8}"
              f"{d1*1000:>8.4f}{ex_x:>9.2f}{prt:>6.2f}{kmult:>8.2f}{c['end']:>8}")

    print("-" * 78)
    print("  graded pairs (coarse, fine): S_SST_c/S_SST_f, S_KE_c/S_KE_f, "
          "S_LS_c/S_LS_f")
    print("  grading on the FINE mesh of each pair, per K0c specification "
          "Section 2.5.")
    print("  C1-C4 are controls and sensitivities on the coarse mesh; they "
          "have no fine twin")
    print("  and are therefore NOT GRADED, by the same rule.")
    print("=" * 78)


if __name__ == "__main__":
    build()
