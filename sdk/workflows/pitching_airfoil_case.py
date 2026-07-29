"""F5b -- pitching NACA 0012, dynamic stall, unsteady incompressible RANS.

Reference case: McAlister, K.W., Carr, L.W., McCroskey, W.J., "Dynamic Stall
Experiments on the NACA 0012 Airfoil," NASA TP-1100, January 1978. Retrieved
and parsed directly (NTRS 19780009057) 2026-07-28/29.

Case (their case "(e)"), confirmed from the primary source text:
  - alpha(t) = 15 deg + 10 deg * sin(omega t)   (mean 15 deg, amplitude 10 deg)
  - reduced frequency k = omega*c/(2 U) = 0.15
  - Reynolds number Re = 2.5e6 (held fixed across their whole test matrix)
  - Mach number M = 0.09 (low-speed; run here as incompressible)
  - pitch axis: quarter chord (stated repeatedly, "pitched about its
    quarter-chord axis")
  - chord 1.22 m, span 1.98 m in the actual rig (chord/tunnel-width ratio
    0.4 -- a real 3D end-effect risk they partially address with end
    plates; not reproducible in a 2D run, see caveat below)

What TP-1100 does NOT give me: a digitized, tabulated CL(alpha) time series
for this exact case. Its dynamic-stall results are presented as scanned
strip-chart figures (CN, CC, CM vs azimuth/time), not machine-readable
numbers, for every (mean angle, amplitude, k) combination including (e).
The report's own SUMMARY/CONCLUSIONS give only report-wide EXTREME bounds
across their whole test matrix ("stall may be delayed by as much as
d(omega t)=pi/2 with loads reaching Cp=-30, CL=3.5, CD=1.5, CM=-0.75") --
not case-(e)-specific numbers. Per the task's explicit fallback: this run
reports the COMPUTED hysteresis loop, peak CL, and stall-onset angle,
compared to TP-1100 only QUALITATIVELY (delayed stall past the static
value, loop topology, order-of-magnitude peak CL against the report-wide
bound) -- NOT as a point-match quantitative gate, because no such citable
point number was found.

Mesh/motion: reuses workflows.transonic_airfoil.transonic_blockmesh_dict
verbatim (the same proven analytic-NACA0012 C-grid O-topology used for the
F2 transonic case), unmodified, at a 25-chord farfield. The ENTIRE mesh
(not a cellZone) is rotated rigidly about the quarter chord via OpenFOAM's
built-in solidBody/oscillatingRotatingMotion mesh mover -- chosen over an
AMI-zoned rotating-region approach because (a) it needs no new mesh
topology (the existing C-grid is reused as-is), (b) the farfield boundary
is a full 25 chords from the airfoil in every direction, so its physical
displacement under a +/-10 deg rotation about a point only 0.25c from the
nearest mesh feature is geometrically negligible relative to that 25c
standoff -- the outer patch keeps returning arbitrarily close to its own
extent, so the freestreamVelocity/freestreamPressure boundary condition
(fixed IN THE LAB FRAME, not mesh-attached) stays valid throughout the
motion. The MEAN 15 deg incidence is realized by fixing the freestream
velocity vector at 15 deg (not by more mesh rotation); only the +/-10 deg
OSCILLATION is the mesh motion, so the net instantaneous incidence in the
lab frame is exactly 15 + 10 sin(omega t), matching the reference case.
"""

from __future__ import annotations

import math
import shutil
import time
from pathlib import Path
from typing import Any, Callable

from workflows.tmr_verification import (
    _foam, _foam_header, _copy_best_effort, _field, fv_schemes,
    pimple_control_dict,
)
from workflows.transonic_airfoil import transonic_blockmesh_dict
from workflows.tmr_verification import NACA_LEVELS, NacaGridLevel
from chief_engineer.head_engineer import parse_coefficient_history

CHORD = 1.0
U_INF = 1.0
RE = 2.5e6
NU = U_INF * CHORD / RE
ALPHA_MEAN_DEG = 15.0
ALPHA_AMP_DEG = 10.0
REDUCED_FREQ = 0.15
OMEGA = 2.0 * REDUCED_FREQ * U_INF / CHORD    # rad/s, = 0.3
PERIOD = 2.0 * math.pi / OMEGA                # convective time units, ~20.94
PITCH_AXIS = (0.25, 0.0, 0.0)                 # quarter chord

