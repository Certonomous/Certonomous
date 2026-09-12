#!/bin/bash
# DRIVAER R2 -- launch ONE level's solve under a HARD CAP.
# Adapted from launch_stage_a.sh, which carries no cap.  Registered by
# verification/campaign/DRIVAER_R2_LAYERED_PREREGISTRATION.md §4, §5 Class 3.
#
# rc IS CAPTURED INSIDE THIS WRAPPER.  `setsid timeout cmd` exits 0 for every
# outcome, so an rc read around the setsid line is meaningless.  The cap is
# applied to `mpirun` ITSELF, not to an outer shell: a TERM to an outer shell
# leaves the ranks running and the cap would be a lie.
set -u
ROOT="$1"; NP="$2"; CAP_MIN="$3"; PRED_GIB="$4"
[ -d "$ROOT" ]        || { echo "REFUSE: no such level root $ROOT"; exit 2; }
[ -d "$ROOT/0.orig" ] || { echo "REFUSE: no 0.orig in $ROOT"; exit 2; }
[ -e "$ROOT/0" ]      && { echo "REFUSE: $ROOT/0 exists; a pre-existing 0/ defeats the age guard"; exit 2; }
for d in "$ROOT"/[1-9]*; do
  [ -d "$d" ] && { echo "REFUSE: time directory $d already exists"; exit 2; }
done

# ---- Class 3b: PRE-LAUNCH MEMORY REFUSAL --------------------------------------
AVAIL=$(free -g | awk '/^Mem:/{print $7}')
CEIL=$(( AVAIL - 4 ))
echo "MEMORY GATE: available=${AVAIL} GiB ceiling=${CEIL} GiB predicted=${PRED_GIB} GiB"
if awk -v p="$PRED_GIB" -v c="$CEIL" 'BEGIN{exit !(p>c)}'; then
  echo "BLOCKED: predicted solver peak ${PRED_GIB} GiB > available-4 = ${CEIL} GiB. NOTHING LAUNCHED."
  exit 3
fi

set +u; source /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1; set -u
cd "$ROOT" || exit 2

# 0.orig -> 0 AT LAUNCH: 0/U dates the rule-4 age guard, so it is stamped NOW.
cp -r 0.orig 0
touch 0/U 0/p 0/k 0/omega 0/nut

CAP_S=$(( CAP_MIN * 60 / NP ))            # core-min cap -> wall-second cap at NP ranks
: > RUN_META.txt
{ echo "launched_utc=$(date -u +%FT%TZ)"; echo "cwd=$ROOT"; echo "ranks=$NP"
  echo "cap_core_min=$CAP_MIN"; echo "cap_wall_s=$CAP_S"
  echo "predicted_peak_GiB=$PRED_GIB"; echo "free_g_available_at_launch_GiB=$AVAIL"
  echo "wrapper_pid=$$"; echo "host=$(hostname)"; } >> RUN_META.txt

write_rc () { printf 'rc=%s\n' "$1" > "$ROOT/rc"; printf 'rc=%s\n' "$1" > "$ROOT/RC.txt"; }

S=$(date +%s)
if [ "$NP" -gt 1 ]; then
  cat > system/decomposeParDict <<DPD
FoamFile { version 2.0; format ascii; class dictionary; object decomposeParDict; }
numberOfSubdomains $NP;
method scotch;
DPD
  nice -n 5 decomposePar -force > log.decomposePar 2>&1
  rc=$?; echo "decomposePar rc=$rc" >> RUN_META.txt
  [ $rc -ne 0 ] && { write_rc $rc; exit $rc; }
  echo "solver_started_utc=$(date -u +%FT%TZ)" >> RUN_META.txt
  timeout -k 60 "$CAP_S" nice -n 5 mpirun -np "$NP" simpleFoam -parallel > log.simpleFoam 2>&1
  rc=$?                                   # <-- captured INSIDE the wrapper
  echo "simpleFoam rc=$rc" >> RUN_META.txt
  if [ $rc -eq 0 ]; then
    # -newTimes skips time 0.  Reconstructing 0 would stamp 0/U NEWER than the
    # endTime fields and the rule-4 age guard would then refuse the run.
    nice -n 5 reconstructPar -newTimes > log.reconstructPar 2>&1
    rrc=$?; echo "reconstructPar rc=$rrc" >> RUN_META.txt
    [ $rrc -ne 0 ] && rc=$rrc
  fi
else
  echo "solver_started_utc=$(date -u +%FT%TZ)" >> RUN_META.txt
  timeout -k 60 "$CAP_S" nice -n 5 simpleFoam > log.simpleFoam 2>&1
  rc=$?
  echo "simpleFoam rc=$rc" >> RUN_META.txt
fi
E=$(date +%s); W=$((E-S))
echo "finished_utc=$(date -u +%FT%TZ)" >> RUN_META.txt
echo "wall_s=$W" >> RUN_META.txt
awk -v w="$W" -v n="$NP" 'BEGIN{printf "core_min=%.1f\n", w*n/60.0}' >> RUN_META.txt
if [ "$rc" = "124" ] || [ "$rc" = "137" ]; then
  echo "CAP EXCEEDED: cap ${CAP_MIN} core-min (${CAP_S} s wall at ${NP} ranks), elapsed ${W} s. RUN STOPPED -- NOT A RESULT. No new budget." \
      > "$ROOT/CAP_BREACH.txt"
fi
write_rc $rc
exit $rc
