#!/usr/bin/env python3
"""Run the preregistered Kaandorp & Dwight (2020) TBRF variant.

Everything this script does is fixed by PREREGISTRATION.md, which was written
before it was run. It fits nothing on test data, tunes no hyperparameter, and
writes its results verbatim whatever they are.

Outputs (all OUTSIDE the repo):
    /home/ubuntu/closure-data/kaandorp_tbrf/results.json
    /home/ubuntu/closure-data/kaandorp_tbrf/ckpt/<model>_seed<k>.npz   (forest)
    /home/ubuntu/closure-data/kaandorp_tbrf/train.log
"""
from __future__ import annotations
import os, sys, json, time, pickle
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
import numpy as np
from joblib import Parallel, delayed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/home/ubuntu/Certonomous/cases/RANS_LES_closure_models/_common")
from tbrf_faithful import (TBDT, fit_tree, forest_predict, normal_blocks, basis_scale,
                  solve_g, b_from_g, MAX_DEPTH, BF_MAX, Q_CAND, IDX6)
from of_read import realisability_violation, barycentric

DD = "/home/ubuntu/closure-data/kaandorp_tbrf"
TAG = "_nodurbin" if os.environ.get("NO_DURBIN") else ""
FEATS = f"features{TAG}.npz"
RESJ = f"results{TAG}.json"
CK = os.path.join(DD, "ckpt" + TAG)
os.makedirs(CK, exist_ok=True)
N_SAMPLE = 21000
N_TREES = 100
SEEDS = [0, 1, 2, 3, 4]
GAMMA_PAPER = 1e-12
VAR_CUT = 1e-4
NJOBS = 16

# SST b_rms from BASELINES.md, quoted for the record (recomputed independently here)
SST_BRMS = {"AR_1_Ret_360": 0.5843, "AR_1_Ret_180": 0.6541, "CBFS13700": 0.3051,
            "alpha_15_13929_4048": 0.2885, "alpha_15_13929_2024": 0.2989,
            "alpha_05_4071_4048": 0.3498, "alpha_05_4071_2024": 0.3202}
TRUTH_UNREAL = {"AR_1_Ret_360": 0.0159, "AR_1_Ret_180": 0.0000, "CBFS13700": 0.0000,
                "alpha_15_13929_4048": 0.0128, "alpha_15_13929_2024": 0.0230,
                "alpha_05_4071_4048": 0.0141, "alpha_05_4071_2024": 0.0246}


def log(*a):
    print(*a, flush=True)


def b_rms_F(pred, truth):
    d = pred - truth
    return float(np.sqrt((d ** 2).sum(axis=(1, 2)).mean()))


def finite_rows(*arrs):
    m = np.ones(arrs[0].shape[0], bool)
    for a in arrs:
        m &= np.isfinite(a).all(axis=tuple(range(1, a.ndim)))
    return m


def realis(b):
    m = finite_rows(b)
    viol, mn = realisability_violation(b[m])
    return float(viol.mean()), float(mn.min()), int((~m).sum())


