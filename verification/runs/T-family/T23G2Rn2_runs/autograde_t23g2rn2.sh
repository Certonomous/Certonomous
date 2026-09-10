#!/bin/bash
# ===========================================================================
# DETACHED WHOLE-RUNG AUTOGRADER for T23G2Rn2 (heat-transfer, 2026-09-09).
# AUTHORED, NOT ARMED.  Structural mirror of
#   verification/runs/T-family/T23G2Rn_runs/autograde_t23g2rn.sh
# for the WHOLE RUNG: T23G2Rn2 launches all three levels CONCURRENTLY (none is
# pre-DONE), so this waits for ALL THREE levels' processes to end, then runs the
# FROZEN comparator ONCE over the whole rung and writes the whole-rung verdict to
# disk, so Sanaa returns to a GRADED verdict, not raw fields.
#
# WATCH CEILING raised to 25.3 h (MAX_POLLS=760 at 120 s) because T23G2Rn2's L3
# CAP timeout is 79,739 s = 22.15 h; the T23G2Rn 20 h ceiling would have graded
# BEFORE L3 finished (T23G2Rn2_PREREGISTRATION.md §7 / §0: >=24 h ceiling owed).
#
# HOW IT IS ARMED (the supervisor's call, AFTER a §3 read and AFTER launch):
#   setsid bash verification/runs/T-family/T23G2Rn2_runs/autograde_t23g2rn2.sh \
#          > verification/runs/T-family/T23G2Rn2_runs/autograde_rung.arm.out 2>&1 &
# setsid makes PPID become 1 so it survives the launching lane's exit AND the
# whole fleet (L-agents-die-with-the-agent).  IT IS NOT setsid'd BY THIS DRAFT.
#
# THE VERDICT COMES ENTIRELY FROM THE FROZEN COMPARATOR.  This watcher adds NO
# grading judgment of its own: it invokes, VERBATIM,
#     python3 docs/campaigns/T-family/analyse_t23g2rn2.py
# and records that instrument's stdout + exit code.  The comparator is:
#   * COMPARATOR PIN (on-disk blob byte-identity; the supervisor confirms it at
#     arm time against the FREEZE-PIN line in freeze commit 2/2's message):
#       2c3f193c1f76aba16c53a2747d8c8baff233056a
#     (docs/campaigns/T-family/analyse_t23g2rn2.py); freeze commit 1/2
#       9ff293229ce6c0a60c9381be50fdf129b1d2199a (pinned in it as
#       GRADING_PATH_FREEZE_COMMIT), pin set in commit 2/2 6c29b259.
#   * it subprocesses the rule-4 completion instrument mark_done_t23g2rn2.py
#     (blob ee1bc912), the thin OPTION (b) wrapper that IMPORTS the frozen
#     mark_done_t23.py (blob 982e1db6, byte-invariant) and reuses its six
#     clauses + age guard verbatim, for ALL THREE levels, REFUSING (exit 2) if
#     ANY level is NOT DONE, then grades and returns RT.exit_code_for(final).
#   * comparator exit-code map (scripts/roache_triple.py):
#       0 = PASS      1 = GATE FAIL      2 = REFUSED (default-deny)
#       3 = NOT A RESULT
#     A REFUSE (exit 2) whose stdout says "rule 4 completion FAILED"/"NOT DONE"
#     means a level is capped/incomplete -- an INFRA confound (PENDING), NOT a
#     scientific NOT A RESULT.
#
# rc is captured INSIDE this wrapper (lesson: `setsid timeout cmd` exits 0 for
# every outcome; capture rc inside the detached wrapper, never around setsid).
# ===========================================================================
set +e

REPO=/home/ubuntu/Certonomous
cd "$REPO" || exit 1

RR="verification/runs/T-family/T23G2Rn2_runs"
COMPARATOR="docs/campaigns/T-family/analyse_t23g2rn2.py"
COMPARATOR_PIN="2c3f193c1f76aba16c53a2747d8c8baff233056a"
FREEZE_COMMIT="9ff293229ce6c0a60c9381be50fdf129b1d2199a"
MARKDONE_PIN="ee1bc912"      # mark_done_t23g2rn2.py (thin wrapper)
MARKDONE_BASE_PIN="982e1db6" # mark_done_t23.py (imported base, byte-invariant)

WATCHLOG="$RR/autograde_rung.watch.log"
STDOUT="$RR/T23G2Rn2_COMPARATOR_STDOUT.txt"
VERDICT="$RR/T23G2Rn2_RUNG_VERDICT.txt"

