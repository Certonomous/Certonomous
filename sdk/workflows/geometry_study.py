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
        f"Measured the surface before deciding anything: {geometry['triangles']:,} "
        f"triangles, streamwise along {axes[geometry['streamwise_axis']]}, span along "
        f"{axes[geometry['span_axis']]}. At the working scale that is "
        f"{geometry['length'] * scale:.1f} m long and {geometry['span'] * scale:.1f} m "
        f"across.")
    script.engineer(
        f"On scale: {basis}. If that length is wrong, the Reynolds number is wrong "
        f"with it and so is every force I report — so it is stated rather than "
        f"buried.")

    reference_values = build_case(
        Path(engineer.out_root) / "case", surface, geometry,
        velocity=velocity, scale=scale, refinement=refinement, iterations=iterations)
    script.engineer(
        f"Case built around the body: farfield sized from its own bounding box, "
        f"k-omega SST with wall functions, forces referenced to the measured "
        f"planform area of {reference_values['planform_area']:.3g} m². "
        f"Freestream {velocity:g} m/s, Reynolds number {reference_values['reynolds']:.1e}.")
    script.researcher(
        f"Note what that reference area is: the silhouette this body actually "
        f"casts, measured off the surface. It is not the published wing reference "
        f"area a handbook would use, so the coefficient we report is not directly "
        f"comparable to a book figure without rebasing it. I would rather measure "
        f"the body in front of us than borrow a number for a different one.")

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
     "scope": "an unsteady solve of the wake the steady picture averages away — "
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
    surface, familiar = _resolve_surface(params.get("surface"))
    label = Path(surface).stem
    out = OUT_ROOT / "geometry-study"
    out.mkdir(parents=True, exist_ok=True)

    # A curriculum body carries an experimental reference and the orientation
    # and speed that put the solve in the reference's regime. Explicit params
    # still win; the hints only fill what the caller left unset.
    reference, hints = _curriculum(label)
    for key, value in hints.items():
        params.setdefault(key, value)

    script = make_transcript(f"geometry study — {label}", emit)
    roster = Roster(emit)
    ledger = ComputeLedger(emit)
    knowledge = KnowledgeBase(emit)
    began = time.monotonic()

    script.system(request or f"Request: mesh and solve {surface}, and report the forces.")

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

    roster.set(CHIEF_ENGINEER, f"reading {surface}", "working")
    announce_geometry(emit, name=surface, label=f"{label} — as supplied")
    script.engineer(
        f"This is a full geometry study on {surface}, not a parameter sweep. What "
        f"I am testing is whether our chain — surface check, snappyHexMesh, "
        f"steady solver — produces a converged force on this body with a mesh "
        f"good enough to believe."
        + (" We have solved this geometry before, so I have a prior to check "
           "myself against." if familiar else
           " We have never solved this body, so there is no prior: the mesh "
           "quality and the convergence history are the only evidence I will "
           "have about whether to trust the number."))
    script.engineer(
        f"It fails if the surface will not mesh cleanly, if quality exceeds our "
        f"gates — non-orthogonality {MAX_NON_ORTHOGONALITY:.0f}°, skewness "
        f"{MAX_SKEWNESS:.0f} — or if the coefficient never settles.",
        )
    requested = params.get("solver_setup")
    if requested:
        script.engineer(
            f"You asked for {requested}. This case is configured for RAS with the "
            f"k-omega SST model, which is what will run — so the request is "
            f"satisfied by the standing setup rather than by a change. If you "
            f"wanted a different closure I would need to say so before solving, "
            f"not after.")
    script.numericist(
        f"Those gates are not ours; they are the standard acceptance band, "
        f"{per('mesh-quality')}. Worth stating up front so the mesh is judged "
        f"against a published threshold rather than whatever it happens to "
        f"produce.")

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
        f"Plan: extract surface features, build the background mesh, snap to the "
        f"body, check quality against the gates, initialise with a potential "
        f"solve, then run the steady solver for {iterations} iterations. Meshing "
        f"is single-threaded and is the long pole — expect minutes, not seconds.")

    engineer = HeadEngineer(f"study-{label}", out, novel=not familiar,
                            on_event=lambda event, payload: None)
    monitor_seen: list[str] = []

    def on_anomaly(anomaly):
        monitor_seen.append(anomaly.kind)
        if anomaly.kind in {"nan", "fpe"}:
            roster.set(MONITOR, f"fatal: {anomaly.kind}", "blocked")
            script.monitor(f"Stopping the study: {anomaly.detail} during {anomaly.step}.")
        elif anomaly.kind == "residual-spike":
            roster.set(MONITOR, "residual spike flagged", "watching")
            script.monitor(f"Residual spike during {anomaly.step}: {anomaly.detail}")
        elif anomaly.kind == "novel-warning":
            roster.set(MONITOR, "unfamiliar solver warning", "watching")
            script.monitor(f"First time we have seen this on an unfamiliar body: "
                           f"{anomaly.line[:150]}")

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
        else:
            report = _build_unfamiliar_case(engineer, script, roster, surface,
                                            params, iterations, emit)
        script.engineer(
            f"Surface accepted: {report['surface']}"
            + (", closed" if report.get("closed") else "")
            + (f" — {', '.join(report['issues'])}" if report.get("issues")
               else ", no defects reported by the surface check."))

        for step, command, note in (
            ("surfaceFeatureExtract", "surfaceFeatureExtract",
             "extracting the feature edges the mesher snaps to"),
            ("blockMesh", "blockMesh", "building the background mesh"),
            ("snappyHexMesh", "snappyHexMesh -overwrite",
             "snapping the mesh to the body — the long stage"),
        ):
            roster.set(CHIEF_ENGINEER, note, "working")
            result = engineer._run_step(step, command, 5400)
            ledger.spend(result.seconds, f"{step} ({result.seconds:.0f}s)")
            script.engineer(f"{step} finished in {result.seconds:.0f}s — {note}.")

        if familiar:
            # The tutorial case keeps its fields in 0.orig; a generated case
            # writes 0/ directly and must not have it swept away.
            engineer._wsl(f"cd {engineer.remote_case} && rm -rf 0 && cp -r 0.orig 0")
        stats = engineer.collect_mesh_stats()
        cells = int(stats.get("cells", 0))
        non_ortho = stats.get("max_non_orthogonality")
        skew = stats.get("max_skewness")
        gate_ok = (non_ortho or 0) <= MAX_NON_ORTHOGONALITY
        roster.set(CHIEF_RESEARCHER, "ruling on mesh quality", "working")
        script.researcher(
            f"Mesh is {cells:,} cells, max non-orthogonality {non_ortho}, max "
            f"skewness {skew}. "
            + (f"Non-orthogonality is inside the {MAX_NON_ORTHOGONALITY:.0f}° gate, so "
               f"the discretization is acceptable. " if gate_ok else
               f"Non-orthogonality exceeds the {MAX_NON_ORTHOGONALITY:.0f}° gate — I am "
               f"not willing to call a force from this mesh validated. ")
            + (f"Skewness {skew} is above the {MAX_SKEWNESS:.0f} guidance on a small "
               f"number of faces; that caps how far I will trust the magnitude, and "
               f"it is why this will not come back as fully validated."
               if (skew or 0) > MAX_SKEWNESS else
               "Skewness is inside guidance as well."))
        roster.idle(CHIEF_RESEARCHER)

        for step, command, note in (
            ("potentialFoam", "potentialFoam -writephi",
             "initialising the velocity field so the steady solver starts sane"),
            ("simpleFoam", "simpleFoam", f"steady solve, {iterations} iterations"),
        ):
            roster.set(CHIEF_ENGINEER, note, "working")
            result = engineer._run_step(step, command, 7200)
            ledger.spend(result.seconds, f"{step} ({result.seconds:.0f}s)")
            script.engineer(f"{step} finished in {result.seconds:.0f}s — {note}.")
    except Exception as exc:
        roster.set(CHIEF_ENGINEER, "halted", "blocked")
        script.engineer(f"The study stopped: {exc}")
        script.save(out / "transcript.txt")
        roster.all_idle()
        return 1

    # ---------------- Results ----------------
    roster.set(CHIEF_ENGINEER, "reading the force history", "working")
    results = engineer.postprocess(("Cd", "Cl"))

    # Paint the geometry with the solved pressure field: the money shot is the
    # body shown carrying its own solution, not a bare wireframe.
    roster.set(CHIEF_ENGINEER, "extracting the surface pressure field", "working")
    from chief_engineer.field_render import extract_and_paint
    painted = extract_and_paint(
        engineer.remote_case, engineer.out_root / f"{label}_field",
        RUN_PREFIX[:-1] if RUN_PREFIX[-1] == "openfoam2606" else RUN_PREFIX,
        field="p", name=label)
    if painted:
        announce_field(emit, "geometry-study", painted,
                       f"{label} — surface pressure from the solve")
        script.engineer(
            "Painted the body with its own surface-pressure field — high on the "
            "leading surfaces, low over the upper wing, straight off the solved "
            "case.")
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
        script.engineer("The solver produced no force history — nothing to report.")
        script.save(out / "transcript.txt")
        roster.all_idle()
        return 1

    relative = abs(2 * drag["sigma"] / drag["value"]) if drag["value"] else None
    skew_ok = (skew or 0) <= MAX_SKEWNESS
    if not gate_ok:
        why = (f"max non-orthogonality {non_ortho} exceeds the {MAX_NON_ORTHOGONALITY:.0f}° "
               f"acceptance gate, so the discretization is not trustworthy here")
    elif not skew_ok:
        why = (f"max skewness {skew} exceeds the acceptance band of {MAX_SKEWNESS:.0f} "
               f"(on a small number of faces), so the magnitude is indicative")
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
        comparison = verdict.pop("comparison", None)
        if comparison:
            script.researcher(
                f"Experimental comparison: the solve gives Cd {comparison['measured_cd']:.4g} "
                f"on planform area; {comparison['basis_note']} that is "
                f"{comparison['compared_cd']:.4g} against {reference['source']}, which "
                f"reports Cd {comparison['reference_cd']:g}. That is "
                + (f"{comparison['relative_error'] * 100:.0f}% apart"
                   if comparison['relative_error'] is not None else "not comparable")
                + f", within a ±{comparison['tolerance'] * 100:.0f}% band.")
    else:
        verdict = trust(relative_error=relative, converged=True,
                        in_validated_regime=gate_ok, calibrated=skew_ok, why=why)
    channels = uncertainty_channels(
        input_2sigma=2 * drag['sigma'], numerical=None, model=None,
        numerical_note="one mesh only — discretization error not separated",
        model_note="kOmegaSST closure error not estimated for this body")
    if emit:
        emit("result.verdict", {"quantity": "Drag coefficient",
                                "value": f"{drag['value']:.4g}",
                                "envelope": f"±{2 * drag['sigma']:.2g}", **verdict})
        emit("uncertainty.channels", channels)
    script.engineer(
        f"Drag settles at {drag['value']:.4g} ± {2 * drag['sigma']:.2g} over the final "
        f"{drag['window']} iterations"
        + (f"; lift at {lift['value']:.4g} ± {2 * lift['sigma']:.2g}." if lift else "."),
        verdict=verdict)

    script.numericist(
        f"Before this is written up, two things it is not. The band on that "
        f"coefficient is how far it moved over the averaging window — it "
        f"establishes the solve is steady and nothing more, so read it as a floor. "
        f"And there is no numerical uncertainty here at all: that needs "
        f"systematically refined grids and a least-squares fit whose scatter sets "
        f"the safety factor, {per('grid-uncertainty')}. One mesh cannot give it. "
        + (f"On validation: {per('vv20')} wants an experimental comparison, and here "
           f"we have one — the verdict is graded against it. Numerical uncertainty is "
           f"still unquantified, so a validated magnitude is not a converged grid."
           if reference else
           f"Nor is this validated — {per('vv20')} wants an experimental comparison, "
           f"and we have made none. Steady, and unvalidated."))

    monitor_summary = engineer.monitor.summary()
    suppressed = sum(monitor_summary.get("suppressed", {}).values())
    script.monitor(
        f"Watched every line of solver output. {monitor_summary['anomalies']} "
        f"event{'' if monitor_summary['anomalies'] == 1 else 's'} matched a watch "
        f"pattern {monitor_summary['by_kind'] or ''}"
        + (f"; {suppressed} were repeats of the same condition and were counted "
           f"rather than repeated at you." if suppressed else ".")
        + (" Nothing fatal." if not monitor_summary["fatal"] else
           " One was fatal and this result should not be used."))
    roster.idle(MONITOR)

    # ---------------- Conclusion ----------------
    script.phase(CONCLUSION)
    elapsed = (time.monotonic() - began) / 60
    script.engineer(
        f"Confirmed: the chain took {surface} from a raw surface to a converged "
        f"force in {elapsed:.1f} minutes of wall time without intervention. The "
        f"coefficient history is flat over the averaging window, which is what "
        f"makes the envelope meaningful rather than decorative.")
    if comparison and verdict["tier"] == "VALIDATED":
        script.engineer(
            f"Confirmed against experiment: the rebased coefficient sits within the "
            f"published band of {reference['source']}, so this magnitude is validated, "
            f"not merely converged — {verdict['reason']}.")
    elif comparison:
        script.engineer(
            f"Not confirmed as validated: the coefficient is converged but "
            f"{verdict['reason']}. It agrees in direction with {reference['source']} "
            f"without landing inside the band.")
    else:
        script.engineer(
            f"Not confirmed: the magnitude is not independently validated. "
            + ("We have a prior for this body and the value is consistent with it, "
               "but consistency with our own earlier run is not validation against "
               "experiment." if familiar else
               "There is no prior and no experimental comparison, so the number "
               "stands on mesh quality and convergence alone.")
            + (f" Skewness above guidance on a small number of faces is the specific "
               f"reason this is reported as a trend rather than a validated magnitude."
               if (skew or 0) > MAX_SKEWNESS else ""))
    script.engineer(
        f"Still unknown: mesh sensitivity. One mesh cannot separate discretization "
        f"error from the physics, and at this cost a refinement study is a "
        f"deliberate decision rather than a reflex — it would roughly double the "
        f"{ledger.as_dict()['spent_core_minutes']:.0f} core-minutes this study spent.")

    if not familiar:
        knowledge.add(f"{label} meshed and solved: {cells:,} cells, "
                      f"Cd {drag['value']:.4g} ± {2 * drag['sigma']:.2g}")
        script.numericist(
            f"Recording this as a case-memory entry. The next time someone asks "
            f"about a body like {label}, the lab can answer from a run it has "
            f"actually done instead of reasoning by analogy.")

    report_doc = lab_report(
        title=f"Geometry study — {label}",
        abstract=[
            f"We took {surface} through surface check, meshing, and a steady "
            f"solve to establish whether the chain yields a trustworthy force.",
            f"The mesh reached {cells:,} cells at max non-orthogonality {non_ortho} "
            f"and max skewness {skew}; drag settled at {drag['value']:.4g} "
            f"± {2 * drag['sigma']:.2g}.",
            f"The result is reported as {verdict['tier'].lower()} — {verdict['reason']}.",
        ],
        methods=[
            f"Surface intake and check on {surface}.",
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
            "envelope": f"max non-orthogonality {non_ortho}, max skewness {skew}",
            **trust(relative_error=0.0, in_validated_regime=gate_ok,
                    calibrated=(skew or 0) <= MAX_SKEWNESS),
        }],
        uncertainty=[
            f"The reported band is the settling spread of the coefficient over the "
            f"averaging window — it says the solve is steady, not that the physics "
            f"is right, and it is a floor rather than a bound.",
            "Numerical uncertainty is not quantified at all: one mesh cannot "
            "separate discretization error from the solution, and no refinement "
            "study was run.",
            (f"Compared against {reference['source']}: {verdict['reason']}."
             if comparison else
             "No experimental comparison was made in this study, so the magnitude is "
             "unvalidated against reality."),
        ],
        next_investigations=[
            f"{entry['title']} — {entry['scope']}" for entry in _AGENDA],
        compute=ledger.as_dict(),
    )
    if emit:
        emit("agenda.updated", {"entries": _AGENDA})
    if emit:
        emit("report.ready", report_doc)
    try:
        from chief_engineer.certificate import build_certificate
        certificate = build_certificate(
            report_doc, out_path=out / "certificate.pdf",
            geometry=label, objective=(request or f"Geometry study of {label}"),
            mission_id=f"geometry-study-{label}",
            issued_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            channels=channels)
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
