#!/usr/bin/env bash
# =============================================================================
# VMFL078 graded-run driver -- Polyhedral Mesh Accuracy / 3-D lid-driven CUBIC
# cavity, Re = 1000.  Ansys Fluid Dynamics Verification Manual, Release 2026 R1,
# printed pp.223-224 (PDF pp.237-238).
# Solver: simpleFoam (OpenFOAM v2606), steady laminar SIMPLEC, 4 MPI ranks.
#
# Frozen pre-registration: cases/ansys_verification/VMFL078/PREREGISTRATION.md
# Frozen comparator      : cases/ansys_verification/VMFL078/grade_vmfl078.py
# Run root               : verification/runs/ansys_verification/VMFL078/
#
# Modelled on cases/ansys_verification/VMFL063/run_vmfl063.sh, the team's reference
# driver, with THREE deliberate departures, each named here so none reads as a slip:
#
#   (a) THERE IS NO CAP AND NO `timeout`.  CASE_PROTOCOL_CHARTER v1.0, Sanaa's own
#       closing sentence: "and for all these 3D cases that still need to run, i dont
#       want to see any budget gates ( time or money). Bc i want to shoot them so we
#       at least have hard 3D demos to show and then we can go back to having some
#       restraint".  VMFL078 is squarely in that scope -- a 3-D case still to run.
#       So sec.4's "cap reached: stop, NOT A RESULT" and CLAUDE.md rule 12's "an
#       overrun stops the run" are SUSPENDED HERE, and nothing in this script kills a
#       solve for spending.  Core-minutes are still MEASURED per level and written to
#       RUN_RC/COST.txt, because rule 12's estimate-versus-actual calibration duty is
#       untouched by the exemption (charter provenance block).  The only ceiling is
#       `endTime`, which is an ITERATION ceiling, not a budget gate: a level that
#       reaches it without converging is NOT A RESULT under rule 5 limb 1.
#
#   (b) 4 MPI RANKS, CONSTANT ACROSS ALL THREE LEVELS.  Constant so that between
#       levels ONLY the mesh changes -- the condition the Roache triple rests on.
#       Verified in the stage-2 bug check: decomposePar rc 0, mpirun rc 0, End line
#       present, probes written by the master, reconstructPar yields U p phi.
#
#   (c) EVERY LEVEL IS RECONSTRUCTED.  In parallel the time-directory fields live in
#       processor*/, and the comparator's strict-completion and age-guard checks read
#       the top-level time directory.  reconstructPar -latestTime is therefore part of
#       the run, not a convenience.
#
# ---------------------------------------------------------------------------
# NO `set -u`.  CATEGORICALLY INCOMPATIBLE with OpenFOAM v2606: sourcing etc/bashrc
# dereferences WM_PROJECT_DIR before assigning it (measured rc 127).  `set -e` does
# not gate reliably here either, so EVERY check gates EXPLICITLY with
# `|| { echo ABORT...; exit <n>; }`.
# =============================================================================

RANKS=4
ENDTIME=40000            # ITERATION ceiling, not a budget gate; residualControl stops earlier

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CASE_DIR="$SCRIPT_DIR/case"
RUN_ROOT="${1:?usage: run_vmfl078.sh <run_root> [levels...]}"
shift 2>/dev/null
LEVELS_TO_RUN="${*:-L1 L2 L3}"

# r = 2 family.  1:1:0.5 counts against 1:1:0.5 edge lengths => CUBIC cells at every
# level (stage-2 checkMesh measured max aspect ratio 1.0 at L1).
declare -A NX=( [L1]=32 [L2]=64  [L3]=128 )
declare -A NY=( [L1]=32 [L2]=64  [L3]=128 )
declare -A NZ=( [L1]=16 [L2]=32  [L3]=64  )

echo "=== VMFL078 launcher  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)  run_root=$RUN_ROOT"

# --- smoke mode: scratch ONLY, never the graded run root ----------------------
SMOKE_ENDTIME=200
if [ -n "$VMFL_SMOKE" ]; then
  case "$RUN_ROOT" in
    */scratchpad/*|*/scratchpad) : ;;
    *) echo "ABORT: VMFL_SMOKE refuses run_root '$RUN_ROOT' -- a smoke runs in scratch ONLY, never where a graded run would look for an answer"; exit 2 ;;
  esac
  LEVELS_TO_RUN="L1"
  ENDTIME="$SMOKE_ENDTIME"
  echo "  SMOKE MODE: L1 only, endTime $SMOKE_ENDTIME, IN SCRATCH; grades nothing"
fi

