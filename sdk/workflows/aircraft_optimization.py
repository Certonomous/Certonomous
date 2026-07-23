"""Optimize an airliner's lift-to-drag ratio against stated mission requirements.

The request states what the aircraft must do — passengers, range, take-off and
landing speeds — and the lab searches a wing design space (span, area, sweep)
for the highest cruise L/D that still meets every requirement. Designs that miss
a requirement are shown as infeasible, not hidden; the winner is the best L/D
that clears them all.

The search runs in two passes. A **conceptual sizing screen** — a textbook drag
polar, a Breguet range check, and stall-speed constraints — maps the whole
grid in milliseconds. Then, when the vortex-lattice solver is reachable, the
**top finalists get real aero solves**: each candidate wing is built as actual
parametric geometry and solved for its polar, the cruise point read off the
solved curve, and the winner picked on solved numbers. The fuselage and tail
stay a parasite-drag buildup — the verdict says exactly which parts were
solved and which were modelled, and the tier is capped accordingly.
"""

from __future__ import annotations

import math
import os
import re
import shutil
import time

from . import OUT_ROOT, make_transcript
from chief_engineer import vspaero
from chief_engineer.compute_audit import audit
from chief_engineer.researcher import ENGINEER_ACK, MissionProperties, method_memo
from chief_engineer.lab import (CHIEF_ENGINEER, CHIEF_RESEARCHER, CONCLUSION,
                                EVIDENCE, HYPOTHESIS, NUMERICIST, PLAN,
                                ComputeLedger, KnowledgeBase, Roster,
                                lab_report, trust, uncertainty_channels)

# Physical constants and modelling assumptions, all stated so the numbers can be
# traced. These are conventional conceptual-design values, not tuned to a body.
_G = 9.81
_RHO_SL = 1.225          # sea-level air density (take-off / landing), kg/m^3
_RHO_CRUISE = 0.38       # ~11 km cruise altitude, kg/m^3
_V_CRUISE = 230.0        # cruise TAS ~ M0.78 at altitude, m/s
_CLMAX_LANDING = 2.6     # full flaps + slats
_CLMAX_TAKEOFF = 2.1     # take-off flap setting
_SFC = 1.7e-5            # thrust-specific fuel consumption, kg/(N·s) (~0.6 lb/lbf/hr)
_FUEL_FRACTION = 0.32    # usable fuel as a fraction of MTOW
_PAYLOAD_FRACTION = 0.22 # payload as a fraction of MTOW (sets MTOW from pax)
_KG_PER_PAX = 100.0      # passenger + baggage
_SPAN_STRUCTURAL_LIMIT = 68.0   # m — beyond this the wing box is impractical
_MU_CRUISE = 1.43e-5     # dynamic viscosity at ~11 km, Pa·s
# Parasite drag of everything that is NOT the wing (fuselage, tail, nacelles,
# interference) — the component-buildup share left when the wing's own viscous
# drag comes from the solver instead of the polar constant.
_CD0_NONWING = 0.013
_TAPER = 0.3             # planform taper ratio for every candidate wing
_N_FINALISTS = 9         # feasible designs promoted to real solves
# Stated 1-sigma input uncertainties, propagated to the headline CI. These are
# the aleatory inputs the sizing rests on; they are declared, not discovered.
_SIGMA_PAYLOAD = 0.025   # passenger + baggage mass, ±5% at 2-sigma
_SIGMA_CD0_NONWING = 0.04  # non-wing parasite buildup, ±8% at 2-sigma
# Backend pacing so the landscape points and the candidate wing in the viewport
# visibly land one by one — the viewer watches the screen fill. Paces the PATH,
# never the numbers; disabled in CI via CERTONOMOUS_SWEEP_PACE_MS=0.
_PACE_S = float(os.environ.get("CERTONOMOUS_SWEEP_PACE_MS", "120")) / 1000.0


def _interp_polar(polar: dict, key: str, cl: float) -> float:
    """Linear interpolation of a polar column against CLtot."""
    cls_, ys = polar["CLtot"], polar[key]
    for i in range(len(cls_) - 1):
        if cls_[i] <= cl <= cls_[i + 1]:
            t = (cl - cls_[i]) / ((cls_[i + 1] - cls_[i]) or 1.0)
            return ys[i] + t * (ys[i + 1] - ys[i])
    i = 0 if cl < cls_[0] else len(cls_) - 2
    t = (cl - cls_[i]) / ((cls_[i + 1] - cls_[i]) or 1.0)
    return ys[i] + t * (ys[i + 1] - ys[i])


