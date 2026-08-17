"""B2 evidence, added 2026-08-17: WHICH SCORER REVISION IS THIS RECORD SCORED UNDER?

`B2_duct_baseline.json` originally named its scoring environment by version
string only -- `closure_challenge==0.2.1` -- while the venv's package metadata
reports 0.3.1. That read as a version skew. It is not one: both strings come
out of the single editable install at /home/ubuntu/closure-challenge-pkg, which
is pinned at 1c4e22c8, where `__init__.py` says 0.2.1 and `pyproject.toml` says
0.3.1 because upstream bumped one and not the other.

This script settles it from the numbers rather than from the prose, and is the
instrument cited by that record's `data_provenance.amendment_2026_08_17` and by
AWS_TREE_PLAN.md section 7.5.

It re-derives all 14 of the record's scoring figures twice:

  * through the scorer exactly as pinned at 1c4e22c8 (vector-magnitude metric),
  * through `evaluate_individual_case` exactly as it reads at tag v0.2.1
    (4796ce35, componentwise metric), restored from the full local mirror at
    /home/ubuntu/mirrors/closure-challenge.git.

If the record is self-consistent under one revision and not the other, the
version string in its prose is settled by its own figures.

READ-ONLY. It writes nothing, and in particular does not touch
`score_our_baseline_result.json`, the original generator's output. It scores
already-published predictions against already-published figures; nothing is fit,
tuned or selected, and no new number is produced.

Run:
    /home/ubuntu/closure-venv/bin/python \
        demo-output/website/dafoam/ladder-b/duct_baseline/recheck_scorer_revision.py
"""
from __future__ import annotations

import sys
from pathlib import Path

EVAL_PKG_DIR = Path("/home/ubuntu/closure-challenge-pkg")
BENCHMARK_DIR = Path("/home/ubuntu/closure-challenge-benchmark")
HERE = Path(__file__).resolve().parent

if str(EVAL_PKG_DIR / "src") not in sys.path:
    sys.path.insert(0, str(EVAL_PKG_DIR / "src"))

import numpy as np
from Ofpp import parse_internal_field
from scipy.interpolate import NearestNDInterpolator

import closure_challenge as _cc
from closure_challenge.dataset_utils import _velocity_field
from closure_challenge.eval import evaluate_individual_case as eval_pinned


def eval_v021(case, pred):
    """evaluate_individual_case verbatim as it reads at tag v0.2.1 (4796ce35).

    Recover it with, offline, from the mirror:
        git -C /home/ubuntu/mirrors/closure-challenge.git \
            show 4796ce35:src/closure_challenge/eval.py
    """
    U_true = _velocity_field(case)
    mae = np.mean(np.abs(pred - U_true))
    scale = np.mean(np.abs(U_true))
    return mae / scale


OUR_TIME = {"AR_1_Ret_360": "456", "AR_3_Ret_360": "1700"}
REF_TIME = {"AR_1_Ret_360": "405", "AR_3_Ret_360": "1540"}

# The 14 scoring figures exactly as published in B2_duct_baseline.json, and
# how each is derived. "floor" and the two MAE rows never pass through the
# scorer, so they are metric-INDEPENDENT and carry no information about which
# revision ran; they are checked anyway so that the 14 is a real 14.
PUBLISHED = {
    "AR_1_Ret_360": {
        "our_score_at_eval_points": 0.129,
        "reproduced_benchmark_baseline_score_at_eval_points": 0.1288,
        "published_floor_json_value": 0.1288,
        "deviation_ours_minus_published_floor_absolute": 0.0002,
        "deviation_ours_minus_published_floor_relative_pct": 0.16,
        "internal_field_scaled_mae_ours_vs_benchmark_baseline_field": 0.000231,
        "internal_field_scaled_mae_pct": 0.023,
    },
    "AR_3_Ret_360": {
        "our_score_at_eval_points": 0.1251,
        "reproduced_benchmark_baseline_score_at_eval_points": 0.1243,
        "published_floor_json_value": 0.1243,
        "deviation_ours_minus_published_floor_absolute": 0.0008,
        "deviation_ours_minus_published_floor_relative_pct": 0.64,
        "internal_field_scaled_mae_ours_vs_benchmark_baseline_field": 0.000915,
        "internal_field_scaled_mae_pct": 0.09,
    },
}
METRIC_DEPENDENT = (
    "our_score_at_eval_points",
    "reproduced_benchmark_baseline_score_at_eval_points",
    "deviation_ours_minus_published_floor_absolute",
    "deviation_ours_minus_published_floor_relative_pct",
)

