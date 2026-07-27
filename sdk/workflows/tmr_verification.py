"""NASA TMR verification ladders, measured: flat plate and bump-in-channel.

The NASA Turbulence Modeling Resource (turbmodels.larc.nasa.gov, mirrored at
tmbwg.github.io/turbmodels) publishes reference verification cases a RANS code
must reproduce on systematically refined grids. This module runs the 2D
zero-pressure-gradient flat plate and the 2D bump-in-channel for the k-omega
SST closure, each with the same discipline. The flat plate:

* Re per unit grid length 5 million, plate from x=0 to x=2 (Re_x = 10 million
  at the trailing edge), domain height 1, inflow at x=-1/3 with a symmetry
  segment ahead of the leading edge — the TMR layout.
* TMR freestream turbulence exactly: k = 9e-9 a^2 and omega = 1e-6 a^2/nu
  (a = U/M, M=0.2), which is the published eddy-viscosity ratio of 0.009.
* A 3-level structured blockMesh ladder with the SAME cell counts as the three
  coarsest TMR family grids (35x25, 69x49, 137x97 nodes = 816, 3264, 13056
  cells), constant-distribution geometric stretching so each level halves
  every spacing, and sub-1 wall y+ on every level.
* simpleFoam (incompressible) with kOmegaSST, run to deep steady convergence;
  wall Cf distribution, Cf at the TMR station x=0.970084071, and the plate
  drag coefficient (Aref = plate area 2) extracted per level.
* Observed order of convergence and Richardson extrapolation across the
  ladder, compared against the CFL3D and FUN3D values published in the TMR
  convergence data files (retrieved live from tmbwg.github.io/turbmodels and
  kept under models/tmr/reference/).

Stated deviations from the TMR reference setup — never hidden:

1. simpleFoam is incompressible; TMR defines a compressible M=0.2 case and
   itself notes incompressible codes land close but not identical.
2. OpenFOAM's kOmegaSST is the strain-production SST (Menter 2003 form);
   the TMR data compared against is SST-V (vorticity production).
3. The top boundary is an OpenFOAM freestream condition at y=1 rather than a
   Riemann farfield (TMR's own study: halving the domain height moves results
   under 0.2 percent).
4. The grids match TMR cell counts and refinement factor 2 but use this
   module's own blockMesh stretching, not the distributed TMR point files.

Everything numeric in the summary is measured from the solves; nothing is
rounded toward the reference.
"""

from __future__ import annotations

import json
import math
import os
import re
import shlex
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence

from chief_engineer.head_engineer import parse_coefficient_history

_HERE = Path(__file__).resolve()
_REPO_ROOT = _HERE.parents[2]

# ---------------------------------------------------------------------------
# Case constants (TMR flat-plate specification, incompressible analog)
# ---------------------------------------------------------------------------

U_INF = 1.0                    # m/s — unit freestream
NU = 2.0e-7                    # m^2/s so Re per unit length = 5e6
MACH = 0.2                     # TMR Mach number; a = U/M below
PLATE_LENGTH = 2.0             # m — plate from x=0 to x=2
X_UPSTREAM = -1.0 / 3.0        # inflow plane ahead of the leading edge
DOMAIN_HEIGHT = 1.0
CF_STATION = 0.970084071       # TMR's Cf reporting station (Re_x ~ 4.85e6)

_A_INF = U_INF / MACH
K_INF = 9.0e-9 * _A_INF ** 2               # TMR: k_farfield = 9e-9 a^2
OMEGA_INF = 1.0e-6 * _A_INF ** 2 / NU      # TMR: omega = 1e-6 rho a^2 / mu
NUT_INF = K_INF / OMEGA_INF                # comes out at exactly 0.009 nu

# Grading: one distribution per direction, held constant across the ladder so
# doubling the count halves every spacing (a genuine refinement-factor-2
# family). R values are total expansion ratios (last cell / first cell).
R_Y = 8.5e4           # wall-normal: first cell ~4.6e-6 m on the coarse level
R_X_PLATE = 100.0     # clustered at the leading edge, stretching to the TE
R_X_UP = 40.0         # upstream block shrinks toward the leading edge

# The coarse pilot was flat in Cd to 1e-9 by iteration 433 of 20000, and the
# SIMPLE residual normalization plateaus long before residualControl would
# fire, so each level runs a fixed, generous iteration budget and must then
# PROVE its own flatness through the tail-spread gate in run_level.
ITERATIONS = {"coarse": 3000, "medium": 4000, "fine": 5000,
              "finer": 9000, "finest": 15000}

REFERENCE_SOURCE = ("turbmodels.larc.nasa.gov 2D flat plate, SST-V "
                    "convergence data (mirror tmbwg.github.io/turbmodels, "
                    "retrieved 2026-07-24)")

# Published TMR grid-convergence values, keyed by cell count N. Copied from
# drag_convergence_sstv.dat / cf_convergence_sstv.dat (models/tmr/reference/).
CFL3D_SST_V = {
    816:    {"cd": 0.270623102e-2, "cf097": 0.255183387e-2},
    3264:   {"cd": 0.278506994e-2, "cf097": 0.262624887e-2},
    13056:  {"cd": 0.282596960e-2, "cf097": 0.266477116e-2},
    52224:  {"cd": 0.284557154e-2, "cf097": 0.268299226e-2},
    208896: {"cd": 0.285332397e-2, "cf097": 0.269085355e-2},
}
FUN3D_SST_V = {
    816:    {"cd": 0.2511992e-2, "cf097": 0.251561562813413e-2},
    3264:   {"cd": 0.2678684e-2, "cf097": 0.260951403464322e-2},
    13056:  {"cd": 0.2773290e-2, "cf097": 0.265845195545244e-2},
    52224:  {"cd": 0.2821307e-2, "cf097": 0.268166367933517e-2},
    208896: {"cd": 0.2844174e-2, "cf097": 0.269054633489452e-2},
}


@dataclass(frozen=True)
class GridLevel:
    name: str          # coarse | medium | fine
    tmr_nodes: str     # the TMR family grid this matches in cell count
    nx_up: int         # cells in the upstream block
    nx_plate: int      # cells along the plate
    ny: int            # wall-normal cells

    @property
    def nx_total(self) -> int:
        return self.nx_up + self.nx_plate

    @property
    def cells(self) -> int:
        return self.nx_total * self.ny


LEVELS = (
    GridLevel("coarse", "35x25", 8, 26, 24),
    GridLevel("medium", "69x49", 16, 52, 48),
    GridLevel("fine", "137x97", 32, 104, 96),
)

# The two finest TMR family grids, queued in demo-output/website/agenda/
# proposals/tmr-flatplate-finest-grids.json to anchor the ladder in the
# asymptotic range. Kept as a separate tuple (same convention as BUMP_LEVELS
# and NACA_LEVELS below) rather than appended to LEVELS in place, since
# test_ladder_matches_the_tmr_cell_counts pins LEVELS to the three-rung pilot;
# both tuples share the same fixed gradings (R_Y, R_X_PLATE, R_X_UP), doubling
# nx_up/nx_plate/ny again from "fine" exactly as the pilot triple doubles.
FINEST_LEVELS = (
    GridLevel("finer", "273x193", 64, 208, 192),    # 52224 cells
    GridLevel("finest", "545x385", 128, 416, 384),  # 208896 cells
)


# ---------------------------------------------------------------------------
# Pure geometry / ladder mathematics (unit-tested, no solver anywhere)
# ---------------------------------------------------------------------------

def geometric_first_cell(length: float, n: int, total_ratio: float) -> float:
    """First cell size of a geometric distribution over ``length`` with ``n``
    cells and total expansion ratio ``total_ratio`` (last/first), the exact
    quantity blockMesh's simpleGrading produces."""
    if n <= 0:
        raise ValueError("cell count must be positive")
    if n == 1 or abs(total_ratio - 1.0) < 1e-12:
        return length / n
    r = total_ratio ** (1.0 / (n - 1))
    return length * (r - 1.0) / (r ** n - 1.0)


def ratio_for_first_cell(length: float, n: int, first_cell: float,
                         lo: float = 1.0 + 1e-9, hi: float = 3.0) -> float:
    """Total expansion ratio giving the requested first cell size (bisection
    on the cell-to-cell ratio; monotone, so this is exact to tolerance)."""
    if first_cell >= length / n:
        return 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if geometric_first_cell(length, n, mid ** (n - 1)) > first_cell:
            lo = mid
        else:
            hi = mid
    return (0.5 * (lo + hi)) ** (n - 1)


def observed_order(f_coarse: float, f_medium: float, f_fine: float,
                   refinement: float = 2.0) -> float | None:
    """Observed order of convergence on a constant-ratio ladder, or None when
    the sequence is not monotone (order is then meaningless and must not be
    reported as a number)."""
    e_cm = f_coarse - f_medium
    e_mf = f_medium - f_fine
    if e_cm == 0 or e_mf == 0 or (e_cm / e_mf) <= 0:
        return None
    return math.log(abs(e_cm) / abs(e_mf)) / math.log(refinement)


def richardson_extrapolate(f_medium: float, f_fine: float, order: float,
                           refinement: float = 2.0) -> float:
    """Richardson estimate of the infinite-grid value from the finest pair."""
    return f_fine + (f_fine - f_medium) / (refinement ** order - 1.0)


def grid_convergence_index(f_medium: float, f_fine: float, order: float,
                           refinement: float = 2.0,
                           safety: float = 1.25) -> float:
    """Fine-grid GCI (Roache), as a fraction of the fine-grid value."""
    if f_fine == 0:
        raise ValueError("fine-grid value of zero has no relative GCI")
    return (safety * abs((f_fine - f_medium) / f_fine)
            / (refinement ** order - 1.0))


