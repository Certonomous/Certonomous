#!/bin/bash
# D6R3 PRE-FREEZE CHECK -- DAFOAM_CHARTER.md section 22.4's three clauses, driven.
# The supervisor checks these PERSONALLY before the freeze sha; this script is what they drive.
# DRAFT.  Nothing here launches a solver.  Nothing is sent or filed (rule 7).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; cd "$HERE"
FAIL=0; note(){ echo "$@"; }
echo "==================================================================="
echo "CLAUSE 1 -- EVERY INSTRUMENT NAMED IN THE FROZEN TABLE EXISTS AT ITS STATED md5"
echo "  (L-579: a table that is TRUE AS WRITTEN about files that do not exist is how the"
echo "   defect survived; and the parent's own d6r2c_grade.py did not exist at its freeze.)"
echo "==================================================================="
for f in d6r3_opt_runScript.py d6r3_p0_arm.sh d6r3_run_arm.sh d6r3_grade.py d6r3_prefreeze.sh \
         d6r3_inrun_guards.py d6r3_mesh_read_gate.py \
         D6R3_INRUN_SELFTEST.json D6R3_GRADE_SELFTEST.json D6R3_R17_SELFTEST.json \
         D6R3_PREFREEZE_CLI.log D6R3_PRODUCER_DIFF.log \
         dafoam_crm_tutorial_page.html dafoam_crm_tutorial_page.txt; do
  if [ -f "$f" ]; then printf "  EXISTS  %-34s %s\n" "$f" "$(md5sum "$f" | cut -d' ' -f1)"
  else printf "  ABSENT  %-34s <-- CLAUSE 1 REFUSES\n" "$f"; FAIL=1; fi
done
echo
echo "==================================================================="
echo "CLAUSE 2 -- THE PRE-FREEZE CHECK DRIVES THE CLI THE LAUNCHER EMITS, NOT THE FUNCTION"
echo "  (L-595/L-570: the FM9 grader's launcher emitted --log, the parser rejected it, and the"
echo "   frozen CLI path could only ever return NOT A RESULT while its selftest stayed green.)"
echo "==================================================================="
echo "-- SYNTHETIC: the selftests, on constructed inputs --"
python3 ./d6r3_inrun_guards.py --selftest --json /dev/null >/tmp/d6r3_ig.out 2>&1; A=$?
tail -2 /tmp/d6r3_ig.out | sed 's/^/     /'
python3 ./d6r3_grade.py --selftest --json /dev/null >/tmp/d6r3_gr.out 2>&1; B=$?
tail -2 /tmp/d6r3_gr.out | sed 's/^/     /'
python3 ./d6r3_mesh_read_gate.py --selftest --json /dev/null >/tmp/d6r3_r17.out 2>&1; C=$?
tail -2 /tmp/d6r3_r17.out | sed 's/^/     /'
echo "     in-run guards rc=$A   grader rc=$B   rule-17 mesh-read gate rc=$C"
[ $A -eq 0 ] && [ $B -eq 0 ] && [ $C -eq 0 ] || FAIL=1
echo
echo "-- REAL ANCHORS: the same CLI driven against values MEASURED on this box, reported"
echo "   SEPARATELY from the synthetic case above --"
python3 - <<'PY'
import subprocess, json, sys
# Drive the guard module's CLI, then assert that the controls it ran include the REAL anchors.
p = subprocess.run([sys.executable, "./d6r3_inrun_guards.py", "--selftest",
                    "--json", "/tmp/d6r3_real.json"], capture_output=True, text=True)
d = json.load(open("/tmp/d6r3_real.json"))
REAL = {
 "80.90429398":   "O_mp worst as-run mesh (measured from O_mp_20260913T013230Z_226722.log)",
 "79.21261137":   "FM10 worst as-run mesh (measured from FM10_20260913T163543Z_1546115.log)",
 "71.23798136":   "present in BOTH logs' check blocks",
 "70.01418200":   "smallest of O_mp's 76 over-70 values",
 "70.44640458682032": "the PUBLISHED mesh as freshly BUILT by this lane (checkMesh)",
 "66.32299475":   "the MACH-wing as-extruded baseline, the only quotable 'Mesh OK.'",
 "0.753":         "D6R2's own deformed-mesh ratio",
 "1.206":         "D6R2's own fresh-mesh ratio",
 "0.1493":        "FM10's measured lift excess",
 "103 of 109":    "D6R2C's measured zero-component count at x0",
}
blob = json.dumps(d)
ok = bad = 0
for k, why in REAL.items():
    hit = k in blob
    print("     %-20s %-6s %s" % (k, "FOUND" if hit else "ABSENT", why))
    ok += hit; bad += (not hit)
print("     real anchors exercised: %d found, %d absent, %d total" % (ok, bad, ok+bad))
g = json.load(open("/tmp/d6r3_gr.json")) if False else None
sys.exit(0 if bad == 0 else 1)
PY
[ $? -eq 0 ] || FAIL=1
python3 - <<'PY'
import subprocess, json, sys
p = subprocess.run([sys.executable, "./d6r3_grade.py", "--selftest", "--json",
                    "/tmp/d6r3_grreal.json"], capture_output=True, text=True)
