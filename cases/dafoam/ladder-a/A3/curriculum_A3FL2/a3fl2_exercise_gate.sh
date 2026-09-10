#!/usr/bin/env bash
# =============================================================================
# A3FL2 PRE-FLIGHT EXERCISE -- CONTENTION GATE (operational; MEASUREMENT ONLY)
#
# WHY THIS EXISTS.  `a3fl2_exercise.sh` runs three smokes at 4 MPI ranks with a
# HARD 180 s per-leg deadline (a3fl2_exercise.sh:75-76, :160).  The deadline is
# WALL time, so contention does not make a leg slower -- it makes the leg TRIP
# the deadline.  A tripped leg exits 124, which the GREEN criterion
# (a3fl2_exercise.sh:198, A3FL2_PREREGISTRATION.md:434-438) reads as rc != 0 and
# therefore NOT GREEN -- INDISTINGUISHABLE from a genuine config failure.
#
# MEASURED, on the exercise's own rung-3 source case
# (/home/ubuntu/certonomous-runs/A3-rung3-n52/rung3_stage1.log, 4 ranks,
# coloring file READ not recomputed):
#     26 primal outer iters      ExecutionTime  30.97 s
#     dRdWTPC assembly  0/1355   ExecutionTime  49.24 s
#     dRdWTPC assembly 1354/1355 ExecutionTime 149.84 s
# i.e. ~150 s of MANDATORY pre-GMRES work, UNCONTENDED, against a 180 s deadline
# -- and the 30-iteration gmresMaxIters smoke cap (a3fl2_exercise.sh:73) caps the
# GMRES solve, NOT that assembly.  Under the box state measured 2026-09-10 03:43Z
# (16 vCPUs, load average ~31, twelve foreign solvers at ~99 % CPU) the two R3
# legs would trip 180 s for a CONTENTION reason and report a FALSE NOT_GREEN.
#
# WHAT THIS DOES.  Polls, read-only, until the binding dafoam rung D6RF10 R3
# releases its 4 MPI ranks, then starts the exercise.  It NEVER writes to, signals,
# stops, or otherwise touches the D6RF10 container, its run root, or any d6rf10
# process -- the ONLY d6rf10 interaction anywhere in this file is
# `docker inspect --format '{{.State.Running}}'`, which is read-only.
#
# THIS FILE GRADES NOTHING AND FREEZES NOTHING.  It declares no verdict.  It does
# not read the prereg PERMISSION line, does not stage a3fl2_grade.py, and has no
# G-FREEZE limb.  The GREEN call and the freeze are the dafoam-supervisor's
# (A3FL2_PREREGISTRATION.md:442-444).
#
# rc DISCIPLINE (L "setsid parent returns zero").  The plain invocation re-execs
# THIS script under setsid, fully detached (own session, PPID=1, stdin /dev/null),
# and the parent's `exit 0` means ONLY "armed".  Every rc that matters --
# GATE_RC and EXERCISE_RC -- is captured INSIDE the detached child and written to
# the gate log.  Nothing is captured around the setsid line.
#
# FLEET-DEATH SURVIVAL.  The child is session-detached with PPID=1, so an agent
# or fleet death does not reap it; and the exercise's own legs run as
# `docker run -d` containers (a3fl2_exercise.sh:155), which outlive every shell.
#
# COST (rule 12 / DAFOAM_CHARTER §12, basis cores x wall for the whole clock).
# The gate itself is a 30 s sleep loop: ~0 core-min.  The exercise it starts is
# the spend, and it is the exercise's own line in A3FL2_PREREGISTRATION.md:275.
# =============================================================================
set -u

GATE_TARGET="d6rf10_R3_20260910T031209Z_953457"   # the binding rung; READ-ONLY, never touched
POLL_S=30                                          # poll interval
CONSEC_FREE=3                                      # consecutive non-"true" reads required to release
MAX_WAIT_S=21600                                   # 6 h ceiling (D6RF10 R3's own hard stop is ~07:54Z)
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
  echo "A3FL2_GATE_ARMED child_pid=$! gate_log=$A3FL2_GATE_LOG target=$GATE_TARGET"
  echo "  This exit 0 means ARMED ONLY. GATE_RC and EXERCISE_RC are written INSIDE the child."
  exit 0
