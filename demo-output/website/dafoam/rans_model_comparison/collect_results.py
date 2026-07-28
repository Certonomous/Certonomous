#!/usr/bin/env python3
"""Collect secondary-flow gate results across the RANS turbulence-model sweep.
Reads each model's final converged U field, computes secondary-flow RMS as
%U_bulk, and pulls solver iteration count / ExecutionTime from log.run.
No fitting/tuning -- pure post-processing of already-converged fields.
"""
import re, os, sys, json, glob

import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
DNS_PCT_AR1 = 2.22  # from F6c_duct_vs_dns.md, AR_1_Ret_360, DNS secondary RMS %Ubulk

def read_of_vector_field(path):
    with open(path) as f:
        txt = f.read()
    m = re.search(r'nonuniform List<vector>\s*\n(\d+)\s*\n\((.*?)\n\)\s*;?', txt, re.S)
    n = int(m.group(1))
    body = m.group(2)
    vecs = re.findall(r'\(([^()]+)\)', body)
    arr = np.array([[float(x) for x in v.split()] for v in vecs])
    assert arr.shape[0] == n, f"{path}: {arr.shape[0]} != {n}"
    return arr

def last_time_dir(case_dir):
    times = []
    for d in os.listdir(case_dir):
        if re.match(r'^\d+$', d) and d != '0':
            times.append(int(d))
    if not times:
        return None
    return str(max(times))

def parse_log(log_path):
    if not os.path.exists(log_path):
        return {"converged": False, "iterations": None, "exec_time_s": None}
    txt = open(log_path).read()
    converged = "SIMPLE solution converged" in txt
    it = None
    m = re.findall(r'^Time = (\d+)', txt, re.M)
    if m:
        it = int(m[-1])
    et = None
    m2 = re.findall(r'ExecutionTime = ([\d.]+) s', txt)
    if m2:
        et = float(m2[-1])
    crashed = "FOAM FATAL" in txt or "sigHandler" in txt or "dumped core" in txt
    return {"converged": converged, "iterations": it, "exec_time_s": et, "crashed": crashed}

MODELS = ["SpalartAllmaras", "kEpsilon", "realizableKE", "kOmega", "LienCubicKE"]

results = {}
for m in MODELS:
    case_dir = os.path.join(BASE, m)
    log_info = parse_log(os.path.join(case_dir, "log.run"))
    td = last_time_dir(case_dir)
    entry = {"log": log_info, "final_time_dir": td}
    if td is not None:
        u_path = os.path.join(case_dir, td, "U")
        if os.path.exists(u_path):
            arr = read_of_vector_field(u_path)
            Ub = float(arr[:, 0].mean())
            sec = np.sqrt(arr[:, 1] ** 2 + arr[:, 2] ** 2)
            sec_rms = float(np.sqrt(np.mean(sec ** 2)))
            sec_max = float(sec.max())
            entry.update({
                "n_cells": int(arr.shape[0]),
                "Ubulk_ms": Ub,
                "secondary_rms_ms": sec_rms,
                "secondary_rms_pct_Ubulk": 100.0 * sec_rms / Ub,
                "secondary_max_pct_Ubulk": 100.0 * sec_max / Ub,
                "pct_of_DNS_captured": 100.0 * (100.0 * sec_rms / Ub) / DNS_PCT_AR1,
                "has_nan_or_inf": bool(np.isnan(arr).any() or np.isinf(arr).any()),
            })
    results[m] = entry

print(json.dumps(results, indent=2))
with open(os.path.join(BASE, "sweep_results.json"), "w") as f:
    json.dump(results, f, indent=2)
