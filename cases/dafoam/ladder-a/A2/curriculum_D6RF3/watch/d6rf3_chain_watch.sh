#!/usr/bin/env bash
# D6RF3 CHAIN WATCHER -- attached to the queue launch of D6RF3_chain.
#
# WHY IT EXISTS.  Sanaa, 2026-09-05, verbatim: "The checks before the run are needed
# and justified.  However, not in an infinite loop.  Past some time the lab must take
# action (this applies to any team) and launch the run with its attached watcher to
# fix/debug and see what happens: act accordingly."
#
# WHAT IT IS.  A READ-ONLY observer.  It never writes into the run root, never signals
# the driver, the launcher or any container, and never edits a frozen file.  Everything
# it writes lands under this directory (the CASE directory's watch/), which is where a
# handoff artefact belongs -- the scratchpad is temp only and is never a handoff
# channel (L-186).
#
# IT SURVIVES THE AGENT THAT ARMED IT.  It is started with setsid from a wrapper, and
# the wrapper captures the rc INSIDE itself: `setsid timeout cmd` exits 0 for every
# outcome, so an rc captured around the setsid line is meaningless.  This script writes
# its own pid to PIDFILE as its FIRST action, so the reported pid is the watcher's own
# and not a parent that has already exited.
#
# IT IS NOT A CAP ENFORCER.  scripts/queue_runner.py's cap_watch owns CAP_OVERRUN.txt
# and ESTIMATE_OVERRUN.txt against the registered cap.  A second enforcer would be a
# second record for one run.  This one observes, times out on its own bound, and says
# what it saw.
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
CASE_DIR="$(cd "$HERE/.." && pwd)"
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6RF3-a2-wing-multipoint-fd
QUEUE_DIR=/home/ubuntu/Certonomous/verification/queue/dafoam
ENTRY=D6RF3_chain.json
CASE_ID=D6RF3_chain

LOG="$HERE/d6rf3_chain_watch.log"
PIDFILE="$HERE/d6rf3_chain_watch.pid"

POLL_S=30
# BOUND: the registered wall envelope plus the driver's own H5 wait bound.  Arm
# deadlines are 7110 s and 2760 s with a 90 s frame allowance each (PREREGISTRATION.md
# section 4a), i.e. 10 050 s of registered run; the driver may additionally hold up to
# H5_BOUND_S = 14400 s waiting for free memory before the first arm.  The bound below
# covers both with margin, and reaching it is REPORTED, never treated as an ending.
BOUND_S=32400
STALL_S=1200

echo $$ > "$PIDFILE"

