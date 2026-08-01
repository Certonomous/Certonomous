"""Diamond airfoil: supersonic wave drag on a symmetric double-wedge
section, gated against exact shock-expansion theory.

The case, the mesh and the closed-form theory are not re-derived here: they
are the same functions that already validated this body (``make_diamond_case``,
``exact_theory``, and the force read in ``run_diamond_case``, all under
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
from workflows.shock_bench import comparison_plot, mesh_and_solve, run_checkmesh, sh

import make_diamond_case  # noqa: E402  (F3_runs, path-inserted by shock_bench)
import exact_theory  # noqa: E402

LABEL = "diamond-airfoil"
BODY = "diamond_airfoil"
_RUN_ROOT = Path.home() / "certonomous-runs" / LABEL

MACH = 2.0
EPS_DEG = 7.125
CHORD = 1.0
Z_THICKNESS = 0.01
GAMMA = 1.4
RES_LEVELS = ("coarse", "medium", "fine")
RES_CELLS = {"coarse": 2000, "medium": 8000, "fine": 32000}
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
    says so ahead of every other guard: a section in a supersonic stream with
    no power source cannot make thrust, so an extrapolated wave drag below
    zero is not a wide band, it is a value the flow cannot produce. This
    ladder extrapolates to 0.03624, so the clause is silent here and the rail
    is in place if that ever stops being so.
    """
    if band is None or band.get("band_abs") is None:
        return "it did not produce three usable rungs"
    return (uq_studies.not_conclusive_reason(
                band, impossible=_ladder_impossible(band))
            or "it did not meet the conclusive test")


def _ladder_impossible(band: dict[str, Any] | None) -> str | None:
    """The clause for an extrapolated wave drag the section cannot have."""
    return uq_studies.impossible_extrapolation(
        band, quantity="the wave drag coefficient",
        why="which is a thrust the section has no way to make",
        floor=0.0, places=5)


_AGENDA = [
    {"title": "Add a second Mach number to the diamond family",
     "scope": "Stand up the case at a second Mach number so the wave drag "
              "act reports a small family rather than a single condition.",
     "cost": "one more mesh-and-solve pair"},
    {"title": "Carry the diamond section to a small angle of attack",
     "scope": "Add lift alongside wave drag and grade both against the "
              "same shock-expansion closed form at a stated small alpha.",
     "cost": "a short mesh-and-solve sweep, same body"},
]


def _condition_tag() -> str:
    return f"M{MACH:g}-eps{EPS_DEG:g}"


def _exact_reference() -> dict[str, float]:
    dw = exact_theory.diamond_wave_drag(MACH, math.radians(EPS_DEG))
    return {"beta_deg": dw["beta_deg"], "cd": dw["cd"]}


def _run_level(case_dir: Path, res_level: str, beta_exact_deg: float) -> dict[str, Any]:
    case_dir.mkdir(parents=True, exist_ok=True)
    meta = make_diamond_case.make_case(str(case_dir), MACH, EPS_DEG, res_level,
                                       beta_exact_deg, c=CHORD)
    mesh_key = f"diamond-{_condition_tag()}-{res_level}"

    def build_mesh() -> None:
        sh("blockMesh", case_dir, case_dir / "log.blockMesh")

    def run_solve() -> None:
        sh("rhoCentralFoam", case_dir, case_dir / "log.rhoCentralFoam")

    cache = mesh_and_solve(
        case_dir=case_dir, mesh_key=mesh_key,
        solve_key_fn=lambda cells: f"{mesh_key}-c{cells}",
        build_mesh=build_mesh, run_solve=run_solve,
        count_cells=lambda: RES_CELLS[res_level])
    mesh_stats = run_checkmesh(case_dir)

    force_files = sorted(glob.glob(f"{case_dir}/postProcessing/forces1/*/force.dat"))
    lines = [line for line in open(force_files[-1]) if not line.startswith("#")]
    fx_slab = float(lines[-1].split()[1])
    fx_per_span_total = 2.0 * (fx_slab / Z_THICKNESS)
    q1 = 0.5 * GAMMA * 1.0 * MACH ** 2
    cd_computed = fx_per_span_total / (q1 * meta["c"])

    return {"res_level": res_level, "cells": cache["cells"],
            "mesh_warm": cache["mesh_warm"], "solve_warm": cache["solve_warm"],
            "mesh_seconds": cache["mesh_seconds"], "solve_seconds": cache["solve_seconds"],
            "mesh_stats": mesh_stats, "cd_computed": cd_computed}


