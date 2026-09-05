#!/bin/bash
# =============================================================================
# a1wrt2_run_arm.sh -- the A1WRT2 arm launcher.  NOT FROZEN.  NOT PINNED.
#
# THIS FILE LAUNCHES NOTHING IN ITS CURRENT STATE.  The container invocation is
# behind `LAUNCH_ENABLED`, which is `0` and which no agent may raise: the item
# is not frozen, its pre-registration is a DRAFT with no evidentiary force, and
# `A1WRT2_SUCCESSOR_DRAFT.md` section 11 lists six things owed before a freeze
# and three more before an enqueue.  ZERO COMPUTE.
#
# WHAT IT IS FOR: draft section 6's cumulative item-ceiling guard, as the UNION
# of the two forms this family already has, plus draft section 8's `G-UNBOUND`
# precondition -- both of which must run and refuse BEFORE the container starts,
# because the runner's own cap is advisory, inert and off by construction
# (`docs/standards/RUNNER_CAP_ENFORCEMENT_CLAUSE.md`, D539).  A cap that reports
# an overrun it can never stop is not a cap.
#
# THE UNION, AND WHERE EACH LIMB COMES FROM
# ------------------------------------------
# FROM `a1wrt_run_unit.sh:283-317` -- A1WRT's own guard, which EXISTS and FIRED
# LIVE (`launcher.queue.out:4`:
#   A1WRT_ITEM_CEILING spent_core_min=55.317 + unit_cap=2943.0 = 2998.317 <= ceiling=3304.0 OK)
#   * the UNMEASURED-refusal limb (`:296-304`), exit 65, which `d6rf` LACKS:
#     an unparseable ledger REFUSES rather than assuming zero, because a zero
#     that means "could not read" is a planted zero (`CLAUDE.md` rule 3).
#
# FROM `d6rf_chain_driver.sh:164-169` -- two limbs A1WRT LACKS:
#   * a `+0.02` comparison tolerance against float noise;
#   * a `STATUS.<arm>` row written ON REFUSAL, so the refusal is durable
#     outside the launcher's stdout.
#
# ADDED HERE (draft section 6 item 3): the spend census is printed on EVERY
# arm, PASS OR REFUSE.  `A1ZE` ADDENDUM C's general test -- can the code path
# distinguish "the check ran and found nothing" from "the check did not run"?
# If it cannot, its zero must refuse -- and a guard that only speaks when it
# refuses fails that test, because its silence is indistinguishable from its
# success.
#
# CORRECTION ON THE RECORD: an earlier brief held that A1WRT's item had NO
# cumulative ceiling guard and that only `d6rf`/`d6rf2` carried one.  A1WRT has
# one, at `a1wrt_run_unit.sh:283-317`, and it is in one respect STRONGER than
# `d6rf`'s.  The unguarded four-arms finding belongs to `a1wr_chain_driver.sh`
# -- A1WR's driver -- and A1WRT uses no chain driver at all.  So this file
# PORTS a guard the item already has, from itself, and adds the two limbs it
# lacked.
#
# SUBMISSIONS PARKED.  Nothing here is filed, sent, uploaded or posted.
# =============================================================================

set -euo pipefail

LAUNCH_ENABLED=0            # <-- 0 until the freeze and the enqueue land.

ITEM="A1WRT2"
# The pinned image (draft section 3, inherited by md5).  The TAG is a name; the
# DIGEST is the identity, and `G-IMG` binds the digest -- which is why
# `measure_image_pins` reads the digest out of the image instead of this line.
IMG="dafoam-idwarp-rot:v1"
ITEM_CEILING_CORE_MIN=685.0
CEIL_TOL=0.02               # d6rf's float-noise tolerance
BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_ROOT="${A1WRT2_RUN_ROOT:-/home/ubuntu/certonomous-runs/A1WRT2}"
LEDGER="$RUN_ROOT/ledger.txt"
# STATUS rows are written under STATUS_DIR so the selftest can drive the
# durable-row limb without writing into the committed case directory.
STATUS_DIR="${A1WRT2_STATUS_DIR:-$BASE}"
STATUS="$STATUS_DIR/STATUS.$ITEM"

# ---- THE RUN-ROOT PRODUCT PATHS, WRITTEN AS LITERALS ------------------------
# Per-arm paths are spelled out rather than interpolated from $ARM.  Two
# reasons, and the second is the one that matters:
#   1. `a1wrt2_instruments.py`'s producer trace resolves a redirection target
#      through the same variable binding the reference extractor uses; a target
#      carrying a live `$` inside its tail is DYNAMIC and is never counted as a
#      producer.  An interpolated path would leave every product of this file
#      untraced -- which is the finding this section exists to close.
#   2. The two arms are NOT symmetric.  TAIL carries a launch precondition on
#      SEAM's verdict (the 2026-09-04 ruling 1) and SEAM carries none, so an
#      arm dispatch that pretended they were interchangeable would be hiding
#      the very asymmetry the ruling introduced.
MANIFEST_PATH="$RUN_ROOT/MANIFEST.json"
SEAM_OUT="$RUN_ROOT/SEAM/out"
TAIL_OUT="$RUN_ROOT/TAIL/out"
SEAM_CASE="$RUN_ROOT/SEAM/case"
TAIL_CASE="$RUN_ROOT/TAIL/case"

usage() { echo "usage: $0 --arm {SEAM|TAIL} [--selftest]" >&2; exit 64; }

ARM=""
SELFTEST=0
while [ $# -gt 0 ]; do
  case "$1" in
    --arm)         ARM="${2:-}"; shift 2 ;;
    --selftest)    SELFTEST=1; shift ;;
    --guards-only) GUARDS_ONLY=1; shift ;;
    --emit-manifest) EMIT_MANIFEST=1; shift ;;
    --emit-ledger)   EMIT_LEDGER="${2:-}"; shift 2 ;;
    # Selftest entries.  They exist so the controls drive THIS FILE'S OWN code
    # rather than a copy of it pasted into the selftest -- the difference that
    # let a broken `measure_image_pins` sit undriven for a day.
    --drive-pin-guard)     DRIVE_PIN_DIG="${2:-}"; DRIVE_PIN_WARP="${3:-}"; shift 3 ;;
    --drive-md5-classifier) DRIVE_MD5="${2:-}"; shift 2 ;;
    *)             usage ;;
  esac
done
GUARDS_ONLY="${GUARDS_ONLY:-0}"
EMIT_MANIFEST="${EMIT_MANIFEST:-0}"
EMIT_LEDGER="${EMIT_LEDGER:-}"
DRIVE_PIN_DIG="${DRIVE_PIN_DIG:-}"
DRIVE_PIN_WARP="${DRIVE_PIN_WARP:-}"
DRIVE_MD5="${DRIVE_MD5:-}"

# ---- the registered per-arm caps.  Draft section 5.4. -----------------------
arm_cap() {
  case "$1" in
    SEAM) echo "10.0" ;;
    TAIL) echo "675.0" ;;
    *)    echo "" ;;
  esac
}

