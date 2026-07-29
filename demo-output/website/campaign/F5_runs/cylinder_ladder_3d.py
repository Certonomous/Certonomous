#!/usr/bin/env python3
"""F5a Re=1000 rung, 3D: the same cylinder, the same Reynolds number, the
same in-plane (x-y) O-grid mesh as the established 2D laminar Re=1000 rung
(``re1000``, 80 radial x 70 tangential x 4 blocks = 22,400 cells, first cell
0.00447D, farfield 20D) -- with ONE new variable added: a spanwise extent
long enough to admit the mode-B instability, resolved with real cells and a
periodic (cyclic) spanwise boundary, instead of the ``empty``-patch
pseudo-3D slab every other rung on this ladder uses.

Why this exists: the Re=1000 gate in F5a_cylinder_reynolds_ladder.md is an
ATTRIBUTION -- "our 2D numbers are high by the amount 2D is documented to be
high, therefore the gap is dimensionality, not solver error" -- backed by
Jiang & Cheng (2017)'s own 2D-vs-3D DNS at this exact Re. This module runs
the SAME solver, SAME Re, SAME in-plane mesh, in 3D, and gates it against
the 3D branch of the SAME reference (Jiang & Cheng's refined 3D mesh: St
0.2105, Cd 1.0138, Cl_rms 0.1191, cross-checked by Papaioannou, Tong,
Williamson & Brown, Norberg). If it lands in that family, the attribution
is demonstrated, not just argued.

Design constants are pulled directly from Jiang & Cheng (2017), J. Fluid
Mech. 832:170-188, Table 1 (mesh) and Table 3 (their OWN 3D mesh-dependence
study at Re=1000 -- fetched and read as part of this task, not
web-search-summarised):

  Spanwise domain length Lz/D:
    - Mode A (spanwise wavelength ~4D) is the dominant 3D structure only
      below Re~270 and needs Lz > 10D to avoid confinement (their Sec. 5).
    - Mode B (spanwise wavelength < 1D) is the ONLY wake mode above Re~270,
      so Re=1000 is deep in mode-B territory and does not need Mode-A's
      large domain.
    - Jiang & Cheng's own 3D mesh-dependence study at Re=1000 (their Table
      3, cases 1 vs 2) tested Lz/D=6 against Lz/D=12 and found the two
      "very close" (St 0.2105 vs 0.2098, Cd 1.0138 vs 1.0104, Cl_rms 0.1191
      vs 0.1063 -- the largest move, ~11%, is on Cl_rms, which is exactly
      the quantity most sensitive to confinement, and it moves the SHORTER
      domain's number closer to the experimental band, not further from
      it). They adopt Lz/D=6 as their production choice for Re=400-1000.
      SPAN_3D below matches that choice directly, not an independent guess.

  Spanwise cell length dz/D (their Table 3, cases 1, 3, 4, 5, all at
  Lz/D=6): 0.05 (ref) / 0.03 / 0.0706 / 0.1. The forces are markedly MORE
  sensitive to dz than to Lz, and specifically overshoot Cl_rms as dz
  coarsens (0.1191 at dz=0.05 -> 0.1624 at dz=0.1, a +36% move) because a
  coarser spanwise grid cannot resolve the streamwise vortices of Mode B
  and under-decorrelates the span. This is the reason DZ_OVER_D below is
  offered at two levels rather than one: dz/D=0.05 is what the reference
  paper actually validated as adequate; dz/D=0.10 is this task's own
  affordable pilot, justified only by the fact that even Jiang & Cheng's
  OWN dz=0.1 case still lands at Cl_rms=0.1624 -- five to eight times below
  the 2D value (~0.97-1.03), i.e. it still discriminates 2D from 3D by
  close to an order of magnitude even though it is not grid-converged in
  the tight (few-%) sense their production mesh is.

Seeding the instability: a translationally-uniform (z-independent) initial
condition sitting exactly on the cyclic-BC symmetry plane can take a long
time to grow 3D structure from floating-point round-off alone. Instead of
waiting on that, ``setFieldsDict`` below carves the span into alternating
slabs of width dz_slab (default 0.5D, i.e. a spanwise SQUARE WAVE with
fundamental wavelength 2*dz_slab = 1D, matched to the Mode-B wavelength
target) and gives each slab a small +/-0.02 U_inf spanwise (w) velocity
kick. This is the direct 3D analogue of the +/-0.1 crossflow perturbation
the 2D cases in this same codebase already use to break symmetry and seed
shedding from an impulsive start (see cylinder_vortex_shedding.initial_fields
docstring) -- small enough not to bias the eventual limit cycle, which the
existing stationarity gate (halves_drift) checks independently, but shaped
at the target instability's own wavelength so it does not have to wait on
whichever wavelength round-off happens to excite first.
"""
from __future__ import annotations

