#!/usr/bin/env bash
# autograde_m1c.sh -- M1-C DETACHED AUTOGRADER (sec 2ba detached grader half).
# FROZEN 2026-09-09 -- §3 check-1 diff-read done by the closure-supervisor (SOUND);
# frozen at the M1-C freeze commit alongside PREREGISTRATION.md.
#
# WHAT IT IS.  A no-live-agent grader.  Launched detached (setsid nohup) it:
#   1. RE-HASHES the frozen grade_m1d.py against its pinned sha256 and REFUSES on
#      any mismatch (the grading path is fixed at the M1-C freeze; a moved grader
#      is not the graded instrument).
#   2. Waits (bounded) until all SIX M1-C arms satisfy the strict rule-4 completion
#      rule, reading each arm's OWN STATUS + log.run (no live solver agent needed).
#   3. Builds a READ-ONLY MERGED symlink root so the frozen grade_m1d.py -- which
#      grades the full 78-arm sweep from one --root -- sees the 72 untouched M1
#      arms AND the 6 fresh M1-C arms, WITHOUT writing into either evidence tree.
#      >>> TOPOLOGY DECISION, FLAGGED FOR THE SUPERVISOR (see PREREGISTRATION ADDENDUM
#          sec A.4): grade_m1d.py takes a single --root; M1-C runs live in a disjoint
#          tree per the rule-4 birth guard, so a merged symlink view is how one grade
#          sees all 78.  Symlinks preserve real mtimes, so the age guard is unaffected.
#   4. Runs grade_m1d.py ONCE, CAPTURING ITS rc INSIDE THIS WRAPPER (L: setsid/timeout
#      parents return 0 for every outcome), and writes that rc to a STATUS file that
#      is the authoritative completion witness.
#
# It NEVER edits grade_m1d.py, never writes into multimodel_sweep/ or m1c_completion/
# field trees, and computes no verdict of its own -- grade_m1d.py is the sole judge.
set -uo pipefail

REPO="/home/ubuntu/Certonomous"
GRADER="$REPO/cases/RANS_LES_closure_models/M1d_multimodel_sweep_g1fix/grade_m1d.py"
PIN="a1ee190550e94be13fb2fc678379e1c23275b9fd4f002905073776d263628790"
BENCH="/home/ubuntu/closure-challenge-benchmark/data"
M1_ROOT="/home/ubuntu/closure-data/multimodel_sweep"
M1C_ROOT="/home/ubuntu/closure-data/m1c_completion"
MERGED="/home/ubuntu/closure-data/m1c_graded"
OUT="$M1C_ROOT/gate_m1c.json"
STATUS="$M1C_ROOT/STATUS.autograde_m1c"
LOG="$M1C_ROOT/autograde_m1c.log"
ENDTIME=20000
POLL_S=60
MAX_WAIT_S=39600          # 11 h ceiling; > sum of the six caps (~6.3 core-h) with margin
PHYS_FIELDS="T U p_rgh alphat nut k omega phi"   # rule-4 thermal-family field set; M1 uses the incompressible subset present in each case

# The six M1-C arms, arm/case (PH first).
ARMS6=( "kOmega/PH_Breuer" "kOmegaSST_null/PH_Breuer" "kOmega/AR_14_Ret_180" \
        "kOmega/AR_7_Ret_180" "kOmega/AR_1_Ret_180" "kOmegaSST_null/AR_1_Ret_180" )

stamp(){ date -u +%Y-%m-%dT%H:%M:%SZ; }
say(){ echo "[$(stamp)] $*" >>"$LOG"; }

write_status(){  # phase rc detail
  printf 'phase=%s\nrc=%s\nutc=%s\ndetail=%s\ngrader=%s\ngrader_sha_pin=%s\nout=%s\n' \
    "$1" "$2" "$(stamp)" "$3" "$GRADER" "$PIN" "$OUT" >"$STATUS"
}

