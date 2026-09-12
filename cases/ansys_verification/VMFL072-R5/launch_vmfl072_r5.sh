#!/usr/bin/env bash
# =============================================================================
# VMFL072-R5 graded-run driver -- Liquid Water Film Down an Inclined Plate
# (Roy & Jain 1989), Ansys Fluid Dynamics Verification Manual 2026 R1 p.211-212.
# Model : regionModels::surfaceFilmModels::kinematicSingleLayer (isothermal,
#         laminar) driven by reactingParcelFoam run INERT (combustion none,
#         chemistry off, radiation off, cloud inactive). OpenFOAM v2606.
# Grid  : SINGLE grid, 256x64x4 primary carrier + 256x64 extruded film region.
# Ranks : 1 (serial). endTime 8.0 s, deltaT 1e-3, adjustTimeStep no -> 8000 steps.
#
# Frozen pre-registration : cases/ansys_verification/VMFL072-R5/PREREGISTRATION.md
# Frozen comparator       : cases/ansys_verification/VMFL072-R5/compare_vmfl072_r5.py
# Transitive dependency   : cases/ansys_verification/VMFL072-R4-A/compare_vmfl072_r4a.py
#                           (read by the comparator's AST reuse guard; blob pinned)
# Run root                : verification/runs/ansys_verification/VMFL072-R5/
#
# THREE PROPERTIES, each named so none reads as a slip:
#
#  (a) NO CAP, NO `timeout`, NO KILL OF ANY KIND. Owner directive ~2026-09-12T01:10Z
#      ("dont want any cap on any run") and the supervisor's ruling of the same date.
#      Every core-minute figure in PREREGISTRATION.md sec.6 is a CALIBRATION
#      PREDICTION, never a stop threshold. Cost is MEASURED and recorded (rule 12's
#      calibration duty survives the exemption); nothing here stops a solve for
#      spending. The only ceiling is endTime, an ITERATION ceiling, not a budget gate.
#      A silently hung solver is watched by the report-only stall observer (sec.6),
#      which escalates and NEVER kills.
#
#  (b) 1 RANK (serial). PREREGISTRATION.md sec.6: the ladder is cheap and serial is
#      the good-citizen choice on an oversubscribed box; core-min = wall_s/60 exactly.
#
#  (c) NO `set -u`. CATEGORICALLY INCOMPATIBLE with OpenFOAM v2606: sourcing
#      etc/bashrc dereferences unbound vars (measured rc 127), and with `set -u` the
#      shell EXITS before any `|| fallback` can write a marker -- a silent failure.
#      EVERY check gates EXPLICITLY with `|| { echo ABORT...; exit <n>; }`, and the
#      launch record is written BEFORE the risky solver step, not after.
# =============================================================================

RANKS=1
ENDTIME=8.0             # ITERATION ceiling (8000 steps at deltaT 1e-3), NOT a budget gate
WRITEINT=50             # -> 160 written time directories
EXPECT_STEPS=8000
EXPECT_DIRS=160

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_DIR="$SCRIPT_DIR/base"
RUN_ROOT="${1:?usage: launch_vmfl072_r5.sh <run_root>}"

echo "=== VMFL072-R5 launcher  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)  run_root=$RUN_ROOT"

