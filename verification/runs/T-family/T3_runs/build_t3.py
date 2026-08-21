#!/usr/bin/env python3
"""
T3 builder: heated backward-facing step at Vogel and Eaton (1985) conditions.

Everything numeric here is taken from T3_CONTRACT.md in this directory; the
contract is binding and this file is its executable form.  Prose lives in
docs/campaigns/T-family/T3_PREREGISTRATION.md.

Usage:  python3 build_t3.py [--out DIR] [--force] [--wm-counts NY_LOW NY_UP]

  --out DIR    write the eight case directories under DIR (default: this run
               tree).  The directory is created if absent.
  --force      rebuild a case directory that already exists, but ONLY if it
               holds no numeric time directory and no LAUNCH_LOCK (a case that
               has been launched is never deleted by this script).
  --wm-counts  override the W_m wall-function counts (ny_low ny_up).  The
               contract's counts are infeasible for the contract's first cell
               (see WM_NY_LOW below); this flag exists so the orchestrator can
               build W_m after the contract has been amended, and the departure
               is written into CASE.txt as wm_counts_override.

DECISIONS THAT ARE DECISIONS, NOT DEFAULTS (all from the contract):

  * THE MESH IS THREE BLOCKS with the finest x cell TOUCHING THE STEP from both
    sides and the finest y cells touching every wall.  The upstream block B1
    runs in x from the inlet to the step, so blockMesh's last/first ratio
    along that block must be BELOW one to put the fine cell at the step
    (L-142: attempt 1 of T1b put its wall cell on the centreline this way).
    Every reciprocal is computed here and written as a number; blockMesh does
    no arithmetic.

  * B1 AND B3 SHARE THE IDENTICAL y DISTRIBUTION and B2 and B3 the identical x
    distribution, so the block interfaces are conformal and the step corner
    is a single shared vertex.

  * GRADING RATIOS ARE FOUND BY BISECTION so that N geometric cells of the
    designed first cell exactly fill the half or the block.  The builder never
    takes a ratio on trust; check_t3_mesh.py reads the written points back.

  * writeInterval STRICTLY LESS THAN endTime (L-140); no residualControl
    (L-141: convergence is judged from written fields by the comparator).

  * W_m: the contract's counts (ny_low 40, ny_up 96) cannot be filled by a
    2.1025e-3 m first cell with a cell-to-cell ratio >= 1 -- see
    wm_feasibility() -- so the builder REFUSES W_m with the arithmetic instead
    of grading it the wrong way.  Nothing else is affected.
"""
import argparse
import math
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- physics and numbers (contract table) --------------------------------
H = 0.038                 # m, step height (scale choice, not a primary number)
NU = 1.5e-5               # m2/s
PR = 0.71
PRT_DEFAULT = 0.85
RE_TARGET = 28000.0
U_IN = 10.35              # m/s, uniform inlet
U_REF = 11.0526           # m/s, predicted core velocity at x = -3.3H (used ONLY
                          # to size the wall cell; the comparator MEASURES it)
CF_EST = 0.003
T_IN = 300.0              # K
DTDN = 1.0e4              # K/m on the heated wall, positive = heating
END_TIME = 20000
WRITE_INTERVAL = 2000     # STRICTLY < END_TIME (L-140)
PURGE_WRITE = 2
Z_EXTENT = 0.1 * H        # one cell, empty
X_STEP_CELL = 0.03 * H    # finest x cell touching the step, both sides
CORE_SEC_PER_CELL_ITER = 1.0 / 4.0e5   # predicted_core_s = nCells*endTime/4e5

