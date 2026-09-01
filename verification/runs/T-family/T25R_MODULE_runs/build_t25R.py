#!/usr/bin/env python3
"""BUILDER for the T25R resolved-channel battery-module cases.

Registered at `docs/campaigns/T-family/T25R_PREREGISTRATION.md` sections 2, 3
and 4.  Written and committed BEFORE ANY COMPUTE.

*** THIS FILE HAS NEVER BEEN EXECUTED. ***  Section 10 of the frozen document
registers the order commit -> the supervisor's personal diff read -> mesh ->
launch, because VERIFICATION_CHARTER.md section 2d.2 closes gates at FIRST
COMPUTE, FEASIBILITY AND BUILD COMPUTE INCLUDED.  Meshing before that read would
close the gates of a comparator the supervisor has not accepted.

`foam()` REFUSES BY NAME to launch any solver.  This script drives blockMesh,
splitMeshRegions and checkMesh and nothing else.

Usage:
    T25R_LEVEL=L1 T25R_CASE=T25R_L1       python3 build_t25R.py A   # dicts
    T25R_LEVEL=L1 T25R_CASE=T25R_L1       python3 build_t25R.py B   # mesh
    T25R_LEVEL=L1 T25R_CASE=T25R_L1       python3 build_t25R.py C   # fields
    python3 build_t25R.py --selftest        # geometry arithmetic only, no I/O

THE LEVEL AND THE STEP ARE READ FROM THE ENVIRONMENT AND NEVER DEFAULTED.  Three
cases are built from one set of bytes and a default here would let a mistyped
launch silently build the wrong level under the right case name (the T24
lesson).
"""
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"

# ---------------------------------------------------------------- geometry
# Section 2.1.  Every number is the frozen document's.
N_CELLS = 8
LX, LY, GAP, DEPTH = 0.100, 0.030, 0.003, 1.000
PITCH = LY + GAP                       # 0.033 m
PLEN_UP, PLEN_DN = 0.050, 0.100        # directive 4.2:401, BUILT here
X0, X1, X2, X3 = -PLEN_UP, 0.0, LX, LX + PLEN_DN
V_CELL = LX * LY * DEPTH               # 3.000e-03 m3

# ------------------------------------------------------------------- mesh
# Section 2.2.  Every N is an EXACT 1.5x of the level below -- no rounding.
LEVELS = {
    "L1": dict(nx_up=16, nx_mid=40, nx_dn=20, ny_ch=24, ny_cell=12, r=1.0),
    "L2": dict(nx_up=24, nx_mid=60, nx_dn=30, ny_ch=36, ny_cell=18, r=1.5),
    "L3": dict(nx_up=36, nx_mid=90, nx_dn=45, ny_ch=54, ny_cell=27, r=2.25),
}
Y1_L1 = 5.175e-05                      # section 2.3, first cell height at L1

# ------------------------------------------------------------- operating point
T_INIT = 293.0                         # K, directive 4.3
U_IN = 8.0                             # m/s, directive 4.4
P_ABS = 1.0e5                          # Pa
Q_TAKEOFF, Q_CRUISE = 70000.0, 2800.0  # W/m3, section 4.2
RAMP_LO, RAMP_HI = 59.999, 60.000      # section 4.5
T_END = 900.0
WRITE_INTERVAL = 5.0
N_OUTER = 5                            # section 3.4; the COST MODEL assumes 5

RHO_AIR, CP_AIR, K_AIR, MU_AIR = 1.2, 1005.0, 0.026, 1.8e-5
PR_AIR = MU_AIR * CP_AIR / K_AIR       # DERIVED so k is EXACTLY 0.026
MW_AIR = 28.9
RHO_S, CP_S, K_S = 2500.0, 1000.0, 3.0  # directive 4.2, ISOTROPIC FALLBACK
MW_S = 30.0

TI = 0.05                              # inlet turbulence intensity
K_IN = 1.5 * (U_IN * TI) ** 2
DH = 2.0 * GAP                         # 0.006 m, a plane slot
L_TURB = 0.07 * DH
OMEGA_IN = math.sqrt(K_IN) / (0.09 ** 0.25 * L_TURB)

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


def env(name):
    v = os.environ.get(name)
    if v is None:
        raise SystemExit("REFUSE: %s is not set; build_t25R.py never defaults "
                         "a registered scalar" % name)
    return v


def case_dir():
    return os.path.join(HERE, env("T25R_CASE"))


def w(relpath, cls, obj, body, location=None):
    p = os.path.join(case_dir(), relpath)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    loc = '    location    "%s";\n' % location if location else ""
    with open(p, "w") as f:
        f.write(HDR % dict(cls=cls, obj=obj, loc=loc))
        f.write("\n" + body.rstrip() + "\n\n")
        f.write("// " + "*" * 73 + " //\n")
    return p


