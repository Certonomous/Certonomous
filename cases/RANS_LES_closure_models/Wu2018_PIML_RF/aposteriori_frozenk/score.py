#!/usr/bin/env python3
"""Score the a-posteriori solves against BASELINES.md sec. 1 metrics."""
from __future__ import annotations
import os, re, sys, json, glob
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = os.path.join(os.path.dirname(os.path.dirname(HERE)), "_common")
sys.path.insert(0, COMMON)
import sst_baseline_metrics as SB
from of_read import (read_field, read_field_expand, sym_to_full, anisotropy, realisability_violation,
                     plane_axes, structured_gradient)

OUT = "/home/ubuntu/closure-data/aposteriori_frozenk/wu2018"
BENCH = "/home/ubuntu/closure-challenge-benchmark/data"
SRC = {"AR_1_Ret_360": f"{BENCH}/DUCT/AR_1_Ret_360",
       "AR_3_Ret_360": f"{BENCH}/DUCT/AR_3_Ret_360",
       "CBFS13700": f"{BENCH}/CBFS"}
CFGS = ["S_null","S_truth","S_mean","S_ml_s0","S_ml_s1","S_ml_s2","L_null","L_truth","L_mean","L_ml_s0","L_ml_s1","L_ml_s2"]


def last_time(d):
    ts = [x for x in os.listdir(d) if re.fullmatch(r"\d+", x) and x != "0"]
    return max(ts, key=int) if ts else None


def log_facts(log):
    """final initial-residuals, continuity error, iteration count, converged?"""
    if not os.path.exists(log):
        return {}
    t = open(log).read()
    it = len(re.findall(r"^Time = ", t, re.M))
    cont = re.findall(r"time step continuity errors : sum local = ([\d.eE+-]+), "
                      r"global = ([\d.eE+-]+), cumulative = ([\d.eE+-]+)", t)
    res = {}
    for f in ("Ux", "Uy", "Uz", "p", "k", "omega"):
        m = re.findall(rf"Solving for {f}, Initial residual = ([\d.eE+-]+)", t)
        if m:
            res[f] = float(m[-1])
    return {"iterations": it,
            "converged": "SIMPLE solution converged" in t,
            "final_residuals": res,
            "max_final_residual": max(res.values()) if res else None,
            "continuity_sum_local": float(cont[-1][0]) if cont else None,
            "continuity_cumulative": float(cont[-1][2]) if cont else None}


BASE_JSON = os.path.join(COMMON, "sst_baseline_metrics.json")


