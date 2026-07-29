"""Family F9 — a real pulsatile CFD solve of flow through the valve orifice.

Replaces the honesty caveat carried by the mega-batch's ``reduced-order``
valve family (``sdk/workflows/valve_study.py``): that family's per-phase
pressure loss comes from an algebraic sharp-orifice correlation
(``dp = 0.5*rho*(Q/(Cd*A))^2``, Cd=0.62), not a solved flow.  This module
solves the flow instead, on an axisymmetric idealization of the valve
geometry.

GEOMETRY. The full three-leaflet valve (``models/curriculum/aortic_valve``)
is not meshed directly here — that is a genuinely 3D, asymmetric leaflet
geometry, and moving it into snappyHexMesh is future work (the FSI item
already on the valve study's own agenda). Instead, the leaflets are frozen
at a chosen opening angle and represented the way the reduced-order model
itself represents them: a sharp-edged axisymmetric orifice plate of the
SAME effective orifice area (``generate_valve.effective_orifice_area``) set
in a pipe of the valve's own root radius. This is the "fixed leaflets"
model-form limit the ROM's own model channel already names — solving that
limit for real is exactly the plug-in point ``valve_study._phase_pressure_loss``
marks, extended from a steady phase point to a genuinely pulsatile cycle.

MESH. A 5-degree wedge (axisymmetric), 5 hex blocks: an upstream pipe
(radius R_pipe) split radially into an inner core (0..R_orifice) and an
outer annulus (R_orifice..R_pipe) that dead-ends into the plate's upstream
face; a short throat block at R_orifice representing the plate itself; and
a downstream pipe, split the same way, whose outer annulus dead-ends into
the plate's downstream face. This produces genuine sharp corners at both
faces of the plate (the vena-contracta-forming geometry the Cd=0.62
correlation itself assumes), without needing a boolean/STL cut.

INFLOW. Sinusoidal, not the ROM's half-sine-with-zero-diastole waveform.
The classical Womersley (1955) closed-form solution for oscillatory pipe
flow is derived for a purely sinusoidal forcing; using a sinusoid directly
lets the Womersley-regime gate compare against that closed form without
first Fourier-decomposing an asymmetric pulse. Q(t) = Q_mean + Q_amp*sin(2 pi
t/T), Q_mean = Q_amp = Q_peak/2, spans [0, Q_peak] — the same flow range the
ROM's three phase points sample — while staying strictly non-negative
(no flow reversal, so no valve/backflow BC complications).

REGIME. The flow is run LAMINAR, not RANS. Two independent reasons converge
on the same choice: (1) the Womersley analytic solution used for the
regime-sanity gate is itself a laminar solution of the linearized
Navier-Stokes equations, so a RANS closure would break direct comparability
with the one closed-form check available; (2) this is a screening
self-consistency exercise, not a validated production solve, and the ROM
being replaced is itself explicit about the physics it drops. Turbulence
is therefore named, not modeled: the pipe Reynolds number at peak flow is
~8.4e3 (the throat is only mildly higher at this opening angle — the
annulus is thin), well into the range where real valve/orifice flow is
transitional-to-turbulent. Any deviation between this laminar CFD and the
ROM's turbulent-asymptote Cd=0.62 correlation has a first-order physical
explanation before a single number is read: laminar CFD cannot capture the
turbulent mixing losses downstream of the vena contracta that the
correlation's Cd implicitly bakes in. Gate 3 checks whether the measured
deviation is consistent with that.
"""

from __future__ import annotations

import math
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

_SDK_ROOT = Path(__file__).resolve().parents[1]
if str(_SDK_ROOT) not in sys.path:
    sys.path.insert(0, str(_SDK_ROOT))

from workflows.tmr_verification import (  # noqa: E402
    _foam_header, _foam, _run_prefix,
    time_weighted_stats, measure_period, halves_drift,
)

_VALVE_DIR = _SDK_ROOT.parent / "models" / "curriculum" / "aortic_valve"
if str(_VALVE_DIR) not in sys.path:
    sys.path.insert(0, str(_VALVE_DIR))
from generate_valve import effective_orifice_area, ROOT_RADIUS  # noqa: E402
from waveform import RHO_BLOOD, NU_BLOOD, Q_PEAK, T_CYCLE  # noqa: E402

# --------------------------------------------------------------------------
# Geometry / physics constants
# --------------------------------------------------------------------------
OPENING_ANGLE_DEG = 65.0          # matched-condition angle (mid-sweep default)
R_PIPE = ROOT_RADIUS              # 0.0115 m, same root radius as the valve study
D_PIPE = 2.0 * R_PIPE
R_ORIFICE = R_PIPE * math.sin(math.radians(OPENING_ANGLE_DEG))
A_PIPE = math.pi * R_PIPE ** 2
A_ORIFICE = effective_orifice_area(OPENING_ANGLE_DEG, R_PIPE)
DISCHARGE_COEFF = 0.62            # same correlation constant as valve_study.py

