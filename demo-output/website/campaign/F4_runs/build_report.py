#!/usr/bin/env python3
"""Collect all F4 cyl/M*/*/result.json files into one summary JSON + a
markdown table fragment, mirroring F3_runs/build_report.py's role."""
import glob
import json
import os

BASE = os.path.dirname(__file__)


def main():
    files = sorted(glob.glob(f"{BASE}/cyl/M*/*/result.json"))
    results = []
    for f in files:
        r = json.load(open(f))
        results.append(r)
    out = {"results": results}
    with open(f"{BASE}/../F4_hypersonic_blunt_body.json", "w") as f:
        json.dump(out, f, indent=2)

    print(f"{'M':>5} {'res':>7} {'ncells':>7} {'standoff_mean':>14} {'billig':>8} "
          f"{'dev%':>7} {'std':>7} {'rmsCp%':>8} {'t_run_s':>9}")
    total_core_min = 0.0
    for r in results:
        total_core_min += (r["t_mesh_s"] + r["t_check_s"] + r["t_run_s"] + r["t_sample_s"]) / 60.0
        print(f"{r['M']:>5.1f} {r['res_level']:>7} {r['ncells']:>7} "
              f"{r['standoff_mean']:>14.5f} {r['delta_billig']:>8.4f} "
              f"{r['standoff_dev_pct']:>7.2f} {r['standoff_std']:>7.4f} "
              f"{r['rms_cp_full_pct_of_cpmax']:>8.3f} {r['t_run_s']:>9.2f}")
    print(f"\nTotal core-minutes (mesh+check+run+sample, all cases): {total_core_min:.2f}")


if __name__ == "__main__":
    main()