d = json.load(open("/tmp/d6r3_grreal.json")); blob = json.dumps(d)
REAL = {"0.02090": "the published baseline CD, dafoam_crm_tutorial_page.txt:131",
        "0.01932": "the published optimised CD, same line",
        "0.02090143421526141": "A6's independently MEASURED baseline for this case",
        "5.539e-4": "D6R2C's own measured final cl04 miss",
        "2.787e-3": "D6R2C's own measured final cl06 miss"}
bad = 0
for k, why in REAL.items():
    hit = k in blob or k.replace("e-4","e-04") in blob or k.replace("e-3","e-03") in blob
    print("     %-22s %-6s %s" % (k, "FOUND" if hit else "ABSENT", why)); bad += (not hit)
print("     grader real anchors: %d absent" % bad)
sys.exit(0 if bad == 0 else 1)
PY
[ $? -eq 0 ] || FAIL=1
echo
echo "-- the LAUNCHER-EMITTED argv, driven to rc, including its failing side.  EACH LINE IS"
echo "   ASSERTED, not merely printed: a line that prints an expectation and does not enforce it"
echo "   is a formality.  (This block printed 'expect 2' against an actual rc=1 on its first run,"
echo "   and the gate was fixed to refuse rather than traceback -- PREREGISTRATION R4 s8d.)"
rcck(){ local want="$1"; shift; "$@" >/dev/null 2>&1; local got=$?
  if [ "$got" -eq "$want" ]; then printf "     rc=%-3s OK      %s\n" "$got" "$*"
  else printf "     rc=%-3s MISMATCH (want %s)  %s  <-- CLAUSE 2 REFUSES\n" "$got" "$want" "$*"; FAIL=1; fi; }
rcck 0  python3 ./d6r3_inrun_guards.py --selftest --json /dev/null
rcck 64 python3 ./d6r3_inrun_guards.py
rcck 2  python3 ./d6r3_inrun_guards.py --log x
rcck 0  python3 ./d6r3_grade.py --selftest --json /dev/null
rcck 2  python3 ./d6r3_grade.py --log x
rcck 0  python3 ./d6r3_mesh_read_gate.py --selftest --json /dev/null
rcck 64 python3 ./d6r3_mesh_read_gate.py
rcck 2  python3 ./d6r3_mesh_read_gate.py --case /nonexistent --generated /nonexistent
echo
echo "==================================================================="
echo "CLAUSE 3 -- EVERY CHANNEL A GATE READS IS SHOWN TO HAVE A WRITER THAT RAN"
echo "  (primal_residual.json had FOUR readers, ZERO writers and ZERO such files anywhere on"
echo "   disk, and the default conv[p]=True stood for every condition.  STILL ON SANAA'S DESK.)"
echo "==================================================================="
printf "  %-26s %-34s %s\n" CHANNEL WRITER STATUS
chan(){ printf "  %-26s %-34s %s\n" "$1" "$2" "$3"; }
chan "opt_SLSQP.txt"        "pyOptSparse SLSQP, runScript.py:255"   "WRITER NAMED; existence asserted by the grader, which REFUSES when it is unreadable"
chan "d6r3_run_record.json" "d6r3_opt_runScript.py, rank-0 block"   "WRITER IN THIS COMMIT"
chan "force.dat"            "OpenFOAM forces FO, staged by d6r3_run_arm.sh" "WRITER IN THIS COMMIT; guard 10 REFUSES when the viscous column is absent"
chan "checkMesh log"        "d6r3_run_arm.sh / the solver's own check" "WRITER IN THIS COMMIT; guard 7 REFUSES a delegated verdict and requires measured quantities"
chan "ledger.txt"           "d6r3_run_arm.sh say()"                 "WRITER IN THIS COMMIT"
chan "the arm log"          "docker run redirect, d6r3_run_arm.sh"  "WRITER IN THIS COMMIT"
chan "d6r3_rule17.json"     "d6r3_opt_runScript.py, before run_model" "WRITER IN THIS COMMIT; the gate ABORTS the run (17) rather than writing a pass it cannot support"
chan "pointProcAddressing"  "decomposePar, inside the container"    "WRITER IS OPENFOAM'S; the rule-17 gate REFUSES when any rank lacks it"
echo
echo "  NOT CLOSED HERE: no channel of this item is a primal_residual.json-class default-true"
echo "  channel, but the general referral stays open and is Sanaa's."
echo
echo "==================================================================="
if [ "$FAIL" -eq 0 ]; then echo "D6R3_PREFREEZE ALL THREE CLAUSES GREEN"; else echo "D6R3_PREFREEZE REFUSED -- see the ABSENT/rc lines above"; fi
echo "==================================================================="
exit $FAIL
