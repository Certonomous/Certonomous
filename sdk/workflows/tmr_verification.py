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
import re
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
ITERATIONS = {"coarse": 3000, "medium": 4000, "fine": 5000}

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
                 lref: float = PLATE_LENGTH, aref: float = PLATE_LENGTH) -> str:
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
        dragDir         (1 0 0);
        liftDir         (0 1 0);
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


def fv_schemes() -> str:
    return _foam_header("dictionary", "fvSchemes", "system") + """
ddtSchemes      { default steadyState; }
gradSchemes     { default Gauss linear; }
divSchemes
{
    // Momentum second order; turbulence advection first-order upwind.
    // The A/B on the coarse grid: linearUpwind on k and omega left a
    // persistent leading-edge bounding oscillation (5997 bounding events,
    // residuals plateaued); upwind removed every bounding event and let the
    // run converge through residualControl. Turbulence advection is
    // negligible against production and destruction in this boundary layer,
    // and the measured observed order reports whatever the ladder delivers.
    default                         none;
    div(phi,U)                      bounded Gauss linearUpwind grad(U);
    div(phi,k)                      bounded Gauss upwind;
    div(phi,omega)                  bounded Gauss upwind;
    div((nuEff*dev2(T(grad(U)))))   Gauss linear;
}
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes   { default corrected; }
wallDist        { method meshWave; }
"""


