"""RAE 2822 transonic aerofoil, AGARD AR-138 Case 9 -- compressible RANS
against digitised experiment.

WHAT THIS IS AND WHY IT EXISTS
------------------------------
``workflows.transonic_airfoil`` records, in its own docstring, that the lab
chose a NACA 0012 for its transonic family because no citable digitised
RAE 2822 Cp dataset could be sourced inside one task's budget, and that no
RAE 2822 comparison is therefore claimed anywhere. That dataset has since been
sourced and validated; see
``demo-output/website/campaign/F12_runs/reference/decode_tape.py`` for its
provenance and the four checks it passes before being admitted.

This module is the case built on it. Unlike F2 (a NACA 0012 graded on shock
POSITION alone, against a literature-recalled inviscid number, in a band), this
is a point comparison of the whole surface pressure distribution, the shock
location and the integrated coefficients against experiment.

THE WALL-INTERFERENCE CORRECTION, WHICH IS THE CLASSIC TRAP ON THIS CASE
------------------------------------------------------------------------
Case 9 was run in a slotted-wall tunnel and its published conditions circulate
in more than one corrected form. Two are used here, both stated, both solved:

  ``TAPE``      M = 0.730, alpha = 2.79 deg.  This is what the reference data
                itself carries. The AFOSR-HTTM tape stores XMREF (free-stream
                Mach) = 0.730, ALPHAG (geometric incidence) = 3.19 deg and
                ALPHAC (corrected incidence) = 2.79 deg for case 9. The
                correction is applied to INCIDENCE ONLY; there is one Mach
                number on the tape and it is the measured one. The Cp values
                are non-dimensionalised on that same measured free stream.

  ``WORKSHOP``  M = 0.734, alpha = 2.79 deg.  The 1st-5th International
                Workshops on High-Order CFD Methods specify case C2.2 (also
                ADIGMA MTC5) at "corrected flow conditions, namely Mach number
                M = 0.734, angle of attack = 2.79 deg, with the same Reynolds
                number", i.e. the same incidence correction plus a Mach
                correction of +0.004.
                https://cfd.ku.edu/hiocfd/case_c2.2.html

The incidence correction is identical in both; only the Mach differs, by 0.004.
The workshop condition is the primary solve here because it is the one the
external community grades against, and the tape condition is solved as well so
the sensitivity to the disagreement is measured rather than assumed. Getting
this wrong is how a confident wrong answer is produced on this case, so both
numbers travel with every result.

A third convention, M = 0.734 with alpha = 2.54 deg, also appears in the
literature. It is NOT used here: 2.54 deg is the tape's corrected incidence for
case 6, not case 9, and pairing it with case 9's Mach number is a conflation.

MODELLING CHOICES THAT ARE CHOICES, NOT MEASUREMENTS
-----------------------------------------------------
* Fully turbulent. The experiment tripped transition at 3% chord (tape file 3,
  ``trip_x_over_c`` = 0.03) and the workshop specifies transition fixed at 3%
  chord on both surfaces. This solve does not model transition; at Re = 6.5e6
  with a trip that far forward the laminar run is a small fraction of the
  chord. Documented, not hidden.
* Free-stream turbulence is not published for this experiment. The values used
  are the NASA Turbulence Modeling Resource's standard far-field state for
  k-omega SST -- eddy-viscosity ratio 0.009, k = 9e-9 a_inf^2,
  omega = 1e-6 rho_inf a_inf^2 / mu_inf -- which is a cited convention rather
  than a guess. See ``freestream_state``.
* Free air. The tunnel walls are not modelled; that is what the corrected
  conditions above exist to stand in for.
"""

from __future__ import annotations

import math
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from workflows.tmr_verification import (
    ratio_for_first_cell, _foam, _foam_header, final_coefficient,
    parse_force_split,
)
from chief_engineer.head_engineer import parse_coefficient_history

# --------------------------------------------------------------------------
# Reference data
# --------------------------------------------------------------------------

REFERENCE_DIR = (Path(__file__).resolve().parents[2] / "demo-output" / "website"
                 / "campaign" / "F12_runs" / "reference")

# Straight from the tape, and re-derivable at any time by running
# reference/decode_tape.py. Quoted here so the workflow can state them without
# reparsing 237 kB of tape image on every call.
EXPERIMENT = {
    "case": 9,
    "mach_uncorrected": 0.730,
    "alpha_geometric_deg": 3.19,
    "alpha_corrected_deg": 2.79,
    "reynolds": 6.5e6,
    "trip_x_over_c": 0.03,
    "CN": 0.8030,
    "CM": -0.0990,
    "CD": 0.0168,
    "cp_tap_uncertainty": 0.0026,
    "source": ("Cook, McDonald & Firmin, AGARD AR-138 (1979); digitised as "
               "AFOSR-HTTM/Stanford flow 8621, hosted by the NASA Turbulence "
               "Modeling Resource"),
}

