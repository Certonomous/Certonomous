#!/usr/bin/env bash
# queue_runner_gate_control.sh -- planted-failure control for the FAIL-CLOSED selftest
# gate in queue_runner.sh.
#
# WHY THIS EXISTS. The gate was added because a control that never runs is not a guard
# (verification cross-team audit of bec46169, finding 5). A GATE WHOSE REFUSAL PATH HAS
# NEVER FIRED IS THE SAME DEFECT ONE LEVEL UP: it would be a refusal nobody has seen
# refuse. So the refusal is driven here, deliberately, against a planted failure.
#
# WHAT IT DRIVES. THE REAL scripts/queue_runner.sh, copied into a scratch tree with only
# its REPO path rewritten, against a STUB queue_runner.py whose --selftest rc is planted
# by $STUB_SELFTEST_RC. The gate logic under test is the real file's, not a restatement:
# a control that re-implements the mechanism grades its own re-implementation.
#
#   control + : selftest rc 0 -> daemon IS started, wrapper rc 0, NO marker written
#   control - : selftest rc 1 -> daemon NOT started, wrapper rc 3, marker names the rc
#               and carries the failing check line
#
# NOTHING REAL IS TOUCHED: the scratch tree is a mkdtemp, the stub never launches a
# solver, and the live runner's pidfile is never read or written.
set -u
REAL_WRAPPER="$(cd "$(dirname "$0")" && pwd)/queue_runner.sh"
TMP=$(mktemp -d -t queue_runner_gate_control_XXXXXX)
trap 'rm -rf "$TMP"' EXIT
ok=0; fail=0
say() { if [ "$1" = 0 ]; then printf '  ok   %s\n' "$2"; ok=$((ok+1)); else printf '  FAIL %s\n' "$2"; fail=$((fail+1)); fi; }

mkdir -p "$TMP/scripts" "$TMP/verification/queue"

# The stub stands in for queue_runner.py. --selftest exits with the planted rc and prints
# a realistic tally line; --daemon records that it was reached and exits.
cat > "$TMP/scripts/queue_runner.py" <<'STUB'
import os, sys, pathlib
rc = int(os.environ.get("STUB_SELFTEST_RC", "0"))
if "--selftest" in sys.argv:
    if rc:
        print("  FAIL planted control failure (this is the negative limb)")
        print("SELFTEST FAIL: 1 of 1 checks failed")
    else:
        print("  ok   planted control")
        print("SELFTEST PASS: 1/1 checks, 0 asserts")
    sys.exit(rc)
if "--daemon" in sys.argv:
    pathlib.Path(os.environ["STUB_DAEMON_MARK"]).write_text("daemon reached\n")
    sys.exit(0)
sys.exit(64)
STUB

# The real wrapper with ONLY its REPO line repointed at the scratch tree.
sed "s|^REPO=.*|REPO=$TMP|" "$REAL_WRAPPER" > "$TMP/scripts/queue_runner.sh"
chmod +x "$TMP/scripts/queue_runner.sh"
if grep -q "^REPO=$TMP\$" "$TMP/scripts/queue_runner.sh"; then
  say 0 "setup: the REAL wrapper is under test, repointed at a scratch REPO"
else
  say 1 "setup: REPO rewrite did not take -- the control would be testing nothing"
  printf 'CONTROL ABORTED\n'; exit 2
fi
# The gate must be present in the file under test, or both limbs would pass vacuously.
grep -q -- "--selftest" "$TMP/scripts/queue_runner.sh" \
  && say 0 "setup: the wrapper under test actually invokes --selftest" \
  || say 1 "setup: no --selftest in the wrapper -- there is no gate to control"

export STUB_DAEMON_MARK="$TMP/DAEMON_REACHED"

# ---------------------------------------------------------------- control +
rm -f "$STUB_DAEMON_MARK" "$TMP"/verification/queue/RUNNER_SELFTEST_FAILED.*
STUB_SELFTEST_RC=0 bash "$TMP/scripts/queue_runner.sh"; rc_pass=$?
for _ in 1 2 3 4 5 6 7 8 9 10; do [ -f "$STUB_DAEMON_MARK" ] && break; sleep 0.2; done
started_pass=no; [ -f "$STUB_DAEMON_MARK" ] && started_pass=yes
markers_pass=$(ls "$TMP"/verification/queue/RUNNER_SELFTEST_FAILED.* 2>/dev/null | wc -l)
[ "$rc_pass" = 0 ] && [ "$started_pass" = yes ] && [ "$markers_pass" = 0 ] \
  && say 0 "control + : selftest PASS -> daemon STARTED, wrapper rc 0, no marker  [rc=$rc_pass started=$started_pass markers=$markers_pass]" \
  || say 1 "control + : expected rc 0 / started yes / markers 0  [rc=$rc_pass started=$started_pass markers=$markers_pass]"

# ---------------------------------------------------------------- control -
rm -f "$STUB_DAEMON_MARK" "$TMP"/verification/queue/RUNNER_SELFTEST_FAILED.*
STUB_SELFTEST_RC=1 bash "$TMP/scripts/queue_runner.sh"; rc_fail=$?
for _ in 1 2 3 4 5; do [ -f "$STUB_DAEMON_MARK" ] && break; sleep 0.2; done
started_fail=no; [ -f "$STUB_DAEMON_MARK" ] && started_fail=yes
mark=$(ls "$TMP"/verification/queue/RUNNER_SELFTEST_FAILED.* 2>/dev/null | head -1)
[ "$rc_fail" = 3 ] && [ "$started_fail" = no ] \
  && say 0 "control - : selftest FAIL -> daemon NOT started, wrapper rc 3  [rc=$rc_fail started=$started_fail]" \
  || say 1 "control - : expected rc 3 / started no  [rc=$rc_fail started=$started_fail]"

