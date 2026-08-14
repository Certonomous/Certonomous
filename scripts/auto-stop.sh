#!/bin/bash
# Auto-stop: power the box off when the lab is genuinely idle.
#
# WHY THIS FILE WAS REWRITTEN (2026-08-12)
# ----------------------------------------
# The previous version decided "is anyone working?" by matching command-line
# STRINGS, one of which was the literal `Certonomous/sdk`. A verification suite
# launched from the repo root as
#
#     python -m pytest sdk/tests/test_rank_claim_surfaces.py
#
# spells that path RELATIVELY, so it did not match, so a running suite counted
# as idleness and the box powered off in the middle of it. That happened at
# 15:35 on 2026-08-12 (`auto-stop: idle 30min, shutting down`), killing the tmux
# server and two in-flight suites, and it is the same class of failure recorded
# on 2026-07-30. A second hole: an actively working Claude session was invisible
# too, so the control room reads as an empty room.
#
# The string test also failed in the other direction. It matched ANY command
# line containing the pattern -- including a `grep Certonomous/sdk` typed to
# investigate this very bug, which silently reprieved the box. A test that both
# misses real work and fires on a mention of itself is not a test.
#
# The rule now: decide on facts a spelling cannot change.
#   1. solver/mesher process names          -- a name, not a path
#   2. any worker process whose CWD is in the repo -- a CWD has one spelling
#   3. a Claude session transcript written recently -- the control room
# Anything genuinely idle for IDLE_MINUTES still stops. Cost discipline is
# unchanged; only the definition of "idle" is repaired.
#
# AMENDED 2026-08-14 (D65): clause 3 named ONE session directory and the config
# directory was migrated out from under it, so the control-room test went back
# to reading an occupied room as an empty one -- not because the test was
# wrong, but because its REFERENT moved. It scans a glob now. Fact 3 is the one
# whose subject can migrate, and that is why it is the one that broke twice.

# Overridable so the negative path -- "genuinely idle, so stop" -- can be tested
# without waiting for a genuinely idle box. A gate nobody can test both ways is
# how the last one shipped broken.
IDLE_MINUTES=${IDLE_MINUTES:-30}
MARKER=${MARKER:-/tmp/last_job_activity}
REPO=${REPO:-/home/ubuntu/Certonomous}
# SESSIONS is a GLOB PATTERN, not a path, and that is deliberate -- see the
# note on clause (3) below. Space-separated patterns are allowed, so a test can
# point this at two scratch directories at once. Assignment context does not
# glob in bash, so the pattern survives to clause (3) unexpanded.
SESSIONS=${SESSIONS:-/home/ubuntu/.claude*/projects/-home-ubuntu-Certonomous}
HOLD="$REPO/.autostop-hold"
HOLD_MAX_HOURS=24

# DRY_RUN=1 prints the decision and never powers off. Used to test this script
# without testing it on the box.
#
# Dry-run lines are TAGGED in the journal. Untagged, a test emits
# `idle 45min, shutting down` that reads exactly like a real power-off, and the
# next person reconstructing why the box died from `journalctl -t auto-stop`
# would count shutdowns that never happened. An instrument must not forge the
# evidence it exists to produce.
say() {
    local msg="$*"
    [ -n "$DRY_RUN" ] && { msg="[DRY_RUN] $msg"; echo "$*"; }
    logger -t auto-stop "$msg"
}
keep() { touch "$MARKER"; say "ALIVE: $1"; exit 0; }

[ -f "$MARKER" ] || touch "$MARKER"
last=$(stat -c %Y "$MARKER"); now=$(date +%s); idle=$(( (now - last) / 60 ))

# (0) Explicit hold, for a long unattended run. It EXPIRES, so a forgotten hold
#     cannot pin the box forever -- a hold that never lapses is a bill.
if [ -f "$HOLD" ]; then
    hold_age_h=$(( (now - $(stat -c %Y "$HOLD")) / 3600 ))
    if [ "$hold_age_h" -lt "$HOLD_MAX_HOURS" ]; then
        keep "hold file set ${hold_age_h}h ago"
    else
        say "hold file is ${hold_age_h}h old (>${HOLD_MAX_HOURS}h) -- expired, ignoring"
    fi
fi

# (1) Solvers and meshers, matched on PROCESS NAME. pgrep -x on the name cannot
#     be triggered by a path, a comment, or a grep that mentions the name.
if pgrep -x 'simpleFoam|pimpleFoam|rhoSimpleFoam|rhoCentralFoam|interFoam|potentialFoam|pisoFoam|blockMesh|snappyHexMesh|checkMesh|vspaero|vspaero_opt' >/dev/null 2>&1; then
    keep "solver or mesher running"
fi

# (2) Any worker process whose CWD is inside the repo AND which is actually
#     burning CPU. This is the clause the relative-path suite needed: a CWD is
#     resolved by the kernel, so `sdk/tests/...` and the absolute spelling are
#     the same fact.
#
#     The CPU test is not decoration. `chief_engineer.server` is a permanent
#     daemon whose CWD is inside the repo; counting mere presence would pin the
#     box forever and silently delete the cost control this script exists for.
#     A running suite burns CPU, a parked server does not, and that is the
#     difference we actually mean by "working". Interactive shells are not
#     counted at all -- an abandoned login shell in the repo must not pin the
#     box for days.
#
#     Sampling twice rather than trusting one instant: a process must show CPU
#     movement across the interval. Cron runs this every 5 minutes and the
#     marker only has to be touched once, so a suite would have to look idle six
#     consecutive times to be mistaken for idleness.
cpu_ticks() { awk '{print $14+$15}' /proc/"$1"/stat 2>/dev/null || echo 0; }

