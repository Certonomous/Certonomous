#!/usr/bin/env python3
"""F5a: unsteady 2D cylinder Reynolds ladder (1000 -> 2000 -> 3900 -> 5000 ->
10000 -> 1e5 -> 1e6), gated rung by rung against literature (see
references.py for every citation actually fetched and read this task).

Reuses, unchanged, the prior-work O-grid mesh generator, PIMPLE control/
solution dicts, and stationarity machinery from sdk/workflows -- see the
docstrings of cylinder_vortex_shedding.py and tmr_verification.py for why
those exist and were validated (St within 0.7% of Roshko at Re=100-180).

New in this module (not in the prior work, because the prior work never
needed it): a kOmegaSST URANS closure for Re>=3900 (turbulent wake, laminar
separation -- a laminar solve is not defensible up there), MPI-parallel
staging capped at 4 ranks for the larger meshes, and two new measurements
the prior work did not extract: base pressure coefficient (a probe just
downstream of the cylinder, at the wake-facing/leeward point) and
recirculation-bubble length (a fan of centerline probes downstream of the
base, mean-velocity sign crossing located by linear interpolation between
the two straddling probes).
"""
from __future__ import annotations

import json
import math
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, Sequence

_HERE = Path(__file__).resolve()
_REPO_ROOT = _HERE.parents[4]
_SDK = _REPO_ROOT / "sdk"
sys.path.insert(0, str(_SDK))

from workflows.tmr_verification import (          # noqa: E402
    _foam, _foam_header, _run_prefix, _copy_best_effort,
    fv_schemes, transport_properties, time_weighted_stats, measure_period,
    halves_drift, _decompose_par_dict,
)
from workflows.cylinder_vortex_shedding import (   # noqa: E402
    DIAMETER, U_INF, SPAN, reynolds_to_nu, block_mesh_dict,
)
from chief_engineer.head_engineer import parse_coefficient_history  # noqa: E402

_RUN_ROOT = Path.home() / "certonomous-runs" / "f5a-cylinder-ladder"

_LAMINAR_TURBULENCE = (
    _foam_header("dictionary", "turbulenceProperties", "constant")
    + "simulationType  laminar;\n"
)
_RAS_TURBULENCE = (
    _foam_header("dictionary", "turbulenceProperties", "constant")
    + "simulationType  RAS;\n\nRAS\n{\n    RASModel        kOmegaSST;\n"
    + "    turbulence      on;\n    printCoeffs     on;\n}\n"
)


# ---------------------------------------------------------------------------
# Near-wall sizing
# ---------------------------------------------------------------------------

def estimate_first_cell(reynolds: float, target_yplus: float = 1.0) -> float:
    """Order-of-magnitude first-cell sizing from a laminar flat-plate
    friction estimate (Blasius Cf = 0.664/sqrt(Re)) -- deliberately crude
    (the true cylinder boundary layer is not a flat plate and separates
    well before any turbulent transition in this subcritical regime), used
    only to seed a mesh; the ACTUAL y+ achieved is measured after every run
    via OpenFOAM's own yPlus function object and reported, not assumed."""
    nu = reynolds_to_nu(reynolds)
    cf = 0.664 / math.sqrt(reynolds)
    u_tau = U_INF * math.sqrt(cf / 2.0)
    return target_yplus * nu / u_tau


# ---------------------------------------------------------------------------
# URANS (kOmegaSST) fields: farfield BC mirrors the existing laminar
# freestreamVelocity/freestreamPressure convention; k/omega/nut add the
# generic OpenFOAM "freestream" type (works for any field, switches
# fixedValue/zeroGradient on local flux direction) at the farfield patch,
# and the SAME low-Re wall treatment tmr_verification.py's flat-plate case
# uses at the wall (kLowReWallFunction / omegaWallFunction blended=true /
# nutLowReWallFunction) -- resolved-viscous-sublayer, not a log-law wall
# function, matching the target y+~1 mesh sizing above.
# ---------------------------------------------------------------------------