fi

# --- detached child ---------------------------------------------------------
echo $$ > "$LOCK"
trap '_rc=$?; echo "GATE_RC=$_rc $(date -u +%FT%TZ)"; rm -f "$LOCK"' EXIT
# A gate stopped by a signal must SAY SO.  Without these, the EXIT trap reports the
# rc of whatever ran last -- a SIGTERM'd gate logged GATE_RC=0, which reads as a
# clean exit when in fact NOTHING was launched.  A false clean exit is worse than
# a loud failure.
on_sig() {
  echo "A3FL2_GATE_KILLED_BY_SIGNAL $(date -u +%FT%TZ) sig=$1 waited_s=$(( $(date -u +%s) - ${T0:-$(date -u +%s)} ))"
  echo "  The gate was stopped BEFORE release. NO exercise was started. D6RF10 untouched."
  exit 143
}
trap 'on_sig TERM' TERM; trap 'on_sig INT' INT; trap 'on_sig HUP' HUP

echo "A3FL2_GATE_START $(date -u +%FT%TZ) pid=$$ ppid=$PPID sid=$(ps -o sid= -p $$ | tr -d ' ')"
echo "  target=$GATE_TARGET poll_s=$POLL_S consec_free=$CONSEC_FREE max_wait_s=$MAX_WAIT_S"
echo "  exercise=$EX"
echo "  D6RF10 IS NEVER TOUCHED: the only interaction is a read-only docker inspect."

T0=$(date -u +%s); free_streak=0; released=no; polls=0
while :; do
  now=$(date -u +%s); waited=$((now - T0))
  running="$(sudo -n docker inspect --format '{{.State.Running}}' "$GATE_TARGET" 2>/dev/null)"
  polls=$((polls + 1))
  if [ "$running" = "true" ]; then
    free_streak=0
    # HEARTBEAT every HEARTBEAT_EVERY polls.  Without it this log is SILENT for up
    # to 6 h and a DEAD gate is indistinguishable from a WAITING one (the
    # "agent watchers die with the agent" tell).  A heartbeat costs one log line.
    if [ $((polls % HEARTBEAT_EVERY)) -eq 1 ]; then
      echo "GATE_HEARTBEAT $(date -u +%FT%TZ) waited_s=$waited target_running=true loadavg=$(cut -d' ' -f1 /proc/loadavg)"
    fi
  else
    free_streak=$((free_streak + 1))
    echo "GATE_POLL $(date -u +%FT%TZ) waited_s=$waited running='${running:-<absent>}' free_streak=$free_streak/$CONSEC_FREE"
    if [ "$free_streak" -ge "$CONSEC_FREE" ]; then released=yes; break; fi
  fi
  if [ "$waited" -ge "$MAX_WAIT_S" ]; then
    echo "A3FL2_GATE_TIMEOUT $(date -u +%FT%TZ) waited_s=$waited -- $GATE_TARGET still running past the 6 h ceiling."
    echo "  NOT LAUNCHING. D6RF10 R3 outliving its own 16905 s deadline is a finding for the supervisor,"
    echo "  and launching into it would be exactly the contention this gate exists to avoid."
    exit 4
  fi
  sleep "$POLL_S"
done

[ "$released" = "yes" ] || exit 5
echo "A3FL2_GATE_RELEASE $(date -u +%FT%TZ) waited_s=$((  $(date -u +%s) - T0 ))"
echo "  loadavg_at_release: $(cut -d' ' -f1-3 /proc/loadavg)   nproc: $(nproc)"
echo "  (load is RECORDED, not gated on -- the gate condition is the D6RF10 container alone.)"

# Run the exercise IN THIS ALREADY-DETACHED PROCESS so its rc is captured HERE.
# a3fl2_exercise.sh self-detaches unless A3FL2_EXERCISE_DETACHED is set
# (a3fl2_exercise.sh:45-54); setting it suppresses a SECOND, redundant setsid fork
# and nothing else.  a3fl2_exercise.sh IS NOT EDITED BY THIS FILE.
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