# ---- LIMB 1: prior spend.  WRITTEN FRESH.  UNMEASURED REFUSES. -------------
# The UNMEASURED-refusal limb is the PRIMARY here, not an extra, and it is kept
# EXACTLY as `a1wrt_run_unit.sh:297-305` has it, because that is the only file
# in this family that gets it right.  From `d6rf_chain_driver.sh` this file
# takes ONLY the projection arithmetic (PROJ = SPENT + THIS ARM's cap, refused
# BEFORE the arm) and the `+0.02` tolerance and the durable STATUS row.  Its
# spend READER is not ported, because it FAILS OPEN two ways, both MEASURED in
# this drafting invocation by running its exact body:
#
#   * ledger ABSENT -> `except IOError: pass` prints `0.000`.  "Could not read"
#     is then indistinguishable from "nothing spent" -- a planted zero inside
#     the guard's own input (CLAUDE.md rule 3).
#   * `core_min=1.2.3` -> its `([0-9.]+)` regex matches the whole malformed
#     token, float() raises a ValueError nothing catches, and $SPENT comes back
#     EMPTY.  The driver then evaluates `( $SPENT + $ACAP )` in python, which
#     with an empty SPENT is `( + 480.0)` -- UNARY PLUS -- so PROJ is a clean
#     `480.000` and THE GUARD PASSES, having silently dropped 100.0 core-min of
#     recorded prior spend.  (Refinement on the record: the comparison does not
#     fail and PROJ is not empty.  It is worse: the guard proceeds on a
#     confidently wrong number.)
#
# THE RULES THIS READER FOLLOWS:
#   ledger ABSENT               -> 0.0        (legitimate: no arm has run)
#   ANY read/decode failure     -> UNMEASURED (refuses at 65)
#   ANY core_min= token that
#     does not float() cleanly  -> UNMEASURED (never a prefix of it)
#   content but zero rows       -> UNMEASURED
# The token is captured WHOLE (`\S+`) and then parsed, so a malformed token can
# never be read as a plausible number.
spent_core_min() {
  python3 - "$LEDGER" <<'PYEOF' 2>/dev/null || echo "UNMEASURED"
import os, re, sys
p = sys.argv[1]
if not os.path.exists(p):
    print("0.0"); raise SystemExit
try:
    raw = open(p, "rb").read().decode("utf-8", "replace")
except Exception:
    print("UNMEASURED"); raise SystemExit
tot, rows = 0.0, 0
for line in raw.splitlines():
    m = re.search(r"\bcore_min=(\S+)", line)
    if not m:
        continue
    try:
        v = float(m.group(1))
    except ValueError:
        print("UNMEASURED"); raise SystemExit
    if v != v or v in (float("inf"), float("-inf")):
        print("UNMEASURED"); raise SystemExit
    tot += v; rows += 1
if rows == 0 and raw.strip():
    print("UNMEASURED"); raise SystemExit
print("%.3f" % tot)
PYEOF
}

# ---- LIMB 2 (draft section 8): G-UNBOUND, over THIS FILE, before launch ----
# Every \$VAR expansion in the launcher, under `set -u`, assigned before first
# use; and a `set +u` fence opened and never closed is itself flagged.  The
# reader is `a1wrt2_grade.py`'s own `g_unbound`, so the gate that grades the
# launcher and the gate that guards it are ONE function and cannot drift apart.
g_unbound_precondition() {
  python3 -c "
import sys
sys.path.insert(0, '$BASE')
import a1wrt2_grade as G
v, notes = G.g_unbound(open('$1', errors='replace').read(),
                       ['A1WRT2_RUN_ROOT', 'BASH_SOURCE'])
print(v)
for n in notes: print('  ' + n, file=sys.stderr)
"
}

# ---- THE GUARD ITSELF -------------------------------------------------------
ceiling_guard() {
  local arm="$1"
  local cap spent proj
  cap="$(arm_cap "$arm")"
  if [ -z "$cap" ]; then
    echo "ABORT: no registered cap for arm $arm" >&2
    exit 64
  fi
  spent="$(spent_core_min)"
  # THE SHELL-SIDE NUMERIC ASSERTION, AND IT IS THE LIMB THAT CATCHES THE
  # UNARY-PLUS TRAP.  `d6rf`'s driver interpolates $SPENT straight into a python
  # expression, so an EMPTY value becomes `( + cap)` -- a valid expression whose
  # value is the cap -- and the guard sails through with the prior spend
  # silently zeroed.  Anything that is not a plain decimal number is treated as
  # UNMEASURED here, BEFORE it can reach an arithmetic context.
  case "$spent" in
    *[!0-9.]*|''|.|*.*.*) spent="UNMEASURED" ;;
  esac
  case "$spent" in
    ''|UNMEASURED)
      echo "ABORT ITEM CEILING: prior spend is UNMEASURED -- $LEDGER exists but"
      echo "  could not be parsed.  An unknown prior spend plus this arm's"
      echo "  ${cap} core-min cap cannot be SHOWN to fit under the"
      echo "  ${ITEM_CEILING_CORE_MIN} ceiling, so this refuses rather than"
      echo "  assuming zero.  A zero that means 'could not read' is a planted"
      echo "  zero (CLAUDE.md rule 3)."
      echo "rc=65 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$arm note=ITEM_CEILING_UNMEASURED" >> "$STATUS_DIR/STATUS.$arm"
      echo "chain=ABORT arm=$arm reason=ITEM_CEILING_UNMEASURED stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
      exit 65 ;;
  esac
  proj="$(python3 -c "print('%.3f' % ($spent + $cap))")"

  # PRINTED ON EVERY ARM, PASS OR REFUSE.  The guard's silence is never
  # mistaken for its success.
  echo "${ITEM}_SPEND_CENSUS arm=$arm spent=$spent this_arm_cap=$cap projected=$proj item_ceiling=$ITEM_CEILING_CORE_MIN"

  if [ "$(python3 -c "print(1 if $proj > $ITEM_CEILING_CORE_MIN + $CEIL_TOL else 0)")" = "1" ]; then
    echo "ABORT ITEM CEILING: $spent core-min already spent + this arm's $cap cap"
    echo "  = $proj > the registered $ITEM_CEILING_CORE_MIN ceiling."
    echo "  An overrun STOPS the run; it does not get a new budget (rule 12)."
    echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$arm note=ITEM_CEILING spent=$spent projected=$proj ceiling=$ITEM_CEILING_CORE_MIN" >> "$STATUS_DIR/STATUS.$arm"
    echo "chain=ABORT arm=$arm reason=ITEM_CEILING spent=$spent projected=$proj stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
    exit 6
  fi
  echo "${ITEM}_ITEM_CEILING OK -- $proj <= $ITEM_CEILING_CORE_MIN (+$CEIL_TOL tol)"
}

