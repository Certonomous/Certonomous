"""Reynolds-aware reduced-order surrogate: build, validate, and re-measure MFMC.

CONTEXT (baseline measured, not assumed): ``scripts/run_mfmc_evidence.py``
found that the race act's reduced-order surrogate (``workflows.shape_
optimization._fit_quadratic``, four anchor solves all at the ONE nominal
chord Reynolds number) is a quadratic in angle of attack alone. Over the
race's actual estimand -- peak L/D under the Reynolds spread at fixed alpha
-- that surrogate's lane is CONSTANT (lo_sigma 0.0 vs solver sigma 0.1272),
the correlation is UNDEFINED, and MFMC degenerates to plain Monte Carlo:
fusion buys nothing. The full alpha-x-Reynolds paired set does show rho =
0.9967, but that number is an alpha-sweep artifact (alpha spans 0-10 deg and
dominates L/D; Reynolds only perturbs it 8%), not evidence the surrogate
tracks Reynolds -- this script's own baseline reproduction below confirms
that reading with fresh numbers.

SCOPE (Reynolds range, stated plainly): the race's own Monte-Carlo ensemble
draws chord Reynolds ~ N(RE_NOMINAL, 0.08*RE_NOMINAL) with RE_NOMINAL=1.0e6
(``workflows.race_benchmark``), and its 8 recorded draws span [800619,
1091316] -- roughly +/-2.5 sigma either side of nominal, measured from the
recorded records. This script trains and validates the new surrogate over
[0.70e6, 1.30e6] (+/-30%, ~3.75 sigma), a margin around that OBSERVED span so
the correlation study never asks the surrogate to extrapolate. Alpha stays
at the race's own domain, 0-10 deg.

DATA SPLIT (genuine, no leakage into the race's recorded pairing):
  TRAIN: a 5x5 factorial grid, alpha in {0, 2.5, 5, 7.5, 10} deg x Re in
    {0.70, 0.85, 1.00, 1.15, 1.30}e6 -- 25 real VSPAERO solves.
  VALIDATION (held out, never fit on): a 4x4 factorial grid offset by a
    half-step in both dimensions, alpha in {1.25, 3.75, 6.25, 8.75} deg x Re
    in {0.775, 0.925, 1.075, 1.225}e6 -- 16 real VSPAERO solves, interpolated
    between training points, not extrapolated.
  Neither grid coincides with the race's recorded mc-lane pairing (integer
  alpha 0-10 x 8 Gaussian-drawn Re values) or its rom-lane anchors (Re
  pinned exactly at 1.0e6): this script asserts that disjointness before
  reporting anything.

METHOD: quadratic-in-(alpha, Re) response surface (chief_engineer.
reynolds_surrogate), fit by least squares on TRAIN only. Train and
validation RMSE/R^2 reported separately -- a favourable-looking validation
number achieved by fitting on it would be exactly the leakage this script
exists to rule out.

MEASUREMENT: the new surrogate is evaluated at the SAME 88 mc-lane paired
records the baseline used (full-set case) and the SAME fixed-alpha-under-
Reynolds-spread estimand (the race's actual question), through the IDENTICAL
estimator code in ``chief_engineer.multifidelity`` (pearson, control-variate
alpha, optimal_allocation, variance_ratio) and the SAME budget convention
(recorded lane spend at the measured per-solve cost). Old vs new correlation,
old vs new vs direct-MC variance ratio, reported side by side; the verdict is
whatever the numbers say, including "still loses."

Run (2-core cap, matching this repo's convention for solve-heavy evidence
scripts)::

    taskset -c 0-1 python scripts/run_reynolds_surrogate_evidence.py
"""
from __future__ import annotations

import json
import os
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

import random                                                       # noqa: E402

from chief_engineer.lessons import record_learned                 # noqa: E402
from chief_engineer.multifidelity import (control_variate_alpha,  # noqa: E402
                                          mfmc_estimate,
                                          optimal_allocation, pearson)
from chief_engineer.reynolds_surrogate import (fit_quality,        # noqa: E402
                                               fit_reynolds_surface,
                                               predict_reynolds_surface)
from chief_engineer.vspaero import VspAeroWingApi                  # noqa: E402
from workflows import OUT_ROOT                                     # noqa: E402
from workflows.race_benchmark import RE_NOMINAL, WING               # noqa: E402
# Read-only import of the exact quadratic-in-alpha machinery the race lane
# used, and of the baseline evidence's own record loader, so both surrogates
# are measured against literally the same recorded objects.
from workflows.shape_optimization import _fit_quadratic, _predict   # noqa: E402
import run_mfmc_evidence as baseline                                 # noqa: E402