# cell counts per level: nx_up (B1), nx_down (B2,B3), ny_low (B2), ny_up (B1,B3)
LEVELS = {
    "c": dict(nx_up=100, nx_down=200, ny_low=60,  ny_up=80,  yplus=1.6),
    "m": dict(nx_up=160, nx_down=320, ny_low=96,  ny_up=128, yplus=1.0),
    "f": dict(nx_up=256, nx_down=512, ny_low=154, ny_up=204, yplus=0.625),
}
# contract's quoted first cells, used as a cross-check of the formula below
CONTRACT_FIRST_CELL = {"c": 1.1213e-4, "m": 7.0083e-5, "f": 4.3802e-5}
WM_FIRST_CELL_CONTRACT = 2.1025e-3
WM_YPLUS = 30.0
# Contract counts for W_m.  INFEASIBLE with the contract's 2.1025e-3 m wall
# cell (0.0553 H): 20 cells per half of 0.5H need >= 0.04205 m (half is 0.019)
# and 48 cells per half of 2H need >= 0.1009 m (half is 0.076).  With a
# cell-to-cell ratio >= 1, at most 9 cells fit per lower half (ny_low <= 18)
# and 36 per upper half (ny_up <= 72).  Feasible pairs and their ratios:
#   ny_low  8: r 1.581   12: 1.163   14: 1.084   16: 1.035   18: 1.001
#   ny_up  32: r 1.101   40: 1.058   48: 1.034   56: 1.018   64: 1.008   72: 1.0002
# The builder refuses W_m at the contract counts and prints this arithmetic;
# --wm-counts builds it once the contract has been amended.
WM_NY_LOW, WM_NY_UP = 16, 48   # AMENDED 2026-08-21 before any case existed (contract case table); 40/96 was infeasible
DM_NX_UP = 60                     # D_m, 10H upstream
OM_NX_DOWN = 480                  # O_m, 45H downstream

# case -> (level, arm, L_up/H, L_down/H, Prt, wall treatment, laminar)
CASES = [
    ("R_c",     "c", "ladder",               48.0, 30.0, PRT_DEFAULT, "resolved",       False),
    ("R_m",     "m", "ladder",               48.0, 30.0, PRT_DEFAULT, "resolved",       False),
    ("R_f",     "f", "ladder",               48.0, 30.0, PRT_DEFAULT, "resolved",       False),
    ("P_m",     "m", "Prt discrimination",   48.0, 30.0, 1.0,         "resolved",       False),
    ("C_lam_m", "m", "Charter 2c trivial baseline, laminar", 48.0, 30.0, PRT_DEFAULT, "none", True),
    ("W_m",     "m", "wall functions",       48.0, 30.0, PRT_DEFAULT, "wall functions", False),
    ("D_m",     "m", "thin inlet boundary layer", 10.0, 30.0, PRT_DEFAULT, "resolved",  False),
    ("O_m",     "m", "outlet independence",  48.0, 45.0, PRT_DEFAULT, "resolved",       False),
]


def u_tau():
    return U_REF * math.sqrt(CF_EST / 2.0)


def first_cell_wall(yplus):
    """Cell HEIGHT whose centre sits at the requested y+ (2*y+*nu/u_tau)."""
    return 2.0 * yplus * NU / u_tau()


def cell_ratio(first, N, L):
    """Cell-to-cell ratio r in [1+1e-9, 2] such that N geometric cells of size
    first, first*r, ..., first*r^(N-1) exactly fill L.  Bisection, 300 steps.
    Refuses (None) when even a uniform fill would overshoot: first*N >= L."""
    if first * N >= L:
        return None
    lo, hi = 1.0 + 1e-9, 2.0
    for _ in range(300):
        m = 0.5 * (lo + hi)
        s = first * ((m ** N - 1.0) / (m - 1.0))
        if s < L:
            lo = m
        else:
            hi = m
    return 0.5 * (lo + hi)


def geometric_sum(first, r, N):
    return first * ((r ** N - 1.0) / (r - 1.0))


def header(cls, obj, loc):
    return (f"FoamFile\n{{\n    version     2.0;\n    format      ascii;\n"
            f"    class       {cls};\n    location    \"{loc}\";\n"
            f"    object      {obj};\n}}\n")


