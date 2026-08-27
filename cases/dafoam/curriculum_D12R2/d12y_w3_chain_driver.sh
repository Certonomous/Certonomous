#!/usr/bin/env bash
# W3 chain driver -- ONE detached process for phases 1 -> 4 of the W3 item
# (cases/dafoam/curriculum_D12R2/W3_PREREGISTRATION.md sec.5), so that no phase is a
# separate runner entry and no wait-wrapper waits on an artefact a no-launch branch will
# never write (the W2R lesson: four wrappers still waiting at their bounds).
#
# Sequence, stopping at the FIRST non-zero rc and recording every rc:
#   phase 1 (33 stages)  ->  comparator --plan  (host python3, writes step_plan.json)
#   phase 2 (the sweep)  ->  comparator --plan2 (writes step_plan2.json)
#   phase 3 (h*, S6b/S6c)->  comparator --plan3 (writes step_plan3.json, G12R-11 authorisation)
#   phase 4 (S8)
# EVERY later phase refuses FOR ITSELF on an absent precondition (the launcher's own
# `[ -f step_plan*.json ] || ABORT exit 1`, its `admissible:false` / `h_star=None` /
# `optimisation_authorised!=True` no-launch branches exit 0 launching nothing, and the
# comparator's plan modes exit 2 on a Refusal); this driver evaluates no precondition
# and decides nothing -- it sequences, records, and stops.  A stop at a registered
# no-launch branch is the registered terminus (NOT A RESULT for the FD line), not a
# failure of the driver.
# Started ONLY detached (the queue runner's setsid nohup form, or the same by hand under
# bc0e687e); cwd is the CASE directory (the plan-step STATUS files land here), the run
# root is the launcher's.  rc of each step is captured INSIDE this detached session.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
LAUNCHER="$HERE/d12y_w3_stage_and_run.sh"
GRADEPY="$HERE/d12y_grade_w3.py"
ROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3-cylinder-unsteady
PERMISSION=bc0e687e
# W3 AMENDMENT 1 (2026-08-27), W3-LAUNCHER-DEF-1: launcher md5 fc7585cf... -> 5563d8a8...
# (two operative cap DEFAULTS corrected to the values the frozen registration already
# named; no gate, threshold, cap, band or label moves -- 900.0/400.0 is what sec.4 says).
# W3 AMENDMENT 2 (2026-08-27), R-RC-4: launcher 5563d8a8... -> 20f8c0c51593576bddaa8a410659d997 (the fatal/signal log scan).
MD5_LAUNCHER=20f8c0c51593576bddaa8a410659d997
# W3 AMENDMENT 2 (2026-08-27), RULING R-RC (Sanaa APPROVED, standing directives sec.0):
# comparator f3c1252c... -> 3b0a75079c932b41ec19477388498842. The driver asserts this at :38 before every step;
# a stale pin here is the D8R-DRIVER-DEF-1 death and the assertion below is what catches it.
MD5_GRADER=3b0a75079c932b41ec19477388498842
STATUS="$HERE/STATUS.W3_chain"
utc () { date -u +%Y-%m-%dT%H:%M:%SZ; }
rec () { echo "stamp=$(utc) driver=d12y_w3_chain_driver.sh $*" | tee -a "$STATUS"; }
cd "$HERE" || exit 4
echo "$MD5_LAUNCHER  $LAUNCHER" | md5sum -c - >/dev/null || { rec "rc=4 event=ABORT reason=launcher_md5_drifted"; exit 4; }
echo "$MD5_GRADER  $GRADEPY" | md5sum -c - >/dev/null || { rec "rc=4 event=ABORT reason=grader_md5_drifted"; exit 4; }
# ---- G-ROOT.5 for the driver itself: a live prefix container or a live sibling driver refuses
LIVE=$(sudo -n docker ps --format '{{.Names}}' 2>/dev/null | grep '^d12y_w3_' | head -3 | tr '\n' ',' | sed 's/,$//')
[ -n "$LIVE" ] && { rec "rc=3 event=G_ROOT5_REFUSED live_prefix_containers=[$LIVE] note=NOTHING-RUN"; exit 3; }
PIDFILE="$ROOT/d12y_w3_driver.pid"
if [ -f "$PIDFILE" ]; then
  OPID=$(tr -dc '0-9' < "$PIDFILE" | head -c 12)
  if [ -n "$OPID" ] && [ "$OPID" != "$$" ] && kill -0 "$OPID" 2>/dev/null; then rec "rc=3 event=G_ROOT5_REFUSED live_driver_pid=$OPID note=two-records-for-one-run-is-the-defect NOTHING-RUN"; exit 3; fi