FARFIELD_R = 25.0
WAKE_LEN = 25.0
FIRST_CELL = 8.0e-6

TU_FREESTREAM = 0.001
MUT_RATIO = 10.0
K_INF = 1.5 * (TU_FREESTREAM * U_INF) ** 2
NUT_INF = MUT_RATIO * NU
OMEGA_INF = K_INF / NUT_INF

_alpha_rad = math.radians(ALPHA_MEAN_DEG)
DRAG_DIR = f"({math.cos(_alpha_rad):.8f} {math.sin(_alpha_rad):.8f} 0)"
LIFT_DIR = f"({-math.sin(_alpha_rad):.8f} {math.cos(_alpha_rad):.8f} 0)"
U_FREESTREAM_VEC = f"({U_INF*math.cos(_alpha_rad):.8f} {U_INF*math.sin(_alpha_rad):.8f} 0)"


def alpha_deg(t: float) -> float:
    return ALPHA_MEAN_DEG + ALPHA_AMP_DEG * math.sin(OMEGA * t)


# --------------------------------------------------------------------------
# constant/dynamicMeshDict
# --------------------------------------------------------------------------

def dynamic_mesh_dict() -> str:
    return _foam_header("dictionary", "dynamicMeshDict", "constant") + f"""
dynamicFvMesh   dynamicMotionSolverFvMesh;

motionSolver    solidBody;

solidBodyMotionFunction oscillatingRotatingMotion;
oscillatingRotatingMotionCoeffs
{{
    origin      ({PITCH_AXIS[0]:.6g} {PITCH_AXIS[1]:.6g} {PITCH_AXIS[2]:.6g});
    axis        (0 0 1);
    omega       {OMEGA:.10g};
    amplitude   (0 0 {ALPHA_AMP_DEG:.6g});
}}
"""


_TURBULENCE = _foam_header("dictionary", "turbulenceProperties", "constant") + """
simulationType  RAS;
RAS
{
    RASModel        kOmegaSST;
    turbulence      on;
    printCoeffs     on;
}
"""


def initial_fields() -> dict[str, str]:
    empty = "        type            empty;\n"

    def bc(*lines: str) -> str:
        return "".join(f"        {line}\n" for line in lines)

    u = _field("volVectorField", "U", "[0 1 -1 0 0 0 0]", f"uniform {U_FREESTREAM_VEC}", {
        "inflow": bc("type            freestreamVelocity;",
                     f"freestreamValue uniform {U_FREESTREAM_VEC};",
                     f"value           uniform {U_FREESTREAM_VEC};"),
        "outflow": bc("type            freestreamVelocity;",
                      f"freestreamValue uniform {U_FREESTREAM_VEC};",
                      f"value           uniform {U_FREESTREAM_VEC};"),
        "airfoil": bc("type            movingWallVelocity;",
                     f"value           uniform (0 0 0);"),
        "frontAndBack": empty,
    })
    p = _field("volScalarField", "p", "[0 2 -2 0 0 0 0]", "uniform 0", {
        "inflow": bc("type            freestreamPressure;", "freestreamValue uniform 0;"),
        "outflow": bc("type            freestreamPressure;", "freestreamValue uniform 0;"),
        "airfoil": bc("type            zeroGradient;"),
        "frontAndBack": empty,
    })
    k = _field("volScalarField", "k", "[0 2 -2 0 0 0 0]", f"uniform {K_INF:.8g}", {
        "inflow": bc("type            inletOutlet;",
                     f"inletValue      uniform {K_INF:.8g};",
                     f"value           uniform {K_INF:.8g};"),
        "outflow": bc("type            inletOutlet;",
                      f"inletValue      uniform {K_INF:.8g};",
                      f"value           uniform {K_INF:.8g};"),
        "airfoil": bc("type            kLowReWallFunction;", "value           uniform 1e-12;"),
        "frontAndBack": empty,
    })
    omega = _field("volScalarField", "omega", "[0 0 -1 0 0 0 0]", f"uniform {OMEGA_INF:.8g}", {
        "inflow": bc("type            inletOutlet;",
                     f"inletValue      uniform {OMEGA_INF:.8g};",
                     f"value           uniform {OMEGA_INF:.8g};"),
        "outflow": bc("type            inletOutlet;",
                      f"inletValue      uniform {OMEGA_INF:.8g};",
                      f"value           uniform {OMEGA_INF:.8g};"),
        "airfoil": bc("type            omegaWallFunction;", "blended         true;",
                     f"value           uniform {OMEGA_INF:.8g};"),
        "frontAndBack": empty,
    })
    nut = _field("volScalarField", "nut", "[0 2 -1 0 0 0 0]", f"uniform {NUT_INF:.8g}", {
        "inflow": bc("type            calculated;", "value           uniform 0;"),
        "outflow": bc("type            calculated;", "value           uniform 0;"),
        "airfoil": bc("type            nutLowReWallFunction;", "value           uniform 0;"),
        "frontAndBack": empty,
    })
    # No pointDisplacement field: verified against the stock sloshingTank2D
    # tutorial (dynamicMotionSolverFvMesh + motionSolver solidBody, no
    # cellZone -- the same pattern used here), whose 0/ directory carries no
    # pointDisplacement file at all. solidBody is a pure algebraic transform
    # of every mesh point from the case's own transformation() function; it
    # solves no PDE and needs no such field.
    return {"U": u, "p": p, "k": k, "omega": omega, "nut": nut}


