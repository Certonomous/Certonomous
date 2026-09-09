#!/usr/bin/env bash
# =============================================================================
# VMFL046-R8 graded-run driver.
# Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p.155 (VMFL046).
#
# Solver: rhoPimpleFoam (OpenFOAM v2606) -- PRESSURE-BASED, TRANSIENT, PIMPLE segregated
# pressure-velocity-energy coupling.  2-D half-nozzle, laminar.
#
# R8 IS THE SOLVER-CHOICE SUCCESSOR TO R7 (register row #70, NOT A RESULT).  R6/R7's density-
# based rhoCentralFoam core-dumped in the transonic startup ("Negative initial temperature")
# -- a solver-specific numerics artifact of the explicit, UNBOUNDED face-reconstruction e->T
# inversion, NOT a capability limit.  An answer-blind smoke (verification/runs/ansys_verification/
# VMFL046-R8/SMOKE_rhoPimple_L1) showed rhoPimpleFoam CLEARS the ~0.028-0.032 s onset (min-T
# 224 K, positive) AND holds through the graded window to 0.08 s (rc 0, End); the lab's own R5
# already ran rhoPimpleFoam to End at all three levels.
#
# R8 IS TWO DELIBERATE CHANGES vs R7 AND NOTHING ELSE:
#   SOLVER + NUMERICS  application rhoCentralFoam -> rhoPimpleFoam, with R5's documented,
#     measurement-forced pressure-based numerics: system/fvSchemes (vanLeer TVD / Euler),
#     system/fvSolution (PIMPLE nOuter 3 / relax 0.7 / maxCo 0.5), constant/fvOptions
#     limitTemperature [150,2000] (a transient stabilizer rhoPimpleFoam HONORS; a no-op in
#     rhoCentralFoam).  controlDict.template carries application rhoPimpleFoam and maxCo 0.5.
#   PHYSICAL CASE carried from R7 BYTE-IDENTICAL: mesh (blockMeshDict.template), start-from-rest
#     0/U, 0/p (waveTransmissive lInf 0.3 -- R6's washout repair), 0/T, and the thermo.
# The GATE (x_shock vs 1.250 m, +-5 %), DELTA_X, endTime, the r=2 triple and every gate limb
# of the comparator are carried from R1-R7 UNCHANGED (L-487).
#
# THE DRIVER CARRIES A BOTH-DIRECTIONS PARITY ASSERT AND REFUSES TO LAUNCH (exit 7) IF VIOLATED:
#   DIRECTION 1  the SEVEN physical inputs carried from R7 byte-identical (0/T, 0/U, 0/p,
#                constant/momentumTransport, constant/thermophysicalProperties,
#                constant/turbulenceProperties, system/blockMeshDict.template).
#   DIRECTION 2  the deliberate solver change is present AND is the registered one:
#                  - system/fvSchemes and system/fvSolution byte-identical to R5's;
#                  - constant/fvOptions byte-identical to R5's (limitTemperature [150,2000]);
#                  - controlDict.template carries `application rhoPimpleFoam` and `maxCo 0.5`.
#
# Frozen pre-registration: cases/ansys_verification/VMFL046-R8/PREREGISTRATION.md
# Frozen comparator      : cases/ansys_verification/VMFL046-R8/grade_vmfl046_r8.py
# Frozen reference       : cases/ansys_verification/VMFL046/quasi1d_reference.py (R1, unchanged)
# Run root (cwd)         : verification/runs/ansys_verification/VMFL046-R8/ (never the case dir)
#
# THE DRIVER SOURCES ITS OWN OpenFOAM ENVIRONMENT AND ONLY THEN ASSERTS ITS TOOLS ON PATH.
# NO `set -u`.  THE CAP IS A RUNNING TOTAL AND A PER-LEVEL CAP (rule 12): an overrun STOPS the
# run (rc 124); it does not get a new budget.
# =============================================================================

RANKS=1

