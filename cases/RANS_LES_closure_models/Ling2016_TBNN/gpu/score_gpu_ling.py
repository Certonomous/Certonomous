#!/usr/bin/env python3
"""Lab-box CPU comparator for the Ling (2016) TBNN GPU arm.

Loads the CLEAN dataset (/home/ubuntu/closure-data/tbnn/dataset.npz) and the
predictions synced back from gpu1, and writes ONE grading JSON of numbers.
It grades NO verdict — the supervisor grades against the frozen thresholds
(PREREGISTRATION_DRAFT.md sec. 8, G1/G2/G3).

Recorded per model (ARM-A TBNN, ARM-A MLP, ARM-B best) and per baseline
(SST = b_RANS, b = 0, train-mean tensor):
  * per-case b_rms on the 8 TEST cases (per seed: mean / lo / hi over seeds)
  * pooled TEST b_rms per seed (G2 fired on the pooled metric in the CPU lane)
  * realisability: violation fraction on TEST cells, and max ||b||_F
    (thresholds for the supervisor: truth 0.79% x 3 = 2.37%; sqrt(2/3)*2 = 1.633)

Controls, before anything is scored (DRAFT sec. 9):
  G0a — PLANT = 1.234e-03 added to b_LES[k,0,1] and b_LES[k,1,0] of a named,
        recorded cell k in a COPY; the b_rms scorer must see a non-zero
        difference that back-solves to the plant within 1e-9 relative,
        else this script prints its refusal and EXITS 2 with no JSON.
  G0b — a cell forced to b = diag(1,1,-2) must be flagged by the
        realisability reader, else exit 2.

Realisability code: the CPU lane's own (_common/of_read.py, the same function
../analyse_tbnn.py imports) when the repository is importable; otherwise the
identical eigenvalue/barycentric computation embedded below.

Usage:
  /home/ubuntu/closure-venv/bin/python score_gpu_ling.py                # score
  /home/ubuntu/closure-venv/bin/python score_gpu_ling.py --g0-only     # controls only
"""
from __future__ import annotations
import argparse, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "/home/ubuntu/closure-data/tbnn/dataset.npz"
PRED_DIR = "/home/ubuntu/closure-data/tbnn_gpu/out"
OUT_JSON = "/home/ubuntu/closure-data/tbnn_gpu/grading_gpu_ling.json"
PLANT = 1.234e-03                      # the lab's standing planted constant

# ---- frozen split, verbatim from ../train_tbnn.py (CPU lane) ---------------
TEST = {"alpha_15_13929_4048", "alpha_15_13929_2024",
        "alpha_05_4071_4048", "alpha_05_4071_2024",
        "AR_1_Ret_360", "AR_3_Ret_360", "AR_14_Ret_180", "NASA_2DWMH"}
VAL = {"alpha_05_10071_4048", "alpha_05_10071_2024",
       "alpha_15_7929_4048", "alpha_15_7929_2024", "AR_7_Ret_180"}
GROUP_EXCLUDED = {"alpha_15_13929_3036", "alpha_05_4071_3036",
                  "alpha_05_10071_3036", "alpha_15_7929_3036"}

# ---- realisability: prefer the CPU lane's own code --------------------------
_COMMON = os.path.join(os.path.dirname(HERE), "..", "_common")
sys.path.insert(0, os.path.abspath(_COMMON))
try:
    from of_read import realisability_violation           # CPU lane's reader
    REALISABILITY_SOURCE = "_common/of_read.py (CPU lane)"
except ImportError:
    REALISABILITY_SOURCE = "embedded eigenvalue/barycentric fallback"

    def realisability_violation(b, tol=0.0):
        """Banerjee et al. (2007) barycentric coordinates; identical to
        _common/of_read.py:realisability_violation."""
        lam = np.linalg.eigvalsh(b)[:, ::-1]              # descending
        c1 = lam[:, 0] - lam[:, 1]
        c2 = 2.0 * (lam[:, 1] - lam[:, 2])
        c3 = 3.0 * lam[:, 2] + 1.0
        mn = np.stack([c1, c2, c3], axis=1).min(axis=1)
        return mn < -tol, mn


def frob_rms(x):
    """The b_rms scorer: RMS of the Frobenius norm, float64 accumulation."""
    x = np.asarray(x, dtype=np.float64)
    return float(np.sqrt((x ** 2).sum(axis=(1, 2)).mean()))


