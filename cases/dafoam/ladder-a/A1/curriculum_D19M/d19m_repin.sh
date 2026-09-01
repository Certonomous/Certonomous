#!/usr/bin/env bash
# ===========================================================================
# Curriculum D19M -- SET THE FROZEN PINS, ALL OF THEM, IN ONE PASS.
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
#   d19m_repin.sh              -- set the pins and print the table
#   d19m_repin.sh --verify     -- recompute and compare; change nothing
#
# THE PINS ARE VERIFIED THREE WAYS at the freeze, as the pre-registration's
# section 7 records: on disk, from the committed blob at HEAD, and from the blob
# at the pre-registration commit.  This script does the first; the other two are
# done in the commit's own shell invocation and pasted into section 7.
# ===========================================================================
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
DRIVER="$HERE/d19m_chain_driver.sh"
LAUNCHER="$HERE/d19m_run_arm.sh"
# THE INSTRUMENT PINS ITS OWN PRODUCER.  D19O inherited a producer whose md5
# was a literal in three places; here the producer is NEW, so `MD5_PRODUCER`
# lives in `d19m_xf.py` and is set by this script like any other pin.
XF="$HERE/d19m_xf.py"
VERIFY=no
case "${1:-}" in --verify) VERIFY=yes ;; esac

# name -> file.  THE DRIVER ITSELF IS NOT SELF-PINNED: it holds the pins.
declare -A PIN=(
  [MD5_LAUNCHER]=d19m_run_arm.sh
  [MD5_GRADER]=d19m_grade.py
  [MD5_XF]=d19m_xf.py
  [MD5_AGE]=d19m_age_guard.py
  [MD5_STALL]=d19m_stall.py
  [MD5_AGGMEM]=d19m_aggregate_memory.py
  [MD5_MARKER]=d19m_stop_marker.sh
  [MD5_RUNSCRIPT]=d19m_runScript.py
  [MD5_PRODUCER]=d19m_runScript.py
  [MD5_DECOMP]=d19m_decomposeParDict
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
echo "D19M_REPIN existence asserted for ${#PIN[@]} files BEFORE any md5"
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
      for target in "$DRIVER" "$LAUNCHER" "$XF"; do
        # ONE guard, not the three my earlier blind patches interleaved here.
        # This block was rewritten rather than patched again: a control whose own
        # control flow is unreadable is not a control.
        if [ "$k" = "MD5_PRODUCER" ]; then
          case "$target" in *.py) ;; *) continue ;; esac
          grep -q "^PRODUCER_MD5 = " "$target" 2>/dev/null || continue
          cur=$(grep -m1 "^PRODUCER_MD5 = " "$target" | grep -oE "[0-9a-f]{32}")
        else
          case "$target" in *.py) continue ;; esac
          grep -q "^$k=" "$target" 2>/dev/null || continue
          cur=$(grep -m1 "^$k=" "$target" | cut -d= -f2)
        fi
        [ "$cur" = "$got" ] && continue
        python3 -c "
import re, sys
path, key, val = '$target', '$k', '$got'
src = open(path).read()
if path.endswith('.py') and key == 'MD5_PRODUCER':
    # the python form: PRODUCER_MD5 = \"...\"
    new, n = re.subn(r'(?m)^PRODUCER_MD5 = \"[^\"]*\"\$',
                     'PRODUCER_MD5 = \"%s\"' % val, src)
else:
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
  for target in "$DRIVER" "$LAUNCHER" "$XF"; do
    if [ "$k" = "MD5_PRODUCER" ]; then
      case "$target" in *.py) ;; *) continue ;; esac
      grep -q "^PRODUCER_MD5 = " "$target" 2>/dev/null || continue
      cur=$(grep -m1 "^PRODUCER_MD5 = " "$target" | grep -oE "[0-9a-f]{32}")
    else
      case "$target" in *.py) continue ;; esac
      grep -q "^$k=" "$target" 2>/dev/null || continue
      cur=$(grep -m1 "^$k=" "$target" | cut -d= -f2)
    fi
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
if path.endswith(".py") and key == "MD5_PRODUCER":
    new, n = re.subn(r'(?m)^PRODUCER_MD5 = "[^"]*"$',
                     'PRODUCER_MD5 = "%s"' % val, src)
