"""Round 4: replace ONLY the three DUCT predictions with variant D, leave the
other five cases byte-identical to the entry of record, and score once.

WHAT CHANGES AND WHAT DOES NOT
------------------------------
The five non-duct CSVs (four periodic hills, NASA_2DWMH) are COPIED from
demo-output/website/closure_challenge_submission/test/ without being
regenerated, and their SHA-256 is asserted unchanged against that
submission's MANIFEST.json.  Nothing about the round-3 decline gate, the
periodic-hill model or the NASA prediction is touched, so any change in the
overall score is attributable to the duct family alone.

THE DUCT MODEL
--------------
Variant D, as diagnosed and validated in closure_duct_reynolds_transfer.py:
  * eighth feature `d/d_max` -- wall distance over the case's own maximum wall
    distance.  Purely geometric, exactly Reynolds-invariant, mesh-only.
  * target regressed as `(U_LES - U_RANS) / mean|U_RANS|` and multiplied back
    by the TARGET case's own mean |U_RANS| at prediction time.
Estimator and hyperparameters are unchanged from the entry of record.
Trained on the benchmark's own four suggested duct training cases.

PRE-REGISTRATION.  Variant D was selected before this script existed, on the
benchmark's own suggested duct validation case AR_7_Ret_180 (0.01345 against
the entry's 0.02032, floor 0.08073), tie-broken on leave-one-duct-out mean.
That selection is recorded in
demo-output/website/closure_challenge_duct_reynolds_transfer.json, written and
committed BEFORE any test score for it was ever computed.  No test-case
outcome influenced the choice, and no alternative variant will be scored
against the test set and then chosen.

LEAKAGE.  Ground truth is read for the four suggested duct training cases
only.  The three duct test cases are opened for their RANS field and mesh
alone -- `_load_duct_ground_truth_U` is never called on them, asserted in
code below.  `evaluation_points()` returns coordinates only and is not a
scoring call.

SCORING.  Exactly one new prediction set is scored: official call #5 under the
unit the ledger has always counted, distinct prediction sets scored.  The
benchmark imposes NO scoring-call limit; this ledger is a self-imposed
discipline and must never be described as compliance with one.

Run (2-core cap)::
    OMP_NUM_THREADS=2 taskset -c 0-1 \
        /home/ubuntu/closure-venv/bin/python \
        sdk/scripts/closure_round4_duct_rescale.py

Writes demo-output/website/closure_challenge_trained_entry_round4_duct.json
and the eight CSVs under
demo-output/website/closure_challenge_submission_round4/test/.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

_SDK = Path(__file__).resolve().parent
_REPO = _SDK.parent.parent
sys.path.insert(0, str(_SDK))
import train_closure_extended_correction as ex  # noqa: E402
import train_closure_periodic_hill_correction as ph  # noqa: E402

import Ofpp  # noqa: E402
from sklearn.ensemble import HistGradientBoostingRegressor  # noqa: E402
from scipy.interpolate import NearestNDInterpolator  # noqa: E402

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

_ENTRY_DIR = lab_paths.CLOSURE_SUBMISSION / "test"
_ENTRY_MANIFEST = lab_paths.CLOSURE_SUBMISSION / "MANIFEST.json"
_OUT_DIR = lab_paths.CLOSURE_SUBMISSION_ROUND4 / "test"
_OUT_JSON = lab_paths.web_file(
    "closure_challenge_trained_entry_round4_duct.json")
_ROUND3 = lab_paths.web_file(
    "closure_challenge_trained_entry_round3_gated.json")

_FMT = "%.10g"
HP = dict(max_iter=300, max_depth=6, learning_rate=0.05,
          l2_regularization=1.0, random_state=0)

DUCT_TRAIN = ex._DUCT_TRAIN
DUCT_TEST = ex._DUCT_TEST
UNCHANGED = ["alpha_15_13929_4048", "alpha_15_13929_2024",
             "alpha_05_4071_4048", "alpha_05_4071_2024", "NASA_2DWMH"]

assert not (set(DUCT_TRAIN) & set(DUCT_TEST))
assert len(UNCHANGED) + len(DUCT_TEST) == 8


def _parse(p):
    return Ofpp.parse_internal_field(str(p))


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _features(f):
    X7 = ph.build_features(f["gradU"], f["k"], f["omega"], f["walldist"], f["U"], f["nu"])
    d = f["walldist"]
    return np.hstack([X7, (d / d.max())[:, None]])


def main() -> None:
    import closure_challenge as cc

    rec: dict = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose": ("Round 4: DUCT-only change. Variant D (Reynolds-invariant d/d_max "
                    "feature + velocity-scale-normalised target) replaces the round-2/3 "
                    "duct model. The five non-duct predictions are byte-identical to the "
                    "entry of record."),
        "pre_registration": (
            "Variant D was selected on the benchmark's own suggested duct validation case "
            "AR_7_Ret_180 and recorded in closure_challenge_duct_reynolds_transfer.json, "
            "committed before any test score for it existed. No test outcome influenced it."),
    }

    # ------------------------------------------------------------------
    # 1. Train variant D on the four suggested duct TRAINING cases only.
    # ------------------------------------------------------------------
    Xs, Ys = [], []
    for c in DUCT_TRAIN:
        f = ex._reconstruct_duct_fields(c, _parse)
        u_les = ex._load_duct_ground_truth_U(c, _parse)
        uref = float(np.linalg.norm(f["U"], axis=1).mean())
        Xs.append(_features(f))
        Ys.append((u_les - f["U"]) / uref)
    X = np.concatenate(Xs)
    Y = np.concatenate(Ys)
    print(f"duct training matrix {X.shape} over {DUCT_TRAIN}")
    models = [HistGradientBoostingRegressor(**HP).fit(X, Y[:, j]) for j in range(3)]
    rec["duct_training"] = {"cases": DUCT_TRAIN, "n_cells": int(X.shape[0]),
                            "n_features": int(X.shape[1]),
                            "target": "(U_LES - U_RANS) / mean|U_RANS| per case"}

    # ------------------------------------------------------------------
    # 2. Predict the three duct TEST cases. RANS + mesh only.
    # ------------------------------------------------------------------
    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    duct_pred = {}
    for c in DUCT_TEST:
        f = ex._reconstruct_duct_fields(c, _parse)          # no ground-truth read
        uref = float(np.linalg.norm(f["U"], axis=1).mean())
        d = np.column_stack([m.predict(_features(f)) for m in models]) * uref
        u_mesh = f["U"] + d
        pts = cc.evaluation_points(c)                        # coordinates only
        duct_pred[c] = NearestNDInterpolator(f["C"], u_mesh)(pts)
        assert duct_pred[c].shape == (1000, 3), f"{c}: {duct_pred[c].shape}"
        # isfinite assert added 2026-08-05 (audit finding G4: this script
        # originally asserted shape only; the audit ran the finiteness check
        # externally). The submission-dir manifest is written separately by
        # sdk/scripts/closure_round4_manifest.py, which makes no scoring call.
        assert np.isfinite(duct_pred[c]).all(), f"{c}: non-finite prediction values"
        np.savetxt(_OUT_DIR / f"{c}.csv", duct_pred[c], delimiter=",", fmt=_FMT)
        print(f"  {c:18s} Uref={uref:8.4f}  mean|dU|={np.linalg.norm(d,axis=1).mean():.5f}"
              f"  ratio to Uref={np.linalg.norm(d,axis=1).mean()/uref:.5f}")

    # ------------------------------------------------------------------
    # 3. Copy the five unchanged CSVs and prove they are unchanged.
    # ------------------------------------------------------------------
    manifest = json.loads(_ENTRY_MANIFEST.read_text())
    entry_hashes = {}
    for k, v in manifest.items():
        if isinstance(v, dict):
            for kk, vv in v.items():
                if isinstance(vv, str) and len(vv) == 64:
                    entry_hashes[kk.replace(".csv", "")] = vv
                elif isinstance(vv, dict) and "sha256" in vv:
                    entry_hashes[kk.replace(".csv", "")] = vv["sha256"]
    copied = {}
    for c in UNCHANGED:
        src = _ENTRY_DIR / f"{c}.csv"
        dst = _OUT_DIR / f"{c}.csv"
        shutil.copyfile(src, dst)
        h = _sha256(dst)
        copied[c] = h
        if c in entry_hashes:
            assert h == entry_hashes[c], f"{c}: copied CSV hash differs from the entry manifest"
    rec["unchanged_cases_sha256"] = copied
    rec["unchanged_cases_verified_against_entry_manifest"] = sorted(
        set(UNCHANGED) & set(entry_hashes))
    print(f"copied 5 unchanged CSVs; "
          f"{len(rec['unchanged_cases_verified_against_entry_manifest'])} hash-verified "
          f"against the entry manifest")

    # ------------------------------------------------------------------
    # 4. Score once.  Official call #5.
    # ------------------------------------------------------------------
    per_case = cc.evaluate_from_csv_by_case(str(_OUT_DIR))
    overall = cc.score_from_csv(str(_OUT_DIR))
    per_case = {k: float(v) for k, v in per_case.items()}
    overall = float(overall)

    r3 = json.loads(_ROUND3.read_text())["official_test_harness_result"]
    prev = r3["round3_gated_per_case"]
    floor = r3["rans_identity_floor_per_case_this_run"]

    rec["official_test_harness_result"] = {
        "round4_overall": round(overall, 4),
        "round4_overall_full": overall,
        "round4_per_case": {k: round(v, 4) for k, v in per_case.items()},
        "round3_overall": r3["round3_gated_overall"],
        "round3_per_case": prev,
        "rans_identity_floor_per_case": floor,
        "delta_vs_round3": round(overall - r3["round3_gated_overall"], 4),
        "improves_on_round3": overall < r3["round3_gated_overall"],
    }
    rec["scoring_calls"] = {
        "this_run": 1,
        "cumulative_distinct_prediction_sets_scored": 5,
        "note": ("The benchmark imposes NO scoring-call limit and instructs submitters to "
                 "preview their score. This ledger is a self-imposed discipline, not "
                 "compliance with a rule."),
    }

    print("\n" + "=" * 74)
    print(f"{'case':22s} {'floor':>9s} {'round3':>9s} {'round4':>9s} {'delta':>9s}")
    for c in cc.case_names():
        dlt = per_case[c] - prev[c]
        mark = "  <- duct" if c in DUCT_TEST else ""
        print(f"{c:22s} {floor[c]:9.4f} {prev[c]:9.4f} {per_case[c]:9.4f} {dlt:+9.4f}{mark}")
    print(f"{'OVERALL':22s} {0.1036:9.4f} {r3['round3_gated_overall']:9.4f} "
          f"{overall:9.4f} {overall - r3['round3_gated_overall']:+9.4f}")
    print("=" * 74)

    _OUT_JSON.write_text(json.dumps(rec, indent=2))
    print(f"\nwrote {_OUT_JSON}")


if __name__ == "__main__":
    main()
