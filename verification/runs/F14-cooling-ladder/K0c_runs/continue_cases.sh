#!/usr/bin/env bash
# continue_cases.sh -- stage 2 of a K0c case: continue from latestTime with an
# accelerated SIMPLE outer loop.  F14 rung K0c.
#
#   ./continue_cases.sh <endTime> <case-directory> [more cases ...]
#
# WHY THIS EXISTS -- THE MEASUREMENT THAT FORCED IT
# -------------------------------------------------
# Stage 1 used K0b's relaxation (U 0.3, p_rgh 0.7, T 0.5).  Under those factors
# every COARSE mesh reached the convergence criterion and every FINE mesh did
# not.  Measured drift of Nu_avg over the last quarter of each stage-1 run:
#
#     Ra1e3_m32   0.0004 %      Ra1e3_m64    2.19 %
#     Ra1e4_m40   0.0084 %      Ra1e4_m80    3.98 %
#     Ra1e5_m64   0.0031 %      Ra1e5_m128   4.67 %
#     Ra1e6_m128  0.0040 %      (Ra1e6_m192 still in stage 1 at the time)
#     C1 g=0, 128x128: 14.65 %
#
# against a criterion of 0.02 %.  The pattern is not noise: an under-relaxed
# SIMPLE outer loop propagates the smooth modes at a rate that falls off like
# 1/N^2, so doubling the mesh needs about four times the iterations.  The C1
# case is the clean demonstration -- with g = 0 the temperature equation is pure
# diffusion whose exact answer is a straight line and Nu = 1, and after 3000
# iterations it was still at Nu = 1.328 with the core sitting near its initial
# 300 K.  Grading any of those fields would have been grading iteration error.
#
# WHAT CHANGES, AND WHY IT DOES NOT CHANGE THE ANSWER
# ---------------------------------------------------
# Relaxation factors and linear-solver tolerances are properties of the PATH to
# the fixed point, not of the fixed point.  The discrete equations -- mesh,
# schemes, boundary conditions, properties -- are untouched, so the converged
# solution is the same solution.  That claim is not left as an assertion: control
# C5 continues Ra1e5_m64, which ALREADY met the convergence criterion under the
# stage-1 factors, under the stage-2 factors and requires its Nu_avg not to move
# by more than the criterion itself.  If relaxation moved the answer, C5 catches
# it.
#
# Nothing here globs for time directories; see the note in run_cases.sh.
set -eo pipefail

FOAM_BASHRC=${FOAM_BASHRC:-/usr/lib/openfoam/openfoam2606/etc/bashrc}
END=$1; shift

for case in "$@"; do
    case=$(readlink -f "$case")
    name=$(basename "$case")

    [ -f "$case/system/controlDict.stage1" ] || \
        cp "$case/system/controlDict" "$case/system/controlDict.stage1"
    [ -f "$case/system/fvSolution.stage1" ] || \
        cp "$case/system/fvSolution" "$case/system/fvSolution.stage1"

    sed -i "s/^startFrom       startTime;/startFrom       latestTime;/; \
            s/^endTime         [0-9]*;/endTime         $END;/; \
            s/^writeInterval   [0-9]*;/writeInterval   $END;/" \
        "$case/system/controlDict"

    # accelerated outer loop: the textbook SIMPLE pairing, and T nearly
    # unrelaxed because on this case it is only weakly coupled back to momentum
    sed -i "s/^\( *\)p_rgh\( \+\)0\.7;/\1p_rgh\20.3;/; \
            s/^\( *\)U\( \+\)0\.3;/\1U\20.7;/; \
            s/^\( *\)T\( \+\)0\.5;/\1T\20.9;/; \
            s/^\( *\)relTol\( \+\)0\.01;/\1relTol\20.001;/" \
        "$case/system/fvSolution"

    for want in "p_rgh           0.3;" "U               0.7;" "T               0.9;"; do
        grep -q -- "$want" "$case/system/fvSolution" || \
            { echo "REFUSE: $name relaxation edit did not take ($want)"; exit 2; }
    done

    start=$(date +%s.%N)
    bash -c ". '$FOAM_BASHRC' >/dev/null 2>&1; cd '$case'; \
             buoyantBoussinesqSimpleFoam > log.buoyantBoussinesqSimpleFoam.stage2 2>&1"
    end=$(date +%s.%N)
    el=$(echo "$end - $start" | bc)
    printf 'stage2_wall_clock_s %.3f\n' "$el" >> "$case/COST.txt"
    printf '%s stage2 wall %.2f s\n' "$name" "$el"
done
