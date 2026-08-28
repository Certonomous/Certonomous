#!/usr/bin/env bash
# D18R-P7 BIRTH CONTROL -- the rule-3 question ("was this reader ever shown able to see a
# non-zero through the REAL code path?") answered on the REAL PRESERVED RUN ROOT, in BOTH
# directions, per Sanaa's 2026-08-28 canonization and the lane sharpening that a
# one-directional control certifies only half an instrument.
#
# The producer is not simulated.  Each arm copies the PRESERVED D18 run root, plants a
# perturbation INTO THE ARTEFACT THE REAL SOLVER WROTE (X-S/d18_X.json), runs the REAL
# FROZEN comparator d18_grade.py over that root so the grade JSON is emitted by the real
# producer in the real schema, and reads that JSON through the successor.
#
#   ARM 0  REPRODUCTION   unperturbed copy -> the frozen grader must reproduce the landed
#                         predictions block byte-for-byte.  Without this the other two arms
#                         prove nothing about the landed verdict.
#   ARM A  MUST-NOT-FLAG  a ~99.96 % divergence planted on shape[3], NOT A RESULT in BOTH
#                         rows -> the successor must EXCLUDE it and stay HIT, while the
#                         ORIGINAL formula on the same JSON says MISS.
#   ARM B  MUST-FLAG      a ~33.63 % divergence planted on shape[1], GRADED in BOTH rows ->
#                         the successor must INCLUDE it and move P7 to MISS.
#
# ZERO solver compute: nothing is meshed, nothing is solved, no container starts.
set -u
CASE=/home/ubuntu/Certonomous/cases/dafoam/curriculum_D18R_P7
D18=/home/ubuntu/Certonomous/cases/dafoam/curriculum_D18_cone_hypersonic
SRC=/home/ubuntu/certonomous-runs/CURRICULUM-D18-cone-hypersonic
LANDED=$SRC/D18_grade_20260828T032852Z.json
WORK=${1:?usage: d18r_p7_birth_control.sh <scratch work dir>}
mkdir -p "$WORK" || exit 3
fails=0

plant () {  # $1 arm tag, $2 component index, $3 scale factor ("" = none)
  local tag=$1 idx=$2 fac=$3 root="$WORK/root_$1"
  rm -rf "$root"; cp -a "$SRC" "$root" || return 3
  rm -rf "$root/__pycache__"
  if [ -n "$fac" ]; then
    python3 - "$root" "$idx" "$fac" <<'PY' || return 3
import json, sys
p = sys.argv[1] + "/X-S/d18_X.json"
d = json.load(open(p))
d["adjoint"]["CD"]["shape"][int(sys.argv[2])] = repr(float(d["adjoint"]["CD"]["shape"][int(sys.argv[2])]) * float(sys.argv[3]))
json.dump(d, open(p, "w"))
PY
  fi
  ( cd "$D18" && PYTHONDONTWRITEBYTECODE=1 python3 ./d18_grade.py --root "$root" \
      --out "$WORK/grade_$tag.json" > "$WORK/grade_$tag.out" 2>&1 )
  echo $?
}

say () { printf '%s\n' "$*"; }
chk () { if [ "$2" = "$3" ]; then say "  [OK ] $1  ($2)"; else say "  [BAD] $1  got=$2 want=$3"; fails=$((fails+1)); fi }

say "D18R-P7 BIRTH CONTROL -- real producer, real preserved root, both directions"
say "date_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
say "d18_grade.py md5   = $(md5sum $D18/d18_grade.py | cut -d' ' -f1)"
say "successor md5      = $(md5sum $CASE/d18r_p7_grade.py | cut -d' ' -f1)"
say "this control md5   = $(md5sum $CASE/d18r_p7_birth_control.sh | cut -d' ' -f1)"
say "preserved artefact = $LANDED"

# ---------------- ARM 0 -------------------------------------------------------
rc=$(plant repro 0 "")
chk "ARM0 frozen grader rc on an unperturbed copy of the preserved root" "$rc" "0"
r0=$(python3 - "$WORK/grade_repro.json" "$LANDED" <<'PY'
import json, sys
a = json.load(open(sys.argv[1])); b = json.load(open(sys.argv[2]))
print("SAME" if (a["predictions"] == b["predictions"] and a["verdict"] == b["verdict"]
                 and a["divergence_shipped_vs_patched_CD"] == b["divergence_shipped_vs_patched_CD"]) else "DIFF")
PY
)
chk "ARM0 REPRODUCTION: predictions + verdict + divergence identical to the landed grade" "$r0" "SAME"

# ---------------- ARMS A and B ------------------------------------------------
read_arm () {  # $1 tag -> "P7corr P7orig signalcomp moved excluded_n item"
  python3 - "$CASE" "$WORK/grade_$1.json" <<'PY'
import json, sys
sys.path.insert(0, sys.argv[1])
import d18r_p7_grade as R
try:
    a = R.regrade_p7(json.load(open(sys.argv[2])))
except R.Refusal as e:
    print("REFUSED REFUSED - - 0 - 0 0"); sys.exit(0)
# The item verdict is a TWO-WORD value from the fixed vocabulary ("GATE FAIL", "NOT A
# RESULT"); emitted bare it word-splits in the caller's `set --` and silently shifts every
# column after it. Measured on this very script before the freeze: ARM B printed
# item=GATE sn_corr=FAIL. Underscores make the field a single shell word.
print("%s %s %s %s %d %s %.4f %.4f" % (a["P7_corrected"], a["P7_original_recomputed"],
      "%s[%d]" % tuple(a["signal_corrected_component"]), a["moved"],
      len(a["excluded_components"]), a["item_verdict_UNCHANGED"].replace(" ", "_"),
      a["sn_corrected"], a["sn_original"]))
PY
}

rc=$(plant A 3 1000.0)
chk "ARM A frozen grader rc with a 1000x plant on the SHIPPED shape[3] adjoint" "$rc" "0"
set -- $(read_arm A)
say "  ARM A read: P7_corrected=$1 P7_original=$2 signal=$3 moved=$4 excluded=$5 item=$6 sn_corr=$7 sn_orig=$8"
chk "ARM A MUST-NOT-FLAG: successor STAYS HIT on a planted divergence at a NOT A RESULT component" "$1" "HIT"
chk "ARM A the ORIGINAL formula on the SAME producer-emitted JSON says MISS (defect live)" "$2" "MISS"
chk "ARM A the successor's signal is a GRADED component, not the planted one" "$3" "shape[1]"
chk "ARM A exactly one component excluded" "$5" "1"

rc=$(plant B 1 1.5)
chk "ARM B frozen grader rc with a 1.5x plant on the SHIPPED shape[1] adjoint" "$rc" "0"
set -- $(read_arm B)
say "  ARM B read: P7_corrected=$1 P7_original=$2 signal=$3 moved=$4 excluded=$5 item=$6 sn_corr=$7 sn_orig=$8"
chk "ARM B MUST-FLAG: successor moves P7 to MISS on a planted divergence at a GRADED component" "$1" "MISS"
chk "ARM B the successor's signal IS the planted component" "$3" "shape[1]"

say ""
if [ "$fails" -eq 0 ]; then
  say "BIRTH CONTROL PASS -- the reader was shown able to see a non-zero AND to stay silent,"
  say "both through the real producer on the real preserved root. failures=0"
  exit 0
fi
say "BIRTH CONTROL FAIL failures=$fails"
exit 2
