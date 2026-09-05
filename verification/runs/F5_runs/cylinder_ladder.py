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
# NOT `parents[4]`, and this is a defect class rather than a typo: a
# repository root derived by COUNTING segments up from a path under a
# MOVING tree points somewhere else the moment the tree moves.  MOVE_MAP
# batch 7 made this file ONE SEGMENT SHALLOWER, so `parents[4]` went from
# the repository root to `/home/ubuntu`.  There is no path literal in the
# expression, so no prefix rewrite and no grep for `demo-output` reaches it
# -- the same class cost `sdk/tests/test_a2_shape.py:28` a green comparison
# over ten synthetic bodies at batch 6.  DERIVED BY SEARCHING for the
# marker, so the answer no longer depends on this file's depth.
_REPO_ROOT = next((_p for _p in Path(__file__).resolve().parents
                  if (_p / "scripts" / "lab_paths.py").is_file()), None)
if _REPO_ROOT is None:
    raise RuntimeError(
        "cannot locate scripts/lab_paths.py above %s; refusing to "
        "guess a repository root" % __file__)
_SDK = _REPO_ROOT / "sdk"
sys.path.insert(0, str(_SDK))

# THE SOLVE-EVIDENCE GUARD.  Loaded by explicit path rather than by putting
# `scripts/` on sys.path: a guard that can be shadowed is not a guard.  Missing
# guard == refuse to run, because run_case()'s first act is to delete its own
# remote directory and without the guard that delete is unconditional.
import importlib.util as _ilu  # noqa: E402

_GUARD_PATH = _REPO_ROOT / "scripts" / "solve_evidence_guard.py"
if not _GUARD_PATH.is_file():
    raise RuntimeError(
        f"solve-evidence guard not found at {_GUARD_PATH}; refusing to run. "
        "run_case() deletes its remote directory before building, and without "
        "the guard that delete is unconditional -- see the guard's docstring "
        "for the rung it would have destroyed.")
if "solve_evidence_guard" in sys.modules:
    # Registered once, reused everywhere: two module objects for one file give
    # SolveEvidencePresent two distinct classes, and a caller's `except` on one
    # silently misses the refusal raised by the other.
    solve_evidence_guard = sys.modules["solve_evidence_guard"]
else:
    _spec = _ilu.spec_from_file_location("solve_evidence_guard", _GUARD_PATH)
    solve_evidence_guard = _ilu.module_from_spec(_spec)
    sys.modules["solve_evidence_guard"] = solve_evidence_guard
    _spec.loader.exec_module(solve_evidence_guard)
safe_rmtree_for_restage = solve_evidence_guard.safe_rmtree_for_restage
safe_replace_mirror = solve_evidence_guard.safe_replace_mirror

from workflows.tmr_verification import (          # noqa: E402
    _foam, _foam_header, _run_prefix, _copy_best_effort,
    fv_schemes, transport_properties, time_weighted_stats, measure_period,
    halves_drift, _decompose_par_dict,
)
from workflows.cylinder_vortex_shedding import (   # noqa: E402
    DIAMETER, U_INF, SPAN, reynolds_to_nu, block_mesh_dict,
)
from chief_engineer.head_engineer import parse_coefficient_history  # noqa: E402
from chief_engineer import lever_echo  # noqa: E402

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


# =====================================================================================
# THE 4-RANK CAP.  Module docstring line 14 states "MPI-parallel staging capped at 4
# ranks for the larger meshes".  UNTIL THIS BLOCK THAT CAP WAS A SENTENCE AND NOTHING
# ELSE: measured, `ranks` occurred ten times in this file with ZERO asserts or raises
# mentioning it, against ten bare `raise` statements as a live control.  `--ranks` is an
# unbounded int that flowed straight to `mpirun -np`, so nothing prevented a 16-rank
# launch on an oversubscribed box.
#
# THIS IS M6SR ITEM 50's EXACT CLASS, ONE CAMPAIGN OVER -- a cap that lives in prose
# while the mechanism binds something else.  There the registered cap and the enforced
# timeout were two independent literals that happened to agree; here the registered cap
# had no enforced counterpart at all.  TWO CAMPAIGNS, ONE DEFECT SHAPE.
#
# THE CAP BINDS THE VALUE THAT REACHES `mpirun`, NOT A COPY OF IT.  `_np_arg()` is the
# ONLY producer of the `-np` argument: the string it returns IS the string passed, so a
# checked-then-discarded value is impossible by construction rather than by discipline.
# =====================================================================================
F5A_MAX_RANKS = 4          # module docstring line 14, verbatim: "capped at 4 ranks"


