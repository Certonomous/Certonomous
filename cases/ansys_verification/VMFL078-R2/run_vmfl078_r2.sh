#!/usr/bin/env bash
# =============================================================================
# VMFL078-R2 graded-run driver -- 3-D lid-driven CUBIC cavity, Re = 1000,
# THE FULL CUBE (no symmetry plane).  Ansys Fluid Dynamics Verification Manual,
# Release 2026 R1, printed pp.223-224 (PDF pp.237-238).
# Solver: simpleFoam (OpenFOAM v2606), steady laminar SIMPLEC, 4 MPI ranks.
#
# Frozen pre-registration: cases/ansys_verification/VMFL078-R2/VMFL078_R2_PREREGISTRATION.md
# Frozen comparator      : cases/ansys_verification/VMFL078-R2/grade_vmfl078_r2.py
# Run root               : verification/runs/ansys_verification/VMFL078-R2/
#
# Modelled on cases/ansys_verification/VMFL078/run_vmfl078.sh, which is NOT edited
# (it may still be executing and it is the driver of a graded case).  Departures:
#   (a) ONE mesh parameter __N__, not three: the family is 32^3 / 64^3 / 128^3, a
#       cube of cubic cells at every level.
#   (b) THREE gate readers per level (mid-span z=0.50, quarter-span z=0.25 and its
#       mirror z=0.75), each carrying the SAME 201 frozen abscissae.
#   (c) The BC guard is inverted: VMFL078 refused a WALL where a symmetry plane was
#       registered; R2 refuses a SYMMETRY PATCH anywhere, because removing it IS the
#       experiment.
#
# NO CAP AND NO `timeout` -- Sanaa's directive #17 (2026-09-12, her fourth ruling):
# no run on any team is stopped by a time or budget cap.  Core-minutes are still
# MEASURED per level and written to RUN_RC/COST.txt: rule 12's estimate-versus-actual
# calibration duty is untouched by the removal of the cap.  The only ceiling is
# `endTime`, an ITERATION ceiling: a level that reaches it without printing the
# converged line is NOT A RESULT under rule 5 limb 1, and the comparator refuses it.
#
# NO `set -u`.  Incompatible with OpenFOAM v2606 (sourcing etc/bashrc dereferences
# WM_PROJECT_DIR before assigning it).  Every check gates EXPLICITLY.
# =============================================================================

RANKS=4
ENDTIME=40000            # ITERATION ceiling, not a budget gate

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CASE_DIR="$SCRIPT_DIR/case"
RUN_ROOT="${1:?usage: run_vmfl078_r2.sh <run_root> [levels...]}"
shift 2>/dev/null
LEVELS_TO_RUN="${*:-F1 F2 F3}"

declare -A NN=( [F1]=32 [F2]=64 [F3]=128 )

echo "=== VMFL078-R2 launcher  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)  run_root=$RUN_ROOT"

# --- 1. LAUNCH-TIME FREEZE CHECK (rule 2) ------------------------------------
REPO="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || { echo "ABORT: not inside a git repository"; exit 2; }
PREREG_REL="cases/ansys_verification/VMFL078-R2/VMFL078_R2_PREREGISTRATION.md"
GRADER_REL="cases/ansys_verification/VMFL078-R2/grade_vmfl078_r2.py"
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

# The band table is INHERITED from VMFL078 and must be byte-identical to the blob the
# limb-B freeze 98ba5a53 committed -- that is what makes R2's limb B like-for-like.
BAND_REL="cases/ansys_verification/VMFL078/figure_78_2/limbB_band_table.json"
BAND_FROZEN="0fbe690025b11d23ca53106cf69385e2961b3e51"
BAND_DISK="$(git -C "$REPO" hash-object "$REPO/$BAND_REL")" || { echo "ABORT: cannot hash the band table"; exit 2; }
[ "$BAND_DISK" = "$BAND_FROZEN" ] || { echo "ABORT: the inherited band table hashes $BAND_DISK, the limb-B freeze committed $BAND_FROZEN. R2 reuses the band UNCHANGED or it is not like-for-like."; exit 2; }
echo "  band table OK (inherited unchanged from the limb-B freeze 98ba5a53): $BAND_DISK"

