#!/usr/bin/env bash
# check_artifacts.sh -- P-D of the D406 repair pre-registration, checked
# independently of the physics.  Exit codes are captured directly; nothing here
# is gated on a pipe.
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
RUNG=$(cd "$HERE/../K0b_mesh_sensitivity" && pwd)
ARCH=$(cd "$HERE/../../THERMAL_K0_runs/K0b_cavity_Ra1e5" && pwd)
fail=0
say() { printf '%-72s %s\n' "$1" "$2"; }

[ -f "$HERE/K0b_m128/log.buoyantBoussinesqSimpleFoam.continue" ]; r=$?
say "P-D.1a  K0b_m128/log.buoyantBoussinesqSimpleFoam.continue exists" "exit $r"; [ $r -eq 0 ] || fail=1

grep -q "^Create mesh for time = 4000$" "$HERE/K0b_m128/log.buoyantBoussinesqSimpleFoam.continue"; r=$?
say "P-D.1b  continuation log opens at 'Create mesh for time = 4000'" "exit $r"; [ $r -eq 0 ] || fail=1

grep -q "^Time = 16000$" "$HERE/K0b_m128/log.buoyantBoussinesqSimpleFoam.continue"; r=$?
say "P-D.1c  continuation log reaches 'Time = 16000'" "exit $r"; [ $r -eq 0 ] || fail=1

grep -q "^continue_wall_clock_s " "$HERE/K0b_m128/COST.txt"; r=$?
say "P-D.2   K0b_m128/COST.txt carries continue_wall_clock_s" "exit $r"; [ $r -eq 0 ] || fail=1

grep -q "^wall_clock_s " "$HERE/K0b_m128/COST.txt"; r=$?
say "P-D.2b  ...and still carries the stage-1 wall_clock_s (appended, not rewritten)" "exit $r"; [ $r -eq 0 ] || fail=1

cmp -s "$HERE/K0b_m128/system/controlDict.4000" "$RUNG/K0b_m128/system/controlDict.4000"; r=$?
say "P-D.3a  controlDict.4000 byte-identical to the PUBLISHED one" "exit $r"; [ $r -eq 0 ] || fail=1

cmp -s "$HERE/K0b_m128/system/controlDict.4000" "$ARCH/system/controlDict"; r=$?
say "P-D.3b  controlDict.4000 byte-identical to the ARCHIVE case's controlDict" "exit $r"; [ $r -eq 0 ] || fail=1

cmp -s "$HERE/K0b_m128/system/controlDict" "$RUNG/K0b_m128/system/controlDict"; r=$?
say "P-D.4   final controlDict byte-identical to the PUBLISHED one" "exit $r"; [ $r -eq 0 ] || fail=1

# P-B: the converged leg must NOT have been continued.
[ ! -e "$HERE/K0b_m32/system/controlDict.4000" ]; r=$?
say "P-B.1   K0b_m32 carries NO controlDict.4000 (it was not continued)" "exit $r"; [ $r -eq 0 ] || fail=1

[ ! -e "$HERE/K0b_m32/log.buoyantBoussinesqSimpleFoam.continue" ]; r=$?
say "P-B.2   K0b_m32 has NO continuation log" "exit $r"; [ $r -eq 0 ] || fail=1

grep -q "^continue_wall_clock_s " "$HERE/K0b_m32/COST.txt"; r=$?
say "P-B.3   K0b_m32/COST.txt has NO continue_wall_clock_s (expect exit 1)" "exit $r"; [ $r -eq 1 ] || fail=1

cmp -s "$HERE/K0b_m32/system/controlDict" "$ARCH/system/controlDict"; r=$?
say "P-B.4   K0b_m32/system/controlDict is still the archive case's own" "exit $r"; [ $r -eq 0 ] || fail=1

grep -q "SIMPLE solution converged in 1386 iterations" "$HERE/K0b_m32/log.buoyantBoussinesqSimpleFoam"; r=$?
say "P-B.5   K0b_m32 stopped itself on residualControl at 1386 iterations" "exit $r"; [ $r -eq 0 ] || fail=1

# the 32x32 published leg's dictionaries, for completeness
for f in system/blockMeshDict system/fvSchemes system/fvSolution system/controlDict; do
  cmp -s "$HERE/K0b_m32/$f" "$RUNG/K0b_m32/$f"; r=$?
  say "        K0b_m32/$f vs published" "exit $r"; [ $r -eq 0 ] || fail=1
done
for f in system/blockMeshDict system/fvSchemes system/fvSolution; do
  cmp -s "$HERE/K0b_m128/$f" "$RUNG/K0b_m128/$f"; r=$?
  say "        K0b_m128/$f vs published" "exit $r"; [ $r -eq 0 ] || fail=1
done

echo
echo "OVERALL: $([ $fail -eq 0 ] && echo ALL CHECKS PASSED || echo 'AT LEAST ONE CHECK FAILED')"
exit $fail
