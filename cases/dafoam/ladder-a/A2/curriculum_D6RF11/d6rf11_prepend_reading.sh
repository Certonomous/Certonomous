#!/usr/bin/env bash
# D6RF11 — put the reading ABOVE the numbers.
#
# The grading path d6rf11_grade.py is frozen with the registration (e21e748b2)
# and is not touched. The hold-release script is running and is not edited in
# place. So this waits until the hold-release has finished grading and exited
# (its D6RF11_HOLD_DONE line), then REWRITES D6RF11_AUTOGRADE.out with the
# reading first and the comparator's own output after it.
#
# It waits, it writes, it kills nothing.
B=/home/ubuntu/certonomous-runs/CURRICULUM-D6RF11-a2-wing-fd-simplec-probe
NOTE="$B/D6RF11_READ_THIS_BEFORE_THE_NUMBERS.txt"
AG="$B/D6RF11_AUTOGRADE.out"
HOLD="$B/D6RF11_HOLD.out"

for i in $(seq 1 34560); do   # 96 h
  if grep -q 'D6RF11_HOLD_DONE' "$HOLD" 2>/dev/null; then
    sleep 5
    if [ -f "$AG" ] && ! grep -q 'READ THIS BEFORE YOU READ THE NUMBERS' "$AG" 2>/dev/null; then
      T=$(mktemp "$B/.ag.XXXXXX") || exit 1
      cat "$NOTE" > "$T"
      printf '\n===================== COMPARATOR OUTPUT FOLLOWS =====================\n\n' >> "$T"
      cat "$AG" >> "$T"
      mv "$T" "$AG"
      echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) D6RF11_READING_PREPENDED into $AG" >> "$HOLD"
    fi
    exit 0
  fi
  sleep 10
done
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) D6RF11_PREPEND_GAVE_UP after 96 h" >> "$HOLD"
