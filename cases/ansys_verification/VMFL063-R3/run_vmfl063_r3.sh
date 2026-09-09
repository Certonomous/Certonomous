#!/bin/bash
# =============================================================================
# VMFL063-R3 LAUNCHER -- domain-independence study for Separated Laminar Flow Over
# a Blunt Plate (VM2026R1 p.193). PREREGISTRATION.md sec.4/5/11.
#
# STAGES:
#   1. LADDER  : solve D0,D1,D2 (de-confined top) + D0_CONFINED (symmetryPlane top,
#                BC-isolation diagnostic), all at the FIXED R2-L3 grid, meshes from
#                the frozen gen_domain_mesh.py.
#   2. PICK D* : grade_vmfl063_r3.py --pick-dstar applies the frozen LR-self-
#                convergence rule (DOMAIN_TOL, never the Target 4.0) -> D* or
#                NOT_CONVERGED. If NOT_CONVERGED the gate is not built (the grader
#                emits ROW NOT A RESULT; PREREGISTRATION outcome 5).
#   3. GATE    : build the BYTE-IDENTICAL R2 gate triple L1/L2/L3 + L1D at D*, under
#                <run_root>/GATE.
#
# FREEZE-PIN (rule 2): before ANY compute, the prereg, comparator, generator AND
# every case input must hash disk==HEAD, and the comparator --selftest must be green
# under python3 and python3 -O. The RUNNING-TOTAL cap is 4000 core-min across ALL
# solves; an overrun STOPS the run (rc124) and gets no new budget; endTime is never
# shrunk to fit (rule 12). AGE GUARD on every solve dir (rule 4).
# =============================================================================
set -u
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CASE_DIR="$SCRIPT_DIR/case"
GEN="$SCRIPT_DIR/gen_domain_mesh.py"
GRADER="$SCRIPT_DIR/grade_vmfl063_r3.py"
PREREG="$SCRIPT_DIR/PREREGISTRATION.md"

ENDTIME=100000           # GENEROUS iteration ceiling (PREREGISTRATION sec.4.4/sec.6,
                         # supervisor amendment 2026-09-09): residualControl stops a
                         # converging solve far earlier (R2-L3 converged at 10637); this
                         # is raised so a converging D1/D2 is NEVER clock-truncated and
                         # the RUNNING-TOTAL COST CAP (CAP_CORE_MIN, rc124) is the binding
                         # budget limit, not endTime. A level that reaches this ceiling
                         # WITHOUT meeting residualControl (last_time==endTime), or shows a
                         # sustained limit cycle, is NOT A RESULT -- genuine non-convergence
                         # / de-confined-domain unsteadiness, NEVER a widened band or a
                         # loosened floor.
RANKS=1                  # serial (PREREGISTRATION sec.7)
CAP_CORE_MIN=4000        # RUNNING TOTAL across ALL solves (PREREGISTRATION sec.7;
                         # supervisor cap-setting 2026-09-09, raised 1400->4000 so the cap
                         # does NOT rc124-stop mid-ladder before the gate triple -- that
                         # would be a wasteful budget-NAR. ~$3.42 derived at cap, << $25.)

RUN_ROOT="${1:?usage: run_vmfl063_r3.sh <run_root>}"
REPO="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || { echo "ABORT: not inside a git repository"; exit 2; }

# --- FREEZE-PIN: disk == HEAD for the grading path AND every case input ---------
pin () {  # <relpath-from-repo>
  local rel="$1"
  local disk head
  disk="$(git -C "$REPO" hash-object "$REPO/$rel" 2>/dev/null)"
  head="$(git -C "$REPO" rev-parse "HEAD:$rel" 2>/dev/null)"
  echo "$head" | grep -qE '^[0-9a-f]{40}$' || head=""
  if [ -z "$disk" ] || [ "$disk" != "$head" ]; then
    echo "ABORT freeze-pin: $rel disk=${disk:-?} head=${head:-?} -- NOT frozen (rule 2)"; exit 2
  fi
  echo "  freeze-pin OK: $rel"
}
REL_BASE="cases/ansys_verification/VMFL063-R3"
pin "$REL_BASE/PREREGISTRATION.md"
pin "$REL_BASE/grade_vmfl063_r3.py"
pin "$REL_BASE/gen_domain_mesh.py"
for f in 0/U 0/p 0.confined/U 0.confined/p constant/momentumTransport constant/transportProperties \
         constant/turbulenceProperties system/fvSchemes system/fvSolution system/controlDict.template; do
  pin "$REL_BASE/case/$f"
done

