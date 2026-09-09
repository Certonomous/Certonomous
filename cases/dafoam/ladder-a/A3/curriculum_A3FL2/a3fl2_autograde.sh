#!/usr/bin/env bash
# =============================================================================
# A3FL2 §2ba DETACHED AUTOGRADER  (mirrors a3fl1_autograde.sh / d6rf10_autograde.sh)
# -----------------------------------------------------------------------------
# Polls the A3FL2 run-root ledger for completion, then grades each leg log with
# the FROZEN grader (md5-verified against the freeze pin), writing per-leg grade
# JSONs + a single DONE marker into the run root.  Runs DETACHED under setsid
# (PPID=1) so the verdict lands even after the agent fleet dies.
#
# It DECLARES NO verdict and files NO README row and NO cost-calibration row --
# those are the dafoam-supervisor's calls after reading A3FL2_AUTOGRADE_DONE.txt.
# It only READS the frozen grader after verifying its md5, and REFUSES (exit 2)
# if the md5 drifted.  OPERATIONAL script (outside the freeze).
# =============================================================================
set -u
RUN_ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-A3FL2-onera-m6-free-conditioning-levers
LEDGER="$RUN_ROOT/ledger.txt"
GRADER=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A3/curriculum_A3FL2/a3fl2_grade.py
GRADER_MD5="<SET_AT_FREEZE>"   # supervisor pins md5(a3fl2_grade.py) at freeze; the md5-drift limb REFUSES
                               # (exit 2) if the on-disk grader ever drifts from this pin, so the autograder
                               # never grades with an unpinned/mutated instrument.
DONE="$RUN_ROOT/A3FL2_AUTOGRADE_DONE.txt"
LOG="$RUN_ROOT/a3fl2_autograde.out"
# CEIL = all three legs' deadlines (600 + 1800 + 1800) + a conditional FD leg (~90 min cap) + margin.
CEIL=12000           # 3.3 h -- covers CONTROL 600s + BASELINE_R3 1800s + TEST_R3 1800s + FD ~5400s + margin
POLL=30

echo "A3FL2_AUTOGRADE_START $(date -u +%FT%TZ) pid=$$ ppid=$PPID" >> "$LOG"
t0=$(date +%s)

# 1. Poll for ladder completion, bounded.  KEY ONLY on the ledger's own A3FL2_LADDER_DONE line.
while :; do
  if grep -qE 'A3FL2_LADDER_DONE' "$LEDGER" 2>/dev/null; then
    echo "TERMINATION seen (A3FL2_LADDER_DONE) $(date -u +%FT%TZ)" >> "$LOG"; break
  fi
  now=$(date +%s)
  if [ $((now - t0)) -ge "$CEIL" ]; then
    echo "CEILING ${CEIL}s hit $(date -u +%FT%TZ) -- grading whatever landed" >> "$LOG"; break
  fi
  sleep "$POLL"
done

# 2. Verify the frozen grader md5 -- REFUSE (exit 2) rather than grade with a drifted/unpinned instrument.
case "$GRADER_MD5" in *SET_AT_FREEZE*|"")
  echo "REFUSE: GRADER_MD5 is a placeholder -- supervisor pins it at freeze $(date -u +%FT%TZ)" >> "$LOG"
  {
    echo "A3FL2 AUTOGRADE REFUSED $(date -u +%FT%TZ)"
    echo "GRADER_MD5 is a placeholder (DRAFT) -- NOT graded until the supervisor pins it at freeze."
  } > "$DONE"
  exit 2 ;;
esac
GOT=$(md5sum "$GRADER" 2>/dev/null | cut -d' ' -f1)
if [ "$GOT" != "$GRADER_MD5" ]; then
  echo "REFUSE: grader md5 $GOT != frozen $GRADER_MD5 $(date -u +%FT%TZ)" >> "$LOG"
  {
    echo "A3FL2 AUTOGRADE REFUSED $(date -u +%FT%TZ)"
    echo "grader md5 drift: $GOT != frozen $GRADER_MD5 -- NOT graded (instrument integrity)."
  } > "$DONE"
  exit 2
fi

# 3. Grade each leg log with the frozen grader.
{
  echo "A3FL2_AUTOGRADE_DONE $(date -u +%FT%TZ)"
  echo "grader=$GRADER md5=$GOT (frozen, VERIFIED)  invocation: --log <leg log> --leg CONTROL|BASELINE_R3|TEST_R3 [--fd-json ...]"
  echo "ledger tail:"; tail -20 "$LEDGER" 2>/dev/null | sed 's/^/  /'
  echo "----- per-leg grades (frozen grader; planted controls self-run) -----"
} > "$DONE"

graded=0
for LEG in CONTROL BASELINE_R3 TEST_R3; do
  L="$RUN_ROOT/$LEG/a3fl2_${LEG}.log"
  [ -f "$L" ] || { echo ">>> $LEG  NO LOG at $L (leg did not run)" >> "$DONE"; continue; }
  GJSON="$RUN_ROOT/${LEG}_autograde.json"
  FD=""
  # TEST_R3 FD table is graded only if the launcher produced it (TEST_R3 converged -> FD leg ran).
  [ "$LEG" = "TEST_R3" ] && [ -f "$RUN_ROOT/TEST_R3/a3fl2_fd.json" ] && FD="--fd-json $RUN_ROOT/TEST_R3/a3fl2_fd.json --run-base $RUN_ROOT/TEST_R3"
  python3 "$GRADER" --log "$L" --leg "$LEG" $FD --out "$GJSON" >> "$LOG" 2>&1; rc=$?
  graded=$((graded+1))
  echo ">>> $LEG  grade_rc=$rc  log=$L  json=$GJSON" >> "$DONE"
  sed 's/^/    /' "$GJSON" >> "$DONE" 2>/dev/null
done

{
  echo "----- ITEM OUTCOME (dafoam-supervisor reads the THREE leg JSONs, composes per prereg §7, declares) -----"
  echo "The item verdict is NOT declared here.  The supervisor composes it from the CONTROL, BASELINE_R3 and"
  echo "TEST_R3 leg grade JSONs using the §7 map (CONTROL breaks? -> BASELINE_R3 reproduces the -3 wall? ->"
  echo "TEST_R3 nd effect), verifies, then declares + files the README row + the docs/COST_CALIBRATION.md row."
  echo "A3FL2_AUTOGRADE_COMPLETE $(date -u +%FT%TZ) graded=$graded"
} >> "$DONE"
echo "A3FL2_AUTOGRADE_COMPLETE $(date -u +%FT%TZ) graded=$graded" >> "$LOG"
