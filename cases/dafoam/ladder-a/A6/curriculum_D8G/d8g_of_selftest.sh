#!/usr/bin/env bash
# =============================================================================
# PERMISSION: FROZEN by the dafoam-supervisor 2026-09-11.
#
# SELFTEST FOR d8g_of.py -- THE PRODUCER.
#
# The producer's whole duty is CONFORMANCE TO THE COMPARATOR.  So this suite does
# not check the producer against the producer's own expectations -- that would be
# a mirror.  It loads d8g_grade.py, THE SPECIFICATION, and drives artefacts
# built by the producer's OWN builders through the comparator's OWN read_P /
# read_A / read_F / functional_plant_control / ctrl_control / grader_plant_control
# / grade_components / _trivial_baseline.  A key the comparator reads and the
# producer never writes fails HERE, for free, instead of at grading time after ten
# arms of compute have been spent.
#
# It does THREE things, and the third is the one that matters:
#
#  (1) it runs the producer's 54-unit suite under BOTH `python3` and `python3 -O`
#      (L-332: an instrument that gates on `assert` gates on nothing under -O;
#      this one carries zero asserts and the census is itself a unit), and
#
#  (2) it asserts the comparator this ran against is the one the supervisor
#      verified, BY MD5 -- a producer proved to conform to a DIFFERENT comparator
#      has been proved to conform to nothing, and
#
#  (3) IT MUTATES A COPY OF THE PRODUCER AND ASSERTS THE SUITE THEN FAILS.  A
#      SUITE THAT PASSES PROVES NOTHING UNTIL IT IS SEEN TO FAIL.  Ten mutations,
#      each removing exactly one control's teeth, each asserted to make a NAMED
#      unit go BAD.  If a mutation is applied and the suite still passes, the unit
#      that was supposed to catch it is ceremony.
#
# THE MUTATOR IS ITSELF A PLANTED-ZERO RISK AND IS GUARDED.  A replace that matches
# nothing yields an UNMUTATED copy; the suite then passes and the control would
# report "the suite failed to fail" when in fact nothing was mutated.  So every
# mutation asserts REPLACEMENT COUNT == 1 and asserts the mutated file DIFFERS
# from the original, BEFORE the suite is run.
#
# WHAT THIS DOES NOT TEST, STATED PLAINLY: it does not test DAFoam, IDWarp, MPI,
# docker, a mesh or a solver.  Every probe is analytic and every fixture is
# synthetic.  A green here means THE ARTEFACT CONTRACT IS SATISFIED AND THE
# CONTROLS REFUSE WHAT THEY CLAIM TO REFUSE.  It does not mean any D8G arm has
# ever run, and it says nothing about whether d8g_runScript.py -- which does not
# yet exist -- will hand this instrument the objects it expects.
# =============================================================================
set -uo pipefail

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
TARGET="$HERE/d8g_of.py"
SPEC="$HERE/d8g_grade.py"
# CONFORMANCE IS TO A SPECIFIC FILE, NOT TO A FILENAME.
# 2026-09-11T16:15Z the dafoam-supervisor verified md5 e94409f1da5732ce206c12924aec9e22
# personally (13/13, 43/43 units under python3 and python3 -O, zero ast.Assert, seven
# mutation controls).  AMENDMENT 2 (a) then changed the comparator's PREDICTED_CORE_MIN
# F2-P and F2-S, so the bytes moved to the value below.
# THE SUPERVISOR'S PERSONAL VERIFICATION DOES NOT TRANSFER TO THE NEW BYTES.  A relayed
# check is a summary, not a check (SUPERVISION_CHARTER.md section 3), and this pin firing
# on the change is what forced that to be said out loud rather than assumed.  The
# comparator must be RE-READ at the md5 below before it is frozen.
# 2026-09-11, AGAIN: AMENDMENT 3 added the G1-RUN completion clause, so the bytes moved a
# SECOND time.  The pin fired a second time, which is the pin doing its job twice, not noise.
# 2026-09-11, A THIRD TIME: the freeze rename and the permission-line flip moved the bytes
# again, WITH NO CHANGE TO ANY GATE.  That is precisely why the value below is taken AFTER
# every byte that will ever change has changed -- a pin taken before the flip would name a
# file that no longer exists in that form.
SPEC_MD5_VERIFIED=12688063e20cbb6fa79cf08d0996d4e1
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
PASS=0; FAIL=0
say() { printf '%s\n' "$*"; }
check() { # $1 = name, $2 = expected, $3 = got
  if [ "$2" = "$3" ]; then PASS=$((PASS+1)); say "  PASS  $1  (expected=$2 got=$3)"
  else FAIL=$((FAIL+1)); say "  FAIL  $1  (expected=$2 got=$3)"; fi
}