# ==========================================================================
# THE CHANNEL GRADING.  Section 2.3.  Solved from the physics, not typed.
# ==========================================================================

def channel_grading(level):
    """(cells per half, per-cell ratio, blockMesh expansion = last/first).

    The first cell height is the level's y+ ~ 1 target, refined with the level.
    The per-half sum d1*(r^N - 1)/(r - 1) must equal the half gap, and r is
    solved for by bisection -- never guessed and never hand-tuned."""
    L = LEVELS[level]
    n = L["ny_ch"] // 2
    if L["ny_ch"] % 2:
        raise SystemExit("REFUSE: ny_ch %d is odd; the channel is graded "
                         "SYMMETRICALLY about its mid-plane and needs an even "
                         "count" % L["ny_ch"])
    d1 = Y1_L1 / L["r"]
    S = (GAP / 2.0) / d1
    lo, hi = 1.0 + 1e-12, 3.0
    for _ in range(300):
        m = 0.5 * (lo + hi)
        if (m ** n - 1.0) / (m - 1.0) < S:
            lo = m
        else:
            hi = m
    r = 0.5 * (lo + hi)
    if not (1.0 < r < 1.35):
        raise SystemExit("REFUSE: per-cell expansion %.5f at %s is outside the "
                         "registered quality window (1, 1.35); section 2.3 "
                         "registers <= 1.15 on all three levels and a value "
                         "outside it means the sizing arithmetic changed"
                         % (r, level))
    return n, r, r ** (n - 1)


def cell_counts(level):
    L = LEVELS[level]
    nx = L["nx_up"] + L["nx_mid"] + L["nx_dn"]
    fluid = nx * L["ny_ch"] * (N_CELLS - 1)
    solid = L["nx_mid"] * L["ny_cell"] * N_CELLS
    return fluid, solid, fluid + solid


# ==========================================================================
# blockMeshDict.  29 blocks: 8 module + 7 channels x 3 streamwise bands.
# ==========================================================================

def build_block_mesh_dict(level):
    L = LEVELS[level]
    n_half, r_cell, expan = channel_grading(level)
    verts, vindex = [], {}

    def V(x, y, z):
        k = (round(x, 12), round(y, 12), round(z, 12))
        if k not in vindex:
            vindex[k] = len(verts)
            verts.append(k)
        return vindex[k]

    blocks, faces = [], {}

    def add(xa, xb, ya, yb, nx, ny, grading, zone):
        v = [V(xa, ya, 0.0), V(xb, ya, 0.0), V(xb, yb, 0.0), V(xa, yb, 0.0),
             V(xa, ya, DEPTH), V(xb, ya, DEPTH), V(xb, yb, DEPTH),
             V(xa, yb, DEPTH)]
        blocks.append((v, nx, ny, grading, zone))
        i = len(blocks) - 1
        faces[(i, "xlo")] = (v[0], v[4], v[7], v[3])
        faces[(i, "xhi")] = (v[1], v[2], v[6], v[5])
        faces[(i, "ylo")] = (v[0], v[1], v[5], v[4])
        faces[(i, "yhi")] = (v[3], v[7], v[6], v[2])
        faces[(i, "zlo")] = (v[0], v[3], v[2], v[1])
        faces[(i, "zhi")] = (v[4], v[5], v[6], v[7])
        return i

    UNI = "simpleGrading (1 1 1)"
    CHG = ("simpleGrading (1 ((0.5 0.5 %.10g) (0.5 0.5 %.10g)) 1)"
           % (expan, 1.0 / expan))

    mod, ch_up, ch_mid, ch_dn = [], [], [], []
    for j in range(N_CELLS):
        y0 = j * PITCH
        mod.append(add(X1, X2, y0, y0 + LY, L["nx_mid"], L["ny_cell"],
                       UNI, "module"))
        if j < N_CELLS - 1:
            c0, c1 = y0 + LY, y0 + LY + GAP
            ch_up.append(add(X0, X1, c0, c1, L["nx_up"], L["ny_ch"],
                             CHG, "coolant"))
            ch_mid.append(add(X1, X2, c0, c1, L["nx_mid"], L["ny_ch"],
                              CHG, "coolant"))
            ch_dn.append(add(X2, X3, c0, c1, L["nx_dn"], L["ny_ch"],
                             CHG, "coolant"))

    patches = [
        ("inlet", "patch", [(b, "xlo") for b in ch_up]),
        ("outlet", "patch", [(b, "xhi") for b in ch_dn]),
        # the plenum channel walls, upstream and downstream of the solid:
        # ADIABATIC, DECLARED (section 2.1).
        ("plenum_wall", "wall",
         [(b, s) for b in ch_up + ch_dn for s in ("ylo", "yhi")]),
        # the module's outer casing: ADIABATIC, directive 4.2:408.
        ("casing", "wall", [(mod[0], "ylo"), (mod[-1], "yhi")]),
        # the cells' streamwise ends: ADIABATIC, DECLARED (section 2.1).
        ("cell_ends", "wall",
         [(b, s) for b in mod for s in ("xlo", "xhi")]),
        ("front", "empty", [(i, "zhi") for i in range(len(blocks))]),
        ("back", "empty", [(i, "zlo") for i in range(len(blocks))]),
    ]

    out = ["scale   1;", "", "vertices", "("]
    out += ["    (%.12g %.12g %.12g)" % v for v in verts]
    out += [");", "", "blocks", "("]
    for v, nx, ny, g, zone in blocks:
        out.append("    hex (%s) %s (%d %d 1) %s"
                   % (" ".join(str(i) for i in v), zone, nx, ny, g))
    out += [");", "", "edges", "(", ");", "", "boundary", "("]
    for name, ptype, fl in patches:
        out += ["    %s" % name, "    {",
                "        type            %s;" % ptype, "        faces", "        ("]
        out += ["            (%s)" % " ".join(str(i) for i in faces[k])
                for k in fl]
        out += ["        );", "    }", ""]
    out += [");", "", "mergePatchPairs", "(", ");"]
    return "\n".join(out)


