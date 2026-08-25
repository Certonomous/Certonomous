#!/bin/bash
# F12 TERMINAL-DEPARTURE PROBE -- registered at
# verification/campaign/F12_TERMINAL_DEPARTURE_PREREGISTRATION.md, blob
# 118fe0d1e409ce5fd64d284fa2172a8c6e5c7788, sha256
# d155396b5a8bec4059859bc9c3be908a9157411c61ebeba12ae9810968f9292e,
# COMMITTED BEFORE THIS SCRIPT RAN.
#
# GRADES NOTHING. Runs OUTSIDE the repository. Touches no registered case, no
# gate, no threshold, and NOT the rung-2 interlock.
set -u
REPO=/home/ubuntu/Certonomous
SRC=$REPO/verification/runs/F12_runs/attempt2_coarse_workshop_M0.734_a2.79
PB=/home/ubuntu/certonomous-runs/f12_terminal_departure_2026-08-25
EV=$REPO/verification/runs/F12_runs/terminal_departure_2026-08-25/evidence
CASE=$PB/case
PREREG_SHA=d155396b5a8bec4059859bc9c3be908a9157411c61ebeba12ae9810968f9292e

mkdir -p $EV

# ---- 0. the freeze must BE the file that ran -----------------------------
GOT=$(sha256sum $REPO/verification/campaign/F12_TERMINAL_DEPARTURE_PREREGISTRATION.md | cut -d' ' -f1)
[ "$GOT" = "$PREREG_SHA" ] || { echo "ABORT: pre-registration sha drift $GOT"; exit 1; }
BLOB=$(cd $REPO && git rev-parse HEAD:verification/campaign/F12_TERMINAL_DEPARTURE_PREREGISTRATION.md)
DISK=$(cd $REPO && git hash-object verification/campaign/F12_TERMINAL_DEPARTURE_PREREGISTRATION.md)
[ "$BLOB" = "$DISK" ] || { echo "ABORT: prereg disk != HEAD"; exit 1; }
echo "FREEZE OK  blob $BLOB" | tee $EV/freeze_verified.txt

# ---- 1. registered rung roots must be ABSENT, and rung 1 UNTOUCHED --------
for d in attempt2_medium_workshop_M0.734_a2.79 attempt2_fine_workshop_M0.734_a2.79 \
         attempt2_medium_tape_M0.730_a2.79 attempt2_medium_farfield2x_M0.734_a2.79; do
  [ -e "$REPO/verification/runs/F12_runs/$d" ] && { echo "ABORT: $d exists"; exit 1; }
done
find $SRC -type f | sort | xargs sha256sum 2>/dev/null | sha256sum > $EV/rung1_fingerprint_before.txt || { echo ABORT-FP; exit 1; }
echo "PRE-ASSERT OK $(date -u +%FT%TZ)"

# ---- 2. target ABSENT, then compose --------------------------------------
[ -e "$CASE" ] && { echo "ABORT: $CASE already exists -- rule 4 guard"; exit 1; }
mkdir -p $CASE || { echo ABORT-MKDIR; exit 1; }
cp -a $SRC/0 $SRC/constant $SRC/system $CASE/ || { echo ABORT-COPY; exit 1; }
rm -f $CASE/system/controlDict.orig

# ---- 3. byte-identity of the 18 files that MUST NOT change ---------------
: > $EV/case_identity_18.txt
N_OK=0; N_BAD=0
for f in system/fvSolution system/fvSchemes system/blockMeshDict system/decomposeParDict \
         0/T 0/U 0/p 0/k 0/omega 0/nut 0/alphat \
         constant/thermophysicalProperties constant/turbulenceProperties \
         constant/polyMesh/points constant/polyMesh/faces constant/polyMesh/owner \
         constant/polyMesh/neighbour constant/polyMesh/boundary; do
  A=$(sha256sum $SRC/$f 2>/dev/null | cut -d' ' -f1)
  B=$(sha256sum $CASE/$f 2>/dev/null | cut -d' ' -f1)
  if [ -n "$A" ] && [ "$A" = "$B" ]; then echo "IDENTICAL $f $A" >> $EV/case_identity_18.txt; N_OK=$((N_OK+1));
  else echo "DIFFERS   $f src=$A probe=$B" >> $EV/case_identity_18.txt; N_BAD=$((N_BAD+1)); fi