unbound_guard() {
  local v
  v="$(g_unbound_precondition "${BASH_SOURCE[0]}")"
  echo "${ITEM}_G_UNBOUND $v -- read over $(basename "${BASH_SOURCE[0]}") by a1wrt2_grade.g_unbound"
  if [ "$v" != "PASS" ]; then
    echo "ABORT G-UNBOUND: the launcher carries an expansion reachable before"
    echo "  its first assignment under set -u, or an unclosed set +u fence."
    echo "  BLOCKED -- the launcher does not run and NO compute is spent."
    echo "rc=6 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=G_UNBOUND_BLOCKED" >> "$STATUS_DIR/STATUS.${ARM:-none}"
    exit 6
  fi
}

# =============================================================================
# THE PRODUCERS.  Draft section 11 item 1a, added by the dafoam-supervisor's
# 2026-09-04 section 11.1 amendment.
#
# BEFORE THIS SECTION THIS FILE PRODUCED NOTHING.  Measured by extraction:
# `a1wrt2_instruments.py --` reported 8 run-root artefacts consumed by gates on
# the graded path, 2 traced, and **6 UNTRACED** -- five of them written at
# exactly one site each, all inside `a1wrt2_grade.py`'s `_build_happy_root`,
# WHICH IS THE SELFTEST FIXTURE BUILDER, and one (`TAIL/out/warp_probe.json`)
# written by nothing anywhere in the registered set.
#
# `G-IMG` and `G-FREEZE` ARE HARD GATES AND `MANIFEST.json` IS THEIR ONLY
# INPUT.  A hard gate fed by nothing is worse than a missing gate, because it
# reports.
#
# ⚠ THE MANIFEST'S TWO PINNED FIELDS ARE **MEASURED**, NEVER COPIED FROM THE
# PINS.  `G-IMG` compares `image_digest` and `libidwarp_md5` against
# `a1wrt2_grade.PIN_IMG_DIGEST` / `PIN_IDWARP_MD5`.  A producer that wrote those
# fields FROM those same constants would make the gate a MIRROR: it would
# compare a pin to a copy of itself and report PASS on any image whatsoever.
# So `measure_image_pins` reads them out of the IMAGE, and if it cannot, the
# manifest records `UNMEASURED` and the gate REFUSES at exit 4 -- it never
# falls back to the pin.
# =============================================================================

# Reads the two image-bound facts OUT OF THE IMAGE.  `docker image inspect`
# does not start a container; the `libidwarp.so` md5 does.
#
# ⚠ THE 2026-09-04 VERSION OF THIS FUNCTION WAS DRIVEN FOR THE FIRST TIME ON
# 2026-09-05 AND WAS MEASURED BROKEN.  It is quoted here because the repair is
# unreadable without it:
#
#     docker run --rm --entrypoint /bin/sh "$img" -c \
#       'md5sum $(python -c "...print(...libidwarp.so...)") 2>/dev/null | cut -d" " -f1'
#
# In this image `python` is NOT on PATH until `loadDAFoam.sh` is sourced, and
# `--entrypoint /bin/sh -c` sources nothing.  So the command substitution
# produced the EMPTY STRING, `md5sum` was handed NO OPERAND, fell back to
# STDIN, read end-of-file, and printed
#
#     d41d8cd98f00b204e9800998ecf8427e     <-- THE MD5 OF THE EMPTY STRING
#
# at rc 0.  `[ -n "$warp" ]` CANNOT SEE THAT: the value is non-empty, so the
# UNMEASURED limb never fired, the manifest would have recorded the md5 of
# nothing as a measurement, and `G-IMG` would have refused reporting an IMAGE
# MISMATCH over an image that is provably correct.
#
# ⚠ THAT IS `CLAUDE.md` RULE 3 WEARING A HASH.  Rule 3 refuses a zero from a
# reader not shown able to see a non-zero; this was a reader returning a
# CONSTANT it had not read, and the defect was invisible for exactly as long as
# nobody drove it.  The pins themselves were never in doubt -- both are now
# MEASURED out of the image and both match.  What was broken was the reader.
#
# THE REPAIR HAS THREE LIMBS, EACH CLOSING ONE OF THOSE FAILURES:
#   1. `bash -lc` with `source /home/dafoamuser/dafoam/loadDAFoam.sh` -- this is
#      A1WRT's PROVEN form (`a1wrt_run_unit.sh:674-677`) and the only form
#      MEASURED to reach this image's python.
#   2. the md5 is computed IN-PROCESS by `hashlib` over bytes actually read from
#      the file, never by `md5sum` over a word that may be empty.
#   3. THE EMPTY-INPUT MD5 IS REFUSED BY NAME, and so is anything that is not 32
#      hex characters.  A reader returning the md5 of nothing has hashed
#      nothing, and that is UNMEASURED however non-empty it looks.
MD5_OF_NOTHING="d41d8cd98f00b204e9800998ecf8427e"
DAFOAM_LOADER="/home/dafoamuser/dafoam/loadDAFoam.sh"

# The md5 classifier, FACTORED OUT so the control can drive THE REAL ONE.  A
# classifier re-typed inside a selftest is a second implementation, and the two
# agree right up until the moment the first one is wrong.
classify_md5() {
  local v="$1"
  if [ "$v" = "$MD5_OF_NOTHING" ]; then
    echo "UNMEASURED"
  elif printf '%s' "$v" | grep -qE '^[0-9a-f]{32}$'; then
    echo "$v"
  else
    echo "UNMEASURED"
  fi
}

measure_image_pins() {
  local img="$1" dig warp
  dig="$(docker image inspect --format '{{index .RepoDigests 0}}' "$img" 2>/dev/null | sed 's/.*@//')"
  case "$dig" in
    sha256:*) : ;;
    *)        dig="UNMEASURED" ;;
  esac
  warp="$(docker run --rm --user 0:0 "$img" bash -lc \
          "source $DAFOAM_LOADER >/dev/null 2>&1 && python -c 'import idwarp,os,hashlib; so=os.path.join(os.path.dirname(idwarp.__file__),\"libidwarp.so\"); print(hashlib.md5(open(so,\"rb\").read()).hexdigest())'" \
          2>/dev/null | tr -d '[:space:]')"
  warp="$(classify_md5 "$warp")"
  echo "$dig $warp"
}

# REFUSES THE ARM **BEFORE THE CONTAINER** when either pin is UNMEASURED.
#
# ⚠ THE ORDERING IS THE REPAIR, AND MEASURING THE READER BROKEN IS WHAT MADE IT
# VISIBLE.  The 2026-09-04 design let the arm RUN with an UNMEASURED pin and
# left `G-IMG` to refuse at GRADE time -- AFTER the spend.  A broken reader
# would therefore have bought SEAM's whole cap to be told the manifest was
# unreadable.  `G-IMG` still refuses at grade time and is unchanged; this guard
# simply means a reader defect costs 0 core-min instead of an arm's cap.
refuse_unmeasured_pins() {
  local arm="$1" dig="$2" warp="$3"
  if [ "$dig" = "UNMEASURED" ] || [ "$warp" = "UNMEASURED" ]; then
    echo "rc=4 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$arm note=IMAGE_PINS_UNMEASURED dig=$dig warp=$warp" >> "$STATUS_DIR/STATUS.$arm"
    echo "${ITEM}_REFUSE arm=$arm G-IMG inputs UNMEASURED (dig=$dig warp=$warp)." >&2
    echo "  Refusing BEFORE the container: a pin this launcher could not read is" >&2
    echo "  never written into the manifest as if it had been read, and the cost" >&2
    echo "  of the reader being broken is 0 core-min rather than this arm's cap." >&2
    exit 4
  fi
  echo "${ITEM}_IMAGE_PINS_MEASURED arm=$arm digest=$dig libidwarp=$warp"
}

