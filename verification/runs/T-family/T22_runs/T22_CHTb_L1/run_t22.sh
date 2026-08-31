#!/bin/bash
# T22_CHTb_L1 -- DETACHED LAUNCHER.  Feasibility solve, serial, 1 rank.
#
# THIS IS A SEPARATE FILE FROM build_t22.py ON PURPOSE.  build_t22.py carries a
# hard refusal on solver names and THAT REFUSAL IS NOT LIFTED: a builder must
# never be able to launch.  Building and launching are two acts under two
# reviews, and putting the launch in its own file is what preserves that, not
# what evades it.
#
# THE setsid TRAP (lab memory, and the reason for the shape below):
#   `setsid timeout cmd` EXITS 0 FOR EVERY OUTCOME.  rc is therefore captured
#   INSIDE this wrapper, on the line immediately after the solver call, and the
#   setsid that detaches this script is never the thing whose status is read.
#
# CAP (CLAUDE.md rule 12): the timeout IS the cap.  An overrun STOPS the run; it
# does not get a new budget.  cap_core_min = TIMEOUT_S * RANKS / 60.
set -u

CASE="/home/ubuntu/Certonomous/verification/runs/T-family/T22_runs/T22_CHTb_L1"
NAME="T22_CHTb_L1"
RANKS=1
TIMEOUT_S=3000                 # cap 50.0 core-min at 1 rank
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"
SOLVER="chtMultiRegionSimpleFoam"

[ -f "$FOAM_BASHRC" ] || { echo "REFUSE: no OpenFOAM environment at $FOAM_BASHRC" >&2; exit 2; }
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
# 0/housing/T IS TOUCHED LAST, so it dates the run that was allowed to produce
# the answer.  Every field at endTime must be NEWER than this file.
touch 0/housing/T

# shellcheck disable=SC1090
. "$FOAM_BASHRC" >/dev/null 2>&1

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
    echo "timeout_s=$TIMEOUT_S"
    echo "capped=$CAPPED"
    echo "solver=$SOLVER"
    echo "end_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "note=rc captured inside this wrapper on the line after the solver call, never around a setsid"
    echo "note=core_min is CONTENDED -- see the load average recorded in START.$NAME"
} > "STATUS.$NAME"

exit "$rc"
