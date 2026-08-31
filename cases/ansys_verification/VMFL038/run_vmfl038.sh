#!/usr/bin/env bash
# =============================================================================
# VMFL038 graded-run driver -- Falling Film Over an Inclined Plane.
# Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p.131-132.
# Solver: simpleFoam (OpenFOAM v2606), steady incompressible laminar, 2-D planar,
# pressure-driven film. Reference: Bird/Stewart/Lightfoot p.45 (ANALYTICAL).
#
# Frozen pre-registration: cases/ansys_verification/VMFL038/PREREGISTRATION.md
# Frozen comparator      : cases/ansys_verification/VMFL038/grade_vmfl038.py
# Run root               : verification/runs/ansys_verification/VMFL038/
#
# Modelled on cases/ansys_verification/VMFL063/run_vmfl063.sh with the VMFL038
# specifics substituted. THE MESH FAMILY REFINES ONE DIRECTION: Nx is fixed at 180
# and Ny doubles per level (40 / 80 / 160), because the wall-shear truncation error
# lives in the film-normal direction only (PREREGISTRATION sec.4).
#
# NO `set -u` (incompatible with OpenFOAM v2606 bashrc); every check gates EXPLICITLY.
# THE CAP IS A RUNNING TOTAL across the three solves; an overrun STOPS the run
# (rc 124) and endTime is NEVER reduced to fit a cap (CLAUDE.md rule 12).
# =============================================================================

RANKS=1
CAP_CORE_MIN=15         # RUNNING TOTAL across L1+L2+L3 (PREREGISTRATION sec.7)
ENDTIME=30000           # iteration ceiling; residualControl { p 1e-10 } stops it earlier

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CASE_DIR="$SCRIPT_DIR/case"
RUN_ROOT="${1:?usage: run_vmfl038.sh <run_root> [levels...]}"
shift 2>/dev/null
LEVELS_TO_RUN="${*:-L1 L2 L3}"

# r = 2 film-normal triple: Ny doubles per level; Nx fixed at 180 (frozen sec.4).
declare -A NY=( [L1]=40 [L2]=80 [L3]=160 )

echo "=== VMFL038 launcher  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)  run_root=$RUN_ROOT"

# --- smoke mode (CHARTER Amendment 1.4 Clause B): scratch ONLY -----------------
SMOKE_ENDTIME=10
if [ -n "$VMFL_SMOKE" ]; then
  case "$RUN_ROOT" in
    */scratchpad/*|*/scratchpad) : ;;
    *) echo "ABORT: VMFL_SMOKE refuses run_root '$RUN_ROOT' -- a smoke runs in scratch ONLY, never in the graded run root"; exit 2 ;;
  esac
  LEVELS_TO_RUN="L1"
  ENDTIME="$SMOKE_ENDTIME"
  echo "  SMOKE MODE: L1 only, endTime $SMOKE_ENDTIME IN THE SCRATCH COPY ONLY; grades nothing"
fi

# --- 1. LAUNCH-TIME FREEZE CHECK (CLAUDE.md rule 2) ---------------------------
REPO="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || { echo "ABORT: not inside a git repository"; exit 2; }
PREREG_REL="cases/ansys_verification/VMFL038/PREREGISTRATION.md"
GRADER_REL="cases/ansys_verification/VMFL038/grade_vmfl038.py"
FREEZE_COMMIT="$(git -C "$REPO" rev-parse HEAD)" || { echo "ABORT: cannot resolve HEAD"; exit 2; }
for REL in "$PREREG_REL" "$GRADER_REL"; do
  git -C "$REPO" cat-file -e "HEAD:$REL" 2>/dev/null || { echo "ABORT: $REL is NOT committed at HEAD -- the freeze IS the evidence (rule 2)"; exit 2; }
  HEADSHA="$(git -C "$REPO" rev-parse "HEAD:$REL")" || { echo "ABORT: cannot resolve HEAD blob of $REL"; exit 2; }
  DISKSHA="$(git -C "$REPO" hash-object "$REPO/$REL")" || { echo "ABORT: cannot hash $REL on disk"; exit 2; }
  [ "$DISKSHA" = "$HEADSHA" ] || { echo "ABORT freeze check: $REL on disk ($DISKSHA) != HEAD blob ($HEADSHA). The file that would run is NOT the file that was frozen."; exit 2; }
  echo "  freeze OK  $REL  $DISKSHA"
  case "$REL" in
    "$PREREG_REL") PREREG_BLOB="$DISKSHA" ;;
    "$GRADER_REL") GRADER_BLOB="$DISKSHA" ;;
  esac
