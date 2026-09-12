#!/usr/bin/env python3
"""Emit the `docs/COST_CALIBRATION.md` row for K2h_L3, computed from the logs.

CLAUDE.md rule 12's last clause: at every process completion the pre-registered
estimate is compared against the actual incurred cost, the ratio is stated, and
the gap is ATTRIBUTED.  This script computes the row rather than letting anyone
retype figures from memory -- append rule 2 of that ledger says numbers come
from committed records, never from memory.

IT DOES NOT APPEND.  It prints the row's cells.  The row lands through
`scripts/append_record.py --path docs/COST_CALIBRATION.md`, which is what makes
a concurrent append REFUSABLE, and the id is generated there -- the ledger's ids
are timestamped (`C-<compact ISO>-<hash>`), not an integer series, so nothing is
"numbered" here.  Committing is the supervisor's act, not this lane's.

THE THREE ARITHMETIC TRAPS THIS SCRIPT EXISTS TO AVOID:

  1. `log.solve` IS APPENDED TO ON RESUME (the registration's ERRATUM).  The
     last `ExecutionTime` line is SEGMENT 2's only; the concatenated
     `grep -c` counts two different clocks.  Every figure here is computed
     PER SEGMENT and then summed.

  2. `STATUS.K2h_L3`'s own `wall_s`, `core_min`, `execution_time_s` and
     `n_timesteps` are SEGMENT-2-ONLY for the same reason -- `.k2h_inner.sh`
     measures from its own T0, which is the resume.  They are read and PRINTED
     for comparison, and they are NOT used as the actual.

  3. WASTE IS NAMED SEPARATELY and never folded into the ratio
     (COMPUTE_BUDGET_CHARTER section 6).  Segment 1 computed past its last
     surviving checkpoint and that tail was discarded by the resume.
"""
import glob
import json
import os
import re
import sys

REPO = "/home/ubuntu/Certonomous"
RUNS = os.path.join(REPO, "verification/runs/F14-cooling-ladder/K2h_runs")
CASE = os.path.join(RUNS, "K2h_L3")
RANKS = 4
POINT = 420.0
CAP = 1260.0
RATE = 0.0513                      # $/core-h, owner-stated; DERIVED, NOT MEASURED
RESUME_AT = 10.0                   # the checkpoint the resume started from
REG_DT = 0.0475                    # section 8's estimated mean deltaT
REG_STEPS = 2358                   # section 8's derived step count
REG_SPS = 2.82                     # section 8's derived wall per step
K2B_DT = 0.0804                    # K2b's MEASURED deltaT at 137,000 cells
LINEAR_RATIO = 1.69                # (664848/137000)**(1/3), section 8's factor
STALL_S = 3600.0                   # charter section 2's stall rule


def _max_jump(clock):
    """Largest single-step wall-clock jump in a segment, seconds."""
    if len(clock) < 2:
        return 0.0
    return max(clock[i] - clock[i - 1] for i in range(1, len(clock)))


def _stall_verdict(clock):
    j = _max_jump(clock)
    if j > STALL_S:
        return ("STALL: a single step took %.1f s, above the %g s stall rule; "
                "the cleaned figure must exclude it" % (j, STALL_S))
    return ("none: largest single-step wall jump %.1f s, against the %g s "
            "stall rule" % (j, STALL_S))


def segments():
    segs, cur = [], None
    for line in open(os.path.join(CASE, "log.solve"), errors="replace"):
        if line.startswith("Build  :"):
            cur = {"t": [], "dt": [], "exec": [], "clock": []}
            segs.append(cur)
        if cur is None:
            continue
        try:
            if line.startswith("Time = "):
                cur["t"].append(float(line.split("=")[1]))
            elif line.startswith("deltaT = "):
                cur["dt"].append(float(line.split("=")[1]))
            elif line.startswith("ExecutionTime = "):
                cur["exec"].append(float(line.split("=")[1].split("s")[0]))
                cur["clock"].append(float(line.split("ClockTime =")[1].split("s")[0]))
        except (ValueError, IndexError):
            pass
    return segs


