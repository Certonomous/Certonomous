#!/bin/bash
# Detached autograder for VMFL078-R2 -- 3-D lid-driven cubic cavity, Re=1000, FULL CUBE.
# WITHOUT THIS THE VERDICT DOES NOT LAND IF THE LAUNCHING SESSION DIES.  VMFL078 nearly
# produced no verdict at all for exactly that reason.
#
# LESSONS BAKED IN, each paid for on this team:
#  - Detached (setsid, stdin /dev/null), so PPID is 1 and it outlives its lane.
#  - The GRADE rc is captured INSIDE this (already-detached) watcher as RC=$? on the
#    line after python3.  `setsid cmd` returns 0 for EVERY outcome, so an rc taken
#    around a setsid line is a lie (setsid-parent-returns-zero).
#  - Trigger from the CONSUMER's OWN reader: the launcher's own RUN_RC.<level> terminal
#    record, which run_vmfl078_r2.sh rewrites on exit AND WRITES EVEN ON A CRASH (the
#    non-zero-rc STOP is AFTER the printf).  A CRASH IS A MEASUREMENT AND GETS GRADED.
#    NEVER a sibling observer's filename (L-532).
#  - The launcher stops at the first non-zero rc, so F3's record may never appear.  The
#    terminal condition is therefore: F3 finished, OR an EARLIER level finished with a
#    non-zero rc (the crash case).  Both are graded; the comparator decides what they mean.
#  - Scope the live-solver check by /proc/PID/cwd.  MANY foreign simpleFoam/mpirun run
#    on this box; a bare `pgrep -x simpleFoam` would see them and never fire.
#  - Re-verify the comparator against its pin IMMEDIATELY before grading (rule 2) and
#    REFUSE on drift.  The pin is read from the committed HEAD blob at arm time.
#  - grade() ONLY, via --run-root.  NEVER --selftest (L-548): a watcher that runs the
#    selftest grades nothing and reports success.
#  - Poll cap FAR beyond any plausible ETA.  Predicted F3 is ~1840 core-min / 4 ranks
#    = ~7.7 h wall, total ~8-10 h; under the contention measured at launch it could be
#    3x that.  96 h ceiling.  A watcher that expires before its run is worse than none.
REPO=/home/ubuntu/Certonomous
CASE=$REPO/cases/ansys_verification/VMFL078-R2
RUNROOT=$REPO/verification/runs/ansys_verification/VMFL078-R2
CMP=$CASE/grade_vmfl078_r2.py
PIN="${VMFL078R2_PIN:?refusing to arm without an explicit comparator pin}"
GRC=$RUNROOT/AUTOGRADE_VMFL078_R2.rc
GLOG=$RUNROOT/GRADING_VMFL078_R2.log
JSON=$RUNROOT/GRADE_VMFL078_R2.json
STATE=$RUNROOT/AUTOGRADE_WATCH_STATE.txt
mkdir -p "$RUNROOT"
log(){ echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >> "$STATE"; }

solver_alive_under_root(){
  local pid cwd
  for pid in $(pgrep -x simpleFoam 2>/dev/null) $(pgrep -x mpirun 2>/dev/null) $(pgrep -x blockMesh 2>/dev/null) $(pgrep -x decomposePar 2>/dev/null) $(pgrep -x reconstructPar 2>/dev/null); do
    cwd=$(readlink "/proc/$pid/cwd" 2>/dev/null) || continue
    case "$cwd" in
      "$RUNROOT"|"$RUNROOT"/*) return 0 ;;
    esac
  done
  return 1
}

# The launcher itself still running is NOT terminal: it may be meshing the next level.
launcher_alive(){
  pgrep -af 'run_vmfl078_r2\.sh' >/dev/null 2>&1
}

terminal(){
  local f rc
  f="$RUNROOT/RUN_RC.F3"
  if grep -qE '^state = FINISHED$' "$f" 2>/dev/null; then
    TERMINAL_WHY="RUN_RC.F3 terminal"; return 0
  fi
  for L in F1 F2; do
    f="$RUNROOT/RUN_RC.$L"
    grep -qE '^state = FINISHED$' "$f" 2>/dev/null || continue
    rc=$(sed -nE 's/^rc = (.*)$/\1/p' "$f" | head -1)
    if [ -n "$rc" ] && [ "$rc" != "0" ]; then
      TERMINAL_WHY="RUN_RC.$L terminal with rc=$rc -- the ladder STOPPED on a crash, and a crash is a measurement"
      return 0
    fi
  done
  return 1
}

log "watcher START pid=$$ ppid=$PPID pin=$PIN runroot=$RUNROOT cap=5760x60s=96h"
CAP=5760; i=0
while [ "$i" -lt "$CAP" ]; do
  if terminal && ! solver_alive_under_root && ! launcher_alive; then
    log "TERMINAL: $TERMINAL_WHY ; no live solver under runroot; no live launcher (poll iter=$i)"
    break
  fi
  i=$((i+1)); sleep 60
done
if [ "$i" -ge "$CAP" ]; then
  log "REFUSE: 96h poll cap reached without a terminal RUN_RC -- NOT grading (never grade an unfinished run). This is a WATCHER cap, not a run cap: nothing was killed."
  echo "poll_cap_reached rc=3 utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$GRC"
  exit 3
fi
sleep 30   # settle: let reconstructPar / RUN_RC / probe writes flush
DISK=$(git -C "$REPO" hash-object "$CMP" 2>/dev/null)
if [ "$DISK" != "$PIN" ]; then
  log "REFUSE: comparator on disk ($DISK) != pin ($PIN) -- rule 2, the grading path has DRIFTED. NOT grading."
  echo "comparator_blob_mismatch disk=$DISK pin=$PIN rc=2 utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$GRC"
  exit 2
fi
log "comparator freeze OK: disk == pin $PIN ; grading with grade() (NOT --selftest)"
rm -rf "$CASE/__pycache__"
python3 "$CMP" --run-root "$RUNROOT" --out "$JSON" --repo "$REPO" > "$GLOG" 2>&1
RC=$?
echo "grade_rc=$RC utc=$(date -u +%Y-%m-%dT%H:%M:%SZ) comparator_blob=$PIN json=$JSON" > "$GRC"
log "grade DONE rc=$RC (0=verdict produced; 2=comparator REFUSED a guard; 3=poll cap)"
exit $RC
