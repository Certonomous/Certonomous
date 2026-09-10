#!/usr/bin/env bash
# =============================================================================
# A3FL2 PRE-FLIGHT EXERCISE -- CONTENTION GATE (operational; MEASUREMENT ONLY)
#
# CITATIONS ARE BY CONTENT, NOT BY LINE NUMBER, AND DELIBERATELY SO.  a3fl2_exercise.sh
# is under CONCURRENT amendment by another lane (it has just gained core-minute accounting
# and an EXERCISE_CAP_CORE_MIN=48 cumulative cap-stop), and every line number in an earlier
# revision of this header went stale the moment that landed -- the self-detach guard moved
# from line 45 to line 69.  A line number written into a file someone else is editing
# schedules its own next correction, so the anchors below are symbols and code fragments,
# which survive the edit.
#
# WHY THIS EXISTS.  `a3fl2_exercise.sh` runs three smokes at 4 MPI ranks behind a
# HARD 180 s per-leg deadline (its `RANKS=4` / `DEADLINE_S=180` settings and the `timeout -k $KILL_GRACE_S $DEADLINE_S mpirun` line).  The deadline is
# WALL time, so contention does not make a leg slower -- it makes the leg TRIP.
# A tripped leg exits 124, which the GREEN criterion (its `{ [ "$rc" = "0" ] && [ "$invalid" = "no" ]; } || GREEN=no` line;
# A3FL2_PREREGISTRATION.md §13) reads as rc != 0 and therefore NOT GREEN --
# INDISTINGUISHABLE from a genuine config failure.  A false NOT_GREEN costs the
# whole exercise spend and teaches nothing.
#
# MEASURED, on the exercise's own rung-3 source case
# (/home/ubuntu/certonomous-runs/A3-rung3-n52/rung3_stage1.log, 4 ranks,
# coloring file READ not recomputed):
#     26 primal outer iters      ExecutionTime  30.97 s
#     dRdWTPC assembly  0/1355   ExecutionTime  49.24 s
#     dRdWTPC assembly 1354/1355 ExecutionTime 149.84 s
# i.e. ~150 s of MANDATORY pre-GMRES work UNCONTENDED against a 180 s deadline --
# about 15 % margin -- and the 30-iteration gmresMaxIters smoke cap
# (its `SMOKE_GMRES_MAXITERS=30`) caps the GMRES solve, NOT that assembly.
#
# THE RELEASE CONDITION IS A CONJUNCTION, and this is the correction that matters.
# An earlier revision of this file gated on the D6RF10 R3 container alone.  That was
# WRONG, and its own comment conceded it.  R3's four ranks are only four of roughly
# twelve busy cores on this 16-vCPU box: when R3 drains, load falls from ~25 to only
# ~21, still oversubscribed ~1.3x by FOREIGN-family solvers that have nothing to do
# with D6RF10 and do not stop when it does.  Gating on R3 alone would release into
# very nearly the same contention this gate exists to avoid.  Both halves must hold:
#     (A) the D6RF10 R3 container is no longer running, AND
#     (B) the box actually has the cores the exercise needs (loadavg1 <= LOAD_MAX).
#
# HOW LOAD_MAX=8 ON 16 vCPUs WAS CHOSEN (derived, not asserted).  The exercise needs
# 4 ranks running at FULL SPEED because its deadline is wall time.  The naive reading
# of "4 free cores" is loadavg1 <= 12, and it is wrong three times over:
#   (a) the 4 ranks the exercise is about to ADD are not in the reading at release
#       time -- releasing at 12 gives 16 the instant the legs start, i.e. exactly
#       saturated, with zero headroom;
#   (b) loadavg1 is a ~60 s EWMA and therefore LAGS -- it under-reports a foreign
#       job that has just started;
#   (c) the measured margin is only ~15 % (153 s of work against 180 s), so even
#       mild core sharing trips the deadline.
# Subtracting the exercise's own 4 ranks from 12 gives 8, which leaves 4 cores of
# genuine buffer against (b) and (c).  Hence LOAD_MAX=8.0.
#
# The 3-consecutive-read requirement applies to the CONJUNCTION, not to either half
# alone, so a momentary dip in one while the other is unsatisfied cannot release the
# gate.  Three reads 30 s apart span 60 s -- one full time constant of loadavg1 --
# so a stale or transient reading cannot on its own satisfy the gate either.
#
# WHAT IS DELIBERATELY NOT TOUCHED.  DEADLINE_S (180 s) and the GREEN criterion are
# REGISTERED (A3FL2_PREREGISTRATION.md §13, the GREEN criterion) and are not this file's to relax.
# Relaxing the deadline would change what rc a leg produces, which is changing the
# gate through the back door.  This file changes WHEN the exercise runs, never WHAT
# it measures or how it is judged.  `a3fl2_exercise.sh` is NOT EDITED by this file
# (a concurrent lane is amending it for core-minute accounting).
#
# D6RF10 IS NEVER TOUCHED.  The only interaction anywhere in this file is
# `docker inspect --format '{{.State.Running}}'`, which is read-only.  The container,
# its run root and its processes are never written to, signalled or stopped.
#
# THIS FILE GRADES NOTHING AND FREEZES NOTHING.  No grader staged, no PERMISSION line
# read, no G-FREEZE limb, no verdict declared.  The GREEN call and the freeze are the
# dafoam-supervisor's (A3FL2_PREREGISTRATION.md §13, freeze order).
#
# rc DISCIPLINE (L "setsid parent returns zero").  The plain invocation re-execs THIS
# script under setsid, fully detached (own session, PPID=1, stdin /dev/null), and the
# parent's `exit 0` means ONLY "armed".  Every rc that matters -- GATE_RC and
# EXERCISE_RC -- is captured INSIDE the detached child.  Nothing is captured around
# the setsid line.
#
# FLEET-DEATH SURVIVAL.  The child is session-detached with PPID=1, so an agent or
# fleet death does not reap it; the exercise's legs run as `docker run -d`
# (its `sudo -n docker run -d --name "$name"` line) and outlive every shell.
#
# COST (rule 12 / DAFOAM_CHARTER §12, basis cores x wall for the whole clock).  The
# gate is a 30 s poll loop: ~0 core-min.  The exercise it starts is the spend, and it
# is the exercise's own line at A3FL2_PREREGISTRATION.md §13, now enforced in-flight by that
# script's own EXERCISE_CAP_CORE_MIN=48 cumulative cap-stop.
# =============================================================================
set -u

