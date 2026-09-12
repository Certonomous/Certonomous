#!/bin/bash
# SUBOFF_A1 -- SOLVE ONE LEVEL, DETACHED AND DURABLY.
#
# rc IS CAPTURED INSIDE THIS WRAPPER, from each utility.  `setsid timeout cmd`
# exits 0 for EVERY outcome, so an rc captured around the setsid line is always a
# lie; this script is the thing setsid launches, and it writes its own rc to disk.
#
# THE MEMORY GATE IS PART OF THE LAUNCH, NOT A COURTESY.  Other teams' multi-day
# solves live on this box and the OOM killer selects on RSS without regard to
# ownership.  If `available` memory is below MIN_AVAIL_GIB at launch, this script
# REFUSES and writes BLOCKED -- it does not try and hope.
#
# S5 (pre-registration 7): a time directory or a previous solver artifact present
# at launch => REFUSE.  Never clear the directory.
#
# AMENDMENT 2026-09-12 -- EVERY PHASE IS PRICED AT ITS OWN TRUE RANK COUNT.
# THE DEFECT THIS REPAIRS, MEASURED ON OUR OWN RECORDS: this script used to price its
# WHOLE T1-T0 window at $RANKS, but `decomposePar` logs `nProcs : 1` and
# `reconstructPar` is serial too.  On the crashed SOLVE_L1 attempt that reported 4.80
# core-min against 1.68 honest -- a 2.86x OVERSTATEMENT -- and every SUBOFF row written
# by this instrument inherited the same bias.  A cost instrument that overstates is not
# 'conservative': it corrupts the calibration ledger in the direction that makes the
# lab's estimates look better than they are.
# Each phase is now timed separately and multiplied by ITS OWN rank count, and
# `total_core_min` is the SUM of the three, not a window times a rank count.
# The legacy window figure is still emitted, under a name that says what it is, so no
# reader can mistake it for the honest total and no old reading silently changes meaning.
#
# PEAK RSS IS RECORDED PER PHASE, from /usr/bin/time -v (the kernel's own high-water
# mark, not a poller that can miss a peak between samples).  The SERIAL phases are the
# ones no rank-derived memory bound covers, so they are exactly the ones worth measuring.
set -u
CASE="$1"; RANKS="$2"; MIN_AVAIL_GIB="$3"
# AMENDMENT 2026-09-12 -- RESUME MODE.  OPTIONAL 4th ARGUMENT; ABSENT => BYTE-IDENTICAL
# BEHAVIOUR TO EVERY RUN THIS SCRIPT HAS EVER DRIVEN.  Authorised by the cfd-supervisor
# on Sanaa's ruling of 2026-08-26, "BOOKKEEPING NEVER VOIDS PHYSICS": a 96-core reboot was
# about to throw away 45 iterations of good physics because a shell redirect character
# meant the ExecutionTime LINE COUNT would not reach endTime.  The physics was never in
# question; the COUNTING was.  This repairs the counting.  NO GATE, THRESHOLD, CAP OR
# LABEL IS MOVED -- Gate C still requires `ExecutionTime count == round(endTime/deltaT)`
# and this change is what lets a resumed run SATISFY it honestly rather than be excused
# from it.
#   RESUME=1  =>  the solver log is APPENDED to (`>>`) instead of truncated (`>`), so the
#                 ExecutionTime lines of the original and the resumed segment accumulate
#                 in one file and the registered count test reads what was ACTUALLY run;
#             =>  monitor stop S5's solver-artifact limb is satisfied DELIBERATELY rather
#                 than disabled: a resume REQUIRES log.simpleFoam and postProcessing/ to
#                 exist, so their presence is the precondition, not the violation.  S5's
#                 PURPOSE -- never launch into a tree holding an answer you did not
#                 produce -- is preserved by the checkpoint assertions below, which refuse
#                 unless a COMPLETE checkpoint exists in EVERY processor tree.
#   THIS GENERALISES.  Every resumed OpenFOAM case in this lab inherits the same defect
#   (DrivAer medium and K2h are the known others).  The pattern here -- append the log,
#   make S5 resume-aware, assert the checkpoint across ALL ranks -- is the repair, not a
#   SUBOFF-local patch.
RESUME="${4:-0}"
S="$CASE/STATUS.solve"

