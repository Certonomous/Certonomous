#!/bin/bash
# =============================================================================
# W3S ARM A (`GSCAN`) CHAIN DRIVER.
#
# IT IS INERT ON PURPOSE.  `W3S_PREREGISTRATION_DRAFT.md` is UNFROZEN and carries no
# committed sha, and `w3s_stage_and_run.sh` HAS NOT BEEN WRITTEN.  This driver therefore
# ABORTS before it does anything, at PREFLIGHT 0, and it aborts because the freeze is
# missing rather than because a path is missing -- a driver that would launch as soon as
# a launcher appeared beside it is a driver that launches on a filesystem accident.
# Under `SUPERVISION_CHARTER.md` sec.3 check 4 the *pre-registration committed before
# compute* check is the supervisor's own and may not be delegated; this file cannot
# discharge it and does not try to.
#
# WHAT IT IS FOR: the CUMULATIVE ITEM-CEILING GUARD, asserted before EVERY leg.
#
# THE TWO PARENTS, AND WHY ONLY ONE OF THEM IS THE PRIMARY.
#   `a1wrt_run_unit.sh:297-305` IS THE PRIMARY.  It is the only guard in this family that
#   refuses on an UNMEASURED prior spend instead of assuming zero, and its own words are
#   the reason: "A zero that means 'could not read' is a planted zero (CLAUDE.md rule 3)."
#   `d6rf_chain_driver.sh:155-170` CONTRIBUTES ITS PROJECTION ARITHMETIC ONLY -- the
#   comparison of (spend-to-date + THIS leg's cap) against the item ceiling BEFORE the leg
#   runs, and `exit 6`.  ITS SPEND READER IS NOT PORTED, AND THAT IS DELIBERATE:
#     (i)  `d6rf_chain_driver.sh:140-141` catches `IOError` and falls through to `0.0`, so
#          a missing or unreadable ledger reads as "nothing has been spent" -- a planted
#          zero in the guard's own input;
#     (ii) its `[0-9.]+` matches `1.2` out of a malformed `core_min=1.2.3`, and the
#          `ValueError` from a token it cannot float is NOT caught at all, so `$SPENT`
#          comes back EMPTY, `$PROJ` becomes empty, the comparison fails and the `if`
#          evaluates false.  THE GUARD FAILS OPEN.
#   So the reader is written fresh, in `w3s_grade.py::spend_from_root`, where it is inside
#   the AST-audited instrument and driven by `--selftest` under `python3` and `python3 -O`.
#   It returns the token UNMEASURED on ANY read or parse failure and NEVER 0.0, and this
#   driver refuses on UNMEASURED.
#
# THREE MORE LIMBS NEITHER PARENT HAS, each driven in `w3s_grade.py --selftest`:
#   - a run root that EXISTS with stage logs and has NO ledger is UNMEASURED, not zero
#     (a1wrt reads a missing ledger as 0.0 unconditionally);
#   - a ledger that exists with ZERO spend rows beside stage logs is UNMEASURED;
#   - the registered leg caps are checked to SUM WITHIN the registered item ceiling before
#     any leg runs -- a registration whose parts exceed its whole is found here or nowhere.
#   And the FRESH case is kept separate from all of them: no root AND no ledger is 0.000,
#   because a blanket refusal on an absent ledger makes a first leg unlaunchable forever.
#
# THE SPEND READER SHIPS ITS OWN PLANT (GA-P3).  Before any census is believed, the reader
# is handed a fixture ledger carrying a known core_min and must return it, and is shown
# returning UNMEASURED in three named directions.  A zero from a reader not shown able to
# see a non-zero is not evidence -- and this particular zero would be read as HEADROOM.
#
# NOTHING HERE IS FILED, SENT OR UPLOADED (CLAUDE.md rule 7).  SUBMISSIONS REMAIN PARKED.
# =============================================================================
set -u

BASE="$(cd "$(dirname "$0")" && pwd)"
GRADER="$BASE/w3s_grade.py"
LAUNCHER="$BASE/w3s_stage_and_run.sh"
PARENT="$BASE/d12y_grade_w3.py"

# ---- PINS.  Bumped IN THE SAME COMMIT as the files they pin (the D8R-DRIVER-DEF-1 /
# ---- 2026-08-28T02:15:29Z death: a driver whose pins lag its instruments by one commit
# ---- aborts every run and blames the wrong file).
MD5_PARENT="3950d30fd09c9b56213a02f5e9864e20"
MD5_GRADER="d24d632cd37f587ebaca7999d9088dec"
MD5_LAUNCHER="NOT_WRITTEN"

# ---- THE FREEZE.  Empty until `dafoam-supervisor` freezes W3S_PREREGISTRATION_DRAFT.md
# ---- and records the sha here, IN THE FREEZE COMMIT.  Empty means this driver refuses.
PREREG_COMMIT=""
PREREG_FILE="$BASE/W3S_PREREGISTRATION_DRAFT.md"

