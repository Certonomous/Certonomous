#!/usr/bin/env bash
# =============================================================================
# PERMISSION: FROZEN by the dafoam-supervisor 2026-09-11.
#
# SELFTEST FOR d8g_grade.py.
#
# It does TWO things, and the second is the one that matters:
#
#  (1) it runs the comparator's own 43-unit planted-fixture suite under BOTH
#      `python3` and `python3 -O` (L-332: a comparator that gates on `assert`
#      gates on nothing under -O; this one carries zero asserts and the census
#      is itself unit-tested against a planted one), and
#
#  (2) IT MUTATES A COPY OF THE COMPARATOR AND ASSERTS THE SUITE THEN FAILS.
#      A SUITE THAT PASSES PROVES NOTHING UNTIL IT IS SEEN TO FAIL.  EIGHT
#      mutations, each removing exactly one gate's teeth, each asserted to make
#      a NAMED unit go BAD.  The eighth (AMENDMENT 3, 2026-09-11) REINSTATES THE
#      COMPLETION HOLE the comparator carried until that date, and the dead-solve
#      demonstration that forced the amendment is the unit that must catch it.  If a mutation is applied and the suite still
#      passes, the unit that was supposed to catch it is ceremony.
#
# THE MUTATOR IS ITSELF A PLANTED-ZERO RISK AND IS GUARDED.  A `sed`/replace
# that matches nothing yields an UNMUTATED copy; the suite then passes, and the
# control reports "the suite failed to fail" when in fact nothing was mutated.
# So every mutation asserts REPLACEMENT COUNT == 1 and asserts the mutated file
# DIFFERS from the original, BEFORE the suite is run.
#
# WHAT THIS DOES NOT TEST, STATED PLAINLY: it does not test DAFoam, docker, a
# mesh or a solver.  Every fixture is synthetic.  A green here means the GATES
# REFUSE WHAT THEY CLAIM TO REFUSE; it does not mean any D8G arm has ever run.
# =============================================================================
set -uo pipefail

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
TARGET="$HERE/d8g_grade.py"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
PASS=0; FAIL=0
say() { printf '%s\n' "$*"; }
check() { # $1 = name, $2 = expected, $3 = got
  if [ "$2" = "$3" ]; then PASS=$((PASS+1)); say "  PASS  $1  (expected=$2 got=$3)"
  else FAIL=$((FAIL+1)); say "  FAIL  $1  (expected=$2 got=$3)"; fi
}

test -f "$TARGET" || { say "REFUSE C0 target not found: $TARGET"; exit 2; }
say "D8G GRADER SELFTEST  target=$TARGET  md5=$(md5sum "$TARGET" | cut -d' ' -f1)"
say "                     date_u=$(date -u +%Y-%m-%dT%H:%M:%SZ)  host_python=$(python3 -V 2>&1)"
say ""

# ---------------------------------------------------------------------------
# A. THE COMPARATOR'S OWN SUITE, BOTH INTERPRETER MODES
# ---------------------------------------------------------------------------
say "A. the comparator's own planted-fixture suite"
python3    "$TARGET" --selftest --tmpdir "$TMP" > "$TMP/clean.out" 2>&1; RC1=$?
python3 -O "$TARGET" --selftest --tmpdir "$TMP" > "$TMP/cleanO.out" 2>&1; RC2=$?
check "A1 suite under python3"        0 "$RC1"
check "A2 suite under python3 -O"     0 "$RC2"
UNITS=$(grep -c '^  \[OK \]' "$TMP/clean.out")
check "A3 unit count under python3"  50 "$UNITS"
check "A4 unit count under python3 -O" 50 "$(grep -c '^  \[OK \]' "$TMP/cleanO.out")"
check "A5 zero BAD units"             0 "$(grep -c '^  \[BAD\]' "$TMP/clean.out")"
check "A6 ast.Assert census == 0 (L-332)" 0 \
  "$(python3 -c "import ast;print(sum(1 for n in ast.walk(ast.parse(open('$TARGET').read())) if isinstance(n,ast.Assert)))")"
say ""

# ---------------------------------------------------------------------------
# B. THE MUTATION CONTROLS.  Each removes one gate's teeth and must be CAUGHT.
# ---------------------------------------------------------------------------
mutate() {  # $1 = tag  $2 = old text  $3 = new text
  python3 - "$TARGET" "$TMP/mut_$1.py" "$2" "$3" <<'PY'
import sys
src, dst, old, new = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
s = open(src).read()
n = s.count(old)
if n != 1:
    sys.stderr.write("MUTATOR REFUSE: pattern occurs %d times, not once\n" % n); sys.exit(3)
open(dst, "w").write(s.replace(old, new))
PY
}

run_mut() {  # $1 = tag  $2 = expected BAD marker (a unit prefix or a refusal string)
  local tag="$1" want="$2"
  if ! cmp -s "$TARGET" "$TMP/mut_$tag.py"; then
    python3 "$TMP/mut_$tag.py" --selftest --tmpdir "$TMP" > "$TMP/mut_$tag.out" 2>&1
    local rc=$?
    local caught=no
    [ "$rc" -ne 0 ] && grep -q -- "$want" "$TMP/mut_$tag.out" && caught=yes
    check "B-$tag SUITE FAILS and [$want] is the catcher" yes "$caught"
  else
    check "B-$tag mutated copy DIFFERS from the original (planted-zero guard)" yes no
  fi
}

