#!/usr/bin/env python3
# =========================================================================
# T25 -- CASE 4 8-CELL BATTERY MODULE, TAKEOFF PULSE: FEASIBILITY BUILDER
#
# *** THIS IS AN UNGATED FEASIBILITY RUNG. ***
# NO frozen pre-registration, NO gate, NO threshold, NO verdict, NO Roache
# triple, NO GCI.  Nothing this builder produces may be graded, cited as a
# result, or shown without the FEASIBILITY caveat on its face.
# Authority: Sanaa's feasibility-first ruling,
#   etc/sessions/2026-08-31T1513Z_sanaa_freeze_clock_and_so3_ruling.md sec 1
#   ("no freeze required for feasibility/physics rungs, never was")
# and the demo order,
#   etc/sessions/2026-08-31T2213Z_sanaa_demo_tonight_priorities.md
#   ("Heat transfer team must laubch the battery case asap").
#
# GEOMETRY AND PULSE ARE THE DIRECTIVE'S, NOT THIS LANE'S:
#   etc/sessions/2026-08-30T2300Z_sanaa_four_new_case_families.md
#   sec 4.2 lines 396-408 (module geometry, cell properties, casing)
#   sec 4.3 lines 411-418 (the takeoff pulse, initial condition)
#   sec 4.4 lines 421-425 (channel air, U_inlet 8 m/s, Re_Dh ~3200)
#   sec 4.5 lines 437-440 (duration 900 s, write every 5 s, probes)
#
# Modelled on build_t20.py / build_t20b.py / run_one_t20.sh in
# verification/runs/T-family/T20_runs/.  The lesson carried over: T20_LC_c's
# first attempt died because constant/g was absent (quarantined at
# T20_LC_c_FAILED_NO_G_20260831T001244Z).  This builder EMITS constant/g and
# ASSERTS it on disk before returning.
#
# TIME STEP IS A BUILD PARAMETER (--delta-t), added 2026-08-31 so that the
# step-size comparison is built by this builder rather than hand-copied.  Two
# cases are emitted from this one file:
#     T25_MOD_L1        --delta-t 0.5    (as built earlier; the default)
#     T25_MOD_L1_DT025  --delta-t 0.25   (half the step, everything else equal)
# The builder now also EVALUATES the pulse-table sampling condition that the
# breakpoint repair below rests on, and REFUSES if any solver step falls
# strictly inside the residual ramp.  The condition was previously asserted in
# a comment only; a condition nothing evaluates is not a guard.
# =========================================================================
import argparse
import os
import re
import shutil
import subprocess
import sys
import textwrap
from fractions import Fraction

# ------------------------------------------------------------------ geometry
N_CELLS   = 8            # directive 4.2:396  "8 prismatic cells in a row"
LX        = 0.100        # m, flow direction   directive 4.2:396
LY        = 0.030        # m, cell thickness   directive 4.2:397
LZ        = 1.000        # m, unit depth (2D)  directive 4.2:397
GAP       = 0.003        # m, cooling channel  directive 4.2:397-398
PITCH     = LY + GAP     # 0.033 m
NX, NY, NZ = 20, 6, 1    # per-cell mesh -> 120 cells/cell, 960 total

# ------------------------------------------------------------------ physics
RHO       = 2500.0       # kg/m3      directive 4.2:402
CP        = 1000.0       # J/kgK      directive 4.2:402-403
# directive 4.2:403-407 registers ANISOTROPIC k (in-plane 25, through-plane 1)
# and gives an explicit fallback, which is the branch taken here:
#   "if the anisotropic path is not available in the chosen solver at v2606,
#    run isotropic k = 3 W/mK and DISCLOSE"
KAPPA     = 3.0          # W/mK isotropic -- THE DIRECTIVE'S OWN FALLBACK, DISCLOSED
KAPPA_BASIS = ("directive 4.2:406-407 isotropic fallback, DISCLOSED; "
               "anisotropic solidThermo tensorial kappa NOT used")

T_INIT    = 293.0        # K          directive 4.3:418
T_INF     = 293.0        # K          directive 4.3:418 (coolant inlet 293 K)

