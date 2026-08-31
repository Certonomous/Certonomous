#!/usr/bin/env bash
# SO-1c LAUNCHER AND DRIVER GUARD SELFTEST -- every guard DRIVEN to FIRE, not
# asserted to exist.  DERIVED from curriculum_SO1a/so1a_groot5_selftest.sh with
# the registered deltas in so1c_groot5_selftest_DELTAS_from_so1a.diff.
#
# THE ZERO-CONTAINER CONSTRAINT, AND THE ONE LEG IT COSTS -- STATED FIRST.
# SO-1a's and SO-1b's suites each started a sacrificial `sleep` container to drive
# the POSITIVE side of G-ROOT.5 leg (a) ("a RUNNING container already carries this
# item's prefix and arm").  This lane is registering under an explicit
# ZERO-CONTAINERS-CREATED instruction, so THAT ONE LEG IS NOT DRIVEN HERE and is
# recorded as NOT DRIVEN rather than quietly counted as passing.  Its NEGATIVE
# side IS driven (leg a0 below: with no such container the guard passes), and the
# exact command that drives the positive side is printed in the evidence so the
# supervisor can run it in one line before first compute.  A leg not driven is
# named; it is never counted.
#
# CONTROLS PROVE A POSITIVE BRANCH BY THE ORDER OF REFUSALS, NEVER BY EXECUTING
# THE PROTECTED PATH.  Every leg below either (i) drives a guard to REFUSE with
# its registered rc, or (ii) shows a guard PASS on a state that is safe by
# construction.  No leg reaches `docker run`, and the suite asserts at the end
# that the run root is still ABSENT.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LAUNCHER="$HERE/so1c_run_arm.sh"
DRIVER="$HERE/so1c_chain_driver.sh"
REG_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-SO1c-a1-naca0012-dragmin-npinv
TMP="${TMPDIR:-/tmp}/so1c_groot5_$$"
N=0; FAIL=0
mkdir -p "$TMP" || exit 4

leg() {  # leg <name> <expected_rc> <actual_rc>
  N=$((N+1))
  if [ "$2" = "$3" ]; then echo "  [OK ] $1 (rc=$3)"; else echo "  [BAD] $1 (want rc=$2 got rc=$3)"; FAIL=$((FAIL+1)); fi
}
# LINE NUMBERS ARE READ FROM EXECUTABLE LINES ONLY.  A first attempt at these
# ordering legs matched the launcher's own COMMENTS about `rm -rf "$WORK"` and
# reported an order that was not the code's -- so the helper strips comment lines
# before taking the first match.  An ordering proof that can be satisfied by prose
# is not an ordering proof.
firstexec() { grep -n -- "$1" "$2" | grep -v ':[[:space:]]*#' | head -1 | cut -d: -f1; }
legc() { # legc <name> <condition-rc>
  N=$((N+1))
  if [ "$2" = "0" ]; then echo "  [OK ] $1"; else echo "  [BAD] $1"; FAIL=$((FAIL+1)); fi
}

echo "SO1c GUARD SELFTEST  stamp=$(date -u +%Y%m%dT%H%M%SZ)"
echo "run root ABSENT before the test: $(test -e "$REG_BASE" && echo NO || echo YES)"
CONTAINERS_BEFORE=$(sudo -n docker ps -a -q 2>/dev/null | wc -l)
echo "containers on the box BEFORE: $CONTAINERS_BEFORE"
echo