# --- CASE INPUTS: every one hashed against its OWN HEAD blob ------------------
NINP=0
for F in 0/U 0/p constant/transportProperties constant/momentumTransport \
         constant/turbulenceProperties system/blockMeshDict.template \
         system/controlDict.template system/fvSchemes system/fvSolution; do
  A="$(git -C "$REPO" rev-parse "HEAD:cases/ansys_verification/VMFL078-R2/case/$F" 2>/dev/null)" || { echo "ABORT: case/$F is not committed at HEAD"; exit 2; }
  B="$(git -C "$REPO" hash-object "$CASE_DIR/$F")" || { echo "ABORT: cannot hash case/$F"; exit 2; }
  [ "$A" = "$B" ] || { echo "ABORT: case/$F on disk ($B) != HEAD blob ($A)"; exit 2; }
  NINP=$((NINP+1))
done
echo "  case inputs OK: $NINP files, each byte-identical to its HEAD blob"

# The numerics must be BYTE-IDENTICAL to VMFL078's, or R2 changes two things at once
# and the experiment is confounded.
for F in system/fvSchemes system/fvSolution constant/transportProperties constant/momentumTransport; do
  A="$(git -C "$REPO" rev-parse "HEAD:cases/ansys_verification/VMFL078/case/$F")" || { echo "ABORT: cannot resolve VMFL078 HEAD blob of $F"; exit 2; }
  B="$(git -C "$REPO" hash-object "$CASE_DIR/$F")"
  [ "$A" = "$B" ] || { echo "ABORT: $F differs from VMFL078's ($B vs $A). R2 changes the GEOMETRY ONLY; a second change confounds the experiment."; exit 2; }
done
echo "  numerics OK: fvSchemes, fvSolution and both property dicts are byte-identical to VMFL078's"

# --- 2. CONTROLS (rule 3): --selftest under BOTH interpreters -----------------
# `python3 -O` deletes every assert, so a control that exists only under one flag is
# not a control (L-332).  Both runs must agree on PASS count, FAIL count and rc.
ST="/tmp/vmfl078r2_selftest.$$"
rm -rf "$SCRIPT_DIR/__pycache__"
python3    "$SCRIPT_DIR/grade_vmfl078_r2.py" --selftest --repo "$REPO" > "$ST"   2>&1; RC_PLAIN=$?
[ "$RC_PLAIN" = "0" ] || { echo "ABORT: comparator --selftest is NOT green under python3 (rc $RC_PLAIN); see $ST"; exit 2; }
rm -rf "$SCRIPT_DIR/__pycache__"
python3 -O "$SCRIPT_DIR/grade_vmfl078_r2.py" --selftest --repo "$REPO" > "$ST.O" 2>&1; RC_O=$?
[ "$RC_O" = "0" ] || { echo "ABORT: comparator --selftest is NOT green under python3 -O (rc $RC_O); see $ST.O"; exit 2; }
NP_PLAIN="$(grep -c '^  \[PASS\]' "$ST")";   NP_O="$(grep -c '^  \[PASS\]' "$ST.O")"
NF_PLAIN="$(grep -c '^  \[FAIL\]' "$ST")";   NF_O="$(grep -c '^  \[FAIL\]' "$ST.O")"
[ "$NP_PLAIN" = "$NP_O" ] || { echo "ABORT: --selftest PASS COUNT differs -- python3 $NP_PLAIN vs -O $NP_O (L-332)"; exit 2; }
[ "$NF_PLAIN" = "$NF_O" ] || { echo "ABORT: --selftest FAIL COUNT differs (L-332)"; exit 2; }
[ "$RC_PLAIN" = "$RC_O" ] || { echo "ABORT: --selftest EXIT RC differs (L-332)"; exit 2; }
for MARK in \
  'AST guard: ast.Assert count is 0 in this file' \
  'one_match REFUSES on two matches' \
  'time dirs sort NUMERICALLY' \
  'planted zero P1a: the gate reader SEES' \
  'planted zero P1b: the plant MOVES the GATE FUNCTIONAL' \
  'planted zero REFUSES against a BLIND reader' \
  'the band literals ARE the committed band table' \
  'B2 threshold is 16, not a count of what was measured' \
  'BC provenance REFUSES a mesh that still carries a SYMMETRY patch' \
  'check_controldict REFUSES a controlDict with the cellPoint fix DELETED' \
  'AGE GUARD catches an answer OLDER than the case' \
  'rule 5 is ONE-WAY: a failing limb D demotes a PASSING limb B' \
  'the FOUR outcomes are the four written in the registration, no fifth' \
  'END-TO-END grade() runs and writes a JSON verdict' ; do
  grep -qF "$MARK" "$ST" || { echo "ABORT: --selftest did not DRIVE the control: $MARK"; exit 2; }
  grep -qF "$MARK" "$ST.O" || { echo "ABORT: control vanishes under -O: $MARK (L-332)"; exit 2; }
