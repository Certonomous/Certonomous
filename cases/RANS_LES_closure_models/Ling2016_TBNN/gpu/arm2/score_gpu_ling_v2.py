#!/usr/bin/env python3
"""Lab-box CPU comparator, ARM 2 — Ling (2016) TBNN, matched-update-count arm.

Loads the CLEAN dataset (/home/ubuntu/closure-data/tbnn/dataset.npz) and the
predictions synced back from gpu1, and writes ONE grading JSON of numbers.
It grades NO verdict — the supervisor grades against the frozen thresholds.

Inherited VERBATIM from v1 score_gpu_ling.py (frozen 11f93da6): the split, the
realisability reader choice, frob_rms, the G0a/G0b controls (refusal -> exit 2,
no JSON), score_pred, collect_model's row-index verification, the scoring mask
(valid AND finite b_LES AND finite b_RANS; identical cells for every model and
baseline), the three baselines.

Added for arm 2:
  (a) the JSON records the sha256 of THIS comparator's own file bytes, of the
      dataset, and of every prediction file it read (closes RESULTS D-5);
  (b) realisability PER CASE PER SEED for every model and baseline: violation
      fraction, that case's OWN truth violation fraction, and max ||b||_F;
  (c) in-family pooled b_rms (the 7 TEST cases excluding NASA_2DWMH) beside the
      8-case pooled figure, for every model and baseline;
  (d) --pred-dir may point at the ARM-1 out directory (pred_tbnn/pred_mlp/
      pred_armb, 5 seeds) so both arms are scored by the same code;
  (e) reference numbers from the CPU lane and from arm 1 are recorded ONLY if
      read from files on disk (path + sha256 recorded); nothing is typed in.

Usage:
  /home/ubuntu/closure-venv/bin/python score_gpu_ling_v2.py                 # score arm 2
  /home/ubuntu/closure-venv/bin/python score_gpu_ling_v2.py --g0-only       # controls only
  /home/ubuntu/closure-venv/bin/python score_gpu_ling_v2.py \
      --pred-dir /home/ubuntu/closure-data/tbnn_gpu/out --out <json>        # score arm 1
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "/home/ubuntu/closure-data/tbnn/dataset.npz"
PRED_DIR = "/home/ubuntu/closure-data/tbnn_gpu/arm2/out"
OUT_JSON = "/home/ubuntu/closure-data/tbnn_gpu/arm2/grading_gpu_ling_v2.json"
PLANT = 1.234e-03                      # the lab's standing planted constant
OUT_OF_FAMILY = "NASA_2DWMH"           # the one TEST case outside the hill/duct families

# reference files, read only if present (e); never typed
CPU_LANE_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))            # Ling2016_TBNN/
COMMON_DIR = os.path.abspath(os.path.join(HERE, "..", "..", "..", "_common"))
REFERENCE_FILES = {
    "cpu_lane_train_log": os.path.join(CPU_LANE_DIR, "train_log.json"),
    "cpu_lane_trainmean_baseline": os.path.join(COMMON_DIR, "trainmean_baseline.json"),
    "cpu_lane_sst_baseline_metrics": os.path.join(COMMON_DIR, "sst_baseline_metrics.json"),
    "arm1_grading_json": "/home/ubuntu/closure-data/tbnn_gpu/grading_gpu_ling.json",
}

# ---- frozen split, verbatim from ../train_tbnn.py (CPU lane) ---------------
TEST = {"alpha_15_13929_4048", "alpha_15_13929_2024",
        "alpha_05_4071_4048", "alpha_05_4071_2024",
        "AR_1_Ret_360", "AR_3_Ret_360", "AR_14_Ret_180", "NASA_2DWMH"}
VAL = {"alpha_05_10071_4048", "alpha_05_10071_2024",
       "alpha_15_7929_4048", "alpha_15_7929_2024", "AR_7_Ret_180"}
GROUP_EXCLUDED = {"alpha_15_13929_3036", "alpha_05_4071_3036",
                  "alpha_05_10071_3036", "alpha_15_7929_3036"}

# ---- realisability: prefer the CPU lane's own code --------------------------
sys.path.insert(0, COMMON_DIR)
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


def sha256_file(path, chunk=1 << 24):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def frob_rms(x):
    """The b_rms scorer: RMS of the Frobenius norm, float64 accumulation."""
    x = np.asarray(x, dtype=np.float64)
    return float(np.sqrt((x ** 2).sum(axis=(1, 2)).mean()))


# --------------------------------------------------------------- G0 controls
def g0_controls(names, cid, valid, bL):
    """G0a + G0b on a COPY of the clean data. Refusal -> exit 2, no JSON.
    Verbatim from v1."""
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


# --------------------------------------------------------------- scoring (v1, verbatim)
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


# --------------------------------------------------------------- scoring (arm-2 additions)
def score_extras(pred_test, bL_test, cid_test, names, test_cases, truth_viol_case):
    """(b) per-case realisability beside the truth's own; (c) in-family pooled."""
    p64 = pred_test.astype(np.float64)
    per_case_real = {}
    for c in test_cases:
        m = cid_test == names.index(c)
        viol, _ = realisability_violation(p64[m])
        per_case_real[c] = dict(viol_frac=float(viol.mean()),
                                truth_viol_frac=truth_viol_case[c],
                                max_frob=float(np.sqrt((p64[m] ** 2).sum(axis=(1, 2)).max())),
                                n=int(m.sum()))
    fam = cid_test != names.index(OUT_OF_FAMILY)
    viol_fam, _ = realisability_violation(p64[fam])
    return dict(per_case_realisability=per_case_real,
                pooled_in_family=frob_rms(p64[fam] - bL_test[fam]),
                viol_frac_in_family=float(viol_fam.mean()),
                max_frob_in_family=float(np.sqrt((p64[fam] ** 2).sum(axis=(1, 2)).max())),
                n_in_family=int(fam.sum()))


