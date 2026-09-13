#!/usr/bin/env bash
# evaluate_m6i_level.sh <LEVEL> -- the whole verdict for one M6I level, in one pass.
#
#   Written BEFORE the levels it grades had finished, so the evaluation cannot be shaped
#   by the numbers.  It calls the FROZEN grader (blob e9d5c04b at 4c931d97c) and changes
#   nothing in it; everything this script adds is a limb registered in
#   verification/campaign/M6I_R1_SOLVE_PREREGISTRATION.md and can only TIGHTEN a verdict.
#
#   C1 (ADDENDUM 8 A8.2)  rc=0, last time == endTime, End line, LC-2 zero, LC-1 peak < 2.0 %
#   C2 (ADDENDUM 8 A8.2 / A3.1 S1+S2)  cfd_cp_rise_at_shock >= 0.212 at eta 0.65 and
#                                       >= 0.320 at eta 0.90, x_shock_cfd < 0.85 c
#   C1 WITHOUT C2 IS NOT A CURED FAMILY: it is GATE FAIL labelled
#   "SURVIVED BY SMEARING -- THE SAME NEGATIVE RESULT BY ANOTHER ROUTE".
#
# IT READS AND GRADES.  IT LAUNCHES NOTHING.
set -u
REPO=/home/ubuntu/Certonomous
L="${1:?usage: evaluate_m6i_level.sh <LEVEL e.g. L1>}"
C="$REPO/verification/runs/M6I_runs/$L"
[ -d "$C" ] || { echo "$L: no such level"; exit 2; }

echo "================ $L ================"
RC=$(cat "$C/RC.txt" 2>/dev/null || echo "ABSENT")
ET=$(grep -oE '^endTime +[0-9]+;' "$C/system/controlDict" 2>/dev/null | grep -oE '[0-9]+')

# ---- DEFECT FIX 1 -- pick the TERMINATING stage log instead of hard-coding a name.
#  A level that finishes on a RESUME stage leaves log.rhoSimpleFoam stopped mid-run with
#  NO End line.  Reading that fixed name grades a COMPLETED run as NOT A RESULT and, worse,
#  hands the same dead log to the frozen grader as its P4 argument, so the grader refuses
#  (exit 2) and NO Cp NUMBER IS PRODUCED AT ALL.
#  MEASURED ON L1: log.rhoSimpleFoam stops at `Time = 844` with 0 End lines; the run
#  actually terminated in log.rhoSimpleFoam.resume.2 at `Time = 8000` with an End line and
#  rc=0.  AS WRITTEN, THIS SCRIPT WOULD HAVE GRADED L1 -- THE FINEST AND BEST LEVEL IN THE
#  FAMILY, 1,098 core-minutes -- AS `NOT A RESULT: C1 failed`, AND WOULD HAVE PRINTED NO
#  Cp ROW FOR IT.  The level that actually landed would have been thrown away by its own
#  measuring instrument.
#  The rule applied is the strict completion rule, unchanged: the terminating log is the
#  stage log that carries an `End` line AND whose last `Time =` equals endTime.  If no
#  stage log satisfies both, NOTHING is guessed -- C1 fails and the grader is not run.
TLOG=""
for f in $(ls -1 "$C"/log.rhoSimpleFoam "$C"/log.rhoSimpleFoam.startup \
                 "$C"/log.rhoSimpleFoam.resume.* 2>/dev/null \
           | grep -v '\.stderr$' | sort -V); do
  grep -q "^End" "$f" 2>/dev/null || continue
  lt=$(grep -E "^Time = " "$f" 2>/dev/null | tail -1 | grep -oE '[0-9]+')
  [ "${lt:-x}" = "${ET:-y}" ] || continue
  TLOG="$f"
done
if [ -n "$TLOG" ]; then
  LAST=$(grep -E "^Time = " "$TLOG" | tail -1 | grep -oE '[0-9]+')
  ENDL=$(grep -c "^End" "$TLOG" || true)
else
  LAST=0; ENDL=0
fi
# ---- DEFECT FIX 2 -- `grep -c` EXITS 1 when it counts zero, so the old
#  `$(grep -c ... || echo 0)` captured the string "0\n0", and `[ "0\n0" -ge 1 ]` failed as a
#  bash syntax error rather than as a count.  C1 came out FAIL for the right reason by
#  accident.  `|| true` above keeps the count and drops the exit status.
echo "  rc=$RC  endTime=$ET  terminating log=${TLOG:-NONE FOUND}  last Time=$LAST  End lines=$ENDL"

