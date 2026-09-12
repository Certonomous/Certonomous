#!/bin/bash
# SUBOFF_A1 -- SOLVE ONE LEVEL, DETACHED AND DURABLY.
#
# rc IS CAPTURED INSIDE THIS WRAPPER, from each utility.  `setsid timeout cmd`
# exits 0 for EVERY outcome, so an rc captured around the setsid line is always a
# lie; this script is the thing setsid launches, and it writes its own rc to disk.
#
# THE MEMORY GATE IS PART OF THE LAUNCH, NOT A COURTESY.  Other teams' multi-day
# solves live on this box and the OOM killer selects on RSS without regard to
# ownership.  If `available` memory is below MIN_AVAIL_GIB at launch, this script
# REFUSES and writes BLOCKED -- it does not try and hope.
#
# S5 (pre-registration 7): a time directory or a previous solver artifact present
# at launch => REFUSE.  Never clear the directory.
set -u
CASE="$1"; RANKS="$2"; MIN_AVAIL_GIB="$3"
S="$CASE/STATUS.solve"

avail=$(free -g | awk '/^Mem:/{print $7}')
if [ "$avail" -lt "$MIN_AVAIL_GIB" ]; then
  { echo "VERDICT=BLOCKED"; echo "reason=memory"; echo "available_GiB=$avail";
    echo "required_GiB=$MIN_AVAIL_GIB";
    echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } > "$S"
  echo "80" > "$CASE/solve_rc"; exit 80
fi

for e in "$CASE"/[0-9]* ; do
  b=$(basename "$e")
  if [ "$b" != "0" ] && [ -e "$e" ]; then
    { echo "VERDICT=BLOCKED"; echo "reason=S5_time_dir_present"; echo "entry=$b"; } > "$S"
    echo "81" > "$CASE/solve_rc"; exit 81
  fi
done
if [ -e "$CASE/log.simpleFoam" ] || [ -e "$CASE/postProcessing" ]; then
  { echo "VERDICT=BLOCKED"; echo "reason=S5_solver_artifact_present"; } > "$S"
  echo "81" > "$CASE/solve_rc"; exit 81
fi

set +u
source /usr/lib/openfoam/openfoam2606/etc/bashrc '' > "$CASE/log.foam_bashrc_source.solve" 2>&1
SRC=$?
set -u
if [ "$SRC" -ne 0 ]; then
  { echo "VERDICT=BLOCKED"; echo "reason=foam_source"; echo "rc=$SRC"; } > "$S"
  echo "91" > "$CASE/solve_rc"; exit 91
fi

cd "$CASE" || { echo "90" > "$CASE/solve_rc"; exit 90; }

# The age guard (rule 4) dates the run from 0/ -- touch it LAST before the solver,
# so every field at endTime must be strictly newer than it.
touch 0/U 0/p 0/k 0/omega 0/nut
{ echo "started_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo "ranks=$RANKS";
  echo "available_GiB_at_launch=$avail"; } > "$S"
T0=$(date +%s)

decomposePar -force > log.decomposePar.solve 2>&1; RC=$?
echo "decomposePar_rc=$RC" >> "$S"
if [ "$RC" -ne 0 ]; then echo "$RC" > solve_rc; exit "$RC"; fi

mpirun -np "$RANKS" simpleFoam -parallel > log.simpleFoam 2>&1; RC=$?
echo "simpleFoam_rc=$RC" >> "$S"
T1=$(date +%s)
{ echo "solver_wall_s=$((T1-T0))";
  echo "solver_core_min=$(echo "($T1-$T0)*$RANKS/60" | bc -l)"; } >> "$S"
if [ "$RC" -ne 0 ]; then echo "$RC" > solve_rc; exit "$RC"; fi

reconstructPar -latestTime > log.reconstructPar.solve 2>&1; RC=$?
echo "reconstructPar_rc=$RC" >> "$S"
if [ "$RC" -ne 0 ]; then echo "$RC" > solve_rc; exit "$RC"; fi

T2=$(date +%s)
{ echo "total_wall_s=$((T2-T0))";
  echo "total_core_min=$(echo "($T2-$T0)*$RANKS/60" | bc -l)"
  echo "finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } >> "$S"
echo "0" > solve_rc
exit 0