# --- smoke mode: scratch ONLY, never the graded run root ---------------------
if [ -n "$VMFL_SMOKE" ]; then
  case "$RUN_ROOT" in
    */scratchpad/*|*/scratchpad|/tmp/*) : ;;
    *) echo "ABORT: VMFL_SMOKE refuses run_root '$RUN_ROOT' -- a smoke runs in scratch ONLY"; exit 2 ;;
  esac
  ENDTIME=0.005; WRITEINT=100000; EXPECT_STEPS=5; EXPECT_DIRS=0
  echo "  SMOKE MODE: endTime $ENDTIME IN SCRATCH; grades nothing, freezes nothing"
fi

# --- 1. LAUNCH-TIME FREEZE CHECK (CLAUDE.md rule 2) --------------------------
REPO="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" || { echo "ABORT: not inside a git repository"; exit 2; }
PREREG_REL="cases/ansys_verification/VMFL072-R5/PREREGISTRATION.md"
GRADER_REL="cases/ansys_verification/VMFL072-R5/compare_vmfl072_r5.py"
R4A_REL="cases/ansys_verification/VMFL072-R4-A/compare_vmfl072_r4a.py"
R4A_PINNED="ca2c73c70ce72a9aa12cf436a482ba83246158f1"   # must match R4A_BLOB_SHA in the comparator
FREEZE_COMMIT="$(git -C "$REPO" rev-parse HEAD)" || { echo "ABORT: cannot resolve HEAD"; exit 2; }

check_blob() {   # $1 = repo-relative path -> echoes the verified disk blob
  local rel="$1"
  git -C "$REPO" cat-file -e "HEAD:$rel" 2>/dev/null || { echo "ABORT: $rel is NOT committed at HEAD -- the freeze IS the evidence (rule 2)" >&2; exit 2; }
  local head disk
  head="$(git -C "$REPO" rev-parse "HEAD:$rel")" || { echo "ABORT: cannot resolve HEAD blob of $rel" >&2; exit 2; }
  disk="$(git -C "$REPO" hash-object "$REPO/$rel")" || { echo "ABORT: cannot hash $rel on disk" >&2; exit 2; }
  [ "$disk" = "$head" ] || { echo "ABORT freeze check: $rel on disk ($disk) != HEAD blob ($head)" >&2; exit 2; }
  echo "$disk"
}

PREREG_BLOB="$(check_blob "$PREREG_REL")" || exit 2
GRADER_BLOB="$(check_blob "$GRADER_REL")" || exit 2
R4A_BLOB="$(check_blob "$R4A_REL")" || exit 2
echo "  freeze OK  prereg $PREREG_BLOB"
echo "  freeze OK  comparator $GRADER_BLOB"
echo "  freeze OK  r4a (transitive dep) $R4A_BLOB"

# The transitive dependency's blob must equal BOTH the value pinned here AND the
# R4A_BLOB_SHA constant inside the comparator -- otherwise the comparator's own
# blob-pin guard would refuse at grade time and this launcher would have run a
# solve whose result cannot be graded.
[ "$R4A_BLOB" = "$R4A_PINNED" ] || { echo "ABORT: r4a blob $R4A_BLOB != launcher-pinned $R4A_PINNED"; exit 2; }
grep -qF "R4A_BLOB_SHA = \"$R4A_PINNED\"" "$REPO/$GRADER_REL" || { echo "ABORT: comparator does not pin r4a blob $R4A_PINNED (its AST guard would refuse at grade time)"; exit 2; }
echo "  r4a pin agrees: launcher == comparator R4A_BLOB_SHA == HEAD blob"

# --- CASE INPUTS: every tracked file under base/ hashed against its HEAD blob -
NINP=0
while IFS= read -r rel; do
  [ -n "$rel" ] || continue
  check_blob "$rel" >/dev/null || exit 2
  NINP=$((NINP+1))
done < <(git -C "$REPO" ls-files "cases/ansys_verification/VMFL072-R5/base")
[ "$NINP" -ge 20 ] || { echo "ABORT: only $NINP case-input files tracked under base/ -- expected the full case tree (>=20)"; exit 2; }
echo "  case inputs OK: $NINP files under base/, each byte-identical to its HEAD blob"

# --- 2. CONTROLS (rule 3): the comparator's --selftest, BOTH interpreters -----
# `python3 -O` deletes every assert; a control that exists only under one flag is
# not a control (L-332). The comparator uses raise Refuse, never bare assert, so
# both must agree and both must be green.
ST="$RUN_ROOT.selftest.$$"
mkdir -p "$(dirname "$ST")" 2>/dev/null
rm -rf "$SCRIPT_DIR/__pycache__"
python3    "$SCRIPT_DIR/compare_vmfl072_r5.py" --selftest > "$ST"   2>&1; RC_PLAIN=$?
rm -rf "$SCRIPT_DIR/__pycache__"
python3 -O "$SCRIPT_DIR/compare_vmfl072_r5.py" --selftest > "$ST.O" 2>&1; RC_O=$?
[ "$RC_PLAIN" = "0" ] || { echo "ABORT: comparator --selftest NOT green under python3 (rc $RC_PLAIN); see $ST"; exit 2; }
[ "$RC_O" = "0" ]     || { echo "ABORT: comparator --selftest NOT green under python3 -O (rc $RC_O); see $ST.O"; exit 2; }
NP_PLAIN="$(grep -c '^  PASS ' "$ST")"; NP_O="$(grep -c '^  PASS ' "$ST.O")"
NF_PLAIN="$(grep -c '^  FAIL ' "$ST")"; NF_O="$(grep -c '^  FAIL ' "$ST.O")"
[ "$NP_PLAIN" = "$NP_O" ] || { echo "ABORT: --selftest PASS count differs python3 $NP_PLAIN vs -O $NP_O (L-332)"; exit 2; }
[ "$NF_PLAIN" = "0" ] && [ "$NF_O" = "0" ] || { echo "ABORT: --selftest has FAILs (python3 $NF_PLAIN, -O $NF_O)"; exit 2; }
for MARK in \
  'blob pin is load-bearing' \
  'live-plant mutant [neutered-writer]' \
  'live-plant mutant [constant-reader]' \
  'live-plant mutant [phantom-offset-reader]' \
  'live-plant mutant [neutered-plant]' \
  'mutation control: WITHOUT the max|Uf| gate' \
  'mutation control: WITHOUT the NaN/inf guard' \
  'conjunct C-10' \
  'footprint guard load-bearing' ; do
  grep -qF "$MARK" "$ST"   || { echo "ABORT: --selftest did not DRIVE the control: $MARK (python3)"; exit 2; }
  grep -qF "$MARK" "$ST.O" || { echo "ABORT: --selftest did not DRIVE the control: $MARK (-O)"; exit 2; }
done
echo "  controls OK: --selftest $NP_PLAIN PASS, 0 FAIL, python3 and -O agree, all named controls driven"
rm -f "$ST" "$ST.O"

# --- run root, age guard, contention + launch records ------------------------
mkdir -p "$RUN_ROOT" || { echo "ABORT: cannot create $RUN_ROOT"; exit 2; }
# AGE GUARD (rule 4): refuse a run root that already holds 0/ or a NUMERIC time
# dir. Regex, not a `[0-9]*` glob -- that also matches 0.orig and reads a template
# as an answer (L-339).
if [ -d "$RUN_ROOT/0" ]; then echo "ABORT age guard: $RUN_ROOT already holds 0/ -- never launch into a tree that holds an answer"; exit 2; fi
EXISTING_T="$(find "$RUN_ROOT" -mindepth 1 -maxdepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?([eE][-+][0-9]+)?$' 2>/dev/null | head -1)"
[ -z "$EXISTING_T" ] || { echo "ABORT age guard: $RUN_ROOT already holds a numeric time directory ($EXISTING_T)"; exit 2; }

{ echo "sampled_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "uptime = $(uptime)"
  echo "nproc = $(nproc)"
  echo "loadavg = $(cut -d' ' -f1-3 /proc/loadavg)"
  echo "mem_available_MB = $(free -m | awk 'NR==2{print $7}')"
  echo "note = contention at launch. RANKS=1 so core_min = wall_s/60 exactly; a busy box inflates wall_s. The contention factor ClockTime/ExecutionTime is MEASURED on THIS run's own log (below) and is PER-RUN, never a lab number (PREREGISTRATION.md sec.6)."
} > "$RUN_ROOT/CONTENTION.txt" 2>&1

LR="$RUN_ROOT/LAUNCH_RECORD.txt"
{ echo "case = VMFL072-R5"
  echo "manual_pages = printed 211-212 (Roy & Jain 1989, film thickness target 0.555 mm)"
  echo "launched_utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "freeze_commit_head = $FREEZE_COMMIT"
  echo "prereg = $PREREG_REL  blob = $PREREG_BLOB"
  echo "comparator = $GRADER_REL  blob = $GRADER_BLOB"
  echo "transitive_dep = $R4A_REL  blob = $R4A_BLOB (pinned $R4A_PINNED)"
  echo "launcher_blob_on_disk = $(git -C "$REPO" hash-object "$0" 2>/dev/null)"
  echo "ranks = $RANKS (serial)"
  echo "endTime = $ENDTIME  deltaT = 1e-3  adjustTimeStep = no  -> $EXPECT_STEPS steps, $EXPECT_DIRS written dirs"
  echo "cap = NONE. Owner no-cap directive 2026-09-12 + supervisor ruling. Cost is MEASURED and calibrated (rule 12); nothing stops a solve for spending."
  echo "smoke_mode = ${VMFL_SMOKE:-no}"
} > "$LR" || { echo "ABORT: cannot write LAUNCH_RECORD.txt"; exit 2; }

# --- OpenFOAM ----------------------------------------------------------------
source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo "ABORT: cannot source the v2606 bashrc"; exit 2; }
for B in reactingParcelFoam blockMesh topoSet extrudeToRegionMesh checkMesh; do
  command -v "$B" >/dev/null || { echo "ABORT: $B not on PATH after sourcing the v2606 bashrc"; exit 2; }
done
SOLVER_BIN="$(command -v reactingParcelFoam)"
echo "solver_bin = $SOLVER_BIN" >> "$LR"
echo "  reactingParcelFoam = $SOLVER_BIN, $RANKS rank"

# --- stage the case, substitute the FROZEN run parameters --------------------
cp -r "$BASE_DIR"/0.orig "$BASE_DIR"/constant "$BASE_DIR"/system "$RUN_ROOT"/ || { echo "ABORT: cannot stage base/ into $RUN_ROOT"; exit 2; }
sed -e "s/@ENDTIME@/$ENDTIME/g" -e "s/@WRITEINT@/$WRITEINT/g" -i "$RUN_ROOT/system/controlDict" || { echo "ABORT: sed controlDict"; exit 2; }
grep -q '@ENDTIME@\|@WRITEINT@' "$RUN_ROOT/system/controlDict" && { echo "ABORT: controlDict token substitution did not take"; exit 2; }
# guards SCOPED to the exact line each claims to measure (VMFL078 probe-count trap)
grep -qE "^endTime[[:space:]]+$ENDTIME;" "$RUN_ROOT/system/controlDict" || { echo "ABORT: controlDict endTime != $ENDTIME"; exit 2; }
grep -qE "^deltaT[[:space:]]+1e-03;" "$RUN_ROOT/system/controlDict" || { echo "ABORT: controlDict deltaT != 1e-03 (the step count would not be $EXPECT_STEPS)"; exit 2; }
grep -qE "^adjustTimeStep[[:space:]]+no;" "$RUN_ROOT/system/controlDict" || { echo "ABORT: adjustTimeStep is not 'no' (ExecutionTime count would not be deterministic)"; exit 2; }
# the FROZEN film linear solver (PREREGISTRATION.md sec.3): smoothSolver, no DILU
grep -qF "smoothSolver" "$RUN_ROOT/system/wallFilmRegion/fvSolution" || { echo "ABORT: film fvSolution is not the frozen smoothSolver (a preconditioned solver could re-enter calcReciprocalD)"; exit 2; }
grep -qiE "DILU|PBiCGStab|PCG" "$RUN_ROOT/system/wallFilmRegion/fvSolution" && { echo "ABORT: film fvSolution names a reciprocal-diagonal preconditioner/solver -- the frozen choice is smoothSolver only (sec.3)"; exit 2; }

# --- mesh pipeline (a crash here is a FINDING, not a retry) -------------------
cd "$RUN_ROOT" || { echo "ABORT: cannot cd $RUN_ROOT"; exit 2; }
cp -r 0.orig 0 || { echo "ABORT: cannot restore 0/ from 0.orig"; exit 2; }
blockMesh > log.blockMesh 2>&1 || { echo "ABORT: blockMesh failed"; tail -20 log.blockMesh; exit 3; }
topoSet -dict system/wallFilmRegion.topoSet > log.topoSet 2>&1 || { echo "ABORT: topoSet failed"; tail -20 log.topoSet; exit 3; }
extrudeToRegionMesh -overwrite > log.extrudeToRegionMesh 2>&1 || { echo "ABORT: extrudeToRegionMesh failed"; tail -25 log.extrudeToRegionMesh; exit 3; }
# checkMesh on the FILM region writes the 'cells:' line the comparator's C-16 reads.
checkMesh -region wallFilmRegion > log.checkMesh.wallFilmRegion 2>&1 || echo "  NOTE: checkMesh -region returned nonzero; its 'cells:' line is still parsed by C-16 (checkMesh warns on many benign mesh facts)"
FCELLS="$(grep -m1 'cells:' log.checkMesh.wallFilmRegion | grep -oE '[0-9]+' | tail -1)"
echo "  mesh OK: film region cells = ${FCELLS:-unknown} (comparator expects 16384)"

# --- report-only stall observer (NEVER kills), spawned before the solver -----
if [ -x "$SCRIPT_DIR/stall_observer_vmfl072_r5.sh" ]; then
  setsid "$SCRIPT_DIR/stall_observer_vmfl072_r5.sh" "$RUN_ROOT" 600 "$RUN_ROOT/RC.txt" 30 >/dev/null 2>&1 &
  echo "  stall observer spawned (600 s, report-only, pid $!)"
fi

# --- the solve. rc captured INSIDE this wrapper (no setsid around it, so the
#     'setsid parent returns zero' trap cannot apply). NO timeout, NO cap. ------
# Touch 0/U LAST at launch so it dates the run for the comparator's age guard.
touch "$RUN_ROOT/0/U"
echo "  launching reactingParcelFoam (no cap, no timeout) utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
S=$(date +%s.%N)
reactingParcelFoam > log.reactingParcelFoam 2>&1
RC=$?
E=$(date +%s.%N)
WALL_S="$(echo "$E - $S" | bc)"
CORE_MIN="$(echo "scale=4; $WALL_S * $RANKS / 60" | bc)"
# BOTH ExecutionTime (CPU) and ClockTime (wall) from the solver's own log tail,
# so the PER-RUN contention factor ClockTime/ExecutionTime is measurable (sec.6).
EXEC_T="$(grep -E '^ExecutionTime = ' log.reactingParcelFoam | tail -1 | sed -E 's/^ExecutionTime = ([0-9.]+).*/\1/')"
CLOCK_T="$(grep -E 'ClockTime = ' log.reactingParcelFoam | tail -1 | sed -E 's/.*ClockTime = ([0-9.]+).*/\1/')"
NEXEC="$(grep -cE '^ExecutionTime = ' log.reactingParcelFoam)"
CONTENTION="$( [ -n "$EXEC_T" ] && [ -n "$CLOCK_T" ] && [ "$EXEC_T" != "0" ] && echo "scale=4; $CLOCK_T / $EXEC_T" | bc || echo "unmeasurable")"

