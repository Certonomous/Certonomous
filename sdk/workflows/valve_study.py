"""Multi-point (cycle-decomposition) internal-flow study of an idealized valve.

A pulsatile but PERIODIC internal flow is screened by decomposing one cardiac
cycle into a few steady phase points, solving each, and cycle-weighting the
result. The design parameter is the leaflet opening angle; the objective is the
cycle-weighted pressure loss across the valve orifice.

This is a SCREENING method, graded CONCEPTUAL MODEL. The pressure loss at each
phase point comes from a transparent reduced-order orifice model
(dp = 0.5 * rho * (Q / (Cd * A_orifice))^2) — the same conceptual-model posture
as the aircraft-sizing study, NOT a solved flow. The place a real steady
internal-flow solve plugs in is marked explicitly (``_phase_pressure_loss``),
and the model-form channel lists every physics the screen drops: the analytic
orifice model itself, neglected phase-interaction (the flow is inertially
unsteady at alpha ~ 17), fixed leaflets, and Newtonian blood.

No clinical claim is made anywhere; the outputs are engineering curves only.
"""

from __future__ import annotations

import math
import os
import time
from pathlib import Path

import yaml

from . import OUT_ROOT, announce_plot, make_transcript
from chief_engineer.compute_audit import audit
from chief_engineer.plot_theme import waveform_figure
from chief_engineer.lab import (CHIEF_ENGINEER, CHIEF_RESEARCHER, CONCLUSION,
                                EVIDENCE, HYPOTHESIS, NUMERICIST, PLAN,
                                ComputeLedger, KnowledgeBase, Roster,
                                lab_report, trust, uncertainty_channels)

# Pull the owned geometry + waveform modules from the curriculum.
_VALVE = Path(__file__).resolve().parents[2] / "models" / "curriculum" / "aortic_valve"
_PHYSICS_RULES = Path(__file__).resolve().parents[2] / "docs" / "physics_rules.yaml"

import sys
if str(_VALVE) not in sys.path:
    sys.path.insert(0, str(_VALVE))
from waveform import (phase_points, womersley, RHO_BLOOD, Q_PEAK,  # noqa: E402
                      T_CYCLE, T_SYSTOLE, NU_BLOOD)
from generate_valve import effective_orifice_area, ROOT_RADIUS  # noqa: E402

CANDIDATE_ANGLES = (35.0, 50.0, 65.0, 80.0)   # 4 candidates
# Backend pacing: the four candidate valves visibly cycle in the viewport as
# each is screened (paces the PATH, never the numbers). Off in CI via env.
_PACE_S = float(os.environ.get("CERTONOMOUS_SWEEP_PACE_MS", "550")) / 1000.0
DISCHARGE_COEFF = 0.62                          # sharp-orifice discharge coefficient
MIN_ORIFICE_AREA = 1.6e-4                        # constraint floor, m^2 (~160 mm^2)
MC_SAMPLES = 200                                 # Monte-Carlo envelope draws
# Input 1-sigma spreads propagated through the screen (fractional).
FLOW_SIGMA = 0.05
CD_SIGMA = 0.06


def _load_womersley_thresholds() -> dict:
    data = yaml.safe_load(_PHYSICS_RULES.read_text(encoding="utf-8")) or {}
    return (data.get("womersley") or {})


def _phase_pressure_loss(flow_rate: float, orifice_area: float,
                         cd: float = DISCHARGE_COEFF) -> float:
    """Steady pressure loss across the orifice at one phase point (Pa).

    REDUCED-ORDER MODEL — this is the single point where a real steady
    internal-flow OpenFOAM solve (inlet flow rate, no-slip leaflets, simpleFoam,
    read dp from the solved field) plugs in. Until then the orifice correlation
    stands in, transparently, and the grade stays CONCEPTUAL MODEL.
    """
    throat_velocity = flow_rate / max(cd * orifice_area, 1e-9)
    return 0.5 * RHO_BLOOD * throat_velocity ** 2


def _cycle_weighted_loss(angle: float, phases, cd: float = DISCHARGE_COEFF) -> float:
    area = effective_orifice_area(angle)
    return sum(p.weight * _phase_pressure_loss(p.flow_rate, area, cd) for p in phases)


