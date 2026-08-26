#!/usr/bin/env bash
# =============================================================================
# VMFL011-R3 graded-run driver -- Laminar Flow in a Triangular Cavity.
# Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p.41.
# Solver: simpleFoam (OpenFOAM v2606), steady laminar SIMPLEC, Re = 400, 2-D.
#
# Frozen pre-registration: cases/ansys_verification/VMFL011-R3/PREREGISTRATION.md
# Frozen comparator      : cases/ansys_verification/VMFL011-R3/grade_vmfl011_r3.py
# Run root               : verification/runs/ansys_verification/VMFL011-R3/
#
# MODELLED LINE FOR LINE ON cases/ansys_verification/VMFL064-R2/run_vmfl064_r2.sh
# (the team's current R2 driver, itself modelled on VMFL017/R2), with the VMFL011
# case specifics substituted.  ARGV: the run root is $1 and it is REQUIRED --
# VMFL064R2-ENTRY-DEF-1 was a queue entry whose argv omitted it and whose launcher
# refused at zero compute.  Every queue entry for this launcher MUST pass <run_root>.
#
# ---------------------------------------------------------------------------
# NO `set -u`.  CATEGORICALLY INCOMPATIBLE with OpenFOAM v2606: sourcing
# etc/bashrc dereferences WM_PROJECT_DIR at bashrc line 184 BEFORE assigning it,
# MEASURED rc 127.  `set -e` also does not gate reliably here, so EVERY check
# gates EXPLICITLY with `|| { echo ABORT...; exit <n>; }`.
# ---------------------------------------------------------------------------
# THE CAP IS BYTE-IDENTICAL TO ATTEMPT 1 (PREREGISTRATION.md sec.7 of the parent,
# blob 4bd8c4285e379e93e1ad4e6c2b9967604d042523) and is a RUNNING TOTAL across the
# three levels, not a per-level cap:
#   core_minutes = wall_s * RANKS / 60 ;  timeout_s = remaining_core_min * 60 / RANKS
# An overrun STOPS the run (rc 124); endTime is NEVER silently reduced to fit a cap
# (CLAUDE.md rule 12).
# =============================================================================

RANKS=1
CAP_CORE_MIN=50          # running TOTAL across all three levels -- byte-identical
ENDTIME=20000            # byte-identical to attempt 1

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CASE_DIR="$SCRIPT_DIR/case"
RUN_ROOT="${1:?usage: run_vmfl011_r3.sh <run_root> [levels...]}"
shift 2>/dev/null
LEVELS_TO_RUN="${*:-L1 L2 L3}"

# r = 2 grid triple: base cells NB and height cells NH double together (parent
# prereg sec.6).  NB is EVEN at every level so the bisector x = 0 is a cell-face
# plane identically placed under refinement.
declare -A NB=( [L1]=20 [L2]=40 [L3]=80  )
declare -A NH=( [L1]=40 [L2]=80 [L3]=160 )

echo "=== VMFL011-R3 launcher  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)  run_root=$RUN_ROOT"

# --- smoke mode ---------------------------------------------------------------
# The smoke NEVER runs in the graded run root: it refuses any root that is not
# under a scratch area, so a smoke can never leave an answer where a graded run
# would look for one (rule 4 age guard; rule 13 the scratchpad is temp only).
SMOKE_ENDTIME=20
if [ -n "$VMFL_SMOKE" ]; then
  case "$RUN_ROOT" in
    */scratchpad/*|*/scratchpad) : ;;
    *) echo "ABORT: VMFL_SMOKE refuses run_root '$RUN_ROOT' -- a smoke runs in scratch ONLY, never in the graded run root"; exit 2 ;;
  esac
  LEVELS_TO_RUN="L1"
  ENDTIME="$SMOKE_ENDTIME"
  echo "  SMOKE MODE: L1 only, endTime shortened to $SMOKE_ENDTIME IN THE SCRATCH COPY ONLY; grades nothing"
fi

# --- 1. LAUNCH-TIME FREEZE CHECK (CLAUDE.md rule 2) ---------------------------
REPO="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || { echo "ABORT: not inside a git repository"; exit 2; }
PREREG_REL="cases/ansys_verification/VMFL011-R3/PREREGISTRATION.md"
GRADER_REL="cases/ansys_verification/VMFL011-R3/grade_vmfl011_r3.py"
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