# ============================================================== constants
def write_g():
    """g = (0 0 0), REGISTERED (section 3.6).  The chtMultiRegion family reads
    constant/g UNCONDITIONALLY, so the file must exist; its VALUE is zero
    because Gr/Re2 = 2.51e-05 and the fluid uses rhoConst, so buoyancy is absent
    from the equations regardless of g.  The Ri criterion that would 'check'
    this is therefore VACUOUS BY CONSTRUCTION and is NOT reported as a passing
    check anywhere in this rung."""
    w("constant/g", "uniformDimensionedVectorField", "g",
      "dimensions      [0 1 -2 0 0 0 0];\n\nvalue           (0 0 0);",
      location="constant")


def write_region_properties():
    w("constant/regionProperties", "dictionary", "regionProperties",
      "regions\n(\n    fluid       (coolant)\n    solid       (module)\n);",
      location="constant")


def write_fluid_thermo():
    w("constant/coolant/thermophysicalProperties", "dictionary",
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

// Air, CONSTANT properties.  Pr is DERIVED as mu*cp/k so that k is EXACTLY
// 0.026 W/mK rather than a rounded 0.7 giving 0.02585.
mixture
{
    specie          { molWeight  %(mw).6g; }
    thermodynamics  { Cp  %(cp).10g;  Hf  0; }
    transport       { mu  %(mu).10g;  Pr  %(pr).12g; }
    equationOfState { rho %(rho).10g; }
}""" % dict(mw=MW_AIR, cp=CP_AIR, mu=MU_AIR, pr=PR_AIR, rho=RHO_AIR),
      location="constant/coolant")


def write_solid_thermo():
    w("constant/module/thermophysicalProperties", "dictionary",
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

// ISOTROPIC kappa = 3.0 W/mK.  This is the directive's OWN stated fallback at
// 4.2:406-407 for the registered anisotropic (25 in-plane / 1 through-plane),
// taken with the DISCLOSE it demands.  Section 3.4 of the frozen document
// states it and section 9 defers the anisotropic rung by name.
mixture
{
    specie          { molWeight  %(mw).6g; }
    transport       { kappa      %(k).10g; }
    thermodynamics  { Hf  0;  Cp  %(cp).10g; }
    equationOfState { rho %(rho).10g; }
}""" % dict(mw=MW_S, k=K_S, cp=CP_S, rho=RHO_S), location="constant/module")


def write_turbulence():
    w("constant/coolant/turbulenceProperties", "dictionary",
      "turbulenceProperties",
      "// Re_Dh = 3200: TRANSITIONAL, and that is DISCLOSED (section 2.3), not\n"
      "// asserted away. kOmegaSST with *LowRe wall treatments and y+ ~ 1.\n"
      "simulationType  RAS;\n\nRAS\n{\n    RASModel        kOmegaSST;\n"
      "    turbulence      on;\n    printCoeffs     on;\n}",
      location="constant/coolant")


def write_radiation(region):
    w("constant/%s/radiationProperties" % region, "dictionary",
      "radiationProperties",
      "// Radiation OFF and DISCLOSED (section 3.4). The directive is silent;\n"
      "// this is a DECLARED OMISSION, not an inherited default.\n"
      "radiation       off;\nradiationModel  none;",
      location="constant/%s" % region)