avail=$(free -g | awk '/^Mem:/{print $7}')
if [ "$avail" -lt "$MIN_AVAIL_GIB" ]; then
  { echo "VERDICT=BLOCKED"; echo "reason=memory"; echo "available_GiB=$avail";
    echo "required_GiB=$MIN_AVAIL_GIB";
    echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } > "$S"
  echo "80" > "$CASE/solve_rc"; exit 80
fi

if [ "$RESUME" != "1" ]; then
  for e in "$CASE"/[0-9]* ; do
    b=$(basename "$e")
    if [ "$b" != "0" ] && [ -e "$e" ]; then
      { echo "VERDICT=BLOCKED"; echo "reason=S5_time_dir_present"; echo "entry=$b"; } > "$S"
      echo "81" > "$CASE/solve_rc"; exit 81
    fi
  done
  if [ -e "$CASE/log.simpleFoam" ] || [ -e "$CASE/postProcessing" ]; then
    { echo "VERDICT=BLOCKED"; echo "reason=S5_solver_artifact_present"; } > "$S"
    echo "81" > "$CASE/solve_rc"; exit 81
  fi
else
  # RESUME PRECONDITIONS.  STRICTER THAN S5, NOT LOOSER.  A resume that cannot name a
  # COMPLETE checkpoint in EVERY rank's tree is refused -- a checkpoint present in one
  # tree and partial in another is not a checkpoint, and resuming from one would produce
  # a silently wrong field set rather than an error.
  if ! grep -qE '^[[:space:]]*startFrom[[:space:]]+latestTime[[:space:]]*;' "$CASE/system/controlDict"; then
    { echo "VERDICT=BLOCKED"; echo "reason=RESUME_startFrom_not_latestTime"; } > "$S"
    echo "82" > "$CASE/solve_rc"; exit 82
  fi
  # AMENDMENT 2026-09-12c -- COMPLETENESS IS CHECKED BY FIELD NAME, NOT BY FILE COUNT.
  # `ls | wc -l >= 6` is a PROXY: six junk files pass it, and a checkpoint missing
  # `phi` while carrying two stray sidecars passes it too.  Rule 4 names the fields;
  # so does this loop.  RESUME_FIELDS is the registered resume set from the queue
  # entry (U p k omega nut phi) -- the same list, written once, checked per rank.
  RESUME_FIELDS="U p k omega nut phi"
  LATEST=""; NEWEST=""
  for t in $(ls -d "$CASE"/processor0/[0-9]* 2>/dev/null | xargs -n1 basename 2>/dev/null | sort -n); do
    [ "$t" = "0" ] && continue
    NEWEST="$t"
    ok=1
    for r in $(seq 0 $((RANKS-1))); do
      for f in $RESUME_FIELDS; do
        [ -s "$CASE/processor$r/$t/$f" ] || ok=0
      done
    done
    [ "$ok" = "1" ] && LATEST="$t"
  done
  if [ -z "$LATEST" ]; then
    { echo "VERDICT=BLOCKED"; echo "reason=RESUME_no_complete_checkpoint_in_all_ranks"; } > "$S"
    echo "83" > "$CASE/solve_rc"; exit 83
  fi
  # AMENDMENT 2026-09-12c -- THE VERIFIED CHECKPOINT MUST BE THE ONE THAT ACTS.
  # This loop verifies the LATEST COMPLETE checkpoint, but `startFrom latestTime`
  # makes OPENFOAM CHOOSE INDEPENDENTLY: it takes the NEWEST time directory on
  # disk, complete or not.  If a PARTIAL newer checkpoint existed -- a write
  # interrupted by the next kill -- this script would record a verified 60 while
  # the solver silently started from a half-written 75, and STATUS.solve would
  # carry a number the run did not use.  Verification that does not bind the
  # action is the same defect as counting log lines instead of physics steps:
  # a figure that is true about the wrong thing.  So: REFUSE when the newest
  # time directory is not the complete one.  The repair for that refusal is to
  # move the partial directory aside by hand, which PRESERVES it; this script
  # never deletes a time directory.
  if [ "$NEWEST" != "$LATEST" ]; then
    { echo "VERDICT=BLOCKED"; echo "reason=RESUME_newest_time_dir_is_not_the_complete_one";
      echo "newest=$NEWEST"; echo "latest_complete=$LATEST";
      echo "note=startFrom latestTime would start the solver from $NEWEST, which is INCOMPLETE. Move $NEWEST aside by hand -- never delete it -- and relaunch."; } > "$S"
    echo "84" > "$CASE/solve_rc"; exit 84
  fi
  { echo "resume=1"; echo "resume_from_verified=$LATEST";
    echo "resume_newest_time_dir=$NEWEST   # EQUAL to resume_from_verified, checked, so latestTime acts on the verified checkpoint"; } >> "$S"