{ echo "rc = $RC"
  echo "state = FINISHED"
  echo "utc = $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "ranks = $RANKS"
  echo "wall_s = $WALL_S"
  echo "core_min = $CORE_MIN     # = wall_s*ranks/60 (RANKS=1: core_min == wall_min)"
  echo "ExecutionTime_cpu_s = ${EXEC_T:-none}   # CPU seconds (contention-independent)"
  echo "ClockTime_wall_s = ${CLOCK_T:-none}     # wall seconds"
  echo "contention_factor = $CONTENTION   # ClockTime/ExecutionTime, PER-RUN, measured on THIS log (sec.6)"
  echo "ExecutionTime_lines = $NEXEC   # completion C-06 expects $EXPECT_STEPS"
  echo "loadavg_at_grade = $(cut -d' ' -f1-3 /proc/loadavg)"
  echo "NOTE = no cap fired and none exists; these figures are for the rule-12 calibration row, not a stop."
} > "$RUN_ROOT/RC.txt"

echo "=== VMFL072-R5 solve returned rc=$RC  wall_s=$WALL_S  core_min=$CORE_MIN  ExecutionTime=${EXEC_T}s  ClockTime=${CLOCK_T}s  contention=$CONTENTION"
echo "=== RC.txt written to $RUN_ROOT/RC.txt.  Grade with: python3 $SCRIPT_DIR/compare_vmfl072_r5.py --runroot $RUN_ROOT"
exit "$RC"