workers=""
for pid in $(pgrep -u ubuntu -x 'python|python3|python3.10|python3.11|python3.12|pytest|mpirun|mpiexec|dafoam|foamRun' 2>/dev/null); do
    cwd=$(readlink /proc/"$pid"/cwd 2>/dev/null) || continue
    case "$cwd" in
        "$REPO"|"$REPO"/*) workers="$workers $pid" ;;
    esac
done

if [ -n "$workers" ]; then
    before=""
    for pid in $workers; do before="$before $pid:$(cpu_ticks "$pid")"; done
    sleep 3
    for entry in $before; do
        pid=${entry%%:*}; t0=${entry##*:}; t1=$(cpu_ticks "$pid")
        # >20 ticks in 3s is ~7% of one core: comfortably above a parked
        # daemon's housekeeping, far below anything doing real work.
        if [ "$(( t1 - t0 ))" -gt 20 ]; then
            keep "worker pid $pid busy in repo ($(( t1 - t0 )) CPU ticks in 3s)"
        fi
    done
fi

# (3) The control room. An active Claude session appends to its transcript every
#     turn, so a fresh transcript means someone is working and a stale one means
#     the room emptied. This is what makes the box safe to leave running AND
#     safe to leave alone: it needs no cooperation from the session, and it
#     lapses by itself.
#
#     WHY THIS CLAUSE SCANS A GLOB AND NOT A PATH (D65, 2026-08-14)
#     -------------------------------------------------------------
#     It shipped on 2026-08-12 naming ONE directory,
#     `/home/ubuntu/.claude-sanaa/projects/-home-ubuntu-Certonomous`. The
#     session config directory was migrated afterwards and the live control
#     room moved to `/home/ubuntu/.claude/projects/...`, leaving the named
#     directory holding a copy nobody appends to any more. Measured at 22:00Z
#     on 2026-08-14: the live transcript was advancing every few seconds
#     (22,849,320 bytes at 21:59:54Z) while the named one had not moved since
#     21:46:43Z. The clause was still firing -- off the quiescent copy, purely
#     because it happened to be under 30 minutes old -- and would have gone
#     silent at 22:16:43Z with the control room fully occupied. That is the
#     2026-08-12 defect back again.
#
#     The test was never wrong. Its SUBJECT moved. A check that names its
#     subject by a path inherits every migration of that path, and it fails
#     SILENTLY because a directory that no longer receives writes looks exactly
#     like a directory nobody is working in. So the clause no longer names a
#     directory: it scans every config dir that exists, and if that set is
#     EMPTY it says so loudly rather than evaluating to false. A control-room
#     check that finds no control room to check must not report an empty room.
session_dirs=()
for d in $SESSIONS; do
    [ -d "$d" ] && session_dirs+=("$d")
done

if [ ${#session_dirs[@]} -eq 0 ]; then
    # A no-match is not "nobody is working". It is "this clause cannot see",
    # and the difference is the whole point: the first reads as idleness and
    # powers the box off. It is not a `keep` either -- a gate that pins the box
    # whenever it is misconfigured is a bill (see the hold-file note above).
    # It is a loud line in the journal, where the next person reading
    # `journalctl -t auto-stop` after an unexplained shutdown will find it.
    say "WARNING: no session transcript directory matches SESSIONS='$SESSIONS' -- clause (3) is BLIND, an occupied control room will not hold this box"
else
    # Errors are surfaced, not swallowed. The previous `2>/dev/null` would have
    # turned any find that could not run into a clean false: `bfs`, which this
    # lab's interactive shells alias `find` to, REJECTS `-newermt "-30 min"` as
    # an invalid timestamp, and under the old redirect that rejection read as
    # "no fresh transcript" and powered the box off.
    scan_err=$(mktemp)
    fresh=$(find "${session_dirs[@]}" -maxdepth 1 -name '*.jsonl' -newermt "-${IDLE_MINUTES} min" -print -quit 2>"$scan_err")
    if [ -s "$scan_err" ]; then
        say "WARNING: transcript scan errored, clause (3) may be BLIND: $(head -1 "$scan_err")"
    fi
    rm -f "$scan_err"
    # The matched file is NAMED in the journal on purpose: had the 2026-08-12
    # version done this, the line would have read `.claude-sanaa/...` every
    # five minutes and the stale referent would have been visible for free.
    if [ -n "$fresh" ]; then
        keep "Claude session transcript written within ${IDLE_MINUTES}min ($fresh)"
    fi
fi

if [ "$idle" -ge "$IDLE_MINUTES" ]; then
    say "idle ${idle}min, shutting down"
    [ -n "$DRY_RUN" ] && { echo "DRY_RUN: would run 'sudo shutdown -h now'"; exit 0; }
    sudo shutdown -h now
fi
say "idle ${idle}min, under threshold ${IDLE_MINUTES}min -- no action"