# --- 1. LAUNCH-TIME FREEZE CHECK (CLAUDE.md rule 2) --------------------------
REPO="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || { echo "ABORT: not inside a git repository"; exit 2; }
PREREG_REL="cases/ansys_verification/VMFL078/PREREGISTRATION.md"
GRADER_REL="cases/ansys_verification/VMFL078/grade_vmfl078.py"
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

# --- CASE INPUTS: every one hashed against its OWN HEAD blob ------------------
NINP=0
for F in 0/U 0/p constant/transportProperties constant/momentumTransport \
         constant/turbulenceProperties system/blockMeshDict.template \
         system/controlDict.template system/fvSchemes system/fvSolution; do
  A="$(git -C "$REPO" rev-parse "HEAD:cases/ansys_verification/VMFL078/case/$F" 2>/dev/null)" || { echo "ABORT: case/$F is not committed at HEAD"; exit 2; }
  B="$(git -C "$REPO" hash-object "$CASE_DIR/$F")" || { echo "ABORT: cannot hash case/$F"; exit 2; }
  [ "$A" = "$B" ] || { echo "ABORT: case/$F on disk ($B) != HEAD blob ($A) -- the case that would run is not the case that was frozen"; exit 2; }
  NINP=$((NINP+1))
done
echo "  case inputs OK: $NINP files, each byte-identical to its HEAD blob"

# --- 2. CONTROLS (rule 3): the comparator's own --selftest, BOTH interpreters -
# `python3 -O` deletes every assert, so a control that exists only under one flag is
# not a control (L-332).  The two runs must agree on PASS count, FAIL count and rc,
# and BOTH must carry the AST-guard marker.
ST="/tmp/vmfl078_selftest.$$"
rm -rf "$SCRIPT_DIR/__pycache__"
python3    "$SCRIPT_DIR/grade_vmfl078.py" --selftest > "$ST"   2>&1; RC_PLAIN=$?
[ "$RC_PLAIN" = "0" ] || { echo "ABORT: comparator --selftest is NOT green under python3 (rc $RC_PLAIN); see $ST"; exit 2; }
rm -rf "$SCRIPT_DIR/__pycache__"
python3 -O "$SCRIPT_DIR/grade_vmfl078.py" --selftest > "$ST.O" 2>&1; RC_O=$?
[ "$RC_O" = "0" ] || { echo "ABORT: comparator --selftest is NOT green under python3 -O (rc $RC_O); see $ST.O"; exit 2; }
NP_PLAIN="$(grep -c '^  \[PASS\]' "$ST")";   NP_O="$(grep -c '^  \[PASS\]' "$ST.O")"
NF_PLAIN="$(grep -c '^  \[FAIL\]' "$ST")";   NF_O="$(grep -c '^  \[FAIL\]' "$ST.O")"
AST_MARK='AST guard: ast.Assert count is 0 in this file'
[ "$NP_PLAIN" = "$NP_O" ] || { echo "ABORT: --selftest PASS COUNT differs -- python3 $NP_PLAIN vs -O $NP_O -- a control that vanishes under -O is not a control (L-332)"; exit 2; }
[ "$NF_PLAIN" = "$NF_O" ] || { echo "ABORT: --selftest FAIL COUNT differs -- python3 $NF_PLAIN vs -O $NF_O (L-332)"; exit 2; }
[ "$RC_PLAIN" = "$RC_O" ] || { echo "ABORT: --selftest EXIT RC differs -- python3 $RC_PLAIN vs -O $RC_O (L-332)"; exit 2; }
grep -qF "$AST_MARK" "$ST"   || { echo "ABORT: --selftest did not print the AST GUARD MARKER under python3"; exit 2; }
grep -qF "$AST_MARK" "$ST.O" || { echo "ABORT: --selftest did not print the AST GUARD MARKER under python3 -O (L-332)"; exit 2; }
grep -q '^SELFTEST: all checks passed' "$ST" || { echo "ABORT: --selftest printed no all-checks-passed line"; exit 2; }
grep -q '^  \[FAIL\]' "$ST" && { echo "ABORT: --selftest printed a FAIL line"; exit 2; }
for MARK in \
  'AST guard: ast.Assert count is 0 in this file' \
  'one_match REFUSES on two matches' \
  'time dirs sort NUMERICALLY' \
  'planted zero P1a: the gate reader SEES' \
  'planted zero P1b: the plant MOVES the GATE FUNCTIONAL' \
  'planted zero P1c: a BLIND writer leaves the functional UNMOVED' \
  'planted zero REFUSES against a BLIND reader' \
  'BC provenance REFUSES a WALL where the symmetry plane was registered' \
  'BC provenance REFUSES a mesh/field DISAGREEMENT' \
  'AGE GUARD catches an answer OLDER than the case' \
  'rule 5 is ONE-WAY' \
  'check_abscissae REFUSES a controlDict with the RIGHT 201 abscissae but the cellPoint order-pollution fix DELETED' \
  'ROW verdict can NEVER be PASS' \
  'END-TO-END ROW VERDICT IS `GATE REACHED`, NOT `PASS`' ; do
  grep -qF "$MARK" "$ST" || { echo "ABORT: --selftest did not DRIVE the control: $MARK"; exit 2; }