GATE_TARGET="d6rf10_R3_20260910T031209Z_953457"   # binding rung; READ-ONLY, never touched
NCPU=16                                            # measured: nproc on this box
LOAD_MAX=8.0                                       # half (B); derivation in the header
POLL_S=30                                          # poll interval
CONSEC_FREE=3                                      # consecutive reads of the CONJUNCTION
MAX_WAIT_S=21600                                   # 6 h ceiling (D6RF10 R3's own hard stop ~07:54Z)
HEARTBEAT_EVERY=10                                 # heartbeat every 10 polls (~5 min)
EX=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A3/curriculum_A3FL2/a3fl2_exercise.sh
EXERCISE_ROOT=/home/ubuntu/certonomous-runs/A3FL2-PREFLIGHT-EXERCISE
LOCK=/home/ubuntu/certonomous-runs/.a3fl2_exercise_gate.lock

# --- SELF-DETACH ------------------------------------------------------------
if [ -z "${A3FL2_GATE_DETACHED:-}" ]; then
  export A3FL2_GATE_DETACHED=1
  A3FL2_GATE_LOG="/home/ubuntu/certonomous-runs/a3fl2_exercise_gate_$(date -u +%Y%m%dT%H%M%SZ)_$$.log"
  export A3FL2_GATE_LOG
  # arm-time refusals: fail NOW, not in six hours.
  [ -x "$EX" ]            || { echo "A3FL2_GATE_REFUSE: exercise not executable: $EX" >&2; exit 3; }
  [ -e "$EXERCISE_ROOT" ] && { echo "A3FL2_GATE_REFUSE: exercise root already exists ($EXERCISE_ROOT) -- archive it by mv first." >&2; exit 3; }
  if [ -e "$LOCK" ] && kill -0 "$(cat "$LOCK" 2>/dev/null)" 2>/dev/null; then
    echo "A3FL2_GATE_REFUSE: another gate is already armed (pid $(cat "$LOCK"))." >&2; exit 3
  fi
  setsid bash "$0" "$@" > "$A3FL2_GATE_LOG" 2>&1 < /dev/null &
  echo "A3FL2_GATE_ARMED child_pid=$! gate_log=$A3FL2_GATE_LOG"
  echo "  release requires BOTH: $GATE_TARGET not running AND loadavg1 <= $LOAD_MAX on $NCPU vCPUs,"
  echo "  held for $CONSEC_FREE consecutive reads ${POLL_S}s apart."
  echo "  This exit 0 means ARMED ONLY. GATE_RC and EXERCISE_RC are written INSIDE the child."
  exit 0