# ---------------------------------------------------------------- G-ROOT.1/.2/.3
BASE="$TMP/not_the_registered_root" bash "$LAUNCHER" Ns-P dafoam/opt-packages:latest >"$TMP/a1.out" 2>&1
leg "(a1) G-ROOT.1 BASE is not this item's registered run root -> ABORT" 3 $?
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-SO1bR-a1-naca0012-dragmin-opt bash "$LAUNCHER" Ns-P dafoam/opt-packages:latest >"$TMP/a2.out" 2>&1
leg "(a2) G-ROOT.1/.2 BASE = SO-1bR's OWN RUN ROOT -> ABORT (the root this item READS)" 3 $?
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6-a2-wing-multipoint bash "$LAUNCHER" Ns-P dafoam/opt-packages:latest >"$TMP/a3.out" 2>&1
leg "(a3) G-ROOT.1/.2 BASE = D6's LIVE run root -> ABORT before any staging" 3 $?
grep -q "CURRICULUM-SO1b-a1-naca0012-dragmin-opt" "$HERE/so1c_run_arm.sh"
legc "(a4) SO-1a's and SO-1b's run roots are BOTH in FORBIDDEN_ROOTS" $?
grep -q "CURRICULUM-SO1a-a1-naca0012-dragmin-gradient" "$HERE/so1c_run_arm.sh"
legc "(a5) ... and SO-1a's is too" $?
grep -q "CURRICULUM-SO1bR-a1-naca0012-dragmin-opt" "$HERE/so1c_run_arm.sh"
legc "(a5b) AMENDMENT R7: SO-1bR's run root -- the root this item now READS -- is in FORBIDDEN_ROOTS too, ADDED BESIDE SO-1b's and never replacing it" $?
# (a5c) AMENDMENT R7.  NOTHING DROVE THE DRIVER'S OWN md5 PINS.  Adding SO-1bR to
# FORBIDDEN_ROOTS changed so1c_run_arm.sh and stale-ed MD5_LAUNCHER; the suite stayed
# GREEN and the chain would have aborted rc=4 before any container -- the W3 death mode.
#
# RE-SCOPED AND FAIL-CLOSED BY AMENDMENT R8, 2026-08-31.  RULING: KEEP, RE-SCOPE,
# DO NOT STRIKE -- the leg is right in kind and its known positive is real (a
# one-byte mutation of so1c_run_arm.sh drove it [BAD] naming pinned-vs-actual).
# TWO DEFECTS, BOTH MEASURED BEFORE BEING REPAIRED:
#   SO1C-A5C-DEF-1 (SCOPE).  The driver carries TWELVE MD5_* pins and R7's leg
#     drove FOUR, under a printed label reading "EVERY md5 PIN IN THE DRIVER" --
#     false of 4-of-12.  Two it missed, MD5_DECOMP_SCOTCH and MD5_DECOMP_SIMPLE,
#     pin IN-REPO files this item stages and the driver asserts at :266-268 with
#     exit 4; a one-byte edit to so1c_decomposeParDict_simple left this leg GREEN
#     while the chain would abort exit 4 before any container -- the exact death
#     mode the leg exists to prevent, alive on a different pin.  R8 widens (a5c)
#     to ALL SIX IN-REPO pins and drives the other six in (a5d).
#   SO1C-A5C-DEF-2 (FAIL-OPEN).  Rename the pin variable AND delete its file and
#     both reads are empty; [ "" = "" ] is TRUE and the leg went GREEN.  ABSENCE
#     OF A SIGNAL READ AS ABSENCE OF A PROBLEM.  An empty read now REFUSES.
# THE LABEL BELOW SAYS WHAT THE LEG ACTUALLY ASSERTS.  THE EXCLUSION IS STATED,
# NOT SILENT: the six MD5_TUT_* pins name OUT-OF-TREE upstream tutorial inputs
# under the driver's own TUT_SRC, which this repository does not hold constant --
# they are driven by (a5d) as a leg of their own, so no pin is left unexamined,
# and (a5e) asserts the two legs between them cover every pin the driver carries.
PINFAIL=0; PINSEEN=0
for pv in MD5_LAUNCHER:so1c_run_arm.sh MD5_GRADER:so1c_grade.py MD5_XN:so1c_xn.py \
          MD5_RUNSCRIPT:so1c_runScript.py \
          MD5_DECOMP_SCOTCH:so1c_decomposeParDict_scotch \
          MD5_DECOMP_SIMPLE:so1c_decomposeParDict_simple; do
  v=${pv%%:*}; f=${pv##*:}
  p=$(grep -oP "(?<=^$v=)[0-9a-f]{32}" "$HERE/so1c_chain_driver.sh")
  a=$(md5sum "$HERE/$f" 2>/dev/null | cut -d" " -f1)
  if [ -z "$p" ]; then echo "    PIN UNREADABLE $v: the driver carries no 32-hex pin under that name (renamed or deleted variable) -- an EMPTY read is a REFUSAL, not a match"; PINFAIL=1; continue; fi
  if [ -z "$a" ]; then echo "    FILE UNREADABLE $f: no md5 (file absent or unreadable) -- an EMPTY read is a REFUSAL, not a match"; PINFAIL=1; continue; fi
  PINSEEN=$((PINSEEN+1))
  [ "$p" = "$a" ] || { echo "    PIN MISMATCH $v pinned=$p actual=$a ($f)"; PINFAIL=1; }
done
[ "$PINSEEN" = "6" ] || { echo "    PIN COUNT $PINSEEN in-repo pins compared, expected 6"; PINFAIL=1; }
legc "(a5c) ALL SIX IN-REPO md5 PINS IN THE DRIVER EQUAL THE FILES THEY PIN ($PINSEEN compared), and an EMPTY read on either side REFUSES -- a stale pin aborts the chain rc=4 before any container.  The six MD5_TUT_* pins name OUT-OF-TREE tutorial inputs and are driven by (a5d); the exclusion is STATED, not silent" $PINFAIL

# (a5d) AMENDMENT R8.  The other six pins, driven rather than excused.  These pin
# the upstream tutorial INPUT bytes under the driver's own TUT_SRC; the driver
# asserts them at :197-199 with exit 4 before it stages anything, so a checkout
# that moved under this item kills the chain exactly as a stale in-repo pin does.
# The path is READ FROM THE FROZEN DRIVER, never re-typed here.
TUT_SRC=$(grep -oP '(?<=^TUT_SRC=)\S+' "$HERE/so1c_chain_driver.sh")
TUTFAIL=0; TUTSEEN=0
if [ -z "$TUT_SRC" ]; then
  echo "    TUT_SRC UNREADABLE: no TUT_SRC assignment in the driver"; TUTFAIL=1
else
  for pv in MD5_TUT_RUNSCRIPT:runScript.py MD5_TUT_GEN:genAirFoilMesh.py MD5_TUT_PREPROC:preProcessing.sh \
            MD5_TUT_PS:profiles/NACA0012PS.profile MD5_TUT_SS:profiles/NACA0012SS.profile \
            MD5_TUT_FFD:FFD/wingFFD.xyz; do
    v=${pv%%:*}; f=${pv##*:}
    p=$(grep -oP "(?<=^$v=)[0-9a-f]{32}" "$HERE/so1c_chain_driver.sh")
    a=$(md5sum "$TUT_SRC/$f" 2>/dev/null | cut -d" " -f1)
    if [ -z "$p" ]; then echo "    PIN UNREADABLE $v: no 32-hex pin under that name -- an EMPTY read is a REFUSAL"; TUTFAIL=1; continue; fi
    if [ -z "$a" ]; then echo "    FILE UNREADABLE $TUT_SRC/$f: no md5 -- an EMPTY read is a REFUSAL"; TUTFAIL=1; continue; fi
    TUTSEEN=$((TUTSEEN+1))
    [ "$p" = "$a" ] || { echo "    PIN MISMATCH $v pinned=$p actual=$a ($TUT_SRC/$f)"; TUTFAIL=1; }
  done
  [ "$TUTSEEN" = "6" ] || { echo "    PIN COUNT $TUTSEEN out-of-tree pins compared, expected 6"; TUTFAIL=1; }
fi
legc "(a5d) ALL SIX OUT-OF-TREE MD5_TUT_* PINS EQUAL THE TUTORIAL INPUTS THEY PIN under $TUT_SRC ($TUTSEEN compared), empty reads REFUSING -- the driver asserts these at :197-199 with exit 4, so a moved checkout is the same death mode as a stale in-repo pin" $TUTFAIL

# (a5e) AMENDMENT R8.  THE COVERAGE ASSERTION ITSELF, so SO1C-A5C-DEF-1 cannot
# recur silently: R7's leg drove 4 of 12 under a label claiming every pin, and
# nothing in the suite could notice.  A pin nobody drives is the W3 death mode
# waiting on a different variable name.  This leg goes RED the moment a
# thirteenth pin is added without being driven.
PINS_IN_DRIVER=$(grep -cE '^MD5_[A-Z_0-9]+=[0-9a-f]{32}' "$HERE/so1c_chain_driver.sh")
[ "$PINS_IN_DRIVER" = "12" ] && [ "$((PINSEEN+TUTSEEN))" = "12" ]
legc "(a5e) THE PIN LIST IS COMPLETE: the driver carries $PINS_IN_DRIVER MD5_* pins and (a5c)+(a5d) drove $((PINSEEN+TUTSEEN)) of them -- R7's (a5c) drove 4 of 12 under a label that claimed all of them, and no leg could see the gap" $?

mkdir -p "$TMP/root3" && chmod 777 "$TMP/root3"
echo "ITEM=SO1b" > "$TMP/root3/ledger.txt"
BASE="$TMP/root3" bash "$LAUNCHER" Ns-P dafoam/opt-packages:latest >"$TMP/a6.out" 2>&1
leg "(a6) G-ROOT.3 a FOREIGN ITEM= ledger row -> ABORT" 3 $?

# ---------------------------------------------------------------- G-ROOT.5 (b)
# The pidfile leg is driven WITHOUT a container: a real live process that is not
# an ancestor of the launcher is exactly what the guard is written to catch.
mkdir -p "$TMP/root5" && chmod 777 "$TMP/root5"
setsid sleep 120 >/dev/null 2>&1 &
FOREIGN=$!
echo "$FOREIGN" > "$TMP/root5/so1c_driver.pid"
BASE="$TMP/root5" bash "$LAUNCHER" Ns-P dafoam/opt-packages:latest >"$TMP/b1.out" 2>&1
RC=$?
kill "$FOREIGN" 2>/dev/null
# G-ROOT.1 fires first on a non-registered BASE, so this leg proves ORDER, not the
# pidfile branch alone; the pidfile branch itself is proved by the code path check
# below.  Controls prove a branch by the ORDER of refusals, never by executing the
# protected path -- so the ordering assertion IS the evidence here.
leg "(b1) a LIVE foreign driver pid + a non-registered root -> ABORT (root guard first)" 3 $RC
L_R5=$(firstexec 'D4S_G_ROOT5_PASS' "$LAUNCHER")
L_RM=$(firstexec 'sudo -n rm -rf "\$WORK"' "$LAUNCHER")
L_DR=$(firstexec 'sudo -n docker run -d' "$LAUNCHER")
[ -n "$L_R5" ] && [ -n "$L_RM" ] && [ -n "$L_DR" ] && [ "$L_R5" -lt "$L_RM" ] && [ "$L_RM" -lt "$L_DR" ]
legc "(b2) ORDER BY LINE NUMBER: G-ROOT.5 pass :$L_R5 < first \`rm -rf \$WORK\` :$L_RM < \`docker run\` :$L_DR" $?

# ---------------------------------------------------------------- G-CAP-PREREG
mkdir -p "$TMP/pr" && cp "$HERE/PREREGISTRATION.md" "$TMP/pr/ok.md" 2>/dev/null
if [ -f "$TMP/pr/ok.md" ]; then
  PREREG="$TMP/pr/ok.md" BASE="$TMP/not_registered" bash "$LAUNCHER" Ns-P dafoam/opt-packages:latest >"$TMP/g0.out" 2>&1
  grep -q "ABORT G-ROOT.1" "$TMP/g0.out"
  legc "(g0) POSITIVE CONTROL: the REAL launcher against the REAL frozen document does NOT abort on G-CAP-PREREG (it reaches the root guard) -- a check that only ever refuses is not a check" $?

  sed 's/Ns-P=30.0/Ns-P=40.0/' "$TMP/pr/ok.md" > "$TMP/pr/cap.md"
  PREREG="$TMP/pr/cap.md" bash "$LAUNCHER" Ns-P dafoam/opt-packages:latest >"$TMP/g1.out" 2>&1
  leg "(g1) a document cap of 40.0 against the launcher's registered 30.0 -> ABORT rc=65 BEFORE any container" 65 $?

  sed 's/CEILING=125.0/CEILING=999.0/' "$TMP/pr/ok.md" > "$TMP/pr/ceil.md"
  PREREG="$TMP/pr/ceil.md" bash "$LAUNCHER" Ns-P dafoam/opt-packages:latest >"$TMP/g2.out" 2>&1
  leg "(g2) a CEILING that is not the sum of the caps -> ABORT rc=65" 65 $?

  grep -v "SO1C-CAP-MANIFEST" "$TMP/pr/ok.md" > "$TMP/pr/nomanifest.md"
  PREREG="$TMP/pr/nomanifest.md" bash "$LAUNCHER" Ns-P dafoam/opt-packages:latest >"$TMP/g3.out" 2>&1
  leg "(g3) the manifest line DELETED -> ABORT rc=65" 65 $?

  PREREG="$TMP/pr/does_not_exist.md" bash "$LAUNCHER" Ns-P dafoam/opt-packages:latest >"$TMP/g4.out" 2>&1
  leg "(g4) the pre-registration ABSENT -> ABORT rc=65" 65 $?

  sed 's/RANKS_N=4/RANKS_N=1/' "$TMP/pr/ok.md" > "$TMP/pr/ranks.md"
  PREREG="$TMP/pr/ranks.md" bash "$LAUNCHER" Ns-P dafoam/opt-packages:latest >"$TMP/g5.out" 2>&1
  leg "(g5) a document RANKS_N of 1 against the launcher's 4 -> ABORT rc=65 (a core-minute cap means nothing without its rank count)" 65 $?
else
  echo "  [SKIP] (g0-g5) G-CAP-PREREG legs: PREREGISTRATION.md not yet on disk"
fi

# ---------------------------------------------------------------- arm table
# The REGISTERED (and ABSENT) base is used here on purpose: the root guards pass,
# and the abort must then come from the ARM TABLE.  The launcher creates nothing
# before that point -- it only `realpath -m`s and reads -- so the run root stays
# absent, which the final leg re-asserts.
BASE="$REG_BASE" bash "$LAUNCHER" X-S dafoam/opt-packages:latest >"$TMP/c1.out" 2>&1
leg "(c1) an UNREGISTERED arm name (SO-1a's X-S) past the root guards -> ABORT rc=64, no rank count" 64 $?
grep -q 'Ns-P|Ni-P|Ns-S|Ni-S)  echo 4 ;;' "$LAUNCHER"
legc "(c2) every solver arm is registered at 4 ranks; MESH at 1" $?
grep -q 'Ns-P|Ni-P|Ns-S|Ni-S)     echo 10,11,12,13 ;;' "$LAUNCHER"
legc "(c3) every np=4 arm is pinned to FOUR DISTINCT cores 10,11,12,13" $?
for CS in "2,3,4,14" "5,6,7,9"; do
  grep -q "echo $CS" "$LAUNCHER" && { echo "  [BAD] (c4) a SIBLING's registered cpuset appears in this launcher: $CS"; FAIL=$((FAIL+1)); }
done
N=$((N+1)); echo "  [OK ] (c4) 10,11,12,13 is DISJOINT from D6's 2,3,4,14 and D4-SHIPPED's 5,6,7,9"
grep -q 'Ns-P|Ns-S) echo scotch ;;' "$LAUNCHER" && grep -q 'Ni-P|Ni-S) echo simple ;;' "$LAUNCHER"
legc "(c5) the decomposition is resolved FROM THE ARM NAME: Ns->scotch, Ni->simple" $?

# ---------------------------------------------------------------- G-OPTDEP
mkdir -p "$TMP/root6/optref/PATCHED" && chmod -R 777 "$TMP/root6"
BASE="$TMP/root6" bash "$LAUNCHER" Ns-P dafoam/opt-packages:latest >"$TMP/d1.out" 2>&1
leg "(d1) an N arm whose row's SO-1b optimum is ABSENT -> ABORT (root guard fires first; see d3 for the guard itself)" 3 $?
L_OD=$(firstexec 'SO1C_G_OPTDEP_PASS' "$LAUNCHER")
L_CP=$(firstexec 'SO1C_G_CAP_PREREG_PASS' "$LAUNCHER")
[ -n "$L_OD" ] && [ "$L_CP" -lt "$L_OD" ] && [ "$L_OD" -lt "$L_RM" ]
legc "(d2) ORDER: G-CAP-PREREG :$L_CP < G-OPTDEP :$L_OD < first \`rm -rf \$WORK\` :$L_RM -- every guard precedes every destructive step" $?
grep -q 'test -f "$OPTREF" ||' "$LAUNCHER" && grep -q "exit 5" "$LAUNCHER"
legc "(d3) G-OPTDEP refuses an absent own-row optimum with rc=5" $?
grep -q "STAGED_INPUT_NOT_A_PRODUCT" "$LAUNCHER"
legc "(d4) the staged so1b_E.json is LABELLED a staged input in the launcher's own log line" $?
L_CPO=$(firstexec 'cp -a "\$OPTREF"' "$LAUNCHER"); L_TCH=$(firstexec 'touch "\$WORK/0"' "$LAUNCHER")
[ -n "$L_CPO" ] && [ -n "$L_TCH" ] && [ "$L_CPO" -lt "$L_TCH" ]
legc "(d5) THE AGE-GUARD ORDER: the staged input is \`cp -a\`d BEFORE the age datum is touched, so a staged input is always OLDER than the datum and can never satisfy an age clause" $?

# ---------------------------------------------------------------- G-SO1B (driver)
mkdir -p "$TMP/so1b/O-P" "$TMP/so1b/O-S" "$TMP/so1b/E-P" "$TMP/so1b/E-S"
mkgrade() { # mkgrade <gopt_P> <gopt_S> <gcl_P> <gcl_S>
  python3 - "$1" "$2" "$3" "$4" <<'PY'
import json, sys, os
b = os.environ["SO1B"]
json.dump({"gates": {"G-OPT_PATCHED": {"verdict": sys.argv[1]}, "G-OPT_SHIPPED": {"verdict": sys.argv[2]},
                     "G-CL_PATCHED": {"verdict": sys.argv[3]}, "G-CL_SHIPPED": {"verdict": sys.argv[4]}}},
          open(os.path.join(b, "SO1bR_grade_x.json"), "w"))
for rk, d in (("PATCHED", "P"), ("SHIPPED", "S")):
    json.dump({"ipopt": {"exit_line": "EXIT: Optimal Solution Found."},
               "shape_opt": ["0.1"], "patchV_opt": ["10.0", "1.13"]},
              open(os.path.join(b, "O-%s" % d, "so1b_O.json"), "w"))
    json.dump({"design_point": {"shape": ["0.1"], "patchV": ["10.0", "1.13"]},
               "adjoint": {}, "identity": {}, "nprocs": 1, "row": rk},
              open(os.path.join(b, "E-%s" % d, "so1b_E.json"), "w"))
PY
}
export SO1B="$TMP/so1b"
# The G-SO1B block is exercised through the driver's OWN python, extracted verbatim
# from the frozen file -- never a re-implementation of it.
gso1b_at() { # gso1b_at <grade_path> <so1b_base> -> rc
  python3 - "$1" "$2" <<'PY' >"$TMP/e.out" 2>&1
import json, os, sys, re
drv = os.environ["DRIVER"]
src = open(drv).read()
body = src.split("python3 - \"$SO1B_GRADE\" \"$SO1B_BASE\" <<'GSO1B'\n", 1)[1].split("\nGSO1B\n", 1)[0]
g = {"__name__": "__main__", "sys": sys}
sys.argv = ["x", sys.argv[1], sys.argv[2]]
exec(compile(body, "G-SO1B", "exec"), g)
PY
  echo $?
}
gso1b() { # gso1b -> rc.  The synthetic fixture, unchanged; now the one-argument
          # case of gso1b_at so the extraction exists in exactly ONE place.
  gso1b_at "$SO1B/SO1bR_grade_x.json" "$SO1B"
}
export DRIVER
mkgrade PASS PASS PASS PASS
leg "(e1) G-SO1B: PATCHED G-OPT PASS, SHIPPED G-OPT PASS, both G-CL PASS -> PROCEED" 0 "$(gso1b)"
mkgrade PASS "GATE REACHED" PASS PASS
leg "(e2) G-SO1B: the SHIPPED row at GATE REACHED is ACCEPTED -- a deformed mesh at an iterate is still a design point (registered asymmetry)" 0 "$(gso1b)"
mkgrade "GATE REACHED" PASS PASS PASS
leg "(e3) G-SO1B: the PATCHED row at GATE REACHED is REFUSED rc=7 -- the control must be a real optimum" 7 "$(gso1b)"
mkgrade PASS PASS PASS "GATE FAIL"
leg "(e4) G-SO1B: a row whose re-solve did not recover the lift (G-CL not PASS) -> REFUSED rc=7" 7 "$(gso1b)"
mkgrade "NOT A RESULT" PASS PASS PASS
leg "(e5) G-SO1B: PATCHED G-OPT NOT A RESULT -> REFUSED rc=7" 7 "$(gso1b)"
grep -q "item_verdict_deliberately_not_read=yes" "$DRIVER"
legc "(e6) G-SO1B READS THE SPECIFIC GATES, NOT SO-1b's ITEM VERDICT -- gating on the item verdict would kill SO-1c in SO-1b's own predicted outcome (SO-1b predicts item GATE FAIL)" $?
# The DRIVER's own comment block explains that it does not read G5E, so a bare
# grep for the word matches PROSE.  Only EXECUTABLE lines are searched.
N=$((N+1))
if grep -n -- "G5E" "$DRIVER" | grep -qv ':[[:space:]]*#'; then
  echo "  [BAD] (e7) an EXECUTABLE line of the driver reads SO-1b's G5E FD gate"; FAIL=$((FAIL+1))
else
  echo "  [OK ] (e7) NO executable line of the driver reads SO-1b's G5E FD gate -- this item buys its own FD table at np=4, and DAFOAM_CHARTER.md section 5 forbids carrying an FD reference across np"
fi

# =========================================================================
# AMENDMENT R8, 2026-08-31 -- THE POSITIVE PATH IS ANCHORED IN A REAL PRODUCER
# ARTEFACT, BECAUSE 51 GREEN LEGS SAW NEITHER BREAK 5 NOR BREAK 6.
#
# WHY THIS BLOCK EXISTS, STATED PLAINLY.  Every G-SO1B fixture above is HAND-BUILT
# by `mkgrade` FROM THE CONSUMER'S EXPECTATIONS: it writes {"gates": {...}} at the
# TOP LEVEL and labels its E artefacts 'PATCHED'/'SHIPPED' -- which is exactly the
# shape the gate reads.  So the suite proved that the gate reads the shape the
# fixture writes, and the fixture writes the shape the gate reads.  THAT IS A
# TAUTOLOGY ON SCHEMA, AND NO NUMBER OF LEGS ESCAPES IT.  A self-test whose
# fixtures are authored from the consumer's expectations CANNOT DETECT A
# PRODUCER-SIDE SCHEMA CHANGE.  SO-1b -> SO-1bR wrapped the grade dict under
# `grade` and labelled the E artefacts 'P'/'S'; the suite stayed 51/0 across both
# changes, and the defect was found only by a supervisor driving the real file by
# hand at the pre-compute gate.
#
# THE REPAIR: the fixtures below are COPIED OUT OF THE PRODUCER'S OWN RUN ROOT and
# are never authored here.  The producer's path is READ FROM THE FROZEN DRIVER, so
# the fixture follows the driver's registered dependency rather than a path typed
# into a test.  THE SYNTHETIC NEGATIVES ABOVE ARE KEPT AND NONE IS WEAKENED: they
# drive refusal branches that a real artefact, which passes, can never reach.
# WHAT IS NEW IS THAT THE **PASS** IS NOW PAID FOR BY A REAL PRODUCER'S BYTES.
# =========================================================================
SO1B_REAL=$(grep -oP '(?<=^SO1B_BASE=)\S+' "$DRIVER")
REALG=$(ls -1 "$SO1B_REAL"/SO1bR_grade_*.json 2>/dev/null | head -1)
realfix() { # realfix <destdir> -- COPY the producer's artefacts; author nothing
  rm -rf "$1" || return 4
  mkdir -p "$1/O-P" "$1/O-S" "$1/E-P" "$1/E-S" || return 4
  cp -a "$REALG" "$1/" || return 4
  for d in O-P O-S; do cp -a "$SO1B_REAL/$d/so1b_O.json" "$1/$d/so1b_O.json" || return 4; done
  for d in E-P E-S; do cp -a "$SO1B_REAL/$d/so1b_E.json" "$1/$d/so1b_E.json" || return 4; done
  return 0
}
if [ -n "$SO1B_REAL" ] && [ -n "$REALG" ] && [ -f "$SO1B_REAL/E-P/so1b_E.json" ] && [ -f "$SO1B_REAL/O-P/so1b_O.json" ]; then
  RF="$TMP/so1b_real"; realfix "$RF"; RG="$RF/$(basename "$REALG")"

  leg "(e8) THE REAL PRODUCER ARTEFACT -- COPIED FROM $SO1B_REAL, NEVER AUTHORED HERE -- through the driver's OWN extracted gate -> PROCEED rc=0.  THIS IS THE LEG R7 DID NOT HAVE: against the frozen driver it refuses rc=7 twice over, first on the top-level gates read (break 5) and then on the row label (break 6)" 0 "$(gso1b_at "$RG" "$RF")"
  grep -q "gates_at=grade.gates" "$TMP/e.out"
  legc "(e8b) ... and the gate RECORDS WHICH REGISTERED LOCATION it read the gates from (gates_at=grade.gates).  A relocation that is not recorded is indistinguishable from a search, and the difference is the whole check" $?

  # (e9) FAIL-CLOSED.  R8 RELOCATED THE READ; IT DID NOT MAKE IT OPTIONAL.
  python3 - "$RG" "$RF/nogates.json" <<'PY'
import json, sys
g = json.load(open(sys.argv[1]))
g.pop("gates", None)
(g.get("grade") or {}).pop("gates", None)
json.dump(g, open(sys.argv[2], "w"))
PY
  leg "(e9) FAIL-CLOSED, DRIVEN ON THE REAL ARTEFACT: the gates mapping DELETED at BOTH registered locations -> REFUSED rc=7.  A relocated read that stopped refusing on genuine absence would have turned a red gate green by removing the gate" 7 "$(gso1b_at "$RF/nogates.json" "$RF")"
  grep -q "NO gates mapping at either REGISTERED location" "$TMP/e.out"
  legc "(e9b) ... AND IT REFUSED FOR ITS OWN REASON.  The rc alone does not discriminate: the FROZEN driver also returns 7 here, on the top-level miss that IS break 5.  A control that passes for the wrong reason is not a control, so the refusal's stated reason is asserted, not just its code" $?

  # (e10) THE LOCATIONS ARE NAMED, NOT HUNTED FOR.
  python3 - "$RG" "$RF/wrongloc.json" <<'PY'
import json, sys
g = json.load(open(sys.argv[1]))
gt = (g.get("grade") or {}).pop("gates")
g.pop("gates", None)
g["results"] = {"gates": gt}
json.dump(g, open(sys.argv[2], "w"))
PY
  leg "(e10) THE TWO LOCATIONS ARE REGISTERED, NOT SEARCHED FOR: the SAME gates mapping, every verdict intact, moved to an UNREGISTERED location (results.gates) -> REFUSED rc=7.  A read that hunts until it finds something always finds something, and would have 'repaired' break 5 by deleting the check" 7 "$(gso1b_at "$RF/wrongloc.json" "$RF")"
  grep -q "NO gates mapping at either REGISTERED location" "$TMP/e.out"
  legc "(e10b) ... AND IT REFUSED FOR ITS OWN REASON: the refusal names the registered locations it looked in and did not find them, rather than falling through to the old top-level miss" $?

  # (e11) THE SWAP.  R8's REGISTERED ACCEPTANCE CONDITION.
  cp -a "$RF/E-S/so1b_E.json" "$RF/E-P/so1b_E.json"
  leg "(e11) THE SWAPPED ARTEFACT, AND THE ACCEPTANCE CONDITION OF AMENDMENT R8: the SHIPPED row's REAL E artefact placed in E-P -> STILL REFUSED rc=7.  The row-label assertion exists to catch an artefact sitting in the WRONG DIRECTORY, and R8's mapping keeps it doing that because the two rows' registered label sets are DISJOINT" 7 "$(gso1b_at "$RG" "$RF")"
  grep -q "labelled row='S'" "$TMP/e.out"
  legc "(e11b) ... and the refusal NAMES THE OFFENDING LABEL IT ACTUALLY FOUND (row='S' sitting in the PATCHED directory) -- a refusal that does not say what it saw is not a finding" $?
  realfix "$RF"

  # (e12) AND THE SWAP IN THE OTHER DIRECTION.
  cp -a "$RF/E-P/so1b_E.json" "$RF/E-S/so1b_E.json"
  leg "(e12) ... and the SWAP IN THE OTHER DIRECTION: the PATCHED row's REAL E artefact placed in E-S -> STILL REFUSED rc=7.  Both directions are driven because a mapping that is disjoint in one direction only is not disjoint" 7 "$(gso1b_at "$RG" "$RF")"
  realfix "$RF"

  # (e13) THE MAPPING IS EXPLICIT, NOT DERIVED FROM THE FIRST LETTER.
  N=$((N+1))
  if grep -q 'ROW_LABELS = {"PATCHED": ("PATCHED", "P"), "SHIPPED": ("SHIPPED", "S")}' "$DRIVER" \
     && ! grep -n 'row\[0\]' "$DRIVER" | grep -qv ':[[:space:]]*#'; then
    echo "  [OK ] (e13) THE ROW-LABEL MAPPING IS WRITTEN OUT IN FULL and NO executable line derives it as row[0].  row[0] agrees with the producer only by the coincidence that PATCHED and SHIPPED share first letters with P and S; a check that is true by coincidence has stopped being a check, and it would silently accept a row named 'PORPOISE' in the PATCHED directory"
  else
    echo "  [BAD] (e13) the row-label mapping is not the registered explicit form, or an executable line derives it as row[0]"; FAIL=$((FAIL+1))
  fi
else
  cat <<'NOREAL'
  [NOT DRIVEN] (e8-e13) THE REAL-PRODUCER FIXTURE LEGS.  SO-1b's run root, or its
      grade / O / E artefacts, are not on this box, so the producer-anchored
      positive path cannot be driven.  NOT COUNTED AS PASSING -- N is not
      incremented.  The synthetic legs (e1-e7) above still ran, and they are
      exactly the legs that were 51/0 while breaks 5 and 6 were live.
NOREAL
fi

# ------------------------------------------- AMENDMENT R6: THE TWO SELECTION SITES
# Both blocks are EXTRACTED VERBATIM from the frozen driver between their own
# markers and executed -- never re-implemented here.  A guard suite that runs its
# own copy of the code proves nothing about the code that ships.
selblk() { sed -n "/^ *# >>> $1/,/^ *# <<< $1/p" "$DRIVER" > "$2"; }
runsel() { ( set -uo pipefail; SO1B_BASE="$2"; BASE="$3"; . "$1" ) >"$TMP/sel.out" 2>&1; echo $?; }

selblk G-SO1B-SELECT "$TMP/sel_grade.sh"
N=$((N+1))
if [ -s "$TMP/sel_grade.sh" ] && grep -q 'SO1B_GRADE_CANDS' "$TMP/sel_grade.sh"; then
  echo "  [OK ] (h0) the G-SO1B-SELECT block EXTRACTS from the frozen driver (a suite that runs its own copy of the code proves nothing about the code that ships)"
else
  echo "  [BAD] (h0) the G-SO1B-SELECT block did not extract"; FAIL=$((FAIL+1))
fi

mkdir -p "$TMP/gsel0" "$TMP/gsel1" "$TMP/gsel2" "$TMP/gbase"
leg "(h1) G-SO1B-SELECT: ZERO SO1bR_grade_*.json -> BLOCKED rc=7 (the frozen v1.0 branch, unchanged)" 7 "$(runsel "$TMP/sel_grade.sh" "$TMP/gsel0" "$TMP/gbase/x")"
grep -q "reason=no_grade" "$TMP/gbase/x.STATUS.preflight" 2>/dev/null
legc "(h1b) ... and the status line still reads reason=no_grade -- the pre-existing no-launch branch is byte-preserved" $?
: > "$TMP/gsel1/SO1bR_grade_20260828T000000Z.json"
RC1=$(runsel "$TMP/sel_grade.sh" "$TMP/gsel1" "$TMP/gbase/y"); OUT1=$(cat "$TMP/sel.out")
leg "(h2) G-SO1B-SELECT: EXACTLY ONE grade artefact -> PROCEED rc=0" 0 "$RC1"
case "$OUT1" in *"G_SO1B_GRADE_SELECTED file=$TMP/gsel1/SO1bR_grade_20260828T000000Z.json n_candidates=1"*) legc "(h2b) ... and THE SELECTION IS RECORDED: the chosen file and the candidate count are printed, not implied" 0 ;;
  *) legc "(h2b) ... and THE SELECTION IS RECORDED: the chosen file and the candidate count are printed, not implied" 1 ;; esac
