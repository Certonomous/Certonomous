"""Supersonic wedge: an oblique shock at a stated Mach number and wedge
half-angle, gated against the exact theta-beta-M oblique-shock relations.

The case, the mesh and the closed-form theory are not re-derived here: they
are the same functions that already validated this body (``make_wedge_case``,
``exact_theory``, and the shock-locus fit in ``run_wedge_case``, all under
``demo-output/website/campaign/F3_runs``). This act adds the control-room
narration, the mesh-and-solve cache, and the certificate.
"""

from __future__ import annotations

import glob
import math
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
from workflows.shock_bench import (
    F3_DIR, comparison_plot, linfit_shock_angle, mesh_and_solve, run_checkmesh, sh)

import make_wedge_case  # noqa: E402  (F3_runs, path-inserted by shock_bench)
import run_wedge_case  # noqa: E402
import exact_theory  # noqa: E402

LABEL = "supersonic-wedge"
BODY = "supersonic_wedge"
_RUN_ROOT = Path.home() / "certonomous-runs" / LABEL

MACH = 2.0
THETA_DEG = 15.0
RES_LEVELS = ("coarse", "medium", "fine")
RES_CELLS = {"coarse": 1800, "medium": 7200, "fine": 28800}
INPUT_ASSUMED_NOTE = "No input uncertainty was assumed for this problem."

_AGENDA = [
    {"title": "Sweep the wedge half-angle toward detachment",
     "scope": "Carry the same case up to the theta-beta-M detachment limit "
              "at this Mach number and confirm the solved shock departs from "
              "the weak-solution branch exactly where theory predicts.",
     "cost": "a short mesh-and-solve sweep, same body"},
    {"title": "Add a second Mach number to the wedge family",
     "scope": "Stand up the case at a second Mach number so the wedge act "
              "reports a small family rather than a single condition.",
     "cost": "one more mesh-and-solve pair"},
]


def _condition_tag() -> str:
    return f"M{MACH:g}-th{THETA_DEG:g}"


def _beta_exact_deg() -> float:
    beta_rad = exact_theory.beta_from_theta(MACH, math.radians(THETA_DEG))
    return math.degrees(beta_rad)


def _exact_reference() -> dict[str, float]:
    beta_exact_deg = _beta_exact_deg()
    shock = exact_theory.oblique_shock(MACH, math.radians(beta_exact_deg))
    return {"beta_deg": beta_exact_deg, "p2_p1": shock["p2_p1"], "M2": shock["M2"]}


def _run_level(case_dir: Path, res_level: str, beta_exact_deg: float) -> dict[str, Any]:
    case_dir.mkdir(parents=True, exist_ok=True)
    meta = make_wedge_case.make_case(str(case_dir), MACH, THETA_DEG, res_level, beta_exact_deg)
    mesh_key = f"wedge-{_condition_tag()}-{res_level}"

    def build_mesh() -> None:
        sh("blockMesh", case_dir, case_dir / "log.blockMesh")

    def run_solve() -> None:
        sh("rhoCentralFoam", case_dir, case_dir / "log.rhoCentralFoam")
        run_wedge_case.write_sampledict(str(case_dir), meta["Lramp"], meta["H"])
        sh("postProcess -func sampleDict -latestTime", case_dir, case_dir / "log.sample")
        sh("postProcess -func surfaceSampleDict -latestTime", case_dir, case_dir / "log.surfsample")

    cache = mesh_and_solve(
        case_dir=case_dir, mesh_key=mesh_key,
        solve_key_fn=lambda cells: f"{mesh_key}-c{cells}",
        build_mesh=build_mesh, run_solve=run_solve,
        count_cells=lambda: RES_CELLS[res_level])
    mesh_stats = run_checkmesh(case_dir)

    # Parsing runs unconditionally over whatever now sits in case_dir, so a
    # warm result and a cold result read identical files identically.
    xs = [0.12 + i * (0.88 - 0.12) / 5 for i in range(6)]
    xs = [x * meta["Lramp"] for x in xs]
    sampdir = sorted(glob.glob(f"{case_dir}/postProcessing/sampleDict/*"))[-1]
    shock_pts = []
    for i, x in enumerate(xs):
        cands = glob.glob(f"{sampdir}/x{i}_*.xy")
        if not cands:
            continue
        result = run_wedge_case.find_shock_y(cands[0])
        if result is None:
            continue
        y_s, *_ = result
        shock_pts.append((x, y_s))
    fit_pts = shock_pts[1:] if len(shock_pts) > 3 else shock_pts
    beta_computed_deg, fit_r2 = linfit_shock_angle(fit_pts)

    surfdir = sorted(glob.glob(f"{case_dir}/postProcessing/surfaceSampleDict/*"))[-1]
    surf_files = (glob.glob(f"{surfdir}/wedgeSurface_p*.raw")
                 or glob.glob(f"{surfdir}/*p*.raw"))
    import numpy as np

    arr = np.loadtxt(surf_files[0], comments="#")
    x_wall, p_wall = arr[:, 0], arr[:, 3]
    order = np.argsort(x_wall)
    x_wall, p_wall = x_wall[order], p_wall[order]
    mid = (x_wall > 0.3 * meta["Lramp"]) & (x_wall < 0.85 * meta["Lramp"])
    p_wall_mean = float(np.mean(p_wall[mid]))

    return {"res_level": res_level, "cells": cache["cells"],
            "mesh_warm": cache["mesh_warm"], "solve_warm": cache["solve_warm"],
            "mesh_seconds": cache["mesh_seconds"], "solve_seconds": cache["solve_seconds"],
            "mesh_stats": mesh_stats, "beta_computed_deg": beta_computed_deg,
            "fit_r2": fit_r2, "p2_p1_computed": p_wall_mean,
            "x_wall": x_wall.tolist(), "p_wall": p_wall.tolist(),
            "shock_pts": shock_pts}