def parse_wall_shear_raw(text: str) -> list[tuple[float, float]]:
    """(x, Cf) pairs from a raw-format patch sample of wallShearStress.

    OpenFOAM's incompressible wallShearStress is kinematic and, on a lower
    wall under +x flow, its x component is negative; Cf follows as
    -tau_x / (0.5 U^2). Lines are ``x y z tau_x tau_y tau_z``; comment lines
    start with ``#``. The profile comes back sorted by x.
    """
    q = 0.5 * U_INF ** 2
    profile: list[tuple[float, float]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split()
        if len(parts) < 6:
            continue
        try:
            x, tau_x = float(parts[0]), float(parts[3])
        except ValueError:
            continue
        profile.append((x, -tau_x / q))
    return sorted(profile)


def cf_at(profile: Sequence[tuple[float, float]], x: float) -> float | None:
    """Cf at station ``x`` by linear interpolation between face centres."""
    inside = [p for p in profile if p[0] is not None]
    if len(inside) < 2 or not inside[0][0] <= x <= inside[-1][0]:
        return None
    for (x0, c0), (x1, c1) in zip(inside, inside[1:]):
        if x0 <= x <= x1:
            if x1 == x0:
                return c0
            w = (x - x0) / (x1 - x0)
            return c0 + w * (c1 - c0)
    return None


def final_coefficient(dat_text: str, column: str = "Cd",
                      tail: int = 200) -> dict[str, float] | None:
    """Converged value of a force-coefficient column: the last iterate, plus
    the peak-to-peak spread over the final ``tail`` iterations as evidence the
    solve was genuinely flat (a steady solve is quoted at its endpoint, not
    averaged into a prettier number)."""
    history = parse_coefficient_history(dat_text)
    series = history.get(column)
    if not series:
        return None
    window = series[-min(tail, len(series)):]
    return {"value": series[-1],
            "spread": max(window) - min(window),
            "iterations": len(series)}


def parse_force_split(log_text: str, name: str = "Cd") -> dict[str, float] | None:
    """Total/pressure/viscous split of a force coefficient from the solver
    log's final forceCoeffs write block (the last occurrence wins)."""
    pattern = re.compile(
        rf"^\s*{re.escape(name)}:\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)\s+"
        rf"([0-9.eE+-]+)", re.MULTILINE)
    match = None
    for match in pattern.finditer(log_text):
        pass
    if match is None:
        return None
    return {"total": float(match.group(1)), "pressure": float(match.group(2)),
            "viscous": float(match.group(3))}


def parse_yplus_dat(text: str, patch: str = "plate") -> dict[str, float] | None:
    """min/max/average y+ for ``patch`` from a yPlus function-object file
    (last row wins: that is the converged state)."""
    result = None
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 5 and parts[1] == patch:
            try:
                result = {"min": float(parts[2]), "max": float(parts[3]),
                          "average": float(parts[4])}
            except ValueError:
                continue
    return result


# ---------------------------------------------------------------------------
# User-visible formatting (product rules: no em dashes, no banned words,
# capitalized bullets, sources cited plainly)
# ---------------------------------------------------------------------------

def format_summary_lines(summary: dict[str, Any]) -> list[str]:
    """The human summary of a completed ladder, one capitalized bullet per
    fact, every number exactly as measured."""
    lines = [
        "NASA TMR flat-plate verification, k-omega SST, "
        "3-grid ladder (turbmodels.larc.nasa.gov)",
    ]
    for grid in summary["grids"]:
        lines.append(
            f"Grid {grid['tmr_nodes']} ({grid['cells']} cells): "
            f"Cd = {grid['cd']:.6f}, Cf(x=0.97) = {grid['cf_station']:.6f}, "
            f"max y+ = {grid['yplus']['max']:.2f}, "
            f"{grid['iterations']} iterations in {grid['wall_seconds']:.0f} s")
    ref_order = summary["comparison"].get("cfl3d_observed_order_same_rungs")
    for key, label in (("cd", "Cd"), ("cf_station", "Cf(x=0.97)")):
        conv = summary["convergence"][key]
        if conv.get("observed_order") is not None:
            note = (f" (CFL3D's own order on these three rungs: "
                    f"{ref_order:.2f})" if key == "cd" and ref_order else "")
            lines.append(
                f"{label}: observed order {conv['observed_order']:.2f}{note}, "
                f"Richardson extrapolate {conv['richardson']:.6f}")
        else:
            lines.append(f"{label}: sequence not monotone, "
                         "no order or extrapolate is quoted")
    comp = summary["comparison"]
    ladder = ", ".join(f"{value:.6f}" for value in comp["cfl3d_cd_ladder"])
    lines.append(
        f"Reference: CFL3D SST-V on the same three grid sizes gives Cd "
        f"{ladder}; finest-grid (545x385) Cd = "
        f"{comp['cfl3d_cd_finest']:.6f} and Cf(x=0.97) = "
        f"{comp['cfl3d_cf097_finest']:.6f} ({summary['reference_source']})")
    if comp.get("cd_extrapolate_vs_cfl3d_finest_pct") is not None:
        lines.append(
            f"Our Richardson Cd sits {comp['cd_extrapolate_vs_cfl3d_finest_pct']:+.2f}% "
            f"from the CFL3D finest-grid value; deviations listed below apply")
    for deviation in summary["deviations"]:
        lines.append(f"Deviation: {deviation}")
    return lines


BANNED_CARD_WORDS = ("demo", "stored", "saved", "cached", "recorded",
                     "pre-computed", "trend")


def card_entry_text(summary: dict[str, Any]) -> str | None:
    """The measured-state text for the lab_stats research-challenge card, or
    None when the ladder did not produce a defensible result (the card must
    then stay at scoping)."""
    conv = summary.get("convergence", {})
    cd = conv.get("cd", {})
    grids = summary.get("grids", ())
    if len(grids) < 3 or cd.get("observed_order") is None:
        return None
    fine = grids[-1]
    text = (
        f"flat plate run live on a 3-grid ladder (816 to 13056 cells, "
        f"y+ under 1): fine-grid Cd {fine['cd']:.6f} vs CFL3D "
        f"{CFL3D_SST_V[13056]['cd']:.6f} on the same size, observed order "
        f"{cd['observed_order']:.1f}, Richardson Cd {cd['richardson']:.6f}; "
        f"bump-in-channel next")
    lowered = text.lower()
    if any(word in lowered for word in BANNED_CARD_WORDS) or "--" in text:
        raise ValueError("card text violates product language rules")
    return text


# ---------------------------------------------------------------------------
# OpenFOAM case generation (plain text builders, all testable)
# ---------------------------------------------------------------------------

def _foam_header(cls: str, obj: str, location: str | None = None) -> str:
    loc = f'    location    "{location}";\n' if location else ""
    return (
        "FoamFile\n{\n    version     2.0;\n    format      ascii;\n"
        f"    class       {cls};\n{loc}    object      {obj};\n}}\n\n"
    )


def blockmesh_dict(level: GridLevel) -> str:
    x0, xle, xte, h = X_UPSTREAM, 0.0, PLATE_LENGTH, DOMAIN_HEIGHT
    return _foam_header("dictionary", "blockMeshDict", "system") + f"""
scale   1;

vertices
(
    ({x0} 0 0)      // 0
    ({xle} 0 0)     // 1
    ({xte} 0 0)     // 2
    ({xte} {h} 0)   // 3
    ({xle} {h} 0)   // 4
    ({x0} {h} 0)    // 5
    ({x0} 0 1)      // 6
    ({xle} 0 1)     // 7
    ({xte} 0 1)     // 8
    ({xte} {h} 1)   // 9
    ({xle} {h} 1)   // 10
    ({x0} {h} 1)    // 11
);

blocks
(
    hex (0 1 4 5 6 7 10 11) ({level.nx_up} {level.ny} 1)
        simpleGrading ({1.0 / R_X_UP:.8g} {R_Y:.8g} 1)
    hex (1 2 3 4 7 8 9 10) ({level.nx_plate} {level.ny} 1)
        simpleGrading ({R_X_PLATE:.8g} {R_Y:.8g} 1)
);

boundary
(
    inlet     {{ type patch;    faces ((0 6 11 5)); }}
    outlet    {{ type patch;    faces ((2 3 9 8)); }}
    top       {{ type patch;    faces ((5 11 10 4) (4 10 9 3)); }}
    bottomSym {{ type symmetry; faces ((0 1 7 6)); }}
    plate     {{ type wall;     faces ((1 2 8 7)); }}
    frontAndBack
    {{
        type empty;
        faces ((0 5 4 1) (1 4 3 2) (6 7 10 11) (7 8 9 10));
    }}
);
"""


def control_dict(iterations: int = 5000, *, patch: str = "plate",
                 lref: float = PLATE_LENGTH, aref: float = PLATE_LENGTH,
                 drag_dir: str = "(1 0 0)",
                 lift_dir: str = "(0 1 0)") -> str:
    return _foam_header("dictionary", "controlDict", "system") + f"""
application     simpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {iterations};
deltaT          1;
writeControl    timeStep;
writeInterval   {iterations};
purgeWrite      2;
writeFormat     ascii;
writePrecision  10;
timeFormat      general;
timePrecision   6;

functions
{{
    forceCoeffs1
    {{
        type            forceCoeffs;
        libs            (forces);
        writeControl    timeStep;
        writeInterval   1;
        patches         ({patch});
        rho             rhoInf;
        rhoInf          1.0;
        magUInf         {U_INF};
        lRef            {lref};
        Aref            {aref};
        CofR            (0 0 0);
        dragDir         {drag_dir};
        liftDir         {lift_dir};
        pitchAxis       (0 0 1);
    }}
    yPlus1
    {{
        type            yPlus;
        libs            (fieldFunctionObjects);
        executeControl  onEnd;
        writeControl    onEnd;
    }}
    wallShearStress1
    {{
        type            wallShearStress;
        libs            (fieldFunctionObjects);
        patches         ({patch});
        executeControl  onEnd;
        writeControl    onEnd;
    }}
    wallCf
    {{
        type            surfaces;
        libs            (sampling);
        executeControl  onEnd;
        writeControl    onEnd;
        surfaceFormat   raw;
        fields          (wallShearStress);
        interpolate     false;
        surfaces
        (
            {patch} {{ type patch; patches ({patch}); }}
        );
    }}
}}
"""


def fv_schemes(limited: bool = False, transient: bool = False) -> str:
    """Discretization schemes. ``limited`` swaps the orthogonal-mesh
    laplacian/snGrad for limited corrected forms; the C-grid airfoil blocks
    carry real non-orthogonality (up to 70 degrees on the coarse rung) that
    the plate and bump meshes simply do not have. ``transient`` selects
    implicit Euler time marching for the time-accurate runs."""
    grad = "cellLimited Gauss linear 1" if limited else "Gauss linear"
    lap = ("Gauss linear limited corrected 0.5" if limited
           else "Gauss linear corrected")
    sng = "limited corrected 0.5" if limited else "corrected"
    ddt = "Euler" if transient else "steadyState"
    bounded = "" if transient else "bounded "
    return _foam_header("dictionary", "fvSchemes", "system") + f"""
ddtSchemes      {{ default {ddt}; }}
gradSchemes     {{ default {grad}; }}
laplacianSchemes {{ default {lap}; }}
snGradSchemes   {{ default {sng}; }}

divSchemes
{{
    // Momentum second order; turbulence advection first-order upwind.
    // The A/B on the coarse grid: linearUpwind on k and omega left a
    // persistent leading-edge bounding oscillation (5997 bounding events,
    // residuals plateaued); upwind removed every bounding event and let the
    // run converge through residualControl. Turbulence advection is
    // negligible against production and destruction in this boundary layer,
    // and the measured observed order reports whatever the ladder delivers.
    // The "bounded" form is a steady-state device and is dropped for the
    // time-accurate runs.
    default                         none;
    div(phi,U)                      {bounded}Gauss linearUpwind grad(U);
    div(phi,k)                      {bounded}Gauss upwind;
    div(phi,omega)                  {bounded}Gauss upwind;
    div((nuEff*dev2(T(grad(U)))))   Gauss linear;
}}
interpolationSchemes {{ default linear; }}
wallDist        {{ method meshWave; }}
"""


def fv_solution(non_orth_correctors: int = 0, relax_p: float = 0.3,
                relax_u: float = 0.7, potential: bool = False,
                p_solver: str = "GAMG") -> str:
    """fvSolution. ``potential`` adds the Phi solver block potentialFoam
    needs; the airfoil case initializes from a potential solution because an
    impulsive uniform start on its extreme-aspect C-grid diverged within 20
    iterations (measured, not theorized). ``p_solver`` exists for the same
    mesh: GAMG stalled on the C-grid's 1e7-aspect cells (a bare Laplace
    solve plateaued at 1000 sweeps), while PCG with DIC converges."""
    if p_solver == "PCG":
        p_inner = ("        solver          PCG;\n"
                   "        preconditioner  DIC;\n")
    else:
        p_inner = ("        solver          GAMG;\n"
                   "        smoother        GaussSeidel;\n")
    phi_block = f"""
    Phi
    {{
{p_inner}        tolerance       1e-08;
        relTol          0.02;
    }}
""" if potential else ""
    potential_block = """
potentialFlow
{
    nNonOrthogonalCorrectors 10;
    PhiRefCell      0;
    PhiRefValue     0;
}
""" if potential else ""
    return _foam_header("dictionary", "fvSolution", "system") + f"""
solvers
{{
    p
    {{
{p_inner}        tolerance       1e-09;
        relTol          0.01;
    }}
{phi_block}    "(U|k|omega)"
    {{
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-10;
        relTol          0.01;
    }}
}}

SIMPLE
{{
    nNonOrthogonalCorrectors {non_orth_correctors};
    consistent      no;
    residualControl
    {{
        p               1e-06;
        U               1e-08;
        "(k|omega)"     1e-08;
    }}
}}
{potential_block}
relaxationFactors
{{
    fields    {{ p {relax_p}; }}
    equations {{ U {relax_u}; k {relax_u}; omega {relax_u}; }}
}}
"""


def transport_properties(nu: float = NU) -> str:
    return _foam_header("dictionary", "transportProperties", "constant") + f"""
transportModel  Newtonian;
nu              {nu};
"""


def turbulence_properties() -> str:
    return _foam_header("dictionary", "turbulenceProperties", "constant") + """
simulationType  RAS;
RAS
{
    RASModel        kOmegaSST;
    turbulence      on;
    printCoeffs     on;
}
"""


def _field(cls: str, obj: str, dimensions: str, internal: str,
           boundaries: dict[str, str]) -> str:
    body = "".join(f"    {name}\n    {{\n{entry}    }}\n"
                   for name, entry in boundaries.items())
    return (_foam_header(cls, obj, "0")
            + f"dimensions      {dimensions};\n\n"
            + f"internalField   {internal};\n\n"
            + "boundaryField\n{\n" + body + "}\n")


def initial_fields() -> dict[str, str]:
    """0/ directory contents keyed by file name, TMR conditions throughout."""
    empty = "        type            empty;\n"
    sym = "        type            symmetry;\n"

    def bc(*lines: str) -> str:
        return "".join(f"        {line}\n" for line in lines)

    u = _field("volVectorField", "U", "[0 1 -1 0 0 0 0]",
               f"uniform ({U_INF} 0 0)", {
                   "inlet": bc("type            fixedValue;",
                               f"value           uniform ({U_INF} 0 0);"),
                   "outlet": bc("type            zeroGradient;"),
                   "top": bc("type            freestreamVelocity;",
                             f"freestreamValue uniform ({U_INF} 0 0);"),
                   "plate": bc("type            noSlip;"),
                   "bottomSym": sym, "frontAndBack": empty,
               })
    p = _field("volScalarField", "p", "[0 2 -2 0 0 0 0]", "uniform 0", {
        "inlet": bc("type            zeroGradient;"),
        "outlet": bc("type            fixedValue;",
                     "value           uniform 0;"),
        "top": bc("type            freestreamPressure;",
                  "freestreamValue uniform 0;"),
        "plate": bc("type            zeroGradient;"),
        "bottomSym": sym, "frontAndBack": empty,
    })
    k = _field("volScalarField", "k", "[0 2 -2 0 0 0 0]",
               f"uniform {K_INF:.8g}", {
                   "inlet": bc("type            fixedValue;",
                               f"value           uniform {K_INF:.8g};"),
                   "outlet": bc("type            inletOutlet;",
                                f"inletValue      uniform {K_INF:.8g};",
                                f"value           uniform {K_INF:.8g};"),
                   "top": bc("type            inletOutlet;",
                             f"inletValue      uniform {K_INF:.8g};",
                             f"value           uniform {K_INF:.8g};"),
                   "plate": bc("type            kLowReWallFunction;",
                               "value           uniform 1e-12;"),
                   "bottomSym": sym, "frontAndBack": empty,
               })
    omega = _field("volScalarField", "omega", "[0 0 -1 0 0 0 0]",
                   f"uniform {OMEGA_INF:.8g}", {
                       "inlet": bc("type            fixedValue;",
                                   f"value           uniform {OMEGA_INF:.8g};"),
                       "outlet": bc("type            inletOutlet;",
                                    f"inletValue      uniform {OMEGA_INF:.8g};",
                                    f"value           uniform {OMEGA_INF:.8g};"),
                       "top": bc("type            inletOutlet;",
                                 f"inletValue      uniform {OMEGA_INF:.8g};",
                                 f"value           uniform {OMEGA_INF:.8g};"),
                       "plate": bc("type            omegaWallFunction;",
                                   "blended         true;",
                                   f"value           uniform {OMEGA_INF:.8g};"),
                       "bottomSym": sym, "frontAndBack": empty,
                   })
    nut = _field("volScalarField", "nut", "[0 2 -1 0 0 0 0]",
                 f"uniform {NUT_INF:.8g}", {
                     "inlet": bc("type            calculated;",
                                 "value           uniform 0;"),
                     "outlet": bc("type            calculated;",
                                  "value           uniform 0;"),
                     "top": bc("type            calculated;",
                               "value           uniform 0;"),
                     "plate": bc("type            nutLowReWallFunction;",
                                 "value           uniform 0;"),
                     "bottomSym": sym, "frontAndBack": empty,
                 })
    return {"U": u, "p": p, "k": k, "omega": omega, "nut": nut}


def write_case(root: Path, level: GridLevel) -> Path:
    """Write the complete OpenFOAM case for one ladder level under ``root``."""
    case = Path(root) / level.name
    for sub in ("0", "constant", "system"):
        (case / sub).mkdir(parents=True, exist_ok=True)
    files = {
        "system/blockMeshDict": blockmesh_dict(level),
        "system/controlDict": control_dict(ITERATIONS.get(level.name, 5000)),
        "system/fvSchemes": fv_schemes(),
        "system/fvSolution": fv_solution(),
        "constant/transportProperties": transport_properties(),
        "constant/turbulenceProperties": turbulence_properties(),
    }
    for name, text in initial_fields().items():
        files[f"0/{name}"] = text
    for rel, text in files.items():
        with (case / rel).open("w", newline="\n") as handle:
            handle.write(text)
    return case


# ---------------------------------------------------------------------------
# OpenFOAM execution: native by default, honoring OPENFOAM_RUN_PREFIX the
# same way chief_engineer/openfoam.py does. A launcher prefix (for example a
# WSL wrapper) still works if someone sets one; nothing here requires WSL.
# ---------------------------------------------------------------------------

_RUN_ROOT = os.environ.get("CERTONOMOUS_TMR_RUN_ROOT",
                           str(Path.home() / "certonomous-runs"))


def _run_prefix() -> list[str]:
    """The launcher prefix, split into argv the same way openfoam.py resolves
    OPENFOAM_RUN_PREFIX. Empty when the OpenFOAM toolchain is already on
    PATH; a single wrapper token ("openfoam2606" on this host) or a longer
    launcher list (a WSL invocation, say) when the caller sets it that way."""
    raw = os.environ.get("OPENFOAM_RUN_PREFIX", "")
    return raw.split() if raw else []


def _foam(args: list[str], cwd: Path, log_name: str,
          timeout: float = 600.0) -> subprocess.CompletedProcess:
    """Run one OpenFOAM utility or solver natively in ``cwd``.

    Output is captured to ``log_name`` under ``cwd``, matching what the
    previous WSL-hosted commands wrote, so downstream log parsing is
    unchanged. There is no remote shell and no bashrc-sourcing preamble: the
    run prefix (``openfoam2606`` on this host) already sets up the OpenFOAM
    environment before the executable runs.
    """
    command = [*_run_prefix(), *args]
    log_path = Path(cwd) / log_name
    with log_path.open("w") as log_file:
        return subprocess.run(command, stdout=log_file,
                              stderr=subprocess.STDOUT, cwd=str(cwd),
                              timeout=timeout)


def _copy_best_effort(src: Path, dst: Path) -> None:
    """Copy an artifact (file or directory) out of the run root; a missing
    or unreadable source is not fatal here, only the caller's own checks on
    the extracted record are."""
    try:
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        elif src.exists():
            shutil.copy2(src, dst)
    except OSError:
        pass


def _stage_and_mesh(level: GridLevel, case_root: Path, out_dir: Path,
                    remote: str, writer: Callable[[Path, GridLevel], Path],
                    log: Callable[[str], None]) -> dict[str, float]:
    """Stage a case into the run root, blockMesh and checkMesh it; return
    step timings."""
    case_dir = writer(case_root, level)
    out_dir.mkdir(parents=True, exist_ok=True)
    remote_dir = Path(remote)
    shutil.rmtree(remote_dir, ignore_errors=True)
    remote_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(case_dir, remote_dir)
    if not (remote_dir / "system" / "controlDict").exists():
        raise RuntimeError(f"staging {level.name} failed: no controlDict "
                           f"landed in {remote_dir}")
    timings: dict[str, float] = {}
    for step in ("blockMesh", "checkMesh"):
        start = time.monotonic()
        log(f"[tmr:{level.name}] {step} started")
        result = _foam([step], remote_dir, f"log.{step}", timeout=600)
        timings[step] = round(time.monotonic() - start, 1)
        _copy_best_effort(remote_dir / f"log.{step}", out_dir / f"log.{step}")
        if result.returncode != 0:
            tail = (remote_dir / f"log.{step}").read_text(errors="replace")
            raise RuntimeError(f"{level.name}/{step} failed:\n"
                               + "\n".join(tail.splitlines()[-20:]))
        log(f"[tmr:{level.name}] {step} finished in {timings[step]:.1f} s")
    return timings


def _extract_record(level: GridLevel, out_dir: Path, remote: str,
                    timings: dict[str, float], station: float | None,
                    yplus_patch: str,
                    log: Callable[[str], None]) -> dict[str, Any]:
    """Pull one solved case's results out of the run root and extract the
    record.

    Raises on anything unextractable or unconverged: a broken rung must never
    be papered over with a partial number.
    """
    out_dir = Path(out_dir)
    remote_dir = Path(remote)
    # A fresh copy every time: a leftover postProcessing tree from an earlier
    # attempt would nest the new one inside it and could offer stale files to
    # the extraction globs below.
    shutil.rmtree(out_dir / "postProcessing", ignore_errors=True)
    _copy_best_effort(remote_dir / "log.simpleFoam", out_dir / "log.simpleFoam")
    _copy_best_effort(remote_dir / "postProcessing", out_dir / "postProcessing")

    coeff_files = sorted((out_dir / "postProcessing").rglob("coefficient*.dat"))
    if not coeff_files:
        raise RuntimeError(f"{level.name}: no force-coefficient output found")
    # The flatness gate reads a short tail: a residualControl stop after N
    # iterations must be judged on its endpoint behavior, not on a window
    # that reaches back into the startup transient.
    cd = final_coefficient(coeff_files[-1].read_text(errors="replace"), "Cd",
                           tail=50)
    if cd is None:
        raise RuntimeError(f"{level.name}: Cd column missing from history")
    if cd["spread"] > 1e-7:
        raise RuntimeError(
            f"{level.name}: Cd still moving ({cd['spread']:.3g} peak-to-peak "
            f"over the last 50 iterations); not defensible as steady")

    raw_files = sorted((out_dir / "postProcessing").rglob("wallShearStress_*.raw"))
    if not raw_files:
        raise RuntimeError(f"{level.name}: no wall-shear sample found")
    profile = parse_wall_shear_raw(raw_files[-1].read_text(errors="replace"))
    cf_station = None
    if station is not None:
        # A single-valued Cf(x) station only makes sense on a single-surface
        # wall (plate, bump); an airfoil folds two surfaces onto one x.
        cf_station = cf_at(profile, station)
        if cf_station is None or cf_station <= 0:
            raise RuntimeError(
                f"{level.name}: Cf at x={station} not extractable "
                f"(profile of {len(profile)} points)")
    cl = final_coefficient(coeff_files[-1].read_text(errors="replace"), "Cl",
                           tail=50)

    yplus_files = sorted((out_dir / "postProcessing").rglob("yPlus.dat"))
    yplus = (parse_yplus_dat(yplus_files[-1].read_text(errors="replace"),
                             yplus_patch)
             if yplus_files else None)
    split = parse_force_split((out_dir / "log.simpleFoam")
                              .read_text(errors="replace"), "Cd")

    record = {
        "level": level.name,
        "tmr_nodes": level.tmr_nodes,
        "cells": level.cells,
        "nx": level.nx_total,
        "ny": level.ny,
        "cd": cd["value"],
        "cd_tail_spread": cd["spread"],
        "cf_station": cf_station,
        "iterations": cd["iterations"],
        "yplus": yplus or {"min": float("nan"), "max": float("nan"),
                           "average": float("nan")},
        "wall_seconds": sum(timings.values()),
        "timings": timings,
        "cf_profile": [(round(x, 6), round(c, 8)) for x, c in profile],
    }
    if cl is not None:
        record["cl"] = cl["value"]
        record["cl_tail_spread"] = cl["spread"]
    if split:
        record["cd_pressure"] = split["pressure"]
        record["cd_viscous"] = split["viscous"]
    station_note = (f"Cf({station:g})={cf_station:.6f} "
                    if cf_station is not None else
                    f"Cl={record.get('cl', float('nan')):.5f} ")
    log(f"[tmr:{level.name}] Cd={cd['value']:.6f} "
        f"{station_note}iters={cd['iterations']} "
        f"wall={record['wall_seconds']:.0f}s")
    return record


def run_level(level: GridLevel, case_root: Path, out_dir: Path,
              log: Callable[[str], None] = print, *,
              writer: Callable[[Path, GridLevel], Path] = write_case,
              remote_prefix: str = "tmr-flatplate",
              station: float | None = CF_STATION, yplus_patch: str = "plate",
              solver_timeout: float = 5400.0,
              init_potential: bool = False) -> dict[str, Any]:
    """Mesh and solve one ladder level natively, extract the record."""
    remote = f"{_RUN_ROOT}/{remote_prefix}-{level.name}"
    out_dir = Path(out_dir)
    timings = _stage_and_mesh(level, case_root, out_dir, remote, writer, log)
    if init_potential:
        _run_potential_init(level, remote, timings, log)
    start = time.monotonic()
    log(f"[tmr:{level.name}] simpleFoam started")
    result = _foam(["simpleFoam"], Path(remote), "log.simpleFoam",
                   timeout=solver_timeout)
    timings["simpleFoam"] = round(time.monotonic() - start, 1)
    if result.returncode != 0:
        tail = (Path(remote) / "log.simpleFoam").read_text(errors="replace")
        raise RuntimeError(f"{level.name}/simpleFoam failed:\n"
                           + "\n".join(tail.splitlines()[-20:]))
    log(f"[tmr:{level.name}] simpleFoam finished in "
        f"{timings['simpleFoam']:.1f} s")
    return _extract_record(level, out_dir, remote, timings, station,
                           yplus_patch, log)


def _run_potential_init(level: GridLevel, remote: str,
                        timings: dict[str, float],
                        log: Callable[[str], None]) -> None:
    """Initialize U and phi from a potential solve before the RANS march."""
    start = time.monotonic()
    log(f"[tmr:{level.name}] potentialFoam started")
    result = _foam(["potentialFoam", "-writephi"], Path(remote),
                   "log.potentialFoam", timeout=1800)
    timings["potentialFoam"] = round(time.monotonic() - start, 1)
    if result.returncode != 0:
        tail = (Path(remote) / "log.potentialFoam").read_text(errors="replace")
        raise RuntimeError(f"{level.name}/potentialFoam failed:\n"
                           + "\n".join(tail.splitlines()[-20:]))
    log(f"[tmr:{level.name}] potentialFoam finished in "
        f"{timings['potentialFoam']:.1f} s")


def launch_level_solver(level: GridLevel, case_root: Path, out_dir: Path,
                        log: Callable[[str], None] = print, *,
                        writer: Callable[[Path, GridLevel], Path] = write_case,
                        remote_prefix: str = "tmr-flatplate",
                        init_potential: bool = False) -> dict[str, float]:
    """Stage, mesh, and start the solve DETACHED, running natively.

    For rungs whose solve outlives any sane foreground window. The detached
    process writes its exit code to ``solve.exit`` when done; the caller polls
    :func:`solver_exit_status` and then runs :func:`collect_level`. Returns
    the mesh-step timings so the eventual record carries the full wall clock.
    """
    remote = f"{_RUN_ROOT}/{remote_prefix}-{level.name}"
    timings = _stage_and_mesh(level, case_root, Path(out_dir), remote,
                              writer, log)
    if init_potential:
        _run_potential_init(level, remote, timings, log)
    remote_dir = Path(remote)
    exit_file = remote_dir / "solve.exit"
    exit_file.unlink(missing_ok=True)
    log_path = remote_dir / "log.simpleFoam"
    log_path.unlink(missing_ok=True)
    # A new session so the solver outlives this call, and this process too if
    # the caller polls from a later invocation; the exit code is written to
    # solve.exit since nothing stays around to capture a return value.
    command = [*_run_prefix(), "simpleFoam"]
    wrapper = (f"{shlex.join(command)} > log.simpleFoam 2>&1; "
              f"echo $? > solve.exit")
    subprocess.Popen(["bash", "-c", wrapper], cwd=str(remote_dir),
                     start_new_session=True, stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)
    if not log_path.exists():
        raise RuntimeError(f"{level.name}: detached solve failed to launch")
    log(f"[tmr:{level.name}] simpleFoam launched detached in {remote}")
    return timings


def solver_exit_status(level: GridLevel,
                       remote_prefix: str = "tmr-flatplate") -> int | None:
    """Exit code of a detached solve, or None while it is still running."""
    remote = f"{_RUN_ROOT}/{remote_prefix}-{level.name}"
    exit_file = Path(remote) / "solve.exit"
    if not exit_file.exists():
        return None
    raw = exit_file.read_text(errors="replace").strip()
    return int(raw) if raw.isdigit() or (raw and raw.lstrip("-").isdigit()) \
        else None


def collect_level(level: GridLevel, out_dir: Path,
                  log: Callable[[str], None] = print, *,
                  remote_prefix: str = "tmr-flatplate",
                  station: float = CF_STATION, yplus_patch: str = "plate",
                  mesh_timings: dict[str, float] | None = None,
                  solve_seconds: float | None = None) -> dict[str, Any]:
    """Extract the record of a finished detached solve (exit code must be 0)."""
    status = solver_exit_status(level, remote_prefix)
    if status != 0:
        raise RuntimeError(f"{level.name}: detached solve not finished "
                           f"cleanly (exit status {status!r})")
    remote = f"{_RUN_ROOT}/{remote_prefix}-{level.name}"
    timings = dict(mesh_timings or {})
    if solve_seconds is not None:
        timings["simpleFoam"] = round(solve_seconds, 1)
    return _extract_record(level, Path(out_dir), remote, timings, station,
                           yplus_patch, log)


# ---------------------------------------------------------------------------
# MPI-parallel solve path: added for the two finest flat-plate rungs (52224
# and 208896 cells), whose serial cost runs to hours. decomposePar and mpirun
# run under the same _run_prefix() as every other step in this module; the
# force/Cf/yPlus function objects all reduce to a single merged file under
# postProcessing regardless of rank count, so _extract_record needs no
# changes and collect_level/solver_exit_status above are reused as-is.
# ---------------------------------------------------------------------------

def _decompose_par_dict(ranks: int) -> str:
    return (_foam_header("dictionary", "decomposeParDict", "system")
            + f"numberOfSubdomains {ranks};\nmethod          scotch;\n")


def launch_level_solver_parallel(level: GridLevel, case_root: Path,
                                 out_dir: Path, ranks: int = 4,
                                 log: Callable[[str], None] = print, *,
                                 writer: Callable[[Path, GridLevel], Path] = write_case,
                                 remote_prefix: str = "tmr-flatplate",
                                 init_potential: bool = False) -> dict[str, float]:
    """Stage, mesh, decompose into ``ranks`` subdomains, and start
    ``mpirun -np ranks simpleFoam -parallel`` DETACHED.

    Mirrors :func:`launch_level_solver` exactly (same remote layout, same
    ``solve.exit`` contract), so :func:`solver_exit_status` and
    :func:`collect_level` work unchanged on a parallel launch.
    """
    remote = f"{_RUN_ROOT}/{remote_prefix}-{level.name}"
    timings = _stage_and_mesh(level, case_root, Path(out_dir), remote,
                              writer, log)
    if init_potential:
        _run_potential_init(level, remote, timings, log)
    remote_dir = Path(remote)
    with (remote_dir / "system" / "decomposeParDict").open(
            "w", newline="\n") as handle:
        handle.write(_decompose_par_dict(ranks))
    start = time.monotonic()
    log(f"[tmr:{level.name}] decomposePar started ({ranks} subdomains)")
    result = _foam(["decomposePar", "-force"], remote_dir, "log.decomposePar",
                   timeout=900)
    timings["decomposePar"] = round(time.monotonic() - start, 1)
    if result.returncode != 0:
        tail = (remote_dir / "log.decomposePar").read_text(errors="replace")
        raise RuntimeError(f"{level.name}/decomposePar failed:\n"
                           + "\n".join(tail.splitlines()[-20:]))
    log(f"[tmr:{level.name}] decomposePar finished in "
        f"{timings['decomposePar']:.1f} s")

    exit_file = remote_dir / "solve.exit"
    exit_file.unlink(missing_ok=True)
    log_path = remote_dir / "log.simpleFoam"
    log_path.unlink(missing_ok=True)
    command = [*_run_prefix(), "mpirun", "-np", str(ranks), "simpleFoam",
              "-parallel"]
    wrapper = (f"{shlex.join(command)} > log.simpleFoam 2>&1; "
              f"echo $? > solve.exit")
    subprocess.Popen(["bash", "-c", wrapper], cwd=str(remote_dir),
                     start_new_session=True, stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)
    if not log_path.exists():
        raise RuntimeError(f"{level.name}: detached parallel solve failed "
                           f"to launch")
    log(f"[tmr:{level.name}] mpirun simpleFoam ({ranks} ranks) launched "
        f"detached in {remote}")
    return timings


# ---------------------------------------------------------------------------
# Ladder orchestration, persistence, plots
# ---------------------------------------------------------------------------

def _convergence_block(values: list[float]) -> dict[str, Any]:
    fc, fm, ff = values
    order = observed_order(fc, fm, ff)
    block: dict[str, Any] = {"ladder": values, "observed_order": order}
    if order is not None:
        block["richardson"] = richardson_extrapolate(fm, ff, order)
        block["gci_fine_pct"] = 100.0 * grid_convergence_index(fm, ff, order)
    return block


def build_summary(grids: list[dict[str, Any]]) -> dict[str, Any]:
    """Assemble the persisted summary from three completed grid records."""
    cd_conv = _convergence_block([g["cd"] for g in grids])
    cf_conv = _convergence_block([g["cf_station"] for g in grids])
    comparison: dict[str, Any] = {
        "cfl3d_cd_ladder": [CFL3D_SST_V[g["cells"]]["cd"] for g in grids],
        "cfl3d_cf097_ladder": [CFL3D_SST_V[g["cells"]]["cf097"] for g in grids],
        "fun3d_cd_ladder": [FUN3D_SST_V[g["cells"]]["cd"] for g in grids],
        "cfl3d_cd_finest": CFL3D_SST_V[208896]["cd"],
        "cfl3d_cf097_finest": CFL3D_SST_V[208896]["cf097"],
        "fun3d_cd_finest": FUN3D_SST_V[208896]["cd"],
        # The reference code's own observed order on the same three rungs:
        # order near 1 on the coarse end of this family is what CFL3D itself
        # shows, so our ladder's order is judged against that, not against
        # the asymptotic 2.
        "cfl3d_observed_order_same_rungs": observed_order(
            *[CFL3D_SST_V[g["cells"]]["cd"] for g in grids]),
        "cd_fine_vs_cfl3d_same_grid_pct":
            100.0 * (grids[-1]["cd"] / CFL3D_SST_V[grids[-1]["cells"]]["cd"] - 1.0),
        "cf097_fine_vs_cfl3d_same_grid_pct":
            100.0 * (grids[-1]["cf_station"]
                     / CFL3D_SST_V[grids[-1]["cells"]]["cf097"] - 1.0),
    }
    if cd_conv.get("richardson") is not None:
        comparison["cd_extrapolate_vs_cfl3d_finest_pct"] = 100.0 * (
            cd_conv["richardson"] / comparison["cfl3d_cd_finest"] - 1.0)
    if cf_conv.get("richardson") is not None:
        comparison["cf097_extrapolate_vs_cfl3d_finest_pct"] = 100.0 * (
            cf_conv["richardson"] / comparison["cfl3d_cf097_finest"] - 1.0)
    return {
        "case": "TMR 2D zero-pressure-gradient flat plate",
        "model": "k-omega SST (OpenFOAM kOmegaSST, strain production)",
        "solver": "simpleFoam, incompressible, OpenFOAM v2606",
        "conditions": {
            "re_per_unit_length": U_INF / NU,
            "plate_length": PLATE_LENGTH,
            "mach_reference": MACH,
            "k_inf": K_INF, "omega_inf": OMEGA_INF,
            "eddy_viscosity_ratio_inf": NUT_INF / NU,
        },
        "grids": [{k: v for k, v in g.items() if k != "cf_profile"}
                  for g in grids],
        "convergence": {"cd": cd_conv, "cf_station": cf_conv},
        "comparison": comparison,
        "reference_source": REFERENCE_SOURCE,
        "numerics": ("Second-order linearUpwind momentum advection, "
                     "first-order upwind advection on k and omega, "
                     "second-order diffusion throughout"),
        "deviations": [
            "Incompressible simpleFoam analog of the M=0.2 case; TMR notes "
            "incompressible codes land close but not identical",
            "OpenFOAM kOmegaSST uses strain production; the TMR data is "
            "SST-V (vorticity production)",
            "Top boundary is an OpenFOAM freestream condition at y=1, not a "
            "Riemann farfield",
            "Grids match TMR cell counts and refinement factor 2 with this "
            "module's own blockMesh stretching, not the TMR point files",
        ],
        "generated_unix": int(time.time()),
    }


def _figures(grids: list[dict[str, Any]], summary: dict[str, Any],
             out_dir: Path) -> list[str]:
    """Cf-profile and grid-convergence figures in the control-room theme."""
    from chief_engineer import plot_theme as _t
    plt = _t._pyplot()
    if plt is None:
        return []
    made: list[str] = []
    shades = [_t.DIM, _t.MUTED, _t.LIVE]

    fig, ax = plt.subplots(figsize=(11.4, 4.6), dpi=150)
    for grid, color in zip(grids, shades):
        xs = [p[0] for p in grid["cf_profile"]]
        cfs = [p[1] for p in grid["cf_profile"]]
        ax.plot(xs, cfs, color=color, linewidth=1.8,
                label=f"{grid['tmr_nodes']} ({grid['cells']} cells)")
    ref = CFL3D_SST_V[208896]["cf097"]
    ax.scatter([CF_STATION], [ref], s=110, color=_t.VALID, zorder=5,
               edgecolor=_t.INK, linewidth=1.2,
               label="CFL3D SST-V, 545x385 grid, x=0.97")
    ax.annotate(f"CFL3D {ref:.5f}\nours (fine) {grids[-1]['cf_station']:.5f}",
                xy=(CF_STATION, ref), xytext=(-12, 26),
                textcoords="offset points", ha="right", fontsize=11,
                color=_t.INK, weight="bold")
    ax.set_xlim(0, PLATE_LENGTH)
    ax.set_ylim(0.002, 0.006)
    _t.style_axes(ax, r"$x$ along the plate [m]", r"$C_f$",
                  "TMR flat plate, k-omega SST: wall skin friction by grid "
                  "(ref. turbmodels.larc.nasa.gov)")
    leg = ax.legend(frameon=False, fontsize=10.5, loc="upper right")
    for text in leg.get_texts():
        text.set_color(_t.INK)
    fig.tight_layout()
    path = out_dir / "flatplate_cf_profiles.png"
    fig.savefig(path)
    plt.close(fig)
    made.append(str(path))

    fig, ax = plt.subplots(figsize=(11.4, 4.6), dpi=150)
    ours_h = [math.sqrt(1.0 / g["cells"]) for g in grids]
    ax.plot(ours_h, [g["cd"] for g in grids], color=_t.LIVE, linewidth=2.2,
            marker="o", markersize=7, markeredgecolor=_t.INK,
            label="This lab (simpleFoam kOmegaSST)")
    for source, data, color in (("CFL3D SST-V", CFL3D_SST_V, _t.VALID),
                                ("FUN3D SST-V", FUN3D_SST_V, _t.TREND)):
        cells = sorted(data)
        ax.plot([math.sqrt(1.0 / n) for n in cells],
                [data[n]["cd"] for n in cells], color=color, linewidth=1.6,
                marker="s", markersize=5, linestyle=(0, (4, 3)), label=source)
    rich = summary["convergence"]["cd"].get("richardson")
    if rich is not None:
        ax.scatter([0.0], [rich], s=120, color=_t.LIVE, marker="D",
                   edgecolor=_t.INK, linewidth=1.2, zorder=5,
                   label="Richardson extrapolate (ours)")
        ax.annotate(f"h=0 extrapolate {rich:.5f}", xy=(0.0, rich),
                    xytext=(10, -18), textcoords="offset points",
                    fontsize=11, color=_t.INK, weight="bold")
    _t.style_axes(ax, r"$h = \sqrt{1/N}$", r"$C_D$ (plate, Aref = 2)",
                  "TMR flat plate: drag-coefficient grid convergence vs "
                  "published CFL3D and FUN3D ladders")
    leg = ax.legend(frameon=False, fontsize=10.5, loc="upper right")
    for text in leg.get_texts():
        text.set_color(_t.INK)
    fig.tight_layout()
    path = out_dir / "flatplate_cd_convergence.png"
    fig.savefig(path)
    plt.close(fig)
    made.append(str(path))
    return made


def run_flat_plate_ladder(out_root: str | Path | None = None,
                          levels: Sequence[GridLevel] = LEVELS,
                          log: Callable[[str], None] = print) -> dict[str, Any]:
    """The whole mission: build, run, extract, compare, persist.

    Writes flatplate_sst.json plus figures under demo-output/website/tmr/ and
    returns the summary dict. Any failed rung raises; nothing partial is
    persisted as if it were a completed ladder.
    """
    out_dir = Path(out_root) if out_root else (
        _REPO_ROOT / "demo-output" / "website" / "tmr")
    out_dir.mkdir(parents=True, exist_ok=True)
    case_root = _REPO_ROOT / "models" / "tmr" / "flatplate"
    grids = []
    for level in levels:
        record = run_level(level, case_root, out_dir / "runs" / level.name, log)
        with (out_dir / "runs" / level.name / "record.json").open(
                "w", newline="\n") as handle:
            json.dump(record, handle)
        grids.append(record)
    return persist_ladder(grids, out_dir, log)


def persist_ladder(grids: list[dict[str, Any]], out_dir: Path,
                   log: Callable[[str], None] = print) -> dict[str, Any]:
    """Summary, figures, and JSON persistence for three completed records
    (kept separate from the solves so an interrupted ladder can be assembled
    from its per-level record files without re-running anything that already
    ran to completion)."""
    out_dir = Path(out_dir)
    summary = build_summary(grids)
    summary["plots"] = [Path(p).name for p in _figures(grids, summary, out_dir)]
    with (out_dir / "flatplate_sst.json").open("w", newline="\n") as handle:
        json.dump(summary, handle, indent=2)
    profiles = {g["level"]: g["cf_profile"] for g in grids}
    with (out_dir / "flatplate_cf_profiles.json").open("w", newline="\n") as handle:
        json.dump(profiles, handle)
    for line in format_summary_lines(summary):
        log(f"[tmr] {line}")
    return summary


# ---------------------------------------------------------------------------
# Bump-in-channel: the second TMR verification case, same discipline
# ---------------------------------------------------------------------------
# TMR spec (tmbwg.github.io/turbmodels/bump.html): viscous wall from x=0 to
# x=1.5 carrying the bump y = 0.05 sin^4(pi x / 0.9 - pi/3) for
# 0.3 <= x <= 1.2; symmetry on the bottom outside the wall; farfield 25 units
# up- and downstream of the wall; a symmetry plane at y=5; M=0.2 and
# Re = 3 million per unit grid length; body reference length 1.5.

BUMP_NU = 1.0 / 3.0e6                             # Re per unit length = 3e6
BUMP_OMEGA_INF = 1.0e-6 * _A_INF ** 2 / BUMP_NU   # TMR farfield omega (75.0)
BUMP_NUT_INF = K_INF / BUMP_OMEGA_INF             # again exactly 0.009 nu
BUMP_WALL_LENGTH = 1.5
BUMP_X_IN, BUMP_X_OUT = -25.0, 26.5               # 25 units beyond each end
BUMP_HEIGHT = 5.0
BUMP_CF_STATION = 0.75                            # TMR's bump-peak station

BUMP_REFERENCE_SOURCE = (
    "turbmodels.larc.nasa.gov 2D bump-in-channel, SST convergence data "
    "(mirror tmbwg.github.io/turbmodels, retrieved 2026-07-24)")

# Published TMR bump grid-convergence values, keyed by cell count N. Copied
# from force_convergence_sst.dat / cf_convergence_sst.dat (kept under
# models/tmr/reference/ as bump_*.dat). cf is at x=0.75, the bump peak.
CFL3D_BUMP_SST = {
    3520:   {"cd": 0.45618542592e-2, "cdp": 0.14787721313e-2,
             "cdv": 0.30830821278e-2, "cl": 0.23518706955e-1,
             "cf075": 0.51639261700e-2},
    14080:  {"cd": 0.37071442412e-2, "cdp": 0.55434360560e-3,
             "cdv": 0.31528006356e-2, "cl": 0.24507319517e-1,
             "cf075": 0.56221550300e-2},
    56320:  {"cd": 0.36071373739e-2, "cdp": 0.43164677088e-3,
             "cdv": 0.31754906030e-2, "cl": 0.24827092796e-1,
             "cf075": 0.57688662800e-2},
    225280: {"cd": 0.36027064448e-2, "cdp": 0.42017585113e-3,
             "cdv": 0.31825305937e-2, "cl": 0.24974439737e-1,
             "cf075": 0.58239931200e-2},
    901120: {"cd": 0.36045158543e-2, "cdp": 0.42098043518e-3,
             "cdv": 0.31835354191e-2, "cl": 0.25047395710e-1,
             "cf075": 0.58482303300e-2},
}
FUN3D_BUMP_SST = {
    3520:   {"cd": 0.4056323e-2, "cf075": 5.219778512e-3},
    14080:  {"cd": 0.3610564e-2, "cf075": 5.612602923e-3},
    56320:  {"cd": 0.3573397e-2, "cf075": 5.764481612e-3},
    225280: {"cd": 0.3590616e-2, "cf075": 5.829360802e-3},
    901120: {"cd": 0.3592588e-2, "cf075": 5.853800103e-3},
}


@dataclass(frozen=True)
class BumpGridLevel:
    name: str
    tmr_nodes: str
    nx_up: int         # cells upstream of the wall (25 units)
    nx_wall: int       # cells along the 1.5-unit wall, uniform
    nx_down: int       # cells downstream of the wall (25 units)
    ny: int

    @property
    def nx_total(self) -> int:
        return self.nx_up + self.nx_wall + self.nx_down

    @property
    def cells(self) -> int:
        return self.nx_total * self.ny


BUMP_LEVELS = (
    BumpGridLevel("coarse", "89x41", 12, 64, 12, 40),
    BumpGridLevel("medium", "177x81", 24, 128, 24, 80),
    BumpGridLevel("fine", "353x161", 48, 256, 48, 160),
)

# Family gradings, fixed across levels exactly as for the flat plate. The
# wall-normal first cell is ~5e-6 on the coarse rung (y+ < 1 at the bump-peak
# u_tau); the outer blocks contract toward the wall so the junction spacing
# matches the uniform wall spacing on every level.
R_Y_BUMP = ratio_for_first_cell(BUMP_HEIGHT, 40, 5.0e-6)
R_X_OUTER = ratio_for_first_cell(25.0, 12, BUMP_WALL_LENGTH / 64)

BUMP_ITERATIONS = {"coarse": 4000, "medium": 6000, "fine": 9000}


def bump_profile(x: float) -> float:
    """The TMR bump wall height: 0.05 sin^4(pi x / 0.9 - pi/3) on
    0.3 <= x <= 1.2, zero on the rest of the wall."""
    if x < 0.3 or x > 1.2:
        return 0.0
    return 0.05 * math.sin(math.pi * x / 0.9 - math.pi / 3.0) ** 4


def bump_edge_points(n: int = 480) -> list[tuple[float, float]]:
    """Interior points of the wall's bottom edge (endpoints are block
    vertices), densely sampled so the piecewise-linear edge is far finer
    than any cell on any level."""
    return [(x, bump_profile(x))
            for x in (BUMP_WALL_LENGTH * i / n for i in range(1, n))]


def bump_blockmesh_dict(level: BumpGridLevel) -> str:
    x0, x1, x2, x3 = BUMP_X_IN, 0.0, BUMP_WALL_LENGTH, BUMP_X_OUT
    h = BUMP_HEIGHT

    def edge(z: float) -> str:
        inner = "\n".join(f"            ({x:.10g} {y:.10g} {z})"
                          for x, y in bump_edge_points())
        return inner
    return _foam_header("dictionary", "blockMeshDict", "system") + f"""
scale   1;

vertices
(
    ({x0} 0 0)     // 0
    ({x1} 0 0)     // 1
    ({x2} 0 0)     // 2
    ({x3} 0 0)     // 3
    ({x3} {h} 0)   // 4
    ({x2} {h} 0)   // 5
    ({x1} {h} 0)   // 6
    ({x0} {h} 0)   // 7
    ({x0} 0 1)     // 8
    ({x1} 0 1)     // 9
    ({x2} 0 1)     // 10
    ({x3} 0 1)     // 11
    ({x3} {h} 1)   // 12
    ({x2} {h} 1)   // 13
    ({x1} {h} 1)   // 14
    ({x0} {h} 1)   // 15
);

blocks
(
    hex (0 1 6 7 8 9 14 15) ({level.nx_up} {level.ny} 1)
        simpleGrading ({1.0 / R_X_OUTER:.8g} {R_Y_BUMP:.8g} 1)
    hex (1 2 5 6 9 10 13 14) ({level.nx_wall} {level.ny} 1)
        simpleGrading (1 {R_Y_BUMP:.8g} 1)
    hex (2 3 4 5 10 11 12 13) ({level.nx_down} {level.ny} 1)
        simpleGrading ({R_X_OUTER:.8g} {R_Y_BUMP:.8g} 1)
);

edges
(
    polyLine 1 2
    (
{edge(0)}
    )
    polyLine 9 10
    (
{edge(1)}
    )
);

boundary
(
    inlet     {{ type patch;    faces ((0 8 15 7)); }}
    outlet    {{ type patch;    faces ((3 4 12 11)); }}
    top       {{ type symmetry; faces ((7 15 14 6) (6 14 13 5) (5 13 12 4)); }}
    bottomSym {{ type symmetry; faces ((0 1 9 8) (2 3 11 10)); }}
    bump      {{ type wall;     faces ((1 2 10 9)); }}
    frontAndBack
    {{
        type empty;
        faces ((0 7 6 1) (1 6 5 2) (2 5 4 3)
               (8 9 14 15) (9 10 13 14) (10 11 12 13));
    }}
);
"""


def bump_initial_fields() -> dict[str, str]:
    """0/ files for the bump case: TMR bump freestream turbulence, symmetry
    top (the TMR spec), low-Re wall treatment on the bump."""
    empty = "        type            empty;\n"
    sym = "        type            symmetry;\n"

    def bc(*lines: str) -> str:
        return "".join(f"        {line}\n" for line in lines)

    u = _field("volVectorField", "U", "[0 1 -1 0 0 0 0]",
               f"uniform ({U_INF} 0 0)", {
                   "inlet": bc("type            fixedValue;",
                               f"value           uniform ({U_INF} 0 0);"),
                   "outlet": bc("type            zeroGradient;"),
                   "top": sym,
                   "bump": bc("type            noSlip;"),
                   "bottomSym": sym, "frontAndBack": empty,
               })
    p = _field("volScalarField", "p", "[0 2 -2 0 0 0 0]", "uniform 0", {
        "inlet": bc("type            zeroGradient;"),
        "outlet": bc("type            fixedValue;",
                     "value           uniform 0;"),
        "top": sym,
        "bump": bc("type            zeroGradient;"),
        "bottomSym": sym, "frontAndBack": empty,
    })
    k = _field("volScalarField", "k", "[0 2 -2 0 0 0 0]",
               f"uniform {K_INF:.8g}", {
                   "inlet": bc("type            fixedValue;",
                               f"value           uniform {K_INF:.8g};"),
                   "outlet": bc("type            inletOutlet;",
                                f"inletValue      uniform {K_INF:.8g};",
                                f"value           uniform {K_INF:.8g};"),
                   "top": sym,
                   "bump": bc("type            kLowReWallFunction;",
                              "value           uniform 1e-12;"),
                   "bottomSym": sym, "frontAndBack": empty,
               })
    omega = _field("volScalarField", "omega", "[0 0 -1 0 0 0 0]",
                   f"uniform {BUMP_OMEGA_INF:.8g}", {
                       "inlet": bc("type            fixedValue;",
                                   f"value           uniform {BUMP_OMEGA_INF:.8g};"),
                       "outlet": bc("type            inletOutlet;",
                                    f"inletValue      uniform {BUMP_OMEGA_INF:.8g};",
                                    f"value           uniform {BUMP_OMEGA_INF:.8g};"),
                       "top": sym,
                       "bump": bc("type            omegaWallFunction;",
                                  "blended         true;",
                                  f"value           uniform {BUMP_OMEGA_INF:.8g};"),
                       "bottomSym": sym, "frontAndBack": empty,
                   })
    nut = _field("volScalarField", "nut", "[0 2 -1 0 0 0 0]",
                 f"uniform {BUMP_NUT_INF:.8g}", {
                     "inlet": bc("type            calculated;",
                                 "value           uniform 0;"),
                     "outlet": bc("type            calculated;",
                                  "value           uniform 0;"),
                     "top": sym,
                     "bump": bc("type            nutLowReWallFunction;",
                                "value           uniform 0;"),
                     "bottomSym": sym, "frontAndBack": empty,
                 })
    return {"U": u, "p": p, "k": k, "omega": omega, "nut": nut}


def write_bump_case(root: Path, level: BumpGridLevel) -> Path:
    """Write the complete bump-in-channel case for one ladder level."""
    case = Path(root) / level.name
    for sub in ("0", "constant", "system"):
        (case / sub).mkdir(parents=True, exist_ok=True)
    files = {
        "system/blockMeshDict": bump_blockmesh_dict(level),
        "system/controlDict": control_dict(
            BUMP_ITERATIONS.get(level.name, 8000), patch="bump",
            lref=BUMP_WALL_LENGTH, aref=BUMP_WALL_LENGTH),
        "system/fvSchemes": fv_schemes(),
        "system/fvSolution": fv_solution(),
        "constant/transportProperties": transport_properties(BUMP_NU),
        "constant/turbulenceProperties": turbulence_properties(),
    }
    for name, text in bump_initial_fields().items():
        files[f"0/{name}"] = text
    for rel, text in files.items():
        with (case / rel).open("w", newline="\n") as handle:
            handle.write(text)
    return case


def build_bump_summary(grids: list[dict[str, Any]]) -> dict[str, Any]:
    """Assemble the persisted bump summary from three completed records."""
    cd_conv = _convergence_block([g["cd"] for g in grids])
    cf_conv = _convergence_block([g["cf_station"] for g in grids])
    fine = grids[-1]
    ref_fine = CFL3D_BUMP_SST[fine["cells"]]
    comparison: dict[str, Any] = {
        "cfl3d_cd_ladder": [CFL3D_BUMP_SST[g["cells"]]["cd"] for g in grids],
        "cfl3d_cf075_ladder": [CFL3D_BUMP_SST[g["cells"]]["cf075"]
                               for g in grids],
        "fun3d_cd_ladder": [FUN3D_BUMP_SST[g["cells"]]["cd"] for g in grids],
        "cfl3d_cd_finest": CFL3D_BUMP_SST[901120]["cd"],
        "cfl3d_cf075_finest": CFL3D_BUMP_SST[901120]["cf075"],
        "fun3d_cd_finest": FUN3D_BUMP_SST[901120]["cd"],
        "cfl3d_observed_order_same_rungs": observed_order(
            *[CFL3D_BUMP_SST[g["cells"]]["cd"] for g in grids]),
        "cd_fine_vs_cfl3d_same_grid_pct":
            100.0 * (fine["cd"] / ref_fine["cd"] - 1.0),
        "cf075_fine_vs_cfl3d_same_grid_pct":
            100.0 * (fine["cf_station"] / ref_fine["cf075"] - 1.0),
    }
    if "cd_pressure" in fine:
        comparison["cd_pressure_fine_vs_cfl3d_same_grid_pct"] = (
            100.0 * (fine["cd_pressure"] / ref_fine["cdp"] - 1.0))
        comparison["cd_viscous_fine_vs_cfl3d_same_grid_pct"] = (
            100.0 * (fine["cd_viscous"] / ref_fine["cdv"] - 1.0))
    if cd_conv.get("richardson") is not None:
        comparison["cd_extrapolate_vs_cfl3d_finest_pct"] = 100.0 * (
            cd_conv["richardson"] / comparison["cfl3d_cd_finest"] - 1.0)
    if cf_conv.get("richardson") is not None:
        comparison["cf075_extrapolate_vs_cfl3d_finest_pct"] = 100.0 * (
            cf_conv["richardson"] / comparison["cfl3d_cf075_finest"] - 1.0)
    return {
        "case": "TMR 2D bump-in-channel",
        "model": "k-omega SST (OpenFOAM kOmegaSST, strain production)",
        "solver": "simpleFoam, incompressible, OpenFOAM v2606",
        "conditions": {
            "re_per_unit_length": U_INF / BUMP_NU,
            "wall_length": BUMP_WALL_LENGTH,
            "mach_reference": MACH,
            "k_inf": K_INF, "omega_inf": BUMP_OMEGA_INF,
            "eddy_viscosity_ratio_inf": BUMP_NUT_INF / BUMP_NU,
        },
        "grids": [{k: v for k, v in g.items() if k != "cf_profile"}
                  for g in grids],
        "convergence": {"cd": cd_conv, "cf_station": cf_conv},
        "cf_station_x": BUMP_CF_STATION,
        "comparison": comparison,
        "reference_source": BUMP_REFERENCE_SOURCE,
        "numerics": ("Second-order linearUpwind momentum advection, "
                     "first-order upwind advection on k and omega, "
                     "second-order diffusion throughout"),
        "deviations": [
            "Incompressible simpleFoam analog of the M=0.2 case; TMR notes "
            "incompressible codes land close but not identical",
            "The TMR bump data is labeled SST; OpenFOAM's kOmegaSST is the "
            "2003 strain-production form, so a small model-variant gap can "
            "remain",
            "Grids match TMR cell counts and refinement factor 2 with this "
            "module's own blockMesh stretching, not the TMR point files",
            "The bump surface enters blockMesh as a 480-segment polyLine, "
            "far finer than any cell, rather than an analytic surface",
        ],
        "generated_unix": int(time.time()),
    }


def format_bump_summary_lines(summary: dict[str, Any]) -> list[str]:
    """Human summary of the bump ladder, same product rules as the plate."""
    lines = [
        "NASA TMR bump-in-channel verification, k-omega SST, "
        "3-grid ladder (turbmodels.larc.nasa.gov)",
    ]
    for grid in summary["grids"]:
        split = ""
        if "cd_pressure" in grid:
            split = (f" (pressure {grid['cd_pressure']:.6f}, "
                     f"viscous {grid['cd_viscous']:.6f})")
        lines.append(
            f"Grid {grid['tmr_nodes']} ({grid['cells']} cells): "
            f"Cd = {grid['cd']:.6f}{split}, "
            f"Cf(x=0.75) = {grid['cf_station']:.6f}, "
            f"max y+ = {grid['yplus']['max']:.2f}, "
            f"{grid['iterations']} iterations in {grid['wall_seconds']:.0f} s")
    ref_order = summary["comparison"].get("cfl3d_observed_order_same_rungs")
    for key, label in (("cd", "Cd"), ("cf_station", "Cf(x=0.75)")):
        conv = summary["convergence"][key]
        if conv.get("observed_order") is not None:
            note = (f" (CFL3D's own order on these three rungs: "
                    f"{ref_order:.2f})" if key == "cd" and ref_order else "")
            lines.append(
                f"{label}: observed order {conv['observed_order']:.2f}{note}, "
                f"Richardson extrapolate {conv['richardson']:.6f}")
        else:
            lines.append(f"{label}: sequence not monotone, "
                         "no order or extrapolate is quoted")
    comp = summary["comparison"]
    ladder = ", ".join(f"{value:.6f}" for value in comp["cfl3d_cd_ladder"])
    lines.append(
        f"Reference: CFL3D SST on the same three grid sizes gives Cd "
        f"{ladder}; finest-grid (1409x641) Cd = "
        f"{comp['cfl3d_cd_finest']:.6f} and Cf(x=0.75) = "
        f"{comp['cfl3d_cf075_finest']:.6f} ({summary['reference_source']})")
    for deviation in summary["deviations"]:
        lines.append(f"Deviation: {deviation}")
    return lines


def _bump_figures(grids: list[dict[str, Any]], summary: dict[str, Any],
                  out_dir: Path) -> list[str]:
    """Bump Cf-profile and Cd-convergence figures, control-room themed."""
    from chief_engineer import plot_theme as _t
    plt = _t._pyplot()
    if plt is None:
        return []
    made: list[str] = []
    shades = [_t.DIM, _t.MUTED, _t.LIVE]

    fig, ax = plt.subplots(figsize=(11.4, 4.6), dpi=150)
    for grid, color in zip(grids, shades):
        xs = [p[0] for p in grid["cf_profile"]]
        cfs = [p[1] for p in grid["cf_profile"]]
        ax.plot(xs, cfs, color=color, linewidth=1.8,
                label=f"{grid['tmr_nodes']} ({grid['cells']} cells)")
    ref = CFL3D_BUMP_SST[901120]["cf075"]
    ax.scatter([BUMP_CF_STATION], [ref], s=110, color=_t.VALID, zorder=5,
               edgecolor=_t.INK, linewidth=1.2,
               label="CFL3D SST, 1409x641 grid, x=0.75")
    ax.annotate(
        f"CFL3D {ref:.5f}\nours (fine) {grids[-1]['cf_station']:.5f}",
        xy=(BUMP_CF_STATION, ref), xytext=(-14, -46),
        textcoords="offset points", ha="right", fontsize=11,
        color=_t.INK, weight="bold")
    ax.set_xlim(0, BUMP_WALL_LENGTH)
    _t.style_axes(ax, r"$x$ along the wall [m]", r"$C_f$",
                  "TMR bump-in-channel, k-omega SST: wall skin friction "
                  "by grid (ref. turbmodels.larc.nasa.gov)")
    leg = ax.legend(frameon=False, fontsize=10.5, loc="upper left")
    for text in leg.get_texts():
        text.set_color(_t.INK)
    fig.tight_layout()
    path = out_dir / "bump_cf_profiles.png"
    fig.savefig(path)
    plt.close(fig)
    made.append(str(path))

    fig, ax = plt.subplots(figsize=(11.4, 4.6), dpi=150)
    ours_h = [math.sqrt(1.0 / g["cells"]) for g in grids]
    ax.plot(ours_h, [g["cd"] for g in grids], color=_t.LIVE, linewidth=2.2,
            marker="o", markersize=7, markeredgecolor=_t.INK,
            label="This lab")
    for source, data, color in (("CFL3D SST", CFL3D_BUMP_SST, _t.VALID),
                                ("FUN3D SST", FUN3D_BUMP_SST, _t.TREND)):
        cells = sorted(data)
        ax.plot([math.sqrt(1.0 / n) for n in cells],
                [data[n]["cd"] for n in cells], color=color, linewidth=1.6,
                marker="s", markersize=5, linestyle=(0, (4, 3)), label=source)
    rich = summary["convergence"]["cd"].get("richardson")
    if rich is not None:
        ax.scatter([0.0], [rich], s=120, color=_t.LIVE, marker="D",
                   edgecolor=_t.INK, linewidth=1.2, zorder=5,
                   label="Richardson extrapolate (ours)")
        ax.annotate(f"h=0 extrapolate {rich:.5f}", xy=(0.0, rich),
                    xytext=(10, 14), textcoords="offset points",
                    fontsize=11, color=_t.INK, weight="bold")
    _t.style_axes(ax, r"$h = \sqrt{1/N}$", r"$C_D$ (wall, Aref = 1.5)",
                  "TMR bump-in-channel: drag-coefficient grid convergence "
                  "vs published CFL3D and FUN3D ladders")
    leg = ax.legend(frameon=False, fontsize=10.5, loc="upper left")
    for text in leg.get_texts():
        text.set_color(_t.INK)
    fig.tight_layout()
    path = out_dir / "bump_cd_convergence.png"
    fig.savefig(path)
    plt.close(fig)
    made.append(str(path))
    return made


def persist_bump_ladder(grids: list[dict[str, Any]], out_dir: Path,
                        log: Callable[[str], None] = print) -> dict[str, Any]:
    """Summary, figures, and JSON persistence for the bump ladder."""
    out_dir = Path(out_dir)
    summary = build_bump_summary(grids)
    summary["plots"] = [Path(p).name
                        for p in _bump_figures(grids, summary, out_dir)]
    with (out_dir / "bump_sst.json").open("w", newline="\n") as handle:
        json.dump(summary, handle, indent=2)
    profiles = {g["level"]: g["cf_profile"] for g in grids}
    with (out_dir / "bump_cf_profiles.json").open("w", newline="\n") as handle:
        json.dump(profiles, handle)
    for line in format_bump_summary_lines(summary):
        log(f"[tmr-bump] {line}")
    return summary


# ---------------------------------------------------------------------------
# Card text and agenda proposals
# ---------------------------------------------------------------------------

def card_update(flat_summary: dict[str, Any],
                bump_summary: dict[str, Any] | None) -> dict[str, str] | None:
    """Status and entry text for the research-challenge card.

    Owner's rules: no method or model names on a card, no em dashes, no
    banned words, nothing described as anything but the measured result.
    Returns None when even the flat plate is not defensible; falls back to
    the flat-plate-only wording when the bump is missing or not defensible.
    """
    flat_ok = (len(flat_summary.get("grids", ())) >= 3 and
               flat_summary["convergence"]["cd"].get("observed_order")
               is not None)
    if not flat_ok:
        return None
    bump_ok = bool(
        bump_summary and len(bump_summary.get("grids", ())) >= 3
        and bump_summary["convergence"]["cd"].get("observed_order") is not None)
    flat_fine = flat_summary["grids"][-1]
    if not bump_ok:
        return {"status": "flat plate measured",
                "entry": card_entry_text(flat_summary) or ""}
    bump_fine = bump_summary["grids"][-1]
    entry = (
        f"flat plate and bump-in-channel each run on a 3-grid ladder "
        f"against the published CFL3D values: flat-plate Cd "
        f"{flat_fine['cd']:.6f} vs {CFL3D_SST_V[flat_fine['cells']]['cd']:.6f} "
        f"at matched grid size, bump Cd {bump_fine['cd']:.6f} vs "
        f"{CFL3D_BUMP_SST[bump_fine['cells']]['cd']:.6f}; "
        f"NACA 0012 airfoil next")
    lowered = entry.lower()
    if any(word in lowered for word in BANNED_CARD_WORDS) or "--" in entry:
        raise ValueError("card text violates product language rules")
    return {"status": "flat plate and bump measured", "entry": entry}


def _ladder_core_minutes(summary: dict[str, Any]) -> float:
    return sum(g["wall_seconds"] for g in summary["grids"]) / 60.0


def build_proposals(flat_summary: dict[str, Any],
                    bump_summary: dict[str, Any]) -> list[dict[str, Any]]:
    """The two next-step agenda proposals, with compute estimates anchored to
    the wall clocks these ladders actually measured tonight."""
    created = time.strftime("%Y-%m-%dT%H:%M:%S")
    flat_min = _ladder_core_minutes(flat_summary)
    bump_min = _ladder_core_minutes(bump_summary)

    # NACA 0012: three coarsest TMR C-grid rungs are the same cell-count
    # scale as the bump rungs; three angles of attack (0, 10, 15 deg), with
    # headroom for slower convergence at high lift.
    naca_est = int(round(3 * bump_min * 1.5)) + 1

    # Flat-plate finest grids: per-iteration cost measured on the fine rung,
    # scaled by cell count (4x, 16x) with iteration counts growing with the
    # wall-normal count (2x, 4x) as observed across tonight's rungs.
    fine = flat_summary["grids"][-1]
    seconds_per_iter = fine["timings"]["simpleFoam"] / fine["iterations"]
    finest_est = int(round(
        (4 * 2 + 16 * 4) * seconds_per_iter * fine["iterations"] / 60.0)) + 1

    return [
        {
            "id": "tmr-naca0012-verification",
            "objective": "Run the TMR 2D NACA 0012 airfoil case on the three "
                         "coarsest reference grid sizes at 0, 10, and 15 "
                         "degrees and compare lift, drag, and surface "
                         "pressure against the published CFL3D and FUN3D "
                         "values",
            "rationale": "The flat-plate ladder landed within 0.3 percent of "
                         "the published value at matched grid size and the "
                         "bump within 1.1 percent; the NACA 0012 is the next "
                         "TMR case and the first with lift, adding a "
                         "genuinely new check on the pipeline",
            "citations": [
                "NASA Langley Turbulence Modeling Resource: 2D NACA 0012 "
                "airfoil validation case (turbmodels.larc.nasa.gov)",
                "TMR CFL3D and FUN3D reference ladders "
                "(tmbwg.github.io/turbmodels)",
            ],
            "est_core_min": naca_est,
            "expected_knowledge_gain": "First lifting-body verification "
                                       "anchor; establishes whether the "
                                       "lab's ladder discipline holds when "
                                       "pressure drag dominates friction",
            "source_kind": "challenge",
            "status": "proposed",
            "created_at": created,
            "launch_prompt": "Extend sdk/workflows/tmr_verification.py with "
                             "the TMR 2D NACA 0012 case: download the "
                             "reference convergence data live from "
                             "tmbwg.github.io/turbmodels, build a C-grid or "
                             "O-grid ladder matching the three coarsest "
                             "reference cell counts, run alpha 0, 10, 15 "
                             "degrees to steady convergence, extract Cl, Cd, "
                             "and Cp, report observed order and Richardson "
                             "extrapolates, and state every deviation "
                             "plainly. Refuse any comparison you cannot "
                             "defend.",
        },
        {
            "id": "tmr-flatplate-finest-grids",
            "objective": "Extend the measured flat-plate ladder to the two "
                         "finest TMR grids (273x193 and 545x385) so the "
                         "extrapolation is anchored in the asymptotic range",
            "rationale": f"Tonight's three rungs cost "
                         f"{flat_min + bump_min:.1f} core-minutes in total "
                         f"and reached about 1 percent of the finest-grid "
                         f"reference; the two finest rungs would close most "
                         f"of that gap and give the observed order room to "
                         f"approach 2",
            "citations": [
                "NASA Langley Turbulence Modeling Resource: 2D "
                "zero-pressure-gradient flat plate (turbmodels.larc.nasa.gov)",
                "TMR SST-V convergence data files "
                "(tmbwg.github.io/turbmodels)",
            ],
            "est_core_min": finest_est,
            "expected_knowledge_gain": "Asymptotic-range verification of the "
                                       "wall treatment and convection "
                                       "discretization; a defensible "
                                       "infinite-grid drag number",
            "source_kind": "challenge",
            "status": "proposed",
            "created_at": created,
            "launch_prompt": "Using sdk/workflows/tmr_verification.py as is, "
                             "add 273x193 and 545x385 rungs to LEVELS with "
                             "the same fixed gradings, run them when the "
                             "machine is quiet (the finest rung is hours, "
                             "not minutes), and extend "
                             "demo-output/website/tmr/flatplate_sst.json "
                             "and the figures with the five-rung ladder.",
        },
    ]


def write_proposals(proposals: list[dict[str, Any]],
                    out_dir: str | Path | None = None) -> list[str]:
    """Write each proposal to demo-output/website/agenda/proposals/<id>.json."""
    target = Path(out_dir) if out_dir else (
        _REPO_ROOT / "demo-output" / "website" / "agenda" / "proposals")
    target.mkdir(parents=True, exist_ok=True)
    written = []
    for proposal in proposals:
        path = target / f"{proposal['id']}.json"
        with path.open("w", newline="\n") as handle:
            json.dump(proposal, handle, indent=2)
        written.append(str(path))
    return written


# ---------------------------------------------------------------------------
# NACA 0012: the third TMR case, first with lift
# ---------------------------------------------------------------------------
# TMR spec (tmbwg.github.io/turbmodels/naca0012_val.html): the sharp-TE
# modified NACA 0012 (equation below, closes exactly at x=1), Re = 6 million
# per chord, M = 0.15, farfield close to 500 chords away (or a point-vortex
# farfield correction). Reference values are the published CFL3D and FUN3D
# results on the finest 897x257 grid; no SST per-grid ladder is published,
# so matched-size comparisons are NOT claimed for this case: our ladder
# reports its own observed order and Richardson value against the published
# finest-grid numbers, with the deviations stated.

NACA_NU = 1.0 / 6.0e6                             # Re per chord = 6e6
_A_NACA = U_INF / 0.15                            # a at the case's M = 0.15
NACA_K_INF = 9.0e-9 * _A_NACA ** 2                # 4.0e-7
NACA_OMEGA_INF = 1.0e-6 * _A_NACA ** 2 / NACA_NU  # 266.67
NACA_NUT_INF = NACA_K_INF / NACA_OMEGA_INF        # 0.009 nu again
NACA_R = 500.0                                    # farfield radius, chords
NACA_WAKE = 500.0                                 # wake block length
NACA_ALPHAS = (10.0, 0.0, 15.0)                   # priority order: lift first

NACA_REFERENCE_SOURCE = (
    "turbmodels.larc.nasa.gov NACA 0012 validation, CFL3D SST on the "
    "897x257 grid with point-vortex farfield correction "
    "(n0012clcd_cfl3d_sst.dat via mirror tmbwg.github.io/turbmodels, "
    "retrieved 2026-07-25); FUN3D values from the same validation page")

# Published finest-grid (897x257) values. CFL3D from the data file; FUN3D
# quoted on the validation page. Keyed by alpha in degrees.
CFL3D_NACA_SST = {
    0.0:  {"cl": -0.76275807991e-5, "cd": 0.80937292380e-2},
    10.0: {"cl": 1.0778080613, "cd": 1.2362110998e-2},
    15.0: {"cl": 1.5067867358, "cd": 2.2186245406e-2},
}
FUN3D_NACA_SST = {
    0.0:  {"cl": 0.0, "cd": 0.00808},
    10.0: {"cl": 1.0840, "cd": 0.01253},
    15.0: {"cl": 1.5109, "cd": 0.02275},
}


@dataclass(frozen=True)
class NacaGridLevel:
    name: str
    tmr_nodes: str
    n_surf_quarter: int   # cells per quarter surface (4 quarters total)
    n_wake: int           # wake cells each side of the cut
    ny: int               # wall-normal cells

    @property
    def nx_total(self) -> int:
        return 4 * self.n_surf_quarter + 2 * self.n_wake

    @property
    def cells(self) -> int:
        return self.nx_total * self.ny


NACA_LEVELS = (
    NacaGridLevel("coarse", "113x33", 16, 24, 32),
    NacaGridLevel("medium", "225x65", 32, 48, 64),
    NacaGridLevel("fine", "449x129", 64, 96, 128),
)

NACA_ITERATIONS = {"coarse": 5000, "medium": 8000, "fine": 12000}

# Family gradings, fixed across levels. Surface: expansion away from the
# leading edge and contraction into the trailing edge (the two mid-chord
# block boundaries make every airfoil face's vertex set unique, which
# blockMesh needs to tell the upper surface from the lower). Wall-normal
# first cell ~6e-6 chords on the coarse rung (y+ under 1); the wake grows
# from the trailing-edge streamwise spacing out to 500 chords.
# The nose radius is 0.016 chords; the first pilot with E_LE = 10 left a
# coarse-rung leading-edge cell wrapping a third of the nose and the solve
# detonated from the stagnation column. E_LE = 50 puts the coarse LE cell at
# ~0.002 chords.
NACA_E_LE = 50.0      # mid-chord to leading-edge spacing ratio
NACA_E_TE = 4.0       # mid-chord to trailing-edge spacing ratio
R_Y_NACA = ratio_for_first_cell(NACA_R, 32, 6.0e-6)
# The wake cut must not carry wall-level clustering 500 chords downstream:
# that gave 1.4e-8-volume cells of aspect 2.8e7 at the outflow and the
# pressure matrix was unsolvable (GAMG stalled on a bare Laplacian there).
# The far end of the wake relaxes to ~0.3-chord first spacing instead; the
# per-edge grading below tapers between the two.
R_Y_FAR = ratio_for_first_cell(NACA_R, 32, 0.3)


def naca_thickness(x: float) -> float:
    """The TMR sharp-trailing-edge NACA 0012 half thickness; exactly zero at
    both x=0 and x=1 (the quartic coefficient closes the trailing edge)."""
    if x <= 0.0:
        return 0.0
    return 0.594689181 * (0.298222773 * math.sqrt(x) - 0.127125232 * x
                          - 0.357907906 * x ** 2 + 0.291984971 * x ** 3
                          - 0.105174606 * x ** 4)


def naca_surface_points(x_lo: float, x_hi: float, sign: float,
                        n: int = 240) -> list[tuple[float, float]]:
    """Interior points of one surface segment, cosine-clustered toward both
    segment ends so the polyLine is densest where curvature lives."""
    points = []
    for i in range(1, n):
        t = 0.5 * (1.0 - math.cos(math.pi * i / n))
        x = x_lo + (x_hi - x_lo) * t
        points.append((x, sign * naca_thickness(x)))
    return points


def _naca_wake_ratio(level_coarse: NacaGridLevel = None) -> float:
    """Total wake expansion so the first wake cell matches the trailing-edge
    streamwise spacing of the coarse family member (fixed across levels)."""
    lv = NACA_LEVELS[0]
    # Upper-rear quarter: length ~ surface arc of [0.5, 1], graded 1/E_TE.
    seg = 0.502
    r = (1.0 / NACA_E_TE) ** (1.0 / (lv.n_surf_quarter - 1))
    first = seg * (r - 1.0) / (r ** lv.n_surf_quarter - 1.0)
    te_spacing = first * r ** (lv.n_surf_quarter - 1)
    return ratio_for_first_cell(NACA_WAKE, lv.n_wake, te_spacing)


R_WAKE_NACA = _naca_wake_ratio()


def naca_blockmesh_dict(level: NacaGridLevel) -> str:
    R, W = NACA_R, 1.0 + NACA_WAKE
    ym = naca_thickness(0.5)
    c45 = R / math.sqrt(2.0)

    def arc_point(deg: float) -> str:
        rad = math.radians(deg)
        return f"({1.0 + R * math.cos(rad):.10g} {R * math.sin(rad):.10g}"

    def edge(kind: str, a: int, b: int, payload: str) -> str:
        return f"    {kind} {a} {b} {payload}"

    def poly(points: list[tuple[float, float]], z: float) -> str:
        inner = "\n".join(f"        ({x:.10g} {y:.10g} {z})"
                          for x, y in points)
        return f"(\n{inner}\n    )"

    up_front = naca_surface_points(0.0, 0.5, +1.0)
    up_rear = naca_surface_points(0.5, 1.0, +1.0)
    lo_front = naca_surface_points(0.0, 0.5, -1.0)
    lo_rear = naca_surface_points(0.5, 1.0, -1.0)
    ns, nw, ny = level.n_surf_quarter, level.n_wake, level.ny
    e_le, e_te = NACA_E_LE, NACA_E_TE

    lines = [_foam_header("dictionary", "blockMeshDict", "system"), """
scale   1;

vertices
("""]
    base = [
        (1.0, 0.0),                    # 0 TE
        (0.0, 0.0),                    # 1 LE
        (0.5, ym),                     # 2 mid upper
        (0.5, -ym),                    # 3 mid lower
        (1.0 - R, 0.0),                # 4 arc left (180 deg)
        (1.0 - c45, c45),              # 5 arc 135 deg
        (1.0, R),                      # 6 arc top (90 deg)
        (1.0 - c45, -c45),             # 7 arc 225 deg
        (1.0, -R),                     # 8 arc bottom (270 deg)
        (W, 0.0),                      # 9 wake end, cut line
        (W, R),                        # 10 wake end top
        (W, -R),                       # 11 wake end bottom
    ]
    for z in (0, 1):
        for i, (x, y) in enumerate(base):
            lines.append(f"    ({x:.10g} {y:.10g} {z})   // {i + 12 * z}")
    lines.append(f""");

blocks
(
    // upper front: LE to mid-chord, fine at the leading edge
    hex (1 2 5 4 13 14 17 16) ({ns} {ny} 1)
        simpleGrading ({e_le:.8g} {R_Y_NACA:.8g} 1)
    // upper rear: mid-chord to TE, contracting into the trailing edge
    hex (2 0 6 5 14 12 18 17) ({ns} {ny} 1)
        simpleGrading ({1.0 / e_te:.8g} {R_Y_NACA:.8g} 1)
    // lower rear: TE to mid-chord, fine at the trailing edge
    hex (0 3 7 8 12 15 19 20) ({ns} {ny} 1)
        simpleGrading ({e_te:.8g} {R_Y_NACA:.8g} 1)
    // lower front: mid-chord to LE, contracting into the leading edge
    hex (3 1 4 7 15 13 16 19) ({ns} {ny} 1)
        simpleGrading ({1.0 / e_le:.8g} {R_Y_NACA:.8g} 1)
    // upper wake: wall-level cut clustering at the TE edge tapering to a
    // mild far-end distribution (per-edge grading, y-edge order 0-3 1-2 5-6 4-7)
    hex (0 9 10 6 12 21 22 18) ({nw} {ny} 1)
        edgeGrading ({R_WAKE_NACA:.8g} {R_WAKE_NACA:.8g} {R_WAKE_NACA:.8g} {R_WAKE_NACA:.8g}
                     {R_Y_NACA:.8g} {R_Y_FAR:.8g} {R_Y_FAR:.8g} {R_Y_NACA:.8g}
                     1 1 1 1)
    // lower wake
    hex (9 0 8 11 21 12 20 23) ({nw} {ny} 1)
        edgeGrading ({1.0 / R_WAKE_NACA:.8g} {1.0 / R_WAKE_NACA:.8g} {1.0 / R_WAKE_NACA:.8g} {1.0 / R_WAKE_NACA:.8g}
                     {R_Y_FAR:.8g} {R_Y_NACA:.8g} {R_Y_NACA:.8g} {R_Y_FAR:.8g}
                     1 1 1 1)
);

edges
(""")
    for z, off in ((0.0, 0), (1.0, 12)):
        lines.append(edge("polyLine", 1 + off, 2 + off, poly(up_front, z)))
        lines.append(edge("polyLine", 2 + off, 0 + off, poly(up_rear, z)))
        lines.append(edge("polyLine", 0 + off, 3 + off, poly(lo_rear[::-1], z)))
        lines.append(edge("polyLine", 3 + off, 1 + off, poly(lo_front[::-1], z)))
        for a, b, deg in ((4, 5, 157.5), (5, 6, 112.5),
                          (8, 7, 247.5), (7, 4, 202.5)):
            lines.append(edge("arc", a + off, b + off,
                              f"{arc_point(deg)} {z:g})"))
    lines.append(f""");

boundary
(
    airfoil
    {{
        type wall;
        faces ((1 2 14 13) (2 0 12 14) (0 3 15 12) (3 1 13 15));
    }}
    // The far boundary is split geometrically so the flow always has hard
    // anchors: Dirichlet velocity on the upstream arc and the lower plane
    // (inflow for alpha >= 0), Dirichlet pressure on the top and downstream
    // planes (outflow). A single all-freestream boundary left the pressure
    // level flapping and the solve never settled (measured on the pilot).
    inflow
    {{
        type patch;
        faces
        (
            (4 5 17 16) (5 6 18 17) (8 7 19 20) (7 4 16 19)
            (11 8 20 23)
        );
    }}
    outflow
    {{
        type patch;
        faces ((6 10 22 18) (9 10 22 21) (9 11 23 21));
    }}
    frontAndBack
    {{
        type empty;
        faces
        (
            (1 2 5 4) (2 0 6 5) (0 3 7 8) (3 1 4 7)
            (0 9 10 6) (9 0 8 11)
            (13 14 17 16) (14 12 18 17) (12 15 19 20) (15 13 16 19)
            (12 21 22 18) (21 12 20 23)
        );
    }}
);
""")
    return "\n".join(lines)


def naca_initial_fields(alpha_deg: float) -> dict[str, str]:
    """0/ files for the airfoil case; the angle of attack lives in the
    freestream velocity vector, the grid never rotates."""
    rad = math.radians(alpha_deg)
    u_vec = f"({math.cos(rad):.8f} {math.sin(rad):.8f} 0)"
    empty = "        type            empty;\n"

    def bc(*lines: str) -> str:
        return "".join(f"        {line}\n" for line in lines)

    u = _field("volVectorField", "U", "[0 1 -1 0 0 0 0]",
               f"uniform {u_vec}", {
                   "inflow": bc("type            fixedValue;",
                                f"value           uniform {u_vec};"),
                   "outflow": bc("type            inletOutlet;",
                                 f"inletValue      uniform {u_vec};",
                                 f"value           uniform {u_vec};"),
                   "airfoil": bc("type            noSlip;"),
                   "frontAndBack": empty,
               })
    # Pressure is pinned on the WHOLE outer boundary, inflow included. With
    # the anchor only on the outflow planes, the front C-region's pressure
    # level floated (its own boundaries are all Neumann) and the solve
    # blew up as a front-versus-wake seesaw within 300 iterations; anchoring
    # everywhere killed it dead (measured on the alpha 0 probe). At 500
    # chords a uniform p is the same approximation the stated point-vortex
    # deviation already covers.
    p = _field("volScalarField", "p", "[0 2 -2 0 0 0 0]", "uniform 0", {
        "inflow": bc("type            fixedValue;",
                     "value           uniform 0;"),
        "outflow": bc("type            fixedValue;",
                      "value           uniform 0;"),
        "airfoil": bc("type            zeroGradient;"),
        "frontAndBack": empty,
    })
    k = _field("volScalarField", "k", "[0 2 -2 0 0 0 0]",
               f"uniform {NACA_K_INF:.8g}", {
                   "inflow": bc("type            fixedValue;",
                                f"value           uniform {NACA_K_INF:.8g};"),
                   "outflow": bc("type            inletOutlet;",
                                 f"inletValue      uniform {NACA_K_INF:.8g};",
                                 f"value           uniform {NACA_K_INF:.8g};"),
                   "airfoil": bc("type            kLowReWallFunction;",
                                 "value           uniform 1e-12;"),
                   "frontAndBack": empty,
               })
    omega = _field("volScalarField", "omega", "[0 0 -1 0 0 0 0]",
                   f"uniform {NACA_OMEGA_INF:.8g}", {
                       "inflow": bc("type            fixedValue;",
                                    f"value           uniform {NACA_OMEGA_INF:.8g};"),
                       "outflow": bc(
                           "type            inletOutlet;",
                           f"inletValue      uniform {NACA_OMEGA_INF:.8g};",
                           f"value           uniform {NACA_OMEGA_INF:.8g};"),
                       "airfoil": bc("type            omegaWallFunction;",
                                     "blended         true;",
                                     f"value           uniform {NACA_OMEGA_INF:.8g};"),
                       "frontAndBack": empty,
                   })
    nut = _field("volScalarField", "nut", "[0 2 -1 0 0 0 0]",
                 f"uniform {NACA_NUT_INF:.8g}", {
                     "inflow": bc("type            calculated;",
                                  "value           uniform 0;"),
                     "outflow": bc("type            calculated;",
                                   "value           uniform 0;"),
                     "airfoil": bc("type            nutLowReWallFunction;",
                                   "value           uniform 0;"),
                     "frontAndBack": empty,
                 })
    return {"U": u, "p": p, "k": k, "omega": omega, "nut": nut}


def write_naca_case(root: Path, level: NacaGridLevel,
                    alpha_deg: float) -> Path:
    """Write the complete airfoil case for one rung at one angle of attack."""
    rad = math.radians(alpha_deg)
    case = Path(root) / f"a{alpha_deg:g}" / level.name
    for sub in ("0", "constant", "system"):
        (case / sub).mkdir(parents=True, exist_ok=True)
    files = {
        "system/blockMeshDict": naca_blockmesh_dict(level),
        "system/controlDict": control_dict(
            NACA_ITERATIONS.get(level.name, 10000), patch="airfoil",
            lref=1.0, aref=1.0,
            drag_dir=f"({math.cos(rad):.8f} {math.sin(rad):.8f} 0)",
            lift_dir=f"({-math.sin(rad):.8f} {math.cos(rad):.8f} 0)"),
        "system/fvSchemes": fv_schemes(limited=True),
        "system/fvSolution": fv_solution(non_orth_correctors=1, relax_p=0.25,
                                         relax_u=0.6, potential=True,
                                         p_solver="PCG"),
        "constant/transportProperties": transport_properties(NACA_NU),
        "constant/turbulenceProperties": turbulence_properties(),
    }
    for name, text in naca_initial_fields(alpha_deg).items():
        files[f"0/{name}"] = text
    for rel, text in files.items():
        with (case / rel).open("w", newline="\n") as handle:
            handle.write(text)
    return case


def build_naca_summary(alpha_deg: float,
                       grids: list[dict[str, Any]]) -> dict[str, Any]:
    """Per-alpha summary. There is no published SST per-grid ladder for this
    case, so the comparison quotes the published finest-grid (897x257)
    values and never claims a matched-size agreement."""
    cd_conv = _convergence_block([g["cd"] for g in grids])
    blocks = {"cd": cd_conv}
    lifting = abs(alpha_deg) > 1e-9
    if lifting:
        blocks["cl"] = _convergence_block([g["cl"] for g in grids])
    ref_c, ref_f = CFL3D_NACA_SST[alpha_deg], FUN3D_NACA_SST[alpha_deg]
    fine = grids[-1]
    comparison: dict[str, Any] = {
        "cfl3d_finest_cl": ref_c["cl"], "cfl3d_finest_cd": ref_c["cd"],
        "fun3d_finest_cl": ref_f["cl"], "fun3d_finest_cd": ref_f["cd"],
        "published_grid": "897x257 (229376 cells); our finest rung is "
                          f"{fine['tmr_nodes']} ({fine['cells']} cells)",
        "cd_fine_vs_cfl3d_finest_pct":
            100.0 * (fine["cd"] / ref_c["cd"] - 1.0),
    }
    if lifting:
        comparison["cl_fine_vs_cfl3d_finest_pct"] = (
            100.0 * (fine["cl"] / ref_c["cl"] - 1.0))
        if blocks["cl"].get("richardson") is not None:
            comparison["cl_extrapolate_vs_cfl3d_finest_pct"] = 100.0 * (
                blocks["cl"]["richardson"] / ref_c["cl"] - 1.0)
    if cd_conv.get("richardson") is not None:
        comparison["cd_extrapolate_vs_cfl3d_finest_pct"] = 100.0 * (
            cd_conv["richardson"] / ref_c["cd"] - 1.0)
    return {
        "case": "TMR NACA 0012 airfoil validation",
        "alpha_deg": alpha_deg,
        "model": "k-omega SST (OpenFOAM kOmegaSST, strain production)",
        "solver": "simpleFoam, incompressible, OpenFOAM v2606",
        "conditions": {
            "re_per_chord": U_INF / NACA_NU, "mach_reference": 0.15,
            "k_inf": NACA_K_INF, "omega_inf": NACA_OMEGA_INF,
            "eddy_viscosity_ratio_inf": NACA_NUT_INF / NACA_NU,
            "farfield_chords": NACA_R,
        },
        "grids": [{k: v for k, v in g.items() if k != "cf_profile"}
                  for g in grids],
        "convergence": blocks,
        "comparison": comparison,
        "reference_source": NACA_REFERENCE_SOURCE,
        "numerics": ("Second-order linearUpwind momentum advection, "
                     "first-order upwind advection on k and omega, "
                     "second-order diffusion throughout"),
        "deviations": [
            "Incompressible simpleFoam analog of the M=0.15 case",
            "No point-vortex farfield correction; the farfield sits at 500 "
            "chords, the distance TMR recommends when the correction is off",
            "The published SST reference is finest-grid only (897x257), so "
            "no matched-size comparison exists for this case; our ladder "
            "reports its own observed order and Richardson value",
            "Grids are this module's own C-grid family at the TMR cell "
            "counts (3584, 14336, 57344), not the TMR point files; the "
            "transfinite blocks carry non-orthogonality up to 70 degrees, "
            "treated with limited gradients and a non-orthogonal corrector",
        ],
        "generated_unix": int(time.time()),
    }


def format_naca_summary_lines(summary: dict[str, Any]) -> list[str]:
    alpha = summary["alpha_deg"]
    lines = [
        f"NASA TMR NACA 0012 validation, alpha {alpha:g} degrees, "
        f"3-grid ladder (turbmodels.larc.nasa.gov)",
    ]
    lifting = "cl" in summary["convergence"]
    for grid in summary["grids"]:
        cl_part = f"Cl = {grid['cl']:.5f}, " if lifting else ""
        lines.append(
            f"Grid {grid['tmr_nodes']} ({grid['cells']} cells): "
            f"{cl_part}Cd = {grid['cd']:.6f}, "
            f"max y+ = {grid['yplus']['max']:.2f}, "
            f"{grid['iterations']} iterations in {grid['wall_seconds']:.0f} s")
    for key, label in (("cl", "Cl"), ("cd", "Cd")):
        conv = summary["convergence"].get(key)
        if conv is None:
            continue
        if conv.get("observed_order") is not None:
            lines.append(
                f"{label}: observed order {conv['observed_order']:.2f}, "
                f"Richardson extrapolate {conv['richardson']:.6f}")
        else:
            lines.append(f"{label}: sequence not monotone, "
                         "no order or extrapolate is quoted")
    comp = summary["comparison"]
    ref = (f"Cl {comp['cfl3d_finest_cl']:.5f} and " if lifting else "")
    lines.append(
        f"Reference: CFL3D SST on the published finest grid (897x257) gives "
        f"{ref}Cd {comp['cfl3d_finest_cd']:.6f}; our finest rung is 57344 "
        f"cells, a quarter of that grid, so this is not a matched-size "
        f"comparison ({summary['reference_source']})")
    for deviation in summary["deviations"]:
        lines.append(f"Deviation: {deviation}")
    return lines


def _naca_figure(alpha_deg: float, grids: list[dict[str, Any]],
                 summary: dict[str, Any], out_dir: Path) -> list[str]:
    """One ladder figure per alpha: Cd (and Cl when lifting) vs h with the
    published finest-grid values drawn as reference lines."""
    from chief_engineer import plot_theme as _t
    plt = _t._pyplot()
    if plt is None:
        return []
    lifting = "cl" in summary["convergence"]
    n_panels = 2 if lifting else 1
    fig, axes = plt.subplots(1, n_panels, figsize=(11.4, 4.6), dpi=150)
    axes = axes if n_panels > 1 else [axes]
    hs = [math.sqrt(1.0 / g["cells"]) for g in grids]
    panels = [("cd", r"$C_D$", "cfl3d_finest_cd", "fun3d_finest_cd")]
    if lifting:
        panels.append(("cl", r"$C_\ell$", "cfl3d_finest_cl",
                       "fun3d_finest_cl"))
    for ax, (key, label, ref_c, ref_f) in zip(axes, panels):
        ax.plot(hs, [g[key] for g in grids], color=_t.LIVE, linewidth=2.2,
                marker="o", markersize=7, markeredgecolor=_t.INK,
                label="This lab")
        ax.axhline(summary["comparison"][ref_c], color=_t.VALID,
                   linewidth=1.6, linestyle=(0, (4, 3)),
                   label="CFL3D, 897x257")
        ax.axhline(summary["comparison"][ref_f], color=_t.TREND,
                   linewidth=1.6, linestyle=(0, (2, 3)),
                   label="FUN3D, 897x257")
        rich = summary["convergence"][key].get("richardson")
        if rich is not None:
            ax.scatter([0.0], [rich], s=120, color=_t.LIVE, marker="D",
                       edgecolor=_t.INK, linewidth=1.2, zorder=5,
                       label="Richardson (ours)")
        _t.style_axes(ax, r"$h=\sqrt{1/N}$", label,
                      f"{label} ladder, alpha {alpha_deg:g} deg")
        leg = ax.legend(frameon=False, fontsize=9.5, loc="best")
        for text in leg.get_texts():
            text.set_color(_t.INK)
    fig.suptitle(f"TMR NACA 0012, alpha {alpha_deg:g} degrees: grid "
                 f"convergence vs published finest-grid values",
                 color=_t.INK, fontsize=13, weight="bold", x=0.02,
                 ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    path = out_dir / f"naca0012_a{alpha_deg:g}_convergence.png"
    fig.savefig(path)
    plt.close(fig)
    return [str(path)]


def persist_naca_ladder(alpha_deg: float, grids: list[dict[str, Any]],
                        out_dir: Path,
                        log: Callable[[str], None] = print) -> dict[str, Any]:
    out_dir = Path(out_dir)
    summary = build_naca_summary(alpha_deg, grids)
    summary["plots"] = [Path(p).name
                        for p in _naca_figure(alpha_deg, grids, summary,
                                              out_dir)]
    with (out_dir / f"naca0012_a{alpha_deg:g}_sst.json").open(
            "w", newline="\n") as handle:
        json.dump(summary, handle, indent=2)
    for line in format_naca_summary_lines(summary):
        log(f"[tmr-naca] {line}")
    return summary


# -- TMR-grid pipeline for the airfoil ---------------------------------------
# The self-built transfinite C-grid was abandoned after five pilot rounds:
# even stabilized, its coarse rung limit-cycled and could not anchor a
# defensible ladder. The TMR-distributed PLOT3D grids (the reference family
# itself) convert cleanly with plot3dToFoam; the wake cut stitches itself
# through the point merge, and autoPatch separates the boundary.

def parse_boundary_patches(text: str) -> dict[str, tuple[int, int]]:
    """Patch name -> (startFace, nFaces) from a polyMesh boundary file."""
    out: dict[str, tuple[int, int]] = {}
    for match in re.finditer(
            r"(\w+)\s*\{[^}]*?nFaces\s+(\d+);\s*startFace\s+(\d+);", text):
        out[match.group(1)] = (int(match.group(3)), int(match.group(2)))
    return out


def classify_naca_patches(points: list[tuple[float, float, float]],
                          faces: list[list[int]],
                          patches: dict[str, tuple[int, int]]
                          ) -> tuple[dict[str, str], float, int, int]:
    """Role of every boundary patch of a converted TMR C-grid, by geometry.

    The TMR files put the 2D plane wherever they like (the NACA family is
    chord x, LIFT along z, spanwise y), so the axes are discovered, never
    assumed: the spanwise axis is the one with the one-cell extent, the
    chord is x, the lift axis is the remaining one. Returns
    ({patch: airfoil|outer|frontAndBack|unused}, span thickness,
    lift_axis, span_axis).
    """
    ranges = [max(p[a] for p in points) - min(p[a] for p in points)
              for a in range(3)]
    span_axis = min(range(3), key=lambda a: ranges[a])
    lift_axis = next(a for a in (2, 1) if a != span_axis)
    span_lo = min(p[span_axis] for p in points)
    thickness = ranges[span_axis]
    roles: dict[str, str] = {}
    for name, (start, n_faces) in patches.items():
        if n_faces == 0:
            roles[name] = "unused"
            continue
        centre = [sum(c) / len(c) for c in zip(
            *(points[i] for i in faces[start]))]
        span_pos = centre[span_axis]
        if (abs(span_pos - span_lo) < 1e-6 * max(1.0, thickness)
                or abs(span_pos - span_lo - thickness)
                < 1e-6 * max(1.0, thickness)):
            roles[name] = "frontAndBack"
        elif -0.1 <= centre[0] <= 1.1 and abs(centre[lift_axis]) < 0.3:
            roles[name] = "airfoil"
        else:
            roles[name] = "outer"
    return roles, thickness, lift_axis, span_axis


def parse_polymesh_points_faces(points_text: str, faces_text: str
                                ) -> tuple[list[tuple[float, float, float]],
                                           list[list[int]]]:
    points = [tuple(float(v) for v in m.groups())
              for m in re.finditer(
                  r"\(([-0-9.eE+]+)\s+([-0-9.eE+]+)\s+([-0-9.eE+]+)\)",
                  points_text)]
    faces = [[int(v) for v in m.group(1).split()]
             for m in re.finditer(r"\d+\(([\d ]+)\)", faces_text)]
    return points, faces


def _axis_vector(chord: float, lift: float, lift_axis: int) -> str:
    """A vector with ``chord`` on x and ``lift`` on the discovered lift axis."""
    comp = [0.0, 0.0, 0.0]
    comp[0] = chord
    comp[lift_axis] = lift
    return f"({comp[0]:.8f} {comp[1]:.8f} {comp[2]:.8f})"


def naca_fields_tmr(alpha_deg: float, roles: dict[str, str],
                    lift_axis: int = 1) -> dict[str, str]:
    """0/ files keyed by field name for a converted TMR grid, with boundary
    entries generated from the discovered patch roles and axes."""
    rad = math.radians(alpha_deg)
    u_vec = _axis_vector(math.cos(rad), math.sin(rad), lift_axis)

    def bc(*lines: str) -> str:
        return "".join(f"        {line}\n" for line in lines)

    def build(role_bcs: dict[str, str]) -> dict[str, str]:
        return {name: role_bcs[role] for name, role in roles.items()}

    empty = "        type            empty;\n"
    unused = bc("type            zeroGradient;")
    u = _field("volVectorField", "U", "[0 1 -1 0 0 0 0]",
               f"uniform {u_vec}", build({
                   "outer": bc("type            inletOutlet;",
                               f"inletValue      uniform {u_vec};",
                               f"value           uniform {u_vec};"),
                   "airfoil": bc("type            noSlip;"),
                   "frontAndBack": empty, "unused": unused}))
    p = _field("volScalarField", "p", "[0 2 -2 0 0 0 0]", "uniform 0", build({
        "outer": bc("type            fixedValue;",
                    "value           uniform 0;"),
        "airfoil": bc("type            zeroGradient;"),
        "frontAndBack": empty, "unused": unused}))
    k = _field("volScalarField", "k", "[0 2 -2 0 0 0 0]",
               f"uniform {NACA_K_INF:.8g}", build({
                   "outer": bc("type            inletOutlet;",
                               f"inletValue      uniform {NACA_K_INF:.8g};",
                               f"value           uniform {NACA_K_INF:.8g};"),
                   "airfoil": bc("type            kLowReWallFunction;",
                                 "value           uniform 1e-12;"),
                   "frontAndBack": empty, "unused": unused}))
    omega = _field("volScalarField", "omega", "[0 0 -1 0 0 0 0]",
                   f"uniform {NACA_OMEGA_INF:.8g}", build({
                       "outer": bc(
                           "type            inletOutlet;",
                           f"inletValue      uniform {NACA_OMEGA_INF:.8g};",
                           f"value           uniform {NACA_OMEGA_INF:.8g};"),
                       "airfoil": bc(
                           "type            omegaWallFunction;",
                           "blended         true;",
                           f"value           uniform {NACA_OMEGA_INF:.8g};"),
                       "frontAndBack": empty, "unused": unused}))
    nut = _field("volScalarField", "nut", "[0 2 -1 0 0 0 0]",
                 f"uniform {NACA_NUT_INF:.8g}", build({
                     "outer": bc("type            calculated;",
                                 "value           uniform 0;"),
                     "airfoil": bc("type            nutLowReWallFunction;",
                                   "value           uniform 0;"),
                     "frontAndBack": empty, "unused": unused}))
    return {"U": u, "p": p, "k": k, "omega": omega, "nut": nut}


NACA_GRID_FILES = {
    "coarse": "n0012_113-33.p3dfmt",
    "medium": "n0012_225-65.p3dfmt",
    "fine": "n0012_449-129.p3dfmt",
}


def run_naca_level(level: NacaGridLevel, alpha_deg: float, out_dir: Path,
                   log: Callable[[str], None] = print, *,
                   detach: bool = False, relax_p: float = 0.25,
                   relax_u: float = 0.6,
                   iterations: int | None = None
                   ) -> dict[str, Any] | dict[str, float]:
    """One (grid, alpha) solve on the actual TMR-distributed C-grid.

    Converts the PLOT3D file, autoPatches the boundary, classifies patches
    geometrically, writes the fields against the discovered names, then
    initializes from a potential solve and runs simpleFoam (inline, or
    detached when ``detach`` is set: the caller then polls
    solver_exit_status and calls collect_level with the returned timings).
    """
    prefix = f"tmr-naca-a{alpha_deg:g}"
    remote = f"{_RUN_ROOT}/{prefix}-{level.name}"
    remote_dir = Path(remote)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    case_root = _REPO_ROOT / "models" / "tmr" / "naca0012"
    grid_src = case_root / "grids" / NACA_GRID_FILES[level.name]

    # Stage a minimal case: dictionaries only; fields come after patching.
    case = case_root / f"a{alpha_deg:g}" / level.name
    for sub in ("system",):
        (case / sub).mkdir(parents=True, exist_ok=True)
    budget = iterations or NACA_ITERATIONS.get(level.name, 10000)
    dicts = {
        "system/controlDict": control_dict(
            budget, patch="PLACEHOLDER", lref=1.0, aref=1.0),
        "system/fvSchemes": fv_schemes(limited=True),
        "system/fvSolution": fv_solution(non_orth_correctors=1,
                                         relax_p=relax_p, relax_u=relax_u,
                                         potential=True, p_solver="PCG"),
        "constant/transportProperties": transport_properties(NACA_NU),
        "constant/turbulenceProperties": turbulence_properties(),
    }
    (case / "constant").mkdir(exist_ok=True)
    for rel, text in dicts.items():
        with (case / rel).open("w", newline="\n") as handle:
            handle.write(text)
    shutil.copy(grid_src, case / "grid.p3dfmt")

    shutil.rmtree(remote_dir, ignore_errors=True)
    remote_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(case, remote_dir)
    if not (remote_dir / "system" / "controlDict").exists():
        raise RuntimeError(f"{level.name}: staging failed")

    timings: dict[str, float] = {}
    for name, args, timeout in (
            ("plot3dToFoam", ["plot3dToFoam", "-noBlank", "grid.p3dfmt"], 900),
            ("autoPatch", ["autoPatch", "80", "-overwrite"], 900)):
        start = time.monotonic()
        result = _foam(args, remote_dir, f"log.{name}", timeout=timeout)
        timings[name] = round(time.monotonic() - start, 1)
        _copy_best_effort(remote_dir / f"log.{name}", out_dir / f"log.{name}")
        if result.returncode != 0:
            tail = (remote_dir / f"log.{name}").read_text(errors="replace")
            raise RuntimeError(f"{level.name}/{name} failed:\n"
                               + "\n".join(tail.splitlines()[-15:]))

    # Pull the mesh description and classify the boundary.
    for item in ("boundary", "points", "faces"):
        _copy_best_effort(remote_dir / "constant" / "polyMesh" / item,
                          out_dir / f"mesh.{item}")
    patches = parse_boundary_patches(
        (out_dir / "mesh.boundary").read_text(errors="replace"))
    points, faces = parse_polymesh_points_faces(
        (out_dir / "mesh.points").read_text(errors="replace"),
        (out_dir / "mesh.faces").read_text(errors="replace"))
    roles, thickness, lift_axis, span_axis = classify_naca_patches(
        points, faces, patches)
    airfoil_patches = [n for n, r in roles.items() if r == "airfoil"]
    if len(airfoil_patches) != 1:
        raise RuntimeError(f"{level.name}: expected one airfoil patch, "
                           f"got {airfoil_patches} from {roles}")
    airfoil = airfoil_patches[0]
    log(f"[tmr-naca:{level.name}] patches {roles}, thickness {thickness:g}, "
        f"lift axis {'xyz'[lift_axis]}")

    # Fields and the real controlDict (patch name and Aref now known),
    # plus boundary types: the z planes become empty, the body a wall.
    fields_dir = out_dir / "0"
    shutil.rmtree(fields_dir, ignore_errors=True)
    fields_dir.mkdir(parents=True)
    for name, text in naca_fields_tmr(alpha_deg, roles, lift_axis).items():
        with (fields_dir / name).open("w", newline="\n") as handle:
            handle.write(text)
    rad = math.radians(alpha_deg)
    control = control_dict(
        budget, patch=airfoil, lref=1.0, aref=thickness,
        drag_dir=_axis_vector(math.cos(rad), math.sin(rad), lift_axis),
        lift_dir=_axis_vector(-math.sin(rad), math.cos(rad), lift_axis))
    with (out_dir / "controlDict.solve").open("w", newline="\n") as handle:
        handle.write(control)

    remote_zero = remote_dir / "0"
    shutil.rmtree(remote_zero, ignore_errors=True)
    remote_zero.mkdir()
    for item in fields_dir.iterdir():
        shutil.copy2(item, remote_zero / item.name)
    shutil.copy2(out_dir / "controlDict.solve",
                remote_dir / "system" / "controlDict")
    boundary_edits = [
        (name, "empty" if role == "frontAndBack" else "wall")
        for name, role in roles.items()
        if role in ("frontAndBack",) or name == airfoil]
    for name, value in boundary_edits:
        result = _foam(["foamDictionary", "-entry", f"entry0/{name}/type",
                       "-set", value, "constant/polyMesh/boundary"],
                       remote_dir, "log.foamDictionary", timeout=120)
        if result.returncode != 0:
            tail = (remote_dir / "log.foamDictionary").read_text(
                errors="replace")
            raise RuntimeError(
                f"{level.name}: boundary edit for {name} failed:\n"
                + "\n".join(tail.splitlines()[-15:]))

    for name, args, timeout in (
            ("checkMesh", ["checkMesh"], 900),
            ("potentialFoam", ["potentialFoam", "-writephi"], 1800)):
        start = time.monotonic()
        result = _foam(args, remote_dir, f"log.{name}", timeout=timeout)
        timings[name] = round(time.monotonic() - start, 1)
        _copy_best_effort(remote_dir / f"log.{name}", out_dir / f"log.{name}")
        if result.returncode != 0:
            tail = (remote_dir / f"log.{name}").read_text(errors="replace")
            raise RuntimeError(f"{level.name}/{name} failed:\n"
                               + "\n".join(tail.splitlines()[-15:]))

    if detach:
        exit_file = remote_dir / "solve.exit"
        exit_file.unlink(missing_ok=True)
        log_path = remote_dir / "log.simpleFoam"
        log_path.unlink(missing_ok=True)
        command = [*_run_prefix(), "simpleFoam"]
        wrapper = (f"{shlex.join(command)} > log.simpleFoam 2>&1; "
                  f"echo $? > solve.exit")
        subprocess.Popen(["bash", "-c", wrapper], cwd=str(remote_dir),
                         start_new_session=True, stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)
        if not log_path.exists():
            raise RuntimeError(f"{level.name}: detached solve failed to launch")
        log(f"[tmr-naca:{level.name}] a{alpha_deg:g} solve launched detached")
        timings["airfoil_patch"] = airfoil  # smuggled for collect_level
        return timings

    start = time.monotonic()
    log(f"[tmr-naca:{level.name}] a{alpha_deg:g} simpleFoam started")
    result = _foam(["simpleFoam"], remote_dir, "log.simpleFoam", timeout=14400)
    timings["simpleFoam"] = round(time.monotonic() - start, 1)
    if result.returncode != 0:
        tail = (remote_dir / "log.simpleFoam").read_text(errors="replace")
        raise RuntimeError(f"{level.name}/simpleFoam failed:\n"
                           + "\n".join(tail.splitlines()[-20:]))
    log(f"[tmr-naca:{level.name}] simpleFoam finished in "
        f"{timings['simpleFoam']:.1f} s")
    return _extract_record(level, out_dir, remote, timings, None,
                           airfoil, log)


# -- time-accurate treatment of the coarse-rung limit cycle -----------------
# The steady runs isolated a sustained wake-driven force oscillation on the
# TMR C-grids under second-order incompressible solves. The honest number for
# such a state is a time-average with its envelope, from a genuinely
# time-accurate solve, never a snapshot of whatever phase a steady iteration
# happened to stop in.

def time_weighted_stats(times: Sequence[float], values: Sequence[float],
                        t_start: float) -> dict[str, float] | None:
    """Trapezoidal time-weighted mean and peak-to-trough envelope of a
    signal over [t_start, end]. Time weighting matters because an adaptive
    time step makes the samples unevenly spaced."""
    window = [(t, v) for t, v in zip(times, values) if t >= t_start]
    if len(window) < 3:
        return None
    area = 0.0
    for (t0, v0), (t1, v1) in zip(window, window[1:]):
        area += 0.5 * (v0 + v1) * (t1 - t0)
    span = window[-1][0] - window[0][0]
    if span <= 0:
        return None
    lo = min(v for _, v in window)
    hi = max(v for _, v in window)
    return {"mean": area / span, "lo": lo, "hi": hi, "band": hi - lo,
            "window_start": window[0][0], "window_end": window[-1][0]}


def measure_period(times: Sequence[float], values: Sequence[float],
                   t_start: float) -> float | None:
    """Mean period of an oscillation from its upward mean-crossings over
    [t_start, end]; None when fewer than two full crossings exist (no
    period may then be quoted)."""
    stats = time_weighted_stats(times, values, t_start)
    if stats is None:
        return None
    mean = stats["mean"]
    crossings = []
    window = [(t, v) for t, v in zip(times, values) if t >= t_start]
    for (t0, v0), (t1, v1) in zip(window, window[1:]):
        if v0 < mean <= v1:
            frac = (mean - v0) / (v1 - v0) if v1 != v0 else 0.0
            crossings.append(t0 + frac * (t1 - t0))
    if len(crossings) < 3:
        return None
    gaps = [b - a for a, b in zip(crossings, crossings[1:])]
    return sum(gaps) / len(gaps)


def halves_drift(times: Sequence[float], values: Sequence[float],
                 t_start: float, t_end: float) -> dict[str, float] | None:
    """Split [t_start, t_end] at its midpoint and time-weight-average each
    half separately.

    A genuine time-average requires the window to be STATIONARY: the mean
    over the first half must agree with the mean over the second half,
    within the same window that ``time_weighted_stats`` folds into one
    number. A transient that is still developing (e.g. k-omega SST ramping
    up from a cold, low-freestream-turbulence start) produces a whole-window
    mean that is a snapshot of an ongoing trend, not a converged value, and
    the two half-window means will disagree by far more than run-to-run
    period noise. None when either half lacks enough samples to average (the
    caller must then treat drift as unknown, not as passing).
    """
    mid = 0.5 * (t_start + t_end)
    first_half = [(t, v) for t, v in zip(times, values) if t_start <= t <= mid]
    first = time_weighted_stats([t for t, _ in first_half],
                                [v for _, v in first_half], t_start)
    second = time_weighted_stats(times, values, mid)
    if first is None or second is None:
        return None
    denom = max(abs(first["mean"]), abs(second["mean"]))
    if denom == 0:
        return None
    return {"first_half_mean": first["mean"], "second_half_mean": second["mean"],
            "relative_drift": abs(second["mean"] - first["mean"]) / denom}


def pimple_control_dict(end_time: float, dt0: float, *, patch: str,
                        aref: float, drag_dir: str, lift_dir: str,
                        max_co: float = 1.5, adjustable: bool = True) -> str:
    # A fixed step exists for restarts seeded from a steady field: the
    # impulsive adjustment there collapses an adaptive step to 1e-5 and the
    # run crawls; implicit Euler rides the few spiky steps out instead.
    return _foam_header("dictionary", "controlDict", "system") + f"""
application     pimpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {end_time};
deltaT          {dt0};
adjustTimeStep  {'yes' if adjustable else 'no'};
maxCo           {max_co};
maxDeltaT       {end_time / 200.0};
writeControl    adjustableRunTime;
writeInterval   {end_time};
purgeWrite      1;
writeFormat     ascii;
writePrecision  10;
timeFormat      general;
timePrecision   8;

functions
{{
    forceCoeffs1
    {{
        type            forceCoeffs;
        libs            (forces);
        writeControl    timeStep;
        writeInterval   1;
        patches         ({patch});
        rho             rhoInf;
        rhoInf          1.0;
        magUInf         {U_INF};
        lRef            1.0;
        Aref            {aref};
        CofR            (0 0 0);
        dragDir         {drag_dir};
        liftDir         {lift_dir};
        pitchAxis       (0 0 1);
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


def pimple_fv_solution() -> str:
    return _foam_header("dictionary", "fvSolution", "system") + """
solvers
{
    p
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-08;
        relTol          0.01;
    }
    pFinal
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-08;
        relTol          0;
    }
    "(U|k|omega)"
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-09;
        relTol          0.01;
    }
    "(U|k|omega)Final"
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-09;
        relTol          0;
    }
}