# The record's two percentage figures are rounded restatements of the figures
# beside them, not independent measurements: the relative deviation divides the
# ALREADY-ROUNDED absolute deviation by the floor, and the MAE percentage is
# 100x the scaled MAE shown at each case's own precision. Reproduce them on the
# record's own basis, and say so rather than quietly using a uniform rule.
MAE_PCT_DP = {"AR_1_Ret_360": 3, "AR_3_Ret_360": 2}


def main() -> int:
    import importlib.metadata as md

    print(f"closure_challenge.__version__  : {_cc.__version__}   (src/closure_challenge/__init__.py)")
    print(f"importlib.metadata.version()   : {md.version('closure-challenge')}   (dist-info, from pyproject.toml)")
    print("both of the above are the SAME checkout, /home/ubuntu/closure-challenge-pkg @ 1c4e22c8\n")

    tally: dict[str, list[bool]] = {}
    for case in ("AR_1_Ret_360", "AR_3_Ret_360"):
        coords = parse_internal_field(str(HERE / case / "constant" / "C"))
        u_ours = parse_internal_field(str(HERE / case / OUR_TIME[case] / "U"))
        ref_dir = BENCHMARK_DIR / "data" / "DUCT" / case
        coords_ref = parse_internal_field(str(ref_dir / "constant" / "C"))
        u_ref = parse_internal_field(str(ref_dir / REF_TIME[case] / "U"))
        assert coords.shape[0] == coords_ref.shape[0], f"{case}: mesh size mismatch"

        xyz = _cc.evaluation_points(case)
        pred_ours = NearestNDInterpolator(coords, u_ours)(xyz)
        pred_ref = NearestNDInterpolator(coords_ref, u_ref)(xyz)

        floor = PUBLISHED[case]["published_floor_json_value"]
        fmae = float(np.mean(np.linalg.norm(u_ours - u_ref, axis=1))
                     / np.mean(np.linalg.norm(u_ref, axis=1)))

        for label, fn in (("AT PIN 1c4e22c8 (v0.3.1 metric)", eval_pinned),
                          ("AT TAG v0.2.1  (4796ce35 metric)", eval_v021)):
            s_ours = float(fn(case, pred_ours))
            s_ref = float(fn(case, pred_ref))
            dev = round(s_ours - floor, 4)
            mae_r = round(fmae, 6)
            derived = {
                "our_score_at_eval_points": round(s_ours, 4),
                "reproduced_benchmark_baseline_score_at_eval_points": round(s_ref, 4),
                "published_floor_json_value": floor,
                "deviation_ours_minus_published_floor_absolute": dev,
                "deviation_ours_minus_published_floor_relative_pct": round(100.0 * dev / floor, 2),
                "internal_field_scaled_mae_ours_vs_benchmark_baseline_field": mae_r,
                "internal_field_scaled_mae_pct": round(100.0 * mae_r, MAE_PCT_DP[case]),
            }
            print(f"--- {case}   {label} ---")
            for key, want in PUBLISHED[case].items():
                got = derived[key]
                ok = got == want
                dep = "metric-dependent  " if key in METRIC_DEPENDENT else "metric-independent"
                tally.setdefault(label, []).append(ok)
                print(f"  {'MATCH ' if ok else 'DIFFER'} [{dep}] {key}: published={want} derived={got}")
            print()

    print("VERDICT")
    for label, results in tally.items():
        print(f"  {label}: {sum(results)}/{len(results)} of the 14 published figures reproduce exactly")
    pin = tally["AT PIN 1c4e22c8 (v0.3.1 metric)"]
    old = tally["AT TAG v0.2.1  (4796ce35 metric)"]
    ok = all(pin) and not all(old)
    print("\n  The record is self-consistent under the pinned revision and under no other."
          if ok else "\n  UNEXPECTED: re-check by hand before citing this.")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