# ------------------------------------------------------------------ the pulse
# directive 4.3:411-414 --  q_takeoff for 0 <= t < 60 s, q_cruise for
# 60 <= t <= 900 s;  P_takeoff = 15 W per cell (heat), q_cruise = 4 W per cell.
V_CELL    = LX * LY * LZ          # 3.000e-03 m3
P_TAKEOFF = 15.0                  # W per cell   directive 4.3:412-413
P_CRUISE  = 4.0                   # W per cell   directive 4.3:413
Q_TAKEOFF = P_TAKEOFF / V_CELL    # 5000.0 W/m3  (matches T20's registered 5000)
Q_CRUISE  = P_CRUISE / V_CELL     # 1333.333... W/m3
T_PULSE   = 60.0                  # s            directive 4.3:411
T_END     = 900.0                 # s            directive 4.3:411, 4.5:437

# ------------------------------------------------------------------ channel h
# The directive pins the channel FLOW (4.4:421-425: air, U_inlet 8 m/s in the
# 3 mm gaps, Re_Dh ~ 3200, transitional) but the coupled fluid region is NOT
# built in this feasibility rung.  h is therefore DERIVED from the directive's
# own flow statement and DISCLOSED as declared-representative:
#   Dh = 2*gap = 0.006 m;  air at ~300 K: k=0.0263 W/mK, nu=1.57e-5 m2/s,
#   Pr=0.707.  Re = U*Dh/nu = 8*0.006/1.57e-5 = 3057 (directive says ~3200).
#   Dittus-Boelter:  Nu = 0.023 Re^0.8 Pr^0.4 = 12.30
#   h  = Nu*k/Dh = 12.30*0.0263/0.006 = 53.9 W/m2K
# NOT MEASURED, NOT VALIDATED, NOT A GATE.  It is a plausible channel-side
# coefficient chosen so the module responds on a physical timescale.
H_CONV    = 53.9
H_BASIS   = ("DERIVED from directive 4.4:421-425 (U=8 m/s, Dh=6 mm, Re~3057) "
             "via Dittus-Boelter; declared-representative, NOT measured, NOT a gate")

DT_DEFAULT = 0.5         # s -- solid-only implicit conduction; no Courant limit
WRITE_INT = 5.0          # s          directive 4.5:437 "every 5 s for fields"
REGION    = "module"
SOLVER    = "chtMultiRegionFoam"

# ------------------------------------------------- the residual pulse ramp
# The Function1 table below interpolates LINEARLY between breakpoints, so the
# pulse edge is a ramp of finite width, not a step.  These two decimals are the
# ends of that ramp and are written into the table verbatim, so the check and
# the dictionary cannot drift apart.
RAMP_LO_STR = "59.999"
RAMP_HI_STR = "60.000"


def ramp_interior_steps(dt, t_end=T_END):
    """Solver step times falling STRICTLY inside the residual ramp.

    Exact decimal arithmetic (Fraction over the decimal strings), so this is a
    statement about the times OpenFOAM will actually reach, not about binary
    rounding.  Returns the list of offending times; empty is the pass.
    """
    d = Fraction(str(dt))
    lo = Fraction(RAMP_LO_STR)
    hi = Fraction(RAMP_HI_STR)
    end = Fraction(str(t_end))
    n_first = max(int(lo / d) - 1, 0)
    n_last = int(hi / d) + 1
    hits = []
    for n in range(n_first, n_last + 1):
        t = n * d
        if lo < t < hi and t <= end:
            hits.append(t)
    return hits


def header(cls, obj, loc):
    return textwrap.dedent(f"""\
        FoamFile
        {{
            version     2.0;
            format      ascii;
            class       {cls};
            location    "{loc}";
            object      {obj};
        }}
        // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
        """)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        fh.write(text)


def cell_y(i):
    """(y_lo, y_hi) of cell i, i = 0..N_CELLS-1."""
    y0 = i * PITCH
    return y0, y0 + LY