def score_full(pred_test, bL_test, cid_test, names, test_cases, truth_viol_case):
    r = score_pred(pred_test, bL_test, cid_test, names, test_cases)
    r.update(score_extras(pred_test, bL_test, cid_test, names, test_cases, truth_viol_case))
    return r


def collect_model(tag, nseeds, test_idx, fsub, bL_test, cid_test, names,
                  test_cases, truth_viol_case, file_shas, which="pred_best"):
    """Load pred_{tag}_s{seed}.npz files; verify their idx matches the TEST
    rows of the clean dataset (v1's refusal, verbatim); score each seed;
    record each file's sha256 (a)."""
    seeds = {}
    for s in range(nseeds):
        p = os.path.join(PRED_DIR, f"pred_{tag}_s{s}.npz")
        if not os.path.exists(p):
            continue
        if p not in file_shas:
            file_shas[p] = sha256_file(p)
        z = np.load(p)
        if not np.array_equal(z["idx"], test_idx):
            print(f"[refuse] {p}: prediction row indices do not match the "
                  "clean dataset's TEST rows. Exit 2.", flush=True)
            sys.exit(2)
        seeds[str(s)] = score_full(z[which].astype(np.float64)[fsub],
                                   bL_test, cid_test, names, test_cases, truth_viol_case)
        seeds[str(s)]["file"] = os.path.basename(p)
        seeds[str(s)]["file_sha256"] = file_shas[p]
    if not seeds:
        return None
    agg = {}
    for c in test_cases:
        v = [seeds[s]["per_case"][c] for s in seeds]
        agg[c] = dict(mean=float(np.mean(v)), lo=float(min(v)),
                      hi=float(max(v)), n=len(v))
    pooled = {s: seeds[s]["pooled"] for s in seeds}
    fam = {s: seeds[s]["pooled_in_family"] for s in seeds}
    return dict(n_seeds=len(seeds), which=which, per_seed=seeds,
                per_case_over_seeds=agg,
                pooled_per_seed=pooled,
                pooled_mean=float(np.mean(list(pooled.values()))),
                pooled_spread=float(max(pooled.values()) - min(pooled.values())),
                pooled_in_family_per_seed=fam,
                pooled_in_family_mean=float(np.mean(list(fam.values()))),
                pooled_in_family_spread=float(max(fam.values()) - min(fam.values())))


# --------------------------------------------------------------- references (e)
def read_references():
    """Numbers from files only. Each entry carries the path and sha256 it was
    read from, or `present: false`. Nothing here is typed in."""
    refs = {}
    for key, path in REFERENCE_FILES.items():
        if not os.path.exists(path):
            refs[key] = dict(path=path, present=False)
            continue
        with open(path) as f:
            j = json.load(f)
        rec = dict(path=path, present=True, sha256=sha256_file(path))
        if key == "cpu_lane_train_log":
            # the CPU lane's Adam-trained TBNN / MLP per-case test b_rms per seed
            rec["results"] = j.get("results")
        elif key == "cpu_lane_trainmean_baseline":
            rec["b_mean"] = j.get("b_mean")
            rec["n_train_cells"] = j.get("n_train_cells")
            rec["n_train_cells_LES_mask_only"] = j.get("n_train_cells_LES_mask_only")
        elif key == "cpu_lane_sst_baseline_metrics":
            rec["b_rms_err_per_test_case"] = {c: j[c].get("b_rms_err") for c in sorted(TEST) if c in j}
        elif key == "arm1_grading_json":
            rec["baselines"] = {k: dict(pooled=v["pooled"], per_case=v["per_case"])
                                for k, v in j.get("baselines", {}).items()}
            rec["models"] = {k: dict(pooled_mean=v["pooled_mean"], pooled_spread=v["pooled_spread"],
                                     n_seeds=v["n_seeds"], per_case_over_seeds=v["per_case_over_seeds"])
                             for k, v in j.get("models", {}).items()}
            rec["truth_viol_frac_test"] = j.get("truth_viol_frac_test")
        refs[key] = rec
    return refs


