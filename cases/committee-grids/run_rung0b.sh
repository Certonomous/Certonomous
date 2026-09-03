#!/bin/bash
# run_rung0b.sh -- the RUNG 0b driver. The SUCCESSOR run, grading all five gates.
#
# Registration: verification/campaign/RUNG0b_MESH_IMPORT_PREREGISTRATION.md.
# Predecessor:  verification/campaign/RUNG0_MESH_IMPORT_PREREGISTRATION.md, frozen at
#               d127d83d4ebf4caaaf0c12c39a063c5f624a03a4. NOT AMENDED. Its PENDING
#               stands as committed.
# Authority for the successor route: f5b8deec, verification CHARTER v1.52.
#
# WHAT IT RUNS.  Phase-A controls FIRST at zero conversion cost; then, per grid,
# ugrid_to_foam.py and checkMesh; then grade_rung0b.py, which runs the phase-B controls
# and grades R0-G1, R0-G2a, **R0-G2b**, R0-G3 and R0-G4 -- section 4's conjunction AS
# WRITTEN, all five gates.
#
# WHAT IS DIFFERENT FROM run_rung0.sh, AND IT IS THE WHOLE POINT.  R0-G2b IS RUNNABLE.
# cases/committee-grids/foam_to_ugrid.py exists, it is INSIDE the grading path, and
# grade_rung0b.py invokes its round trip per grid. A `PASS` IS THEREFORE REACHABLE FROM
# THIS DRIVER, and it is reachable only through section 4's conjunction over all five
# gates on all four grids.
#
# THE COMPARATOR LIVES OUTSIDE THE RUN ROOT, and that is a filing fix, not a gate
# change. The predecessor filed its comparator INSIDE the run root whose absence was
# its own pre-compute proof, so no honest pin could exist and its queue row read
# ABSENT-AT-FREEZE. This one is in cases/, so the freeze commit carries the comparator,
# the writer and the reader while the run root does not yet exist.
#
# THE CAP IS STRUCTURAL, NOT A POLICY.  Section 5.2 fixes the hard cap at 13.2 core-min.
# At ranks = 1 that is 792 wall seconds, enforced by a `timeout` budget RECOMPUTED
# BEFORE EVERY STEP from one total. An overrun STOPS THE RUN; it does not get a new
# budget (CLAUDE.md rule 12). A cap nothing enforces is not a cap.
#
# THE FLEET SAFETY CEILING is section 5.3's 39.6 core-min = 2376 wall s at 1 rank, and
# it is a SECOND, independent `timeout` around the whole driver, so that a defect in the
# per-step budget arithmetic cannot let the box be eaten. Sanaa 2026-09-03 ~21:00Z: the
# one hard structural stop that survives.
#
# R0-G4, THE NO-CLOBBER GUARD.  The driver REFUSES (exit 3) if any target case directory
# already exists, writing nothing. It stamps RUN_ROOT_CREATED_EPOCH BEFORE producing any
# artifact, and every artifact the comparator grades must be NEWER than that stamp.
#
# rc IS CAPTURED INSIDE THIS SCRIPT, never around a `setsid` line: `setsid timeout cmd`
# exits 0 for every outcome, so a wrapper reading the setsid parent's rc reads a
# constant zero.
set -u

RUN_ROOT=/home/ubuntu/Certonomous/verification/runs/RUNG0b_MESH_IMPORT_runs
GRIDDIR_DPW5=/home/ubuntu/certonomous-runs/dpw5-committee-probe/grid
GRIDDIR_HLPW6=/home/ubuntu/certonomous-runs/hlpw6-memory-probe/grid
CONV=/home/ubuntu/Certonomous/cases/committee-grids/ugrid_to_foam.py
GRADE=/home/ubuntu/Certonomous/cases/committee-grids/grade_rung0b.py

CAP_CORE_MIN=13.2
RANKS=1
BUDGET=792                                   # 13.2 * 60 / 1. THE WHOLE RUN'S BUDGET.
CEILING=2376                                 # 39.6 core-min. Section 5.3's fleet stop.
START=$(date +%s)

