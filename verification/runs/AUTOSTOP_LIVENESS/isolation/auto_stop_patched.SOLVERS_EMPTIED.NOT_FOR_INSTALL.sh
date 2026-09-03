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

# ===========================================================================
# THIS FILE IS NOT INSTALLED. SANAA INSTALLS IT, OR NOBODY DOES.
# ---------------------------------------------------------------------------
# No agent in this lab has written to /usr/local/bin/auto-stop.sh, run any
# sudo, or touched cron. The three lines below are the whole handover.
#
#   1. BACK UP THE LIVE FILE FIRST, so the install is reversible:
#        sudo cp -a /usr/local/bin/auto-stop.sh \
#          "/usr/local/bin/auto-stop.sh.bak.$(date -u +%Y%m%dT%H%M%SZ)"
#
#   2. INSTALL (ends root:root 0755, the mode and owner it has today):
#        sudo install -o root -g root -m 0755 \
#          /home/ubuntu/Certonomous/scripts/auto_stop_patched.sh \
#          /usr/local/bin/auto-stop.sh
#
#   3. VERIFY WITHOUT STOPPING ANYTHING -- prints the decision, exits 0, and
#      cannot reach `shutdown` because DRY_RUN short-circuits the line above
#      it:
#        sudo env DRY_RUN=1 /usr/local/bin/auto-stop.sh
#      Expect one line beginning `ALIVE:` or `idle Nmin, ...`. Run it as root:
#      as `ubuntu` it also prints `touch: cannot touch
#      '/tmp/last_job_activity': Permission denied`, because the real marker is
#      root-owned. That is the marker check, not a fault in the script.
#
#   TO ROLL BACK: sudo install -o root -g root -m 0755 <the .bak file> \
#                   /usr/local/bin/auto-stop.sh
# ===========================================================================

# ===========================================================================
# ADDED 2026-09-03 (cfd lane) -- THE 02:25:05Z CONTAINER POWEROFF
# ---------------------------------------------------------------------------
# WHAT HAPPENED, from artifacts still on disk and re-measured on 2026-09-03
# at 16:0xZ before a line of this patch was written:
#
#   journalctl -b -1 -t auto-stop, final two lines:
#       Sep 03 02:25:05 auto-stop[348771]: idle 34min, shutting down
#       Sep 03 02:25:05 auto-stop[348774]: idle 34min, under threshold 30min -- no action
#   journalctl -b -1 tail: systemd reached poweroff.target at 02:25:14.
#   last -x: "shutdown system down ... Thu Sep 3 02:25 - 15:34 (13:09)".
#
#   docker inspect, both containers:
#       a1wr_sweep_C_20260902T181935Z  Started 2026-09-02T18:35:58.899Z
#                                      Finished 2026-09-03T02:25:05.628Z  Exit 143
#       a1wr_sweep_I_20260902T181935Z  Started 2026-09-02T18:35:58.638Z
#                                      Finished 2026-09-03T02:25:05.617Z  Exit 143
#       both User "0:0", both WorkingDir /mnt/case.
#   143 = 128+15 = SIGTERM. They were killed BY the poweroff, 7h49m into a
#   10.33 h `timeout` budget. Nothing was salvaged.
#
# THE BOX WAS NOT IDLE AND SAID IT WAS. That is the defect.
#
# WHY NONE OF (1), (2), (3) COULD SEE IT -- none of them was wrong about what
# it tests; they simply do not test where the work was:
#
#   (1) matches basename(/proc/PID/exe) against SOLVERS. DAFoam's primal here
#       is an IN-PROCESS library call from `python /mnt/runScript.py`, so the
#       basename on the host was `python`. No process named DARhoSimpleFoam
#       ever existed, so adding the name to SOLVERS would have changed nothing.
#
#   (2) requires `pgrep -u ubuntu` AND a cwd under $REPO. Both fail, either one
#       fatally: the container ran User=0:0 (measured above) so every process
#       in it is uid 0; and its cwd resolves in the container mount namespace
#       to /mnt/case, whose host side is
#       /home/ubuntu/certonomous-runs/A1WR/STAGE12/sweep_C -- outside $REPO.
#
#   (3) is a control-room test and was doing its job: the room went quiet at
#       ~01:51 and the clause correctly went silent. It was simply the only
#       clause holding the box, and an overnight container sweep is exactly
#       what it was never meant to cover.
#
# THE REPAIR RULE: the work was never invisible -- it was writing to disk the
# whole time. Measured: the newest mtime under /home/ubuntu/certonomous-runs
# at the moment of the decision was
#   2026-09-03 02:24:58.535  .../A1WR/STAGE12/inflight.txt
# SEVEN SECONDS before this script declared the box idle. Nothing had to be
# guessed. The box had to be asked a question nobody asked it.
#
# So three clauses are ADDED, after (3), and nothing above them is edited.
#
# ---------------------------------------------------------------------------
# WHICH SIGNALS ARE LOAD-BEARING, stated plainly as the brief requires
# ---------------------------------------------------------------------------
# Every one of these is a signal some party ALREADY maintains for its own
# reasons. Not one is a convention invented here and hoped for:
#
#   (4) `docker ps -q` + host-namespace pids from `docker top`, sampled for CPU
#       movement with the SAME cpu_ticks helper and the SAME >20-ticks-in-3s
#       threshold clause (2) already uses. Maintained by: the docker daemon.
#   (5a) the wrapper argv that scripts/queue_runner.py:529-536 itself writes --
#       `bash -c "cd <cwd> && <argv> ...; echo ... > <cwd>/STATUS.queue.<id>"`.
#       Maintained by: the queue runner's own launcher.
#   (5b) a `launched/*.json` record that the daemon has NOT yet stamped
#       `_launch.status_seen_utc` (queue_runner.py:300, 645-654), CONJOINED
#       with `_launch.sid` still naming a live session in `ps -eo sid=`.
#       Maintained by: the daemon (the record) and the kernel (the session).
#   (6) file mtimes under RUNROOTS. Maintained by: the filesystem.
#
# WHY (5b) NEEDS BOTH HALVES, measured rather than argued. On 2026-09-03 there
# were 303 launched records; 5 lacked `status_seen_utc` -- including
# A1WR_chain.json, the very chain this poweroff killed -- and ZERO of the 5
# had a live sid. The record alone would therefore pin this box permanently on
# five dead rows. The kernel's session liveness is what makes the clause expire
# by itself, which is the property clause (0)'s hold file was given by hand.
# ===========================================================================