SEED = 20260727
REPLAY_RESAMPLES = 4000

RE_REF = RE_NOMINAL                       # 1.0e6, the race's own nominal Re
TRAIN_ALPHAS = [0.0, 2.5, 5.0, 7.5, 10.0]
# The middle level is deliberately NOT exactly 1.00e6: that value is both the
# race's rom-lane anchor Reynolds and its mc-lane nominal-sample Reynolds, so
# at the shared integer alphas (0, 5, 10) a training point would exactly
# coincide with a recorded race pair. 1.02e6 keeps the grid centered near
# nominal without touching either recorded design (checked by
# ``check_no_leakage`` below, not just asserted here).
TRAIN_RES = [0.70e6, 0.85e6, 1.02e6, 1.15e6, 1.30e6]
VAL_ALPHAS = [1.25, 3.75, 6.25, 8.75]
VAL_RES = [0.775e6, 0.925e6, 1.075e6, 1.225e6]

WORK = SDK.parent / "mission-output" / "reynolds-surrogate" / "work"
PROPOSAL = (SDK.parent / "demo-output" / "website" / "agenda" / "proposals"
            / "r1-multifidelity-propagation.json")
COST_TIMING_N = 200_000


# --------------------------------------------------------------------------
# Real VSPAERO anchors: training grid + held-out validation grid
# --------------------------------------------------------------------------

def _grid(alphas, res, tag_prefix):
    return [{"alpha": a, "re": r, "tag": f"{tag_prefix}-a{a:g}-re{r:.0f}"}
            for a in alphas for r in res]


def _solve_grid(points: list[dict], subdir: str) -> list[dict]:
    api = VspAeroWingApi(WORK / subdir, reuse_prior=True)
    designs = [{**WING, "re_cref": p["re"], "alpha_start": p["alpha"],
               "alpha_end": p["alpha"], "alpha_npts": 1,
               "tag_hint": p["tag"]} for p in points]
    out = []
    started = time.time()

    def on_result(i, result, error):
        if error:
            print(f"  ! solve failed for {points[i]['tag']}: {error}")

    results = api.evaluate_many(designs, max_workers=2, on_result=on_result)
    for p, r in zip(points, results):
        if r is None:
            continue
        out.append({**p, "l_d": float(r["polar"]["L_D"][0]),
                    "seconds": float(r.get("elapsed_s", 0.0))})
    print(f"  {subdir}: {len(out)}/{len(points)} solves "
          f"({time.time() - started:.1f}s wall, 2-core cap)")
    return out


def build_datasets() -> tuple[list[dict], list[dict]]:
    train_points = _grid(TRAIN_ALPHAS, TRAIN_RES, "train")
    val_points = _grid(VAL_ALPHAS, VAL_RES, "val")
    print(f"TRAINING GRID: {len(train_points)} points, alpha in "
          f"{TRAIN_ALPHAS} deg x Re in {[f'{r:.2e}' for r in TRAIN_RES]}")
    train = _solve_grid(train_points, "train")
    print(f"VALIDATION GRID (held out, never fit on): {len(val_points)} "
          f"points, alpha in {VAL_ALPHAS} deg x Re in "
          f"{[f'{r:.2e}' for r in VAL_RES]}")
    val = _solve_grid(val_points, "val")
    return train, val


def check_no_leakage(train: list[dict], val: list[dict],
                     mc: list[dict], rom: list[dict]) -> None:
    """Proactive validation: the new surrogate's training/validation designs
    must not coincide with the race's recorded pairing (that pairing is the
    evaluation set the correlation study measures against)."""
    recorded = {(round(r["alpha"], 3), round(r["re_cref"], 1))
                for r in mc + rom}
    new_points = {(round(p["alpha"], 3), round(p["re"], 1))
                 for p in train + val}
    overlap = recorded & new_points
    if overlap:
        raise AssertionError(f"training/validation design overlaps the "
                             f"race's recorded pairing: {overlap}")
    train_set = {(p["alpha"], p["re"]) for p in train}
    val_set = {(p["alpha"], p["re"]) for p in val}
    if train_set & val_set:
        raise AssertionError("validation grid overlaps the training grid")
    print("LEAKAGE CHECK: training/validation designs disjoint from both "
          "the race's recorded pairing and each other -- PASS")