# --- 2. CASE INPUTS AND REFERENCE, BYTE-IDENTICAL TO ATTEMPT 1 ----------------
# Every input file and the reference CSV are hashed against the ATTEMPT-1 HEAD
# blob, so "the case and the reference did not change" is a CHECK at launch, not a
# claim in a document.  The R3 changes the PLANT PLACEMENT inside the rule-3 control
# (L-347), makes every channel control run and report before any exit, and
# changes nothing else on the grading path.
for F in case/0/U case/0/p case/constant/transportProperties \
         case/constant/turbulenceProperties case/system/blockMeshDict.template \
         case/system/controlDict.template case/system/fvSchemes case/system/fvSolution \
         reference/vmfl011_benchmark_xnorm.csv; do
  A="$(git -C "$REPO" rev-parse "HEAD:cases/ansys_verification/VMFL011/$F" 2>/dev/null)" || { echo "ABORT: no attempt-1 $F at HEAD"; exit 2; }
  B="$(git -C "$REPO" hash-object "$SCRIPT_DIR/$F")" || { echo "ABORT: cannot hash R2 $F"; exit 2; }
  [ "$A" = "$B" ] || { echo "ABORT: $F is NOT the attempt-1 input ($B != $A) -- the R3 changes the PLANT PLACEMENT and the control REPORTING, nothing else"; exit 2; }
done
echo "  case inputs and reference byte-identical to the attempt-1 family (9 files)"

# --- 3. THE CONTROLS, BEFORE A CORE-MINUTE IS SPENT (rule 3, L-332) ----------
# The comparator's own --selftest DRIVES the planted-zero controls, the L-340
# plant-sizing repair on the REAL attempt-1 bytes, the observed-order floor and the
# L-342 field classes.  A comparator whose controls do not fire does not grade this
# run, so the launcher refuses BEFORE spending anything.  Checked under BOTH
# interpreters, because `python3 -O` deletes every assert and a control that exists
# only under one flag is not a control (L-332).
ST="/tmp/vmfl011r2_selftest.$$"
python3 "$SCRIPT_DIR/grade_vmfl011_r3.py" --selftest > "$ST" 2>&1 || { echo "ABORT: comparator --selftest is NOT green under python3; see $ST"; exit 2; }
python3 -O "$SCRIPT_DIR/grade_vmfl011_r3.py" --selftest > "$ST.O" 2>&1 || { echo "ABORT: comparator --selftest is NOT green under python3 -O; see $ST.O"; exit 2; }
cmp -s "$ST" "$ST.O" || { echo "ABORT: comparator --selftest differs between python3 and python3 -O -- a control that vanishes under -O is not a control (L-332)"; exit 2; }
grep -q '^SELFTEST: all checks passed' "$ST" || { echo "ABORT: comparator --selftest printed no all-checks-passed line"; exit 2; }
grep -q '^  \[FAIL\]' "$ST" && { echo "ABORT: comparator --selftest printed a FAIL line"; exit 2; }
grep -q 'planted-zero REFUSES (exit 2) a reader that cannot see the plant' "$ST" || { echo "ABORT: comparator --selftest did not exercise the planted-zero control (rule 3)"; exit 2; }
grep -q 'L-340 REPAIR DRIVEN on the real attempt-1 L1 bytes' "$ST" || { echo "ABORT: comparator --selftest did not DRIVE the L-340 plant-sizing repair"; exit 2; }
grep -q 'the SIZING is the repair, not the shape' "$ST" || { echo "ABORT: comparator --selftest did not show the sizing to be load-bearing"; exit 2; }
grep -q 'P_MIN turns a computed p = 0.01 into DEGENERATE' "$ST" || { echo "ABORT: comparator --selftest did not exercise the observed-order floor (P_MIN)"; exit 2; }
grep -q 'ast.Assert count in this file is 0' "$ST" || { echo "ABORT: comparator --selftest did not run the L-332 assert census"; exit 2; }
grep -q 'L-347 probe 1: the R2 row-0 pair STILL REFUSES on the real R2 bytes' "$ST" || { echo "ABORT: comparator --selftest did not DRIVE the L-347 placement repair against the R2 bytes"; exit 2; }
grep -q 'L-347 probe 2: the REGISTERED argmin pair PASSES on the same bytes' "$ST" || { echo "ABORT: comparator --selftest did not show the registered argmin placement passing"; exit 2; }
grep -q 'L-347 probe 4: a BLIND reader is still REFUSED under the argmin plant' "$ST" || { echo "ABORT: comparator --selftest did not show a blind reader still refused (the repair must not weaken the control)"; exit 2; }
grep -q 'L-347 clause 3: with BOTH channels blinded BOTH are reported FAIL' "$ST" || { echo "ABORT: comparator --selftest did not show EVERY channel control running and reporting before exit (L-347 clause 3)"; exit 2; }
NCHK="$(grep -c '^  \[PASS\]' "$ST")"
echo "  controls OK: --selftest $NCHK/$NCHK PASS, byte-identical under python3 and python3 -O"
rm -f "$ST" "$ST.O"

