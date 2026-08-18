#!/usr/bin/env python3
"""Post-hoc analysis of a completed F5a cylinder rung.

Usage:  analyze_re3900.py [CASE_DIR] [END_TIME] [OUT_JSON]

Reads the run's own postProcessing output from disk and applies the SAME
statistics machinery cylinder_ladder.py uses (time_weighted_stats,
measure_period, halves_drift, and the module's own base_cpb /
recirculation_length logic). Zero new compute.

Written for the Re=3900 rung, whose own record.json this reproduces exactly --
an L-2 confirmation obtained by recomputing from raw solver output rather than
trusting the self-report. Parameterised so the corrected-spacing rerun (and any
later rung) can be scored on the identical code path, which is the only way the
two are comparable.

Note the averaging-window sweep below: the ladder's default "second half"
(t >= 45) still carried 6.63% Cd drift at Re=3900, so a single window is not
evidence a mean has settled -- report the sweep, and justify the window by its
measured drift.
"""
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path("/home/ubuntu/Certonomous")
sys.path.insert(0, str(REPO / "sdk"))

from workflows.tmr_verification import (  # noqa: E402
    time_weighted_stats, measure_period, halves_drift,
)
from workflows.cylinder_vortex_shedding import DIAMETER, U_INF  # noqa: E402
from chief_engineer.head_engineer import parse_coefficient_history  # noqa: E402

sys.path.insert(0, str(REPO / "demo-output/website/campaign/F5_runs"))
from cylinder_ladder import (  # noqa: E402
    parse_probes_scalar, parse_probes_vector, centerline_probe_points,
)

CASE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "/home/ubuntu/certonomous-runs/f5a-cylinder-ladder/re3900")
END_TIME = float(sys.argv[2]) if len(sys.argv) > 2 else 90.0
OUT_JSON = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(
    "/tmp/claude-1000/-home-ubuntu-Certonomous/982d6244-5800-47f3-a450-80ce0b0a24b7"
    "/scratchpad/re3900_analysis.json")
print(f"case={CASE}\nend_time={END_TIME}")

hist = parse_coefficient_history(
    (CASE / "postProcessing/forceCoeffs1/0/coefficient.dat").read_text(errors="replace"))
times = hist["Time"]
print(f"steps={len(times)}  t_final={times[-1]:.4f}  (endTime={END_TIME})")

out = {"case": str(CASE), "end_time": END_TIME, "t_final": times[-1],
       "steps": len(times), "diameter": DIAMETER, "u_inf": U_INF}

# Sweep several averaging-window starts to show the result is not an artifact
# of one arbitrary window choice.
for frac in (0.5, 0.6, 0.7):
    t_start = frac * END_TIME
    cd = time_weighted_stats(times, hist["Cd"], t_start)
    cl = time_weighted_stats(times, hist["Cl"], t_start)
    per = measure_period(times, hist["Cl"], t_start)
    dr = halves_drift(times, hist["Cd"], cd["window_start"], cd["window_end"])
    st = (DIAMETER / (per * U_INF)) if per else None
    # RMS lift about its own mean
    win = [(t, c) for t, c in zip(times, hist["Cl"]) if t >= t_start]
    clm = sum(c for _, c in win) / len(win)
    cl_rms = (sum((c - clm) ** 2 for _, c in win) / len(win)) ** 0.5
    rec = {"t_start": t_start,
           "cd_mean": cd["mean"], "cd_band": cd["band"],
           "cl_mean": cl["mean"], "cl_band": cl["band"], "cl_rms": cl_rms,
           "period": per, "strouhal": st,
           "cd_relative_drift": dr["relative_drift"] if dr else None,
           "stationary": (dr["relative_drift"] <= 0.10) if dr else None}
    out[f"window_{frac}"] = rec
    print(f"\n--- averaging window t>={t_start:g} ---")
    print(f"  Cd  = {cd['mean']:.4f} +/- {cd['band']:.4f}")
    print(f"  Cl  = {cl['mean']:.4f} +/- {cl['band']:.4f}   Cl_rms = {cl_rms:.4f}")
    print(f"  St  = {st:.4f}" if st else "  St  = no period detected")
    print(f"  Cd drift = {100*dr['relative_drift']:.2f}%  stationary={dr['relative_drift']<=0.10}")

# base pressure coefficient
t_start = 0.5 * END_TIME
ptimes, prows = parse_probes_scalar((CASE / "postProcessing/probesBase/0/p").read_text(errors="replace"))
pser = [r[0] for r in prows if r]
ps = time_weighted_stats(ptimes, pser, t_start)
cp = ps["mean"] / (0.5 * U_INF ** 2)
out["cpb"] = {"p_mean": ps["mean"], "cp": cp, "cpb_magnitude": -cp,
              "band": ps["band"] / (0.5 * U_INF ** 2)}
print(f"\n-Cpb = {-cp:.4f}  (band +/- {ps['band']/(0.5*U_INF**2):.4f})")

