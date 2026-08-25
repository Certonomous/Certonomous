#!/bin/bash
# F12 ENERGY-BOUND DISCRIMINATOR -- three-arm runner.
# Registered at verification/campaign/F12_ENERGY_BOUND_DISCRIMINATOR_PREREGISTRATION.md,
# commit 54acad46f8b038310cfd4c52218a102d2a83e580,
# blob e976f90a55ef077d623af5d609fbe32d245641d5,
# sha256 23c3e4524cf11301ff2e9e38dc2d9de1b3caad77e49f7ba1c940a8dab7790ca3,
# COMMITTED BEFORE THIS SCRIPT RAN.
#
# GRADES NOTHING. Transient time directories run OUTSIDE the repository.
# Touches no registered case, no gate, no threshold, and NOT the rung-2 interlock.
# `set -e` is NOT relied upon: every step captures its status explicitly.
set -u
REPO=/home/ubuntu/Certonomous
SRC=$REPO/verification/runs/F12_runs/attempt2_coarse_workshop_M0.734_a2.79
ROOT=/home/ubuntu/certonomous-runs/f12_energy_bound_discriminator_2026-08-25
REC=$REPO/verification/runs/F12_runs/energy_bound_discriminator_2026-08-25
PREREG=$REPO/verification/campaign/F12_ENERGY_BOUND_DISCRIMINATOR_PREREGISTRATION.md
PREREG_SHA=23c3e4524cf11301ff2e9e38dc2d9de1b3caad77e49f7ba1c940a8dab7790ca3
PREREG_BLOB=e976f90a55ef077d623af5d609fbe32d245641d5
RUNGS="attempt2_medium_workshop_M0.734_a2.79 attempt2_fine_workshop_M0.734_a2.79 attempt2_medium_tape_M0.730_a2.79 attempt2_medium_farfield2x_M0.734_a2.79"

# ---- 0. THE FREEZE MUST BE THE FILE THAT RAN ------------------------------
GOT=$(sha256sum $PREREG | cut -d' ' -f1)
[ "$GOT" = "$PREREG_SHA" ] || { echo "ABORT: prereg sha drift $GOT"; exit 1; }
BLOB=$(cd $REPO && git rev-parse HEAD:verification/campaign/F12_ENERGY_BOUND_DISCRIMINATOR_PREREGISTRATION.md)
DISK=$(cd $REPO && git hash-object verification/campaign/F12_ENERGY_BOUND_DISCRIMINATOR_PREREGISTRATION.md)
[ "$BLOB" = "$DISK" ] || { echo "ABORT: prereg disk != HEAD ($DISK vs $BLOB)"; exit 1; }
[ "$BLOB" = "$PREREG_BLOB" ] || { echo "ABORT: prereg blob drift $BLOB"; exit 1; }
echo "FREEZE OK  blob $BLOB  sha256 $GOT" | tee $REC/evidence/freeze_verified.txt

# ---- 1. PRE-ASSERT: rungs 2-5 ABSENT, rung 1 fingerprinted ---------------
for d in $RUNGS; do
  if [ -e "$REPO/verification/runs/F12_runs/$d" ]; then echo "ABORT: registered rung dir $d EXISTS"; exit 1; fi
done
echo "PRE-ASSERT: rungs 2-5 ABSENT (test -e, this invocation)" | tee $REC/evidence/rung_absence_before.txt
find $SRC -type f | sort | xargs sha256sum 2>/dev/null | sha256sum > $REC/evidence/rung1_fingerprint_before.txt
[ -s $REC/evidence/rung1_fingerprint_before.txt ] || { echo "ABORT: fingerprint empty"; exit 1; }
echo "rung1 fingerprint before: $(cat $REC/evidence/rung1_fingerprint_before.txt)"

MUST_NOT_CHANGE="system/fvSolution system/fvSchemes system/blockMeshDict system/decomposeParDict \
0/T 0/U 0/p 0/k 0/omega 0/nut 0/alphat \
constant/thermophysicalProperties constant/turbulenceProperties \
constant/polyMesh/points constant/polyMesh/faces constant/polyMesh/owner \
constant/polyMesh/neighbour constant/polyMesh/boundary"

