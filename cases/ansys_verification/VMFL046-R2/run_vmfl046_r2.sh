#!/usr/bin/env bash
# =============================================================================
# VMFL046-R2 graded-run driver.
# Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p.155 (VMFL046).
# Solver: rhoSimpleFoam (OpenFOAM v2606), steady compressible, laminar, 2-D half-nozzle.
# NUMERICS ARE BYTE-IDENTICAL TO R1 -- see the R1-PARITY ASSERT below.  R2 changes the
# INSTRUMENT (refining sampler) and the CLOCK (endTime), and nothing else.
#
# Frozen pre-registration: cases/ansys_verification/VMFL046-R2/PREREGISTRATION.md
# Frozen comparator      : cases/ansys_verification/VMFL046-R2/grade_vmfl046_r2.py
# Frozen reference        : cases/ansys_verification/VMFL046/quasi1d_reference.py  (R1, unchanged)
# Run root (cwd)         : verification/runs/ansys_verification/VMFL046-R2/  (never the case dir)
#
# The driver SOURCES its own OpenFOAM env and asserts its tools on PATH (charter §14/§15:
# a smoke in a shell the launch never gets proves nothing).  NO `set -u`.
# THE CAP IS ENFORCED TWICE (rule 12, charter §26.2): a PER-LEVEL cap and a RUNNING TOTAL.
# An overrun STOPS the run (rc 124); it does not get a new budget.
# =============================================================================

RANKS=1

# --- COST (PREREGISTRATION §8).  Basis: R1's MEASURED per-level actuals at endTime 20000
# (0.94 / 5.11 / 21.89 core-min), scaled linearly in iterations by the R2 endTime factor 3,
# plus a stated 10 % instrumentation allowance for the refined sampler (3.2x the points at
# L3 and 3x the sample writes).  Caps are ~3x per charter §26.2.
CAP_CORE_MIN=276                 # RUNNING TOTAL across all three solves
declare -A CAP_LEVEL=( [L1]=9.3 [L2]=50.6 [L3]=216.7 )   # ~3x each level's own estimate

# endTime is 3x R1's, a ROUND MULTIPLIER CHOSEN FOR GENEROSITY (charter §16.2: an endTime
# generous enough that the CRITERION, not the clock, decides).  It is NOT read off any
# measured settling iteration -- no data beyond iteration 20000 exists at any level.
# VMFL046R2_ENDTIME overrides ONLY for a CLAUSE-B one-iteration smoke; the graded default
# is 60000 and is unchanged.
ENDTIME="${VMFL046R2_ENDTIME:-60000}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
CASE_DIR="$SCRIPT_DIR/case"
R1_CASE_DIR="$REPO_ROOT/cases/ansys_verification/VMFL046/case"
RUN_ROOT="${1:?usage: run_vmfl046_r2.sh <run_root> [levels...]}"
shift 2>/dev/null
LEVELS_TO_RUN="${*:-L1 L2 L3}"
SMOKE="${VMFL046R2_SMOKE:-0}"
# The GRADED sampling interval is 500 and the frozen comparator refuses any other value
# (grade_vmfl046_r2.py SAMPLE_INTERVAL).  It is overridable ONLY under a CLAUSE-B smoke, so
# that one iteration can prove the refined sampler really writes nPoints rows (charter §39.5).
SAMPLEINT=500
if [ "$SMOKE" = "1" ] && [ -n "$VMFL046R2_SAMPLEINT" ]; then SAMPLEINT="$VMFL046R2_SAMPLEINT"; fi

# r=2 grid triple, IDENTICAL to R1: converging / diverging axial counts and transverse count
# all double.  NPOINTS = 2*(NXA+NXB)+1 -- the sampler refines with the mesh (defect 1).
declare -A NXA=( [L1]=40  [L2]=80  [L3]=160 )
declare -A NXB=( [L1]=120 [L2]=240 [L3]=480 )
declare -A NY=(  [L1]=20  [L2]=40  [L3]=80  )
declare -A NPOINTS=( [L1]=321 [L2]=641 [L3]=1281 )

echo "=== VMFL046-R2 launcher  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)  run_root=$RUN_ROOT  endTime=$ENDTIME  smoke=$SMOKE"

# ---- 0. every path this driver references EXISTS (charter §39.5, applied to the launcher:
#         `bash -n` checks syntax and never checks path existence).
for p in "$CASE_DIR" "$CASE_DIR/0" "$CASE_DIR/constant" "$CASE_DIR/system" \
         "$CASE_DIR/system/blockMeshDict.template" "$CASE_DIR/system/controlDict.template" \
         "$CASE_DIR/system/fvSchemes" "$CASE_DIR/system/fvSolution" \
         "$CASE_DIR/0/T" "$CASE_DIR/0/U" "$CASE_DIR/0/p" \
         "$CASE_DIR/constant/fvOptions" "$CASE_DIR/constant/momentumTransport" \
         "$CASE_DIR/constant/thermophysicalProperties" "$CASE_DIR/constant/turbulenceProperties" \
         "$R1_CASE_DIR" ; do
  [ -e "$p" ] || { echo "ABORT: driver references a path that does not exist: $p"; exit 2; }