done
echo "  controls OK: --selftest $NP_PLAIN/$NP_PLAIN PASS; python3 and -O agree on PASS $NP_PLAIN/$NP_O, FAIL $NF_PLAIN/$NF_O, rc $RC_PLAIN/$RC_O; both carry the AST guard marker"
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
  echo "note = contention at launch. core-minutes are wall_s*RANKS/60 and a busy box inflates wall_s (COMPUTE_BUDGET_CHARTER sec.6: waste is reported, never absorbed). The stage-2 rate anchor 2.79e-06 s/cell/iter was itself measured at loadavg ~18 on 16 cores and is therefore an UPPER bound."
} > "$RUN_ROOT/CONTENTION.txt" 2>&1

LR="$RUN_ROOT/LAUNCH_RECORD.txt"
{ echo "case = VMFL078"
  echo "manual_pages = printed 223-224 (PDF 237-238)"
  echo "supersedes = nothing -- FIRST registration of this case; no VMFL078 register row exists"
  echo "launched_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "freeze_commit_head = $FREEZE_COMMIT"
  echo "prereg = $PREREG_REL"
  echo "prereg_blob = $PREREG_BLOB"
  echo "comparator = $GRADER_REL"
  echo "comparator_blob = $GRADER_BLOB"
  echo "launcher_blob_on_disk = $(git -C "$REPO" hash-object "$0")"
  echo "levels = $LEVELS_TO_RUN"
  echo "ranks = $RANKS (CONSTANT across levels: only the mesh changes between levels)"
  echo "endTime = $ENDTIME  (ITERATION ceiling; residualControl stops earlier)"
  echo "cap = NONE.  CASE_PROTOCOL_CHARTER v1.0 closing clause (Sanaa, 2026-09-10) exempts 3-D cases still to run from budget gates, time or money. Cost is MEASURED and recorded; nothing here stops a solve for spending."
  echo "smoke_mode = ${VMFL_SMOKE:-no}"
} > "$LR" || { echo "ABORT: cannot write LAUNCH_RECORD.txt"; exit 2; }

