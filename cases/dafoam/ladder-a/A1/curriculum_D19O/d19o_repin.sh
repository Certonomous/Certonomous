#!/usr/bin/env bash
# ===========================================================================
# Curriculum D19O -- SET THE FROZEN PINS, ALL OF THEM, IN ONE PASS.
#
# WHY ALL AT ONCE, AND WHY THE SENTINEL IS DELETED RATHER THAN LEFT DEFINED.
# `curriculum_SO3/PREREGISTRATION.md` section 7: a pin table filled in for the
# files that happen to exist, INSIDE THE EXECUTABLE THAT STAGES EVERY ARM, would
# read agreement on every pin it holds while a file that launcher copies is still
# missing.  And a fail-closed sentinel of 32 zeros is a WELL-FORMED md5, so a
# dead sentinel left in place would be counted as a real pin by a completeness
# check -- a fail-open waiting to be re-used.  Here the sentinels are the literal
# strings `MD5_*_UNSET`, which are NOT well-formed md5s, so `md5sum -c` cannot
# accept one by accident and the driver refuses on the literal before it even
# tries.
#
#   d19o_repin.sh              -- set the pins and print the table
#   d19o_repin.sh --verify     -- recompute and compare; change nothing
#
# THE PINS ARE VERIFIED THREE WAYS at the freeze, as the pre-registration's
# section 7 records: on disk, from the committed blob at HEAD, and from the blob
# at the pre-registration commit.  This script does the first; the other two are
# done in the commit's own shell invocation and pasted into section 7.
# ===========================================================================
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
DRIVER="$HERE/d19o_chain_driver.sh"
LAUNCHER="$HERE/d19o_run_arm.sh"
VERIFY=no
case "${1:-}" in --verify) VERIFY=yes ;; esac

# name -> file.  THE DRIVER ITSELF IS NOT SELF-PINNED: it holds the pins.
declare -A PIN=(
  [MD5_LAUNCHER]=d19o_run_arm.sh
  [MD5_GRADER]=d19o_grade.py
  [MD5_XF]=d19o_xf.py
  [MD5_AGE]=d19o_age_guard.py
  [MD5_STALL]=d19o_stall.py
  [MD5_AGGMEM]=d19o_aggregate_memory.py
  [MD5_MARKER]=d19o_stop_marker.sh
  [MD5_RUNSCRIPT]=d19o_runScript.py
  [MD5_DECOMP]=d19o_decomposeParDict
)

# EXISTENCE FIRST AND SEPARATELY (DAFOAM_CHARTER.md section 18.3).
MISSING=""
for k in "${!PIN[@]}"; do
  test -f "$HERE/${PIN[$k]}" || MISSING="$MISSING ${PIN[$k]}"
done
if [ -n "$MISSING" ]; then
  echo "REFUSE section 18.3: cannot pin a set that is incomplete. Missing:$MISSING"
  exit 2
fi
echo "D19O_REPIN existence asserted for ${#PIN[@]} files BEFORE any md5"
echo

# ===========================================================================
# THE FIXPOINT, AND WHY A SINGLE PASS IS NOT ENOUGH -- MEASURED, NOT ANTICIPATED.
# `MD5_LAUNCHER` lives in the DRIVER, and this script also writes `MD5_XF`,
# `MD5_RUNSCRIPT` and `MD5_DECOMP` INTO THE LAUNCHER.  So a single pass computes
# `MD5_LAUNCHER` from launcher bytes that the same pass then rewrites, and the
# pin is stale the instant it is written.  That is the SO-2MR failure with the
# repin script as its author rather than a lane.
#
# The first run of this script did exactly that, and it was caught by
# `--verify`.  The repair is to ITERATE TO A FIXPOINT here, in one invocation,
# and to REFUSE if one is not reached -- rather than to document a rule that the
# operator must run it twice.
# ===========================================================================
if [ "$VERIFY" = "no" ]; then
  PASS=0
  while [ "$PASS" -lt 8 ]; do
    PASS=$((PASS+1))
    CHANGED=0
    for k in $(printf '%s\n' "${!PIN[@]}" | sort); do
      got=$(md5sum "$HERE/${PIN[$k]}" | cut -d' ' -f1)
      for target in "$DRIVER" "$LAUNCHER"; do
        grep -q "^$k=" "$target" 2>/dev/null || continue
        cur=$(grep -m1 "^$k=" "$target" | cut -d= -f2)
        [ "$cur" = "$got" ] && continue
        python3 -c "
import re, sys
path, key, val = '$target', '$k', '$got'
src = open(path).read()
new, n = re.subn(r'(?m)^%s=.*\$' % re.escape(key), '%s=%s' % (key, val), src)
if n != 1:
    sys.stderr.write('REFUSE %s appears %d times in %s (want exactly 1)\n' % (key, n, path))
    sys.exit(2)
open(path, 'w').write(new)
" || exit 2
        CHANGED=$((CHANGED+1))
      done
    done
    echo "  pass $PASS: $CHANGED pin(s) written"
    [ "$CHANGED" -eq 0 ] && break
  done
  if [ "$CHANGED" -ne 0 ]; then
    echo "REFUSE no fixpoint after $PASS passes -- the pins do not settle."
    exit 2
  fi
  echo "  FIXPOINT reached after $PASS pass(es); the last pass wrote nothing."
  echo
fi

RC=0
for k in $(printf '%s\n' "${!PIN[@]}" | sort); do
  f="${PIN[$k]}"
  got=$(md5sum "$HERE/$f" | cut -d' ' -f1)
  # `MD5_XF` appears in BOTH the driver and the launcher; both are updated.
  for target in "$DRIVER" "$LAUNCHER"; do
    grep -q "^$k=" "$target" 2>/dev/null || continue
    cur=$(grep -m1 "^$k=" "$target" | cut -d= -f2)
    if [ "$VERIFY" = "yes" ]; then
      if [ "$cur" != "$got" ]; then
        printf "  DRIFT   %-24s %-26s pinned=%s ondisk=%s\n" "$k" "$(basename "$target")" "$cur" "$got"
        RC=1
      else
        printf "  OK      %-24s %-26s %s\n" "$k" "$(basename "$target")" "$got"
      fi
    else
      python3 - "$target" "$k" "$got" <<'EOF'
import re, sys
path, key, val = sys.argv[1], sys.argv[2], sys.argv[3]
src = open(path).read()
new, n = re.subn(r"(?m)^%s=.*$" % re.escape(key), "%s=%s" % (key, val), src)
if n != 1:
    sys.stderr.write("REFUSE %s appears %d times in %s (want exactly 1)\n" % (key, n, path))
    sys.exit(2)
open(path, "w").write(new)
EOF
      [ $? -ne 0 ] && RC=2
      printf "  SET     %-24s %-26s %s\n" "$k" "$(basename "$target")" "$got"
    fi
  done
done

echo
if [ "$VERIFY" = "yes" ]; then
  [ "$RC" -eq 0 ] && echo "D19O_REPIN VERIFY: every pin matches its file on disk." \
                  || echo "D19O_REPIN VERIFY: **DRIFT** -- a pin does not match its file."
else
  echo "D19O_REPIN DONE.  Now re-run d19o_repin.sh --verify, then re-issue"
  echo "PREREGISTRATION.md section 7 with these values.  Editing any pinned file"
  echo "rewrites the very bytes every declaration of its md5 pins, so every such"
  echo "declaration is stale the instant the file is saved -- that is what cost"
  echo "SO-2MR its first arm."
fi
exit $RC
