"""Offline evidence for multifidelity Monte Carlo (Innovation Standard).

Stage-2 evidence run for the approved proposal ``r1-multifidelity-propagation``:
the pure MFMC math in ``chief_engineer.multifidelity`` is exercised on the
race act's REAL paired records — no new solve anywhere. The race left behind,
in ``mission-output/race-study/work``, every Monte-Carlo lane VSPAERO solve
(design = angle of attack x drawn Reynolds, with measured wall seconds) and
the reduced-order lane's anchor solves; the recorded anchors refit the same
quadratic response surface the race used (coefficients cross-checked against
the stored race summary). That surface, evaluated at each solved design's
alpha, is the low-fidelity lane; the recorded VSPAERO result is the
high-fidelity lane; the pairing the race discarded is the evidence.

Measured here, honestly:
1. The ROM-solver correlation over the full paired set, the control-variate
   coefficient, the measured cost ratio, the MFMC optimal allocation at the
   race's own recorded budget, and the analytic variance reduction vs
   single-fidelity MC at equal budget.
2. An EMPIRICAL replay check on the same records: resampled small-budget MC
   vs MFMC estimates of the paired-population mean, so the analytic variance
   ratio is confirmed against data rather than asserted.
3. The estimand the race actually asked about (peak L/D under the Reynolds
   spread at fixed alpha): the recorded surrogate is a function of alpha
   only, so at fixed alpha its lane is CONSTANT, the correlation is
   undefined, and MFMC degenerates to plain MC — fusion buys nothing for
   that question with this surrogate. Stated with the numbers, not hidden.

    python scripts/run_mfmc_evidence.py
"""
from __future__ import annotations

import json
import os
import random
import statistics
import sys
import time
from datetime import date
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))
os.environ.setdefault("CHIEF_ENGINEER_WORKDIR", str(SDK / "chief-engineer-runs"))
os.environ.setdefault("CERTONOMOUS_SWEEP_PACE_MS", "0")

from chief_engineer.lessons import record_learned                # noqa: E402
from chief_engineer.multifidelity import (control_variate_alpha,  # noqa: E402
                                          mfmc_estimate,
                                          optimal_allocation,
                                          pearson,
                                          variance_ratio)
# Read-only import of the exact quadratic-fit machinery the race lane used.
from workflows.shape_optimization import _fit_quadratic, _predict  # noqa: E402

RACE_WORK = SDK.parent / "mission-output" / "race-study" / "work"
RACE_SUMMARY = (SDK.parent / "demo-output" / "website" / "race"
                / "pass1" / "race.json")
PROPOSAL = (SDK.parent / "demo-output" / "website" / "agenda" / "proposals"
            / "r1-multifidelity-propagation.json")
SEED = 20260725
REPLAY_BUDGET_SOLVES = 10       # small-budget replay: ten solves' worth
REPLAY_RESAMPLES = 4000


# --------------------------------------------------------------------------
# The recorded artifacts
# --------------------------------------------------------------------------

def load_records() -> tuple[list[dict], list[dict]]:
    """Every completed solve in the race work tree: the MC lane's paired
    designs and the ROM lane's anchors. Retry stubs (``-r`` directories that
    never ran) are skipped because they hold no result."""
    def read_dir(p: Path) -> dict | None:
        result = p / "result.json"
        job = p / "job.json"
        if not (result.exists() and job.exists()):
            return None
        r = json.loads(result.read_text(encoding="utf-8"))
        j = json.loads(job.read_text(encoding="utf-8"))
        return {"tag": p.name, "alpha": float(j["alpha_start"]),
                "re_cref": float(j["re_cref"]),
                "l_d": float(r["polar"]["L_D"][0]),
                "seconds": float(r["elapsed_s"])}

    mc = [rec for p in sorted((RACE_WORK / "mc").iterdir())
          if (rec := read_dir(p)) is not None]
    rom = [rec for p in sorted((RACE_WORK / "rom").iterdir())
           if (rec := read_dir(p)) is not None]
    if not mc or not rom:
        raise SystemExit(f"race records not found under {RACE_WORK}")
    return mc, rom


