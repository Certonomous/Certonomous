#!/usr/bin/env bash
# =============================================================================
# D6RF9 §2ba DETACHED AUTOGRADER  (charter v1.72 fa038083; mirrors cfd's M6)
# -----------------------------------------------------------------------------
# Polls the D6RF9 ladder ledger for completion, then AUTHORITATIVELY re-grades
# every real-solver rung with the FROZEN grader (md5-verified against the freeze
# pin), writing each grade JSON + a single DONE marker into the run root.  Run
# DETACHED under setsid (PPID=1, own session) so the verdict lands even after the
# agent fleet dies.
#
# It DECLARES NO verdict and files NO README row and NO cost-calibration row --
# those are the supervisor's calls after reading D6RF9_AUTOGRADE_DONE.txt.  This
# is an OPERATIONAL script (outside the freeze ed181847): it only READS the
# frozen grader after verifying its md5, and REFUSES (exit 2) if the md5 drifted.
# =============================================================================
set -u
RUN_ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D6RF9-a2-wing-convergence-probe
LEDGER="$RUN_ROOT/ledger.txt"
GRADER=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6RF9/d6rf9_grade.py
GRADER_MD5=6e76ed57ac6890b0a7fa260c46dc517b
DONE="$RUN_ROOT/D6RF9_AUTOGRADE_DONE.txt"
LOG="$RUN_ROOT/d6rf9_autograde.out"
CEIL=5400            # 90-min hard ceiling
POLL=30

echo "AUTOGRADE_START $(date -u +%FT%TZ) pid=$$ ppid=$PPID cpuset-agnostic (grading only)" >> "$LOG"
t0=$(date +%s)

# 1. Poll for ladder completion, bounded.  KEY ONLY on the ledger's own
#    D6RF9_LADDER_DONE line -- the authoritative completion marker the launcher
#    writes.  (A prior version also grepped d6rf9_launch*.out for LADDER_RC=,
#    which false-matched STALE launch .out files from earlier aborted attempts
#    and fired the autograder mid-R1; fixed 2026-09-09.)
while :; do
  if grep -qE 'D6RF9_LADDER_DONE' "$LEDGER" 2>/dev/null; then
    echo "TERMINATION seen (D6RF9_LADDER_DONE) $(date -u +%FT%TZ)" >> "$LOG"; break
  fi
  now=$(date +%s)
  if [ $((now - t0)) -ge "$CEIL" ]; then
    echo "CEILING ${CEIL}s hit $(date -u +%FT%TZ) -- grading whatever landed" >> "$LOG"; break
  fi
  sleep "$POLL"
done

# 2. Verify the frozen grader md5 -- REFUSE (exit 2) rather than grade with a drifted instrument.
GOT=$(md5sum "$GRADER" 2>/dev/null | cut -d' ' -f1)
if [ "$GOT" != "$GRADER_MD5" ]; then
  echo "REFUSE: grader md5 $GOT != frozen $GRADER_MD5 $(date -u +%FT%TZ)" >> "$LOG"
  {
    echo "D6RF9 AUTOGRADE REFUSED $(date -u +%FT%TZ)"
    echo "grader md5 drift: $GOT != frozen $GRADER_MD5 -- NOT graded (instrument integrity)."
  } > "$DONE"
  exit 2
fi

# 3. Authoritatively grade each real-solver rung log (skip pure config-install aborts).
{
  echo "D6RF9_AUTOGRADE_DONE $(date -u +%FT%TZ)"
  echo "grader=$GRADER md5=$GOT (frozen ed181847 pin, VERIFIED)  invocation: --log <log> --rung <Rn>  (NO --skip-freeze)"
  echo "ledger tail:"
  tail -40 "$LEDGER" 2>/dev/null | sed 's/^/  /'
  echo "----- per-rung authoritative grades (frozen grader; controls self-run) -----"
} > "$DONE"

any_pass=0
graded=0
for L in "$RUN_ROOT"/R[1-4]_*.log; do
  [ -f "$L" ] || continue
  base=$(basename "$L"); rung=${base%%_*}
  if grep -q 'D6RF9_LEG_ABORT' "$L" && ! grep -q 'Time = ' "$L"; then
    echo ">>> $rung  SKIPPED (config-install abort, solver never ran): $L" >> "$DONE"
    continue
  fi
  GJSON="$RUN_ROOT/${rung}_autograde.json"
  python3 "$GRADER" --log "$L" --rung "$rung" > "$GJSON" 2>>"$LOG"; rc=$?
  graded=$((graded+1))
  echo ">>> $rung  grade_rc=$rc  log=$L  json=$GJSON" >> "$DONE"
  sed 's/^/    /' "$GJSON" >> "$DONE" 2>/dev/null
  # any_pass keys ONLY on the single authoritative "binding_verdict" field.
  # (Fixed 2026-09-09: the prior regex also alternated on '"verdict":"PASS"'
  #  and a bare '"PASS"', which matched per-FIELD verdicts (U0/p_corrected) and
  #  the control states "EXERCISED-PASS" -- so it reported any_pass=1 on the
  #  all-GATE-FAIL/NOT-A-RESULT D6RF9 ladder. Cosmetic aggregation false
  #  positive, not a grading error; the per-rung binding verdicts read direct
  #  were always correct. There is exactly one binding_verdict line per grade
  #  json; a rung that truly reaches the floor grades binding_verdict PASS.)
  grep -qE '"binding_verdict"[[:space:]]*:[[:space:]]*"PASS"' "$GJSON" 2>/dev/null && any_pass=1
done

{
  echo "----- LADDER OUTCOME (supervisor reads + declares; NOT declared here) -----"
  if [ "$graded" -eq 0 ]; then
    echo "NO real-solver rung graded -- all logs were config-install aborts (a defect, not a result)."
  elif [ "$any_pass" -eq 1 ]; then
    echo "At least one rung shows PASS -> a rung reached the 1.0e-05 floor: this UNBLOCKS the mandatory D6R2 transonic multipoint. Supervisor: verify + declare the item verdict + README two-row + cost row."
  else
    echo "All graded rungs ran to endTime and none reached the 1.0e-05 floor -> a MEASURED N-D43 capability-exhaustion finding for Sanaa (NOT a failure to hide). Supervisor: verify + declare."
  fi
  echo "AUTOGRADE_COMPLETE $(date -u +%FT%TZ) graded=$graded any_pass=$any_pass"
} >> "$DONE"
echo "AUTOGRADE_COMPLETE $(date -u +%FT%TZ) graded=$graded any_pass=$any_pass" >> "$LOG"