fi

# --- detached child ---------------------------------------------------------
echo $$ > "$LOCK"
trap '_rc=$?; echo "GATE_RC=$_rc $(date -u +%FT%TZ)"; rm -f "$LOCK"' EXIT
# A gate stopped by a signal must SAY SO.  Without these, the EXIT trap reports the rc
# of whatever ran last -- a SIGTERM'd gate logged GATE_RC=0, which reads as a clean
# exit when in fact NOTHING was launched.  A false clean exit is worse than a loud
# failure.  (Verified in practice 2026-09-10T03:56:27Z: sig=TERM, GATE_RC=143.)
on_sig() {
  echo "A3FL2_GATE_KILLED_BY_SIGNAL $(date -u +%FT%TZ) sig=$1 waited_s=$(( $(date -u +%s) - ${T0:-$(date -u +%s)} ))"
  echo "  The gate was stopped BEFORE release. NO exercise was started. D6RF10 untouched."
  exit 143
}
trap 'on_sig TERM' TERM; trap 'on_sig INT' INT; trap 'on_sig HUP' HUP

echo "A3FL2_GATE_START $(date -u +%FT%TZ) pid=$$ ppid=$PPID sid=$(ps -o sid= -p $$ | tr -d ' ')"
echo "  RELEASE CONDITION (conjunction, both halves, $CONSEC_FREE consecutive reads):"
echo "    (A) container $GATE_TARGET NOT running"
echo "    (B) loadavg1 <= $LOAD_MAX on $NCPU vCPUs  [4 ranks needed + 4 cores buffer; see header]"
echo "  poll_s=$POLL_S max_wait_s=$MAX_WAIT_S exercise=$EX"
echo "  D6RF10 IS NEVER TOUCHED: the only interaction is a read-only docker inspect."

