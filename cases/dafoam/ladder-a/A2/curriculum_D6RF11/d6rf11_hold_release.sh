#!/usr/bin/env bash
# D6RF11 HOLD-AND-RELEASE.  It waits.  It never kills, signals or renices.
#
# TWO conditions, BOTH required, re-read every 30 s:
#   (1) A3GC-AR1 HAS LANDED -- pid 2766682 (docker client, cwd
#       /home/ubuntu/certonomous-runs/A3GC-AR1, container sleepy_golick, 4 ranks)
#       is no longer alive.  IT WATCHES THE PROCESS, NOT THE CLOCK: an estimated
#       05:30Z is not evidence that a run finished.
#   (2) THE SUPERVISOR'S GO EXISTS -- D6RF11_ARM.go present in the run root.
#       DELIBERATELY ABSENT at freeze: the pre-registration's section 0 disproved
#       the premise the launch ruling rested on (the R3 measurement is at the
#       IDENTICAL design, bit-for-bit, so there is no transfer gap to test), and
#       arming an auto-fire on a question already answered would spend compute on
#       the wrong measurement.  To arm:  touch <run root>/D6RF11_ARM.go
B=/home/ubuntu/certonomous-runs/CURRICULUM-D6RF11-a2-wing-fd-simplec-probe
RUNNER=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6RF11/d6rf11_run_probe.sh
AR1_PID=2766682
OUT="$B/D6RF11_HOLD.out"
GO="$B/D6RF11_ARM.go"

say() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >> "$OUT"; }

say "D6RF11_HOLD_ARMED runner=$RUNNER ar1_pid=$AR1_PID go_file=$GO go_present=$([ -f "$GO" ] && echo yes || echo NO-HOLDING)"

last=""
for i in $(seq 1 11520); do   # 96 h of waiting; it only ever stops waiting
  ar1_alive=$(kill -0 "$AR1_PID" 2>/dev/null && echo yes || echo no)
  go=$([ -f "$GO" ] && echo yes || echo no)
  state="ar1_alive=$ar1_alive go=$go"
  [ "$state" != "$last" ] && { say "D6RF11_HOLD_STATE $state"; last="$state"; }
  if [ "$ar1_alive" = "no" ] && [ "$go" = "yes" ]; then
    say "D6RF11_RELEASE both conditions met -- launching"
    {
      echo "D6RF11_LAUNCH_BEGIN $(date -u +%Y-%m-%dT%H:%M:%SZ)"
      echo "D6RF11_PREREG_AND_GRADER_COMMITTED_BEFORE_COMPUTE see cases/dafoam/ladder-a/A2/curriculum_D6RF11/"
      bash "$RUNNER"
      rc=$?                       # rc CAPTURED INSIDE this wrapper
      echo "D6RF11_RUNNER_RC=$rc"
      echo "D6RF11_LAUNCH_END $(date -u +%Y-%m-%dT%H:%M:%SZ) rc=$rc"
    } >> "$B/D6RF11_LAUNCH.out" 2>&1
    # grade it, on the path frozen with the registration
    {
      echo "D6RF11_AUTOGRADE_BEGIN $(date -u +%Y-%m-%dT%H:%M:%SZ)"
      python3 /home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6RF11/d6rf11_grade.py --base "$B"
      echo "D6RF11_AUTOGRADE_GRADER_EXIT=$?  (comparator exit status is NOT the verdict)"
      echo "D6RF11_AUTOGRADE_END $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    } >> "$B/D6RF11_AUTOGRADE.out" 2>&1
    say "D6RF11_HOLD_DONE"
    exit 0
  fi
  sleep 30
done
say "D6RF11_HOLD_GAVE_UP_WAITING after 96 h -- nothing was launched"
