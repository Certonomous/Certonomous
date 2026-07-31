"""Multifidelity fusion of the race ensemble WITH A REAL ERROR BUDGET.

Closes the approved proposal ``r1-multifidelity-propagation``'s remaining
half. Two earlier evidence runs measured what fusion BUYS
(``run_mfmc_evidence.py``, 2026-07-25: rho 0.9967, 150x variance reduction;
``run_reynolds_surrogate_evidence.py``, 2026-07-27: a Reynolds-aware cheap
lane that lifts the race's own fixed-alpha estimand from rho UNDEFINED to
0.9997). Neither budgeted the error. A variance-reduction factor is not an
error bar: MFMC is unbiased for E[high-fidelity], not for E[truth], so the
factor shrinks exactly one term of four and leaves the other three where
they were.

This script measures all four terms on the race act's own estimand and
reports which one dominates after fusion.

THE ENSEMBLE, AND WHAT WAS SILENTLY MISSING FROM IT
---------------------------------------------------
``mission-output/race-study/work/mc`` holds 176 design directories. Only 88
carry a ``result.json``. The other 88 each carry a ``job.json`` and a
``log.vspaero`` whose entire contents are the Windows python-launcher stub
message ("Python was not found; run without arguments to install from the
Microsoft Store") -- they never reached the solver. Their designs are a
SECOND, independent 8-sample Reynolds draw over the same 11-point alpha grid
(sample 0 is RE_NOMINAL exactly in both draws, so 11 of the 176 designs
coincide and the union spans 15 distinct Reynolds samples, 165 distinct
designs). The race act reported on the surviving half and never said the
other half was gone.

``scripts/recover_lost_race_members.py`` re-solved all 88 on this host with
the same ``job.json``, the same worker, and OpenVSP 3.51.1; a control
re-solve of a SURVIVING design (mc-s0a0) reproduced its recorded L/D
bit-identically (18.140687390989), so the recovered lane and the recorded
lane are the same measurement. This script uses the recovered members to
measure -- not impute -- what the dropped members would have contributed,
which is the F6d question ("Convergence gating biases the band toward the
wrong answer", NOT_PASSING_REGISTER.md) asked of a different gate.

THE FOUR TERMS
--------------
1. ESTIMATOR (sampling) error. Shrinks as 1/sqrt(n) and is the ONLY term
   MFMC touches. Reported as the standard error of the fused mean at the
   race lane's own recorded budget.
2. CHEAP-LANE (surrogate) error. Contributes ZERO bias to the MFMC estimate
   for any fixed alpha -- that is the point of a control variate -- and
   enters only through rho. Reported as the held-out RMSE it WOULD carry if
   the anchors were dropped and the ensemble read surrogate-only.
3. MISSING-MEMBER (gating) bias. Measured: the estimand computed on the
   surviving half against the estimand computed on the full recovered
   ensemble.
4. HIGH-FIDELITY MODEL-FORM error. VSPAERO is a vortex-lattice method with
   an empirical viscous-drag estimate; the wing is solved without fuselage,
   tail or nacelle. The lab has no measured band for it -- ``docs/
   UNCERTAINTY.md`` lists "Solver model-form error: cross-fidelity
   disagreement (e.g. VSPAERO panel-method vs higher-fidelity references)"
   under Roadmap, i.e. as a channel that does not exist yet. It is reported
   here as UNQUANTIFIED, by name, and ``uq.combine_expanded`` carries it in
   its ``missing`` list rather than letting the combined number look whole.

Run::

    python scripts/run_mfmc_error_budget.py
"""
from __future__ import annotations

import json
import math
import os
import random
import statistics
import sys
import time
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))
os.environ.setdefault("CHIEF_ENGINEER_WORKDIR", str(SDK / "chief-engineer-runs"))

from chief_engineer import uq                                      # noqa: E402
from chief_engineer.multifidelity import (control_variate_alpha,   # noqa: E402
                                          mfmc_estimate,
                                          optimal_allocation, pearson,
                                          variance_ratio)
from chief_engineer.reynolds_surrogate import (fit_quality,        # noqa: E402
                                               fit_reynolds_surface,
                                               predict_reynolds_surface)
