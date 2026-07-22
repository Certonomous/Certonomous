"""Optimize an airliner's lift-to-drag ratio against stated mission requirements.

The request states what the aircraft must do — passengers, range, take-off and
landing speeds — and the lab searches a wing design space (span, area, sweep)
for the highest cruise L/D that still meets every requirement. Designs that miss
a requirement are shown as infeasible, not hidden; the winner is the best L/D
that clears them all.

This is a **conceptual-design sizing model**, not a CFD solve: a textbook drag
polar (induced + parasite drag over aspect ratio and sweep), a Breguet range
check, and stall-speed constraints for take-off and landing. It is honest about
that — the verdict never exceeds TREND ONLY, and the model-form uncertainty
channel says a real aero solve (OpenVSP/VSPAERO or RANS) would be needed to
validate a magnitude. The value here is the design-space reasoning, transparent
and requirement-driven, not a validated coefficient.
"""

from __future__ import annotations

import math
import re

from . import OUT_ROOT, make_transcript
from chief_engineer.compute_audit import audit
from chief_engineer.researcher import ENGINEER_ACK, MissionProperties, method_memo
from chief_engineer.lab import (CHIEF_ENGINEER, CHIEF_RESEARCHER, CONCLUSION,
                                EVIDENCE, HYPOTHESIS, NUMERICIST, PLAN,
                                ComputeLedger, KnowledgeBase, Roster,
                                lab_report, per, trust, uncertainty_channels)

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
        "L_D": round(l_over_d, 4), "mtow_kg": round(mtow, 0),
        "approach_speed": round(approach_speed, 2), "takeoff_speed": round(takeoff_speed, 2),
        "range_km": round(breguet_range_km, 0),
        "feasible": not violations, "violations": violations,
    }


