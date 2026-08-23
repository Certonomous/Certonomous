#!/usr/bin/env python3
"""FS1 - maximal feature library. Computes every candidate invariant on every
benchmark case. SELECTS NOTHING.

Blocks
  A  47 minimal-integrity-basis invariants of {S, Omega, A_p, A_k}
     [Wu, Xiao & Paterson 2018, Table B.4, arXiv:1801.02762v4 preprint p. 35;
      antisymmetric mapping A = -I x v, their Eq. (B.1a,b), p. 35]
     normalised per their Table 1 (p. 8): alpha_hat = alpha/(|alpha| + |beta|)
  B  the same 47, with the time scale replaced by the Durbin-bounded variant
     (normalisation VARIANT, not a new feature - see FEATURE_LIBRARY.md)
  C  supplementary scalars q1-q3 [Wu et al. Table 2, p. 9] and the
     Ling/Kaandorp scalar set, each with its Galilean status flagged
  D  Pope's five invariants of the normalised (s, r) pair, for continuity with
     the tensor-basis reproductions

Writes one .npz per case to /home/ubuntu/closure-data/features/ (outside the repo).
Nothing is fitted. Reads only.
"""
from __future__ import annotations
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, COMMON)
from of_read import read_field, latest_time_dir, sym_to_full, structured_gradient
from wall_distance import wall_distance
import sst_baseline_metrics as SB

OUT = "/home/ubuntu/closure-data/features"
BETA_STAR = 0.09
CT_DURBIN = 6.0
os.makedirs(OUT, exist_ok=True)

mm = lambda a, b: np.einsum("nij,njk->nik", a, b)
tr = lambda a: np.einsum("nii->n", a)


def antisym_from_vec(v):
    """A = -I x v  (Wu et al. Eq. B.1): A_ij = -eps_ijk v_k."""
    n = v.shape[0]
    A = np.zeros((n, 3, 3))
    A[:, 0, 1] = -v[:, 2]; A[:, 1, 0] = v[:, 2]
    A[:, 0, 2] = v[:, 1];  A[:, 2, 0] = -v[:, 1]
    A[:, 1, 2] = -v[:, 0]; A[:, 2, 1] = v[:, 0]
    return A


def invariants_47(S, W, P, K):
    """Wu et al. Table B.4. Returns (N,47) and the list of 47 names."""
    S2 = mm(S, S); S3 = mm(S2, S)
    W2 = mm(W, W); P2 = mm(P, P); K2 = mm(K, K)
    out, names = [], []

    def add(name, M):
        out.append(tr(M)); names.append(name)

    add("I1_trS2", S2); add("I2_trS3", S3)                       # (1,0)
    add("I3_trW2", W2); add("I4_trP2", P2); add("I5_trK2", K2)   # (0,1)
    for tag, A, A2 in (("W", W, W2), ("P", P, P2), ("K", K, K2)):  # (1,1) 6-14
        add(f"tr{tag}2S", mm(A2, S))
        add(f"tr{tag}2S2", mm(A2, S2))
        add(f"tr{tag}2S{tag}S2", mm(mm(mm(A2, S), A), S2))
    add("trWP", mm(W, P)); add("trPK", mm(P, K)); add("trWK", mm(W, K))  # (0,2)
    # (1,2) 18-41: three antisymmetric pairs x 8
    for (t1, A, A2), (t2, B, B2) in ((("W", W, W2), ("P", P, P2)),
                                     (("W", W, W2), ("K", K, K2)),
                                     (("P", P, P2), ("K", K, K2))):
        add(f"tr{t1}{t2}S", mm(mm(A, B), S))
        add(f"tr{t1}{t2}S2", mm(mm(A, B), S2))
        add(f"tr{t1}2{t2}S", mm(mm(A2, B), S))          # starred pair, term 1
        add(f"tr{t2}2{t1}S", mm(mm(B2, A), S))          # starred pair, term 2
        add(f"tr{t1}2{t2}S2", mm(mm(A2, B), S2))
        add(f"tr{t2}2{t1}S2", mm(mm(B2, A), S2))
        add(f"tr{t1}2S{t2}S2", mm(mm(mm(A2, S), B), S2))
        add(f"tr{t2}2S{t1}S2", mm(mm(mm(B2, S), A), S2))
    add("trWPK", mm(mm(W, P), K))                                # (0,3) 42
    add("trWPKS", mm(mm(mm(W, P), K), S))                        # (1,3) 43-47
    add("trWKPS", mm(mm(mm(W, K), P), S))
    add("trWPKS2", mm(mm(mm(W, P), K), S2))
    add("trWKPS2", mm(mm(mm(W, K), P), S2))
    add("trWPSKS2", mm(mm(mm(mm(W, P), S), K), S2))
    return np.stack(out, axis=1), names


