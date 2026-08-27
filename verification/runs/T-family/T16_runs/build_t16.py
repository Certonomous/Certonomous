#!/usr/bin/env python3
"""Build T16's three registered cases: DEVELOPING laminar MIXED CONVECTION in a
vertical parallel-plate channel with asymmetric isothermal walls,
buoyantBoussinesqSimpleFoam, LAMINAR, 2-D.

WHAT THE CASE IS.  An OPEN channel of gap b = 0.02 m (x) and height H = ASPECT*b
(y), hot wall at x = 0 (T_h), cold wall at x = b (T_c), one cell deep (empty
front/back), gravity (0 -g 0).  Fluid enters at y = 0 with a UNIFORM (plug)
upward velocity U0 and leaves at y = H.  The flow develops from the plug profile
into the fully developed mixed-convection profile that `exact_t16.py` DERIVES
from the Boussinesq equations; the comparator grades one row at the registered
STATION and proves with witness W1 that the row is z-invariant, i.e. developed.

WHY THE TEMPERATURE FIELD IS EXACT EVERYWHERE, INLET INCLUDED.  The inlet and
outlet carry `zeroGradient` on T.  The linear field T = T_c + dT (1 - x/b)
satisfies the interior equation (it has no y dependence, so u.grad(T) = 0, and
it is harmonic in x), both wall Dirichlet conditions, AND both zeroGradient
conditions -- so it is the exact continuous solution FOR ANY velocity field.
There is therefore NO thermal entrance region and the buoyancy that drives the
momentum equation is the exact buoyancy from the first iteration.  ONLY the
HYDRODYNAMIC development remains, and its length is what the registered
ASPECT and STATION are sized on (measured, not assumed -- see the
pre-registration's scratch probe).

THE MESH FAMILY.  N x (ASPECT*N) SQUARE cells, N = 20 / 40 / 80: r21 = r32 = 2
exactly in both directions; non-orthogonality 0, skewness 0, aspect ratio 1 by
construction.  The mesh is BUILT HERE (blockMesh + checkMesh at build time,
MESH_STANDARD.md 8.1 "build before you freeze"); polyMesh is not committed, the
dictionaries and the birth certificate (BUILD.txt, log.blockMesh,
log.checkMesh.build) are.

THE L-341 HAZARD DOES NOT ARISE.  Every boundary condition here is
fixedValue / zeroGradient / noSlip / fixedFluxPressure -- conditions whose
parameters are purely physical.  No `mixed` (Robin) condition is used, so no
coefficient contains the mesh spacing and nothing has to be recomputed per
level.  `--check-levels` makes that claim executable: it REFUSES if any 0.orig
field carries a `mixed` entry, and REFUSES unless the three levels share every
physical constant and differ ONLY in N.

WHAT IS WRITTEN AT BUILD.  0.orig only.  No 0/ and no numeric time directory may
exist in a case at the freeze; the launcher (run_one_t16.sh) creates 0/ from
0.orig and touches 0/T last (the age-guard datum, standing rule 4).

NO `assert` STATEMENT IN THIS FILE (L-332).  Every refusal is sys.exit(2).

Usage:  build_t16.py --root DIR [--level c|m|f ...]        build cases
        build_t16.py --check-levels                         run the guards only
        build_t16.py --write-registered [--root DIR]        write T16_registered.json
        build_t16.py --selftest                             drive the guards
        build_t16.py --probe DIR --N n --aspect a --end e   build ONE scratch
                                                            probe case (disclosed
                                                            pre-compute, outside
                                                            the repository)
"""
import argparse
import ast
import json
import math
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exact_t16 as EX                                   # noqa: E402

# ---------------------------------------------------------------- constants
B      = 0.02                 # m, channel gap (x)
ASPECT = 64                   # H / b -- sized on the MEASURED development length
H      = ASPECT * B           # m, channel height (y)
W      = 0.001                # m, depth of the single cell (empty direction)
NU     = 1.5e-5               # m2/s
PR     = 0.71
PRT    = 0.85                 # unused in laminar; carried for the dictionary form
BETA   = 1.0 / 300.0          # 1/K
G_ACC  = 9.81                 # m/s2
RE     = 100.0                # registered Reynolds number, U0 b / nu
U0     = RE * NU / B          # m/s, the MEAN (and here also the inlet plug) speed
G_MIX  = EX.G_REG             # registered mixed-convection group Gr/Re = 48
DT     = G_MIX * NU * U0 / (G_ACC * BETA * B * B)     # K, DERIVED from G_MIX
T_COLD = 300.0                # K, = TRef: the Boussinesq reference is the COLD wall
T_HOT  = T_COLD + DT
TREF   = T_COLD