# PRODUCES: $RUN_ROOT/MANIFEST.json -- the sole input of the HARD gates G-IMG
# and G-FREEZE.  Runs on the host, BEFORE the container.
# ⚠ THE MANIFEST IS WRITTEN BY A LITERAL REDIRECTION AND NOT BY A PATH HANDED
# TO PYTHON, AND THE REASON IS THE TRACE ITSELF.  The first version of this
# function passed `$MANIFEST_PATH` as an argv entry and opened it inside the
# heredoc; the producer trace then reported `MANIFEST.json  UNTRACED <-- WRITTEN
# ONLY BY THE SELFTEST FIXTURE BUILDER`, because a redirection is what the
# extractor can see and an argv path is not.  Rather than widen the extractor
# to follow argv into a heredoc -- which would let a producer be "found" through
# an inference the reader cannot check -- the producer is written in the form
# the extractor reads directly.  A producer only a clever checker can find is a
# producer the next reader will not find either.
write_manifest() {
  local arm="$1" img="$2" dig="$3" warp="$4"
  mkdir -p "$RUN_ROOT"
  python3 - "$RUN_ROOT" "$arm" "$img" "$dig" "$warp" > "$MANIFEST_PATH" <<'PYEOF'
import hashlib, json, os, sys
run_root, arm, img, dig, warp = sys.argv[1:6]
def md5(p):
    with open(p, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()
# The OBSERVED side of G-FREEZE: md5s measured off the STAGED files, IN THE RUN
# ROOT, never off the item directory.  Hashing the item directory would certify
# a file the container never saw -- a freeze check on the wrong copy.
inst = {}
for name in ("runScript.py", "run_arm.sh"):
    p = os.path.join(run_root, name)
    if os.path.exists(p):
        inst[name] = md5(p)
sys.stdout.write(json.dumps({
    "item": "A1WRT2", "arm": arm, "run_root": run_root,
    "image": img,
    # MEASURED, never copied from the registered pin.  "UNMEASURED" here makes
    # G-IMG refuse at exit 4; it must never read as agreement.
    "image_digest": dig, "libidwarp_md5": warp,
    "instruments": inst,
    "env_declared": ["A1WRT2_RUN_ROOT", "A1WRT2_STATUS_DIR", "BASH_SOURCE"],
}, indent=1, sort_keys=True) + "\n")
PYEOF
  echo "${ITEM}_MANIFEST written $MANIFEST_PATH (image_digest=$dig libidwarp_md5=$warp)" >&2
}

# PRODUCES: $RUN_ROOT/ledger.txt -- read by G-CAPS and G-CEILING, and by this
# file's own `spent_core_min`.  One row per arm, appended.
append_ledger_row() {
  local arm="$1" rc="$2" wall="$3" ranks="$4" cap="$5" cm
  mkdir -p "$RUN_ROOT"
  cm="$(python3 -c "print('%.3f' % ($wall * $ranks / 60.0))")"
  echo "ARM=$arm ROW=PATCHED IMG=$IMG rc=$rc wall_s=$wall ranks=$ranks core_min=$cm cap_core_min=$cap mode=CONTINUED stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$LEDGER"
  echo "${ITEM}_LEDGER_ROW arm=$arm rc=$rc core_min=$cm cap=$cap"
}

# =============================================================================
# RULING 1 OF THE dafoam-supervisor, 2026-09-04 -- THE TAIL'S LAUNCH
# PRECONDITION ON SEAM'S VERDICT.
#
# Draft section 3's *"CONTINUED from `SEAM`'s final state, in the same process"*
# is STRUCK.  `G-SEAM` is this item's REGISTERED FALSIFIER: if it fails, every
# tail point is withdrawn AS A TAIL.  A single process spanning both arms would
# have ALREADY COMPUTED THE TAIL by the time the seam could be graded, so the
# falsifier could not stop the spend it exists to stop.  SEAM is 10.0 core-min
# and TAIL is 675.0.  675 core-min riding on a control that cannot gate it is
# not a control; it is a POST-HOC REPORT WEARING A STOP RULE'S NAME.
#
# THIS IS THE STOP RULE, AND IT IS A CHECKED PRECONDITION RATHER THAN A
# CONVENTION: it runs BEFORE the TAIL container starts, it reads SEAM's own
# artefacts off disk through the GRADER'S OWN gate functions, and only `PASS`
# lets the arm proceed.  It is driven in BOTH directions by the selftest.
# =============================================================================
seam_precondition_guard() {
  local v rc
  set +e
  v="$(python3 "$BASE/a1wrt2_grade.py" --seam-precond "$RUN_ROOT" 2>&1)"
  rc=$?
  set -e
  echo "$v" | tail -4
  if [ "$rc" != "0" ]; then
    echo "ABORT SEAM PRECONDITION: the SEAM arm's verdict does NOT permit TAIL."
    echo "  TAIL is 675.0 core-min behind a falsifier that has not cleared."
    echo "  Draft section 9: if G-SEAM fails the tail is not a continuation of"
    echo "  A1WR's polar and every point in it is WITHDRAWN AS A TAIL, so"
    echo "  buying it would be buying six solves whose registered purpose is"
    echo "  already refuted.  An overrun stops the run; so does a refuted one."
    echo "rc=7 stamp=$(date -u +%Y%m%dT%H%M%SZ) arm=$ARM note=SEAM_PRECONDITION_REFUSED" >> "$STATUS_DIR/STATUS.$ARM"
    echo "chain=ABORT arm=TAIL reason=SEAM_PRECONDITION stamp=$(date -u +%Y%m%dT%H%M%SZ)" >> "$STATUS"
    exit 7
  fi
  echo "${ITEM}_SEAM_PRECOND OK -- SEAM's verdict permits the TAIL arm"
}

# ---- SELFTEST: both guards driven in BOTH directions, on static fixtures ---
if [ "$SELFTEST" = "1" ]; then
  echo "${ITEM}_RUN_ARM SELFTEST -- host shell.  ONE container is started, for
  the image-pin measurement only (~2 wall s x 1 rank = ~0.033 core-min,
  ~\$0.00003 DERIVED at the owner-stated rate, cost_basis REPORTED-BY-OWNER).
  NO SOLVER RUNS.  Authorised by the dafoam-supervisor 2026-09-05; the
  2026-09-04 banner said NO container and that is no longer true."
  TD="$(mktemp -d)"
  trap 'rm -rf "$TD"' EXIT
  FAILED=0

  drive() {  # name expected_rc command...
    local name="$1" want="$2"; shift 2
    local out rc
    out="$("$@" 2>&1)" && rc=0 || rc=$?
    if [ "$rc" = "$want" ]; then
      echo "CONTROL $name  EXERCISED  rc=$rc (expected $want)"
      echo "$out" | sed -n '1,2p' | sed 's/^/    /'
    else
      echo "CONTROL $name  NOT EXERCISED  rc=$rc, expected $want"
      echo "$out" | sed 's/^/    /'
      FAILED=1
    fi
  }

  # ==========================================================================
  # ⚠ A CLEAN SEAM ARM IS STAGED INTO EVERY FIXTURE ROOT THAT DRIVES `--arm
  # TAIL`, AND THE REASON IS A FINDING, NOT PLUMBING.
  #
  # Ruling 1 added a launch precondition to the TAIL arm.  Re-running this
  # selftest unchanged, TWO ceiling controls that had always passed --
  # `ceiling/under-passes-and-prints` and `ceiling/exactly-at-ceiling-passes`
  # -- came back rc=7 instead of rc=0.  Not a regression: they drove
  # `--arm TAIL` against a run root with no SEAM arm, so what they had been
  # asserting was "the launcher exits 0", which conflates the ceiling limb with
  # every other reason the arm might or might not proceed.  A control that
  # cannot separate the limb it names from the rest of the launcher passes for
  # reasons it does not state.  Staging a clean SEAM makes the ceiling controls
  # test the CEILING, and the precondition controls below test the
  # PRECONDITION, on their own.
  # ==========================================================================
  mk_seam() {   # $1 = fixture run root
    python3 -c "
import sys, tempfile, shutil, pathlib
sys.path.insert(0, '$BASE')
import a1wrt2_grade as G
src = G._build_happy_root(pathlib.Path(tempfile.mkdtemp()))
shutil.copytree(str(src / 'SEAM'), '$1/SEAM')
" >/dev/null 2>&1
  }

  # -- ceiling: REFUSE at 6.  A fixture ledger summing 680.0 with TAIL's 675.0
  #    cap projects 1355.0 > 685.0.
  mkdir -p "$TD/over"; printf 'ITEM=A1WRT2\nARM=SEAM core_min=680.0\n' > "$TD/over/ledger.txt"
  drive "ceiling/over-refuses-at-6" 6 \
    env A1WRT2_STATUS_DIR="$TD" A1WRT2_RUN_ROOT="$TD/over" bash "${BASH_SOURCE[0]}" --arm TAIL --guards-only

  # -- ceiling: PASS and PRINT THE CENSUS.  3.10 + 675.0 = 678.10 <= 685.0.
  mkdir -p "$TD/under"; printf 'ITEM=A1WRT2\nARM=SEAM core_min=3.10\n' > "$TD/under/ledger.txt"
  mk_seam "$TD/under"
  drive "ceiling/under-passes-and-prints" 0 \
    env A1WRT2_STATUS_DIR="$TD" A1WRT2_RUN_ROOT="$TD/under" bash "${BASH_SOURCE[0]}" --arm TAIL --guards-only

  # -- ceiling: UNMEASURED REFUSES at 65, never at 0.0.
  mkdir -p "$TD/bad"; printf 'this ledger has no parseable core_min row\n' > "$TD/bad/ledger.txt"
  drive "ceiling/unmeasured-refuses-at-65" 65 \
    env A1WRT2_STATUS_DIR="$TD" A1WRT2_RUN_ROOT="$TD/bad" bash "${BASH_SOURCE[0]}" --arm TAIL --guards-only

  # -- ceiling: A MALFORMED core_min TOKEN REFUSES.  This is the case that
  #    actually happens and the one d6rf's reader fails open on -- and the
  #    fixture carries a REAL 100.0 prior spend on the row above it, so a
  #    reader that silently zeroed the ledger would show up as a PASS here.
  mkdir -p "$TD/malformed"
  printf 'ARM=SEAM core_min=100.0\nARM=TAIL core_min=1.2.3\n' > "$TD/malformed/ledger.txt"
  drive "ceiling/malformed-token-refuses-at-65" 65 \
    env A1WRT2_STATUS_DIR="$TD" A1WRT2_RUN_ROOT="$TD/malformed" bash "${BASH_SOURCE[0]}" --arm TAIL --guards-only

  # -- ceiling: an UNREADABLE ledger (mode 000) refuses, and does NOT read 0.0.
  mkdir -p "$TD/noperm"; printf 'ARM=SEAM core_min=100.0\n' > "$TD/noperm/ledger.txt"
  chmod 000 "$TD/noperm/ledger.txt"
  if [ "$(id -u)" = "0" ]; then
    echo "CONTROL ceiling/unreadable-refuses  NOT APPLICABLE  running as root; mode 000 does not deny root, so this limb cannot be driven here and is NOT claimed"
  else
    drive "ceiling/unreadable-refuses-at-65" 65 \
      env A1WRT2_STATUS_DIR="$TD" A1WRT2_RUN_ROOT="$TD/noperm" bash "${BASH_SOURCE[0]}" --arm TAIL --guards-only
  fi
  chmod 644 "$TD/noperm/ledger.txt"

  # -- ceiling: an ABSENT ledger is a legitimate 0.0 and must NOT refuse.
  mkdir -p "$TD/fresh"
  drive "ceiling/absent-ledger-is-zero" 0 \
    env A1WRT2_STATUS_DIR="$TD" A1WRT2_RUN_ROOT="$TD/fresh" bash "${BASH_SOURCE[0]}" --arm SEAM --guards-only

  # -- the TOLERANCE limb, which A1WRT's form lacks: 685.0 exactly, +0.0 over,
  #    must NOT trip.  Without `+0.02` this is a coin toss on float noise.
  mkdir -p "$TD/exact"; printf 'ARM=SEAM core_min=10.0\n' > "$TD/exact/ledger.txt"
  mk_seam "$TD/exact"
  drive "ceiling/exactly-at-ceiling-passes" 0 \
    env A1WRT2_STATUS_DIR="$TD" A1WRT2_RUN_ROOT="$TD/exact" bash "${BASH_SOURCE[0]}" --arm TAIL --guards-only

  # -- G-UNBOUND over this file itself: must PASS.
  drive "unbound/this-launcher-passes" 0 \
    env A1WRT2_STATUS_DIR="$TD" A1WRT2_RUN_ROOT="$TD/fresh" bash "${BASH_SOURCE[0]}" --arm SEAM --guards-only

  # -- G-UNBOUND on the committed POSITIVE fixture: must BLOCK.  Driven
  #    through the same reader the guard uses, so the guard and its control
  #    cannot disagree about what the gate is.
  V="$(g_unbound_precondition "$BASE/fixtures/g_unbound_positive.sh")"
  if [ "$V" = "BLOCKED" ]; then
    echo "CONTROL unbound/positive-fixture-blocks  EXERCISED  -> $V"
  else
    echo "CONTROL unbound/positive-fixture-blocks  NOT EXERCISED  -> $V"; FAILED=1
  fi
  V="$(g_unbound_precondition "$BASE/fixtures/g_unbound_negative.sh")"
  if [ "$V" = "PASS" ]; then
    echo "CONTROL unbound/negative-fixture-passes  EXERCISED  -> $V"
  else
    echo "CONTROL unbound/negative-fixture-passes  NOT EXERCISED  -> $V"; FAILED=1
  fi

  # -- the STATUS row is DURABLE outside stdout (d6rf's limb).
  if grep -q 'note=ITEM_CEILING ' "$TD/STATUS.TAIL" 2>/dev/null; then
    echo "CONTROL ceiling/status-row-durable  EXERCISED  -> STATUS.TAIL carries the refusal"
  else
    echo "CONTROL ceiling/status-row-durable  NOT EXERCISED  -> no STATUS.TAIL row"; FAILED=1
  fi

  # ==========================================================================
  # THE PRODUCERS, DRIVEN.  Draft section 11 item 1a.
  # ==========================================================================

  # -- MANIFEST.json is actually PRODUCED, on disk, by this file.
  mkdir -p "$TD/prod"
  env A1WRT2_STATUS_DIR="$TD" A1WRT2_RUN_ROOT="$TD/prod" \
    bash "${BASH_SOURCE[0]}" --arm SEAM --emit-manifest >/dev/null 2>&1 || true
  if [ -s "$TD/prod/MANIFEST.json" ]; then
    echo "CONTROL producer/manifest-is-written  EXERCISED  -> $(wc -c < "$TD/prod/MANIFEST.json") bytes at \$RUN_ROOT/MANIFEST.json"
  else
    echo "CONTROL producer/manifest-is-written  NOT EXERCISED  -> no MANIFEST.json"; FAILED=1
  fi

  # -- AND THE MIRROR IS REFUSED.  An UNMEASURED image digest must make G-IMG
  #    REFUSE at 4, never fall back to the registered pin.  This is the limb
  #    that matters: a producer that copied the pins into the manifest would
  #    make the hard gate compare a constant to itself.
  MIRROR="$(python3 -c "
import json, sys
sys.path.insert(0, '$BASE')
import a1wrt2_grade as G
m = json.load(open('$TD/prod/MANIFEST.json'))
try:
    G.g_img_freeze(m, {})
except G.Refuse as e:
    print('REFUSE%d' % e.code)
else:
    print('PASSED')
" 2>&1)"
  if [ "$MIRROR" = "REFUSE4" ]; then
    echo "CONTROL producer/unmeasured-digest-refuses  EXERCISED  -> G-IMG REFUSE exit 4 on image_digest=UNMEASURED; the producer never substitutes the pin"
  else
    echo "CONTROL producer/unmeasured-digest-refuses  NOT EXERCISED  -> $MIRROR"; FAILED=1
  fi

  # -- AND A MEASURED-LOOKING DIGEST THAT MATCHES THE PIN PASSES, so the
  #    refusing limb above is not simply a gate that refuses everything.
  env A1WRT2_STATUS_DIR="$TD" A1WRT2_RUN_ROOT="$TD/prod" \
      A1WRT2_FAKE_DIGEST="sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35" \
      A1WRT2_FAKE_WARPMD5="85f59e87253e0a71a813f64ca6e4c425" \
    bash "${BASH_SOURCE[0]}" --arm SEAM --emit-manifest >/dev/null 2>&1 || true
  MIRROR2="$(python3 -c "
import json, sys
sys.path.insert(0, '$BASE')
import a1wrt2_grade as G
m = json.load(open('$TD/prod/MANIFEST.json'))
v, _n = G.g_img_freeze(m, {})
print(v)
" 2>&1)"
  if [ "$MIRROR2" = "PASS" ]; then
    echo "CONTROL producer/measured-digest-passes  EXERCISED  -> G-IMG PASS when the manifest carries the measured digest"
  else
    echo "CONTROL producer/measured-digest-passes  NOT EXERCISED  -> $MIRROR2"; FAILED=1
  fi

  # -- ledger.txt is actually PRODUCED, and G-CAPS reads the row back.
  env A1WRT2_STATUS_DIR="$TD" A1WRT2_RUN_ROOT="$TD/prod" \
    bash "${BASH_SOURCE[0]}" --arm SEAM --emit-ledger 186 >/dev/null 2>&1 || true
  if grep -q 'ARM=SEAM .*core_min=3.100' "$TD/prod/ledger.txt" 2>/dev/null; then
    echo "CONTROL producer/ledger-row-is-written  EXERCISED  -> 186 wall_s x 1 rank = 3.100 core-min written to \$RUN_ROOT/ledger.txt"
  else
    echo "CONTROL producer/ledger-row-is-written  NOT EXERCISED  -> $(cat "$TD/prod/ledger.txt" 2>/dev/null | head -1)"; FAILED=1
  fi

  # ==========================================================================
  # `measure_image_pins` IS NOW DRIVEN FOR REAL, AND DRIVING IT IS WHAT FOUND
  # THE TWO DEFECTS ABOVE.  Authorised by the dafoam-supervisor 2026-09-05:
  # "I authorise the measurement rather than the redefinition."
  #
  # Cost: ONE container, ~2 wall s x 1 rank = ~0.033 core-min per selftest run,
  # priced at the c7a.4xlarge owner-stated $0.0513/core-h => ~$0.00003 DERIVED,
  # cost_basis REPORTED-BY-OWNER (CLAUDE.md rule 12; the box cannot read its own
  # billing).  Under the $25 pre-authorisation and costed here anyway.
  # ==========================================================================
  PIN_DIG="sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35"
  PIN_WARP="85f59e87253e0a71a813f64ca6e4c425"

  if docker image inspect "$IMG" >/dev/null 2>&1; then
    GOT_PINS="$(measure_image_pins "$IMG")"
    GOT_DIG="${GOT_PINS% *}"; GOT_WARP="${GOT_PINS#* }"
    if [ "$GOT_DIG" = "$PIN_DIG" ] && [ "$GOT_WARP" = "$PIN_WARP" ]; then
      echo "CONTROL producer/image-pins-measured  EXERCISED-PASS  BOTH pins read OUT OF THE IMAGE and both match: digest=$GOT_DIG libidwarp=$GOT_WARP"
    else
      echo "CONTROL producer/image-pins-measured  EXERCISED-FAIL  measured digest=$GOT_DIG libidwarp=$GOT_WARP against pins $PIN_DIG / $PIN_WARP -- THIS STOPS THE FREEZE"; FAILED=1
    fi
  else
    echo "CONTROL producer/image-pins-measured  NOT EXERCISED  the pinned image $IMG is not present on this box; declared in its third state and never counted as a pass"
  fi

  # -- THE MD5-OF-NOTHING LIMB.  This is the control the 2026-09-04 version could
  #    not have had, because it was the bug: `md5sum` with no operand reads STDIN,
  #    sees EOF, and prints the md5 of the empty string at rc 0, which is
  #    non-empty and so slipped past a `[ -n ... ]` guard.  Driven as a REFUSAL,
  #    through THIS FILE'S OWN classifier and not a copy of it.
  MDN_OUT="$(env A1WRT2_STATUS_DIR="$TD" bash "${BASH_SOURCE[0]}" \
               --arm SEAM --drive-md5-classifier "$MD5_OF_NOTHING")"
  MDN_GOOD="$(env A1WRT2_STATUS_DIR="$TD" bash "${BASH_SOURCE[0]}" \
               --arm SEAM --drive-md5-classifier "$PIN_WARP")"
  if [ "$MDN_OUT" = "UNMEASURED" ] && [ "$MDN_GOOD" = "$PIN_WARP" ]; then
    echo "CONTROL producer/md5-of-nothing-is-UNMEASURED  EXERCISED-FAIL  d41d8cd98f00b204e9800998ecf8427e -- the md5 of the EMPTY STRING -- maps to UNMEASURED, while the real pin $PIN_WARP passes through unchanged.  Both limbs driven, so this is a classifier and not a guard that refuses everything"
  else
    echo "CONTROL producer/md5-of-nothing-is-UNMEASURED  NOT EXERCISED  nothing->$MDN_OUT (want UNMEASURED), pin->$MDN_GOOD (want $PIN_WARP)"; FAILED=1
  fi

  # -- THE REFUSAL ORDERING, BOTH DIRECTIONS.  UNMEASURED must refuse BEFORE the
  #    container (exit 4); measured pins must permit (exit 0).  Without the
  #    second limb this control could not tell a working guard from one that
  #    refuses everything.
  drive "pins/unmeasured-refuses-before-container" 4 \
    env A1WRT2_STATUS_DIR="$TD" bash "${BASH_SOURCE[0]}" --arm SEAM --drive-pin-guard UNMEASURED "$PIN_WARP"
  drive "pins/unmeasured-warp-refuses-before-container" 4 \
    env A1WRT2_STATUS_DIR="$TD" bash "${BASH_SOURCE[0]}" --arm SEAM --drive-pin-guard "$PIN_DIG" UNMEASURED
  drive "pins/measured-pins-permit" 0 \
    env A1WRT2_STATUS_DIR="$TD" bash "${BASH_SOURCE[0]}" --arm SEAM --drive-pin-guard "$PIN_DIG" "$PIN_WARP"

  # -- THE LOADER LINE, ASSERTED BY EXTRACTION OVER THIS FILE'S OWN BYTES.
  #    The defect was a MISSING line, and a missing line is exactly what a
  #    selftest that only drives functions cannot see.
  # The control's own grep line matches the pattern it greps for, so it is
  # EXCLUDED BY NAME.  Without that the count is inflated by one and the
  # threshold passes with one arm body missing the loader -- a control that
  # counts itself is a control with a free pass built in.
  N_LOADER="$(grep "source \$DAFOAM_LOADER" "${BASH_SOURCE[0]}" | grep -cv N_LOADER || true)"
  if [ "$N_LOADER" -eq 3 ]; then
    echo "CONTROL loader/every-container-sources-the-loader  EXERCISED-PASS  exactly $N_LOADER container invocations source $DAFOAM_LOADER, and they are the three that exist: measure_image_pins + both arm bodies (the control excludes its own grep line).  Without it this image reports 'python: command not found' and NO SOLVER STARTS"
  else
    echo "CONTROL loader/every-container-sources-the-loader  NOT EXERCISED  $N_LOADER sites source the loader, expected exactly 3"; FAILED=1
  fi

  # ==========================================================================
  # RULING 1: THE TAIL'S PRECONDITION ON SEAM'S VERDICT, BOTH DIRECTIONS.
  # ==========================================================================
  # An ABSENT SEAM arm must refuse TAIL at 7 -- the case that matters most,
  # because it is the state the run root is in when TAIL would first be
  # launched by hand.
  mkdir -p "$TD/nos"; printf 'ARM=SEAM core_min=3.10\n' > "$TD/nos/ledger.txt"
  drive "seam-precond/absent-seam-refuses-TAIL-at-7" 7 \
    env A1WRT2_STATUS_DIR="$TD" A1WRT2_RUN_ROOT="$TD/nos" bash "${BASH_SOURCE[0]}" --arm TAIL --guards-only

  # -- and the SAME run root must NOT refuse the SEAM arm, because SEAM is the
  #    precondition rather than being subject to it.  Without this limb the
  #    control could not tell a working precondition from a launcher that
  #    refuses everything.
  drive "seam-precond/does-not-gate-the-SEAM-arm" 0 \
    env A1WRT2_STATUS_DIR="$TD" A1WRT2_RUN_ROOT="$TD/nos" bash "${BASH_SOURCE[0]}" --arm SEAM --guards-only

  # -- a CLEAN SEAM arm must PERMIT TAIL.  The happy SEAM tree is built by the
  #    grader's own fixture builder, so the precondition is driven against the
  #    same bytes the grader grades.
  mkdir -p "$TD/ok"; mk_seam "$TD/ok"
  printf 'ARM=SEAM core_min=3.10\n' > "$TD/ok/ledger.txt"
  drive "seam-precond/clean-seam-permits-TAIL" 0 \
    env A1WRT2_STATUS_DIR="$TD" A1WRT2_RUN_ROOT="$TD/ok" bash "${BASH_SOURCE[0]}" --arm TAIL --guards-only

  # -- and a SEAM whose rc is 97 must refuse TAIL at 7, from the same tree.
  echo "97" > "$TD/ok/SEAM/out/rc"
  drive "seam-precond/seam-rc-97-refuses-TAIL-at-7" 7 \
    env A1WRT2_STATUS_DIR="$TD" A1WRT2_RUN_ROOT="$TD/ok" bash "${BASH_SOURCE[0]}" --arm TAIL --guards-only
  echo "0" > "$TD/ok/SEAM/out/rc"

  # -- THE DURABLE ROW ON A PRECONDITION REFUSAL, as for the ceiling limb.
  if grep -q 'note=SEAM_PRECONDITION_REFUSED' "$TD/STATUS.TAIL" 2>/dev/null; then
    echo "CONTROL seam-precond/status-row-durable  EXERCISED  -> STATUS.TAIL carries the refusal outside stdout"
  else
    echo "CONTROL seam-precond/status-row-durable  NOT EXERCISED  -> no row"; FAILED=1
  fi

  if [ "$FAILED" = "0" ]; then
    echo "${ITEM}_RUN_ARM SELFTEST OK -- every guard driven in BOTH directions"
    exit 0
  fi
  echo "${ITEM}_RUN_ARM SELFTEST FAILED"
  exit 1
fi

[ -n "$ARM" ] || usage

# --- THE PRODUCER DRIVE PATHS.  Host only, no container, no solver. ----------
# These exist so the producers written above are DRIVEN rather than merely
# written.  A producer nothing has ever executed is the same class of evidence
# as a gate nothing has ever failed.
if [ "$EMIT_MANIFEST" = "1" ]; then
  write_manifest "$ARM" "$IMG" "${A1WRT2_FAKE_DIGEST:-UNMEASURED}" \
                 "${A1WRT2_FAKE_WARPMD5:-UNMEASURED}"
  exit 0
fi
if [ -n "$EMIT_LEDGER" ]; then
  append_ledger_row "$ARM" 0 "$EMIT_LEDGER" 1 "$(arm_cap "$ARM")"
  exit 0
fi
# The pin guard and the md5 classifier, driven through THE REAL FUNCTIONS.
if [ -n "$DRIVE_MD5" ]; then
  classify_md5 "$DRIVE_MD5"
  exit 0
fi
if [ -n "$DRIVE_PIN_DIG" ]; then
  refuse_unmeasured_pins "$ARM" "$DRIVE_PIN_DIG" "$DRIVE_PIN_WARP"
  exit 0
fi

# --- THE GUARDS RUN BEFORE ANYTHING ELSE, AND BEFORE THE CONTAINER ----------
unbound_guard
ceiling_guard "$ARM"

# RULING 1: the TAIL arm, and ONLY the TAIL arm, is gated on SEAM's verdict.
# SEAM carries no such precondition -- it IS the precondition.
if [ "$ARM" = "TAIL" ]; then
  seam_precondition_guard
fi

if [ "$GUARDS_ONLY" = "1" ]; then
  echo "${ITEM}_GUARDS_ONLY -- guards driven, nothing launched"
  exit 0
fi

if [ "$LAUNCH_ENABLED" != "1" ]; then
  echo "${ITEM}_NOT_LAUNCHING -- LAUNCH_ENABLED=0."
  echo "  This item is NOT FROZEN, NOT PINNED and NOT ENQUEUED, and its"
  echo "  pre-registration is a DRAFT with no evidentiary force.  Draft"
  echo "  section 11 lists four things owed before the freeze and three more"
  echo "  before the enqueue, including the dafoam-supervisor's own"
  echo "  SUPERVISION_CHARTER section 3 checks 1 and 4, which are NOT"
  echo "  DELEGABLE and which no lane may perform on the supervisor's behalf."
  echo "  Enqueueing is not authorisation and no lane launches this item."
  exit 0
fi

# =============================================================================
# THE ARM BODIES.  UNREACHABLE WHILE `LAUNCH_ENABLED=0`, AND WRITTEN ANYWAY,
# BECAUSE THEY ARE THE PRODUCERS THE GATES' INPUTS ARE TRACED TO.
#
# `a1wrt2_grade.read_text` REFUSES at exit 2 on an absent artefact, so a
# product these bodies have not yet created can never read as a passing gate --
# it reads as a refusal.  That is what makes writing the producer and not
# running it an honest state rather than a hole.
#
# The two bodies are spelled out separately, with LITERAL paths, for the
# reasons at `MANIFEST_PATH` above.
# =============================================================================
# ⚠ EVERY CONTAINER BELOW SOURCES `loadDAFoam.sh`, AND THAT LINE IS THE SECOND
# DEFECT THE 2026-09-05 PIN MEASUREMENT EXPOSED.  The 2026-09-04 arm bodies ran
#
#     "$IMG" /bin/bash -lc 'cd /mnt && python /run_root/runScript.py -task sweep'
#
# with NO loader sourced.  Driving `measure_image_pins` for the first time
# returned `python: command not found` from a login shell on this image -- and
# the arm bodies had the SAME shape, so THE SOLVER WOULD NEVER HAVE STARTED.
# Both arms would have written an empty `sweep.log`, propagated a non-zero rc
# and produced no point at all.  `A1WRT` U1 ran because `a1wrt_run_unit.sh:675`
# sources the loader; this successor dropped that line.
#
# MEASURED, 2026-09-05: with the loader sourced, `python` resolves and the
# in-process md5 returns `85f59e87253e0a71a813f64ca6e4c425`, exactly the pin.
# Without it, `/bin/sh` AND `/bin/bash -lc` both report `command not found`.
run_seam_arm() {
  local rc t0 t1
  mkdir -p "$SEAM_OUT"
  DIG_WARP="$(measure_image_pins "$IMG")"
  refuse_unmeasured_pins SEAM "${DIG_WARP% *}" "${DIG_WARP#* }"
  write_manifest SEAM "$IMG" "${DIG_WARP% *}" "${DIG_WARP#* }"
  t0="$(date +%s)"
  set +e
  timeout 900 docker run --rm --user 0:0 --cpuset-cpus="0" --memory=8g \
    -e OMP_NUM_THREADS=1 -v "$SEAM_CASE:/mnt" -v "$RUN_ROOT:/run_root" \
    "$IMG" /bin/bash -lc "source $DAFOAM_LOADER && cd /mnt && python /run_root/runScript.py -task sweep" \
    > "$SEAM_OUT/sweep.log" 2>&1
  rc=$?
  set -e
  # THE PRODUCER'S OWN rc, PROPAGATED, NEVER RECOMPUTED FROM MARKERS.  This is
  # the `a1wr_cmd.sh:96-102` defect (draft section 4.1) refused by construction:
  # that file decides its unit's status from `grep -c '^AOA_POINT_END '`, which
  # counts a CRASHED point too, and so exited 0 over its own producer's rc=97.
  echo "$rc" > "$SEAM_OUT/rc"
  t1="$(date +%s)"
  append_ledger_row SEAM "$rc" "$((t1 - t0))" 1 "$(arm_cap SEAM)"
  return 0
}

run_tail_arm() {
  local rc t0 t1
  mkdir -p "$TAIL_OUT"
  DIG_WARP="$(measure_image_pins "$IMG")"
  refuse_unmeasured_pins TAIL "${DIG_WARP% *}" "${DIG_WARP#* }"
  write_manifest TAIL "$IMG" "${DIG_WARP% *}" "${DIG_WARP#* }"
  t0="$(date +%s)"
  set +e
  timeout 40500 docker run --rm --user 0:0 --cpuset-cpus="0" --memory=8g \
    -e OMP_NUM_THREADS=1 -v "$TAIL_CASE:/mnt" -v "$RUN_ROOT:/run_root" \
    "$IMG" /bin/bash -lc "source $DAFOAM_LOADER && cd /mnt && python /run_root/runScript.py -task sweep" \
    > "$TAIL_OUT/sweep.log" 2>&1
  rc=$?
  set -e
  echo "$rc" > "$TAIL_OUT/rc"
  t1="$(date +%s)"
  append_ledger_row TAIL "$rc" "$((t1 - t0))" 1 "$(arm_cap TAIL)"
  return 0
}

case "$ARM" in
  SEAM) run_seam_arm ;;
  TAIL) run_tail_arm ;;
  *)    usage ;;
esac
exit 0