def freestream_turbulence(reynolds: float) -> dict[str, float]:
    """Deliberately very low freestream turbulence (eddy-viscosity ratio
    0.009, the same ratio the NASA TMR flat-plate case specifies -- see
    tmr_verification.py's own docstring) so the model does not trip the
    boundary layer turbulent ahead of the (laminar, per the task's own
    framing) separation point; no transition model is used, matching
    standard practice in the Re=3900 URANS literature (e.g. the SST-DDES/
    SST-IDDES runs in He/Zhao/Wan, references.py)."""
    nu = reynolds_to_nu(reynolds)
    intensity = 0.0005
    k_inf = 1.5 * (intensity * U_INF) ** 2
    nut_inf = 0.009 * nu
    omega_inf = k_inf / nut_inf
    return {"k": k_inf, "omega": omega_inf, "nut": nut_inf}


def initial_fields_urans(reynolds: float, perturbation: float = 0.1) -> dict[str, str]:
    nu = reynolds_to_nu(reynolds)
    ft = freestream_turbulence(reynolds)
    u_internal = f"({U_INF:g} {perturbation:g} 0)"
    u_free = f"({U_INF:g} 0 0)"
    u_text = (
        _foam_header("volVectorField", "U", "0")
        + "dimensions      [0 1 -1 0 0 0 0];\n\n"
        + f"internalField   uniform {u_internal};\n\n"
        + "boundaryField\n{\n"
        + "    farfield\n    {\n        type            freestreamVelocity;\n"
        + f"        freestreamValue uniform {u_free};\n"
        + f"        value           uniform {u_free};\n    }}\n"
        + "    cylinder\n    {\n        type            noSlip;\n    }\n"
        + "    frontAndBack\n    {\n        type            empty;\n    }\n}\n"
    )
    p_text = (
        _foam_header("volScalarField", "p", "0")
        + "dimensions      [0 2 -2 0 0 0 0];\n\n"
        + "internalField   uniform 0;\n\nboundaryField\n{\n"
        + "    farfield\n    {\n        type            freestreamPressure;\n"
        + "        freestreamValue uniform 0;\n        value           uniform 0;\n    }\n"
        + "    cylinder\n    {\n        type            zeroGradient;\n    }\n"
        + "    frontAndBack\n    {\n        type            empty;\n    }\n}\n"
    )

    def scalar(name: str, dims: str, value: float, wall_lines: str) -> str:
        return (
            _foam_header("volScalarField", name, "0")
            + f"dimensions      {dims};\n\n"
            + f"internalField   uniform {value:.8g};\n\nboundaryField\n{{\n"
            + "    farfield\n    {\n        type            freestream;\n"
            + f"        freestreamValue uniform {value:.8g};\n"
            + f"        value           uniform {value:.8g};\n    }}\n"
            + f"    cylinder\n    {{\n{wall_lines}    }}\n"
            + "    frontAndBack\n    {\n        type            empty;\n    }\n}\n"
        )

    k_text = scalar("k", "[0 2 -2 0 0 0 0]", ft["k"],
                    "        type            kLowReWallFunction;\n"
                    "        value           uniform 1e-12;\n")
    omega_text = scalar("omega", "[0 0 -1 0 0 0 0]", ft["omega"],
                        "        type            omegaWallFunction;\n"
                        "        blended         true;\n"
                        f"        value           uniform {ft['omega']:.8g};\n")
    nut_text = scalar("nut", "[0 2 -1 0 0 0 0]", ft["nut"],
                      "        type            nutLowReWallFunction;\n"
                      "        value           uniform 0;\n")
    return {"U": u_text, "p": p_text, "k": k_text, "omega": omega_text, "nut": nut_text}