def _check_ranks(ranks: object) -> int:
    """Validate a rank count against the registered cap.  -> the int, or RAISES.

    Called at the serial/parallel branch as well as inside `_np_arg`, because a value
    below 1 would otherwise take the SERIAL branch silently and never reach the cap.

    THE BOOL TEST MUST COME FIRST, AND THAT ORDERING IS LOAD-BEARING.  `isinstance(True,
    int)` is True in Python, so `True` would pass the int test, become 1, and run SERIAL
    -- silently, which is the exact class this repair exists to close.  Testing for bool
    AFTER the int test would therefore never fire.
    AND IT GUARDS THE PATH argparse DOES NOT: `--ranks` is `type=int`, so the CLI already
    rejects a bool; this check protects PROGRAMMATIC callers, which bypass that
    validation entirely.  A guard that only covered the path already covered would be
    decoration.
    """
    if isinstance(ranks, bool) or not isinstance(ranks, int):
        raise RuntimeError(
            f"ranks must be an int, got {type(ranks).__name__} ({ranks!r}). "
            "REFUSED: a rank count that is not an integer cannot be capped.")
    if ranks < 1:
        raise RuntimeError(
            f"ranks={ranks} is below 1. REFUSED: a non-positive rank count would take "
            "the SERIAL branch silently and never be checked against the cap.")
    if ranks > F5A_MAX_RANKS:
        raise RuntimeError(
            f"ranks={ranks} exceeds the registered cap of {F5A_MAX_RANKS} "
            "(module docstring line 14: 'MPI-parallel staging capped at 4 ranks for the "
            "larger meshes'). REFUSED BEFORE ANY SOLVER STARTS. Until this check existed "
            "the cap was a sentence and nothing enforced it, so a 16-rank launch on an "
            "oversubscribed box was possible -- and oversubscription does not merely slow "
            "a run, it makes its core-minutes uninterpretable, because contention and "
            "misprediction can no longer be separated in the calibration row.")
    return ranks


def _np_arg(ranks: object) -> str:
    """THE ONLY PRODUCER OF `mpirun -np`'s ARGUMENT.  The cap binds HERE.

    The returned string is the one placed in the argument list, so the value that was
    checked and the value that runs are THE SAME OBJECT'S TEXT -- not a copy validated
    somewhere else and trusted afterwards.
    """
    return str(_check_ranks(ranks))


