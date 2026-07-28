"""Transonic NACA0012 airfoil, rhoSimpleFoam + k-omega SST -- compressible RANS
with a genuine shock, for the mega-batch's Family 2 (transonic).

MESH: reused, unmodified, from ``tmr_verification.naca_blockmesh_dict`` at the
``NACA_LEVELS[0]`` ("coarse", 3584-cell) rung -- the same analytic O-grid
topology (LE/TE clustered spline surface, wall-normal first cell ~6e-6 chords,
500-chord farfield) already built and exercised there for the incompressible
NASA-TMR NACA 0012 verification case. Mesh geometry does not care whether the
flow behind it is compressible, so nothing about the mesh generator changes;
only the field files, thermophysical/turbulence properties, fvSchemes,
fvSolution and controlDict are new, and they follow OpenFOAM's own stock
``$FOAM_TUTORIALS/compressible/rhoSimpleFoam/aerofoilNACA0012`` tutorial
(divSchemes, relaxation factors, perfect-gas thermophysicalProperties) rather
than inventing a compressible solver setup from scratch -- adapted only to
this O-grid's ``airfoil``/``inflow``/``outflow`` patch names in place of the
tutorial's ``wall``/``freestream`` pair.

GEOMETRY CHOICE (NACA0012, not RAE2822): the task allows either. RAE2822's
Case 9/10 flow conditions (M=0.734/alpha=2.79 deg/Re=6.5e6 attached;
M=0.754/alpha=2.57 deg/Re=6.2e6 shock-separated) are well corroborated across
independent sources, but this task did not turn up a citable, directly
fetchable DIGITIZED Cp/shock dataset for RAE2822 within its effort budget --
so no RAE2822 quantitative comparison is claimed anywhere in this module or
in PHYSICS_FAMILIES.md. NACA0012 is exact and analytic (no coordinate-table
risk), and the classical M=0.8, alpha=1.25 deg NACA0012 case is one of the
most widely reproduced transonic CFD benchmarks in the literature: an
INVISCID solution of this case produces two shocks, a strong one on the
suction (upper) side near x/c ~ 0.6 and a weak one on the pressure (lower)
side near x/c ~ 0.35 (reported consistently across independent shock-capturing
/ Riemann-solver validation papers reproducing this AGARD/GAMM workshop case).
Our solve is VISCOUS turbulent RANS, not inviscid Euler, so the upper shock is
expected to sit somewhat UPSTREAM of the inviscid x/c ~0.6 position (published
turbulent-RANS/experimental studies of this same case at nearby alpha, e.g.
DPW-vintage NACA0012 shock-boundary-layer-interaction studies, describe the
shock migrating upstream of the inviscid location as separation approaches);
the validation gate here is therefore a BAND (0.35-0.60 chord) anchored on the
inviscid number, not a point match -- and is reported as such, never dressed
up as an exact quantitative Cp comparison.

Freestream turbulence (k, omega) is not published for either reference case,
so it is set from a standard low-turbulence wind-tunnel assumption (turbulence
intensity Tu=0.1%, eddy-viscosity ratio mut/mu=10) -- a documented modeling
choice, not a measured input.
"""

from __future__ import annotations

import math
import shutil
import time
from pathlib import Path
from typing import Any, Callable

from workflows.tmr_verification import (
    NACA_LEVELS, NacaGridLevel, naca_thickness, naca_surface_points,
    ratio_for_first_cell,
    _foam, _foam_header, _run_prefix, _copy_best_effort,
    final_coefficient, parse_force_split,
)
from chief_engineer.head_engineer import parse_coefficient_history

GAMMA = 1.4
R_AIR = 287.05          # J/(kg K)
P_INF = 101_325.0       # Pa
T_INF = 300.0           # K
CHORD = 1.0             # the O-grid is built at chord = 1
TU_FREESTREAM = 0.001   # 0.1% freestream turbulence intensity (assumed)
MUT_RATIO = 10.0        # freestream eddy-viscosity ratio mut/mu (assumed)

LEVEL: NacaGridLevel = NACA_LEVELS[0]   # "coarse" cell counts (16/24/32), reused

