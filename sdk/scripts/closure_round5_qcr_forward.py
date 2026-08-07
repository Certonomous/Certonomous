"""Round 5: the QCR forward route, executed under the frozen rule.

Item `w3-qcr-forward-on-the-ducts-is-the-rank-1-route` (approved and claimed
2026-08-05 under Katie's blanket approval + rank-1 directive). The application
rule was frozen and committed BEFORE any solve
(demo-output/website/campaign/R5_RULE_FREEZE.md, commit 0bade54a): QCR ships
on ALL three test ducts or on NONE, decided by AR_7_Ret_180 alone.

THE GATE, MEASURED (validation_AR7.json, 2026-08-05/07):
  V1 QCR/SST scaled MAE ratio 0.4770 <= 0.70          PASS
  V2 in-plane Pearson r 0.9284 >= 0.85                PASS
  V3 both arms converged on residualControl           PASS
  -> verdict ALL: QCR replaces the ML duct correction on AR_1_Ret_360,
     AR_3_Ret_360 and AR_14_Ret_180. The five non-duct CSVs are copied
     byte-identical from round 4 and hash-asserted.

TEST-BLIND. The three test ducts were opened for RANS inputs and mesh only;
the *_LES truth files were never copied into the solve directories, so no
test ground truth was even present in the run tree. The scoring guard below
stubs every scoring/truth entry point of the evaluation package before any
case is touched; `evaluation_points` is captured coords-only first, exactly
the round-4 precedent (closure_round4_duct_rescale.py used it as
"coordinates only"; closure_divergence_audit.py's guard is the stub pattern).

NO SCORING CALL. This script makes none and proves it by armed stubs. The
round-5 scoring decision belongs to the supervisor; the ledger stays at 5
distinct prediction sets scored.

Physicality (audit G2): the QCR fields come out of a solenoidal SIMPLE solve,
so unlike the round-4 post-hoc deltaU they satisfy continuity by
construction. This script MEASURES that through the identical validated
Green-Gauss operator the audit used, rather than asserting it.

Run::
    /home/ubuntu/closure-venv/bin/python sdk/scripts/closure_round5_qcr_forward.py
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

_SDK = Path(__file__).resolve().parent
_REPO = _SDK.parent.parent
sys.path.insert(0, str(_SDK))

import closure_mesh_recon as mr  # noqa: E402
import train_closure_periodic_hill_correction as ph  # noqa: E402
import Ofpp  # noqa: E402
from scipy.interpolate import NearestNDInterpolator  # noqa: E402

_WEB = _REPO / "demo-output" / "website"
_R4_DIR = _WEB / "closure_challenge_submission_round4" / "test"
_R4_MANIFEST = _WEB / "closure_challenge_submission_round4" / "MANIFEST.json"
_OUT_DIR = _WEB / "closure_challenge_submission_round5" / "test"
_OUT_JSON = _WEB / "closure_challenge_round5_qcr_forward.json"
_RUN = Path("/home/ubuntu/certonomous-runs/w3-qcr-rank1")
_BENCH = Path("/home/ubuntu/closure-challenge-benchmark/data/DUCT")

_FMT = "%.10g"

DUCT_TEST = {"AR_1_Ret_360": 395, "AR_3_Ret_360": 1956, "AR_14_Ret_180": 8947}
CAPS = {"AR_1_Ret_360": 3000, "AR_3_Ret_360": 6000, "AR_14_Ret_180": 14000,
        "AR_7_Ret_180": 12000}
UNCHANGED = ["alpha_15_13929_4048", "alpha_15_13929_2024",
             "alpha_05_4071_4048", "alpha_05_4071_2024", "NASA_2DWMH"]
AR7_ARMS = {"AR_7_Ret_180_sst": 4652, "AR_7_Ret_180_qcr": 4660}


class ScoringCallRefused(RuntimeError):
    pass


def _arm_guard():
    """Import the evaluation package solely to capture coords-only access,
    then stub every scoring / truth entry point so a scoring call is
    impossible from this process."""
    if str(ph.EVAL_PKG_DIR / "src") not in sys.path:
        sys.path.insert(0, str(ph.EVAL_PKG_DIR / "src"))
    import closure_challenge as cc
    from closure_challenge import dataset_utils as du
    from closure_challenge import eval as ev

    # Evaluation coordinates come from the benchmark's own shipped
    # convenience files (README: "These points are also provided for
    # convenience under data/evaluation_points") -- plain coordinate CSVs,
    # so this script never touches the truth dict at all, which is strictly
    # cleaner than the round-4 evaluation_points() route.
    def _pts(case):
        p = _BENCH.parent / "evaluation_points" / f"{case}_points.csv"
        pts = np.loadtxt(p, delimiter=",")   # headerless 1000x3, verified
        assert pts.shape == (1000, 3), pts.shape
        return pts

    def _refuse(name):
        def _raiser(*_a, **_kw):
            raise ScoringCallRefused(
                f"{name}() was called by closure_round5_qcr_forward.py. "
                "Round 5 is pre-registered NO-SCORING in this session; the "
                "scoring decision belongs to the supervisor.")
        return _raiser

    blocked = ("score", "score_from_csv", "evaluate_by_case",
               "evaluate_from_csv_by_case", "evaluate_individual_case",
               "_velocity_field", "_ground_truth", "_load_csv_predictions",
               "evaluation_points")
    for mod in (cc, du, ev):
        for name in blocked:
            if hasattr(mod, name):
                setattr(mod, name, _refuse(name))
    try:
        cc.score_from_csv(str(_OUT_DIR))
    except ScoringCallRefused:
        print("[guard] verified: closure_challenge.score_from_csv() now raises")
    else:
        raise SystemExit("scoring guard failed to arm; refusing to continue")
    return _pts


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _div_stats(arm_dir: Path, t: int):
    """Volume-weighted RMS divergence of the arm's converged U through the
    audit's validated Green-Gauss operator (closure_mesh_recon)."""
    mesh = mr.Mesh(arm_dir)
    C, V = mr.reconstruct_cell_centres_vols(mesh)
    u_path = arm_dir / str(t) / "U"
    U = Ofpp.parse_internal_field(str(u_path))
    assert C.shape[0] == U.shape[0]
    ub = mr.read_vector_boundary_field(u_path, list(mesh.boundary.keys()))
    g = mr.green_gauss_grad_u(mesh, U, C, V, ub)
    div = g[:, 0] + g[:, 4] + g[:, 8]
    w = V / V.sum()
    return (float(np.sqrt(np.sum(w * div ** 2))),
            float(np.sqrt(np.sum(w * np.sum(g ** 2, axis=1)))), U, C)


