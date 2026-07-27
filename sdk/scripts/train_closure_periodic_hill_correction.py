"""Trained data-driven RANS velocity-correction entry for the closure-challenge
benchmark, scoped to the periodic-hills (Parm_PH_29) sub-family.

CONTEXT: demo-output/website/agenda/r3-closure-challenge-rans-floor.json
measured a zero-ML "RANS-identity reference floor" of overall 0.1036 by
scoring the benchmark's own raw k-omega SST velocity field, unmodified,
through the benchmark's own closure_challenge.score(). This script is the
first genuinely TRAINED attempt, proposed in
demo-output/website/agenda/r3-closure-challenge-trained-baseline.json.

SCOPE DECISION (stated plainly, not hidden): the benchmark ships the
derived tensor-basis inputs this field's literature standard requires
(gradU, walldist) ONLY for the periodic-hills (Parm_PH_29) case family.
The DUCT, CBFS, PH_Breuer and NASA_2DWMH cases do not ship gradU (DUCT/
CBFS/PH_Breuer also lack walldist and mesh coordinates in their solved
time directories). Computing a velocity-gradient reconstruction and a
geometric wall-distance field from scratch for those families is a
separate, larger effort out of scope for this run. So:
  - A real invariant, non-dimensional, tensor-basis feature set (Pope's 5
    scalar invariants of the normalized strain/rotation tensors, plus a
    turbulent Reynolds number and a turbulent/mean kinetic-energy ratio)
    is built and a model is TRAINED on it, using only the periodic-hills
    training cases the benchmark's own suggested split allows.
  - The trained correction is applied ONLY to the 4 periodic-hill test
    cases (alpha_15_13929_4048, alpha_15_13929_2024, alpha_05_4071_4048,
    alpha_05_4071_2024).
  - The other 4 test cases (AR_1_Ret_360, AR_3_Ret_360, AR_14_Ret_180,
    NASA_2DWMH) are passed through UNCORRECTED (identical to the RANS-
    identity floor) because no matching-family training data with the
    required derived fields exists in this release within this run's
    scope. This is reported explicitly, not disguised as a full-benchmark
    trained model.

DATA SPLIT (the benchmark's own suggested split, never touching the 8
named test cases for training or validation -- see this repo's binding
rule note in r3-closure-challenge-trained-baseline.json):
  TRAIN (21 cases): all Parm_PH_29 variations not listed as test or
    validation below.
  VALIDATION (4 cases, held out, never trained on): alpha_05_10071_4048,
    alpha_05_10071_2024, alpha_15_7929_4048, alpha_15_7929_2024.
  TEST (the 8 official cases; ground truth is only ever touched through
    closure_challenge.score()/evaluate_by_case(), which is called exactly
    once at the end): alpha_15_13929_4048, alpha_15_13929_2024,
    alpha_05_4071_4048, alpha_05_4071_2024, AR_1_Ret_360, AR_3_Ret_360,
    AR_14_Ret_180, NASA_2DWMH.

METHOD: per-cell features from the RANS solution only (no ground truth
used at inference time) -- Pope's 5 invariants of the (k/epsilon)-scaled
strain-rate and rotation-rate tensors built from gradU, a turbulent
Reynolds number sqrt(k)*walldist/(50*nu), and the turbulent/mean kinetic
energy ratio k/(k + 0.5|U|^2). Target: per-cell velocity correction
delta_U = U_LES - U_RANS. Model: one HistGradientBoostingRegressor per
velocity component (start with gradient-boosted trees, not a neural
network, per the queued proposal's launch guidance).

Setup: identical scratch-clone convention as
sdk/scripts/run_closure_challenge_evidence.py. Requires scikit-learn in
addition to that script's dependencies (numpy, scipy, Ofpp,
closure_challenge).

Run (2-core cap)::
    taskset -c 0-1 python sdk/scripts/train_closure_periodic_hill_correction.py

Writes demo-output/website/closure_challenge_trained_entry.json.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np

_SDK = Path(__file__).resolve().parents[1]
_REPO = _SDK.parent
_OUT = _REPO / "demo-output" / "website" / "closure_challenge_trained_entry.json"

_DEFAULT_BENCHMARK_DIR = Path.home() / "closure-challenge-benchmark"
_DEFAULT_EVAL_PKG_DIR = Path.home() / "closure-challenge-pkg"
BENCHMARK_DIR = Path(os.environ.get("CLOSURE_BENCHMARK_DIR", str(_DEFAULT_BENCHMARK_DIR)))
EVAL_PKG_DIR = Path(os.environ.get("CLOSURE_EVAL_PKG_DIR", str(_DEFAULT_EVAL_PKG_DIR)))

CMU = 0.09

# ---------------------------------------------------------------------------
# Case inventory (verified against the scratch clone's directory listing;
# counts match the README: PHLL29 = 21 train + 4 val + 4 test = 29 total).
# ---------------------------------------------------------------------------
_PH_TEST = [
    "alpha_15_13929_4048", "alpha_15_13929_2024",
    "alpha_05_4071_4048", "alpha_05_4071_2024",
]
_PH_VAL = [
    "alpha_05_10071_4048", "alpha_05_10071_2024",
    "alpha_15_7929_4048", "alpha_15_7929_2024",
]
_PH_TRAIN = [
    "alpha_05_10071_3036", "alpha_05_4071_3036", "alpha_05_7071_2024",
    "alpha_05_7071_3036", "alpha_05_7071_4048",
    "alpha_075",
    "alpha_10_12000_2024", "alpha_10_12000_3036", "alpha_10_12000_4048",
    "alpha_10_6000_2024", "alpha_10_6000_3036", "alpha_10_6000_4048",
    "alpha_10_9000_2024", "alpha_10_9000_3036", "alpha_10_9000_4048",
    "alpha_125",
    "alpha_15_10929_2024", "alpha_15_10929_3036", "alpha_15_10929_4048",
    "alpha_15_13929_3036", "alpha_15_7929_3036",
]

# The 4 non-periodic-hill test cases: passed through uncorrected (identical
# to the RANS-identity floor). Paths mirror
# sdk/scripts/run_closure_challenge_evidence.py's _RANS_TIME/_COORD_SUBPATH.
_OTHER_TEST_RANS = {
    "AR_1_Ret_360": ("data/DUCT/AR_1_Ret_360", "405", "constant/C"),
    "AR_3_Ret_360": ("data/DUCT/AR_3_Ret_360", "1540", "constant/C"),
    "AR_14_Ret_180": ("data/DUCT/AR_14_Ret_180", "7009", "constant/C"),
    "NASA_2DWMH": ("data/NASA_2DWMH", "2000", "2000/C"),
}

assert len(_PH_TRAIN) == 21 and len(_PH_VAL) == 4 and len(_PH_TEST) == 4
assert not (set(_PH_TRAIN) & set(_PH_VAL))
assert not (set(_PH_TRAIN) & set(_PH_TEST))
assert not (set(_PH_VAL) & set(_PH_TEST))


def _case_dir(case: str) -> Path:
    alpha = "alpha_" + case.split("_")[1]
    return BENCHMARK_DIR / "data" / "Parm_PH_29" / alpha / case


def _read_nu(case_dir: Path) -> float:
    text = (case_dir / "constant" / "transportProperties").read_text()
    m = re.search(r"\bnu\s+nu\s*\[[^\]]*\]\s*([0-9eE+\-.]+)\s*;", text)
    if not m:
        raise ValueError(f"could not parse nu from {case_dir}")
    return float(m.group(1))


def _load_rans_fields(case: str, parse_internal_field):
    d = _case_dir(case)
    t = d / "20000"
    C = parse_internal_field(str(t / "C"))
    U = parse_internal_field(str(t / "U"))
    gradU = parse_internal_field(str(t / "gradU"))
    k = parse_internal_field(str(t / "k"))
    omega = parse_internal_field(str(t / "omega"))
    walldist = parse_internal_field(str(t / "walldist"))
    nu = _read_nu(d)
    n = U.shape[0]
    assert C.shape[0] == n and gradU.shape[0] == n and k.shape[0] == n \
        and omega.shape[0] == n and walldist.shape[0] == n, f"{case}: field size mismatch"
    return dict(C=C, U=U, gradU=gradU, k=k, omega=omega, walldist=walldist, nu=nu)


def _load_ground_truth_U(case: str, parse_internal_field):
    d = _case_dir(case)
    u_les = parse_internal_field(str(d / "0" / "U_LES"))
    return u_les


def build_features(gradU: np.ndarray, k: np.ndarray, omega: np.ndarray,
                    walldist: np.ndarray, U: np.ndarray, nu: float) -> np.ndarray:
    """Invariant, non-dimensional, per-cell feature vector.

    Uses only quantities derivable from the RANS solution itself (no
    ground truth), so the identical function applies at train and
    inference time.
    """
    n = gradU.shape[0]
    g = gradU.reshape(n, 3, 3)
    # OpenFOAM's own grad(U) internal-field component order is
    # (xx xy xz yx yy yz zx zy zz), i.e. component (i,j) = d(U_i)/d(x_j).
    S = 0.5 * (g + np.transpose(g, (0, 2, 1)))
    W = 0.5 * (g - np.transpose(g, (0, 2, 1)))

    omega_safe = np.maximum(omega, 1e-8)
    tau = 1.0 / (CMU * omega_safe)  # ~ k/epsilon time scale
    S_hat = tau[:, None, None] * S
    W_hat = tau[:, None, None] * W

    I1 = np.einsum("nij,nji->n", S_hat, S_hat)
    I2 = np.einsum("nij,nji->n", W_hat, W_hat)
    I3 = np.einsum("nij,njk,nki->n", S_hat, S_hat, S_hat)
    I4 = np.einsum("nij,njk,nki->n", W_hat, W_hat, S_hat)
    I5 = np.einsum("nij,njk,nkl,nli->n", W_hat, W_hat, S_hat, S_hat)

    re_y = np.sqrt(np.maximum(k, 0.0)) * walldist / (50.0 * nu)
    umag2 = np.sum(U ** 2, axis=-1)
    tke_ratio = k / (k + 0.5 * umag2 + 1e-12)

    feats = np.stack([I1, I2, I3, I4, I5, re_y, tke_ratio], axis=1)
    return feats


FEATURE_NAMES = ["I1_S2", "I2_W2", "I3_S3", "I4_W2S", "I5_W2S2", "Re_y", "tke_ratio"]


def scaled_mae(U_pred: np.ndarray, U_true: np.ndarray) -> float:
    """Identical formula to closure_challenge.eval.evaluate_individual_case."""
    mae = np.mean(np.linalg.norm(U_pred - U_true, axis=-1))
    scale = np.mean(np.linalg.norm(U_true, axis=-1))
    return float(mae / scale)


def main() -> None:
    if not BENCHMARK_DIR.exists():
        print(f"ERROR: benchmark scratch clone not found at {BENCHMARK_DIR}.", file=sys.stderr)
        sys.exit(1)
    if str(EVAL_PKG_DIR / "src") not in sys.path:
        sys.path.insert(0, str(EVAL_PKG_DIR / "src"))

    from closure_challenge import case_names, evaluate_by_case, score, evaluation_points
    import closure_challenge as _cc
    from Ofpp import parse_internal_field
    from scipy.interpolate import NearestNDInterpolator
    from sklearn.ensemble import HistGradientBoostingRegressor

    os.chdir(BENCHMARK_DIR)

    expected_cases = set(_PH_TEST) | set(_OTHER_TEST_RANS.keys())
    actual_cases = set(case_names())
    if expected_cases != actual_cases:
        print(f"ERROR: case set mismatch vs benchmark harness. "
              f"Expected {sorted(expected_cases)}, got {sorted(actual_cases)}.", file=sys.stderr)
        sys.exit(1)

    # ---------------- CHECK 1: reproduce the RANS-identity floor first ----
    floor_predictions = {}
    for case in _PH_TEST:
        f = _load_rans_fields(case, parse_internal_field)
        interp = NearestNDInterpolator(f["C"], f["U"])
        floor_predictions[case] = interp(evaluation_points(case))
    for case, (case_path, time_dir, coord_sub) in _OTHER_TEST_RANS.items():
        coords = parse_internal_field(os.path.join(case_path, coord_sub))
        u_rans = parse_internal_field(os.path.join(case_path, time_dir, "U"))
        interp = NearestNDInterpolator(coords, u_rans)
        floor_predictions[case] = interp(evaluation_points(case))
    floor_overall = float(score(floor_predictions))
    floor_per_case = {c: float(v) for c, v in evaluate_by_case(floor_predictions).items()}
    floor_reproduces_recorded = round(floor_overall, 4) == 0.1036
    print(f"[check] RANS-identity floor reproduced under this harness invocation: "
          f"{floor_overall:.4f} (recorded 0.1036) -> "
          f"{'MATCH' if floor_reproduces_recorded else 'MISMATCH'}")

    # ---------------- Build train / validation feature sets ---------------
    def build_case_arrays(case_list):
        X_parts, y_parts, sizes = [], [], {}
        for case in case_list:
            f = _load_rans_fields(case, parse_internal_field)
            u_les = _load_ground_truth_U(case, parse_internal_field)
            assert u_les.shape[0] == f["U"].shape[0], f"{case}: U_LES/mesh size mismatch"
            X = build_features(f["gradU"], f["k"], f["omega"], f["walldist"], f["U"], f["nu"])
            y = u_les - f["U"]
            X_parts.append(X)
            y_parts.append(y)
            sizes[case] = X.shape[0]
        return np.concatenate(X_parts, axis=0), np.concatenate(y_parts, axis=0), sizes

    print(f"[data] building training features from {len(_PH_TRAIN)} cases (never touching "
          f"validation or test cases for fitting)...")
    X_train, y_train, train_sizes = build_case_arrays(_PH_TRAIN)
    print(f"[data] train: {X_train.shape[0]} cells, {X_train.shape[1]} features")

    # ---------------- Fit: one HGB regressor per velocity component --------
    models = []
    for comp in range(3):
        m = HistGradientBoostingRegressor(
            max_iter=300, max_depth=6, learning_rate=0.05,
            l2_regularization=1.0, random_state=0,
        )
        m.fit(X_train, y_train[:, comp])
        models.append(m)
    print("[train] fit 3 HistGradientBoostingRegressor models (u, v, w correction components)")

    def predict_correction(X):
        return np.stack([m.predict(X) for m in models], axis=1)

    # ---------------- TRAIN score (pooled + per-case; NOT a validation number) ----
    # Reconstructed per-case (not from the flat X_train/y_train arrays directly)
    # so per-case U_pred/U_true bookkeeping is unambiguous.
    train_per_case = {}
    offset = 0
    all_true_train, all_pred_train = [], []
    for case in _PH_TRAIN:
        n = train_sizes[case]
        Xc = X_train[offset:offset + n]
        f = _load_rans_fields(case, parse_internal_field)
        u_true = _load_ground_truth_U(case, parse_internal_field)
        delta_pred = predict_correction(Xc)
        u_pred = f["U"] + delta_pred
        train_per_case[case] = scaled_mae(u_pred, u_true)
        all_true_train.append(u_true)
        all_pred_train.append(u_pred)
        offset += n
    train_overall = scaled_mae(np.concatenate(all_pred_train), np.concatenate(all_true_train))
    print(f"[train score] pooled scaled-MAE over {len(_PH_TRAIN)} training cases: {train_overall:.4f}")

    # ---------------- VALIDATION score (genuinely held out, never fit on) --
    val_per_case = {}
    all_true_val, all_pred_val = [], []
    for case in _PH_VAL:
        f = _load_rans_fields(case, parse_internal_field)
        u_true = _load_ground_truth_U(case, parse_internal_field)
        Xc = build_features(f["gradU"], f["k"], f["omega"], f["walldist"], f["U"], f["nu"])
        delta_pred = predict_correction(Xc)
        u_pred = f["U"] + delta_pred
        val_per_case[case] = scaled_mae(u_pred, u_true)
        all_true_val.append(u_true)
        all_pred_val.append(u_pred)
    val_overall = scaled_mae(np.concatenate(all_pred_val), np.concatenate(all_true_val))
    print(f"[validation score] pooled scaled-MAE over {len(_PH_VAL)} held-out validation cases: "
          f"{val_overall:.4f}")
    overfit_flag = val_overall > train_overall * 1.5
    print(f"[check] train vs validation divergence: train={train_overall:.4f} "
          f"val={val_overall:.4f} -> {'OVERFIT SUSPECTED' if overfit_flag else 'no strong divergence'}")

    # ---------------- Also report the RANS-identity floor computed the SAME
    # way (pooled scaled-MAE on raw mesh cells) on train/val cases, so the
    # ML delta on those cases is visible before ever touching the official
    # test harness. ----------------------------------------------------
    def identity_pooled(case_list):
        trues, preds = [], []
        for case in case_list:
            f = _load_rans_fields(case, parse_internal_field)
            u_true = _load_ground_truth_U(case, parse_internal_field)
            trues.append(u_true)
            preds.append(f["U"])
        return scaled_mae(np.concatenate(preds), np.concatenate(trues))

    train_identity = identity_pooled(_PH_TRAIN)
    val_identity = identity_pooled(_PH_VAL)
    print(f"[reference] raw-RANS pooled scaled-MAE on the SAME cells: "
          f"train={train_identity:.4f} val={val_identity:.4f}")

    # ---------------- TEST: apply trained correction to the 4 PH test cases,
    # pass the other 4 through unmodified, score with the official harness --
    predictions = {}
    for case in _PH_TEST:
        f = _load_rans_fields(case, parse_internal_field)
        Xc = build_features(f["gradU"], f["k"], f["omega"], f["walldist"], f["U"], f["nu"])
        delta_pred = predict_correction(Xc)
        u_pred_mesh = f["U"] + delta_pred
        interp = NearestNDInterpolator(f["C"], u_pred_mesh)
        predictions[case] = interp(evaluation_points(case))
    for case, (case_path, time_dir, coord_sub) in _OTHER_TEST_RANS.items():
        predictions[case] = floor_predictions[case]  # unmodified, already computed above

    trained_overall = float(score(predictions))
    trained_per_case = {c: float(v) for c, v in evaluate_by_case(predictions).items()}

    delta_vs_floor = round(trained_overall - floor_overall, 4)
    delta_vs_docket_rank4 = round(trained_overall - 0.0779, 4)
    beats_floor = trained_overall < floor_overall

    print("\n=== FINAL (official 8-case harness) ===")
    print(f"RANS-identity floor:  {floor_overall:.4f}")
    print(f"Trained entry:        {trained_overall:.4f}")
    print(f"Delta vs floor (0.1036): {delta_vs_floor:+.4f} "
          f"({'BEATS' if beats_floor else 'WORSE THAN'} floor)")
    print(f"Delta vs docket rank-4 (0.0779): {delta_vs_docket_rank4:+.4f}")

    leakage_check = {
        "train_val_test_disjoint": not (set(_PH_TRAIN) & set(_PH_VAL))
                                    and not (set(_PH_TRAIN) & set(_PH_TEST))
                                    and not (set(_PH_VAL) & set(_PH_TEST)),
        "ground_truth_test_npz_touched_only_via": "closure_challenge.score()/evaluate_by_case(), "
                                                    "called once on the final predictions dict",
        "model_fit_only_on": "_PH_TRAIN (21 cases); validation and test cells never appear in "
                              "X_train/y_train",
    }

    record = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "measured_date": str(date.today()),
        "purpose": "First genuinely trained closure-challenge entry (periodic-hills sub-family "
                   "only), scored through the benchmark's own harness, measured against the "
                   "versioned RANS-identity floor (0.1036) and the recorded rank-4 target (0.0779).",
        "scope_limitation": (
            "Correction trained and applied only to the 4 periodic-hill test cases. The other 4 "
            "test cases (AR_1_Ret_360, AR_3_Ret_360, AR_14_Ret_180, NASA_2DWMH) are passed through "
            "UNMODIFIED raw RANS (identical to the floor) because the benchmark does not ship "
            "gradU (DUCT/CBFS/PH_Breuer) or walldist/mesh-C in solved time directories (DUCT/CBFS/"
            "PH_Breuer) needed for the same invariant feature set, and reconstructing those fields "
            "from the mesh was out of scope for this run."
        ),
        "metric_definition": {
            "per_case": "scaled MAE = mean(||U_pred - U_true||) over 1000 fixed eval points, "
                        "divided by mean(||U_true||)",
            "overall": "plain mean of the 8 per-case scaled MAE values, lower is better",
            "source": "closure_challenge/eval.py (identical package/commit as the floor evidence)",
        },
        "data_split": {
            "train_cases": _PH_TRAIN,
            "validation_cases_held_out": _PH_VAL,
            "test_cases_official": sorted(expected_cases),
            "n_train_cells": int(X_train.shape[0]),
        },
        "features": FEATURE_NAMES,
        "model": "HistGradientBoostingRegressor x3 (one per velocity component), "
                 "max_iter=300, max_depth=6, learning_rate=0.05",
        "checks": {
            "baseline_reproduces_0_1036_under_this_harness_invocation": floor_reproduces_recorded,
            "measured_floor_this_run": round(floor_overall, 4),
            "train_validation_test_leakage": leakage_check,
            "train_vs_validation_divergence_flag": overfit_flag,
        },
        "scores": {
            "train_pooled_scaled_mae": round(train_overall, 4),
            "train_pooled_scaled_mae_per_case": {c: round(v, 4) for c, v in train_per_case.items()},
            "train_raw_rans_identity_on_same_cells": round(train_identity, 4),
            "validation_pooled_scaled_mae": round(val_overall, 4),
            "validation_pooled_scaled_mae_per_case": {c: round(v, 4) for c, v in val_per_case.items()},
            "validation_raw_rans_identity_on_same_cells": round(val_identity, 4),
        },
        "official_test_harness_result": {
            "trained_entry_overall": round(trained_overall, 4),
            "trained_entry_per_case": {c: round(v, 4) for c, v in trained_per_case.items()},
            "rans_identity_floor_overall_this_run": round(floor_overall, 4),
            "rans_identity_floor_per_case_this_run": {c: round(v, 4) for c, v in floor_per_case.items()},
            "delta_vs_floor": delta_vs_floor,
            "beats_floor": beats_floor,
            "delta_vs_docket_rank4_0_0779": delta_vs_docket_rank4,
        },
    }

    _OUT.parent.mkdir(parents=True, exist_ok=True)
    _OUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {_OUT}")


if __name__ == "__main__":
    main()
