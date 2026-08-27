#!/usr/bin/env bash
# F26D -- launch the Ringleb DISCRIMINATING ARM. Registered by
# PREREGISTRATION_F26D_2026-08-27.md. DIAGNOSTIC, NOT A LADDER: nothing here is an
# F26 ladder level, and no outcome rescopes or unblocks F26_RINGLEB.
#
# 3 arms x 4 levels, all SERIAL (1 rank); decomposePar is never invoked.
# One change per run (Sanaa section 3): AV differs from A0 only in mu, AM only in
# the streamline band. build_f26d.py enforces that -- this script chooses nothing.
#
# `set -e` is NOT relied on anywhere: every rc is captured and tested explicitly
# (L-314). `set -u` is off around the OpenFOAM bashrc, which reads unbound
# variables (L-339).
set -o pipefail

ROOT=/home/ubuntu/Certonomous
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_ROOT="$ROOT/verification/runs/F26D_runs"
FOAM_BASHRC=/usr/lib/openfoam/openfoam2606/etc/bashrc
CAP_CORE_MIN=10.2            # pre-registration section 6; NEVER raised
ARMS="A0 AV AM"
LEVELS="L1 L2 L3 L4"
PREREG_COMMIT=""

for a in "$@"; do
  case "$a" in
    --prereg-commit=*) PREREG_COMMIT="${a#*=}" ;;
    *) echo "usage: run_f26d.sh --prereg-commit=<sha>" >&2; exit 1 ;;
  esac
done
if [ -z "$PREREG_COMMIT" ]; then
  echo "REFUSED: --prereg-commit=<sha> is required; the grading path is fixed at the freeze." >&2
  exit 1
fi

# Rule 2: the frozen document that governs this run must BE the committed blob.
if ! python3 "$HERE/grade_f26d.py" --prereg-commit="$PREREG_COMMIT" --run-root=/nonexistent >/dev/null 2>&1; then
  if ! git -C "$ROOT" rev-parse "$PREREG_COMMIT:cases/F26_RINGLEB/PREREGISTRATION_F26D_2026-08-27.md" >/dev/null 2>&1; then
    echo "REFUSED: $PREREG_COMMIT does not carry the pre-registration blob." >&2
    exit 2
  fi
fi

# Absence condition (pre-registration section 8). REFUSE, never delete.
if [ -e "$RUN_ROOT" ]; then
  if find "$RUN_ROOT" -maxdepth 3 \( -name "processor*" -o -regex '.*/[0-9]+\(\.[0-9]+\)?' \) | grep -q .; then
    echo "REFUSED: $RUN_ROOT already holds a time or processor directory. Not deleted (rule 4)." >&2
    exit 2
  fi
fi
mkdir -p "$RUN_ROOT" || exit 1
date -u +"%Y-%m-%dT%H:%M:%SZ" > "$RUN_ROOT/LAUNCH_UTC.txt"
echo "$PREREG_COMMIT" > "$RUN_ROOT/PREREG_COMMIT.txt"

SPENT=0
for ARM in $ARMS; do
  for LV in $LEVELS; do
    D="$RUN_ROOT/$ARM/$LV"
    # Cap is PROJECTED before the level and CHECKED after it. A crossing halts;
    # unrun levels are simply absent and the grader reads them as such.
    OVER=$(python3 -c "print(1 if $SPENT >= $CAP_CORE_MIN else 0)")
    if [ "$OVER" = "1" ]; then
      echo "CAP REACHED: $SPENT core-min >= $CAP_CORE_MIN. HALTING; $ARM/$LV and later are unrun." \
        | tee -a "$RUN_ROOT/CAP.txt"
      exit 3
    fi
    mkdir -p "$D" || exit 1
    if ! python3 "$HERE/build_f26d.py" "$D/case" --arm "$ARM" --level "$LV" > "$D/log.build" 2>&1; then
      echo "BUILD FAILED for $ARM/$LV (see $D/log.build). Reported, not hidden." | tee -a "$RUN_ROOT/BUILD_FAILURES.txt"
      echo "build-failed" > "$D/RC.txt"
      continue
    fi
    bash -c ". $FOAM_BASHRC > /dev/null 2>&1; rhoSimpleFoam -case '$D/case' > '$D/log.solve' 2>&1"
    RC=$?
    echo "$RC" > "$D/RC.txt"
    CT=$(grep -oE 'ClockTime = [0-9]+' "$D/log.solve" | tail -1 | grep -oE '[0-9]+$')
    [ -z "$CT" ] && CT=0
    SPENT=$(python3 -c "print(round($SPENT + $CT/60.0, 4))")
    echo "$ARM $LV rc=$RC ClockTime=${CT}s cumulative=${SPENT} core-min" | tee -a "$RUN_ROOT/PROGRESS.txt"
  done
done
echo "$SPENT" > "$RUN_ROOT/SPENT_CORE_MIN.txt"
echo "F26D complete: $SPENT core-min against a cap of $CAP_CORE_MIN. Grade with grade_f26d.py."
exit 0