# recirculation length
pts = centerline_probe_points()
utimes, urows = parse_probes_vector((CASE / "postProcessing/probesCenterline/0/U").read_text(errors="replace"))
profile = []
for i in range(len(pts)):
    ser = [r[i][0] for r in urows if len(r) > i]
    s = time_weighted_stats(utimes, ser, t_start)
    if s:
        profile.append((pts[i][0], s["mean"]))
lr = None
for (x0, u0), (x1, u1) in zip(profile, profile[1:]):
    if u0 < 0 <= u1:
        frac_ = (0.0 - u0) / (u1 - u0) if u1 != u0 else 0.0
        lr = (x0 + frac_ * (x1 - x0)) - DIAMETER / 2.0
        break
out["recirculation"] = {"lr_over_d": (lr / DIAMETER) if lr is not None else None,
                        "u_min": min(u for _, u in profile),
                        "any_reversed_flow": any(u < 0 for _, u in profile),
                        "profile": profile}
print(f"Lr/D = {lr/DIAMETER:.4f}" if lr is not None else "Lr/D = not found (no sign crossing)")
print(f"  u_min on centerline = {min(u for _, u in profile):.4f}, "
      f"any reversed = {any(u < 0 for _, u in profile)}")

# --- Raw (non-time-averaged) near-base reversal statistics -------------------
# Tests the falsifiable mechanism recorded for this rung: the mean bubble
# vanishes NOT because the flow stops reversing (reversal frequency is ~34-48%
# and flat across Re 1000/2000/3900) but because the forward-going excursions
# grow (max +Ux 0.22 -> 0.52 -> 0.81) until they swamp the reversal in the mean.
# The prediction on record: a corrected-spacing rerun should keep reversal
# frequency ~35%. If it instead drops sharply AND a mean bubble reappears, the
# mechanism is wrong. Computed here so that test is one command, not a re-derivation.
#
# COMPARISON BASIS -- must match the existing record or the numbers are not
# comparable. The figures already on record ("34-39% of all 7,275 samples",
# max +Ux 0.22 -> 0.52 -> 0.81 across the three rungs) are:
#   * restricted to the averaging window (t >= t_start), NOT all of t=0..90 --
#     7,275 is a count of TIME rows in that window, not probe-samples; and
#   * reported as the PER-PROBE range across the window, not one aggregate.
# Aggregating over every probe and all time instead gives 45.9% for the same
# case -- a real-looking but spurious 7-12 point "change". Both bases are
# emitted below; `per_probe_fraction_range` is the one to compare against the
# record, `aggregate_fraction_all_time` is context only.
def reversal_stats(lo_s: float, hi_s: float, t_start: float) -> dict[str, Any]:
    idx = [i for i, (x, _, _) in enumerate(pts)
           if lo_s <= (x - DIAMETER / 2.0) / DIAMETER <= hi_s]
    keep = [r for t, r in zip(utimes, urows) if t >= t_start]
    per_probe, mx_pos, mx_neg = [], float("-inf"), float("inf")
    for i in idx:
        tot = rev = 0
        for row in keep:
            if len(row) <= i:
                continue
            ux = row[i][0]
            tot += 1
            rev += ux < 0
            mx_pos, mx_neg = max(mx_pos, ux), min(mx_neg, ux)
        if tot:
            per_probe.append(rev / tot)
    agg_tot = sum(1 for row in urows for i in idx if len(row) > i)
    agg_rev = sum(1 for row in urows for i in idx if len(row) > i and row[i][0] < 0)
    return {"window_s_over_D": [lo_s, hi_s], "t_start": t_start,
            "n_time_rows_in_window": len(keep), "n_probes": len(idx),
            "per_probe_fraction_range": [min(per_probe), max(per_probe)] if per_probe else None,
            "aggregate_fraction_all_time": (agg_rev / agg_tot) if agg_tot else None,
            "max_positive_ux": mx_pos if per_probe else None,
            "max_negative_ux": mx_neg if per_probe else None}

_ts = 0.5 * END_TIME
out["reversal"] = {"near_base_0.05_0.25": reversal_stats(0.05, 0.25, _ts),
                   "near_wake_0.05_0.50": reversal_stats(0.05, 0.50, _ts)}
for key, rs in out["reversal"].items():
    if rs["per_probe_fraction_range"]:
        lo, hi = rs["per_probe_fraction_range"]
        print(f"\nreversal {key} (t>={rs['t_start']:g}, {rs['n_time_rows_in_window']} time rows, "
              f"{rs['n_probes']} probes):")
        print(f"  per-probe reversal {100*lo:.1f}-{100*hi:.1f}%   "
              f"[aggregate over all time: {100*rs['aggregate_fraction_all_time']:.1f}%]")
        print(f"  max +Ux {rs['max_positive_ux']:.3f}, max -Ux {rs['max_negative_ux']:.3f}")

yp = (CASE / "postProcessing/yPlus1/0/yPlus.dat").read_text(errors="replace").strip().splitlines()
out["yplus_last"] = yp[-1] if yp else None
print(f"\nyPlus last line: {yp[-1] if yp else 'n/a'}")

OUT_JSON.write_text(json.dumps(out, indent=2, default=str))
print(f"\nwrote {OUT_JSON}")