# the graded station, in gaps from the inlet, and the witness offsets
STATION_B  = 48              # y_station = STATION_B * b
WITNESS_B  = (-8, -4, +4, +8)   # gaps, relative to the station

LEVELS   = {"c": 20, "m": 40, "f": 80}
END_TIME = {"c": 10000, "m": 20000, "f": 40000}

# cost: POINT from the MEASURED scratch probe of THIS case on THIS box
# (T16_PREREGISTRATION.md section 8); CEILING from T13's registered ceiling
# rate, T4 level c on the same solver, MEASURED (C-119).
RATE_POINT   = None          # filled by --write-registered from RATE_POINT_MEASURED
RATE_POINT_MEASURED = 3.8932e-06   # core-s per cell-iteration, MEASURED (see section 8)
RATE_CEILING = 5.874e-06
CAP_CORE_MIN = {"c": 40, "m": 300, "f": 2400}
RANKS = 1
SOLVER = "buoyantBoussinesqSimpleFoam"
FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"

EXIT_OK, EXIT_REFUSE = 0, 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def case_name(level):
    return "T16_MC_%s" % level


def cells(level):
    N = LEVELS[level]
    return N * ASPECT * N


def head(cls, obj, loc=None):
    l = ('    location    "%s";\n' % loc) if loc else ""
    return ("FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
            "    class       %s;\n%s    object      %s;\n}\n" % (cls, l, obj))


# ------------------------------------------------------------------ guards
def check_levels(g_mix=None, fields_text=None):
    """Executable form of three registration claims.  REFUSES (exit 2) if the
    derived mixed-convection group is not the registered 48, if the registered
    G is not strictly below the DERIVED flow-reversal threshold, if the three
    levels differ in anything but N, or if a `mixed` condition is present."""
    g_mix = G_MIX if g_mix is None else g_mix
    dT = g_mix * NU * U0 / (G_ACC * BETA * B * B)
    g_back = G_ACC * BETA * dT * B * B / (NU * U0)
    if abs(g_back - G_MIX) > 1e-9:
        refuse("registered G = %g is not what the constants give: %.12g" % (G_MIX, g_back))
    if not g_back < EX.G_REVERSAL:
        refuse("G = %.12g is at or past the DERIVED reversal threshold %g; this rung "
               "registers an unreversed profile" % (g_back, EX.G_REVERSAL))
    re_back = U0 * B / NU
    if abs(re_back - RE) > 1e-9:
        refuse("registered Re = %g is not what the constants give: %.12g" % (RE, re_back))
    per_level = {lv: (B, H, NU, PR, BETA, TREF, G_ACC, dT, T_HOT, T_COLD, U0) for lv in LEVELS}
    if len(set(per_level.values())) != 1:
        refuse("physical constants differ across levels: %r" % per_level)
    txt = fields_text if fields_text is not None else "\n".join(
        fields(lv)[k] for lv in LEVELS for k in ("T", "U", "p_rgh", "alphat"))
    if re.search(r"\bmixed\b", txt):
        refuse("a `mixed` (Robin) boundary condition is present; L-341's mesh-dependent "
               "valueFraction hazard WOULD arise and this rung registers that it does not")
    if not 0 < STATION_B < ASPECT:
        refuse("the graded station %g b is not inside the channel of %g b" % (STATION_B, ASPECT))
    for w in WITNESS_B:
        if not 0 < STATION_B + w < ASPECT:
            refuse("witness offset %+d b puts a row outside the channel" % w)
    print("  check-levels PASSES: G = Gr/Re = %.12g from the constants (reversal at %g, "
          "margin %.4f); Re = %.12g; dT = %.17g K; U0 = %.17g m/s; station %g b of %g b; "
          "levels differ only in N = %s; no `mixed` BC"
          % (g_back, EX.G_REVERSAL, EX.G_REVERSAL / g_back, re_back, dT, U0,
             STATION_B, ASPECT, [LEVELS[k] for k in ("c", "m", "f")]))
    return True


