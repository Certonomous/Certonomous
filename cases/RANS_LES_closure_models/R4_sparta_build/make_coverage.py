#!/usr/bin/env python3
"""COVERAGE.md - the FS2/FS5 coverage document registered at
PREREGISTRATION.md sec. 7, DELIVERED LATE on 2026-08-23 (RESULTS.md
departure D-14).

Computes, on the REALISED 12-case training set and the FROZEN fields the
SpaRTA regression actually fitted:

  1. each selected feature's range on each training family, against the others
     (leave-one-family-out, the same fold structure the fit used);
  2. the pooled training range;
  3. the per-cell rank of the SELECTED tensor set {T1, T2, T3} per family,
     which is the reference a future test-family rank is compared against.

NOTHING IS FITTED. NO TEST OR VALIDATION CASE IS OPENED - the loop runs over
the twelve directories that exist under /home/ubuntu/closure-data/r4/dataset/,
all of them benchmark TRAINING cases, and the zero-shot guard below refuses any
other name. No test number is computed here; sec. 7 forbids it until the
scoring call.

Reads only.  Writes COVERAGE.md and artefacts/coverage.json beside MODEL.md.
"""
from __future__ import annotations
import json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from r4_lib import assert_no_test_case          # zero-shot boundary, in code

DS = "/home/ubuntu/closure-data/r4/dataset"
OUT_MD = os.path.join(HERE, "COVERAGE.md")
OUT_JSON = os.path.join(HERE, "artefacts", "coverage.json")

# MODEL.md sec. "The frozen model": the selected term sets.
#   R      = 2k [ c1 + c2 I1 + c3 I2 + c4 I2^2 ] T1
#   b^Delta =    c5 T2 + c6 I2 T2 + c7 T3
# Selected SCALAR features: I1, I2 (and the derived multiplier I2^2).
# Selected TENSORS: T1, T2, T3.  T4 is NOT selected and is not covered here.
CT_INDEX = {"T1": 0, "T2": 6, "T3": 12}          # names[j*6] per assemble_dataset
FAM_ORDER = ["hills", "ducts", "PHLL10595", "CBFS13700"]
RANK_RTOL = 1e-10        # same convention as assemble_dataset.py's {T1..T4} rank


def fit_mask(z):
    """The EXACT mask fs3_select.py fitted on (its lines 89-90)."""
    kraw, kDef, CR, bDel, CT = (z["k_les_raw"], z["kDef"], z["CR"],
                                z["bDel"], z["CT"])
    return ((kraw > 0) & np.isfinite(kDef) & np.isfinite(CR).all(axis=0)
            & np.isfinite(bDel).all(axis=(1, 2))
            & np.isfinite(CT).all(axis=(0, 2, 3)))


def stats(v):
    return dict(n=int(v.size), min=float(v.min()), p01=float(np.percentile(v, 1)),
                p50=float(np.median(v)), p99=float(np.percentile(v, 99)),
                max=float(v.max()))


def guard_is_armed():
    """Plant a control on the zero-shot guard before trusting its silence.
    `assert_no_test_case` takes an ITERABLE; handing it a bare string would
    intersect character-by-character and pass on everything, so the call sites
    below pass lists and this check proves the guard can still say no."""
    try:
        assert_no_test_case(["NASA_2DWMH"])
    except AssertionError:
        return True
    raise SystemExit("REFUSING: the zero-shot guard did not fire on a known "
                     "TEST case; its silence on the training set means nothing.")


def load():
    man = json.load(open(os.path.join(DS, "dataset_manifest.json")))
    guard_is_armed()
    assert_no_test_case(list(man["cases"]))       # the whole set, once
    per_case, fam_of = {}, {}
    for case, meta in sorted(man["cases"].items()):
        assert_no_test_case([case])               # refuses TEST and validation
        z = np.load(os.path.join(DS, f"{case}.npz"))
        ok = fit_mask(z)
        I1, I2 = z["I1"][ok], z["I2"][ok]
        CT = z["CT"]
        cols = {"I1": I1, "I2": I2, "I2^2": I2 ** 2}
        Ts = {}
        for nm, j in CT_INDEX.items():
            T = CT[j][ok]                                     # (n,3,3)
            cols["||%s||_F" % nm] = np.sqrt((T ** 2).sum(axis=(1, 2)))
            Ts[nm] = T.reshape(-1, 9)
        M = np.stack([Ts["T1"], Ts["T2"], Ts["T3"]], axis=1)  # (n,3,9)
        sv = np.linalg.svd(M, compute_uv=False)
        rank = (sv > sv[:, :1] * RANK_RTOL).sum(axis=1)
        # Rank alone answers "independent?", never "how nearly dependent?".
        # sigma_1/sigma_3 is the quantity that sees a set going soft.
        cond = sv[:, 0] / np.maximum(sv[:, 2], 1e-300)
        per_case[case] = dict(cols=cols, rank=rank, cond=cond,
                              n_cells=int(ok.size), n_used=int(ok.sum()),
                              n_dropped=int((~ok).sum()))
        fam_of[case] = meta["family"]
    return man, per_case, fam_of


