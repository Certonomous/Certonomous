#!/usr/bin/env python3
"""FS2 degeneracy audit + FS5 extrapolation-coverage check on the FS1 library.

Per flow family and per feature: variance, range, the fraction algebraically
zero, and the feature-matrix numerical rank. Plus the tensor-basis per-cell rank
(charter section 5(b)) and the FS5 test-vs-training range coverage.

No training. Reads the FS1 .npz files and the benchmark tensor basis.
"""
from __future__ import annotations
import json, os, sys, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, COMMON)
sys.path.insert(0, os.path.join(os.path.dirname(COMMON), "Ling2016_TBNN"))
from train_tbnn import TEST

FEAT = "/home/ubuntu/closure-data/features"
OUT_JSON = os.path.join(FEAT, "fs2_audit.json")
ZERO_ABS = 1e-12          # |value| below this counts as algebraically zero
ZERO_REL = 1e-12          # ... or below this fraction of the feature's own max
RANK_RCOND = 1e-10        # SVD tolerance, relative to the largest singular value

# ---- D476/FS5: the unclipped q1 companion -------------------------------
# q1_wallRe is clipped at 2.0, and on this column the training maximum IS the
# clip, so the FS5 above-max branch is structurally unreachable: it reports
# "in range" by construction, not by measurement. The companion below is the
# same quantity WITHOUT the clip -- a diagnostic that never enters F or the
# manifest's `features`. See FS5_D476_CLIP_REPAIR_PREREGISTRATION.md.
DIAG_COMPANION = "q1_wallRe_raw"
PLANT_FACTOR = 1.5        # planted excursion, in multiples of the training max


def load_all():
    man = json.load(open(os.path.join(FEAT, "manifest.json")))
    names = man["features"]
    data, fam = {}, {}
    for case, m in man["cases"].items():
        z = np.load(os.path.join(FEAT, f"{case}.npz"), allow_pickle=True)
        data[case] = z["F"].astype(np.float64)
        fam[case] = m["family"]
    return names, data, fam, man


def rank_of(X):
    """Numerical rank of the column-standardised feature matrix."""
    Xs = X - X.mean(0)
    sd = Xs.std(0); sd[sd < 1e-300] = 1.0
    Xs = Xs / sd
    s = np.linalg.svd(Xs, compute_uv=False)
    tol = RANK_RCOND * s[0] if s[0] > 0 else 0.0
    return int((s > tol).sum()), s


def case_npz(case):
    return os.path.join(FEAT, f"{case}.npz")


def read_companion(npz_path):
    """The ONLY path by which the unclipped companion reaches this audit.

    Returns the column as float64, or None if this .npz predates the D476
    companion. The planted control below goes through this same function, from
    disk, so what the control proves is what the audit actually uses.
    """
    z = np.load(npz_path, allow_pickle=True)
    if "D" not in z.files or "diag_names" not in z.files:
        return None
    dn = [str(x) for x in z["diag_names"]]
    if DIAG_COMPANION not in dn:
        return None
    return z["D"][:, dn.index(DIAG_COMPANION)].astype(np.float64)


def companion_coverage(x, hi, span):
    """Coverage of one case's companion column against the TRAINING companion
    range. Non-finite cells are excluded and counted separately rather than
    silently dropped."""
    fin = np.isfinite(x)
    v = x[fin]
    above = v > hi
    return {
        "n_cells": int(x.size),
        "n_cells_nonfinite": int((~fin).sum()),
        "n_cells_above_training_max": int(above.sum()),
        "frac_cells_above_training_max": float(above.mean()) if v.size else 0.0,
        # negative means the case stays inside the training envelope
        "worst_excursion_training_spans": float(((v - hi) / span).max()) if v.size else float("nan"),
        "max": float(v.max()) if v.size else float("nan"),
        "min": float(v.min()) if v.size else float("nan"),
    }