: > "$TMP/gsel2/SO1bR_grade_20260828T000000Z.json"; : > "$TMP/gsel2/SO1bR_grade_20260828T010000Z.json"
RC2=$(runsel "$TMP/sel_grade.sh" "$TMP/gsel2" "$TMP/gbase/z"); OUT2=$(cat "$TMP/sel.out")
leg "(h3) THE R5 DEFECT, DRIVEN: TWO grade artefacts -> REFUSED rc=7.  The frozen v1.0 form was \`ls -1t ... | head -1\`, which would have SILENTLY TAKEN THE NEWER ONE by mtime" 7 "$RC2"
N=$((N+1))
if echo "$OUT2" | grep -q "SO1bR_grade_20260828T000000Z.json" && echo "$OUT2" | grep -q "SO1bR_grade_20260828T010000Z.json" && grep -q "reason=grade_selection_ambiguous" "$TMP/gbase/z.STATUS.preflight" 2>/dev/null; then
  echo "  [OK ] (h3b) ... naming BOTH candidates and recording reason=grade_selection_ambiguous -- a refusal that does not say what it could not choose between is not a finding"
else
  echo "  [BAD] (h3b) ... naming BOTH candidates and recording reason=grade_selection_ambiguous"; FAIL=$((FAIL+1))
