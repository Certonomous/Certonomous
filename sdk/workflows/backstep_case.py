"""F5c -- 2D backward-facing step (BFS), steady RANS, gated against
Driver & Seegmiller (1985).

Reference: Driver, D. M. and Seegmiller, H. L., "Features of a Reattaching
Turbulent Shear Layer in Divergent Channel Flow," AIAA Journal, Vol. 23,
No. 2, Feb. 1985, pp. 163-171, DOI: 10.2514/3.8890. Retrieved via the NASA
Turbulence Modeling Resource mirror (tmbwg.github.io/turbmodels/backstep_val
.html) 2026-07-28.

Case parameters taken from the primary source, NOT from the task brief's
approximate "6.1" / "37,500" figures (both close but not exact):
  - expansion ratio  (Y0 + H) / Y0 = 1.125  (upstream channel height
    Y0 = 8H, downstream channel height 9H)
  - Re_H (step height, reference velocity at x/H=-4 centerline) ~ 36,000
  - Re_theta (inlet momentum thickness) = 5000
  - inlet boundary-layer thickness at x/H=-4 ~ 1.5H (turbulent)
  - reference Mach ~0.128 (effectively incompressible; run as such)
  - MEASURED reattachment length: x_r/H = 6.26 +/- 0.10

Geometry: 5-block structured hex mesh, H=1 (nondimensional).
  x in [-4, 0]:  upstream channel, y in [1, 9]           (block A)
  x in [0, 10]:  downstream near-field, y in [0,1]+[1,9]  (blocks B1/B2)
  x in [10, 30]: downstream far-field,  y in [0,1]+[1,9]  (blocks C1/C2)
All blocks are axis-aligned rectangles (no curved edges) -- the mesh is
Cartesian and orthogonal by construction; only cell SIZE is graded.

Inlet: a 1/7-power-law turbulent boundary-layer profile (delta=1.5H,
U=0 at the wall y=1, U=Uref for y-1>=delta) imposed via ``codedFixedValue``
at x=-4H -- matching the paper's own reference station, not an assumed
long development length. Freestream turbulence intensity/eddy-viscosity
ratio at the inlet are NOT published in the retrieved source; Tu=2%,
mut/mu=10 are used as a documented assumption (same style as F1/F2).
Near-wall turbulence treatment: low-Re (kLowReWallFunction /
omegaWallFunction blended / nutLowReWallFunction), reused verbatim from
the F6a NASA-hump case (workflows.tmr_verification), because linear
wall functions are known to be unreliable through a separating/
reattaching shear layer.

Solver: simpleFoam (incompressible, steady RANS), kOmegaSST -- a linear
Boussinesq eddy-viscosity closure, which the literature (and this
family's own task brief) documents as typically UNDER-predicting BFS
reattachment length, landing near x_r/H ~ 5-6 rather than 6.26.
"""

from __future__ import annotations

import math
import re
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from workflows.tmr_verification import (
    _foam, _foam_header, _copy_best_effort, _field,
    fv_schemes, ratio_for_first_cell,
)


def _step_fv_solution(*, consistent: bool = False, relax_p: float = 0.15,
                      relax_u: float = 0.4) -> str:
    """A local fvSolution (not tmr_verification's shared one, which has no
    SIMPLEC switch) -- SIMPLEC (``consistent yes``) is a standard, low-risk
    remedy for SIMPLE's slow/fragile convergence on recirculating flows, and
    is being tried here specifically because the plain-SIMPLE coarse and
    medium solves both converged (residuals ~1e-4 to 1e-7) to the SAME
    physically implausible double-separation wall-shear signature -- ruled
    out as a resolution artifact (coarse vs. medium agree), ruled out as a
    top-wall near-wall-treatment artifact (slip-wall test, unchanged) -- so
    this tests whether it is instead a SIMPLE-branch/relaxation artifact."""
    solver = "yes" if consistent else "no"
    return _foam_header("dictionary", "fvSolution", "system") + f"""
solvers
{{
    p
    {{
        solver          GAMG;
        smoother        GaussSeidel;
        tolerance       1e-09;
        relTol          0.01;
    }}
    "(U|k|omega)"
    {{
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-10;
        relTol          0.01;
    }}
}}

SIMPLE
{{
    nNonOrthogonalCorrectors 1;
    consistent      {solver};
    residualControl
    {{
        p               1e-06;
        U               1e-08;
        "(k|omega)"     1e-08;
    }}
}}

relaxationFactors
{{
    fields    {{ p {relax_p}; }}
    equations {{ U {relax_u}; k {relax_u}; omega {relax_u}; }}
}}
"""

# --------------------------------------------------------------------------
# Case constants (Driver & Seegmiller 1985)
# --------------------------------------------------------------------------

H = 1.0                    # step height, the length scale
Y0 = 8.0 * H                # upstream channel height -> expansion ratio 1.125
Y_TOP = Y0 + H               # = 9H, downstream channel height / top wall
X_IN = -4.0 * H              # inlet plane, matches the paper's Uref station
X_MID = 10.0 * H             # near/far block split
X_OUT = 30.0 * H             # outlet plane
RE_H = 36_000.0              # step-height Reynolds number (measured source)
U_REF = 1.0
NU = U_REF * H / RE_H
DELTA_BL = 1.5 * H           # inlet boundary-layer thickness
TU_FREESTREAM = 0.02         # assumed (not published) -- documented
MUT_RATIO = 10.0             # assumed (not published) -- documented
K_INF = 1.5 * (TU_FREESTREAM * U_REF) ** 2
NUT_INF = MUT_RATIO * NU
OMEGA_INF = K_INF / NUT_INF