# --------------------------------------------------------------- G0 controls
def g0_controls(names, cid, valid, bL):
    """G0a + G0b on a COPY of the clean data. Refusal -> exit 2, no JSON."""
    case = sorted(TEST)[0]
    ci = names.index(case)
    rows = np.flatnonzero((cid == ci) & valid)
    k = int(rows[0])                                       # named, recorded cell
    b_clean = bL[(cid == ci) & valid].astype(np.float64)
    b_plant = b_clean.copy()
    b01 = float(b_plant[0, 0, 1])
    b_plant[0, 0, 1] += PLANT
    b_plant[0, 1, 0] += PLANT
    pred = np.zeros_like(b_clean)                          # b = 0 as reference
    # (1) the per-case b_rms scorer must see a NON-ZERO difference
    rms_c = frob_rms(pred - b_clean)
    rms_p = frob_rms(pred - b_plant)
    diff = rms_p - rms_c
    # (2) back-solve through the known SINGLE-CELL contribution to the RMS
    # (DRAFT sec. 9), same scorer on exactly the planted cell: a whole-case
    # float64 back-solve carries ~1e-8 sqrt round-trip error and cannot
    # certify 1e-9 relative; the single-cell contribution can.
    rms_kc = frob_rms((pred - b_clean)[0:1])
    rms_kp = frob_rms((pred - b_plant)[0:1])
    dss = rms_kp ** 2 - rms_kc ** 2                        # = 2((b01+P)^2 - b01^2)
    recovered = -b01 + math.sqrt(max(b01 * b01 + dss / 2.0, 0.0))
    rel = abs(recovered - PLANT) / PLANT
    print(f"[G0a] case={case} cell={k} b01={b01:.6e} diff={diff:.3e} "
          f"recovered={recovered:.9e} rel_err={rel:.3e}", flush=True)
    if diff == 0.0 or rel >= 1e-9:
        print("[G0a] REFUSAL: the b_rms scorer did not read back the plant. "
              "A zero from a reader not shown able to see a non-zero is not "
              "evidence. No grading JSON is written. Exit 2.", flush=True)
        sys.exit(2)

    b_test = b_clean[:64].copy()
    b_test[0] = np.diag([1.0, 1.0, -2.0])
    viol, mn = realisability_violation(b_test)
    print(f"[G0b] forced b=diag(1,1,-2), ||b||_F={math.sqrt(6):.4f}, "
          f"min_bary={mn[0]:.4f}, flagged={bool(viol[0])}", flush=True)
    if not viol[0]:
        print("[G0b] REFUSAL: the realisability reader did not flag "
              "b=diag(1,1,-2). G3 cannot be read. Exit 2.", flush=True)
        sys.exit(2)
    return dict(plant=PLANT, case=case, cell=k, b01_before=b01,
                rms_clean=rms_c, rms_planted=rms_p, diff=diff,
                recovered_plant=recovered, rel_err=rel,
                g0b_flagged=bool(viol[0]), g0b_min_bary=float(mn[0]))


# --------------------------------------------------------------- scoring
def score_pred(pred_test, bL_test, cid_test, names, test_cases):
    """pred_test: (n_test,3,3) in dataset row order over TEST rows."""
    per_case = {}
    for c in test_cases:
        m = cid_test == names.index(c)
        per_case[c] = frob_rms(pred_test[m] - bL_test[m])
    pooled = frob_rms(pred_test - bL_test)
    viol, _ = realisability_violation(pred_test.astype(np.float64))
    return dict(per_case=per_case, pooled=pooled,
                viol_frac=float(viol.mean()),
                max_frob=float(np.sqrt((pred_test.astype(np.float64) ** 2)
                                       .sum(axis=(1, 2)).max())))


def collect_model(tag, nseeds, test_idx, fsub, bL_test, cid_test, names,
                  test_cases, which="pred_best"):
    """Load pred_{tag}_s{seed}.npz files; verify their idx matches the TEST
    rows of the clean dataset; score each seed."""
    seeds = {}
    for s in range(nseeds):
        p = os.path.join(PRED_DIR, f"pred_{tag}_s{s}.npz")
        if not os.path.exists(p):
            continue
        z = np.load(p)
        if not np.array_equal(z["idx"], test_idx):
            print(f"[refuse] {p}: prediction row indices do not match the "
                  "clean dataset's TEST rows. Exit 2.", flush=True)
            sys.exit(2)
        seeds[str(s)] = score_pred(z[which].astype(np.float64)[fsub],
                                   bL_test, cid_test, names, test_cases)
    if not seeds:
        return None
    agg = {}
    for c in test_cases:
        v = [seeds[s]["per_case"][c] for s in seeds]
        agg[c] = dict(mean=float(np.mean(v)), lo=float(min(v)),
                      hi=float(max(v)), n=len(v))
    pooled = {s: seeds[s]["pooled"] for s in seeds}
    return dict(n_seeds=len(seeds), which=which, per_seed=seeds,
                per_case_over_seeds=agg,
                pooled_per_seed=pooled,
                pooled_mean=float(np.mean(list(pooled.values()))),
                pooled_spread=float(max(pooled.values()) - min(pooled.values())))


