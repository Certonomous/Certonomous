#!/usr/bin/env bash
# run_cases.sh -- mesh and solve one K2e case.  F14 rung K2e.
#
#   ./run_cases.sh <case-directory> [more case directories ...]
#
# One case per invocation argument, run SERIALLY inside this script; launch
# several copies in the background to use more than one core.  Every solve is
# single-core, so core-minutes = the per-case wall clock, and both are written
# to <case>/COST.txt.
#
# The application is read out of the case's own system/controlDict, so the same
# script runs the Boussinesq and the variable-density halves of the sweep and
# there is no second place for the two to drift apart.
#
# WHY THE OPENFOAM ENVIRONMENT IS SOURCED PER COMMAND
# ---------------------------------------------------
# Sourcing etc/bashrc into this shell fails twice over: it dereferences unset
# variables (fatal under `set -u`) and its config.sh/setup aborts with
# "pop_var_context: head of shell_variables not a function context" when sourced
# under `set -e`.  Every foam command is therefore run through its own
# `bash -c '. bashrc && ...'`, the pattern K0c's run_cases.sh and
# scripts/heat_balance.py already use in this repo.
#
# TIME-DIRECTORY HYGIENE, AND THE GLOB THAT MUST NOT BE USED
# ----------------------------------------------------------
# A previous pass on this repo cleaned cases with `rm -rf <case>/[0-9]*`.  That
# glob matches `0.orig`, the initial-condition directory the case is REBUILT
# from, and it deleted every one of them in the K0b tree.  Nothing in this file
# globs for time directories: old times go through `foamListTimes -rm`, which is
# OpenFOAM's own enumeration of parseable time values and cannot see `0.orig`.
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

    app=$(awk '/^application/ {print $2}' "$case/system/controlDict" | tr -d ';')
    [ -n "$app" ] || { echo "REFUSE: $case names no application"; exit 2; }

    start=$(date +%s.%N)

    foam "$case" "foamListTimes -rm >/dev/null 2>&1 || true"
    rm -rf "$case/0" "$case/postProcessing"
    cp -r "$case/0.orig" "$case/0"

    foam "$case" "blockMesh > log.blockMesh 2>&1"
    foam "$case" "checkMesh > log.checkMesh 2>&1"
    foam "$case" "$app > log.$app 2>&1" || true    # a diverged run is DATA; the
                                                   # convergence check grades it
    end=$(date +%s.%N)
    el=$(echo "$end - $start" | bc)
    printf '%s  %s  wall %.2f s\n' "$name" "$app" "$el"
    printf 'case %s\napplication %s\nwall_clock_s %.3f\ncores 1\ncore_minutes %.4f\n' \
        "$name" "$app" "$el" "$(echo "$el / 60" | bc -l)" > "$case/COST.txt"
done