def planted_control(case, hi, span):
    """Rule 3, on the companion reader.

    Inject one value strictly above every training companion value into a COPY
    of a TEST case's companion column, write it to disk, read it back through
    read_companion() and score it with companion_coverage() -- the audit's own
    path. The flagged count must rise by exactly one and the reported maximum
    must be the planted value. If the reader cannot see the plant, this audit
    REFUSES (exit 2): a zero from a reader not shown able to see a non-zero is
    not evidence.
    """
    src = case_npz(case)
    z = np.load(src, allow_pickle=True)
    D = np.array(z["D"])
    dn = [str(x) for x in z["diag_names"]]
    j = dn.index(DIAG_COMPANION)

    base = companion_coverage(read_companion(src), hi, span)
    # plant into the SMALLEST finite cell, which is certainly not already
    # flagged, so a working reader must show exactly one more flagged cell
    col = D[:, j].astype(np.float64)
    fin = np.where(np.isfinite(col))[0]
    idx = int(fin[np.argmin(col[fin])])
    plant = float(PLANT_FACTOR * hi)

    with tempfile.TemporaryDirectory() as td:
        D[idx, j] = plant
        p = os.path.join(td, os.path.basename(src))
        np.savez_compressed(p, F=z["F"], names=z["names"], D=D,
                            diag_names=z["diag_names"])
        got = read_companion(p)
        seen = companion_coverage(got, hi, span) if got is not None else None

    ok = (seen is not None
          and seen["n_cells_above_training_max"] == base["n_cells_above_training_max"] + 1
          and seen["max"] >= plant * (1.0 - 1e-5))
    rec = {
        "method": "one cell of a copy of the test case's companion column set to "
                  f"{PLANT_FACTOR} x the training unclipped max, written to a "
                  "temporary .npz and read back through read_companion() and "
                  "companion_coverage() -- the same path the audit uses",
        "case": case, "cell_index": idx, "planted_value": plant,
        "training_max": float(hi),
        "flagged_before": base["n_cells_above_training_max"],
        "flagged_after": None if seen is None else seen["n_cells_above_training_max"],
        "max_read_back": None if seen is None else seen["max"],
        "verdict": "PASS" if ok else "GATE FAIL",
    }
    if not ok:
        print("REFUSED (rule 3, planted control): the companion reader did not "
              f"see a planted excursion of {plant:.6g} in {case} at cell {idx}. "
              f"Flagged cells before {rec['flagged_before']}, after "
              f"{rec['flagged_after']} (expected {base['n_cells_above_training_max'] + 1}), "
              f"max read back {rec['max_read_back']}. A zero from this reader is "
              "not evidence; no coverage number is emitted.", file=sys.stderr)
        sys.exit(2)
    return rec


def companion_block(tr_cases, te_cases):
    """The FS5 physical-envelope subsection (D476). Measures only; moves no
    verdict."""
    tr = [read_companion(case_npz(c)) for c in tr_cases]
    te = [read_companion(case_npz(c)) for c in te_cases]
    if any(v is None for v in tr + te):
        missing = [c for c, v in zip(tr_cases + te_cases, tr + te) if v is None]
        print("REFUSED: the unclipped q1 companion is absent from "
              f"{len(missing)} case .npz file(s), e.g. {missing[:3]}. These "
              "predate D476; re-run build_features.py. The FS5 companion "
              "instrument does not degrade to silence.", file=sys.stderr)
        sys.exit(2)

    pooled_tr = np.concatenate(tr)
    f = np.isfinite(pooled_tr)
    v = pooled_tr[f]
    lo, hi = float(v.min()), float(v.max())
    span = max(hi - lo, 1e-30)
    train = {
        "n_cells": int(pooled_tr.size), "n_cells_nonfinite": int((~f).sum()),
        "min": lo, "p50": float(np.percentile(v, 50)),
        "p99": float(np.percentile(v, 99)), "max": hi, "span": span,
    }
    control = planted_control(sorted(te_cases)[0], hi, span)
    per = {c: companion_coverage(x, hi, span) for c, x in zip(te_cases, te)}
    return {
        "label":
            "PHYSICAL-ENVELOPE coverage, NOT input-space coverage. The MODEL "
            "INPUT q1_wallRe remains clipped at 2.0 and therefore remains "
            "trivially in-range on the above-max branch by construction -- "
            "nothing here changes that, and no feature, no column of F and no "
            "entry of the manifest's `features` is altered. The numbers below "
            "are the UNCLIPPED companion "
            f"`{DIAG_COMPANION}`, a diagnostic only, and they answer the "
            "question FS5 exists to ask: did the PHYSICS leave the training "
            "envelope. Measurement only -- no verdict moves from this block "
            "(D476 chief clause); excursions on already-graded cases are "
            "instrument information beside standing verdicts.",
        "feature_shadowed": "q1_wallRe", "clip": 2.0,
        "planted_control": control,
        "training_unclipped": train,
        "per_test_case": per,
    }