# ----------------------------------------------------------- dictionaries
def block_mesh_dict(N, aspect):
    return (head("dictionary", "blockMeshDict", "system") +
            "scale 1;\n\nvertices\n(\n"
            "    (0 0 0) (%.17g 0 0) (%.17g %.17g 0) (0 %.17g 0)\n"
            "    (0 0 %.17g) (%.17g 0 %.17g) (%.17g %.17g %.17g) (0 %.17g %.17g)\n);\n\n"
            "blocks\n(\n    hex (0 1 2 3 4 5 6 7) (%d %d 1) simpleGrading (1 1 1)\n);\n\n"
            "edges ();\n\nboundary\n(\n"
            "    hot          { type wall;  faces ( (0 4 7 3) ); }\n"
            "    cold         { type wall;  faces ( (1 2 6 5) ); }\n"
            "    inlet        { type patch; faces ( (0 1 5 4) ); }\n"
            "    outlet       { type patch; faces ( (3 7 6 2) ); }\n"
            "    frontAndBack { type empty; faces ( (0 3 2 1) (4 5 6 7) ); }\n"
            ");\n\nmergePatchPairs ();\n"
            % (B, B, aspect * B, aspect * B, W, B, W, B, aspect * B, W, aspect * B, W,
               N, aspect * N))