CONDITIONS = {
    # name -> (Mach, alpha_deg, what it is)
    "workshop": (0.734, 2.79, "International Workshop on High-Order CFD "
                              "Methods case C2.2 corrected conditions"),
    "tape": (0.730, 2.79, "AFOSR-HTTM tape: measured Mach, corrected incidence"),
}

GAMMA = 1.4
R_AIR = 287.05
P_INF = 101_325.0
T_INF = 300.0
CHORD = 1.0


def load_experiment_cp() -> dict[str, list[tuple[float, float]]]:
    """The digitised Case 9 taps, (x/c, Cp) per surface, sorted by x/c."""
    out = {}
    for surface in ("upper", "lower"):
        path = REFERENCE_DIR / f"rae2822_case9_cp_{surface}.dat"
        pts = []
        for line in path.read_text().splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            x, cp = line.split()
            pts.append((float(x), float(cp)))
        out[surface] = sorted(pts)
    return out


def load_coordinates() -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    """(upper, lower) design ordinates, (x/c, y/c), leading edge first."""
    upper, lower = [], []
    path = REFERENCE_DIR / "rae2822_coordinates.dat"
    for line in path.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        x, yu, yl = (float(v) for v in line.split())
        upper.append((x, yu))
        lower.append((x, yl))
    return upper, lower


# --------------------------------------------------------------------------
# Surface geometry
# --------------------------------------------------------------------------

class _SurfaceSpline:
    """y(x) for one aerofoil surface, splined against sqrt(x).

    A rounded leading edge has y ~ sqrt(x), whose derivative is unbounded at
    x = 0, so a spline built directly on x oscillates over the first few
    stations. Splining against t = sqrt(x) makes the leading edge locally
    LINEAR in the spline variable and removes that failure mode.

    The interpolant is a not-a-knot cubic, which is C2. A shape-preserving
    PCHIP was tried first, on the usual reasoning that it cannot invent a
    wiggle between two tabulated points. Measured on this table, that reasoning
    inverts: PCHIP is only C1, so surface curvature jumps at all 65 knots, and
    over 0.2 < x/c < 0.6 -- which is exactly where this case's shock stands --
    it returns a curvature range of -1.415 to +0.271 with steps up to 1.379,
    i.e. it flattens segments between knots and reverses the sign of the
    curvature on a section that is convex there. The cubic returns -0.672 to
    -0.322 over the same interval with steps of 0.004. Curvature kinks on an
    aerofoil surface print as pressure kinks, so the smoother interpolant is
    the honest one here and the shape-preserving argument does not survive
    contact with the data.
    """

    def __init__(self, points: list[tuple[float, float]]):
        from scipy.interpolate import CubicSpline

        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        self._x_max = xs[-1]
        self._spline = CubicSpline([math.sqrt(x) for x in xs], ys)

    def __call__(self, x: float) -> float:
        return float(self._spline(math.sqrt(max(0.0, min(x, self._x_max)))))


@dataclass(frozen=True)
class Section:
    upper: _SurfaceSpline
    lower: _SurfaceSpline

    def y(self, x: float, sign: float) -> float:
        return self.upper(x) if sign > 0 else self.lower(x)


def rae_section() -> Section:
    upper, lower = load_coordinates()
    return Section(_SurfaceSpline(upper), _SurfaceSpline(lower))


def surface_points(section: Section, x_lo: float, x_hi: float, sign: float,
                   n: int = 240) -> list[tuple[float, float]]:
    """Interior points of one surface segment, cosine-clustered toward both
    segment ends so the polyLine is densest where curvature lives."""
    pts = []
    for i in range(1, n):
        t = 0.5 * (1.0 - math.cos(math.pi * i / n))
        x = x_lo + (x_hi - x_lo) * t
        pts.append((x, section.y(x, sign)))
    return pts


# --------------------------------------------------------------------------
# Mesh ladder
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class GridLevel:
    name: str
    n_surf_quarter: int   # cells per quarter of the surface (4 quarters)
    n_wake: int           # streamwise cells in each wake block
    ny: int               # wall-normal cells

    @property
    def cells(self) -> int:
        return (4 * self.n_surf_quarter + 2 * self.n_wake) * self.ny


