#!/bin/bash
# launch_k2f.sh -- K2f launcher.  Registration sections 11 and 16.
#
# WHY THIS FILE ASSERTS AND K2d's DID NOT
# ---------------------------------------
# launch_k2d.sh:7 read `GUARD_S="$3"`.  It computed no guard and ASSERTED
# NOTHING about the one it was handed.  A retired watcher passed 8034 by hand
# (RETIRED_2026-09-11/watch_l3.sh:46-47) -- 2.52x tighter than the registered
# 20,250 s and at half the registered ranks -- and K2d_L3 died at 33 % of its
# iterations having written nothing at all.  L1, one level earlier, had used the
# registered value exactly, so nothing but the caller changed.
#
# Here the registered table below is the ONLY source of ranks and guard, and a
# handed pair that does not match its level's row is REFUSED at exit 2.
# This file is PINNED by the registration's section 15 freeze block; K2d's
# launcher was not, and it is the file that accepted the hand-passed value.
#
#   ./launch_k2f.sh <CASE> <RANKS> <GUARD_S> [--alt]
#   ./launch_k2f.sh --check-only <CASE> <RANKS> <GUARD_S> [--alt]   # assert, do not launch
#
# --alt selects the C-DECOMP row (registration section 4.2): the same mesh at a
# DIFFERENT rank count, which separates "the cycle is a property of the case"
# from "the cycle is a property of the parallel path".
#
# EXIT MAP (registration section 9.5): 0 OK, 1 FAIL, 2 REFUSE.
# The exit code does not carry a verdict.
#
# NICE: deliberately absent.  Registration section 18.4 -- core-minutes are
# wall x ranks / 60, so nice does not reduce the work or the wall time of the
# niced process; it makes it yield, INCREASING its own wall time while its ranks
# stay allocated, and the run would bill more core-minutes for identically the
# same computation.  Contention is MEASURED instead (both ClockTime and
# ExecutionTime are recorded) and never silently managed.

set +u; . /usr/lib/openfoam/openfoam2606/etc/bashrc; set -u
set -e

# ============================ THE REGISTERED TABLE ==========================
# Registration section 11, with alt_ranks from section 18.3.  Every guard is
# 3 x POINT at that row's ranks, and a reader can reproduce each one from the
# registered POINT: L1 15.6, L2 104.8, L3 897.2 core-min (contention-free).
#   row = "<ranks> <guard_s>"
reg_row() {  # $1 = case, $2 = "main" | "alt"
  case "$1:$2" in
    K2f_L1:main) echo "4 702"    ;;   # 3 x 15.6  / 4 x 60
    K2f_L1:alt)  echo "2 1404"   ;;   # 3 x 15.6  / 2 x 60
    K2f_L2:main) echo "4 4716"   ;;   # 3 x 104.8 / 4 x 60
    K2f_L2:alt)  echo "8 2358"   ;;   # 3 x 104.8 / 8 x 60
    K2f_L3:main) echo "8 20187"  ;;   # 3 x 897.2 / 8 x 60
    K2f_L3:alt)  echo "4 40374"  ;;   # 3 x 897.2 / 4 x 60  (section 18.3)
    *)           echo ""         ;;
  esac
}

CHECK_ONLY=0
if [ "${1:-}" = "--check-only" ]; then CHECK_ONLY=1; shift; fi
CASE="${1:-}"; RANKS="${2:-}"; GUARD_S="${3:-}"; ROW="main"
[ "${4:-}" = "--alt" ] && ROW="alt"

if [ -z "$CASE" ] || [ -z "$RANKS" ] || [ -z "$GUARD_S" ]; then
  echo "REFUSE: usage: $0 [--check-only] <CASE> <RANKS> <GUARD_S> [--alt]"; exit 2
fi

# ---- THE ASSERTION.  A handed pair that is not the registered row REFUSES. ---
WANT="$(reg_row "$CASE" "$ROW")"
if [ -z "$WANT" ]; then
  echo "REFUSE: $CASE is not a K2f level. The registered levels are K2f_L1, K2f_L2, K2f_L3."
  exit 2
fi
W_RANKS="${WANT% *}"; W_GUARD="${WANT#* }"
if [ "$RANKS" != "$W_RANKS" ] || [ "$GUARD_S" != "$W_GUARD" ]; then
  echo "REFUSE: handed ranks=$RANKS guard=${GUARD_S}s for $CASE ($ROW row),"
  echo "        but the REGISTERED row is ranks=$W_RANKS guard=${W_GUARD}s."
  echo "        The registered table in this file is the only legitimate source"
  echo "        of either number. K2d_L3 was launched on a hand-passed 8034 s"
  echo "        against a registered 20,250 s and lost 535.600 core-minutes."
  exit 2
