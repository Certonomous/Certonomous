"""Variance-based sensitivity mission: which input owns the output spread.

The lab already propagates stated input spreads through its screens and quotes
one envelope out. That envelope says how wide the answer is; it never says
WHICH input made it wide, so any campaign to buy the spread down is aimed by
guesswork. This mission aims it by measurement.

The method is the pick-and-freeze (Saltelli) variance decomposition offered by
Dakota under sampling with variance-based decomposition: two independent base
matrices of ``n_base`` rows plus one column-swapped matrix per input, cost
``n_base * (M + 2)`` evaluations, from which the first-order (main) index

    S_i  = Var_i[ E(Y | X_i) ] / Var(Y)

and the total-effect index S_T_i follow. S_i is the variance share the input
owns alone; S_T_i is its share including every interaction it takes part in,
and the gap between the two IS the interaction. An input whose total index is
small can be frozen at its nominal value without moving the envelope.

The primitive is ``chief_engineer.sensitivity`` (Saltelli 2010 main estimator,
Jansen 1999 total estimator, percentile bootstrap intervals, deterministic
given the seed). Its offline evidence, on the two models below plus the
closed-form Ishigami benchmark, is recorded in the Innovation Standard.

Adoption conditions this mission enforces on camera, exactly as the standard
writes them:

* Every Sobol identity must hold within bootstrap interval (indices in [0, 1],
  main at or below total per input, mains summing to at most 1). A run that
  fails an identity is sampling noise and is reported as such, never as
  physics.
* Two inputs whose intervals overlap are UNRESOLVED at that budget, never
  force-ranked. The mission then spends more base samples until they separate
  and reports the budget that did it.
* The indices inherit the fidelity of the model they were measured on: a
  ranking taken through a research-model screen aims uncertainty work at that
  screen and claims nothing about a solved flow.
* The input distributions are each act's own published spreads, never spreads
  invented for the decomposition.

Two cases run, both on reduced-order paths at microsecond cost per evaluation:
the valve screen's cycle-weighted pressure loss over its flow-amplitude and
discharge-coefficient spreads, and the airliner sizing chain's cruise lift to
drag over its payload-mass and non-wing drag spreads.

    python -m workflows.sobol_sensitivity
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import yaml

from . import (OUT_ROOT, announce_plot, emit_table, make_transcript)
from chief_engineer.compute_audit import audit
from chief_engineer.lab import (CHIEF_ENGINEER, CHIEF_RESEARCHER, CONCLUSION,
                                EVIDENCE, HYPOTHESIS, NUMERICIST, PLAN,
                                ComputeLedger, KnowledgeBase, Roster,
                                lab_report, trust, uncertainty_channels)
from chief_engineer.plot_theme import variance_share_figure
from chief_engineer.sensitivity import (SobolIndices, normal_input,
                                        sobol_indices, uniform_sigma_input)

# Admissibility lives in the governed physics file, never as constants here,
# so a ruling on camera points at a stated criterion. The opening design is
# the N of 200 the approved proposal priced; the ceiling is where a mission
# stops escalating and reports the ranking unresolved rather than inventing
# an order. Defaults below are the file's own values and exist only so the
# module still imports if the file cannot be read.
_PHYSICS_RULES = Path(__file__).resolve().parents[2] / "docs" / "physics_rules.yaml"


def _gates() -> dict:
    try:
        data = yaml.safe_load(_PHYSICS_RULES.read_text(encoding="utf-8")) or {}
    except OSError:
        data = {}
    rules = data.get("sobol") or {}
    return {
        "identity_slack": float(rules.get("identity_slack", 0.05)),
        "min_base_samples": int(rules.get("min_base_samples", 200)),
        "max_base_samples": int(rules.get("max_base_samples", 3200)),
        "bootstrap_resamples": int(rules.get("bootstrap_resamples", 200)),
        "confidence_level": float(rules.get("confidence_level", 0.95)),
    }


# One seed per case, fixed, so the whole mission replays to the last digit.
SEED_VALVE = 20260731
SEED_AIRLINER = 20260732

_INDEX_HEADERS = ("Input", "Main Effect", "Interval (95%)",
                  "Total Effect", "Interval (95%)")
_LADDER_HEADERS = ("Base Sample", "Evaluations", "Leading Input",
                   "Runner Up", "Gate Cleared")
_CORNER_HEADERS = ("Corner", "Dominant Input", "Output", "Swing")

CITATIONS = (
    "Dakota Reference Manual, Sampling With Variance Based Decomposition, "
    "Sandia National Laboratories",
    "Dakota Theory Manual, Stochastic Expansion Methods, Sandia National "
    "Laboratories",
)

AGENDA = [
    {"title": "Correlated input spreads",
     "scope": "estimate variance shares when two inputs are dependent, which "
              "pick-and-freeze cannot do, so a case whose spreads move "
              "together can still be apportioned",
     "cost": "comparable per evaluation; a different estimator"},
    {"title": "Second-order index map",
     "scope": "resolve the interaction the main-to-total gap only totals, "
              "naming which pair of inputs it belongs to",
     "cost": "N times (2M + 2) evaluations"},
    {"title": "Variance apportionment through a solved path",
     "scope": "carry the same decomposition through a meshed and solved case "
              "so the ranking speaks about the flow rather than the screen "
              "that stands in for it",
     "cost": "one solve per evaluation; a multifidelity estimator first"},
]


# --------------------------------------------------------------------------
# The two cases, each built from its own act's published spreads
# --------------------------------------------------------------------------

def _valve_case() -> dict:
    """The valve screen's cycle-weighted loss over the spreads it publishes."""
    from workflows import valve_study as vs

    phases = vs.phase_points()
    admissible = [a for a in vs.CANDIDATE_ANGLES
                  if vs.effective_orifice_area(a) >= vs.MIN_ORIFICE_AREA]
    winner = min(admissible, key=lambda a: vs._cycle_weighted_loss(a, phases))
    area = vs.effective_orifice_area(winner)

    def model(flow_f: float, cd_f: float) -> float:
        return sum(p.weight * vs._phase_pressure_loss(
            p.flow_rate * flow_f, area, vs.DISCHARGE_COEFF * cd_f)
            for p in phases)

    return {
        "key": "valve",
        "title": "Valve screen, cycle-weighted pressure loss",
        "output": "cycle-weighted pressure loss",
        "unit": "Pa",
        "model": model,
        "dists": {
            "flow amplitude": uniform_sigma_input(1.0, vs.FLOW_SIGMA),
            "discharge coefficient": uniform_sigma_input(1.0, vs.CD_SIGMA),
        },
        "sigmas": {"flow amplitude": vs.FLOW_SIGMA,
                   "discharge coefficient": vs.CD_SIGMA},
        "family": "bounded uniform at a matching 1-sigma, the convention this "
                  "screen's own envelope sweeps",
        "seed": SEED_VALVE,
        "setting": f"leaflet opening {winner:g} degrees, orifice "
                   f"{area * 1e6:.0f} mm^2",
        "fidelity": "research model",
        "buy_down": {
            "discharge coefficient": "a solved phase point, or an orifice "
                                     "correlation calibrated at this bore "
                                     "ratio",
            "flow amplitude": "a tighter measurement of the ejection waveform",
        },
    }


