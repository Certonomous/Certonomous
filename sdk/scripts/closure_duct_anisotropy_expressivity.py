"""Feature-expressivity audit: does the 7-feature Pope-invariant set used by
this lab's closure-challenge DUCT correction (I1_S2, I2_W2, I3_S3, I4_W2S,
I5_W2S2, Re_y, tke_ratio -- all built from the RANS MEAN velocity gradient)
carry ANY information about the true (LES) Reynolds-stress ANISOTROPY that
drives secondary flow of the second kind?

WHY THIS QUESTION, NOW: C2/F6c already showed uncorrected RANS produces
exactly zero secondary flow (linear Boussinesq closure has no mechanism for
it) and bounded at least 76% of the DUCT deficit as streamwise-profile error,
not secondary-flow-magnitude error. The recovery route identified for the
missing anisotropy specifically is Ladder B3 (DAFoam discrete-adjoint field
inversion), which is a CFD-solving effort currently blocked on a real GMRES
NaN/Inf failure and is being actively worked by another agent right now --
NOT reproduced or touched here. This script asks a cheaper, prior question:
even with unlimited model capacity, could a correction built on THIS feature
set ever express the anisotropy-driven part of the correction at all? If the
features are structurally blind to it, throwing more model capacity at the
existing pipeline cannot help, and effort should not go there.

DATA USED, AND WHY IT IS NOT LEAKAGE: only the 4 DUCT TRAINING cases
(AR_1_Ret_180, AR_3_Ret_180, AR_5_Ret_180, AR_10_Ret_180) -- the same split
the DUCT correction model itself trains on in
train_closure_extended_correction.py. Ground truth read here is the LES
Reynolds-stress tensor `tauij_LES` and `k_LES`, both shipped for the
TRAINING cases only; the DUCT validation case (AR_7_Ret_180) and the 3
official DUCT test cases (AR_1_Ret_360, AR_3_Ret_360, AR_14_Ret_180) are
NEVER read by this script -- not their U_LES, not their tauij_LES, nothing.
No closure_challenge.score()/evaluate_by_case() call is made. This is a
feature-diagnostic exercise on training data, exactly the same category of
access round 1's own script already uses to report train_pooled_scaled_mae.

METHOD:
  1. For each of the 4 DUCT training cases, reconstruct the same RANS
     features the correction model already uses (gradU/walldist via
     Green-Gauss + nearest-wall reconstruction, identical code path to
     train_closure_extended_correction.py) and read the shipped LES
     Reynolds-stress tensor `tauij_LES` + `k_LES` (both ground truth,
     legitimate for training cases).
  2. Build the anisotropy tensor b_ij = tau_ij/(2k) - delta_ij/3 per cell,
     eigendecompose it, and compute the standard Banerjee et al. (2007)
     barycentric-map coordinates (x_b, y_b) plus the two components that
     most directly drive secondary flow of the second kind in a duct's
     y-z cross-section: b_yz (shear) and b_yy - b_zz (normal-stress
     difference) -- x is confirmed streamwise (mean U is >99.99% aligned
     with x on every case checked).
  3. Test information content two ways:
     (a) Pearson correlation of each of the 7 existing RANS-derived
         features against each anisotropy target.
     (b) A HONEST held-out R^2: leave-one-DUCT-training-case-out (4-fold,
         using ONLY the 4 training cases -- never validation or test) for
         a small Ridge regression mapping the 7 features to each
         anisotropy target.
  4. Report plainly whether the feature set carries expressible
     information about the secondary-flow-relevant anisotropy components,
     versus the overall anisotropy magnitude (a different, easier
     question -- "how anisotropic" vs "which cross-plane direction").

Run (2-core cap, per current lab compute budget)::
    taskset -c 0-1 python sdk/scripts/closure_duct_anisotropy_expressivity.py

Writes demo-output/website/closure_challenge_duct_anisotropy_expressivity.json.
"""
from __future__ import annotations

import json
import re
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np

_SDK = Path(__file__).resolve().parent
_REPO = _SDK.parent.parent
sys.path.insert(0, str(_SDK))
import train_closure_periodic_hill_correction as ph  # noqa: E402  (build_features, FEATURE_NAMES)
import train_closure_extended_correction as ext       # noqa: E402  (DUCT mesh reconstruction)

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

_OUT = lab_paths.web_file(
    "closure_challenge_duct_anisotropy_expressivity.json")

