#!/usr/bin/env python3
"""
T1b builder: fully developed TURBULENT pipe flow against two correlations.

Written to docs/campaigns/T-family/T1b_DESIGN.md and
T1_FORCED_CONVECTION_CANON_PREREGISTRATION.md 3, BEFORE any case was solved.
The band is already armed and committed in T1b_band.json.

DECISIONS THAT ARE DECISIONS, NOT DEFAULTS:

  * BOTH WALL TREATMENTS ARE BUILT.  Choosing one would throw away the result
    that the difference between them IS -- a measurement of how much of the
    thermal answer is the wall treatment rather than the model.

  * D = 0.2 m IS SET BY A CONSTRAINT.  At Re = 3e5 a 0.02 m pipe needs
    U = 225 m/s, which is Mach 0.66 and not incompressible.  At 0.2 m the same
    Reynolds number runs at 22.5 m/s, Mach 0.066.

  * THE FIRST CELL IS SIZED PER REYNOLDS NUMBER, not once for the sweep.  A
    single mesh across a 30x Re range would sit at y+ = 0.05 at the bottom and
    y+ = 1 at the top; scaling it per Re holds the wall resolution constant so
    the four points are numerically comparable.

  * WALL BOUNDARY CONDITIONS ARE THE LAB'S OWN VALIDATED SET, read from
    K0cS_runs/S_SST_f rather than invented: nutLowReWallFunction,
    kLowReWallFunction, omegaWallFunction, alphat calculated at zero.

  * L = 100 D and Nusselt is measured at 60, 70 AND 80 D.  Turbulent entry
    length estimates in the literature spread from about 10 to 60 diameters;
    this design does not pick one and hope, it measures whether Nu has
    plateaued and reports NOT A RESULT if it has not.

  * writeInterval STRICTLY LESS THAN endTime (L-140), and the wall radius is
    read from the mesh by the comparator, never taken as D/2 -- in T1c that
    assumption cost 9 % of the Nusselt number.
"""
import math
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))

D = 0.2
R = D / 2.0
L = 100.0 * D
NU = 1.5e-5
PR = 0.71
PRT_DEFAULT = 0.85
T_IN = 300.0
DTDN = 50.0                 # constant wall heat flux, as dT/dn [K/m]
WEDGE_DEG = 5.0
END_TIME = 20000
WRITE_INTERVAL = 2000       # STRICTLY < END_TIME
STATIONS = (60.0, 70.0, 80.0)

RE_SWEEP = {"10k": 1.0e4, "30k": 3.0e4, "100k": 1.0e5, "300k": 3.0e5}
# (radial cells, axial cells, target y+ of the FIRST CELL CENTRE)
RESOLVED = {"c": (50, 250, 1.6), "m": (80, 400, 1.0), "f": (128, 640, 0.625)}

# THE WALL-FUNCTION ARM DOES NOT EXIST AT EVERY REYNOLDS NUMBER, AND THAT IS A
# RESULT RATHER THAN A BUILD FAILURE.
#
# A y+ = 50 first cell has height 2 * 50 * nu / u_tau.  Against R = 0.1 m:
#
#     Re      first cell     first/R    cells that fit (N <= R/first)
#     1e4     3.19e-02       0.319                    3
#     3e4     1.23e-02       0.123                    8
#     1e5     4.22e-03       0.042                   23
#     3e5     1.57e-03       0.016                   63
#
# A geometrically growing mesh needs first <= R/N, so at Re = 1e4 a wall-function
# mesh would have THREE cells across the radius -- the first of them a third of
# the pipe.  That is not a mesh anyone should grade, and no amount of tuning
# fixes it: the constraint is physical, because at low Re the viscous sublayer
# occupies a large fraction of a small pipe.
#
# The arm is therefore built ONLY where at least MIN_WF_CELLS fit, and its
# absence elsewhere is REPORTED with the arithmetic rather than passed over.
WALLFUNC_YPLUS = 50.0
WALLFUNC_NX = 400
MIN_WF_CELLS = 12
WF_FILL = 0.6          # fraction of the "cells that fit" bound actually used


def petukhov_f(Re):
    return (0.790 * math.log(Re) - 1.64) ** -2.0


def u_tau(Re):
    U = Re * NU / D
    return U * math.sqrt(petukhov_f(Re) / 8.0)