L_UP = 5.0 * D_PIPE               # upstream straight length
L_THROAT = 0.10 * D_PIPE          # plate thickness
L_DOWN = 8.0 * D_PIPE             # downstream straight length
L_TOTAL = L_UP + L_THROAT + L_DOWN

HALF_ANGLE_DEG = 2.5               # 5 deg total wedge

RHO = RHO_BLOOD
NU = NU_BLOOD

Q_MEAN = Q_PEAK / 2.0
Q_AMP = Q_PEAK / 2.0
U_MEAN = Q_MEAN / A_PIPE
U_AMP = Q_AMP / A_PIPE

# Monitor stations (axial, m from inlet)
X_UPSTREAM_TAP = L_UP - 2.0 * D_PIPE   # "far field" undisturbed tap, 3D from inlet
X_PROFILE = L_UP - 2.0 * D_PIPE        # same station: radial-profile sampling
X_THROAT_MID = L_UP + 0.5 * L_THROAT
X_DOWNSTREAM_TAP = L_UP + L_THROAT + 3.0 * D_PIPE

N_RADIAL_PROBES = 9


def womersley_alpha(t_cycle: float, radius: float = R_PIPE, nu: float = NU) -> float:
    omega = 2.0 * math.pi / t_cycle
    return radius * math.sqrt(omega / nu)


ALPHA_PHYSIOLOGICAL = womersley_alpha(T_CYCLE)


# --------------------------------------------------------------------------
# Mesh: 5-block axisymmetric wedge, sharp-edged orifice plate
# --------------------------------------------------------------------------

def _grading_str(vals) -> str:
    return f"({vals[0]:.6g} {vals[1]:.6g} {vals[2]:.6g})"


