#!/bin/bash
# Serial-ish chain for the T10a-R pool.  NEVER more than TWO of this lane's
# processes at once (brief: 12 of 16 cores are held by T1b L4 and T3 ext1, a
# T9a-D lane may take 3; everything here runs nice 15 and yields to them).
# Waits for R_q's solve and R_x's preprocessing, then launches R_x (the long
# pole) and R_s (short) together, and waits for both.
HERE="$(cd "$(dirname "$0")" && pwd)"
LOG="$HERE/log.chain"
say() { echo "$(date -u +%FT%TZ) chain: $*" >> "$LOG"; }
say "waiting for STATUS.R_q and R_x/BUILD.txt"
until [ -e "$HERE/STATUS.R_q" ] && [ -f "$HERE/R_x/BUILD.txt" ]; do sleep 30; done
say "R_q status: $(cat "$HERE/STATUS.R_q")"
say "R_x preprocessing: $(grep viewFactorsGen_rc "$HERE/R_x/BUILD.txt")"
if ! grep -q "viewFactorsGen_rc  0" "$HERE/R_x/BUILD.txt"; then
    say "R_x viewFactorsGen did not succeed -- NOT launching R_x; launching R_s only"
    "$HERE/launch_t10aR.sh" R_s >> "$LOG" 2>&1
    until [ -e "$HERE/STATUS.R_s" ]; do sleep 30; done
    say "R_s status: $(cat "$HERE/STATUS.R_s")"
    say "CHAIN DONE (R_x BLOCKED at preprocessing)"
    exit 0
fi
say "launching R_s"
"$HERE/launch_t10aR.sh" R_s >> "$LOG" 2>&1
say "launching R_x"
"$HERE/launch_t10aR.sh" R_x >> "$LOG" 2>&1
w=0
until [ -e "$HERE/STATUS.R_s" ] && [ -e "$HERE/STATUS.R_x" ]; do
    sleep 60; w=$((w+60))
    [ $((w % 1800)) -eq 0 ] && say "still waiting (${w}s): R_s=$([ -e "$HERE/STATUS.R_s" ] && echo done || echo running) R_x=$([ -e "$HERE/STATUS.R_x" ] && echo done || echo running) rss=$(ps -o rss= -C buoyantSimpleFoam | tr '\n' ' ')"
done
say "R_s status: $(cat "$HERE/STATUS.R_s")"
say "R_x status: $(cat "$HERE/STATUS.R_x")"
say "CHAIN DONE -- all three T10a-R cases have STATUS"
