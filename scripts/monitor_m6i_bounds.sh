#!/usr/bin/env bash
# monitor_m6i_bounds.sh -- LC-1 / LC-2 readout for the M6I levels.
#
#   usage: monitor_m6i_bounds.sh [L1 L2 L3 ...]
#
# REGISTERED BY verification/campaign/M6I_R1_SOLVE_PREREGISTRATION.md ADDENDUM 5 section A5.2.
#
# WHY THIS EXISTS.  Sanaa's stop rule is "residual growth or a field outside bounds -> stop".
# With a bounding fvOption active the field is NEVER outside bounds -- it is held AT the
# bound -- so the trigger cannot fire.  L2 ran 668 iterations with up to 99.72 % of its cells
# pinned at Tmax and nuTilda at 3.08e43 before an FPE stopped it by accident.  A limiter
# doing no work is a safety net; a limiter pinning a tenth of the domain IS the divergence.
#
# THIS SCRIPT READS LOGS AND PRINTS.  IT LAUNCHES NOTHING AND IT KILLS NOTHING.
set -u
RUNS="$(cd "$(dirname "$0")/../verification/runs/M6I_runs" && pwd)"
THRESH_PCT=2.0        # A5.2 LC-1
THRESH_RUNLEN=20      # A5.2 LC-1: consecutive reported iterations above THRESH_PCT
NUTILDA_MAX=1e6       # A5.2 LC-2

for L in "${@:-L1 L2 L3}"; do
  C="$RUNS/$L"
  [ -d "$C" ] || { echo "$L: no such level"; continue; }
  LOGS=$(ls "$C"/log.rhoSimpleFoam "$C"/log.rhoSimpleFoam.resume.* 2>/dev/null)
  [ -n "$LOGS" ] || { echo "$L: no stage-2 log yet"; continue; }
  echo "=== $L ==="
  # LC-1
  cat $LOGS | grep -oE "Type=(Upper|Lower), LimitedCells=[0-9]+, CellsPercent=[0-9.]+" \
  | awk -F'CellsPercent=' -v t="$THRESH_PCT" -v R="$THRESH_RUNLEN" '
      { p=$2+0; n++; if(p>mx)mx=p
        if(p>t){run++; if(run>mxrun)mxrun=run} else run=0 }
      END{ if(n==0){print "  LC-1: no limitTemperature lines"; exit}
           printf "  LC-1: peak CellsPercent %.2f %% over %d reported lines; longest run above %.1f %% = %d (threshold %d)\n", mx, n, t, mxrun, R
           if(mxrun>=R) print "  LC-1: **BREACHED** -> NOT A RESULT, BOUND-CONCEALED DIVERGENCE"
           else print "  LC-1: within threshold" }'
  # LC-2
  NB=$(cat $LOGS | grep -c "bounding nuTilda" || true)
  if [ "${NB:-0}" = "0" ]; then
    echo "  LC-2: zero 'bounding nuTilda' lines"
  else
    echo "  LC-2: $NB 'bounding nuTilda' lines; worst:"
    cat $LOGS | grep "bounding nuTilda" \
      | awk -v m="$NUTILDA_MAX" '{for(i=1;i<=NF;i++) if($i=="max:"){v=$(i+1)+0; if(v>w)w=v}}
          END{printf "        max nuTilda %g (LC-2 threshold %g) -> %s\n", w, m+0,
                     (w>m+0 ? "**BREACHED** -> NOT A RESULT" : "within threshold")}'
  fi
  # context
  echo "  iterations in stage-2 log(s): $(cat $LOGS | grep -cE '^Time = ')"
  echo "  last Ux initial residual: $(cat $LOGS | grep 'Solving for Ux' | tail -1 | grep -oE 'Initial residual = [0-9.e+-]+')"
done
