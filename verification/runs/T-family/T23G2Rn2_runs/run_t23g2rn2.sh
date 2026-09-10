#!/bin/bash
# T23G2Rn2 detached launcher.  ONE LEVEL PER INVOCATION.  Structural sibling of
# verification/runs/T-family/T23G2Rn_runs/run_t23g2rn.sh, adapted for the FROZEN
# §2ba numerics CORRECTED-successor T23G2Rn2
# (docs/campaigns/T-family/T23G2Rn2_PREREGISTRATION.md, two-commit freeze
# 1/2 9ff29322 / 2/2 6c29b259).
#
# GATE FIRST.  The A2.5 static pre-flight (preflight_gate_t23g2rn2.py) is this
# job's FIRST action and is DEFAULT-DENY: if it exits non-zero, NO SOLVER STARTS.
# That gate now ALSO enforces the §5.3 numerics gate (WRITTEN p_rgh block reads
# tolerance 1e-09 / maxIter 100 / relTol 0.01 / solver GAMG / smoother GaussSeidel).
#
# CAP (CLAUDE.md rule 12): the timeout IS the cap.  An overrun STOPS the run; it
# does not get a new budget and a capped level is NOT restarted with a bigger
# number.  Caps/points from T23G2Rn2_PREREGISTRATION.md §6.
#
# rc is captured INSIDE this wrapper on the line immediately after `wait` on the
# solver child, NEVER around a setsid (setsid timeout cmd exits 0 for every
# outcome; setsid-parent-zero lesson).  The solver runs as a backgrounded child
# ONLY so its pid can be recorded for the whole-rung autograder's kill -0 poll;
# `wait "$SOLVER_PID"` propagates the timeout's real exit code, so `rc=$?` on the
# next line is the genuine solver outcome, exactly as a foreground call would be.
set -u

LEVEL="${1:-}"
RUNS="/home/ubuntu/Certonomous/verification/runs/T-family/T23G2Rn2_runs"
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"
SOLVER="chtMultiRegionSimpleFoam"
RANKS=1                       # §6: ranks = 1 on every level.  NO decomposition.

case "$LEVEL" in
    T23G2Rn2_L1) TIMEOUT_S=3441;  CAP=57.35;    POINT=39.11   ;;
    T23G2Rn2_L2) TIMEOUT_S=19958; CAP=332.64;   POINT=226.80  ;;
    T23G2Rn2_L3) TIMEOUT_S=79739; CAP=1328.98;  POINT=906.12  ;;
    *) echo "REFUSE: level must be T23G2Rn2_L1|T23G2Rn2_L2|T23G2Rn2_L3, got '${LEVEL}'" >&2
       exit 3 ;;
esac

CASE="$RUNS/$LEVEL"

# ---- THE GATE.  FIRST ACTION.  DEFAULT DENY. ------------------------------
python3 "$RUNS/preflight_gate_t23g2rn2.py" "$LEVEL"
GATE_RC=$?
if [ "$GATE_RC" -ne 0 ]; then
    echo "REFUSED BY THE A2.5 PRE-FLIGHT GATE (rc=$GATE_RC). NO SOLVER STARTED." >&2
    exit "$GATE_RC"
fi

[ -f "$FOAM_BASHRC" ] || { echo "REFUSE: no OpenFOAM at $FOAM_BASHRC" >&2; exit 2; }
set +u
# shellcheck disable=SC1090
. "$FOAM_BASHRC" >/dev/null 2>&1 || true
set -u
SOLVER_PATH="$(command -v "$SOLVER" 2>/dev/null || true)"
[ -n "$SOLVER_PATH" ] || { echo "REFUSE: '$SOLVER' NOT RESOLVABLE" >&2; exit 2; }

cd "$CASE" || exit 2