say() { printf '%s %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >> "$LOG"; }

newest_mtime_age_s() {   # age in seconds of the newest file anywhere under $1, or -1
  local d="$1" t now
  [ -d "$d" ] || { echo -1; return; }
  t=$(find "$d" -newermt '@0' -printf '%T@\n' 2>/dev/null | sort -n | tail -1)
  [ -n "$t" ] || { echo -1; return; }
  now=$(date +%s)
  awk -v a="$now" -v b="$t" 'BEGIN{printf "%d", a-b}'
}

ledger_core_min() {      # cumulative core_min from the run root ledger, or UNMEASURED
  local f="$BASE/ledger.txt"
  [ -f "$f" ] || { echo UNMEASURED; return; }
  awk '{ for (i=1;i<=NF;i++) if ($i ~ /^core_min=/) { split($i,p,"="); if (p[2]+0==p[2]) s+=p[2] } }
       END { printf "%.3f", s+0 }' "$f"
}

say "WATCH START pid=$$ ppid=$PPID sid=$(ps -o sid= -p $$ 2>/dev/null | tr -d ' ') case=$CASE_ID"
say "WATCH scope=READ-ONLY: observes the queue entry, the run root and the case STATUS files; touches none of them."
say "WATCH bound_s=$BOUND_S poll_s=$POLL_S stall_s=$STALL_S run_root=$BASE"
say "WATCH registered: F_mp cap 480.0 core-min / TMO 7110 s; REF_off cap 190.0 core-min / TMO 2760 s; item ceiling 670.0 core-min; predicted 215.77 (PREREGISTRATION.md sections 4a, 4a.1, frozen 9c079a84)."

START=$(date +%s)
TAKEN=no
ROOT_SEEN=no
STALL_REPORTED=no
RC_TERMINAL=""

while :; do
  NOW=$(date +%s); ELAPSED=$(( NOW - START ))

  # --- where is the queue entry? -------------------------------------------
  if [ "$TAKEN" = no ]; then
    if [ -f "$QUEUE_DIR/launched/$ENTRY" ]; then
      TAKEN=yes
      PID=$(python3 -c "import json,sys;print(json.load(open('$QUEUE_DIR/launched/$ENTRY')).get('_launch',{}).get('pid','?'))" 2>/dev/null || echo '?')
      UTC=$(python3 -c "import json,sys;print(json.load(open('$QUEUE_DIR/launched/$ENTRY')).get('_launch',{}).get('utc','?'))" 2>/dev/null || echo '?')
      say "TAKEN the daemon took the entry: launched/$ENTRY  launch_pid=$PID launch_utc=$UTC"
    elif [ -f "$QUEUE_DIR/refused/$ENTRY" ]; then
      say "REFUSED the validator refused the entry -> refused/$ENTRY.  See refused/${ENTRY%.json}.REFUSED.txt.  NOTHING LAUNCHED, 0 core-min."
      RC_TERMINAL=4; break
    elif [ -f "$QUEUE_DIR/$ENTRY" ]; then
      [ $(( ELAPSED % 300 )) -lt "$POLL_S" ] && say "QUEUED still in the drop path after ${ELAPSED}s (the daemon HOLDs on busy%, core fraction or MemAvailable and retries every tick; a hold is not a refusal)."
    else
      say "MISSING entry is in neither the drop path, launched/ nor refused/ after ${ELAPSED}s.  REPORTED, not acted on."
    fi
  fi

  # --- the run root ---------------------------------------------------------
  if [ -d "$BASE" ]; then
    if [ "$ROOT_SEEN" = no ]; then ROOT_SEEN=yes; say "ROOT staged: $BASE exists (the driver creates it on the first fire)."; fi
    AGE=$(newest_mtime_age_s "$BASE")
    SPENT=$(ledger_core_min)
    NC=$(docker ps -q 2>/dev/null | wc -l)
    MEM=$(awk '/MemAvailable/{printf "%.1f",$2/1048576}' /proc/meminfo)
    say "TICK elapsed=${ELAPSED}s newest_artefact_age=${AGE}s ledger_core_min=$SPENT containers=$NC mem_avail_gb=$MEM"
    if [ "$AGE" -ge 0 ] && [ "$AGE" -gt "$STALL_S" ] && [ "$NC" -eq 0 ] && [ "$STALL_REPORTED" = no ]; then
      STALL_REPORTED=yes
      say "STALL nothing under the run root has been written for ${AGE}s and no container is running.  REPORTED as a finding for the supervisor; this watcher takes no action against the run."
      { echo "STALL observed $(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo "newest artefact age ${AGE}s, containers 0, ledger core_min $SPENT"; } >> "$HERE/d6rf3_chain_watch.FINDINGS"
    fi
    [ "$AGE" -le "$STALL_S" ] && STALL_REPORTED=no
    for s in "$BASE"/STATUS.* ; do
      [ -f "$s" ] || continue
      L=$(tail -n 1 "$s" 2>/dev/null)
      say "STATUS $(basename "$s"): $L"
    done
    if [ -f "$BASE/CHAIN_DONE" ]; then
      say "CHAIN_DONE $(tail -n 1 "$BASE/CHAIN_DONE")"
      RC_TERMINAL=0; break
    fi
  else
    [ $(( ELAPSED % 300 )) -lt "$POLL_S" ] && say "ROOT not yet staged after ${ELAPSED}s (absent is the pre-launch state; the driver stages it)."
  fi

  # --- the runner's own record of the launch argv's exit --------------------
  if [ -f "$CASE_DIR/STATUS.queue.$CASE_ID" ]; then
    say "LAUNCH-ARGV-EXIT $(tail -n 1 "$CASE_DIR/STATUS.queue.$CASE_ID")"
    say "NOTE that rc is the exit status of the LAUNCH ARGV, not the solver's rc (L-342 field classes).  Rule 4 is applied from the case's own RC and log files."
    RC_TERMINAL=0; break
  fi

  if [ "$ELAPSED" -ge "$BOUND_S" ]; then
    say "BOUND-REACHED ${ELAPSED}s >= ${BOUND_S}s with no terminal condition.  This is REPORTED, never read as an ending: the chain may still be alive.  Re-attach rather than restart -- a restart would be a second record for one run."
    RC_TERMINAL=3; break
  fi
  sleep "$POLL_S"
done

# --- closing summary ---------------------------------------------------------
say "---- CLOSING SUMMARY ----"
say "queue entry: drop=$( [ -f "$QUEUE_DIR/$ENTRY" ] && echo present || echo absent )  launched=$( [ -f "$QUEUE_DIR/launched/$ENTRY" ] && echo present || echo absent )  refused=$( [ -f "$QUEUE_DIR/refused/$ENTRY" ] && echo present || echo absent )"
say "run root: $( [ -d "$BASE" ] && echo present || echo ABSENT )  ledger_core_min=$(ledger_core_min)  against predicted 215.77 / item ceiling 670.0"
if [ -f "$BASE/ledger.txt" ]; then
  while IFS= read -r l; do say "LEDGER $l"; done < <(tail -n 20 "$BASE/ledger.txt")
fi
for s in "$BASE"/STATUS.* "$CASE_DIR"/STATUS.queue."$CASE_ID"; do
  [ -f "$s" ] || continue
  say "FINAL $(basename "$s"): $(tail -n 1 "$s")"
done
say "OWED AT COMPLETION, and this watcher does not discharge them: (1) grading by d6rf3_grade.py, which verifies its own bytes against the committed blob and refuses on a mismatch; (2) the section 12.4 plateau report -- each component's plateau_pct beside the 10.0 bar, and whether the bar was exercised at all; (3) the ONE-ROW PATCHED label, NOT a full DAFOAM_CHARTER section 6 verdict, with the unbought SHIPPED row priced at 155.70 core-min; (4) the docs/COST_CALIBRATION.md row, actual/predicted against 215.77 core-min with waste named separately."
say "WATCH END terminal_rc=${RC_TERMINAL:-unset}"
exit "${RC_TERMINAL:-3}"