# Run trees that live OUTSIDE $REPO because they are too large for git. A
# space-separated list, so a test can point it at a scratch directory and so
# adding a root is one word.
#
# /home/ubuntu/closure-data and /home/ubuntu/closure-challenge-benchmark are
# DELIBERATELY NOT HERE. Measured 2026-09-03: their newest file mtimes are
# 2026-08-31 and 2026-08-17 -- they are dataset stores, not active run trees,
# and clause (6) pays a full inode walk on the QUIET path. Adding a root that
# has not been written in three weeks buys no protection and pays that walk.
# Add one the day a campaign starts writing there, not before.
RUNROOTS=${RUNROOTS:-/home/ubuntu/certonomous-runs}

# THE FRESHNESS WINDOW, and why this number rather than a round one.
#
# It has to exceed the worst gap between consecutive writes a REAL run shows,
# and sit comfortably inside IDLE_MINUTES.
#
# A PREDECESSOR DRAFT JUSTIFIED 20 min FROM A NUMBER THAT DOES NOT MEAN WHAT
# IT LOOKS LIKE, and the correction matters more than the answer. It read the
# surviving mtimes of the dead run -- 02:05:19, 02:07:11, 02:07:13, 02:07:17,
# 02:24:07, 02:24:21, 02:24:58 -- and called the 02:07:17 -> 02:24:07 step a
# "worst inter-write gap of 16.8 min". It is not one. An mtime records only a
# file's LAST write, so a set of final mtimes cannot reconstruct the cadence of
# anything; sweep.log was appended thousands of times inside that "gap". The
# figure was an artifact of the reading, and a window sized from it would have
# been sized from noise.
#
# WHAT IS ACTUALLY MEASURABLE is each log's own clock. Every OpenFOAM/DAFoam
# iteration block ends `ExecutionTime = ... ClockTime = <n> s`, and each such
# line IS a write to that log, so consecutive ClockTime values give TRUE
# inter-write gaps -- the thing the mtime reading only pretended to give.
#
# Measured 2026-09-03 over 176 real lab logs under /home/ubuntu/certonomous-runs
# (every log >50 kB carrying >=20 ClockTime lines, sampled from 906 candidates):
#
#   distribution of each log's WORST gap:  max 1049s   p99 1037s
#                                          p95  136s   median 1s
#   the tail, named:
#     1049s  W5-regrade/sail_patched_checktotals.log   (n=41, span 1145s)
#     1037s  W5-regrade/sail_stock_checktotals.log     (n=41, span 1134s)
#      649s  CURRICULUM-D7FR-a3-m6-fd/F-S_...log       (n=242, span 1072s)
#      524s  CURRICULUM-D5-a2-wing-ffd-density/O48_...log (n=1881)
#      205s  A1WR/STAGE12/sweep_C/out/sweep.log        (the run that died)
#
# WORST MEASURED INTER-WRITE GAP OF A REAL RUN ON THIS BOX: 1049 s = 17.5 min.
#
# THIS IS WHY THE NUMBER MOVED FROM 20 TO 30. The A1WR sweeps alone would have
# justified 20 min (their own worst gap is 205 s, and the whole ten-log family
# tops out at 208 s). Widening the sample from 10 logs to 176 put a 17.5-min
# gap in the record -- inside a 20-min window by 2.5 minutes. A window sized
# 1.15x the worst thing already on disk is not a margin, it is a coincidence.
#
# THE PROTECTION IS LARGER THAN THE WINDOW, and this is the figure that
# actually governs. `keep` TOUCHES THE MARKER, so clause (6) keeps firing until
# the newest write ages past RUN_FRESH_MINUTES, and only then does the
# IDLE_MINUTES countdown begin. TOTAL TOLERATED SILENCE after a run's last
# write is therefore RUN_FRESH_MINUTES + IDLE_MINUTES = 30 + 30 = 60 min,
# minus up to one cron interval (5 min) of granularity: 55-60 min. Against the
# worst measured gap of 17.5 min that is a margin of 3.1x-3.4x.
#
# WHAT THE CHANGE COSTS, stated rather than hidden: nothing at all on a box
# with no run tree writes, because clause (6) never fires there and the
# original 30-min countdown is untouched. It costs only AFTER a real run ends,
# where the box now lingers up to 60 min instead of up to 50. That is 10 extra
# minutes x 16 cores = 160 core-min = 2.67 core-h ~ $0.14 per stop event at the
# recorded $0.0513/core-h -- DERIVED, NOT MEASURED (this box cannot read its
# own billing, COMPUTE_BUDGET_CHARTER §5). Against 7h49m x 2 cores of DAFoam
# thrown away on 2026-09-03, that is the trade being made.
#
# Applied to the fatal night: at the 02:20:04 tick the newest mtime was at most
# 12.8 min old, inside the window, the marker would have been touched, and
# 02:25:05 would have read `idle 5min`. The sweeps would have finished.
#
# A SECOND, INDEPENDENT MEASUREMENT points the same way. The chain driver
# cases/dafoam/ladder-a/A1/wall_resolved_aoa_polar/a1wr_chain_driver.sh:204
# rewrites `$RUN/inflight.txt` on every pass of its wait loop and then
# `sleep 20` (line 205). That run root carried a 20-SECOND heartbeat for the
# whole 7h49m, and its last beat landed 6.5 s before the poweroff.
#
# HONEST LIMIT: a run whose write cadence exceeds the tolerated silence is
# still invisible to this clause, and the 176-log sample cannot bound a tail it
# did not observe. That is what .autostop-hold is for, and it is the right tool
# -- it is explicit, and it expires.
RUN_FRESH_MINUTES=${RUN_FRESH_MINUTES:-30}

