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

NAME=""; CASE="."; EXPECT=""; ITEM=""; RANKS=""; EST=""
while [ $# -gt 0 ]; do
    case "$1" in
        --name)   NAME="$2"; shift 2 ;;
        --case)   CASE="$2"; shift 2 ;;
        --expect) EXPECT="$2"; shift 2 ;;
        --item)   ITEM="$2"; shift 2 ;;
        --ranks)  RANKS="$2"; shift 2 ;;
        --est)    EST="$2"; shift 2 ;;
        --)       shift; break ;;
        *)        echo "unknown arg: $1"; exit 2 ;;
    esac
done
[ -n "$NAME" ] || { echo "FAIL: --name is required"; exit 2; }
[ $# -gt 0 ]   || { echo "FAIL: no command given after --"; exit 2; }

# ---- 0. attribution: which approved item is this, and what will it cost? ---
#
# WHY THIS IS HERE AND NOT AT APPROVAL. The largest overrun on record is
# 1,175.0 core-minutes against a 120 core-minute estimate, 9.8 times under, and
# the item was at `proposed` the whole time and was never approved. No approval
# was sought, so no budget applied: the compute-budget charter was not bent, it
# was bypassed. A spend gate that fires at approval cannot see that run. The
# only moment every run passes through is this one.
#
# WHAT IT DOES NOT DO YET. It does not refuse, and --item is not required. The
# charter's ceilings are proposed and have never been ratified, and a launcher
# enforcing a number nobody agreed to would be legislating; making --item
# mandatory would also break every caller in flight. So this records and it
# warns. The record is what a ratified ceiling would later bind on:
# `scripts/dispatch_queue.py` counts how many completion records can be
# attributed at all, and before this existed the answer was 0 of 132.
#
# WHY --ranks MATTERS AS MUCH AS --item. Core-minutes are wall seconds times
# MPI ranks over sixty (COMPUTE_BUDGET_CHARTER section 2). Every completion
# record already carried a start and a finish, so wall time was always
# derivable and core-minutes never were.
ATTRIB="UNATTRIBUTED (--item not given)"
if [ -n "$ITEM" ]; then
    ITEM_STATUS=$(python3 - "$ITEM" <<'PY' 2>/dev/null || true
import json, pathlib, sys
item = sys.argv[1]
path = pathlib.Path("/home/ubuntu/Certonomous/demo-output/website/agenda"
                    "/docket.json")
try:
    data = json.loads(path.read_text(encoding="utf-8"))
except Exception as exc:  # a docket we cannot read is a finding, not a crash
    print(f"docket unreadable: {type(exc).__name__}")
    raise SystemExit(0)
rows = data.get("proposals") if isinstance(data, dict) else data
for row in rows or []:
    if isinstance(row, dict) and row.get("id") == item:
        print(f"{row.get('status')}, est_core_min={row.get('est_core_min')}")
        raise SystemExit(0)
print("NOT ON THE DOCKET")
PY
)
    [ -n "$ITEM_STATUS" ] || ITEM_STATUS="lookup failed"
    ATTRIB="$ITEM ($ITEM_STATUS)"
    case "$ITEM_STATUS" in
        approved*) : ;;
        *) echo "WARNING: $ITEM is '$ITEM_STATUS', not approved. The largest" ;
           echo "         overrun on record ran on an unapproved item. This" ;
           echo "         launch is recorded as such, and is not refused." ;;
    esac
else
    echo "WARNING: no --item. This run's cost cannot be attributed to anything"
    echo "         on the docket, which is how the worst overrun went unseen."
fi
if [ -z "$RANKS" ]; then
    echo "WARNING: no --ranks. Core-minutes are wall seconds x ranks / 60, so"
    echo "         without it this run's cost is not derivable from its own"
    echo "         record, however long the record says it took."
fi

# ---- 1. preflight gate ----------------------------------------------------
PF=/home/ubuntu/Certonomous/scripts/case_preflight.sh
if [ -x "$PF" ] && [ -d "$CASE" ]; then
    if ! "$PF" "$CASE" --quiet; then
        echo "REFUSING TO LAUNCH: $CASE failed preflight. Fix it, do not override."
        exit 1
    fi
fi