def run_case(name: str, out_dir: Path, log: Callable[[str], None] = print, *,
            ranks: int = 1, solver_timeout: float = 28800.0,
            **build_kwargs) -> dict[str, Any]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    case = out_dir / "case"
    remote_dir = _RUN_ROOT / name
    # WAS: shutil.rmtree(remote_dir, ignore_errors=True) -- unconditional and
    # silent about its own failures, as the FIRST act of run_case(), so
    # "re-run the rung" was the same keystroke as "destroy the rung".  Refuses
    # now when the directory holds time directories > 0 with fields
    # (reconstructed or under processor*/) or a postProcessing series with data
    # rows, and names what would have been lost.  No override flag, by
    # decision: the printed recovery is a human `mv` aside, which preserves the
    # physics.  See scripts/solve_evidence_guard.py and re2000's condition,
    # recorded at run_rung.py:harvest().
    safe_rmtree_for_restage(remote_dir)
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

    _check_ranks(ranks)          # covers the SERIAL path too (ranks < 1)
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
        solve_args = [*_run_prefix(), "mpirun", "-np", _np_arg(ranks), "pimpleFoam", "-parallel"]
    else:
        solve_args = [*_run_prefix(), "pimpleFoam"]

    start = time.monotonic()
    log(f"[{name}] pimpleFoam started ({params['turbulence']}, "
        f"{params['cells']} cells, {ranks} rank(s)), end_time={params['end_time']:g}")
    log_path = remote_dir / "log.pimpleFoam"
    with log_path.open("w") as lf:
        # The only launch in this module that does not already go through
        # tmr_verification._foam. `remote_dir` is the same object passed to
        # `cwd=` below, so the echoed directory and the executing directory
        # cannot disagree (L-45); the shared predicate decides what counts as
        # a solve, so `-postProcess` and utilities get nothing.
        block = lever_echo.echo_if_solver(solve_args, remote_dir)
        if block:
            lf.write(block)
            lf.flush()
        result = subprocess.run(solve_args, stdout=lf, stderr=subprocess.STDOUT,
                                cwd=str(remote_dir), timeout=solver_timeout)
    timings["pimpleFoam"] = round(time.monotonic() - start, 1)
    _copy_best_effort(log_path, out_dir / "log.pimpleFoam")
    if result.returncode != 0:
        tail = log_path.read_text(errors="replace")
        raise RuntimeError(f"{name}: pimpleFoam failed:\n" + "\n".join(tail.splitlines()[-30:]))
    log(f"[{name}] pimpleFoam finished in {timings['pimpleFoam']:.1f}s")

    # WAS: shutil.rmtree(out_dir/"postProcessing", ignore_errors=True) -- the
    # local mirror destroyed unconditionally, then refreshed BEST-EFFORT.  The
    # mirror is now removed only when the source can replace its rows.
    safe_replace_mirror(out_dir / "postProcessing", remote_dir / "postProcessing")
    _copy_best_effort(remote_dir / "postProcessing", out_dir / "postProcessing")
    coeff_path = _coefficient_series_path(out_dir)
    history = parse_coefficient_history(coeff_path.read_text(errors="replace"))
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


# =====================================================================================
# GAP 5(b) -- THE COEFFICIENT SERIES IS PICKED BY ROLE, NOT BY SORT ORDER.
#
# THE DEFECT: `sorted((out_dir/"postProcessing").rglob("coefficient*.dat"))[-1]`.  Where a
# collision has left BOTH `coefficient.dat` and `coefficient_0.dat`, ASCII ordering puts
# '.' (0x2E) before '_' (0x5F), so `[-1]` silently selected `coefficient_0.dat`.  That is
# the lab's standing `grep ... | tail -1` coin flip and L-490's instance #8: A FILE CHOSEN
# BY SORT ORDER RATHER THAN BY ROLE.
#
# THE HAZARD IS REAL, NARROW, AND WAS NOT YET REALISED.  MEASURED on this box, and the
# bytes are vendored beside this file at fixtures/coefficient_collision/:
#   coefficient.dat    2,730 bytes, 21 lines, t 0.0056601638 -> 0.063442255
#   coefficient_0.dat  3,638 bytes, 25 lines, t 0.0056601638 -> 0.099670273
# BOTH START AT THE SAME TIME and the values differ in the sixth digit, so they are TWO
# DIFFERENT RUNS OF THE SAME CASE -- not a continuation.  Preferring the unsuffixed name
# would harvest the SHORTER series on no better ground than its filename.  NEITHER IS
# CANONICAL BY ANY PROPERTY THIS CODE CAN READ, which is exactly when refusal is honest.
#
# AND REFUSAL WAS ESTABLISHED AFFORDABLE *BEFORE* IT WAS CHOSEN, NOT DISCOVERED AFTER.
# MEASURED across every F5 run tree on this box: TEN OF ELEVEN carry EXACTLY ONE
# `coefficient.dat` in EXACTLY ONE directory; only one pilot tree carries two.  A refusal
# that broke legitimate restart harvests would have been worse than the bug, so the
# distribution was measured first and the design chosen second.
# =====================================================================================
def _coefficient_series_path(out_dir: Path) -> Path:
    """THE SOLE SELECTOR of the force-coefficient series.  -> the path, or RAISES.

    Exactly one candidate is used.  MORE THAN ONE IS REFUSED, NEVER RESOLVED BY ORDER:
    a silent wrong pick is worse than a stop, because the wrong series grades cleanly.
    """
    found = sorted((Path(out_dir) / "postProcessing").rglob("coefficient*.dat"))
    if not found:
        raise RuntimeError(
            f"no forceCoeffs output under {out_dir}/postProcessing -- no "
            "coefficient*.dat exists. REFUSED: there is nothing to harvest.")
    if len(found) > 1:
        detail = "; ".join(f"{f} ({f.stat().st_size} bytes)" for f in found)
        raise RuntimeError(
            f"AMBIGUOUS FORCE-COEFFICIENT SERIES under {out_dir}/postProcessing: "
            f"{len(found)} candidates -- {detail}. REFUSED, AND DELIBERATELY NOT RESOLVED "
            "BY SORT ORDER. The previous code took sorted(...)[-1], which selects "
            "`coefficient_0.dat` over `coefficient.dat` because '.' sorts before '_' -- a "
            "collision file chosen by ASCII accident. Where two series start at the same "
            "time and differ in value they are two DIFFERENT RUNS, and no property this "
            "code can read says which is authoritative. Move the superseded file aside and "
            "re-harvest; do NOT let the harvester guess.")
    return found[0]