def write_fv_options():
    """THE TAKEOFF PULSE.  Section 4.5, and every v2606 trap it names.

    1. THE FIELD IS `h`, NOT `T`.  The solid energy equation is in ENTHALPY;
       an fvOptions entry on `T` is NEVER MATCHED and NEVER APPLIED, OpenFOAM
       emits one non-fatal warning and the solid then converges SILENTLY
       UNHEATED.  That is exactly what CLAUDE.md rule 3 exists for.
    2. `injectionRate` DOES NOT EXIST at v2606.  The accepted forms are
       `sources` (2206+) or the legacy `injectionRateSuSp`.
    3. `volumeMode` IS MANDATORY -- a missing key is a FATAL read, and the wrong
       mode is a SILENT scale error by exactly the zone volume.  `specific` is
       registered, so the values below are in W/m3.
    4. THE BREAKPOINTS ARE THE ENDS OF A RAMP, NOT A STEP.  Function1 `table`
       defaults interpolationScheme to `linear`.  The ramp ENDS at 60.000 so
       t = 60 samples the CRUISE endpoint exactly, which is where the directive
       pins it (60 <= t <= 900).  A 1 ms ramp in (59.999, 60.000) remains; no
       step time at deltaT 0.5 or 0.25 falls inside it, and the comparator
       CHECKS that rather than asserting it."""
    w("constant/module/fvOptions", "dictionary", "fvOptions", """// THE TAKEOFF PULSE -- section 4.2 (C-RATE FIRST) and section 4.5.
//   basis: 350 Wh/L high-power aviation pouch; V = 3.000e-03 m3/m;
//          E = 1050.0 Wh; takeoff 5C at a 4.0 %% heat fraction;
//          cruise 1C at a 0.8 %% heat fraction (the fraction scales as I,
//          because I2R heat scales as I2 while power scales as I).
//   0 <= t < 60 s   : 210.00 W/cell / 3.000e-03 m3 = %(qt).6f W/m3
//   60 <= t <= 900 s:   8.400 W/cell / 3.000e-03 m3 = %(qc).6f W/m3
//
// REGISTERED PREDICTION, BEFORE THE RUN: the adiabatic bound on the pulse rise
// is q*t/(rho*cp) = %(ad).4f K.  The rise will be of order 1.4-1.7 K, NOT tens
// of kelvin.  Whatever is measured is the deliverable; the basis was chosen
// first and the rise was not tuned to it.

volumetricHeatSource
{
    type            scalarSemiImplicitSource;
    active          yes;
    selectionMode   all;
    volumeMode      specific;
    sources
    {
        h
        {
            explicit    table
            (
                (  0.000  %(qt).6f)
                ( %(lo).3f  %(qt).6f)
                ( %(hi).3f  %(qc).6f)
                (%(te).3f  %(qc).6f)
            );
            implicit    none;
        }
    }
}""" % dict(qt=Q_TAKEOFF, qc=Q_CRUISE, lo=RAMP_LO, hi=RAMP_HI, te=T_END,
            ad=Q_TAKEOFF * 60.0 / (RHO_S * CP_S)),
      location="constant/module")


# ================================================================== system
def write_control_dict(dt):
    steps = int(round(T_END / dt))
    w("system/controlDict", "dictionary", "controlDict", """application     chtMultiRegionFoam;

startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         %(te)g;
deltaT          %(dt)g;

// NO ADAPTIVE STEPPING ON GATED RUNS (directive 4.5, reproducibility).  With
// adjustTimeStep no, maxCo and maxDi are INERT and are therefore NOT WRITTEN
// AT ALL -- an inert control in a frozen dictionary is a future reader's trap.
// The step is derived from the 60 s pulse edge and the ~696 s lumped tau
// (section 3.3), NOT from a Courant number.  Co ~ 1600 is REPORTED, never
// controlled; chtMultiRegionFoam is implicit and max Co 1 is a CHOICE.
adjustTimeStep  no;

// %(steps)d registered steps.  CLAUDE.md rule 4's ExecutionTime clause is a
// STEP-COUNT identity, not a time-value identity (section 6.4 conjunct 5).

writeControl    runTime;
writeInterval   %(wi)g;
purgeWrite      0;

// writePrecision 12, NOT the default 6.  At T ~ 293 K six significant figures
// leave a ~1 mK write quantum, LARGER than the within-cell streamwise signal
// D3 gates on (10 x PLANT = 1.234e-02 K).  T21 section 2.4.
writeFormat     ascii;
writePrecision  12;
writeCompression off;
timeFormat      general;
timePrecision   12;
runTimeModifiable false;

// INSTRUMENTS.  Every `operation` name below was read out of
// surfaceFieldValue.C:74-95 at v2606 BEFORE this file was written, because a
// function object with an unknown operation aborts AT CONSTRUCTION and would
// throw away the whole solve.  `sum`, `areaAverage` and `weightedSum` are all
// present there.
//
// Heat balance, exact for constant c_p:
//     H_out - H_in = c_p * ( sum_outlet(phi_f T_f) + sum_inlet(phi_f T_f) )
// phi is the MASS flux [kg/s] and is NEGATIVE on an inflow face, so the two
// weightedSum rows ADD rather than subtract.  Section 6.2 integrates them over
// 900 s and gates |R|/E_gen <= 2 %%.
functions
{
    outlet_hflux
    {
        type            surfaceFieldValue;
        libs            (fieldFunctionObjects);
        region          coolant;
        regionType      patch;
        name            outlet;
        operation       weightedSum;
        weightField     phi;
        fields          (T);
        writeControl    timeStep;
        writeInterval   1;
        writeFields     false;
        log             false;
    }
    inlet_hflux
    {
        $outlet_hflux;
        name            inlet;
    }
    outlet_mdot
    {
        $outlet_hflux;
        operation       sum;
        fields          (phi);
    }
    inlet_mdot
    {
        $outlet_mdot;
        name            inlet;
    }
    outlet_Tbar
    {
        $outlet_hflux;
        operation       areaAverage;
        writeControl    runTime;
        writeInterval   %(wi)g;
    }
    inlet_Tbar
    {
        $outlet_Tbar;
        name            inlet;
    }
    module_minmax
    {
        type            fieldMinMax;
        libs            (fieldFunctionObjects);
        region          module;
        fields          (T);
        writeControl    runTime;
        writeInterval   %(wi)g;
        log             false;
    }
}""" % dict(te=T_END, dt=dt, wi=WRITE_INTERVAL, steps=steps), location="system")


