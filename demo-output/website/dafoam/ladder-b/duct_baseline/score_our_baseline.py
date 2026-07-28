"""B2 evidence: score OUR OWN uncorrected k-omega SST RANS baseline (run
with this box's OpenFOAM v2606, not the benchmark authors' original OpenFOAM
v7 + custom library) against the benchmark's own per-case scorer
(closure_challenge.evaluate_individual_case, the exact function behind the
published RANS-identity floor), and separately against the benchmark's own
shipped baseline field (the RANS-identity floor's source field) directly.

Only forward evaluation happens here: an uncorrected RANS field is scored
against ground truth via the benchmark's own unmodified scorer, the same
operation already performed for closure_challenge_rans_floor.json. Nothing
is fit, tuned, or selected using the ground-truth fields -- this is a
one-shot measurement, matching the floor script's own precedent.

Only touches AR_1_Ret_360 / AR_3_Ret_360 (test cases) as B2 requires; does
not evaluate or reference any other case.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

BENCHMARK_DIR = Path(os.environ.get("CLOSURE_BENCHMARK_DIR", str(Path.home() / "closure-challenge-benchmark")))
EVAL_PKG_DIR = Path(os.environ.get("CLOSURE_EVAL_PKG_DIR", str(Path.home() / "closure-challenge-pkg")))
HERE = Path(__file__).resolve().parent

if str(EVAL_PKG_DIR / "src") not in sys.path:
    sys.path.insert(0, str(EVAL_PKG_DIR / "src"))

from closure_challenge.eval import evaluate_individual_case
import closure_challenge as _cc
from Ofpp import parse_internal_field
from scipy.interpolate import NearestNDInterpolator
import numpy as np

OUR_TIME = {"AR_1_Ret_360": "456", "AR_3_Ret_360": "1700"}
REF_TIME = {"AR_1_Ret_360": "405", "AR_3_Ret_360": "1540"}
PUBLISHED_FLOOR = {"AR_1_Ret_360": 0.1288, "AR_3_Ret_360": 0.1243}

report = {"per_case": {}}

for case in ("AR_1_Ret_360", "AR_3_Ret_360"):
    coords = parse_internal_field(str(HERE / case / "constant" / "C"))
    u_ours = parse_internal_field(str(HERE / case / OUR_TIME[case] / "U"))
    assert coords.shape[0] == u_ours.shape[0], f"{case}: our field/mesh size mismatch"

    ref_case_dir = BENCHMARK_DIR / "data" / "DUCT" / case
    coords_ref = parse_internal_field(str(ref_case_dir / "constant" / "C"))
    u_ref = parse_internal_field(str(ref_case_dir / REF_TIME[case] / "U"))
    assert coords_ref.shape[0] == u_ref.shape[0], f"{case}: benchmark field/mesh size mismatch"
    assert coords.shape[0] == coords_ref.shape[0], (
        f"{case}: our mesh ({coords.shape[0]} cells) and benchmark mesh "
        f"({coords_ref.shape[0]} cells) cell counts differ"
    )
    coord_diff = float(np.abs(coords - coords_ref).max())

    xyz_eval = _cc.evaluation_points(case)
    pred_ours = NearestNDInterpolator(coords, u_ours)(xyz_eval)
    pred_ref = NearestNDInterpolator(coords_ref, u_ref)(xyz_eval)

    score_ours = float(evaluate_individual_case(case, {case: pred_ours}))
    score_ref_reproduced = float(evaluate_individual_case(case, {case: pred_ref}))

    u_mag_ref = np.linalg.norm(u_ref, axis=1)
    u_mag_diff = np.linalg.norm(u_ours - u_ref, axis=1)
    field_scaled_mae = float(np.mean(u_mag_diff) / np.mean(u_mag_ref))

    report["per_case"][case] = {
        "max_coord_diff_same_mesh_sanity_check": coord_diff,
        "our_converged_iteration": OUR_TIME[case],
        "benchmark_converged_iteration": REF_TIME[case],
        "our_score_at_eval_points": round(score_ours, 4),
        "reproduced_benchmark_score_at_eval_points": round(score_ref_reproduced, 4),
        "published_floor_json_value": PUBLISHED_FLOOR[case],
        "deviation_ours_minus_published_floor": round(score_ours - PUBLISHED_FLOOR[case], 4),
        "internal_field_scaled_mae_ours_vs_benchmark_baseline": round(field_scaled_mae, 6),
    }

print(json.dumps(report, indent=2))
out_path = HERE / "score_our_baseline_result.json"
out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(f"\nWrote {out_path}")