LEVELS="T23G2Rn2_L1 T23G2Rn2_L2 T23G2Rn2_L3"

log() { echo "$(date -u +%FT%TZ) $*" >> "$WATCHLOG"; }

log "ARMED pid=$$ ppid=$PPID sid=$(ps -o sid= -p $$ 2>/dev/null | tr -d ' ') -- detached T23G2Rn2 WHOLE-RUNG autograder"
log "watching levels: $LEVELS ; comparator pin $COMPARATOR_PIN (freeze $FREEZE_COMMIT) ; mark_done pin $MARKDONE_PIN (base $MARKDONE_BASE_PIN)"

# --- GRADE-ONCE guard (idempotent; survives a re-arm) ----------------------
if [ -f "$VERDICT" ]; then
  log "GRADE-ONCE: verdict artifact $VERDICT already exists -- already graded, nothing to do; exiting 0"
  exit 0
fi

# The pids to watch are written by each level's detached launch wrapper into
#   $RR/PIDS.<LEVEL>   (one line: "<wrapper_pid> <timeout_pid>")
# The rung is READY-TO-GRADE only when ALL THREE PIDS files exist AND none of
# their pids is alive.  A missing PIDS file means that level has not been
# launched yet -- we do NOT grade a rung that is not fully launched (fail-safe).
# `kill -0 <pid>` returns 0 while the pid is alive (these are our own
# processes).  We NEVER grade while ANY watched pid is alive.
rung_alive() {
  local seen=0
  for lv in $LEVELS; do
    local pf="$RR/PIDS.$lv"
    if [ ! -f "$pf" ]; then
      # level not launched yet -> treat rung as "still alive" (not ready)
      return 0
    fi
    seen=$((seen + 1))
    for p in $(cat "$pf" 2>/dev/null); do
      case "$p" in ''|*[!0-9]*) continue ;; esac
      kill -0 "$p" 2>/dev/null && return 0
    done
  done
  # all three PIDS files present and no watched pid alive
  [ "$seen" -eq 3 ] && return 1
  return 0
}

# --- POLL loop -------------------------------------------------------------
# ~120s between polls; absolute ceiling 760 polls = 25.3h so it never loops
# forever (then grades anyway -- the comparator refuses fail-closed on an
# incomplete run, which is the honest outcome).  RAISED from T23G2Rn's 600/20h:
# T23G2Rn2's L3 CAP timeout is 79,739s = 22.15h, so a 20h ceiling would grade
# BEFORE L3 finished -- the ceiling MUST exceed the largest per-level CAP.
MAX_POLLS=760
i=0
ended=0
while [ "$i" -lt "$MAX_POLLS" ]; do
  if ! rung_alive; then
    log "RUNG ENDED: all three levels' PIDS files present and no watched pid alive after ${i} polls"
    ended=1
    break
  fi
  if [ $((i % 10)) -eq 0 ]; then
    log "heartbeat poll=$i : rung still alive (a level's pid present, or a PIDS file not yet written); waiting"
  fi
  i=$((i + 1))
  sleep 120
done

if [ "$ended" -eq 0 ]; then
  log "WATCH CEILING reached (${MAX_POLLS} polls ~25.3h) with the rung still apparently alive -- grading anyway; the comparator refuses fail-closed if any level is incomplete (honest)"
fi

# --- re-check the grade-once guard (a re-arm may have graded meanwhile) -----
if [ -f "$VERDICT" ]; then
  log "GRADE-ONCE (post-wait): verdict artifact appeared during the wait -- already graded; exiting 0"
  exit 0
fi

# --- (a) clear stale bytecode BEFORE grading (stale-pycache lesson) ---------
# A stale __pycache__ can invert a comparator's logic; clear every dir on the
# grading path before the frozen comparator imports anything.
log "clearing stale __pycache__ on the grading path"
for d in "docs/campaigns/T-family" \
         "scripts" \
         "verification/runs/T-family/T23_runs" \
         "verification/runs/T-family/T23G2Rn2_runs"; do
  find "$d" -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null
done

# --- (b) run the FROZEN comparator, capture stdout+stderr and its exit code -
log "running frozen comparator: python3 $COMPARATOR (verdict is ENTIRELY its stdout+exit code)"
python3 "$COMPARATOR" > "$STDOUT" 2>&1
GRC=$?
log "comparator finished rc=$GRC ; stdout captured to $STDOUT"

