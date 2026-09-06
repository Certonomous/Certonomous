#!/usr/bin/env bash
# ===========================================================================
# D6RF4 RUN-ROOT STAGER.  IT LAUNCHES NOTHING.
#
# WHY THIS FILE EXISTS, STATED FIRST BECAUSE IT IS THE WHOLE POINT.
#
# D6RF4's P_conv arm was placed at 16:32:07Z and ABORTED `launcher_rc=4` at
# 16:33:09Z having burned ZERO SOLVER CORE-MINUTES, at d6rf4_run_arm.sh:515:
#
#     test "$(stat -c '%a' "$BASE")" = "777" || { echo "ABORT L-251 ..."; exit 4; }
#
# THE RUN ROOT NEVER EXISTED.  `d6rf4_run_arm.sh` contains ZERO `mkdir`: the
# launcher has never created its own run root, in this item or in its parent.
# In D6RF3 that work lived in `d6rf3_chain_driver.sh:92-112`, headed "ROOT
# STAGING on the first fire only".  D6RF4 registered ONE arm, dropped the chain
# driver, and THE ROOT-STAGING BLOCK WENT WITH IT -- while the launcher still
# assumes a populated root in THREE places:
#
#   :515       $BASE exists and its mode is exactly 777          (L-251)
#   :518-527   NINE files md5-asserted directly in $BASE/
#   :632       $BASE/base/constant/polyMesh/points{,.gz}, md5 == MD5_REF_MESH
#
# This is DETERMINISTIC, not a race: the same argv aborts identically.  And
# merely creating the directory is NOT the repair -- it would then abort at the
# first md5 check.  THE REPAIR IS THE WHOLE STAGING LAYER, NOT THE MKDIR.
#
# ---------------------------------------------------------------------------
# THIS IS THE THIRD DROPPED-LAYER FAILURE IN THIS FAMILY IN ONE NIGHT.
# A1WRT2 deleted a `cmd.sh` wrapper and lost FOUR clauses, two of which are
# still missing.  The lesson its successor was handed -- "enumerate what the
# deleted layer did, CLAUSE BY CLAUSE, and account for every clause" -- is
# discharged for D6RF4 in PREREGISTRATION.md's 2026-09-06 ROOT-STAGING
# amendment: 282 lines, 171 non-comment non-blank, 29 clauses, ZERO
# unaccounted.  THIS FILE IS THE "RESTORED" COLUMN OF THAT TABLE.
#
# ---------------------------------------------------------------------------
# THE STAGING LIST IS DERIVED FROM THE LAUNCHER'S OWN BYTES, NOT WRITTEN HERE.
#
# A SECOND HAND LIST IS THE DEFECT THAT PRODUCED THIS ABORT.  D6RF3 carried the
# instrument names and md5s TWICE -- once in the launcher and once in the chain
# driver -- and the two lists could drift; when the driver was dropped, the
# launcher's list was left asserting files nobody staged.  So this file writes
# NO instrument name and NO md5 of its own.  It PARSES `d6rf4_run_arm.sh` for
# the exact assertion lines
#
#     echo "$MD5_<NAME>  $BASE/<file>" | md5sum -c -
#
# resolves each `MD5_<NAME>` against that launcher's OWN `^MD5_<NAME>=` line,
# and stages precisely that set.  IF THE LAUNCHER GAINS A TENTH ASSERTION, THIS
# FILE STAGES A TENTH FILE WITHOUT BEING EDITED.  A parser that finds ZERO
# assertions REFUSES (rc 40) -- it does not report "nothing to stage", which is
# the planted-zero shape in a stager (CLAUDE.md rule 3).  Each `MD5_<NAME>` is
# asserted assigned EXACTLY ONCE in the launcher: `d6rf4_run_arm.sh:92-96`
# records that `MD5_ANCHOR_GATE` was once assigned twice with the STALE value
# second, and in shell the last assignment wins.
#
# ---------------------------------------------------------------------------
# NO GATE, THRESHOLD, BAND, CAP, DEADLINE OR LABEL IS TOUCHED BY THIS FILE.
# `d6rf4_run_arm.sh` IS NOT EDITED and its md5 is not re-pinned.  This file is
# ADDITIVE: it puts on disk the state the launcher has always assumed.
#
# THERE IS NO `rm -rf`, NO `rm -r` AND NO `find -delete` IN THIS FILE.  It
# creates and copies; it never removes.  A root that is already there is
# RE-ASSERTED, never re-staged and never cleaned.
#
# THIS FILE LAUNCHES NOTHING.  It runs no container, calls no launcher and
# places no queue row.  THE RE-FIRE IS THE dafoam-supervisor's DECISION.
#
# REGISTERED EXIT CODES (DISJOINT FROM THE LAUNCHER'S 3/4/5/7/8/64/65/77, so a
# queue row's `launcher_rc` names WHICH layer refused):
#   0   staged, or already present and fully re-asserted
#   40  shape / usage -- launcher absent, parser found nothing, a duplicate
#       `MD5_*` assignment, an unresolvable pin
#   41  an md5 mismatch, source side or staged side
#   42  the cumulative item-ceiling guard refused, or spend is UNMEASURED
#   43  a refusal -- foreign root, ALREADY_BOUGHT, live driver, live container,
#       or a pre-existing arm directory
#   44  a filesystem step failed -- mkdir, chmod, cp, or the L-251 mode read
#
# `set -e` DOES NOT GATE at the top level of a harness Bash call.  Every step
# below gates explicitly with `|| { echo ABORT...; exit N; }`.
# ===========================================================================
set -uo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ITEM=D6RF4
ARM=P_conv
REGISTERED_BASE=/home/ubuntu/certonomous-runs/CURRICULUM-D6RF4-a2-wing-convergence-probe
# `BASE` is overridable ONLY so d6rf4_stage_root_control.py can drive this file
# against a sandbox root.  `d6rf4_run_arm.sh:82` takes the override the same
# way, so the control drives the launcher's assertions against the same root
# this stager built -- the two agree by construction, not by transcription.
BASE="${BASE:-$REGISTERED_BASE}"
D4_BASE_SRC="${D4_BASE_SRC:-/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/base}"
LAUNCHER="$HERE/d6rf4_run_arm.sh"
CEILING_GUARD="$HERE/../../../_common/item_ceiling_guard.py"