def block_mesh_dict(*, nx_up: int = 60, nx_throat: int = 6, nx_down: int = 90,
                    nr_in: int = 24, nr_out: int = 8,
                    r_grade_wall: float = 6.0, r_grade_core: float = 1.6,
                    x_grade_plate: float = 4.0) -> str:
    """5 hex blocks, wedge revolve. x-stations: 0=inlet, 1=plate front,
    2=plate back, 3=outlet. r-stations: 0=axis, 1=orifice radius, 2=pipe wall.
    Points at r=0 are shared between the wedge's front and back copies
    (a degenerate axis edge, the standard OpenFOAM wedge-with-centerline
    device)."""
    half = math.radians(HALF_ANGLE_DEG)
    xs = (0.0, L_UP, L_UP + L_THROAT, L_TOTAL)
    rs = (0.0, R_ORIFICE, R_PIPE)

    verts: list[str] = []
    # index(xi, ri, side): side 'B'=back(-angle) 'F'=front(+angle)
    idx: dict[tuple[int, int, str], int] = {}

    def add_vertex(x: float, r: float, side: str) -> int:
        y = r * math.cos(half)
        z = -r * math.sin(half) if side == "B" else r * math.sin(half)
        verts.append(f"    ({x:.8g} {y:.8g} {z:.8g})")
        return len(verts) - 1

    for xi, x in enumerate(xs):
        axis_i = add_vertex(x, 0.0, "B")
        idx[(xi, 0, "B")] = axis_i
        idx[(xi, 0, "F")] = axis_i          # shared: axis is degenerate
        for ri in (1, 2):
            idx[(xi, ri, "B")] = add_vertex(x, rs[ri], "B")
            idx[(xi, ri, "F")] = add_vertex(x, rs[ri], "F")

    def V(xi: int, ri: int, side: str) -> int:
        return idx[(xi, ri, side)]

    def hexblock(xi_lo, xi_hi, ri_lo, ri_hi, nx, ngr_r, x_grade=1.0,
                r_grade=1.0) -> str:
        b0 = V(xi_lo, ri_lo, "B"); b1 = V(xi_hi, ri_lo, "B")
        b2 = V(xi_hi, ri_hi, "B"); b3 = V(xi_lo, ri_hi, "B")
        f0 = V(xi_lo, ri_lo, "F"); f1 = V(xi_hi, ri_lo, "F")
        f2 = V(xi_hi, ri_hi, "F"); f3 = V(xi_lo, ri_hi, "F")
        grading = _grading_str((x_grade, r_grade, 1.0))
        return (f"    hex ({b0} {b1} {b2} {b3} {f0} {f1} {f2} {f3}) "
                f"({nx} {ngr_r} 1) simpleGrading {grading}")

    blocks = []
    faces_wedge_back, faces_wedge_front = [], []
    faces_axis = []

    def loop_back(xi_lo, xi_hi, ri_lo, ri_hi):
        return (f"            ({V(xi_lo,ri_lo,'B')} {V(xi_hi,ri_lo,'B')} "
                f"{V(xi_hi,ri_hi,'B')} {V(xi_lo,ri_hi,'B')})")

    def loop_front(xi_lo, xi_hi, ri_lo, ri_hi):
        return (f"            ({V(xi_lo,ri_lo,'F')} {V(xi_lo,ri_hi,'F')} "
                f"{V(xi_hi,ri_hi,'F')} {V(xi_hi,ri_lo,'F')})")

    # U_inner (x0-x1, r0-r1): cluster toward r1 (shear layer feeding the throat)
    blocks.append(hexblock(0, 1, 0, 1, nx_up, nr_in, x_grade=1.0,
                           r_grade=r_grade_core))
    faces_wedge_back.append(loop_back(0, 1, 0, 1))
    faces_wedge_front.append(loop_front(0, 1, 0, 1))
    faces_axis.append(f"            ({V(0,0,'B')} {V(1,0,'B')} "
                      f"{V(1,0,'B')} {V(0,0,'B')})")

    # U_outer (x0-x1, r1-r2): cluster toward r2 (pipe wall)
    blocks.append(hexblock(0, 1, 1, 2, nx_up, nr_out, x_grade=1.0,
                           r_grade=r_grade_wall))
    faces_wedge_back.append(loop_back(0, 1, 1, 2))
    faces_wedge_front.append(loop_front(0, 1, 1, 2))

    # T (x1-x2, r0-r1): the plate/throat, cluster toward r1 (bore wall)
    blocks.append(hexblock(1, 2, 0, 1, nx_throat, nr_in, x_grade=1.0,
                           r_grade=r_grade_core))
    faces_wedge_back.append(loop_back(1, 2, 0, 1))
    faces_wedge_front.append(loop_front(1, 2, 0, 1))
    faces_axis.append(f"            ({V(1,0,'B')} {V(2,0,'B')} "
                      f"{V(2,0,'B')} {V(1,0,'B')})")

    # D_inner (x2-x3, r0-r1): cluster toward x2 (jet development)
    blocks.append(hexblock(2, 3, 0, 1, nx_down, nr_in, x_grade=1.0 / x_grade_plate,
                           r_grade=r_grade_core))
    faces_wedge_back.append(loop_back(2, 3, 0, 1))
    faces_wedge_front.append(loop_front(2, 3, 0, 1))
    faces_axis.append(f"            ({V(2,0,'B')} {V(3,0,'B')} "
                      f"{V(3,0,'B')} {V(2,0,'B')})")

    # D_outer (x2-x3, r1-r2): cluster toward r2
    blocks.append(hexblock(2, 3, 1, 2, nx_down, nr_out, x_grade=1.0 / x_grade_plate,
                           r_grade=r_grade_wall))
    faces_wedge_back.append(loop_back(2, 3, 1, 2))
    faces_wedge_front.append(loop_front(2, 3, 1, 2))

    inlet_faces = [loop_back(0, 0, 0, 1).replace("hex", ""),
                  ]  # placeholder unused, built below explicitly

    def face(xi, ri_lo, ri_hi, side):
        if side == "B":
            return (f"            ({V(xi,ri_lo,'B')} {V(xi,ri_hi,'B')} "
                    f"{V(xi,ri_hi,'F')} {V(xi,ri_lo,'F')})")
        else:
            return (f"            ({V(xi,ri_lo,'B')} {V(xi,ri_lo,'F')} "
                    f"{V(xi,ri_hi,'F')} {V(xi,ri_hi,'B')})")

    inlet = [face(0, 0, 1, "B"), face(0, 1, 2, "B")]
    outlet = [face(3, 0, 1, "F"), face(3, 1, 2, "F")]
    pipe_wall = [face(0, 1, 2, "F"), face(3, 1, 2, "B")]  # r=r2 outer faces (U_outer, D_outer)
    # correct outward faces at r=r2 use the "outward from axis" loop; reuse
    # a radial-face helper oriented at fixed ri (constant-r face)
    def rface(xi_lo, xi_hi, ri):
        return (f"            ({V(xi_lo,ri,'B')} {V(xi_hi,ri,'B')} "
                f"{V(xi_hi,ri,'F')} {V(xi_lo,ri,'F')})")
    pipe_wall = [rface(0, 1, 2), rface(2, 3, 2)]
    throat_wall = [rface(1, 2, 1)]
    plate_front = [face(1, 1, 2, "B")]
    plate_back = [face(2, 1, 2, "F")]

    boundary = (
        "boundary\n(\n"
        "    inlet\n    {\n        type patch;\n        faces\n        (\n"
        + "\n".join(inlet) + "\n        );\n    }\n"
        "    outlet\n    {\n        type patch;\n        faces\n        (\n"
        + "\n".join(outlet) + "\n        );\n    }\n"
        "    pipeWall\n    {\n        type wall;\n        faces\n        (\n"
        + "\n".join(pipe_wall) + "\n        );\n    }\n"
        "    plate\n    {\n        type wall;\n        faces\n        (\n"
        + "\n".join(throat_wall + plate_front + plate_back) + "\n        );\n    }\n"
        "    axis\n    {\n        type empty;\n        faces\n        (\n"
        + "\n".join(faces_axis) + "\n        );\n    }\n"
        "    back\n    {\n        type wedge;\n        faces\n        (\n"
        + "\n".join(faces_wedge_back) + "\n        );\n    }\n"
        "    front\n    {\n        type wedge;\n        faces\n        (\n"
        + "\n".join(faces_wedge_front) + "\n        );\n    }\n"
        ");\n"
    )

    return (
        _foam_header("dictionary", "blockMeshDict", "system")
        + "scale   1;\n\n"
        + "vertices\n(\n" + "\n".join(verts) + "\n);\n\n"
        + "blocks\n(\n" + "\n".join(blocks) + "\n);\n\n"
        + "edges\n(\n);\n\n"
        + boundary
        + "\nmergePatchPairs\n(\n);\n"
    )