done

# --- CASE INPUTS: every one hashed against its OWN HEAD blob -------------------
for F in 0/U 0/p constant/transportProperties constant/momentumTransport \
         constant/turbulenceProperties system/blockMeshDict.template \
         system/controlDict.template system/fvSchemes system/fvSolution; do
  A="$(git -C "$REPO" rev-parse "HEAD:cases/ansys_verification/VMFL038/case/$F" 2>/dev/null)" || { echo "ABORT: case/$F is not committed at HEAD"; exit 2; }
  B="$(git -C "$REPO" hash-object "$CASE_DIR/$F")" || { echo "ABORT: cannot hash case/$F"; exit 2; }
  [ "$A" = "$B" ] || { echo "ABORT: case/$F on disk ($B) != HEAD blob ($A) -- the case that would run is not the case that was frozen"; exit 2; }
done
echo "  case inputs OK: 9 files, each byte-identical to its HEAD blob"

# --- CONTROLS: the comparator's own --selftest, BOTH interpreters --------------
ST="/tmp/vmfl038_selftest.$$"
rm -rf "$SCRIPT_DIR/__pycache__"
python3    "$SCRIPT_DIR/grade_vmfl038.py" --selftest > "$ST"   2>&1; RC_PLAIN=$?
[ "$RC_PLAIN" = "0" ] || { echo "ABORT: comparator --selftest is NOT green under python3 (rc $RC_PLAIN); see $ST"; exit 2; }
rm -rf "$SCRIPT_DIR/__pycache__"
python3 -O "$SCRIPT_DIR/grade_vmfl038.py" --selftest > "$ST.O" 2>&1; RC_O=$?
[ "$RC_O" = "0" ] || { echo "ABORT: comparator --selftest is NOT green under python3 -O (rc $RC_O); see $ST.O"; exit 2; }
NP_PLAIN="$(grep -c '^  \[PASS\]' "$ST")";   NP_O="$(grep -c '^  \[PASS\]' "$ST.O")"
NF_PLAIN="$(grep -c '^  \[FAIL\]' "$ST")";   NF_O="$(grep -c '^  \[FAIL\]' "$ST.O")"
AST_MARK='AST guard: ast.Assert count is 0 in this file'
[ "$NP_PLAIN" = "$NP_O" ] || { echo "ABORT: --selftest PASS COUNT differs -- python3 $NP_PLAIN vs python3 -O $NP_O (L-332)"; exit 2; }
[ "$NF_PLAIN" = "$NF_O" ] || { echo "ABORT: --selftest FAIL COUNT differs (L-332)"; exit 2; }
[ "$RC_PLAIN" = "$RC_O" ] || { echo "ABORT: --selftest EXIT RC differs (L-332)"; exit 2; }
grep -qF "$AST_MARK" "$ST"   || { echo "ABORT: --selftest did not print the AST GUARD MARKER under python3"; exit 2; }
grep -qF "$AST_MARK" "$ST.O" || { echo "ABORT: --selftest did not print the AST GUARD MARKER under python3 -O (L-332)"; exit 2; }
grep -q '^SELFTEST: all checks passed' "$ST" || { echo "ABORT: --selftest printed no all-checks-passed line"; exit 2; }
grep -q '^  \[FAIL\]' "$ST" && { echo "ABORT: --selftest printed a FAIL line"; exit 2; }
for MARK in \
  'AST guard: ast.Assert count is 0 in this file' \
  'one_match REFUSES on two matches' \
  'time dirs sort NUMERICALLY' \
  'wall-shear REFUSES a non-developed' \
  'planted zero P1a' \
  'planted zero P1b' \
  'BLIND writer' \
  'GATE FAIL: CONVERGING but the value is OUTSIDE' \
  'EXACT triple, even with the value' \
  'GCI > GCI_MAX' ; do
  grep -qF "$MARK" "$ST" || { echo "ABORT: --selftest did not DRIVE the control: $MARK"; exit 2; }
done
NCHK="$(grep -c '^  \[PASS\]' "$ST")"
echo "  controls OK: --selftest $NCHK/$NCHK PASS; python3 and python3 -O agree on PASS $NP_PLAIN/$NP_O, FAIL $NF_PLAIN/$NF_O, rc $RC_PLAIN/$RC_O; AST marker in both"
rm -f "$ST" "$ST.O"

