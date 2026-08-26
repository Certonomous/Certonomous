#!/usr/bin/env bash
# =============================================================================
# VMFL017-R2 graded-run driver -- Transonic Flow over an RAE 2822 Airfoil
# (Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p.69).
# Solver: rhoCentralFoam / kOmegaSST (OpenFOAM v2606), TRANSIENT EXPLICIT,
# adjustTimeStep + maxCo, 2D C-mesh, characteristic far field.
#
# Frozen pre-registration: cases/ansys_verification/VMFL017/R2/PREREGISTRATION.md
# Frozen comparator      : cases/ansys_verification/VMFL017/R2/grade_vmfl017_r2.py
# The driving numbers this script ASSERTS are registered in PRE-COMPUTE AMENDMENT 2
# of that pre-registration: maxCo 0.2, maxDeltaT 1e-5, deltaT 1e-9, endTime 0.05 s,
# writeInterval 0.05 (adjustableRunTime), forceCoeffs executeInterval 1e-4.
#
# ---------------------------------------------------------------------------
# NO `set -u`.  CATEGORICALLY INCOMPATIBLE with OpenFOAM v2606: sourcing
# etc/bashrc dereferences WM_PROJECT_DIR at bashrc line 184 BEFORE assigning it,
# MEASURED rc 127 (PREREG_TEMPLATE Amendment 3 item 3; prereg line 13 "NO set -u").
# `set -e` also does not gate reliably here, so EVERY check gates EXPLICITLY with
# `|| { echo ABORT...; exit <n>; }`.
# ---------------------------------------------------------------------------
# PREREG_TEMPLATE AMENDMENT 3 -- the six required launcher artifacts:
#   1. launch-time freeze verification of prereg AND comparator against HEAD  -> below
#   2. cap enforcement in the executable path, timeout_s = cap_core_min*60/RANKS -> below
#   3. no `set -u`, reason named                                              -> above
#   4. planted-zero control                                                   -> below
#   5. mesh birth certificate                                                 -> below
#   6. a pre-flight smoke test that exercises THIS LAUNCHER                    -> VMFL_SMOKE
#
# CAPS ARE PER LEVEL, NOT a shared drawdown -- prereg line 12 registers
# "PER-LEVEL caps (NOT a shared drawdown): L1 300, L2 600, L3 1500 core-min",
# under the supervisor's anti-starvation directive of 2026-08-25 (a shared budget
# let one slow level starve a later one into a FALSE failure, VMFL003_M2 arm C).
# Running total core-minutes ARE accounted and recorded beside each level, but the
# gate that stops a level is that level's OWN cap, exactly as frozen.
# core_minutes = wall_s * RANKS / 60 ;  timeout_s = cap_core_min * 60 / RANKS.
# An overrun STOPS the level (rc 124); endTime is NEVER silently reduced to fit a
# cap (prereg line 12; CLAUDE.md rule 12).
# =============================================================================

RANKS=1
declare -A CAP=( [L1]=300 [L2]=600 [L3]=1500 )   # core-min, frozen prereg line 12

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CASE_DIR="$SCRIPT_DIR/case"
RUN_ROOT="${1:-$PWD}"
shift 2>/dev/null
LEVELS_TO_RUN="${*:-L1 L2 L3}"

# Registered numbers this launcher ASSERTS against the case inputs (prereg line 13
# "endTime/writeInterval assertion"; PRE-COMPUTE AMENDMENT 2 registers the values).
REG_ENDTIME="0.05"
REG_WRITEINTERVAL="0.05"
REG_MAXCO="0.2"
REG_MAXDELTAT="1e-5"
REG_DELTAT="1e-9"
REG_FO_EXECINTERVAL="1e-4"

echo "=== VMFL017-R2 launcher  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)  run_root=$RUN_ROOT"