def norm_bounded(a, beta):
    """Wu et al. Table 1 / Eq. (8): alpha_hat = alpha / (|alpha| + |beta|)."""
    na = np.sqrt((a ** 2).sum(axis=(1, 2)))[:, None, None] if a.ndim == 3 else \
         np.linalg.norm(a, axis=1)[:, None]
    b = beta[:, None, None] if a.ndim == 3 else beta[:, None]
    return a / np.maximum(na + np.abs(b), 1e-30)


def case_features(case, path, family):
    d = SB.load_case(case, path, family)
    t = latest_time_dir(path)
    C, U, k, nut = d["C"], d["U"], d["k"], d["nut"]
    omega = read_field(os.path.join(path, t, "omega"))
    p = read_field(os.path.join(path, t, "p"))
    nu = SB.case_meta(path).get("nu", 1e-5)
    A = (np.asarray(d["gradU"]).reshape(-1, 3, 3).transpose(0, 2, 1)
         if d.get("gradU") is not None else structured_gradient(C, U))
    S = 0.5 * (A + A.transpose(0, 2, 1))
    W = 0.5 * (A - A.transpose(0, 2, 1))
    eps = BETA_STAR * np.maximum(k, 0.0) * np.maximum(omega, 1e-30)
    gp = structured_gradient(C, p)
    gk = structured_gradient(C, k)
    DUDt = np.einsum("nj,nij->ni", U, A)                 # steady mean material derivative
    dwall, wp = wall_distance(path, C)
    if dwall is None:
        dwall = np.full(C.shape[0], np.nan)

    nS = np.sqrt((S ** 2).sum(axis=(1, 2)))
    nW = np.sqrt((W ** 2).sum(axis=(1, 2)))

    blocks, names = [], []
    for tag, Tinv in (("A", eps / np.maximum(k, 1e-30)),           # beta = eps/k
                      ("B", 1.0 / np.maximum(
                          np.maximum(k / np.maximum(eps, 1e-30),
                                     CT_DURBIN * np.sqrt(nu / np.maximum(eps, 1e-30))), 1e-30))):
        Sh = norm_bounded(S, Tinv)
        Wh = norm_bounded(W, nW)
        Ph = antisym_from_vec(norm_bounded(gp, np.linalg.norm(DUDt, axis=1)))
        Kh = antisym_from_vec(norm_bounded(gk, eps / np.sqrt(np.maximum(k, 1e-30))))
        inv, nm = invariants_47(Sh, Wh, Ph, Kh)
        blocks.append(inv); names += [f"{n}__{tag}" for n in nm]

    # Block C - supplementary scalars
    _b = lambda a, c: np.where(np.abs(a) + np.abs(c) > 1e-30,
                               a / np.maximum(np.abs(a) + np.abs(c), 1e-30), 0.0)
    tau_R = sym_to_full(d["tau_R"])
    # D476/FS5: the wall-distance Reynolds number BEFORE the clip at 2.0. The
    # feature q1_wallRe below is min(this, 2.0) -- one expression, so the
    # diagnostic companion cannot drift from the feature it shadows. NaN
    # handling is therefore identical by construction: both inherit dwall's
    # NaN (np.minimum propagates it), so the clipped and unclipped columns are
    # non-finite on exactly the same cells.
    q1_wallRe_raw = np.sqrt(np.maximum(k, 0)) * dwall / (50.0 * nu)
    q = {
        "q1_wallRe":        np.minimum(q1_wallRe_raw, 2.0),
        "q2_turbIntensity": _b(k, 0.5 * (U ** 2).sum(1)),
        "q3_timeScaleRatio": _b(k / np.maximum(eps, 1e-30), 1.0 / np.maximum(nS, 1e-30)),
        "q4_pgradAlongStreamline": _b(np.einsum("ni,ni->n", U, gp),
                                      np.linalg.norm(gp, axis=1) * np.linalg.norm(U, axis=1)),
        "q5_excessRotation": _b(nW - nS, nW + nS),
        "q6_stressRatio":   _b(np.sqrt((tau_R ** 2).sum(axis=(1, 2))), k),
        "q7_viscRatio":     _b(nut, 100.0 * nu),
        "q8_kConvection":   _b(np.einsum("ni,ni->n", U, gk),
                               np.abs(np.einsum("nij,nij->n", tau_R, S))),
        "q9_nonOrthogonality": _b(np.abs(np.einsum("ni,nj,nij->n", U, U, S)),
                                  (np.linalg.norm(U, axis=1) ** 2) * nS),
        "q10_streamlineCurv": _b(np.abs(np.einsum("ni,nij,nj->n", U, A, U)),
                                 (np.linalg.norm(U, axis=1) ** 2)
                                 * np.sqrt((A ** 2).sum(axis=(1, 2)))),
        "q11_turbReynolds": _b(np.sqrt(np.maximum(k, 0)) / np.maximum(nu * omega, 1e-30), 50.0),
    }
    blocks.append(np.stack(list(q.values()), axis=1)); names += list(q.keys())

    # Block D - Pope's five, on the Durbin-bounded normalisation
    Tt = np.maximum(k / np.maximum(eps, 1e-30),
                    CT_DURBIN * np.sqrt(nu / np.maximum(eps, 1e-30)))[:, None, None]
    s, r = S * Tt, W * Tt
    s2 = mm(s, s); r2 = mm(r, r)
    pope = np.stack([tr(s2), tr(r2), tr(mm(s2, s)), tr(mm(r2, s)), tr(mm(r2, s2))], axis=1)
    blocks.append(pope); names += ["lam1", "lam2", "lam3", "lam4", "lam5"]

    F = np.concatenate(blocks, axis=1).astype(np.float64)

    # DIAGNOSTICS (D476). Read by the FS5 coverage instrument only. These are
    # NOT features: they never enter F, never enter the manifest's `features`,
    # and nothing that selects or fits reads them.
    diag = {"q1_wallRe_raw": q1_wallRe_raw}
    D = np.stack(list(diag.values()), axis=1).astype(np.float64)
    return F, names, D, list(diag.keys()), dict(
        n_cells=int(C.shape[0]), wall_patches=wp, nu=float(nu),
        family=family, time=t)