mkdir -p "$RUN_ROOT" || { echo "ABORT: mkdir $RUN_ROOT"; exit 2; }

# --- comparator selftest green under BOTH interpreters, and --verify-frozen -----
for PY in "python3" "python3 -O"; do
  rm -rf "$SCRIPT_DIR/__pycache__"
  $PY "$GRADER" --selftest > "$RUN_ROOT/selftest_$(echo $PY|tr ' -' '__').log" 2>&1 || {
    echo "ABORT: comparator --selftest not green under '$PY'"; exit 2; }
done
"$GRADER" --verify-frozen || { echo "ABORT: --verify-frozen mismatch"; exit 2; }

LR="$RUN_ROOT/LAUNCH_RECORD.txt"
PREREG_BLOB="$(git -C "$REPO" hash-object "$PREREG")"
GRADER_BLOB="$(git -C "$REPO" hash-object "$GRADER")"
GEN_BLOB="$(git -C "$REPO" hash-object "$GEN")"
{ echo "VMFL063-R3 launch $(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo "cap_core_min=$CAP_CORE_MIN (running total)";
  echo "prereg_blob=$PREREG_BLOB comparator_blob=$GRADER_BLOB generator_blob=$GEN_BLOB"; } > "$LR"

# PRE-FIRST-COMPUTE AMENDMENT (supervisor 2026-09-09): the OpenFOAM v2606 bashrc
# references WM_PROJECT_DIR before setting it, which aborts under `set -u` (the first
# re-launch died here, launcher_rc=1, BEFORE any compute). Disable nounset ONLY for the
# source (the proven R8 driver runs with no set -u at all for the same reason), then
# restore it. No gate/threshold/band/cap/label/comparator touched.
set +u
source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo "ABORT: cannot source OpenFOAM v2606"; exit 2; }
set -u
command -v simpleFoam >/dev/null || { echo "ABORT: simpleFoam not on PATH"; exit 2; }
command -v blockMesh  >/dev/null || { echo "ABORT: blockMesh not on PATH"; exit 2; }
SOLVER_BIN="$(command -v simpleFoam)"
TOTAL_CORE_MIN=0