def first_cell(Re, yplus):
    """Cell HEIGHT whose centre sits at the requested y+."""
    return 2.0 * yplus * NU / u_tau(Re)


def grading(first, N):
    """Cell-to-cell ratio placing N cells of geometric growth across R.

    `first` is the height of the cell AT THE WALL.  The direction in which that
    cell ends up is decided in block_mesh(), not here -- see the note there.
    """
    lo, hi = 1.0 + 1e-9, 2.0
    for _ in range(300):
        m = 0.5 * (lo + hi)
        s = first * ((m ** N - 1.0) / (m - 1.0)) if m > 1.0 else first * N
        if s < R:
            lo = m
        else:
            hi = m
    return 0.5 * (lo + hi)


def header(cls, obj, loc):
    return (f"FoamFile\n{{\n    version     2.0;\n    format      ascii;\n"
            f"    class       {cls};\n    location    \"{loc}\";\n"
            f"    object      {obj};\n}}\n")


def block_mesh(nr, nx, expansion):
    """
    THE RECIPROCAL IN THE RADIAL simpleGrading IS THE POINT OF THIS FUNCTION.

    Attempt 1 of T1b wrote `simpleGrading (1 expansion 1)` with expansion > 1 and
    was refuted by its own mesh.  blockMesh reads a simpleGrading entry as the
    ratio of the LAST cell to the FIRST cell along that direction, and the radial
    direction of this block runs from the AXIS (vertices 0,1 at y = 0) to the
    WALL (y = R).  A ratio above one therefore grows the cells from axis to wall
    and puts the SMALLEST cell on the centreline, where nothing happens, and the
    LARGEST cell against the wall, where the entire physics lives.

    Measured on attempt 1's own points file, at Re = 3e5 on the finest level:

        cell touching the axis   1.96e-05 m   <- the designed WALL cell
        cell touching the wall   4.11e-03 m   <- 210 times too thick
        achieved y+ at the wall  52.3         <- design asked for 0.625

    and the consequences were not subtle: the Darcy friction factor came out
    0.00230 against Petukhov's 0.01444, a factor of six low, and the Nusselt
    number 83 against a two-correlation reference near 500.  Both improved
    monotonically under refinement (Nu 37 -> 56 -> 83) without approaching
    anything, because refinement of an inverted mesh moves the wall cell closer
    to correct without ever getting there.

    Emitting 1/expansion reverses the sequence.  The total is unchanged, because
    a geometric series summed backwards has the same sum, so the mesh still fills
    R exactly and the wall cell is `first` by construction.  Verified against the
    written points file: wall cell 1.959909e-05 m against a designed
    1.961777e-05 m, the 0.095 % being the wedge cos(theta/2) factor.
    """
    h = math.radians(WEDGE_DEG / 2.0)
    y, z = R * math.cos(h), R * math.sin(h)
    return header("dictionary", "blockMeshDict", "system") + f"""
scale 1;
vertices
(
    (0        0            0)
    ({L:.8f}  0            0)
    ({L:.8f}  {y:.10f}     {-z:.10f})
    (0        {y:.10f}     {-z:.10f})
    (0        {y:.10f}     {z:.10f})
    ({L:.8f}  {y:.10f}     {z:.10f})
);
blocks
(
    hex (0 1 2 3 0 1 5 4) ({nx} {nr} 1) simpleGrading (1 {1.0/expansion:.8f} 1)
);
edges ();
boundary
(
    inlet   {{ type patch; faces ( (0 3 4 0) ); }}
    outlet  {{ type patch; faces ( (1 2 5 1) ); }}
    wall    {{ type wall;  faces ( (3 2 5 4) ); }}
    front   {{ type wedge; faces ( (0 1 5 4) ); }}
    back    {{ type wedge; faces ( (0 1 2 3) ); }}
);
mergePatchPairs ();
"""


def wedge_tail():
    return "    front   { type wedge; }\n    back    { type wedge; }\n}\n"


def f_U(U):
    return header("volVectorField", "U", "0") + f"""
dimensions      [0 1 -1 0 0 0 0];
internalField   uniform ({U:.10g} 0 0);
boundaryField
{{
    inlet   {{ type fixedValue; value uniform ({U:.10g} 0 0); }}
    outlet  {{ type zeroGradient; }}
    wall    {{ type noSlip; }}
""" + wedge_tail()


