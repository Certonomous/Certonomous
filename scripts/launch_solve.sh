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

# ---- 0b. the load this run is about to join ---------------------------------
#
# WHY. A wall clock taken while the box is oversubscribed measures the
# contention, not the work, and the lab has already been bitten: the B-52 rung-7
# record found that a cost basis taken from finer2's WALL clock of 285 s was 35
# percent contention, because that run logs ExecutionTime 183.26 s against
# ClockTime 284 s. Its sibling fine-uq is worse and was never flagged: 167.72 s
# of CPU inside 344 s of wall, 51 percent contention. Both fed planning numbers.
#
# So the record has to carry the conditions. Load alone is a snapshot and does
# not cover the run, so this captures it at BOTH ends, and the collector below
# additionally reads the run's OWN ExecutionTime/ClockTime ratio, which is the
# only figure that covers the whole run rather than an instant of it.
#
# WHAT THE RATIO DOES NOT MEASURE, stated because a bound with an undeclared
# hole is worse than a wider honest one: ExecutionTime/ClockTime detects a
# process that did not get its core. It cannot see memory-bandwidth contention,
# which slows the CPU time itself, so a ratio of 1.0 bounds scheduling
# contention only and is not a certificate that the box was quiet.
CORES=$(nproc 2>/dev/null || echo 0)
RESERVED_CORES=2                       # matches scripts/dispatch_queue.py
USABLE_CORES=$(( CORES > RESERVED_CORES ? CORES - RESERVED_CORES : 0 ))
LOAD_AT_LAUNCH=$(cut -d' ' -f1 /proc/loadavg 2>/dev/null || echo 0)
LIVE_JOBS=0
for j in "$REG"/*.job; do
    [ -e "$j" ] || continue
    ( . "$j"; kill -0 "$JOB_PID" 2>/dev/null ) && LIVE_JOBS=$(( LIVE_JOBS + 1 ))
done
if [ -n "$RANKS" ] && [ "$USABLE_CORES" -gt 0 ]; then
    OVER=$(python3 -c "print(1 if $LOAD_AT_LAUNCH + $RANKS > $USABLE_CORES else 0)" 2>/dev/null || echo 0)
else
    OVER=$(python3 -c "print(1 if $LOAD_AT_LAUNCH > $USABLE_CORES else 0)" 2>/dev/null || echo 0)
fi
if [ "$OVER" = "1" ]; then
    echo "WARNING: load is $LOAD_AT_LAUNCH on $CORES cores ($USABLE_CORES usable,"
    echo "         $LIVE_JOBS registered job(s) live) and this run adds"
    echo "         ${RANKS:-an unstated number of} rank(s). The box is over"
    echo "         capacity, so this run's WALL clock will read the contention."
    echo "         It is recorded, not refused: no concurrency limit has been"
    echo "         ratified, and a launcher enforcing one would be legislating."
fi

# ---- 1. preflight gate ----------------------------------------------------
# THIS GATE USED TO FAIL FALSE. The condition was `[ -x "$PF" ] && [ -d "$CASE" ]`,
# so a preflight script that was present but NOT EXECUTABLE skipped the whole gate
# and the launch proceeded -- silently, with no line in the output saying the case
# had not been checked. That was not hypothetical: `scripts/case_preflight.sh` was
# tracked mode 100644, so EVERY FRESH CLONE of this repo launched without the
# preflight D12 promises "the caller cannot forget". This box masked it because its
# working copy carried the bit locally while the index did not.
#
# The rule the fix encodes: ask whether the check RAN before asking what it found,
# and give "did not run" its own verdict instead of folding it into the pass. An
# absent preflight and a passing preflight are different facts.
PF=/home/ubuntu/Certonomous/scripts/case_preflight.sh
if [ -d "$CASE" ]; then
    PF_HOW=""
    if [ -x "$PF" ]; then
        PF_HOW=exec
    elif [ -f "$PF" ]; then
        # Present but not executable: run it through its interpreter rather than
        # treating a missing mode bit as a clean bill of health.
        PF_HOW=bash
        echo "NOTE: $PF is not executable; running it via bash. Fix its exec bit."
    fi
    case "$PF_HOW" in
        exec)
            if ! "$PF" "$CASE" --quiet; then
                echo "REFUSING TO LAUNCH: $CASE failed preflight. Fix it, do not override."
                exit 1
            fi
            ;;
        bash)
            if ! bash "$PF" "$CASE" --quiet; then
                echo "REFUSING TO LAUNCH: $CASE failed preflight. Fix it, do not override."
                exit 1
            fi
            ;;
        *)
            # The third verdict. Not a pass and not a failure -- unknown, said out
            # loud, because a reader who sees no preflight line otherwise cannot
            # tell "checked and clean" from "never checked". Whether an absent
            # preflight should REFUSE rather than warn is a chief's call and is
            # deliberately not decided here.
            echo "PREFLIGHT NOT RUN: $PF is missing. The case was NOT checked; this is not a pass."
            ;;
    esac
fi

STAMP=$(date -u +%Y%m%dT%H%M%SZ)
EPOCH=$(date -u +%s)
LOG="$REG/${NAME}_${STAMP}.log"
JOB="$REG/${NAME}_${STAMP}.job"
REC="$REG/${NAME}_${STAMP}.done"

# ---- 1.5 lever echo (Verification Charter v1.5 section 9, 2026-08-08) -----
# The four lever classes stock OpenFOAM never echoes -- fvSchemes tokens,
# fvSolution `consistent`, BC types, silent dictionary values -- go into the
# run log at t=0, each file hash-bound by sha256, so levers_verified_active
# is satisfiable at write time instead of failing retroactively. The block
# is fenced; nothing that parses solver output needs to change.
#
# WHERE IT IS EMITTED FROM, AND WHY THAT MOVED (L-45, 2026-08-10). This block
# used to be built HERE, in the launcher, out of the caller-supplied `--case`
# path -- while the command itself ran under `setsid nohup "$@"` in the
# launcher's inherited working directory, with nothing binding the two. A
# mismatched `--case` would have written an echo of dictionaries that DID NOT
# RUN at the head of the log of a solve that did: a manufactured verification,
# indistinguishable downstream from a real one. That is the failure direction
# a verification instrument may never have. It never fired -- every log in
# this registry predates the echo's adoption by twenty hours -- so the channel
# was open and unused, and this closes it before it was ever exercised.
#
# It is now emitted BY THE LAUNCHED PROCESS ITSELF, from that process's own
# working directory, in the same shell that then `exec`s the command. The
# directory is read, never passed; `--case` travels along only so the emitter
# can DISAGREE with it and refuse. One implementation, the canonical one in
# `sdk/chief_engineer/lever_echo.py`, so the shell copy cannot drift from the
# Python one that every record is built with.
#
# THE `exec` IS LOAD-BEARING, not tidiness: it replaces the wrapper shell with
# the solver, so $! below is the solver's REAL pid and not a wrapper's. That
# is L-6, the exact trap this launcher exists to close; `--check`, the
# collector and every kill in this file key on that pid.

# ---- 1.6 the rank count that actually ran (L-40, resource dimension) -------
# `--ranks` is a number the CALLER declares, and the collector below multiplies
# by it: core-minutes = wall x ranks / 60. Nothing used to check it against the
# command. A declared rank count nobody verified is the container runner's rank
# clamp with the clamp taken out -- the cost arithmetic is still wrong and
# still silent, and it feeds every pre-registration, every cost grading and the
# calibration scorecard's measured basis.
#
# This reads the ARGUMENT VECTOR, which is what will be exec'd -- not a string
# to be split. When the command nests a shell (`bash -c "..."`), the real
# invocation is inside a string this cannot see, and the answer is
# UNVERIFIABLE, stated: an unchecked number reported as checked is the whole
# defect, so a null here says so rather than guessing serial.
RANKS_OBSERVED=""
_prev=""
_nested=0
for _a in "$@"; do
    case "$_a" in
        -c) _nested=1 ;;
    esac
    case "$_prev" in
        -np|-n|--np|--n)
            case "$_a" in
                ''|*[!0-9]*) : ;;
                *) RANKS_OBSERVED="$_a" ;;
            esac ;;
    esac
    _prev="$_a"
done
if [ "$_nested" = "1" ]; then
    RANKS_OBSERVED="UNVERIFIABLE"
elif [ -z "$RANKS_OBSERVED" ]; then
    RANKS_OBSERVED=1                     # no mpirun in the vector: serial
fi
if [ -n "$RANKS" ] && [ "$RANKS_OBSERVED" != "UNVERIFIABLE" ] \
   && [ "$RANKS" != "$RANKS_OBSERVED" ]; then
    echo "RANK MISMATCH: --ranks says $RANKS, the command runs $RANKS_OBSERVED."
    echo "         Cost is computed from what RAN ($RANKS_OBSERVED), not from"
    echo "         what was declared, and both are recorded in the run log's"
    echo "         RUNTIME-ENVELOPE block and in the completion record."
fi
# What the cost is actually priced on, so the collector and the record agree.
RANKS_EFFECTIVE="$RANKS_OBSERVED"
[ "$RANKS_EFFECTIVE" = "UNVERIFIABLE" ] && RANKS_EFFECTIVE="$RANKS"

# ---- 2. launch detached, capture the REAL pid -----------------------------
setsid nohup env LEVER_ECHO_DECLARED_CASE="${CASE:-}" \
    LEVER_ECHO_DECLARED_RANKS="${RANKS:-}" \
    LEVER_ECHO_OBSERVED_RANKS="${RANKS_OBSERVED:-}" \
    bash -c 'python3 /home/ubuntu/Certonomous/scripts/lever_echo_emit.py 2>/dev/null || true
exec "$@"' bash "$@" >> "$LOG" 2>&1 < /dev/null &
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
JOB_CORES=$CORES
JOB_USABLE_CORES=$USABLE_CORES
JOB_LOAD_AT_LAUNCH=$LOAD_AT_LAUNCH
JOB_LIVE_JOBS_AT_LAUNCH=$LIVE_JOBS
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
        echo "ranks:    '"${RANKS:-UNSTATED}"' (declared)"
        echo "ranks_observed: '"$RANKS_OBSERVED"'  (read from the argument"
        echo "          vector that was exec'"'"'d; UNVERIFIABLE when the command"
        echo "          nests a shell whose contents this cannot see)"
        echo "ranks_priced_on: '"$RANKS_EFFECTIVE"'  (cost below uses THIS)"
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
        if [ -n "'"$RANKS_EFFECTIVE"'" ]; then
            echo "core_min: $(python3 -c "print(round($WALL_S * '"$RANKS_EFFECTIVE"' / 60.0, 3))" 2>/dev/null || echo UNSTATED)"
        else
            echo "core_min: NOT DERIVABLE (no rank count was given at launch)"
        fi
        # ---- the conditions this cost was measured under ------------------
        # Recorded because a core-minute figure with no load beside it cannot
        # be told apart from a measurement of the queue. See section 0b.
        LOAD_AT_FINISH=$(cut -d" " -f1 /proc/loadavg 2>/dev/null || echo UNSTATED)
        echo "cores:    '"$CORES"' ('"$USABLE_CORES"' usable, 2 reserved)"
        echo "load_at_launch: '"$LOAD_AT_LAUNCH"'  (with '"$LIVE_JOBS"' registered job(s) already live)"
        echo "load_at_finish: $LOAD_AT_FINISH"
        # The runs OWN contention measurement, which covers the whole run
        # rather than an instant of it. OpenFOAM prints CPU and wall side by
        # side on every iteration; the last pair is the total.
        # cut -d" " -f3 rather than a second grep for a number: grep -o on the
        # bare pattern also matches the e and E inside the word ExecutionTime,
        # which this self-test caught before the field ever reached a record.
        CPU_S=$(grep -oE "ExecutionTime = [0-9.]+" "'"$LOG"'" 2>/dev/null | tail -1 | cut -d" " -f3)
        CLOCK_S=$(grep -oE "ClockTime = [0-9.]+" "'"$LOG"'" 2>/dev/null | tail -1 | cut -d" " -f3)
        if [ -n "$CPU_S" ] && [ -n "$CLOCK_S" ]; then
            RATIO=$(python3 -c "print(round($CPU_S / $CLOCK_S, 4)) if $CLOCK_S > 0 else print(0)" 2>/dev/null || echo "")
            echo "solver_cpu_s: $CPU_S   solver_wall_s: $CLOCK_S"
            echo "cpu_to_wall: $RATIO  (1.0 = the process got its core; below 1 the"
            echo "             difference is scheduling contention, not work. It does"
            echo "             NOT see memory-bandwidth contention, so it is a bound"
            echo "             on one kind of contention and not a quiet-box proof.)"
            if [ -n "'"$RANKS_EFFECTIVE"'" ]; then
                echo "core_min_cpu: $(python3 -c "print(round($CPU_S * '"$RANKS_EFFECTIVE"' / 60.0, 3))" 2>/dev/null || echo UNSTATED)  (PRICE ON THIS, not core_min: the"
                echo "             B-52 rung-7 record measured a basis taken from a wall"
                echo "             clock that was 35 percent contention)"
            fi
            VERDICT=$(python3 -c "
r = $RATIO
print(\"USABLE FOR PRICING (cpu_to_wall %.3f)\" % r if r >= 0.95 else
      \"NOT USABLE FOR PRICING: %.1f percent of this wall clock was contention. Quote core_min_cpu, or quote nothing.\" % (100 * (1 - r)))" 2>/dev/null)
            echo "pricing_basis: ${VERDICT:-CANNOT TELL}"
        else
            echo "solver_cpu_s: UNSTATED (the log prints no ExecutionTime/ClockTime pair)"
            echo "pricing_basis: CANNOT TELL -- no CPU time in the log, so this wall"
            echo "               clock cannot be separated from the contention it ran in"
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