def block_mesh(L_up, L_down, nx_up, nx_down, ny_low, ny_up,
               R_x_up, R_x_down, R_y_low, R_y_up):
    """
    Three blocks.  Vertices (z = 0 then z = Z_EXTENT):
      0 (-L_up, H)  1 (0, H)  2 (0, 5H)  3 (-L_up, 5H)
      4 (0, 0)      5 (L_down, 0)  6 (L_down, H)  7 (L_down, 5H)
    B1 = hex(0 1 2 3)  upstream,   x: -L_up -> 0 (fine cell at the END, so the
                                    written x ratio is 1/R_x_up, BELOW one)
    B2 = hex(4 5 6 1)  lower down, x: 0 -> L_down (fine cell FIRST, ratio R_x_down)
    B3 = hex(1 6 7 2)  upper down, same x as B2, same y as B1.
    y in every block is two-sided: (0.5 0.5 R) then (0.5 0.5 1/R), R = last/first
    of a geometric half starting at the wall cell.  All reciprocals are numbers.
    """
    z = Z_EXTENT
    fiveH = 5.0 * H
    v = [(-L_up, H), (0.0, H), (0.0, fiveH), (-L_up, fiveH),
         (0.0, 0.0), (L_down, 0.0), (L_down, H), (L_down, fiveH)]
    verts = "".join(f"    ({x:.10f} {y:.10f} {0.0:.10f})\n" for x, y in v)
    verts += "".join(f"    ({x:.10f} {y:.10f} {z:.10f})\n" for x, y in v)
    yg_up = f"( (0.5 0.5 {R_y_up:.12g}) (0.5 0.5 {1.0/R_y_up:.12g}) )"
    yg_low = f"( (0.5 0.5 {R_y_low:.12g}) (0.5 0.5 {1.0/R_y_low:.12g}) )"
    xg_up = f"{1.0/R_x_up:.12g}"          # the reciprocal, BY HAND (L-142)
    xg_down = f"{R_x_down:.12g}"
    return header("dictionary", "blockMeshDict", "system") + f"""
scale 1;
vertices
(
{verts});
blocks
(
    // B1 upstream: x from inlet to step, fine x cell touches x = 0 (ratio < 1)
    hex (0 1 2 3 8 9 10 11) ({nx_up} {ny_up} 1)
    simpleGrading ( {xg_up} {yg_up} 1 )
    // B2 lower downstream: y from heated wall (0) to step top (H)
    hex (4 5 6 1 12 13 14 9) ({nx_down} {ny_low} 1)
    simpleGrading ( {xg_down} {yg_low} 1 )
    // B3 upper downstream: y from H to 5H, identical y grading to B1
    hex (1 6 7 2 9 14 15 10) ({nx_down} {ny_up} 1)
    simpleGrading ( {xg_down} {yg_up} 1 )
);
edges ();
boundary
(
    inlet        {{ type patch; faces ( (0 3 11 8) ); }}
    outlet       {{ type patch; faces ( (5 6 14 13) (6 7 15 14) ); }}
    upstreamWall {{ type wall;  faces ( (0 1 9 8) ); }}
    stepWall     {{ type wall;  faces ( (4 1 9 12) ); }}
    heatedWall   {{ type wall;  faces ( (4 5 13 12) ); }}
    topWall      {{ type wall;  faces ( (3 2 10 11) (2 7 15 10) ); }}
    frontAndBack {{ type empty;
                   faces ( (0 1 2 3) (8 9 10 11)
                           (4 5 6 1) (12 13 14 9)
                           (1 6 7 2) (9 14 15 10) ); }}
);
mergePatchPairs ();
"""


WALLS = ("upstreamWall", "stepWall", "heatedWall", "topWall")


def walls(entry):
    return "".join(f"    {w:13s}{entry}\n" for w in WALLS)


def tail():
    return "    frontAndBack { type empty; }\n}\n"


def f_U():
    return header("volVectorField", "U", "0") + f"""
dimensions      [0 1 -1 0 0 0 0];
internalField   uniform ({U_IN:.10g} 0 0);
boundaryField
{{
    inlet        {{ type fixedValue; value uniform ({U_IN:.10g} 0 0); }}
    outlet       {{ type inletOutlet; inletValue uniform (0 0 0); value $internalField; }}
""" + walls("{ type noSlip; }") + tail()


def f_p():
    return header("volScalarField", "p_rgh", "0") + """
dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0;
boundaryField
{
    inlet        { type zeroGradient; }
    outlet       { type fixedValue; value uniform 0; }
""" + walls("{ type zeroGradient; }") + tail()