def block_mesh_dict():
    verts, blocks = [], []
    faces_channel, faces_casing, faces_end = [], [], []
    faces_front, faces_back = [], []
    for i in range(N_CELLS):
        y0, y1 = cell_y(i)
        b = 8 * i
        verts += [
            f"    ({0:.6f} {y0:.6f} {0:.6f})",
            f"    ({LX:.6f} {y0:.6f} {0:.6f})",
            f"    ({LX:.6f} {y1:.6f} {0:.6f})",
            f"    ({0:.6f} {y1:.6f} {0:.6f})",
            f"    ({0:.6f} {y0:.6f} {LZ:.6f})",
            f"    ({LX:.6f} {y0:.6f} {LZ:.6f})",
            f"    ({LX:.6f} {y1:.6f} {LZ:.6f})",
            f"    ({0:.6f} {y1:.6f} {LZ:.6f})",
        ]
        blocks.append(
            f"    hex ({b+0} {b+1} {b+2} {b+3} {b+4} {b+5} {b+6} {b+7}) "
            f"({NX} {NY} {NZ}) simpleGrading (1 1 1)")
        # y-lo face of this cell: casing for cell 0, channel otherwise
        ylo = f"        ({b+0} {b+1} {b+5} {b+4})"
        yhi = f"        ({b+3} {b+7} {b+6} {b+2})"
        (faces_casing if i == 0 else faces_channel).append(ylo)
        (faces_casing if i == N_CELLS - 1 else faces_channel).append(yhi)
        # flow-direction ends -> plenums; adiabatic here, DISCLOSED
        faces_end.append(f"        ({b+0} {b+4} {b+7} {b+3})")
        faces_end.append(f"        ({b+1} {b+2} {b+6} {b+5})")
        faces_back.append(f"        ({b+0} {b+3} {b+2} {b+1})")
        faces_front.append(f"        ({b+4} {b+5} {b+6} {b+7})")

    def patch(name, ptype, faces):
        body = "\n".join(faces)
        return (f"    {name}\n    {{\n        type {ptype};\n"
                f"        faces\n        (\n{body}\n        );\n    }}\n")

    return (header("dictionary", "blockMeshDict", "system") + f"""
scale   1;

// 8 DISCONNECTED blocks -- one per prismatic cell.  The 3 mm channels of
// directive 4.2:397-398 are NOT meshed in this feasibility rung; their effect
// enters as an imposed convective coefficient on the channel-facing patches.

vertices
(
{chr(10).join(verts)}
);

blocks
(
{chr(10).join(blocks)}
);

edges ();

boundary
(
{patch("channelFaces", "wall", faces_channel)}{patch("casingWalls", "wall", faces_casing)}{patch("ends", "wall", faces_end)}{patch("front", "empty", faces_front)}{patch("back", "empty", faces_back)}
);

mergePatchPairs ();

// ****************************************************************** //
""")


def field_T():
    return (header("volScalarField", "T", f"0/{REGION}") + f"""
dimensions      [0 0 0 1 0 0 0];

internalField   uniform {T_INIT};

boundaryField
{{
    channelFaces
    {{
        type            externalWallHeatFluxTemperature;
        mode            coefficient;
        h               constant {H_CONV};
        Ta              constant {T_INF};
        emissivity      0;
        kappaMethod     solidThermo;
        value           uniform {T_INIT};
    }}
    casingWalls
    {{
        type            zeroGradient;   // directive 4.2:408 adiabatic casing
    }}
    ends
    {{
        type            zeroGradient;   // plenum ends; adiabatic, DISCLOSED
    }}
    "front|back"
    {{
        type            empty;
    }}
}}

// ****************************************************************** //
""")


def field_p():
    return (header("volScalarField", "p", f"0/{REGION}") + f"""
dimensions      [1 -1 -2 0 0 0 0];

internalField   uniform 1e5;

boundaryField
{{
    "channelFaces|casingWalls|ends"
    {{
        type            zeroGradient;
    }}
    "front|back"
    {{
        type            empty;
    }}
}}

// ****************************************************************** //
""")


def thermo():
    return (header("dictionary", "thermophysicalProperties", f"constant/{REGION}") + f"""
thermoType
{{
    type            heSolidThermo;
    mixture         pureMixture;
    transport       constIso;
    thermo          hConst;
    equationOfState rhoConst;
    specie          specie;
    energy          sensibleEnthalpy;
}}

mixture
{{
    specie          {{ molWeight   50; }}
    transport       {{ kappa       {KAPPA}; }}   // {KAPPA_BASIS}
    thermodynamics  {{ Hf          0; Cp {CP}; }}
    equationOfState {{ rho         {RHO}; }}
}}

// ****************************************************************** //
""")