# --------------------------------------------------------------------------
# Case files
# --------------------------------------------------------------------------

def transport_properties() -> str:
    return (_foam_header("dictionary", "transportProperties", "constant")
           + f"\ntransportModel  Newtonian;\nnu              {NU:.6g};\n")


def turbulence_properties() -> str:
    return (_foam_header("dictionary", "turbulenceProperties", "constant")
           + "\nsimulationType  laminar;\n")


def fv_schemes() -> str:
    return _foam_header("dictionary", "fvSchemes", "system") + """
ddtSchemes      { default Euler; }
gradSchemes     { default Gauss linear; }
laplacianSchemes { default Gauss linear corrected; }
snGradSchemes   { default corrected; }

divSchemes
{
    default                         none;
    div(phi,U)                      Gauss linearUpwind grad(U);
    div((nuEff*dev2(T(grad(U)))))   Gauss linear;
}
interpolationSchemes { default linear; }
wallDist        { method meshWave; }
"""


def fv_solution() -> str:
    return _foam_header("dictionary", "fvSolution", "system") + """
solvers
{
    p
    {
        solver          PCG;
        preconditioner  DIC;
        tolerance       1e-08;
        relTol          0.02;
    }
    pFinal
    {
        $p;
        relTol          0;
    }
    U
    {
        solver          smoothSolver;
        smoother        symGaussSeidel;
        tolerance       1e-09;
        relTol          0.01;
    }
    UFinal
    {
        $U;
        relTol          0;
    }
}

PIMPLE
{
    nOuterCorrectors    2;
    nCorrectors         2;
    nNonOrthogonalCorrectors 1;
}
"""


def _probe_points() -> list[tuple[float, float, float]]:
    pts = [(X_UPSTREAM_TAP, 1e-6, 0.0), (X_THROAT_MID, 1e-6, 0.0),
          (X_DOWNSTREAM_TAP, 1e-6, 0.0)]
    r_max = 0.92 * R_PIPE
    for i in range(N_RADIAL_PROBES):
        r = (i + 0.5) / N_RADIAL_PROBES * r_max
        pts.append((X_PROFILE, r, 0.0))
    return pts


def control_dict(*, end_time: float, dt0: float, t_cycle: float,
                 write_interval: float, max_co: float = 0.9) -> str:
    pts = _probe_points()
    pts_str = "\n".join(f"        ({x:.8g} {y:.8g} {z:.8g})" for x, y, z in pts)
    return _foam_header("dictionary", "controlDict", "system") + f"""
application     pimpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {end_time:.8g};
deltaT          {dt0:.6g};
adjustTimeStep  yes;
maxCo           {max_co:.4g};
maxDeltaT       {t_cycle / 400.0:.6g};
writeControl    adjustableRunTime;
writeInterval   {write_interval:.6g};
purgeWrite      3;
writeFormat     ascii;
writePrecision  9;
timeFormat      general;
timePrecision   9;

functions
{{
    probes1
    {{
        type            probes;
        libs            (sampling);
        writeControl    timeStep;
        writeInterval   1;
        fields          (p U);
        probeLocations
        (
{pts_str}
        );
    }}
}}
"""