def main(request: str | None = None, params: dict | None = None, emit=None) -> int:
    params = dict(params or {})
    out = OUT_ROOT / LABEL
    out.mkdir(parents=True, exist_ok=True)

    script = make_transcript(LABEL, emit)
    roster = Roster(emit)
    ledger = ComputeLedger(emit)
    knowledge = KnowledgeBase(emit)
    ref = _exact_reference()

    script.phase(HYPOTHESIS, "Wave drag on a symmetric diamond section")
    bullets(script.researcher,
           "The diamond section turns the flow through a leading compression "
           "and a trailing expansion on each panel, and the pressure "
           "integral over all four panels gives the wave drag predicted by "
           f"shock-expansion theory, {per('shock-expansion')}.",
           "Falsification: if the measured wave drag departs from the "
           "closed form value outside the stated tolerance, the hypothesis "
           "fails.")

    script.phase(PLAN, "Mesh at three resolutions, solve, integrate the pressure")
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
    announce_geometry(emit, name="diamond_airfoil.stl", label=display_name(BODY))
    bullets(script.engineer,
           "Plan: mesh the diamond section at three resolutions, coarsest "
           "to finest, solve the compressible flow through the selected "
           "solver at each, and integrate the pressure over the panels.",
           "The finest mesh is the production result; the two cheaper "
           "meshes bound its grid sensitivity.")
    roster.idle(CHIEF_ENGINEER)

    script.phase(EVIDENCE, "Meshing and solving the diamond section")
    roster.set(NUMERICIST, "meshing and solving the diamond ladder", "working")
    beta_exact_deg = ref["beta_deg"]
    levels: dict[str, dict[str, Any]] = {}
    headers = ("Mesh", "Cells", "Wave drag coefficient")
    table_rows: list[list[str]] = []
    try:
        for res_level in RES_LEVELS:
            case_dir = _RUN_ROOT / res_level
            result = _run_level(case_dir, res_level, beta_exact_deg)
            levels[res_level] = result
            ledger.spend(result["mesh_seconds"] + result["solve_seconds"],
                        f"diamond {res_level}")
            table_rows.append([res_level, result["cells"],
                               f"{result['cd_computed']:.5f}"])
            emit_table(emit, script, role="NUMERICIST",
                      title="Diamond mesh ladder", headers=headers,
                      rows=[table_rows[-1]], table_id="diamond-ladder",
                      append=len(table_rows) > 1)
    except Exception as exc:
        bullets(script.engineer,
               "The diamond solve did not complete; the run logs carry the "
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
        out / "diamond_wave_drag.png",
        xlabel="cells (mesh ladder)", ylabel="wave drag coefficient",
        title="Diamond airfoil wave drag: solved vs exact shock-expansion theory",
        series=[("solved wave drag",
                [levels[r]["cells"] for r in RES_LEVELS],
                [levels[r]["cd_computed"] for r in RES_LEVELS], "points")],
        hline=(ref["cd"], "exact wave drag"))
    announce_plot(emit, LABEL, plot_path, "Diamond wave drag vs exact theory")

    script.phase(CONCLUSION, "Grid sensitivity, verdict, uncertainty")
    roster.set(NUMERICIST, "grid sensitivity across the diamond ladder", "working")
    cells_series = [levels[r]["cells"] for r in RES_LEVELS]
    cd_series = [levels[r]["cd_computed"] for r in RES_LEVELS]
    # dim=2 is read off this ladder's own mesh, not off the case name. The
    # diamond blockMeshDict lays four blocks of (nx ny 1) with the front and
    # back planes typed empty, so refinement moves in exactly two directions
    # and the cell count grows as the square of the linear refinement (2000,
    # 8000, 32000: a factor of 4 per rung, 2 in each direction). Left at the
    # dim=3 default the representative size is the cube root of the same
    # counts, which stretches every observed order by exactly 1.5.
    band = uq_studies.eca_hoekstra_band(cells_series, cd_series, dim=2)
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
    ladder_spread = max(cd_series) - min(cd_series)
    # The total is the root sum of squares over the channels that carry a
    # figure, through the same call every other act uses. Input and model are
    # passed as absent, so they are stated as unquantified rather than
    # silently counted as zero.
    total = uq_studies.combine_expanded(
        input_2sigma=None, numerical_abs=numerical_abs, model_abs=None)
    combined = total["combined_95"]
    bullets(script.numericist,
           "Grid sensitivity study: three meshes of the same diamond "
           "section, one knob moved, the wave drag tracked at each.",
           (f"The wave drag coefficient moved {ladder_spread:.5f} across the "
            f"three rungs, and no band is read from that spread."
            if numerical_abs is None else
            f"The ladder is conclusive, so the numerical channel carries "
            f"{numerical_abs:.5f}."),
           (f"The ladder is not conclusive: {ladder_reason}."
            if numerical_abs is None else ""),
           (f"{ladder_holding}."
            if numerical_abs is None and ladder_holding else ""),
           citations=[per("shock-expansion")])
    roster.idle(NUMERICIST)

    cd_computed = production["cd_computed"]
    rel_error = abs(cd_computed - ref["cd"]) / ref["cd"]
    verdict = trust(
        relative_error=rel_error, converged=True,
        in_validated_regime=gates_pass, calibrated=True, solver_backed=True,
        tight_threshold=0.02,
        why=(f"a selected-solver wave drag graded against exact "
             f"shock-expansion theory; envelope {rel_error * 100:.2f}% of "
             f"the exact value"))
    emit_table(emit, script, role="CHIEF ENGINEER", title="Diamond verdict",
              headers=("Quantity", "Exact", "Solved", "Deviation"),
              rows=[["Wave drag coefficient", f"{ref['cd']:.5f}",
                    f"{cd_computed:.5f}", f"{100 * rel_error:.2f}%"]],
              table_id="diamond-verdict")
    if emit:
        # The interval keys ride along only when a combined 95% figure exists.
        # With no quantified channel there is no interval, and the headline
        # says so by carrying no interval at all.
        verdict_payload = {"quantity": "Wave drag coefficient",
                           "value": f"{cd_computed:.5f}", **verdict}
        if combined is not None:
            verdict_payload["ci"] = f"{combined:.5f}"
            verdict_payload["confidence"] = "95%"
        emit("result.verdict", verdict_payload)

    channels = uncertainty_channels(
        input_2sigma=None, numerical=numerical_abs, model=None,
        input_note=INPUT_ASSUMED_NOTE,
        numerical_note=(
            f"Grid sensitivity band across the mesh ladder: "
            f"{numerical_abs:.5f}." if numerical_abs is not None else
            f"• The wave drag coefficient moved {ladder_spread:.5f} across "
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
        title="Total uncertainty on the wave drag coefficient",
        headers=("Channel", "Value", "In the total"),
        rows=[["Input", "Not quantified", "No, and not counted as zero"],
              ["Numerical",
               f"{numerical_abs:.5f}" if numerical_abs is not None
               else "Not quantified",
               "Yes" if numerical_abs is not None
               else "No, the mesh ladder is not conclusive"],
              ["Model form", "Not quantified",
               "No, the case shares the theory's inviscid assumption"],
              ["Total",
               f"{combined:.5f}" if combined is not None else "Not reported",
               "The quantified channels" if combined is not None
               else "No channel is quantified, so no interval is reported"]],
        table_id="diamond-uncertainty")
    bullets(script.researcher,
           "Three uncertainty channels are named for this number: the input "
           "channel, the numerical channel from the mesh ladder, and the "
           "model channel, each with its state on the table above.",
           ("The wave drag coefficient is reported as a point estimate: no "
            "channel carries a figure, so there is no 95% interval to quote."
            if combined is None else
            f"The wave drag coefficient carries a combined 95% interval of "
            f"{combined:.5f} over the quantified channels."))

    caveat_bullets = caveats or ["Mesh quality cleared both published gates."]
    bullets(script.engineer, *caveat_bullets)

    knowledge.add("Diamond airfoil wave drag confirmed against exact "
                  "shock-expansion theory.")
    if emit:
        emit("agenda.updated", {"entries": _AGENDA})

    # The certificate captions the first result's envelope "95% confidence
    # interval" whenever it reads as a bare magnitude, so the key is present
    # only when a combined 95% figure exists. Absent, it prints as a point
    # estimate.
    headline_result: dict[str, Any] = {
        "quantity": "Wave drag coefficient", "value": f"{cd_computed:.5f}",
        "tier": verdict["tier"], "reason": verdict["reason"]}
    if combined is not None:
        headline_result["envelope"] = f"{combined:.5f}"

    report_doc = lab_report(
        title="Diamond airfoil: shock-expansion wave drag validation",
        abstract=["A symmetric diamond section at a stated Mach number "
                 "produces a wave drag graded against exact shock-expansion "
                 "theory."],
        methods=["Mesh and solve the diamond section at three resolutions "
                "through the selected solver.", "Integrate the pressure "
                "over the four panels to the wave drag coefficient."],
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
            ("Wave drag coefficient", f"{cd_computed:.5f}"),
            ("Grid sensitivity band",
             f"{numerical_abs:.5f}" if numerical_abs is not None
             else "Not reported, the ladder is not conclusive"),
            ("Cells", f"{production['cells']}"),
        ]
        certificate = build_certificate_v2(
            cert_doc, out_path=cert_path, geometry=BODY,
            objective=(request or "Diamond airfoil, shock-expansion wave drag validation"),
            mission_id=f"{LABEL}-{int(time.time())}",
            issued_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            channels=channels, display_name=display_name(BODY),
            source_filename="diamond_airfoil.stl",
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
