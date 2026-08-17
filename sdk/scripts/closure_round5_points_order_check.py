"""Round-5 support check: prove the benchmark's convenience coordinate files
(data/evaluation_points/<case>_points.csv) are row-for-row the same points, in
the same order, as the coordinates the round-4 CSVs were generated at.

Method, truth-free by construction: retrain the round-4 duct model (variant D,
deterministic, random_state=0, training-duct truth only -- the identical legal
read rounds 1-4 made), predict at the CONVENIENCE-FILE coordinates, and
compare row-wise against the shipped round-4 duct CSVs, which were generated
at closure_challenge.evaluation_points() ordering and scored. Row-wise
agreement at write precision proves the two coordinate sources are identical
in content AND order. No closure_challenge import, no scoring call, no test
ground truth, no npz file opened.

Run::
    /home/ubuntu/closure-venv/bin/python sdk/scripts/closure_round5_points_order_check.py
"""
from __future__ import annotations

import json
import sys
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

_R4_TEST = lab_paths.CLOSURE_SUBMISSION_ROUND4 / "test"
_PTS_DIR = Path("/home/ubuntu/closure-challenge-benchmark/data/evaluation_points")

HP = dict(max_iter=300, max_depth=6, learning_rate=0.05,
          l2_regularization=1.0, random_state=0)
DUCT_TRAIN = ex._DUCT_TRAIN
DUCT_TEST = ["AR_1_Ret_360", "AR_3_Ret_360", "AR_14_Ret_180"]


def _parse(p):
    return Ofpp.parse_internal_field(str(p))


def _features(f):
    X7 = ph.build_features(f["gradU"], f["k"], f["omega"], f["walldist"],
                           f["U"], f["nu"])
    d = f["walldist"]
    return np.hstack([X7, (d / d.max())[:, None]])


def main() -> None:
    Xs, Ys = [], []
    for c in DUCT_TRAIN:
        f = ex._reconstruct_duct_fields(c, _parse)
        u_les = ex._load_duct_ground_truth_U(c, _parse)   # TRAINING duct truth
        uref = float(np.linalg.norm(f["U"], axis=1).mean())
        Xs.append(_features(f))
        Ys.append((u_les - f["U"]) / uref)
    X, Y = np.concatenate(Xs), np.concatenate(Ys)
    models = [HistGradientBoostingRegressor(**HP).fit(X, Y[:, j])
              for j in range(3)]

    out = {}
    for c in DUCT_TEST:
        f = ex._reconstruct_duct_fields(c, _parse)        # RANS + mesh only
        uref = float(np.linalg.norm(f["U"], axis=1).mean())
        d = np.column_stack([m.predict(_features(f)) for m in models]) * uref
        u_mesh = f["U"] + d
        pts = np.loadtxt(_PTS_DIR / f"{c}_points.csv", delimiter=",")
        assert pts.shape == (1000, 3), pts.shape
        pred = NearestNDInterpolator(f["C"], u_mesh)(pts)
        shipped = np.loadtxt(_R4_TEST / f"{c}.csv", delimiter=",")
        out[c] = float(np.abs(pred - shipped).max())
        print(f"{c:16s} max row-wise |regenerated - shipped| = {out[c]:.3e}")
    ok = all(v < 1e-6 for v in out.values())
    print(json.dumps({"max_abs_row_diff": out, "ordering_verified": ok}))
    if not ok:
        raise SystemExit("ordering NOT verified; do not ship round-5 CSVs")


if __name__ == "__main__":
    main()