# A clean factor-2 ladder in every direction, so an observed order of
# convergence is meaningful on it.
LEVELS = (
    GridLevel("coarse", 48, 48, 80),     # 23,040 cells
    GridLevel("medium", 96, 96, 160),    # 92,160 cells
    GridLevel("fine", 192, 192, 320),    # 368,640 cells
)

FARFIELD_R = 50.0     # chords, circular outer boundary centred on the TE
WAKE_LEN = 50.0       # chords of rectangular extension downstream
E_LE = 50.0           # mid-chord to leading-edge surface spacing ratio
E_TE = 4.0            # mid-chord to trailing-edge surface spacing ratio
FIRST_CELL = 2.0e-6   # wall-normal first cell in chords; y+ ~ 0.5 at Re 6.5e6


def _wake_ratio(level: GridLevel, wake_len: float) -> float:
    """Total wake expansion so the first wake cell matches the surface
    trailing-edge streamwise spacing."""
    seg = 0.502
    r = (1.0 / E_TE) ** (1.0 / (level.n_surf_quarter - 1))
    first = seg * (r - 1.0) / (r ** level.n_surf_quarter - 1.0)
    te_spacing = first * r ** (level.n_surf_quarter - 1)
    return ratio_for_first_cell(wake_len, level.n_wake, te_spacing)