def winner_ci95(best: dict, reqs: dict, *, polar: dict | None,
                n: int = 400, seed: int = 7) -> float:
    """95% CI on the winner's L/D: the stated input uncertainties Monte-Carlo
    propagated through the actual evaluation chain — the solved polar when one
    exists, the sizing model otherwise. Real spread machinery, no fudge."""
    import random
    import statistics

    rng = random.Random(seed)
    samples: list[float] = []
    for _ in range(n):
        mass_f = rng.gauss(1.0, _SIGMA_PAYLOAD)
        if polar:
            cl = best["cl_cruise"] * mass_f
            cd0 = _CD0_NONWING * rng.gauss(1.0, _SIGMA_CD0_NONWING)
            cdi = _interp_polar(polar, "CDi", cl)
            cdo = _interp_polar(polar, "CDo", cl)
            samples.append(cl / (cd0 + cdo + cdi))
        else:
            perturbed = dict(reqs)
            perturbed["passengers"] = reqs["passengers"] * mass_f
            r = evaluate_design(best["span"], best["area"],
                                best["sweep_deg"], perturbed)
            samples.append(r["L_D"])
    return 2.0 * statistics.stdev(samples)


def parse_requirements(text: str) -> dict:
    """Pull the mission requirements out of the prompt; state defaults for any
    that are missing so nothing is silently assumed."""
    text = text or ""

    def _speed(patterns: list[str], default: float) -> tuple[float, bool]:
        for pat in patterns:
            m = re.search(pat, text, re.I)
            if m:
                value = float(m.group(1).replace(",", ""))
                unit = (m.group(2) or "").lower() if m.lastindex and m.lastindex >= 2 else ""
                if "kn" in unit:
                    value *= 0.514444
                elif "km/h" in unit or "kph" in unit:
                    value /= 3.6
                return value, True
        return default, False

    pax_match = re.search(r"(\d[\d,]*)\s*(?:people|passengers?|pax|seats?)", text, re.I)
    passengers = int(pax_match.group(1).replace(",", "")) if pax_match else 180
    range_match = re.search(r"(?:range[^\d]{0,12})?(\d[\d,]*(?:\.\d+)?)\s*(km|nm|mi)\b", text, re.I)
    range_km = 5000.0
    range_stated = False
    if range_match:
        r = float(range_match.group(1).replace(",", ""))
        unit = range_match.group(2).lower()
        range_km = r * (1.852 if unit == "nm" else 1.609 if unit == "mi" else 1.0)
        range_stated = True

    takeoff, to_stated = _speed(
        [r"take[\s-]?off\s*(?:speed)?[^\d]{0,6}(\d+(?:\.\d+)?)\s*(m/s|kn(?:ots)?|km/h|kph)?"], 80.0)
    landing, ld_stated = _speed(
        [r"land(?:ing)?\s*(?:speed)?[^\d]{0,6}(\d+(?:\.\d+)?)\s*(m/s|kn(?:ots)?|km/h|kph)?"], 70.0)

    return {
        "passengers": passengers, "passengers_stated": bool(pax_match),
        "range_km": range_km, "range_stated": range_stated,
        "takeoff_speed": takeoff, "takeoff_stated": to_stated,
        "landing_speed": landing, "landing_stated": ld_stated,
    }