# `docker`, overridable so the test can substitute a stub and never need the
# real daemon.
DOCKER=${DOCKER:-docker}

# Where the queue daemon keeps its per-team `launched/` records. Derived from
# $REPO so a test that injects a scratch REPO can never read the real queue.
QUEUE_ROOT=${QUEUE_ROOT:-$REPO/verification/queue}

# INDETERMINATE-THEREFORE-ALIVE, and the one escape hatch.
#
# Sanaa's requirement, 2026-09-03: a detector that reports "idle" because it
# COULD NOT LOOK is the exact failure mode that powers off a live campaign.
# So when docker is installed but unreadable -- daemon down, socket gone,
# permission denied -- clause (4) resolves to ALIVE, because a containerized
# solve cannot be ruled out.
#
# THE COST THIS BUYS, said out loud rather than buried: if dockerd dies and
# stays dead, this clause pins the box and Sanaa pays by the hour until someone
# notices. Every other blind clause in this file is a loud journal line for
# exactly that reason. The resolution is not to weaken the rule but to give it
# a switch: DOCKER_BLIND_ALIVE=0 restores fall-through, the journal line names
# the switch, and the decision to throw it is a human's.
#
# The degenerate case is separated on purpose: if there is NO docker executable
# at all, that is not indeterminate, it is determinate -- no container can be
# running -- and it falls through with a loud line rather than pinning a box
# that has never had docker on it.
DOCKER_BLIND_ALIVE=${DOCKER_BLIND_ALIVE:-1}