X_R_REFERENCE = 6.26         # Driver & Seegmiller measured x_r/H
X_R_REFERENCE_BAND = 0.10    # +/- band on the measured value

# Height of the independent near-wall U_x line sample (see
# ``nearwall_reattachment``). 2e-3 H sits a few cells above the wall on every
# level here (first cell 4e-4 H), inside the region where U_x carries the same
# sign as the wall shear, and well below the shear layer.
NEARWALL_SAMPLE_Y = 2.0e-3


@dataclass(frozen=True)
class StepGridLevel:
    name: str
    nx_up: int      # x in [-4,0],  upstream block A
    ny_hi: int      # y in [H,9H],  blocks A / B2 / C2 (shared grading)
    nx_near: int    # x in [0,10],  blocks B1lo/B1hi/B2
    nx_far: int     # x in [10,30], blocks C1lo/C1hi/C2
    ny_lo: int      # y in [0,H/2] and [H/2,H] EACH (two fine-at-both-ends
                     # sub-blocks per near/far column -- see _gradings)
    x_resolved: bool = False   # see X_RESOLVED_* below

    @property
    def cells(self) -> int:
        return (self.nx_up * self.ny_hi
                + (self.nx_near + self.nx_far) * (2 * self.ny_lo + self.ny_hi))


# The ``x_resolved`` levels exist because of a DETECTOR-RESOLUTION problem, not
# a physics one (LESSONS L-28). Reattachment is read as a zero crossing of Cf
# between adjacent wall FACE CENTRES, so the gate's ±0.10 H band can only be
# adjudicated if the wall faces near x_r are spaced comfortably inside it. On
# the original single-sided x grading -- which puts the whole streamwise budget
# of the [0,10H] block into the step corner and lets cells expand monotonically
# after it -- the faces straddling x/H ~ 6 are 0.55-0.81 H apart on `coarse`,
# 0.28-0.43 H on `medium` and 0.15-0.23 H on `fine`: every level's increment is
# larger than the band it is being graded against. The x_resolved levels keep
# the fine corner spacing but hold the cells UNIFORM at <= X_RESOLVED_TARGET
# through the region the bubble actually closes in, via a blockMesh
# multi-grading. This is a resolution requirement stated from the gate band and
# the detector, with no reference to the value being measured.
X_RESOLVED_CORNER_FRAC = 0.10   # first 1H of the [0,10H] block stays graded
X_RESOLVED_CORNER_CELLS = 0.15  # ...taking this fraction of the block's cells
X_RESOLVED_TARGET = 0.05        # target uniform cell size over the rest, in H

STEP_LEVELS = (
    StepGridLevel("coarse", nx_up=16, ny_hi=50, nx_near=50, nx_far=25, ny_lo=30),
    StepGridLevel("medium", nx_up=24, ny_hi=70, nx_near=80, nx_far=40, ny_lo=42),
    StepGridLevel("fine",   nx_up=36, ny_hi=100, nx_near=130, nx_far=65, ny_lo=60),
    StepGridLevel("xr-coarse", nx_up=16, ny_hi=50, nx_near=200, nx_far=50,
                  ny_lo=30, x_resolved=True),
    StepGridLevel("xr-medium", nx_up=24, ny_hi=70, nx_near=300, nx_far=75,
                  ny_lo=42, x_resolved=True),
    StepGridLevel("xr-fine", nx_up=36, ny_hi=100, nx_near=450, nx_far=110,
                  ny_lo=60, x_resolved=True),
)
STEP_ITERATIONS = {"coarse": 2000, "medium": 3500, "fine": 5000,
                   "xr-coarse": 20000, "xr-medium": 20000, "xr-fine": 20000}

# Wall-normal first cell, step heights. At Re_H=36,000 with Cf~O(0.005-0.01)
# for a turbulent duct, u_tau/Uref ~ 0.05-0.07, so y+=1 sits at roughly
# y/H ~ 1/(Re_H * u_tau/Uref) ~ 4e-4 -- this value targets y+ < 1 (low-Re
# wall treatment, not a wall function) with a per-cell grading ratio that
# stays under ~1.25 given the cell counts above (checked empirically: the
# ny_hi=20/ny_lo=16 first attempt at 1e-4 produced 1.5-1.7 per-cell growth,
# an unacceptably poor mesh -- the cell counts and FIRST_CELL below were
# co-tuned so every level's per-cell ratio stays under ~1.35).
FIRST_CELL = 4.0e-4