def _airliner_case() -> dict:
    """The airliner sizing chain's cruise L/D over the spreads it publishes."""
    from workflows.aircraft_optimization import (_CD0_NONWING,
                                                 _SIGMA_CD0_NONWING,
                                                 _SIGMA_PAYLOAD, _design_grid,
                                                 evaluate_design,
                                                 parse_requirements)

    reqs = parse_requirements("")
    screened = [evaluate_design(s, a, w, reqs) for s, a, w in _design_grid()]
    winner = max((d for d in screened if d["feasible"]), key=lambda d: d["L_D"])

    def model(mass_f: float, cd0_f: float) -> float:
        perturbed = dict(reqs)
        perturbed["passengers"] = reqs["passengers"] * mass_f
        r = evaluate_design(winner["span"], winner["area"],
                            winner["sweep_deg"], perturbed)
        cl = r["cl_cruise"]
        cd = cl / r["L_D"]
        return cl / (cd + (cd0_f - 1.0) * _CD0_NONWING)

    return {
        "key": "airliner",
        "title": "Airliner sizing chain, cruise lift to drag",
        "output": "cruise lift to drag",
        "unit": "",
        "model": model,
        "dists": {"payload mass": normal_input(1.0, _SIGMA_PAYLOAD),
                  "non-wing drag": normal_input(1.0, _SIGMA_CD0_NONWING)},
        "sigmas": {"payload mass": _SIGMA_PAYLOAD,
                   "non-wing drag": _SIGMA_CD0_NONWING},
        "family": "Gaussian, the convention this act's 95% interval quotes",
        "seed": SEED_AIRLINER,
        "setting": f"winning planform, span {winner['span']:g} m, area "
                   f"{winner['area']:g} m^2, sweep {winner['sweep_deg']:g} "
                   f"degrees",
        "fidelity": "research model",
        "buy_down": {
            "non-wing drag": "a component drag build measured against a "
                             "solved fuselage and empennage",
            "payload mass": "a firmer payload definition from the "
                            "requirement owner",
        },
    }