test -f "$TARGET" || { say "REFUSE C0 producer not found: $TARGET"; exit 2; }
test -f "$SPEC"   || { say "REFUSE C0 comparator not found: $SPEC -- the producer's only duty is"; \
                       say "         conformance to it, and a suite that cannot load it proves nothing"; exit 2; }
say "D8G PRODUCER SELFTEST  target=$TARGET  md5=$(md5sum "$TARGET" | cut -d' ' -f1)"
say "                       spec=$SPEC  md5=$(md5sum "$SPEC" | cut -d' ' -f1)"
say "                       date_u=$(date -u +%Y-%m-%dT%H:%M:%SZ)  host_python=$(python3 -V 2>&1)"
say ""

# ---------------------------------------------------------------------------
# A. THE PRODUCER'S OWN SUITE, BOTH INTERPRETER MODES, AGAINST THE VERIFIED SPEC
# ---------------------------------------------------------------------------
say "A. the producer's planted-fixture suite, driven through the comparator's own readers"
check "A0 the comparator is the md5 the supervisor verified" \
  "$SPEC_MD5_VERIFIED" "$(md5sum "$SPEC" | cut -d' ' -f1)"
python3    "$TARGET" --selftest --tmpdir "$TMP" > "$TMP/clean.out" 2>&1; RC1=$?
python3 -O "$TARGET" --selftest --tmpdir "$TMP" > "$TMP/cleanO.out" 2>&1; RC2=$?
check "A1 suite under python3"           0 "$RC1"
check "A2 suite under python3 -O"        0 "$RC2"
check "A3 unit count under python3"     54 "$(grep -c '^  \[OK \]' "$TMP/clean.out")"
check "A4 unit count under python3 -O"  54 "$(grep -c '^  \[OK \]' "$TMP/cleanO.out")"
check "A5 zero BAD units"                0 "$(grep -c '^  \[BAD\]' "$TMP/clean.out")"
check "A6 ast.Assert census == 0 (L-332)" 0 \
  "$(python3 -c "import ast;print(sum(1 for n in ast.walk(ast.parse(open('$TARGET').read())) if isinstance(n,ast.Assert)))")"
# A7 WAS A DELIBERATE TRIPWIRE ON THE FREEZE AND IT HAS FIRED.  Until 2026-09-11 it asserted
# PRODUCER_MD5 was still the unfrozen token, so a lane could not quietly guess a hash.  The
# producer script now EXISTS and the constant is PINNED to the three-way D8 -> D8R -> D8G
# byte identity, so the unit is INVERTED: the token must be GONE and the pin must be the
# frozen md5.  Inverted, not deleted -- a tripwire that is removed rather than turned around
# leaves the step it guarded unguarded.
check "A7 PRODUCER_MD5 is PINNED to the frozen producer md5 (the token is gone)" 1 \
  "$(grep -c '^PRODUCER_MD5 = "28c7819487a025a5f6554d38062a2b66"' "$TARGET")"
check "A7b the unfrozen token no longer appears anywhere in the producer" 0 \
  "$(grep -c '__D8G_'"UNFROZEN__" "$TARGET")"
say ""