def fit_surrogate(rom: list[dict]) -> tuple[list[float], float]:
    """Refit the race's quadratic from the recorded anchor solves and return
    (coefficients, per-evaluation cost in seconds, measured here)."""
    anchors = [r for r in rom if r["tag"].startswith("rom-anchor")]
    coeff = _fit_quadratic([r["alpha"] for r in anchors],
                           [r["l_d"] for r in anchors])
    # Measure the cheap lane's cost the same way the race measured the
    # solver's: wall-clock it, on this machine, over enough calls to resolve.
    n = 200_000
    t0 = time.perf_counter()
    acc = 0.0
    for i in range(n):
        acc += _predict(coeff, (i % 101) * 0.1)
    cost_lo = (time.perf_counter() - t0) / n
    assert acc != 0.0
    return coeff, max(cost_lo, 1e-9)


# --------------------------------------------------------------------------
# The measurements
# --------------------------------------------------------------------------

def full_set_case(mc: list[dict], coeff: list[float],
                  cost_lo: float) -> dict:
    hi = [r["l_d"] for r in mc]
    lo = [_predict(coeff, r["alpha"]) for r in mc]
    cost_hi = sum(r["seconds"] for r in mc) / len(mc)
    rho = pearson(hi, lo)
    alpha = control_variate_alpha(hi, lo)
    budget = len(mc) * cost_hi          # the MC lane's own recorded spend
    plan = optimal_allocation(rho, cost_hi, cost_lo, budget)
    return {"n_pairs": len(mc), "rho": rho, "alpha": alpha,
            "cost_hi_s": cost_hi, "cost_lo_s": cost_lo, "plan": plan}


def replay_check(mc: list[dict], coeff: list[float], alpha: float,
                 analytic_ratio: float) -> dict:
    """Empirical confirmation on the records themselves: estimate the
    paired-population mean from a small budget many times, MC vs MFMC, and
    compare the measured variance ratio with the analytic one. The cheap
    lane's cost is negligible at this cost ratio, so MFMC spends its whole
    budget on solves minus one bookkeeping margin, and sweeps the surrogate
    over the entire population for volume."""
    hi = [r["l_d"] for r in mc]
    lo = [_predict(coeff, r["alpha"]) for r in mc]
    truth = statistics.fmean(hi)
    rng = random.Random(SEED)
    n = REPLAY_BUDGET_SOLVES
    mc_errs, mf_errs = [], []
    for _ in range(REPLAY_RESAMPLES):
        rows = [rng.randrange(len(hi)) for _ in range(n)]
        mc_errs.append(statistics.fmean(hi[r] for r in rows) - truth)
        fused = mfmc_estimate([hi[r] for r in rows], [lo[r] for r in rows],
                              [v for i, v in enumerate(lo)], alpha=alpha)
        mf_errs.append(fused["estimate"] - truth)
    var_mc = statistics.fmean(e * e for e in mc_errs)
    var_mf = statistics.fmean(e * e for e in mf_errs)
    return {"budget_solves": n, "resamples": REPLAY_RESAMPLES,
            "empirical_ratio": var_mf / var_mc,
            "analytic_ratio": analytic_ratio,
            "rmse_mc": var_mc ** 0.5, "rmse_mfmc": var_mf ** 0.5}


def fixed_alpha_case(mc: list[dict], coeff: list[float]) -> dict:
    """The race's own estimand: peak L/D under the Reynolds spread. Every
    recorded peak sits at the same alpha, where the alpha-only surrogate is
    constant — the pairing carries no Reynolds information at all."""
    by_sample: dict[str, list[dict]] = {}
    for r in mc:
        sample = r["tag"].split("a")[0]          # "mc-s0", "mc-s1", ...
        by_sample.setdefault(sample, []).append(r)
    peaks = [max(pts, key=lambda p: p["l_d"]) for pts in by_sample.values()]
    peak_alpha = statistics.mode(p["alpha"] for p in peaks)
    at_alpha = [p for p in peaks if p["alpha"] == peak_alpha]
    hi = [p["l_d"] for p in at_alpha]
    lo = [_predict(coeff, p["alpha"]) for p in at_alpha]
    try:
        rho = pearson(hi, lo)
        degenerate = False
    except ValueError:
        rho = None
        degenerate = True
    return {"n_samples": len(hi), "peak_alpha": peak_alpha,
            "hi_sigma": statistics.pstdev(hi),
            "lo_sigma": statistics.pstdev(lo),
            "rho": rho, "degenerate": degenerate}


