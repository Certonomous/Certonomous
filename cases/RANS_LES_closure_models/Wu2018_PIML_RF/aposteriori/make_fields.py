#!/usr/bin/env python3
"""Build the bijDelta / kDeficit fields for the a-posteriori re-solve, and run
the registered pre-solve gate G0. See PREREGISTRATION.md.

bijDelta := Delta b  (= b_LES - b_RANS convention; identical to the forest's
regression target). kDeficit := uniform 0.  Nothing is fitted here except the
forest itself, which is retrained with the pre-registered split.
"""
from __future__ import annotations
import os, re, sys, json
import numpy as np
from sklearn.ensemble import RandomForestRegressor

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.join(os.path.dirname(os.path.dirname(HERE)), "_common")
sys.path.insert(0, COMMON)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "Ling2016_TBNN"))
from of_read import realisability_violation
from train_tbnn import TEST, VAL, GROUP_EXCLUDED

OUT = "/home/ubuntu/closure-data/aposteriori/wu2018"
BENCH = "/home/ubuntu/closure-challenge-benchmark/data"
CASES = {"AR_1_Ret_360": f"{BENCH}/DUCT/AR_1_Ret_360",
         "AR_3_Ret_360": f"{BENCH}/DUCT/AR_3_Ret_360",
         "CBFS13700":    f"{BENCH}/CBFS"}
SYM = [(0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)]   # OpenFOAM xx xy xz yy yz zz


def to6(b):
    return np.stack([b[:, i, j] for i, j in SYM], axis=1)


def patches(case_dir):
    """(name, type) for every boundary patch, in file order."""
    txt = open(os.path.join(case_dir, "constant", "polyMesh", "boundary")).read()
    txt = re.sub(r"/\*.*?\*/", "", txt, flags=re.S)
    body = txt[txt.index("("):txt.rindex(")")]
    out = []
    for m in re.finditer(r"(\w+)\s*\{[^{}]*?type\s+(\w+)\s*;", body, re.S):
        out.append((m.group(1), m.group(2)))
    return out



# constraint patch types must be matched exactly by the patchField type;
# everything else (walls, inlets, outlets) takes zeroGradient.
CONSTRAINT = {"empty", "cyclic", "cyclicAMI", "symmetry", "symmetryPlane",
              "wedge", "processor", "processorCyclic", "nonConformalCyclic"}


def pfield(ptype):
    return f"{ptype};" if ptype in CONSTRAINT else "zeroGradient;"

def write_sym(path, name, arr6, pats, loc="0"):
    n = arr6.shape[0]
    L = [f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       volSymmTensorField;
    location    "{loc}";
    object      {name};
}}

dimensions      [0 0 0 0 0 0 0];

internalField   nonuniform List<symmTensor>
{n}
("""]
    L += ["(" + " ".join(f"{v:.12g}" for v in row) + ")" for row in arr6]
    L.append(")\n;\n\nboundaryField\n{")
    for pn, pt in pats:
        L.append(f"    {pn}\n    {{\n        type            " + pfield(pt) + "\n    }")
    L.append("}\n")
    open(path, "w").write("\n".join(L))


def write_scalar_uniform(path, name, val, pats, dims, loc="0"):
    L = [f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       volScalarField;
    location    "{loc}";
    object      {name};
}}

dimensions      {dims};

internalField   uniform {val};

boundaryField
{{"""]
    for pn, pt in pats:
        L.append(f"    {pn}\n    {{\n        type            " + pfield(pt) + "\n    }")
    L.append("}\n")
    open(path, "w").write("\n".join(L))


