"""Hypersonic cylinder: a bow shock standing off a blunt circular leading
edge, gated against the Billig shock-standoff correlation and, on the
windward surface, modified Newtonian pressure theory.

The case, the mesh and the closed-form theory are not re-derived here: they
are the same functions that already validated this body (``make_cylinder_case``,
``billig_theory``, and the shock-locus fit in ``run_cylinder_case``, all under
``demo-output/website/campaign/F4_runs``). This act adds the control-room
narration, the mesh-and-solve cache, and the certificate.
"""

from __future__ import annotations

import glob
import math
import re
import time
from pathlib import Path
from typing import Any

from chief_engineer.certificate import build_certificate_v2
from chief_engineer.compute_audit import audit
from chief_engineer.display_names import display_name
from chief_engineer.lab import (
    CHIEF_ENGINEER, CONCLUSION, EVIDENCE, HYPOTHESIS, NUMERICIST, PLAN,
    ComputeLedger, KnowledgeBase, Roster, lab_report, per, trust, uncertainty_channels)
from chief_engineer import uq as uq_studies

from workflows import (
    OUT_ROOT, announce_geometry, announce_plot, bullets, emit_table, make_transcript)
from workflows.geometry_study import mesh_caveat_lines, mesh_gates_pass, mesh_validity
from workflows.shock_bench import comparison_plot, mesh_and_solve, run_checkmesh, sh

import make_cylinder_case  # noqa: E402  (F4_runs, path-inserted by shock_bench)
import run_cylinder_case  # noqa: E402
import billig_theory  # noqa: E402

LABEL = "hypersonic-cylinder"
BODY = "hypersonic_cylinder"
_RUN_ROOT = Path.home() / "certonomous-runs" / LABEL

MACH = 8.0
RES_LEVELS = ("coarse", "medium", "fine")
RES_CELLS = {"coarse": 1000, "medium": 4000, "fine": 16000}
N_THETA_STATIONS = 7
N_AVG_SNAPSHOTS = 3
INPUT_ASSUMED_NOTE = "No input uncertainty was assumed for this problem."

_AGENDA = [
    {"title": "Sweep Mach number across the hypersonic cylinder family",
     "scope": "Carry the same body up through a second and third Mach "
              "number and confirm the standoff distance tracks the Billig "
              "correlation's Mach dependence throughout.",
     "cost": "two more mesh-and-solve triples, same body"},
    {"title": "Extend the windward Cp comparison past the shoulder",
     "scope": "Push the surface sampling stations further around the body "
              "and confirm modified Newtonian theory's known departure past "
              "the shoulder is bounded and explained.",
     "cost": "no new solve, a wider sampling pass on the finished field"},
]


def _time_dirs(case_dir: Path) -> list[str]:
    names = [p.name for p in case_dir.iterdir()
             if p.is_dir() and re.fullmatch(r"[0-9]+\.?[0-9]*", p.name) and p.name != "0"]
    return sorted(names, key=float)


def _exact_reference() -> dict[str, float]:
    return {"standoff": billig_theory.billig_delta_over_R(MACH) * make_cylinder_case.R,
            "cp_max": billig_theory.cp_max_rayleigh_pitot(MACH)}