# --- one solve: <out_dir> <rc_root> <case_id> <domain> <level> <zerodir> <confined?>
solve_case () {
  local OUT="$1" RCROOT="$2" ID="$3" DOMAIN="$4" LEVEL="$5" ZERO="$6" CONFINED="$7"

  # AGE GUARD (rule 4): never launch into a tree already holding an answer.
  if [ -d "$OUT/0" ]; then echo "ABORT age guard: $OUT already holds 0/"; exit 2; fi
  local EXISTING_T
  EXISTING_T="$(find "$OUT" -mindepth 1 -maxdepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?([eE][-+][0-9]+)?$' 2>/dev/null | head -1)"
  [ -z "$EXISTING_T" ] || { echo "ABORT age guard: $OUT already holds a numeric time dir ($EXISTING_T)"; exit 2; }

  # RUNNING-TOTAL cap drawdown, in the executable path.
  local REMAIN TIMEOUT_S
  REMAIN="$(python3 -c "print(max(0.0, $CAP_CORE_MIN - $TOTAL_CORE_MIN))")"
  TIMEOUT_S="$(python3 -c "print(int($REMAIN * 60 / $RANKS))")"
  [ "$TIMEOUT_S" -gt 0 ] || { echo "ABORT: BUDGET EXHAUSTED before $ID (spent $TOTAL_CORE_MIN of $CAP_CORE_MIN). rule 12."; exit 2; }
  echo "--- $ID ($DOMAIN $LEVEL${CONFINED:+ CONFINED})  remaining ${REMAIN}/${CAP_CORE_MIN} core-min  timeout ${TIMEOUT_S}s"

  mkdir -p "$OUT" || { echo "ABORT: mkdir $OUT"; exit 2; }
  cp -r "$CASE_DIR"/constant "$OUT"/ || { echo "ABORT: copy constant"; exit 2; }
  mkdir -p "$OUT/system" "$OUT/0"
  cp "$CASE_DIR"/system/fvSchemes "$CASE_DIR"/system/fvSolution "$OUT/system"/ || { echo "ABORT: copy fv*"; exit 2; }
  cp "$CASE_DIR/$ZERO"/U "$CASE_DIR/$ZERO"/p "$OUT/0"/ || { echo "ABORT: copy 0 from $ZERO"; exit 2; }

  # mesh: the frozen generator is the SOLE authority (PREREGISTRATION sec.4.2)
  python3 "$GEN" "$DOMAIN" "$LEVEL" > "$OUT/system/blockMeshDict" || { echo "ABORT: gen_domain_mesh $DOMAIN $LEVEL"; exit 2; }
  if [ -n "$CONFINED" ]; then
    # BC-isolation twin: the far-field top reverts to the OLD confining symmetryPlane.
    sed -i 's/farfield { type patch;/farfield { type symmetryPlane;/' "$OUT/system/blockMeshDict"
    grep -q 'farfield { type symmetryPlane;' "$OUT/system/blockMeshDict" || { echo "ABORT: confined farfield sed did not take"; exit 2; }
  fi
  sed -e "s/__ENDTIME__/$ENDTIME/g" "$CASE_DIR"/system/controlDict.template > "$OUT/system/controlDict" || { echo "ABORT: sed controlDict"; exit 2; }
  grep -qE "^endTime[[:space:]]+$ENDTIME;" "$OUT/system/controlDict" || { echo "ABORT: controlDict endTime != $ENDTIME"; exit 2; }

  ( cd "$OUT" && blockMesh > log.blockMesh 2>&1 ) || { echo "ABORT: blockMesh failed at $ID -- a crash is a FINDING, not a retry"; exit 2; }
  ( cd "$OUT" && checkMesh > log.checkMesh 2>&1 )
  python3 - "$OUT" "$ID" "$REPO" <<'PYBC' || { echo "ABORT: mesh birth certificate"; exit 2; }
import json, re, sys, os, subprocess, datetime
out, cid, repo = sys.argv[1], sys.argv[2], sys.argv[3]
t = open(os.path.join(out,'log.checkMesh'), errors='replace').read()
def g(p, c=float):
    m = re.search(p, t); return c(m.group(1)) if m else None
bc = {'case_id': cid, 'cells': g(r'cells:\s+(\d+)', int), 'points': g(r'points:\s+(\d+)', int),
      'max_aspect_ratio': g(r'Max aspect ratio = ([0-9.eE+-]+)'),
      'max_non_orthogonality': g(r'non-orthogonality Max: ([0-9.eE+-]+)'),
      'mesh_ok': 'Mesh OK' in t, 'failed_checks': g(r'Failed (\d+) mesh checks', int) or 0,
      'blockMeshDict_sha': subprocess.run(['git','hash-object',os.path.join(out,'system','blockMeshDict')],capture_output=True,text=True).stdout.strip(),
      'minted_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
json.dump(bc, open(os.path.join(out,'birth_certificate.json'),'w'), indent=2, sort_keys=True)
print('  birth cert %s: cells=%s meshOK=%s AR=%s nonOrtho=%s' % (cid, bc['cells'], bc['mesh_ok'], bc['max_aspect_ratio'], bc['max_non_orthogonality']))
PYBC

  # 0/ touched LAST -> the age-guard datum (rule 4)
  touch "$OUT"/0/* || { echo "ABORT: touch $OUT/0"; exit 2; }

  local T0 SRC RC WAIT_RC T1 WALL CORE_MIN
  T0="$(date +%s)"
  rm -f "$OUT/.solver_rc"
  ( cd "$OUT" || exit 90
    setsid timeout "${TIMEOUT_S}"s simpleFoam > log.simpleFoam 2>&1
    SRC=$?; echo "$SRC" > .solver_rc; exit "$SRC" ) &
  local SPID=$!
  wait "$SPID"; WAIT_RC=$?
  if [ -f "$OUT/.solver_rc" ]; then RC="$(cat "$OUT/.solver_rc")"; else RC="$WAIT_RC"; fi
  T1="$(date +%s)"; WALL=$((T1-T0))
  CORE_MIN="$(python3 -c "print(round($WALL*$RANKS/60.0,4))")"
  TOTAL_CORE_MIN="$(python3 -c "print(round($TOTAL_CORE_MIN + $CORE_MIN,4))")"
  if [ "$RC" -eq 0 ]; then
    ( cd "$OUT" && postProcess -func writeCellCentres -latestTime > log.writeCellCentres 2>&1 ) \
      || echo "  WARN: writeCellCentres failed at $ID (grader will REFUSE on missing Cx/Cy)"
  fi
  local LAST_TIME ENDED CONV
  LAST_TIME="$(grep -E '^Time = ' "$OUT/log.simpleFoam" 2>/dev/null | tail -1 | sed -E 's/^Time = //')"
  ENDED="$(grep -cE '^End$' "$OUT/log.simpleFoam" 2>/dev/null)"
  CONV="$(grep -c 'SIMPLE solution converged' "$OUT/log.simpleFoam" 2>/dev/null)"
  printf 'rc = %s\ncase_id = %s\ndomain = %s\nlevel = %s\nconfined = %s\nstate = FINISHED\nwait_rc = %s\nwall_s = %s\nranks = %s\ncore_min = %s\ntotal_core_min_so_far = %s\ntimeout_s = %s\ncap_core_min = %s\nendTime = %s\nlast_time_in_log = %s\nEnd_lines = %s\nSIMPLE_converged_lines = %s\nprereg_blob = %s\ncomparator_blob = %s\ngenerator_blob = %s\nsolver_bin = %s\nutc = %s\nnote = rc CAPTURED INSIDE the detached subshell; 124 == the RUNNING-TOTAL cap fired (rule 12); endTime is never shrunk to fit. L-342: absent -> comparator reports rc NOT MEASURED.\n' \
    "$RC" "$ID" "$DOMAIN" "$LEVEL" "${CONFINED:-no}" "$WAIT_RC" "$WALL" "$RANKS" "$CORE_MIN" "$TOTAL_CORE_MIN" "$TIMEOUT_S" "$CAP_CORE_MIN" "$ENDTIME" "${LAST_TIME:-none}" "${ENDED:-0}" "${CONV:-0}" "$PREREG_BLOB" "$GRADER_BLOB" "$GEN_BLOB" "$SOLVER_BIN" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    > "$RCROOT/RUN_RC.$ID" || { echo "ABORT: cannot write RUN_RC.$ID"; exit 2; }
  { echo "$ID ($DOMAIN $LEVEL): rc=$RC wall_s=$WALL core_min=$CORE_MIN total=$TOTAL_CORE_MIN last_time=${LAST_TIME:-none} End=${ENDED:-0} conv=${CONV:-0}"; } >> "$LR"
  if [ "$RC" -ne 0 ]; then
    echo "STOP $ID: rc=$RC (124 == cap; an overrun gets no new budget and endTime is not shrunk, rule 12). A crash is a FINDING."
    echo "later solves NOT launched (stopped at $ID)" >> "$LR"
    exit "$RC"
  fi
}

# --- STAGE 1: the domain ladder (fixed R2-L3 grid) + the BC-isolation twin -------
solve_case "$RUN_ROOT/D0"          "$RUN_ROOT" "D0"          "D0" "L3" "0"          ""
solve_case "$RUN_ROOT/D1"          "$RUN_ROOT" "D1"          "D1" "L3" "0"          ""
solve_case "$RUN_ROOT/D2"          "$RUN_ROOT" "D2"          "D2" "L3" "0"          ""
solve_case "$RUN_ROOT/D0_CONFINED" "$RUN_ROOT" "D0_CONFINED" "D0" "L3" "0.confined" "yes"

# --- STAGE 2: pick D* by the FROZEN self-convergence rule (never the Target) -----
DSTAR_LINE="$("$GRADER" --pick-dstar --run-root "$RUN_ROOT" | tee -a "$LR" | grep '^D_STAR=')"
DSTAR="${DSTAR_LINE#D_STAR=}"
echo "D* = $DSTAR"
if [ "$DSTAR" = "NOT_CONVERGED" ]; then
  echo "DOMAIN NOT_CONVERGED within the frozen ladder -- the gate is NOT built."
  echo "Grade with: $GRADER --run-root $RUN_ROOT --out $RUN_ROOT/GRADING_VMFL063_R3.json"
  echo "(grader emits ROW NOT A RESULT; PREREGISTRATION outcome 5: a bigger-ladder successor is owed)"
  exit 0
fi
case "$DSTAR" in D0|D1|D2) : ;; *) echo "ABORT: unexpected D* = '$DSTAR'"; exit 2 ;; esac

# --- STAGE 3: the BYTE-IDENTICAL R2 gate triple + L1D, built at D* ----------------
GATE="$RUN_ROOT/GATE"; mkdir -p "$GATE"
solve_case "$GATE/L1"  "$GATE" "L1"  "$DSTAR" "L1" "0" ""
solve_case "$GATE/L2"  "$GATE" "L2"  "$DSTAR" "L2" "0" ""
solve_case "$GATE/L3"  "$GATE" "L3"  "$DSTAR" "L3" "0" ""
solve_case "$GATE/L1D" "$GATE" "L1D" "$DSTAR" "L1" "0" ""

echo "ALL SOLVES DONE. total_core_min=$TOTAL_CORE_MIN of cap $CAP_CORE_MIN. D* = $DSTAR"
echo "Grade with: $GRADER --run-root $RUN_ROOT --out $RUN_ROOT/GRADING_VMFL063_R3.json"
