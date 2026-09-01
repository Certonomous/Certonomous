#!/usr/bin/env bash
# =============================================================================
# AOA POLAR -- the program that runs INSIDE the container.
#
# A FILE, NOT AN INLINE HEREDOC, DELIBERATELY: SO-1b evaluated its one real
# decision inside a heredoc that existed only inside a shell script, which is
# untestable by construction and fired unexamined at rc=7. This file can be
# md5-pinned, read, and driven end to end.
#
# PRIMAL ONLY. No adjoint, no optimiser, no FFD deformation, no CL trim --
# `findFeasibleDesign` is never called on this path.
#
# TWO STAGES, IN THIS ORDER:
#   1. THE CONTINUED SWEEP. ONE process, all declared alphas, ascending.
#      `0/` is reset from `0.orig` ONCE, before the process starts, so alpha_0
#      is cold and every later point inherits its predecessor's converged state
#      IN MEMORY. That is the continuation.
#   2. THE COLD CONTROLS. One process per control alpha, in a SEPARATE case
#      directory, each with `0/` reset from `0.orig` immediately before it.
#      These are the instrument check on stage 1 and the path-dependence test.
#      They run in their own tree so they cannot disturb stage 1's artefacts.
#
# NOTE ON WHY THE RESET IS LOAD-BEARING: pyDAFoam renames the converged
# solution back into `0/` when a primal finishes (verified on disk: the SO3aF
# case's `0/` holds solved U/p/nuTilda/nut after its run, alongside the numbered
# time directories). So a "cold" start that does not reset `0/` is not cold.
#
# NEITHER STAGE RETRIES, RELAXES OR RE-TUNES A POINT THAT DID NOT CONVERGE, AND
# NEITHER DROPS ONE. A point that fails is recorded and the program continues.
# =============================================================================
set -uo pipefail

cd /mnt/case || { echo "AOA_FATAL cannot cd /mnt/case"; exit 90; }

# ---- point-of-use existence asserts -----------------------------------------
# Startup-only asserts are how a path that is valid once becomes a silent
# failure on every later use (so1br_chain_driver.sh:83/:206).
test -f /mnt/aoa_runScript.py       || { echo "AOA_FATAL runScript absent at point of use"; exit 91; }
test -d 0.orig                      || { echo "AOA_FATAL 0.orig absent at point of use"; exit 92; }
test -f constant/polyMesh/points.gz || { echo "AOA_FATAL mesh absent at point of use"; exit 93; }
test -n "${AOA_ALPHAS:-}"           || { echo "AOA_FATAL AOA_ALPHAS unset"; exit 94; }
test -n "${AOA_COLD_ALPHAS:-}"      || { echo "AOA_FATAL AOA_COLD_ALPHAS unset"; exit 94; }
test -d /mnt/case_cold              || { echo "AOA_FATAL case_cold absent at point of use"; exit 92; }

mkdir -p /mnt/out || { echo "AOA_FATAL cannot mkdir /mnt/out"; exit 95; }

# DECLARED is counted from the actual list, never asserted from memory.
DECLARED=0
for A in $AOA_ALPHAS; do DECLARED=$((DECLARED + 1)); done
NCOLD=0
for A in $AOA_COLD_ALPHAS; do NCOLD=$((NCOLD + 1)); done
echo "AOA_DECLARED=$DECLARED list=[$AOA_ALPHAS]"
echo "AOA_COLD_DECLARED=$NCOLD list=[$AOA_COLD_ALPHAS]"

# =============================================================================
# STAGE 1 -- THE CONTINUED SWEEP
# =============================================================================
echo "AOA_STAGE1_BEGIN utc=$(date -u +%Y-%m-%dT%H%M%SZ)"
rm -rf 0 && cp -r 0.orig 0 || { echo "AOA_FATAL cannot reset 0/ before the sweep"; exit 96; }
echo "AOA_STAGE1_COLD_START 0/ reset from 0.orig -- alpha_0 is cold"

