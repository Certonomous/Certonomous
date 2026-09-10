#!/bin/bash
# ===========================================================================
# DETACHED WHOLE-RUNG AUTOGRADER for T4e (heat-transfer, 2026-09-10).
# Structural mirror of verification/runs/T-family/T23G2Rn2_runs/autograde_t23g2rn2.sh.
#
# T4e launches all three levels CONCURRENTLY (none is pre-DONE), so this waits
# for ALL THREE levels to finish, then runs the FROZEN completion instrument and
# the FROZEN comparator ONCE over the whole rung and writes the rung verdict
# artifact to disk, so a returning agent finds a GRADED record, not raw fields.
#
# ARMED with setsid so PPID becomes 1 and it survives the launching lane's exit
# AND a whole-fleet death (agent-watchers-die-with-the-agent).
#
# rc is captured INSIDE this wrapper (`setsid timeout cmd` exits 0 for every
# outcome; capture rc inside the detached wrapper, never around the setsid line).
#
# THE VERDICT COMES ENTIRELY FROM THE FROZEN INSTRUMENTS.  This watcher adds NO
# grading judgment of its own.  Grading path, pinned by blob at the T4e freeze
# (T4e_PREREGISTRATION.md section 12; every one re-verified MATCH against
# `git ls-tree HEAD` before launch, 2026-09-10):
#     analyse_t4e.py      740575a7      mark_done_t4e.py    e4e44396
#     build_t4e.py        6e77d62f      launch_t4e.sh       441ccdfb
#     T4e_registered.json a11380c6      trajectory_t4e.py   512b3691
#   frozen imports: T4_runs/analyse_t4.py 6f362447 ; scripts/roache_triple.py 78e56a3b
#   comparator self-pin: the FREEZE-PIN line analyse_t4e.py@740575a7 in the
#   freeze commit message (a file cannot contain its own committed hash).
#
# COMPARATOR EXIT MAP, read from analyse_t4e.py itself (line 92:
#   EXIT_OK, EXIT_SELFTEST_FAIL, EXIT_REFUSE = 0, 1, 2):
#     0 = graded (rows written to gate_t4e.json; the ROW verdicts carry
#         PASS / GATE FAIL / NOT A RESULT -- see the honest note below)
#     1 = selftest fail        2 = REFUSED (default-deny)
# NOTE, STATED PLAINLY: unlike analyse_t23g2rn2.py, analyse_t4e.py prints NO
# single "RUNG VERDICT:" line and its exit code is NOT the roache_triple 0/1/2/3
# map -- it returns EXIT_OK once it has graded, whatever the row verdicts are.
# The rung's verdict therefore lives in the PER-ROW lines (G1/G2/G3 ... -> <verdict>)
# and in gate_t4e.json.  This artifact records those lines VERBATIM and does not
# synthesise a rung-level verdict of its own.
#
# T4e COMPLETION SEMANTICS (T4e_PREREGISTRATION.md sections 3b / 11, registered
# BEFORE compute).  A refusal for NOT DONE on the FINE level is NOT automatically
# an infrastructure confound: the registered D1 branch DELIBERATELY stops the fine
# leg early on robust limit-cycle confirmation, in which case mark_done_t4e.py
# correctly reports NOT DONE and analyse_t4e.py correctly refuses.  The two are
# told apart by the presence of the instrument-written marker
#   D1_CONFIRMED_TERMINATE.T4e_IJ_f
# which this watcher REPORTS AS A FACT (present / absent).  It does not itself
# decide which branch obtains -- that is the supervisor's read.
# ===========================================================================
set +e

REPO=/home/ubuntu/Certonomous
cd "$REPO" || exit 1

RR="verification/runs/T-family/T4e_runs"
COMPARATOR="$RR/analyse_t4e.py"
MARKDONE="$RR/mark_done_t4e.py"
COMPARATOR_PIN="740575a7"
MARKDONE_PIN="e4e44396"
ANALYSE_T4_PIN="6f362447"
ROACHE_PIN="78e56a3b"

WATCHLOG="$RR/autograde_rung.watch.log"
MD_STDOUT="$RR/T4e_MARKDONE_STDOUT.txt"
STDOUT="$RR/T4e_COMPARATOR_STDOUT.txt"
VERDICT="$RR/T4e_RUNG_VERDICT.txt"

CASES="T4e_IJ_c T4e_IJ_m T4e_IJ_f"

log() { echo "$(date -u +%FT%TZ) $*" >> "$WATCHLOG"; }

log "ARMED pid=$$ ppid=$PPID sid=$(ps -o sid= -p $$ 2>/dev/null | tr -d ' ') -- detached T4e WHOLE-RUNG autograder"
log "watching cases: $CASES ; comparator pin $COMPARATOR_PIN ; mark_done pin $MARKDONE_PIN ; frozen imports $ANALYSE_T4_PIN / $ROACHE_PIN"

