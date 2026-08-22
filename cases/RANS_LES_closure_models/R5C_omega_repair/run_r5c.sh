#!/bin/bash
# R5C - run the frozen extractions with kCorrectiveFrozenFoamV2.
#
#   run_r5c.sh legacy     the 2 gate-G2 cases, omegaSourceRepair FALSE
#   run_r5c.sh repaired   the 27 R5C cases,   omegaSourceRepair TRUE
#
# Each case is a serial kCorrectiveFrozenFoamV2 solve (no decomposition: the
# solver writes once, at its own settle iteration) followed by
# `postProcess -func 'grad(U)'` on that directory, so the record uses the SAME
# discrete gradient the frozen solve used (R4/W2 regression convention 1).
#
# rc is recorded to <case>/rc and the elapsed wall time to <case>/wall_seconds
# for the STRICT COMPLETION RULE and for the cost actual.  Completed cases are
# SKIPPED, never rerun; `--force` is deliberately NOT offered - a frozen
# extraction is not restarted in place (PREREGISTRATION sec. 4).
#
# Concurrency is capped at 6 (PREREGISTRATION sec. 6): the box carries the
# T-family thermal lane, whose priority is restored.  Nothing is reniced.
set -u
SET=${1:?usage: run_r5c.sh legacy|repaired}
case "$SET" in
  legacy)   ROOT=/home/ubuntu/closure-data/r5c/w2_legacy ;;
  repaired) ROOT=/home/ubuntu/closure-data/r5c/frozen ;;
  *) echo "usage: run_r5c.sh legacy|repaired" >&2; exit 2 ;;
esac
JOBS=${JOBS:-6}

one() {
  local C="$1" D="$ROOT/$1"
  if [ -f "$D/rc" ] && [ "$(cat "$D/rc")" = "0" ]; then
    echo "[skip-done] $C"; return 0
  fi
  local t0 t1
  t0=$(date +%s.%N)
  ( cd "$D" && openfoam2606 kCorrectiveFrozenFoamV2 ) > "$D/log.frozen" 2>&1
  local rc=$?
  if [ $rc -eq 0 ]; then
    local T
    T=$(ls "$D" | grep -E '^[0-9]+$' | grep -v '^0$' | sort -n | tail -1)
    ( cd "$D" && openfoam2606 postProcess -func 'grad(U)' -time "$T" ) \
        > "$D/log.gradU" 2>&1
    rc=$?
  fi
  t1=$(date +%s.%N)
  echo "$rc" > "$D/rc"
  awk -v a="$t0" -v b="$t1" 'BEGIN{printf "%.2f\n", b-a}' > "$D/wall_seconds"
  echo "[done rc=$rc $(cat "$D/wall_seconds")s] $C"
}
export -f one; export ROOT

cd "$ROOT"
ls -d */ | tr -d / | xargs -P "$JOBS" -I{} bash -c 'one "$@"' _ {}
echo "ALL R5C $SET RUNS DISPATCHED"