# --- COST (PREREGISTRATION sec7).  BASIS IS MEASURED (rhoPimpleFoam):
#   R5 ran rhoPimpleFoam to End at all three levels -- L1 3.1 / L2 22.6 / L3 171.583 core-min
#   (verification/runs/ansys_verification/VMFL046-R5/launcher.queue.out).  R8 uses the
#   start-from-rest IC (R7's), which the L1 answer-blind smoke measured at 7.68 core-min
#   (SMOKE_rhoPimple_L1, WITH box contention) -- ~2.5x R5's impulsive-IC L1.  R8 point estimate
#   applies a start-from-rest factor ~2.0 to R5's L2/L3: L1 ~7.7 / L2 ~45 / L3 ~345 core-min.
#   Per-level caps are ~3x the estimate; the running total is their sum.  The est-vs-actual
#   calibration is OWED at R8 completion (rule 12).
CAP_CORE_MIN=1200                # RUNNING TOTAL (~3x the ~398 core-min point estimate)
declare -A CAP_LEVEL=( [L1]=24 [L2]=140 [L3]=1040 )   # ~3x 7.7 / 45 / 345

# endTime is PHYSICAL SECONDS and is R7's (== R1-R7), UNCHANGED: 0.080 s.
# VMFL046R8_ENDTIME overrides ONLY for a CLAUSE-B smoke; the frozen comparator REFUSES any
# level whose controlDict does not carry the graded value.
ENDTIME="${VMFL046R8_ENDTIME:-0.080}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CASE_DIR="$SCRIPT_DIR/case"
R7_CASE_DIR="$REPO_ROOT/cases/ansys_verification/VMFL046-R7/case"
R5_CASE_DIR="$REPO_ROOT/cases/ansys_verification/VMFL046-R5/case"
RUN_ROOT="${1:?usage: run_vmfl046_r8.sh <run_root> [levels...]}"
shift 2>/dev/null
LEVELS_TO_RUN="${*:-L1 L2 L3}"
SMOKE="${VMFL046R8_SMOKE:-0}"

SAMPLEDT=5.0e-04
if [ "$SMOKE" = "1" ] && [ -n "$VMFL046R8_SAMPLEDT" ]; then SAMPLEDT="$VMFL046R8_SAMPLEDT"; fi

# SEVEN physical inputs carried from R7 BYTE-IDENTICAL.
CARRIED_R7=( "0/T" "0/U" "0/p" "constant/momentumTransport" \
             "constant/thermophysicalProperties" "constant/turbulenceProperties" \
             "system/blockMeshDict.template" )
# THREE numerics inputs carried from R5 BYTE-IDENTICAL (the deliberate solver change).
CARRIED_R5=( "system/fvSchemes" "system/fvSolution" "constant/fvOptions" )

# r=2 grid triple, IDENTICAL to R1-R7.  NPOINTS = 2*(NXA+NXB)+1.
declare -A NXA=( [L1]=40  [L2]=80  [L3]=160 )
declare -A NXB=( [L1]=120 [L2]=240 [L3]=480 )
declare -A NY=(  [L1]=20  [L2]=40  [L3]=80  )
declare -A NPOINTS=( [L1]=321 [L2]=641 [L3]=1281 )

echo "=== VMFL046-R8 launcher  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)  run_root=$RUN_ROOT  endTime=$ENDTIME s  sampleDt=$SAMPLEDT s  smoke=$SMOKE"

# ---- 0. every path this driver references, checked to exist.
for p in "$CASE_DIR" "$CASE_DIR/0" "$CASE_DIR/constant" "$CASE_DIR/system" \
         "$CASE_DIR/system/blockMeshDict.template" "$CASE_DIR/system/controlDict.template" \
         "$CASE_DIR/system/fvSchemes" "$CASE_DIR/system/fvSolution" \
         "$CASE_DIR/constant/fvOptions" \
         "$CASE_DIR/0/T" "$CASE_DIR/0/U" "$CASE_DIR/0/p" \
         "$CASE_DIR/constant/momentumTransport" \
         "$CASE_DIR/constant/thermophysicalProperties" "$CASE_DIR/constant/turbulenceProperties" \
         "$R7_CASE_DIR" "$R5_CASE_DIR" ; do
  [ -e "$p" ] || { echo "ABORT: driver references a path that does not exist: $p"; exit 2; }
done

# ---- 1. OpenFOAM environment, sourced by the driver, then asserted.
source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo "ABORT: cannot source /usr/lib/openfoam/openfoam2606/etc/bashrc"; exit 2; }
command -v blockMesh     >/dev/null || { echo "ABORT: blockMesh not on PATH after sourcing the v2606 bashrc"; exit 2; }
command -v rhoPimpleFoam >/dev/null || { echo "ABORT: rhoPimpleFoam not on PATH after sourcing the v2606 bashrc"; exit 2; }