def _gradings(level: StepGridLevel) -> dict[str, float]:
    r_y_hi = ratio_for_first_cell(Y0, level.ny_hi, FIRST_CELL)
    # The y<H region is split at y=H/2 into TWO sub-blocks, each fine at ONE
    # end: fine-at-wall (y=0, for wall shear / y+) and fine-at-shear-layer
    # (y=H, the step-lip height where the separating shear layer originates
    # and initially sits, before curving down toward reattachment). A single
    # one-sided grading across the full [0,H] span was measured to leave the
    # shear layer sitting in that block's COARSE end near x=0 (cells up to
    # ~0.2H there, versus an incoming shear-layer thickness of a few 0.01H)
    # -- the first pilot of this mesh reattached at x_r/H=0.68 against a
    # reference of 6.26, an order-of-magnitude miss far beyond any
    # documented turbulence-model deficiency, traced to exactly this: the
    # shear layer was numerically smeared/merged almost immediately because
    # nothing resolved it. Splitting into fine-at-both-ends fixes this.
    r_y_lo1 = ratio_for_first_cell(0.5 * H, level.ny_lo, FIRST_CELL)   # fine at y=0
    r_y_lo2 = ratio_for_first_cell(0.5 * H, level.ny_lo, FIRST_CELL)   # fine at y=H (inverted below)
    r_x_up = ratio_for_first_cell(4.0 * H, level.nx_up, FIRST_CELL * 40.0)
    near_first = FIRST_CELL * 20.0
    if level.x_resolved:
        # Two-section multi-grading over [0,10H]: a graded corner section, then
        # a uniform section whose cell size sets the detector's increment.
        corner_len = X_RESOLVED_CORNER_FRAC * 10.0 * H
        corner_cells = max(2, int(round(X_RESOLVED_CORNER_CELLS * level.nx_near)))
        uniform_cells = level.nx_near - corner_cells
        r_corner = ratio_for_first_cell(corner_len, corner_cells, near_first)
        uniform_dx = (10.0 * H - corner_len) / uniform_cells
        near_last = uniform_dx
        x_near_spec = (f"( ({X_RESOLVED_CORNER_FRAC:.6g} "
                       f"{corner_cells / level.nx_near:.6g} {r_corner:.8g}) "
                       f"({1.0 - X_RESOLVED_CORNER_FRAC:.6g} "
                       f"{uniform_cells / level.nx_near:.6g} 1) )")
    else:
        r_x_near = ratio_for_first_cell(10.0 * H, level.nx_near, near_first)
        near_last = near_first * r_x_near
        uniform_dx = None
        x_near_spec = f"{r_x_near:.8g}"
    r_x_far = ratio_for_first_cell(20.0 * H, level.nx_far, near_last)
    return {"r_y_hi": r_y_hi, "r_y_lo1": r_y_lo1, "r_y_lo2": r_y_lo2,
            "r_x_up": r_x_up, "x_near_spec": x_near_spec, "r_x_far": r_x_far,
            "uniform_dx": uniform_dx}


def step_blockmesh_dict(level: StepGridLevel) -> str:
    g = _gradings(level)
    # Unique (x, y) points -> indices 0-13 at z=0, 14-27 at z=1.
    pts = [
        (X_IN, H),         # 0
        (X_IN, Y_TOP),     # 1
        (0.0, 0.0),        # 2
        (0.0, 0.5 * H),    # 3
        (0.0, H),          # 4
        (0.0, Y_TOP),      # 5
        (X_MID, 0.0),      # 6
        (X_MID, 0.5 * H),  # 7
        (X_MID, H),        # 8
        (X_MID, Y_TOP),    # 9
        (X_OUT, 0.0),      # 10
        (X_OUT, 0.5 * H),  # 11
        (X_OUT, H),        # 12
        (X_OUT, Y_TOP),    # 13
    ]
    o = len(pts)   # 14, the z=1 index offset
    lines = [_foam_header("dictionary", "blockMeshDict", "system"), """
scale   1;

vertices
("""]
    for z in (0.0, 1.0):
        for i, (x, y) in enumerate(pts):
            lines.append(f"    ({x:.10g} {y:.10g} {z:.10g})   // {i + o * int(z):d}")
    lines.append(""");

blocks
(""")
    nu_, nh, nn, nf, nl = level.nx_up, level.ny_hi, level.nx_near, level.nx_far, level.ny_lo

    def hexb(bl: int, br: int, tr: int, tl: int, nx: int, ny: int, gx: str, gy: str,
             comment: str) -> str:
        return (f"    hex ({bl} {br} {tr} {tl} {bl+o} {br+o} {tr+o} {tl+o}) "
               f"({nx} {ny} 1) simpleGrading ({gx} {gy} 1)  // {comment}")

    lines.append(hexb(0, 4, 5, 1, nu_, nh, f"{1.0/g['r_x_up']:.8g}", f"{g['r_y_hi']:.8g}",
                      "A upstream"))
    lines.append(hexb(2, 6, 7, 3, nn, nl, g['x_near_spec'], f"{g['r_y_lo1']:.8g}",
                      "B1lo near, y in [0,H/2], fine at wall"))
    lines.append(hexb(3, 7, 8, 4, nn, nl, g['x_near_spec'], f"{1.0/g['r_y_lo2']:.8g}",
                      "B1hi near, y in [H/2,H], fine at shear layer"))
    lines.append(hexb(4, 8, 9, 5, nn, nh, g['x_near_spec'], f"{g['r_y_hi']:.8g}",
                      "B2 near, y in [H,9H]"))
    lines.append(hexb(6, 10, 11, 7, nf, nl, f"{g['r_x_far']:.8g}", f"{g['r_y_lo1']:.8g}",
                      "C1lo far, y in [0,H/2]"))
    lines.append(hexb(7, 11, 12, 8, nf, nl, f"{g['r_x_far']:.8g}", f"{1.0/g['r_y_lo2']:.8g}",
                      "C1hi far, y in [H/2,H]"))
    lines.append(hexb(8, 12, 13, 9, nf, nh, f"{g['r_x_far']:.8g}", f"{g['r_y_hi']:.8g}",
                      "C2 far, y in [H,9H]"))
    lines.append(");\n\nboundary\n(")

    def face(a: int, b: int) -> str:
        return f"({a} {b} {b+o} {a+o})"

    front_back = [(0, 4, 5, 1), (2, 6, 7, 3), (3, 7, 8, 4), (4, 8, 9, 5),
                 (6, 10, 11, 7), (7, 11, 12, 8), (8, 12, 13, 9)]
    fb_faces = "\n".join(f"            ({a} {b} {c} {d})" for a, b, c, d in front_back)
    fb_faces_top = "\n".join(f"            ({a+o} {b+o} {c+o} {d+o})"
                             for a, b, c, d in front_back)

    lines.append(f"""
    inlet
    {{ type patch; faces ({face(0,1)}); }}
    outlet
    {{ type patch; faces ({face(10,11)} {face(11,12)} {face(12,13)}); }}
    topWall
    {{ type wall; faces ({face(1,5)} {face(5,9)} {face(9,13)}); }}
    bottomWallUpstream
    {{ type wall; faces ({face(0,4)}); }}
    stepFace
    {{ type wall; faces ({face(2,3)} {face(3,4)}); }}
    bottomWallDownstream
    {{ type wall; faces ({face(2,6)} {face(6,10)}); }}
    frontAndBack
    {{
        type empty;
        faces
        (
{fb_faces}
{fb_faces_top}
        );
    }}
""")
    lines.append(");\n\nmergePatchPairs\n(\n);\n")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# constant/ + 0/