from chief_engineer.vspaero import VspAeroWingApi                  # noqa: E402
from workflows.race_benchmark import RE_NOMINAL, WING              # noqa: E402
from workflows.shape_optimization import _fit_quadratic, _predict  # noqa: E402

ROOT = SDK.parent
RACE_WORK = ROOT / "mission-output" / "race-study" / "work"
RECOVERED = ROOT / "mission-output" / "mfmc-recovery" / "work"
SURROGATE_WORK = ROOT / "mission-output" / "mfmc-recovery" / "surrogate"
OUT_JSON = ROOT / "demo-output" / "website" / "mfmc_error_budget.json"

RE_REF = RE_NOMINAL
TRAIN_ALPHAS = [0.0, 2.5, 5.0, 7.5, 10.0]
TRAIN_RES = [0.70e6, 0.85e6, 1.02e6, 1.15e6, 1.30e6]
VAL_ALPHAS = [1.25, 3.75, 6.25, 8.75]
VAL_RES = [0.775e6, 0.925e6, 1.075e6, 1.225e6]
COST_TIMING_N = 200_000


# --------------------------------------------------------------------------
# Records
# --------------------------------------------------------------------------

def _read(case: Path) -> dict | None:
    result, job = case / "result.json", case / "job.json"
    if not (result.exists() and job.exists()):
        return None
    r = json.loads(result.read_text(encoding="utf-8"))
    j = json.loads(job.read_text(encoding="utf-8"))
    return {"tag": case.name, "alpha": float(j["alpha_start"]),
            "re": float(j["re_cref"]), "l_d": float(r["polar"]["L_D"][0]),
            "seconds": float(r.get("elapsed_s") or 0.0),
            "case": str(case)}


def load_lanes() -> dict:
    surviving = [rec for p in sorted((RACE_WORK / "mc").iterdir())
                 if (rec := _read(p)) is not None]
    recovered = [rec for p in sorted(RECOVERED.iterdir())
                 if p.is_dir() and (rec := _read(p)) is not None]
    anchors = [rec for p in sorted((RACE_WORK / "rom").iterdir())
               if p.name.startswith("rom-anchor")
               and (rec := _read(p)) is not None]
    dropped_no_result = sorted(p.name for p in (RACE_WORK / "mc").iterdir()
                               if not (p / "result.json").exists())
    return {"surviving": surviving, "recovered": recovered,
            "anchors": anchors, "dropped_tags": dropped_no_result}


# --------------------------------------------------------------------------
# The Reynolds-aware cheap lane (rebuilt here, held-out validated)
# --------------------------------------------------------------------------

def solve_grid(alphas, res, subdir):
    api = VspAeroWingApi(SURROGATE_WORK / subdir, reuse_prior=True)
    pts = [{"alpha": a, "re": r, "tag": f"{subdir}-a{a:g}-re{r:.0f}"}
           for a in alphas for r in res]
    designs = [{**WING, "re_cref": p["re"], "alpha_start": p["alpha"],
                "alpha_end": p["alpha"], "alpha_npts": 1,
                "tag_hint": p["tag"]} for p in pts]
    results = api.evaluate_many(designs, max_workers=8)
    return [{**p, "l_d": float(r["polar"]["L_D"][0])}
            for p, r in zip(pts, results) if r is not None]


def build_cheap_lane(mc_all: list[dict]) -> dict:
    train = solve_grid(TRAIN_ALPHAS, TRAIN_RES, "train")
    val = solve_grid(VAL_ALPHAS, VAL_RES, "val")
    recorded = {(round(r["alpha"], 3), round(r["re"], 1)) for r in mc_all}
    fresh = {(round(p["alpha"], 3), round(p["re"], 1)) for p in train + val}
    overlap = recorded & fresh
    if overlap:
        raise AssertionError(f"cheap lane trained on evaluation designs: "
                             f"{sorted(overlap)[:5]}")
    coeff = fit_reynolds_surface([p["alpha"] for p in train],
                                 [p["re"] for p in train],
                                 [p["l_d"] for p in train], RE_REF)
    return {
        "coeff": coeff,
        "train": fit_quality([p["alpha"] for p in train],
                             [p["re"] for p in train],
                             [p["l_d"] for p in train], coeff, RE_REF),
        "val": fit_quality([p["alpha"] for p in val], [p["re"] for p in val],
                           [p["l_d"] for p in val], coeff, RE_REF),
        "n_train": len(train), "n_val": len(val),
        "leakage_check": "PASS: no training or validation design coincides "
                         "with any evaluated race design",
    }