import json
import math
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Callable

_HERE = Path(__file__).resolve()
sys.path.insert(0, str(_HERE.parent))
_REPO_ROOT = _HERE.parents[4]
sys.path.insert(0, str(_REPO_ROOT / "sdk"))

from workflows.tmr_verification import (          # noqa: E402
    _foam, _foam_header, _run_prefix, _copy_best_effort,
    fv_schemes, transport_properties, time_weighted_stats, measure_period,
    halves_drift, _decompose_par_dict, ratio_for_first_cell,
)
from workflows.cylinder_vortex_shedding import (   # noqa: E402
    DIAMETER, U_INF, block_mesh_dict,
)
import cylinder_ladder as CL                        # noqa: E402
from chief_engineer.head_engineer import parse_coefficient_history  # noqa: E402

_RUN_ROOT = Path.home() / "certonomous-runs" / "f5a-cylinder-ladder"

# ---------------------------------------------------------------------------
# The one new experimental variable: spanwise extent and resolution.
# Everything else (Re=1000, laminar, in-plane mesh, farfield, first cell,
# dt0, maxCo) is held byte-identical to the established re1000 rung.
# ---------------------------------------------------------------------------
REYNOLDS = 1000.0
N_RADIAL = 80            # matches re1000 rung exactly
N_TANGENTIAL = 70        # matches re1000 rung exactly
FIRST_CELL = 0.00447     # matches re1000 rung exactly
FARFIELD_DIAMETERS = 20.0  # matches re1000 rung exactly
DT0 = 0.005
MAX_CO = 1.5

SPAN_3D_OVER_D = 6.0     # Jiang & Cheng (2017) Table 1/3 production choice

# Two spanwise-resolution presets. "reference" reproduces Jiang & Cheng's
# own validated dz/D=0.05; "pilot" is this task's affordable dz/D=0.10
# option (their own least-resolved sensitivity case, Table 3 case 5).
DZ_PRESETS = {
    "reference": 0.05,   # 120 spanwise cells over Lz/D=6 -- 2,688,000 total
    "pilot": 0.10,        # 60 spanwise cells over Lz/D=6  -- 1,344,000 total
}

SLAB_WIDTH_OVER_D = 0.5   # seeding square-wave half-wavelength -> lambda=1D
SEED_W_AMPLITUDE = 0.02   # spanwise velocity kick, fraction of U_inf


def n_span_for(dz_over_d: float, span_over_d: float = SPAN_3D_OVER_D) -> int:
    n = span_over_d / dz_over_d
    n_round = round(n)
    if abs(n - n_round) > 1e-6:
        raise ValueError(f"span/dz = {n} is not an integer number of cells")
    return int(n_round)


def cell_count(n_span: int) -> int:
    return N_RADIAL * N_TANGENTIAL * 4 * n_span


# ---------------------------------------------------------------------------
# Fields: same uniform 2D-style baseline as every laminar rung on this
# ladder, but with the frontAndBack patch replaced by a cyclic front/back
# pair (no BC values needed for a cyclic patch, only the type).
# ---------------------------------------------------------------------------

