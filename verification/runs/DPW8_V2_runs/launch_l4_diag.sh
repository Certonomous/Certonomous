#!/bin/bash
# Launch one arm of the DPW8_V2 L4 divergence diagnosis.
# Pre-registration: verification/campaign/DPW8_V2_L4_DIVERGENCE_DIAG_PREREGISTRATION.md @ 99f939ee
#
# Usage: launch_l4_diag.sh <arm_dir_name>
#
# Section 9 traps this closes:
#  - the OpenFOAM bashrc is sourced in the SAME command as the launch (non-login
#    shells have no simpleFoam on PATH; that failure produced the 0-byte relaunch log
#    dpw8_v2_L4_gate_20260729T231306Z.log);
#  - setsid, so the solver outlives the agent;
#  - the exit code is written to solver.rc so completion is decided by rc, not by the
#    existence of any marker file (a .done body, not its filename).
# Section 8: the 75 core-min per-arm cap is enforced mechanically by timeout.
# Section 6: 0/ is touched last before launch so it dates the run, for the age guard.

set -u
ARM="$1"
HERE="$(cd "$(dirname "$0")" && pwd)"
D="$HERE/$ARM"
CAP_S=4450          # 75 core-min cap, single rank, minus checkMesh headroom
FOAM_BASHRC=/usr/lib/openfoam/openfoam2606/etc/bashrc

if [ ! -d "$D" ]; then echo "no such arm dir: $D" >&2; exit 1; fi

# Guard: refuse to launch into a directory that already holds a numeric time dir
# other than 0 (standing rule 4 -- a guard refuses a case where a time dir exists).
STALE=$(find "$D" -maxdepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+' \
        ! -name 0 -printf '%f ' 2>/dev/null)
if [ -n "$STALE" ]; then
  echo "REFUSING: $ARM already holds time directories: $STALE" >&2
  exit 1
fi
if [ -f "$D/log.simpleFoam" ]; then
  echo "REFUSING: $ARM already holds log.simpleFoam" >&2
  exit 1
fi

# Age guard reference: touch 0/ LAST before launch so every field written at endTime
# is provably newer than the initial condition this run started from.
touch "$D"/0/*
date -u +"%Y-%m-%dT%H:%M:%SZ" > "$D/LAUNCHED_AT"

cd "$D" || exit 1

# `set -u` MUST be off across the source: OpenFOAM v2606's etc/bashrc reads
# WM_PROJECT_DIR at line 184 before setting it, so under `set -u` the sourced script
# aborts the CALLING shell instantly, before any output. That produces a zero-byte
# launcher log and no solver.rc -- the identical silent signature that section 9
# trap 1 describes for the missing-PATH case, from a completely different cause.
# Measured 2026-08-23: `bash -c 'set -u; source .../etc/bashrc ""'` -> rc 127,
# "WM_PROJECT_DIR: unbound variable"; the same line without `set -u` -> rc 0.
set +u
echo "[launcher] sourcing $FOAM_BASHRC"
source "$FOAM_BASHRC" "" >/dev/null 2>&1
echo "[launcher] simpleFoam resolves to: $(command -v simpleFoam || echo NOT-ON-PATH)"

if ! command -v simpleFoam >/dev/null 2>&1; then
  echo "REFUSING: simpleFoam not on PATH after sourcing $FOAM_BASHRC" >&2
  echo "127" > "$D/solver.rc"
  exit 127
fi

echo "[launcher] checkMesh"
checkMesh -noTopology > "$D/log.checkMesh" 2>&1
echo "checkMesh rc=$?" >> "$D/log.checkMesh"

echo "[launcher] simpleFoam starting, cap ${CAP_S}s"
/usr/bin/time -f "%e wall_s %P cpu" -o "$D/solver.time" \
  timeout "$CAP_S" simpleFoam > "$D/log.simpleFoam" 2>&1
RC=$?
echo "[launcher] simpleFoam exited rc=$RC"
echo "$RC" > "$D/solver.rc"
date -u +"%Y-%m-%dT%H:%M:%SZ" > "$D/FINISHED_AT"
exit $RC
