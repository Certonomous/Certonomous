#!/usr/bin/env python3
"""build_cases.py -- generate every K0cX CROSS-GEOMETRY case from one table.

    python3 build_cases.py [case ...]     # writes case directories next to this file

WHAT THIS BUILDS
----------------
The Betts and Bokhari enclosed tall cavity (ERCOFTAC Classic Collection Case
079) at Ra = 0.86e6 and 1.43e6, specified by

    docs/campaigns/F14-cooling-ladder/K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md

Section 2 and addendum A1, solved with the THREE turbulence models the
square-cavity rung K0cS graded plus a LAMINAR control, each on a mandatory
mesh pair, with a third mesh level at the higher Rayleigh number.

This is the cross-geometry half of a pair.  K0cS took these models to Ampofo
and Karayiannis's square cavity at Ra 1.58e9; this takes the same three to a
28.7 aspect-ratio tall cavity three Rayleigh decades lower.  Predictions are in
`docs/campaigns/F14-cooling-ladder/K0cX_PREREGISTRATION.md`, committed before
any case here was solved.

NOTHING PHYSICAL IS TYPED INTO THIS FILE
----------------------------------------
The geometry, the two temperature differentials and the two Rayleigh numbers
are PARSED OUT OF THE SPECIFICATION at build time.  The top and bottom wall
temperature profiles are READ OUT OF THE PRIMARY DATA FILES.  The two turbulent
Prandtl numbers used by the sensitivity cases are PARSED OUT OF ADDENDUM A1.6b,
which derived them from Betts Table 1.  If any of those cannot be read, this
script exits 2 and builds nothing.

PATHS ARE RESOLVED BY UPWARD SEARCH, AND THAT IS A REPAIR
---------------------------------------------------------
`K0cT_runs/build_cases.py` resolves its specification as `HERE/../<name>`.
That literal was correct when the K0cT run tree lived under
`docs/campaigns/F14-cooling-ladder/` and became false when a repository
reorganisation moved it to `verification/runs/F14-cooling-ladder/`.  Verified
by execution on 2026-08-18, not by reading:

    $ python3 K0cT_runs/build_cases.py
    REFUSE: gate specification not found at
      /home/ubuntu/Certonomous/verification/runs/F14-cooling-ladder/K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md

That is the SAME L-137 instance `K0cT_NUSSELT_REGRADE.md` Section 6.1 found and
fixed in `analyse_k0ct.py`; the build script beside it was never fixed and is
still broken at HEAD.  Recorded rather than silently worked around.

WHAT DIFFERS FROM K0cT's BUILD, AND WHY
---------------------------------------
1.  `kEpsilon` is added.  It is the HIGH-Reynolds-number model and takes the
    high-Re wall treatment (`nutkWallFunction`, `kqRWallFunction`); the two
    low-Re models take `nutLowReWallFunction` / `kLowReWallFunction`.  Giving
    kEpsilon a low-Re treatment it has no damping functions for would be
    building a straw man.  Its y+ is measured and reported per case, because
    the gate spec's own argument (K0cT_RESULTS.md Section 1.2a) is that wall
    functions are inadmissible on this mesh -- that argument is TESTED here
    rather than used to exclude the model without evidence.
2.  `residualControl` is REMOVED.  K0cT Section 4 measured that three of its
    cases stopped on residualControl at 6-10k iterations and had to be
    continued past it by a second script.  Removing it makes every case a
    single stage governed by its endTime, so one completion marker per case is
    the whole contract.
3.  A THIRD mesh level (extra-fine, 1.6x again) at the higher Ra.  Grid
    refinement is the axis on which both low-Re models misbehaved at the square
    cavity, and a two-point difference cannot show a trend.
4.  The laminar control is run on the FULL mesh pair at BOTH Rayleigh numbers,
    not on one coarse mesh.  Docket D411 records that at the square cavity the
    set of rows kOmegaSST passed that the laminar control did not was EMPTY.
    A control that cheap must be graded on every row it can reach.
5.  Per-case `Prt`.  The sensitivity cases use the values addendum A1.6b
    DERIVED from Betts Table 1 (1.071 at lo Ra, 1.283 at hi Ra), parsed here.

TURBULENCE MODEL, SCHEMES, PLATE TEMPERATURES, AND THE Ra-MATCHING VISCOSITY
----------------------------------------------------------------------------
Identical in form and derivation to `K0cT_runs/build_cases.py`, whose module
docstring states each and is not repeated here:
  * plate levels from the four rubber-wall end extrapolations (boundary-
    condition data only; the graded `mt_z0_*` profiles are deliberately unused);
  * nu chosen so Ra is exact, because dT and W are measured;
  * second-order LIMITED convection schemes, because the vertical cell Peclet
    number on this case is of order 100.
Holding those fixed is what makes this rung a model comparison and not a
re-specification of the case.
"""

