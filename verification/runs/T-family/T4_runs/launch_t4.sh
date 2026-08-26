#!/bin/bash
# T4 -- detach the three registered levels under setsid so they survive a
# fleet kill (a usage limit terminates every agent at once; a solver started
# in an agent's foreground Bash gets SIGTERMed with it).
#
# Usage: launch_t4.sh            # all three registered levels
#        launch_t4.sh c m        # a subset, same registered caps
#
# THE CAPS AND RANKS BELOW ARE THE REGISTERED ONES and are not arguments.
# T4_PREREGISTRATION.md section 9 fixes them; passing them on a command line
# would let a caller quietly widen a cap that rule 12 says stops the run.
set -o pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cap_for()   { case "$1" in c) echo 50;; m) echo 300;; f) echo 1600;; esac; }
ranks_for() { echo 1; }   # every registered level is serial; see prereg section 9

LEVELS="${*:-c m f}"
for L in $LEVELS; do
    case "$L" in c|m|f) ;; *) echo "REFUSE: '$L' is not a registered level" >&2; exit 3;; esac
done

for L in $LEVELS; do
    CAP=$(cap_for "$L"); RANKS=$(ranks_for "$L")
    if [ -e "$HERE/STATUS.T4_IJ_$L" ]; then
        echo "SKIP T4_IJ_$L: STATUS already exists (refusing to overwrite a completed run's record)"
        continue
    fi
    setsid nohup "$HERE/run_one_t4.sh" "$L" "$CAP" "$RANKS" \
        >> "$HERE/launch.$L.log" 2>&1 < /dev/null &
    echo "launched T4_IJ_$L  wrapper_pid=$!  cap=${CAP} core-min  ranks=${RANKS}  timeout=$((CAP*60/RANKS)) s"
done
echo "Detached.  STATUS.T4_IJ_<level> appears when each finishes; nothing here waits."