def check_reynolds_span(mc: list[dict]) -> None:
    observed = [r["re_cref"] for r in mc]
    lo, hi = min(observed), max(observed)
    ok = TRAIN_RES[0] <= lo and hi <= TRAIN_RES[-1]
    print(f"REYNOLDS SPAN CHECK: race's own MC ensemble observed "
          f"[{lo:.0f}, {hi:.0f}]; training/validation domain "
          f"[{TRAIN_RES[0]:.0f}, {TRAIN_RES[-1]:.0f}] "
          f"{'brackets it -- PASS' if ok else 'DOES NOT BRACKET IT -- FAIL'}")
    if not ok:
        raise AssertionError("training domain does not cover the observed "
                             "Reynolds span; the correlation study would be "
                             "extrapolating")


# --------------------------------------------------------------------------
# Fit + train/validation accuracy (never the same points)
# --------------------------------------------------------------------------

def fit_and_validate(train: list[dict], val: list[dict]) -> dict:
    coeff = fit_reynolds_surface([p["alpha"] for p in train],
                                 [p["re"] for p in train],
                                 [p["l_d"] for p in train], RE_REF)
    train_quality = fit_quality([p["alpha"] for p in train],
                               [p["re"] for p in train],
                               [p["l_d"] for p in train], coeff, RE_REF)
    val_quality = fit_quality([p["alpha"] for p in val],
                             [p["re"] for p in val],
                             [p["l_d"] for p in val], coeff, RE_REF)
    overfit = val_quality["rmse"] > 3.0 * train_quality["rmse"]
    return {"coeff": coeff, "train": train_quality, "val": val_quality,
            "overfit_flag": overfit}


def measure_cost_lo_new(coeff: list[float]) -> float:
    t0 = time.perf_counter()
    acc = 0.0
    for i in range(COST_TIMING_N):
        acc += predict_reynolds_surface(coeff, (i % 101) * 0.1,
                                        RE_REF * (1.0 + (i % 37) * 0.001), RE_REF)
    cost = (time.perf_counter() - t0) / COST_TIMING_N
    assert acc != 0.0
    return max(cost, 1e-9)


# --------------------------------------------------------------------------
# Correlation + MFMC, old vs new, same records, same estimator code
# --------------------------------------------------------------------------

def full_set_comparison(mc: list[dict], old_coeff: list[float],
                        new_coeff: list[float], cost_hi: float,
                        cost_lo_old: float, cost_lo_new: float) -> dict:
    hi = [r["l_d"] for r in mc]
    lo_old = [_predict(old_coeff, r["alpha"]) for r in mc]
    lo_new = [predict_reynolds_surface(new_coeff, r["alpha"], r["re_cref"],
                                       RE_REF) for r in mc]
    budget = len(mc) * cost_hi
    rho_old = pearson(hi, lo_old)
    rho_new = pearson(hi, lo_new)
    plan_old = optimal_allocation(rho_old, cost_hi, cost_lo_old, budget)
    plan_new = optimal_allocation(rho_new, cost_hi, cost_lo_new, budget)
    return {"n_pairs": len(mc), "budget_s": budget,
            "rho_old": rho_old, "rho_new": rho_new,
            "variance_ratio_old": plan_old.variance_ratio,
            "variance_ratio_new": plan_new.variance_ratio,
            "plan_new": plan_new}


def _fixed_alpha_subset(mc: list[dict]) -> tuple[float, list[dict]]:
    by_sample: dict[str, list[dict]] = {}
    for r in mc:
        sample = r["tag"].split("a")[0]
        by_sample.setdefault(sample, []).append(r)
    peaks = [max(pts, key=lambda p: p["l_d"]) for pts in by_sample.values()]
    peak_alpha = statistics.mode(p["alpha"] for p in peaks)
    return peak_alpha, [p for p in peaks if p["alpha"] == peak_alpha]


