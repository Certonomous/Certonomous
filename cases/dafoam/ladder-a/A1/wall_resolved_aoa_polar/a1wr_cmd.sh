#!/usr/bin/env bash
# =============================================================================
# A1WR -- the in-container UNIT program. ONE unit = ONE container = ONE process
# = np 1 (A1WR_PREREGISTRATION.md Addendum A section 13.5) on ONE cpuset core
# (Addendum B section 14.2), OMP_NUM_THREADS=1 exported by the launcher
# (section 14.3).
#
# A FILE, NOT AN INLINE HEREDOC (the SO-1b lesson, carried from aoa_cmd.sh).
#
# Modes, selected by $A1WR_MODE:
#   PROBE      one point at the binding angle, FIXED iteration count: the
#              runScript runs at A1WR_PRIMAL_TOL=1e-30 so DAFoam can never
#              stop early, and controlDict endTime caps it at exactly the
#              registered 1,500. The primal is EXPECTED to end in DAFoam's
#              "Primal solution failed!" AnalysisError -- that is the
#              registered no-convergence-claim of section 5 Stage 1, not a
#              defect. After the primal, y+ is read FIELD-EXACTLY from the
#              written endTime state via the solver-hosted postProcess form
#              (the bare `postProcess` form reads y+ = 0 everywhere -- MEASURED
#              during instrument checks, the exact rule-3 blind-reader trap --
#              and is therefore FORBIDDEN here).
#   CONTINUED  the 19-point ascending continued sweep, 0/ reset ONCE.
#   COLD       one cold-control point, its own case tree, 0/ reset first.
#
# NEITHER MODE RETRIES, RELAXES, RE-TUNES OR DROPS A POINT (section 5 Stage 2).
# =============================================================================
set -uo pipefail

cd /mnt/case || { echo "A1WR_FATAL cannot cd /mnt/case"; exit 90; }

test -f /mnt/runScript.py            || { echo "A1WR_FATAL runScript absent at point of use"; exit 91; }
test -d 0.orig                       || { echo "A1WR_FATAL 0.orig absent at point of use"; exit 92; }
test -f constant/polyMesh/points.gz  || { echo "A1WR_FATAL mesh absent at point of use"; exit 93; }
test -n "${A1WR_MODE:-}"             || { echo "A1WR_FATAL A1WR_MODE unset"; exit 94; }
test -n "${A1WR_ALPHAS:-}"           || { echo "A1WR_FATAL A1WR_ALPHAS unset"; exit 94; }
test -n "${A1WR_TOL:-}"              || { echo "A1WR_FATAL A1WR_TOL unset"; exit 94; }
test -n "${A1WR_TMO:-}"              || { echo "A1WR_FATAL A1WR_TMO unset"; exit 94; }

mkdir -p /mnt/out || { echo "A1WR_FATAL cannot mkdir /mnt/out"; exit 95; }

# G-WALLTREAT clause 1, asserted AT THE POINT OF USE on the staged bytes:
grep -q '"useWallFunction": False,' /mnt/runScript.py \
  || { echo "A1WR_FATAL G-WALLTREAT: staged runScript does not carry useWallFunction False"; exit 98; }
echo "A1WR_WALLTREAT_SCRIPT_OK useWallFunction False present in staged runScript"

DECLARED=0
for A in $A1WR_ALPHAS; do DECLARED=$((DECLARED + 1)); done
FIRST_ALPHA=$(set -- $A1WR_ALPHAS; echo "$1")
echo "A1WR_UNIT mode=$A1WR_MODE declared=$DECLARED list=[$A1WR_ALPHAS] tol=$A1WR_TOL tmo=$A1WR_TMO omp=${OMP_NUM_THREADS:-UNSET} utc=$(date -u +%Y-%m-%dT%H%M%SZ)"

rm -rf 0 && cp -r 0.orig 0 || { echo "A1WR_FATAL cannot reset 0/ from 0.orig"; exit 96; }
echo "A1WR_COLD_START 0/ reset from 0.orig -- first point of this unit is cold"

MODE_FOR_LEDGER="$A1WR_MODE"
[ "$A1WR_MODE" = "PROBE" ] && MODE_FOR_LEDGER="COLD"   # runScript knows CONTINUED/COLD only

AOA_MODE="$MODE_FOR_LEDGER" \
AOA_ALPHAS="$A1WR_ALPHAS" \
AOA_POINTS_JSON=/mnt/out/points.json \
AOA_ALPHA0="$FIRST_ALPHA" \
AOA_LEDGER=/mnt/out/LEDGER.tsv \
A1WR_PRIMAL_TOL="$A1WR_TOL" \
timeout -k 60 "$A1WR_TMO" \
  python /mnt/runScript.py -task sweep > /mnt/out/sweep.log 2>&1
SRC=$?
echo "A1WR_SWEEP_RC rc=$SRC log=/mnt/out/sweep.log"

EXEC="$(grep -c '^AOA_POINT_END ' /mnt/out/sweep.log 2>/dev/null || true)"; EXEC="${EXEC:-0}"
CONV="$(grep -c 'satisfied the prescribed tolerance' /mnt/out/sweep.log 2>/dev/null || true)"; CONV="${CONV:-0}"
BCOK="$(grep -c 'BCType=nutLowReWallFunction' /mnt/out/sweep.log 2>/dev/null || true)"; BCOK="${BCOK:-0}"
echo "A1WR_COUNTS declared=$DECLARED point_end_markers=$EXEC converged_lines=$CONV walltreat_lines=$BCOK"

if [ "$A1WR_MODE" = "PROBE" ]; then
  # ---- the field-exact y+ read, on the state the FIXED 1,500 iterations left.
  # DAFoam does NOT rename a FAILED primal's time directory (measured in the
  # pre-freeze instrument check), so the endTime state sits at directory 1500,
  # written because controlDict writeInterval == endTime == 1500 for the probe.
  test -n "${A1WR_PP_SOLVER:-}" || { echo "A1WR_FATAL A1WR_PP_SOLVER unset for PROBE"; exit 94; }
  if [ ! -d 1500 ]; then
    echo "A1WR_PROBE_NO_ENDTIME_STATE dir 1500 absent -- the probe primal did not reach its fixed 1,500 iterations; y+ NOT MEASURED"
    exit 97
  fi
  "$A1WR_PP_SOLVER" -postProcess -func yPlus -time 1500 > /mnt/out/probe_yplus.log 2>&1
  PRC=$?
  echo "A1WR_PROBE_PP rc=$PRC solver=$A1WR_PP_SOLVER out=/mnt/out/probe_yplus.log"
  grep 'patch wing y+' /mnt/out/probe_yplus.log || echo "A1WR_PROBE_PP_NO_WING_LINE"
  # Probe success = the point ran its fixed iterations AND produced a parseable
  # y+ line. The GATE decision itself belongs to a1wr_stage1_gate.py on the host.
  if [ "$EXEC" = "1" ] && [ "$PRC" = "0" ] && grep -q 'patch wing y+' /mnt/out/probe_yplus.log; then
    echo "A1WR_PROBE_COMPLETE"
    exit 0
  fi
  echo "A1WR_PROBE_INCOMPLETE exec=$EXEC pp_rc=$PRC -- NOT a completion"
  exit 97
fi

if [ "$EXEC" -eq "$DECLARED" ]; then
  echo "A1WR_ALL_POINTS_EXECUTED declared=$DECLARED"
  exit 0
fi
echo "A1WR_TRUNCATED declared=$DECLARED executed=$EXEC -- NOT a completion"
exit 97