# Re-assert the rule-4 age guard here too (safe run directly, not only behind gate).
[ -e "$CASE/0" ] && { echo "REFUSE: $CASE/0 exists" >&2; exit 2; }
for d in "$CASE"/[1-9]*; do
    [ -d "$d" ] && { echo "REFUSE: time directory $d exists" >&2; exit 2; }
done

cp -r 0.orig 0 || exit 2
# 0/housing/T IS TOUCHED LAST, so it dates the run allowed to produce the
# answer.  Every field at endTime must be NEWER than this file (rule 4 age guard).
touch 0/housing/T

ENDT=$(sed -n 's/^[[:space:]]*endTime[[:space:]]\+\([0-9]\+\);.*/\1/p' system/controlDict | head -1)

{
    echo "case=$LEVEL"
    echo "start_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "ranks=$RANKS"
    echo "decomposition=NONE  # recorded AS AN ABSENCE (§6); decomposePar is not run"
    echo "timeout_s=$TIMEOUT_S"
    echo "cap_core_min=$CAP"
    echo "point_core_min=$POINT"
    echo "endTime=$ENDT   # UNCHANGED from T23G2R (§2.2); §2ba fix is the p_rgh tol/maxIter dials only"
    echo "nproc=$(nproc)"
    echo "loadavg=$(cut -d' ' -f1-3 /proc/loadavg)"
    echo "solver=$SOLVER"
    echo "solver_path=$SOLVER_PATH"
    echo "prereg=docs/campaigns/T-family/T23G2Rn2_PREREGISTRATION.md (FROZEN 9ff29322/6c29b259)"
    echo "preflight_gate=PASS (rc=0) before any solver line, incl. §5.3 numerics gate"
    echo "note=box load recorded BEFORE the solver line, not after"
} > "START.$LEVEL"

T0=$(date +%s)
# Backgrounded ONLY to record the pid for the whole-rung autograder; `wait`
# below restores foreground semantics and captures the real rc on the next line.
timeout "${TIMEOUT_S}s" "$SOLVER" > log.solve 2>&1 &
SOLVER_PID=$!
# PIDS.<LEVEL>: one line, space-separated pids -- the wrapper's own pid ($$) and
# the timeout/solver child pid.  autograde_t23g2rn2.sh reads this file and polls
# every pid with `kill -0`; the level counts as ALIVE until the wrapper exits.
echo "$$ $SOLVER_PID" > "$RUNS/PIDS.$LEVEL"
wait "$SOLVER_PID"
rc=$?                          # <-- IMMEDIATELY after wait: the real solver rc.
T1=$(date +%s)
WALL=$((T1 - T0))
CORE_MIN=$(python3 -c "print('%.4f' % ($WALL * $RANKS / 60.0))")
if [ "$rc" -eq 124 ]; then CAPPED=1; else CAPPED=0; fi

{
    echo "case=$LEVEL"
    echo "rc=$rc"
    echo "wall_s=$WALL"
    echo "ranks=$RANKS"
    echo "core_min=$CORE_MIN"
    echo "cap_core_min=$CAP"
    echo "point_core_min=$POINT"
    echo "timeout_s=$TIMEOUT_S"
    echo "capped=$CAPPED"
    echo "solver=$SOLVER"
    echo "end_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "note=rc captured inside this wrapper on the line after wait on the solver child"
    echo "note=a capped level is NOT restarted with a bigger number (rule 12)"
} > "STATUS.$LEVEL"

# y+ per level: GATED, on every wall patch.  Run in a SCRATCH COPY so no graded
# artifact is written.  Only after a clean solve.
if [ "$rc" -eq 0 ]; then
    SCRATCH="$(mktemp -d)"
    cp -r "$CASE" "$SCRATCH/yp" 2>/dev/null && \
      ( cd "$SCRATCH/yp" && "$SOLVER" -postProcess -func yPlus -region fluid -latestTime \
          > "$CASE/log.yPlus.fluid" 2>&1 ) || true
    rm -rf "$SCRATCH"
fi

exit "$rc"