def f_T():
    body = header("volScalarField", "T", "0") + f"""
dimensions      [0 0 0 1 0 0 0];
internalField   uniform {T_IN:.10g};
boundaryField
{{
    inlet        {{ type fixedValue; value uniform {T_IN:.10g}; }}
    outlet       {{ type inletOutlet; inletValue uniform {T_IN:.10g}; value $internalField; }}
    upstreamWall {{ type zeroGradient; }}
    stepWall     {{ type zeroGradient; }}
    heatedWall   {{ type fixedGradient; gradient uniform {DTDN:.10g}; }}
    topWall      {{ type zeroGradient; }}
"""
    return body + tail()


def k_in():
    return 1.5 * (0.02 * U_IN) ** 2


def omega_in():
    return math.sqrt(k_in()) / (0.09 ** 0.25 * 0.07 * 4.0 * H)


def f_k(wallfunc):
    wb = ("{ type kqRWallFunction; value $internalField; }" if wallfunc
          else "{ type kLowReWallFunction; value $internalField; }")
    return header("volScalarField", "k", "0") + f"""
dimensions      [0 2 -2 0 0 0 0];
internalField   uniform {k_in():.8g};
boundaryField
{{
    inlet        {{ type fixedValue; value uniform {k_in():.8g}; }}
    outlet       {{ type inletOutlet; inletValue $internalField; value $internalField; }}
""" + walls(wb) + tail()


def f_omega():
    return header("volScalarField", "omega", "0") + f"""
dimensions      [0 0 -1 0 0 0 0];
internalField   uniform {omega_in():.8g};
boundaryField
{{
    inlet        {{ type fixedValue; value uniform {omega_in():.8g}; }}
    outlet       {{ type inletOutlet; inletValue $internalField; value $internalField; }}
""" + walls("{ type omegaWallFunction; value $internalField; }") + tail()


def f_nut(wallfunc):
    wb = ("{ type nutkWallFunction; value uniform 0; }" if wallfunc
          else "{ type nutLowReWallFunction; value uniform 0; }")
    return header("volScalarField", "nut", "0") + """
dimensions      [0 2 -1 0 0 0 0];
internalField   uniform 0;
boundaryField
{
    inlet        { type calculated; value uniform 0; }
    outlet       { type calculated; value uniform 0; }
""" + walls(wb) + tail()


def f_alphat(wallfunc, prt):
    wb = (f"{{ type alphatJayatillekeWallFunction; Prt {prt:.10g}; value uniform 0; }}"
          if wallfunc else "{ type calculated; value uniform 0; }")
    return header("volScalarField", "alphat", "0") + """
dimensions      [0 2 -1 0 0 0 0];
internalField   uniform 0;
boundaryField
{
    inlet        { type calculated; value uniform 0; }
    outlet       { type calculated; value uniform 0; }
""" + walls(wb) + tail()


def transport(prt):
    return header("dictionary", "transportProperties", "constant") + f"""
transportModel  Newtonian;
nu              {NU:.10g};
beta            0;
TRef            {T_IN:.10g};
Pr              {PR:.10g};
Prt             {prt:.10g};
"""


def turbulence(laminar):
    if laminar:
        return header("dictionary", "turbulenceProperties", "constant") + """
simulationType  laminar;
"""
    return header("dictionary", "turbulenceProperties", "constant") + """
simulationType  RAS;
RAS
{
    RASModel        kOmegaSST;
    turbulence      on;
    printCoeffs     on;
}
"""


def gravity():
    return header("uniformDimensionedVectorField", "g", "constant") + """
dimensions      [0 1 -2 0 0 0 0];
value           (0 0 0);
"""


def control():
    return header("dictionary", "controlDict", "system") + f"""
application     buoyantBoussinesqSimpleFoam;
startFrom       latestTime;
startTime       0;
stopAt          endTime;
endTime         {END_TIME};
deltaT          1;
writeControl    timeStep;
writeInterval   {WRITE_INTERVAL};
purgeWrite      {PURGE_WRITE};
writeFormat     ascii;
writePrecision  16;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;
"""