fi

set +u
source /usr/lib/openfoam/openfoam2606/etc/bashrc '' > "$CASE/log.foam_bashrc_source.solve" 2>&1
SRC=$?
set -u
if [ "$SRC" -ne 0 ]; then
  { echo "VERDICT=BLOCKED"; echo "reason=foam_source"; echo "rc=$SRC"; } > "$S"
  echo "91" > "$CASE/solve_rc"; exit 91
fi

cd "$CASE" || { echo "90" > "$CASE/solve_rc"; exit 90; }

# The age guard (rule 4) dates the run from 0/ -- touch it LAST before the solver,
# so every field at endTime must be strictly newer than it.
touch 0/U 0/p 0/k 0/omega 0/nut
# AMENDMENT 2026-09-12b -- STATUS.solve IS PRESERVED ACROSS A RESUME, NOT TRUNCATED.
# `> "$S"` destroys the previous segment's cost record.  That record is the ONLY
# artifact carrying the killed segment's decomposePar and simpleFoam core-minutes, and
# rule 12's calibration row is owed for BOTH segments.  On a resume the existing file is
# moved aside to STATUS.solve.segment<N> before the new one is opened; nothing is lost
# and no reader's key names change.
if [ "$RESUME" = "1" ] && [ -f "$S" ]; then
  n=1; while [ -e "$S.segment$n" ]; do n=$((n+1)); done
  mv "$S" "$S.segment$n"
fi
{ echo "started_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; echo "ranks=$RANKS";
  echo "available_GiB_at_launch=$avail";
  echo "resume=$RESUME"; } > "$S"
[ "$RESUME" = "1" ] && echo "resume_from_verified=$LATEST" >> "$S"
T0=$(date +%s)

# AMENDMENT 2026-09-12b -- decomposePar IS SKIPPED ON A RESUME, AND THIS IS THE WHOLE
# POINT OF THE RESUME.  `decomposePar -force` DELETES every existing processor*/
# directory and rebuilds them from 0/.  Run on a resume it would destroy the very
# checkpoint the resume exists to continue from -- the run would silently start at
# iteration 0 with a log that says "resume", which is the exact outcome Sanaa's ruling
# forbids, and it would be UNDETECTABLE after the fact because the evidence is what gets
# deleted.  MEASURED ON THIS CASE: SOLVE_L2/processor{0,1,2,3}/60 hold 8 files each,
# 21:29Z; a `-force` decomposition removes all four trees.
# The serial-phase cost keys are still written, with SKIPPED values, so no reader that
# expects them reads a missing key as a zero.
TD0=$(date +%s)
if [ "$RESUME" = "1" ]; then
  TD1=$TD0; RC=0
  { echo "decomposePar_rc=0";
    echo "decomposePar_wall_s=0";
    echo "decomposePar_ranks=1";
    echo "decomposePar_core_min=0   # SKIPPED ON RESUME -- see AMENDMENT 2026-09-12b";
    echo "decomposePar_SKIPPED_RESUME=1";
    echo "decomposePar_peak_rss_kB=SKIPPED_RESUME"; } >> "$S"
