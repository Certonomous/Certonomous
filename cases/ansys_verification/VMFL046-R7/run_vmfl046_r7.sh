#!/usr/bin/env bash
# =============================================================================
# VMFL046-R7 graded-run driver.
# Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p.155 (VMFL046).
#
# Solver: rhoCentralFoam (OpenFOAM v2606) -- DENSITY-BASED, TRANSIENT, KNP central-upwind
# shock capturing (Greenshields, Weller, Gasparini & Reese 2010, DOI 10.1002/fld.2069).
# 2-D half-nozzle, laminar.  Solver, outlet (waveTransmissive lInf 0.3), schemes (vanLeer),
# maxCo 0.2, endTime, mesh, sampler, DELTA_X and the GATE are all carried from R6.
#
# R7 IS ONE DELIBERATE CHANGE vs R6 AND NOTHING ELSE:
#   AXIS (INITIAL CONDITION)  0/U internalField uniform (100 0 0) -> uniform (0 0 0):
#     the ANSWER-BLIND START-FROM-REST.  R6 (register row #63) core-dumped at Time
#     ~1.86e-4 s with "Negative initial temperature T0 = -16.02 K": the impulsive uniform
#     IC (U=100 m/s -- subsonic everywhere, incl. the eventually-supersonic diverging
#     section -- against p=200000 mismatched to both BCs) drove e = rhoE/rho - 0.5|U|^2
#     negative during the violent startup.  An answer-blind scratch smoke FALSIFIED the
#     Courant/Minmod ramp lever (Minmod at maxCo 0.05 still blew up at ~1.93e-4 s) and
#     ISOLATED the fix to start-from-rest at the FROZEN R6 config (rc 0, no negative-T,
#     stable march to 4e-3 s, Courant pinned 0.209).  Zero velocity plants no shock, no
#     location, no bias; the steady shock is set by the FROZEN pressure BCs (inlet
#     totalPressure p0 301325, outlet waveTransmissive fieldInf 176325) and is IC-independent
#     for a convergent transient -- gate-blind (PREREGISTRATION.md sec 3).
#
# THE PREDECESSOR IS R6.  The driver carries a BOTH-DIRECTIONS parity assert against R6 and
# REFUSES to launch (exit 7) if it is violated:
#   DIRECTION 1  the NINE carried inputs (0/T, 0/p, momentumTransport, thermophysicalProperties,
#                turbulenceProperties, blockMeshDict.template, controlDict.template, fvSchemes,
#                fvSolution) must be byte-identical to R6's -- R7 touches ONLY the IC.
#   DIRECTION 2  the deliberate change must be present AND be the registered one:
#                  - 0/U differs from R6 AND its internalField line carries `uniform (0 0 0)`
#                    AND its internalField line does NOT carry `(100 0 0)` (the boundaryField
#                    retains (100 0 0) as byte-identical patch `value` placeholders -- so the
#                    negative assert is scoped to the internalField LINE, not the whole file);
#                  - 0/p is byte-identical to R6 (p=200000, waveTransmissive lInf 0.3 preserved
#                    -- the smoke showed dropping p to 176325 re-destabilises the startup);
#                  - the case carries EXACTLY 10 files (unchanged from R6).
# A successor that reverted the IC, or touched any carried input, is UNFREEZABLE here.
#
# Frozen pre-registration: cases/ansys_verification/VMFL046-R7/PREREGISTRATION.md
# Frozen comparator      : cases/ansys_verification/VMFL046-R7/grade_vmfl046_r7.py
#                          (COMMENT-ONLY successor of grade_vmfl046_r6.py, blob bad1408f;
#                           ast.dump-equal, tokenize-equal excl comments; selftest 70 ok/0)
# Frozen reference       : cases/ansys_verification/VMFL046/quasi1d_reference.py (R1, unchanged)
# Run root (cwd)         : verification/runs/ansys_verification/VMFL046-R7/ (never the case dir)
#
# THE DRIVER SOURCES ITS OWN OpenFOAM ENVIRONMENT AND ONLY THEN ASSERTS ITS TOOLS ON PATH
# (charter sec14/sec15; the VMFL072 G-00 lesson).
#
# NO `set -u`.  THE CAP IS ENFORCED TWICE (rule 12, charter sec26.2): a PER-LEVEL cap and a
# RUNNING TOTAL.  An overrun STOPS the run (rc 124); it does not get a new budget.
# =============================================================================