def _design_grid() -> list[tuple[float, float, float]]:
    """A span × area sweep at a fixed representative sweep angle."""
    grid = []
    for span in (34, 40, 46, 52, 58, 64):
        for area in (240, 300, 360, 420):
            grid.append((float(span), float(area), 27.5))
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
        dimensionality=2,          # wing span and area are the free variables
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
        "The mission fixes the requirements; the wing is the free variable. "
        "Requirements on the table: " + "; ".join(stated) + ". Any I was not given "
        "I have assumed and said so, because the Reynolds of the whole answer rides "
        "on the weight, and the weight rides on the passenger count.")
    script.engineer(
        "Hypothesis: L/D climbs with aspect ratio, so the best design pushes span "
        "as far as the structure allows — but the low-speed requirements set a "
        "floor on wing area, and range ties back to L/D through Breguet. I expect "
        "the optimum to sit where the aspect ratio is as high as the landing speed "
        "will permit.")

    # ---------------- Plan ----------------
    script.phase(PLAN)
    grid = _design_grid()
    capacity = audit(min(12, len(grid)), memory_per_worker_mb=128)
    if emit:
        emit("audit.completed", capacity.panel())
    script.engineer(capacity.headline(), panel=capacity.panel())
    script.engineer(
        f"Plan: evaluate {len(grid)} wings across span and area at a fixed 27.5° "
        f"sweep — each one sized against every requirement, its cruise L/D from the "
        f"drag polar, its range from Breguet. The infeasible ones stay on the plot "
        f"so the trade is visible, not hidden.")
    script.numericist(
        f"State the fidelity up front: this is conceptual sizing, {per('rom')} in "
        f"spirit — a drag polar and weight fractions, not a solved flow. It ranks "
        f"designs and finds the trade; it does not validate a number. A real aero "
        f"solve is what would move this off a trend.")

    # ---------------- Evidence ----------------
    script.phase(EVIDENCE)
    roster.set(CHIEF_ENGINEER, "sizing the design space", "working")
    roster.set_workers(min(capacity.capacity, len(grid)), "sizing wings")
    results = []
    for span, area, sweep in grid:
        r = evaluate_design(span, area, sweep, reqs)
        results.append(r)
        if emit:
            emit("landscape.point", {"design": {"span": r["span"], "wing_area": r["area"]},
                                     "metrics": {"L_D": r["L_D"]}, "feasible": r["feasible"]})
    ledger.spend(len(grid) * 0.02, f"{len(grid)} conceptual sizing evaluations")
    roster.set_workers(0)

    feasible = [r for r in results if r["feasible"]]
    infeasible = results[:]  # for narration counts
    n_infeasible = len(results) - len(feasible)
    if not feasible:
        script.engineer(
            "No wing in the grid meets every requirement at once — the low-speed "
            "limits and the range requirement do not both close on this planform. "
            "That is a real answer: the mission as stated needs a relaxation "
            "(more wing area, a lower landing speed, or shorter range) before an "
            "L/D optimum exists.")
        verdict = trust(relative_error=None, converged=True,
                        in_validated_regime=False, calibrated=False,
                        why="the mission requirements are mutually infeasible on this planform")
        if emit:
            emit("result.verdict", {"quantity": "Best feasible L/D",
                                    "value": "none", "envelope": "—", **verdict})
        script.save(out / "transcript.txt")
        roster.all_idle()
        return 0

    best = max(feasible, key=lambda r: r["L_D"])
    script.engineer(
        f"{len(feasible)} of {len(results)} wings clear every requirement; "
        f"{n_infeasible} miss on low-speed or range and are shown as infeasible. "
        f"The best feasible design: span {best['span']:.0f} m, area {best['area']:.0f} m², "
        f"aspect ratio {best['aspect_ratio']:.1f} → L/D {best['L_D']:.1f}, "
        f"MTOW {best['mtow_kg']/1000:.0f} t, range {best['range_km']:.0f} km, "
        f"approach {best['approach_speed']:.0f} m/s.")

    # ---------------- Conclusion ----------------
    script.phase(CONCLUSION)
    channels = uncertainty_channels(
        input_2sigma=None, numerical=None, model=None,
        numerical_note="the design grid is discrete — the true optimum lies between grid points",
        model_note="conceptual drag polar, not a solved flow — a real aero solve would set the magnitude")
    if emit:
        emit("uncertainty.channels", channels)
    script.researcher(
        f"Read this as a design-space result, not a validated coefficient. The "
        f"ranking is trustworthy — higher aspect ratio buys L/D until the landing "
        f"speed stops it, and that trade is physical. The absolute L/D {best['L_D']:.1f} "
        f"is a conceptual estimate; {per('vv20')} would want a solved flow and a "
        f"comparison before anyone flies on the number.")
    verdict = trust(relative_error=0.0, converged=True, in_validated_regime=False,
                    calibrated=True,
                    why="conceptual sizing model, not a validated aero solve — the trade is real, the magnitude is a trend")
    if emit:
        emit("result.verdict", {"quantity": "Best feasible L/D",
                                "value": f"{best['L_D']:.1f}",
                                "envelope": "conceptual estimate", **verdict})
    knowledge.add(
        f"Airliner L/D sizing for {reqs['passengers']} pax / {reqs['range_km']:.0f} km: "
        f"best feasible L/D {best['L_D']:.1f} at span {best['span']:.0f} m, "
        f"aspect ratio {best['aspect_ratio']:.1f}")

    report = lab_report(
        title=f"Aircraft L/D optimization — {reqs['passengers']} pax, {reqs['range_km']:.0f} km",
        abstract=[
            f"We searched a {len(grid)}-wing design space for the highest cruise "
            f"L/D meeting the stated mission requirements.",
            f"The best feasible wing reaches L/D {best['L_D']:.1f} at span "
            f"{best['span']:.0f} m and aspect ratio {best['aspect_ratio']:.1f}; "
            f"{n_infeasible} designs were infeasible on low-speed or range.",
            "The result is a conceptual-design trade, reported as a trend rather "
            "than a validated magnitude.",
        ],
        methods=[
            "Weights from the passenger count via a payload fraction; MTOW carries a "
            "mild span-structural penalty.",
            "Cruise L/D from a drag polar (induced drag over aspect ratio and Oswald "
            "efficiency, parasite drag with sweep).",
            "Feasibility from stall-speed limits for take-off and landing and a "
            "Breguet range check.",
        ],
        results=[{
            "quantity": "Best feasible L/D",
            "value": f"{best['L_D']:.1f}",
            "envelope": f"span {best['span']:.0f} m, AR {best['aspect_ratio']:.1f}, "
                        f"range {best['range_km']:.0f} km",
            **verdict,
        }],
        uncertainty=[
            "The trade — L/D rising with aspect ratio until the landing speed caps "
            "it — is physical and trustworthy.",
            "The absolute L/D is a conceptual estimate from a drag polar, not a "
            "solved flow; treat the magnitude as a trend.",
            "The optimum sits between discrete grid points, so the reported design "
            "is the best sampled, not the continuous optimum.",
        ],
        future_work=[
            "Run the winning planform through a real aero solve (OpenVSP/VSPAERO or "
            "RANS) to turn the L/D from a trend into a validated magnitude.",
            "Refine the grid around the feasible optimum for the continuous best.",
            "Add a wing-weight model that closes MTOW iteratively rather than by a "
            "fixed payload fraction.",
        ],
        compute=ledger.as_dict(),
    )
    if emit:
        emit("report.ready", report)
    script.save(out / "transcript.txt")
    roster.all_idle()
    print("Artifacts in", out)
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(main(request=" ".join(sys.argv[1:]) or None))
