#!/usr/bin/env bash
# =============================================================================
# autograde_watch_vmfl072_r3.sh -- DETACHED disconnect-safe autograder for
# VMFL072-R3.  The §2ba disconnect-safe GRADING leg: the queue daemon is the
# scheduler leg, this is the grading leg, and neither needs a live agent.
#
# ---- NOT ARMED.  DRAFTED, NOT LAUNCHED, NOT COMMITTED. ----------------------
# Drafted by an ansys-lane-opus 2026-09-10.  The lane did NOT run it and did NOT
# arm it.  The supervisor reads it as a diff (non-delegable §3 check-1) and arms
# it with the single setsid line reported alongside this file.
#
# Modelled on the PROVEN, LIVE example
#   cases/ansys_verification/VMFL063-R3/autograde_watch_vmfl063_r3.sh
# (its instance runs at pid 827346, PPID 1).  Same shape: bounded poll -> a
# terminal decision -> a rule-2 freeze re-verify -> ONE comparator invocation ->
# rc captured INSIDE this process.
#
# WHY IT EXISTS: VMFL072-R3's launcher does NOT grade at exit.  Its :250-251 are
# a COMMENT printing the command a human should run "only after ALL FIVE levels
# are complete", so grading currently depends on an agent being alive at a future
# instant -- which this lab has ruled unacceptable.  The five levels are fast
# (registered caps L1 1.5, L2 9, L3 65, B2 100, C1 9 core-min, all serial) and
# will very likely finish after the launching session is gone.
#
# WHAT IT ADDS: NOTHING BUT TIMING.  It decides WHEN to grade.
# compare_vmfl072_r3.py is the sole authority on WHAT the verdict is -- the
# strict completion rule, the plateau/station/exactness conjunction, the planted
# controls P1/P2, and every band.  This wrapper computes no gate quantity, reads
# no field, and applies no threshold.  If it ever appears to, that is a defect.
#
# WHAT IT WILL NOT DO, BY CONSTRUCTION:
#   * it never launches, re-launches or re-runs a level -- it contains no call to
#     launch_vmfl072_r3.sh, apply_level.sh, run_inner.sh, blockMesh or pimpleFoam;
#   * it never signals, kills or waits on a solver -- there is no kill, pkill,
#     killall or `wait` in this file.  The only process call is a read-only
#     `pgrep -c -x pimpleFoam`, used for ONE diagnostic log line and gated on
#     nothing (`pgrep -f` is deliberately avoided: it matches the invoking
#     command line, and fleet agents are invisible to it anyway);
#   * it never polls forever -- see the three termination paths below;
#   * it never grades twice -- an atomic mkdir lock plus an rc-file short-circuit.
#
# ---- THE TERMINATION LOGIC, WHICH IS THE PART WORTH READING -----------------
# A level is in exactly one of three states, decided from FILES only:
#   STOPPED       <run root>/<L>/RC.txt exists AND carries a line matching ^rc=.
#                 The frozen wrapper writes it with rc captured INSIDE itself
#                 (launcher :222-223: `rc=$?` then `echo "rc=${rc}" > RC.txt`),
#                 so RC.txt is the authoritative "this level has stopped" signal --
#                 and it is the SAME file the comparator itself reads at :365-370,
#                 where a missing or unparseable RC.txt is its own C-01 Refuse.
#                 ⚠ STOPPED MEANS STOPPED, NOT SUCCEEDED.  rc is recorded and
#                 classified for the log; it NEVER decides whether to grade.  The
#                 comparator is the authority on whether a stopped level is
#                 gradeable, and a crashed level MUST still reach it so that the
#                 NOT A RESULT lands on disk with no live agent.
#   IN-FLIGHT     the run dir exists but RC.txt does not -- a solver is working, or
#                 its wrapper is between the solver exit and the RC.txt write.
#   NOT-LAUNCHED  no run dir at all.  Either the daemon has not reached this
#                 level's queue entry yet, or the launcher REFUSED it at a guard.
#
# ---- rc CLASSIFICATION, RECORDED AND LOGGED, GATING NOTHING -----------------
#   rc 0            the solver exited cleanly.
#   rc 124 | 137    the registered cap STOPPED the run (timeout TERM, then KILL).
#                   The frozen wrapper appends its own OVERRUN block for these two
#                   and only these two.  rule 12: an overrun stops the run; it does
#                   not get a new budget.
#   rc 128+n        KILLED BY SIGNAL n -- a CRASH, not a cap-stop and not a
#                   completion.  rc 136 = 128+8 = SIGFPE.  MEASURED on this very
#                   run: L3 carries rc=136, NO OVERRUN block, finished
#                   2026-09-10T16:17:06Z against a 65 core-min cap it was nowhere
#                   near.  Calling that an overrun would be false, and bucketing it
#                   with rc 0 would be worse.
#   any other rc    a nonzero exit that is neither cap nor signal -- also a crash.
#
# Termination path 1 -- CLEAN: all five levels STOPPED.  Grade at once.
# Termination path 2 -- SETTLED: no level is IN-FLIGHT, and at least one is
#                 NOT-LAUNCHED, and that whole picture has been UNCHANGED for
#                 STABLE_ITERS consecutive polls.  Grade, and let the comparator
#                 refuse for the missing level -- which is the correct, honest
#                 outcome and is exactly what a NOT A RESULT is for.
# Termination path 3 -- CAP: the bounded poll ceiling is hit.  Do NOT grade;
#                 write the reason to the rc file and exit 3, so a future session
#                 finds a stated cause rather than silence.
#
# WHY PATH 2 NEEDS A STABILITY WINDOW AND NOT A ONE-SHOT TEST.  THIS WAS SETTLED
# BY THE CASE ITSELF DURING DRAFTING, IN BOTH DIRECTIONS, AND BOTH ARE RECORDED:
#
#   16:09:59Z  STATUS.queue.VMFL072-R3-B2  launcher_rc=2   <- refused, no run dir
#   16:11:04Z  STATUS.queue.VMFL072-R3-C1  launcher_rc=2   <- refused, no run dir
#   16:12:12Z / 16:13:15Z / 16:14:20Z      L1 / L2 / L3  launcher_rc=0, run dirs appear
#   16:15:25Z  STATUS.queue.VMFL072-R3-B2  launcher_rc=0   <- RETRIED, run dir appears
#   16:16:31Z  STATUS.queue.VMFL072-R3-C1  launcher_rc=0   <- RETRIED, run dir appears
#
# So B2 and C1 WERE refused by a launcher guard, and the queue daemon THEN RETRIED
# THEM SUCCESSFULLY about five minutes later -- their entries have since moved from
# the pending directory into verification/queue/ansys-verification/launched/.  All
# five levels are now in flight, which makes path 1 the expected route.
#
# ⚠ THE MEASURED POINT, AND IT IS THE WHOLE ARGUMENT FOR THE WINDOW: a watcher
# armed between 16:11 and 16:15 with a ONE-SHOT path-2 test would have seen three
# levels done, none in flight and two "never coming", GRADED THREE LEVELS, and
# produced a spurious refusal FOUR MINUTES BEFORE B2 AND C1 LANDED.  The stability
# window is what prevents that, and it is now confirmed against the real case and
# not only against the synthetic RETRY arm of the selftest below.
#
# The converse hazard is still live and is why path 2 exists at all: queue_runner.py's
# own header says an entry it declines to launch "is left where it was, retried next
# tick", so a level CAN be retried -- but nothing guarantees a retry ever succeeds,
# and a trigger that waited for five RC.txt files unconditionally WOULD POLL FOREVER
# on a level that stays refused.  Path 2 bounds that; path 3 bounds everything.
#
# NOT ESTABLISHED, AND NOT GUESSED HERE: *why* B2 and C1 were refused at the first
# attempt.  Each queue launch redirects over
# cases/ansys_verification/VMFL072-R3/launcher.queue.out, so those two refusal
# reasons were CLOBBERED by the later launches and are not recoverable from that
# file.  A refusal is a finding until triage says otherwise, and that triage is the
# supervisor's, not this script's.
#
# rc IS CAPTURED INSIDE THIS PROCESS.  `setsid timeout cmd` exits 0 for every
# outcome, so an rc taken around the setsid line would report success on a
# timeout, a signal and a crash alike.  RC=$? sits on the line after the
# comparator call, and nothing runs between them.
#
# ---- DRAFT-TIME TRIGGER SELFTEST, WITH THREE MUTATION CONTROLS --------------
# ⚠ THIS SUPERSEDES AN EARLIER SELFTEST THAT WAS VOID.  The first version of this
# watcher polled for `RUN_RC`, a filename the frozen launcher NEVER WRITES, so its
# Path 1 was unreachable and it would have polled to the 12 h cap and exited
# WITHOUT GRADING -- the appearance of a grading leg and none of the substance.
# The supervisor's check-1 caught it.  The selftest that "passed" then is void
# because it exercised the wrong filename, and it is redone here against RC.txt.
#
# The lane did NOT run this script.  It DID test the trigger by lifting `rc_of`,
# `classify_rc` and the 12-line level classifier VERBATIM out of this file and
# driving them against fixtures in a scratch tree -- so the tested code IS the
# shipped code, and the real run root was only ever READ.
#
# 17 arms, 17 ok / 0 FAILED:
#   CONTACT WITH THE REAL FROZEN ARTIFACTS (not synthetic fixtures -- the L-522
#   lesson: a suite that authors its own inputs tests the author's mental model of
#   the input, which is exactly how the RUN_RC defect survived):
#     rc_of reads the REAL L1/L2/L3/C1 RC.txt -> 0 / 0 / 136 / 0            [ok x4]
#     the real L3 classifies as CRASH-SIGNAL(SIGFPE 128+8)                  [ok]
#     the real L1 classifies as CLEAN-EXIT                                  [ok]
#     a 124 file with its OVERRUN block classifies as CAP-STOP, not a crash [ok]
#     the OVERRUN block does not hijack the rc= read (reads 124)            [ok]
#     an EMPTY RC.txt (the write race) yields NO rc                         [ok]
#     a file carrying only cap_* keys yields NO rc                          [ok]
#   TRIGGER SCENARIOS:
#     ALLFIVE    five RC.txt                       -> path 1 at iter 1      [ok]
#     NOW_B2LIVE the MEASURED state at drafting     -> path 3, NOT path 1/2 [ok]
#     B2LANDS    B2 RC.txt lands at iter 6          -> path 1 at iter 7     [ok]
#     REFUSED2   L1-L3 stopped, B2/C1 never launched-> path 2 at iter 16    [ok]
#     RETRY      B2 dir at iter 8, RC.txt at 20     -> path 1 at iter 21    [ok]
#     EMPTY      nothing launched                   -> path 2, not forever  [ok]
#     ALLCRASH   all five stopped with rc 136       -> path 1 (STILL grades)[ok]
#     WRITERACE  B2 RC.txt exists but is EMPTY      -> path 3, NOT path 1   [ok]
#
# MUTATION CONTROLS -- a suite that cannot go red proves nothing (8 arms each):
#   CONTROL (as shipped)                                    8 ok / 0 FAILED
#   M1  filename reverted to RUN_RC (THE CAUGHT DEFECT)     4 ok / 4 FAILED
#   M2  existence-only, the rc_of guard removed             7 ok / 1 FAILED
#   M3  anchors + digit guard removed from rc_of            8 ok / 0 FAILED
#
# READING THESE, INCLUDING THE ONE THAT DID NOT DISCRIMINATE:
#   M1 is the important one: THIS SUITE WOULD HAVE CAUGHT THE RUN_RC DEFECT, red on
#   4 of 8 arms.  M2 shows the `rc_of` guard is load-bearing: with mere file
#   existence as the test, WRITERACE goes red -- the watcher grades a level whose
#   wrapper has created RC.txt but not yet written an rc into it.
#   M3 STAYED GREEN, AND THAT IS REPORTED RATHER THAN QUIETLY DROPPED.  An
#   unanchored `grep 'rc=' | cut -d= -f2` returns the CORRECT value on all four real
#   and synthetic fixtures ('136', '124', '', ''), because this wrapper always
#   writes `rc=<digits>` as the FIRST line of RC.txt with `>` and no other key in
#   the file contains the substring `rc=`.  So the `^rc=[0-9]+$` anchor is
#   DEFENSIVE INSURANCE against a future format change, NOT a guard measured to be
#   load-bearing today.  It is kept because it costs nothing, and it is described
#   here as insurance so that nobody cites it as a tested protection.
# =============================================================================
set +u
set -o pipefail

