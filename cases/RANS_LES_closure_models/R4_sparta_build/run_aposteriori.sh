#!/bin/bash
# R4 step 4 - run the a-posteriori propagations.
#
# Serial simpleFoam per case (the meshes are 2k-22k cells; decomposition costs
# more than it saves at this size and keeps the logs comparable with W2).
# rc is recorded to <case>/rc for the STRICT COMPLETION RULE.  A case that
# already meets the rule is SKIPPED, never rerun; --force overrides.
# Nothing is ever killed: every case is capped by endTime in controlDict and
# checkpointed at writeInterval, so an interrupted run resumes.
set -u
ROOT=/home/ubuntu/closure-data/r4/aposteriori
HERE=$(dirname "$(readlink -f "$0")")
PY=/home/ubuntu/closure-venv/bin/python
JOBS=${JOBS:-8}
FORCE=${FORCE:-}
FILTER=${FILTER:-}

one() {
  local D="$ROOT/$1"
  [ -d "$D" ] || { echo "[missing] $1"; return 0; }
  if [ "$FORCE" != "--force" ] && [ -f "$D/rc" ] && [ "$(cat "$D/rc")" = "0" ] \
     && grep -qE '^End$' "$D/log.solve" 2>/dev/null; then
    echo "[skip-complete] $1"; return 0
  fi
  rm -f "$D/rc"
  local t0=$(date +%s)
  ( cd "$D" && openfoam2606 simpleFoam ) > "$D/log.solve" 2>&1
  local rc=$?
  echo "$rc" > "$D/rc"
  echo "$(( $(date +%s) - t0 ))" > "$D/wall_seconds"
  echo "[done rc=$rc $(cat "$D/wall_seconds")s] $1"
}
export -f one; export ROOT HERE PY FORCE FILTER

cd "$ROOT"
# FILTER selects a subset of <case>/<config> directories (a grep -E pattern);
# with no FILTER every configuration of every case is dispatched.
ls -d */*/ | sed 's:/$::' | grep -E "${FILTER:-.}" \
  | xargs -P "$JOBS" -I{} bash -c 'one "$@"' _ {}
echo "ALL A-POSTERIORI RUNS DISPATCHED"