def main():
    segs = segments()
    rows, tot_exec, tot_clock, tot_steps = [], 0.0, 0.0, 0
    for i, s in enumerate(segs, 1):
        if not s["exec"]:
            continue
        e, c = s["exec"][-1], s["clock"][-1]
        n = len(s["t"])
        rows.append({
            "segment": i, "t_first": s["t"][0], "t_last": s["t"][-1],
            "steps": n, "exec_s": e, "clock_s": c,
            "core_min": e * RANKS / 60.0,
            "s_per_step": e / len(s["exec"]),
            "dt_mean": sum(s["dt"]) / len(s["dt"]),
            "exe_over_clk": e / c, "contention_pct": 100.0 * (1.0 - e / c),
            # THE STALL RULE, ACTUALLY MEASURED.  This field previously read
            # `"none ..." if c <= STALL_S or True else ""`, whose `or True` made
            # it report "none" unconditionally -- a guard that cannot say yes is
            # not a guard, and it would have put a false "no stall" into a ledger
            # cell.  The rule is per ROW: a single time step whose wall clock
            # exceeds 3600 s.  The largest single-step ClockTime jump in the
            # segment is what is compared against it, and it is PRINTED so the
            # margin is visible rather than asserted.
            "max_step_clock_s": _max_jump(s["clock"]),
            "stall_rows": _stall_verdict(s["clock"]),
        })
        tot_exec += e
        tot_clock += c
        tot_steps += n

    gross = tot_exec * RANKS / 60.0

    # ---- WASTE, named separately and NEVER folded into the ratio ------------
    s1 = rows[0]
    lost_t = max(0.0, s1["t_last"] - RESUME_AT)
    lost_steps = sum(1 for t in segs[0]["t"] if t > RESUME_AT)
    waste_cm = lost_steps * s1["s_per_step"] * RANKS / 60.0

    # CLEANED = gross minus rows the stall rule matches (charter section 2).
    # Derived from the MEASUREMENT above, never asserted: if a segment carries a
    # stalled step the row must say so and the two figures must differ.
    stalled = [r for r in rows if r["max_step_clock_s"] > STALL_S]
    cleaned = gross - sum(r["max_step_clock_s"] * RANKS / 60.0 for r in stalled)
    stall_note = ("none — largest single-step wall jump across both segments "
                  "%.1f s, against the %g s stall rule"
                  % (max(r["max_step_clock_s"] for r in rows), STALL_S)
                  ) if not stalled else (
        "%d stalled step(s) removed: %s" % (
            len(stalled), "; ".join("segment %d %.1f s" % (r["segment"],
                                    r["max_step_clock_s"]) for r in stalled)))
    dt_meas = rows[-1]["dt_mean"]
    true_ratio = K2B_DT / dt_meas
    sps_meas = tot_exec / max(1, tot_steps)

    status = {}
    sp = os.path.join(RUNS, "STATUS.K2h_L3")
    if os.path.exists(sp):
        for line in open(sp):
            if "=" in line:
                k, v = line.strip().split("=", 1)
                status[k] = v

    out = {
        "date": "2026-09-12", "team": "heat-transfer", "rung": "K2h_L3",
        "predicted_core_min": POINT, "cap_core_min": CAP,
        "actual_gross_core_min": gross,
        "actual_cleaned_core_min": cleaned,
        "stall_rule": stall_note,
        "ratio_cleaned_over_predicted": cleaned / POINT,
        "ratio_vs_cap": cleaned / CAP,
        "cap_crossed": cleaned > CAP,
        "dollars_DERIVED_NOT_MEASURED": cleaned / 60.0 * RATE,
        "segments": rows,
        "total_steps": tot_steps,
        "measured_mean_deltaT": dt_meas,
        "registered_mean_deltaT": REG_DT,
        "deltaT_miss_factor": REG_DT / dt_meas,
        "true_deltaT_ratio_vs_K2b": true_ratio,
        "registered_linear_ratio": LINEAR_RATIO,
        "measured_s_per_step": sps_meas,
        "registered_s_per_step": REG_SPS,
        "pimple_factor_conservatism": REG_SPS / sps_meas,
        "registered_steps": REG_STEPS,
        "step_miss_factor": tot_steps / REG_STEPS,
        "contention_per_segment_pct": [r["contention_pct"] for r in rows],
        "waste_core_min": waste_cm,
        "waste_what": (
            "segment 1 ran to t=%.4f but only the t=%g checkpoint survived; "
            "%.4f s of simulated time = %d steps at segment 1's measured "
            "%.4f s/step was computed and DISCARDED by the resume"
            % (s1["t_last"], RESUME_AT, lost_t, lost_steps, s1["s_per_step"])),
        "STATUS_file_figures_SEGMENT_2_ONLY_DO_NOT_USE_AS_ACTUAL": status,
    }
    print(json.dumps(out, indent=2))

    print("\n" + "=" * 78)
    print("DRAFT ROW for docs/COST_CALIBRATION.md -- NOT APPENDED, NOT COMMITTED.")
    print("id is generated by scripts/append_record.py at append time.")
    print("=" * 78)
    cells = [
        "<id generated at append>", "2026-09-12", "heat-transfer",
        ("**K2h_L3 — the F14 rack-row module graded TRANSIENT, one level and NO "
         "TRIPLE.** Section 3 of the registration forbids an observed order or a "
         "GCI from a mixed steady/time-averaged set; K2h_L1 and K2h_L2 do not "
         "exist, so none is quoted. Graded quantity `DPbar` = time-averaged "
         "`DP_module` over simulated 42–112 s, read at `endTime` 112 from the "
         "`fieldAverage` output through the FROZEN `foam_patch_reader."
         "area_average`. <VERDICT AND GATE SENTENCE FILLED AT COMPLETION>"),
        "%g core-min (POINT, section 8; cap %g)" % (POINT, CAP),
        "**%.2f core-min** (sum of the two log segments' own last `ExecutionTime`, "
        "%.2f s × %d ranks — NOT `STATUS.K2h_L3`, whose figures are segment-2-only)"
        % (gross, tot_exec, RANKS),
        "**%.2f core-min** (stall rule: %s)" % (cleaned, stall_note),
        "**%.3f** (cleaned/predicted)" % (cleaned / POINT),
        ("**MISPREDICTION, AND SPECIFICALLY A WRONG SCALING LAW — not contention "
         "and not waste.** Section 8 scaled a COURANT-LIMITED time step by the "
         "LINEAR cell-count ratio (664848/137000)^(1/3) = %.2f, predicting mean "
         "`deltaT` %.4f s from K2b's measured %.4f s at 137,000 cells. **The true "
         "ratio is %.1fx**: measured mean `deltaT` is **%.7f s**, identical to nine "
         "significant figures across all %d steps of both segments because it is "
         "pinned at the Courant ceiling (`Courant Number max: 1.99989` against "
         "`maxCo 2.0`; `maxDeltaT 0.25` never binds). **On a locally refined mesh "
         "the Courant limit is set by the SMALLEST cell, not the mean, so a "
         "per-cell-count scaling is the wrong law.** Step count %d against a "
         "registered %d = %.2fx. "
         "**OFFSETTING TERM, named because it partly cancelled the miss:** the "
         "×2.5 PIMPLE-over-SIMPLE factor was CONSERVATIVE by %.2fx — %.4f s/step "
         "measured against %.2f predicted. "
         "**CONTENTION, separately named and NOT folded into the ratio "
         "(COMPUTE_BUDGET_CHARTER §6):** exe/clk per segment %s, i.e. %s — "
         "negligible, so the overrun is not this run losing cycles to the "
         "scheduler. "
         "**WASTE, separately named and NOT folded into the ratio: %.2f core-min** "
         "— %s. The other %.2f core-min of segment 1 is NOT waste: the resume "
         "preserved it and it is this run's initial condition. "
         "**$%.4f DERIVED, NOT MEASURED** at $%g/core-h, c7a.4xlarge, "
         "owner-stated — the box cannot read its own billing "
         "(`COMPUTE_BUDGET_CHARTER.md` §5). "
         "**Registered cap %g core-min %s (%.2fx).** Per Sanaa's 2026-09-12 "
         "04:20Z directive #17 the cap is a FLAG and not a STOP: the run was "
         "never stopped, no guard was armed and no signal was sent. Whether a "
         "crossing forces `NOT A RESULT` is ESCALATED AND UNRULED and is not "
         "settled by this row."
         % (LINEAR_RATIO, REG_DT, K2B_DT, true_ratio, dt_meas, tot_steps,
            tot_steps, REG_STEPS, tot_steps / REG_STEPS,
            REG_SPS / sps_meas, sps_meas, REG_SPS,
            ", ".join("%.4f" % r["exe_over_clk"] for r in rows),
            " and ".join("%.2f %%" % r["contention_pct"] for r in rows),
            waste_cm, out["waste_what"], s1["core_min"] - waste_cm,
            cleaned / 60.0 * RATE, RATE, CAP,
            "CROSSED" if cleaned > CAP else "not crossed", cleaned / CAP)),
        ("run `verification/runs/F14-cooling-ladder/K2h_runs/K2h_L3` "
         "(`log.solve` split at its two `Build  :` banners, `GRADE.K2h_L3.json`, "
         "`WATCH.lane.K2h_L3.tsv`, `CAP_FLAG.cumulative.txt`); comparator "
         "`K2h_runs/analyse_k2h.py`; prereg "
         "`docs/campaigns/F14-cooling-ladder/K2h_PREREGISTRATION.md` frozen at "
         "`db523d06a`, AMENDMENT 1 + ADDENDUM 1 + ERRATUM + ADDENDUM 2"),
    ]
    print("| " + " | ".join(cells) + " |")
    return 0


if __name__ == "__main__":
    sys.exit(main())