def main():
    cases = []
    for c, p in sorted(SB.PH_ALPHA.items()):
        cases.append((c, p, "hill"))
    for c, p in sorted(SB.DUCTS.items()):
        cases.append((c, p, "duct"))
    for c, sub, fam in (("PHLL10595", "PH_Breuer", "hill_breuer"),
                        ("CBFS13700", "CBFS", "cbfs"), ("NASA_2DWMH", "NASA_2DWMH", "hump")):
        pp = os.path.join(SB.DATA, sub)
        if os.path.isdir(os.path.join(pp, c)):
            pp = os.path.join(pp, c)
        cases.append((c, pp, fam))
    meta = {}
    names = None
    diag_names = None
    for c, p, fam in cases:
        F, names, D, diag_names, m = case_features(c, p, fam)
        np.savez_compressed(os.path.join(OUT, f"{c}.npz"), F=F.astype(np.float32),
                            names=np.array(names),
                            D=D.astype(np.float32), diag_names=np.array(diag_names))
        m["n_features"] = F.shape[1]
        m["n_nonfinite"] = int((~np.isfinite(F)).sum())
        m["n_diag_nonfinite"] = int((~np.isfinite(D)).sum())
        meta[c] = m
        print(f"[ok] {c:24s} {fam:12s} n={m['n_cells']:6d} F={F.shape} nonfinite={m['n_nonfinite']}", flush=True)
    json.dump({"features": names, "cases": meta,
               "n_features": len(names),
               "diagnostics": diag_names,
               "diagnostics_note":
                   "D476/FS5. Arrays under the `D` key of each case .npz, named by "
                   "`diag_names`. DIAGNOSTIC ONLY: not features, never in `features`, "
                   "never in F, read by the FS5 coverage instrument alone."},
              open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
    print(f"\n{len(names)} features x {len(cases)} cases -> {OUT}")
    print(f"{len(diag_names)} diagnostics (not features): {diag_names}")


if __name__ == "__main__":
    main()