# --------------------------------------------------------------------------
# Reading the indices
# --------------------------------------------------------------------------

def _overlap(a: tuple[float, float], b: tuple[float, float]) -> bool:
    return a[1] >= b[0] and b[1] >= a[0]


def _leading_pair(result: SobolIndices) -> tuple[tuple, tuple]:
    """The two largest main effects, each as (name, index, interval)."""
    rows = sorted(
        ((name, result.main[i], result.main_ci[i])
         for i, name in enumerate(result.names)),
        key=lambda r: r[1], reverse=True)
    return rows[0], rows[1]


def _separated(result: SobolIndices) -> bool:
    """Is the leading input's share distinguishable from the runner up's?"""
    lead, runner = _leading_pair(result)
    return not _overlap(lead[2], runner[2])


def _point_identities(result: SobolIndices, slack: float) -> dict[str, bool]:
    """The Sobol identities on the POINT estimates, at the governed slack.

    ``SobolIndices.identity_report`` widens each check by the bootstrap
    interval, which is the right test for whether the estimator is consistent
    with the identity. It is not the right test for whether the numbers are
    fit to put on screen: at a small base sample the interval is wide enough
    to excuse first-order indices summing to 1.2 of the whole variance, and a
    variance share above the whole variance is not a share. This check holds
    the point estimates to the fixed slack the physics file states, and a run
    that fails it is noise-dominated and buys more base samples.
    """
    report = dict(result.identity_report(slack=slack))
    report["mains sum within slack of 1"] = sum(result.main) <= 1.0 + slack
    return report


def _index_rows(result: SobolIndices) -> list[list[str]]:
    rows = []
    for i, name in enumerate(result.names):
        m_lo, m_hi = result.main_ci[i]
        t_lo, t_hi = result.total_ci[i]
        rows.append([name,
                     f"{result.main[i]:.3f}",
                     f"{m_lo:.3f} to {m_hi:.3f}",
                     f"{result.total[i]:.3f}",
                     f"{t_lo:.3f} to {t_hi:.3f}"])
    return rows


def _admissible(result: SobolIndices, gates: dict) -> bool:
    """Separated leaders AND identities holding on the point estimates."""
    return (_separated(result)
            and all(_point_identities(result, gates["identity_slack"]).values()))


def _ladder(case: dict, gates: dict) -> tuple[list[SobolIndices], bool]:
    """Run the approved budget, then double it until the run is admissible."""
    rungs: list[SobolIndices] = []
    n = gates["min_base_samples"]
    while True:
        rungs.append(sobol_indices(
            case["model"], case["dists"], n_base=n, seed=case["seed"],
            bootstrap=gates["bootstrap_resamples"],
            ci_level=gates["confidence_level"]))
        if _admissible(rungs[-1], gates) or n >= gates["max_base_samples"]:
            break
        n *= 2
    return rungs, _admissible(rungs[-1], gates)


def _corner_check(case: dict, result: SobolIndices) -> dict:
    """Evaluate the model at the dominant input's own spread corners.

    The decomposition says which input owns the variance; this confirms the
    claim the direct way, by moving that input across its spread with every
    other input at nominal and reading the swing off the output. It runs on
    the same path the indices were measured on, so it prices that path and
    nothing beyond it.
    """
    lead, _ = _leading_pair(result)
    names = list(result.names)
    index = names.index(lead[0])
    sigma = case["sigmas"][lead[0]]
    # The bounded-uniform convention places its edges at 1 +/- sigma*sqrt(3);
    # a Gaussian input is walked to the same nominal multiple so the two
    # cases' corners are read on one convention.
    reach = sigma * (3.0 ** 0.5)
    nominal = [1.0] * len(names)
    lo = list(nominal); lo[index] = 1.0 - reach
    hi = list(nominal); hi[index] = 1.0 + reach
    f_nom = float(case["model"](*nominal))
    f_lo = float(case["model"](*lo))
    f_hi = float(case["model"](*hi))
    return {"input": lead[0], "reach": reach, "nominal": f_nom,
            "low": f_lo, "high": f_hi,
            "swing": abs(f_hi - f_lo),
            "relative": abs(f_hi - f_lo) / abs(f_nom) if f_nom else 0.0}