# --- GRADE-ONCE guard (idempotent; survives a re-arm) ----------------------
if [ -f "$VERDICT" ]; then
  log "GRADE-ONCE: $VERDICT already exists -- already graded, nothing to do; exiting 0"
  exit 0
fi

# --- readiness ------------------------------------------------------------
# launch_t4e.sh writes STATUS.<case> in the run root AFTER the solver has
# returned and its rc has been captured (that file IS the launcher's completion
# contract, and is what mark_done_t4e.py reads).  A missing STATUS means that
# level is still running or was never launched -- we NEVER grade a rung that is
# not fully finished (fail-safe).  Belt and braces: we also refuse to grade
# while ANY process still holds one of the case directories as its cwd.
rung_alive() {
  local seen=0
  for c in $CASES; do
    [ -f "$RR/STATUS.$c" ] || return 0          # not finished (or not launched)
    seen=$((seen + 1))
  done
  for c in $CASES; do
    local cd_abs="$REPO/$RR/$c"
    for p in /proc/[0-9]*; do
      [ "$(readlink "$p/cwd" 2>/dev/null)" = "$cd_abs" ] && return 0
    done
  done
  [ "$seen" -eq 3 ] && return 1
  return 0
}

# --- POLL loop -------------------------------------------------------------
# 120 s between polls.  Absolute ceiling MUST exceed the largest per-level CAP:
# the FINE leg's registered timeout_s is 360060 s = 100.0 h (T4e_registered.json
# cases.T4e_IJ_f.timeout_s), so a ceiling below that would grade before the fine
# leg finished.  MAX_POLLS=3120 = 374400 s = 104.0 h > 100.0 h, with margin.
MAX_POLLS=3120
i=0
ended=0
while [ "$i" -lt "$MAX_POLLS" ]; do
  if ! rung_alive; then
    log "RUNG ENDED: all three STATUS files present and no process holds a case dir, after ${i} polls"
    ended=1
    break
  fi
  if [ $((i % 30)) -eq 0 ]; then
    log "heartbeat poll=$i : rung still alive; STATUS present: $(for c in $CASES; do [ -f "$RR/STATUS.$c" ] && printf '%s ' "$c"; done)"
  fi
  i=$((i + 1))
  sleep 120
done

if [ "$ended" -eq 0 ]; then
  log "WATCH CEILING reached (${MAX_POLLS} polls ~104 h) with the rung still apparently alive -- grading anyway; the instruments refuse fail-closed on an incomplete run, which is the honest outcome"
fi

if [ -f "$VERDICT" ]; then
  log "GRADE-ONCE (post-wait): verdict artifact appeared during the wait -- already graded; exiting 0"
  exit 0
fi

# --- (a) clear stale bytecode BEFORE grading (stale-pycache lesson) ---------
log "clearing stale __pycache__ on the grading path"
for d in "$RR" "verification/runs/T-family/T4_runs" "scripts"; do
  find "$d" -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null
done

# --- (b) the FROZEN completion instrument (rule 4 + age guard) --------------
log "running frozen completion instrument: python3 $MARKDONE --root $RR"
python3 "$MARKDONE" --root "$RR" > "$MD_STDOUT" 2>&1
MDRC=$?
log "mark_done finished rc=$MDRC ; stdout captured to $MD_STDOUT"

# --- (c) the FROZEN comparator, stdout+stderr and exit code captured -------
log "running frozen comparator: python3 $COMPARATOR (the verdict is ENTIRELY its stdout + exit code)"
python3 "$COMPARATOR" > "$STDOUT" 2>&1
GRC=$?
log "comparator finished rc=$GRC ; stdout captured to $STDOUT"

# --- extract, VERBATIM, what the comparator actually printed ---------------
ROW_LINES="$(grep -E '^(G1|G2|G3) ' "$STDOUT")"
LEVEL_LINES="$(grep -E '^level [cmf] ' "$STDOUT")"
REFUSE_LINE="$(grep -E 'REFUSE' "$STDOUT" | tail -1)"
FINAL_LINE="$(grep -vE '^\s*$' "$STDOUT" | tail -1)"
D1_MARKER="$RR/D1_CONFIRMED_TERMINATE.T4e_IJ_f"
if [ -f "$D1_MARKER" ]; then D1_STATE="PRESENT ($D1_MARKER)"; else D1_STATE="ABSENT"; fi

# --- INTERPRETATION (faithful to analyse_t4e.py's OWN exit map, line 92) ----
if [ "$GRC" -eq 2 ]; then
  if grep -qE 'no DONE\.|NOT DONE' "$STDOUT" "$MD_STDOUT"; then
    if [ -f "$D1_MARKER" ]; then
      INTERP="exit 2 => REFUSE for a missing DONE marker, AND the instrument-written D1 marker IS PRESENT.