# ---------------------------------------------------------------------------
# B. THE MUTATION CONTROLS.  Each removes one control's teeth and must be CAUGHT.
# ---------------------------------------------------------------------------
mut_case() {  # $1 = tag  $2 = old text  $3 = new text  $4 = the unit/string that must catch it
  local tag="$1" old="$2" new="$3" want="$4"
  local dst="$TMP/mut_$tag.py"
  rm -f "$dst"
  # THE MUTATOR IS ITSELF A PLANTED-ZERO RISK.  A replace that matches nothing yields an
  # UNMUTATED copy, the suite then passes, and the control reports "failed to fail" when in
  # fact NOTHING WAS MUTATED.  So: exactly one occurrence, and the copy must DIFFER.  And
  # this function ALWAYS emits exactly one check -- an earlier draft of this file chained
  # `mutate ... && run_mut ...` and a REFUSED MUTATOR SILENTLY EMITTED NO CHECK AT ALL,
  # which is the same class of hole the mutator guard exists to close.
  if ! python3 - "$TARGET" "$dst" "$old" "$new" <<'MUTPY' 2>"$TMP/mut_$tag.err"
import sys
src, dst, old, new = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
s = open(src).read()
n = s.count(old)
if n != 1:
    sys.stderr.write("MUTATOR REFUSE: pattern occurs %d times, not once\n" % n)
    sys.exit(3)
open(dst, "w").write(s.replace(old, new))
MUTPY
  then
    check "B-$tag MUTATOR applied exactly one replacement" yes "no($(tr -d '\n' < "$TMP/mut_$tag.err"))"
    return
  fi
  if cmp -s "$TARGET" "$dst"; then
    check "B-$tag mutated copy DIFFERS from the original (planted-zero guard)" yes no
    return
  fi
  # --specdir points the mutated copy at the REAL comparator.  WITHOUT IT the copy would
  # fail because the comparator is absent, and this control would claim a catch it did not
  # make -- a green from the wrong cause.
  python3 "$dst" --selftest --tmpdir "$TMP" --specdir "$HERE" > "$TMP/mut_$tag.out" 2>&1
  local rc=$?
  local caught=no
  if [ "$rc" -ne 0 ] && grep -q -- "$want" "$TMP/mut_$tag.out"; then caught=yes; fi
  if grep -q '^REFUSE the comparator' "$TMP/mut_$tag.out"; then caught="no(comparator-not-loaded)"; fi
  check "B-$tag SUITE FAILS and [$want] is the catcher" yes "$caught"
}

say "B. mutation controls -- the suite must be SEEN TO FAIL"

# B1  THE PRODUCER STOPS EVALUATING THE TRIVIAL STEP.  The single most expensive mistake
#     available to this instrument: the arm completes, the table looks full, and the
#     comparator's _trivial_baseline REFUSES at grading time with 42 primals already spent.
mut_case FD-NO-TRIVIAL-STEP \
  '    return sorted(set(STEPS["twist"]) | {TRIVIAL_STEP})' \
  '    return sorted(STEPS["twist"])' \
  'BAD] U32 every registered component carries ALL FOUR steps'

# B2  components_requested silently loses a component -- read_F refuses BY IDENTITY.
mut_case FD-COMPONENTS-SHORT \
  '            "components_requested": [[dv, int(idx)] for dv, idx in comps],' \
  '            "components_requested": [[dv, int(idx)] for dv, idx in comps[:-1]],' \
  'BAD] U31 comparator read_F ACCEPTS'

# B3  the trivial step is written as a NEAR MISS.  read_F allows 1e-15; a value that LOOKS
#     right is exactly what that tolerance exists for.
mut_case FD-TRIVIAL-NEAR-MISS \
  '            "trivial_step": triv,                           # 1.0e-3 to within 1e-15 or read_F refuses' \
  '            "trivial_step": triv * (1.0 + 1e-12),           # planted near miss' \
  'BAD] U31 comparator read_F ACCEPTS'

