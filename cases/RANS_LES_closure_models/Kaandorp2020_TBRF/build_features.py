#!/usr/bin/env python3
"""Assemble the Kaandorp & Dwight (2020) feature sets FS1 / FS2 / FS3 and the
Pope tensor basis for the cases named in PREREGISTRATION.md.

Reads only from the benchmark clone. Writes one npz + a provenance json into
/home/ubuntu/closure-data/kaandorp_tbrf/  (OUTSIDE the repo).

Feature definitions, all from VERIFIED-PDF pages:
  FS1 (6 raw)  - Kaandorp & Dwight 2020, Table 1 p.25 / eq. (8) p.15 (Pope 1975)
  FS2 (10 raw) - Kaandorp & Dwight 2020, Table 1 p.25, invariants added by grad-k
  FS3 (9 raw)  - Kaandorp & Dwight 2020, Table 1 p.25 == Wang, Wu & Xiao 2017
                 Table 1 q1..q9 (q10 streamline curvature is not in Kaandorp's set)
  FS3 normalisation rule  q = q_raw / (|q_raw| + |q_norm|), except the wall-distance
                 Reynolds number - Wang, Wu & Xiao 2017 Table 1 caption p.10 and
                 Wu, Xiao & Paterson 2018 eq. (8) p.9.

Departures D1-D10 are listed in PREREGISTRATION.md section 2.2.
"""
from __future__ import annotations
import os, sys, re, json, time, hashlib
import numpy as np
from scipy.spatial import cKDTree

COMMON = "/home/ubuntu/Certonomous/cases/RANS_LES_closure_models/_common"
sys.path.insert(0, COMMON)
from of_read import (read_field, latest_time_dir, sym_to_full, anisotropy,
                     structured_gradient, plane_axes, structured_shape)
import sst_baseline_metrics as SB
from tensor_basis import invariants_and_basis, BETA_STAR, CT_DURBIN

OUT = "/home/ubuntu/closure-data/kaandorp_tbrf"
# POST-HOC diagnostic switch (see RESULTS.md sec. "post-hoc"): NO_DURBIN=1 drops
# departure D2 and uses Kaandorp eq. (7) verbatim, T = k/eps with no lower bound.
NO_DURBIN = bool(os.environ.get("NO_DURBIN"))
TAG = "_nodurbin" if NO_DURBIN else ""
os.makedirs(OUT, exist_ok=True)
DATA = SB.DATA

# ----------------------------------------------------------------- the splits
# frozen in PREREGISTRATION.md section 3.1
BENCH_TEST_HILLS = ["alpha_15_13929_4048", "alpha_15_13929_2024",
                    "alpha_05_4071_4048", "alpha_05_4071_2024"]
BENCH_VAL_HILLS = ["alpha_05_10071_4048", "alpha_05_10071_2024",
                   "alpha_15_7929_4048", "alpha_15_7929_2024"]
GROUP_SIBLINGS = ["alpha_15_13929_3036", "alpha_05_4071_3036"]   # dropped: leakage

TEST_CASES = ["AR_1_Ret_360", "AR_1_Ret_180", "CBFS13700"]
CONTROL_CASES = list(BENCH_TEST_HILLS)


def hill_group(case):
    """(alpha, domain-length) group key; the height suffix is dropped."""
    m = re.match(r"(alpha_\d+)_(\d+)_(\d+)$", case)
    if m:
        return (m.group(1), m.group(2))
    return (case, "")


def build_case_table():
    train, meta = [], {}
    for c, p in sorted(SB.PH_ALPHA.items()):
        meta[c] = (p, "hill")
        if c in BENCH_TEST_HILLS or c in BENCH_VAL_HILLS or c in GROUP_SIBLINGS:
            continue
        train.append(c)
    meta["PHLL10595"] = (os.path.join(DATA, "PH_Breuer"), "hill")
    train.append("PHLL10595")
    meta["CBFS13700"] = (os.path.join(DATA, "CBFS"), "hill")
    for c in ("AR_1_Ret_180", "AR_1_Ret_360"):
        meta[c] = (os.path.join(DATA, "DUCT", c), "duct")
    return sorted(train), meta


# ------------------------------------------------------- wall distance (D3)
_WALL_RE = re.compile(r"(\w+)\s*\{([^}]*)\}", re.S)


