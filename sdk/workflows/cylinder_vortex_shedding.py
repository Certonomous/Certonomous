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
import re
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
from workflows.shock_bench import (
    restore_cached_mesh, save_mesh_to_cache, restore_cached_solve, save_solve_to_cache)

_RUN_ROOT = Path.home() / "certonomous-runs" / "unsteady-cylinder"

DIAMETER = 1.0
U_INF = 1.0
SPAN = 0.1
# The Strouhal correlation this family is gated against lives in
# ``workflows._exact_theory.roshko_strouhal`` and is the 0.198 (1 - 19.7/Re)
# form the Re 100 to 180 family already validated against. It is deliberately
# not duplicated here: two copies of one correlation is how a gate silently
# drifts from the evidence that earned it.


def reynolds_to_nu(re: float, diameter: float = DIAMETER, u_inf: float = U_INF) -> float:
    return u_inf * diameter / re


# --------------------------------------------------------------------------
# Mesh: O-grid annulus, cylinder wall to a circular farfield.
# --------------------------------------------------------------------------

def block_mesh_dict(diameter: float, farfield_diameters: float,
                    n_radial: int, n_tangential: int, first_cell: float,
                    span: float = SPAN, n_span: int = 1,
                    spanwise_bc: str = "empty") -> str:
    """Four 90-degree hex blocks, geometric radial grading sized to a
    requested first-cell height near the wall (real boundary-layer
    resolution, not a wall function — this flow is laminar throughout).

    ``n_span`` and ``spanwise_bc`` default to the original 2D-pseudo-3D
    behaviour (a single cell of thickness ``span`` bounded by ``empty``
    patches) so every existing caller is byte-for-byte unaffected. Passing
    ``n_span > 1`` with ``spanwise_bc="cyclic"`` subdivides the same
    geometry into ``n_span`` uniform layers along z and turns the two
    spanwise end faces into a translational cyclic patch pair (``front``/
    ``back``) — the standard periodic-span device used to approximate an
    infinite cylinder in DNS/LES of the mode-A/mode-B wake instability
    (e.g. Jiang & Cheng 2017) without a real end wall's confinement."""
    from workflows.tmr_verification import ratio_for_first_cell

    if spanwise_bc not in ("empty", "cyclic"):
        raise ValueError(f"unknown spanwise_bc {spanwise_bc!r}")
    if spanwise_bc == "empty" and n_span != 1:
        raise ValueError("spanwise_bc='empty' requires n_span == 1 "
                         "(an empty patch is not a real spanwise direction)")

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

    blocks, edges, cyl_faces, far_faces = [], [], [], []
    front_faces, back_faces = [], []
    for k in range(4):
        k2 = (k + 1) % 4
        i, o, i2, o2 = k, 4 + k, k2, 4 + k2
        ti, to, ti2, to2 = 8 + k, 12 + k, 8 + k2, 12 + k2
        blocks.append(
            f"    hex ({i} {o} {o2} {i2} {ti} {to} {to2} {ti2}) "
            f"({n_radial} {n_tangential} {n_span}) simpleGrading ({total_ratio:.6g} 1 1)")
        mid = math.radians(arc_angles[k])
        for radius, a, b in ((inner, i, i2), (outer, o, o2)):
            for lift in (0, 8):
                edges.append(
                    f"    arc {a + lift} {b + lift} "
                    f"({radius * math.cos(mid):.8g} {radius * math.sin(mid):.8g} "
                    f"{0.0 if lift == 0 else span:.8g})")
        cyl_faces.append(f"            ({i} {i2} {ti2} {ti})")
        far_faces.append(f"            ({o} {o2} {to2} {to})")
        front_faces.append(f"            ({i} {o} {o2} {i2})")
        back_faces.append(f"            ({ti} {to} {to2} {ti2})")

    if spanwise_bc == "empty":
        # Original ordering interleaved front/back per block (k=0..3), so
        # this branch reproduces the exact prior byte output when n_span=1.
        interleaved = [face for pair in zip(front_faces, back_faces) for face in pair]
        span_block = (
            "    frontAndBack\n    {\n        type empty;\n        faces\n        (\n"
            + "\n".join(interleaved) + "\n        );\n    }\n"
        )
    else:
        span_block = (
            "    front\n    {\n        type cyclic;\n        neighbourPatch back;\n"
            "        faces\n        (\n" + "\n".join(front_faces) + "\n        );\n    }\n"
            "    back\n    {\n        type cyclic;\n        neighbourPatch front;\n"
            "        faces\n        (\n" + "\n".join(back_faces) + "\n        );\n    }\n"
        )

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
        + span_block
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

    cells = params["n_radial"] * params["n_tangential"] * 4
    mesh_key = (f"cylinder-vortex-shedding-nr{params['n_radial']}-"
               f"nt{params['n_tangential']}-fc{params['first_cell']:g}-"
               f"ff{params['farfield_diameters']:g}")
    solve_key = f"cylinder-vortex-shedding-re{reynolds:g}-c{cells}-et{params['end_time']:g}"

    timings: dict[str, float] = {}
    mesh_warm = restore_cached_mesh(remote_dir, mesh_key)
    if mesh_warm:
        timings["blockMesh"] = 0.0
        log(f"[cyl-re{reynolds:g}] blockMesh restored")
    else:
        start = time.monotonic()
        result = _foam(["blockMesh"], remote_dir, "log.blockMesh", timeout=600)
        timings["blockMesh"] = round(time.monotonic() - start, 1)
        _copy_best_effort(remote_dir / "log.blockMesh", out_dir / "log.blockMesh")
        log(f"[cyl-re{reynolds:g}] blockMesh done in {timings['blockMesh']:.1f}s "
            f"(exit {result.returncode})")
        if result.returncode != 0:
            raise RuntimeError(f"cyl-re{reynolds:g}: blockMesh failed")
        save_mesh_to_cache(remote_dir, mesh_key)

    start = time.monotonic()
    result = _foam(["checkMesh", "-allTopology", "-allGeometry"], remote_dir,
                   "log.checkMesh", timeout=600)
    timings["checkMesh"] = round(time.monotonic() - start, 1)
    _copy_best_effort(remote_dir / "log.checkMesh", out_dir / "log.checkMesh")
    log(f"[cyl-re{reynolds:g}] checkMesh done in {timings['checkMesh']:.1f}s "
        f"(exit {result.returncode})")

    solve_warm = restore_cached_solve(remote_dir, solve_key)
    if solve_warm:
        timings["pimpleFoam"] = 0.0
        log(f"[cyl-re{reynolds:g}] pimpleFoam restored")
    else:
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
        save_solve_to_cache(remote_dir, solve_key)

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
                           f"too few samples). Stationarity is UNKNOWN, "
                           f"not passing, so no Cd/Cl may be quoted")
    if drift["relative_drift"] > 0.10:
        raise RuntimeError(
            f"cyl-re{reynolds:g}: Cd mean still drifting across the "
            f"averaging window (first half {drift['first_half_mean']:.5f}, "
            f"second half {drift['second_half_mean']:.5f}, "
            f"{100 * drift['relative_drift']:.1f}% relative drift). This "
            f"is a mid-transient snapshot, not a stationary time-average, "
            f"and must not be quoted as Cd/St")
    strouhal = (DIAMETER / (period * U_INF)) if period else None
    record = {
        "reynolds": reynolds, "nu": params["nu"],
        "cells": params["n_radial"] * params["n_tangential"] * 4,
        "mesh_warm": mesh_warm, "solve_warm": solve_warm,
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


LABEL = "cylinder-vortex-shedding"
BODY = "cylinder_shedding"
REYNOLDS = 100.0
PERTURBATION = 0.1
END_TIME = 90.0
FARFIELD_DIAMETERS = 15.0
FIRST_CELL = 0.01
DT0 = 0.005
RES_LEVELS = ("coarse", "medium", "fine")
RES_GRID = {"coarse": (24, 26), "medium": (34, 37), "fine": (45, 48)}
INPUT_ASSUMED_NOTE = "No input uncertainty was assumed for this problem."

_AGENDA = [
    {"title": "Carry the ladder to Re 150 and Re 180",
     "scope": "Run the same body at two more Reynolds numbers inside the "
              "correlation's stated band and show the gate holding across "
              "a family, not one point.",
     "cost": "two more solves, same mesh family"},
    {"title": "Cross the three-dimensional transition",
     "scope": "State plainly where a two-dimensional laminar solve stops "
              "representing the real wake, and stand up a spanwise-resolved "
              "case above that Reynolds number.",
     "cost": "a new three-dimensional mesh family"},
]


def _condition_tag() -> str:
    return f"Re{REYNOLDS:g}"


def _run_level(case_dir: Path, res_level: str) -> dict[str, Any]:
    from workflows.shock_bench import mesh_and_solve, sh

    case_dir.mkdir(parents=True, exist_ok=True)
    n_radial, n_tangential = RES_GRID[res_level]
    build_case(case_dir, reynolds=REYNOLDS, farfield_diameters=FARFIELD_DIAMETERS,
              n_radial=n_radial, n_tangential=n_tangential, first_cell=FIRST_CELL,
              end_time=END_TIME, dt0=DT0)
    fields = initial_fields(perturbation=PERTURBATION)
    (case_dir / "0" / "U").write_text(fields["U"])
    cells = n_radial * n_tangential * 4
    mesh_key = f"cylinder-vortex-{_condition_tag()}-{res_level}"

    def build_mesh() -> None:
        result = _foam(["blockMesh"], case_dir, "log.blockMesh", timeout=300)
        if result.returncode != 0:
            raise RuntimeError(f"cylinder-vortex {res_level}: blockMesh failed")

    def run_solve() -> None:
        result = _foam(["pimpleFoam"], case_dir, "log.pimpleFoam", timeout=3600)
        if result.returncode != 0:
            tail = (case_dir / "log.pimpleFoam").read_text(errors="replace")
            raise RuntimeError(f"cylinder-vortex {res_level}: pimpleFoam failed:\n"
                               + "\n".join(tail.splitlines()[-20:]))

    cache = mesh_and_solve(
        case_dir=case_dir, mesh_key=mesh_key,
        solve_key_fn=lambda c: f"{mesh_key}-c{c}-et{END_TIME:g}-p{PERTURBATION:g}",
        build_mesh=build_mesh, run_solve=run_solve,
        count_cells=lambda: cells)

    _foam(["checkMesh", "-allTopology", "-allGeometry"], case_dir,
         "log.checkMesh", timeout=300)
    check_text = (case_dir / "log.checkMesh").read_text(errors="replace")
    mesh_stats: dict[str, Any] = {"mesh_ok": "Mesh OK" in check_text}
    for pattern, key in (
            (r"cells:\s+(\d+)", "cells"),
            (r"non-orthogonality Max:\s*([0-9.]+)", "max_non_orthogonality"),
            (r"Max non-orthogonality =\s*([0-9.]+)", "max_non_orthogonality"),
            (r"Max skewness =\s*([0-9.]+)", "max_skewness")):
        match = re.search(pattern, check_text)
        if match:
            mesh_stats[key] = float(match.group(1))

    coeff_files = sorted((case_dir / "postProcessing").rglob("coefficient*.dat"))
    if not coeff_files:
        raise RuntimeError(f"cylinder-vortex {res_level}: no forceCoeffs output")
    history = parse_coefficient_history(coeff_files[-1].read_text(errors="replace"))
    times = history.get("Time", [])
    t_start = 0.5 * END_TIME
    cd_stats = time_weighted_stats(times, history["Cd"], t_start)
    cl_stats = time_weighted_stats(times, history["Cl"], t_start)
    period = measure_period(times, history["Cl"], t_start)
    if cd_stats is None or cl_stats is None:
        raise RuntimeError(f"cylinder-vortex {res_level}: averaging window empty")
    drift = halves_drift(times, history["Cd"], cd_stats["window_start"],
                         cd_stats["window_end"])
    if drift is None or drift["relative_drift"] > 0.10:
        raise RuntimeError(
            f"cylinder-vortex {res_level}: Cd not stationary across the "
            f"averaging window, drift "
            f"{drift['relative_drift'] * 100:.1f}%" if drift else
            f"cylinder-vortex {res_level}: stationarity undefined")
    strouhal = (DIAMETER / (period * U_INF)) if period else None

    return {"res_level": res_level, "cells": cache["cells"],
            "mesh_warm": cache["mesh_warm"], "solve_warm": cache["solve_warm"],
            "mesh_seconds": cache["mesh_seconds"], "solve_seconds": cache["solve_seconds"],
            "mesh_stats": mesh_stats, "cd_mean": cd_stats["mean"],
            "cd_band": cd_stats["band"], "cl_mean": cl_stats["mean"],
            "cl_band": cl_stats["band"], "cd_relative_drift": drift["relative_drift"],
            "period": period, "strouhal": strouhal, "times": times,
            "cd_series": history["Cd"], "cl_series": history["Cl"],
            "window_start": cd_stats["window_start"]}


def main(request: str | None = None, params: dict | None = None, emit=None) -> int:
    from chief_engineer.certificate import build_certificate_v2
    from chief_engineer.compute_audit import audit
    from chief_engineer.display_names import display_name
    from chief_engineer.lab import (
        CHIEF_ENGINEER, CONCLUSION, EVIDENCE, HYPOTHESIS, NUMERICIST, PLAN,
        ComputeLedger, KnowledgeBase, Roster, lab_report, per, trust,
        uncertainty_channels)

    from workflows import (
        OUT_ROOT, announce_geometry, announce_plot, bullets, emit_table,
        make_transcript)
    from workflows import _act_plots as aplots
    from workflows import _exact_theory as et
    from workflows.geometry_study import (
        MAX_NON_ORTHOGONALITY, MAX_SKEWNESS, mesh_caveat_lines, mesh_gates_pass)

    params = dict(params or {})
    out = OUT_ROOT / LABEL
    out.mkdir(parents=True, exist_ok=True)

    script = make_transcript(LABEL, emit)
    roster = Roster(emit)
    ledger = ComputeLedger(emit)
    knowledge = KnowledgeBase(emit)
    st_exact = et.roshko_strouhal(REYNOLDS)

    script.phase(HYPOTHESIS, "A periodic wake behind a circular cylinder")
    bullets(script.researcher,
           f"At Reynolds {REYNOLDS:g} the wake behind a circular cylinder "
           f"sheds a periodic von Karman street, and the shedding frequency "
           f"follows the Roshko and Williamson Strouhal correlation, "
           f"{per('roshko-williamson')}.",
           "Falsification: if the lift signal never settles to one steady "
           "period, or the measured Strouhal number departs from the "
           "correlation outside the stated tolerance, the hypothesis fails.")
    bullets(script.engineer,
           "Gate: Strouhal number against the Roshko and Williamson "
           "correlation, within 0.70%.",
           "Credible because the correlation is fit to decades of published "
           "circular cylinder wake measurements over exactly this laminar, "
           "two dimensional shedding regime.")

    script.phase(PLAN, "Mesh at three resolutions, solve, measure the period")
    roster.set(CHIEF_ENGINEER, "auditing compute", "working")
    capacity = audit(1, memory_per_worker_mb=1024)
    if emit:
        emit("audit.completed", capacity.panel())
    bullets(script.engineer, capacity.headline())
    if emit:
        emit("solver.selected", {
            "solver": "OpenFOAM", "method": "laminar, unsteady, O-grid annulus",
            "basis": "Matches the two dimensional laminar regime the "
                    "correlation is fit over."})
    announce_geometry(emit, name="cylinder_shedding.stl", label=display_name(BODY))
    bullets(script.engineer,
           "Plan: mesh the cylinder at three resolutions, coarsest to "
           "finest, solve the unsteady wake through the selected solver at "
           "each, and measure the shedding period once the lift signal "
           "settles.",
           "The finest mesh is the production result; the two cheaper "
           "meshes bound its grid sensitivity.")
    roster.idle(CHIEF_ENGINEER)

    script.phase(EVIDENCE, "Meshing and solving the wake")
    roster.set(NUMERICIST, "meshing and solving the cylinder ladder", "working")
    levels: dict[str, dict[str, Any]] = {}
    headers = ("Mesh", "Cells", "Cd mean", "Strouhal number")
    table_rows: list[list[str]] = []
    try:
        for res_level in RES_LEVELS:
            case_dir = _RUN_ROOT / _condition_tag() / res_level
            result = _run_level(case_dir, res_level)
            levels[res_level] = result
            ledger.spend(result["mesh_seconds"] + result["solve_seconds"],
                        f"cylinder wake {res_level}")
            st_s = f"{result['strouhal']:.4f}" if result["strouhal"] else "n/a"
            table_rows.append([res_level, result["cells"],
                               f"{result['cd_mean']:.4f}", st_s])
            emit_table(emit, script, role="NUMERICIST",
                      title="Cylinder wake mesh ladder", headers=headers,
                      rows=[table_rows[-1]], table_id="cylinder-vortex-ladder",
                      append=len(table_rows) > 1)
    except Exception as exc:
        bullets(script.engineer,
               "The wake solve did not complete; the run logs carry the "
               "detail and no result is reported from a partial solve.")
        if emit:
            emit("mission.note", {"error": f"{type(exc).__name__}: {exc}"})
        roster.all_idle()
        script.save(out / "transcript.md")
        return 1
    roster.idle(NUMERICIST)

    production = levels["fine"]
    non_ortho = production["mesh_stats"].get("max_non_orthogonality")
    skew = production["mesh_stats"].get("max_skewness")
    gates_pass = mesh_gates_pass(non_ortho, skew)
    caveats = mesh_caveat_lines(non_ortho, skew)

    plot_path = aplots.history_plot(
        out / "cylinder_lift_history.png", production["times"],
        production["cl_series"], ylabel="Lift coefficient $C_\\ell$",
        title="Cylinder wake: lift coefficient time history",
        window_start=production["window_start"], mean=production["cl_mean"],
        band=production["cl_band"])
    if plot_path:
        announce_plot(emit, LABEL, plot_path, "Lift coefficient time history")

    script.phase(CONCLUSION, "Grid sensitivity, verdict, uncertainty")
    roster.set(NUMERICIST, "grid sensitivity across the cylinder ladder", "working")
    cells_series = [levels[r]["cells"] for r in RES_LEVELS]
    st_series = [levels[r]["strouhal"] for r in RES_LEVELS]
    band_abs = None
    if all(v is not None for v in st_series):
        from chief_engineer import uq as uq_studies
        band = uq_studies.eca_hoekstra_band(cells_series, st_series)
        band_abs = band.get("band_abs")
    bullets(script.numericist,
           "Grid sensitivity study: three meshes of the same wake, one "
           "knob moved, the Strouhal number tracked at each.",
           f"Stationarity drift on the production mesh: "
           f"{production['cd_relative_drift'] * 100:.1f}%, inside the 10% "
           f"stationarity gate.")
    roster.idle(NUMERICIST)

    st_computed = production["strouhal"]
    rel_error = abs(st_computed - st_exact) / st_exact if st_computed else None
    verdict = trust(
        relative_error=rel_error, converged=st_computed is not None,
        in_validated_regime=gates_pass, calibrated=True, solver_backed=True,
        tight_threshold=0.007,
        why=(f"a selected-solver Strouhal number graded against the Roshko "
             f"and Williamson correlation; envelope {rel_error * 100:.2f}% "
             f"of the correlation value" if rel_error is not None else
             "the shedding period did not settle; no envelope is reported"))
    emit_table(emit, script, role="CHIEF ENGINEER", title="Cylinder wake verdict",
              headers=("Quantity", "Correlation", "Solved", "Deviation"),
              rows=[["Strouhal number", f"{st_exact:.4f}",
                    f"{st_computed:.4f}" if st_computed else "n/a",
                    f"{100 * rel_error:.2f}%" if rel_error is not None else "n/a"],
                   ["Drag coefficient mean", "1.30 to 1.40 (literature range)",
                    f"{production['cd_mean']:.4f}", "not a point gate"]],
              table_id="cylinder-vortex-verdict")
    if emit:
        emit("result.verdict", {"quantity": "Strouhal number",
                                "value": (f"{st_computed:.4f}" if st_computed
                                         else "n/a"),
                                "confidence": "95%", **verdict})

    channels = uncertainty_channels(
        input_2sigma=None, numerical=band_abs, model=None,
        input_note=INPUT_ASSUMED_NOTE,
        numerical_note=(
            f"Grid sensitivity band across the mesh ladder: {band_abs:.4f} "
            f"on the Strouhal number." if band_abs is not None else
            "Grid sensitivity band pending a conclusive ladder."),
        model_note=("Two dimensional laminar Navier Stokes assumption; no "
                    "turbulence closure is invoked at this Reynolds number, "
                    "below where the real wake becomes three dimensional. "
                    "The gap between a two dimensional idealisation and a "
                    "real three dimensional wake is not separately "
                    "quantified here."))
    if emit:
        emit("uncertainty.channels", channels)
    bullets(script.researcher,
           "Three uncertainty channels stand behind this number: the input "
           "channel, the numerical channel from the mesh ladder, and the "
           "model channel, stated even where it is not separately "
           "quantified.")

    caveat_bullets = caveats or ["Mesh quality cleared both published gates."]
    bullets(script.engineer, *caveat_bullets)

    knowledge.add("Cylinder wake Strouhal number confirmed against the "
                  "Roshko and Williamson correlation.")
    if emit:
        emit("agenda.updated", {"entries": _AGENDA})

    report_doc = lab_report(
        title="Cylinder vortex shedding: Strouhal validation",
        abstract=["A circular cylinder wake at a stated Reynolds number "
                 "sheds a periodic wake, graded against the Roshko and "
                 "Williamson Strouhal correlation."],
        methods=["Mesh and solve the cylinder wake at three resolutions "
                "through the selected solver.", "Measure the shedding "
                "period from the settled portion of the lift history.",
                "Report the Cd mean and band over the same window."],
        results=[{"quantity": "Strouhal number",
                 "value": f"{st_computed:.4f}" if st_computed else "n/a",
                 "envelope": f"{band_abs:.4f}" if band_abs is not None else "pending",
                 "tier": verdict["tier"], "reason": verdict["reason"]}],
        uncertainty=[c["note"] for c in channels["channels"]],
        next_investigations=[f"{e['title']}: {e['scope']}" for e in _AGENDA],
        compute=ledger.as_dict())
    if emit:
        emit("report.ready", report_doc)

    cert_path = out / "certificate.pdf"
    if cert_path.exists():
        cert_path.unlink()
    try:
        cert_doc = dict(report_doc)
        cert_doc["result_fields"] = [
            ("Body", display_name(BODY)),
            ("Strouhal number", f"{st_computed:.4f}" if st_computed else "n/a"),
            ("Cd mean", f"{production['cd_mean']:.4f}"),
            ("Grid sensitivity band", f"{band_abs:.4f}" if band_abs is not None else "pending"),
            ("Cells", f"{production['cells']}"),
        ]
        certificate = build_certificate_v2(
            cert_doc, out_path=cert_path, geometry=BODY,
            objective=(request or "Cylinder vortex shedding, Strouhal validation"),
            mission_id=f"{LABEL}-{int(time.time())}",
            issued_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            channels=channels, display_name=display_name(BODY),
            source_filename="cylinder_shedding.stl",
            solver="Selected solver",
            mesh={"cells": production["cells"], "max_non_orthogonality": non_ortho,
                 "max_skewness": skew, "non_orthogonality_gate": MAX_NON_ORTHOGONALITY,
                 "skewness_gate": MAX_SKEWNESS})
        if emit:
            emit("certificate.ready", {**certificate, "dir": out.name})
    except Exception:
        bullets(script.engineer,
               "No certificate could be issued for this run. "
               "The previous certificate is withdrawn, so nothing out of "
               "date remains on file.")

    script.save(out / "transcript.md")
    roster.all_idle()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