STATUS="$RUN_ROOT/STATUS.RUNG0b_MESH_IMPORT"
mkdir -p "$RUN_ROOT"

say() { echo "[$(date -u +%H:%M:%S)] $*"; }
remaining() { local now; now=$(date +%s); echo $(( BUDGET - (now - START) )); }
fail() { say "STOPPED rc=$1: $2"; echo "rc=$1 $2" > "$STATUS"; exit "$1"; }

# ---- R0-G4: refuse a pre-existing case directory. Rule 4's guard. ----------------
CASES="DPW5_L1T_hex DPW5_L1T_prism DPW5_L1T_hybrid HLPW6_h6c1_rans_3a_1"
for C in $CASES; do
  if [ -e "$RUN_ROOT/$C" ]; then
    fail 3 "R0-G4 no-clobber: $RUN_ROOT/$C already exists. A run is never launched into a tree that already holds an answer."
  fi
done

# ---- the age-guard datum, stamped BEFORE any artifact is produced. ---------------
date +%s.%N > "$RUN_ROOT/RUN_ROOT_CREATED_EPOCH"
say "RUN_ROOT_CREATED_EPOCH = $(cat "$RUN_ROOT/RUN_ROOT_CREATED_EPOCH")"

# ⚠ `set -u` MUST BE OFF ACROSS THIS SOURCE LINE. RUNG 0 attempt 1 died here:
# /usr/lib/openfoam/openfoam2606/etc/bashrc:184 reads WM_PROJECT_DIR before setting it,
# and an unbound variable in a SOURCED file kills the sourcing shell outright -- after
# the epoch stamp and before any `fail` handler could write a STATUS. The defect was the
# SILENCE, not the exit code. Designed out here rather than re-learned.
set +u
. /usr/lib/openfoam/openfoam2606/etc/bashrc >/dev/null 2>&1
set -u
[ -n "${FOAM_APPBIN:-}" ] || fail 4 "FOAM_APPBIN unset after sourcing the OpenFOAM bashrc -- the environment did not come up"
export PATH="$FOAM_APPBIN:$PATH"
command -v checkMesh >/dev/null || fail 4 "checkMesh not on PATH after sourcing the OpenFOAM bashrc"
say "OpenFOAM environment up: $(command -v checkMesh)"

# ---- PHASE A controls run FIRST, at ZERO conversion cost. ------------------------
say "phase-A planted controls (registration section 7) -- before any conversion"
timeout "$(remaining)" python3 "$GRADE" --run-root "$RUN_ROOT" --controls-only \
    > "$RUN_ROOT/log.controls" 2>&1
RC=$?
[ $RC -eq 0 ] || fail 5 "phase-A controls did not all fire (rc=$RC) -- NOT A RESULT, and no core-minutes were spent on a conversion"
say "phase-A controls: all fired"

echo "{\"steps\":[" > "$RUN_ROOT/TIMING.json"
FIRST=1

one_grid() {
  local NAME=$1 UG=$2 MB=$3
  local C="$RUN_ROOT/$NAME"
  mkdir -p "$C/constant" "$C/system"
  cat > "$C/system/controlDict" <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object controlDict; }
application     simpleFoam;
startFrom       startTime;  startTime 0;
stopAt          endTime;    endTime   1;
deltaT          1;          writeControl timeStep;  writeInterval 1000;
runTimeModifiable false;
EOF
  # checkMesh in v2606 constructs an fvMesh and needs these two dictionaries. Their
  # absence aborted RUNG1_M6 attempt 1 after a VALID mesh had already been built and
  # cost 0.9167 core-min of waste. Written here so that cannot recur.
  cat > "$C/system/fvSchemes" <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object fvSchemes; }
