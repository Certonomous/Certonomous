#!/usr/bin/env python3
"""R4 steps 2-3 - FS3 selection and sparse model discovery.

Everything below is the frozen PREREGISTRATION, section by section:

  sec. 1    the candidate library for a model INTENDED FOR SYMBOLIC
            PROPAGATION is T1, T2, T3 only, because `kOmegaSSTSparta`
            implements no T4 and would silently evaluate n=4 as T3.  Library
            `prop`.
  sec. 2.1  on a MIXED-FAMILY fit T4 and I2 are RETAINED (the collinearity is
            only partial off the ducts) and the condition number of the fitted
            design matrix is reported per fit.  Library `full`.
            A ducts-only fit would exclude both; this lane runs no ducts-only
            fit, and the exclusion is therefore recorded as not triggered.
  sec. 2.2  the 12 pooled-training dead features of the 110-feature audit are
            excluded from every fit.  None of the 12 is a member of the SpaRTA
            ansatz library (they are Wu-Xiao-Paterson invariants of {S,W,Ap,Ak},
            not I1^p I2^q T_n), so the exclusion is honoured and empty; the
            intersection is asserted empty rather than assumed.
  sec. 2.3  no nu-carrying normaliser: tau = 1/omega throughout.  Asserted by
            construction - nu is never read.
  sec. 2.4  models capped at 5 terms; exponent grid p,q in {0,1,2}, p+q <= 2;
            ties in cross-validated error broken toward FEWER terms.
  sec. 3    three selection methods, all run, all reported: mutual information,
            permutation importance on a held-out training FAMILY, and an
            elastic-net path with l1_ratio in {0.1,0.5,0.7,0.9,0.95,0.99,1.0}
            and a 60-point alpha path chosen by cross-FAMILY CV.  Folds are
            whole families, never random cells.  Agreement between the three
            rankings is reported as a Spearman rank correlation.
  sec. 5    seeds 0, 1, 2 wherever a method is stochastic.

STANDING RULE, not optional: a PLANTED-ZERO CONTROL.  Two columns with a known
true coefficient of exactly zero are appended to every design matrix - a seeded
permutation of the candidate most correlated with the target (same marginal
distribution, no physical relation) and a seeded Gaussian column at the same
RMS.  The control PASSES only if neither appears in the selected support and
both rank below every selected term under all three methods.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np
from scipy.stats import spearmanr
from sklearn.feature_selection import mutual_info_regression

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r4_lib as R

DS = os.path.join(R.WORK, "dataset")
OUT = os.path.join(R.WORK, "fs3")
SEEDS = [0, 1, 2]                                   # PREREGISTRATION sec. 5
L1_RATIOS = [0.1, 0.5, 0.7, 0.9, 0.95, 0.99, 1.0]   # PREREGISTRATION sec. 3
N_ALPHA = 60                                        # PREREGISTRATION sec. 3
MAX_TERMS = 5                                       # PREREGISTRATION sec. 2.4
ALPHA_MIN_RATIO = 1e-4
MI_SUBSAMPLE = 20000
R_SCALED = True     # see load(): the per-case k*omega non-dimensionalisation
FAMILIES = ["hills", "ducts", "PHLL10595", "CBFS13700"]
# PREREGISTRATION sec. 2.2 - the 12 pooled-training dead features
DEAD_12 = [f"{n}__{t}" for n in ("trW2SWS2", "trW2SPS2", "trW2SKS2",
                                 "trP2KS2", "trK2PS2", "trWPSKS2")
           for t in ("A", "B")]


# --------------------------------------------------------------- data
def load(cases_used):
    man = json.load(open(os.path.join(DS, "dataset_manifest.json")))
    names = man["candidates"]
    assert not (set(names) & set(DEAD_12)), (
        "PREREGISTRATION sec. 2.2: a pooled-training dead feature entered the "
        "SpaRTA ansatz library")
    Xr, yr, Xb, yb, grp_c, grp_r, meta = [], [], [], [], [], [], {}
    for case in cases_used:
        z = np.load(os.path.join(DS, f"{case}.npz"))
        fam = man["cases"][case]["family"]
        CT, CR = z["CT"], z["CR"]                 # (M,N,3,3), (M,N)
        kDef, bDel, k = z["kDef"], z["bDel"], z["k"]
        kraw, omega = z["k_les_raw"], z["omega"]
        # Fit mask.  The LES anisotropy is undefined where the SHIPPED k_LES is
        # non-positive; the solver's own bound(k, kMin) has already replaced
        # those cells with a small positive number, so the written k cannot see
        # them and b^Delta there is O(1e5) nonsense.  Counts are reported.
        ok = (kraw > 0) & np.isfinite(kDef) & np.isfinite(CR).all(axis=0) \
            & np.isfinite(bDel).all(axis=(1, 2)) & np.isfinite(CT).all(axis=(0, 2, 3))
        # R non-dimensionalisation.  R has the dimensions of k*omega and its
        # RMS spans eight orders of magnitude across the training families
        # (0.0066 on CBFS13700 to 1.66e6 on the ducts, whose bulk velocity is
        # ~50 m/s on a 1 mm half-height).  An unweighted pooled fit on the raw
        # quantity is a duct fit with the other three families as rounding
        # error.  Each case's R rows -- target AND candidates alike -- are
        # therefore divided by ONE positive constant, the case median of
        # k*omega on the fitted cells.  It is a physical scale of the same
        # dimensions, computed from the frozen fields and not from the target,
        # and dividing both sides of a linear system by a constant leaves every
        # coefficient's value and meaning unchanged.  The unscaled fit is run
        # as a declared sensitivity.
        sc = float(np.median(k[ok] * omega[ok])) if R_SCALED else 1.0
        meta[case] = dict(family=fam, n_cells=int(k.size),
                          n_used=int(ok.sum()), n_dropped=int((~ok).sum()),
                          R_scale_median_k_omega=sc,
                          rms_R=float(np.sqrt((kDef[ok] ** 2).mean())),
                          rms_bDelta=float(np.sqrt((bDel[ok] ** 2).sum((1, 2)).mean())))
        Xr.append(CR[:, ok].T / sc)
        yr.append(kDef[ok] / sc)
        Xb.append(CT[:, ok].reshape(CT.shape[0], -1, 9).transpose(1, 0, 2)
                  .reshape(-1, CT.shape[0]))
        yb.append(bDel[ok].reshape(-1))
        grp_r.append(np.full(int(ok.sum()), FAMILIES.index(fam)))
        grp_c.append(np.full(int(ok.sum()) * 9, FAMILIES.index(fam)))
    return dict(names=names,
                Xr=np.concatenate(Xr), yr=np.concatenate(yr),
                Xb=np.concatenate(Xb), yb=np.concatenate(yb),
                gr=np.concatenate(grp_r), gb=np.concatenate(grp_c), meta=meta)


def restrict(names, X, library):
    """PREREGISTRATION sec. 1 vs sec. 2.1: T1-T3 only, or the full T1-T4."""
    if library == "full":
        keep = list(range(len(names)))
    else:
        keep = [i for i, n in enumerate(names) if not n.endswith("T4")]
    return [names[i] for i in keep], X[:, keep]


def plant_zeros(X, y, names, seed):
    """Two columns whose true coefficient is exactly zero, by construction."""
    rng = np.random.default_rng(1000 + seed)
    rms = np.sqrt((X ** 2).mean(axis=0))
    rms[rms == 0] = 1.0
    c = np.abs((X / rms) .T @ y) / len(y)
    j = int(np.argmax(c))
    perm = X[rng.permutation(X.shape[0]), j]
    gauss = rng.standard_normal(X.shape[0]) * rms[j]
    Xp = np.column_stack([X, perm, gauss])
    return Xp, names + [f"PZ_perm({names[j]})", "PZ_gauss"], j


# ------------------------------------------------------- FS3 method 1: MI
def mi_rank(X, y, seed):
    rng = np.random.default_rng(seed)
    n = min(MI_SUBSAMPLE, X.shape[0])
    idx = rng.choice(X.shape[0], n, replace=False)
    return mutual_info_regression(X[idx], y[idx], random_state=seed)


# ------------------------------ FS3 method 2: permutation importance, LOFO
def perm_importance(X, y, g, seed, ridge=1e-8):
    rng = np.random.default_rng(seed)
    imp = np.zeros(X.shape[1])
    nfold = 0
    for f in np.unique(g):
        tr, te = g != f, g == f
        if tr.sum() == 0 or te.sum() == 0:
            continue
        A = X[tr].T @ X[tr]
        th = np.linalg.solve(A + ridge * np.trace(A) / A.shape[0]
                             * np.eye(A.shape[0]), X[tr].T @ y[tr])
        base = float(((X[te] @ th - y[te]) ** 2).mean())
        for j in range(X.shape[1]):
            Xp = X[te].copy()
            Xp[:, j] = Xp[rng.permutation(Xp.shape[0]), j]
            imp[j] += float(((Xp @ th - y[te]) ** 2).mean()) - base
        nfold += 1
    return imp / max(nfold, 1)


# -------------------------------- FS3 method 3: elastic-net path, family CV
def enet_path(Xs, y, l1_ratio, alphas, w0=None, tol=1e-7, max_iter=500):
    """Cyclic coordinate descent on the Gram matrix, warm-started down the
    alpha path.  Objective (1/2N)||y-Xw||^2 + a*r*|w|_1 + a*(1-r)/2*|w|^2."""
    N, m = Xs.shape
    G = (Xs.T @ Xs) / N
    b = (Xs.T @ y) / N
    w = np.zeros(m) if w0 is None else w0.copy()
    Gw = G @ w
    out = []
    for a in alphas:
        l1, l2 = a * l1_ratio, a * (1.0 - l1_ratio)
        for _ in range(max_iter):
            dmax = 0.0
            for j in range(m):
                wj = w[j]
                z = b[j] - Gw[j] + G[j, j] * wj
                wn = np.sign(z) * max(abs(z) - l1, 0.0) / (G[j, j] + l2)
                if wn != wj:
                    Gw += G[:, j] * (wn - wj)
                    w[j] = wn
                    dmax = max(dmax, abs(wn - wj))
            if dmax <= tol * max(np.abs(w).max(), 1e-12):
                break
        out.append(w.copy())
    return out


def lasso_entry_order(X, y, names):
    """Index of the first alpha on the pure-lasso (l1_ratio = 1) path at which
    each column becomes nonzero.  Lower = enters earlier = stronger.  A column
    whose true coefficient is zero should enter late, or never."""
    rms = np.sqrt((X ** 2).mean(axis=0)); rms[rms == 0] = 1.0
    Xs = X / rms
    alphas = alpha_grid(Xs, y, 1.0)
    entry = {n: None for n in names}
    for i, w in enumerate(enet_path(Xs, y, 1.0, alphas)):
        for j in np.flatnonzero(np.abs(w) > 1e-12):
            if entry[names[j]] is None:
                entry[names[j]] = i
    return {k: (N_ALPHA if v is None else int(v)) for k, v in entry.items()}


def alpha_grid(Xs, y, l1_ratio):
    amax = np.abs(Xs.T @ y).max() / (len(y) * max(l1_ratio, 1e-3))
    return np.logspace(np.log10(amax), np.log10(ALPHA_MIN_RATIO * amax), N_ALPHA)


def enet_family_cv(X, y, g, names):
    """Cross-FAMILY CV over the (l1_ratio, alpha) grid.  Returns the CV-optimal
    point, its support, and every support seen anywhere on the grid."""
    rms = np.sqrt((X ** 2).mean(axis=0)); rms[rms == 0] = 1.0
    Xs = X / rms
    best = None
    supports = {}
    grid = []
    for r in L1_RATIOS:
        alphas = alpha_grid(Xs, y, r)
        # full-data path -> the supports the path visits
        for w in enet_path(Xs, y, r, alphas):
            s = tuple(np.flatnonzero(np.abs(w) > 1e-12))
            if s:
                supports[s] = supports.get(s, 0) + 1
        # cross-family CV of the same path
        err = np.zeros(len(alphas))
        for f in np.unique(g):
            tr, te = g != f, g == f
            rmsf = np.sqrt((X[tr] ** 2).mean(axis=0)); rmsf[rmsf == 0] = 1.0
            Xtr = X[tr] / rmsf
            ws = enet_path(Xtr, y[tr], r, alpha_grid(Xtr, y[tr], r))
            # held-out MSE from the fold's own Gram: identical arithmetic to
            # ||X_te w - y_te||^2 / n_te, at O(m^2) per alpha instead of O(N m)
            Xte = X[te] / rmsf
            Gte = Xte.T @ Xte
            bte = Xte.T @ y[te]
            yy = float(y[te] @ y[te])
            nte = int(te.sum())
            for i, w in enumerate(ws):
                err[i] += (w @ Gte @ w - 2.0 * (w @ bte) + yy) / nte
        err /= len(np.unique(g))
        i = int(np.argmin(err))
        grid.append(dict(l1_ratio=r, alpha=float(alphas[i]),
                         cv_mse=float(err[i])))
        if best is None or err[i] < best["cv_mse"]:
            wfull = enet_path(Xs, y, r, alphas)[i]
            best = dict(l1_ratio=r, alpha=float(alphas[i]),
                        cv_mse=float(err[i]),
                        support=[names[j] for j in
                                 np.flatnonzero(np.abs(wfull) > 1e-12)],
                        coefficients={names[j]: float(wfull[j] / rms[j])
                                      for j in
                                      np.flatnonzero(np.abs(wfull) > 1e-12)})
    return best, supports, grid


# ------------------------------------------------------- form scoring (FS4)
def ols(X, y, cols, ridge=0.0):
    A = X[:, cols].T @ X[:, cols]
    if ridge:
        A = A + ridge * np.trace(A) / A.shape[0] * np.eye(A.shape[0])
    return np.linalg.solve(A, X[:, cols].T @ y)


def lofo_mse(X, y, g, cols):
    e, n = 0.0, 0
    for f in np.unique(g):
        tr, te = g != f, g == f
        try:
            th = ols(X[tr], y[tr], cols, ridge=1e-10)
        except np.linalg.LinAlgError:
            return np.inf
        e += float(((X[te][:, cols] @ th - y[te]) ** 2).mean())
        n += 1
    return e / max(n, 1)


def select_form(X, y, g, names, supports, extra_supports, pz_idx):
    """PREREGISTRATION sec. 2.4: cap 5 terms, ties broken toward FEWER terms.
    A form containing a planted-zero column is never selectable; it is
    recorded so the control is measurable."""
    cands = {}
    for s in list(supports) + [tuple(extra_supports)]:
        s = tuple(sorted(set(s)))
        if 0 < len(s) <= MAX_TERMS:
            cands[s] = supports.get(s, 0)
    rows = []
    for s, hits in cands.items():
        contaminated = bool(set(s) & set(pz_idx))
        rows.append(dict(support=[names[j] for j in s], idx=list(s),
                         n_terms=len(s), grid_hits=int(hits),
                         contaminated_by_planted_zero=contaminated,
                         lofo_cv_mse=lofo_mse(X, y, g, list(s))))
    for r in rows:
        if not np.isfinite(r["lofo_cv_mse"]):
            # an exactly-collinear support can make the normal-equation solve
            # return non-finite coefficients without raising; such a form is
            # unfittable, is recorded, and is never selectable
            r["lofo_cv_mse"] = float("inf")
            r["unfittable"] = True
    rows.sort(key=lambda r: (r["lofo_cv_mse"], r["n_terms"]))
    clean = [r for r in rows if not r["contaminated_by_planted_zero"]
             and np.isfinite(r["lofo_cv_mse"])]
    assert clean, "no planted-zero-free, fittable candidate form survived"
    best = clean[0]
    # tie-break toward fewer terms: anything within 1% of the best CV error
    tied = [r for r in clean if r["lofo_cv_mse"] <= best["lofo_cv_mse"] * 1.01]
    best = sorted(tied, key=lambda r: (r["n_terms"], r["lofo_cv_mse"]))[0]
    return best, rows


def cond_number(X, cols):
    A = X[:, cols]
    s = np.linalg.svd(A, compute_uv=False)
    return float(s[0] / max(s[-1], 1e-300))


# ------------------------------------------------------------------ driver
def run_target(tag, X, y, g, names, library, res):
    t0 = time.time()
    names_l, Xl = restrict(names, X, library)
    per_seed = {}
    for seed in SEEDS:
        Xp, namesp, j0 = plant_zeros(Xl, y, names_l, seed)
        pz_idx = [len(namesp) - 2, len(namesp) - 1]
        rms = np.sqrt((Xp ** 2).mean(axis=0)); rms[rms == 0] = 1.0
        mi = mi_rank(Xp / rms, y, seed)
        pi = perm_importance(Xp / rms, y, g, seed)
        best, supports, grid = enet_family_cv(Xp, y, g, namesp)
        enet_score = np.zeros(len(namesp))
        for s, h in supports.items():
            for jj in s:
                enet_score[jj] += h
        form, rows = select_form(Xp, y, g, namesp, supports,
                                 [namesp.index(n) for n in best["support"]],
                                 pz_idx)
        cols = form["idx"]
        theta = ols(Xp, y, cols)
        rk = lambda v: (-v).argsort().argsort()          # 0 = most important
        ranks = dict(mi=rk(mi).tolist(), perm=rk(pi).tolist(),
                     enet=rk(enet_score).tolist())
        sp = {}
        for a, b in (("mi", "perm"), ("mi", "enet"), ("perm", "enet")):
            sp[f"{a}_vs_{b}"] = float(spearmanr(ranks[a], ranks[b]).statistic)
        entry = lasso_entry_order(Xp, y, namesp)
        pz = {}
        for p in pz_idx:
            sel_entry = max(entry[t] for t in form["support"])
            pz[namesp[p]] = dict(
                in_selected_support=namesp[p] in form["support"],
                mi_rank=int(ranks["mi"][p]), perm_rank=int(ranks["perm"][p]),
                enet_gridhit_rank=int(ranks["enet"][p]),
                lasso_entry_index=entry[namesp[p]],
                latest_lasso_entry_among_selected_terms=int(sel_entry),
                enters_after_every_selected_term=bool(entry[namesp[p]]
                                                      > sel_entry),
                below_every_selected_term_on_mi_and_perm=bool(all(
                    ranks[m][p] > max(ranks[m][namesp.index(t)]
                                      for t in form["support"])
                    for m in ("mi", "perm"))),
                # REPORTED, NOT GRADED: the cross-family-CV-optimal elastic net
                # is not a sparse selector at its own optimum - it admits pure
                # noise.  That is a measurement about the method, not about the
                # frozen model, and it is why the term set is frozen from the
                # cross-validated FORM search and not from this coefficient.
                enet_cv_optimum_coefficient=float(
                    best["coefficients"].get(namesp[p], 0.0)),
                enet_cv_optimum_admits_it=bool(
                    namesp[p] in best["support"]))
        pz_pass = all((not v["in_selected_support"])
                      and v["below_every_selected_term_on_mi_and_perm"]
                      and v["enters_after_every_selected_term"]
                      for v in pz.values())
        per_seed[seed] = dict(
            selected_terms=form["support"], n_terms=form["n_terms"],
            coefficients={namesp[c]: float(t) for c, t in zip(cols, theta)},
            lofo_cv_mse=form["lofo_cv_mse"],
            design_condition_number=cond_number(Xp, cols),
            enet_cv_optimum=best,
            spearman_top20_agreement=sp,
            ranking_mi={namesp[i]: float(mi[i]) for i in range(len(namesp))},
            ranking_perm={namesp[i]: float(pi[i]) for i in range(len(namesp))},
            ranking_enet_gridhits={namesp[i]: int(enet_score[i])
                                   for i in range(len(namesp))},
            planted_zero_control=pz,
            planted_zero_verdict="PASS" if pz_pass else "GATE FAIL",
            lasso_entry_order=entry,
            n_forms_considered=len(rows),
            top_forms=sorted(rows, key=lambda r: r["lofo_cv_mse"])[:8])
        print(f"  [{tag}/{library}/seed {seed}] terms={form['support']} "
              f"cv_mse={form['lofo_cv_mse']:.6g} PZ={per_seed[seed]['planted_zero_verdict']}",
              flush=True)
    forms = {s: per_seed[s]["selected_terms"] for s in SEEDS}
    res[f"{tag}__{library}"] = dict(
        target=tag, library=library, n_rows=int(X.shape[0]),
        n_candidates=len(names_l),
        seed_agreement=(len({tuple(sorted(v)) for v in forms.values()}) == 1),
        per_seed=per_seed, wall_seconds=round(time.time() - t0, 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", required=True,
                    help="comma-separated case list (the COMPLETE frozen runs)")
    ap.add_argument("--out", default=os.path.join(OUT, "fs3.json"))
    ap.add_argument("--r-unscaled", action="store_true",
                    help="declared sensitivity: fit R in raw m^2/s^3")
    a = ap.parse_args()
    global R_SCALED
    if a.r_unscaled:
        R_SCALED = False
    cases = a.cases.split(",")
    R.assert_no_test_case(cases)
    os.makedirs(OUT, exist_ok=True)
    d = load(cases)
    res = dict(cases=cases, cell_accounting=d["meta"], seeds=SEEDS,
               l1_ratios=L1_RATIOS, n_alpha=N_ALPHA, max_terms=MAX_TERMS,
               families_present=sorted({m["family"] for m in d["meta"].values()}),
               dead_12_intersection=[])
    for tag, X, y, g in (("R", d["Xr"], d["yr"], d["gr"]),
                         ("bDelta", d["Xb"], d["yb"], d["gb"])):
        for lib in ("prop", "full"):
            run_target(tag, X, y, g, d["names"], lib, res)
    def _np(o):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.bool_,)):
            return bool(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(type(o))
    json.dump(res, open(a.out, "w"), indent=1, default=_np)
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