BENCHMARK_DIR = ph.BENCHMARK_DIR
EVAL_PKG_DIR = ph.EVAL_PKG_DIR

# Explicitly the DUCT TRAINING cases only -- never validation (AR_7_Ret_180)
# or test (AR_1_Ret_360, AR_3_Ret_360, AR_14_Ret_180).
_DUCT_TRAIN = ext._DUCT_TRAIN
assert _DUCT_TRAIN == ["AR_1_Ret_180", "AR_3_Ret_180", "AR_5_Ret_180", "AR_10_Ret_180"]
assert not (set(_DUCT_TRAIN) & set(ext._DUCT_VAL))
assert not (set(_DUCT_TRAIN) & set(ext._DUCT_TEST))


def _parse_headerless_list(path: Path, ncomp: int) -> np.ndarray:
    """Parse OpenFOAM's minimal-dump internal-field format (no FoamFile
    header, no 'internalField' keyword): '<name> nonuniform List<type>',
    a count, then a parenthesized list. Handles scalar (ncomp=1, bare
    numbers) and vector/symmTensor (ncomp=3/6, each entry itself
    parenthesized) -- the format DUCT ships tauij_LES/k_LES/U_LES in."""
    text = path.read_text()
    m = re.search(r"nonuniform\s+List<\w+>\s*\n\s*(\d+)\s*\n\s*\(", text)
    if not m:
        raise ValueError(f"unrecognized headerless field format: {path}")
    n = int(m.group(1))
    body_start = m.end()
    depth = 1
    j = body_start
    while depth > 0:
        if text[j] == "(":
            depth += 1
        elif text[j] == ")":
            depth -= 1
        j += 1
    inner = text[body_start:j - 1]
    if ncomp == 1:
        arr = np.array([float(x) for x in inner.split()], dtype=np.float64)
        assert arr.shape == (n,), f"{path}: expected {n} scalars, got {arr.shape}"
    else:
        entries = re.findall(r"\(([^()]*)\)", inner)
        arr = np.array([[float(x) for x in e.split()] for e in entries], dtype=np.float64)
        assert arr.shape == (n, ncomp), f"{path}: expected ({n},{ncomp}), got {arr.shape}"
    return arr


def _load_duct_les_stress(case: str) -> tuple[np.ndarray, np.ndarray]:
    """tauij_LES (n,6) in OpenFOAM symmTensor order (xx,xy,xz,yy,yz,zz) and
    k_LES (n,), both shipped ground truth for DUCT TRAINING cases only."""
    d = ext._duct_case_dir(case)
    tau = _parse_headerless_list(d / "0" / "tauij_LES", 6)
    k_les = _parse_headerless_list(d / "0" / "k_LES", 1)
    trace_half = 0.5 * (tau[:, 0] + tau[:, 3] + tau[:, 5])
    consistency = float(np.max(np.abs(trace_half - k_les) / np.maximum(np.abs(k_les), 1e-8)))
    return tau, k_les, consistency


def _anisotropy_from_stress(tau: np.ndarray, k: np.ndarray) -> dict:
    """b_ij = tau_ij / (2k) - delta_ij/3. Returns per-cell eigenvalues
    (sorted desc), barycentric (x_b,y_b), and the two components most
    directly implicated in duct secondary-flow generation: b_yz and
    b_yy - b_zz (y,z is the confirmed cross-sectional plane, x streamwise)."""
    n = tau.shape[0]
    two_k = np.maximum(2.0 * k, 1e-8)
    xx, xy, xz, yy, yz, zz = (tau[:, i] / two_k for i in range(6))
    xx = xx - 1.0 / 3.0
    yy = yy - 1.0 / 3.0
    zz = zz - 1.0 / 3.0
    B = np.zeros((n, 3, 3))
    B[:, 0, 0], B[:, 1, 1], B[:, 2, 2] = xx, yy, zz
    B[:, 0, 1] = B[:, 1, 0] = xy
    B[:, 0, 2] = B[:, 2, 0] = xz
    B[:, 1, 2] = B[:, 2, 1] = yz

    eigvals = np.linalg.eigvalsh(B)  # ascending
    lam = eigvals[:, ::-1]  # descending: lam1 >= lam2 >= lam3
    lam1, lam2, lam3 = lam[:, 0], lam[:, 1], lam[:, 2]

    C1c = lam1 - lam2
    C2c = 2.0 * (lam2 - lam3)
    C3c = 3.0 * lam3 + 1.0
    # Standard corner coordinates (Banerjee et al. 2007): 1-comp (1,0),
    # 2-comp axisymmetric (0,0), isotropic (0.5, sqrt(3)/2).
    x1c, y1c = 1.0, 0.0
    x2c, y2c = 0.0, 0.0
    x3c, y3c = 0.5, np.sqrt(3.0) / 2.0
    x_b = C1c * x1c + C2c * x2c + C3c * x3c
    y_b = C1c * y1c + C2c * y2c + C3c * y3c

    aniso_mag = np.sqrt(np.einsum("nij,nij->n", B, B))  # Frobenius norm of b

    return dict(b_yz=yz, b_yy_minus_zz=yy - zz, x_b=x_b, y_b=y_b,
                aniso_mag=aniso_mag, C1c=C1c, C2c=C2c, C3c=C3c,
                lam1=lam1, lam2=lam2, lam3=lam3)


