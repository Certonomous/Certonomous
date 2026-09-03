#!/usr/bin/env bash
# SO-3aF2 ENVIRONMENT ASSERTION -- runs INSIDE the container, ahead of every arm.
#
#   usage: so3af2_env_assert.sh <loader> <command...>
#
# WHY THIS FILE EXISTS. The MESH arm was launched twice and exited rc=127 twice.
# The first time nothing was staged. The second time the inputs were staged
# correctly and `preProcessing.sh` RAN -- and exited at its own first guard:
#
#     OpenFOAM environment not found, forgot to source the OpenFOAM bashrc?
#     bash: line 1: checkMesh: command not found
#
# The arm command never sourced the DAFoam environment, and `bash -lc` does not
# supply it: a non-interactive login shell reads /etc/profile and the first of
# ~/.bash_profile, ~/.bash_login, ~/.profile -- NOT ~/.bashrc, which is where a
# DAFoam image's environment hangs. Every working driver in this family sources
# it explicitly; `a1wr_chain_driver.sh:173` is the one this item's own ladder was
# built on, and the string appears 110 times across the family's drivers.
#
# AND IT DOES NOT TRUST THE `source`. A `source` that silently no-ops is exactly
# the failure this item has already paid for twice, and "we sourced it, so it must
# be loaded" is the same weakening `S6` was rescued from in A1WRT. The shape is
# write-read-back-assert, applied to an environment: source it, then verify from
# the environment itself that what the arm needs is actually there, and REFUSE BY
# NAME if it is not.
#
# ENV-5 IS THE LOAD-BEARING ONE: `$WM_PROJECT` is the exact variable
# `preProcessing.sh` tests in its own first three lines. Asserting the variable
# the arm's own script checks is stronger than asserting one we chose.
#
# rc 11, ITS OWN CODE. Distinct from the four registered NO-LAUNCH branches
# (3/4/5/6), the producer's residual refusal (7), the cap (8), the staging
# precondition (9) and the docker-start failure (10). It can only ever refuse
# MORE, never less.
#
# NO `assert` ANYWHERE: this is shell, and every refusal below is an explicit
# test-and-exit that prints its own name.

set -uo pipefail

if [ "$#" -lt 2 ]; then
  echo "ABORT ENV-0 usage: so3af2_env_assert.sh <loader> <command...>"
  exit 11
fi

LOADER="$1"
shift

if [ ! -f "$LOADER" ]; then
  echo "ABORT ENV-1 loader $LOADER is not a file inside this container. UNMEASURED, not assumed."
  exit 11
fi

# shellcheck disable=SC1090
source "$LOADER"
SRC_RC=$?
if [ "$SRC_RC" != "0" ]; then
  echo "ABORT ENV-2 sourcing $LOADER returned $SRC_RC"
  exit 11
fi

if ! command -v checkMesh > /dev/null 2>&1; then
  echo "ABORT ENV-3 checkMesh is NOT on PATH after sourcing $LOADER -- the MESH arm invokes it by name"
  exit 11
fi

if [ -z "${FOAM_APPBIN:-}" ]; then
  echo "ABORT ENV-4 FOAM_APPBIN is EMPTY after sourcing $LOADER"
  exit 11
fi

if [ -z "${WM_PROJECT:-}" ]; then
  echo "ABORT ENV-5 WM_PROJECT is EMPTY after sourcing $LOADER -- this is the VERY VARIABLE"
  echo "ABORT ENV-5 preProcessing.sh tests in its own first three lines, and the variable whose"
  echo "ABORT ENV-5 absence produced this item's second rc=127."
  exit 11
fi

echo "SO3AF2_ENV_OK loader=$LOADER checkMesh=$(command -v checkMesh) FOAM_APPBIN=$FOAM_APPBIN WM_PROJECT=$WM_PROJECT"

exec "$@"