def initial_fields_laminar_3d(perturbation: float = 0.1) -> dict[str, str]:
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
        + "    front\n    {\n        type            cyclic;\n    }\n"
        + "    back\n    {\n        type            cyclic;\n    }\n}\n"
    )
    p_text = (
        _foam_header("volScalarField", "p", "0")
        + "dimensions      [0 2 -2 0 0 0 0];\n\n"
        + "internalField   uniform 0;\n\nboundaryField\n{\n"
        + "    farfield\n    {\n        type            freestreamPressure;\n"
        + "        freestreamValue uniform 0;\n        value           uniform 0;\n    }\n"
        + "    cylinder\n    {\n        type            zeroGradient;\n    }\n"
        + "    front\n    {\n        type            cyclic;\n    }\n"
        + "    back\n    {\n        type            cyclic;\n    }\n}\n"
    )
    return {"U": u_text, "p": p_text}


def set_fields_dict(span: float, slab_width: float = SLAB_WIDTH_OVER_D * DIAMETER,
                    w_amplitude: float = SEED_W_AMPLITUDE, u_inf: float = U_INF,
                    perturbation: float = 0.1) -> str:
    """Alternating +/- spanwise-velocity slabs seeding a fundamental
    wavelength of 2*slab_width, targeted at the Mode-B wavelength (<1D;
    default slab_width=0.5D -> lambda=1D)."""
    n_slabs = int(round(span / slab_width))
    regions = []
    big = 1000.0 * (DIAMETER + span)
    for i in range(n_slabs):
        z0 = i * slab_width
        z1 = (i + 1) * slab_width
        w = w_amplitude * u_inf * (1 if i % 2 == 0 else -1)
        regions.append(
            "    boxToCell\n    {\n"
            f"        box ({-big:.6g} {-big:.6g} {z0:.6g}) ({big:.6g} {big:.6g} {z1:.6g});\n"
            "        fieldValues\n        (\n"
            f"            volVectorFieldValue U ({u_inf:g} {perturbation:g} {w:.6g})\n"
            "        );\n    }\n"
        )
    return (
        _foam_header("dictionary", "setFieldsDict", "system")
        + f"defaultFieldValues\n(\n    volVectorFieldValue U ({u_inf:g} {perturbation:g} 0)\n);\n\n"
        + "regions\n(\n" + "\n".join(regions) + "\n);\n"
    )


def base_probe_point_3d(first_cell: float, span: float) -> tuple[float, float, float]:
    x = DIAMETER / 2.0 + 1.5 * first_cell
    return (x, 0.0, span / 2.0)


def centerline_probe_points_3d(span: float, lo_over_d: float = 0.05,
                               hi_over_d: float = 2.4, step_over_d: float = 0.05
                               ) -> list[tuple[float, float, float]]:
    pts = []
    n = int(round((hi_over_d - lo_over_d) / step_over_d)) + 1
    for i in range(n):
        s = lo_over_d + i * step_over_d
        x = DIAMETER / 2.0 + s * DIAMETER
        pts.append((x, 0.0, span / 2.0))
    return pts


# ---------------------------------------------------------------------------
# Case build
# ---------------------------------------------------------------------------

