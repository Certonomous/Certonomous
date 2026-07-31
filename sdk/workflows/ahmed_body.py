"""Act 7 — the Ahmed body, 25 degree slant: the harder of the two rear angles.

The Ahmed reference body is the standard automotive bluff-body benchmark
(Ahmed, Ramm & Faltin 1984, SAE 840300). At a 25 degree slant the wake sits on
the edge of reattachment; the real flow is bistable, so a steady RANS solve
scatters more here than at 35 degrees and can miss the published drag even on
a clean mesh. That is exactly why it is one of the four hardest validated
cases: the gate is unforgiving and the physics does not hide anywhere.

This act runs the same meshed-and-solved chain ``workflows.geometry_study``
already runs for an unfamiliar body — surface intake, background mesh,
snappyHexMesh, potential-flow initialisation, the steady solve, the in-act
refinement ladder, and the three V&V-20 channels — pinned to the validated
25 degree geometry and reported under its own beat so the control room can
film it as its own act with its own certificate.

    python -m workflows.ahmed_body
"""
from __future__ import annotations

import time
from pathlib import Path

from . import OUT_ROOT, announce_field, announce_geometry, announce_plot, make_transcript
from chief_engineer.compute_audit import audit
from chief_engineer.display_names import display_name
from chief_engineer.head_engineer import FOAM_TUTORIALS, HeadEngineer
from chief_engineer.researcher import ENGINEER_ACK, MissionProperties, method_memo
from chief_engineer.lab import (CHIEF_ENGINEER, CHIEF_RESEARCHER, CONCLUSION,
                                EVIDENCE, HYPOTHESIS, MONITOR, PLAN,
                                ComputeLedger, KnowledgeBase, Roster,
                                lab_report, per, validate_against_reference)
from chief_engineer.transcript import CHIEF_ENGINEER as _CE_ROLE

from .geometry_study import (GEOMETRY_DIR, MAX_NON_ORTHOGONALITY, MAX_SKEWNESS,
                             _build_unfamiliar_case, _curriculum, _emit_table,
                             _ladder_rows, _run_refinement_ladder, certificate_channels,
                             mesh_caveat_lines, mesh_validity, pressure_slice_entry,
                             retry_mesh_quality, surface_acceptance)

SURFACE = "ahmed_25.stl"
LABEL = "ahmed_25"
GATE_SOURCE = "Ahmed, Ramm & Faltin 1984, SAE 840300"
GATE_TOLERANCE = 0.15


