"""Offline evidence for the closure-challenge RANS-identity reference floor.

This is NOT a training run and installs no ML framework. It measures two
things against the external benchmark's OWN scoring code, so a displayed
number always has a re-derivable source behind it:

1. LEADERBOARD REPRODUCTION: scores the benchmark's own bundled submission
   (submissions/montoya) with the benchmark's own ``closure_challenge``
   package, and checks the result against the docket's recorded target
   (rank 4, overall 0.0779, 8 named per-case values). This is an
   independent check that a previously-displayed external figure is real,
   not a claim of our own.

2. RANS-IDENTITY REFERENCE FLOOR: takes the converged k-omega SST velocity
   field the benchmark repo already ships as an input feature for each of
   the 8 test cases (no ML correction, no training, no fitted parameter of
   any kind), nearest-neighbor interpolates it onto the benchmark's own
   evaluation points, and scores it with the benchmark's own
   ``closure_challenge.score()``. This quantifies how much the published,
   trained entries add over doing nothing -- it is a reference floor, not a
   competing submission, and is labeled that way throughout.

REQUIRED, NOT BUNDLED: this script does not ship, vendor, or copy any of the
benchmark's data or ground truth into this repository. The data repository
(github.com/rmcconke/closure-challenge-benchmark) carries no LICENSE file
and its GitHub API license field is null, so its redistribution terms are
unstated; only the separate evaluation-code package
(github.com/rmcconke/closure-challenge) is MIT. You must point this script
at your own scratch clones of both repositories (outside this repo) and
have the ``closure_challenge`` package importable (installed from the
eval-code clone, editable, or from PyPI).

Setup (outside this repository, e.g. in $HOME, never under Certonomous/)::

    git clone https://github.com/rmcconke/closure-challenge-benchmark.git
    git clone https://github.com/rmcconke/closure-challenge.git closure-challenge-pkg
    python -m venv ~/closure-venv && source ~/closure-venv/bin/activate
    pip install numpy scipy ofpp
    pip install -e ~/closure-challenge-pkg

Run (at most a few cores; this is seconds of compute, not a batch job)::

    export CLOSURE_BENCHMARK_DIR=~/closure-challenge-benchmark   # optional, this is the default
    export CLOSURE_EVAL_PKG_DIR=~/closure-challenge-pkg          # optional, this is the default
    taskset -c 0-3 python sdk/scripts/run_closure_challenge_evidence.py

Writes ``demo-output/website/closure_challenge_rans_floor.json``.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path

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

_SDK = Path(__file__).resolve().parents[1]
_REPO = _SDK.parent
_OUT = lab_paths.web_file("closure_challenge_rans_floor.json")

_DEFAULT_BENCHMARK_DIR = Path.home() / "closure-challenge-benchmark"
_DEFAULT_EVAL_PKG_DIR = Path.home() / "closure-challenge-pkg"

BENCHMARK_DIR = Path(os.environ.get("CLOSURE_BENCHMARK_DIR", str(_DEFAULT_BENCHMARK_DIR)))
EVAL_PKG_DIR = Path(os.environ.get("CLOSURE_EVAL_PKG_DIR", str(_DEFAULT_EVAL_PKG_DIR)))

# Converged RANS-solution timestep per test case (the mesh is static; this is
# just which written time directory holds the solved, non-initial field).
# Verified by directory listing against each case's own scratch clone.
_RANS_TIME = {
    "alpha_15_13929_4048": ("data/Parm_PH_29/alpha_15/alpha_15_13929_4048", "20000"),
    "alpha_15_13929_2024": ("data/Parm_PH_29/alpha_15/alpha_15_13929_2024", "20000"),
    "alpha_05_4071_4048": ("data/Parm_PH_29/alpha_05/alpha_05_4071_4048", "20000"),
    "alpha_05_4071_2024": ("data/Parm_PH_29/alpha_05/alpha_05_4071_2024", "20000"),
    "AR_1_Ret_360": ("data/DUCT/AR_1_Ret_360", "405"),
    "AR_3_Ret_360": ("data/DUCT/AR_3_Ret_360", "1540"),
    "AR_14_Ret_180": ("data/DUCT/AR_14_Ret_180", "7009"),
    "NASA_2DWMH": ("data/NASA_2DWMH", "2000"),
}
# Coordinate field lives in "constant/C" for the DUCT cases (mesh predates any
# written time directory) and in "<time>/C" for the others.
_COORD_SUBPATH = {
    "AR_1_Ret_360": "constant/C",
    "AR_3_Ret_360": "constant/C",
    "AR_14_Ret_180": "constant/C",
}


def _git_commit(repo_dir: Path) -> str | None:
    if not (repo_dir / ".git").exists():
        return None
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_dir), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True, timeout=10,
        )
        return out.stdout.strip()
    except Exception:
        return None


def _git_commit_date(repo_dir: Path) -> str | None:
    if not (repo_dir / ".git").exists():
        return None
    try:
        out = subprocess.run(
            ["git", "-C", str(repo_dir), "log", "-1", "--format=%ai"],
            capture_output=True, text=True, check=True, timeout=10,
        )
        return out.stdout.strip()
    except Exception:
        return None


def main() -> None:
    if not BENCHMARK_DIR.exists():
        print(f"ERROR: benchmark scratch clone not found at {BENCHMARK_DIR}.", file=sys.stderr)
        print("Clone it first (see this script's module docstring) and/or set "
              "CLOSURE_BENCHMARK_DIR. Refusing to fabricate a result.", file=sys.stderr)
        sys.exit(1)

    if str(EVAL_PKG_DIR / "src") not in sys.path:
        sys.path.insert(0, str(EVAL_PKG_DIR / "src"))

    try:
        from closure_challenge import (case_names, evaluate_by_case,
                                        evaluate_from_csv_by_case, score,
                                        score_from_csv)
    except ImportError as exc:
        print(f"ERROR: closure_challenge is not importable ({exc}). Install it from "
              f"{EVAL_PKG_DIR} (pip install -e ...) or from PyPI, then re-run.",
              file=sys.stderr)
        sys.exit(1)

    import closure_challenge as _cc
    try:
        import Ofpp
        from Ofpp import parse_internal_field
    except ImportError as exc:
        print(f"ERROR: Ofpp is not importable ({exc}). pip install ofpp, then re-run.",
              file=sys.stderr)
        sys.exit(1)
    from scipy.interpolate import NearestNDInterpolator

    os.chdir(BENCHMARK_DIR)

    expected_cases = set(_RANS_TIME.keys())
    actual_cases = set(case_names())
    if expected_cases != actual_cases:
        print(f"ERROR: case set mismatch. Expected {sorted(expected_cases)}, "
              f"harness reports {sorted(actual_cases)}. The benchmark repo may "
              "have changed its test cases since this script was written.",
              file=sys.stderr)
        sys.exit(1)

    # --- Part 1: leaderboard reproduction (their own submission, their own
    # scorer; this checks a PREVIOUSLY DISPLAYED external figure, not ours) --
    montoya_score = score_from_csv(os.path.join("submissions", "montoya"))
    montoya_cases = evaluate_from_csv_by_case(os.path.join("submissions", "montoya"))
    docket_recorded_rank4 = {
        "overall": 0.0779,
        "per_case": [0.068, 0.1364, 0.0591, 0.0882, 0.0895, 0.0866, 0.0487, 0.0464],
    }
    reproduced_matches_docket = (
        round(float(montoya_score), 4) == docket_recorded_rank4["overall"]
        and [round(float(v), 4) for v in montoya_cases.values()]
        == docket_recorded_rank4["per_case"]
    )

    # --- Part 2: RANS-identity reference floor (zero ML, zero training) -----
    predictions = {}
    for case, (case_path, time_dir) in _RANS_TIME.items():
        coord_subpath = _COORD_SUBPATH.get(case, f"{time_dir}/C")
        coords = parse_internal_field(os.path.join(case_path, coord_subpath))
        u_rans = parse_internal_field(os.path.join(case_path, time_dir, "U"))
        assert coords.shape[0] == u_rans.shape[0], f"{case}: mesh/field size mismatch"
        xyz_eval = _cc.evaluation_points(case)
        predictions[case] = NearestNDInterpolator(coords, u_rans)(xyz_eval)

    per_case_floor = {c: float(v) for c, v in evaluate_by_case(predictions).items()}
    overall_floor = float(score(predictions))

    record = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "measured_date": str(date.today()),
        "purpose": (
            "Machine-readable, re-derivable evidence behind the "
            "closure-challenge RANS-identity reference floor and the "
            "independent reproduction of the docket's recorded external "
            "leaderboard figures. No benchmark data files are stored in "
            "this repository; every number here is regenerated from a "
            "scratch clone plus this script."
        ),
        "no_benchmark_data_in_repo": True,
        "provenance": {
            "benchmark_repo_url": "https://github.com/rmcconke/closure-challenge-benchmark",
            "benchmark_repo_commit": _git_commit(BENCHMARK_DIR),
            "benchmark_repo_commit_date": _git_commit_date(BENCHMARK_DIR),
            "eval_package_repo_url": "https://github.com/rmcconke/closure-challenge",
            "eval_package_repo_commit": _git_commit(EVAL_PKG_DIR),
            "eval_package_repo_commit_date": _git_commit_date(EVAL_PKG_DIR),
            "eval_package_reported_version": getattr(_cc, "__version__", None),
            "scratch_clone_dirs_used_this_run": {
                "benchmark": str(BENCHMARK_DIR),
                "eval_package": str(EVAL_PKG_DIR),
            },
            "script": "sdk/scripts/run_closure_challenge_evidence.py",
        },
        "metric_definition": {
            "per_case": (
                "scaled MAE = mean(||U_pred - U_true||) over the case's 1000 "
                "fixed evaluation points, divided by mean(||U_true||)"
            ),
            "overall": "plain mean of the 8 per-case scaled MAE values, lower is better",
            "source": "closure_challenge/eval.py, evaluate_individual_case() and score()",
        },
        "leaderboard_reproduction": {
            "description": (
                "Reproduces the benchmark's OWN rank-4 submission (Montoya, "
                "Oulghelou, and Cinnella) through the benchmark's OWN scorer, "
                "to check the figures already displayed in this lab's "
                "benchmarks.json before this run."
            ),
            "measured_overall": round(float(montoya_score), 4),
            "measured_per_case": [round(float(v), 4) for v in montoya_cases.values()],
            "matches_docket_recorded_target": reproduced_matches_docket,
            "docket_recorded_target": docket_recorded_rank4,
        },
        "rans_identity_reference_floor": {
            "description": (
                "Zero-ML, zero-training reference point: the k-omega SST "
                "RANS velocity field the benchmark ships as an input "
                "feature, unmodified, interpolated onto the official "
                "evaluation points and scored with the unmodified "
                "closure_challenge.score(). This is a floor that quantifies "
                "how much the published entries add over raw RANS -- it is "
                "not itself a competing submission and should not be "
                "presented as one."
            ),
            "interpolation_method": "nearest-neighbor (scipy NearestNDInterpolator), "
                                     "the same method the package's own README/tests use as their example",
            "overall_score": round(overall_floor, 4),
            "per_case_scores": {c: round(v, 4) for c, v in per_case_floor.items()},
            "comparison_to_docket_rank4": round(overall_floor - docket_recorded_rank4["overall"], 4),
        },
        "no_ml_framework_installed": True,
        "packages_used": ["numpy", "scipy", "Ofpp", "closure_challenge"],
    }

    _OUT.parent.mkdir(parents=True, exist_ok=True)
    _OUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(record, indent=2))
    print(f"\nWrote {_OUT}")


if __name__ == "__main__":
    main()
