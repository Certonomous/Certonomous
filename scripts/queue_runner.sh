#!/usr/bin/env bash
# queue_runner.sh -- start scripts/queue_runner.py detached IF it is not already running.
# Idempotent: safe to call from cron every minute and from @reboot. The runner's own
# pidfile lock (verification/queue/runner.pid + liveness check) refuses a second copy,
# so this wrapper cannot start two. Sanaa, 2026-08-26 (73eccb1b): "I do NOT want the
# instances to be idle at any point even if the lab dies."
#
# ===========================================================================
# FAIL-CLOSED SELFTEST GATE -- 2026-08-31, cfd-supervisor ruling, after
# verification's cross-team audit of bec46169 (finding 5).
#
# WHY. The round-robin scheduler carried an ABSORBING-STATE defect that gave
# twenty consecutive launches to one team while starving the other five. It
# survived 41 existing selftest checks. The repair added a control (R1/R1-NEG)
# that DOES discriminate -- 40 of 63 team subsets starve under the old logic
# and none under the new -- but that control was wired into NOTHING: the
# wrapper launched --daemon, check_harness.py never called --selftest, and no
# hook or cron ran it. It had fired exactly once, by hand, before deploy.
# A CONTROL THAT DISCRIMINATES BUT NEVER RUNS SITS EXACTLY WHERE THE ABSENT
# CONTROL SAT THE DAY BEFORE. It is not a guard, it is a memory of a guard.
# So the gate goes on the runner's OWN start path, which fires at the one
# moment that matters: every deploy and every restart.
#
# NOT check_harness.py -- that is shared harness tooling and not cfd's to gate.
# This wrapper is unambiguously the runner's own.
#
# WHY FAIL-CLOSED, on tonight's evidence. A DARK RUNNER IS LOUD: queue depth
# climbs and it is noticed in minutes. A MIS-SCHEDULING RUNNER IS SILENT: it
# ran twenty launches before anyone saw it. When one failure mode announces
# itself and the other does not, choose the one that announces itself.
#
# THE HONEST RISK, stated here and not only in a report: a selftest failure
# for an UNRELATED reason -- git unavailable at boot, a transient, a broken
# interpreter -- leaves the lab WITH NO RUNNER, which cuts against Sanaa's
# standing never-idle order. That is a real cost and it is accepted knowingly,
# with one mandatory mitigation: the condition must ANNOUNCE ITSELF rather
# than present as unexplained silence, so on failure this script writes
# RUNNER_SELFTEST_FAILED.<utc>.txt beside runner.log carrying the rc and the
# failing check names, and logs the refusal to runner.log and runner.restarts.log.
#
# DELIBERATELY ABSENT, and neither is an oversight:
#   * NO RETRY LOOP. A retry converts a hard refusal into a slow one and hides
#     the very condition the marker exists to announce.
#   * NO BYPASS FLAG. A bypass is how fail-closed decays into advisory, and
#     this repository holds the live proof of that decay in this very runner:
#     cap enforcement (D539) has sat ADVISORY / INERT / OFF since 2026-08-27
#     while CLAUDE.md rule 12 says an overrun stops the run. If this gate ever
#     needs to be off, it is edited here, in the open, by someone who owns it.
#
# The selftest is LOAD-INDEPENDENT by construction -- all 21 of its tick()
# calls inject `measure=` (the L-339 repair); the only non-injecting call is
# the live daemon's own. Measured 5.14 s wall at load average 13.35, so a busy
# box cannot flake it and it costs ~5 s on the critical path of a restart.
# Refusal path proven by scripts/queue_runner_gate_control.sh.
# ===========================================================================
REPO=/home/ubuntu/Certonomous
PIDFILE=$REPO/verification/queue/runner.pid
QDIR=$REPO/verification/queue
if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE" 2>/dev/null)" 2>/dev/null; then
  exit 0   # alive; nothing to do
fi
cd "$REPO" || exit 1

# ---------------------------------------------------------------- the gate
SELFTEST_OUT=$(python3 "$REPO/scripts/queue_runner.py" --selftest 2>&1)
SELFTEST_RC=$?
if [ "$SELFTEST_RC" -ne 0 ]; then
  UTC=$(date -u +%FT%TZ)
  MARK="$QDIR/RUNNER_SELFTEST_FAILED.$(date -u +%Y%m%dT%H%M%SZ).txt"
  {
    printf '%s RUNNER NOT STARTED -- queue_runner.py --selftest FAILED, rc=%s\n\n' "$UTC" "$SELFTEST_RC"
    printf 'The queue runner is FAIL-CLOSED on its own selftest (see the header of\n'
    printf 'scripts/queue_runner.sh for why). NOTHING IS SCHEDULED while this file is\n'
    printf 'the newest RUNNER_SELFTEST_FAILED marker and no runner is alive.\n\n'
    printf 'THIS IS NOT A SILENT FAILURE AND MUST NOT BE TREATED AS ONE: the queue is\n'
    printf 'not draining because the runner REFUSED TO START, not because it is idle.\n\n'
    printf -- '--- failing checks and verdict line ---\n'
    printf '%s\n' "$SELFTEST_OUT" | grep -E '^  FAIL|^SELFTEST|^REFUSE' || printf '(no FAIL/SELFTEST line -- the selftest did not reach its tally; see full output)\n'
    printf -- '\n--- full --selftest output ---\n'
    printf '%s\n' "$SELFTEST_OUT"
  } > "$MARK"
  printf '%s queue_runner.sh: SELFTEST FAILED rc=%s -- RUNNER NOT STARTED; see %s\n' \
      "$UTC" "$SELFTEST_RC" "$MARK" >> "$QDIR/runner.restarts.log"
  printf '%s SELFTEST-GATE: runner NOT started, --selftest rc=%s -- see %s\n' \
      "$UTC" "$SELFTEST_RC" "$MARK" >> "$QDIR/runner.log"
  exit 3
fi

setsid nohup python3 "$REPO/scripts/queue_runner.py" --daemon >> "$QDIR/runner.out" 2>&1 < /dev/null &
# `$!` is the setsid pid, not the daemon's own; the daemon writes the authoritative
# pid to runner.pid itself. Pre-existing behaviour, recorded rather than changed.
echo "$(date -u +%FT%TZ) queue_runner.sh: (re)started runner pid $! (--selftest PASS)" >> "$QDIR/runner.restarts.log"