import math
import os
import re
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _find_up(relpath):
    """Resolve a repository-relative path by walking UP from this file."""
    d = HERE
    while True:
        cand = os.path.join(d, relpath)
        if os.path.exists(cand):
            return os.path.abspath(cand)
        if os.path.isdir(os.path.join(d, ".git")):
            return os.path.abspath(os.path.join(d, relpath))
        parent = os.path.dirname(d)
        if parent == d:
            return os.path.abspath(relpath)
        d = parent


SPEC = _find_up("docs/campaigns/F14-cooling-ladder/"
                "K0c_DIFFERENTIALLY_HEATED_CAVITY_GATE.md")
DATA = _find_up("docs/campaigns/F14-cooling-ladder/reference-data/betts_bokhari")

GMAG = 9.81
PR = 0.71
PRT_DEFAULT = 0.85     # docs/physics_rules.yaml thermal:turbulent_prandtl_default
RHO0 = 1.1614
CP0 = 1007.0
LZ = 0.01


# ---------------------------------------------------------------------------
# the specification, parsed rather than remembered
# ---------------------------------------------------------------------------

def read_spec():
    if not os.path.isfile(SPEC):
        raise SystemExit(f"REFUSE: gate specification not found at {SPEC}")
    txt = open(SPEC).read()
    flat = " ".join(txt.split())

    m = re.search(r"Tall rectangular cavity,\s*([\d.]+)\s*m high x\s*([\d.]+)\s*m wide"
                  r"\s*x\s*([\d.]+)\s*m deep", txt)
    if not m:
        raise SystemExit("REFUSE: cannot read the cavity geometry from the "
                         "specification Section 2.2.")
    H, W, D = (float(m.group(i)) for i in (1, 2, 3))

    m = re.search(r"temperature differentials\s*([\d.]+)\s*C and\s*([\d.]+)\s*C", txt)
    if not m:
        raise SystemExit("REFUSE: cannot read the two temperature differentials.")
    dT_lo, dT_hi = float(m.group(1)), float(m.group(2))

    m = re.search(r"Rayleigh numbers\s*\|\s*([\d.]+)e6 and\s*([\d.]+)e6", txt)
    if not m:
        raise SystemExit("REFUSE: cannot read the two Rayleigh numbers.")
    Ra_lo, Ra_hi = float(m.group(1)) * 1e6, float(m.group(2)) * 1e6

    # --- the MEASURED turbulent Prandtl numbers, addendum A1.6b -------------
    # DERIVED there from Betts Table 1 as Prt = (nu_T/nu)/(alpha_T/alpha).Pr.
    # The sensitivity cases use these and nothing else; a Prt typed into this
    # file would make the sensitivity a comparison against a number this
    # script supplied itself.
    rows = re.findall(
        r"\|\s*(lo|hi) Ra [\d.]+e6\s*\|\s*[\d.]+\s*\|\s*[\d.]+\s*\|\s*[\d.]+\s*\|"
        r"\s*\*\*([\d.]+)\*\*\s*\|\s*([\d.]+)\s*\|", flat)
    prt_meas = {k: float(v) for k, v, _ in rows}
    if set(prt_meas) != {"lo", "hi"}:
        raise SystemExit(
            "REFUSE: addendum A1.6b's measured turbulent Prandtl number rows "
            "could not be read. The Prt sensitivity has no grounded value and "
            "nothing is built.")
    baseline = {float(b) for _, _, b in rows}
    if baseline != {PRT_DEFAULT}:
        raise SystemExit(
            f"REFUSE: A1.6b states the solve used Prt {baseline}, but this "
            f"build's default is {PRT_DEFAULT}. The sensitivity would not be "
            "the one the addendum describes.")

    return dict(H=H, W=W, D=D, prt_meas=prt_meas,
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
    if at_start:
        x0, x1, v0, v1 = xs[0], xs[1], vs[0], vs[1]
    else:
        x0, x1, v0, v1 = xs[-2], xs[-1], vs[-2], vs[-1]
    return v0 + (v1 - v0) * (xt - x0) / (x1 - x0)


def plate_levels(suf, W_mm):
    """T_mean from the two RUBBER WALL profiles only.  K0cT rule, unchanged."""
    ends = []
    for fn in (f"mt_rt_z0_{suf}.dat", f"mt_rb_z0_{suf}.dat"):
        xs, vs = load_dat(fn)
        ends.append(extrap(xs, vs, 0.0, True))
        ends.append(extrap(xs, vs, W_mm, False))
    return sum(ends) / len(ends), ends


def rubber_profile_expr(suf, which, T_shift_K):
    xs_mm, Ts_C = load_dat(f"mt_r{which}_z0_{suf}.dat")
    xs = [x / 1000.0 for x in xs_mm]
    Ts = [T + T_shift_K for T in Ts_C]
    expr = f"{Ts[-1]:.6f}"
    for i in range(len(xs) - 2, -1, -1):
        x0, x1, t0, t1 = xs[i], xs[i + 1], Ts[i], Ts[i + 1]
        slope = (t1 - t0) / (x1 - x0)
        seg = f"({t0:.6f} + {slope:.6f}*(pos().x() - {x0:.8f}))"
        if i == 0:
            seg = f"(pos().x() <= {x0:.8f} ? {t0:.6f} : {seg})"
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


def _sfv(name, patch, op, fields):
    return f"""    {name}
    {{
        type            surfaceFieldValue;
        libs            (fieldFunctionObjects);
        regionType      patch;
        name            {patch};
        operation       {op};
        fields          ({fields});
        writeFields     false;
        writeToFile     true;
        log             true;
        executeControl  timeStep;
        executeInterval 50;
        writeControl    timeStep;
        writeInterval   50;
    }}
"""


def _vfv(name, op, fields):
    return f"""    {name}
    {{
        type            volFieldValue;
        libs            (fieldFunctionObjects);
        regionType      all;
        operation       {op};
        fields          ({fields});
        writeFields     false;
        writeToFile     true;
        log             true;
        executeControl  timeStep;
        executeInterval 50;
        writeControl    timeStep;
        writeInterval   50;
    }}
"""


def functions(H, W, probe_heights, model):
    probes = "\n".join(
        f"            ({0.5*W:.8f} {yh*H:.8f} {0.5*LZ:.8f})" for yh in probe_heights)
    # nut is a per-iteration RELAMINARISATION diagnostic, not an end-state one:
    # at the square cavity LaunderSharma's eddy viscosity collapsed DURING the
    # run, and a field written only at endTime cannot show when.
    turb = "" if model == "laminar" else _vfv("nutMax", "max", "nut")
    return f"""
functions
{{
    gradT
    {{
        type            grad;
        libs            (fieldFunctionObjects);
        field           T;
        result          k0cxGradT;
        executeControl  timeStep;
        executeInterval 50;
        writeControl    none;
        log             false;
    }}
{_sfv("hotFlux", "hotWall", "areaNormalIntegrate", "k0cxGradT")}\
{_sfv("coldFlux", "coldWall", "areaNormalIntegrate", "k0cxGradT")}\
{_sfv("hotT", "hotWall", "areaAverage", "T")}\
{_sfv("coldT", "coldWall", "areaAverage", "T")}\
{_sfv("topT", "topWall", "areaAverage", "T")}\
{_sfv("bottomT", "bottomWall", "areaAverage", "T")}\
{_vfv("Uymax", "max", "U")}\
{_vfv("Uymin", "min", "U")}\
{turb}\
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

// The cell Peclet number on this case is of order 100 in the vertical
// direction, so a pure central scheme is inadmissible and the choice is
// recorded with its measured basis (printed by this build).
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

wallDist
{
    method          meshWave;
}
"""


# residualControl is DELIBERATELY ABSENT.  K0cT Section 4 measured that it
# stopped three cases at 6-10k iterations, well before the graded quantities
# were steady, and each had to be continued by a second script.  Every case
# here runs to its endTime in one stage, so one marker per case is the whole
# completion contract.
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


def transport(nu, beta, TRef, prt):
    return f"""
transportModel  Newtonian;

nu              {nu:.9e};
beta            {beta:.9e};
TRef            {TRef:.6f};
Pr              {PR:.6f};
Prt             {prt:.4f};
"""


def field_T(Th, Tc, top_expr, bot_expr, Tinit):
    def patch(name, expr):
        return (f"    {name}\n    {{\n"
                "        type            uniformFixedValue;\n"
                "        uniformValue\n        {\n"
                "            type        expression;\n"
                f"            expression  #{{ {expr} #}};\n"
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
{patch("topWall", top_expr)}{patch("bottomWall", bot_expr)}\
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


def field_scalar(dim, val, wall_bc):
    walls = "\n".join(
        f"    {p}\n    {{\n        type            {wall_bc};\n"
        f"        value           $internalField;\n    }}"
        for p in ("hotWall", "coldWall", "topWall", "bottomWall"))
    return (f"\ndimensions      {dim};\n\ninternalField   uniform {val:.9e};\n\n"
            f"boundaryField\n{{\n{walls}\n"
            "    frontAndBack    { type empty; }\n}\n")


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
# mesh levels: the coarse/fine pair is IDENTICAL to K0cT's, so this rung's
# kOmegaSST leg is a reproduction check on an independently written build.
MESH = {"c": (40, 120, 60000),      # nx, ny, endTime
        "f": (64, 192, 50000),
        "x": (102, 307, 30000)}     # 1.6x again; hi Ra only
D1_COARSE = 2.0e-04
NX_COARSE = 40

MODELS = {"SST": "kOmegaSST", "KE": "kEpsilon",
          "LS": "LaunderSharmaKE", "LAM": "laminar"}

PROBE_HEIGHTS = (0.30, 0.40, 0.50, 0.60, 0.70)


def case_table(prt_meas):
    cases = {}
    # graded mesh pairs: every model, both Ra, coarse and fine
    for rung in ("lo", "hi"):
        for tag, model in MODELS.items():
            for lvl in ("c", "f"):
                cases[f"X_{rung}_{lvl}_{tag}"] = dict(
                    rung=rung, lvl=lvl, model=model, prt=PRT_DEFAULT)
    # third mesh level, hi Ra, the three turbulence models plus laminar
    for tag in ("SST", "KE", "LS"):
        cases[f"X_hi_x_{tag}"] = dict(rung="hi", lvl="x", model=MODELS[tag],
                                      prt=PRT_DEFAULT)
    # SENSITIVITY: Prt at the value MEASURED in this very cavity (A1.6b)
    cases["P_lo_f_SST"] = dict(rung="lo", lvl="f", model="kOmegaSST",
                               prt=prt_meas["lo"])
    cases["P_hi_f_SST"] = dict(rung="hi", lvl="f", model="kOmegaSST",
                               prt=prt_meas["hi"])
    cases["P_hi_f_KE"] = dict(rung="hi", lvl="f", model="kEpsilon",
                              prt=prt_meas["hi"])
    return cases


def sutherland_nu(T_K):
    mu = 1.716e-05 * (T_K / 273.15) ** 1.5 * (273.15 + 110.4) / (T_K + 110.4)
    rho = 101325.0 / (287.058 * T_K)
    return mu / rho


def build(only=None):
    spec = read_spec()
    H, W = spec["H"], spec["W"]
    CASES = case_table(spec["prt_meas"])
    print("=" * 92)
    print("K0cX CROSS-GEOMETRY case build -- Betts and Bokhari tall cavity")
    print("=" * 92)
    print(f"  parsed from the specification: H = {H} m, W = {W} m, D = {spec['D']} m")
    print(f"  parsed from the specification: dT = {spec['lo']['dT']} / {spec['hi']['dT']} C, "
          f"Ra = {spec['lo']['Ra']:.3e} / {spec['hi']['Ra']:.3e}")
    print(f"  parsed from addendum A1.6b: MEASURED Prt = {spec['prt_meas']['lo']} (lo), "
          f"{spec['prt_meas']['hi']} (hi); build default {PRT_DEFAULT}")
    print("-" * 92)

    rung = {}
    for suf in ("lo", "hi"):
        dT = spec[suf]["dT"]
        Ra = spec[suf]["Ra"]
        T_mean_C, ends = plate_levels(suf, W * 1000.0)
        T_mean = T_mean_C + 273.15
        beta = 1.0 / T_mean
        nu = math.sqrt(GMAG * beta * dT * W ** 3 * PR / Ra)
        rung[suf] = dict(dT=dT, Ra=Ra, T_mean=T_mean, beta=beta, nu=nu,
                         Th=T_mean + 0.5 * dT, Tc=T_mean - 0.5 * dT,
                         nu_hb=sutherland_nu(T_mean))
        print(f"  rung {suf}: rubber-wall end extrapolations "
              f"{['%.2f' % e for e in ends]} C -> T_mean {T_mean_C:.3f} C, "
              f"T_hot {T_mean_C+0.5*dT:.3f} C, T_cold {T_mean_C-0.5*dT:.3f} C")
        print(f"           beta.dT = {beta*dT:.5f}"
              + ("   *** ABOVE the 0.1 Boussinesq line of docs/physics_rules.yaml"
                 if beta * dT > 0.1 else "   (below the 0.1 Boussinesq line)"))
        print(f"           nu (Ra exact) {nu:.6e}; Sutherland {rung[suf]['nu_hb']:.6e}; "
              f"difference {100*(nu-rung[suf]['nu_hb'])/rung[suf]['nu_hb']:+.2f} %")

    print("-" * 92)
    print(f"{'case':<16}{'rung':>5}{'model':>17}{'nx':>5}{'ny':>5}{'cells':>8}"
          f"{'d1 mm':>8}{'exp':>8}{'Prt':>7}{'Pe_y':>8}{'iters':>8}")

    built = 0
    for name in sorted(CASES):
        c = CASES[name]
        if only and name not in only:
            continue
        r = rung[c["rung"]]
        dT, nu = r["dT"], r["nu"]
        alpha = nu / PR
        nx, ny, end = MESH[c["lvl"]]
        d1 = D1_COARSE * (NX_COARSE / nx)
        exp_ratio, ratio = expansion(nx // 2, 0.5 * W, d1)
        dy = H / ny
        Vc = math.sqrt(GMAG * r["beta"] * dT * W)
        Pe_y = 0.6 * Vc * dy / alpha
        k0 = 1.5 * (0.05 * Vc) ** 2
        lturb = 0.07 * W
        omega0 = math.sqrt(k0) / (0.09 ** 0.25 * lturb)
        eps0 = 0.09 ** 0.75 * k0 ** 1.5 / lturb
        Ra_eff = GMAG * r["beta"] * dT * W ** 3 / (nu * alpha)

        print(f"{name:<16}{c['rung']:>5}{c['model']:>17}{nx:>5}{ny:>5}{nx*ny:>8}"
              f"{d1*1000:>8.4f}{exp_ratio:>8.2f}{c['prt']:>7.3f}{Pe_y:>8.1f}{end:>8}")

        case = os.path.join(HERE, name)
        if os.path.isdir(case):
            shutil.rmtree(case)

        top_expr, top_pts = rubber_profile_expr(c["rung"], "t", 273.15)
        bot_expr, bot_pts = rubber_profile_expr(c["rung"], "b", 273.15)

        w(case, "system", "blockMeshDict", "dictionary",
          blockmesh(W, H, nx, ny, exp_ratio))
        w(case, "system", "controlDict", "dictionary",
          controldict(end, functions(H, W, PROBE_HEIGHTS, c["model"])))
        w(case, "system", "fvSchemes", "dictionary", FVSCHEMES)
        w(case, "system", "fvSolution", "dictionary", fvsolution(0.4, 0.7, 0.6, 0.4))
        w(case, "constant", "transportProperties", "dictionary",
          transport(nu, r["beta"], r["T_mean"], c["prt"]))
        w(case, "constant", "g", "uniformDimensionedVectorField",
          f"\ndimensions      [0 1 -2 0 0 0 0];\nvalue           (0 {-GMAG:.6f} 0);\n")
        w(case, "constant", "turbulenceProperties", "dictionary",
          turbulence_properties(c["model"]))
        w(case, "constant", "thermalAuditProperties", "dictionary",
          f"\nrho0            {RHO0};\ncp0             {CP0};\n")
        w(case, "0.orig", "T", "volScalarField",
          field_T(r["Th"], r["Tc"], top_expr, bot_expr, r["T_mean"]))
        w(case, "0.orig", "U", "volVectorField", FIELD_U)
        w(case, "0.orig", "p_rgh", "volScalarField", FIELD_PRGH)
        w(case, "0.orig", "alphat", "volScalarField", FIELD_ALPHAT)

        highRe = (c["model"] == "kEpsilon")
        if c["model"] != "laminar":
            w(case, "0.orig", "nut", "volScalarField",
              field_scalar("[0 2 -1 0 0 0 0]", 0.0,
                           "nutkWallFunction" if highRe else "nutLowReWallFunction"))
            w(case, "0.orig", "k", "volScalarField",
              field_scalar("[0 2 -2 0 0 0 0]", k0,
                           "kqRWallFunction" if highRe else "kLowReWallFunction"))
            if c["model"] == "kOmegaSST":
                w(case, "0.orig", "omega", "volScalarField",
                  field_scalar("[0 0 -1 0 0 0 0]", omega0, "omegaWallFunction"))
            else:
                w(case, "0.orig", "epsilon", "volScalarField",
                  field_scalar("[0 2 -3 0 0 0 0]", eps0, "epsilonWallFunction"))

        graded = name.startswith("X_") and c["lvl"] in ("c", "f")
        with open(os.path.join(case, "CASE.txt"), "w") as fh:
            fh.write(
                f"case              {name}\n"
                f"rung              {c['rung']}\n"
                f"model             {c['model']}\n"
                f"mesh_level        {c['lvl']}\n"
                f"graded            {'yes' if graded else 'no'}\n"
                f"wall_treatment    {'high-Re wall functions' if highRe else ('none (laminar)' if c['model']=='laminar' else 'low-Re, integrate to wall')}\n"
                f"Ra                {r['Ra']:.9e}\n"
                f"Ra_effective      {Ra_eff:.9e}\n"
                f"H                 {H} m\n"
                f"W                 {W} m\n"
                f"nx                {nx}\nny                {ny}\n"
                f"cells             {nx*ny}\n"
                f"d1                {d1:.9e} m\n"
                f"expansion_ratio   {exp_ratio:.6f} (cell-to-cell {ratio:.6f})\n"
                f"dy                {dy:.9e} m\n"
                f"dT                {dT:.9f} K\n"
                f"T_mean            {r['T_mean']:.9f} K\n"
                f"T_hot             {r['Th']:.9f} K\n"
                f"T_cold            {r['Tc']:.9f} K\n"
                f"beta              {r['beta']:.9e} 1/K\n"
                f"beta_dT           {r['beta']*dT:.9f}\n"
                f"nu                {nu:.9e} m2/s\n"
                f"nu_sutherland     {r['nu_hb']:.9e} m2/s\n"
                f"alpha             {alpha:.9e} m2/s\n"
                f"Pr                {PR:.6f}\n"
                f"Prt               {c['prt']:.6f}\n"
                f"Vc                {Vc:.9f} m/s\n"
                f"k_seed            {k0:.9e} m2/s2\n"
                f"Pe_y_at_peak      {Pe_y:.6f}\n"
                f"endTime           {end}\n")
            fh.write("top_wall_profile_points_x_m_T_K\n")
            for x, t in top_pts:
                fh.write(f"  {x:.6f} {t:.4f}\n")
            fh.write("bottom_wall_profile_points_x_m_T_K\n")
            for x, t in bot_pts:
                fh.write(f"  {x:.6f} {t:.4f}\n")
        built += 1

    print("-" * 92)
    print(f"  built {built} cases")
    print("  graded mesh pairs (coarse, fine) per model per Ra; the third level "
          "'x' is a TREND leg,")
    print("  and the P_* cases are the Prt SENSITIVITY, which grades nothing.")
    print("=" * 92)


if __name__ == "__main__":
    build(sys.argv[1:] or None)