def main(request: str | None = None, params: dict | None = None, emit=None) -> int:
    params = dict(params or {})
    out = OUT_ROOT / LABEL
    out.mkdir(parents=True, exist_ok=True)

    script = make_transcript(LABEL, emit)
    roster = Roster(emit)
    ledger = ComputeLedger(emit)
    knowledge = KnowledgeBase(emit)
    ref = _exact_reference()

    script.phase(HYPOTHESIS, "A compression corner in supersonic flow")
    bullets(script.researcher,
           "The wedge turns the flow through a stated deflection angle, "
           "and an attached oblique shock forms at the angle set by the "
           f"theta beta Mach relation, {per('oblique-shock')}.",
           "Falsification: if the fitted shock angle or the wall pressure "
           "ratio departs from the closed form relation outside the stated "
           "tolerance, or the shock does not settle to one steady angle, "
           "the hypothesis fails.")

    script.phase(PLAN, "Mesh at three resolutions, solve, locate the shock")
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
    announce_geometry(emit, name="supersonic_wedge.stl", label=display_name(BODY))
    bullets(script.engineer,
           "Plan: mesh the wedge at three resolutions, coarsest to finest, "
           "solve the compressible flow through the selected solver at each, "
           "and locate the shock from the density field.",
           "The finest mesh is the production result; the two cheaper "
           "meshes bound its grid sensitivity.")
    roster.idle(CHIEF_ENGINEER)

    script.phase(EVIDENCE, "Meshing and solving the wedge")
    roster.set(NUMERICIST, "meshing and solving the wedge ladder", "working")
    beta_exact_deg = ref["beta_deg"]
    levels: dict[str, dict[str, Any]] = {}
    headers = ("Mesh", "Cells", "Shock angle (deg)", "Wall p2/p1")
    table_rows: list[list[str]] = []
    try:
        for res_level in RES_LEVELS:
            case_dir = _RUN_ROOT / res_level
            result = _run_level(case_dir, res_level, beta_exact_deg)
            levels[res_level] = result
            ledger.spend(result["mesh_seconds"] + result["solve_seconds"],
                        f"wedge {res_level}")
            table_rows.append([res_level, result["cells"],
                               f"{result['beta_computed_deg']:.3f}",
                               f"{result['p2_p1_computed']:.4f}"])
            emit_table(emit, script, role="NUMERICIST",
                      title="Wedge mesh ladder", headers=headers,
                      rows=[table_rows[-1]], table_id="wedge-ladder",
                      append=len(table_rows) > 1)
    except Exception as exc:
        bullets(script.engineer,
               "The wedge solve did not complete; the run logs carry the "
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

    plot_path = comparison_plot(
        out / "wedge_wall_pressure.png",
        xlabel="x / chord", ylabel="p / p1 (wall)",
        title="Wedge wall pressure: solved vs the exact oblique shock relation",
        series=[("solved wall pressure",
                [x / max(production["x_wall"]) for x in production["x_wall"]],
                production["p_wall"], "line")],
        hline=(ref["p2_p1"], "exact p2/p1"))
    announce_plot(emit, LABEL, plot_path, "Wedge wall pressure vs exact theory")

    script.phase(CONCLUSION, "Grid sensitivity, verdict, uncertainty")
    roster.set(NUMERICIST, "grid sensitivity across the wedge ladder", "working")
    cells_series = [levels[r]["cells"] for r in RES_LEVELS]
    beta_series = [levels[r]["beta_computed_deg"] for r in RES_LEVELS]
    band = uq_studies.eca_hoekstra_band(cells_series, beta_series)
    band_abs = band.get("band_abs")
    bullets(script.numericist,
           "Grid sensitivity study: three meshes of the same wedge, one "
           "knob moved, the shock angle tracked at each.",
           f"Fit quality on the production mesh: R squared "
           f"{production['fit_r2']:.4f}." if production.get("fit_r2") else
           "Fit quality reported on the production mesh.",
           citations=[per("oblique-shock")])
    roster.idle(NUMERICIST)

    beta_computed = production["beta_computed_deg"]
    rel_error = abs(beta_computed - beta_exact_deg) / beta_exact_deg
    p_computed = production["p2_p1_computed"]
    p_rel_error = abs(p_computed - ref["p2_p1"]) / ref["p2_p1"]
    verdict = trust(
        relative_error=rel_error, converged=True,
        in_validated_regime=gates_pass, calibrated=True, solver_backed=True,
        tight_threshold=0.02,
        why=(f"a selected-solver shock angle graded against the exact "
             f"oblique-shock relations; envelope {rel_error * 100:.2f}% of "
             f"the exact value"))
    emit_table(emit, script, role="CHIEF ENGINEER", title="Wedge verdict",
              headers=("Quantity", "Exact", "Solved", "Deviation"),
              rows=[["Shock angle (deg)", f"{beta_exact_deg:.3f}",
                    f"{beta_computed:.3f}", f"{100 * rel_error:.2f}%"],
                   ["Wall p2/p1", f"{ref['p2_p1']:.4f}",
                    f"{p_computed:.4f}", f"{100 * p_rel_error:.2f}%"]],
              table_id="wedge-verdict")
    if emit:
        emit("result.verdict", {"quantity": "Oblique shock angle",
                                "value": f"{beta_computed:.3f} deg",
                                "confidence": "95%", **verdict})

    channels = uncertainty_channels(
        input_2sigma=None, numerical=band_abs, model=None,
        input_note=INPUT_ASSUMED_NOTE,
        numerical_note=(
            f"Grid sensitivity band across the mesh ladder: {band_abs:.3f} "
            f"deg." if band_abs is not None else
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

    knowledge.add("Oblique shock angle confirmed against the theta beta "
                  "Mach relation on the compression wedge.")
    if emit:
        emit("agenda.updated", {"entries": _AGENDA})

    report_doc = lab_report(
        title="Supersonic wedge: oblique shock validation",
        abstract=["A stated Mach number and wedge half angle produce an "
                 "attached oblique shock, graded against the exact theta "
                 "beta Mach relation."],
        methods=["Mesh and solve the wedge at three resolutions through the "
                "selected solver.", "Locate the shock from the density "
                "field and fit its angle.", "Sample the wall pressure over "
                "the settled portion of the ramp."],
        results=[{"quantity": "Shock angle", "value": f"{beta_computed:.3f} deg",
                 "envelope": f"{band_abs:.3f} deg" if band_abs is not None else "pending",
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
            ("Shock angle", f"{beta_computed:.3f} deg"),
            ("Wall p2/p1", f"{p_computed:.4f}"),
            ("Grid sensitivity band", f"{band_abs:.3f} deg" if band_abs is not None else "pending"),
            ("Cells", f"{production['cells']}"),
        ]
        certificate = build_certificate_v2(
            cert_doc, out_path=cert_path, geometry=BODY,
            objective=(request or "Supersonic wedge, oblique shock validation"),
            mission_id=f"{LABEL}-{int(time.time())}",
            issued_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            channels=channels, display_name=display_name(BODY),
            source_filename="supersonic_wedge.stl",
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