def build_case_3d(case_dir: Path, *, dz_preset: str, end_time: float,
                  perturbation: float = 0.1) -> dict[str, Any]:
    case = Path(case_dir)
    for sub in ("0", "constant", "system"):
        (case / sub).mkdir(parents=True, exist_ok=True)
    nu = DIAMETER * U_INF / REYNOLDS
    dz = DZ_PRESETS[dz_preset]
    span = SPAN_3D_OVER_D * DIAMETER
    n_span = n_span_for(dz, SPAN_3D_OVER_D)

    (case / "system" / "blockMeshDict").write_text(
        block_mesh_dict(DIAMETER, FARFIELD_DIAMETERS, N_RADIAL, N_TANGENTIAL,
                        FIRST_CELL, span=span, n_span=n_span, spanwise_bc="cyclic"))
    (case / "system" / "fvSchemes").write_text(CL.fv_schemes(limited=False, transient=True))
    (case / "system" / "fvSolution").write_text(CL.pimple_fv_solution())
    (case / "constant" / "transportProperties").write_text(CL.transport_properties(nu))
    (case / "constant" / "turbulenceProperties").write_text(CL._LAMINAR_TURBULENCE)

    base_pt = base_probe_point_3d(FIRST_CELL, span)
    cl_pts = centerline_probe_points_3d(span)
    (case / "system" / "controlDict").write_text(
        CL.control_dict(end_time, DT0, aref=DIAMETER * span, max_co=MAX_CO,
                        base_point=base_pt, centerline_points=cl_pts))
    (case / "system" / "setFieldsDict").write_text(
        set_fields_dict(span, perturbation=perturbation))

    for name, text in initial_fields_laminar_3d(perturbation).items():
        (case / "0" / name).write_text(text)

    return {"reynolds": REYNOLDS, "nu": nu, "turbulence": "laminar",
            "n_radial": N_RADIAL, "n_tangential": N_TANGENTIAL,
            "n_span": n_span, "dz_over_d": dz, "span_over_d": SPAN_3D_OVER_D,
            "cells": cell_count(n_span), "first_cell": FIRST_CELL,
            "farfield_diameters": FARFIELD_DIAMETERS, "end_time": end_time,
            "dt0": DT0, "max_co": MAX_CO, "base_point": base_pt,
            "centerline_points": cl_pts, "perturbation": perturbation,
            "dz_preset": dz_preset}


def stage(name: str, out_dir: Path, *, dz_preset: str, end_time: float,
         run_check_mesh: bool = True) -> dict[str, Any]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    case = out_dir / "case"
    remote_dir = _RUN_ROOT / name
    shutil.rmtree(remote_dir, ignore_errors=True)
    remote_dir.parent.mkdir(parents=True, exist_ok=True)

    params = build_case_3d(case, dz_preset=dz_preset, end_time=end_time)
    shutil.copytree(case, remote_dir)

    timings: dict[str, float] = {}
    start = time.monotonic()
    result = _foam(["blockMesh"], remote_dir, "log.blockMesh", timeout=1800)
    timings["blockMesh"] = round(time.monotonic() - start, 1)
    _copy_best_effort(remote_dir / "log.blockMesh", out_dir / "log.blockMesh")
    print(f"[{name}] blockMesh done in {timings['blockMesh']:.1f}s (exit {result.returncode}), "
         f"cells={params['cells']:,} (n_span={params['n_span']}, dz/D={params['dz_over_d']:g})")
    if result.returncode != 0:
        raise RuntimeError(f"{name}: blockMesh failed")

    if run_check_mesh:
        start = time.monotonic()
        result = _foam(["checkMesh", "-allTopology", "-allGeometry"], remote_dir,
                       "log.checkMesh", timeout=1800)
        timings["checkMesh"] = round(time.monotonic() - start, 1)
        _copy_best_effort(remote_dir / "log.checkMesh", out_dir / "log.checkMesh")
        print(f"[{name}] checkMesh done in {timings['checkMesh']:.1f}s (exit {result.returncode})")

    (out_dir / "stage_params.json").write_text(json.dumps(
        {"params": params, "timings": timings, "remote_dir": str(remote_dir)}, indent=2))
    return {"params": params, "remote_dir": remote_dir, "timings": timings}


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--dz-preset", choices=list(DZ_PRESETS), default="pilot")
    parser.add_argument("--end-time", type=float, default=150.0)
    parser.add_argument("--no-check-mesh", action="store_true")
    args = parser.parse_args(argv)

    result = stage(args.name, Path(args.out), dz_preset=args.dz_preset,
                   end_time=args.end_time, run_check_mesh=not args.no_check_mesh)
    print(json.dumps({k: v for k, v in result.items() if k != "remote_dir"} |
                     {"remote_dir": str(result["remote_dir"])}, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