def wall_patches(case_dir):
    """[(name, startFace, nFaces)] for every polyMesh patch of type 'wall'."""
    bf = os.path.join(case_dir, "constant", "polyMesh", "boundary")
    txt = open(bf).read()
    body = txt[txt.index("// *"):]
    out = []
    for name, blk in _WALL_RE.findall(body):
        if re.search(r"type\s+wall\s*;", blk):
            sf = int(re.search(r"startFace\s+(\d+)\s*;", blk).group(1))
            nf = int(re.search(r"nFaces\s+(\d+)\s*;", blk).group(1))
            out.append((name, sf, nf))
    return out


def _read_points(path):
    txt = open(path).read()
    i = txt.index("// *")
    rest = txt[i:]
    m = re.search(r"(\d+)\s*\n?\s*\(", rest)
    n = int(m.group(1))
    body = rest[m.end():]
    body = body[:body.rindex(")")]
    v = np.fromstring(body.replace("(", " ").replace(")", " "), sep=" ")
    return v.reshape(n, 3)


def _read_faces(path):
    """-> list of index arrays (ASCII faceList, 'n(a b c ...)' per line)."""
    txt = open(path).read()
    i = txt.index("// *")
    rest = txt[i:]
    m = re.search(r"(\d+)\s*\n?\s*\(", rest)
    n = int(m.group(1))
    body = rest[m.end():]
    faces = []
    for mm in re.finditer(r"(\d+)\s*\(([^)]*)\)", body):
        faces.append(np.fromstring(mm.group(2), sep=" ", dtype=float).astype(np.int64))
        if len(faces) == n:
            break
    return faces


def wall_distance(case_dir, C):
    """Distance from every cell centre to the nearest wall-patch face centre or
    vertex. Verified against the shipped `walldist` on the periodic hills."""
    pm = os.path.join(case_dir, "constant", "polyMesh")
    pats = wall_patches(case_dir)
    if not pats:
        raise RuntimeError(f"{case_dir}: no wall patches")
    pts = _read_points(os.path.join(pm, "points"))
    faces = _read_faces(os.path.join(pm, "faces"))
    tgt = []
    for _, sf, nf in pats:
        for f in faces[sf:sf + nf]:
            v = pts[f]
            tgt.append(v.mean(axis=0))
            tgt.append(v)
    flat = np.vstack([t.reshape(-1, 3) for t in tgt])
    d, _ = cKDTree(flat).query(C, k=1)
    return d


# ------------------------------------------------------------------ features
def _mm(a, b):
    return np.einsum("nij,njk->nik", a, b)


def _tr(a):
    return np.einsum("nii->n", a)


def fs1_invariants(s, r):
    """Kaandorp Table 1 FS1: traces of S^2, S^3, R^2, R^2 S, R^2 S^2, R^2 S R S^2."""
    s2 = _mm(s, s); s3 = _mm(s2, s); r2 = _mm(r, r)
    return np.stack([_tr(s2), _tr(s3), _tr(r2), _tr(_mm(r2, s)),
                     _tr(_mm(r2, s2)),
                     _tr(_mm(_mm(_mm(r2, s), r), s2))], axis=1), s2, r2


def fs2_invariants(s, r, a, s2, r2):
    """Kaandorp Table 1 FS2: the 10 invariants added when grad-k enters.
    One labelling is taken for the three starred entries (departure D5)."""
    a2 = _mm(a, a)
    ra = _mm(r, a)
    return np.stack([
        _tr(a2),                                     # Ak^2
        _tr(_mm(a2, s)),                             # Ak^2 S
        _tr(_mm(a2, s2)),                            # Ak^2 S^2
        _tr(_mm(_mm(_mm(a2, s), a), s2)),            # Ak^2 S Ak S^2
        _tr(ra),                                     # R Ak
        _tr(_mm(ra, s)),                             # R Ak S
        _tr(_mm(ra, s2)),                            # R Ak S^2
        _tr(_mm(_mm(r2, a), s)),                     # R^2 Ak S   *
        _tr(_mm(_mm(r2, a), s2)),                    # R^2 Ak S^2 *
        _tr(_mm(_mm(_mm(r2, s), a), s2)),            # R^2 S Ak S^2 *
    ], axis=1)


def _nrm(raw, norm):
    """q = raw / (|raw| + |norm|)  (Wang 2017 Table 1 caption; Wu 2018 eq. 8)."""
    return raw / (np.abs(raw) + np.abs(norm) + 1e-300)


