#!/bin/bash
# DMR R3 STEP-0 DIAGNOSTIC driver -- answer-blind negativity locator (NOT graded).
#
# Restarts the FINE (N=240) positivity-successor case R3p from its last healthy
# written field (t = 0.10, decomposed on disk) with a `fieldMinMax` functionObject
# on (T e p rho U), `location yes`, `writeControl timeStep`, and NO NUMERICS CHANGE
# (Minmod reconstruction + maxCo 0.1 retained, Kurganov flux retained), so the
# min/max AND the cell LOCATION of the extremum are recorded EVERY step through the
# failing window.  Its output feeds step0_negativity_reader.py, which reports which
# physical scalar field first goes negative and WHERE -- the L-501 answer-blind
# measurement that selects the mechanism-appropriate lever.
#
# THIS IS A DIAGNOSTIC PROBE, NOT A GRADED TRIPLE MEMBER.  A SIGFPE here (rc 136,
# expected ~t=0.116) is THE MEASUREMENT, not a failure: the driver RECORDS the
# solver rc and proceeds to run the reader regardless.  Because it is a restart
# (startFrom latestTime) it necessarily writes into a case that already carries the
# t=0..0.10 seed; the rule-4 graded-run age guard (fresh answer, 0/T newest) does
# NOT apply to a probe.  The guard this driver DOES enforce: refuse if the STEP-0
# root already exists -- never overwrite a prior diagnostic.
#
# rc IS CAPTURED INSIDE THIS WRAPPER, never around the setsid/timeout line
# (setsid parent returns 0 for every outcome).  Its OWN small hard cap STOPS the
# run with no new budget (rule 12); STEP 0's cap is SEPARATE from the L1 family cap.

set -u
SRC=/home/ubuntu/Certonomous/verification/runs/DMR_R3_POSITIVITY_SUCCESSOR_runs/R3p
R=/home/ubuntu/Certonomous/verification/runs/DMR_R3_STEP0_DIAG_runs
CASE="$R/STEP0"
READER=/home/ubuntu/Certonomous/verification/runs/DMR_runs/step0_negativity_reader.py

RANKS=4
CAP_COREMIN=5.0
CAP_CORESEC=300           # 5.0 * 60 -- STEP-0's OWN small hard cap (separate)

# ---- guard: never overwrite a prior diagnostic ----------------------------
if [ -e "$R" ]; then
  echo "REFUSED: $R already exists. STEP 0 never overwrites a prior diagnostic." \
    | tee "/tmp/step0_refused_$$.txt" 2>/dev/null
  exit 90
fi
if [ ! -d "$SRC/processor0/0.1" ]; then
  echo "REFUSED: restart seed $SRC/processor0/0.1 absent -- cannot restart R3p from t=0.10" >&2
  exit 91
fi

mkdir -p "$R" || exit 1
# read-only copy of the crashed R3p tree (preserves the original evidence)
cp -a "$SRC" "$CASE" || { echo "ABORT: copy of R3p failed" | tee "$R/REFUSED.txt"; exit 92; }
# drop the crashed run's bookkeeping so it cannot be mistaken for this probe's
rm -f "$CASE"/RC_*.txt "$CASE"/log.rhoCentralFoam "$CASE"/successor.*.txt 2>/dev/null

# ---- diagnostic controlDict: restart, per-step writes + fieldMinMax --------
# NO numerics change: only startFrom/writeControl/writeInterval change and a
# functionObject is added.  maxCo 0.1, adjustTimeStep, Euler, Minmod all retained.
cat > "$CASE/system/controlDict" <<'EOF'
FoamFile
{
    version 2.0; format ascii; class dictionary; location "system"; object controlDict;
}

application     rhoCentralFoam;
startFrom       latestTime;
startTime       0;
stopAt          endTime;
endTime         0.2;
deltaT          1e-6;
writeControl    timeStep;
writeInterval   25;
purgeWrite      0;
writeFormat     ascii;
writePrecision  8;
timeFormat      general;
timePrecision   8;
runTimeModifiable true;
adjustTimeStep  yes;
maxCo           0.1;
maxDeltaT       5e-4;

