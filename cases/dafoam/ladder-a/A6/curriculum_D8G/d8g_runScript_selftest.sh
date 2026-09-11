#!/usr/bin/env bash
# =============================================================================
# PERMISSION: FROZEN by the dafoam-supervisor 2026-09-11.
#
# SELFTEST FOR d8g_runScript.py -- THE D8G PRODUCER SCRIPT.
#
# THE PRODUCER IS A BYTE COPY AND THAT IS THE REGISTRATION, NOT A CONVENIENCE.
# PREREGISTRATION.md:316 says it in as many words: "because D8G's producer is D8R's
# and a family whose acceptance rule changes between levels is not a family."  So
# this suite cannot live inside the file it tests -- a `--selftest` block would
# break the byte identity that IS the provenance.  It tests
# `d8g_runScript_contract.py`, the separate checker, in three ways:
#
#  (1) the checker's 27 units against the real producer, under BOTH `python3` and
#      `python3 -O` (L-332: an instrument that gates on `assert` gates on nothing
#      under -O; this one carries zero and the census is printed), and
#
#  (2) THE THREE-WAY BYTE IDENTITY, asserted here as well as inside the checker,
#      because it is the whole provenance claim: D8's frozen opt/runScript.py,
#      curriculum_D8R/d8r_runScript.py and this file are ONE md5, and this file is
#      NOT the archived A6 tutorial runScript that sits in the same staging tree
#      carrying a different acceptance pair, and
#
#  (3) IT MUTATES A COPY OF THE PRODUCER AND ASSERTS THE CHECKER THEN FAILS.
#      A SUITE THAT PASSES PROVES NOTHING UNTIL IT IS SEEN TO FAIL.  Thirteen
#      mutations, each breaking exactly one thing `d8g_of.py` or `d8g_grade.py`
#      depends on, each asserted to make a NAMED unit go BAD.  Note the direction:
#      THE PRODUCER IS MUTATED, NOT THE CHECKER -- a checker mutation would prove
#      only that the checker can fail, not that it can catch.
#
# THE MUTATOR IS ITSELF A PLANTED-ZERO RISK AND IS GUARDED: every mutation asserts
# REPLACEMENT COUNT == 1 and asserts the copy DIFFERS, before the checker is run,
# and this harness ALWAYS emits exactly one check per mutation -- an earlier suite
# in this case directory chained `mutate && run` and a refused mutator silently
# emitted no check at all.
#
# WHAT THIS DOES NOT TEST, STATED PLAINLY: nothing here imports DAFoam, IDWarp,
# mphys, pyGeo or OpenMDAO, and the header is NEVER EXECUTED.  A green means the
# producer satisfies the contract `d8g_of.py` reads it through.  It does NOT mean
# any D8G arm has ever run, and it says nothing about whether DAFoamBuilder accepts
# these options on a 5,568-cell mesh.
# =============================================================================
set -uo pipefail

HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
TARGET="$HERE/d8g_runScript.py"
CHECKER="$HERE/d8g_runScript_contract.py"
OF="$HERE/d8g_of.py"
FROZEN_MD5=28c7819487a025a5f6554d38062a2b66
D8R_PRODUCER=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A6/curriculum_D8R/d8r_runScript.py
D8_PRODUCER=/home/ubuntu/certonomous-runs/CURRICULUM-D8-a6-twist-opt/opt/runScript.py
ARCHIVE_TUTORIAL=/home/ubuntu/certonomous-runs/A6-crm-wing/runScript.py
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
PASS=0; FAIL=0
say() { printf '%s\n' "$*"; }
check() { if [ "$2" = "$3" ]; then PASS=$((PASS+1)); say "  PASS  $1  (expected=$2 got=$3)"
          else FAIL=$((FAIL+1)); say "  FAIL  $1  (expected=$2 got=$3)"; fi; }

for f in "$TARGET" "$CHECKER" "$OF"; do
  test -f "$f" || { say "REFUSE C0 not found: $f"; exit 2; }
done
say "D8G RUNSCRIPT SELFTEST  target=$TARGET"
say "                        md5=$(md5sum "$TARGET" | cut -d' ' -f1)"
say "                        checker=$CHECKER"
say "                        date_u=$(date -u +%Y-%m-%dT%H:%M:%SZ)  host_python=$(python3 -V 2>&1)"
say ""