done
grep -q '^SELFTEST: all checks passed' "$ST" || { echo "ABORT: --selftest printed no all-checks-passed line"; exit 2; }
grep -q '^  \[FAIL\]' "$ST" && { echo "ABORT: --selftest printed a FAIL line"; exit 2; }
echo "  controls OK: --selftest $NP_PLAIN PASS under python3 and $NP_O under -O, 0 FAIL, rc $RC_PLAIN/$RC_O"
rm -f "$ST" "$ST.O"

# --- run root, contention record, launch record ------------------------------
mkdir -p "$RUN_ROOT" || { echo "ABORT: cannot create $RUN_ROOT"; exit 2; }
{ echo "sampled_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "uptime = $(uptime)"
  echo "nproc = $(nproc)"
  echo "loadavg = $(cut -d' ' -f1-3 /proc/loadavg)"
  echo "mem_available_MB = $(free -m | awk 'NR==2{print $7}')"
  echo "-- other solver processes on the box at launch --"
  ps -eo comm= | grep -E 'Foam|foam|python3|docker' | sort | uniq -c | sort -rn | head -12
  echo "note = contention at launch. core-minutes are wall_s*RANKS/60 and a busy box inflates wall_s (COMPUTE_BUDGET_CHARTER sec.6: waste is reported, never absorbed). The pre-registered cost is anchored on VMFL078's MEASURED L3, which itself ran at loadavg ~48 on 16 cores, so the estimate already carries a contention factor of about 2."
} > "$RUN_ROOT/CONTENTION.txt" 2>&1

LR="$RUN_ROOT/LAUNCH_RECORD.txt"
{ echo "case = VMFL078-R2"
  echo "manual_pages = printed 223-224 (PDF 237-238)"
  echo "supersedes = NOTHING. VMFL078 stands as graded (limb A GATE REACHED, limb B GATE FAIL) and its gates are CLOSED. R2 is a SUCCESSOR that tests a named hypothesis about that GATE FAIL."
  echo "launched_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "freeze_commit_head = $FREEZE_COMMIT"
  echo "prereg = $PREREG_REL"
  echo "prereg_blob = $PREREG_BLOB"
  echo "comparator = $GRADER_REL"
  echo "comparator_blob = $GRADER_BLOB"
  echo "band_table_inherited = $BAND_REL blob $BAND_DISK (unchanged from limb-B freeze 98ba5a532e30ecee4e6da3a61be8a7dcf2e4a8dc)"
  echo "launcher_blob_on_disk = $(git -C "$REPO" hash-object "$0")"
  echo "levels = $LEVELS_TO_RUN  (F1 32^3, F2 64^3, F3 128^3; r = 2)"
  echo "ranks = $RANKS (CONSTANT across levels: only the mesh changes between levels)"
  echo "endTime = $ENDTIME  (ITERATION ceiling; residualControl stops earlier)"
  echo "cap = NONE. Sanaa directive #17, 2026-09-12: no run on any team is stopped by a time or budget cap. Cost is MEASURED and recorded; nothing here kills a solve for spending."
} > "$LR" || { echo "ABORT: cannot write LAUNCH_RECORD.txt"; exit 2; }

# --- OpenFOAM ----------------------------------------------------------------
source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo "ABORT: cannot source the v2606 bashrc"; exit 2; }
for B in simpleFoam blockMesh checkMesh decomposePar reconstructPar mpirun; do
  command -v "$B" >/dev/null || { echo "ABORT: $B not on PATH after sourcing the v2606 bashrc"; exit 2; }
done
SOLVER_BIN="$(command -v simpleFoam)"
echo "solver_bin = $SOLVER_BIN" >> "$LR"
echo "  simpleFoam = $SOLVER_BIN, $RANKS ranks"

TOTAL_CORE_MIN=0
OVERALL_RC=0