REPO=/home/ubuntu/Certonomous
CASE_DIR="$REPO/cases/ansys_verification/VMFL072-R3"
RUN_ROOT="$REPO/verification/runs/ansys_verification/VMFL072-R3"
COMPARATOR="$CASE_DIR/compare_vmfl072_r3.py"

# The registered grading-path pin, from PREREGISTRATION.md's COMPARATOR_BLOB and
# re-asserted by the launcher's own G-03 guard (launch_vmfl072_r3.sh:124).
PIN_BLOB="2fcc0ced1bb99192f25c80b323af161cf25b90ac"

# The five registered levels, in the comparator's own order
# (compare_vmfl072_r3.py:622, :639, :840).
LEVELS="L1 L2 L3 B2 C1"

# ---- output artefacts, ALL under the run root, none of them a gate ------------
STATE="$RUN_ROOT/AUTOGRADE_WATCH_STATE_VMFL072_R3.txt"
STATE_BOOT="$CASE_DIR/AUTOGRADE_WATCH_BOOTSTRAP_VMFL072_R3.txt"
GLOG="$RUN_ROOT/GRADING_VMFL072_R3.log"     # the comparator's stdout+stderr; IT is the record
GRC="$RUN_ROOT/AUTOGRADE_VMFL072_R3.rc"
LOCK="$RUN_ROOT/.autograde_vmfl072_r3.lock"

