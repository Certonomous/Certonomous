#!/bin/bash
# =============================================================================
# W3S ARM A (`GSCAN`) CHAIN DRIVER.
#
# IT IS INERT ON PURPOSE.  `W3S_PREREGISTRATION_DRAFT.md` is UNFROZEN and carries no
# committed sha, so this driver ABORTS at PREFLIGHT 0 before it does anything.
#
# UPDATED 2026-09-04: `w3s_stage_and_run.sh` IS NOW WRITTEN, and so is the record producer
# `w3s_stage_record.py` it executes.  The header above used to say the launcher did not
# exist; that sentence is now FALSE and is replaced rather than left standing, because a
# stale claim in a driver's own first screen is exactly what a reader trusts.  THE DRIVER
# IS STILL INERT, and it is inert for TWO INDEPENDENT REASONS, either of which alone
# stops it:
#   (1) PREFLIGHT 0 here -- `PREREG_COMMIT` is empty, so nothing is frozen (rule 2);
#   (2) `LAUNCH_ENABLED=0` in the launcher, which no lane may raise.
# It aborts because the FREEZE is missing rather than because a path is missing -- a
# driver that would launch as soon as a launcher appeared beside it is a driver that
# launches on a filesystem accident.  Under `SUPERVISION_CHARTER.md` sec.3 check 4 the
# *pre-registration committed before compute* check is the supervisor's own and may not
# be delegated; this file cannot discharge it and does not try to.
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
RECORD="$BASE/w3s_stage_record.py"
PARENT="$BASE/d12y_grade_w3.py"
PARENT_LAUNCHER="$BASE/d12y_w3_stage_and_run.sh"
RUNPY="$BASE/d12y_run_script.py"
CEILING_GUARD="$BASE/../_common/item_ceiling_guard.py"