# --- OpenFOAM ----------------------------------------------------------------
source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo "ABORT: cannot source /usr/lib/openfoam/openfoam2606/etc/bashrc"; exit 2; }
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
  [ -n "${NX[$L]}" ] || { echo "ABORT: no registered mesh counts for level $L"; exit 2; }

  # AGE GUARD (rule 4): refuse a level directory that already holds 0/ or a numeric
  # time dir.  NO `[0-9]*` glob -- that also matches `0.orig` and reads a template as
  # an answer (L-339).  Numeric dirs by regex.
  if [ -d "$OUT/0" ]; then echo "ABORT age guard: $OUT already holds 0/ -- a run is never launched into a tree that already holds an answer"; exit 2; fi
  EXISTING_T="$(find "$OUT" -mindepth 1 -maxdepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?([eE][-+][0-9]+)?$' 2>/dev/null | head -1)"
  [ -z "$EXISTING_T" ] || { echo "ABORT age guard: $OUT already holds a numeric time directory ($EXISTING_T)"; exit 2; }

  echo "--- $L  ${NX[$L]}x${NY[$L]}x${NZ[$L]} = $(( NX[$L] * NY[$L] * NZ[$L] )) cells  ranks $RANKS  endTime $ENDTIME  (no cap, per the Case Protocol exemption)"
  mkdir -p "$OUT" || { echo "ABORT: mkdir $OUT"; exit 2; }
  cp -r "$CASE_DIR"/0 "$CASE_DIR"/constant "$CASE_DIR"/system "$OUT"/ || { echo "ABORT: cannot copy the case templates into $OUT"; exit 2; }

  sed -e "s/__NX__/${NX[$L]}/g" -e "s/__NY__/${NY[$L]}/g" -e "s/__NZ__/${NZ[$L]}/g" \
      "$OUT/system/blockMeshDict.template" > "$OUT/system/blockMeshDict" || { echo "ABORT: sed blockMeshDict for $L"; exit 2; }
  grep -q '__NX__\|__NY__\|__NZ__' "$OUT/system/blockMeshDict" && { echo "ABORT: blockMeshDict substitution did not take at $L"; exit 2; }
  sed -e "s/__ENDTIME__/$ENDTIME/g" "$OUT/system/controlDict.template" > "$OUT/system/controlDict" || { echo "ABORT: sed controlDict for $L"; exit 2; }
  grep -qE "^endTime[[:space:]]+$ENDTIME;" "$OUT/system/controlDict" || { echo "ABORT: controlDict endTime is not the registered $ENDTIME at $L"; exit 2; }
  grep -qF 'interpolationScheme cellPoint' "$OUT/system/controlDict" || { echo "ABORT: the cellPoint order-pollution fix is MISSING from the controlDict that would run at $L"; exit 2; }
  # AMENDED 2026-09-12 (before first compute; see PREREGISTRATION.md foot). The prior
  # form counted EVERY line in the whole controlDict beginning with 12 spaces and
  # "(0.5 ", which also matched two lines inside the UNRELATED probe block further down
  # (each holding five triples on one line) -- so it reported 203 for a centrelineProbe
  # block that carries exactly the registered 201. The guard measured something other
  # than what it claimed to measure. Scoped to the centrelineProbe function object.
  # The registered abscissa count is UNCHANGED at 201.
  NLOC="$(awk '/^    centrelineProbe/{f=1} f && /^    [a-zA-Z]/ && !/centrelineProbe/{f=0} f' "$OUT/system/controlDict" | grep -cE '^            \(0\.5 ')"
  [ "$NLOC" = "201" ] || { echo "ABORT: controlDict at $L carries $NLOC centreline probe locations, registered 201"; exit 2; }

  printf 'FoamFile { version 2.0; format ascii; class dictionary; object decomposeParDict; }\nnumberOfSubdomains %d;\nmethod          scotch;\n' "$RANKS" \
    > "$OUT/system/decomposeParDict" || { echo "ABORT: cannot write decomposeParDict at $L"; exit 2; }

  ( cd "$OUT" && blockMesh > log.blockMesh 2>&1 ) || { echo "ABORT: blockMesh failed at $L -- a crash is a FINDING, not a retry"; exit 2; }
  ( cd "$OUT" && checkMesh > log.checkMesh 2>&1 )

  # --- MESH BIRTH CERTIFICATE, from this level's own checkMesh ---------------
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
    raise SystemExit('  ABORT: checkMesh is not clean at this level (Case Protocol sec.2: quality within the registered gates or the case stops)')
