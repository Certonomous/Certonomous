#!/bin/bash
# =====================================================================
# MRF R2 ET8000 -- DURABLE BACKSTOP for the triple grading on fine's landing.
#
# WHY THIS EXISTS (L-186). The incumbent grader (pid 2381356, on_triple.sh) and
# its three sibling watchers all live in ANOTHER SESSION'S SCRATCHPAD:
#   /tmp/claude-1000/-home-ubuntu-Certonomous/80f960ef-.../scratchpad/mrf_disk_watch
# The scratchpad is temp, has been wiped three times in one day, and bash reads a
# script INCREMENTALLY from disk as it executes -- so a wipe can break a live
# watcher mid-flight AND destroy the record it was going to leave. This script
# lives on a durable path inside the case family and closes both holes.
#
# WHAT THIS IS, AND WHAT IT IS NOT.
#   It is a COURIER and a FALLBACK LAUNCHER. It computes NO number of its own.
#   Every number in its output comes from the frozen grader
#   verification/runs/navier_class/MRF/R2/grade_triple_r2.py (blob
#   b3758cc5427b12bec76f8c23b2188276401a1db8, identical at 5c6869f7 and at HEAD),
#   whose rule-3 plant is its OWN: it copies each level's moment.dat to a tempdir,
#   overwrites the first data row's total_z with measure_states_mrf.PLANT, re-reads
#   through read_total_axial, and returns False unless the planted value comes back
#   to 1e-12 -- per level, on that level's own artifact. This script neither adds
#   nor weakens a control; it preserves the frozen grader's verdict verbatim.
#   It is READ-ONLY on the graded tree (the frozen grader plants only into a
#   tempfile.mkdtemp copy and never writes into any case dir).
#
# NO DOUBLE RECORD. Two agents on one item produce two records for one run. So:
#   - if the incumbent's artifact TRIPLE_R2.out is COMPLETE within the grace window,
#     this script STANDS DOWN, grades nothing, and merely PRESERVES the incumbent's
#     output verbatim on the durable path;
#   - if the incumbent produced NOTHING by the end of grace (its scratchpad wiped,
#     or its shell died before it started), this script grades once and says so;
#   - if the incumbent produced a PARTIAL artifact that never terminated, this
#     script grades and DOES NOT COPY the partial, quoting its byte count and last
#     line in the provenance banner so a reader can find it.
#   - a durable record that already exists is never overwritten (idempotent).
#   - the claim is atomic (mkdir), so two copies of this script cannot both write.
#
# WHY "COMPLETE" AND NOT "NON-EMPTY" -- the defect this script had at 51129c367,
# found by the cfd-supervisor's check-1 diff-read and fixed here. The incumbent
# writes with one shell redirect over a brace block:
#     { echo banner; ...; python3 "$G"; echo "### grader rc=$?"; } > TRIPLE_R2.out
# so the file is created empty by the redirect and becomes NON-EMPTY within
# milliseconds, as the first echo lands -- long BEFORE the grader has produced a
# verdict. A `[ -s "$INC" ]` test therefore asks whether bytes exist, when what
# must be known is whether the RECORD IS FINISHED. It would have been true on the
# very first poll (both watchers wait on the same rc marker; the incumbent sleeps
# 120 s and this script 180 s, so it arrives ~60 s after the banner lands), and
# this script would have copied a banner and a half-written verdict under a
# provenance line reading "the incumbent's bytes, unedited" -- true about the
# source and MISLEADING about the completeness -- and then the idempotence guard
# would have made that truncated record PERMANENT. A truncated record that cannot
# be remade is worse than no record: the next reader cannot tell it is truncated.
# ASKED OF IT WHAT WE ASK OF A CONTROL -- what result would have failed the old
# test? Essentially nothing: a lone banner passed it.
# THE FIX uses the incumbent's own terminator as a sentinel. Its LAST line is
# `### grader rc=$?`, so the artifact counts as a record only when its final line
# matches ^### grader rc=. That is exact. A size-stability check is NOT a
# substitute -- a grader that stalls mid-write looks perfectly stable.
#
# IT NEVER TOUCHES THE RUNNING SOLVER. It polls for the rc sidecar on disk. It
# never signals, never pgreps the solver, never writes into fine/ while it runs.
# =====================================================================
set -u

