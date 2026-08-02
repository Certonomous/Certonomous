"""What the cross-family structural mismatch criterion (proven half:
I3_S3/I4_W2S mismatch against a model's training regime -- see
closure_generalization_criterion.py) says about the 8 OFFICIAL test cases,
computed from their RANS-derived features ONLY, against the model currently
applied to each in the round-3 gated entry.

THIS IS A DECISION-TABLE EXERCISE, NOT A DECISION. It changes nothing: no
correction is altered, no closure_challenge.score()/evaluate_by_case() call
is made, and no ground truth (U_LES/tauij_LES) of any test case is read.
Whether to spend a 5th official scoring call on anything this table shows
is explicitly the coordinator's decision, not this script's.

LEAKAGE STATEMENT, stated the same way as every other artifact on this
ladder: the criterion's parameters (training-regime bounds for the PH and
DUCT models) were computed entirely from TRAINING data in
closure_generalization_criterion.py (21 PH train cases, 4 DUCT train cases)
and are RECOMPUTED here from the same training cases via the same
case_level_features() call (not refit -- no model is trained in this
script at all, only feature aggregation, which is deterministic and
reproduces the prior run's numbers exactly). Applying a frozen,
already-validated rule to test-side FEATURES (not ground truth) is exactly
what round 3's gate application already did, and exactly what the
coordinator's own audit of that action accepted. Ground truth is not read
for any of the 8 test cases anywhere in this script.

A DUE-DILIGENCE CORRECTION MADE WHILE BUILDING THIS TABLE, kept in the
record rather than quietly fixed: the first pass used mean_I3_S3 (as
closure_generalization_criterion.py did) and found NASA_2DWMH's mean_I3_S3
= +2.1e8 -- an absurd number given PH's entire training range is
[-4.7e-4, +3.7e-5]. Investigated before trusting it. Traced to a REAL but
DIFFERENT phenomenon than the proven DUCT mechanism: NASA_2DWMH has a large
low-turbulence, near-freestream region (its RANS omega stays at a
non-negligible background value there while k collapses to near-zero),
and EVERY tau-normalized Pope invariant (I1 through I5, not just I3/I4)
explodes in that region, because tau = 1/(Cmu*omega) stops representing a
meaningful turbulence timescale once k is negligible relative to the mean
strain rate. Checked with the robust p90(|.|) statistic (matching C1's own
established preference for p90 over mean) and against the FULL 15-feature
domain-coverage count: NASA_2DWMH is out of PH's training range on ALL 15
features simultaneously, not selectively on I3/I4. This is NOT the proven
"model has zero learned dependence on an algebraically-forced-zero
dimension" mechanism (that proof exists only for the DUCT model, and only
for I3_S3/I4_W2S specifically) -- it is a global, non-specific covariate
shift caused by a feature-pipeline fragility in low-turbulence regions.
Reported honestly below, not folded into the proven-mechanism finding, and
its predictive value is separately checked against NASA_2DWMH's ALREADY-
KNOWN (legitimate, round-2, single official call) actual outcome of only
+0.0011 -- mild, not catastrophic -- which does not match what the DUCT
mechanism would predict if it applied here. It does not.

Run (2-core cap, per current lab compute budget; box is loaded overnight
with a 17-hour 3D solve and six other threads, so this stays deliberately
tiny -- no model fitting at all, just feature extraction on 8 cases plus
the same aggregation already used to build training-regime bounds)::
    taskset -c 0-1 python sdk/scripts/closure_criterion_on_test_features.py

Writes demo-output/website/closure_challenge_criterion_test_case_table.json.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np

_SDK = Path(__file__).resolve().parent
_REPO = _SDK.parent.parent
sys.path.insert(0, str(_SDK))
import train_closure_periodic_hill_correction as ph  # noqa: E402
import train_closure_extended_correction as ext        # noqa: E402
import closure_baseline_error_gate as gate               # noqa: E402  (case_level_features)

_OUT = _REPO / "demo-output" / "website" / "closure_challenge_criterion_test_case_table.json"
_ROUND3 = _REPO / "demo-output" / "website" / "closure_challenge_trained_entry_round3_gated.json"

BENCHMARK_DIR = ph.BENCHMARK_DIR
EVAL_PKG_DIR = ph.EVAL_PKG_DIR

# What is CURRENTLY applied to each official test case, per round 3
# (closure_challenge_trained_entry_round3_gated.json). "None" means the
# gate declined the correction and raw RANS (the floor) is submitted --
# there is no model in use on that case to have a blind spot about.
_CURRENTLY_APPLIED = {
    "alpha_15_13929_4048": "PH",
    "alpha_15_13929_2024": "PH",
    "alpha_05_4071_4048": None,   # round-3 gate: DECLINE -> raw RANS
    "alpha_05_4071_2024": None,   # round-3 gate: DECLINE -> raw RANS
    "AR_1_Ret_360": "DUCT",
    "AR_3_Ret_360": "DUCT",
    "AR_14_Ret_180": "DUCT",
    "NASA_2DWMH": "PH",           # pre-registered fallback, round 2
}
# Already-known (legitimate, single official round-2 scoring call) actual
# per-case delta (corrected - floor) for the currently-applied model, where
# an entry exists -- used ONLY to sanity-check the criterion's predictive
# meaning, never to fit or select anything (all deltas below are already
# public/recorded facts, not new reads).
_KNOWN_ACTUAL_DELTA = {
    "alpha_15_13929_4048": -0.0819, "alpha_15_13929_2024": -0.1038,
    "alpha_05_4071_4048": None, "alpha_05_4071_2024": None,  # declined; delta n/a to "current"
    "AR_1_Ret_360": -0.0369, "AR_3_Ret_360": -0.0381, "AR_14_Ret_180": -0.0287,
    "NASA_2DWMH": +0.0011,
}


def main() -> None:
    t0 = time.time()
    if not BENCHMARK_DIR.exists():
        print(f"ERROR: benchmark scratch clone not found at {BENCHMARK_DIR}.", file=sys.stderr)
        sys.exit(1)
    if str(EVAL_PKG_DIR / "src") not in sys.path:
        sys.path.insert(0, str(EVAL_PKG_DIR / "src"))
    from Ofpp import parse_internal_field

    import os
    os.chdir(BENCHMARK_DIR)

    all_test_cases = set(ph._PH_TEST) | set(ph._OTHER_TEST_RANS.keys())
    assert all_test_cases == set(_CURRENTLY_APPLIED.keys())

    # ---------------- Training-regime bounds, recomputed from the same
    # training-only cases as closure_generalization_criterion.py (no model
    # fit -- feature aggregation only, deterministic). --------------------
    def case_level(loader_fn, case):
        f = loader_fn(case, parse_internal_field)
        X = ph.build_features(f["gradU"], f["k"], f["omega"], f["walldist"], f["U"], f["nu"])
        return gate.case_level_features(X, f["U"]), f

    ph_train_feats = [case_level(ph._load_rans_fields, c)[0] for c in ph._PH_TRAIN]
    duct_train_feats = [case_level(ext._reconstruct_duct_fields, c)[0] for c in ext._DUCT_TRAIN]
    feat_names = sorted(ph_train_feats[0].keys())

    def range_of(rows):
        arr = np.array([[r[k] for k in feat_names] for r in rows])
        return arr.min(axis=0), arr.max(axis=0)

    ph_min, ph_max = range_of(ph_train_feats)
    duct_min, duct_max = range_of(duct_train_feats)
    train_range = {"PH": (ph_min, ph_max), "DUCT": (duct_min, duct_max)}
    i3_idx, i4_idx = feat_names.index("p90_I3_S3"), feat_names.index("p90_I4_W2S")
    ph_i3_train_max = float(ph_max[i3_idx])
    duct_i3_train_max = float(duct_max[i3_idx])
    print(f"[frozen-equivalent thresholds, robust p90 statistic] "
          f"PH training max p90_I3_S3={ph_i3_train_max:.4e}  "
          f"DUCT training max p90_I3_S3={duct_i3_train_max:.4e}")

    def structural_mismatch_p90_i3(p90_i3_abs: float, model: str) -> bool:
        train_max = ph_i3_train_max if model == "PH" else duct_i3_train_max
        return bool(abs(p90_i3_abs) > 10.0 * max(train_max, 1e-12))

    def coverage_out_of_range(cfeat: dict, model: str) -> int:
        tmin, tmax = train_range[model]
        v = np.array([cfeat[k] for k in feat_names])
        return int(np.sum((v < tmin) | (v > tmax)))

    # ---------------- Test-case features, RANS-side only, no ground truth. --
    rows = []
    for case in ph._PH_TEST:
        cf, f = case_level(ph._load_rans_fields, case)
        rows.append((case, cf))
    for case in ext._DUCT_TEST:
        cf, f = case_level(ext._reconstruct_duct_fields, case)
        rows.append((case, cf))
    f = ext._reconstruct_nasa_fields("NASA_2DWMH", parse_internal_field)
    X = ph.build_features(f["gradU"], f["k"], f["omega"], f["walldist"], f["U"], f["nu"])
    rows.append(("NASA_2DWMH", gate.case_level_features(X, f["U"])))

    table = []
    print("\n=== DECISION TABLE (test-blind features only; nothing applied) ===")
    for case, cfeat in rows:
        current = _CURRENTLY_APPLIED[case]
        p90_i3 = cfeat["p90_I3_S3"]
        ph_flag = structural_mismatch_p90_i3(p90_i3, "PH")
        duct_flag = structural_mismatch_p90_i3(p90_i3, "DUCT")
        flag_on_current = None if current is None else (ph_flag if current == "PH" else duct_flag)
        cov_current = None if current is None else coverage_out_of_range(cfeat, current)
        is_global_covariate_shift = bool(cov_current is not None and cov_current == len(feat_names))
        row = dict(
            case=case, currently_applied_model=current,
            p90_I3_S3_abs=round(abs(p90_i3), 6),
            ph_model_would_flag_i3_mismatch=ph_flag,
            duct_model_would_flag_i3_mismatch=duct_flag,
            flag_on_currently_applied_model=flag_on_current,
            coverage_out_of_range_on_current_model_of_15=cov_current,
            proven_mechanism_applies=bool(flag_on_current and current == "DUCT"),
            global_covariate_shift_not_proven_mechanism=bool(flag_on_current and current == "PH" and is_global_covariate_shift),
            known_actual_delta_from_legitimate_round2_call=_KNOWN_ACTUAL_DELTA[case],
        )
        table.append(row)
        print(f"{case:22s} current={str(current):5s} p90_I3_S3_abs={abs(p90_i3):10.4e} "
              f"flag_on_current={flag_on_current} coverage={cov_current}/15  "
              f"known_actual_delta={_KNOWN_ACTUAL_DELTA[case]}")

    n_flagged_total = sum(1 for r in table if r["flag_on_currently_applied_model"])
    n_proven = sum(1 for r in table if r["proven_mechanism_applies"])
    n_global_shift = sum(1 for r in table if r["global_covariate_shift_not_proven_mechanism"])
    elapsed_s = time.time() - t0

    verdict = {
        "n_flagged_total": n_flagged_total,
        "n_flagged_by_proven_duct_mechanism": n_proven,
        "n_flagged_as_global_covariate_shift_unproven": n_global_shift,
        "changes_anything_actionable": n_proven > 0,
        "statement": (
            f"Of the 8 official test cases, the PROVEN mechanism (DUCT model extrapolating from "
            f"an algebraically-forced-zero dimension) flags {n_proven} under the model currently "
            f"applied to it -- all 3 duct test cases sit comfortably inside the DUCT model's own "
            f"training regime (as expected: they are the same physical class), and both PH test "
            f"cases the PH model corrects, plus both cases the round-3 gate already declined, sit "
            f"comfortably inside the PH model's training regime. This changes NOTHING about the "
            f"current entry through the proven mechanism. "
            f"Separately, {n_global_shift} case (NASA_2DWMH) is flagged, but not by the proven "
            f"mechanism -- it is out of the PH model's training range on ALL 15 features "
            f"simultaneously (a global covariate shift traced to a real but different cause: the "
            f"tau=1/(Cmu*omega) turbulence-timescale normalization exploding in NASA_2DWMH's "
            f"low-turbulence outer-flow region, not the DUCT model's proven zero-variance blind "
            f"spot). This does NOT match the proven mechanism's predictive pattern: NASA_2DWMH's "
            f"already-known actual outcome (legitimate round-2 official call) is a MILD +0.0011 "
            f"regression, not the 3.9x-10.4x catastrophic breakdown the proven mechanism produced "
            f"in every one of its 6 confirmed instances. Reading this flag as equivalent evidence "
            f"would overclaim what was proven. "
            # --- CORRECTED 2026-08-02 (c6-nasa-hump-the-only-last-place). This clause used to
            # read "No action is available for NASA_2DWMH regardless: no alternative
            # training-family model exists for it, ...". The first half was FALSE and is
            # withdrawn. CBFS13700 -- the curved backward-facing step, a 2D smooth-wall
            # separating-and-reattaching flow, i.e. the nearest flow in the benchmark to a
            # wall-mounted hump -- ships as TRAINING data with its 0/U_LES, 0/k_LES, 0/p_LES
            # and 0/tauij_LES fields, and is legal to fit on. The pre-registered argument
            # (train_closure_extended_correction.py lines 27-40) compared periodic hills
            # against DUCT only; CBFS is not named, not rejected, not mentioned. The second
            # half stands and is the only thing keeping the case shut. Record:
            # demo-output/website/closure_challenge_C6_hump_decision.md.
            f"What constrains NASA_2DWMH is WHO may choose and WHEN, not the absence of a "
            f"candidate: an alternative legal training family does exist (CBFS13700, shipped "
            f"as training data and physically nearer the hump than the periodic hills the "
            f"applied model was fitted on), but its correction choice was pre-registered in "
            f"round 2 before its test score was ever seen, and revisiting that choice now -- "
            f"having already seen its outcome -- would itself be the exact test-truth-informed "
            f"model selection the leakage rule forbids. Taking the CBFS route therefore "
            f"requires a pre-registration written and frozen before anything is scored; it is "
            f"not available as an unplanned action, which is a different and weaker statement "
            f"than 'no action is available'. "
            f"BOTTOM LINE: the criterion, applied strictly within the domain it was proven for, "
            f"changes nothing about the current entry, and there is no case for which it "
            f"identifies an available, leakage-clean action. Zero cases warrant a 5th official "
            f"scoring call on this evidence."
        ),
    }
    print("\n=== VERDICT ===")
    print(verdict["statement"])

    record = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "measured_date": str(date.today()),
        "purpose": "Apply the structural mismatch criterion to the 8 official test cases' "
                   "RANS-derived features, against the model currently applied to each in the "
                   "round-3 gated entry. A decision TABLE, not a decision -- nothing is applied, "
                   "no scoring call is made.",
        "leakage_statement": {
            "criterion_parameters_source": "recomputed from the same 21 PH / 4 DUCT TRAINING "
                "cases as closure_generalization_criterion.py via case_level_features() "
                "(deterministic aggregation, no model fit); reproduces that run's PH/DUCT "
                "training-regime bounds",
            "test_case_ground_truth_read": False,
            "closure_challenge_score_call_made": False,
            "correction_applied_or_changed": False,
            "known_actual_deltas_used_only_for": "sanity-checking the criterion's predictive "
                "meaning post hoc, against numbers already public from a legitimate prior "
                "official call -- never used to fit, threshold, or select anything in this "
                "script's criterion",
        },
        "due_diligence_correction": (
            "First pass used mean_I3_S3 and found NASA_2DWMH at +2.1e8, an implausible number "
            "given PH's training range of [-4.7e-4, +3.7e-5]. Investigated rather than reported "
            "at face value: traced to a real per-cell phenomenon (confirmed with the more robust "
            "p90 statistic, and with a full 15-feature domain-coverage check showing NASA_2DWMH "
            "is out of range on literally all 15 features, not selectively on I3/I4) but a "
            "DIFFERENT mechanism than the proven DUCT case -- see module docstring for the full "
            "account."
        ),
        "currently_applied_model_per_case": _CURRENTLY_APPLIED,
        "table": table,
        "verdict": verdict,
        "compute": {"elapsed_seconds": round(elapsed_s, 1), "cores_cap": 2},
    }

    _OUT.parent.mkdir(parents=True, exist_ok=True)
    _OUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"\nelapsed: {elapsed_s:.1f}s")
    print(f"Wrote {_OUT}")


if __name__ == "__main__":
    main()