for L in $LEVELS_TO_RUN; do
  OUT="$RUN_ROOT/$L"
  [ -n "${NN[$L]}" ] || { echo "ABORT: no registered mesh count for level $L"; exit 2; }

  # AGE GUARD (rule 4): refuse a level dir that already holds 0/ or a numeric time dir.
  if [ -d "$OUT/0" ]; then echo "ABORT age guard: $OUT already holds 0/"; exit 2; fi
  EXISTING_T="$(find "$OUT" -mindepth 1 -maxdepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?([eE][-+][0-9]+)?$' 2>/dev/null | head -1)"
  [ -z "$EXISTING_T" ] || { echo "ABORT age guard: $OUT already holds a numeric time directory ($EXISTING_T)"; exit 2; }

  NCELL=$(( NN[$L] * NN[$L] * NN[$L] ))
  echo "--- $L  ${NN[$L]}^3 = $NCELL cells  ranks $RANKS  endTime $ENDTIME  (NO CAP)"
  mkdir -p "$OUT" || { echo "ABORT: mkdir $OUT"; exit 2; }
  cp -r "$CASE_DIR"/0 "$CASE_DIR"/constant "$CASE_DIR"/system "$OUT"/ || { echo "ABORT: cannot copy the case templates into $OUT"; exit 2; }

  sed -e "s/__N__/${NN[$L]}/g" "$OUT/system/blockMeshDict.template" > "$OUT/system/blockMeshDict" || { echo "ABORT: sed blockMeshDict for $L"; exit 2; }
  grep -q '__N__' "$OUT/system/blockMeshDict" && { echo "ABORT: blockMeshDict substitution did not take at $L"; exit 2; }
  sed -e "s/__ENDTIME__/$ENDTIME/g" "$OUT/system/controlDict.template" > "$OUT/system/controlDict" || { echo "ABORT: sed controlDict for $L"; exit 2; }
  grep -qE "^endTime[[:space:]]+$ENDTIME;" "$OUT/system/controlDict" || { echo "ABORT: controlDict endTime is not the registered $ENDTIME at $L"; exit 2; }
  # Each of the THREE gate readers must carry the cellPoint fix and exactly 201 abscissae.
  for P in midspanProbe quarterProbe quarter75Probe; do
    BLK="$(awk -v P="    $P" '$0==P{f=1} f&&/^    [a-zA-Z]/&&$0!=P{f=0} f' "$OUT/system/controlDict")"
    echo "$BLK" | grep -qF 'interpolationScheme cellPoint' || { echo "ABORT: the cellPoint order-pollution fix is MISSING from $P at $L"; exit 2; }
    NLOC="$(echo "$BLK" | grep -cE '^            \(0\.5 ')"
    [ "$NLOC" = "201" ] || { echo "ABORT: $P at $L carries $NLOC probe locations, registered 201"; exit 2; }
  done
  # R2's defining guard: no symmetry patch anywhere in the case that would run.
  # AMENDED 2026-09-12, BEFORE FIRST COMPUTE (see VMFL078_R2_PREREGISTRATION.md, dated
  # amendment at the foot).  The prior form grepped the RAW files, so it matched the
  # word "symmetry" inside the EXPLANATORY COMMENTS of blockMeshDict and 0/U -- which
  # exist precisely because removing the symmetry plane is the experiment -- and aborted
  # a correct case.  The guard measured something other than what it claimed to measure.
  # It now strips // comments first, so it tests PATCH DECLARATIONS and nothing else.
  # The registered refusal condition is UNCHANGED: no symmetry patch, anywhere.
  for F in "$OUT/system/blockMeshDict" "$OUT/0/U"; do
    sed -E 's://.*::' "$F" | grep -qi 'symmetry' && { echo "ABORT: a symmetry patch survives in $F at $L -- removing it IS the experiment"; exit 2; }
  done
  # and prove the guard still has teeth: it MUST fire on a declaration it should catch.
  printf '    zzz { type symmetryPlane; }\n' > "$OUT/system/.guard_probe"
  sed -E 's://.*::' "$OUT/system/.guard_probe" | grep -qi 'symmetry' || { echo "ABORT: the symmetry guard is DEAD -- it did not fire on a planted symmetryPlane declaration"; exit 2; }
  rm -f "$OUT/system/.guard_probe"

  printf 'FoamFile { version 2.0; format ascii; class dictionary; object decomposeParDict; }\nnumberOfSubdomains %d;\nmethod          scotch;\n' "$RANKS" \
    > "$OUT/system/decomposeParDict" || { echo "ABORT: cannot write decomposeParDict at $L"; exit 2; }

  ( cd "$OUT" && blockMesh > log.blockMesh 2>&1 ) || { echo "ABORT: blockMesh failed at $L -- a crash is a FINDING, not a retry"; exit 2; }
  ( cd "$OUT" && checkMesh > log.checkMesh 2>&1 )

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
print('  birth certificate: cells=%s meshOK=%s maxSkew=%s maxAR=%s maxNonOrtho=%s' % (bc['cells'], bc['mesh_ok'], bc['max_skewness'], bc['max_aspect_ratio'], bc['max_non_orthogonality']))
if not bc['mesh_ok'] or bc['failed_checks']:
    raise SystemExit('  ABORT: checkMesh is not clean at this level')
