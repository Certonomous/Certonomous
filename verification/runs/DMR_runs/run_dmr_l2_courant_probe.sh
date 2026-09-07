#!/bin/bash
# DMR R3 L2 COURANT PROBE driver -- FINE-ONLY (N=240) robustness probe.
#
# QUESTION (falsifiable, single level): does the finest DMR level (N=240) with the
# Tadmor flux AND the time step halved (maxCo 0.1 -> 0.05) reach endTime t=0.2
# WITHOUT a SIGFPE?  L1 (Tadmor flux alone, maxCo 0.1) only DELAYED the
# energy-positivity collapse -- the crash moved t=0.116 -> t=0.15006 but did NOT
# reach t=0.2.  This probe measures whether halving the step CURES the collapse at
# the finest level, isolating the Courant (dt) lever.
#
# THIS IS A ROBUSTNESS PROBE, NOT A ROACHE TRIPLE.  It runs ONE level (N=240) only;
# it yields NO grid-convergence triple, NO GCI, NO Gate T'.  IF it reaches t=0.2 it
# grades the SINGLE level against Gate V' (0.0231) as an INFORMATIVE kinematics
# check (not a triple verdict); IF it SIGFPEs it runs the check-1'd
# step0_negativity_reader.py on the per-step fieldMinMax output to diagnose which
# field/site goes negative and where -- the L-501 answer-blind mechanism read.  A
# SIGFPE here (rc ~136) is THE MEASUREMENT, not a failure of the driver: the driver
# RECORDS the solver rc and proceeds to diagnose regardless (it is NOT graded as a
# capability finding off one SIGFPE -- L-501).
#
# rc IS CAPTURED INSIDE THIS WRAPPER, never around a setsid/timeout line (setsid
# parent returns 0 for every outcome).  Its OWN registered hard cap STOPS the run
# with no new budget (rule 12); the cap is this probe's alone.
#
# GUARD (rule 4): refuses if the FRESH probe root already exists -- a probe is never
# run into a tree something else may have written (this is a fresh full run from
# t=0, so the ABSENT guard applies; there is no restart seed).
#
# GRADE-PATH INTEGRITY (rule 2): IF (and only if) the level reaches t=0.2, the frozen
# grader dmr_locator_v2.py is hashed against its committed blob and grading is refused
# if it differs.  The grader reads shock POSITION and no scheme file, so it grades the
# maxCo-0.05 case unchanged and is REUSED UNCHANGED, never edited (rule 6).

set -u

R=/home/ubuntu/Certonomous/verification/runs/DMR_R3_L2_COURANT_PROBE_runs
CASE="$R/L2"
GEN=/home/ubuntu/Certonomous/verification/runs/DMR_runs/make_case_tadmor_co05.py
GRADER=/home/ubuntu/Certonomous/verification/runs/DMR_runs/dmr_locator_v2.py
FROZEN_GRADER_BLOB=52aacf9669bcf23e88a0bf7984b299fa8aaf286e
READER=/home/ubuntu/Certonomous/verification/runs/DMR_runs/step0_negativity_reader.py

N=240
RANKS=4
CAP_COREMIN=90.0
CAP_CORESEC=5400          # 90.0 * 60 -- this probe's OWN registered hard cap (§6)

# ---- guard: never write into a populated root (rule 4) --------------------
if [ -e "$R" ]; then
  echo "REFUSED: $R already exists. A probe is never run into a pre-existing tree." \
    | tee "/tmp/l2_courant_refused_$$.txt" 2>/dev/null
  exit 90
fi
mkdir -p "$R" || exit 1

# `-u` dropped around the source ONLY (L-339: the openfoam bashrc reads an unbound
# WM_PROJECT_DIR at its line ~184 under `set -u` and would kill this shell silently).
# USER exported first (L-343: a cron-started queue runner carries no USER).
export USER="${USER:-${LOGNAME:-$(id -un)}}"
set +u
source /usr/lib/openfoam/openfoam2606/etc/bashrc > /dev/null 2>>"$R/log.sourceerr"
set -u
command -v rhoCentralFoam >/dev/null || {
  echo "ABORT: rhoCentralFoam not on PATH after sourcing" | tee "$R/REFUSED.txt"
  echo 91 > "$R/probe.rc.txt"; sync; exit 91; }

USED_CORESEC=0

breach() {
  echo "CAP BREACH: ${USED_CORESEC}s core-seconds > ${CAP_CORESEC} (${CAP_COREMIN} core-min)" \
       "-- L2 COURANT PROBE STOPPED at step '$1', no new budget" \
       | tee -a "$R/CAP_BREACH.txt"
  echo 9 > "$R/probe.rc.txt"; sync; exit 9
}

# step <label> <ranks> <logfile> -- command follows.  rc captured HERE; the caller
# inspects the emitted rc.  Cap-enforced; a solver rc!=0 is NOT an abort here (a
# SIGFPE is the measurement) -- the caller decides.
step() {
  local label=$1 ranks=$2 log=$3; shift 3
  local remaining=$(( CAP_CORESEC - USED_CORESEC ))
  [ "$remaining" -le 0 ] && breach "$label"
  local budget_wall=$(( remaining / ranks ))
  local s; s=$(date +%s)
  timeout "${budget_wall}s" "$@" > "$log" 2>&1
  local rc=$?
  local e=$(( $(date +%s) - s ))
  USED_CORESEC=$(( USED_CORESEC + e * ranks ))
  echo "$rc" > "$CASE/RC_${label}.txt" 2>/dev/null || echo "$rc" > "$R/RC_${label}.txt"
  sync
  echo "[L2/${label}] rc=$rc wall=${e}s ranks=$ranks used=${USED_CORESEC}core-s" \
    | tee -a "$R/PROGRESS.txt"
  [ "$rc" -eq 124 ] && breach "$label (timeout at its cap slice)"
  [ "$USED_CORESEC" -gt "$CAP_CORESEC" ] && breach "$label"
  echo "$rc"   # emit rc for the caller's inspection
}