AOA_MODE=CONTINUED \
AOA_POINTS_JSON=/mnt/out/points_continued.json \
AOA_ALPHA0=0.0 \
timeout -k 30 "${AOA_STAGE1_TMO:-1500}" \
  python /mnt/aoa_runScript.py -task sweep > /mnt/out/sweep.log 2>&1
S1RC=$?
echo "AOA_STAGE1_END rc=$S1RC log=/mnt/out/sweep.log"

# EXECUTED counted from the program's OWN emitted markers, never assumed.
# `grep -c` PRINTS 0 AND EXITS 1 with no match, so `|| echo 0` would append a
# SECOND zero and make the variable the two-line string "0\n0" -- that is what
# put a stray bare 0 into STATUS.SO3aF. `|| true` keeps grep's count.
S1_EXEC="$(grep -c '^AOA_POINT_END ' /mnt/out/sweep.log 2>/dev/null || true)"
S1_CONV="$(grep -c 'satisfied the prescribed tolerance' /mnt/out/sweep.log 2>/dev/null || true)"
S1_EXEC="${S1_EXEC:-0}"; S1_CONV="${S1_CONV:-0}"
echo "AOA_STAGE1_COUNTS declared=$DECLARED executed=$S1_EXEC converged_lines=$S1_CONV"

# =============================================================================
# STAGE 2 -- THE COLD CONTROLS
# Stage 1's rc does NOT gate stage 2. If the sweep failed, the cold controls
# are MORE informative, not less, and skipping them would discard the only
# independent check on the continuation instrument.
# =============================================================================
echo "AOA_STAGE2_BEGIN utc=$(date -u +%Y-%m-%dT%H%M%SZ)"
cd /mnt/case_cold || { echo "AOA_FATAL cannot cd /mnt/case_cold"; exit 90; }
test -d 0.orig || { echo "AOA_FATAL case_cold has no 0.orig"; exit 92; }

C_EXEC=0
for A in $AOA_COLD_ALPHAS; do
  echo "AOA_COLD_BEGIN alpha=$A utc=$(date -u +%Y-%m-%dT%H%M%SZ)"
  rm -rf 0 && cp -r 0.orig 0 || { echo "AOA_FATAL cannot reset 0/ for cold alpha=$A"; exit 96; }
  AOA_MODE=COLD \
  AOA_ALPHAS="$A" \
  AOA_POINTS_JSON="/mnt/out/points_cold_${A}.json" \
  AOA_ALPHA0="$A" \
  timeout -k 20 "${AOA_COLD_TMO:-300}" \
    python /mnt/aoa_runScript.py -task sweep > "/mnt/out/cold_alpha_${A}.log" 2>&1
  crc=$?
  echo "AOA_COLD_END alpha=$A rc=$crc log=/mnt/out/cold_alpha_${A}.log"
  if [ "$crc" -eq 0 ]; then C_EXEC=$((C_EXEC + 1)); fi
done
echo "AOA_STAGE2_COUNTS cold_declared=$NCOLD cold_executed=$C_EXEC"

# =============================================================================
# BOTH counts, always, whatever happened. NO SUCCESS TOKEN OVER A TRUNCATED
# PROGRAM -- W3's launcher printed PHASE1_COMPLETE unconditionally after
# blocking 20 of 33 declared stages and misled a triage into calling it normal.
# =============================================================================
echo "AOA_COUNTS declared=$DECLARED executed=$S1_EXEC cold_declared=$NCOLD cold_executed=$C_EXEC"

if [ "$S1_EXEC" -eq "$DECLARED" ] && [ "$C_EXEC" -eq "$NCOLD" ]; then
  echo "AOA_ALL_POINTS_EXECUTED declared=$DECLARED cold_declared=$NCOLD"
  exit 0
fi
echo "AOA_TRUNCATED declared=$DECLARED executed=$S1_EXEC cold_declared=$NCOLD cold_executed=$C_EXEC -- NOT a completion"
exit 97
