"""G1 of the methods audit (CLOSURE_METHODS_COMPARISON.md, ac2f37ee): seed
sensitivity of the round-1 periodic-hills model, measured TEST-BLIND.

WHY THIS IS LIVE: the PH model's 327,600 training cells exceed sklearn
1.9.0's 200,000-row binning subsample threshold, so HistGradientBoosting's
bin edges -- hence the trees, hence the three PH-model-served predictions
(alpha_15_13929_4048, alpha_15_13929_2024, NASA_2DWMH) -- depend on
``random_state``. The entry of record was trained at random_state=0 only,
and the gap to rank 2 is 0.0030.

PROTOCOL (pre-registered in closure_challenge_stability_physicality_audit.md
SS0.1, committed 73fa6a33 BEFORE this script first ran):
  * 8 seeds (random_state = 0..7), everything else frozen byte-for-byte
    against round 1 (same 21 training cases, 7 features, hyperparameters,
    venv). Seed 0 must reproduce the recorded round-1 model (train pooled
    0.0620 / validation pooled 0.0876) or the run is invalid.
  * Each seed is scored on the 4 PH VALIDATION cases only, with the same
    cell-wise scaled-MAE formula round 1 validates with. No harness scoring
    call is made; the raising-stub guard from
    export_closure_submission_csvs.py is re-armed first and proven armed.
  * Each seed also predicts at the three served test cases' RANS-derived
    features, interpolated to the official evaluation points (coordinates
    only). Seed-to-seed prediction spread at those points needs no ground
    truth and bounds the seed-induced per-case score change.
  * Materiality line, fixed in advance: 0.0003 (10% of the 0.0030 gap) on
    either overall-equivalent spread estimate; 0.0030 on any single case.

Run (2-core cap)::
    OMP_NUM_THREADS=2 taskset -c 0-1 \
        /home/ubuntu/closure-venv/bin/python \
        sdk/scripts/closure_ph_seed_sensitivity.py

Writes demo-output/website/closure_challenge_seed_sensitivity.json.
"""
from __future__ import annotations

import itertools
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

_SDK = Path(__file__).resolve().parent
_REPO = _SDK.parent.parent
sys.path.insert(0, str(_SDK))
import train_closure_periodic_hill_correction as ph  # noqa: E402
import train_closure_extended_correction as ex  # noqa: E402

# The one module that names this repository's tree (MOVE_MAP batch 3).
# Every name it exports is bound to a legacy/successor PAIR resolved
# against the filesystem at import, so the constants below are correct
# before the move, between batches and after it, with no edit here.
import sys as _sys  # noqa: E402
import pathlib as _pathlib  # noqa: E402
_LAB_PATHS_DIR = str(_pathlib.Path(__file__).resolve().parents[2]
                     / "scripts")
if _LAB_PATHS_DIR not in _sys.path:
    _sys.path.insert(0, _LAB_PATHS_DIR)
import lab_paths  # noqa: E402

_OUT = lab_paths.web_file("closure_challenge_seed_sensitivity.json")
_SCRATCH = Path(os.environ.get(
    "CLOSURE_SCRATCH",
    "/tmp/claude-1000/-home-ubuntu-Certonomous/64b13819-ff95-4d4d-a50f-3720bab19084/scratchpad"))

SEEDS = list(range(8))
SERVED = ["alpha_15_13929_4048", "alpha_15_13929_2024", "NASA_2DWMH"]
PROXY = {"alpha_15_13929_4048": "alpha_15_7929_4048",
         "alpha_15_13929_2024": "alpha_15_7929_2024",
         "NASA_2DWMH": None}  # no family validation case exists (round-2 record)
MATERIAL_OVERALL = 0.0003   # 10% of the 0.0030 gap to rank 2 -- pre-registered
MATERIAL_SINGLE = 0.0030    # a one-case spread the size of the whole gap


class ScoringCallRefused(RuntimeError):
    pass


