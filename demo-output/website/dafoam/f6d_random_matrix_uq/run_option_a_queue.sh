#!/bin/bash
# F6d Option A queue runner.
# Survives the death of any agent: it is launched with setsid and holds its own
# concurrency limit.
#
# ---------------------------------------------------------------------------
# WHY THE CLAIM DIRECTORY EXISTS. On 2026-08-11 two durable launchers ran over
# this same case set and two simpleFoam processes shared `d0.2_s000`, one of the
# three controls. The guard below used to be `[ -f log.simpleFoam ]` evaluated
# ONCE, at the top of the loop, and then the loop slept in an unbounded wait for
# the job pool to drain before launching. A case that acquired a log DURING that
# wait was launched anyway. Reproduced: with the pool saturated, two launchers
# both passed the file test, both slept 20 s, and the second reached its launch
# 200 ms after the first had already created the log -- a 20.04 s window in which
# the answer the guard was acting on had been false the whole time.
#
# A GUARD CHECKED BEFORE AN UNBOUNDED WAIT IS NOT A GUARD (LESSONS.md L-69).
# And moving the file test closer to the launch would not have fixed it: a file
# existence test is test-then-act, so there is always a window between the test
# and the launch, however small. It can be narrowed and never closed. What is
# needed is an operation that decides the winner atomically, which is why the
# claim below is `mkdir` -- on any POSIX filesystem exactly one of N concurrent
# callers succeeds and the rest get EEXIST, in one indivisible step. (`set -o
# noclobber` with `>` on a lock file has the same succeed-or-fail-atomically
# property and would serve equally.)
#
# WHY A DUPLICATE IS DANGEROUS RATHER THAN MERELY WASTEFUL. `system/controlDict`
# carries `startFrom latestTime`, so **a duplicate launch is a FORK, not a
# repeat.** It does not harmlessly redo work already done: it restarts from
# whatever snapshot the survivor has most recently written and then competes for
# THE SAME SNAPSHOT FILENAMES. In the incident the duplicate ran for about 60
# seconds, crossed one write time, and completely overwrote the survivor's
# `7500/` directory plus nine `singleGraph_x*/7500/` profile files. That data is
# gone -- overwritten in place, not corrupted, not recoverable -- and one point
# of a published trajectory is the duplicate's output. See
# campaign/F6D_COLLISION_INDEPENDENCE_CHECK.md and LESSONS.md L-64, L-69.
#
# "No output exists yet" is not a claim on a case, because output appears only
# after the race has already been lost. The claim below is the claim.
# ---------------------------------------------------------------------------
ROOT=/home/ubuntu/Certonomous/demo-output/website/dafoam/f6d_random_matrix_uq/f6d_option_a
MAXJOBS=8
REMAINING="d0.2_s000 d0.2_s027 d0.6_s011 d0.6_s021 d0.6_s022 d0.6_s035 d0.6_s039 null"

# Claims live beside the cases, never inside them: a case directory holds only
# solver output, and the mtimes in there are forensic evidence (a snapshot
# directory older than the files inside it is how the 2026-08-11 overwrite was
# detected). Writing into a case to coordinate about the case would erase that.
CLAIMS="$ROOT/.launch_claims"

source /usr/lib/openfoam/openfoam2606/etc/bashrc || exit 91

mkdir -p "$CLAIMS" || exit 92

for c in $REMAINING; do
  # Cheap early skip: do not queue behind the job pool for a case that is
  # already running or finished. This is an optimisation ONLY -- it is not the
  # guard, and nothing may rely on it, because by the time we stop waiting it
  # may be stale. That mistaken reliance is the entire defect this file records.
  if [ -f "$ROOT/$c/log.simpleFoam" ]; then
    continue                      # already started by someone else
  fi

  while [ "$(pgrep -c simpleFoam || true)" -ge "$MAXJOBS" ]; do
    sleep 20
  done

  # ---- everything from here to the launch is adjacent to the launch ----

  # (1) Atomic claim. Succeeds for exactly one caller; every other launcher,
  #     including one that passed the early skip in the same instant, fails
  #     here and moves on. This is what makes durability unique per work unit
  #     rather than merely present (L-64).
  if ! mkdir "$CLAIMS/$c" 2>/dev/null; then
    echo "queue_runner: $c is claimed by $(cat "$CLAIMS/$c/owner" 2>/dev/null || echo 'another launcher') -- skipping" >&2
    continue
  fi
  printf 'pid=%s host=%s started=%s\n' "$$" "$(hostname)" "$(date -u +%FT%TZ)" \
      > "$CLAIMS/$c/owner"

  # (2) Re-check the log AFTER claiming and immediately before launching. The
  #     claim only excludes launchers that take claims; a launcher that does not
  #     (the agent pool that caused the incident did not) is still caught here.
  #     Two guards of different kinds, both adjacent to the action.
  if [ -f "$ROOT/$c/log.simpleFoam" ]; then
    echo "queue_runner: $c acquired a log during the wait -- NOT launching" >&2
    continue                      # claim is retained deliberately; see below
  fi

  cd "$ROOT/$c" || continue
  setsid nohup simpleFoam > "$ROOT/$c/log.simpleFoam" 2>&1 < /dev/null &
  sleep 3
done

wait
echo "queue_runner: all remaining cases launched" > "$ROOT/.queue_runner_done"

# CLAIMS ARE NOT RELEASED, AND THAT IS DELIBERATE. A claim that expires or is
# cleaned up on exit is not exclusive -- it is a lease, and a lease races with
# the next launcher exactly as the file test did. A stale claim blocks a re-run
# of that case, which is the SAFE direction to fail: a case that does not start
# is visible and costs one restart, a case that starts twice silently destroys a
# snapshot. To genuinely re-run a case, remove its claim by hand, having first
# confirmed no solver is live on it:
#     pgrep -a simpleFoam | grep <case>      # must be empty
#     rm -rf .launch_claims/<case>
