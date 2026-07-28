"""2D laminar vortex-shedding cylinder, Re ~ 100-200 — an UNSTEADY validation
case with a genuine published reference (Strouhal number and mean Cd from
the classical circular-cylinder wake literature).

Reuses the same O-grid annulus topology as the mega-batch's steady
``simpleFoam`` cylinder (``chief_engineer/openfoam.py``), enlarged (20
diameters to the farfield, instead of 10) to keep the vortex street's
blockage and far-boundary reflection small, and re-meshed for a genuinely
resolved laminar boundary layer (first cell 0.006D near the wall — this
regime has no turbulence model and no wall function to fall back on). The
solve itself, the averaging, and the stationarity gate reuse
``sdk/workflows/tmr_verification.py`` verbatim (``pimple_control_dict``,
``pimple_fv_solution``, ``fv_schemes``, ``transport_properties``,
``time_weighted_stats``, ``measure_period``, ``halves_drift``) rather than
re-deriving them, so this case is gated by the exact same stationarity check
that the NACA 0012 transient defect (commit 6606434) added: a mean quoted
over a window whose two halves disagree by more than 10% is refused rather
than reported.

Reference literature for Re_D = 100-200 (subcritical, laminar, periodic
vortex shedding):
 - Strouhal number: Roshko, A. (1954) "On the Development of Turbulent Wakes
   from Vortex Streets", NACA Report 1191 (St ~ 0.212(1 - 21.2/Re) for
   50 < Re < 200): https://ntrs.nasa.gov/citations/19930091905
 - Williamson, C.H.K. (1996) "Vortex Dynamics in the Cylinder Wake",
   Annu. Rev. Fluid Mech. 28:477-539, the standard modern St-Re curve:
   https://doi.org/10.1146/annurev.fl.28.010196.002401
 - Mean Cd / Cl' compilations at Re=100: Henderson, R.D. (1995) "Details of
   the drag curve near the onset of vortex shedding", Phys. Fluids 7, 2102,
   https://doi.org/10.1063/1.868459 (Cd ~ 1.35); numerous CFD benchmark
   papers converge on Cd ~ 1.3-1.4, Cl' ~ 0.2-0.3 at Re=100 with this same
   two-dimensional, purely laminar setup.
"""

from __future__ import annotations

import math
import shutil
import time
from pathlib import Path
from typing import Any, Callable

from workflows.tmr_verification import (
    _foam, _foam_header, _run_prefix, _copy_best_effort,
    fv_schemes, pimple_control_dict, pimple_fv_solution, transport_properties,
    time_weighted_stats, measure_period, halves_drift,
)
from chief_engineer.head_engineer import parse_coefficient_history

_RUN_ROOT = Path.home() / "certonomous-runs" / "unsteady-cylinder"

DIAMETER = 1.0
U_INF = 1.0
SPAN = 0.1


def reynolds_to_nu(re: float, diameter: float = DIAMETER, u_inf: float = U_INF) -> float:
    return u_inf * diameter / re


# --------------------------------------------------------------------------
# Mesh: O-grid annulus, cylinder wall to a circular farfield.
# --------------------------------------------------------------------------