# --- extract the reported lines from the comparator's own stdout ------------
RUNG_LINE="$(grep -E '^RUNG VERDICT:' "$STDOUT" | tail -1)"
REFUSE_LINE="$(grep -E 'REFUSED \(exit 2\):' "$STDOUT" | tail -1)"
# per-level triple / per-quantity gate lines the comparator prints via note():
TRIPLE_LINES="$(grep -E 'G-PLATEAU|G-RATIO|G-ORDER|A2\.1|p\(Q4\)|G-YPLUS|G-MESHSIM|G-CONV|VERDICT:' "$STDOUT")"

# --- INTERPRETATION ---------------------------------------------------------
# Faithful to scripts/roache_triple.py exit-code map (0/1/2/3).
if [ "$GRC" -eq 2 ]; then
  if grep -qE 'rule 4 completion FAILED|NOT DONE' "$STDOUT"; then
    INTERP="exit 2 => REFUSE, and the stdout says rule-4 completion FAILED / NOT DONE.
INTERPRETATION: rung = PENDING (infra-confounded: a level capped/incomplete, not a scientific NOT A RESULT); the incomplete level(s) need a fresh re-run per the pre-registered plan (new dir, registered endTime, §6 cap)."
    WHOLE_RUNG_VERDICT="PENDING (infra-confounded -- a level incomplete; fresh re-run needed)"
  else
    INTERP="exit 2 => REFUSE (default-deny), but NOT for a rule-4/NOT-DONE reason. The comparator refused for another cause; the refusal reason is recorded verbatim below and must be triaged."
    WHOLE_RUNG_VERDICT="REFUSED (exit 2) -- see refusal reason below"
  fi
elif [ "$GRC" -eq 0 ] || [ "$GRC" -eq 1 ] || [ "$GRC" -eq 3 ]; then
  # 0=PASS, 1=GATE FAIL, 3=NOT A RESULT -- the graded whole-rung verdict is the
  # comparator's own RUNG VERDICT line, recorded verbatim.
  if [ -n "$RUNG_LINE" ]; then
    WHOLE_RUNG_VERDICT="$RUNG_LINE"
  else
    WHOLE_RUNG_VERDICT="(rc=$GRC but no 'RUNG VERDICT:' line found in stdout -- inspect $STDOUT)"
  fi
  INTERP="exit $GRC => graded verdict (0=PASS, 1=GATE FAIL, 3=NOT A RESULT). The whole-rung verdict is the comparator's own RUNG VERDICT line, recorded verbatim."
else
  WHOLE_RUNG_VERDICT="(unexpected comparator rc=$GRC -- inspect $STDOUT)"
  INTERP="UNEXPECTED comparator exit code $GRC (not in {0,1,2,3}); the comparator may itself be broken. Inspect $STDOUT before trusting anything."
fi

# --- write the durable verdict artifact -------------------------------------
{
  echo "T23G2Rn2 WHOLE-RUNG VERDICT"
  echo "graded_at_utc : $(date -u +%FT%TZ)"
  echo "graded_by     : detached autograder autograde_t23g2rn2.sh (pid $$, PPID at arm = $PPID)"
  echo "comparator    : $COMPARATOR"
  echo "comparator_pin: $COMPARATOR_PIN"
  echo "freeze_commit : $FREEZE_COMMIT"
  echo "mark_done_pin : $MARKDONE_PIN (wrapper) ; base $MARKDONE_BASE_PIN (mark_done_t23.py)"
  echo "comparator_rc : $GRC"
  echo "comparator_stdout: $STDOUT"
  echo ""
  echo "WHOLE-RUNG VERDICT: $WHOLE_RUNG_VERDICT"
  echo ""
  echo "--- comparator final line (verbatim) ---"
  [ -n "$RUNG_LINE" ] && echo "$RUNG_LINE"
  [ -n "$REFUSE_LINE" ] && echo "$REFUSE_LINE"
  echo ""
  echo "--- per-level triple / per-quantity gate lines (verbatim from stdout) ---"
  if [ -n "$TRIPLE_LINES" ]; then
    echo "$TRIPLE_LINES"
  else
    echo "(no gate summary lines found -- the comparator likely refused before grading; see $STDOUT)"
  fi
  echo ""
  echo "--- INTERPRETATION ---"
  echo "$INTERP"
  echo ""
  echo "NOTE: this verdict is the FROZEN COMPARATOR's stdout+exit code on disk."
  echo "A returning agent still owes the supervisor's diff-read + big-claim check before it is repeated upward."
} > "$VERDICT"

log "VERDICT WRITTEN to $VERDICT : $WHOLE_RUNG_VERDICT"
log "COMPLETE -- exiting 0"
exit 0