TOP_SOLUTION = """// The TOP-LEVEL PIMPLE dict is the one chtMultiRegionFoam reads for its outer
// loop: readPIMPLEControls.H builds an fvSolution on the runTime (there is no
// top-level mesh) and takes nOuterCorrectors from it.
//
// *** THERE IS NO residualControl ON THIS SOLVER'S OUTER LOOP. ***
// chtMultiRegionFoam.C:109 is a plain `for (oCorr=0; oCorr<nOuterCorr; ++oCorr)`
// -- NOT pimpleControl -- so the loop runs EXACTLY nOuterCorrectors sweeps every
// step, unconditionally, and emits no "converged in"/"not converged within"
// line, ever.  Section 3.5 of the frozen document gates on the LAST-SWEEP
// initial residuals instead, and says why: a comparator counting zero
// "not converged" lines in a log that can never contain one would report a
// PLANTED ZERO as a clean pass.
//
// nOuterCorrectors 5 IS ALSO THE COST MODEL'S ASSUMPTION (section 8.1): one
// PIMPLE step is priced at 5 SIMPLE-equivalent outer iterations.  Changing it
// changes the registered cost and is not a free edit.
PIMPLE
{
    nOuterCorrectors 5;
    nNonOrthogonalCorrectors 0;
}"""

FLUID_SCHEMES = """ddtSchemes      { default Euler; }

gradSchemes     { default Gauss linear; }

divSchemes
{
    default         none;
    // FIRST ORDER IN SPACE ON THE ADVECTED SCALARS, DECLARED (section 3.4).
    // Upwind is chosen for BOUNDEDNESS at Co ~ 1600 and it is a REGISTERED
    // ACCURACY COST, not a hidden one.
    div(phi,U)      bounded Gauss upwind;
    div(phi,K)      bounded Gauss upwind;
    div(phi,h)      bounded Gauss upwind;
    div(phi,k)      bounded Gauss upwind;
    div(phi,omega)  bounded Gauss upwind;
    div(phi,Ekp)    bounded Gauss upwind;
    div(((rho*nuEff)*dev2(T(grad(U))))) Gauss linear;
}

laplacianSchemes{ default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes   { default corrected; }
wallDist        { method meshWave; nRequired false; }"""

FLUID_SOLUTION = """solvers
{
    rho
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-08;
        relTol          0;
    }
    rhoFinal { $rho; relTol 0; }

    "p_rgh.*"
    {
        solver          GAMG;
        tolerance       1e-09;
        relTol          0.01;
        smoother        GaussSeidel;
    }
    p_rghFinal
    {
        $p_rgh;
        tolerance       1e-09;
        relTol          0;
    }

    "(U|h|k|omega)"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-10;
        relTol          0.01;
    }
    "(U|h|k|omega)Final"
    {
        $U;
        tolerance       1e-10;
        relTol          0;
    }
}

PIMPLE
{
    momentumPredictor true;
    nCorrectors     2;
    nNonOrthogonalCorrectors 0;
    // frozenFlow IS AVAILABLE at v2606 and IS DELIBERATELY NOT USED.  It would
    // stop solving momentum entirely and advance energy alone -- a STRONGER
    // approximation than section 3.3's quasi-steady framing.  Left at its
    // default false: the full momentum and turbulence equations are solved on
    // every outer sweep of every time step.  The flow field is SOLVED here,
    // not imposed.
}

relaxationFactors
{
    fields    { "p_rgh"  0.7; }
    equations { "(U|h|k|omega)"  0.9; }
    // The FINAL outer sweep is unrelaxed by omission, which is what makes the
    // last-sweep initial residual of section 3.5 a meaningful convergence
    // measure rather than a relaxation artefact.
}"""