say "B. mutation controls -- the suite must be SEEN TO FAIL"

# B1  G-PLAT's statistic becomes the ADJACENT-SAMPLE DELTA -- the exact defect the
#     amendment refuses by name (cfd's DrivAer Gate A1 limb, caught 2026-09-10).
mutate G-PLAT-ADJACENT \
  '    ptp = max(window) - min(window)' \
  '    ptp = max(abs(window[i + 1] - window[i]) for i in range(len(window) - 1)) if len(window) > 1 else 0.0' \
  && run_mut G-PLAT-ADJACENT 'U8 MUTATION drifting CD history'

# B2  G-PRIMAL's tolerance read-back stops refusing on a mismatch (it becomes the
#     "soft note" the amendment forbids).
mutate G-PRIMAL-SOFT \
  '    if abs(tol - PRIMAL_MIN_RES_TOL) > 1e-18 or abs(diff - PRIMAL_MIN_RES_TOL_DIFF) > 1e-9:' \
  '    if False:' \
  && run_mut G-PRIMAL-SOFT 'U10 MUTATION primalMinResTolDiff 100'

# B3  the trivial-baseline WITHDRAWAL becomes a warning (always "did not also pass").
mutate G-FD-NO-WITHDRAWAL \
  '            "also_passed": bool(agg <= FD_CONDITIONAL_PCT),' \
  '            "also_passed": False,' \
  && run_mut G-FD-NO-WITHDRAWAL 'U11 MUTATION the deliberately-wrong 1e-3 step ALSO PASSES'

# B4  the sign-flip clause is dropped from the band, so a flip hides behind a small
#     aggregate.
mutate G-FD-NO-SIGNFLIP \
  '    if out["sign_flips"] > 0:' \
  '    if False:' \
  && run_mut G-FD-NO-SIGNFLIP 'U12 MUTATION sign-flipped twist'

# B5  the per-component plateau tolerance is widened to 1000 %, so nothing is ever
#     flagged and nothing is ever excluded by name.
mutate G-FD-PLATEAU-WIDE \
  'PLATEAU_TOL_PCT = 10.0' \
  'PLATEAU_TOL_PCT = 1000.0' \
  && run_mut G-FD-PLATEAU-WIDE 'U15 a component that stabilises NOWHERE'

# B6  THE RESIDUAL READER IS MADE STRUCTURALLY BLIND IN THE CRUDE WAY -- it reads
#     finalRes INSTEAD of initRes.  The MUST-SEE plant catches it: the reader cannot see
#     the planted `nuTilda initRes: 9.876e-03` at all.
mutate G-PRIMAL-FINALRES-ONLY \
  '_RE_INITRES = re.compile(r"^(U0|U1|U2|he|p|nuTilda)\s+initRes:\s+([0-9.eE+-]+)", re.M)' \
  '_RE_INITRES = re.compile(r"^(U0|U1|U2|he|p|nuTilda)\s+initRes:\s+[0-9.eE+-]+\s+finalRes:\s+([0-9.eE+-]+)", re.M)' \
  && run_mut G-PRIMAL-FINALRES-ONLY 'residual_reader_must_see_plant_not_seen'

# B7  AND THE SUBTLE WAY, WHICH IS THE ONE THE ANTI-PLANT EXISTS FOR: the reader takes the
#     MAX of initRes AND finalRes, so IT STILL PASSES THE MUST-SEE PLANT and only the
#     DISCRIMINATING ANTI-PLANT can catch it.  A reader shown able to see a non-zero ON
#     THE WRONG FIELD has not been shown able to see the right one (section 4.8 (ii)).
#     THIS IS THE MUTATION THAT PROVES THE ANTI-PLANT IS NOT CEREMONY.
mutate G-PRIMAL-FINALRES-MAX \
  '            vals[m.group(1)] = float(m.group(2))' \
  '            vals[m.group(1)] = max(float(m.group(2)), float(re.search(r"finalRes:\s+([0-9.eE+-]+)", m.string[m.start():m.end() + 60]).group(1)))' \
  && run_mut G-PRIMAL-FINALRES-MAX 'residual_reader_SAW_THE_FINALRES_ANTI_PLANT'

# B8  AMENDMENT 3's CLAUSE IS REINSTATED AS THE HOLE IT REPLACED -- G1 stops running the
#     completion check at all, which is EXACTLY the state the comparator was in until
#     2026-09-11.  U44's dead solve must then grade instead of being refused.  THE
#     DEMONSTRATION THAT FORCED THE AMENDMENT IS NOW THE REGRESSION TEST THAT GUARDS IT:
#     if this mutation ever stops being caught, the comparator has silently gone back to
#     certifying a corpse at order 2.0000, and every number in that chain looks like success.
mutate G1-RUN-HOLE-REINSTATED \
  '        out.setdefault("run_completion", {})[arm] = g1_run_completion(base, arm, text)' \
  '        out.setdefault("run_completion", {})[arm] = {"HOLE_REINSTATED": True}' \
  && run_mut G1-RUN-HOLE-REINSTATED 'U44 THE DEAD SOLVE'

say ""
say "D8G GRADER SELFTEST SUMMARY pass=$PASS fail=$FAIL"
if [ "$FAIL" -ne 0 ]; then say "SELFTEST FAIL"; exit 2; fi
say "SELFTEST PASS $PASS/$((PASS+FAIL))"
exit 0