def blockmesh_dict(section: Section, level: GridLevel, *,
                   farfield_r: float = FARFIELD_R, wake_len: float = WAKE_LEN,
                   first_cell: float = FIRST_CELL) -> str:
    """O-grid around the section plus a rectangular wake extension.

    Topology is the one already exercised by ``workflows.transonic_airfoil``
    (four quarter blocks around the surface, split at the leading edge, both
    mid-chord points and the trailing edge, plus upper and lower wake blocks),
    generalised from that module's analytic symmetric thickness law to an
    arbitrary cambered section read from a coordinate table. The two mid-chord
    block corners therefore sit at (0.5, y_upper(0.5)) and (0.5, y_lower(0.5))
    rather than at +/- the same thickness.
    """
    R, W = farfield_r, farfield_r + wake_len
    r_y = ratio_for_first_cell(R, level.ny, first_cell)
    r_y_far = ratio_for_first_cell(R, level.ny, min(0.3, 0.3 * farfield_r / 25.0))
    r_wake = _wake_ratio(level, wake_len)
    y_up_mid = section.y(0.5, +1.0)
    y_lo_mid = section.y(0.5, -1.0)
    c45 = R / math.sqrt(2.0)

    def arc_point(deg: float) -> str:
        rad = math.radians(deg)
        return f"({1.0 + R * math.cos(rad):.10g} {R * math.sin(rad):.10g}"

    def poly(points: list[tuple[float, float]], z: float) -> str:
        inner = "\n".join(f"        ({x:.10g} {y:.10g} {z})" for x, y in points)
        return f"(\n{inner}\n    )"

    up_front = surface_points(section, 0.0, 0.5, +1.0)
    up_rear = surface_points(section, 0.5, 1.0, +1.0)
    lo_front = surface_points(section, 0.0, 0.5, -1.0)
    lo_rear = surface_points(section, 0.5, 1.0, -1.0)
    ns, nw, ny = level.n_surf_quarter, level.n_wake, level.ny

    lines = [_foam_header("dictionary", "blockMeshDict", "system"), """
scale   1;

vertices
("""]
    base = [
        (1.0, 0.0), (0.0, 0.0), (0.5, y_up_mid), (0.5, y_lo_mid),
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
        simpleGrading ({E_LE:.8g} {r_y:.8g} 1)
    hex (2 0 6 5 14 12 18 17) ({ns} {ny} 1)
        simpleGrading ({1.0 / E_TE:.8g} {r_y:.8g} 1)
    hex (0 3 7 8 12 15 19 20) ({ns} {ny} 1)
        simpleGrading ({E_TE:.8g} {r_y:.8g} 1)
    hex (3 1 4 7 15 13 16 19) ({ns} {ny} 1)
        simpleGrading ({1.0 / E_LE:.8g} {r_y:.8g} 1)
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
    lines.append("""
);

boundary
(
    aerofoil
    {
        type wall;
        faces ((1 2 14 13) (2 0 12 14) (0 3 15 12) (3 1 13 15));
    }
    inflow
    {
        type patch;
        faces
        (
            (4 5 17 16) (5 6 18 17) (8 7 19 20) (7 4 16 19)
            (11 8 20 23)
        );
    }
    outflow
    {
        type patch;
        faces ((6 10 22 18) (9 10 22 21) (9 11 23 21));
    }
    frontAndBack
    {
        type empty;
        faces
        (
            (1 2 5 4) (2 0 6 5) (0 3 7 8) (3 1 4 7)
            (0 9 10 6) (9 0 8 11)
            (13 14 17 16) (14 12 18 17) (12 15 19 20) (15 13 16 19)
            (12 21 22 18) (21 12 20 23)
        );
    }
);
""")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# Free-stream state
# --------------------------------------------------------------------------

def freestream_state(mach: float, reynolds: float, *, p_inf: float = P_INF,
                     t_inf: float = T_INF) -> dict[str, float]:
    """Dimensional free-stream state realising (Mach, Re) at chord = 1.

    Turbulence far field follows the NASA Turbulence Modeling Resource's
    standard k-omega SST condition rather than an assumed tunnel turbulence
    level: mu_t/mu = 0.009, k = 9e-9 a_inf^2, omega = 1e-6 rho_inf a_inf^2 /
    mu_inf. Those three are mutually consistent by construction, since
    nu_t = k/omega = 0.009 mu/rho.
    """
    a_inf = math.sqrt(GAMMA * R_AIR * t_inf)
    u_inf = mach * a_inf
    rho_inf = p_inf / (R_AIR * t_inf)
    mu = rho_inf * u_inf * CHORD / reynolds
    nu = mu / rho_inf
    k_inf = 9.0e-9 * a_inf ** 2
    omega_inf = 1.0e-6 * rho_inf * a_inf ** 2 / mu
    return {
        "a_inf": a_inf, "u_inf": u_inf, "rho_inf": rho_inf, "mu": mu, "nu": nu,
        "k_inf": k_inf, "omega_inf": omega_inf, "nut_inf": k_inf / omega_inf,
        "q_inf": 0.5 * rho_inf * u_inf ** 2,
    }


# --------------------------------------------------------------------------
# constant/* and system/*
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
        molWeight   28.96;
    }}
    thermodynamics
    {{
        Cp          1004.5;
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


def fv_solution(residual: float = 1.0e-6) -> str:
    return _foam_header("dictionary", "fvSolution") + f"""
solvers
{{
    p
    {{
        solver          GAMG;
        smoother        GaussSeidel;
        tolerance       1e-8;
        relTol          0.01;
    }}
    "(U|k|omega|e)"
    {{
        solver          PBiCGStab;
        preconditioner  DILU;
        tolerance       1e-9;
        relTol          0.1;
    }}
}}

SIMPLE
{{
    residualControl
    {{
        p               {residual:g};
        U               {residual:g};
        "(k|omega|e)"   {residual:g};
    }}
    nNonOrthogonalCorrectors 1;
    pMinFactor      0.1;
    pMaxFactor      2;
}}

relaxationFactors
{{
    fields
    {{
        p               0.3;
        rho             0.05;
    }}
    equations
    {{
        U               0.3;
        e               0.5;
        "(k|omega)"     0.5;
    }}
}}
"""


def control_dict(iterations: int, *, rho_inf: float, u_inf: float,
                 alpha_deg: float, write_interval: int | None = None) -> str:
    """Aref is chord x span. The mesh is one cell thick between z = 0 and
    z = 1, so span = 1 chord and Aref = 1. (transonic_airfoil records the
    measured consequence of getting this wrong: Aref = 0.1 there put every
    coefficient out by exactly 10x.)"""
    rad = math.radians(alpha_deg)
    drag_dir = f"({math.cos(rad):.10f} {math.sin(rad):.10f} 0)"
    lift_dir = f"({-math.sin(rad):.10f} {math.cos(rad):.10f} 0)"
    return _foam_header("dictionary", "controlDict") + f"""
application     rhoSimpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {iterations};
deltaT          1;
writeControl    timeStep;
writeInterval   {write_interval or iterations};
purgeWrite      1;
writeFormat     ascii;
writePrecision  10;
timeFormat      general;
timePrecision   6;
runTimeModifiable false;

functions
{{
    forceCoeffs1
    {{
        type            forceCoeffs;
        libs            (forces);
        writeControl    timeStep;
        writeInterval   1;
        patches         (aerofoil);
        rho             rho;
        rhoInf          {rho_inf:.10g};
        magUInf         {u_inf:.10g};
        lRef            {CHORD};
        Aref            {CHORD * 1.0};
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
            aerofoil {{ type patch; patches (aerofoil); }}
        );
    }}
    yPlus
    {{
        type            yPlus;
        libs            (fieldFunctionObjects);
        executeControl  onEnd;
        writeControl    onEnd;
    }}
    machNo
    {{
        type            MachNo;
        libs            (fieldFunctionObjects);
        executeControl  onEnd;
        writeControl    onEnd;
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


def initial_fields(alpha_deg: float, state: dict[str, float]) -> dict[str, str]:
    rad = math.radians(alpha_deg)
    u_inf = state["u_inf"]
    u_vec = f"({u_inf * math.cos(rad):.8f} {u_inf * math.sin(rad):.8f} 0)"
    empty = "        type            empty;\n"

    def bc(*lines: str) -> str:
        return "".join(f"        {line}\n" for line in lines)

    def far(kind: str, value: str) -> dict[str, str]:
        return {p: bc(f"type            {kind};", f"inletValue      uniform {value};",
                      f"value           uniform {value};")
                for p in ("inflow", "outflow")}

    k_inf, omega_inf, nut_inf = state["k_inf"], state["omega_inf"], state["nut_inf"]

    fields = {}
    fields["U"] = _field("volVectorField", "U", "[0 1 -1 0 0 0 0]",
                         f"uniform {u_vec}", {
        "inflow": bc("type            freestreamVelocity;",
                     f"freestreamValue uniform {u_vec};",
                     f"value           uniform {u_vec};"),
        "outflow": bc("type            freestreamVelocity;",
                      f"freestreamValue uniform {u_vec};",
                      f"value           uniform {u_vec};"),
        "aerofoil": bc("type            noSlip;"),
        "frontAndBack": empty})
    fields["p"] = _field("volScalarField", "p", "[1 -1 -2 0 0 0 0]",
                         f"uniform {P_INF:.10g}", {
        "inflow": bc("type            freestreamPressure;",
                     f"freestreamValue uniform {P_INF:.10g};"),
        "outflow": bc("type            freestreamPressure;",
                      f"freestreamValue uniform {P_INF:.10g};"),
        "aerofoil": bc("type            zeroGradient;"),
        "frontAndBack": empty})
    fields["T"] = _field("volScalarField", "T", "[0 0 0 1 0 0 0]",
                         f"uniform {T_INF:.10g}",
                         {**far("inletOutlet", f"{T_INF:.10g}"),
                          "aerofoil": bc("type            zeroGradient;"),
                          "frontAndBack": empty})
    # Wall-resolved treatment: the first cell sits at y+ ~ 0.5, so k is driven
    # to zero at the wall and nut is not modelled by a log-law bridge.
    fields["k"] = _field("volScalarField", "k", "[0 2 -2 0 0 0 0]",
                         f"uniform {k_inf:.8g}",
                         {**far("inletOutlet", f"{k_inf:.8g}"),
                          "aerofoil": bc("type            kLowReWallFunction;",
                                         f"value           uniform {k_inf:.8g};"),
                          "frontAndBack": empty})
    fields["omega"] = _field("volScalarField", "omega", "[0 0 -1 0 0 0 0]",
                             f"uniform {omega_inf:.8g}",
                             {**far("inletOutlet", f"{omega_inf:.8g}"),
                              "aerofoil": bc("type            omegaWallFunction;",
                                             f"value           uniform {omega_inf:.8g};"),
                              "frontAndBack": empty})
    fields["nut"] = _field("volScalarField", "nut", "[0 2 -1 0 0 0 0]",
                           f"uniform {nut_inf:.8g}", {
        "inflow": bc("type            calculated;", "value           uniform 0;"),
        "outflow": bc("type            calculated;", "value           uniform 0;"),
        "aerofoil": bc("type            nutLowReWallFunction;",
                       "value           uniform 0;"),
        "frontAndBack": empty})
    fields["alphat"] = _field("volScalarField", "alphat", "[1 -1 -1 0 0 0 0]",
                              "uniform 0", {
        "inflow": bc("type            calculated;", "value           uniform 0;"),
        "outflow": bc("type            calculated;", "value           uniform 0;"),
        "aerofoil": bc("type            compressible::alphatWallFunction;",
                       "value           uniform 0;"),
        "frontAndBack": empty})
    return fields


# --------------------------------------------------------------------------
# Mesh quality gate (docs/standards/MESH_STANDARD.md)
# --------------------------------------------------------------------------

MAX_NON_ORTHOGONALITY = 70.0   # checkMesh's own nonOrthThreshold_
MAX_SKEWNESS = 4.0             # checkMesh's own skewThreshold_, boundary faces included


def parse_check_mesh(text: str) -> dict[str, Any]:
    """The quality numbers the lab's mesh standard gates on, plus the counts
    checkMesh prints, straight out of a log."""
    out: dict[str, Any] = {"failed_checks": []}
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("Max cell openness") and "aspect ratio" in s:
            out["max_aspect_ratio"] = float(s.split("=")[-1].split()[0].rstrip("."))
        elif "Mesh non-orthogonality Max:" in s:
            parts = s.split()
            out["max_non_orthogonality"] = float(parts[parts.index("Max:") + 1])
        elif s.startswith("Max skewness ="):
            out["max_skewness"] = float(s.split("=")[1].split()[0].rstrip("."))
        elif s.startswith("cells:"):
            out.setdefault("cells", int(s.split()[-1]))
        elif "***" in s:
            out["failed_checks"].append(s.lstrip("* ").strip())
        elif s.startswith("Mesh OK"):
            out["mesh_ok"] = True
    return out


def mesh_gate(quality: dict[str, Any]) -> dict[str, Any]:
    breaches = []
    nonortho = quality.get("max_non_orthogonality")
    skew = quality.get("max_skewness")
    if nonortho is None or nonortho > MAX_NON_ORTHOGONALITY:
        breaches.append(f"max non-orthogonality {nonortho} > {MAX_NON_ORTHOGONALITY}")
    if skew is None or skew > MAX_SKEWNESS:
        breaches.append(f"max skewness {skew} > {MAX_SKEWNESS}")
    return {"passed": not breaches, "breaches": breaches,
            "max_non_orthogonality": nonortho, "max_skewness": skew,
            "max_aspect_ratio": quality.get("max_aspect_ratio"),
            # Aspect ratio is advisory per the mesh standard: reference-grade
            # wall-resolved grids run to 7e4 and a hard gate at 1000 would
            # reject all of them. It is recorded, with its alignment
            # justification (anisotropy is wall-normal, on orthogonal cells).
            "aspect_ratio_gated": False}


# --------------------------------------------------------------------------
# Surface pressure extraction and shock detection
# --------------------------------------------------------------------------

def split_surfaces(raw_text: str, section: Section, p_inf: float, q_inf: float
                   ) -> dict[str, list[tuple[float, float]]]:
    """(x/c, Cp) per surface from a raw patch sample of p.

    Assignment is by proximity to each surface spline, NOT by the sign of y.
    The RAE 2822 has aft camber: its lower surface crosses above the chord line
    near x/c = 0.93 and stays there to the trailing edge, so a sign-of-y split
    silently moves the last few percent of the lower surface onto the upper
    one, exactly where the trailing-edge pressures are being compared.
    """
    upper, lower = [], []
    for line in raw_text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        if len(parts) < 4:
            continue
        try:
            x, y, p = float(parts[0]), float(parts[1]), float(parts[3])
        except ValueError:
            continue
        cp = (p - p_inf) / q_inf
        du = abs(y - section.y(x, +1.0))
        dl = abs(y - section.y(x, -1.0))
        (upper if du <= dl else lower).append((x, cp))
    return {"upper": sorted(upper), "lower": sorted(lower)}


def sonic_cp(mach: float) -> float:
    """Critical pressure coefficient: the Cp at which the local flow is sonic."""
    t = (1.0 + 0.5 * (GAMMA - 1.0) * mach * mach) / (1.0 + 0.5 * (GAMMA - 1.0))
    return (t ** (GAMMA / (GAMMA - 1.0)) - 1.0) / (0.5 * GAMMA * mach * mach)


def shock_location(profile: list[tuple[float, float]], mach: float, *,
                   x_lo: float = 0.10, x_hi: float = 0.95) -> dict[str, Any] | None:
    """Where the upper-surface shock stands, by two definitions.

    ``steepest``  midpoint of the adjacent sample pair with the largest
                  positive dCp/dx. This is the detector F2 uses, and F2's
                  record documents its failure mode: it can only return values
                  on the sample lattice, so its resolution is the local sample
                  spacing and a deviation smaller than one spacing is not
                  resolved. That spacing is returned alongside as
                  ``steepest_resolution`` and must be quoted with the value.

    ``sonic``     x/c at which Cp crosses the critical value from below on the
                  recompression, found by linear interpolation between the two
                  bracketing samples. This is continuous in x rather than
                  quantised, is defined identically on the experimental taps
                  and on the CFD samples, and is the value graded on.
    """
    window = [(x, cp) for x, cp in profile if x_lo <= x <= x_hi]
    if len(window) < 3:
        return None
    best = None
    for (x0, c0), (x1, c1) in zip(window, window[1:]):
        if x1 <= x0:
            continue
        slope = (c1 - c0) / (x1 - x0)
        if best is None or slope > best[1]:
            best = (0.5 * (x0 + x1), slope, x1 - x0)
    if best is None:
        return None

    cp_star = sonic_cp(mach)
    sonic_x = None
    # walk forward from the strongest recompression and take the first upward
    # crossing of Cp* at or after it
    for (x0, c0), (x1, c1) in zip(window, window[1:]):
        if x1 < best[0]:
            continue
        if c0 < cp_star <= c1:
            sonic_x = x0 + (x1 - x0) * (cp_star - c0) / (c1 - c0)
            break
    return {"steepest_x_over_c": best[0], "steepest_dcp_dx": best[1],
            "steepest_resolution": best[2], "sonic_x_over_c": sonic_x,
            "cp_star": cp_star}


def cp_deviation(cfd: list[tuple[float, float]],
                 experiment: list[tuple[float, float]]) -> dict[str, Any]:
    """RMS and peak deviation of the CFD surface pressure from the measured
    taps, evaluated AT THE TAP LOCATIONS by interpolating the CFD onto them.

    The CFD is the interpolated side on purpose. Interpolating the 50-odd
    experimental taps onto hundreds of CFD faces would invent experimental
    values between taps and then grade against them; interpolating the dense
    CFD onto the sparse taps only ever reads the CFD where it is smooth.
    """
    import numpy as np

    xs = np.array([p[0] for p in cfd])
    cps = np.array([p[1] for p in cfd])
    order = np.argsort(xs)
    xs, cps = xs[order], cps[order]
    ex = np.array([p[0] for p in experiment])
    ey = np.array([p[1] for p in experiment])
    inside = (ex >= xs.min()) & (ex <= xs.max())
    ex, ey = ex[inside], ey[inside]
    interp = np.interp(ex, xs, cps)
    diff = interp - ey
    worst = int(np.argmax(np.abs(diff)))
    return {"n_taps": int(len(ex)),
            "rms": float(np.sqrt(np.mean(diff ** 2))),
            "mean_signed": float(np.mean(diff)),
            "max_abs": float(np.abs(diff).max()),
            "max_abs_at_x": float(ex[worst]),
            "per_tap": [(float(a), float(b), float(c))
                        for a, b, c in zip(ex, ey, interp)]}


# --------------------------------------------------------------------------
# Case assembly and run
# --------------------------------------------------------------------------

def build_case(case_dir: Path, *, mach: float, alpha_deg: float,
               reynolds: float = 6.5e6, level: GridLevel = LEVELS[0],
               iterations: int = 6000, farfield_r: float = FARFIELD_R,
               wake_len: float = WAKE_LEN) -> dict[str, Any]:
    case = Path(case_dir)
    for sub in ("0", "constant", "system"):
        (case / sub).mkdir(parents=True, exist_ok=True)
    section = rae_section()
    state = freestream_state(mach, reynolds)

    (case / "system" / "blockMeshDict").write_text(
        blockmesh_dict(section, level, farfield_r=farfield_r, wake_len=wake_len))
    (case / "system" / "fvSchemes").write_text(fv_schemes())
    (case / "system" / "fvSolution").write_text(fv_solution())
    (case / "system" / "controlDict").write_text(
        control_dict(iterations, rho_inf=state["rho_inf"],
                     u_inf=state["u_inf"], alpha_deg=alpha_deg))
    (case / "constant" / "thermophysicalProperties").write_text(
        thermophysical_properties(state["mu"]))
    (case / "constant" / "turbulenceProperties").write_text(_TURBULENCE_PROPERTIES)
    for name, text in initial_fields(alpha_deg, state).items():
        (case / "0" / name).write_text(text)
    return {"mach": mach, "alpha_deg": alpha_deg, "reynolds": reynolds,
            "level": level.name, "cells_nominal": level.cells,
            "iterations": iterations, "farfield_r": farfield_r, **state}


def solver_converged(log_text: str) -> bool:
    """The solver's own convergence statement, not a residual that looks
    small (LESSONS L-14/L-15)."""
    return "SIMPLE solution converged" in log_text


def run_case(*, mach: float, alpha_deg: float, work_dir: Path,
             reynolds: float = 6.5e6, level: GridLevel = LEVELS[0],
             iterations: int = 6000, farfield_r: float = FARFIELD_R,
             ranks: int = 1, timeout: float = 7200.0,
             log: Callable[[str], None] = print) -> dict[str, Any]:
    case = Path(work_dir)
    if case.exists():
        shutil.rmtree(case, ignore_errors=True)
    case.mkdir(parents=True, exist_ok=True)
    params = build_case(case, mach=mach, alpha_deg=alpha_deg, reynolds=reynolds,
                        level=level, iterations=iterations, farfield_r=farfield_r)
    section = rae_section()
    timings: dict[str, float] = {}

    def step(name: str, args: list[str], limit: float) -> Any:
        start = time.monotonic()
        result = _foam(args, case, f"log.{name}", timeout=limit)
        timings[name] = round(time.monotonic() - start, 1)
        return result

    if step("blockMesh", ["blockMesh"], 1800).returncode != 0:
        raise RuntimeError("rae2822: blockMesh failed:\n" + "\n".join(
            (case / "log.blockMesh").read_text(errors="replace").splitlines()[-25:]))
    step("checkMesh", ["checkMesh"], 1800)
    quality = parse_check_mesh((case / "log.checkMesh").read_text(errors="replace"))
    gate = mesh_gate(quality)

    if ranks > 1:
        (case / "system" / "decomposeParDict").write_text(
            _foam_header("dictionary", "decomposeParDict")
            + f"numberOfSubdomains {ranks};\nmethod scotch;\n")
        step("decomposePar", ["decomposePar"], 1800)
        solve = step("rhoSimpleFoam",
                     ["mpirun", "-np", str(ranks), "rhoSimpleFoam", "-parallel"],
                     timeout)
        step("reconstructPar", ["reconstructPar", "-latestTime"], 1800)
    else:
        solve = step("rhoSimpleFoam", ["rhoSimpleFoam"], timeout)

    log_text = (case / "log.rhoSimpleFoam").read_text(errors="replace")
    if solve.returncode != 0:
        raise RuntimeError("rae2822: rhoSimpleFoam failed:\n"
                           + "\n".join(log_text.splitlines()[-30:]))

    coeff = sorted((case / "postProcessing" / "forceCoeffs1").rglob("coefficient*.dat"))
    if not coeff:
        raise RuntimeError("rae2822: no forceCoeffs output")
    dat = coeff[-1].read_text(errors="replace")
    cd, cl, cm = (final_coefficient(dat, c) for c in ("Cd", "Cl", "CmPitch"))
    if cd is None or cl is None:
        raise RuntimeError("rae2822: Cd/Cl not found in forceCoeffs output")
    history = parse_coefficient_history(dat)

    # Normal force, the quantity the experiment publishes (CN is referred to
    # the CHORD, lift and drag to the free stream).
    rad = math.radians(alpha_deg)
    cn = cl["value"] * math.cos(rad) + cd["value"] * math.sin(rad)

    surfaces = {}
    shock = None
    raw = sorted((case / "postProcessing" / "surfaceP").rglob("*.raw"))
    if raw:
        state = freestream_state(mach, reynolds)
        surfaces = split_surfaces(raw[-1].read_text(errors="replace"), section,
                                  P_INF, state["q_inf"])
        shock = shock_location(surfaces["upper"], mach)

    record = {
        **{k: params[k] for k in ("mach", "alpha_deg", "reynolds", "level",
                                  "iterations", "farfield_r")},
        "cells": quality.get("cells", params["cells_nominal"]),
        "mesh_quality": quality, "mesh_gate": gate,
        "converged": solver_converged(log_text),
        "iterations_run": len(history.get("Cd", [])),
        "cd": cd["value"], "cd_spread": cd["spread"],
        "cl": cl["value"], "cl_spread": cl["spread"],
        "cm": cm["value"] if cm else None,
        "cn": cn,
        "cd_split": parse_force_split(log_text, "Cd"),
        "shock": shock,
        "surfaces": surfaces,
        "ranks": ranks,
        "timings": timings,
        "wall_seconds": sum(timings.values()),
        "core_seconds": sum(v for k, v in timings.items()
                            if k != "rhoSimpleFoam") + timings.get(
                                "rhoSimpleFoam", 0.0) * ranks,
    }
    log("[rae2822 %s M%.3f a%.2f] cells %d  converged %s  Cl %.5f  Cd %.6f  "
        "CN %.5f  shock %s" % (level.name, mach, alpha_deg, record["cells"],
                               record["converged"], record["cl"], record["cd"],
                               cn, shock["sonic_x_over_c"] if shock else None))
    return record
