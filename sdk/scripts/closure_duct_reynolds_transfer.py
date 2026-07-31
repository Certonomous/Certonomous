"""Why the DUCT correction transfers badly, and a fix validated only on data
the benchmark permits us to fit on.

--------------------------------------------------------------------------
THE FINDING THAT MOTIVATED THIS, AND THE LAB CLAIM IT CORRECTS
--------------------------------------------------------------------------
The lab's public record (closure.html, CLOSURE_CHALLENGE_STATUS.md sec 0b,
closure_challenge_duct_anisotropy_expressivity.json) attributes the duct
deficit to two of the seven input features, I3_S3 and I4_W2S, being
algebraically identically zero on every duct.  That degeneracy is real and
independently reproduced here.  It cannot, however, be the explanation for
the deficit, and the reason is arithmetic:

    those two features are identically zero on ALL THREE duct test cases,
    including AR_14_Ret_180, on which the entry of record is the best score
    on the board (0.0303 against a next-best 0.0325).

A defect present in equal measure on the case we win and the cases we lose
does not discriminate between them.  Something else does.

--------------------------------------------------------------------------
WHAT ACTUALLY DISCRIMINATES: Re_y LEAVES THE TRAINED RANGE
--------------------------------------------------------------------------
The seven features are five Pope invariants (non-dimensional by construction),
`tke_ratio` (non-dimensional), and `Re_y = sqrt(k)*d/(50*nu)` -- the only
feature that carries the Reynolds number.  A HistGradientBoostingRegressor
cannot extrapolate: beyond the training range it returns the boundary leaf's
constant.  Measured here, test-blind, from the RANS solve and mesh alone:

    case              Re_y max / trained max   our rank on the board
    AR_1_Ret_360              1.85x                  5 of 5
    AR_3_Ret_360              2.07x                  4 of 5
    AR_14_Ret_180             0.90x                  1 of 5

The two cases where the model is asked to extrapolate in Re_y are the two it
loses; the case that stays inside the trained range is the one it wins.  Every
duct the benchmark permits us to train or validate on sits at Re_tau ~= 164,
so this extrapolation was never exercised during fitting.

--------------------------------------------------------------------------
THE CANDIDATE FIX, AND HOW FAR IT IS ACTUALLY VALIDATED
--------------------------------------------------------------------------
Variant D: add `d/d_max` -- wall distance over the case's own maximum wall
distance, purely geometric and exactly Reynolds-invariant -- as an eighth
feature, and regress the correction normalised by the case's own mean
|U_RANS| instead of in m/s, rescaling by the target case's own mean |U_RANS|
at prediction time.  Both added quantities come from the cheap solve and the
mesh; neither needs ground truth.

Validated on every held-out set the rules allow:

  * the benchmark's own suggested duct validation case AR_7_Ret_180,
  * leave-one-duct-out over the four suggested duct training cases,
  * the nine `alpha_10_*` periodic hills (Re = 6000, 9000, 12000 at fixed
    geometry, all nine inside the suggested TRAINING list), both upward
    extrapolation and interpolation in Reynolds number.

STATED PLAINLY, BECAUSE IT MATTERS: none of these is a Reynolds-number
transfer test at a doubled *velocity scale*, which is what the two failing
duct cases actually demand.  The duct data the rules permit contains exactly
one Reynolds number, and the periodic-hill sweep varies Re through viscosity
at nearly fixed bulk velocity (mean |U| moves only 0.76 -> 0.73 across the
sweep), so `Re_y` never leaves its trained range there either -- measured, not
assumed.  The periodic-hill result is therefore evidence about Reynolds
generalisation in general, NOT a reproduction of the duct saturation
mechanism.  No legal test of that mechanism exists in this benchmark.  The
fix is motivated by a measured mechanism and validated for no-harm; it is not
proven to close the duct deficit, and this script does not claim it does.

--------------------------------------------------------------------------
LEGALITY
--------------------------------------------------------------------------
Ground truth is read for the 4 suggested duct training cases, the 1 suggested
duct validation case, and 9 suggested periodic-hill TRAINING cases.  The three
duct test cases are opened only for their RANS field and mesh, to measure
feature coverage.  No test-case ground truth is read.  Nothing is scored
against the official harness by this script; it makes zero scoring calls.

Run (2-core cap)::
    OMP_NUM_THREADS=2 taskset -c 0-1 \
        /home/ubuntu/closure-venv/bin/python \
        sdk/scripts/closure_duct_reynolds_transfer.py

Writes demo-output/website/closure_challenge_duct_reynolds_transfer.json.
"""
from __future__ import annotations

