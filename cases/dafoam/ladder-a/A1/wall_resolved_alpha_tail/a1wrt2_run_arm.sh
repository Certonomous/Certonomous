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
ITEM_CEILING_CORE_MIN=685.0
CEIL_TOL=0.02               # d6rf's float-noise tolerance
BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUN_ROOT="${A1WRT2_RUN_ROOT:-/home/ubuntu/certonomous-runs/A1WRT2}"
LEDGER="$RUN_ROOT/ledger.txt"
# STATUS rows are written under STATUS_DIR so the selftest can drive the
# durable-row limb without writing into the committed case directory.
STATUS_DIR="${A1WRT2_STATUS_DIR:-$BASE}"
STATUS="$STATUS_DIR/STATUS.$ITEM"

usage() { echo "usage: $0 --arm {SEAM|TAIL} [--selftest]" >&2; exit 64; }

ARM=""
SELFTEST=0
while [ $# -gt 0 ]; do
  case "$1" in
    --arm)         ARM="${2:-}"; shift 2 ;;
    --selftest)    SELFTEST=1; shift ;;
    --guards-only) GUARDS_ONLY=1; shift ;;
    *)             usage ;;
  esac
done
GUARDS_ONLY="${GUARDS_ONLY:-0}"

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

# ---- SELFTEST: both guards driven in BOTH directions, on static fixtures ---
if [ "$SELFTEST" = "1" ]; then
  echo "${ITEM}_RUN_ARM SELFTEST -- host shell, NO container, NO compute"
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

  # -- ceiling: REFUSE at 6.  A fixture ledger summing 680.0 with TAIL's 675.0
  #    cap projects 1355.0 > 685.0.
  mkdir -p "$TD/over"; printf 'ITEM=A1WRT2\nARM=SEAM core_min=680.0\n' > "$TD/over/ledger.txt"
  drive "ceiling/over-refuses-at-6" 6 \
    env A1WRT2_STATUS_DIR="$TD" A1WRT2_RUN_ROOT="$TD/over" bash "${BASH_SOURCE[0]}" --arm TAIL --guards-only

  # -- ceiling: PASS and PRINT THE CENSUS.  3.10 + 675.0 = 678.10 <= 685.0.
  mkdir -p "$TD/under"; printf 'ITEM=A1WRT2\nARM=SEAM core_min=3.10\n' > "$TD/under/ledger.txt"
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

  if [ "$FAILED" = "0" ]; then
    echo "${ITEM}_RUN_ARM SELFTEST OK -- every guard driven in BOTH directions"
    exit 0
  fi
  echo "${ITEM}_RUN_ARM SELFTEST FAILED"
  exit 1
fi

[ -n "$ARM" ] || usage

# --- BOTH GUARDS RUN BEFORE ANYTHING ELSE, AND BEFORE THE CONTAINER ---------
unbound_guard
ceiling_guard "$ARM"

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

echo "unreachable while LAUNCH_ENABLED=0" >&2
exit 70