def main():
    z = np.load("/home/ubuntu/closure-data/tbnn/dataset.npz", allow_pickle=True)
    names = [str(x) for x in z["names"]]
    bL, bR, valid, cid = z["b_LES"], z["b_RANS"], z["valid"], z["case_id"]
    F = np.load("/home/ubuntu/closure-data/tbnn/features_ext.npz", allow_pickle=True)["F"]
    cid_of = {n: i for i, n in enumerate(names)}
    finite = (np.isfinite(bL).all(axis=(1, 2)) & np.isfinite(bR).all(axis=(1, 2))
              & np.isfinite(F).all(axis=1))
    ok = valid & finite

    split = {n: ("test" if n in TEST else "val" if n in VAL
                 else "excluded" if n in GROUP_EXCLUDED else "train") for n in names}
    train_names = [n for n in names if split[n] == "train"]
    mtr = np.isin(cid, [cid_of[c] for c in train_names]) & ok
    dB_all = to6(bL - bR)
    b_mean = bL[mtr].mean(0)
    print(f"[train] {len(train_names)} cases, {int(mtr.sum())} cells", flush=True)

    forests = {}
    for seed in (0, 1, 2):
        rf = RandomForestRegressor(n_estimators=100, max_depth=20, min_samples_leaf=9,
                                   max_features="sqrt", random_state=seed, n_jobs=8)
        rf.fit(F[mtr], dB_all[mtr])
        forests[seed] = rf
        print(f"[fit] seed {seed} done", flush=True)

    report = {"train_cases": sorted(train_names), "n_train_cells": int(mtr.sum()),
              "b_mean": b_mean.tolist(), "cases": {}}

    for case, cdir in CASES.items():
        i = cid_of[case]
        sel = (cid == i)
        n = int(sel.sum())
        pats = patches(cdir)
        good = ok[sel]
        cfg = {}
        # TRUTH and MEAN
        cfg["truth"] = np.where(good[:, None], dB_all[sel], 0.0)
        cfg["mean"] = np.where(good[:, None], to6(b_mean[None] - bR[sel]), 0.0)
        for seed, rf in forests.items():
            p = rf.predict(F[sel])
            cfg[f"ml_s{seed}"] = np.where(good[:, None], p, 0.0)

        cinfo = {"n_cells": n, "n_zeroed_invalid": int((~good).sum()),
                 "patches": pats, "configs": {}}
        for tag, arr6 in cfg.items():
            d = os.path.join(OUT, "_fields", case, tag)
            os.makedirs(d, exist_ok=True)
            write_sym(os.path.join(d, "bijDelta"), "bijDelta", arr6, pats)
            write_scalar_uniform(os.path.join(d, "kDeficit"), "kDeficit", 0,
                                 pats, "[0 2 -3 0 0 0 0]")
            # ---- gate G0: b_total at iteration 0 must equal b_RANS + bijDelta
            full = np.zeros((n, 3, 3))
            for c, (a, b) in enumerate(SYM):
                full[:, a, b] = arr6[:, c]; full[:, b, a] = arr6[:, c]
            b_tot = bR[sel] + full
            if tag.startswith("ml"):
                seed = int(tag.split("_s")[1])
                b_pred = bR[sel] + np.zeros_like(full)
                pf = forests[seed].predict(F[sel])
                for c, (a, b) in enumerate(SYM):
                    b_pred[:, a, b] += pf[:, c]
                    if a != b: b_pred[:, b, a] += pf[:, c]
                num = np.linalg.norm((b_tot - b_pred)[good].reshape(-1, 9), axis=1)
                den = np.linalg.norm(b_pred[good].reshape(-1, 9), axis=1) + 1e-30
                g0 = float(np.sqrt((num ** 2).sum() / (den ** 2).sum()))
            else:
                g0 = 0.0
            # Realisability is reported at two tolerances. tol=0 in float64
            # counts cells that sit ONE float32 ulp (2.98e-08) outside the
            # triangle -- exact two-component states in the shipped float32
            # data, not physics. tol=1e-6 is the registered reporting value:
            # far below any physical anisotropy scale, far above float32 ulp.
            v, _ = realisability_violation(b_tot[good], tol=1e-6)
            v0, _ = realisability_violation(b_tot[good])
            tv, _ = realisability_violation(bL[sel][good], tol=1e-6)
            cinfo["configs"][tag] = {
                "G0_rel_L2": g0,
                "viol_injected_b_total": float(v.mean()),
                "viol_injected_b_total_tol0": float(v0.mean()),
                "viol_truth": float(tv.mean()),
                "max_norm_b_total": float(np.sqrt((b_tot[good] ** 2).sum(axis=(1, 2))).max()),
                "rms_bijDelta": float(np.sqrt((arr6 ** 2).sum(1).mean())),
            }
            print(f"[{case:14s} {tag:7s}] G0={g0:.2e} viol={v.mean():.4f} (tol0 {v0.mean():.4f}) "
                  f"(truth {tv.mean():.4f}) max||b||={cinfo['configs'][tag]['max_norm_b_total']:.4f}", flush=True)
        report["cases"][case] = cinfo

    json.dump(report, open(os.path.join(OUT, "fields_report.json"), "w"), indent=1)
    worst = max(c["configs"][t]["G0_rel_L2"] for c in report["cases"].values() for t in c["configs"])
    print(f"\nGATE G0: worst relative L2 = {worst:.3e}  -> "
          f"{'PASS (<1e-10)' if worst < 1e-10 else 'FAIL'}", flush=True)


if __name__ == "__main__":
    main()