date -u +%Y%m%dT%H%M%SZ > "$R/probe.t0.txt"; sync

# ---- generate the maxCo-0.05 case via the co05 generator ------------------
python3 "$GEN" "$CASE" "$N" > "$R/log.makeCase_L2" 2>&1 || {
  echo "ABORT: make_case_tadmor_co05.py failed for L2 (N=$N)" | tee "$R/REFUSED.txt"
  echo 92 > "$R/probe.rc.txt"; sync; exit 92; }

# ---- add the per-step fieldMinMax functionObject (for the check-1'd reader) --
# The generated controlDict keeps its own maxCo 0.05 / adjustableRunTime / 0.02
# writeInterval (so t=0.2 fields are written for grading); the functionObject
# writes min/max AND cell LOCATION of (T e p rho U) EVERY step for the reader.
cat >> "$CASE/system/controlDict" <<'EOF'

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

cd "$CASE" || exit 1

# ---- pre-solve steps: a nonzero rc here IS an abort (broken case) ----------
for ps in "blockMesh|blockMesh" "checkMesh|checkMesh" "setExprFields|setExprFields" "decomposePar|decomposePar"; do
  lbl=${ps%%|*}; cmd=${ps##*|}
  rc=$(step "$lbl" 1 "$CASE/log.$lbl" "$cmd" | tail -1)
  if [ "$rc" -ne 0 ]; then
    echo "PRE-SOLVE STEP FAILED: L2/$lbl rc=$rc -- cannot run a broken case" | tee -a "$R/PROGRESS.txt"
    echo "$rc" > "$R/probe.rc.txt"; sync; exit "$rc"
  fi
done

# ---- the solve: a SIGFPE (rc ~136) is the MEASUREMENT, NOT an abort ---------
SOLVER_RC=$(step rhoCentralFoam 4 "$CASE/log.rhoCentralFoam" mpirun -np 4 rhoCentralFoam -parallel | tail -1)
echo "L2 solver rc=${SOLVER_RC} (a SIGFPE/136 here is the measurement, not a driver failure)" \
  | tee -a "$R/PROGRESS.txt"

# ---- did it reach t=0.2?  (rc==0 AND a clean End line) ---------------------
REACHED=no
if [ "$SOLVER_RC" -eq 0 ] && grep -qE '^End$' "$CASE/log.rhoCentralFoam"; then
  REACHED=yes
fi
echo "L2 reached_endTime=${REACHED}" | tee -a "$R/PROGRESS.txt"

if [ "$REACHED" = "yes" ]; then
  # -------- reached t=0.2: grade the SINGLE level (informative Gate V') ------
  cd "$CASE" || exit 1
  step reconstructPar   1 "$CASE/log.reconstructPar"   reconstructPar >/dev/null
  step writeCellCentres 1 "$CASE/log.writeCellCentres" postProcess -func writeCellCentres -time 0.2 >/dev/null

  # grade-path integrity (rule 2) THEN grade
  GB=$(git -C /home/ubuntu/Certonomous hash-object "$GRADER" 2>/dev/null)
  if [ "$GB" != "$FROZEN_GRADER_BLOB" ]; then
    echo "REFUSED: grader blob '$GB' != frozen '$FROZEN_GRADER_BLOB' -- grading path not the frozen instrument" \
      | tee "$R/GRADE_REFUSED.txt"
    echo 93 > "$R/probe.rc.txt"; sync; exit 93
  fi
  step grade 1 "$CASE/log.grade" python3 "$GRADER" "$CASE" "$N" --out "$CASE/locator_result.json" >/dev/null
  echo "L2 GRADED (single-level informative Gate V', NOT a triple): see $CASE/locator_result.json" \
    | tee -a "$R/PROGRESS.txt"
else
  # -------- SIGFPE / did not reach t=0.2: diagnose with the check-1'd reader --
  DAT=$(find "$CASE/postProcessing/fieldMinMax" -name fieldMinMax.dat 2>/dev/null | sort | tail -1)
  if [ -z "$DAT" ]; then
    echo "L2: no fieldMinMax.dat written -- the probe captured no steps; INCONCLUSIVE" \
      | tee -a "$R/PROGRESS.txt"
  else
    python3 "$READER" "$DAT" --out "$CASE/l2_negativity_result.json" \
      > "$CASE/log.l2_reader" 2>&1
    READER_RC=$?
    echo "[L2/reader] rc=${READER_RC} (0=measured, 2=control refused) see $CASE/l2_negativity_result.json" \
      | tee -a "$R/PROGRESS.txt"
  fi
fi

cd "$R" || exit 1
date -u +%Y%m%dT%H%M%SZ > "$R/probe.t1.txt"
printf '%s\n' "$USED_CORESEC" > "$R/probe.coresec.txt"
echo "$SOLVER_RC" > "$R/probe.rc.txt"; sync
echo "L2 COURANT PROBE COMPLETE: used ${USED_CORESEC} core-seconds = $(echo "scale=2; $USED_CORESEC/60" | bc) core-min against the ${CAP_COREMIN} core-min cap; solver rc=${SOLVER_RC}, reached_endTime=${REACHED}" \
  | tee -a "$R/PROGRESS.txt"