# ---- THE ONE MD5 THIS FILE PINS ITSELF, AND WHY IT IS THE EXCEPTION -------
# The instrument md5s are read from the launcher.  The CEILING GUARD is not an
# instrument the launcher asserts -- it is the shared implementation at
# cases/dafoam/_common/, pinned by D6RF3's driver at :64 and carried here
# unchanged.  Nothing else in this file is a transcribed hash.
MD5_CEILING_GUARD=1ea97c9245dedbc451d62e1bcfe26eb9

# ---- THE ITEM CEILING, AND IT IS QUOTED, NOT CHOSEN -----------------------
# `d6rf4_grade.py:184` registers `CAPS = {"P_conv": 54.00}` and `:696` computes
# `ceiling_core_min = sum(CAPS.values())`.  WITH ONE REGISTERED ARM THE ITEM
# CEILING **IS** THE ARM CAP, and both numbers below are that same registered
# 54.00 read out of the frozen grader -- NOT a new threshold, and nothing here
# moves a cap.  PREREGISTRATION.md section 8.2 registers the cap; the amendment
# at line 621 of that file distinguishes it from the LAUNCHER's own
# `CEILING = 3.0 x CAP = 162.0`, which is a different quantity with a different
# consequence and is NOT the figure used here.
ITEM_CEILING_CORE_MIN=54.00
ARM_CAP_CORE_MIN=54.00

# Overridable for the same reason `BASE` is: so the control can drive this file
# without overwriting the real root's staging record.
STAGE_EVID="${STAGE_EVID:-$HERE/D6RF4_ROOT_STAGING.txt}"
say() { echo "$*"; echo "$*" >> "$STAGE_EVID"; }

: > "$STAGE_EVID"
say "D6RF4_STAGE_ROOT begin utc=$(date -u +%Y%m%dT%H%M%SZ) pid=$$ item=$ITEM arm=$ARM base=$BASE launches=NOTHING"

test -f "$LAUNCHER" || { say "ABORT SHAPE launcher absent: $LAUNCHER -- the staging list is DERIVED from it and cannot be guessed"; exit 40; }
LAUNCHER_MD5=$(md5sum "$LAUNCHER" | cut -d' ' -f1)
say "D6RF4_STAGE_ROOT launcher=$LAUNCHER md5=$LAUNCHER_MD5 (READ, not pinned here -- this file never re-pins the launcher)"