def cheap_cost(coeff) -> float:
    t0 = time.perf_counter()
    acc = 0.0
    for i in range(COST_TIMING_N):
        acc += predict_reynolds_surface(coeff, (i % 101) * 0.1,
                                        RE_REF * (1.0 + (i % 37) * 0.001),
                                        RE_REF)
    assert acc != 0.0
    return max((time.perf_counter() - t0) / COST_TIMING_N, 1e-9)


# --------------------------------------------------------------------------
# The race's own estimand: peak L/D under the Reynolds spread
# --------------------------------------------------------------------------

def peaks(records: list[dict]) -> list[dict]:
    """One peak-L/D point per Reynolds sample (the race's estimand)."""
    by_re: dict[float, list[dict]] = {}
    for r in records:
        by_re.setdefault(round(r["re"], 3), []).append(r)
    return [max(pts, key=lambda p: p["l_d"]) for pts in by_re.values()]


def estimand(records: list[dict]) -> dict:
    pk = peaks(records)
    vals = [p["l_d"] for p in pk]
    n = len(vals)
    sd = statistics.stdev(vals) if n > 1 else 0.0
    return {"n_samples": n, "mean": statistics.fmean(vals),
            "sd": sd, "sem": sd / math.sqrt(n) if n else 0.0,
            "min": min(vals), "max": max(vals),
            "re_values": sorted(round(p["re"], 1) for p in pk),
            "peak_alphas": sorted({p["alpha"] for p in pk})}


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> None:
    lanes = load_lanes()
    surviving, recovered, anchors = (lanes["surviving"], lanes["recovered"],
                                     lanes["anchors"])
    full = surviving + recovered
    print(f"race lane: {len(surviving)} surviving, {len(recovered)} recovered, "
          f"{len(lanes['dropped_tags'])} directories had no result")

    cheap = build_cheap_lane(full)
    coeff = cheap["coeff"]
    print(f"cheap lane: train RMSE {cheap['train']['rmse']:.4f} "
          f"(n={cheap['n_train']}), HELD-OUT val RMSE "
          f"{cheap['val']['rmse']:.4f} (n={cheap['n_val']}), "
          f"val R2 {cheap['val']['r2']:.5f}")

    # ---- fusion on the race's estimand, full recovered ensemble ----------
    pk = peaks(full)
    hi = [p["l_d"] for p in pk]
    lo = [predict_reynolds_surface(coeff, p["alpha"], p["re"], RE_REF)
          for p in pk]
    rho = pearson(hi, lo)
    alpha_cv = control_variate_alpha(hi, lo)
    cost_hi = statistics.fmean(r["seconds"] for r in full if r["seconds"] > 0)
    cost_lo = cheap_cost(coeff)
    budget = len(pk) * cost_hi
    plan = optimal_allocation(rho, cost_hi, cost_lo, budget)

    # The fused estimate: solver anchors at every drawn Reynolds, plus the
    # cheap lane swept over a dense Reynolds population it never solved.
    rng = random.Random(20260731)
    lo_extra = [predict_reynolds_surface(
        coeff, 0.0, max(1e5, rng.gauss(RE_NOMINAL, 0.08 * RE_NOMINAL)), RE_REF)
        for _ in range(plan.n_lo)]
    fused = mfmc_estimate(hi, lo, lo_extra, alpha=alpha_cv)

    # ---- empirical confirmation of the analytic variance ratio ----------
    # Both estimators must aim at the SAME target or the comparison measures
    # a bias, not a variance: the target is the paired-population mean of hi,
    # so the cheap lane's "population" here is the paired lo values, repeated
    # until the paired subset's own weight in mean(lo_all) is negligible.
    rng2 = random.Random(20260731)
    truth = statistics.fmean(hi)
    n_small = 6
    lo_pop = lo * 500
    mc_err, mf_err = [], []
    for _ in range(4000):
        idx = [rng2.randrange(len(hi)) for _ in range(n_small)]
        mc_err.append(statistics.fmean(hi[i] for i in idx) - truth)
        f = mfmc_estimate([hi[i] for i in idx], [lo[i] for i in idx],
                          lo_pop, alpha=alpha_cv)
        mf_err.append(f["estimate"] - truth)
    var_mc = statistics.fmean(e * e for e in mc_err)
    var_mf = statistics.fmean(e * e for e in mf_err)
    replay = {"budget_solves": n_small, "resamples": 4000,
              "empirical_variance_ratio": var_mf / var_mc,
              "analytic_variance_ratio": variance_ratio(rho, cost_hi, cost_lo),
              "rmse_direct": var_mc ** 0.5, "rmse_fused": var_mf ** 0.5,
              "note": "both lanes estimate the same target (the paired "
                      "population mean of the solver lane), so this "
                      "confirms the estimator's VARIANCE. It does not test "
                      "the control-variate shift reported above, which "
                      "deliberately aims at the wider Reynolds population "
                      "the 15 drawn samples represent."}

    # ---- the drawn Reynolds sample, which the shift corrects -------------
    drawn = sorted(round(p["re"], 1) for p in pk)
    re_sem = 0.08 * RE_NOMINAL * math.sqrt(len(drawn) - 1) / len(drawn)
    re_diag = {
        "n_distinct_reynolds": len(drawn),
        "drawn_mean": statistics.fmean(drawn),
        "drawn_sd": statistics.stdev(drawn),
        "population_mean": RE_NOMINAL,
        "population_sigma": 0.08 * RE_NOMINAL,
        "sample_mean_sem": re_sem,
        "sample_mean_z": (statistics.fmean(drawn) - RE_NOMINAL) / re_sem,
        "note": "the ensemble fixes sample 0 at nominal and draws the rest, "
                "so the sample mean has sem sigma*sqrt(n-1)/n",
    }

    # ---- the four error terms -------------------------------------------
    est_full = estimand(full)
    est_surv = estimand(surviving)
    est_rec = estimand(recovered)
    gating_bias = est_surv["mean"] - est_full["mean"]

    se_direct = est_full["sem"]
    se_fused = se_direct * math.sqrt(plan.variance_ratio)

    budget_terms = {
        "estimator_direct_sem": se_direct,
        "estimator_fused_sem": se_fused,
        "cheap_lane_heldout_rmse_if_unanchored": cheap["val"]["rmse"],
        "cheap_lane_bias_contribution": 0.0,
        "missing_member_bias_measured": gating_bias,
        "high_fidelity_model_form": None,
    }
    combined = uq.combine_expanded(
        input_2sigma=2.0 * est_full["sd"],
        numerical_abs=2.0 * se_fused,
        model_abs=None)

    report = {
        "measured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "script": "sdk/scripts/run_mfmc_error_budget.py",
        "solver": "VSPAERO, OpenVSP 3.51.1",
        "ensemble": {
            "surviving_records": len(surviving),
            "recovered_records": len(recovered),
            "recovered_from": str(RECOVERED),
            "dropped_cause": "log.vspaero contains only the Windows "
                             "python-launcher stub message; the solver never "
                             "ran. Cause is identical for all 88 and is "
                             "independent of the design.",
            "control_reproduction": "mc-s0a0 re-solved on this host returned "
                                    "L/D 18.140687390989, bit-identical to "
                                    "the 2026-07-25 record",
            "distinct_reynolds_samples_surviving": est_surv["n_samples"],
            "distinct_reynolds_samples_recovered": est_rec["n_samples"],
            "distinct_reynolds_samples_union": est_full["n_samples"],
        },
        "cheap_lane": {k: v for k, v in cheap.items() if k != "coeff"},
        "cheap_lane_coefficients": coeff,
        "fusion": {
            "estimand": "peak L/D over the drawn chord-Reynolds spread",
            "n_pairs": len(pk), "rho": rho, "control_variate_alpha": alpha_cv,
            "cost_hi_s": cost_hi, "cost_lo_s": cost_lo,
            "cost_ratio": plan.cost_ratio, "budget_s": budget,
            "n_hi": plan.n_hi, "n_lo": plan.n_lo,
            "variance_ratio": plan.variance_ratio,
            "equal_budget_speedup": plan.speedup_equal_error,
            "pays": plan.pays,
            "fused_estimate": fused["estimate"],
            "hi_only_mean": fused["hi_mean"],
            "control_variate_shift": fused["lo_shift"],
        },
        "estimand_surviving_half": est_surv,
        "estimand_recovered_half": est_rec,
        "estimand_full_ensemble": est_full,
        "replay_check": replay,
        "drawn_reynolds": re_diag,
        "error_budget": budget_terms,
        "combined": combined,
    }
    OUT_JSON.write_text(json.dumps(report, indent=1), encoding="utf-8")

    print()
    print(f"ESTIMAND peak L/D, surviving half   : {est_surv['mean']:.5f} "
          f"+/- {est_surv['sem']:.5f} (n={est_surv['n_samples']}), "
          f"sd {est_surv['sd']:.5f}")
    print(f"ESTIMAND peak L/D, recovered half   : {est_rec['mean']:.5f} "
          f"+/- {est_rec['sem']:.5f} (n={est_rec['n_samples']}), "
          f"sd {est_rec['sd']:.5f}")
    print(f"ESTIMAND peak L/D, full ensemble    : {est_full['mean']:.5f} "
          f"+/- {est_full['sem']:.5f} (n={est_full['n_samples']}), "
          f"sd {est_full['sd']:.5f}")
    print(f"MISSING-MEMBER BIAS (surviving - full): {gating_bias:+.5f} "
          f"({gating_bias / est_full['mean']:+.4%})")
    print()
    print(f"FUSION rho {rho:.6f}, cost ratio {plan.cost_ratio:.3e}, "
          f"allocation {plan.n_hi} solves + {plan.n_lo} cheap evals, "
          f"variance ratio {plan.variance_ratio:.6g} "
          f"({plan.speedup_equal_error:.1f}x), pays={plan.pays}")
    print(f"FUSED estimate {fused['estimate']:.5f} vs solver-only mean "
          f"{fused['hi_mean']:.5f} (control-variate shift "
          f"{fused['lo_shift']:+.5f})")
    print()
    print("ERROR BUDGET on peak L/D (absolute, L/D units):")
    print(f"  1 estimator, direct MC at this budget : {se_direct:.5f}")
    print(f"  1 estimator, after fusion             : {se_fused:.5f}")
    print(f"  2 cheap lane, bias into fused estimate: 0.00000 (control "
          f"variate is unbiased for any fixed alpha)")
    print(f"  2 cheap lane, held-out RMSE if the anchors were dropped: "
          f"{cheap['val']['rmse']:.5f}")
    print(f"  3 missing members, MEASURED bias      : "
          f"{abs(gating_bias):.5f}")
    print(f"  4 VSPAERO model form vs truth         : UNQUANTIFIED "
          f"(docs/UNCERTAINTY.md lists it under Roadmap)")
    print(f"  combined over quantified channels     : "
          f"{combined['combined_95']:.5f}; missing: {combined['missing']}")
    print(f"    (input channel, 2 sd of the physical Reynolds spread: "
          f"{2 * est_full['sd']:.5f} -- {2 * est_full['sd'] / combined['combined_95']:.1%} "
          f"of the combined; the fused estimator contributes "
          f"{2 * se_fused / combined['combined_95']:.2%})")
    print()
    print(f"REPLAY CHECK: analytic variance ratio "
          f"{replay['analytic_variance_ratio']:.6g}, empirical "
          f"{replay['empirical_variance_ratio']:.6g} over "
          f"{replay['resamples']} resamples at {replay['budget_solves']} solves")
    print(f"DRAWN REYNOLDS: mean {re_diag['drawn_mean']:.0f} vs nominal "
          f"{RE_NOMINAL:.0f} ({re_diag['sample_mean_z']:+.2f} sigma of the "
          f"sample mean), sd {re_diag['drawn_sd']:.0f} vs population sigma "
          f"{re_diag['population_sigma']:.0f} -- the control-variate shift "
          f"corrects the mean, not the spread")
    print()
    print(f"written: {OUT_JSON}")


if __name__ == "__main__":
    main()