def initial_fields(u0: float) -> dict[str, str]:
    u_text = (_foam_header("volVectorField", "U", "0")
             + f"\ndimensions      [0 1 -1 0 0 0 0];\n\n"
             + f"internalField   uniform ({u0:.6g} 0 0);\n\n"
             + "boundaryField\n{\n"
             + "    inlet   { type fixedValue; value $internalField; }\n"
             + "    outlet  { type inletOutlet; inletValue uniform (0 0 0); "
               "value uniform (0 0 0); }\n"
             + "    pipeWall { type noSlip; }\n"
             + "    plate    { type noSlip; }\n"
             + "    axis     { type empty; }\n"
             + "    back     { type wedge; }\n"
             + "    front    { type wedge; }\n"
             + "}\n")
    p_text = (_foam_header("volScalarField", "p", "0")
             + "\ndimensions      [0 2 -2 0 0 0 0];\n\n"
             + "internalField   uniform 0;\n\n"
             + "boundaryField\n{\n"
             + "    inlet   { type zeroGradient; }\n"
             + "    outlet  { type fixedValue; value uniform 0; }\n"
             + "    pipeWall { type zeroGradient; }\n"
             + "    plate    { type zeroGradient; }\n"
             + "    axis     { type empty; }\n"
             + "    back     { type wedge; }\n"
             + "    front    { type wedge; }\n"
             + "}\n")
    return {"U": u_text, "p": p_text}


def inlet_sine_bc(t_cycle: float) -> str:
    """The pulsatile inlet BC, spliced into 0/U's inlet entry in place of
    ``fixedValue`` for the unsteady cases: uniformFixedValue driven by a
    Function1 sine (native OpenFOAM, no runtime-compiled BC needed)."""
    freq = 1.0 / t_cycle
    return f"""    inlet
    {{
        type            uniformFixedValue;
        uniformValue
        {{
            type        sine;
            frequency   {freq:.10g};
            amplitude   {U_AMP:.8g};
            scale       (1 0 0);
            level       ({U_MEAN:.8g} 0 0);
        }}
        value           uniform ({U_MEAN:.8g} 0 0);
    }}
"""


def write_case(root: Path, *, steady_u: float | None, t_cycle: float,
              end_time: float, dt0: float, write_interval: float,
              **mesh_kwargs) -> Path:
    case = Path(root)
    for sub in ("0", "constant", "system"):
        (case / sub).mkdir(parents=True, exist_ok=True)
    (case / "system" / "blockMeshDict").write_text(
        block_mesh_dict(**mesh_kwargs))
    (case / "system" / "fvSchemes").write_text(fv_schemes())
    (case / "system" / "fvSolution").write_text(fv_solution())
    (case / "constant" / "transportProperties").write_text(transport_properties())
    (case / "constant" / "turbulenceProperties").write_text(turbulence_properties())
    u0 = steady_u if steady_u is not None else U_MEAN
    fields = initial_fields(u0)
    if steady_u is None:
        # pulsatile: replace the single-line fixedValue inlet entry with the
        # multi-line sine BC block (a plain substring replace -- no line-scan
        # skip logic that can eat the rest of the dictionary if the entry
        # it's replacing isn't itself split cleanly across lines).
        needle = "    inlet   { type fixedValue; value $internalField; }\n"
        assert needle in fields["U"], "inlet fixedValue entry not found to splice"
        fields["U"] = fields["U"].replace(needle, inlet_sine_bc(t_cycle))
    (case / "0" / "U").write_text(fields["U"])
    (case / "0" / "p").write_text(fields["p"])
    (case / "system" / "controlDict").write_text(control_dict(
        end_time=end_time, dt0=dt0, t_cycle=t_cycle,
        write_interval=write_interval))
    return case


# --------------------------------------------------------------------------
# Execution helpers (foreground; the caller launches via launch_solve.sh)
# --------------------------------------------------------------------------

def run_util(case: Path, args: list[str], log_name: str, timeout: float = 900.0):
    return _foam(args, case, log_name, timeout=timeout)


def build_and_check(case: Path) -> dict[str, Any]:
    r1 = run_util(case, ["blockMesh"], "log.blockMesh")
    r2 = run_util(case, ["checkMesh", "-allTopology", "-allGeometry"],
                 "log.checkMesh")
    return {"blockMesh_rc": r1.returncode, "checkMesh_rc": r2.returncode}
