#!/bin/bash
# Detached wrapper for the D6RF4 P_conv watcher.
# THE rc IS CAPTURED INSIDE THIS WRAPPER, not around the setsid line:
# `setsid timeout cmd` returns 0 for every outcome, so an rc taken around
# setsid is meaningless.  This file records the WATCHER's own exit.
HERE=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6RF4
python3 "$HERE/d6rf4_watch_p_conv.py" --watch \
        --out "$HERE/P_conv_WATCH.txt" --interval 20 --deadline 5400
rc=$?
echo "watcher_rc=$rc end=$(date -u +%Y-%m-%dT%H:%M:%SZ) note=exit-of-the-WATCHER-not-of-the-arm" \
     >> "$HERE/P_conv_WATCH.rc"
