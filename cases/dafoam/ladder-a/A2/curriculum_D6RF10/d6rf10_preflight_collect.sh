#!/usr/bin/env bash
# =============================================================================
# curriculum D6RF10 -- THE §2ba PRE-FLIGHT COLLECTOR.
#
# Polls the exercise ledger (`d6rf10_preflight_exercise.sh`) for
# `D6RF10_PREFLIGHT_DONE`, then reads each smoke's container log and EMITS, per
# rung (R2/R3/R4), the two MEASUREMENTS §2ba needs:
#   (a) the LATE-window per-step wall cost
#        = (ExecutionTime[last] - ExecutionTime[mid]) / (steps between),
#        taken over the DEVELOPED-field late window (mid..last), NOT the cheap
#        early steps -- the per-step cost escalates, so an early sample lies low.
#   (b) `p_first_uncorrected` at the last sampled Time, and whether it sits
#        within ~1% of its own late-window values (a plateau flag).
# Written to `d6rf10_preflight_MEASUREMENTS.json` under the exercise root.
#
# THIS COLLECTOR DECLARES NO VERDICT AND SIZES NO DEADLINE. It does NOT invoke
# `d6rf10_grade.py`, does NOT read the frozen gate/floor, and does NOT compare
# against any threshold. Sizing the R3/R4 deadlines and deciding their endTime
# (300 if flat by 300, else longer) is the dafoam-supervisor's call, made FROM
# these measurements -- not this script's.
#
# SELF-DETACH (same pattern as the exercise/launcher): the plain command
# re-execs THIS script under setsid; there is no verdict for the parent exit to
# carry, so the parent's `exit 0` is only the detach spawn.
# =============================================================================
set -u
set -o pipefail

if [ -z "${D6RF10_COLLECT_DETACHED:-}" ]; then
  export D6RF10_COLLECT_DETACHED=1
  D6RF10_COLLECT_OUT="/home/ubuntu/certonomous-runs/d6rf10_preflight_collect_$(date -u +%Y%m%dT%H%M%SZ)_$$.out"
  export D6RF10_COLLECT_OUT
  setsid bash "$0" "$@" > "$D6RF10_COLLECT_OUT" 2>&1 < /dev/null &
  echo "D6RF10_COLLECT_DETACHED child_pid=$! launch_out=$D6RF10_COLLECT_OUT"
  echo "  polls the exercise ledger, then writes d6rf10_preflight_MEASUREMENTS.json; NO verdict, NO deadline."
  exit 0
fi
trap '_c_rc=$?; echo "COLLECT_RC=$_c_rc" >> "${D6RF10_COLLECT_OUT:-/dev/null}"' EXIT

EXERCISE_BASE=/home/ubuntu/certonomous-runs/D6RF10-PREFLIGHT-EXERCISE
LEDGER="$EXERCISE_BASE/preflight_ledger.txt"
POLL_INTERVAL_S=30
POLL_MAX_S=14400   # 4 h cap on polling; a measurement that has not finished by then is reported as not-done, no verdict

# ---- poll for D6RF10_PREFLIGHT_DONE ----------------------------------------
waited=0
while :; do
  if [ -f "$LEDGER" ] && grep -q '^D6RF10_PREFLIGHT_DONE' "$LEDGER" 2>/dev/null; then
    echo "D6RF10_COLLECT_LEDGER_DONE after ${waited}s"
    break
  fi
  if [ "$waited" -ge "$POLL_MAX_S" ]; then
    echo "D6RF10_COLLECT_TIMEOUT no D6RF10_PREFLIGHT_DONE after ${POLL_MAX_S}s -- nothing collected, NO verdict."
    exit 4
  fi
  sleep "$POLL_INTERVAL_S"
  waited=$((waited + POLL_INTERVAL_S))
done

# ---- parse the smoke logs and emit the measurements JSON -------------------
EX_BASE="$EXERCISE_BASE" python3 - <<'PYEOF'
import json, os, re, statistics

base = os.environ["EX_BASE"]
ledger = os.path.join(base, "preflight_ledger.txt")

logs, rc, stopped = {}, {}, {}
with open(ledger, errors="replace") as fh:
    for line in fh:
        if line.startswith("D6RF10_PREFLIGHT_SMOKE_DONE"):
            d = dict(kv.split("=", 1) for kv in line.split() if "=" in kv)
            sm = d.get("smoke")
            if sm:
                logs[sm] = d.get("log")
                rc[sm] = d.get("rc")
                stopped[sm] = d.get("stopped")

