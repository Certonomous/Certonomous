#!/bin/bash
# ===========================================================================
# DETACHED AUTOGRADER for the T23G2R whole-rung (heat-transfer, disconnect-prep
# 2026-09-09). ARMED via setsid so it survives the death of the launching agent
# AND the whole fleet: it waits for the L3 solver to terminate, then runs the
# FROZEN comparator ONCE and writes the whole-rung verdict to disk, so Sanaa
# returns to a GRADED verdict, not raw fields.
#
# WHY THIS EXISTS: L1 and L2 are already DONE (their STATUS.* markers persist on
# disk); L3 (endTime 28000) is still solving and will very likely finish AFTER
# the current agent fleet has died (~08:36Z est., hard cap 14:10:37Z). No queue
# daemon runs a post-completion grade hook, so without this watcher a fleet death
# would leave the rung SOLVED but UNGRADED.
#
# THE VERDICT COMES ENTIRELY FROM THE FROZEN COMPARATOR. This watcher adds NO
# grading judgment of its own: it invokes, verbatim,
#     python3 docs/campaigns/T-family/analyse_t23g2r.py
# and records that instrument's stdout + exit code. The comparator is:
#   * COMPARATOR PIN (on-disk blob byte-identity confirmed by the supervisor):
#       0a1b1f98d0165503c4482e06ad10ecc9d0604c38
#     (docs/campaigns/T-family/analyse_t23g2r.py)
#   * it subprocesses the completion instrument mark_done_t23.py, PIN 982e1db6
#     (verification/runs/T-family/T23_runs/mark_done_t23.py), rule-4 strict
#     completion + age guard, for ALL THREE levels, REFUSING (exit 2) if ANY
#     level is NOT DONE, then grades and returns RT.exit_code_for(final).
#   * comparator exit-code map (scripts/roache_triple.py:177 / :712):
#       0 = PASS      1 = GATE FAIL      2 = REFUSED (default-deny)
#       3 = NOT A RESULT
#     A REFUSE (exit 2) whose stdout says "rule 4 completion FAILED"/"NOT DONE"
#     means L3 is capped/incomplete -- an INFRA confound (PENDING), NOT a
#     scientific NOT A RESULT.
#
# HARD CAP on the L3 solver: 14:10:37Z (the timeout wrapper's own deadline).
# This watcher additionally caps its own watching at 20h so it never polls
# forever.
#
# rc is captured INSIDE this wrapper (lesson: `setsid timeout cmd` exits 0 for
# every outcome; capture rc inside the detached wrapper, never around setsid).
# ===========================================================================
set +e

REPO=/home/ubuntu/Certonomous
cd "$REPO" || exit 1

RR="verification/runs/T-family/T23G2R_runs"
COMPARATOR="docs/campaigns/T-family/analyse_t23g2r.py"
COMPARATOR_PIN="0a1b1f98d0165503c4482e06ad10ecc9d0604c38"
MARKDONE_PIN="982e1db6"

WATCHLOG="$RR/autograde_L3.watch.log"
STDOUT="$RR/T23G2R_COMPARATOR_STDOUT.txt"
VERDICT="$RR/T23G2R_RUNG_VERDICT.txt"

# The two L3 processes to watch (supervisor-verified):
#   472335 = timeout wrapper ; 472337 = the chtMultiRegionSimpleFoam solver
L3_WRAP_PID=472335
L3_SOLVER_PID=472337

log() { echo "$(date -u +%FT%TZ) $*" >> "$WATCHLOG"; }

log "ARMED pid=$$ ppid=$PPID sid=$(ps -o sid= -p $$ 2>/dev/null | tr -d ' ') -- detached T23G2R L3 autograder"
log "watching L3 pids: wrapper=$L3_WRAP_PID solver=$L3_SOLVER_PID ; comparator pin $COMPARATOR_PIN ; mark_done pin $MARKDONE_PIN"