def fixed_alpha_comparison(mc: list[dict], old_coeff: list[float],
                          new_coeff: list[float], cost_hi: float,
                          cost_lo_old: float, cost_lo_new: float) -> dict:
    """The race's OWN estimand: peak L/D under the Reynolds spread at fixed
    alpha. This is the case the baseline found degenerate for the alpha-only
    surrogate; here it is measured for the Reynolds-aware one, on the exact
    same subset, with the exact same estimator code."""
    peak_alpha, at_alpha = _fixed_alpha_subset(mc)
    hi = [p["l_d"] for p in at_alpha]
    lo_old = [_predict(old_coeff, p["alpha"]) for p in at_alpha]
    lo_new = [predict_reynolds_surface(new_coeff, p["alpha"], p["re_cref"],
                                       RE_REF) for p in at_alpha]
    hi_sigma = statistics.pstdev(hi)
    lo_sigma_old = statistics.pstdev(lo_old)
    lo_sigma_new = statistics.pstdev(lo_new)
    try:
        rho_old = pearson(hi, lo_old)
        degenerate_old = False
    except ValueError:
        rho_old = None
        degenerate_old = True
    rho_new = pearson(hi, lo_new)     # new surrogate moves with Re: expect defined
    budget = len(at_alpha) * cost_hi  # this estimand's own recorded spend
    plan_new = optimal_allocation(rho_new, cost_hi, cost_lo_new, budget)
    return {"peak_alpha_deg": peak_alpha, "n_samples": len(at_alpha),
            "hi_sigma": hi_sigma,
            "lo_sigma_old": lo_sigma_old, "lo_sigma_new": lo_sigma_new,
            "rho_old": rho_old, "degenerate_old": degenerate_old,
            "rho_new": rho_new, "budget_s": budget,
            "variance_ratio_new": plan_new.variance_ratio,
            "pays_new": plan_new.pays, "plan_new": plan_new}


# --------------------------------------------------------------------------
# Empirical confirmation: resampled small-budget MC vs MFMC against the
# analytic variance ratio, same technique the baseline evidence used
# (``run_mfmc_evidence.replay_check``), generalized to accept any hi/lo pair
# so it covers both the full-set case and the fixed-alpha estimand.
# --------------------------------------------------------------------------

def replay_check(hi: list[float], lo: list[float], alpha: float,
                 analytic_ratio: float, budget_solves: int) -> dict:
    truth = statistics.fmean(hi)
    rng = random.Random(SEED)
    n = min(budget_solves, len(hi))
    mc_errs, mf_errs = [], []
    for _ in range(REPLAY_RESAMPLES):
        rows = [rng.randrange(len(hi)) for _ in range(n)]
        mc_errs.append(statistics.fmean(hi[r] for r in rows) - truth)
        fused = mfmc_estimate([hi[r] for r in rows], [lo[r] for r in rows],
                              list(lo), alpha=alpha)
        mf_errs.append(fused["estimate"] - truth)
    var_mc = statistics.fmean(e * e for e in mc_errs)
    var_mf = statistics.fmean(e * e for e in mf_errs)
    return {"budget_solves": n, "resamples": REPLAY_RESAMPLES,
            "empirical_ratio": var_mf / var_mc, "analytic_ratio": analytic_ratio,
            "rmse_mc": var_mc ** 0.5, "rmse_mfmc": var_mf ** 0.5}


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------