# --- run root, contention record, launch record -------------------------------
mkdir -p "$RUN_ROOT" || { echo "ABORT: cannot create $RUN_ROOT"; exit 2; }
{ echo "sampled_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "uptime = $(uptime)"
  echo "nproc = $(nproc)"
  echo "loadavg = $(cut -d' ' -f1-3 /proc/loadavg)"
  echo "mem_available_MB = $(free -m | awk 'NR==2{print $7}')"
  echo "-- other solver processes on the box at launch --"
  ps -eo comm= | grep -E 'Foam|foam|python3|docker' | sort | uniq -c | sort -rn | head -12
  echo "note = contention at launch; core-minutes are wall_s*RANKS/60 and a busy box inflates wall_s (COMPUTE_BUDGET_CHARTER sec.6: waste is reported, never absorbed)"
} > "$RUN_ROOT/CONTENTION.txt" 2>&1

LR="$RUN_ROOT/LAUNCH_RECORD.txt"
{ echo "case = VMFL011-R3"
  echo "supersedes = register row #26 (VMFL011, NOT A RESULT) -- a NEW row, the old one is never overwritten"
  echo "launched_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "freeze_commit_head = $FREEZE_COMMIT"
  echo "prereg = $PREREG_REL"
  echo "prereg_blob = $PREREG_BLOB"
  echo "comparator = $GRADER_REL"
  echo "comparator_blob = $GRADER_BLOB"
  echo "launcher_blob_on_disk = $(git -C "$REPO" hash-object "$0")"
  echo "levels = $LEVELS_TO_RUN"
  echo "ranks = $RANKS"
  echo "cap_core_min = $CAP_CORE_MIN  (RUNNING TOTAL across levels, byte-identical to attempt 1)"
  echo "endTime = $ENDTIME"
  echo "smoke_mode = ${VMFL_SMOKE:-no}"
} > "$LR" || { echo "ABORT: cannot write LAUNCH_RECORD.txt"; exit 2; }

# --- OpenFOAM ------------------------------------------------------------------
# L-343 USER PIN, BEFORE the bashrc is sourced and gated explicitly.
# /usr/lib/openfoam/openfoam2606/etc/bashrc:190 reads
#   export WM_PROJECT_USER_DIR="$HOME/$WM_PROJECT/${USER:-user}-$WM_PROJECT_VERSION"
# A cron-started queue runner carries LOGNAME but NO USER (measured on this box,
# pid 459727), so FOAM_USER_LIBBIN would resolve to a `user-v2606` directory that
# does not exist and any user-built library would silently vanish from the
# launched solver's path.  This case links no user library, so the pin cannot
# change a number here -- it is applied anyway because the launcher must be
# correct under the runner it will actually be launched by, and USER, id -un and
# FOAM_USER_LIBBIN are RECORDED as infrastructure fields (L-342, L-343 rule 1).
export USER="${USER:-${LOGNAME:-$(id -un)}}"
[ -n "$USER" ] || { echo "ABORT: cannot resolve USER for the OpenFOAM bashrc (L-343)"; exit 2; }
source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo "ABORT: cannot source /usr/lib/openfoam/openfoam2606/etc/bashrc"; exit 2; }
{ echo "user_env = $USER"
  echo "id_un = $(id -un)"
  echo "foam_user_libbin = ${FOAM_USER_LIBBIN:-unset}"
  echo "wm_project_user_dir = ${WM_PROJECT_USER_DIR:-unset}"
} >> "$LR"
echo "  L-343 USER pin: USER=$USER  id -un=$(id -un)  FOAM_USER_LIBBIN=${FOAM_USER_LIBBIN:-unset}"
command -v simpleFoam >/dev/null || { echo "ABORT: simpleFoam not on PATH after sourcing the v2606 bashrc"; exit 2; }
command -v blockMesh  >/dev/null || { echo "ABORT: blockMesh not on PATH"; exit 2; }
SOLVER_BIN="$(command -v simpleFoam)"
echo "solver_bin = $SOLVER_BIN" >> "$LR"
echo "  simpleFoam = $SOLVER_BIN"