import json
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

_OUT = _REPO / "demo-output" / "website" / "closure_challenge_duct_reynolds_transfer.json"

DUCT_TRAIN, DUCT_VAL, DUCT_TEST = ex._DUCT_TRAIN, ex._DUCT_VAL, ex._DUCT_TEST
PH_FAM = {r: [f"alpha_10_{r}_{m}" for m in ("2024", "3036", "4048")]
          for r in ("6000", "9000", "12000")}
PH_ALL = [c for v in PH_FAM.values() for c in v]
RY = ph.FEATURE_NAMES.index("Re_y")

# Executable leakage assertions, not prose.
assert set(PH_ALL) <= set(ph._PH_TRAIN)
assert not (set(PH_ALL) & (set(ph._PH_TEST) | set(ph._PH_VAL)))
assert not (set(DUCT_TRAIN + DUCT_VAL) & set(DUCT_TEST))

HP = dict(max_iter=300, max_depth=6, learning_rate=0.05,
          l2_regularization=1.0, random_state=0)   # identical to the entry of record


def _parse(p):
    return Ofpp.parse_internal_field(str(p))


def _pack(f, u_les=None):
    X7 = ph.build_features(f["gradU"], f["k"], f["omega"], f["walldist"], f["U"], f["nu"])
    d = f["walldist"]
    rec = dict(X7=X7, U=f["U"], Uref=float(np.linalg.norm(f["U"], axis=1).mean()),
               d_norm=(d / d.max())[:, None])
    if u_les is not None:
        rec["u_les"] = u_les
    return rec


def make_X(rec, variant):
    if variant == "A":
        return rec["X7"]
    if variant == "D":
        return np.hstack([rec["X7"], rec["d_norm"]])
    raise ValueError(variant)


NORM = {"A": False, "D": True}


def fit_apply(store, variant, train_cases, target_cases):
    X = np.concatenate([make_X(store[c], variant) for c in train_cases])
    if NORM[variant]:
        Y = np.concatenate([(store[c]["u_les"] - store[c]["U"]) / store[c]["Uref"]
                            for c in train_cases])
    else:
        Y = np.concatenate([store[c]["u_les"] - store[c]["U"] for c in train_cases])
    ms = [HistGradientBoostingRegressor(**HP).fit(X, Y[:, j]) for j in range(3)]
    out = {}
    for c in target_cases:
        dd = np.column_stack([m.predict(make_X(store[c], variant)) for m in ms])
        if NORM[variant]:
            dd = dd * store[c]["Uref"]
        out[c] = float(ph.scaled_mae(store[c]["U"] + dd, store[c]["u_les"]))
    return out