# --------------------------------------------------------------------------
# Reporting, proposal update, lessons
# --------------------------------------------------------------------------

def update_proposal(full: dict, replay: dict, fixed: dict,
                    verdict: str) -> None:
    plan = full["plan"]
    data = json.loads(PROPOSAL.read_text(encoding="utf-8"))
    sentence = (
        f" Offline evidence measured {date.today().isoformat()} on the race "
        f"act's recorded pairs: correlation {full['rho']:.4f} over "
        f"{full['n_pairs']} matched design evaluations, measured cost ratio "
        f"{plan.cost_ratio:.2e}, optimal allocation {plan.n_hi} solves + "
        f"{plan.n_lo} surrogate evaluations at the lane's own budget, "
        f"variance reduction factor {1.0 / plan.variance_ratio:.1f}x vs "
        f"single-fidelity MC at equal cost (empirical replay "
        f"{1.0 / replay['empirical_ratio']:.1f}x); for the race's actual "
        f"fixed-alpha Reynolds-spread estimand the alpha-only surrogate is "
        f"constant and fusion buys nothing — a Reynolds-aware cheap model "
        f"is the named prerequisite.")
    marker = " Offline evidence measured"
    base = data["rationale"].split(marker)[0]
    data["rationale"] = base + sentence
    # The agenda owns `status` (it changes only when the owner clicks), so
    # the standard's stage lives in its own field alongside the evidence.
    data["evidence_stage"] = "offline-evidence-measured"
    data["evidence"] = {
        "measured_at": date.today().isoformat(),
        "standard_stage": "Stage 2 - offline evidence on a benchmark",
        "script": "sdk/scripts/run_mfmc_evidence.py",
        "paired_records": full["n_pairs"],
        "rho": round(full["rho"], 6),
        "control_variate_alpha": round(full["alpha"], 6),
        "cost_hi_s": round(full["cost_hi_s"], 3),
        "cost_lo_s": full["cost_lo_s"],
        "cost_ratio": round(plan.cost_ratio, 1),
        "budget_s": round(plan.budget, 1),
        "allocation": {"n_hi": plan.n_hi, "n_lo": plan.n_lo,
                       "r_optimal": round(plan.r_optimal, 1)},
        "variance_ratio_analytic": plan.variance_ratio,
        "variance_ratio_empirical": replay["empirical_ratio"],
        "equal_budget_speedup": round(1.0 / plan.variance_ratio, 1),
        "fixed_alpha_estimand": {
            "peak_alpha_deg": fixed["peak_alpha"],
            "hi_sigma": round(fixed["hi_sigma"], 4),
            "lo_sigma": round(fixed["lo_sigma"], 6),
            "rho": fixed["rho"],
            "degenerate": fixed["degenerate"],
        },
        "verdict": verdict,
    }
    PROPOSAL.write_text(json.dumps(data, indent=2), encoding="utf-8")