POLL=60            # s between polls
BOOT_CAP=60        # ~1 h for the run root to appear (it already exists at drafting)
CAP=720            # 720 x 60 s = 12 h ceiling.  The registered caps total 184.5
                   # core-min (~3.1 h serial); 12 h leaves room for queue wait,
                   # box contention and a daemon retry of B2/C1, and still
                   # terminates with a stated reason instead of lingering.
STABLE_ITERS=15    # ~15 min of an unchanged picture before path 2 fires.

log(){ echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >> "$STATE"; }
# Releases only the lock this process created.  It never touches a lock it did
# not take -- that path exits 4 before reaching here.
release_lock(){ rm -f "$LOCK/owner" 2>/dev/null; rmdir "$LOCK" 2>/dev/null; }

# rc_of <RC.txt> -> the solver rc, or EMPTY if the file has no parseable rc.
# ANCHORED to the `rc=` KEY AT LINE START.  RC.txt carries several rc-ish keys --
# `rc=`, `cap_sec=`, `cap_core_min=` -- plus, for rc 124/137, free OVERRUN prose
# mentioning caps.  An unanchored `grep rc=` reads `cap_core_min=65` and reports a
# level as rc 65; a substring match inside the OVERRUN block is worse still. The
# `^rc=` anchor plus the digit-only guard is what makes this reader correct, and
# the selftest below has a MUTANT that removes the anchor and goes red.
rc_of(){
  local v
  v="$(grep -m1 -E '^rc=[0-9]+$' "$1" 2>/dev/null | cut -d= -f2)"
  case "$v" in (''|*[!0-9]*) printf '' ;; (*) printf '%s' "$v" ;; esac
}