done

# ---- 1. OpenFOAM environment, sourced by the driver itself (charter §14/§15).
source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo "ABORT: cannot source /usr/lib/openfoam/openfoam2606/etc/bashrc"; exit 2; }
command -v blockMesh     >/dev/null || { echo "ABORT: blockMesh not on PATH after sourcing the v2606 bashrc"; exit 2; }
command -v rhoSimpleFoam >/dev/null || { echo "ABORT: rhoSimpleFoam not on PATH after sourcing the v2606 bashrc"; exit 2; }

# ---- 2. R1-PARITY ASSERT: the numerics are UNCHANGED.  Every case input except
#         system/controlDict.template must be BYTE-IDENTICAL to R1's.  This is the
#         mechanical proof of the R2 experimental design (instrument-only repair), and it
#         fails loudly if anyone edits a scheme, a BC or the mesh template.
PARITY_FILES="0/T 0/U 0/p constant/fvOptions constant/momentumTransport constant/thermophysicalProperties constant/turbulenceProperties system/blockMeshDict.template system/fvSchemes system/fvSolution"
for rel in $PARITY_FILES; do
  [ -f "$R1_CASE_DIR/$rel" ] || { echo "ABORT: R1 parity reference missing: $R1_CASE_DIR/$rel"; exit 7; }
  a=$(cmp -s "$CASE_DIR/$rel" "$R1_CASE_DIR/$rel" && echo same || echo differ)
  [ "$a" = "same" ] || { echo "ABORT: R2 case input $rel DIFFERS from R1 -- the numerics-unchanged claim in PREREGISTRATION §6 is false"; exit 7; }
done
echo "R1-parity OK: all 10 numerics inputs byte-identical to cases/ansys_verification/VMFL046/case/"

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
    rel="cases/ansys_verification/VMFL046-R2/case/${f#$CASE_DIR/}"
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
  sed "s/__NXA__/${NXA[$L]}/g; s/__NXB__/${NXB[$L]}/g; s/__NY__/${NY[$L]}/g" "$LD/system/blockMeshDict.template" > "$LD/system/blockMeshDict"
  sed "s/__ENDTIME__/$ENDTIME/g; s/__NPOINTS__/${NPOINTS[$L]}/g; s/__SAMPLEINT__/$SAMPLEINT/g" "$LD/system/controlDict.template" > "$LD/system/controlDict"
  grep -q "__ENDTIME__\|__NPOINTS__\|__SAMPLEINT__\|__NXA__\|__NXB__\|__NY__" "$LD/system/controlDict" "$LD/system/blockMeshDict" \
    && { echo "ABORT $L: an unsubstituted template token survived into a live dictionary"; exit 8; }
  touch "$LD/0/U" "$LD/0/p" "$LD/0/T"   # 0/ dated LAST (rule 4 age-guard reference)

  ( cd "$LD" && blockMesh ) > "$LD/log.blockMesh" 2>&1 || { echo "ABORT $L: blockMesh rc=$?"; exit 10; }

  remaining=$(awk "BEGIN{print ($CAP_CORE_MIN-$CORE_MIN_USED)}")
  lvlcap="${CAP_LEVEL[$L]}"
  budget=$(awk "BEGIN{print ($remaining < $lvlcap) ? $remaining : $lvlcap}")
  timeout_s=$(awk "BEGIN{printf \"%d\", $budget*60/$RANKS}")
  if [ "$timeout_s" -le 0 ]; then echo "ABORT $L: cap exhausted before launch (rule 12)"; exit 124; fi
  echo "  $L: budget=${budget} core-min (level cap $lvlcap, remaining total $remaining) -> timeout ${timeout_s}s"

  t0=$(date +%s)
  ( cd "$LD" && timeout "${timeout_s}s" rhoSimpleFoam ) > "$LD/log.rhoSimpleFoam" 2>&1
  rc=$?
  echo "$rc" > "$LD/RUN_RC"
  t1=$(date +%s); wall=$((t1-t0))
  used=$(awk "BEGIN{print $wall*$RANKS/60}")
  CORE_MIN_USED=$(awk "BEGIN{print $CORE_MIN_USED+$used}")
  echo "  $L: rc=$rc wall=${wall}s core_min_used=$CORE_MIN_USED / cap $CAP_CORE_MIN"
  if [ "$rc" = "124" ]; then echo "ABORT $L: cap overrun stopped the run (rc 124, rule 12)"; exit 124; fi
  if [ "$rc" != "0" ]; then echo "ABORT $L: rhoSimpleFoam rc=$rc"; exit 11; fi
done

echo "=== VMFL046-R2 launcher done  core_min_used=$CORE_MIN_USED  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