def fs3_features(U, k, eps, nu, d, gradU, gradk, gradp, tau_R, S_raw):
    """Kaandorp Table 1 FS3 == Wang, Wu & Xiao 2017 Table 1 q1..q9."""
    Om_raw = 0.5 * (gradU - gradU.transpose(0, 2, 1))
    nS = np.sqrt(np.maximum(_tr(_mm(S_raw, S_raw)), 0.0))
    nO = np.sqrt(np.maximum(-_tr(_mm(Om_raw, Om_raw)), 0.0))
    UU = np.einsum("ni,ni->n", U, U)

    q1 = _nrm(0.5 * (nO ** 2 - nS ** 2), nS ** 2)
    q2 = _nrm(k, 0.5 * UU)
    q3 = np.minimum(np.sqrt(np.maximum(k, 0.0)) * d / (50.0 * nu), 2.0)
    gp2 = np.einsum("ni,ni->n", gradp, gradp)
    q4 = _nrm(np.einsum("ni,ni->n", U, gradp), np.sqrt(gp2 * UU))
    q5 = _nrm(k / np.maximum(eps, 1e-300), 1.0 / np.maximum(nS, 1e-300))
    # d(U_k^2)/dx_k with gradU[i][j] = dU_i/dx_j
    dUk2 = 2.0 * np.einsum("nk,nkk->n", U, gradU)
    q6 = _nrm(np.sqrt(gp2), 0.5 * dUk2)
    UgU = np.einsum("ni,nj,nij->n", U, U, gradU)
    den7 = np.sqrt(np.maximum(UU * np.einsum("ni,nij,nk,nkj->n", U, gradU, U, gradU), 0.0))
    q7 = _nrm(UgU, den7)
    q8 = _nrm(np.einsum("ni,ni->n", U, gradk),
              np.abs(np.einsum("njk,njk->n", tau_R, S_raw)))
    q9 = _nrm(np.sqrt(np.maximum(np.einsum("nij,nij->n", tau_R, tau_R), 0.0)), k)
    return np.stack([q1, q2, q3, q4, q5, q6, q7, q8, q9], axis=1)


FEATURE_NAMES = (
    ["fs1_trS2", "fs1_trS3", "fs1_trR2", "fs1_trR2S", "fs1_trR2S2", "fs1_trR2SRS2"] +
    ["fs2_trA2", "fs2_trA2S", "fs2_trA2S2", "fs2_trA2SAS2", "fs2_trRA",
     "fs2_trRAS", "fs2_trRAS2", "fs2_trR2AS", "fs2_trR2AS2", "fs2_trR2SAS2"] +
    ["fs3_q1_Qcrit", "fs3_q2_TI", "fs3_q3_Red", "fs3_q4_dpds", "fs3_q5_timescale",
     "fs3_q6_pgrad", "fs3_q7_nonorth", "fs3_q8_convprod", "fs3_q9_tauratio"])
N_FS1 = 6


def case_arrays(case, path, family):
    d = SB.load_case(case, path, family)
    t = d["time"]
    C, U, k, n = d["C"], d["U"], d["k"], d["n"]
    omega = read_field(os.path.join(path, t, "omega"))
    p = read_field(os.path.join(path, t, "p"))
    nu = SB.case_meta(path).get("nu")
    if nu is None or nu <= 0:
        raise RuntimeError(f"{case}: no nu")

    # velocity gradient dU_i/dx_j  (D1)
    A = np.asarray(d["gradU"]).reshape(-1, 3, 3).transpose(0, 2, 1)
    grad_src = ("shipped gradU" if os.path.exists(os.path.join(path, t, "gradU"))
                else "of_read.structured_gradient (D1)")
    S_raw = 0.5 * (A + A.transpose(0, 2, 1))
    W_raw = 0.5 * (A - A.transpose(0, 2, 1))

    eps = BETA_STAR * np.maximum(k, 0.0) * np.maximum(omega, 1e-30)
    Tt = np.maximum(k, 0.0) / np.maximum(eps, 1e-30)
    if not NO_DURBIN:
        Tt = np.maximum(Tt, CT_DURBIN * np.sqrt(nu / np.maximum(eps, 1e-30)))   # D2
    s = S_raw * Tt[:, None, None]
    r = W_raw * Tt[:, None, None]

    gradk = structured_gradient(C, k)
    gradp = structured_gradient(C, p)

    # A_k = -I x grad(k), grad(k) normalised by sqrt(k)/eps  (Kaandorp eq. 13)
    g = gradk * (np.sqrt(np.maximum(k, 0.0)) / np.maximum(eps, 1e-30))[:, None]
    Ak = np.zeros((n, 3, 3))
    Ak[:, 0, 1] = -g[:, 2]; Ak[:, 0, 2] = g[:, 1]
    Ak[:, 1, 0] = g[:, 2];  Ak[:, 1, 2] = -g[:, 0]
    Ak[:, 2, 0] = -g[:, 1]; Ak[:, 2, 1] = g[:, 0]

    f1, s2, r2 = fs1_invariants(s, r)
    f2 = fs2_invariants(s, r, Ak, s2, r2)
    wd_file = os.path.join(path, t, "walldist")
    dist = wall_distance(path, C)
    wd_check = None
    if os.path.exists(wd_file):
        wd = read_field(wd_file)
        wd_check = dict(rel_L2=float(np.linalg.norm(dist - wd) / np.linalg.norm(wd)),
                        max_abs=float(np.abs(dist - wd).max()),
                        median_rel=float(np.median(np.abs(dist - wd)
                                                   / np.maximum(wd, 1e-30))))
    tau_R = sym_to_full(d["tau_R"])
    f3 = fs3_features(U, k, eps, nu, dist, A, gradk, gradp, tau_R, S_raw)

    _, Tb = invariants_and_basis(s, r)
    b_L, valid = anisotropy(sym_to_full(d["tau_LES"]), d["k_LES"])
    b_R, _ = anisotropy(tau_R, k, k_ref=d["k_LES"])
    X = np.concatenate([f1, f2, f3], axis=1)
    ok = valid & np.isfinite(X).all(axis=1) & np.isfinite(Tb).all(axis=(1, 2, 3)) \
        & np.isfinite(b_L).all(axis=(1, 2))
    return dict(case=case, X=X.astype(np.float64), T=Tb.astype(np.float32),
                b_LES=b_L.astype(np.float32), b_RANS=b_R.astype(np.float32),
                valid=ok, n=n, grad_src=grad_src, wd_check=wd_check, nu=nu)