def main() -> int:
    mc, rom = load_records()
    coeff, cost_lo = fit_surrogate(rom)
    if RACE_SUMMARY.exists():
        stored = json.loads(RACE_SUMMARY.read_text(encoding="utf-8"))
        stored_coeff = stored.get("rom", {}).get("coefficients")
        if stored_coeff:
            drift = max(abs(a - b) for a, b in zip(coeff, stored_coeff))
            print(f"surrogate refit cross-check vs stored race summary: "
                  f"max coefficient drift {drift:.2e}")

    full = full_set_case(mc, coeff, cost_lo)
    plan = full["plan"]
    replay = replay_check(mc, coeff, full["alpha"], plan.variance_ratio)
    fixed = fixed_alpha_case(mc, coeff)

    print(f"PAIRED RECORDS: {full['n_pairs']} designs solved in both lanes "
          f"(alpha x Reynolds grid), surrogate = race quadratic in alpha")
    print(f"  correlation rho          {full['rho']:.4f}")
    print(f"  control-variate alpha    {full['alpha']:.4f}")
    print(f"  measured costs           solve {full['cost_hi_s']:.2f} s, "
          f"surrogate {cost_lo:.2e} s  (ratio {plan.cost_ratio:.2e})")
    print(f"  optimal allocation       {plan.n_hi} solves + {plan.n_lo} "
          f"surrogate evals at the recorded {plan.budget:.0f} s budget "
          f"(r* = {plan.r_optimal:.0f})")
    print(f"  variance ratio (MFMC/MC) {plan.variance_ratio:.4f} analytic, "
          f"{replay['empirical_ratio']:.4f} empirical replay "
          f"({replay['resamples']} resamples at {replay['budget_solves']} "
          f"solves' budget)")
    print(f"  equal-budget speedup     {1.0 / plan.variance_ratio:.1f}x "
          f"analytic, {1.0 / replay['empirical_ratio']:.1f}x empirical")
    print(f"FIXED-ALPHA ESTIMAND (the race's question, peak at alpha "
          f"{fixed['peak_alpha']:g} deg over the Reynolds spread):")
    print(f"  solver-lane sigma {fixed['hi_sigma']:.4f}, surrogate-lane "
          f"sigma {fixed['lo_sigma']:.2e} over {fixed['n_samples']} samples "
          f"-> correlation "
          f"{'undefined (constant surrogate)' if fixed['degenerate'] else format(fixed['rho'], '.4f')}")

    speed = 1.0 / plan.variance_ratio
    verdict = (
        f"Split verdict. For estimands the surrogate tracks (anything that "
        f"varies with alpha, e.g. the sweep-mean L/D), MFMC at the MC "
        f"lane's own {plan.budget:.0f} s budget would have cut estimator "
        f"variance by {speed:.1f}x (rho {full['rho']:.4f}, cost ratio "
        f"{plan.cost_ratio:.0e}) — equivalently, matched the MC lane's "
        f"error using roughly {plan.variance_ratio:.0%} of its budget. For "
        f"the question the race actually asked — peak L/D under the "
        f"Reynolds spread at fixed alpha — the recorded surrogate carries "
        f"no Reynolds dependence, its lane is constant across the ensemble, "
        f"and MFMC would NOT have beaten the race's approach at any budget: "
        f"fusion needs a cheap model that moves with the uncertain input.")
    print("VERDICT:", verdict)

    update_proposal(full, replay, fixed, verdict)
    print(f"proposal updated: {PROPOSAL}")

    record_learned(
        "r1-multifidelity-propagation",
        f"MFMC offline evidence from the race act's own discarded pairing "
        f"({full['n_pairs']} designs with both a surrogate value and a "
        f"VSPAERO solve, measured costs {full['cost_hi_s']:.1f} s vs "
        f"{cost_lo:.0e} s): correlation {full['rho']:.4f}, optimal "
        f"allocation {plan.n_hi} solves + {plan.n_lo} surrogate sweeps, "
        f"variance reduction {speed:.1f}x at equal budget, confirmed "
        f"empirically at {1.0 / replay['empirical_ratio']:.1f}x by "
        f"replaying small-budget estimates over the real records. The "
        f"pairing a race produces is estimator fuel, not a spent artifact.")
    record_learned(
        "r1-multifidelity-estimand-match",
        f"MFMC's gain is estimand-specific: the race surrogate is quadratic "
        f"in alpha only, so at the fixed peak alpha its lane is constant "
        f"(sigma {fixed['lo_sigma']:.0e} vs solver sigma "
        f"{fixed['hi_sigma']:.3f}), correlation is undefined, and fusion "
        f"buys exactly nothing for the Reynolds-spread question the race "
        f"asked. Before proposing fusion, check that the cheap model "
        f"actually varies with the uncertain input; otherwise the measured "
        f"rho is an alpha-sweep artifact, not usable correlation.")
    print("lessons recorded: r1-multifidelity-propagation, "
          "r1-multifidelity-estimand-match")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