# tmr_verification's naca_blockmesh_dict hardcodes a 500-chord farfield and
# wake (tuned for its incompressible point-vortex-corrected lift case). That
# extreme stretch (measured there: ~2.8e7 aspect-ratio wake cells) is
# survivable for pressure-based incompressible solving but blew up
# rhoSimpleFoam within a handful of iterations here (measured: "Negative
# initial temperature" by iteration 3) -- compressible density/energy
# coupling is far less tolerant of extreme cell stretching. Transonic
# external flow does not need a 500-chord farfield anyway (20-30 chords is
# standard practice for a characteristic/freestream far boundary), so this
# module regenerates the SAME topology and LE/TE surface clustering at a much
# more modest domain size instead of reusing naca_blockmesh_dict directly.
FARFIELD_R = 25.0        # chords
WAKE_LEN = 25.0          # chords
E_LE = 50.0              # mid-chord to leading-edge spacing ratio (as tmr's)
E_TE = 4.0               # mid-chord to trailing-edge spacing ratio (as tmr's)
FIRST_CELL = 8.0e-6      # wall-normal first cell, chords (y+ << 1 target)


def _wake_ratio(level: NacaGridLevel, wake_len: float) -> float:
    """Total wake expansion so the first wake cell matches the coarse
    family's trailing-edge streamwise spacing (mirrors tmr's _naca_wake_ratio,
    parameterized on wake length instead of the fixed 500-chord constant)."""
    seg = 0.502
    r = (1.0 / E_TE) ** (1.0 / (level.n_surf_quarter - 1))
    first = seg * (r - 1.0) / (r ** level.n_surf_quarter - 1.0)
    te_spacing = first * r ** (level.n_surf_quarter - 1)
    return ratio_for_first_cell(wake_len, level.n_wake, te_spacing)