def main():
    man, per_case, fam_of = load()
    names = ["I1", "I2", "I2^2", "||T1||_F", "||T2||_F", "||T3||_F"]
    fams = {f: [c for c in per_case if fam_of[c] == f] for f in FAM_ORDER}

    cat = lambda cs, k: np.concatenate([per_case[c]["cols"][k] for c in cs])
    catr = lambda cs: np.concatenate([per_case[c]["rank"] for c in cs])
    catk = lambda cs: np.concatenate([per_case[c]["cond"] for c in cs])

    out = {"generated": "2026-08-23", "training_cases": sorted(per_case),
           "n_cases": len(per_case),
           "n_cells_total": int(sum(p["n_cells"] for p in per_case.values())),
           "n_cells_fitted": int(sum(p["n_used"] for p in per_case.values())),
           "n_cells_dropped": int(sum(p["n_dropped"] for p in per_case.values())),
           "rank_rtol": RANK_RTOL, "per_family": {}, "pooled": {},
           "lofo": {}, "rank_per_family": {}, "per_case": {}}

    allc = sorted(per_case)
    for k in names:
        out["pooled"][k] = stats(cat(allc, k))
    for f, cs in fams.items():
        out["per_family"][f] = {k: stats(cat(cs, k)) for k in names}
        r, kc = catr(cs), catk(cs)
        out["rank_per_family"][f] = dict(
            mean=float(r.mean()), min=int(r.min()), max=int(r.max()),
            hist=[int((r == i).sum()) for i in range(4)], n=int(r.size),
            cond_p50=float(np.median(kc)), cond_p99=float(np.percentile(kc, 99)),
            cond_max=float(kc.max()))
    r, kc = catr(allc), catk(allc)
    out["rank_pooled"] = dict(mean=float(r.mean()), min=int(r.min()),
                              max=int(r.max()),
                              hist=[int((r == i).sum()) for i in range(4)],
                              n=int(r.size),
                              cond_p50=float(np.median(kc)),
                              cond_p99=float(np.percentile(kc, 99)),
                              cond_max=float(kc.max()))

    # Leave-one-family-out coverage: each family's cells against the range set
    # by the other three.  Same fold structure as the fit's cross-family CV.
    for f, cs in fams.items():
        others = [c for c in allc if fam_of[c] != f]
        row = {}
        for k in names:
            ref, hel = cat(others, k), cat(cs, k)
            lo, hi = ref.min(), ref.max()
            span = hi - lo
            below, above = hel < lo, hel > hi
            outside = below | above
            exc = np.zeros_like(hel)
            exc[below] = (lo - hel[below]) / max(span, 1e-300)
            exc[above] = (hel[above] - hi) / max(span, 1e-300)
            row[k] = dict(ref_min=float(lo), ref_max=float(hi),
                          held_min=float(hel.min()), held_max=float(hel.max()),
                          frac_outside=float(outside.mean()),
                          frac_below=float(below.mean()),
                          frac_above=float(above.mean()),
                          worst_excursion_spans=float(exc.max()))
        anyout = np.zeros(len(cat(cs, names[0])), dtype=bool)
        for k in names:
            ref = cat(others, k)
            hel = cat(cs, k)
            anyout |= (hel < ref.min()) | (hel > ref.max())
        row["_any_feature"] = dict(frac_cells_outside=float(anyout.mean()),
                                   n_cells=int(anyout.size))
        out["lofo"][f] = row

    for c in allc:
        p = per_case[c]
        out["per_case"][c] = dict(family=fam_of[c], n_cells=p["n_cells"],
                                  n_fitted=p["n_used"], n_dropped=p["n_dropped"],
                                  rank_mean=float(p["rank"].mean()),
                                  rank_min=int(p["rank"].min()),
                                  rank_max=int(p["rank"].max()),
                                  cond_p50=float(np.median(p["cond"])),
                                  cond_p99=float(np.percentile(p["cond"], 99)),
                                  cond_max=float(p["cond"].max()))

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    json.dump(out, open(OUT_JSON, "w"), indent=1, sort_keys=True)
    print(json.dumps({k: out[k] for k in
                      ("n_cases", "n_cells_fitted", "n_cells_dropped")}, indent=1))
    print("pooled:", json.dumps(out["pooled"], indent=1))
    print("rank_pooled:", json.dumps(out["rank_pooled"]))
    for f in FAM_ORDER:
        print(f, "rank", json.dumps(out["rank_per_family"][f]))
        print(f, "lofo any-feature", json.dumps(out["lofo"][f]["_any_feature"]))
    print("WROTE", OUT_JSON)


if __name__ == "__main__":
    main()