def block_mesh_dict(diameter: float, farfield_diameters: float,
                    n_radial: int, n_tangential: int, first_cell: float,
                    span: float = SPAN) -> str:
    """Four 90-degree hex blocks, geometric radial grading sized to a
    requested first-cell height near the wall (real boundary-layer
    resolution, not a wall function — this flow is laminar throughout)."""
    from workflows.tmr_verification import ratio_for_first_cell

    inner = diameter / 2.0
    outer = farfield_diameters * diameter
    length = outer - inner
    total_ratio = ratio_for_first_cell(length, n_radial, first_cell)

    half = math.sqrt(0.5)
    corner_angles = (-45.0, 45.0, 135.0, 225.0)
    arc_angles = (0.0, 90.0, 180.0, 270.0)

    def ring(radius: float, z: float) -> list[str]:
        pts = []
        for angle in corner_angles:
            rad = math.radians(angle)
            pts.append(f"    ({radius * math.cos(rad):.8g} {radius * math.sin(rad):.8g} {z:.8g})")
        return pts

    vertices = (ring(inner, 0.0) + ring(outer, 0.0)
               + ring(inner, span) + ring(outer, span))

    blocks, edges, cyl_faces, far_faces, empty_faces = [], [], [], [], []
    for k in range(4):
        k2 = (k + 1) % 4
        i, o, i2, o2 = k, 4 + k, k2, 4 + k2
        ti, to, ti2, to2 = 8 + k, 12 + k, 8 + k2, 12 + k2
        blocks.append(
            f"    hex ({i} {o} {o2} {i2} {ti} {to} {to2} {ti2}) "
            f"({n_radial} {n_tangential} 1) simpleGrading ({total_ratio:.6g} 1 1)")
        mid = math.radians(arc_angles[k])
        for radius, a, b in ((inner, i, i2), (outer, o, o2)):
            for lift in (0, 8):
                edges.append(
                    f"    arc {a + lift} {b + lift} "
                    f"({radius * math.cos(mid):.8g} {radius * math.sin(mid):.8g} "
                    f"{0.0 if lift == 0 else span:.8g})")
        cyl_faces.append(f"            ({i} {i2} {ti2} {ti})")
        far_faces.append(f"            ({o} {o2} {to2} {to})")
        empty_faces.append(f"            ({i} {o} {o2} {i2})")
        empty_faces.append(f"            ({ti} {to} {to2} {ti2})")

    return (
        _foam_header("dictionary", "blockMeshDict", "system")
        + "convertToMeters 1;\n\n"
        + "vertices\n(\n" + "\n".join(vertices) + "\n);\n\n"
        + "blocks\n(\n" + "\n".join(blocks) + "\n);\n\n"
        + "edges\n(\n" + "\n".join(edges) + "\n);\n\n"
        + "boundary\n(\n"
        + "    cylinder\n    {\n        type wall;\n        faces\n        (\n"
        + "\n".join(cyl_faces) + "\n        );\n    }\n"
        + "    farfield\n    {\n        type patch;\n        faces\n        (\n"
        + "\n".join(far_faces) + "\n        );\n    }\n"
        + "    frontAndBack\n    {\n        type empty;\n        faces\n        (\n"
        + "\n".join(empty_faces) + "\n        );\n    }\n"
        + ");\n\nmergePatchPairs\n(\n);\n"
    )


_LAMINAR_TURBULENCE = (
    _foam_header("dictionary", "turbulenceProperties", "constant")
    + "simulationType  laminar;\n"
)


def initial_fields(perturbation: float = 0.02) -> dict[str, str]:
    """A tiny uniform cross-stream offset on the initial condition only (not
    on the farfield boundary target) breaks the O-grid's exact left-right
    symmetry so the wake instability grows from a real (if small) disturbance
    rather than waiting on discretization round-off alone; this is a standard
    device for triggering vortex shedding from an impulsive start and does
    not bias the eventual limit cycle, which the stationarity gate below
    checks for independently."""
    u_internal = f"({U_INF:g} {perturbation:g} 0)"
    u_free = f"({U_INF:g} 0 0)"
    u_text = (
        _foam_header("volVectorField", "U", "0")
        + "dimensions      [0 1 -1 0 0 0 0];\n\n"
        + f"internalField   uniform {u_internal};\n\n"
        + "boundaryField\n{\n"
        + "    farfield\n    {\n"
        + "        type            freestreamVelocity;\n"
        + f"        freestreamValue uniform {u_free};\n"
        + f"        value           uniform {u_free};\n"
        + "    }\n"
        + "    cylinder\n    {\n        type            noSlip;\n    }\n"
        + "    frontAndBack\n    {\n        type            empty;\n    }\n"
        + "}\n"
    )
    p_text = (
        _foam_header("volScalarField", "p", "0")
        + "dimensions      [0 2 -2 0 0 0 0];\n\n"
        + "internalField   uniform 0;\n\n"
        + "boundaryField\n{\n"
        + "    farfield\n    {\n"
        + "        type            freestreamPressure;\n"
        + "        freestreamValue uniform 0;\n"
        + "        value           uniform 0;\n"
        + "    }\n"
        + "    cylinder\n    {\n        type            zeroGradient;\n    }\n"
        + "    frontAndBack\n    {\n        type            empty;\n    }\n"
        + "}\n"
    )
    return {"U": u_text, "p": p_text}


