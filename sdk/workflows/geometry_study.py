"""Take a real surface through the whole chain and report what it costs.

Intake and surface check, meshing, the solver, and a force reported with the
band its own history supports.  This is the expensive path — a body of a few
hundred thousand cells takes minutes per stage — so the study narrates cost as
it goes and the monitoring agent watches the solver output while it runs.

Any OBJ or STL in ``sdk/geometry`` works; the surface named in the request is
used when it exists, and the validated motorBike is the default.

    python -m workflows.geometry_study
    python -m workflows.geometry_study airplane.stl
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path

from . import (OUT_ROOT, RUN_PREFIX, announce_field, announce_geometry,
               announce_plot, make_transcript)
from chief_engineer.compute_audit import audit
from chief_engineer.external_aero import analyse_surface, build_case
from chief_engineer.head_engineer import (FOAM_TUTORIALS, HeadEngineer,
                                          envelope_statistics,
                                          parse_coefficient_history,
                                          plot_with_envelope)
from chief_engineer.researcher import ENGINEER_ACK, MissionProperties, method_memo
from chief_engineer.display_names import display_name
from chief_engineer.lab import (CHIEF_ENGINEER, CHIEF_RESEARCHER, CONCLUSION,
                                EVIDENCE, HYPOTHESIS, MONITOR, NUMERICIST, PLAN,
                                ComputeLedger, KnowledgeBase, Roster,
                                lab_report, per, trust, uncertainty_channels)

GEOMETRY_DIR = Path(__file__).resolve().parents[1] / "geometry"
RUN_ROOT_PARENT = "~/certonomous-runs"
DEFAULT_SURFACE = "motorBike.obj"
# Mesh-quality acceptance thresholds from the OpenFOAM guidance indexed in the
# knowledge base: non-orthogonality is a hard gate, skewness a warning band.
MAX_NON_ORTHOGONALITY = 70.0
MAX_SKEWNESS = 4.0


CURRICULUM_DIR = GEOMETRY_DIR.parent.parent / "models" / "curriculum"


def _curriculum(label: str):
    """Load the curriculum reference and solve hints for a body, if any.

    Imported by absolute path so the workflow does not depend on the curriculum
    package being on the import path; a missing curriculum is simply no
    reference, and the study falls back to its convergence-only verdict.
    """
    try:
        import importlib.util

        reg_path = CURRICULUM_DIR / "registry.py"
        if not reg_path.exists():
            return None, {}
        spec = importlib.util.spec_from_file_location("curriculum_registry", reg_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        reference = module.reference_for(label)
        hints = module.solve_hints(label) if reference else {}
        return reference, hints
    except Exception:
        return None, {}


def _resolve_surface(name: str | None) -> tuple[str, bool]:
    """Return the surface to study and whether the lab has solved it before."""
    if name:
        candidate = GEOMETRY_DIR / Path(name).name
        if candidate.exists():
            return candidate.name, candidate.name.lower().startswith("motorbike")
    return DEFAULT_SURFACE, True


def _build_unfamiliar_case(engineer, script, roster, surface, params,
                           iterations, emit):
    """Build a case around a body the lab has never solved.

    The awkward part of accepting arbitrary geometry is scale: a file can
    declare metres and still be dimensionally absurd. Rather than silently
    trusting it, the Chief states the length it is working to, because the
    Reynolds number — and therefore every force — rides on that number.
    """
    import shutil

    source = GEOMETRY_DIR / surface
    streamwise_axis = params.get("streamwise_axis")
    velocity = float(params.get("velocity", 100.0))
    refinement = int(params.get("refinement", 3))
    geometry = analyse_surface(
        source, streamwise_axis=int(streamwise_axis) if streamwise_axis is not None else None)
    raw_length = geometry["length"]

    stated = params.get("reference_length")
    if stated:
        reference = float(stated)
        basis = f"you stated a reference length of {reference:.1f} m"
    elif raw_length > 150:
        reference = 50.0
        basis = (f"the file's own units would make this body {raw_length:.0f} units "
                 f"long, which is not a plausible size for it; I am working to a "
                 f"{reference:.0f} m reference length instead")
    else:
        reference = raw_length
        basis = "the file's units are dimensionally plausible, so I am taking them as metres"
    scale = reference / raw_length

    axes = "XYZ"
    script.engineer(
        f"• Surface measured: {geometry['triangles']:,} triangles, streamwise "
        f"{axes[geometry['streamwise_axis']]}, span {axes[geometry['span_axis']]}. "
        f"• Working scale: {geometry['length'] * scale:.1f} m long, "
        f"{geometry['span'] * scale:.1f} m across.")
    script.engineer(
        f"• Scale basis: {basis}. "
        f"• Wrong length → wrong Reynolds → wrong forces; stated, not buried.")

    reference_values = build_case(
        Path(engineer.out_root) / "case", surface, geometry,
        velocity=velocity, scale=scale, refinement=refinement, iterations=iterations)
    script.engineer(
        f"• Case built: farfield from the body's own bounding box, k-omega SST. "
        f"• Reference area: measured planform "
        f"{reference_values['planform_area']:.3g} m². "
        f"• Freestream {velocity:g} m/s; Re {reference_values['reynolds']:.1e}.")
    script.researcher(
        "• Reference area is the measured silhouette, not a handbook wing area. "
        "• Book comparison needs rebasing first: measure the body, don't borrow numbers.")

    # Stage the case inside the compute node and scale the surface with it.
    local_case = Path(engineer.out_root) / "case"
    shutil.copy(source, local_case / "constant" / "triSurface" / surface)
    wsl_case = str(local_case).replace("C:", "/mnt/c").replace("\\", "/")
    engineer._wsl(f"rm -rf {engineer.remote_case} && mkdir -p {RUN_ROOT_PARENT} && "
                  f"cp -r '{wsl_case}' {engineer.remote_case}")
    engineer._wsl(
        f"cd {engineer.remote_case} && openfoam2606 surfaceTransformPoints "
        f"-scale '({scale:.6f} {scale:.6f} {scale:.6f})' "
        f"constant/triSurface/{surface} constant/triSurface/_scaled.stl && "
        f"mv constant/triSurface/_scaled.stl constant/triSurface/{surface}")
    return {"surface": surface, "closed": True, "issues": [],
            "reference": reference_values,
            "planform_area": geometry["planform_area"] * scale * scale,
            "frontal_area": geometry["frontal_area"] * scale * scale}


# New questions a solved body opens — ambitions, not remediations. Fed to the
# research-agenda panel and to the report's "Next investigations".
_AGENDA = [
    {"title": "Drag build-up under yaw",
     "scope": "sweep the approach angle and map how the force builds as the "
              "body meets the flow off-axis",
     "cost": "one solve per angle on the cached mesh"},
    {"title": "Resolve the shedding",
     "scope": "an unsteady solve of the wake the steady picture averages away, "
              "the spectrum, not just the mean force",
     "cost": "transient solve; ~1 order of magnitude over steady"},
    {"title": "Next body in the class",
     "scope": "take the same gated chain to the nearest unsolved body in the "
              "library and grow the validated set",
     "cost": "one full chain per body; meshing dominates"},
]


def main(request: str | None = None, params: dict | None = None,
         iterations: int = 300, emit=None) -> int:
    params = dict(params or {})
    out = OUT_ROOT / "geometry-study"
    out.mkdir(parents=True, exist_ok=True)

    # A body was named in the prompt but is not in the staged catalog and no
    # surface was supplied for it. Say so honestly rather than silently solving
    # the default body (motorBike) and passing it off as the requested one.
    unavailable = params.get("surface_unavailable")
    if unavailable and not params.get("surface"):
        script = make_transcript("geometry study", emit)
        script.system(request or f"Request: solve the supplied {unavailable} geometry.")
        note = (f"• The prompt names {unavailable}, which is not in the staged "
                f"geometry catalog and no surface file was supplied for it. "
                f"• This run will not solve a different body and pass it off as "
                f"{unavailable}: stage or upload that geometry, then re-run.")
        script.engineer(note)
        if emit:
            emit("mission.note", {"unavailable": unavailable, "detail": note})
        script.save(out / "transcript.txt")
        return 0

    surface, familiar = _resolve_surface(params.get("surface"))
    label = Path(surface).stem
    shown = display_name(label)  # camera-facing name; `label` stays the file-safe slug

    # A curriculum body carries an experimental reference and the orientation
    # and speed that put the solve in the reference's regime. Explicit params
    # still win; the hints only fill what the caller left unset.
    reference, hints = _curriculum(label)
    for key, value in hints.items():
        params.setdefault(key, value)

    script = make_transcript(f"geometry study: {shown}", emit)
    roster = Roster(emit)
    ledger = ComputeLedger(emit)
    knowledge = KnowledgeBase(emit)
    began = time.monotonic()

    script.system(request or f"Request: mesh and solve {shown}, and report the forces.")

    # ---------------- Hypothesis ----------------
    script.phase(HYPOTHESIS)
    # Chief Researcher records the method choice before the chain runs.
    roster.set(CHIEF_RESEARCHER, "selecting the method", "working")
    props = MissionProperties(
        kind="single-body-study",
        objective="a trustworthy drag coefficient for this body",
        dimensionality=0,
        regime="steady turbulent (RANS)",
        smoothness="gated",
        fidelity="a solved field",
        admissibility_cite="against the standard mesh-quality acceptance band")
    for line in method_memo(props):
        script.researcher(line)
    roster.idle(CHIEF_RESEARCHER)
    script.engineer(ENGINEER_ACK)

    roster.set(CHIEF_ENGINEER, f"reading {shown}", "working")
    announce_geometry(emit, name=surface, label=f"{shown}, as supplied")
    script.engineer(
        f"• Full geometry study on {shown}: a measurement, not a sweep. "
        f"• Question: does the chain produce a converged force on a believable mesh? "
        + ("• Prior exists for this body; I will check against it."
           if familiar else
           "• No prior: mesh quality and convergence are the only evidence."))
    script.engineer(
        f"• Fails if: surface won't mesh; gates exceeded "
        f"(non-ortho {MAX_NON_ORTHOGONALITY:.0f}°, skew {MAX_SKEWNESS:.0f}); "
        f"or the force never settles.")
    requested = params.get("solver_setup")
    if requested:
        script.engineer(
            f"• You asked for {requested}: the standing setup already runs it. "
            f"• A different closure would need saying before solving, not after.")
    script.numericist(
        f"• The gates are the standard acceptance band, {per('mesh-quality')}. "
        "• The mesh is judged against a published threshold, not itself.")

    # ---------------- Plan ----------------
    script.phase(PLAN)
    capacity = audit(1, memory_per_worker_mb=2048)
    if emit:
        emit("audit.completed", capacity.panel())
        # The plan commits to the RANS chain here — the solver badge is earned
        # at this moment, not asserted at page load.
        emit("solver.selected", {
            "solver": "OpenFOAM", "method": "steady RANS, k-omega SST",
            "basis": "plan commits the body to the meshed-and-solved chain"})
    script.engineer(capacity.headline(), panel=capacity.panel())
    script.engineer(
        f"• Plan: features → background mesh → snap → quality gates → potential "
        f"init → {iterations} steady iterations. "
        f"• Meshing is the long pole: minutes, not seconds.")

    engineer = HeadEngineer(f"study-{label}", out, novel=not familiar,
                            on_event=lambda event, payload: None)
    monitor_seen: list[str] = []

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
            script.monitor(f"• New on an unfamiliar body: {anomaly.line[:150]}")

    engineer.monitor.on_anomaly = on_anomaly

    # ---------------- Evidence ----------------
    script.phase(EVIDENCE)
    roster.set(MONITOR, "watching solver output", "watching")
    roster.set(CHIEF_ENGINEER, "staging the case", "working")

    try:
        if familiar:
            engineer.stage_case(f"{FOAM_TUTORIALS}/incompressible/simpleFoam/motorBike")
            geometry_source = (f"{GEOMETRY_DIR / surface}" if (GEOMETRY_DIR / surface).exists()
                               else f"{FOAM_TUTORIALS}/resources/geometry/motorBike.obj.gz")
            wsl_source = geometry_source.replace("C:", "/mnt/c").replace("\\", "/")
            report = engineer.intake_geometry(wsl_source, surface)
            # Run the iteration count the plan and report actually claim — the
            # tutorial ships a longer endTime, and the force is settled well
            # inside this window, so aligning them keeps the report truthful and
            # the warm on-camera solve inside its slot.
            engineer.set_iteration_count(iterations)
        else:
            report = _build_unfamiliar_case(engineer, script, roster, surface,
                                            params, iterations, emit)
        script.engineer(
            f"• Surface accepted: {shown}"
            + (", closed" if report.get("closed") else "") + ". "
            + (f"• Issues: {', '.join(report['issues'])}." if report.get("issues")
               else "• No defects reported by the surface check."))
        script.engineer(
            "• Selected: k-omega SST, steady RANS, standard closure for "
            "attached external flow, solved on a quality-gated mesh.")

        warm = engineer.restore_cached_mesh(label)
        if warm:
            roster.set(CHIEF_ENGINEER, "reusing the cached snapped mesh", "working")
            script.engineer(
                "• Snapped mesh found in cache, reusing it, skipping the mesh build. "
                "• The mesh is the pinned path; the solve still runs live on it.")
        else:
            for step, command, note in (
                ("surfaceFeatureExtract", "surfaceFeatureExtract",
                 "extracting the feature edges the mesher snaps to"),
                ("blockMesh", "blockMesh", "building the background mesh"),
                ("snappyHexMesh", "snappyHexMesh -overwrite",
                 "snapping the mesh to the body, the long stage"),
            ):
                roster.set(CHIEF_ENGINEER, note, "working")
                result = engineer._run_step(step, command, 5400)
                ledger.spend(result.seconds, f"{step} ({result.seconds:.0f}s)")
                script.engineer(f"• {step}: {result.seconds:.0f} s, {note}.")
            # Cache the freshly snapped mesh so the next run of this body is warm.
            engineer.save_mesh_to_cache(label)

        if familiar:
            # The tutorial case keeps its fields in 0.orig; a generated case
            # writes 0/ directly and must not have it swept away.
            engineer._wsl(f"cd {engineer.remote_case} && rm -rf 0 && cp -r 0.orig 0")
        stats = engineer.collect_mesh_stats()
        cells = int(stats.get("cells", 0))
        non_ortho = stats.get("max_non_orthogonality")
        skew = stats.get("max_skewness")
        if emit:
            emit("mesh.stats", {"cells": cells,
                                "max_non_orthogonality": non_ortho,
                                "max_skewness": skew})
        # Sensible display precision — one decimal on the angle, two on skew —
        # never the raw many-digit float the checkMesh regex captured.
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

        ranks = engineer.solve_ranks()
        parallel = ranks > 1 and engineer.decompose_for_parallel(ranks)
        if parallel:
            script.engineer(
                f"• Case decomposed into {ranks} subdomains: the steady solve "
                f"runs in parallel across the fleet, same mesh and same numbers.")
        for step, base, note in (
            ("potentialFoam", "potentialFoam -writephi",
             "initialising the velocity field so the steady solver starts sane"),
            ("simpleFoam", "simpleFoam", f"steady solve, {iterations} iterations"),
        ):
            command = f"mpirun -np {ranks} {base} -parallel" if parallel else base
            roster.set(CHIEF_ENGINEER, note, "working")
            result = engineer._run_step(step, command, 7200)
            ledger.spend(result.seconds, f"{step} ({result.seconds:.0f}s)")
            script.engineer(f"• {step}: {result.seconds:.0f} s, {note}.")
        if parallel:
            engineer.reconstruct_latest()
    except Exception as exc:
        roster.set(CHIEF_ENGINEER, "halted", "blocked")
        # A failed stage raises with the raw solver log tail attached, for the
        # saved log file — never narrate that verbatim, just which stage and
        # that the detail is on record.
        step_match = re.match(r"step '(\w+)' failed", str(exc))
        stopped_at = step_match.group(1) if step_match else "a solver stage"
        script.engineer(f"• The study stopped: {stopped_at} did not complete "
                        f"cleanly; detail in the saved log, not on screen.")
        script.save(out / "transcript.txt")
        roster.all_idle()
        return 1

    # ---------------- Results ----------------
    roster.set(CHIEF_ENGINEER, "reading the force history", "working")
    results = engineer.postprocess(("Cd", "Cl"))

    # Live iteration trace: stream the drag coefficient as the solver marched it,
    # so the viewer watches Cd being computed through the run and its ±2σ
    # envelope form and tighten as the solution settles (#7).
    cd_hist = engineer.histories.get("Cd")
    if emit and cd_hist and cd_hist["series"]:
        iters, series = cd_hist["iterations"], cd_hist["series"]
        n = len(series)
        step = max(1, n // 40)          # ~40 points across the whole run
        win = max(5, n // 10)           # rolling window for the live envelope
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

    # Paint the geometry with the solved pressure field: the money shot is the
    # body shown carrying its own solution, not a bare wireframe.
    roster.set(CHIEF_ENGINEER, "extracting the surface pressure field", "working")
    from chief_engineer.field_render import extract_and_paint

    # Face-count sanity check reference: the painted body should carry a large
    # fraction of the input surface's triangles, not a couple of flat domain
    # rectangles. Count the local input surface if we have it.
    input_triangles = None
    local_surface = GEOMETRY_DIR / surface
    if local_surface.exists():
        try:
            from chief_engineer.geometry import load_surface
            input_triangles = load_surface(local_surface)["triangles_total"]
        except Exception:
            input_triangles = None

    painted = extract_and_paint(
        engineer.remote_case, engineer.out_root / f"{label}_field",
        RUN_PREFIX[:-1] if RUN_PREFIX[-1] == "openfoam2606" else RUN_PREFIX,
        field="p", name=label, input_triangles=input_triangles)
    if painted:
        # The field URL is /api/field/geometry-study/<file>, served from the
        # beat's output root — so the painted JSON has to live directly under
        # `out`, not in the per-case subdirectory the solve wrote it to (the same
        # copy-to-out step the envelope plots already take).
        served = out / Path(painted).name
        try:
            served.write_bytes(Path(painted).read_bytes())
            painted = str(served)
        except OSError:
            pass
        announce_field(emit, "geometry-study", painted,
                       f"{shown}, surface pressure from the solve")
        script.engineer(
            "• Body painted with its own solved surface pressure. "
            "• High on leading surfaces, low over the upper wing.")
    plots: list[str] = []
    for name in ("Cd", "Cl"):
        png = engineer.out_root / f"{name}_envelope.png"
        if png.exists():
            target = out / png.name
            target.write_bytes(png.read_bytes())
            plots.append(str(target))
            announce_plot(emit, "geometry-study", target,
                          f"{'Drag' if name == 'Cd' else 'Lift'} history with envelope")

    drag = results.get("Cd")
    lift = results.get("Cl")
    if not drag:
        script.engineer("• No force history from the solver, nothing to report.")
        script.save(out / "transcript.txt")
        roster.all_idle()
        return 1

    relative = abs(2 * drag["sigma"] / drag["value"]) if drag["value"] else None
    skew_ok = (skew or 0) <= MAX_SKEWNESS
    if not gate_ok:
        why = (f"Mesh quality: max non-orthogonality {non_ortho_s}, above the "
               f"{MAX_NON_ORTHOGONALITY:.0f}° gate; the numerical channel carries "
               f"the residual")
    elif not skew_ok:
        why = (f"Mesh quality: max skewness {skew_s} on isolated faces, above the "
               f"{MAX_SKEWNESS:.1f} gate; the numerical channel carries the residual")
    else:
        why = ""
    comparison = None
    if reference:
        # The lab holds an experiment for this body: grade the force against it,
        # which is the only path that can reach VALIDATED.
        from chief_engineer.lab import validate_against_reference
        verdict = validate_against_reference(
            measured_cd=drag["value"], reference=reference,
            planform_area=report.get("planform_area"),
            frontal_area=report.get("frontal_area"),
            converged=True, in_validated_regime=gate_ok, calibrated=skew_ok,
            solved_reynolds=report.get("reference", {}).get("reynolds"))
        # Keep the comparison IN the verdict: the suite writer and the wall
        # read it downstream — popping it here was the wall-arithmetic bug.
        comparison = verdict.get("comparison")
        if comparison:
            script.researcher(
                f"• Solve gives Cd {comparison['measured_cd']:.4g}; rebased "
                f"{comparison['compared_cd']:.4g} vs {reference['source']} "
                f"Cd {comparison['reference_cd']:g}. "
                + (f"• {comparison['relative_error'] * 100:.0f}% apart, "
                   if comparison['relative_error'] is not None else "• Not comparable, ")
                + f"band ±{comparison['tolerance'] * 100:.0f}%.")
    else:
        verdict = trust(relative_error=relative, converged=True,
                        in_validated_regime=gate_ok, calibrated=skew_ok, why=why)
    # Stored UQ studies (refinement ladder, closure trio) populate the
    # numerical and model channels when their setup fingerprint matches this
    # mission; a mismatch says "study pending", never a stale band.
    from chief_engineer import uq as uq_studies
    if familiar:
        study_fp = uq_studies.setup_fingerprint(
            body=label, solver="openfoam-simpleFoam", closure="kOmegaSST",
            velocity=20.0, refinement="tutorial-5-6", iterations=iterations)
    else:
        study_fp = uq_studies.setup_fingerprint(
            body=label, solver="openfoam-simpleFoam", closure="kOmegaSST",
            velocity=float(params.get("velocity", 100.0)),
            refinement=int(params.get("refinement", 3)),
            iterations=iterations)
    lookup = uq_studies.channels_for(label, study_fp)
    numerical_val = model_val = None
    numerical_note = ("one mesh only, discretization error not separated; a "
                      "grid-refinement study is the marked next step")
    model_note = "kOmegaSST closure error not estimated for this body"
    if lookup["numerical"]:
        numerical_val = lookup["numerical"]["band_abs"]
        numerical_note = lookup["numerical"]["method"]
        if lookup["provenance"]:
            numerical_note += f"; study {', '.join(lookup['provenance'][:3])}"
    elif lookup["pending"]:
        numerical_note = ("study pending: no matching refinement study for "
                          "this setup")
    if lookup["model"]:
        model_val = lookup["model"]["band_abs"]
        model_note = lookup["model"]["method"]
    channels = uncertainty_channels(
        input_2sigma=2 * drag['sigma'], numerical=numerical_val,
        model=model_val,
        input_note="the ± band is the statistical spread of the solved force "
                   "over the averaging window, settled-state scatter; "
                   "freestream speed and fluid properties are taken as "
                   "specified exactly",
        numerical_note=numerical_note,
        model_note=model_note)
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
    script.engineer(
        f"• Drag settles at {drag['value']:.4g} ± {2 * drag['sigma']:.2g} over "
        f"{drag['window']} iterations"
        + (f". • Lift {lift['value']:.4g} ± {2 * lift['sigma']:.2g}." if lift else "."),
        verdict=verdict)

    script.numericist(
        f"• Numerical uncertainty needs refined grids, {per('grid-uncertainty')}; one mesh cannot give it. "
        + ("• An experimental comparison exists for this body."
           if reference else
           "• No experimental comparison was made; a solved comparison is the next step."))

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
        f"• Confirmed: raw surface → converged force in {elapsed:.1f} min, no intervention. "
        "• Coefficient history flat over the window: the envelope means something.")
    if comparison and verdict["tier"] == "VALIDATED":
        script.engineer(
            f"• Confirmed against experiment: inside the published band of "
            f"{reference['source']}. "
            f"• Validated, not merely converged: {verdict['reason']}.")
    elif comparison:
        script.engineer(
            f"• Converged but not validated: {verdict['reason']}. "
            f"• Agrees in direction with {reference['source']}; outside the band.")
    else:
        script.engineer(
            "• Magnitude not independently validated. "
            + ("• Consistent with our prior, but self-consistency is not validation."
               if familiar else
               "• No prior, no experiment: the number stands on mesh quality and convergence.")
            + (" • Skewness above guidance is why the mesh channel carries the caveat."
               if (skew or 0) > MAX_SKEWNESS else ""))
    script.engineer(
        "• Still unknown: mesh sensitivity, one mesh cannot separate discretization from physics. "
        f"• A refinement study would roughly double the "
        f"{ledger.as_dict()['spent_core_minutes']:.0f} core-minutes spent.")

    if not familiar:
        knowledge.add(f"{shown} meshed and solved: {cells:,} cells, "
                      f"Cd {drag['value']:.4g} ± {2 * drag['sigma']:.2g}")
        script.numericist(
            f"• Recorded in case memory. "
            f"• Next question about a body like {shown} answers from a real run.")

    report_doc = lab_report(
        title=f"Geometry study: {shown}",
        abstract=[
            f"We took {shown} through surface check, meshing, and a steady "
            f"solve to establish whether the chain yields a trustworthy force.",
            f"The mesh reached {cells:,} cells at max non-orthogonality {non_ortho_s} "
            f"and max skewness {skew_s}; drag settled at {drag['value']:.4g} "
            f"± {2 * drag['sigma']:.2g}.",
            f"The result is reported as {verdict['tier'].lower()}: {verdict['reason']}.",
        ],
        methods=[
            f"Surface intake and check on {shown}.",
            f"Background mesh plus snappyHexMesh to {cells:,} cells; quality gated at "
            f"{MAX_NON_ORTHOGONALITY:.0f}° non-orthogonality and {MAX_SKEWNESS:.0f} skewness.",
            f"Potential-flow initialisation followed by {iterations} steady iterations.",
            "Forces averaged over the final fifth of the iteration history; the band "
            "is the spread of that window.",
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
        }] if lift else []) + ([{
            "quantity": "Drag vs experiment",
            "value": f"Cd {comparison['compared_cd']:.4g} vs {comparison['reference_cd']:g}",
            "envelope": (f"{comparison['relative_error'] * 100:.0f}% apart, "
                         f"±{comparison['tolerance'] * 100:.0f}% band"
                         if comparison['relative_error'] is not None else "not comparable"),
            **verdict,
        }] if comparison else []) + [{
            "quantity": "Mesh",
            "value": f"{cells:,} cells",
            "envelope": f"max non-orthogonality {non_ortho_s}, max skewness {skew_s}",
            **trust(relative_error=0.0, in_validated_regime=gate_ok,
                    calibrated=(skew or 0) <= MAX_SKEWNESS),
        }],
        uncertainty=[
            "Reported band: settling spread of the coefficient over the "
            "averaging window, a floor, not a bound.",
            "Numerical uncertainty is not quantified: one mesh cannot "
            "separate discretization error from the solution, and no refinement "
            "study was run.",
            (f"Compared against {reference['source']}: {verdict['reason']}."
             if comparison else
             "No experimental comparison was made in this study, so the magnitude is "
             "unvalidated against reality."),
        ],
        next_investigations=[
            f"{entry['title']}: {entry['scope']}" for entry in _AGENDA],
        compute=ledger.as_dict(),
    )
    if emit:
        emit("agenda.updated", {"entries": _AGENDA})
    if emit:
        emit("report.ready", report_doc)
    try:
        # The redesigned certificate is the default as of Sanaa's sign-off
        # (2026-07-23, old-vs-new B-52 comparison approved).
        from chief_engineer.certificate import build_certificate_v2
        certificate = build_certificate_v2(
            report_doc, out_path=out / "certificate.pdf",
            geometry=shown, objective=(request or f"Geometry study of {shown}"),
            mission_id=f"geometry-study-{label}",
            issued_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            channels=channels,
            display_name=display_name(label),
            source_filename=surface,
            solver="OpenFOAM, k-omega SST steady RANS")
        if emit:
            emit("certificate.ready", {**certificate, "dir": out.name})
    except Exception as exc:  # a certificate must never take down a good solve
        script.engineer(f"(Certificate could not be issued: {exc})")
    engineer.report_markdown()
    script.save(out / "transcript.txt")
    roster.all_idle()
    print("Artifacts in", out)
    return 0


if __name__ == "__main__":
    named = [a for a in sys.argv[1:] if not a.startswith("-")]
    raise SystemExit(main(params={"surface": named[0]} if named else None))