SOLID_SCHEMES = """ddtSchemes      { default Euler; }
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
    hFinal { $h; tolerance 1e-12; relTol 0; }
}

PIMPLE
{
    nNonOrthogonalCorrectors 0;
}

relaxationFactors { equations { h  1; } }"""


# ================================================================== fields
def field(region, obj, dims, internal, patches):
    body = ["dimensions      %s;" % dims, "",
            "internalField   uniform %s;" % internal, "",
            "boundaryField", "{",
            "    #includeEtc \"caseDicts/setConstraintTypes\""]
    for name, spec in patches:
        body += ["    %s" % name, "    {"]
        body += ["        %s" % s for s in spec]
        body += ["    }"]
    body.append("}")
    cls = "volVectorField" if internal.startswith("(") else "volScalarField"
    w("0.orig/%s/%s" % (region, obj), cls, obj, "\n".join(body),
      location='"0.orig/%s"' % region)


COUPLED = ["type            compressible::turbulentTemperatureRadCoupledMixed;",
           "Tnbr            T;", "qrNbr           none;", "qr              none;",
           "useImplicit     true;"]


def write_fluid_fields(iface):
    walls = ["plenum_wall", iface]

    field("coolant", "U", "[0 1 -1 0 0 0 0]", "(%.10g 0 0)" % U_IN,
          [("inlet", ["type            fixedValue;",
                      "value           uniform (%.10g 0 0);" % U_IN]),
           ("outlet", ["type            inletOutlet;",
                       "inletValue      uniform (0 0 0);",
                       "value           $internalField;"])]
          + [(p, ["type            noSlip;"]) for p in walls])

    field("coolant", "p_rgh", "[1 -1 -2 0 0 0 0]", "%.10g" % P_ABS,
          [("inlet", ["type            zeroGradient;"]),
           ("outlet", ["type            fixedValue;",
                       "value           uniform %.10g;" % P_ABS])]
          + [(p, ["type            fixedFluxPressure;",
                  "value           $internalField;"]) for p in walls])

    field("coolant", "p", "[1 -1 -2 0 0 0 0]", "%.10g" % P_ABS,
          [(p, ["type            calculated;", "value           $internalField;"])
           for p in ["inlet", "outlet"] + walls])

    field("coolant", "T", "[0 0 0 1 0 0 0]", "%.10g" % T_INIT,
          [("inlet", ["type            fixedValue;",
                      "value           uniform %.10g;" % T_INIT]),
           ("outlet", ["type            inletOutlet;",
                       "inletValue      uniform %.10g;" % T_INIT,
                       "value           $internalField;"]),
           ("plenum_wall", ["type            zeroGradient;"]),
           (iface, COUPLED + ["kappaMethod     fluidThermo;",
                              "value           $internalField;"])])

    field("coolant", "k", "[0 2 -2 0 0 0 0]", "%.10g" % K_IN,
          [("inlet", ["type            fixedValue;",
                      "value           uniform %.10g;" % K_IN]),
           ("outlet", ["type            inletOutlet;",
                       "inletValue      uniform %.10g;" % K_IN,
                       "value           $internalField;"])]
          + [(p, ["type            kLowReWallFunction;",
                  "value           $internalField;"]) for p in walls])

    field("coolant", "omega", "[0 0 -1 0 0 0 0]", "%.10g" % OMEGA_IN,
          [("inlet", ["type            fixedValue;",
                      "value           uniform %.10g;" % OMEGA_IN]),
           ("outlet", ["type            inletOutlet;",
                       "inletValue      uniform %.10g;" % OMEGA_IN,
                       "value           $internalField;"])]
          + [(p, ["type            omegaWallFunction;",
                  "value           $internalField;"]) for p in walls])

    field("coolant", "nut", "[0 2 -1 0 0 0 0]", "0",
          [("inlet", ["type            calculated;", "value           uniform 0;"]),
           ("outlet", ["type            calculated;", "value           uniform 0;"])]
          + [(p, ["type            nutLowReWallFunction;",
                  "value           uniform 0;"]) for p in walls])

    field("coolant", "alphat", "[1 -1 -1 0 0 0 0]", "0",
          [("inlet", ["type            calculated;", "value           uniform 0;"]),
           ("outlet", ["type            calculated;", "value           uniform 0;"])]
          + [(p, ["type            compressible::alphatWallFunction;",
                  "Prt             0.85;", "value           uniform 0;"])
             for p in walls])


