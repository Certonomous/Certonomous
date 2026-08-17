#!/usr/bin/env bash
# rewrite_precision.sh -- stage 3: rewrite the converged fields at full ASCII
# precision.  F14 rung K0c.
#
#   ./rewrite_precision.sh <case-directory> [more cases ...]
#
# THE MEASUREMENT THAT FORCED THIS
# --------------------------------
# The cross-check that guards the snGrad trap compares the wall flux built from
# the raw T cells against the same integral recomputed by
# scripts/heat_balance.py.  On Ra1e3_m32 the two differed by 0.0058 percent --
# far above the 1e-6 the check demands, and with no plausible physical cause on
# an orthogonal uniform mesh.
#
# The cause is arithmetic, not physics.  These cases carry an absolute
# temperature around 300 K while the whole driving difference at Ra = 1e3 is
# 0.0109 K, and the near-wall difference the estimator actually consumes,
# T_wall - T_first_cell, is about 1.9e-4 K.  `writePrecision 10` writes
# 300.0054408: ten significant figures of a 300 K number is 1e-7 of absolute
# resolution, which leaves the 1.9e-4 K quantity with barely three good digits.
# Averaged over 32 wall faces that is ~1e-4 relative, which is what was seen.
#
# The solver's own in-pass integral does not suffer this: it is computed in
# double precision inside the run and only its RESULT is printed.  So the
# disagreement was an artefact of the file format, and the honest fix is to
# stop truncating rather than to widen the tolerance until the truncation fits
# inside it.  writePrecision 16 costs nothing and removes the artefact.
#
# This does NOT change any graded number materially: at 1e-4 relative the
# truncation is a hundredth of the tightest band on the gate.  It changes what
# the cross-check is able to see, which is the point of the cross-check.
#
# The run is continued from latestTime; the case is already converged so
# residualControl stops it almost at once and the write is the only real work.
set -eo pipefail

FOAM_BASHRC=${FOAM_BASHRC:-/usr/lib/openfoam/openfoam2606/etc/bashrc}

for case in "$@"; do
    case=$(readlink -f "$case")
    name=$(basename "$case")
    latest=$(bash -c ". '$FOAM_BASHRC' >/dev/null 2>&1; cd '$case'; foamListTimes | tail -1")
    end=$((latest + 200))

    sed -i "s/^startFrom       startTime;/startFrom       latestTime;/; \
            s/^endTime         [0-9]*;/endTime         $end;/; \
            s/^writeInterval   [0-9]*;/writeInterval   $end;/; \
            s/^writePrecision  [0-9]*;/writePrecision  16;/" \
        "$case/system/controlDict"
    grep -q "writePrecision  16;" "$case/system/controlDict" || \
        { echo "REFUSE: $name writePrecision edit did not take"; exit 2; }

    start=$(date +%s.%N)
    bash -c ". '$FOAM_BASHRC' >/dev/null 2>&1; cd '$case'; \
             buoyantBoussinesqSimpleFoam > log.buoyantBoussinesqSimpleFoam.stage3 2>&1"
    fin=$(date +%s.%N)
    el=$(echo "$fin - $start" | bc)
    printf 'stage3_wall_clock_s %.3f\n' "$el" >> "$case/COST.txt"
    printf '%s stage3 wall %.2f s (from t=%s)\n' "$name" "$el" "$latest"
done