def build_case(case_dir: Path, level: NacaGridLevel, *, end_time: float,
              dt0: float = 0.002, max_co: float = 1.0) -> dict[str, Any]:
    case = Path(case_dir)
    for sub in ("0", "constant", "system"):
        (case / sub).mkdir(parents=True, exist_ok=True)
    (case / "system" / "blockMeshDict").write_text(
        transonic_blockmesh_dict(level, farfield_r=FARFIELD_R, wake_len=WAKE_LEN,
                                 first_cell=FIRST_CELL))
    (case / "system" / "fvSchemes").write_text(fv_schemes(limited=True, transient=True))
    (case / "system" / "fvSolution").write_text(_pimple_fv_solution_with_mesh())
    control = pimple_control_dict(end_time, dt0, patch="airfoil", aref=CHORD,
                                  drag_dir=DRAG_DIR, lift_dir=LIFT_DIR,
                                  max_co=max_co, adjustable=True)
    (case / "system" / "controlDict").write_text(control)
    (case / "constant" / "transportProperties").write_text(
        _foam_header("dictionary", "transportProperties", "constant")
        + f"transportModel  Newtonian;\nnu              {NU:.8g};\n")
    (case / "constant" / "turbulenceProperties").write_text(_TURBULENCE)
    (case / "constant" / "dynamicMeshDict").write_text(dynamic_mesh_dict())
    for name, text in initial_fields().items():
        (case / "0" / name).write_text(text)
    return {"level": level.name, "cells": level.cells, "end_time": end_time,
           "dt0": dt0, "max_co": max_co, "re": RE, "nu": NU, "omega": OMEGA,
           "period": PERIOD}


def _pimple_fv_solution_with_mesh() -> str:
    """pimple_fv_solution() plus a ``pcorr`` entry -- pimpleFoam's moving-
    mesh flux correction (meshPhi) needs its own solver block on a dynamic
    mesh; a static-mesh case (pimple_fv_solution's only prior use, the F5a
    cylinder) never triggers that code path, so the entry was absent and
    the first pilot of this case died immediately: "FOAM FATAL IO ERROR:
    Entry 'pcorr' not found in dictionary system/fvSolution/solvers"."""
    from workflows.tmr_verification import pimple_fv_solution
    base = pimple_fv_solution()
    pcorr_block = (
        "    pcorr\n    {\n"
        "        solver          PCG;\n"
        "        preconditioner  DIC;\n"
        "        tolerance       1e-05;\n"
        "        relTol          0;\n"
        "    }\n"
        "    pcorrFinal\n    {\n"
        "        $pcorr;\n"
        "        relTol          0;\n"
        "    }\n"
    )
    # Insert pcorr as the first entry inside "solvers\n{".
    marker = "solvers\n{\n"
    idx = base.index(marker) + len(marker)
    return base[:idx] + pcorr_block + base[idx:]