def write_solid_fields(iface):
    adia = ["casing", "cell_ends"]
    field("module", "T", "[0 0 0 1 0 0 0]", "%.10g" % T_INIT,
          [(p, ["type            zeroGradient;"]) for p in adia]
          + [(iface, COUPLED + ["kappaMethod     solidThermo;",
                                "value           $internalField;"])])
    field("module", "p", "[1 -1 -2 0 0 0 0]", "%.10g" % P_ABS,
          [(p, ["type            zeroGradient;"]) for p in adia + [iface]])


# ============================================================ mesh utilities
def foam(cmd, log):
    """Run one OpenFOAM MESHING or INSPECTION utility.  NEVER a solver."""
    tool = cmd.split()[0]
    banned = ("chtMultiRegionFoam", "chtMultiRegionSimpleFoam", "simpleFoam",
              "pimpleFoam", "solidFoam", "buoyantSimpleFoam",
              "buoyantPimpleFoam", "potentialFoam")
    if tool in banned or tool.endswith("Foam"):
        raise SystemExit("REFUSE: build_t25R.py never launches a solver (%s). "
                         "Section 10 registers commit -> diff read -> mesh -> "
                         "launch, and this script is the MESH step only." % tool)
    full = ("set -o pipefail; . %s >/dev/null 2>&1; cd %s && %s > %s 2>&1"
            % (FOAM_BASHRC, case_dir(), cmd, log))
    return subprocess.run(["bash", "-c", full], capture_output=True,
                          text=True).returncode


def read_patch_names(region):
    import re as _re
    p = os.path.join(case_dir(), "constant", region, "polyMesh", "boundary")
    if not os.path.isfile(p):
        raise SystemExit("REFUSE: no %s -- phase C cannot name the coupled "
                         "patch it must write a BC for" % p)
    txt = open(p).read()
    names, depth, prev = [], 0, None
    for t in _re.findall(r'[A-Za-z_][A-Za-z0-9_.:-]*|[{}();]', txt):
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


def selftest():
    """Geometry and mesh arithmetic ONLY.  Writes nothing and runs nothing."""
    fails = 0

    def chk(name, cond):
        nonlocal fails
        print("  %-4s %s" % ("ok" if cond else "FAIL", name))
        if not cond:
            fails += 1

    chk("module height is 8*0.030 + 7*0.003 = 0.261 m",
        abs((N_CELLS - 1) * PITCH + LY - 0.261) < 1e-12)
    chk("V_cell is 3.000e-03 m3", abs(V_CELL - 3.0e-3) < 1e-15)
    chk("channel length is 0.250 m", abs(X3 - X0 - 0.250) < 1e-12)

    tot = {}
    for lv in ("L1", "L2", "L3"):
        f, s, t = cell_counts(lv)
        n, r, e = channel_grading(lv)
        tot[lv] = t
        print("    %s  fluid %6d  solid %6d  total %6d   half %2d  r %.5f  "
              "expansion %.4f" % (lv, f, s, t, n, r, e))
        chk("%s per-cell channel expansion <= 1.15 (section 2.3)" % lv,
            r <= 1.15)
    chk("cell-count ratio L2/L1 is exactly 2.25 (r=1.5 in 2 directions)",
        abs(tot["L2"] / tot["L1"] - 2.25) < 1e-12)
    chk("cell-count ratio L3/L2 is exactly 2.25",
        abs(tot["L3"] / tot["L2"] - 2.25) < 1e-12)
    chk("L1 total is the registered 16608", tot["L1"] == 16608)
    chk("L2 total is the registered 37368", tot["L2"] == 37368)
    for lv in ("L1", "L2", "L3"):
        L = LEVELS[lv]
        chk("%s ny_ch is even (the channel is graded symmetrically)" % lv,
            L["ny_ch"] % 2 == 0)
    for a, b in (("L1", "L2"), ("L2", "L3")):
        for k in ("nx_up", "nx_mid", "nx_dn", "ny_ch", "ny_cell"):
            chk("%s/%s %s ratio is EXACTLY 1.5 (no rounding)" % (b, a, k),
                LEVELS[b][k] == LEVELS[a][k] * 3 // 2
                and LEVELS[a][k] * 3 % 2 == 0)
    chk("the pulse ramp ENDS at 60.000, so t=60 samples CRUISE exactly",
        RAMP_HI == 60.0 and RAMP_LO < 60.0)
    for dt in (0.5, 0.25):
        k0 = int(math.floor(RAMP_LO / dt)) - 2
        hits = [k * dt for k in range(max(k0, 0), k0 + 8)
                if RAMP_LO < k * dt < RAMP_HI]
        chk("no step time at deltaT %g falls inside the ramp" % dt, not hits)
    chk("the adiabatic pulse bound is 1.680 K",
        abs(Q_TAKEOFF * 60.0 / (RHO_S * CP_S) - 1.68) < 1e-9)
    chk("q_takeoff/q_cruise is 25 (the I2 scaling, not a tuning knob)",
        abs(Q_TAKEOFF / Q_CRUISE - 25.0) < 1e-12)
    chk("Pr is DERIVED so k is exactly 0.026",
        abs(MU_AIR * CP_AIR / PR_AIR - K_AIR) < 1e-15)
    chk("blockMeshDict builds 29 blocks (8 module + 7x3 coolant)",
        build_block_mesh_dict("L1").count("    hex (") == 29)
    for lv in ("L1", "L2"):
        d = build_block_mesh_dict(lv)
        chk("%s blockMeshDict names both zones and both empty patches" % lv,
            " module (" in d and " coolant (" in d
            and "type            empty;" in d)
    chk("foam() REFUSES a solver by name",
        _refuses(lambda: foam("chtMultiRegionFoam", "x")))
    print("SELFTEST %s (%d failed)" % ("PASS" if fails == 0 else "FAIL", fails))
    return 0 if fails == 0 else 1


