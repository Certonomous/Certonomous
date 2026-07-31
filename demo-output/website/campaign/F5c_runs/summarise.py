#!/usr/bin/env python3
"""Aggregate F5c run records into the gate table.

Reports, for each run: the mesh, the algorithm, the achieved outer-loop
residuals, the reattachment length, the independent near-wall-U cross-check,
and -- because this case does not reach a steady fixed point -- the
oscillation band of x_r/H over the last ``--window`` iterations rather than
the single end-of-run sample. The detector's own resolution (the spacing of
the two wall faces bracketing the crossing) is reported next to every x_r,
per LESSONS L-28.

Usage: summarise.py [--window N] RUN_DIR [RUN_DIR ...]
"""
import argparse
import json
import statistics
from pathlib import Path

X_R_REF, X_R_BAND = 6.26, 0.10


def bracket_spacing(profile, xr):
    """Face spacing straddling the crossing -- the detector's resolution."""
    best = None
    for (x0, _), (x1, _) in zip(profile, profile[1:]):
        if x0 <= xr <= x1:
            best = x1 - x0
    return best


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", type=int, default=5000)
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args()

    rows = []
    for rd in (Path(p) for p in args.runs):
        rec = json.loads((rd / "record.json").read_text())
        prof = json.loads((rd / "wall_shear_profile.json").read_text())
        hist = [(t, v) for t, v in rec["x_r_over_h_history"] if v is not None]
        last = rec["final_iteration"] or (hist[-1][0] if hist else 0)
        win = [v for t, v in hist if t > last - args.window]
        row = {
            "run": rd.name,
            "level": rec["level"],
            "cells": rec["cells"],
            "algorithm": rec.get("algorithm", "SIMPLEC"),
            "relax_p": rec.get("relax_p"), "relax_u": rec.get("relax_u"),
            "inlet_bl_turbulence": rec.get("inlet_bl_turbulence", False),
            "iterations": rec["iterations"],
            "final_iteration": rec["final_iteration"],
            "final_initial_residuals": rec["final_initial_residuals"],
            "converged_to_gate": rec["converged"],
            "x_r_over_h_end": rec["x_r_over_h"],
            "x_r_over_h_nearwall_U": rec["x_r_over_h_nearwall_U"],
            "detector_bracket_spacing_over_h":
                bracket_spacing(prof, rec["x_r_over_h"]) if rec["x_r_over_h"] else None,
            "window_iterations": args.window,
            "window_samples": len(win),
            "x_r_over_h_window_mean": statistics.fmean(win) if win else None,
            "x_r_over_h_window_min": min(win) if win else None,
            "x_r_over_h_window_max": max(win) if win else None,
            "x_r_over_h_window_stdev": (statistics.stdev(win) if len(win) > 1 else None),
            "old_detector_would_report": (rec["reattachment"] or {}).get(
                "bubble_start_over_h"),
            "corner_eddy_over_h": (rec["reattachment"] or {}).get("corner_eddy_over_h"),
            "attached_to_outlet": (rec["reattachment"] or {}).get("attached_to_outlet"),
            "wall_seconds": rec["wall_seconds"],
        }
        m = row["x_r_over_h_window_mean"]
        row["deviation_pct_window_mean"] = (
            100.0 * (m - X_R_REF) / X_R_REF if m is not None else None)
        row["in_gate_window_mean"] = (
            abs(m - X_R_REF) <= X_R_BAND if m is not None else False)
        rows.append(row)

    hdr = (f"{'run':26} {'cells':>7} {'alg':8} {'it':>6} {'p-res':>9} "
           f"{'x_r end':>8} {'nearU':>7} {'mean':>7} {'min':>6} {'max':>6} "
           f"{'dev%':>7} {'old':>6}")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        p = r["final_initial_residuals"].get("p")
        print(f"{r['run']:26} {r['cells']:7,} {r['algorithm']:8} "
              f"{r['final_iteration'] or 0:6} {p if p is None else f'{p:.2e}':>9} "
              f"{r['x_r_over_h_end']:8.3f} {r['x_r_over_h_nearwall_U'] or 0:7.3f} "
              f"{r['x_r_over_h_window_mean'] or 0:7.3f} "
              f"{r['x_r_over_h_window_min'] or 0:6.3f} "
              f"{r['x_r_over_h_window_max'] or 0:6.3f} "
              f"{r['deviation_pct_window_mean'] or 0:+7.1f} "
              f"{r['old_detector_would_report'] or 0:6.3f}")
    print(f"\nreference: Driver & Seegmiller 1985, x_r/H = {X_R_REF} +/- {X_R_BAND}")
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(
            {"reference_x_r_over_h": X_R_REF, "reference_band": X_R_BAND,
             "runs": rows}, indent=2))
        print(f"wrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
