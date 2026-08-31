#!/bin/bash
# ===========================================================================
# VMFL033-R2 -- Viscous Heating in an Annulus.  LAUNCHER.
#
# R2 succeeds VMFL033-R1 (row #21, NOT A RESULT).  R1's files are NOT touched.
# R2's ONE substantive setup change: endTime 20000 -> 100000 (a 5x fixed-
# iteration ceiling) so the finest mesh can converge.  Everything staged from
# $CASE/case is BYTE-IDENTICAL to R1.
#
# NO `set -u`.  REASON, MEASURED (carried from R1): OpenFOAM v2606's etc/bashrc
# dereferences WM_PROJECT_DIR before assigning it, so `set -u` aborts the source
# with rc 127.  `set -e` is not relied on either; every check gates explicitly
# with `|| { echo ABORT...; exit 1; }`.
#
# Carries the full non-droppable list from R1:
#   * launch-time freeze verification of prereg AND comparator (HEAD-blob match)
#   * cap enforcement in the EXECUTABLE path, PER LEVEL: timeout_s = cap*60/RANKS
#   * required fields asserted as the CONSUMER needs, intersected with the actual
#     closure, phi excluded
#   * endTime % writeInterval == 0 AND a field dir AT endTime
# ===========================================================================
REPO=/home/ubuntu/Certonomous
CASE=$REPO/cases/ansys_verification/VMFL033-R2
RUNROOT=$REPO/verification/runs/ansys_verification/VMFL033-R2
PREREG=cases/ansys_verification/VMFL033-R2/PREREGISTRATION.md
GRADER=cases/ansys_verification/VMFL033-R2/grade_vmfl033_r2.py
ENDTIME=100000
WRITEINTERVAL=100000
RANKS=1

MODE="${1:-graded}"          # graded | smoke

cd $REPO || { echo "ABORT: cannot cd $REPO"; exit 1; }

# --------------------------------------------------- the freeze verification
H=$(git rev-parse HEAD) || { echo "ABORT: cannot read HEAD"; exit 1; }
PB=$(git rev-parse $H:$PREREG 2>/dev/null) || { echo "ABORT: $PREREG is NOT committed at HEAD -- the freeze must be committed BEFORE compute"; exit 1; }
PD=$(git hash-object $PREREG)               || { echo "ABORT: cannot hash $PREREG"; exit 1; }
GB=$(git rev-parse $H:$GRADER 2>/dev/null)  || { echo "ABORT: $GRADER is NOT committed at HEAD"; exit 1; }
GD=$(git hash-object $GRADER)               || { echo "ABORT: cannot hash $GRADER"; exit 1; }
[ "$PB" = "$PD" ] || { echo "ABORT: pre-registration on disk ($PD) != HEAD blob ($PB)"; exit 1; }
[ "$GB" = "$GD" ] || { echo "ABORT: comparator on disk ($GD) != HEAD blob ($GB)"; exit 1; }
echo "FREEZE VERIFIED  HEAD=$H  prereg=$PB  comparator=$GB"

python3 $GRADER --selftest > /dev/null 2>&1 || { echo "ABORT: comparator --selftest is NOT green"; exit 1; }
echo "COMPARATOR SELFTEST GREEN"

source /usr/lib/openfoam/openfoam2606/etc/bashrc > /dev/null 2>&1
[ -n "$WM_PROJECT_DIR" ] || { echo "ABORT: OpenFOAM environment did not load"; exit 1; }

# ------------------------------------------------------------- the levels --
# PER-LEVEL caps, NOT a shared drawdown: one slow level must never starve a later one.
# Predicted at 5x R1's MEASURED per-level actuals (0.4167/0.6333/1.0167 core-min at
# 20000 iter) = 2.08/3.17/5.08 core-min at 100000 iter.  Caps carry ~3.8x headroom
# each so contention (box load up to ~15/16) or heavier per-iteration I/O at 100000
# iterations cannot make the CAP the thing that kills R2 -- R1 died of too FEW
# iterations, and a cap set too tight would kill R2 the same way for a different reason.
LEVELS="L1_nr32:32:8 L2_nr64:64:12 L3_nr128:128:20"