# Every path and interval is overridable ONLY so that --drill can exercise each
# branch in a sandbox. Defaults are the real ones; a normal run passes nothing.
R2=${BS_R2:-/home/ubuntu/Certonomous/verification/runs/navier_class/MRF/R2}
F=${BS_F:-$R2/ET8000/fine}
G=${BS_G:-$R2/grade_triple_r2.py}
FROZEN_BLOB=${BS_FROZEN_BLOB:-b3758cc5427b12bec76f8c23b2188276401a1db8}
INC=${BS_INC:-/tmp/claude-1000/-home-ubuntu-Certonomous/80f960ef-5d3e-4c55-8964-1a39e21031b0/scratchpad/mrf_disk_watch/TRIPLE_R2.out}

DUR=${BS_DUR:-$R2/TRIPLE_R2_RECORD.txt}          # THE durable record. One per run.
LOCK=${BS_LOCK:-$R2/.backstop_triple_r2.lock}    # atomic claim
LOG=${BS_LOG:-$R2/backstop_triple_r2.log}

POLL=${BS_POLL:-60}
MAX_WAIT_RC=${BS_MAX_WAIT_RC:-21600}  # 6 h ceiling on waiting for fine's rc
SETTLE=${BS_SETTLE:-180}              # let reconstructPar finish writing endTime fields
GRACE=${BS_GRACE:-1500}               # 25 min for the incumbent to produce its artifact
GRACE_POLL=${BS_GRACE_POLL:-30}

log() { echo "[$(date -u +%FT%TZ)] $*" >> "$LOG"; }

# THE COMPLETENESS TEST. The incumbent's own LAST line is `### grader rc=$?`, so
# that terminator -- and nothing weaker -- says the record is finished. See the
# header for why `[ -s ]` was wrong and would have been true on the first poll.
inc_complete() { [ -s "$1" ] && tail -n 1 "$1" 2>/dev/null | grep -q '^### grader rc='; }

# --- idempotence: a landed record is never re-made ---------------------
if [ -s "$DUR" ]; then
  log "STAND DOWN: durable record already exists and is non-empty -> $DUR"
  exit 0
fi

# --- atomic claim: only one backstop may proceed -----------------------
# A `mkdir` claim survives SIGKILL, because the EXIT trap never runs. A stale lock
# would then make EVERY future backstop stand down at the claim while NO durable
# record exists -- the one combination where this script is disarmed and silent
# about it. So the owning pid goes INSIDE the lock, and a lock whose owner is gone
# is reclaimed, loudly.
claim() {
  if mkdir "$LOCK" 2>/dev/null; then echo $$ > "$LOCK/pid"; return 0; fi
  owner=$(cat "$LOCK/pid" 2>/dev/null)
  if [ -n "$owner" ] && [ -d "/proc/$owner" ]; then
    log "STAND DOWN: another backstop holds the claim ($LOCK, live owner pid $owner)"
    return 1
  fi
  log "STALE LOCK RECLAIMED: $LOCK was held by pid '${owner:-<none recorded>}', which is"
  log "  NOT ALIVE. A lock outliving its owner disarms every future backstop silently;"
  log "  it is reclaimed here and the reclamation is recorded rather than passed over."
  rm -f "$LOCK/pid"; rmdir "$LOCK" 2>/dev/null
  mkdir "$LOCK" 2>/dev/null || { log "STAND DOWN: lost the reclaim race on $LOCK"; return 1; }
  echo $$ > "$LOCK/pid"; return 0
}
claim || exit 0
trap 'rm -f "$LOCK/pid" 2>/dev/null; rmdir "$LOCK" 2>/dev/null' EXIT

log "ARMED. waiting on $F/rc (poll ${POLL}s, ceiling ${MAX_WAIT_RC}s). incumbent artifact watched at $INC"

# --- wait for fine's completion artifact -------------------------------
waited=0
while [ ! -f "$F/rc" ]; do
  if [ "$waited" -ge "$MAX_WAIT_RC" ]; then
    log "CEILING REACHED after ${waited}s with no rc sidecar. NOT grading. A run that"
    log "  has not written its completion artifact is not done; this is a finding for triage,"
    log "  not a timeout to absorb."
    exit 3
  fi
  sleep "$POLL"; waited=$((waited + POLL))
done
log "fine rc sidecar appeared (rc=$(cat "$F/rc" 2>/dev/null)). settling ${SETTLE}s for reconstructPar."
sleep "$SETTLE"

