#!/usr/bin/env bash
# continue_cases.sh -- continue a K0c-T case from its latestTime.  F14 rung K0c-T.
#
#   ./continue_cases.sh <endTime> <case-directory> [more ...]
#
# WHY THIS EXISTS.  Six of the nine cases met their `residualControl` or ran out
# their first-stage iteration budget while the GRADED quantities were still
# moving by more than the standing convergence criterion of
# docs/physics_rules.yaml (peak-to-peak spread over a fixed 400-iteration
# window).  The residuals are not the criterion and never were; this script is
# what the criterion costs when it is not met.
#
# It NEVER runs blockMesh, NEVER touches 0.orig, and NEVER removes a time
# directory: the continued run restarts from latestTime and the first stage's
# log travels with the case as log.buoyantBoussinesqSimpleFoam (stage 1) beside
# log.buoyantBoussinesqSimpleFoam.stage2.
set -eo pipefail
FOAM_BASHRC=${FOAM_BASHRC:-/usr/lib/openfoam/openfoam2606/etc/bashrc}
END="$1"; shift
foam() { local dir="$1"; shift; bash -c ". '$FOAM_BASHRC' >/dev/null 2>&1; cd '$dir' || exit 1; $*"; }

for case in "$@"; do
    case=$(readlink -f "$case"); name=$(basename "$case")
    start=$(date +%s.%N)
    sed -i "s/^startFrom       startTime;/startFrom       latestTime;/" "$case/system/controlDict"
    sed -i "s/^endTime         .*/endTime         $END;/" "$case/system/controlDict"
    sed -i "s/^writeInterval   .*/writeInterval   $END;/" "$case/system/controlDict"
    # DEFECT FOUND BY EXECUTION, 2026-08-18: the first version of this script
    # wrote every continuation to log.buoyantBoussinesqSimpleFoam.stage2, so a
    # SECOND continuation OVERWROTE the first one's log.  It happened on T_hi_c
    # and S_hi_c_seed100 before it was caught.  The monitored series survived
    # because they live in postProcessing/, which a continuation appends to in a
    # new time directory rather than replacing -- but the iteration trace did
    # not.  The stage number is now derived from what is already on disk.
    n=2; while [ -f "$case/log.buoyantBoussinesqSimpleFoam.stage$n" ]; do n=$((n+1)); done
    foam "$case" "buoyantBoussinesqSimpleFoam > log.buoyantBoussinesqSimpleFoam.stage$n 2>&1"
    end=$(date +%s.%N); el=$(echo "$end - $start" | bc)
    printf '%s  stage%s wall %.2f s\n' "$name" "$n" "$el"
    printf 'case %s\nstage%s_wall_clock_s %.3f\ncores 1\nstage%s_core_minutes %.4f\n' \
        "$name" "$n" "$el" "$n" "$(echo "$el / 60" | bc -l)" >> "$case/COST.txt"
done
