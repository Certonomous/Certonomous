"""Write the eight submittable Closure Challenge prediction CSVs, WITHOUT
making a scoring call.

WHY THIS SCRIPT EXISTS
----------------------
The lab's round-3 entry (overall 0.0676, per-case recorded in
demo-output/website/closure_challenge_trained_entry_round3_gated.json) was the
ENTRY OF RECORD WHEN THIS SCRIPT WAS WRITTEN, on 2026-07-30. It is not the
entry of record now: round 4 superseded it (0.0654, recorded 2026-07-31) and
round 5 superseded round 4 on 2026-08-07 (0.056647191704213645,
demo-output/website/closure_challenge_round5_qcr.json). This script stays
round-3 scoped on purpose -- reproducing that round's prediction set is the
whole of its job -- and the round-3 entry it reproduces had
only ever existed as an in-memory ``predictions`` dict and a JSON of scores.
apply_closure_ph_gate.py contains no CSV-writing code, so there has never
been a submittable artifact. This script reproduces that exact prediction
set and writes it to disk in the benchmark's required format.

THE REQUIRED FORMAT, confirmed against the four accepted submissions in the
benchmark repo (submissions/{wu,montoya,wang} at commit deb91557):
    one file per case, named ``{case}.csv``
    1000 rows x 3 columns (Ux, Uy, Uz), comma-delimited, NO header
This is also the layout the evaluation package's own loader expects:
``closure_challenge.eval._load_csv_predictions`` reads ``folder/f"{case}.csv"``
for each name in ``case_names()``.

NO SCORING CALL IS MADE, AND THAT IS ENFORCED IN CODE, NOT PROMISED IN PROSE
---------------------------------------------------------------------------
The benchmark imposes NO limit on scoring calls -- it ships the test ground
truth in the package and its README instructs submitters to preview their
score. The lab's scoring-call ledger ("four official scoring calls, ever" as
this round-3-era script was written; the cumulative count is six after round
5's 2026-08-07 call) is a SELF-IMPOSED
discipline, stricter than the rules require, and must never be described as
compliance with a benchmark rule. This script keeps that discipline: writing
a CSV of an already-scored prediction set buys no new information, so it must
not consume a new call.

Rather than merely omitting the calls, ``_forbid_scoring()`` below replaces
every function in the evaluation package that can read the test ground-truth
VELOCITIES -- score, score_from_csv, evaluate_by_case, evaluate_from_csv_by_case,
evaluate_individual_case, _velocity_field, _ground_truth -- with functions
that raise RuntimeError, in every namespace they are reachable from. If a
future edit ever reintroduces a scoring call here, this script dies instead of
quietly spending one.

``evaluation_points(case)`` IS still called, and it is not a scoring call: it
returns ``_ground_truth()[case]['coords']`` only, never ``['U']``. The task
statement requires it -- "predict the flow field for a series of test cases
given ... a given CFD mesh" -- and every submitter must interpolate to those
points. The guard therefore keeps a private, coords-only path open and blocks
every route to the velocities.

WHAT IS REPRODUCED
------------------
Stages 1 to 3 of apply_closure_ph_gate.py, byte-for-byte in behaviour:
  STAGE 1  refit the C1 gate on the 21 PH TRAIN cases only.
  STAGE 2  evaluate the frozen gate on the 4 PH TEST cases using RANS field +
           mesh features only (no U_LES for any test case is read).
  STAGE 3  assemble the 8-case predictions dict -- PH test cases gate-selected
           between the round-1 corrected prediction and the raw-RANS floor;
           DUCT and NASA_2DWMH reproduced exactly as round 2.
STAGE 4 (scoring) is deliberately absent.

VERIFICATION WITHOUT SCORING
----------------------------
The run is checked against the recorded round-3 JSON on quantities that owe
nothing to test ground truth: the harness commits, the refit alpha and
threshold (0.7499 / 0.1263), the top-3 screened feature names, and all four
gate decisions. If any of those drift, the CSVs are not the entry of record
and the script says so loudly. Shape and finiteness of every CSV are checked
directly. A manifest with a SHA-256 per file is written alongside.

Run (2-core cap, per current lab compute budget)::
    taskset -c 0-1 python sdk/scripts/export_closure_submission_csvs.py

Writes demo-output/website/closure_challenge_submission/test/{case}.csv (8 files)
   and demo-output/website/closure_challenge_submission/MANIFEST.json
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np

_SDK = Path(__file__).resolve().parent
_REPO = _SDK.parent.parent
sys.path.insert(0, str(_SDK))
import train_closure_periodic_hill_correction as ph   # round-1 script
import train_closure_extended_correction as ext        # round-2 script
import closure_baseline_error_gate as gate             # C1 gate

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

_OUTDIR = lab_paths.CLOSURE_SUBMISSION
_CSVDIR = _OUTDIR / "test"
_MANIFEST = _OUTDIR / "MANIFEST.json"
_ROUND3 = lab_paths.web_file(
    "closure_challenge_trained_entry_round3_gated.json")

BENCHMARK_DIR = ph.BENCHMARK_DIR
EVAL_PKG_DIR = ph.EVAL_PKG_DIR

# Submission CSV numeric format. The accepted submissions use 6 significant
# figures; 10 is used here so that rounding cannot move a reported digit.
_FMT = "%.10g"
_EXPECTED_ROWS = 1000
_EXPECTED_COLS = 3


class ScoringCallRefused(RuntimeError):
    """Raised if anything in this script tries to read test ground-truth
    velocities. This script exists precisely to avoid that."""


def _forbid_scoring(cc, du, ev) -> dict:
    """Disable every route from this process to the test ground-truth
    VELOCITIES, while leaving the coords-only evaluation-point lookup open.

    Returns a dict with the one private, coords-only accessor this script is
    allowed to use. Everything else raises."""
    real_ground_truth = du._ground_truth
    cached = real_ground_truth()

    def coords_only(case):
        """The only permitted read: evaluation-point coordinates."""
        return np.asarray(cached[case]["coords"])

    permitted_case_names = list(dict.fromkeys(cached.keys()))

    def _refuse(name):
        def _raiser(*_a, **_kw):
            raise ScoringCallRefused(
                f"{name}() was called by export_closure_submission_csvs.py. "
                "This script writes CSVs for an ALREADY-SCORED prediction set "
                "and must not consume a scoring call. Nothing here needs the "
                "test ground-truth velocities."
            )
        return _raiser

    blocked = ("score", "score_from_csv", "evaluate_by_case",
               "evaluate_from_csv_by_case", "evaluate_individual_case",
               "_velocity_field", "_ground_truth", "_load_csv_predictions")
    for mod in (cc, du, ev):
        for name in blocked:
            if hasattr(mod, name):
                setattr(mod, name, _refuse(name))

    return {"evaluation_points": coords_only, "case_names": permitted_case_names}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    t0 = time.time()
    if not BENCHMARK_DIR.exists():
        print(f"ERROR: benchmark scratch clone not found at {BENCHMARK_DIR}.", file=sys.stderr)
        sys.exit(1)
    if str(EVAL_PKG_DIR / "src") not in sys.path:
        sys.path.insert(0, str(EVAL_PKG_DIR / "src"))

    import closure_challenge as _cc
    from closure_challenge import dataset_utils as _du
    from closure_challenge import eval as _ev

    # ---- BEFORE ANY PIPELINE WORK: shut every door to the test velocities --
    permitted = _forbid_scoring(_cc, _du, _ev)
    evaluation_points = permitted["evaluation_points"]
    all_test_cases = set(permitted["case_names"])
    print("[guard] closure_challenge scoring functions disabled for this process; "
          "only evaluation-point coordinates are readable")

    # Prove the guard is armed rather than asserting it in a comment.
    try:
        _cc.score({})
    except ScoringCallRefused:
        print("[guard] verified: closure_challenge.score() now raises")
    else:  # pragma: no cover - defensive
        print("ERROR: the scoring guard is not armed. Refusing to continue.", file=sys.stderr)
        sys.exit(1)

    from Ofpp import parse_internal_field
    from scipy.interpolate import NearestNDInterpolator
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.linear_model import Ridge, RidgeCV

    # ---------------- CHECK 0: harness identical to rounds 1/2/3 -----------
    bench_commit = ext._git_commit(BENCHMARK_DIR)
    pkg_commit = ext._git_commit(EVAL_PKG_DIR)
    harness_matches = (
        bench_commit == ext._ROUND1_PROVENANCE["benchmark_repo_commit"]
        and pkg_commit == ext._ROUND1_PROVENANCE["eval_package_repo_commit"]
    )
    print(f"[check] harness identical to rounds 1/2/3 -> "
          f"{'MATCH' if harness_matches else 'MISMATCH'}")
    if not harness_matches:
        print("ERROR: harness mismatch; these CSVs would not be the entry of record.",
              file=sys.stderr)
        sys.exit(1)

    import os
    os.chdir(BENCHMARK_DIR)

    expected = set(ph._PH_TEST) | set(ph._OTHER_TEST_RANS.keys())
    assert expected == all_test_cases, (expected, all_test_cases)

    # =====================================================================
    # STAGE 1 -- reproduce the C1 gate, fit on the 21 PH TRAIN cases only.
    # =====================================================================
    case_feats, baseline_err = {}, {}
    for case in gate._PH_TRAIN:  # 21 cases, train only
        f = ph._load_rans_fields(case, parse_internal_field)
        u_true = ph._load_ground_truth_U(case, parse_internal_field)  # TRAIN truth
        X = ph.build_features(f["gradU"], f["k"], f["omega"], f["walldist"], f["U"], f["nu"])
        case_feats[case] = gate.case_level_features(X, f["U"])
        baseline_err[case] = ph.scaled_mae(f["U"], u_true)

    feature_names = sorted(next(iter(case_feats.values())).keys())
    Xtr = np.array([[case_feats[c][k] for k in feature_names] for c in gate._PH_TRAIN])
    ytr = np.array([baseline_err[c] for c in gate._PH_TRAIN])

    screening = {nm: gate.pearson_r(Xtr[:, j], ytr) for j, nm in enumerate(feature_names)}
    ranked = sorted(screening.items(), key=lambda kv: -abs(kv[1]))
    top3_names = [nm for nm, _ in ranked[:3]]
    top3_idx = [feature_names.index(nm) for nm in top3_names]

    mu = Xtr.mean(axis=0)
    sd = Xtr.std(axis=0)
    sd[sd < 1e-12] = 1.0
    Xtr_top3 = ((Xtr - mu) / sd)[:, top3_idx]

    cv_model = RidgeCV(alphas=np.logspace(-2, 3, 25), store_cv_results=True)
    cv_model.fit(Xtr_top3, ytr)
    chosen_alpha = float(cv_model.alpha_)

    loo_pred = np.zeros_like(ytr)
    for i in range(len(ytr)):
        mask = np.ones(len(ytr), dtype=bool)
        mask[i] = False
        m = Ridge(alpha=chosen_alpha)
        m.fit(Xtr_top3[mask], ytr[mask])
        loo_pred[i] = m.predict(Xtr_top3[i:i + 1])[0]
    threshold = float(np.median(loo_pred))

    final_gate_model = Ridge(alpha=chosen_alpha)
    final_gate_model.fit(Xtr_top3, ytr)
    print(f"[gate] alpha={chosen_alpha:.4f} threshold={threshold:.4f} "
          f"top3={top3_names}")

    # =====================================================================
    # STAGE 2 -- frozen gate on the 4 PH TEST cases, features only.
    # =====================================================================
    gate_decisions = {}
    for case in ph._PH_TEST:
        f = ph._load_rans_fields(case, parse_internal_field)  # no U_LES read
        X = ph.build_features(f["gradU"], f["k"], f["omega"], f["walldist"], f["U"], f["nu"])
        feats = gate.case_level_features(X, f["U"])
        x_top3 = (((np.array([[feats[k] for k in feature_names]])) - mu) / sd)[:, top3_idx]
        pred_baseline = float(final_gate_model.predict(x_top3)[0])
        gate_decisions[case] = {
            "predicted_baseline_error": round(pred_baseline, 4),
            "threshold": round(threshold, 4),
            "gate_says_apply_correction": bool(pred_baseline > threshold),
        }
        print(f"  {case:24s} predicted_baseline={pred_baseline:.4f} -> "
              f"{'APPLY' if gate_decisions[case]['gate_says_apply_correction'] else 'DECLINE'}")

    # =====================================================================
    # STAGE 3 -- assemble the 8-case predictions dict (round-3 gated entry).
    # =====================================================================
    floor_predictions = {}
    for case in ph._PH_TEST:
        f = ph._load_rans_fields(case, parse_internal_field)
        floor_predictions[case] = NearestNDInterpolator(f["C"], f["U"])(evaluation_points(case))
    for case, (case_path, time_dir, coord_sub) in ph._OTHER_TEST_RANS.items():
        coords = parse_internal_field(os.path.join(case_path, coord_sub))
        u_rans = parse_internal_field(os.path.join(case_path, time_dir, "U"))
        floor_predictions[case] = NearestNDInterpolator(coords, u_rans)(evaluation_points(case))

    # PH correction model, identical to rounds 1/2 (21 train cases, same
    # hyperparameters, random_state=0 -- deterministic).
    X_ph_parts, y_ph_parts = [], []
    for c in ph._PH_TRAIN:
        f = ph._load_rans_fields(c, parse_internal_field)
        X_ph_parts.append(ph.build_features(f["gradU"], f["k"], f["omega"],
                                            f["walldist"], f["U"], f["nu"]))
        y_ph_parts.append(ph._load_ground_truth_U(c, parse_internal_field) - f["U"])
    X_train_ph = np.concatenate(X_ph_parts, axis=0)
    y_train_ph = np.concatenate(y_ph_parts, axis=0)
    ph_models = [HistGradientBoostingRegressor(max_iter=300, max_depth=6,
                                               learning_rate=0.05,
                                               l2_regularization=1.0,
                                               random_state=0).fit(X_train_ph, y_train_ph[:, comp])
                 for comp in range(3)]

    def ph_predict_correction(X):
        return np.stack([m.predict(X) for m in ph_models], axis=1)

    predictions, ph_source = {}, {}
    for case in ph._PH_TEST:
        if gate_decisions[case]["gate_says_apply_correction"]:
            f = ph._load_rans_fields(case, parse_internal_field)
            Xc = ph.build_features(f["gradU"], f["k"], f["omega"], f["walldist"], f["U"], f["nu"])
            u_pred_mesh = f["U"] + ph_predict_correction(Xc)
            predictions[case] = NearestNDInterpolator(f["C"], u_pred_mesh)(evaluation_points(case))
            ph_source[case] = "corrected (round-1 PH model, gate says APPLY)"
        else:
            predictions[case] = floor_predictions[case]
            ph_source[case] = "raw RANS floor (gate says DECLINE)"

    # DUCT: reproduced exactly as round 2.
    X_parts, y_parts = [], []
    for case in ext._DUCT_TRAIN:
        f = ext._reconstruct_duct_fields(case, parse_internal_field)
        u_les = ext._load_duct_ground_truth_U(case, parse_internal_field)
        X_parts.append(ph.build_features(f["gradU"], f["k"], f["omega"],
                                         f["walldist"], f["U"], f["nu"]))
        y_parts.append(u_les - f["U"])
    X_train_duct = np.concatenate(X_parts, axis=0)
    y_train_duct = np.concatenate(y_parts, axis=0)
    duct_models = [HistGradientBoostingRegressor(max_iter=300, max_depth=6,
                                                 learning_rate=0.05,
                                                 l2_regularization=1.0,
                                                 random_state=0).fit(X_train_duct, y_train_duct[:, comp])
                   for comp in range(3)]

    for case in ext._DUCT_TEST:
        f = ext._reconstruct_duct_fields(case, parse_internal_field)
        X = ph.build_features(f["gradU"], f["k"], f["omega"], f["walldist"], f["U"], f["nu"])
        u_pred_mesh = f["U"] + np.stack([m.predict(X) for m in duct_models], axis=1)
        predictions[case] = NearestNDInterpolator(f["C"], u_pred_mesh)(evaluation_points(case))

    # NASA_2DWMH: PH model, unchanged from round 2.
    nasa_f = ext._reconstruct_nasa_fields("NASA_2DWMH", parse_internal_field)
    X_nasa = ph.build_features(nasa_f["gradU"], nasa_f["k"], nasa_f["omega"],
                               nasa_f["walldist"], nasa_f["U"], nasa_f["nu"])
    u_pred_nasa_mesh = nasa_f["U"] + ph_predict_correction(X_nasa)
    predictions["NASA_2DWMH"] = NearestNDInterpolator(nasa_f["C"],
                                                      u_pred_nasa_mesh)(evaluation_points("NASA_2DWMH"))

    assert set(predictions.keys()) == all_test_cases

    # =====================================================================
    # VERIFY AGAINST THE ENTRY OF RECORD -- no test truth involved.
    # =====================================================================
    r3 = json.loads(_ROUND3.read_text())
    rec_gate = r3["gate_refit_check"]
    rec_dec = r3["gate_decisions_on_official_ph_test_cases"]
    rec_src = r3["ph_prediction_source_per_case"]

    checks = {
        "benchmark_repo_commit_matches": bench_commit == r3["harness_check"]["benchmark_repo_commit"],
        "eval_package_repo_commit_matches": pkg_commit == r3["harness_check"]["eval_package_repo_commit"],
        "chosen_alpha_matches": round(chosen_alpha, 4) == rec_gate["chosen_alpha"],
        "threshold_matches": round(threshold, 4) == rec_gate["train_loo_median_threshold"],
        "top3_features_match": top3_names == rec_gate["top3_features"],
        "gate_decisions_match": all(
            gate_decisions[c]["gate_says_apply_correction"]
            == rec_dec[c]["gate_says_apply_correction"] for c in ph._PH_TEST),
        "gate_predicted_errors_match": all(
            gate_decisions[c]["predicted_baseline_error"]
            == rec_dec[c]["predicted_baseline_error"] for c in ph._PH_TEST),
        "ph_prediction_source_matches": ph_source == rec_src,
    }
    for k, v in checks.items():
        print(f"[verify] {k}: {'OK' if v else 'FAIL'}")
    if not all(checks.values()):
        print("ERROR: this run does not reproduce the round-3 entry of record. "
              "Refusing to write CSVs that would misrepresent the recorded score.",
              file=sys.stderr)
        sys.exit(1)

    # =====================================================================
    # WRITE THE EIGHT CSVs
    # =====================================================================
    _CSVDIR.mkdir(parents=True, exist_ok=True)
    files = {}
    for case in sorted(all_test_cases):
        arr = np.asarray(predictions[case], dtype=float)
        if arr.shape != (_EXPECTED_ROWS, _EXPECTED_COLS):
            print(f"ERROR: {case} has shape {arr.shape}, expected "
                  f"({_EXPECTED_ROWS}, {_EXPECTED_COLS}).", file=sys.stderr)
            sys.exit(1)
        if not np.isfinite(arr).all():
            print(f"ERROR: {case} contains non-finite values.", file=sys.stderr)
            sys.exit(1)
        path = _CSVDIR / f"{case}.csv"
        np.savetxt(path, arr, delimiter=",", fmt=_FMT)

        # Read the file back and confirm it parses to the same numbers under
        # the package's own loader semantics (np.loadtxt, comma, no header).
        back = np.loadtxt(path, delimiter=",")
        assert back.shape == (_EXPECTED_ROWS, _EXPECTED_COLS)
        max_roundtrip = float(np.max(np.abs(back - arr)))
        with path.open("r", encoding="utf-8") as fh:
            n_lines = sum(1 for _ in fh)
        files[case] = {
            "file": f"test/{case}.csv",
            "rows": n_lines,
            "cols": _EXPECTED_COLS,
            "has_header": False,
            "delimiter": ",",
            "sha256": _sha256(path),
            "max_roundtrip_abs_error": max_roundtrip,
            "prediction_source": ph_source.get(case, "round-2 trained correction, unchanged"),
        }
        print(f"[write] {path.name:26s} {n_lines} rows x {_EXPECTED_COLS} cols  "
              f"roundtrip<={max_roundtrip:.2e}")

    elapsed_s = time.time() - t0
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "measured_date": str(date.today()),
        "purpose": "The eight submittable prediction CSVs for the Closure Challenge, "
                   "reproducing the round-3 gated entry without making a "
                   "scoring call. Round 3 was the entry of record when this script "
                   "was written (2026-07-30); it is not now -- round 5 "
                   "(0.056647191704213645, scored 2026-08-07, "
                   "closure_challenge_round5_qcr.json) is.",
        "produced_by": "sdk/scripts/export_closure_submission_csvs.py",
        "reproduces": "demo-output/website/closure_challenge_trained_entry_round3_gated.json",
        "scoring_calls_made_by_this_run": 0,
        "how_zero_is_guaranteed": (
            "closure_challenge.score, score_from_csv, evaluate_by_case, "
            "evaluate_from_csv_by_case, evaluate_individual_case, _velocity_field, "
            "_ground_truth and _load_csv_predictions were all replaced with "
            "raising stubs in the closure_challenge, dataset_utils and eval "
            "namespaces BEFORE any pipeline work, and the guard was proven armed "
            "by calling score() and catching the refusal. Only evaluation-point "
            "COORDINATES were read; no test-case ground-truth velocity was "
            "readable from this process."
        ),
        "scoring_call_limit_note": (
            "The benchmark imposes no scoring-call limit. It ships the test ground "
            "truth in the evaluation package and instructs submitters to preview "
            "their score. The lab's scoring-call ledger (\"four-calls-ever\" as this "
            "round-3-era script was written; the cumulative count is six after "
            "round 5's 2026-08-07 call, so the next one would be the 7th) is a "
            "self-imposed "
            "discipline, stricter than the rules require, and is not compliance "
            "with any benchmark rule."
        ),
        "format": {
            "layout": "flat {case}.csv inside a test/ directory",
            "precedent": "matches accepted submissions wu, montoya and wang at "
                         "benchmark commit deb91557",
            "rows": _EXPECTED_ROWS,
            "cols": _EXPECTED_COLS,
            "header": None,
            "delimiter": ",",
            "numeric_format": _FMT,
        },
        "harness": {
            "benchmark_repo_commit": bench_commit,
            "eval_package_repo_commit": pkg_commit,
            "eval_package_version_string_note": (
                "The package's __init__ reports __version__ = '0.2.1' while "
                "pyproject.toml at this commit declares 0.3.1 ('v0.3.1: vector "
                "magnitude metric, mean over cases'). Upstream never bumped "
                "__version__. Cite the commit hash, not the version string."
            ),
        },
        "gate_refit_check": {
            "chosen_alpha": round(chosen_alpha, 4),
            "train_loo_median_threshold": round(threshold, 4),
            "top3_features": top3_names,
        },
        "gate_decisions_on_official_ph_test_cases": gate_decisions,
        "verification_against_entry_of_record": checks,
        "recorded_scores_not_recomputed_here": {
            "overall": r3["official_test_harness_result"]["round3_gated_overall"],
            "per_case": r3["official_test_harness_result"]["round3_gated_per_case"],
            "source": "closure_challenge_trained_entry_round3_gated.json (round-3 run)",
        },
        "files": files,
        "compute": {"elapsed_seconds": round(elapsed_s, 1), "cores_cap": 2},
    }
    _MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"\nelapsed: {elapsed_s:.1f}s")
    print(f"Wrote 8 CSVs to {_CSVDIR}")
    print(f"Wrote {_MANIFEST}")
    print("Scoring calls made by this run: 0 (enforced, not merely omitted).")


if __name__ == "__main__":
    main()
