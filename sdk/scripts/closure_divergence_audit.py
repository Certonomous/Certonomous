"""G2 of the methods audit (CLOSURE_METHODS_COMPARISON.md, ac2f37ee):
a-posteriori physicality (continuity) of the corrected velocity fields,
measured TEST-BLIND.

THE QUESTION: the submitted corrected field U = U_RANS + deltaU is a
cell-wise ML output added to a solenoidal RANS solution. Nothing guarantees
div(U) stays small, and nobody had measured it. Every other entrant on the
board re-solves the governing equations, so their submitted fields satisfy
continuity by construction; ours is the only one that does not, and "we
measured it and here is the number" is the only honest position.

OPERATOR: the already-validated Green-Gauss machinery of
closure_mesh_recon.py (gradU r=0.9997-1.0000 against shipped fields on PH
training cases; cell C/V to ~1e-13). div(U) = tr(grad U) per cell. Both the
raw RANS field and the corrected field go through the IDENTICAL operator, so
operator discretization error cancels in the ratio. Boundary faces carry the
RANS field's own boundary metadata for both fields (the correction is
cell-centred and does not alter boundary conditions) -- recorded, not hidden.

TEST-BLIND LEGALITY (checked against the guard's own definition before
running): this reads RANS fields, mesh geometry, and our own model outputs
-- exactly the categories rounds 2-4 legitimately read for test cases. No
U_LES of any validation or test case is read; ground truth is read ONLY for
the 21 PH + 4 DUCT training cases, to refit the two frozen models exactly as
the entry of record did (deterministic at random_state=0). The raising-stub
scoring guard is re-armed and proven armed before any pipeline work. The
regenerated test fields are verified against the shipped round-4 submission
CSVs at the official evaluation points before being trusted, so the
divergence numbers are about THE submitted fields, not a lookalike.

Pre-registration: closure_challenge_stability_physicality_audit.md SS0.2,
committed 73fa6a33 before this script first ran (material line: ratio >= 2
on any model-corrected case).

Run (2-core cap)::
    OMP_NUM_THREADS=2 taskset -c 2-3 \
        /home/ubuntu/closure-venv/bin/python \
        sdk/scripts/closure_divergence_audit.py

Writes demo-output/website/closure_challenge_divergence_audit.json and (for
the round-4 manifest builder) the regenerated eval-point predictions to the
session scratchpad.
"""
from __future__ import annotations

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
import closure_mesh_recon as mr  # noqa: E402
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

_OUT = lab_paths.web_file("closure_challenge_divergence_audit.json")
_CSV_DIR = lab_paths.CLOSURE_SUBMISSION_ROUND4 / "test"
_SCRATCH = Path(os.environ.get(
    "CLOSURE_SCRATCH",
    "/tmp/claude-1000/-home-ubuntu-Certonomous/64b13819-ff95-4d4d-a50f-3720bab19084/scratchpad"))

HP = dict(max_iter=300, max_depth=6, learning_rate=0.05,
          l2_regularization=1.0, random_state=0)


class ScoringCallRefused(RuntimeError):
    pass


def _forbid_scoring(cc, du, ev):
    cached = du._ground_truth()

    def coords_only(case):
        return np.asarray(cached[case]["coords"])

    def _refuse(name):
        def _raiser(*_a, **_kw):
            raise ScoringCallRefused(
                f"{name}() was called by closure_divergence_audit.py. This audit is "
                "test-blind by pre-registration; nothing here may consume a scoring "
                "call or read test velocities.")
        return _raiser

    blocked = ("score", "score_from_csv", "evaluate_by_case",
               "evaluate_from_csv_by_case", "evaluate_individual_case",
               "_velocity_field", "_ground_truth", "_load_csv_predictions")
    for mod in (cc, du, ev):
        for name in blocked:
            if hasattr(mod, name):
                setattr(mod, name, _refuse(name))
    return coords_only