# --- smoke mode (Amendment 3 item 6) -----------------------------------------
# The smoke NEVER runs in the graded run root: it refuses any root that is not
# under the scratch area, so a smoke can never leave an answer where a graded run
# would look for one (rule 4 age guard; rule 13 the scratchpad is temp only).
SMOKE_ENDTIME="2e-8"
SMOKE_FO_INTERVAL="2e-9"
if [ -n "$VMFL_SMOKE" ]; then
  case "$RUN_ROOT" in
    */scratchpad/*|*/scratchpad) : ;;
    *) echo "ABORT: VMFL_SMOKE refuses run_root '$RUN_ROOT' -- a smoke runs in scratch ONLY, never in the graded run root"; exit 2 ;;
  esac
  LEVELS_TO_RUN="L1"
  echo "  SMOKE MODE: L1 only, endTime shortened to $SMOKE_ENDTIME IN THE SCRATCH COPY ONLY"
fi

# --- 1. LAUNCH-TIME FREEZE CHECK (CLAUDE.md rule 2; template Amendment 2) -----
# Refuses with exit 2 if either frozen file on disk differs from its HEAD blob.
REPO="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || { echo "ABORT: not inside a git repository"; exit 2; }
PREREG_REL="cases/ansys_verification/VMFL017/R2/PREREGISTRATION.md"
GRADER_REL="cases/ansys_verification/VMFL017/R2/grade_vmfl017_r2.py"
BIRTH_REL="cases/ansys_verification/VMFL017/mesh_birth/BIRTH_CERTIFICATE.md"
FREEZE_COMMIT="$(git -C "$REPO" rev-parse HEAD)" || { echo "ABORT: cannot resolve HEAD"; exit 2; }
for REL in "$PREREG_REL" "$GRADER_REL"; do
  git -C "$REPO" cat-file -e "HEAD:$REL" 2>/dev/null || { echo "ABORT: $REL is NOT committed at HEAD -- the freeze IS the evidence (rule 2)"; exit 2; }
  HEADSHA="$(git -C "$REPO" show "HEAD:$REL" | git -C "$REPO" hash-object --stdin)" || { echo "ABORT: cannot hash HEAD blob of $REL"; exit 2; }
  DISKSHA="$(git -C "$REPO" hash-object "$REPO/$REL")" || { echo "ABORT: cannot hash $REL on disk"; exit 2; }
  [ "$DISKSHA" = "$HEADSHA" ] || { echo "ABORT freeze check: $REL on disk ($DISKSHA) != HEAD blob ($HEADSHA). The file that would run is NOT the file that was frozen."; exit 2; }
  echo "  freeze OK  $REL  $DISKSHA"
  case "$REL" in
    "$PREREG_REL") PREREG_BLOB="$DISKSHA" ;;
    "$GRADER_REL") GRADER_BLOB="$DISKSHA" ;;
  esac
done

# --- 5. MESH BIRTH CERTIFICATE (MESH_STANDARD sec.6) --------------------------
# The R2 blockMeshDicts are the attempt-1 family REUSED byte for byte (prereg line 7);
# its birth certificate is the certificate for this mesh family.
git -C "$REPO" cat-file -e "HEAD:$BIRTH_REL" 2>/dev/null || { echo "ABORT: mesh birth certificate $BIRTH_REL not at HEAD (MESH_STANDARD sec.6)"; exit 2; }
BIRTH_BLOB="$(git -C "$REPO" rev-parse "HEAD:$BIRTH_REL")"
echo "  mesh birth certificate OK  $BIRTH_REL  $BIRTH_BLOB"
for L in L1 L2 L3; do
  A="$(git -C "$REPO" rev-parse "HEAD:cases/ansys_verification/VMFL017/case/system/blockMeshDict.$L" 2>/dev/null)" || { echo "ABORT: no attempt-1 blockMeshDict.$L at HEAD"; exit 2; }
  B="$(git -C "$REPO" hash-object "$CASE_DIR/system/blockMeshDict.$L")" || { echo "ABORT: cannot hash R2 blockMeshDict.$L"; exit 2; }
  [ "$A" = "$B" ] || { echo "ABORT: blockMeshDict.$L is NOT the birth-certified attempt-1 mesh ($B != $A)"; exit 2; }