def schemes():
    return header("dictionary", "fvSchemes", "system") + """
ddtSchemes      { default steadyState; }
gradSchemes     { default Gauss linear; }
divSchemes
{
    default         none;
    div(phi,U)      bounded Gauss linearUpwind grad(U);
    div(phi,T)      bounded Gauss limitedLinear 1;
    div(phi,k)      bounded Gauss limitedLinear 1;
    div(phi,omega)  bounded Gauss limitedLinear 1;
    div((nuEff*dev2(T(grad(U))))) Gauss linear;
}
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes   { default corrected; }
wallDist        { method meshWave; }
"""


def solution():
    # NO residualControl: the case runs to endTime and convergence is judged
    # from written fields by the comparator (L-141).
    return header("dictionary", "fvSolution", "system") + """
solvers
{
    p_rgh { solver PCG; preconditioner DIC; tolerance 1e-11; relTol 0.001; }
    "(U|T|k|omega)"
    { solver PBiCGStab; preconditioner DILU; tolerance 1e-11; relTol 0.01; }
}
SIMPLE
{
    nNonOrthogonalCorrectors 0;
    pRefCell        0;
    pRefValue       0;
}
relaxationFactors
{
    fields { p_rgh 0.3; }
    equations { U 0.7; T 0.7; k 0.7; omega 0.7; }
}
"""


