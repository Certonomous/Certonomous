"""Round-5 CANDIDATE: a regime-specific correction model for the gate-declined
("alpha_05") periodic-hills regime. TRAINS AND VALIDATES ONLY. NO SCORING.

CONTEXT (demo-output/website/closure_challenge_C2_error_decomposition.md,
"Recommended next action"): the round-3/4 entry declines the PH correction on
the two alpha_05 test cases because the C1 gate predicts their raw-RANS
baseline is already good and the global PH model hurts such cases (+0.0262,
+0.0255 at round 2). Declining banked C2's 0.0066 recoverable term; this
script builds the strictly-better option C2 recommends: a second model TRAINED
on the low-baseline-error regime, so the decline branch can submit a genuine
correction instead of raw RANS.

WHAT "alpha_05 REGIME" MEANS HERE (decided from C2's addendum, not the case
names): C2 falsified the alpha-naming framing -- the training split already
contains five alpha_05 cases and the global model still hurts alpha_05 at
test; NASA_2DWMH (not a hill) sits in the same degraded group. The framing
that survives is BASELINE QUALITY: the global correction hurts where raw RANS
is already good. Operationally the regime is therefore defined by the SAME
frozen C1 gate that makes the test-time decision: a case is in-regime iff the
gate's predicted baseline error <= the train-LOO-median threshold (0.1263).
That is exactly the population the regime model would ever be applied to.

TWO MEMBERSHIP VARIANTS (they disagree on 2 of 21 training cases; both are
built and the choice is made on held-out evidence under rules declared below,
BEFORE any correction delta was computed):
  A (deployment-symmetric): train on cases whose gate LOO-predicted baseline
    <= 0.1263 -- matches the feature distribution the model faces at test.
  B (semantic): train on cases whose ACTUAL baseline scaled-MAE <= 0.1263 --
    matches the mechanism (learn small corrections from cases that only need
    small corrections; A admits alpha_10_9000_2024 whose actual baseline is
    0.1799).
Training ground truth for train/validation cases is legitimate (round 1 and
C1 both read it); membership uses LOO predictions for training cases because
the final gate's in-sample predictions would be optimistic.

MODEL: identical architecture and hyperparameters to round 1
(HistGradientBoostingRegressor x3, max_iter=300, max_depth=6, lr=0.05,
l2_regularization=1.0, random_state=0). Nothing is tuned.

HELD-OUT EVALUATION (all training-family, never a test case):
  1. Leave-one-case-out over each variant's training set: hold out one case,
     train on the rest, compare corrected vs raw-RANS scaled-MAE on the
     held-out case.
  2. The single gate-declined validation case alpha_05_10071_4048 (final
     models, trained on their full membership sets, applied to a case no
     variant ever fit on).

SELECTION AND GO/NO-GO RULES, DECLARED BEFORE ANY DELTA EXISTED:
  - Comparison set: the 10 cases in BOTH memberships (apples-to-apples), each
    evaluated under its LOO model, plus the validation case.
  - Select the variant with the lower mean LOO delta (corrected - baseline)
    over the comparison set.
  - GO (carry to a round-5 pre-registration) iff the selected variant:
      (i)   improves the validation case vs raw RANS (delta < 0),
      (ii)  has mean LOO delta < 0 over the comparison set,
      (iii) hurts no comparison-set case by more than +0.010.
    Otherwise NO-GO: gating stands as the honest route and this record
    documents the negative result. The rules are not revisited after the
    numbers exist.

LEAKAGE POSITION: this script never imports closure_challenge, never reads a
file belonging to any of the 8 test cases, and makes no scoring call of any
kind. The only ground truth read is U_LES for the 21 train + 4 validation PH
cases, exactly as round 1 and C1 already do.

Run (2-core cap, lab convention)::
    source ~/closure-venv/bin/activate
    taskset -c 0-1 python sdk/scripts/train_closure_alpha05_regime_model.py

Writes demo-output/website/closure_challenge_alpha05_regime_model.json.
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
import train_closure_periodic_hill_correction as ph  # round-1 conventions
import closure_baseline_error_gate as gate           # C1 feature aggregation

_OUT = _REPO / "demo-output" / "website" / "closure_challenge_alpha05_regime_model.json"

_VAL_IN_REGIME = "alpha_05_10071_4048"  # the one gate-declined validation case
_HURT_CAP = 0.010                        # rule (iii)

_HGB_KW = dict(max_iter=300, max_depth=6, learning_rate=0.05,
               l2_regularization=1.0, random_state=0)


def main() -> None:
    t0 = time.time()
    from Ofpp import parse_internal_field
    from sklearn.ensemble import HistGradientBoostingRegressor
    from sklearn.linear_model import Ridge, RidgeCV

    import os
    os.chdir(ph.BENCHMARK_DIR)

    # ---- guard: this process must never open a test-case path ------------
    _test_fragments = [f"/{c}/" for c in ph._PH_TEST] + \
                      [p for (p, _, _) in ph._OTHER_TEST_RANS.values()]
    _real_open = open

    def _guarded_open(file, *a, **kw):
        s = str(file)
        for frag in _test_fragments:
            if frag in s:
                raise PermissionError(f"TEST-BLIND GUARD: refused to open {s}")
        return _real_open(file, *a, **kw)

    import builtins
    builtins.open = _guarded_open
    print("[guard] armed: any attempt to open a test-case path raises")

    # ---- load features, targets, baselines for 21 train + 4 val ----------
    cells, case_feats, baseline = {}, {}, {}
    for case in ph._PH_TRAIN + ph._PH_VAL:
        f = ph._load_rans_fields(case, parse_internal_field)
        u_true = ph._load_ground_truth_U(case, parse_internal_field)
        X = ph.build_features(f["gradU"], f["k"], f["omega"], f["walldist"], f["U"], f["nu"])
        cells[case] = dict(X=X, U=f["U"], y=u_true - f["U"], u_true=u_true)
        case_feats[case] = gate.case_level_features(X, f["U"])
        baseline[case] = ph.scaled_mae(f["U"], u_true)

    # ---- reproduce the frozen C1 top-3 gate byte-for-byte -----------------
    names = sorted(next(iter(case_feats.values())).keys())
    Xtr = np.array([[case_feats[c][k] for k in names] for c in ph._PH_TRAIN])
    ytr = np.array([baseline[c] for c in ph._PH_TRAIN])
    screening = {nm: gate.pearson_r(Xtr[:, j], ytr) for j, nm in enumerate(names)}
    ranked = sorted(screening.items(), key=lambda kv: -abs(kv[1]))
    top3 = [nm for nm, _ in ranked[:3]]
    idx = [names.index(nm) for nm in top3]
    mu, sd = Xtr.mean(0), Xtr.std(0)
    sd[sd < 1e-12] = 1.0
    Xs = ((Xtr - mu) / sd)[:, idx]
    cv = RidgeCV(alphas=np.logspace(-2, 3, 25), store_cv_results=True)
    cv.fit(Xs, ytr)
    alpha = float(cv.alpha_)
    loo_pred = np.zeros_like(ytr)
    for i in range(len(ytr)):
        m = np.ones(len(ytr), bool)
        m[i] = False
        r = Ridge(alpha=alpha)
        r.fit(Xs[m], ytr[m])
        loo_pred[i] = r.predict(Xs[i:i + 1])[0]
    thr = float(np.median(loo_pred))
    gate_reproduced = (round(alpha, 4) == 0.7499 and round(thr, 4) == 0.1263)
    print(f"[gate] refit: top3={top3} alpha={alpha:.4f} thr={thr:.4f} "
          f"-> {'MATCHES C1/round-3 recorded values' if gate_reproduced else 'MISMATCH'}")
    if not gate_reproduced:
        print("ERROR: gate refit does not reproduce the frozen C1 gate; refusing to "
              "define regime membership from a drifted gate.", file=sys.stderr)
        sys.exit(1)

    final_gate = Ridge(alpha=alpha)
    final_gate.fit(Xs, ytr)

    def gate_predict(case: str) -> float:
        x = np.array([[case_feats[case][k] for k in names]])
        return float(final_gate.predict(((x - mu) / sd)[:, idx])[0])

    # ---- regime membership -------------------------------------------------
    loo_by_case = {c: float(loo_pred[i]) for i, c in enumerate(ph._PH_TRAIN)}
    members_A = [c for c in ph._PH_TRAIN if loo_by_case[c] <= thr]
    members_B = [c for c in ph._PH_TRAIN if baseline[c] <= thr]
    comparison_set = sorted(set(members_A) & set(members_B))
    val_gate_pred = gate_predict(_VAL_IN_REGIME)
    assert val_gate_pred <= thr, "validation case is expected to be gate-declined"
    print(f"[regime] A (gate LOO <= thr): {len(members_A)} cases; "
          f"B (actual baseline <= thr): {len(members_B)} cases; "
          f"comparison set: {len(comparison_set)}")
    print(f"[regime] A-only: {sorted(set(members_A) - set(members_B))}; "
          f"B-only: {sorted(set(members_B) - set(members_A))}")

    # ---- train/evaluate helpers -------------------------------------------
    def fit_models(case_list):
        X = np.concatenate([cells[c]["X"] for c in case_list], axis=0)
        y = np.concatenate([cells[c]["y"] for c in case_list], axis=0)
        models = []
        for comp in range(3):
            m = HistGradientBoostingRegressor(**_HGB_KW)
            m.fit(X, y[:, comp])
            models.append(m)
        return models

    def corrected_mae(models, case):
        d = np.stack([m.predict(cells[case]["X"]) for m in models], axis=1)
        return ph.scaled_mae(cells[case]["U"] + d, cells[case]["u_true"])

    variants = {}
    for tag, members in (("A_gate_symmetric", members_A), ("B_actual_baseline", members_B)):
        loo_rows = {}
        for held in members:
            rest = [c for c in members if c != held]
            models = fit_models(rest)
            corr = corrected_mae(models, held)
            loo_rows[held] = {
                "baseline": round(baseline[held], 4),
                "loo_corrected": round(corr, 4),
                "delta": round(corr - baseline[held], 4),
            }
            print(f"[LOO {tag}] {held:24s} baseline={baseline[held]:.4f} "
                  f"corrected={corr:.4f} delta={corr - baseline[held]:+.4f}")
        final_models = fit_models(members)
        val_corr = corrected_mae(final_models, _VAL_IN_REGIME)
        comp_deltas = [loo_rows[c]["delta"] for c in comparison_set]
        variants[tag] = {
            "members": members,
            "n_train_cells": int(sum(cells[c]["X"].shape[0] for c in members)),
            "loo": loo_rows,
            "comparison_set_mean_delta": round(float(np.mean(comp_deltas)), 4),
            "comparison_set_max_delta": round(float(np.max(comp_deltas)), 4),
            "validation_case": {
                "case": _VAL_IN_REGIME,
                "raw_rans_baseline": round(baseline[_VAL_IN_REGIME], 4),
                "global_round1_model_recorded": 0.0772,
                "regime_corrected": round(val_corr, 4),
                "delta_vs_baseline": round(val_corr - baseline[_VAL_IN_REGIME], 4),
            },
        }
        print(f"[{tag}] comparison-set mean delta {variants[tag]['comparison_set_mean_delta']:+.4f}, "
              f"max {variants[tag]['comparison_set_max_delta']:+.4f}; "
              f"validation {_VAL_IN_REGIME}: {val_corr:.4f} vs baseline "
              f"{baseline[_VAL_IN_REGIME]:.4f} ({val_corr - baseline[_VAL_IN_REGIME]:+.4f})")

    # ---- selection + GO/NO-GO under the pre-declared rules -----------------
    order = sorted(variants, key=lambda t: variants[t]["comparison_set_mean_delta"])
    selected = order[0]
    sel = variants[selected]
    rule_i = sel["validation_case"]["delta_vs_baseline"] < 0
    rule_ii = sel["comparison_set_mean_delta"] < 0
    rule_iii = sel["comparison_set_max_delta"] <= _HURT_CAP
    go = bool(rule_i and rule_ii and rule_iii)
    print(f"\n[selection] {selected} (mean deltas: "
          f"{ {t: v['comparison_set_mean_delta'] for t, v in variants.items()} })")
    print(f"[go/no-go] (i) validation improves: {rule_i}; (ii) mean LOO delta < 0: "
          f"{rule_ii}; (iii) max LOO delta <= +{_HURT_CAP}: {rule_iii} -> "
          f"{'GO' if go else 'NO-GO'}")

    elapsed = time.time() - t0
    record = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "measured_date": str(date.today()),
        "purpose": "Round-5 CANDIDATE only: regime-specific PH correction for the "
                   "gate-declined (low-predicted-baseline) regime, per C2's recommended "
                   "next action. Trained and validated on training-family data only; "
                   "NO scoring call, NO test-case file opened (open() guard armed).",
        "regime_definition": {
            "framing": "baseline quality, not alpha naming (C2's corrected framing): "
                       "in-regime iff the frozen C1 top-3 gate predicts baseline "
                       "scaled-MAE <= the train-LOO-median threshold",
            "gate_features": top3,
            "gate_alpha": round(alpha, 4),
            "threshold": round(thr, 4),
            "gate_refit_matches_c1_and_round3": gate_reproduced,
            "train_membership_uses": "LOO predictions (final-gate in-sample predictions "
                                      "would be optimistic)",
        },
        "train_case_table": {
            c: {"actual_baseline": round(baseline[c], 4),
                "gate_loo_pred": round(loo_by_case[c], 4),
                "in_A": c in members_A, "in_B": c in members_B}
            for c in ph._PH_TRAIN
        },
        "validation_case_gate_decisions": {
            c: {"actual_baseline": round(baseline[c], 4),
                "gate_pred": round(gate_predict(c), 4),
                "declined": gate_predict(c) <= thr}
            for c in ph._PH_VAL
        },
        "model": "HistGradientBoostingRegressor x3, identical hyperparameters to round 1 "
                 "(max_iter=300, max_depth=6, lr=0.05, l2=1.0, random_state=0); nothing tuned",
        "selection_rules_declared_before_any_delta_existed": {
            "comparison_set": comparison_set,
            "select": "lower mean LOO delta over the comparison set",
            "go_iff": [
                "(i) validation case delta < 0 vs raw RANS",
                "(ii) mean LOO delta < 0 over comparison set",
                f"(iii) no comparison-set LOO delta > +{_HURT_CAP}",
            ],
        },
        "variants": variants,
        "selected_variant": selected,
        "go_no_go": {
            "rule_i_validation_improves": bool(rule_i),
            "rule_ii_mean_loo_negative": bool(rule_ii),
            "rule_iii_hurt_cap": bool(rule_iii),
            "decision": "GO" if go else "NO-GO",
        },
        "leakage_statement": {
            "closure_challenge_imported": False,
            "scoring_calls_made": 0,
            "test_case_files_opened": 0,
            "open_guard": "builtins.open wrapped to raise on any test-case path; "
                          "armed before any data was read",
            "ground_truth_read_for": "21 train + 4 validation PH cases only "
                                      "(round-1/C1 precedent)",
        },
        "compute": {
            "elapsed_seconds": round(elapsed, 1),
            "cores_cap": 2,
            "core_minutes_upper_bound": round(elapsed * 2 / 60.0, 1),
        },
    }
    _OUT.parent.mkdir(parents=True, exist_ok=True)
    with _real_open(_OUT, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(record, indent=2) + "\n")
    print(f"\nelapsed {elapsed:.1f}s; wrote {_OUT}")


if __name__ == "__main__":
    main()
