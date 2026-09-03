#!/bin/bash
# T25R6a ARM RUNNER -- ONE CASE, 40 STEPS, endTime 0.8 (prereg section 9).
#
#   run_one_t25R6a.sh --case-dir <abs case dir> --timeout <s> --ranks 2
#
# rc IS CAPTURED INSIDE, immediately after mpirun.  A `setsid timeout ...` line
# exits 0 for EVERY outcome including a kill, so an rc read around it is a
# constant zero that means nothing (T25R3 section 6.3).
set -o pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
T25R5="$(cd "$HERE/../T25R5_LINSOLVER_runs" && pwd)"

# --- FROZEN AT PREREG 8.2.  Per-run caps set by the team at ~3x each run's own
# --- estimate (Sanaa 2026-09-03 18:00Z item 2).  timeout_s = cap_core_min*60/ranks.
declare -A REG_TIMEOUT=( [L1]=396 [L3]=2970 )
declare -A REG_CAP=( [L1]=13.20 [L3]=99.00 )
RANKS_REG=2
# --- FROZEN: the E6 dictionary verifier, delegated and blob-verified.
VERIFY_BLOB="3a0945445d10762f6b549e729c704ac93df68f4e"

CASE=""; TO=""; RANKS=""
while [ $# -gt 0 ]; do
  case "$1" in
    --case-dir) CASE="$2"; shift 2 ;;
    --timeout)  TO="$2";   shift 2 ;;
    --ranks)    RANKS="$2"; shift 2 ;;
    --no-detach) shift ;;
    *) echo "REFUSE: unknown argument $1"; exit 80 ;;
  esac
done

[ -n "$CASE" ] || { echo "REFUSE: --case-dir is required"; exit 81; }
RUN="$(basename "$CASE")"
trap 'S=$?; [ -d "$CASE" ] && echo "$S" > "$CASE/.rc.$RUN.launcher"; \
      echo "launcher exit rc=$S"' EXIT

case "$RUN" in
  *_L1) LV=L1 ;;
  *_L3) LV=L3 ;;
  *) echo "REFUSE: $RUN carries no registered level suffix (_L1/_L3)"; exit 91 ;;
esac

# --- THE CAP IS ENFORCED, NOT INTENDED.  A cap nothing enforces is not a cap:
# --- refuse a --timeout that is not the registered one, and refuse if the
# --- registered timeout does not equal cap_core_min * 60 / ranks.
[ -n "$RANKS" ] || RANKS=$RANKS_REG
[ "$RANKS" = "$RANKS_REG" ] || { echo "REFUSE: --ranks $RANKS != registered $RANKS_REG"; exit 82; }
WANT=${REG_TIMEOUT[$LV]}
[ -n "$TO" ] || TO=$WANT
[ "$TO" = "$WANT" ] || { echo "REFUSE: --timeout $TO != registered timeout_s $WANT for $LV"; exit 83; }
PROD=$(python3 -c "print(int(round(${REG_CAP[$LV]}*60/$RANKS_REG)))")
[ "$WANT" = "$PROD" ] || { echo "REFUSE: registered timeout_s $WANT != cap ${REG_CAP[$LV]}*60/$RANKS_REG = $PROD"; exit 84; }
echo "  cap check: $LV cap ${REG_CAP[$LV]} core-min x 60 / $RANKS_REG ranks = ${PROD}s = registered timeout"

[ -d "$CASE" ] || { echo "REFUSE: no case dir $CASE"; exit 89; }

# --- E6 IS ENFORCED HERE, NOT ASSUMED, by the FROZEN T25R5 verifier.  Exit 0 is
# --- the FULL E6 verdict; exit 3 (ADMISSIBLE-DICTONLY) is NOT E6 and must not
# --- launch a solver.
V5="$T25R5/verify_arm_t25R5.py"
[ -f "$V5" ] || { echo "REFUSE: frozen verifier absent: $V5"; exit 85; }
GOT=$(python3 -c "
import hashlib,sys
d=open('$V5','rb').read()
h=hashlib.sha1(); h.update(b'blob %d\0'%len(d)); h.update(d); print(h.hexdigest())")
[ "$GOT" = "$VERIFY_BLOB" ] || { echo "REFUSE: verify_arm_t25R5.py is not the registered blob ($GOT != $VERIFY_BLOB)"; exit 86; }
echo "  ok   frozen E6 verifier is the registered blob ${VERIFY_BLOB:0:12}"

ARM="${RUN%_L*}"
python3 "$V5" --arm "$ARM" --case "$CASE"
V=$?
[ "$V" -eq 0 ] || { echo "REFUSE: verify_arm_t25R5.py returned $V (0 = full E6). Not launching."; exit 87; }

. /usr/lib/openfoam/openfoam2606/etc/bashrc > "$CASE/log.foamenv" 2>&1
command -v chtMultiRegionFoam >/dev/null 2>&1 || { echo "REFUSE: solver not on PATH"; exit 88; }
cd "$CASE" || exit 90

# --- RULE 4's AGE GUARD is only evaluable if `0/` is created HERE, at launch.
[ -d "$CASE/0" ] && { echo "REFUSE: 0/ exists; the age guard would be unevaluable"; exit 92; }
TD=$(find "$CASE" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended \
     -regex '.*/[0-9]+(\.[0-9]+)?$' 2>/dev/null | head -3)
[ -n "$TD" ] && { echo "REFUSE: time directory present: $TD"; exit 93; }
cp -r "$CASE/0.orig" "$CASE/0" || exit 94
sleep 1; touch "$CASE/0/module/T" || exit 95   # touched LAST: it DATES the run

decomposePar -allRegions -force > log.decomposePar 2>&1
D=$?; echo "$D" > ".rc.$RUN.decomposePar"; [ "$D" -eq 0 ] || exit 96

# --- CONTENTION WITNESS.  This rung's whole output is a TIMING RATIO and this
# --- box is shared.  Record the load either side so the ratio can be read with
# --- its environment rather than as if the box were quiet.
cat /proc/loadavg > ".load.$RUN.before"
date -u +%Y-%m-%dT%H:%M:%SZ > ".t.$RUN.start"

timeout "$TO" mpirun --bind-to none -np "$RANKS" chtMultiRegionFoam -parallel > log.solve.legA 2>&1
RC=$?                                   # <-- INSIDE, immediately after mpirun
echo "$RC" > ".rc.$RUN.legA"
date -u +%Y-%m-%dT%H:%M:%SZ > ".t.$RUN.end"
cat /proc/loadavg > ".load.$RUN.after"
echo "T25R6a $RUN rc=$RC (124 = CAP STOP; rule 12: an overrun stops the run.
  prereg 7.3: a cap-stop is a BOUND, not a disqualification -- the grader
  computes Sigma CAP at the bound and a censored run can never PASS.)"

python3 "$HERE/mark_done_t25R6a.py" --case "$CASE" || true
exit "$RC"