# --- run root, contention record, launch record -------------------------------
mkdir -p "$RUN_ROOT" || { echo "ABORT: cannot create $RUN_ROOT"; exit 2; }
{ echo "sampled_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "uptime = $(uptime)"; echo "nproc = $(nproc)"
  echo "loadavg = $(cut -d' ' -f1-3 /proc/loadavg)"
  echo "mem_available_MB = $(free -m | awk 'NR==2{print $7}')"
  echo "-- other solver processes at launch --"
  ps -eo comm= | grep -E 'Foam|foam|python3|docker' | sort | uniq -c | sort -rn | head -12
  echo "note = a busy box inflates wall_s; core-min = wall_s*RANKS/60 (COMPUTE_BUDGET_CHARTER sec.6)"
} > "$RUN_ROOT/CONTENTION.txt" 2>&1

LR="$RUN_ROOT/LAUNCH_RECORD.txt"
{ echo "case = VMFL038"; echo "manual_page = 131-132"
  echo "supersedes = nothing -- FIRST registration of this case"
  echo "launched_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "freeze_commit_head = $FREEZE_COMMIT"
  echo "prereg = $PREREG_REL"; echo "prereg_blob = $PREREG_BLOB"
  echo "comparator = $GRADER_REL"; echo "comparator_blob = $GRADER_BLOB"
  echo "launcher_blob_on_disk = $(git -C "$REPO" hash-object "$0")"
  echo "levels = $LEVELS_TO_RUN"; echo "ranks = $RANKS"
  echo "cap_core_min = $CAP_CORE_MIN  (RUNNING TOTAL across levels)"
  echo "endTime = $ENDTIME"; echo "smoke_mode = ${VMFL_SMOKE:-no}"
} > "$LR" || { echo "ABORT: cannot write LAUNCH_RECORD.txt"; exit 2; }

# --- OpenFOAM ------------------------------------------------------------------
source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo "ABORT: cannot source openfoam2606 bashrc"; exit 2; }
command -v simpleFoam >/dev/null || { echo "ABORT: simpleFoam not on PATH"; exit 2; }
command -v blockMesh  >/dev/null || { echo "ABORT: blockMesh not on PATH"; exit 2; }
SOLVER_BIN="$(command -v simpleFoam)"
echo "solver_bin = $SOLVER_BIN" >> "$LR"; echo "  simpleFoam = $SOLVER_BIN"

TOTAL_CORE_MIN=0
OVERALL_RC=0

for L in $LEVELS_TO_RUN; do
  OUT="$RUN_ROOT/$L"
  [ -n "${NY[$L]}" ] || { echo "ABORT: no registered mesh counts for level $L"; exit 2; }

  # AGE GUARD (rule 4): refuse a level dir already holding 0/ or a numeric time dir.
  if [ -d "$OUT/0" ]; then echo "ABORT age guard: $OUT already holds 0/"; exit 2; fi
  EXISTING_T="$(find "$OUT" -mindepth 1 -maxdepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?([eE][-+][0-9]+)?$' 2>/dev/null | head -1)"
  [ -z "$EXISTING_T" ] || { echo "ABORT age guard: $OUT already holds a numeric time directory ($EXISTING_T)"; exit 2; }

  # CAP: RUNNING-TOTAL drawdown in the executable path.
  REMAIN="$(python3 -c "print(max(0.0, $CAP_CORE_MIN - $TOTAL_CORE_MIN))")" || { echo "ABORT: cap arithmetic failed for $L"; exit 2; }
  TIMEOUT_S="$(python3 -c "print(int($REMAIN * 60 / $RANKS))")" || { echo "ABORT: timeout arithmetic failed for $L"; exit 2; }
  [ "$TIMEOUT_S" -gt 0 ] || { echo "ABORT: BUDGET EXHAUSTED before $L (spent $TOTAL_CORE_MIN of $CAP_CORE_MIN core-min). An overrun STOPS the run (rule 12)."; exit 2; }
  echo "--- $L  Ny=${NY[$L]}  remaining ${REMAIN} of ${CAP_CORE_MIN} core-min  timeout ${TIMEOUT_S}s"

  mkdir -p "$OUT" || { echo "ABORT: mkdir $OUT"; exit 2; }
  cp -r "$CASE_DIR"/0 "$CASE_DIR"/constant "$CASE_DIR"/system "$OUT"/ || { echo "ABORT: cannot copy case templates into $OUT"; exit 2; }
  sed -e "s/__NY__/${NY[$L]}/g" "$OUT/system/blockMeshDict.template" > "$OUT/system/blockMeshDict" || { echo "ABORT: sed blockMeshDict for $L"; exit 2; }
  grep -q '__NY__' "$OUT/system/blockMeshDict" && { echo "ABORT: blockMeshDict substitution did not take at $L"; exit 2; }
  sed -e "s/__ENDTIME__/$ENDTIME/g" "$OUT/system/controlDict.template" > "$OUT/system/controlDict" || { echo "ABORT: sed controlDict for $L"; exit 2; }
  grep -qE "^endTime[[:space:]]+$ENDTIME;" "$OUT/system/controlDict" || { echo "ABORT: controlDict endTime is not the registered $ENDTIME at $L"; exit 2; }

  ( cd "$OUT" && blockMesh > log.blockMesh 2>&1 ) || { echo "ABORT: blockMesh failed at $L -- a crash is a FINDING, not a retry"; exit 2; }
  ( cd "$OUT" && checkMesh > log.checkMesh 2>&1 )

  # MESH BIRTH CERTIFICATE (MESH_STANDARD sec.6)
  python3 - "$OUT" "$L" <<'PYBC' || { echo "ABORT: could not mint the mesh birth certificate"; exit 2; }