else:
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
# ===========================================================================
# THE PRE-REGISTRATION'S OWN TABLE IS CHECKED TOO, AND THIS CLOSES A REAL GAP.
#
# D19M's section 7 table went STALE the moment a pinned file was edited after the
# table was written -- MEASURED at this item's own freeze: `d19m_grade.py` and
# `d19m_chain_driver.sh` were both edited (an XE prediction corrected 3.10 ->
# 2.60) AFTER section 7 was authored, and the document went to commit carrying
# two hashes that no longer named their files.  That is the SO-2MR failure, in a
# freeze, and `--verify` did not see it because it only ever read the DRIVER, the
# LAUNCHER and the INSTRUMENT.
#
# THE EXECUTABLE PINS AND THE DOCUMENTED PINS ARE DIFFERENT CLAIMS, and a check
# that reads only the first cannot see the second go wrong.
# ===========================================================================
if [ "$VERIFY" = "yes" ] && [ -f "$HERE/PREREGISTRATION.md" ]; then
  echo
  python3 - "$HERE" <<'EOF'
import hashlib, os, re, sys
here = sys.argv[1]
txt = open(os.path.join(here, "PREREGISTRATION.md")).read()

# THE CHECKER IMPLEMENTS THE DOCUMENT'S OWN READING RULE, AND IT HAS TO.
# Rule 6 forbids editing above an amendment, so a corrected pin is published at
# the FOOT while the struck value still stands in section 7 -- and an amendment's
# own table SPELLS the struck value on purpose, so that a grep for it lands on the
# correction.  A checker that treated every hash in the file as a live claim would
# therefore report the amendment's own struck column as drift, which is exactly
# what the first version of this check did.
#
# THE RULE: scan in document order and keep the LAST hash recorded for each file;
# on a row carrying several hashes (an amendment's STRUCK | CORRECT table), the
# LAST one on the line wins.  That is precisely what "a reader must carry the
# value from the amendment, not from section 7" means, expressed as code.
# PAIRED BY ADJACENCY, not by sharing a line.  A line-wide pairing associated
# `d19m_xf.py` with the PHYSICS-BLOCK md5, because section 7.1 names both in one
# sentence -- two different claims about two different byte ranges.  The pattern
# below requires the hash to FOLLOW the filename with nothing between but table
# and emphasis markup, so a filename mentioned in prose beside an unrelated hash
# cannot be mistaken for a pin.
PAIR = re.compile(r"`(d19m_[A-Za-z_]*(?:\.py|\.sh)?)`(?:\s*\|)?\s*\**`([0-9a-f]{32})`")
last = {}
for f, h in PAIR.findall(txt):
    last[f] = h          # document order; a later record supersedes an earlier

bad = []
for f, h in sorted(last.items()):
    full = os.path.join(here, f)
    if not os.path.isfile(full):
        bad.append((f, h, "ABSENT")); continue
    got = hashlib.md5(open(full, "rb").read()).hexdigest()
    if got != h:
        bad.append((f, h, got))
if bad:
    for f, h, got in bad:
        print("  PREREG-DRIFT %-28s documented=%s ondisk=%s" % (f, h, got))
    print("  PREREGISTRATION.md CARRIES %d STALE PIN(S) -- amend it before launch." % len(bad))
    sys.exit(1)
seen = last
print("  PREREG OK  %d documented pin(s) match their files on disk" % len(seen))
EOF
  [ $? -ne 0 ] && RC=1
fi

if [ "$VERIFY" = "yes" ]; then
  [ "$RC" -eq 0 ] && echo "D19M_REPIN VERIFY: every pin matches its file on disk." \
                  || echo "D19M_REPIN VERIFY: **DRIFT** -- a pin does not match its file."
else
  echo "D19M_REPIN DONE.  Now re-run d19m_repin.sh --verify, then re-issue"
  echo "PREREGISTRATION.md section 7 with these values.  Editing any pinned file"
  echo "rewrites the very bytes every declaration of its md5 pins, so every such"
  echo "declaration is stale the instant the file is saved -- that is what cost"
  echo "SO-2MR its first arm."
fi
exit $RC