# classify_rc <rc> -> a label for the LOG AND THE RECORD.  It gates NOTHING.
classify_rc(){
  case "$1" in
    0)        printf 'CLEAN-EXIT' ;;
    124|137)  printf 'CAP-STOP(overrun, rule 12; the wrapper writes its own OVERRUN block)' ;;
    134)      printf 'CRASH-SIGNAL(SIGABRT 128+6)' ;;
    136)      printf 'CRASH-SIGNAL(SIGFPE 128+8 -- NOT a cap-stop and NOT a completion)' ;;
    139)      printf 'CRASH-SIGNAL(SIGSEGV 128+11)' ;;
    '')       printf 'NO-PARSEABLE-rc' ;;
    *)        if [ "$1" -gt 128 ] 2>/dev/null; then printf 'CRASH-SIGNAL(128+%s)' "$(( $1 - 128 ))"
              else printf 'NONZERO-EXIT(crash)'; fi ;;
  esac
}

# ---- bootstrap: never write into a run root that does not exist ---------------
if [ ! -d "$RUN_ROOT" ]; then
  STATE="$STATE_BOOT"; : > "$STATE"
  log "run root absent at arm; waiting up to $((BOOT_CAP*POLL)) s for it to appear"
  b=0
  while [ "$b" -lt "$BOOT_CAP" ] && [ ! -d "$RUN_ROOT" ]; do b=$((b+1)); sleep "$POLL"; done
  if [ ! -d "$RUN_ROOT" ]; then
    log "REFUSE: run root $RUN_ROOT never appeared within the bootstrap cap; NOT grading"
    echo "run_root_absent rc=3 utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$STATE_BOOT.rc"
    exit 3
  fi
  STATE="$RUN_ROOT/AUTOGRADE_WATCH_STATE_VMFL072_R3.txt"