fi
# phase 1 REQUIRES an absent root (the launcher refuses exit 6 otherwise); the pidfile is
# written inside the root the launcher creates, so it is written AFTER phase 1 starts the
# root -- until then the prefix-container reading above is the live guard.
SID=$(ps -o sid= -p $$ 2>/dev/null | tr -d ' ')
rec "event=START pid=$$ sid=${SID:-?} ppid=$PPID root=$ROOT permission=$PERMISSION"
[ -e "$ROOT" ] && { rec "rc=6 event=ROOT_EXISTS root=$ROOT note=phase-1-requires-an-absent-root; a completed phase is not deleted to re-run it. NOTHING-RUN"; exit 6; }
step () {   # step <label> <cmd...>
  local LABEL="$1"; shift
  rec "event=BEGIN step=$LABEL"
  "$@" > "$HERE/W3_${LABEL}.out" 2>&1
  local rc=$?
  rec "rc=$rc event=END step=$LABEL out=W3_${LABEL}.out"
  return $rc
}
CHAIN_RC=0
step phase1 bash "$LAUNCHER" --phase 1 || CHAIN_RC=$?
if [ "$CHAIN_RC" -eq 0 ] && [ -d "$ROOT" ]; then echo "$$" > "$PIDFILE"; trap 'rm -f "$PIDFILE"' EXIT; fi
[ "$CHAIN_RC" -eq 0 ] && { step plan   python3 "$GRADEPY" --manifest "$ROOT/manifest.jsonl" --root "$ROOT" --plan  || CHAIN_RC=$?; }
[ "$CHAIN_RC" -eq 0 ] && { step phase2 bash "$LAUNCHER" --phase 2 || CHAIN_RC=$?; }
[ "$CHAIN_RC" -eq 0 ] && { step plan2  python3 "$GRADEPY" --manifest "$ROOT/manifest.jsonl" --root "$ROOT" --plan2 || CHAIN_RC=$?; }
[ "$CHAIN_RC" -eq 0 ] && { step phase3 bash "$LAUNCHER" --phase 3 || CHAIN_RC=$?; }
[ "$CHAIN_RC" -eq 0 ] && { step plan3  python3 "$GRADEPY" --manifest "$ROOT/manifest.jsonl" --root "$ROOT" --plan3 || CHAIN_RC=$?; }
[ "$CHAIN_RC" -eq 0 ] && { step phase4 bash "$LAUNCHER" --phase 4 || CHAIN_RC=$?; }
if [ "$CHAIN_RC" -eq 0 ]; then rec "chain=COMPLETE rc=0"; else rec "chain=STOPPED_AT_FIRST_NONZERO rc=$CHAIN_RC note=a-stop-at-a-registered-no-launch-branch-is-the-registered-terminus"; fi
[ -f "$ROOT/step_plan.json" ] && rec "step_plan=$(python3 -c "import json;d=json.load(open('$ROOT/step_plan.json'));print('admissible=%s h_min=%s W=%s delta_window_exact=%s envelope=%s' % (d.get('admissible'),d.get('h_min'),d.get('W'),d.get('delta_window_exact'),d.get('delta_window_envelope')))" 2>/dev/null)"
exit "$CHAIN_RC"
