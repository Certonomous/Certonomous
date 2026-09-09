#!/usr/bin/env bash
# =============================================================================
# autograde_watch_vmfl046_r8.sh -- DETACHED disconnect-safe autograder for
# VMFL046-R8 (Supersonic normal-shock CD nozzle, rhoPimpleFoam pressure-based).
# The §2ba disconnect-safe grading leg (the supervisor holds the live leg).
#
# WHY: the R8 graded solve (3 levels, L3 cap 1040 core-min ~17 h) runs under the
# capacity-managed queue daemon and the fleet dies periodically.  Launched with
# `setsid`, this watcher survives fleet + launching-agent death (PPID=1, own
# session): it waits for the driver to TERMINATE, then runs the FROZEN comparator
# ONCE so the verdict lands with NO live fleet.
#
# THIS WATCHER ADDS NO GRADING LOGIC.  It only decides WHEN.  grade_vmfl046_r8.py
# is the authority (strict completion rule 4 per level, Roache triple, the frozen
# gate x_shock vs 1.250 m +-5 %, LIMB (b) clamp-non-binding, LIMB (c) washout).
# Before grading it re-verifies the comparator on disk is byte-for-byte the frozen
# file (rule 2).  rc is captured INSIDE this process because setsid's own exit
# status is always 0 (memory: setsid-parent-returns-zero).
# =============================================================================
set +u

REPO=/home/ubuntu/Certonomous
CASE_DIR="$REPO/cases/ansys_verification/VMFL046-R8"
RUN_ROOT="$REPO/verification/runs/ansys_verification/VMFL046-R8"
COMPARATOR="$CASE_DIR/grade_vmfl046_r8.py"
PIN_BLOB="f89114bb6ff81f683c6c6718460040cab305a8ce"   # frozen a7a0e72b; disk==HEAD verified at arm
LAUNCHER_OUT="$CASE_DIR/launcher.queue.out"

STATE="$RUN_ROOT/AUTOGRADE_WATCH_STATE.txt"
GLOG="$RUN_ROOT/GRADING_VMFL046_R8.log"
GJSON="$RUN_ROOT/GRADING_VMFL046_R8.json"
GRC="$RUN_ROOT/AUTOGRADE_VMFL046_R8.rc"

log(){ echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >> "$STATE"; }
: > "$STATE"
log "watcher START pid=$$ ppid=$PPID sid=$(ps -o sid= -p $$ 2>/dev/null | tr -d ' ')"
log "run_root=$RUN_ROOT comparator=$COMPARATOR pin=$PIN_BLOB"
log "waits for the queue-launched driver to TERMINATE (launcher.queue.out 'launcher done'|'ABORT', or STATUS.queue file), then grades once"

POLL=60
CAP=2880          # 48 h ceiling (L3 cap ~17 h + queue wait + contention)
i=0
STARTED=0
TERMINAL=""
while [ "$i" -lt "$CAP" ]; do
  # start-race guard: the driver may not be launched by the daemon yet.
  if [ "$STARTED" -eq 0 ]; then
    if [ -f "$LAUNCHER_OUT" ] || pgrep -f 'run_vmfl046_r8.sh' >/dev/null 2>&1 || [ -d "$RUN_ROOT/L1" ]; then
      STARTED=1; log "driver START detected at iter=$i"
    fi
  fi
  # terminal signal: the launcher argv has exited (success or abort).
  if [ -f "$LAUNCHER_OUT" ] && grep -aqE 'VMFL046-R8 launcher done|^ABORT' "$LAUNCHER_OUT" 2>/dev/null; then
    TERMINAL="launcher.queue.out"; break
  fi
  if ls "$CASE_DIR"/STATUS.queue.VMFL046-R8 "$CASE_DIR"/STATUS.VMFL046-R8 >/dev/null 2>&1; then
    TERMINAL="STATUS.queue"; break
  fi
  # if it started and both the driver and any rhoPimpleFoam are gone, treat as terminal.
  if [ "$STARTED" -eq 1 ] && ! pgrep -f 'run_vmfl046_r8.sh' >/dev/null 2>&1 \
       && ! pgrep -x rhoPimpleFoam >/dev/null 2>&1; then
    TERMINAL="driver+solver-gone"; break
  fi
  i=$((i+1)); sleep "$POLL"
done

if [ -z "$TERMINAL" ]; then
  log "REFUSE: poll cap $CAP reached without a terminal signal -- NOT grading; a future session must investigate"
  echo "poll_cap_reached rc=3 utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$GRC"
  exit 3
fi
log "driver TERMINAL via $TERMINAL at iter=$i; settling 30 s for bookkeeping flush"
sleep 30

# ---- rule 2: grade only with the frozen file --------------------------------
DISK_BLOB="$(git -C "$REPO" hash-object "$COMPARATOR" 2>/dev/null)"
if [ "$DISK_BLOB" != "$PIN_BLOB" ]; then
  log "REFUSE: comparator on disk ($DISK_BLOB) != pinned freeze blob ($PIN_BLOB) (rule 2). NOT grading."
  echo "comparator_blob_mismatch disk=$DISK_BLOB pin=$PIN_BLOB rc=2 utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$GRC"
  exit 2
fi
log "comparator freeze OK  disk==pin  $PIN_BLOB"

# ---- grade ONCE; capture rc INSIDE this process -----------------------------
log "grading: python3 $COMPARATOR $RUN_ROOT"
python3 "$COMPARATOR" "$RUN_ROOT" > "$GLOG" 2>&1
RC=$?
VERDICT="$(grep -aoE 'VERDICT: .*' "$GLOG" 2>/dev/null | head -1 | sed 's/VERDICT: //')"
if [ -z "$VERDICT" ]; then
  if grep -aq '^REFUSE:' "$GLOG" 2>/dev/null; then VERDICT="NOT A RESULT (comparator REFUSED, exit 2)"; else VERDICT="see GRADING_VMFL046_R8.log"; fi
fi
echo "grade_rc=$RC utc=$(date -u +%Y-%m-%dT%H:%M:%SZ) comparator_blob=$PIN_BLOB" > "$GRC"
UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
cat > "$GJSON" <<EOF
{
  "case_id": "VMFL046-R8",
  "grade_rc": $RC,
  "verdict": "$VERDICT",
  "comparator_blob": "$PIN_BLOB",
  "prereg_commit": "a7a0e72b",
  "run_root": "$RUN_ROOT",
  "graded_utc": "$UTC",
  "terminal_signal": "$TERMINAL",
  "note": "rc 0 = GATE REACHED (band); rc 1 = GATE FAIL or NOT A RESULT (see log verdict); rc 2 = comparator REFUSED (incomplete/failed run) = NOT A RESULT. Verdict text and all limb prints are in GRADING_VMFL046_R8.log."
}
EOF
log "grade DONE rc=$RC verdict='$VERDICT'  json=$GJSON  log=$GLOG"
log "watcher END (verdict on disk; a future session/supervisor records it in the register + commits)"
exit "$RC"