TIME = re.compile(r'^Time = (\d+)\s*$')
EXEC = re.compile(r'^ExecutionTime = (\S+) s')
PRES = re.compile(r'^p initRes: (\S+) finalRes: (\S+) nIters: (\d+)\s*$')

out = {
    "item": "D6RF10",
    "exercise": "preflight",
    "note": ("MEASUREMENT ONLY -- no verdict, no deadline sizing. The "
             "dafoam-supervisor sizes R3/R4 deadlines and decides endTime "
             "(300 if flat by 300, else longer) FROM these numbers."),
    "per_rung": {},
}

for sm, logbn in logs.items():
    rec = {"rc": rc.get(sm), "stopped": stopped.get(sm), "log": logbn}
    path = os.path.join(base, logbn) if logbn else None
    if not path or not os.path.isfile(path):
        rec["error"] = "log absent on disk"
        out["per_rung"][sm] = rec
        continue

    steps, cur = [], None
    with open(path, errors="replace") as fh:
        for line in fh:
            mt = TIME.match(line)
            if mt:
                if cur is not None:
                    steps.append(cur)
                cur = {"time": int(mt.group(1)), "exec": None, "p_first": None}
                continue
            if cur is None:
                continue
            me = EXEC.match(line)
            if me:
                try:
                    cur["exec"] = float(me.group(1))
                except ValueError:
                    pass
                continue
            mp = PRES.match(line)
            if mp and cur["p_first"] is None:
                try:
                    cur["p_first"] = float(mp.group(1))
                except ValueError:
                    pass
        if cur is not None:
            steps.append(cur)

    tsteps = [s for s in steps if s["exec"] is not None]
    psteps = [s for s in steps if s["p_first"] is not None]
    rec["n_steps_sampled"] = len(steps)
    rec["n_exec_samples"] = len(tsteps)
    rec["n_p_first_samples"] = len(psteps)
    rec["last_time"] = steps[-1]["time"] if steps else None

    # (a) LATE-window per-step wall cost over the developed-field window mid..last
    if len(tsteps) >= 2:
        mid = len(tsteps) // 2
        t_mid, t_last = tsteps[mid], tsteps[-1]
        dsteps = t_last["time"] - t_mid["time"]
        if dsteps > 0:
            rec["late_window_per_step_wall_s"] = {
                "mid_time": t_mid["time"], "last_time": t_last["time"],
                "mid_exec_s": t_mid["exec"], "last_exec_s": t_last["exec"],
                "steps_between": dsteps,
                "late_per_step_wall_s": round((t_last["exec"] - t_mid["exec"]) / dsteps, 4),
            }
        else:
            rec["late_window_per_step_wall_s"] = {"error": "non-increasing time across late window"}
    else:
        rec["late_window_per_step_wall_s"] = {"error": "fewer than 2 ExecutionTime samples"}

    # (b) p_first_uncorrected at last sampled Time + late-window plateau flag
    if psteps:
        mid = len(psteps) // 2
        late = [s["p_first"] for s in psteps[mid:]]
        p_last = psteps[-1]["p_first"]
        lo, hi = min(late), max(late)
        ref = abs(p_last) if p_last else (abs(statistics.median(late)) or 1.0)
        spread = (hi - lo) / ref if ref else None
        rec["p_first_uncorrected"] = {
            "at_last_sampled_time": p_last,
            "last_sampled_time": psteps[-1]["time"],
            "late_window_min": lo,
            "late_window_max": hi,
            "late_window_n": len(late),
            "relative_spread_over_last": (round(spread, 6) if spread is not None else None),
            "plateau_within_1pct": bool(spread is not None and spread <= 0.01),
        }
    else:
        rec["p_first_uncorrected"] = {"error": "no `p initRes:` lines parsed"}

    out["per_rung"][sm] = rec

dest = os.path.join(base, "d6rf10_preflight_MEASUREMENTS.json")
with open(dest, "w") as fh:
    json.dump(out, fh, indent=2, sort_keys=True)
    fh.write("\n")
print("D6RF10_PREFLIGHT_MEASUREMENTS_WRITTEN dest=%s rungs=%s" % (dest, ",".join(sorted(out["per_rung"]))))
PYEOF

echo "D6RF10_COLLECT_DONE measurements written; NO verdict declared, NO deadline sized."
exit 0