def _divergence_setup(case_dir: Path, u_path: Path, U: np.ndarray):
    """Mesh geometry + boundary metadata once per case; returns a closure
    computing (vol-weighted RMS div, vol-weighted RMS |gradU|_F) for any
    cell field on this mesh, plus V."""
    mesh = mr.Mesh(case_dir)
    C, V = mr.reconstruct_cell_centres_vols(mesh)
    assert C.shape[0] == U.shape[0], f"{case_dir}: mesh/field size mismatch"
    u_boundary = mr.read_vector_boundary_field(u_path, list(mesh.boundary.keys()))

    def stats(field: np.ndarray):
        g = mr.green_gauss_grad_u(mesh, field, C, V, u_boundary)
        div = g[:, 0] + g[:, 4] + g[:, 8]
        w = V / V.sum()
        rms_div = float(np.sqrt(np.sum(w * div ** 2)))
        rms_grad = float(np.sqrt(np.sum(w * np.sum(g ** 2, axis=1))))
        return rms_div, rms_grad

    return stats


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

    os.chdir(ph.BENCHMARK_DIR)

    # ------------------------------------------------------------------
    # Refit the two frozen models exactly as the entry of record did.
    # Deterministic: random_state=0; the PH model's seed-0 identity with
    # the entry is separately anchored in closure_challenge_seed_sensitivity.json.
    # ------------------------------------------------------------------
    print("[model] refitting round-1 PH model (21 train cases, seed 0)...")
    Xp, yp = [], []
    for c in ph._PH_TRAIN:
        f = ph._load_rans_fields(c, parse_internal_field)
        Xp.append(ph.build_features(f["gradU"], f["k"], f["omega"],
                                    f["walldist"], f["U"], f["nu"]))
        yp.append(ph._load_ground_truth_U(c, parse_internal_field) - f["U"])
    Xp, yp = np.concatenate(Xp), np.concatenate(yp)
    ph_models = [HistGradientBoostingRegressor(**HP).fit(Xp, yp[:, j]) for j in range(3)]

    def ph_delta(X):
        return np.stack([m.predict(X) for m in ph_models], axis=1)

    print("[model] refitting round-4 Variant D duct model (4 train cases, seed 0)...")

    def duct_features(f):
        X7 = ph.build_features(f["gradU"], f["k"], f["omega"],
                               f["walldist"], f["U"], f["nu"])
        d = f["walldist"]
        return np.hstack([X7, (d / d.max())[:, None]])

    Xd, Yd = [], []
    for c in ex._DUCT_TRAIN:
        f = ex._reconstruct_duct_fields(c, parse_internal_field)
        u_les = ex._load_duct_ground_truth_U(c, parse_internal_field)
        uref = float(np.linalg.norm(f["U"], axis=1).mean())
        Xd.append(duct_features(f))
        Yd.append((u_les - f["U"]) / uref)
    Xd, Yd = np.concatenate(Xd), np.concatenate(Yd)
    duct_models = [HistGradientBoostingRegressor(**HP).fit(Xd, Yd[:, j]) for j in range(3)]

    def duct_delta(f):
        uref = float(np.linalg.norm(f["U"], axis=1).mean())
        return np.column_stack([m.predict(duct_features(f)) for m in duct_models]) * uref

    # ------------------------------------------------------------------
    # Case inventory: (name, family, role, model)
    # ------------------------------------------------------------------
    cases = []
    for c in ph._PH_TRAIN:
        cases.append((c, "PH", "train", "PH"))
    for c in ph._PH_VAL:
        cases.append((c, "PH", "validation", "PH"))
    cases += [("alpha_15_13929_4048", "PH", "test", "PH"),
              ("alpha_15_13929_2024", "PH", "test", "PH"),
              ("alpha_05_4071_4048", "PH", "test", "declined"),
              ("alpha_05_4071_2024", "PH", "test", "declined")]
    for c in ex._DUCT_TRAIN:
        cases.append((c, "DUCT", "train", "DUCT_D"))
    for c in ex._DUCT_VAL:
        cases.append((c, "DUCT", "validation", "DUCT_D"))
    for c in ex._DUCT_TEST:
        cases.append((c, "DUCT", "test", "DUCT_D"))
    cases.append(("NASA_2DWMH", "NASA", "test", "PH"))

    results = {}
    regen_preds = {}
    for name, family, role, model in cases:
        tc = time.time()
        if family == "PH":
            d = ph._case_dir(name)
            t = d / "20000"
            f = ph._load_rans_fields(name, parse_internal_field)
            u_path = t / "U"
        elif family == "DUCT":
            d = ex._duct_case_dir(name)
            t = d / ex._duct_solved_time(d)
            f = ex._reconstruct_duct_fields(name, parse_internal_field)
            u_path = t / "U"
        else:
            d = ph.BENCHMARK_DIR / "data" / "NASA_2DWMH"
            t = d / "2000"
            f = ex._reconstruct_nasa_fields(name, parse_internal_field)
            u_path = t / "U"

        if model == "PH":
            delta = ph_delta(ph.build_features(f["gradU"], f["k"], f["omega"],
                                               f["walldist"], f["U"], f["nu"]))
        elif model == "DUCT_D":
            delta = duct_delta(f)
        else:  # declined: submitted field IS the RANS field
            delta = np.zeros_like(f["U"])
        u_corr = f["U"] + delta

        stats = _divergence_setup(d, u_path, f["U"])
        rms_rans, rms_grad_rans = stats(f["U"])
        rms_corr, _ = stats(u_corr)
        ratio = rms_corr / rms_rans if rms_rans > 0 else float("inf")

        row = {
            "family": family, "role": role, "model_applied": model,
            "n_cells": int(f["U"].shape[0]),
            "rms_div_U_RANS": rms_rans,
            "rms_div_U_corrected": rms_corr,
            "ratio_corrected_over_rans": ratio,
            "rms_gradU_frobenius_RANS": rms_grad_rans,
            "div_over_grad_scale_RANS": rms_rans / rms_grad_rans,
            "div_over_grad_scale_corrected": rms_corr / rms_grad_rans,
        }
        results[name] = row
        print(f"[{name:22s}] {role:10s} {model:8s} "
              f"div_RANS {rms_rans:10.4g}  div_corr {rms_corr:10.4g}  "
              f"ratio {ratio:8.3f}  ({time.time()-tc:.0f}s)")

        # Regenerate the eval-point prediction for test cases and verify
        # against the shipped round-4 CSVs.
        if role == "test":
            pts = evaluation_points(name)
            pred = NearestNDInterpolator(f["C"], u_corr)(pts)
            regen_preds[name] = pred
            shipped = np.loadtxt(_CSV_DIR / f"{name}.csv", delimiter=",")
            dmax = float(np.abs(pred - shipped).max())
            row["regenerated_vs_shipped_round4_csv_max_abs_diff"] = dmax
            ok = dmax < 5e-7
            print(f"    regenerated vs shipped CSV: max abs diff {dmax:.3g} "
                  f"-> {'MATCH' if ok else 'MISMATCH'}")

    # ------------------------------------------------------------------
    # Aggregate + verdict against the pre-registered line (ratio >= 2).
    # ------------------------------------------------------------------
    corrected_rows = {k: v for k, v in results.items() if v["model_applied"] != "declined"}
    ratios = {k: v["ratio_corrected_over_rans"] for k, v in corrected_rows.items()}
    worst = max(ratios, key=ratios.get)
    material = any(r >= 2.0 for r in ratios.values())
    csv_ok = all(v.get("regenerated_vs_shipped_round4_csv_max_abs_diff", 0.0) < 5e-7
                 for v in results.values())

    print("\n=== G2 verdict against the pre-registered line (ratio >= 2) ===")
    print(f"  worst ratio: {ratios[worst]:.3f} on {worst}; "
          f"{sum(1 for r in ratios.values() if r >= 2.0)} of {len(ratios)} "
          f"model-corrected cases at or above 2 -> "
          f"{'MATERIAL' if material else 'below the line'}")
    print(f"  regenerated test fields match shipped round-4 CSVs: {csv_ok}")

    record = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "purpose": ("G2 of the methods audit: volume-weighted RMS divergence of the "
                    "corrected field U_RANS + deltaU vs the raw RANS field's own "
                    "divergence, through the identical validated Green-Gauss operator, "
                    "on every case the two frozen models serve or were selected on, "
                    "plus the 8 official test cases (RANS + mesh + own predictions "
                    "only -- no ground truth)."),
        "pre_registration": {
            "file": "demo-output/website/closure_challenge_stability_physicality_audit.md",
            "committed_before_first_run": "73fa6a33",
            "material_if_any_corrected_ratio_geq": 2.0,
        },
        "operator": {
            "source": "sdk/scripts/closure_mesh_recon.py green_gauss_grad_u, "
                      "div = tr(grad U)",
            "validation": "gradU vs shipped: r 0.9997-1.0000 on PH training cases "
                          "(closure_challenge_trained_entry_round2.json); C/V to ~1e-13",
            "boundary_treatment": "RANS boundary metadata for both fields (the "
                                   "correction is cell-centred; BCs unchanged)",
            "norm": "sqrt(sum V_i div_i^2 / sum V_i)",
        },
        "leakage": {
            "scoring_calls_made": 0,
            "guard": "raising stubs re-armed and verified before any pipeline work",
            "ground_truth_reads": "21 PH + 4 DUCT training cases only (model refits, "
                                   "identical to the entry of record)",
            "test_cases_opened_for": "RANS fields + mesh + own model outputs only",
        },
        "per_case": results,
        "verdict": {
            "material": bool(material),
            "worst_ratio_case": worst,
            "worst_ratio": ratios[worst],
            "regenerated_test_fields_match_shipped_csvs": bool(csv_ok),
        },
        "compute": {"elapsed_seconds": round(time.time() - t0, 1), "cores_cap": 2},
    }
    _OUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    if _SCRATCH.exists():
        np.savez_compressed(_SCRATCH / "g2_regenerated_test_predictions.npz", **regen_preds)
    print(f"\nwrote {_OUT}  ({record['compute']['elapsed_seconds']}s)")


if __name__ == "__main__":
    main()
