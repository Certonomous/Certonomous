#!/bin/bash
# NIGHTLY BOARD MERGE -- WRAPPER ONLY. NO CRONTAB ENTRY IS INSTALLED BY THIS FILE
# AND NONE WAS INSTALLED WHEN IT WAS WRITTEN.
#
# Wiring a scheduled job is the chief's hand, not a lane's. The proposed entry is
# quoted at the foot of this file; it is a PROPOSAL and installing it is a separate,
# deliberate act by the chief, AFTER the cutover described in the merger's --adopt
# help text has been taken.
#
# Sanaa's PLUMBING FREEZE directive, 2026-08-31: "Boards become per-team files (one
# writer each), merged into the lab board by a nightly tool -- no shared-file
# splicing by agents, ever."
#
# Pattern follows scripts/index_autoclear.sh: flock -n so two runs never overlap,
# logs to /home/ubuntu/harness-state/, touches nothing it was not asked to touch.
#
# THE MERGER'S OWN INTERLOCK IS WHAT MAKES THIS SAFE TO SCHEDULE EARLY:
# merge_lab_state.py REFUSES (rc 3) to overwrite a docs/LAB_STATE.md that does not
# already carry the generated-file marker. So if this entry were installed BEFORE
# cutover, every run would refuse and log rc=3, and the live hand-maintained board
# would be untouched. The dangerous ordering is not merely documented; it is
# unrepresentable from this wrapper, which never passes --adopt.

set -u
REPO=/home/ubuntu/Certonomous
LOG=/home/ubuntu/harness-state/merge_lab_state.log
cd "$REPO" || exit 1

exec 9>/tmp/certonomous_merge_lab_state.lock
flock -n 9 || exit 0

TS=$(date -u +%FT%TZ)

# Never --adopt from cron. Cutover is a human act, once.
OUT=$(timeout 300 python3 "$REPO/scripts/merge_lab_state.py" 2>&1)
RC=$?

SHA=$(sha256sum "$REPO/docs/LAB_STATE.md" 2>/dev/null | cut -c1-16)
BYTES=$(wc -c < "$REPO/docs/LAB_STATE.md" 2>/dev/null)

case "$RC" in
  0) MSG="OK" ;;
  2) MSG="REFUSED-MALFORMED-SOURCE-OR-ROSTER (board untouched)" ;;
  3) MSG="REFUSED-NOT-YET-ADOPTED (board untouched; cutover not taken)" ;;
  5) MSG="REFUSED-PLANTED-CONTROL-FAILED (board untouched; the merger cannot show it sees a team's bytes)" ;;
  6) MSG="REFUSED-AFTER-WRITE-READBACK-MISMATCH (BOARD ON DISK IS SUSPECT)" ;;
  124) MSG="TIMEOUT-300s (board untouched)" ;;
  *) MSG="UNEXPECTED" ;;
esac

{
  echo "$TS rc=$RC $MSG board_bytes=$BYTES board_sha=$SHA"
  # The merger's own words on a refusal are the whole diagnostic value of a
  # refusal, so they are logged rather than discarded. A silent refusal at 03:00
  # is a board that stops updating and nobody notices for a week.
  if [ "$RC" != "0" ]; then
    echo "$OUT" | sed 's/^/    /'
  fi
} >> "$LOG"

exit "$RC"

# ---------------------------------------------------------------------------
# PROPOSED CRONTAB ENTRY -- NOT INSTALLED. For the chief to install by hand,
# after cutover:
#
#   17 3 * * *  /home/ubuntu/Certonomous/scripts/merge_lab_state_cron.sh
#
# 03:17 UTC, off the hour so it does not collide with every other :00 job.
# Cost, MEASURED 2026-08-31 on the real 3.7 MB sources, not estimated: 2.70 s wall
# on one core, 62 MB peak RSS = 0.045 core-minutes per run, 1.4 core-minutes a
# month. Most of that is the eight full board builds the live planted control
# performs (one negative limb + seven positive, one per source). It is not a
# compute item and it is not worth weakening the control to save.
#
# Before installing, the chief should decide ONE open question the lane could not
# decide for her: WHO COMMITS THE MERGED BOARD. This wrapper regenerates the
# WORKTREE file only and commits nothing -- deliberately, because an unattended
# cron job that writes to refs/heads/main is a much larger change than a merge
# tool, and rule 10's private-index protocol assumes an agent who can inspect a
# conflict. Options, in the lane's order of preference:
#   (a) leave it uncommitted; the next supervisor to commit its own source file
#       also lands the regenerated board (one extra explicit path);
#   (b) have the chief run the merger before /form-teams each session, which is
#       when the board is actually READ, and skip cron entirely;
#   (c) commit from cron under the private-index protocol with a CAS retry.
# (b) is arguably the honest one: the board's only consumer is a session start.
# ---------------------------------------------------------------------------