def fv_options(dt):
    return (header("dictionary", "fvOptions", f"constant/{REGION}") + f"""
// THE TAKEOFF PULSE -- directive 4.3:411-414, implemented as the directive
// asks: scalarSemiImplicitSource with a time-dependent Function1 table.
//   0 <= t < 60 s   : {P_TAKEOFF} W/cell / {V_CELL:.6e} m3 = {Q_TAKEOFF:.6f} W/m3
//   60 <= t <= 900 s: {P_CRUISE} W/cell / {V_CELL:.6e} m3 = {Q_CRUISE:.6f} W/m3
//
// BREAKPOINT PLACEMENT -- repaired 2026-08-31, BEFORE first compute.
// OpenFOAM's Function1 table defaults interpolationScheme to "linear"
// (v2606 src/OpenFOAM/primitives/functions/Function1/Table/TableBase.C,
// getOrDefault<word>("interpolationScheme", "linear", keyType::LITERAL)),
// so the two breakpoints around the pulse edge are the ends of a RAMP, not
// a step.  The ramp originally spanned 59.999 -> 60.001, straddling t = 60;
// with deltaT 0.5 the solver lands exactly on t = 60.000, mid-ramp, and
// sampled 3166.666667 W/m3 there -- but the directive pins t = 60 in the
// CRUISE branch (60 <= t <= 900), i.e. {Q_CRUISE:.6f} W/m3.  The file
// contradicted the directive at exactly one instant.  The ramp now ENDS at
// 60.000, so t = 60 samples the cruise endpoint exactly and the takeoff
// branch is unaffected for every t <= 59.999.
// Residual: a 1 ms ramp in ({RAMP_LO_STR}, {RAMP_HI_STR}) remains -- a
// piecewise-linear table cannot represent a true discontinuity.  THIS CASE
// STEPS AT deltaT {dt}, and the builder EVALUATED the sampling condition for
// that step before writing this file: steps falling strictly inside the ramp
// = {len(ramp_interior_steps(dt))}.  The builder refuses to emit a case for
// which that count is non-zero.  A deltaT finer than 1 ms would sample the
// ramp, and that is the condition under which this placement must be
// revisited.

volumetricHeatSource
{{
    type            scalarSemiImplicitSource;
    selectionMode   all;
    volumeMode      specific;
    sources
    {{
        h
        {{
            explicit    table
            (
                (  0.000  {Q_TAKEOFF:.6f})
                ({RAMP_LO_STR:>7}  {Q_TAKEOFF:.6f})
                ({RAMP_HI_STR:>7}  {Q_CRUISE:.6f})
                ({T_END:.3f}  {Q_CRUISE:.6f})
            );
            implicit    none;
        }}
    }}
}}

// ****************************************************************** //
""")


def control_dict(dt):
    probes = []
    for idx in (0, 3, 7):                       # cells 1, 4, 8 -- directive 4.5:438
        y0, y1 = cell_y(idx)
        probes.append(f"            ({LX/2:.6f} {(y0+y1)/2:.6f} {LZ/2:.6f})")
    return (header("dictionary", "controlDict", "system") + f"""
application     {SOLVER};

startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {T_END};

deltaT          {dt};

writeControl    runTime;
writeInterval   {WRITE_INT};

purgeWrite      0;
writeFormat     ascii;
writePrecision  12;
writeCompression off;
timeFormat      general;
timePrecision   12;
runTimeModifiable no;
adjustTimeStep  no;

functions
{{
    cellProbes
    {{
        type            probes;
        libs            (sampling);
        region          {REGION};
        writeControl    timeStep;
        writeInterval   1;
        fields          (T);
        probeLocations
        (
{chr(10).join(probes)}
        );
    }}
    moduleMinMax
    {{
        type            fieldMinMax;
        libs            (fieldFunctionObjects);
        region          {REGION};
        writeControl    timeStep;
        writeInterval   1;
        fields          (T);
    }}
}}

// ****************************************************************** //
""")


FVSCHEMES = """
ddtSchemes      { default Euler; }
gradSchemes     { default Gauss linear; }
divSchemes      { default none; }
laplacianSchemes{ default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes   { default corrected; }

// ****************************************************************** //
"""

FVSOLUTION = """
solvers
{
    h
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-12;
        relTol          0;
    }
    hFinal
    {
        $h;
        tolerance       1e-12;
        relTol          0;
    }
}

PIMPLE
{
    nNonOrthogonalCorrectors 0;
}

// ****************************************************************** //
"""