def main() -> None:
    pts_fn = _arm_guard()

    rec: dict = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "item": "w3-qcr-forward-on-the-ducts-is-the-rank-1-route",
        "rule_freeze": "demo-output/website/campaign/R5_RULE_FREEZE.md @ 0bade54a, "
                       "written and committed before any solve",
        "model": {"RASModel": "kOmegaSSTQCR", "Ccr1": 0.3, "trained": False,
                  "library_commit": "303247bb",
                  "library_sha256": "b741839596bc8624789652fdc69b476594dc24419e"
                                    "dd21faedac004e2c1cc808"},
        "validation_gate": json.loads((_RUN / "validation_AR7.json").read_text()),
        "scoring_calls_made_by_this_run": 0,
    }
    assert rec["validation_gate"]["gate_ALL_OR_NONE"] == "ALL"

    # ------------------------------------------------------------------
    # 1. Convergence + physicality of every arm this route ran.
    # ------------------------------------------------------------------
    conv = {}
    fields = {}
    for arm, t in {**AR7_ARMS, **{f"{c}_qcr": t for c, t in DUCT_TEST.items()}}.items():
        case = arm.replace("_sst", "").replace("_qcr", "")
        log = (_RUN / arm / "log.simpleFoam").read_text()
        assert f"SIMPLE solution converged in {t} iterations" in log, arm
        rms_div, rms_grad, U, C = _div_stats(_RUN / arm, t)
        conv[arm] = {"iterations": t, "cap": CAPS[case],
                     "converged_on_residualControl": True,
                     "rms_div_U": rms_div,
                     "rms_gradU_frobenius": rms_grad,
                     "div_over_grad": rms_div / rms_grad}
        fields[arm] = (U, C)
        print(f"{arm:22s} converged {t:5d}/{CAPS[case]:5d}  "
              f"rms div(U) = {rms_div:.3e}  (|gradU| = {rms_grad:.3e})")
    rec["arms"] = conv

    # ------------------------------------------------------------------
    # 2. The three duct CSVs from the converged QCR fields. RANS-side only.
    # ------------------------------------------------------------------
    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    new_hashes = {}
    for case in DUCT_TEST:
        arm = f"{case}_qcr"
        U, _ = fields[arm]
        C = Ofpp.parse_internal_field(str(_BENCH / case / "constant" / "C"))
        assert C.shape[0] == U.shape[0], case
        pts = pts_fn(case)  # coordinates only
        pred = NearestNDInterpolator(C, U)(pts)
        assert pred.shape == (1000, 3), f"{case}: {pred.shape}"
        assert np.isfinite(pred).all(), f"{case}: non-finite prediction"
        out = _OUT_DIR / f"{case}.csv"
        np.savetxt(out, pred, delimiter=",", fmt=_FMT)
        new_hashes[case] = _sha256(out)
        print(f"  {case:16s} csv written, sha256 {new_hashes[case][:12]}…")
    rec["duct_csvs_sha256"] = new_hashes

    # ------------------------------------------------------------------
    # 3. Copy the five unchanged CSVs and prove them unchanged.
    # ------------------------------------------------------------------
    r4 = json.loads(_R4_MANIFEST.read_text())
    r4_hashes = {}
    for k, v in r4.items():
        if isinstance(v, dict):
            for kk, vv in v.items():
                if isinstance(vv, dict) and "sha256" in vv:
                    r4_hashes[kk.replace(".csv", "")] = vv["sha256"]
                elif isinstance(vv, str) and len(vv) == 64:
                    r4_hashes[kk.replace(".csv", "")] = vv
    copied = {}
    for c in UNCHANGED:
        src, dst = _R4_DIR / f"{c}.csv", _OUT_DIR / f"{c}.csv"
        shutil.copyfile(src, dst)
        h = _sha256(dst)
        assert c in r4_hashes and h == r4_hashes[c], \
            f"{c}: hash differs from round-4 manifest"
        copied[c] = h
    rec["unchanged_cases_sha256"] = copied
    print(f"copied {len(copied)} unchanged CSVs, all hash-verified against "
          "the round-4 manifest")

    rec["what_ships"] = {
        "changed": sorted(DUCT_TEST), "unchanged": UNCHANGED,
        "rule": "all-or-none, frozen 0bade54a; verdict ALL on AR_7 evidence"}
    _OUT_JSON.write_text(json.dumps(rec, indent=2))
    print(f"wrote {_OUT_JSON}")
    print("NO scoring call was made; the guard held for the whole run.")


if __name__ == "__main__":
    main()