fi

# ---- idempotence, guard 1: a completed grade is never redone -----------------
if [ -f "$GRC" ] && grep -q 'grade_rc=' "$GRC" 2>/dev/null; then
  log "ALREADY GRADED -- $GRC carries a grade_rc; exiting without re-grading (idempotent)"
  exit 0
fi

# ---- idempotence, guard 2: atomic lock, so two watchers cannot both grade ----
# mkdir is atomic on this filesystem; a stale lock is REPORTED, never removed by
# this script, because silently stealing a lock is how two graders end up racing.
if ! mkdir "$LOCK" 2>/dev/null; then
  : > "${STATE}.contended"
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) REFUSE: lock $LOCK is held -- another watcher owns this grade. NOT grading, NOT removing the lock." >> "${STATE}.contended"
  exit 4
fi
echo "pid=$$ armed=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$LOCK/owner"

: > "$STATE"
log "watcher START pid=$$ ppid=$PPID sid=$(ps -o sid= -p $$ 2>/dev/null | tr -d ' ')"
log "run_root=$RUN_ROOT"
log "comparator=$COMPARATOR pin=$PIN_BLOB"
log "levels=$LEVELS  poll=${POLL}s  cap=${CAP} iters (~$((CAP*POLL/3600)) h)  stability_window=${STABLE_ITERS} iters"
log "trigger: ALL FIVE RC.txt with a parseable ^rc= line (path 1); or no level IN-FLIGHT and >=1 NOT-LAUNCHED, stable ${STABLE_ITERS} iters (path 2); or poll cap with a recorded reason (path 3)"
log "RC.txt is the launcher's own completion record (:222-223) and the comparator's own C-01 input (:365-370) -- this watcher reads the SAME file, never a different one"
log "this watcher NEVER launches, re-runs, signals or kills anything"

# ---- poll ---------------------------------------------------------------------
i=0
TERMINAL=""
PREV_PIC=""
STABLE=0
DONE_LIST=""; INFLIGHT_LIST=""; NOTLAUNCHED_LIST=""