def transonic_blockmesh_dict(level: NacaGridLevel, *, farfield_r: float = FARFIELD_R,
                             wake_len: float = WAKE_LEN,
                             first_cell: float = FIRST_CELL) -> str:
    """The same O-grid topology as tmr_verification.naca_blockmesh_dict
    (surface polyLines from naca_surface_points/naca_thickness, four LE/TE
    quarter blocks plus upper/lower wake blocks), regenerated at a domain
    size and wall-normal spacing sized for this module, not tmr's."""
    R, W = farfield_r, farfield_r + wake_len
    r_y = ratio_for_first_cell(R, level.ny, first_cell)
    r_y_far = ratio_for_first_cell(R, level.ny, min(0.3, 0.3 * farfield_r / 25.0))
    r_wake = _wake_ratio(level, wake_len)
    ym = naca_thickness(0.5)
    c45 = R / math.sqrt(2.0)

    def arc_point(deg: float) -> str:
        rad = math.radians(deg)
        return f"({1.0 + R * math.cos(rad):.10g} {R * math.sin(rad):.10g}"

    def poly(points: list[tuple[float, float]], z: float) -> str:
        inner = "\n".join(f"        ({x:.10g} {y:.10g} {z})" for x, y in points)
        return f"(\n{inner}\n    )"

    up_front = naca_surface_points(0.0, 0.5, +1.0)
    up_rear = naca_surface_points(0.5, 1.0, +1.0)
    lo_front = naca_surface_points(0.0, 0.5, -1.0)
    lo_rear = naca_surface_points(0.5, 1.0, -1.0)
    ns, nw, ny = level.n_surf_quarter, level.n_wake, level.ny
    e_le, e_te = E_LE, E_TE

    lines = [_foam_header("dictionary", "blockMeshDict", "system"), """
scale   1;

vertices
("""]
    base = [
        (1.0, 0.0), (0.0, 0.0), (0.5, ym), (0.5, -ym),
        (1.0 - R, 0.0), (1.0 - c45, c45), (1.0, R), (1.0 - c45, -c45), (1.0, -R),
        (W, 0.0), (W, R), (W, -R),
    ]
    for z in (0, 1):
        for i, (x, y) in enumerate(base):
            lines.append(f"    ({x:.10g} {y:.10g} {z})   // {i + 12 * z}")
    lines.append(f""");

blocks
(
    hex (1 2 5 4 13 14 17 16) ({ns} {ny} 1)
        simpleGrading ({e_le:.8g} {r_y:.8g} 1)
    hex (2 0 6 5 14 12 18 17) ({ns} {ny} 1)
        simpleGrading ({1.0 / e_te:.8g} {r_y:.8g} 1)
    hex (0 3 7 8 12 15 19 20) ({ns} {ny} 1)
        simpleGrading ({e_te:.8g} {r_y:.8g} 1)
    hex (3 1 4 7 15 13 16 19) ({ns} {ny} 1)
        simpleGrading ({1.0 / e_le:.8g} {r_y:.8g} 1)
    hex (0 9 10 6 12 21 22 18) ({nw} {ny} 1)
        edgeGrading ({r_wake:.8g} {r_wake:.8g} {r_wake:.8g} {r_wake:.8g}
                     {r_y:.8g} {r_y_far:.8g} {r_y_far:.8g} {r_y:.8g}
                     1 1 1 1)
    hex (9 0 8 11 21 12 20 23) ({nw} {ny} 1)
        edgeGrading ({1.0 / r_wake:.8g} {1.0 / r_wake:.8g} {1.0 / r_wake:.8g} {1.0 / r_wake:.8g}
                     {r_y_far:.8g} {r_y:.8g} {r_y:.8g} {r_y_far:.8g}
                     1 1 1 1)
);

edges
(""")
    for z, off in ((0.0, 0), (1.0, 12)):
        lines.append(f"    polyLine {1 + off} {2 + off} {poly(up_front, z)}")
        lines.append(f"    polyLine {2 + off} {0 + off} {poly(up_rear, z)}")
        lines.append(f"    polyLine {0 + off} {3 + off} {poly(lo_rear[::-1], z)}")
        lines.append(f"    polyLine {3 + off} {1 + off} {poly(lo_front[::-1], z)}")
        for a, b, deg in ((4, 5, 157.5), (5, 6, 112.5), (8, 7, 247.5), (7, 4, 202.5)):
            lines.append(f"    arc {a + off} {b + off} {arc_point(deg)} {z:g})")
    lines.append(f""");

boundary
(
    airfoil
    {{
        type wall;
        faces ((1 2 14 13) (2 0 12 14) (0 3 15 12) (3 1 13 15));
    }}
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


def freestream_state(mach: float, reynolds: float, *, p_inf: float = P_INF,
                     t_inf: float = T_INF) -> dict[str, float]:
    """Dimensional freestream state realizing (Mach, Re) at chord = 1."""
    a_inf = math.sqrt(GAMMA * R_AIR * t_inf)
    u_inf = mach * a_inf
    rho_inf = p_inf / (R_AIR * t_inf)
    mu = rho_inf * u_inf * CHORD / reynolds
    nu = mu / rho_inf
    k_inf = 1.5 * (TU_FREESTREAM * u_inf) ** 2
    nut_inf = MUT_RATIO * nu
    omega_inf = k_inf / nut_inf
    return {
        "a_inf": a_inf, "u_inf": u_inf, "rho_inf": rho_inf, "mu": mu, "nu": nu,
        "k_inf": k_inf, "omega_inf": omega_inf, "nut_inf": nut_inf,
        "q_inf": 0.5 * rho_inf * u_inf ** 2,
    }


# --------------------------------------------------------------------------
# constant/*
# --------------------------------------------------------------------------

def thermophysical_properties(mu: float) -> str:
    return _foam_header("dictionary", "thermophysicalProperties") + f"""
thermoType
{{
    type            hePsiThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState perfectGas;
    specie          specie;
    energy          sensibleInternalEnergy;
}}

mixture
{{
    specie
    {{
        molWeight   28.9;
    }}
    thermodynamics
    {{
        Cp          1005;
        Hf          0;
    }}
    transport
    {{
        mu          {mu:.8g};
        Pr          0.71;
    }}
}}
"""


_TURBULENCE_PROPERTIES = _foam_header("dictionary", "turbulenceProperties") + """
simulationType          RAS;

RAS
{
    RASModel            kOmegaSST;
    turbulence          on;
    printCoeffs         on;
}
"""


# --------------------------------------------------------------------------
# system/*
# --------------------------------------------------------------------------

def fv_schemes() -> str:
    return _foam_header("dictionary", "fvSchemes") + """
ddtSchemes
{
    default         steadyState;
}

gradSchemes
{
    default         Gauss linear;
    limited         cellLimited Gauss linear 1;
    grad(U)         $limited;
    grad(k)         $limited;
    grad(omega)     $limited;
}

divSchemes
{
    default         none;
    div(phi,U)      bounded Gauss linearUpwind limited;
    energy          bounded Gauss linearUpwind limited;
    div(phi,e)      $energy;
    div(phi,K)      $energy;
    div(phi,Ekp)    $energy;
    turbulence      bounded Gauss upwind;
    div(phi,k)      $turbulence;
    div(phi,omega)  $turbulence;
    div(phid,p)     Gauss upwind;
    div((phi|interpolate(rho)),p)  bounded Gauss upwind;
    div(((rho*nuEff)*dev2(T(grad(U)))))    Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
}

snGradSchemes
{
    default         corrected;
}

wallDist
{
    method          meshWave;
}
"""


def fv_solution() -> str:
    return _foam_header("dictionary", "fvSolution") + """
solvers
{
    p
    {
        solver          GAMG;
        smoother        GaussSeidel;
        tolerance       1e-6;
        relTol          0.01;
    }
    "(U|k|omega|e)"
    {
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-6;
        relTol          0.1;
    }
}

SIMPLE
{
    residualControl
    {
        p               1e-4;
        U               1e-4;
        "(k|omega|e)"   1e-4;
    }
    nNonOrthogonalCorrectors 2;
    pMinFactor      0.1;
    pMaxFactor      2;
}

relaxationFactors
{
    fields
    {
        p               0.3;
        rho             0.01;
    }
    equations
    {
        U               0.15;
        e               0.3;
        "(k|omega)"     0.3;
    }
}
"""


def control_dict(iterations: int, *, rho_inf: float, u_inf: float,
                 drag_dir: str, lift_dir: str, aref: float = CHORD * 1.0) -> str:
    # Aref = chord * span. The O-grid's frontAndBack patches sit at z=0 and
    # z=1 (see transonic_blockmesh_dict's vertex list), i.e. span = 1 chord
    # -- NOT the 0.1-chord span the incompressible cylinder case uses.
    # Measured bug: Aref=0.1 here put Cd at 0.43 and Cl at 1.09 for
    # M=0.8/alpha=1.25 deg, both exactly 10x the physically expected
    # Cd~0.04/Cl~0.11 -- Aref=1.0 (this file's default) is the fix.
    return _foam_header("dictionary", "controlDict") + f"""
application     rhoSimpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {iterations};
deltaT          1;
writeControl    timeStep;
writeInterval   {iterations};
purgeWrite      1;
writeFormat     ascii;
writePrecision  8;
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
        patches         (airfoil);
        rho             rho;
        rhoInf          {rho_inf:.8g};
        magUInf         {u_inf:.8g};
        lRef            {CHORD};
        Aref            {aref};
        CofR            (0.25 0 0);
        dragDir         {drag_dir};
        liftDir         {lift_dir};
        pitchAxis       (0 0 1);
    }}
    surfaceP
    {{
        type            surfaces;
        libs            (sampling);
        executeControl  onEnd;
        writeControl    onEnd;
        surfaceFormat   raw;
        fields          (p);
        interpolate     false;
        surfaces
        (
            airfoil {{ type patch; patches (airfoil); }}
        );
    }}
}}
"""


def _field(cls: str, obj: str, dimensions: str, internal: str,
          boundaries: dict[str, str]) -> str:
    body = "".join(f"    {name}\n    {{\n{entry}    }}\n"
                   for name, entry in boundaries.items())
    return (_foam_header(cls, obj, "0") + f"dimensions      {dimensions};\n\n"
            + f"internalField   {internal};\n\n"
            + "boundaryField\n{\n" + body + "}\n")


def initial_fields(mach: float, alpha_deg: float, state: dict[str, float]) -> dict[str, str]:
    rad = math.radians(alpha_deg)
    u_inf = state["u_inf"]
    u_vec = f"({u_inf * math.cos(rad):.6f} {u_inf * math.sin(rad):.6f} 0)"
    empty = "        type            empty;\n"

    def bc(*lines: str) -> str:
        return "".join(f"        {line}\n" for line in lines)

    farfield = {}
    for patch in ("inflow", "outflow"):
        farfield[patch] = None  # filled per field below

    u = _field("volVectorField", "U", "[0 1 -1 0 0 0 0]", f"uniform {u_vec}", {
        "inflow": bc("type            freestreamVelocity;",
                     f"freestreamValue uniform {u_vec};",
                     f"value           uniform {u_vec};"),
        "outflow": bc("type            freestreamVelocity;",
                      f"freestreamValue uniform {u_vec};",
                      f"value           uniform {u_vec};"),
        "airfoil": bc("type            noSlip;"),
        "frontAndBack": empty,
    })
    p = _field("volScalarField", "p", "[1 -1 -2 0 0 0 0]", f"uniform {P_INF:.6g}", {
        "inflow": bc("type            freestreamPressure;",
                     f"freestreamValue uniform {P_INF:.6g};"),
        "outflow": bc("type            freestreamPressure;",
                      f"freestreamValue uniform {P_INF:.6g};"),
        "airfoil": bc("type            zeroGradient;"),
        "frontAndBack": empty,
    })
    t = _field("volScalarField", "T", "[0 0 0 1 0 0 0]", f"uniform {T_INF:.6g}", {
        "inflow": bc("type            inletOutlet;",
                     f"inletValue      uniform {T_INF:.6g};",
                     f"value           uniform {T_INF:.6g};"),
        "outflow": bc("type            inletOutlet;",
                      f"inletValue      uniform {T_INF:.6g};",
                      f"value           uniform {T_INF:.6g};"),
        "airfoil": bc("type            zeroGradient;"),
        "frontAndBack": empty,
    })
    k_inf, omega_inf, nut_inf = state["k_inf"], state["omega_inf"], state["nut_inf"]
    k = _field("volScalarField", "k", "[0 2 -2 0 0 0 0]", f"uniform {k_inf:.6g}", {
        "inflow": bc("type            inletOutlet;",
                     f"inletValue      uniform {k_inf:.6g};",
                     f"value           uniform {k_inf:.6g};"),
        "outflow": bc("type            inletOutlet;",
                      f"inletValue      uniform {k_inf:.6g};",
                      f"value           uniform {k_inf:.6g};"),
        "airfoil": bc("type            kqRWallFunction;",
                      f"value           uniform {k_inf:.6g};"),
        "frontAndBack": empty,
    })
    omega = _field("volScalarField", "omega", "[0 0 -1 0 0 0 0]", f"uniform {omega_inf:.6g}", {
        "inflow": bc("type            inletOutlet;",
                     f"inletValue      uniform {omega_inf:.6g};",
                     f"value           uniform {omega_inf:.6g};"),
        "outflow": bc("type            inletOutlet;",
                      f"inletValue      uniform {omega_inf:.6g};",
                      f"value           uniform {omega_inf:.6g};"),
        "airfoil": bc("type            omegaWallFunction;",
                      f"value           uniform {omega_inf:.6g};"),
        "frontAndBack": empty,
    })
    nut = _field("volScalarField", "nut", "[0 2 -1 0 0 0 0]", f"uniform {nut_inf:.6g}", {
        "inflow": bc("type            calculated;", "value           uniform 0;"),
        "outflow": bc("type            calculated;", "value           uniform 0;"),
        "airfoil": bc("type            nutkWallFunction;", "value           uniform 0;"),
        "frontAndBack": empty,
    })
    alphat = _field("volScalarField", "alphat", "[1 -1 -1 0 0 0 0]", "uniform 0", {
        "inflow": bc("type            calculated;", "value           uniform 0;"),
        "outflow": bc("type            calculated;", "value           uniform 0;"),
        "airfoil": bc("type            compressible::alphatWallFunction;",
                      "value           uniform 0;"),
        "frontAndBack": empty,
    })
    return {"U": u, "p": p, "T": t, "k": k, "omega": omega, "nut": nut, "alphat": alphat}


# --------------------------------------------------------------------------
# Case assembly + run
# --------------------------------------------------------------------------

def build_case(case_dir: Path, *, mach: float, alpha_deg: float, reynolds: float,
              iterations: int = 500) -> dict[str, Any]:
    case = Path(case_dir)
    for sub in ("0", "constant", "system"):
        (case / sub).mkdir(parents=True, exist_ok=True)

    state = freestream_state(mach, reynolds)
    rad = math.radians(alpha_deg)
    drag_dir = f"({math.cos(rad):.8f} {math.sin(rad):.8f} 0)"
    lift_dir = f"({-math.sin(rad):.8f} {math.cos(rad):.8f} 0)"

    (case / "system" / "blockMeshDict").write_text(transonic_blockmesh_dict(LEVEL))
    (case / "system" / "fvSchemes").write_text(fv_schemes())
    (case / "system" / "fvSolution").write_text(fv_solution())
    control = control_dict(iterations, rho_inf=state["rho_inf"], u_inf=state["u_inf"],
                           drag_dir=drag_dir, lift_dir=lift_dir)
    (case / "system" / "controlDict").write_text(control)
    (case / "constant" / "thermophysicalProperties").write_text(
        thermophysical_properties(state["mu"]))
    (case / "constant" / "turbulenceProperties").write_text(_TURBULENCE_PROPERTIES)
    for name, text in initial_fields(mach, alpha_deg, state).items():
        (case / "0" / name).write_text(text)
    return {"mach": mach, "alpha_deg": alpha_deg, "reynolds": reynolds,
            "iterations": iterations, "cells": LEVEL.cells, **state}


def parse_wall_p_raw(text: str, p_inf: float, q_inf: float) -> list[tuple[float, float]]:
    """(x, Cp) pairs from a raw-format patch sample of p, sorted by x."""
    profile: list[tuple[float, float]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split()
        if len(parts) < 4:
            continue
        try:
            x, p = float(parts[0]), float(parts[3])
        except ValueError:
            continue
        profile.append((x, (p - p_inf) / q_inf))
    return sorted(profile)


def shock_location(profile: list[tuple[float, float]], *, x_lo: float = 0.05,
                   x_hi: float = 0.95) -> dict[str, float] | None:
    """Steepest recompression (max positive dCp/dx) on one surface within
    [x_lo, x_hi] -- the shock foot. None if the profile is too sparse."""
    window = [(x, cp) for x, cp in profile if x_lo <= x <= x_hi]
    if len(window) < 3:
        return None
    best = None
    for (x0, c0), (x1, c1) in zip(window, window[1:]):
        if x1 == x0:
            continue
        slope = (c1 - c0) / (x1 - x0)
        if best is None or slope > best[1]:
            best = (0.5 * (x0 + x1), slope)
    if best is None:
        return None
    return {"x_over_c": best[0], "dcp_dx": best[1]}


def run_case(*, mach: float, alpha_deg: float, reynolds: float, work_dir: Path,
            iterations: int = 500, timeout: float = 900.0,
            log: Callable[[str], None] = print) -> dict[str, Any]:
    case = Path(work_dir)
    if case.exists():
        shutil.rmtree(case, ignore_errors=True)
    case.mkdir(parents=True, exist_ok=True)
    params = build_case(case, mach=mach, alpha_deg=alpha_deg, reynolds=reynolds,
                        iterations=iterations)

    timings: dict[str, float] = {}
    for step, args in (("blockMesh", ["blockMesh"]), ("checkMesh", ["checkMesh"])):
        start = time.monotonic()
        result = _foam(args, case, f"log.{step}", timeout=300)
        timings[step] = round(time.monotonic() - start, 1)
        if step == "blockMesh" and result.returncode != 0:
            tail = (case / f"log.{step}").read_text(errors="replace")
            raise RuntimeError(f"naca-transonic: blockMesh failed:\n"
                               + "\n".join(tail.splitlines()[-20:]))

    start = time.monotonic()
    result = _foam(["rhoSimpleFoam"], case, "log.rhoSimpleFoam", timeout=timeout)
    timings["rhoSimpleFoam"] = round(time.monotonic() - start, 1)
    log_text = (case / "log.rhoSimpleFoam").read_text(errors="replace")
    if result.returncode != 0:
        raise RuntimeError("naca-transonic: rhoSimpleFoam failed:\n"
                           + "\n".join(log_text.splitlines()[-25:]))

    coeff_files = sorted((case / "postProcessing" / "forceCoeffs1").rglob("coefficient*.dat"))
    if not coeff_files:
        raise RuntimeError("naca-transonic: no forceCoeffs output")
    dat_text = coeff_files[-1].read_text(errors="replace")
    cd = final_coefficient(dat_text, "Cd")
    cl = final_coefficient(dat_text, "Cl")
    if cd is None or cl is None:
        raise RuntimeError("naca-transonic: Cd/Cl not found in forceCoeffs output")
    # The pressure/viscous split comes from the solver log's own printed
    # "Coefficient Total Pressure Viscous Internal" table (parse_force_split),
    # NOT from the coefficient.dat file's "Cd(f)"/"Cd(r)" columns -- measured
    # directly: for this case those two do not even sum to Cd (e.g. one run
    # logged Cd=0.432 but Cd(f)+Cd(r) = -0.329 + 0.761 = 0.432 in appearance,
    # yet the SAME columns for the cylinder family split roughly in half by
    # geometric front/rear, not by pressure/viscous -- an OpenFOAM column
    # whose meaning is not the one this task needs, so it is not used here).
    split = parse_force_split(log_text, "Cd")
    history = parse_coefficient_history(dat_text)

    surf_files = sorted((case / "postProcessing" / "surfaceP").rglob("*.raw"))
    upper_shock = lower_shock = None
    if surf_files:
        state = freestream_state(mach, reynolds)
        # naca surface points are in (x, y) with y = +/-thickness; split by
        # sign of the sampled y-coordinate to separate upper/lower surfaces.
        upper_pts, lower_pts = _split_upper_lower(surf_files[-1].read_text(errors="replace"),
                                                   P_INF, state["q_inf"])
        upper_shock = shock_location(upper_pts)
        lower_shock = shock_location(lower_pts)

    record = {
        "mach": mach, "alpha_deg": alpha_deg, "reynolds": reynolds,
        "cells": params["cells"], "iterations": iterations,
        "iterations_actual": len(history.get("Cd", [])),
        "cd": cd["value"], "cd_spread": cd["spread"],
        "cl": cl["value"], "cl_spread": cl["spread"],
        "cd_pressure": split["pressure"] if split else None,
        "cd_viscous": split["viscous"] if split else None,
        "upper_shock_x_over_c": upper_shock["x_over_c"] if upper_shock else None,
        "lower_shock_x_over_c": lower_shock["x_over_c"] if lower_shock else None,
        "wall_seconds": sum(timings.values()), "timings": timings,
    }
    log(f"[naca-transonic M{mach:g}a{alpha_deg:g}Re{reynolds:.3g}] "
        f"Cd {cd['value']:.5f} (spread {cd['spread']:.2e}), "
        f"Cl {cl['value']:.5f}, upper shock x/c="
        f"{record['upper_shock_x_over_c']}")
    return record


def _split_upper_lower(text: str, p_inf: float, q_inf: float
                       ) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    upper, lower = [], []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split()
        if len(parts) < 4:
            continue
        try:
            x, y, p = float(parts[0]), float(parts[1]), float(parts[3])
        except ValueError:
            continue
        cp = (p - p_inf) / q_inf
        (upper if y >= 0 else lower).append((x, cp))
    return sorted(upper), sorted(lower)