ddtSchemes      { default steadyState; }
gradSchemes     { default Gauss linear; }
divSchemes      { default none; }
laplacianSchemes{ default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes   { default corrected; }
EOF
  cat > "$C/system/fvSolution" <<'EOF'
FoamFile { version 2.0; format ascii; class dictionary; object fvSolution; }
solvers { }
EOF

  local T0 T1 R CONVS CHECKS
  T0=$(date +%s)
  [ "$(remaining)" -gt 0 ] || fail 6 "cap exhausted before converting $NAME"
  say "convert $NAME"
  timeout "$(remaining)" python3 "$CONV" "$UG" "$MB" "$C" > "$C/log.convert" 2>&1
  R=$?
  [ $R -eq 0 ] || fail 7 "ugrid_to_foam rc=$R on $NAME (124 = cap stop)"
  T1=$(date +%s); CONVS=$((T1-T0))

  T0=$(date +%s)
  [ "$(remaining)" -gt 0 ] || fail 6 "cap exhausted before checkMesh on $NAME"
  say "checkMesh $NAME"
  ( cd "$C" && timeout "$(remaining)" checkMesh > log.checkMesh 2>&1 )
  R=$?
  [ $R -eq 0 ] || fail 8 "checkMesh rc=$R on $NAME (124 = cap stop). A non-zero rc here is a PROCESS failure. checkMesh's own mesh VERDICT is never read by this rung (L-459)."
  T1=$(date +%s); CHECKS=$((T1-T0))

  [ $FIRST -eq 1 ] || echo "," >> "$RUN_ROOT/TIMING.json"
  FIRST=0
  printf '{"grid":"%s","convert_wall_s":%d,"checkMesh_wall_s":%d,"ranks":%d}' \
      "$NAME" "$CONVS" "$CHECKS" "$RANKS" >> "$RUN_ROOT/TIMING.json"
  say "$NAME done: convert ${CONVS}s checkMesh ${CHECKS}s  (remaining budget $(remaining)s)"
}

one_grid DPW5_L1T_hex         "$GRIDDIR_DPW5/L1.T.rev01.p3d.hex.r8.ugrid"    "$GRIDDIR_DPW5/dpw5_L1T.mapbc"
one_grid DPW5_L1T_prism       "$GRIDDIR_DPW5/L1.T.rev01.p3d.prism.r8.ugrid"  "$GRIDDIR_DPW5/dpw5_L1T.mapbc"
one_grid DPW5_L1T_hybrid      "$GRIDDIR_DPW5/L1.T.rev01.p3d.hybrid.r8.ugrid" "$GRIDDIR_DPW5/dpw5_L1T.mapbc"
one_grid HLPW6_h6c1_rans_3a_1 "$GRIDDIR_HLPW6/h6c1_rans_3a_1.b8.ugrid"       "$GRIDDIR_HLPW6/h6c1_rans_3a_1.mapbc"

echo "]}" >> "$RUN_ROOT/TIMING.json"

# ---- grading: phase-B controls, then all five gates including R0-G2b. ------------
say "grading (phase-B controls, then R0-G1 / R0-G2a / R0-G2b / R0-G3 / R0-G4)"
timeout "$(remaining)" python3 "$GRADE" --run-root "$RUN_ROOT" > "$RUN_ROOT/log.analyse" 2>&1
RC=$?
TOTAL=$(( $(date +%s) - START ))
CORE_MIN=$(python3 -c "print(round($TOTAL*$RANKS/60.0,4))")
say "TOTAL ${TOTAL} wall s at ${RANKS} rank = ${CORE_MIN} core-min (cap ${CAP_CORE_MIN}, ceiling 39.6)"
echo "rc=$RC total_wall_s=$TOTAL core_min=$CORE_MIN cap_core_min=$CAP_CORE_MIN ceiling_core_min=39.6" > "$STATUS"
[ $RC -eq 0 ] || fail 9 "grade_rung0b rc=$RC -- see $RUN_ROOT/log.analyse"
say "DONE. Verdict is in $RUN_ROOT/RESULTS.json and log.analyse. All five gates were graded."
exit 0
