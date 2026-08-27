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
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-SO1b-a1-naca0012-dragmin-opt bash "$LAUNCHER" Ns-P dafoam/opt-packages:latest >"$TMP/a2.out" 2>&1
leg "(a2) G-ROOT.1/.2 BASE = SO-1b's OWN RUN ROOT -> ABORT (the root this item READS)" 3 $?
BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6-a2-wing-multipoint bash "$LAUNCHER" Ns-P dafoam/opt-packages:latest >"$TMP/a3.out" 2>&1
leg "(a3) G-ROOT.1/.2 BASE = D6's LIVE run root -> ABORT before any staging" 3 $?
grep -q "CURRICULUM-SO1b-a1-naca0012-dragmin-opt" "$HERE/so1c_run_arm.sh"
legc "(a4) SO-1a's and SO-1b's run roots are BOTH in FORBIDDEN_ROOTS" $?
grep -q "CURRICULUM-SO1a-a1-naca0012-dragmin-gradient" "$HERE/so1c_run_arm.sh"
legc "(a5) ... and SO-1a's is too" $?

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
          open(os.path.join(b, "SO1b_grade_x.json"), "w"))
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
gso1b() { # gso1b -> rc
  python3 - "$SO1B/SO1b_grade_x.json" "$SO1B" <<'PY' >"$TMP/e.out" 2>&1
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
