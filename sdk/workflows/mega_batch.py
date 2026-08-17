"""Mega-batch runner — continuous REAL solver evaluations into a durable ledger.

This is the all-night accumulator for the website. It streams an unbounded,
*deterministic* sequence of designs through a bounded pool of workers, and
appends every finished evaluation as one JSON line to a durable ledger. Six
solver families are interleaved: steady laminar OpenFOAM cylinders, VSPAERO
vortex-lattice wing polars, a reduced-order valve-cycle screen, unsteady 2D
vortex-shedding cylinders (pimpleFoam, genuinely shedding), transonic
NACA0012 airfoils (rhoSimpleFoam, a real shock forms), and -- Family F10 --
the Ahmed body in 3D viscous RANS (simpleFoam, k-omega SST, wall functions,
snappyHexMesh), the batch's only genuinely 3D viscous CFD family: see
``demo-output/website/mega-batch/PHYSICS_FAMILIES.md`` for each family's
design space, validation gate, and measured per-evaluation cost,
``demo-output/website/mega-batch/F10_3D_VISCOUS_FAMILY.md`` for F10
specifically, and ``demo-output/website/mega-batch/F10_YPLUS_FIX.md`` for
why F10's mesh refinement now follows Reynolds number instead of being
fixed across the whole design space.

Two properties make it demo-safe:

- **Real only.** Both backends run the actual solvers (OpenFOAM ``simpleFoam``
  behind ``OPENFOAM_RUN_PREFIX``; VSPAERO behind ``OPENVSP_RUN_PREFIX``). Every
  ledger row is labelled ``real-solve``; nothing here is a model surrogate. If a
  solver is unreachable the batch refuses to fabricate — it records the failure.
- **Crash-durable + resumable.** Each design maps deterministically from its
  integer index (``design_for_index``), and every row carries that index. On
  restart the runner reads the ledger, learns which indices are already done,
  and resumes with the next un-attempted index — so an interrupted run picks up
  exactly where it left off without repeating or losing work.

The ledger row shape (one JSON object per line)::

    {"index", "solver", "label", "design", "metrics",
     "wall_seconds", "timestamp", "ok" [, "error"]
     [, "wall_time_excursion"]}

``wall_time_excursion`` appears only on a row the Monitor Standard's S9 rule
calls an excursion, and never on an ordinary row.

Concurrency is capped (default 4) to honour the machine's compute treaty; each
solve is its own process in its own directory, so the workers never share state.
Case directories are deleted after their metrics are extracted to bound disk use.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import shutil
import sys
import threading
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Make ``chief_engineer`` importable when run as a plain script (sdk/ on path).
_SDK_ROOT = Path(__file__).resolve().parents[1]
if str(_SDK_ROOT) not in sys.path:
    sys.path.insert(0, str(_SDK_ROOT))

from chief_engineer.openfoam import OpenFoamCylinderApi  # noqa: E402
from chief_engineer.vspaero import VspAeroWingApi  # noqa: E402
from chief_engineer.head_engineer import parse_coefficient_history  # noqa: E402
from chief_engineer.log_signatures import (  # noqa: E402
    WALL_TIME_FIELD,
    wall_time_record_field,
)
from chief_engineer.external_aero import analyse_surface, build_case  # noqa: E402
from workflows import cylinder_vortex_shedding as cvs  # noqa: E402
from workflows import transonic_airfoil as ta  # noqa: E402
from workflows.tmr_verification import _foam, parse_yplus_dat  # noqa: E402

# The one module that names this repository's tree (MOVE_MAP batch 3).
# Every name it exports is bound to a legacy/successor PAIR resolved
# against the filesystem at import, so the constants below are correct
# before the move, between batches and after it, with no edit here.
import sys as _sys  # noqa: E402
import pathlib as _pathlib  # noqa: E402
_LAB_PATHS_DIR = str(_pathlib.Path(__file__).resolve().parents[2]
                     / "scripts")
if _LAB_PATHS_DIR not in _sys.path:
    _sys.path.insert(0, _LAB_PATHS_DIR)
import lab_paths  # noqa: E402

CYLINDER = "openfoam-cylinder"
WING = "vspaero-wing"
VALVE = "reduced-order"
CYLINDER_UNSTEADY = "openfoam-cylinder-unsteady"
TRANSONIC_AIRFOIL = "rhosimplefoam-naca0012-transonic"
AHMED_VISCOUS_3D = "simplefoam-ahmed-3d-viscous"

# Family 1 (unsteady 2D vortex shedding) batch parameters, measured and
# locked in against the Roshko/Williamson Strouhal gate (PHYSICS_FAMILIES.md):
# end_time=90 with the 0.1 cross-stream perturbation lands the Re=100 case
# within 0.7% of St = 0.198*(1 - 19.7/Re) after the halves-drift stationarity
# gate passes; end_time=70 left more drift (6.5%) and end_time=60 with the
# module's own default 0.02 perturbation never reached the limit cycle at
# all (Cl was still rising every sample at t=60). Measured cost ~230-270s/eval.
UNSTEADY_CYLINDER_END_TIME = 90.0
UNSTEADY_CYLINDER_PERTURBATION = 0.1

# Family 2 (transonic) batch parameters -- see PHYSICS_FAMILIES.md for the
# convergence study this iteration cap is measured against.
TRANSONIC_ITERATIONS = 2000

# Family F10 (3D viscous RANS, Ahmed body) batch parameters -- see
# F10_3D_VISCOUS_FAMILY.md for the reproduction run these are measured
# against. This is a REUSE, not a rebuild: refinement=2 and iterations=250
# are exactly the settings mission-output/geometry-study/study-ahmed_25 used
# to reach its own VALIDATED tier (45,753 cells, Cd 0.3219 vs experiment
# 0.285, +-15% band) -- read directly off that case's own stored
# system/snappyHexMeshDict (`body { level (2 3); }`) and system/controlDict
# (`endTime 250;`), not re-derived. Air kinematic viscosity matches the same
# study's (and geometry_study.py's own) AIR_KINEMATIC_VISCOSITY convention.
AHMED_GEOMETRY_DIR = _SDK_ROOT / "geometry"
AHMED_REFINEMENT = 2
# refinement=2's first cell grows too far from the wall once Re climbs past
# ~2.8e6, pushing average y+ over the [30,500] wall-function ceiling -- see
# F10_YPLUS_FIX.md for the measured evidence (17/52 F10 rows failed the y+
# gate this way). The mesh now follows Reynolds number instead of being a
# single fixed recipe across the whole [1.5e6, 4.0e6] design space:
# refinement stays at 2 below the threshold (cheaper, and already
# comfortably in-band there) and steps up to 3 at/above it. Measured,
# real-dispatch numbers (F10_YPLUS_FIX.md): refinement=2 gives y+avg 255.85
# at Re=1.53e6, 438.99 at Re=2.73e6, 451.38 at Re=2.81e6 (all PASS) but
# 628.19 at Re=3.99e6 (FAIL); refinement=3 gives y+avg 463.89 at Re=3.99e6
# (PASS, ~7% margin under the 500 ceiling) and 190.88 / 325.48 at the
# lower/mid points (confirms the switch is not a knife-edge).
AHMED_REFINEMENT_RE_THRESHOLD = 2.8e6
AHMED_REFINEMENT_HIGH_RE = 3
AHMED_ITERATIONS = 250
AHMED_VISCOSITY = 1.5e-5
# Quality gates, non-negotiable -- an evaluation failing any of these is
# recorded ok=False, not silently kept. checkMesh thresholds reused verbatim
# from workflows/geometry_study.py's own MAX_NON_ORTHOGONALITY / MAX_SKEWNESS
# (the same gates the original Ahmed body study itself had to clear).
AHMED_NON_ORTHO_GATE = 70.0
AHMED_SKEWNESS_GATE = 4.0
# Residual gate matches build_case's own SIMPLE residualControl target
# (system/fvSolution: `residualControl { p 1e-4; U 1e-4; "(k|omega)" 1e-4; }`)
# -- the case is asking itself to reach 1e-4; the gate holds it to that.
AHMED_RESIDUAL_GATE = 1e-4
# y+ band for a kOmegaSST wall-function mesh: standard OpenFOAM wall-function
# guidance keeps the first cell in the log-law region (roughly 30-300);
# widened to 500 here for a coarse industrial external-aero mesh (the A4
# ladder measured mean y+ 205.72 on this exact 45,760-cell mesh with a
# different SIMPLE-family solver -- see F10_3D_VISCOUS_FAMILY.md).
AHMED_YPLUS_LOW = 30.0
AHMED_YPLUS_HIGH = 500.0
# Stationarity gate, same halves-drift discipline and 10% tolerance as
# Family 1 (openfoam-cylinder-unsteady) -- reused, not reinvented.
AHMED_DRIFT_GATE = 0.10
# Frontal area, measured directly off the STL bounding box (0.389 x 0.288 m,
# both slant STLs share the same overall envelope) -- matches
# models/curriculum/ahmed_25/reference.yaml's stated 0.112 m^2 and the A4
# ladder's own rebasing ratio.
AHMED_FRONTAL_AREA_M2 = 0.389 * 0.288
# Ahmed, Ramm & Faltin 1984, SAE 840300, as cited by
# models/curriculum/ahmed_{25,35}/reference.yaml -- the same source and the
# same +-15% tolerance band already used for this geometry's VALIDATED tier.
AHMED_REFERENCE = {
    25.0: {"cd": 0.285, "tolerance": 0.15,
          "source": "Ahmed, Ramm & Faltin 1984, SAE 840300"},
    35.0: {"cd": 0.26, "tolerance": 0.15,
          "source": "Ahmed, Ramm & Faltin 1984, SAE 840300"},
}

# Seed offset keeps this sequence stable and distinct from any other sampler.
_SEED_BASE = 90_210


# --------------------------------------------------------------------------
# Deterministic design stream — index -> design
# --------------------------------------------------------------------------

def design_for_index(index: int) -> dict[str, Any]:
    """Map an integer index to a solver + design, deterministically.

    A 12-way interleave (index % 12) holds a mix over a long run:

    - kind 0-2 (3/12): steady simpleFoam cylinder, Re ~10-45 (unchanged --
      this is the ORIGINAL, cheap, always-converges family).
    - kind 3-4 (2/12): VSPAERO wing polars (unchanged).
    - kind 5   (1/12): reduced-order valve-cycle evaluations (unchanged).
    - kind 6-8 (3/12): Family 1 -- pimpleFoam unsteady 2D vortex shedding,
      Re 100-1000 (genuinely shedding, well above the steady family's Re<=45
      cap). Validated against the Roshko/Williamson Strouhal correlation for
      Re 100-200; see PHYSICS_FAMILIES.md.
    - kind 9-10 (2/12): Family 2 -- rhoSimpleFoam transonic NACA0012, Mach
      0.7-0.85 (a real shock forms). See PHYSICS_FAMILIES.md for the shock-
      position validation.
    - kind 11  (1/12): Family F10 -- simpleFoam Ahmed body, the batch's only
      genuinely 3D viscous RANS family (k-omega SST, wall functions,
      snappyHexMesh; every other "3D" family, vspaero-wing, is an inviscid
      panel method). Geometry varies over the two validated slant angles
      (25 deg, 35 deg -- a real geometric design axis, not just a flow-
      condition sweep); Reynolds varies 1.5e6-4.0e6, inside the reference's
      stated valid band [1.0e6, 5.0e6]. See F10_3D_VISCOUS_FAMILY.md.

    The valve rows are honest reduced-order evaluations (``solver='reduced-order'``),
    NOT solves — a cycle-decomposition orifice screen, three phase points each.
    The new families cost far more per evaluation (~minutes, not seconds,
    and for F10 low-single-digit minutes -- see F10_3D_VISCOUS_FAMILY.md) than
    the original three, by design -- this is the mega-batch's deliberate
    trade of raw throughput for real physics depth.
    """
    rng = random.Random(_SEED_BASE + index)
    kind = index % 12
    if kind == 11:
        slant = 25.0 if rng.random() < 0.65 else 35.0
        reynolds = round(rng.uniform(1.5e6, 4.0e6), 0)
        return {
            "solver": AHMED_VISCOUS_3D,
            "design": {"slant_deg": slant, "reynolds": reynolds},
        }
    if kind in (6, 7, 8):
        reynolds = round(rng.uniform(100.0, 1000.0), 3)
        return {
            "solver": CYLINDER_UNSTEADY,
            "design": {"reynolds": reynolds},
        }
    if kind in (9, 10):
        mach = round(rng.uniform(0.70, 0.85), 4)
        alpha_deg = round(rng.uniform(0.0, 3.0), 3)
        reynolds = round(rng.uniform(3.0e6, 7.0e6), 0)
        return {
            "solver": TRANSONIC_AIRFOIL,
            "design": {"mach": mach, "alpha_deg": alpha_deg, "reynolds": reynolds},
        }
    if kind in (0, 1, 2):
        diameter = round(rng.uniform(0.5, 2.0), 4)
        velocity = round(rng.uniform(0.5, 2.5), 4)
        re_target = rng.uniform(10.0, 45.0)
        viscosity = round(velocity * diameter / re_target, 6)
        viscosity = min(max(viscosity, 0.01), 0.2)
        refinement = round(rng.uniform(0.6, 1.6), 3)
        return {
            "solver": CYLINDER,
            "design": {
                "cylinder_diameter": diameter,
                "inlet_velocity": velocity,
                "kinematic_viscosity": viscosity,
                "mesh_refinement": refinement,
            },
        }
    if kind in (3, 4):
        span = round(rng.uniform(20.0, 70.0), 3)
        aspect = rng.uniform(6.0, 16.0)
        area = round(span * span / aspect, 3)
        sweep = round(rng.uniform(0.0, 35.0), 2)
        taper = round(rng.uniform(0.2, 0.6), 3)
        cl_target = round(rng.uniform(0.4, 0.6), 3)
        return {
            "solver": WING,
            "design": {
                "span": span,
                "area": area,
                "sweep": sweep,
                "taper": taper,
                "cl_target": cl_target,
            },
        }
    opening_angle = round(rng.uniform(35.0, 85.0), 2)
    return {
        "solver": VALVE,
        "design": {"opening_angle_deg": opening_angle},
    }


# --------------------------------------------------------------------------
# Single-task evaluation
# --------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_cylinder(index: int, design: dict[str, float], work_root: Path) -> dict[str, Any]:
    case_dir = work_root / "cylinder" / f"case-{index:06d}"
    api = OpenFoamCylinderApi(case_dir)
    try:
        raw = api.evaluate(design, ["geometry", "aerodynamics"])
    finally:
        api.close()
    keys = (
        "Cd", "Cl", "Re", "Cd_oscillation", "convergence_residual",
        "converged", "solver_iterations", "cell_count",
    )
    metrics = {k: raw[k] for k in keys if k in raw}
    shutil.rmtree(case_dir, ignore_errors=True)
    return metrics


def _run_cylinder_unsteady(index: int, design: dict[str, float], work_root: Path) -> dict[str, Any]:
    """pimpleFoam laminar vortex shedding, Re 100-1000 -- Family 1 (unsteady 2D).

    Reuses cylinder_vortex_shedding.build_case verbatim for the mesh (O-grid
    annulus, boundary-layer-resolved, laminar) and fvSchemes/fvSolution/
    controlDict, and the exact same stationarity-gated averaging
    (time_weighted_stats / measure_period / halves_drift) that the transient
    NACA 0012 defect (commit 6606434) added -- a mean quoted over a window
    whose two halves disagree by more than 10% is refused, not reported. Runs
    directly in ``work_root``, one directory per index (no shared remote-copy
    path), so concurrent workers never collide the way cylinder_vortex_
    shedding.run_case's fixed ``cyl-re{reynolds:g}`` path could.

    The one deliberate change from the module's own demo default: the
    cross-stream perturbation that seeds the shedding instability is raised
    from 0.02 to UNSTEADY_CYLINDER_PERTURBATION (0.1) -- measured directly
    against this batch's end_time budget (0.02 left the wake still growing,
    not at its limit cycle, at t=60; 0.1 reaches stationarity and lands the
    Re=100-200 Strouhal numbers within 5% of the Roshko/Williamson curve --
    see PHYSICS_FAMILIES.md for the three validation runs).
    """
    reynolds = float(design["reynolds"])
    end_time = UNSTEADY_CYLINDER_END_TIME
    # 0.01D was tuned and validated for the Re 100-200 gate band; above it,
    # tighten the wall-normal first cell (thinner boundary layer) so the
    # mesh does not silently under-resolve the higher-Re cases.
    first_cell = 0.01 if reynolds <= 200.0 else 0.01 * (200.0 / reynolds) ** 0.5
    dt0 = 0.005 * min(1.0, 200.0 / reynolds)

    case_dir = work_root / "cylinder-unsteady" / f"case-{index:06d}"
    shutil.rmtree(case_dir, ignore_errors=True)
    case_dir.mkdir(parents=True, exist_ok=True)
    params = cvs.build_case(
        case_dir, reynolds=reynolds, farfield_diameters=15.0,
        n_radial=45, n_tangential=48, first_cell=first_cell,
        end_time=end_time, dt0=dt0,
    )
    fields = cvs.initial_fields(perturbation=UNSTEADY_CYLINDER_PERTURBATION)
    (case_dir / "0" / "U").write_text(fields["U"])

    timings: dict[str, float] = {}
    for step, args in (("blockMesh", ["blockMesh"]),
                       ("checkMesh", ["checkMesh", "-allTopology", "-allGeometry"])):
        start = time.time()
        result = cvs._foam(args, case_dir, f"log.{step}", timeout=300)
        timings[step] = round(time.time() - start, 1)
        if step == "blockMesh" and result.returncode != 0:
            raise RuntimeError(f"cylinder-unsteady #{index}: blockMesh failed")

    start = time.time()
    result = cvs._foam(["pimpleFoam"], case_dir, "log.pimpleFoam", timeout=900)
    timings["pimpleFoam"] = round(time.time() - start, 1)
    if result.returncode != 0:
        tail = (case_dir / "log.pimpleFoam").read_text(errors="replace")
        raise RuntimeError(f"cylinder-unsteady #{index}: pimpleFoam failed:\n"
                           + "\n".join(tail.splitlines()[-20:]))

    coeff_files = sorted((case_dir / "postProcessing").rglob("coefficient*.dat"))
    if not coeff_files:
        raise RuntimeError(f"cylinder-unsteady #{index}: no forceCoeffs output")
    history = parse_coefficient_history(coeff_files[-1].read_text(errors="replace"))
    times = history.get("Time", [])
    t_start = 0.5 * end_time
    cd_stats = cvs.time_weighted_stats(times, history["Cd"], t_start)
    cl_stats = cvs.time_weighted_stats(times, history["Cl"], t_start)
    period = cvs.measure_period(times, history["Cl"], t_start)
    if cd_stats is None or cl_stats is None:
        raise RuntimeError(f"cylinder-unsteady #{index}: averaging window empty "
                           f"(ran to t={times[-1] if times else 0:g})")
    drift = cvs.halves_drift(times, history["Cd"], cd_stats["window_start"], cd_stats["window_end"])
    if drift is None:
        raise RuntimeError(f"cylinder-unsteady #{index}: halves_drift undefined, "
                           f"stationarity unknown, Cd/St refused")
    if drift["relative_drift"] > 0.10:
        raise RuntimeError(
            f"cylinder-unsteady #{index}: Cd still drifting across the averaging "
            f"window ({100 * drift['relative_drift']:.1f}% relative drift). "
            f"Not a stationary time-average, Cd/St refused")
    strouhal = (cvs.DIAMETER / (period * cvs.U_INF)) if period else None
    st_ref = 0.198 * (1.0 - 19.7 / reynolds) if 50.0 <= reynolds <= 200.0 else None
    st_dev_pct = (100.0 * abs(strouhal - st_ref) / st_ref
                 if (strouhal and st_ref) else None)
    metrics = {
        "reynolds": reynolds, "cells": params["n_radial"] * params["n_tangential"] * 4,
        "end_time_cap": end_time, "perturbation": UNSTEADY_CYLINDER_PERTURBATION,
        "steps": len(times),
        "cd_mean": cd_stats["mean"], "cd_band": cd_stats["band"],
        "cd_relative_drift": drift["relative_drift"],
        "cl_mean": cl_stats["mean"], "cl_band": cl_stats["band"],
        "period": period, "strouhal": strouhal,
        "strouhal_roshko_ref": st_ref, "strouhal_deviation_pct": st_dev_pct,
    }
    shutil.rmtree(case_dir, ignore_errors=True)
    return metrics


def _run_transonic_airfoil(index: int, design: dict[str, float], work_root: Path) -> dict[str, Any]:
    """rhoSimpleFoam NACA0012, Mach 0.7-0.85 -- Family 2 (transonic).

    See ``workflows.transonic_airfoil`` for the mesh, solver setup, and the
    documented validation approach (shock position vs. the classical M=0.8/
    alpha=1.25 deg inviscid two-shock benchmark). Iteration count is fixed
    and bounded (TRANSONIC_ITERATIONS); the case directory is removed after
    the ledger metrics are extracted, same as every other family.
    """
    case_dir = work_root / "transonic-naca0012" / f"case-{index:06d}"
    record = ta.run_case(
        mach=float(design["mach"]), alpha_deg=float(design["alpha_deg"]),
        reynolds=float(design["reynolds"]), work_dir=case_dir,
        iterations=TRANSONIC_ITERATIONS, timeout=900,
    )
    shutil.rmtree(case_dir, ignore_errors=True)
    return record


def _run_wing(index: int, design: dict[str, float], work_root: Path) -> dict[str, Any]:
    api = VspAeroWingApi(work_root / "wing")
    raw = api.evaluate(design)
    matched = raw.get("matched", {}) or {}
    built = raw.get("built", {}) or {}
    cdi = matched.get("cdi")
    cdo = matched.get("cdo_wing")
    cl = matched.get("cl")
    cd_total = None
    if cdi is not None and cdo is not None:
        cd_total = cdi + cdo
    l_over_d = (cl / cd_total) if (cl is not None and cd_total) else None
    metrics = {
        "cl": cl,
        "cdi": cdi,
        "cdo_wing": cdo,
        "cd_total": cd_total,
        "L_D": l_over_d,
        "alpha": matched.get("alpha"),
        "span_efficiency": matched.get("span_efficiency"),
        "extrapolated": matched.get("extrapolated"),
        "built_span": built.get("span"),
        "built_area": built.get("area"),
    }
    case_dir = raw.get("case_dir")
    if case_dir:
        shutil.rmtree(case_dir, ignore_errors=True)
    return metrics


_RESIDUAL_RE = re.compile(r"Solving for (\w+),.*Final residual = ([0-9.eE+-]+)")
_CHECKMESH_CELLS_RE = re.compile(r"cells:\s+(\d+)")
_CHECKMESH_NONORTHO_RE = re.compile(
    r"non-orthogonality Max:\s*([0-9.]+)|Max non-orthogonality =\s*([0-9.]+)")
_CHECKMESH_SKEW_RE = re.compile(r"Max skewness =\s*([0-9.]+)")


def _ahmed_final_residuals(text: str) -> dict[str, float]:
    """Final residual per solved field from the last occurrence in the log."""
    residuals: dict[str, float] = {}
    for line in text.splitlines():
        match = _RESIDUAL_RE.search(line)
        if match:
            residuals[match.group(1)] = float(match.group(2))
    return residuals


def _ahmed_checkmesh_stats(text: str) -> dict[str, Any]:
    """checkMesh verdict, cell count, non-orthogonality, skewness -- the
    exact fields the F10 mesh gate checks, parsed with the same regexes
    chief_engineer.head_engineer.HeadEngineer.collect_mesh_stats uses."""
    stats: dict[str, Any] = {"mesh_ok": "Mesh OK" in text}
    cells = _CHECKMESH_CELLS_RE.search(text)
    if cells:
        stats["cells"] = int(cells.group(1))
    nonortho = _CHECKMESH_NONORTHO_RE.search(text)
    if nonortho:
        stats["max_non_orthogonality"] = float(nonortho.group(1) or nonortho.group(2))
    skew = _CHECKMESH_SKEW_RE.search(text)
    if skew:
        stats["max_skewness"] = float(skew.group(1))
    return stats


def _ahmed_add_yplus_function(control_dict_path: Path) -> None:
    """Append a yPlus function object to a controlDict ``build_case`` wrote.

    ``external_aero.build_case`` writes only ``forceCoeffs1`` -- no family
    upstream of F10 needed a y+ gate, because none of them is a wall-bounded
    3D viscous solve. The block below matches the yPlus function object
    ``workflows/tmr_verification.py`` already uses elsewhere in this repo
    (onEnd only: the gate only needs the converged, final value).
    """
    text = control_dict_path.read_text()
    marker = "    }\n}\n"
    if not text.endswith(marker):
        raise RuntimeError(
            "ahmed-viscous: controlDict layout changed, cannot append yPlus "
            "function object safely")
    yplus_block = (
        "    }\n\n    yPlus1\n    {\n"
        "        type            yPlus;\n"
        "        libs            (\"libfieldFunctionObjects.so\");\n"
        "        executeControl  onEnd;\n"
        "        writeControl    onEnd;\n"
        "    }\n}\n"
    )
    control_dict_path.write_text(text[: -len(marker)] + yplus_block)


def _latest_yplus(post_root: Path, patch: str) -> tuple[dict, float, str] | None:
    """The y+ state chosen by the Time written INSIDE the file, never by
    glob order or by directory name.

    This is the bump collector's repair applied to this reader (docket item
    w1-yplus-restart-rename-blindness-in-the-batch-gate). Three traps, all
    measured on the bump ladder before this existed here:

    1. postProcessing time directories are named for a run's START time, so
       sorting directory names does not sort states.
    2. OpenFOAM renames a function object's output to ``<name>_<time>.dat``
       when the file already exists on a restart -- exactly as it does for
       coefficient.dat, which the coefficient read above already survives by
       globbing ``coefficient*.dat``. A bare ``yPlus.dat`` glob then reads a
       header-only leftover or a stale first-run state.
    3. Keeping the last parse of an arbitrary iteration order lets the
       filesystem decide which state is reported.

    So: glob ``yPlus*.dat``, parse every candidate, and select by the
    largest Time stamp any data row carries. Returns (parsed y+ dict,
    that Time, source path relative to post_root) or None if nothing
    parseable exists. In this batch every attempt starts from a wiped case
    directory, so the renamed layout cannot arise from the runner itself
    (measured: zero renamed files across every surviving case, zero retried
    Ahmed indices in the ledger); this read stops being wrong the day that
    invariant slips rather than the day somebody notices.
    """
    best: tuple[float, dict, Path] | None = None
    for path in sorted(post_root.rglob("yPlus*.dat")):
        text = path.read_text(errors="replace")
        parsed = parse_yplus_dat(text, patch=patch)
        if not parsed:
            continue
        stamps = []
        for line in text.splitlines():
            parts = line.split()
            if not parts or parts[0].startswith("#"):
                continue
            try:
                stamps.append(float(parts[0]))
            except ValueError:
                continue
        if not stamps:
            continue
        stamp = max(stamps)
        if best is None or stamp > best[0]:
            best = (stamp, parsed, path)
    if best is None:
        return None
    return best[1], best[0], best[2].relative_to(post_root).as_posix()


def _ahmed_refinement_for_reynolds(reynolds: float) -> int:
    """Mesh refinement level, following Reynolds number -- see F10_YPLUS_FIX.md.

    A single fixed-refinement mesh cannot support the whole F10 design
    space: the first cell's absolute height is set by the mesh alone, but
    wall shear (and therefore y+ at that fixed height) grows with Re, so a
    mesh sized for the bottom of the range overshoots the [30, 500]
    wall-function band at the top. Rather than widen the gate, the mesh
    itself now follows Re: refinement=2 (the original, validated recipe)
    below the measured threshold, refinement=3 at/above it. Both branches
    are measured, not assumed -- see F10_YPLUS_FIX.md for the four
    real-dispatch data points this threshold is set from.
    """
    if reynolds >= AHMED_REFINEMENT_RE_THRESHOLD:
        return AHMED_REFINEMENT_HIGH_RE
    return AHMED_REFINEMENT


def _run_ahmed_viscous(index: int, design: dict[str, float], work_root: Path) -> dict[str, Any]:
    """Ahmed body, simpleFoam, k-omega SST wall functions -- Family F10.

    Reuses ``chief_engineer.external_aero.analyse_surface`` / ``build_case``
    verbatim (the same case-writer ``workflows/geometry_study.py`` used to
    build the already-VALIDATED ``mission-output/geometry-study/study-
    ahmed_25`` case: 45,753 cells, Cd 0.3219 vs Ahmed/Ramm/Faltin 1984 SAE
    840300's 0.285, +-15% band) -- this is a promotion of that existing body
    into the batch, not a rebuild. ``refinement=2`` and ``iterations=250``
    are read directly off that case's own stored snappyHexMeshDict/
    controlDict, not re-derived.

    Unlike every family above it, this one solves a real snappyHexMesh
    surface mesh and a full 3D k-omega SST field -- the batch's only
    genuinely 3D VISCOUS RANS family (vspaero-wing is an inviscid vortex-
    lattice panel method: no boundary layer, no Reynolds number). Every
    evaluation is gated on four measured, non-negotiable checks -- mesh
    quality (checkMesh), y+ band, residual convergence, and force-
    coefficient stationarity -- any one of which failing raises, so the row
    lands in the ledger as ok=False with a stated reason, never silently
    kept. See F10_3D_VISCOUS_FAMILY.md for the measured per-evaluation cost
    and the family-level validation gate result.
    """
    slant = float(design["slant_deg"])
    reynolds = float(design["reynolds"])
    stl_name = f"ahmed_{int(slant)}.stl"
    source = AHMED_GEOMETRY_DIR / stl_name
    if not source.exists():
        raise RuntimeError(f"ahmed-viscous #{index}: missing geometry {source}")

    geometry = analyse_surface(source, streamwise_axis=0)
    velocity = reynolds * AHMED_VISCOSITY / geometry["length"]
    refinement = _ahmed_refinement_for_reynolds(reynolds)

    case_dir = work_root / "ahmed-viscous" / f"case-{index:06d}"
    shutil.rmtree(case_dir, ignore_errors=True)
    (case_dir / "constant" / "triSurface").mkdir(parents=True, exist_ok=True)
    shutil.copy(source, case_dir / "constant" / "triSurface" / stl_name)

    build_case(case_dir, stl_name, geometry, velocity=velocity,
              viscosity=AHMED_VISCOSITY, scale=1.0, refinement=refinement,
              iterations=AHMED_ITERATIONS)
    _ahmed_add_yplus_function(case_dir / "system" / "controlDict")

    timings: dict[str, float] = {}
    for step, args in (("surfaceFeatureExtract", ["surfaceFeatureExtract"]),
                       ("blockMesh", ["blockMesh"]),
                       ("snappyHexMesh", ["snappyHexMesh", "-overwrite"])):
        start = time.time()
        result = _foam(args, case_dir, f"log.{step}", timeout=900)
        timings[step] = round(time.time() - start, 1)
        if result.returncode != 0:
            raise RuntimeError(f"ahmed-viscous #{index}: {step} failed")

    # ---- Gate 1: mesh quality (checkMesh) ----
    start = time.time()
    _foam(["checkMesh"], case_dir, "log.checkMesh", timeout=300)
    timings["checkMesh"] = round(time.time() - start, 1)
    mesh_stats = _ahmed_checkmesh_stats((case_dir / "log.checkMesh").read_text(errors="replace"))
    non_ortho = mesh_stats.get("max_non_orthogonality")
    skew = mesh_stats.get("max_skewness")
    mesh_gate_pass = (
        mesh_stats.get("mesh_ok", False)
        and (non_ortho is None or non_ortho <= AHMED_NON_ORTHO_GATE)
        and (skew is None or skew <= AHMED_SKEWNESS_GATE)
    )
    if not mesh_gate_pass:
        raise RuntimeError(
            f"ahmed-viscous #{index}: MESH GATE FAILED, checkMesh_ok="
            f"{mesh_stats.get('mesh_ok')}, non_ortho={non_ortho}, skew={skew} "
            f"(gates: non_ortho<={AHMED_NON_ORTHO_GATE}, skew<={AHMED_SKEWNESS_GATE})")

    # potentialFoam seeds a better initial field for simpleFoam (matches the
    # validated recipe's own step); it is an initialization aid, not gated --
    # a poor potential-flow start still lets simpleFoam converge, just slower.
    start = time.time()
    _foam(["potentialFoam", "-writephi"], case_dir, "log.potentialFoam", timeout=300)
    timings["potentialFoam"] = round(time.time() - start, 1)

    start = time.time()
    result = _foam(["simpleFoam"], case_dir, "log.simpleFoam", timeout=1800)
    timings["simpleFoam"] = round(time.time() - start, 1)
    log_text = (case_dir / "log.simpleFoam").read_text(errors="replace")
    if result.returncode != 0:
        raise RuntimeError(
            f"ahmed-viscous #{index}: simpleFoam failed:\n"
            + "\n".join(log_text.splitlines()[-20:]))

    # ---- Gate 2: convergence residual reached ----
    residuals = _ahmed_final_residuals(log_text)
    tracked = [residuals[k] for k in ("Ux", "Uy", "Uz", "p") if k in residuals]
    residual_max = max(tracked) if len(tracked) == 4 else None
    if residual_max is None or residual_max > AHMED_RESIDUAL_GATE:
        raise RuntimeError(
            f"ahmed-viscous #{index}: RESIDUAL GATE FAILED, "
            f"max(Ux,Uy,Uz,p) final residual {residual_max} > {AHMED_RESIDUAL_GATE} "
            f"(residuals seen: {residuals})")

    # ---- Gate 3: force-coefficient stationarity ----
    coeff_files = sorted((case_dir / "postProcessing").rglob("coefficient*.dat"))
    if not coeff_files:
        raise RuntimeError(f"ahmed-viscous #{index}: no forceCoeffs output")
    history = parse_coefficient_history(coeff_files[-1].read_text(errors="replace"))
    times = history.get("Time", [])
    cd_series = history.get("Cd", [])
    if not times or not cd_series:
        raise RuntimeError(f"ahmed-viscous #{index}: empty force-coefficient history")
    window_iters = min(len(times), 50)
    window_start = times[-window_iters]
    drift = cvs.halves_drift(times, cd_series, window_start, times[-1])
    if drift is None:
        raise RuntimeError(
            f"ahmed-viscous #{index}: halves_drift undefined, stationarity "
            f"unknown, Cd refused")
    if drift["relative_drift"] > AHMED_DRIFT_GATE:
        raise RuntimeError(
            f"ahmed-viscous #{index}: STATIONARITY GATE FAILED, Cd drifting "
            f"{100 * drift['relative_drift']:.1f}% across the final "
            f"{window_iters}-iteration window (limit {100 * AHMED_DRIFT_GATE:.0f}%)")
    cd_stats = cvs.time_weighted_stats(times, cd_series, window_start)
    cl_series = history.get("Cl")
    cl_stats = (cvs.time_weighted_stats(times, cl_series, window_start)
               if cl_series else None)

    # ---- Gate 4: y+ range achieved ----
    # Selected by the Time inside the file across yPlus*.dat, never by a
    # bare-filename glob whose last match a restart rename can leave stale
    # or header-only (see _latest_yplus).
    yplus_hit = _latest_yplus(case_dir / "postProcessing", patch="body")
    yplus = yplus_hit[0] if yplus_hit else None
    yplus_gate_pass = yplus is not None and AHMED_YPLUS_LOW <= yplus["average"] <= AHMED_YPLUS_HIGH
    if not yplus_gate_pass:
        raise RuntimeError(
            f"ahmed-viscous #{index}: Y+ GATE FAILED, {yplus} not inside "
            f"[{AHMED_YPLUS_LOW}, {AHMED_YPLUS_HIGH}] (wall-function log-law band)")

    # Every gate passed: extract metrics, including an *informational* (not
    # gating) comparison against the citable experimental reference -- the
    # family's validation gate is that AT LEAST ONE design point reproduces
    # it (see F10_3D_VISCOUS_FAMILY.md), not that every row must.
    cd_planform = cd_stats["mean"]
    rebase_ratio = geometry["planform_area"] / AHMED_FRONTAL_AREA_M2
    cd_frontal = cd_planform * rebase_ratio
    ref = AHMED_REFERENCE.get(slant)
    rel_error = abs(cd_frontal - ref["cd"]) / ref["cd"] if ref else None

    metrics = {
        "slant_deg": slant,
        "reynolds": reynolds,
        "velocity": round(velocity, 3),
        "mesh_refinement": refinement,
        "cells": mesh_stats.get("cells"),
        "checkmesh_ok": mesh_stats.get("mesh_ok"),
        "max_non_orthogonality": non_ortho,
        "max_skewness": skew,
        "yplus_min": yplus["min"],
        "yplus_max": yplus["max"],
        "yplus_avg": yplus["average"],
        # So a reader can check the y+ is the state the Cd beside it came
        # from (the bump collector records the same pair of facts).
        "yplus_time": yplus_hit[1],
        "yplus_source": yplus_hit[2],
        "residual_max_UUUp": residual_max,
        "residuals": residuals,
        "solver_iterations": times[-1],
        "cd_relative_drift": drift["relative_drift"],
        "cd_planform_area_basis": round(cd_planform, 5),
        "cl_planform_area_basis": round(cl_stats["mean"], 5) if cl_stats else None,
        "planform_area_m2": round(geometry["planform_area"], 6),
        "cd_frontal_area_basis": round(cd_frontal, 5),
        "reference_cd_frontal": ref["cd"] if ref else None,
        "reference_source": ref["source"] if ref else None,
        "relative_error_vs_reference": round(rel_error, 4) if rel_error is not None else None,
        "validated_tier": bool(rel_error is not None and rel_error <= ref["tolerance"]),
        "timings_s": timings,
    }
    shutil.rmtree(case_dir, ignore_errors=True)
    return metrics


def _run_valve(index: int, design: dict[str, float]) -> dict[str, Any]:
    """Reduced-order valve-cycle evaluation — NOT a solve; labelled as such.

    One opening angle, decomposed into the k=3 systolic phase points, each
    passed through the transparent orifice pressure-loss model, then
    cycle-weighted with a deterministic Monte-Carlo input envelope. This reuses
    the exact ROM the Act 3 valve workflow ships, so the numbers are consistent.
    """
    from workflows import valve_study as vs  # lazy: it edits sys.path on import

    angle = float(design["opening_angle_deg"])
    phases = vs.phase_points()
    area = vs.effective_orifice_area(angle)
    weighted = vs._cycle_weighted_loss(angle, phases)
    mean, two_sigma = vs._mc_envelope(angle, phases)
    alpha = vs.womersley(vs.ROOT_RADIUS)
    return {
        "cycle_weighted_loss_Pa": round(weighted, 3),
        "loss_mean_Pa": round(mean, 3),
        "loss_envelope_2sigma_Pa": round(two_sigma, 3),
        "orifice_area_mm2": round(area * 1e6, 2),
        "womersley_alpha": round(alpha, 3),
        "feasible": area >= vs.MIN_ORIFICE_AREA,
        "phase_points": len(phases),
    }


def run_task(index: int, work_root: Path) -> dict[str, Any]:
    """Evaluate one design; never raises — failures come back as ok=False rows."""
    spec = design_for_index(index)
    solver = spec["solver"]
    design = spec["design"]
    # Cylinder and wing are real solves; the valve row is an honest
    # reduced-order (ROM) evaluation — labelled distinctly, never as a solve.
    label = "reduced-order-eval" if solver == VALVE else "real-solve"
    start = time.time()
    record: dict[str, Any] = {
        "index": index,
        "solver": solver,
        "label": label,
        "design": design,
        "timestamp": _now_iso(),
    }
    try:
        if solver == CYLINDER:
            metrics = _run_cylinder(index, design, work_root)
        elif solver == WING:
            metrics = _run_wing(index, design, work_root)
        elif solver == CYLINDER_UNSTEADY:
            metrics = _run_cylinder_unsteady(index, design, work_root)
        elif solver == TRANSONIC_AIRFOIL:
            metrics = _run_transonic_airfoil(index, design, work_root)
        elif solver == AHMED_VISCOUS_3D:
            metrics = _run_ahmed_viscous(index, design, work_root)
        else:
            metrics = _run_valve(index, design)
        record["metrics"] = metrics
        record["ok"] = True
    except Exception as exc:  # a poison design must not sink the batch
        record["metrics"] = {}
        record["ok"] = False
        record["error"] = f"{type(exc).__name__}: {exc}"
    record["wall_seconds"] = round(time.time() - start, 3)
    # Monitor Standard S9. A run whose wall time is a large multiple of the
    # learned envelope for its solver kind keeps that finding as a named field
    # on its own row, so fleet learning can separate genuine solver cost from
    # infrastructure stalls instead of averaging the two together. An ordinary
    # row carries no such field at all, and no existing field is ever altered.
    excursion = wall_time_record_field(solver, record["wall_seconds"])
    if excursion:
        record[WALL_TIME_FIELD] = excursion
    return record


# --------------------------------------------------------------------------
# Ledger I/O (durable append + resume)
# --------------------------------------------------------------------------

_LEDGER_LOCK = threading.Lock()


def append_ledger(ledger_path: Path, record: dict[str, Any]) -> None:
    """Append one record as a JSON line, flushed and fsync'd for crash safety."""
    line = json.dumps(record, ensure_ascii=False)
    with _LEDGER_LOCK:
        with ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
            handle.flush()
            os.fsync(handle.fileno())


def load_done_indices(ledger_path: Path) -> set[int]:
    """Indices already attempted (ok or not) — the resume set."""
    done: set[int] = set()
    if not ledger_path.exists():
        return done
    for line in ledger_path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
            done.add(int(record["index"]))
        except Exception:
            continue
    return done


# --------------------------------------------------------------------------
# Learning pass — every batch is a learning opportunity
# --------------------------------------------------------------------------

# Refresh the distilled learned study after this many completions in-session,
# and always once more when the session ends. Cheap (one ledger read), and a
# failure here must never sink the batch itself.
LEARN_EVERY = 500


def distill_learning(ledger_path: Path, log=print) -> None:
    """Distill the ledger into the learned study; never raises."""
    try:
        from chief_engineer.ledger_learning import distill_to_file
        study = distill_to_file(ledger_path)
        log(
            f"[mega-batch] learning refreshed: "
            f"{study['provenance']['row_count']} ledger rows distilled"
        )
    except Exception as exc:  # learning is best-effort, the batch is not
        log(f"[mega-batch] learning pass skipped: {type(exc).__name__}: {exc}")


# --------------------------------------------------------------------------
# Resource guards
# --------------------------------------------------------------------------
#
# Added after the 2026-07-27 outage. The instance went unreachable at ~05:12:56
# UTC while two DAFoam adjoint containers and this batch shared 30 GB of RAM
# with no swap; the last sysstat sample (05:10:03) recorded 460 MB free and
# committed memory at 112.90% of RAM. There was no OOM kill and no disk
# exhaustion in the logs -- the box livelocked in reclaim before the OOM killer
# could act. These guards stop the batch cleanly while headroom still exists,
# rather than letting it participate in a second such livelock.

RESOURCE_CHECK_SECONDS = 10.0


def free_disk_gb(path: Path) -> float:
    """GiB free on the filesystem holding ``path``."""
    return shutil.disk_usage(path).free / (1024 ** 3)


def available_mem_gb() -> float:
    """GiB of MemAvailable, the kernel's own estimate of allocatable memory.

    Returns ``inf`` if /proc/meminfo is unreadable, so a parsing problem can
    never stop a healthy batch.
    """
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                return float(line.split()[1]) / (1024 ** 2)
    except Exception:
        pass
    return float("inf")


# --------------------------------------------------------------------------
# Continuous run loop
# --------------------------------------------------------------------------

def run_batch(
    ledger_path: Path,
    work_root: Path,
    *,
    workers: int = 4,
    max_tasks: int | None = None,
    max_seconds: float | None = None,
    stop_file: Path | None = None,
    min_free_disk_gb: float = 20.0,
    min_avail_mem_gb: float = 2.0,
    log=print,
) -> dict[str, int]:
    """Stream designs through ``workers`` slots, appending each result.

    Stops when any of the bounds is hit: ``max_tasks`` completed *this session*,
    ``max_seconds`` elapsed, ``stop_file`` appears, free disk falls below
    ``min_free_disk_gb``, or available memory falls below ``min_avail_mem_gb``.
    Resumes from the ledger.
    """
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    (work_root / "cylinder").mkdir(parents=True, exist_ok=True)
    (work_root / "wing").mkdir(parents=True, exist_ok=True)
    (work_root / "cylinder-unsteady").mkdir(parents=True, exist_ok=True)
    (work_root / "transonic-naca0012").mkdir(parents=True, exist_ok=True)
    (work_root / "ahmed-viscous").mkdir(parents=True, exist_ok=True)

    done = load_done_indices(ledger_path)
    log(f"[mega-batch] resuming: {len(done)} indices already in ledger")
    log(
        f"[mega-batch] baseline: workers={workers} "
        f"free_disk={free_disk_gb(work_root):.1f} GB "
        f"avail_mem={available_mem_gb():.1f} GB; "
        f"guards stop at disk<{min_free_disk_gb:.1f} GB, mem<{min_avail_mem_gb:.1f} GB"
    )

    start = time.time()
    next_index = 0
    submitted_this_session = 0
    completed_this_session = 0
    stats = {"ok": 0, "failed": 0, CYLINDER: 0, WING: 0}

    # Resource guards are sampled at most once every RESOURCE_CHECK_SECONDS so
    # the tight submit loop does not spam syscalls. ``guard_trip`` latches: once
    # a guard fires the batch stops for good this session and the reason is
    # reported at the end, so a stop is never silent.
    guard_state = {"last_check": 0.0, "trip": None}

    def resource_guard_tripped() -> str | None:
        if guard_state["trip"] is not None:
            return guard_state["trip"]
        now = time.time()
        if now - guard_state["last_check"] < RESOURCE_CHECK_SECONDS:
            return None
        guard_state["last_check"] = now
        disk = free_disk_gb(work_root)
        if disk < min_free_disk_gb:
            guard_state["trip"] = (
                f"free disk {disk:.1f} GB below the {min_free_disk_gb:.1f} GB floor"
            )
            log(f"[mega-batch] RESOURCE GUARD: {guard_state['trip']}, draining and stopping")
            return guard_state["trip"]
        mem = available_mem_gb()
        if mem < min_avail_mem_gb:
            guard_state["trip"] = (
                f"available memory {mem:.1f} GB below the {min_avail_mem_gb:.1f} GB floor"
            )
            log(f"[mega-batch] RESOURCE GUARD: {guard_state['trip']}, draining and stopping")
            return guard_state["trip"]
        return None

    def should_stop() -> bool:
        if stop_file is not None and stop_file.exists():
            return True
        if max_seconds is not None and (time.time() - start) >= max_seconds:
            return True
        if max_tasks is not None and submitted_this_session >= max_tasks:
            return True
        tripped = resource_guard_tripped()
        if tripped is not None:
            return True
        return False

    def claim_next() -> int:
        nonlocal next_index
        while next_index in done:
            next_index += 1
        index = next_index
        next_index += 1
        done.add(index)
        return index

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        inflight: dict[Any, int] = {}
        while True:
            while len(inflight) < workers and not should_stop():
                index = claim_next()
                inflight[pool.submit(run_task, index, work_root)] = index
                submitted_this_session += 1
            if not inflight:
                break
            finished, _ = wait(inflight, timeout=5.0, return_when=FIRST_COMPLETED)
            for future in finished:
                index = inflight.pop(future)
                record = future.result()
                append_ledger(ledger_path, record)
                completed_this_session += 1
                stats[record["solver"]] = stats.get(record["solver"], 0) + 1
                if record.get("ok"):
                    stats["ok"] += 1
                    log(
                        f"[mega-batch] #{index} {record['solver']} ok "
                        f"{record['wall_seconds']}s "
                        f"(session {completed_this_session})"
                    )
                else:
                    stats["failed"] += 1
                    log(f"[mega-batch] #{index} {record['solver']} FAILED: {record.get('error')}")
                if completed_this_session % LEARN_EVERY == 0:
                    distill_learning(ledger_path, log=log)
            if should_stop() and not inflight:
                break

    # Every batch is a learning opportunity: distill the ledger into the
    # learned study at session end (best-effort, never fatal).
    distill_learning(ledger_path, log=log)

    total = len(load_done_indices(ledger_path))
    reason = guard_state["trip"]
    log(
        f"[mega-batch] session done: completed {completed_this_session} "
        f"(ok {stats['ok']}, failed {stats['failed']}); ledger total {total}"
        + (f"; STOPPED BY RESOURCE GUARD: {reason}" if reason else "")
    )
    stats["ledger_total"] = total
    stats["session_completed"] = completed_this_session
    stats["guard_trip"] = reason
    return stats


# --------------------------------------------------------------------------
# Single-instance lock
# --------------------------------------------------------------------------
#
# Added 2026-07-27 after an audit of the ledger found 55 duplicated indices in
# 186,838-186,893, every pair written between 05:11:15 and 05:12:52 on
# 2026-07-27 -- BEFORE the outage, not across the restart. ``claim_next`` runs
# on one thread and adds to ``done`` the moment it hands an index out, so a
# single session physically cannot emit the same index twice. Two sessions can.
# ``runner.pid`` was dated 05:11 and held PID 2303296, so a second runner was
# launched while the 03:21 runner was still alive, and both appended for the
# ~100 s until the box died.
#
# This is the same failure mode as the historical 1,168-duplicate episode in
# 59,899-61,068. The ledger is append-only and the distiller de-duplicates
# prefer-ok, so no measurement is lost -- but the distinct-evaluation count is
# corrupted every time it happens. Refusing the second launch is the fix.

def _pid_is_live_runner(pid: int) -> bool:
    """True if ``pid`` is alive AND looks like another mega-batch runner.

    Checked against the cmdline so a recycled PID belonging to some unrelated
    process can never block a legitimate start.
    """
    try:
        cmdline = Path(f"/proc/{pid}/cmdline").read_bytes().decode("utf-8", "replace")
    except (FileNotFoundError, ProcessLookupError, PermissionError):
        return False
    return "mega_batch" in cmdline


def acquire_runner_lock(pid_file: Path, *, force: bool = False, log=print) -> bool:
    """Claim ``pid_file`` for this process. False means refuse to start."""
    if pid_file.exists():
        try:
            existing = int(pid_file.read_text().strip())
        except (ValueError, OSError):
            existing = None
        if existing is not None and existing != os.getpid() and _pid_is_live_runner(existing):
            if not force:
                log(
                    f"[mega-batch] REFUSING TO START: another runner is live at PID "
                    f"{existing} (per {pid_file}). Two concurrent runners duplicate "
                    f"ledger indices. This exact mistake corrupted 55 rows on "
                    f"2026-07-27. Stop it first, or pass --force if you are certain."
                )
                return False
            log(f"[mega-batch] --force given; starting alongside live PID {existing}")
    pid_file.parent.mkdir(parents=True, exist_ok=True)
    pid_file.write_text(str(os.getpid()))
    return True


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _default_paths() -> tuple[Path, Path]:
    # demo-output/website/mega-batch/ledger.jsonl relative to repo root.
    repo_root = _SDK_ROOT.parent
    ledger = lab_paths.MEGA_BATCH / "ledger.jsonl"
    work_root = lab_paths.MEGA_BATCH / "work"
    return ledger, work_root


def main(argv: list[str] | None = None) -> int:
    ledger_default, work_default = _default_paths()
    parser = argparse.ArgumentParser(description="Continuous real-solver mega-batch.")
    parser.add_argument("--ledger", type=Path, default=ledger_default)
    parser.add_argument("--work-root", type=Path, default=work_default)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--max-tasks", type=int, default=None,
                        help="stop after N tasks submitted this session")
    parser.add_argument("--max-seconds", type=float, default=None,
                        help="stop after N seconds of wall time")
    parser.add_argument("--stop-file", type=Path, default=None,
                        help="stop gracefully when this file appears")
    parser.add_argument("--min-free-disk-gb", type=float, default=20.0,
                        help="stop gracefully when free disk falls below this (GiB)")
    parser.add_argument("--min-avail-mem-gb", type=float, default=2.0,
                        help="stop gracefully when available memory falls below this (GiB)")
    parser.add_argument("--pid-file", type=Path, default=None,
                        help="single-instance lock file (default: runner.pid beside the ledger)")
    parser.add_argument("--force", action="store_true",
                        help="start even if another live runner holds the pid file")
    args = parser.parse_args(argv)

    pid_file = args.pid_file
    if pid_file is None:
        pid_file = args.ledger.parent / "runner.pid"
    if not acquire_runner_lock(pid_file.resolve(), force=args.force):
        return 1

    stop_file = args.stop_file
    if stop_file is None:
        stop_file = args.ledger.parent / "STOP"

    run_batch(
        args.ledger.resolve(),
        args.work_root.resolve(),
        workers=args.workers,
        max_tasks=args.max_tasks,
        max_seconds=args.max_seconds,
        stop_file=stop_file,
        min_free_disk_gb=args.min_free_disk_gb,
        min_avail_mem_gb=args.min_avail_mem_gb,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