# ---- PINS.  Bumped IN THE SAME COMMIT as the files they pin (the D8R-DRIVER-DEF-1 /
# ---- 2026-08-28T02:15:29Z death: a driver whose pins lag its instruments by one commit
# ---- aborts every run and blames the wrong file).
#
# THE ENUMERATION IS OVER WHAT IS EXECUTED, NOT OVER WHAT LOOKS LIKE AN INSTRUMENT
# (DAFOAM_CHARTER.md sec.18.3).  `w3s_stage_and_run.sh` executes `w3s_stage_record.py`,
# `../_common/item_ceiling_guard.py`, `d12y_run_script.py` and -- through the record
# producer -- reads the FATAL token list out of `d12y_w3_stage_and_run.sh`.  All six are
# checked for EXISTENCE FIRST and SEPARATELY, before any md5, because an md5-agreement
# control over a subset can read agreement on every pin it holds while a dependency the
# frozen code executes is absent: SO2a froze a memory gate whose implementing script was
# not in the freeze commit and its own control still read `eight of eight AGREE`.
MD5_PARENT="3950d30fd09c9b56213a02f5e9864e20"
MD5_PARENT_LAUNCHER="8a92f3f84f72d6806a2e5c5df88d82ef"
MD5_RUNPY="2790c39a09cd458d5a3263d7f1811da5"
MD5_GRADER="d24d632cd37f587ebaca7999d9088dec"
MD5_RECORD="8ee3b0ad9b8dfe113f83f1a145f6431b"
MD5_LAUNCHER="02e00e3d420abb34b8e9d9eb6b933831"

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
  local rc=0 f pair want got
  # ---- (1) EXISTENCE, over EVERY file this driver or its launcher EXECUTES or IMPORTS,
  # ---- including the ones that carry no md5 pin.  Asked FIRST and asked SEPARATELY.
  for f in "$PARENT" "$PARENT_LAUNCHER" "$RUNPY" "$GRADER" "$RECORD" "$LAUNCHER" \
           "$CEILING_GUARD"; do
    if [ ! -f "$f" ]; then
      say "ABORT MISSING_INSTRUMENT $f -- a file the chain EXECUTES or IMPORTS is not on"
      say "  disk. Existence is asserted BEFORE any md5 (DAFOAM_CHARTER.md sec.18.3)."
      rc=4
    fi
  done
  [ "$rc" -eq 0 ] || return $rc
  # ---- (2) ONLY THEN, the md5s.
  for pair in "$PARENT:$MD5_PARENT" "$PARENT_LAUNCHER:$MD5_PARENT_LAUNCHER" \
              "$RUNPY:$MD5_RUNPY" "$GRADER:$MD5_GRADER" "$RECORD:$MD5_RECORD" \
              "$LAUNCHER:$MD5_LAUNCHER"; do
    f="${pair%:*}"; want="${pair##*:}"
    got=$(md5sum "$f" | cut -d' ' -f1)
    if [ "$want" = "PIN_AT_FREEZE" ]; then
      say "PIN_UNSET $(basename "$f") md5=$got -- the pin is set IN THE FREEZE COMMIT,"
      say "  in the same commit as the file it pins. Until then PREFLIGHT 0 refuses and"
      say "  nothing reaches this line on a launch path."
      rc=4
      continue
    fi
    if [ "$got" != "$want" ]; then
      say "ABORT MD5_DRIFT $(basename "$f") is $got, pinned $want"; rc=4
    fi
  done
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
  # THE CONTROL THAT USED TO STAND HERE PROVED PREFLIGHT 1 REFUSES A MISSING LAUNCHER.
  # Writing the launcher REMOVED ITS PREMISE, so it is replaced rather than left standing
  # on a condition that can no longer occur -- a control whose premise is gone is a
  # control that cannot fail, and a green from one means nothing.
  unit "S2 PREFLIGHT 1 PASSES: 7 executed files present, 6 pins agree (rc=0)" \
       "$( [ $rc -eq 0 ] && echo 1 || echo 0 )"
  local f_present=1
  for f in "$PARENT" "$PARENT_LAUNCHER" "$RUNPY" "$GRADER" "$RECORD" "$LAUNCHER" \
           "$CEILING_GUARD"; do
    [ -f "$f" ] || f_present=0
  done
  unit "S2b every file the chain EXECUTES or IMPORTS is on disk (7 of 7, existence asked before any md5)" \
       "$f_present"
  # THE NEGATIVE DIRECTION IS DRIVEN WHERE IT BELONGS, and it is named here rather than
  # duplicated badly: `w3s_stage_and_run.sh --selftest` drives BOTH pin directions against
  # mutated copies of itself -- `PINS-PLANT-a-drifted-md5-REFUSES-rc4` and
  # `PINS-PLANT-an-ABSENT-executed-file-REFUSES-rc4` -- so the existence-before-md5 rule
  # has been shown able to refuse.  This driver checks the same seven files with the same
  # ordering; it does not re-plant the same control in a second place.
  bash "$LAUNCHER" --selftest >/dev/null 2>&1; rc=$?
  unit "S2c the LAUNCHER's own selftest passes (47 controls, both pin directions planted, 0 NOT EXERCISED)" \
       "$( [ $rc -eq 0 ] && echo 1 || echo 0 )"
  python3 "$RECORD" --selftest >/dev/null 2>&1; rc=$?
  unit "S2d the RECORD PRODUCER's selftest passes under python3" \
       "$( [ $rc -eq 0 ] && echo 1 || echo 0 )"
  python3 -O "$RECORD" --selftest >/dev/null 2>&1; rc=$?
  unit "S2e the RECORD PRODUCER's selftest passes under python3 -O (a guard that vanishes under a flag is not a guard)" \
       "$( [ $rc -eq 0 ] && echo 1 || echo 0 )"
  python3 "$RECORD" --producer-trace >/dev/null 2>&1; rc=$?
  unit "S2f every artefact key the FROZEN comparator reads has a producer in the registered set" \
       "$( [ $rc -eq 0 ] && echo 1 || echo 0 )"

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