def initial_fields_laminar(perturbation: float = 0.1) -> dict[str, str]:
    u_internal = f"({U_INF:g} {perturbation:g} 0)"
    u_free = f"({U_INF:g} 0 0)"
    u_text = (
        _foam_header("volVectorField", "U", "0")
        + "dimensions      [0 1 -1 0 0 0 0];\n\n"
        + f"internalField   uniform {u_internal};\n\nboundaryField\n{{\n"
        + "    farfield\n    {\n        type            freestreamVelocity;\n"
        + f"        freestreamValue uniform {u_free};\n"
        + f"        value           uniform {u_free};\n    }}\n"
        + "    cylinder\n    {\n        type            noSlip;\n    }\n"
        + "    frontAndBack\n    {\n        type            empty;\n    }\n}\n"
    )
    p_text = (
        _foam_header("volScalarField", "p", "0")
        + "dimensions      [0 2 -2 0 0 0 0];\n\n"
        + "internalField   uniform 0;\n\nboundaryField\n{\n"
        + "    farfield\n    {\n        type            freestreamPressure;\n"
        + "        freestreamValue uniform 0;\n        value           uniform 0;\n    }\n"
        + "    cylinder\n    {\n        type            zeroGradient;\n    }\n"
        + "    frontAndBack\n    {\n        type            empty;\n    }\n}\n"
    )
    return {"U": u_text, "p": p_text}


# ---------------------------------------------------------------------------
# controlDict with the two new probe families (base Cp, centerline Lr)
# ---------------------------------------------------------------------------

def base_probe_point(first_cell: float) -> tuple[float, float, float]:
    x = DIAMETER / 2.0 + 1.5 * first_cell
    return (x, 0.0, SPAN / 2.0)


def centerline_probe_points(lo_over_d: float = 0.05, hi_over_d: float = 2.4,
                            step_over_d: float = 0.05) -> list[tuple[float, float, float]]:
    pts = []
    n = int(round((hi_over_d - lo_over_d) / step_over_d)) + 1
    for i in range(n):
        s = lo_over_d + i * step_over_d
        x = DIAMETER / 2.0 + s * DIAMETER
        pts.append((x, 0.0, SPAN / 2.0))
    return pts


def _probes_block(name: str, field: str, points: Sequence[tuple[float, float, float]]) -> str:
    locs = "\n".join(f"        ({x:.6g} {y:.6g} {z:.6g})" for x, y, z in points)
    return (
        f"    {name}\n    {{\n        type            probes;\n"
        f"        libs            (sampling);\n"
        f"        writeControl    timeStep;\n        writeInterval   1;\n"
        f"        fields          ({field});\n        probeLocations\n        (\n{locs}\n        );\n    }}\n"
    )


def control_dict(end_time: float, dt0: float, *, aref: float, max_co: float,
                 base_point: tuple[float, float, float],
                 centerline_points: Sequence[tuple[float, float, float]]) -> str:
    return _foam_header("dictionary", "controlDict", "system") + f"""
application     pimpleFoam;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         {end_time};
deltaT          {dt0};
adjustTimeStep  yes;
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
        patches         (cylinder);
        rho             rhoInf;
        rhoInf          1.0;
        magUInf         {U_INF};
        lRef            1.0;
        Aref            {DIAMETER * SPAN};
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
""" + _probes_block("probesBase", "p", [base_point]) \
    + _probes_block("probesCenterline", "U", centerline_points) + "}\n"


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


# ---------------------------------------------------------------------------
# Probe parsing
# ---------------------------------------------------------------------------