# --------------------------------------------------------------------------
# The mission
# --------------------------------------------------------------------------

def _fmt(value: float, unit: str) -> str:
    text = f"{value:.4g}"
    return f"{text} {unit}".strip()


def _run_case(case: dict, *, script, emit, roster, ledger, out: Path,
              gates: dict) -> dict:
    roster.set(CHIEF_ENGINEER, f"apportioning the {case['key']} variance",
               "working")
    spreads = ", ".join(f"{name} {sigma * 100:g}%"
                        for name, sigma in case["sigmas"].items())
    script.engineer(
        f"• Case: {case['title']}, at its {case['setting']}. "
        f"• Published spreads carried in: {spreads}, 1-sigma. "
        f"• Family: {case['family']}.")

    started = time.time()
    rungs, resolved = _ladder(case, gates)
    elapsed = time.time() - started
    final = rungs[-1]

    def _rung_verdict(r: SobolIndices) -> str:
        if not _separated(r):
            return "No, the two intervals overlap"
        broken = [name for name, ok
                  in _point_identities(r, gates["identity_slack"]).items()
                  if not ok]
        if broken:
            return f"No, {broken[0]} fails"
        return "Yes"

    emit_table(emit, script, role=CHIEF_ENGINEER,
               title=f"Sample ladder, {case['title']}",
               headers=list(_LADDER_HEADERS),
               rows=[[f"{r.n_base}", f"{r.n_evaluations}",
                      f"{_leading_pair(r)[0][0]} {_leading_pair(r)[0][1]:.3f}",
                      f"{_leading_pair(r)[1][0]} {_leading_pair(r)[1][1]:.3f}",
                      _rung_verdict(r)]
                     for r in rungs],
               table_id=f"sobol-ladder-{case['key']}")

    if len(rungs) == 1:
        script.engineer(
            f"• The approved design settles it: base sample "
            f"{final.n_base}, {final.n_evaluations} evaluations. "
            f"• The two intervals do not overlap and every identity holds on "
            f"the point estimates. "
            f"• The order is measured rather than asserted.")
    elif resolved:
        script.engineer(
            f"• The approved design of {gates['min_base_samples']} base "
            f"samples does not clear the gate, so no order is claimed there. "
            f"• Doubling to a base sample of {final.n_base} "
            f"({final.n_evaluations} evaluations) clears it. "
            f"• That is the budget this ranking rests on.")
    else:
        script.engineer(
            f"• The gate is still not cleared at the "
            f"{gates['max_base_samples']} base-sample ceiling the physics "
            f"file sets. "
            f"• The ranking is unresolved at this budget and the mission "
            f"reports it that way. "
            f"• Nothing is force-ranked out of overlapping intervals.")

    emit_table(emit, script, role=CHIEF_ENGINEER,
               title=f"Variance shares, {case['title']}",
               headers=list(_INDEX_HEADERS), rows=_index_rows(final),
               table_id=f"sobol-indices-{case['key']}")

    # --- the identity gate, at the slack the physics file states -----------
    identities = _point_identities(final, gates["identity_slack"])
    passed = sum(1 for ok in identities.values() if ok)
    if all(identities.values()):
        script.numericist(
            f"• Every Sobol identity holds at the "
            f"{gates['identity_slack']:g} slack the physics file states: "
            f"{passed} of {len(identities)}. "
            f"• Indices inside 0 to 1, each main effect at or under its "
            f"total, the first-order shares summing to at most the whole "
            f"variance. "
            f"• The apportionment is admissible.")
    else:
        failed = [name for name, ok in identities.items() if not ok]
        script.numericist(
            f"• A Sobol identity fails: {failed[0]}. "
            f"• {passed} of {len(identities)} hold. "
            f"• This is sampling noise, not physics, and no ranking is "
            f"read off it.")

    interaction = max(t - s for s, t in zip(final.main, final.total))
    if interaction > gates["identity_slack"]:
        interaction_line = (
            f"• Widest gap between a total effect and its own first-order "
            f"share: {interaction:.3f}. "
            f"• That gap is the interaction the single-input picture leaves "
            f"out.")
    else:
        interaction_line = (
            f"• Widest gap between a total effect and its own first-order "
            f"share: {max(interaction, 0.0):.3f}, under the "
            f"{gates['identity_slack']:g} slack. "
            f"• No interaction is resolvable above the estimator's own "
            f"scatter, so a single-input reduction campaign is well posed "
            f"here.")
    script.numericist(
        f"• First-order shares sum to {sum(final.main):.3f} of the whole "
        f"variance. " + interaction_line)

    corner = _corner_check(case, final)
    emit_table(emit, script, role=NUMERICIST,
               title=f"Corner check, {case['title']}",
               headers=list(_CORNER_HEADERS),
               rows=[["Low edge", corner["input"],
                      _fmt(corner["low"], case["unit"]),
                      f"{(corner['low'] - corner['nominal']) / corner['nominal'] * 100:+.1f}%"],
                     ["Nominal", corner["input"],
                      _fmt(corner["nominal"], case["unit"]), "0.0%"],
                     ["High edge", corner["input"],
                      _fmt(corner["high"], case["unit"]),
                      f"{(corner['high'] - corner['nominal']) / corner['nominal'] * 100:+.1f}%"]],
               table_id=f"sobol-corner-{case['key']}")
    script.numericist(
        f"• Corner check on the leading input: {corner['input']} walked "
        f"across its own spread with every other input at nominal. "
        f"• The {case['output']} swings {corner['relative'] * 100:.1f}% of "
        f"its nominal value. "
        f"• The swing is measured on the same path the shares were, so it "
        f"prices that path and claims nothing past it.")

    lead, runner = _leading_pair(final)
    png = variance_share_figure(
        out / f"variance_share_{case['key']}.png",
        list(final.names), list(final.main), list(final.total),
        list(final.main_ci), list(final.total_ci),
        title=f"{case['title']}: variance share per input",
        subtitle=(f"pick-and-freeze, base sample {final.n_base}, "
                  f"{final.n_evaluations} evaluations, seed {final.seed}"))
    if png:
        announce_plot(emit, "sobol-sensitivity", png,
                      f"Variance share per input: {case['title']}")

    ledger.spend(elapsed, f"{sum(r.n_evaluations for r in rungs)} "
                          f"reduced-order evaluations, {case['key']} case")
    roster.idle(CHIEF_ENGINEER)
    return {"case": case, "rungs": rungs, "result": final,
            "resolved": resolved, "identities": identities,
            "corner": corner, "lead": lead, "runner": runner,
            "plot": png, "elapsed": elapsed,
            "evaluations": sum(r.n_evaluations for r in rungs)}