functions
{
    fieldMinMax
    {
        type            fieldMinMax;
        libs            (fieldFunctionObjects);
        fields          (T e p rho U);
        location        yes;
        writeControl    timeStep;
        writeInterval   1;
    }
}
EOF

source /usr/lib/openfoam/openfoam2606/etc/bashrc > /dev/null 2>>"$R/log.sourceerr"
command -v rhoCentralFoam >/dev/null || {
  echo "ABORT: rhoCentralFoam not on PATH after sourcing" | tee "$R/REFUSED.txt"
  echo 93 > "$R/step0.rc.txt"; sync; exit 93; }

USED_CORESEC=0
cd "$CASE" || exit 1

# step <label> <ranks> <logfile> -- command follows.  rc captured HERE.
step() {
  local label=$1 ranks=$2 log=$3; shift 3
  local remaining=$(( CAP_CORESEC - USED_CORESEC ))
  if [ "$remaining" -le 0 ]; then
    echo "CAP BREACH: ${USED_CORESEC}s > ${CAP_CORESEC}s (${CAP_COREMIN} core-min) -- STEP 0 STOPPED at '$label', no new budget" \
      | tee -a "$R/CAP_BREACH.txt"
    echo 9 > "$R/step0.rc.txt"; sync; exit 9
  fi
  local budget_wall=$(( remaining / ranks ))
  local s=$(date +%s)
  timeout "${budget_wall}s" "$@" > "$log" 2>&1
  local rc=$?
  local e=$(( $(date +%s) - s ))
  USED_CORESEC=$(( USED_CORESEC + e * ranks ))
  echo "$rc" > "$CASE/RC_${label}.txt"; sync
  echo "[STEP0/${label}] rc=$rc wall=${e}s ranks=$ranks used=${USED_CORESEC}core-s" \
    | tee -a "$R/PROGRESS.txt"
  echo "$rc"   # emit rc for the caller's inspection
}

date -u +%Y%m%dT%H%M%SZ > "$R/step0.t0.txt"; sync

# The solver is EXPECTED to SIGFPE (~rc 136) around t=0.116.  That IS the
# measurement.  Record rc; do NOT abort the probe on a nonzero solver rc.
SOLVER_RC=$(step rhoCentralFoam 4 "$CASE/log.rhoCentralFoam" mpirun -np 4 rhoCentralFoam -parallel | tail -1)
echo "STEP-0 solver rc=${SOLVER_RC} (a SIGFPE/136 here is the measurement, not a failure)" \
  | tee -a "$R/PROGRESS.txt"

# The fieldMinMax functionObject writes a single reduced file at the case root
# postProcessing (rank 0).  Locate it and run the reader (a probe, not a grade).
DAT=$(find "$CASE/postProcessing/fieldMinMax" -name fieldMinMax.dat 2>/dev/null | sort | tail -1)
if [ -z "$DAT" ]; then
  echo "STEP-0: no fieldMinMax.dat written -- the probe captured no steps; INCONCLUSIVE" \
    | tee -a "$R/PROGRESS.txt"
  echo "$SOLVER_RC" > "$R/step0.rc.txt"; sync; exit 0
fi
python3 "$READER" "$DAT" --out "$CASE/step0_negativity_result.json" \
  > "$CASE/log.step0_reader" 2>&1
READER_RC=$?
echo "[STEP0/reader] rc=${READER_RC} (0=measured, 2=control refused)" | tee -a "$R/PROGRESS.txt"

date -u +%Y%m%dT%H%M%SZ > "$R/step0.t1.txt"
printf '%s\n' "$USED_CORESEC" > "$R/step0.coresec.txt"
echo "$SOLVER_RC" > "$R/step0.rc.txt"; sync
echo "STEP-0 COMPLETE: used ${USED_CORESEC} core-seconds = $(echo "scale=2; $USED_CORESEC/60" | bc) core-min vs ${CAP_COREMIN} core-min cap; solver rc=${SOLVER_RC}, reader rc=${READER_RC}" \
  | tee -a "$R/PROGRESS.txt"
