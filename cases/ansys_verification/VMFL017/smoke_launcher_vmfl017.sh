#!/usr/bin/env bash
# Pre-flight LAUNCHER smoke (template Amendment 3 item 6): runs run_vmfl017.sh itself
# with VMFL_SMOKE=1 (L1, endTime overridden to 200 iters) against a SCRATCH run root,
# so the launcher's freeze check, blockMesh/checkMesh, 0/U age marker, rhoSimpleFoam
# invocation, per-level cap and RUN_RC record are all EXERCISED end-to-end -- not the
# solver in a bypass. Grades nothing; scratch discarded. Requires prereg+comparator at HEAD.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRATCH="$(mktemp -d /tmp/vmfl017_launchsmoke.XXXXXX)"
echo "launcher smoke -> $SCRATCH"
VMFL_SMOKE=1 bash "$SCRIPT_DIR/run_vmfl017.sh" "$SCRATCH/run"; RC=$?
OK=1
[ "$RC" -eq 0 ] || { echo "SMOKE FAIL: launcher exited rc=$RC"; OK=0; }
grep -q "^rc=0" "$SCRATCH/run/L1/RUN_RC.txt" 2>/dev/null || { echo "SMOKE FAIL: no rc=0 in L1/RUN_RC.txt"; OK=0; }
D=$(ls -d "$SCRATCH"/run/L1/postProcessing/forceCoeffs1/*/coefficient.dat 2>/dev/null | head -1)
[ -n "$D" ] && [ "$(grep -vc '^#' "$D")" -gt 0 ] || { echo "SMOKE FAIL: no forceCoeffs Cd/Cl data"; OK=0; }
grep -q "^End" "$SCRATCH/run/L1/log.rhoSimpleFoam" 2>/dev/null || { echo "SMOKE FAIL: no End in solver log"; OK=0; }
[ "$OK" -eq 1 ] && echo "LAUNCHER SMOKE OK (L1 exercised the launcher end-to-end)"
rm -rf "$SCRATCH"
[ "$OK" -eq 1 ]