# --- GRADE-ONCE guard (idempotent; survives a re-arm) ----------------------
if [ -f "$VERDICT" ]; then
  log "GRADE-ONCE: verdict artifact $VERDICT already exists -- already graded, nothing to do; exiting 0"
  exit 0
fi

# L3 is ENDED when NEITHER pid exists. `kill -0 <pid>` returns 0 while the pid
# is alive (a permission error would also print nothing and return non-zero,
# but these are our own processes). We NEVER grade while either pid is alive.
l3_alive() {
  kill -0 "$L3_WRAP_PID" 2>/dev/null && return 0
  kill -0 "$L3_SOLVER_PID" 2>/dev/null && return 0
  return 1
}

# --- POLL loop -------------------------------------------------------------
# ~120s between polls; absolute ceiling 600 polls = 20h so it never loops
# forever (then grades anyway -- the comparator refuses fail-closed on an
# incomplete run, which is the honest outcome).
MAX_POLLS=600
i=0
ended=0
while [ "$i" -lt "$MAX_POLLS" ]; do
  if ! l3_alive; then
    log "L3 ENDED: neither wrapper($L3_WRAP_PID) nor solver($L3_SOLVER_PID) alive after ${i} polls"
    ended=1
    break
  fi
  # heartbeat every 10th poll (~20 min) to keep the log lean but alive
  if [ $((i % 10)) -eq 0 ]; then
    log "heartbeat poll=$i : L3 still alive (wrapper and/or solver present); waiting"
  fi
  i=$((i + 1))
  sleep 120
done

if [ "$ended" -eq 0 ]; then
  log "WATCH CEILING reached (${MAX_POLLS} polls ~20h) with L3 still apparently alive -- grading anyway; the comparator refuses fail-closed if L3 is incomplete (honest)"
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
         "verification/runs/T-family/T23_runs" \
         "verification/runs/T-family/T23G2R_runs"; do
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
# {L1,L2,L3} triple / per-quantity gate lines the comparator prints via note():
TRIPLE_LINES="$(grep -E 'G-PLATEAU|G-RATIO|G-ORDER|A2\.1|p\(Q4\)|G-YPLUS|G-MESHSIM|G-CONV|VERDICT:' "$STDOUT")"

# --- INTERPRETATION ---------------------------------------------------------
# Faithful to scripts/roache_triple.py exit-code map (0/1/2/3).
if [ "$GRC" -eq 2 ]; then
  if grep -qE 'rule 4 completion FAILED|NOT DONE' "$STDOUT"; then
    INTERP="exit 2 => REFUSE, and the stdout says rule-4 completion FAILED / NOT DONE.
INTERPRETATION: rung = PENDING (infra-confounded: L3 capped/incomplete, not a scientific NOT A RESULT); fresh-L3 re-run needed (new dir, endTime 28000, ~1063 core-min) per the pre-registered plan -- L1+L2 markers persist."
    WHOLE_RUNG_VERDICT="PENDING (infra-confounded -- L3 incomplete; fresh-L3 re-run needed)"
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
  echo "T23G2R WHOLE-RUNG VERDICT"
  echo "graded_at_utc : $(date -u +%FT%TZ)"
  echo "graded_by     : detached autograder autograde_t23g2r_l3.sh (pid $$, PPID at arm = $PPID)"
  echo "comparator    : $COMPARATOR"
  echo "comparator_pin: $COMPARATOR_PIN"
  echo "mark_done_pin : $MARKDONE_PIN"
  echo "comparator_rc : $GRC"
  echo "comparator_stdout: $STDOUT"
  echo ""
  echo "WHOLE-RUNG VERDICT: $WHOLE_RUNG_VERDICT"
  echo ""
  echo "--- comparator final line (verbatim) ---"
  [ -n "$RUNG_LINE" ] && echo "$RUNG_LINE"
  [ -n "$REFUSE_LINE" ] && echo "$REFUSE_LINE"
  echo ""
  echo "--- {L1,L2,L3} triple / per-quantity gate lines (verbatim from stdout) ---"
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
