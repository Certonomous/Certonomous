#!/usr/bin/env bash
# =============================================================================
# SO-3 CHAIN-DRIVER SELFTEST.  Every leg DRIVEN.  Nothing launches.
#
# The chain driver has no `--source-only`: its first executable line after the
# constants is a dependency assertion, and every guard below it is destructive
# or long-running.  So this file DRIVES it in the only two ways that are safe
# and are also the two that matter:
#
#   (c1)-(c6) STATIC: parse the driver's own bytes and cross-check them against
#             the launcher's and the comparator's registered tables.  Three
#             files carry the arm->row mapping and SO-1c DIED AT ITS SECOND ARM
#             because one of three call sites was repaired.  Agreement between
#             them is the check that would have caught it.
#   (c7)-(c9) EXECUTED: run the driver in a sandbox where its dependency and
#             md5 assertions FIRE, and demand each refusal BY NAME with its
#             registered rc.  A guard that has never fired is not evidence.
#
# THE FENCE ON THE EXECUTED LEGS, AND THE INCIDENT THAT REWROTE IT.
#
# The first version of this file said, in this comment: *"every leg aborts before
# `mkdir -p "$BASE"`"*.  THAT SENTENCE WAS TRUE WHEN IT WAS WRITTEN AND BECAME
# FALSE ONE COMMAND LATER.  It was written while every md5 pin in the chain
# driver still held the fail-closed sentinel, so leg (c8) aborted at the md5 gate
# above the staging.  `so3_repin.sh` then SET the pins, and the SAME LEG,
# UNCHANGED, sailed past that gate, staged the real run root at
# `/home/ubuntu/certonomous-runs/CURRICULUM-SO3-...-optimisation` and RAN THE
# MESH ARM INSIDE THE SHIPPED CONTAINER -- rc=0, 10 s wall, 0.167 core-min
# MEASURED, no solver.  The output was quarantined, not deleted, at
# `QUARANTINE-SO3-selftest-accidental-launch-20260901T0242Z`.
#
# A CLAIM ABOUT BEHAVIOUR THAT IS NOT RE-CHECKED AFTER THE THING IT DESCRIBES
# CHANGES IS THE FAILURE THIS ENTIRE ITEM IS BUILT TO CATCH, and this lane
# committed it in its own test file.  So the fence is now TWO INDEPENDENT
# MECHANISMS, NEITHER OF WHICH DEPENDS ON THE PINS BEING UNSET, and leg (c0)
# ASSERTS BOTH BEFORE ANY LEG EXECUTES THE DRIVER:
#
#   FENCE 1  `BASE=` is REWRITTEN in every sandbox copy to point inside the temp
#            directory.  Even a driver that ran to completion could not address
#            the real run root.  Asserted by reading the sandbox copy back.
#   FENCE 2  a pinned dependency is deliberately MUTATED in each sandbox, so the
#            md5 assertion fires at rc=4 whatever the pins hold.  That is also
#            what makes the refusal a REAL drive rather than an artefact of an
#            unset table -- the original leg proved only that a sentinel refuses.
#
# Neither fence is trusted on its own and neither is described without being
# driven.  Nothing here launches a container.
# =============================================================================
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
DRIVER="$HERE/so3_chain_driver.sh"
LAUNCHER="$HERE/so3_run_arm.sh"
GRADER="$HERE/so3_grade.py"
test -f "$DRIVER" || { echo "ABORT driver absent: $DRIVER"; exit 2; }

PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); printf '  [OK ] %s\n' "$1"; }
bad() { FAIL=$((FAIL+1)); printf '  [FAIL] %s\n' "$1"; }
chk() { if [ "$2" = "$3" ]; then ok "$1 ($2)"; else bad "$1: got [$2] want [$3]"; fi; }

DECLARED="MESH O-S XE-S FE-S O-P XE-P FE-P"
TMP=$(mktemp -d "${TMPDIR:-/tmp}/so3_chain_selftest_XXXXXX")
trap 'rm -rf "$TMP"' EXIT

echo "SO-3 CHAIN-DRIVER SELFTEST"