# The refusal must ANNOUNCE ITSELF -- that is the whole mitigation for fail-closed.
if [ -n "$mark" ] && grep -q "rc=1" "$mark" && grep -q "planted control failure" "$mark"; then
  say 0 "control - : marker written, names rc=1 AND carries the failing check line"
else
  say 1 "control - : marker missing or does not name the rc and failing check  [mark=${mark:-none}]"
fi
grep -q "SELFTEST FAILED rc=1" "$TMP/verification/queue/runner.restarts.log" 2>/dev/null \
  && say 0 "control - : refusal logged to runner.restarts.log" \
  || say 1 "control - : refusal NOT logged to runner.restarts.log"
grep -q "SELFTEST-GATE" "$TMP/verification/queue/runner.log" 2>/dev/null \
  && say 0 "control - : refusal logged to runner.log, where a reader looks" \
  || say 1 "control - : refusal NOT logged to runner.log"

# The marker must have a FIXED NAME. A per-attempt name would put 1,440 files a day in
# the queue root during exactly the incident someone is reading, and would force the
# reader to sort filenames to find the current one (cfd-supervisor ruling 2026-08-31).
[ "$(basename "${mark:-none}")" = "RUNNER_SELFTEST_FAILED.txt" ] \
  && say 0 "control - : marker has the FIXED name RUNNER_SELFTEST_FAILED.txt, not a per-attempt name" \
  || say 1 "control - : marker name is not fixed  [$(basename "${mark:-none}")]"

# --------------------------------------- control -- : a SECOND failure OVERWRITES
# This is the limb that would have caught the original defect: it accumulated, and
# nothing asserted that it did not.
first_body=$(cat "$mark" 2>/dev/null | head -1)
STUB_SELFTEST_RC=1 bash "$TMP/scripts/queue_runner.sh" >/dev/null 2>&1
n_marks=$(ls "$TMP"/verification/queue/RUNNER_SELFTEST_FAILED* 2>/dev/null | wc -l)
second_body=$(cat "$TMP/verification/queue/RUNNER_SELFTEST_FAILED.txt" 2>/dev/null | head -1)
[ "$n_marks" = 1 ] \
  && say 0 "control -- : a SECOND failure OVERWRITES -- exactly one marker file, never a pile  [n=$n_marks]" \
  || say 1 "control -- : markers ACCUMULATED across failures  [n=$n_marks]"
[ -n "$second_body" ] && [ "$second_body" != "$first_body" ] \
  && say 0 "control -- : the overwritten marker describes the LATEST attempt (its stamp moved)" \
  || say 1 "control -- : marker did not refresh on the second failure"

# --------------------------------------- control + + : recovery CLEARS the marker
# A marker that outlives its condition is an evidence line that lies: it would sit
# beside a healthy daemon. Same class as the finding-6 log-line defect.
rm -f "$STUB_DAEMON_MARK"
STUB_SELFTEST_RC=0 bash "$TMP/scripts/queue_runner.sh" >/dev/null 2>&1
for _ in 1 2 3 4 5 6 7 8 9 10; do [ -f "$STUB_DAEMON_MARK" ] && break; sleep 0.2; done
cleared=no; [ ! -f "$TMP/verification/queue/RUNNER_SELFTEST_FAILED.txt" ] && cleared=yes
[ "$cleared" = yes ] && [ -f "$STUB_DAEMON_MARK" ] \
  && say 0 "control + + : a successful start CLEARS the stale marker (it cannot outlive its condition)" \
  || say 1 "control + + : stale marker survived a successful start  [cleared=$cleared]"
grep -q "cleared RUNNER_SELFTEST_FAILED" "$TMP/verification/queue/runner.log" 2>/dev/null \
  && say 0 "control + + : the clearing is LOGGED, so recovery stays visible instead of vanishing" \
  || say 1 "control + + : marker cleared SILENTLY -- the recovery left no record"

# ------------------------------------------------- control -- : already-alive short circuit
# A live runner must short-circuit BEFORE the gate, or every cron minute would pay 5 s of
# selftest and a restart storm would serialise behind it.
rm -f "$STUB_DAEMON_MARK"
echo $$ > "$TMP/verification/queue/runner.pid"     # this shell: certainly alive
STUB_SELFTEST_RC=1 bash "$TMP/scripts/queue_runner.sh"; rc_alive=$?
[ "$rc_alive" = 0 ] && [ ! -f "$STUB_DAEMON_MARK" ] \
  && say 0 "control -- : a LIVE runner short-circuits before the gate (rc 0, no selftest paid, nothing started)" \
  || say 1 "control -- : live-runner short circuit broken  [rc=$rc_alive]"
rm -f "$TMP/verification/queue/runner.pid"

printf '\n'
if [ "$fail" -ne 0 ]; then printf 'GATE CONTROL FAIL: %s of %s checks failed\n' "$fail" "$((ok+fail))"; exit 1; fi
printf 'GATE CONTROL PASS: %s/%s checks\n' "$ok" "$((ok+fail))"