def build_case(case_dir: Path, *, reynolds: float, farfield_diameters: float = 20.0,
              n_radial: int = 90, n_tangential: int = 70,
              first_cell: float = 0.006, end_time: float = 150.0,
              dt0: float = 0.005) -> dict[str, Any]:
    case = Path(case_dir)
    for sub in ("0", "constant", "system"):
        (case / sub).mkdir(parents=True, exist_ok=True)

    nu = reynolds_to_nu(reynolds)
    (case / "system" / "blockMeshDict").write_text(
        block_mesh_dict(DIAMETER, farfield_diameters, n_radial, n_tangential, first_cell))
    (case / "system" / "fvSchemes").write_text(fv_schemes(limited=False, transient=True))
    (case / "system" / "fvSolution").write_text(pimple_fv_solution())
    (case / "constant" / "transportProperties").write_text(transport_properties(nu))
    (case / "constant" / "turbulenceProperties").write_text(_LAMINAR_TURBULENCE)
    control = pimple_control_dict(
        end_time, dt0, patch="cylinder", aref=DIAMETER * SPAN,
        drag_dir="(1 0 0)", lift_dir="(0 1 0)", max_co=1.5, adjustable=True)
    (case / "system" / "controlDict").write_text(control)
    for name, text in initial_fields().items():
        (case / "0" / name).write_text(text)
    return {"reynolds": reynolds, "nu": nu, "n_radial": n_radial,
            "n_tangential": n_tangential, "first_cell": first_cell,
            "farfield_diameters": farfield_diameters, "end_time": end_time}


