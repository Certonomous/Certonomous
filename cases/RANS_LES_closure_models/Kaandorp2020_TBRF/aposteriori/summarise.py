#!/usr/bin/env python3
"""Render the lane table from results.json plus the extra diagnostics the
cross-lane comparison needs: transported k vs shipped k vs k_LES, the b_rms of
the injected field, secondary-flow magnitude, and the convergence STATE of every
row (CONVERGED / STAGNATED-NOT-CONVERGED / CAPPED / DIVERGED)."""
from __future__ import annotations
import os, sys, json, re
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COMMON = "/home/ubuntu/Certonomous/cases/RANS_LES_closure_models/_common"
sys.path.insert(0, HERE); sys.path.insert(0, COMMON)
from of_read import read_field, latest_time_dir
import sst_baseline_metrics as SB
from setup_case import CASES
import run_lane as RL

ROOT = "/home/ubuntu/closure-data/aposteriori/kaandorp"
GATE = RL.GATE


def state(case, t0):
    """Convergence state from the log plus field movement between checkpoints."""
    lg = os.path.join(case, "log.run")
    if not os.path.exists(lg):
        return "NO-LOG", None, None
    txt = open(lg, errors="replace").read()
    conv = "SIMPLE solution converged" in txt
    # NB: the log header always contains "trapFpe: Floating point exception
    # trapping enabled", so that string must NOT be used as a divergence test.
    crashed = ("FOAM FATAL" in txt) or ("Foam::sigFpe" in txt) or ("End" not in txt[-400:])
    ts = sorted([x for x in os.listdir(case)
                 if os.path.isdir(os.path.join(case, x))
                 and os.path.exists(os.path.join(case, x, "U"))
                 and _f(x) is not None and _f(x) > float(t0)], key=float)
    if crashed and not ts:
        return "DIVERGED", None, None
    move = None
    if len(ts) >= 2:
        a = read_field(os.path.join(case, ts[-2], "U"))
        b = read_field(os.path.join(case, ts[-1], "U"))
        ub = float(np.abs(a).max())
        move = float(np.abs(b - a).max() / ub)
    if crashed:
        return "DIVERGED", move, (ts[-1] if ts else None)
    if conv:
        return "CONVERGED-residualControl", move, (ts[-1] if ts else None)
    if move is not None and move < 1e-6:
        return "CONVERGED-stagnation", move, ts[-1]
    return "CAPPED-NOT-CONVERGED", move, (ts[-1] if ts else None)


def _f(x):
    try:
        return float(x)
    except ValueError:
        return None


def main():
    r = json.load(open(os.path.join(ROOT, "results.json")))
    rows = []
    for key, v in r["runs"].items():
        tag, lab = key.split("__")
        src, fam = CASES[tag]
        d = SB.load_case(tag, src, fam)
        t0 = latest_time_dir(src)
        st, move, tw = state(v["case"], t0)
        k_new = None
        if tw and os.path.exists(os.path.join(v["case"], tw, "k")):
            k_new = float(read_field(os.path.join(v["case"], tw, "k")).mean())
        rows.append(dict(case=tag, cfg=lab, state=st, move=move, t_written=tw,
                         iters=v.get("iterations"), wall_s=v.get("wall_s"),
                         U_rms=v.get("U_rms"), U_mae=v.get("U_mae"),
                         k_mean=k_new, k_mean_SST=float(d["k"].mean()),
                         k_mean_LES=float(d["k_LES"].mean()),
                         b_rms_total=v.get("b_rms_total"),
                         unreal=v.get("unrealisable_frac"),
                         divU=v.get("divU_rms_over_gradscale"),
                         inplane=v.get("inplane_pct_bulk"),
                         inplane_LES=v.get("inplane_pct_bulk_LES"),
                         x_reatt=v.get("x_reatt"),
                         res_p=v.get("res_p_final"), res_Ux=v.get("res_Ux_final")))
    for extra in ("frozen_R_AR_1_Ret_360.json", "frozen_R_CBFS13700.json"):
        p = os.path.join(ROOT, extra)
        if not os.path.exists(p):
            continue
        f = json.load(open(p))
        if "propagate" not in f:
            continue
        tag = extra.replace("frozen_R_", "").replace(".json", "")
        src, fam = CASES[tag]
        d = SB.load_case(tag, src, fam)
        t0 = latest_time_dir(src)
        v = f["propagate"]
        st, move, tw = state(v["case"], t0)
        rows.append(dict(case=tag, cfg="TRUTH+R (POST-HOC)", state=st, move=move,
                         t_written=tw, iters=v.get("iterations"),
                         wall_s=v.get("wall_s"), U_rms=v.get("U_rms"),
                         U_mae=v.get("U_mae"),
                         k_mean=float(read_field(os.path.join(v["case"], tw, "k")).mean())
                         if tw else None,
                         k_mean_SST=float(d["k"].mean()),
                         k_mean_LES=float(d["k_LES"].mean()),
                         b_rms_total=v.get("b_rms_total"),
                         unreal=v.get("unrealisable_frac"),
                         divU=v.get("divU_rms_over_gradscale"),
                         inplane=v.get("inplane_pct_bulk"),
                         inplane_LES=v.get("inplane_pct_bulk_LES"),
                         x_reatt=v.get("x_reatt"),
                         res_p=v.get("res_p_final"), res_Ux=v.get("res_Ux_final")))
    json.dump(rows, open(os.path.join(ROOT, "table.json"), "w"), indent=1)
    hdr = (f"{'case':14s} {'cfg':18s} {'state':26s} {'it':>6s} {'wall_s':>8s} "
           f"{'U_rms':>9s} {'U_mae':>9s} {'k_mean':>9s} {'b_rms':>8s} "
           f"{'unreal':>7s} {'divU':>10s} {'2ndry%':>8s} {'x_reatt':>8s}")
    print(hdr); print("-" * len(hdr))
    for x in sorted(rows, key=lambda z: (z["case"], z["cfg"])):
        f = lambda v, w, p: (f"{v:{w}.{p}f}" if isinstance(v, float) else f"{'--':>{w}}")
        print(f"{x['case']:14s} {x['cfg']:18s} {x['state']:26s} "
              f"{(x['iters'] if x['iters'] is not None else -1):6d} "
              f"{(x['wall_s'] if x['wall_s'] is not None else -1):8.1f} "
              f"{f(x['U_rms'],9,5)} {f(x['U_mae'],9,5)} {f(x['k_mean'],9,3)} "
              f"{f(x['b_rms_total'],8,4)} {f(x['unreal'],7,4)} "
              f"{(x['divU'] if x['divU'] is not None else float('nan')):10.2e} "
              f"{f(x['inplane'],8,4)} {f(x['x_reatt'],8,3)}")
    print("\ngates:", json.dumps(GATE))
    for tag in sorted({x['case'] for x in rows}):
        z = [x for x in rows if x['case'] == tag][0]
        print(f"{tag}: k_SST={z['k_mean_SST']:.3f} k_LES={z['k_mean_LES']:.3f} "
              f"2ndry_LES={z['inplane_LES']}")


if __name__ == "__main__":
    main()