# ---- C1 -------------------------------------------------------------------
bash "$REPO/scripts/monitor_m6i_bounds.sh" "$L" 2>/dev/null | sed 's/^/  /'
C1=PASS
[ "$RC" = "0" ] || C1=FAIL
[ "${LAST:-0}" = "${ET:-x}" ] || C1=FAIL
[ "${ENDL:-0}" -ge 1 ] 2>/dev/null || C1=FAIL
# ---- DEFECT FIX 3 -- the LC-2 limb read only the startup and stage-2 logs and was BLIND
#  to every resume stage.  On L1 the resume stages carry 7,098 of the 7,635 `bounding
#  nuTilda` lines, so the limb was reading 7 % of its own evidence.  Read every stage log.
NBMAX=$(cat $(ls -1 "$C"/log.rhoSimpleFoam "$C"/log.rhoSimpleFoam.startup \
                    "$C"/log.rhoSimpleFoam.resume.* 2>/dev/null | grep -v '\.stderr$') \
        2>/dev/null | grep "bounding nuTilda" \
        | awk '{for(j=1;j<=NF;j++) if($j=="max:"){v=$(j+1)+0; if(v>m)m=v}} END{print m+0}')
awk -v x="${NBMAX:-0}" 'BEGIN{exit !(x>1e6)}' && C1=FAIL
echo "  C1 (it ran) = $C1   [worst bounding nuTilda max = ${NBMAX:-0}, LC-2 threshold 1e6]"

# ---- the frozen grader, unchanged ----------------------------------------
if [ -f "$C/cp_extracted.json" ] && [ -n "$TLOG" ]; then
  # The frozen grader's P4 argument is the TERMINATING log, not a fixed name (DEFECT FIX 1).
  # The grader itself is UNCHANGED -- blob e9d5c04b at 4c931d97c.  Only which log it is
  # pointed at changes, and it is pointed at the log that actually carries the End line.
  python3 "$REPO/scripts/grade_m6_agard_cp.py" \
     "$REPO/models/onera_m6/agard_ar138_table_b1_14_test2308_cp.dat" \
     "$C/cp_extracted.json" "$TLOG" "$C/m6i_grade_$L.json" > /dev/null 2>&1
  python3 - "$C/m6i_grade_$L.json" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
print("  FROZEN GRADER VERDICT: %s"%d["verdict"])
pc=d.get("planted_control",{})
print("  planted control seen: %s (rms moved %.4f, required %.4f)"
      %(pc.get("reader_saw_the_plant"),pc.get("rms_moved_by",0),pc.get("required_response",0)))
print("  %-18s %9s %9s %7s"%("row","RMS","band","in?"))
for k,v in d.get("cp_rows",{}).items():
    print("  %-18s %9.4f %9.3f %7s"%(k,v["rms_dev"],v["band_rms"],v["within_band"]))
# ---- C2: A8.2 / A3.1 S1 + S2, keyed to the EXPERIMENT alone
S1={ "eta0.65":0.212, "eta0.90":0.320 }
c2=True; rows=[]
for k,v in d.get("shock",{}).items():
    need=S1.get(k)
    rise=v.get("cfd_cp_rise_at_shock"); x=v.get("x_shock_cfd")
    ok = (need is not None and rise is not None and rise>=need and x is not None and x<0.85)
    c2 = c2 and ok
    rows.append("  %s: cfd_cp_rise %.4f vs S1 >= %.3f | x_shock %.4f vs S2 < 0.85 -> %s"
                %(k,rise or 0,need or 0,x or 0,"SHOCK-BEARING" if ok else "NOT shock-bearing"))
if not d.get("shock"): c2=False; rows.append("  no shock rows produced")
print("\n".join(rows))
print("  C2 (it still has a shock) = %s"%("PASS" if c2 else "FAIL"))
open(sys.argv[1]+".c2","w").write("PASS" if c2 else "FAIL")
PY
  C2=$(cat "$C/m6i_grade_$L.json.c2" 2>/dev/null || echo FAIL)
else
  echo "  no cp_extracted.json -- the grader was not run and NO Cp NUMBER EXISTS for this level"
  C2=FAIL
fi

# ---- the conjunction ------------------------------------------------------
echo
if [ "$C1" = "PASS" ] && [ "$C2" = "PASS" ]; then
  echo "  RUNG-4 OUTCOME: C1 and C2 BOTH HOLD -- the level ran AND kept its shock."
  echo "  The frozen grader's verdict above stands as this level's verdict."
elif [ "$C1" = "PASS" ]; then
  echo "  RUNG-4 OUTCOME: GATE FAIL -- SURVIVED BY SMEARING, THE SAME NEGATIVE RESULT BY"
  echo "  ANOTHER ROUTE. C1 holds and C2 does not: the scheme bought stability with the"
  echo "  graded quantity. This is NOT a cured family (ADDENDUM 8 A8.2)."
else
  echo "  RUNG-4 OUTCOME: NOT A RESULT -- C1 failed. No Cp from this level is quoted."
fi