# ---- 2. R8 PARITY ASSERT -- BOTH DIRECTIONS.
# DIRECTION 1: the seven physical inputs byte-identical to R7.
for rel in "${CARRIED_R7[@]}"; do
  [ -f "$CASE_DIR/$rel" ]    || { echo "ABORT: R8 carried physical input missing: $rel"; exit 7; }
  [ -f "$R7_CASE_DIR/$rel" ] || { echo "ABORT: R7 parity reference missing: $R7_CASE_DIR/$rel"; exit 7; }
  cmp -s "$CASE_DIR/$rel" "$R7_CASE_DIR/$rel" \
    || { echo "ABORT: R8 physical input $rel DIFFERS from R7 -- R8 carries the physical case byte-identical and changes only the solver/numerics (PREREG sec8)"; exit 7; }
done
# DIRECTION 2: the deliberate solver change is present AND is the registered R5 numerics.
for rel in "${CARRIED_R5[@]}"; do
  [ -f "$CASE_DIR/$rel" ]    || { echo "ABORT: R8 numerics input missing: $rel"; exit 7; }
  [ -f "$R5_CASE_DIR/$rel" ] || { echo "ABORT: R5 numerics reference missing: $R5_CASE_DIR/$rel"; exit 7; }
  cmp -s "$CASE_DIR/$rel" "$R5_CASE_DIR/$rel" \
    || { echo "ABORT: R8 numerics input $rel DIFFERS from R5 -- R8's pressure-based numerics must be R5's documented set (PREREG sec2)"; exit 7; }
done
# fvSchemes must DIFFER from R7's (the density-based reconstruct schemes) -- the change is real.
cmp -s "$CASE_DIR/system/fvSchemes" "$R7_CASE_DIR/system/fvSchemes" 2>/dev/null && { echo "ABORT: system/fvSchemes IDENTICAL to R7 -- the registered solver change was never made"; exit 7; }
# controlDict.template carries the registered solver + Courant.
grep -qE '^\s*application\s+rhoPimpleFoam\s*;' "$CASE_DIR/system/controlDict.template" || { echo "ABORT: controlDict.template does not carry application rhoPimpleFoam (PREREG sec6)"; exit 7; }
grep -qE '^\s*maxCo\s+0\.5\s*;' "$CASE_DIR/system/controlDict.template" || { echo "ABORT: controlDict.template does not carry maxCo 0.5 (PREREG sec6)"; exit 7; }
grep -qE 'type\s+limitTemperature' "$CASE_DIR/constant/fvOptions" || { echo "ABORT: constant/fvOptions carries no limitTemperature (PREREG sec2/LIMB b)"; exit 7; }
N_R8=$(find "$CASE_DIR" -type f | wc -l)
[ "$N_R8" = "11" ] || { echo "ABORT: R8 carries $N_R8 case inputs, expected 11"; exit 7; }
echo "R8-parity OK: 7 physical inputs byte-identical to R7; fvSchemes/fvSolution/fvOptions byte-identical to R5; controlDict rhoPimpleFoam/maxCo 0.5; 11 files."

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
    rel="cases/ansys_verification/VMFL046-R8/case/${f#$CASE_DIR/}"
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

  # rc captured DIRECTLY from the timeout subshell (its exit status IS timeout's: 124 on kill,
  # else the solver's rc).  NO setsid (setsid-parent-returns-zero).
  t0=$(date +%s)
  ( cd "$LD" && timeout "${timeout_s}s" rhoPimpleFoam ) > "$LD/log.rhoPimpleFoam" 2>&1
  rc=$?
  echo "$rc" > "$LD/RUN_RC"
  t1=$(date +%s); wall=$((t1-t0))
  used=$(awk "BEGIN{print $wall*$RANKS/60}")
  CORE_MIN_USED=$(awk "BEGIN{print $CORE_MIN_USED+$used}")
  echo "  $L: rc=$rc wall=${wall}s core_min_used=$CORE_MIN_USED / cap $CAP_CORE_MIN"
  if [ "$rc" = "124" ]; then echo "ABORT $L: cap overrun stopped the run (rc 124, rule 12)"; exit 124; fi
  if [ "$rc" != "0" ]; then echo "ABORT $L: rhoPimpleFoam rc=$rc"; exit 11; fi
done

echo "=== VMFL046-R8 launcher done  core_min_used=$CORE_MIN_USED  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
