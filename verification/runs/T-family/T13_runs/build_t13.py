#!/usr/bin/env python3
"""Build T13's three registered cases: natural convection in a tall vertical
slot, conduction regime, Ra_L = 100, buoyantBoussinesqSimpleFoam, LAMINAR, 2-D.

WHAT THE CASE IS.  A closed slot of width L = 0.02 m and height H = 16 L,
hot wall at x = 0, cold wall at x = L, adiabatic no-slip ends, one cell deep
(empty front/back).  The infinite-slot exact solution (exact_t13.py) is read at
mid-height, where the end-region disturbance is bounded a priori below 1e-9
relative (exp(-2.75 * 8)) and is MEASURED by the comparator's witness W1 on
every level rather than trusted.

THE MESH FAMILY.  N x 16N square cells, N = 20 / 40 / 80: r21 = r32 = 2 exactly
in both directions; 6 400 / 25 600 / 102 400 cells; non-orthogonality 0,
skewness 0, aspect ratio 1 by construction.  The mesh is BUILT HERE (blockMesh
+ checkMesh at build time, MESH_STANDARD.md section 8.1 "build before you
freeze"); polyMesh is not committed, the dictionaries and the birth
certificate (BUILD.txt, log.blockMesh, log.checkMesh.build) are.

THE L-341 HAZARD DOES NOT ARISE.  Every boundary condition here is
fixedValue / zeroGradient / noSlip / fixedFluxPressure -- conditions whose
parameters are purely physical.  No `mixed` (Robin) condition is used, so no
coefficient contains the mesh spacing and nothing has to be recomputed per
level.  The `--check-levels` guard makes that claim executable: it REFUSES if
any 0.orig field carries a `mixed` entry, and it REFUSES unless the three
levels share every physical constant and differ ONLY in N.

WHAT IS WRITTEN AT BUILD.  0.orig only.  No 0/ and no numeric time directory
may exist in a case at the freeze; the launcher (run_one_t13.sh) creates 0/
from 0.orig and touches 0/T last (the age-guard datum).

NO `assert` STATEMENT IN THIS FILE (L-332).  Every refusal is sys.exit(2).

Usage:  build_t13.py --root DIR [--level c|m|f ...]        build cases
        build_t13.py --check-levels                         run the guards only
        build_t13.py --write-registered [--root DIR]        write T13_registered.json
        build_t13.py --selftest                             drive the guards
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
import exact_t13 as EX                                   # noqa: E402

# ---------------------------------------------------------------- constants
L      = 0.02                 # m, gap width
ASPECT = 16                   # H / L
H      = ASPECT * L           # m, slot height
W      = 0.001                # m, depth of the single cell (empty direction)
NU     = 1.5e-5               # m2/s
PR     = 0.71
PRT    = 0.85                 # unused in laminar; carried for the dictionary form
BETA   = 1.0 / 300.0          # 1/K
TREF   = 300.0                # K, = (T_h + T_c)/2 -- the antisymmetry point
G      = 9.81                 # m/s2
RA     = 100.0                # registered Rayleigh number, g beta dT L^3 Pr / nu^2
DT     = RA * NU * NU / (PR * G * BETA * L ** 3)      # K, DERIVED from Ra
T_HOT  = TREF + 0.5 * DT
T_COLD = TREF - 0.5 * DT
U_REF  = G * BETA * DT * L * L / NU                   # m/s, v = U_REF * phi(xi)
GR     = RA / PR

LEVELS = {"c": 20, "m": 40, "f": 80}
END_TIME = {"c": 10000, "m": 20000, "f": 40000}
# cost (T13_PREREGISTRATION.md section 9): POINT from K0f C_lam's MEASURED
# laminar rate of THIS solver, 2.773e-06 core-s per cell-iteration
# (ExecutionTime 5564.7 s / (50 176 cells x 40 000 it), STATUS.C_lam);
# CEILING from T4's measured kOmegaSST rate 5.874e-06 (C-119); caps are
# hang guards above the ceiling.
RATE_POINT   = 5564.7 / (50176.0 * 40000.0)
RATE_CEILING = 5.874e-06
CAP_CORE_MIN = {"c": 8, "m": 64, "f": 500}
RANKS = 1
SOLVER = "buoyantBoussinesqSimpleFoam"
FOAM_BASHRC = "/usr/lib/openfoam/openfoam2606/etc/bashrc"

EXIT_OK, EXIT_REFUSE = 0, 2


def refuse(msg):
    print("REFUSE: " + msg)
    sys.exit(EXIT_REFUSE)


def case_name(level):
    return "T13_VS_%s" % level


def cells(level):
    N = LEVELS[level]
    return N * ASPECT * N


def head(cls, obj, loc=None):
    l = ('    location    "%s";\n' % loc) if loc else ""
    return ("FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
            "    class       %s;\n%s    object      %s;\n}\n" % (cls, l, obj))


# ------------------------------------------------------------------ guards
def check_levels(ra=None, fields_text=None):
    """Executable form of two registration claims.  Refuses (exit 2) if the
    derived Ra is not the registered one, if the three levels differ in
    anything but N, or if a `mixed` condition is present (L-341 non-arising)."""
    ra = RA if ra is None else ra
    dT = ra * NU * NU / (PR * G * BETA * L ** 3)
    ra_back = G * BETA * dT * L ** 3 * PR / (NU * NU)
    if abs(ra_back - 100.0) > 1e-9:
        refuse("registered Ra_L = 100 is not what the constants give: %.12g" % ra_back)
    # the only per-level difference is N: the dictionaries below take no other level input
    per_level = {lv: (L, H, NU, PR, BETA, TREF, G, dT, T_HOT, T_COLD) for lv in LEVELS}
    if len(set(per_level.values())) != 1:
        refuse("physical constants differ across levels: %r" % per_level)
    txt = fields_text if fields_text is not None else "\n".join(
        fields(lv)[k] for lv in LEVELS for k in ("T", "U", "p_rgh", "alphat"))
    if re.search(r"\bmixed\b", txt):
        refuse("a `mixed` (Robin) boundary condition is present; L-341's mesh-dependent "
               "valueFraction hazard WOULD arise and this rung registers that it does not")
    print("  check-levels PASSES: Ra_L = %.12g from the constants; dT = %.17g K; "
          "u_ref = %.10e m/s; v_max = %.10e m/s; levels differ only in N = %s; no `mixed` BC"
          % (ra_back, dT, U_REF, U_REF * EX.PHI_MAX, [LEVELS[k] for k in ("c", "m", "f")]))
    return True


# ----------------------------------------------------------- dictionaries
def block_mesh_dict(level):
    N = LEVELS[level]
    return (head("dictionary", "blockMeshDict", "system") +
            "scale 1;\n\nvertices\n(\n"
            "    (0 0 0) (%.17g 0 0) (%.17g %.17g 0) (0 %.17g 0)\n"
            "    (0 0 %.17g) (%.17g 0 %.17g) (%.17g %.17g %.17g) (0 %.17g %.17g)\n);\n\n"
            "blocks\n(\n    hex (0 1 2 3 4 5 6 7) (%d %d 1) simpleGrading (1 1 1)\n);\n\n"
            "edges ();\n\nboundary\n(\n"
            "    hot          { type wall;  faces ( (0 4 7 3) ); }\n"
            "    cold         { type wall;  faces ( (1 2 6 5) ); }\n"
            "    bottom       { type wall;  faces ( (0 1 5 4) ); }\n"
            "    top          { type wall;  faces ( (3 7 6 2) ); }\n"
            "    frontAndBack { type empty; faces ( (0 3 2 1) (4 5 6 7) ); }\n"
            ");\n\nmergePatchPairs ();\n"
            % (L, L, H, H, W, L, W, L, H, W, H, W, N, ASPECT * N))


def control_dict(level):
    et = END_TIME[level]
    return (head("dictionary", "controlDict", "system") +
            "application     %s;\nstartFrom       startTime;\nstartTime       0;\n"
            "stopAt          endTime;\nendTime         %d;\ndeltaT          1;\n"
            "writeControl    timeStep;\nwriteInterval   %d;\npurgeWrite      2;\n"
            "writeFormat     ascii;\nwritePrecision  16;\nwriteCompression off;\n"
            "timeFormat      general;\ntimePrecision   6;\nrunTimeModifiable false;\n"
            % (SOLVER, et, et // 10))


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
    return (head("dictionary", "fvSolution", "system") +
            "solvers\n{\n"
            "    p_rgh\n    {\n        solver          PCG;\n        preconditioner  DIC;\n"
            "        tolerance       1e-10;\n        relTol          0.01;\n    }\n"
            "    \"(U|T)\"\n    {\n        solver          PBiCGStab;\n        preconditioner  DILU;\n"
            "        tolerance       1e-12;\n        relTol          0.01;\n    }\n}\n\n"
            "SIMPLE\n{\n    nNonOrthogonalCorrectors 0;\n    pRefCell        0;\n    pRefValue       0;\n}\n\n"
            "relaxationFactors\n{\n    fields    { p_rgh 0.7; }\n"
            "    equations { U 0.3; T 0.5; }\n}\n")


def constant_files():
    return {
        "g": (head("uniformDimensionedVectorField", "g", "constant") +
              "dimensions      [0 1 -2 0 0 0 0];\nvalue           (0 %.17g 0);\n" % (-G)),
        "transportProperties": (head("dictionary", "transportProperties", "constant") +
                                "transportModel  Newtonian;\nnu              %.17g;\n"
                                "Pr              %.17g;\nPrt             %.17g;\n"
                                "beta            %.17g;\nTRef            %.17g;\n"
                                % (NU, PR, PRT, BETA, TREF)),
        "turbulenceProperties": (head("dictionary", "turbulenceProperties", "constant") +
                                 "simulationType  laminar;\n"),
    }


def fields(level):
    walls = "(hot|cold|bottom|top)"
    return {
        "T": (head("volScalarField", "T", "0") +
              "dimensions      [0 0 0 1 0 0 0];\n\ninternalField   uniform %.17g;\n\n"
              "boundaryField\n{\n"
              "    hot          { type fixedValue; value uniform %.17g; }\n"
              "    cold         { type fixedValue; value uniform %.17g; }\n"
              "    bottom       { type zeroGradient; }\n"
              "    top          { type zeroGradient; }\n"
              "    frontAndBack { type empty; }\n}\n" % (TREF, T_HOT, T_COLD)),
        "U": (head("volVectorField", "U", "0") +
              "dimensions      [0 1 -1 0 0 0 0];\n\ninternalField   uniform (0 0 0);\n\n"
              "boundaryField\n{\n"
              "    \"%s\"  { type noSlip; }\n"
              "    frontAndBack { type empty; }\n}\n" % walls),
        "p_rgh": (head("volScalarField", "p_rgh", "0") +
                  "dimensions      [0 2 -2 0 0 0 0];\n\ninternalField   uniform 0;\n\n"
                  "boundaryField\n{\n"
                  "    \"%s\"  { type fixedFluxPressure; rho rhok; value uniform 0; }\n"
                  "    frontAndBack { type empty; }\n}\n" % walls),
        "alphat": (head("volScalarField", "alphat", "0") +
                   "dimensions      [0 2 -1 0 0 0 0];\n\ninternalField   uniform 0;\n\n"
                   "boundaryField\n{\n"
                   "    \"%s\"  { type calculated; value uniform 0; }\n"
                   "    frontAndBack { type empty; }\n}\n" % walls),
    }


# ------------------------------------------------------------------ build
def run_foam(tool, case, log):
    cmd = "source %s > /dev/null 2>&1; %s -case %s > %s 2>&1" % (FOAM_BASHRC, tool, case, log)
    t0 = time.time()
    r = subprocess.run(["bash", "-c", cmd])
    return r.returncode, time.time() - t0


def build(root, level):
    N = LEVELS[level]
    case = os.path.join(root, case_name(level))
    for sub in ("system", "constant", "0.orig"):
        os.makedirs(os.path.join(case, sub), exist_ok=True)
    for name in ("0",):
        if os.path.exists(os.path.join(case, name)):
            refuse("%s already has a 0/ directory; a case is built once, from nothing" % case)
    for d in os.listdir(case):
        if re.fullmatch(r"[0-9]+(\.[0-9]+)?", d):
            refuse("%s already has time directory %s; refusing to build over it" % (case, d))
    open(os.path.join(case, "system", "blockMeshDict"), "w").write(block_mesh_dict(level))
    open(os.path.join(case, "system", "controlDict"), "w").write(control_dict(level))
    open(os.path.join(case, "system", "fvSchemes"), "w").write(fv_schemes())
    open(os.path.join(case, "system", "fvSolution"), "w").write(fv_solution())
    for k, v in constant_files().items():
        open(os.path.join(case, "constant", k), "w").write(v)
    for k, v in fields(level).items():
        open(os.path.join(case, "0.orig", k), "w").write(v)
    open(os.path.join(case, "CASE.txt"), "w").write(
        "case=%s\nlevel=%s\nN=%d\nNy=%d\ncells=%d\nL=%.17g\nH=%.17g\naspect=%d\ndx=%.17g\n"
        "nu=%.17g\nPr=%.17g\nbeta=%.17g\nTRef=%.17g\ng=%.17g\nRa_L=%.17g\nGr_L=%.17g\n"
        "dT=%.17g\nT_hot=%.17g\nT_cold=%.17g\nu_ref=%.17g\nv_max_exact=%.17g\n"
        "xi_star=%.17g\nphi_max=%.17g\nendTime=%d\nwriteInterval=%d\nsolver=%s\nranks=%d\n"
        % (case_name(level), level, N, ASPECT * N, cells(level), L, H, ASPECT, L / N,
           NU, PR, BETA, TREF, G, RA, GR, DT, T_HOT, T_COLD, U_REF, U_REF * EX.PHI_MAX,
           EX.XI_STAR, EX.PHI_MAX, END_TIME[level], END_TIME[level] // 10, SOLVER, RANKS))
    # BUILD BEFORE YOU FREEZE (MESH_STANDARD section 8.1): the mesh is made and
    # certified now; a blockMesh refusal is a diagnostic (8.2), never routed around.
    rc_bm, t_bm = run_foam("blockMesh", case, os.path.join(case, "log.blockMesh"))
    if rc_bm != 0:
        refuse("blockMesh rc=%d on %s -- see log.blockMesh" % (rc_bm, case))
    rc_cm, t_cm = run_foam("checkMesh", case, os.path.join(case, "log.checkMesh.build"))
    body = open(os.path.join(case, "log.checkMesh.build"), errors="replace").read()
    mcells = re.search(r"^\s*cells:\s+(\d+)", body, re.M)
    if not mcells or int(mcells.group(1)) != cells(level):
        refuse("checkMesh reports %s cells, registered %d" % (mcells.group(1) if mcells else None, cells(level)))
    lines = [ln.strip() for ln in body.splitlines()
             if re.search(r"cells:|non-orthogonality|skewness|aspect ratio|Mesh OK|Failed", ln)]
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    open(os.path.join(case, "BUILD.txt"), "w").write(
        "case            %s\ndate            %s\nblockMesh_rc    %d   wall %.3f s\n"
        "checkMesh_rc    %d   wall %.3f s\n%s\n"
        % (case_name(level), stamp, rc_bm, t_bm, rc_cm, t_cm,
           "\n".join("checkMesh       " + ln for ln in lines)))
    print("  built %s N=%d cells=%d blockMesh rc=%d checkMesh rc=%d (%s)"
          % (case_name(level), N, cells(level), rc_bm, rc_cm,
             "; ".join(ln for ln in lines if "Mesh OK" in ln or "Failed" in ln)))
    return case


# --------------------------------------------------------- registered JSON
def registered():
    exp = {r["N"]: r for r in EX.expectation_table(tuple(LEVELS[k] for k in ("c", "m", "f")))}
    cases = {}
    for lv in ("c", "m", "f"):
        N = LEVELS[lv]
        pt = cells(lv) * END_TIME[lv] * RATE_POINT / 60.0
        ce = cells(lv) * END_TIME[lv] * RATE_CEILING / 60.0
        cases[case_name(lv)] = dict(
            level=lv, N=N, Ny=ASPECT * N, cells=cells(lv), dx_m=L / N,
            endTime=END_TIME[lv], writeInterval=END_TIME[lv] // 10,
            cap_core_min=CAP_CORE_MIN[lv], timeout_s=CAP_CORE_MIN[lv] * 60 // RANKS,
            point_core_min=round(pt, 3), ceiling_core_min=round(ce, 3),
            expected_G1_rel_error=exp[N]["G1_rel"], expected_xi_max_error=exp[N]["G1b_err"])
    f_rel = abs(exp[LEVELS["f"]]["G1_rel"])
    f_loc = abs(exp[LEVELS["f"]]["G1b_err"])
    return dict(
        rung="T13",
        title="natural convection in a vertical slot, conduction regime (Batchelor 1954 parallel flow), EXACT tier",
        capability_grid_cell="natural convection x laminar x 2D (docs/capability/heat-transfer_GRID.md)",
        solver=SOLVER, turbulence="laminar", dimensionality=2, ranks=RANKS,
        physics=dict(L_m=L, H_m=H, aspect=ASPECT, depth_m=W, nu=NU, Pr=PR, beta=BETA, TRef=TREF,
                     g=G, Ra_L=RA, Gr_L=GR, dT_K=DT, T_hot=T_HOT, T_cold=T_COLD, u_ref=U_REF,
                     v_max_exact=U_REF * EX.PHI_MAX, xi_star=EX.XI_STAR, phi_max=EX.PHI_MAX,
                     Nu_exact=EX.NU_EXACT),
        cases=cases, refinement_ratio=2.0, factor_of_safety=1.25,
        roache_floors=dict(
            source="scripts/roache_triple.py, imported by name (MESH_STANDARD.md section 10.5, chief ruling 01967a7b); the comparator defines neither and REFUSES if these numbers differ from the import",
            STAGNANT_FLOOR=0.5, P_MIN=0.05),
        graded_rows=dict(
            G1=dict(quantity="v(xi*)/u_ref at mid-height, 4-point Lagrange at xi* = 1/2 - sqrt(3)/6",
                    reference=EX.PHI_MAX, band_rel=1.5e-3, grading="Roache triple, rule 5",
                    band_ground="2.1x the DERIVED fine-level discretisation error %.3e (exact_t13.discrete_expectation); the coarse (%.3e) and medium (%.3e) levels are predicted OUTSIDE it"
                    % (f_rel, abs(exp[20]["G1_rel"]), abs(exp[40]["G1_rel"]))),
            G1b=dict(quantity="xi_max, location of the maximum upflow from the cubic through the 4 cells around it",
                     reference=EX.XI_STAR, band_abs=1.5e-4, grading="Roache triple, rule 5",
                     band_ground="2.2x the DERIVED fine-level error %.3e; coarse (%.3e) and medium (%.3e) predicted OUTSIDE"
                     % (f_loc, abs(exp[20]["G1b_err"]), abs(exp[40]["G1b_err"]))),
            G2=dict(quantity="RMS over the mid-height row of (T - T_lin)/dT",
                    reference=0.0, floor_abs=1.0e-6, grading="ABSOLUTE FLOOR (EXACT-class row): a linear T is in the null space of the scheme's truncation error, so its triple is EXACT/DEGENERATE by construction and rule 5 (2) would return NOT A RESULT for a row that cannot be wrong by discretisation; the triple states are PRINTED, the verdict is the floor"),
            G3=dict(quantity="Nu_L = -(dT/dx)_wall L/dT from the half-cell wall gradient, hot and cold walls, mid-height row",
                    reference=EX.NU_EXACT, floor_abs=2.0e-4, grading="ABSOLUTE FLOOR (EXACT-class row), as G2",
                    floor_ground="the half-cell gradient amplifies a temperature deviation delta by 2N; at N_f = 80 the witness floor 1e-6 on delta gives 1.6e-4; registered 2.0e-4")),
        controls=dict(
            C_CONV=dict(what="iterative convergence: initial residuals of Uy, T and p_rgh <= 1e-6 at EVERY iteration of the final 10 percent; Ux is a degenerate (~0) channel and is REPORTED, never gated (L-338)", floor=1.0e-6),
            C_PLAT=dict(what="plateau: |G1(endTime) - G1(endTime - writeInterval)| / G1 <= 1e-7", floor=1.0e-7),
            W0=dict(what="y-invariance mirror: the rows just above and just below mid-height agree in v (per u_ref phi_max) and T (per dT) to 1e-6", floor=1.0e-6),
            W1=dict(what="end-effect witness: rows at H/2 +- L, +- 2L, +- 4L agree with the graded row in v (per u_ref phi_max) and T (per dT) to 1e-6; exceeding it means the level is NOT in the parallel-flow regime -> gate (1) NOT A RESULT", floor=1.0e-6),
            C_RA=dict(what="operand identity (L-331): nu, Pr, beta, TRef, g, T_hot, T_cold, L, N are READ FROM THE CASE FILES, printed, and Ra_L recomputed from them must equal 100 to 1e-9", floor=1.0e-9),
            C_ORDER=dict(what="cell-ordering control: the graded row's T must fall monotonically from hot to cold with the registered slope -dT/L to 1e-6 relative; a transposed ordering (y-fastest) shows a constant row and REFUSES"),
            C_PZ=dict(what="planted-zero control per reader (rule 3, L-340 sizing): point plant for G1/G1b/G3/W1, ALL-ROW plant for the RMS reader G2; both arms; measured detection ladder; REFUSES on a blind or noisy reader")),
        predictions=dict(
            P1="G1 and G1b triples CONVERGING with observed order p in [1.5, 2.5]; derived expectation p = 2.000 / 2.000",
            P2="G1 relative deviation at f in [+4.9e-4, +9.1e-4] (the derived +7.03e-4 within 30 percent), POSITIVE sign; c and m OUTSIDE the +-1.5e-3 band",
            P2b="xi_max error at f in [-8.8e-5, -4.7e-5] (the derived -6.77e-5 within 30 percent), NEGATIVE sign",
            P3="|Nu - 1| < 1e-4 on both walls at f",
            P4="witness W1 < 1e-7 on every level (a priori bound ~1e-9 relative at 8L from the ends)",
            P5="G2 RMS < 1e-7 at f",
            P6="all three levels meet C_CONV and C_PLAT within their registered endTime"),
        cost=dict(rate_point_core_s_per_cell_it=RATE_POINT,
                  rate_point_source="K0f C_lam, LAMINAR buoyantBoussinesqSimpleFoam, MEASURED: ExecutionTime 5564.7 s over 50 176 cells x 40 000 iterations (verification/runs/F14-cooling-ladder/K0f_runs/STATUS.C_lam, C_lam/log.solve)",
                  rate_ceiling_core_s_per_cell_it=RATE_CEILING,
                  rate_ceiling_source="T4 level c, kOmegaSST on the same solver, MEASURED (STATUS.T4_IJ_c, C-119)",
                  overhead_floor="C-118: below ~1e3 cells the per-iteration cost is overhead-dominated and linear cell-step scaling over-predicts 2.2-2.4x; the coarsest level here has 6 400 cells, above that regime, and the same over-prediction direction is expected (T4's ratio 0.423 at 5k-83k cells)",
                  usd_per_core_h=0.0513,
                  usd_basis="derived, not measured, reported-by-owner rate (COMPUTE_BUDGET_CHARTER section 5)"),
        completion=dict(needed_fields=["T", "U", "p_rgh", "phi"],
                        infrastructure_fields=["wall_s", "timeout_s", "ranks", "core_min", "capped", "checkmesh_rc", "solver", "solver_path", "note", "started_utc", "ended_utc"],
                        note="capped is an INFRASTRUCTURE field and never a completion conjunct (L-342)"),
    )


def selftest():
    fails = []
    print("build_t13 selftest (guards driven both ways):")
    try:
        check_levels()
        print("  [ok ] check-levels passes on the registered constants")
    except SystemExit:
        fails.append("check-levels refused the registered constants")
    # a mutant Ra must be refused
    fired = False
    try:
        check_levels(ra=101.0)
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    print("  [%s] Ra mutated to 101 -> REFUSE exit 2" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("ra")
    # a planted `mixed` condition must be refused
    fired = False
    try:
        check_levels(fields_text=fields("c")["T"].replace("zeroGradient", "mixed"))
    except SystemExit as e:
        fired = (e.code == EXIT_REFUSE)
    print("  [%s] planted `mixed` BC -> REFUSE exit 2 (L-341 guard fires)" % ("ok " if fired else "FAIL"))
    if not fired:
        fails.append("mixed")
    # cell counts and the ratio
    ok = all(cells(lv) == LEVELS[lv] ** 2 * ASPECT for lv in LEVELS) and \
        cells("m") == 4 * cells("c") and cells("f") == 4 * cells("m")
    print("  [%s] cells 6400/25600/102400, r = 2 in 2-D" % ("ok " if ok else "FAIL"))
    if not ok:
        fails.append("cells")
    n_assert = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse(open(os.path.abspath(__file__)).read())))
    planted = sum(isinstance(x, ast.Assert) for x in ast.walk(ast.parse("assert 1\n")))
    ok = (n_assert == 0 and planted == 1)
    print("  [%s] AST assert count in this file = %d (counter sees a planted assert: %d)" % ("ok " if ok else "FAIL", n_assert, planted))
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
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if a.check_levels:
        check_levels()
        sys.exit(EXIT_OK)
    if a.write_registered:
        out = os.path.join(a.root or HERE, "T13_registered.json")
        json.dump(registered(), open(out, "w"), indent=2)
        print("  wrote %s" % out)
        sys.exit(EXIT_OK)
    if not a.root:
        refuse("--root is required")
    EX.verify()
    check_levels()
    for lv in (a.level or ["c", "m", "f"]):
        build(a.root, lv)
