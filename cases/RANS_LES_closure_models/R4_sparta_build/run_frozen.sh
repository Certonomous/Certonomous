#!/bin/bash
# R4 step 1 - run the 27 k-corrective-frozen-RANS extractions.
#
# Each case is a serial kCorrectiveFrozenFoam solve (no decomposition: the
# solver writes once, at its own settle iteration) followed by
# `postProcess -func 'grad(U)'` on that directory, so the regression uses the
# SAME discrete gradient the frozen solve used (W2 regression convention 1).
#
# rc is recorded to <case>/rc for the STRICT COMPLETION RULE.  Completed cases
# are SKIPPED, never rerun: `run_frozen.sh --force` overrides.
set -u
ROOT=/home/ubuntu/closure-data/r4/frozen
HERE=$(dirname "$(readlink -f "$0")")
PY=/home/ubuntu/closure-venv/bin/python
JOBS=${JOBS:-8}
FORCE=${1:-}

one() {
  local C="$1" D="$ROOT/$1"
  if [ "$FORCE" != "--force" ]; then
    if $PY -c "
import sys; sys.path.insert(0,'$HERE')
import r4_lib as R
ok,why,_=R.frozen_complete('$D')
sys.exit(0 if ok else 1)" 2>/dev/null; then
      echo "[skip-complete] $C"; return 0
    fi
  fi
  rm -f "$D/rc"
  ( cd "$D" && openfoam2606 kCorrectiveFrozenFoam ) > "$D/log.frozen" 2>&1
  local rc=$?
  if [ $rc -eq 0 ]; then
    local T
    T=$(ls "$D" | grep -E '^[0-9]+$' | grep -v '^0$' | sort -n | tail -1)
    ( cd "$D" && openfoam2606 postProcess -func 'grad(U)' -time "$T" ) \
        > "$D/log.gradU" 2>&1
    rc=$?
  fi
  echo "$rc" > "$D/rc"
  echo "[done rc=$rc] $C"
}
export -f one; export ROOT HERE PY FORCE

cd "$ROOT"
ls -d */ | tr -d / | xargs -P "$JOBS" -I{} bash -c 'one "$@"' _ {}
echo "ALL FROZEN RUNS DISPATCHED"