def case_txt(case_dir, n_cells_total, dt):
    return f"""T25 -- CASE 4 8-CELL BATTERY MODULE, TAKEOFF PULSE
==================================================================
*** UNGATED FEASIBILITY RUN.  NOT GRID-CONVERGED.  NOT GATED.
*** NO VERDICT.  NO ROACHE TRIPLE.  NO GCI.  NOT A RESULT.
==================================================================

WHAT THIS IS
  An 8-cell battery module driven by the directive's takeoff power pulse,
  built to answer ONE feasibility question: does the module geometry mesh,
  build and step under chtMultiRegionFoam at v2606, and does it produce
  per-cell temperature histories with a visible module spread?

WHAT THIS IS NOT
  It is not a verified result and may not be graded.  The coupled air
  channel is NOT exercised (see SIMPLIFICATIONS).  No gate, threshold or
  band exists for any quantity here, and none may be invented after the
  fact from these numbers.

PROVENANCE OF EVERY VALUE
  directive = etc/sessions/2026-08-30T2300Z_sanaa_four_new_case_families.md

  n cells                8            directive 4.2:396
  cell Lx (flow)         {LX} m        directive 4.2:396
  cell Ly (thickness)    {LY} m       directive 4.2:397
  cell Lz (unit depth)   {LZ} m       directive 4.2:397
  channel gap            {GAP} m      directive 4.2:397-398
  module height          {(N_CELLS-1)*PITCH + LY:.3f} m       DERIVED: 8*{LY} + 7*{GAP}
  rho                    {RHO} kg/m3  directive 4.2:402
  cp                     {CP} J/kgK   directive 4.2:402-403
  kappa                  {KAPPA} W/mK      {KAPPA_BASIS}
  T_initial              {T_INIT} K       directive 4.3:418
  T_inf (coolant)        {T_INF} K       directive 4.3:418
  P_takeoff              {P_TAKEOFF} W/cell   directive 4.3:412-413
  P_cruise               {P_CRUISE} W/cell    directive 4.3:413
  V_cell                 {V_CELL:.6e} m3  DERIVED: Lx*Ly*Lz
  q_takeoff              {Q_TAKEOFF:.4f} W/m3 DERIVED: P_takeoff/V_cell
  q_cruise               {Q_CRUISE:.4f} W/m3 DERIVED: P_cruise/V_cell
  pulse switch           t = {T_PULSE} s     directive 4.3:411
  duration               {T_END} s      directive 4.3:411, 4.5:437
  write interval         {WRITE_INT} s        directive 4.5:437
  h (channel faces)      {H_CONV} W/m2K   {H_BASIS}
  deltaT                 {dt} s        CHOSEN: solid-only implicit conduction,
                                      no Courant constraint (no fluid region)
  mesh                   {NX}x{NY}x{NZ} per cell -> {n_cells_total} cells total   CHOSEN
  solver                 {SOLVER}   directive 4.5:431

SIMPLIFICATIONS -- EVERY ONE A DEPARTURE FROM THE DIRECTIVE, STATED AT SIZE
  1. THE COOLING CHANNELS ARE NOT MESHED.  Directive 4.4:420-428 registers a
     coupled air flow (U_inlet 8 m/s, kOmegaSST, turbulentTemperature-
     CoupledBaffleMixed interfaces).  This rung imposes a convective
     coefficient on the channel-facing patches instead.  Nothing here says
     anything about the channel flow, the outlet coolant temperature, or the
     laminar-vs-SST model-form sensitivity of directive 4.6:465.
     WHY: a Courant-limited coupled solve at max Co 1 in a 3 mm gap at
     8 m/s needs dt ~ 4e-5 s; 900 s of that is ~2e7 steps and is not a
     tonight-sized job.  The reduction is what makes a feasibility answer
     available at all, and it is disclosed rather than absorbed.
  2. ISOTROPIC kappa = {KAPPA} W/mK, not the registered anisotropic
     (in-plane 25 / through-plane 1).  This is the directive's OWN stated
     fallback at 4.2:406-407, taken with the DISCLOSE it demands.
  3. THE FLOW-DIRECTION ENDS ARE ADIABATIC.  Directive 4.2:401 gives a 50 mm
     inlet plenum and a 100 mm exit plenum; neither is built.
  4. NO cell-to-cell conduction path (directive 4.4:427-428 puts contact
     through the channel only in rung A, so this matches rung A).
  5. h IS DERIVED, NOT MEASURED, and not validated against anything.

WHAT THE MODULE SPREAD IN THIS RUN ACTUALLY MEANS
  Cells 1 and 8 sit against the adiabatic casing (directive 4.2:408) and are
  cooled on ONE face; cells 2-7 are cooled on TWO.  The spread this run
  produces is that geometric asymmetry and nothing else.  It is NOT the
  coolant-heating-along-the-channel mechanism, which needs the fluid region.

RULE 4 COMPLETION -- the field list for THIS case, measured not inherited
  Fields expected at <endTime>/{REGION}/ : T and p.
  NOT the thermal-family default T U p_rgh alphat nut k omega -- there is no
  fluid region and those fields do not and must not exist.  p is present
  because a solid region of {SOLVER} requires it (T20's launcher guards on
  exactly {{T, p}} for the same reason).

case_dir = {case_dir}

==================================================================
TIME STEP, AND THE PULSE-TABLE SAMPLING CHECK FOR IT
(appended 2026-08-31 when the step size became a build parameter;
 every line above this block kept its original line number)
==================================================================
  deltaT for THIS case    {dt} s
  steps to endTime        {int(round(T_END / dt))}   DERIVED: {T_END} / {dt}

  The step-size family built from this builder:
    T25_MOD_L1        deltaT 0.5  s   the baseline
    T25_MOD_L1_DT025  deltaT 0.25 s   half the step, EVERYTHING else identical
  The two differ in system/controlDict deltaT and in nothing else; both are
  emitted by build_t25.py, neither is a hand-copied tree.

  THE PULSE EDGE IS A RAMP, AND THIS IS THE CHECK THAT IT IS NOT SAMPLED.
  constant/{REGION}/fvOptions holds a Function1 table whose default
  interpolation is LINEAR, so the breakpoints at {RAMP_LO_STR} and
  {RAMP_HI_STR} are the ends of a 1 ms ramp rather than a discontinuity.
  A solver step landing strictly inside that ramp would sample a heat source
  that is neither the takeoff value nor the cruise value.
    solver step times           n * {dt} s, n = 0 .. {int(round(T_END / dt))}
    steps strictly inside
      ({RAMP_LO_STR}, {RAMP_HI_STR})       {len(ramp_interior_steps(dt))}
  The builder evaluates this in exact decimal arithmetic before writing any
  dictionary and REFUSES to emit the case if the count is not zero.  It is a
  guard, not a comment.  A deltaT finer than 1 ms would sample the ramp and
  the breakpoint placement would have to be revisited.
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--case-dir", required=True)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--delta-t", type=float, default=DT_DEFAULT,
                    help="solver time step, s (default %(default)s)")
    a = ap.parse_args()
    case = os.path.abspath(a.case_dir)
    dt = a.delta_t

    # ---- guard: the pulse edge is a ramp; no step may land inside it -------
    if dt <= 0:
        sys.exit(f"REFUSE: --delta-t must be positive, got {dt}")
    hits = ramp_interior_steps(dt)
    if hits:
        sys.exit(
            f"REFUSE: deltaT {dt} s puts {len(hits)} solver step(s) strictly "
            f"inside the residual pulse ramp ({RAMP_LO_STR}, {RAMP_HI_STR}): "
            + ", ".join(str(float(t)) for t in hits[:8])
            + ".  The breakpoint placement must be revisited before a case at "
              "this step size is built; it is not a matter of rebuilding.")

    # ---- guard: never build into a case that already has 0/ or a time dir ---
    if os.path.isdir(case):
        if os.path.exists(os.path.join(case, "0")):
            sys.exit(f"REFUSE: {case} already has a 0/ directory")
        for d in os.listdir(case):
            if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d) and \
               os.path.isdir(os.path.join(case, d)):
                sys.exit(f"REFUSE: {case} already has time directory {d}")
        if os.path.exists(os.path.join(case, "constant")) and not a.force:
            sys.exit(f"REFUSE: {case} already built; pass --force to rebuild")
        if a.force:
            shutil.rmtree(case)
    os.makedirs(case, exist_ok=True)

    write(f"{case}/system/blockMeshDict",            block_mesh_dict())
    write(f"{case}/system/{REGION}/blockMeshDict",   block_mesh_dict())
    write(f"{case}/system/controlDict",              control_dict(dt))
    write(f"{case}/system/fvSchemes",                header("dictionary", "fvSchemes", "system") + FVSCHEMES)
    write(f"{case}/system/fvSolution",               header("dictionary", "fvSolution", "system") + FVSOLUTION)
    write(f"{case}/system/{REGION}/fvSchemes",       header("dictionary", "fvSchemes", f"system/{REGION}") + FVSCHEMES)
    write(f"{case}/system/{REGION}/fvSolution",      header("dictionary", "fvSolution", f"system/{REGION}") + FVSOLUTION)
    write(f"{case}/constant/{REGION}/thermophysicalProperties", thermo())
    write(f"{case}/constant/{REGION}/fvOptions",     fv_options(dt))
    write(f"{case}/0.orig/{REGION}/T",               field_T())
    write(f"{case}/0.orig/{REGION}/p",               field_p())

    # ---- regionProperties: zero fluid regions ------------------------------
    write(f"{case}/constant/regionProperties",
          header("dictionary", "regionProperties", "constant") + f"""
