#!/usr/bin/env bash
# =============================================================================
# VMFL046 graded-run driver -- Supersonic flow with a normal shock in a CD nozzle.
# Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p.155.
# Solver: rhoSimpleFoam (OpenFOAM v2606), steady compressible, laminar, 2-D half-nozzle.
#
# Frozen pre-registration: cases/ansys_verification/VMFL046/PREREGISTRATION.md
# Frozen comparator      : cases/ansys_verification/VMFL046/grade_vmfl046.py
# Frozen reference        : cases/ansys_verification/VMFL046/quasi1d_reference.py
# Run root (cwd)         : verification/runs/ansys_verification/VMFL046/  (never the case dir)
#
# Modelled on run_vmfl054_r2.sh. The driver SOURCES its own OpenFOAM env and asserts its
# tools on PATH (charter section 15: a smoke in a shell the launch never gets proves
# nothing; the driver must not depend on the caller's environment). NO `set -u`.
# THE CAP IS A RUNNING TOTAL (rule 12): an overrun STOPS the run (rc 124).
# =============================================================================

RANKS=1
CAP_CORE_MIN=30          # RUNNING TOTAL across all three solves (PREREGISTRATION sec.7)
# The run goes to endTime (residualControl removed); convergence is the M(0.9) plateau the
# comparator judges (§22.5). VMFL046_ENDTIME overrides ONLY for a CLAUSE-B one-iteration smoke
# (§20.3); the graded default is 20000 and is unchanged.
ENDTIME="${VMFL046_ENDTIME:-20000}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CASE_DIR="$SCRIPT_DIR/case"
RUN_ROOT="${1:?usage: run_vmfl046.sh <run_root> [levels...]}"
shift 2>/dev/null
LEVELS_TO_RUN="${*:-L1 L2 L3}"
SMOKE="${VMFL046_SMOKE:-0}"

# r=2 grid triple: converging / diverging axial counts and transverse count all double.
declare -A NXA=( [L1]=40  [L2]=80  [L3]=160 )
declare -A NXB=( [L1]=120 [L2]=240 [L3]=480 )
declare -A NY=(  [L1]=20  [L2]=40  [L3]=80  )

echo "=== VMFL046 launcher  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)  run_root=$RUN_ROOT  smoke=$SMOKE"

source /usr/lib/openfoam/openfoam2606/etc/bashrc || { echo "ABORT: cannot source /usr/lib/openfoam/openfoam2606/etc/bashrc"; exit 2; }
command -v blockMesh     >/dev/null || { echo "ABORT: blockMesh not on PATH after sourcing the v2606 bashrc"; exit 2; }
command -v rhoSimpleFoam >/dev/null || { echo "ABORT: rhoSimpleFoam not on PATH after sourcing the v2606 bashrc"; exit 2; }

if [ "$SMOKE" = "1" ]; then
  case "$RUN_ROOT" in
    /tmp/*|*/scratchpad/*) : ;;
    *) echo "ABORT smoke: run_root $RUN_ROOT is not under a scratch area"; exit 3 ;;
  esac
fi

for L in $LEVELS_TO_RUN; do
  if [ -d "$RUN_ROOT/$L" ] && ls -d "$RUN_ROOT/$L"/[0-9]* >/dev/null 2>&1; then
    echo "ABORT: $RUN_ROOT/$L already holds a numeric time dir (rule 4 age guard)"; exit 4
  fi
done

if [ "$SMOKE" != "1" ]; then
  H=$(git -C "$SCRIPT_DIR" rev-parse HEAD) || { echo "ABORT: no HEAD"; exit 5; }
  while IFS= read -r f; do
    rel="cases/ansys_verification/VMFL046/case/${f#$CASE_DIR/}"
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
  sed "s/__ENDTIME__/$ENDTIME/g" "$LD/system/controlDict.template" > "$LD/system/controlDict"
  touch "$LD/0/U" "$LD/0/p" "$LD/0/T"   # 0/ dated LAST (rule 4 age-guard reference)

  ( cd "$LD" && blockMesh ) > "$LD/log.blockMesh" 2>&1 || { echo "ABORT $L: blockMesh rc=$?"; exit 10; }

  remaining=$(awk "BEGIN{print ($CAP_CORE_MIN-$CORE_MIN_USED)}")
  timeout_s=$(awk "BEGIN{printf \"%d\", $remaining*60/$RANKS}")
  if [ "$timeout_s" -le 0 ]; then echo "ABORT $L: cap exhausted before launch (rule 12)"; exit 124; fi

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

echo "=== VMFL046 launcher done  core_min_used=$CORE_MIN_USED  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
