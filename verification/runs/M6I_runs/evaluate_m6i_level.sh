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
LAST=$(grep -E "^Time = " "$C/log.rhoSimpleFoam" 2>/dev/null | tail -1 | grep -oE '[0-9]+' || echo 0)
ENDL=$(grep -c "^End" "$C/log.rhoSimpleFoam" 2>/dev/null || echo 0)
echo "  rc=$RC  endTime=$ET  last stage-2 Time=$LAST  End lines=$ENDL"

# ---- C1 -------------------------------------------------------------------
bash "$REPO/scripts/monitor_m6i_bounds.sh" "$L" 2>/dev/null | sed 's/^/  /'
C1=PASS
[ "$RC" = "0" ] || C1=FAIL
[ "${LAST:-0}" = "${ET:-x}" ] || C1=FAIL
[ "${ENDL:-0}" -ge 1 ] 2>/dev/null || C1=FAIL
NBMAX=$(cat "$C"/log.rhoSimpleFoam.startup "$C"/log.rhoSimpleFoam 2>/dev/null | grep "bounding nuTilda" \
        | awk '{for(j=1;j<=NF;j++) if($j=="max:"){v=$(j+1)+0; if(v>m)m=v}} END{print m+0}')
awk -v x="${NBMAX:-0}" 'BEGIN{exit !(x>1e6)}' && C1=FAIL
echo "  C1 (it ran) = $C1   [worst bounding nuTilda max = ${NBMAX:-0}, LC-2 threshold 1e6]"

# ---- the frozen grader, unchanged ----------------------------------------
if [ -f "$C/cp_extracted.json" ]; then
  python3 "$REPO/scripts/grade_m6_agard_cp.py" \
     "$REPO/models/onera_m6/agard_ar138_table_b1_14_test2308_cp.dat" \
     "$C/cp_extracted.json" "$C/log.rhoSimpleFoam" "$C/m6i_grade_$L.json" > /dev/null 2>&1
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