def main():
    t0 = time.time()
    train, meta = build_case_table()
    allc = train + TEST_CASES + CONTROL_CASES
    assert len(set(allc)) == len(allc), "case listed twice"
    assert not (set(train) & set(TEST_CASES)), "train/test overlap"
    assert not (set(train) & set(CONTROL_CASES)), "train/control overlap"
    gtr = {hill_group(c) for c in train}
    gte = {hill_group(c) for c in TEST_CASES + CONTROL_CASES}
    assert not (gtr & gte), f"group leak: {gtr & gte}"
    print(f"[split] train={len(train)} test={len(TEST_CASES)} "
          f"control={len(CONTROL_CASES)}; group-disjoint OK", flush=True)

    X, T, bL, bR, val, cid, names, splits, wd = [], [], [], [], [], [], [], [], {}
    for i, c in enumerate(allc):
        p, fam = meta[c]
        d = case_arrays(c, p, fam)
        X.append(d["X"]); T.append(d["T"]); bL.append(d["b_LES"]); bR.append(d["b_RANS"])
        val.append(d["valid"]); cid.append(np.full(d["n"], i, np.int32))
        names.append(c)
        splits.append("train" if c in train else
                      ("TEST" if c in TEST_CASES else "control"))
        if d["wd_check"] is not None:
            wd[c] = d["wd_check"]
        print(f"[ok] {c:24s} n={d['n']:6d} split={splits[-1]:7s} "
              f"valid={int(d['valid'].sum()):6d} grad={d['grad_src']}", flush=True)

    np.savez(os.path.join(OUT, f"features{TAG}.npz"),
             X=np.concatenate(X), T=np.concatenate(T),
             b_LES=np.concatenate(bL), b_RANS=np.concatenate(bR),
             valid=np.concatenate(val), case_id=np.concatenate(cid),
             names=np.array(names), splits=np.array(splits),
             feature_names=np.array(FEATURE_NAMES))
    prov = dict(benchmark="/home/ubuntu/closure-challenge-benchmark",
                commit="deb91557184af3cb95f5190494ec52d8f2c6a0d1",
                source_url="https://github.com/rmcconke/closure-challenge-benchmark.git",
                sha256_ls_files_data="e9cd3f22ec235bd3e218931dfb76d522b429b63883a16f2c86cbb3993a360401",
                beta_star=BETA_STAR, CT_durbin=(0.0 if NO_DURBIN else CT_DURBIN),
                durbin_bound_applied=(not NO_DURBIN),
                n_train_cases=len(train), train_cases=train,
                test_cases=TEST_CASES, control_cases=CONTROL_CASES,
                walldist_verification=wd, seconds=round(time.time() - t0, 1))
    json.dump(prov, open(os.path.join(OUT, f"features{TAG}_provenance.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in prov.items() if k != "train_cases"}, indent=1))


if __name__ == "__main__":
    main()