PYBC

  ( cd "$OUT" && decomposePar > log.decomposePar 2>&1 ) || { echo "ABORT: decomposePar failed at $L"; exit 2; }

  # per-level pre-record, so a killed launcher still leaves what it was under
  printf 'level=%s\nstate=STARTED\nranks=%d\nendTime=%s\ncap=NONE (Case Protocol v1.0 3-D exemption)\nprereg_blob=%s\ncomparator_blob=%s\nstarted_utc=%s\n' \
    "$L" "$RANKS" "$ENDTIME" "$PREREG_BLOB" "$GRADER_BLOB" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$RUN_ROOT/RUN_RC.$L" \
    || { echo "ABORT: cannot write RUN_RC.$L"; exit 2; }

  # 0/ is touched LAST, immediately before the solver: it is the age-guard datum that
  # dates the run allowed to produce the answer (rule 4).
  touch "$OUT"/0/* || { echo "ABORT: cannot touch $OUT/0"; exit 2; }

  T0="$(date +%s)"
  # DETACHED SOLVER (L-336): setsid makes it its own session leader so it survives the
  # launching lane's death.  THE rc IS CAPTURED INSIDE the subshell, immediately after
  # the command returns -- `setsid cmd` returns 0 for every outcome when its rc is
  # taken OUTSIDE the wrapper (L-336, and the setsid-parent-returns-zero lesson).
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

  # Departure (c): the comparator's completion and age-guard checks read the TOP-LEVEL
  # time directory, which in parallel does not exist until this runs.
  if [ "$RC" -eq 0 ]; then
    ( cd "$OUT" && reconstructPar -latestTime > log.reconstructPar 2>&1 ) || echo "  WARN: reconstructPar failed at $L (the comparator will REFUSE on missing fields)"
  fi

  # latest numeric time directory, by REGEX and NUMERIC compare -- never a `[0-9]*`
  # glob and never a lexicographic sort (950 would beat 2000).
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

  printf 'rc = %s\nlevel = %s\nstate = FINISHED\nwait_rc = %d\nwall_s = %d\nranks = %d\ncore_min = %s\ntotal_core_min_so_far = %s\ncap = NONE\nendTime = %s\nlast_time_in_log = %s\nEnd_lines = %s\nSIMPLE_converged_lines = %s\nlatest_time_dir = %s\nfield_at_latest_newer_than_0_U = %s\ncells = %s\nnx = %s\nny = %s\nnz = %s\ndetach_wrapper_pid = %s\nprereg_blob = %s\ncomparator_blob = %s\nsolver_bin = %s\nutc = %s\nnote = rc is the mpirun/simpleFoam exit status, CAPTURED INSIDE the detached subshell. There is NO timeout and NO cap: CASE_PROTOCOL_CHARTER v1.0 closing clause exempts 3-D cases still to run from budget gates. core_min is MEASURED for the rule-12 calibration duty, which the exemption does not withdraw. L-342: this file is INFRASTRUCTURE -- absent, the comparator reports rc NOT MEASURED and still grades the physics artefacts.\n' \
    "$RC" "$L" "$WAIT_RC" "$WALL" "$RANKS" "$CORE_MIN" "$TOTAL_CORE_MIN" "$ENDTIME" "${LAST_TIME:-none}" "${ENDED:-0}" "${CONVERGED:-0}" "${ENDT_DIR:-none}" "$ENDT_OK" "${CELLS:-unknown}" "${NX[$L]}" "${NY[$L]}" "${NZ[$L]}" "$SOLVER_PID" "$PREREG_BLOB" "$GRADER_BLOB" "$SOLVER_BIN" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    > "$RUN_ROOT/RUN_RC.$L" || { echo "ABORT: cannot write RUN_RC.$L"; exit 2; }

  echo "level $L : rc=$RC wall_s=$WALL core_min=$CORE_MIN total=$TOTAL_CORE_MIN last_time=${LAST_TIME:-none} End_lines=${ENDED:-0} converged_lines=${CONVERGED:-0} latest_time_dir=${ENDT_DIR:-none} field_newer_than_0_U=$ENDT_OK" >> "$LR"

  # STOP AT THE FIRST NON-ZERO rc.  A crash is a FINDING, not a retry (SUPERVISION
  # sec.3 check 2).  This is not a budget stop and the exemption does not touch it.
  if [ "$RC" -ne 0 ]; then
    OVERALL_RC="$RC"
    echo "STOP $L: rc=$RC after ${WALL}s = ${CORE_MIN} core-min (running total ${TOTAL_CORE_MIN})."
    echo "  A non-zero rc is a FINDING, not a retry.  This is NOT a cap: there is no cap on this case."
    echo "later levels are NOT launched" >> "$LR"
    break
  fi
  echo "done $L: ${WALL}s = ${CORE_MIN} core-min (running total ${TOTAL_CORE_MIN}), latest time dir ${ENDT_DIR:-none}"
done

printf 'total_core_min = %s\nranks = %d\noverall_rc = %s\nsmoke_mode = %s\ncap = NONE (CASE_PROTOCOL_CHARTER v1.0 closing clause, Sanaa 2026-09-10: 3-D cases still to run carry no budget gate, time or money)\ncost_basis = core-minutes = wall_s*RANKS/60, MEASURED from this run. Dollars are DERIVED at the owner-stated c7a.4xlarge rate $0.0513/core-h (Sanaa 2026-08-21/22) and are REPORTED-BY-OWNER, NOT MEASURED -- the box cannot read its own billing (COMPUTE_BUDGET_CHARTER sec.5). The estimate-versus-actual comparison is landed in docs/COST_CALIBRATION.md at completion (rule 12); the exemption removes the cap, not the calibration.\n' \
  "$TOTAL_CORE_MIN" "$RANKS" "$OVERALL_RC" "${VMFL_SMOKE:-no}" > "$RUN_ROOT/COST.txt" || { echo "ABORT: cannot write COST.txt"; exit 2; }
echo "total_core_min = $TOTAL_CORE_MIN" >> "$LR"
echo "finished_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$LR"
echo "=== VMFL078 launcher done, overall rc=$OVERALL_RC, total ${TOTAL_CORE_MIN} core-min (no cap)"
echo "grade with: python3 $SCRIPT_DIR/grade_vmfl078.py --run-root $RUN_ROOT --out $RUN_ROOT/GRADING_VMFL078.json"
exit "$OVERALL_RC"
