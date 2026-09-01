#!/bin/bash
# DMR rung R3 (h = 1/240) -- per verification/campaign/DMR_R3_TRIPLE_PREREGISTRATION.md
# frozen 68742cec, BEFORE this script ran.
#
# HARD CAP 35.0 core-min (SS6).  A BREACH STOPS THE RUN and writes R3_CAP_BREACH.txt;
# it does not get a new budget.  core-min = wall_s * ranks / 60, accumulated per step
# with that step's OWN rank count -- serial steps count 1 rank, the solve counts 4.
#
# rc IS MEASURED INSIDE THIS WRAPPER, NEVER AROUND THE setsid LINE.
# `setsid timeout cmd` exits 0 for every outcome, so a caller that reads the setsid
# parent's status learns nothing.  Every step writes its own RC file here and syncs.
#
# GUARD: refuses if the case directory already exists.  A rung is not graded on a
# tree that something else may have written.

R=/home/ubuntu/Certonomous/verification/runs/DMR_runs
CASE=$R/res240
N=240
RANKS=4
CAP_COREMIN=35.0
CAP_CORESEC=2100          # 35.0 * 60

cd "$R" || exit 1

# ---- guard: never write into a populated case -----------------------------
if [ -e "$CASE" ]; then
  echo "REFUSED: $CASE already exists. A rung is not graded on a pre-existing tree." \
    | tee "$R/R3_REFUSED.txt"
  echo 90 > "$R/res240.rc.txt"; sync; exit 90
fi

source /usr/lib/openfoam/openfoam2606/etc/bashrc > /dev/null 2>>"$R/log.r3.sourceerr"
command -v rhoCentralFoam >/dev/null || {
  echo "ABORT: rhoCentralFoam not on PATH after sourcing" | tee "$R/R3_REFUSED.txt"
  echo 91 > "$R/res240.rc.txt"; sync; exit 91; }

USED_CORESEC=0
breach() {
  echo "CAP BREACH: ${USED_CORESEC}s core-seconds > ${CAP_CORESEC} (${CAP_COREMIN} core-min)" \
       "-- R3 STOPPED at step '$1', no new budget" | tee -a "$R/R3_CAP_BREACH.txt"
  echo 9 > "$R/res240.rc.txt"; sync; exit 9
}

# run <label> <ranks> <logfile> -- command follows
step() {
  local label=$1 ranks=$2 log=$3; shift 3
  local remaining=$(( CAP_CORESEC - USED_CORESEC ))
  [ "$remaining" -le 0 ] && breach "$label"
  local budget_wall=$(( remaining / ranks ))
  local s=$(date +%s)
  timeout "${budget_wall}s" "$@" > "$log" 2>&1
  local rc=$?
  local e=$(( $(date +%s) - s ))
  USED_CORESEC=$(( USED_CORESEC + e * ranks ))
  echo "$rc" > "$CASE/RC_${label}.txt" 2>/dev/null || echo "$rc" > "$R/RC_${label}.txt"
  sync
  echo "[$label] rc=$rc wall=${e}s ranks=$ranks used=${USED_CORESEC}core-s" \
    | tee -a "$R/R3_PROGRESS.txt"
  if [ "$rc" -eq 124 ]; then breach "$label (timeout at its cap slice)"; fi
  if [ "$rc" -ne 0 ]; then
    echo "STEP FAILED: $label rc=$rc -- recorded, not softened" | tee -a "$R/R3_PROGRESS.txt"
    echo "$rc" > "$R/res240.rc.txt"; sync; exit "$rc"
  fi
  [ "$USED_CORESEC" -gt "$CAP_CORESEC" ] && breach "$label"
  return 0
}

date -u +%Y%m%dT%H%M%SZ > "$R/res240.t0.txt"; sync

python3 "$R/make_case.py" "$CASE" "$N" > "$R/log.makeCase_r3" 2>&1 || {
  echo "ABORT: make_case.py failed"; echo 92 > "$R/res240.rc.txt"; sync; exit 92; }

cd "$CASE" || exit 1
step blockMesh       1 "$CASE/log.blockMesh"       blockMesh
step checkMesh       1 "$CASE/log.checkMesh"       checkMesh
step setExprFields   1 "$CASE/log.setExprFields"   setExprFields
step decomposePar    1 "$CASE/log.decomposePar"    decomposePar
step rhoCentralFoam  4 "$CASE/log.rhoCentralFoam"  mpirun -np 4 rhoCentralFoam -parallel
step reconstructPar  1 "$CASE/log.reconstructPar"  reconstructPar
step writeCellCentres 1 "$CASE/log.writeCellCentres" postProcess -func writeCellCentres -time 0.2

date -u +%Y%m%dT%H%M%SZ > "$R/res240.t1.txt"
echo 0 > "$R/res240.rc.txt"
printf '%s\n' "$USED_CORESEC" > "$R/res240.coresec.txt"
sync
echo "R3 COMPLETE: used ${USED_CORESEC} core-seconds = $(echo "scale=2; $USED_CORESEC/60" | bc) core-min against a ${CAP_COREMIN} cap" \
  | tee -a "$R/R3_PROGRESS.txt"