else
  /usr/bin/time -v -o time.decomposePar.solve decomposePar -force > log.decomposePar.solve 2>&1; RC=$?
  TD1=$(date +%s)
  DPEAK=$(grep "Maximum resident set size" time.decomposePar.solve | grep -oE "[0-9]+$")
  { echo "decomposePar_rc=$RC";
    echo "decomposePar_wall_s=$((TD1-TD0))";
    echo "decomposePar_ranks=1   # SERIAL -- the log says nProcs : 1";
    echo "decomposePar_core_min=$(echo "($TD1-$TD0)*1/60" | bc -l)";
    echo "decomposePar_peak_rss_kB=${DPEAK:-UNMEASURED}"; } >> "$S"
  if [ "$RC" -ne 0 ]; then echo "$RC" > solve_rc; exit "$RC"; fi
fi

TS0=$(date +%s)
# AMENDMENT 2026-09-12c -- THE REDIRECT IS NOW GUARDED ON RESUME, AS THE COMMENT
# ABOVE ALWAYS CLAIMED IT WAS.  It was written unconditionally (`>>` on every run).
# In practice a fresh run could not accumulate logs, because S5 refuses to start when
# log.simpleFoam already exists -- but that safety came from a DIFFERENT GUARD than
# the one the comment names, and an instrument whose comment names the wrong
# guarantor is one the next reader trusts for the wrong reason.  Loosen S5 for any
# reason later and fresh runs would have silently appended.  Now the branch is real:
# a fresh run TRUNCATES and a resume APPENDS, and neither depends on S5 holding.
if [ "$RESUME" = "1" ]; then
  /usr/bin/time -v -o time.simpleFoam.solve mpirun -np "$RANKS" simpleFoam -parallel >> log.simpleFoam 2>&1; RC=$?
else
  /usr/bin/time -v -o time.simpleFoam.solve mpirun -np "$RANKS" simpleFoam -parallel > log.simpleFoam 2>&1; RC=$?
fi
TS1=$(date +%s); T1=$TS1
SPEAK=$(grep "Maximum resident set size" time.simpleFoam.solve | grep -oE "[0-9]+$")
{ echo "simpleFoam_rc=$RC";
  echo "simpleFoam_wall_s=$((TS1-TS0))";
  echo "simpleFoam_ranks=$RANKS";
  echo "simpleFoam_core_min=$(echo "($TS1-$TS0)*$RANKS/60" | bc -l)";
  echo "simpleFoam_peak_rss_kB=${SPEAK:-UNMEASURED}   # largest single rank, not the sum";
  echo "LEGACY_window_core_min_OVERSTATED=$(echo "($T1-$T0)*$RANKS/60" | bc -l)   # the OLD figure: the whole window priced at RANKS, including the SERIAL decomposePar. Kept only so an old reading is recognisable; it is NOT the cost."; } >> "$S"
if [ "$RC" -ne 0 ]; then echo "$RC" > solve_rc; exit "$RC"; fi

TR0=$(date +%s)
/usr/bin/time -v -o time.reconstructPar.solve reconstructPar -latestTime > log.reconstructPar.solve 2>&1; RC=$?
TR1=$(date +%s)
RPEAK=$(grep "Maximum resident set size" time.reconstructPar.solve | grep -oE "[0-9]+$")
{ echo "reconstructPar_rc=$RC";
  echo "reconstructPar_wall_s=$((TR1-TR0))";
  echo "reconstructPar_ranks=1   # SERIAL";
  echo "reconstructPar_core_min=$(echo "($TR1-$TR0)*1/60" | bc -l)";
  echo "reconstructPar_peak_rss_kB=${RPEAK:-UNMEASURED}"; } >> "$S"
if [ "$RC" -ne 0 ]; then echo "$RC" > solve_rc; exit "$RC"; fi

T2=$(date +%s)
{ echo "total_wall_s=$((T2-T0))";
  echo "total_core_min=$(echo "(($TD1-$TD0)*1 + ($TS1-$TS0)*$RANKS + ($TR1-$TR0)*1)/60" | bc -l)   # SUM OF PHASES, each at ITS OWN rank count -- NOT the window times RANKS";
  echo "LEGACY_total_core_min_OVERSTATED=$(echo "($T2-$T0)*$RANKS/60" | bc -l)   # the OLD arithmetic, kept for recognisability only";
  echo "finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } >> "$S"
echo "0" > solve_rc
exit 0
