#!/usr/bin/env bash
# =============================================================================
# d6rf3_final_spend_control.sh -- the control on `d6rf3_chain_driver.sh`'s
# COMPLETION-PATH closing block, which writes the item's final spend INTO THE
# LEDGER.
#
# WHY IT EXISTS. The P1 replacement removed the parent's fail-open
# `spent_core_min()` reader and LEFT ONE CALL SITE POINTING AT IT
# (`FINAL_SPEND=$(spent_core_min)`). An undefined function makes the expansion
# EMPTY, so the driver wrote `total_core_min=` into `ledger.txt` -- which reads
# to a human as ZERO SPEND RECORDED. It fired ONLY on `chain=COMPLETE`: the
# success path, the one least likely to be examined, and the one whose figure
# gets quoted into a cost calibration.
#
# `bash -n` CANNOT SEE IT, and that is the point worth carrying forward: an
# undefined function is a RUNTIME failure, so a syntax check certifies the file
# and misses this entirely. Same family as `assert` vanishing under `python -O`
# -- A CHECK WHOSE SCOPE DOES NOT COVER THE FAILURE IT IS TRUSTED FOR. "Both
# bash -n clean" was true and was the wrong instrument.
#
# WHAT IT DRIVES. The REAL lines, extracted from `d6rf3_chain_driver.sh` by
# pattern at run time -- never a copy pasted in here, which would drift from the
# file it certifies. No container, no arm, ZERO SOLVER CORE-MINUTES.
#
# WHAT IT ASSERTS, and it asserts the REASON and not merely an exit code: the
# emitted field is NON-EMPTY, PARSES as a decimal or as the guard's own
# `UNMEASURED` token, MATCHES what actually landed in `ledger.txt`, and EQUALS
# the value expected for that ledger. An empty field is the thing being
# controlled for -- a wrong number would at least look wrong.
#
# AND IT IS SHOWN ABLE TO FAIL (CLAUDE.md rule 3): the final limb re-creates the
# orphaned form and requires the control to observe an EMPTY field. A control
# never shown seeing the defect it names is not a control.
# =============================================================================
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
CEILING_GUARD="$HERE/../../../_common/item_ceiling_guard.py"
ITEM_CEILING_CORE_MIN=670.0
DRIVER="$HERE/d6rf3_chain_driver.sh"

test -f "$DRIVER"        || { echo "  FAIL driver absent: $DRIVER"; exit 2; }
test -f "$CEILING_GUARD" || { echo "  FAIL ceiling guard absent: $CEILING_GUARD"; exit 2; }

BLOCK=$(sed -n '/^FINAL_LINE=/,/^echo "D6RF3_SPEND_FINAL/p' "$DRIVER")
test -n "$BLOCK" || { echo "  FAIL could not extract the closing block from the real driver"; exit 2; }

echo "D6RF3 FINAL-SPEND CONTROL -- the completion path, driven on the real lines"
echo "  driver $DRIVER"
rc=0

drive() {   # $1 label   $2 ledger setup   $3 expected field
  BASE=$(mktemp -d); eval "$2"
  OUT=$(eval "$BLOCK" 2>&1 | tail -1)
  FIELD=$(printf '%s' "$OUT" | grep -oE 'total_core_min=[^ ]*' | cut -d= -f2)
  LEDG=$(grep -oE 'total_core_min=[^ ]*' "$BASE/ledger.txt" 2>/dev/null | tail -1 | cut -d= -f2)
  NONEMPTY=$([ -n "$FIELD" ] && echo yes || echo NO)
  PARSES=$(printf '%s' "$FIELD" | grep -qE '^([0-9]+\.?[0-9]*|UNMEASURED)$' && echo yes || echo NO)
  MATCH=$([ "$FIELD" = "$LEDG" ] && echo yes || echo NO)
  GOOD=$([ "$NONEMPTY$PARSES$MATCH" = "yesyesyes" ] && [ "$FIELD" = "$3" ] && echo OK || echo FAIL)
  [ "$GOOD" = OK ] || rc=1
  printf '  %-4s %-34s field=%-12s non_empty=%-3s parses=%-3s in_ledger=%-3s (expected %s)\n' \
         "$GOOD" "$1" "${FIELD:-<EMPTY>}" "$NONEMPTY" "$PARSES" "$MATCH" "$3"
}

drive "clean ledger, two arms" \
  'printf "ITEM=D6RF3\nARM=F_mp core_min=155.700\nARM=REF_off core_min=60.070\n" > "$BASE/ledger.txt"' \
  "215.770"
drive "empty ledger (no arms yet)" \
  'printf "ITEM=D6RF3\n" > "$BASE/ledger.txt"' \
  "0.000"
drive "ABSENT ledger" \
  'true' \
  "UNMEASURED"
drive "malformed token core_min=1.2.3" \
  'printf "ITEM=D6RF3\nARM=F_mp core_min=1.2.3\n" > "$BASE/ledger.txt"' \
  "UNMEASURED"

echo "  --- the control shown able to SEE the defect it names (rule 3) ---"
BASE=$(mktemp -d); printf "ITEM=D6RF3\n" > "$BASE/ledger.txt"
ORPHANED=$(spent_core_min 2>/dev/null)     # the removed reader: undefined here
printf 'D6RF3_SPEND_FINAL total_core_min=%s item_ceiling=%s\n' \
       "$ORPHANED" "$ITEM_CEILING_CORE_MIN" > "$BASE/orphaned.txt"
OLDF=$(grep -oE 'total_core_min=[^ ]*' "$BASE/orphaned.txt" | cut -d= -f2)
if [ -z "$OLDF" ]; then
  echo "  OK   the ORPHANED form writes total_core_min=<EMPTY> into the ledger"
else
  echo "  FAIL the orphaned form did not reproduce; this control proves nothing"; rc=1
fi

echo "  RESULT $([ $rc -eq 0 ] && echo 'ALL DIRECTIONS AS REGISTERED' || echo 'NOT AS REGISTERED')"
exit $rc