# DRY_RUN=1 prints the decision and never powers off. Used to test this script
# without testing it on the box.
#
# Dry-run lines are TAGGED in the journal. Untagged, a test emits
# `idle 45min, shutting down` that reads exactly like a real power-off, and the
# next person reconstructing why the box died from `journalctl -t auto-stop`
# would count shutdowns that never happened. An instrument must not forge the
# evidence it exists to produce.
#
# ADDED 2026-09-03 (cfd lane): AUTO_STOP_DRY_RUN is a SECOND SPELLING of
# DRY_RUN and nothing more. It exists because `DRY_RUN` is a name several other
# scripts on this box already use for something else, so a test that exports it
# cannot prove it reached THIS script. `AUTO_STOP_DRY_RUN=1` is unambiguous,
# and scripts/test_auto_stop_liveness.py sets it. This is the ONLY change this
# patch makes to the script's interface, and it is an ADDITION: the existing
# DRY_RUN spelling is unchanged and still works, and neither spelling can ever
# power the box off.
DRY_RUN=${DRY_RUN:-${AUTO_STOP_DRY_RUN:-}}
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

# (1) Solvers and meshers, matched on the EXECUTABLE the kernel resolved --
#     /proc/<pid>/exe -- not on the process name and not on the command line.
#
#     2026-08-18: this clause previously used `pgrep -x` over /proc/<pid>/comm,
#     and comm is TRUNCATED BY THE KERNEL TO 15 CHARACTERS. Every name in the
#     old list happened to be 14 chars or fewer, so the defect was invisible --
#     while the thermal campaign's own solvers are 17 and 27 characters:
#     buoyantSimpleFoam, buoyantPimpleFoam, buoyantBoussinesqSimpleFoam. A live
#     27-char solver was controlled and `pgrep -x` returned NO MATCH, so a
#     detached overnight thermal solve with the control room closed satisfied
#     no clause at all and the box powered off underneath it. Adding the names
#     to the list would NOT have fixed it -- comm can never hold them.
#
#     /proc/<pid>/exe is a kernel-resolved symlink to the real binary and is not
#     truncated, so the match is on identity rather than on a printable label.
#     It also cannot be forged by a path, a comment, an editor buffer or a grep
#     that merely mentions the name, which is the property the old `-x` was
#     chosen for and which `pgrep -f` would have thrown away.
SOLVERS=''   # ISOLATION VARIANT -- NOT FOR INSTALL
for pid in $(ls /proc 2>/dev/null | grep -E '^[0-9]+$'); do
    exe=$(readlink "/proc/$pid/exe" 2>/dev/null) || continue
    [ -n "$exe" ] || continue
    base=${exe##*/}
    for s in $SOLVERS; do
        if [ "$base" = "$s" ]; then
            keep "solver or mesher running ($base, pid $pid)"
        fi
    done
done

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

# ===========================================================================
# CLAUSES (4), (5), (6) -- ADDED 2026-09-03 (cfd lane)
#
# THE INVARIANT, stated first because everything below is subordinate to it:
#   THIS PATCH MAY ONLY MAKE THE BOX HARDER TO STOP, NEVER EASIER.
# Mechanically: every line added below is either a `say` (a journal line, no
# decision) or a `keep` (which touches the marker and exits 0 -- i.e. ALIVE).
# Not one line added below can cause a stop, and not one line above this
# banner was edited, so the set of states that reach `sudo shutdown` is a
# STRICT SUBSET of the original's. `diff /usr/local/bin/auto-stop.sh` against
# this file shows zero deleted lines outside the two documented additions
# (the AUTO_STOP_DRY_RUN spelling, and the `exit 0` at the foot).
#
# The converse is also a failure and is not waved away: Sanaa pays for this
# box, and a patch that never stops it has replaced one bill with another.
# That is why clause (4) keeps its CPU test, why (5b) requires a live kernel
# session and not just a stale record, and why (6) is a freshness window and
# not a "the directory exists" test.
#
# WHY THEY SIT HERE, AFTER (3), AND ARE NOT NUMBERED (1b)/(2b)/(2c). Every
# clause is keep-or-fall-through, so ORDER changes no decision -- only cost.
# Two facts fix the position: clause (4) needs the `cpu_ticks` helper defined
# above clause (2), and clause (6) pays a full inode walk on the QUIET path
# (measured 2026-09-03 with GNU find, the binary root cron actually gets:
# 7.07 s over 679,384 files under /home/ubuntu/certonomous-runs; ~0 s on the
# busy path, because `-print -quit` stops at the first match). Putting the
# expensive clause LAST means it only runs on a box the cheap clauses have
# already declined. Cron fires this every 5 min, so 7 s of one core on the
# idle path is 2.3% of one core, and it buys the backstop.
# ===========================================================================

# (4) A CONTAINER THAT IS BURNING CPU.
#
#     This is the clause the DAFoam sweeps needed. It does NOT ask what is
#     running inside -- that question is what defeated clause (1), because the
#     answer was `python` calling a library. It asks the two facts a container
#     cannot spell its way out of: docker says it is up, and its host-side pids
#     are moving CPU ticks.
#
#     `docker top <id> -o pid` returns HOST-NAMESPACE pids. Re-measured
#     2026-09-03 against a live probe container on this box: docker reported
#     pid 27788 and /proc/27788/stat existed on the host. So the EXISTING,
#     reviewed `cpu_ticks` sampler works unchanged on containerized processes,
#     and the >20-ticks-in-3s threshold that already separates a parked daemon
#     from a working suite separates a parked container from a solving one. No
#     new judgement is introduced.
#
#     THE PID PARSE IS PADDING-PROOF, and this is a correction to a predecessor
#     draft, not decoration. That draft filtered with `grep -E '^[0-9]+$'`.
#     Measured on this box, `docker top -o pid` emits unpadded lines
#     ("PID\n27788\n") so the grep happened to work -- but `docker top` shells
#     out to the HOST's ps, and ps right-aligns numeric columns on many
#     builds, where `^[0-9]+$` matches nothing, `cpids` comes back empty, and
#     the clause silently reports no containerized work at all. The awk below
#     takes the first all-numeric FIELD of each line after the header, which is
#     correct padded or not, and correct for `docker top`'s default column set
#     too.
#
#     THE CPU TEST IS NOT OPTIONAL, for the reason it was not optional in
#     clause (2): `docker ps -q` non-empty alone would let one forgotten
#     `docker run -d ... sleep infinity` pin this box for as long as it exists.
#     Measured 2026-09-03: 40 containers on this box, all Exited -- the lab
#     does leave them behind. An exited container is invisible to `docker ps`;
#     a detached idle one would not be.
#
#     ROOT AND THE DOCKER SOCKET, stated explicitly because it is the one
#     assumption that could make this clause a no-op: /var/run/docker.sock is
#     root:docker. This script runs from ROOT cron -- verified 2026-09-03 and
#     not assumed, by reading `journalctl -t auto-stop -o json`: every genuine
#     5-minute tick carries _UID=0, _GID=0 (the uid-1000 lines in that journal
#     are this lane's own tagged [DRY_RUN] tests). Root reaches the socket as
#     owner. The `ubuntu` user reaches it via group 113(docker) (measured:
#     `docker:x:113:ubuntu`), so the test suite works too. A future caller in
#     NEITHER position gets the INDETERMINATE path below, never a false idle.
if ! command -v "$DOCKER" >/dev/null 2>&1; then
    # DETERMINATE, not indeterminate: with no docker executable there can be
    # no running container, so this is a real negative and must not pin a box
    # that has never had docker on it. Loud, because a vanished docker on a
    # box that runs containerized sweeps is itself a finding.
    say "WARNING: no '$DOCKER' executable on PATH -- clause (4) is NOT APPLICABLE (no container can be running); clause (6) is the backstop"
else
    containers=$("$DOCKER" ps -q 2>/dev/null)
    docker_rc=$?
    if [ "$docker_rc" -ne 0 ]; then
        # INDETERMINATE. docker is installed and we cannot read it -- daemon
        # down, socket gone, permission denied. A containerized solve cannot
        # be ruled out, so this resolves to ALIVE. See DOCKER_BLIND_ALIVE
        # above for the cost this buys and the switch that undoes it.
        if [ "$DOCKER_BLIND_ALIVE" = "1" ]; then
            keep "INDETERMINATE: '$DOCKER ps' failed (rc=$docker_rc) -- docker is installed but unreadable, so a containerized solve CANNOT be ruled out; holding the box (set DOCKER_BLIND_ALIVE=0 to restore fall-through)"
        else
            say "WARNING: '$DOCKER ps' failed (rc=$docker_rc) and DOCKER_BLIND_ALIVE=0 -- clause (4) is BLIND to containerized solvers; clause (6) is the backstop"
        fi
    elif [ -n "$containers" ]; then
        cpids=""
        top_failed=""
        for cid in $containers; do
            p=$("$DOCKER" top "$cid" -o pid 2>/dev/null | awk 'NR>1 {for (i=1;i<=NF;i++) if ($i ~ /^[0-9]+$/) { print $i; break }}')
            if [ -z "$p" ]; then top_failed="$top_failed $cid"; continue; fi
            cpids="$cpids $p"
        done
        if [ -n "$top_failed" ]; then
            # THIS one IS a keep, and the difference from the rc!=0 case above
            # is only in what we know: there, whether any container exists at
            # all; here, we KNOW one is up and cannot judge it. Unknown state
            # over KNOWN work resolves to ALIVE. It is self-expiring, because a
            # container that exits stops being listed by `docker ps` next tick.
            keep "container(s) up but 'docker top' unreadable ($top_failed) -- cannot judge, treating as work"
        fi
        if [ -n "$cpids" ]; then
            cbefore=""
            for pid in $cpids; do cbefore="$cbefore $pid:$(cpu_ticks "$pid")"; done
            sleep 3
            for entry in $cbefore; do
                pid=${entry%%:*}; t0=${entry##*:}; t1=$(cpu_ticks "$pid")
                if [ "$(( t1 - t0 ))" -gt 20 ]; then
                    keep "container process pid $pid busy ($(( t1 - t0 )) CPU ticks in 3s)"
                fi
            done
        fi
    fi
fi

# (5) A QUEUE-LAUNCHED CHAIN THAT IS NOT FINISHED.
#
#     Two independent signals, because the brief's hardest case -- "a chain
#     between stages, where no solver binary is momentarily running but the
#     chain is not finished" -- is precisely where a single signal is thin.
#
#     (5a) THE WRAPPER'S OWN ARGV. Measured shape, not an invented pattern:
#          scripts/queue_runner.py:529-536 launches every queued case as
#              setsid nohup bash -c "cd '<cwd>' && <argv> > '<out>' 2>&1; \
#                  R=$?; echo \"launcher_rc=$R ...\" > '<cwd>/STATUS.queue.<id>'"
#          so the host sees comm `bash`, a cwd of entry["cwd"], and the literal
#          `STATUS.queue.` in argv. That wrapper lives until the WHOLE argv
#          finishes, which is exactly the between-stages case: mid-chain, the
#          wrapper is alive and idle and this clause sees it.
#
#          WHY THE EXISTING CLAUSES MISS IT. Clause (2) pgreps
#          python|python3|...|mpirun|mpiexec|dafoam|foamRun -- `bash` is not in
#          that list and never was. And entry["cwd"] for the sweeps that died
#          was /home/ubuntu/certonomous-runs/A1WR/STAGE12, OUTSIDE $REPO, so
#          even had `bash` been listed the cwd test would have rejected it.
#
#          WHY PRESENCE AND NOT CPU, the opposite of clause (2)'s choice. A
#          chain driver's own CPU is ~zero BY DESIGN: it is blocked in `wait`
#          on a `docker run` or a solver child that holds all the CPU. A CPU
#          test here would reject exactly the process the clause exists to see.
#          Presence is right for a driver and wrong for chief_engineer.server
#          because a driver EXITS when its case finishes and the server never
#          does. The pinning risk is bounded by construction: the lab's launch
#          argv are wall-capped (the sweeps ran under `timeout -k 60 37200`),
#          so a driver cannot outlive its cap. HONEST RESIDUAL: an argv
#          committed with no `timeout` could pin this box until killed. That is
#          a queue-entry defect, it is named in the journal line below, and it
#          is preferable to the 7h49m this clause exists to stop losing.
#
#          THE STRING MATCH, AND THE 2026-08-12 TRAP IT MUST NOT REPEAT. This
#          script was rewritten once because a command-line string test matched
#          a `grep` typed to investigate it. That cannot happen here, and it is
#          worth being precise rather than trusting it: the match requires comm
#          == `bash` EXACTLY (a grep, an editor or an ssh has its own comm),
#          AND a kernel-resolved cwd inside $REPO or a RUNROOT, AND the
#          launcher's OWN emitted signature `STATUS.queue.`. An investigator's
#          `grep STATUS.queue.` has comm `grep` and fails the first test before
#          the string is ever read.
#
#          NOT COUNTED, deliberately: `queue_runner.py --daemon` itself
#          (measured 2026-09-03: pid 1664, cwd /home/ubuntu/Certonomous, uid
#          ubuntu). It is a permanent daemon and clause (2) already, correctly,
#          declines it on the CPU test. This clause must not smuggle it back
#          in, which is why it keys on the `STATUS.queue.` argv the DRIVER
#          carries and the DAEMON does not.
for pid in $(pgrep -u ubuntu -x bash 2>/dev/null); do
    # THE `2>/dev/null` GOES FIRST, AND THAT ORDER IS THE WHOLE POINT.
    # Redirections are applied left to right, so `< /proc/$pid/cmdline
    # 2>/dev/null` attempts the INPUT redirect while stderr is still the
    # inherited one -- and a pid that exits between `pgrep` and this line (a
    # race that is guaranteed to happen on a busy box, not merely possible)
    # makes bash print `/proc/<pid>/cmdline: No such file or directory` to the
    # real stderr. Observed live on 2026-09-03 running this very file:
    #     scripts/auto_stop_patched.sh: line 586: /proc/80203/cmdline: ...
    # Under root cron that line becomes mail, every five minutes, from a
    # process whose entire job is to be quiet unless something is wrong. The
    # decision was never affected -- `|| continue` fires correctly either way,
    # verified both orders -- but an instrument that cries wolf on a routine
    # race trains its reader to ignore it, and the next line it prints will be
    # the one that mattered.
    cmdline=$(tr '\0' ' ' 2>/dev/null < /proc/"$pid"/cmdline) || continue
    case "$cmdline" in
        *STATUS.queue.*) ;;
        *) continue ;;
    esac
    cwd=$(readlink /proc/"$pid"/cwd 2>/dev/null) || continue
    [ -n "$cwd" ] || continue
    ok=""
    case "$cwd" in
        "$REPO"|"$REPO"/*) ok=1 ;;
    esac
    for root in $RUNROOTS; do
        case "$cwd" in
            "$root"|"$root"/*) ok=1 ;;
        esac
    done
    if [ -n "$ok" ]; then
        keep "queue-launched chain driver pid $pid alive (cwd $cwd)"
    fi
done

#     (5b) THE DAEMON'S OWN IN-FLIGHT BIT, CONJOINED WITH A LIVE SESSION.
#
#          (5a) reads a process. (5b) reads the DAEMON'S BOOKKEEPING, so a
#          chain that re-detaches and orphans its wrapper is still covered.
#          queue_runner.py stamps `_launch.status_seen_utc` on a launched
#          record exactly once, when it observes that case's STATUS file
#          (queue_runner.py:300 skips a record already stamped; :645-654 does
#          the stamping). A record WITHOUT that stamp is, in the daemon's own
#          words, still in flight.
#
#          THE RECORD ALONE IS NOT ENOUGH AND THE MEASUREMENT SAYS SO. On
#          2026-09-03 this repo held 303 launched records; 5 lacked the stamp
#          -- A1WR_chain.json (the chain THIS poweroff killed, sid 55739),
#          D4-SHIPPED_ACC_F3, D7FR_F-P, D7FR_F-S, W3_chain_r4 -- and ZERO of
#          the 5 had a live session. A clause keyed on the record alone would
#          pin this box permanently, today, on five dead rows. So the clause
#          requires the kernel to agree: `_launch.sid` must still name a live
#          session in `ps -eo sid=`. The record says "not finished"; the
#          kernel says "still there". Neither party is guessing, and the
#          conjunction expires by itself when the session dies -- which is the
#          property clause (0)'s hold file had to be given by hand.
#
#          COST: one `grep -L` over the launched records to find the unstamped
#          few (5 of 303 today), then one `ps`. Not a per-record fork.
#
#          QUEUE_ROOT derives from $REPO, so a test injecting a scratch REPO
#          reads a scratch queue and can never be held alive by the real one.
if [ -d "$QUEUE_ROOT" ]; then
    unstamped=$(grep -L '"status_seen_utc"' "$QUEUE_ROOT"/*/launched/*.json 2>/dev/null)
    if [ -n "$unstamped" ]; then
        live_sids=" $(ps -eo sid= 2>/dev/null | tr -s ' ' '\n' | grep -E '^[0-9]+$' | sort -u | tr '\n' ' ') "
        for rec in $unstamped; do
            sid=$(grep -o '"sid"[[:space:]]*:[[:space:]]*[0-9][0-9]*' "$rec" 2>/dev/null | head -1 | grep -o '[0-9][0-9]*$')
            [ -n "$sid" ] || continue
            case "$live_sids" in
                *" $sid "*)
                    keep "queue record still in flight and its session is alive (sid $sid, $rec)"
                    ;;
            esac
        done
    fi
fi

# (6) A RUN TREE WRITTEN TO RECENTLY.
#
#     THE BACKSTOP, and the clause that would have saved the run on its own.
#     It asks the one question nobody asked at 02:25:05Z: is anything on this
#     box still WRITING? Measured after the fact -- the newest mtime under
#     /home/ubuntu/certonomous-runs was 2026-09-03 02:24:58.535, SEVEN SECONDS
#     before this script logged `idle 34min, shutting down`.
#
#     It is namespace-proof and uid-proof in a way clauses (1) and (2) cannot
#     be, which is exactly why it is the backstop: a bind-mounted write lands
#     on the HOST inode whatever the container calls the path and whatever uid
#     made it. The sweeps' `/mnt/out/sweep.log` IS
#     /home/ubuntu/certonomous-runs/A1WR/STAGE12/sweep_C/out/sweep.log.
#
#     WHY A REFERENCE FILE AND NOT `-newermt "-20 min"`. This is the second
#     correction to a predecessor draft, and it is the same defect this file's
#     clause (3) comment already records, reintroduced. `bfs`, which this
#     lab's interactive shells resolve `find` to, REJECTS a relative
#     `-newermt` timestamp. Re-measured 2026-09-03, verbatim:
#         bfs: error: ... -newermt "-20 min" ... Invalid timestamp.
#     Under root cron `find` is /usr/bin/find (GNU findutils) and `-newermt`
#     works -- proven independently by clause (3) firing correctly in the
#     journal every 5 minutes -- so the draft was not broken WHERE IT RUNS.
#     But it was broken wherever anyone tests it, and a clause whose test
#     environment and production environment disagree is a clause nobody can
#     check. `touch -d` a reference file and use `-newer <file>`: measured
#     2026-09-03 to work identically under BOTH bfs 4.1.1 and GNU find,
#     including the positive control -- a file touched now is FOUND by both.
#     Same answer, one fewer way to be silently wrong.
#
#     `-print -quit` stops at the first match, so the cost is ~0 s whenever the
#     answer is yes and 7.07 s over 679,384 files when it is no (measured with
#     GNU find). The expensive path is the idle one, which is the right way
#     round.
#
#     A SCAN THAT CANNOT SEE RESOLVES TO ALIVE, not to idle. This is the
#     backstop; a blind backstop is the 02:25:05Z hole reopened. A missing root
#     is different and stays a loud line: a directory that does not exist is a
#     determinate negative, not an unreadable one.
run_ref=$(mktemp 2>/dev/null)
if [ -z "$run_ref" ] || ! touch -d "-${RUN_FRESH_MINUTES} minutes" "$run_ref" 2>/dev/null; then
    rm -f "$run_ref"
    keep "INDETERMINATE: clause (6) could not build its ${RUN_FRESH_MINUTES}min reference file -- the backstop cannot see, so it cannot report idle"
fi
for root in $RUNROOTS; do
    if [ ! -d "$root" ]; then
        # Same doctrine as clause (3)'s empty glob: a missing subject is not an
        # idle box, and it is not a keep either. It is a loud line.
        say "WARNING: run root '$root' does not exist -- clause (6) cannot see it"
        continue
    fi
    run_err=$(mktemp)
    hot=$(find "$root" -newer "$run_ref" -type f -print -quit 2>"$run_err")
    if [ -s "$run_err" ]; then
        first_err=$(head -1 "$run_err")
        rm -f "$run_err" "$run_ref"
        keep "INDETERMINATE: run-tree scan of '$root' errored, the backstop is BLIND so it must not report idle: $first_err"
    fi
    rm -f "$run_err"
    # The file is NAMED, for the reason clause (3) names its transcript: the
    # next person reading `journalctl -t auto-stop` after an unexplained
    # shutdown gets to see WHICH write held the box, or that none did.
    if [ -n "$hot" ]; then
        rm -f "$run_ref"
        keep "run tree written within ${RUN_FRESH_MINUTES}min ($hot)"
    fi
done
rm -f "$run_ref"

if [ "$idle" -ge "$IDLE_MINUTES" ]; then
    say "idle ${idle}min, shutting down"
    [ -n "$DRY_RUN" ] && { echo "DRY_RUN: would run 'sudo shutdown -h now'"; exit 0; }
    sudo shutdown -h now
    # ADDED 2026-09-03 (cfd lane): AN EVIDENCE DEFECT, not a behaviour one.
    # `shutdown -h now` SCHEDULES the halt and RETURNS, so control fell through
    # to the line below and the journal recorded, at the same second (measured,
    # journalctl -b -1 -t auto-stop, 2026-09-03):
    #     02:25:05 auto-stop[348771]: idle 34min, shutting down
    #     02:25:05 auto-stop[348774]: idle 34min, under threshold 30min -- no action
    # The second line is false on its own terms -- 34 is not under 30 -- and it
    # tells anyone reconstructing the poweroff that the script decided NOT to
    # act, directly beneath the line where it did. This file's own doctrine is
    # that an instrument must not forge the evidence it exists to produce; that
    # standard applies to a reassuring line as much as to a shutdown line.
    exit 0
fi
say "idle ${idle}min, under threshold ${IDLE_MINUTES}min -- no action"