done
echo "  blockMeshDict L1/L2/L3 identical to the birth-certified attempt-1 family"

# --- REGISTERED-NUMBER ASSERTION (prereg line 13; AMENDMENT 2) ----------------
# A launcher cannot assert a value the freeze never fixed -- AMENDMENT 2 fixes them,
# and this block is what makes the registration binding on what actually runs.
CD="$CASE_DIR/system/controlDict"
[ -f "$CD" ] || { echo "ABORT: no $CD"; exit 2; }
_dictval() { grep -oE "^[[:space:]]*$1[[:space:]]+[^;]+;" "$2" | head -1 | sed -E "s/^[[:space:]]*$1[[:space:]]+//; s/;[[:space:]]*$//" | tr -d '[:space:]'; }
_num_eq() { python3 -c "import sys;a=float(sys.argv[1]);b=float(sys.argv[2]);sys.exit(0 if a==b else 1)" "$1" "$2"; }
for PAIR in "endTime:$REG_ENDTIME" "deltaT:$REG_DELTAT" "maxCo:$REG_MAXCO" "maxDeltaT:$REG_MAXDELTAT"; do
  K="${PAIR%%:*}"; WANT="${PAIR#*:}"; GOT="$(_dictval "$K" "$CD")"
  [ -n "$GOT" ] || { echo "ABORT: controlDict has no $K -- AMENDMENT 2 registers $K = $WANT"; exit 2; }
  _num_eq "$GOT" "$WANT" || { echo "ABORT: controlDict $K = $GOT but AMENDMENT 2 registers $WANT"; exit 2; }
  echo "  registered OK  controlDict $K = $GOT"
done
WI="$(grep -A2 '^writeControl' "$CD" | grep -oE 'writeInterval[[:space:]]+[^;]+;' | head -1 | sed -E 's/writeInterval[[:space:]]+//; s/;$//' | tr -d '[:space:]')"
_num_eq "$WI" "$REG_WRITEINTERVAL" || { echo "ABORT: controlDict writeInterval = $WI but AMENDMENT 2 registers $REG_WRITEINTERVAL"; exit 2; }
grep -qE '^[[:space:]]*writeControl[[:space:]]+adjustableRunTime;' "$CD" || { echo "ABORT: controlDict writeControl is not adjustableRunTime -- AMENDMENT 2 registers adjustableRunTime so the last written time lands EXACTLY on endTime"; exit 2; }
grep -qE '^[[:space:]]*adjustTimeStep[[:space:]]+yes;' "$CD" || { echo "ABORT: controlDict adjustTimeStep is not yes"; exit 2; }
echo "  registered OK  controlDict writeControl adjustableRunTime, writeInterval = $WI, adjustTimeStep yes"
FOEI="$(grep -oE 'executeInterval[[:space:]]+[^;]+;' "$CD" | head -1 | sed -E 's/executeInterval[[:space:]]+//; s/;$//' | tr -d '[:space:]')"
_num_eq "$FOEI" "$REG_FO_EXECINTERVAL" || { echo "ABORT: forceCoeffs executeInterval = $FOEI but AMENDMENT 2 registers $REG_FO_EXECINTERVAL"; exit 2; }
echo "  registered OK  forceCoeffs1 executeInterval = $FOEI  (~500 samples over $REG_ENDTIME s)"
# the comparator's endTime must be the SAME number -- it is the value the grader refuses on
CMP_ENDTIME="$(grep -oE '^ENDTIME_PHYS[[:space:]]*=[[:space:]]*[0-9.eE+-]+' "$SCRIPT_DIR/grade_vmfl017_r2.py" | head -1 | sed -E 's/.*=[[:space:]]*//')"
_num_eq "$CMP_ENDTIME" "$REG_ENDTIME" || { echo "ABORT: comparator ENDTIME_PHYS = $CMP_ENDTIME but controlDict/AMENDMENT 2 register $REG_ENDTIME"; exit 2; }
echo "  registered OK  comparator ENDTIME_PHYS = $CMP_ENDTIME == controlDict endTime"
# plateau sampling: samples over the run and in the comparator's final window
CMP_MINS="$(grep -oE '^PLATEAU_MIN_SAMPLES[[:space:]]*=[[:space:]]*[0-9]+' "$SCRIPT_DIR/grade_vmfl017_r2.py" | head -1 | sed -E 's/.*=[[:space:]]*//')"
CMP_WFRAC="$(grep -oE '^WINDOW_FRAC[[:space:]]*=[[:space:]]*[0-9.]+' "$SCRIPT_DIR/grade_vmfl017_r2.py" | head -1 | sed -E 's/.*=[[:space:]]*//')"
python3 -c "
import sys
n=float(sys.argv[1])/float(sys.argv[2]); w=n*float(sys.argv[3]); need=float(sys.argv[4])
print('  registered OK  %.0f forceCoeffs samples over the run, %.0f in the final %.0f%% window >= PLATEAU_MIN_SAMPLES %.0f'%(n,w,100*float(sys.argv[3]),need))
sys.exit(0 if w>=need else 1)" "$REG_ENDTIME" "$REG_FO_EXECINTERVAL" "$CMP_WFRAC" "$CMP_MINS" \
  || { echo "ABORT: the registered executeInterval does not deliver PLATEAU_MIN_SAMPLES in the comparator's window"; exit 2; }

