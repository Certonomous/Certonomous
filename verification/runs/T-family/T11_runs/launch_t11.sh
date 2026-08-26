#!/bin/bash
# T11 -- detach the three registered levels under setsid so they survive a
# fleet kill. The registered caps and ranks are NOT command-line arguments:
# T11_PREREGISTRATION.md fixes them, and passing them in would let a caller
# quietly widen a cap that rule 12 says stops the run.
set -o pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cap_for(){ case "$1" in c) echo 2;; m) echo 4;; f) echo 8;; esac; }
LEVELS="${*:-c m f}"
for L in $LEVELS; do case "$L" in c|m|f) ;; *) echo "REFUSE: '$L' is not a registered level" >&2; exit 3;; esac; done
for L in $LEVELS; do
    CAP=$(cap_for "$L")
    if [ -e "$HERE/STATUS.T11_PW_$L" ]; then
        echo "SKIP T11_PW_$L: STATUS already exists (refusing to overwrite a completed run's record)"; continue
    fi
    setsid nohup "$HERE/run_one_t11.sh" "$L" "$CAP" 1 >> "$HERE/launch.$L.log" 2>&1 < /dev/null &
    echo "launched T11_PW_$L wrapper_pid=$! cap=${CAP} core-min ranks=1 timeout=$((CAP*60)) s"
done
echo "Detached. STATUS.T11_PW_<level> appears when each finishes; nothing here waits."