say "A. the contract checker against the real producer, both interpreter modes"
python3    "$CHECKER" --target "$TARGET" --of "$OF" > "$TMP/clean.out" 2>&1;  RC1=$?
python3 -O "$CHECKER" --target "$TARGET" --of "$OF" > "$TMP/cleanO.out" 2>&1; RC2=$?
check "A1 checker under python3"            0 "$RC1"
check "A2 checker under python3 -O"         0 "$RC2"
check "A3 unit count under python3"        27 "$(grep -c '^  \[OK \]' "$TMP/clean.out")"
check "A4 unit count under python3 -O"     27 "$(grep -c '^  \[OK \]' "$TMP/cleanO.out")"
check "A5 zero BAD units"                   0 "$(grep -c '^  \[BAD\]' "$TMP/clean.out")"
check "A6 ast.Assert census of the PRODUCER is 0 (L-332)" 0 \
  "$(python3 -c "import ast;print(sum(1 for n in ast.walk(ast.parse(open('$TARGET').read())) if isinstance(n,ast.Assert)))")"
check "A7 ast.Assert census of the CHECKER is 0 (L-332)" 0 \
  "$(python3 -c "import ast;print(sum(1 for n in ast.walk(ast.parse(open('$CHECKER').read())) if isinstance(n,ast.Assert)))")"
check "A8 the checker leaves NO __pycache__ in the case directory (a stale cache inverts the mutation controls below)" \
  absent "$(test -d "$HERE/__pycache__" && echo present || echo absent)"
say ""

say "B. THE THREE-WAY BYTE IDENTITY -- the provenance claim, checked here too"
check "B1 producer == the frozen D8->D8R->D8G md5" "$FROZEN_MD5" "$(md5sum "$TARGET" | cut -d' ' -f1)"
check "B2 producer == curriculum_D8R/d8r_runScript.py (FROZEN, graded two-row PASS)" \
  "$(md5sum "$D8R_PRODUCER" 2>/dev/null | cut -d' ' -f1)" "$(md5sum "$TARGET" | cut -d' ' -f1)"
check "B3 producer == D8's own frozen opt/runScript.py" \
  "$(md5sum "$D8_PRODUCER" 2>/dev/null | cut -d' ' -f1)" "$(md5sum "$TARGET" | cut -d' ' -f1)"
check "B4 producer is NOT the archived A6 tutorial runScript (the WRONG file, same staging tree)" \
  different "$([ "$(md5sum "$TARGET" | cut -d' ' -f1)" = "$(md5sum "$ARCHIVE_TUTORIAL" 2>/dev/null | cut -d' ' -f1)" ] && echo same || echo different)"
say ""

mut_case() {  # $1 tag  $2 old  $3 new  $4 the unit that must catch it
  local tag="$1" old="$2" new="$3" want="$4"
  local dst="$TMP/mut_$tag.py"
  rm -f "$dst"
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
    check "C-$tag MUTATOR applied exactly one replacement" yes "no($(tr -d '\n' < "$TMP/mut_$tag.err"))"
    return
  fi
  if cmp -s "$TARGET" "$dst"; then
    check "C-$tag mutated copy DIFFERS from the original (planted-zero guard)" yes no
    return
  fi
  python3 "$CHECKER" --target "$dst" --of "$OF" > "$TMP/mut_$tag.out" 2>&1
  local rc=$? caught=no
  if [ "$rc" -ne 0 ] && grep -q -- "$want" "$TMP/mut_$tag.out"; then caught=yes; fi
  if grep -q '^REFUSE target not found' "$TMP/mut_$tag.out"; then caught="no(target-not-loaded)"; fi
  check "C-$tag CHECKER FAILS and [$want] is the catcher" yes "$caught"
}

say "C. mutation controls -- THE PRODUCER IS MUTATED and the checker must be SEEN TO FAIL"

# C1  THE ACCEPTANCE PAIR BECOMES THE ARCHIVED TUTORIAL'S.  This is the single most
#     expensive confusion available: both files live in the same staging tree, the arm
#     completes, and the comparator REFUSES (exit 2) on the log read-back afterwards.
mut_case TOLDIFF-IS-THE-TUTORIALS '"primalMinResTolDiff": 1.0e4,' '"primalMinResTolDiff": 100.0,' \
  'BAD] U17 primalMinResTolDiff == 10000'