fi

selblk G-MESHREF-SELECT "$TMP/sel_mesh.sh"
SHA_A=$(printf 'a%.0s' $(seq 64)); SHA_B=$(printf 'b%.0s' $(seq 64))
mkmesh() { # mkmesh <dir> <nfiles> <nsha>
  rm -rf "$1"; mkdir -p "$1"; local i j
  for i in $(seq 1 "$2"); do
    : > "$1/MESH_2026082${i}T000000Z_$i.log"
    for j in $(seq 1 "$3"); do echo "${SHA_A}  constant/polyMesh/points" >> "$1/MESH_2026082${i}T000000Z_$i.log"; done
  done
}
mb() { rm -rf "$TMP/mb"; mkdir -p "$TMP/mb/optref"; echo "$TMP/mb"; }
mkmesh "$TMP/m1" 1 1; B=$(mb)
RC4=$(runsel "$TMP/sel_mesh.sh" "$TMP/m1" "$B"); OUT4=$(cat "$TMP/sel.out")
leg "(h4) G-MESHREF-SELECT: ONE MESH_*.log carrying ONE points-sha256 -> PROCEED rc=0" 0 "$RC4"
N=$((N+1))
if [ "$(cat "$B/optref/so1b_mesh_points_sha256.txt" 2>/dev/null)" = "${SHA_A}  constant/polyMesh/points" ] && grep -q "G_MESHREF_SELECTED file=$TMP/m1/MESH_20260821T000000Z_1.log n_candidates=1 sha_lines=1" "$B/optref/so1b_mesh_points_sha256.SELECTION.txt" 2>/dev/null; then
  echo "  [OK ] (h4b) ... the reference is the ONE sha from the ONE NAMED file, and the SELECTION RECORD beside it names that file and the candidate count"
