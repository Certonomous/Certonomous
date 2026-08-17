#!/usr/bin/env bash
# run_cases.sh -- mesh and solve one K0c case.  F14 rung K0c.
#
#   ./run_cases.sh <case-directory> [more case directories ...]
#
# One case per invocation argument, run SERIALLY inside this script; launch
# several copies of this script in the background to use more than one core.
# Each solve is single-core, so core-minutes = the per-case wall clock, and both
# are written to <case>/COST.txt.
#
# WHY THE OPENFOAM ENVIRONMENT IS SOURCED PER COMMAND
# ---------------------------------------------------
# Sourcing etc/bashrc into this shell fails twice over: it dereferences unset
# variables (fatal under `set -u`) and its config.sh/setup aborts with
# "pop_var_context: head of shell_variables not a function context" when sourced
# under `set -e`.  Every foam command is therefore run through its own
# `bash -c '. bashrc && ...'`, which is the pattern scripts/heat_balance.py and
# the K0b analyse.py already use in this repo.
#
# TIME-DIRECTORY HYGIENE, AND THE GLOB THAT MUST NOT BE USED
# ----------------------------------------------------------
# A previous pass on this repo cleaned cases with `rm -rf <case>/[0-9]*`.  That
# glob matches `0.orig`, which is the initial-condition directory the case is
# REBUILT from, and it deleted every one of them in the K0b tree before a
# hygiene check caught it.  Nothing in this file globs for time directories.
# Old times are removed by `foamListTimes -rm`, OpenFOAM's own enumeration of
# parseable time values: `0.orig` is not a parseable time and is invisible to
# it, and `0` is preserved by the utility by design.
set -eo pipefail

FOAM_BASHRC=${FOAM_BASHRC:-/usr/lib/openfoam/openfoam2606/etc/bashrc}

foam() {          # foam <case-dir> <command line ...>
    local dir="$1"; shift
    bash -c ". '$FOAM_BASHRC' >/dev/null 2>&1; cd '$dir' || exit 1; $*"
}

for case in "$@"; do
    case=$(readlink -f "$case")
    name=$(basename "$case")
    [ -d "$case/0.orig" ] || { echo "REFUSE: $case has no 0.orig"; exit 2; }

    start=$(date +%s.%N)

    foam "$case" "foamListTimes -rm >/dev/null 2>&1 || true"
    rm -rf "$case/0" "$case/postProcessing"
    cp -r "$case/0.orig" "$case/0"

    foam "$case" "blockMesh > log.blockMesh 2>&1"
    foam "$case" "checkMesh > log.checkMesh 2>&1"
    foam "$case" "buoyantBoussinesqSimpleFoam > log.buoyantBoussinesqSimpleFoam 2>&1"

    end=$(date +%s.%N)
    el=$(echo "$end - $start" | bc)
    printf '%s  wall %.2f s\n' "$name" "$el"
    printf 'case %s\nwall_clock_s %.3f\ncores 1\ncore_minutes %.4f\n' \
        "$name" "$el" "$(echo "$el / 60" | bc -l)" > "$case/COST.txt"
done