def run_case(reynolds: float, out_dir: Path, log: Callable[[str], None] = print,
            **build_kwargs) -> dict[str, Any]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    case = out_dir / "case"
    remote_dir = _RUN_ROOT / f"cyl-re{reynolds:g}"
    shutil.rmtree(remote_dir, ignore_errors=True)
    remote_dir.parent.mkdir(parents=True, exist_ok=True)

    params = build_case(case, reynolds=reynolds, **build_kwargs)
    shutil.copytree(case, remote_dir)

    timings: dict[str, float] = {}
    for step, args, timeout in (
            ("blockMesh", ["blockMesh"], 600),
            ("checkMesh", ["checkMesh", "-allTopology", "-allGeometry"], 600)):
        start = time.monotonic()
        result = _foam(args, remote_dir, f"log.{step}", timeout=timeout)
        timings[step] = round(time.monotonic() - start, 1)
        _copy_best_effort(remote_dir / f"log.{step}", out_dir / f"log.{step}")
        log(f"[cyl-re{reynolds:g}] {step} done in {timings[step]:.1f}s "
            f"(exit {result.returncode})")
        if step == "blockMesh" and result.returncode != 0:
            raise RuntimeError(f"cyl-re{reynolds:g}: blockMesh failed")

    start = time.monotonic()
    log(f"[cyl-re{reynolds:g}] pimpleFoam started, end_time={params['end_time']:g}")
    result = _foam(["pimpleFoam"], remote_dir, "log.pimpleFoam", timeout=14400)
    timings["pimpleFoam"] = round(time.monotonic() - start, 1)
    _copy_best_effort(remote_dir / "log.pimpleFoam", out_dir / "log.pimpleFoam")
    if result.returncode != 0:
        tail = (remote_dir / "log.pimpleFoam").read_text(errors="replace")
        raise RuntimeError(f"cyl-re{reynolds:g}: pimpleFoam failed:\n"
                           + "\n".join(tail.splitlines()[-25:]))
    log(f"[cyl-re{reynolds:g}] pimpleFoam finished in {timings['pimpleFoam']:.1f}s")

    shutil.rmtree(out_dir / "postProcessing", ignore_errors=True)
    _copy_best_effort(remote_dir / "postProcessing", out_dir / "postProcessing")
    coeff_files = sorted((out_dir / "postProcessing").rglob("coefficient*.dat"))
    if not coeff_files:
        raise RuntimeError(f"cyl-re{reynolds:g}: no forceCoeffs output")
    history = parse_coefficient_history(coeff_files[-1].read_text(errors="replace"))
    times = history["Time"]
    end_time = params["end_time"]
    t_start = 0.5 * end_time
    cd_stats = time_weighted_stats(times, history["Cd"], t_start)
    cl_stats = time_weighted_stats(times, history["Cl"], t_start)
    period = measure_period(times, history["Cl"], t_start)
    if cd_stats is None or cl_stats is None:
        raise RuntimeError(f"cyl-re{reynolds:g}: averaging window empty "
                           f"(ran to t={times[-1] if times else 0:g}, "
                           f"requested window start {t_start:g})")
    drift = halves_drift(times, history["Cd"], cd_stats["window_start"], cd_stats["window_end"])
    if drift is None:
        raise RuntimeError(f"cyl-re{reynolds:g}: halves_drift could not be "
                           f"computed (one half of the averaging window has "
                           f"too few samples) -- stationarity is UNKNOWN, "
                           f"not passing, so no Cd/Cl may be quoted")
    if drift["relative_drift"] > 0.10:
        raise RuntimeError(
            f"cyl-re{reynolds:g}: Cd mean still drifting across the "
            f"averaging window (first half {drift['first_half_mean']:.5f}, "
            f"second half {drift['second_half_mean']:.5f}, "
            f"{100 * drift['relative_drift']:.1f}% relative drift) -- this "
            f"is a mid-transient snapshot, not a stationary time-average, "
            f"and must not be quoted as Cd/St")
    strouhal = (DIAMETER / (period * U_INF)) if period else None
    record = {
        "reynolds": reynolds, "nu": params["nu"],
        "cells": params["n_radial"] * params["n_tangential"] * 4,
        "end_time": end_time, "steps": len(times),
        "cd_mean": cd_stats["mean"], "cd_band": cd_stats["band"],
        "cd_lo": cd_stats["lo"], "cd_hi": cd_stats["hi"],
        "cd_relative_drift": drift["relative_drift"],
        "cd_first_half_mean": drift["first_half_mean"],
        "cd_second_half_mean": drift["second_half_mean"],
        "cl_mean": cl_stats["mean"], "cl_band": cl_stats["band"],
        "cl_lo": cl_stats["lo"], "cl_hi": cl_stats["hi"],
        "averaging_window": [cd_stats["window_start"], cd_stats["window_end"]],
        "period": period, "strouhal": strouhal,
        "wall_seconds": sum(timings.values()), "timings": timings,
    }
    st_text = f"St {strouhal:.4f}" if strouhal else "no period detected"
    log(f"[cyl-re{reynolds:g}] Cd {cd_stats['mean']:.4f} (band {cd_stats['band']:.4f}), "
        f"Cl' (half-band) {0.5 * cl_stats['band']:.4f}, {st_text}")
    return record


def main(argv: list[str] | None = None) -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reynolds", type=float, required=True)
    parser.add_argument("--out", type=str, required=True)
    parser.add_argument("--end-time", type=float, default=150.0)
    args = parser.parse_args(argv)
    record = run_case(args.reynolds, Path(args.out), end_time=args.end_time)
    out_json = Path(args.out) / "record.json"
    out_json.write_text(json.dumps(record, indent=2))
    print(json.dumps(record, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
