#!/bin/bash
# Serial chain for the T10a pool: launch each case via launch_t10a.sh (G1-G3
# guards), wait for its STATUS.<case>, then the next.  One solver at a time.
# Kills nothing; a case that never writes STATUS parks the chain (age guard
# and markers protect grading; the chain logs its wait).
HERE="$(cd "$(dirname "$0")" && pwd)"
LOG="$HERE/log.chain_serial"
for CASE in S_c S_m S_f S_C1 S_f_q S_f_s B_c B_m B_f B_C3 B_f_q B_f_s H_2d; do
    echo "$(date -u +%FT%TZ) chain: launching $CASE" >> "$LOG"
    "$HERE/launch_t10a.sh" "$CASE" >> "$LOG" 2>&1
    w=0
    until [ -e "$HERE/STATUS.$CASE" ]; do sleep 30; w=$((w+30)); [ $((w % 1800)) -eq 0 ] && echo "$(date -u +%FT%TZ) chain: still waiting on $CASE (${w}s)" >> "$LOG"; done
    echo "$(date -u +%FT%TZ) chain: $CASE status: $(cat "$HERE/STATUS.$CASE")" >> "$LOG"
done
echo "$(date -u +%FT%TZ) chain: ALL 13 T10a CASES HAVE STATUS" >> "$LOG"
