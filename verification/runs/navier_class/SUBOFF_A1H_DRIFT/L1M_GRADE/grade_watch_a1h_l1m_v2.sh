#!/bin/bash
# SUBOFF A1h -- L1M SWEEP -- DETACHED LANDING GRADER, v2.
#
# v1 (grade_watch_a1h_l1m.sh) waited on the PRESENCE of solve_rc.  That was wrong and it
# was caught by the thing it was watching: all seven wrappers had ALREADY written
# solve_rc=1 when the solvers died at 00:11-00:14Z, so v1 fired at once.  v2 waits on the
# LANDING CONDITION ITSELF -- last Time == endTime AND solve_rc == 0 -- which a dead run
# cannot satisfy.  v1 was stopped by its own pid; NOTHING ELSE WAS TOUCHED.
#
# A NEW FILENAME, NOT AN EDIT.  Overwriting a running bash script in place is fatal (bash
# re-reads lazily by byte offset).  v1's path is never rewritten; v2 gets its own.
#
# rc IS CAPTURED INSIDE THIS WRAPPER.  `setsid timeout cmd` exits 0 for every outcome.
# IT GRADES; IT DOES NOT DECIDE.  The only verdict is the frozen comparator's.
# IT STOPS NOTHING and writes nothing into the seven cases (directive #17, read-only).
set +u
REPO=/home/ubuntu/Certonomous
SWEEP=$REPO/verification/runs/navier_class/SUBOFF_A1H_DRIFT/L1M_SWEEP
OUTD=$REPO/verification/runs/navier_class/SUBOFF_A1H_DRIFT/L1M_GRADE
CMP=$REPO/cases/navier_class/SUBOFF_A1/grade_suboff_a1h.py
CMP_FROZEN_BLOB=13ac40d3746d9e22716a9bddb4714a8f19a0d4d6
POINTS="BETA_m12 BETA_m08 BETA_m04 BETA_p00 BETA_p04 BETA_p08 BETA_p12"
END=3000
LOG=$OUTD/LANDING_v2.log
JSON=$OUTD/A1H_L1M_GRADE.json
WM=$OUTD/WINDOW_MEANS_REPORTED.json
DEADLINE=$(( $(date +%s) + 48*3600 ))
say() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $*" >> "$LOG"; }

say "WATCHER v2 START pid=$$ ppid=$PPID"
say "waiting on the LANDING CONDITION: last Time == $END AND solve_rc == 0, all seven"
while :; do
  MISSING=""
  for p in $POINTS; do
    RC=$(cat "$SWEEP/$p/solve_rc" 2>/dev/null)
    LT=$(tac "$SWEEP/$p/log.simpleFoam" 2>/dev/null | grep -m1 -E '^Time = ' | awk '{print $3}')
    [ "$RC" = "0" ] && [ "$LT" = "$END" ] || MISSING="$MISSING $p(rc=${RC:-none},t=${LT:-none})"
  done
  if [ -z "$MISSING" ]; then say "LANDING CONDITION MET on all seven"; break; fi
  if [ "$(date +%s)" -ge "$DEADLINE" ]; then
    say "48 h elapsed; points still unlanded:$MISSING -- grading anyway. NOTHING STOPPED."
    break
  fi
  sleep 60
done
sleep 120
NOW_BLOB=$(cd "$REPO" && git hash-object "$CMP" 2>/dev/null)
say "comparator blob now=$NOW_BLOB frozen=$CMP_FROZEN_BLOB"
if [ "$NOW_BLOB" != "$CMP_FROZEN_BLOB" ]; then
  say "BLOCKED: comparator on disk is not the frozen blob (rule 2). No grade produced."
  echo "2" > "$OUTD/A1H_L1M_GRADE.rc"; exit 2
fi
rm -rf "$OUTD/scratch"; mkdir -p "$OUTD/scratch"
python3 "$CMP" --run-root "$SWEEP" --scratch "$OUTD/scratch" --out "$JSON" --end-time $END \
        > "$OUTD/A1H_L1M_GRADE.stdout" 2> "$OUTD/A1H_L1M_GRADE.stderr"
RC=$?; echo "$RC" > "$OUTD/A1H_L1M_GRADE.rc"; say "comparator rc=$RC"
python3 "$OUTD/report_window_means.py" "$SWEEP" "$OUTD/scratch" "$WM" \
        > "$OUTD/WINDOW_MEANS.stdout" 2> "$OUTD/WINDOW_MEANS.stderr"
WRC=$?; echo "$WRC" > "$OUTD/WINDOW_MEANS.rc"; say "window-mean reader rc=$WRC"
python3 "$OUTD/write_landing.py" "$JSON" "$WM" "$RC" "$WRC" > "$OUTD/LANDING.txt" 2>> "$LOG"
say "LANDING WRITTEN $OUTD/LANDING.txt"
say "WATCHER v2 END"
exit 0