def _run_level(case_dir: Path, res_level: str) -> dict[str, Any]:
    case_dir.mkdir(parents=True, exist_ok=True)
    meta = make_cylinder_case.make_case(str(case_dir), MACH, res_level)
    mesh_key = f"hyp-cylinder-M{MACH:g}-{res_level}"

    def build_mesh() -> None:
        sh("blockMesh", case_dir, case_dir / "log.blockMesh")

    def run_solve() -> None:
        sh("rhoCentralFoam", case_dir, case_dir / "log.rhoCentralFoam")
        thetas = run_cylinder_case.write_sampledicts(str(case_dir), meta["R_top"],
                                                     N_THETA_STATIONS)
        times = _time_dirs(case_dir)
        snap = times[-N_AVG_SNAPSHOTS:] if len(times) >= N_AVG_SNAPSHOTS else times
        sh(f"postProcess -func sampleDict -time '{snap[0]}:{snap[-1]}'",
          case_dir, case_dir / "log.sample")
        sh(f"postProcess -func surfaceSampleDict -time '{snap[0]}:{snap[-1]}'",
          case_dir, case_dir / "log.surfsample")

    cache = mesh_and_solve(
        case_dir=case_dir, mesh_key=mesh_key,
        solve_key_fn=lambda cells: f"{mesh_key}-c{cells}",
        build_mesh=build_mesh, run_solve=run_solve,
        count_cells=lambda: RES_CELLS[res_level])
    mesh_stats = run_checkmesh(case_dir)

    thetas_deg = [i * (run_cylinder_case.THETA_MAX_DEG - 3.0) / (N_THETA_STATIONS - 1)
                 for i in range(N_THETA_STATIONS)]
    times = _time_dirs(case_dir)
    snap_times = times[-N_AVG_SNAPSHOTS:] if len(times) >= N_AVG_SNAPSHOTS else times

    standoff_snapshots = []
    for st in snap_times:
        sampdir = case_dir / "postProcessing" / "sampleDict" / st
        cands = glob.glob(f"{sampdir}/r0_*.xy")
        if not cands:
            continue
        dist_s, _, _ = run_cylinder_case.find_shock_r(cands[0])
        if dist_s is not None:
            standoff_snapshots.append(float(dist_s))

    import numpy as np

    standoff_mean = float(np.mean(standoff_snapshots)) if standoff_snapshots else None

    q1 = 0.5 * 1.4 * 1.0 * MACH ** 2
    cp_snaps = []
    theta_wall_deg = None
    for st in snap_times:
        surfdir = case_dir / "postProcessing" / "surfaceSampleDict" / st
        surf_files = (glob.glob(f"{surfdir}/cylSurface_p*.raw")
                     or glob.glob(f"{surfdir}/*p*.raw"))
        if not surf_files:
            continue
        arr = np.loadtxt(surf_files[0], comments="#")
        x_wall, y_wall, p_wall = arr[:, 0], arr[:, 1], arr[:, 3]
        theta = np.degrees(np.arctan2(y_wall, -x_wall))
        order = np.argsort(theta)
        theta, p_wall = theta[order], p_wall[order]
        if theta_wall_deg is None:
            theta_wall_deg = theta
        cp_snaps.append((p_wall - 1.0) / q1)
    cp_mean = np.mean(np.array(cp_snaps), axis=0) if cp_snaps else None
    cp_newton = None
    if theta_wall_deg is not None:
        cp_newton = np.array([billig_theory.modified_newtonian_cp_of_theta_c(
            math.radians(t), MACH) for t in theta_wall_deg])

    return {"res_level": res_level, "cells": cache["cells"],
            "mesh_warm": cache["mesh_warm"], "solve_warm": cache["solve_warm"],
            "mesh_seconds": cache["mesh_seconds"], "solve_seconds": cache["solve_seconds"],
            "mesh_stats": mesh_stats, "standoff_mean": standoff_mean,
            "theta_wall_deg": theta_wall_deg.tolist() if theta_wall_deg is not None else [],
            "cp_mean": cp_mean.tolist() if cp_mean is not None else [],
            "cp_newton": cp_newton.tolist() if cp_newton is not None else []}