def main() -> int:
    mc, rom = baseline.load_records()
    old_coeff, cost_lo_old = baseline.fit_surrogate(rom)
    cost_hi = sum(r["seconds"] for r in mc) / len(mc)

    train, val = build_datasets()
    check_no_leakage(train, val, mc, rom)
    check_reynolds_span(mc)

    fit = fit_and_validate(train, val)
    new_coeff = fit["coeff"]
    cost_lo_new = measure_cost_lo_new(new_coeff)

    print("\nBASELINE SURROGATE: quadratic in alpha only "
          f"(coefficients {['%.4g' % c for c in old_coeff]}, 4 anchors all "
          f"at Re={RE_NOMINAL:.0f})")
    print(f"NEW SURROGATE: quadratic in (alpha, Re/{RE_REF:.0f}) "
          f"(coefficients {['%.4g' % c for c in new_coeff]}, "
          f"{len(train)} training anchors)")
    print(f"  TRAIN  n={fit['train']['n']}  rmse={fit['train']['rmse']:.4f} "
          f"L/D  r2={fit['train']['r2']:.5f}  "
          f"max|err|={fit['train']['max_abs_error']:.4f}")
    print(f"  VALID  n={fit['val']['n']}  rmse={fit['val']['rmse']:.4f} "
          f"L/D  r2={fit['val']['r2']:.5f}  "
          f"max|err|={fit['val']['max_abs_error']:.4f}")
    print(f"  OVERFIT CHECK: validation rmse "
          f"{'>' if fit['overfit_flag'] else '<='} 3x train rmse -- "
          f"{'OVERFIT FLAGGED' if fit['overfit_flag'] else 'no overfit flagged'}")

    full = full_set_comparison(mc, old_coeff, new_coeff, cost_hi,
                               cost_lo_old, cost_lo_new)
    hi_full = [r["l_d"] for r in mc]
    lo_full_new = [predict_reynolds_surface(new_coeff, r["alpha"], r["re_cref"],
                                            RE_REF) for r in mc]
    alpha_full_new = control_variate_alpha(hi_full, lo_full_new)
    replay_full = replay_check(hi_full, lo_full_new, alpha_full_new,
                               full["variance_ratio_new"], budget_solves=10)
    print(f"\nFULL PAIRED SET ({full['n_pairs']} designs, alpha x Reynolds "
          f"grid, same records baseline used):")
    print(f"  correlation      old {full['rho_old']:.4f}  ->  new "
          f"{full['rho_new']:.4f}")
    print(f"  variance ratio   old {full['variance_ratio_old']:.5f} "
          f"({1/full['variance_ratio_old']:.1f}x)  ->  new "
          f"{full['variance_ratio_new']:.5f} "
          f"({1/full['variance_ratio_new']:.1f}x)  vs direct MC ratio 1.0")
    print(f"  empirical replay (new) {replay_full['empirical_ratio']:.5f} "
          f"vs analytic {replay_full['analytic_ratio']:.5f} "
          f"({replay_full['resamples']} resamples, "
          f"{replay_full['budget_solves']}-solve budget)")

    fixed = fixed_alpha_comparison(mc, old_coeff, new_coeff, cost_hi,
                                   cost_lo_old, cost_lo_new)
    peak_alpha_r, at_alpha_r = _fixed_alpha_subset(mc)
    hi_fixed = [p["l_d"] for p in at_alpha_r]
    lo_fixed_new = [predict_reynolds_surface(new_coeff, p["alpha"], p["re_cref"],
                                             RE_REF) for p in at_alpha_r]
    alpha_fixed_new = control_variate_alpha(hi_fixed, lo_fixed_new)
    replay_fixed = replay_check(hi_fixed, lo_fixed_new, alpha_fixed_new,
                                fixed["variance_ratio_new"],
                                budget_solves=min(3, len(hi_fixed) - 1))
    print(f"\nFIXED-ALPHA ESTIMAND (the race's actual question -- peak L/D "
          f"under the Reynolds spread at alpha={fixed['peak_alpha_deg']:g} "
          f"deg, {fixed['n_samples']} samples):")
    print(f"  solver sigma     {fixed['hi_sigma']:.4f}")
    print(f"  surrogate sigma  old {fixed['lo_sigma_old']:.2e}  ->  new "
          f"{fixed['lo_sigma_new']:.4f}")
    print(f"  correlation      old "
          f"{'undefined (constant surrogate)' if fixed['degenerate_old'] else format(fixed['rho_old'], '.4f')}"
          f"  ->  new {fixed['rho_new']:.4f}")
    print(f"  variance ratio   old N/A (no fusion possible; equals direct "
          f"MC, ratio 1.0)  ->  new {fixed['variance_ratio_new']:.5f} "
          f"({1/fixed['variance_ratio_new']:.2f}x)")
    print(f"  empirical replay (new) {replay_fixed['empirical_ratio']:.5f} "
          f"vs analytic {replay_fixed['analytic_ratio']:.5f} "
          f"({replay_fixed['resamples']} resamples, "
          f"{replay_fixed['budget_solves']}-solve budget, population "
          f"{len(hi_fixed)})")
    mfmc_now_wins = fixed["pays_new"] and fixed["variance_ratio_new"] < 1.0
    verdict = (
        f"For the race's actual estimand (peak L/D under the Reynolds "
        f"spread at fixed alpha), the Reynolds-aware surrogate moves the "
        f"correlation from UNDEFINED (constant lane) to "
        f"{fixed['rho_new']:.4f}, and MFMC "
        + (f"NOW WINS: variance ratio {fixed['variance_ratio_new']:.4f} "
           f"({1/fixed['variance_ratio_new']:.2f}x vs the direct approach) "
           f"at the estimand's own {fixed['budget_s']:.0f} s budget."
           if mfmc_now_wins else
           f"still does NOT beat the direct approach at this estimand: "
           f"variance ratio {fixed['variance_ratio_new']:.4f} "
           f"({'>' if fixed['variance_ratio_new'] >= 1 else '<'} 1), "
           f"correlation {fixed['rho_new']:.4f} is "
           f"{'too weak' if not fixed['pays_new'] else 'borderline'} given "
           f"the measured cost ratio.")
        + f" On the full alpha x Reynolds paired set the correlation moved "
        f"from {full['rho_old']:.4f} to {full['rho_new']:.4f} and the "
        f"variance ratio from {full['variance_ratio_old']:.5f} to "
        f"{full['variance_ratio_new']:.5f} "
        f"({1/full['variance_ratio_new']:.1f}x vs direct MC).")
    print("\nVERDICT:", verdict)

    evidence = {
        "measured_at": date.today().isoformat(),
        "script": "sdk/scripts/run_reynolds_surrogate_evidence.py",
        "reynolds_range": {"train_val_domain_re": [TRAIN_RES[0], TRAIN_RES[-1]],
                           "observed_race_span_re": [min(r["re_cref"] for r in mc),
                                                     max(r["re_cref"] for r in mc)],
                           "re_ref": RE_REF},
        "data_split": {"train_n": len(train), "val_n": len(val),
                       "train_alphas": TRAIN_ALPHAS, "train_res": TRAIN_RES,
                       "val_alphas": VAL_ALPHAS, "val_res": VAL_RES},
        "surrogate_accuracy": {"train": fit["train"], "val": fit["val"],
                              "overfit_flag": fit["overfit_flag"]},
        "full_set_case": {"n_pairs": full["n_pairs"],
                         "rho_old": round(full["rho_old"], 6),
                         "rho_new": round(full["rho_new"], 6),
                         "variance_ratio_old": full["variance_ratio_old"],
                         "variance_ratio_new": full["variance_ratio_new"],
                         "variance_ratio_new_empirical": replay_full["empirical_ratio"]},
        "fixed_alpha_estimand": {
            "peak_alpha_deg": fixed["peak_alpha_deg"],
            "n_samples": fixed["n_samples"],
            "hi_sigma": round(fixed["hi_sigma"], 4),
            "lo_sigma_old": fixed["lo_sigma_old"],
            "lo_sigma_new": round(fixed["lo_sigma_new"], 6),
            "rho_old": fixed["rho_old"], "degenerate_old": fixed["degenerate_old"],
            "rho_new": round(fixed["rho_new"], 6),
            "variance_ratio_new": fixed["variance_ratio_new"],
            "variance_ratio_new_empirical": replay_fixed["empirical_ratio"],
            "pays_new": fixed["pays_new"],
            "mfmc_now_wins": mfmc_now_wins,
        },
        "verdict": verdict,
    }
    out_path = SDK.parent / "demo-output" / "website" / "reynolds_surrogate_evidence.json"
    out_path.write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(f"\nevidence written: {out_path}")

    if PROPOSAL.exists():
        data = json.loads(PROPOSAL.read_text(encoding="utf-8"))
        data["reynolds_aware_evidence"] = evidence
        PROPOSAL.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"proposal updated (additive field 'reynolds_aware_evidence'): "
              f"{PROPOSAL}")

    record_learned(
        "r1-reynolds-aware-surrogate",
        f"Replaced the race act's alpha-only reduced-order surrogate with a "
        f"quadratic-in-(alpha, Re) surface trained on {len(train)} real "
        f"VSPAERO anchors over Re in [{TRAIN_RES[0]:.2e}, {TRAIN_RES[-1]:.2e}] "
        f"(the race's own 8%-sigma ensemble observed [{min(r['re_cref'] for r in mc):.2e}, "
        f"{max(r['re_cref'] for r in mc):.2e}]), validated on {len(val)} held-out "
        f"points (train rmse {fit['train']['rmse']:.4f}, val rmse "
        f"{fit['val']['rmse']:.4f} L/D). On the race's actual fixed-alpha "
        f"Reynolds-spread estimand the correlation moved from undefined to "
        f"{fixed['rho_new']:.4f} and MFMC "
        f"{'now beats the direct approach' if mfmc_now_wins else 'still does not beat the direct approach'} "
        f"there (variance ratio {fixed['variance_ratio_new']:.4f}). On the "
        f"full alpha x Reynolds set correlation moved "
        f"{full['rho_old']:.4f} -> {full['rho_new']:.4f}.")
    print("lesson recorded: r1-reynolds-aware-surrogate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
