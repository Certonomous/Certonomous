#!/bin/bash
# a1wrt2_seam_watch.sh -- READ-ONLY watcher for the A1WRT2 SEAM arm.
#
# WHAT THIS IS.  Sanaa ruled 2026-09-05: "The checks before the run are needed
# and justified.  However, not in an infinite loop.  Past some time the lab must
# take action (this applies to any team) and launch the run with its attached
# watcher to fix/debug and see what happens: act accordingly."  This is that
# watcher.  It is attached at the enqueue and it SURVIVES THE AGENT -- it is
# started under `setsid`, because an agent's watcher dies with the agent and a
# "waiting on my monitor" completion is the dead-agent tell.
#
# WHAT THIS IS NOT.  IT GRADES NOTHING.  The verdict on SEAM belongs to
# a1wrt2_grade.py and to no other reader.  Every line this file writes is
# prefixed OBSERVED, RC, CONTROL or WATCH -- never PASS, GATE REACHED, GATE
# FAIL, NOT A RESULT, BLOCKED or PENDING.  It touches nothing under the run
# root: every access is a read.
#
# THE HEADLINE IT EXISTS TO CATCH.  P-SEAMTIME predicts sweep.log's first
# anchored '^Time = ' is 4001 and its last 4200, meaning the restart loaded
# state.  If the first is 1, the producer resets the counter on a `latestTime`
# start too.  BOTH OUTCOMES ARE RESULTS.  This file records which happened and
# does not decide what it means.
#
# rc IS CAPTURED INSIDE THIS WRAPPER.  `setsid timeout cmd` exits 0 for every
# outcome, so an rc captured around the setsid line is meaningless.  This script
# records its own termination reason and rc in its own output, at the foot.

CASE=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A1/wall_resolved_alpha_tail
RUN_ROOT=/home/ubuntu/certonomous-runs/A1WRT2
SEAM_OUT="$RUN_ROOT/SEAM/out"
SWEEP="$SEAM_OUT/sweep.log"
RCFILE="$SEAM_OUT/rc"
LEDGER="$RUN_ROOT/ledger.txt"
MANIFEST="$RUN_ROOT/MANIFEST.json"
STATUS="$CASE/STATUS.SEAM"
QDIR=/home/ubuntu/Certonomous/verification/queue/dafoam
LAUNCHLOG=/home/ubuntu/Certonomous/verification/queue/LAUNCH_LOG.tsv
OUT="$CASE/a1wrt2_seam_watch.out"
CONTROL="$CASE/a1wrt2_seam_watch.control"

CEILING=2400          # 40 min hard ceiling.  SEAM's in-container deadline is
                      # 900 s; add the 60 s queue poll and ~94 s container
                      # start and this is generous and BOUNDED.  The watcher
                      # stops itself; it does not loop forever.
INTERVAL=10

say() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" >> "$OUT"; }

# --- the reader, defined once and used for BOTH the control and the real file
first_time() { grep -oE '^Time = [0-9.eE+-]+' "$1" 2>/dev/null | head -1 | sed 's/^Time = //'; }
last_time()  { grep -oE '^Time = [0-9.eE+-]+' "$1" 2>/dev/null | tail -1 | sed 's/^Time = //'; }
n_times()    { grep -cE '^Time = ' "$1" 2>/dev/null || echo 0; }

: > "$OUT"
say "WATCH start pid=$$ ppid=$PPID sid=$(ps -o sid= -p $$ 2>/dev/null | tr -d ' ')"
say "WATCH arm=SEAM ONLY.  TAIL is not watched and does not move on this row."
say "WATCH run_root=$RUN_ROOT sweep=$SWEEP"
say "WATCH ceiling=${CEILING}s interval=${INTERVAL}s -- bounded, not an infinite loop"

# --- PLANTED CONTROL (CLAUDE.md rule 3).  A zero from a reader not shown able
# --- to see a non-zero is not evidence.  Before this watcher is allowed to
# --- report "no Time line yet", its OWN reader is shown a Time line it must
# --- find, and a decoy it must NOT find.
{
  echo "Create time = 0.01 s"
  echo "Time = 4001"
  echo "  not a time line: Time = 9999 indented, must NOT be read as anchored"
  echo "Time = 4200"
  echo "End"
} > "$CONTROL"
CF="$(first_time "$CONTROL")"; CL="$(last_time "$CONTROL")"; CN="$(n_times "$CONTROL")"
say "CONTROL planted first=$CF last=$CL count=$CN (expected first=4001 last=4200 count=2)"
if [ "$CF" = "4001" ] && [ "$CL" = "4200" ] && [ "$CN" = "2" ]; then
  say "CONTROL PASS -- this reader is shown able to see an anchored Time line and to reject an indented decoy.  Its later zeros are therefore evidence."