def f_p():
    return header("volScalarField", "p_rgh", "0") + """
dimensions      [0 2 -2 0 0 0 0];
internalField   uniform 0;
boundaryField
{
    inlet   { type zeroGradient; }
    outlet  { type fixedValue; value uniform 0; }
    wall    { type zeroGradient; }
""" + wedge_tail()


def f_T():
    return header("volScalarField", "T", "0") + f"""
dimensions      [0 0 0 1 0 0 0];
internalField   uniform {T_IN:.10g};
boundaryField
{{
    inlet   {{ type fixedValue; value uniform {T_IN:.10g}; }}
    outlet  {{ type zeroGradient; }}
    wall    {{ type fixedGradient; gradient uniform {DTDN:.10g}; }}
""" + wedge_tail()


def f_k(U, wallfunc):
    k = 1.5 * (0.05 * U) ** 2
    wb = ("{ type kqRWallFunction; value $internalField; }" if wallfunc
          else "{ type kLowReWallFunction; value $internalField; }")
    return header("volScalarField", "k", "0") + f"""
dimensions      [0 2 -2 0 0 0 0];
internalField   uniform {k:.8g};
boundaryField
{{
    inlet   {{ type fixedValue; value uniform {k:.8g}; }}
    outlet  {{ type zeroGradient; }}
    wall    {wb}
""" + wedge_tail()


def f_omega(U, wallfunc):
    k = 1.5 * (0.05 * U) ** 2
    om = math.sqrt(k) / (0.09 ** 0.25 * 0.07 * D)
    return header("volScalarField", "omega", "0") + f"""
dimensions      [0 0 -1 0 0 0 0];
internalField   uniform {om:.8g};
boundaryField
{{
    inlet   {{ type fixedValue; value uniform {om:.8g}; }}
    outlet  {{ type zeroGradient; }}
    wall    {{ type omegaWallFunction; value $internalField; }}
""" + wedge_tail()


def f_nut(wallfunc):
    wb = ("{ type nutkWallFunction; value uniform 0; }" if wallfunc
          else "{ type nutLowReWallFunction; value uniform 0; }")
    return header("volScalarField", "nut", "0") + f"""
dimensions      [0 2 -1 0 0 0 0];
internalField   uniform 0;
boundaryField
{{
    inlet   {{ type calculated; value uniform 0; }}
    outlet  {{ type calculated; value uniform 0; }}
    wall    {wb}
""" + wedge_tail()


def f_alphat(wallfunc, prt):
    wb = (f"{{ type alphatJayatillekeWallFunction; Prt {prt:.10g}; "
          "value uniform 0; }" if wallfunc
          else "{ type calculated; value uniform 0; }")
    return header("volScalarField", "alphat", "0") + f"""
dimensions      [0 2 -1 0 0 0 0];
internalField   uniform 0;
boundaryField
{{
    inlet   {{ type calculated; value uniform 0; }}
    outlet  {{ type calculated; value uniform 0; }}
    wall    {wb}
""" + wedge_tail()


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
purgeWrite      2;
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
    residualControl { p_rgh 1e-8; U 1e-8; T 1e-8; k 1e-8; omega 1e-8; }
}
relaxationFactors
{
    fields { p_rgh 0.3; }
    equations { U 0.7; T 0.7; k 0.7; omega 0.7; }
}
"""


def build(name, Re, nr, nx, yplus, wallfunc, prt, laminar):
    U = Re * NU / D
    fc = first_cell(Re, yplus) if not laminar else R / nr * 0.5
    g = grading(fc, nr)
    expansion = g ** (nr - 1)
    d = os.path.join(HERE, name)
    if os.path.exists(d):
        shutil.rmtree(d)
    for sub in ("0.orig", "constant", "system"):
        os.makedirs(os.path.join(d, sub))
    w = lambda rel, txt: open(os.path.join(d, rel), "w").write(txt)
    w("system/blockMeshDict", block_mesh(nr, nx, expansion))
    w("system/controlDict", control())
    w("system/fvSchemes", schemes())
    w("system/fvSolution", solution())
    w("constant/transportProperties", transport(prt))
    w("constant/turbulenceProperties", turbulence(laminar))
    w("constant/g", gravity())
    w("0.orig/U", f_U(U))
    w("0.orig/p_rgh", f_p())
    w("0.orig/T", f_T())
    w("0.orig/alphat", f_alphat(wallfunc and not laminar, prt))
    if not laminar:
        w("0.orig/k", f_k(U, wallfunc))
        w("0.orig/omega", f_omega(U, wallfunc))
        w("0.orig/nut", f_nut(wallfunc))
    w("CASE.txt", f"""case              {name}
