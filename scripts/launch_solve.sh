#!/usr/bin/env bash
# launch_solve.sh -- the ONLY sanctioned way to start a long solve.
#
#   ./launch_solve.sh --name <tag> --case <dir> --expect <artifact> -- <command...>
#
# It does four things the caller cannot forget to do:
#   1. runs case_preflight.sh and REFUSES to launch if it fails
#   2. launches the command detached, recording its real PID
#   3. arms a collector at launch that writes a completion record when the PID
#      dies -- so the result survives the caller's turn ending
#   4. registers the job so `launch_solve.sh --check` can tell whether an
#      agent's "finished" claim is true
#
# WHY THIS EXISTS (D12). The agent-exits-while-solver-runs pattern recurred
# THREE TIMES BEFORE the L-5 rule was written and THREE MORE TIMES AFTER --
# the ladder agent twice, the DPW agent once, and the F4 agent once. Discipline
# demonstrably does not fix it, so the responsibility moves out of the agent's
# head and into the launcher. An agent may still forget; the harness cannot.
set -u

REG="${SOLVE_REGISTRY:-/home/ubuntu/Certonomous/demo-output/website/solve_registry}"
mkdir -p "$REG"

# ---- --check mode: is any registered job still alive? ---------------------
if [ "${1:-}" = "--check" ]; then
    live=0
    for j in "$REG"/*.job; do
        [ -e "$j" ] || continue
        # shellcheck disable=SC1090
        . "$j"
        if kill -0 "$JOB_PID" 2>/dev/null; then
            echo "LIVE   $JOB_NAME (pid $JOB_PID, started $JOB_START) -> $JOB_CASE"
            live=1
        fi
    done
    [ "$live" = "0" ] && echo "no live registered solves"
    exit $live
fi

NAME=""; CASE="."; EXPECT=""
while [ $# -gt 0 ]; do
    case "$1" in
        --name)   NAME="$2"; shift 2 ;;
        --case)   CASE="$2"; shift 2 ;;
        --expect) EXPECT="$2"; shift 2 ;;
        --)       shift; break ;;
        *)        echo "unknown arg: $1"; exit 2 ;;
    esac
done
[ -n "$NAME" ] || { echo "FAIL: --name is required"; exit 2; }
[ $# -gt 0 ]   || { echo "FAIL: no command given after --"; exit 2; }

# ---- 1. preflight gate ----------------------------------------------------
PF=/home/ubuntu/Certonomous/scripts/case_preflight.sh
if [ -x "$PF" ] && [ -d "$CASE" ]; then
    if ! "$PF" "$CASE" --quiet; then
        echo "REFUSING TO LAUNCH: $CASE failed preflight. Fix it, do not override."
        exit 1
    fi
fi

STAMP=$(date -u +%Y%m%dT%H%M%SZ)
LOG="$REG/${NAME}_${STAMP}.log"
JOB="$REG/${NAME}_${STAMP}.job"
REC="$REG/${NAME}_${STAMP}.done"

# ---- 2. launch detached, capture the REAL pid -----------------------------
setsid nohup "$@" > "$LOG" 2>&1 < /dev/null &
PID=$!
cat > "$JOB" <<EOF
JOB_NAME="$NAME"
JOB_PID=$PID
JOB_CASE="$CASE"
JOB_START="$STAMP"
JOB_LOG="$LOG"
JOB_EXPECT="$EXPECT"
EOF

# ---- 3. arm the collector AT LAUNCH, not afterwards ------------------------
# It outlives the caller: it is setsid'd and writes the completion record
# itself, so a turn ending cannot orphan the result.
setsid nohup bash -c '
    while kill -0 '"$PID"' 2>/dev/null; do sleep 15; done
    {
        echo "job:      '"$NAME"'"
        echo "pid:      '"$PID"'"
        echo "started:  '"$STAMP"'"
        echo "finished: $(date -u +%Y%m%dT%H%M%SZ)"
        echo "case:     '"$CASE"'"
        if [ -n "'"$EXPECT"'" ]; then
            if [ -e "'"$EXPECT"'" ]; then echo "expected_artifact: PRESENT ('"$EXPECT"')"
            else echo "expected_artifact: MISSING ('"$EXPECT"') -- process exited without producing it"; fi
        fi
        echo "--- last 25 log lines ---"
        tail -25 "'"$LOG"'" 2>/dev/null
    } > "'"$REC"'"
    rm -f "'"$JOB"'"
' >/dev/null 2>&1 </dev/null &
disown 2>/dev/null || true

echo "launched $NAME pid=$PID"
echo "  log:       $LOG"
echo "  collector: armed (writes $REC on exit)"
[ -n "$EXPECT" ] && echo "  expects:   $EXPECT"
exit 0