# --- grace: give the incumbent its chance to produce A COMPLETE record -
g=0
while [ "$g" -lt "$GRACE" ]; do
  if inc_complete "$INC"; then
    log "INCUMBENT PRODUCED A COMPLETE ARTIFACT after ${g}s of grace (terminator seen)."
    log "  STANDING DOWN from grading;"
    log "  preserving it verbatim on the durable path. No second record is produced."
    {
      echo "###############################################################################"
      echo "# MRF R2 ET8000 TRIPLE -- DURABLE RECORD"
      echo "# PROVENANCE: this is a VERBATIM COPY of the INCUMBENT grader's output."
      echo "#   incumbent : on_triple.sh, pid 2381356, another session's scratchpad"
      echo "#   source    : $INC"
      echo "#   copied by : backstop_triple_r2.sh at $(date -u +%FT%TZ)"
      echo "# THE BACKSTOP GRADED NOTHING. It stood down so that one run yields one record."
      echo "# Everything below this banner is the incumbent's bytes, unedited."
      echo "###############################################################################"
      cat "$INC"
    } > "$DUR"
    log "PRESERVED -> $DUR"
    exit 0
  fi
  sleep "$GRACE_POLL"; g=$((g + GRACE_POLL))
done

# --- grace expired: grade once, ourselves. TWO DISTINCT CAUSES, and they are
# --- reported as two distinct things, because "produced nothing" and "started and
# --- died mid-grade" are different facts about the incumbent.
if [ -s "$INC" ]; then
  INC_STATE=PARTIAL
  INC_BYTES=$(wc -c < "$INC" 2>/dev/null)
  INC_LAST=$(tail -n 1 "$INC" 2>/dev/null)
  log "GRACE EXPIRED (${GRACE}s). THE INCUMBENT ARTIFACT IS PARTIAL: $INC_BYTES bytes at $INC"
  log "  with NO terminator -- last line: $INC_LAST"
  log "  The incumbent BEGAN and then died or hung mid-grade. The partial is NOT copied:"
  log "  a truncated record under a 'verbatim, unedited' banner reads as a finished one."
  log "  GRADING ONCE, and the partial is named in the record so a reader can find it."
else
  INC_STATE=ABSENT
  log "GRACE EXPIRED (${GRACE}s) with NO incumbent artifact at all at $INC."
  log "  The incumbent is presumed lost (scratchpad wiped, or its shell died). GRADING ONCE."
fi
{
  echo "###############################################################################"
  echo "# MRF R2 ET8000 TRIPLE -- DURABLE RECORD"
  echo "# PROVENANCE: produced by backstop_triple_r2.sh at $(date -u +%FT%TZ)."
  if [ "$INC_STATE" = PARTIAL ]; then
    echo "# The incumbent grader (on_triple.sh, pid 2381356) produced a PARTIAL artifact"
    echo "#   $INC"
    echo "#   $INC_BYTES bytes, NO '### grader rc=' terminator."
    echo "#   its last line was: $INC_LAST"
    echo "# It began and then died or hung mid-grade. THE PARTIAL WAS DELIBERATELY NOT"
    echo "# COPIED -- a truncated verdict under a 'verbatim, unedited' banner reads as a"
    echo "# finished one, and the idempotence guard would have made it permanent. The"
    echo "# backstop graded instead. The partial is named above so it can be inspected."
  else
    echo "# The incumbent grader (on_triple.sh, pid 2381356) produced NO artifact at"
    echo "#   $INC"
    echo "# within ${GRACE}s of fine landing, so the backstop graded."
  fi
  echo "# This is the ONLY record of this grading; if the incumbent later writes one,"
  echo "# the two must be reconciled, not stacked."
  echo "###############################################################################"
  echo "### frozen grader self-verification (rule 2): the file that grades must be the"
  echo "### file that was frozen BEFORE fine landed."
  cd /home/ubuntu/Certonomous || exit 4
  d=$(git hash-object "$G")
  echo "###   disk blob      $d"
  echo "###   frozen blob    $FROZEN_BLOB  (== blob at 5c6869f7 and at HEAD)"
  if [ "$d" != "$FROZEN_BLOB" ]; then
    echo "REFUSE: the grader on disk is NOT the frozen blob. A grader that changed after"
    echo "the run cannot be shown to be the file that would have graded it. NOT A RESULT."
    exit 2
  fi
  echo "###   IDENTICAL -- the frozen grader is the file that grades."
  echo "### fine completion artifacts, COPIED from the run's own sidecars (not computed):"
  echo "###   rc=$(cat "$F/rc" 2>/dev/null) core_min=$(cat "$F/CORE_MINUTES.txt" 2>/dev/null) wall_s=$(cat "$F/WALL_SECONDS_SOLVE.txt" 2>/dev/null) ranks=$(cat "$F/RANKS.txt" 2>/dev/null)"
  echo
  python3 "$G"
  echo "### grader rc=$?"
} > "$DUR" 2>&1
log "GRADED -> $DUR (grader rc captured inside the record)"
exit 0
