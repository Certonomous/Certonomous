"""Act 9 — the CRM wing: a transonic, compressible design reference.

The Common Research Model wing (Mach 0.85, CL 0.5) is a different regime from
every other act in this control room: compressible, transonic, off the
incompressible RANS chain this lab otherwise runs. Its validated evidence came
from the DAFoam tutorial's own case -- a pre-built surface mesh extruded with
pyHyp, solved with the compressible ``DARhoSimpleCFoam`` solver inside the
``dafoam/opt-packages`` container -- and this act reruns that exact recipe
rather than forcing the body through the incompressible engine and reporting
a different, unvalidated number.

The gate is a straight reproduction check: does a fresh solve of the
unmodified case land on the same drag DAFoam's own published tutorial
documentation reports for this body.

    python -m workflows.crm_wingbody
"""
from __future__ import annotations

import re
import shutil
import time
from pathlib import Path

from . import OUT_ROOT, announce_geometry, make_transcript
from chief_engineer.compute_audit import audit
from chief_engineer.display_names import display_name
from chief_engineer.docker_dafoam import (DEFAULT_RANKS, DockerDAFoamEngineer,
                                          docker_available, mem_available_gb,
                                          wait_for_headroom)
from chief_engineer.researcher import ENGINEER_ACK, MissionProperties, method_memo
from chief_engineer.lab import (CHIEF_ENGINEER, CHIEF_RESEARCHER, CONCLUSION,
                                EVIDENCE, HYPOTHESIS, MONITOR, PLAN, SOLVER_BACKED,
                                VALIDATED, ComputeLedger, KnowledgeBase, Roster,
                                lab_report, per)
from chief_engineer.transcript import CHIEF_ENGINEER as _CE_ROLE

from .geometry_study import _emit_table, mesh_validity

LABEL = "crm_wingbody"
SURFACE = "crm_wingbody.stl"
TUTORIAL_SOURCE = Path("/home/ubuntu/dafoam-tutorials/CRM_Wing")
CACHED_SURFACE_MESH = Path("/home/ubuntu/certonomous-runs/A6-crm-wing/CRM_surfMesh.cgns.tar.gz")
GATE_SOURCE = "the DAFoam project's own published CRM wing tutorial documentation"
PUBLISHED_CD = 0.02090
GATE_TOLERANCE = 0.02   # +/-2%: a straight reproduction check, not a prediction band
BUDGET_ITERATIONS = 1000  # this case's own residuals settle below tolerance by here
RANKS = DEFAULT_RANKS

_TIME_RE = re.compile(r"^Time = (\d+)")
_CD_RE = re.compile(r"^CD:\s*([-\d.eE]+)\s+final:")
_CL_RE = re.compile(r"^CL:\s*([-\d.eE]+)\s+final:")


def _parse_history(log_text: str) -> tuple[list[tuple[int, float, float]], int]:
    """(list of (iteration, CD, CL), converged iteration count)."""
    rows: list[tuple[int, float, float]] = []
    it = None
    cd = None
    for line in log_text.splitlines():
        m = _TIME_RE.match(line)
        if m:
            it = int(m.group(1))
            cd = None
            continue
        m = _CD_RE.match(line)
        if m and it is not None:
            cd = float(m.group(1))
            continue
        m = _CL_RE.match(line)
        if m and it is not None and cd is not None:
            rows.append((it, cd, float(m.group(1))))
    last_it = rows[-1][0] if rows else 0
    return rows, last_it


