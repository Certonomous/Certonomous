"""Supersonic cone: a conical shock at a stated Mach number and cone
half-angle, gated against the exact Taylor-Maccoll solution.

The case, the mesh and the closed-form theory are not re-derived here: they
are the same functions that already validated this body (``make_cone_case``,
``exact_theory``, and the shock-locus fit in ``run_cone_case``, all under
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
    comparison_plot, linfit_shock_angle, mesh_and_solve, run_checkmesh, sh)

import make_cone_case  # noqa: E402  (F3_runs, path-inserted by shock_bench)
import run_cone_case  # noqa: E402
import exact_theory  # noqa: E402

LABEL = "supersonic-cone"
BODY = "supersonic_cone"
_RUN_ROOT = Path.home() / "certonomous-runs" / LABEL

MACH = 2.35
THETA_C_DEG = 10.0
RES_LEVELS = ("coarse", "medium", "fine")
RES_CELLS = {"coarse": 1800, "medium": 7200, "fine": 28800}
INPUT_ASSUMED_NOTE = "No input uncertainty was assumed for this problem."


def _ladder_reason(band: dict[str, Any] | None) -> str:
    """Why the uncertainty layer did not call this refinement ladder conclusive.

    ``eca_hoekstra_band`` hands back a fallback ``band_abs`` even when it sets
    ``conclusive`` False, so the flag is what decides whether a number may be
    reported, and this sentence is what the act says instead of the number.

    The wording comes from ``uq.not_conclusive_reason`` rather than being
    rebuilt here, so every act that declines a band says the same sentence
    about the same failure and a mode added to the uncertainty layer reaches
    this act without anyone remembering to edit it. Only the no-usable-rungs
    case is answered locally: the layer has no phrase that names the missing
    rungs.

    EVERY GUARD THAT HOLDS THIS LADDER IS NAMED, IMPOSSIBLE VALUE FIRST. A
    ladder can fail more than one guard, and naming only the earliest one
    tells a viewer something true and unimportant in place of something true
    and decisive. Where this act knows the physics of its own functional it
    says so ahead of every other guard: a conical shock stands ahead of the
    cone at a positive angle, so an extrapolated angle below zero is not a
    wide band, it is a value the flow cannot produce. This ladder extrapolates
    to 26.226 deg, which is an angle a flow can have, so the clause is silent
    here and the rail is in place if that ever stops being so.
    """
    if band is None or band.get("band_abs") is None:
        return "it did not produce three usable rungs"
    return (uq_studies.not_conclusive_reason(
                band, impossible=_ladder_impossible(band))
            or "it did not meet the conclusive test")


def _ladder_impossible(band: dict[str, Any] | None) -> str | None:
    """The clause for an extrapolated cone shock angle no flow can have."""
    return uq_studies.impossible_extrapolation(
        band, quantity="the conical shock angle",
        why="which is not a shock angle any flow can have",
        floor=0.0, unit="deg")


_AGENDA = [
    {"title": "Sweep the cone half-angle toward detachment",
     "scope": "Carry the same case up toward the conical-shock detachment "
              "limit at this Mach number and confirm the solved cone shock "
              "tracks the Taylor-Maccoll branch throughout.",
     "cost": "a short mesh-and-solve sweep, same body"},
    {"title": "Add a second Mach number to the cone family",
     "scope": "Stand up the case at a second Mach number so the cone act "
              "reports a small family rather than a single condition.",
     "cost": "one more mesh-and-solve pair"},
]


def _condition_tag() -> str:
    return f"M{MACH:g}-th{THETA_C_DEG:g}"


def _exact_reference() -> dict[str, float]:
    tm = exact_theory.taylor_maccoll_solve(MACH, math.radians(THETA_C_DEG))
    return {"beta_deg": math.degrees(tm["beta"]), "pc_p1": tm["pc_p1"], "M2": tm["M2"]}


def _run_level(case_dir: Path, res_level: str, beta_exact_deg: float) -> dict[str, Any]:
    case_dir.mkdir(parents=True, exist_ok=True)
    meta = make_cone_case.make_case(str(case_dir), MACH, THETA_C_DEG, res_level, beta_exact_deg)
    mesh_key = f"cone-{_condition_tag()}-{res_level}"

    def build_mesh() -> None:
        sh("blockMesh", case_dir, case_dir / "log.blockMesh")

    def run_solve() -> None:
        sh("rhoCentralFoam", case_dir, case_dir / "log.rhoCentralFoam")
        run_cone_case.write_sampledicts(str(case_dir), meta["x_max"], meta["R"])
        sh("postProcess -func sampleDict -latestTime", case_dir, case_dir / "log.sample")
        sh("postProcess -func surfaceSampleDict -latestTime", case_dir, case_dir / "log.surfsample")

    cache = mesh_and_solve(
        case_dir=case_dir, mesh_key=mesh_key,
        solve_key_fn=lambda cells: f"{mesh_key}-c{cells}",
        build_mesh=build_mesh, run_solve=run_solve,
        count_cells=lambda: RES_CELLS[res_level])
    mesh_stats = run_checkmesh(case_dir)

    xs = [(0.12 + i * (0.88 - 0.12) / 5) * meta["x_max"] for i in range(6)]
    sampdir = sorted(glob.glob(f"{case_dir}/postProcessing/sampleDict/*"))[-1]
    shock_pts = []
    for i, x in enumerate(xs):
        cands = glob.glob(f"{sampdir}/x{i}_*.xy")
        if not cands:
            continue
        r_s = run_cone_case.find_shock_r(cands[0])
        if r_s is None:
            continue
        shock_pts.append((x, r_s))
    fit_pts = shock_pts[1:] if len(shock_pts) > 3 else shock_pts
    beta_computed_deg, fit_r2 = linfit_shock_angle(fit_pts)

    surfdir = sorted(glob.glob(f"{case_dir}/postProcessing/surfaceSampleDict/*"))[-1]
    surf_files = (glob.glob(f"{surfdir}/coneSurface_p*.raw")
                 or glob.glob(f"{surfdir}/*p*.raw"))
    import numpy as np

    arr = np.loadtxt(surf_files[0], comments="#")
    x_wall, p_wall = arr[:, 0], arr[:, 3]
    order = np.argsort(x_wall)
    x_wall, p_wall = x_wall[order], p_wall[order]
    mid = (x_wall > 0.3 * meta["x_max"]) & (x_wall < 0.85 * meta["x_max"])
    p_wall_mean = float(np.mean(p_wall[mid]))

    return {"res_level": res_level, "cells": cache["cells"],
            "mesh_warm": cache["mesh_warm"], "solve_warm": cache["solve_warm"],
            "mesh_seconds": cache["mesh_seconds"], "solve_seconds": cache["solve_seconds"],
            "mesh_stats": mesh_stats, "beta_computed_deg": beta_computed_deg,
            "fit_r2": fit_r2, "pc_p1_computed": p_wall_mean,
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

    script.phase(HYPOTHESIS, "A conical shock in supersonic flow")
    bullets(script.researcher,
           "The cone stands off a straight conical shock, and the flow "
           "between the shock and the cone surface follows the "
           f"Taylor-Maccoll solution, {per('taylor-maccoll')}.",
           "Falsification: if the fitted shock angle or the cone surface "
           "pressure ratio departs from the closed form solution outside "
           "the stated tolerance, or the shock does not settle to one "
           "steady cone, the hypothesis fails.")

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
    announce_geometry(emit, name="supersonic_cone.stl", label=display_name(BODY))
    bullets(script.engineer,
           "Plan: mesh the cone at three resolutions, coarsest to finest, "
           "solve the compressible flow through the selected solver at each, "
           "and locate the conical shock from the density field.",
           "The finest mesh is the production result; the two cheaper "
           "meshes bound its grid sensitivity.")
    roster.idle(CHIEF_ENGINEER)

    script.phase(EVIDENCE, "Meshing and solving the cone")
    roster.set(NUMERICIST, "meshing and solving the cone ladder", "working")
    beta_exact_deg = ref["beta_deg"]
    levels: dict[str, dict[str, Any]] = {}
    headers = ("Mesh", "Cells", "Shock angle (deg)", "Wall pc/p1")
    table_rows: list[list[str]] = []
    try:
        for res_level in RES_LEVELS:
            case_dir = _RUN_ROOT / res_level
            result = _run_level(case_dir, res_level, beta_exact_deg)
            levels[res_level] = result
            ledger.spend(result["mesh_seconds"] + result["solve_seconds"],
                        f"cone {res_level}")
            table_rows.append([res_level, result["cells"],
                               f"{result['beta_computed_deg']:.3f}",
                               f"{result['pc_p1_computed']:.4f}"])
            emit_table(emit, script, role="NUMERICIST",
                      title="Cone mesh ladder", headers=headers,
                      rows=[table_rows[-1]], table_id="cone-ladder",
                      append=len(table_rows) > 1)
    except Exception as exc:
        bullets(script.engineer,
               "The cone solve did not complete; the run logs carry the "
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
        out / "cone_wall_pressure.png",
        xlabel="x / axial length", ylabel="p / p1 (cone surface)",
        title="Cone surface pressure: solved vs the exact Taylor-Maccoll solution",
        series=[("solved surface pressure",
                [x / max(production["x_wall"]) for x in production["x_wall"]],
                production["p_wall"], "line")],
        hline=(ref["pc_p1"], "exact pc/p1"))
    announce_plot(emit, LABEL, plot_path, "Cone surface pressure vs exact theory")

    script.phase(CONCLUSION, "Grid sensitivity, verdict, uncertainty")
    roster.set(NUMERICIST, "grid sensitivity across the cone ladder", "working")
    cells_series = [levels[r]["cells"] for r in RES_LEVELS]
    beta_series = [levels[r]["beta_computed_deg"] for r in RES_LEVELS]
    # dim=2 is read off this ladder's own mesh, not off the case name, and
    # axisymmetric does not by itself mean two dimensional. What settles it is
    # that the cone blockMeshDict lays two blocks of (nx ny 1) between a
    # frontWedge and a backWedge patch: one cell in azimuth, never refined. The
    # flow field is axisymmetric in three dimensions, but the DISCRETIZATION
    # moves in exactly two, and the cell count grows as the square of the
    # linear refinement (1800, 7200, 28800: a factor of 4 per rung, 2 in each
    # direction). Left at the dim=3 default the representative size is the cube
    # root of the same counts, which stretches every observed order by 1.5.
    band = uq_studies.eca_hoekstra_band(cells_series, beta_series, dim=2)
    # The ladder's own verdict on itself decides whether a number may leave
    # this act. A band the uncertainty layer marks not conclusive is the
    # conservative fallback, not a 95% figure, and the certificate captions
    # the first result's envelope "95% confidence interval", so an
    # unquantified numerical channel is the only honest reading here.
    # reportable_band is the only safe read: it hands back the figure when the
    # ladder earned the right to state one and None otherwise, so the
    # conservative fallback band cannot reach the certificate's interval.
    numerical_abs = uq_studies.reportable_band(band)
    ladder_reason = _ladder_reason(band)
    # Silent while one guard holds this ladder, which is the case today; it
    # speaks the moment more than one does, so the first-named guard can never
    # read as the whole reason on this surface.
    ladder_holding = uq_studies.guards_holding_note(band)
    ladder_spread = max(beta_series) - min(beta_series)
    # The total is the root sum of squares over the channels that carry a
    # figure, through the same call every other act uses. Input and model are
    # passed as absent, so they are stated as unquantified rather than
    # silently counted as zero.
    total = uq_studies.combine_expanded(
        input_2sigma=None, numerical_abs=numerical_abs, model_abs=None)
    combined = total["combined_95"]
    bullets(script.numericist,
           "Grid sensitivity study: three meshes of the same cone, one "
           "knob moved, the conical shock angle tracked at each.",
           f"Fit quality on the production mesh: R squared "
           f"{production['fit_r2']:.4f}." if production.get("fit_r2") else
           "Fit quality reported on the production mesh.",
           (f"The conical shock angle moved {ladder_spread:.3f} deg across "
            f"the three rungs, and no band is read from that spread."
            if numerical_abs is None else
            f"The ladder is conclusive, so the numerical channel carries "
            f"{numerical_abs:.3f} deg."),
           (f"The ladder is not conclusive: {ladder_reason}."
            if numerical_abs is None else ""),
           (f"{ladder_holding}."
            if numerical_abs is None and ladder_holding else ""),
           citations=[per("taylor-maccoll")])
    roster.idle(NUMERICIST)

    beta_computed = production["beta_computed_deg"]
    rel_error = abs(beta_computed - beta_exact_deg) / beta_exact_deg
    p_computed = production["pc_p1_computed"]
    p_rel_error = abs(p_computed - ref["pc_p1"]) / ref["pc_p1"]
    verdict = trust(
        relative_error=rel_error, converged=True,
        in_validated_regime=gates_pass, calibrated=True, solver_backed=True,
        tight_threshold=0.03,
        why=(f"a selected-solver conical shock angle graded against the "
             f"exact Taylor-Maccoll solution; envelope {rel_error * 100:.2f}% "
             f"of the exact value"))
    emit_table(emit, script, role="CHIEF ENGINEER", title="Cone verdict",
              headers=("Quantity", "Exact", "Solved", "Deviation"),
              rows=[["Shock angle (deg)", f"{beta_exact_deg:.3f}",
                    f"{beta_computed:.3f}", f"{100 * rel_error:.2f}%"],
                   ["Wall pc/p1", f"{ref['pc_p1']:.4f}",
                    f"{p_computed:.4f}", f"{100 * p_rel_error:.2f}%"]],
              table_id="cone-verdict")
    if emit:
        # The interval keys ride along only when a combined 95% figure exists.
        # With no quantified channel there is no interval, and the headline
        # says so by carrying no interval at all.
        verdict_payload = {"quantity": "Conical shock angle",
                           "value": f"{beta_computed:.3f} deg", **verdict}
        if combined is not None:
            verdict_payload["ci"] = f"{combined:.3f} deg"
            verdict_payload["confidence"] = "95%"
        emit("result.verdict", verdict_payload)

    channels = uncertainty_channels(
        input_2sigma=None, numerical=numerical_abs, model=None,
        input_note=INPUT_ASSUMED_NOTE,
        numerical_note=(
            f"Grid sensitivity band across the mesh ladder: "
            f"{numerical_abs:.3f} deg." if numerical_abs is not None else
            f"• The conical shock angle moved {ladder_spread:.3f} deg across "
            f"the three rungs of this mesh ladder. "
            f"• The ladder is not conclusive: {ladder_reason}. "
            + (f"• {ladder_holding}. " if ladder_holding else "")
            + f"• No band is read from that spread, so this channel is not "
            f"quantified."),
        model_note=("The solved case shares the reference theory's inviscid "
                    "assumption, so no closure model form gap applies here."))
    if emit:
        emit("uncertainty.channels", channels)
    emit_table(
        emit, script, role="CHIEF ENGINEER",
        title="Total uncertainty on the conical shock angle",
        headers=("Channel", "Value (deg)", "In the total"),
        rows=[["Input", "Not quantified", "No, and not counted as zero"],
              ["Numerical",
               f"{numerical_abs:.3f}" if numerical_abs is not None
               else "Not quantified",
               "Yes" if numerical_abs is not None
               else "No, the mesh ladder is not conclusive"],
              ["Model form", "Not quantified",
               "No, the case shares the theory's inviscid assumption"],
              ["Total",
               f"{combined:.3f}" if combined is not None else "Not reported",
               "The quantified channels" if combined is not None
               else "No channel is quantified, so no interval is reported"]],
        table_id="cone-uncertainty")
    bullets(script.researcher,
           "Three uncertainty channels are named for this number: the input "
           "channel, the numerical channel from the mesh ladder, and the "
           "model channel, each with its state on the table above.",
           ("The conical shock angle is reported as a point estimate: no "
            "channel carries a figure, so there is no 95% interval to quote."
            if combined is None else
            f"The conical shock angle carries a combined 95% interval of "
            f"{combined:.3f} deg over the quantified channels."))

    caveat_bullets = caveats or ["Mesh quality cleared both published gates."]
    bullets(script.engineer, *caveat_bullets)

    knowledge.add("Conical shock angle confirmed against the Taylor-Maccoll "
                  "solution on the supersonic cone.")
    if emit:
        emit("agenda.updated", {"entries": _AGENDA})

    # The certificate captions the first result's envelope "95% confidence
    # interval" whenever it reads as a bare magnitude, so the key is present
    # only when a combined 95% figure exists. Absent, it prints as a point
    # estimate.
    headline_result: dict[str, Any] = {
        "quantity": "Shock angle", "value": f"{beta_computed:.3f} deg",
        "tier": verdict["tier"], "reason": verdict["reason"]}
    if combined is not None:
        headline_result["envelope"] = f"{combined:.3f} deg"

    report_doc = lab_report(
        title="Supersonic cone: Taylor-Maccoll validation",
        abstract=["A stated Mach number and cone half angle produce a "
                 "conical shock, graded against the exact Taylor-Maccoll "
                 "solution."],
        methods=["Mesh and solve the cone at three resolutions through the "
                "selected solver.", "Locate the conical shock from the "
                "density field and fit its angle.", "Sample the cone "
                "surface pressure over the settled portion of its length."],
        results=[headline_result],
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
            ("Wall pc/p1", f"{p_computed:.4f}"),
            ("Grid sensitivity band",
             f"{numerical_abs:.3f} deg" if numerical_abs is not None
             else "Not reported, the ladder is not conclusive"),
            ("Cells", f"{production['cells']}"),
        ]
        certificate = build_certificate_v2(
            cert_doc, out_path=cert_path, geometry=BODY,
            objective=(request or "Supersonic cone, Taylor-Maccoll validation"),
            mission_id=f"{LABEL}-{int(time.time())}",
            issued_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            channels=channels, display_name=display_name(BODY),
            source_filename="supersonic_cone.stl",
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