# ===========================================================================
# THE DERIVATION.  Emits one `VAR FILE MD5` triple per `$BASE/` assertion the
# launcher makes, or a REFUSE- token.  It reads the launcher's bytes and
# nothing else.
# ===========================================================================
DERIVED=$(python3 - "$LAUNCHER" <<'PYEOF'
import re, sys, pathlib

src = pathlib.Path(sys.argv[1]).read_text(errors="replace").splitlines()

# The launcher's $BASE-side identity assertions, verbatim shape:
#     echo "$MD5_<NAME>  $BASE/<file>" | md5sum -c -
ASSERT = re.compile(r'^\s*echo\s+"\$(MD5_[A-Z0-9_]+)\s+\$BASE/([A-Za-z0-9_.]+)"\s*\|\s*md5sum\s+-c\s+-')
PIN = re.compile(r'^(MD5_[A-Z0-9_]+)=([0-9a-f]{32})\s*(?:#.*)?$')

pairs, seen_lines = [], []
for i, line in enumerate(src, 1):
    m = ASSERT.match(line)
    if m:
        pairs.append((m.group(1), m.group(2)))
        seen_lines.append(i)

# A PARSER THAT FINDS NOTHING REFUSES.  An empty staging list is
# indistinguishable from "this launcher asserts nothing at $BASE", and staging
# nothing would let the launcher abort exactly the way it already did.
if not pairs:
    print("REFUSE-EMPTY the derivation found ZERO $BASE-side md5 assertions in "
          "%s.  A stager that stages nothing has not proved delivery, it has "
          "failed to read." % sys.argv[1])
    raise SystemExit(0)

dupes = [f for _, f in pairs if [x for _, x in pairs].count(f) > 1]
if dupes:
    print("REFUSE-DUPLICATE the launcher asserts the same $BASE file more than "
          "once: %s" % " ".join(sorted(set(dupes))))
    raise SystemExit(0)

# EVERY PIN RESOLVED AGAINST ITS OWN ASSIGNMENT, AND THE ASSIGNMENT COUNTED.
# d6rf4_run_arm.sh:92-96: MD5_ANCHOR_GATE was assigned TWICE in an early draft
# and the STALE value came second.  In shell the last assignment wins.  The
# count is PINNED, not the appearance trusted.
pins, counts = {}, {}
for line in src:
    m = PIN.match(line)
    if m:
        counts[m.group(1)] = counts.get(m.group(1), 0) + 1
        pins[m.group(1)] = m.group(2)

for var, _ in pairs:
    n = counts.get(var, 0)
    if n != 1:
        print("REFUSE-PIN %s is assigned %d time(s) in the launcher; exactly 1 "
              "is required or the value staged against is not the value "
              "asserted." % (var, n))
        raise SystemExit(0)

# The reference-mesh pin is read the same way and is NOT a separate hand value.
if counts.get("MD5_REF_MESH", 0) != 1:
    print("REFUSE-PIN MD5_REF_MESH is assigned %d time(s); exactly 1 required."
          % counts.get("MD5_REF_MESH", 0))
    raise SystemExit(0)

print("OK %d %s" % (len(pairs), " ".join("%s:%s:%s" % (v, f, pins[v]) for v, f in pairs)))
print("REFMESH %s" % pins["MD5_REF_MESH"])
print("LINES %s" % ",".join(str(i) for i in seen_lines))
PYEOF
) || { say "ABORT SHAPE the derivation could not be performed -- delivery is UNMEASURED and is NOT reported as clean"; exit 40; }

case "$DERIVED" in
  OK\ *) : ;;
  *) say "ABORT SHAPE $DERIVED"; exit 40 ;;
esac