# --------------------------------------------------------------------------

_LOWRE_TURB = _foam_header("dictionary", "turbulenceProperties", "constant") + """
simulationType  RAS;
RAS
{
    RASModel        kOmegaSST;
    turbulence      on;
    printCoeffs     on;
}
"""

# The 1/7-power-law inlet profile: U=0 at the wall (y=H), U=Uref for
# y-H >= DELTA_BL. Imposed via codedFixedValue at the x=X_IN plane
# because that plane IS the paper's own Uref reference station (x/H=-4),
# not an assumed development length upstream of it.
_INLET_CODE = f"""
    type            codedFixedValue;
    value           uniform ({U_REF:.6g} 0 0);
    name            stepInletProfile;

    code
    #{{
        const fvPatch& p = this->patch();
        const vectorField& Cf = p.Cf();
        vectorField& field = *this;
        const scalar Uref = {U_REF:.10g};
        const scalar Hwall = {H:.10g};
        const scalar delta = {DELTA_BL:.10g};
        forAll(Cf, i)
        {{
            scalar yp = Cf[i].y() - Hwall;
            scalar frac = min(max(yp / delta, 0.0), 1.0);
            field[i] = vector(Uref * Foam::pow(frac, 1.0/7.0), 0.0, 0.0);
        }}
    #}};
"""


# --------------------------------------------------------------------------
# Optional equilibrium-boundary-layer inlet turbulence (sensitivity only)
# --------------------------------------------------------------------------
# The baseline imposes a uniform freestream k/omega across the whole inlet
# plane, so the 1/7-power-law velocity profile arrives with essentially no
# turbulence inside it and has only 4H to build its own. Measured on the
# baseline coarse solve, that leaves the boundary layer at the step lip at
# Re_theta = 4,768 (documented experiment: 5,000) with a peak k about half the
# equilibrium value. This option instead specifies k and omega from the
# friction velocity implied by the documented Re_theta, which is the standard
# way to state a turbulent-BL inlet. It is a SENSITIVITY, run and reported
# separately: it is justified by matching the experiment's stated boundary
# layer, and must not be selected on the basis of the reattachment length it
# produces.
CMU = 0.09
KAPPA = 0.41
RE_THETA_REF = 5000.0
# Coles/Karman-Schoenherr style flat-plate correlation, Cf = 0.025 Re_th^-1/4.
CF_INLET = 0.025 * RE_THETA_REF ** -0.25
U_TAU_INLET = U_REF * math.sqrt(0.5 * CF_INLET)

_INLET_K_CODE = f"""
    type            codedFixedValue;
    value           uniform {K_INF:.8g};
    name            stepInletK;

    code
    #{{
        const fvPatch& p = this->patch();
        const vectorField& Cf = p.Cf();
        scalarField& field = *this;
        const scalar Hwall = {H:.10g};
        const scalar delta = {DELTA_BL:.10g};
        const scalar kEq = {U_TAU_INLET ** 2 / math.sqrt(CMU):.10g};
        const scalar kInf = {K_INF:.10g};
        forAll(Cf, i)
        {{
            scalar yp = Cf[i].y() - Hwall;
            scalar f = min(max(yp / delta, 0.0), 1.0);
            // linear decay of the log-layer level across the layer, floored
            // at the freestream value used by the baseline case
            field[i] = max(kEq * (1.0 - f), kInf);
        }}
    #}};
"""

_INLET_OMEGA_CODE = f"""
    type            codedFixedValue;
    value           uniform {OMEGA_INF:.8g};
    name            stepInletOmega;

    code
    #{{
        const fvPatch& p = this->patch();
        const vectorField& Cf = p.Cf();
        scalarField& field = *this;
        const scalar Hwall = {H:.10g};
        const scalar delta = {DELTA_BL:.10g};
        const scalar kEq = {U_TAU_INLET ** 2 / math.sqrt(CMU):.10g};
        const scalar kInf = {K_INF:.10g};
        const scalar omInf = {OMEGA_INF:.10g};
        const scalar kappa = {KAPPA:.10g};
        const scalar cmu25 = {CMU ** 0.25:.10g};
        forAll(Cf, i)
        {{
            scalar yp = max(Cf[i].y() - Hwall, 1e-12);
            scalar f = min(yp / delta, 1.0);
            scalar k = max(kEq * (1.0 - f), kInf);
            // mixing length l = min(kappa*y, 0.09*delta); omega = sqrt(k)/(Cmu^0.25 l)
            scalar l = min(kappa * yp, 0.09 * delta);
            field[i] = max(Foam::sqrt(k) / (cmu25 * l), omInf);
        }}
    #}};
"""


