#!/usr/bin/env bash
# =============================================================================
# SO-3a ALPHA FEASIBILITY -- the program that runs INSIDE the container.
#
# THIS IS A FILE, NOT AN INLINE HEREDOC, DELIBERATELY. SO-1b evaluated its one
# real decision inside a heredoc that existed only inside a shell script, which
# is untestable by construction and fired unexamined at rc=7. This file can be
# md5-pinned, read, and driven end to end.
#
# PRIMAL ONLY. No adjoint, no optimiser, no FFD deformation, no CL trim.
# The runScript is invoked with -task run_model, which is `prob.run_model()`
# and nothing else.
# =============================================================================
set -uo pipefail

cd /mnt/case || { echo "SO3AF_FATAL cannot cd /mnt/case"; exit 90; }

# Point-of-use existence asserts. Startup-only asserts are how a path that is
# valid once becomes a silent failure on every later use.
test -f /mnt/so3af_runScript.py || { echo "SO3AF_FATAL runScript absent at point of use"; exit 91; }
test -d 0.orig                  || { echo "SO3AF_FATAL 0.orig absent at point of use"; exit 92; }
test -f constant/polyMesh/points.gz || { echo "SO3AF_FATAL mesh absent at point of use"; exit 93; }
test -n "${SO3AF_ALPHAS:-}"     || { echo "SO3AF_FATAL SO3AF_ALPHAS unset"; exit 94; }

mkdir -p /mnt/out || { echo "SO3AF_FATAL cannot mkdir /mnt/out"; exit 95; }

# DECLARED is counted from the actual list, not asserted from memory.
DECLARED=0
for A in $SO3AF_ALPHAS; do DECLARED=$((DECLARED + 1)); done
echo "SO3AF_DECLARED_ALPHAS=$DECLARED list=[$SO3AF_ALPHAS]"

EXECUTED=0
CONVERGED=0
for A in $SO3AF_ALPHAS; do
  echo "SO3AF_ALPHA_BEGIN alpha=$A utc=$(date -u +%Y-%m-%dT%H%M%SZ)"

  # Each operating point starts from the SAME initial field, so the three
  # solves are independent and no point inherits its neighbour's answer.
  rm -rf 0 && cp -r 0.orig 0 || { echo "SO3AF_FATAL cannot reset 0/ for alpha=$A"; exit 96; }

  LOG="/mnt/out/primal_alpha_${A}.log"
  SO3AF_AOA="$A" timeout -k 20 150 python /mnt/so3af_runScript.py -task run_model > "$LOG" 2>&1
  rc=$?
  echo "SO3AF_ALPHA_END alpha=$A rc=$rc log=$LOG"

  if [ "$rc" -eq 0 ]; then
    EXECUTED=$((EXECUTED + 1))
    # A zero rc is not convergence. DAFoam prints the primal residual state;
    # a run that hit maxIter without meeting primalMinResTol still exits 0.
    if grep -q "Primal solution converged" "$LOG" 2>/dev/null; then
      CONVERGED=$((CONVERGED + 1))
      echo "SO3AF_ALPHA_CONVERGED alpha=$A"
    else
      echo "SO3AF_ALPHA_NOT_CONVERGED alpha=$A (rc 0 but no convergence line -- reported, not absorbed)"
    fi
  fi
done

# BOTH counts, always, whatever happened.
echo "SO3AF_COUNTS declared=$DECLARED executed=$EXECUTED converged=$CONVERGED"

# NO SUCCESS-READING TOKEN OVER A TRUNCATED PROGRAM. W3's launcher printed
# PHASE1_COMPLETE unconditionally after blocking 20 of 33 stages and that token
# misled a triage into calling it a normal completion. This one is conditional
# and the failure branch says which count fell short.
if [ "$EXECUTED" -eq "$DECLARED" ]; then
  echo "SO3AF_ALL_ALPHAS_EXECUTED declared=$DECLARED executed=$EXECUTED"
  exit 0
fi

echo "SO3AF_TRUNCATED declared=$DECLARED executed=$EXECUTED -- NOT a completion"
exit 97