def selftest_rank_cap() -> int:
    """THE CAP'S PLANTED CONTROL.  A cap with no firing control is how gap 4 happened.

    Every limb is a DELTA: the clean twin must be ACCEPTED and the plant must be REFUSED.
    A suite that only showed refusals would be satisfied by a function that refuses
    everything, which would break every legitimate launch and pass this test.

    ⚠ THIS CONTROL LIVES INSIDE THE FILE IT GUARDS, WHICH IS WEAKER THAN AN EXTERNAL ONE,
    AND THE WEAKNESS IS RECORDED RATHER THAN GLOSSED.  It is internal for ONE reason and
    it is not convenience: THE COUPLING LIMB CANNOT BE WRITTEN FROM OUTSIDE.  An external
    control could exercise `_check_ranks` in isolation and would still pass if a future
    edit stopped routing the `-np` argument through `_np_arg` altogether -- the very
    regression that would reinstate gap 4.  A control that only validated the guard would
    have been BETTER placed outside; this one has to sit where it can see the call site.
    DO NOT READ THIS AS A GENERAL PREFERENCE FOR INTERNAL CONTROLS.
    """
    ok, fired = True, []

    # THE CLEAN TWINS -- these must be ACCEPTED, including the cap's own boundary value.
    for r in (1, 2, 3, F5A_MAX_RANKS):
        got = _np_arg(r)
        if got != str(r):
            ok = False
            fired.append(f"CLEAN {r}: _np_arg returned {got!r}, expected {str(r)!r}")
        else:
            fired.append(f"CLEAN {r}: accepted, -np argument {got!r}")

    # THE PLANTS -- each must be REFUSED.  16 is the value Section 7 named as the hazard.
    for r, why in ((F5A_MAX_RANKS + 1, "one over the cap"), (16, "the oversubscription "
                   "case Section 7 named"), (0, "would take the serial branch silently"),
                   (-1, "negative"), (2.0, "float, not int"), (True, "bool masquerading "
                   "as int")):
        try:
            _np_arg(r)
            ok = False
            fired.append(f"PLANT {r!r} ({why}): NOT REFUSED -- the cap does not bind")
        except RuntimeError:
            fired.append(f"PLANT {r!r} ({why}): REFUSED")

    # THE COUPLING LIMB: the checked value must BE the value that reaches mpirun, not a
    # copy.  Built the way run_case builds it, so a future edit that stops routing through
    # _np_arg breaks this rather than leaving it vacuously green.
    args = ["mpirun", "-np", _np_arg(F5A_MAX_RANKS), "pimpleFoam", "-parallel"]
    if args[args.index("-np") + 1] != str(F5A_MAX_RANKS):
        ok = False
        fired.append("COUPLING: the -np argument is not the value _np_arg returned")
    else:
        fired.append(f"COUPLING: mpirun receives {args[args.index('-np') + 1]!r}, the "
                     "string _np_arg returned -- checked value and passed value are one")

    for line in fired:
        print(f"  RANK-CAP {line}")
    print(f"  DISCRIMINATES: clean values accepted AND violating values refused = {ok}")
    print("RANK-CAP SELFTEST " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


PLANT_CD = 1.2345678901e+00          # gap 5(a): a value no real Cd will collide with
COEFF_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "coefficient_collision"
COEFF_FIXTURE_SOURCE = Path(
    "/home/ubuntu/certonomous-runs/f5a-cylinder-ladder/f5b_re1000_3d_pilot_stage"
    "/postProcessing/forceCoeffs1/0")


def selftest_coefficient_harvest() -> int:
    """GAP 5 -- THE HARVEST PATH'S PLANTED CONTROLS.  Both halves, one control.

    (a) THE READER: `parse_coefficient_history` had NO planted-zero control anywhere --
        measured, zero `plant` tokens in `sdk/chief_engineer/head_engineer.py` against 13
        `def`s as a live control.  ⚠ THE READER LIVES IN THAT MODULE, NOT IN THE F5 TREE;
        Section 7 says only "harvest path" and does not say where, which is itself a small
        instance of L-490's class.
    (b) THE SELECTOR: `_coefficient_series_path` must REFUSE an ambiguous set rather than
        resolve it by sort order.

    THE (b) FIXTURE IS THE REAL TWO-FILE SHAPE, VENDORED beside this file with its
    provenance.  A control planted into the shape you ASSUME can certify a reader that
    could never have matched the shape you FACE -- this lab has paid for that once.
    VENDORED rather than read live because the original is out-of-git, read-only to us and
    cleanable by anyone, and A CONTROL THAT GOES RED WHEN SOMEONE TIDIES A SCRATCH TREE
    TEACHES PEOPLE TO IGNORE ITS RED.
    AND THE DRIFT LIMB KEEPS THAT SAFE: while the original still exists the vendored bytes
    are asserted IDENTICAL to it, so the fixture cannot silently diverge from the reality
    it was captured from; when the original is gone the control still runs on bytes proved
    faithful at capture.
    """
    import tempfile
    ok, fired = True, []

    # ---- (a) PLANTED-ZERO ON THE READER.  A DELTA: the plant must be SEEN and the
    # unplanted twin must NOT carry it, so the reader is shown able to see both states.
    header = "# Time Cd Cl Cm\n"
    clean = header + "1.0 0.5 0.1 0.01\n2.0 0.6 0.2 0.02\n"
    planted = header + f"1.0 0.5 0.1 0.01\n2.0 {PLANT_CD!r} 0.2 0.02\n"
    c_clean = parse_coefficient_history(clean)
    c_plant = parse_coefficient_history(planted)
    saw, free = PLANT_CD in c_plant.get("Cd", []), PLANT_CD not in c_clean.get("Cd", [])
    if saw and free:
        fired.append(f"READER: planted Cd={PLANT_CD!r} and READ IT BACK; the unplanted "
                     "twin does NOT carry it -- a delta, not a colour")
    else:
        ok = False
        fired.append(f"READER: plant seen={saw}, clean free of it={free} -- a reader not "
                     "shown able to see a non-zero is not evidence (rule 3)")
    if c_clean.get("Time") != [1.0, 2.0]:
        ok = False
        fired.append(f"READER: Time read as {c_clean.get('Time')!r}, expected [1.0, 2.0]")
    else:
        fired.append("READER: Time column read back exactly")

    # ---- THE DRIFT LIMB.  While the original exists, the vendored bytes must equal it.
    names = ("coefficient.dat", "coefficient_0.dat")
    for n in names:
        v = COEFF_FIXTURE / n
        if not v.is_file():
            ok = False
            fired.append(f"FIXTURE: vendored {n} is MISSING at {v} -- this control REFUSES "
                         "rather than substituting a synthetic file")
    if all((COEFF_FIXTURE / n).is_file() for n in names):
        if COEFF_FIXTURE_SOURCE.is_dir() and all(
                (COEFF_FIXTURE_SOURCE / n).is_file() for n in names):
            drift = [n for n in names
                     if (COEFF_FIXTURE / n).read_bytes()
                     != (COEFF_FIXTURE_SOURCE / n).read_bytes()]
            if drift:
                ok = False
                fired.append(f"FIXTURE DRIFT: vendored copies differ from the live source "
                             f"for {drift} -- the fixture no longer represents reality")
            else:
                fired.append("FIXTURE: vendored bytes are IDENTICAL to the live source "
                             "(cross-checked against the original, which still exists)")
        else:
            fired.append("FIXTURE: the live source is GONE; running on vendored bytes "
                         "proved faithful at capture. NOT a failure -- this is why they "
                         "were vendored.")

    # ---- (b) THE SELECTOR, ON THE VENDORED REAL SHAPE.
    if all((COEFF_FIXTURE / n).is_file() for n in names):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            one = base / "single" / "postProcessing" / "forceCoeffs1" / "0"
            two = base / "collision" / "postProcessing" / "forceCoeffs1" / "0"
            one.mkdir(parents=True); two.mkdir(parents=True)
            (one / names[0]).write_bytes((COEFF_FIXTURE / names[0]).read_bytes())
            for n in names:
                (two / n).write_bytes((COEFF_FIXTURE / n).read_bytes())

            got = _coefficient_series_path(base / "single")
            if got.name == names[0]:
                fired.append(f"SELECTOR CLEAN TWIN: a single series is ACCEPTED, returning "
                             f"{got.name}")
            else:
                ok = False
                fired.append(f"SELECTOR CLEAN TWIN: returned {got.name!r}, expected "
                             f"{names[0]!r}")
            try:
                picked = _coefficient_series_path(base / "collision")
                ok = False
                fired.append("SELECTOR PLANT: the two-file collision was NOT refused -- it "
                             f"silently returned {picked.name!r}")
            except RuntimeError as exc:
                both = all(n in str(exc) for n in names)
                fired.append(f"SELECTOR PLANT: REFUSED, and the message names BOTH "
                             f"candidates = {both}")
                if not both:
                    ok = False

    for line in fired:
        print(f"  HARVEST {line}")
    print("  DISCRIMINATES: reader sees the plant AND misses it when absent; selector "
          f"accepts one series AND refuses two = {ok}")
    print("COEFFICIENT-HARVEST SELFTEST " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    # THE SELFTEST IS INTERCEPTED BEFORE `parse_args`, AND THAT IS NOT STYLE.
    # `--name`, `--reynolds`, `--turbulence` and `--out` are `required=True`, so argparse
    # exits 2 on their absence BEFORE any flag of ours is reached: checking
    # `args.selftest_rank_cap` after parsing left the control UNREACHABLE.  MEASURED, by
    # running it in place after applying the patch -- it is exactly gap 4's own shape one
    # level up, a guard that exists and cannot fire.
    _argv = sys.argv[1:] if argv is None else argv
    if "--selftest-rank-cap" in _argv:
        return selftest_rank_cap()
    if "--selftest-coefficient-harvest" in _argv:
        return selftest_coefficient_harvest()

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
    parser.add_argument("--selftest-rank-cap", action="store_true",
                        help="run the 4-rank cap's planted control and exit")
    parser.add_argument("--selftest-coefficient-harvest", action="store_true",
                        help="run the harvest path's planted controls and exit")
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