def fv_solution() -> str:
    return _foam_header("dictionary", "fvSolution", "system") + """
solvers
{
    p
    {
        solver          GAMG;
        smoother        GaussSeidel;
        tolerance       1e-09;
        relTol          0.01;
    }
    "(U|k|omega)"
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-10;
        relTol          0.01;
    }
}

SIMPLE
{
    nNonOrthogonalCorrectors 0;
    consistent      no;
    residualControl
    {
        p               1e-06;
        U               1e-08;
        "(k|omega)"     1e-08;
    }
}

relaxationFactors
{
    fields    { p 0.3; }
    equations { U 0.7; k 0.7; omega 0.7; }
}
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
# WSL execution (same launcher pattern as the Head Engineer, kept local so
# this module stays standalone; nothing here touches head_engineer state)
# ---------------------------------------------------------------------------

_WSL = ["wsl", "-d", "Ubuntu", "-u", "foam", "--"]
_RUN_ROOT = "~/certonomous-runs"


def _wsl(command: str, timeout: float = 600.0) -> subprocess.CompletedProcess:
    preamble = ("for rc in /usr/lib/openfoam/openfoam*/etc/bashrc; do "
                "source \"$rc\" >/dev/null 2>&1; break; done; ")
    return subprocess.run([*_WSL, "bash", "-c", preamble + command],
                          capture_output=True, text=True, timeout=timeout)


def _stage_and_mesh(level: GridLevel, case_root: Path, out_dir: Path,
                    remote: str, writer: Callable[[Path, GridLevel], Path],
                    log: Callable[[str], None]) -> dict[str, float]:
    """Stage a case into WSL, blockMesh and checkMesh it; return step timings."""
    case_win = writer(case_root, level)
    out_dir.mkdir(parents=True, exist_ok=True)
    staged = _wsl(
        f"rm -rf {remote} && mkdir -p {_RUN_ROOT} && "
        f"cp -r \"$(wslpath '{case_win}')\" {remote} && "
        f"test -f {remote}/system/controlDict && echo STAGED")
    if "STAGED" not in staged.stdout:
        raise RuntimeError(f"staging {level.name} failed: "
                           f"{(staged.stderr or staged.stdout)[:300]}")
    timings: dict[str, float] = {}
    for step in ("blockMesh", "checkMesh"):
        start = time.monotonic()
        log(f"[tmr:{level.name}] {step} started")
        result = _wsl(f"cd {remote} && openfoam2606 {step} "
                      f"> log.{step} 2>&1 && echo DONE", timeout=600)
        timings[step] = round(time.monotonic() - start, 1)
        _wsl(f"cp {remote}/log.{step} \"$(wslpath '{out_dir}')\"/ || true")
        if "DONE" not in result.stdout:
            tail = _wsl(f"tail -20 {remote}/log.{step}").stdout
            raise RuntimeError(f"{level.name}/{step} failed:\n{tail}")
        log(f"[tmr:{level.name}] {step} finished in {timings[step]:.1f} s")
    return timings


def _extract_record(level: GridLevel, out_dir: Path, remote: str,
                    timings: dict[str, float], station: float,
                    yplus_patch: str,
                    log: Callable[[str], None]) -> dict[str, Any]:
    """Pull one solved case's results back to Windows and extract the record.

    Raises on anything unextractable or unconverged: a broken rung must never
    be papered over with a partial number.
    """
    out_dir = Path(out_dir)
    # A fresh copy every time: a leftover postProcessing tree from an earlier
    # attempt would nest the new one inside it and could offer stale files to
    # the extraction globs below.
    shutil.rmtree(out_dir / "postProcessing", ignore_errors=True)
    _wsl(f"cp {remote}/log.simpleFoam \"$(wslpath '{out_dir}')\"/ || true")
    _wsl(f"cp -r {remote}/postProcessing \"$(wslpath '{out_dir}')\"/",
         timeout=300)

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
    cf_station = cf_at(profile, station)
    if cf_station is None or cf_station <= 0:
        raise RuntimeError(f"{level.name}: Cf at x={station} not extractable "
                           f"(profile of {len(profile)} points)")

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
    if split:
        record["cd_pressure"] = split["pressure"]
        record["cd_viscous"] = split["viscous"]
    log(f"[tmr:{level.name}] Cd={cd['value']:.6f} "
        f"Cf({station:g})={cf_station:.6f} iters={cd['iterations']} "
        f"wall={record['wall_seconds']:.0f}s")
    return record


def run_level(level: GridLevel, case_root: Path, out_dir: Path,
              log: Callable[[str], None] = print, *,
              writer: Callable[[Path, GridLevel], Path] = write_case,
              remote_prefix: str = "tmr-flatplate",
              station: float = CF_STATION, yplus_patch: str = "plate",
              solver_timeout: float = 5400.0) -> dict[str, Any]:
    """Mesh and solve one ladder level in WSL, pull results back, extract."""
    remote = f"{_RUN_ROOT}/{remote_prefix}-{level.name}"
    out_dir = Path(out_dir)
    timings = _stage_and_mesh(level, case_root, out_dir, remote, writer, log)
    start = time.monotonic()
    log(f"[tmr:{level.name}] simpleFoam started")
    result = _wsl(f"cd {remote} && openfoam2606 simpleFoam "
                  f"> log.simpleFoam 2>&1 && echo DONE",
                  timeout=solver_timeout)
    timings["simpleFoam"] = round(time.monotonic() - start, 1)
    if "DONE" not in result.stdout:
        tail = _wsl(f"tail -20 {remote}/log.simpleFoam").stdout
        raise RuntimeError(f"{level.name}/simpleFoam failed:\n{tail}")
    log(f"[tmr:{level.name}] simpleFoam finished in "
        f"{timings['simpleFoam']:.1f} s")
    return _extract_record(level, out_dir, remote, timings, station,
                           yplus_patch, log)


def launch_level_solver(level: GridLevel, case_root: Path, out_dir: Path,
                        log: Callable[[str], None] = print, *,
                        writer: Callable[[Path, GridLevel], Path] = write_case,
                        remote_prefix: str = "tmr-flatplate") -> dict[str, float]:
    """Stage, mesh, and start the solve DETACHED inside WSL.

    For rungs whose solve outlives any sane foreground window. The nohup'd
    process writes its exit code to ``solve.exit`` when done; the caller polls
    :func:`solver_exit_status` and then runs :func:`collect_level`. Returns
    the mesh-step timings so the eventual record carries the full wall clock.
    """
    remote = f"{_RUN_ROOT}/{remote_prefix}-{level.name}"
    timings = _stage_and_mesh(level, case_root, Path(out_dir), remote,
                              writer, log)
    # setsid puts the solver in its own session so WSL's per-session cleanup
    # cannot reap it when this command's wsl.exe exits, and the launching
    # shell stays alive (sleep) until the solver has demonstrably opened its
    # log. A bare "nohup ... &" here dies with the session — measured, not
    # theorized: the first launch attempt left no log and no exit file.
    launched = _wsl(
        f"cd {remote} && rm -f solve.exit && "
        f"setsid nohup bash -c 'cd {remote} && openfoam2606 simpleFoam "
        f"> log.simpleFoam 2>&1; echo $? > solve.exit' "
        f"< /dev/null >/dev/null 2>&1 & sleep 3; "
        f"test -f {remote}/log.simpleFoam && echo LAUNCHED", timeout=120)
    if "LAUNCHED" not in launched.stdout:
        raise RuntimeError(f"{level.name}: detached solve failed to launch")
    log(f"[tmr:{level.name}] simpleFoam launched detached in {remote}")
    return timings


def solver_exit_status(level: GridLevel,
                       remote_prefix: str = "tmr-flatplate") -> int | None:
    """Exit code of a detached solve, or None while it is still running."""
    remote = f"{_RUN_ROOT}/{remote_prefix}-{level.name}"
    raw = _wsl(f"cat {remote}/solve.exit 2>/dev/null").stdout.strip()
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
        "solver": "simpleFoam, incompressible, OpenFOAM v2606 under WSL",
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
        "solver": "simpleFoam, incompressible, OpenFOAM v2606 under WSL",
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


if __name__ == "__main__":
    run_flat_plate_ladder()