def main(request: str | None = None, params: dict | None = None,
         emit=None) -> int:
    params = params or {}
    out = OUT_ROOT / "sobol-sensitivity"
    out.mkdir(parents=True, exist_ok=True)
    script = make_transcript("sobol sensitivity", emit)
    roster = Roster(emit)
    ledger = ComputeLedger(emit)
    knowledge = KnowledgeBase(emit)

    script.system(request or
                  "Request: apportion the output variance of the lab's "
                  "screens across their published input spreads, and say "
                  "which spread is worth buying down first.")

    # ---------------- Hypothesis ----------------
    script.phase(HYPOTHESIS)
    roster.set(CHIEF_ENGINEER, "framing the study", "working")
    script.engineer(
        "• An envelope says how wide the answer is. "
        "• It never says which input made it wide, so reduction work is "
        "aimed by guesswork. "
        "• Chief Researcher rules on the decomposition before anything runs.")

    roster.set(CHIEF_RESEARCHER, "selecting the method", "working")
    script.researcher(
        "• Variance-based decomposition splits the output variance into the "
        "share each input owns. "
        "• The first-order index is that share alone; the total-effect index "
        "adds every interaction the input takes part in. "
        "• An input whose total index is near zero can be held at nominal "
        "without moving the envelope.",
        citations=CITATIONS)
    script.researcher(
        f"• Estimator: pick-and-freeze over two base matrices plus one "
        f"column swap per input, at a cost of base sample times inputs plus "
        f"two. "
        f"• Admissibility: every Sobol identity must hold on the point "
        f"estimates at the slack the governed physics file states, or the "
        f"run is sampling noise and reports as noise. "
        f"• Two inputs whose intervals overlap stand as unresolved; the "
        f"budget rises until they separate, up to the ceiling the governed "
        f"physics file sets. "
        f"• The spreads are each act's own published spreads, never spreads "
        f"invented for this decomposition.",
        citations=CITATIONS)
    script.researcher(
        "• The indices inherit the fidelity of the path they are measured "
        "on. "
        "• Both paths here are reduced-order screens, so the ranking aims "
        "uncertainty work at those screens and says nothing about a meshed "
        "and solved flow. "
        "• Rejected: ranking by one-at-a-time perturbation, which prices no "
        "interaction at all. "
        "• Deferred to agenda: correlated spreads, a second-order index map, "
        "and the same decomposition through a solved path.")
    if emit:
        emit("agenda.updated", {"entries": AGENDA})
    roster.idle(CHIEF_RESEARCHER)
    script.engineer("On it.")

    # ---------------- Plan ----------------
    script.phase(PLAN)
    gates = _gates()
    cases = [_valve_case(), _airliner_case()]
    capacity = audit(2, memory_per_worker_mb=64)
    if emit:
        emit("audit.completed", capacity.panel())
    script.engineer(capacity.headline(), panel=capacity.panel())
    script.engineer(
        f"• Plan: {len(cases)} cases, each with 2 inputs, opening at the "
        f"approved base sample of {gates['min_base_samples']}. "
        f"• Opening cost per case: "
        f"{gates['min_base_samples'] * 4} evaluations. "
        f"• Every evaluation runs a reduced-order path, so the whole mission "
        f"is seconds of compute.")
    script.numericist(
        "• Each case is seeded once, so the draws, the column swaps and the "
        "bootstrap all replay to the last digit. "
        "• The intervals are percentile bootstrap over the base-sample rows. "
        "• No index is quoted without its interval.")

    # ---------------- Evidence ----------------
    script.phase(EVIDENCE)
    runs = [_run_case(case, script=script, emit=emit, roster=roster,
                      ledger=ledger, out=out, gates=gates) for case in cases]

    # ---------------- Conclusion ----------------
    script.phase(CONCLUSION)
    resolved_runs = [r for r in runs if r["resolved"]]
    summary_rows = []
    for r in runs:
        lead, runner = r["lead"], r["runner"]
        summary_rows.append([
            r["case"]["title"],
            f"{lead[0]} {lead[1] * 100:.0f}%",
            f"{runner[0]} {runner[1] * 100:.0f}%",
            f"{r['result'].n_base}",
            "Measured" if r["resolved"] else "Unresolved at the cap",
        ])
    emit_table(emit, script, role=CHIEF_ENGINEER,
               title="Where the variance sits",
               headers=["Case", "Leading Input", "Runner Up", "Base Sample",
                        "Order"],
               rows=summary_rows, table_id="sobol-summary")

    recommendations = []
    for r in resolved_runs:
        lead, runner = r["lead"], r["runner"]
        ratio = lead[1] / runner[1] if runner[1] > 0 else float("inf")
        action = r["case"]["buy_down"].get(lead[0], "")
        recommendations.append(
            f"{r['case']['title']}: {lead[0]} owns {lead[1] * 100:.0f}% of "
            f"the variance against {runner[1] * 100:.0f}% for {runner[0]}, "
            f"{ratio:.1f} times the share. Spend the next measurement "
            f"effort on {action}.")
    for line in recommendations:
        script.engineer("• " + line.replace(". Spend", ". • Spend"))

    if len(resolved_runs) < len(runs):
        for r in runs:
            if any(r is x for x in resolved_runs):
                continue
            script.engineer(
                f"• {r['case']['title']}: the two shares cannot be told "
                f"apart at this budget. "
                f"• No input is named as the one to buy down. "
                f"• A wider base sample is what that question needs.")

    total_evals = sum(r["evaluations"] for r in runs)
    total_seconds = sum(r["elapsed"] for r in runs)
    script.numericist(
        f"• Measured cost of the whole apportionment: {total_evals} "
        f"evaluations in {total_seconds:.2f} s. "
        f"• The proposal priced this at 6 core-minutes. "
        f"• Every path here is reduced-order, so the measured cost lands "
        f"far under the estimate.")

    verdict = trust(converged=True, solver_backed=False,
                    why="variance shares measured on reduced-order screens; "
                        "each index inherits the fidelity of the path it was "
                        "taken through")
    headline = resolved_runs[0] if resolved_runs else runs[0]
    lead = headline["lead"]
    if emit:
        emit("result.verdict", {
            "quantity": f"Variance share, {headline['case']['output']}",
            "value": f"{lead[1]:.3f}",
            "ci": f"{lead[2][0]:.3f} to {lead[2][1]:.3f}",
            "confidence": "95%",
            "envelope": f"{lead[0]}, base sample "
                        f"{headline['result'].n_base}",
            **verdict})

    channels = uncertainty_channels(
        input_2sigma=None,
        numerical=None,
        model=None,
        input_note="This mission apportions the input channel rather than "
                   "widening it. "
                   "• The share each input owns is the quantity reported, "
                   "with its bootstrap interval.",
        numerical_note="The estimator's own sampling error is carried as the "
                       "bootstrap interval on every index; no index is quoted "
                       "without one.",
        model_note="Pick-and-freeze assumes the inputs are independent. Both "
                   "paths are reduced-order screens, so the shares aim "
                   "uncertainty work at those screens and describe no solved "
                   "flow.")
    if emit:
        emit("uncertainty.channels", channels)

    for r in resolved_runs:
        knowledge.add(
            f"Variance apportionment, {r['case']['title']}: {r['lead'][0]} "
            f"owns {r['lead'][1] * 100:.0f}% of the variance against "
            f"{r['runner'][1] * 100:.0f}% for {r['runner'][0]}, at a base "
            f"sample of {r['result'].n_base}")

    results = []
    for r in runs:
        lead = r["lead"]
        results.append({
            "quantity": f"Variance share, {r['case']['output']}",
            "value": f"{lead[0]} {lead[1]:.3f}",
            "envelope": f"{lead[2][0]:.3f} to {lead[2][1]:.3f} (95%), base "
                        f"sample {r['result'].n_base}",
            **(verdict if r["resolved"] else
               trust(converged=False,
                     why="the leading two intervals overlap at this budget, "
                         "so no order is measured"))})

    report = lab_report(
        title="Variance apportionment across the published input spreads",
        abstract=[
            "Two reduced-order screens were decomposed by variance rather "
            "than propagated, so the envelope each one quotes is now split "
            "into the share every input owns.",
            "The design is pick-and-freeze at a cost of base sample times "
            "inputs plus two, with first-order and total-effect indices and "
            "a percentile bootstrap interval on each.",
            f"{total_evals} evaluations in {total_seconds:.2f} s of measured "
            f"wall time across both cases.",
        ],
        methods=[
            "Pick-and-freeze variance decomposition over two independent "
            "base matrices and one column-swapped matrix per input.",
            "First-order index by the Saltelli 2010 estimator, total-effect "
            "index by the Jansen 1999 estimator, intervals by percentile "
            "bootstrap over the base-sample rows.",
            "Input distributions are each act's own published spreads: the "
            "valve's bounded uniform at a matching 1-sigma, the airliner's "
            "Gaussian.",
            "Admissibility as the Innovation Standard writes it: every Sobol "
            "identity inside the bootstrap interval, and overlapping "
            "intervals reported as unresolved rather than force-ranked.",
        ],
        results=results,
        uncertainty=[
            "Each index carries a 95% percentile bootstrap interval; an "
            "index without its interval is not reported.",
            "Overlapping intervals are an unresolved order, not a close "
            "call: the base sample rises until they separate or the mission "
            "says it could not resolve them.",
            "Pick-and-freeze assumes independent inputs; a case whose "
            "spreads move together needs a different estimator.",
            "Both paths are reduced-order screens. The apportionment aims "
            "uncertainty work at those screens and describes no meshed and "
            "solved flow.",
        ],
        next_investigations=[e["title"] + ": " + e["scope"] for e in AGENDA],
        compute=ledger.as_dict())
    plots = [{"title": f"Variance share per input: {r['case']['title']}",
              "file": Path(r["plot"]).name,
              "url": f"/api/plot/sobol-sensitivity/{Path(r['plot']).name}"}
             for r in runs if r["plot"]]
    if plots:
        report["plots"] = plots
    if emit:
        emit("report.ready", report)

    script.save(out / "transcript.txt")
    roster.all_idle()
    print("Artifacts in", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(request=" ".join(sys.argv[1:]) or None))