if [ "$MODE" = "smoke" ]; then
    RUNROOT=/tmp/claude-1000/-home-ubuntu-Certonomous/64b13819-ff95-4d4d-a50f-3720bab19084/scratchpad/vmfl033r2_smokeroot
    rm -rf $RUNROOT
    LEVELS="L1_nr32:32:5"
    ENDTIME=20
    WRITEINTERVAL=20
fi

mkdir -p $RUNROOT || { echo "ABORT: cannot make $RUNROOT"; exit 1; }
cat > $RUNROOT/LAUNCH_RECORD.txt <<EOF
utc            = $(date -u +%Y-%m-%dT%H:%M:%SZ)
mode           = $MODE
HEAD           = $H
prereg_blob    = $PB
comparator_blob= $GB
endTime        = $ENDTIME
writeInterval  = $WRITEINTERVAL
ranks          = $RANKS
EOF

for SPEC in $LEVELS; do
  NAME=${SPEC%%:*};  REST=${SPEC#*:};  NR=${REST%%:*};  CAP=${REST##*:}
  D=$RUNROOT/$NAME
  [ -d "$D" ] && { echo "ABORT: $D already exists -- rule 4's guard refuses a case whose run dir is already there"; exit 1; }
  mkdir -p $D || { echo "ABORT: cannot make $D"; exit 1; }
  cp -r $CASE/case/* $D/ || { echo "ABORT: cannot stage $D"; exit 1; }

  python3 $CASE/make_blockmeshdict.py $NR $D/system/blockMeshDict > /dev/null \
      || { echo "ABORT[$NAME]: blockMeshDict generation failed"; exit 1; }
  sed -e "s/__ENDTIME__/$ENDTIME/" -e "s/__WRITEINTERVAL__/$WRITEINTERVAL/" \
      $D/system/controlDict.template > $D/system/controlDict \
      || { echo "ABORT[$NAME]: controlDict templating failed"; exit 1; }
  rm -f $D/system/controlDict.template

  python3 -c "
import sys
et,wi=$ENDTIME,$WRITEINTERVAL
if wi<=0 or et % wi != 0:
    sys.exit(1)
" || { echo "ABORT[$NAME]: endTime $ENDTIME is not an exact multiple of writeInterval $WRITEINTERVAL -- the run would write NO gradeable output"; exit 1; }

  ( cd $D && blockMesh > log.blockMesh 2>&1 ) || { echo "ABORT[$NAME]: blockMesh failed"; exit 1; }
  ( cd $D && checkMesh > log.checkMesh 2>&1 ) || { echo "ABORT[$NAME]: checkMesh failed"; exit 1; }
  grep -q "Mesh OK" $D/log.checkMesh || { echo "ABORT[$NAME]: checkMesh did not report Mesh OK"; exit 1; }

  ( cd $D && postProcess -func writeCellCentres -time 0 > log.writeCellCentres0 2>&1 ) \
      || { echo "ABORT[$NAME]: writeCellCentres at time 0 failed"; exit 1; }
  python3 - "$D" > $D/MESH_BIRTH_CERTIFICATE.txt <<'PYBC' || { echo "ABORT[$NAME]: birth certificate failed"; exit 1; }
import math, re, sys, os
d = sys.argv[1]
txt = open(os.path.join(d, "0", "C")).read()
txt = re.sub(r"/\*.*?\*/", " ", txt, flags=re.S)
start = txt.index("(", txt.index("List<vector>")) + 1
dep, i = 1, start
while i < len(txt) and dep:
    if txt[i] == "(": dep += 1
    elif txt[i] == ")": dep -= 1
    i += 1
N = r"[-+0-9.eE]+"
tri = re.findall(r"\(\s*(%s)\s+(%s)\s+(%s)\s*\)" % (N, N, N), txt[start:i-1])
rs = [math.hypot(float(a), float(b)) for a, b, c in tri]
if not rs:
    raise SystemExit("no cell centres read")
print("cells_read_from_C = %d" % len(rs))
print("r_min             = %.12g" % min(rs))
print("r_max             = %.12g" % max(rs))
print("NOTE: every radius above is READ BACK from OpenFOAM's own C field.")
print("      Nothing is constructed from nr, dr or (j+1/2).")
PYBC

  TIMEOUT_S=$(python3 -c "print(int($CAP*60/$RANKS))")
  echo "LAUNCH $NAME nr=$NR cap=${CAP} core-min timeout=${TIMEOUT_S}s"
  T0=$(date +%s)
  ( cd $D && timeout ${TIMEOUT_S}s buoyantSimpleFoam > log.buoyantSimpleFoam 2>&1 )
  RC=$?
  T1=$(date +%s)
  WALL=$((T1-T0))
  CORE_MIN=$(python3 -c "print('%.4f' % ($WALL*$RANKS/60.0))")
  REMAIN=$(python3 -c "print('%.4f' % ($CAP - $WALL*$RANKS/60.0))")

  if [ $RC -eq 124 ]; then
      echo "CAP CROSSED[$NAME]: the ${CAP} core-min cap stopped the run at ${WALL}s. Reported, not absorbed."
  fi

  if [ $RC -eq 0 ]; then
      ( cd $D && postProcess -func writeCellCentres -time $ENDTIME > log.writeCellCentres 2>&1 ) \
          || { echo "ABORT[$NAME]: writeCellCentres at endTime failed"; RC=90; }
  fi

  cat > $D/RUN_RC.txt <<EOF
rc                 = $RC
dir                = $D
mode               = $MODE
level              = $NAME
nr                 = $NR
endTime            = $ENDTIME
writeInterval      = $WRITEINTERVAL
wall_s             = $WALL
ranks              = $RANKS
core_min           = $CORE_MIN
cap_core_min       = $CAP
remaining_core_min = $REMAIN
timeout_s_granted  = $TIMEOUT_S
prereg_blob        = $PB
comparator_blob    = $GB
finished_utc       = $(date -u +%Y-%m-%dT%H:%M:%SZ)
EOF

  if [ $RC -ne 0 ]; then
      echo "LEVEL $NAME ENDED rc=$RC after ${WALL}s (${CORE_MIN} core-min) -- a non-zero exit is a FINDING"
      continue
  fi

  [ -d "$D/$ENDTIME" ] || { echo "ABORT[$NAME]: no field directory at endTime $ENDTIME -- the run was clean and wrote NOTHING gradeable"; exit 1; }

  CLOSURE=$(sed -n 's/^ *simulationType *\([A-Za-z]*\) *;.*/\1/p' $D/constant/momentumTransport | head -1)
  [ -n "$CLOSURE" ] || { echo "ABORT[$NAME]: constant/momentumTransport names no simulationType"; exit 1; }
  case "$CLOSURE" in
    laminar)   NEED="T U p p_rgh C" ;;
    kEpsilon)  NEED="T U p p_rgh k epsilon nut C" ;;
    kOmegaSST) NEED="T U p p_rgh k omega nut C" ;;
    *) echo "ABORT[$NAME]: closure '$CLOSURE' has no registered field set -- REFUSED, never guessed"; exit 1 ;;
  esac
  for F in $NEED; do
      [ -f "$D/$ENDTIME/$F" ] || { echo "ABORT[$NAME]: required field '$F' is MISSING at endTime (closure '$CLOSURE' needs: $NEED)"; exit 1; }
  done
  echo "LEVEL $NAME rc=0 wall=${WALL}s ${CORE_MIN} core-min; fields present for closure '$CLOSURE': $NEED"
done

echo "ALL LEVELS DONE ($MODE)"
