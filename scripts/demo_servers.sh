#!/usr/bin/env bash
# demo_servers.sh -- keep the two demo surfaces up.
#
#   :8765  control room   (chief_engineer.server, missions + validation wall)
#   :8080  static website (demo-output/website, incl. benchmarks.html)
#
# Started by cron @reboot and safe to re-run at any time: it only starts a
# server that is not already listening, so running it twice cannot produce the
# duplicate-listener situation where a stale process answers instead of the
# live one.
#
# WHY THIS EXISTS. This instance auto-stops when idle and has restarted several
# times mid-session. Servers launched by hand die with it, and the operator
# discovers this as "connection refused" in the middle of preparing a demo.
set -u

REPO=/home/ubuntu/Certonomous
# 2026-08-18: the three server logs used to be written to /home/ubuntu directly
# and were the last loose files at that root. They are re-pointed at
# /home/ubuntu/logs/ here rather than merely moved, because a log that is moved
# without re-pointing its writer is recreated at the old path by the next
# @reboot launch -- and worse, a process ALREADY holding the old descriptor keeps
# writing to the moved inode, so the file at the new path looks frozen while the
# real output goes somewhere nobody is looking.
LOGDIR=/home/ubuntu/logs
mkdir -p "$LOGDIR"
LOG=$LOGDIR/demo_servers.log

# OpenFOAM lives behind the openfoam2606 launcher on this box, not on PATH.
# cron @reboot hands this script a bare environment, so a server started that
# way inherited no launcher, and an act shelling out to an OpenFOAM utility
# died with FileNotFoundError -- surfacing on camera only as "the wake solve
# did not complete". Exported here so a cron-started server and a hand-started
# one are the same server. Matches ops/aws/provision.sh line 49. (VSPAERO
# needs no prefix here; it is reachable natively.)
export OPENFOAM_RUN_PREFIX="${OPENFOAM_RUN_PREFIX:-openfoam2606}"

listening() { ss -lnt 2>/dev/null | grep -q ":$1 "; }
stamp()     { date -u +%FT%TZ; }

if listening 8765; then
    echo "$(stamp) control room already listening on 8765" >> "$LOG"
else
    cd "$REPO/sdk" || exit 1
    setsid nohup python3 -u -m chief_engineer.server \
        >> "$LOGDIR/control_room.log" 2>&1 < /dev/null &
    disown 2>/dev/null || true
    echo "$(stamp) started control room on 8765" >> "$LOG"
fi

if listening 8080; then
    echo "$(stamp) static site already listening on 8080" >> "$LOG"
else
    cd "$REPO" || exit 1
    # R13 / batch 8: the served root is `web/` -- the five files that were
    # actually reachable from a page.  It was `demo-output/website`, whose
    # 19,149 tracked files were served and 19,144 of them referenced by nothing.
    setsid nohup python3 -u -m http.server 8080 --directory web \
        >> "$LOGDIR/static_site.log" 2>&1 < /dev/null &
    disown 2>/dev/null || true
    echo "$(stamp) started static site on 8080" >> "$LOG"
fi
