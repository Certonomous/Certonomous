#!/usr/bin/env bash
# =============================================================================
# VMFL054-R3 graded-run driver -- Laminar flow in a Trapezoidal Driven Cavity.
# Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p.173 (VMFL054).
# Solver: simpleFoam (OpenFOAM v2606), steady laminar SIMPLEC, Re = 400, 2-D.
#
# WHY R3 (the ONLY change from R2): R2 graded the r=2 triple L1/L2/L3 = 40/80/160
# and landed a monotone CONVERGING triple with observed order p = 3.438 -- ABOVE the
# frozen ceiling 3.0 (register #53, GATE FAIL, PREDICTED in the freeze). A 3-point
# estimate cannot distinguish genuine super-2nd-order convergence from a PRE-ASYMPTOTIC
# artefact. R3 ADDS A FOURTH, FINER LEVEL L4 = 320x320 (r=2) so the order can be read
# on the FINEST triple L2/L3/L4 (closer to the asymptotic range) with a 4-point
# diagnostic. NOTHING ELSE CHANGES: the comparator's gate constants, the case inputs and
# both R1/R2 rulings are byte-identical to R2's frozen package; only the driver's level
# set and the running-total cap change (the extra level costs more).
#
# NO `set -u` (incompatible with OpenFOAM v2606 etc/bashrc, PREREG_TEMPLATE Am.3).
# THE CAP IS A RUNNING TOTAL (CLAUDE.md rule 12): an overrun STOPS the run (rc 124).
# =============================================================================

RANKS=1
CAP_CORE_MIN=60          # RUNNING TOTAL across all FOUR solves (PREREGISTRATION sec.7);
                         # est. ~13.5 core-min; cap generous -- an overrun STOPS the run.
ENDTIME=50000            # iteration ceiling; residualControl stops it earlier

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CASE_DIR="$SCRIPT_DIR/case"
RUN_ROOT="${1:?usage: run_vmfl054_r3.sh <run_root> [levels...]}"
shift 2>/dev/null
LEVELS_TO_RUN="${*:-L1 L2 L3 L4}"
SMOKE="${VMFL054_R3_SMOKE:-0}"

declare -A NX=( [L1]=40 [L2]=80  [L3]=160 [L4]=320 )
declare -A NY=( [L1]=40 [L2]=80  [L3]=160 [L4]=320 )

echo "=== VMFL054-R3 launcher  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)  run_root=$RUN_ROOT  smoke=$SMOKE"

# --- OpenFOAM environment: source it and assert the solver is on PATH, UNCONDITIONALLY,
#     so the driver works under the bare daemon shell and under a manual smoke alike.
#     (This is the R2 fix carried forward; R1 dropped exactly these lines.) ------------
source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo "ABORT: cannot source /usr/lib/openfoam/openfoam2606/etc/bashrc"; exit 2; }
command -v blockMesh  >/dev/null || { echo "ABORT: blockMesh not on PATH after sourcing the v2606 bashrc"; exit 2; }
command -v simpleFoam >/dev/null || { echo "ABORT: simpleFoam not on PATH after sourcing the v2606 bashrc"; exit 2; }

# --- smoke mode: refuse any root not under a scratch area; skip the HEAD-blob check. -
if [ "$SMOKE" = "1" ]; then
  case "$RUN_ROOT" in
    /tmp/*|*/scratchpad/*) : ;;
    *) echo "ABORT smoke: run_root $RUN_ROOT is not under a scratch area"; exit 3 ;;
  esac
fi

# --- age guard (rule 4): refuse a run root that already holds an answer ----------
for L in $LEVELS_TO_RUN; do
  if [ -d "$RUN_ROOT/$L" ] && ls -d "$RUN_ROOT/$L"/[0-9]* >/dev/null 2>&1; then
    echo "ABORT: $RUN_ROOT/$L already holds a numeric time dir (rule 4 age guard)"; exit 4
  fi
done

# --- input-integrity / freeze check (skipped in smoke): every case input byte-identical
#     to its blob at HEAD. (Caveat carried from R1/R2: this pins to HEAD, not to the
#     prereg_commit -- rule 6 is the backstop; a future hardening should pin to the sha.) -
if [ "$SMOKE" != "1" ]; then
  H=$(git -C "$SCRIPT_DIR" rev-parse HEAD) || { echo "ABORT: no HEAD"; exit 5; }
  while IFS= read -r f; do
    rel="cases/ansys_verification/VMFL054-R3/case/${f#$CASE_DIR/}"
    disk=$(git -C "$SCRIPT_DIR" hash-object "$f")
    blob=$(git -C "$SCRIPT_DIR" rev-parse "HEAD:$rel" 2>/dev/null)
    if [ "$disk" != "$blob" ]; then
      echo "ABORT: case input $rel does not match its HEAD blob (disk=$disk blob=${blob:-MISSING})"; exit 6
    fi
  done < <(find "$CASE_DIR" -type f | sort)
  echo "input-integrity OK: all case inputs match HEAD $H"
fi

CORE_MIN_USED=0
for L in $LEVELS_TO_RUN; do
  LD="$RUN_ROOT/$L"
  mkdir -p "$LD"
  cp -r "$CASE_DIR"/* "$LD"/
  sed "s/__NX__/${NX[$L]}/g; s/__NY__/${NY[$L]}/g" "$LD/system/blockMeshDict.template" > "$LD/system/blockMeshDict"
  sed "s/__ENDTIME__/$ENDTIME/g" "$LD/system/controlDict.template" > "$LD/system/controlDict"
  touch "$LD/0/U" "$LD/0/p"   # 0/ dated LAST at launch (rule 4 age-guard reference)

  ( cd "$LD" && blockMesh ) > "$LD/log.blockMesh" 2>&1 || { echo "ABORT $L: blockMesh rc=$?"; exit 10; }

  remaining=$(awk "BEGIN{print ($CAP_CORE_MIN-$CORE_MIN_USED)}")
  timeout_s=$(awk "BEGIN{printf \"%d\", $remaining*60/$RANKS}")
  if [ "$timeout_s" -le 0 ]; then echo "ABORT $L: cap exhausted before launch (rule 12)"; exit 124; fi

  t0=$(date +%s)
  ( cd "$LD" && timeout "${timeout_s}s" simpleFoam ) > "$LD/log.simpleFoam" 2>&1
  rc=$?
  echo "$rc" > "$LD/RUN_RC"   # solver rc persisted for the comparator's rule-4 rc limb
  t1=$(date +%s)
  wall=$((t1-t0))
  used=$(awk "BEGIN{print $wall*$RANKS/60}")
  CORE_MIN_USED=$(awk "BEGIN{print $CORE_MIN_USED+$used}")
  echo "  $L: rc=$rc wall=${wall}s core_min_used=$CORE_MIN_USED / cap $CAP_CORE_MIN"
  if [ "$rc" = "124" ]; then echo "ABORT $L: cap overrun stopped the run (rc 124, rule 12)"; exit 124; fi
  if [ "$rc" != "0" ]; then echo "ABORT $L: simpleFoam rc=$rc"; exit 11; fi
done

echo "=== VMFL054-R3 launcher done  core_min_used=$CORE_MIN_USED  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