while [ "$i" -lt "$CAP" ]; do
  DONE_LIST=""; INFLIGHT_LIST=""; NOTLAUNCHED_LIST=""
  ndone=0; ninflight=0; nnot=0
  for L in $LEVELS; do
    d="$RUN_ROOT/$L"
    if [ -f "$d/RC.txt" ] && [ -n "$(rc_of "$d/RC.txt")" ]; then
      DONE_LIST="$DONE_LIST $L";      ndone=$((ndone+1))
    elif [ -d "$d" ]; then
      INFLIGHT_LIST="$INFLIGHT_LIST $L"; ninflight=$((ninflight+1))
    else
      NOTLAUNCHED_LIST="$NOTLAUNCHED_LIST $L"; nnot=$((nnot+1))
    fi
  done

  # path 1 -- CLEAN
  if [ "$ndone" -eq 5 ]; then TERMINAL="all-five-RC.txt"; break; fi

  # path 2 -- SETTLED: nothing in flight, something never launched, picture stable
  PIC="done:${DONE_LIST# } inflight:${INFLIGHT_LIST# } notlaunched:${NOTLAUNCHED_LIST# }"
  if [ "$PIC" = "$PREV_PIC" ]; then STABLE=$((STABLE+1)); else
    STABLE=0; PREV_PIC="$PIC"; log "state change at iter=$i -> $PIC"
  fi
  if [ "$ninflight" -eq 0 ] && [ "$nnot" -gt 0 ] && [ "$STABLE" -ge "$STABLE_ITERS" ]; then
    TERMINAL="settled-with-unlaunched-levels(${NOTLAUNCHED_LIST# })"; break
  fi

  i=$((i+1)); sleep "$POLL"
done

# path 3 -- CAP
if [ -z "$TERMINAL" ]; then
  log "REFUSE: poll cap $CAP reached without a terminal condition -- NOT grading"
  log "  last picture: $PIC"
  echo "poll_cap_reached rc=3 utc=$(date -u +%Y-%m-%dT%H:%M:%SZ) cap_iters=$CAP poll_s=$POLL last_picture='$PIC' reason='no terminal condition: levels remained IN-FLIGHT past the ceiling, so this is a STALL or a cap-kill to investigate, not a verdict' note='NOT A RESULT is a call for the comparator and the supervisor, NOT for this wrapper -- nothing was graded'" > "$GRC"
  release_lock
  exit 3
fi

log "TERMINAL via $TERMINAL at iter=$i"
log "  DONE:         ${DONE_LIST:-  none}"
log "  IN-FLIGHT:    ${INFLIGHT_LIST:-  none}"
log "  NOT-LAUNCHED: ${NOTLAUNCHED_LIST:-  none}"
for L in $LEVELS; do
  s="$CASE_DIR/STATUS.queue.VMFL072-R3-$L"
  [ -f "$s" ] && log "  queue record $L: $(head -1 "$s")"
  if [ -f "$RUN_ROOT/$L/RC.txt" ]; then
    _rc="$(rc_of "$RUN_ROOT/$L/RC.txt")"
    log "  RC.txt $L: rc='${_rc}' -> $(classify_rc "$_rc")   finished=$(grep -m1 '^finished=' "$RUN_ROOT/$L/RC.txt" 2>/dev/null | cut -d= -f2-)  cap_core_min=$(grep -m1 '^cap_core_min=' "$RUN_ROOT/$L/RC.txt" 2>/dev/null | cut -d= -f2)  overrun_block=$(grep -c '^OVERRUN' "$RUN_ROOT/$L/RC.txt" 2>/dev/null)"
  fi
done
log "diagnostic only, gated on nothing: pimpleFoam processes visible = $(pgrep -c -x pimpleFoam 2>/dev/null || echo 0)"
log "settling 30 s for the frozen wrapper's bookkeeping flush"
sleep 30

