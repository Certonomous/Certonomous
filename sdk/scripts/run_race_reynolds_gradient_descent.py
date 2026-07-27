"""Gradient-driven design optimization on the race act's ROM lane, extended
into the newly-available Reynolds dimension.

BASELINE (measured before this script existed, not touched here): the race
act's reduced-order lane (``workflows.race_benchmark.run_rom_path``, reusing
``workflows.shape_optimization._fit_quadratic``/``_predict``) fits L/D as a
quadratic in angle of attack ALONE -- its four anchors are all solved at the
one nominal chord Reynolds (``RE_NOMINAL`` = 1.0e6). The recorded pass2 run
(``demo-output/website/race/pass2/race.json``) converged to alpha* = 0.0 deg
(the alpha lower bound), predicted L/D 18.2247, confirmed by one real VSPAERO
solve at L/D 18.1407 (surrogate error 0.084). Reynolds was never a design
variable there -- it was pinned at the one nominal value throughout.

WHAT'S NEW: commit 069cf13 added ``chief_engineer.reynolds_surrogate``, a
quadratic-in-(alpha, Re) response surface trained on 25 real VSPAERO anchors
and validated on 16 held-out points (train r2 0.994, val r2 0.989), valid over
Re in [0.70e6, 1.30e6]. This is the first time Re has been available to an
optimizer here.

THIS SCRIPT'S OPTIMIZATION PROBLEM:
  objective   : maximise predicted L/D(alpha, Re) on the NACA 4412 finite wing
  design vars : alpha in [0, 10] deg (the race's own alpha domain)
                Re    in [0.70e6, 1.30e6] (the surrogate's validated domain,
                         which brackets the race's own observed sampled span
                         [800619, 1091316])
  constraints : box bounds only; the confirmation solve must return a finite
                polar (no solver failure) to count
  method      : real (analytic) gradient of the fitted quadratic surface,
                projected gradient ASCENT (maximising) in normalized
                coordinates, starting at the race ROM lane's own converged
                design (alpha=0 deg, Re=1.0e6) -- i.e. this walks the existing
                converged answer further, along the one axis that just became
                available.

Every anchor solve is read from the cached VSPAERO results already on disk
from commit 069cf13's evidence run (``mission-output/reynolds-surrogate/work``,
``reuse_prior=True`` -- identical cache-reuse contract used everywhere else in
this codebase). The BASELINE confirmation and the CONVERGED-DESIGN
confirmation are both solved FRESH here (``reuse_prior=False``) so both
numbers come from this run, on this machine, back to back.

Run (2-core cap)::

    taskset -c 0-1 python scripts/run_race_reynolds_gradient_descent.py
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

SDK = Path(__file__).resolve().parents[1]
if str(SDK) not in sys.path:
    sys.path.insert(0, str(SDK))
os.environ.setdefault("CHIEF_ENGINEER_WORKDIR", str(SDK / "chief-engineer-runs"))

from chief_engineer.reynolds_surrogate import (fit_quality,            # noqa: E402
                                               fit_reynolds_surface,
                                               predict_reynolds_surface)
from chief_engineer.vspaero import VspAeroWingApi                      # noqa: E402
from workflows.race_benchmark import RE_NOMINAL, WING                   # noqa: E402

RE_REF = RE_NOMINAL  # 1.0e6

# Identical training/validation grid to commit 069cf13's evidence run, so the
# fitted surface here is exactly reproducible from the same cached anchors.
TRAIN_ALPHAS = [0.0, 2.5, 5.0, 7.5, 10.0]
TRAIN_RES = [0.70e6, 0.85e6, 1.02e6, 1.15e6, 1.30e6]
VAL_ALPHAS = [1.25, 3.75, 6.25, 8.75]
VAL_RES = [0.775e6, 0.925e6, 1.075e6, 1.225e6]

WORK = SDK.parent / "mission-output" / "reynolds-surrogate" / "work"
# Raw solver case directories (STL/VSP3/polar files) are working state, not a
# publishable artifact -- they live under mission-output like every other
# solve in this repo (gitignored). Only the distilled JSON result below is
# written under demo-output/website.
CONFIRM_WORK = SDK.parent / "mission-output" / "race-reynolds-gradient" / "confirm"
OUT = SDK.parent / "demo-output" / "website" / "race-reynolds-gradient"

ALPHA_LO, ALPHA_HI = 0.0, 10.0
RE_LO, RE_HI = 0.70e6, 1.30e6
START_ALPHA, START_RE = 0.0, RE_NOMINAL  # the race ROM lane's own converged design

DESCENT_STEP_DIVISOR = 30.0   # same convention as workflows.shape_optimization.descend
MAX_STEPS = 200


def _grid(alphas, res, tag_prefix):
    return [{"alpha": a, "re": r, "tag": f"{tag_prefix}-a{a:g}-re{r:.0f}"}
            for a in alphas for r in res]


def _solve_grid(points, subdir):
    api = VspAeroWingApi(WORK / subdir, reuse_prior=True)
    designs = [{**WING, "re_cref": p["re"], "alpha_start": p["alpha"],
               "alpha_end": p["alpha"], "alpha_npts": 1,
               "tag_hint": p["tag"]} for p in points]

    def on_result(i, result, error):
        if error:
            print(f"  ! solve failed for {points[i]['tag']}: {error}")

    results = api.evaluate_many(designs, max_workers=2, on_result=on_result)
    out = []
    for p, r in zip(points, results):
        if r is None:
            continue
        out.append({**p, "l_d": float(r["polar"]["L_D"][0])})
    return out


# --------------------------------------------------------------------------
# Analytic gradient of the fitted quadratic-in-(alpha, u) surface
#   L/D = c0 + c1*a + c2*a^2 + c3*u + c4*u^2 + c5*a*u,  u = (Re - Re_ref)/Re_ref
# --------------------------------------------------------------------------

def _grad_alpha_u(coeff, alpha, u):
    c0, c1, c2, c3, c4, c5 = coeff
    d_alpha = c1 + 2.0 * c2 * alpha + c5 * u
    d_u = c3 + 2.0 * c4 * u + c5 * alpha
    return d_alpha, d_u


def _finite_diff_grad(coeff, alpha, re, h_alpha=1e-3, h_re=100.0):
    """Central finite-difference gradient at (alpha, re), for the proactive
    gradient check against the analytic one."""
    def f(a, r):
        return predict_reynolds_surface(coeff, a, r, RE_REF)

    d_alpha = (f(alpha + h_alpha, re) - f(alpha - h_alpha, re)) / (2 * h_alpha)
    d_re = (f(alpha, re + h_re) - f(alpha, re - h_re)) / (2 * h_re)
    return d_alpha, d_re


def descend(coeff):
    """Projected gradient ASCENT (maximising L/D) in normalized (alpha, u)
    coordinates, mirroring workflows.shape_optimization.descend's contract:
    every step computed, every iterate clamped to bounds, full trajectory
    returned. Nothing here is interpolated or padded."""
    a_range = ALPHA_HI - ALPHA_LO
    u_lo, u_hi = (RE_LO - RE_REF) / RE_REF, (RE_HI - RE_REF) / RE_REF
    u_range = u_hi - u_lo

    def to_re(u):
        return u * RE_REF + RE_REF

    alpha = min(max(START_ALPHA, ALPHA_LO), ALPHA_HI)
    u = min(max((START_RE - RE_REF) / RE_REF, u_lo), u_hi)

    # Normalized-space gradient at a design point: chain rule through the
    # a_range / u_range scaling so both axes are commensurate (both live in
    # roughly [0,1]-scale units regardless of alpha being O(10) and Re being
    # O(1e6)).
    def norm_grad(alpha, u):
        d_alpha, d_u = _grad_alpha_u(coeff, alpha, u)
        return d_alpha * a_range, d_u * u_range

    # Per-iteration adaptive step, sized from the LOCAL normalized-gradient
    # magnitude (not a single global worst case -- the corner-to-corner
    # gradient here spans orders of magnitude). Standard projected-gradient
    # treatment of an active bound: when an axis is pinned at a bound and its
    # raw gradient points further OUT of the box, that component contributes
    # nothing feasible -- it is excluded from both the step-size normalization
    # and the stopping test (the "active-set" gradient), otherwise a steep
    # but infeasible component starves progress on the other, still-feasible
    # axis. Every step still moves at most 1/DESCENT_STEP_DIVISOR of the box
    # (in normalized units) and every iterate is clamped to the real bounds.
    max_move = 1.0 / DESCENT_STEP_DIVISOR
    tolerance = 1e-3
    eps = 1e-9

    def active_grad(alpha, u, gn_alpha, gn_u):
        eff_alpha = gn_alpha
        if (alpha <= ALPHA_LO + eps and gn_alpha < 0) or \
           (alpha >= ALPHA_HI - eps and gn_alpha > 0):
            eff_alpha = 0.0
        eff_u = gn_u
        if (u <= u_lo + eps and gn_u < 0) or (u >= u_hi - eps and gn_u > 0):
            eff_u = 0.0
        return eff_alpha, eff_u

    trajectory = []

    def record(alpha, u):
        d_alpha, d_u = _grad_alpha_u(coeff, alpha, u)
        gn_alpha, gn_u = norm_grad(alpha, u)
        trajectory.append({
            "alpha": alpha, "re": to_re(u),
            "objective": predict_reynolds_surface(coeff, alpha, to_re(u), RE_REF),
            "gradient": {"d_alpha": d_alpha, "d_re": d_u / RE_REF},
            "gradient_norm_normalized": math.hypot(gn_alpha, gn_u),
        })

    record(alpha, u)
    for _ in range(MAX_STEPS):
        gn_alpha, gn_u = norm_grad(alpha, u)
        eff_alpha, eff_u = active_grad(alpha, u, gn_alpha, gn_u)
        gnorm = math.hypot(eff_alpha, eff_u)
        if gnorm <= tolerance:
            break
        step = max_move / gnorm
        # ASCENT: move WITH the (active-set) gradient, in normalized units
        # (step*eff_alpha is a normalized-alpha move, so *a_range converts it
        # back to real degrees; same for u), then clamp to real bounds.
        proposed_alpha = min(max(alpha + step * eff_alpha * a_range, ALPHA_LO), ALPHA_HI)
        proposed_u = min(max(u + step * eff_u * u_range, u_lo), u_hi)
        moved_alpha = abs(proposed_alpha - alpha) / a_range
        moved_u = abs(proposed_u - u) / u_range
        # No feasible move happened this step: stop, this is the constrained
        # optimum.
        if math.hypot(moved_alpha, moved_u) <= eps:
            break
        alpha, u = proposed_alpha, proposed_u
        record(alpha, u)
    return trajectory, {"max_move_per_step": max_move, "tolerance": tolerance}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    print("=" * 78)
    print("STEP 1 -- baseline: race act's alpha-only ROM lane (recorded, not "
          "touched by this script)")
    baseline_recorded_path = (SDK.parent / "demo-output" / "website" / "race"
                              / "pass2" / "race.json")
    baseline_recorded = None
    if baseline_recorded_path.exists():
        rec = json.loads(baseline_recorded_path.read_text())
        baseline_recorded = rec.get("rom")
        print(f"  recorded alpha* = {baseline_recorded['alpha_star']:g} deg, "
              f"Re pinned at {RE_NOMINAL:.3e} (never varied), "
              f"predicted L/D {baseline_recorded['predicted']:.4f}, "
              f"confirmed L/D {baseline_recorded['confirmed']:.4f}, "
              f"surrogate error {baseline_recorded['surrogate_error']:.4f}")
    else:
        print("  no prior race.json found on disk")

    print("\nSTEP 2 -- reload the 25 training + 16 validation VSPAERO anchors "
          "from commit 069cf13's cache (reuse_prior=True, no new solves)")
    train = _solve_grid(_grid(TRAIN_ALPHAS, TRAIN_RES, "train"), "train")
    val = _solve_grid(_grid(VAL_ALPHAS, VAL_RES, "val"), "val")
    print(f"  train anchors: {len(train)}/25   validation anchors: {len(val)}/16")

    coeff = fit_reynolds_surface([p["alpha"] for p in train],
                                 [p["re"] for p in train],
                                 [p["l_d"] for p in train], RE_REF)
    tq = fit_quality([p["alpha"] for p in train], [p["re"] for p in train],
                     [p["l_d"] for p in train], coeff, RE_REF)
    vq = fit_quality([p["alpha"] for p in val], [p["re"] for p in val],
                     [p["l_d"] for p in val], coeff, RE_REF)
    print(f"  fit: train rmse={tq['rmse']:.4f} r2={tq['r2']:.4f}   "
          f"val rmse={vq['rmse']:.4f} r2={vq['r2']:.4f}")
    print(f"  coefficients (c0..c5): {['%.5g' % c for c in coeff]}")

    print("\nSTEP 3 -- proactive check: analytic gradient vs finite-difference, "
          "at the start point")
    d_alpha_an, d_re_an = _grad_alpha_u(
        coeff, START_ALPHA, (START_RE - RE_REF) / RE_REF)
    d_re_an = d_re_an / RE_REF
    d_alpha_fd, d_re_fd = _finite_diff_grad(coeff, START_ALPHA, START_RE)
    gcheck = {
        "analytic": {"d_alpha": d_alpha_an, "d_re": d_re_an},
        "finite_difference": {"d_alpha": d_alpha_fd, "d_re": d_re_fd},
        "abs_error": {"d_alpha": abs(d_alpha_an - d_alpha_fd),
                      "d_re": abs(d_re_an - d_re_fd)},
    }
    print(f"  d(L/D)/d(alpha): analytic {d_alpha_an:.6f}  fd {d_alpha_fd:.6f}  "
          f"|err| {gcheck['abs_error']['d_alpha']:.2e}")
    print(f"  d(L/D)/d(Re):    analytic {d_re_an:.3e}  fd {d_re_fd:.3e}  "
          f"|err| {gcheck['abs_error']['d_re']:.2e}")
    grad_check_pass = (gcheck['abs_error']['d_alpha'] < 1e-4
                       and gcheck['abs_error']['d_re'] < 1e-9)
    print(f"  VERDICT: {'PASS' if grad_check_pass else 'FAIL'}")

    print("\nSTEP 4 -- gradient-driven descent (ascent on L/D) over (alpha, Re), "
          f"start alpha={START_ALPHA:g} deg, Re={START_RE:.3e}")
    trajectory, descent_meta = descend(coeff)
    for i, pt in enumerate(trajectory):
        gn = math.hypot(pt["gradient"]["d_alpha"], pt["gradient"]["d_re"] * RE_REF)
        print(f"  step {i:2d}: alpha={pt['alpha']:7.4f} deg  Re={pt['re']:.5e}  "
              f"L/D={pt['objective']:.4f}  |grad|_norm={pt['gradient_norm_normalized']:.4e}")
    converged = trajectory[-1]
    steps = len(trajectory) - 1
    in_domain = (ALPHA_LO - 1e-9 <= converged["alpha"] <= ALPHA_HI + 1e-9
                and RE_LO - 1e-9 <= converged["re"] <= RE_HI + 1e-9)
    print(f"\n  converged after {steps} steps: alpha*={converged['alpha']:.4f} deg, "
          f"Re*={converged['re']:.5e}, predicted L/D={converged['objective']:.4f}")
    print(f"  VALIDITY DOMAIN CHECK: alpha in [{ALPHA_LO},{ALPHA_HI}], "
          f"Re in [{RE_LO:.2e},{RE_HI:.2e}] -- "
          f"{'INSIDE -- PASS' if in_domain else 'OUTSIDE -- FAIL (extrapolation)'}")

    print("\nSTEP 5 -- confirmation: fresh real VSPAERO solves (reuse_prior=False) "
          "at the BASELINE design and at the CONVERGED design")
    confirm_api = VspAeroWingApi(CONFIRM_WORK, reuse_prior=False)

    def _confirm(alpha, re, tag):
        design = {**WING, "re_cref": re, "alpha_start": alpha, "alpha_end": alpha,
                  "alpha_npts": 1, "tag_hint": tag}
        t0 = time.time()
        result = confirm_api.evaluate(design)
        elapsed = time.time() - t0
        l_d = float(result["polar"]["L_D"][0])
        return l_d, elapsed, result

    baseline_l_d, baseline_s, _ = _confirm(START_ALPHA, START_RE, "baseline-fresh")
    print(f"  baseline  (alpha={START_ALPHA:g}, Re={START_RE:.3e}): "
          f"confirmed L/D = {baseline_l_d:.4f}  ({baseline_s:.2f}s, fresh solve)")

    converged_l_d, converged_s, _ = _confirm(
        converged["alpha"], converged["re"], "converged-fresh")
    print(f"  converged (alpha={converged['alpha']:.4f}, Re={converged['re']:.5e}): "
          f"confirmed L/D = {converged_l_d:.4f}  ({converged_s:.2f}s, fresh solve)")

    predicted_at_converged = converged["objective"]
    gap = converged_l_d - predicted_at_converged
    print(f"\n  SURROGATE VS SOLVER GAP at the converged design: predicted "
          f"{predicted_at_converged:.4f}  vs  confirmed {converged_l_d:.4f}  "
          f"-> gap {gap:+.4f} L/D ({abs(gap) / converged_l_d * 100:.2f}% of value)")

    improvement_abs = converged_l_d - baseline_l_d
    improvement_pct = improvement_abs / baseline_l_d * 100
    print(f"\n  MEASURED IMPROVEMENT vs baseline (both confirmed by fresh "
          f"solver runs this session): {improvement_abs:+.4f} L/D "
          f"({improvement_pct:+.2f}%)")

    report = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "baseline_recorded_prior_run": baseline_recorded,
        "surrogate_fit": {"coefficients": coeff, "train": tq, "val": vq,
                          "re_ref": RE_REF, "domain": {"alpha": [ALPHA_LO, ALPHA_HI],
                                                        "re": [RE_LO, RE_HI]}},
        "gradient_check": {**gcheck, "pass": grad_check_pass},
        "descent": {"start": {"alpha": START_ALPHA, "re": START_RE},
                   "trajectory": trajectory, "steps": steps,
                   "meta": descent_meta},
        "domain_check": {"in_domain": in_domain,
                         "alpha_bounds": [ALPHA_LO, ALPHA_HI],
                         "re_bounds": [RE_LO, RE_HI]},
        "confirmation": {
            "baseline": {"alpha": START_ALPHA, "re": START_RE,
                        "confirmed_l_d": baseline_l_d, "solve_seconds": baseline_s},
            "converged": {"alpha": converged["alpha"], "re": converged["re"],
                         "predicted_l_d": predicted_at_converged,
                         "confirmed_l_d": converged_l_d,
                         "gap": gap, "solve_seconds": converged_s},
        },
        "measured_improvement": {"absolute_l_d": improvement_abs,
                                 "percent": improvement_pct},
    }
    out_path = OUT / "gradient_descent_result.json"
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nresult written: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