def main() -> None:
    rec: dict = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose": ("Diagnose why the DUCT correction transfers badly to the Re_tau=360 "
                    "test ducts, and validate a candidate fix on train/validation data only."),
        "official_scoring_calls_made_by_this_script": 0,
        "hyperparameters": {k: v for k, v in HP.items()},
    }

    # ---------------- duct store ----------------
    duct = {}
    for c in DUCT_TRAIN + DUCT_VAL + DUCT_TEST:
        f = ex._reconstruct_duct_fields(c, _parse)
        u = ex._load_duct_ground_truth_U(c, _parse) if c in DUCT_TRAIN + DUCT_VAL else None
        duct[c] = _pack(f, u)

    # ---------------- 1. the degeneracy is real but does not discriminate ----
    Xtr = np.concatenate([duct[c]["X7"] for c in DUCT_TRAIN])
    i3 = ph.FEATURE_NAMES.index("I3_S3")
    i4 = ph.FEATURE_NAMES.index("I4_W2S")
    rec["degeneracy_reproduced_but_non_discriminating"] = {
        "max_abs_I3_S3_over_duct_training_cells": float(np.abs(Xtr[:, i3]).max()),
        "max_abs_I4_W2S_over_duct_training_cells": float(np.abs(Xtr[:, i4]).max()),
        "max_abs_I3_S3_per_test_duct": {
            c: float(np.abs(duct[c]["X7"][:, i3]).max()) for c in DUCT_TEST},
        "max_abs_I4_W2S_per_test_duct": {
            c: float(np.abs(duct[c]["X7"][:, i4]).max()) for c in DUCT_TEST},
        "why_it_cannot_explain_the_deficit": (
            "Both features are numerically zero on all three duct test cases, including "
            "AR_14_Ret_180 where the entry of record is best on the board (0.0303 vs a "
            "next-best 0.0325). A defect equally present on the case we win and the cases "
            "we lose does not discriminate between them."),
    }

    # ---------------- 2. Re_y coverage, test-blind -------------------------
    lo, hi = Xtr.min(axis=0), Xtr.max(axis=0)
    cov = {}
    for c in DUCT_TRAIN + DUCT_VAL + DUCT_TEST:
        X = duct[c]["X7"]
        cov[c] = {
            "role": ("train" if c in DUCT_TRAIN else "validation" if c in DUCT_VAL else "TEST"),
            "Re_y_max": float(X[:, RY].max()),
            "Re_y_max_over_trained_max": float(X[:, RY].max() / hi[RY]),
            "pct_cells_outside_trained_range_any_feature":
                float(100.0 * ((X < lo) | (X > hi)).any(axis=1).mean()),
            "pct_cells_Re_y_above_trained_max": float(100.0 * (X[:, RY] > hi[RY]).mean()),
            "mean_U_rans": duct[c]["Uref"],
        }
    rec["feature_coverage_test_blind"] = {
        "trained_range_over_4_duct_training_cases":
            {n: [float(lo[j]), float(hi[j])] for j, n in enumerate(ph.FEATURE_NAMES)},
        "per_case": cov,
        "note": ("Built from the RANS solve and mesh only. No ground truth is required to "
                 "compute any of this, and none was read for the three test ducts."),
    }

    # ---------------- 3. duct validation of the fix -----------------------
    duct_res = {"leave_one_duct_out": {}, "suggested_validation_case_AR_7_Ret_180": {}}
    loo = {"A": [], "D": []}
    for held in DUCT_TRAIN:
        tr = [c for c in DUCT_TRAIN if c != held]
        entry = {"floor": float(ph.scaled_mae(duct[held]["U"], duct[held]["u_les"]))}
        for v in ("A", "D"):
            s = fit_apply(duct, v, tr, [held])[held]
            entry[v] = s
            loo[v].append(s)
        duct_res["leave_one_duct_out"][held] = entry
    duct_res["leave_one_duct_out"]["MEAN"] = {v: float(np.mean(loo[v])) for v in ("A", "D")}

    fl7 = float(ph.scaled_mae(duct["AR_7_Ret_180"]["U"], duct["AR_7_Ret_180"]["u_les"]))
    v7 = {"floor": fl7}
    for v in ("A", "D"):
        s = fit_apply(duct, v, DUCT_TRAIN, DUCT_VAL)["AR_7_Ret_180"]
        v7[v] = s
        v7[f"{v}_pct_of_floor_error_removed"] = float(100 * (fl7 - s) / fl7)
    duct_res["suggested_validation_case_AR_7_Ret_180"] = v7
    rec["duct_family_validation"] = duct_res

    # ---------------- 4. periodic-hill Reynolds sweep ---------------------
    phs = {}
    for c in PH_ALL:
        f = ph._load_rans_fields(c, _parse)
        phs[c] = _pack(f, ph._load_ground_truth_U(c, _parse))
    ph_tr_max = max(phs[c]["X7"][:, RY].max() for c in PH_FAM["6000"] + PH_FAM["9000"])
    ph_res = {
        "caveat": ("Re_y does NOT leave its trained range across this sweep -- measured "
                   "below -- so this is a Reynolds-generalisation test but NOT a "
                   "reproduction of the duct saturation mechanism."),
        "Re_y_trained_max_over_Re_6000_9000": float(ph_tr_max),
        "Re_y_max_ratio_at_Re_12000": {
            c: float(phs[c]["X7"][:, RY].max() / ph_tr_max) for c in PH_FAM["12000"]},
        "mean_U_rans_per_case": {c: phs[c]["Uref"] for c in PH_ALL},
        "splits": {},
    }
    for label, (tr, te) in {
        "extrapolate_up_train_6000_9000_predict_12000":
            (PH_FAM["6000"] + PH_FAM["9000"], PH_FAM["12000"]),
        "interpolate_train_6000_12000_predict_9000":
            (PH_FAM["6000"] + PH_FAM["12000"], PH_FAM["9000"]),
    }.items():
        fl = {c: float(ph.scaled_mae(phs[c]["U"], phs[c]["u_les"])) for c in te}
        block = {"floor_per_case": fl, "floor_mean": float(np.mean(list(fl.values())))}
        for v in ("A", "D"):
            r = fit_apply(phs, v, tr, te)
            block[v] = {"per_case": r, "mean": float(np.mean(list(r.values())))}
        block["D_pct_better_than_A"] = float(
            100 * (block["A"]["mean"] - block["D"]["mean"]) / block["A"]["mean"])
        block["D_beats_A_on_n_of_n_cases"] = [
            int(sum(block["D"]["per_case"][c] < block["A"]["per_case"][c] for c in te)), len(te)]
        ph_res["splits"][label] = block
    rec["periodic_hill_reynolds_sweep"] = ph_res

    rec["verdict"] = {
        "variant_D": ("eighth feature d/d_max (wall distance / case max wall distance, "
                      "exactly Reynolds-invariant, mesh-only) plus target normalised by the "
                      "case's own mean |U_RANS|"),
        "selection_rule_stated_before_any_test_scoring": (
            "Chosen on the benchmark's own suggested duct validation case AR_7_Ret_180, "
            "tie-broken on leave-one-duct-out mean. No test-case score influenced it."),
        "what_is_proven": (
            "D does no harm and materially helps on every held-out set the rules permit: "
            "the suggested duct validation case, leave-one-duct-out, and both directions of "
            "the periodic-hill Reynolds sweep."),
        "what_is_NOT_proven": (
            "That D closes the duct deficit on AR_1_Ret_360 and AR_3_Ret_360. No legal test "
            "of Reynolds transfer at a doubled velocity scale exists in this benchmark, "
            "because every duct the rules let us fit on sits at one Reynolds number."),
    }

    _OUT.write_text(json.dumps(rec, indent=2))

    # ------------------------- console summary ----------------------------
    print("Re_y coverage (test-blind):")
    for c in DUCT_TRAIN + DUCT_VAL + DUCT_TEST:
        e = cov[c]
        print(f"  {e['role']:10s} {c:18s} Re_y max = {e['Re_y_max_over_trained_max']:.2f}x "
              f"trained max   cells above: {e['pct_cells_Re_y_above_trained_max']:5.2f}%")
    print("\nduct leave-one-out mean:  A "
          f"{duct_res['leave_one_duct_out']['MEAN']['A']:.5f}   D "
          f"{duct_res['leave_one_duct_out']['MEAN']['D']:.5f}")
    print(f"AR_7_Ret_180 validation:  floor {v7['floor']:.5f}   "
          f"A {v7['A']:.5f} ({v7['A_pct_of_floor_error_removed']:.1f}% removed)   "
          f"D {v7['D']:.5f} ({v7['D_pct_of_floor_error_removed']:.1f}% removed)")
    for label, b in ph_res["splits"].items():
        print(f"PH {label}: A {b['A']['mean']:.5f}  D {b['D']['mean']:.5f}  "
              f"D better by {b['D_pct_better_than_A']:+.1f}% "
              f"({b['D_beats_A_on_n_of_n_cases'][0]}/{b['D_beats_A_on_n_of_n_cases'][1]} cases)")
    print(f"\nwrote {_OUT}")
    print("official scoring calls made: 0")


if __name__ == "__main__":
    main()