else
  echo "  [BAD] (h4b) ... the reference is the ONE sha from the ONE NAMED file, and the SELECTION RECORD beside it names that file"; FAIL=$((FAIL+1))
fi
mkmesh "$TMP/m2" 2 1; B=$(mb)
RC5=$(runsel "$TMP/sel_mesh.sh" "$TMP/m2" "$B"); OUT5=$(cat "$TMP/sel.out")
leg "(h5) THE R1 DEFECT, DRIVEN: TWO MESH_*.log in SO-1b's root -> REFUSED rc=4.  The frozen v1.0 form was a MULTI-FILE \`grep ... | head -4\`, and under ugrep multi-file output order is a RACE" 4 "$RC5"
N=$((N+1))
if echo "$OUT5" | grep -q "MESH_20260821T000000Z_1.log" && echo "$OUT5" | grep -q "MESH_20260822T000000Z_2.log" && [ ! -s "$B/optref/so1b_mesh_points_sha256.txt" ]; then
  echo "  [OK ] (h5b) ... naming BOTH candidates, and NO reference file is written -- the ambiguous read never reaches disk"
else
  echo "  [BAD] (h5b) ... naming BOTH candidates, and NO reference file is written"; FAIL=$((FAIL+1))
fi
mkmesh "$TMP/m3" 1 0; B=$(mb)
leg "(h6) G-MESHREF-SELECT: ONE MESH_*.log carrying ZERO points-sha256 lines -> REFUSED rc=4 (a reference that names no mesh is not a reference)" 4 "$(runsel "$TMP/sel_mesh.sh" "$TMP/m3" "$B")"
mkmesh "$TMP/m4" 1 2; B=$(mb)
leg "(h7) G-MESHREF-SELECT: ONE MESH_*.log carrying TWO points-sha256 lines -> REFUSED rc=4.  This is the input that used to reach the GRADER and publish as a MESH-REGENERATION-DETERMINISM finding" 4 "$(runsel "$TMP/sel_mesh.sh" "$TMP/m4" "$B")"