# --- 4. PLANTED-ZERO CONTROL (CLAUDE.md rule 3) -------------------------------
# The comparator's own --selftest DRIVES the planted-zero (PLANT = 7.531e-3) and the
# observed-order floor controls. A comparator whose controls do not fire does not grade
# this run, so the launcher refuses before spending a core-minute.
python3 "$SCRIPT_DIR/grade_vmfl017_r2.py" --selftest > "/tmp/vmfl017r2_selftest.$$" 2>&1 || { echo "ABORT: comparator --selftest is NOT green (planted-zero / p-floor controls); see /tmp/vmfl017r2_selftest.$$"; exit 2; }
grep -q '^SELFTEST OK' "/tmp/vmfl017r2_selftest.$$" || { echo "ABORT: comparator --selftest printed no SELFTEST OK"; exit 2; }
grep -q 'plant seen' "/tmp/vmfl017r2_selftest.$$" || { echo "ABORT: comparator --selftest did not exercise the planted-zero control"; exit 2; }
echo "  planted-zero + p-floor controls OK (comparator --selftest green)"
rm -f "/tmp/vmfl017r2_selftest.$$"

# --- run root, contention record, launch record -------------------------------
mkdir -p "$RUN_ROOT" || { echo "ABORT: cannot create $RUN_ROOT"; exit 2; }
{ echo "utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "uptime = $(uptime)"
  echo "nproc = $(nproc)"
  echo "loadavg = $(cat /proc/loadavg)"
  echo "MemAvailable_kB = $(grep MemAvailable /proc/meminfo | tr -s ' ' | cut -d' ' -f2)"
  echo "note = contention at launch; core-minutes are wall_s*RANKS/60 and a busy box inflates wall_s (COMPUTE_BUDGET_CHARTER sec.6: waste is reported, never absorbed)"
} > "$RUN_ROOT/CONTENTION.txt" || { echo "ABORT: cannot write CONTENTION.txt"; exit 2; }

