#!/bin/bash
# Foreground, collision-safe launcher for ONE T1b L4 extension case.
# Usage: launch_t1b_L4_ext1.sh <case> <cap_core_min> <ranks>
# Guards E0/E1/E2/E3/E4 mirrored here before anything is touched, then
# run_one_t1b_L4_ext1.sh is detached with setsid nohup so the solver outlives
# the launching agent.  Nothing here ever kills a process.
# Exit: 0 launched, 1 skipped (lock held), 2 refused, 4 usage.
HERE="$(cd "$(dirname "$0")" && pwd)"
CASE="$1"; CAP="$2"; RANKS="$3"
CDIR="$HERE/$CASE"
LOCK="$CDIR/EXT1_LOCK"
case "$CASE" in
    R_10k_x|R_100k_x|R_300k_x) ;;
    *) echo "usage: $0 <R_10k_x|R_100k_x|R_300k_x> <cap_core_min> <ranks>" >&2; exit 4;;
esac
[ -n "$CAP" ] && [ -n "$RANKS" ] || { echo "usage: $0 <case> <cap_core_min> <ranks>" >&2; exit 4; }
[ -d "$CDIR" ] || { echo "REFUSED $CASE: no case dir" >&2; exit 4; }
grep -q '^rc=0 ' "$HERE/STATUS.$CASE" 2>/dev/null || { echo "REFUSED $CASE: E3 STATUS not rc=0" >&2; exit 2; }
grep -q '^End$' "$CDIR/log.solve" || { echo "REFUSED $CASE: E3 log.solve has no End" >&2; exit 2; }
[ -e "$CDIR/log.solve.ext1" ] && { echo "REFUSED $CASE: E4 log.solve.ext1 exists" >&2; exit 2; }
if ! mkdir "$LOCK" 2>/dev/null; then
    echo "SKIP    $CASE: E1 EXT1_LOCK already exists"; exit 1
fi
echo "launcher pid=$$ lock=$(date -u +%FT%TZ) cap_core_min=$CAP ranks=$RANKS timeout_s=$(( CAP * 60 / RANKS ))" >> "$LOCK/launch.log"
for p in /proc/[0-9]*; do
    if [ "$(readlink "$p/cwd" 2>/dev/null)" = "$CDIR" ]; then
        msg="E2: pid ${p#/proc/} ($(readlink "$p/exe" 2>/dev/null)) already running in case dir"
        echo "REFUSED launcher pid=$$ $(date -u +%FT%TZ): $msg" >> "$LOCK/launch.log"
        echo "REFUSED $CASE: $msg"; exit 2
    fi
done
cd "$HERE" || exit 4
setsid nohup "$HERE/run_one_t1b_L4_ext1.sh" "$CASE" "$CAP" "$RANKS" > /dev/null 2>&1 &
WP=$!
echo "launcher pid=$$ detached wrapper pid=$WP $(date -u +%FT%TZ)" >> "$LOCK/launch.log"
echo "LAUNCH  $CASE: guards passed; wrapper pid=$WP cap=$CAP core-min ranks=$RANKS timeout=$(( CAP * 60 / RANKS ))s"
exit 0