def initial_fields(*, inlet_bl_turbulence: bool = False) -> dict[str, str]:
    empty = "        type            empty;\n"

    def coded(block: str) -> str:
        return "".join(f"        {l}\n" for l in block.strip("\n").splitlines())

    def bc(*lines: str) -> str:
        return "".join(f"        {line}\n" for line in lines)

    walls = ("topWall", "bottomWallUpstream", "stepFace", "bottomWallDownstream")

    u_bounds = {"inlet": "".join(f"        {l}\n" for l in _INLET_CODE.strip("\n").splitlines())}
    for w in walls:
        u_bounds[w] = bc("type            noSlip;")
    u_bounds["outlet"] = bc("type            inletOutlet;",
                        f"inletValue      uniform ({U_REF:.6g} 0 0);",
                        f"value           uniform ({U_REF:.6g} 0 0);")
    u_bounds["frontAndBack"] = empty
    u = _field("volVectorField", "U", "[0 1 -1 0 0 0 0]",
              f"uniform ({U_REF:.6g} 0 0)", u_bounds)

    p_bounds = {"inlet": bc("type            zeroGradient;")}
    for w in walls:
        p_bounds[w] = bc("type            zeroGradient;")
    p_bounds["outlet"] = bc("type            fixedValue;", "value           uniform 0;")
    p_bounds["frontAndBack"] = empty
    p = _field("volScalarField", "p", "[0 2 -2 0 0 0 0]", "uniform 0", p_bounds)

    k_bounds = {"inlet": (coded(_INLET_K_CODE) if inlet_bl_turbulence
                          else bc("type            fixedValue;",
                                  f"value           uniform {K_INF:.8g};"))}
    for w in walls:
        k_bounds[w] = bc("type            kLowReWallFunction;",
                         "value           uniform 1e-12;")
    k_bounds["outlet"] = bc("type            inletOutlet;",
                        f"inletValue      uniform {K_INF:.8g};",
                        f"value           uniform {K_INF:.8g};")
    k_bounds["frontAndBack"] = empty
    k = _field("volScalarField", "k", "[0 2 -2 0 0 0 0]", f"uniform {K_INF:.8g}", k_bounds)

    om_bounds = {"inlet": (coded(_INLET_OMEGA_CODE) if inlet_bl_turbulence
                           else bc("type            fixedValue;",
                                   f"value           uniform {OMEGA_INF:.8g};"))}
    for w in walls:
        om_bounds[w] = bc("type            omegaWallFunction;",
                         "blended         true;",
                         f"value           uniform {OMEGA_INF:.8g};")
    om_bounds["outlet"] = bc("type            inletOutlet;",
                         f"inletValue      uniform {OMEGA_INF:.8g};",
                         f"value           uniform {OMEGA_INF:.8g};")
    om_bounds["frontAndBack"] = empty
    omega = _field("volScalarField", "omega", "[0 0 -1 0 0 0 0]",
                  f"uniform {OMEGA_INF:.8g}", om_bounds)

    nut_bounds = {"inlet": bc("type            calculated;", "value           uniform 0;")}
    for w in walls:
        nut_bounds[w] = bc("type            nutLowReWallFunction;", "value           uniform 0;")
    nut_bounds["outlet"] = bc("type            calculated;", "value           uniform 0;")
    nut_bounds["frontAndBack"] = empty
    nut = _field("volScalarField", "nut", "[0 2 -1 0 0 0 0]", f"uniform {NUT_INF:.8g}", nut_bounds)

    return {"U": u, "p": p, "k": k, "omega": omega, "nut": nut}


def control_dict(iterations: int, *, sample_every: int = 0) -> str:
    """``sample_every`` > 0 additionally writes the wall-shear profile every
    N iterations, so the convergence of the GATE QUANTITY itself (x_r/H vs
    iteration) is recorded rather than inferred from residuals. F5c's first
    pass reported "converged" off the linear solver's *final* residuals while
    the SIMPLE *initial* residuals were still at 1e-3; a settled x_r history
    is the check that does not depend on reading the right residual."""
    if sample_every > 0:
        ctrl = ("        executeControl  timeStep;\n"
                f"        executeInterval {sample_every};\n"
                "        writeControl    timeStep;\n"
                f"        writeInterval   {sample_every};\n")
    else:
        ctrl = ("        executeControl  onEnd;\n"
                "        writeControl    onEnd;\n")
    # The wallShearStress VOLUME field is never written: with purgeWrite 1 a
    # periodic field write would create (and then delete) time directories and
    # race the solver's own end-time write. Only the patch samples are kept.
    ws_ctrl = ctrl.replace("        writeControl    timeStep;\n"
                           f"        writeInterval   {sample_every};\n",
                           "        writeControl    none;\n") \
        if sample_every > 0 else ctrl.replace(
            "        writeControl    onEnd;\n", "        writeControl    none;\n")
    return _foam_header("dictionary", "controlDict", "system") + f"""
application     simpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {iterations};
deltaT          1;
writeControl    timeStep;
writeInterval   {iterations};
purgeWrite      1;
writeFormat     ascii;
writePrecision  10;
timeFormat      general;
timePrecision   6;

functions
{{
    wallShearStress1
    {{
        type            wallShearStress;
        libs            (fieldFunctionObjects);
        patches         (bottomWallDownstream);
{ws_ctrl}    }}
    wallSample
    {{
        type            surfaces;
        libs            (sampling);
{ctrl}        surfaceFormat   raw;
        fields          (wallShearStress p);
        interpolate     false;
        surfaces
        (
            bottomWallDownstream
            {{ type patch; patches (bottomWallDownstream); }}
        );
    }}
    nearWallLine
    {{
        type            sets;
        libs            (sampling);
{ctrl}        setFormat       raw;
        interpolationScheme cellPoint;
        fields          (U);
        sets
        (
            nearWall
            {{
                type    uniform;
                axis    x;
                start   (0.002 {NEARWALL_SAMPLE_Y:.6g} 0.5);
                end     ({X_OUT - 0.002:.6g} {NEARWALL_SAMPLE_Y:.6g} 0.5);
                nPoints 1500;
            }}
        );
    }}
    yPlus1
    {{
        type            yPlus;
        libs            (fieldFunctionObjects);
        executeControl  onEnd;
        writeControl    onEnd;
    }}
}}
"""


