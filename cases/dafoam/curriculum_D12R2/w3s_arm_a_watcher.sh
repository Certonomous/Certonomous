#!/usr/bin/env bash
# =====================================================================================
# W3S ARM A WATCHER
#
# WHAT THIS WATCHES, STATED HONESTLY: at the time of arming there is NO RUNNING SOLVER.
# W3S is blocked at two committed gates -- w3s_chain_driver.sh:91 PREREG_COMMIT="" (the
# chain aborts rc=70 NOT_FROZEN) and w3s_stage_and_run.sh:138 LAUNCH_ENABLED=0. So this
# watcher does NOT tail a solver. It waits for the Arm A run root to APPEAR, and only
# then begins reporting the ledger and manifest. If the supervisor fills PREREG_COMMIT
# and places the queue row, this watcher is already in position.
#
# It writes ONLY under the case directory -- never the scratchpad, which is temp-only and
# is not a handoff channel (L-186).
#
# Every reading is labelled. A line this watcher could not read is reported as NOT READ,
# never as zero: a reader that reports 0 when it cannot see is a planted zero in its own
# output.
# =====================================================================================
set -u

BASE="/home/ubuntu/Certonomous/cases/dafoam/curriculum_D12R2"
ROOT="/home/ubuntu/certonomous-runs/CURRICULUM-D12R2W3S-GSCAN-cylinder-unsteady"
LEDGER="$ROOT/ledger.txt"
MANIFEST="$ROOT/manifest.jsonl"
POLL="${W3S_WATCH_POLL_S:-60}"

stamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }

# --- the detector, factored out so the planted control drives THE SAME CODE ----------
# echoes: ABSENT | PRESENT_NO_LEDGER | PRESENT_LEDGER:<n rows>
detect() {
  local r="$1"
  if [ ! -e "$r" ]; then echo "ABSENT"; return 0; fi
  if [ ! -f "$r/ledger.txt" ]; then echo "PRESENT_NO_LEDGER"; return 0; fi
  echo "PRESENT_LEDGER:$(wc -l < "$r/ledger.txt" | tr -d ' ')"
}

# --- the planted control, BOTH SIDES, driven before the loop is entered --------------
selfcontrol() {
  local d neg pos rc=0
  d="$(mktemp -d)"
  neg="$(detect "$d/does_not_exist")"
  mkdir -p "$d/live"; printf 'STAGE=S0 rc=0 core_min=1.750\nLEG=SETUP rc=0\n' > "$d/live/ledger.txt"
  pos="$(detect "$d/live")"
  echo "CONTROL negative(absent root)  -> $neg"
  echo "CONTROL positive(root+ledger)  -> $pos"
  [ "$neg" = "ABSENT" ] || { echo "CONTROL FAIL: negative side did not report ABSENT"; rc=1; }
  [ "$pos" = "PRESENT_LEDGER:2" ] || { echo "CONTROL FAIL: positive side did not read 2 ledger rows"; rc=1; }
  rm -rf "$d"
  if [ "$rc" -eq 0 ]; then
    echo "CONTROL VERDICT: the detector is shown able to report BOTH a root that exists"
    echo "  (with its ledger row count) AND one that does not. Its ABSENT readings below"
    echo "  are therefore evidence, not silence."
  else
    echo "CONTROL VERDICT: FAILED -- this watcher is NOT armed, because an uncontrolled"
    echo "  detector reporting ABSENT forever is indistinguishable from a broken one."
  fi
  return $rc
}

echo "=== W3S ARM A WATCHER ==="
echo "armed_at   $(stamp)"
echo "pid        $$"
echo "root       $ROOT"
echo "poll_s     $POLL"
echo "blockers   driver PREREG_COMMIT empty (rc=70) ; launcher LAUNCH_ENABLED=0"
echo "--- planted control, both sides ---"
selfcontrol || { echo "EXIT 3 control failed"; exit 3; }
echo "--- watch loop ---"

LAST=""
while :; do
  S="$(detect "$ROOT")"
  if [ "$S" != "$LAST" ]; then
    echo "[$(stamp)] STATE $S"
    LAST="$S"
  fi
  case "$S" in
    PRESENT_LEDGER:*)
      echo "[$(stamp)] --- ledger tail ---"
      tail -5 "$LEDGER" 2>/dev/null || echo "  NOT READ: ledger unreadable"
      if [ -f "$MANIFEST" ]; then
        echo "[$(stamp)] manifest rows: $(wc -l < "$MANIFEST" | tr -d ' ')"
      else
        echo "[$(stamp)] manifest: NOT PRESENT (not zero rows -- absent)"
      fi
      # the arm is four legs; a LEG_OK for A2 or any non-zero leg rc ends the watch
      if grep -q "^LEG=A2 " "$LEDGER" 2>/dev/null; then
        echo "[$(stamp)] A2 leg row present -- arm A has reached its last leg. Watch ends."
        exit 0
      fi
      ;;
  esac
  sleep "$POLL"
done