TOTAL_CORE_MIN=0
OVERALL_RC=0

for L in $LEVELS_TO_RUN; do
  OUT="$RUN_ROOT/$L"
  [ -n "${NB[$L]}" ] || { echo "ABORT: no registered mesh counts for level $L"; exit 2; }

  # AGE GUARD (rule 4): refuse a level directory that already holds 0/ or a time dir.
  # NO `[0-9]*` glob anywhere -- L-339: such a glob also matches `0.orig` and reads a
  # template directory as an existing answer.  Numeric time dirs are matched by regex.
  if [ -d "$OUT/0" ]; then echo "ABORT age guard: $OUT already holds 0/ -- a run is never launched into a tree that already holds an answer"; exit 2; fi
  EXISTING_T="$(find "$OUT" -mindepth 1 -maxdepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?([eE][-+][0-9]+)?$' 2>/dev/null | head -1)"
  [ -z "$EXISTING_T" ] || { echo "ABORT age guard: $OUT already holds a numeric time directory ($EXISTING_T)"; exit 2; }

  # CAP ENFORCEMENT: the RUNNING-TOTAL drawdown, in the executable path.
  REMAIN="$(python3 -c "print(max(0.0, $CAP_CORE_MIN - $TOTAL_CORE_MIN))")" || { echo "ABORT: cap arithmetic failed for $L"; exit 2; }
  TIMEOUT_S="$(python3 -c "print(int($REMAIN * 60 / $RANKS))")" || { echo "ABORT: timeout arithmetic failed for $L"; exit 2; }
  [ "$TIMEOUT_S" -gt 0 ] || { echo "ABORT: BUDGET EXHAUSTED before $L (spent $TOTAL_CORE_MIN of $CAP_CORE_MIN core-min). An overrun STOPS the run and does NOT get a new budget (rule 12)."; exit 2; }
  echo "--- $L  remaining ${REMAIN} of ${CAP_CORE_MIN} core-min  ranks ${RANKS}  timeout ${TIMEOUT_S}s"

  mkdir -p "$OUT" || { echo "ABORT: mkdir $OUT"; exit 2; }
  cp -r "$CASE_DIR"/0 "$CASE_DIR"/constant "$CASE_DIR"/system "$OUT"/ || { echo "ABORT: cannot copy the case templates into $OUT"; exit 2; }
  sed -e "s/__NB__/${NB[$L]}/g" -e "s/__NH__/${NH[$L]}/g" \
      "$OUT/system/blockMeshDict.template" > "$OUT/system/blockMeshDict" || { echo "ABORT: sed blockMeshDict for $L"; exit 2; }
  grep -q '__NB__\|__NH__' "$OUT/system/blockMeshDict" && { echo "ABORT: blockMeshDict substitution did not take at $L"; exit 2; }
  sed -e "s/__ENDTIME__/$ENDTIME/g" "$OUT/system/controlDict.template" > "$OUT/system/controlDict" || { echo "ABORT: sed controlDict for $L"; exit 2; }
  grep -qE "^stopAt +endTime; +endTime +$ENDTIME;" "$OUT/system/controlDict" || { echo "ABORT: controlDict endTime is not the registered $ENDTIME at $L"; exit 2; }

  ( cd "$OUT" && blockMesh > log.blockMesh 2>&1 ) || { echo "ABORT: blockMesh failed at $L -- a crash is a FINDING, not a retry"; exit 2; }
  ( cd "$OUT" && checkMesh > log.checkMesh 2>&1 )

  # MESH BIRTH CERTIFICATE, minted from this level's own checkMesh (MESH_STANDARD sec.6)
  python3 - "$OUT" "$L" <<'PYBC' || { echo "ABORT: could not mint the mesh birth certificate"; exit 2; }
import json, re, sys, os, subprocess, datetime
out, lvl = sys.argv[1], sys.argv[2]
t = open(os.path.join(out, 'log.checkMesh'), errors='replace').read()
def g(pat, cast=float):
    m = re.search(pat, t)
    return cast(m.group(1)) if m else None
