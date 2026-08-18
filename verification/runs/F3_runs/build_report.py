#!/usr/bin/env python3
"""Assemble the F3 supersonic exact-theory deliverable JSON from all result.json
files plus the exact_theory.py closed-form values. Run after all CFD cases
have finished."""
import json, glob, sys
sys.path.insert(0, "/home/ubuntu/Certonomous/demo-output/website/campaign/F3_runs")
import numpy as np
from exact_theory import oblique_shock, beta_from_theta, taylor_maccoll_solve, diamond_wave_drag

ROOT = "/home/ubuntu/Certonomous/demo-output/website/campaign/F3_runs"


def total_time(d):
    return d.get("t_mesh_s", 0) + d.get("t_run_s", 0) + d.get("t_sample_s", 0)


def load_all(pattern):
    out = []
    for f in sorted(glob.glob(f"{ROOT}/{pattern}")):
        out.append((f, json.load(open(f))))
    return out


report = {"family": "F3", "campaign": "supersonic exact-theory (wedge / cone / diamond)",
          "solver": "rhoCentralFoam, OpenFOAM v2606, native (no Docker)",
          "gas_model": "gamma=1.4, inviscid (mu=0), nondimensional a=1 at T=1 "
                       "(molWeight chosen so R gives gamma=1.4), so U magnitude = Mach number",
          "cases": {}}

# --- Wedge ---
wedge_pairs = {}
for f, d in load_all("wedge/*/*/result.json"):
    key = f"M{d['M']}_th{d['theta_deg']}"
    wedge_pairs.setdefault(key, {"M": d["M"], "theta_deg": d["theta_deg"], "levels": {}})
    exact = oblique_shock(d["M"], beta_from_theta(d["M"], np.radians(d["theta_deg"])))
    wedge_pairs[key]["exact"] = dict(beta_deg=float(np.degrees(beta_from_theta(d["M"], np.radians(d["theta_deg"])))),
                                      p2_p1=float(exact["p2_p1"]), rho2_rho1=float(exact["rho2_rho1"]),
                                      M2=float(exact["M2"]))
    wedge_pairs[key]["levels"][d["res_level"]] = dict(
        ncells=d["ncells"], core_s=total_time(d),
        beta_computed_deg=d["beta_computed_deg"], beta_all_stations_deg=d["beta_all_stations_deg"],
        fit_r2=d["fit_r2"], fit_r2_all=d["fit_r2_all_stations"],
        p_wall_mean=d["p_wall_mean"], p_wall_std=d["p_wall_std"],
        beta_dev_pct=100 * (d["beta_computed_deg"] - d["beta_exact_deg"]) / d["beta_exact_deg"],
        beta_all_dev_pct=100 * (d["beta_all_stations_deg"] - d["beta_exact_deg"]) / d["beta_exact_deg"],
        p_dev_pct=100 * (d["p_wall_mean"] - exact["p2_p1"]) / exact["p2_p1"],
    )
report["cases"]["1_wedge"] = wedge_pairs

# --- Cone ---
cone_pairs = {}
for f, d in load_all("cone/*/*/result.json"):
    key = f"M{d['M']}_thc{d['theta_c_deg']}"
    cone_pairs.setdefault(key, {"M": d["M"], "theta_c_deg": d["theta_c_deg"], "levels": {}})
    tm = taylor_maccoll_solve(d["M"], np.radians(d["theta_c_deg"]))
    cone_pairs[key]["exact_taylor_maccoll_own_solver"] = dict(
        beta_deg=float(np.degrees(tm["beta"])), M2=float(tm["M2"]), p2_p1=float(tm["p2_p1"]),
        M_c=float(tm["M_c"]), pc_p1=float(tm["pc_p1"]))
    cone_pairs[key]["levels"][d["res_level"]] = dict(
        ncells=d["ncells"], core_s=total_time(d),
        beta_computed_deg=d["beta_computed_deg"], beta_all_stations_deg=d["beta_all_stations_deg"],
        fit_r2=d["fit_r2"], fit_r2_all=d["fit_r2_all_stations"],
        p_wall_mean=d["p_wall_mean"], p_wall_std=d["p_wall_std"],
        beta_dev_pct=100 * (d["beta_computed_deg"] - d["beta_exact_deg"]) / d["beta_exact_deg"],
        beta_all_dev_pct=100 * (d["beta_all_stations_deg"] - d["beta_exact_deg"]) / d["beta_exact_deg"],
        p_dev_pct=100 * (d["p_wall_mean"] - tm["pc_p1"]) / tm["pc_p1"],
    )
report["cases"]["2_cone"] = cone_pairs

# --- Diamond ---
diamond_pairs = {}
for f, d in load_all("diamond/*/*/result.json"):
    key = f"M{d['M']}_eps{d['eps_deg']}"
    diamond_pairs.setdefault(key, {"M": d["M"], "eps_deg": d["eps_deg"], "levels": {}})
    ex = diamond_wave_drag(d["M"], np.radians(d["eps_deg"]))
    diamond_pairs[key]["exact"] = dict(beta_deg=float(ex["beta_deg"]), p2_p1=float(ex["p2_p1"]),
                                        p3_p1=float(ex["p3_p1"]), cd=float(ex["cd"]))
    diamond_pairs[key]["levels"][d["res_level"]] = dict(
        ncells=d["ncells"], core_s=d["t_mesh_s"] + d["t_run_s"],
        cd_computed=d["cd_computed"], deviation_pct=d["deviation_pct"])
report["cases"]["3_diamond"] = diamond_pairs

total_core_s = 0
for case in report["cases"].values():
    for pair in case.values():
        for lvl in pair["levels"].values():
            total_core_s += lvl["core_s"]
report["total_core_minutes"] = total_core_s / 60

with open(f"{ROOT}/../F3_supersonic_exact_theory.json", "w") as f:
    json.dump(report, f, indent=2)

print(json.dumps(report, indent=2)[:2000])
print("...")
print("TOTAL CORE-MINUTES:", report["total_core_minutes"])