RANKS=1

# --- COST (PREREGISTRATION sec7).  BASIS CARRIED FROM R6 (rhoCentralFoam still unmeasured --
# R6 core-dumped in startup): POINT ESTIMATE 538 core-min (L1 8.88 / L2 60.14 / L3 468.90),
# from R4's measured per-level actuals x f_solver 1.10.  Start-from-rest may modestly change
# the step count but stays inside f_solver in [0.7,1.5], which the ~3x caps absorb.  The true
# rhoCentralFoam f_solver calibration (vs the assumed 1.10) is OWED at R7 completion (rule 12).
CAP_CORE_MIN=1614                # RUNNING TOTAL (>= 3 x 537.9)
declare -A CAP_LEVEL=( [L1]=27 [L2]=181 [L3]=1410 )  # >= 3x 8.88 / 60.14 / 468.90

# endTime is PHYSICAL SECONDS and is R6's (== R5 == R4 == R3), UNCHANGED: 0.080 s.
# VMFL046R7_ENDTIME overrides ONLY for a CLAUSE-B smoke; the frozen comparator REFUSES any
# level whose controlDict does not carry the graded value.
ENDTIME="${VMFL046R7_ENDTIME:-0.080}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CASE_DIR="$SCRIPT_DIR/case"
R6_CASE_DIR="$REPO_ROOT/cases/ansys_verification/VMFL046-R6/case"
RUN_ROOT="${1:?usage: run_vmfl046_r7.sh <run_root> [levels...]}"
shift 2>/dev/null
LEVELS_TO_RUN="${*:-L1 L2 L3}"
SMOKE="${VMFL046R7_SMOKE:-0}"

# The GRADED centreline sampling interval is 5.0e-04 s and the frozen comparator refuses any
# other value (grade_vmfl046_r7.py SAMPLE_DT).  Overridable ONLY under a CLAUSE-B smoke.
SAMPLEDT=5.0e-04
if [ "$SMOKE" = "1" ] && [ -n "$VMFL046R7_SAMPLEDT" ]; then SAMPLEDT="$VMFL046R7_SAMPLEDT"; fi

# The NINE inputs carried from R6 BYTE-IDENTICAL (everything except the IC velocity 0/U).
CARRIED=( "0/T" "0/p" "constant/momentumTransport" "constant/thermophysicalProperties" \
          "constant/turbulenceProperties" "system/blockMeshDict.template" \
          "system/controlDict.template" "system/fvSchemes" "system/fvSolution" )

# r=2 grid triple, IDENTICAL to R1-R6.  NPOINTS = 2*(NXA+NXB)+1 -- the sampler refines with
# the mesh.
declare -A NXA=( [L1]=40  [L2]=80  [L3]=160 )
declare -A NXB=( [L1]=120 [L2]=240 [L3]=480 )
declare -A NY=(  [L1]=20  [L2]=40  [L3]=80  )
declare -A NPOINTS=( [L1]=321 [L2]=641 [L3]=1281 )

echo "=== VMFL046-R7 launcher  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)  run_root=$RUN_ROOT  endTime=$ENDTIME s  sampleDt=$SAMPLEDT s  smoke=$SMOKE"

# ---- 0. EVERY PATH THIS DRIVER REFERENCES, CHECKED TO EXIST BEFORE ANYTHING RUNS.
for p in "$CASE_DIR" "$CASE_DIR/0" "$CASE_DIR/constant" "$CASE_DIR/system" \
         "$CASE_DIR/system/blockMeshDict.template" "$CASE_DIR/system/controlDict.template" \
         "$CASE_DIR/system/fvSchemes" "$CASE_DIR/system/fvSolution" \
         "$CASE_DIR/0/T" "$CASE_DIR/0/U" "$CASE_DIR/0/p" \
         "$CASE_DIR/constant/momentumTransport" \
         "$CASE_DIR/constant/thermophysicalProperties" "$CASE_DIR/constant/turbulenceProperties" \
         "$R6_CASE_DIR" ; do
  [ -e "$p" ] || { echo "ABORT: driver references a path that does not exist: $p"; exit 2; }