# C2  the tolerance itself drifts -- the accept floor silently becomes 1e-02.
mut_case TOL-DRIFTED '"primalMinResTol": 1.0e-8,' '"primalMinResTol": 1.0e-6,' \
  'BAD] U16 primalMinResTol == 1.0e-08'

# C3  THE CADENCE CHANGES AND G-PLAT'S WINDOW COLLAPSES.  At printInterval 100 the arm
#     prints 11 samples, not 101; the window falls to 10 and the level is one sample from
#     NOT A RESULT FOR WANT OF EVIDENCE.
mut_case PRINTINTERVAL-100 '"printInterval": 10,' '"printInterval": 100,' \
  'BAD] U19 printInterval == 10'

# C4  `Top` is renamed, so d8g_of.py's ns['Top'] KeyErrors -- AFTER the container started.
mut_case TOP-RENAMED 'class Top(Multipoint):' 'class TopModel(Multipoint):' \
  'BAD] U7 `class Top` is defined ABOVE the anchor'

# C5  THE ANCHOR VANISHES: split() returns the whole file, the header exec runs
#     `om.n2` and `prob.setup` a second time, and nothing says so.
mut_case ANCHOR-GONE '# OpenMDAO setup' '# OpenMDAO set-up' \
  'BAD] U5 the anchor'

# C6  THE ANCHOR APPEARS TWICE: split()[0] silently truncates the header at the FIRST
#     one and `Top` is never defined.  Both directions of the same unit.
mut_case ANCHOR-TWICE '# Mesh deformation setup' '# OpenMDAO setup' \
  'BAD] U5 the anchor'

# C7  the design surface is renamed -- it no longer matches the patch the mesh record
#     registers, and every functional integrates over nothing.
mut_case DESIGNSURFACE-CASE '"designSurfaces": ["wing"],' '"designSurfaces": ["Wing"],' \
  'BAD] U21 designSurfaces'

# C8  THE SECOND GRADED FUNCTIONAL DISAPPEARS.  Section 4.6 grades CD *and* CL, and
#     G-PLAT applies independently to both; without CL the whole second row is ungated.
mut_case CL-FUNCTION-GONE '"CL": {' '"CLift": {' \
  'BAD] U22 daOptions'

# C9  patchV stops being a design variable -- read_A requires adjoint.{CD,CL}.patchV and
#     would KeyError at grading time.
mut_case PATCHV-NOT-A-DV 'self.add_design_var("patchV"' 'self.add_design_var("patchVel"' \
  'BAD] U24 both'

# C10 THE HEADER BUILDS A PROBLEM OF ITS OWN.  The exec would then construct a second
#     om.Problem before d8g_of.py builds the one it actually drives.
mut_case HEADER-BUILDS-PROBLEM 'meshOptions = {' 'prob = om.Problem()
meshOptions = {' \
  'BAD] U10 the header builds NO om.Problem'

# C11 THE HEADER PRINTS.  G-PRIMAL and G-PLAT read the SOLVER'S own stdout; a producer
#     line in that stream is forged evidence for a gate that reads the log.
mut_case HEADER-PRINTS 'meshOptions = {' 'print("Time = 0")
meshOptions = {' \
  'BAD] U12 the header PRINTS NOTHING'

# C12 THE HEADER BRANCHES ON THE PARSED ARGS.  d8g_of.py substitutes sys.argv with
#     `-task run_model`; a header that branched would take a path the arm did not choose.
mut_case HEADER-USES-ARGS 'meshOptions = {' 'if args.task == "run_driver":
    pass
meshOptions = {' \
  'BAD] U13 the header never CONSUMES the parsed args'

# C13 THE BYTES MOVE AT ALL.  The provenance claim is a byte identity; one trailing
#     newline breaks it, and d8g_of.py's own PRODUCER_MD5 refusal would then fire.
mut_case BYTES-MOVED 'import argparse' 'import argparse  # trailing edit' \
  'BAD] U1 the producer hashes to the frozen'

say ""
say "D8G RUNSCRIPT SELFTEST SUMMARY pass=$PASS fail=$FAIL"
if [ "$FAIL" -ne 0 ]; then say "SELFTEST FAIL"; exit 2; fi
say "SELFTEST PASS $PASS/$((PASS+FAIL))"
exit 0