def control_dict(end_time):
    return (head("dictionary", "controlDict", "system") +
            "application     %s;\nstartFrom       startTime;\nstartTime       0;\n"
            "stopAt          endTime;\nendTime         %d;\ndeltaT          1;\n"
            "writeControl    timeStep;\nwriteInterval   %d;\npurgeWrite      2;\n"
            "writeFormat     ascii;\nwritePrecision  16;\nwriteCompression off;\n"
            "timeFormat      general;\ntimePrecision   6;\nrunTimeModifiable false;\n"
            % (SOLVER, end_time, end_time // 10))


def fv_schemes():
    return (head("dictionary", "fvSchemes", "system") +
            "ddtSchemes      { default steadyState; }\n"
            "gradSchemes     { default Gauss linear; }\n"
            "divSchemes\n{\n    default         none;\n"
            "    div(phi,U)      bounded Gauss linearUpwind grad(U);\n"
            "    div(phi,T)      bounded Gauss limitedLinear 1;\n"
            "    div((nuEff*dev2(T(grad(U))))) Gauss linear;\n}\n"
            "laplacianSchemes { default Gauss linear corrected; }\n"
            "interpolationSchemes { default linear; }\n"
            "snGradSchemes   { default corrected; }\n")


def fv_solution():
    # NO residualControl (L-141): the run length is endTime by registration and
    # convergence is judged by the frozen comparator from the residual history.
    # CHOSEN ON THE DISCLOSED SCRATCH PROBES, BEFORE ANY FREEZE (section 8 of the
    # pre-registration).  Four combinations were run on scratch copies of THIS
    # case outside the repository.  With this one -- PCG/DIC, p_rgh 0.7, U 0.3 --
    # AND the consistent `prghPressure` outlet, the p_rgh outer initial residual
    # collapses: 5.3e-03 at 1 600 iterations, then 2.0e-05 / 6.4e-06 / 2.7e-06 /
    # 1.1e-06 / 4.7e-07 by 3 400 of the registered 10 000 at N = 20.  With the
    # INCONSISTENT `fixedValue uniform 0` outlet it stalled near 1.5e-03, and
    # GAMG with the channel relaxation split (p_rgh 0.3, U 0.7) limit-cycled near
    # 1.1e-02 for 3 600 iterations; neither is registered.  The registered
    # C_CONV floor is therefore the family's 1e-06, unweakened.
    return (head("dictionary", "fvSolution", "system") +
            "solvers\n{\n"
            "    p_rgh\n    {\n        solver          PCG;\n        preconditioner  DIC;\n"
            "        tolerance       1e-10;\n        relTol          0.01;\n    }\n"
            "    \"(U|T)\"\n    {\n        solver          PBiCGStab;\n        preconditioner  DILU;\n"
            "        tolerance       1e-12;\n        relTol          0.01;\n    }\n}\n\n"
            "SIMPLE\n{\n    nNonOrthogonalCorrectors 0;\n}\n\n"
            "relaxationFactors\n{\n    fields    { p_rgh 0.7; }\n"
            "    equations { U 0.3; T 0.5; }\n}\n")


def constant_files():
    return {
        "g": (head("uniformDimensionedVectorField", "g", "constant") +
              "dimensions      [0 1 -2 0 0 0 0];\nvalue           (0 %.17g 0);\n" % (-G_ACC)),
        "transportProperties": (head("dictionary", "transportProperties", "constant") +
                                "transportModel  Newtonian;\nnu              %.17g;\n"
                                "Pr              %.17g;\nPrt             %.17g;\n"
                                "beta            %.17g;\nTRef            %.17g;\n"
                                % (NU, PR, PRT, BETA, TREF)),
        "turbulenceProperties": (head("dictionary", "turbulenceProperties", "constant") +
                                 "simulationType  laminar;\n"),
    }


def fields(level=None):
    walls = "(hot|cold)"
    return {
        # T: walls Dirichlet, inlet AND outlet zeroGradient.  The linear field
        # satisfies all four exactly, for any velocity field -- see the header.
        "T": (head("volScalarField", "T", "0") +
              "dimensions      [0 0 0 1 0 0 0];\n\ninternalField   uniform %.17g;\n\n"
              "boundaryField\n{\n"
              "    hot          { type fixedValue; value uniform %.17g; }\n"
              "    cold         { type fixedValue; value uniform %.17g; }\n"
              "    inlet        { type zeroGradient; }\n"
              "    outlet       { type zeroGradient; }\n"
              "    frontAndBack { type empty; }\n}\n" % (T_COLD, T_HOT, T_COLD)),
        "U": (head("volVectorField", "U", "0") +
              "dimensions      [0 1 -1 0 0 0 0];\n\ninternalField   uniform (0 %.17g 0);\n\n"
              "boundaryField\n{\n"
              "    \"%s\"  { type noSlip; }\n"
              "    inlet        { type fixedValue; value uniform (0 %.17g 0); }\n"
              "    outlet       { type zeroGradient; }\n"
              "    frontAndBack { type empty; }\n}\n" % (U0, walls, U0)),
        "p_rgh": (head("volScalarField", "p_rgh", "0") +
                  "dimensions      [0 2 -2 0 0 0 0];\n\ninternalField   uniform 0;\n\n"
                  "boundaryField\n{\n"
                  "    \"%s\"  { type fixedFluxPressure; rho rhok; value uniform 0; }\n"
                  "    inlet        { type fixedFluxPressure; rho rhok; value uniform 0; }\n"
                  # NOT `fixedValue uniform 0`.  In this solver
                  # p_rgh = p - rhok*(g & h) with rhok = 1 - beta (T - TRef), so at a
                  # FIXED height p_rgh varies ACROSS the channel wherever T does.  At
                  # the outlet of this case that variation is
                  # beta dT g H = (1/300)(4.1284)(9.81)(1.28) = 1.73e-01 m2/s2, and
                  # pinning p_rgh uniform would force it to zero -- measured on the
                  # disclosed scratch probe as a violent last-row disturbance with
                  # REVERSED cells.  `prghPressure` sets p_rgh from a uniform STATIC
                  # pressure, which is the consistent statement.
                  "    outlet       { type prghPressure; rho rhok; p uniform 0; value uniform 0; }\n"
                  "    frontAndBack { type empty; }\n}\n" % walls),
        "alphat": (head("volScalarField", "alphat", "0") +
                   "dimensions      [0 2 -1 0 0 0 0];\n\ninternalField   uniform 0;\n\n"
                   "boundaryField\n{\n"
                   "    \"%s\"  { type calculated; value uniform 0; }\n"
                   "    inlet        { type calculated; value uniform 0; }\n"
                   "    outlet       { type calculated; value uniform 0; }\n"
                   "    frontAndBack { type empty; }\n}\n" % walls),
    }


# ------------------------------------------------------------------ build
def run_foam(tool, case, log):
    cmd = "source %s > /dev/null 2>&1; %s -case %s > %s 2>&1" % (FOAM_BASHRC, tool, case, log)
    t0 = time.time()
    r = subprocess.run(["bash", "-c", cmd])
    return r.returncode, time.time() - t0


def _write_case(case, N, aspect, end_time, name):
    for sub in ("system", "constant", "0.orig"):
        os.makedirs(os.path.join(case, sub), exist_ok=True)
    if os.path.exists(os.path.join(case, "0")):
        refuse("%s already has a 0/ directory; a case is built once, from nothing" % case)
    for d in os.listdir(case):
        if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d):
            refuse("%s already has time directory %s; refusing to build over it" % (case, d))
    open(os.path.join(case, "system", "blockMeshDict"), "w").write(block_mesh_dict(N, aspect))
    open(os.path.join(case, "system", "controlDict"), "w").write(control_dict(end_time))
    open(os.path.join(case, "system", "fvSchemes"), "w").write(fv_schemes())
    open(os.path.join(case, "system", "fvSolution"), "w").write(fv_solution())
    for k, v in constant_files().items():
        open(os.path.join(case, "constant", k), "w").write(v)
    for k, v in fields().items():
        open(os.path.join(case, "0.orig", k), "w").write(v)
    ncells = N * aspect * N
    open(os.path.join(case, "CASE.txt"), "w").write(
        "case=%s\nN=%d\nNy=%d\ncells=%d\nb=%.17g\nH=%.17g\naspect=%d\ndx=%.17g\n"
        "nu=%.17g\nPr=%.17g\nbeta=%.17g\nTRef=%.17g\ng=%.17g\nRe=%.17g\nG_mix=%.17g\n"
        "G_reversal=%.17g\ndT=%.17g\nT_hot=%.17g\nT_cold=%.17g\nU0=%.17g\n"
        "station_b=%g\nU_at_0p25=%.17g\nU_at_0p75=%.17g\nY_max=%.17g\nshear_ratio=%.17g\n"
        "endTime=%d\nwriteInterval=%d\nsolver=%s\nranks=%d\n"
        % (name, N, aspect * N, ncells, B, aspect * B, aspect, B / N,
           NU, PR, BETA, TREF, G_ACC, RE, G_MIX, EX.G_REVERSAL, DT, T_HOT, T_COLD, U0,
           STATION_B, EX.U(0.25), EX.U(0.75), EX.Y_max(), EX.shear_ratio(),
           end_time, end_time // 10, SOLVER, RANKS))
    rc_bm, t_bm = run_foam("blockMesh", case, os.path.join(case, "log.blockMesh"))
    if rc_bm != 0:
        refuse("blockMesh rc=%d on %s -- see log.blockMesh" % (rc_bm, case))
    rc_cm, t_cm = run_foam("checkMesh", case, os.path.join(case, "log.checkMesh.build"))
    body = open(os.path.join(case, "log.checkMesh.build"), errors="replace").read()
    mcells = re.search(r"^\s*cells:\s+(\d+)", body, re.M)
    if not mcells or int(mcells.group(1)) != ncells:
        refuse("checkMesh reports %s cells, registered %d"
               % (mcells.group(1) if mcells else None, ncells))
    lines = [ln.strip() for ln in body.splitlines()
             if re.search(r"cells:|non-orthogonality|skewness|aspect ratio|Mesh OK|Failed", ln)]
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    open(os.path.join(case, "BUILD.txt"), "w").write(
        "case            %s\ndate            %s\nblockMesh_rc    %d   wall %.3f s\n"
        "checkMesh_rc    %d   wall %.3f s\n%s\n"
        % (name, stamp, rc_bm, t_bm, rc_cm, t_cm,
           "\n".join("checkMesh       " + ln for ln in lines)))
    print("  built %s N=%d aspect=%d cells=%d blockMesh rc=%d checkMesh rc=%d (%s)"
          % (name, N, aspect, ncells, rc_bm, rc_cm,
             "; ".join(ln for ln in lines if "Mesh OK" in ln or "Failed" in ln)))
    return case


def build(root, level):
    return _write_case(os.path.join(root, case_name(level)), LEVELS[level], ASPECT,
                       END_TIME[level], case_name(level))


# --------------------------------------------------------- registered JSON
def registered():
    Ns = [LEVELS[k] for k in ("c", "m", "f")]
    exp = {r["N"]: r for r in EX.expectation_table(Ns)}
    cases = {}
    for lv in ("c", "m", "f"):
        N = LEVELS[lv]
        pt = cells(lv) * END_TIME[lv] * RATE_POINT_MEASURED / 60.0
        ce = cells(lv) * END_TIME[lv] * RATE_CEILING / 60.0
        cases[case_name(lv)] = dict(
            level=lv, N=N, Ny=ASPECT * N, cells=cells(lv), dx_m=B / N,
            endTime=END_TIME[lv], writeInterval=END_TIME[lv] // 10,
            cap_core_min=CAP_CORE_MIN[lv], timeout_s=CAP_CORE_MIN[lv] * 60 // RANKS,
            point_core_min=round(pt, 3), ceiling_core_min=round(ce, 3),
            expected_G1_rel_error=exp[N]["G1_rel_err"],
            expected_Ymax_error=exp[N]["G1b_abs_err"],
            expected_G3_rel_error=exp[N]["G3_rel_err"])
    f_rel = abs(exp[LEVELS["f"]]["G1_rel_err"])
    f_loc = abs(exp[LEVELS["f"]]["G1b_abs_err"])
    f_sr = abs(exp[LEVELS["f"]]["G3_rel_err"])
    return dict(
        rung="T16",
        title="developing laminar MIXED CONVECTION in a vertical parallel-plate channel with "
              "asymmetric isothermal walls, EXACT tier (referent DERIVED in exact_t16.py from "
              "the Boussinesq equations; NO paper is used and none is on disk)",
        capability_grid_cell="mixed convection x laminar x 2D (docs/capability/heat-transfer_GRID.md) "
                             "-- registered as CAN NOT DO / not attempted at HEAD c9ff33d9",
        solver=SOLVER, turbulence="laminar", dimensionality=2, ranks=RANKS,
        physics=dict(b_m=B, H_m=H, aspect=ASPECT, depth_m=W, nu=NU, Pr=PR, beta=BETA,
                     TRef=TREF, g=G_ACC, Re=RE, U0=U0, G_mix=G_MIX,
                     G_reversal=EX.G_REVERSAL, reversal_margin=EX.G_REVERSAL / G_MIX,
                     dT_K=DT, T_hot=T_HOT, T_cold=T_COLD,
                     station_gaps=STATION_B, witness_gaps=list(WITNESS_B),
                     U_at_0p25=EX.U(0.25), U_at_0p75=EX.U(0.75),
                     Y_max=EX.Y_max(), shear_ratio=EX.shear_ratio(), P_dimensionless=EX.P_of(G_MIX)),
        cases=cases, refinement_ratio=2.0, factor_of_safety=1.25,
        roache_floors=dict(
            source="scripts/roache_triple.py, imported by name (MESH_STANDARD.md section 10.5, "
                   "chief ruling 01967a7b); the comparator defines neither and REFUSES if these "
                   "numbers differ from the import",
            STAGNANT_FLOOR=0.5, P_MIN=0.05),
        graded_rows=dict(
            G1=dict(quantity="v(Y = 0.25)/U0 on the station row, 4-point Lagrange at cell centres",
                    reference=EX.U(0.25), band_rel=2.4e-4, grading="Roache triple, rule 5",
                    band_ground="3.0x the DERIVED fine-level discretisation error %.3e "
                                "(exact_t16.discrete_expectation); the coarse (%.3e) and medium "
                                "(%.3e) levels are predicted OUTSIDE it"
                                % (f_rel, abs(exp[20]["G1_rel_err"]), abs(exp[40]["G1_rel_err"]))),
            G1b=dict(quantity="Y_max, location of the maximum upflow on the station row, from the "
                              "cubic through the 4 cells around it",
                     reference=EX.Y_max(), band_abs=2.4e-4, grading="Roache triple, rule 5",
                     band_ground="3.0x the DERIVED fine-level error %.3e; coarse (%.3e) and medium "
                                 "(%.3e) predicted OUTSIDE"
                                 % (f_loc, abs(exp[20]["G1b_abs_err"]), abs(exp[40]["G1b_abs_err"]))),
            G3=dict(quantity="tau_hot / tau_cold from the half-cell wall gradients of v on the "
                             "station row",
                    reference=EX.shear_ratio(), band_rel=1.2e-3, grading="Roache triple, rule 5",
                    band_ground="3.0x the DERIVED fine-level error %.3e; coarse (%.3e) and medium "
                                "(%.3e) predicted OUTSIDE"
                                % (f_sr, abs(exp[20]["G3_rel_err"]), abs(exp[40]["G3_rel_err"]))),
            G2=dict(quantity="RMS over the station row of (T - T_lin)/dT",
                    reference=0.0, floor_abs=1.0e-6,
                    grading="ABSOLUTE FLOOR (EXACT-class row): the linear T is an exact solution of "
                            "the continuous problem for ANY velocity field and is in the null space "
                            "of the scheme's truncation error, so its triple is EXACT/DEGENERATE by "
                            "construction and rule 5 (2) would return NOT A RESULT for a row that "
                            "cannot be wrong by discretisation; the triple states are PRINTED, the "
                            "verdict is the floor")),
        controls=dict(
            C_CONV=dict(what="iterative convergence: initial residuals of Uy, T and p_rgh <= 1e-6 at "
                             "EVERY iteration of the final 10 percent; Ux is a near-degenerate "
                             "cross-channel component and is REPORTED, never gated (L-338). The "
                             "floor is the FAMILY'S 1e-6, unweakened, and it is registered because "
                             "it was MEASURED REACHABLE on the disclosed scratch probe of this "
                             "exact case: p_rgh fell 5.3e-03 -> 2.0e-05 -> 6.4e-06 -> 2.7e-06 -> "
                             "1.1e-06 -> 4.7e-07 by 3 400 of the registered 10 000 iterations at "
                             "N = 20, once the outlet carried the CONSISTENT prghPressure condition",
                        floor=1.0e-6),
            C_PLAT=dict(what="plateau: |G1(endTime) - G1(endTime - writeInterval)| / G1 <= 1e-7",
                        floor=1.0e-7),
            W1=dict(what="DEVELOPMENT witness and gate-(1) precondition: the rows at station "
                         "-16b, -8b, -4b, +4b, +8b must agree with the graded station row in "
                         "v/U0 to 2e-4 and in T/dT to 1e-6.  Exceeding it means the station is "
                         "NOT in the fully developed regime the referent describes -> the level "
                         "is NOT A RESULT under rule 5 clause (1).  This witness, not an assumed "
                         "entrance-length correlation, is what entitles the rung to compare "
                         "against a FULLY DEVELOPED closed form",
                     floor_row_max_v=2.0e-4, floor_graded_reader=2.0e-5, floor_T=1.0e-6),
            C_G=dict(what="operand identity (L-331): nu, Pr, beta, TRef, g, T_hot, T_cold, b, U0, N "
                          "are READ FROM THE CASE FILES, printed, and G = Gr/Re recomputed from them "
                          "must equal 48 to 1e-9; the DERIVED reversal threshold 72 is recomputed and "
                          "the margin printed",
                     floor=1.0e-9),
            C_MASS=dict(what="the station row's cell-volume-weighted mean of v must equal U0 to 1e-6 "
                             "relative -- the referent normalises on the MEAN velocity, so a station "
                             "row whose mean is not U0 is not the profile the closed form describes",
                        floor=1.0e-6),
            C_ORDER=dict(what="cell-ordering control: the station row's T must fall monotonically "
                              "from hot to cold with the registered slope -dT/b to 1e-6 relative; a "
                              "transposed ordering (y-fastest) shows a constant row and REFUSES"),
            C_PZ=dict(what="planted-zero control per reader (rule 3, L-340 sizing): a POINT plant for "
                           "the point readers G1/G1b/G3/W1, and an ALL-ROW ALTERNATING-SIGN plant for "
                           "the RMS reader G2 -- a constant offset is invisible to an RMS-about-the-"
                           "linear-fit reader BY CONSTRUCTION, so the plant is shaped to the reader; "
                           "both arms, a measured detection ladder, and REFUSAL on a blind reader")),
        predictions=dict(
            P1="G1, G1b and G3 triples CONVERGING with observed order p in [1.5, 2.5]; the derived "
               "expectation is p = 2.000 on all three",
            P2="G1 relative deviation at f in [+%.2e, +%.2e] (the derived %+.3e within 30 percent), "
               "POSITIVE sign; c and m OUTSIDE the +-2.4e-4 band"
               % (0.7 * exp[80]["G1_rel_err"], 1.3 * exp[80]["G1_rel_err"], exp[80]["G1_rel_err"]),
            P2b="Y_max error at f in [%.2e, %.2e] (the derived %+.3e within 30 percent), NEGATIVE sign"
                % (1.3 * exp[80]["G1b_abs_err"], 0.7 * exp[80]["G1b_abs_err"], exp[80]["G1b_abs_err"]),
            P2c="tau_hot/tau_cold relative deviation at f in [+%.2e, +%.2e] (the derived %+.3e within "
                "30 percent), POSITIVE sign"
                % (0.7 * exp[80]["G3_rel_err"], 1.3 * exp[80]["G3_rel_err"], exp[80]["G3_rel_err"]),
            P3="NO FLOW REVERSAL anywhere on the station row: v > 0 in every cell, and the cold-wall "
               "shear is POSITIVE.  G = 48 is exactly 2/3 of the DERIVED reversal threshold 72.  A "
               "reversed cell at the station FALSIFIES either the derivation or the solve and the "
               "rung reports it as such",
            P4="W1 development witness under 2e-5 ON THE GRADED READER and under 2e-4 in the row max-norm of v/U0 on every level at the registered station",
            P5="G2 RMS < 1e-7 at f -- the linear temperature field is exact for any velocity field",
            P6="all three levels meet C_CONV and C_PLAT within their registered endTime"),
        cost=dict(rate_point_core_s_per_cell_it=RATE_POINT_MEASURED,
                  rate_point_source="MEASURED on a SCRATCH COPY of this exact case on this box, "
                                    "outside the repository (T16_PREREGISTRATION.md section 8)",
                  rate_ceiling_core_s_per_cell_it=RATE_CEILING,
                  rate_ceiling_source="T4 level c, kOmegaSST on the same solver, MEASURED "
                                      "(STATUS.T4_IJ_c, C-119); carried as the CEILING only",
                  usd_per_core_h=0.0513,
                  usd_basis="derived, not measured, reported-by-owner rate "
                            "(COMPUTE_BUDGET_CHARTER section 5)"),
        completion=dict(needed_fields=["T", "U", "p_rgh", "phi"],
                        infrastructure_fields=["wall_s", "timeout_s", "ranks", "core_min", "capped",
                                               "checkmesh_rc", "solver", "solver_path", "note",
                                               "started_utc", "ended_utc"],
                        note="capped is an INFRASTRUCTURE field and never a completion conjunct (L-342)"),
    )


def selftest():
    fails = []
    print("build_t16 selftest (guards driven both ways):")
    try:
        check_levels()
        print("  [ok ] check-levels passes on the registered constants")
    except SystemExit:
        fails.append("check-levels refused the registered constants")
    fired = False
    try:
        check_levels(g_mix=49.0)
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    print("  [%s] G mutated to 49 -> REFUSE exit 2" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("gmix")
    fired = False
    try:
        check_levels(fields_text=fields()["T"].replace("zeroGradient", "mixed"))
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    print("  [%s] planted `mixed` BC -> REFUSE exit 2 (L-341 guard fires)" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("mixed")
    ok = all(cells(lv) == LEVELS[lv] ** 2 * ASPECT for lv in LEVELS) and \
        cells("m") == 4 * cells("c") and cells("f") == 4 * cells("m")
    print("  [%s] cells %d/%d/%d, r = 2 in 2-D"
          % ("ok " if ok else "FAIL", cells("c"), cells("m"), cells("f")))
    if not ok:
        fails.append("cells")
    ok = (abs(EX.U(0.25) - 1.5) < 1e-13 and abs(EX.shear_ratio() - 5.0) < 1e-13
          and abs(EX.Y_max() - (36.0 - math.sqrt(336.0)) / 48.0) < 1e-13)
    print("  [%s] the referent still returns U(0.25) = 1.5, tau ratio 5, Y_max = %.15f"
          % ("ok " if ok else "FAIL", EX.Y_max()))
    if not ok:
        fails.append("referent")
    n_assert = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse(open(os.path.abspath(__file__)).read())))
    planted = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse("assert 1\n")))
    ok = (n_assert == 0 and planted == 1)
    print("  [%s] AST assert count in this file = %d (counter sees a planted assert: %d)"
          % ("ok " if ok else "FAIL", n_assert, planted))
    if not ok:
        fails.append("ast")
    print("SELFTEST %s (%d failed)" % ("PASS" if not fails else "FAIL", len(fails)))
    return 0 if not fails else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root")
    ap.add_argument("--level", action="append", choices=list(LEVELS))
    ap.add_argument("--check-levels", action="store_true")
    ap.add_argument("--write-registered", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--probe")
    ap.add_argument("--N", type=int, default=20)
    ap.add_argument("--aspect", type=int, default=96)
    ap.add_argument("--end", type=int, default=4000)
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if a.check_levels:
        check_levels()
        sys.exit(EXIT_OK)
    if a.probe:
        # DISCLOSED pre-compute scratch probe.  It refuses to write anywhere
        # inside the repository, so it can never touch a registered tree.
        p = os.path.abspath(a.probe)
        if p.startswith(os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))):
            refuse("--probe target %s is inside the repository; a scratch probe lives outside it" % p)
        os.makedirs(p, exist_ok=True)
        _write_case(p, a.N, a.aspect, a.end, "T16_PROBE_N%d_A%d" % (a.N, a.aspect))
        sys.exit(EXIT_OK)
    if a.write_registered:
        out = os.path.join(a.root or HERE, "T16_registered.json")
        json.dump(registered(), open(out, "w"), indent=2)
        print("  wrote %s" % out)
        sys.exit(EXIT_OK)
    if not a.root:
        refuse("--root is required")
    r, f = EX.verify(quiet=True)
    if f:
        refuse("the referent's Route B does not verify: %s" % "; ".join(f))
    check_levels()
    for lv in (a.level or ["c", "m", "f"]):
        build(a.root, lv)