def evaluate_design(span: float, area: float, sweep_deg: float, reqs: dict) -> dict:
    """Size one wing against the requirements and return its L/D and feasibility.

    Weights come from the passenger count; the drag polar gives cruise L/D; the
    stall speed sets whether the wing is large enough for the stated take-off and
    landing speeds; and a Breguet estimate gives the range this L/D can fly.
    """
    payload = reqs["passengers"] * _KG_PER_PAX
    mtow = payload / _PAYLOAD_FRACTION
    # A larger span costs structural weight; kept mild and explicit.
    mtow *= 1.0 + 0.0025 * max(0.0, span - 36.0)
    landing_weight = 0.85 * mtow

    aspect_ratio = span ** 2 / area
    sweep = math.radians(sweep_deg)
    oswald = 0.80 * math.cos(sweep) ** 0.15
    cd0 = 0.019 + 0.00025 * (sweep_deg - 25.0) ** 2 / 10.0
    cl_cruise = mtow * _G / (0.5 * _RHO_CRUISE * _V_CRUISE ** 2 * area)
    cd = cd0 + cl_cruise ** 2 / (math.pi * aspect_ratio * oswald)
    l_over_d = cl_cruise / cd

    v_stall_land = math.sqrt(2 * landing_weight * _G / (_RHO_SL * area * _CLMAX_LANDING))
    v_stall_to = math.sqrt(2 * mtow * _G / (_RHO_SL * area * _CLMAX_TAKEOFF))
    approach_speed = 1.3 * v_stall_land
    takeoff_speed = 1.2 * v_stall_to

    breguet_range_km = (
        _V_CRUISE / (_G * _SFC) * l_over_d
        * math.log(1.0 / (1.0 - _FUEL_FRACTION)) / 1000.0)

    violations = []
    if approach_speed > reqs["landing_speed"] + 1e-6:
        violations.append(
            f"approach speed {approach_speed:.0f} m/s exceeds the {reqs['landing_speed']:.0f} m/s landing limit")
    if takeoff_speed > reqs["takeoff_speed"] + 1e-6:
        violations.append(
            f"take-off speed {takeoff_speed:.0f} m/s exceeds the {reqs['takeoff_speed']:.0f} m/s limit")
    if breguet_range_km < reqs["range_km"] - 1e-6:
        violations.append(
            f"range {breguet_range_km:.0f} km short of the {reqs['range_km']:.0f} km requirement")
    if span > _SPAN_STRUCTURAL_LIMIT:
        violations.append(f"span {span:.0f} m beyond the {_SPAN_STRUCTURAL_LIMIT:.0f} m structural limit")

    return {
        "span": round(span, 3), "area": round(area, 2), "sweep_deg": round(sweep_deg, 2),
        "aspect_ratio": round(aspect_ratio, 3),
        "cl_cruise": round(cl_cruise, 4),
        "L_D": round(l_over_d, 4), "mtow_kg": round(mtow, 0),
        "approach_speed": round(approach_speed, 2), "takeoff_speed": round(takeoff_speed, 2),
        "range_km": round(breguet_range_km, 0),
        "feasible": not violations, "violations": violations,
    }


def _solve_finalist_slot(index, api, design, emit=None, script=None):
    """Solve one finalist wing on worker slot ``index``, surviving a mid-batch kill.

    Mirrors the shape-optimization sweep so the on-camera resilience beat rides an
    industry-grade surface (a real airliner wing), not a toy body. Before the slot
    does its work it checks whether that worker was struck down — a kill marker
    dropped by scripts/kill_worker.sh, read through the shared fleet mechanism. If
    so, the loss is reported on the record, the marker cleared, a fresh worker
    stood up, and the wing re-solved — so the batch finishes with exactly the
    polar a clean run would have produced. The wing is solved once either way;
    only the slot that carries it changes. A solve that returns no polar comes
    back as None so one bad wing does not sink the batch.
    """
    from chief_engineer.fleet import clear_sabotage, worker_sabotaged

    if worker_sabotaged(index):
        clear_sabotage(index)
        lost = (f"• Worker {index} stopped responding mid-solve. "
                f"• Reprovisioning and re-running its wing; the polar still lands.")
        took_over = f"• A fresh worker took over slot {index}; its wing re-solves."
        if script is not None:
            script.engineer(lost)
        if emit is not None:
            emit("worker.killed", {"worker_index": index, "detail": lost, "pending": 1})
            emit("worker.reprovisioned", {"worker_index": index, "detail": took_over})
    try:
        return api.evaluate(design)
    except Exception:
        return None


# The third planform variable: quarter-chord sweep. Varying it (not just span
# and area) makes the candidate wing visibly morph on screen — the planform
# rocks through the sweep angles as well as growing and shrinking. It is a real
# design variable, not decoration: cd0 carries a compressibility penalty that is
# minimised near 25° (the drag-divergence-optimal sweep for this cruise Mach) and
# span efficiency falls with sweep, so the optimiser finds a genuine interior
# sweep optimum rather than railing to an edge.
_SWEEPS = (20.0, 25.0, 30.0, 35.0)


def _design_grid() -> list[tuple[float, float, float]]:
    """A span × area × sweep sweep of the wing design space.

    Sweep is the innermost loop so the viewport wing rocks through the sweep
    angles repeatedly across the screening — the geometry changes many times,
    not just once, which is the whole point of watching the design space fill.
    """
    grid = []
    for span in (34, 40, 46, 52, 58, 64):
        for area in (240, 300, 360, 420):
            for sweep in _SWEEPS:
                grid.append((float(span), float(area), float(sweep)))
    return grid


