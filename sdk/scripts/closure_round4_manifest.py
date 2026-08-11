"""G4 of the methods audit (CLOSURE_METHODS_COMPARISON.md, ac2f37ee): close
the round-4 manifest gap.

The round-4 submission directory carried no MANIFEST.json and the three duct
CSVs that ARE round 4 (AR_1_Ret_360, AR_3_Ret_360, AR_14_Ret_180) had no
recorded SHA-256 -- the manifest discipline of rounds 1-3 covered only the
five copied cases. This script writes
demo-output/website/closure_challenge_submission_round4/MANIFEST.json with
the same schema as the round-3 manifest
(demo-output/website/closure_challenge_submission/MANIFEST.json), hashing all
eight files.

ZERO SCORING RISK BY CONSTRUCTION: this script never imports
closure_challenge at all. It reads CSV bytes, the two existing manifest/entry
records, and the regenerated eval-point predictions that
closure_divergence_audit.py verified against the shipped CSVs (for the
max_roundtrip_abs_error column). No benchmark data of any kind is opened.

Run::
    /home/ubuntu/closure-venv/bin/python sdk/scripts/closure_round4_manifest.py
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import time
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np

_REPO = Path(__file__).resolve().parents[2]
_WEB = _REPO / "demo-output" / "website"
_R3_MANIFEST = _WEB / "closure_challenge_submission" / "MANIFEST.json"
_R4_DIR = _WEB / "closure_challenge_submission_round4"
_R4_TEST = _R4_DIR / "test"
_R4_ENTRY = _WEB / "closure_challenge_trained_entry_round4_duct.json"
_OUT = _R4_DIR / "MANIFEST.json"
_SCRATCH = Path(os.environ.get(
    "CLOSURE_SCRATCH",
    "/tmp/claude-1000/-home-ubuntu-Certonomous/64b13819-ff95-4d4d-a50f-3720bab19084/scratchpad"))

UNCHANGED = ["alpha_15_13929_4048", "alpha_15_13929_2024",
             "alpha_05_4071_4048", "alpha_05_4071_2024", "NASA_2DWMH"]
DUCT_NEW = ["AR_1_Ret_360", "AR_3_Ret_360", "AR_14_Ret_180"]
# Interim anchor recorded by the methods audit (ac2f37ee, G4) for the first
# duct CSV -- abbreviated there as c007e120...ce1d.
AUDIT_ANCHOR = {"AR_1_Ret_360": ("c007e120", "ce1d")}


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _git_head(repo: Path) -> str:
    return subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True,
                          timeout=10).stdout.strip()


def main() -> None:
    t0 = time.time()
    r3 = json.loads(_R3_MANIFEST.read_text())
    entry = json.loads(_R4_ENTRY.read_text())
    regen = np.load(_SCRATCH / "g2_regenerated_test_predictions.npz")

    files = {}
    checks = {"unchanged_match_round3_manifest": True,
              "unchanged_match_round4_entry_record": True,
              "duct_csvs_match_divergence_audit_regeneration": True,
              "audit_interim_anchor_matches": True}

    for c in sorted(UNCHANGED + DUCT_NEW):
        p = _R4_TEST / f"{c}.csv"
        arr = np.loadtxt(p, delimiter=",")
        assert arr.shape == (1000, 3), f"{c}: {arr.shape}"
        assert np.isfinite(arr).all(), f"{c}: non-finite values"
        h = _sha256(p)
        roundtrip = float(np.abs(arr - regen[c]).max())
        if c in UNCHANGED:
            r3h = r3["files"][c]["sha256"]
            if h != r3h:
                checks["unchanged_match_round3_manifest"] = False
            if h != entry["unchanged_cases_sha256"][c]:
                checks["unchanged_match_round4_entry_record"] = False
            src = r3["files"][c]["prediction_source"]
        else:
            # the divergence audit regenerated these fields from the frozen
            # Variant D pipeline and verified them against the shipped bytes
            if roundtrip >= 5e-7:
                checks["duct_csvs_match_divergence_audit_regeneration"] = False
            if c in AUDIT_ANCHOR:
                pre, suf = AUDIT_ANCHOR[c]
                if not (h.startswith(pre) and h.endswith(suf)):
                    checks["audit_interim_anchor_matches"] = False
            src = ("round-4 Variant D duct model (closure_round4_duct_rescale.py; "
                   "pre-registered in closure_challenge_duct_reynolds_transfer.json)")
        files[c] = {
            "file": f"test/{c}.csv",
            "rows": 1000, "cols": 3, "has_header": False, "delimiter": ",",
            "sha256": h,
            "max_roundtrip_abs_error": roundtrip,
            "prediction_source": src,
        }
        print(f"{c:24s} {h[:12]}...  roundtrip {roundtrip:.3g}")

    assert all(checks.values()), f"verification failed: {checks}"

    r4res = entry["official_test_harness_result"]
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "measured_date": str(date.today()),
        "purpose": ("The eight submittable prediction CSVs for the Closure Challenge, "
                    "round 4 (overall 0.0654 -- the entry of record until 2026-08-07, "
                    "when round 5 superseded it at 0.056647191704213645; see "
                    "closure_challenge_round5_qcr.json), hashed and verified "
                    "without making a scoring call. Closes audit finding G4 "
                    "(CLOSURE_METHODS_COMPARISON.md ac2f37ee): the three new duct CSVs "
                    "now carry recorded SHA-256 hashes, matching the manifest discipline "
                    "of rounds 1-3. The gate blocks below are carried verbatim from the "
                    "round-3 manifest: the five non-duct CSVs are byte-identical to that "
                    "submission, so its gate provenance is their provenance."),
        "produced_by": "sdk/scripts/closure_round4_manifest.py",
        "reproduces": "demo-output/website/closure_challenge_trained_entry_round4_duct.json",
        "scoring_calls_made_by_this_run": 0,
        "how_zero_is_guaranteed": (
            "This script never imports closure_challenge and opens no benchmark data. "
            "It reads only the eight CSV files' bytes, the round-3 manifest, the round-4 "
            "entry record, and the regenerated eval-point predictions that "
            "closure_divergence_audit.py produced under an armed raising-stub scoring "
            "guard and verified against the shipped CSVs."),
        "scoring_call_limit_note": (
            "The benchmark imposes no scoring-call limit. It ships the test ground truth "
            "in the evaluation package and instructs submitters to preview their score. "
            "The lab's ledger (five distinct prediction sets scored as of this round-4 "
            "manifest; six after round 5's 2026-08-07 call) is a "
            "self-imposed discipline, stricter than the rules require, and is not "
            "compliance with any benchmark rule."),
        "format": r3["format"],
        "harness": {
            "benchmark_repo_commit": _git_head(Path.home() / "closure-challenge-benchmark"),
            "eval_package_repo_commit": _git_head(Path.home() / "closure-challenge-pkg"),
            "eval_package_version_string_note": r3["harness"]["eval_package_version_string_note"],
        },
        "gate_refit_check": r3["gate_refit_check"],
        "gate_decisions_on_official_ph_test_cases": r3["gate_decisions_on_official_ph_test_cases"],
        "verification_against_entry_of_record": {
            "unchanged_cases_sha256_match_round3_manifest": checks["unchanged_match_round3_manifest"],
            "unchanged_cases_sha256_match_round4_entry_record": checks["unchanged_match_round4_entry_record"],
            "duct_csvs_match_frozen_pipeline_regeneration": checks["duct_csvs_match_divergence_audit_regeneration"],
            "ar_1_ret_360_matches_audit_interim_anchor_c007e120_ce1d": checks["audit_interim_anchor_matches"],
            "benchmark_repo_commit_matches_round3_manifest":
                _git_head(Path.home() / "closure-challenge-benchmark") == r3["harness"]["benchmark_repo_commit"],
            "eval_package_repo_commit_matches_round3_manifest":
                _git_head(Path.home() / "closure-challenge-pkg") == r3["harness"]["eval_package_repo_commit"],
        },
        "recorded_scores_not_recomputed_here": {
            "overall": r4res["round4_overall"],
            "per_case": r4res["round4_per_case"],
            "source": "closure_challenge_trained_entry_round4_duct.json (round-4 run, "
                      "official call #5)",
        },
        "files": files,
        "compute": {"elapsed_seconds": round(time.time() - t0, 1), "cores_cap": 2},
    }
    _OUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {_OUT}")


if __name__ == "__main__":
    main()
