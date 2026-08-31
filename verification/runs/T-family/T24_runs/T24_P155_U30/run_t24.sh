#!/bin/bash
# T24_P155_U30 -- DETACHED LAUNCHER.  T24, serial, 1 rank.
# Gates FROZEN at docs/campaigns/T-family/T24_PREREGISTRATION.md, commit b90574899143.
#
# THIS FILE IS run_t23.sh WITH THREE EDITS: this header; CASE/NAME/TIMEOUT_S; and
# the START.<case> block, which is NOT a new mechanism -- it is T23 section 5.4's
# own registered text, which run_t23.sh never implemented (T23_RESULTS.md 5.2
# reported that divergence rather than smoothing it over).  T24 section 3.5b
# registers it and this launcher writes it.
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

CASE="/home/ubuntu/Certonomous/verification/runs/T-family/T24_runs/T24_P155_U30"
NAME="T24_P155_U30"
RANKS=1
TIMEOUT_S=2700                 # cap 45.0 core-min at 1 rank (T24 5.2), ENACTED
FOAM_BASHRC="/usr/lib/openfoam/openfoam2606/etc/bashrc"
SOLVER="chtMultiRegionSimpleFoam"

# --- 0. THE SOLVER MUST BE REACHABLE.  Ported verbatim in shape from
# run_one_t20.sh:130-138, which launched five T20 cases clean on 2026-08-31.
# LAUNCH 1 OF THIS CASE DIED HERE: `set -u` was in force when the bashrc was
# sourced, and etc/bashrc aborts the shell under `set -u` (WM_PROJECT_DIR
# unbound).  The `>/dev/null 2>&1` swallowed the message, which is why
# launcher.queue.out was 0 bytes.  Three guards, and only these three:
#   (a) refuse if the bashrc file is absent;
#   (b) lift `set -u` across the source, and `|| true` on the source itself;
#   (c) refuse if the solver does not RESOLVE after sourcing -- a guard that
#       makes a future environment failure loud instead of silent.
[ -f "$FOAM_BASHRC" ] || { echo "REFUSE: no OpenFOAM environment at $FOAM_BASHRC" >&2; exit 2; }
set +u
# shellcheck disable=SC1090
. "$FOAM_BASHRC" >/dev/null 2>&1 || true
set -u
SOLVER_PATH="$(command -v "$SOLVER" 2>/dev/null || true)"
[ -n "$SOLVER_PATH" ] || { echo "REFUSE: solver '$SOLVER' is NOT RESOLVABLE after sourcing ${FOAM_BASHRC}. Nothing ran, no STATUS written." >&2; exit 2; }

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

# The bashrc was sourced ABOVE, before the age guard, with `set -u` lifted and
# the solver's resolution checked.  The source that used to sit HERE, under
# `set -u`, is the line that killed launch 1; it is not repeated.

# T24 section 3.5b / 5.5: the load reading is taken BEFORE the solver starts, on
# this box, in this invocation.  After the fact a contended number is
# indistinguishable from a mispredicted one, so section 5.5 registers a
# 1-minute load average above nproc as producing a COST but NOT a calibration row.
{
    echo "case=$NAME"
    echo "start_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "loadavg=$(cut -d' ' -f1-3 /proc/loadavg)"
    echo "nproc=$(nproc)"
    echo "solvers_already_running=$(pgrep -c chtMultiRegionSim || true)"
    echo "note=written BEFORE the solver line; the saturation threshold is loadavg_1min > nproc (T24 5.5)"
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
    echo "timeout_s=$TIMEOUT_S"
    echo "capped=$CAPPED"
    echo "solver=$SOLVER"
    echo "end_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "note=rc captured inside this wrapper on the line after the solver call, never around a setsid"
    echo "note=core_min is CONTENDED -- see the load average recorded in START.$NAME, which THIS launcher writes"
    echo "note=queue_runner.py has clobbered this file across five cases; rc is DERIVED-FROM-LOG at grading (T24 3.5a)"
} > "STATUS.$NAME"

exit "$rc"
