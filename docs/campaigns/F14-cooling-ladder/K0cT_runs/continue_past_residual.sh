#!/usr/bin/env bash
# continue_past_residual.sh -- F14 rung K0c-T.
#
#   ./continue_past_residual.sh <endTime> <case> [more ...]
#
# WHY.  T_hi_f, T_lo_f and M_hi_f_LS all STOPPED on their own `residualControl`
# -- 6688, 6237 and 10185 iterations -- and each then met the standing
# peak-to-peak criterion in its last 400 iterations by two to three orders of
# magnitude.  That is exactly the shape docs/physics_rules.yaml warns about:
# "the residuals stopped moving" is not the criterion, and a run that STOPS on
# residuals can stop before a slow instability has grown.  The COARSE hi-Ra mesh
# in this same rung does NOT reach steady state at all, and it took 140000
# iterations to establish that.  So the residual stop is REMOVED here and the
# fine meshes are run far past it, governed by the graded-quantity criterion
# alone.  If the answer moves, the first stage was a premature stop and this
# script found it; if it does not, the graded value is the same number arrived
# at from a longer run and the residual stop cost nothing.
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
    # the residual stop, removed rather than loosened, and recorded here
    python3 - "$case/system/fvSolution" <<'PY'
import re, sys
p = sys.argv[1]
s = open(p).read()
body = [
    "residualControl",
    "    {",
    "        // residual stop REMOVED for the continuation stage; see",
    "        // continue_past_residual.sh.  Convergence is judged by the",
    "        // graded-quantity peak-to-peak criterion, never by these.",
    "        p_rgh           1e-30;",
    "        U               1e-30;",
    "        T               1e-30;",
    '        "(k|omega|epsilon)" 1e-30;',
    "    }",
]
new = re.sub(r"residualControl\s*\{[^}]*\}", "\n".join(body), s, count=1)
if new == s and "1e-30" not in s:
    sys.exit("REFUSE: residualControl block not found in " + p)
open(p, "w").write(new)
PY
    n=2; while [ -f "$case/log.buoyantBoussinesqSimpleFoam.stage$n" ]; do n=$((n+1)); done
    foam "$case" "buoyantBoussinesqSimpleFoam > log.buoyantBoussinesqSimpleFoam.stage$n 2>&1"
    end=$(date +%s.%N); el=$(echo "$end - $start" | bc)
    printf '%s  stage%s wall %.2f s\n' "$name" "$n" "$el"
    printf 'case %s\nstage%s_wall_clock_s %.3f\ncores 1\nstage%s_core_minutes %.4f\n' \
        "$name" "$n" "$el" "$n" "$(echo "$el / 60" | bc -l)" >> "$case/COST.txt"
done
