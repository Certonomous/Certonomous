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

# ===========================================================================
# ENV-0 -- THE SILENT-EXIT TRAP.  rc 12.
#
# ADDENDUM 4.  On 2026-09-03T22:24:16Z this script exited 1 and said NOTHING
# ABOUT ITSELF: no ENV-n refusal, no SO3AF2_ENV_OK.  It neither passed nor
# refused, and rc=1 was outside the item's whole registered set.
#
# THAT IS THE THIRD MEMBER OF TONIGHT'S COVERAGE-LIE FAMILY AND THE ONE THE
# OTHER TWO DO NOT COVER: a leg that passes for the wrong reason, a leg
# unreachable while reporting PASS -- and now a leg that is SILENT rather than
# wrong.  A silent instrument is the hardest of the three to notice, because
# there is nothing to read.
#
# THE RULE THIS ENFORCES: an instrument must ALWAYS say which of its outcomes
# occurred, INCLUDING "neither".  The trap fires on any exit that reached
# neither a named refusal nor the OK line, prints the LAST CHECKPOINT REACHED so
# the silence itself becomes evidence, and exits 12 -- distinct from the four
# NO-LAUNCH codes (3/4/5/6), the producer (7), the cap (8), staging (9), docker
# start (10) and the environment refusals (11).
# ===========================================================================
ENV_CHECKPOINT="entry: before argument parsing"
ENV_VERDICT_EMITTED=0

env_exit_trap() {
  local rc="$1"
  if [ "$ENV_VERDICT_EMITTED" = "1" ]; then
    return
  fi
  echo "ABORT ENV-0 ASSERT TERMINATED WITHOUT VERDICT -- this script exited $rc having emitted"
  echo "ABORT ENV-0 neither a named refusal nor SO3AF2_ENV_OK. The silence is the finding."
  echo "ABORT ENV-0 last_checkpoint_reached: $ENV_CHECKPOINT"
  exit 12
}
trap 'env_exit_trap $?' EXIT

if [ "$#" -lt 2 ]; then
  ENV_VERDICT_EMITTED=1
  echo "ABORT ENV-0-USAGE so3af2_env_assert.sh <loader> <command...>"
  exit 11
fi

LOADER="$1"
shift

if [ ! -f "$LOADER" ]; then
  ENV_VERDICT_EMITTED=1
  echo "ABORT ENV-1 loader $LOADER is not a file inside this container. UNMEASURED, not assumed."
  exit 11
fi

ENV_CHECKPOINT="about to source the loader"

# ⚠ `set -u` IS RELAXED ACROSS THIS ONE LINE, AND ONLY THIS ONE LINE.
#
# A THIRD-PARTY INIT SCRIPT'S UNBOUND REFERENCES ARE EXPECTED BEHAVIOUR, NOT A
# DEFECT TO BE CAUGHT.  OpenFOAM's own `etc/bashrc` references `WM_PROJECT_DIR`
# before setting it -- entirely normal for an init script -- and under `set -u`
# bash aborted INSIDE the source, exit 1, before any check below could run.
#
# A1WR's driver carries `set -uo pipefail` too (`a1wr_chain_driver.sh:27`) and
# works, because its `source` runs inside a FRESH `bash -lc` IN THE CONTAINER,
# which does not inherit the host script's shell options: ITS `set -u` AND ITS
# `source` ARE IN DIFFERENT SHELLS ON DIFFERENT MACHINES.  This script had both
# in one shell.
#
# THIS WEAKENS NOTHING.  ENV-1 through ENV-5 are the actual verification and
# every one of them runs with `set -u` RESTORED.  The relaxation covers exactly
# one line, whose failure is now REPORTED by ENV-2's `SRC_RC` instead of by a
# dead shell.
set +u
# shellcheck disable=SC1090
source "$LOADER"
SRC_RC=$?
set -u
ENV_CHECKPOINT="sourced the loader, rc=$SRC_RC; about to verify the environment"
if [ "$SRC_RC" != "0" ]; then
  ENV_VERDICT_EMITTED=1
  echo "ABORT ENV-2 sourcing $LOADER returned $SRC_RC"
  exit 11
fi

ENV_CHECKPOINT="checking ENV-3 (checkMesh on PATH)"
if ! command -v checkMesh > /dev/null 2>&1; then
  ENV_VERDICT_EMITTED=1
  echo "ABORT ENV-3 checkMesh is NOT on PATH after sourcing $LOADER -- the MESH arm invokes it by name"
  exit 11
fi

ENV_CHECKPOINT="checking ENV-4 (FOAM_APPBIN)"
if [ -z "${FOAM_APPBIN:-}" ]; then
  ENV_VERDICT_EMITTED=1
  echo "ABORT ENV-4 FOAM_APPBIN is EMPTY after sourcing $LOADER"
  exit 11
fi

ENV_CHECKPOINT="checking ENV-5 (WM_PROJECT)"
if [ -z "${WM_PROJECT:-}" ]; then
  ENV_VERDICT_EMITTED=1
  echo "ABORT ENV-5 WM_PROJECT is EMPTY after sourcing $LOADER -- this is the VERY VARIABLE"
  echo "ABORT ENV-5 preProcessing.sh tests in its own first three lines, and the variable whose"
  echo "ABORT ENV-5 absence produced this item's second rc=127."
  exit 11
fi

ENV_VERDICT_EMITTED=1
ENV_CHECKPOINT="all checks passed; about to exec the arm command"
echo "SO3AF2_ENV_OK loader=$LOADER checkMesh=$(command -v checkMesh) FOAM_APPBIN=$FOAM_APPBIN WM_PROJECT=$WM_PROJECT"

exec "$@"