done

# ---- 1. OpenFOAM environment, SOURCED BY THE DRIVER ITSELF, THEN asserted (charter sec14/sec15).
source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo "ABORT: cannot source /usr/lib/openfoam/openfoam2606/etc/bashrc"; exit 2; }
command -v blockMesh      >/dev/null || { echo "ABORT: blockMesh not on PATH after sourcing the v2606 bashrc"; exit 2; }
command -v rhoCentralFoam >/dev/null || { echo "ABORT: rhoCentralFoam not on PATH after sourcing the v2606 bashrc"; exit 2; }

# ---- 2. R6-PARITY ASSERT -- BOTH DIRECTIONS.
# DIRECTION 1: the nine carried inputs byte-identical to R6.
for rel in "${CARRIED[@]}"; do
  [ -f "$CASE_DIR/$rel" ]     || { echo "ABORT: R7 carried input missing: $rel"; exit 7; }
  [ -f "$R6_CASE_DIR/$rel" ]  || { echo "ABORT: R6 parity reference missing: $R6_CASE_DIR/$rel"; exit 7; }
  cmp -s "$CASE_DIR/$rel" "$R6_CASE_DIR/$rel" \
    || { echo "ABORT: R7 carried input $rel DIFFERS from R6 -- R7 is an IC-only change and must NOT touch the solver/outlet/mesh/thermo (PREREG sec8)"; exit 7; }
done
# DIRECTION 2: the deliberate IC change is present and is the REGISTERED one.
cmp -s "$CASE_DIR/0/U" "$R6_CASE_DIR/0/U" && { echo "ABORT: 0/U IDENTICAL to R6 -- the registered start-from-rest IC change was never made"; exit 7; }
# 0/p must be byte-identical to R6 (p=200000, lInf 0.3 preserved -- named per supervisor).
cmp -s "$CASE_DIR/0/p" "$R6_CASE_DIR/0/p" || { echo "ABORT: 0/p DIFFERS from R6 -- the smoke showed dropping p from 200000 re-destabilises the startup; 0/p must be carried byte-identical (PREREG sec3)"; exit 7; }
# The (0 0 0)/(100 0 0) checks are scoped to the internalField LINE ONLY: the boundaryField
# legitimately retains (100 0 0) as byte-identical patch `value` placeholders.
U_INT_LINE="$(grep -E '^[[:space:]]*internalField' "$CASE_DIR/0/U" | head -1)"
echo "$U_INT_LINE" | grep -qE 'uniform[[:space:]]*\(0 0 0\)' || { echo "ABORT: 0/U internalField is not the registered start-from-rest `uniform (0 0 0)` (PREREG sec3)"; exit 7; }
echo "$U_INT_LINE" | grep -qE '\(100 0 0\)' && { echo "ABORT: 0/U internalField still carries the impulsive (100 0 0) -- the start-from-rest change was not made"; exit 7; }
N_R7=$(find "$CASE_DIR" -type f | wc -l)
[ "$N_R7" = "10" ] || { echo "ABORT: R7 carries $N_R7 case inputs, expected 10 (unchanged from R6)"; exit 7; }
echo "R6-parity OK: 9 carried inputs byte-identical to R6; 0/U internalField changed to start-from-rest (0 0 0); 0/p byte-identical (p=200000, lInf 0.3); 10 files."

