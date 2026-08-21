#!/bin/bash
# Foreground pool launcher for T3: launches the given cases one at a time via
# launch_t3.sh, never exceeding CAP concurrent solver processes under this run
# tree.  A "slot" is a process whose readlink /proc/<pid>/exe ends in
# /buoyantBoussinesqSimpleFoam (or /checkMesh, which the runner executes
# immediately before the solver and which therefore IS a slot about to be
# occupied) and whose /proc/<pid>/cwd lies under this run tree.  Polls every
# 60 s until a slot is free.  Safe to re-run: G1 in launch_t3.sh makes a
# re-launch of an already-launched case a no-op (SKIP), and refusals (G2/G3)
# are printed and skipped, never retried or cleaned up.  Nothing is killed.
# Usage:  launch_all_t3.sh CAP case [case ...]
HERE="$(cd "$(dirname "$0")" && pwd)"
CAP="$1"; shift
case "$CAP" in ''|*[!0-9]*) echo "usage: $0 CAP case [case ...]" >&2; exit 4;; esac
[ $# -ge 1 ] || { echo "usage: $0 CAP case [case ...]" >&2; exit 4; }
POLL=60

slots_used() {
    local n=0 p exe cwd
    for p in /proc/[0-9]*; do
        exe="$(readlink "$p/exe" 2>/dev/null)" || continue
        case "$exe" in */buoyantBoussinesqSimpleFoam|*/checkMesh) ;; *) continue;; esac
        cwd="$(readlink "$p/cwd" 2>/dev/null)" || continue
        case "$cwd" in "$HERE"/*) n=$((n+1));; esac
    done
    echo "$n"
}

for CASE in "$@"; do
    [ -d "$HERE/$CASE" ] || { echo "NOCASE  $CASE: no such case dir under $HERE"; continue; }
    if [ -d "$HERE/$CASE/LAUNCH_LOCK" ]; then
        echo "SKIP    $CASE: G1 LAUNCH_LOCK already exists (no slot consumed)"; continue
    fi
    while :; do
        used=$(slots_used)
        [ "$used" -lt "$CAP" ] && break
        echo "WAIT    $CASE: $used of $CAP slots in use under $HERE; $(date -u +%FT%TZ)"
        sleep "$POLL"
    done
    "$HERE/launch_t3.sh" "$CASE"
    rc=$?
    # give the wrapper time to appear as checkMesh/solver before the next count
    [ "$rc" -eq 0 ] && sleep 10
done
echo "launch_all_t3 finished $(date -u +%FT%TZ): $(slots_used) slot(s) in use under $HERE"
exit 0