else
  say "CONTROL REFUSED -- the reader could not see the planted line.  THIS WATCHER'S ZEROS ARE NOT EVIDENCE.  Exiting rc=2 rather than reporting a zero it cannot defend."
  say "WATCH end reason=CONTROL_REFUSED rc=2"
  exit 2
fi

# --- the observation loop
t0=$(date +%s)
seen_root=0; seen_manifest=0; seen_sweep=0; seen_first=0; seen_rc=0; reason=CEILING; rc=1
while :; do
  now=$(date +%s); el=$(( now - t0 ))
  [ "$el" -ge "$CEILING" ] && { reason=CEILING; rc=3; break; }

  if [ "$seen_root" = 0 ] && [ -d "$RUN_ROOT" ]; then
    seen_root=1; say "OBSERVED run_root APPEARED after ${el}s -- the stager has started"
  fi
  if [ "$seen_manifest" = 0 ] && [ -s "$MANIFEST" ]; then
    seen_manifest=1; say "OBSERVED MANIFEST.json written ($(wc -c < "$MANIFEST") bytes) -- G-IMG/G-FREEZE now have their input"
  fi
  if [ "$seen_sweep" = 0 ] && [ -f "$SWEEP" ]; then
    seen_sweep=1; say "OBSERVED sweep.log APPEARED after ${el}s -- the container is running"
  fi

  if [ "$seen_first" = 0 ] && [ -s "$SWEEP" ]; then
    f="$(first_time "$SWEEP")"
    if [ -n "$f" ]; then
      seen_first=1
      say "OBSERVED FIRST ANCHORED TIME = $f"
      if [ "$f" = "4001" ]; then
        say "OBSERVED P-SEAMTIME first-value MATCHES the registered prediction (4001): the restart LOADED STATE.  Grading belongs to a1wrt2_grade.py, not to this reader."
      elif [ "$f" = "1" ]; then
        say "OBSERVED P-SEAMTIME first-value is 1, NOT 4001: on this evidence the producer resets the counter on a latestTime start too.  THIS IS A RESULT, NOT A FAILURE TO WORK AROUND -- it is the mechanism SEAM was bought to measure, and 14 prior points left it open.  Expect G-COMPLETE to fail SEAM and the TAIL precondition to refuse at rc=7 at <= 10.0 core-min.  Grading belongs to a1wrt2_grade.py."
      else
        say "OBSERVED P-SEAMTIME first-value is $f -- NEITHER 4001 NOR 1.  Third outcome, unregistered.  Reported, not interpreted."
      fi
    fi
  fi

  if [ -s "$RCFILE" ]; then
    seen_rc=1; reason=PRODUCER_RC_WRITTEN; rc=0; break
  fi

  sleep "$INTERVAL"
done

el=$(( $(date +%s) - t0 ))
say "WATCH loop ended after ${el}s reason=$reason"

# --- final observation, taken once, after the loop
if [ -s "$SWEEP" ]; then
  say "OBSERVED sweep.log final: first=$(first_time "$SWEEP") last=$(last_time "$SWEEP") anchored_count=$(n_times "$SWEEP") bytes=$(wc -c < "$SWEEP")"
  say "OBSERVED sweep.log End line present: $(grep -c '^End' "$SWEEP" 2>/dev/null)"
else
  say "OBSERVED sweep.log ABSENT OR EMPTY at loop end (reader control PASSED above, so this zero is evidence)"
fi
[ -s "$RCFILE" ] && say "RC producer rc=$(cat "$RCFILE") (written by a1wrt2_run_arm.sh:run_seam_arm, captured inside the launcher immediately after its own docker run -- never recomputed from markers)"
[ -s "$LEDGER" ] && say "OBSERVED ledger.txt: $(tr '\n' ' | ' < "$LEDGER")"
[ -s "$STATUS" ] && say "OBSERVED STATUS.SEAM: $(tr '\n' ' | ' < "$STATUS")"
say "OBSERVED queue drop dir now holds: $(ls "$QDIR"/*.json 2>/dev/null | xargs -r -n1 basename | tr '\n' ' ')"
say "OBSERVED launched/ holds A1WRT2_SEAM: $(ls "$QDIR"/launched/A1WRT2_SEAM*.json 2>/dev/null | xargs -r -n1 basename | tr '\n' ' ')"
[ -f "$LAUNCHLOG" ] && say "OBSERVED LAUNCH_LOG last A1WRT2_SEAM row: $(grep 'A1WRT2_SEAM' "$LAUNCHLOG" 2>/dev/null | tail -1)"

say "WATCH end reason=$reason rc=$rc  (this rc is THIS WATCHER'S, captured inside this wrapper, and is NOT the producer's rc and NOT a verdict on SEAM)"
exit "$rc"