rung              T1b (fully developed turbulent pipe, two-correlation band)
model             {'laminar (TRIVIAL BASELINE, Charter 2c)' if laminar else 'kOmegaSST'}
wall_treatment    {'wall functions' if wallfunc else 'resolved'}
target_yplus      {yplus}
D                 {D} m
L                 {L} m  ({L/D:.0f} D)
nu                {NU} m2/s
Pr                {PR}
Prt               {prt}
Re                {Re:.0f}
U                 {U:.10g} m/s
Mach_approx       {U/343.0:.4f}
T_in              {T_IN} K
dTdn_wall         {DTDN} K/m
mesh              {nr} radial x {nx} axial
first_cell        {fc:.6e} m
cell_ratio        {g:.6f}
expansion         {expansion:.4f}
u_tau_estimate    {u_tau(Re):.6f} m/s
stations          {', '.join(str(s) for s in STATIONS)} D
endTime           {END_TIME}
writeInterval     {WRITE_INTERVAL}
""")
    return dict(name=name, Re=Re, cells=nr * nx, yplus=yplus, first=fc,
                ratio=g, wallfunc=wallfunc, prt=prt, laminar=laminar, U=U)


def main():
    made = []
    skipped = []
    for tag, Re in RE_SWEEP.items():
        for lvl, (nr, nx, yp) in RESOLVED.items():
            made.append(build(f"R_{tag}_{lvl}", Re, nr, nx, yp, False,
                              PRT_DEFAULT, False))
        fc = first_cell(Re, WALLFUNC_YPLUS)
        fits = int(R / fc)
        if fits >= MIN_WF_CELLS:
            nr = max(MIN_WF_CELLS, int(WF_FILL * fits))
            made.append(build(f"W_{tag}", Re, nr, WALLFUNC_NX, WALLFUNC_YPLUS,
                              True, PRT_DEFAULT, False))
        else:
            skipped.append((tag, Re, fc, fc / R, fits))
        nr, nx, yp = RESOLVED["f"]
        made.append(build(f"P_{tag}", Re, nr, nx, yp, False, 1.0, False))
    made.append(build("C_lam", 1.0e4, RESOLVED["m"][0], RESOLVED["m"][1],
                      RESOLVED["m"][2], False, PRT_DEFAULT, True))

    if skipped:
        print("WALL-FUNCTION ARM NOT BUILT at these Reynolds numbers, and the")
        print("reason is geometric, not a build failure:")
        for tag, Re, fc, frac, fits in skipped:
            print(f"  Re = {Re:.0f}: a y+ = {WALLFUNC_YPLUS:.0f} first cell is "
                  f"{fc:.4e} m = {frac:.1%} of the pipe radius; only {fits} cells "
                  f"fit across R, below the {MIN_WF_CELLS}-cell floor.")
        print("  At low Re the viscous sublayer occupies a large fraction of a")
        print("  small pipe, so no wall-function mesh is admissible there.\n")

    tot = sum(m["cells"] for m in made)
    print(f"T1b: {len(made)} cases, {tot} cells total, endTime {END_TIME}")
    print(f"  D = {D} m, L = {L/D:.0f} D, stations {STATIONS} D")
    print(f"\n  {'case':12s} {'Re':>8s} {'cells':>7s} {'y+':>6s} "
          f"{'first cell':>11s} {'ratio':>7s} {'U m/s':>7s}  arm")
    for m in made:
        arm = ("LAMINAR baseline" if m["laminar"] else
               "wall functions" if m["wallfunc"] else
               f"resolved Prt={m['prt']}")
        print(f"  {m['name']:12s} {m['Re']:8.0f} {m['cells']:7d} {m['yplus']:6.3f} "
              f"{m['first']:11.4e} {m['ratio']:7.4f} {m['U']:7.3f}  {arm}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