def build_case(case_dir: Path, level: StepGridLevel, *,
              iterations: int | None = None, sample_every: int = 0,
              inlet_bl_turbulence: bool = False,
              consistent: bool = True, relax_p: float = 0.3,
              relax_u: float = 0.6) -> dict[str, Any]:
    case = Path(case_dir)
    for sub in ("0", "constant", "system"):
        (case / sub).mkdir(parents=True, exist_ok=True)
    it = iterations if iterations is not None else STEP_ITERATIONS[level.name]
    (case / "system" / "blockMeshDict").write_text(step_blockmesh_dict(level))
    (case / "system" / "fvSchemes").write_text(fv_schemes(limited=False, transient=False))
    (case / "system" / "fvSolution").write_text(
        _step_fv_solution(consistent=consistent, relax_p=relax_p, relax_u=relax_u))
    (case / "system" / "controlDict").write_text(
        control_dict(it, sample_every=sample_every))
    (case / "constant" / "transportProperties").write_text(
        _foam_header("dictionary", "transportProperties", "constant")
        + f"transportModel  Newtonian;\nnu              {NU:.8g};\n")
    (case / "constant" / "turbulenceProperties").write_text(_LOWRE_TURB)
    for name, text in initial_fields(inlet_bl_turbulence=inlet_bl_turbulence).items():
        (case / "0" / name).write_text(text)
    return {"level": level.name, "cells": level.cells, "iterations": it, "nu": NU,
            "re_h": RE_H, "first_cell": FIRST_CELL,
            "inlet_bl_turbulence": inlet_bl_turbulence}


def parse_wall_raw(text: str) -> list[tuple[float, float]]:
    """(x, Cf) pairs from the raw-format bottomWallDownstream sample, sorted
    by x, with Cf POSITIVE for forward (attached) near-wall flow.

    SIGN CONVENTION -- this is the defect that made F5c read 4-12x low for
    two sessions, see the "2026-07-30 sign-convention correction" section of
    ``F5bc_unsteady_statistics.md``. OpenFOAM's ``wallShearStress`` function
    object computes, in ``wallShearStress.C``::

        ssp = (-Sfp/magSfp) & Reffp

    with ``Reff = -nuEff*devTwoSymm(grad(U))`` (``linearViscousStress.C``).
    On a LOWER wall the outward normal is -j, so ``-Sf/magSf`` is +j and the
    streamwise component comes out as ``Reff_yx = -nuEff*dU_x/dy`` -- i.e.
    **negative** where the near-wall flow runs forward and **positive**
    inside a recirculation. The original version of this function returned
    tau_x unnegated and the detector below then read the ``neg->pos``
    crossing as reattachment, which is exactly backwards: it located a
    SEPARATION, and specifically the downstream edge of the secondary corner
    eddy at x/H ~ 1.5, while calling the real reattachment at x/H ~ 5.6 an
    "unexplained second separation." ``tmr_verification.parse_wall_shear_raw``
    (the F6a NASA-hump case in this same repo) already had the negation and
    documented the convention; this function was written separately and lost
    it. Cf is normalised by 0.5*Uref^2 to match that sibling.

    Lines are ``x y z tau_x tau_y tau_z``; comments start with ``#``.
    """
    q = 0.5 * U_REF ** 2
    out: list[tuple[float, float]] = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        if len(parts) < 6:
            continue
        try:
            x = float(parts[0])
            tau_x = float(parts[3])
        except ValueError:
            continue
        out.append((x, -tau_x / q))
    return sorted(out)


def _sign_runs(profile: list[tuple[float, float]]) -> list[dict[str, Any]]:
    """Contiguous same-sign runs of Cf, each with its interpolated start and
    end x (zero crossings), so the wall-flow topology can be read directly
    rather than inferred from a single crossing."""
    runs: list[dict[str, Any]] = []
    for (x0, c0), (x1, c1) in zip(profile, profile[1:]):
        s0 = 1 if c0 >= 0.0 else -1
        s1 = 1 if c1 >= 0.0 else -1
        if not runs:
            runs.append({"sign": s0, "x_start": profile[0][0], "x_end": x0})
        if s1 == s0:
            runs[-1]["x_end"] = x1
        else:
            xc = x0 + (-c0 / (c1 - c0)) * (x1 - x0) if c1 != c0 else x0
            runs[-1]["x_end"] = xc
            runs.append({"sign": s1, "x_start": xc, "x_end": x1})
    for r in runs:
        r["length"] = r["x_end"] - r["x_start"]
    return runs