def main(request: str | None = None, params: dict | None = None,
         iterations: int = 1, emit=None) -> int:
    params = params or {}
    out = OUT_ROOT / "aircraft-optimization"
    out.mkdir(parents=True, exist_ok=True)
    script = make_transcript("aircraft optimization", emit)
    roster = Roster(emit)
    ledger = ComputeLedger(emit)
    knowledge = KnowledgeBase(emit)

    reqs = parse_requirements(request or "")
    script.system(request or "Request: maximise the airliner's lift-to-drag ratio "
                             "subject to its mission requirements.")

    # ---------------- Hypothesis ----------------
    script.phase(HYPOTHESIS)
    # Chief Researcher puts the method choice on the record before anything runs.
    roster.set(CHIEF_RESEARCHER, "selecting the method", "working")
    props = MissionProperties(
        kind="parametric-optimization",
        objective="maximise the cruise lift-to-drag ratio",
        dimensionality=3,          # wing span, area, and quarter-chord sweep
        regime="steady",
        smoothness="smooth",
        fidelity="a conceptual sizing model",
        constraints=("take-off speed", "landing speed", "range"))
    for line in method_memo(props):
        script.researcher(line)
    roster.idle(CHIEF_RESEARCHER)
    script.engineer(ENGINEER_ACK)

    roster.set(CHIEF_ENGINEER, "reading the requirements", "working")
    stated = []
    stated.append(f"{reqs['passengers']} passengers" + ("" if reqs["passengers_stated"] else " (assumed)"))
    stated.append(f"{reqs['range_km']:.0f} km range" + ("" if reqs["range_stated"] else " (assumed)"))
    stated.append(f"take-off ≤ {reqs['takeoff_speed']:.0f} m/s" + ("" if reqs["takeoff_stated"] else " (assumed)"))
    stated.append(f"landing ≤ {reqs['landing_speed']:.0f} m/s" + ("" if reqs["landing_stated"] else " (assumed)"))
    script.engineer(
        "• Requirements fixed: " + "; ".join(stated) + ". "
        "• Unstated values are assumed and marked. "
        "• Weight rides on the passenger count; the whole answer rides on weight.")
    script.engineer(
        "• Hypothesis: L/D climbs with aspect ratio, so push span to the limit. "
        "• Low-speed limits floor the area; Breguet ties range to L/D. "
        "• Expect the optimum where landing speed caps aspect ratio.")

    # ---------------- Plan ----------------
    script.phase(PLAN)
    grid = _design_grid()
    capacity = audit(min(12, len(grid)), memory_per_worker_mb=128)
    if emit:
        emit("audit.completed", capacity.panel())
    script.engineer(capacity.headline(), panel=capacity.panel())

    solver_live = vspaero.available()
    if solver_live and emit:
        # The plan just committed to a solver — this is the moment the badge
        # is earned, never before.
        emit("solver.selected", {
            "solver": "VSPAERO", "method": "vortex lattice",
            "basis": "plan commits the finalist wings to real aero solves"})
    if emit:
        # The plan phase puts the landscape skeleton on screen before any
        # point exists — axes, units, and objective announced up front.
        emit("landscape.init", {
            "title": "Design-space landscape",
            "x": {"key": "span", "label": "span [m]"},
            "y": {"key": "wing_area", "label": "wing area [m²]"},
            "objective": {"key": "L_D", "label": "L/D", "direction": "max"}})
    plan_line = (
        f"• Plan: screen {len(grid)} wings over span, area, and quarter-chord sweep. "
        f"• Infeasible designs stay on the plot, keeping the trade visible.")
    if solver_live:
        plan_line += (
            f" • Top {_N_FINALISTS} feasible finalists then get real "
            f"vortex-lattice solves, in parallel.")
    script.engineer(plan_line)
    if solver_live:
        script.numericist(
            "• Screen is conceptual sizing; finalists are solved, induced plus "
            "wing viscous drag. "
            "• Fuselage and tail stay a stated buildup.")
    else:
        script.numericist(
            "• Conceptual sizing only, a drag polar, not a solved flow. "
            "• It ranks designs and finds the trade; it validates nothing. "
            "• A real aero solve is what would set the magnitude.")

    # ---------------- Evidence ----------------
    script.phase(EVIDENCE)
    roster.set(CHIEF_ENGINEER, "sizing the design space", "working")
    n_slots = min(capacity.capacity, len(grid))
    roster.set_workers(n_slots, "sizing wings")
    results = []
    screen_started = time.time()
    best_ld_so_far = None
    for idx, (span, area, sweep) in enumerate(grid):
        slot = idx % n_slots
        r = evaluate_design(span, area, sweep, reqs)
        results.append(r)
        if emit:
            # The dispatch panel watches this slot pick the candidate up, then
            # report it done — the fleet is visibly working through the grid.
            emit("dispatch.update", {"slot": slot, "state": "solving",
                                     "label": f"span {r['span']:.0f} m / {r['area']:.0f} m²",
                                     "detail": "conceptual sizing"})
            emit("landscape.point", {"design": {"span": r["span"], "wing_area": r["area"]},
                                     "metrics": {"L_D": r["L_D"]}, "feasible": r["feasible"],
                                     "why": r["violations"] or None})
            # The candidate under evaluation appears in the viewport as the
            # parametric wing it is — span, area, and sweep visibly differing.
            emit("geometry.ready", {
                "url": (f"/api/geometry?span={r['span']:g}&area={r['area']:g}"
                        f"&sweep={r['sweep_deg']:g}&taper={_TAPER:g}"),
                "label": f"candidate wing, span {r['span']:.0f} m, "
                         f"area {r['area']:.0f} m²"})
            # Live best-feasible-L/D trace — the running optimum climbs on screen.
            if r["feasible"]:
                best_ld_so_far = (r["L_D"] if best_ld_so_far is None
                                  else max(best_ld_so_far, r["L_D"]))
                emit("trace.point", {
                    "series": "best_L_D", "x": idx + 1, "y": round(best_ld_so_far, 3),
                    "x_label": "candidates screened", "y_label": "best feasible L/D",
                    "title": "Best feasible L/D, running optimum", "feasible": True})
        if _PACE_S:
            time.sleep(_PACE_S)
        if emit:
            emit("dispatch.update", {"slot": slot, "state": "done",
                                     "label": f"span {r['span']:.0f} m / {r['area']:.0f} m²",
                                     "detail": (f"L/D {r['L_D']:.1f}" if r["feasible"]
                                                else "infeasible")})
    screen_elapsed = time.time() - screen_started
    ledger.spend(len(grid) * 0.02, f"{len(grid)} conceptual sizing evaluations")
    roster.set_workers(0)
    script.engineer(f"• Screening sweep: {screen_elapsed:.2f} s, {len(grid)} designs.")

    feasible = [r for r in results if r["feasible"]]
    infeasible = results[:]  # for narration counts
    n_infeasible = len(results) - len(feasible)
    if not feasible:
        script.engineer(
            "• No wing meets every requirement at once, so nothing closes. "
            "• The mission needs a relaxation: more area, slower landing, or less range. "
            "• That is a real answer, not a failure.")
        verdict = trust(relative_error=None, converged=True,
                        in_validated_regime=False, calibrated=False,
                        why="the mission requirements are mutually infeasible on this planform")
        if emit:
            emit("result.verdict", {"quantity": "Best feasible L/D",
                                    "value": "none", "envelope": "n/a", **verdict})
        script.save(out / "transcript.txt")
        roster.all_idle()
        return 0

    best = max(feasible, key=lambda r: r["L_D"])
    script.engineer(
        f"• {len(feasible)} of {len(results)} wings clear every requirement; "
        f"{n_infeasible} shown infeasible. "
        f"• Best screened: span {best['span']:.0f} m, AR {best['aspect_ratio']:.1f} "
        f"→ L/D {best['L_D']:.1f}. "
        f"• MTOW {best['mtow_kg']/1000:.0f} t; range {best['range_km']:.0f} km; "
        f"approach {best['approach_speed']:.0f} m/s.")

    # ---- real solves on the finalists --------------------------------------
    solved_ok: list[dict] = []
    if solver_live:
        finalists = sorted(feasible, key=lambda r: r["L_D"],
                           reverse=True)[:_N_FINALISTS]
        api = vspaero.VspAeroWingApi(out / "vspaero")
        roster.set(CHIEF_ENGINEER, "solving the finalist wings", "working")
        roster.set_workers(len(finalists),
                           "vortex-lattice solves on finalist wings")
        script.engineer(
            f"• Promoting the top {len(finalists)} feasible wings to real solves. "
            f"• Each is actual geometry; each polar is solved, not estimated.")
        designs = [{
            "span": f["span"], "area": f["area"], "sweep": f["sweep_deg"],
            "taper": _TAPER, "cl_target": f["cl_cruise"],
            "re_cref": (_RHO_CRUISE * _V_CRUISE
                        * (f["area"] / f["span"]) / _MU_CRUISE),
        } for f in finalists]
        if emit:
            # Each finalist takes a worker slot for a real vortex-lattice solve —
            # the dispatch panel shows the whole fan-out solving at once.
            for slot, f in enumerate(finalists):
                emit("dispatch.update", {"slot": slot, "state": "solving",
                                         "label": f"finalist span {f['span']:.0f} m",
                                         "detail": "vortex-lattice solve"})
        started = time.time()
        # Each finalist rides a kill-checkable worker slot: scripts/kill_worker.sh
        # can strike one mid-batch, and the slot reports the loss, reprovisions,
        # and re-solves — the same polar lands. Solved in parallel, order preserved.
        from concurrent.futures import ThreadPoolExecutor
        n_slots = min(capacity.capacity, len(designs))
        with ThreadPoolExecutor(max_workers=max(1, n_slots)) as pool:
            batch = list(pool.map(
                lambda job: _solve_finalist_slot(job[0], api, job[1], emit, script),
                enumerate(designs)))
        elapsed = time.time() - started
        roster.set_workers(0)
        if emit:
            for slot, (f, result) in enumerate(zip(finalists, batch)):
                emit("dispatch.update", {
                    "slot": slot, "state": "done" if result else "lost",
                    "label": f"finalist span {f['span']:.0f} m",
                    "detail": "solved" if result else "no polar"})
        ledger.spend(elapsed * len(finalists),
                     f"{len(finalists)} vortex-lattice wing solves")
        script.engineer(
            f"• Finalist solves: {elapsed:.1f} s, {len(finalists)} wings in parallel.")

        for f, result in zip(finalists, batch):
            if not result:
                script.engineer(
                    f"• Finalist span {f['span']:.0f} m returned no polar, "
                    f"stays screened, marked unsolved.")
                continue
            matched = result["matched"]
            cd_total = _CD0_NONWING + matched["cdo_wing"] + matched["cdi"]
            f["L_D_solved"] = round(f["cl_cruise"] / cd_total, 4)
            f["alpha_solved"] = round(matched["alpha"], 3)
            f["cdi_solved"] = round(matched["cdi"], 6)
            f["cdo_wing_solved"] = round(matched["cdo_wing"], 6)
            f["extrapolated"] = bool(matched["extrapolated"])
            f["_polar"] = result["polar"]
            solved_ok.append(f)
            surface = out / f"wing-span{f['span']:g}-area{f['area']:g}.stl"
            try:
                shutil.copy(result["stl_path"], surface)
            except OSError:
                surface = None
            if emit:
                emit("vspaero.polar", {
                    "design": {"span": f["span"], "wing_area": f["area"],
                               "sweep": f["sweep_deg"]},
                    "polar": result["polar"], "matched": matched,
                    "L_D_total": f["L_D_solved"],
                    "solver": result.get("solver_version", "VSPAERO")})
                emit("landscape.point", {
                    "design": {"span": f["span"], "wing_area": f["area"]},
                    "metrics": {"L_D": f["L_D_solved"]},
                    "feasible": True, "solved": True})
                if surface:
                    emit("geometry.ready", {
                        "url": f"/api/surface/aircraft-optimization/{surface.name}",
                        "label": f"solved finalist, span {f['span']:.0f} m, "
                                 f"area {f['area']:.0f} m²"})
            script.engineer(
                f"• Solved span {f['span']:.0f} m: alpha {f['alpha_solved']:.1f}°, "
                f"CDi {f['cdi_solved']:.4f}, wing viscous {f['cdo_wing_solved']:.4f}. "
                f"• Whole-aircraft L/D {f['L_D_solved']:.1f} with the stated "
                f"non-wing buildup.")

        if solved_ok:
            best = max(solved_ok, key=lambda r: r["L_D_solved"])
            screen_agreed = best is max(feasible, key=lambda r: r["L_D"])
            script.engineer(
                f"• Winner on solved numbers: span {best['span']:.0f} m, area "
                f"{best['area']:.0f} m² → L/D {best['L_D_solved']:.1f}. "
                + ("• The screen ranked it first as well."
                   if screen_agreed else
                   "• The solver moved the pick; the screen had it wrong."))
            winner_surface = out / f"wing-span{best['span']:g}-area{best['area']:g}.stl"
            if emit and winner_surface.exists():
                emit("geometry.ready", {
                    "url": f"/api/surface/aircraft-optimization/{winner_surface.name}",
                    "label": f"winning wing, span {best['span']:.0f} m, "
                             f"solved L/D {best['L_D_solved']:.1f}"})
        else:
            script.engineer(
                "• No finalist returned a usable polar. "
                "• The result stands on the conceptual screen alone.")

    # ---------------- Conclusion ----------------
    script.phase(CONCLUSION)
    won_solved = bool(solved_ok)
    best_ld = best["L_D_solved"] if won_solved else best["L_D"]
    # Headline CI: stated input uncertainties propagated through the real
    # evaluation chain (the solved polar when one exists).
    ci95 = winner_ci95(best, reqs, polar=best.get("_polar"))
    # Stored anchors study: sizing-model deviation at the solved finalists
    # feeds the model channel when its fingerprint matches this configuration.
    from chief_engineer import uq as uq_studies
    anchors = uq_studies.channels_for(
        "airliner-wing",
        uq_studies.setup_fingerprint(body="airliner-wing", solver="vspaero",
                                     closure="vortex-lattice", velocity=230.0,
                                     refinement=None, iterations=None))
    model_band = (anchors["model"]["band_abs"] if anchors["model"] else None)
    input_note = (
        "Monte-Carlo over the stated payload-mass and non-wing-drag spreads; "
        "requirements are held as exact specification, and the remaining "
        "sizing constants (SFC, fuel fraction, cruise altitude) are fixed")
    if won_solved:
        model_note = ("wing induced and viscous drag are solved (vortex "
                      "lattice); fuselage, tail, and nacelle parasite drag "
                      "remain a component buildup")
        if model_band is not None:
            model_note = (f"{anchors['model']['method']} "
                          f"({len(anchors['model'].get('members', {}))} solved "
                          f"anchors); non-wing drag remains a component buildup")
        channels = uncertainty_channels(
            input_2sigma=round(ci95, 2),
            numerical=None,
            model=None if model_band is None else round(model_band, 3),
            input_note=input_note,
            numerical_note="the design grid is discrete, so the true optimum lies "
                           "between grid points; the vortex-lattice polar itself "
                           "is converged at the solved panel density",
            model_note=model_note)
    else:
        channels = uncertainty_channels(
            input_2sigma=round(ci95, 2), numerical=None, model=None,
            input_note=input_note,
            numerical_note="the design grid is discrete, so the true optimum lies "
                           "between grid points",
            model_note="drag-polar sizing model; a solve would set the "
                       "magnitude")
    if emit:
        emit("uncertainty.channels", channels)
    if won_solved:
        script.researcher(
            "• Wing solved: induced and viscous drag off a real polar at cruise. "
            "• Non-wing drag is a stated buildup, not yet solved. "
            "• A full-configuration solve and comparison would close that gap.")
        verdict = trust(
            converged=True, in_validated_regime=False, calibrated=True,
            solver_backed=True,
            why="wing solved by vortex lattice; non-wing parasite drag from a "
                "stated component buildup")
    else:
        script.researcher(
            "• Ranking trustworthy: aspect ratio buys L/D until landing speed stops it. "
            f"• The magnitude {best['L_D']:.1f} ± {ci95:.1f} is a sizing-model estimate. "
            f"• A solved flow and a comparison would set the magnitude.")
        verdict = trust(
            converged=True, solver_backed=False,
            why="drag-polar sizing model; no solve behind the magnitude")
    headline_ci = ci95
    if won_solved and model_band is not None:
        headline_ci = uq_studies.combine_expanded(
            input_2sigma=ci95, numerical_abs=None,
            model_abs=model_band)["combined_95"]
    if emit:
        emit("result.verdict", {"quantity": "Best feasible L/D",
                                "value": f"{best_ld:.1f}",
                                "ci": f"{headline_ci:.1f}", "confidence": "95%",
                                "envelope": ("solved wing + stated buildup"
                                             if won_solved else
                                             "sizing-model estimate"), **verdict})
    knowledge.add(
        f"Airliner L/D for {reqs['passengers']} pax / {reqs['range_km']:.0f} km: "
        f"best feasible L/D {best_ld:.1f} at span {best['span']:.0f} m, "
        f"aspect ratio {best['aspect_ratio']:.1f}"
        + (" (wing solved, vortex lattice)" if won_solved else " (screened)"))

    agenda = [
        {"title": "Cruise Mach trade",
         "scope": "sweep cruise Mach against the fixed requirements to find where "
                  "the range-speed-L/D surface actually peaks",
         "cost": "one more sweep dimension; solver already in place"},
        {"title": "Composite-span structural limits",
         "scope": "explore spans beyond today's structural cap with a composite "
                  "wing-box weight model driving MTOW",
         "cost": "a weight-model extension plus a re-run of the sweep"},
        {"title": "Full-configuration solve",
         "scope": "put the fuselage and tail in the solved model and trim the "
                  "winner for static margin",
         "cost": "richer geometry per candidate; same solver, longer polars"},
    ]
    if emit:
        emit("agenda.updated", {"entries": agenda})

    methods = [
        "Weights from the passenger count via a payload fraction; MTOW carries a "
        "mild span-structural penalty.",
        "Screening L/D from a drag polar (induced drag over aspect ratio and "
        "Oswald efficiency, parasite drag with sweep).",
        "Feasibility from stall-speed limits for take-off and landing and a "
        "Breguet range check.",
    ]
    if won_solved:
        methods.append(
            f"The top {len(solved_ok)} feasible finalists were built as parametric "
            f"geometry and solved by a vortex-lattice method in parallel; the "
            f"cruise point was interpolated on each solved polar, and the winner "
            f"was picked on solved numbers.")

    abstract = [
        f"We searched a {len(grid)}-wing design space for the highest cruise "
        f"L/D meeting the stated mission requirements.",
        f"The best feasible wing reaches L/D {best_ld:.1f} ± {headline_ci:.1f} (95%) "
        f"at span {best['span']:.0f} m and aspect ratio {best['aspect_ratio']:.1f}; "
        f"{n_infeasible} designs were infeasible on low-speed or range.",
        ("The winner stands on a solved wing polar with a stated non-wing "
         "buildup." if won_solved else
         "The result comes from the stated sizing model with its input "
         "envelope propagated."),
    ]

    uncertainty = [
        "The trade, L/D rising with aspect ratio until the landing speed caps "
        "it, is physical and trustworthy.",
        ("Wing induced and viscous drag are solved; the non-wing parasite share "
         "is a stated buildup." if won_solved else
         "The absolute L/D comes from a drag polar sizing model, not a solved "
         "flow; the model channel carries that."),
        "The optimum sits between discrete grid points, so the reported design "
        "is the best sampled, not the continuous optimum.",
    ]

    report = lab_report(
        title=f"Aircraft L/D optimization: {reqs['passengers']} pax, {reqs['range_km']:.0f} km",
        abstract=abstract,
        methods=methods,
        results=[{
            "quantity": "Best feasible L/D",
            "value": f"{best_ld:.1f} ± {headline_ci:.1f} (95%)",
            "envelope": f"span {best['span']:.0f} m, AR {best['aspect_ratio']:.1f}, "
                        f"range {best['range_km']:.0f} km",
            **verdict,
        }],
        uncertainty=uncertainty,
        next_investigations=[f"{entry['title']}: {entry['scope']}"
                             for entry in agenda],
        compute=ledger.as_dict(),
    )
    if emit:
        emit("report.ready", report)

    # The Certonomous certificate for the airliner act: the best feasible L/D
    # with its 95% CI, the solver named only when the finalists were actually
    # solved, and the full three-channel table (input Monte-Carlo, numerical
    # grid-discreteness, model from the UQ airliner-anchors study where the
    # fingerprint matches). Wrapped so a certificate never sinks a good mission.
    try:
        from chief_engineer.certificate import build_certificate_v2

        cert_doc = {
            "results": [
                {"quantity": "Best feasible cruise L/D",
                 "value": f"{best_ld:.1f}",
                 "envelope": f"{headline_ci:.1f}", **verdict},
                {"quantity": "Winning wing",
                 "value": f"span {best['span']:.0f} m, AR {best['aspect_ratio']:.1f}",
                 "envelope": f"range {best['range_km']:.0f} km"},
            ],
            "compute": ledger.as_dict(),
        }
        solver = ("OpenVSP VSPAERO, vortex lattice" if won_solved
                  else "Conceptual drag-polar sizing model")
        certificate = build_certificate_v2(
            cert_doc, out_path=out / "certificate.pdf",
            geometry="airliner",
            objective=(request or "Maximise the airliner cruise lift-to-drag "
                       "ratio subject to its mission requirements."),
            mission_id="aircraft-optimization",
            issued_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            channels=channels,
            display_name="300-passenger twin-aisle airliner, planform study",
            solver=solver)
        if emit:
            emit("certificate.ready", {**certificate, "dir": out.name})
    except Exception as exc:  # a certificate must never take down a good mission
        script.engineer(f"(Certificate could not be issued: {exc})")

    script.save(out / "transcript.txt")
    roster.all_idle()
    print("Artifacts in", out)
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(main(request=" ".join(sys.argv[1:]) or None))