# ---- REGISTERED, and echoed by the grader so the two cannot drift apart silently.
ITEM_CEILING_CORE_MIN="330.0"
LEGS="SETUP A0 A1 A2"
ROOT_ARM_A="/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3S-GSCAN-cylinder-unsteady"

SELFCHECK=0
[ "${1:-}" = "--selfcheck" ] && SELFCHECK=1

say() { echo "W3S_DRIVER $*"; }

# -----------------------------------------------------------------------------
# PREFLIGHT 0 -- THE FREEZE.  First, and unconditional.
# -----------------------------------------------------------------------------
preflight_freeze() {
  if [ -z "$PREREG_COMMIT" ]; then
    say "ABORT NOT_FROZEN: PREREG_COMMIT is empty. $PREREG_FILE carries no committed sha,"
    say "  so no gate, threshold, cap or label in it is frozen (CLAUDE.md rule 2). The"
    say "  pre-registration-committed-before-compute check is the supervisor's own and may"
    say "  not be delegated (SUPERVISION_CHARTER.md sec.3 check 4). NOTHING LAUNCHES."
    return 70
  fi
  if ! git -C "$BASE" cat-file -e "${PREREG_COMMIT}:cases/dafoam/curriculum_D12R2/$(basename "$PREREG_FILE")" 2>/dev/null; then
    say "ABORT FREEZE_UNVERIFIABLE: $PREREG_COMMIT does not carry the pre-registration blob."
    return 70
  fi
  return 0
}

# -----------------------------------------------------------------------------
# PREFLIGHT 1 -- INSTRUMENT IDENTITY.  A version string is not an identity
# (DAFOAM_CHARTER.md sec.6); an md5 is.
# -----------------------------------------------------------------------------
preflight_instruments() {
  local rc=0
  for pair in "$PARENT:$MD5_PARENT" "$GRADER:$MD5_GRADER"; do
    local f="${pair%:*}" want="${pair##*:}"
    if [ ! -f "$f" ]; then say "ABORT MISSING_INSTRUMENT $f"; rc=4; continue; fi
    local got; got=$(md5sum "$f" | cut -d' ' -f1)
    if [ "$got" != "$want" ]; then
      say "ABORT MD5_DRIFT $(basename "$f") is $got, pinned $want"; rc=4
    fi
  done
  if [ ! -f "$LAUNCHER" ]; then
    say "ABORT LAUNCHER_NOT_WRITTEN: $LAUNCHER does not exist. Arm A's 6-stage graph has"
    say "  not been built, so there is nothing to drive."
    rc=4
  fi
  return $rc
}

# -----------------------------------------------------------------------------
# THE CUMULATIVE ITEM-CEILING GUARD.  Asserted BEFORE every leg.
# The reader, the UNMEASURED token, the plant and the projection all live in the
# grader, where they are AST-audited and driven under `python3` and `python3 -O`.
# Its exit codes ARE this function's contract:  0 ok | 6 ceiling/already-bought
# | 64 registration inconsistent | 65 UNMEASURED prior spend.
# -----------------------------------------------------------------------------
ceiling_guard() {
  local leg="$1"; shift
  local out rc
  out=$(python3 "$GRADER" --cumulative-item-ceiling --leg "$leg" "$@" \
        --tmpdir "${TMPDIR:-/tmp}" 2>&1); rc=$?
  case "$rc" in
    0)  say "CEILING leg=$leg OK $(printf '%s' "$out" | python3 -c 'import json,sys; print(json.load(sys.stdin)["reason"])' 2>/dev/null)" ;;
    6)  say "ABORT ITEM_CEILING leg=$leg -- an overrun STOPS the run; it does not get a new budget (rule 12)"
        printf '%s\n' "$out" ;;
    64) say "ABORT REGISTRATION_INCONSISTENT leg=$leg -- the registered caps do not fit the ceiling"
        printf '%s\n' "$out" ;;
    65) say "ABORT UNMEASURED leg=$leg -- prior spend could not be measured, so it is not assumed zero"
        printf '%s\n' "$out" ;;
    *)  say "ABORT CEILING_GUARD_ITSELF_FAILED leg=$leg rc=$rc"
        printf '%s\n' "$out"; rc=65 ;;
  esac
  return $rc
}