fi
echo "ASSERT OK: $CASE ($ROW row) ranks=$RANKS guard=${GUARD_S}s matches the registered row."
[ "$CHECK_ONLY" = "1" ] && exit 0

HERE="$(cd "$(dirname "$0")" && pwd)"; cd "$HERE/$CASE"

# clause 7 immediately before arming, from the completion instrument
python3 "$HERE/mark_done_k2f.py" --guard "$HERE/$CASE" >/dev/null || exit 2

# ARM 0/ FROM 0.orig AT LAUNCH -- 0/T is touched last and dates the run, which
# is what the age guard (rule 4 clause 6) compares every field against.
rm -rf 0 && cp -r 0.orig 0 && touch 0/T

cat > system/decomposeParDict <<EOD
FoamFile { version 2.0; format ascii; class dictionary; object decomposeParDict; }
numberOfSubdomains $RANKS;
method scotch;
EOD
decomposePar -force > log.decomposePar 2>&1

# WITNESS captured BEFORE the launch. No absolute time, no slack: the test is a
# STRICT INCREASE against this exact value.
WIT_BEFORE=$(stat -c %Y log.decomposePar)
echo "$WIT_BEFORE" > WITNESS.before

cat > .run_inner.sh <<'EOI'
set +u; . /usr/lib/openfoam/openfoam2606/etc/bashrc; set -u
cd "$1"; RANKS="$2"; GUARD_S="$3"
T0=$(date +%s)
# rc captured INSIDE the wrapper. `setsid timeout cmd` exits 0 for EVERY
# outcome, so an rc captured around the setsid line is meaningless.
timeout "$GUARD_S" mpirun -np "$RANKS" buoyantBoussinesqSimpleFoam -parallel > log.solve 2>&1
RC=$?
T1=$(date +%s); WALL=$((T1-T0))
# A PARALLEL run leaves its fields in processor*/<t>/, so the case root has NO
# time directory and rule 4 clauses 3 and 4 CANNOT pass. Reconstruct before
# writing STATUS. Post-processing, not a grading-path change: the fields are
# this run's and they postdate 0/T, so the age guard still binds.
if [ "$RC" = "0" ]; then reconstructPar -latestTime > log.reconstructPar 2>&1 || true; fi
CM=$(python3 -c "print(f'{$WALL*$RANKS/60:.3f}')")
# CONTENTION IS MEASURED, NOT MANAGED (registration section 18.4): record the
# solver's own ClockTime and ExecutionTime so the factor is a number in STATUS
# rather than an inference from wall time.
EX=$(grep -oE 'ExecutionTime = [0-9.]+' log.solve | tail -1 | grep -oE '[0-9.]+$' || echo "")
CL=$(grep -oE 'ClockTime = [0-9.]+'     log.solve | tail -1 | grep -oE '[0-9.]+$' || echo "")
# A trip is a FINDING and is triaged; it is NEVER labelled from the exit code
# alone. K2d wrote note=HANG_GUARD_TRIPPED mechanically on rc=124 for a solver
# that was working at the instant it died.
NOTE=clean
[ "$RC" = "124" ] && NOTE=GUARD_TRIPPED_TRIAGE_REQUIRED
[ "$RC" != "0" ] && [ "$RC" != "124" ] && NOTE=SOLVER_NONZERO_EXIT
{ echo "case=$(basename "$1")"; echo "rc=$RC"; echo "wall_s=$WALL"
  echo "ranks=$RANKS"; echo "core_min=$CM"; echo "timeout_s=$GUARD_S"
  echo "execution_time_s=$EX"; echo "clock_time_s=$CL"
  echo "solver=buoyantBoussinesqSimpleFoam"; echo "note=$NOTE"
  echo "ended_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } > "../STATUS.$(basename "$1")"
EOI
chmod +x .run_inner.sh
setsid bash .run_inner.sh "$PWD" "$RANKS" "$GUARD_S" </dev/null >.run_outer.out 2>&1 &
echo $! > PIDS.launcher
echo "LAUNCHED pid=$(cat PIDS.launcher) cwd=$PWD ranks=$RANKS guard=${GUARD_S}s row=$ROW"