def main():
    names, data, fam, man = load_all()
    nF = len(names)
    families = sorted(set(fam.values()))
    out = {"n_features": nF, "families": families,
           "rank_rcond": RANK_RCOND, "zero_abs": ZERO_ABS,
           "zero_test": "absolute only: max|v| < 1e-12; see L-TBD-F2",
           "per_family": {}, "per_feature": {}, "coverage": {}}

    fam_X = {f: np.concatenate([data[c] for c in data if fam[c] == f]) for f in families}
    pooled = np.concatenate([data[c] for c in data])

    # ---- per-family rank and per-feature degeneracy
    for f in families + ["POOLED"]:
        X = pooled if f == "POOLED" else fam_X[f]
        r, s = rank_of(X)
        col_max = np.abs(X).max(0)
        # DEAD is an ABSOLUTE test only. A relative test against a global max
        # across features is meaningless here: the features are incommensurable
        # (the Pope invariants reach 1e14 while every normalised invariant is
        # bounded by ~1), so a global threshold of 1e-12*gmax = 150 would flag
        # every bounded feature as dead. See LESSONS_DRAFT.md L-TBD-F2.
        dead = [names[i] for i in range(nF) if col_max[i] < ZERO_ABS]
        near_const = [names[i] for i in range(nF)
                      if names[i] not in dead and X[:, i].std() < 1e-8 * max(col_max[i], 1e-30)]
        out["per_family"][f] = {
            "n_cells": int(X.shape[0]), "rank": r, "n_features": nF,
            "rank_deficiency": nF - r,
            "n_dead": len(dead), "dead_features": dead,
            "n_near_constant": len(near_const), "near_constant_features": near_const,
            "max_abs_by_feature": {names[i]: float(col_max[i]) for i in range(nF)},
            "singular_value_ratio_first_to_last": float(s[0] / max(s[-1], 1e-300)),
        }

    # ---- per-feature stats, pooled
    for i, n in enumerate(names):
        v = pooled[:, i]
        out["per_feature"][n] = {
            "mean": float(v.mean()), "std": float(v.std()),
            "min": float(v.min()), "max": float(v.max()),
            "p01": float(np.percentile(v, 1)), "p50": float(np.percentile(v, 50)),
            "p99": float(np.percentile(v, 99)),
            "frac_below_1e-12_abs": float((np.abs(v) < ZERO_ABS).mean()),
            # D476: hard-bound saturation. N-B38 recorded that whether other
            # bounded features saturate was UNMEASURED; these two close it.
            # A HARD bound shows frac_at_max well above 0. An asymptotically
            # bounded `_b`-form feature that crowds its bound without touching
            # it shows frac_at_max ~ 0 with p99 near the bound -- a different
            # pattern, and reading it is an audit question, not a repair.
            "frac_at_min": float((v == v.min()).mean()),
            "frac_at_max": float((v == v.max()).mean()),
        }

    # ---- FS5 coverage: TEST cases against TRAINING cases
    tr_cases = [c for c in data if c not in TEST]
    te_cases = [c for c in data if c in TEST]
    Xtr = np.concatenate([data[c] for c in tr_cases])
    lo, hi = Xtr.min(0), Xtr.max(0)
    span = np.maximum(hi - lo, 1e-30)
    cov = {}
    for c in te_cases:
        X = data[c]
        outside = (X < lo) | (X > hi)
        # how far beyond, in units of the training span
        beyond = np.maximum((lo - X) / span, (X - hi) / span).max(0)
        cov[c] = {
            "n_cells": int(X.shape[0]),
            "frac_cells_any_feature_outside": float(outside.any(1).mean()),
            "mean_frac_features_outside_per_cell": float(outside.mean()),
            "features_with_any_outside": int((outside.any(0)).sum()),
            "worst_features": sorted(
                [(names[i], float(outside[:, i].mean()), float(beyond[i]))
                 for i in range(nF) if outside[:, i].any()],
                key=lambda t: -t[1])[:12],
        }
    out["coverage"] = {"train_cases": sorted(tr_cases), "test_cases": sorted(te_cases),
                       "per_test_case": cov}
    out["coverage"]["q1_wallRe_unclipped_companion"] = companion_block(
        tr_cases, te_cases)

    # ---- charter section 5(b): per-cell rank of Pope's ten-tensor basis.
    # Re-measured here because the figure "3.24, never above 5" is quoted in
    # three records from a pointer (Kaandorp2020_TBRF/train_log.json) that does
    # not resolve. This is the live source.
    # [2026-08-22: the file exists on disk and is now committed at this commit;
    # it was untracked, so git-side lookups reported it absent -- see L-225.
    # The FS2 sec. 4 re-sourcing stands; 3.24 is the pooled-sample rank
    # statistic, 3.738 the case-mean.]
    DS = "/home/ubuntu/closure-data/tbnn/dataset.npz"
    if os.path.exists(DS):
        z = np.load(DS, allow_pickle=True)
        Tt, cid = z["T"], z["case_id"]
        cnames = [str(x) for x in z["names"]]
        rng = np.random.default_rng(0)
        br = {}
        for i, cn in enumerate(cnames):
            idx = np.where(cid == i)[0]
            if idx.size > 4000:
                idx = rng.choice(idx, 4000, replace=False)
            M = Tt[idx].reshape(len(idx), 10, 9).astype(np.float64)
            sv = np.linalg.svd(M, compute_uv=False)
            rk = (sv > 1e-8 * sv[:, :1]).sum(1)
            br[cn] = {"n_sampled": int(len(idx)), "mean_rank": float(rk.mean()),
                      "min_rank": int(rk.min()), "max_rank": int(rk.max()),
                      "hist": np.bincount(rk, minlength=11).tolist()}
        allr = np.array([v["mean_rank"] for v in br.values()])
        out["tensor_basis_rank"] = {
            "method": "numerical rank of the 10x9 flattened tensor stack per cell, "
                      "singular values above 1e-8*sigma_max; up to 4000 cells per case, seed 0",
            "per_case": br,
            "pooled_mean_of_case_means": float(allr.mean()),
            "min_case_mean": float(allr.min()), "max_case_mean": float(allr.max()),
            "max_rank_any_cell": int(max(v["max_rank"] for v in br.values())),
            "source_note": "live re-measurement; supersedes the unsourced 3.24 quoted in "
                           "Ling2016_TBNN/RESULTS.md, Wu2018_PIML_RF/RESULTS.md and "
                           "_common/FEASIBILITY.md (charter section 5(b) provenance defect)",
        }
        print(f"\ntensor-basis per-cell rank: case means {allr.min():.3f}-{allr.max():.3f}, "
              f"mean of case means {allr.mean():.3f}, max rank in any cell "
              f"{out['tensor_basis_rank']['max_rank_any_cell']}")

    json.dump(out, open(OUT_JSON, "w"), indent=1)

    print(f"{nF} features, families {families}")
    print(f"\n{'family':14s} {'cells':>8s} {'rank':>6s} {'deficit':>8s} {'dead':>6s} {'nearconst':>10s} {'s1/sN':>12s}")
    for f in families + ["POOLED"]:
        d = out["per_family"][f]
        print(f"{f:14s} {d['n_cells']:8d} {d['rank']:6d} {d['rank_deficiency']:8d} "
              f"{d['n_dead']:6d} {d['n_near_constant']:10d} {d['singular_value_ratio_first_to_last']:12.3e}")
    print("\nDEAD (algebraically zero) pooled:")
    for n in out["per_family"]["POOLED"]["dead_features"]:
        print(f"    {n}")
    print("\nFS5 coverage, TEST vs TRAINING range:")
    for c, d in cov.items():
        print(f"  {c:22s} cells outside on >=1 feature: {d['frac_cells_any_feature_outside']*100:6.2f}% "
              f" features ever outside: {d['features_with_any_outside']:3d}/{nF}")

    cb = out["coverage"]["q1_wallRe_unclipped_companion"]
    t = cb["training_unclipped"]
    print(f"\nFS5 PHYSICAL-ENVELOPE coverage, unclipped q1 companion "
          f"({DIAG_COMPANION}); the model input q1_wallRe stays clipped at 2.0 "
          f"and in-range by construction.")
    print(f"  planted control: {cb['planted_control']['verdict']} "
          f"(flagged {cb['planted_control']['flagged_before']} -> "
          f"{cb['planted_control']['flagged_after']} on a planted "
          f"{cb['planted_control']['planted_value']:.4g})")
    print(f"  training unclipped: min {t['min']:.4g}  p50 {t['p50']:.4g}  "
          f"p99 {t['p99']:.4g}  max {t['max']:.4g}")
    for c in sorted(cb["per_test_case"]):
        d = cb["per_test_case"][c]
        print(f"  {c:22s} above training max: {d['frac_cells_above_training_max']*100:6.2f}% "
              f"({d['n_cells_above_training_max']:6d} cells)  worst excursion "
              f"{d['worst_excursion_training_spans']:+8.4f} training spans  "
              f"case max {d['max']:.4g}")


if __name__ == "__main__":
    main()