run_arm () {
  ARM=$1; LEVER_FILE=$2
  CASE=$ROOT/$ARM/case
  EV=$REC/evidence/$ARM
  mkdir -p $EV
  echo; echo "================= ARM $ARM ================="

  # rule-4 guard: refuse a case with 0/ or a time dir already present
  if [ -e "$CASE" ]; then echo "ABORT[$ARM]: $CASE already exists -- rule 4 guard"; return 1; fi
  mkdir -p $CASE || { echo "ABORT[$ARM]: mkdir"; return 1; }
  cp -a $SRC/0 $SRC/constant $SRC/system $CASE/ || { echo "ABORT[$ARM]: copy"; return 1; }
  rm -f $CASE/system/controlDict.orig
  NT=$(ls -d $CASE/[0-9]* 2>/dev/null | grep -v '/0$' | wc -l)
  [ "$NT" = "0" ] || { echo "ABORT[$ARM]: $NT time dirs already present"; return 1; }

  # ---- the controlDict output-control delta, common to all arms ----
  cp $CASE/system/controlDict $ROOT/$ARM/controlDict_BEFORE || { echo "ABORT[$ARM]: cd copy"; return 1; }
  sed -i -e 's/^endTime  *6000;/endTime         148;/' \
         -e 's/^writeInterval  *6000;/writeInterval   1;/' \
         -e 's/^purgeWrite  *1;/purgeWrite      0;/' $CASE/system/controlDict || { echo "ABORT[$ARM]: sed cd"; return 1; }
  grep -q '^writeCompression' $CASE/system/controlDict || \
    sed -i 's/^writeFormat  *ascii;/writeFormat     ascii;\nwriteCompression off;/' $CASE/system/controlDict
  diff $ROOT/$ARM/controlDict_BEFORE $CASE/system/controlDict > $EV/controlDict_delta.diff
  grep -qE '^endTime +148;' $CASE/system/controlDict || { echo "ABORT[$ARM]: endTime"; return 1; }
  grep -qE '^writeInterval +1;' $CASE/system/controlDict || { echo "ABORT[$ARM]: writeInterval"; return 1; }
  grep -qE '^purgeWrite +0;' $CASE/system/controlDict || { echo "ABORT[$ARM]: purgeWrite"; return 1; }
  grep -qE '^writeCompression +off;' $CASE/system/controlDict || { echo "ABORT[$ARM]: writeCompression"; return 1; }

  # ---- the arm's own single-line lever ----
  case "$ARM" in
    arm0) : ;;
    arm1) sed -i 's/^    div(phi,e)      \$energy;$/    div(phi,e)      bounded Gauss upwind;/' $CASE/system/fvSchemes || { echo "ABORT[$ARM]: sed lever"; return 1; }
          grep -qE '^    div\(phi,e\)      bounded Gauss upwind;$' $CASE/system/fvSchemes || { echo "ABORT[$ARM]: lever NOT applied"; return 1; }
          grep -qE '^    div\(phi,Ekp\)    \$energy;$' $CASE/system/fvSchemes || { echo "ABORT[$ARM]: div(phi,Ekp) unexpectedly changed"; return 1; } ;;
    arm2) sed -i 's/^        rho             0.05;$/        rho             0.3;/' $CASE/system/fvSolution || { echo "ABORT[$ARM]: sed lever"; return 1; }
          grep -qE '^        rho             0.3;$' $CASE/system/fvSolution || { echo "ABORT[$ARM]: lever NOT applied"; return 1; }
          grep -qE '^        p               0.3;$' $CASE/system/fvSolution || { echo "ABORT[$ARM]: p relaxation unexpectedly changed"; return 1; } ;;
  esac
  if [ -n "$LEVER_FILE" ]; then
    diff $SRC/$LEVER_FILE $CASE/$LEVER_FILE > $EV/lever_THE_ENTIRE_DELTA.diff
    NCH=$(grep -c '^[<>]' $EV/lever_THE_ENTIRE_DELTA.diff)
    [ "$NCH" = "2" ] || { echo "ABORT[$ARM]: lever diff has $NCH changed lines, expected exactly 2 (one < one >)"; return 1; }
  fi

  # ---- byte identity of the 18 files that must not change ----
  : > $EV/case_identity_18.txt
  N_OK=0; N_BAD=0; BADLIST=""
  for f in $MUST_NOT_CHANGE; do
    A=$(sha256sum $SRC/$f 2>/dev/null | cut -d' ' -f1)
    B=$(sha256sum $CASE/$f 2>/dev/null | cut -d' ' -f1)
    if [ -n "$A" ] && [ "$A" = "$B" ]; then echo "IDENTICAL $f $A" >> $EV/case_identity_18.txt; N_OK=$((N_OK+1));
    else echo "DIFFERS   $f src=$A arm=$B" >> $EV/case_identity_18.txt; N_BAD=$((N_BAD+1)); BADLIST="$BADLIST $f"; fi
  done
  echo "identical $N_OK / differ $N_BAD ; differing:$BADLIST" >> $EV/case_identity_18.txt
  if [ -z "$LEVER_FILE" ]; then
    [ "$N_OK" = "18" ] && [ "$N_BAD" = "0" ] || { echo "ABORT[$ARM]: identity $N_OK/18 differ $N_BAD ($BADLIST)"; return 1; }
    echo "CASE IDENTITY 18/18 OK (arm 0 changes NOTHING but controlDict output controls)"
  else
    [ "$N_OK" = "17" ] && [ "$N_BAD" = "1" ] || { echo "ABORT[$ARM]: identity $N_OK/18 differ $N_BAD ($BADLIST)"; return 1; }
    [ "$BADLIST" = " $LEVER_FILE" ] || { echo "ABORT[$ARM]: the differing file is '$BADLIST', not the named lever $LEVER_FILE"; return 1; }
    echo "CASE IDENTITY 17/18 OK; the ONE differing file is the named lever $LEVER_FILE ($NCH-line diff)"
  fi

  # ---- FIRE, rc captured to disk and READ BACK ----
  date -u +%FT%TZ > $EV/START_UTC.txt
  cat /proc/loadavg > $EV/CONTENTION_at_launch.txt
  T0=$(date +%s.%N)
  ( cd $CASE && setsid openfoam2606 rhoSimpleFoam > log.rhoSimpleFoam 2>&1; echo "$?" > RC.txt; sync )
  T1=$(date +%s.%N)
  python3 -c "print(f'{$T1-$T0:.6f}')" > $EV/WALL_S.txt
  cat /proc/loadavg > $EV/CONTENTION_at_end.txt
  date -u +%FT%TZ > $EV/END_UTC.txt
  sync
  RC=$(cat $CASE/RC.txt 2>/dev/null)
  case "$RC" in ''|*[!0-9]*) echo "REFUSED[$ARM]: RC.txt missing/empty/non-integer -- rc is NOT MEASURED"; return 1;; esac
  echo "$RC" > $EV/RC.txt
  cp $CASE/log.rhoSimpleFoam $EV/log.rhoSimpleFoam || { echo "ABORT[$ARM]: log copy"; return 1; }
  echo "$ARM: rc = $RC  wall = $(cat $EV/WALL_S.txt) s  times written = $(ls -d $CASE/[0-9]* 2>/dev/null | wc -l)"

  # ---- post-assert, this invocation ----
  find $SRC -type f | sort | xargs sha256sum 2>/dev/null | sha256sum > $EV/rung1_fingerprint_after.txt
  cmp -s $REC/evidence/rung1_fingerprint_before.txt $EV/rung1_fingerprint_after.txt \
    && echo "$ARM: RUNG-1 FINGERPRINT UNCHANGED" || { echo "ABORT[$ARM]: rung 1 CHANGED"; return 1; }
  for d in $RUNGS; do
    if [ -e "$REPO/verification/runs/F12_runs/$d" ]; then echo "ABORT[$ARM]: registered rung dir $d APPEARED"; return 1; fi
  done
  echo "$ARM: POST-ASSERT OK -- rungs 2-5 still ABSENT (test -e, this invocation)"
  return 0
}

# Arms are selected on the command line so that ARM 0 CAN BE FIRED AND ITS
# FAITHFULNESS (P0) CHECKED BEFORE arms 1 and 2 exist at all -- the freeze's
# control-first rule, enforced by the invocation and not merely by ordering.
mkdir -p $ROOT
[ $# -ge 1 ] || { echo "usage: run_arms.sh arm0|arm1|arm2 [...]"; exit 2; }
FAIL=0
for A in "$@"; do
  case "$A" in
    arm0) run_arm arm0 ""                  || FAIL=1 ;;
    arm1) run_arm arm1 system/fvSchemes    || FAIL=1 ;;
    arm2) run_arm arm2 system/fvSolution   || FAIL=1 ;;
    *) echo "ABORT: unknown arm '$A'"; FAIL=1 ;;
  esac
  [ "$FAIL" = "0" ] || break
done
echo; echo "RUNNER_EXIT=$FAIL"
echo "$FAIL" > $REC/evidence/RUNNER_RC_$1.txt
sync
exit $FAIL
