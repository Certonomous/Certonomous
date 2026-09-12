#!/bin/bash
# r2_fine SNAPPY HEADROOM GUARD -- arms the fleet memory rule ON A RUNNING JOB.
#
# THE GAP THIS CLOSES: the fleet rule (predicted peak <= available - 4 GiB) is
# evaluated ONCE, AT LAUNCH, and nothing re-evaluates it while a long build runs.
# r2_fine passed its gate honestly at 01:28Z with available 15 GiB.  By 01:53Z
# available was 11 and snappy was still in CASTELLATION with the LAYER PHASE --
# where the peak occurs -- entirely ahead of it.  A gate that passes at t=0 tells
# you very little about t=45min.
#
# WHAT IT KILLS, AND WHY THAT ONE: ONLY r2_fine's snappyHexMesh and its
# /usr/bin/time parent.  Both are OURS.  If something on this box must die
# tonight it is the 25-minute-old castellation, not MRF fine at ~6,900 of 8,000
# iterations, not ansys rhoCentralFoam at three and a half days, not the other
# cfd lane's SUBOFF_A1, and not T-family's 34-hour buoyant run.  A kernel OOM
# picks by score.  WE PICK BY VALUE.
#
# IDENTIFICATION IS BY CWD, RE-CONFIRMED AT THE MOMENT OF THE KILL, NEVER BY
# PATTERN.  pkill matches its own invoking command line, and tonight has already
# produced three cases of a label being right while its referent was wrong --
# including, ten minutes ago, four simpleFoam ranks I briefly took for my own
# coarse solve that were in fact ANOTHER LANE's SUBOFF_A1 job.  My coarse ranks
# hold 0.11 GiB each; SUBOFF's hold 1.2.  Reading the cwd is what caught it.
set -u
R=/home/ubuntu/Certonomous/verification/runs/navier_class/DRIVAER/r2_fine
SNAPPY=2625466          # snappyHexMesh,  cwd asserted == $R below
TIMER=2625465           # /usr/bin/time parent, cwd asserted == $R below
SERIES="$R/HEADROOM_SERIES.tsv"

# --- TRIGGERS.  Deliberately ABOVE the line they protect, because a 10 s sample
#     against a layer phase that can allocate in seconds must fire with room to
#     spare.  The fleet rule's floor is 4 GiB; this fires at 5.
KILL_AVAIL_GIB=5        # available below this -> kill, do not wait for recovery
KILL_RSS_GIB=8.5        # snappy RSS above this WHILE available < 6 -> kill
KILL_RSS_AVAIL_GIB=6

confirm_cwd () {  # confirm_cwd <pid> -- returns 0 only if it is still OUR process
  [ -d "/proc/$1" ] || return 1
  [ "$(readlink /proc/$1/cwd 2>/dev/null)" = "$R" ] || return 1
  tr '\0' ' ' < /proc/$1/cmdline 2>/dev/null | grep -q snappyHexMesh || return 1
  return 0
}

printf 'utc\tavail_GiB\tsnappy_RSS_GiB\tstage\n' > "$SERIES"
while :; do
  # snappy gone on its own -> the build finished or died; the guard's job is over
  [ -d "/proc/$SNAPPY" ] || { echo "$(date -u +%FT%TZ) snappy $SNAPPY no longer running; guard stands down" >> "$SERIES.log"; exit 0; }

  avail=$(free -m | awk '/^Mem:/{printf "%.2f", $7/1024}')
  rssk=$(awk '/^VmRSS/{print $2}' /proc/$SNAPPY/status 2>/dev/null)
  rss=$(awk -v r="${rssk:-0}" 'BEGIN{printf "%.2f", r/1048576}')
  stage=$(tail -1 "$R/log.snappyHexMesh" 2>/dev/null | cut -c1-60 | tr '\t' ' ')
  printf '%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$avail" "$rss" "$stage" >> "$SERIES"

  fire=""
  awk -v a="$avail" -v k="$KILL_AVAIL_GIB" 'BEGIN{exit !(a<k)}' && fire="available ${avail} GiB < ${KILL_AVAIL_GIB} GiB"
  awk -v r="$rss" -v k="$KILL_RSS_GIB" -v a="$avail" -v ka="$KILL_RSS_AVAIL_GIB" 'BEGIN{exit !(r>k && a<ka)}' \
      && fire="snappy RSS ${rss} GiB > ${KILL_RSS_GIB} GiB while available ${avail} GiB < ${KILL_RSS_AVAIL_GIB} GiB"

  if [ -n "$fire" ]; then
    {
      echo "TRIGGER FIRED $(date -u +%FT%TZ): $fire"
      echo "stage at trigger: $stage"
    } >> "$SERIES.log"
    if confirm_cwd "$SNAPPY"; then
      kill -TERM "$SNAPPY" 2>/dev/null
      sleep 10
      [ -d "/proc/$SNAPPY" ] && confirm_cwd "$SNAPPY" && kill -KILL "$SNAPPY" 2>/dev/null
      echo "killed snappy $SNAPPY (cwd re-confirmed as $R at kill time)" >> "$SERIES.log"
    else
      echo "REFUSED TO KILL $SNAPPY: cwd/cmdline no longer match $R -- pid may have been reused. NOTHING KILLED." >> "$SERIES.log"
    fi
    if [ -d "/proc/$TIMER" ] && [ "$(readlink /proc/$TIMER/cwd 2>/dev/null)" = "$R" ]; then
      kill -TERM "$TIMER" 2>/dev/null
      echo "killed timer parent $TIMER (cwd confirmed)" >> "$SERIES.log"
    else
      echo "timer parent $TIMER not killed: cwd did not confirm" >> "$SERIES.log"
    fi
    exit 3
  fi
  sleep 10
done