done
echo "identical $N_OK / differ $N_BAD" >> $EV/case_identity_18.txt
[ "$N_OK" = "18" ] && [ "$N_BAD" = "0" ] || { echo "ABORT: case identity $N_OK/18"; exit 1; }
echo "CASE IDENTITY 18/18 OK"

# ---- 4. THE ENTIRE DELTA: four controlDict output-control lines ----------
cp $CASE/system/controlDict $PB/controlDict_BEFORE || { echo ABORT-CD; exit 1; }
sed -i -e 's/^endTime  *6000;/endTime         148;/' \
       -e 's/^writeInterval  *6000;/writeInterval   1;/' \
       -e 's/^purgeWrite  *1;/purgeWrite      0;/' $CASE/system/controlDict || { echo ABORT-SED; exit 1; }
grep -q '^writeCompression' $CASE/system/controlDict || \
  sed -i 's/^writeFormat  *ascii;/writeFormat     ascii;\nwriteCompression off;/' $CASE/system/controlDict
diff $PB/controlDict_BEFORE $CASE/system/controlDict > $EV/controlDict_THE_ENTIRE_DELTA.diff
grep -qE '^endTime +148;' $CASE/system/controlDict || { echo "ABORT: endTime not 148"; exit 1; }
grep -qE '^writeInterval +1;' $CASE/system/controlDict || { echo "ABORT: writeInterval not 1"; exit 1; }
grep -qE '^purgeWrite +0;' $CASE/system/controlDict || { echo "ABORT: purgeWrite not 0"; exit 1; }
grep -qE '^writeCompression +off;' $CASE/system/controlDict || { echo "ABORT: writeCompression not off"; exit 1; }
echo "DELTA OK: $(grep -c '^[<>]' $EV/controlDict_THE_ENTIRE_DELTA.diff) changed lines"

# ---- 5. FIRE, detached, rc captured to disk and READ BACK ----------------
date -u +%FT%TZ > $EV/START_UTC.txt
cat /proc/loadavg > $EV/CONTENTION_at_launch.txt
T0=$(date +%s.%N)
( cd $CASE && setsid openfoam2606 rhoSimpleFoam > log.rhoSimpleFoam 2>&1; echo "$?" > RC.txt; sync )
T1=$(date +%s.%N)
python3 -c "print(f'{$T1-$T0:.6f}')" > $EV/WALL_S.txt
cat /proc/loadavg > $EV/CONTENTION_at_end.txt
date -u +%FT%TZ > $EV/END_UTC.txt

RC=$(cat $CASE/RC.txt 2>/dev/null)
case "$RC" in ''|*[!0-9]*) echo "REFUSED: RC.txt missing/empty/non-integer -- rc is NOT MEASURED"; exit 1;; esac
echo "$RC" > $EV/RC.txt
echo "rc = $RC  wall = $(cat $EV/WALL_S.txt) s"

cp $CASE/log.rhoSimpleFoam $EV/log.rhoSimpleFoam || { echo ABORT-LOGCOPY; exit 1; }
find $SRC -type f | sort | xargs sha256sum 2>/dev/null | sha256sum > $EV/rung1_fingerprint_after.txt
diff $EV/rung1_fingerprint_before.txt $EV/rung1_fingerprint_after.txt >/dev/null \
  && echo "RUNG-1 FINGERPRINT UNCHANGED" || { echo "ABORT: rung 1 CHANGED"; exit 1; }
for d in attempt2_medium_workshop_M0.734_a2.79 attempt2_fine_workshop_M0.734_a2.79 \
         attempt2_medium_tape_M0.730_a2.79 attempt2_medium_farfield2x_M0.734_a2.79; do
  [ -e "$REPO/verification/runs/F12_runs/$d" ] && { echo "ABORT: $d appeared"; exit 1; }
done
echo "POST-ASSERT OK: rungs 2-5 still absent"
echo "times written: $(ls -d $CASE/[0-9]* 2>/dev/null | wc -l)"