def run_case(level: NacaGridLevel, out_dir: Path, *, end_time: float, dt0: float = 0.002,
            max_co: float = 1.0, timeout: float = 1800.0,
            log: Callable[[str], None] = print) -> dict[str, Any]:
    out_dir = Path(out_dir)
    case = out_dir / "case"
    if case.exists():
        shutil.rmtree(case, ignore_errors=True)
    params = build_case(case, level, end_time=end_time, dt0=dt0, max_co=max_co)

    timings: dict[str, float] = {}
    for step, args in (("blockMesh", ["blockMesh"]), ("checkMesh", ["checkMesh"])):
        start = time.monotonic()
        result = _foam(args, case, f"log.{step}", timeout=300)
        timings[step] = round(time.monotonic() - start, 1)
        log(f"[pitch-{level.name}] {step} done in {timings[step]:.1f}s (exit {result.returncode})")
        if step == "blockMesh" and result.returncode != 0:
            tail = (case / f"log.{step}").read_text(errors="replace")
            raise RuntimeError(f"pitch-{level.name}: blockMesh failed:\n"
                               + "\n".join(tail.splitlines()[-25:]))

    # An impulsive uniform start on this same C-grid topology was already
    # measured (F2, tmr_verification module docstring) to diverge within
    # ~20 iterations because of its extreme near-wall cell aspect ratio; a
    # first pilot of THIS case, started impulsively, blew up identically
    # (CL reported in the tens of thousands). potentialFoam gives a
    # rotational-free initial guess consistent with the t=0 incidence
    # (alpha_mean=15 deg, since sin(0)=0) before the real march starts.
    from workflows.tmr_verification import fv_solution as _generic_fv_solution
    pimple_solution = (case / "system" / "fvSolution").read_text()
    (case / "system" / "fvSolution").write_text(
        _generic_fv_solution(non_orth_correctors=1, potential=True, p_solver="PCG"))
    start = time.monotonic()
    result = _foam(["potentialFoam", "-writephi"], case, "log.potentialFoam", timeout=600)
    timings["potentialFoam"] = round(time.monotonic() - start, 1)
    log(f"[pitch-{level.name}] potentialFoam done in {timings['potentialFoam']:.1f}s "
       f"(exit {result.returncode})")
    if result.returncode != 0:
        tail = (case / "log.potentialFoam").read_text(errors="replace")
        raise RuntimeError(f"pitch-{level.name}: potentialFoam failed:\n"
                           + "\n".join(tail.splitlines()[-25:]))
    (case / "system" / "fvSolution").write_text(pimple_solution)

    start = time.monotonic()
    result = _foam(["pimpleFoam"], case, "log.pimpleFoam", timeout=timeout)
    timings["pimpleFoam"] = round(time.monotonic() - start, 1)
    log_text = (case / "log.pimpleFoam").read_text(errors="replace")
    if result.returncode != 0:
        raise RuntimeError(f"pitch-{level.name}: pimpleFoam failed:\n"
                           + "\n".join(log_text.splitlines()[-30:]))

    coeff_files = sorted((case / "postProcessing" / "forceCoeffs1").rglob("coefficient*.dat"))
    if not coeff_files:
        raise RuntimeError(f"pitch-{level.name}: no forceCoeffs output")
    history = parse_coefficient_history(coeff_files[-1].read_text(errors="replace"))
    times = history.get("Time", [])
    cl = history.get("Cl", [])
    cd = history.get("Cd", [])
    alphas = [alpha_deg(t) for t in times]

    record = {
        "level": level.name, "cells": level.cells, "end_time": end_time,
        "dt0": dt0, "max_co": max_co, "re": RE, "mach_reference": 0.09,
        "reduced_freq": REDUCED_FREQ, "alpha_mean_deg": ALPHA_MEAN_DEG,
        "alpha_amp_deg": ALPHA_AMP_DEG, "omega": OMEGA, "period": PERIOD,
        "n_steps": len(times), "times": times, "alpha_deg": alphas,
        "cl": cl, "cd": cd,
        "cl_max": max(cl) if cl else None,
        "cl_max_alpha_deg": alphas[cl.index(max(cl))] if cl else None,
        "wall_seconds": sum(timings.values()), "timings": timings,
    }
    log(f"[pitch-{level.name}] {len(times)} steps to t={times[-1] if times else 0:.2f} "
       f"(periods={((times[-1] if times else 0)/PERIOD):.2f}), "
       f"CLmax={record['cl_max']}, wall_s={record['wall_seconds']:.1f}")
    return record