def main():
    global PRED_DIR
    ap = argparse.ArgumentParser()
    ap.add_argument("--g0-only", action="store_true",
                    help="run the planted controls only (pre-freeze proof)")
    ap.add_argument("--pred-dir", default=PRED_DIR,
                    help="arm-2 out dir (default) or the arm-1 out dir (d)")
    ap.add_argument("--out", default=OUT_JSON)
    ap.add_argument("--nseeds", type=int, default=5,
                    help="seed files scanned: pred_<tag>_s0..s{nseeds-1}; missing ones are skipped")
    args = ap.parse_args()
    PRED_DIR = args.pred_dir

    self_sha = sha256_file(os.path.abspath(__file__))          # (a) own bytes
    data_sha = sha256_file(DATA)
    print(f"[witness] comparator sha256 {self_sha}\n[witness] dataset sha256 {data_sha}", flush=True)

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

    # truth's own realisability, pooled and per case (the G3 ratio's denominator)
    tviol, _ = realisability_violation(bL_test)
    truth_viol_case = {}
    for c in test_cases:
        m = cid_test == names.index(c)
        v, _ = realisability_violation(bL_test[m])
        truth_viol_case[c] = float(v.mean())
    fam = cid_test != names.index(OUT_OF_FAMILY)

    file_shas = {}
    out = dict(written=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               comparator=os.path.abspath(__file__), comparator_sha256=self_sha,
               dataset=DATA, dataset_sha256=data_sha, pred_dir=PRED_DIR,
               plant_control=g0, realisability_source=REALISABILITY_SOURCE,
               n_test_predicted=int(tmask.sum()), n_test_scored=int(fsub.sum()),
               n_test_dropped_nonfinite_bRANS=int((~fsub).sum()),
               n_train=int(trmask.sum()),
               in_family_cases=[c for c in test_cases if c != OUT_OF_FAMILY],
               out_of_family_case=OUT_OF_FAMILY, n_in_family_scored=int(fam.sum()),
               truth_viol_frac_test=float(tviol.mean()),
               truth_viol_frac_in_family=float(tviol[fam].mean()),
               truth_viol_frac_per_case=truth_viol_case,
               grades_verdict=False,
               note="numbers only; the supervisor grades against the frozen thresholds",
               models={}, baselines={}, prediction_files={}, references={})

    # ---- baselines: SST (b_RANS), b = 0, train-mean tensor -----------------
    sst = bR[tmask][fsub].astype(np.float64)       # finite by construction
    out["baselines"]["SST"] = score_full(sst, bL_test, cid_test, names, test_cases, truth_viol_case)
    out["baselines"]["zero"] = score_full(np.zeros_like(bL_test), bL_test, cid_test,
                                          names, test_cases, truth_viol_case)
    bmean = bL[trmask].astype(np.float64).mean(axis=0)
    out["baselines"]["train_mean"] = score_full(
        np.broadcast_to(bmean, bL_test.shape).copy(),
        bL_test, cid_test, names, test_cases, truth_viol_case)
    out["baselines"]["train_mean"]["tensor"] = bmean.tolist()

    # ---- models: arm-2 tags (3 seeds) and arm-1 tags (5 seeds) share names --
    for tag, label in (("tbnn", "TBNN"), ("mlp", "MLP"), ("armb", "ARM-B best")):
        for which in ("pred_best", "pred_final"):
            m = collect_model(tag, args.nseeds, test_idx, fsub, bL_test, cid_test,
                              names, test_cases, truth_viol_case, file_shas, which=which)
            if m is not None:
                out["models"][f"{label} [{which}]"] = m
    out["prediction_files"] = {os.path.basename(p): s for p, s in sorted(file_shas.items())}

    # ---- references, from files only (e) -----------------------------------
    out["references"] = read_references()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(out, f, indent=1)
    print(f"\n[score] wrote {args.out}", flush=True)
    for name, m in out["baselines"].items():
        print(f"  baseline {name:11s} pooled={m['pooled']:.4f} in-family={m['pooled_in_family']:.4f} "
              f"viol={m['viol_frac']*100:.2f}% max||b||={m['max_frob']:.3f}", flush=True)
    for name, m in out["models"].items():
        print(f"  {name:22s} pooled_mean={m['pooled_mean']:.4g} spread={m['pooled_spread']:.4g} "
              f"in-family_mean={m['pooled_in_family_mean']:.4g} seeds={m['n_seeds']}", flush=True)


if __name__ == "__main__":
    main()
