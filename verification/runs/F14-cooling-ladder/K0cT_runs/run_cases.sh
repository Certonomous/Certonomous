#!/usr/bin/env bash
# run_cases.sh -- mesh and solve one K0c TURBULENT case.  F14 rung K0c-T.
#
#   ./run_cases.sh <case-directory> [more case directories ...]
#
# Carried unchanged in form from K0c_runs/run_cases.sh, including its two
# recorded traps:
#   * the OpenFOAM environment is sourced per command, because sourcing
#     etc/bashrc into this shell fails under both `set -u` and `set -e`;
#   * NOTHING here globs for time directories.  `rm -rf <case>/[0-9]*` matches
#     `0.orig` and destroyed every initial-condition directory in the K0b tree
#     once already.  Old times go by `foamListTimes -rm`, which enumerates
#     parseable time values only and cannot see `0.orig`.
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