Per the pre-registered completion semantics (T4e_PREREGISTRATION.md sections 3b/11, frozen before compute) this is the REGISTERED D1 branch: the fine leg was DELIBERATELY stopped on robust limit-cycle confirmation, so mark_done correctly reports NOT DONE and the comparator correctly refuses to grade a triple that has no converged fine field. The finding is read from the D1 marker + the trajectory, NOT from this comparator. Which branch obtains is the SUPERVISOR's read, not this watcher's."
    else
      INTERP="exit 2 => REFUSE for a missing DONE marker, and NO D1 marker is present.
This is an INCOMPLETE / infra-confounded run (a level capped, crashed or short), not a scientific verdict. Read $MD_STDOUT for the failing rule-4 clause and the per-level STATUS files for rc/capped."
    fi
  else
    INTERP="exit 2 => REFUSE (default-deny) for a reason that is NOT a missing DONE marker -- a planted-zero control or reader refusal. The refusal line is recorded verbatim below and MUST be triaged before anything here is believed."
  fi
elif [ "$GRC" -eq 0 ]; then
  INTERP="exit 0 => the comparator GRADED the rung and wrote gate_t4e.json.
Note plainly: analyse_t4e.py returns EXIT_OK once it has graded, WHATEVER the row verdicts are -- its exit code is NOT the roache_triple 0/1/2/3 map and it prints no single 'RUNG VERDICT:' line. The rung's verdict is carried by the PER-ROW lines recorded verbatim below and by gate_t4e.json. Rule 5 governs: a row whose triple is not CONVERGING is NOT A RESULT whatever its value."
elif [ "$GRC" -eq 1 ]; then
  INTERP="exit 1 => SELFTEST FAIL path in analyse_t4e.py. Nothing here is a result; the instrument itself must be triaged."
else
  INTERP="UNEXPECTED comparator rc=$GRC (not in {0,1,2}); the comparator may itself be broken. Inspect $STDOUT before trusting anything."
fi

# --- write the durable verdict artifact -------------------------------------
{
  echo "T4e WHOLE-RUNG VERDICT ARTIFACT"
  echo "graded_at_utc  : $(date -u +%FT%TZ)"
  echo "graded_by      : detached autograder autograde_t4e.sh (pid $$, PPID at arm = $PPID)"
  echo "comparator     : $COMPARATOR   pin $COMPARATOR_PIN"
  echo "mark_done      : $MARKDONE   pin $MARKDONE_PIN"
  echo "frozen imports : T4_runs/analyse_t4.py $ANALYSE_T4_PIN ; scripts/roache_triple.py $ROACHE_PIN"
  echo "mark_done_rc   : $MDRC   (stdout: $MD_STDOUT)"
  echo "COMPARATOR EXIT CODE: $GRC   (stdout: $STDOUT)"
  echo "D1 marker      : $D1_STATE"
  echo ""
  echo "--- comparator FINAL LINE (verbatim, last non-blank line of its stdout) ---"
  echo "$FINAL_LINE"
  echo ""
  echo "--- comparator PER-ROW verdict lines (verbatim) ---"
  if [ -n "$ROW_LINES" ]; then echo "$ROW_LINES"; else echo "(no G1/G2/G3 row lines -- the comparator refused before grading; see $STDOUT)"; fi
  echo ""
  echo "--- comparator PER-LEVEL control lines (verbatim) ---"
  if [ -n "$LEVEL_LINES" ]; then echo "$LEVEL_LINES"; else echo "(none)"; fi
  echo ""
  echo "--- refusal line, if any (verbatim) ---"
  if [ -n "$REFUSE_LINE" ]; then echo "$REFUSE_LINE"; else echo "(none)"; fi
  echo ""
  echo "--- completion instrument stdout (verbatim) ---"
  cat "$MD_STDOUT" 2>/dev/null || echo "(missing)"
  echo ""
  echo "--- per-leg STATUS (cost, rule 12: core-minutes) ---"
  for c in $CASES; do
    echo "[$c]"
    cat "$RR/STATUS.$c" 2>/dev/null || echo "  (no STATUS -- this leg never finished)"
  done
  echo ""
  echo "--- INTERPRETATION ---"
  echo "$INTERP"
  echo ""
  echo "NOTE: this artifact is the FROZEN INSTRUMENTS' stdout + exit codes on disk."
  echo "A returning agent STILL OWES the supervisor's diff-read (SUPERVISION_CHARTER section 3:"
  echo "measurement-script diffs read as diffs, crash triage, big-claim verification) BEFORE this"
  echo "verdict is repeated upward. This watcher graded nothing itself and asserts no verdict of its own."
} > "$VERDICT"

log "VERDICT ARTIFACT WRITTEN to $VERDICT (comparator rc=$GRC, mark_done rc=$MDRC, D1 marker $D1_STATE)"
log "COMPLETE -- exiting 0"
exit 0
