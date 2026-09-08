#!/usr/bin/env bash
# SO-3D-R STAGE 2 SUCCESSOR "R" -- detached 36-leg campaign DAEMON.  DRAFT -- NOT FROZEN.
#
# The parent (curriculum_SO3DR_stage2/) embedded its 36-leg loop directly in
# so3dr_stage2_run_leg.sh and was launched under `setsid nohup bash run_leg.sh ...`.
# That posture LOSES the launcher's rc: `setsid <cmd>` makes the parent process
# exit 0 for EVERY outcome of <cmd> (memory note: setsid-parent-returns-zero;
# L capture rc INSIDE the detached wrapper, never around the setsid line).
#
# This _R daemon is the fix: it is the process placed under setsid+nohup, it
# invokes the frozen-instrument-verifying per-leg launcher ONCE (which itself
# iterates all 36 registered legs and enforces the 198 core-min CUMULATIVE hard
# stop and the per-leg 1200 s / 3600 s-stall stop), and it captures that
# launcher's rc INSIDE this wrapper into <BASE>.rc.txt with an End marker.  The
# outer setsid line's own exit status is therefore meaningless by design and is
# ignored; the real verdict lives in <BASE>.rc.txt.
#
# G-ROOT no-delete: the launcher refuses a pre-existing -base; this daemon also
# refuses if the freshly stamped BASE already exists, and NEVER deletes a tree.
#
# The daemon touches NO frozen file.  It does not run any solver itself; the
# solver runs inside the per-leg launcher's containers.
set -uo pipefail

CASE_DIR="/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_SO3DR_stage2_R"
RUN_LEG="$CASE_DIR/so3dr_stage2R_run_leg.sh"
RUNS_PARENT="/home/ubuntu/certonomous-runs"

CPUSET="${CPUSET:-}"
BASE="${BASE:-}"       # optional override; default is a fresh timestamped root
while [ $# -gt 0 ]; do
  case "$1" in
    -cpuset) CPUSET="$2"; shift 2;;
    -base)   BASE="$2";   shift 2;;
    *) echo "ABORT usage: -cpuset <cores> [-base <root>]"; exit 64;;
  esac
done
[ -n "$CPUSET" ] || { echo "ABORT: -cpuset must be given explicitly; placement is never defaulted"; exit 64; }
[ -x "$RUN_LEG" ] || [ -f "$RUN_LEG" ] || { echo "ABORT: per-leg launcher not found at $RUN_LEG"; exit 64; }

# ---- fresh, timestamped campaign root (parent stamp pattern), G-ROOT no-delete ----
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
[ -n "$BASE" ] || BASE="$RUNS_PARENT/CURRICULUM-SO3DR-STAGE2R-a2-cl04-standalone-$STAMP"
[ -e "$BASE" ] && { echo "ABORT G-ROOT: $BASE exists; never reuse or delete an interrupted run root -- pick a fresh stamp"; exit 3; }

LAUNCH_OUT="$BASE.launch.out"
RC_FILE="$BASE.rc.txt"

echo "=== SO3DR_STAGE2R DAEMON START $(date -u +%Y%m%dT%H%M%SZ) base=$BASE cpuset=$CPUSET ===" | tee -a "$LAUNCH_OUT"

# Invoke the per-leg launcher ONCE with NO -only_dv_block_line so it iterates all
# 36 registered legs.  rc is captured INSIDE this wrapper (setsid-parent-returns-zero).
bash "$RUN_LEG" -base "$BASE" -cpuset "$CPUSET" >> "$LAUNCH_OUT" 2>&1
RC=$?

echo "$RC" > "$RC_FILE"
echo "=== SO3DR_STAGE2R DAEMON END rc=$RC $(date -u +%Y%m%dT%H%M%SZ) base=$BASE rcfile=$RC_FILE ===" | tee -a "$LAUNCH_OUT"
exit $RC
