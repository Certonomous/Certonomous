#!/usr/bin/env python3
"""Render the preregistered scoreboard from results.json. No fitting, no choices."""
import json, sys
import numpy as np

DD = "/home/ubuntu/closure-data/kaandorp_tbrf"
r = json.load(open(f"{DD}/results.json"))
GATE = {"AR_1_Ret_360": 0.5843, "AR_1_Ret_180": 0.6541, "CBFS13700": 0.3051,
        "alpha_15_13929_4048": 0.2885, "alpha_15_13929_2024": 0.2989,
        "alpha_05_4071_4048": 0.3498, "alpha_05_4071_2024": 0.3202}
TRUTH_UNREAL = {"AR_1_Ret_360": 0.0159, "AR_1_Ret_180": 0.0000, "CBFS13700": 0.0000,
                "alpha_15_13929_4048": 0.0128, "alpha_15_13929_2024": 0.0230,
                "alpha_05_4071_4048": 0.0141, "alpha_05_4071_2024": 0.0246}
cases = r["meta"]["test_cases"] + r["meta"]["control_cases"]


def agg(m, c, key):
    v = [s["per_case"][c][key] for s in r["runs"][m]["seeds"].values()]
    return float(np.mean(v)), float(np.std(v, ddof=1)) if len(v) > 1 else 0.0, len(v)


print("== b_rms_F, mean +/- std over seeds ==")
hdr = f"{'model':30s}" + "".join(f"{c[:18]:>20s}" for c in cases)
print(hdr)
for m in r["runs"]:
    row = f"{m:30s}"
    for c in cases:
        mu, sd, n = agg(m, c, "b_rms_F")
        row += f"{mu:12.4f}+-{sd:6.4f}"
    print(row)
print(f"{'SST (BASELINES.md)':30s}" + "".join(f"{GATE[c]:20.4f}" for c in cases))
for k, lab in (("B0_sst", "SST recomputed here"), ("B1_meanb", "B1 mean-b"),
               ("B2_zero", "B2 b=0"), ("tensor_basis_ceiling", "basis ceiling"),
               ("truth_norm", "||b_LES|| rms")):
    print(f"{lab:30s}" + "".join(f"{r['baselines'][c][k]:20.4f}" for c in cases))

print("\n== unrealisable fraction ==")
for m in r["runs"]:
    row = f"{m:30s}"
    for c in cases:
        mu, sd, n = agg(m, c, "unrealisable_frac")
        row += f"{mu:12.4f}+-{sd:6.4f}"
    print(row)
print(f"{'TRUTH (BASELINES.md)':30s}" + "".join(f"{TRUTH_UNREAL[c]:20.4f}" for c in cases))
print(f"{'truth recomputed':30s}" +
      "".join(f"{r['baselines'][c]['truth_unrealisable_frac']:20.4f}" for c in cases))
print(f"{'SST':30s}" +
      "".join(f"{r['baselines'][c]['sst_unrealisable_frac']:20.4f}" for c in cases))

print("\n== mean |trace(b_pred)| ==")
for m in r["runs"]:
    print(f"{m:30s}" + "".join(f"{agg(m, c, 'mean_abs_trace')[0]:20.5f}" for c in cases))

print("\n== in-sample b_rms_F, leaves, depth-cap hits, fit seconds ==")
for m in r["runs"]:
    ss = r["runs"][m]["seeds"]
    ins = np.mean([s["in_sample_b_rms_F"] for s in ss.values()])
    lv = np.mean([s["mean_leaves"] for s in ss.values()])
    dh = np.mean([s["depth_cap_hits"] for s in ss.values()])
    ft = np.mean([s["fit_seconds"] for s in ss.values()])
    print(f"{m:30s} in-sample={ins:8.4f} leaves={lv:8.0f} depth_cap={dh:6.1f} "
          f"fit={ft:6.1f}s nseeds={len(ss)} maxfeat={r['runs'][m]['max_features']} "
          f"minleaf={r['runs'][m]['min_samples_leaf']} gamma={r['runs'][m]['gamma']:g}")

print("\n== claim (i): FS-full vs FS-SRonly on the PRIMARY case AR_1_Ret_360 ==")
try:
    full = [m for m in r["runs"] if m.endswith("_full")][0]
    sr = [m for m in r["runs"] if m.endswith("_SRonly")][0]
    for c in cases:
        a = agg(full, c, "b_rms_F"); b = agg(sr, c, "b_rms_F")
        sep = (a[0] + 2 * a[1]) < (b[0] - 2 * b[1])
        print(f"  {c:22s} full={a[0]:.4f}+-{a[1]:.4f}  SRonly={b[0]:.4f}+-{b[1]:.4f}  "
              f"better={a[0] < b[0]}  2sigma_separated={sep}")
except IndexError:
    pass
print("\ncore_hours=", r["meta"].get("core_hours"), " wall_hours=", r["meta"].get("wall_hours"))