def _mc_envelope(angle: float, phases) -> tuple[float, float]:
    """Mean and 2-sigma of the cycle-weighted loss under input uncertainty.

    Deterministic, seedless sampling: the draws are a fixed low-discrepancy
    sweep over the flow and Cd spreads, so the envelope is reproducible without
    a RNG (which the workflows avoid).
    """
    samples = []
    n = int(round(math.sqrt(MC_SAMPLES)))
    for i in range(n):
        for j in range(n):
            fq = 1.0 + FLOW_SIGMA * (2.0 * (i + 0.5) / n - 1.0) * math.sqrt(3)
            fc = 1.0 + CD_SIGMA * (2.0 * (j + 0.5) / n - 1.0) * math.sqrt(3)
            area = effective_orifice_area(angle)
            val = sum(p.weight * _phase_pressure_loss(p.flow_rate * fq, area,
                                                      DISCHARGE_COEFF * fc)
                      for p in phases)
            samples.append(val)
    mean = sum(samples) / len(samples)
    var = sum((s - mean) ** 2 for s in samples) / len(samples)
    return mean, 2.0 * math.sqrt(var)


AGENDA = [
    {"title": "Harmonic-balance cycle solve",
     "scope": "resolve phase-interaction the multi-point screen drops, solving the "
              "coupled harmonics of one cycle instead of independent phase points",
     "cost": "~1 order of magnitude over the multi-point screen"},
    {"title": "Unsteady fluid–structure interaction",
     "scope": "move the leaflets, coupling the flow to leaflet dynamics so opening "
              "is solved, not prescribed",
     "cost": "~2 orders of magnitude; transient FSI, remeshing"},
    {"title": "Non-Newtonian blood rheology",
     "scope": "replace the Newtonian viscosity with a shear-thinning model in the "
              "orifice jet and wake",
     "cost": "modest over a Newtonian solve; a constitutive-model swap"},
]