LR="$RUN_ROOT/LAUNCH_RECORD.txt"
{ echo "case = VMFL017-R2"
  echo "launched_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "freeze_commit_head = $FREEZE_COMMIT"
  echo "prereg = $PREREG_REL"
  echo "prereg_blob = $PREREG_BLOB"
  echo "comparator = $GRADER_REL"
  echo "comparator_blob = $GRADER_BLOB"
  echo "mesh_birth_certificate = $BIRTH_REL ($BIRTH_BLOB)"
  echo "levels = $LEVELS_TO_RUN"
  echo "ranks = $RANKS"
  echo "caps_core_min = L1=${CAP[L1]} L2=${CAP[L2]} L3=${CAP[L3]}  (PER LEVEL, not a shared drawdown -- prereg line 12)"
  echo "registered = endTime $REG_ENDTIME s ; deltaT $REG_DELTAT ; maxCo $REG_MAXCO ; maxDeltaT $REG_MAXDELTAT ; writeInterval $REG_WRITEINTERVAL adjustableRunTime ; forceCoeffs executeInterval $REG_FO_EXECINTERVAL"
  echo "smoke_mode = ${VMFL_SMOKE:-no}"
} > "$LR" || { echo "ABORT: cannot write LAUNCH_RECORD.txt"; exit 2; }

# --- OpenFOAM ------------------------------------------------------------------
source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo "ABORT: cannot source /usr/lib/openfoam/openfoam2606/etc/bashrc"; exit 2; }
command -v rhoCentralFoam >/dev/null || { echo "ABORT: rhoCentralFoam not on PATH after sourcing the v2606 bashrc"; exit 2; }
command -v blockMesh >/dev/null || { echo "ABORT: blockMesh not on PATH"; exit 2; }
SOLVER_BIN="$(command -v rhoCentralFoam)"
echo "solver_bin = $SOLVER_BIN" >> "$LR"
echo "  rhoCentralFoam = $SOLVER_BIN"

TOTAL_CORE_MIN=0
OVERALL_RC=0