def basis_ceiling(T, b):
    """Minimum achievable ||b - sum g_m T_m||_F per cell: the projection of the
    truth onto the span of the 10 basis tensors. No model of any kind that is
    linear in this basis can do better than this, cell by cell."""
    F = T.reshape(T.shape[0], 10, 9).transpose(0, 2, 1).astype(np.float64)   # (n,9,10)
    y = b.reshape(b.shape[0], 9).astype(np.float64)
    G = np.einsum("nam,nap->nmp", F, F)
    r = np.einsum("nam,na->nm", F, y)
    g = solve_g(G, r, 1e-10)
    res = y - np.einsum("nam,nm->na", F, g)
    step = max(1, G.shape[0] // 500)
    rk = [np.linalg.matrix_rank(F[i], tol=1e-8 * max(abs(F[i]).max(), 1e-30))
          for i in range(0, F.shape[0], step)]
    return float(np.sqrt((res ** 2).sum(axis=1).mean())), float(np.mean(rk))


def main():
    t_wall0 = time.time()
    d = np.load(os.path.join(DD, FEATS), allow_pickle=False)
    X, T, bL, bR = d["X"], d["T"], d["b_LES"], d["b_RANS"]
    valid, cid = d["valid"], d["case_id"]
    names = [str(s) for s in d["names"]]
    splits = [str(s) for s in d["splits"]]
    fnames = [str(s) for s in d["feature_names"]]

    tr_ids = [i for i, s in enumerate(splits) if s == "train"]
    te_ids = [i for i, s in enumerate(splits) if s == "TEST"]
    ct_ids = [i for i, s in enumerate(splits) if s == "control"]

    # ---------------------------------------------- disjointness assertions (3.2)
    assert set(tr_ids) & set(te_ids) == set()
    assert set(tr_ids) & set(ct_ids) == set()
    import re

    def grp(c):
        m = re.match(r"(alpha_\d+)_(\d+)_(\d+)$", c)
        return (m.group(1), m.group(2)) if m else (c, "")
    gtr = {grp(names[i]) for i in tr_ids}
    gev = {grp(names[i]) for i in te_ids + ct_ids}
    assert not (gtr & gev), f"group leak {gtr & gev}"
    train_mask = np.isin(cid, tr_ids) & valid
    log(f"[assert] case-disjoint OK; group-disjoint OK; "
        f"train cells {int(train_mask.sum())} over {len(tr_ids)} cases")

    train_pool = np.nonzero(train_mask)[0]
    eval_sets = {}
    for i in te_ids + ct_ids:
        m = np.nonzero((cid == i) & valid)[0]
        eval_sets[names[i]] = m
        assert np.intersect1d(m, train_pool).size == 0, f"cell leak {names[i]}"
    log("[assert] no cell index shared between the training pool and any eval case")

    results = {"meta": dict(n_sample=N_SAMPLE, n_trees=N_TREES, seeds=SEEDS,
                            gamma_paper=GAMMA_PAPER, var_cut=VAR_CUT,
                            max_depth=MAX_DEPTH, bf_max=BF_MAX, q_cand=Q_CAND,
                            train_cases=[names[i] for i in tr_ids],
                            test_cases=[names[i] for i in te_ids],
                            control_cases=[names[i] for i in ct_ids]),
               "runs": {}, "baselines": {}, "diagnostics": {}}

    # ------------------------------------------------------------- baselines B0/B2
    rng0 = np.random.default_rng(12345)
    ref = rng0.choice(train_pool, N_SAMPLE, replace=False)
    b_mean_train = bL[ref].astype(np.float64).mean(axis=0)
    log(f"[B1] mean training b = {np.array2string(b_mean_train, precision=4)}")
    for cname, m in eval_sets.items():
        bt = bL[m].astype(np.float64)
        z = np.zeros_like(bt)
        bs = bR[m].astype(np.float64)
        fm = finite_rows(bs)
        r_sst = b_rms_F(bs[fm], bt[fm])
        ceil, rk = basis_ceiling(T[m], bt)
        results["baselines"][cname] = dict(
            n_cells=int(m.size),
            B0_sst=r_sst, B0_sst_baselines_md=SST_BRMS.get(cname),
            B1_meanb=b_rms_F(np.broadcast_to(b_mean_train, bt.shape), bt),
            B2_zero=b_rms_F(z, bt),
            truth_norm=float(np.sqrt((bt ** 2).sum(axis=(1, 2)).mean())),
            tensor_basis_ceiling=ceil, basis_rank_mean=rk,
            n_sst_nonfinite=int((~fm).sum()),
            truth_unrealisable_frac=realis(bt)[0],
            sst_unrealisable_frac=realis(bs)[0])
        log(f"[base] {cname:22s} n={m.size:6d} SST={r_sst:.4f} "
            f"(BASELINES.md {SST_BRMS.get(cname)}) B1={results['baselines'][cname]['B1_meanb']:.4f} "
            f"B2={results['baselines'][cname]['B2_zero']:.4f} "
            f"basis-ceiling={ceil:.4f} rank={rk:.2f}")

    # --------------------------------------------------------------- feature sets
    Xs0 = X[ref]
    var = Xs0.var(axis=0)
    keep_all = np.nonzero(var >= VAR_CUT)[0]
    keep_fs1 = np.array([i for i in keep_all if i < 6])
    keep_fs12 = np.array([i for i in keep_all if i < 16])
    results["diagnostics"]["feature_variance"] = {fnames[i]: float(var[i])
                                                  for i in range(len(fnames))}
    results["diagnostics"]["survivors"] = dict(
        FS1=[fnames[i] for i in keep_fs1],
        FS12=[fnames[i] for i in keep_fs12],
        ALL=[fnames[i] for i in keep_all])
    log(f"[feat] survivors FS1={len(keep_fs1)} FS1+FS2={len(keep_fs12)} ALL={len(keep_all)}")

    MODELS = [
        ("FS%d_full" % len(keep_all), keep_all, 11, 9, GAMMA_PAPER, SEEDS),
        ("FS%d_SRonly" % len(keep_fs1), keep_fs1, len(keep_fs1), 9, GAMMA_PAPER, SEEDS),
        ("FS%d_SRonly_papergrown" % len(keep_fs1), keep_fs1, len(keep_fs1), 1,
         GAMMA_PAPER, SEEDS),
        ("FS%d_SR_gradk" % len(keep_fs12), keep_fs12, min(11, len(keep_fs12)), 9,
         GAMMA_PAPER, SEEDS),
        ("FS%d_full_gamma1e-6" % len(keep_all), keep_all, 11, 9, 1e-6, SEEDS[:3]),
        ("FS%d_full_gamma1e-3" % len(keep_all), keep_all, 11, 9, 1e-3, SEEDS[:3]),
    ]

    # ---------------------------------------------------- extrapolation statistic
    med = np.median(Xs0[:, keep_all], axis=0)
    iqr = np.subtract(*np.percentile(Xs0[:, keep_all], [75, 25], axis=0))
    iqr = np.where(iqr > 0, iqr, 1.0)
    Z = (Xs0[:, keep_all] - med) / iqr
    Cov = np.cov(Z.T) + 1e-6 * np.eye(Z.shape[1])
    Ci = np.linalg.inv(Cov)
    dm = lambda A: np.sqrt(np.maximum(np.einsum("na,ab,nb->n", A, Ci, A), 0.0))
    md_tr = dm(Z)
    lo = Xs0[:, keep_all].min(axis=0); hi = Xs0[:, keep_all].max(axis=0)
    ext = {"train_sample": dict(median=float(np.median(md_tr)),
                                p95=float(np.percentile(md_tr, 95)), out_of_box=0.0)}
    for cname, m in eval_sets.items():
        Ze = (X[m][:, keep_all] - med) / iqr
        v = dm(Ze)
        oob = float(np.mean(((X[m][:, keep_all] < lo) | (X[m][:, keep_all] > hi)).any(axis=1)))
        ext[cname] = dict(median=float(np.median(v)), p95=float(np.percentile(v, 95)),
                          max=float(v.max()), out_of_box=oob)
        log(f"[extrap] {cname:22s} Mahalanobis med={ext[cname]['median']:.2f} "
            f"p95={ext[cname]['p95']:.2f} outside-train-box={oob:.3f}")
    results["diagnostics"]["extrapolation"] = ext

    # ------------------------------------------------------------------ training
    core_s = 0.0
    for mname, cols, mfeat, mleaf, gamma, seeds in MODELS:
        results["runs"][mname] = dict(features=[fnames[i] for i in cols],
                                      max_features=int(mfeat),
                                      min_samples_leaf=int(mleaf), gamma=gamma,
                                      seeds={})
        for seed in seeds:
            t0 = time.time()
            rng = np.random.default_rng(1000 + seed)
            samp = rng.choice(train_pool, N_SAMPLE, replace=False)
            assert np.intersect1d(samp, np.concatenate(list(eval_sets.values()))).size == 0
            Ts = T[samp]
            scale = basis_scale(Ts)
            A, c = normal_blocks(Ts.astype(np.float64), bL[samp].astype(np.float64), scale)
            Xk = X[samp][:, cols]
            trees = Parallel(n_jobs=NJOBS, backend="loky")(
                delayed(fit_tree)((seed * 10000 + t, Xk, A, c, mfeat, mleaf, gamma))
                for t in range(N_TREES))
            fit_s = time.time() - t0
            leaves = int(np.mean([t.n_leaf for t in trees]))
            dhit = int(np.sum([t.depth_hits for t in trees]))
            per = {}
            for cname, m in eval_sets.items():
                bp = forest_predict(trees, X[m][:, cols], T[m], scale)
                bt = bL[m].astype(np.float64)
                vf, mn, nnf = realis(bp)
                per[cname] = dict(b_rms_F=b_rms_F(bp, bt),
                                  b_rmse_comp=b_rms_F(bp, bt) / 3.0,
                                  unrealisable_frac=vf, min_barycentric=mn,
                                  n_nonfinite=nnf,
                                  mean_abs_trace=float(np.abs(
                                      np.einsum("nii->n", bp)).mean()))
            bp_in = forest_predict(trees, Xk, Ts, scale)
            insample = b_rms_F(bp_in, bL[samp].astype(np.float64))
            wall = time.time() - t0
            core_s += fit_s * NJOBS + (wall - fit_s)
            results["runs"][mname]["seeds"][str(seed)] = dict(
                per_case=per, in_sample_b_rms_F=insample, fit_seconds=fit_s,
                wall_seconds=wall, mean_leaves=leaves, depth_cap_hits=dhit)
            with open(os.path.join(CK, f"{mname}_seed{seed}.pkl"), "wb") as fh:
                pickle.dump(dict(trees=trees, scale=scale, cols=cols,
                                 feature_names=[fnames[i] for i in cols]), fh)
            log(f"[fit] {mname:26s} seed={seed} {wall:6.1f}s leaves={leaves:5d} "
                f"depthhits={dhit} in-sample={insample:.4f} " +
                " ".join(f"{k.split('_')[0]}:{v['b_rms_F']:.4f}" for k, v in per.items()))
            json.dump(results, open(os.path.join(DD, RESJ), "w"), indent=1)

    results["meta"]["core_hours"] = core_s / 3600.0
    results["meta"]["wall_hours"] = (time.time() - t_wall0) / 3600.0
    json.dump(results, open(os.path.join(DD, RESJ), "w"), indent=1)
    log(f"[done] core-hours={core_s/3600:.2f} wall-hours={(time.time()-t_wall0)/3600:.2f}")


if __name__ == "__main__":
    main()
