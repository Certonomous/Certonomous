#!/bin/bash
# T23G level T23G_C -- DETACHED LAUNCHER.  Serial, 1 rank.
# CAP (CLAUDE.md rule 12, T23G section 8.2): the timeout IS the cap.  An overrun
# STOPS the run; it does not get a new budget.
set -u

CASE="/home/ubuntu/Certonomous/verification/runs/T-family/T23G_runs/T23G_C"
NAME="T23G_C"
RANKS=1
TIMEOUT_S=1500           # cap 25.0 core-min at 1 rank
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"
SOLVER="chtMultiRegionSimpleFoam"

[ -f "$FOAM_BASHRC" ] || { echo "REFUSE: no OpenFOAM environment at $FOAM_BASHRC" >&2; exit 2; }
set +u
# shellcheck disable=SC1090
. "$FOAM_BASHRC" >/dev/null 2>&1 || true
set -u
SOLVER_PATH="$(command -v "$SOLVER" 2>/dev/null || true)"
[ -n "$SOLVER_PATH" ] || { echo "REFUSE: solver '$SOLVER' is NOT RESOLVABLE after sourcing ${FOAM_BASHRC}." >&2; exit 2; }

cd "$CASE" || exit 2

# Rule 4 age guard: refuse a case that already carries a 0/ or a time directory.
if [ -e "$CASE/0" ]; then
    echo "REFUSE: $CASE/0 already exists -- the age guard cannot date this run" >&2
    exit 2
fi
for d in "$CASE"/[1-9]*; do
    [ -e "$d" ] && { echo "REFUSE: time directory $d already exists" >&2; exit 2; }
done

cp -r 0.orig 0 || exit 2
# 0/housing/T IS TOUCHED LAST, so it dates the run allowed to produce the answer.
# Every field at endTime must be NEWER than this file (mark_done_t23.py:14-22).
touch 0/housing/T

# THE START RECORD, WRITTEN BEFORE THE SOLVER LINE.  The load is recorded when it
# can still mean something; measured after the fact it proves nothing.
{
    echo "case=$NAME"
    echo "start_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "ranks=$RANKS"
    echo "timeout_s=$TIMEOUT_S"
    echo "cap_core_min=25.0"
    echo "point_core_min=7.56"
    echo "endTime=10000   # LEVEL INVARIANT, identical at all three levels"
    echo "nproc=$(nproc)"
    echo "loadavg=$(cut -d' ' -f1-3 /proc/loadavg)"
    echo "solver=$SOLVER"
    echo "solver_path=$SOLVER_PATH"
    echo "prereg=docs/campaigns/T-family/T23G_PREREGISTRATION.md v1.1"
    echo "note=box load recorded BEFORE the solver line, not after"
} > "START.$NAME"

T0=$(date +%s)
timeout "${TIMEOUT_S}s" "$SOLVER" > log.solve 2>&1
rc=$?                                    # <-- IMMEDIATELY after the solver line
T1=$(date +%s)

WALL=$((T1 - T0))
CORE_MIN=$(python3 -c "print('%.4f' % ($WALL * $RANKS / 60.0))")
CAP_CORE_MIN=$(python3 -c "print('%.4f' % ($TIMEOUT_S * $RANKS / 60.0))")
if [ "$rc" -eq 124 ]; then CAPPED=1; else CAPPED=0; fi

{
    echo "case=$NAME"
    echo "rc=$rc"
    echo "wall_s=$WALL"
    echo "ranks=$RANKS"
    echo "core_min=$CORE_MIN"
    echo "cap_core_min=$CAP_CORE_MIN"
    echo "point_core_min=7.56"
    echo "timeout_s=$TIMEOUT_S"
    echo "capped=$CAPPED"
    echo "solver=$SOLVER"
    echo "end_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "note=rc captured inside this wrapper on the line after the solver call, never around a setsid"
    echo "note=a capped level is NOT restarted with a bigger number (rule 12)"
} > "STATUS.$NAME"

# y+ per level, section 7.4: MEASURED and REPORTED, NEVER GATED.  Only after a
# clean solve -- a y+ read off a capped or crashed run would be meaningless.
if [ "$rc" -eq 0 ]; then
    postProcess -func yPlus -region fluid -latestTime > log.yPlus.fluid 2>&1 || true
fi

exit "$rc"