echo
echo "(c1) THE DECLARED COUNT AND THE ARM SET AGREE ACROSS THE THREE FILES"
echo "     THAT CARRY THEM.  SO-1c died at its second arm because SO-1bR"
echo "     labelled its per-row artefacts one way and SO-1c's consumers"
echo "     compared against another, and an amendment repaired ONE of THREE"
echo "     call sites.  CLAUDE.md rule 14: a lesson is not applied until EVERY"
echo "     call site asserts it."
DN=$(grep -aoE '^DECLARED_ARMS=[0-9]+' "$DRIVER" | head -1 | cut -d= -f2)
chk "(c1) the driver declares" "$DN" "7"
GN=$(python3 -c "
import sys; sys.path.insert(0,'$HERE')
import so3_grade as G; print(G.N_DECLARED)" 2>/dev/null)
chk "(c1) the comparator declares" "$GN" "7"
GARMS=$(python3 -c "
import sys; sys.path.insert(0,'$HERE')
import so3_grade as G; print(' '.join(G.ARMS_DECLARED))" 2>/dev/null)
chk "(c1) the comparator's arm list" "$GARMS" "$DECLARED"

echo
echo "(c2) THE ARM -> ROW MAPPING IS THE SAME IN ALL THREE FILES."
# shellcheck disable=SC1090
. "$LAUNCHER" --source-only
for A in $DECLARED; do
  DROW=$(sed -n '/^row_of_arm() {/,/^}/p' "$DRIVER" \
         | grep -aE "^ *$A\)" | awk '{print $3}' | head -1)
  LROW=$(row_of "$A")
  GROW=$(python3 -c "
import sys; sys.path.insert(0,'$HERE')
import so3_grade as G; print(G.ARM_ROW.get('$A',''))" 2>/dev/null)
  if [ "$DROW" = "$LROW" ] && [ "$LROW" = "$GROW" ] && [ -n "$LROW" ]; then
    ok "(c2) $A -> $LROW in driver, launcher AND comparator"
  else
    bad "(c2) $A disagrees: driver=[$DROW] launcher=[$LROW] comparator=[$GROW]"
  fi
done
# THE UNDECLARED ARM.  `Q-S` would have matched a `*-S` suffix glob and been
# handed the SHIPPED image.  It must fall through to empty in the driver too.
QROW=$(sed -n '/^row_of_arm() {/,/^}/p' "$DRIVER" | grep -acE "^ *Q-S\)" || true)
chk "(c2) undeclared arm Q-S has no row in the driver" "${QROW:-0}" "0"

echo
echo "(c3) BOTH ROWS RUN, AND THE IMAGES ARE PINNED BY DIGEST, NEVER BY TAG."
NS=0; NP=0
for A in $DECLARED; do
  case "$(row_of "$A")" in SHIPPED) NS=$((NS+1));; PATCHED) NP=$((NP+1));; esac
done
if [ "$NS" -ge 3 ] && [ "$NP" -ge 3 ]; then
  ok "(c3) $NS SHIPPED arms and $NP PATCHED arms -- the two-row verdict DAFOAM section 6 demands"
else
  bad "(c3) the program is not two-rowed: SHIPPED=$NS PATCHED=$NP"
fi
if grep -aq 'IMG_PATCHED_DIGEST=sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35' "$LAUNCHER" \
   && grep -aq 'IMG_SHIPPED_DIGEST=sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc' "$LAUNCHER"; then
  ok "(c3) both image digests are pinned in the launcher and match SO-3aR2's G9"
else
  bad "(c3) an image digest is missing or has drifted from SO-3aR2's G9"
fi
if grep -aq 'D4S_IDWARP_SO_MD5' "$LAUNCHER"; then
  ok "(c3) the launcher prints libidwarp.so's md5 FROM INSIDE the container -- the bytes, not the tag"
else
  bad "(c3) the launcher does not read the library md5 inside the container"
fi

echo
echo "(c4) THE DEPENDENCY LIST COVERS EVERY FILE THE CHAIN EXECUTES OR IMPORTS."
echo "     DAFOAM section 18.3.  SO-2a read *eight of eight AGREE* while a file"
echo "     its own driver executed was ABSENT, and the chain sat on a guaranteed"
echo "     no-launch branch for four hours.  Existence is a DIFFERENT question"
echo "     from md5 agreement and cannot be inferred from any level of it."
# FOUR OF THE NINE DEPENDENCIES ARE NAMED THROUGH SHELL VARIABLES ($LAUNCHER,
# $GRADER, $AGG_SCRIPT, $STOP_MARKER), so a grep for the FILENAME cannot see
# them and the first draft of this leg reported all four as missing.  A check
# that cannot see half its subject reports the subject as absent -- which is the
# SO-1b "guard pinned to a name that moved" failure in a test file.  The
# variables are resolved from the driver's OWN assignments so the leg reads the
# same binding the driver executes.
DEPBLOCK=$(sed -n '/^for _dep in/,/^done$/p' "$DRIVER")
resolve_dep() {   # $1 = filename -> the token the driver actually writes
  V=$(grep -aoE "^[A-Z_]+=\"?\\\$HERE/$1\"?$|^[A-Z_]+=\"\\\$HERE/$1\"" "$DRIVER" | head -1 | cut -d= -f1)
  [ -n "$V" ] && { printf '$%s' "$V"; return; }
  printf '%s' "$1"
}
for F in so3_run_arm.sh so3_grade.py so3_aggregate_memory.py so3_stop_marker.sh \
         so3_runScript.py so3_xf.py so3_decomposeParDict so3_stall.py so3_age_guard.py; do
  TOK=$(resolve_dep "$F")
  if printf '%s' "$DEPBLOCK" | grep -aqF "$TOK"; then
    if [ -f "$HERE/$F" ]; then ok "(c4) $F (as $TOK) is asserted-before-md5 AND exists on disk"
    else bad "(c4) $F is asserted by the driver but DOES NOT EXIST"; fi
  else
    bad "(c4) $F is executed or imported by this item but is NOT in the dependency assertion"
  fi
done
DEPN=$(grep -aoE 'SO3_DEPS_EXIST n=[0-9]+' "$DRIVER" | head -1 | grep -aoE '[0-9]+$')
DEPC=$(printf '%s' "$DEPBLOCK" | grep -aoE '"\$(LAUNCHER|GRADER|AGG_SCRIPT|STOP_MARKER)"|so3_[a-zA-Z_]+\.(py|sh)|so3_decomposeParDict' | sort -u | wc -l)
chk "(c4) the printed dependency count matches the list it printed for" "$DEPN" "$DEPC"

echo
echo "(c5) NO SUCCESS-READING TOKEN OVER A TRUNCATED PROGRAM."
echo "     W3 printed PHASE1_COMPLETE unconditionally over 20 blocked stages and"
echo "     that token misled a triage."
if grep -aq 'if \[ "\$CHAIN_RC" -eq 0 \] && \[ "\$EXECUTED" -eq "\$DECLARED_ARMS" \]; then' "$DRIVER"; then
  ok "(c5) COMPLETE is written ONLY on rc=0 AND executed == declared"
else
  bad "(c5) the COMPLETE branch is not guarded on both conditions"
fi
for T in 'chain=BLOCKED ' 'chain=NOT A RESULT '; do
  if grep -aq "$T" "$DRIVER"; then ok "(c5) a shortfall writes a rule-1 token: [$T]"
  else bad "(c5) no rule-1 token for the shortfall branch [$T]"; fi
done
BADTOK=$(grep -acE 'chain=(SUCCESS|OK|DONE|FINISHED|PHASE[0-9]*_COMPLETE)' "$DRIVER" || true)
chk "(c5) no soft success synonym anywhere in the driver" "${BADTOK:-0}" "0"

echo
echo "(c6) THE STOP MARKER LANDS ON EVERY EXIT PATH, AT ONE FIXED ADDRESS."
SM=$(grep -acE '^bash "\$STOP_MARKER"' "$DRIVER" || true)
chk "(c6) exactly one stop-marker call site" "${SM:-0}" "1"
if grep -aq 'SO3_STOP_MARKER_FAILED' "$DRIVER"; then
  ok "(c6) a marker that did NOT land says so -- the successor is told it has no fixed address"
else
  bad "(c6) a failed stop marker is silent"
fi

echo
echo "(c0) THE FENCE ON EVERY EXECUTED LEG, ASSERTED BEFORE ANY LEG RUNS."
echo "     Two independent mechanisms, neither depending on the pins being"
echo "     unset.  See the incident in this file's header."
REAL_BASE=$(grep -aoE '^BASE=\S+' "$DRIVER" | head -1 | cut -d= -f2)
sandbox() {   # $1 = destination -- copies the item in and REPOINTS BASE
  local D="$1"
  cp -a "$DRIVER" "$D/so3_chain_driver.sh"
  local F
  for F in so3_run_arm.sh so3_grade.py so3_aggregate_memory.py so3_stop_marker.sh \
           so3_runScript.py so3_xf.py so3_decomposeParDict so3_stall.py so3_age_guard.py; do
    cp -a "$HERE/$F" "$D/$F" 2>/dev/null
  done
  # FENCE 1: the sandbox driver addresses a run root INSIDE the temp directory.
  sed -i -E "s#^BASE=.*#BASE=$D/RUNROOT#" "$D/so3_chain_driver.sh"
}
SBF="$TMP/fence"; mkdir -p "$SBF"; sandbox "$SBF"
SB_BASE=$(grep -aoE '^BASE=\S+' "$SBF/so3_chain_driver.sh" | head -1 | cut -d= -f2)
if [ "$SB_BASE" = "$REAL_BASE" ]; then
  bad "(c0) FENCE 1 FAILED: the sandbox driver still addresses the REAL run root [$SB_BASE].  NO EXECUTED LEG MAY RUN."
  echo "DRIVE aborted at the fence"; exit 1
fi
case "$SB_BASE" in
  "$TMP"/*) ok "(c0) FENCE 1: the sandbox driver addresses [$SB_BASE], inside the temp dir, NOT [$REAL_BASE]" ;;
  *) bad "(c0) FENCE 1 FAILED: sandbox BASE [$SB_BASE] is outside the temp dir"; exit 1 ;;
esac
if [ -e "$REAL_BASE" ]; then
  bad "(c0) THE REAL RUN ROOT ALREADY EXISTS at [$REAL_BASE] -- this item has not run and a pre-existing root is what its own cold-start guard refuses"
else
  ok "(c0) the real run root [$REAL_BASE] does NOT exist before this suite, and leg (c8) asserts it still does not afterwards"
fi

echo
echo "(c7) EXECUTED: THE DEPENDENCY REFUSAL FIRES, BY NAME, AT rc=4."
echo "     Driven in a sandbox with a deliberately missing neighbour.  Nothing"
echo "     reaches a run root: the abort is above every mkdir."
SB="$TMP/deps"; mkdir -p "$SB"
sandbox "$SB"
rm -f "$SB/so3_age_guard.py"   # deliberately ABSENT
OUT=$(cd "$SB" && bash ./so3_chain_driver.sh MESH 2>&1); RC=$?
if [ "$RC" -eq 4 ] && printf '%s' "$OUT" | grep -aq 'dependency ABSENT before any md5.*so3_age_guard.py'; then
  ok "(c7) rc=4 and the refusal NAMES the absent file (so3_age_guard.py)"
else
  bad "(c7) expected rc=4 naming so3_age_guard.py; got rc=$RC out=[$(printf '%s' "$OUT" | head -2 | tr '\n' ' ')]"
fi

echo
echo "(c8) EXECUTED: THE md5 REFUSAL FIRES, BY NAME, AT rc=4, ON A PINNED"
echo "     DEPENDENCY THAT WAS MUTATED.  A stale pin aborts the chain BEFORE any"
echo "     container -- the W3 death mode -- and that is the intended cost of"
echo "     freezing.  SO-2M lost its FIRST ARM to the opposite choice: three md5"
echo "     pins inherited through an item-token rename were stale the instant the"
echo "     rename ran, and they LOOKED like pins."
SB2="$TMP/md5"; mkdir -p "$SB2"
sandbox "$SB2"
# THE MUTATION.  One pinned dependency's bytes are changed, so the driver's own
# md5 assertion MUST fire -- whether the pins are sentinels or real.  The
# original form of this leg relied on the pins being UNSET and therefore stopped
# working, silently and dangerously, the moment they were set.
printf '\n# selftest mutation -- so3_chain_driver_selftest.sh (c8)\n' >> "$SB2/so3_stall.py"
OUT=$(cd "$SB2" && bash ./so3_chain_driver.sh MESH 2>&1); RC=$?
if [ "$RC" -eq 4 ] && printf '%s' "$OUT" | grep -aq 'md5 drifted or UNSET'; then
  ok "(c8) rc=4 on a MUTATED pinned dependency -- FAIL CLOSED, and the message names the drift"
else
  bad "(c8) expected rc=4 at the md5 assertion; got rc=$RC out=[$(printf '%s' "$OUT" | tail -2 | tr '\n' ' ')]"
fi
# AND THE POSITIVE HALF: the SAME sandbox, UNMUTATED, must get PAST the md5 gate.
# Without this the leg above could be passing because the sandbox is broken in
# some unrelated way, and a refusal from the wrong cause is not a drive.
SB2b="$TMP/md5ok"; mkdir -p "$SB2b"
sandbox "$SB2b"
OUT=$(cd "$SB2b" && bash ./so3_chain_driver.sh Q-UNDECLARED 2>&1); RC=$?
if printf '%s' "$OUT" | grep -aq 'md5 drifted or UNSET'; then
  bad "(c8) the UNMUTATED sandbox also failed the md5 gate -- the red leg above proves nothing"
else
  ok "(c8) the UNMUTATED sandbox PASSES the md5 gate (it then refuses the undeclared arm, rc=$RC) -- so the red leg is a reading of the mutation"
fi
# THE FAIL-CLOSED SENTINEL'S SHAPE, read from the DERIVATION SCRIPT where it is
# defined.  The first form of this leg read the chain driver's FIRST `^MD5_*=`
# line and called it "the sentinel" -- which was true only while the table was
# unset, and after re-pinning it read a real md5 and reported it as a fail-open.
# A check that reads a different thing depending on when it runs is not a check.
SENT=$(grep -aoE "^SENT='[^']+'" "$HERE/so3_derive_from_so3ar2.sh" | head -1 | cut -d"'" -f2)
if [ -z "$SENT" ]; then
  bad "(c8) the derivation script defines no sentinel constant to check"
elif printf '%s' "$SENT" | grep -aqE '^[0-9a-f]{32}$'; then
  bad "(c8) the sentinel [$SENT] has the SHAPE of an md5 -- it is a fail-open one edit away"
else
  ok "(c8) the sentinel [$SENT] CANNOT be an md5, so md5sum -c fails closed"
fi
NSENT=$(grep -acF "$SENT" "$HERE/so3_chain_driver.sh" "$HERE/so3_run_arm.sh" "$HERE/so3_xf.py" 2>/dev/null | awk -F: '{n+=$2} END{print n+0}')
chk "(c8) and no sentinel survives after re-pinning" "$NSENT" "0"

echo "(c9) EXECUTED: AN UNDECLARED ARM NAMES NO ROW AND THE CHAIN REFUSES."
SB3="$TMP/arm"; mkdir -p "$SB3"
sed -e 's/^MD5_\([A-Z_]*\)=UNSET-PIN-SET-AFTER-THE-LAST-EDIT-FAILS-CLOSED/MD5_\1=SKIP/' \
    "$DRIVER" > "$SB3/so3_chain_driver.sh"
# The md5 lines are left intact; this leg only needs the ARM check, which sits
# AFTER them, so it is driven by asking the row function directly out of the
# driver's own bytes rather than by running past a guard that must not be
# weakened.  A leg that disabled a guard to reach a later one would be testing a
# file nobody runs.
Q=$(bash -c "$(sed -n '/^row_of_arm() {/,/^}/p' "$DRIVER"); row_of_arm Q-S")
chk "(c9) row_of_arm Q-S (driver's own bytes, executed)" "$Q" ""
I=$(bash -c "IMG_SHIPPED=S; IMG_PATCHED=P; $(sed -n '/^row_of_arm() {/,/^}/p' "$DRIVER"); $(sed -n '/^img_of() {/,/^}/p' "$DRIVER"); img_of Q-S")
chk "(c9) img_of Q-S returns empty, so the caller aborts rc=64" "$I" ""
I=$(bash -c "IMG_SHIPPED=S; IMG_PATCHED=P; $(sed -n '/^row_of_arm() {/,/^}/p' "$DRIVER"); $(sed -n '/^img_of() {/,/^}/p' "$DRIVER"); img_of O-P")
chk "(c9) and img_of O-P DOES answer, so the empty case is a refusal and not a broken function" "$I" "P"

echo
echo "(c10) THE FENCE, RE-ASSERTED AFTER EVERY EXECUTED LEG.  Asserting it only"
echo "      BEFORE is what let the first version of this file run a container:"
echo "      the claim was checked once and the world changed under it."
if [ -e "$REAL_BASE" ]; then
  bad "(c10) THIS SUITE CREATED THE REAL RUN ROOT [$REAL_BASE].  A selftest that stages a run root is a run, and this is a FENCE BREACH."
else
  ok "(c10) the real run root [$REAL_BASE] still does not exist -- no executed leg reached it"
fi
NC=$(sudo -n docker ps -a --format '{{.Names}}' 2>/dev/null | grep -ac '^so3_' || true)
chk "(c10) and no container carrying this item's prefix exists" "${NC:-0}" "0"

echo
echo "DRIVE $((PASS+FAIL)) checks, $FAIL fail"
[ "$FAIL" -eq 0 ] || exit 1