if [ "$SMOKE" = "1" ]; then
  case "$RUN_ROOT" in
    /tmp/*|*/scratchpad/*) : ;;
    *) echo "ABORT smoke: run_root $RUN_ROOT is not under a scratch area"; exit 3 ;;
  esac
fi

# ---- 3. rule-4 age guard, BEFORE anything is written.
for L in $LEVELS_TO_RUN; do
  if [ -d "$RUN_ROOT/$L" ] && ls -d "$RUN_ROOT/$L"/[0-9]* >/dev/null 2>&1; then
    echo "ABORT: $RUN_ROOT/$L already holds a numeric time dir (rule 4 age guard)"; exit 4
  fi
done

# ---- 4. input integrity: every case input matches its committed blob (rule 2).
if [ "$SMOKE" != "1" ]; then
  H=$(git -C "$SCRIPT_DIR" rev-parse HEAD) || { echo "ABORT: no HEAD"; exit 5; }
  while IFS= read -r f; do
    rel="cases/ansys_verification/VMFL046-R7/case/${f#$CASE_DIR/}"
    disk=$(git -C "$SCRIPT_DIR" hash-object "$f")
    blob=$(git -C "$SCRIPT_DIR" rev-parse "HEAD:$rel" 2>/dev/null)
    if [ "$disk" != "$blob" ]; then
      echo "ABORT: case input $rel does not match its HEAD blob (disk=$disk blob=${blob:-MISSING})"; exit 6
    fi
  done < <(find "$CASE_DIR" -type f | sort)
  echo "input-integrity OK: all case inputs match HEAD $H (caveat: pins to HEAD not prereg_commit; rule 6 is the backstop)"
fi

CORE_MIN_USED=0
for L in $LEVELS_TO_RUN; do
  LD="$RUN_ROOT/$L"
  mkdir -p "$LD"
  cp -r "$CASE_DIR"/* "$LD"/
  rm -f "$LD/system/blockMeshDict.template" "$LD/system/controlDict.template"
  sed "s/__NXA__/${NXA[$L]}/g; s/__NXB__/${NXB[$L]}/g; s/__NY__/${NY[$L]}/g" "$CASE_DIR/system/blockMeshDict.template" > "$LD/system/blockMeshDict"
  sed "s/__ENDTIME__/$ENDTIME/g; s/__NPOINTS__/${NPOINTS[$L]}/g; s/__SAMPLEDT__/$SAMPLEDT/g" "$CASE_DIR/system/controlDict.template" > "$LD/system/controlDict"
  grep -q "__ENDTIME__\|__NPOINTS__\|__SAMPLEDT__\|__NXA__\|__NXB__\|__NY__" "$LD/system/controlDict" "$LD/system/blockMeshDict" \
    && { echo "ABORT $L: an unsubstituted template token survived into a live dictionary"; exit 8; }
  touch "$LD/0/U" "$LD/0/p" "$LD/0/T"   # 0/ dated LAST (rule 4 age-guard reference)

  ( cd "$LD" && blockMesh ) > "$LD/log.blockMesh" 2>&1 || { echo "ABORT $L: blockMesh rc=$?"; exit 10; }

  remaining=$(awk "BEGIN{print ($CAP_CORE_MIN-$CORE_MIN_USED)}")
  lvlcap="${CAP_LEVEL[$L]}"
  budget=$(awk "BEGIN{print ($remaining < $lvlcap) ? $remaining : $lvlcap}")
  timeout_s=$(awk "BEGIN{printf \"%d\", $budget*60/$RANKS}")
  if [ "$timeout_s" -le 0 ]; then echo "ABORT $L: cap exhausted before launch (rule 12)"; exit 124; fi
  echo "  $L: budget=${budget} core-min (level cap $lvlcap, remaining total $remaining) -> timeout ${timeout_s}s"

  # rc is captured DIRECTLY from the timeout subshell (its exit status IS timeout's: 124 on
  # kill, else the solver's rc).  NO setsid (setsid-parent-returns-zero).
  t0=$(date +%s)
  ( cd "$LD" && timeout "${timeout_s}s" rhoCentralFoam ) > "$LD/log.rhoCentralFoam" 2>&1
  rc=$?
  echo "$rc" > "$LD/RUN_RC"
  t1=$(date +%s); wall=$((t1-t0))
  used=$(awk "BEGIN{print $wall*$RANKS/60}")
  CORE_MIN_USED=$(awk "BEGIN{print $CORE_MIN_USED+$used}")
  echo "  $L: rc=$rc wall=${wall}s core_min_used=$CORE_MIN_USED / cap $CAP_CORE_MIN"
  if [ "$rc" = "124" ]; then echo "ABORT $L: cap overrun stopped the run (rc 124, rule 12)"; exit 124; fi
  if [ "$rc" != "0" ]; then echo "ABORT $L: rhoCentralFoam rc=$rc"; exit 11; fi
done

echo "=== VMFL046-R7 launcher done  core_min_used=$CORE_MIN_USED  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
