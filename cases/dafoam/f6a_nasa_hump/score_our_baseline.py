import sys, json
sys.path.insert(0, '/home/ubuntu/closure-challenge-pkg/src')
from closure_challenge.eval import evaluate_individual_case
import closure_challenge as cc
from Ofpp import parse_internal_field
from scipy.interpolate import NearestNDInterpolator
import numpy as np

case = "NASA_2DWMH"
OURS_DIR = "/home/ubuntu/Certonomous/demo-output/website/dafoam/f6a_nasa_hump/case"
REF_DIR = "/home/ubuntu/closure-challenge-benchmark/data/NASA_2DWMH"
PUBLISHED_FLOOR = 0.0621

coords_ours = parse_internal_field(f"{OURS_DIR}/0/C")
u_ours = parse_internal_field(f"{OURS_DIR}/1772/U")
assert coords_ours.shape[0] == u_ours.shape[0], (coords_ours.shape, u_ours.shape)

coords_ref = parse_internal_field(f"{REF_DIR}/0/C")
u_ref = parse_internal_field(f"{REF_DIR}/2000/U")
assert coords_ref.shape[0] == u_ref.shape[0], (coords_ref.shape, u_ref.shape)

coord_diff = float(np.abs(coords_ours - coords_ref).max())

xyz_eval = cc.evaluation_points(case)
pred_ours = NearestNDInterpolator(coords_ours, u_ours)(xyz_eval)
pred_ref = NearestNDInterpolator(coords_ref, u_ref)(xyz_eval)

score_ours = float(evaluate_individual_case(case, {case: pred_ours}))
score_ref_reproduced = float(evaluate_individual_case(case, {case: pred_ref}))

u_mag_ref = np.linalg.norm(u_ref, axis=1)
u_mag_diff = np.linalg.norm(u_ours - u_ref, axis=1)
field_scaled_mae = float(np.mean(u_mag_diff) / np.mean(u_mag_ref))

report = {
    "case": case,
    "max_coord_diff_same_mesh_sanity_check": coord_diff,
    "our_converged_iteration": 1772,
    "benchmark_converged_iteration": 2000,
    "our_score_at_eval_points": round(score_ours, 4),
    "reproduced_benchmark_score_at_eval_points": round(score_ref_reproduced, 4),
    "published_floor_json_value": PUBLISHED_FLOOR,
    "deviation_ours_minus_published_floor": round(score_ours - PUBLISHED_FLOOR, 4),
    "internal_field_scaled_mae_ours_vs_benchmark_baseline": round(field_scaled_mae, 6),
}
print(json.dumps(report, indent=2))
with open(f"{OURS_DIR}/score_our_baseline_result.json", "w") as f:
    json.dump(report, f, indent=2)