def reattachment_length(cf_profile: list[tuple[float, float]]) -> dict[str, Any] | None:
    """Reattachment x_r/H of the PRIMARY recirculation bubble.

    ``cf_profile`` is (x, Cf) with Cf positive for forward flow (see
    ``parse_wall_raw``). The primary bubble is taken as the LONGEST
    contiguous reversed-flow (Cf < 0) region on bottomWallDownstream, and
    x_r is the x at which Cf crosses back up through zero at that region's
    downstream end. Taking the longest region rather than the first crossing
    is what makes this robust to the secondary (and, on finer meshes,
    tertiary) corner eddies that sit between the step face and the primary
    bubble and each contribute their own pair of crossings -- the failure
    that produced the original 0.5-1.5H readings.

    The full sign topology is returned alongside so a reader can see the
    corner-eddy structure and check that nothing separates again downstream
    of x_r (a real reattachment must be followed by attached flow to the
    outlet; if it is not, that is reported rather than hidden).
    """
    pts = [(x, c) for x, c in cf_profile if x >= 0.0]
    if len(pts) < 3:
        return None
    runs = _sign_runs(pts)
    reversed_runs = [r for r in runs if r["sign"] < 0]
    if not reversed_runs:
        return None
    primary = max(reversed_runs, key=lambda r: r["length"])
    if primary is runs[-1]:
        # Never reattaches inside the domain -- not a reattachment length.
        return None
    xr = primary["x_end"]
    downstream = [r for r in runs if r["x_start"] >= xr - 1e-12]
    # The forward-flow run immediately upstream of the primary bubble is the
    # secondary corner eddy; its downstream edge is the crossing the original
    # detector mistook for reattachment.
    idx = runs.index(primary)
    corner = runs[idx - 1] if idx > 0 and runs[idx - 1]["sign"] > 0 else None
    return {
        "x_r": xr,
        "x_r_over_h": xr / H,
        "bubble_start_over_h": primary["x_start"] / H,
        "bubble_length_over_h": primary["length"] / H,
        "corner_eddy_over_h": ([corner["x_start"] / H, corner["x_end"] / H]
                               if corner else None),
        "attached_to_outlet": all(r["sign"] > 0 for r in downstream),
        "sign_runs_over_h": [
            {"sign": "forward" if r["sign"] > 0 else "reversed",
             "x_start_over_h": r["x_start"] / H, "x_end_over_h": r["x_end"] / H}
            for r in runs],
    }


def nearwall_reattachment(text: str) -> dict[str, Any] | None:
    """Independent reattachment estimate from the sign of U_x on a sampled
    line one buffer-layer height above the downstream wall.

    This exists specifically so the gate quantity does not rest on the
    ``wallShearStress`` sign convention that F5c got wrong once already: U_x
    close to the wall is signed by the flow direction itself, with no
    function-object convention in between. The two estimates must agree to
    within about a cell; a disagreement means one of them is being misread.
    """
    pts: list[tuple[float, float]] = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        if len(parts) < 4:
            continue
        try:
            pts.append((float(parts[0]), float(parts[-3])))
        except ValueError:
            continue
    pts = sorted(p for p in pts if p[0] >= 0.0)
    if len(pts) < 3:
        return None
    runs = _sign_runs(pts)
    reversed_runs = [r for r in runs if r["sign"] < 0]
    if not reversed_runs or max(reversed_runs, key=lambda r: r["length"]) is runs[-1]:
        return None
    primary = max(reversed_runs, key=lambda r: r["length"])
    return {"x_r": primary["x_end"], "x_r_over_h": primary["x_end"] / H,
            "sample_height_over_h": NEARWALL_SAMPLE_Y / H}


_RES_RE = re.compile(r"Solving for (\w+), Initial residual = ([0-9.eE+-]+)")


def parse_simple_residuals(log_text: str) -> dict[int, dict[str, float]]:
    """SIMPLE *initial* residuals per outer iteration, keyed by iteration.

    Only the FIRST ``Initial residual`` per field per outer iteration is
    kept: with ``nNonOrthogonalCorrectors 1`` the pressure equation is solved
    twice per outer iteration and the second solve's numbers are an inner
    correction, not the outer-loop residual. The linear solver's "Final
    residual" is never used here -- reading it as the convergence measure is
    what let this case be reported as converged at 1e-9 while its outer p
    residual was still 2.5e-3.
    """
    hist: dict[int, dict[str, float]] = {}
    it: int | None = None
    for line in log_text.splitlines():
        if line.startswith("Time = "):
            try:
                it = int(line.split("=", 1)[1].strip())
            except ValueError:
                it = None
            continue
        if it is None:
            continue
        m = _RES_RE.search(line)
        if m:
            hist.setdefault(it, {}).setdefault(m.group(1), float(m.group(2)))
    return hist


#: Outer-loop residual gate. ``fvSolution``'s residualControl is set tighter
#: than this (1e-6/1e-8) and is left as-is so a run that does converge stops
#: on its own; this is the level at or below which the reported x_r is
#: treated as a converged number for gating purposes, and it is checked on
#: the initial residuals of every transported field.
RESIDUAL_GATE = {"p": 1.0e-5, "Ux": 1.0e-6, "Uy": 1.0e-6,
                 "k": 1.0e-6, "omega": 1.0e-6}


