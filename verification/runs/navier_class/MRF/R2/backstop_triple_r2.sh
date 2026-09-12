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
#   - if the incumbent's artifact TRIPLE_R2.out exists and is non-empty within the
#     grace window, this script STANDS DOWN, grades nothing, and merely PRESERVES
#     the incumbent's output verbatim on the durable path;
#   - only if the incumbent produced nothing by the end of grace (its scratchpad
#     wiped, or its shell died) does this script grade, once, and say so.
#   - a durable record that already exists is never overwritten (idempotent).
#   - the claim is atomic (mkdir), so two copies of this script cannot both write.
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

# --- idempotence: a landed record is never re-made ---------------------
if [ -s "$DUR" ]; then
  log "STAND DOWN: durable record already exists and is non-empty -> $DUR"
  exit 0
fi

# --- atomic claim: only one backstop may proceed -----------------------
if ! mkdir "$LOCK" 2>/dev/null; then
  log "STAND DOWN: another backstop holds the claim ($LOCK)"
  exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null' EXIT

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

# --- grace: give the incumbent its chance to produce THE record --------
g=0
while [ "$g" -lt "$GRACE" ]; do
  if [ -s "$INC" ]; then
    log "INCUMBENT PRODUCED ITS ARTIFACT after ${g}s of grace. STANDING DOWN from grading;"
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

# --- the incumbent produced nothing: grade once, ourselves -------------
log "GRACE EXPIRED (${GRACE}s) with no incumbent artifact at $INC."
log "  The incumbent is presumed lost (scratchpad wiped, or its shell died). GRADING ONCE."
{
  echo "###############################################################################"
  echo "# MRF R2 ET8000 TRIPLE -- DURABLE RECORD"
  echo "# PROVENANCE: produced by backstop_triple_r2.sh at $(date -u +%FT%TZ)."
  echo "# The incumbent grader (on_triple.sh, pid 2381356) produced NO artifact at"
  echo "#   $INC"
  echo "# within ${GRACE}s of fine landing, so the backstop graded. This is the ONLY"
  echo "# record of this grading; if the incumbent later writes one, the two must be"
  echo "# reconciled, not stacked."
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
