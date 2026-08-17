"""
Zero-ML 'identity RANS' baseline for the Closure Challenge benchmark.

This is NOT a trained model. It predicts the raw k-omega SST RANS velocity
field (no data-driven correction at all) for each of the 8 official test
cases, interpolates it onto the official evaluation points, and scores it
with the benchmark's own closure_challenge.score() function.

Purpose: establish a defensible, honestly-labeled floor number using only
the RANS solves already present in the benchmark's own data release, run
through the benchmark's own scoring code. This required no training code
and no ML framework.
"""
import numpy as np
from scipy.interpolate import NearestNDInterpolator
from Ofpp import parse_internal_field
from closure_challenge import score, evaluate_by_case, evaluation_points, case_names

CASES = {
    "alpha_15_13929_4048": {
        "C": "data/Parm_PH_29/alpha_15/alpha_15_13929_4048/20000/C",
        "U": "data/Parm_PH_29/alpha_15/alpha_15_13929_4048/20000/U",
    },
    "alpha_15_13929_2024": {
        "C": "data/Parm_PH_29/alpha_15/alpha_15_13929_2024/20000/C",
        "U": "data/Parm_PH_29/alpha_15/alpha_15_13929_2024/20000/U",
    },
    "alpha_05_4071_4048": {
        "C": "data/Parm_PH_29/alpha_05/alpha_05_4071_4048/20000/C",
        "U": "data/Parm_PH_29/alpha_05/alpha_05_4071_4048/20000/U",
    },
    "alpha_05_4071_2024": {
        "C": "data/Parm_PH_29/alpha_05/alpha_05_4071_2024/20000/C",
        "U": "data/Parm_PH_29/alpha_05/alpha_05_4071_2024/20000/U",
    },
    "AR_1_Ret_360": {
        "C": "data/DUCT/AR_1_Ret_360/constant/C",
        "U": "data/DUCT/AR_1_Ret_360/405/U",
    },
    "AR_3_Ret_360": {
        "C": "data/DUCT/AR_3_Ret_360/constant/C",
        "U": "data/DUCT/AR_3_Ret_360/1540/U",
    },
    "AR_14_Ret_180": {
        "C": "data/DUCT/AR_14_Ret_180/constant/C",
        "U": "data/DUCT/AR_14_Ret_180/7009/U",
    },
    "NASA_2DWMH": {
        "C": "data/NASA_2DWMH/0/C",
        "U": "data/NASA_2DWMH/2000/U",
    },
}

assert set(CASES.keys()) == set(case_names()), (set(CASES.keys()), set(case_names()))

predictions = {}
for case, paths in CASES.items():
    coords = parse_internal_field(paths["C"])
    U_rans = parse_internal_field(paths["U"])
    assert coords.shape[0] == U_rans.shape[0], f"{case}: mesh/field size mismatch"

    xyz_eval = evaluation_points(case)  # (1000, 3)

    interp = NearestNDInterpolator(coords, U_rans)
    U_pred = interp(xyz_eval)

    predictions[case] = U_pred
    print(f"{case}: {coords.shape[0]} RANS cells -> {xyz_eval.shape[0]} eval points")

per_case = evaluate_by_case(predictions)
overall = score(predictions)

print("\nPer-case scaled MAE (RANS identity baseline, no ML correction):")
for case in case_names():
    print(f"  {case}: {per_case[case]:.4f}")

print(f"\nOverall score (mean over 8 cases): {overall:.4f}")