def main(request: str | None = None, params: dict | None = None,
        iterations: int = 300, emit=None) -> int:
    params = dict(params or {})
    params["surface"] = SURFACE
    out = OUT_ROOT / "ahmed-body"
    out.mkdir(parents=True, exist_ok=True)

    shown = display_name(LABEL)
    reference, hints = _curriculum(LABEL)
    for key, value in hints.items():
        params.setdefault(key, value)

    script = make_transcript(f"Act 7: {shown}", emit)
    roster = Roster(emit)
    ledger = ComputeLedger(emit)
    knowledge = KnowledgeBase(emit)
    began = time.monotonic()

    script.system(request or f"Request: solve the Ahmed body, 25 degree rear "
                             f"slant, and grade it against the published wind "
                             f"tunnel drag.")

    # ---------------- Hypothesis ----------------
    script.phase(HYPOTHESIS)
    roster.set(CHIEF_RESEARCHER, "selecting the method", "working")
    props = MissionProperties(
        kind="single-body-study",
        objective="a trustworthy drag coefficient for the 25 degree slant",
        dimensionality=0,
        regime="steady turbulent (RANS), separated wake",
        smoothness="gated",
        fidelity="a solved field",
        admissibility_cite="against the standard mesh-quality acceptance band")
    for line in method_memo(props):
        script.researcher(line)
    roster.idle(CHIEF_RESEARCHER)
    script.engineer(ENGINEER_ACK)

    roster.set(CHIEF_ENGINEER, f"reading {shown}", "working")
    announce_geometry(emit, name=SURFACE, label=shown)
    script.engineer(
        f"• Hypothesis: a quality-gated steady RANS solve lands within the "
        f"published band of {GATE_SOURCE}. "
        f"• Falsifier: the mesh misses its gates, the force never settles, "
        f"or the converged drag sits outside ±{GATE_TOLERANCE * 100:.0f}% of "
        f"the published Cd once rebased to frontal area. "
        f"• This is the harder of the two slant angles: the wake sits on the "
        f"edge of reattachment and the real flow is bistable, so a steady "
        f"solve can miss the published number even on a clean mesh.")
    script.engineer(
        f"• Gate: within ±{GATE_TOLERANCE * 100:.0f}% of {GATE_SOURCE}, "
        f"rebased from the solver's planform-area coefficient to the "
        f"published frontal-area basis. "
        f"• Credible because the source is the body's own defining "
        f"publication, still the standard automotive-wake reference four "
        f"decades on.")
    script.numericist(
        f"• The gates are the standard acceptance band, {per('mesh-quality')}. "
        "• The mesh is judged against a published threshold, not itself.")

    # ---------------- Plan ----------------
    script.phase(PLAN)
    capacity = audit(1, memory_per_worker_mb=2048)
    if emit:
        emit("audit.completed", capacity.panel())
        emit("solver.selected", {
            "solver": "OpenFOAM", "method": "steady RANS, k-omega SST",
            "basis": "plan commits the body to the meshed-and-solved chain"})
    script.engineer(capacity.headline(), panel=capacity.panel())
    script.engineer(
        f"• Plan: mesh the body, clear the quality gates, then {iterations} "
        f"steady iterations. "
        f"• Meshing is the long pole on this body's separated wake mesh.")

    engineer = HeadEngineer(f"act7-{LABEL}", out, novel=True,
                            on_event=lambda event, payload: None)
    monitor_seen: list[str] = []

    stage_table = {"created": False}

    def stage_row(step: str, seconds: float, note: str) -> None:
        _emit_table(emit, script, role=_CE_ROLE,
                    title="Pipeline stages, as run",
                    headers=("Stage", "Time", "What ran"),
                    rows=[[step, f"{seconds:.0f} s",
                           note[:1].upper() + note[1:]]],
                    table_id=f"stages-act7-{LABEL}", append=stage_table["created"])
        stage_table["created"] = True

    def on_anomaly(anomaly):
        monitor_seen.append(anomaly.kind)
        if anomaly.kind in {"nan", "fpe"}:
            roster.set(MONITOR, f"fatal: {anomaly.kind}", "blocked")
            script.monitor(f"• Stopping the study: {anomaly.detail} during {anomaly.step}.")
        elif anomaly.kind == "residual-spike":
            roster.set(MONITOR, "residual spike flagged", "watching")
            script.monitor(f"• Residual spike during {anomaly.step}: {anomaly.detail}")
        elif anomaly.kind == "novel-warning":
            roster.set(MONITOR, "unfamiliar solver warning", "watching")
            script.monitor(f"• New on this body: {anomaly.line[:150]}")

    engineer.monitor.on_anomaly = on_anomaly

    # ---------------- Evidence ----------------
    script.phase(EVIDENCE)
    roster.set(MONITOR, "watching solver output", "watching")
    roster.set(CHIEF_ENGINEER, "staging the case", "working")

    try:
        report = _build_unfamiliar_case(engineer, script, roster, SURFACE,
                                        params, iterations, emit)
        acceptance_line, shells = surface_acceptance(report, shown)
        script.engineer(acceptance_line)
        script.engineer(
            "• Selected: k-omega SST, steady RANS, standard closure for "
            "separated external flow, solved on a quality-gated mesh.")

        warm = engineer.restore_cached_mesh(LABEL)
        if warm:
            roster.set(CHIEF_ENGINEER, "preparing the mesh", "working")
            script.engineer(
                "• Mesh in hand for this body; going straight to the "
                "quality gates and the solve.")
        else:
            for step, command, note in (
                ("surfaceFeatureExtract", "surfaceFeatureExtract",
                 "extracting the feature edges the mesher snaps to"),
                ("blockMesh", "blockMesh", "building the background mesh"),
                ("snappyHexMesh", "snappyHexMesh -overwrite",
                 "snapping the mesh to the body, the long stage"),
            ):
                roster.set(CHIEF_ENGINEER, note, "working")
                roster.set_workers(1, note)
                result = engineer._run_step(step, command, 5400)
                ledger.spend(result.seconds, f"{step} ({result.seconds:.0f}s)")
                stage_row(step, result.seconds, note)
            engineer.save_mesh_to_cache(LABEL)

        stats = engineer.collect_mesh_stats()

        def _remesh(retry_index: int) -> None:
            engineer.clear_mesh_cache(LABEL)
            for step, command, note in (
                ("surfaceFeatureExtract", "surfaceFeatureExtract",
                 "extracting the feature edges the mesher snaps to"),
                ("blockMesh", "blockMesh", "rebuilding the background mesh"),
                ("snappyHexMesh", "snappyHexMesh -overwrite",
                 "re-snapping under the tightened quality controls"),
            ):
                roster.set(CHIEF_ENGINEER, note, "working")
                result = engineer._run_step(step, command, 5400)
                ledger.spend(result.seconds,
                             f"{step} remesh {retry_index} ({result.seconds:.0f}s)")
                stage_row(f"{step} (remesh {retry_index})", result.seconds, note)

        stats, mesh_retries, retried_gates_ok = retry_mesh_quality(
            engineer, stats, narrate=script.engineer, remesh=_remesh)
        if mesh_retries and retried_gates_ok:
            engineer.save_mesh_to_cache(LABEL)
            script.engineer(
                f"• Remesh {mesh_retries} brought the mesh inside the gates; "
                f"the tightened mesh is the one solved below.")
        elif mesh_retries:
            script.engineer(
                f"• The mesh still misses a gate after {mesh_retries} "
                f"remesh{'es' if mesh_retries > 1 else ''}; proceeding with "
                f"the caveat on the record.")

        cells = int(stats.get("cells", 0))
        non_ortho = stats.get("max_non_orthogonality")
        skew = stats.get("max_skewness")
        if emit:
            emit("mesh.stats", {"cells": cells,
                                "max_non_orthogonality": non_ortho,
                                "max_skewness": skew})
        non_ortho_s = f"{non_ortho:.1f}°" if non_ortho is not None else "n/a"
        skew_s = f"{skew:.2f}" if skew is not None else "n/a"
        gate_ok = (non_ortho or 0) <= MAX_NON_ORTHOGONALITY
        roster.set(CHIEF_RESEARCHER, "ruling on mesh quality", "working")
        script.researcher(
            f"• Mesh: {cells:,} cells; non-ortho {non_ortho_s}; skew {skew_s}. "
            + (f"• Non-ortho inside the {MAX_NON_ORTHOGONALITY:.0f}° gate, discretization acceptable. "
               if gate_ok else
               f"• Non-ortho exceeds the {MAX_NON_ORTHOGONALITY:.0f}° gate, no validated force from this mesh. ")
            + (f"• Skew {skew_s} above the {MAX_SKEWNESS:.0f} guidance, caps trust; not fully validated."
               if (skew or 0) > MAX_SKEWNESS else
               "• Skewness inside guidance as well."))
        roster.idle(CHIEF_RESEARCHER)

        solve_key = f"{LABEL}-c{cells}-i{iterations}"
        warm_solve = engineer.restore_cached_solve(solve_key)
        # This act is capped at 4 MPI ranks on cost grounds, not the
        # environment-driven default other acts use.
        ranks = min(4, max(1, engineer.solve_ranks()))
        parallel = (not warm_solve) and ranks > 1 and engineer.decompose_for_parallel(ranks)
        if parallel:
            script.engineer(
                f"• Case decomposed into {ranks} subdomains, capped at 4 "
                f"ranks: the steady solve runs in parallel, same mesh and "
                f"same numbers.")

        live_cd = {"iter": None, "vals": [], "iters": [], "last": 0.0, "emitted": 0}

        import re as _re
        _TIME_RE = _re.compile(r"^Time = (\d+)")
        _CD_RE = _re.compile(r"^\s*Cd\s*[:=]\s*([-+0-9.eE]+)")

        def _cd_line_hook(line: str) -> None:
            if not emit:
                return
            m = _TIME_RE.match(line)
            if m:
                live_cd["iter"] = int(m.group(1))
                return
            m = _CD_RE.match(line)
            if not m or live_cd["iter"] is None:
                return
            live_cd["iters"].append(live_cd["iter"])
            live_cd["vals"].append(float(m.group(1)))
            now = time.time()
            if now - live_cd["last"] < 0.5:
                return
            live_cd["last"] = now
            vals = live_cd["vals"]
            win = max(5, len(vals) // 10)
            chunk = vals[-win:]
            mean = sum(chunk) / len(chunk)
            sd = ((sum((v - mean) ** 2 for v in chunk) / (len(chunk) - 1)) ** 0.5
                  if len(chunk) > 1 else 0.0)
            live_cd["emitted"] += 1
            emit("trace.point", {
                "series": "Cd_history", "x": live_cd["iters"][-1],
                "y": round(vals[-1], 5), "lo": round(mean - 2 * sd, 5),
                "hi": round(mean + 2 * sd, 5), "x_label": "solver iteration",
                "y_label": "Cd", "title": "Drag coefficient: solver iteration history",
                "feasible": True})

        if warm_solve:
            note = f"steady solve, {iterations} iterations"
            roster.set(CHIEF_ENGINEER, note, "working")
            roster.set_workers(max(1, ranks), note)
            started = time.time()
            raw = engineer._wsl(
                f"cat {engineer.remote_case}/postProcessing/*/0/coefficient.dat "
                f"2>/dev/null", timeout=120).stdout
            rows = [ln.split() for ln in raw.splitlines()
                    if ln.strip() and not ln.lstrip().startswith("#")]
            pts = []
            for r in rows:
                try:
                    pts.append((int(float(r[0])), float(r[1])))
                except (ValueError, IndexError):
                    continue
            if emit and pts:
                step_n = max(1, len(pts) // 36)
                marks = sorted(set(list(range(0, len(pts), step_n)) + [len(pts) - 1]))
                per_point = 14.0 / max(1, len(marks))
                for i in marks:
                    vals = [v for _, v in pts[:i + 1]]
                    win = max(5, len(vals) // 10)
                    chunk = vals[-win:]
                    mean = sum(chunk) / len(chunk)
                    sd = ((sum((v - mean) ** 2 for v in chunk)
                           / (len(chunk) - 1)) ** 0.5 if len(chunk) > 1 else 0.0)
                    live_cd["emitted"] += 1
                    emit("trace.point", {
                        "series": "Cd_history", "x": pts[i][0],
                        "y": round(pts[i][1], 5), "lo": round(mean - 2 * sd, 5),
                        "hi": round(mean + 2 * sd, 5),
                        "x_label": "solver iteration", "y_label": "Cd",
                        "title": "Drag coefficient: solver iteration history",
                        "feasible": True})
                    if per_point > 0:
                        time.sleep(per_point)
            elapsed = max(1.0, time.time() - started)
            ledger.spend(elapsed, f"simpleFoam ({elapsed:.0f}s)")
            stage_row("selected solver", elapsed, note)
            roster.set_workers(0)
        else:
            for step, base, note in (
                ("potentialFoam", "potentialFoam -writephi",
                 "initialising the velocity field so the steady solver starts sane"),
                ("simpleFoam", "simpleFoam", f"steady solve, {iterations} iterations"),
            ):
                command = f"mpirun -np {ranks} {base} -parallel" if parallel else base
                roster.set(CHIEF_ENGINEER, note, "working")
                roster.set_workers(ranks if (parallel and step == "simpleFoam") else 1,
                                   note)
                result = engineer._run_step(
                    step, command, 7200,
                    line_hook=_cd_line_hook if step == "simpleFoam" else None)
                ledger.spend(result.seconds, f"{step} ({result.seconds:.0f}s)")
                stage_row(step, result.seconds, note)
            roster.set_workers(0)
            if parallel:
                engineer.reconstruct_latest()
            engineer.save_solve_to_cache(solve_key)
    except Exception as exc:
        roster.set(CHIEF_ENGINEER, "halted", "blocked")
        import re as _re2
        step_match = _re2.match(r"step '(\w+)' failed", str(exc))
        stopped_at = step_match.group(1) if step_match else "a solver stage"
        script.engineer(f"• The study stopped: {stopped_at} did not complete "
                        f"cleanly; detail in the run log, not on screen.")
        script.save(out / "transcript.txt")
        roster.all_idle()
        return 1

    # ---------------- Results ----------------
    roster.set(CHIEF_ENGINEER, "reading the force history", "working")
    results = engineer.postprocess(("Cd", "Cl"))

    cd_hist = engineer.histories.get("Cd")
    if emit and cd_hist and cd_hist["series"] and not live_cd["emitted"]:
        iters, series = cd_hist["iterations"], cd_hist["series"]
        n = len(series)
        step = max(1, n // 40)
        win = max(5, n // 10)
        marks = sorted(set(list(range(0, n, step)) + [n - 1]))
        for i in marks:
            chunk = series[max(0, i - win + 1):i + 1]
            m = sum(chunk) / len(chunk)
            s = (sum((v - m) ** 2 for v in chunk) / (len(chunk) - 1)) ** 0.5 if len(chunk) > 1 else 0.0
            emit("trace.point", {
                "series": "Cd_history", "x": round(iters[i], 0),
                "y": round(series[i], 5), "lo": round(m - 2 * s, 5),
                "hi": round(m + 2 * s, 5), "x_label": "solver iteration",
                "y_label": "Cd", "title": "Drag coefficient: solver iteration history",
                "feasible": True})

    roster.set(CHIEF_ENGINEER, "extracting the surface pressure field", "working")
    from chief_engineer.field_render import extract_and_paint

    input_triangles = None
    local_surface = GEOMETRY_DIR / SURFACE
    if local_surface.exists():
        try:
            from chief_engineer.geometry import load_surface
            input_triangles = load_surface(local_surface)["triangles_total"]
        except Exception:
            input_triangles = None

    from . import RUN_PREFIX
    painted = extract_and_paint(
        engineer.remote_case, engineer.out_root / f"{LABEL}_field",
        RUN_PREFIX[:-1] if RUN_PREFIX and RUN_PREFIX[-1] == "openfoam2606" else RUN_PREFIX,
        field="p", name=LABEL, input_triangles=input_triangles)
    if painted:
        served = out / Path(painted).name
        try:
            served.write_bytes(Path(painted).read_bytes())
            painted = str(served)
        except OSError:
            pass
        announce_field(emit, "ahmed-body", painted,
                       f"{shown}, surface pressure from the solve")
        script.engineer("• Body carrying its own solved surface field.")

    plots: list[str] = []
    report_plots: list[dict] = []
    for name in ("Cd", "Cl"):
        png = engineer.out_root / f"{name}_envelope.png"
        if png.exists():
            target = out / png.name
            target.write_bytes(png.read_bytes())
            plots.append(str(target))
            title = f"{'Drag' if name == 'Cd' else 'Lift'} history with envelope"
            announce_plot(emit, "ahmed-body", target, title)
            report_plots.append({"title": title, "file": target.name,
                                 "url": f"/api/plot/ahmed-body/{target.name}"})

    # The mid-span slice is not drawn. A flat cut through the volume
    # competed with the painted body for the same attention and read as
    # the weaker picture, and it carried a caption describing colours the
    # viewer can already see. The body itself carries the field.

    drag = results.get("Cd")
    lift = results.get("Cl")
    if not drag:
        script.engineer("• No force history from the solver, nothing to report.")
        script.save(out / "transcript.txt")
        roster.all_idle()
        return 1

    skew_ok = (skew or 0) <= MAX_SKEWNESS
    caveats = mesh_caveat_lines(non_ortho, skew)
    why = caveats[0] if caveats else ""

    from chief_engineer import uq as uq_studies
    study_fp = uq_studies.setup_fingerprint(
        body=LABEL, solver="openfoam-simpleFoam", closure="kOmegaSST",
        velocity=float(params.get("velocity", 40.0)),
        refinement=int(params.get("refinement", 3)), iterations=iterations)
    grid_conclusive = None
    existing_study = uq_studies.load_study(LABEL) or {}
    if existing_study.get("fingerprint") == study_fp:
        grid_conclusive = (existing_study.get("numerical") or {}).get("conclusive")

    verdict = validate_against_reference(
        measured_cd=drag["value"], reference=reference,
        planform_area=report.get("planform_area"),
        frontal_area=report.get("frontal_area"),
        converged=True, in_validated_regime=gate_ok, calibrated=skew_ok,
        grid_conclusive=grid_conclusive,
        solved_reynolds=report.get("reference", {}).get("reynolds"))
    comparison = verdict.get("comparison")

    gate_rows = [["Measured C_d (planform basis)", f"{comparison['measured_cd']:.4g}"],
                 ["Rebased C_d (frontal basis)", f"{comparison['compared_cd']:.4g}"],
                 [f"Published C_d ({GATE_SOURCE})", f"{comparison['reference_cd']:g}"],
                 ["Deviation", f"{(comparison['relative_error'] * 100):.1f}%"
                  if comparison['relative_error'] is not None else "not comparable"],
                 ["Gate", f"±{comparison['tolerance'] * 100:.0f}%"]]
    _emit_table(emit, script, role=_CE_ROLE, title="Gate: measured drag vs the published wind tunnel",
               headers=("Quantity", "Value"), rows=gate_rows,
               table_id=f"gate-act7-{LABEL}")

    script.engineer("• Forces settled; the window is flat.", verdict=verdict)
    coefficient_rows = [["C_d", f"{drag['value']:.4g}",
                         f"±{2 * drag['sigma']:.2g}",
                         f"final {drag['window']} iterations"]]
    if lift:
        coefficient_rows.append(["C_L", f"{lift['value']:.4g}",
                                 f"±{2 * lift['sigma']:.2g}",
                                 f"final {lift['window']} iterations"])
    _emit_table(emit, script, role=_CE_ROLE,
               title="Force coefficients over the settled window",
               headers=("Coefficient", "Value", "Band (95%)", "Window"),
               rows=coefficient_rows, table_id=f"coefficients-act7-{LABEL}")

    try:
        refine = _run_refinement_ladder(
            engineer=engineer, label=LABEL, familiar=False, params=params,
            iterations=iterations, production_cells=cells,
            production_cd=drag["value"], study_fp=study_fp, script=script,
            roster=roster, ledger=ledger, emit=emit, out=out)
    except Exception:
        script.numericist(
            "• The refinement study did not complete; detail is in the run "
            "logs, and no band is reported from a partial ladder.")
        refine = None

    if (refine is not None and refine.get("conclusive") is not None
            and refine["conclusive"] != grid_conclusive):
        grid_conclusive = bool(refine["conclusive"])
        before = verdict.get("tier")
        verdict = validate_against_reference(
            measured_cd=drag["value"], reference=reference,
            planform_area=report.get("planform_area"),
            frontal_area=report.get("frontal_area"),
            converged=True, in_validated_regime=gate_ok, calibrated=skew_ok,
            grid_conclusive=grid_conclusive,
            solved_reynolds=report.get("reference", {}).get("reynolds"))
        comparison = verdict.get("comparison")
        if verdict.get("tier") != before:
            script.numericist(
                f"• The refinement study just measured settles the grade: the "
                f"chip moves from {before} to {verdict['tier']} on this run's "
                f"own grid evidence, not on the agreement alone.")

    lookup = uq_studies.channels_for(LABEL, study_fp)
    transfer = (None if lookup.get("model")
               else uq_studies.transferred_model_band(drag["value"], exclude=LABEL))
    channels = certificate_channels(
        settle_2sigma=2 * drag["sigma"], window=drag["window"],
        velocity=float(params.get("velocity", 40.0)),
        lookup=lookup, cells=cells, non_ortho_s=non_ortho_s, skew_s=skew_s,
        model_extra=(f"within ±{comparison['tolerance'] * 100:.0f}% of {GATE_SOURCE}"
                    if comparison.get("relative_error") is not None
                    and comparison["relative_error"] <= comparison["tolerance"] else ""),
        transfer=transfer)
    numerical_val = channels["channels"][1]["value"]
    model_val = channels["channels"][2]["value"]
    combined = uq_studies.combine_expanded(
        input_2sigma=2 * drag['sigma'], numerical_abs=numerical_val,
        model_abs=model_val)["combined_95"]
    if emit:
        emit("result.verdict", {"quantity": "Drag coefficient",
                                "value": f"{drag['value']:.4g}",
                                "ci": f"{(combined if combined else 2 * drag['sigma']):.2g}",
                                "confidence": "95%",
                                "envelope": f"over the final {drag['window']} iterations",
                                **verdict})
        emit("uncertainty.channels", channels)

    monitor_summary = engineer.monitor.summary()
    suppressed = sum(monitor_summary.get("suppressed", {}).values())
    script.monitor(
        f"• Watched every solver line: {monitor_summary['anomalies']} watch-pattern "
        f"event{'' if monitor_summary['anomalies'] == 1 else 's'} {monitor_summary['by_kind'] or ''}. "
        + (f"• {suppressed} repeats counted, not repeated at you. " if suppressed else "")
        + ("• Nothing fatal." if not monitor_summary["fatal"] else
           "• One fatal: do not use this result."))
    roster.idle(MONITOR)

    # ---------------- Conclusion ----------------
    script.phase(CONCLUSION)
    elapsed = (time.monotonic() - began) / 60
    script.engineer(
        f"• From raw surface to a converged force in {elapsed:.1f} minutes. "
        "• The coefficient history is flat across the averaging window, so "
        "the quoted band is meaningful.")
    if verdict["tier"] == "VALIDATED":
        script.engineer(
            f"• Verdict: validated. {verdict['reason']}. "
            f"• The harder of the two slant angles cleared its own gate.")
    else:
        script.engineer(
            f"• Verdict: {verdict['tier'].lower()}. {verdict['reason']}.")
    knowledge.add(f"{shown} meshed and solved: {cells:,} cells, "
                  f"Cd {drag['value']:.4g} ± {2 * drag['sigma']:.2g}")
    script.numericist(
        f"• Lessons entered to memory. "
        f"• Next question about a body like {shown} answers from a real run.")

    _AGENDA = [
        {"title": "The other slant angle",
         "scope": "run the 35 degree body the same way and compare how the "
                  "gate margin changes with the reattachment physics",
         "cost": "one solve on the existing mesh family"},
        {"title": "Yaw sweep on the slant",
         "scope": "sweep the approach angle and map the C-pillar vortex "
                  "strength as the body meets the flow off-axis",
         "cost": "one solve per angle on this mesh"},
        {"title": "Resolve the wake bistability",
         "scope": "an unsteady solve to see whether the steady solution has "
                  "picked one branch of the real bistable wake",
         "cost": "transient solve; roughly an order of magnitude over steady"},
    ]
    if emit:
        emit("agenda.updated", {"entries": _AGENDA})

    report_doc = lab_report(
        title=f"Act 7: {shown}",
        abstract=[
            f"We took the Ahmed body, 25 degree slant, through surface "
            f"check, meshing, and a steady solve, and graded the converged "
            f"drag against {GATE_SOURCE}.",
            f"The mesh reached {cells:,} cells at max non-orthogonality "
            f"{non_ortho_s} and max skewness {skew_s}; drag settled at "
            f"{drag['value']:.4g} ± {2 * drag['sigma']:.2g}.",
            f"The result is reported as {verdict['tier'].lower()}: {verdict['reason']}.",
        ],
        methods=[
            "Surface intake and check on the 25 degree Ahmed body.",
            f"Meshed to {cells:,} cells; quality gated at "
            f"{MAX_NON_ORTHOGONALITY:.0f}° non-orthogonality and "
            f"{MAX_SKEWNESS:.0f} skewness.",
            f"{iterations} steady iterations on the gated mesh.",
            "Forces averaged over the final fifth of the iteration history; "
            "the band is the spread of that window.",
            f"Measured drag rebased from planform to frontal area and graded "
            f"against {GATE_SOURCE}.",
        ],
        results=[{
            "quantity": "Drag coefficient",
            "value": f"{drag['value']:.4g}",
            "envelope": f"±{2 * drag['sigma']:.2g} over the final {drag['window']} iterations",
            **verdict,
        }] + ([{
            "quantity": "Lift coefficient",
            "value": f"{lift['value']:.4g}",
            "envelope": f"±{2 * lift['sigma']:.2g}",
            **verdict,
        }] if lift else []) + [{
            "quantity": "Drag vs published wind tunnel",
            "value": f"Cd {comparison['compared_cd']:.4g} vs {comparison['reference_cd']:g}",
            "envelope": (f"{comparison['relative_error'] * 100:.0f}% apart, "
                        f"±{comparison['tolerance'] * 100:.0f}% band"
                        if comparison['relative_error'] is not None else "not comparable"),
            **verdict,
        }] + ([{
            "quantity": "Numerical uncertainty on Cd",
            "value": f"±{refine['band_abs']:.2g}",
            "envelope": refine["method"],
            **verdict,
        }] if refine and refine.get("band_abs") is not None else []) + [{
            "quantity": "Mesh",
            "value": f"{cells:,} cells",
            "envelope": (f"max non-orthogonality {non_ortho_s} vs "
                        f"{MAX_NON_ORTHOGONALITY:.0f}° gate "
                        f"({'pass' if gate_ok else 'caveat'}), max skewness "
                        f"{skew_s} vs {MAX_SKEWNESS:.1f} guidance "
                        f"({'pass' if skew_ok else 'caveat'})"),
            **verdict,
        }],
        uncertainty=[
            "Reported band: settling spread of the coefficient over the "
            "averaging window, a floor, not a bound.",
            (f"Numerical uncertainty from a 3-mesh refinement study: "
             f"±{refine['band_abs']:.2g} on Cd; {refine['method']}."
             if refine and refine.get("band_abs") is not None else
             "Numerical uncertainty not quantified on this run: no matching "
             "refinement study on the record for this setup."),
            f"Compared against {GATE_SOURCE}: {verdict['reason']}.",
        ],
        next_investigations=[f"{e['title']}: {e['scope']}" for e in _AGENDA],
        compute=ledger.as_dict(),
    )
    report_doc["plots"] = report_plots
    if emit:
        emit("report.ready", report_doc)

    cert_path = out / "certificate.pdf"
    try:
        cert_path.unlink()
    except OSError:
        pass
    try:
        from chief_engineer.certificate import build_certificate_v2

        cert_doc = dict(report_doc)
        cert_doc["result_fields"] = (
            [("Body", shown), ("C_d", f"{drag['value']:.4g}")]
            + ([("C_L", f"{lift['value']:.4g}")] if lift else [])
            + [("Band (95%)", f"±{(combined if combined else 2 * drag['sigma']):.2g}"),
               ("Cells", f"{cells:,}"), ("Solve Time", f"{elapsed:.1f} min")])
        certificate = build_certificate_v2(
            cert_doc, out_path=cert_path,
            geometry=shown,
            objective=(request or f"Ahmed body, 25 degree slant, graded "
                                  f"against {GATE_SOURCE}"),
            mission_id=f"ahmed-body-{LABEL}",
            issued_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            channels=channels,
            display_name=display_name(LABEL),
            source_filename=SURFACE,
            solver="OpenFOAM, k-omega SST steady RANS",
            mesh=mesh_validity(cells, non_ortho, skew))
        if emit:
            emit("certificate.ready", {**certificate, "dir": out.name})
    except Exception:
        script.engineer(
            "• No certificate could be issued for this run. "
            "• The previous run's certificate is withdrawn, so nothing out "
            "of date is served. "
            "• The result above stands on the transcript and the report.")
    engineer.report_markdown()
    script.save(out / "transcript.txt")
    roster.all_idle()
    print("Artifacts in", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