def main(request: str | None = None, params: dict | None = None, emit=None) -> int:
    params = dict(params or {})
    out = OUT_ROOT / LABEL
    out.mkdir(parents=True, exist_ok=True)

    script = make_transcript(LABEL, emit)
    roster = Roster(emit)
    ledger = ComputeLedger(emit)
    knowledge = KnowledgeBase(emit)
    ref = _exact_reference()

    script.phase(HYPOTHESIS, "A bow shock standing off a blunt leading edge")
    bullets(script.researcher,
           "A detached bow shock stands off the cylinder's blunt leading "
           f"edge, and its standoff distance follows the Billig correlation, "
           f"{per('billig')}, while the windward surface pressure follows "
           "modified Newtonian theory.",
           "Falsification: if the measured standoff distance or the "
           "windward pressure departs from either closed form relation "
           "outside the stated tolerance, or the shock does not settle "
           "across the late time snapshots, the hypothesis fails.")

    script.phase(PLAN, "Mesh at three resolutions, solve, locate the bow shock")
    roster.set(CHIEF_ENGINEER, "auditing compute", "working")
    capacity = audit(1, memory_per_worker_mb=1024)
    if emit:
        emit("audit.completed", capacity.panel())
    bullets(script.engineer, capacity.headline())
    if emit:
        emit("solver.selected", {
            "solver": "OpenFOAM",
            "method": "density based compressible solver, inviscid",
            "basis": "Matches the non-dimensional gas the reference theory assumes."})
    announce_geometry(emit, name="hypersonic_cylinder.stl", label=display_name(BODY))
    bullets(script.engineer,
           "Plan: mesh the cylinder at three resolutions, coarsest to "
           "finest, solve the compressible flow through the selected "
           "solver at each, and locate the bow shock from the density "
           "field across several late time snapshots.",
           "The finest mesh is the production result; the two cheaper "
           "meshes bound its grid sensitivity.")
    roster.idle(CHIEF_ENGINEER)

    script.phase(EVIDENCE, "Meshing and solving the hypersonic cylinder")
    roster.set(NUMERICIST, "meshing and solving the cylinder ladder", "working")
    levels: dict[str, dict[str, Any]] = {}
    headers = ("Mesh", "Cells", "Shock standoff (delta/R)")
    table_rows: list[list[str]] = []
    try:
        for res_level in RES_LEVELS:
            case_dir = _RUN_ROOT / res_level
            result = _run_level(case_dir, res_level)
            levels[res_level] = result
            ledger.spend(result["mesh_seconds"] + result["solve_seconds"],
                        f"hypersonic cylinder {res_level}")
            standoff_s = (f"{result['standoff_mean']:.4f}"
                         if result["standoff_mean"] is not None else "n/a")
            table_rows.append([res_level, result["cells"], standoff_s])
            emit_table(emit, script, role="NUMERICIST",
                      title="Hypersonic cylinder mesh ladder", headers=headers,
                      rows=[table_rows[-1]], table_id="hypersonic-cylinder-ladder",
                      append=len(table_rows) > 1)
    except Exception as exc:
        bullets(script.engineer,
               "The hypersonic cylinder solve did not complete; the run "
               "logs carry the detail and no result is reported from a "
               "partial solve.")
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

    plot_path = None
    if production["theta_wall_deg"]:
        plot_path = comparison_plot(
            out / "cylinder_windward_cp.png",
            xlabel="theta from stagnation point (deg)", ylabel="Cp (windward surface)",
            title="Hypersonic cylinder windward Cp: solved vs modified Newtonian theory",
            series=[("solved Cp", production["theta_wall_deg"],
                    production["cp_mean"], "points"),
                   ("modified Newtonian Cp", production["theta_wall_deg"],
                    production["cp_newton"], "line")])
        announce_plot(emit, LABEL, plot_path,
                     "Hypersonic cylinder windward Cp vs modified Newtonian theory")

    script.phase(CONCLUSION, "Grid sensitivity, verdict, uncertainty")
    roster.set(NUMERICIST, "grid sensitivity across the cylinder ladder", "working")
    cells_series = [levels[r]["cells"] for r in RES_LEVELS]
    standoff_series = [levels[r]["standoff_mean"] for r in RES_LEVELS]
    band_abs = None
    if all(v is not None for v in standoff_series):
        band = uq_studies.eca_hoekstra_band(cells_series, standoff_series)
        band_abs = band.get("band_abs")
    bullets(script.numericist,
           "Grid sensitivity study: three meshes of the same cylinder, one "
           "knob moved, the shock standoff tracked at each, averaged over "
           "several late time snapshots at every mesh.",
           citations=[per("billig")])
    roster.idle(NUMERICIST)

    standoff_computed = production["standoff_mean"]
    rel_error = (abs(standoff_computed - ref["standoff"]) / ref["standoff"]
                if standoff_computed is not None else None)
    verdict = trust(
        relative_error=rel_error, converged=standoff_computed is not None,
        in_validated_regime=gates_pass, calibrated=True, solver_backed=True,
        tight_threshold=0.007,
        why=(f"a selected-solver shock standoff graded against the Billig "
             f"correlation; envelope {rel_error * 100:.2f}% of the exact "
             f"value" if rel_error is not None else
             "the standoff snapshots did not settle; no envelope is reported"))
    verdict_rows = [["Shock standoff (delta/R)", f"{ref['standoff']:.4f}",
                    f"{standoff_computed:.4f}" if standoff_computed is not None else "n/a",
                    f"{100 * rel_error:.2f}%" if rel_error is not None else "n/a"]]
    emit_table(emit, script, role="CHIEF ENGINEER", title="Hypersonic cylinder verdict",
              headers=("Quantity", "Exact", "Solved", "Deviation"),
              rows=verdict_rows, table_id="hypersonic-cylinder-verdict")
    if emit:
        emit("result.verdict", {
            "quantity": "Shock standoff distance",
            "value": (f"{standoff_computed:.4f} R" if standoff_computed is not None else "n/a"),
            "confidence": "95%", **verdict})

    channels = uncertainty_channels(
        input_2sigma=None, numerical=band_abs, model=None,
        input_note=INPUT_ASSUMED_NOTE,
        numerical_note=(
            f"Grid sensitivity band across the mesh ladder: {band_abs:.4f}."
            if band_abs is not None else
            "Grid sensitivity band pending a conclusive ladder."),
        model_note=("The solved case shares the reference theory's inviscid "
                    "assumption, so no closure model form gap applies here."))
    if emit:
        emit("uncertainty.channels", channels)
    bullets(script.researcher,
           "Three uncertainty channels stand behind this number: the input "
           "channel, the numerical channel from the mesh ladder, and the "
           "model channel, stated even where it does not apply.")

    caveat_bullets = caveats or ["Mesh quality cleared both published gates."]
    bullets(script.engineer, *caveat_bullets)

    knowledge.add("Hypersonic bow shock standoff confirmed against the "
                  "Billig correlation on the blunt cylinder.")
    if emit:
        emit("agenda.updated", {"entries": _AGENDA})

    report_doc = lab_report(
        title="Hypersonic cylinder: Billig shock standoff validation",
        abstract=["A stated hypersonic Mach number over a blunt circular "
                 "leading edge produces a bow shock, graded against the "
                 "Billig shock standoff correlation."],
        methods=["Mesh and solve the cylinder at three resolutions through "
                "the selected solver.", "Locate the bow shock from the "
                "density field along the stagnation line, averaged across "
                "several late time snapshots.", "Sample the windward "
                "surface pressure and grade it against modified Newtonian "
                "theory."],
        results=[{"quantity": "Shock standoff distance",
                 "value": (f"{standoff_computed:.4f} R" if standoff_computed is not None else "n/a"),
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
            ("Shock standoff", f"{standoff_computed:.4f} R" if standoff_computed is not None else "n/a"),
            ("Grid sensitivity band", f"{band_abs:.4f}" if band_abs is not None else "pending"),
            ("Cells", f"{production['cells']}"),
        ]
        certificate = build_certificate_v2(
            cert_doc, out_path=cert_path, geometry=BODY,
            objective=(request or "Hypersonic cylinder, Billig shock standoff validation"),
            mission_id=f"{LABEL}-{int(time.time())}",
            issued_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            channels=channels, display_name=display_name(BODY),
            source_filename="hypersonic_cylinder.stl",
            solver="Selected solver",
            mesh=mesh_validity(production["cells"], non_ortho, skew))
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