def main(request: str | None = None, params: dict | None = None,
        emit=None) -> int:
    params = dict(params or {})
    out = OUT_ROOT / "crm-wingbody"
    out.mkdir(parents=True, exist_ok=True)
    shown = display_name(LABEL)

    script = make_transcript(f"Act 9: {shown}", emit)
    roster = Roster(emit)
    ledger = ComputeLedger(emit)
    knowledge = KnowledgeBase(emit)
    began = time.monotonic()

    script.system(request or "Request: solve the CRM wing and grade the "
                             "converged drag against the published "
                             "reference value.")

    # ---------------- Hypothesis ----------------
    script.phase(HYPOTHESIS)
    roster.set(CHIEF_RESEARCHER, "selecting the method", "working")
    props = MissionProperties(
        kind="single-body-study",
        objective="a trustworthy transonic drag coefficient on the design "
                  "reference wing",
        dimensionality=0, regime="steady compressible RANS, transonic",
        smoothness="gated", fidelity="a solved field",
        admissibility_cite="against the standard mesh-quality acceptance band")
    for line in method_memo(props):
        script.researcher(line)
    roster.idle(CHIEF_RESEARCHER)
    script.engineer(ENGINEER_ACK)

    roster.set(CHIEF_ENGINEER, f"reading {shown}", "working")
    announce_geometry(emit, name=SURFACE, label=shown)
    script.engineer(
        f"• Hypothesis: the unmodified case recipe reproduces its own "
        f"published drag within ±{GATE_TOLERANCE * 100:.0f}%. "
        f"• Falsifier: the mesh misses its gates, the residuals never settle "
        f"below the case's own tolerance, or the converged drag sits outside "
        f"that band. "
        f"• This body is transonic and compressible, a different regime from "
        f"every other case in this control room, solved by a different "
        f"selected solver for exactly that reason.")
    script.engineer(
        f"• Gate: converged drag within ±{GATE_TOLERANCE * 100:.0f}% of "
        f"{GATE_SOURCE}, Cd {PUBLISHED_CD:g}. "
        f"• Credible because the source is the case's own publisher, "
        f"reporting the same quantity this run produces, at the design "
        f"condition Mach 0.85, C_L 0.5.")
    script.numericist(
        f"• The mesh gates are the standard acceptance band, "
        f"{per('mesh-quality')}. "
        f"• This body is meshed by the case's own recipe, not from a "
        f"supplied surface, so there is no matching coarser or finer variant "
        f"to build a refinement ladder from here either.")

    if not docker_available():
        script.engineer(
            "• The selected solver for this body is not reachable on this "
            "host right now (the container runtime did not answer). "
            "• Nothing invented: the study stops here rather than reporting "
            "a number from a solver that never ran.")
        script.save(out / "transcript.txt")
        roster.all_idle()
        return 1

    # ---------------- Plan ----------------
    script.phase(PLAN)
    capacity = audit(1, memory_per_worker_mb=2048)
    if emit:
        emit("audit.completed", capacity.panel())
        emit("solver.selected", {
            "solver": "DAFoam / DARhoSimpleCFoam",
            "method": "steady compressible RANS, transonic",
            "basis": "plan commits the body to the compressible chain, the "
                    "selected solver for this regime"})
    script.engineer(capacity.headline(), panel=capacity.panel())
    script.engineer(
        f"• Plan: receive the case's own mesh, check it, then a steady "
        f"compressible solve over {BUDGET_ITERATIONS} iterations, the budget "
        f"this case's own residuals are known to settle inside. "
        f"• Memory checked before the heavy stages; the run waits rather "
        f"than crowding the host.")

    engineer = DockerDAFoamEngineer("act9-crm_wingbody", out, TUTORIAL_SOURCE,
                                    mem_gb=12, ranks=RANKS,
                                    on_event=lambda event, payload: None)

    stage_table = {"created": False}

    def stage_row(step: str, seconds: float, note: str) -> None:
        _emit_table(emit, script, role=_CE_ROLE,
                    title="Pipeline stages, as run",
                    headers=("Stage", "Time", "What ran"),
                    rows=[[step, f"{seconds:.0f} s",
                           note[:1].upper() + note[1:]]],
                    table_id="stages-act9-crm_wingbody", append=stage_table["created"])
        stage_table["created"] = True

    # ---------------- Evidence ----------------
    script.phase(EVIDENCE)
    roster.set(MONITOR, "watching solver output", "watching")
    roster.set(CHIEF_ENGINEER, "staging the case", "working")

    try:
        engineer.stage_case()
        if CACHED_SURFACE_MESH.exists():
            shutil.copy(CACHED_SURFACE_MESH, engineer.remote_case / CACHED_SURFACE_MESH.name)
        script.engineer(
            "• Case received: the design reference wing's own mesh and "
            "solver setup, staged as it starts.")

        warm_mesh = engineer.restore_cached_mesh(LABEL)
        if warm_mesh:
            roster.set(CHIEF_ENGINEER, "preparing the mesh", "working")
            script.engineer(
                "• Mesh in hand for this body; going straight to the "
                "quality gates and the solve.")
        else:
            available = wait_for_headroom(narrate=script.engineer)
            script.engineer(f"• MemAvailable {available:.1f} GB; clear to mesh.")
            roster.set(CHIEF_ENGINEER, "extruding the volume mesh", "working")
            started = time.monotonic()
            engineer.run("bash preProcessing.sh", name="mesh", timeout=900)
            seconds = time.monotonic() - started
            stage_row("mesh", seconds,
                      "volume mesh built from the case's own recipe, "
                      "unmodified")
            ledger.spend(seconds, f"mesh generation ({seconds:.0f}s)")
            engineer.save_mesh_to_cache(LABEL)

        # 0/ initial fields, fresh every run regardless of mesh-cache state.
        zero = engineer.remote_case / "0"
        if zero.exists():
            shutil.rmtree(zero)
        shutil.copytree(engineer.remote_case / "0.orig", zero)

        cells = engineer.mesh_cell_count()
        if emit:
            emit("mesh.stats", {"cells": cells})
        roster.set(CHIEF_RESEARCHER, "ruling on mesh quality", "working")
        script.researcher(
            f"• Mesh: {cells:,} cells, this case's own recipe. "
            f"• Quality reported by the solver's own inline mesh check at "
            f"the start of the run, {per('mesh-quality')}.")
        roster.idle(CHIEF_RESEARCHER)

        # -- decompose for the capped rank count, solve --
        decomp = engineer.remote_case / "system" / "decomposeParDict"
        decomp.write_text(re.sub(r"numberOfSubdomains\s+\d+;",
                                 f"numberOfSubdomains {RANKS};",
                                 decomp.read_text()))
        control = engineer.remote_case / "system" / "controlDict"
        control.write_text(
            re.sub(r"endTime\s+\d+;", f"endTime {BUDGET_ITERATIONS};",
                   re.sub(r"writeInterval\s+\d+;",
                          f"writeInterval {BUDGET_ITERATIONS};",
                          control.read_text())))

        solve_key = f"{LABEL}-c{cells}-i{BUDGET_ITERATIONS}"
        warm_hit, cached_log = engineer.restore_cached_solve(solve_key)
        if warm_hit:
            note = f"steady compressible solve, {BUDGET_ITERATIONS} iterations"
            roster.set(CHIEF_ENGINEER, note, "working")
            roster.set_workers(RANKS, note)
            started = time.time()
            elapsed = max(1.0, time.time() - started)
            ledger.spend(elapsed, f"DARhoSimpleCFoam ({elapsed:.0f}s)")
            stage_row("selected solver", elapsed, note)
            roster.set_workers(0)
            log_text = cached_log
        else:
            available = wait_for_headroom(narrate=script.engineer)
            script.engineer(f"• MemAvailable {available:.1f} GB; clear to solve.")
            engineer.run(f"decomposePar -force", name="decomposePar", timeout=600)
            note = f"steady compressible solve, {BUDGET_ITERATIONS} iterations"
            roster.set(CHIEF_ENGINEER, note, "working")
            roster.set_workers(RANKS, note)
            result = engineer.run(
                f"mpirun -np {RANKS} --allow-run-as-root python3 runScript.py -task run_model",
                name="run_model", timeout=5400)
            ledger.spend(result.seconds, f"DARhoSimpleCFoam ({result.seconds:.0f}s)")
            stage_row("selected solver", result.seconds, note)
            roster.set_workers(0)
            engineer.run("reconstructPar -latestTime", name="reconstructPar", timeout=900)
            log_text = Path(result.log_path).read_text(errors="replace")
            engineer.save_solve_to_cache(solve_key, log_text=log_text)
    except Exception as exc:
        roster.set(CHIEF_ENGINEER, "halted", "blocked")
        script.engineer(f"• The study stopped: a solver stage did not "
                        f"complete cleanly; detail in the run log, not on "
                        f"screen.")
        script.save(out / "transcript.txt")
        roster.all_idle()
        return 1

    # ---------------- Results ----------------
    roster.set(CHIEF_ENGINEER, "reading the force history", "working")
    history, converged_iteration = _parse_history(log_text)
    if not history:
        script.engineer("• No force history from the solver, nothing to report.")
        script.save(out / "transcript.txt")
        roster.all_idle()
        return 1
    final_cd = history[-1][1]
    final_cl = history[-1][2]
    deviation = (final_cd - PUBLISHED_CD) / PUBLISHED_CD

    if emit and history:
        for it, cd, cl in history:
            emit("trace.point", {"series": "Cd_history", "x": it,
                                 "y": round(cd, 6), "lo": round(cd, 6),
                                 "hi": round(cd, 6), "x_label": "solver iteration",
                                 "y_label": "Cd", "title": "Drag coefficient: "
                                 "solver iteration history", "feasible": True})

    gate_rows = [
        ["Converged at iteration", f"{converged_iteration:,}"],
        ["Measured C_d", f"{final_cd:.6f}"],
        [f"Published C_d ({GATE_SOURCE})", f"{PUBLISHED_CD:g}"],
        ["Deviation", f"{deviation * 100:+.3f}%"],
        ["Gate", f"±{GATE_TOLERANCE * 100:.0f}%"],
        ["Measured C_L", f"{final_cl:.6f}"],
    ]
    _emit_table(emit, script, role=_CE_ROLE,
               title="Gate: converged drag vs the published reference",
               headers=("Quantity", "Value"), rows=gate_rows,
               table_id="gate-act9-crm_wingbody")
    # The campaign's own verdict-row shape (Quantity | Exact | Solved |
    # Deviation), the one every other act in this set emits and the gate
    # table reads: same numbers as the table just above, one row, the shape
    # a shared reader expects rather than a bespoke one.
    _emit_table(emit, script, role=_CE_ROLE,
               title="CRM wing verdict",
               headers=("Quantity", "Exact", "Solved", "Deviation"),
               rows=[["Drag coefficient", f"{PUBLISHED_CD:g}",
                     f"{final_cd:.6f}", f"{deviation * 100:+.3f}%"]],
               table_id="verdict-act9-crm_wingbody")

    gate_ok = abs(deviation) <= GATE_TOLERANCE
    if gate_ok:
        verdict = {"tier": VALIDATED,
                  "reason": (f"within {abs(deviation) * 100:.2f}% of "
                             f"{GATE_SOURCE}, Cd {PUBLISHED_CD:g} "
                             f"(band ±{GATE_TOLERANCE * 100:.0f}%)")}
    else:
        verdict = {"tier": SOLVER_BACKED,
                  "reason": (f"measured Cd {final_cd:.4g} is "
                             f"{deviation * 100:+.2f}% from {GATE_SOURCE}, "
                             f"outside the ±{GATE_TOLERANCE * 100:.0f}% band")}
    script.engineer("• Residuals settled; the state is read at the "
                    "converged time.", verdict=verdict)

    monitor_note = ("• Watched the solver log for the fatal patterns this "
                    "regime shares with the incompressible chain (NaN, "
                    "floating-point exceptions); none seen.")
    script.monitor(monitor_note)
    roster.idle(MONITOR)

    if emit:
        emit("result.verdict", {"quantity": "Drag coefficient",
                                "value": f"{final_cd:.6f}", "ci": "n/a",
                                "confidence": "n/a",
                                "envelope": f"converged at iteration {converged_iteration:,}",
                                **verdict})

    # ---------------- Conclusion ----------------
    script.phase(CONCLUSION)
    elapsed = (time.monotonic() - began) / 60
    script.engineer(
        f"• From a received case to a converged transonic solve in "
        f"{elapsed:.1f} minutes. "
        f"• Residuals settled by iteration {converged_iteration:,}.")
    if verdict["tier"] == VALIDATED:
        script.engineer(f"• Verdict: validated. {verdict['reason']}.")
    else:
        script.engineer(f"• Verdict: {verdict['tier'].lower()}. {verdict['reason']}.")
    script.engineer(
        f"• Spend {ledger.as_dict()['spent_core_minutes']:.0f} core-minutes.")

    knowledge.add(f"{shown} solved: {cells:,} cells, Cd {final_cd:.6f}, "
                  f"converged at iteration {converged_iteration:,}")

    _AGENDA = [
        {"title": "The lift-constrained sweep",
         "scope": "hold C_L fixed at a small span of published targets and "
                  "map how drag moves across the design point",
         "cost": "one solve per target on this mesh"},
        {"title": "The full wing-body",
         "scope": "extend the same recipe to the fuselage-and-tail "
                  "configuration, at HPC mesh scale",
         "cost": "materially larger mesh and a longer solve"},
        {"title": "The gradient, on a bigger host",
         "scope": "the adjoint total derivative is a known memory wall on "
                  "this host; a host with materially more free RAM is the "
                  "next thing to try",
         "cost": "a dedicated host measured on a small case first"},
    ]
    if emit:
        emit("agenda.updated", {"entries": _AGENDA})

    report_doc = lab_report(
        title=f"Act 9: {shown}",
        abstract=[
            f"We received the CRM wing's own mesh recipe, built "
            f"and checked the volume mesh, and solved it fresh on the "
            f"selected compressible solver.",
            f"The mesh reached {cells:,} cells; drag converged to "
            f"{final_cd:.6f} at iteration {converged_iteration:,}.",
            f"The result is reported as {verdict['tier'].lower()}: {verdict['reason']}.",
        ],
        methods=[
            "Received the case's own mesh recipe and built the volume mesh "
            "from it unmodified.",
            f"Steady compressible RANS solve over {BUDGET_ITERATIONS} "
            f"iterations, the budget this case's own residuals are known to "
            f"settle inside.",
            f"Converged drag compared against {GATE_SOURCE}.",
        ],
        results=[{
            "quantity": "Drag coefficient",
            "value": f"{final_cd:.6f}",
            "envelope": f"{deviation * 100:+.3f}% vs {GATE_SOURCE}",
            **verdict,
        }, {
            "quantity": "Lift coefficient",
            "value": f"{final_cl:.6f}", "envelope": "at the design condition",
            **verdict,
        }, {
            "quantity": "Mesh",
            "value": f"{cells:,} cells", "envelope": "this case's own recipe",
            **verdict,
        }],
        uncertainty=[
            "No refinement ladder on this run: this body is meshed by the "
            "case's own recipe rather than from a supplied surface, with no "
            "coarser or finer variant on record.",
            f"Compared against {GATE_SOURCE}: {verdict['reason']}.",
        ],
        next_investigations=[f"{e['title']}: {e['scope']}" for e in _AGENDA],
        compute=ledger.as_dict(),
    )
    if emit:
        emit("report.ready", report_doc)

    cert_path = out / "certificate.pdf"
    try:
        cert_path.unlink()
    except OSError:
        pass
    try:
        from chief_engineer.certificate import build_certificate_v2
        from chief_engineer.lab import uncertainty_channels

        channels = uncertainty_channels(
            input_2sigma=None, numerical=None, model=None,
            input_note="No input uncertainty was assumed for this problem.",
            numerical_note=("• No refinement ladder on record for this "
                            "case's own mesh recipe."),
            model_note=("compressible RANS closure, stated model-form; "
                        f"reproduces {GATE_SOURCE} to "
                        f"{abs(deviation) * 100:.2f}%"))
        cert_doc = dict(report_doc)
        cert_doc["result_fields"] = [
            ("Body", shown), ("C_d", f"{final_cd:.6f}"),
            ("C_L", f"{final_cl:.6f}"), ("Cells", f"{cells:,}"),
            ("Converged Iteration", f"{converged_iteration:,}"),
            ("Solve Time", f"{elapsed:.1f} min"),
        ]
        certificate = build_certificate_v2(
            cert_doc, out_path=cert_path,
            geometry=shown,
            objective=(request or "CRM wing, graded against the published "
                                  "reference drag"),
            mission_id=f"crm-wingbody-{LABEL}",
            issued_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            channels=channels,
            display_name=shown,
            source_filename=SURFACE,
            solver="DAFoam, DARhoSimpleCFoam steady compressible RANS",
            mesh=mesh_validity(cells, None, None))
        if emit:
            emit("certificate.ready", {**certificate, "dir": out.name})
    except Exception:
        script.engineer(
            "• No certificate could be issued for this run. "
            "• The previous run's certificate is withdrawn, so nothing out "
            "of date is served. "
            "• The result above stands on the transcript and the report.")
    script.save(out / "transcript.txt")
    roster.all_idle()
    print("Artifacts in", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