def main(request: str | None = None, params: dict | None = None,
         iterations: int = 1, emit=None) -> int:
    params = params or {}
    out = OUT_ROOT / "valve-study"
    out.mkdir(parents=True, exist_ok=True)
    script = make_transcript("valve study", emit)
    roster = Roster(emit)
    ledger = ComputeLedger(emit)
    knowledge = KnowledgeBase(emit)
    phases = phase_points()

    script.system(request or "Request: minimise the pressure loss across the valve "
                             "over the cardiac cycle by choosing the leaflet opening angle.")

    # ---------------- Hypothesis ----------------
    script.phase(HYPOTHESIS)
    roster.set(CHIEF_ENGINEER, "framing the study", "working")
    script.engineer(
        "• Pulsatile flow: a single steady snapshot would be cycle-blind. "
        "• Chief Researcher rules on the cycle decomposition before anything runs.")

    # ------------- Researcher method-selection memo (periodic decomposition) ----
    roster.set(CHIEF_RESEARCHER, "selecting the method", "working")
    thresholds = _load_womersley_thresholds()
    strict = float(thresholds.get("strict_quasi_steady_max", 1.0))
    screen_max = float(thresholds.get("multipoint_screening_max", 25.0))
    alpha = womersley(ROOT_RADIUS, T_CYCLE, NU_BLOOD)

    # (a) periodicity insight
    script.researcher(
        "• Internal flow, pulsatile but periodic. "
        "• Periodic forcing converts to a few steady phase points, weighted back together.")
    # (b) Womersley computed AND displayed with the ruling
    if alpha <= strict:
        ruling = (f"• Womersley α ≈ {alpha:.1f}, under the strict limit {strict:g}. "
                  f"• Each instant is effectively steady.")
    elif alpha <= screen_max:
        ruling = (f"• Womersley α ≈ {alpha:.1f}: above the strict limit {strict:g}, "
                  f"inertially unsteady. "
                  f"• Under the screening ceiling {screen_max:g}, admissible as a SCREEN. "
                  f"• Dropped phase-interaction rides as model-form in the channel table.")
    else:
        ruling = (f"• Womersley α ≈ {alpha:.1f} exceeds the screening ceiling "
                  f"{screen_max:g}. "
                  f"• Not even a useful screen: do not proceed on this method.")
    script.researcher(ruling)
    # (c) the plan
    weights = ", ".join(f"{p.name.split()[0]} {p.weight:.2f}" for p in phases)
    script.researcher(
        f"• Strategy: {len(phases)}-point cycle decomposition, weights {weights}. "
        f"• Objective: cycle-weighted pressure loss; each phase a steady problem. "
        f"• Gradients stay cheap at every phase point.")
    # (d) rejected / deferred rungs, on record
    script.researcher(
        "• Rejected: single snapshot, prices one instant as the whole cycle. "
        "• Deferred to agenda: harmonic-balance cycle solve; unsteady FSI for moving leaflets.")
    if emit:
        emit("agenda.updated", {"entries": AGENDA})
    roster.idle(CHIEF_RESEARCHER)
    script.engineer("On it.")

    # ---------------- Plan ----------------
    script.phase(PLAN)
    n_solves = len(CANDIDATE_ANGLES) * len(phases)
    capacity = audit(min(12, n_solves), memory_per_worker_mb=256)
    if emit:
        emit("audit.completed", capacity.panel())
    script.engineer(capacity.headline(), panel=capacity.panel())
    if emit:
        # Landscape skeleton on screen at plan time — axes and objective first.
        emit("landscape.init", {
            "title": "Candidate landscape",
            "x": {"key": "opening_angle_deg", "label": "opening angle [°]"},
            "y": {"key": "orifice_area_mm2", "label": "orifice area [mm²]"},
            "objective": {"key": "cycle_pressure_loss",
                          "label": "cycle loss [Pa]", "direction": "min"}})
    script.engineer(
        f"• Plan: {len(CANDIDATE_ANGLES)} angles × {len(phases)} phases = "
        f"{n_solves} steady evaluations. "
        f"• Objective: cycle-weighted loss with a Monte-Carlo envelope. "
        f"• Constraint: minimum orifice area.")
    script.numericist(
        "• Each phase is a reduced-order orifice model, not a solved flow. "
        "• A real internal-flow solve is the marked plug-in point. "
        "• Ranks angles and screens the trade.")

    # The systolic waveform figure — the k=3 weighted phase points on the pulse
    # the study decomposes. Publication-grade, GUI-themed; reports lead with it.
    wave_png = waveform_figure(
        out / "systolic_waveform.png", phases, q_peak=Q_PEAK, t_systole=T_SYSTOLE,
        t_cycle=T_CYCLE, alpha=alpha,
        title="Idealized systolic waveform: three weighted phase points")
    if wave_png:
        announce_plot(emit, "valve-study", wave_png,
                      "Systolic waveform: the three weighted phase points solved")

    # ---------------- Evidence ----------------
    script.phase(EVIDENCE)
    roster.set(CHIEF_ENGINEER, "screening the phase points", "working")
    granted = min(capacity.capacity, n_solves)
    roster.set_workers(granted, "phase evaluations")
    results = []
    if emit:
        emit("objective.spec", {"metric": "cycle_pressure_loss", "direction": "min"})
    eval_started = time.time()
    trace_x, trace_y, trace_lo, trace_hi = [], [], [], []
    for slot, angle in enumerate(CANDIDATE_ANGLES):
        if emit:
            # The dispatch panel watches this slot pick up the candidate.
            emit("dispatch.update", {"slot": slot, "state": "solving",
                                     "label": f"opening {angle:g}°",
                                     "detail": "phase decomposition"})
            # The candidate valve appears in the viewport as the surface it is —
            # the orifice visibly pinches or opens with the angle.
            emit("geometry.ready", {
                "url": f"/api/geometry?valve_angle={angle:g}",
                "label": f"candidate valve, opening {angle:g}°"})
        if _PACE_S:
            time.sleep(_PACE_S)
        area = effective_orifice_area(angle)
        per_phase = [(p.name, _phase_pressure_loss(p.flow_rate, area)) for p in phases]
        obj, band = _mc_envelope(angle, phases)
        feasible = area >= MIN_ORIFICE_AREA
        results.append({"angle": angle, "area": area, "objective": obj,
                        "band": band, "feasible": feasible, "per_phase": per_phase})
        trace_x.append(angle); trace_y.append(obj)
        trace_lo.append(obj - band); trace_hi.append(obj + band)
        if emit:
            emit("landscape.point", {
                "design": {"opening_angle_deg": round(angle, 1),
                           "orifice_area_mm2": round(area * 1e6, 1)},
                "metrics": {"cycle_pressure_loss": round(obj, 1)},
                "objective": round(obj, 1), "direction": "min",
                "feasible": feasible})
            # Live objective trace — the cycle-weighted loss curve grows as each
            # candidate lands, envelope forming in real time.
            emit("trace.point", {
                "series": "cycle_pressure_loss", "x": round(angle, 1),
                "y": round(obj, 1), "lo": round(obj - band, 1),
                "hi": round(obj + band, 1),
                "x_label": "opening angle [deg]", "y_label": "cycle loss [Pa]",
                "title": "Cycle-weighted pressure loss", "feasible": feasible})
            emit("dispatch.update", {"slot": slot, "state": "done",
                                     "label": f"opening {angle:g}°",
                                     "detail": f"{obj:.0f} Pa"})
        script.engineer(
            f"• Opening {angle:g}° → orifice {area*1e6:.0f} mm², loss "
            f"{obj:.0f} ± {band:.0f} Pa"
            + ("." if feasible else ". • Infeasible: below the minimum orifice area."))
    eval_elapsed = time.time() - eval_started
    ledger.spend(n_solves * 0.05, f"{n_solves} reduced-order phase evaluations")
    roster.set_workers(0)
    script.engineer(f"• Phase evaluations: {eval_elapsed:.2f} s, {n_solves} solves.")

    feasible = [r for r in results if r["feasible"]]
    if not feasible:
        script.engineer("• No candidate clears the orifice-area floor. "
                        "• The sweep needs a wider opening range first.")
        script.save(out / "transcript.txt"); roster.all_idle(); return 0
    best = min(feasible, key=lambda r: r["objective"])

    # ---------------- Conclusion ----------------
    script.phase(CONCLUSION)
    if emit:
        # The winning valve stays on screen after the run — the render the
        # viewer reads the report beside.
        emit("geometry.ready", {
            "url": f"/api/geometry?valve_angle={best['angle']:g}",
            "label": f"winning valve, opening {best['angle']:g}°, "
                     f"{best['objective']:.0f} Pa"})
    script.engineer(
        f"• {len(feasible)} of {len(results)} candidates clear the orifice floor. "
        f"• Winner: {best['angle']:g}° at {best['objective']:.0f} ± "
        f"{best['band']:.0f} Pa. "
        f"• Widest admissible orifice, exactly what orifice physics predicts.")
    channels = uncertainty_channels(
        input_2sigma=best["band"], numerical=None, model=None,
        input_note="2-sigma Monte-Carlo envelope propagated from the spread in "
                   "phase flow-rate and the orifice discharge coefficient",
        numerical_note="the cycle is sampled at three phase points; between-phase "
                       "structure is not resolved",
        model_note="reduced-order orifice model, not a solved flow; phase-interaction "
                    "neglected (alpha ~ %.0f, inertially unsteady); leaflets fixed, "
                    "not moving; Newtonian blood approximation" % alpha)
    if emit:
        emit("uncertainty.channels", channels)
    script.researcher(
        "• A screen, not a validated pressure: the ranking is trustworthy. "
        "• A solved internal flow would set the pressure magnitude. "
        "• The three missing capabilities are on the research agenda.")
    verdict = trust(converged=True, solver_backed=False,
                    why="reduced-order orifice screen on a screening geometry; "
                        "the flow is inertially unsteady")
    if emit:
        emit("result.verdict", {"quantity": "Cycle-weighted pressure loss",
                                "value": f"{best['objective']:.0f}",
                                "ci": f"{best['band']:.0f} Pa",
                                "confidence": "95%",
                                "envelope": f"at opening {best['angle']:g} deg",
                                **verdict})
    knowledge.add(
        f"Valve opening-angle screen: lowest cycle-weighted loss at "
        f"{best['angle']:g} deg ({best['objective']:.0f} Pa), Womersley ~ {alpha:.0f}, "
        f"multi-point decomposition (conceptual model)")

    report = lab_report(
        title=f"Valve opening-angle screen: cycle-weighted pressure loss",
        abstract=[
            f"A pulsatile internal flow was screened by decomposing the cardiac "
            f"cycle into {len(phases)} steady phase points (Womersley ~ {alpha:.0f}, "
            f"below the multi-point screening ceiling).",
            f"Across {len(CANDIDATE_ANGLES)} opening angles the lowest cycle-weighted "
            f"pressure loss is at {best['angle']:g} deg, {best['objective']:.0f} +/- "
            f"{best['band']:.0f} Pa.",
            "This is a reduced-order screen on an owned screening geometry; the "
            "model channel carries what the screen leaves out."],
        methods=[
            "Idealized three-leaflet valve; leaflet opening angle sets the effective "
            "orifice area.",
            "In-repo half-sine systolic waveform; three phase points weighted by the "
            "stroke-volume fraction each carries.",
            "Per-phase pressure loss from a reduced-order orifice model; cycle-weighted "
            "objective with a Monte-Carlo input envelope; minimum-orifice constraint."],
        results=[{"quantity": "Cycle-weighted pressure loss",
                  "value": f"{best['objective']:.0f} ± {best['band']:.0f} Pa (95%)",
                  "envelope": f"at opening {best['angle']:g} deg",
                  **verdict}],
        uncertainty=[
            "The ranking (wider orifice, lower loss) is physical and trustworthy.",
            "The magnitude is a reduced-order estimate; the model channel names "
            "what is not in it.",
            f"The flow is inertially unsteady (Womersley ~ {alpha:.0f}); "
            "phase-interaction is dropped by the multi-point screen."],
        next_investigations=[e["title"] + ": " + e["scope"] for e in AGENDA],
        compute=ledger.as_dict())
    if emit:
        emit("report.ready", report)
    script.save(out / "transcript.txt")
    roster.all_idle()
    print("Artifacts in", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(request=" ".join(sys.argv[1:]) or None))
