#!/bin/bash
# CRM WING-ALONE L2 -- COST ROW WATCHER. IT EMITS NO VERDICT AND GRADES NOTHING.
#
# IT IS NOT A SECOND GRADER. "Two watchers on one run is two records" is a rule about
# GRADERS -- a second thing emitting a verdict makes a second record of a verdict. This
# emits cost, and cost_row_crm_l2.py MACHINE-ENFORCES that by scanning its own output for
# every token in CLAUDE.md rule 1's vocabulary and refusing to write if it finds one.
#
# FILES IT MAY WRITE, AND NO OTHERS:
#   COST_ROW.txt  COST_ROW.log  COST_WRITER_RC.txt  COST_ROW.REFUSED.txt
# It NEVER writes the grader's outputs (GRADE_CRM_L2.txt, VERDICT.crm_l2, grade_rc,
# AUTOGRADE.*, GRADE_PLANT/), NEVER writes solve_rc or any rc the grader reads, and NEVER
# writes into 0/, 4000/ or postProcessing/. If it fails, grader and run are untouched.
#
# NO KILL PRIMITIVE AND NO CAP. It reads. rc IS CAPTURED INSIDE THIS WRAPPER, because
# `setsid cmd` exits 0 for every outcome and the rc around the setsid line means nothing.
set -u
CASE="$1"; LPID="$2"; WRITER="$3"
LOG="$CASE/COST_ROW.log"
say() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >> "$LOG"; }
say "ARMED case=$CASE launcher_pid=$LPID writer=$WRITER"
say "writer sha256=$(sha256sum "$WRITER" | cut -d' ' -f1)"
say "COST ONLY. NO VERDICT. NO CAP. NO KILL PRIMITIVE. Trigger = the run's own solve_rc."

N=0
while [ ! -f "$CASE/solve_rc" ]; do
  ALIVE=0
  if [ -d "/proc/$LPID" ]; then
    CWD=$(readlink "/proc/$LPID/cwd" 2>/dev/null || echo "")
    CMD=$(tr '\0' ' ' < "/proc/$LPID/cmdline" 2>/dev/null || echo "")
    if [ "$CWD" = "$CASE" ]; then
      case "$CMD" in *launch_crm_l2.sh*) ALIVE=1 ;; esac
    fi
  fi
  if [ "$ALIVE" -eq 0 ]; then
    say "LAUNCHER $LPID GONE BY IDENTITY with no solve_rc. Writing the row from whatever"
    say "artifacts exist; the writer names every field it cannot measure as UNMEASURED."
    break
  fi
  N=$((N+1))
  [ $((N % 30)) -eq 1 ] && say "WAITING reading=$N. Not signalling; not capping; just waiting."
  sleep 60
done

# rc CAPTURED INSIDE THIS WRAPPER, at the point of the call.
python3 "$WRITER" "$CASE" >> "$LOG" 2>&1
CRC=$?
echo "$CRC" > "$CASE/COST_WRITER_RC.txt"
say "COST WRITER EXITED rc=$CRC (0 wrote COST_ROW.txt | 2 REFUSED: its output carried a verdict token)"
say "DONE. Nothing was signalled, nothing was stopped, and no verdict was written."
exit "$CRC"
