#!/usr/bin/env bash
# Detached wrapper for the D6RF3 chain watcher.
#
# THE ONE THING THIS FILE EXISTS FOR: the rc is captured INSIDE the detached
# process.  `setsid timeout cmd` returns 0 for every outcome, so an rc read
# around the setsid line says nothing about what the watcher did.  Here the
# watcher's own exit status is read into $R by this wrapper, which is itself
# the detached child, and written to the .rc file and the log.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/d6rf3_chain_watch.out"
LOG="$HERE/d6rf3_chain_watch.log"
{
  echo "wrapper_start $(date -u +%Y-%m-%dT%H:%M:%SZ) wrapper_pid=$$ sid=$(ps -o sid= -p $$ 2>/dev/null | tr -d ' ')"
} >> "$OUT"
bash "$HERE/d6rf3_chain_watch.sh" >> "$OUT" 2>&1
R=$?
printf 'watcher_rc=%s end=%s note=rc-captured-INSIDE-the-detached-wrapper-never-around-the-setsid-line\n' \
  "$R" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$OUT"
printf '%s\n' "$R" > "$HERE/d6rf3_chain_watch.rc"
printf '%s watcher_rc=%s (0 terminal condition observed; 3 bound reached or unset; 4 the entry was refused)\n' \
  "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$R" >> "$LOG"
exit "$R"