def parse_probes_scalar(text: str) -> tuple[list[float], list[list[float]]]:
    times: list[float] = []
    rows: list[list[float]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        times.append(float(parts[0]))
        rows.append([float(v) for v in parts[1:]])
    return times, rows


def parse_probes_vector(text: str) -> tuple[list[float], list[list[tuple[float, float, float]]]]:
    times: list[float] = []
    rows: list[list[tuple[float, float, float]]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # "(ux uy uz) (ux uy uz) ..." after the leading time column
        first_paren = line.find("(")
        t = float(line[:first_paren].strip())
        body = line[first_paren:]
        nums = [float(x) for x in body.replace("(", " ").replace(")", " ").split()]
        vecs = [tuple(nums[i:i + 3]) for i in range(0, len(nums), 3)]
        times.append(t)
        rows.append(vecs)
    return times, rows


def base_cpb(out_dir: Path, t_start: float) -> dict[str, Any] | None:
    files = sorted((out_dir / "postProcessing" / "probesBase").rglob("p"))
    if not files:
        return None
    times, rows = parse_probes_scalar(files[-1].read_text(errors="replace"))
    p_series = [row[0] for row in rows if row]
    stats = time_weighted_stats(times, p_series, t_start)
    if stats is None:
        return None
    # incompressible p is kinematic (p/rho); Cp = p/(0.5*U_inf^2), rhoInf=1
    cp = stats["mean"] / (0.5 * U_INF ** 2)
    return {"p_mean": stats["mean"], "cp": cp, "cpb_magnitude": -cp,
            "band": stats["band"] / (0.5 * U_INF ** 2)}


def recirculation_length(out_dir: Path, t_start: float,
                         points: Sequence[tuple[float, float, float]]) -> dict[str, Any] | None:
    files = sorted((out_dir / "postProcessing" / "probesCenterline").rglob("U"))
    if not files:
        return None
    times, rows = parse_probes_vector(files[-1].read_text(errors="replace"))
    n_probes = len(points)
    profile: list[tuple[float, float]] = []
    for i in range(n_probes):
        ux_series = [row[i][0] for row in rows if len(row) > i]
        stats = time_weighted_stats(times, ux_series, t_start)
        if stats is None:
            continue
        x = points[i][0]
        profile.append((x, stats["mean"]))
    if len(profile) < 2:
        return None
    lr = None
    for (x0, u0), (x1, u1) in zip(profile, profile[1:]):
        if u0 < 0 <= u1:
            frac = (0.0 - u0) / (u1 - u0) if u1 != u0 else 0.0
            x_cross = x0 + frac * (x1 - x0)
            lr = x_cross - DIAMETER / 2.0
            break
    return {"lr_over_d": (lr / DIAMETER) if lr is not None else None,
            "profile": profile,
            "u_min": min(u for _, u in profile),
            "any_reversed_flow": any(u < 0 for _, u in profile)}


# ---------------------------------------------------------------------------
# Case build / run
# ---------------------------------------------------------------------------

def build_case(case_dir: Path, *, reynolds: float, turbulence: str,
              farfield_diameters: float, n_radial: int, n_tangential: int,
              first_cell: float, end_time: float, dt0: float, max_co: float,
              perturbation: float = 0.1) -> dict[str, Any]:
    case = Path(case_dir)
    for sub in ("0", "constant", "system"):
        (case / sub).mkdir(parents=True, exist_ok=True)
    nu = reynolds_to_nu(reynolds)
    (case / "system" / "blockMeshDict").write_text(
        block_mesh_dict(DIAMETER, farfield_diameters, n_radial, n_tangential, first_cell))
    (case / "system" / "fvSchemes").write_text(fv_schemes(limited=False, transient=True))
    (case / "system" / "fvSolution").write_text(pimple_fv_solution())
    (case / "constant" / "transportProperties").write_text(transport_properties(nu))
    base_pt = base_probe_point(first_cell)
    cl_pts = centerline_probe_points()
    (case / "system" / "controlDict").write_text(
        control_dict(end_time, dt0, aref=DIAMETER * SPAN, max_co=max_co,
                    base_point=base_pt, centerline_points=cl_pts))
    if turbulence == "laminar":
        (case / "constant" / "turbulenceProperties").write_text(_LAMINAR_TURBULENCE)
        for name, text in initial_fields_laminar(perturbation).items():
            (case / "0" / name).write_text(text)
    elif turbulence == "kOmegaSST":
        (case / "constant" / "turbulenceProperties").write_text(_RAS_TURBULENCE)
        for name, text in initial_fields_urans(reynolds, perturbation).items():
            (case / "0" / name).write_text(text)
    else:
        raise ValueError(f"unknown turbulence model {turbulence!r}")
    return {"reynolds": reynolds, "nu": nu, "turbulence": turbulence,
            "n_radial": n_radial, "n_tangential": n_tangential,
            "cells": n_radial * n_tangential * 4, "first_cell": first_cell,
            "farfield_diameters": farfield_diameters, "end_time": end_time,
            "dt0": dt0, "max_co": max_co, "base_point": base_pt,
            "centerline_points": cl_pts, "perturbation": perturbation}


def run_case(name: str, out_dir: Path, log: Callable[[str], None] = print, *,
            ranks: int = 1, solver_timeout: float = 28800.0,
            **build_kwargs) -> dict[str, Any]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    case = out_dir / "case"
    remote_dir = _RUN_ROOT / name
    shutil.rmtree(remote_dir, ignore_errors=True)
    remote_dir.parent.mkdir(parents=True, exist_ok=True)

    params = build_case(case, **build_kwargs)
    shutil.copytree(case, remote_dir)

    timings: dict[str, float] = {}
    for step, args, timeout in (
            ("blockMesh", ["blockMesh"], 900),
            ("checkMesh", ["checkMesh", "-allTopology", "-allGeometry"], 900)):
        start = time.monotonic()
        result = _foam(args, remote_dir, f"log.{step}", timeout=timeout)
        timings[step] = round(time.monotonic() - start, 1)
        _copy_best_effort(remote_dir / f"log.{step}", out_dir / f"log.{step}")
        log(f"[{name}] {step} done in {timings[step]:.1f}s (exit {result.returncode})")
        if step == "blockMesh" and result.returncode != 0:
            raise RuntimeError(f"{name}: blockMesh failed")

    if ranks > 1:
        with (remote_dir / "system" / "decomposeParDict").open("w", newline="\n") as fh:
            fh.write(_decompose_par_dict(ranks))
        start = time.monotonic()
        result = _foam(["decomposePar", "-force"], remote_dir, "log.decomposePar", timeout=1800)
        timings["decomposePar"] = round(time.monotonic() - start, 1)
        _copy_best_effort(remote_dir / "log.decomposePar", out_dir / "log.decomposePar")
        if result.returncode != 0:
            raise RuntimeError(f"{name}: decomposePar failed")
        log(f"[{name}] decomposePar ({ranks} ranks) done in {timings['decomposePar']:.1f}s")
        solve_args = [*_run_prefix(), "mpirun", "-np", str(ranks), "pimpleFoam", "-parallel"]
    else:
        solve_args = [*_run_prefix(), "pimpleFoam"]

    start = time.monotonic()
    log(f"[{name}] pimpleFoam started ({params['turbulence']}, "
        f"{params['cells']} cells, {ranks} rank(s)), end_time={params['end_time']:g}")
    log_path = remote_dir / "log.pimpleFoam"
    with log_path.open("w") as lf:
        result = subprocess.run(solve_args, stdout=lf, stderr=subprocess.STDOUT,
                                cwd=str(remote_dir), timeout=solver_timeout)
    timings["pimpleFoam"] = round(time.monotonic() - start, 1)
    _copy_best_effort(log_path, out_dir / "log.pimpleFoam")
    if result.returncode != 0:
        tail = log_path.read_text(errors="replace")
        raise RuntimeError(f"{name}: pimpleFoam failed:\n" + "\n".join(tail.splitlines()[-30:]))
    log(f"[{name}] pimpleFoam finished in {timings['pimpleFoam']:.1f}s")

    shutil.rmtree(out_dir / "postProcessing", ignore_errors=True)
    _copy_best_effort(remote_dir / "postProcessing", out_dir / "postProcessing")
    coeff_files = sorted((out_dir / "postProcessing").rglob("coefficient*.dat"))
    if not coeff_files:
        raise RuntimeError(f"{name}: no forceCoeffs output")
    history = parse_coefficient_history(coeff_files[-1].read_text(errors="replace"))
    times = history["Time"]
    end_time = params["end_time"]
    t_start = 0.5 * end_time
    cd_stats = time_weighted_stats(times, history["Cd"], t_start)
    cl_stats = time_weighted_stats(times, history["Cl"], t_start)
    period = measure_period(times, history["Cl"], t_start)
    if cd_stats is None or cl_stats is None:
        raise RuntimeError(f"{name}: averaging window empty "
                           f"(ran to t={times[-1] if times else 0:g}, "
                           f"requested window start {t_start:g})")
    drift = halves_drift(times, history["Cd"], cd_stats["window_start"], cd_stats["window_end"])
    if drift is None:
        raise RuntimeError(f"{name}: halves_drift undecidable -- stationarity UNKNOWN")
    yplus_files = sorted((out_dir / "postProcessing").rglob("yPlus.dat"))
    yplus_text = yplus_files[-1].read_text(errors="replace") if yplus_files else ""

    cpb = base_cpb(out_dir, t_start)
    lr = recirculation_length(out_dir, t_start, params["centerline_points"])

    strouhal = (DIAMETER / (period * U_INF)) if period else None
    record = {
        "name": name, "reynolds": params["reynolds"], "nu": params["nu"],
        "turbulence": params["turbulence"], "cells": params["cells"],
        "n_radial": params["n_radial"], "n_tangential": params["n_tangential"],
        "first_cell": params["first_cell"], "farfield_diameters": params["farfield_diameters"],
        "ranks": ranks, "end_time": end_time, "dt0": params["dt0"],
        "max_co": params["max_co"], "steps": len(times),
        "cd_mean": cd_stats["mean"], "cd_band": cd_stats["band"],
        "cd_relative_drift": drift["relative_drift"],
        "cd_first_half_mean": drift["first_half_mean"],
        "cd_second_half_mean": drift["second_half_mean"],
        "cl_mean": cl_stats["mean"], "cl_band": cl_stats["band"],
        "averaging_window": [cd_stats["window_start"], cd_stats["window_end"]],
        "period": period, "strouhal": strouhal,
        "cpb": cpb, "recirculation": lr,
        "yplus_raw": yplus_text.strip().splitlines()[-3:] if yplus_text else [],
        "wall_seconds": sum(timings.values()), "timings": timings,
        "stationary": drift["relative_drift"] <= 0.10,
    }
    lr_txt = f"Lr/D {lr['lr_over_d']:.3f}" if lr and lr["lr_over_d"] else "Lr/D not found"
    cpb_txt = f"-Cpb {cpb['cpb_magnitude']:.3f}" if cpb else "Cpb n/a"
    st_txt = f"St {strouhal:.4f}" if strouhal else "no period detected"
    log(f"[{name}] Cd {cd_stats['mean']:.4f} (drift {100*drift['relative_drift']:.1f}%), "
        f"{st_txt}, {cpb_txt}, {lr_txt}, wall {record['wall_seconds']:.0f}s")
    return record


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True)
    parser.add_argument("--reynolds", type=float, required=True)
    parser.add_argument("--turbulence", choices=["laminar", "kOmegaSST"], required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--n-radial", type=int, default=90)
    parser.add_argument("--n-tangential", type=int, default=80)
    parser.add_argument("--first-cell", type=float, default=None)
    parser.add_argument("--farfield-diameters", type=float, default=20.0)
    parser.add_argument("--end-time", type=float, default=90.0)
    parser.add_argument("--dt0", type=float, default=0.005)
    parser.add_argument("--max-co", type=float, default=1.5)
    parser.add_argument("--ranks", type=int, default=1)
    parser.add_argument("--perturbation", type=float, default=0.1)
    parser.add_argument("--solver-timeout", type=float, default=28800.0)
    args = parser.parse_args(argv)

    first_cell = args.first_cell
    if first_cell is None:
        if args.turbulence == "laminar":
            first_cell = 0.01 * math.sqrt(200.0 / args.reynolds) if args.reynolds > 200 else 0.01
        else:
            first_cell = estimate_first_cell(args.reynolds, target_yplus=1.0)

    record = run_case(
        args.name, Path(args.out), ranks=args.ranks,
        solver_timeout=args.solver_timeout,
        reynolds=args.reynolds, turbulence=args.turbulence,
        farfield_diameters=args.farfield_diameters, n_radial=args.n_radial,
        n_tangential=args.n_tangential, first_cell=first_cell,
        end_time=args.end_time, dt0=args.dt0, max_co=args.max_co,
        perturbation=args.perturbation)
    out_json = Path(args.out) / "record.json"
    out_json.write_text(json.dumps(record, indent=2, default=str))
    print(json.dumps({k: v for k, v in record.items()
                      if k not in ("recirculation",)}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