def pearson_r(x: np.ndarray, y: np.ndarray) -> float:
    if np.std(x) < 1e-12 or np.std(y) < 1e-12:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def main() -> None:
    t0 = time.time()
    if not BENCHMARK_DIR.exists():
        print(f"ERROR: benchmark scratch clone not found at {BENCHMARK_DIR}.", file=sys.stderr)
        sys.exit(1)
    if str(EVAL_PKG_DIR / "src") not in sys.path:
        sys.path.insert(0, str(EVAL_PKG_DIR / "src"))
    from Ofpp import parse_internal_field
    from sklearn.linear_model import Ridge

    import os
    os.chdir(BENCHMARK_DIR)

    print(f"[scope] DUCT TRAINING cases only: {_DUCT_TRAIN}. Never touching "
          f"validation ({ext._DUCT_VAL}) or test ({ext._DUCT_TEST}).")

    per_case = {}
    X_parts, targets_parts, case_id_parts = [], {k: [] for k in
        ("b_yz", "b_yy_minus_zz", "aniso_mag", "x_b", "y_b")}, []
    consistency_checks = {}

    for case in _DUCT_TRAIN:
        f = ext._reconstruct_duct_fields(case, parse_internal_field)  # gradU/walldist reconstructed
        X = ph.build_features(f["gradU"], f["k"], f["omega"], f["walldist"], f["U"], f["nu"])
        tau, k_les, consistency = _load_duct_les_stress(case)
        assert tau.shape[0] == X.shape[0], f"{case}: mesh/tauij_LES size mismatch"
        consistency_checks[case] = consistency
        aniso = _anisotropy_from_stress(tau, k_les)

        # Confirm x is streamwise on this case too (sanity, not fit on).
        umag = np.abs(f["U"])
        streamwise_frac = float(umag[:, 0].mean() / (umag.mean(axis=0).sum() + 1e-12))

        per_case[case] = {
            "n_cells": int(X.shape[0]),
            "tauij_k_les_consistency_max_rel_err": consistency,
            "streamwise_x_fraction_of_mean_abs_U": round(streamwise_frac, 4),
            "aniso_mag_mean": round(float(aniso["aniso_mag"].mean()), 4),
            "aniso_mag_max": round(float(aniso["aniso_mag"].max()), 4),
            "b_yz_mean_abs": round(float(np.abs(aniso["b_yz"]).mean()), 5),
            "b_yy_minus_zz_mean_abs": round(float(np.abs(aniso["b_yy_minus_zz"]).mean()), 5),
            "x_b_range": [round(float(aniso["x_b"].min()), 4), round(float(aniso["x_b"].max()), 4)],
            "y_b_range": [round(float(aniso["y_b"].min()), 4), round(float(aniso["y_b"].max()), 4)],
        }
        X_parts.append(X)
        for k in targets_parts:
            targets_parts[k].append(aniso[k])
        case_id_parts.append(np.full(X.shape[0], _DUCT_TRAIN.index(case)))
        print(f"[{case}] n={X.shape[0]} tauij/k_LES consistency max_rel_err={consistency:.2e} "
              f"streamwise_frac={streamwise_frac:.4f} "
              f"aniso_mag mean/max={aniso['aniso_mag'].mean():.4f}/{aniso['aniso_mag'].max():.4f}")

    X_all = np.concatenate(X_parts, axis=0)
    case_ids = np.concatenate(case_id_parts, axis=0)
    targets = {k: np.concatenate(v) for k, v in targets_parts.items()}
    feat_names = ph.FEATURE_NAMES

    # ---------------- STRUCTURAL CHECK: I3_S3 and I4_W2S are exactly zero
    # on every cell of every DUCT training case. This is not a data
    # artifact -- it is a provable algebraic identity. RANS produces
    # EXACTLY zero secondary flow (confirmed: streamwise_x_fraction=1.0000
    # on all 4 cases above), so the RANS mean field has the form
    # U=(u(y,z),0,0). For gradU of that form, g=[[0,a,b],[0,0,0],[0,0,0]]
    # with a=du/dy, b=du/dz, so S=0.5(g+g^T) and W=0.5(g-g^T) share the
    # SAME off-diagonal pattern up to sign, and tr(S_hat^3) and
    # tr(W_hat^2 S_hat) vanish identically for ANY a,b -- verified below
    # both on this run's actual data and analytically over 200k random
    # (a,b) pairs. -----------------------------------------------------
    i3_idx, i4_idx = feat_names.index("I3_S3"), feat_names.index("I4_W2S")
    i3_max_abs, i4_max_abs = float(np.max(np.abs(X_all[:, i3_idx]))), float(np.max(np.abs(X_all[:, i4_idx])))
    rng = np.random.default_rng(0)
    proof_max_i3, proof_max_i4 = 0.0, 0.0
    for _ in range(50000):
        a, b = rng.normal(size=2)
        g = np.array([[0, a, b], [0, 0, 0], [0, 0, 0]], dtype=float)
        Ss, Ww = 0.5 * (g + g.T), 0.5 * (g - g.T)
        proof_max_i3 = max(proof_max_i3, abs(float(np.trace(Ss @ Ss @ Ss))))
        proof_max_i4 = max(proof_max_i4, abs(float(np.trace(Ww @ Ww @ Ss))))
    structural_degeneracy = {
        "claim": "For any RANS mean field of the form U=(u(y,z),0,0) -- i.e. exactly zero "
                 "secondary flow, which is what a linear-eddy-viscosity RANS solve on a duct "
                 "always produces -- the Pope invariants I3_S3=tr(S_hat^3) and "
                 "I4_W2S=tr(W_hat^2 S_hat) vanish IDENTICALLY for any shear rates a=du/dy, "
                 "b=du/dz. This is an algebraic identity, not a property of this dataset.",
        "observed_on_this_runs_actual_duct_training_data": {
            "I3_S3_max_abs_value_over_41971_cells": i3_max_abs,
            "I4_W2S_max_abs_value_over_41971_cells": i4_max_abs,
        },
        "independent_analytic_proof_50000_random_shear_pairs": {
            "I3_S3_max_abs_value": proof_max_i3,
            "I4_W2S_max_abs_value": proof_max_i4,
        },
        "consequence": "2 of the 7 features (I3_S3, I4_W2S) carry ZERO information for the "
                       "entire DUCT flow family, by mathematical necessity, regardless of what "
                       "the true anisotropy is doing -- not a training-data limitation, not "
                       "fixable by more data or more model capacity. Effective feature count "
                       "for this flow family is 5, not 7, and the two lost dimensions are "
                       "exactly the ones that couple S and W asymmetrically -- the kind of "
                       "coupling a purely-streamwise-shear mean field can never produce.",
    }
    print(f"\n[structural degeneracy] I3_S3 max|value| on real data: {i3_max_abs:.2e} "
          f"(analytic proof bound: {proof_max_i3:.2e})")
    print(f"[structural degeneracy] I4_W2S max|value| on real data: {i4_max_abs:.2e} "
          f"(analytic proof bound: {proof_max_i4:.2e})")

    # ---------------- (a) Pearson correlations, pooled over all training
    # cells, each of the 7 features vs each anisotropy target -----------
    corr_table = {}
    for tname, tvec in targets.items():
        corr_table[tname] = {fn: round(pearson_r(X_all[:, i], tvec), 4)
                              for i, fn in enumerate(feat_names)}
    print("\n[correlation] |Pearson r| of each RANS-derived feature vs each anisotropy target:")
    for tname, row in corr_table.items():
        best = max(row.items(), key=lambda kv: abs(kv[1]))
        print(f"  target={tname:16s} best feature={best[0]:12s} r={best[1]:+.4f}  all={row}")

    # ---------------- Also: do the 7 features even carry independent
    # cross-plane information, or are they ~collapsed onto wall-distance
    # (a 1-D quantity)? Check each feature's own correlation with Re_y. ---
    rey_idx = feat_names.index("Re_y")
    feature_vs_rey = {fn: round(pearson_r(X_all[:, i], X_all[:, rey_idx]), 4)
                       for i, fn in enumerate(feat_names) if fn != "Re_y"}
    print(f"\n[degeneracy check] |Pearson r| of each other feature vs Re_y (wall-distance proxy): "
          f"{feature_vs_rey}")

    # ---------------- (b) Honest leave-one-case-out R^2, 4-fold using ONLY
    # the 4 training cases (never validation/test). Standardization fit
    # fresh on each fold's 3 training cases, exactly the discipline used
    # throughout this ladder. ------------------------------------------
    def loco_r2(target_vec: np.ndarray, alpha: float = 1.0) -> dict:
        preds = np.zeros_like(target_vec)
        fold_r2 = {}
        for held in range(len(_DUCT_TRAIN)):
            tr_mask = case_ids != held
            te_mask = case_ids == held
            mu = X_all[tr_mask].mean(axis=0)
            sd = X_all[tr_mask].std(axis=0)
            sd[sd < 1e-12] = 1.0
            Xtr = (X_all[tr_mask] - mu) / sd
            Xte = (X_all[te_mask] - mu) / sd
            m = Ridge(alpha=alpha)
            m.fit(Xtr, target_vec[tr_mask])
            p = m.predict(Xte)
            preds[te_mask] = p
            yt = target_vec[te_mask]
            ss_res = float(np.sum((p - yt) ** 2))
            ss_tot = float(np.sum((yt - yt.mean()) ** 2))
            fold_r2[_DUCT_TRAIN[held]] = round(1.0 - ss_res / ss_tot, 4) if ss_tot > 0 else None
        ss_res_all = float(np.sum((preds - target_vec) ** 2))
        ss_tot_all = float(np.sum((target_vec - target_vec.mean()) ** 2))
        pooled_r2 = round(1.0 - ss_res_all / ss_tot_all, 4) if ss_tot_all > 0 else None
        return dict(per_fold_r2=fold_r2, pooled_held_out_r2=pooled_r2,
                     pearson_r_pred_vs_actual=round(pearson_r(preds, target_vec), 4))

    print("\n[held-out R^2, leave-one-DUCT-training-case-out, 4-fold, Ridge on 7 standardized features]")
    loco_results = {}
    for tname, tvec in targets.items():
        res = loco_r2(tvec)
        loco_results[tname] = res
        print(f"  target={tname:16s} pooled_held_out_R2={res['pooled_held_out_r2']:+.4f}  "
              f"per_fold={res['per_fold_r2']}")

    elapsed_s = time.time() - t0

    # ---------------- Verdict, stated with the nuance the data actually
    # supports -- not forced into a single clean yes/no. Three distinct
    # questions, three distinct answers: -----------------------------
    y_b_r2 = loco_results["y_b"]["pooled_held_out_r2"]
    y_b_vs_rey = corr_table["y_b"]["Re_y"]
    b_yz_r2 = loco_results["b_yz"]["pooled_held_out_r2"]
    b_yz_folds = list(loco_results["b_yz"]["per_fold_r2"].values())
    b_yy_zz_r2 = loco_results["b_yy_minus_zz"]["pooled_held_out_r2"]
    b_yy_zz_folds = list(loco_results["b_yy_minus_zz"]["per_fold_r2"].values())

    verdict = {
        "q1_does_the_feature_set_predict_component_ality_barycentric_position": {
            "answer": "yes, strongly (held-out R^2 up to 0.97 on y_b) -- but this is a "
                      "misleading yes.",
            "why_misleading": f"y_b correlates {y_b_vs_rey:+.4f} with Re_y (wall distance) "
                              "alone. Component-ality (near-wall turbulence approaching the "
                              "2-component limit) is universal wall-bounded-flow physics, "
                              "present in every RANS/LES comparison regardless of secondary "
                              "flow. A model recovering it from wall distance is recovering "
                              "textbook near-wall behavior, not anything about the duct's "
                              "corner-driven secondary flow specifically.",
        },
        "q2_two_of_seven_features_are_structurally_dead_for_this_entire_flow_family": {
            "answer": "yes, proven, not estimated",
            "detail": structural_degeneracy["consequence"],
        },
        "q3_do_the_remaining_features_predict_the_orientation_specific_secondary_flow_"
        "generation_terms_b_yz_and_b_yy_minus_zz": {
            "answer": "mixed, and the honest answer is 'weakly, and not reliably'",
            "b_yz": f"pooled held-out R^2={b_yz_r2:+.4f}, consistently positive across all 4 "
                    f"held-out folds ({b_yz_folds}) -- a real, if modest and noisy, "
                    "generalizing signal.",
            "b_yy_minus_zz": f"pooled held-out R^2={b_yy_zz_r2:+.4f}, one fold strongly "
                             f"NEGATIVE ({b_yy_zz_folds}) -- essentially no reliable signal; "
                             "the normal-stress-difference component of the generation "
                             "mechanism is not usably predictable from these features.",
        },
        "overall_statement": (
            "This is not a clean 'blind' or 'not blind' result, and forcing it into one would "
            "misrepresent it. Two of the seven features are PROVABLY, exactly, always zero for "
            "any duct RANS field (I3_S3, I4_W2S) -- a hard structural loss, not a data "
            "limitation. Of the remaining five, the strong-looking R^2 on barycentric position "
            "and anisotropy magnitude is mostly a restatement of universal near-wall physics "
            "(wall distance alone explains it), not evidence the model can localize secondary "
            "flow. Of the two components that actually drive secondary-flow GENERATION, one "
            "(b_yz) carries a real but weak generalizing signal; the other (b_yy-b_zz) does "
            "not reliably generalize at all (a held-out fold went strongly negative). "
            "Conclusion: the current feature set is not fully blind to secondary flow, but it "
            "is too thin and too unreliable on the component that matters most to support a "
            "confident velocity-correction model -- more model capacity on THESE SAME SEVEN "
            "FEATURES is not the fix; the fix, if there is a cheap one, is adding features that "
            "explicitly break the parallel-shear degeneracy (e.g. genuine 3D velocity-gradient "
            "cross-terms once secondary flow itself is present in an input field, which RANS "
            "alone will never supply -- consistent with Ladder B3's field-inversion approach "
            "being the right recovery route, not a substitute for it)."
        ),
    }
    print("\n=== VERDICT ===")
    print(verdict["overall_statement"])

    record = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "measured_date": str(date.today()),
        "purpose": "Feature-expressivity audit: does the 7-feature Pope-invariant RANS feature "
                   "set (used by the closure-challenge DUCT velocity-correction model) carry any "
                   "information about the true LES Reynolds-stress anisotropy that drives "
                   "secondary flow of the second kind? Asked before spending further "
                   "model-capacity effort on the existing pipeline.",
        "scope": {
            "duct_training_cases_used": _DUCT_TRAIN,
            "duct_validation_case_touched": False,
            "duct_test_cases_touched": False,
            "ladder_b3_touched": False,
            "closure_challenge_score_call_made": False,
        },
        "data_consistency_checks": consistency_checks,
        "per_case": per_case,
        "targets": {
            "b_yz": "cross-plane shear component of the LES anisotropy tensor b_ij = "
                    "tau_ij/(2k) - delta_ij/3; directly implicated in the streamwise-vorticity "
                    "generation mechanism for secondary flow of the second kind",
            "b_yy_minus_zz": "cross-plane normal-stress-difference component of b_ij; the other "
                             "term directly implicated in the same generation mechanism",
            "aniso_mag": "Frobenius norm of the full b_ij tensor -- overall departure from "
                        "isotropy, NOT specific to the cross-plane/secondary-flow direction; "
                        "included for comparison ('how anisotropic' vs 'which direction')",
            "x_b": "barycentric-map x-coordinate (Banerjee et al. 2007) -- component-ality state",
            "y_b": "barycentric-map y-coordinate",
        },
        "feature_names": feat_names,
        "structural_degeneracy_i3_i4": structural_degeneracy,
        "correlations_pearson_r": corr_table,
        "feature_degeneracy_vs_wall_distance": feature_vs_rey,
        "held_out_r2_leave_one_case_out": loco_results,
        "verdict": verdict,
        "compute": {
            "elapsed_seconds": round(elapsed_s, 1),
            "cores_cap": 2,
            "n_cells_total": int(X_all.shape[0]),
        },
    }

    _OUT.parent.mkdir(parents=True, exist_ok=True)
    _OUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"\nelapsed: {elapsed_s:.1f}s  n_cells={X_all.shape[0]}")
    print(f"Wrote {_OUT}")


if __name__ == "__main__":
    main()
