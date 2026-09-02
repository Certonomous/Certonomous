#!/usr/bin/env bash
# =============================================================================
# VMFL054 graded-run driver -- Laminar flow in a Trapezoidal Driven Cavity.
# Ansys Fluid Dynamics Verification Manual, Release 2026 R1, p.173 (VMFL054).
# Solver: simpleFoam (OpenFOAM v2606), steady laminar SIMPLEC, Re = 400, 2-D.
#
# Frozen pre-registration: cases/ansys_verification/VMFL054/PREREGISTRATION.md
# Frozen comparator      : cases/ansys_verification/VMFL054/grade_vmfl054.py
# Run root               : verification/runs/ansys_verification/VMFL054/  (created
#                          by the queue runner / caller; cwd = run root, never the
#                          case dir -- CHARTER Amendment 1.4 / §11.4).
#
# Modelled on cases/ansys_verification/VMFL063/run_vmfl063.sh, leaner: this is a
# THREE-level r=2 Roache triple (L1/L2/L3), no determinism twin. Named departures
# from the reference driver, so neither reads as a slip:
#   (a) gate quantity is a probe (u_x at the cavity centre), not a wall functional;
#   (b) THREE levels, not four -- no L1D twin this round (a DRAFT; the supervisor
#       may add one before freeze).
#
# NO `set -u` (incompatible with OpenFOAM v2606 etc/bashrc, PREREG_TEMPLATE Am.3).
# `set -e` does not gate reliably here; EVERY check gates EXPLICITLY.
#
# THE CAP IS A RUNNING TOTAL (CLAUDE.md rule 12): an overrun STOPS the run (rc 124);
# endTime is NEVER silently reduced to fit the cap.
# =============================================================================

RANKS=1
CAP_CORE_MIN=40          # RUNNING TOTAL across all three solves (PREREGISTRATION sec.7)
ENDTIME=50000            # iteration ceiling; residualControl stops it earlier

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CASE_DIR="$SCRIPT_DIR/case"
RUN_ROOT="${1:?usage: run_vmfl054.sh <run_root> [levels...]}"
shift 2>/dev/null
LEVELS_TO_RUN="${*:-L1 L2 L3}"
SMOKE="${VMFL054_SMOKE:-0}"

# r=2 grid triple: every level doubles BOTH counts (frozen prereg sec.4).
declare -A NX=( [L1]=40 [L2]=80  [L3]=160 )
declare -A NY=( [L1]=40 [L2]=80  [L3]=160 )

echo "=== VMFL054 launcher  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)  run_root=$RUN_ROOT  smoke=$SMOKE"

# --- smoke mode: refuse any root that is not under a scratch area, so a smoke can
#     never leave an answer where a graded run would look (rule 4 age guard). Smoke
#     ALSO skips the HEAD-blob freeze check, because a smoke runs pre-freeze. -------
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

# --- input-integrity / freeze check (skipped in smoke): every case input must be
#     byte-identical to its blob at HEAD, so the files that run ARE the files that
#     were frozen. Active once the supervisor has committed the frozen package. ----
if [ "$SMOKE" != "1" ]; then
  H=$(git -C "$SCRIPT_DIR" rev-parse HEAD) || { echo "ABORT: no HEAD"; exit 5; }
  while IFS= read -r f; do
    rel="cases/ansys_verification/VMFL054/case/${f#$CASE_DIR/}"
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
  # 0/ is touched LAST so it dates the run (rule 4 age guard reference).
  touch "$LD/0/U" "$LD/0/p"

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

echo "=== VMFL054 launcher done  core_min_used=$CORE_MIN_USED  utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