PYBC

  ( cd "$OUT" && decomposePar > log.decomposePar 2>&1 ) || { echo "ABORT: decomposePar failed at $L"; exit 2; }

  printf 'level=%s\nstate=STARTED\nranks=%d\nendTime=%s\ncap=NONE (Sanaa directive #17, 2026-09-12)\nprereg_blob=%s\ncomparator_blob=%s\nstarted_utc=%s\n' \
    "$L" "$RANKS" "$ENDTIME" "$PREREG_BLOB" "$GRADER_BLOB" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$RUN_ROOT/RUN_RC.$L" \
    || { echo "ABORT: cannot write RUN_RC.$L"; exit 2; }

  # 0/ is touched LAST, immediately before the solver: it is the age-guard datum.
  touch "$OUT"/0/* || { echo "ABORT: cannot touch $OUT/0"; exit 2; }

  T0="$(date +%s)"
  # DETACHED SOLVER.  THE rc IS CAPTURED INSIDE the subshell, immediately after the
  # command returns -- `setsid cmd` returns 0 for every outcome when its rc is taken
  # OUTSIDE the wrapper (L-336, setsid-parent-returns-zero).
  rm -f "$OUT/.solver_rc"
  (
    cd "$OUT" || exit 90
    setsid mpirun -np "$RANKS" simpleFoam -parallel > log.simpleFoam 2>&1
    SRC=$?
    echo "$SRC" > .solver_rc
    exit "$SRC"
  ) &
  SOLVER_PID=$!
  wait "$SOLVER_PID"
  WAIT_RC=$?
  if [ -f "$OUT/.solver_rc" ]; then RC="$(cat "$OUT/.solver_rc")"; else RC="$WAIT_RC"; fi
  T1="$(date +%s)"
  WALL=$((T1-T0))
  CORE_MIN="$(python3 -c "print(round($WALL*$RANKS/60.0, 4))")"
  TOTAL_CORE_MIN="$(python3 -c "print(round($TOTAL_CORE_MIN + $CORE_MIN, 4))")"

  if [ "$RC" -eq 0 ]; then
    ( cd "$OUT" && reconstructPar -latestTime > log.reconstructPar 2>&1 ) || echo "  WARN: reconstructPar failed at $L (the comparator will REFUSE on missing fields)"
  fi

  ENDT_DIR=""; ENDT_OK="no"
  for D in $(find "$OUT" -mindepth 1 -maxdepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?([eE][-+][0-9]+)?$' 2>/dev/null); do
    B="$(basename "$D")"
    if python3 -c "import sys;sys.exit(0 if float(sys.argv[1])>0 else 1)" "$B" 2>/dev/null; then
      if [ -z "$ENDT_DIR" ] || python3 -c "import sys;sys.exit(0 if float(sys.argv[1])>float(sys.argv[2]) else 1)" "$B" "$(basename "$ENDT_DIR")"; then ENDT_DIR="$D"; fi
    fi
  done
  if [ -n "$ENDT_DIR" ] && [ -f "$ENDT_DIR/U" ] && [ "$ENDT_DIR/U" -nt "$OUT/0/U" ]; then ENDT_OK="yes"; fi
  LAST_TIME="$(grep -E '^Time = ' "$OUT/log.simpleFoam" 2>/dev/null | tail -1 | sed -E 's/^Time = //')"
  ENDED="$(grep -cE '^End$' "$OUT/log.simpleFoam" 2>/dev/null)"
  CONVERGED="$(grep -c 'SIMPLE solution converged' "$OUT/log.simpleFoam" 2>/dev/null)"
  CELLS="$(python3 -c "import json;print(json.load(open('$OUT/birth_certificate.json'))['cells'])" 2>/dev/null)"

  printf 'rc = %s\nlevel = %s\nstate = FINISHED\nwait_rc = %d\nwall_s = %d\nranks = %d\ncore_min = %s\ntotal_core_min_so_far = %s\ncap = NONE\nendTime = %s\nlast_time_in_log = %s\nEnd_lines = %s\nSIMPLE_converged_lines = %s\nlatest_time_dir = %s\nfield_at_latest_newer_than_0_U = %s\ncells = %s\nn = %s\ndetach_wrapper_pid = %s\nprereg_blob = %s\ncomparator_blob = %s\nsolver_bin = %s\nutc = %s\nnote = rc is the mpirun/simpleFoam exit status, CAPTURED INSIDE the detached subshell. There is NO timeout and NO cap (Sanaa directive #17, 2026-09-12). core_min is MEASURED for the rule-12 calibration duty, which the removal of the cap does not withdraw. L-342: this file is INFRASTRUCTURE -- absent, the comparator reports rc NOT MEASURED and still grades the physics artefacts.\n' \
    "$RC" "$L" "$WAIT_RC" "$WALL" "$RANKS" "$CORE_MIN" "$TOTAL_CORE_MIN" "$ENDTIME" "${LAST_TIME:-none}" "${ENDED:-0}" "${CONVERGED:-0}" "${ENDT_DIR:-none}" "$ENDT_OK" "${CELLS:-unknown}" "${NN[$L]}" "$SOLVER_PID" "$PREREG_BLOB" "$GRADER_BLOB" "$SOLVER_BIN" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    > "$RUN_ROOT/RUN_RC.$L" || { echo "ABORT: cannot write RUN_RC.$L"; exit 2; }

  echo "level $L : rc=$RC wall_s=$WALL core_min=$CORE_MIN total=$TOTAL_CORE_MIN last_time=${LAST_TIME:-none} End_lines=${ENDED:-0} converged_lines=${CONVERGED:-0} latest_time_dir=${ENDT_DIR:-none} field_newer_than_0_U=$ENDT_OK" >> "$LR"

  if [ "$RC" -ne 0 ]; then
    OVERALL_RC="$RC"
    echo "STOP $L: rc=$RC after ${WALL}s = ${CORE_MIN} core-min (running total ${TOTAL_CORE_MIN})."
    echo "  A non-zero rc is a FINDING, not a retry.  This is NOT a cap: there is no cap on this case."
    echo "later levels are NOT launched" >> "$LR"
    break
  fi
  echo "done $L: ${WALL}s = ${CORE_MIN} core-min (running total ${TOTAL_CORE_MIN}), latest time dir ${ENDT_DIR:-none}"
done

printf 'total_core_min = %s\nranks = %d\noverall_rc = %s\ncap = NONE (Sanaa directive #17, 2026-09-12: no run on any team is stopped by a time or budget cap)\npredicted_core_min = 1900 (VMFL078_R2_PREREGISTRATION.md sec.6)\ncost_basis = core-minutes = wall_s*RANKS/60, MEASURED from this run. Dollars are DERIVED at the owner-stated c7a.4xlarge rate $0.0513/core-h (Sanaa 2026-08-21/22) and are REPORTED-BY-OWNER, NOT MEASURED -- the box cannot read its own billing (COMPUTE_BUDGET_CHARTER sec.5). The estimate-versus-actual comparison lands in docs/COST_CALIBRATION.md at completion (rule 12); removing the cap does not remove the calibration.\n' \
  "$TOTAL_CORE_MIN" "$RANKS" "$OVERALL_RC" > "$RUN_ROOT/COST.txt" || { echo "ABORT: cannot write COST.txt"; exit 2; }
echo "total_core_min = $TOTAL_CORE_MIN" >> "$LR"
echo "finished_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LR"
echo "=== VMFL078-R2 launcher done, overall rc=$OVERALL_RC, total ${TOTAL_CORE_MIN} core-min (no cap)"
exit "$OVERALL_RC"