import json, re, sys, os, subprocess, datetime
out, lvl = sys.argv[1], sys.argv[2]
t = open(os.path.join(out, 'log.checkMesh'), errors='replace').read()
def g(pat, cast=float):
    m = re.search(pat, t); return cast(m.group(1)) if m else None
bc = {'level': lvl, 'cells': g(r'cells:\s+(\d+)', int), 'points': g(r'points:\s+(\d+)', int),
      'faces': g(r'faces:\s+(\d+)', int), 'max_aspect_ratio': g(r'Max aspect ratio = ([0-9.eE+-]+)'),
      'max_skewness': g(r'Max skewness = ([0-9.eE+-]+)'),
      'max_non_orthogonality': g(r'non-orthogonality Max: ([0-9.eE+-]+)'),
      'mesh_ok': 'Mesh OK' in t, 'failed_checks': g(r'Failed (\d+) mesh checks', int) or 0,
      'blockMeshDict_sha': subprocess.run(['git','hash-object',os.path.join(out,'system','blockMeshDict')],capture_output=True,text=True).stdout.strip(),
      'minted_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
json.dump(bc, open(os.path.join(out, 'birth_certificate.json'), 'w'), indent=2, sort_keys=True)
print('  birth certificate: cells=%s meshOK=%s maxSkew=%s maxAR=%s maxNonOrtho=%s' % (bc['cells'], bc['mesh_ok'], bc['max_skewness'], bc['max_aspect_ratio'], bc['max_non_orthogonality']))
PYBC

  printf 'level=%s\nstate=STARTED\nranks=%d\ncap_core_min=%s\nremaining_core_min=%s\ntimeout_s=%d\nendTime=%s\nprereg_blob=%s\ncomparator_blob=%s\nstarted_utc=%s\nnote=RUNNING-TOTAL drawdown. L-342 INFRASTRUCTURE artifact.\n' \
    "$L" "$RANKS" "$CAP_CORE_MIN" "$REMAIN" "$TIMEOUT_S" "$ENDTIME" "$PREREG_BLOB" "$GRADER_BLOB" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$RUN_ROOT/RUN_RC.$L" \
    || { echo "ABORT: cannot write RUN_RC.$L"; exit 2; }

  # 0/ touched LAST, immediately before the solver: the age-guard datum (rule 4).
  touch "$OUT"/0/* || { echo "ABORT: cannot touch $OUT/0"; exit 2; }

  T0="$(date +%s)"
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
  wait "$SOLVER_PID"; WAIT_RC=$?
  if [ -f "$OUT/.solver_rc" ]; then RC="$(cat "$OUT/.solver_rc")"; else RC="$WAIT_RC"; fi
  T1="$(date +%s)"; WALL=$((T1-T0))
  CORE_MIN="$(python3 -c "print(round($WALL*$RANKS/60.0, 4))")"
  TOTAL_CORE_MIN="$(python3 -c "print(round($TOTAL_CORE_MIN + $CORE_MIN, 4))")"

  # Cx, Cy at the converged time (wall-face abscissae + cell-centre rows). On success.
  if [ "$RC" -eq 0 ]; then
    ( cd "$OUT" && postProcess -func writeCellCentres -latestTime > log.writeCellCentres 2>&1 ) || echo "  WARN: writeCellCentres failed at $L (the grader will REFUSE on missing Cx/Cy)"
  fi

  ENDT_DIR=""
  for D in $(find "$OUT" -mindepth 1 -maxdepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?([eE][-+][0-9]+)?$' 2>/dev/null); do
    B="$(basename "$D")"
    if python3 -c "import sys;sys.exit(0 if float(sys.argv[1])>0 else 1)" "$B" 2>/dev/null; then
      if [ -z "$ENDT_DIR" ] || python3 -c "import sys;sys.exit(0 if float(sys.argv[1])>float(sys.argv[2]) else 1)" "$B" "$(basename "$ENDT_DIR")"; then ENDT_DIR="$D"; fi
    fi
  done
  LAST_TIME="$(grep -E '^Time = ' "$OUT/log.simpleFoam" 2>/dev/null | tail -1 | sed -E 's/^Time = //')"
  ENDED="$(grep -cE '^End$' "$OUT/log.simpleFoam" 2>/dev/null)"
  CONVERGED="$(grep -c 'SIMPLE solution converged' "$OUT/log.simpleFoam" 2>/dev/null)"

  printf 'rc = %s\nlevel = %s\nstate = FINISHED\nwait_rc = %d\nwall_s = %d\nranks = %d\ncore_min = %s\ntotal_core_min_so_far = %s\ntimeout_s = %d\ncap_core_min = %s\nendTime = %s\nlast_time_in_log = %s\nEnd_lines = %s\nSIMPLE_converged_lines = %s\nlatest_time_dir = %s\nny = %s\ndetach_wrapper_pid = %s\ndetach_wrapper_sid = %s\nprereg_blob = %s\ncomparator_blob = %s\nsolver_bin = %s\nutc = %s\nnote = rc captured INSIDE the detached subshell; 124 = the RUNNING-TOTAL cap fired. endTime is NEVER reduced to fit a cap (rule 12). L-342 INFRASTRUCTURE.\n' \
    "$RC" "$L" "$WAIT_RC" "$WALL" "$RANKS" "$CORE_MIN" "$TOTAL_CORE_MIN" "$TIMEOUT_S" "$CAP_CORE_MIN" "$ENDTIME" "${LAST_TIME:-none}" "${ENDED:-0}" "${CONVERGED:-0}" "${ENDT_DIR:-none}" "${NY[$L]}" "$SOLVER_PID" "${WSID:-unknown}" "$PREREG_BLOB" "$GRADER_BLOB" "$SOLVER_BIN" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    > "$RUN_ROOT/RUN_RC.$L" || { echo "ABORT: cannot write RUN_RC.$L"; exit 2; }

  { echo "level $L : rc=$RC wall_s=$WALL core_min=$CORE_MIN total=$TOTAL_CORE_MIN cap=$CAP_CORE_MIN timeout_s=$TIMEOUT_S last_time=${LAST_TIME:-none} End_lines=${ENDED:-0} converged_lines=${CONVERGED:-0} latest_time_dir=${ENDT_DIR:-none}"; } >> "$LR"

  if [ "$RC" -ne 0 ]; then
    OVERALL_RC="$RC"
    echo "STOP $L: rc=$RC after ${WALL}s = ${CORE_MIN} core-min (running total ${TOTAL_CORE_MIN} of ${CAP_CORE_MIN})."
    echo "  A non-zero rc is a FINDING, not a retry. rc=124 means the running-total cap stopped it (rule 12)."
    echo "later levels are NOT launched" >> "$LR"
    break
  fi
  echo "done $L: ${WALL}s = ${CORE_MIN} core-min (running total ${TOTAL_CORE_MIN} of ${CAP_CORE_MIN}), latest time dir ${ENDT_DIR:-none}"
done

printf 'total_core_min = %s\ncap_core_min = %s\nranks = %d\noverall_rc = %s\nsmoke_mode = %s\ncost_basis = owner-stated rate $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22); REPORTED-BY-OWNER, NOT MEASURED -- the box cannot read its own billing (COMPUTE_BUDGET_CHARTER.md sec.5). Dollars are DERIVED.\n' \
  "$TOTAL_CORE_MIN" "$CAP_CORE_MIN" "$RANKS" "$OVERALL_RC" "${VMFL_SMOKE:-no}" > "$RUN_ROOT/COST.txt" || { echo "ABORT: cannot write COST.txt"; exit 2; }
echo "total_core_min = $TOTAL_CORE_MIN" >> "$LR"
echo "finished_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LR"
echo "=== VMFL038 launcher done, overall rc=$OVERALL_RC, total ${TOTAL_CORE_MIN} core-min of ${CAP_CORE_MIN}"
echo "grade with: python3 $SCRIPT_DIR/grade_vmfl038.py --run-root $RUN_ROOT --out $RUN_ROOT/GRADING_VMFL038.json"
exit "$OVERALL_RC"