# THE DEFECT SHAPE IS GONE FROM EXECUTABLE LINES -- and the pattern is PROVEN ON A
# KNOWN POSITIVE FIRST.  A sweep that returns zero on ground truth it has never
# been shown to see is measuring its own regex, not the code.
N=$((N+1))
PROBE=$(printf 'a=$(ls -1t foo | head -1)\nb=$(grep z bar | head -4)\n' | grep -cE 'ls -1t|head -4')
RESID=$(grep -nE 'ls -1t|head -4' "$DRIVER" | grep -vc ':[[:space:]]*#')
if [ "$PROBE" = "2" ] && [ "$RESID" = "0" ]; then
  echo "  [OK ] (h8) NO EXECUTABLE line of the driver still selects with \`ls -1t\` or \`head -4\` (residue=$RESID), and the sweep pattern was PROVEN on a planted known positive first (probe=$PROBE of 2)"
else
  echo "  [BAD] (h8) selection-defect residue=$RESID on executable lines, probe=$PROBE (want 0 and 2)"; FAIL=$((FAIL+1))
fi

# ---------------------------------------------------------------- instrument
python3 "$HERE/so1c_xn.py" -mode F -optimum /dev/null >"$TMP/f1.out" 2>&1
leg "(f1) the instrument refuses an unregistered mode -> rc=64" 64 $?
python3 "$HERE/so1c_xn.py" -mode N >"$TMP/f2.out" 2>&1
leg "(f2) the instrument refuses with no -optimum path -> rc=64" 64 $?
grep -q "REGISTERED_NPROCS = 4" "$HERE/so1c_xn.py"
legc "(f3) the instrument cross-asserts nprocs against MPI AND against the dictionary" $?
grep -q "G-ROWX" "$HERE/so1c_xn.py"
legc "(f4) the instrument refuses an optimum artefact whose libidwarp md5 is another row's" $?

