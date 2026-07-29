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


@dataclass(frozen=True)
class StepGridLevel:
    name: str
    nx_up: int      # x in [-4,0],  upstream block A
    ny_hi: int      # y in [H,9H],  blocks A / B2 / C2 (shared grading)
    nx_near: int    # x in [0,10],  blocks B1lo/B1hi/B2
    nx_far: int     # x in [10,30], blocks C1lo/C1hi/C2
    ny_lo: int      # y in [0,H/2] and [H/2,H] EACH (two fine-at-both-ends
                     # sub-blocks per near/far column -- see _gradings)

    @property
    def cells(self) -> int:
        return (self.nx_up * self.ny_hi
                + (self.nx_near + self.nx_far) * (2 * self.ny_lo + self.ny_hi))


STEP_LEVELS = (
    StepGridLevel("coarse", nx_up=16, ny_hi=50, nx_near=50, nx_far=25, ny_lo=30),
    StepGridLevel("medium", nx_up=24, ny_hi=70, nx_near=80, nx_far=40, ny_lo=42),
    StepGridLevel("fine",   nx_up=36, ny_hi=100, nx_near=130, nx_far=65, ny_lo=60),
)
STEP_ITERATIONS = {"coarse": 2000, "medium": 3500, "fine": 5000}

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
    r_x_near = ratio_for_first_cell(10.0 * H, level.nx_near, FIRST_CELL * 20.0)
    near_first = FIRST_CELL * 20.0
    near_last = near_first * r_x_near
    r_x_far = ratio_for_first_cell(20.0 * H, level.nx_far, near_last)
    return {"r_y_hi": r_y_hi, "r_y_lo1": r_y_lo1, "r_y_lo2": r_y_lo2,
            "r_x_up": r_x_up, "r_x_near": r_x_near, "r_x_far": r_x_far}


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
    lines.append(hexb(2, 6, 7, 3, nn, nl, f"{g['r_x_near']:.8g}", f"{g['r_y_lo1']:.8g}",
                      "B1lo near, y in [0,H/2], fine at wall"))
    lines.append(hexb(3, 7, 8, 4, nn, nl, f"{g['r_x_near']:.8g}", f"{1.0/g['r_y_lo2']:.8g}",
                      "B1hi near, y in [H/2,H], fine at shear layer"))
    lines.append(hexb(4, 8, 9, 5, nn, nh, f"{g['r_x_near']:.8g}", f"{g['r_y_hi']:.8g}",
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


def initial_fields() -> dict[str, str]:
    empty = "        type            empty;\n"

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

    k_bounds = {"inlet": bc("type            fixedValue;",
                           f"value           uniform {K_INF:.8g};")}
    for w in walls:
        k_bounds[w] = bc("type            kLowReWallFunction;",
                         "value           uniform 1e-12;")
    k_bounds["outlet"] = bc("type            inletOutlet;",
                        f"inletValue      uniform {K_INF:.8g};",
                        f"value           uniform {K_INF:.8g};")
    k_bounds["frontAndBack"] = empty
    k = _field("volScalarField", "k", "[0 2 -2 0 0 0 0]", f"uniform {K_INF:.8g}", k_bounds)

    om_bounds = {"inlet": bc("type            fixedValue;",
                            f"value           uniform {OMEGA_INF:.8g};")}
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


def control_dict(iterations: int) -> str:
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
        executeControl  onEnd;
        writeControl    onEnd;
    }}
    wallSample
    {{
        type            surfaces;
        libs            (sampling);
        executeControl  onEnd;
        writeControl    onEnd;
        surfaceFormat   raw;
        fields          (wallShearStress p);
        interpolate     false;
        surfaces
        (
            bottomWallDownstream
            {{ type patch; patches (bottomWallDownstream); }}
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
              iterations: int | None = None) -> dict[str, Any]:
    case = Path(case_dir)
    for sub in ("0", "constant", "system"):
        (case / sub).mkdir(parents=True, exist_ok=True)
    it = iterations if iterations is not None else STEP_ITERATIONS[level.name]
    (case / "system" / "blockMeshDict").write_text(step_blockmesh_dict(level))
    (case / "system" / "fvSchemes").write_text(fv_schemes(limited=False, transient=False))
    (case / "system" / "fvSolution").write_text(
        _step_fv_solution(consistent=True, relax_p=0.3, relax_u=0.6))
    (case / "system" / "controlDict").write_text(control_dict(it))
    (case / "constant" / "transportProperties").write_text(
        _foam_header("dictionary", "transportProperties", "constant")
        + f"transportModel  Newtonian;\nnu              {NU:.8g};\n")
    (case / "constant" / "turbulenceProperties").write_text(_LOWRE_TURB)
    for name, text in initial_fields().items():
        (case / "0" / name).write_text(text)
    return {"level": level.name, "cells": level.cells, "iterations": it, "nu": NU,
            "re_h": RE_H, "first_cell": FIRST_CELL}


def parse_wall_raw(text: str) -> list[tuple[float, float, float]]:
    """(x, tau_x, p) triples from the raw-format bottomWallDownstream sample,
    sorted by x. wallShearStress is written as a 3-component vector; only
    the x-component (streamwise) is used for the reattachment sign change."""
    out = []
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
        out.append((x, tau_x))
    return sorted(out)


def reattachment_length(tau_profile: list[tuple[float, float]]) -> dict[str, Any] | None:
    """Locate the sign change of streamwise wall shear from negative
    (reversed, recirculating) to positive (reattached) closest to the step,
    by linear interpolation between bracketing samples. Returns x_r/H."""
    # Skip the immediate step-corner singularity noise (x/H < 0.3) where a
    # false early crossing is common in coarse meshes.
    pts = [(x, t) for x, t in tau_profile if x >= 0.3 * H]
    for (x0, t0), (x1, t1) in zip(pts, pts[1:]):
        if t0 < 0.0 <= t1:
            frac = -t0 / (t1 - t0) if t1 != t0 else 0.0
            xr = x0 + frac * (x1 - x0)
            return {"x_r": xr, "x_r_over_h": xr / H, "bracket": (x0, x1)}
    return None


def run_case(level: StepGridLevel, out_dir: Path, *, iterations: int | None = None,
            timeout: float = 1800.0, log: Callable[[str], None] = print) -> dict[str, Any]:
    out_dir = Path(out_dir)
    case = out_dir / "case"
    if case.exists():
        shutil.rmtree(case, ignore_errors=True)
    params = build_case(case, level, iterations=iterations)

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

    raw_files = sorted((case / "postProcessing" / "wallSample").rglob("*wallShearStress*.raw"))
    if not raw_files:
        raise RuntimeError(f"bfs-{level.name}: no wallShearStress sample output")
    profile = parse_wall_raw(raw_files[-1].read_text(errors="replace"))
    reattach = reattachment_length(profile)

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
        "x_r_over_h": reattach["x_r_over_h"] if reattach else None,
        "reference_x_r_over_h": X_R_REFERENCE,
        "reference_x_r_band": X_R_REFERENCE_BAND,
        "deviation_pct": (100.0 * (reattach["x_r_over_h"] - X_R_REFERENCE) / X_R_REFERENCE
                          if reattach else None),
        "wall_shear_profile": profile,
        "pressure_profile": pressure_profile,
        "wall_seconds": sum(timings.values()), "timings": timings,
    }
    xr_text = f"x_r/H={record['x_r_over_h']:.3f}" if reattach else "NO REATTACHMENT FOUND"
    log(f"[bfs-{level.name}] {xr_text} (ref {X_R_REFERENCE}+/-{X_R_REFERENCE_BAND}), "
       f"cells={level.cells}, wall_s={record['wall_seconds']:.1f}")
    return record