STAMP=$(date -u +%Y%m%dT%H%M%SZ)
EPOCH=$(date -u +%s)
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
JOB_ITEM="$ITEM"
JOB_RANKS="$RANKS"
JOB_EST="$EST"
JOB_ATTRIB="$ATTRIB"
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
        # Attribution and cost, recorded here because this is the only moment
        # every run passes through. A field is printed even when it is empty,
        # with the word that says so, because an absent line and an unrecorded
        # value are indistinguishable to anything reading this file later.
        echo "item:     '"${ITEM:-UNATTRIBUTED}"'"
        echo "attribution: '"$ATTRIB"'"
        echo "ranks:    '"${RANKS:-UNSTATED}"'"
        echo "est_core_min: '"${EST:-UNSTATED}"'"
        WALL_S=$(( $(date -u +%s) - '"$EPOCH"' ))
        # NOTE: no apostrophes in this block. It lives inside a single-quoted
        # bash -c string, and one would end the string.
        # The collector polls every 15 s, so this is an upper bound within 15 s
        # of the real lifetime of the process, and so is the finished stamp
        # above and every one already in this registry. Stated because a cost
        # figure with an undeclared bias is worse than one with a declared bias,
        # and on a short run 15 s is the whole measurement.
        echo "wall_s:   $WALL_S  (upper bound; the collector polls every 15 s)"
        if [ -n "'"$RANKS"'" ]; then
            echo "core_min: $(python3 -c "print(round($WALL_S * '"$RANKS"' / 60.0, 3))" 2>/dev/null || echo UNSTATED)"
        else
            echo "core_min: NOT DERIVABLE (no rank count was given at launch)"
        fi
        CONV_CHECKER=/home/ubuntu/Certonomous/scripts/check_convergence.py
        CONV_ITERS=""
        if [ -x "$CONV_CHECKER" ] || [ -f "$CONV_CHECKER" ]; then
            # check_convergence.py exits 0/1/2 for CONVERGED/NOT_CONVERGED/
            # CANNOT_TELL -- all three are legitimate VERDICTS, not errors, so
            # a nonzero exit here must NOT be treated as the checker failing.
            # Only a truly empty result (checker crashed before printing
            # anything, e.g. exit 3 usage/IO error with no stdout) counts as
            # an actual failure of the checker itself.
            CONV_LINE=$(python3 "$CONV_CHECKER" "'"$LOG"'" --case "'"$CASE"'" --oneline 2>&1)
            if [ -z "$CONV_LINE" ]; then
                CONV_LINE="CANNOT_TELL: checker produced no output (see stderr, checker may have crashed)"
            fi
            # Pull the converged iteration count (if any) so a run that
            # converged BEFORE its --expect endTime does not get reported as
            # having failed to produce an artifact it was never going to
            # write -- a residualControl-gated run that stops early is a
            # SUCCESS, not a missing result (the same false alarm this
            # project already caught once on F8). Best-effort: silent no-op
            # if the checker errors or the field is absent.
            CONV_ITERS=$(python3 "$CONV_CHECKER" "'"$LOG"'" --case "'"$CASE"'" --json 2>/dev/null \
                | python3 -c "import json,sys
try:
    d=json.load(sys.stdin)
    print(d.get(\"detail\",{}).get(\"iterations_at_convergence\",\"\"))
except Exception:
    print(\"\")" 2>/dev/null)
        fi
        if [ -n "'"$EXPECT"'" ]; then
            if [ -e "'"$EXPECT"'" ]; then
                echo "expected_artifact: PRESENT ('"$EXPECT"')"
            elif [ -n "$CONV_ITERS" ] && [ -e "$(dirname "$(dirname "'"$EXPECT"'")")/$CONV_ITERS/$(basename "'"$EXPECT"'")" ]; then
                echo "expected_artifact: PRESENT AT CONVERGED ITERATION ($(dirname "$(dirname "'"$EXPECT"'")")/$CONV_ITERS/$(basename "'"$EXPECT"'")) -- residualControl stopped the run at $CONV_ITERS, before the --expect path'"'"'s endTime; not missing, converged early"
            else
                echo "expected_artifact: MISSING ('"$EXPECT"') -- process exited without producing it"
            fi
        fi
        if [ -n "${CONV_LINE:-}" ]; then
            echo "convergence: $CONV_LINE"
        else
            echo "convergence: CANNOT_TELL: checker not found at $CONV_CHECKER"
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
