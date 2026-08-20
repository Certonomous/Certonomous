#!/usr/bin/env python3
"""Post-hoc diagnostics on the trained forests. Fits nothing, tunes nothing.

The preregistered metric is b_rms_F, a second moment. This pass reports the whole
error distribution behind it, because a second moment cannot distinguish "the
model is uniformly bad" from "the model is good in the median cell and unbounded
in a few per cent of them", and those two failures have different causes and
different cures.

Also reported:
  * the size of the fitted tensor-basis coefficients g (rank-deficiency diagnostic);
  * median-over-trees vs mean-over-trees (Kaandorp sec. 2.5 p.21 claim that the
    median is what makes the TBRF robust);
  * the fraction of predictions violating the hard bound ||b||_F <= sqrt(2/3);
  * the same error with predictions rescaled onto that bound -- NOT a model we
    preregistered, reported only to locate the error.

Usage:  python analyse.py [--nodurbin]
"""
from __future__ import annotations
import os, sys, json, pickle
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/home/ubuntu/Certonomous/cases/RANS_LES_closure_models/_common")
import tbrf_faithful
from tbrf_faithful import b_from_g, IDX6


class _Compat(pickle.Unpickler):
    """Checkpoints written before this module was renamed reference module
    'tbrf'; that name now belongs to a DIFFERENT agent's implementation
    (see INCIDENT_tbrf_overwrite_2026-08-20.md). Remap on load, process-local."""

    def find_class(self, module, name):
        if module == "tbrf":
            module = "tbrf_faithful"
        return super().find_class(module, name)
from of_read import realisability_violation

DD = "/home/ubuntu/closure-data/kaandorp_tbrf"
TAG = "_nodurbin" if "--nodurbin" in sys.argv else ""
CK = os.path.join(DD, "ckpt" + TAG)
BMAX = np.sqrt(2.0 / 3.0)
# b_LES and T are stored as float32 in features.npz. On CBFS13700 4.60 % of the
# truth cells sit EXACTLY on an edge of the barycentric triangle in float64
# (min coordinate = 0.0); float32 round-trip pushes them to -2.98e-8 and a
# zero-tolerance test then calls them unrealisable. TOL is set above that noise
# floor and six orders below any physically meaningful violation.
TOL = 1e-7


def main():
    d = np.load(os.path.join(DD, f"features{TAG}.npz"), allow_pickle=False)
    X, T, bL = d["X"], d["T"], d["b_LES"]
    valid, cid = d["valid"], d["case_id"]
    names = [str(s) for s in d["names"]]
    res = json.load(open(os.path.join(DD, f"results{TAG}.json")))
    ev = res["meta"]["test_cases"] + res["meta"]["control_cases"]
    idx = {c: np.nonzero((cid == names.index(c)) & valid)[0] for c in ev}
    out = {}
    for mname, run in res["runs"].items():
        seeds = sorted(run["seeds"])
        acc = {c: [] for c in ev}
        gstat = []
        for sd in seeds:
            f = os.path.join(CK, f"{mname}_seed{sd}.pkl")
            if not os.path.exists(f):
                continue
            ck = _Compat(open(f, "rb")).load()
            trees, scale, cols = ck["trees"], ck["scale"], ck["cols"]
            gall = np.concatenate([t.gleaf for t in trees])
            gstat.append([float(np.median(np.abs(gall))),
                          float(np.percentile(np.abs(gall), 99)),
                          float(np.abs(gall).max())])
            for c in ev:
                m = idx[c]
                P = np.empty((len(trees), m.size, 3, 3))
                for i, t in enumerate(trees):
                    P[i] = b_from_g(t.predict_g(X[m][:, cols]), T[m], scale)
                bt = bL[m].astype(np.float64)
                med = np.empty_like(bt, dtype=np.float64)
                for a, b_ in IDX6:
                    v = np.median(P[:, :, a, b_], axis=0)
                    med[:, a, b_] = v; med[:, b_, a] = v
                mean = P.mean(axis=0)
                e = np.sqrt(((med - bt) ** 2).sum(axis=(1, 2)))
                em = np.sqrt(((mean - bt) ** 2).sum(axis=(1, 2)))
                nb = np.sqrt((med ** 2).sum(axis=(1, 2)))
                cl = med * np.minimum(1.0, BMAX / np.maximum(nb, 1e-30))[:, None, None]
                ec = np.sqrt(((cl - bt) ** 2).sum(axis=(1, 2)))
                vf0, _ = realisability_violation(med, tol=0.0)
                vf, _ = realisability_violation(med, tol=TOL)
                tv0, _ = realisability_violation(bt, tol=0.0)
                tv, _ = realisability_violation(bt, tol=TOL)
                acc[c].append(dict(
                    unreal_tol0=float(vf0.mean()), unreal_tol=float(vf.mean()),
                    truth_unreal_tol0=float(tv0.mean()), truth_unreal_tol=float(tv.mean()),
                    rms=float(np.sqrt((e ** 2).mean())),
                    p50=float(np.median(e)), p90=float(np.percentile(e, 90)),
                    p99=float(np.percentile(e, 99)), max=float(e.max()),
                    mean_agg_rms=float(np.sqrt((em ** 2).mean())),
                    frac_over_bound=float((nb > BMAX).mean()),
                    clipped_rms=float(np.sqrt((ec ** 2).mean())),
                    clipped_p50=float(np.median(ec))))
        if not gstat:
            continue
        g = np.array(gstat).mean(axis=0)
        e = {"g_abs_p50": g[0], "g_abs_p99": g[1], "g_abs_max": g[2], "cases": {}}
        for c in ev:
            if not acc[c]:
                continue
            ks = acc[c][0].keys()
            e["cases"][c] = {k: [float(np.mean([a[k] for a in acc[c]])),
                                 float(np.std([a[k] for a in acc[c]], ddof=1))
                                 if len(acc[c]) > 1 else 0.0] for k in ks}
        out[mname] = e
        print(f"\n{mname}  |g| p50={g[0]:.3g} p99={g[1]:.3g} max={g[2]:.3g}")
        for c, v in e["cases"].items():
            print(f"  {c:22s} RMS={v['rms'][0]:9.4f}  p50={v['p50'][0]:.4f} "
                  f"p90={v['p90'][0]:.4f} p99={v['p99'][0]:9.4f}  "
                  f"meanagg={v['mean_agg_rms'][0]:11.4f}  "
                  f"over-bound={v['frac_over_bound'][0]:.4f}  "
                  f"clippedRMS={v['clipped_rms'][0]:.4f}  "
                  f"unreal(tol)={v['unreal_tol'][0]:.4f}+-{v['unreal_tol'][1]:.4f} "
                  f"[tol0={v['unreal_tol0'][0]:.4f}; truth {v['truth_unreal_tol'][0]:.4f}"
                  f"/{v['truth_unreal_tol0'][0]:.4f}]", flush=True)
    json.dump(out, open(os.path.join(DD, f"diagnostics{TAG}.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