def main():
    global PRED_DIR
    ap = argparse.ArgumentParser()
    ap.add_argument("--g0-only", action="store_true",
                    help="run the planted controls only (pre-freeze proof)")
    ap.add_argument("--pred-dir", default=PRED_DIR)
    ap.add_argument("--out", default=OUT_JSON)
    args = ap.parse_args()
    PRED_DIR = args.pred_dir

    z = np.load(DATA, allow_pickle=True)
    names = [str(x) for x in z["names"]]
    cid, valid, bL, bR = z["case_id"], z["valid"], z["b_LES"], z["b_RANS"]

    g0 = g0_controls(names, cid, valid, bL)
    if args.g0_only:
        print("[g0-only] controls passed; nothing scored, no JSON written.", flush=True)
        return

    test_cases = sorted(TEST)
    # rows the GPU driver predicted on: the npz `valid` mask (k_LES floor only)
    tmask = np.isin(cid, [names.index(c) for c in test_cases]) & valid
    test_idx = np.flatnonzero(tmask).astype(np.int64)
    # scoring mask: additionally require finite b_LES AND finite b_RANS, so
    # every model and every baseline (SST included) is scored on the IDENTICAL
    # cells — the CPU lane's convention (_common/score_prediction.py: `valid`
    # vs `valid_les_only`, 567 cells apart, all non-finite b_RANS).
    finite = (np.isfinite(bL).all(axis=(1, 2)) & np.isfinite(bR).all(axis=(1, 2)))
    fsub = finite[tmask]                       # within the predicted TEST rows
    bL_test = bL[tmask][fsub].astype(np.float64)
    cid_test = cid[tmask][fsub]
    held = TEST | VAL | GROUP_EXCLUDED
    trmask = (np.isin(cid, [names.index(c) for c in names if c not in held])
              & valid & finite)

    out = dict(written=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               dataset=DATA, pred_dir=PRED_DIR, plant_control=g0,
               realisability_source=REALISABILITY_SOURCE,
               n_test_predicted=int(tmask.sum()), n_test_scored=int(fsub.sum()),
               n_test_dropped_nonfinite_bRANS=int((~fsub).sum()),
               n_train=int(trmask.sum()),
               grades_verdict=False,
               note="numbers only; the supervisor grades against the frozen thresholds",
               models={}, baselines={})

    # ---- baselines: SST (b_RANS), b = 0, train-mean tensor -----------------
    sst = bR[tmask][fsub].astype(np.float64)       # finite by construction
    out["baselines"]["SST"] = score_pred(sst, bL_test, cid_test, names, test_cases)
    out["baselines"]["zero"] = score_pred(np.zeros_like(bL_test),
                                          bL_test, cid_test, names, test_cases)
    bmean = bL[trmask].astype(np.float64).mean(axis=0)
    out["baselines"]["train_mean"] = score_pred(
        np.broadcast_to(bmean, bL_test.shape).copy(),
        bL_test, cid_test, names, test_cases)
    out["baselines"]["train_mean"]["tensor"] = bmean.tolist()
    # truth's own realisability on the same TEST cells, for the G3 ratio
    tviol, _ = realisability_violation(bL_test)
    out["truth_viol_frac_test"] = float(tviol.mean())

    # ---- models ------------------------------------------------------------
    for tag, label, nseeds in (("tbnn", "ARM-A TBNN", 5),
                               ("mlp", "ARM-A MLP", 5),
                               ("armb", "ARM-B best", 5)):
        for which in ("pred_best", "pred_final"):
            m = collect_model(tag, nseeds, test_idx, fsub, bL_test, cid_test,
                              names, test_cases, which=which)
            if m is not None:
                out["models"][f"{label} [{which}]"] = m

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(out, f, indent=1)
    print(f"\n[score] wrote {args.out}", flush=True)
    for name, m in out["baselines"].items():
        print(f"  baseline {name:11s} pooled={m['pooled']:.4f} "
              f"viol={m['viol_frac']*100:.2f}% max||b||={m['max_frob']:.3f}", flush=True)
    for name, m in out["models"].items():
        print(f"  {name:26s} pooled_mean={m['pooled_mean']:.4f} "
              f"spread={m['pooled_spread']:.4g} seeds={m['n_seeds']}", flush=True)


if __name__ == "__main__":
    main()
