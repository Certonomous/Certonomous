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
#
# AMENDMENT 2026-09-12 -- EVERY PHASE IS PRICED AT ITS OWN TRUE RANK COUNT.
# THE DEFECT THIS REPAIRS, MEASURED ON OUR OWN RECORDS: this script used to price its
# WHOLE T1-T0 window at $RANKS, but `decomposePar` logs `nProcs : 1` and
# `reconstructPar` is serial too.  On the crashed SOLVE_L1 attempt that reported 4.80
# core-min against 1.68 honest -- a 2.86x OVERSTATEMENT -- and every SUBOFF row written
# by this instrument inherited the same bias.  A cost instrument that overstates is not
# 'conservative': it corrupts the calibration ledger in the direction that makes the
# lab's estimates look better than they are.
# Each phase is now timed separately and multiplied by ITS OWN rank count, and
# `total_core_min` is the SUM of the three, not a window times a rank count.
# The legacy window figure is still emitted, under a name that says what it is, so no
# reader can mistake it for the honest total and no old reading silently changes meaning.
#
# PEAK RSS IS RECORDED PER PHASE, from /usr/bin/time -v (the kernel's own high-water
# mark, not a poller that can miss a peak between samples).  The SERIAL phases are the
# ones no rank-derived memory bound covers, so they are exactly the ones worth measuring.
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

TD0=$(date +%s)
/usr/bin/time -v -o time.decomposePar.solve decomposePar -force > log.decomposePar.solve 2>&1; RC=$?
TD1=$(date +%s)
DPEAK=$(grep "Maximum resident set size" time.decomposePar.solve | grep -oE "[0-9]+$")
{ echo "decomposePar_rc=$RC";
  echo "decomposePar_wall_s=$((TD1-TD0))";
  echo "decomposePar_ranks=1   # SERIAL -- the log says nProcs : 1";
  echo "decomposePar_core_min=$(echo "($TD1-$TD0)*1/60" | bc -l)";
  echo "decomposePar_peak_rss_kB=${DPEAK:-UNMEASURED}"; } >> "$S"
if [ "$RC" -ne 0 ]; then echo "$RC" > solve_rc; exit "$RC"; fi

TS0=$(date +%s)
/usr/bin/time -v -o time.simpleFoam.solve mpirun -np "$RANKS" simpleFoam -parallel > log.simpleFoam 2>&1; RC=$?
TS1=$(date +%s); T1=$TS1
SPEAK=$(grep "Maximum resident set size" time.simpleFoam.solve | grep -oE "[0-9]+$")
{ echo "simpleFoam_rc=$RC";
  echo "simpleFoam_wall_s=$((TS1-TS0))";
  echo "simpleFoam_ranks=$RANKS";
  echo "simpleFoam_core_min=$(echo "($TS1-$TS0)*$RANKS/60" | bc -l)";
  echo "simpleFoam_peak_rss_kB=${SPEAK:-UNMEASURED}   # largest single rank, not the sum";
  echo "LEGACY_window_core_min_OVERSTATED=$(echo "($T1-$T0)*$RANKS/60" | bc -l)   # the OLD figure: the whole window priced at RANKS, including the SERIAL decomposePar. Kept only so an old reading is recognisable; it is NOT the cost."; } >> "$S"
if [ "$RC" -ne 0 ]; then echo "$RC" > solve_rc; exit "$RC"; fi

TR0=$(date +%s)
/usr/bin/time -v -o time.reconstructPar.solve reconstructPar -latestTime > log.reconstructPar.solve 2>&1; RC=$?
TR1=$(date +%s)
RPEAK=$(grep "Maximum resident set size" time.reconstructPar.solve | grep -oE "[0-9]+$")
{ echo "reconstructPar_rc=$RC";
  echo "reconstructPar_wall_s=$((TR1-TR0))";
  echo "reconstructPar_ranks=1   # SERIAL";
  echo "reconstructPar_core_min=$(echo "($TR1-$TR0)*1/60" | bc -l)";
  echo "reconstructPar_peak_rss_kB=${RPEAK:-UNMEASURED}"; } >> "$S"
if [ "$RC" -ne 0 ]; then echo "$RC" > solve_rc; exit "$RC"; fi

T2=$(date +%s)
{ echo "total_wall_s=$((T2-T0))";
  echo "total_core_min=$(echo "(($TD1-$TD0)*1 + ($TS1-$TS0)*$RANKS + ($TR1-$TR0)*1)/60" | bc -l)   # SUM OF PHASES, each at ITS OWN rank count -- NOT the window times RANKS";
  echo "LEGACY_total_core_min_OVERSTATED=$(echo "($T2-$T0)*$RANKS/60" | bc -l)   # the OLD arithmetic, kept for recognisability only";
  echo "finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } >> "$S"
echo "0" > solve_rc
exit 0