def wm_feasibility(first, ny_low, ny_up):
    """Return a list of human-readable reasons the W_m counts cannot be met."""
    bad = []
    for name, n, half in (("ny_low", ny_low, 0.5 * H), ("ny_up", ny_up, 2.0 * H)):
        if first * (n // 2) >= half:
            bad.append(f"{name} {n}: {n//2} cells of first cell {first:.4e} m "
                       f"need at least {first*(n//2):.4e} m but the half is "
                       f"{half:.4e} m; at most {int(half/first)} cells fit per "
                       f"half (cell-to-cell ratio >= 1), i.e. {name} <= "
                       f"{2*int(half/first)}")
    return bad


def design(level, L_up_H, L_down_H, wallfunc, laminar, wm_counts):
    lv = dict(LEVELS[level])
    if wallfunc:
        fc = first_cell_wall(WM_YPLUS)
        lv["ny_low"], lv["ny_up"] = wm_counts
        lv["yplus"] = WM_YPLUS
    else:
        fc = first_cell_wall(lv["yplus"])
    if L_up_H == 10.0:
        lv["nx_up"] = DM_NX_UP
    if L_down_H == 45.0:
        lv["nx_down"] = OM_NX_DOWN
    L_up, L_down = L_up_H * H, L_down_H * H
    r = dict(
        y_low=cell_ratio(fc, lv["ny_low"] // 2, 0.5 * H),
        y_up=cell_ratio(fc, lv["ny_up"] // 2, 2.0 * H),
        x_up=cell_ratio(X_STEP_CELL, lv["nx_up"], L_up),
        x_down=cell_ratio(X_STEP_CELL, lv["nx_down"], L_down),
    )
    if any(v is None for v in r.values()):
        return None, lv, fc, r
    R = dict(
        y_low=r["y_low"] ** (lv["ny_low"] // 2 - 1),
        y_up=r["y_up"] ** (lv["ny_up"] // 2 - 1),
        x_up=r["x_up"] ** (lv["nx_up"] - 1),
        x_down=r["x_down"] ** (lv["nx_down"] - 1),
    )
    n = lv["nx_up"] * lv["ny_up"] + lv["nx_down"] * (lv["ny_low"] + lv["ny_up"])
    return dict(lv=lv, fc=fc, r=r, R=R, nCells=n, L_up=L_up, L_down=L_down), lv, fc, r


def numeric_time_dirs(d):
    import re
    return [x for x in os.listdir(d)
            if re.fullmatch(r"[0-9]+(\.[0-9]+)?", x) and x != "0"]


def build(out, name, level, arm, L_up_H, L_down_H, prt, treatment, laminar,
          force, wm_counts):
    wallfunc = treatment == "wall functions"
    dz, lv, fc, r = design(level, L_up_H, L_down_H, wallfunc, laminar, wm_counts)
    if wallfunc:
        reasons = wm_feasibility(fc, lv["ny_low"], lv["ny_up"])
        if reasons:
            return None, reasons
    if dz is None:
        return None, [f"{k}: first cell does not fit (ratio would be below 1)"
                      for k, v in r.items() if v is None]
    d = os.path.join(out, name)
    if os.path.exists(d):
        if not force:
            return None, [f"{d} exists; pass --force to rebuild (only if never launched)"]
        if numeric_time_dirs(d) or os.path.exists(os.path.join(d, "LAUNCH_LOCK")):
            return None, [f"{d} has been launched (time dirs or LAUNCH_LOCK); refusing to delete"]
        shutil.rmtree(d)
    for sub in ("0.orig", "constant", "system"):
        os.makedirs(os.path.join(d, sub))
    w = lambda rel, txt: open(os.path.join(d, rel), "w").write(txt)
    w("system/blockMeshDict", block_mesh(
        dz["L_up"], dz["L_down"], lv["nx_up"], lv["nx_down"], lv["ny_low"],
        lv["ny_up"], dz["R"]["x_up"], dz["R"]["x_down"], dz["R"]["y_low"],
        dz["R"]["y_up"]))
    w("system/controlDict", control())
    w("system/fvSchemes", schemes())
    w("system/fvSolution", solution())
    w("constant/transportProperties", transport(prt))
    w("constant/turbulenceProperties", turbulence(laminar))
    w("constant/g", gravity())
    w("0.orig/U", f_U())
    w("0.orig/p_rgh", f_p())
    w("0.orig/T", f_T())
    w("0.orig/alphat", f_alphat(wallfunc, prt))
    # k, omega, nut are written for every case, the laminar control included
    # (contract: harmless there; turbulenceProperties decides what is solved)
    w("0.orig/k", f_k(wallfunc))
    w("0.orig/omega", f_omega())
    w("0.orig/nut", f_nut(wallfunc))
    pred = dz["nCells"] * END_TIME * CORE_SEC_PER_CELL_ITER
    model = ("laminar (TRIVIAL BASELINE, Charter 2c)" if laminar else "kOmegaSST")
    override = ("" if not wallfunc or tuple(wm_counts) == (WM_NY_LOW, WM_NY_UP)
                else f"wm_counts_override  ny_low {wm_counts[0]} ny_up {wm_counts[1]} "
                     f"(contract says {WM_NY_LOW} {WM_NY_UP}; contract amendment required)\n")
    w("CASE.txt", f"""case              {name}
rung              T3 (heated backward-facing step, Vogel and Eaton 1985 conditions)
level             {level}
arm               {arm}
model             {model}
wall_treatment    {treatment}
target_yplus      {lv['yplus']}
H                 {H} m
nu                {NU} m2/s
Pr                {PR}
Prt               {prt}
Re_target         {RE_TARGET:.0f}
U_in              {U_IN} m/s
T_in              {T_IN} K
dTdn_wall         {DTDN} K/m
L_up_H            {L_up_H:g}
L_down_H          {L_down_H:g}
nx_up             {lv['nx_up']}
nx_down           {lv['nx_down']}
ny_low            {lv['ny_low']}
ny_up             {lv['ny_up']}
first_cell_wall   {fc:.6e} m
first_cell_x_step {X_STEP_CELL:.6e} m
endTime           {END_TIME}
writeInterval     {WRITE_INTERVAL}
nCells_design     {dz['nCells']}
predicted_core_s  {pred:.0f}
r_y_low           {dz['r']['y_low']:.10f}  (cell-to-cell, B2 y, each half of {lv['ny_low']//2} cells)
r_y_up            {dz['r']['y_up']:.10f}  (cell-to-cell, B1/B3 y, each half of {lv['ny_up']//2} cells)
r_x_up            {dz['r']['x_up']:.10f}  (cell-to-cell, B1 x, growing away from the step)
r_x_down          {dz['r']['x_down']:.10f}  (cell-to-cell, B2/B3 x, growing downstream)
grading_y_low     {dz['R']['y_low']:.10g}  (written as (0.5 0.5 R) (0.5 0.5 1/R))
grading_y_up      {dz['R']['y_up']:.10g}  (written as (0.5 0.5 R) (0.5 0.5 1/R))
grading_x_up      {1.0/dz['R']['x_up']:.10g}  (written ratio, BELOW one: fine cell at the step, L-142)
grading_x_down    {dz['R']['x_down']:.10g}  (written ratio, fine cell at the step)
u_tau_estimate    {u_tau():.6f} m/s  (U_ref {U_REF}, Cf {CF_EST})
k_in              {k_in():.8g}
omega_in          {omega_in():.8g}
{override}""")
    return dict(name=name, level=level, lv=lv, fc=fc, r=dz["r"], R=dz["R"],
                nCells=dz["nCells"], pred=pred, arm=arm, prt=prt,
                treatment=treatment), []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=HERE)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--wm-counts", nargs=2, type=int, default=(WM_NY_LOW, WM_NY_UP),
                    metavar=("NY_LOW", "NY_UP"))
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)

    # cross-check the formula against the contract's quoted first cells
    for lvl, q in CONTRACT_FIRST_CELL.items():
        got = first_cell_wall(LEVELS[lvl]["yplus"])
        assert abs(got - q) / q < 1e-4, (lvl, got, q)
    assert abs(first_cell_wall(WM_YPLUS) - WM_FIRST_CELL_CONTRACT) / WM_FIRST_CELL_CONTRACT < 1e-4
    for lvl in LEVELS.values():
        assert lvl["ny_low"] % 2 == 0 and lvl["ny_up"] % 2 == 0
    assert WRITE_INTERVAL < END_TIME
    for n in a.wm_counts:
        assert n % 2 == 0, "W_m counts must be even (two-sided grading)"

    made, failed = [], {}
    for (name, level, arm, lu, ld, prt, treat, lam) in CASES:
        m, reasons = build(out, name, level, arm, lu, ld, prt, treat, lam,
                           a.force, tuple(a.wm_counts))
        if m:
            made.append(m)
        else:
            failed[name] = reasons

    print(f"T3: {len(made)} of {len(CASES)} cases written under {out}; "
          f"endTime {END_TIME}, writeInterval {WRITE_INTERVAL}, H = {H} m")
    print(f"  u_tau estimate {u_tau():.6f} m/s; k_in {k_in():.6g}; omega_in {omega_in():.6g}")
    hdr = (f"  {'case':8s} {'nx_up':>5s} {'nx_dn':>5s} {'ny_lo':>5s} {'ny_up':>5s} "
           f"{'wall cell':>11s} {'step x cell':>11s} {'r_ylo':>8s} {'r_yup':>8s} "
           f"{'r_xup':>8s} {'r_xdn':>8s} {'R_ylo':>8s} {'R_yup':>8s} "
           f"{'xg_up':>10s} {'xg_dn':>8s} {'nCells':>7s} {'core-s':>7s}  arm")
    print(hdr)
    for m in made:
        lv = m["lv"]
        print(f"  {m['name']:8s} {lv['nx_up']:5d} {lv['nx_down']:5d} {lv['ny_low']:5d} "
              f"{lv['ny_up']:5d} {m['fc']:11.4e} {X_STEP_CELL:11.4e} "
              f"{m['r']['y_low']:8.5f} {m['r']['y_up']:8.5f} {m['r']['x_up']:8.5f} "
              f"{m['r']['x_down']:8.5f} {m['R']['y_low']:8.3f} {m['R']['y_up']:8.3f} "
              f"{1.0/m['R']['x_up']:10.3e} {m['R']['x_down']:8.3f} {m['nCells']:7d} "
              f"{m['pred']:7.0f}  {m['arm']} / {m['treatment']} / Prt {m['prt']}")
    if failed:
        print()
        print("NOT BUILT (the reason is arithmetic from the contract, not a build failure):")
        for c, rs in failed.items():
            print(f"  {c}:")
            for r in rs:
                print(f"    - {r}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