def main():
    base = json.load(open(BASE_JSON))
    out = {}
    for case, sdir in SRC.items():
        truth_dir = os.path.join(sdir, "0")
        U_LES = read_field(os.path.join(truth_dir, "U_LES"))
        k_LES = read_field(os.path.join(truth_dir, "k_LES"))
        tau_LES = sym_to_full(read_field(os.path.join(truth_dir, "tauij_LES")))
        bL, validL = anisotropy(tau_LES, k_LES)
        _db = SB.load_case(case, sdir, "duct" if case.startswith("AR_") else "cbfs")
        bR_base = np.nan_to_num(anisotropy(sym_to_full(_db["tau_R"]), _db["k"], k_ref=k_LES)[0])
        Uref = np.linalg.norm(U_LES, axis=1).mean()
        lastt = max([x for x in os.listdir(sdir) if re.fullmatch(r"\d+", x) and x != "0"], key=int)
        k_base = read_field(os.path.join(sdir, lastt, "k"))
        C = read_field(os.path.join(sdir, "constant", "C")) if os.path.exists(
            os.path.join(sdir, "constant", "C")) else read_field(os.path.join(truth_dir, "C"))
        keep, thin = plane_axes(C)
        is_duct = case.startswith("AR_")
        Ubulk = np.abs(U_LES[:, thin]).mean()
        sec_LES = np.linalg.norm(U_LES[:, keep], axis=1).mean()
        out[case] = {"n_cells": len(U_LES), "U_ref_mean_LES": float(Uref),
                     "BASE_U_rms_shipped": base[case]["U_rms_err_rel"],
                     "BASE_U_mae_shipped": base[case]["U_mae_rel"],
                     "U_bulk_LES": float(Ubulk),
                     "is_duct": bool(is_duct),
                     "sec_mean_LES_pct": float(100 * sec_LES / Ubulk) if is_duct else None,
                     "truth_viol": float(realisability_violation(bL[validL], tol=1e-6)[0].mean()),
                     "configs": {}}
        for cfg in CFGS:
            d = os.path.join(OUT, case, cfg)
            lf = log_facts(os.path.join(d, "log.solve"))
            t = last_time(d) if os.path.isdir(d) else None
            rec = dict(lf)
            done = os.path.join(d, "log.solve.done")
            if os.path.exists(done):
                m = re.search(r"rc=(\S+) seconds=(\d+)", open(done).read())
                rec["rc"], rec["wall_s"] = int(m.group(1)), int(m.group(2))
            if t is None:
                rec["status"] = "NO OUTPUT TIME DIR"
                out[case]["configs"][cfg] = rec
                continue
            U = read_field(os.path.join(d, t, "U"))
            k = read_field(os.path.join(d, t, "k"))
            nut = read_field(os.path.join(d, t, "nut"))
            e = U - U_LES
            rec["time_dir"] = t
            rec["U_rms"] = float(np.sqrt((e ** 2).sum(1).mean()) / Uref)
            rec["U_mae"] = float(np.abs(e).sum(1).mean() / Uref)
            if is_duct:
                rec["sec_mean_pct"] = float(100 * np.linalg.norm(U[:, keep], axis=1).mean() / Ubulk)
                rec["sec_recovered_frac"] = rec["sec_mean_pct"] / out[case]["sec_mean_LES_pct"]
            # transported-k drift: b^Delta is frozen but k is NOT, and the
            # realised stress is tau = 2k(b_lin + b^Delta), so a k that moves
            # away from baseline corrupts tau even with a perfect b^Delta.
            rec["k_mean"] = float(k.mean())
            rec["k_over_k_baseline"] = float(k.mean() / k_base.mean())
            rec["k_over_k_LES"] = float(k.mean() / k_LES.mean())
            # Converged anisotropy, computed directly. tauijRecon is NOT written
            # by kOmegaSSTCorrectedFrozenK: that field is assembled inside
            # kOmegaSSTCorrected::correct(), which the frozen model deliberately
            # does not call. Momentum is unaffected (divDevReff uses bijDelta_ and
            # k_ directly), but the diagnostic output is absent, so b_total is
            # reconstructed from the written fields as
            #     b_total = -(nu_t/k) S + bijDelta.
            # Departure D-2 in RESULTS.md.
            Agrad = structured_gradient(C, U)
            Ssym = 0.5 * (Agrad + Agrad.transpose(0, 2, 1))
            bD = sym_to_full(read_field_expand(os.path.join(d, "0", "bijDelta"), len(U)))
            b_tot = -(nut / np.maximum(k, 1e-30))[:, None, None] * Ssym + bD
            fin = np.isfinite(b_tot).all(axis=(1, 2)) & validL
            v, _ = realisability_violation(b_tot[fin], tol=1e-6)
            rec["viol_converged_b"] = float(v.mean())
            rec["b_rms_vs_LES"] = float(np.sqrt(
                ((b_tot[fin] - bL[fin]) ** 2).sum(axis=(1, 2)).mean()))
            rec["b_rms_injected_vs_LES"] = float(np.sqrt(
                (((bR_base + bD)[fin] - bL[fin]) ** 2).sum(axis=(1, 2)).mean()))
            out[case]["configs"][cfg] = rec
    # NULL state, the NULL-BASE gap, and the dual H1 reading
    REG = 1e-6      # registered convergence threshold on every initial residual
    for case, c in out.items():
        nc = c["configs"].get("S_null", {})
        nu = nc.get("U_rms")
        mx = nc.get("max_final_residual")
        conv = bool(nc.get("converged")) and mx is not None and mx < REG
        c["NULL_state"] = "CONVERGED" if conv else "STAGNATED-NOT-CONVERGED"
        c["NULL_iterations"] = nc.get("iterations")
        c["NULL_final_residuals"] = nc.get("final_residuals")
        if nu is not None:
            c["NULL_minus_BASE_U_rms"] = nu - c["BASE_U_rms_shipped"]
        # H1 against BOTH comparators, per case, for every ML seed
        ml = [c["configs"][k]["U_rms"] for k in ("S_ml_s0", "S_ml_s1", "S_ml_s2")
              if "U_rms" in c["configs"].get(k, {})]
        if ml:
            spread = max(ml) - min(ml)
            c["ML_mean_U_rms"] = float(np.mean(ml))
            c["ML_seed_spread"] = float(spread)
            if nu is not None:
                c["H1_vs_NULL"] = bool(np.mean(ml) < nu - spread)
            c["H1_vs_BASE_shipped"] = bool(np.mean(ml) < c["BASE_U_rms_shipped"] - spread)
    json.dump(out, open(os.path.join(OUT, "scores.json"), "w"), indent=1)
    for case, c in out.items():
        sl = c.get("sec_mean_LES_pct")
        print(f"\n=== {case}  (n={c['n_cells']}" + (f", sec_LES={sl:.3f}% of bulk" if sl else "") + ")")
        print(f"    BASE (shipped SST, BASELINES.md): U_rms={c['BASE_U_rms_shipped']:.4f} "
              f"U_mae={c['BASE_U_mae_shipped']:.4f}"
              + (f"   |   NULL-BASE = {c['NULL_minus_BASE_U_rms']:+.4f} (benchmark convergence gap, N-B23)"
                 if "NULL_minus_BASE_U_rms" in c else ""))
        fr = c.get("NULL_final_residuals") or {}
        print(f"    NULL: {c.get('NULL_state')} at {c.get('NULL_iterations')} iters; "
              "residuals " + " ".join(f"{k}={v:.2e}" for k, v in fr.items()))
        if "H1_vs_NULL" in c or "H1_vs_BASE_shipped" in c:
            print(f"    H1 (ML mean {c.get('ML_mean_U_rms', float('nan')):.4f}, spread "
                  f"{c.get('ML_seed_spread', float('nan')):.4f}): vs NULL = {c.get('H1_vs_NULL')} ; "
                  f"vs shipped BASE = {c.get('H1_vs_BASE_shipped')}")
        print(f"{'cfg':7s} {'U_rms':>8s} {'U_mae':>8s} {'sec%':>8s} {'k/kb':>6s} {'b_rms':>7s} "
              f"{'viol':>7s} {'cont':>10s} {'maxRes':>9s} {'iters':>7s} {'s':>5s} conv")
        for cfg, r in c["configs"].items():
            if "U_rms" not in r:
                print(f"{cfg:7s} {r.get('status','?')}"); continue
            sec = f"{r['sec_mean_pct']:8.4f}" if 'sec_mean_pct' in r else "      --"
            print(f"{cfg:7s} {r['U_rms']:8.4f} {r['U_mae']:8.4f} {sec} "
                  f"{r.get('k_over_k_baseline', float('nan')):6.3f} "
                  f"{r.get('b_rms_vs_LES', float('nan')):7.4f} {r.get('viol_converged_b', float('nan')):7.4f} "
                  f"{r.get('continuity_sum_local', float('nan')):10.2e} "
                  f"{r.get('max_final_residual', float('nan')):9.2e} {r.get('iterations', -1):7d} "
                  f"{r.get('wall_s', -1):5d} {r.get('converged')}")


if __name__ == "__main__":
    main()