def run_case(level: StepGridLevel, out_dir: Path, *, iterations: int | None = None,
            timeout: float = 1800.0, sample_every: int = 0,
            inlet_bl_turbulence: bool = False, consistent: bool = True,
            relax_p: float = 0.3, relax_u: float = 0.6,
            log: Callable[[str], None] = print) -> dict[str, Any]:
    out_dir = Path(out_dir)
    case = out_dir / "case"
    if case.exists():
        shutil.rmtree(case, ignore_errors=True)
    params = build_case(case, level, iterations=iterations, sample_every=sample_every,
                        inlet_bl_turbulence=inlet_bl_turbulence,
                        consistent=consistent, relax_p=relax_p, relax_u=relax_u)

    timings: dict[str, float] = {}
    for step, args in (("blockMesh", ["blockMesh"]), ("checkMesh", ["checkMesh"])):
        start = time.monotonic()
        result = _foam(args, case, f"log.{step}", timeout=300)
        timings[step] = round(time.monotonic() - start, 1)
        log(f"[bfs-{level.name}] {step} done in {timings[step]:.1f}s (exit {result.returncode})")
        if step == "blockMesh" and result.returncode != 0:
            tail = (case / f"log.{step}").read_text(errors="replace")
            raise RuntimeError(f"bfs-{level.name}: blockMesh failed:\n"
                               + "\n".join(tail.splitlines()[-25:]))

    start = time.monotonic()
    result = _foam(["simpleFoam"], case, "log.simpleFoam", timeout=timeout)
    timings["simpleFoam"] = round(time.monotonic() - start, 1)
    log_text = (case / "log.simpleFoam").read_text(errors="replace")
    if result.returncode != 0:
        raise RuntimeError(f"bfs-{level.name}: simpleFoam failed:\n"
                           + "\n".join(log_text.splitlines()[-30:]))

    def _by_time(paths: list[Path]) -> list[tuple[int, Path]]:
        stamped = []
        for p in paths:
            try:
                stamped.append((int(p.parent.name), p))
            except ValueError:
                continue
        return sorted(stamped)

    raw_files = _by_time(list(
        (case / "postProcessing" / "wallSample").rglob("*wallShearStress*.raw")))
    if not raw_files:
        raise RuntimeError(f"bfs-{level.name}: no wallShearStress sample output")
    profile = parse_wall_raw(raw_files[-1][1].read_text(errors="replace"))
    reattach = reattachment_length(profile)

    # x_r/H against outer-iteration count: the gate quantity's own history.
    xr_history = []
    for t, p in raw_files:
        r = reattachment_length(parse_wall_raw(p.read_text(errors="replace")))
        xr_history.append((t, r["x_r_over_h"] if r else None))

    # Independent, convention-free cross-check from near-wall U_x.
    line_files = _by_time(list((case / "postProcessing" / "nearWallLine").rglob("*U*.xy"))
                          + list((case / "postProcessing" / "nearWallLine").rglob("*U*.raw")))
    nearwall = (nearwall_reattachment(line_files[-1][1].read_text(errors="replace"))
                if line_files else None)

    residuals = parse_simple_residuals(log_text)
    last_it = max(residuals) if residuals else None
    final_res = residuals.get(last_it, {}) if last_it is not None else {}
    converged = bool(final_res) and all(
        final_res.get(f, float("inf")) <= gate for f, gate in RESIDUAL_GATE.items())

    p_files = sorted((case / "postProcessing" / "wallSample").rglob("*_p.raw"))
    pressure_profile = None
    if p_files:
        pressure_profile = []
        for line in p_files[-1].read_text(errors="replace").splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            parts = s.split()
            if len(parts) < 4:
                continue
            try:
                pressure_profile.append((float(parts[0]), float(parts[3])))
            except ValueError:
                continue
        pressure_profile.sort()

    record = {
        "level": level.name, "cells": level.cells, "iterations": params["iterations"],
        "re_h": RE_H, "nu": NU, "first_cell": FIRST_CELL,
        "inlet_bl_turbulence": inlet_bl_turbulence,
        "algorithm": ("SIMPLEC" if consistent else "SIMPLE"),
        "relax_p": relax_p, "relax_u": relax_u,
        "x_r_over_h": reattach["x_r_over_h"] if reattach else None,
        "reattachment": reattach,
        "x_r_over_h_nearwall_U": nearwall["x_r_over_h"] if nearwall else None,
        "nearwall_check": nearwall,
        "x_r_over_h_history": xr_history,
        "reference_x_r_over_h": X_R_REFERENCE,
        "reference_x_r_band": X_R_REFERENCE_BAND,
        "deviation_pct": (100.0 * (reattach["x_r_over_h"] - X_R_REFERENCE) / X_R_REFERENCE
                          if reattach else None),
        "in_gate": (abs(reattach["x_r_over_h"] - X_R_REFERENCE) <= X_R_REFERENCE_BAND
                    if reattach else False),
        "final_iteration": last_it,
        "final_initial_residuals": final_res,
        "residual_gate": RESIDUAL_GATE,
        "converged": converged,
        "wall_shear_profile": profile,
        "pressure_profile": pressure_profile,
        "wall_seconds": sum(timings.values()), "timings": timings,
    }
    xr_text = f"x_r/H={record['x_r_over_h']:.3f}" if reattach else "NO REATTACHMENT FOUND"
    nw_text = (f", nearwall-U check {nearwall['x_r_over_h']:.3f}" if nearwall else "")
    log(f"[bfs-{level.name}] {xr_text}{nw_text} "
       f"(ref {X_R_REFERENCE}+/-{X_R_REFERENCE_BAND}), cells={level.cells}, "
       f"converged={converged}, wall_s={record['wall_seconds']:.1f}")
    return record