N_INSTR=$(printf '%s\n' "$DERIVED" | head -1 | awk '{print $2}')
TRIPLES=$(printf '%s\n' "$DERIVED" | head -1 | cut -d' ' -f3-)
REFMESH_MD5=$(printf '%s\n' "$DERIVED" | sed -n 's/^REFMESH //p')
ASSERT_LINES=$(printf '%s\n' "$DERIVED" | sed -n 's/^LINES //p')
case "$N_INSTR" in ''|*[!0-9]*) say "ABORT SHAPE instrument count is not a number: '$N_INSTR'"; exit 40 ;; esac
test "$N_INSTR" -gt 0 || { say "ABORT SHAPE instrument count is $N_INSTR"; exit 40; }
test -n "$REFMESH_MD5" || { say "ABORT SHAPE MD5_REF_MESH did not resolve"; exit 40; }
say "D6RF4_STAGE_ROOT DERIVED $N_INSTR \$BASE-side assertion(s) from the launcher's own bytes, at lines [$ASSERT_LINES]; MD5_REF_MESH=$REFMESH_MD5"

# ---- SOURCE SIDE FIRST.  Nothing is created until every source file exists
# ---- and already hashes to the value the launcher will demand.  A stager that
# ---- makes a directory and THEN discovers a bad source has left a half-root
# ---- behind that the launcher would abort on at :518 instead of :515.
for t in $TRIPLES; do
  V=${t%%:*}; rest=${t#*:}; F=${rest%%:*}; M=${rest##*:}
  test -f "$HERE/$F" || { say "ABORT SOURCE $F is asserted by the launcher ($V) and is ABSENT from the item directory $HERE"; exit 41; }
  G=$(md5sum "$HERE/$F" | cut -d' ' -f1)
  test "$G" = "$M" || { say "ABORT SOURCE md5 $F got=$G want=$M ($V) -- the item directory does not hold the bytes the launcher asserts, so staging it would only move the abort from :515 to :518"; exit 41; }
  say "D6RF4_STAGE_ROOT SOURCE OK $F md5=$M ($V)"
done

test -d "$D4_BASE_SRC" || { say "ABORT SOURCE D4 base source absent: $D4_BASE_SRC"; exit 41; }
SRC_MESH=""
for c in "$D4_BASE_SRC/constant/polyMesh/points" "$D4_BASE_SRC/constant/polyMesh/points.gz"; do
  [ -f "$c" ] && { SRC_MESH="$c"; break; }
done
test -n "$SRC_MESH" || { say "ABORT SOURCE $D4_BASE_SRC/constant/polyMesh holds NEITHER points NOR points.gz -- the undeformed reference mesh is this arm's md5 anchor"; exit 41; }
SRC_MESH_MD5=$(md5sum "$SRC_MESH" | cut -d' ' -f1)
test "$SRC_MESH_MD5" = "$REFMESH_MD5" || { say "ABORT SOURCE reference mesh md5 $SRC_MESH_MD5 != launcher's MD5_REF_MESH $REFMESH_MD5 -- staging this would warp the FD perturbation from an already-deformed mesh, the confound that killed D4's arm F"; exit 41; }
test -f "$D4_BASE_SRC/FFD/wingFFD.xyz" || { say "ABORT SOURCE $D4_BASE_SRC has no FFD/wingFFD.xyz"; exit 41; }
say "D6RF4_STAGE_ROOT SOURCE OK base=$D4_BASE_SRC mesh=$(basename "$SRC_MESH") md5=$SRC_MESH_MD5 FFD/wingFFD.xyz present"

# ---- LIVE-WORK GUARD, BEFORE ANY CREATE.  Carried from d6rf3_chain_driver.sh
# ---- :130-136 (the driver pidfile) and widened with the launcher's own
# ---- G-ROOT.5 container reading, because two records for one run is the
# ---- defect this family keeps paying for.
#
# THE DOCKER READ IS REPORTED AS UNMEASURED WHEN IT FAILS, NEVER AS "none".
# `docker ps` that cannot run and `docker ps` that returns nothing produce the
# same empty string, and reading the second from the first is the planted-zero
# shape (rule 3).  This stager creates and copies but never removes, so an
# UNMEASURED reading is REPORTED and does not refuse -- the launcher's own
# G-ROOT.5 reads it again immediately before anything destructive.
if PS_OUT=$(sudo -n docker ps --format '{{.Names}}' 2>/dev/null); then
  DOCKER_READ=MEASURED
  LIVE=$(printf '%s\n' "$PS_OUT" | grep "^d6rf4_${ARM}_" | head -3 | tr '\n' ',' | sed 's/,$//')
else
  DOCKER_READ=UNMEASURED
  LIVE=""
fi
say "D6RF4_STAGE_ROOT LIVE_READ docker=$DOCKER_READ same_arm_containers=[${LIVE:-none}]"
if [ -n "$LIVE" ]; then
  say "ABORT LIVE a RUNNING container already carries this item's prefix and arm: [$LIVE].  Staging under a live arm is two records for one run.  REFUSED."
  exit 43
fi
PIDFILE="$BASE/d6rf4_driver.pid"
if [ -f "$PIDFILE" ]; then
  OLD=$(tr -dc '0-9' < "$PIDFILE" | head -c 12)
  if [ -n "$OLD" ] && kill -0 "$OLD" 2>/dev/null; then
    say "ABORT LIVE a driver pidfile names live pid $OLD ($PIDFILE).  Another process owns this run root.  REFUSED."
    exit 43
  fi
fi

# ---- FOREIGN ROOT, REFUSED BEFORE ANY WRITE AND BEFORE ANY D6RF4 ASSERTION.
# THIS ORDERING WAS A DEFECT AND ITS OWN CONTROL CAUGHT IT.  On the control's
# FIRST drive, direction D8 (a root whose ledger reads `ITEM=D19T`) came back
# rc=41 "ABORT STAGED md5" instead of rc=43: the foreign-item check sat AFTER
# the staged-instrument assertions, so another item's run root was reported as
# a D6RF4 md5 failure -- a true refusal with a false reason, which sends its
# reader hunting the wrong defect.  The check is hoisted here, ahead of every
# write and every D6RF4-shaped assertion.  The later ledger block is NOT
# removed: this one is a PRE-WRITE REFUSAL, that one is a POST-STAGE
# ASSERTION, and they answer different questions.
if [ -f "$BASE/ledger.txt" ]; then
  PRE_FOREIGN=$(grep -a "^ITEM=" "$BASE/ledger.txt" | grep -av "^ITEM=$ITEM$" | head -1)
  test -z "$PRE_FOREIGN" || { say "ABORT REFUSE the root at $BASE carries another item: $PRE_FOREIGN.  Nothing is written into another item's run root."; exit 43; }
fi

# ===========================================================================
# ROOT STAGING ON THE FIRST FIRE ONLY -- d6rf3_chain_driver.sh:92-112's clause,
# RESTORED.  On a root that already exists NOTHING IS RE-STAGED and NOTHING IS
# REMOVED; every assertion below still runs, so this file is safe to place in
# front of EVERY fire and the ceiling guard is asserted before every fire
# rather than only before the first.
# ===========================================================================
if [ ! -d "$BASE" ]; then
  mkdir -p "$BASE" || { say "ABORT FS cannot create run root $BASE"; exit 44; }
  chmod 777 "$BASE" || { say "ABORT FS chmod 777 $BASE (L-251)"; exit 44; }
  cp -a "$D4_BASE_SRC" "$BASE/base" || { say "ABORT FS copy base/ from $D4_BASE_SRC"; exit 44; }
  for t in $TRIPLES; do
    rest=${t#*:}; F=${rest%%:*}
    cp -a "$HERE/$F" "$BASE/$F" || { say "ABORT FS copy instrument $F into $BASE/"; exit 44; }
  done
  # G-ROOT.3 accepts ONLY an exact `ITEM=D6RF4` line; staging metadata goes on a
  # line that does not start with ITEM= (D5-DRIVER-DEF-1, inherited through
  # d6rf3_chain_driver.sh:105-108).
  echo "ITEM=$ITEM" > "$BASE/ledger.txt" || { say "ABORT FS cannot write $BASE/ledger.txt"; exit 44; }
  echo "STAGED stamp=$(date -u +%Y%m%dT%H%M%SZ) base_src=$D4_BASE_SRC launcher_md5=$LAUNCHER_MD5 stager=d6rf4_stage_root.sh" >> "$BASE/ledger.txt"
  STAGED_NOW=yes
  say "D6RF4_ROOT_STAGED base=$BASE stamp=$(date -u +%Y%m%dT%H%M%SZ) mode=$(stat -c '%a' "$BASE") instruments=$N_INSTR base_src=$D4_BASE_SRC"
else
  STAGED_NOW=no
  say "D6RF4_ROOT_PRESENT base=$BASE (NOT re-staged, NOTHING removed) -- every assertion below still runs"
fi

# ===========================================================================
# THE LAUNCHER'S THREE ASSUMPTIONS, ASSERTED HERE TOO.  These are not a
# substitute for the launcher's own checks -- they are a cheaper, earlier copy
# of them, so a staging failure is named as a staging failure rather than
# arriving as `ABORT L-251 run root mode ` with an empty mode field.
# ===========================================================================

# (1) :515 -- exists, and mode EXACTLY 777.
MODE=$(stat -c '%a' "$BASE" 2>/dev/null)
test -n "$MODE" || { say "ABORT FS cannot read the mode of $BASE -- it does not exist after staging"; exit 44; }
test "$MODE" = "777" || { say "ABORT L-251 run root mode $MODE != 777 at $BASE -- d6rf4_run_arm.sh:515 would refuse this root"; exit 44; }
say "D6RF4_STAGE_ROOT (1/3) OK $BASE exists, mode=$MODE -- d6rf4_run_arm.sh:515 satisfied"

# (2) :518-527 -- every asserted file present at $BASE with the launcher's md5.
for t in $TRIPLES; do
  V=${t%%:*}; rest=${t#*:}; F=${rest%%:*}; M=${rest##*:}
  echo "$M  $BASE/$F" | md5sum -c - >/dev/null 2>&1 || {
    say "ABORT STAGED md5 $F at $BASE ($V want=$M got=$(md5sum "$BASE/$F" 2>/dev/null | cut -d' ' -f1 || echo ABSENT)) -- d6rf4_run_arm.sh would refuse this at its \$BASE assertion"
    exit 41; }
done
say "D6RF4_STAGE_ROOT (2/3) OK all $N_INSTR staged instrument md5s match the launcher's own pins at $BASE -- d6rf4_run_arm.sh:$ASSERT_LINES satisfied"

# (3) :632 -- the undeformed reference mesh, under either name, md5 anchored.
STAGED_MESH=""
for c in "$BASE/base/constant/polyMesh/points" "$BASE/base/constant/polyMesh/points.gz"; do
  [ -f "$c" ] && { STAGED_MESH="$c"; break; }
done
test -n "$STAGED_MESH" || { say "ABORT STAGED $BASE/base/constant/polyMesh holds NEITHER points NOR points.gz -- d6rf4_run_arm.sh:632 would refuse"; exit 41; }
STAGED_MESH_MD5=$(md5sum "$STAGED_MESH" | cut -d' ' -f1)
test "$STAGED_MESH_MD5" = "$REFMESH_MD5" || { say "ABORT STAGED reference mesh md5 $STAGED_MESH_MD5 != $REFMESH_MD5"; exit 41; }
test -f "$BASE/base/FFD/wingFFD.xyz" || { say "ABORT STAGED base/ has no FFD/wingFFD.xyz (d6rf3_chain_driver.sh:128's clause)"; exit 41; }
say "D6RF4_STAGE_ROOT (3/3) OK $STAGED_MESH md5=$STAGED_MESH_MD5, FFD/wingFFD.xyz present -- d6rf4_run_arm.sh:632 satisfied"

# ---- G-ROOT.3's own precondition, asserted rather than left vacuous -------
# THE LAUNCHER'S G-ROOT.3 IS `if [ -f "$BASE/ledger.txt" ]`, so ON AN ABSENT
# ROOT IT PASSES VACUOUSLY AND PRINTS `ledger_clean=yes` -- which it did, in
# launcher.queue.out, sixty-two seconds before the abort.  A ledger that EXISTS
# and carries this item's exact ITEM= line makes that pass mean something.
test -f "$BASE/ledger.txt" || { say "ABORT STAGED $BASE/ledger.txt absent -- G-ROOT.3 would pass VACUOUSLY on an absent ledger and announce ledger_clean=yes"; exit 41; }
grep -aqx "ITEM=$ITEM" "$BASE/ledger.txt" || { say "ABORT STAGED $BASE/ledger.txt has no exact 'ITEM=$ITEM' line"; exit 41; }
FOREIGN=$(grep -a "^ITEM=" "$BASE/ledger.txt" | grep -av "^ITEM=$ITEM$" | head -1)
test -z "$FOREIGN" || { say "ABORT REFUSE the ledger at $BASE/ledger.txt carries another item: $FOREIGN"; exit 43; }
grep -aq "ROW=SHIPPED" "$BASE/ledger.txt" && { say "ABORT REFUSE the ledger already carries SHIPPED rows; D6RF is registered PATCHED-ONLY"; exit 43; }
say "D6RF4_STAGE_ROOT LEDGER OK exact ITEM=$ITEM line present, no foreign item, no SHIPPED row -- G-ROOT.3 now passes on EVIDENCE, not on an absent file"

# ---- ALREADY_BOUGHT -- d6rf3_chain_driver.sh:172-176's clause, RESTORED ---
if grep -aq "^ARM=$ARM .* rc=0 " "$BASE/ledger.txt" 2>/dev/null; then
  say "ABORT REFUSE ALREADY_BOUGHT arm $ARM has an rc=0 ledger row; a second record for one run is the defect."
  exit 43
fi

# ---- THE ARM DIRECTORY MUST BE ABSENT -- the launcher's S1 refusal, caught
# ---- here, before a 1.8 MB base copy rather than after it.  NOTHING IS
# ---- REMOVED: recovery is an explicit `mv`, never an implicit delete.
if [ -e "$BASE/$ARM" ]; then
  say "ABORT REFUSE $BASE/$ARM already exists.  This stager does not remove an arm directory and neither does the launcher (:618)."
  say "  A re-fire needs the partial arm directory ARCHIVED by mv, not deleted."
  exit 43
fi

# ===========================================================================
# THE CUMULATIVE ITEM-CEILING GUARD -- d6rf3_chain_driver.sh:144-196's clause,
# RESTORED, and asserted BEFORE the fire because this file runs before it.
#
# The guard answers on its EXIT CODE.  No spend figure is interpolated into any
# shell arithmetic context -- that is the fail-open the shared implementation
# was written to close.  An absent, unreadable or unparseable ledger is
# UNMEASURED and REFUSES; it is never 0.0.
#
# WITH ONE REGISTERED ARM the cumulative check and the per-arm cap coincide:
# both are the 54.00 core-min `d6rf4_grade.py:184` registers.  That is not a
# reason to drop the guard -- a re-fire after a NON-ZERO rc can spend again,
# and ALREADY_BOUGHT only covers the rc=0 case.
# ===========================================================================
test -f "$CEILING_GUARD" || { say "ABORT CEILING item ceiling guard absent: $CEILING_GUARD"; exit 42; }
echo "$MD5_CEILING_GUARD  $CEILING_GUARD" | md5sum -c - >/dev/null 2>&1 || { say "ABORT CEILING item ceiling guard md5 (want $MD5_CEILING_GUARD, got $(md5sum "$CEILING_GUARD" | cut -d' ' -f1))"; exit 42; }
# THE rc IS TAKEN OFF THE GUARD ITSELF, NOT OFF A PIPELINE.  `cmd | head -1`
# reports head's success under some shell settings and the guard's under
# others; the guard answers on its EXIT CODE and that code is read directly.
GUARD_OUT=$(python3 "$CEILING_GUARD" --check --ledger "$BASE/ledger.txt" \
             --cap "$ARM_CAP_CORE_MIN" --ceiling "$ITEM_CEILING_CORE_MIN" \
             --label "$ITEM/$ARM" 2>&1)
GUARD_RC=$?
GUARD_LINE=$(printf '%s\n' "$GUARD_OUT" | head -1)
if [ "$GUARD_RC" -ne 0 ]; then
  say "ABORT CEILING item ceiling or UNMEASURED spend for arm $ARM (guard rc=$GUARD_RC)"
  say "  $GUARD_LINE"
  say "  An overrun stops the run; it does not get a new budget (CLAUDE.md rule 12),"
  say "  and an unreadable ledger is UNMEASURED, which refuses like a breach."
  exit 42
fi
say "D6RF4_STAGE_ROOT CEILING OK cap=$ARM_CAP_CORE_MIN ceiling=$ITEM_CEILING_CORE_MIN guard_rc=$GUARD_RC | $GUARD_LINE"

say "D6RF4_STAGE_ROOT COMPLETE base=$BASE staged_now=$STAGED_NOW instruments=$N_INSTR mode=$MODE utc=$(date -u +%Y%m%dT%H%M%SZ)"
say "D6RF4_STAGE_ROOT THIS FILE LAUNCHED NOTHING.  The re-fire is the dafoam-supervisor's decision."
exit 0