PIMPLE
{
    nOuterCorrectors    2;
    nCorrectors         2;
    nNonOrthogonalCorrectors 1;
}

relaxationFactors
{
    fields    { p 0.3; pFinal 1; }
    equations { "(U|k|omega)" 0.7; "(U|k|omega)Final" 1; }
}
"""


def run_naca_transient(level: NacaGridLevel, alpha_deg: float, out_dir: Path,
                       log: Callable[[str], None] = print, *,
                       end_time: float = 30.0, dt0: float = 0.002,
                       transient_fraction: float = 0.4,
                       init_from: str | None = None,
                       adjustable_dt: bool = True) -> dict[str, Any]:
    """Time-accurate pimpleFoam run of one (grid, alpha), reporting the
    time-averaged coefficients with their limit-cycle envelope.

    The average starts after ``transient_fraction`` of the run; the record
    carries the window, the band, and the measured period (None when fewer
    than three mean-crossings fit the window, in which case no period is
    quoted and the averaging quality must be judged accordingly).

    ``init_from`` (a time-directory path from a completed steady run on the
    SAME converted grid) seeds the march with a developed turbulent field.
    Without it the freestream-cold start stays effectively laminar for far
    longer than any affordable window: measured, a 30-unit cold start ended
    at Cd 0.00033 with max y+ 0.5 and no oscillation at all, because SST
    transition in genuine time is slow at 0.039 percent freestream
    turbulence, a shortcut steady pseudo-time quietly takes.
    """
    prefix = f"tmr-naca-t-a{alpha_deg:g}"
    remote = f"{_RUN_ROOT}/{prefix}-{level.name}"
    remote_dir = Path(remote)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    case_root = _REPO_ROOT / "models" / "tmr" / "naca0012"
    grid_src = case_root / "grids" / NACA_GRID_FILES[level.name]

    case = case_root / f"t-a{alpha_deg:g}" / level.name
    (case / "system").mkdir(parents=True, exist_ok=True)
    (case / "constant").mkdir(exist_ok=True)
    dicts = {
        "system/controlDict": control_dict(100, patch="PLACEHOLDER"),
        "system/fvSchemes": fv_schemes(limited=True, transient=True),
        "system/fvSolution": pimple_fv_solution(),
        "constant/transportProperties": transport_properties(NACA_NU),
        "constant/turbulenceProperties": turbulence_properties(),
    }
    for rel, text in dicts.items():
        with (case / rel).open("w", newline="\n") as handle:
            handle.write(text)
    shutil.copy(grid_src, case / "grid.p3dfmt")

    shutil.rmtree(remote_dir, ignore_errors=True)
    remote_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(case, remote_dir)
    if not (remote_dir / "system" / "controlDict").exists():
        raise RuntimeError(f"{level.name}: staging failed")

    timings: dict[str, float] = {}
    for name, args, timeout in (
            ("plot3dToFoam", ["plot3dToFoam", "-noBlank", "grid.p3dfmt"], 900),
            ("autoPatch", ["autoPatch", "80", "-overwrite"], 900)):
        start = time.monotonic()
        result = _foam(args, remote_dir, f"log.{name}", timeout=timeout)
        timings[name] = round(time.monotonic() - start, 1)
        if result.returncode != 0:
            raise RuntimeError(f"{level.name}/{name} failed")

    for item in ("boundary", "points", "faces"):
        _copy_best_effort(remote_dir / "constant" / "polyMesh" / item,
                          out_dir / f"mesh.{item}")
    patches = parse_boundary_patches(
        (out_dir / "mesh.boundary").read_text(errors="replace"))
    points, faces = parse_polymesh_points_faces(
        (out_dir / "mesh.points").read_text(errors="replace"),
        (out_dir / "mesh.faces").read_text(errors="replace"))
    roles, thickness, lift_axis, span_axis = classify_naca_patches(
        points, faces, patches)
    airfoil = next(n for n, r in roles.items() if r == "airfoil")
    log(f"[tmr-naca-t:{level.name}] a{alpha_deg:g} patches ok, "
        f"lift axis {'xyz'[lift_axis]}")

    fields_dir = out_dir / "0"
    shutil.rmtree(fields_dir, ignore_errors=True)
    fields_dir.mkdir(parents=True)
    for name, text in naca_fields_tmr(alpha_deg, roles, lift_axis).items():
        with (fields_dir / name).open("w", newline="\n") as handle:
            handle.write(text)
    rad = math.radians(alpha_deg)
    control = pimple_control_dict(
        end_time, dt0, patch=airfoil, aref=thickness,
        drag_dir=_axis_vector(math.cos(rad), math.sin(rad), lift_axis),
        lift_dir=_axis_vector(-math.sin(rad), math.cos(rad), lift_axis),
        adjustable=adjustable_dt)
    with (out_dir / "controlDict.solve").open("w", newline="\n") as handle:
        handle.write(control)
    # potentialFoam needs its Phi entry; swap fvSolution for the init, then
    # restore the PIMPLE one for the march.
    with (out_dir / "fvSolution.init").open("w", newline="\n") as handle:
        handle.write(fv_solution(non_orth_correctors=1, potential=True,
                                 p_solver="PCG"))

    remote_zero = remote_dir / "0"
    shutil.rmtree(remote_zero, ignore_errors=True)
    remote_zero.mkdir()
    for item in fields_dir.iterdir():
        shutil.copy2(item, remote_zero / item.name)
    shutil.copy2(out_dir / "controlDict.solve",
                remote_dir / "system" / "controlDict")
    shutil.copy2(out_dir / "fvSolution.init",
                remote_dir / "system" / "fvSolution")
    boundary_edits = [
        (name, "empty" if role == "frontAndBack" else "wall")
        for name, role in roles.items()
        if role == "frontAndBack" or name == airfoil]
    for name, value in boundary_edits:
        result = _foam(["foamDictionary", "-entry", f"entry0/{name}/type",
                       "-set", value, "constant/polyMesh/boundary"],
                       remote_dir, "log.foamDictionary", timeout=120)
        if result.returncode != 0:
            tail = (remote_dir / "log.foamDictionary").read_text(
                errors="replace")
            raise RuntimeError(
                f"{level.name}: boundary edit for {name} failed:\n"
                + "\n".join(tail.splitlines()[-15:]))

    if init_from:
        init_dir = Path(init_from)
        required = ("U", "p", "k", "omega", "nut")
        if not all((init_dir / name).exists() for name in required):
            raise RuntimeError(f"{level.name}: seeding from {init_from} "
                               f"failed (missing one of {required})")
        for name in required:
            shutil.copy2(init_dir / name, remote_zero / name)
        phi_src = init_dir / "phi"
        if phi_src.exists():
            shutil.copy2(phi_src, remote_zero / "phi")
        log(f"[tmr-naca-t:{level.name}] fields seeded from {init_from}")
    else:
        start = time.monotonic()
        result = _foam(["potentialFoam", "-writephi"], remote_dir,
                       "log.potentialFoam", timeout=1800)
        timings["potentialFoam"] = round(time.monotonic() - start, 1)
        if result.returncode != 0:
            raise RuntimeError(f"{level.name}: potentialFoam failed")
    solution = pimple_fv_solution()
    with (out_dir / "fvSolution.march").open("w", newline="\n") as handle:
        handle.write(solution)
    shutil.copy2(out_dir / "fvSolution.march",
                remote_dir / "system" / "fvSolution")

    start = time.monotonic()
    log(f"[tmr-naca-t:{level.name}] a{alpha_deg:g} pimpleFoam started "
        f"(T = {end_time:g})")
    result = _foam(["pimpleFoam"], remote_dir, "log.pimpleFoam", timeout=7200)
    timings["pimpleFoam"] = round(time.monotonic() - start, 1)
    _copy_best_effort(remote_dir / "log.pimpleFoam",
                      out_dir / "log.pimpleFoam")
    if result.returncode != 0:
        tail = (remote_dir / "log.pimpleFoam").read_text(errors="replace")
        raise RuntimeError(f"{level.name}/pimpleFoam failed:\n"
                           + "\n".join(tail.splitlines()[-20:]))
    log(f"[tmr-naca-t:{level.name}] pimpleFoam finished in "
        f"{timings['pimpleFoam']:.1f} s")

    shutil.rmtree(out_dir / "postProcessing", ignore_errors=True)
    _copy_best_effort(remote_dir / "postProcessing",
                      out_dir / "postProcessing")
    coeff_files = sorted((out_dir / "postProcessing").rglob("coefficient*.dat"))
    history = parse_coefficient_history(
        coeff_files[-1].read_text(errors="replace"))
    times = history["Time"]
    t_start = transient_fraction * end_time
    cd_stats = time_weighted_stats(times, history["Cd"], t_start)
    cl_stats = time_weighted_stats(times, history["Cl"], t_start)
    period = measure_period(times, history["Cl"], t_start)
    if cd_stats is None or cl_stats is None:
        raise RuntimeError(f"{level.name}: averaging window empty")
    # A whole-window time-average is only meaningful if the window is
    # STATIONARY. Without this check a Cd that is still ramping up (SST
    # turbulence slowly developing from a cold, low-freestream-turbulence
    # start) silently reports its whole-window mean as if it were a
    # converged value, when it is really a snapshot partway through an
    # ongoing trend — measured on the 300-convective-unit alpha=0 coarse
    # rung, Cd rose 0.00032 -> 0.00089 monotonically in five successive
    # 60-unit chunks with no sign of leveling off, a 37% first-half vs
    # second-half drift on the very window the mean was quoted from. Reject
    # anything past a much smaller drift than that; a real limit cycle's two
    # halves agree far better than 10%.
    drift = halves_drift(times, history["Cd"],
                         cd_stats["window_start"], cd_stats["window_end"])
    if drift is not None and drift["relative_drift"] > 0.10:
        raise RuntimeError(
            f"{level.name}: Cd mean still drifting across the averaging "
            f"window (first half {drift['first_half_mean']:.6f}, second "
            f"half {drift['second_half_mean']:.6f}, "
            f"{100 * drift['relative_drift']:.0f}% relative drift); this is "
            f"a mid-transient snapshot, not a stationary time-average, and "
            f"must not be quoted as Cd")
    n_periods = ((cd_stats["window_end"] - cd_stats["window_start"]) / period
                 if period else None)
    yplus_files = sorted((out_dir / "postProcessing").rglob("yPlus.dat"))
    yplus = (parse_yplus_dat(yplus_files[-1].read_text(errors="replace"),
                             airfoil) if yplus_files else None)
    record = {
        "level": level.name, "tmr_nodes": level.tmr_nodes,
        "cells": level.cells, "alpha_deg": alpha_deg,
        "solver": "pimpleFoam, time accurate",
        "end_time": end_time, "steps": len(times),
        "cd_mean": cd_stats["mean"], "cd_band": cd_stats["band"],
        "cd_lo": cd_stats["lo"], "cd_hi": cd_stats["hi"],
        "cd_relative_drift": drift["relative_drift"] if drift else None,
        "cl_mean": cl_stats["mean"], "cl_band": cl_stats["band"],
        "cl_lo": cl_stats["lo"], "cl_hi": cl_stats["hi"],
        "averaging_window": [cd_stats["window_start"],
                             cd_stats["window_end"]],
        "period": period, "periods_in_window": n_periods,
        "yplus": yplus or {"min": float("nan"), "max": float("nan"),
                           "average": float("nan")},
        "wall_seconds": sum(timings.values()),
        "timings": timings,
    }
    log(f"[tmr-naca-t:{level.name}] a{alpha_deg:g}: "
        f"Cl {cl_stats['mean']:+.5f} (band {cl_stats['band']:.4f}), "
        f"Cd {cd_stats['mean']:+.6f} (band {cd_stats['band']:.5f}), "
        f"period {period if period else float('nan'):.3f}, "
        f"{len(times)} steps, wall {record['wall_seconds']:.0f} s")
    return record


def stop_requested(out_root: Path | None = None) -> bool:
    """The owner's STOP file: when present, no new solve may be launched."""
    root = Path(out_root) if out_root else (
        _REPO_ROOT / "demo-output" / "website" / "tmr")
    return (root / "STOP").exists()


if __name__ == "__main__":
    run_flat_plate_ladder()