# B4  THE CONTROL'S ZERO ARM STOPS BEING EXACTLY ZERO.  ctrl_control tests `!= 0.0`, not a
#     tolerance, and 1e-300 is not zero.
mut_case CTRL-ZERO-NOT-EXACT \
  '    zero = 0.0' \
  '    zero = 1e-300' \
  'BAD] U35 comparator ctrl_control RECOVERS'

# B5  THE PLANTED ARM LOSES ITS FACTOR OF TWO -- the classic central-difference slip.  The
#     comparator recovers the constant to 1e-9 RELATIVE, so a factor of 2 is nine orders out.
mut_case CTRL-PLANT-NO-FACTOR-TWO \
  '    planted = PLANT / (2.0 * CTRL_STEP)' \
  '    planted = PLANT / CTRL_STEP' \
  'BAD] U35 comparator ctrl_control RECOVERS'

# B6  THE CTRL COLLISION GUARD GOES INERT.  A measured derivative could then land on the
#     control's own value and nothing would say so.
mut_case CTRL-COLLISION-INERT \
  '    if hits:' \
  '    if False:' \
  'BAD] U45 check_ctrl_not_confusable REFUSES a MEASURED derivative that is exactly 0.0'

# B7  THE TWO CELL READERS STOP BEING CROSS-CHECKED.  A header note that disagrees with the
#     mesh it describes would then be written into the artefact as MEASURED.
mut_case CELLS-NO-CROSSCHECK \
  '    if body is not None and int(body) != int(note):' \
  '    if False:' \
  'BAD] U10 measure_cells REFUSES a header note that disagrees'

# B8  THE PLATEAU-WINDOW FORECAST ALWAYS SAYS YES.  The arm then launches at a printInterval
#     that cannot produce ten samples, and G-PLAT makes the level NOT A RESULT FOR WANT OF
#     EVIDENCE after the core-minutes are gone.
mut_case PLATEAU-FORECAST-ALWAYS-OK \
  '            "floor": PLATEAU_MIN_SAMPLES, "sufficient": bool(w >= PLATEAU_MIN_SAMPLES),' \
  '            "floor": PLATEAU_MIN_SAMPLES, "sufficient": True,' \
  'BAD] U21 the forecast REFUSES printInterval 200'

# B9  THE D8G_ PREFIX IS DROPPED FROM EVERY PRINTED LINE.  The prefix is the STRUCTURAL half
#     of the anti-forgery guard: it is what stops an instrument line from ever beginning with
#     a token the comparator's log readers anchor on.
mut_case LOG-PREFIX-DROPPED \
  '    return line if line.startswith("D8G_") else "D8G_" + line' \
  '    return line' \
  'BAD] U23 every line this instrument prints is D8G_-prefixed'

# B10 THE HYGIENE CHECKER ITSELF GOES INERT -- it inspects no patterns and so can never see a
#     forged line.  THIS IS THE MUTATION THAT PROVES U24 IS NOT CEREMONY.
mut_case LOG-HYGIENE-INERT \
  '    for pat in GRADER_LOG_PATTERNS:' \
  '    for pat in []:' \
  'BAD] U24 lines_are_clean CATCHES a forged solver line'

# B11 THE WRITTEN-ARTEFACT READ-BACK STOPS CHECKING GRADIENT PROVENANCE.  An F table with a
#     placeholder adjoint_source md5 would be written, and the comparator would refuse it at
#     grading time instead of the producer refusing it in seconds.
mut_case READBACK-NO-SOURCE-MD5 \
  '    if not (isinstance(src, str) and re.fullmatch(r"[0-9a-f]{32}", src)):' \
  '    if False:' \
  'BAD] U50 verify_written_F REFUSES an adjoint_source md5'

say ""
say "D8G PRODUCER SELFTEST SUMMARY pass=$PASS fail=$FAIL"
if [ "$FAIL" -ne 0 ]; then say "SELFTEST FAIL"; exit 2; fi
say "SELFTEST PASS $PASS/$((PASS+FAIL))"
exit 0