# -----------------------------------------------------------------------------
# --selfcheck : drive every guard at ZERO COMPUTE, in BOTH directions.
# A guard shown only passing has not been shown to be a guard (L-314).
# -----------------------------------------------------------------------------
selfcheck() {
  local n=0 bad=0
  unit() { n=$((n+1)); if [ "$2" = "1" ]; then echo "  [OK ] $1"; else echo "  [BAD] $1"; bad=$((bad+1)); fi; }

  local rc
  preflight_freeze >/dev/null 2>&1; rc=$?
  unit "S1 PREFLIGHT 0 REFUSES while PREREG_COMMIT is empty (rc=70, NOT_FROZEN)" \
       "$( [ $rc -eq 70 ] && echo 1 || echo 0 )"
  preflight_instruments >/dev/null 2>&1; rc=$?
  unit "S2 PREFLIGHT 1 REFUSES while $(basename "$LAUNCHER") is not written (rc=4)" \
       "$( [ $rc -eq 4 ] && echo 1 || echo 0 )"

  local d; d=$(mktemp -d)
  # ---- the FRESH direction: a root that does not exist yet costs nothing.
  ceiling_guard A0 --root "$d/never_created" >/dev/null 2>&1; rc=$?
  unit "S3 CEILING a FRESH root -> rc=0 (a blanket refusal on an absent ledger would make a first leg unlaunchable forever)" \
       "$( [ $rc -eq 0 ] && echo 1 || echo 0 )"
  # ---- the UNMEASURED direction: a root with stage logs and no ledger.
  mkdir -p "$d/noledger"; : > "$d/noledger/S5_x.log"
  ceiling_guard A0 --root "$d/noledger" >/dev/null 2>&1; rc=$?
  unit "S4 CEILING a root with stage logs and NO ledger -> rc=65 UNMEASURED, not 0.0" \
       "$( [ $rc -eq 65 ] && echo 1 || echo 0 )"
  # ---- the MALFORMED-TOKEN direction: the one that makes d6rf's guard fail OPEN.
  mkdir -p "$d/malformed"
  echo "STAGE=S5 rc=0 core_min=1.2.3 memavail_GiB=20.0" > "$d/malformed/ledger.txt"
  ceiling_guard A0 --root "$d/malformed" >/dev/null 2>&1; rc=$?
  unit "S5 CEILING a malformed core_min=1.2.3 -> rc=65 UNMEASURED (d6rf reads 1.2, then its uncaught ValueError empties \$SPENT and the guard passes)" \
       "$( [ $rc -eq 65 ] && echo 1 || echo 0 )"
  # ---- the PROJECTION direction: healthy ledger, projection over the ceiling.
  mkdir -p "$d/over"
  echo "STAGE=S5 rc=0 core_min=200.0 memavail_GiB=20.0" > "$d/over/ledger.txt"
  ceiling_guard A2 --root "$d/over" >/dev/null 2>&1; rc=$?
  unit "S6 CEILING 200.0 spent + leg A2 cap 155.0 = 355.0 > ceiling $ITEM_CEILING_CORE_MIN -> rc=6" \
       "$( [ $rc -eq 6 ] && echo 1 || echo 0 )"
  # ---- the HAPPY direction, so the battery is not a battery of refusals.
  mkdir -p "$d/ok"
  echo "STAGE=S0 rc=0 core_min=1.750 memavail_GiB=20.0" > "$d/ok/ledger.txt"
  ceiling_guard A1 --root "$d/ok" >/dev/null 2>&1; rc=$?
  unit "S7 CEILING 1.750 spent + leg A1 cap 70.0 <= ceiling -> rc=0 (the guard is not merely refusing everything)" \
       "$( [ $rc -eq 0 ] && echo 1 || echo 0 )"
  # ---- CUMULATIVE ACROSS ROOTS, which is the whole point of an item ceiling.
  ceiling_guard A2 --root "$d/ok" --root "$d/over" >/dev/null 2>&1; rc=$?
  unit "S8 CEILING spend sums ACROSS roots: 1.750 + 200.0 + 155.0 > ceiling -> rc=6" \
       "$( [ $rc -eq 6 ] && echo 1 || echo 0 )"
  # ---- the guard's own instrument identity.
  local got; got=$(md5sum "$GRADER" | cut -d' ' -f1)
  unit "S9 the grader on disk is the pinned $MD5_GRADER" \
       "$( [ "$got" = "$MD5_GRADER" ] && echo 1 || echo 0 )"
  got=$(md5sum "$PARENT" | cut -d' ' -f1)
  unit "S10 the FROZEN parent is UNEDITED at $MD5_PARENT (CLAUDE.md rule 6)" \
       "$( [ "$got" = "$MD5_PARENT" ] && echo 1 || echo 0 )"

  rm -rf "$d"
  echo "W3S DRIVER SELFCHECK units=$n failures=$bad"
  [ "$bad" -eq 0 ] || return 2
  echo "W3S DRIVER SELFCHECK PASS $n/$n"
  return 0
}

if [ "$SELFCHECK" = "1" ]; then
  selfcheck; exit $?
fi

# =============================================================================
# THE CHAIN.  Never reached today: PREFLIGHT 0 refuses.
# =============================================================================
say "start stamp=$(date -u +%Y%m%dT%H%M%SZ) pid=$$ base=$BASE"
preflight_freeze || exit $?
preflight_instruments || exit $?

for LEG in $LEGS; do
  ceiling_guard "$LEG" --root "$ROOT_ARM_A" || exit $?
  say "leg=$LEG would launch here; the launcher is written and pinned before this line runs"
  "$LAUNCHER" --leg "$LEG" --root "$ROOT_ARM_A" || exit $?
done
say "chain complete stamp=$(date -u +%Y%m%dT%H%M%SZ)"