# ---------------------------------------------------------------- THE NOT-DRIVEN LEG
# DELIBERATELY NOT COUNTED: `N` is not incremented here.  A leg that was not
# driven must never inflate a pass count.
cat <<'NOTDRIVEN'
  [NOT DRIVEN] (a0+) G-ROOT.5 leg (a) POSITIVE side -- "a RUNNING container already
      carries this item's prefix and arm".  Driving it requires CREATING a container,
      and this registration is made under an explicit ZERO-CONTAINERS-CREATED
      instruction.  IT IS NOT COUNTED AS PASSING.  Its NEGATIVE side is driven above
      (no so1c_ container exists, and the guard passes).  The one-line command that
      drives the positive side, for the supervisor to run BEFORE first compute:
        sudo -n docker run -d --name so1c_Ns-P_selftest --cpus=0.1 --cpuset-cpus=15 \
             --memory=64m alpine sleep 30 >/dev/null && \
        BASE=/home/ubuntu/certonomous-runs/CURRICULUM-SO1c-a1-naca0012-dragmin-npinv \
             bash so1c_run_arm.sh Ns-P dafoam-idwarp-rot:v1 ; echo rc=$? ; \
        sudo -n docker rm -f so1c_Ns-P_selftest
      EXPECTED: rc=3, "ABORT G-ROOT.5 a RUNNING container already carries this item's
      prefix and arm".
NOTDRIVEN

echo
LIVE_SO1C=$(sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep -c "^so1c_")
echo "(a0) NEGATIVE side of G-ROOT.5 leg (a): so1c_ containers RUNNING = $LIVE_SO1C (expected 0)"
CONTAINERS_AFTER=$(sudo -n docker ps -a -q 2>/dev/null | wc -l)
echo "containers on the box AFTER: $CONTAINERS_AFTER (BEFORE was $CONTAINERS_BEFORE)"
echo "run root ABSENT after the test (freeze condition): $(test -e "$REG_BASE" && echo NO || echo YES)"
if [ "$CONTAINERS_AFTER" != "$CONTAINERS_BEFORE" ]; then
  echo "  [BAD] THIS SUITE CREATED OR REMOVED A CONTAINER"; FAIL=$((FAIL+1))
fi
rm -rf "$TMP"
echo
echo "SO1c guard selftest: $N legs driven, $FAIL fail, 1 leg NOT DRIVEN and named (never counted)"
exit $([ "$FAIL" -eq 0 ] && echo 0 || echo 1)