bc = {'level': lvl, 'cells': g(r'cells:\s+(\d+)', int), 'points': g(r'points:\s+(\d+)', int),
      'faces': g(r'faces:\s+(\d+)', int), 'max_aspect_ratio': g(r'Max aspect ratio = ([0-9.eE+-]+)'),
      'max_skewness': g(r'Max skewness = ([0-9.eE+-]+)'),
      'max_non_orthogonality': g(r'non-orthogonality Max: ([0-9.eE+-]+)'),
      'mesh_ok': 'Mesh OK' in t, 'failed_checks': g(r'Failed (\d+) mesh checks', int) or 0,
      'blockMeshDict_sha': subprocess.run(['git','hash-object',os.path.join(out,'system','blockMeshDict')],capture_output=True,text=True).stdout.strip(),
      'minted_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
json.dump(bc, open(os.path.join(out, 'birth_certificate.json'), 'w'), indent=2, sort_keys=True)
print('  birth certificate: cells=%s meshOK=%s maxSkew=%s maxAR=%s' % (bc['cells'], bc['mesh_ok'], bc['max_skewness'], bc['max_aspect_ratio']))
PYBC

  # per-level pre-record so a killed launcher still leaves the cap it was under
  printf 'level=%s\nstate=STARTED\nranks=%d\ncap_core_min=%s\nremaining_core_min=%s\ntimeout_s=%d\nendTime=%s\nprereg_blob=%s\ncomparator_blob=%s\nstarted_utc=%s\nnote=RUNNING-TOTAL drawdown, byte-identical to attempt 1. This file is an L-342 INFRASTRUCTURE artifact: the comparator gates on the physics artefacts and reports rc NOT MEASURED if this file is absent.\n' \
    "$L" "$RANKS" "$CAP_CORE_MIN" "$REMAIN" "$TIMEOUT_S" "$ENDTIME" "$PREREG_BLOB" "$GRADER_BLOB" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$RUN_ROOT/RUN_RC.$L" \
    || { echo "ABORT: cannot write RUN_RC.$L"; exit 2; }

  # 0/ is touched LAST, immediately before the solver: it is the age-guard datum
  # that dates the run allowed to produce the answer (CLAUDE.md rule 4).
  touch "$OUT"/0/* || { echo "ABORT: cannot touch $OUT/0"; exit 2; }

  T0="$(date +%s)"
  # DETACHED SOLVER (L-336): setsid makes the solver its own session leader so it
  # survives the launching lane's death.  THE rc IS CAPTURED INSIDE the subshell,
  # immediately after `timeout` returns, and written to disk there -- so the number
  # that reaches RUN_RC.$L is the SOLVER's own status and not one invented by any
  # later stage of the wrapper.  Detachment is verified by the WRAPPER's SID == PID
  # (field 6 of /proc/<pid>/stat), never by the solver's ppid.
  rm -f "$OUT/.solver_rc"
  (
    cd "$OUT" || exit 90
    setsid timeout "${TIMEOUT_S}"s simpleFoam > log.simpleFoam 2>&1
    SRC=$?
    echo "$SRC" > .solver_rc
    exit "$SRC"
  ) &
  SOLVER_PID=$!
  WSID=""
  for _try in $(seq 1 100); do WSID="$(awk '{print $6}' /proc/$SOLVER_PID/stat 2>/dev/null)"; [ -n "$WSID" ] && break; done
  wait "$SOLVER_PID"
  WAIT_RC=$?
  if [ -f "$OUT/.solver_rc" ]; then RC="$(cat "$OUT/.solver_rc")"; else RC="$WAIT_RC"; fi
  T1="$(date +%s)"
  WALL=$((T1-T0))
  CORE_MIN="$(python3 -c "print(round($WALL*$RANKS/60.0, 4))")"
  TOTAL_CORE_MIN="$(python3 -c "print(round($TOTAL_CORE_MIN + $CORE_MIN, 4))")"

  # latest numeric time directory, by REGEX -- never a `[0-9]*` glob (L-339).
  ENDT_DIR=""; ENDT_OK="no"
  for D in $(find "$OUT" -mindepth 1 -maxdepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?([eE][-+][0-9]+)?$' 2>/dev/null); do
    B="$(basename "$D")"
    if python3 -c "import sys;sys.exit(0 if float(sys.argv[1])>0 else 1)" "$B" 2>/dev/null; then
      if [ -z "$ENDT_DIR" ] || python3 -c "import sys;sys.exit(0 if float(sys.argv[1])>float(sys.argv[2]) else 1)" "$B" "$(basename "$ENDT_DIR")"; then ENDT_DIR="$D"; fi
    fi
  done
  if [ -n "$ENDT_DIR" ] && [ -f "$ENDT_DIR/U" ] && [ "$ENDT_DIR/U" -nt "$OUT/0/U" ]; then ENDT_OK="yes"; fi
  LAST_TIME="$(grep -E '^Time = ' "$OUT/log.simpleFoam" 2>/dev/null | tail -1 | sed -E 's/^Time = //')"
  ENDED="$(grep -cE '^End' "$OUT/log.simpleFoam" 2>/dev/null)"

  # THE MEASURED rc GOES TO DISK on BOTH the success and the abort path.
  printf 'rc = %s\nlevel = %s\nstate = FINISHED\nwait_rc = %d\nwall_s = %d\nranks = %d\ncore_min = %s\ntotal_core_min_so_far = %s\ntimeout_s = %d\ncap_core_min = %s\nendTime = %s\nlast_time_in_log = %s\nEnd_lines = %s\nlatest_time_dir = %s\nfield_at_latest_newer_than_0_U = %s\ndetach_wrapper_pid = %s\ndetach_wrapper_sid = %s\nprereg_blob = %s\ncomparator_blob = %s\nsolver_bin = %s\nutc = %s\nnote = rc is simpleFoam exit status under timeout, CAPTURED INSIDE the detached subshell; 124 means the RUNNING-TOTAL cap fired. endTime is NEVER reduced to fit a cap (rule 12). L-342: this file is INFRASTRUCTURE -- absent, the comparator reports rc NOT MEASURED and grades the physics artefacts.\n' \
    "$RC" "$L" "$WAIT_RC" "$WALL" "$RANKS" "$CORE_MIN" "$TOTAL_CORE_MIN" "$TIMEOUT_S" "$CAP_CORE_MIN" "$ENDTIME" "${LAST_TIME:-none}" "${ENDED:-0}" "${ENDT_DIR:-none}" "$ENDT_OK" "$SOLVER_PID" "${WSID:-unknown}" "$PREREG_BLOB" "$GRADER_BLOB" "$SOLVER_BIN" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    > "$RUN_ROOT/RUN_RC.$L" || { echo "ABORT: cannot write RUN_RC.$L"; exit 2; }

  if [ "$WSID" = "$SOLVER_PID" ]; then echo "  detach OK ($L): wrapper pid=$SOLVER_PID is a session leader (SID==PID)"; else echo "  DETACH WARN ($L): wrapper pid=$SOLVER_PID SID=${WSID:-unknown} -- not a session leader"; fi
  { echo "level $L : rc=$RC wall_s=$WALL core_min=$CORE_MIN total=$TOTAL_CORE_MIN cap=$CAP_CORE_MIN timeout_s=$TIMEOUT_S last_time=${LAST_TIME:-none} End_lines=${ENDED:-0} latest_time_dir=${ENDT_DIR:-none} field_newer_than_0_U=$ENDT_OK"; } >> "$LR"

  # STOP AT THE FIRST NON-ZERO rc.
  if [ "$RC" -ne 0 ]; then
    OVERALL_RC="$RC"
    echo "STOP $L: rc=$RC after ${WALL}s = ${CORE_MIN} core-min (running total ${TOTAL_CORE_MIN} of ${CAP_CORE_MIN})."
    echo "  A non-zero rc is a FINDING, not a retry. rc=124 means the running-total cap stopped it;"
    echo "  an overrun does NOT get a new budget and endTime is NOT shrunk to fit (rule 12)."
    echo "later levels are NOT launched" >> "$LR"
    break
  fi
  echo "done $L: ${WALL}s = ${CORE_MIN} core-min (running total ${TOTAL_CORE_MIN} of ${CAP_CORE_MIN}), latest time dir ${ENDT_DIR:-none}"
done

printf 'total_core_min = %s\ncap_core_min = %s\nranks = %d\noverall_rc = %s\nsmoke_mode = %s\ncost_basis = owner-stated rate $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22); REPORTED-BY-OWNER, NOT MEASURED -- the box cannot read its own billing (COMPUTE_BUDGET_CHARTER.md sec.5). Dollars are DERIVED.\n' \
  "$TOTAL_CORE_MIN" "$CAP_CORE_MIN" "$RANKS" "$OVERALL_RC" "${VMFL_SMOKE:-no}" > "$RUN_ROOT/COST.txt" || { echo "ABORT: cannot write COST.txt"; exit 2; }
echo "total_core_min = $TOTAL_CORE_MIN" >> "$LR"
echo "finished_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LR"
echo "=== VMFL011-R3 launcher done, overall rc=$OVERALL_RC, total ${TOTAL_CORE_MIN} core-min of ${CAP_CORE_MIN}"
echo "grade with: python3 $SCRIPT_DIR/grade_vmfl011_r3.py --run-root $RUN_ROOT"
exit "$OVERALL_RC"
