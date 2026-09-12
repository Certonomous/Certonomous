#!/bin/bash
# CRM WING-ALONE L2, M=0.85 -- LAUNCH WHEN THE MRF RANKS ARE CONFIRMED GONE.
#
# IT NEVER KILLS AND IT NEVER SIGNALS ANOTHER TEAM'S PROCESS.  It only READS /proc.
#
# WHY /proc AND NOT THE MRF LOG.  The cfd-supervisor's constraint: the ranks are not ours
# until they are CONFIRMED GONE -- not when the log prints End, not when we expect it.  The
# MRF lane grades on those ranks' output and a premature launch collides with it.
#
# PID REUSE IS HANDLED.  A bare `-d /proc/<pid>` test is wrong: Linux recycles pids, so a
# NEW process can occupy an old number and look like MRF still running -- or, worse, the
# check could pass while a recycled pid points somewhere else.  A rank counts as GONE when
# /proc/<pid> is absent OR its cwd is no longer the MRF case.  Identity, never the number.
#
# NO CLOCK AND NO SPEND TRIGGER.  It waits on process identity and MemAvailable, both
# hardware/ownership facts.  Sanaa has ruled three times that no run stops on budget or clock.
# rc IS CAPTURED INSIDE THIS WRAPPER -- `setsid timeout cmd` exits 0 for every outcome.
set -u
CASE="$1"; RANKS="$2"; MIN_AVAIL_GIB="$3"
MRF_DIR="/home/ubuntu/Certonomous/verification/runs/navier_class/MRF/R2/ET8000/fine"
MRF_PIDS="2200481 2200482 2200483 2200484 2200485 2200486"
S="$CASE/STATUS.solve"; LOG="$CASE/LAUNCH.log"
say() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >> "$LOG"; }
say "ARMED case=$CASE ranks=$RANKS need_avail=${MIN_AVAIL_GIB}GiB (READS /proc ONLY; NEVER SIGNALS; no clock or spend trigger)"

# ---- 1. wait for every MRF rank to be GONE BY IDENTITY ----------------------
N=0
while true; do
  ALIVE=0
  for p in $MRF_PIDS; do
    if [ -d "/proc/$p" ]; then
      CWD=$(readlink "/proc/$p/cwd" 2>/dev/null || echo "")
      [ "$CWD" = "$MRF_DIR" ] && ALIVE=$((ALIVE+1))
    fi
  done
  [ "$ALIVE" -eq 0 ] && { say "ALL SIX MRF RANKS CONFIRMED GONE by /proc cwd identity after $N readings. The ranks are ours."; break; }
  N=$((N+1))
  [ $((N % 10)) -eq 1 ] && say "WAITING $ALIVE of 6 MRF ranks still live in $MRF_DIR (reading $N). Not signalling; just waiting."
  sleep 60
done

# ---- 2. memory, re-read at the moment of launch -----------------------------
avail=$(free -g | awk '/^Mem:/{print $7}')
if [ "$avail" -lt "$MIN_AVAIL_GIB" ]; then
  { echo "VERDICT=BLOCKED"; echo "reason=memory"; echo "available_GiB=$avail";
    echo "required_GiB=$MIN_AVAIL_GIB"; echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } > "$S"
  echo "80" > "$CASE/solve_rc"; say "BLOCKED on memory: ${avail} < ${MIN_AVAIL_GIB} GiB. Refusing rather than risking an OOM kill on another team."; exit 80
fi

# ---- 3. S5: never launch onto an existing result ----------------------------
for e in "$CASE"/[0-9]*; do
  b=$(basename "$e")
  if [ "$b" != "0" ] && [ -e "$e" ]; then
    { echo "VERDICT=BLOCKED"; echo "reason=S5_time_dir_present"; echo "entry=$b"; } > "$S"
    echo "81" > "$CASE/solve_rc"; say "BLOCKED: time dir $b present. Never clearing a directory."; exit 81
  fi
done

set +u; source /usr/lib/openfoam/openfoam2606/etc/bashrc '' > "$CASE/log.foam_source" 2>&1; SRC=$?; set -u
[ "$SRC" -ne 0 ] && { echo "91" > "$CASE/solve_rc"; say "BLOCKED: foam source rc=$SRC"; exit 91; }
cd "$CASE" || { echo "90" > "$CASE/solve_rc"; exit 90; }

# The age guard (rule 4) dates the run from 0/ -- touched LAST before the solver.
touch 0/U 0/p 0/T 0/k 0/omega 0/nut 0/alphat
{ echo "started_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo "ranks=$RANKS";
  echo "available_GiB_at_launch=$avail"; } > "$S"

TS0=$(date +%s)
/usr/bin/time -v -o time.rhoSimpleFoam mpirun -np "$RANKS" rhoSimpleFoam -parallel > log.rhoSimpleFoam 2>&1; RC=$?
TS1=$(date +%s)
SPEAK=$(grep "Maximum resident set size" time.rhoSimpleFoam | grep -oE "[0-9]+$")
{ echo "rhoSimpleFoam_rc=$RC"; echo "solver_wall_s=$((TS1-TS0))"; echo "solver_ranks=$RANKS";
  echo "solver_core_min=$(echo "($TS1-$TS0)*$RANKS/60" | bc -l)";
  echo "solver_peak_rss_kB=${SPEAK:-UNMEASURED}"; } >> "$S"
say "SOLVER EXITED rc=$RC after $((TS1-TS0)) s"
if [ "$RC" -ne 0 ]; then echo "$RC" > solve_rc; exit "$RC"; fi

TR0=$(date +%s)
reconstructPar -latestTime > log.reconstructPar 2>&1; RC=$?
TR1=$(date +%s)
{ echo "reconstructPar_rc=$RC"; echo "reconstructPar_wall_s=$((TR1-TR0))";
  echo "reconstructPar_ranks=1   # SERIAL";
  echo "total_core_min=$(echo "(($TS1-$TS0)*$RANKS + ($TR1-$TR0)*1)/60" | bc -l)   # SUM OF PHASES at their OWN rank counts";
  echo "finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } >> "$S"
if [ "$RC" -ne 0 ]; then echo "$RC" > solve_rc; exit "$RC"; fi
echo "0" > solve_rc
say "COMPLETE rc=0"
exit 0