def _refuses(fn):
    try:
        fn()
    except SystemExit as e:
        return isinstance(e.code, str) and e.code.startswith("REFUSE")
    return False


def main():
    if "--selftest" in sys.argv:
        return selftest()
    phase = sys.argv[1] if len(sys.argv) > 1 else "all"
    level = env("T25R_LEVEL")
    if level not in LEVELS:
        raise SystemExit("REFUSE: T25R_LEVEL=%r is not a registered level" % level)
    dt = float(env("T25R_DT"))
    if dt not in (0.5, 0.25):
        raise SystemExit("REFUSE: T25R_DT=%g is not a registered step "
                         "(section 1 registers 0.5 and 0.25 only)" % dt)

    if phase in ("all", "A"):
        w("system/blockMeshDict", "dictionary", "blockMeshDict",
          build_block_mesh_dict(level), location="system")
        write_control_dict(dt)
        w("system/fvSchemes", "dictionary", "fvSchemes",
          SOLID_SCHEMES, location="system")
        w("system/fvSolution", "dictionary", "fvSolution",
          TOP_SOLUTION, location="system")
        for reg, sch, sol in (("coolant", FLUID_SCHEMES, FLUID_SOLUTION),
                              ("module", SOLID_SCHEMES, SOLID_SOLUTION)):
            w("system/%s/fvSchemes" % reg, "dictionary", "fvSchemes", sch,
              location="system/%s" % reg)
            w("system/%s/fvSolution" % reg, "dictionary", "fvSolution", sol,
              location="system/%s" % reg)
        write_g()
        write_region_properties()
        write_fluid_thermo()
        write_solid_thermo()
        write_turbulence()
        for reg in ("coolant", "module"):
            write_radiation(reg)
        write_fv_options()
        f, s, t = cell_counts(level)
        n, r, e = channel_grading(level)
        print("phase A: dictionaries written for %s at %s, deltaT %g"
              % (env("T25R_CASE"), level, dt))
        print("  registered cells: fluid %d + solid %d = %d; channel half %d "
              "cells, per-cell r %.5f, blockMesh expansion %.4f"
              % (f, s, t, n, r, e))

    if phase in ("all", "B"):
        for cmd, log in (("blockMesh", "log.blockMesh"),
                         ("splitMeshRegions -cellZones -overwrite",
                          "log.splitMeshRegions")):
            rc = foam(cmd, log)
            print("%s rc=%d" % (cmd.split()[0], rc))
            if rc:
                return rc
        for reg in ("coolant", "module"):
            rc = foam("checkMesh -region %s" % reg, "log.checkMesh.%s" % reg)
            print("checkMesh %s rc=%d" % (reg, rc))
            if rc:
                return rc

    if phase in ("all", "C"):
        pats = {r: read_patch_names(r) for r in ("coolant", "module")}
        for r, nlist in pats.items():
            print("%-8s patches: %s" % (r, nlist))
        # SECTION 2.5's REGISTERED ASSERTION: exactly one interface per region.
        for r, other in (("coolant", "module"), ("module", "coolant")):
            got = [p for p in pats[r] if p.startswith("%s_to_" % r)]
            if len(got) != 1:
                raise SystemExit("REFUSE: region %s carries %d `%s_to_*` "
                                 "patches, expected exactly 1 (section 2.5). "
                                 "The conjugate coupling is not what was "
                                 "registered and NOTHING is launched on it."
                                 % (r, len(got), r))
        write_fluid_fields([p for p in pats["coolant"]
                            if p.startswith("coolant_to_")][0])
        write_solid_fields([p for p in pats["module"]
                            if p.startswith("module_to_")][0])
        print("phase C: 0.orig fields written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
