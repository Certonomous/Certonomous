#!/bin/bash
# launch_t5.sh -- T5 launch gate (prereg S15).  Launches ONE case through the FROZEN
# run_one_t5.sh (313df45c), which re-execs itself under setsid and carries the
# solver's real rc into STATUS.<case> (S16.1).  THIS FILE NEVER TRUSTS THE CALLER-
# VISIBLE rc OF run_one_t5.sh: a detached wrapper's exit status is meaningless by
# construction, so the launch is recorded from /proc (pid, sid, cwd), not from $?.
#
# GUARDS, each a refusal (rc 2):
#   G1  atomic LAUNCH_LOCK.<case> via mkdir in T5_runs/ -- a second launcher loses
#   G2  no process holds the case dir as cwd (readlink /proc/*/cwd)
#   G3  no numeric time directory other than 0, and no 0/, exists (L-143)
#   G4  0.orig/, CASE.txt and the frozen launcher are present
#   G5  --timeout is an integer = cap_core_min * 60 / ranks, computed HERE from
#       CASE.txt's per_case_guard_core_min_3xModelB (S11.3) so the number is
#       traceable, never typed
# Launch authority is cited by the caller in LAUNCH_RECORD.md (bc0e687e); this file
# records nothing about authority and grants none.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
CASE="${1:-}"; RANKS="${2:-}"
if [ "$CASE" = "--selftest" ]; then exec "$HERE/launch_t5.sh" __selftest__ 1; fi
[ -n "$CASE" ] && [ -n "$RANKS" ] || { echo "usage: $0 <case> <ranks>  [--selftest]" >&2; exit 2; }
if [ "$CASE" = "__selftest__" ]; then
    T=$(mktemp -d /tmp/claude-1000/-home-ubuntu/*/scratchpad/t5_launch_XXXX 2>/dev/null || mktemp -d)
    mkdir -p "$T/K/0.orig"; printf 'case=K\nper_case_guard_core_min_3xModelB=60\n' > "$T/K/CASE.txt"
    cp "$HERE/run_one_t5.sh" "$T/" ; cp "$HERE/launch_t5.sh" "$T/"
    fails=0
    # arm 1: a held lock refuses
    mkdir "$T/LAUNCH_LOCK.K"; "$T/launch_t5.sh" K 1 >/dev/null 2>&1; [ $? -eq 2 ] || { echo "FAILED: held lock did not refuse"; fails=1; }
    rmdir "$T/LAUNCH_LOCK.K"
    # arm 2: a process holding the case as cwd refuses
    ( cd "$T/K" && sleep 5 ) & SP=$!
    sleep 0.3; "$T/launch_t5.sh" K 1 >/dev/null 2>&1; [ $? -eq 2 ] || { echo "FAILED: cwd-holder did not refuse"; fails=1; }
    kill $SP 2>/dev/null; wait $SP 2>/dev/null; rmdir "$T/LAUNCH_LOCK.K" 2>/dev/null
    # arm 3: a numeric time directory refuses
    mkdir "$T/K/1000"; "$T/launch_t5.sh" K 1 >/dev/null 2>&1; [ $? -eq 2 ] || { echo "FAILED: time dir did not refuse"; fails=1; }
    rmdir "$T/K/1000"; rmdir "$T/LAUNCH_LOCK.K" 2>/dev/null
    # arm 4: an armed 0/ refuses
    mkdir "$T/K/0"; "$T/launch_t5.sh" K 1 >/dev/null 2>&1; [ $? -eq 2 ] || { echo "FAILED: existing 0/ did not refuse"; fails=1; }
    rmdir "$T/K/0"; rmdir "$T/LAUNCH_LOCK.K" 2>/dev/null
    # arm 5: non-integer ranks refuses
    "$T/launch_t5.sh" K x >/dev/null 2>&1; [ $? -eq 2 ] || { echo "FAILED: bad ranks did not refuse"; fails=1; }
    rm -rf "$T"
    [ $fails -eq 0 ] && echo "SELFTEST PASS: 5 refusal arms fired." || echo "SELFTEST FAIL"
    exit $fails
fi
case "$RANKS" in ''|*[!0-9]*|0) echo "REFUSED $CASE: ranks '$RANKS' is not a positive integer" >&2; exit 2;; esac
CDIR="$HERE/$CASE"; LOCK="$HERE/LAUNCH_LOCK.$CASE"
[ -d "$CDIR/0.orig" ] && [ -f "$CDIR/CASE.txt" ] || { echo "REFUSED $CASE: G4 no 0.orig or CASE.txt (not built)" >&2; exit 2; }
[ -x "$HERE/run_one_t5.sh" ] || { echo "REFUSED $CASE: G4 frozen launcher run_one_t5.sh absent" >&2; exit 2; }
if ! mkdir "$LOCK" 2>/dev/null; then echo "REFUSED $CASE: G1 LAUNCH_LOCK held ($LOCK)" >&2; exit 2; fi
echo "launcher pid=$$ lock=$(date -u +%FT%TZ)" >> "$LOCK/launch.log"
for p in /proc/[0-9]*; do
    if [ "$(readlink "$p/cwd" 2>/dev/null)" = "$CDIR" ]; then
        echo "REFUSED $CASE: G2 pid ${p#/proc/} ($(readlink "$p/exe" 2>/dev/null)) holds the case dir as cwd" | tee -a "$LOCK/launch.log" >&2; exit 2
    fi
done
[ -e "$CDIR/0" ] && { echo "REFUSED $CASE: G3 0/ already exists (armed before)" | tee -a "$LOCK/launch.log" >&2; exit 2; }
STALE=$(find "$CDIR" -maxdepth 1 -mindepth 1 -type d -regextype posix-extended -regex '.*/[0-9]+(\.[0-9]+)?$' -printf '%f ')
[ -n "$STALE" ] && { echo "REFUSED $CASE: G3 numeric time dir(s) present: $STALE" | tee -a "$LOCK/launch.log" >&2; exit 2; }
CAP=$(sed -n 's/^per_case_guard_core_min_3xModelB=//p' "$CDIR/CASE.txt")
case "$CAP" in ''|*[!0-9.]*) echo "REFUSED $CASE: G5 no per-case cap in CASE.txt" >&2; exit 2;; esac
TIMEOUT=$(awk -v c="$CAP" -v r="$RANKS" 'BEGIN{printf "%d", c*60/r}')
echo "cap_core_min=$CAP ranks=$RANKS timeout_s=$TIMEOUT" >> "$LOCK/launch.log"
"$HERE/run_one_t5.sh" --case-dir "$CDIR" --timeout "$TIMEOUT" --ranks "$RANKS" \
    --solver "$(sed -n 's/^solver=//p' "$CDIR/CASE.txt")" >> "$LOCK/launch.log" 2>&1
# the rc above is the DETACHING parent's and is NOT used.  Record from /proc instead.
sleep 2
for p in /proc/[0-9]*; do
    if [ "$(readlink "$p/cwd" 2>/dev/null)" = "$CDIR" ]; then
        pid=${p#/proc/}; sid=$(awk '{print $6}' "$p/stat" 2>/dev/null)
        echo "LAUNCHED $CASE: pid=$pid sid=$sid exe=$(readlink "$p/exe" 2>/dev/null) cwd=$CDIR timeout_s=$TIMEOUT ranks=$RANKS $(date -u +%FT%TZ)" | tee -a "$LOCK/launch.log"
        exit 0
    fi
done
echo "NOT SEEN $CASE: no process holds $CDIR as cwd 2 s after launch -- check $CDIR/log.launch; nothing is inferred" | tee -a "$LOCK/launch.log" >&2
exit 3