T0=$(date -u +%s); free_streak=0; released=no; polls=0
unmet_A=0; unmet_B=0; unmet_both=0; last_running="?"; last_load="?"
while :; do
  now=$(date -u +%s); waited=$((now - T0)); polls=$((polls + 1))

  running="$(sudo -n docker inspect --format '{{.State.Running}}' "$GATE_TARGET" 2>/dev/null)"
  load1="$(cut -d' ' -f1 /proc/loadavg)"
  last_running="${running:-<absent>}"; last_load="$load1"

  # (A) container drained.  Empty output (container gone) also satisfies A.
  if [ "$running" = "true" ]; then okA=no; else okA=yes; fi
  # (B) box has the cores.  awk does the float compare bash cannot.
  if awk -v l="$load1" -v t="$LOAD_MAX" 'BEGIN{exit !(l<=t)}'; then okB=yes; else okB=no; fi

  if [ "$okA" = "yes" ] && [ "$okB" = "yes" ]; then
    free_streak=$((free_streak + 1))
    echo "GATE_POLL $(date -u +%FT%TZ) waited_s=$waited A=ok(running='${running:-<absent>}') B=ok(loadavg1=$load1<=$LOAD_MAX) streak=$free_streak/$CONSEC_FREE"
    if [ "$free_streak" -ge "$CONSEC_FREE" ]; then released=yes; break; fi
  else
    # the streak is on the CONJUNCTION: either half failing resets it.
    if [ "$free_streak" -gt 0 ]; then
      echo "GATE_STREAK_RESET $(date -u +%FT%TZ) waited_s=$waited A=$okA B=$okB (loadavg1=$load1) -- conjunction broken, streak back to 0"
    fi
    free_streak=0
    if   [ "$okA" = "no" ] && [ "$okB" = "no" ]; then unmet_both=$((unmet_both + 1))
    elif [ "$okA" = "no" ]; then unmet_A=$((unmet_A + 1))
    else unmet_B=$((unmet_B + 1)); fi
  fi

  if [ $((polls % HEARTBEAT_EVERY)) -eq 1 ]; then
    echo "GATE_HEARTBEAT $(date -u +%FT%TZ) waited_s=$waited A_container_running='${running:-<absent>}' B_loadavg1=$load1 (need <=$LOAD_MAX) streak=$free_streak/$CONSEC_FREE"
  fi

  if [ "$waited" -ge "$MAX_WAIT_S" ]; then
    echo "A3FL2_GATE_TIMEOUT $(date -u +%FT%TZ) waited_s=$waited polls=$polls"
    echo "  WHICH HALF WAS UNSATISFIED (poll counts over the whole wait):"
    echo "    (A) container still running, box otherwise free : $unmet_A polls"
    echo "    (B) container drained, but loadavg1 > $LOAD_MAX  : $unmet_B polls"
    echo "    (A+B) both unsatisfied                          : $unmet_both polls"
    echo "  last reading: container_running='$last_running'  loadavg1=$last_load  (threshold $LOAD_MAX on $NCPU vCPUs)"
    if [ "$unmet_B" -gt "$unmet_A" ] && [ "$unmet_B" -gt "$unmet_both" ]; then
      echo "  DOMINANT CAUSE: half (B) -- CROSS-FAMILY SATURATION. D6RF10 R3 drained but foreign"
      echo "  solvers held the box above the threshold. This is a FINDING about cross-family"
      echo "  compute contention, and it is the finding the supervisor asked for."
    elif [ "$unmet_A" -gt "$unmet_B" ] && [ "$unmet_A" -gt "$unmet_both" ]; then
      echo "  DOMINANT CAUSE: half (A) -- D6RF10 R3 outlived its own 16905 s deadline."
    else
      echo "  DOMINANT CAUSE: both halves together -- the box never drained at all."
    fi
    echo "  NOT LAUNCHING, DELIBERATELY. Launching anyway would spend the exercise's core-minutes"
    echo "  on legs that trip the 180 s wall deadline for a CONTENTION reason and report a FALSE"
    echo "  NOT_GREEN -- a wasted spend that teaches nothing. A non-launch with zero compute spent"
    echo "  is the honest outcome and is itself the result. Nothing is frozen; nothing is graded."
    exit 4
  fi

  # `sleep N & wait` rather than a foreground `sleep`: bash DEFERS trap handling until a
  # foreground command returns, which made a SIGTERM take 26 s to be acted on (measured
  # 2026-09-10, kill at 03:56:01Z, trap fired 03:56:27Z).  `wait` is interruptible, so the
  # signal traps above fire immediately.
  sleep "$POLL_S" & wait $! || true
done

[ "$released" = "yes" ] || exit 5
echo "A3FL2_GATE_RELEASE $(date -u +%FT%TZ) waited_s=$(( $(date -u +%s) - T0 ))"
echo "  BOTH halves held for $CONSEC_FREE consecutive reads: container '$last_running', loadavg1 $last_load <= $LOAD_MAX."
echo "  loadavg now: $(cut -d' ' -f1-3 /proc/loadavg)   nproc: $(nproc)"

# Run the exercise IN THIS ALREADY-DETACHED PROCESS so its rc is captured HERE.
# a3fl2_exercise.sh self-detaches unless A3FL2_EXERCISE_DETACHED is set
# (its `if [ -z "${A3FL2_EXERCISE_DETACHED:-}" ]` guard); setting it suppresses a SECOND,
# redundant setsid fork and
# nothing else.  a3fl2_exercise.sh IS NOT EDITED BY THIS FILE.
export A3FL2_EXERCISE_DETACHED=1
export A3FL2_EXERCISE_OUT="$A3FL2_GATE_LOG"
bash "$EX"
EX_RC=$?
echo "EXERCISE_RC=$EX_RC $(date -u +%FT%TZ)"

DONE="$EXERCISE_ROOT/A3FL2_EXERCISE_DONE.txt"
if [ -f "$DONE" ]; then
  echo "----- A3FL2_EXERCISE_DONE.txt (raw conditions; the GREEN call is the supervisor's) -----"
  cat "$DONE"
else
  echo "A3FL2_GATE_NOTE: no $DONE written -- the exercise aborted before the marker. See above."
fi
exit "$EX_RC"