def _forbid_scoring(cc, du, ev):
    """Identical raising-stub guard as export_closure_submission_csvs.py:
    every route to the test ground-truth velocities raises; only the
    coords-only evaluation-point lookup stays open."""
    cached = du._ground_truth()

    def coords_only(case):
        return np.asarray(cached[case]["coords"])

    def _refuse(name):
        def _raiser(*_a, **_kw):
            raise ScoringCallRefused(
                f"{name}() was called by closure_ph_seed_sensitivity.py. "
                "This audit is test-blind by pre-registration; nothing here "
                "may consume a scoring call or read test velocities.")
        return _raiser

    blocked = ("score", "score_from_csv", "evaluate_by_case",
               "evaluate_from_csv_by_case", "evaluate_individual_case",
               "_velocity_field", "_ground_truth", "_load_csv_predictions")
    for mod in (cc, du, ev):
        for name in blocked:
            if hasattr(mod, name):
                setattr(mod, name, _refuse(name))
    return coords_only


def main() -> None:
    t0 = time.time()
    if str(ph.EVAL_PKG_DIR / "src") not in sys.path:
        sys.path.insert(0, str(ph.EVAL_PKG_DIR / "src"))

    import closure_challenge as _cc
    from closure_challenge import dataset_utils as _du
    from closure_challenge import eval as _ev
    evaluation_points = _forbid_scoring(_cc, _du, _ev)
    try:
        _cc.score({})
    except ScoringCallRefused:
        print("[guard] verified: closure_challenge.score() now raises")
    else:
        print("ERROR: scoring guard not armed; refusing to continue.", file=sys.stderr)
        sys.exit(1)

    from Ofpp import parse_internal_field
    from scipy.interpolate import NearestNDInterpolator
    from sklearn.ensemble import HistGradientBoostingRegressor
    import sklearn

    os.chdir(ph.BENCHMARK_DIR)

    # ---------------- data: 21 train + 4 val PH cases (legal truth reads),
    # plus RANS-only features for the three served test cases ---------------
    print("[data] loading 21 PH training cases...")
    X_parts, y_parts = [], []
    for c in ph._PH_TRAIN:
        f = ph._load_rans_fields(c, parse_internal_field)
        X_parts.append(ph.build_features(f["gradU"], f["k"], f["omega"],
                                         f["walldist"], f["U"], f["nu"]))
        y_parts.append(ph._load_ground_truth_U(c, parse_internal_field) - f["U"])
    X_train = np.concatenate(X_parts)
    y_train = np.concatenate(y_parts)
    n_train = X_train.shape[0]
    assert n_train == 327600, f"expected 327600 training cells, got {n_train}"
    print(f"[data] {n_train} training cells (> 200000 binning subsample: "
          f"seed is live for this model)")

    print("[data] loading 4 PH validation cases (held out, never fit on)...")
    val = {}
    for c in ph._PH_VAL:
        f = ph._load_rans_fields(c, parse_internal_field)
        val[c] = dict(
            X=ph.build_features(f["gradU"], f["k"], f["omega"],
                                f["walldist"], f["U"], f["nu"]),
            U=f["U"],
            U_true=ph._load_ground_truth_U(c, parse_internal_field))

    print("[data] building RANS-only features for the 3 served test cases...")
    served = {}
    for c in ("alpha_15_13929_4048", "alpha_15_13929_2024"):
        f = ph._load_rans_fields(c, parse_internal_field)  # no U_LES read
        served[c] = dict(
            X=ph.build_features(f["gradU"], f["k"], f["omega"],
                                f["walldist"], f["U"], f["nu"]),
            U=f["U"], C=f["C"])
    nf = ex._reconstruct_nasa_fields("NASA_2DWMH", parse_internal_field)
    served["NASA_2DWMH"] = dict(
        X=ph.build_features(nf["gradU"], nf["k"], nf["omega"],
                            nf["walldist"], nf["U"], nf["nu"]),
        U=nf["U"], C=nf["C"])
    eval_pts = {c: evaluation_points(c) for c in SERVED}

    # RANS floor at the eval points: the scale for the test-side bound.
    rans_at_pts = {}
    for c in SERVED:
        interp = NearestNDInterpolator(served[c]["C"], served[c]["U"])
        rans_at_pts[c] = interp(eval_pts[c])

    # ---------------- the seed loop ---------------------------------------
    per_seed = {}
    test_preds = {c: {} for c in SERVED}
    for seed in SEEDS:
        ts = time.time()
        models = []
        for comp in range(3):
            m = HistGradientBoostingRegressor(
                max_iter=300, max_depth=6, learning_rate=0.05,
                l2_regularization=1.0, random_state=seed)
            m.fit(X_train, y_train[:, comp])
            models.append(m)

        def predict(X):
            return np.stack([m.predict(X) for m in models], axis=1)

        # train-side bookkeeping: mean |delta_pred - delta_true| on the
        # training cells (a plain correction-space MAE, not round 1's pooled
        # scaled MAE -- the validation numbers below are the metric of record).
        delta_train = predict(X_train)
        per_case_val, vp, vt = {}, [], []
        for c in ph._PH_VAL:
            u_pred = val[c]["U"] + predict(val[c]["X"])
            per_case_val[c] = ph.scaled_mae(u_pred, val[c]["U_true"])
            vp.append(u_pred)
            vt.append(val[c]["U_true"])
        val_pooled = ph.scaled_mae(np.concatenate(vp), np.concatenate(vt))

        for c in SERVED:
            u_mesh = served[c]["U"] + predict(served[c]["X"])
            interp = NearestNDInterpolator(served[c]["C"], u_mesh)
            test_preds[c][seed] = interp(eval_pts[c])

        per_seed[seed] = {
            "validation_pooled_scaled_mae": val_pooled,
            "validation_per_case": per_case_val,
            "train_mae_pooled_delta_vs_target": float(
                np.mean(np.linalg.norm(delta_train - y_train, axis=1))),
            "fit_seconds": round(time.time() - ts, 1),
        }
        print(f"[seed {seed}] val pooled {val_pooled:.6f}  per-case "
              + " ".join(f"{c.split('_')[-2]}_{c.split('_')[-1]}:{v:.6f}"
                         for c, v in per_case_val.items())
              + f"  ({per_seed[seed]['fit_seconds']}s)")

    # ---------------- seed-0 reproduction check ---------------------------
    rec1 = json.loads(lab_paths.web_file(
        "closure_challenge_trained_entry.json").read_text())
    recorded_val = rec1["scores"]["validation_pooled_scaled_mae"]
    seed0_val = round(per_seed[0]["validation_pooled_scaled_mae"], 4)
    seed0_ok = seed0_val == recorded_val
    print(f"[check] seed 0 reproduces recorded validation pooled scaled-MAE: "
          f"{seed0_val} vs recorded {recorded_val} -> "
          f"{'MATCH' if seed0_ok else 'MISMATCH'}")

    # Also anchor seed-0 test predictions against the shipped round-4 CSVs
    # (byte-written at %.10g): proves the seed-0 member of this ensemble IS
    # the entry of record's model, so the spread is ABOUT the entry.
    csv_dir = lab_paths.CLOSURE_SUBMISSION_ROUND4 / "test"
    csv_match = {}
    for c in SERVED:
        shipped = np.loadtxt(csv_dir / f"{c}.csv", delimiter=",")
        d = float(np.abs(test_preds[c][0] - shipped).max())
        csv_match[c] = d
        print(f"[check] seed-0 prediction vs shipped round-4 CSV {c}: "
              f"max abs diff {d:.3g}")

    # ---------------- spreads vs the pre-registered lines ------------------
    def spread(vals):
        return float(max(vals) - min(vals))

    R = {}
    for c in SERVED:
        p = PROXY[c]
        if p is not None:
            R[c] = spread([per_seed[s]["validation_per_case"][p] for s in SEEDS])
        else:
            R[c] = None
    R_pooled = spread([per_seed[s]["validation_pooled_scaled_mae"] for s in SEEDS])
    R_val_per_case = {c: spread([per_seed[s]["validation_per_case"][c] for s in SEEDS])
                      for c in ph._PH_VAL}

    B = {}
    for c in SERVED:
        scale = float(np.mean(np.linalg.norm(rans_at_pts[c], axis=1)))
        worst = 0.0
        for i, j in itertools.combinations(SEEDS, 2):
            d = float(np.mean(np.linalg.norm(test_preds[c][i] - test_preds[c][j],
                                             axis=1))) / scale
            worst = max(worst, d)
        B[c] = worst

    S_proxy = (R["alpha_15_13929_4048"] + R["alpha_15_13929_2024"]
               + B["NASA_2DWMH"]) / 8.0
    S_bound = sum(B.values()) / 8.0
    singles = [v for v in list(R.values()) + list(B.values()) if v is not None]
    material = (S_proxy >= MATERIAL_OVERALL or S_bound >= MATERIAL_OVERALL
                or max(singles) >= MATERIAL_SINGLE)

    print("\n=== G1 verdict against the pre-registered lines ===")
    for c in SERVED:
        print(f"  {c:24s} proxy-range R={R[c] if R[c] is None else f'{R[c]:.6f}'}"
              f"  test-side bound B={B[c]:.6f}")
    print(f"  validation pooled range: {R_pooled:.6f}")
    print(f"  S_proxy={S_proxy:.6f}  S_bound={S_bound:.6f}  "
          f"(material line {MATERIAL_OVERALL}) -> "
          f"{'MATERIAL' if material else 'below the line'}")

    record = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose": ("G1 of the methods audit: seed sensitivity of the round-1 PH model, "
                    "measured test-blind on the 4 PH validation cases and as a no-truth "
                    "prediction-spread bound at the 3 served test cases' evaluation points."),
        "pre_registration": {
            "file": "demo-output/website/closure_challenge_stability_physicality_audit.md",
            "committed_before_first_run": "73fa6a33",
            "material_if_overall_equivalent_spread_geq": MATERIAL_OVERALL,
            "material_if_any_single_case_geq": MATERIAL_SINGLE,
        },
        "mechanism": {
            "sklearn_version": sklearn.__version__,
            "n_train_cells": int(n_train),
            "binning_subsample_threshold": 200000,
            "seed_is_live_because": "n_train_cells > subsample threshold, so bin edges are "
                                     "drawn from a random 200k-row subsample per seed",
        },
        "protocol": {
            "seeds": SEEDS,
            "frozen": "21 PH training cases, 7 features, HGB hyperparameters "
                      "(max_iter=300, max_depth=6, lr=0.05, l2=1.0), venv",
            "scoring_calls_made": 0,
            "guard": "raising stubs re-armed and verified before any pipeline work "
                     "(same mechanism as export_closure_submission_csvs.py)",
            "ground_truth_reads": "21 PH train + 4 PH validation cases only",
        },
        "seed0_reproduction": {
            "validation_pooled_matches_round1_record": bool(seed0_ok),
            "recorded": recorded_val, "measured": seed0_val,
            "max_abs_diff_vs_shipped_round4_csvs": csv_match,
        },
        "per_seed": {str(s): per_seed[s] for s in SEEDS},
        "spreads": {
            "validation_per_case_range": R_val_per_case,
            "validation_pooled_range": R_pooled,
            "proxy_range_for_served_predictions": R,
            "test_side_prediction_spread_bound": B,
            "overall_equivalent_S_proxy": S_proxy,
            "overall_equivalent_S_bound": S_bound,
        },
        "verdict": {
            "material": bool(material),
            "gap_to_rank2": 0.0030,
        },
        "compute": {"elapsed_seconds": round(time.time() - t0, 1), "cores_cap": 2},
    }
    _OUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    if _SCRATCH.exists():
        np.savez_compressed(
            _SCRATCH / "g1_test_predictions.npz",
            **{f"{c}__{s}": test_preds[c][s] for c in SERVED for s in SEEDS})
    print(f"\nwrote {_OUT}  ({record['compute']['elapsed_seconds']}s)")


if __name__ == "__main__":
    main()