regions
(
    fluid   ()
    solid   ({REGION})
);

// ****************************************************************** //
""")

    # ---- constant/g -- THE T20_LC_c LESSON, EMITTED AND THEN ASSERTED ------
    write(f"{case}/constant/g",
          header("uniformDimensionedVectorField", "g", "constant") + """
dimensions      [0 1 -2 0 0 0 0];
value           (0 0 0);

// ****************************************************************** //
""")

    # ---- mesh --------------------------------------------------------------
    env = os.environ.copy()
    bm = subprocess.run(
        ["bash", "-lc",
         f'set +u; . /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1; '
         f'blockMesh -case "{case}" -region {REGION}'],
        capture_output=True, text=True, env=env)
    write(f"{case}/log.blockMesh", bm.stdout + bm.stderr)
    if bm.returncode != 0:
        sys.exit(f"REFUSE: blockMesh rc={bm.returncode}; see {case}/log.blockMesh")

    owner = f"{case}/constant/{REGION}/polyMesh/owner"
    if not os.path.exists(owner):
        sys.exit(f"REFUSE: blockMesh produced no mesh at {owner}")

    n_cells = N_CELLS * NX * NY * NZ
    write(f"{case}/CASE.txt", case_txt(case, n_cells, dt))

    # ---- ASSERTIONS: the guards that are cheap, actually evaluated ----------
    problems = []
    if not os.path.exists(f"{case}/constant/g"):
        problems.append("constant/g ABSENT -- this is exactly what killed T20_LC_c")
    for f in ("T", "p"):
        if not os.path.exists(f"{case}/0.orig/{REGION}/{f}"):
            problems.append(f"0.orig/{REGION}/{f} ABSENT")
    if not os.path.exists(f"{case}/constant/regionProperties"):
        problems.append("constant/regionProperties ABSENT")

    # Read the step back OFF DISK rather than trusting the variable that wrote
    # it: the whole point of the second case is that its deltaT differs.
    cd_text = open(f"{case}/system/controlDict").read()
    m = re.search(r"^\s*deltaT\s+([0-9.eE+-]+)\s*;", cd_text, re.M)
    if not m:
        problems.append("system/controlDict has no deltaT entry")
    elif float(m.group(1)) != dt:
        problems.append(
            f"system/controlDict deltaT reads {m.group(1)} on disk, wanted {dt}")

    # And read the pulse table back, so the sampling check is a check on the
    # dictionary that will actually be solved, not on this script's constants.
    fvo_text = open(f"{case}/constant/{REGION}/fvOptions").read()
    for bp in (RAMP_LO_STR, RAMP_HI_STR):
        if f"({bp:>7}  " not in fvo_text:
            problems.append(f"pulse table breakpoint {bp} ABSENT from fvOptions")
    if problems:
        sys.exit("REFUSE: " + "; ".join(problems))

    print(f"BUILT {case}")
    print(f"  cells      {n_cells}  ({N_CELLS} blocks x {NX}x{NY}x{NZ})")
    print(f"  constant/g present: {os.path.exists(f'{case}/constant/g')}")
    print(f"  q_takeoff  {Q_TAKEOFF:.4f} W/m3 for t < {T_PULSE} s")
    print(f"  q_cruise   {Q_CRUISE:.4f} W/m3 for t >= {T_PULSE} s")
    print(f"  deltaT     {dt} s, read back from disk as {m.group(1)}")
    print(f"  endTime    {T_END} s at deltaT {dt} s -> "
          f"{int(round(T_END/dt))} steps")
    print(f"  ramp ({RAMP_LO_STR}, {RAMP_HI_STR}) interior steps: "
          f"{len(hits)}   (must be 0)")


if __name__ == "__main__":
    main()