: >"$LOG"; write_status "STARTED" "na" "autograder launched, no live agent"
say "autograde_m1c start"

# --- 1. FREEZE GATE: re-hash the grader against its pin -----------------------
if [ ! -f "$GRADER" ]; then
  write_status "REFUSED" 2 "grader absent at pinned path"; say "REFUSE grader absent"; exit 2
fi
GOT=$(sha256sum "$GRADER" | awk '{print $1}')
if [ "$GOT" != "$PIN" ]; then
  write_status "REFUSED" 2 "grader sha256 $GOT != pin $PIN -- grading path not the graded instrument"
  say "REFUSE sha mismatch got=$GOT pin=$PIN"; exit 2
fi
say "freeze gate OK: grade_m1d.py sha256 == pin"

# --- 2. rule-4 completion poll on the six arms --------------------------------
arm_complete(){  # arm/case -> 0 if strictly complete
  local ac="$1" d="$M1C_ROOT/$ac" st="$M1C_ROOT/$ac/STATUS.M1c_${ac//\//__}"
  # rc=0 from the run_m1.sh STATUS (rc captured inside that wrapper)
  local S="$d/STATUS"
  [ -f "$S" ] || return 1
  grep -q '^rc=0$' "$S" || return 1
  # End line + last time == endTime in the solver log
  local lg="$d/log.run"
  [ -f "$lg" ] || return 1
  grep -qa '^End$' "$lg" || return 1
  local lastT; lastT=$(grep -a '^Time = ' "$lg" | tail -1 | awk '{print $3}')
  [ "$lastT" = "$ENDTIME" ] || return 1
  # endTime field dir present, with U at least
  [ -f "$d/$ENDTIME/U" ] || return 1
  # age guard: endTime/U newer than 0/U
  [ "$d/$ENDTIME/U" -nt "$d/0/U" ] || return 1
  return 0
}

waited=0
while :; do
  done_n=0
  for ac in "${ARMS6[@]}"; do arm_complete "$ac" && done_n=$((done_n+1)); done
  say "completion poll: $done_n/6 arms strictly complete"
  [ "$done_n" -eq 6 ] && break
  if [ "$waited" -ge "$MAX_WAIT_S" ]; then
    write_status "TIMEOUT" 3 "only $done_n/6 arms complete after ${MAX_WAIT_S}s; NOT grading a partial sweep"
    say "TIMEOUT $done_n/6"; exit 3
  fi
  sleep "$POLL_S"; waited=$((waited+POLL_S))
done
say "all 6 arms strictly complete per rule-4"

# --- 3. read-only merged symlink root (72 M1 + 6 M1-C), no evidence-tree writes
rm -rf "$MERGED"; mkdir -p "$MERGED"
for arm in kOmega kOmegaSST_null; do
  mkdir -p "$MERGED/$arm"
  if [ -d "$M1_ROOT/$arm" ]; then
    for cdir in "$M1_ROOT/$arm"/*/; do
      cid=$(basename "$cdir"); ln -sfn "$M1_ROOT/$arm/$cid" "$MERGED/$arm/$cid"
    done
  fi
done
# overlay the 6 fresh M1-C arms (repoint the symlink at the new tree)
for ac in "${ARMS6[@]}"; do
  ln -sfn "$M1C_ROOT/$ac" "$MERGED/$ac"
done
say "merged symlink root built at $MERGED"

# --- 4. grade ONCE, rc captured INSIDE this wrapper ---------------------------
python3 "$GRADER" --root "$MERGED" --bench-root "$BENCH" --out "$OUT" >>"$LOG" 2>&1
GRC=$?
say "grade_m1d.py returned rc=$GRC (captured inside wrapper), gate at $OUT"
write_status "GRADED" "$GRC" "grade_m1d.py rc=$GRC; merged 78-arm root; see $OUT and $LOG"
exit "$GRC"