# ---- rule 2, guard A: the file that grades must BE the frozen file ------------
DISK_BLOB="$(git -C "$REPO" hash-object "$COMPARATOR" 2>/dev/null)"
if [ "$DISK_BLOB" != "$PIN_BLOB" ]; then
  log "REFUSE: comparator on disk ($DISK_BLOB) != registered pin ($PIN_BLOB) (rule 2). NOT grading."
  echo "comparator_blob_mismatch disk=$DISK_BLOB pin=$PIN_BLOB rc=2 utc=$(date -u +%Y-%m-%dT%H:%M:%SZ) terminal_signal=$TERMINAL" > "$GRC"
  release_lock
  exit 2
fi
log "freeze guard A OK: disk == pin  $PIN_BLOB"

# ---- rule 2, guard B: the pin must also be what is COMMITTED ------------------
# A SECOND, genuinely independent check, and NOT an invented comparator flag:
# compare_vmfl072_r3.py takes only --runroot and --selftest (its argparse at
# :1074-1076), so it has no self-verify mode to call.  Guard A proves the file on
# disk is the pinned blob; guard B proves that blob is the one in the repository
# at HEAD -- i.e. that the pin is not a local artefact of an uncommitted edit.
# HEAD is captured ONCE, in this shell, because a lane can move HEAD between two
# reads (L-223).
H="$(git -C "$REPO" rev-parse HEAD 2>/dev/null)"
HEAD_BLOB="$(git -C "$REPO" rev-parse "$H:cases/ansys_verification/VMFL072-R3/compare_vmfl072_r3.py" 2>/dev/null)"
if [ "$HEAD_BLOB" != "$PIN_BLOB" ]; then
  log "REFUSE: the pinned blob is not the blob committed at HEAD $H (HEAD has $HEAD_BLOB) (rule 2). NOT grading."
  echo "comparator_not_committed head=$H head_blob=$HEAD_BLOB pin=$PIN_BLOB rc=2 utc=$(date -u +%Y-%m-%dT%H:%M:%SZ) terminal_signal=$TERMINAL" > "$GRC"
  release_lock
  exit 2
fi
log "freeze guard B OK: pin == blob committed at HEAD $H"

# ---- grade ONCE.  The flag set is the REGISTERED one, not an invented one -----
# `--runroot` (one word) is the comparator's own argparse name (:1075) and is the
# exact invocation the frozen launcher prints at :250-251.  There is no --out and
# no --verify-frozen on this comparator; stdout IS the record, so it is captured
# to $GLOG and never post-processed into a verdict by this wrapper.
log "grading: python3 $COMPARATOR --runroot $RUN_ROOT"
python3 "$COMPARATOR" --runroot "$RUN_ROOT" > "$GLOG" 2>&1
RC=$?          # <-- captured INSIDE this process, on the line after the call
log "comparator exited rc=$RC"

VERDICT="$(grep -aoE 'VERDICT[^\n]*' "$GLOG" 2>/dev/null | head -1)"
[ -z "$VERDICT" ] && VERDICT="see $GLOG"

echo "grade_rc=$RC utc=$(date -u +%Y-%m-%dT%H:%M:%SZ) comparator_blob=$PIN_BLOB head=$H terminal_signal=$TERMINAL levels_done='${DONE_LIST# }' levels_not_launched='${NOTLAUNCHED_LIST# }' log=$GLOG note='the COMPARATOR is the authority and its exit codes are its own: rc 0/1 = graded (verdict text in the log); rc 2 = REFUSED (Refuse -- incomplete run, unreadable artifact, a planted control unseen) = NOT A RESULT; rc 3 = NotAResult; any other nonzero = comparator crash = INSTRUMENT FAULT = NOT A RESULT, never GATE FAIL. This wrapper computed NO gate quantity and applied NO threshold; it only decided WHEN to run.'" > "$GRC"

log "grade DONE rc=$RC verdict='$VERDICT'  log=$GLOG  rc_file=$GRC"
log "watcher END -- the verdict is on disk with no live fleet; a future session/supervisor records it in the register and commits"
release_lock
exit "$RC"
