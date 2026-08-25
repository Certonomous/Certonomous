#!/bin/bash
# ===========================================================================
# VMFL033 -- Viscous Heating in an Annulus.  LAUNCHER.
#
# NO `set -u`.  REASON, MEASURED: OpenFOAM v2606's etc/bashrc dereferences
# WM_PROJECT_DIR at line 184 BEFORE assigning it, so `set -u` aborts the source
# with rc 127 and no solver ever starts.  `set -e` is ALSO not relied on: it
# does not gate at a Bash tool top level nor inside `( set -e; ... )`, so EVERY
# check below gates explicitly with `|| { echo ABORT...; exit 1; }`.
#
# Carries the full PREREG_TEMPLATE non-droppable list:
#   Amendment 2 -- launch-time freeze verification of prereg AND comparator
#   Amendment 3 -- cap enforcement in the EXECUTABLE path, per level, by the
#                  general formula timeout_s = remaining_core_min*60/RANKS
#   Amendment 5 -- required fields asserted as the CONSUMER needs them,
#                  intersected with the closure actually named, phi excluded
#   plus: endTime % writeInterval == 0 AND a field dir AT endTime
# ===========================================================================
REPO=/home/ubuntu/Certonomous
CASE=$REPO/cases/ansys_verification/VMFL033
RUNROOT=$REPO/verification/runs/ansys_verification/VMFL033
PREREG=cases/ansys_verification/VMFL033/PREREGISTRATION.md
GRADER=cases/ansys_verification/VMFL033/grade_vmfl033.py
ENDTIME=20000
WRITEINTERVAL=20000
RANKS=1

MODE="${1:-graded}"          # graded | smoke

cd $REPO || { echo "ABORT: cannot cd $REPO"; exit 1; }

# --------------------------------------------------- AMENDMENT 2: the freeze
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
LEVELS="L1_nr32:32:5 L2_nr64:64:8 L3_nr128:128:15"

if [ "$MODE" = "smoke" ]; then
    # AMENDMENT 3 item 6: the smoke test EXERCISES THIS LAUNCHER, not the solver in a
    # bypass environment.  It runs the SMALLEST level for 20 iterations in a scratch
    # root and PRINTS NO FIELD VALUE, so it can create no pre-freeze observation.
    RUNROOT=/tmp/claude-1000/-home-ubuntu-Certonomous/64b13819-ff95-4d4d-a50f-3720bab19084/scratchpad/vmfl033_smokeroot
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

  # ---- endTime must be an EXACT multiple of writeInterval, checked BEFORE the solve
  python3 -c "
import sys
et,wi=$ENDTIME,$WRITEINTERVAL
if wi<=0 or et % wi != 0:
    sys.exit(1)
" || { echo "ABORT[$NAME]: endTime $ENDTIME is not an exact multiple of writeInterval $WRITEINTERVAL -- the run would write NO gradeable output"; exit 1; }

  ( cd $D && blockMesh > log.blockMesh 2>&1 ) || { echo "ABORT[$NAME]: blockMesh failed"; exit 1; }
  ( cd $D && checkMesh > log.checkMesh 2>&1 ) || { echo "ABORT[$NAME]: checkMesh failed"; exit 1; }
  grep -q "Mesh OK" $D/log.checkMesh || { echo "ABORT[$NAME]: checkMesh did not report Mesh OK"; exit 1; }

  # ---- AMENDMENT 3 item 5: mesh birth certificate, read off the MESH, never assumed
  ( cd $D && postProcess -func writeCellCentres -time 0 > log.writeCellCentres0 2>&1 ) \
      || { echo "ABORT[$NAME]: writeCellCentres at time 0 failed"; exit 1; }
  python3 - "$D" > $D/MESH_BIRTH_CERTIFICATE.txt <<'PYBC' || { echo "ABORT[$NAME]: birth certificate failed"; exit 1; }
import math, re, sys, os
d = sys.argv[1]
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
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

  # ---- AMENDMENT 3 item 2: cap in the EXECUTABLE path, PER LEVEL
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

  # ---- a field directory must EXIST at endTime
  [ -d "$D/$ENDTIME" ] || { echo "ABORT[$NAME]: no field directory at endTime $ENDTIME -- the run was clean and wrote NOTHING gradeable"; exit 1; }

  # ---- AMENDMENT 5: assert what the CONSUMER needs, intersected with the ACTUAL
  #      closure, phi EXCLUDED as solver-generated; REFUSE NAMING THE MISSING FIELD.
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