for L in $LEVELS_TO_RUN; do
  OUT="$RUN_ROOT/$L"
  CAPL="${CAP[$L]}"
  [ -n "$CAPL" ] || { echo "ABORT: no registered cap for level $L"; exit 2; }

  # AGE GUARD (rule 4): refuse a level directory that already holds 0/ or a time dir.
  # NO `[0-9]*` glob anywhere -- L-339: such a glob also matches `0.orig` and reads a
  # template directory as an existing answer. Numeric time dirs are matched by regex.
  if [ -d "$OUT/0" ]; then echo "ABORT age guard: $OUT already holds 0/ -- a run is never launched into a tree that already holds an answer"; exit 2; fi
  EXISTING_T="$(find "$OUT" -mindepth 1 -maxdepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?([eE][-+][0-9]+)?$' 2>/dev/null | head -1)"
  [ -z "$EXISTING_T" ] || { echo "ABORT age guard: $OUT already holds a numeric time directory ($EXISTING_T)"; exit 2; }

  TIMEOUT_S="$(python3 -c "print(int($CAPL*60/$RANKS))")" || { echo "ABORT: cap arithmetic failed for $L"; exit 2; }
  echo "--- $L  cap ${CAPL} core-min  ranks ${RANKS}  timeout ${TIMEOUT_S}s"

  mkdir -p "$OUT" || { echo "ABORT: mkdir $OUT"; exit 2; }
  cp -r "$CASE_DIR"/0 "$CASE_DIR"/constant "$CASE_DIR"/system "$OUT"/ || { echo "ABORT: cannot copy the case templates into $OUT"; exit 2; }
  [ -f "$OUT/system/blockMeshDict.$L" ] || { echo "ABORT: no blockMeshDict.$L in the case templates"; exit 2; }
  cp "$OUT/system/blockMeshDict.$L" "$OUT/system/blockMeshDict" || { echo "ABORT: cannot select blockMeshDict.$L"; exit 2; }

  if [ -n "$VMFL_SMOKE" ]; then
    # SCRATCH COPY ONLY. The graded controlDict on disk is never touched; endTime is
    # shortened here so the launcher itself can be exercised end to end in minutes.
    # The forceCoeffs intervals are shortened here TOO, so the smoke exercises the
    # function object and the comparator's reader path (postProcessing/forceCoeffs1/
    # <t>/coefficient.dat, col 1 = Cd, col 4 = Cl) rather than only the solver.
    sed -i -e "s/^endTime         0.05;/endTime         $SMOKE_ENDTIME;/" \
           -e "s/^writeInterval   0.05;/writeInterval   $SMOKE_ENDTIME;/" \
           -e "s/executeInterval 1e-4;/executeInterval $SMOKE_FO_INTERVAL;/" \
           -e "s/writeInterval   1e-4;/writeInterval   $SMOKE_FO_INTERVAL;/" "$OUT/system/controlDict" \
      || { echo "ABORT: smoke endTime substitution failed"; exit 2; }
    grep -qE "^endTime         $SMOKE_ENDTIME;" "$OUT/system/controlDict" || { echo "ABORT: smoke endTime substitution did not take"; exit 2; }
    grep -qE "executeInterval $SMOKE_FO_INTERVAL;" "$OUT/system/controlDict" || { echo "ABORT: smoke forceCoeffs interval substitution did not take"; exit 2; }
  fi

  # per-level pre-record so a killed launcher still leaves the cap it was under
  printf 'level=%s\nstate=STARTED\nranks=%d\ncap_core_min=%s\ntimeout_s=%d\nprereg_blob=%s\ncomparator_blob=%s\nstarted_utc=%s\nnote=per-level independent cap (prereg line 12; NOT a shared drawdown)\n' \
    "$L" "$RANKS" "$CAPL" "$TIMEOUT_S" "$PREREG_BLOB" "$GRADER_BLOB" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$RUN_ROOT/RUN_RC.$L" \
    || { echo "ABORT: cannot write RUN_RC.$L"; exit 2; }

  T0="$(date +%s)"
  (
    cd "$OUT" || exit 90
    blockMesh > log.blockMesh 2>&1 || exit 91
    checkMesh > log.checkMesh 2>&1 || exit 92
    # 0/U is touched LAST, immediately before the solver: it is the age-guard datum
    # that dates the run allowed to produce the answer (CLAUDE.md rule 4).
    touch 0/U || exit 93
    timeout "$TIMEOUT_S" rhoCentralFoam > log.rhoCentralFoam 2>&1
  )
  RC=$?
  T1="$(date +%s)"
  WALL=$((T1-T0))
  CORE_MIN="$(python3 -c "print(round($WALL*$RANKS/60.0, 4))")"
  TOTAL_CORE_MIN="$(python3 -c "print(round($TOTAL_CORE_MIN + $CORE_MIN, 4))")"

  # field-dir-at-endTime check (prereg line 13): a time directory at the registered
  # endTime, carrying U, and NEWER than 0/U. Recorded, never used to soften rc.
  ENDT_DIR=""; ENDT_OK="no"
  for D in $(find "$OUT" -mindepth 1 -maxdepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?([eE][-+][0-9]+)?$' 2>/dev/null); do
    B="$(basename "$D")"
    if python3 -c "import sys;sys.exit(0 if float(sys.argv[1])>0 else 1)" "$B" 2>/dev/null; then
      if [ -z "$ENDT_DIR" ] || python3 -c "import sys;sys.exit(0 if float(sys.argv[1])>float(sys.argv[2]) else 1)" "$B" "$(basename "$ENDT_DIR")"; then ENDT_DIR="$D"; fi
    fi
  done
  if [ -n "$ENDT_DIR" ] && [ -f "$ENDT_DIR/U" ] && [ "$ENDT_DIR/U" -nt "$OUT/0/U" ]; then ENDT_OK="yes"; fi
  LAST_TIME="$(grep -E '^Time = ' "$OUT/log.rhoCentralFoam" 2>/dev/null | tail -1 | sed -E 's/^Time = //')"
  ENDED="$(grep -cE '^End' "$OUT/log.rhoCentralFoam" 2>/dev/null)"

  printf 'level=%s\nstate=FINISHED\nrc=%d\nwall_s=%d\nranks=%d\ncore_min=%s\ntotal_core_min_so_far=%s\ntimeout_s=%d\ncap_core_min=%s\nlast_time_in_log=%s\nEnd_lines=%s\nlatest_time_dir=%s\nfield_at_endTime_newer_than_0_U=%s\nprereg_blob=%s\ncomparator_blob=%s\nsolver_bin=%s\nutc=%s\nnote=rc is rhoCentralFoam exit status under timeout; 124 means the level hit its OWN per-level cap. endTime is NEVER reduced to fit a cap (prereg line 12).\n' \
    "$L" "$RC" "$WALL" "$RANKS" "$CORE_MIN" "$TOTAL_CORE_MIN" "$TIMEOUT_S" "$CAPL" "${LAST_TIME:-none}" "${ENDED:-0}" "${ENDT_DIR:-none}" "$ENDT_OK" "$PREREG_BLOB" "$GRADER_BLOB" "$SOLVER_BIN" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    > "$RUN_ROOT/RUN_RC.$L" || { echo "ABORT: cannot write RUN_RC.$L"; exit 2; }

  if [ -n "$VMFL_SMOKE" ]; then
    CDAT="$(find "$OUT/postProcessing/forceCoeffs1" -name coefficient.dat 2>/dev/null | head -1)"
    [ -n "$CDAT" ] || { echo "ABORT smoke: forceCoeffs1 wrote NO coefficient.dat -- the comparator's reader would have nothing to read"; exit 2; }
    NROW="$(grep -cvE '^[[:space:]]*(#|$)' "$CDAT")"
    NCOL="$(grep -vE '^[[:space:]]*(#|$)' "$CDAT" | head -1 | awk '{print NF}')"
    python3 -c "import sys;sys.exit(0 if int(sys.argv[1])>=2 and int(sys.argv[2])>4 else 1)" "$NROW" "$NCOL" \
      || { echo "ABORT smoke: coefficient.dat has $NROW data rows / $NCOL columns -- the reader needs col 1 (Cd) and col 4 (Cl)"; exit 2; }
    SMOKE_CD="$(grep -vE '^[[:space:]]*(#|$)' "$CDAT" | tail -1 | awk '{print $2}')"
    SMOKE_CL="$(grep -vE '^[[:space:]]*(#|$)' "$CDAT" | tail -1 | awk '{print $5}')"
    echo "  SMOKE forceCoeffs OK: $CDAT  rows=$NROW cols=$NCOL  last Cd=$SMOKE_CD Cl=$SMOKE_CL (NOT a result -- 2e-8 s of physical time)"
    echo "smoke_forceCoeffs = rows=$NROW cols=$NCOL last_Cd=$SMOKE_CD last_Cl=$SMOKE_CL" >> "$LR"
  fi

  { echo "level $L : rc=$RC wall_s=$WALL core_min=$CORE_MIN cap=$CAPL timeout_s=$TIMEOUT_S last_time=${LAST_TIME:-none} End_lines=${ENDED:-0} latest_time_dir=${ENDT_DIR:-none} field_newer_than_0_U=$ENDT_OK"; } >> "$LR"

  if [ "$RC" -ne 0 ]; then
    OVERALL_RC="$RC"
    echo "STOP $L: rc=$RC after ${WALL}s = ${CORE_MIN} core-min (cap ${CAPL} core-min)."
    echo "  A non-zero rc is a FINDING, not a retry. rc=124 means the per-level cap stopped it;"
    echo "  an overrun does NOT get a new budget and endTime is NOT shrunk to fit (rule 12)."
    echo "later levels are NOT launched" >> "$LR"
    break
  fi
  echo "done $L: ${WALL}s = ${CORE_MIN} core-min (cap ${CAPL} core-min), latest time dir ${ENDT_DIR:-none}"
done

echo "total_core_min = $TOTAL_CORE_MIN" >> "$LR"
echo "finished_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LR"
echo "=== VMFL017-R2 launcher done, overall rc=$OVERALL_RC, total ${TOTAL_CORE_MIN} core-min"
echo "grade with: python3 $SCRIPT_DIR/grade_vmfl017_r2.py --run-root $RUN_ROOT"
exit "$OVERALL_RC"
